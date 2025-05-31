#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2009, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: AFH Screens Module
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/09/07 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/AFH_Screens_DH.py $
# $Revision: #3 $
# $DateTime: 2016/09/07 20:40:46 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/AFH_Screens_DH.py#3 $
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
from AFH import CclearanceDictionary,CdPES
from RAP import ClassRAP

DEBUG = 0


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


   def evalTempCapAllHeads(self, tcc1_modifiedDict, tcc2_dict, tccStructDict, tempSpecDict, heaterElement ):
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
      if not testSwitch.extern.FE_0157745_387179_AFH_TCS_WARP:
         tblCap = 'P035_TEMP_CAP'
      else:
         tblCap = 'P035_TEMP_CAP2'
      try:     self.dut.dblData.delTable(tblCap)
      except:  pass

      for iHead in self.headList:
         if testSwitch.ENABLE_TCC_RESET_BY_HEAD_BEFORE_AFH4 == 1 and iHead in self.dut.TccResetHeadList:
            continue
         if not testSwitch.extern.FE_0157745_387179_AFH_TCS_WARP:

            self.evalTempCap(iHead, tcc1_modifiedDict[iHead], tcc2_dict[iHead], tccStructDict['dWrtClr1_dict'][iHead].values(),
                          tempSpecDict, self.temp.retHDATemp(certTemp = 1))
         else:
            for iZoneIndex in TP.TCS_WARP_ZONES.keys():
               self.evalTempCap(iHead, tcc1_modifiedDict[iHead][iZoneIndex], tcc2_dict[iHead], tccStructDict['dWrtClr1_dict'][iHead].values(),
                          tempSpecDict, self.temp.retHDATemp(certTemp = 1), iZoneIndex)
         # end of for iHead in self.headList


      # -------------------> display temperature capability <-------------------

      objMsg.printDblogBin(self.dut.dblData.Tables(tblCap))


   def evalTempCap(self, iHead, tcc1, tcc2, whClr1, tempSpecDict, certTemp, iZoneIndex = 0):
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
      if not testSwitch.extern.FE_0157745_387179_AFH_TCS_WARP:
         tblCap = 'P035_TEMP_CAP'
      else:
         tblCap = 'P035_TEMP_CAP2'
      minClr = min(whClr1)    # these should be the CERT temp WH clr values
      maxClr = max(whClr1)

      # --------------> Section 4 - calculate temperature capability for this head <------------------
      high_clr_limit = tempSpecDict['loTemp'][1]
      low_clr_limit = tempSpecDict['hiTemp'][1]

      if tcc1 > 0:
         hotTempCap = ((high_clr_limit - maxClr) / tcc1 ) + certTemp
         coldTempCap = (( low_clr_limit - minClr ) / tcc1 ) + certTemp

      elif tcc1 < 0:
         hotTempCap = ((high_clr_limit - minClr) / tcc1 ) + certTemp
         coldTempCap = (( low_clr_limit - maxClr ) / tcc1 ) + certTemp
      else: # if tcc1 == 0
         coldTempCap = -999
         hotTempCap = 999

      MINIMUM_TEMP_LIMIT = -40   # Celsius
      MAXIMUM_TEMP_LIMIT = 120   # Celsius

      if (coldTempCap > MAXIMUM_TEMP_LIMIT):
         coldTempCap = MAXIMUM_TEMP_LIMIT
         objMsg.printMsg('Calc Cold Temp Cap greater than %s C, set Cold Temp Cap = %s C' % (MAXIMUM_TEMP_LIMIT, MAXIMUM_TEMP_LIMIT), objMsg.CMessLvl.IMPORTANT)

      if (coldTempCap < MINIMUM_TEMP_LIMIT):
         coldTempCap = MINIMUM_TEMP_LIMIT
         objMsg.printMsg('Calc Cold Temp Cap less than %s C, set Cold Temp Cap = %s C'  % ( MINIMUM_TEMP_LIMIT, MINIMUM_TEMP_LIMIT ), objMsg.CMessLvl.IMPORTANT)

      if (hotTempCap > MAXIMUM_TEMP_LIMIT):
         hotTempCap = MAXIMUM_TEMP_LIMIT
         objMsg.printMsg('Calc Hot Temp Cap greater than %s C, set Hot Temp Cap = %s C' % (MAXIMUM_TEMP_LIMIT, MAXIMUM_TEMP_LIMIT), objMsg.CMessLvl.IMPORTANT)

      if (hotTempCap < MINIMUM_TEMP_LIMIT):
         hotTempCap = MINIMUM_TEMP_LIMIT
         objMsg.printMsg('Calc Hot Temp Cap less than %s C, set Hot Temp Cap = %s C' % ( MINIMUM_TEMP_LIMIT , MINIMUM_TEMP_LIMIT), objMsg.CMessLvl.IMPORTANT)

      if tcc2 != 0.0:
         ScrCmds.raiseException(11044, 'evalTempCap/No support for tcc2 != 0.0 ')


      # --------------> Section 5 - add temperature capability info to DBLOG <------------------
      if not testSwitch.extern.FE_0157745_387179_AFH_TCS_WARP:
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
         })
         objMsg.printMsg('evalTempCap/ Hd: %2s, tcc1: %12.9f, tcc2: %12.9f, cold Temp Cap: %6.1f, hot Temp Cap: %6.1f' % \
         (iHead, tcc1, tcc2, coldTempCap, hotTempCap))
      else:
         self.dut.dblData.Tables('P035_TEMP_CAP2').addRecord(
                     {
                        'SPC_ID': self.spcID,
                        'OCCURRENCE': self.dut.objSeq.getOccurrence(),
                        'SEQ': self.dut.objSeq.getSeq(),
                        'TEST_SEQ_EVENT': self.dut.objSeq.getTestSeqEvent(35),

                        'HD_PHYS_PSN':self.dut.LgcToPhysHdMap[iHead],
                        'HD_LGC_PSN':iHead,
                        'COLD_CAP':self.oUtility.setDBPrecision(coldTempCap, 8, 0),
                        'HOT_CAP':self.oUtility.setDBPrecision(hotTempCap, 8, 0),
                        'REGION': TP.TCS_WARP_ZONES.keys().index(iZoneIndex),
                     } )
         objMsg.printMsg('evalTempCap/ Hd: %2s, Zone: %d tcc1: %12.9f, tcc2: %12.9f, cold Temp Cap: %6.1f, hot Temp Cap: %6.1f' % \
         (iHead, iZoneIndex, tcc1, tcc2, coldTempCap, hotTempCap))
      return coldTempCap, hotTempCap
   #-------------------------------------------------------------------------------------------------------
   def calTempLimitAllHeads(self, tcc1Dict, heaterElement, tccDict ):
      #step1: read back write clr and wrt loss of AHF2
      self.frm.readFramesFromCM_SIM()
      dWrtClr1_dict = {}
      dWrtLoss_dict = {}
      dTestTrk_dict = {}
      clearanceDataType = tccDict[heaterElement]['clearanceDataType']
      for iHead in self.headList:
         dWrtClr1_dict[iHead] = {}
         dWrtLoss_dict[iHead] = {}
         dTestTrk_dict[iHead] = {}
         for frame in self.frm.dPesSim.DPES_FRAMES:
            iZone = int(frame['Zone'])
            if ( (frame['mode'] == AFH_MODE_TEST_135_INTERPOLATED_DATA) and (frame['stateIndex'] == 2) and \
                 (frame['PHYS_HD'] == self.dut.LgcToPhysHdMap[iHead]) and ( frame['Heater Element'] == heaterElementNameToFramesDict[heaterElement] ) ):
               dWrtClr1_dict[iHead][iZone] = float(frame[clearanceDataType]) * angstromsScaler
               dWrtLoss_dict[iHead][iZone] = float(frame['WrtLoss']) * angstromsScaler
               dTestTrk_dict[iHead][iZone] = float(frame['Cylinder'])/1000.0

      #try:     self.dut.dblData.delTable('P_TEMP_LIMIT_WITH_0_WRT_HTR_DAC')
      #except:  pass
      #step2: read back target wrt clr
      TargetWrtClr1_dict = [[15]*(self.dut.numZones+1) for i in range(self.dut.imaxHead)]
      CProcess().St({'test_num':172, 'spc_id': 1234, 'prm_name':[], 'CWORD1': 5,'timeout': 600.0})
      table_afh_target_clr = self.dut.dblData.Tables('P172_AFH_DH_CLEARANCE').chopDbLog('SPC_ID', 'match',str(1234))
      for row in table_afh_target_clr:
         hd = int(row['HD_LGC_PSN'])
         zn = int(row['DATA_ZONE'])
         TargetWrtClr1_dict[hd][zn] = int(row['WRT_HEAT_TRGT_CLRNC'])
      objMsg.printMsg("TargetWrtClr1_dict %s." % TargetWrtClr1_dict)

      #step3: calculate WrtLoss introduced WrtClr loss at 0 heater DAC. (not equal?)
      #CProcess().St({'test_num':172, 'prm_name':'AFH PTP Coef Dump', 'timeout': 1800, 'CWORD1': (15,), 'spc_id':12345})
      #coefTable = self.dut.dblData.Tables('P172_AFH_PTP_COEF').chopDbLog('SPC_ID', 'match',str(12345))
      #eqnTypes = ['WRT_HTR_PTP_COEF']
      #for coefNum in range(AFH_MAX_NUM_COEFS_IN_RAP_PER_EQN_TYPE):
      #   for coefType in eqnTypes:
      #      need to complete here if in-drv afh coeffs enabled
      from PreAmp import CPreAmp
      oPreamp = CPreAmp()

      activeCoeffs = {}
      odPES  = CdPES(TP.masterHeatPrm_11, TP.defaultOCLIM)
      coefs = odPES.getClrCoeff(TP.clearance_Coefficients, self.dut.PREAMP_TYPE, self.dut.AABType)
      activeCoeffs.update(coefs)
      WC = activeCoeffs['WRT_HTR_PTP_COEF']['LO_POWER']
      for hd in range(self.dut.imaxHead):
         for zn in range(self.dut.numZones):
            dWrtLoss_dict[hd][zn] = WC[0]+WC[1]*(dTestTrk_dict[hd][zn]/1000.0) + WC[2]*(dTestTrk_dict[hd][zn]/1000.0)**2 + 0 + 0 + 0 +\
                                    WC[6]*(dWrtLoss_dict[hd][zn]/254.0) + WC[7]*(dWrtLoss_dict[hd][zn]/254.0)*(dTestTrk_dict[hd][zn]/1000.0) +\
                                    0 + WC[9]*((dWrtLoss_dict[hd][zn]/254.0)**2)
      objMsg.printMsg("dWrtLoss_dict= %s." % (dWrtLoss_dict))
      for hd in self.headList:
         minWHClrM = 1000
         for zn in range(self.dut.numZones):
            if minWHClrM > (dWrtClr1_dict[hd][zn] - TargetWrtClr1_dict[hd][zn] - dWrtLoss_dict[hd][zn]*254):
               minWHClrM = dWrtClr1_dict[hd][zn] - TargetWrtClr1_dict[hd][zn] - dWrtLoss_dict[hd][zn]*254
         objMsg.printMsg("minWHClrM= %s." % (minWHClrM))
         self.calTemplimit(hd,heaterElement,tcc1Dict[hd], minWHClrM, tccDict, self.temp.retHDATemp(certTemp = 1))

      # -------------------> display temperature limit <-------------------
      objMsg.printDblogBin(self.dut.dblData.Tables('P_TEMP_LIMIT_WITH_0_WRT_HTR_DAC'))


   def calTemplimit(self, iHead,heaterElement,tcc1, minWHClrM, tccDict, certTemp):
      coldTemp_dTc = tccDict[heaterElement]['COLD_TEMP_DTC']
      dTc = tccDict[heaterElement]['dTc']

      hotTemp_dTh = tccDict[heaterElement]['HOT_TEMP_DTH']
      dTh = tccDict[heaterElement]['dTh']

      tempLimit1 = -1000.0
      tempLimit2 = 1000.0
      if tcc1 == 0:
         if dTh < 0:
            tempLimit2 = hotTemp_dTh - minWHClrM/dTh
         if dTc > 0:
            tempLimit1 = coldTemp_dTc - minWHClrM/dTc
      elif tcc1 < 0:  #negtive tcc1
         #check hotTemp_dTh
         if (certTemp - hotTemp_dTh)* tcc1 >= minWHClrM:
            tempLimit2 = certTemp - minWHClrM/tcc1
         elif dTh + tcc1 < 0:
               tempLimit2 = hotTemp_dTh - (minWHClrM - (certTemp - hotTemp_dTh)*tcc1)/(dTh + tcc1)
         if dTc + tcc1> 0: 
           tempLimit1 = coldTemp_dTc - (minWHClrM - (certTemp - coldTemp_dTc)*tcc1)/(dTc + tcc1)
      else:        #positive tcc1
         #check coldTemp_dTc
         if (certTemp - coldTemp_dTc)*tcc1 >= minWHClrM:
            tempLimit1 = certTemp - minWHClrM/tcc1
         elif dTc + tcc1 > 0:
            tempLimit1 = coldTemp_dTc - (minWHClrM - (certTemp - coldTemp_dTc)*tcc1)/(dTc + tcc1)
         if dTh + tcc1 < 0:
            tempLimit2 = hotTemp_dTh - (minWHClrM - (certTemp - hotTemp_dTh)*tcc1)/(dTh + tcc1)

      self.dut.dblData.Tables('P_TEMP_LIMIT_WITH_0_WRT_HTR_DAC').addRecord(
         {
         'SPC_ID': self.spcID,
         'OCCURRENCE': self.dut.objSeq.getOccurrence(),
         'SEQ': self.dut.objSeq.getSeq(),
         'HD_PHYS_PSN':self.dut.LgcToPhysHdMap[iHead],
         'HD_LGC_PSN':iHead,
         'TCC1':self.oUtility.setDBPrecision(tcc1, 8, 8),
         'TEMP_LIMIT1':self.oUtility.setDBPrecision(tempLimit1, 8, 1),
         'TEMP_LIMIT2':self.oUtility.setDBPrecision(tempLimit2, 8, 1),
         })
      #objMsg.printMsg('calTempLimit/ Hd: %2s, tcc1: %12.9f, LowLimitTemp: %6.1f, HighLimitTemp: %6.1f' % (iHead, tcc1, tempLimit1, tempLimit2))
      return tempLimit1, tempLimit2

   def calTempLimitBaseOnTCC(self, spc_id ):
      if testSwitch.virtualRun:
         return
      #step1: read back TCC1 from drive
      tcc1_List_R = [0,]*self.dut.imaxHead
      tcc1_List_W = [0,]*self.dut.imaxHead
      RetrieveTcCoeff_prm = TP.Retrieve_TC_Coeff_Prm_172.copy()
      RetrieveTcCoeff_prm['spc_id'] = spc_id
      CProcess().St(RetrieveTcCoeff_prm)
      if not testSwitch.extern.FE_0157745_387179_AFH_TCS_WARP:
         P172_AFH_DH_TC_COEF_Tbl = self.dut.dblData.Tables('P172_AFH_DH_TC_COEF').chopDbLog('SPC_ID', 'match',str(RetrieveTcCoeff_prm['spc_id']))
      else:
         P172_AFH_DH_TC_COEF_Tbl = self.dut.dblData.Tables('P172_AFH_DH_TC_COEF_2').chopDbLog('SPC_ID', 'match',str(RetrieveTcCoeff_prm['spc_id']))
      for entry in P172_AFH_DH_TC_COEF_Tbl:
         if entry.get('ACTIVE_HEATER') == 'R':
            tcc1_List_R[int(entry.get('HD_LGC_PSN'))] = float(entry.get('THERMAL_CLR_COEF1'))
         else:
            tcc1_List_W[int(entry.get('HD_LGC_PSN'))] = float(entry.get('THERMAL_CLR_COEF1'))
      #step2: calculate the temp limit
      heaterElement = "WRITER_HEATER"   # do W+H only mode.
      self.spcID = RetrieveTcCoeff_prm['spc_id']
      self.calTempLimitAllHeads( tcc1_List_W, heaterElement, TP.tcc_DH_values)
   #-------------------------------------------------------------------------------------------------------
   def SmartTccLimits(self):
      if testSwitch.virtualRun:
         return 0,0
      #step1: read back write clr and wrt loss of AHF2
      from AFH_SIM import CAFH_Frames
      OAFH_Frames= CAFH_Frames()
      OAFH_Frames.readFramesFromCM_SIM()
      dWrtClr1_dict = {}
      dWrtLoss_dict = {}
      dTestTrk_dict = {}
      heaterElement = "WRITER_HEATER"   # do W+H only mode.
      clearanceDataType = TP.tcc_DH_values[heaterElement]['clearanceDataType']
      for iHead in range(self.dut.imaxHead):
         dWrtClr1_dict[iHead] = {}
         dWrtLoss_dict[iHead] = {}
         dTestTrk_dict[iHead] = {}
         for frame in OAFH_Frames.dPesSim.DPES_FRAMES:
            iZone = int(frame['Zone'])
            if ( (frame['mode'] == AFH_MODE_TEST_135_INTERPOLATED_DATA) and (frame['stateIndex'] == 2) and \
                 (frame['PHYS_HD'] == self.dut.LgcToPhysHdMap[iHead]) and ( frame['Heater Element'] == heaterElementNameToFramesDict[heaterElement] ) ):
               dWrtClr1_dict[iHead][iZone] = float(frame[clearanceDataType]) * angstromsScaler
               dWrtLoss_dict[iHead][iZone] = float(frame['WrtLoss']) * angstromsScaler
               dTestTrk_dict[iHead][iZone] = float(frame['Cylinder'])
         objMsg.printMsg("Hd:%s, dWrtClr1_dict %s." % (iHead, dWrtClr1_dict[iHead]))
         objMsg.printMsg("Hd:%s, dWrtLoss_dict %s." % (iHead, dWrtLoss_dict[iHead]))
         objMsg.printMsg("Hd:%s, dTestTrk_dict %s." % (iHead, dTestTrk_dict[iHead]))
      
      #step2: read back target wrt clr
      TargetWrtClr1_dict = [[15]*(self.dut.numZones+1) for i in range(self.dut.imaxHead)]
      CProcess().St({'test_num':172, 'spc_id': 12345, 'prm_name':[], 'CWORD1': 5,'timeout': 600.0})
      table_afh_target_clr = self.dut.dblData.Tables('P172_AFH_DH_CLEARANCE').chopDbLog('SPC_ID', 'match',str(12345))
      for row in table_afh_target_clr:
         hd = int(row['HD_LGC_PSN'])
         zn = int(row['DATA_ZONE'])
         TargetWrtClr1_dict[hd][zn] = int(row['WRT_HEAT_TRGT_CLRNC'])
      objMsg.printMsg("TargetWrtClr1_dict %s." % TargetWrtClr1_dict)

      #step3: calculate WrtLoss introduced WrtClr loss at 0 heater DAC. (not equal?)
      #CProcess().St({'test_num':172, 'prm_name':'AFH PTP Coef Dump', 'timeout': 1800, 'CWORD1': (15,), 'spc_id':12345})
      #coefTable = self.dut.dblData.Tables('P172_AFH_PTP_COEF').chopDbLog('SPC_ID', 'match',str(12345))
      #eqnTypes = ['WRT_HTR_PTP_COEF']
      #for coefNum in range(AFH_MAX_NUM_COEFS_IN_RAP_PER_EQN_TYPE):
      #   for coefType in eqnTypes:
      #      need to complete here if in-drv afh coeffs enabled
      from PreAmp import CPreAmp
      oPreamp = CPreAmp()

      activeCoeffs = {}
      odPES  = CdPES(TP.masterHeatPrm_11, TP.defaultOCLIM)
      coefs = odPES.getClrCoeff(TP.clearance_Coefficients, self.dut.PREAMP_TYPE, self.dut.AABType)
      activeCoeffs.update(coefs)
      WC = activeCoeffs['WRT_HTR_PTP_COEF']['LO_POWER']
      for hd in range(self.dut.imaxHead):
         for zn in range(self.dut.numZones):
            dWrtLoss_dict[hd][zn] = WC[0]+WC[1]*(dTestTrk_dict[hd][zn]/1000.0) + WC[2]*(dTestTrk_dict[hd][zn]/1000.0)**2 + 0 + 0 + 0 +\
                                    WC[6]*(dWrtLoss_dict[hd][zn]/254.0) + WC[7]*(dWrtLoss_dict[hd][zn]/254.0)*(dTestTrk_dict[hd][zn]/1000.0) +\
                                    0 + WC[9]*((dWrtLoss_dict[hd][zn]/254.0)**2)
      objMsg.printMsg("dWrtLoss_dict= %s." % (dWrtLoss_dict))
      #step4: calculate minimum wrt clr margin
      minWHClrM = [1000,]*self.dut.imaxHead
      for hd in range(self.dut.imaxHead):
         for zn in range(self.dut.numZones):
            #if minWHClrM[hd] > (dWrtClr1_dict[hd][zn] - TP.afhZoneTargets['TGT_WRT_CLR'][zn] - dWrtLoss_dict[hd][zn]):
            #   minWHClrM[hd] = dWrtClr1_dict[hd][zn] - TP.afhZoneTargets['TGT_WRT_CLR'][zn] - dWrtLoss_dict[hd][zn]
            if minWHClrM[hd] > (dWrtClr1_dict[hd][zn] - TargetWrtClr1_dict[hd][zn] - dWrtLoss_dict[hd][zn]*254):
               minWHClrM[hd] = dWrtClr1_dict[hd][zn] - TargetWrtClr1_dict[hd][zn] - dWrtLoss_dict[hd][zn]*254
      objMsg.printMsg("minWHClrM= %s." % (minWHClrM))
      #step5: calcaulte tcc1 limitLo and limitHi
      certTemp = CTemperature().retHDATemp(certTemp = 1)
      dTc = TP.tcc_DH_values[heaterElement]['dTc']
      dTcTemp = TP.tcc_DH_values[heaterElement]['COLD_TEMP_DTC']
      dTh = TP.tcc_DH_values[heaterElement]['dTh']
      dThTemp = TP.tcc_DH_values[heaterElement]['HOT_TEMP_DTH']
      tccLimitLo = [0.0,]*self.dut.imaxHead
      tccLimitHi = [0.0,]*self.dut.imaxHead
      for hd in range(self.dut.imaxHead):
         tccLimitHi[hd] = (minWHClrM[hd] + dTc*(TP.GuaranteedOperTempSpec['OPER_TEMP_SPEC_LO'] - dTcTemp))/(certTemp - TP.GuaranteedOperTempSpec['OPER_TEMP_SPEC_LO'])
         tccLimitLo[hd] = (minWHClrM[hd] + dTh*(TP.GuaranteedOperTempSpec['OPER_TEMP_SPEC_HI'] - dThTemp))/(certTemp - TP.GuaranteedOperTempSpec['OPER_TEMP_SPEC_HI'])
      objMsg.printMsg("tccLimitLo= %s. tccLimitHi= %s." % (tccLimitLo,tccLimitHi))
      return tccLimitLo, tccLimitHi

   #-------------------------------------------------------------------------------------------------------

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
      #                 Return:  tccDict(dict)      - main TCC related input dictionary
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

      if testSwitch.FE_0165920_341036_DISABLE_READER_HEATER_CONTACT_DETECT_AFH2:
         heaterElementList = self.dut.heaterElementList
      else:
         heaterElementList = [ "WRITER_HEATER" ]
         if self.dut.isDriveDualHeater == 1:
            heaterElementList.append( "READER_HEATER" )

      tccStructDict = {}
      tcc1_unModifiedDict = {}
      tcc1_modifiedDict = {}
      tcc2_dict = {}
      objRAP = ClassRAP()

      # 1st create the data
      for heaterElement in heaterElementList:

         # The new TCS function
         # --------------------
         #
         # 1.  get the dcdt data
         tccStructDict[heaterElement] = self.getTCCDataFromAFHFrames( tccDict, heaterElement )

         # 2.  compute the olympic scored TCC1
         tcc1_unModifiedDict[heaterElement], tcc1_modifiedDict[heaterElement], tcc2_dict[heaterElement] = self.computeOlympicScoredTCC( tccStructDict[heaterElement], tccDict, nTempCERT, heaterElement )

         # 3.  save TCC1 data by head to FLASH
         for iHead in self.headList:
            if testSwitch.ENABLE_TCC_RESET_BY_HEAD_BEFORE_AFH4 == 1 and iHead in self.dut.TccResetHeadList:
               continue
            if testSwitch.FE_0169232_341036_ENABLE_AFH_TGT_CLR_CANON_PARAMS == 1:
               from AFH_canonParams import *
               tcc_DH_values = getTCS_values()
            else:
               tcc_DH_values = TP.tcc_DH_values
            if not testSwitch.extern.FE_0157745_387179_AFH_TCS_WARP:

               objRAP.SaveTCC_toRAP(iHead, tcc1_modifiedDict[heaterElement][iHead], tcc2_dict[heaterElement][iHead], heaterElement, tcc_DH_values)        # this saves values to RAP
               if self.dut.isDriveDualHeater == 0:
                  objRAP.SaveTCC_toRAP(iHead, tcc1_modifiedDict[heaterElement][iHead], tcc2_dict[heaterElement][iHead], "READER_HEATER", tcc_DH_values) 
            else:
               #for iZone in TP.TCS_WARP_ZONES.keys():  

                  objRAP.SaveTCC_toRAP(iHead, tcc1_modifiedDict[heaterElement][iHead], tcc2_dict[heaterElement][iHead], heaterElement, tcc_DH_values, TP.TCS_WARP_ZONES.keys())        # this saves values to RAP
                  if self.dut.isDriveDualHeater == 0:
                     objRAP.SaveTCC_toRAP(iHead, tcc1_modifiedDict[heaterElement][iHead], tcc2_dict[heaterElement][iHead], "READER_HEATER", tcc_DH_values, TP.TCS_WARP_ZONES.keys()) 
         # end of loop.

      self.mFSO.saveRAPtoFLASH()                #Save the settings from RAP to flash (non-volatile)

      #Report coefficients
      RetrieveTcCoeff_prm = TP.Retrieve_TC_Coeff_Prm_172.copy()
      RetrieveTcCoeff_prm['spc_id'] = self.spcID
      self.St( RetrieveTcCoeff_prm )

      # 2nd screen the data
      for heaterElement in heaterElementList:
         self.screenHardFailTCC1_andTCC2( tcc1_modifiedDict[heaterElement], tcc2_dict[heaterElement], tccDict, heaterElement )
         # Note: should also refactor for W+H vs. HO

      heaterElement = "WRITER_HEATER"   # do W+H only mode.

      # 5.  evaluate the temperature capability
      self.evalTempCapAllHeads( tcc1_modifiedDict[heaterElement], tcc2_dict[heaterElement], tccStructDict[heaterElement], tempSpecDict, heaterElement )

      if testSwitch.FE_0258915_348429_COMMON_TWO_TEMP_CERT_SCRN_A00008:
         self.CheckDownGradeOnExtremeTCC( tcc1_modifiedDict[heaterElement] )
      if testSwitch.ENABLE_SMART_TCS_LIMITS_DATA_COLLECTION == 1:
         spc_id = 1
         self.calTempLimitBaseOnTCC(spc_id)

      return tcc1_unModifiedDict, tcc1_modifiedDict, tcc2_dict


   def getTCCDataFromAFHFrames( self, tccDict, heaterElement ):
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

      self.frm.display_frames(2)

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
               if (frame['mode'] == AFH_MODE) and  (frame['PHYS_HD'] == self.dut.LgcToPhysHdMap[iHead]) and (not frame['stateIndex'] in state_list[iHead]) and ( frame['Heater Element'] == heaterElementNameToFramesDict[heaterElement] ):
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
            if ( not frame['stateIndex'] in state_list ):
               state_list.append(frame['stateIndex'])

         first_stateIndex = state_list[len(state_list) - 2]
         second_stateIndex = state_list[len(state_list) - 1]
         if testSwitch.FE_0130771_341036_AFH_FORCE_USE_AFH3_AND_AFH4_IN_TCS_CALC == 1:
            if first_stateIndex != stateTableToAFH_internalStateNumberTranslation[prior_AFH_state]:
               ScrCmds.raiseException(11044, 'Data for %s not found.' % prior_AFH_state)
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

      clearanceDataType = tccDict[heaterElement]['clearanceDataType']

      for iHead in self.headList:
         if testSwitch.ENABLE_TCC_RESET_BY_HEAD_BEFORE_AFH4 == 1 and iHead in self.dut.TccResetHeadList:
            continue
         dWrtClr1_dict[iHead] = {}
         dWrtClr2_dict[iHead] = {}
         dTemp1_dict[iHead] = {}
         dTemp2_dict[iHead] = {}

         for frame in self.frm.dPesSim.DPES_FRAMES:
            iZone = int(frame['Zone'])
            if testSwitch.FE_AFH3_TO_IMPROVE_TCC == 1:
                     if ( (frame['mode'] == AFH_MODE) and (frame['stateIndex'] == first_stateIndex[iHead]) and \
                          (frame['PHYS_HD'] == self.dut.LgcToPhysHdMap[iHead]) and ( frame['Heater Element'] == heaterElementNameToFramesDict[heaterElement] ) ):
                        dWrtClr1_dict[iHead][iZone] = float(frame[clearanceDataType]) * angstromsScaler
                        dTemp1_dict[iHead][iZone] = frame['dPES Measure Temp']

                     if ( (frame['mode'] == AFH_MODE) and (frame['stateIndex'] == second_stateIndex[iHead]) and \
                          (frame['PHYS_HD'] == self.dut.LgcToPhysHdMap[iHead]) and ( frame['Heater Element'] == heaterElementNameToFramesDict[heaterElement] ) ):
                        dWrtClr2_dict[iHead][iZone] = float(frame[clearanceDataType]) * angstromsScaler
                        dTemp2_dict[iHead][iZone] = frame['dPES Measure Temp']
            else:
                     if ( (frame['mode'] == AFH_MODE) and (frame['stateIndex'] == first_stateIndex) and \
                          (frame['PHYS_HD'] == self.dut.LgcToPhysHdMap[iHead]) and ( frame['Heater Element'] == heaterElementNameToFramesDict[heaterElement] ) ):
                        dWrtClr1_dict[iHead][iZone] = float(frame[clearanceDataType]) * angstromsScaler
                        dTemp1_dict[iHead][iZone] = frame['dPES Measure Temp']

                     if ( (frame['mode'] == AFH_MODE) and (frame['stateIndex'] == second_stateIndex) and \
                          (frame['PHYS_HD'] == self.dut.LgcToPhysHdMap[iHead]) and ( frame['Heater Element'] == heaterElementNameToFramesDict[heaterElement] ) ):
                        dWrtClr2_dict[iHead][iZone] = float(frame[clearanceDataType]) * angstromsScaler
                        dTemp2_dict[iHead][iZone] = frame['dPES Measure Temp']


         AllPossiblePositions = []
         if 'onlyChkZonesList' in tccDict[heaterElement].keys():
            AllPossiblePositions = tccDict[heaterElement]['onlyChkZonesList']
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


   def computeOlympicScoredTCC(self, tccStructDict, tccDict, nTempCERT, heaterElement ):
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

      objMsg.printMsg("computeOlympicScoredTCC/ heaterElement: %s " % (heaterElement))


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

      min_temp_diff_between_hot_cold = 14
      tcs_allHeads = []

      if testSwitch.ENABLE_SMART_TCS_LIMITS:
         if heaterElement == "WRITER_HEATER":
            tcc1_loLimitWrtHt, tcc1_upLimitWrtHt = self.SmartTccLimits()

      # initialize values

      for iHead in self.headList:
         if testSwitch.ENABLE_TCC_RESET_BY_HEAD_BEFORE_AFH4 == 1 and iHead in self.dut.TccResetHeadList:
            continue
         skipTCS_calculation = False
         dcdtUnModifiedDict[iHead] = {}
         if not testSwitch.extern.FE_0157745_387179_AFH_TCS_WARP:
            tcc1_unModifiedDict[iHead] = 0.0
            tcc1_modifiedDict[iHead] = 0.0
         else:
            tcc1_unModifiedDict[iHead] = [ 0.0 for zoneGroup in TP.TCS_WARP_ZONES.keys() ]
            tcc1_modifiedDict[iHead] = [ 0.0 for zoneGroup in TP.TCS_WARP_ZONES.keys() ]
         tcc2_dict[iHead] = 0.0

         if nTempCERT == 1:
            if not testSwitch.extern.FE_0157745_387179_AFH_TCS_WARP:
               tcc1_unModifiedDict[iHead] = tccDict[heaterElement]['TCS1']
               tcc1_modifiedDict[iHead] = tccDict[heaterElement]['TCS1']
            else:
               tcc1_unModifiedDict[iHead] = [ tccDict[heaterElement]['TCS1'] for zoneGroup in TP.TCS_WARP_ZONES.keys() ]
               tcc1_modifiedDict[iHead] = [ tccDict[heaterElement]['TCS1'] for zoneGroup in TP.TCS_WARP_ZONES.keys() ] 

            # add minor fail code here.
            curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(135)
            self.dut.objSeq.curRegSPCID = 1

            self.dut.dblData.Tables('P_MINOR_FAIL_CODE').addRecord(
               {
                  'HD_PHYS_PSN'     : self.dut.LgcToPhysHdMap[iHead],
                  'ERROR_CODE'      : 0,
                  'SPC_ID'          : self.spcID,
                  'OCCURRENCE'      : occurrence,
                  'SEQ'             : curSeq,
                  'TEST_SEQ_EVENT'  : testSeqEvent,
                  'HD_LGC_PSN'      : iHead,
                  'TEST_NUMBER'     : 135,
                  'FAIL_DATA'       : "Default TCS1= %s used for heater element: %s on this head." % (tccDict[heaterElement]['TCS1'], heaterElement),
               })
            objMsg.printDblogBin(self.dut.dblData.Tables('P_MINOR_FAIL_CODE'))


         if nTempCERT >= 2:
            if ConfigVars[CN].get('BenchTop', 0) != 0:   # if running in benchTop mode then force 1 Temp CERT
               objMsg.printMsg('Warning!!! - Ignore enforcing a delta Temp for 2 Temp CERT.  Should never be used in real process in factory!!   This is due to BenchTop configVar != 0', objMsg.CMessLvl.IMPORTANT)
            else:
               if (len(dTemp1_dict[iHead].values()) >= 1) and ( len(dTemp2_dict[iHead].values()) >= 1):
                  absoluteMedianDeltaTemp = abs(MathLib.median(dTemp1_dict[iHead].values()) - MathLib.median(dTemp2_dict[iHead].values()))
               else:
                  absoluteMedianDeltaTemp = 7000000   # a clearly bogus number in hopes that
                  # it will cause an error if ever used in a subsequent calculation,
                  # which it is hoped it will NOT be.


#CHOOI-18May17 OffSpec
#                if absoluteMedianDeltaTemp < TP.minTCCTempDifferential and ConfigVars[CN].get('hotBenchTop', 0) == 0:
#                   ScrCmds.raiseException(12517, 'Insufficent (%s C) temperature separation found between hot and cold states' % ( absoluteMedianDeltaTemp )) # at this point print out as much as you can about the local data structures to assist in debug

            objMsg.printMsg('Choosing 2 Temp DH Cert', objMsg.CMessLvl.IMPORTANT)

            # unModified values
            for iZone in commonZoneDict[iHead]:
               deltaTemp = float(dTemp2_dict[iHead][iZone] - dTemp1_dict[iHead][iZone])
               if abs(deltaTemp) < 1e-9:
                  deltaTemp = 1
                  objMsg.printMsg("MeasureTCC/ detected possible divide by zero.  Set delta temp to 1e-9")
               dcdtUnModifiedDict[iHead][iZone] = (dWrtClr2_dict[iHead][iZone] - dWrtClr1_dict[iHead][iZone]) / deltaTemp

            if len(commonZoneDict[iHead]) < AFH_TCS_MINIMUM_NUM_COMMON_VALID_TEST_135_MEASUREMENTS:
               skipTCS_calculation = True
               if not testSwitch.extern.FE_0157745_387179_AFH_TCS_WARP:
                  tcc1_unModifiedDict[iHead] =  tccDict[heaterElement]['TCS1']
                  tcc1_modifiedDict[iHead] =  tccDict[heaterElement]['TCS1']
               else:
                  tcc1_unModifiedDict[iHead] = [ tccDict[heaterElement]['TCS1'] for zoneGroup in TP.TCS_WARP_ZONES.keys() ]
                  tcc1_modifiedDict[iHead] = [ tccDict[heaterElement]['TCS1'] for zoneGroup in TP.TCS_WARP_ZONES.keys() ] 
              
               objMsg.printMsg("MeasureTCC/ Hd: %s less than 3 common positions %s detected." % ( iHead, commonZoneDict[iHead] ))
               if not testSwitch.extern.FE_0157745_387179_AFH_TCS_WARP:
                  objMsg.printMsg("MeasureTCC/ Hd: %s, Skipping computation of TCS.  Relying on default for TCC1 (TCC2 is hard-coded at 0) tcc1: %10.7f, tcc2: %10.7f" %
                     ( iHead, tcc1_unModifiedDict[iHead], tcc2_dict[iHead] ) )
               else:
                  objMsg.printMsg("MeasureTCC/ Hd: %s, Skipping computation of TCS.  Relying on default for TCC1 (TCC2 is hard-coded at 0) tcc1: %10.7f, tcc2: %10.7f" %
                     ( iHead, tcc1_unModifiedDict[iHead][0], tcc2_dict[iHead] ) )
               # add minor fail code here.
               curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(135)
               self.dut.objSeq.curRegSPCID = 1

               self.dut.dblData.Tables('P_MINOR_FAIL_CODE').addRecord(
                  {
                     'HD_PHYS_PSN'     : self.dut.LgcToPhysHdMap[iHead],
                     'ERROR_CODE'      : 0,
                     'SPC_ID'          : self.spcID,
                     'OCCURRENCE'      : occurrence,
                     'SEQ'             : curSeq,
                     'TEST_SEQ_EVENT'  : testSeqEvent,
                     'HD_LGC_PSN'      : iHead,
                     'TEST_NUMBER'     : 135,
                     'FAIL_DATA'       : "Default TCS1= %s used for heater element: %s on this head." % (tccDict[heaterElement]['TCS1'], heaterElement),
                  })
               objMsg.printDblogBin(self.dut.dblData.Tables('P_MINOR_FAIL_CODE'))


            if skipTCS_calculation == False:
               # compute un-modified TCC1
               dcdtList = dcdtUnModifiedDict[iHead].values()
               zoneList = dcdtUnModifiedDict[iHead].keys()
               enableCalculateTCS_RSquare = 0
               if testSwitch.extern.FE_0157745_387179_AFH_TCS_WARP and testSwitch.FE_AFH_RSQUARE_TCC:
                  dcdtList_warp = dcdtList
                  if 1: #dcdtList_warp[heaterElement]['enableCalculateTCS_RSquare'] == 1:
                      dcdtList_abs = [ abs(item) for item in dcdtList_warp ]
                      while( max(dcdtList_abs) >= 0.8):                           
                         dcdtList_warp.pop(dcdtList_abs.index(max(dcdtList_abs)))
                         zoneList.pop(dcdtList_abs.index(max(dcdtList_abs)))
                         dcdtList_abs = [ abs(item) for item in dcdtList_warp ]
                         if(len(dcdtList_warp) <= 4):
                           enableCalculateTCS_RSquare = 0
                           break
                      else:                           
                         while(len(dcdtList_warp) > 4):  
                            #from VBAR import CTripletPicker
                            from MathLib import linreg
                            slope, intercept, Rsq = linreg(zoneList, dcdtList_warp)
                            objMsg.printMsg("slope, intercept, Rsq zoneList dcdtList_warp %s %s %s %s %s" % ( str(slope), str(intercept), str(Rsq), str(zoneList), str(dcdtList_warp) ))
                            if Rsq > 0.5:
                                slope_coef = [25, 75, 125]
                                for zoneGroup in TP.TCS_WARP_ZONES.keys():
                                   tcc1_modifiedDict[iHead][zoneGroup] =  intercept + slope * slope_coef[zoneGroup]    # linear term
                                   tcc1_unModifiedDict[iHead][zoneGroup] =  intercept + slope * slope_coef[zoneGroup]    # linear term
                                objMsg.printMsg("tcc = %s " % ( str(tcc1_modifiedDict[iHead])))
                                enableCalculateTCS_RSquare = 1
                                break
                            else:
                               dcdtList_abs = [ abs(item) for item in dcdtList_warp ]                           
                               dcdtList_warp.pop(dcdtList_abs.index(max(dcdtList_abs)))
                               zoneList.pop(dcdtList_abs.index(max(dcdtList_abs)))
                               if len(dcdtList_warp) <= 4:
                                  enableCalculateTCS_RSquare = 0
                                  break                           
                         else:
                            enableCalculateTCS_RSquare = 0

               
               if enableCalculateTCS_RSquare == 0: 
                  dcdtList = dcdtUnModifiedDict[iHead].values()
                  dcdtList.pop(dcdtList.index(min(dcdtList)))
                  dcdtList.pop(dcdtList.index(max(dcdtList)))
                  if not testSwitch.extern.FE_0157745_387179_AFH_TCS_WARP:
                     tcc1_unModifiedDict[iHead] =  MathLib.mean(dcdtList)    # linear term
                     tcc1_modifiedDict[iHead] =  MathLib.mean(dcdtList)      # linear term
                  else:
                     for zoneGroup in TP.TCS_WARP_ZONES.keys():  
                       tcc1_modifiedDict[iHead][zoneGroup] =  MathLib.mean(dcdtList)   # linear term
                       tcc1_unModifiedDict[iHead][zoneGroup] = MathLib.mean(dcdtList)   # linear term
                  
                  objMsg.printMsg("average tcc = %s " % ( str(tcc1_modifiedDict[iHead])))  


            # Modified values
            if 'enableModifyTCS_values' in tccDict[heaterElement]:
               if tccDict[heaterElement]['enableModifyTCS_values'] == 1:
                  if not testSwitch.extern.FE_0157745_387179_AFH_TCS_WARP :
                     if tcc1_modifiedDict[iHead] > tccDict[heaterElement]['MODIFIED_SLOPE_USL']:
                        tcc1_modifiedDict[iHead] = tccDict[heaterElement]['MODIFIED_SLOPE_USL']

                     if tcc1_modifiedDict[iHead] < tccDict[heaterElement]['MODIFIED_SLOPE_LSL']:
                        tcc1_modifiedDict[iHead] = tccDict[heaterElement]['MODIFIED_SLOPE_LSL']

                     if testSwitch.ENABLE_SMART_TCS_LIMITS:
                        if heaterElement == "WRITER_HEATER":
                           if tcc1_modifiedDict[iHead] > tcc1_upLimitWrtHt[iHead]:
                              objMsg.printMsg("Head:%s WRITER_HEATER Tcc1:%s, over upper spec limit:%s, so reset!" % ( iHead, tcc1_modifiedDict[iHead],tcc1_upLimitWrtHt[iHead] ))
                              tcc1_modifiedDict[iHead] = tcc1_upLimitWrtHt[iHead]

                           if tcc1_modifiedDict[iHead] < tcc1_loLimitWrtHt[iHead]:
                              objMsg.printMsg("Head:%s WRITER_HEATER Tcc1:%s, over lower spec limit:%s, so reset!" % ( iHead, tcc1_modifiedDict[iHead],tcc1_loLimitWrtHt[iHead] ))
                              tcc1_modifiedDict[iHead] = tcc1_loLimitWrtHt[iHead]  
                  else:
                     for zoneGroup in TP.TCS_WARP_ZONES.keys():
                        if tcc1_modifiedDict[iHead][zoneGroup] > tccDict[heaterElement]['MODIFIED_SLOPE_USL']:
                           tcc1_modifiedDict[iHead][zoneGroup] = tccDict[heaterElement]['MODIFIED_SLOPE_USL']

                        if tcc1_modifiedDict[iHead][zoneGroup] < tccDict[heaterElement]['MODIFIED_SLOPE_LSL']:
                           tcc1_modifiedDict[iHead][zoneGroup] = tccDict[heaterElement]['MODIFIED_SLOPE_LSL']

                        if testSwitch.ENABLE_SMART_TCS_LIMITS:
                           if heaterElement == "WRITER_HEATER":
                              if tcc1_modifiedDict[iHead][zoneGroup] > tcc1_upLimitWrtHt[iHead]:
                                 objMsg.printMsg("Head:%s WRITER_HEATER Tcc1:%s, over upper spec limit:%s, so reset!" % ( iHead, tcc1_modifiedDict[iHead][zoneGroup],tcc1_upLimitWrtHt[iHead] ))
                                 tcc1_modifiedDict[iHead][zoneGroup] = tcc1_upLimitWrtHt[iHead]

                              if tcc1_modifiedDict[iHead][zoneGroup] < tcc1_loLimitWrtHt[iHead]:
                                 objMsg.printMsg("Head:%s WRITER_HEATER Tcc1:%s, over lower spec limit:%s, so reset!" % ( iHead, tcc1_modifiedDict[iHead][zoneGroup],tcc1_loLimitWrtHt[iHead] ))
                                 tcc1_modifiedDict[iHead][zoneGroup] = tcc1_loLimitWrtHt[iHead]  
            else:
               tccDict[heaterElement]['enableModifyTCS_values'] = 0
               tccDict[heaterElement]['MODIFIED_SLOPE_USL'] = 999
               tccDict[heaterElement]['MODIFIED_SLOPE_LSL'] = -999

            for iZone in commonZoneDict[iHead]:

               curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(135)
               setDBPrecision = self.oUtility.setDBPrecision

               heaterElementTableDisplay = {
                  "WRITER_HEATER": "W",
                  "READER_HEATER": "R",
               }

               self.dut.LgcToPhysHdMap[iHead]
               heaterElementTableDisplay[ heaterElement ]
               if not testSwitch.extern.FE_0157745_387179_AFH_TCS_WARP :
                  MOD_TCC1 = setDBPrecision( tcc1_modifiedDict[iHead], 0, 3 )
               else:
                  for zoneGroup in TP.TCS_WARP_ZONES.keys():
                     if iZone >= TP.TCS_WARP_ZONES[zoneGroup][0] and  iZone <= TP.TCS_WARP_ZONES[zoneGroup][1]:
                         MOD_TCC1 = setDBPrecision( tcc1_modifiedDict[iHead][zoneGroup], 0, 3 )
                         break
               dictRow = {
                  'HD_PHYS_PSN'    :self.dut.LgcToPhysHdMap[iHead],
                  'ACTIVE_HEATER'  : heaterElementTableDisplay[ heaterElement ],
                  'DATA_ZONE'      : iZone,
                  'SPC_ID'         : self.spcID,
                  'OCCURRENCE'     : occurrence,
                  'SEQ'            : curSeq,
                  'TEST_SEQ_EVENT' : testSeqEvent,
                  'HD_LGC_PSN'     : iHead,
                  'CLR_ACTUATION_MODE' : tccDict[heaterElement]['clearanceDataType'],
                  'WRT_CLR_1'      : setDBPrecision( dWrtClr1_dict[iHead][iZone], 0, 2 ),
                  'TEMP_1'         : dTemp1_dict[iHead][iZone],
                  'WRT_CLR_2'      : setDBPrecision( dWrtClr2_dict[iHead][iZone], 0, 2 ),
                  'TEMP_2'         : dTemp2_dict[iHead][iZone],
                  'RAW_SLOPE_MSRMNT'     : setDBPrecision( dcdtUnModifiedDict[iHead][iZone], 0, 3 ),
                  'RAW_TCC_1'      : MOD_TCC1, #setDBPrecision( tcc1_unModifiedDict[iHead], 0, 3 ),
                  'MOD_SLOPE_LSL'  : setDBPrecision( tccDict[heaterElement]['MODIFIED_SLOPE_LSL'], 0, 3 ),
                  'MOD_SLOPE_USL'  : setDBPrecision( tccDict[heaterElement]['MODIFIED_SLOPE_USL'], 0, 3 ),
                  'MOD_TCC_1'      : MOD_TCC1,
                  'RAW_TCC_2'          : setDBPrecision( tcc2_dict[iHead], 0, 3 ),
                  }

               self.dut.dblData.Tables('P_AFH_DH_MEASURED_TCC').addRecord( dictRow )
               objMsg.printMsg("computeOlympicScoredTCC/ dictRow: %s" % ( dictRow ))

      objMsg.printDblogBin(self.dut.dblData.Tables('P_AFH_DH_MEASURED_TCC'))

      return tcc1_unModifiedDict, tcc1_modifiedDict, tcc2_dict


   def screenHardFailTCC1_andTCC2(self, tcc1_dict, tcc2_dict, tccDict, heaterElement ):
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
         if testSwitch.extern.FE_0157745_387179_AFH_TCS_WARP :
             for zoneGroup in TP.TCS_WARP_ZONES.keys():
                if (tcc1_dict[iHead][zoneGroup] > tccDict[heaterElement]['TCS1_USL']):
                   ScrCmds.raiseException(14722, 'Hd: %s TCS: %s exceeded upper spec limit: %s' % (str(iHead), str(tcc1_dict[iHead][zoneGroup]), str(tccDict[heaterElement]['TCS1_USL'])))
                if (tcc1_dict[iHead][zoneGroup] < tccDict[heaterElement]['TCS1_LSL']):
                   ScrCmds.raiseException(14722, 'Hd: %s TCS: %s exceeded lower spec limit: %s' % (str(iHead), str(tcc1_dict[iHead][zoneGroup]), str(tccDict[heaterElement]['TCS1_LSL'])))
         else:
            if (tcc1_dict[iHead] > tccDict[heaterElement]['TCS1_USL']):
               ScrCmds.raiseException(14722, 'Hd: %s TCS: %s exceeded upper spec limit: %s' % (str(iHead), str(tcc1_dict[iHead]), str(tccDict[heaterElement]['TCS1_USL'])))
            if (tcc1_dict[iHead] < tccDict[heaterElement]['TCS1_LSL']):
               ScrCmds.raiseException(14722, 'Hd: %s TCS: %s exceeded lower spec limit: %s' % (str(iHead), str(tcc1_dict[iHead]), str(tccDict[heaterElement]['TCS1_LSL'])))
         if (tcc2_dict[iHead] > tccDict[heaterElement]['TCS2_USL']):
            ScrCmds.raiseException(14722, 'Hd: %s TCS: %s exceeded upper spec limit: %s' % (str(iHead), str(tcc2_dict[iHead]), str(tccDict[heaterElement]['TCS2_USL'])))
         if (tcc2_dict[iHead] < tccDict[heaterElement]['TCS2_LSL']):
            ScrCmds.raiseException(14722, 'Hd: %s TCS: %s exceeded lower spec limit: %s' % (str(iHead), str(tcc2_dict[iHead]), str(tccDict[heaterElement]['TCS2_LSL'])))

      # end of screenHardFailTCC1_andTCC2
   def CheckDownGradeOnExtremeTCC(self, tcc1_modifiedDict):
      import cPickle, SIM_FSO
      data = SIM_FSO.CSimpleSIMFile("VBAR_DATA").read()
      wpp, (tableData, colHdrData) = cPickle.loads(data)
      
      #measAllZns.unserialize((tableData, colHdrData))
      meas = {}
      try:
      
         for rowData in tableData:
            # Determine the hd, zn, and wp information, to be used for the data dictionary keys.
            (hd, zn) = rowData[:2]
   
            # Now use that hd, zn, wp information to construct a dictionary, using the data
            # in the column hdr list and the associated values in the row data list.
            if not meas.has_key((hd, zn)):
               meas[(hd, zn)]={}
            meas[(hd, zn)] = dict(zip(colHdrData[2:], rowData[2:]))
      except:
         objMsg.printMsg('VBAR SIM data not available')
         objMsg.printMsg(traceback.format_exc())
         objMsg.printMsg("Same_Two_Temp_CERT_Downgrade Unable to Trigger %s" % fail_List)
         return
      
      fail_hd = []
      for hd in self.headList: #range(self.dut.imaxHead):
         data_list = []
         for zn in range(self.dut.numZones):
            if meas.has_key((hd, zn)):
               #objMsg.printMsg('VBAR BPIMH hd %d zn %d Rsq %.4f' % (hd,zn, meas[(hd, zn)]['BPIMH']))
               data_list.append(meas[(hd, zn)]['BPIMH'])
         if len(data_list):
            average_data = float(sum(data_list)/len(data_list))
            objMsg.printMsg('VBAR_DBG hd %d Ave_HMSM %4f' % (hd, average_data))
            if average_data > 0.03:
               fail_hd.append(hd)
               
      for iHead in self.headList:
         if not testSwitch.extern.FE_0157745_387179_AFH_TCS_WARP :
            objMsg.printMsg('TCC_DBG hd %d TCC1 %.4f' % (hd, tcc1_modifiedDict[iHead]))
            if (tcc1_modifiedDict[iHead] > 0.18) and iHead in fail_hd:
               if self.dut.CAPACITY_CUS.find('STD') < 0 and not self.downGradeOnFly(1, 14722):
                  if self.downGradeOnFly(1, 14722):
                     objMsg.printMsg("Same_Two_Temp_CERT_Downgrade Trigger %s" % fail_List)
                  else:
                     objMsg.printMsg("Same_Two_Temp_CERT_Downgrade Unable to Trigger %s" % fail_List)
         else:    
            for zoneGroup in TP.TCS_WARP_ZONES.keys():
               objMsg.printMsg('TCC_DBG hd %d zngroup %d TCC1 %.4f' % (hd,zoneGroup, tcc1_modifiedDict[iHead][zoneGroup]))
               if (tcc1_modifiedDict[iHead][zoneGroup] > 0.18) and iHead in fail_hd:
                  if self.dut.CAPACITY_CUS.find('STD') < 0 and not self.downGradeOnFly(1, 14722):
                     if self.downGradeOnFly(1, 14722):
                        objMsg.printMsg("Same_Two_Temp_CERT_Downgrade Trigger %s" % fail_List)
                     else:
                        objMsg.printMsg("Same_Two_Temp_CERT_Downgrade Unable to Trigger %s" % fail_List)


   def burnishCheck(self, burnish_params, minClr_params, validState = 0, partial_AFH3_passed_head = [], fail_any_zone = 0):
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

      ## note minClr_params is deprecated and NOT used.

      self.request_reRunVBAR = False

      if testSwitch.FE_0165920_341036_DISABLE_READER_HEATER_CONTACT_DETECT_AFH2:
         heaterElementList = self.dut.heaterElementList
      else:
         heaterElementList = [ "WRITER_HEATER" ]
         if self.dut.isDriveDualHeater == 1 and testSwitch.AFH_BURNISH_CHECK_BYPASS_READER_CLR == 0:
            heaterElementList.append( "READER_HEATER" )

      for heaterElement in heaterElementList:
         burnish_paramsByHeaterElement = burnish_params[heaterElement]

         self.burnishCheckSingleElement( burnish_paramsByHeaterElement, heaterElement, validState, partial_AFH3_passed_head = partial_AFH3_passed_head, fail_any_zone = fail_any_zone  )

      if self.request_reRunVBAR:
         # Check to make sure we haven't exceeded our VBAR rerun limit
         self.dut.rerunVbar += 1
         if self.dut.rerunVbar > 1:
            ScrCmds.raiseException(14799, "Attempting to start restart VBAR more than once. Fail to avoid infinite loop")
         self.dut.stateTransitionEvent = 'reRunVBAR'        # this shouldn't be updated until we are sure we are going to re-run VBAR
         self.dut.objData.update({'RERUN_VBAR':self.dut.rerunVbar})

      # end of burnishCheck


   def burnishCheckSingleElement(self, burnish_params, heaterElement, validState = 0, partial_AFH3_passed_head = [], fail_any_zone = 0):
      """
      #######################################################################################################################
      #
      #               Function:  burnishCheckSingleElement
      #
      #        Original Author:  Michael T. Brady
      #
      #            Description:  checks for burnishing on the heads for a single head element( reader/writer) at one time
      #
      #          Prerrequisite:  run FH contact detect at least 2 times
      #
      #                  Input:  burnish_params(dict), heaterElement(str), validState(int)
      #
      #                 Return:  P_AFH_DH_BURNISH_CHECK or P_BURNISH_CHECK2 DBLog table (DBLog Tbl)
      #
      #######################################################################################################################

      """

      if (validState == 0):
         objMsg.printMsg('Skipping burnish check between states %s and %s.  Currently in state: %s' % \
            ( burnish_params['groupA_nth_AFH_state'], burnish_params['groupB_nth_AFH_state'], self.AFH_State))
         return -1

      objMsg.printMsg('burnishCheck/ validState: %s, burnish_params: %s' % (validState, burnish_params))
      self.frm.readFramesFromCM_SIM()
      self.frm.display_frames(2)

      local_clrDict1 = CclearanceDictionary()
      local_clrDict2 = CclearanceDictionary()
      if  burnish_params.get('comparison_type', '') == 'abs_rddac' :
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

      if testSwitch.FE_0165687_341036_AFH_SKIP_DELTA_VBAR_CHK_AFH2B_READER_HTR == 1:
         if (stateTableName == 'AFH2B') and (burnish_params['mode'] == 'delta_VBAR') and (heaterElement == "READER_HEATER"):
            objMsg.printMsg("burnishCheckSingleElement/ Skipping delta VBAR burnish check in state 'AFH2B' for the 'READER_HEATER'.")
            DELTA_VBAR_BURNISH_CHECK_SKIPPED = -3
            return DELTA_VBAR_BURNISH_CHECK_SKIPPED

      if testSwitch.FE_0165920_341036_DISABLE_READER_HEATER_CONTACT_DETECT_AFH2:
         if (heaterElement == "READER_HEATER"):
            if self.AFH_State == 3:
               firstState = stateTableToAFH_internalStateNumberTranslation['AFH1']
               secondState = stateTableToAFH_internalStateNumberTranslation['AFH3']
            else:
               READER_HEATER_BURNISH_CHECK_SKIPPED = -4
               return READER_HEATER_BURNISH_CHECK_SKIPPED


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

            if ( (frame['mode'] == desiredAFH_MODE) and \
               (frame['Heater Element'] == heaterElementNameToFramesDict[heaterElement]) and \
               (frame['stateIndex'] == firstState) and \
               (frame['PHYS_HD'] == self.dut.LgcToPhysHdMap[iHead])):
               local_clrDict1.setClrDict( iHead, frame['Zone'], frame['Read Clearance'], frame['WrtLoss'], frame['Write Clearance'], frame['Zone'] )
               if burnish_params.get('comparison_type', '') == 'abs_rddac' :
                  local_DACDict1.setDACDict( iHead, frame['Zone'], frame['Write Heat Contact DAC'], frame['Heater Only Contact DAC'], frame['Zone'] )

      for frame in self.frm.dPesSim.DPES_FRAMES:
         for iHead in self.headList:

            if ( (frame['mode'] == desiredAFH_MODE) and \
               (frame['Heater Element'] == heaterElementNameToFramesDict[heaterElement]) and \
               (frame['stateIndex'] == secondState) and \
               (frame['PHYS_HD'] == self.dut.LgcToPhysHdMap[iHead])):
               local_clrDict2.setClrDict( iHead, frame['Zone'], frame['Read Clearance'], frame['WrtLoss'], frame['Write Clearance'], frame['Zone'] )
               if burnish_params.get('comparison_type', '') == 'abs_rddac' :
                  local_DACDict2.setDACDict( iHead, frame['Zone'], frame['Write Heat Contact DAC'], frame['Heater Only Contact DAC'], frame['Zone'] )

      #
      for iHead in self.headList:
         if not (iHead in local_clrDict1.clrDict):
            ScrCmds.raiseException(42187, 'local_clrDict1.clrDict: %s  Hd: %s No data found for burnish Check' % ( local_clrDict1.clrDict, iHead ))
         if not (iHead in local_clrDict2.clrDict):
            if testSwitch.FE_AFH3_TO_DO_BURNISH_CHECK == 1 and self.AFH_State == 3 and iHead in partial_AFH3_passed_head :
               pass #partial_AFH3_passed_head.append(iHead) 
            else:
               ScrCmds.raiseException(42187, 'local_clrDict2.clrDict: %s  Hd: %s No data found for burnish Check' % ( local_clrDict2.clrDict, iHead ))
         if burnish_params.get('comparison_type', '') == 'abs_rddac' :
            if not (iHead in local_DACDict1.clrDict):
               ScrCmds.raiseException(42187, 'local_DACDict1.clrDict: %s  Hd: %s No data found for burnish Check' % ( local_DACDict1.clrDict, iHead ))
            if not (iHead in local_DACDict2.clrDict):
               ScrCmds.raiseException(42187, 'local_DACDict2.clrDict: %s  Hd: %s No data found for burnish Check' % ( local_DACDict2.clrDict, iHead ))

         # what about the not enough data found case!
         if len(local_clrDict1.clrDict[iHead]) < 2:
            ScrCmds.raiseException(42187, 'local_clrDict1.clrDict: %s  Hd: %s Not enough data found for burnish Check' % ( local_clrDict1.clrDict, iHead ))
         if testSwitch.FE_AFH3_TO_DO_BURNISH_CHECK == 1 and self.AFH_State == 3 :
             if iHead not in partial_AFH3_passed_head:
               if len(local_clrDict2.clrDict[iHead]) < 2:
                  ScrCmds.raiseException(42187, 'local_clrDict2.clrDict: %s  Hd: %s Not enough data found for burnish Check' % ( local_clrDict2.clrDict, iHead ))
         if burnish_params.get('comparison_type', '') == 'abs_rddac' :
            if len(local_DACDict1.clrDict[iHead]) < 2:
               ScrCmds.raiseException(42187, 'local_DACDict1.clrDict: %s  Hd: %s Not enough data found for burnish Check' % ( local_DACDict1.clrDict, iHead ))
            if len(local_DACDict2.clrDict[iHead]) < 2:
               ScrCmds.raiseException(42187, 'local_DACDict2.clrDict: %s  Hd: %s Not enough data found for burnish Check' % ( local_DACDict2.clrDict, iHead ))

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
         ScrCmds.raiseException(42187, 'Error no temperature data found!') # at this point print out as much as you can about the local data structures to assist in debug


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

      if burnish_params.get('comparison_type', '') == 'abs_rddac' :
         if( (local_DACDict1.clrDict == {}) or (local_DACDict2.clrDict == {}) ):
             ScrCmds.raiseException(42187, 'local_DACDict1.clrDict: %s, local_DACDict2.clrDict: %s; FRAMES data not found for burnish Check... exiting early return -1' % (str(local_DACDict1.clrDict), str(local_DACDict2.clrDict)))

      if burnish_params.get('comparison_type', '') == 'abs_rddac' :
         AFH_clearanceTypeIndex =  AFH_RdDac
         if heaterElement == "WRITER_HEATER":
            AFH_clearanceActuationModeStr = "PreHeatWrt_Dac"
         else:
            AFH_clearanceActuationModeStr = "Read_Dac"
      else:
         if testSwitch.AFH_BURNISH_CHECK_BYPASS_READER_CLR == 0:
            AFH_clearanceTypeIndex = AFH_RdClr
            if heaterElement == "WRITER_HEATER":
               AFH_clearanceActuationModeStr = "PreHeatWrt_Clr"
            else:
               AFH_clearanceActuationModeStr = "Read_Clearance"
         else:             
            if heaterElement == "WRITER_HEATER":
               AFH_clearanceTypeIndex = AFH_WHClr
               AFH_clearanceActuationModeStr = "Write_Clearance" 
            else:
               AFH_clearanceTypeIndex = AFH_RdClr
               AFH_clearanceActuationModeStr = "Read_Clearance"

      # use rdClr for both the WRITER_HEATER (pre-heat) and READER_HEATER (read heat)

      spc_id = 0
      try:
         prevBurnishTable = self.dut.dblData.Tables('P_AFH_DH_BURNISH_CHECK').tableDataObj()
         spc_id = int(prevBurnishTable[len(prevBurnishTable)-1]['SPC_ID']) + 1
         if (testSwitch.AFH2_FAIL_BURNISH_RERUN_AFH1 and self.AFH_State == stateTableToAFH_internalStateNumberTranslation['AFH2']) or (testSwitch.FE_AFH3_TO_DO_BURNISH_CHECK and self.AFH_State == stateTableToAFH_internalStateNumberTranslation['AFH3']):
            if self.dut.BurnishFailedHeads:
               spc_id += 1000           
      except:
         prevBurnishTable = {}
         spc_id = self.spcID

      curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(35)
      setDBPrecision = self.oUtility.setDBPrecision

      # calculate burnish algorithm
      hdStatus = {}
      hdStatusSub = {}
      deltaBurnishCheck = {}
      deltaBurnish = ''
      for iHead in local_clrDict1.clrDict.keys():

         if testSwitch.FE_AFH3_TO_DO_BURNISH_CHECK == 1 and self.AFH_State == 3 :
             if iHead in partial_AFH3_passed_head:
                hdStatus[iHead] = PASS   # head status should default to pass
                hdStatusSub[iHead] = PASS   # head status should default to pass
                continue
         hdStatus[iHead] = PASS   # head status should default to pass
         hdStatusSub[iHead] = PASS   # head status should default to pass
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

         #

         heaterElementTableDisplay = {
            "WRITER_HEATER": "W",
            "READER_HEATER": "R",
         }


         if burnish_params['mode'] == 'burnish':
            listWrtClrFirstState = []
            listWrtClrSecondState = []
            if burnish_params.get('comparison_type', '') == 'abs_rddac' :
               objMsg.printMsg("Burnish Check by RD Dac ")
               for meas in listCommonPos:
                  listWrtClrFirstState.append(local_DACDict1.clrDict[iHead][meas][AFH_clearanceTypeIndex])
                  listWrtClrSecondState.append(local_DACDict2.clrDict[iHead][meas][AFH_clearanceTypeIndex])
            else:
               for meas in listCommonPos:
                  listWrtClrFirstState.append(local_clrDict1.clrDict[iHead][meas][AFH_clearanceTypeIndex])
                  listWrtClrSecondState.append(local_clrDict2.clrDict[iHead][meas][AFH_clearanceTypeIndex])



            if (len(listWrtClrFirstState) < 2 ) or (len(listWrtClrSecondState) < 2):
               if burnish_params.get('comparison_type', '') == 'abs_rddac' :
                  objMsg.printMsg("burnishCheck/ local_DACDict1.clrDict: %s" % (local_DACDict1.clrDict))
                  objMsg.printMsg("burnishCheck/ local_DACDict2.clrDict: %s" % (local_DACDict2.clrDict))
                  objMsg.printMsg("burnishCheck/ listWrtClrFirstState: %s, listWrtClrSecondState: %s" % (listWrtClrFirstState, listWrtClrSecondState))
                  ScrCmds.raiseException(42187, "burnishCheck/ failed!  Insufficent Data.")
               else:
                  objMsg.printMsg("burnishCheck/ local_clrDict1.clrDict: %s" % (local_clrDict1.clrDict))
                  objMsg.printMsg("burnishCheck/ local_clrDict2.clrDict: %s" % (local_clrDict2.clrDict))
                  objMsg.printMsg("burnishCheck/ listWrtClrFirstState: %s, listWrtClrSecondState: %s" % (listWrtClrFirstState, listWrtClrSecondState))
                  ScrCmds.raiseException(42187, "burnishCheck/ failed!  Insufficent Data.")


            lowest_pos = listWrtClrFirstState.index(min(listWrtClrFirstState))

            listWrtClrFirstState.pop(lowest_pos)
            listWrtClrSecondState.pop(lowest_pos)
            if fail_any_zone: 
               positiveDelta = -999
               negativeDelta =  999
               for ii in range(0, len(listWrtClrFirstState)):
                  deltaClr = listWrtClrSecondState[ii] - listWrtClrFirstState[ii]
                  if deltaClr >= positiveDelta:
                     positiveDelta = deltaClr
                  if deltaClr <= negativeDelta:
                     negativeDelta = deltaClr
               objMsg.printMsg('Max_positive_delta_clr: %s ' % str(positiveDelta), objMsg.CMessLvl.CRITICAL)
               objMsg.printMsg('Min_negative_delta_clr: %s ' % str(negativeDelta), objMsg.CMessLvl.CRITICAL)
            adjAvgWrtClrFirstState = MathLib.mean(listWrtClrFirstState)
            adjAvgWrtClrSecondState = MathLib.mean(listWrtClrSecondState)

            deltaBurnishCheck = adjAvgWrtClrSecondState - adjAvgWrtClrFirstState

            if burnish_params.get('comparison_type', '') != 'abs_rddac' :
                if (testSwitch.AFH_ENABLE_ANGSTROMS_SCALER_USE_254 == 1):
                   if ( abs(burnish_params['twoSidedLimit_USL']) < 1.0 ) or ( abs(burnish_params['twoSidedLimit_LSL']) < 1.0 ):
                      ScrCmds.raiseException(11044, 'burnishCheck/ Burnish input params: twoSidedLimit_USL and twoSidedLimit_LSL must be in Angstroms with flag AFH_ENABLE_ANGSTROMS_SCALER_USE_254 enabled.') # at this point print out as much as you can about the local data structures to assist in debug
            if fail_any_zone:
               if (positiveDelta > burnish_params['twoSidedLimit_USL']):
                  hdStatus[iHead] = FAIL   # Fail
                  deltaBurnishCheck = positiveDelta
                  if (positiveDelta > burnish_params['twoSidedHardLimit_USL']):
                     hdStatusSub[iHead] = FAIL 
               if (negativeDelta < burnish_params['twoSidedLimit_LSL']):
                  hdStatus[iHead] = FAIL   # Fail
                  deltaBurnishCheck = negativeDelta
                  if (negativeDelta < burnish_params['twoSidedHardLimit_LSL']):
                     hdStatusSub[iHead] = FAIL 
            else:
               if (deltaBurnishCheck > burnish_params['twoSidedLimit_USL']):
                  hdStatus[iHead] = FAIL   # Fail
                  if (deltaBurnishCheck > burnish_params['twoSidedHardLimit_USL']):
                     hdStatusSub[iHead] = FAIL 
               if (deltaBurnishCheck < burnish_params['twoSidedLimit_LSL']):
                  hdStatus[iHead] = FAIL   # Fail
                  if (deltaBurnishCheck < burnish_params['twoSidedHardLimit_LSL']):
                     hdStatusSub[iHead] = FAIL 
            if DEBUG:
               objMsg.printMsg('Head: %s, state: %s, listWrtClrFirstState:%s, adjAvgWrtClrFirstState: %s, state: %s, listWrtClrSecondState: %s, adjAvgWrtClrSecondState: %s, delta (2nd-1st) burnish check  : %s, USL: %s, LSL: %s, pass(1)/fail(0): %s' % \
                     (iHead, firstState, listWrtClrFirstState, adjAvgWrtClrFirstState, secondState, \
                     listWrtClrSecondState, adjAvgWrtClrSecondState, deltaBurnishCheck, burnish_params['twoSidedLimit_USL'], burnish_params['twoSidedLimit_LSL'], hdStatus[iHead]) )

            # -------------->  output burnish data to DBLog table  <---------------------------------


            for meas in listCommonPos:
               if burnish_params.get('comparison_type', '') == 'abs_rddac' :
                  clr1     = setDBPrecision(local_DACDict1.clrDict[iHead][meas][AFH_clearanceTypeIndex], 0, 4)
                  clr2     = setDBPrecision(local_DACDict2.clrDict[iHead][meas][AFH_clearanceTypeIndex], 0, 4)
               else:
                  clr1     = setDBPrecision(local_clrDict1.clrDict[iHead][meas][AFH_clearanceTypeIndex], 0, 4)
                  clr2     = setDBPrecision(local_clrDict2.clrDict[iHead][meas][AFH_clearanceTypeIndex], 0, 4)
               self.dut.dblData.Tables('P_AFH_DH_BURNISH_CHECK').addRecord(
                  {
                  'SPC_ID'             : spc_id,
                  'OCCURRENCE'         : occurrence,
                  'SEQ'                : curSeq,
                  'TEST_SEQ_EVENT'     : testSeqEvent,
                  'TEST_TYPE'          : burnish_params['mode'],
                  'ACTIVE_HEATER'      : heaterElementTableDisplay[heaterElement],
                  'CLR_ACTUATION_MODE' : AFH_clearanceActuationModeStr,
                  'HD_PHYS_PSN'        : self.dut.LgcToPhysHdMap[iHead],
                  'TEST_PSN'           : meas,
                  'HD_LGC_PSN'         : iHead,
                  'WRT_HTR_CLR_1'      : clr1, #setDBPrecision(local_clrDict1.clrDict[iHead][meas][AFH_clearanceTypeIndex], 0, 4),
                  'WRT_HTR_CLR_2'      : clr2, #setDBPrecision(local_clrDict2.clrDict[iHead][meas][AFH_clearanceTypeIndex], 0, 4),
                  'MOD_CALC_AVG_1'     : setDBPrecision(adjAvgWrtClrFirstState, 0, 4),
                  'MOD_CALC_AVG_2'     : setDBPrecision(adjAvgWrtClrSecondState, 0, 4),
                  'DELTA_BURNISH_CHECK': setDBPrecision(deltaBurnishCheck, 0, 4),
                  'BURNISH_USL'        : setDBPrecision(burnish_params['twoSidedLimit_USL'], 0, 4),
                  'HD_STATUS'          : str(hdStatus[iHead]),
                  'BURNISH_LSL'        : setDBPrecision(burnish_params['twoSidedLimit_LSL'], 0, 4),
                  })

         else:    # delta VBAR clearance check
            objMsg.printMsg('Performing delta VBAR clearance calculation (by position comparison) ... not traditional burnish check calculation')

            for meas in listCommonPos:

               deltaBurnishCheck = local_clrDict2.clrDict[iHead][meas][AFH_clearanceTypeIndex] - local_clrDict1.clrDict[iHead][meas][AFH_clearanceTypeIndex]

               if (testSwitch.AFH_ENABLE_ANGSTROMS_SCALER_USE_254 == 1):
                  if ( abs(burnish_params['twoSidedLimit_USL']) < 1.0 ) or ( abs(burnish_params['twoSidedLimit_LSL']) < 1.0 ):
                     ScrCmds.raiseException(11044, 'burnishCheck/ Burnish input params: twoSidedLimit_USL and twoSidedLimit_LSL must be in Angstroms with flag AFH_ENABLE_ANGSTROMS_SCALER_USE_254 enabled.') # at this point print out as much as you can about the local data structures to assist in debug

               if (deltaBurnishCheck > burnish_params['twoSidedLimit_USL']):
                  hdStatus[iHead] = FAIL   # Fail
               if (deltaBurnishCheck < burnish_params['twoSidedLimit_LSL']):
                  hdStatus[iHead] = FAIL   # Fail


               if DEBUG:
                  objMsg.printMsg('Head: %s, state: %s, heaterElement: %s, Clr1: %5.2f, state: %s, Clr2: %5.2f, delta (2nd-1st) burnish check  : %5.2f, USL: %5.2f, LSL: %5.2f, pass(1)/fail(0): %s' % \
                     (iHead, firstState, heaterElement, local_clrDict1.clrDict[iHead][meas][AFH_clearanceTypeIndex], \
                        secondState, local_clrDict2.clrDict[iHead][meas][AFH_clearanceTypeIndex], \
                        deltaBurnishCheck, burnish_params['twoSidedLimit_USL'], burnish_params['twoSidedLimit_LSL'], hdStatus[iHead]) )

               adjAvgWrtClrFirstState = -1
               adjAvgWrtClrSecondState = -1  # these have no meaning in the delta VBAR clearance algorithm where each position is now checked individually

               self.dut.dblData.Tables('P_AFH_DH_BURNISH_CHECK').addRecord(
                  {
                  'SPC_ID'             : spc_id,
                  'OCCURRENCE'         : occurrence,
                  'SEQ'                : curSeq,
                  'TEST_SEQ_EVENT'     : testSeqEvent,
                  'TEST_TYPE'          : burnish_params['mode'],
                  'ACTIVE_HEATER'      : heaterElementTableDisplay[heaterElement],
                  'CLR_ACTUATION_MODE' : AFH_clearanceActuationModeStr,
                  'HD_PHYS_PSN'        : self.dut.LgcToPhysHdMap[iHead],
                  'TEST_PSN'           : meas,
                  'HD_LGC_PSN'         : iHead,
                  'WRT_HTR_CLR_1'      : setDBPrecision(local_clrDict1.clrDict[iHead][meas][AFH_clearanceTypeIndex], 0, 4),
                  'WRT_HTR_CLR_2'      : setDBPrecision(local_clrDict2.clrDict[iHead][meas][AFH_clearanceTypeIndex], 0, 4),
                  'MOD_CALC_AVG_1'     : setDBPrecision(adjAvgWrtClrFirstState, 0, 4),
                  'MOD_CALC_AVG_2'     : setDBPrecision(adjAvgWrtClrSecondState, 0, 4),
                  'DELTA_BURNISH_CHECK'  : setDBPrecision(deltaBurnishCheck, 0, 4),
                  'BURNISH_USL'          : setDBPrecision(burnish_params['twoSidedLimit_USL'], 0, 4),
                  'HD_STATUS'            : str(hdStatus[iHead]),
                  'BURNISH_LSL'          : setDBPrecision(burnish_params['twoSidedLimit_LSL'], 0, 4),
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
      if testSwitch.FE_AFH3_TO_DO_BURNISH_CHECK == 1 and self.AFH_State == stateTableToAFH_internalStateNumberTranslation['AFH3'] :
         try:
            objMsg.printDblogBin(self.dut.dblData.Tables('P_AFH_DH_BURNISH_CHECK'))
         except:
            pass

      if burnish_params['mode'] == 'burnish':

         # -------------->  fail the drive here for burnishing  <---------------------------------
         if (testSwitch.AFH2_FAIL_BURNISH_RERUN_AFH1 and self.AFH_State == stateTableToAFH_internalStateNumberTranslation['AFH2']) or (testSwitch.FE_AFH3_TO_DO_BURNISH_CHECK and self.AFH_State == stateTableToAFH_internalStateNumberTranslation['AFH3']):
            reAFHburnish_fail_heads = []
         for iHead in local_clrDict1.clrDict.keys():
            if testSwitch.FE_AFH3_TO_DO_BURNISH_CHECK == 1 and self.AFH_State == 3 :
               if iHead in partial_AFH3_passed_head:
                  continue
            if (hdStatus[iHead] == 0):
               objMsg.printMsg('Head: %s failed for burnishing ' % str(iHead), objMsg.CMessLvl.CRITICAL)
               if hdStatusSub[iHead] == 0:
                  ScrCmds.raiseException(14570, "Failed for burnishing @ Head : [%s]" % str(iHead))
               if (testSwitch.AFH2_FAIL_BURNISH_RERUN_AFH1 and self.AFH_State == stateTableToAFH_internalStateNumberTranslation['AFH2']) or (testSwitch.FE_AFH3_TO_DO_BURNISH_CHECK and self.AFH_State == stateTableToAFH_internalStateNumberTranslation['AFH3']):
                  self.dut.BurnishFailedHeads.append(iHead)
               if (testSwitch.AFH2_FAIL_BURNISH_RERUN_AFH1 and self.AFH_State == stateTableToAFH_internalStateNumberTranslation['AFH2']) or (testSwitch.FE_AFH3_TO_DO_BURNISH_CHECK and self.AFH_State == stateTableToAFH_internalStateNumberTranslation['AFH3']):
                  reAFHburnish_fail_heads.append(iHead)
               else:      
                  ScrCmds.raiseException(14559, "Head: %s failed for burnishing " % str(iHead))
         if (testSwitch.AFH2_FAIL_BURNISH_RERUN_AFH1 and self.AFH_State == stateTableToAFH_internalStateNumberTranslation['AFH2']) or (testSwitch.FE_AFH3_TO_DO_BURNISH_CHECK and self.AFH_State == stateTableToAFH_internalStateNumberTranslation['AFH3']):
            if reAFHburnish_fail_heads != []:
               ScrCmds.raiseException(14559, "Head: %s failed for burnishing " % str(reAFHburnish_fail_heads))                           
         objMsg.printMsg('*' * 40 + ' End of Checking deltas between 1st and 2nd measurements for burnishing ' + '*' * 40)
         return self.dut.dblData.Tables('P_AFH_DH_BURNISH_CHECK').tableDataObj()

      if burnish_params['mode'] == 'delta_VBAR':
         for iHead in local_clrDict1.clrDict.keys():

            # For VE only, force a failure first time through only to exercise the restartVbar transition
            if (testSwitch.virtualRun):
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
                     self.request_reRunVBAR = True

         return self.dut.dblData.Tables('P_AFH_DH_BURNISH_CHECK').tableDataObj()


   def crossStrokeClrCheck(self, crossStrokeClrLimit):
      objMsg.printMsg("crossStrokeClrCheck is disabled.  Please rely upon T135 internal checks instead.")


   def clearanceRangeCheck(self, clrRangeChkLimit):
      objMsg.printMsg("clearanceRangeCheck is disabled.  Please rely upon T135 internal checks instead.")


   def extreme_OD_ID_clearanceRangeCheck(self, extreme_OD_ID_clearanceRangeCheck):
      objMsg.printMsg("extreme_OD_ID_clearanceRangeCheck is disabled.  Please rely upon T135 internal checks instead.")
