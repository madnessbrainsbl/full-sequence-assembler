#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2009, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: AFH Screens Module
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/03/18 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/TSE/Work/JinHao/PF3/BOB/scripts/AFH_Screens_T135.py $
# $Revision: #1 $
# $DateTime: 2016/03/18 00:38:55 $
# $Author: jinhao.h.hu $
# $Header: //depot/TSE/Work/JinHao/PF3/BOB/scripts/AFH_Screens_T135.py#1 $
# Level: 3

#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
import ScrCmds
from Process import CProcess
import Utility
import FSO
from AFH_SIM import CAFH_Frames
from Drive import objDut
import MessageHandler as objMsg
from AFH_constants import *
from Temperature import CTemperature
import MathLib
from AFH import CclearanceDictionary


#######################################################################################################################
#
#                  class:  CAFH_Screens
#
#        Original Author:  Michael T. Brady
#
#            Description:  AFH Screens
#
#          Prerrequisite:  In most cases valid AFH SIM binary data loaded in memory.
#
#######################################################################################################################

class CAFH_Screens(CProcess):
   TEMP_QUAL_RANGE = TP.TccCal_temp_range #Single sided range of temperatures to auto-load the afh-SIM data
   def __init__(self):
      CProcess.__init__(self)
      self.dut = objDut

      # libraries to link in.
      self.frm = CAFH_Frames()
      self.mFSO = FSO.CFSO()
      self.clrDict = CclearanceDictionary()

      # variables to initialize
      self.headList = range(objDut.imaxHead)   # note imaxHead is the number of heads
      self.numMeasPos = len(TP.maskParams['tracks'])
      self.temp = CTemperature()
      self.spcID = 1


      self.AFH_State = AFH_UNINITIALIZED_AFH_STATE
      self.AFH_State = self.frm.set_AFH_StateFromStateTableStateName()
      self.spcID = int(self.AFH_State * 10000)   # this statement must be after setting the internal AFH State
      testSwitch.getmd5SumForAFH_flags()
      if ( testSwitch.extern.AFH_MAJ_REL_NUM == 0 ) and ( testSwitch.extern.AFH_MIN_REL_NUM == 0 ):
         objMsg.printMsg("AFH Release 0.0 Detected.  Most likely caused by SF3 flg.py file not loaded.  Fail.")
         ScrCmds.raiseException(11044, 'Invalid AFH Release Number 0.0 detected!')  # should never execute this


   def SaveTCC_toRAP(self, head, tcc1, tcc2):
      """
      #########################################################################################
      #
      #               Function:  SaveTCC
      #
      #        Original Author:  Michael T. Brady
      #
      #            Description:  save TCC values to RAP
      #
      #                  Input:  tcc1 and tcc2
      #
      #           Return Value:  None
      #
      #########################################################################################

      """

      # Update the AFH Temperature Correction Coefficients
      tc1Mask            = (0x0000, 0x0002,)
      tc2Mask            = (0x0000, 0x0004,)
      dTcMask            = (0x0000, 0x0008,)
      dThMask            = (0x0000, 0x0010,)
      COLD_TEMP_DTC_mask = (0x0000, 0x0020,)
      HOT_TEMP_DTH_mask  = (0x0000, 0x0040,)

      TC_Coeff = TP.TC_Coeff_Prm_178.copy()
      TC_Coeff['HEAD_RANGE'] = 2**head # Head mask of heads to update with input parms

      TC_Coeff['CWORD1'] = TC_Coeff["CWORD1"][0] | 0x0800

      TC_Coeff.update({"BIT_MASK": tc1Mask,
         "TEMPERATURE_COEF" : self.oUtility.returnIntMantWord(tcc1),})
      self.St(TC_Coeff)
      objMsg.printMsg("forceTcs2EqualZero == 1 so force 0 non-linear component", objMsg.CMessLvl.DEBUG)
      tcc2 = 0
      TC_Coeff.update({"BIT_MASK": tc2Mask,
         "TEMPERATURE_COEF" : self.oUtility.returnIntMantWord(tcc2),})
      #Save coeficcients
      self.St(TC_Coeff)

      tccDict_178 = TP.tccDict_178
      # save dTc and dTh
      if 'dTc' in tccDict_178:
         objMsg.printMsg("SaveTCC/ head: %2s, BIT_MASK: %10s, TEMPERATURE_COEF: %0.10f" % ( head, dTcMask, tccDict_178['dTc']) )
         TC_Coeff.update({"BIT_MASK": dTcMask, "TEMPERATURE_COEF" : self.oUtility.returnIntMantWord(tccDict_178['dTc']),})
         self.St(TC_Coeff)
      if 'dTh' in tccDict_178:
         objMsg.printMsg("SaveTCC/ head: %2s, BIT_MASK: %10s, TEMPERATURE_COEF: %0.10f" % ( head, dThMask, tccDict_178['dTh']) )
         TC_Coeff.update({"BIT_MASK": dThMask, "TEMPERATURE_COEF" : self.oUtility.returnIntMantWord(tccDict_178['dTh']),})
         self.St(TC_Coeff)
      if 'COLD_TEMP_DTC' in tccDict_178:
         objMsg.printMsg("SaveTCC/ head: %2s, BIT_MASK: %10s, TEMPERATURE_COEF: %0.10f" % ( head, COLD_TEMP_DTC_mask, tccDict_178['COLD_TEMP_DTC']) )
         TC_Coeff.update({"BIT_MASK": COLD_TEMP_DTC_mask, "TEMPERATURE_COEF" : self.oUtility.returnIntMantWord(tccDict_178['COLD_TEMP_DTC']),})
         self.St(TC_Coeff)
      if 'HOT_TEMP_DTH' in tccDict_178:
         objMsg.printMsg("SaveTCC/ head: %2s, BIT_MASK: %10s, TEMPERATURE_COEF: %0.10f" % ( head, HOT_TEMP_DTH_mask, tccDict_178['HOT_TEMP_DTH']) )
         TC_Coeff.update({"BIT_MASK": HOT_TEMP_DTH_mask, "TEMPERATURE_COEF" : self.oUtility.returnIntMantWord(tccDict_178['HOT_TEMP_DTH']),})
         self.St(TC_Coeff)

      if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT == 1:
         self.St({'test_num':172, 'prm_name': 'Retrieve TC Coefficient', "CWORD1" : (10), 'spc_id': 1, })


   def evalTempCapAllHeads(self, tcc1_modifiedDict, tcc2_dict, tccStructDict, tempSpecDict ):
      """
      #########################################################################################
      #
      #               Function:  evalTempCapAllHeads
      #
      #        Original Author:  Michael T. Brady
      #
      #            Description:  call evalTempCap for all heads
      #
      #                  Input:  tcc1_modifiedDict(dict) - modified TCC1 values
      #                          tcc2_dict(dict) - tcc2 values
      #                          tccStructDict(dict) -
      #                          tempSpecDict(dict) - values needed for temp capability
      #
      #
      #           Return Value:  None
      #
      #########################################################################################
      """

      try:     self.dut.dblData.delTable('P035_TEMP_CAP')
      except:  pass

      for iHead in self.headList:

         self.evalTempCap(iHead, tcc1_modifiedDict[iHead], tcc2_dict[iHead], tccStructDict['dWrtClr1_dict'][iHead].values(),
                          tempSpecDict, self.temp.retHDATemp(certTemp = 1))
         # end of for iHead in self.headList


      # -------------------> display temperature capability <-------------------

      objMsg.printDblogBin(self.dut.dblData.Tables('P035_TEMP_CAP'))


   def evalTempCap(self, iHead, tcc1, tcc2, whClr1, tempSpecDict, certTemp):
      """
      #########################################################################################
      #
      #               Function:  evalTempCap
      #
      #        Original Author:  Michael T. Brady
      #
      #            Description:  compute temperature capability for a specified head
      #
      #                  Input:
      #
      #           Return Value:
      #
      #########################################################################################
      """

      minClr = min(whClr1)    # these should be the CERT temp WH clr values
      maxClr = max(whClr1)

      # --------------> Section 4 - calculate temperature capability for this head <------------------
      high_clr_limit = tempSpecDict['loTemp'][1] # 0.85 uin
      low_clr_limit = tempSpecDict['hiTemp'][1]   # 0 uin

      if tcc1 < 0:
         coldTempCap = MathLib.SolveQuadratic(tcc2, tcc1, maxClr - high_clr_limit, 0) + certTemp
         hotTempCap = MathLib.SolveQuadratic(tcc2, tcc1, minClr - low_clr_limit, 0) + certTemp
      elif tcc1 > 0:
         coldTempCap = MathLib.SolveQuadratic(tcc2, tcc1, minClr - low_clr_limit, 0) + certTemp
         hotTempCap = MathLib.SolveQuadratic(tcc2, tcc1, maxClr - high_clr_limit, 0) + certTemp
      else: # if tcc1 == 0
         coldTempCap = -999
         hotTempCap = 999

      if (coldTempCap < -1000):
         coldTempCap = -1000
         objMsg.printMsg('Calc Cold Temp Cap less than -1000 C, set Cold Temp Cap = -1000 C', objMsg.CMessLvl.IMPORTANT)
      if (hotTempCap > 1000):
         hotTempCap = 1000
         objMsg.printMsg('Calc Hot Temp Cap greater than 1000 C, set Hot Temp Cap = 1000 C', objMsg.CMessLvl.IMPORTANT)


      # --------------> Section 5 - add temperature capability info to DBLOG <------------------
      self.dut.dblData.Tables('P035_TEMP_CAP').addRecord(
         {
         'SPC_ID': self.spcID,
         'OCCURRENCE': self.dut.objSeq.getOccurrence(),
         'SEQ': self.dut.objSeq.getSeq(),
         'TEST_SEQ_EVENT': self.dut.objSeq.getTestSeqEvent(35),
         'HD_PHYS_PSN':self.dut.LgcToPhysHdMap[iHead],
         'HD_LGC_PSN':iHead,
         'COLD_CAP':self.oUtility.setDBPrecision(coldTempCap, 8, 0),
         'HOT_CAP':self.oUtility.setDBPrecision(hotTempCap, 8, 0),
         } )
      objMsg.printMsg('evalTempCap/ Hd: %2s, tcc1: %12.9f, tcc2: %12.9f, cold Temp Cap: %6.1f, hot Temp Cap: %6.1f' % \
         (iHead, tcc1, tcc2, coldTempCap, hotTempCap))
      return coldTempCap, hotTempCap


   def MeasureTCC(self, tccDict, tempSpecDict, maskParams, nTempCERT):
      """
      Algorithm
      =========
         Picks through the clearance values in Frames data and calculates the TCC slopes using
         olympic scoring.
         If only 1 temp is present then a default TCS value is loaded specified by tccDict['default']
         Currently only TCC1 is calculated.
         TCC2 is hard-coded to 0.  This will be changed when a decision is made in the F3 code about how to calculate these values

      Failure Criteria
      ================
         Function fails based on tempSpecDict: if extrapolated clearance is different than the clearance limit the failing clearance is evaluated
         based on the centerTemp.

      Parameters
      ==========
         @param tempSpecDict: Dictionary of extrapolated temperature failing points and clearances 'name':(Temp, clearance); EG... 'lo':[(0,)]
      """
      # checks for common failure modes

      if testSwitch.FE_0131890_341036_AFH_ADD_FOLDING_OF_TCS_CALC == 1:
         tcs_allHeads = self.getComputeSaveAndScreenTCS( tccDict, tempSpecDict, nTempCERT )

      else:
         if len(self.frm.dPesSim.DPES_FRAMES) < (self.dut.imaxHead * 4):
            self.frm.display_frames()
            ScrCmds.raiseException(11044, 'Insufficent Frames data found to calculate TCC values') # at this point print out as much as you can about the local data structures to assist in debug

         # find states to use for TCC calculation
         state_list = []
         for frame in self.frm.dPesSim.DPES_FRAMES:
            if (frame['mode'] == AFH_MODE) and (not frame['stateIndex'] in state_list):
               state_list.append(frame['stateIndex'])
         first_stateIndex = state_list[len(state_list) - 2]
         second_stateIndex = state_list[len(state_list) - 1]
         if testSwitch.FE_0130771_341036_AFH_FORCE_USE_AFH3_AND_AFH4_IN_TCS_CALC == 1:
            if first_stateIndex != stateTableToAFH_internalStateNumberTranslation['AFH3']:
               ScrCmds.raiseException(11044, 'Data for AFH3 not found.')
            if second_stateIndex != stateTableToAFH_internalStateNumberTranslation['AFH4']:
               ScrCmds.raiseException(11044, 'Data for AFH4 not found.')

         # checks for common failure modes
         if len(state_list) < 2:
            self.frm.display_frames()
            ScrCmds.raiseException(11044, 'Insufficent Frames data found to calculate TCC values') # at this point print out as much as you can about the local data structures to assist in debug

         # initialize values
         if ConfigVars[CN].get('BenchTop', 0) != 0:   # if running in benchTop mode then force 1 Temp CERT
            objMsg.printMsg('Warning!!! - 1 Temp CERT calibration forced due to BenchTop configVar != 0', objMsg.CMessLvl.IMPORTANT)
            nTempCERT = 1

         try:     self.dut.dblData.delTable('P035_TEMP_CAP')
         except:  pass
         tcs_allHeads = []

         for iHead in self.headList:
            objMsg.printMsg("MeasureTCC/ Hd: %s  *************************************************************************" % ( iHead ))
            dWrtClr1 = {}
            dWrtClr2 = {}
            dTemp1 = {}
            dTemp2 = {}
            dcdt = {}

            for frame in self.frm.dPesSim.DPES_FRAMES:
               iPos = int(frame['Zone'])

               if ( (frame['mode'] == AFH_MODE) and (frame['stateIndex'] == first_stateIndex) and (frame['LGC_HD'] == iHead)):
                  dWrtClr1[iPos] = frame['Write Clearance']
                  dTemp1[iPos] = frame['dPES Measure Temp']

               if ( (frame['mode'] == AFH_MODE) and (frame['stateIndex'] == second_stateIndex) and (frame['LGC_HD'] == iHead)):
                  dWrtClr2[iPos] = frame['Write Clearance']
                  dTemp2[iPos] = frame['dPES Measure Temp']

            AllPossiblePositions = []
            if 'onlyChkZonesList' in tccDict.keys():
               AllPossiblePositions = tccDict['onlyChkZonesList']
            else:
               AllPossiblePositions = dWrtClr1.keys() + dWrtClr2.keys()

            listCommonPos = []
            for iPos in AllPossiblePositions:
               if (iPos in dWrtClr1.keys()) and (iPos in dWrtClr2.keys()) and (iPos not in listCommonPos):
                  listCommonPos.append(iPos)

            listCommonPos.sort()

            if len(listCommonPos) < AFH_TCS_MINIMUM_NUM_COMMON_VALID_TEST_135_MEASUREMENTS:
               objMsg.printMsg("MeasureTCC/ Hd: %s less than 3 common positions %s detected." % ( iHead, listCommonPos ))

               tcc1 = TP.tccDict_178['TCS1']
               tcc2 = 0
               objMsg.printMsg("MeasureTCC/ Hd: %s, Skipping computation of TCS.  Relying on default for TCC1 (TCC2 is hard-coded at 0) tcc1: %10.7f, tcc2: %10.7f" %
                     ( iHead, tcc1, tcc2 ) )
               continue

            if nTempCERT == 1:
               tcc1 = tccDict['default']
               tcc2 = 0

               for iPos in listCommonPos:
                  dcdt[iPos] = 0.0

            if nTempCERT >= 2:
#CHOOI-30Mar17 OffSpec
#                if abs(MathLib.median(dTemp1.values()) - MathLib.median(dTemp2.values())) < TP.min_temp_diff_between_hot_cold and ConfigVars[CN].get('hotBenchTop', 0) == 0:
#                   ScrCmds.raiseException(12517, 'Insufficent (%s C) temperature separation found between hot and cold states' % \
#                      ( abs(MathLib.median(dTemp1.values()) - MathLib.median(dTemp2.values())) )) # at this point print out as much as you can about the local data structures to assist in debug

               # -------------------> Section 3 Calculate tcc1, tcc2 <-------------------

               objMsg.printMsg('Choosing 2 Temp Cert', objMsg.CMessLvl.IMPORTANT)
               for iPos in listCommonPos:
                  dcdt[iPos] = (dWrtClr2[iPos] - dWrtClr1[iPos]) / float(dTemp2[iPos] - dTemp1[iPos])

               dcdtList = dcdt.values()
               dcdtList.pop(dcdtList.index(min(dcdtList)))
               dcdtList.pop(dcdtList.index(max(dcdtList)))
               tcc1 = MathLib.mean(dcdtList)      # linear term
               tcc2 = 0                            # 2nd order term

               if testSwitch.FE_0159623_396795_SET_OUT_OF_BOUNDS_TCS_VALUES_TO_MEAN == 1:
                  if testSwitch.FE_0165968_396795_FAIL_ON_ABSOLUTE_TCS_VALUE_BEFORE_FOLDING:
                     # Per Allan Luk, fail drive if absolue TCS value > allowable before folding
                     if 'TCS1_AbsFailureLimitDuringTCSFolding' not in tccDict:
                        ScrCmds.raiseException(11044, 'Flag FE_0165968_396795_FAIL_ON_ABSOLUTE_TCS_VALUE_BEFORE_FOLDING requires test parameter TCS1_AbsFailureLimitDuringTCSFolding to be present.')
                     if abs(tcc1) >= tccDict['TCS1_AbsFailureLimitDuringTCSFolding']:
                        ScrCmds.raiseException(14722, 'Hd: %s TCS: %s exceeded spec limit: %s' % (str(iHead), str(tcc1), str(tccDict['TCS1_AbsFailureLimitDuringTCSFolding'])))

                  if ('TCS1_UpperLimitSetToMean' not in tccDict) or ('TCS1_LowerLimitSetToMean' not in tccDict) or ('default' not in tccDict):
                     ScrCmds.raiseException(11044, 'Flag FE_0159623_396795_SET_OUT_OF_BOUNDS_TCS_VALUES_TO_MEAN requires default, TCS1_Lower(&upper)LimitSetToMean parameters be present.')
                  if tcc1 > tccDict['TCS1_UpperLimitSetToMean']:
                     tcc1 = TP.tccDict_178['default']
                  if tcc1 < tccDict['TCS1_LowerLimitSetToMean']:
                     tcc1 = TP.tccDict_178['default']

               for iPos in listCommonPos:
                  dcdt[iPos]
                  objMsg.printMsg('MeasureTCC/ Hd: %s, Meas: %s, whClr1: %6f uin, temp1: %s C, whClr2: %6f uin, temp2: %s C, dcdt: %10.7f uin/C, tcc1: %10.7f, tcc2: %10.7f' % \
                     (iHead, iPos, dWrtClr1[iPos], dTemp1[iPos], dWrtClr2[iPos], dTemp2[iPos], dcdt[iPos], tcc1, tcc2), objMsg.CMessLvl.IMPORTANT)

            self.SaveTCC_toRAP(iHead, tcc1, tcc2)        # this saves values to RAP
            if 'TCS1_USL' in tccDict.keys() and 'TCS1_LSL' in tccDict.keys() and 'TCS2_USL' in tccDict.keys() and 'TCS2_LSL' in tccDict.keys():
               if (tcc1 > tccDict['TCS1_USL']):
                  ScrCmds.raiseException(14722, 'Hd: %s TCS: %s exceeded upper spec limit: %s' % (str(iHead), str(tcc1), str(tccDict['TCS1_USL'])))
               if (tcc1 < tccDict['TCS1_LSL']):
                  ScrCmds.raiseException(14722, 'Hd: %s TCS: %s exceeded lower spec limit: %s' % (str(iHead), str(tcc1), str(tccDict['TCS1_LSL'])))
               if (tcc2 > tccDict['TCS2_USL']):
                  ScrCmds.raiseException(14722, 'Hd: %s TCS: %s exceeded upper spec limit: %s' % (str(iHead), str(tcc2), str(tccDict['TCS2_USL'])))
               if (tcc2 < tccDict['TCS2_LSL']):
                  ScrCmds.raiseException(14722, 'Hd: %s TCS: %s exceeded lower spec limit: %s' % (str(iHead), str(tcc2), str(tccDict['TCS2_LSL'])))

            tcs_allHeads.append([iHead, tcc1, tcc2])
            self.evalTempCap(iHead, tcc1, tcc2, dWrtClr1.values(), tempSpecDict, self.temp.retHDATemp(certTemp = 1))
            # end of for head loop

         self.mFSO.saveRAPtoFLASH()                #Save the settings from RAP to flash (non-volatile)

         # -------------------> Section 4 display temperature capability <-------------------


         objMsg.printDblogBin(self.dut.dblData.Tables('P035_TEMP_CAP'))

         #Report coefficients
         RetrieveTcCoeff_prm = TP.Retrieve_TC_Coeff_Prm_172.copy()
         RetrieveTcCoeff_prm['spc_id'] = self.spcID
         self.St( RetrieveTcCoeff_prm )

      return tcs_allHeads

      #----------------->   end of method MeasureTCC()   <------------------------------


   def getComputeSaveAndScreenTCS(self, tccDict, tempSpecDict, nTempCERT):
      """
      #######################################################################################################################
      #
      #               Function:  getComputeSaveAndScreenTCS
      #                          the refactored "MeasureTCC"
      #
      #        Original Author:  Michael T. Brady
      #
      #            Description:  Get, compute, save to FLASH, and screen the TCC data
      #
      #          Prerrequisite:  Nominally Run AFH 3 and AFH 4
      #
      #                  Input:  None
      #
      #                 Return:  tccDict(dict)
      #                          tempSpecDict(dict) - values needed for the evaulate temperature capability.
      #                          nTempCERT(int)
      #
      #              Algorithm:
      #                          Picks through the clearance values in Frames data and calculates the TCC slopes using
      #                          olympic scoring.
      #                          If only 1 temp is present then a default TCS value is loaded specified by tccDict['default']
      #                          Currently only TCC1 is calculated.
      #                          TCC2 is hard-coded to 0.  This will be changed when a decision is made in the F3 code about how to calculate these values
      #
      #
      #######################################################################################################################

      """

      # The new TCS function
      # --------------------
      #
      # 1.  get the dcdt data
      tccStructDict = self.getTCCDataFromAFHFrames( tccDict )

      # 2.  compute the olympic scored TCC1
      tcc1_unModifiedDict, tcc1_modifiedDict, tcc2_dict = self.computeOlympicScoredTCC( tccStructDict, tccDict, nTempCERT )

      # 3.  save TCC1 data by head to FLASH
      for iHead in self.headList:
         self.SaveTCC_toRAP(iHead, tcc1_modifiedDict[iHead], tcc2_dict[iHead])        # this saves values to RAP

      self.mFSO.saveRAPtoFLASH()                #Save the settings from RAP to flash (non-volatile)

      #Report coefficients
      RetrieveTcCoeff_prm = TP.Retrieve_TC_Coeff_Prm_172.copy()
      RetrieveTcCoeff_prm['spc_id'] = self.spcID
      self.St( RetrieveTcCoeff_prm )

      # 4.  screen the data      
      self.screenHardFailTCC1_andTCC2( tcc1_unModifiedDict, tcc2_dict, tccDict )

      # Note: should also refactor for W+H vs. HO
      #
      self.evalTempCapAllHeads( tcc1_modifiedDict, tcc2_dict, tccStructDict, tempSpecDict )

      return tcc1_unModifiedDict, tcc1_modifiedDict, tcc2_dict


   def getTCCDataFromAFHFrames( self, tccDict ):
      """
      #######################################################################################################################
      #
      #               Function:  getTCCDataFromAFHFrames
      #
      #        Original Author:  Michael T. Brady
      #
      #            Description:  Gets the TCC data
      #
      #          Prerrequisite:  Nominally Run AFH 3 and AFH 4
      #
      #                  Input:  None
      #
      #                 Return:  tccStructDict(dict)  A structure of other dictionaries holding the raw data to be computed.
      #
      #######################################################################################################################
      """

      # checks for common failure modes

      if len(self.frm.dPesSim.DPES_FRAMES) < (self.dut.imaxHead * 4):
         self.frm.display_frames()
         ScrCmds.raiseException(11044, 'Insufficent Frames data found to calculate TCC values') # at this point print out as much as you can about the local data structures to assist in debug

      if testSwitch.AFH3_ENABLED:
         prior_AFH_state = 'AFH3'
      else:
         if testSwitch.IN_DRIVE_AFH_COEFF_PER_HEAD_GENERATION_SUPPORT:
            prior_AFH_state = 'AFH1'
         else:
            prior_AFH_state = 'AFH2'

      # find states to use for TCC calculation
      if testSwitch.FE_AFH3_TO_IMPROVE_TCC == 1:
         state_list = {}
         first_stateIndex = {}
         second_stateIndex = {}
         for iHead in self.headList:
            state_list[iHead] = []
            for frame in self.frm.dPesSim.DPES_FRAMES:
               if (frame['mode'] == AFH_MODE) and  (frame['LGC_HD'] == iHead) and (not frame['stateIndex'] in state_list[iHead]):
                  state_list[iHead].append(frame['stateIndex'])
         for iHead in self.headList:
            first_stateIndex[iHead] = state_list[iHead][len(state_list[iHead]) - 2]
            second_stateIndex[iHead] = state_list[iHead][len(state_list[iHead]) - 1]
            if testSwitch.FE_0130771_341036_AFH_FORCE_USE_AFH3_AND_AFH4_IN_TCS_CALC == 1:
               if first_stateIndex[iHead] != stateTableToAFH_internalStateNumberTranslation[prior_AFH_state]:
                  ScrCmds.raiseException(11044, 'Data of %s not found.' %prior_AFH_state)
               if second_stateIndex[iHead] != stateTableToAFH_internalStateNumberTranslation['AFH4']:
                  ScrCmds.raiseException(11044, 'Data for AFH4 not found.')



            # checks for common failure modes
            if len(state_list[iHead]) < 2:
               self.frm.display_frames()
               ScrCmds.raiseException(11044, 'Insufficent Frames data found to calculate TCC values') # at this point print out as much as you can about the local data structures to assist in debug
      else:
         state_list = []
         for frame in self.frm.dPesSim.DPES_FRAMES:
            if (frame['mode'] == AFH_MODE) and (not frame['stateIndex'] in state_list):
               state_list.append(frame['stateIndex'])
         first_stateIndex = state_list[len(state_list) - 2]
         second_stateIndex = state_list[len(state_list) - 1]

         if testSwitch.FE_0130771_341036_AFH_FORCE_USE_AFH3_AND_AFH4_IN_TCS_CALC == 1:
            if first_stateIndex != stateTableToAFH_internalStateNumberTranslation[prior_AFH_state]:
               ScrCmds.raiseException(11044, 'Data of %s not found.' %s)
            if second_stateIndex != stateTableToAFH_internalStateNumberTranslation['AFH4']:
               ScrCmds.raiseException(11044, 'Data for AFH4 not found.')


      # checks for common failure modes
      if len(state_list) < 2:
         self.frm.display_frames()
         ScrCmds.raiseException(11044, 'Insufficent Frames data found to calculate TCC values') # at this point print out as much as you can about the local data structures to assist in debug

      dWrtClr1_dict = {}
      dWrtClr2_dict = {}
      dTemp1_dict = {}
      dTemp2_dict = {}
      commonZoneDict = {}

      for iHead in self.headList:
         dWrtClr1_dict[iHead] = {}
         dWrtClr2_dict[iHead] = {}
         dTemp1_dict[iHead] = {}
         dTemp2_dict[iHead] = {}

         for frame in self.frm.dPesSim.DPES_FRAMES:
            iZone = int(frame['Zone'])
            if testSwitch.FE_AFH3_TO_IMPROVE_TCC == 1:

               if ( (frame['mode'] == AFH_MODE) and (frame['stateIndex'] == first_stateIndex[iHead]) and (frame['LGC_HD'] == iHead) and (frame['Heater Element'] == WRITER_HEATER_INDEX)):
                  dWrtClr1_dict[iHead][iZone] = float(frame['Write Clearance'])
                  dTemp1_dict[iHead][iZone] = frame['dPES Measure Temp']

               if ( (frame['mode'] == AFH_MODE) and (frame['stateIndex'] == second_stateIndex[iHead]) and (frame['LGC_HD'] == iHead) and (frame['Heater Element'] == WRITER_HEATER_INDEX)):
                  dWrtClr2_dict[iHead][iZone] = float(frame['Write Clearance'])
                  dTemp2_dict[iHead][iZone] = frame['dPES Measure Temp']
            else:
               if ( (frame['mode'] == AFH_MODE) and (frame['stateIndex'] == first_stateIndex) and (frame['LGC_HD'] == iHead)):
                  dWrtClr1_dict[iHead][iZone] = float(frame['Write Clearance'])
                  dTemp1_dict[iHead][iZone] = frame['dPES Measure Temp']

               if ( (frame['mode'] == AFH_MODE) and (frame['stateIndex'] == second_stateIndex) and (frame['LGC_HD'] == iHead)):
                  dWrtClr2_dict[iHead][iZone] = float(frame['Write Clearance'])
                  dTemp2_dict[iHead][iZone] = frame['dPES Measure Temp']

         AllPossiblePositions = []
         if 'onlyChkZonesList' in tccDict.keys():
            AllPossiblePositions = tccDict['onlyChkZonesList']
         else:
            AllPossiblePositions = dWrtClr1_dict[iHead].keys() + dWrtClr2_dict[iHead].keys()

         commonZoneDict[ iHead ] = []
         for iZone in AllPossiblePositions:
            if (iZone in dWrtClr1_dict[iHead].keys()) and (iZone in dWrtClr2_dict[iHead].keys()) and (iZone not in commonZoneDict[ iHead ]):
               commonZoneDict[ iHead ].append(iZone)

         commonZoneDict[ iHead ].sort()
         # end of for iHead in self.headList:

      tccStructDict = {}
      tccStructDict['dWrtClr1_dict'] = dWrtClr1_dict
      tccStructDict['dWrtClr2_dict'] = dWrtClr2_dict
      tccStructDict['dTemp1_dict'] = dTemp1_dict
      tccStructDict['dTemp2_dict'] = dTemp2_dict
      tccStructDict['commonZoneDict'] = commonZoneDict

      return tccStructDict


   def computeOlympicScoredTCC(self, tccStructDict, tccDict, nTempCERT ):
      """
      #######################################################################################################################
      #
      #               Function:  computeOlympicScoredTCC
      #
      #        Original Author:  Michael T. Brady
      #
      #            Description:  Compute the TCC using olympic scoring using legacy algorithms.
      #
      #          Prerrequisite:  run getTCCData
      #
      #                  Input:  None
      #
      #                 Return:  tccStructDict(dict)  A structure of other dictionaries holding the raw data to be computed.
      #
      #######################################################################################################################
      """

      # initializations
      dWrtClr1_dict = tccStructDict['dWrtClr1_dict']
      dWrtClr2_dict = tccStructDict['dWrtClr2_dict']
      dTemp1_dict = tccStructDict['dTemp1_dict']
      dTemp2_dict = tccStructDict['dTemp2_dict']
      commonZoneDict = tccStructDict['commonZoneDict']

      dcdtUnModifiedDict = {}
      tcc1_unModifiedDict = {}
      tcc1_modifiedDict = {}
      tcc2_dict = {}
      tcs_allHeads = []

      # initialize values
      if ConfigVars[CN].get('BenchTop', 0) != 0:   # if running in benchTop mode then force 1 Temp CERT
         objMsg.printMsg('Warning!!! - 1 Temp CERT calibration forced due to BenchTop configVar != 0', objMsg.CMessLvl.IMPORTANT)
         nTempCERT = 1


      for iHead in self.headList:
         skipTCS_calculation = False
         dcdtUnModifiedDict[iHead] = {}

         tcc1_unModifiedDict[iHead] = 0.0
         tcc1_modifiedDict[iHead] = 0.0
         tcc2_dict[iHead] = 0.0

         if nTempCERT == 1:
            tcc1_unModifiedDict[iHead] = tccDict['TCS1']
            tcc1_modifiedDict[iHead] = tccDict['TCS1']

         if nTempCERT >= 2:
#CHOOI-30Mar17 OffSpec
#             if abs(MathLib.median(dTemp1_dict[iHead].values()) - MathLib.median(dTemp2_dict[iHead].values())) < TP.minTCCTempDifferential and ConfigVars[CN].get('hotBenchTop', 0) == 0:
#                ScrCmds.raiseException(12517, 'Insufficent (%s C) temperature separation found between hot and cold states' % \
#                   ( abs(MathLib.median(dTemp1_dict[iHead].values()) - MathLib.median(dTemp2_dict[iHead].values())) )) # at this point print out as much as you can about the local data structures to assist in debug

            objMsg.printMsg('Choosing 2 Temp Cert', objMsg.CMessLvl.IMPORTANT)

            # unModified values
            for iZone in commonZoneDict[iHead]:
               dcdtUnModifiedDict[iHead][iZone] = (dWrtClr2_dict[iHead][iZone] - dWrtClr1_dict[iHead][iZone]) / float(dTemp2_dict[iHead][iZone] - dTemp1_dict[iHead][iZone])

            if len(commonZoneDict[iHead]) < AFH_TCS_MINIMUM_NUM_COMMON_VALID_TEST_135_MEASUREMENTS:
               objMsg.printMsg("MeasureTCC/ Hd: %s less than 3 common positions %s detected." % ( iHead, commonZoneDict[iHead] ))

               objMsg.printMsg("MeasureTCC/ Hd: %s, Skipping computation of TCS.  Relying on default for TCC1 (TCC2 is hard-coded at 0) tcc1: %10.7f, tcc2: %10.7f" %
                     ( iHead, tcc1_unModifiedDict[iHead], tcc2_dict[iHead] ) )
               skipTCS_calculation = True
               tcc1_unModifiedDict[iHead] =  tccDict['TCS1']
               tcc1_modifiedDict[iHead] =  tccDict['TCS1']

            if skipTCS_calculation == False:
               # compute un-modified TCC1
               dcdtList = dcdtUnModifiedDict[iHead].values()
               dcdtList.pop(dcdtList.index(min(dcdtList)))
               dcdtList.pop(dcdtList.index(max(dcdtList)))
               tcc1_unModifiedDict[iHead] =  MathLib.mean(dcdtList)      # linear term
               tcc1_modifiedDict[iHead] =  MathLib.mean(dcdtList)      # linear term

            # Modified values
            if 'enableModifyTCS_values' in tccDict:
               if tccDict['enableModifyTCS_values'] == 1:

                  if tcc1_modifiedDict[iHead] > tccDict['MODIFIED_SLOPE_USL']:
                     tcc1_modifiedDict[iHead] = tccDict['MODIFIED_SLOPE_USL']

                  if tcc1_modifiedDict[iHead] < tccDict['MODIFIED_SLOPE_LSL']:
                     tcc1_modifiedDict[iHead] = tccDict['MODIFIED_SLOPE_LSL']
            else:
               tccDict['enableModifyTCS_values'] = 0
               tccDict['MODIFIED_SLOPE_USL'] = 999
               tccDict['MODIFIED_SLOPE_LSL'] = -999

            objMsg.printMsg('MeasureTCC')
            objMsg.printMsg('Hd Zone   whClr1 temp1   whClr2 temp2  un-modified_dcdt(u"/C) un-modified_tcc1(u"/C) MODIFIED_SLOPE_LSL MODIFIED_SLOPE_USL modified_tcc1(u"/C)  tcc2(u"/C)')

            for iZone in commonZoneDict[iHead]:
               objMsg.printMsg('%2d %4d %8.6f %5d %8.6f %5d %23.9f %22.9f %14.9f %14.9f %19.9f %10.9f' % \
                  (iHead, iZone, dWrtClr1_dict[iHead][iZone],
                     dTemp1_dict[iHead][iZone], dWrtClr2_dict[iHead][iZone], dTemp2_dict[iHead][iZone],
                     dcdtUnModifiedDict[iHead][iZone], tcc1_unModifiedDict[iHead], tccDict['MODIFIED_SLOPE_LSL'],
                     tccDict['MODIFIED_SLOPE_USL'],  tcc1_modifiedDict[iHead], tcc2_dict[iHead]), objMsg.CMessLvl.IMPORTANT)

               # Must FIX!!!
               # add new process table here

               curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(135)
               setDBPrecision = self.oUtility.setDBPrecision

               self.dut.dblData.Tables('P_AFH_MEASURED_TCC').addRecord(
                  {
                  'HD_PHYS_PSN'    :self.dut.LgcToPhysHdMap[iHead],
                  'DATA_ZONE'      : iZone,
                  'SPC_ID'         : self.spcID,
                  'OCCURRENCE'     : occurrence,
                  'SEQ'            : curSeq,
                  'TEST_SEQ_EVENT' : testSeqEvent,
                  'HD_LGC_PSN'     : iHead,
                  'ACTUATION_MODE' : "WPH",
                  'WRT_CLR_1'      : setDBPrecision( dWrtClr1_dict[iHead][iZone], 0, 9 ),
                  'TEMP_1'         : dTemp1_dict[iHead][iZone],
                  'WRT_CLR_2'      : setDBPrecision( dWrtClr2_dict[iHead][iZone], 0, 9 ),
                  'TEMP_2'         : dTemp2_dict[iHead][iZone],
                  'UNMODIFIED_SLOPE_MSRMNT'     : setDBPrecision( dcdtUnModifiedDict[iHead][iZone], 0, 9 ),
                  'UNMODIFIED_THERMAL_CLR_COEF_1': setDBPrecision( tcc1_unModifiedDict[iHead], 0, 9 ),
                  'MODIFIED_SLOPE_LSL'                : setDBPrecision( tccDict['MODIFIED_SLOPE_LSL'], 0, 9 ),
                  'MODIFIED_SLOPE_USL'                : setDBPrecision( tccDict['MODIFIED_SLOPE_USL'], 0, 9 ),
                  'MODIFIED_THERMAL_CLR_COEF_1'  : setDBPrecision( tcc1_modifiedDict[iHead], 0, 9 ),
                  'THERMAL_CLR_COEF_2'           : setDBPrecision( tcc2_dict[iHead], 0, 9 ),
                  })

      objMsg.printDblogBin(self.dut.dblData.Tables('P_AFH_MEASURED_TCC'))

      return tcc1_unModifiedDict, tcc1_modifiedDict, tcc2_dict


   def screenHardFailTCC1_andTCC2(self, tcc1_dict, tcc2_dict, tccDict ):
      """
      #######################################################################################################################
      #
      #               Function:  screenHardFailTCC1_andTCC2
      #
      #        Original Author:  Michael T. Brady
      #
      #            Description:  screen TCC1 and TCC2.  Also, compute temperature capability
      #
      #          Prerrequisite:
      #
      #                  Input:  tccDict(dict), tempSpecDict(dict)
      #
      #                 Return:
      #
      #######################################################################################################################
      """

      for iHead in self.headList:
         if 'TCS1_USL' in tccDict.keys() and 'TCS1_LSL' in tccDict.keys() and 'TCS2_USL' in tccDict.keys() and 'TCS2_LSL' in tccDict.keys():
            if (tcc1_dict[iHead] > tccDict['TCS1_USL']):
               ScrCmds.raiseException(14722, 'Hd: %s TCS: %s exceeded upper spec limit: %s' % (str(iHead), str(tcc1_dict[iHead]), str(tccDict['TCS1_USL'])))
            if (tcc1_dict[iHead] < tccDict['TCS1_LSL']):
               ScrCmds.raiseException(14722, 'Hd: %s TCS: %s exceeded lower spec limit: %s' % (str(iHead), str(tcc1_dict[iHead]), str(tccDict['TCS1_LSL'])))
            if (tcc2_dict[iHead] > tccDict['TCS2_USL']):
               ScrCmds.raiseException(14722, 'Hd: %s TCS: %s exceeded upper spec limit: %s' % (str(iHead), str(tcc2_dict[iHead]), str(tccDict['TCS2_USL'])))
            if (tcc2_dict[iHead] < tccDict['TCS2_LSL']):
               ScrCmds.raiseException(14722, 'Hd: %s TCS: %s exceeded lower spec limit: %s' % (str(iHead), str(tcc2_dict[iHead]), str(tccDict['TCS2_LSL'])))

      # end of screenHardFailTCC1_andTCC2


   def burnishCheck(self, burnish_params, minClr_params, validState = 0):
      """
      #######################################################################################################################
      #
      #               Function:  burnishCheck
      #
      #        Original Author:  Michael T. Brady
      #
      #            Description:  checks for burnishing on the heads
      #
      #          Prerrequisite:  run FH contact detect at least 2 times
      #
      #                  Input:  burnish_params(dict), minClr_params(dict), validState(int)
      #
      #                 Return:  P_AFH_DH_BURNISH_CHECK or P_BURNISH_CHECK2 DBLog table (DBLog Tbl)
      #
      #######################################################################################################################

      """

      if ( "WRITER_HEATER" in burnish_params.keys() ) or ( "READER_HEATER" in burnish_params.keys() ):
         ScrCmds.raiseException(11044, 'AFH Error.  DH burnish params found in classic T135 single-heater burnish chk routine.')


      if (validState == 0):
         objMsg.printMsg('Skipping burnish check between states %s and %s.  Currently in state: %s' % \
            ( burnish_params['groupA_nth_AFH_state'], burnish_params['groupB_nth_AFH_state'], self.AFH_State))
         return -1

      objMsg.printMsg('burnishCheck/ validState: %s, burnish_params: %s, minClr_params: %s' % (validState, burnish_params, minClr_params))
      self.frm.readFramesFromCM_SIM()
      self.frm.display_frames(2)

      local_clrDict1 = CclearanceDictionary()
      local_clrDict2 = CclearanceDictionary()
      if testSwitch.FE_0133254_357260_CREATE_CLEARANCE_DELTA_TABLE or ( burnish_params.get('comparison_type', '') == 'abs_rddac' ):
         local_DACDict1 = CclearanceDictionary()
         local_DACDict2 = CclearanceDictionary()

      firstState, secondState = -1, -1

      stateList = self.frm.getAFHStateList()
      try:
         firstState = stateList[burnish_params['groupA_nth_AFH_state']-1]
         secondState = stateList[burnish_params['groupB_nth_AFH_state']-1]
      except:
         objMsg.printMsg("burnishCheck/ nth_AFH_state not found!  Current state: %s, stateList: %s, groupA_nth_AFH_state: %s, groupB_nth_AFH_state: %s, firstState: %s, secondState: %s " %
            (self.AFH_State, stateList, burnish_params['groupA_nth_AFH_state'], burnish_params['groupB_nth_AFH_state'], firstState, secondState))
         ScrCmds.raiseException(42187, "burnishCheck/ invalid process parameters!")

      stateTableName = self.dut.nextState
      if stateTableName == 'AFH2B':
         if burnish_params['mode'] == 'burnish':
            firstState = stateTableToAFH_internalStateNumberTranslation['AFH1']
            secondState = stateTableToAFH_internalStateNumberTranslation['AFH2']
         elif burnish_params['mode'] == 'delta_VBAR':
            firstState = stateTableToAFH_internalStateNumberTranslation['AFH2A']
            secondState = stateTableToAFH_internalStateNumberTranslation['AFH2']

      if (len(self.frm.dPesSim.DPES_FRAMES) < (self.dut.imaxHead * self.numMeasPos)):
         ScrCmds.raiseException(42187, 'Insufficent Frames data found to calculate burnish check') # at this point print out as much as you can about the local data structures to assist in debug

      if burnish_params['mode'] == 'burnish':
         desiredAFH_MODE = AFH_MODE
      elif burnish_params['mode'] == 'delta_VBAR':
         desiredAFH_MODE = AFH_MODE_TEST_135_INTERPOLATED_DATA
      else:
         desiredAFH_MODE = AFH_MODE

      for frame in self.frm.dPesSim.DPES_FRAMES:
         for iHead in self.headList:
            if (burnish_params['groupA_consistchk'] == 'First' and frame['consistCheckIndex'] != 0):
               continue

            if ( (frame['mode'] == desiredAFH_MODE) and (frame['stateIndex'] == firstState) and (frame['LGC_HD'] == iHead)):
               local_clrDict1.setClrDict( iHead, frame['Zone'], frame['Read Clearance'], frame['WrtLoss'], frame['Write Clearance'], frame['Zone'] )
               if testSwitch.FE_0133254_357260_CREATE_CLEARANCE_DELTA_TABLE or ( burnish_params.get('comparison_type', '') == 'abs_rddac' ):
                  local_DACDict1.setDACDict( iHead, frame['Zone'], frame['Write Heat Contact DAC'], frame['Heater Only Contact DAC'], frame['Zone'] )

      for frame in self.frm.dPesSim.DPES_FRAMES:
         for iHead in self.headList:
            if (burnish_params['groupB_consistchk'] == 'First' and frame['consistCheckIndex'] != 0):
               continue

            if ( (frame['mode'] == desiredAFH_MODE) and (frame['stateIndex'] == secondState) and (frame['LGC_HD'] == iHead)):
               local_clrDict2.setClrDict( iHead, frame['Zone'], frame['Read Clearance'], frame['WrtLoss'], frame['Write Clearance'], frame['Zone'] )
               if testSwitch.FE_0133254_357260_CREATE_CLEARANCE_DELTA_TABLE or ( burnish_params.get('comparison_type', '') == 'abs_rddac' ):
                  local_DACDict2.setDACDict( iHead, frame['Zone'], frame['Write Heat Contact DAC'], frame['Heater Only Contact DAC'], frame['Zone'] )

      for iHead in self.headList:
         if not (iHead in local_clrDict1.clrDict):
            ScrCmds.raiseException(42187, 'local_clrDict1.clrDict: %s  Hd: %s No data found for burnish Check' % ( local_clrDict1.clrDict, iHead ))
         if not (iHead in local_clrDict2.clrDict):
            ScrCmds.raiseException(42187, 'local_clrDict2.clrDict: %s  Hd: %s No data found for burnish Check' % ( local_clrDict2.clrDict, iHead ))

         # what about the not enough data found case!
         if len(local_clrDict1.clrDict[iHead]) < 2:
            ScrCmds.raiseException(42187, 'local_clrDict1.clrDict: %s  Hd: %s Not enough data found for burnish Check' % ( local_clrDict1.clrDict, iHead ))
         if len(local_clrDict2.clrDict[iHead]) < 2:
            ScrCmds.raiseException(42187, 'local_clrDict2.clrDict: %s  Hd: %s Not enough data found for burnish Check' % ( local_clrDict2.clrDict, iHead ))


      ## Run a quick check to make sure that multiple Temp CERT data is not being compared!
      measTemps = []
      for frame in self.frm.dPesSim.DPES_FRAMES:
         if frame['mode'] == AFH_MODE:
            measTemps.append(frame['dPES Measure Temp'])

      # create a matrix of number of temps, frequency of that temp and sort it from greatest freq to least
      matrixMeasTemps = [[i1, measTemps.count(i1)] for i1 in set(measTemps)]
      matrixMeasTemps.sort(key = lambda x: x[1], reverse=True)
      if DEBUG == 1:
         objMsg.printMsg('matrixMeasTemps  : %s' % str(matrixMeasTemps), objMsg.CMessLvl.DEBUG)

      if len(matrixMeasTemps) == 0:
         ScrCmds.raiseException(11044, 'Error no temperature data found!') # at this point print out as much as you can about the local data structures to assist in debug

      measTemps = []
      measTemps.append(matrixMeasTemps[0][0])

      i1 = 1
      while (i1 < len(matrixMeasTemps)):
         if (abs(matrixMeasTemps[i1][0] - matrixMeasTemps[0][0]) > self.TEMP_QUAL_RANGE):   # if at least 14 oC of sepearation then it's valid
            objMsg.printMsg('Severe Warning!!! Appears that multiple temp CERT data was found in burnish check calculations.', objMsg.CMessLvl.IMPORTANT)
         i1 += 1

      # check for empty data
      if (  (local_clrDict1.clrDict == {}) or (local_clrDict2.clrDict == {})  ):
         ScrCmds.raiseException(42187, 'local_clrDict1.clrDict: %s, local_clrDict2.clrDict: %s; FRAMES data not found for burnish Check... exiting early return -1' % (str(local_clrDict1.clrDict), str(local_clrDict2.clrDict)))

      # lower flying head and writeMargin(another low clr) checks
      if minClr_params['low_flyer_head_check'] == 1:
         for iHead in local_clrDict2.clrDict.keys():
            for meas in local_clrDict2.clrDict[iHead].keys():
               if local_clrDict2.clrDict[iHead][meas][AFH_WHClr] < minClr_params['lowFlyingHeadLimit']:
                  objMsg.printMsg('Head:  %s, Measurement Pos:  %s, Write Clr:  %s, Write Clr LSL %s' % \
                     ( str(iHead), str(meas), str(local_clrDict2.clrDict[iHead][meas][AFH_WHClr]), str(minClr_params['lowFlyingHeadLimit']) ))
                  if testSwitch.AFH2_FAIL_BURNISH_RERUN_AFH1:
                     self.dut.BurnishFailedHeads.append(iHead)
                  ScrCmds.raiseException(11186, "Failed for low flying head.")
               writeMargin = local_clrDict2.clrDict[iHead][meas][AFH_WHClr] - local_clrDict2.clrDict[iHead][meas][AFH_WrtLoss]
               if writeMargin < minClr_params['writeMargin_LSL']:
                  if testSwitch.AFH2_FAIL_BURNISH_RERUN_AFH1:
                     self.dut.BurnishFailedHeads.append(iHead)
                  ScrCmds.raiseException(11186, "Head: %s, Measurement Pos: %s, Write Margin: %s less than Write Margin limit: %s" % \
                     (str(iHead), str(meas), str(writeMargin), str(minClr_params['writeMargin_LSL'])))
         objMsg.printMsg("Low flying head limit check passed.")

      if minClr_params['high_flyer_head_check'] == 1:
         for iHead in local_clrDict2.clrDict.keys():
            for meas in local_clrDict2.clrDict[iHead].keys():
               if local_clrDict2.clrDict[iHead][meas][AFH_WHClr] > minClr_params['highFlyingHeadLimit_WH_USL']:
                  objMsg.printMsg('Head:  %s, Measurement Pos:  %s, Write Clr:  %s, Write Clr USL %s' % \
                     ( str(iHead), str(meas), str(local_clrDict2.clrDict[iHead][meas][AFH_WHClr]), str(minClr_params['highFlyingHeadLimit_WH_USL']) ))
                  if testSwitch.AFH2_FAIL_BURNISH_RERUN_AFH1:
                     self.dut.BurnishFailedHeads.append(iHead)
                  ScrCmds.raiseException(11186, "Failed for high flying head.")
         objMsg.printMsg("High flying head limit check passed.")

      spc_id = 0
      try:
         prevBurnishTable = self.dut.dblData.Tables('P_AFH_DH_BURNISH_CHECK').tableDataObj()
         spc_id = int(prevBurnishTable[len(prevBurnishTable)-1]['SPC_ID']) + 1
         if testSwitch.AFH2_FAIL_BURNISH_RERUN_AFH1:
            if self.dut.BurnishFailedHeads:
               spc_id += 1000          
      except:
         prevBurnishTable = {}

      curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(35)
      setDBPrecision = self.oUtility.setDBPrecision

      # calculate burnish algorithm
      hdStatus = {}
      deltaBurnishCheck = {}
      deltaBurnish = ''
      heaterElementTableDisplay = {
         "WRITER_HEATER": "W",
         "READER_HEATER": "R",
      }

      for iHead in local_clrDict1.clrDict.keys():

         hdStatus[iHead] = PASS   # head status should default to pass

         AllPossiblePositions = []
         if 'onlyChkZonesList' in burnish_params.keys():
            AllPossiblePositions = burnish_params['onlyChkZonesList']
         else:
            AllPossiblePositions = local_clrDict1.clrDict[iHead].keys() + local_clrDict2.clrDict[iHead].keys()

         listCommonPos = []
         for iPos in AllPossiblePositions:
            if (iPos in local_clrDict1.clrDict[iHead].keys()) and (iPos in local_clrDict2.clrDict[iHead].keys()) and (iPos not in listCommonPos):
               listCommonPos.append(iPos)
         listCommonPos.sort()

         if burnish_params['mode'] == 'burnish':
            listWrtClrFirstState = []
            listWrtClrSecondState = []

            for meas in listCommonPos:
               listWrtClrFirstState.append(local_clrDict1.clrDict[iHead][meas][AFH_WHClr])
               listWrtClrSecondState.append(local_clrDict2.clrDict[iHead][meas][AFH_WHClr])

            if (len(listWrtClrFirstState) < 2 ) or (len(listWrtClrSecondState) < 2):
               objMsg.printMsg("burnishCheck/ local_clrDict1.clrDict: %s" % (local_clrDict1.clrDict))
               objMsg.printMsg("burnishCheck/ local_clrDict2.clrDict: %s" % (local_clrDict2.clrDict))
               objMsg.printMsg("burnishCheck/ listWrtClrFirstState: %s, listWrtClrSecondState: %s" % (listWrtClrFirstState, listWrtClrSecondState))
               ScrCmds.raiseException(42187, "burnishCheck/ failed!  Insufficent Data.")

            lowest_pos = listWrtClrFirstState.index(min(listWrtClrFirstState))

            listWrtClrFirstState.pop(lowest_pos)
            listWrtClrSecondState.pop(lowest_pos)

            adjAvgWrtClrFirstState = MathLib.mean(listWrtClrFirstState)
            adjAvgWrtClrSecondState = MathLib.mean(listWrtClrSecondState)

            deltaBurnishCheck = adjAvgWrtClrSecondState - adjAvgWrtClrFirstState

            if burnish_params['comparison_type'] == 'abs':
               deltaBurnishCheck = abs(deltaBurnishCheck)

            if (deltaBurnishCheck > burnish_params['burnishLimit']):
               hdStatus[iHead] = FAIL   # Fail

            objMsg.printMsg('Head: %s, state: %s, listWrtClrFirstState:%s, adjAvgWrtClrFirstState: %s, state: %s, listWrtClrSecondState: %s, adjAvgWrtClrSecondState: %s, delta (2nd-1st) burnish check  : %s, compare: %s, limit: %s, pass(1)/fail(0): %s' % \
                  (iHead, firstState, listWrtClrFirstState, adjAvgWrtClrFirstState, secondState, \
                  listWrtClrSecondState, adjAvgWrtClrSecondState, deltaBurnishCheck, burnish_params['comparison_type'], burnish_params['burnishLimit'], hdStatus[iHead]) )

            # -------------->  output burnish data to DBLog table  <---------------------------------

            for meas in listCommonPos:
               self.dut.dblData.Tables('P_AFH_DH_BURNISH_CHECK').addRecord(
                  {
                  'SPC_ID'             : spc_id,
                  'OCCURRENCE'         : occurrence,
                  'SEQ'                : curSeq,
                  'TEST_SEQ_EVENT'     : testSeqEvent,
                  'TEST_TYPE'          : burnish_params['mode'],
                  'ACTIVE_HEATER'      : heaterElementTableDisplay["WRITER_HEATER"],
                  'CLR_ACTUATION_MODE' : "Write_Clearance",
                  'HD_PHYS_PSN'        : self.dut.LgcToPhysHdMap[iHead],
                  'TEST_PSN'           : meas,
                  'HD_LGC_PSN'         : iHead,
                  'WRT_HTR_CLR_1': setDBPrecision(local_clrDict1.clrDict[iHead][meas][AFH_WHClr], 0, 4),
                  'WRT_HTR_CLR_2': setDBPrecision(local_clrDict2.clrDict[iHead][meas][AFH_WHClr], 0, 4),
                  'MOD_CALC_AVG_1': setDBPrecision(adjAvgWrtClrFirstState, 0, 4),
                  'MOD_CALC_AVG_2': setDBPrecision(adjAvgWrtClrSecondState, 0, 4),
                  'DELTA_BURNISH_CHECK': setDBPrecision(deltaBurnishCheck, 0, 4),
                  'BURNISH_USL': setDBPrecision(burnish_params['burnishLimit'], 0, 4),
                  'HD_STATUS': str(hdStatus[iHead]),
                  })

               if testSwitch.FE_0133254_357260_CREATE_CLEARANCE_DELTA_TABLE or ( burnish_params.get('comparison_type', '') == 'abs_rddac' ):
                  self.dut.dblData.Tables('P_CLEARANCE_DELTAS').addRecord(
                     {
                     'HD_PHYS_PSN'     : self.dut.LgcToPhysHdMap[iHead],
                     'TEST_PSN'        : meas,
                     'SPC_ID'          : spc_id,
                     'OCCURRENCE'      : occurrence,
                     'SEQ'             : curSeq,
                     'TEST_SEQ_EVENT'  : testSeqEvent,
                     'HD_LGC_PSN'      : iHead,
                     'WH_CLRNC_1'      : setDBPrecision(local_clrDict1.clrDict[iHead][meas][AFH_WHClr], 0, 4),
                     'WH_CLRNC_2'      : setDBPrecision(local_clrDict2.clrDict[iHead][meas][AFH_WHClr], 0, 4),
                     'WH_CLRNC_DELTA'  : setDBPrecision((local_clrDict2.clrDict[iHead][meas][AFH_WHClr]-local_clrDict1.clrDict[iHead][meas][AFH_WHClr]), 0, 4),
                     'HO_CLRNC_1'      : setDBPrecision(local_clrDict1.clrDict[iHead][meas][AFH_RdClr], 0, 4),
                     'HO_CLRNC_2'      : setDBPrecision(local_clrDict2.clrDict[iHead][meas][AFH_RdClr], 0, 4),
                     'HO_CLRNC_DELTA'  : setDBPrecision((local_clrDict2.clrDict[iHead][meas][AFH_RdClr]-local_clrDict1.clrDict[iHead][meas][AFH_RdClr]), 0, 4),
                     'WH_DAC_1'        : setDBPrecision(local_DACDict1.clrDict[iHead][meas][AFH_WHDAC], 0, 4),
                     'WH_DAC_2'        : setDBPrecision(local_DACDict2.clrDict[iHead][meas][AFH_WHDAC], 0, 4),
                     'WH_DAC_DELTA'    : setDBPrecision((local_DACDict2.clrDict[iHead][meas][AFH_WHDAC]-local_DACDict1.clrDict[iHead][meas][AFH_WHDAC]), 0, 4),
                     'HO_DAC_1'        : setDBPrecision(local_DACDict1.clrDict[iHead][meas][AFH_HODAC], 0, 4),
                     'HO_DAC_2'        : setDBPrecision(local_DACDict2.clrDict[iHead][meas][AFH_HODAC], 0, 4),
                     'HO_DAC_DELTA'    : setDBPrecision((local_DACDict2.clrDict[iHead][meas][AFH_HODAC]-local_DACDict1.clrDict[iHead][meas][AFH_HODAC]), 0, 4),
                     })

            if testSwitch.FE_0133254_357260_CREATE_CLEARANCE_DELTA_TABLE or ( burnish_params.get('comparison_type', '') == 'abs_rddac' ):
               objMsg.printDblogBin(self.dut.dblData.Tables('P_CLEARANCE_DELTAS'))


         else:    # delta VBAR clearance check
            objMsg.printMsg('Performing delta VBAR clearance calculation (by position comparison) ... not traditional burnish check calculation')

            for meas in listCommonPos:

               deltaBurnishCheck = local_clrDict2.clrDict[iHead][meas][AFH_WHClr] - local_clrDict1.clrDict[iHead][meas][AFH_WHClr]

               if burnish_params['comparison_type'] == 'abs':
                  deltaBurnishCheck = abs(deltaBurnishCheck)

               if (deltaBurnishCheck > burnish_params['burnishLimit']):
                  hdStatus[iHead] = FAIL   # Fail


               objMsg.printMsg('Head: %s, state: %s, WHClr1:%s, state: %s, WHClr2: %s, delta (2nd-1st) burnish check  : %s, compare: %s, limit: %s, pass(1)/fail(0): %s' % \
                  (iHead, firstState, local_clrDict1.clrDict[iHead][meas][AFH_WHClr], \
                     secondState, local_clrDict2.clrDict[iHead][meas][AFH_WHClr], \
                     deltaBurnishCheck, burnish_params['comparison_type'], burnish_params['burnishLimit'], hdStatus[iHead]) )

               adjAvgWrtClrFirstState = -1
               adjAvgWrtClrSecondState = -1  # these have no meaning in the delta VBAR clearance algorithm where each position is now checked individually

               self.dut.dblData.Tables('P_AFH_DH_BURNISH_CHECK').addRecord(
                  {
                  'SPC_ID'             : spc_id,
                  'OCCURRENCE'         : occurrence,
                  'SEQ'                : curSeq,
                  'TEST_SEQ_EVENT'     : testSeqEvent,
                  'TEST_TYPE'          : burnish_params['mode'],
                  'ACTIVE_HEATER'      : heaterElementTableDisplay["WRITER_HEATER"],
                  'CLR_ACTUATION_MODE' : "Write_Clearance",
                  'HD_PHYS_PSN'        : self.dut.LgcToPhysHdMap[iHead],
                  'TEST_PSN'           : meas,
                  'HD_LGC_PSN'         : iHead,
                  'WRT_HTR_CLR_1'      : setDBPrecision(local_clrDict1.clrDict[iHead][meas][AFH_WHClr], 0, 4),
                  'WRT_HTR_CLR_2'      : setDBPrecision(local_clrDict2.clrDict[iHead][meas][AFH_WHClr], 0, 4),
                  'MOD_CALC_AVG_1'     : setDBPrecision(adjAvgWrtClrFirstState, 0, 4),
                  'MOD_CALC_AVG_2'     : setDBPrecision(adjAvgWrtClrSecondState, 0, 4),
                  'DELTA_BURNISH_CHECK'  : setDBPrecision(deltaBurnishCheck, 0, 4),
                  'BURNISH_USL'          : setDBPrecision(burnish_params['burnishLimit'], 0, 4),
                  'HD_STATUS'          : str(hdStatus[iHead]),
                  })

            # end of else delta VBAR clearance check
         # end of for head loop

         deltaBurnish = deltaBurnish + str(setDBPrecision(deltaBurnishCheck, 0, 4))
         if (iHead < len(local_clrDict1.clrDict.keys())-1):
            deltaBurnish = deltaBurnish + '_'
         # objMsg.printMsg("deltaBurnish = %s" %(deltaBurnish))     # debug

      self.frm.clearFrames()
      self.frm.display_frames()

      # for combo spec screen in WRITE_SCRN
      self.dut.driveattr['DELTA_BURNISH'] = str(deltaBurnish)
      objMsg.printMsg("DELTA_BURNISH = %s" %(str(self.dut.driveattr['DELTA_BURNISH'])))     # debug

      if burnish_params['mode'] == 'burnish':

         # -------------->  fail the drive here for burnishing  <---------------------------------
         if testSwitch.AFH2_FAIL_BURNISH_RERUN_AFH1:
            reAFHburnish_fail_heads = []
         for iHead in local_clrDict1.clrDict.keys():
            if (hdStatus[iHead] == 0):
               objMsg.printMsg('Head: %s failed for burnishing ' % str(iHead), objMsg.CMessLvl.CRITICAL)
               if testSwitch.AFH2_FAIL_BURNISH_RERUN_AFH1:
                  self.dut.BurnishFailedHeads.append(iHead)
               if testSwitch.AFH2_FAIL_BURNISH_RERUN_AFH1:
                  reAFHburnish_fail_heads.append(iHead)
               else:   
                  ScrCmds.raiseException(14559, "Head: %s failed for burnishing " % str(iHead))
         if testSwitch.AFH2_FAIL_BURNISH_RERUN_AFH1:
            if reAFHburnish_fail_heads != []:
               ScrCmds.raiseException(14559, "Head: %s failed for burnishing " % str(reAFHburnish_fail_heads))                  
               
         objMsg.printMsg('*' * 40 + ' End of Checking deltas between 1st and 2nd measurements for burnishing ' + '*' * 40)
         return self.dut.dblData.Tables('P_AFH_DH_BURNISH_CHECK').tableDataObj()

      if burnish_params['mode'] == 'delta_VBAR':
         for iHead in local_clrDict1.clrDict.keys():

            # For VE only, force a failure first time through only to exercise the restartVbar transition
            if testSwitch.virtualRun:
               hdStatus[iHead] = getattr(self.dut, "VE_AFHFailFlag", FAIL)
               self.dut.VE_AFHFailFlag = PASS

            if (self.AFH_State == 2) and (validState == 1) and (hdStatus[iHead] == FAIL):
               stateTableName = self.dut.nextState
               if stateTableName == 'AFH2B':
                  objMsg.printMsg("Head failed 2nd deltaVBAR check after running AFH2 a 2nd time.")
                  ScrCmds.raiseException(14559, "Head: %s failed for burnishing " % str(iHead))
               else:
                  if not testSwitch.virtualRun:
                     objMsg.printMsg('Head: %s failed delta VBAR clr check! re-running VBAR' % str(iHead), objMsg.CMessLvl.CRITICAL)
                     self.dut.stateTransitionEvent = 'reRunVBAR'

         if self.dut.stateTransitionEvent == 'reRunVBAR':
            # Check to make sure we haven't exceeded our VBAR rerun limit
            self.dut.rerunVbar += 1
            self.dut.objData.update({'RERUN_VBAR':self.dut.rerunVbar})
            if self.dut.rerunVbar > 1:
               ScrCmds.raiseException(14799, "Attempting to start restart VBAR more than once. Fail to avoid infinite loop")

         return self.dut.dblData.Tables('P_AFH_DH_BURNISH_CHECK').tableDataObj()


   def crossStrokeClrCheck(self, crossStrokeClrLimit):
      """
      #######################################################################################################################
      #
      #               Function:  crossStrokeClrCheck
      #
      #        Original Author:  Michael T. Brady
      #
      #            Description:  checks for large OD to ID clearance variation
      #
      #          Prerrequisite:  frames data is present for at least 1 state
      #
      #                  Input:  cross strock clr limits
      #
      #           Return  Type:  Integer
      #
      #           Return Value:  the last numFHCallsIndex Index from frames data
      #
      #######################################################################################################################

      """

      local_clrDict1 = CclearanceDictionary()

      # 1. pull information from frames
      self.frm.readFramesFromCM_SIM()

      numHeads = int(len(self.headList))

      if (len(self.frm.dPesSim.DPES_FRAMES) < (numHeads * 4)):
         objMsg.printMsg('Less than 8 Frames data were found to calculate a crossStrokeClrCheck check', objMsg.CMessLvl.VERBOSEDEBUG)
         return -1

      afhMode = AFH_MODE_TEST_135_INTERPOLATED_DATA

      for frame in self.frm.dPesSim.DPES_FRAMES:
         for iHead in self.headList:
            if ( ( frame['mode'] == afhMode ) and ( frame['LGC_HD'] == iHead )):
               local_clrDict1.setClrDict( iHead, frame['Zone'], frame['Read Clearance'], frame['WrtLoss'], frame['Write Clearance'], frame['Zone'] )

      self.frm.clearFrames()
      self.frm.display_frames()

      if (local_clrDict1.clrDict == {}):
         objMsg.printMsg('FRAMES data not found for cross Stroke Clr Check... exiting early return -1', objMsg.CMessLvl.CRITICAL)
         return -1

      # 2. Calculate the OD - ID cross stroke delta on a per head basis

      objMsg.printMsg('*' * 40 + ' Summary of cross stroke Clr check ' + '*' * 40, objMsg.CMessLvl.VERBOSEDEBUG)

      deltaCrossStrokeWHClr = {}
      deltaCrossStrokeHOClr = {}

      for curHead in self.headList:
         max_pos = max(local_clrDict1.clrDict[curHead].keys())
         min_pos = min(local_clrDict1.clrDict[curHead].keys())

         deltaCrossStrokeWHClr[curHead] = local_clrDict1.clrDict[curHead][min_pos][AFH_WHClr] - local_clrDict1.clrDict[curHead][max_pos][AFH_WHClr]
         deltaCrossStrokeHOClr[curHead] = local_clrDict1.clrDict[curHead][min_pos][AFH_RdClr] - local_clrDict1.clrDict[curHead][max_pos][AFH_RdClr]

         objMsg.printMsg('crossStrokeClrCheck/ Hd: %s, WH Clr at OD: %s, WH Clr at ID: %s, delta: %s, limit: %s' % \
            (curHead, local_clrDict1.clrDict[curHead][min_pos][AFH_WHClr], local_clrDict1.clrDict[curHead][max_pos][AFH_WHClr], \
            deltaCrossStrokeWHClr[curHead], crossStrokeClrLimit[AFH_WHMODE]))
         objMsg.printMsg('crossStrokeClrCheck/ Hd: %s, HO Clr at OD: %s, HO Clr at ID: %s, delta: %s, limit: %s' % \
            (curHead, local_clrDict1.clrDict[curHead][min_pos][AFH_RdClr], local_clrDict1.clrDict[curHead][max_pos][AFH_RdClr], \
            deltaCrossStrokeHOClr[curHead], crossStrokeClrLimit[AFH_HOMODE]))


      for curHead in self.headList:
         if (abs(deltaCrossStrokeWHClr[curHead]) > crossStrokeClrLimit[AFH_WHMODE]):
            objMsg.printMsg('crossStrokeClrCheck/ Head: %s, abs(delta W+H Clr: %s) greater than (Cross Stroke Limit: %s)' % \
               (str(curHead), str(abs(deltaCrossStrokeWHClr[curHead])), str(crossStrokeClrLimit[AFH_WHMODE])), objMsg.CMessLvl.CRITICAL )
            ScrCmds.raiseException(11257, "Drive failed for W+H Clr values Cross Stroke OD-ID limit exceeded.")

         if (abs(deltaCrossStrokeHOClr[curHead]) > crossStrokeClrLimit[AFH_HOMODE]):
            objMsg.printMsg('crossStrokeClrCheck/ Head: %s, abs(delta Heater-Only Clr: %s) greater than (Cross Stroke Limit: %s)' % \
               (str(curHead), str(abs(deltaCrossStrokeHOClr[curHead])), str(crossStrokeClrLimit[AFH_HOMODE])), objMsg.CMessLvl.CRITICAL )
            ScrCmds.raiseException(11257, "Drive failed for Heater-Only values Cross Stroke OD-ID limit exceeded.")

      objMsg.printMsg('Drive passed cross stroke OD-ID check. ', objMsg.CMessLvl.IMPORTANT)

      return (deltaCrossStrokeWHClr, deltaCrossStrokeHOClr)     # let the drive move on


   def clearanceRangeCheck(self, clrRangeChkLimit):
      """
      #########################################################################################
      #
      #               Function:  clearanceRangeCheck
      #
      #        Original Author:  Michael T. Brady
      #
      #            Description:  screen to check the max Clr - min Clr by actuation mode (WH or HO)
      #
      #                  Input:  clrRangeChkLimit
      #
      #           Return Value:
      #
      #########################################################################################
      """

      # 1. pull information from frames
      self.frm.readFramesFromCM_SIM()

      MAX_CLR = 10000.0      # in micro-inches
      MIN_CLR = -10000.0     # in micro-inches
      objMsg.printMsg('*' * 40 + ' Summary of clearance range check ' + '*' * 40, objMsg.CMessLvl.VERBOSEDEBUG)

      rangeWrtClr = {}
      rangeRdClr = {}

      afhMode = AFH_MODE_TEST_135_INTERPOLATED_DATA

      for iHead in self.headList:
         maxWrtClr = MIN_CLR
         maxRdClr = MIN_CLR
         minWrtClr = MAX_CLR
         minRdClr = MAX_CLR
         posList = []
         for frame in self.frm.dPesSim.DPES_FRAMES:
            local_iPos = int( frame['Zone'] )
            if ( (frame['mode'] == afhMode) and (frame['LGC_HD'] == iHead) and ( local_iPos not in posList )):
               posList.append( local_iPos )

         self.numMeasPos = len(posList)

         for iPos in posList:
            for frame in self.frm.dPesSim.DPES_FRAMES:
               if ( (frame['mode'] == afhMode) and (frame['LGC_HD'] == iHead) and frame['Zone'] == iPos):
                  wrtClr = frame['Write Clearance']
                  rdClr = frame['Read Clearance']

            if wrtClr > maxWrtClr:
               maxWrtClr = wrtClr

            if rdClr > maxRdClr:
               maxRdClr = rdClr

            if wrtClr < minWrtClr:
               minWrtClr = wrtClr

            if rdClr < minRdClr:
               minRdClr = rdClr

            if (maxWrtClr == MIN_CLR) or (maxRdClr == MIN_CLR) or (minWrtClr == MAX_CLR) or (minRdClr == MAX_CLR):
               objMsg.printMsg("crossStrokeClrCheck/ One or more data structs not updated!")
               objMsg.printMsg("crossStrokeClrCheck/ local_clrDict1.clrDict: %s" % str(local_clrDict1.clrDict))
               self.frm.readFramesFromCM_SIM()
               self.frm.display_frames()
               ScrCmds.raiseException(11044, "crossStrokeClrCheck failed!  One or more data structs not updated!")

            rangeWrtClr[iHead] = abs(maxWrtClr - minWrtClr)
            rangeRdClr[iHead] = abs(maxRdClr - minRdClr)
            # end of iPos loop
         objMsg.printMsg("crossStrokeClrCheck/ Hd: %s, rangeWrtClr: %0.6f, limit: %0.6f, rangeRdClr: %0.6f, limit: %0.6f" %
            (iHead, rangeWrtClr[iHead], clrRangeChkLimit['rangeLimit_wrtClr'], rangeRdClr[iHead], clrRangeChkLimit['rangeLimit_rdClr']))

      for iHead in self.headList:
         if rangeWrtClr[iHead] > clrRangeChkLimit['rangeLimit_wrtClr']:
            objMsg.printMsg("crossStrokeClrCheck/ write Clr range : %s execeeded limit %s " %
               (rangeWrtClr[iHead], clrRangeChkLimit['rangeLimit_wrtClr']))
            ScrCmds.raiseException(11257, "Range of write Clr values exceeded limit.")

         if rangeRdClr[iHead] > clrRangeChkLimit['rangeLimit_rdClr']:
            objMsg.printMsg("crossStrokeClrCheck/ read Clr range : %s execeeded limit %s " %
               (rangeRdClr[iHead], clrRangeChkLimit['rangeLimit_rdClr']))
            ScrCmds.raiseException(11257, "Range of read Clr values exceeded limit.")

      objMsg.printMsg("crossStrokeClrCheck/ Head: %s passed range check of wrtClr limit %s and rdClr limit %s" %
         (iHead, clrRangeChkLimit['rangeLimit_wrtClr'], clrRangeChkLimit['rangeLimit_rdClr']))


   def extreme_OD_ID_clearanceRangeCheck(self, extreme_OD_ID_clearanceRangeCheck):
      """
      #########################################################################################
      #
      #               Function:  extreme_OD_ID_clearanceRangeCheck
      #
      #        Original Author:  Michael T. Brady
      #
      #            Description:  screen to check the max - minimum clearance using test 135 and interpolated data.
      #
      #                  Input:  extreme_OD_ID_clearanceRangeCheck
      #
      #           Return Value:
      #
      #########################################################################################
      """

      # 1. pull information from frames
      self.frm.readFramesFromCM_SIM()

      MAX_CLR = 10000.0      # in micro-inches
      MIN_CLR = -10000.0     # in micro-inches
      objMsg.printMsg('*' * 40 + ' Summary of clearance range check ' + '*' * 40, objMsg.CMessLvl.VERBOSEDEBUG)

      rangeWrtClr = {}
      rangeRdClr = {}

      for iHead in self.headList:
         maxWrtClr = MIN_CLR
         maxRdClr = MIN_CLR
         minWrtClr = MAX_CLR
         minRdClr = MAX_CLR

         for frame in self.frm.dPesSim.DPES_FRAMES:
            if ( (frame['mode'] in [AFH_MODE_TEST_135_INTERPOLATED_DATA, AFH_MODE_TEST_135_EXTREME_ID_OD_DATA]) and (frame['LGC_HD'] == iHead)):
               wrtClr = frame['Write Clearance']
               rdClr = frame['Read Clearance']

               if wrtClr > maxWrtClr:
                  maxWrtClr = wrtClr

               if rdClr > maxRdClr:
                  maxRdClr = rdClr

               if wrtClr < minWrtClr:
                  minWrtClr = wrtClr

               if rdClr < minRdClr:
                  minRdClr = rdClr
               # end of if
            # end of for frame

         if (maxWrtClr == MIN_CLR) or (maxRdClr == MIN_CLR) or (minWrtClr == MAX_CLR) or (minRdClr == MAX_CLR):
            objMsg.printMsg("extreme_OD_ID_clearanceRangeCheck/ One or more data structs not updated!")
            self.frm.readFramesFromCM_SIM()
            self.frm.display_frames(2)
            ScrCmds.raiseException(11044, "crossStrokeClrCheck failed!  One or more data structs not updated!")

         rangeWrtClr[iHead] = abs(maxWrtClr - minWrtClr)
         rangeRdClr[iHead] = abs(maxRdClr - minRdClr)
         if testSwitch.virtualRun == 1:
            extreme_OD_ID_clearanceRangeCheck['rangeLimit_wrtClr'] = 0.3 # in micro-inches
            extreme_OD_ID_clearanceRangeCheck['rangeLimit_rdClr']  = 0.3 # in micro-inches

         # end of iPos loop
         objMsg.printMsg("extreme_OD_ID_clearanceRangeCheck/ Hd: %s, rangeWrtClr: %0.6f, limit: %0.6f, rangeRdClr: %0.6f, limit: %0.6f" %
            (iHead, rangeWrtClr[iHead], extreme_OD_ID_clearanceRangeCheck['rangeLimit_wrtClr'], rangeRdClr[iHead], extreme_OD_ID_clearanceRangeCheck['rangeLimit_rdClr']))


      for iHead in self.headList:
         if rangeWrtClr[iHead] > extreme_OD_ID_clearanceRangeCheck['rangeLimit_wrtClr']:
            objMsg.printMsg("extreme_OD_ID_clearanceRangeCheck/ write Clr range : %s execeeded limit %s " %
               (rangeWrtClr[iHead], extreme_OD_ID_clearanceRangeCheck['rangeLimit_wrtClr']))
            ScrCmds.raiseException(11257, "Range of write Clr values exceeded limit.")

         if rangeRdClr[iHead] > extreme_OD_ID_clearanceRangeCheck['rangeLimit_rdClr']:
            objMsg.printMsg("extreme_OD_ID_clearanceRangeCheck/ read Clr range : %s execeeded limit %s " %
               (rangeRdClr[iHead], extreme_OD_ID_clearanceRangeCheck['rangeLimit_rdClr']))
            ScrCmds.raiseException(11257, "Range of read Clr values exceeded limit.")

         objMsg.printMsg("extreme_OD_ID_clearanceRangeCheck/ Head: %s passed range check of wrtClr limit %s and rdClr limit %s" %
            (iHead, extreme_OD_ID_clearanceRangeCheck['rangeLimit_wrtClr'], extreme_OD_ID_clearanceRangeCheck['rangeLimit_rdClr']))

      if testSwitch.virtualRun == 1:
         return rangeWrtClr, rangeRdClr
