#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: base TCC calibration states
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/09/23 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_TccCal.py $
# $Revision: #4 $
# $DateTime: 2016/09/23 03:40:27 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_TccCal.py#4 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
import MessageHandler as objMsg
from State import CState
from PowerControl import objPwrCtrl
from MathLib import mean, stDev_standard
import ScrCmds
import sptCmds
from Exceptions import EndOfPackException, InvalidTrackException

DEBUG = 0
DEBUG_TCC = 0


#-------------------------------------------------------------------------------------------------------
class CRampTempDiff(CState):
   """
      Description: Class that will perform a confirmed HDA start temperature differential.
      Base: N/A
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):

      from AFH import CdPES
      odPES = CdPES(TP.masterHeatPrm_11, TP.defaultOCLIM)
      # Retrieve minimum Temperature from AFH 3
      if testSwitch.FE_0328119_322482_P_SAVE_AFH_CERT_TEMP_TO_FIS:
            if testSwitch.AFH3_ENABLED:
               minTempInAFH3 = int(DriveAttributes.get('PRIMARY_TEMP', '25'))
            else:
               minTempInAFH3 = int(DriveAttributes.get('SECONDARY_TEMP', '25'))
            objMsg.printMsg("get AFH mini temperature %d" % minTempInAFH3)
      else:
         odPES.frm.readFramesFromDRIVE_SIM()
         odPES.frm.writeFramesToCM_SIM()                             # This is necessary so that there is a CM copy for findClearance to read from the CM SIM.

         if testSwitch.IN_DRIVE_AFH_COEFF_PER_HEAD_GENERATION_SUPPORT:
            minTempInAFH3 = odPES.frm.getMinimumTemp(1)
         else:
            if testSwitch.AFH3_ENABLED:
               minTempInAFH3 = odPES.frm.getMinimumTemp(3)
            else:
               minTempInAFH3 = odPES.frm.getMinimumTemp(2)

      #Temporary
      from Rim import objRimType
      if objRimType.IsLowCostSerialRiser():
         objMsg.printMsg("Bypass VER_RAMP for now")
         return

      from Temperature import CTemperature
      if testSwitch.FE_0251909_480505_NEW_TEMP_PROFILE_FOR_ROOM_TEMP_PRE2:
         CTemperature().waitForTempRamp(TP.minTCCTempDifferential,TP.TccAccMarginCold, minTempInAFH3)
      else:
         CTemperature().waitForTempRampDown(TP.minTCCTempDifferential,TP.TccAccMarginCold, minTempInAFH3)

      if testSwitch.FE_0163145_470833_P_NEPTUNE_SUPPORT_PROC_CTRL20_21:
         cellTemp = (ReportTemperature()/10.0)
         driveTemp = odPES.temp.retHDATemp()
         self.dut.updateCellTemp(cellTemp)
         self.dut.updateDriveTemp(driveTemp)
         objMsg.printMsg("PROC_CTRL20 (cell temp) =%s PROC_CTRL21 (drive temp) =%s" % (cellTemp, driveTemp))


#-------------------------------------------------------------------------------------------------------
class CTccReset(CState):
   """
      Description: Class that will check AFH2 data to decide whether reset to default TCC values or generate
      TCC base on AFH4 result
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      objMsg.printMsg("testSwitch.ENABLE_TCC_RESET_BY_HEAD_BEFORE_AFH4 = %d." % testSwitch.ENABLE_TCC_RESET_BY_HEAD_BEFORE_AFH4)

      if testSwitch.ENABLE_TCC_RESET_BY_HEAD_BEFORE_AFH4 == 1:
         objMsg.printMsg("ENABLE_TCC_RESET_BY_HEAD_BEFORE_AFH4 is on.")

         if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT == 1:
            from AFH_Screens_DH import CAFH_Screens
         else:
            from AFH_Screens_T135 import CAFH_Screens

         oAFH_Screens  = CAFH_Screens()
         oAFH_Screens.frm.readFramesFromCM_SIM()   # okay to read from the CM copy

         oAFH_Screens.frm.display_frames(2)

         # checks for common failure modes
         if len(oAFH_Screens.frm.dPesSim.DPES_FRAMES) < (self.dut.imaxHead * 4):
            ScrCmds.raiseException(11044, 'Insufficent Frames data decide TCC reset or not')

         state_list = []    # in case AFH3 is enable
         for frame in oAFH_Screens.frm.dPesSim.DPES_FRAMES:
            if ( not frame['stateIndex'] in state_list ):
               state_list.append(frame['stateIndex'])
         if len(state_list) < 2:
            ScrCmds.raiseException(11044, 'Insufficent Frames data decide TCC reset or not')

         first_stateIndex = state_list[len(state_list) - 2]
         second_stateIndex = state_list[len(state_list) - 1]
         if first_stateIndex != stateTableToAFH_internalStateNumberTranslation['AFH1']:
            ScrCmds.raiseException(11044, 'Data for AFH1 not found.')
         if second_stateIndex != stateTableToAFH_internalStateNumberTranslation['AFH2']:
            ScrCmds.raiseException(11044, 'Data for AFH2 not found.')

         # get AFH1 and AFH2 data writer heater write clr (if self.dut.isDriveDualHeater == 1 ?)
         for iHead in oAFH_Screens.headList:
            deltaWrtClr[iHead] = []
            for frame in oAFH_Screens.frm.dPesSim.DPES_FRAMES:
               iZone = int(frame['Zone'])
               if ( (frame['mode'] == AFH_MODE_TEST_135_INTERPOLATED_DATA) and (frame['stateIndex'] == first_stateIndex) and \
                    (frame['LGC_HD'] == iHead) and ( frame['Heater Element'] == heaterElementNameToFramesDict["WRITER_HEATER"] ) ):
                  dWrtClr1 = float(frame['wrtClr']) * angstromsScaler
               else:
                  continue

               if ( (frame['mode'] == AFH_MODE_TEST_135_INTERPOLATED_DATA) and (frame['stateIndex'] == second_stateIndex) and \
                    (frame['LGC_HD'] == iHead) and ( frame['Heater Element'] == heaterElementNameToFramesDict["WRITER_HEATER"] ) ):
                  dWrtClr2 = float(frame['wrtClr']) * angstromsScaler
               else:
                  continue

               deltaWrtCl[iHead].append(abs(dWrtClr1 - dWrtClr2))
               objMsg.printMsg("deltaWrtCl len %d for head %d." % (len(deltaWrtCl[iHead]),iHead))
               objMsg.printMsg("deltaWrtCl %d." % deltaWrtCl[iHead])
               objMsg.printMsg("deltaWrtCl_mean %s." % abs(mean(deltaWrtCl[iHead])))
               objMsg.printMsg("deltaWrtCl_mean_spec %d." % TP.TccResetSpec['DELTA_CLR_MEAN'])
               objMsg.printMsg("deltaWrtCl_stDev %d." % abs(stDev_standard(deltaWrtCl[iHead])))
               objMsg.printMsg("deltaWrtCl_stDev_spec %d." % TP.TccResetSpec['DELTA_CLR_STDEV'])

            if abs(mean(deltaWrtCl[iHead])) > TP.TccResetSpec['DELTA_CLR_MEAN'] or \
               abs(stDev_standard(deltaWrtCl[iHead])) > TP.TccResetSpec['DELTA_CLR_STDEV']:
               # reload the TCS (should be default TCS in RAP now. just in case)
               from RAP import ClassRAP
               objRAP = ClassRAP()
               if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT:
                  if not testSwitch.extern.FE_0157745_387179_AFH_TCS_WARP:
                     objRAP.SaveTCC_toRAP( iHead, TP.tcc_DH_dict_178 ['WRITER_HEATER']['TCS1'], TP.tcc_DH_dict_178["WRITER_HEATER"]['TCS2'], "WRITER_HEATER",TP.tcc_DH_values)
                     objRAP.SaveTCC_toRAP( iHead, TP.tcc_DH_dict_178 ['READER_HEATER']['TCS1'], TP.tcc_DH_dict_178["READER_HEATER"]['TCS2'], "READER_HEATER",TP.tcc_DH_values)
                  else:
                     objRAP.SaveTCC_toRAP( iHead, TP.tcc_DH_dict_178 ['WRITER_HEATER']['TCS1'], TP.tcc_DH_dict_178["WRITER_HEATER"]['TCS2'], "WRITER_HEATER",TP.tcc_DH_values,TP.TCS_WARP_ZONES.keys())
                     objRAP.SaveTCC_toRAP( iHead, TP.tcc_DH_dict_178 ['READER_HEATER']['TCS1'], TP.tcc_DH_dict_178["READER_HEATER"]['TCS2'], "READER_HEATER",TP.tcc_DH_values,TP.TCS_WARP_ZONES.keys())
               else:     # single heater drive
                  objRAP.SaveTCC_toRAP( iHead, TP.tccDict_178['TCS1']*254.0 , TP.tcc_DH_dict_178["WRITER_HEATER"]['TCS2'], "WRITER_HEATER",TP.tcc_DH_values)

               self.dut.TccResetHeadList.append(iHead)
               try:
                  self.dut.objData.update({'TccResetHeadList':self.dut.TccResetHeadList})
               except:
                  objMsg.printMsg("Fail to save TccResetHeadList to objdata")
      else:
         objMsg.printMsg("ENABLE_TCC_RESET_BY_HEAD_BEFORE_AFH4 is off.")


#-------------------------------------------------------------------------------------------------------
class CTccCalibration(CState):
   """
      Description: Class that will perform a 1 stop AFH Calibrations for TCC values
      Base: Based on st10 Tonka 2 implementation
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def saveThresholdToHap (self, threshold = 0x3C, UseAFHDbLog = 1):
       if UseAFHDbLog: 
          T135DETCRSettings = self.dut.dblData.Tables('P135_DETCR_OPTI_SETTINGS2').tableDataObj()
          objMsg.printMsg('P135_DETCR_OPTI_SETTINGS2=%s' %str(T135DETCRSettings))
       DetcrThresholdDict = {}
       T135RDDetcrThresholdDict = {}
       #DetcrWRThresholdDict = {}
       T135WRDetcrThresholdDict = {}

       if UseAFHDbLog: # get from AFH DETCR Settings result
          for row in T135DETCRSettings:
             if row['WPH'] == 'N':
                if int(row['HD_LGC_PSN']) not in T135RDDetcrThresholdDict.keys():
                   T135RDDetcrThresholdDict[int(row['HD_LGC_PSN'])] = {}
                #if int(row['DATA_ZONE']) not in T135RDDetcrThresholdDict[int(row['HD_LGC_PSN'])].keys(): 
                T135RDDetcrThresholdDict[int(row['HD_LGC_PSN'])][int(row['DATA_ZONE'])] = int(row['WORKING_THRL'])


          #for head in T135RDDetcrThresholdDict.keys(): #range(self.dut.imaxHead):
             #if head not in DetcrThresholdDict.keys():
                #DetcrRDThresholdDict[head] = [0xFF for zone in range(self.dut.numZones)]

          for row in T135DETCRSettings:
             if row['WPH'] == 'Y':
                if int(row['HD_LGC_PSN']) not in T135WRDetcrThresholdDict.keys():
                   T135WRDetcrThresholdDict[int(row['HD_LGC_PSN'])] = {}
                #if int(row['DATA_ZONE']) not in T135WRDetcrThresholdDict[int(row['HD_LGC_PSN'])].keys(): 
                T135WRDetcrThresholdDict[int(row['HD_LGC_PSN'])][int(row['DATA_ZONE'])] = int(row['WORKING_THRL'])
    
          for head in T135WRDetcrThresholdDict.keys(): #range(self.dut.imaxHead):
             #if head not in DetcrThresholdDict.keys():
                DetcrThresholdDict[head] = [0xFF for zone in range(self.dut.numZones)]
       else:
           for head in range(self.dut.imaxHead):
               DetcrThresholdDict[head] = [0xFF for zone in range(self.dut.numZones )]
               T135WRDetcrThresholdDict[head] = {}
               T135RDDetcrThresholdDict[head] = {}
               for zone in range(self.dut.numZones ):
                  T135WRDetcrThresholdDict[head][zone] = threshold
                  T135RDDetcrThresholdDict[head][zone] = threshold

       from FSO import CFSO
       objFSO = CFSO()
       #objFSO.St(TP.enableLiveSensor_11)
       objFSO.St(TP.disableTASensor_11)
       objFSO.saveSAPtoFLASH()
       if self.dut.heaterElementList:
           heaterElementList = self.dut.heaterElementList
       else:
           heaterElementList = [ "WRITER_HEATER",  "READER_HEATER" ]
       objMsg.printMsg('heaterelement=%s' %str(heaterElementList))
       for head in DetcrThresholdDict.keys():
          for heaterelement in heaterElementList:
          #for heaterelement in [0,1]:
             
             if UseAFHDbLog: # get from AFH DETCR Settings result
                if heaterelement == "READER_HEATER":
                   T135DetcrThresholdDict = T135RDDetcrThresholdDict[head]
                else: 
                   T135DetcrThresholdDict = T135WRDetcrThresholdDict[head]
                tunedZones = T135DetcrThresholdDict.keys()
                tunedZones.sort()
                key_index = 0
                for zone in range(self.dut.numZones):
                   if zone <= min(tunedZones):
                       DetcrThresholdDict[head][zone] = T135DetcrThresholdDict[tunedZones[0]]
                   elif zone >= max(tunedZones):
                       DetcrThresholdDict[head][zone] = T135DetcrThresholdDict[tunedZones[-1]]
                   else:
                      start_x = T135DetcrThresholdDict[ tunedZones[key_index]]
                      slope = float(T135DetcrThresholdDict[tunedZones[key_index + 1]] - T135DetcrThresholdDict[tunedZones[key_index]]) / (tunedZones[key_index+1]-  tunedZones[key_index])
                      DetcrThresholdDict[head][zone] = start_x + int(round(slope * (zone - tunedZones[key_index])))
                      if zone >= tunedZones[key_index + 1]:
                          key_index += 1
                objMsg.printMsg('LIVESensorThreshold=%s' %str(DetcrThresholdDict))
             else:                 
                if heaterelement == "READER_HEATER":
                   DetcrThresholdDict[head] = T135RDDetcrThresholdDict[head]
                else: 
                   DetcrThresholdDict[head] = T135WRDetcrThresholdDict[head]
             #if testSwitch.extern.FE_0251134_387179_RAP_ALLOCATE_FOR_LIVE_SENSOR_ON_HAP:
             t094param = TP.LiveSensor_prm_094.copy()
             DYNAMIC_THRESH = TP.LiveSensor_prm_094["DYNAMIC_THRESH"]
             DYNAMIC_THRESH = list(DYNAMIC_THRESH)
             if self.dut.HGA_SUPPLIER in ['RHO']:
                DYNAMIC_THRESH[0] = 0x28
             else:
                DYNAMIC_THRESH[0] = 0x23
             DYNAMIC_THRESH = tuple(DYNAMIC_THRESH)
             t094param["DYNAMIC_THRESH"] = DYNAMIC_THRESH

             LIVE_SENSOR_THRESHOLD = [0 for zone in range((self.dut.numZones / 2) + (self.dut.numZones % 2) )]
             if threshold == 0:
                for zone in range(self.dut.numZones):
                   if zone % 2 == 1:
                      LIVE_SENSOR_THRESHOLD[zone/2] += DetcrThresholdDict[head][zone]
                   else:
                      LIVE_SENSOR_THRESHOLD[zone/2] += (DetcrThresholdDict[head][zone] << 8)
             else:
                LIVE_SENSOR_THRESHOLD = [ (threshold | (threshold << 8)) for zone in range(((self.dut.numZones ) / 2) + ((self.dut.numZones ) % 2) )] #[0x2828 for zone in range(((self.dut.numZones ) / 2) + ((self.dut.numZones ) % 2) )]
                #t094param["THRESHOLD"] =  threshold # 0x28 
             t094param["LIVE_SENSOR_THRESHOLD"] = LIVE_SENSOR_THRESHOLD

             objMsg.printMsg('LIVESensorThreshold=%s' %str(LIVE_SENSOR_THRESHOLD))
             t094param["HEAD_RANGE"] = head | (head << 8)
             objMsg.printMsg('HEAD_RANGE=%s' %str(head | (head << 8)))
             if heaterelement == "READER_HEATER":
                t094param["CWORD3"] = 0x8000
             else:
                t094param["CWORD3"] = 0x2000
             objFSO.St(t094param)
             #TP.LiveSensor_prm_094.update({"CWORD3" : (0x4000,)})
             #objFSO.St(TP.LiveSensor_prm_094)
             #objFSO.St({'test_num':172, 'prm_name':'retrieve RAP tables','CWORD1':9,'timeout': 800})
       #objFSO.St(TP.enableLiveSensor_11)
       objFSO.St(TP.disableTASensor_11)
       objFSO.saveSAPtoFLASH()
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from AFH import CdPES, CAFH
      from AFH_mainLoop import CAFH_test135
      from Temperature import CTemperature

      oTemp = CTemperature()
      if testSwitch.FE_0148761_409401_P_CHECK_HDA_TEMP == 1:
         if self.params.get('chkTemp', 'N') == 'Y':
            attrName = self.dut.nextState+'_DELAY'
            self.dut.driveattr[attrName] = 0
            curTemp = oTemp.retHDATemp()
            if curTemp > 26:
               import time
               objMsg.printMsg("Current temperature more than 26.")
               objMsg.printMsg("Powering down for 15 min.")
               objPwrCtrl.powerOff()
               time.sleep(900) # poweroff delay for 15 min
               objPwrCtrl.powerOn(useESlip = 1)
               self.dut.driveattr[attrName] += 1
               curTemp = oTemp.retHDATemp()

      odPES  = CdPES(TP.masterHeatPrm_11, TP.defaultOCLIM)        # Instantiate dpes object.. don't allow default data
      cAFH = CAFH()

      odPES.frm.readFramesFromDRIVE_SIM()
      odPES.frm.writeFramesToCM_SIM()                             # This is necessary so that there is a CM copy for findClearance to read from the CM SIM.

      if self.dut.nextState in ['AFH4',  ]:
         if testSwitch.ENABLE_T175_ZAP_CONTROL:
            cAFH.St(TP.zapPrm_175_zapOff)
         else:
            cAFH.St(TP.setZapOffPrm_011)
            if not testSwitch.BF_0119055_231166_USE_SVO_CMD_ZAP_CTRL:
               cAFH.St({'test_num':178, 'prm_name':'Save SAP in RAM to FLASH', 'CWORD1':0x420})

      oTemp.getCellTemperature()

      odPES.setMasterHeat(TP.masterHeatPrm_11, setMHeatOn = 1)    # Enable master heat

      coefs = cAFH.getClrCoeff(TP.clearance_Coefficients, self.dut.PREAMP_TYPE, self.dut.AABType)
      odPES.lmt.maxDAC = (2**TP.dpreamp_number_bits_DAC.get(self.dut.PREAMP_TYPE,0)) - 1


      if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT == 1:
         odPES.getDHStatus( self.dut.PREAMP_TYPE, self.dut.AABType, TP.clearance_Coefficients )

      if testSwitch.FE_0280534_480505_DETCR_ON_OFF_BECAUSE_SERVO_DISABLE_DETCR_BY_DEFAULT:
         # needed due to M10P servo code, servo code disables DETCR by default so DETCR on/off commands need to be called before and after using DETCR
         cAFH.St(TP.setDetcrOnPrm_011)
         cAFH.St({'test_num':178, 'prm_name':'Save SAP in RAM to FLASH', 'CWORD1':0x420})

      self.odPES = None
      oAFH_test135 = CAFH_test135()
      oAFH_test135.findClearance_st135(TP.heatSearchParams)

      if testSwitch.FE_0280534_480505_DETCR_ON_OFF_BECAUSE_SERVO_DISABLE_DETCR_BY_DEFAULT:
         # needed due to M10P servo code, servo code disables DETCR by default so DETCR on/off commands need to be called before and after using DETCR
         cAFH.St(TP.setDetcrOffPrm_011)
         cAFH.St({'test_num':178, 'prm_name':'Save SAP in RAM to FLASH', 'CWORD1':0x420})

      if (testSwitch.FE_0121797_341036_AFH_USE_T109_FOR_TEST_135_TRACK_CLEANUP == 1):
         oAFH_test135.writeCustomerZeroesToTestedTracksUsingTest109()
      if self.dut.nextState in ['AFH4',  ]:
         if testSwitch.ENABLE_T175_ZAP_CONTROL:
            cAFH.St(TP.zapPrm_175_zapOn)
         else:
            cAFH.St(TP.setZapOnPrm_011)
            if not testSwitch.BF_0119055_231166_USE_SVO_CMD_ZAP_CTRL:
               cAFH.St({'test_num':178, 'prm_name':'Save SAP in RAM to FLASH', 'CWORD1':0x420})

         if testSwitch.extern.FE_0251134_387179_RAP_ALLOCATE_FOR_LIVE_SENSOR_ON_HAP:
            self.saveThresholdToHap ()

      self.oAFH_test135 = None


      certTemp = odPES.temp.retHDATemp(certTemp = 1)
      odPES = None
      if testSwitch.FE_AFH4_TO_USE_TWO_ZONES_TCC != 1:

         # TCS screen
         if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT == 1:
            from AFH_Screens_DH import CAFH_Screens
         else:
            from AFH_Screens_T135 import CAFH_Screens

         oAFH_Screens  = CAFH_Screens()
         oAFH_Screens.frm.readFramesFromCM_SIM()   # okay to read from the CM copy

         if testSwitch.FE_0139388_341036_AFH_DUAL_HEATER_V32_ABOVE == 1:
            if testSwitch.FE_0169232_341036_ENABLE_AFH_TGT_CLR_CANON_PARAMS == 1:
               from AFH_canonParams import *
               tcc_DH_values = getTCS_values()
            else:
               tcc_DH_values = TP.tcc_DH_values
            oAFH_Screens.getComputeSaveAndScreenTCS(tcc_DH_values, TP.tempSpecDict_178, TP.nTempCERT )
         else:
            oAFH_Screens.MeasureTCC(TP.tccDict_178, TP.tempSpecDict_178, TP.maskParams, TP.nTempCERT )

         oAFH_Screens = None   # allow GC

      self.dut.AFHCleanUp = 1
      self.dut.objData.update({'AFH_CLEANUP':self.dut.AFHCleanUp})

      if testSwitch.ENABLE_TCC_SCRN_IN_AFH4 and self.dut.nextState == 'AFH4':
         from AFH_SIM import CAFH_Frames
         OAFH_Frames= CAFH_Frames()
         OAFH_Frames.readFramesFromCM_SIM()
         from AFH_constants import *

         if testSwitch.CHENGAI:
            heaterElement = "READER_HEATER"   # reader heater only
            for iHead in range(0,self.dut.imaxHead):
               dRdCntDacMeasured_dict4 = [255,]*self.dut.numZones  ## store WrtCntDact measeured AFH4
               dRdClrMeasured_dict4 = [0.0,]*self.dut.numZones  ## store WrtCntDact measeured AFH4
               id_zn = 0
               od_zn = self.dut.numZones + 1
               for frame in OAFH_Frames.dPesSim.DPES_FRAMES:
                  ## collect AFH4 Measeured data
                  iZone = int(frame['Zone'])
                  if ( (frame['mode'] == AFH_MODE) and (frame['stateIndex'] == 4) and \
                       (frame['LGC_HD'] == iHead) and ( frame['Heater Element'] == heaterElementNameToFramesDict[heaterElement] ) ):
                     dRdCntDacMeasured_dict4[iZone] = int(frame['Heater Only Contact DAC'])
                     dRdClrMeasured_dict4[iZone] = float(frame['Read Clearance'])
                     if iZone < od_zn:
                         od_zn = iZone
                     if iZone > id_zn:
                         id_zn = iZone
               if (dRdCntDacMeasured_dict4[od_zn] < 44) and (dRdClrMeasured_dict4[od_zn] - dRdClrMeasured_dict4[id_zn] < -20.5):
                  ScrCmds.raiseException(48448, "OD rd contactDac is too low and OD_ID rd clr delta is too large.")
         else:
            tcc1_List_W = [0,]*self.dut.imaxHead
            spc_id = 2000
            RetrieveTcCoeff_prm = TP.Retrieve_TC_Coeff_Prm_172.copy()
            RetrieveTcCoeff_prm['spc_id'] = spc_id
            cAFH.St(RetrieveTcCoeff_prm)
            ##CProcess().St(RetrieveTcCoeff_prm)
            #P172_AFH_DH_TC_COEF_Tbl = self.dut.dblData.Tables('P172_AFH_DH_TC_COEF').chopDbLog('SPC_ID', 'match',str(RetrieveTcCoeff_prm['spc_id']))
            if not testSwitch.extern.FE_0157745_387179_AFH_TCS_WARP:
               P172_AFH_DH_TC_COEF_Tbl = self.dut.dblData.Tables('P172_AFH_DH_TC_COEF').chopDbLog('SPC_ID', 'match',str(RetrieveTcCoeff_prm['spc_id']))
            else:
               P172_AFH_DH_TC_COEF_Tbl = self.dut.dblData.Tables('P172_AFH_DH_TC_COEF_2').chopDbLog('SPC_ID', 'match',str(RetrieveTcCoeff_prm['spc_id']))
            for entry in P172_AFH_DH_TC_COEF_Tbl:
               if entry.get('ACTIVE_HEATER') == 'W':
                  tcc1_List_W[int(entry.get('HD_LGC_PSN'))] = float(entry.get('THERMAL_CLR_COEF1'))
            objMsg.printMsg("tcc1_List_W= %s." % (tcc1_List_W))

            heaterElement = "WRITER_HEATER"   # do W+H only mode.
            for iHead in range(0,self.dut.imaxHead):
               dWrtCntDac_dict = [255,]*self.dut.numZones   ## store WrtCntDact interpolated AFH2
               dWrtCntDac_dict4 = [255,]*self.dut.numZones  ## store WrtCntDact interpolated AFH4
               dWrtCntDacMeasured_dict = [255,]*self.dut.numZones  ## store WrtCntDact measeured AFH2
               dWrtCntDacMeasured_dict4 = [255,]*self.dut.numZones  ## store WrtCntDact measeured AFH4
               dDeltaWrtCntDac_dict = []  ## store delta WrtCntDact measeured AFH4 - AFH2
               for frame in OAFH_Frames.dPesSim.DPES_FRAMES:
                  iZone = int(frame['Zone'])

                  ## collect AFH2 Measeured data
                  if ( (frame['mode'] == AFH_MODE) and (frame['stateIndex'] == 2) and \
                       (frame['LGC_HD'] == iHead) and ( frame['Heater Element'] == heaterElementNameToFramesDict[heaterElement] ) ):
                     dWrtCntDacMeasured_dict[iZone] = int(frame['Write Heat Contact DAC'])

                  ## collect AFH2 Interpolated data
                  if ( (frame['mode'] == AFH_MODE_TEST_135_INTERPOLATED_DATA) and (frame['stateIndex'] == 2) and \
                       (frame['LGC_HD'] == iHead) and ( frame['Heater Element'] == heaterElementNameToFramesDict[heaterElement] ) ):
                     dWrtCntDac_dict[iZone] = int(frame['Write Heat Contact DAC'])

                  ## collect AFH4 Measeured data
                  if ( (frame['mode'] == AFH_MODE) and (frame['stateIndex'] == 4) and \
                       (frame['LGC_HD'] == iHead) and ( frame['Heater Element'] == heaterElementNameToFramesDict[heaterElement] ) ):
                     dWrtCntDacMeasured_dict4[iZone] = int(frame['Write Heat Contact DAC'])

                  ## collect AFH4 Interpolated data
                  if ( (frame['mode'] == AFH_MODE_TEST_135_INTERPOLATED_DATA) and (frame['stateIndex'] == 4) and \
                       (frame['LGC_HD'] == iHead) and ( frame['Heater Element'] == heaterElementNameToFramesDict[heaterElement] ) ):
                     dWrtCntDac_dict4[iZone] = int(frame['Write Heat Contact DAC'])

               objMsg.printMsg("dWrtCntDacMeasured_dict= %s." % (dWrtCntDacMeasured_dict))
               objMsg.printMsg("dWrtCntDac_dict= %s." % (dWrtCntDac_dict))
               objMsg.printMsg("dWrtCntDacMeasured_dict4= %s." % (dWrtCntDacMeasured_dict4))
               objMsg.printMsg("dWrtCntDac_dict4= %s." % (dWrtCntDac_dict4))
               objMsg.printMsg("head: %d, min(dWrtCntDac_dict)= %d, tcc1W = %s " % (iHead, min(dWrtCntDac_dict), tcc1_List_W[iHead]))

               ## data processing
               i = 0
               while (i < len(dWrtCntDacMeasured_dict) and i < len(dWrtCntDacMeasured_dict4)):
                  dDeltaWrtCntDac_dict.append(dWrtCntDacMeasured_dict4[i] - dWrtCntDacMeasured_dict[i])
                  i += 1
               objMsg.printMsg("dDeltaWrtCntDac_dict= %s." % (dDeltaWrtCntDac_dict))
               lowest_highest_pos = dDeltaWrtCntDac_dict.index(min(dDeltaWrtCntDac_dict))
               dDeltaWrtCntDac_dict.pop(lowest_highest_pos)
               lowest_highest_pos = dDeltaWrtCntDac_dict.index(max(dDeltaWrtCntDac_dict))
               dDeltaWrtCntDac_dict.pop(lowest_highest_pos)
               objMsg.printMsg("dDeltaWrtCntDac_dict (after take out max-min)= %s." % (dDeltaWrtCntDac_dict))

               ## Checking limit
               if mean(dDeltaWrtCntDac_dict) < -12 :
                  ScrCmds.raiseException(48448, "Delta between (measured) AFH4 and AFH2 is too Negative.")
                  objMsg.printMsg("head: %d, avg (dDeltaWrtCntDac_dict)= %d" % (iHead,mean(dDeltaWrtCntDac_dict)))

               if min(dWrtCntDac_dict) < 14 and tcc1_List_W[iHead] > 0.007:
                  ScrCmds.raiseException(48448, "TCC1 slope is Over Power.")
                  objMsg.printMsg("head: %d, min(dWrtCntDac_dict)= %d, tcc1W = %s " % (iHead,min(dWrtCntDac_dict),tcc1_List_W[iHead]))

               if abs(mean(dWrtCntDac_dict4) - mean(dWrtCntDac_dict)) > 14.5 and tcc1_List_W[iHead] < -0.62 :
                  ScrCmds.raiseException(48448, "TCC1 slope is under Power and Delta between AFH4 and AFH2 is too big.")
                  objMsg.printMsg("head: %d, abs(AFH4 - AFH2)= %d, tcc1W = %s " % (iHead,abs(mean(dWrtCntDac_dict4) - mean(dWrtCntDac_dict4)),tcc1_List_W[iHead]))


#-------------------------------------------------------------------------------------------------------
class CTrackCleanup(CState):
   """
      Description: Class that will perform a rewrite of tracks affected by various non-LBA based tests
       - Currently supports T135 (AFH), T250, T238 and T211 (VBAR-HMS)
       - Replaces CAFHCleanup
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      
      if self.dut.powerLossEvent or self.dut.raiseSerialformat \
      or (testSwitch.proqualCheck and self.dut.prevOperStatus["%s_TEST_DONE" % (self.dut.nextOper)] == "PASS"):
         objMsg.printMsg("skip TrackCleanup and raise to do serial format")
         ScrCmds.raiseException(0, 'skip TrackCleanup and raise to do serial format.')
      
      from serialScreen import sptDiagCmds

      self.oSerial = sptDiagCmds()
      sptCmds.enableDiags()
      self.oSerial.syncBaudRate()
      self.oSerial.setZeroPattern()
      objMsg.printMsg("Begin Track Cleanup")

      if self.oSerial.BGMS_EnabledInCode():
         self.oSerial.changeAMPS("BGMS_ENABLE", 0, mask = 1)
         self.oSerial.changeAMPS("BGMS_PRESCAN", 0, mask = 1)
         self.oSerial.changeAMPS("ReadAfterWriteControl", 0, mask = 1)

      # Clear the altlist
      self.oSerial.clearAltList()

      self.trackCleanupSerpentPad = getattr(TP, 'trackCleanupSerpentPad', 200)
      if testSwitch.BF_0209197_357260_P_TRACK_CLEANUP_HANDLE_MAX_TRACK:
         self.logTrkRanges = self.oSerial.getLogTrkRanges()

      # Build dictionary of track spans to cleanup
      trackRangeDict = self.buildTrackRangeDict()

      if testSwitch.virtualRun:
         trackRangeDict = {0: [[1846, 1872], [16394, 16420], [21944, 21987], [34402, 34428], [50408, 50434], [65963, 65989], [70389, 70430], [81413, 81439], [96481, 96507]], 1: [[1758, 1784], [15729, 15755], [21064, 21105], [32917, 32943], [48166, 48192], [63007, 63033], [67244, 67275], [77673, 77699], [91986, 92012]]}

      objMsg.printMsg('trackRangeDict: %s' %trackRangeDict)

      # Set Retries
      sptCmds.gotoLevel('2')
      parameters = [self.params.get('MODE', 0),self.params.get('RD_RETRIES', ''),self.params.get('WR_RETRIES', ''),self.params.get('T_LEVEL', ''),self.params.get('OPTIONS', '')]
      for param in range(len(parameters)):
         if parameters[param] != '':
            parameters[param] = '%x' %parameters[param]
      sptCmds.sendDiagCmd('Y%s,%s,%s,%s,%s' %(parameters[0],parameters[1],parameters[2],parameters[3],parameters[4])) # Enable normal retries for DERP

      if testSwitch.FE_0184418_357260_P_USE_TRACK_WRITES_FOR_CLEANUP:   # Perform track writes for cleanup
         if testSwitch.FE_0187241_357260_P_USE_BAND_WRITES_FOR_CLEANUP:
            ScrCmds.raiseException(11044, 'Script Exception - Must select Track or Band cleanup - Not Both')
         self.writeTrackRanges(trackRangeDict)
      elif testSwitch.FE_0187241_357260_P_USE_BAND_WRITES_FOR_CLEANUP:  # Perform Band writes for SMR cleanup  TODO: Add switch
         self.writeBandRanges(trackRangeDict)
      else:                                                             # Default cleanup uses LBA based writes
         # Build a list of LBA spans to cleanup
         rwRanges = self.buildLBASpans(trackRangeDict)

         # Write LBA ranges identified
         self.writeLBARanges(rwRanges)

      self.oSerial.resetAMPs()
      sptCmds.enableESLIP()
      self.dut.AFHCleanUp = 0
      self.dut.objData.update({'AFH_CLEANUP':self.dut.AFHCleanUp})

   #-------------------------------------------------------------------------------------------------------
   def writeLBARanges(self, rwRanges):
      printResult = False
      loopSleepTime = 0.5
      timeout = 2000             # LBA range could be quite large

      if testSwitch.virtualRun:
         data = """Mantaray.SATA.BANSHEEST.OEM.9kServo_RAP17.NonQNR
Product FamilyId: 3A, MemberId: 01
HDA SN: 9XK002AX, RPM: 7202, Wedges: 1A0, Heads: A, OrigHeads: A, Lbas: 1A955672, PreampType: 01 69
PCBA SN: 0000S002XHTS, Controller: BANSHEEST_1_0(FFFF)(FF-FF-FF-FF, Channel: Unknown, PowerAsic: MCKINLEY DESKTOP LITE Rev 14, BufferBytes: 4000000
Package Version: MR713C.SDP1.00221078.7L00.26, Package P/N: ---------, Package Global ID: 00379676,
Package Build Date: 11/10/2009, Package Build Time: 13:48:26, Package CFW Version: MR71.SDP1.00221078.7L00,
Package SFW1 Version: ----, Package SFW2 Version: ----, Package SFW3 Version: ----, Package SFW4 Version: ----
Controller FW Rev: 11101348, CustomerRel: ZZ7L, Changelist: 00221078, ProdType: MR71.SDP1, Date: 11/10/2009, Time: 134826, UserId: 00357094
Servo FW Rev: C326
RAP FW Implementation Key: 11, Format Rev: 0202, Contents Rev: 8C 05 05 00
Features:
- Quadradic Equation AFH enabled
- VBAR with adjustable zone boundaries enabled
- Volume Based Sparing enabled
- IOEDC enabled
- IOECC enabled
- DERP Read Retries enabled
- LTTC-UDR2 compiled off """
      else:
         data=sptCmds.sendDiagCmd(CTRL_L,altPattern='PreampType:',printResult=True)

      import re
      m = re.search('Lbas:', data)
      lbas = data[m.end():].split(',')[0]
      lbas = int(lbas,16)

      sptCmds.gotoLevel('A')

      for startLBA, endLBA in rwRanges:
         timeout += 1.5e-5 * (endLBA - startLBA)

         if startLBA > lbas-1:
            objMsg.printMsg("startLBA > max user lba- skipping range")
            continue
         elif endLBA > lbas-1:
            objMsg.printMsg("endLBA > max user lba - truncating range to %d" % (lbas-1,))
            endLBA = lbas-1
         for retry in range(self.params.get('RETRY_COUNT', 0)+1):
            try:
               self.oSerial.rw_LBAs(startLBA = startLBA, endLBA = endLBA, mode = 'W', timeout = timeout, printResult = printResult, loopSleepTime = loopSleepTime)
               break
            except:
               pass
         else:
            raise

         if testSwitch.GA_0149146_357260_LBA_READS_IN_AFH_CLEANUP:
            objMsg.printMsg("Read-Verifiying (LBAs: %X - %X)" % (startLBA, endLBA))
            self.oSerial.rw_LBAs(startLBA = startLBA, endLBA = endLBA, mode = 'R', timeout = timeout, printResult = printResult, loopSleepTime = loopSleepTime)

   #-------------------------------------------------------------------------------------------------------
   def writeTrackRanges(self, trackRangeDict):
      printResult = 0
      if DEBUG > 2: printResult = DEBUG
      timeout = 2000

      numCyls, zones = self.oSerial.getZoneInfo(printResult = printResult)
      if DEBUG > 2:
         objMsg.printMsg("numCyls: %s, zones: %s" % (numCyls, zones))

      sptCmds.gotoLevel('2')

      for head in trackRangeDict:
         for startCyl, endCyl in trackRangeDict[head]:
            ### To do: add a chk if both startcyl & endcyl return invalid FirstUsrLBA, if so skip this range. ####
            if startCyl > numCyls[head]-1:
               objMsg.printMsg("Range %s to %s of head: %s is invalid!!" %(startCyl, endCyl, head))
               #startCyl = numCyls[head]
               continue
            if endCyl >= numCyls[head]:
               endCyl = numCyls[head]-1

            if testSwitch.FE_SGP_81592_RETRY_DURING_TRACK_CLEANUP_4_CHS_MODE:
               WRT_retry = TP.trackCleanupRetryCnt
               while 1:
                  try:
                     objMsg.printMsg("Track Cleanup - writing tracks: %s to %s, head: %s" %(startCyl, endCyl, head))
                     self.oSerial.rw_CHSTrackRange('W', startCyl, endCyl, head, printResult = printResult, DiagErrorsToIgnore = ['00003010'])


                     break     # exit if no error reported
                  except:
                     if WRT_retry > 0:
                        WRT_retry -= 1
                        objMsg.printMsg("WRT ERROR REPORTED! Retry %d on: %s to %s, head: %s" %(WRT_retry, startCyl, endCyl, head))
                     else: raise

            else:
               objMsg.printMsg("Track Cleanup - writing tracks: %s to %s, head: %s" %(startCyl, endCyl, head))
               self.oSerial.rw_CHSTrackRange('W', startCyl, endCyl, head, printResult = printResult, DiagErrorsToIgnore = ['00003010'])

            if testSwitch.SGP_81592_CHS_READS_IN_AFH_CLEANUP:
               if testSwitch.FE_SGP_81592_RETRY_DURING_TRACK_CLEANUP_4_CHS_MODE:
                  RD_retry = TP.trackCleanupRetryCnt
                  while 1:
                     try:
                        objMsg.printMsg("Read-Verifiying ( Head: %s, Cyls: %s - %s)" % (head, startCyl, endCyl))
                        self.oSerial.rw_CHSTrackRange('R', startCyl, endCyl, head, printResult = printResult, DiagErrorsToIgnore = ['00003010'])
                        break
                     except:
                        if RD_retry > 0:
                           RD_retry -= 1
                           objMsg.printMsg("RD ERROR REPORTED! Re-write (%d) tracks %s to %s, head %s b4 re-read." %(RD_retry, startCyl, endCyl, head))
                           self.oSerial.rw_CHSTrackRange('W', startCyl, endCyl, head, printResult = printResult, DiagErrorsToIgnore = ['00003010'])
                        else: raise

               else:
                  objMsg.printMsg("Read-Verifiying ( Head: %s, Cyls: %s - %s)" % (head, startCyl, endCyl))
                  self.oSerial.rw_CHSTrackRange('R', startCyl, endCyl, head, printResult = printResult, DiagErrorsToIgnore = ['00003010'])
   
   #-------------------------------------------------------------------------------------------------------
   def sortBandRange(self, startBand, endBand):
      if startBand > endBand:
         return ( (endBand, startBand) )
      return ( (startBand, endBand) )
   
   #-------------------------------------------------------------------------------------------------------
   def writeBandRanges(self, trackRangeDict):
      printResult = DEBUG > 0
      timeout = 2000

      if testSwitch.FE_0194980_357260_P_LIMIT_SMR_TRACK_CLEANUP_TO_VALID_BANDS:
         #minLBA, maxLBA = self.oSerial.getLBARange()
         #maxBand = self.oSerial.getBandInfo(maxLBA, 0, printResult = printResult, mode = 'lba')['BandID']
         minLBID, maxLBID, FirstMCZ = self.oSerial.getBANDRange(printResult=False)
         maxBand = maxLBID
         if DEBUG > 0:
            objMsg.printMsg("Track Cleanup - maxBand = %s" %maxBand)

      if testSwitch.FE_0258639_305538_CONSOLIDATE_BANDS_BEFORE_CLEANUP:
         bandRanges = []
      for head in trackRangeDict:
         for startCyl, endCyl in trackRangeDict[head]:
            startZone = self.oSerial.getTrackInfo(startCyl, head, printResult = printResult, mode = 'logical')['ZONE']
            endZone = self.oSerial.getTrackInfo(endCyl, head, printResult = printResult, mode = 'logical')['ZONE']
            if testSwitch.virtualRun:
               endZone = 3
            #workaround until F3 fix the display bug where cylinder in MC zone returns physical zn number instead of logical zn number
            if ((startZone+endZone) == FirstMCZ) and (startZone == FirstMCZ-1): 
               objMsg.printMsg("Drv return logical MCZn as %s, reset to %s" % (endZone,FirstMCZ))
               endZone = FirstMCZ
            #end of workaround

            if DEBUG > 0:
               objMsg.printMsg("Track Cleanup - startCyl = %s, endCyl = %s" %(startCyl, endCyl))
               objMsg.printMsg("Track Cleanup - startZone = %s, endZone = %s" %(startZone, endZone))

            if not testSwitch.FE_0258639_305538_CONSOLIDATE_BANDS_BEFORE_CLEANUP:
               bandRanges = []
            if startZone == endZone:
               bandRanges.append( self.sortBandRange(self.oSerial.getBandInfo(startCyl, head, printResult = printResult)['BandID'], self.oSerial.getBandInfo(endCyl, head, printResult = printResult)['BandID']) )
            else:
               # Band Range for first Zone:
               bandRanges.append( self.sortBandRange(self.oSerial.getBandInfo(startCyl, head, printResult = printResult)['BandID'], self.oSerial.getValidBand(startZone, head, mode = 'last', printResult = printResult)) )
               if DEBUG > 0: objMsg.printMsg('bandRanges1: %s' %bandRanges)
               # Band Ranges for middle zones:
               for zone in range(startZone+1, endZone):
                  bandRanges.append( self.sortBandRange(self.oSerial.getValidBand(zone, head, mode = 'first', printResult = printResult), self.oSerial.getValidBand(zone, head, mode = 'last', printResult = printResult)) )
               if DEBUG > 0: objMsg.printMsg('bandRanges2: %s' %bandRanges)
               # Band Range for last Zone:
               bandRanges.append( self.sortBandRange(self.oSerial.getValidBand(endZone, head, mode = 'first', printResult = printResult), self.oSerial.getBandInfo(endCyl, head, printResult = printResult)['BandID']) )
               if DEBUG > 0: objMsg.printMsg('bandRanges3: %s' %bandRanges)

            if DEBUG > 0: objMsg.printMsg('Final bandRanges: %s' %bandRanges)

            if testSwitch.FE_0258639_305538_CONSOLIDATE_BANDS_BEFORE_CLEANUP:
               continue # only do cleanup after consolidated all heads

            if testSwitch.FE_0194980_357260_P_LIMIT_SMR_TRACK_CLEANUP_TO_VALID_BANDS:
               for startBand, endBand in bandRanges:
                  # check for wrap around scenario where
                  if (min(startBand, endBand) <= maxBand):
                     if startBand > maxBand:
                        startBand = maxBand
                     if endBand > maxBand:
                        endBand = maxBand
                     ############# perform band w/r here
                     if testSwitch.FE_0254235_081592_ADDING_RETRY_WITH_PWRCYC_IN_SMR_TRACK_CLEANUP:
                        WRTRetryCnt = TP.trackCleanupRetryCnt
                        while 1:
                           try:                        
                              objMsg.printMsg("Track Cleanup - writing bands: %s to %s, head: %s" %(startBand, endBand, head))
                              self.oSerial.rw_BandRange('W', min(startBand, endBand), abs(startBand-endBand)+1, printResult = printResult, DiagErrorsToIgnore = ['00003010', '00003000', '00003021'])
                              break    # exit if no error reported
                           except:
                              if WRTRetryCnt > 0:
                                 objMsg.printMsg("WRT ERROR REPORTED! Retry %d on bands %s to %s, head: %s" %(WRTRetryCnt, startBand, endBand, head))
                                 WRTRetryCnt -= 1
                              else:
                                 objPwrCtrl.powerCycle()
                                 raise
                           
                        RDRetryCnt = TP.trackCleanupRetryCnt
                        while 1:
                           try:                        
                              objMsg.printMsg("Track Cleanup - Reading bands: %s to %s, head: %s" %(startBand, endBand, head))
                              self.oSerial.rw_BandRange('R', min(startBand, endBand), abs(startBand-endBand)+1, printResult = printResult, DiagErrorsToIgnore = ['00003010', '00003000', '00003021'])
                              break    # exit if no error reported
                           except:
                              if RDRetryCnt > 0:
                                 objMsg.printMsg("RD ERROR REPORTED! Retry %d on bands %s to %s, head: %s" %(RDRetryCnt, startBand, endBand, head))
                                 RDRetryCnt -= 1
                              else:
                                 objPwrCtrl.powerCycle()
                                 raise

                     else:
                        objMsg.printMsg("Track Cleanup - writing bands: %s to %s, head: %s" %(startBand, endBand, head))
                        self.oSerial.writeBandRange(min(startBand, endBand), abs(startBand-endBand)+1, printResult = printResult, DiagErrorsToIgnore = ['00003010', '00003000', '00003021'])
                  else:
                     objMsg.printMsg("Track Cleanup - skipping bands: %s to %s, head: %s" %(startBand, endBand, head))
            else:
               for startBand, endBand in bandRanges:
                  objMsg.printMsg("Track Cleanup - writing bands: %s to %s, head: %s" %(startBand, endBand, head))
                  self.oSerial.writeBandRange(min(startBand, endBand), abs(startBand-endBand)+1, printResult = printResult, DiagErrorsToIgnore = ['00003010', '00003021'])

      if testSwitch.FE_0258639_305538_CONSOLIDATE_BANDS_BEFORE_CLEANUP:
         # consolidate band ranges
         if DEBUG > 0: objMsg.printMsg('bandRanges= %s' % str(bandRanges))
         bandRanges.sort()
         newbandRanges = []
         newEndBand    = 0
         for idx in range(len(bandRanges)):
            curStartBand = min(bandRanges[idx])
            curEndBand = max(bandRanges[idx])
            if idx == 0: # first band range, so init newStartBand, continue to next band
               newStartBand = curStartBand
            else:
               if newEndBand < curStartBand-1: # not contiguous, append previous band range
                  newbandRanges.append(( newStartBand, newEndBand ))
                  newStartBand = curStartBand
            # update newEndBand
            newEndBand = max(newEndBand, curEndBand)
            # if at last band range, then append this last band range
            if idx == len(bandRanges)-1:
               newbandRanges.append(( newStartBand, newEndBand ))

         if DEBUG > 0: objMsg.printMsg('newbandRanges= %s' % str(newbandRanges))
         if testSwitch.FE_0194980_357260_P_LIMIT_SMR_TRACK_CLEANUP_TO_VALID_BANDS:
            for startBand, endBand in newbandRanges:
               # check for wrap around scenario where
               if (min(startBand, endBand) <= maxBand):
                  if startBand > maxBand:
                     startBand = maxBand
                  if endBand > maxBand:
                     endBand = maxBand
                  ############# perform band w/r here
                  if testSwitch.FE_0254235_081592_ADDING_RETRY_WITH_PWRCYC_IN_SMR_TRACK_CLEANUP:
                     WRTRetryCnt = TP.trackCleanupRetryCnt
                     while 1:
                        try:                        
                           objMsg.printMsg("Track Cleanup - writing bands: %s to %s.." % (startBand, endBand))
                           self.oSerial.rw_BandRange('W', min(startBand, endBand), abs(startBand-endBand)+1, printResult = printResult, DiagErrorsToIgnore = ['00003010', '00003000', '00003021'])
                           break    # exit if no error reported
                        except:
                           if WRTRetryCnt > 0:
                              objMsg.printMsg("WRT ERROR REPORTED! Retry %d on bands %s to %s" %(WRTRetryCnt, startBand, endBand))
                              WRTRetryCnt -= 1
                           else:
                              objPwrCtrl.powerCycle()
                              raise
                        
                     RDRetryCnt = TP.trackCleanupRetryCnt
                     while 1:
                        try:                        
                           objMsg.printMsg("Track Cleanup - Reading bands: %s to %s.." % (startBand, endBand))
                           self.oSerial.rw_BandRange('R', min(startBand, endBand), abs(startBand-endBand)+1, printResult = printResult, DiagErrorsToIgnore = ['00003010', '00003000', '00003021'])
                           break    # exit if no error reported
                        except:
                           if RDRetryCnt > 0:
                              objMsg.printMsg("RD ERROR REPORTED! Retry %d on bands %s to %s" %(RDRetryCnt, startBand, endBand))
                              RDRetryCnt -= 1
                           else:
                              objPwrCtrl.powerCycle()
                              raise

                  else:
                     objMsg.printMsg("Track Cleanup - writing bands: %s to %s.." % (startBand, endBand))
                     self.oSerial.writeBandRange(min(startBand, endBand), abs(startBand-endBand)+1, printResult = printResult, DiagErrorsToIgnore = ['00003010', '00003000', '00003021'])
               else:
                  objMsg.printMsg("Track Cleanup - skipping bands: %s to %s" %(startBand, endBand))
         else:
            for startBand, endBand in newbandRanges:
               objMsg.printMsg("Track Cleanup - writing bands: %s to %s ..." %(startBand, endBand))
               self.oSerial.writeBandRange(min(startBand, endBand), abs(startBand-endBand)+1, printResult = printResult, DiagErrorsToIgnore = ['00003010', '00003021'])


   #-------------------------------------------------------------------------------------------------------
   def buildLBASpans(self, trackRangeDict):
      from ContinuousSet import cSet
      rwSpans = []
      for head in trackRangeDict:
         for minTrack, maxTrack in trackRangeDict[head]:

            try:
               startLBA, endLBA, minTrack = self.getTrackLBARangeSearch(minTrack, head, direction = -1, allowEndOfPackNegSearch = False, maxLoopLimit = maxTrack - minTrack)
            except (InvalidTrackException, EndOfPackException):
               objMsg.printMsg("Range is outside of user LBA space... skipping range.")
               continue

            try:
               sLBA, eLBA, maxTrack = self.getTrackLBARangeSearch(maxTrack, head, direction = 1, allowEndOfPackNegSearch = True, maxLoopLimit = maxTrack - minTrack)
               if testSwitch.virtualRun:
                  eLBA += 0xFFFFF
            except (EndOfPackException, InvalidTrackException):
               try:
                  objMsg.printMsg("Invalid AFH Span end range. Retrying closer to AFH Track")
                  sLBA, eLBA, maxTrack = self.getTrackLBARangeSearch(maxTrack, head, direction = -1, allowEndOfPackNegSearch = True, maxLoopLimit = self.trackCleanupSerpentPad)
               except (InvalidTrackException, EndOfPackException):
                  objMsg.printMsg("Critical Error when finding end range! Locating last valid track.")
                  maxTrack = self.findLastValidTrack(minTrack, head, direction = 1)
                  sLBA, eLBA, maxTrack = self.getTrackLBARangeSearch(maxTrack, head, direction = -1, allowEndOfPackNegSearch = False, maxLoopLimit = self.trackCleanupSerpentPad)

            span = cSet(min([sLBA, startLBA]), max([eLBA, endLBA]))
            rwSpans = self.addSpanToSpans(span, rwSpans)

      # Regenerate the LBA list as ranges so we don't carry around the huge spans
      rwRanges = [[min(i), max(i)] for i in rwSpans]
      objMsg.printMsg('rwRanges: %s' %rwRanges)

      #Sort the spans... prefered
      rwRanges.sort(key = lambda i: list(i)[0])
      objMsg.printMsg("Addressing # spans: %d" % (len(rwRanges),))

      return rwRanges

   #-------------------------------------------------------------------------------------------------------
   def displayCurrentTrkSpanDict(self, trackSpansDict):
      itrackRangeDict = {}
      itrackSpansDict = self.emptyDict()
      itrackSpansDict = trackSpansDict
      for head in itrackSpansDict:
         itrackRangeDict[head] = [[min(i), max(i)] for i in itrackSpansDict[head]]
         if DEBUG > 0: objMsg.printMsg('hd: %d current trackRangeDict: %s' % (head,itrackRangeDict[head]))

   #-------------------------------------------------------------------------------------------------------
   def buildTrackRangeDict(self):
      trackPadScalar         = getattr(TP, 'trackPadMultiplier',     1.2)
      trackCleanupAFHPad     = int((getattr(TP, 'trackCleanupAFHPad',     100) + self.trackCleanupSerpentPad) * trackPadScalar)
      trackCleanupT211Pad    = int((getattr(TP, 'trackCleanupT211Pad',    10) + self.trackCleanupSerpentPad) * trackPadScalar)
      trackCleanupT238Pad    = int((getattr(TP, 'trackCleanupT238Pad',    10) + self.trackCleanupSerpentPad) * trackPadScalar)
      trackCleanupT234Pad    = int((getattr(TP, 'trackCleanupT234Pad',    150) + self.trackCleanupSerpentPad) * trackPadScalar)
      trackCleanupT250Pad    = int((getattr(TP, 'trackCleanupT250Pad',    5) + self.trackCleanupSerpentPad) * trackPadScalar)
      trackCleanupT61Pad     = int((getattr(TP, 'trackCleanupT61Pad',     10) + self.trackCleanupSerpentPad) * trackPadScalar)
      trackCleanupT190Pad    = int((getattr(TP, 'trackCleanupT190Pad',     10) + self.trackCleanupSerpentPad) * trackPadScalar)
      if testSwitch.FE_0258915_348429_COMMON_TWO_TEMP_CERT : 
         trackCleanupT199Pad    = int((getattr(TP, 'trackCleanupT199Pad',     10) + self.trackCleanupSerpentPad) * trackPadScalar)
      trackCleanupT195Pad    = int((getattr(TP, 'trackCleanupT195Pad',     10) + self.trackCleanupSerpentPad) * trackPadScalar)
      trackCleanupNCTCPad    = int((getattr(TP, 'trackCleanupNCTCPad',     50) + self.trackCleanupSerpentPad) * trackPadScalar)

      trackSpansDict = self.emptyDict()
      if DEBUG > 0:
         objMsg.printMsg("trackCleanupAFHPad = %d, trackCleanupT211Pad = %d, trackCleanupT250Pad = %d, trackCleanupT61Pad = %d," \
                        % (trackCleanupAFHPad, trackCleanupT211Pad, trackCleanupT250Pad, trackCleanupT61Pad))
         objMsg.printMsg("trackCleanupT190Pad = %d, trackCleanupNCTCPad = %d, trackCleanupT195Pad = %d," \
                        % (trackCleanupT190Pad, trackCleanupNCTCPad, trackCleanupT195Pad))
      # Build a list of affected tracks (without duplicates)
      if not (testSwitch.FE_0121797_341036_AFH_USE_T109_FOR_TEST_135_TRACK_CLEANUP or self.params.get('CLEAN_ONLY_250', False)):
         try:
            if testSwitch.virtualRun:
               testTracksDict = {0: [1492, 33953, 69573, 96672, 128973, 162142, 195421, 231916], 1: [1402, 32014, 65800, 91597, 122400, 154052, 185595, 219854]}
            else:
               testTracksDict = self.dut.objData.retrieve('LogTest35_Tracks')
            objMsg.printMsg("LogTest35_Tracks: %s" %testTracksDict)
            trackSpansDict, testTracksDict = self.addTracksToSpans(trackCleanupAFHPad, testTracksDict, trackSpansDict)

            objMsg.printMsg('AFH4 logical testTracksDict: %s' %testTracksDict)
            self.displayCurrentTrkSpanDict(trackSpansDict)
         except:
            objMsg.printMsg("Warning -- Skipping clean up of TccCal test tracks - no table data found")
            testTracksDict = {}


      ###===========================================================
      # Append list with Test 250 tracks if available
      ###===========================================================
      try:           # Append list with Test 250 tracks if available
         T250BERlog = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').tableDataObj()
         objMsg.printMsg('Appending cleanup track list with T250 tracks')
         testTracksDict = self.emptyDict()
         if testSwitch.virtualRun:
            testTracksDict = {0: [2960, 12494, 19682, 29013, 38711, 47000, 57419, 66449, 72555, 78600, 85610, 92437, 100764, 108530, 116290, 123666, 134111, 141898, 150522, 158478, 165664, 171334, 178533, 185555, 192417, 198307, 206752, 213077, 221177, 228745, 234959], \
                              1: [2781, 11743, 18534, 27349, 36509, 44376, 54266, 62836, 68630, 74396, 81083, 87560, 95500, 102906, 110306, 117339, 127300, 134726, 142972, 150559, 157411, 162791, 169621, 176283, 182760, 188319, 196250, 202222, 209831, 216905, 222684]}
         else:
            for item in T250BERlog:
               testTracksDict[int(item['HD_LGC_PSN'])].append(int(int(item['START_TRK_NUM'])+(TP.prm_quickSER_250_TCC_2['NUM_TRACKS_PER_ZONE']/2)))
         objMsg.printMsg("T250 tracks to add: %s" %testTracksDict)
         trackSpansDict, testTracksDict = self.addTracksToSpans(trackCleanupT250Pad+(TP.prm_quickSER_250_TCC_2['NUM_TRACKS_PER_ZONE']/2)+1, testTracksDict, trackSpansDict)

         objMsg.printMsg('T250 logical testTracksDict: %s' %testTracksDict)
         self.displayCurrentTrkSpanDict(trackSpansDict)
      except:        # Unable to recover T250 data, go on without
         objMsg.printMsg('Unable to recover P250_ERROR_RATE_BY_ZONE table - skipping T250 cleanup')

      ###===========================================================
      # Append list with Test 250 Segmented BER tracks if available
      ###===========================================================
      try:           # Append list with Test 250 tracks if available
         T250SEGBERlog = self.dut.dblData.Tables('P250_SEGMENT_BER_SUM').tableDataObj()
         objMsg.printMsg('Appending cleanup track list with T250 SEG BER tracks')
         testTracksDict = self.emptyDict()
         if testSwitch.virtualRun:
            testTracksDict = {0: [2960, 12494, 19682, 29013, 38711, 47000, 57419, 66449, 72555, 78600, 85610, 92437, 100764, 108530, 116290, 123666, 134111, 141898, 150522, 158478, 165664, 171334, 178533, 185555, 192417, 198307, 206752, 213077, 221177, 228745, 234959], \
                              1: [2781, 11743, 18534, 27349, 36509, 44376, 54266, 62836, 68630, 74396, 81083, 87560, 95500, 102906, 110306, 117339, 127300, 134726, 142972, 150559, 157411, 162791, 169621, 176283, 182760, 188319, 196250, 202222, 209831, 216905, 222684]}
         else:
            for item in T250SEGBERlog:
               testTracksDict[int(item['HD_PHYS_PSN'])].append(int(int(item['TRK_NUM'])-(TP.SEG_BER_NUM_TRACKS_PER_ZONE/2)))
         objMsg.printMsg("T250 SEG BER tracks to add: %s" %testTracksDict)
         trackSpansDict, testTracksDict = self.addTracksToSpans(trackCleanupT250Pad+(TP.prm_quickSER_250_TCC_2['NUM_TRACKS_PER_ZONE']/2)+1, testTracksDict, trackSpansDict)

         objMsg.printMsg('T250 SEG BER logical testTracksDict: %s' %testTracksDict)
         self.displayCurrentTrkSpanDict(trackSpansDict)
      except:        # Unable to recover T250 data, go on without
         objMsg.printMsg('Unable to recover P250_SEGMENT_BER_SUM table - skipping T250 SEG BER cleanup')


      ###===========================================================
      # Append list with Test 238 tracks if available
      ###===========================================================
      try:           # Append list with Test 238 tracks if available
         T238Joglog = self.dut.dblData.Tables('P238_MICROJOG_CAL').tableDataObj()
         objMsg.printMsg('Appending cleanup track list with T238 tracks')
         param = TP.base_PHAST_CQM_JOG_COLD_238
         # increment * retries + right sided margin... this will be excessive for butterfly retries < target track but only by 1/2 rights sided margin... so 3 tracks by default
         jogTrackSingleSidedMargin = ( param.get('RETRY_INCR', 10) * param.get('RETRIES', 20) ) + param['NUM_ADJ_ERASE'] + 1 + ( param.get('INCREMENT', 4) * param.get('NUM_SAMPLES',  2) )

         testTracksDict = self.emptyDict()
         for item in T238Joglog:
            if testSwitch.BF_0184722_357260_TRACK_CLEANUP_USE_ONLY_LOG_HD:
               testTracksDict[int(item['HD_LGC_PSN'])].append(int(item['TRK_NUM']))
            else:
               testTracksDict[int(item['HD_PHYS_PSN'])].append(int(item['TRK_NUM']))
         objMsg.printMsg("T238 tracks to add: %s" %testTracksDict)
         trackSpansDict, testTracksDict = self.addTracksToSpans(max(trackCleanupT238Pad,jogTrackSingleSidedMargin), testTracksDict, trackSpansDict)

         objMsg.printMsg('T238 logical testTracksDict: %s' %testTracksDict)
         self.displayCurrentTrkSpanDict(trackSpansDict)

      except:        # Unable to recover T238 data, go on without
         objMsg.printMsg('Unable to recover P238_MICROJOG_CAL table - skipping T238 cleanup')
      ###===========================================================
      # Append list with Test 211 (VBAR HMS) tracks if available
      ###===========================================================         
           
      try:            # Append list with Test 211 (VBAR HMS) fail tracks if available
         T211HMSlog_FAIL = self.dut.dblData.Tables('P000_DRIVE_OP_FAILURE').tableDataObj()
         objMsg.printMsg('Appending cleanup track list with T211 HMS failed tracks')
         testTracksDict = self.emptyDict()
         for item in T211HMSlog_FAIL:
            if item['OPERATION'] == 'WRITE':
                testTracksDict[int(item['HD_PHYS_PSN'])].append(int(item['TRK_NUM']))
         objMsg.printMsg("T211 fail tracks to add: %s" %testTracksDict)
         trackSpansDict, testTracksDict = self.addTracksToSpans(trackCleanupT211failPad, testTracksDict, trackSpansDict)

         objMsg.printMsg('T211 HMS logical fail testTracksDict: %s' %testTracksDict)
         self.displayCurrentTrkSpanDict(trackSpansDict)
      except:        # Unable to recover T211 data, go on without
         objMsg.printMsg('Unable to recover P000_DRIVE_OP_FAILURE table - Continue to passed T211 cleanup')
      ###===========================================================
      # Append list with Test 211 (VBAR HMS) tracks if available
      ###===========================================================
      try:           # Append list with Test 211 (VBAR HMS) tracks if available
         T211HMSlog = self.dut.dblData.Tables('P211_HMS_MEASUREMENT').tableDataObj()
         objMsg.printMsg('Appending cleanup track list with T211 HMS tracks')
         testTracksDict = self.emptyDict()
         for item in T211HMSlog:
            testTracksDict[int(item['HD_LGC_PSN'])].append(int(item['TRK_NUM']))
         objMsg.printMsg("T211 tracks to add: %s" %testTracksDict)
         trackSpansDict, testTracksDict = self.addTracksToSpans(trackCleanupT211Pad, testTracksDict, trackSpansDict)

         objMsg.printMsg('T211 HMS logical testTracksDict: %s' %testTracksDict)
         self.displayCurrentTrkSpanDict(trackSpansDict)
      except:        # Unable to recover T211 data, go on without
         objMsg.printMsg('Unable to recover P211_HMS_MEASUREMENT table - skipping T211 cleanup')

      ###===========================================================
      # Append list with Test 250 (OAR_SCREEN_ELT) tracks if available
      ###===========================================================
      try:           # Append list with Test 250 (OAR_SCREEN_ELT) tracks if available
         T250OARlog = self.dut.dblData.Tables('P_OAR_SCREEN_SUMMARY').tableDataObj()
         objMsg.printMsg('Appending cleanup track list with OAR test tracks')
         testTracksDict = self.emptyDict()
         for item in T250OARlog:
            testTracksDict[int(item['HD_PHYS_PSN'])].append(int(item['TRK_NUM']))
         objMsg.printMsg("OAR tracks to add: %s" %testTracksDict)
         trackSpansDict, testTracksDict = self.addTracksToSpans(trackCleanupT250Pad, testTracksDict, trackSpansDict)

         objMsg.printMsg('OAR logical testTracksDict: %s' %testTracksDict)
         self.displayCurrentTrkSpanDict(trackSpansDict)

      except:        # Unable to recover T211 data, go on without
         objMsg.printMsg('Unable to recover P_OAR_SCREEN_SUMMARY table - skipping OAR cleanup')

      ###===========================================================
      # Append list with Test 61 (OverWrite) tracks if available (-/+ 3 trks of testtrk)
      ###===========================================================
      try:           # Append list with Test 61 (Overwrite) tracks if available
         T61OWlog = self.dut.dblData.Tables('P061_OW_MEASUREMENT').tableDataObj()
         objMsg.printMsg('Appending cleanup track list with T61 OW tracks')
         testTracksDict = self.emptyDict()
         for item in T61OWlog:
            testTracksDict[int(item['HD_PHYS_PSN'])].append(int(item['TRK_NUM']))
         objMsg.printMsg("T61 tracks to add: %s" %testTracksDict)
         trackSpansDict, testTracksDict = self.addTracksToSpans(trackCleanupT61Pad, testTracksDict, trackSpansDict)

         objMsg.printMsg('T61 OW logical testTracksDict: %s' %testTracksDict)
         self.displayCurrentTrkSpanDict(trackSpansDict)
      except:        # Unable to recover T61 data, go on without
         objMsg.printMsg('Unable to recover P061_OW_MEASUREMENT table - skipping OAR cleanup')

      ###===========================================================
      # Append list with Test 190 (P190_HSC_DATA) tracks if available
      ###===========================================================
      try:           # Append list with Test 190 (P190_HSC_DATA) tracks if available
         T190HSClog = self.dut.dblData.Tables('P190_HSC_DATA').tableDataObj()
         objMsg.printMsg('Appending cleanup track list with T190 CSC tracks')
         testTracksDict = self.emptyDict()
         for item in T190HSClog:
            testTracksDict[int(item['HD_LGC_PSN'])].append(int(item['TRK_NUM']))
         objMsg.printMsg("T190 CSC tracks to add: %s" %testTracksDict)
         trackSpansDict, testTracksDict = self.addTracksToSpans(trackCleanupT190Pad, testTracksDict, trackSpansDict)

         objMsg.printMsg('T190 HSC logical testTracksDict: %s' %testTracksDict)
         self.displayCurrentTrkSpanDict(trackSpansDict)
      except:        # Unable to recover T190 data, go on without
         objMsg.printMsg('Unable to recover P190_HSC_DATA table - skipping T190 CSC cleanup')

      ###====================================================================
      # Append list with Test 190 NCTC (P190_TEST_TRACKS) tracks if available
      ###====================================================================
      try:           # Append list with Test 190 (P190_TEST_TRACKS) tracks if available
         T190HSClog = self.dut.dblData.Tables('P190_TEST_TRACKS').tableDataObj()
         objMsg.printMsg('Appending cleanup track list with T190 NCTC tracks')
         testTracksDict = self.emptyDict()
         for item in T190HSClog:
            self.TrkCtr = int(item['TRK_NUM']) + int(int(item['TRK_RANGE'])/2)
            if DEBUG > 0:
                #self.TrkCtr = int(item['TRK_NUM']) + int(item['TRK_RANGE'])
                objMsg.printMsg('Trk Range = %d trknum = %d trk ctr = %d' % (int(item['TRK_RANGE']), int(item['TRK_NUM']), self.TrkCtr) )
            testTracksDict[int(item['HD_LGC_PSN'])].append(self.TrkCtr)
         objMsg.printMsg("T190 NCTC tracks to add: %s" %testTracksDict)
         if abs(int(item['TRK_RANGE'])) > trackCleanupNCTCPad:
            trackCleanupNCTCPad = abs(int(item['TRK_RANGE']))
            objMsg.printMsg("New NCTC trkpadding = %d" %trackCleanupNCTCPad)
         trackSpansDict, testTracksDict = self.addTracksToSpans(trackCleanupNCTCPad, testTracksDict, trackSpansDict)

         objMsg.printMsg('T190 NCTC logical testTracksDict: %s' %testTracksDict)
         self.displayCurrentTrkSpanDict(trackSpansDict)
      except:        # Unable to recover T190 data, go on without
         objMsg.printMsg('Unable to recover P190_TEST_TRACKS table - skipping T190 NCTC cleanup')

      ###===========================================================
      # Append list with Test 195 (P195_VGA_CSM) tracks if available
      ###===========================================================
      try:           # Append list with Test 195 (P195_VGA_CSM) tracks if available
         T195log = self.dut.dblData.Tables('P195_VGA_CSM').tableDataObj()
         objMsg.printMsg('Appending cleanup track list with T195 tracks')
         testTracksDict = self.emptyDict()
         for item in T195log:
            testTracksDict[int(item['HD_LGC_PSN'])].append(int(item['TRK_NUM']))
         objMsg.printMsg("T195 tracks to add: %s" %testTracksDict)
         trackSpansDict, testTracksDict = self.addTracksToSpans(trackCleanupT195Pad, testTracksDict, trackSpansDict)

         objMsg.printMsg('T195 logical testTracksDict: %s' %testTracksDict)
         self.displayCurrentTrkSpanDict(trackSpansDict)

      except:        # Unable to recover T195 data, go on without
         objMsg.printMsg('Unable to recover P195_VGA_CSM table - skipping T195 cleanup')
      if testSwitch.FE_0258915_348429_COMMON_TWO_TEMP_CERT :
         ###===========================================================
         # Append list with Test 199 (P199_INSTABILITY_TA) tracks if available
         ###===========================================================
         try:           # Append list with Test 195 (P199_INSTABILITY_TA) tracks if available
             T195log = self.dut.dblData.Tables('P199_INSTABILITY_TA').tableDataObj()
             objMsg.printMsg('Appending cleanup track list with T199 tracks')
             testTracksDict = self.emptyDict()
             for item in T195log:
                 testTracksDict[int(item['HD_LGC_PSN'])].append(int(item['TRK_NUM']))
             objMsg.printMsg("T199 tracks to add: %s" %testTracksDict)
             trackSpansDict, testTracksDict = self.addTracksToSpans(trackCleanupT195Pad, testTracksDict, trackSpansDict)
             objMsg.printMsg('T199 logical testTracksDict: %s' %testTracksDict)
             self.displayCurrentTrkSpanDict(trackSpansDict)

         except:        # Unable to recover T199 data, go on without
             objMsg.printMsg('Unable to recover P199_INSTABILITY_TA table - skipping T199 cleanup')
      ###===========================================================
      # Append list with Test 234 (EAW) tracks if available (-/+ 100 trks of testtrk)
      ###===========================================================
      try:           # Append list with Test 234 (EAW) tracks if available
         T234EAWlog = self.dut.dblData.Tables('P234_EAW_ERROR_RATE2').tableDataObj()
         objMsg.printMsg('Appending cleanup track list with T234 EAW tracks')
         testTracksDict = self.emptyDict()
         for item in T234EAWlog:
             testTracksDict[int(item['HD_PHYS_PSN'])].append(int(item['TRK_NUM']))
         objMsg.printMsg("T234 tracks to add: %s" %testTracksDict)
         trackSpansDict, testTracksDict = self.addTracksToSpans(trackCleanupT234Pad, testTracksDict, trackSpansDict)
             
         objMsg.printMsg('T234 EAW logical testTracksDict: %s' %testTracksDict)
         self.displayCurrentTrkSpanDict(trackSpansDict)
      except:        # Unable to recover T234 data, go on without
         objMsg.printMsg('Unable to recover P234_EAW_ERROR_RATE2 table - skipping EAW cleanup')
             
      ###===========================================================
      # Append list with Test 50 (Encroach) tracks if available (-/+ 100 trks of testtrk)
      ###===========================================================
      try:           # Append list with T50 (Encroach) tracks if available
         T50log = self.dut.dblData.Tables('P050_ENCROACH_BER').tableDataObj()
         objMsg.printMsg('Appending cleanup track list with T50 Encroach tracks')
         testTracksDict = self.emptyDict()
         for item in T50log:
             testTracksDict[int(item['HD_PHYS_PSN'])].append(int(item['TRK_NUM']))
         objMsg.printMsg("T50 tracks to add: %s" %testTracksDict)
         trackSpansDict, testTracksDict = self.addTracksToSpans(trackCleanupAFHPad, testTracksDict, trackSpansDict)
                
         objMsg.printMsg('T50 Encroach logical testTracksDict: %s' %testTracksDict)
         self.displayCurrentTrkSpanDict(trackSpansDict)
      except:        # Unable to recover T50 data, go on without
         objMsg.printMsg('Unable to recover P050_ENCROACH_BER table - skipping T50 cleanup')
    
      ###===========================================================
      # Append list with Test 51 (ATI/STE) tracks if available (-/+ 100 trks of testtrk)
      ###===========================================================
      try:           # Append list with Test 51 (ATI/STE)tracks if available
         T51log = self.dut.dblData.Tables('P051_ERASURE_BER').tableDataObj()
         objMsg.printMsg('Appending cleanup track list with T51 ATI STE tracks')
         testTracksDict = self.emptyDict()
         for item in T51log:
             testTracksDict[int(item['HD_PHYS_PSN'])].append(int(item['TRK_NUM']))
         objMsg.printMsg("T51 tracks to add: %s" %testTracksDict)
         trackSpansDict, testTracksDict = self.addTracksToSpans(trackCleanupAFHPad, testTracksDict, trackSpansDict)
    
         objMsg.printMsg('T51 ATI STE logical testTracksDict: %s' %testTracksDict)
         self.displayCurrentTrkSpanDict(trackSpansDict)
      except:        # Unable to recover T51 data, go on without
         objMsg.printMsg('Unable to recover P051_ERASURE_BER table - skipping T51 cleanup')
             
      ###===========================================================
      # Append list with Test 395 (Hd SCRN) tracks if available (-/+ 5 trks of testtrk)
      ###===========================================================
      try:           # Append list with Test 395 (Hd SCRN)tracks if available
         T395log = self.dut.dblData.Tables('P395_AFS_THRESHOLD_SUM').tableDataObj()
         objMsg.printMsg('Appending cleanup track list with T395 Hd SCRN tracks')
         testTracksDict = self.emptyDict()
         for item in T395log:
             testTracksDict[int(item['HD_PHYS_PSN'])].append(int(item['TRK_NUM']))
         objMsg.printMsg("T395 tracks to add: %s" %testTracksDict)
         trackSpansDict, testTracksDict = self.addTracksToSpans(trackCleanupT195Pad, testTracksDict, trackSpansDict)
             
         objMsg.printMsg('T395 ATI STE logical testTracksDict: %s' %testTracksDict)
         self.displayCurrentTrkSpanDict(trackSpansDict)
      except:        # Unable to recover T395 data, go on without
         objMsg.printMsg('Unable to recover P395_AFS_THRESHOLD_SUM table - skipping T395 cleanup')
             
      ###===========================================================
      # Append list with Test 103 (WIJITA) tracks if available (-/+ 5 trks of testtrk)
      ###===========================================================
      try:           # Append list with Test 103 (WIJITA)tracks if available
         T103log = self.dut.dblData.Tables('P103_WIJITA').tableDataObj()
         objMsg.printMsg('Appending cleanup track list with T103 WIJITA tracks')
         testTracksDict = self.emptyDict()
         for item in T103log:
             testTracksDict[int(item['HD_PHYS_PSN'])].append(int(item['TRK_NUM']))
         objMsg.printMsg("T103 tracks to add: %s" %testTracksDict)
         trackSpansDict, testTracksDict = self.addTracksToSpans(trackCleanupT195Pad, testTracksDict, trackSpansDict)
           
         objMsg.printMsg('T103 WIJITA logical testTracksDict: %s' %testTracksDict)
         self.displayCurrentTrkSpanDict(trackSpansDict)
      except:        # Unable to recover T103 data, go on without
         objMsg.printMsg('Unable to recover P103_WIJITA table - skipping T103 cleanup')
      ###===========================================================
      # Append list with failure tracks reported via table 'P000_DRIVE_OP_FAILURE'
      ###===========================================================
      try:           # Append list with problematic tracks frm table 'P000_DRIVE_OP_FAILURE'
         FailTrkTbl = self.dut.dblData.Tables('P000_DRIVE_OP_FAILURE').tableDataObj()
         objMsg.printMsg('Appending cleanup track list with failure tracks reported in SF3')
         testTracksDict = self.emptyDict()
         for item in FailTrkTbl:
            testTracksDict[int(item['HD_LGC_PSN'])].append(int(item['TRK_NUM']))
         objMsg.printMsg("Failed tracks added: %s" %testTracksDict)
         trackSpansDict, testTracksDict = self.addTracksToSpans(trackCleanupT211Pad, testTracksDict, trackSpansDict)

         objMsg.printMsg('Logical converted testTracksDict: %s' %testTracksDict)
         self.displayCurrentTrkSpanDict(trackSpansDict)
      except:        # Unable to recover T211 data, go on without
         objMsg.printMsg('Table P000_DRIVE_OP_FAILURE not found - skipping P000 cleanup')

      #-------------------------------- exiting module .. -----------------------
      # Regenerate the track list as ranges so we don't carry around the huge spans
      trackRangeDict = {}
      for head in trackSpansDict:
         trackRangeDict[head] = [[min(i), max(i)] for i in trackSpansDict[head]]
         if DEBUG > 0: objMsg.printMsg('Hd: %d trackRangeDict b4 sorting: %s' % (head, trackRangeDict[head]))

      # Sort the ranges
      for head in trackRangeDict:
         trackRangeDict[head].sort(key = lambda i: list(i)[0])

      return trackRangeDict

   #-------------------------------------------------------------------------------------------------------
   def addSpanToSpans(self, span, spans):
      for index in xrange(len(spans)):
         if len(spans[index].intersection(span)) > 0:
            #spans overlap so join them
            spans[index].update(span)
            break
      else:
         #triggered if we didn't find this span intersecting with another
         spans.append(span)

      return spans

   #-------------------------------------------------------------------------------------------------------
   def getTrackLBARangeSearch(self, track, head, direction = 1, allowEndOfPackNegSearch = False, maxLoopLimit = 10000):
      startLBA = None
      endLBA = None
      originalTrack = track
      invalidTrackCount = 0
      maxSearchRange = min(10000, (maxLoopLimit-1)/2)

      for counter in range(maxLoopLimit):
         try:
            startLBA, endLBA, track = self.getTrackLBARange(track, head)
            break
         except InvalidTrackException:
            if track == 0:
               direction = 1
               invalidTrackCount = 0

         except EndOfPackException:
            if allowEndOfPackNegSearch:
               direction = -1
               #invalidTrackCount = 0
               #track = originalTrack
            else:
               ScrCmds.raiseException(11044, "End of pack reached", EndOfPackException)

         if ((invalidTrackCount >= maxSearchRange) and not (originalTrack == 0)):
            #if we have greater than 500 invalid tracks then let's search the other direction from the original track
            direction *= -1
            track = originalTrack
            invalidTrackCount = 0

         track += direction
         invalidTrackCount += 1
         if DEBUG > 2:
            objMsg.printMsg("Modifying track evaluation to 0x%X (invalidtkcnt=%d)" % (track,invalidTrackCount) )

      else:
         ScrCmds.raiseException(11044, "Unable to find AFH Track space", EndOfPackException)

      if None in (startLBA, endLBA):
         ScrCmds.raiseException(11044, "Unable to find AFH Track space", EndOfPackException)

      return startLBA, endLBA, track

   #-------------------------------------------------------------------------------------------------------
   def findLastValidTrack(self, startTrack, head, direction = 1):
      increment = 5

      incVal = (increment * direction)
      counter = 0
      abort = False
      for counter in xrange(0xFFFF):
         try:
            startLBA, endLBA, startTrack = self.getTrackLBARange(startTrack, head)
         except (InvalidTrackException, EndOfPackException):
            startTrack -= incVal

            if abort:
               break
            else:
               abort = True

            incVal = (1 * direction)

         startTrack += incVal

      return startTrack

   #-------------------------------------------------------------------------------------------------------
   def getTrackLBARange(self, track, head):
      startLBA = None
      endLBA = None

      if testSwitch.virtualRun or (DEBUG > 2):
        trackInfo = self.oSerial.getTrackInfo(track,head, printResult = True, mode = 'logical')
      else:
        trackInfo = self.oSerial.getTrackInfo(track,head, printResult = False, mode = 'logical')

      if not testSwitch.BF_0164718_357260_P_HANDLE_LEGACY_32_BIT_LBAS:
         invalidLBA = 0xFFFFFFFFFFFF
      else:
         invalidLBA = 0xFFFFFFFF

      if DEBUG > 2:
         FLBA = trackInfo['FIRST_LBA']
         FPBA = trackInfo['FIRST_PBA']
         LSEC = trackInfo['LOG_SECS']
         #PSEC = trackInfo['PHY_SECS']
         ZN = trackInfo['ZONE']
         LGHD = trackInfo['LOG_HEAD']
         LCYL = trackInfo['LOG_CYL']
         objMsg.printMsg("FLba 0x%X, FPba 0x%X, LgSc 0x%X " % (FLBA, FPBA, LSEC))
         objMsg.printMsg("Zn %d Hd %d LgCyl 0x%X" % (ZN, LGHD, LCYL))

      if trackInfo['FIRST_LBA'] < invalidLBA:   # Verify valid LBAs on track

         startLBA = trackInfo['FIRST_LBA']
         endLBA = startLBA + trackInfo['LOG_SECS'] - 1

         if DEBUG > 2:
            objMsg.printMsg("Returning s,e: 0x%X,0x%X" % (startLBA, endLBA))
      else:                                     # Handle case with no valid LBAs on track
         if DEBUG > 2:
            objMsg.printMsg("Invalid LBAs on track!\ntrackInfo: %s" % trackInfo)

         if trackInfo['LOG_CYL'] == 0xFFFFFFFF:
            if DEBUG > 0: objMsg.printMsg("EndOfPackException raised!!!")
            raise EndOfPackException
         else:
            raise InvalidTrackException

      return [startLBA, endLBA, track]

   #-------------------------------------------------------------------------------------------------------
   def emptyDict(self):
      dict = {}
      numHeads = getattr(TP, 'numHeads', 2)
      for head in range(numHeads):
         dict[head] = []
      return dict

   #-------------------------------------------------------------------------------------------------------
   def addTracksToSpans(self, tracksToPad, phytestTracksDict, trackSpansDict):
      from ContinuousSet import cSet

      # Remove duplicate tracks from list
      for head in phytestTracksDict:
         phytestTracksDict[head] = list(set(phytestTracksDict[head]))
         phytestTracksDict[head].sort()

      # Convert tracks to Logical
      lgctestTracksDict = self.convertToLogical(phytestTracksDict)

      # Create list of track ranges to reduce track => LBA translation overhead
      for head in lgctestTracksDict:
         for track in lgctestTracksDict[head]:
            if testSwitch.BF_0209197_357260_P_TRACK_CLEANUP_HANDLE_MAX_TRACK:
               span = cSet(max(self.logTrkRanges[head]['MIN_LOG_CYL'], track - tracksToPad), min(self.logTrkRanges[head]['MAX_LOG_CYL'],track + tracksToPad))
            else:
               span = cSet(max(0, track - tracksToPad), track + tracksToPad)
            trackSpansDict[head] = self.addSpanToSpans(span, trackSpansDict[head])
      return trackSpansDict, lgctestTracksDict

   #-------------------------------------------------------------------------------------------------------
   def convertToLogical(self, trackDict):
      logicalTrackDict = {}

      for head in trackDict:
         logicalTrackDict[head] = []
         for track in trackDict[head]:
            trackInfo = self.oSerial.getTrackInfo(track,head, printResult = False)
            if DEBUG > 2:
               FLBA = trackInfo['FIRST_LBA']
               FPBA = trackInfo['FIRST_PBA']
               LSEC = trackInfo['LOG_SECS']
               #PSEC = trackInfo['PHY_SECS']
               ZN = trackInfo['ZONE']
               LGHD = trackInfo['LOG_HEAD']
               LCYL = trackInfo['LOG_CYL']
               objMsg.printMsg("FLba 0x%X, FPba 0x%X, LgSc 0x%X, " % (FLBA, FPBA, LSEC))
               objMsg.printMsg("Zn %d Hd %d LgCyl 0x%X" % (ZN, LGHD, LCYL))

            if trackInfo['LOG_CYL'] != 0xFFFFFFFF:
               logicalTrackDict[head].extend([trackInfo['LOG_CYL']])
            else:
               if testSwitch.BF_0209197_357260_P_TRACK_CLEANUP_HANDLE_MAX_TRACK:
                  logicalTrackDict[head].extend([self.logTrkRanges[head]['MAX_LOG_CYL']])
               else:
                  pass

      return logicalTrackDict


#----------------------------------------------------------------------------------------------------------
class CRroScrn(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from Servo import CServoScreen
      oSrvScreen = CServoScreen()

      oSrvScreen.resonanceTest(TP.prm_RRO_Resonance_180)


#-------------------------------------------------------------------------------------------------------
class CTcc_Verify(CState):
   """
      Class to vefify TCC - Smart TCC
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      spc_id = 3
      if testSwitch.RESET_TCC1_SLOPE_IF_BOTH_TCC1_AND_BER_OVER_SPEC == 1 and self.dut.nextState == 'TCC_VERIFY1':
         self.VerifyAndResetTcc()

      if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT == 1 and self.dut.nextState == 'TCC_VERIFY2':
         from AFH_Screens_DH import CAFH_Screens
         oAFH_Screens = CAFH_Screens()
         oAFH_Screens.calTempLimitBaseOnTCC(spc_id)
         tcc1_loLimitWrtHt, tcc1_upLimitWrtHt = oAFH_Screens.SmartTccLimits()

   #-------------------------------------------------------------------------------------------------------
   def VerifyAndResetTcc(self):
      from RdWr import CRdScrn2File
      from RAP import ClassRAP
      objRAP = ClassRAP()
      oRdScrn2File = CRdScrn2File()
      try:
         # Grab all the ber data.
         List_r2_ber  = oRdScrn2File.Retrieve_RD_SCRN2_RAW()
         List_r2c_ber = self.dut.List_r2c_ber
      except:
         objMsg.printMsg("Fail to read ber data, let it pass and verify by BER later")
         return
      if len(self.dut.TccChgByBerHeadList) != 0:
         try:
            List_r2d_ber = self.dut.List_r2d_ber
            for hd in self.dut.TccChgByBerHeadList:
               List_r2c_ber[hd] =  List_r2d_ber[hd]
         except:
            pass

      objMsg.printMsg("List_fnc2_ber  = %s"%(str(List_r2_ber)))
      objMsg.printMsg("List_crt2_ber = %s"%(str(List_r2c_ber)))
      spcid = 100
      for head in xrange(self.dut.imaxHead):
         objMsg.printMsg("***Head %s, avg_crt2_ber_list = %s***"%(str(head),str(mean(List_r2c_ber[head])))) 
         objMsg.printMsg("***Head %s, avg_fnc2_ber_list = %s***"%(str(head),str(mean(List_r2_ber[head])))) 
         resetWrtTCS = 0
         resetRdTCS = 0
         slope = 'NONE'
         delta_ber = abs(mean(List_r2c_ber[head])) - abs(mean(List_r2_ber[head]))
         objMsg.printMsg("***Head %s, Delta_ber(abs(Avg_crt2) - abs(Avg_fnc2)) = %s***"%(str(head),str(delta_ber)))

         if abs(delta_ber) > TP.delta_R2C_bigger_than_R2:
            spcid = spcid + 1
            oRdScrn2File.Show_P172_AFH_TC_COEF_2(spcid)
            if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT:
               Current_TCC1_R, Current_TCC1_W = oRdScrn2File.Get_Current_TCC1(spcid)
               objMsg.printMsg("Current_TCC1_R %s"%(str(Current_TCC1_R)))
               objMsg.printMsg("Current_TCC1_W %s"%(str(Current_TCC1_W)))

               W_TCS1_DEFAULT     = TP.tcc_DH_dict_178 ['WRITER_HEATER']['TCS1']   # in angtrom/C
               R_TCS1_DEFAULT     = TP.tcc_DH_dict_178 ['READER_HEATER']['TCS1']   # in angtrom/C
               if (delta_ber > 0 and not testSwitch.FE_0258915_348429_COMMON_TWO_TEMP_CERT) or \
                  (delta_ber < 0 and testSwitch.FE_0258915_348429_COMMON_TWO_TEMP_CERT): 
                  if Current_TCC1_W[head] < W_TCS1_DEFAULT:
                     resetWrtTCS  = 1
                     objMsg.printMsg("*****CURRENT WRT TCS1 OVER POWER, NEED TO BE RESET!*****")
                  if Current_TCC1_R[head] < R_TCS1_DEFAULT:
                     resetRdTCS = 1
                     objMsg.printMsg("*****CURRENT RD TCS1 OVER POWER, NEED TO BE RESET!*****")
               else:
                  if Current_TCC1_W[head] > W_TCS1_DEFAULT:
                     resetWrtTCS  = 1
                     objMsg.printMsg("*****CURRENT WRT TCS1 UNDER POWER, NEED TO BE RESET!*****")
                  if Current_TCC1_R[head] > R_TCS1_DEFAULT:
                     resetRdTCS = 1
                     objMsg.printMsg("*****CURRENT RD TCS1 UNDER POWER, NEED TO BE RESET!*****")
            else:
               Current_TCC1 = oRdScrn2File.Get_Current_TCC1(spcid)
               TCS1_DEFAULT     = TP.tccDict_178['TCS1']*254.0      #convert  uinch/C to angtrom/C
               if (delta_ber > 0 and not testSwitch.FE_0258915_348429_COMMON_TWO_TEMP_CERT) or \
                  (delta_ber < 0 and testSwitch.FE_0258915_348429_COMMON_TWO_TEMP_CERT): 
                  if Current_TCC1_W[head] < W_TCS1_DEFAULT:
                     resetWrtTCS  = 1
                     objMsg.printMsg("*****CURRENT WRT TCS1 OVER POWER, NEED TO BE RESET!*****")
               else:
                  if Current_TCC1_W[head] > W_TCS1_DEFAULT:
                     resetWrtTCS  = 1
                     objMsg.printMsg("*****CURRENT WRT TCS1 UNDER POWER, NEED TO BE RESET!*****")


            if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT:
               if resetWrtTCS  == 1:
                  if not testSwitch.extern.FE_0157745_387179_AFH_TCS_WARP:
                     objRAP.SaveTCC_toRAP( head, TP.tcc_DH_dict_178 ['WRITER_HEATER']['TCS1'], TP.tcc_DH_dict_178["WRITER_HEATER"]['TCS2'], "WRITER_HEATER",TP.tcc_DH_values)
                  else:
                     objRAP.SaveTCC_toRAP( head, TP.tcc_DH_dict_178 ['WRITER_HEATER']['TCS1'], TP.tcc_DH_dict_178["WRITER_HEATER"]['TCS2'], "WRITER_HEATER",TP.tcc_DH_values,TP.TCS_WARP_ZONES.keys())
               if resetRdTCS == 1:
                  if not testSwitch.extern.FE_0157745_387179_AFH_TCS_WARP:
                     objRAP.SaveTCC_toRAP( head, TP.tcc_DH_dict_178 ['READER_HEATER']['TCS1'], TP.tcc_DH_dict_178["READER_HEATER"]['TCS2'], "READER_HEATER",TP.tcc_DH_values)
                  else:
                     objRAP.SaveTCC_toRAP( head, TP.tcc_DH_dict_178 ['READER_HEATER']['TCS1'], TP.tcc_DH_dict_178["READER_HEATER"]['TCS2'], "READER_HEATER",TP.tcc_DH_values,TP.TCS_WARP_ZONES.keys())
            else:     # single heater drive
               if resetWrtTCS  == 1:
                  if not testSwitch.extern.FE_0157745_387179_AFH_TCS_WARP:
                     objRAP.SaveTCC_toRAP( head, TP.tccDict_178['TCS1']*254.0 , TP.tcc_DH_dict_178["WRITER_HEATER"]['TCS2'], "WRITER_HEATER",TP.tcc_DH_values)
                  else:
                     objRAP.SaveTCC_toRAP( head, TP.tccDict_178['TCS1']*254.0 , TP.tcc_DH_dict_178["WRITER_HEATER"]['TCS2'], "WRITER_HEATER",TP.tcc_DH_values,TP.tcc_DH_values,TP.TCS_WARP_ZONES.keys())
            if resetRdTCS == 1 or resetWrtTCS  == 1:
               objRAP.mFSO.saveRAPtoFLASH()


#----------------------------------------------------------------------------------------------------------
class CTcc_BY_BER(CState):
   """
      Class made for calling method that runs test250 for track err rate differential screen
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      self.use_vbar_sova = eval(self.params.get('USE_VBAR_SOVA', "0"))
      objMsg.printMsg("self.use_vbar_sova %s"%(str(self.use_vbar_sova)))

      try:
         if not testSwitch.FE_0258915_348429_COMMON_TWO_TEMP_CERT:
           List_r2a_ber = self.dut.List_r2a_ber
         List_r2c_ber = self.dut.List_r2c_ber
      except:
         self.dut.stateTransitionEvent = 'restartAtState'
         self.dut.nextState = 'READ_SCRN2A'
         return

      #if testSwitch.TCC_SLOPE_TUNED_BY_BER == 0:
      #   return 0


      # Grab all the ber data.
      if testSwitch.FE_0110575_341036_ENABLE_MEASURING_CONTACT_USING_TEST_135 == 1:
         if testSwitch.extern.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT == 1:
            from AFH_Screens_DH import CAFH_Screens
         else:
            from AFH_Screens_T135 import CAFH_Screens
      else:
         if testSwitch.extern.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT == 1:
            from AFH_Screens_DH import CAFH_Screens
         else:
            from AFH_Screens_T035 import CAFH_Screens

      from RdWr import CRdScrn2File

      self.oAFH_Screens  = CAFH_Screens()
      oRdScrn2File = CRdScrn2File()

      if testSwitch.extern.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT == 1:
         from AFH import CAFH
         oAFH = CAFH()
         oAFH.getDHStatus( self.dut.PREAMP_TYPE, self.dut.AABType, TP.clearance_Coefficients )

      SetFailSafe()
      ## Set original TCC back remove ######################################
      #from RAP import ClassRAP
      #objRAP = ClassRAP()
      #if testSwitch.FE_0169232_341036_ENABLE_AFH_TGT_CLR_CANON_PARAMS == 1:
      #   from AFH_canonParams import *
      #   tcc_DH_values = getTCS_values()
      #else:
      #   tcc_DH_values = TP.tcc_DH_values

      #original_tcc =[-0.008,-0.008]
      ##original_tcc =[-0.0014310165,-0.0005000000]
      #for head_t in xrange(0,self.dut.imaxHead):
      #   tcc2 = 0
      #   objRAP.SaveTCC_toRAP(head_t, original_tcc[head_t], tcc2, "WRITER_HEATER",tcc_DH_values)  # this saves values to RAP
      #self.oAFH_Screens.mFSO.saveRAPtoFLASH()                #Save the settings from RAP to flash (non-volatile)
      #######################################################################
      #objMsg.printMsg("############################    Default TCC slope From Drive    ############################# ")
      oRdScrn2File.Show_P172_AFH_TC_COEF_2(105)
      #objMsg.printMsg("Retrive the READ_SCRN2 (FNC2) error rate from sytem zone")
      #objMsg.printMsg("############################    End of  TCC slope From Drive    ############################# ")


      List_save_default_TCC1  = [[] for hd in xrange(self.dut.imaxHead)]
      List_save_default_TCC1_R  = [[] for hd in xrange(self.dut.imaxHead)]
      List_save_default_TCC1_W  = [[] for hd in xrange(self.dut.imaxHead)]
      List_r2_ber  = oRdScrn2File.Retrieve_RD_SCRN2_RAW()
      self.dut.List_r2_ber = List_r2_ber

      #List_save_default_TCC1 = oRdScrn2File.Get_Current_TCC1()
      if testSwitch.extern.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT:
         List_save_default_TCC1_R, List_save_default_TCC1_W = oRdScrn2File.Get_Current_TCC1(105)
         if DEBUG_TCC > 0:
            objMsg.printMsg("List_save_default_TCC1_R %s"%(str(List_save_default_TCC1_R)))
            objMsg.printMsg("List_save_default_TCC1_W %s"%(str(List_save_default_TCC1_W)))
         List_save_default_TCC1 = List_save_default_TCC1_W
      else:
         List_save_default_TCC1 = oRdScrn2File.Get_Current_TCC1(105)
         if DEBUG_TCC > 0:
            objMsg.printMsg("List_save_default_TCC1 %s"%(str(List_save_default_TCC1)))

      # TCC2 is hardcoded to 0
      List_save_default_TCC2 = 0.0


      objMsg.printMsg("####################################  SPEC and Data Segment ########################################################")
      objMsg.printMsg("r2_ber  -> BER list from READ_SCRN2  (FNC2 state) No TCC compensation at Hot Temperature")
      objMsg.printMsg("r2a_ber -> BER list from READ_SCRN2A (CRT2 state) No TCC compensation at Cold Temperature")
      objMsg.printMsg("r2c_ber -> BER list from READ_SCRN2C (CRT2 state) With TCC compensation at Cold Temperature")
      objMsg.printMsg("TP.ber_spec %s"%(str(TP.ber_spec)))
      objMsg.printMsg("TP.tcc1_step_size %s"%(str(TP.tcc1_step_size)))
      objMsg.printMsg("TP.tcc1_step_size_dec %s"%(str(TP.tcc1_step_size_dec)))
      objMsg.printMsg("TP.Maximum_TCC1_Step_allowed %s"%(str(TP.Maximum_TCC1_Step_allowed)))
      if DEBUG_TCC > 0:
         objMsg.printMsg("List_save_default_TCC1 = %s"%(str(List_save_default_TCC1)))
         objMsg.printMsg("List_r2_ber  = %s"%(str(List_r2_ber)))
         objMsg.printMsg("List_r2c_ber = %s"%(str(List_r2c_ber)))
      if not testSwitch.FE_0258915_348429_COMMON_TWO_TEMP_CERT:
         objMsg.printMsg("List_r2a_ber = %s"%(str(List_r2a_ber)))
         objMsg.printMsg("TP.delta_R2_R2A_ber = %s"  %(str(TP.delta_R2_R2A_ber)))
      objMsg.printMsg("####################################  End of SPEC and Data Segment #################################################")
      ########################################################################
      if testSwitch.extern.FE_0157745_387179_AFH_TCS_WARP:
         #tcc_by_zone_list = TP.TCS_WARP_ZONES
         tcc_by_zone_key  = TP.TCS_WARP_ZONES.keys()
         tcc_by_zone_list = {}
         
         for key in TP.TCS_WARP_ZONES.keys():
            if  testSwitch.FE_AFH_RSQUARE_TCC:
               tcc_by_zone_list[key] =  TP.TCS_WARP_ZONES[key] # (0, self.dut.numZones-1)
            else:
               tcc_by_zone_list[key] =  (0, self.dut.numZones-1)
         tcc_by_zone_key.sort()
      else:
         tcc_by_zone_list = {0:(0, self.dut.numZones-1)}
         tcc_by_zone_key  = tcc_by_zone_list.keys()
         tcc_by_zone_key.sort()

      step_count_needed   = [[] for hd in xrange(self.dut.imaxHead)]
      final_tcc1          = [[] for hd in xrange(self.dut.imaxHead)]
      segment_tune_zone   = [[] for hd in xrange(self.dut.imaxHead)]
      segment_target_ber  = [[] for hd in xrange(self.dut.imaxHead)]
      final_tuned_ber     = [[] for hd in xrange(self.dut.imaxHead)]
      start_tuned_ber     = [[] for hd in xrange(self.dut.imaxHead)]
      direction     = [[] for hd in xrange(self.dut.imaxHead)]
      slope_type    = [[] for hd in xrange(self.dut.imaxHead)]
      revert_orig_TCC1    = [[] for hd in xrange(self.dut.imaxHead)]
      delta_write_heater  = [[] for hd in xrange(self.dut.imaxHead)]
      delta_read_heater   = [[] for hd in xrange(self.dut.imaxHead)]
      delta_pre_heater    = [[] for hd in xrange(self.dut.imaxHead)]
      need_repot_coef = 'N'
      need_save_to_flash = 'N'

      if testSwitch.FE_0257006_348085_EXCLUDE_UMP_FROM_TCC_BY_BER:
         objMsg.printMsg("TP.UMP_ZONE = %s"%(str(TP.UMP_ZONE)))
         for hd in xrange(self.dut.imaxHead):
            for zn in TP.UMP_ZONE[self.dut.numZones]:
               objMsg.printMsg("hd = %d zn = %d"%(hd, zn))
               List_r2_ber[hd][zn] = 0
               List_r2c_ber[hd][zn] = 0
               if not testSwitch.FE_0258915_348429_COMMON_TWO_TEMP_CERT: # R2A is skipped in 25/50degC CERT
                  List_r2a_ber[hd][zn] = 0
         if DEBUG_TCC > 0:
            objMsg.printMsg("List_r2_ber ( Exclude UMP Zones)  = %s"%(str(List_r2_ber)))
            objMsg.printMsg("List_r2c_ber( Exclude UMP Zones)  = %s"%(str(List_r2c_ber)))
         if not testSwitch.FE_0258915_348429_COMMON_TWO_TEMP_CERT: # R2A is skipped in 25/50degC CERT
            objMsg.printMsg("List_r2a_ber( Exclude UMP Zones)  = %s"%(str(List_r2a_ber)))
      ########################################################
      # Fail drive if the delta R2 - R2A > spec
      if not testSwitch.FE_0258915_348429_COMMON_TWO_TEMP_CERT: # R2A is skipped in 25/50degC CERT
         for head in xrange(self.dut.imaxHead):
            for zone in xrange(self.dut.numZones):
               delta = List_r2_ber[head][zone] - List_r2a_ber[head][zone]
               objMsg.printMsg("Head = %s Zone = %s R2 = %s R2a= %s delta = %s"  %(str(head), str(zone),str(List_r2_ber[head][zone]), str(List_r2a_ber[head][zone]), str(delta)))
               if abs(delta) > TP.delta_R2_R2A_ber:
                  objMsg.printMsg("Fail delta (R2 - R2A) at Head = %s Zone = %s delta = %s"  %(str(head), str(zone), str(delta)))
                  ScrCmds.raiseException(11262, "R2 - R2A BER exceed limit")             




      objMsg.printMsg("####################################  Start Tune the Tcc1 Slope by BER  ############################################")
      spc_id = 10000
      for head in xrange(self.dut.imaxHead):
         tcc_izone = 0
         for tcc_zone_segment in tcc_by_zone_key:
            if testSwitch.FE_AFH_RSQUARE_TCC or tcc_zone_segment == tcc_by_zone_key[0]: #rsq_tcc
               # Determine slope of the head by comparing the avg R2 and R2a
               objMsg.printMsg("Tuning region: Head %s Start_zone %s End_zone %s"%(head,str(tcc_by_zone_list[tcc_zone_segment][0]), str(tcc_by_zone_list[tcc_zone_segment][1])))
               if not testSwitch.FE_0258915_348429_COMMON_TWO_TEMP_CERT: # R2A is skipped in 25/50degC CERT
                  if self.DriveSlopeByBer(List_r2a_ber,List_r2_ber, head,tcc_by_zone_list[tcc_zone_segment][0],tcc_by_zone_list[tcc_zone_segment][1]) == 'NEGATIVE_SLOPE':
                     objMsg.printMsg("Slope behavior: NEGATIVE_SLOPE by BER => Average BER R2 (Hot Temp) > Average BER R2a (Cold). Both R2 and R2a no TCC.")
                     slope_type_ber = 'NEG_SLOPE'
                     # Check the polarity of the slope if match with the AFH4 data      
                     #if DriveSlopeByAFH4() == 'POSITIVE_SLOPE':        
                     #   raise
                  else: # POSITIVE SLOPE
                     objMsg.printMsg("Slope behavior: POSITIVE_SLOPE by BER => Average BER R2 (Hot Temp) < Average BER R2a (Cold). Both R2 and R2a no TCC.")
                     slope_type_ber = 'POS_SLOPE'
                     # Check the polarity of the slope if match with the AFH4 data      
                     #if DriveSlopeByAFH4() == 'NEGATIVE_SLOPE':        
                     #   raise
               else:
                  slope_type_ber = 'NEG_SLOPE'
                  # Check the polarity of the slope if match with the AFH4 data
                  #if DriveSlopeByAFH4() == 'POSITIVE_SLOPE':
                  #   raise

               # Determine if the AFH4 tcc1 is slope is over/under compensate by comparing the R2C (with TCC) and R2 (no TCC)
               Tcc1slopeResult = self.ExamineTCC1slopeByBer(List_r2c_ber, List_r2_ber,head, tcc_by_zone_list[tcc_zone_segment][0],tcc_by_zone_list[tcc_zone_segment][1])
               spc_id = spc_id + 1
               if Tcc1slopeResult == 'OVER_COMPENSATE': # Avg R2C > Avg R2 ==> slope too negative
                  #zone_to_tune = self.GetZoneWithMaxPositiveMargin(List_r2c_ber,List_r2_ber, head, tcc_by_zone_list[tcc_zone_segment][0],tcc_by_zone_list[tcc_zone_segment][1])
                  zone_to_tune, target_ber = self.getWorstBerZone(List_r2c_ber[head], tcc_by_zone_list[tcc_zone_segment][0],tcc_by_zone_list[tcc_zone_segment][1])
                  objMsg.printMsg(" <<<< Target to decrease BER of head %s, zone %s (Tuning region: Start_zone = %s End_zone = %s) to meet target_ber of %s >>>>"%(str(head),str(zone_to_tune),str(tcc_by_zone_list[tcc_zone_segment][0]), str(tcc_by_zone_list[tcc_zone_segment][1]),str(List_r2_ber[head][zone_to_tune])))
                  current_TCC1, new_TCC1 = self.TuneTCC1ToMeetTargetBer(head, zone_to_tune, List_r2_ber[head][zone_to_tune],slope_type_ber,'DECREASE_BER', tcc_zone_segment, tcc_izone,spc_id) 
                  if current_TCC1 != new_TCC1['tcc1_slope']:
                     if head not in self.dut.TccChgByBerHeadList:
                        self.dut.TccChgByBerHeadList.append(head)

                  direction[head].append('DEC_BER')
               elif Tcc1slopeResult == 'OVER_NEED_RESET':
                  if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT:
                     default_W_TCS1 = TP.tcc_DH_dict_178 ['WRITER_HEATER']['TCS1']        # in angtrom/C
                     default_R_TCS1 = TP.tcc_DH_dict_178 ['READER_HEATER']['TCS1']        # in angtrom/C
                     new_W_TCC1 = default_W_TCS1
                     new_R_TCC1 = default_R_TCS1
                  else:
                     default_TCS1 = TP.tccDict_178['TCS1']*254.0                        # convert  uinch/C to angtrom/C
                     new_TCC1 = default_TCS1
                  #direction[head].append('DEC_BER')
               else:
                  #zone_to_tune = self.GetZoneWithMaxNegativeMargin(List_r2c_ber,List_r2_ber, head, tcc_by_zone_list[tcc_zone_segment][0],tcc_by_zone_list[tcc_zone_segment][1])
                  zone_to_tune, target_ber = self.getWorstBerZone(List_r2c_ber[head], tcc_by_zone_list[tcc_zone_segment][0],tcc_by_zone_list[tcc_zone_segment][1])
                  objMsg.printMsg("<<<< Target to Increase BER of head %s, zone %s (Tuning region: Start_zone = %s End_zone = %s) to meet target_ber of %s >>>>"%(str(head),str(zone_to_tune),str(tcc_by_zone_list[tcc_zone_segment][0]), str(tcc_by_zone_list[tcc_zone_segment][1]), str(List_r2_ber[head][zone_to_tune])))
                  current_TCC1, new_TCC1 = self.TuneTCC1ToMeetTargetBer(head, zone_to_tune, List_r2_ber[head][zone_to_tune],slope_type_ber,'INCREASE_BER', tcc_zone_segment, tcc_izone, spc_id)
                  if current_TCC1 != new_TCC1['tcc1_slope']:
                     if head not in self.dut.TccChgByBerHeadList:
                        self.dut.TccChgByBerHeadList.append(head)

                  direction[head].append('INC_BER')
               if Tcc1slopeResult != 'OVER_NEED_RESET':
                  ## Store the value
                  segment_tune_zone[head].append(zone_to_tune)
                  segment_target_ber[head].append(List_r2_ber[head][zone_to_tune])
                  final_tuned_ber[head].append(new_TCC1['BER_AT_END_HEATER'])
                  start_tuned_ber[head].append(new_TCC1['BER_AT_START'])
                  step_count_needed[head].append(new_TCC1['STEP_COUNT'])
                  final_tcc1[head].append(new_TCC1['tcc1_slope'])
                  slope_type[head].append(slope_type_ber)
                  revert_orig_TCC1[head].append(new_TCC1['REVERT'])

                  delta_write_heater[head].append(new_TCC1['DELTA_WRITE_HEATER'])
                  delta_read_heater[head].append(new_TCC1['DELTA_READ_HEATER'])
                  delta_pre_heater[head].append(new_TCC1['DELTA_PRE_HEATER'])

                  # Save the new TCC1 to the drive #########
                  objMsg.printMsg("#########  Head %d Segment %s Final TCC1 = %s"%(head,str(tcc_zone_segment), str(new_TCC1['tcc1_slope'])))
               if len(self.dut.TccChgByBerHeadList):
                  # Indicating TCC changed
                  if 'TCC_BY_BER' in TP.Proc_Ctrl30_Def:
                     self.dut.driveattr['PROC_CTRL30'] = '0X%X' % (int(self.dut.driveattr.get('PROC_CTRL30', '0'),16) | TP.Proc_Ctrl30_Def['TCC_BY_BER'])
            if testSwitch.extern.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT == 1:
               #oAFH.getDHStatus( self.dut.PREAMP_TYPE, self.dut.AABType, TP.clearance_Coefficients )
               # get the DH status and store in dut for future use
               from RAP import ClassRAP
               objRAP = ClassRAP()
               if testSwitch.FE_0169232_341036_ENABLE_AFH_TGT_CLR_CANON_PARAMS == 1:
                  from AFH_canonParams import *
                  tcc_DH_values = getTCS_values()
               else:
                  tcc_DH_values = TP.tcc_DH_values
               from AFH_constants import AFH_ANGSTROMS_PER_MICROINCH
               if not testSwitch.extern.FE_0157745_387179_AFH_TCS_WARP:
                  if  self.dut.isDriveDualHeater==1: # dual heater drive
                    if Tcc1slopeResult == 'OVER_NEED_RESET':
                       objRAP.SaveTCC_toRAP( head, new_W_TCC1, List_save_default_TCC2, "WRITER_HEATER",tcc_DH_values)
                       objRAP.SaveTCC_toRAP( head, new_R_TCC1, TP.tcc_DH_dict_178["READER_HEATER"]['TCS2'], "READER_HEATER",tcc_DH_values)
                    else:
                       objRAP.SaveTCC_toRAP( head, new_TCC1['tcc1_slope'], List_save_default_TCC2, "WRITER_HEATER",tcc_DH_values)
                       #objRAP.SaveTCC_toRAP( iHead, TP.tcc_DH_dict_178["READER_HEATER"]['TCS1'], TP.tcc_DH_dict_178["READER_HEATER"]['TCS2'], "READER_HEATER" )
                  else:     # single heater drive
                    if Tcc1slopeResult == 'OVER_NEED_RESET':
                       objRAP.SaveTCC_toRAP( head, new_W_TCC1, List_save_default_TCC2, "WRITER_HEATER",tcc_DH_values)
                       objRAP.SaveTCC_toRAP( head, new_R_TCC1, List_save_default_TCC2, "READER_HEATER",tcc_DH_values)
                    else:
                       objRAP.SaveTCC_toRAP( head, new_TCC1['tcc1_slope'], List_save_default_TCC2, "WRITER_HEATER",tcc_DH_values)
                       objRAP.SaveTCC_toRAP( head, new_TCC1['tcc1_slope'], List_save_default_TCC2, "READER_HEATER",tcc_DH_values)
               else:
                  if  self.dut.isDriveDualHeater==1: # dual heater drive
                    if Tcc1slopeResult == 'OVER_NEED_RESET':   
                       if testSwitch.FE_AFH_RSQUARE_TCC:                     
                          objRAP.SaveTCC_toRAP( head, new_W_TCC1, List_save_default_TCC2, "WRITER_HEATER",tcc_DH_values, [tcc_zone_segment, ]) # tcc_rsq
                       else:
                          objRAP.SaveTCC_toRAP( head, new_W_TCC1, List_save_default_TCC2, "WRITER_HEATER",tcc_DH_values, TP.TCS_WARP_ZONES.keys())
                          objRAP.SaveTCC_toRAP( head, new_R_TCC1, TP.tcc_DH_dict_178["READER_HEATER"]['TCS2'], "READER_HEATER",tcc_DH_values,TP.TCS_WARP_ZONES.keys())
                    else:
                       if testSwitch.FE_AFH_RSQUARE_TCC: 
                          objRAP.SaveTCC_toRAP( head, new_TCC1['tcc1_slope'], List_save_default_TCC2, "WRITER_HEATER", tcc_DH_values, [tcc_zone_segment, ]) #  # tcc_rsq
                       else:
                          objRAP.SaveTCC_toRAP( head, new_TCC1['tcc1_slope'], List_save_default_TCC2, "WRITER_HEATER", tcc_DH_values, TP.TCS_WARP_ZONES.keys())

                  else:     # single heater drive
                    if Tcc1slopeResult == 'OVER_NEED_RESET':
                      if testSwitch.FE_AFH_RSQUARE_TCC: 
                         objRAP.SaveTCC_toRAP( head, new_TCC1, List_save_default_TCC2, "WRITER_HEATER",  [tcc_zone_segment, ])
                      else:
                         objRAP.SaveTCC_toRAP( head, new_TCC1, List_save_default_TCC2, "WRITER_HEATER", tcc_DH_values,TP.TCS_WARP_ZONES.keys())
                         objRAP.SaveTCC_toRAP( head, new_TCC1, List_save_default_TCC2, "READER_HEATER", tcc_DH_values,TP.TCS_WARP_ZONES.keys())
                    else:
                       if testSwitch.FE_AFH_RSQUARE_TCC: 
                          objRAP.SaveTCC_toRAP( head, new_TCC1['tcc1_slope'], List_save_default_TCC2, "WRITER_HEATER",  [tcc_zone_segment, ])
                       else:
                          objRAP.SaveTCC_toRAP( head, new_TCC1['tcc1_slope'], List_save_default_TCC2, "WRITER_HEATER", tcc_DH_values,TP.TCS_WARP_ZONES.keys())
                          objRAP.SaveTCC_toRAP( head, new_TCC1['tcc1_slope'], List_save_default_TCC2, "READER_HEATER", tcc_DH_values,TP.TCS_WARP_ZONES.keys())
            else:
               if not testSwitch.extern.FE_0157745_387179_AFH_TCS_WARP:
                  self.oAFH_Screens.SaveTCC( head, new_TCC1['tcc1_slope'], List_save_default_TCC2 )
               else:
                  self.oAFH_Screens.SaveTCC( head, new_TCC1['tcc1_slope'], List_save_default_TCC2,TP.TCS_WARP_ZONES.keys() )
            tcc_izone = tcc_izone +1
            need_repot_coef = 'Y'
            need_save_to_flash = 'Y'

      objMsg.printMsg("####################################  End of Tune the Tcc1 Slope by BER  ############################################")

      if TP.save_to_flash == 1:
         if need_save_to_flash == 'Y':
            objMsg.printMsg("####################################  Saving the TCC1 to Flash   ####################################################")
            self.oAFH_Screens.mFSO.saveRAPtoFLASH()                #Save the settings from RAP to flash (non-volatile)
      else:
         objMsg.printMsg("##### No save TCC1 to Flash ####")

      if not testSwitch.FE_0315271_348085_P_OPTIMIZING_TCC_BY_BER_FOR_CM_OVERLOADING:
         objMsg.printMsg("==========================================================================================================================")
         objMsg.printMsg("==========================================================================================================================")
         if testSwitch.extern.FE_0157745_387179_AFH_TCS_WARP:
             objMsg.printMsg("===============================    Summary for Compensation Step Needed    ===============================")
             objMsg.printMsg(" Head   Segment  zone  Compensated_step    step_size       new_TCC1        orig_TCC1        Target_ber       Final_BER        Start_BER        Slope       Direction     REVERT   D_PRE_HEAT D_WRT_HEAT D_RD_HEAT")
             for head in xrange(self.dut.imaxHead):
                if len(segment_tune_zone[head])>0:
                   for tcc_zone_segment in xrange(0,1): #len(TP.TCS_WARP_ZONES)):
                      objMsg.printMsg(" %d       %d      %d         %d               %s       %9.4f        %9.4f        %9.4f       %9.4f       %9.4f     %s      %s      %s      %s      %s      %s"%(head, tcc_zone_segment, segment_tune_zone[head][tcc_zone_segment], step_count_needed[head][tcc_zone_segment],str(TP.tcc1_step_size),final_tcc1[head][tcc_zone_segment],List_save_default_TCC1[head][tcc_zone_segment],segment_target_ber[head][tcc_zone_segment],final_tuned_ber[head][tcc_zone_segment],start_tuned_ber[head][tcc_zone_segment],str(slope_type[head][tcc_zone_segment]),str(direction[head][tcc_zone_segment]),str(revert_orig_TCC1[head][tcc_zone_segment]),str(delta_pre_heater[head][tcc_zone_segment]),str(delta_write_heater[head][tcc_zone_segment]),str(delta_read_heater[head][tcc_zone_segment])))
         else:
             objMsg.printMsg("===============================    Summary for Compensation Step Needed    ===============================")
             objMsg.printMsg(" Head   Segment  zone  Compensated_step    step_size       new_TCC1        orig_TCC1        Target_ber       Final_BER        Start_BER        Slope       Direction     REVERT   D_PRE_HEAT D_WRT_HEAT D_RD_HEAT")
             for head in xrange(self.dut.imaxHead):
                if len(segment_tune_zone[head])>0:
                   objMsg.printMsg(" %d       %d      %d         %d               %s       %9.4f        %9.4f        %9.4f       %9.4f       %9.4f     %s      %s       %s      %s       %s       %s"%(head, tcc_zone_segment, segment_tune_zone[head][tcc_zone_segment], step_count_needed[head][tcc_zone_segment],str(TP.tcc1_step_size),final_tcc1[head][tcc_zone_segment],List_save_default_TCC1[head],segment_target_ber[head][tcc_zone_segment],final_tuned_ber[head][tcc_zone_segment],start_tuned_ber[head][tcc_zone_segment],str(slope_type[head][tcc_zone_segment]),str(direction[head][tcc_zone_segment]),str(revert_orig_TCC1[head][tcc_zone_segment]),str(delta_pre_heater[head][tcc_zone_segment]),str(delta_write_heater[head][tcc_zone_segment]),str(delta_read_heater[head][tcc_zone_segment])))
         objMsg.printMsg("==========================================================================================================================")
         objMsg.printMsg("==========================================================================================================================")
         objMsg.printMsg("==========================================================================================================================")

      # Dblog Implementation
      if testSwitch.extern.FE_0157745_387179_AFH_TCS_WARP:
          for head in xrange(self.dut.imaxHead):
             if len(segment_tune_zone[head])>0:
                for tcc_zone_segment in xrange(0,1): #len(TP.TCS_WARP_ZONES)):
                   self.dut.dblData.Tables('P_TCC_BY_BER').addRecord({
                    'SPC_ID'              : 1, #self.dut.objSeq.curRegSPCID,
                    'OCCURRENCE'          : self.dut.objSeq.getOccurrence(),
                    'SEQ'                 : self.dut.objSeq.curSeq,
                    'TEST_SEQ_EVENT'      : self.dut.objSeq.getTestSeqEvent(0),
                    'HD_LGC_PSN'          : head,  # hd
                    'HD_PHYS_PSN'         : self.dut.LgcToPhysHdMap[head],  # hd
                    'SEGMENT'             : tcc_zone_segment,
                    'DATA_ZONE'           : segment_tune_zone[head][tcc_zone_segment],
                    'STEP' : step_count_needed[head][tcc_zone_segment],
                    'STEP_SIZE' : TP.tcc1_step_size,
                    'NEW_TCC1' : self.oAFH_Screens.oUtility.setDBPrecision(final_tcc1[head][tcc_zone_segment],0, 5),
                    'ORIG_TCC1' : self.oAFH_Screens.oUtility.setDBPrecision(List_save_default_TCC1[head][tcc_zone_segment],0, 5),
                    'TARGET_BER' : self.oAFH_Screens.oUtility.setDBPrecision(segment_target_ber[head][tcc_zone_segment],0, 5),
                    'FINAL_BER' : self.oAFH_Screens.oUtility.setDBPrecision(final_tuned_ber[head][tcc_zone_segment],0, 5),
                    'START_BER' : self.oAFH_Screens.oUtility.setDBPrecision(start_tuned_ber[head][tcc_zone_segment],0, 5),
                    'SLOPE_TYPE' : slope_type[head][tcc_zone_segment],
                    'DIRECTION' : direction[head][tcc_zone_segment],
                    'REVERT' : revert_orig_TCC1[head][tcc_zone_segment],
                    'DELTA_PRE_HEAT' : delta_pre_heater[head][tcc_zone_segment],
                    'DELTA_WRT_HEAT' : delta_write_heater[head][tcc_zone_segment],
                    'DELTA_RD_HEAT' : delta_read_heater[head][tcc_zone_segment],
                   })
      else:
          for head in xrange(self.dut.imaxHead):
             if len(segment_tune_zone[head])>0:
                self.dut.dblData.Tables('P_TCC_BY_BER').addRecord({
                    'SPC_ID'              : 1, #self.dut.objSeq.curRegSPCID,
                    'OCCURRENCE'          : self.dut.objSeq.getOccurrence(),
                    'SEQ'                 : self.dut.objSeq.curSeq,
                    'TEST_SEQ_EVENT'      : self.dut.objSeq.getTestSeqEvent(0),
                    'HD_LGC_PSN'          : head,  # hd
                    'HD_PHYS_PSN'         : self.dut.LgcToPhysHdMap[head],  # hd
                    'SEGMENT'             : tcc_zone_segment,
                    'DATA_ZONE'           : segment_tune_zone[head][tcc_zone_segment],
                    'STEP' : step_count_needed[head][tcc_zone_segment],
                    'STEP_SIZE' : TP.tcc1_step_size,
                    'NEW_TCC1' : self.oAFH_Screens.oUtility.setDBPrecision(final_tcc1[head][tcc_zone_segment],0, 5),
                    'ORIG_TCC1' :  self.oAFH_Screens.oUtility.setDBPrecision(List_save_default_TCC1[head],0, 5),
                    'TARGET_BER' : self.oAFH_Screens.oUtility.setDBPrecision(segment_target_ber[head][tcc_zone_segment],0, 5),
                    'FINAL_BER' : self.oAFH_Screens.oUtility.setDBPrecision(final_tuned_ber[head][tcc_zone_segment],0, 5),
                    'START_BER' : self.oAFH_Screens.oUtility.setDBPrecision(start_tuned_ber[head][tcc_zone_segment],0, 5),
                    'SLOPE_TYPE' : slope_type[head][tcc_zone_segment],
                    'DIRECTION' : direction[head][tcc_zone_segment],
                    'REVERT' : revert_orig_TCC1[head][tcc_zone_segment],
                    'DELTA_PRE_HEAT' : delta_pre_heater[head][tcc_zone_segment],
                    'DELTA_WRT_HEAT' : delta_write_heater[head][tcc_zone_segment],
                    'DELTA_RD_HEAT' : delta_read_heater[head][tcc_zone_segment],

                })
      if len(segment_tune_zone[head])>0:
         objMsg.printMsg("self.dut.objSeq.curRegSPCID %s"  %(str(self.dut.objSeq.curRegSPCID)))
         if DEBUG_TCC > 0:
            objMsg.printMsg("P_TCC_BY_BER %s"  %(str(self.dut.dblData.Tables('P_TCC_BY_BER'))))
         objMsg.printDblogBin(self.dut.dblData.Tables('P_TCC_BY_BER'))
      #Report coefficients
      if need_repot_coef == 'Y':
         objMsg.printMsg("###################    Final TCC slope Program to Drive    ################### ")
         oRdScrn2File.Show_P172_AFH_TC_COEF_2(spcID=30000)

      if testSwitch.ENABLE_SMART_TCS_LIMITS_DATA_COLLECTION:
         if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT == 1:
            from AFH_Screens_DH import CAFH_Screens
            self.oAFH_Screens = CAFH_Screens()
            spc_id = 2
            self.oAFH_Screens.calTempLimitBaseOnTCC(spc_id)
      ClearFailSafe()

      # Temporary  code to be remove later.
      if TP.save_to_flash != 1:
         inPrm = self.oAFH_Screens.oUtility.copy(TP.prm_errRateByZone)
         inPrm.update({'TEST_HEAD':  255, 'MAX_ERR_RATE' : -80, 'TEST_ZONES': range(self.dut.numZones), 
            'SER_raw_BER_limit': TP.prm_quickSER_250_RHO['SER_raw_BER_limit']})
         from RdWr import CRdWrScreen
         oRdWrScreen = CRdWrScreen()
         oRdWrScreen.ErrorRateMeasurement(inPrm, flawListMask=0x40, spc_id=8000, numRetries=3, retryEC=[10482] )
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

   #-------------------------------------------------------------------------------------------------------
   def ConvertDeltaDacToSlope(self, delta_dac):
      return 0

   #-------------------------------------------------------------------------------------------------------
   def get_dec_step_size(self, delta_ber):
      #objMsg.printMsg("TP.tcc1_step_size_dec %s"  %(str(TP.tcc1_step_size_dec)))
      # keys = TP.tcc1_step_size_dec.keys()
      for keys in TP.tcc1_step_size_dec.keys():
        if delta_ber >= keys[0] and delta_ber < keys[1]:
           return TP.tcc1_step_size_dec[keys]

   #-------------------------------------------------------------------------------------------------------
   def getBerAndWorkingHeaterWithTCCOn(self, testHead, testZones):
      from Process import CProcess
      oProc = CProcess()

      T250_fail = 0

      if DEBUG_TCC > 0:
         objMsg.printMsg("get ber for head %d zone %s" %( testHead, str(testZones)))

      prm_errRateByZone = TP.prm_errRateByZone.copy()
      prm_errRateByZone.update({'TEST_HEAD':  ( testHead<<8 | testHead,),})
      prm_errRateByZone['CWORD2'] =  prm_errRateByZone['CWORD2'] | 0x1000 # Display the working heater.
      try:
      #Delete RAM objects
         self.dut.dblData.delTable('P250_ERROR_RATE_BY_ZONE')
         self.dut.dblData.delTable('P172_AFH_DH_WORKING_ADAPT')
      except: pass
         
      testZoneList = []
      testZoneList.append(testZones)        
      MaskList = oProc.oUtility.convertListToZoneBankMasks(testZoneList)
      for bank, list in MaskList.iteritems():
         if list:
            prm_errRateByZone['ZONE_MASK_EXT'], prm_errRateByZone['ZONE_MASK'] = oProc.oUtility.convertListTo64BitMask(list)
            if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
               prm_errRateByZone['ZONE_MASK_BANK'] = bank
            try:
               oProc.St(prm_errRateByZone)
               berData = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').tableDataObj()
               workingHeaterData = self.dut.dblData.Tables('P172_AFH_DH_WORKING_ADAPT').tableDataObj()
            except:
               T250_fail = 1
               return (0, 0, 0, 0, T250_fail)

      import types
      if (type(berData) == types.ListType):
         berData = berData[-1]

      if (type(workingHeaterData) == types.ListType):
         workingHeaterData = workingHeaterData[-1]

      if DEBUG_TCC > 0:
         objMsg.printMsg("250 table %s" %(str(berData)))

      return (float(berData['RAW_ERROR_RATE']), int(workingHeaterData['WRITER_WRITE_HEAT']), int(workingHeaterData['READER_READ_HEAT']), int(workingHeaterData['WRITER_PRE_HEAT']), T250_fail)
   """
   {'BITS_READ_LOG10': '0.000000', 'HD_PHYS_PSN': '0', 'OCCURRENCE': 20, 'SPC_ID': 1, 'ERROR_RATE_TYPE': 'SECTOR', 'DATA_ERR_CNT': '2603', 'TEST_SEQ_EVENT': 1, 'ECC_LEVEL': '0', 'DATA_ZONE': '0', 'SEQ': 0, 'FAIL_CODE': '0', 'HD_LGC_PSN': '0', 'RAW_ERROR_RATE': '-5.587397', 'START_TRK_NUM': '11545', 'SYNC_ERR_CNT': '0', 'NUM_SOVA_ITERATIONS': '-1'}

    HD_PHYS_PSN DATA_ZONE NUM_SOVA_ITERATIONS ERROR_RATE_TYPE HD_LGC_PSN START_TRK_NUM ECC_LEVEL BITS_READ_LOG10 RAW_ERROR_RATE DATA_ERR_CNT SYNC_ERR_CNT FAIL_CODE
              0         0                  -1          SYMBOL          0          8586       255        9.001682      -4.880089        13231            0         0
              0         1                  -1          SYMBOL          0         19878       255        9.000895      -5.013810         9707            0         0
              0         2                  -1          SYMBOL          0         29742       255        9.002305      -4.879532        13267            0         0

   """

   #-------------------------------------------------------------------------------------------------------
   def get_ber_with_TCC_on(self, testHead, testZones):
      from Process import CProcess
      oProc = CProcess()

      T250_fail = 0
      objMsg.printMsg("get ber for head %d zone %s" %( testHead, str(testZones)))

      prm_errRateByZone = TP.prm_errRateByZone.copy()
      prm_errRateByZone.update({'TEST_HEAD':  ( testHead<<8 | testHead,),})
      try:
      #Delete RAM objects
         self.dut.dblData.delTable('P250_ERROR_RATE_BY_ZONE')
      except: pass
         
      testZoneList = []
      testZoneList.append(testZones)        
      MaskList = oProc.oUtility.convertListToZoneBankMasks(testZoneList)
      for bank, list in MaskList.iteritems():
         if list:
            prm_errRateByZone['ZONE_MASK_EXT'], prm_errRateByZone['ZONE_MASK'] = oProc.oUtility.convertListTo64BitMask(list)
            if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
               prm_errRateByZone['ZONE_MASK_BANK'] = bank
            try:
               oProc.St(prm_errRateByZone)
               berData = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').tableDataObj()
            except:
               T250_fail = 1
               return (0, T250_fail)

      import types
      if (type(berData) == types.ListType):
         berData = berData[-1]
      objMsg.printMsg("250 table %s" %(str(berData)))

      #for entry in berData:
      #   if int(entry["HD_PHYS_PSN"]) == testHead and int(entry['DATA_ZONE']) ==  testZones:
      #      ber = float(entry['RAW_ERROR_RATE'])
      #      return ber
      return (float(berData['RAW_ERROR_RATE']), T250_fail)
   """
   {'BITS_READ_LOG10': '0.000000', 'HD_PHYS_PSN': '0', 'OCCURRENCE': 20, 'SPC_ID': 1, 'ERROR_RATE_TYPE': 'SECTOR', 'DATA_ERR_CNT': '2603', 'TEST_SEQ_EVENT': 1, 'ECC_LEVEL': '0', 'DATA_ZONE': '0', 'SEQ': 0, 'FAIL_CODE': '0', 'HD_LGC_PSN': '0', 'RAW_ERROR_RATE': '-5.587397', 'START_TRK_NUM': '11545', 'SYNC_ERR_CNT': '0', 'NUM_SOVA_ITERATIONS': '-1'}

    HD_PHYS_PSN DATA_ZONE NUM_SOVA_ITERATIONS ERROR_RATE_TYPE HD_LGC_PSN START_TRK_NUM ECC_LEVEL BITS_READ_LOG10 RAW_ERROR_RATE DATA_ERR_CNT SYNC_ERR_CNT FAIL_CODE
              0         0                  -1          SYMBOL          0          8586       255        9.001682      -4.880089        13231            0         0
              0         1                  -1          SYMBOL          0         19878       255        9.000895      -5.013810         9707            0         0
              0         2                  -1          SYMBOL          0         29742       255        9.002305      -4.879532        13267            0         0

   """
   #-------------------------------------------------------------------------------------------------------
   def TuneTCC1ToMeetTargetBer(self, head, izone, target_ber, slope_type_ber= 'NEG_SLOPE', direction = 'INCREASE_BER', tcc_zone_segment=0, tcc_zone =0, spc_id = 1):
      if testSwitch.FE_0110575_341036_ENABLE_MEASURING_CONTACT_USING_TEST_135 == 1:
         if testSwitch.extern.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT == 1:
            from AFH_Screens_DH import CAFH_Screens
         else:
            from AFH_Screens_T135 import CAFH_Screens
      else:
         if testSwitch.extern.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT == 1:
            from AFH_Screens_DH import CAFH_Screens
         else:
            from AFH_Screens_T035 import CAFH_Screens
      #from AFH_Screens_T035 import CAFH_Screens
      from RdWr import CRdScrn2File

      #### odPES  = AFH.CdPES(TP.masterHeatPrm_11, TP.defaultOCLIM) #Instantiate dpes object.. don't allow default data
      oAFH_Screens  = CAFH_Screens()
      oRdScrn2File  = CRdScrn2File()
      ### coefs = odPES.getClrCoeff(TP.clearance_Coefficients, self.dut.PREAMP_TYPE, self.dut.AABType)
      SetFailSafe()

      ## Grab the DAC ##List_PREHEATT_default
      if not testSwitch.FE_0315271_348085_P_OPTIMIZING_TCC_BY_BER_FOR_CM_OVERLOADING:
         table_AFH_Heater = oRdScrn2File.Show_P172_AFH_HEATER(tcc_on = 1) ## TCC off
         List_WRITE_HEAT_default = oRdScrn2File.Get_Current_WriteHeat(table_AFH_Heater)
         List_READ_HEAT_default  = oRdScrn2File.Get_Current_ReadHeat(table_AFH_Heater)
         List_PREHEAT_default    = oRdScrn2File.Get_Current_PreHeat(table_AFH_Heater)
         objMsg.printMsg("List_WRITE_HEAT_default %s"%(str(List_WRITE_HEAT_default)))
         objMsg.printMsg("List_READ_HEAT_default %s"%(str(List_READ_HEAT_default)))
         objMsg.printMsg("List_PREHEAT_default %s"%(str(List_PREHEAT_default)))

      if not testSwitch.FE_0258915_348429_COMMON_TWO_TEMP_CERT:
         gap_increase_ber = 0.12
         gap_decrease_ber = -0.05
      else:
         gap_increase_ber = -0.10
         gap_decrease_ber = 0.10

      objMsg.printMsg("gap_increase_ber %s"  %(str(gap_increase_ber)))
      objMsg.printMsg("gap_decrease_ber %s"  %(str(gap_decrease_ber)))
      #objMsg.printMsg("direction = %s slope_type_ber = %s"%(str(direction), str(slope_type_ber)))
      oRdScrn2File.Show_P172_AFH_TC_COEF_2(spc_id)
      if testSwitch.extern.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT:
         List_TCC1_R, List_TCC1_W = oRdScrn2File.Get_Current_TCC1(spc_id)
         if DEBUG_TCC >0:
            objMsg.printMsg("List_TCC1_R %s"%(str(List_TCC1_R)))
            objMsg.printMsg("List_TCC1_W %s"%(str(List_TCC1_W)))
         if testSwitch.extern.FE_0157745_387179_AFH_TCS_WARP:
            Original_TCC1 = List_TCC1_W[head][tcc_zone]
         else:
            Original_TCC1 = List_TCC1_W[head]
      else:
         List_TCC1 = oRdScrn2File.Get_Current_TCC1(spc_id)
         Original_TCC1 = List_TCC1[head]
         if DEBUG_TCC >0:
            objMsg.printMsg("List_TCC1 %s"%(str(List_TCC1)))
      objMsg.printMsg("Original_TCC1 %s"%(str(Original_TCC1)))
      # Determine if the slope positive / negative AFH4


      tccber_result = {}
      #odPES.setMasterHeat(TP.masterHeatPrm_11, setMHeatOn = 1) #enable master heat
      T250_fail = 0
      tccber_result = {}
      iMaxHead = self.dut.imaxHead
      numofzone = self.dut.numZones

      tccber_result = {}
      tccber_result['TARGET_BER'] = target_ber
      tccber_result['T250_FAILED'] = 'N'
      tccber_result['BER_NON_LINEAR'] = 'N'
      tccber_result['BER_MET'] = 'N'
      tccber_result['BER_AT_START_HEATER'] = 0
      tccber_result['BER_AT_START'] = 0
      tccber_result['BER_AT_END_HEATER'] = 0
      tccber_result['STEP_COUNT']  = 0
      tccber_result['REVERT'] = 'N'
      tccber_result['DELTA_WRITE_HEATER'] = 0
      tccber_result['DELTA_READ_HEATER'] = 0
      tccber_result['DELTA_PRE_HEATER'] = 0
      heater_ber = {}

      tcc2 = 0
      objMsg.printMsg("tcc_zone_segment                  = %s"  %(str(tcc_zone_segment)))
      objMsg.printMsg("TP.tcc1_step_size                 = %s"  %(str(TP.tcc1_step_size)))
      objMsg.printMsg("TP.tcc1_step_size_dec             = %s"%(str(TP.tcc1_step_size_dec)))
      objMsg.printMsg("head %s izone %s target_ber       = %s"  %(str(head),str(izone),str(target_ber)))
      objMsg.printMsg("TP.step_to_check_delta_ber        = %s"  %(str(TP.step_to_check_delta_ber)))
      objMsg.printMsg("TP.expected_minimun_ber_increaset = %s"  %(str(TP.expected_minimun_ber_increase)))
      objMsg.printMsg("TP.delta_R2C_bigger_than_R2       = %s"%(str(TP.delta_R2C_bigger_than_R2)))

      if self.use_vbar_sova: #2D VBAR with target sova for different zn

         #target SFR varies on zone retrieved from system zone (vbar_data)
         if testSwitch.extern.FE_0164615_208705_T211_STORE_CAPABILITIES:
            from SIM_FSO import CSimpleSIMFile
            import cPickle
            from VBAR import CVbarMeasurement
            data = CSimpleSIMFile("VBAR_DATA").read()
            wpp, (tableData, colHdrData) = cPickle.loads(data)
            self.measAllZns = CVbarMeasurement()
            self.measAllZns.unserialize((tableData, colHdrData))
            #retrive target sfr of the head and zone
            target_sfr = TP.Target_SFRs[( (self.measAllZns.getRecord('TGT_SFR_IDX', head, izone)))]
         else : #not available in the system zone
            target_sfr = -2.55

         TCC_MIN_BER_NOT_COMPENSATED = abs(target_sfr) - 0.05
         ber_spec = target_sfr + 0.15

      else:
         ber_spec = TP.ber_spec
         TCC_MIN_BER_NOT_COMPENSATED = TP.TCC_MIN_BER_NOT_COMPENSATED
         
      if testSwitch.FE_0258915_348429_COMMON_TWO_TEMP_CERT:
         sign_factor = -1 # Some computations are reversed under Common 2Temp
      else:
         sign_factor = 1
         
      if abs(target_ber) < abs(ber_spec):
         minimu_spec = target_ber + 0.1 * sign_factor# Expect 0.1db poorer at CRT2, better for Common 2Temp
      else:
         minimu_spec = ber_spec

      objMsg.printMsg("TCC_MIN_BER_NOT_COMPENSATED %s"%(str(TCC_MIN_BER_NOT_COMPENSATED)))
      objMsg.printMsg("minimu_spec %s TP.ber_spec %s target_ber %s"  %(str(minimu_spec),str(ber_spec),str(target_ber)))


      objMsg.printMsg("TP.Maximum_TCC1_Step_allowed %s"  %(str(TP.Maximum_TCC1_Step_allowed)))
      objMsg.printMsg("TP.TP.Maximum_TCC1_Step_allowed_for_dec %s"  %(str(TP.Maximum_TCC1_Step_allowed_for_dec)))

      if direction == 'INCREASE_BER':
         maximum_step_allowed = TP.Maximum_TCC1_Step_allowed
      else:
         maximum_step_allowed = TP.Maximum_TCC1_Step_allowed_for_dec

      objMsg.printMsg("maximum_step_allowed %s"  %(str(maximum_step_allowed)))

      ber = 0
      previous_ber = 0
      previous_new_TCC1 = 0
      step_size_for_increase = TP.tcc1_step_size
      step_size_for_decrease = TP.tcc1_step_size
      delta_ber = 0.0


      new_TCC1 = Original_TCC1
      delta_ber_inc = 0
      delta_ber_dec = 0
      ber_at_step_zero = 0

      delta_WRITE_HEAT = 0
      delta_READ_HEAT  = 0
      delta_PREHEAT    = 0
      prev_delta_WRITE_HEAT = 0
      prev_delta_READ_HEAT  = 0
      prev_delta_PREHEAT    = 0

      #trunk code FE_0139388_341036_AFH_DUAL_HEATER_V32_ABOVE was cleaned and default true
      if not (testSwitch.TRUNK_BRINGUP or testSwitch.ROSEWOOD7): # should be removed if FE_0139388_341036_AFH_DUAL_HEATER_V32_ABOVE=1 always to avoid confusion
          if (testSwitch.extern.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT == 1)and testSwitch.extern.FE_0139388_341036_AFH_DUAL_HEATER_V32_ABOVE:
             TCS1_USL     = TP.tcc_DH_dict_178 ['WRITER_HEATER']['TCS1_USL'] # in angtrom/C
             TCS1_LSL     = TP.tcc_DH_dict_178 ['WRITER_HEATER']['TCS1_LSL']  # in angtrom/C
             default_TCS1 = TP.tcc_DH_dict_178 ['WRITER_HEATER']['TCS1']        # in angtrom/C
          else:
             TCS1_USL     = TP.tccDict_178['TCS1_USL']*254.0     #convert  uinch/C to angtrom/C
             TCS1_LSL     = TP.tccDict_178['TCS1_LSL'] *254.0     # convert  uinch/C to angtrom/C
             default_TCS1 = TP.tccDict_178['TCS1']*254.0           # convert  uinch/C to angtrom/C
      else:
          if (testSwitch.extern.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT == 1):
             TCS1_USL     = TP.tcc_DH_dict_178 ['WRITER_HEATER']['TCS1_USL'] # in angtrom/C
             TCS1_LSL     = TP.tcc_DH_dict_178 ['WRITER_HEATER']['TCS1_LSL']  # in angtrom/C
             default_TCS1 = TP.tcc_DH_dict_178 ['WRITER_HEATER']['TCS1']        # in angtrom/C
          else:
             TCS1_USL     = TP.tccDict_178['TCS1_USL']*254.0     #convert  uinch/C to angtrom/C
             TCS1_LSL     = TP.tccDict_178['TCS1_LSL'] *254.0     # convert  uinch/C to angtrom/C
             default_TCS1 = TP.tccDict_178['TCS1']*254.0           # convert  uinch/C to angtrom/C

      objMsg.printMsg("TCS1_USL = %f TCS1_LSL = %f default_TCS1 = %f"  %(TCS1_USL,TCS1_LSL,default_TCS1))
      if testSwitch.ENABLE_SMART_TCS_LIMITS:
         objMsg.printMsg("TCS1_USL = %f TCS1_LSL = %f default_TCS1 = %f"  %(TCS1_USL,TCS1_LSL,default_TCS1))            
         tcc1_loLimitWrtHt, tcc1_upLimitWrtHt = oAFH_Screens.SmartTccLimits()
         if TCS1_USL > tcc1_upLimitWrtHt[head]:
            TCS1_USL = tcc1_upLimitWrtHt[head]
         if TCS1_LSL < tcc1_loLimitWrtHt[head]:
            TCS1_LSL = tcc1_loLimitWrtHt[head]  
         if default_TCS1 > TCS1_USL:
            default_TCS1 = TCS1_USL
         elif default_TCS1 < TCS1_LSL:
            default_TCS1 = TCS1_LSL
         objMsg.printMsg("TCS1_USL_ADJ = %f TCS1_LSL_ADJ = %f ADJ_TCS1 = %f"  %(TCS1_USL,TCS1_LSL,default_TCS1))  

      for step_count in xrange(0, maximum_step_allowed):

         T250_fail = 0


         objMsg.printMsg("####  Tweaking the tcc1 Slope: step_count %s, new_TCC1 %s, Direction %s, slope_type_ber = %s   ####"  %(str(step_count),str(new_TCC1),str(direction), str(slope_type_ber)))
         objMsg.printMsg("step_size_for_decrease = %s step_size_for_increase = %s"  %(str(step_size_for_decrease),str(step_size_for_increase)))
         # Save the new TCC1 to the drive #########
         if testSwitch.extern.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT == 1:
            from RAP import ClassRAP
            objRAP = ClassRAP()
            if testSwitch.FE_0169232_341036_ENABLE_AFH_TGT_CLR_CANON_PARAMS == 1:
               from AFH_canonParams import *
               tcc_DH_values = getTCS_values()
            else:
               tcc_DH_values = TP.tcc_DH_values
            if not testSwitch.extern.FE_0157745_387179_AFH_TCS_WARP:
               if self.dut.isDriveDualHeater==1: # dual heater drive
                  objRAP.SaveTCC_toRAP( head, new_TCC1, tcc2, "WRITER_HEATER",tcc_DH_values)
                  #objRAP.SaveTCC_toRAP( iHead, TP.tcc_DH_dict_178["READER_HEATER"]['TCS1'], TP.tcc_DH_dict_178["READER_HEATER"]['TCS2'], "READER_HEATER" )
               else:     # single heater drive
                  objRAP.SaveTCC_toRAP( head, new_TCC1, tcc2, "WRITER_HEATER",tcc_DH_values)
                  objRAP.SaveTCC_toRAP( head, new_TCC1, tcc2, "READER_HEATER",tcc_DH_values)
            else:
               if  self.dut.isDriveDualHeater==1: # dual heater drive
                  if testSwitch.FE_AFH_RSQUARE_TCC: 
                     objRAP.SaveTCC_toRAP( head, new_TCC1, tcc2, "WRITER_HEATER",tcc_DH_values,  [tcc_zone_segment, ] ) #tcc_rsq
                  else:
                     objRAP.SaveTCC_toRAP( head, new_TCC1, tcc2, "WRITER_HEATER",tcc_DH_values, TP.TCS_WARP_ZONES.keys() ) #tcc_rsq
               else:     # single heater drive
                  if testSwitch.FE_AFH_RSQUARE_TCC: 
                     objRAP.SaveTCC_toRAP( head, new_TCC1, tcc2, "WRITER_HEATER", [tcc_zone_segment, ])
                  else:
                     objRAP.SaveTCC_toRAP( head, new_TCC1, tcc2, "WRITER_HEATER",tcc_DH_values,TP.TCS_WARP_ZONES.keys())
                     objRAP.SaveTCC_toRAP( head, new_TCC1, tcc2, "READER_HEATER",tcc_DH_values,TP.TCS_WARP_ZONES.keys())
         else:
            if not testSwitch.extern.FE_0157745_387179_AFH_TCS_WARP:
               oAFH_Screens.SaveTCC( head, new_TCC1, tcc2 )
            else:
               oAFH_Screens.SaveTCC( head, new_TCC1, tcc2, tcc_zone_segment )

         objMsg.printMsg("Read back P172_AFH_TC_COEF_2 for the new_TCC1 %s for head %d step_count = %s"  %(str(new_TCC1),head,str(step_count)))
         oRdScrn2File.Show_P172_AFH_TC_COEF_2()
         previous_ber = ber
         if testSwitch.FE_0315271_348085_P_OPTIMIZING_TCC_BY_BER_FOR_CM_OVERLOADING:
            objMsg.printMsg("step_count => %d head = %d zone = %s"  %(step_count, head, str(izone) ))
            ber, writer_write_heat, reader_read_heat, writer_pre_heat,  T250_fail = self.getBerAndWorkingHeaterWithTCCOn(head, izone)
         else:
            ber, T250_fail = self.get_ber_with_TCC_on(head, izone)
         if step_count == 0:
             if testSwitch.FE_0315271_348085_P_OPTIMIZING_TCC_BY_BER_FOR_CM_OVERLOADING:
                initial_writer_write_heat = writer_write_heat
                initial_reader_read_heat  = reader_read_heat
                initial_writer_pre_heat   = writer_pre_heat
             tccber_result['BER_AT_START'] = ber
             ber_at_step_zero = ber

         tccber_result['tcc1_slope'] = new_TCC1
         if T250_fail:
            objMsg.printMsg("T250 Failed for head %d zone %d new_TCC1 %d"  %(head, izone, new_TCC1))
            tccber_result['T250_FAILED'] = 'Y'
            break
         else:
            heater_ber[step_count] = ber
            tccber_result['STEP_COUNT'] = step_count
            tccber_result['BER_AT_END_HEATER'] = ber

         if not testSwitch.FE_0315271_348085_P_OPTIMIZING_TCC_BY_BER_FOR_CM_OVERLOADING:
            table_AFH_Heater = oRdScrn2File.Show_P172_AFH_HEATER(tcc_on = 1) ## TCC off
            List_WRITE_HEAT  = oRdScrn2File.Get_Current_WriteHeat(table_AFH_Heater)
            List_READ_HEAT   = oRdScrn2File.Get_Current_ReadHeat(table_AFH_Heater)
            List_PREHEAT     = oRdScrn2File.Get_Current_PreHeat(table_AFH_Heater)

         if direction == 'DECREASE_BER':
            delta_ber = abs(ber) - abs(target_ber)

            prev_delta_WRITE_HEAT = delta_WRITE_HEAT
            prev_delta_READ_HEAT  = delta_READ_HEAT
            prev_delta_PREHEAT    = delta_PREHEAT

            if testSwitch.FE_0315271_348085_P_OPTIMIZING_TCC_BY_BER_FOR_CM_OVERLOADING:
               delta_WRITE_HEAT = initial_writer_write_heat - writer_write_heat
               delta_READ_HEAT  = initial_reader_read_heat  - reader_read_heat
               delta_PREHEAT    = initial_writer_pre_heat   - writer_pre_heat
            else:
               delta_WRITE_HEAT = List_WRITE_HEAT_default[head*(self.dut.numZones) + izone] - List_WRITE_HEAT[head*(self.dut.numZones) + izone]
               delta_READ_HEAT  = List_READ_HEAT_default[head*(self.dut.numZones) + izone]  - List_READ_HEAT[head*(self.dut.numZones) + izone]
               delta_PREHEAT    = List_PREHEAT_default[head*(self.dut.numZones) + izone]    - List_PREHEAT[head*(self.dut.numZones) + izone]


            tccber_result['DELTA_WRITE_HEATER'] = delta_WRITE_HEAT
            tccber_result['DELTA_READ_HEATER'] = delta_READ_HEAT
            tccber_result['DELTA_PRE_HEATER'] = delta_PREHEAT

            #objMsg.printMsg("Head %d Zone %d (head*(self.dut.numZones+1) + izone)= %s self.dut.numZones %s "  %(head, izone, str(head*(self.dut.numZones+1) + izone),  str(self.dut.numZones)))
            if not testSwitch.FE_0315271_348085_P_OPTIMIZING_TCC_BY_BER_FOR_CM_OVERLOADING:
               objMsg.printMsg("Head %d Zone %d List_WRITE_HEAT_default %s List_READ_HEAT_default %s List_PREHEAT_default %s "  %(head, izone, str(List_WRITE_HEAT_default[head*(self.dut.numZones) + izone]),  str(List_READ_HEAT_default[head*(self.dut.numZones) + izone]),str(List_PREHEAT_default[head*(self.dut.numZones) + izone])))
               objMsg.printMsg("Head %d Zone %d List_WRITE_HEAT %s List_READ_HEAT %s List_PREHEAT %s "  %(head, izone, str(List_WRITE_HEAT[head*(self.dut.numZones) + izone]),  str(List_READ_HEAT[head*(self.dut.numZones) + izone]),str(List_PREHEAT[head*(self.dut.numZones) + izone])))
            objMsg.printMsg("Head = %d Zone = %d delta_WRITE_HEAT = %s delta_READ_HEAT = %s delta_PREHEAT = %s "  %(head, izone, str(delta_WRITE_HEAT),  str(delta_READ_HEAT),str(delta_PREHEAT)))

         elif direction == 'INCREASE_BER':
            delta_ber = abs(target_ber)-abs(ber)

            prev_delta_WRITE_HEAT = delta_WRITE_HEAT
            prev_delta_READ_HEAT  = delta_READ_HEAT
            prev_delta_PREHEAT    = delta_PREHEAT

            if testSwitch.FE_0315271_348085_P_OPTIMIZING_TCC_BY_BER_FOR_CM_OVERLOADING:
               delta_WRITE_HEAT = writer_write_heat - initial_writer_write_heat
               delta_READ_HEAT  = reader_read_heat - initial_reader_read_heat
               delta_PREHEAT    = writer_pre_heat - initial_writer_pre_heat
            else:
               delta_WRITE_HEAT = List_WRITE_HEAT[head*(self.dut.numZones) + izone] - List_WRITE_HEAT_default[head*(self.dut.numZones) + izone]
               delta_READ_HEAT  = List_READ_HEAT[head*(self.dut.numZones) + izone]  - List_READ_HEAT_default[head*(self.dut.numZones) + izone]
               delta_PREHEAT    = List_PREHEAT[head*(self.dut.numZones) + izone]    - List_PREHEAT_default[head*(self.dut.numZones) + izone]


            tccber_result['DELTA_WRITE_HEATER'] = delta_WRITE_HEAT
            tccber_result['DELTA_READ_HEATER'] = delta_READ_HEAT
            tccber_result['DELTA_PRE_HEATER'] = delta_PREHEAT
            objMsg.printMsg("Head %d Zone %d (head*(self.dut.numZones+1) + izone)= %s self.dut.numZones %s "  %(head, izone, str(head*(self.dut.numZones) + izone),  str(self.dut.numZones)))
            if not testSwitch.FE_0315271_348085_P_OPTIMIZING_TCC_BY_BER_FOR_CM_OVERLOADING:
                objMsg.printMsg("Head %d Zone %d List_WRITE_HEAT_default %s List_READ_HEAT_default %s List_PREHEAT_default %s "  %(head, izone, str(List_WRITE_HEAT_default[head*(self.dut.numZones) + izone]),  str(List_READ_HEAT_default[head*(self.dut.numZones) + izone]),str(List_PREHEAT_default[head*(self.dut.numZones) + izone])))
                objMsg.printMsg("Head %d Zone %d List_WRITE_HEAT %s List_READ_HEAT %s List_PREHEAT %s "  %(head, izone, str(List_WRITE_HEAT[head*(self.dut.numZones) + izone]),  str(List_READ_HEAT[head*(self.dut.numZones) + izone]),str(List_PREHEAT[head*(self.dut.numZones) + izone])))
            objMsg.printMsg("Head %d Zone %d delta_WRITE_HEAT %s delta_READ_HEAT %s delta_PREHEAT %s "  %(head, izone, str(delta_WRITE_HEAT),  str(delta_READ_HEAT),str(delta_PREHEAT)))

            if delta_WRITE_HEAT >= TP.maximum_delta_writer_heat:
               tccber_result['tcc1_slope']         = new_TCC1 + step_size_for_increase  * sign_factor
               tccber_result['STEP_COUNT']         = step_count  - 1
               tccber_result['DELTA_WRITE_HEATER'] = prev_delta_WRITE_HEAT
               tccber_result['DELTA_READ_HEATER']  = prev_delta_READ_HEAT
               tccber_result['DELTA_PRE_HEATER']   = prev_delta_PREHEAT
               objMsg.printMsg("INCREASE_BER:Exceeding Maximum delta DAC allowed (TP.maximum_delta_writer_heat = %s) .Revert to previous TCC1  head %d zone %d new_TCC1 from %s revert to %s"  %(str(TP.maximum_delta_writer_heat),head, izone, str(new_TCC1),str(tccber_result['tcc1_slope'])))
               break;


         if direction == 'INCREASE_BER':
            # Check at step 0 if the worst zone ber already too good.
            if ((step_count == 0) and (abs(ber) >= TCC_MIN_BER_NOT_COMPENSATED)):
               # Revert back to original TCC1 as the increment of delta is not significant
               new_TCC1 = Original_TCC1
               tccber_result['STEP_COUNT']        = 0
               tccber_result['tcc1_slope']        = new_TCC1
               tccber_result['REVERT'] = 'Y'
               tccber_result['BER_AT_END_HEATER'] = ber_at_step_zero
               tccber_result['DELTA_WRITE_HEATER'] = 0
               tccber_result['DELTA_READ_HEATER'] = 0
               tccber_result['DELTA_PRE_HEATER'] = 0
               objMsg.printMsg("No TCC_BY_BER tuning at head = %d zone = %d new_TCC1 = %s as the BER too good!!!"  %(head, izone, str(new_TCC1)))
               break

            # Check if the delta ber
            delta_ber_inc = abs(ber)-abs(ber_at_step_zero)
            objMsg.printMsg("===>>> Step %s head %d zone %d delta_ber_inc %s ber_at_step_zero %s TP.expected_minimun_ber_increase %s TP.step_to_check_delta_ber %s"  %(str(step_count), head, izone, str(delta_ber_inc),str(ber_at_step_zero),str(TP.expected_minimun_ber_increase),str(TP.step_to_check_delta_ber)))
            if ((step_count == TP.step_to_check_delta_ber) and (delta_ber_inc < TP.expected_minimun_ber_increase)):
               # Revert back to original TCC1 as the increment of delta is not significant
               new_TCC1 = Original_TCC1
               tccber_result['STEP_COUNT']        = 0
               tccber_result['tcc1_slope']        = new_TCC1
               tccber_result['REVERT'] = 'Y'
               tccber_result['BER_AT_END_HEATER'] = ber_at_step_zero
               tccber_result['DELTA_WRITE_HEATER'] = 0
               tccber_result['DELTA_READ_HEATER'] = 0
               tccber_result['DELTA_PRE_HEATER'] = 0
               objMsg.printMsg("Revert back the original TCC1 as BER increment is insignificant at head = %d zone = %d new_TCC1 = %s"  %(head, izone, str(new_TCC1)))
               break

         elif direction == 'DECREASE_BER':
            delta_ber_dec = abs(ber_at_step_zero) - abs(ber)
            objMsg.printMsg("===>>> Step %s head %d zone %d delta_ber_dec %s ber_at_step_zero %s TP.expected_minimun_ber_increase %s TP.step_to_check_delta_ber %s"  %(str(step_count), head, izone, str(delta_ber_dec),str(ber_at_step_zero),str(TP.expected_minimun_ber_increase),str(TP.step_to_check_delta_ber)))
            if ((step_count == TP.step_to_check_delta_ber) and (delta_ber_dec < TP.expected_minimun_ber_increase)):
               # Revert back to original TCC1 as the increment of delta is not significant
               new_TCC1 = Original_TCC1
               tccber_result['STEP_COUNT']        = 0
               tccber_result['tcc1_slope']        = new_TCC1
               tccber_result['REVERT'] = 'Y'
               tccber_result['BER_AT_END_HEATER'] = ber_at_step_zero
               tccber_result['DELTA_WRITE_HEATER'] = 0
               tccber_result['DELTA_READ_HEATER'] = 0
               tccber_result['DELTA_PRE_HEATER'] = 0
               objMsg.printMsg("Revert back the original TCC1 as BER decrement is insignificant at head = %d zone = %d new_TCC1 = %s"  %(head, izone, str(new_TCC1)))
               break
         if (direction == 'INCREASE_BER' and slope_type_ber == 'NEG_SLOPE' and ( ((abs(target_ber)-abs(ber))<= gap_increase_ber) ) ):
            objMsg.printMsg("INCREASE_BER/NEGATIVE_SLOPE: Ber met for head %d zone %d ber %s target_ber %s tune_TCC1 %s step_count %s delta_ber %s"  %(head, izone, str(ber),str(target_ber), str(new_TCC1),str(step_count),str((abs(ber)-abs(target_ber)))))

            tccber_result['BER_MET'] = 'Y'
            tccber_result['BER_AT_END_HEATER'] = ber
            tccber_result['STEP_COUNT'] = step_count
            tccber_result['tcc1_slope']        = new_TCC1
            break
         elif (direction == 'DECREASE_BER' and slope_type_ber == 'NEG_SLOPE' and ( ((abs(ber) - abs(target_ber)) <= gap_decrease_ber) or (abs(ber)<= abs(minimu_spec)))):
            objMsg.printMsg("DECREASE_BER/NEGATIVE_SLOPE: Ber met for head %d zone %d ber %s target_ber %s tune_TCC1 %s step_count %s delta_ber %s"  %(head, izone, str(ber),str(target_ber), str(new_TCC1),str(step_count),str((abs(ber)-abs(target_ber)))))
            tccber_result['BER_MET'] = 'Y'
            objMsg.printMsg("delta_ber = %s, ber %s target_ber %s "  %(str(delta_ber), str(abs(ber)), str(target_ber)))
            if (abs(ber)<= abs(minimu_spec)):
               if (step_count != 0):
                  tccber_result['BER_AT_END_HEATER'] = previous_ber
                  tccber_result['tcc1_slope']     = new_TCC1 - step_size_for_decrease * sign_factor
                  tccber_result['STEP_COUNT'] = step_count  - 1
                  tccber_result['DELTA_WRITE_HEATER'] = prev_delta_WRITE_HEAT
                  tccber_result['DELTA_READ_HEATER']  = prev_delta_READ_HEAT
                  tccber_result['DELTA_PRE_HEATER']   = prev_delta_PREHEAT
                  objMsg.printMsg("DECREASE_BER/NEGATIVE_SLOPE: Revert to previous TCC1  head %d zone %d new_TCC1 %s"  %(head, izone, str(new_TCC1)))
                  objMsg.printMsg("step_count %s new_TCC1 %s"  %(str(step_count),str(new_TCC1)))
               else:
                  tccber_result['BER_AT_END_HEATER'] = ber
                  tccber_result['STEP_COUNT'] = step_count
                  tccber_result['tcc1_slope']        = new_TCC1
            else:
               tccber_result['BER_AT_END_HEATER'] = ber
               tccber_result['STEP_COUNT']        = step_count
               tccber_result['tcc1_slope']        = new_TCC1
            break
         elif (direction == 'INCREASE_BER' and slope_type_ber == 'POS_SLOPE' and ( ((abs(target_ber)-abs(ber))<= gap_increase_ber) ) ):
            objMsg.printMsg("INCREASE_BER:POSITIVE_SLOPE: Ber met for head %d zone %d ber %s target_ber %s tune_TCC1 %s step_count %s delta_ber %s"  %(head, izone, str(ber),str(target_ber), str(new_TCC1),str(step_count),str((abs(ber)-abs(target_ber)))))
            tccber_result['BER_MET'] = 'Y'
            tccber_result['BER_AT_END_HEATER'] = ber
            tccber_result['STEP_COUNT']        = step_count
            tccber_result['tcc1_slope']        = new_TCC1
            break
         elif (direction == 'DECREASE_BER' and slope_type_ber == 'POS_SLOPE' and ( ((abs(ber) - abs(target_ber)) <= gap_decrease_ber) or (abs(ber)<= abs(minimu_spec)))):
            objMsg.printMsg("DECREASE_BER/POSITIVE_SLOPE: Ber met for head %d zone %d ber %s target_ber %s tune_TCC1 %s step_count %s delta_ber %s"  %(head, izone, str(ber),str(target_ber), str(new_TCC1),str(step_count),str((abs(ber)-abs(target_ber)))))
            tccber_result['BER_MET'] = 'Y'
            if (abs(ber)<= abs(minimu_spec)):
               if (step_count != 0):
                  tccber_result['BER_AT_END_HEATER'] = previous_ber
                  tccber_result['tcc1_slope']      = new_TCC1 - step_size_for_decrease * sign_factor
                  tccber_result['STEP_COUNT'] = step_count  - 1
                  tccber_result['DELTA_WRITE_HEATER'] = prev_delta_WRITE_HEAT
                  tccber_result['DELTA_READ_HEATER']  = prev_delta_READ_HEAT
                  tccber_result['DELTA_PRE_HEATER']   = prev_delta_PREHEAT
                  objMsg.printMsg("DECREASE_BER/POSITIVE_SLOPE: Revert to previous TCC1  head %d zone %d new_TCC1 %s"  %(head, izone, str(new_TCC1)))
                  objMsg.printMsg("step_count %s new_TCC1 %s"  %(str(step_count),str(new_TCC1)))
               else:
                  tccber_result['BER_AT_END_HEATER'] = ber
                  tccber_result['STEP_COUNT'] = step_count
                  tccber_result['tcc1_slope']        = new_TCC1
            else:
               tccber_result['BER_AT_END_HEATER'] = ber
               tccber_result['STEP_COUNT']        = step_count
               tccber_result['tcc1_slope']        = new_TCC1
            break

         # Multiple step size
         if step_count != (maximum_step_allowed -1):
             ##step_size_for_decrease = self.get_dec_step_size(delta_ber) # disable
             objMsg.printMsg("step_size_for_decrease = %s delta_ber = %s"  %(str(step_size_for_decrease),str(delta_ber)))
             if direction == 'INCREASE_BER' and slope_type_ber == 'NEG_SLOPE':
                new_TCC1 = new_TCC1 - (step_size_for_increase * sign_factor)
             elif direction == 'DECREASE_BER' and slope_type_ber == 'NEG_SLOPE':
                new_TCC1 = new_TCC1 + (step_size_for_decrease * sign_factor)
             elif direction == 'INCREASE_BER' and slope_type_ber == 'POS_SLOPE':
                new_TCC1 = new_TCC1 - (step_size_for_increase)
             elif direction == 'DECREASE_BER' and slope_type_ber == 'POS_SLOPE':
                new_TCC1 = new_TCC1 + (step_size_for_decrease)

         if new_TCC1 > TCS1_USL or new_TCC1 < TCS1_LSL:
             objMsg.printMsg("Revert back the original TCC1 as the TC1 = %f out of the TCS1_USL %f and TCS1_LSL %f"  %(new_TCC1,TCS1_USL,TCS1_LSL))
             new_TCC1 = Original_TCC1
             tccber_result['STEP_COUNT']         = 0
             tccber_result['tcc1_slope']         = new_TCC1
             tccber_result['REVERT']             = 'Y'
             tccber_result['BER_AT_END_HEATER']  = ber_at_step_zero
             tccber_result['DELTA_WRITE_HEATER'] = 0
             tccber_result['DELTA_READ_HEATER']  = 0
             tccber_result['DELTA_PRE_HEATER']   = 0
             break

      else:
         tccber_result['STEP_COUNT']        = step_count
         tccber_result['tcc1_slope']        = new_TCC1
      return Original_TCC1, tccber_result

   #-------------------------------------------------------------------------------------------------------
   def GetDACToMeetTargetBer(self, head, izone, target_ber):
      from RdWr import CRdScrn2File
      from AFH import CdPES
      oTccBERCalibration = CTccBERCalibration(self.dut)
      odPES  = CdPES(TP.masterHeatPrm_11, TP.defaultOCLIM) #Instantiate dpes object.. don't allow default data
      oRdScrn2File  = CRdScrn2File()
      coefs = odPES.getClrCoeff(TP.clearance_Coefficients, self.dut.PREAMP_TYPE, self.dut.AABType)
      SetFailSafe()
      table_AFH_Heater = oRdScrn2File.Show_P172_AFH_HEATER()
      List_WRITE_HEAT = oRdScrn2File.Get_Current_WriteHeat(table_AFH_Heater)
      List_READ_HEAT  = oRdScrn2File.Get_Current_ReadHeat(table_AFH_Heater)
      List_PREHEAT = oRdScrn2File.Get_Current_PreHeat(table_AFH_Heater)
      objMsg.printMsg("List_WRITE_HEAT %s"%(str(List_WRITE_HEAT)))
      objMsg.printMsg("List_READ_HEAT %s"%(str(List_READ_HEAT)))
      objMsg.printMsg("List_PREHEAT %s"%(str(List_PREHEAT)))
      tccber_result = {}
      dac_work_dict = {}
      clr_dict = {}
      odPES.setMasterHeat(TP.masterHeatPrm_11, setMHeatOn = 1) #enable master heat
      T250_fail = 0
      tccber_result = {}
      clr_dict = {}
      iMaxHead = self.dut.imaxHead
      numofzone = self.dut.numZones
      #List_zone =  [0, 4, 21, 23]
      dac_org=[]
      dac_work_dict=[]
      startheater_backoff = 5
      dac_org.append( List_WRITE_HEAT[(head*numofzone)+izone])
      dac_work_dict.append( List_WRITE_HEAT[(head*numofzone)+izone])
      max_CD_inc = 2


      tccber_result = {}
      tccber_result['AFH4_CD'] = 0
      tccber_result['AFH2_WORKING_HEATER'] = List_WRITE_HEAT[(head*numofzone)+izone]
      tccber_result['TCCBER_START_HEATER'] = List_WRITE_HEAT[(head*numofzone)+izone] - startheater_backoff
      tccber_result['TCCBER_HEATER_LIMIT'] = List_WRITE_HEAT[(head*numofzone)+izone] + max_CD_inc
      tccber_result['TARGET_BER'] = target_ber
      tccber_result['T250_FAILED'] = 'N'
      tccber_result['BER_NON_LINEAR'] = 'N'
      tccber_result['BER_MET'] = 'N'
      tccber_result['BER_AT_START_HEATER'] = 0
      tccber_result['BER_AT_END_HEATER'] = 0
      tccber_result['delta_DAC'] = 0
      heater_ber = {}
      for WorkHTROffset in xrange(1,max_CD_inc + startheater_backoff,1):
         T250_fail = 0
         WH = List_WRITE_HEAT[(head*numofzone)+izone] + WorkHTROffset - startheater_backoff
         RH = List_READ_HEAT[(head*numofzone)+izone]
         PH = List_PREHEAT[(head*numofzone)+izone]
         objMsg.printMsg("WH %s RH %s PH %s"  %(str(WH), str(RH), str(PH)))
         odPES.setWorkingHeaters(izone, head, WH, RH, PH)
         ber, T250_fail = oTccBERCalibration.get_ber(head, izone)
         tccber_result['TCCBER_END_HEATER'] = WH
         tccber_result['delta_DAC']         = List_WRITE_HEAT[(head*numofzone)+izone] - tccber_result['TCCBER_END_HEATER']
         if T250_fail:
            WorkHTROffset = WorkHTROffset - 1
            objMsg.printMsg("T250 Failed for head %d zone %d offset %d"  %(head, izone, WorkHTROffset+1))
            dac_work_dict =  WH - 1
            tccber_result['T250_FAILED'] = 'Y'
            break
         else:
            heater_ber[WH] = ber
            tccber_result['BER_AT_END_HEATER'] = ber
            if WorkHTROffset == 1:
               tccber_result['BER_AT_START_HEATER'] = ber
            ber_chk_fail, max_ber_heater = oTccBERCalibration.chk_ber(heater_ber)
            if ber_chk_fail:
               dac_work_dict = max_ber_heater
               objMsg.printMsg("heat-ber linearity check failed for head %d zone %d heater-ber %s select heater %d"  %(head, izone, str(heater_ber), max_ber_heater))
               tccber_result['BER_NON_LINEAR'] = 'Y'
               tccber_result['TCCBER_END_HEATER'] = WH
               tccber_result['delta_DAC']         = List_WRITE_HEAT[(head*numofzone)+izone] - tccber_result['TCCBER_END_HEATER']
               break;
         #meet #abs(ber - List_RdScrn2_BER[ head*numofzone + izone]) < 0.2: #meet
         if (WorkHTROffset - startheater_backoff <= 5 and (abs(ber) - abs(target_ber)) >= 0) or \
            ((WorkHTROffset - startheater_backoff <= 2) and (WorkHTROffset - startheater_backoff > 5) and \
            (abs(ber - target_ber) < 0.2)) or ((WorkHTROffset - startheater_backoff > 2)  and (abs(ber - target_ber) < 0.3)):

            objMsg.printMsg("Ber met for head %d zone %d offset %d"  %(head, izone, WorkHTROffset))
            tccber_result['BER_MET'] = 'Y'
            dac_work_dict =  WH
            tccber_result['TCCBER_END_HEATER'] = WH
            tccber_result['BER_AT_END_HEATER'] = ber
            tccber_result['delta_DAC']         = List_WRITE_HEAT[(head*numofzone)+izone] - tccber_result['TCCBER_END_HEATER']
            break
      else:
         dac_work_dict =  List_WRITE_HEAT[(head*numofzone)+izone] + 2
         tccber_result['TCCBER_END_HEATER'] = dac_work_dict
         tccber_result['delta_DAC']         = List_WRITE_HEAT[(head*numofzone)+izone] - tccber_result['TCCBER_END_HEATER']

      return tccber_result

   #-------------------------------------------------------------------------------------------------------
   def getWorstBerZone(self, ber_list = [], start_zone=0,end_zone=23):
      if DEBUG_TCC > 0:
         objMsg.printMsg("ber_list %s"%(str(ber_list)))
      worst_ber  = min(ber_list)
      for zone in xrange(start_zone,(end_zone+1)):
         if testSwitch.FE_0257006_348085_EXCLUDE_UMP_FROM_TCC_BY_BER:
            if zone in TP.UMP_ZONE[self.dut.numZones]:
               continue
         if ber_list[zone] > worst_ber and ber_list[zone] < 0:
            worst_ber = ber_list[zone]
            worst_zone = zone
      objMsg.printMsg("Pick Worst_zone = %s of Worst_ber = %s to Optimize"%(str(worst_zone), str(worst_ber)))
      return worst_zone, worst_ber

   #-------------------------------------------------------------------------------------------------------
   def DriveSlopeByBer(self, r2a_ber_list = [], r2_ber_list = [], head = 0, start_zone=0, end_zone=0):
      if DEBUG_TCC > 0:
         objMsg.printMsg("r2a_ber_list %s"%(str(r2a_ber_list))) # cold
         objMsg.printMsg("r2_ber_list %s"%(str(r2_ber_list)))   # hot

      delta_ber = abs(mean(r2_ber_list[head][start_zone:(end_zone+1)])) - abs(mean(r2a_ber_list[head][start_zone:(end_zone+1)]))
      if DEBUG_TCC > 0:
         objMsg.printMsg("Head %s zone %s to %s Delta_ber(Avg_r2 - Avg_r2a) = %s avg_r2_ber_list = %s avg_r2a_ber_list = %s"%(str(head),str(start_zone),str(end_zone),str(delta_ber),str(mean(r2_ber_list[head])),str(mean(r2a_ber_list[head]))))

      if delta_ber < 0: # positive slope
         slope = 'POSITIVE_SLOPE'
      else:             # negative slope
         slope = 'NEGATIVE_SLOPE'
      return slope

   #-------------------------------------------------------------------------------------------------------
   def DriveSlopeByAFH4(self, tcc1):
      objMsg.printMsg("tcc1 %s"%(str(tcc1))) #
      if tcc1 > 0: # positive slope
         slope = 'POSITIVE_SLOPE'
      else:             # negative slope
         slope = 'NEGATIVE_SLOPE'
      return slope

   #-------------------------------------------------------------------------------------------------------
   def ExamineTCC1slopeByBer(self, r2c_ber_list = [], r2_ber_list = [], head = 0, start_zone =0, end_zone=0):
      if DEBUG_TCC:
         objMsg.printMsg("r2c_ber_list %s"%(str(r2c_ber_list))) # cold
         objMsg.printMsg("r2_ber_list %s"%(str(r2_ber_list)))   # hot

      delta_ber = abs(mean(r2c_ber_list[head][start_zone:(end_zone+1)])) - abs(mean(r2_ber_list[head][start_zone:(end_zone+1)]))

      #objMsg.printMsg("Head %s zone %s to %s Delta_ber(Avg_r2c - Avg_r2) = %s avg_r2c_ber_list = %s avg_r2_ber_list = %s"%(str(head),str(start_zone),str(end_zone),str(delta_ber),str(mean(r2c_ber_list[head])),str(mean(r2_ber_list[head]))))
      objMsg.printMsg("***Head %s zone %s to zone %s, Delta_ber(abs(Avg_r2c) - abs(Avg_r2)) = %s***"%(str(head),str(start_zone),str(end_zone),str(delta_ber)))

      if delta_ber > 0: #
         slope = 'OVER_COMPENSATE'
         objMsg.printMsg("slope performance: %s => Avg BER of R2c > Avg BER of R2"%(str(slope)))
         if delta_ber > TP.delta_R2C_bigger_than_R2 and not testSwitch.RESET_TCC1_SLOPE_IF_BOTH_TCC1_AND_BER_OVER_SPEC: #0.4:
            # reset to default.
            ScrCmds.raiseException(48448, "TCC1 slope is Over Power. R2C is too good")
      else:             #
         slope = 'UNDER_COMPENSATE'
         objMsg.printMsg("slope performance: %s => Avg BER of R2c < Avg BER of R2 "%(str(slope)))
         if abs(delta_ber) > TP.delta_R2C_bigger_than_R2 and not testSwitch.RESET_TCC1_SLOPE_IF_BOTH_TCC1_AND_BER_OVER_SPEC: #0.4:
            # reset to default.
            ScrCmds.raiseException(48448, "TCC1 slope is under Power. R2C is too bad")
      return slope

   #-------------------------------------------------------------------------------------------------------
   def GetZoneWithMaxPositiveMargin(self, r2c_ber_list = [], r2_ber_list = [], head = 0, start_zone=0, end_zone=0):

      objMsg.printMsg("GetZoneWithMaxPositiveMargin: head %s start_zone %s end_zone %s"%(str(head),str(start_zone),str(end_zone))) # cold
      objMsg.printMsg("r2c_ber_list %s"%(str(r2c_ber_list))) # cold
      objMsg.printMsg("r2_ber_list %s"%(str(r2_ber_list)))   # hot

      max_delta_ber = r2c_ber_list[head][start_zone] - r2_ber_list[head][start_zone]
      max_zone      = start_zone
      for zone in xrange(start_zone, end_zone+1) :
         delta_ber = abs(r2c_ber_list[head][zone]) - abs(r2_ber_list[head][zone])
         objMsg.printMsg("head %s zone %s delta_ber %s max_delta_ber %s"%(str(head),str(zone),str(delta_ber),str(max_delta_ber)))
         if delta_ber > max_delta_ber:
             max_delta_ber = delta_ber
             max_zone      = zone
      objMsg.printMsg("delta_ber %s"%(str(delta_ber)))   # hot
      objMsg.printMsg("max_zone %s max_delta_ber %s"%(str(max_zone),str(max_delta_ber)))   # hot

      return max_zone

   #-------------------------------------------------------------------------------------------------------
   def GetZoneWithMaxNegativeMargin(self, r2c_ber_list = [], r2_ber_list = [], head = 0, start_zone=0, end_zone=0):
      objMsg.printMsg("GetZoneWithMaxNegativeMargin: head %s start_zone %s end_zone %s"%(str(head),str(start_zone),str(end_zone))) # cold
      objMsg.printMsg("r2c_ber_list %s"%(str(r2c_ber_list))) # cold
      objMsg.printMsg("r2_ber_list %s"%(str(r2_ber_list)))   # hot

      min_delta_ber = r2c_ber_list[head][start_zone] - r2_ber_list[head][start_zone]
      min_zone      = start_zone
      for zone in xrange(start_zone, end_zone+1):
         delta_ber = abs(r2c_ber_list[head][zone]) - abs(r2_ber_list[head][zone])
         objMsg.printMsg("head %s zone %s delta_ber %s min_delta_ber %s"%(str(head),str(zone),str(delta_ber),str(min_delta_ber)))
         if delta_ber < min_delta_ber:
             min_delta_ber = delta_ber
             min_zone      = zone
      objMsg.printMsg("delta_ber %s"%(str(delta_ber)))   # hot
      objMsg.printMsg("min_zone %s min_delta_ber %s"%(str(min_zone),str(min_delta_ber)))   # hot
      return min_zone


#----------------------------------------------------------------------------------------------------------
class CHSC_TCC(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.dut = dut
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      import struct
      from math import log
      from AFH import CdPES
      from Process import CCudacom
      from Temperature import CTemperature

      self.oCudacom = CCudacom()
      self.odPES = CdPES(TP.masterHeatPrm_11, TP.defaultOCLIM)
      self.oTemp = CTemperature()

      a=lambda d:(sum((x-1.*sum(d)/len(d))**2 for x in d)/(1.*(len(d)-1)))**.5

      try:
         if not testSwitch.virtualRun:
            self.dut.dblData.delTable('P190_HSC_DATA', forceDeleteDblTable = 1)
      except:
         objMsg.printMsg(" delete table failed" )

      #objMsg.printMsg("High Temp HSC: Run ")

      try:
         if not testSwitch.virtualRun:
            self.dut.dblData.Tables('P190_HSC_DATA').deleteIndexRecords(1)#del file pointers
            self.dut.dblData.delTable('P190_HSC_DATA')#del RAM objects
      except:
         objMsg.printMsg("table delete failed. ")
         pass

      #zt = self.dut.dblData.Tables(TP.zone_table['table_name']).tableDataObj()

      Prm_190 = TP.prm_190_HSC_TCC.copy()
      loopcnt = Prm_190['LOOP_CNT']
      
      try:
         if not testSwitch.virtualRun:
            self.dut.dblData.delTable('P190_HSC_DATA', forceDeleteDblTable = 1)
      except:
         objMsg.printMsg("delete table failed" )

      SetFailSafe()

      ColdDownDelay = 15*60*1
      ScriptPause(0)

      if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
         MaskList = self.odPES.oUtility.convertListToZoneBankMasks(Prm_190['ZONE'])
         Prm_190.pop('ZONE')
         for bank,list in MaskList.iteritems():
            if list:
               Prm_190['BIT_MASK_EXT'], Prm_190['BIT_MASK'] = self.odPES.oUtility.convertListTo64BitMask(list)
               Prm_190['ZONE_MASK_BANK'] = bank
               self.odPES.St(Prm_190) #175: RW Tracks MINIZAP_175 in OPTIZAP_1
      else:
         if 'ZONE' in Prm_190: del Prm_190['ZONE']
         self.odPES.St(Prm_190)
      ClearFailSafe()

##########################################################################################

      #DIHA Screening
      if testSwitch.ENABLE_DIHA_FOR_INSTABLE_HD_SCRN:
         if self.dut.currentState in ['HSC_TCC_HT']:
            spcid = 0
         else:
            spcid = 1

         tableData0 = self.dut.dblData.Tables('P190_HSC_DATA').tableDataObj()

         for row in tableData0:
            dblog_record = {
                 'SPC_ID'          : spcid,
                 'HD_PHYS_PSN'     : int(row['HD_LGC_PSN']),
                 'DATA_ZONE'       : int(row['DATA_ZONE']),
                 'TRACK'           : int(row['TRK_NUM']),
                 'REV'             : int(row['INDEX1']),
                 'HSC_MEAN'        : int(row['READ_INDEX']),
                 'HSC_STDEV'       : float(row['DATA1']),
                 }

            self.dut.dblData.Tables('P190_DIHA_DATA').addRecord(dblog_record)


         wedge_stdev_mean =0
         wedge_stdev_stdev = 0


         tableData1 = self.dut.dblData.Tables('P190_HSC_DATA').tableDataObj()

         tableData3 = self.dut.dblData.Tables('P190_DIHA_DATA3').tableDataObj()

         for head in range(self.dut.imaxHead):
            for zone in range(self.dut.numZones):
               for row in tableData3:
                  if (int(row['HD_LGC_PSN'])== head)  and (int(row['DATA_ZONE']) == zone):
                     wedge_stdev_mean =float(row['SS_STV_AVE'])
                     wedge_stdev_stdev = float(row['SS_STV_STV'])

               hsc_avg=[]
               hsc_stdev=[]
               for row in tableData1:
                  if (int(row['HD_LGC_PSN'])== head)  and (int(row['DATA_ZONE']) == zone):
                     hsc_avg.append( int(row['READ_INDEX'])  )
                     hsc_stdev.append( float(row['DATA1'])  )
               hsc_avg_hz = sum(hsc_avg)/(loopcnt)
               hsc_stdev_hz = sum(hsc_stdev)/(loopcnt)

               if hsc_avg_hz != 0:
                  dblog_record = {
                       'SPC_ID'          : spcid,
                       'HD_PHYS_PSN'     : head,
                       'DATA_ZONE'       : zone,
                       #'TRACK'          : int(row['TRK_NUM']),
                       'HSC_MEAN_MEAN'   : hsc_avg_hz,
                       'HSC_STDEV_MEAN'  : hsc_stdev_hz,
                       'HSC_MEAN_STDEV'  : a(hsc_avg),
                       'HSC_STDEV_STDEV' : a(hsc_stdev),
                       'HSC_STDEV2_MEAN'  : wedge_stdev_mean,
                       'HSC_STDEV2_STDEV' : wedge_stdev_stdev,
                       }
                  self.dut.dblData.Tables('P190_DIHA_SUMMARY').addRecord(dblog_record)

         objMsg.printDblogBin(self.dut.dblData.Tables('P190_DIHA_DATA'), spcId32=spcid)
         objMsg.printDblogBin(self.dut.dblData.Tables('P190_DIHA_SUMMARY'), spcId32=spcid)


##########################################################################################

      #HSC and TCC calculation
      tableData = self.dut.dblData.Tables('P190_HSC_DATA').tableDataObj()

      #num_heater (reader & writer) TCC value
      num_heater_cal = (testSwitch.ENABLE_WRITER_THERMAL_CLR_COEF_CAL and 2 or 1)

      #### Get hsc amplitude at high temp ####
      if self.dut.currentState in ['HSC_TCC_HT']:
         num_zone_tested = 0
         for head in range(self.dut.imaxHead):
            for zone in range(self.dut.numZones):
               hsc0=[]
               if testSwitch.ENABLE_WRITER_THERMAL_CLR_COEF_CAL:
                  hsc1=[]

               for row in tableData:
                  if (int(row['HD_LGC_PSN'])== head)  and (int(row['DATA_ZONE']) == zone) and (int(row['INDEX1']) > loopcnt-11):
                     hsc0.append( int(row['READ_INDEX'])  )
                     if testSwitch.ENABLE_WRITER_THERMAL_CLR_COEF_CAL:
                        hsc1.append( int(row['INDEX2'])  )
                     head =  int(row['HD_LGC_PSN'])
                     zone  =  int(row['DATA_ZONE'])
                     trk  =  int(row['TRK_NUM'])


                     if int(row['INDEX1']) == loopcnt-1 :
                        #objMsg.printMsg("hsc0cccccccccccc %s" % str(hsc0))
                        num_zone_tested += 1
                        hsc0[0]= sum(hsc0)/(loopcnt-10)
                        self.dut.hsc_ht_lst.append(hsc0[0])

                        if testSwitch.ENABLE_WRITER_THERMAL_CLR_COEF_CAL:
                           hsc1[0]= sum(hsc1)/(loopcnt-10)
                           self.dut.hsc_ht_lst.append(hsc1[0])

                        dblog_record = {
                             'HD_PHYS_PSN'     : head,
                             'DATA_ZONE'       : zone,
                             'TRACK'           : trk,
                             'HSC_RH'          : hsc0[0],
                             'HSC_WH'          : ( (not testSwitch.ENABLE_WRITER_THERMAL_CLR_COEF_CAL) and "N.A" or hsc1[0]),
                             }

                        self.dut.dblData.Tables('P190_TCC_DATA').addRecord(dblog_record)


         #########

         #measure temperature first before power cylce to prevent cool down
         HighTemp = self.oTemp.retHDATemp()
         self.dut.hsc_ht_lst.append(99999)
         #append current temperature [num_heater_cal * (num_zone_tested)]
         for i in range(num_heater_cal * num_zone_tested):
            self.dut.hsc_ht_lst.append(HighTemp)

         objPwrCtrl.powerOff()
         ScriptPause(10)
         #objMsg.printMsg("========================================================================================================")
         objMsg.printMsg("========================================================================================================")
         objPwrCtrl.powerOn(useESlip=1)

         #objMsg.printMsg("hsc_ht_lstcddddddcc %s" % str(self.dut.hsc_ht_lst))
         from array import array
         from base_SerialTest import CFormat2File1
         oRdFmt2File = CFormat2File1()
         #objMsg.printMsg("ccyy save hsc_tcc to pc file..........")
         oRdFmt2File.Save_HSC_Format(array('f', self.dut.hsc_ht_lst))


      #### End of Get hsc amplitude at high temp ####


      #### Get hsc amplitude at low temp ####
      if self.dut.currentState in ['HSC_TCC_LT']:


         LowTemp = self.oTemp.retHDATemp()

         #objMsg.printMsg( "ccccccccretHDATemp: %f angstroms"   % (LowTemp ))


         #########
         #self.dut.hsc_ht_lst= [3000,3100,3200,3300,3400,  4000,4100,4200,4300,4400]

         objPwrCtrl.powerOff()
         ScriptPause(10)
         #objMsg.printMsg("========================================================================================================")
         objMsg.printMsg("========================================================================================================")
         objPwrCtrl.powerOn(useESlip=1)

         from base_SerialTest import CFormat2File1
         oRdFmt2File = CFormat2File1()
         self.dut.hsc_ht_lst = []
         self.dut.hsc_ht_lst = oRdFmt2File.Retrieve_HSC_Format(0)
         objMsg.printMsg("self.dut.Format_List2eeeeeeeeeeeeeeeeeeeee %s" % str(self.dut.hsc_ht_lst))

         num_zones =  int(self.dut.hsc_ht_lst.index(99999)/(self.dut.imaxHead*num_heater_cal))
         objMsg.printMsg("Number of Zones Tested %d" % num_zones)

         #get zone table, rpm speed, preamp coefficient gamma reader and writer heater only once
         # get zone table
         self.odPES.mFSO.getZoneTable()
         zonetable = self.dut.dblData.Tables(TP.zone_table['table_name']).tableDataObj()

         # get rpm speed
         tmpParam = dict(TP.getRpmPrm_11_HSC.copy())
         tmpParam["START_ADDRESS"] = self.odPES.oUtility.ReturnTestCylWord(144)
         tmpParam["END_ADDRESS"] = self.odPES.oUtility.ReturnTestCylWord(144)
         self.odPES.St(tmpParam)
         rpm=int(self.dut.dblData.Tables('P011_SV_RAM_RD_BY_OFFSET').tableDataObj()[-1]['READ_DATA'],16)

         #get preamp coefficient gamma reader and writer heater only one
         if testSwitch.FE_0110575_341036_ENABLE_MEASURING_CONTACT_USING_TEST_135 == 1:
            if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT == 1:
               import AFH_Screens_DH
            else:
               import AFH_Screens_T135
         else:
            if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT == 1:
               import AFH_Screens_DH
            else:
               import AFH_Screens_T035


         self.odPES = CdPES(TP.masterHeatPrm_11, TP.defaultOCLIM)
         self.odPES.frm.clearCM_SIM_method(self.params.get('clearCM_SIM', 0))

         self.odPES.setMasterHeat(TP.masterHeatPrm_11, setMHeatOn = 1) #enable master heat

         self.odPES.lmt.maxDAC = (2**TP.dpreamp_number_bits_DAC.get(self.dut.PREAMP_TYPE, 0)) - 1

         coefs = self.odPES.getClrCoeff(TP.clearance_Coefficients, self.dut.PREAMP_TYPE, self.dut.AABType)
         if self.dut.HGA_SUPPLIER == 'RHO':
            objMsg.printMsg("coefs['gammaReaderHeater'][0] %f, coefs['gammaReaderHeater'][1] %f, coefs['gammaReaderHeater'][2] %f"
               %(coefs['gammaReaderHeater'][0], coefs['gammaReaderHeater'][1], coefs['gammaReaderHeater'][2]))
         else:
            objMsg.printMsg("coefs['gammaWriterHeater'][0]: %f, coefs['gammaWriterHeater'][1]: %f, coefs['gammaWriterHeater'][2]: %f"
               %(coefs['gammaWriterHeater'][0], coefs['gammaWriterHeater'][1], coefs['gammaWriterHeater'][2]))

         HiTempIndex = len(self.dut.hsc_ht_lst) - 1   # just use last temperature value
         objMsg.printMsg("CCYY Retrieve High Temp %f" % (self.dut.hsc_ht_lst[HiTempIndex]))

         for head in range(self.dut.imaxHead):
            i = 0
            for zone in range(self.dut.numZones):
               hsc0=[]
               if testSwitch.ENABLE_WRITER_THERMAL_CLR_COEF_CAL:
                  hsc1=[]
               for row in tableData:
                  if (int(row['HD_LGC_PSN'])== head)  and (int(row['DATA_ZONE']) == zone) and (int(row['INDEX1']) > loopcnt-11):
                     hsc0.append( int(row['READ_INDEX'])  )
                     if testSwitch.ENABLE_WRITER_THERMAL_CLR_COEF_CAL:
                        hsc1.append( int(row['INDEX2'])  )
                     head =  int(row['HD_LGC_PSN'])
                     zone  =  int(row['DATA_ZONE'])
                     trk  =  int(row['TRK_NUM'])

                     if int(row['INDEX1']) ==loopcnt-1 :
                        #objMsg.printMsg("hsc0cccccccccccc %s" % str(hsc0))

                        hsc0[0]= sum(hsc0)/(loopcnt-10)
                        if testSwitch.ENABLE_WRITER_THERMAL_CLR_COEF_CAL:
                           hsc1[0]= sum(hsc1)/(loopcnt-10)

                        #################################################################
                        ## Radius

                        mCylinder=(trk>>16)&0xFFFF
                        lCylinder = trk&0xFFFF
                        buf, errorCode = self.oCudacom.Fn(1370, lCylinder, mCylinder, head, 0)
                        result = struct.unpack(">LLH", buf)
                        radius = (result[2]/(16.0*1000.0))

                        #################################################################
                        ## Data rate
                        Index = self.odPES.dth.getFirstRowIndexFromTable_byZone(zonetable, head, zone)
                        datarate  = float(zonetable[Index]['NRZ_FREQ'])

                        #################################################################
                        ##kfci calculation
                        Kfci = 60*datarate*(Prm_190["FREQUENCY"])/(2*3.1416*radius*rpm*100)

                        datarate=datarate*(Prm_190["FREQUENCY"])/100

                        #objMsg.printMsg( "head  ======================= %d"   % (head))
                        #objMsg.printMsg( "LN zone   ======================= %d"   % (zone))
                        #objMsg.printMsg( "LN track      ======================= %d"   % (trk))
                        #objMsg.printMsg( "Kfci     = %f"   % (60*datarate/(2*3.1416*radius*rpm)))
                        #objMsg.printMsg( "datarate : %f"   % (datarate))
                        #objMsg.printMsg( "radius : %f"   % (radius))
                        #objMsg.printMsg( "rpm  : %f"   % (rpm))

                        aa=0
                        aa_rh =0
                        if testSwitch.ENABLE_WRITER_THERMAL_CLR_COEF_CAL:
                           aa_wh =0

                        l_2T = (radius*2*3.14159*rpm*4)/(60*(datarate/1000))
                        #objMsg.printMsg( "l(2T wavelength) = (radius*2 p*rpm*4)/(60*(f/1000)) = %f"   % (l_2T))
                        #objMsg.printMsg( "HIRP2 = (l_2T/(2*3.14159))*(log(hsc0/hsc1)) = " )
                        aa = (l_2T/(2*3.14159));
                        #objMsg.printMsg( "(l_2T/(2*pi)) = %f"   % (aa))

                        try:
                           #objMsg.printMsg( "hsc0[0]===cccc=========== %d"   % (hsc0[0]))
                           #objMsg.printMsg( "self.dut.hsc_ht_lst[head*num_zones+i]====cccc=============== %d"   % (self.dut.hsc_ht_lst[head*num_zones*2+i*2]))
                           aa_rh =  aa*(log(float(hsc0[0])/float(self.dut.hsc_ht_lst[head*num_zones*num_heater_cal+i*num_heater_cal])))*254
                        except:
                           objMsg.printMsg("log (hsc low temp/hsc high temp) rh failed!!!!!!!!!!!!!!!!!!!!!")

                        if testSwitch.ENABLE_WRITER_THERMAL_CLR_COEF_CAL:
                           try:
                              #objMsg.printMsg( "hsc1[0]===cccc=========== %d"   % (hsc1[0]))
                              #objMsg.printMsg( "self.dut.hsc_ht_lst[head*num_zones+i+1]====cccc=============== %d"   % (self.dut.hsc_ht_lst[head*num_zones*2+i*2+1]))
                              aa_wh =  aa*(log(float(hsc1[0])/float(self.dut.hsc_ht_lst[head*num_zones*num_heater_cal+i*num_heater_cal + 1])))*254
                           except:
                              objMsg.printMsg("log (hsc low temp /hsc high temp) wh failed!!!!!!!!!!!!!!!!!!!!!")


                        #objMsg.printMsg( "HIRP2 ===index: %d =====================================================: %f angstroms"   % (i,aa))
                        if 0:  # Disable Gamma

                           if self.dut.HGA_SUPPLIER == 'RHO':
                              gammaH = float( coefs['gammaReaderHeater'][0] )  +    float( coefs['gammaReaderHeater'][1] )*float(trk/1000) +      float( coefs['gammaReaderHeater'][2] )*float(trk/1000)*float(trk/1000)
                              #objMsg.printMsg( "gammaReaderHeatercoeff 1=========================================================: %f "   % (coefs['gammaReaderHeater'][0]))
                              #objMsg.printMsg( "gammaReaderHeatercoeff 2=========================================================: %f "   % (coefs['gammaReaderHeater'][1]))
                              #objMsg.printMsg( "gammaReaderHeatercoeff 3=========================================================: %f "   % (coefs['gammaReaderHeater'][2]))
                           else:
                              gammaH = float( coefs['gammaWriterHeater'][0] )  +    float( coefs['gammaWriterHeater'][1] )*float(trk/1000) +      float( coefs['gammaWriterHeater'][2] )*float(trk/1000)*float(trk/1000)
                              #objMsg.printMsg( "gammaWriterHeatercoeff 1=========================================================: %f "   % (coefs['gammaWriterHeater'][0]))
                              #objMsg.printMsg( "gammaWriterHeatercoeff 2=========================================================: %f "   % (coefs['gammaWriterHeater'][1]))
                              #objMsg.printMsg( "gammaWriterHeatercoeff 3=========================================================: %f "   % (coefs['gammaWriterHeater'][2]))

                        else:
                           gammaH = 1


                        HIRP2_g_rh = gammaH*aa_rh
                        if testSwitch.ENABLE_WRITER_THERMAL_CLR_COEF_CAL:
                           HIRP2_g_wh = gammaH*aa_wh

                        #objMsg.printMsg( "HIRP2_Gamma rh ==========================================================: %f angstroms"   % (HIRP2_g_rh))
                        #objMsg.printMsg( "HIRP2_Gamma wh ==========================================================: %f angstroms"   % (HIRP2_g_wh))

                        tc1_rh = HIRP2_g_rh/(LowTemp - self.dut.hsc_ht_lst[HiTempIndex])
                        if testSwitch.ENABLE_WRITER_THERMAL_CLR_COEF_CAL:
                           tc1_wh = HIRP2_g_wh/(LowTemp - self.dut.hsc_ht_lst[HiTempIndex])

                        #objMsg.printMsg( "iiiii=========================================================: %f "   % (i))



                        if self.dut.HGA_SUPPLIER == 'RHO':

                           dblog_record = {
                                'HD_PHYS_PSN'     : head,
                                'DATA_ZONE'       : zone,
                                'TRACK'           : trk,
                                'HSC0_RH'         : self.dut.hsc_ht_lst[head*num_zones*num_heater_cal+i*num_heater_cal],
                                'HSC0_WH'         : ( (not testSwitch.ENABLE_WRITER_THERMAL_CLR_COEF_CAL) and "N.A" or self.dut.hsc_ht_lst[head*num_zones*num_heater_cal+i*num_heater_cal+1]),
                                'HSC1_RH'         : hsc0[0],
                                'HSC1_WH'         : ( (not testSwitch.ENABLE_WRITER_THERMAL_CLR_COEF_CAL) and "N.A" or hsc1[0]),
                                'HIRP2_RH'        : ("%.7f" % (0-HIRP2_g_rh)),
                                'HIRP2_WH'        : ( (not testSwitch.ENABLE_WRITER_THERMAL_CLR_COEF_CAL) and "N.A" or (0-HIRP2_g_wh)),
                                'TC1_RH'          : ("%.7f" % (0-tc1_rh)),
                                'TC1_WH'          : ( (not testSwitch.ENABLE_WRITER_THERMAL_CLR_COEF_CAL) and "N.A" or (0-tc1_wh)),
                                'TEMP_HI'         : self.dut.hsc_ht_lst[HiTempIndex],
                                'TEMP_LO'         : LowTemp,
                                }
                        else:
                           dblog_record = {
                                'HD_PHYS_PSN'     : head,
                                'DATA_ZONE'       : zone,
                                'TRACK'           : trk,
                                'HSC0_RH'         : ( (not testSwitch.ENABLE_WRITER_THERMAL_CLR_COEF_CAL) and "N.A" or self.dut.hsc_ht_lst[head*num_zones*num_heater_cal+i*num_heater_cal+1]),
                                'HSC0_WH'         : self.dut.hsc_ht_lst[head*num_zones*num_heater_cal+i*num_heater_cal],
                                'HSC1_RH'         : ( (not testSwitch.ENABLE_WRITER_THERMAL_CLR_COEF_CAL) and "N.A" or hsc1[0]),
                                'HSC1_WH'         : hsc0[0],
                                'HIRP2_RH'        : ( (not testSwitch.ENABLE_WRITER_THERMAL_CLR_COEF_CAL) and "N.A" or (0-HIRP2_g_wh)),
                                'HIRP2_WH'        : ("%.7f" %(0-HIRP2_g_rh)),
                                'TC1_RH'          : ( (not testSwitch.ENABLE_WRITER_THERMAL_CLR_COEF_CAL) and "N.A" or (0-tc1_wh)),
                                'TC1_WH'          : ("%.7f"%(0-tc1_rh)),
                                'TEMP_HI'         : self.dut.hsc_ht_lst[HiTempIndex],
                                'TEMP_LO'         : LowTemp,
                                }


                        self.dut.dblData.Tables('P190_TCC_SUMMARY').addRecord(dblog_record)
                        i= i+1

      #### End of Get hsc amplitude at low temp ####

      headvendor = str(self.dut.HGA_SUPPLIER)

      Do_TCC_RAP_update = 1


      if self.dut.currentState in ['HSC_TCC_HT']:
         objMsg.printDblogBin(self.dut.dblData.Tables('P190_TCC_DATA'))
      if self.dut.currentState in ['HSC_TCC_LT']:
         objMsg.printDblogBin(self.dut.dblData.Tables('P190_TCC_SUMMARY'))

         tableData4 = self.dut.dblData.Tables('P190_TCC_SUMMARY').tableDataObj()

         for head in range(self.dut.imaxHead):
            if headvendor in ['TDK', 'HWY']:
               tc1_wh_lst=[]
               tc1_wh_lst_cal=[]
            else: #RH0
               tc1_rh_lst=[]
               tc1_rh_lst_cal=[]

            for row in tableData4:
               if int(row['HD_PHYS_PSN']) == head:
                  if headvendor in ['TDK', 'HWY']:
                     tc1_wh_lst.append( float(row['TC1_WH'])  )
                  else:
                     tc1_rh_lst.append( float(row['TC1_RH'])  )
            if headvendor in ['TDK', 'HWY']:
               tc1_wh_lst.sort()
               tc1_wh_lst.pop()
               tc1_wh_lst.pop(0)
            else: #RHO
               tc1_rh_lst.sort()
               tc1_rh_lst.pop()
               tc1_rh_lst.pop(0)

            if headvendor in ['TDK', 'HWY']:
               wh_fail_cnt = 0
            else: #RHO
               rh_fail_cnt = 0

            if headvendor in ['TDK', 'HWY']:
               for item in tc1_wh_lst:
                  if (item<1) and (item>-1):
                     tc1_wh_lst_cal.append(item)
                  else:
                     objMsg.printMsg( "Invalid data wh: %f "   % (item))
                     wh_fail_cnt=wh_fail_cnt+1
            else: #RH0
               for item in tc1_rh_lst:
                  if (item<1) and (item>-1):
                     tc1_rh_lst_cal.append(item)
                  else:
                     objMsg.printMsg( "Invalid data rh: %f "   % (item))
                     rh_fail_cnt=rh_fail_cnt+1

            try:
               if headvendor in ['TDK', 'HWY']:
                  self.dut.R_THERMAL_CLR_COEF1.append( sum(tc1_wh_lst_cal)/len(tc1_wh_lst_cal) - 0.1 )
                  self.dut.W_THERMAL_CLR_COEF1.append( sum(tc1_wh_lst_cal)/len(tc1_wh_lst_cal) - 0.1 )
                  objMsg.printMsg("TDK head -0.1 offset applied !!!")
               if headvendor == 'RHO':
                  self.dut.R_THERMAL_CLR_COEF1.append( sum(tc1_rh_lst_cal)/len(tc1_rh_lst_cal) )
                  # use default no update  self.dut.W_THERMAL_CLR_COEF1.append( sum(tc1_wh_lst_cal)/len(tc1_wh_lst_cal) )
            except:
               objMsg.printMsg("TC list is empty!!!!!!!!!!!!")
               self.dut.NCTC_VALID_TCC = 0
               pass

            if headvendor in ['TDK', 'HWY']:
               fail_heater_cnt = wh_fail_cnt
            else :
               fail_heater_cnt = rh_fail_cnt

            if fail_heater_cnt>4:
               Do_TCC_RAP_update =0
               objMsg.printMsg("TOO MANY Invalid data, Skip RAP update !!!")
               self.dut.NCTC_VALID_TCC = 0

         objMsg.printMsg("self.dut.R_THERMAL_CLR_COEF1ccccccccccccccccc %s" % str(self.dut.R_THERMAL_CLR_COEF1))     #debug
         objMsg.printMsg("self.dut.W_THERMAL_CLR_COEF1ccccccccccccccccc %s" % str(self.dut.W_THERMAL_CLR_COEF1))     #debug

         if 0:  #Do_TCC_RAP_update:
            for iHead in range(self.dut.imaxHead):
               from RAP import ClassRAP
               objRAP = ClassRAP()
               if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT:
                  if len(self.dut.W_THERMAL_CLR_COEF1)!=0:
                     objRAP.SaveTCC_toRAP( iHead, self.dut.W_THERMAL_CLR_COEF1[iHead], TP.tcc_DH_dict_178["WRITER_HEATER"]['TCS2'], "WRITER_HEATER",TP.tcc_DH_values)
                  else:
                     objMsg.printMsg("W_THERMAL_CLR_COEF1 empty !!!")
                  if len(self.dut.R_THERMAL_CLR_COEF1)!=0:
                     objRAP.SaveTCC_toRAP( iHead, self.dut.R_THERMAL_CLR_COEF1[iHead], TP.tcc_DH_dict_178["READER_HEATER"]['TCS2'], "READER_HEATER",TP.tcc_DH_values)
                  else:
                     objMsg.printMsg("R_THERMAL_CLR_COEF1 empty !!!")


               else:     # single heater drive
                  if len(self.dut.W_THERMAL_CLR_COEF1)!=0:
                     objRAP.SaveTCC_toRAP( iHead, self.dut.W_THERMAL_CLR_COEF1[iHead], TP.tcc_DH_dict_178["WRITER_HEATER"]['TCS2'], "WRITER_HEATER",TP.tcc_DH_values)
                  else:
                     objMsg.printMsg("W_THERMAL_CLR_COEF1 empty !!!")

         if testSwitch.NCTC_CLOSED_LOOP:
            from RdWr import CRdScrn2File
            oRdScrn2File  = CRdScrn2File()
            oRdScrn2File.Show_P172_AFH_TC_COEF_2(100)
            if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT:
               Current_TCC1_R, Current_TCC1_W = oRdScrn2File.Get_Current_TCC1(100)

            else:
               Current_TCC1 = oRdScrn2File.Get_Current_TCC1(100)

      return


#----------------------------------------------------------------------------------------------------------
class CTccupdate(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.dut = dut
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if self.dut.NCTC_VALID_TCC==1:

         if 1:
            for iHead in range(self.dut.imaxHead):
               from RAP import ClassRAP
               objRAP = ClassRAP()
               if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT:
                  if len(self.dut.W_THERMAL_CLR_COEF1)!=0:
                     if not testSwitch.extern.FE_0157745_387179_AFH_TCS_WARP:
                        objRAP.SaveTCC_toRAP( iHead, self.dut.W_THERMAL_CLR_COEF1[iHead], TP.tcc_DH_dict_178["WRITER_HEATER"]['TCS2'], "WRITER_HEATER",TP.tcc_DH_values)
                     else: 
                        objRAP.SaveTCC_toRAP( iHead, self.dut.W_THERMAL_CLR_COEF1[iHead], TP.tcc_DH_dict_178["WRITER_HEATER"]['TCS2'], "WRITER_HEATER",TP.tcc_DH_values, TP.TCS_WARP_ZONES.keys())
                  else:
                     objMsg.printMsg("W_THERMAL_CLR_COEF1 empty !!!")
                  if len(self.dut.R_THERMAL_CLR_COEF1)!=0:
                     if not testSwitch.extern.FE_0157745_387179_AFH_TCS_WARP:
                        objRAP.SaveTCC_toRAP( iHead, self.dut.R_THERMAL_CLR_COEF1[iHead], TP.tcc_DH_dict_178["READER_HEATER"]['TCS2'], "READER_HEATER",TP.tcc_DH_values)
                     else: 
                        objRAP.SaveTCC_toRAP( iHead, self.dut.R_THERMAL_CLR_COEF1[iHead], TP.tcc_DH_dict_178["READER_HEATER"]['TCS2'], "READER_HEATER",TP.tcc_DH_values, TP.TCS_WARP_ZONES.keys())
                  else:
                     objMsg.printMsg("R_THERMAL_CLR_COEF1 empty !!!")


               else:     # single heater drive
                  if len(self.dut.W_THERMAL_CLR_COEF1)!=0:
                     if not testSwitch.extern.FE_0157745_387179_AFH_TCS_WARP:
                        objRAP.SaveTCC_toRAP( iHead, self.dut.W_THERMAL_CLR_COEF1[iHead], TP.tcc_DH_dict_178["WRITER_HEATER"]['TCS2'], "WRITER_HEATER",TP.tcc_DH_values)
                     else:
                        objRAP.SaveTCC_toRAP( iHead, self.dut.W_THERMAL_CLR_COEF1[iHead], TP.tcc_DH_dict_178["WRITER_HEATER"]['TCS2'], "WRITER_HEATER",TP.tcc_DH_values, TP.TCS_WARP_ZONES.keys())

                  else:
                     objMsg.printMsg("W_THERMAL_CLR_COEF1 empty !!!")

         objRAP.mFSO.saveRAPtoFLASH()
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

         from RdWr import CRdScrn2File
         oRdScrn2File  = CRdScrn2File()
         oRdScrn2File.Show_P172_AFH_TC_COEF_2(101)
         if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT:
            Current_TCC1_R, Current_TCC1_W = oRdScrn2File.Get_Current_TCC1(101)

         else:
            Current_TCC1 = oRdScrn2File.Get_Current_TCC1(101)


#----------------------------------------------------------------------------------------------------------
class CInitTcc(CState):
   """
      Description: Support control TCC for two plug process.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params

      if dut.nextOper == 'PRE2':
         depList = ['INIT_RAP']
      else:
         depList = []

      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):

      mode = self.params.get('MODE','ON')

      if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT == 1:
         from AFH_Screens_DH import CAFH_Screens
         from RAP import ClassRAP

         oAFH_Screens  = CAFH_Screens()
         objRAP = ClassRAP()
         if mode.upper() == 'OFF':
            tcc_dict = TP.tcc_OFF.copy()
         else:
            tcc_dict = TP.tcc_DH_values.copy()

         oAFH_Screens.St({'test_num':172, 'prm_name': 'TCC Coef before Change', "CWORD1" : (10), 'spc_id': 100, })

         for iHead in oAFH_Screens.headList:
            if not testSwitch.extern.FE_0157745_387179_AFH_TCS_WARP:
               objRAP.SaveTCC_toRAP( iHead, tcc_dict["WRITER_HEATER"]['TCS1'], tcc_dict["WRITER_HEATER"]['TCS2'], "WRITER_HEATER", tcc_dict )
               objRAP.SaveTCC_toRAP( iHead, tcc_dict["READER_HEATER"]['TCS1'], tcc_dict["READER_HEATER"]['TCS2'], "READER_HEATER", tcc_dict )
            else:
               objRAP.SaveTCC_toRAP( iHead, tcc_dict["WRITER_HEATER"]['TCS1'], tcc_dict["WRITER_HEATER"]['TCS2'], "WRITER_HEATER", tcc_dict,TP.TCS_WARP_ZONES.keys())
               objRAP.SaveTCC_toRAP( iHead, tcc_dict["READER_HEATER"]['TCS1'], tcc_dict["READER_HEATER"]['TCS2'], "READER_HEATER", tcc_dict, TP.TCS_WARP_ZONES.keys())

         objRAP.mFSO.saveRAPtoFLASH()
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
         oAFH_Screens.St({'test_num':172, 'prm_name': 'TCC Coef after Change', "CWORD1" : (10), 'spc_id': 101, })


#----------------------------------------------------------------------------------------------------------
class CInitDTH(CState):
   """
      Description: Support control TCC for two plug process.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):

      # Grab all the ber data.
      from RdWr import CRdScrn2File

      mode = self.params.get('MODE','ON')

      # Retrieve the tuned value
      List_save_default_TCC1    = [[] for hd in xrange(self.dut.imaxHead)]
      List_save_default_TCC1_R  = [[] for hd in xrange(self.dut.imaxHead)]
      List_save_default_TCC1_W  = [[] for hd in xrange(self.dut.imaxHead)]
      oRdScrn2File  = CRdScrn2File()
      oRdScrn2File.Show_P172_AFH_TC_COEF_2(102)
      #List_save_default_TCC1 = oRdScrn2File.Get_Current_TCC1()
      if testSwitch.extern.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT:
         List_save_default_TCC1_R, List_save_default_TCC1_W = oRdScrn2File.Get_Current_TCC1(102)
         objMsg.printMsg("List_save_default_TCC1_R %s"%(str(List_save_default_TCC1_R)))
         objMsg.printMsg("List_save_default_TCC1_W %s"%(str(List_save_default_TCC1_W)))
         List_save_default_TCC1 = List_save_default_TCC1_W
      else:
         List_save_default_TCC1 = oRdScrn2File.Get_Current_TCC1(102)
         objMsg.printMsg("List_save_default_TCC1 %s"%(str(List_save_default_TCC1)))

      if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT == 1:
         from AFH_Screens_DH import CAFH_Screens
         from RAP import ClassRAP
         
         oAFH_Screens  = CAFH_Screens()
         objRAP = ClassRAP()

         tcc_dict = TP.tcc_DH_values.copy()

         if mode.upper() == 'OFF': 
            tcc_dict["WRITER_HEATER"]['HOT_TEMP_DTH'] = TP.OPEN_UP_HOT_TEMP_DTH
            tcc_dict["READER_HEATER"]['HOT_TEMP_DTH'] = TP.OPEN_UP_HOT_TEMP_DTH
            objMsg.printMsg("Open Up: HOT_TEMP_DTH (WRITER_HEATER) %d"%(tcc_dict["WRITER_HEATER"]['HOT_TEMP_DTH']))
            objMsg.printMsg("Open Up: HOT_TEMP_DTH (READER_HEATER) %d"%(tcc_dict["READER_HEATER"]['HOT_TEMP_DTH']))
            #oAFH_Screens.St({'test_num':178, 'prm_name': 'SYS_AREA_PREP_STATE OFF','CWORD1':288, "SYS_AREA_PREP_STATE" : (0xFF),})
         else:
            objMsg.printMsg("Use Recommended: HOT_TEMP_DTH (WRITER_HEATER)%d"%(tcc_dict["WRITER_HEATER"]['HOT_TEMP_DTH']))
            objMsg.printMsg("Use Recommended: HOT_TEMP_DTH (READER_HEATER)%d"%(tcc_dict["READER_HEATER"]['HOT_TEMP_DTH']))
            #oAFH_Screens.St({'test_num':178, 'prm_name': 'SYS_AREA_PREP_STATE ON','CWORD1': 288, "SYS_AREA_PREP_STATE" : (0xFE),})

         
         for iHead in oAFH_Screens.headList:
            tcc_dict["WRITER_HEATER"]['TCS1'] = List_save_default_TCC1_W[iHead]
            tcc_dict["READER_HEATER"]['TCS1'] = List_save_default_TCC1_R[iHead]

            if not testSwitch.extern.FE_0157745_387179_AFH_TCS_WARP:
               objRAP.SaveTCC_toRAP( iHead, tcc_dict["WRITER_HEATER"]['TCS1'], tcc_dict["WRITER_HEATER"]['TCS2'], "WRITER_HEATER", tcc_dict )
               objRAP.SaveTCC_toRAP( iHead, tcc_dict["READER_HEATER"]['TCS1'], tcc_dict["READER_HEATER"]['TCS2'], "READER_HEATER", tcc_dict )
            else:
               objRAP.SaveTCC_toRAP( iHead, tcc_dict["WRITER_HEATER"]['TCS1'], tcc_dict["WRITER_HEATER"]['TCS2'], "WRITER_HEATER", tcc_dict, TP.TCS_WARP_ZONES.keys() )
               objRAP.SaveTCC_toRAP( iHead, tcc_dict["READER_HEATER"]['TCS1'], tcc_dict["READER_HEATER"]['TCS2'], "READER_HEATER", tcc_dict, TP.TCS_WARP_ZONES.keys())


         objRAP.mFSO.saveRAPtoFLASH()
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
         oAFH_Screens.St({'test_num':172, 'prm_name': 'TCC Coef after Change', "CWORD1" : (10), 'spc_id': 101, })

