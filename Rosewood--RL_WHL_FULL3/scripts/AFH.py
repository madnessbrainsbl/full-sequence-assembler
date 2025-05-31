#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2009, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: AFH Module
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/09/30 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/AFH.py $
# $Revision: #2 $
# $DateTime: 2016/09/30 02:58:41 $
# $Author: yihua.jiang $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/AFH.py#2 $
# Level: 3

#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
import types, struct
import ScrCmds
from Process import CProcess
import Utility
from Utility import CUtility
import FSO
import MathLib
from AFH_SIM import CAFH_Frames
from Servo import CServoFunc
import MessageHandler as objMsg
from AFH_constants import *
from Drive import objDut
from PowerControl import objPwrCtrl
from SampleMonitor import TD
from Temperature import CTemperature


DEBUG = 0
FAST_DEBUG = 0                      # This should always be set to 0 for a valid AFH process run

class CAFH(CProcess):
   """
   CAFH module provides a base class functionality to allow for manipulation of the fly height control system.

   General AFH Documentation
   =========================
      U{Algorithm Documentation <F3_AFH_Flow.htm>}
   """
   def __init__(self):
      CProcess.__init__(self)
      self.dut = objDut
      self.masterHeatState = self.dut.driveattr.get('MASTER_HEAT_STATE', 1)
      self.mFSO = FSO.CFSO()
      self.suppress_AFH_errors = 0     # set flag to non-zero to suppress AFH errors.
      self.AFH_error = ()


   def setMasterHeat(self, masterHeatPrm, setMHeatOn = 1):
      self.St(masterHeatPrm['read'])
      mastheatVal = int(self.dut.dblData.Tables('P011_SV_RAM_RD_BY_OFFSET').tableDataObj()[-1]['READ_DATA'],16)

      if testSwitch.BF_0122569_341036_AFH_MASTER_HEAT_SET_T011_USE_MASK_VALUE_FFFE:
         mastheatVal & 0x0001  # Ensure we are checking the master heat bit (0) and nothing else
      if  mastheatVal == setMHeatOn:
         if DEBUG == 1:
            objMsg.printMsg("Master Heat Value Initial Matches Requested")
         return None
      else:
         if testSwitch.BF_0122569_341036_AFH_MASTER_HEAT_SET_T011_USE_MASK_VALUE_FFFE:
            masterHeatPrm['enable']['MASK_VALUE'] = 0xFFFE  # Ensure we modify the master heat bit (0) and nothing else
            masterHeatPrm['disable']['MASK_VALUE'] = 0xFFFE
         if setMHeatOn == 1:
            self.St(masterHeatPrm['enable'])
            self.St(masterHeatPrm['read'])
            self.masterHeatState = 1
         elif setMHeatOn == 0:
            self.St(masterHeatPrm['disable'])
            self.St(masterHeatPrm['read'])
            self.masterHeatState = 0
         self.St(masterHeatPrm['saveSAP'])

      self.dut.driveattr['MASTER_HEAT_STATE'] = self.masterHeatState


   def setTargets(self, prepTargets, rwTargets):
      self.St(prepTargets)
      self.St(rwTargets)


   def setIRPCoefs(self, preamType, waferType, powerMode, coefDict, forceRAPWrite = 1, hrmAddC0WitC1 = 1):
      activeCoeffs = {}
      coefs = self.getClrCoeff(coefDict, preamType, waferType, hrmAddC0WitC1 = hrmAddC0WitC1)
      activeCoeffs.update(coefs)

      eqnTypes = ['WRT_PTP_COEF', 'HTR_PTP_COEF', 'WRT_HTR_PTP_COEF']

      baseCoefs_178 = TP.baseCoefs_Prm_178.copy()
      baseCoefs_178['CWORD1'] = baseCoefs_178["CWORD1"][0] | 0x0800
      if testSwitch.IN_DRIVE_AFH_COEFF_PER_HEAD_GENERATION_SUPPORT:
         baseCoefs_178['HEAD_RANGE'] = (0x00FF,)

      for coefNum in range(AFH_MAX_NUM_COEFS_IN_RAP_PER_EQN_TYPE):
         setPrm = {}
         setPrm.update( baseCoefs_178 )
         for coefType in eqnTypes:
            if len(activeCoeffs[coefType][powerMode]) > coefNum:
               if (type(activeCoeffs[coefType][powerMode][coefNum]) == types.StringType):
                  setPrm[coefType] = self.oUtility.returnIntMantWord(0, 10**6)
               else:
                  if DEBUG == 1:
                     objMsg.printMsg('setIRPCoefs/ coefNum: %s, coefType: %s, value: %s ' % (str(coefNum), str(coefType), str(activeCoeffs[coefType][powerMode][coefNum]), ))
                  setPrm[coefType] = self.oUtility.returnIntMantWord(activeCoeffs[coefType][powerMode][coefNum], 10**6)
            else:
               setPrm[coefType] = self.oUtility.returnIntMantWord(0, 10**6)
            setPrm['BIT_MASK'] = self.oUtility.ReturnTestCylWord(2**(coefNum+1))
         self.St(setPrm)

      if forceRAPWrite == 1:
         self.mFSO.saveRAPtoFLASH()


   def verifyIRPCoefs(self, varianceAllowed, preamType, waferType, powerMode, coefDict, spc_id = 1):
      """
      Verify that the process coefficients and the coefficients stored in the RAP agree to within
         the absolute difference supplied in the parameter varianceAllowed.
      """
      activeCoeffs = {}
      coefs = self.getClrCoeff(coefDict, preamType, waferType)
      activeCoeffs.update(coefs)

      eqnTypes = ['WRT_PTP_COEF', 'HTR_PTP_COEF', 'WRT_HTR_PTP_COEF']

      # re-populate coef table
      afh_ptp_prm = TP.AFH_PTP_Coef_Dump_Prm_172.copy()
      afh_ptp_prm['spc_id'] = spc_id
      self.St( afh_ptp_prm )

      coefTable = self.dut.dblData.Tables('P172_AFH_PTP_COEF').tableDataObj()
      deltaList = {}
      for coefType in eqnTypes:
         deltaList[coefType] = []
      try:
         for coefNum in range(AFH_MAX_NUM_COEFS_IN_RAP_PER_EQN_TYPE):
            for coefType in eqnTypes:

               if len(activeCoeffs[coefType][powerMode]) > coefNum:
                  if (type(activeCoeffs[coefType][powerMode][coefNum]) == types.StringType):
                     processVal = 0
                  else:
                     processVal = activeCoeffs[coefType][powerMode][coefNum]
               else:
                  processVal = 0
               rapVal = float(coefTable[coefNum-AFH_MAX_NUM_COEFS_IN_RAP_PER_EQN_TYPE][coefType])
               absDelta = abs(processVal - rapVal)
               deltaList[coefType].append(absDelta)
               result = self.areProcessAndRAPvaluesEqual(processVal, rapVal, varianceAllowed)
               if result == FAIL and not testSwitch.virtualRun:
                  ScrCmds.raiseException(10279, {"COEF_NUM":coefNum, "COEF_TYPE":coefType, "EXP":processVal, "VAL":rapVal})
      finally:
         if DEBUG == 1:
            objMsg.printMsg("Calculated Absolute Differentials", objMsg.CMessLvl.VERBOSEDEBUG)
         objMsg.printDict(deltaList, objMsg.CMessLvl.VERBOSEDEBUG, colWidth = 20)


   def getClrCoeff(self, clr_Coeff, preamp, aabtype, hrmAddC0WitC1 = 1):
      eqnTypes = ['WRT_PTP_COEF', 'HTR_PTP_COEF', 'WRT_HTR_PTP_COEF']
      if testSwitch.HAMR:
         coef = clr_Coeff.copy()
         c1 = coef['WRT_PTP_COEF']['LO_POWER'][0]         
         if hrmAddC0WitC1:
            c1 = c1 + coef['WRT_PTP_COEF']['LO_POWER'][28]
         coef['WRT_PTP_COEF']['LO_POWER'][0] = c1
         return coef
      else:
         return clr_Coeff #using test parameter extractor to resolve

   def setDualHeaterinRAP(self, preamType, AABType, coefDict):

      coefs = self.getClrCoeff(coefDict, preamType, AABType)
      objMsg.printMsg("Dual heater support enabled. %d " % ( testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT ))

      if (testSwitch.virtualRun == 1):
         if ( testSwitch.extern.AFH_MAJ_REL_NUM == 30 ) and ( testSwitch.extern.AFH_MIN_REL_NUM == 0 ):
            coefs['isDriveDualHeater'] = 1

      if 'isDriveDualHeater' in coefs:

         self.dut.isDriveDualHeater = coefs['isDriveDualHeater']
         objMsg.printMsg("AFH READER_HEATER is enabled.")

         # call 178
         self.St( TP.test178_enableReaderHeater )

         # check with T172
         self.St( TP.test172_displayActiveHeater )

         self.mFSO.saveRAPtoFLASH()
      else:
         objMsg.printMsg("AFH READER_HEATER is disabled.")

         # call 178
         self.St( TP.test178_disableReaderHeater )

         # check with T172
         self.St( TP.test172_displayActiveHeater )

         self.mFSO.saveRAPtoFLASH()
      self.St( TP.test172_displayActiveHeater )


   def setGammaHValues(self, preamType, AABType, coefDict, test178_gammaH):
      coefs = self.getClrCoeff(coefDict, preamType, AABType)

      if testSwitch.BF_0161447_340210_DUAL_HTR_IN_HEAD_CAL == 0:
         if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT == 1:
            self.setDualHeaterinRAP(preamType, AABType, coefDict)

         else:
            objMsg.printMsg("Dual heater support disabled. %d " % ( testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT ))

      if 'gammaWriterHeater' in coefs:
         objMsg.printMsg('Updating AFH gammaWriterHeater values in RAP')
         test178_gammaH.update({'AFH_GAMMA':(
            self.oUtility.float_as_words(float(coefs['gammaWriterHeater'][0]), _little_endian=1) +
            self.oUtility.float_as_words(float(coefs['gammaWriterHeater'][1]), _little_endian=1) +
            self.oUtility.float_as_words(float(coefs['gammaWriterHeater'][2]), _little_endian=1)), })

         test178_gammaH.update({'AFH_GAMMA_W':(
            self.oUtility.float_as_words(float(coefs['gammaWriter'][0]), _little_endian=1) +
            self.oUtility.float_as_words(float(coefs['gammaWriter'][1]), _little_endian=1) +
            self.oUtility.float_as_words(float(coefs['gammaWriter'][2]), _little_endian=1)), })

         cword3 = test178_gammaH["CWORD3"]
         if type(cword3) == types.TupleType:
            cword3 = cword3[0]
         if type(cword3) == types.ListType:
            cword3 = cword3[0]
         cword3 = cword3 | AFH_TEST178_GAMMA_H_CWORD3
         cword3 = cword3 | AFH_TEST178_GAMMA_W_CWORD3

         if testSwitch.extern.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT == 1:
            if 'gammaReaderHeater' in coefs:
               test178_gammaH.update({'AFH_GAMMA_R':(
                  self.oUtility.float_as_words(float(coefs['gammaReaderHeater'][0]), _little_endian=1) +
                  self.oUtility.float_as_words(float(coefs['gammaReaderHeater'][1]), _little_endian=1) +
                  self.oUtility.float_as_words(float(coefs['gammaReaderHeater'][2]), _little_endian=1)), })
               cword3 = cword3 | AFH_TEST178_GAMMA_R_CWORD3

         test178_gammaH["CWORD3"] = cword3

         self.St(test178_gammaH)
         self.St( TP.AFH_GAMMA_Prm_172 )
      # end of setGammaHValues()


   def getDHStatus( self, preamType, AABType, coefDict ):
      coefs = self.getClrCoeff(coefDict, preamType, AABType)

      if (testSwitch.virtualRun == 1):
         if ( testSwitch.extern.AFH_MAJ_REL_NUM == 30 ) and ( testSwitch.extern.AFH_MIN_REL_NUM == 0 ):
            coefs['isDriveDualHeater'] = 1

      if 'isDriveDualHeater' in coefs:
         self.dut.isDriveDualHeater = coefs['isDriveDualHeater']
         objMsg.printMsg("AFH READER_HEATER is enabled.")

      # check with T172
      self.St( TP.test172_displayActiveHeater )


   def display_IEEE754_format(self, f1, verbose = 0):

      [a1, a2, a3, a4] = struct.unpack('4B', struct.pack('f', f1))
      s = a4 >> 7
      e = (a4 & 0x7F) << 1
      e = e + ((a3 & 0x80) >> 7)
      f = a1 + (a2 << 8) + ((a3 & 0x7F)<< 16)

      if verbose >= 1:
         objMsg.printMsg("display_IEEE754_format/ input: %s, sign(1-bit): %s, exp(8-bit): %s, fraction(23-bit): %s" % \
            (str(f1), str(s), str(e), str(f)))


   def return_IEEE754_format(self, f1, verbose = 0):

      [a1, a2, a3, a4] = struct.unpack('4B', struct.pack('f', f1))

      s = a4 >> 7
      e = (a4 & 0x7F) << 1
      e = e + ((a3 & 0x80) >> 7)
      f = a1 + (a2 << 8) + ((a3&0x7F)<<16)

      self.display_IEEE754_format(f1, verbose)
      return [s, e, f]


   def areFloatsIEE754Equal(self, f1, f2, verbose = 0):
      """
      returns FAIL if not equal
      PASS if equal

      if verbose == 0 then display nothing
      if verbose == 1 then display IEEE 754 values broken down.
      """

      [f1_s, f1_e, f1_f] = self.return_IEEE754_format(f1, verbose)
      [f2_s, f2_e, f2_f] = self.return_IEEE754_format(f2, verbose)

      if (f1_s == f2_s) and (f1_e == f2_e) and (f1_f == f2_f):
         return PASS
      else:
         return FAIL


   def areFloatsEqualWithinPrecision(self, f1, f2, sigfigs):
      sig_mag = (sigfigs) / float(2.0)

      if (abs(f1 - f2) < sig_mag):
         return PASS
      else:
         return FAIL


   def areProcessAndRAPvaluesEqual(self, f1, f2, sigfigs, verbose = 0):
      if type(f1) == types.StringType or type(f2) == types.StringType:
         return FAIL
      f1 = float(f1)
      f2 = float(f2)

      # 1.) check to see if numbers are bit for bit IEEE 754 equivalent
      # A check for bit by bit equivalency is necessary, because there are some combinations of numbers
      # that will fail areFloatsEqualwithinPrecision(), but pass areFloatsIEE754Equal().
      result = self.areFloatsIEE754Equal(f1, f2, verbose = verbose)

      # 2.) if not bit for bit equivalent test for equalWithinPrecision
      if result == FAIL:
         result = self.areFloatsEqualWithinPrecision(f1, f2, sigfigs)
      return result


   def set_AFH_error(self, errorCode, errorString):
      if (self.AFH_error == () and self.suppress_AFH_errors != 0):
         objMsg.printMsg('Fatal Script Error Occurred!!!')
         objMsg.printMsg('Error Code: %s (%s) is being suppressed until after all FH contact values have been measured.' \
            % (str(errorCode), str(errorString)))
         self.AFH_error = (errorCode, errorString)

      if (self.suppress_AFH_errors == 0):
         ScrCmds.raiseException(errorCode, errorString)


   def raise_AFH_error(self,):
      if self.AFH_error != ():
         ScrCmds.raiseException(self.AFH_error[0], self.AFH_error[1])


class CclearanceDictionary:
   """
      #######################################################################################################################
      #
      #                  Class:  clearanceDictionary
      #
      #        Original Author:  Michael T. Brady
      #
      #            Description:  Provides data structure to hold clearance data by head by measured position
      #
      #######################################################################################################################

   """
   def __init__(self, ):
      self.clrDict = {}

   def setClrDict(self, hdKey, MeasNum, RdClr, WrtLoss, WHClr, iZone):
      if not self.clrDict.has_key(hdKey):
         self.clrDict[hdKey] = {}
      self.clrDict[hdKey][MeasNum] = [RdClr, WrtLoss, WHClr, iZone]

   def setDACDict(self, hdKey, MeasNum, whDAC, hoDAC, iZone):
      if not self.clrDict.has_key(hdKey):
         self.clrDict[hdKey] = {}
      self.clrDict[hdKey][MeasNum] = [whDAC, hoDAC, iZone]


class CdPES(CAFH):
   """
      dPES class provides methods and attributes to the contact detection framework
   @type dHdContactDict: dict
   @param dHdContactDict: Dictionary containing contact detection data for all heads test-tracks
   """
   TEMP_QUAL_RANGE = TP.TccCal_temp_range #Single sided range of temperatures to auto-load the afh-SIM data
   #into the active dictionary for. Will allow coarse contact override if loaded.

   def __init__(self, masterHeatPrm, defOCLIM = 16):
      """__init__: Intializes the class level variables.
      """
      CAFH.__init__(self)
      self.updateRequiredAFH_Tables(spc_id = 1)

      self.defOCLIM = defOCLIM   #Default off track limit for servo unsafe

      self.consCheckSum = {}
      self.measured_contact = {}    # used to determine if the current contact DAC values was just measured(1) or re-displayed(0)
      self.dHdContactDict = {}
      self.heatOnlyDict = {}
      self.clrDict = CclearanceDictionary()

      # other class links
      self.oServoFunctions =  CServoFunc()
      self.oUtility = Utility.CUtility()
      self.dth = FSO.dataTableHelper()
      self.frm = CAFH_Frames()
      self.lmt = MathLib.CDAC_limits()
      self.mth = MathLib.CAFH_Computations()
      self.temp = CTemperature()

      if (testSwitch.FE_0159597_357426_DSP_SCREEN == 1) and (self.dut.nextState == 'AFH1_DSP'):
         objMsg.printMsg("DSPtruthValue AFH is %x" % TD.Truth)
         self.headList = TD.Truth #range(TD.Truth,TD.Truth+1)
      else:
         self.headList = range(objDut.imaxHead)   # getZoneTable()  # needs to be called prior to the init so that this is valid

      self.masterHeatPrm = masterHeatPrm
      self.reportOption = 1
      self.curHDATemp = None
      self.AFH_State = AFH_UNINITIALIZED_AFH_STATE

      self.AFH_State = self.frm.set_AFH_StateFromStateTableStateName()
      self.spcID = int(self.AFH_State * 10000)   # this statement must be after setting the internal AFH State

      self.exceptionPath1 = 0
      self.uniformTrack = 0   # radius flag used to determine if WHIRP/HIRP CYL term should be treated as a uniform cyl/pre-VBAR cyl(1) or logical cyl (0)
      self.P_DAC_CLR_spcID = 0
      self.exceptionPath2 = 0 # returned from st(35) if servo goes into Twiddle state and contact is declared
      self.unitTestLoop = {}
      self.totalST35Calls = 0
      self.unitTest = {}
      self.unitTest['ClrList'] = []
      self.numMeasPos = len(TP.maskParams['tracks'])

      # update the master dictionaries
      self.dHdContactDict = {}
      self.heatOnlyDict = {}
      self.availableActuationModes = [AFH_WHMODE, AFH_HOMODE]
      self.skip_HO_mode = DISABLE
      self.mth.clearAllCachedTrackInformation()

      from AFH_mainLoop import CAFH_test135
      self.oAFH_mainLoop = CAFH_test135()

      testSwitch.getmd5SumForAFH_flags()
      if ( testSwitch.extern.AFH_MAJ_REL_NUM == 0 ) and ( testSwitch.extern.AFH_MIN_REL_NUM == 0 ):
         objMsg.printMsg("AFH Release 0.0 Detected.  Most likely caused by SF3 flg.py file not loaded.  Fail.")
         ScrCmds.raiseException(11044, 'Invalid AFH Release Number 0.0 detected!')  # should never execute this


   def updateRequiredAFH_Tables(self, spc_id = -1):
      # 3. zone table
      self.mFSO.getZoneTable()


   def __contactDictUpd(self, contactDict, hdKey , MeasNum, iTrack, contactVal, temp ):
      if not contactDict.has_key(hdKey):
         contactDict[hdKey] = {}
      contactDict[hdKey][MeasNum] = [iTrack, contactVal, temp]


   def addContactDictsToFrames(self, consistCheckIndex, curHead):
      """
      Note:   States in the StateTable are encoded for FH purposes to mean the following
      First  FH Test(AFH1, T02) is AFH_State index 0
      Second FH Test(AFH2, T09)  is AFH_State index 1
      """
      if DEBUG == 1:
         objMsg.printMsg('addContactDictsToFrames/Updating clearance data to drive marshall object (/var/merlin/results/cell_address/DRIVE_SN_serialize.log;  self.dHdContactDict : %s, self.heatOnlyDict: %s' % (str(self.dHdContactDict), str(self.heatOnlyDict)))

      try:
         self.dut.objData.marshallObject['dHdContactDict'] = self.dHdContactDict
      except:
         pass

      try:
         self.dut.objData.marshallObject['heatOnlyDict'] = self.heatOnlyDict
      except:
         pass

      self.dut.objData.serialize()

      #Add data to AFH SIM local file
      self.frm.dPesSim.DPES_HEADER['HdCount'] = len(self.dHdContactDict.keys())

      mode = AFH_MODE #  Represents if frames data is dPES contact detection data 0, or field adjust data 1
      self.frm.dPesSim.DPES_HEADER['Measurements Per Head'] = len(self.dHdContactDict[curHead].keys())
      for meas in self.dHdContactDict[curHead].keys():
         self.frm.dPesSim.addMeasurement(
            mode, self.dut.nextState[-4:], self.AFH_State, consistCheckIndex,
            curHead,
            self.mFSO.trackToZone(curHead, self.dHdContactDict[curHead][meas][AFH_TRACK]),
            self.dHdContactDict[curHead][meas][AFH_TRACK],
            int(meas),
            self.dHdContactDict[curHead][meas][AFH_TEMP],
            self.dHdContactDict[curHead][meas][AFH_DET],
            self.heatOnlyDict[curHead][meas][AFH_DET],
            self.clrDict.clrDict[curHead][meas][AFH_RdClr],
            self.clrDict.clrDict[curHead][meas][AFH_WHClr],
            self.clrDict.clrDict[curHead][meas][AFH_WrtLoss],
            )


   def calc_Clr_by_pos(self, iHead, heatOnlyDict, writePHeatDict, coefs, heatMode):
      """displayDPESTable prints the contact detection dictionary using objMsg.

      """
      if testSwitch.virtualRun:
         self.updateRequiredAFH_Tables()

         zt = self.dut.dblData.Tables(TP.zone_table['table_name']).tableDataObj()        
         wps = self.dut.dblData.Tables('P172_WRITE_POWERS').tableDataObj()
         sysZt = self.dut.dblData.Tables(TP.zone_table['resvd_table_name']).tableDataObj()
         
      prm = TP.CalcClrByPos_Prm_49.copy()

      self.clrDict.clrDict[iHead] = heatOnlyDict[iHead].copy()

      for meas in heatOnlyDict[iHead].keys():
         if not testSwitch.virtualRun:

            prm['TEST_HEAD'] = iHead
            prm['HT_ONLY_TEST_CYL'] = self.oUtility.ReturnTestCylWord(heatOnlyDict[iHead][meas][AFH_TRACK])
            prm['WRT_HT_TEST_CYL'] = self.oUtility.ReturnTestCylWord(writePHeatDict[iHead][meas][AFH_TRACK])

            prm['HT_ONLY_CONTACT_DAC'] = heatOnlyDict[iHead][meas][AFH_DET]
            prm['WRT_HT_CONTACT_DAC'] = writePHeatDict[iHead][meas][AFH_DET]
            self.St(prm)
            t49 = self.dut.dblData.Tables('P049_HEAT_CLEARANCE').tableDataObj()
            st_RdClr = float(self.dth.getRowFromTable_byTable(t49)['HT_ONLY_CLR'])
            st_WrtLoss = float(self.dth.getRowFromTable_byTable(t49)['WRT_LOSS'])
            st_WHClr = float(self.dth.getRowFromTable_byTable(t49)['WRT_HT_CLR'])
            st_Zone = float(self.dth.getRowFromTable_byTable(t49)['HT_ONLY_ZONE'])
         else:
            HOtrk = heatOnlyDict[iHead][meas][AFH_TRACK]

            temp_heatClr = self.mth.getHeaterClr(heatOnlyDict[iHead][meas][AFH_DET], iHead, HOtrk, coefs['HTR_PTP_COEF'][heatMode], self.lmt.maxclr_USL)

            iZone = self.mFSO.trackToZone(iHead, HOtrk)

            try:    nrzFreq = zt[self.dth.getFirstRowIndexFromTable_byZone(zt, iHead, iZone)]['NRZ_FREQ']
            except: nrzFreq = sysZt[self.dth.getFirstRowIndexFromTable_byZone(sysZt, iHead, iZone)]['NRZ_FREQ']

            Iw = self.dth.getRowFromTable(wps, iHead, iZone)['WRT_CUR']
            Ovs = self.dth.getRowFromTable(wps, iHead, iZone)['OVS_WRT_CUR']
            Ovd = self.dth.getRowFromTable(wps, iHead, iZone)['OVS_DUR']
            HirpWriteLoss = self.mth.CalcClearanceLoss(iHead, writePHeatDict[iHead][meas][AFH_TRACK], nrzFreq, Iw, Ovs, Ovd, coefs['WRT_PTP_COEF'][heatMode])

            writeLoss = self.mth.fromHirpWriteLossToWriteLoss(iHead, writePHeatDict[iHead][meas][AFH_TRACK], HirpWriteLoss)

            temp_wphClr = self.mth.getWriteClr(iHead, writePHeatDict[iHead][meas][AFH_TRACK], \
               coefs['WRT_HTR_PTP_COEF'][heatMode], writeLoss, writePHeatDict[iHead][meas][AFH_DET], self.lmt.maxclr_USL)

            st_RdClr = temp_heatClr
            st_WrtLoss = HirpWriteLoss
            st_WHClr = temp_wphClr
            st_Zone = iZone

         self.clrDict.setClrDict(iHead, meas, st_RdClr, st_WrtLoss, st_WHClr, st_Zone)
         # end of for each meas loop

      objMsg.printMsg('calc_Clr_by_pos/self.clrDict.clrDict  : %s' % str(self.clrDict.clrDict), objMsg.CMessLvl.IMPORTANT)


   def findLowestRROTrack(self, startTrack, endTrack, stepSize, iHead, pesPrm, testedTracks = []):
      """
      findLowestRROTrack recieves a input range of tracks to verify are acceptable for performing dPES on per the requirements defined in the inPrm
      @type lInRange: list
      @param lInRange: List of track
      @type iTrackStep: integer
      @param iTrackStep: integer that defines the spacing between tracks in the range to look for PES values.
      @type dPesPrm: dict
      @param dPesPrm: Dictionary parameter input as defined for test33 in ESG documentation.
      @return: List of Lists: [RRO, nRRO] values by track and head
      """
      lowestRRO = 100
      lowestRROTrk = -1
      VEOnly_RROStack = [3.2, 4.1, 7.9, 6.2]

      if startTrack < 1:
         startTrack = 1
      if endTrack > self.dut.maxTrack[iHead] - 1:
         endTrack = self.dut.maxTrack[iHead] - 1

      trackRange = range(startTrack, endTrack, stepSize)

      objMsg.printMsg("findLowestRROTrack/ Hd: %s trackRange: %s" % (iHead, trackRange))

      for iTestTrack in trackRange:
         if iTestTrack not in testedTracks:
            #Range Check the test tracks to make sure we don't go out-of bounds
            if iTestTrack < 1:
               iTestTrack = 1
            elif iTestTrack > self.dut.maxTrack[iHead] - 1:
               iTestTrack = self.dut.maxTrack[iHead] - 1

            tstPrm = {}
            tstPrm.update(pesPrm)
            tstPrm.update({"TEST_CYL" : self.oUtility.ReturnTestCylWord(iTestTrack),
                           "END_CYL"  : self.oUtility.ReturnTestCylWord(iTestTrack),
                           "TEST_HEAD": iHead})
            tstPrm['CWORD1'] = 0x8036
            self.oServoFunctions.St(tstPrm)
            RRO = DriveVars['H'+str(iHead)+'_RRO']
            if testSwitch.virtualRun:
               if VEOnly_RROStack != []:
                  RRO = VEOnly_RROStack.pop()
               else:
                  RRO = DriveVars['H'+str(iHead)+'_RRO']
            if RRO <= lowestRRO or lowestRROTrk == -1:
               lowestRRO = RRO
               lowestRROTrk = iTestTrack

            # restricted tracks
            if lowestRROTrk == 0:
               lowestRROTrk = 1
            if lowestRROTrk == self.dut.maxTrack[iHead]:
               lowestRROTrk = self.dut.maxTrack[iHead] - 1

      return lowestRROTrk, lowestRRO


   def __setmaxHeaterDAC(self, preamp_DACs_backoff_from_Max_DAC_T35):
      self.maxHeaterDACAllowed = int(self.lmt.maxDAC - preamp_DACs_backoff_from_Max_DAC_T35)
      if (self.maxHeaterDACAllowed < 0) or (self.maxHeaterDACAllowed > self.lmt.maxDAC):
         self.maxHeaterDACAllowed = self.lmt.maxDAC


   def findClrID_V3BAR(self, preamp_DACs_backoff_from_Max_DAC_T35, heatSearchParams, retryParams, pesPrm, basePrm, maskParams, coefs, lubePrm, V3BAR_phase5_params, \
      heatMode, deStroke_drive_185_params):

      # check to ensure that we are in the proper AFH state
      self.mth.clearAllCachedTrackInformation()

      self.frm.readFramesFromCM_SIM()
      stateList = self.frm.getAFHStateList()
      if stateList != []:  # if not in the first AFH state
         objMsg.printMsg('Not in correct state to run V3BAR')
         return -1
      self.frm.clearFrames()

      self.__setmaxHeaterDAC(preamp_DACs_backoff_from_Max_DAC_T35)
      setStroke_trkList = []
      contactDetectParameters = basePrm, maskParams, retryParams, heatSearchParams, pesPrm, coefs, lubePrm, heatMode, V3BAR_phase5_params['actuation_mode']

      unitTestClrList_backup = self.oUtility.copy(self.unitTest['ClrList'])
      for iHead in self.headList:
         self.unitTest['ClrList'] = self.oUtility.copy(unitTestClrList_backup)

         self.V3BAR_clrMaxPos = []
         self.V3BAR_trkMaxPos = []

         # Calculate a default maximum nominal track based on P172_ZONE_TBL
         maxPos = len(maskParams['tracks']) - 1
         maxPosNomTrk = int(maskParams['scaling'][maxPos] * self.dut.maxTrack[iHead])
         maxPosNomTrk_old = maxPosNomTrk
         nominalTrkStepSizeToSkip = V3BAR_phase5_params['amount_of_stroke_to_skip'] * maxPosNomTrk


         ID_search_coarse_retry = 0
         numAdditionalIterations = self.numberAdditionalIterations(iHead, V3BAR_phase5_params)
         ID_search_coarse_retry_limit = V3BAR_phase5_params['ID_search_coarse_retry_limit'] + numAdditionalIterations

         objMsg.printMsg("V3BAR/Hd: %s, ID_search_coarse_retry_limit: %s, V3BAR_phase5_params: %s, numAdditionalIterations: %s" % \
            (iHead, ID_search_coarse_retry_limit, V3BAR_phase5_params['ID_search_coarse_retry_limit'], numAdditionalIterations))

         state = 'measure_maxPosFirstTime'
         while (state != 'end'):

            if state == 'measure_maxPosFirstTime':
               # measure maxPos for the first time
               offset = 0
               (maxPosClr, maxPosNomTrk) = self.ID_track_limit(iHead, maxPosNomTrk, maxPos, \
                  nominalTrkStepSizeToSkip, V3BAR_phase5_params['num_skips'], offset, V3BAR_phase5_params['min_clr'], \
                  V3BAR_phase5_params['num_invalid_DAC_retries'], \
                  contactDetectParameters)
               state = 'measure_maxPosMinus1FirstTime'

            if state == 'measure_maxPosMinus1FirstTime':
               # measure maxPos - 1 for the first time
               maxPosMinus1_nomTrk = int(maskParams['scaling'][maxPos - 1] * self.dut.maxTrack[iHead])
               offset = 0
               iPos = maxPos - 1
               (maxPosMinus1_clr, maxPosMinus1_nomTrk) = self.ID_track_limit(iHead, maxPosMinus1_nomTrk, iPos, \
                  0, 1, offset, V3BAR_phase5_params['min_clr'], V3BAR_phase5_params['num_invalid_DAC_retries'], \
                  contactDetectParameters)
               state = 'check_if_done'

            if state == 'check_if_done':   # state 3
               # call check_if_done()
               status, maxPosNomTrk, path = self.check_if_done(maxPosNomTrk, maxPosMinus1_clr, V3BAR_phase5_params)
               if ( status == AFH_V3BAR_STATUS_GIVE_UP ):
                  state = 'end'
               if status == PASS:
                  state = 'saveMaxTrk'
               else:
                  state = 'areRetriesExceeded'

            if state == 'areRetriesExceeded': # state 3A
               ID_search_coarse_retry += 1
               if ID_search_coarse_retry > ID_search_coarse_retry_limit:

                  # check first to determine if the drive should be failed for contamination
                  if abs(maxPosMinus1_clr - maxPosClr) > V3BAR_phase5_params['pos3_minus_pos2_clr_limit']:
                     ScrCmds.raiseException(14683, "V3BAR - drive failed for ID contamination Hd: %s, pos2 clr: %s minus pos3 clr %s greater than limit: %s" % \
                        (iHead, maxPosMinus1_clr, maxPosClr, V3BAR_phase5_params['pos3_minus_pos2_clr_limit']))  # 14683

                  # if no contamination, then simply fail for exceeding the retries
                  ScrCmds.raiseException(14706, "V3BAR - drive failed number of retries exceeded!  Hd: %s, retries %s, limit: %s" % \
                     (iHead, ID_search_coarse_retry, ID_search_coarse_retry_limit))
               else:
                  state = 'remeasureMaxPos'

            if state == 'remeasureMaxPos':   # state 4

               # if yes, then delta between 2 and 3 is still too high, continue looking farther from ID until delta is smaller
               offset = 1
               (maxPosClr, maxPosNomTrk) = self.ID_track_limit(iHead, maxPosNomTrk, maxPos, \
                  nominalTrkStepSizeToSkip, V3BAR_phase5_params['num_skips'], offset, 0, V3BAR_phase5_params['num_invalid_DAC_retries'], \
                  contactDetectParameters)

               # ------>  Add entry to DBLog table here to set minor health bit
               curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(35)
               self.dut.objSeq.curRegSPCID = 1
               self.dut.dblData.Tables('P_MINOR_FAIL_CODE').addRecord(
                  {
                  'HD_PHYS_PSN':  self.dut.LgcToPhysHdMap[iHead],
                  'ERROR_CODE':  12185,
                  'SPC_ID': self.spcID,
                  'OCCURRENCE': occurrence,  # This mismatch needs to be addressed all over the code because the generating code is incorrect TODO
                  'SEQ':curSeq,
                  'TEST_SEQ_EVENT': testSeqEvent,
                  'HD_LGC_PSN':  iHead,
                  'TEST_NUMBER': 35,
                  'FAIL_DATA':   "Hd %s ID Roll-off %s exceeds limit of %s" % (iHead, maxPosMinus1_clr - maxPosClr, V3BAR_phase5_params['delta_Z']),
                  })
               objMsg.printDblogBin(self.dut.dblData.Tables('P_MINOR_FAIL_CODE'))
               objMsg.printMsg('findClrID_V3BAR/ hd: %s destroking required to avoid extreme ID roll-off' % str(iHead))
               state = 'check_if_done_afterRetries'

            if state == 'check_if_done_afterRetries': # state 5
               # call check_if_done()
               status, maxPosNomTrk, path = self.check_if_done(maxPosNomTrk, maxPosMinus1_clr, V3BAR_phase5_params)
               if status == PASS:
                  state = 'reMeasureMaxPosMinus1'  # go on to state 6
               else:
                  state = 'areRetriesExceeded'  # go back to state 3A

            if state == 'reMeasureMaxPosMinus1':  # state 6
               maxPosMinus1_nomTrk = int(maskParams['scaling'][maxPos - 1] * self.dut.maxTrack[iHead])
               offset = 0
               iPos = maxPos - 1
               (maxPosMinus1_clr, maxPosMinus1_nomTrk) = self.ID_track_limit(iHead, maxPosMinus1_nomTrk, iPos, \
                  0, 1, offset, V3BAR_phase5_params['min_clr'], V3BAR_phase5_params['num_invalid_DAC_retries'], \
                  contactDetectParameters)
               state = 'check_if_done'

            if state == 'saveMaxTrk':  # state 7
               objMsg.printMsg("ID_track_limit/ check_if_done() Hd: %s chose %s" %(iHead, path))
               setStroke_trkList.append(maxPosNomTrk)
               state = 'checkForContamination'

            if state == 'checkForContamination':
               if abs(maxPosMinus1_clr - maxPosClr) > V3BAR_phase5_params['pos3_minus_pos2_clr_limit']:
                  ScrCmds.raiseException(14683, "V3BAR - drive failed for ID contamination Hd: %s, pos2 clr: %s minus pos3 clr %s greater than limit: %s" % \
                     (iHead, maxPosMinus1_clr, maxPosClr, V3BAR_phase5_params['pos3_minus_pos2_clr_limit']))  # 14683
               state = 'end'
         # end of for loop iHead

      maxPosNomTrk_AllHeads = min(setStroke_trkList)
      self.set_stroke(maxPosNomTrk_AllHeads, deStroke_drive_185_params)
      self.mFSO.getZoneTable()
      retrieveWPs_prm = TP.RetrieveWPs_Prm_172.copy()
      retrieveWPs_prm.update({ 'spc_id': self.spcID })
      self.St( retrieveWPs_prm )
      objMsg.printMsg('findClrID_V3BAR/Summary set the maximum nominal logical cyl for all heads from: %s to: %s' % (maxPosNomTrk_old, maxPosNomTrk_AllHeads))
      self.mth.clearAllCachedTrackInformation()

      return maxPosNomTrk_AllHeads

      # end of method findClrID_V3BAR() ------------------------------------------------------------------------------>


   def ID_track_limit(self, iHead, nominal_cyl, iPos, nominalTrkStepSizeToSkip, num_skips, offset, min_clr_limit, \
      num_invalid_DAC_retries, contactDetectParameters):

      basePrm, maskParams, retryParams, heatSearchParams, pesPrm, coefs, lubePrm, heatMode, actuation_mode = contactDetectParameters

      invalidValues = [self.lmt.maxDAC, ]
      for ID_search_fine_retry in range(num_skips):
         temp_DAC = invalidValues[0]
         invalid_DAC_retry = 0
         while (temp_DAC in invalidValues) and (invalid_DAC_retry < num_invalid_DAC_retries):
            # or (temp_DAC in invalidValues)
            test_cyl = int(nominal_cyl - ((ID_search_fine_retry + offset) * nominalTrkStepSizeToSkip))

            #set-up call for 135

            if testSwitch.virtualRun == 1:
               self.oAFH_mainLoop.unitTest['errorCode'] = []
            self.oAFH_mainLoop.findClearance_V3BAR( iHead, test_cyl )

            temp_DAC, temp_Clr = self.oAFH_mainLoop.get135ResultsForV3BAR()

            if testSwitch.virtualRun == 1:
               if len(self.unitTest['ClrList']) > 0:
                  temp_Clr = self.unitTest['ClrList'].pop()
                  temp_DAC = -1
               else:
                  temp_Clr = 0.4
                  temp_DAC = -1

               if testSwitch.AFH_ENABLE_ANGSTROMS_SCALER_USE_254 == 1:
                  temp_Clr *= AFH_MICRO_INCHES_TO_ANGSTROMS

            # Test 35/135 results completely returned as of this point.

            if testSwitch.virtualRun == 1:
               if len(self.unitTest['ClrList']) > 0:
                  temp_Clr = self.unitTest['ClrList'].pop()
                  temp_DAC = -1

            if iPos == len(maskParams['tracks']) - 1:
               self.V3BAR_clrMaxPos.append(temp_Clr)
               self.V3BAR_trkMaxPos.append(test_cyl)

            try:  radius = self.mth.UniformTrackToRadius(iHead, test_cyl)
            except: radius = -1.0   # if this conversion fails then continue as this is only used for data reporting to assist HDIG.

            output = ( iHead, test_cyl, iPos, radius, temp_DAC, temp_Clr, min_clr_limit, self.V3BAR_trkMaxPos )
            objMsg.printMsg('ID_track_limit/ V3BAR hd: %s, trk: %6s, iPos: %s, radius: %f, DAC: %s, Clr: %6f, LSL: %6f, trk stack: %s' % output )
            if testSwitch.virtualRun == 1:
               if 'output' not in self.unitTest.keys():
                  self.unitTest['output'] = []
               self.unitTest['output'].append(output)

            ######################## DBLOG Implementaion- Setup
            curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(35)

            self.dut.dblData.Tables('P_DESTROKE_CLEARANCE').addRecord(
               {
               'SPC_ID'             : str(self.spcID),
               'OCCURRENCE'         : occurrence,
               'SEQ'                : curSeq,
               'TEST_SEQ_EVENT'     : testSeqEvent,
               'HD_PHYS_PSN'        :self.dut.LgcToPhysHdMap[iHead],
               'HD_LGC_PSN'         : iHead,
               'LGC_TRK_NUM'        : test_cyl,
               'NOM_CYL'            : test_cyl,
               'RADIUS'             : self.oUtility.setDBPrecision(radius, 0, 3),
               'ACTUATION_MODE'     : str(actuation_mode),
               'AFH_ZONE'           : self.oUtility.setDBPrecision(iPos, 2, 0),
               'HEATER_DAC'         : self.oUtility.setDBPrecision(temp_DAC, 5, 0),
               'CLEARANCE'          : self.oUtility.setDBPrecision(temp_Clr, 0, 8),
               'MIN_CLEARANCE_SPEC' : self.oUtility.setDBPrecision(min_clr_limit, 0, 8),
               })

            objMsg.printDblogBin(self.dut.dblData.Tables('P_DESTROKE_CLEARANCE'))

            if temp_Clr > min_clr_limit:
               return(temp_Clr, test_cyl)

            if (temp_DAC in invalidValues):
               invalid_DAC_retry += 1
               # find new track location
               if FAST_DEBUG == 0:
                  trDict = self.findLowestRROTrack(
                     range(test_cyl - retryParams['minSearch'], test_cyl + retryParams['maxSearch']),
                     retryParams['stepSearch'], iHead, pesPrm, test_cyl)
                  objMsg.printMsg("Retrying on track %s (RRO:%s)" % (str(trDict['track']), str(trDict['val'])))

            # end of while loop invalid DAC retry
         # end of while loop

      objMsg.printMsg('ID_track_limit/ V3BAR - drive failed to find new maximum nominal logical cyl')
      objMsg.printMsg('ID_track_limit/ trk: %s, clr: %s LESS THAN limit: %s' % (str(test_cyl), str(temp_Clr), str(min_clr_limit)))
      ScrCmds.raiseException(11186, "V3BAR - drive flying too low at extreme ID.  clr: %s LESS THAN %s limit" % (str(temp_Clr), str(min_clr_limit)))


   def set_stroke(self, maxPosNomTrk, deStroke_drive_185_params):
      deStroke_drive_185_params.update({'TEST_CYL': self.oUtility.ReturnTestCylWord(maxPosNomTrk)})
      objMsg.printMsg('V3BAR - destroke all heads to nominal logical cyl: %s !!!' % str(maxPosNomTrk))
      try:

         prm_mc = hex(self.dut.objData.retrieve('maxCyl_185'))
         nbits = len(prm_mc)
         #objMsg.printMsg("self.dut.maxCyl_185 %s" % str(self.dut.maxCyl_185))
         lst_MaxCyl = (eval(prm_mc[:nbits-4]), eval(''.join(["0x", prm_mc[nbits-4:nbits]]))) # create a tuple of MAx Cyl
         TP.deStroke_drive_185_params.update({'CWORD1':0x2800})
         TP.deStroke_drive_185_params.update({'MAX_CYL':lst_MaxCyl})
         #objMsg.printMsg("MAX_CYL_185 %s" % str(TP.deStroke_drive_185_params['MAX_CYL']))
      except:
         objMsg.printMsg("Destroke limit not applied")
         pass

      self.St(deStroke_drive_185_params)


   def check_if_done(self, maxPosNomTrk, maxPosMinus1_clr, prms):
      """
      Algorithm is per Bruce Emo's email from 11-Dec 2007
      """

   ##   Constants
   ##   Threshold = 7 angstroms = 0.0276 microinches.
   ##
   ##   Variables
   ##   clearatpos4  = array[1..10] of real       // array of clearance measurements at position 4 (ID)
   ##   trackatpos4  = array[1..10] of longint    // array of nominal track positions for measurements at position 4 (ID)
   ##   numatpos4    = integer                    // number of measurements done at position 4
   ##   clearatpos3  = real                       // clearance measurement at position 3
   ##   maxPosNomTrk     = longint                // the nominal track that the ID should be set to if status = done
   ##
   ##   After measurement(s) done at position 4 and have a measurement above the "minimum clearance limit"
   ##   After first measurement done at position 3
   ##   Call "check_if_done" routine to determine if another measurement must be made

      delta_Z = prms['delta_Z']
      # constants
      done = PASS
      notdone = FAIL
      path = ""

      status = notdone
      # have we already done more than one measurement at position 4?

      if len(self.V3BAR_clrMaxPos) != len(self.V3BAR_trkMaxPos):
         ScrCmds.raiseException(11044, 'V3BAR - len(self.V3BAR_clrMaxPos) != len(self.V3BAR_trkMaxPos)')  # !!! something went really wrong with the algorithm fail immediately

      numatpos4 = len(self.V3BAR_clrMaxPos) - 1

      if len(self.V3BAR_clrMaxPos) == 1:
         if ((maxPosMinus1_clr - self.V3BAR_clrMaxPos[numatpos4]) < -1.0 * prms['primary_delta_Z']):
            path = "Path 4"   # quit.  Do not keep trying on this head.
            maxPosNomTrk = self.V3BAR_trkMaxPos[ 0 ]
            status = AFH_V3BAR_STATUS_GIVE_UP

         if ( (abs(maxPosMinus1_clr - self.V3BAR_clrMaxPos[numatpos4]) < prms['primary_delta_Z']) ):
            status = done     # met the criteria
            maxPosNomTrk = self.V3BAR_trkMaxPos[numatpos4]
            path = "Path 1"
      else:
         if ( (maxPosMinus1_clr - self.V3BAR_clrMaxPos[numatpos4]) < -1.0 * delta_Z ):
            path = "Path 4"   # quit.  Do not keep trying on this head.
            maxPosNomTrk = self.V3BAR_trkMaxPos[ 0 ]
            status = AFH_V3BAR_STATUS_GIVE_UP

         # more than one measurement - check both pos3 vs pos 4 and delta between last two measurements
         if ((maxPosMinus1_clr - self.V3BAR_clrMaxPos[numatpos4]) < delta_Z) and \
            ((self.V3BAR_clrMaxPos[numatpos4] - self.V3BAR_clrMaxPos[numatpos4 - 1]) < delta_Z):
            status = done     # met the criteria
            # check if difference between last two measurements is small
            if ((self.V3BAR_clrMaxPos[numatpos4] - self.V3BAR_clrMaxPos[numatpos4 - 1]) < (prms['path2_scaler1'] * delta_Z)):    # path2_scaler1 = 0.333
               # it is small, use prior measurement location to set the stroke
               maxPosNomTrk = self.V3BAR_trkMaxPos[numatpos4 - 1]
               path = "Path 2A"
            else:
               maxPosNomTrk = self.V3BAR_trkMaxPos[numatpos4]
               path = "Path 2B"
         else:
            # didn't meet the first criteria, try the second
            # check if below twice the delta_Z and delta is below 2/3 the delta_Z
            if ((maxPosMinus1_clr - self.V3BAR_clrMaxPos[numatpos4]) < (delta_Z * prms['path2_scaler2'])) and \
               ((self.V3BAR_clrMaxPos[numatpos4] - self.V3BAR_clrMaxPos[numatpos4 - 1]) < (prms['path2_scaler3'] * delta_Z)):    # path2_scaler2 = 2
               # met the criteria                                                                                        # path2_scaler3 = 0.667
               status = done
               # check if difference between last two measurements is small
               if ((self.V3BAR_clrMaxPos[numatpos4] - self.V3BAR_clrMaxPos[numatpos4 - 1]) < (prms['path2_scaler4'] * delta_Z)): # path2_scaler3 = 0.333
                  # it is small, use prior measurement location to set the stroke
                  maxPosNomTrk = self.V3BAR_trkMaxPos[numatpos4 - 1]
                  path = "Path 2C"
               else:
                  maxPosNomTrk = self.V3BAR_trkMaxPos[numatpos4]
                  path = "Path 2D"
            else:
               if len(self.V3BAR_clrMaxPos) >= prms['path3_num_iterations']:  # path3_num_iterations = 8
                  rng1 = max(self.V3BAR_clrMaxPos) - min(self.V3BAR_clrMaxPos)
                  if (rng1 < (prms['path3_scaler1'] * delta_Z)):              # path3_scaler1 = 0.5,
                     status = done  # met the criteria
                     for pos in range(0, len(self.V3BAR_clrMaxPos)):
                        rng2 = max(self.V3BAR_clrMaxPos[pos:]) - min(self.V3BAR_clrMaxPos[pos:])
                        if (rng2 < (prms['path3_scaler2'] * delta_Z)):        # path3_scalar2 = 0.25
                           maxPosNomTrk = self.V3BAR_trkMaxPos[pos]
                           path = "Path 3A"
                           break # intended to break out of the for loop
      return status, maxPosNomTrk, path


   def numberAdditionalIterations(self, iHead, V3BAR_phase5_params):
      #1.  get # of tracks gained
      trkTbl1 = self.dut.dblData.Tables('P185_TRK_0_V3BAR_CALHD').tableDataObj()
      trksGainedID = float(self.dth.getRowFromTable_byHead(trkTbl1, iHead)['NUM_TRKS_GAINED_AT_ID'])

      #2.  get total # of tracks
      trkTbl2 = self.dut.dblData.Tables('P185_DEFAULTS').tableDataObj()
      totalVCATPhysicalTrks = float(self.dth.getRowFromTable_byTable(trkTbl2)['DFLT_MAX_CYLINDER'])

      #3.  compute # of steps to increase
      number_additional_iterations = int((trksGainedID/totalVCATPhysicalTrks) / float(V3BAR_phase5_params['amount_of_stroke_to_skip']))
      objMsg.printMsg("V3BAR/ Hd: %s, number_additional_iterations: %s, trksGainedID: %s, totalVCATPhysicalTrks: %s, amount_of_stroke_to_skip: %s" % \
            (iHead, number_additional_iterations, trksGainedID, totalVCATPhysicalTrks, V3BAR_phase5_params['amount_of_stroke_to_skip']))
      return number_additional_iterations


   def calculateClearanceByZoneAndSetHeatersUsingTest49(self, updateClearance, spc_id = 0):
      if (self.AFH_State in [ 3 ]):
         objMsg.printMsg("skipping calculation of clearance in state: %s" % (self.dut.nextState))
         # note: this will override what updateClearance is set to.
         return -1

      if spc_id == 0:
         spc_id = self.spcID + 1

      self.frm.openFilePtrsForSelfTestToReadSIMFileDirectly()

      calcClrByZone_prm = TP.CalcClrByZone_Prm_49.copy()
      calcClrByZone_prm.update({ 'spc_id': spc_id })
      self.St( calcClrByZone_prm )
      self.frm.closeFilePtrsForSelfTestToReadSIMFileDirectly()

      afh_workingAdapts_prm = TP.AFH_WorkingAdapts_Prm_172.copy()
      afh_workingAdapts_prm.update({ 'spc_id': spc_id })
      afh_clearance_prm = TP.AFH_Clearance_Prm_172.copy()
      afh_clearance_prm.update({ 'spc_id': spc_id })
      self.St( afh_workingAdapts_prm )
      self.St( afh_clearance_prm )

      if updateClearance == ON:
         objMsg.printMsg("Saving working RAP values including clearance and heater values to FLASH")
         self.mFSO.saveRAPtoFLASH()
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

      spc_id += 100
      afh_workingAdapts_prm.update({ 'spc_id': spc_id })
      afh_clearance_prm.update({ 'spc_id': spc_id })
      self.St( afh_workingAdapts_prm )
      self.St( afh_clearance_prm )


   def setClearanceTargets(self, afhClearanceZone, afhZonePrm, zoneUpdateList, dacMeasScaleFactor = 255.0, hd=None):
      """
      Set HGA clearance targets.. inputs don't conform to MCT-> use u" number and it will be converted
      """

      if testSwitch.AFH_ENABLE_ANGSTROMS_SCALER_USE_254 == 1:
         dacMeasScaleFactor = 1
      else:
         dacMeasScaleFactor = AFH_ANGSTROMS_PER_MICROINCH

      setPrm = {}
      setPrm.update(afhClearanceZone)
      if hd != None:
         setPrm['HEAD_RANGE'] = hd
      if testSwitch.FE_0203247_463655_AFH_ENABLE_WGC_CLR_SETTING_SUPPORT:
         setPrm1 = TP.afhTargetWGC_by_zone

      ClrAdj = 0
      if 'LSI5230' in self.dut.PREAMP_TYPE and self.dut.PREAMP_REV <= 3:
         ClrAdj = 2

      if len(afhZonePrm["TGT_WRT_CLR"]) == len(afhZonePrm["TGT_MAINTENANCE_CLR"]) == len(afhZonePrm["TGT_PREWRT_CLR"]) == len(afhZonePrm["TGT_RD_CLR"]):
         if testSwitch.FE_0261922_305538_CONSOLIDATE_AFH_TARGET_ZONES:
            # ========= New method, consolidate all zone bit masks to single T178 call for the same setting ==========
            zipAfh = zip(afhZonePrm['TGT_WRT_CLR'], afhZonePrm['TGT_MAINTENANCE_CLR'], afhZonePrm['TGT_PREWRT_CLR'], afhZonePrm['TGT_RD_CLR'])
            sortedZn = {}
            for zn, clr in enumerate(zipAfh): # group by clr settings, values = 64-bit zone mask
               if clr in sortedZn:  sortedZn[clr].append(zn) 
               else: sortedZn[clr] = [zn] 

            # sortedZn = hold the 64-bit zone mask, grouped by clr settings, e.g. {(16, 16, 16, 16): 0x10000000, (18, 18, 18, 18): 0x40000000, (15, 15, 15, 15): 0x8FFFFFFF, (17, 17, 17, 17): 0x20000000}
            for clr in sortedZn:
               if testSwitch.AFH_ENABLE_ANGSTROMS_SCALER_USE_254:
                  if min(clr) < 1.0:
                     ScrCmds.raiseException(11044, \
                        'AFH target clearance should NOT be less than 1 ANGSTROM with flag AFH_ENABLE_ANGSTROMS_SCALER_USE_254 enabled!')

               setPrm["TGT_WRT_CLR"] = (int(round((clr[0] + ClrAdj) * dacMeasScaleFactor)),)
               setPrm["TGT_MAINTENANCE_CLR"] = (int(round((clr[1] + ClrAdj) * dacMeasScaleFactor)),)
               setPrm["TGT_PREWRT_CLR"] = (int(round((clr[2] + ClrAdj) * dacMeasScaleFactor)),)
               setPrm["TGT_RD_CLR"] = (int(round((clr[3] + ClrAdj) * dacMeasScaleFactor)),)
               if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
                  #bit mask & bit mask ext param is no longer supported
                  if 'BIT_MASK' in setPrm:     del setPrm['BIT_MASK'] 
                  if 'BIT_MASK_EXT' in setPrm: del setPrm['BIT_MASK_EXT']
                  if testSwitch.extern.FE_0270095_504159_SUPPORT_LOOPING_ZONE_T178:
                     for startZn, endZn in \
                        Utility.CUtility().convertZoneListToZoneRange(sortedZn[clr]):
                        setPrm['ZONE'] = (startZn << 8) + endZn
                        self.St(setPrm)
                  else: #trunk backward compability
                     for zn in sortedZn[clr]:
                        setPrm['ZONE'] = zn
                        self.St(setPrm)
               else:
                  setPrm['BIT_MASK_EXT'], setPrm['BIT_MASK'] = Utility.CUtility().convertListTo64BitMask(sortedZn[clr]) 
                  self.St(setPrm)

               ## Initial WGC value as TGT_WRT_CLR
               ## Once WGC feature is fully implement, this parameter will be intialized only in InitRAP
               if testSwitch.FE_0203247_463655_AFH_ENABLE_WGC_CLR_SETTING_SUPPORT:
                  try:
                     setPrm1["C_ARRAY1"][9] = setPrm["TGT_WRT_CLR"][0]
                     if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
                        #bit mask & bit mask ext param is no longer supported
                        if 'BIT_MASK' in setPrm1:     del setPrm1['BIT_MASK'] 
                        if 'BIT_MASK_EXT' in setPrm1: del setPrm1['BIT_MASK_EXT']
                        if testSwitch.extern.FE_0270095_504159_SUPPORT_LOOPING_ZONE_T178:
                           for startZn, endZn in \
                              Utility.CUtility().convertZoneListToZoneRange(sortedZn[clr]):
                              setPrm1['ZONE'] = (startZn << 8) + endZn
                              self.St(setPrm1)
                     else:
                        setPrm1["BIT_MASK"] = setPrm["BIT_MASK"]
                        setPrm1["BIT_MASK_EXT"] = setPrm["BIT_MASK_EXT"]
                        self.St(setPrm1)
                  except: # fail safe
                     pass

         else:
            # ========= Old method, individually call T178 for each zone ==========
            for i in zoneUpdateList:
               if testSwitch.AFH_ENABLE_ANGSTROMS_SCALER_USE_254 == 1:
                  if ((afhZonePrm["TGT_WRT_CLR"][i] < 1.0) or (afhZonePrm["TGT_MAINTENANCE_CLR"][i] < 1.0 ) \
                        or (afhZonePrm["TGT_PREWRT_CLR"][i] < 1.0 ) or (afhZonePrm["TGT_RD_CLR"][i] < 1.0 )):
   
                     ScrCmds.raiseException(11044, 'AFH target clearance should NOT be less than 1 ANGSTROM with flag AFH_ENABLE_ANGSTROMS_SCALER_USE_254 enabled!')
   
               setPrm["TGT_WRT_CLR"] = (int(round((afhZonePrm["TGT_WRT_CLR"][i] + ClrAdj)*dacMeasScaleFactor)),)
               setPrm["TGT_MAINTENANCE_CLR"] = (int(round((afhZonePrm["TGT_MAINTENANCE_CLR"][i] + ClrAdj)*dacMeasScaleFactor)),)
               setPrm["TGT_PREWRT_CLR"] = (int(round((afhZonePrm["TGT_PREWRT_CLR"][i] + ClrAdj)*dacMeasScaleFactor)),)
               setPrm["TGT_RD_CLR"] = (int(round((afhZonePrm["TGT_RD_CLR"][i] + ClrAdj)*dacMeasScaleFactor)),)
               if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
                  MaskList = Utility.CUtility().convertListToZoneBankMasks(zoneUpdateList)
                  objMsg.printMsg("MaskList = %s" % MaskList)
                  for bank,list in MaskList.iteritems():
                     if list:
                        objMsg.printMsg("list = %s" % list) 
                        setPrm['BIT_MASK_EXT'], setPrm['BIT_MASK'] = Utility.CUtility().convertListTo64BitMask(list)
                        setPrm['ZONE_MASK_BANK'] = bank
                        objMsg.printMsg("setPrm = %s" % setPrm)
                        self.St(setPrm)
               else:
                  setPrm['BIT_MASK_EXT'], setPrm['BIT_MASK'] = Utility.CUtility().convertListTo64BitMask(zoneUpdateList)
                  self.St(setPrm)
   
               ## Initial WGC value as TGT_WRT_CLR
               ## Once WGC feature is fully implement, this parameter will be intialized only in InitRAP
               if testSwitch.FE_0203247_463655_AFH_ENABLE_WGC_CLR_SETTING_SUPPORT:
                  try:
                     setPrm1["C_ARRAY1"][9] = setPrm["TGT_WRT_CLR"][0]
                     if i < 32:
                        setPrm1["BIT_MASK"] = setPrm["BIT_MASK"]
                        setPrm1["BIT_MASK_EXT"] = (0,0)
                     else:
                        setPrm1["BIT_MASK"] = (0,0)
                        setPrm1["BIT_MASK_EXT"] = Utility.CUtility().ReturnTestCylWord(2**(i-32))
                     self.St(setPrm1)
                  except:
                     pass
      else:
         ScrCmds.raiseException(12179, "From TestParameters parameter lengths do not match")


class CAFH_AR_Shared_Functions:
   """
   """
   def __init__(self, ):
      """__init__: Intializes the class level variables.
      """
      self.dut = objDut

   def logTestTracks(self, head_name, track):
      """
      Logs the test tracks that are used for test 35 in the process
      @type head_name: name of the head
      @param head_name: string containing the name of the head
      @note head_name: example of input 0
      @type track: Logical Track
      @param track: integer base 10 containing the track number
      """
      # if the track is already in the list then don't add it.

      # for power loss recovery
      try:
         if not self.dut.objData.marshallObject.__contains__('LogTest35_Tracks'):
            self.dut.objData.marshallObject['LogTest35_Tracks'] = {}
      except: pass

      try:
         if not self.dut.objData.marshallObject['LogTest35_Tracks'][head_name].__contains__(track):
            self.dut.objData.marshallObject['LogTest35_Tracks'][head_name].append(track)
      except:
         # if this failed it would be because the head index has not yet been created.
         # initialize self.dut.objData.marshallObject['LogTest35_Tracks'] to a dictionary by head of empty lists
         for iHead in range(self.dut.imaxHead):
            self.dut.objData.marshallObject['LogTest35_Tracks'][iHead] = []

         # if the track is already in the list don't add it again
         if not self.dut.objData.marshallObject['LogTest35_Tracks'][head_name].__contains__(track):
            self.dut.objData.marshallObject['LogTest35_Tracks'][head_name].append(track)

      self.dut.objData.marshallObject['LogTest35_Tracks'][head_name].sort()


   # ------------------------>  End of Class CdPES  <---------------------------------------------------------------------
