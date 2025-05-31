#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Base AFH states
#
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/09/30 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_AFH.py $
# $Revision: #7 $
# $DateTime: 2016/09/30 04:00:38 $
# $Author: yihua.jiang $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_AFH.py#7 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
from State import CState
import MessageHandler as objMsg
from PowerControl import objPwrCtrl


#----------------------------------------------------------------------------------------------------------
class CInitAFH(CState):
   """
      Description: Class that will perform a 1 stop AFH Calibrations/testing
      Base: Based on Firebirds calibration routines.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      self.dut = dut

      if dut.nextOper == 'PRE2':
         depList = ['MDW_CAL', 'INIT_RAP']
      else:
         depList = []

      if 0: # testSwitch.ENABLE_FAFH_STATE_CHECKING == 1:
         if (dut.nextOper == 'FNC2') and ( dut.nextState == 'AFH3' ):
            depList.append( 'FAFH_TRACK_PREP_1' )
         if (dut.nextOper == 'PRE2') and ( dut.nextState == 'AFH3' ):
            depList.append( 'FAFH_TRACK_PREP_1' )
      CState.__init__(self, dut, depList)
      if testSwitch.AFH2_FAIL_BURNISH_RERUN_AFH1:
         self.burnishretriedAFH1 = 0
         if not (dut.nextState == 'AFH3'):
            if self.dut.BurnishFailedHeads and self.burnishretriedAFH1 == 0:
               self.burnishretriedAFH1 = 2 # we are here becos we are in rerun AFH2
   
   #-------------------------------------------------------------------------------------------------------
   def ReInitAFHState (self):
      objMsg.printMsg("reinit AFH state")

      if self.burnishretriedAFH1 == 1:
         self.dut.nextState = 'AFH1'
      if self.burnishretriedAFH1 == 2:
         self.dut.nextState = 'AFH2'

      from StateTable import StateParams
      import StateMachine

      self.params = StateMachine.evalPhaseOut(StateParams[self.dut.nextOper][self.dut.nextState])
   
   #-------------------------------------------------------------------------------------------------------
   def RunParticalSweep (self):
      objMsg.printMsg('ParticalSweep before reAFH1 ')
      from StateTable import StateParams
      import StateMachine      
      try:
        params = StateMachine.evalPhaseOut(StateParams[self.dut.nextOper]['PARTICLE_SWEEP'])
      except:
        params = {}
      from Sweep_Base import CParticleSweep   
      ParticleSweep = CParticleSweep(self.dut, params)
      ParticleSweep.run()

   #-------------------------------------------------------------------------------------------------------
   def _deltaClrIDOD(self):
      try:
         data = self.dut.dblData.Tables('P135_FINAL_CURVE_FIT_STAT').tableDataObj()
      except:
         objMsg.printMsg('Attention!!! Table P135_FINAL_CURVE_FIT_STAT is not found')
         return
      
      maxDelta = 0
      minDelta = 0
      for entry in data:
         if int(entry['SPC_ID'])/10000 == 1: #filter AFH1 data
            continue
         if maxDelta < float(entry['MAX_ID_OD_DELTA_DAC']):
            maxDelta = float(entry['MAX_ID_OD_DELTA_DAC'])
         if minDelta > float(entry['MAX_ID_OD_DELTA_DAC']):
            minDelta = float(entry['MAX_ID_OD_DELTA_DAC'])
      if self.dut.HGA_SUPPLIER in ['HWY','TDK']:
         if maxDelta > 21:
            self.dut.driveattr['PROC_CTRL30'] = '0X%X' % (int(self.dut.driveattr.get('PROC_CTRL30', '0'),16) | TP.Proc_Ctrl30_Def['QAFH'])
      else:
         if minDelta < -29 and minDelta > -100:
            self.dut.driveattr['PROC_CTRL30'] = '0X%X' % (int(self.dut.driveattr.get('PROC_CTRL30', '0'),16) | TP.Proc_Ctrl30_Def['QAFH'])
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      import ScrCmds
      from Temperature import CTemperature 
      from FSO import CFSO

      self.oTemp = CTemperature()
      self.mFSO = CFSO()
      if testSwitch.extern.FE_0366862_322482_CERT_DETCR_LIVE_SENSOR:
         self.mFSO.St(TP.disableTASensor_11)
         self.mFSO.St(TP.disableLiveSensor_11)
         self.mFSO.saveSAPtoFLASH()
      if testSwitch.AFH2_FAIL_BURNISH_RERUN_AFH1 and not (self.dut.nextState == 'AFH3'):
         self.ReInitAFHState()

      if self.dut.nextOper == 'FNC':
         testSwitch.FE_0148761_409401_P_CHECK_HDA_TEMP = 1

      if testSwitch.FE_0148761_409401_P_CHECK_HDA_TEMP == 1:
         if self.params.get('chkTemp', 'N') == 'Y':
            attrName = self.dut.nextState+'_DELAY'
            self.dut.driveattr[attrName] = 0
            curTemp = self.oTemp.retHDATemp()
            if curTemp < 50:
               if self.dut.powerLossEvent == 1:
                  retry = 3
               else:
                  retry = 1
               while retry > 0:
                  objMsg.printMsg("Current temperature less than 50.")
                  objMsg.printMsg("Auto seek T30 with Sequential Forward/Reverse, 5 mins")
                  self.mFSO.St(TP.hdstr_autoSeek_30)
                  self.dut.driveattr[attrName] += 1
                  curTemp = self.oTemp.retHDATemp()
                  objMsg.printMsg("Retry loop %s, curTemp = %s" %(retry,curTemp))
                  if self.params.get('ChkTempNoLoop', 'N') == 'Y':
                     if curTemp < 50:
                        retry += 1
                     else:
                        break
                  else:
                     if curTemp < 50:
                        retry -= 1
                     else:
                        break

      if testSwitch.CHECK_AND_WAIT_HDA_TEMP_IN_AFH:   # wait for hda temp to reach ~ same as cell temp
         reqTemp, minTemp, maxTemp = TP.temp_profile[self.dut.nextOper]
         curTemp = self.oTemp.retHDATemp()
         while (curTemp < minTemp or curTemp > maxTemp):
            if curTemp < minTemp:
               minWait = minTemp - curTemp
            else:
               minWait = curTemp - maxTemp
            if minWait > 5: minWait = 5   # set max to 5 mins
            objMsg.printMsg("Current Temp = %d, Range = %d - %d, wait %d mins..." % (curTemp, minTemp, maxTemp, minWait))
            ScriptPause(minWait*60)
            curTemp = self.oTemp.retHDATemp()

      if (testSwitch.MR_RESISTANCE_MONITOR):
          from Servo import CServoOpti
          self.oSrvOpti = CServoOpti()
          try:
              if testSwitch.RUN_VBIAS_T186:
                 self.oSrvOpti.setePreampBiasMode(enable = True)
              elif testSwitch.RUN_VBIAS_T186_A2D:
                 self.oSrvOpti.setBiasOption(TP.CURRENT_MODE)
                 objMsg.printMsg("Set Bias Option to Current Mode")
                 self.mFSO.St({'test_num' : 178, 'prm_name' : 'saveSAP2Flash_178', 'CWORD1' : 0x420,})        #write to SAP
                 objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1) #perform power cycle before this test
                 objMsg.printMsg("Power Cycle Complete")
              self.mFSO.St(TP.PresetAGC_InitPrm_186_break)
              if testSwitch.RUN_VBIAS_T186:
                 self.oSrvOpti.setePreampBiasMode(enable = False)
              elif testSwitch.RUN_VBIAS_T186_A2D:
                 self.oSrvOpti.setBiasOption(TP.VOLTAGE_MODE)
                 objMsg.printMsg("Set Bias Option to Voltage Mode")
                 self.mFSO.St({'test_num' : 178, 'prm_name' : 'saveSAP2Flash_178', 'CWORD1' : 0x420,})        #write to SAP
                 objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1) #perform power cycle before this test
                 objMsg.printMsg("Power Cycle Complete")
          except:
              pass

      if testSwitch.FE_0280534_480505_DETCR_ON_OFF_BECAUSE_SERVO_DISABLE_DETCR_BY_DEFAULT:
         # needed due to M10P servo code, servo code disables DETCR by default so DETCR on/off commands need to be called before and after using DETCR
         self.mFSO.St(TP.setDetcrOnPrm_011)
         self.mFSO.St({'test_num':178, 'prm_name':'Save SAP in RAM to FLASH', 'CWORD1':0x420})
      
      #Disable ZAP in flash so no remenant zap is read in subsequent operations
      if testSwitch.ENABLE_T175_ZAP_CONTROL:
         self.mFSO.St(TP.zapPrm_175_zapOff)
      else:
         self.mFSO.St(TP.setZapOffPrm_011)
         if not testSwitch.BF_0119055_231166_USE_SVO_CMD_ZAP_CTRL:
            self.mFSO.St({'test_num':178, 'prm_name':'Save SAP in RAM to FLASH', 'CWORD1':0x420})

      if self.params.get('clearCM_SIM', 0):
         # Clear the restart VBAR counter (prevents complications between restart VBAR and waterfall
         self.dut.rerunVbar = 0
         self.dut.objData.update({'RERUN_VBAR':self.dut.rerunVbar})

      from AFH import CdPES
      self.odPES = CdPES(TP.masterHeatPrm_11, TP.defaultOCLIM)
      if testSwitch.HAMR and self.odPES.AFH_State == 2:
         self.odPES.setIRPCoefs(self.dut.PREAMP_TYPE, self.dut.AABType, TP.PRE_AMP_HEATER_MODE, TP.clearance_Coefficients,  forceRAPWrite = 1, hrmAddC0WitC1 = 0)
         self.odPES.St({'test_num':172, 'prm_name':'AFH PTP Coef Dump', 'timeout': 1800, 'CWORD1': (15,), 'spc_id':10010})
      from AFH_constants import stateTableToAFH_internalStateNumberTranslation 
      if ((testSwitch.AFH2_FAIL_BURNISH_RERUN_AFH1 and self.odPES.AFH_State in [stateTableToAFH_internalStateNumberTranslation['AFH1'],  stateTableToAFH_internalStateNumberTranslation['AFH2']]) or (testSwitch.FE_AFH3_TO_DO_BURNISH_CHECK and self.odPES.AFH_State == stateTableToAFH_internalStateNumberTranslation['AFH3'])) and self.dut.BurnishFailedHeads and self.params.get('clearCM_SIM', 0):
         if self.odPES.frm.removeDepopFrameDataFromCM_SIM(burnish_fail_heads= self.dut.BurnishFailedHeads ):
            self.odPES.frm.clearCM_SIM_method(self.params.get('clearCM_SIM', 0))
            self.dut.BurnishFailedHeads = range(self.dut.imaxHead)
            objMsg.printMsg("Fail to modify sim file, retest all heads")
      else:
         self.odPES.frm.clearCM_SIM_method(self.params.get('clearCM_SIM', 0))

      if self.odPES.AFH_State == 3:
         self.oTemp.waitForTempRampUp(TP.requiredDeltaTempBetweenAFH2_and_AFH3,TP.TccAccMargin)
      self.oTemp.getCellTemperature()

      self.odPES.setMasterHeat(TP.masterHeatPrm_11, setMHeatOn = 1) #enable master heat

      self.odPES.lmt.maxDAC = (2**TP.dpreamp_number_bits_DAC.get(self.dut.PREAMP_TYPE, 0)) - 1


      coefs = self.odPES.getClrCoeff(TP.clearance_Coefficients, self.dut.PREAMP_TYPE, self.dut.AABType)

      if testSwitch.AFH_V3BAR_phase5 == 1:
         self.odPES.findClrID_V3BAR(TP.dpreamp_DACs_backoff_from_Max_DAC_T35.get(self.dut.PREAMP_TYPE,0),\
            TP.heatSearchParams, TP.T35_Retry_Loop_Params, TP.pesMeasurePrm_33, TP.baseDpesPrm_35, TP.maskParams, \
            coefs, TP.lubeSmoothPrm_33, TP.V3BAR_phase5_params, TP.PRE_AMP_HEATER_MODE, TP.deStroke_drive_185_params,)

      if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT == 1:
         self.odPES.getDHStatus( self.dut.PREAMP_TYPE, self.dut.AABType, TP.clearance_Coefficients )


      if testSwitch.FE_0174845_379676_HUMIDITY_SENSOR_CALIBRATION:
         self.oTemp.measureHumidity(spc_id=202)

      #######################################
      # Main AFH Loop
      import AFH_mainLoop
      self.oAFH_test135 = AFH_mainLoop.CAFH_test135()
      if (not testSwitch.AFH2_FAIL_BURNISH_RERUN_AFH1) or (self.dut.nextState in [ 'AFH3', 'AFH4', ]):
          self.oAFH_test135.findClearance_st135(TP.heatSearchParams)
      else:
            objMsg.printMsg("Fail AFH2 rerun AFH1?")
            try:
               self.oAFH_test135.findClearance_st135(TP.heatSearchParams)
            except ScriptTestFailure, (failureData):
               if   self.dut.nextState != 'AFH2' or self.burnishretriedAFH1 != 0:
                  raise
               try: ec = failureData[0][2]
               except: ec = -1
               objMsg.printMsg('Fail AFH2 rerun AFH1, st135/ ec: %s' % str(ec), objMsg.CMessLvl.VERBOSEDEBUG)
               if ec not in TP.AFH2_RETRYFROM_AFH1_ERROR_CODE:
                  raise
               self.mFSO.saveRAPtoFLASH()
               objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
               self.RunParticalSweep()
               objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
               self.burnishretriedAFH1 += 1
               self.run()

         # needed due to M10P servo code, servo code disables DETCR by default so DETCR on/off commands need to be called before and after using DETCR
      if testSwitch.FE_0280534_480505_DETCR_ON_OFF_BECAUSE_SERVO_DISABLE_DETCR_BY_DEFAULT:
         self.mFSO.St(TP.setDetcrOffPrm_011)
         self.mFSO.St({'test_num':178, 'prm_name':'Save SAP in RAM to FLASH', 'CWORD1':0x420})
      if not testSwitch.FE_AFH3_TO_DO_BURNISH_CHECK or self.dut.nextState != 'AFH3':
         self.oAFH_test135 = None


      if (testSwitch.MR_RESISTANCE_MONITOR and 0):
          try:
              self.mFSO.St(TP.PresetAGC_InitPrm_186_break)
          except:
              pass
      #######################################
      #
      if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT == 1:
         from AFH_Screens_DH import CAFH_Screens
      else:
         from AFH_Screens_T135 import CAFH_Screens
      oAFH_Screens = CAFH_Screens()

      if testSwitch.FE_0174845_379676_HUMIDITY_SENSOR_CALIBRATION:
         if self.dut.nextState == 'AFH2':
            self.oTemp.measureHumidity(saveToRap=1,spc_id=203)
         else:
            self.oTemp.measureHumidity(spc_id=204)
      try:
         if  testSwitch.AFH2_FAIL_BURNISH_RERUN_AFH1 and self.burnishretriedAFH1 != 0 and not (self.dut.nextState in [ 'AFH3', 'AFH4', ]):
             oAFH_Screens.burnishCheck(TP.burnish_params_1R, TP.minClr_params_1R, validState = self.params.get('brnsh_chk', 0))
             oAFH_Screens.burnishCheck(TP.burnish_params_2R, TP.minClr_params_2R, validState = self.params.get('brnsh_chk2', 0))
             oAFH_Screens.burnishCheck(TP.deltaClrVBAR_burnish_paramsR, TP.minClr_params_3R, validState = self.params.get('deltaVBAR_chk', 0))
             if testSwitch.FE_AFH_BURNISH_CHECK_BY_RDDAC == 1:
                objMsg.printMsg("Burnish Check by RD Dac is ON")
                oAFH_Screens.burnishCheck(TP.burnish_params_RDDAC1R, TP.minClr_params_RDDAC1R, validState = self.params.get('brnsh_chk', 0))

         else:
            oAFH_Screens.burnishCheck(TP.burnish_params_1, TP.minClr_params_1, validState = self.params.get('brnsh_chk', 0))
            oAFH_Screens.burnishCheck(TP.burnish_params_2, TP.minClr_params_2, validState = self.params.get('brnsh_chk2', 0))
            oAFH_Screens.burnishCheck(TP.deltaClrVBAR_burnish_params, TP.minClr_params_3, validState = self.params.get('deltaVBAR_chk', 0))
            if testSwitch.FE_AFH_BURNISH_CHECK_BY_RDDAC == 1:
               objMsg.printMsg("Burnish Check by RD Dac is ON")
               oAFH_Screens.burnishCheck(TP.burnish_params_RDDAC1, TP.minClr_params_1, validState = self.params.get('brnsh_chk', 0))
         if testSwitch.FE_AFH3_TO_DO_BURNISH_CHECK and self.dut.nextState == 'AFH3' and (self.oAFH_test135.reAFH3_heads or self.dut.AFH3FailBurnish ):
              if self.dut.AFH3FailBurnish < 2:
                 bypass_head = list(set(range(self.dut.imaxHead)) - set(self.oAFH_test135.reAFH3_heads))
              else:
                 bypass_head = list(set(range(self.dut.imaxHead)) - set(self.dut.BurnishFailedHeads))
              objMsg.printMsg("FE_AFH3_TO_DO_BURNISH_CHECK1 %d %s %s %s %s" %(testSwitch.FE_AFH3_TO_DO_BURNISH_CHECK, self.oAFH_test135.ReAFH3_for_burnish, str(self.dut.BurnishFailedHeads), str(bypass_head), str(self.oAFH_test135.reAFH3_heads) ))
              if self.dut.AFH3FailBurnish < 2:
                 oAFH_Screens.burnishCheck(TP.burnish_params_3, TP.minClr_params_2, validState = self.params.get('brnsh_chk3', 0), partial_AFH3_passed_head = bypass_head, fail_any_zone = 1)
              else:
                 oAFH_Screens.burnishCheck(TP.burnish_params_3, TP.minClr_params_2, validState = self.params.get('brnsh_chk3', 0), partial_AFH3_passed_head = bypass_head)
         objMsg.printDblogBin(self.dut.dblData.Tables('P_AFH_DH_BURNISH_CHECK'))

         if ( testSwitch.WA_0111581_341036_AFH_RUN_AFH1_SCREENS_AFTER_HIRP == 0) or \
            ((testSwitch.WA_0111581_341036_AFH_RUN_AFH1_SCREENS_AFTER_HIRP == 1) and ( oAFH_Screens.AFH_State >= 2 ) ):
            if getattr(TP, 'bgSTD', 1) == 1:
               oAFH_Screens.crossStrokeClrCheck(TP.crossStrokeClrLimit)

            if testSwitch.AFH_ENABLE_CLR_RANGE_CHECK_IN_CROSS_STROKE_CHECK == 1:
               oAFH_Screens.clearanceRangeCheck(TP.clrRangeChkLimit)
      except ScrCmds.CRaiseException,exceptionData:

         if self.dut.nextState == 'AFH2' and not testSwitch.AFH2_FAIL_BURNISH_RERUN_AFH1 :
            raise
         if self.burnishretriedAFH1 != 0:
            raise
         if self.dut.nextState == 'AFH3' and not testSwitch.FE_AFH3_TO_DO_BURNISH_CHECK:
            raise
         if testSwitch.FE_AFH3_TO_DO_BURNISH_CHECK and self.dut.AFH3FailBurnish >= 1 and self.dut.nextState == 'AFH3':
            objMsg.printMsg('Script Fail AFH3 rerun burnishcheck/ ec: %s' % str(exceptionData[0][2]), objMsg.CMessLvl.VERBOSEDEBUG)
            raise
         try: ec = exceptionData[0][2]
         except: ec = -1
         objMsg.printMsg('Script Fail AFH2 rerun AFH1, st135/ ec: %s' % str(ec), objMsg.CMessLvl.VERBOSEDEBUG)
         if ec not in TP.AFH2_RETRYFROM_AFH1_ERROR_CODE:
            raise
         if self.dut.nextState == 'AFH3' and testSwitch.FE_AFH3_TO_DO_BURNISH_CHECK:
            self.dut.AFH3FailBurnish = 1
         self.mFSO.saveRAPtoFLASH()
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
         self.RunParticalSweep()
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
         if self.dut.nextState == 'AFH2' and testSwitch.AFH2_FAIL_BURNISH_RERUN_AFH1 :
            self.burnishretriedAFH1 += 1
            self.run()

      if self.dut.nextState in ['AFH3', 'AFH4']:
         #Enable ZAP in flash if comes out from AFH3.
         if testSwitch.ENABLE_T175_ZAP_CONTROL:
            self.mFSO.St(TP.zapPrm_175_zapOn)
         else:
            self.mFSO.St(TP.setZapOnPrm_011)
            if not testSwitch.BF_0119055_231166_USE_SVO_CMD_ZAP_CTRL:
               self.mFSO.St({'test_num':178, 'prm_name':'Save SAP in RAM to FLASH', 'CWORD1':0x420})


      oAFH_Screens = None   # allow GC
      if testSwitch.HAMR and self.odPES.AFH_State == 2:
         #self.odPES.setIRPCoefs(self.dut.PREAMP_TYPE, self.dut.AABType, TP.PRE_AMP_HEATER_MODE, TP.clearance_Coefficients,  forceRAPWrite = 1, hrmAddC0WitC1 = 1)
         self.odPES.St({'test_num':172, 'prm_name':'Hamr Laser', 'timeout': 1800, 'CWORD1': (62,), 'spc_id':170})

      self.odPES = None    # Allow Garbage Collection

      if testSwitch.FE_0167320_007955_CREATE_P_DELTA_BURNISH_TA_SUM_COMBO:

         if self.dut.nextState == 'AFH3':
            curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
            deltaBurnishChkData = self.dut.dblData.Tables('P_AFH_DH_BURNISH_CHECK').tableDataObj()
            T134TaSumHd2Data = self.dut.dblData.Tables('P134_TA_SUM_HD2').tableDataObj()

            testType = self.params.get('testType', "burnish")
            activeHeater = self.params.get('activeHeater', "W")

            for burnishRecord in xrange(len(deltaBurnishChkData)):   # Need DELTA_BURNISH_CHECK from after AFH3 which is currently SEQ = 18, so get > 10 for room to move around
               if deltaBurnishChkData[burnishRecord]['TEST_TYPE'] == testType and deltaBurnishChkData[burnishRecord]['ACTIVE_HEATER'] == activeHeater:
                  for taRecord in xrange(len(T134TaSumHd2Data)):
                     if int(deltaBurnishChkData[burnishRecord]['HD_LGC_PSN']) == int(T134TaSumHd2Data[taRecord]['HD_LGC_PSN']):
                        self.dut.dblData.Tables('P_DELTA_BURNISH_TA_SUM_COMBO').addRecord({
                         'SPC_ID'                      : -1,
                         'OCCURRENCE'                  : occurrence,
                         'SEQ'                         : curSeq,
                         'TEST_SEQ_EVENT'              : testSeqEvent,
                         'HD_PHYS_PSN'                 : self.dut.LgcToPhysHdMap[int(deltaBurnishChkData[burnishRecord]['HD_LGC_PSN'])],
                         'HD_LGC_PSN'                  : deltaBurnishChkData[burnishRecord]['HD_LGC_PSN'],
                         'TEST_TYPE'                   : deltaBurnishChkData[burnishRecord]['TEST_TYPE'],
                         'ACTIVE_HEATER'               : deltaBurnishChkData[burnishRecord]['ACTIVE_HEATER'],
                         'DELTA_BURNISH_CHECK'         : deltaBurnishChkData[burnishRecord]['DELTA_BURNISH_CHECK'],
                         'TA_CNT'                      : T134TaSumHd2Data[taRecord]['TA_CNT'],
                         'SQRT_AMP_WIDTH'              : T134TaSumHd2Data[taRecord]['SQRT_AMP_WIDTH'],
                         'MAX_AMP_WIDTH'               : T134TaSumHd2Data[taRecord]['MAX_AMP_WIDTH'],
                         'AMP0_CNT'                    : T134TaSumHd2Data[taRecord]['AMP0_CNT'],
                         'AMP1_CNT'                    : T134TaSumHd2Data[taRecord]['AMP1_CNT'],
                         'AMP2_CNT'                    : T134TaSumHd2Data[taRecord]['AMP2_CNT'],
                         'AMP3_CNT'                    : T134TaSumHd2Data[taRecord]['AMP3_CNT'],
                         'AMP4_CNT'                    : T134TaSumHd2Data[taRecord]['AMP4_CNT'],
                         'AMP5_CNT'                    : T134TaSumHd2Data[taRecord]['AMP5_CNT'],
                         'AMP6_CNT'                    : T134TaSumHd2Data[taRecord]['AMP6_CNT'],
                         'AMP7_CNT'                    : T134TaSumHd2Data[taRecord]['AMP7_CNT'],
                         })
                        break

            objMsg.printDblogBin(self.dut.dblData.Tables('P_DELTA_BURNISH_TA_SUM_COMBO'))

      if testSwitch.FE_0170519_407749_P_HSA_BP_ENABLE_DELTA_BURNISH_AND_OTF_CHECK:
         if self.dut.nextState == 'AFH3':

            curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)

            deltaBurnishChk_tbl = self.dut.dblData.Tables('P_AFH_DH_BURNISH_CHECK').tableDataObj()

            testType = self.params.get('testType', "burnish")
            activeHeater = self.params.get('activeHeater', "R")

            for record in deltaBurnishChk_tbl:
               if record['TEST_TYPE'] == testType and record['ACTIVE_HEATER'] == activeHeater:
                  self.dut.dblData.Tables('P_HSA_BP_DELTA_BURNISH_CHECK').addRecord({
                   'SPC_ID'                      : -1,
                   'OCCURRENCE'                  : occurrence,
                   'SEQ'                         : curSeq,
                   'TEST_SEQ_EVENT'              : testSeqEvent,
                   'HD_PHYS_PSN'                 : self.dut.LgcToPhysHdMap[record['HD_LGC_PSN']],
                   'HD_LGC_PSN'                  : record['HD_LGC_PSN'],
                   'TEST_TYPE'                   : record['TEST_TYPE'],
                   'ACTIVE_HEATER'               : record['ACTIVE_HEATER'],
                   'DELTA_BURNISH_CHECK'         : record['DELTA_BURNISH_CHECK'],
                   'HSA_BP_PN'                   : self.dut.HSA_BP_PN,
                  })

            objMsg.printDblogBin(self.dut.dblData.Tables('P_HSA_BP_DELTA_BURNISH_CHECK'))
      if testSwitch.FE_0258915_348429_COMMON_TWO_TEMP_CERT_SCRN_A00001 and self.dut.partNum[-3:] not in TP.RetailTabList and self.burnishretriedAFH1 == 1 :
         objMsg.printMsg("===============FE_0258915_348429_COMMON_TWO_TEMP_CERT_SCRN_A00001===============")
         objMsg.printMsg("BurnishFailedHeads %s " % self.dut.BurnishFailedHeads)
         if len(self.dut.BurnishFailedHeads):
            wrt_clr_1 ={}
            for hd in self.dut.BurnishFailedHeads:
               wrt_clr_1[hd] = []
            try:
               deltaBurnishChk_tbl = self.dut.dblData.Tables('P_AFH_DH_BURNISH_CHECK').tableDataObj()
            except:
               deltaBurnishChk_tbl = {}
            if deltaBurnishChk_tbl:
               for record in deltaBurnishChk_tbl:
                  if int(record['HD_PHYS_PSN']) in self.dut.BurnishFailedHeads and record['ACTIVE_HEATER'] == 'W' :
                     wrt_clr_1[int(record['HD_PHYS_PSN'])].append(float(record['WRT_HTR_CLR_1']))
               fail_List = []
               for hd in self.dut.BurnishFailedHeads:
                  if len(wrt_clr_1[hd]):
                     if sum(wrt_clr_1[hd])/len(wrt_clr_1[hd]) > TP.burnish_params_MaxWt_Clr: #78.0:
                        objMsg.printMsg("BurnishFailedHeads %d Mean Wrt_clr %4f exceeds the spec %4f,need to downgrade.!!!" % (hd,sum(wrt_clr_1[hd])/len(wrt_clr_1[hd]), TP.burnish_params_MaxWt_Clr))
                        fail_List.append(hd)
                     else:
                        objMsg.printMsg("BurnishFailedHeads %d Mean Wrt_clr %4f " % (hd,sum(wrt_clr_1[hd])/len(wrt_clr_1[hd])))
               if len(fail_List):
                  objMsg.printMsg("Same_Two_Temp_CERT_Downgrade Trigger %s" % fail_List)
                  if not self.downGradeOnFly(1, 14559):
                     ScrCmds.raiseException(14559, "BurnishFailedHeads exceed limit: %s" % fail_List)
                     
      if testSwitch.FE_0258915_348429_COMMON_TWO_TEMP_CERT_SCRN_A00002:
         try:
            deltaBurnishChk_tbl = self.dut.dblData.Tables('P_AFH_DH_BURNISH_CHECK').tableDataObj()
         except:
            deltaBurnishChk_tbl = {}
            
         if deltaBurnishChk_tbl:
            wrt_clr_1 ={}
            wrt_clr_2 ={}
            for hd in range(self.dut.imaxHead):
               wrt_clr_1[hd] = {}
               wrt_clr_2[hd] = {}
            objMsg.printMsg("===============FE_0258915_348429_COMMON_TWO_TEMP_CERT_SCRN_A00002===============")
            for record in deltaBurnishChk_tbl:
               if record['ACTIVE_HEATER'] == 'W' :
                  wrt_clr_1[int(record['HD_PHYS_PSN'])][int(record['TEST_PSN'])]= float(record['WRT_HTR_CLR_1'])
                  wrt_clr_2[int(record['HD_PHYS_PSN'])][int(record['TEST_PSN'])]= float(record['WRT_HTR_CLR_2'])
            fail_List = []
            for hd in range(self.dut.imaxHead):
               if wrt_clr_1[hd].has_key(0) and wrt_clr_1[hd].has_key(self.dut.numZones - 1) and wrt_clr_2[hd].has_key(self.dut.numZones - 1):
                  delta_ODID_Clr = wrt_clr_1[hd][0] - wrt_clr_1[hd][self.dut.numZones - 1]
                  delta_ID_Burnish = wrt_clr_2[hd][self.dut.numZones - 1] - wrt_clr_1[hd][self.dut.numZones - 1]
                  if delta_ODID_Clr > TP.burnish_params_delta_ODID and delta_ID_Burnish > TP.burnish_params_ID:
                     fail_List.append(hd)
                     objMsg.printMsg("BurnishFailedHeads: %d OD ID Delta Wrt_clr: %4f ID Burnish: %4f exceeds the spec, need to downgrade!!!" % (hd, delta_ODID_Clr, delta_ID_Burnish))
                  else:
                     objMsg.printMsg("BurnishFailedHeads: %d OD ID Delta Wrt_clr: %4f ID Burnish: %4f " % (hd, delta_ODID_Clr, delta_ID_Burnish))
            if len(fail_List) and self.dut.partNum[-3:] not in TP.RetailTabList:
               objMsg.printMsg("Same_Two_Temp_CERT_Downgrade Trigger %s" % fail_List)
               if not self.downGradeOnFly(1, 14559):
                  ScrCmds.raiseException(14559, "BurnishFailedHeads exceed limit: %s" % fail_List)

      if testSwitch.AFH2_FAIL_BURNISH_RERUN_AFH1 and self.dut.nextState in ['AFH1', 'AFH2',] :
         objMsg.printMsg("end of AFH test, burnishretriedAFH1=%d" %self.burnishretriedAFH1)
         if self.burnishretriedAFH1 == 1: # we are here becos rerun AFH1 passed
            self.burnishretriedAFH1 = 2
            try:
               self.dut.objData.update({'BurnishdHeads':self.dut.BurnishFailedHeads})
            except:
               objMsg.printMsg("Fail to save reAFH1 burnish head to objdata")
            self.dut.driveattr['RERUNAFH1'] = '1'
            #reststart
            self.dut.stateTransitionEvent = 'restartAtState'
            if testSwitch.RUN_TPINOMINAL1:
                self.dut.nextState = 'TPINOMINAL'
            else:
                self.dut.nextState = 'TRIPLET_OPTI_V2'
            #self.run()
      if testSwitch.FE_AFH3_TO_DO_BURNISH_CHECK:
         objMsg.printMsg("end of AFH3 test, dut.AFH3FailBurnish=%d" %self.dut.AFH3FailBurnish)
         if self.dut.AFH3FailBurnish == 1: # we are here becos rerun AFH1 passed    
            self.dut.AFH3FailBurnish += 1                                       
            try:
               self.dut.objData.update({'AFH3FailBurnish':self.dut.AFH3FailBurnish})
            except:
               objMsg.printMsg("Fail to save AFH3 burnish head to objdata")
            self.dut.driveattr['RERUNAFH3'] = '1'
            #reststart
            #self.dut.stateTransitionEvent = 'restartAtState'
           # self.dut.nextState = 'TRIPLET_OPTI'
            if self.dut.BG not in ['SBS']:
               self.run()
      if testSwitch.ENABLE_SMART_TCS_LIMITS_DATA_COLLECTION and self.dut.nextState == 'AFH2':
         if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT == 1:
            from AFH_Screens_DH import CAFH_Screens
            oAFH_Screens = CAFH_Screens()
            tcc1_loLimitWrtHt, tcc1_upLimitWrtHt = oAFH_Screens.SmartTccLimits()

      if testSwitch.FE_0338712_305538_P_AFH_CLR_SCREENING:
         from dbLogUtilities import DBLogCheck
         dblchk = DBLogCheck(self.dut)
         if ( dblchk.checkComboScreen(TP.T135_AFH_Clr_Screen_Spec) == FAIL ):
            if testSwitch.ENABLE_ON_THE_FLY_DOWNGRADE and self.downGradeOnFly(1, 14734):
               objMsg.printMsg('Failed for AFH Clr Screening, downgrade to %s as %s' % (self.dut.BG, self.dut.partNum))
            else:
               ScrCmds.raiseException(14734, 'Failed AFH Clr Screening @ Head : %s' % str(dblchk.failHead))
      if testSwitch.extern.FE_0366862_322482_CERT_DETCR_LIVE_SENSOR:
         #self.mFSO.St(TP.enableTASensor_11)
         self.mFSO.St(TP.enableLiveSensor_11)
         self.mFSO.saveSAPtoFLASH()    

      if testSwitch.FE_0360203_518226_2D_CTU_RDG_RDCLR_COMBO_SCREEN:
      
         if self.dut.nextState == 'AFH2':
            T185_RAMP_CYL = {}
            maxhead = 0
            try:
               T185Data = self.dut.dblData.Tables('P185_TRK_0_V3BAR_CALHD').tableDataObj()
            except:
               T185Data = {}
            if T185Data:     
               for index in range(len(T185Data)):
                   hd =int(T185Data[index]['HD_LGC_PSN'])
                   T185_RAMP_CYL[hd] = int(T185Data[index]['RAMP_CYL'])
                   if hd > maxhead: maxhead = hd
                   
            from dbLogUtilities import DBLogCheck
            dblchk = DBLogCheck(self.dut, 'AFH2 RD_CLR_Screening', verboseLevel=2)
            if (maxhead ==3 and T185_RAMP_CYL[3]>TP.T185_RDG_Screen_Spec and T185_RAMP_CYL[1]-T185_RAMP_CYL[0]>0) and dblchk.checkComboScreen(TP.T135_AFH2_RD_Clr_Screen_Spec) == FAIL:
            #if 1:
               if testSwitch.ENABLE_ON_THE_FLY_DOWNGRADE and self.downGradeOnFly(1, 14734):
                  objMsg.printMsg('Failed for AFH Clr Screening, downgrade to %s as %s' % (self.dut.BG, self.dut.partNum))
               else:
                  ScrCmds.raiseException(14734, 'Failed AFH2 RD_Clr combo Screening')

      if testSwitch.IS_2D_DRV == 0 and self.dut.BG in ['SBS'] and \
         self.dut.nextState in ['AFH2', 'AFH3'] and self.burnishretriedAFH1 == 0:
         self._deltaClrIDOD()

#----------------------------------------------------------------------------------------------------------
class CLLIWP(CState):
   """
    This class runs test 177 and uses paramters desgined to go before INIT_SYS.
    A better job of tuning VGAS will be performed in the Test 177 immediately preceding INIT_SYS from this
    point in the process.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):

      if testSwitch.HAMR: # and self.dut.nextState == 'AFH1': 
         from AFH_Screens_DH import CAFH_Screens
         from AFH import CdPES
         self.odPES = CdPES(TP.masterHeatPrm_11, TP.defaultOCLIM)
         oAFH_Screens = CAFH_Screens()
         self.odPES.St({'test_num':172, 'prm_name':'AFH PTP Coef Dump', 'timeout': 1800, 'CWORD1': (15,), 'spc_id':10001})
         
         prm_172_display_AFH_adapts_summary = TP.prm_172_display_AFH_adapts_summary.copy()
         prm_172_display_AFH_adapts_summary['spc_id'] = 10001
         oAFH_Screens.St(prm_172_display_AFH_adapts_summary)
         self.odPES.setIRPCoefs(self.dut.PREAMP_TYPE, self.dut.AABType, TP.PRE_AMP_HEATER_MODE, TP.clearance_Coefficients)
         self.odPES.St({'test_num':172, 'prm_name':'AFH PTP Coef Dump', 'timeout': 1800, 'CWORD1': (15,), 'spc_id':10002})
         prm_172_display_AFH_adapts_summary['spc_id'] = 10002
         oAFH_Screens.St(prm_172_display_AFH_adapts_summary)

#----------------------------------------------------------------------------------------------------------
class CpostAfh177(CState):
   """
    This class runs test 177 and uses paramters desgined to go before INIT_SYS.
    A better job of tuning VGAS will be performed in the Test 177 immediately preceding INIT_SYS from this
    point in the process.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if testSwitch.extern.OPTI_MAJ_REL_NUM >= 9 or (testSwitch.extern.OPTI_MAJ_REL_NUM == 7 and testSwitch.extern.OPTI_MIN_REL_NUM >= 1):
         from Process import CProcess
         oProcess = CProcess()
         oProcess.St(TP.pgaPostAFHGainCalPrm_177)


#----------------------------------------------------------------------------------------------------------
class CpostAFH335(CState):
   """
    This class runs test 335
      - Intended to be run following AFH in PRE2
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from Process import CProcess
      oProcess = CProcess()      
      oProcess.St(TP.MDW_SCAN_Prm_335)
      if testSwitch.FE_0158632_357260_P_ENABLE_TEST_163_MDW_QUALITY_CHECK:
         oProcess.St(TP.prm_163_MDW_QLTY_OD)
         oProcess.St(TP.prm_163_MDW_QLTY_ID)


#----------------------------------------------------------------------------------------------------------
class CAFH1_screens(CState):
   """
      Run AFH1 screens after HIRP.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params

      if dut.nextOper == 'PRE2':
         depList = ['AFH1']
      else:
         depList = []

      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from AFH_Screens_T135 import CAFH_Screens

      oAFH_Screens  = CAFH_Screens()

      oAFH_Screens.AFH_State = 1     # force the AFH state to AFH1

      if ( testSwitch.WA_0111581_341036_AFH_RUN_AFH1_SCREENS_AFTER_HIRP == 1):

         oAFH_Screens.crossStrokeClrCheck(TP.crossStrokeClrLimit)

         if testSwitch.AFH_ENABLE_CLR_RANGE_CHECK_IN_CROSS_STROKE_CHECK == 1:
            oAFH_Screens.clearanceRangeCheck(TP.clrRangeChkLimit)

      if ( testSwitch.AFH_ENABLE_TEST135_OD_ID_ROLLOFF_SCREEN == 1 ):
         oAFH_Screens.extreme_OD_ID_clearanceRangeCheck( TP.extreme_OD_ID_clearanceRangeCheck )


#----------------------------------------------------------------------------------------------------------
class CFAFH_frequencySelect(CState):
   """
      FAFH Frequency Selection state.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params

      if dut.nextOper == 'PRE2':
         depList = ['AFH1']
      else:
         depList = []

      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if not ( testSwitch.FE_0145389_341036_FAFH_ENABLE_FREQUENCY_SELECT_CAL == 1 ):
         objMsg.printMsg("FAFH Frequency Select State is currently disabled.")

      if ( testSwitch.FE_0145389_341036_FAFH_ENABLE_FREQUENCY_SELECT_CAL == 1 ):
         from AFH_FAFH import CFAFH
         oFAFH = CFAFH()
         oFAFH.runFAFH_frequencyCalibration()
         if testSwitch.extern.DB_0174652_357257_T74_CREATE_VERIFY_TEST_TRACKS_COMMAND:
            objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)


#----------------------------------------------------------------------------------------------------------
class CFAFH_trackPrep(CState):
   """
      FAFH Track Preparation
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params

      if dut.nextOper == 'PRE2':
         depList = ['AFH2']
      else:
         depList = []

      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if not ( testSwitch.FE_0145400_341036_FAFH_ENABLE_TRACK_PREP == 1 ):
         objMsg.printMsg("FAFH Track Preparation State is currently disabled.")

      if ( testSwitch.FE_0145400_341036_FAFH_ENABLE_TRACK_PREP == 1 ):
         from AFH_FAFH import CFAFH
         oFAFH = CFAFH()
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
         oFAFH.runFAFH_trackPrep()
         if testSwitch.extern.DB_0174652_357257_T74_CREATE_VERIFY_TEST_TRACKS_COMMAND:
#           oFAFH.runFAFH_AR_measurement('', 1)
            objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

      if testSwitch.extern.FE_0366862_322482_CERT_DETCR_LIVE_SENSOR:
         from base_TccCal import CTccCalibration
         self.oTccCal = CTccCalibration(self.dut)
         self.oTccCal.saveThresholdToHap(20, UseAFHDbLog=0)
         #self.oFSO.St(TP.enableTASensor_11)
         from FSO import CFSO
         self.oFSO = CFSO()
         self.oFSO.St(TP.enableLiveSensor_11)
         self.oFSO.St(TP.disableTASensor_11)
         self.oFSO.saveSAPtoFLASH()

#----------------------------------------------------------------------------------------------------------
class CFAFH_calibration(CState):
   """
      FAFH Calibration
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params

      if dut.nextOper == 'PRE2':
         depList = ['AFH2']
      else:
         depList = []

      if testSwitch.ENABLE_FAFH_STATE_CHECKING == 1:
         if (dut.nextOper == 'FNC2') and ( dut.nextState == 'FAFH_CAL_TEMP_1' ):
            depList.append( 'AFH3' )
         if (dut.nextOper == 'PRE2') and ( dut.nextState == 'FAFH_CAL_TEMP_1' ):
            depList.append( 'AFH3' )

         if (dut.nextOper == 'CRT2') and ( dut.nextState == 'FAFH_CAL_TEMP_2' ):
            depList.append( 'AFH4' )

      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if not ( testSwitch.FE_0145412_341036_FAFH_ENABLE_AR_MEASUREMENT == 1 ):
         objMsg.printMsg("FAFH AR Measurement Calibration State is currently disabled.")

      if ( testSwitch.FE_0145412_341036_FAFH_ENABLE_AR_MEASUREMENT == 1 ):
         from AFH_FAFH import CFAFH
         oFAFH = CFAFH()
         oFAFH.runFAFH_AR_measurement(self.params['tempIndexStr'])
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

            
#----------------------------------------------------------------------------------------------------------
class CAFHDeltasTables(CState):
   """
   Calculates deltas between reader and writer DAC measurements.
    - Data from P135_FINAL_CONTACT
    - Generates temporary P_RD_WRT_DAC_DELTA table for Grading use only
    Parameters:
      None
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      seq, occurrence, testSeqEvent = self.dut.objSeq.registerCurrentTest(0)

      wrRdDacData = self.dut.dblData.Tables('P135_FINAL_CONTACT').tableDataObj()

      min_SPC_ID = int(self.params.get('MIN_SPC_ID', 20000))
      max_SPC_ID = int(self.params.get('MAX_SPC_ID', 29999))
      MSRD_INTRPLTD = str(self.params.get('MSRD_INTRPLTD', 'M'))

      objMsg.printMsg('Building Weak Write Delta BER table')
      for item in wrRdDacData:
         if not item.has_key('SPC_ID') and testSwitch.virtualRun:
            item['SPC_ID'] = 0
         if int(item['SPC_ID']) >= min_SPC_ID\
               and int(item['SPC_ID']) <= max_SPC_ID\
               and str(item['MSRD_INTRPLTD']) == MSRD_INTRPLTD:

            self.dut.dblData.Tables('P_RD_WRT_DAC_DELTA').addRecord(
               {
               'SPC_ID'                      : int(item['SPC_ID']),
               'OCCURRENCE'                  : occurrence,
               'SEQ'                         : seq,
               'TEST_SEQ_EVENT'              : testSeqEvent,
               'HEAD'                        : item['HD_PHYS_PSN'],
               'ZONE'                        : item['DATA_ZONE'],
               'CNTCT_DAC_DELTA'             : float(item['RD_CNTCT_DAC']) - float(item['WRT_CNTCT_DAC']),
               'CLR_DELTA'                   : float(item['RD_CLR']) - float(item['WRT_CLR']),
               'MSRD_INTRPLTD'               : item['MSRD_INTRPLTD'],
               'CONTACT_TEMP'                : item['CONTACT_TEMP'],
               })

      objMsg.printDblogBin(self.dut.dblData.Tables('P_RD_WRT_DAC_DELTA'))


#----------------------------------------------------------------------------------------------------------
class CGenerateAFH_Coeff(CState):
   """
      Generate AFH coefficients
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params

      if dut.nextOper == 'PRE2':
         depList = [ 'AGC_JOG', 'AFH1', 'RW_GAP_CAL' ]
         #depList = []
      else:
         depList = []

      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      #from PowerControl import objPwrCtrl
      #objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1) # add powercycle here to avoid hang?
      from Process import CProcess
      oProcess = CProcess()
      #oProcess.St(TP.spinupPrm_1)

      #oPreamp = CPreAmp()

      #oPreamp.setPreAmpHeaterMode(TP.setPreampHeaterMode_178, TP.PRE_AMP_HEATER_MODE)
      #odPES  = AFH.CdPES(TP.masterHeatPrm_11, TP.defaultOCLIM)
      #odPES.setIRPCoefs(self.dut.PREAMP_TYPE, self.dut.AABType, TP.PRE_AMP_HEATER_MODE, TP.clearance_Coefficients, forceRAPWrite = 1)

      oProcess.St({'test_num':172, 'prm_name':'P172_AFH_PTP_COEF', 'timeout': 800, 'CWORD1': 15, 'spc_id':1000})
      oProcess.St({'test_num':172, 'prm_name':'P172_AFH_CLEARANCE', 'timeout': 800, 'CWORD1': 5, 'spc_id':1000})
      oProcess.St({'test_num':172, 'prm_name':'P172_AFH_WORKING_ADAPTS', 'timeout': 800, 'CWORD1': 4, 'spc_id':1000})

      st192Prm = TP.prm_192_base.copy()

      CWORD2_MASK = 0x0100    # save to flash
      if testSwitch.IN_DRIVE_AFH_COEFF_PER_HEAD_GENERATION_SUPPORT_DATA_COLLECTION:
         CWORD2_MASK = 0

      if self.params.get('CoeffDone', 0)== 0:
         st192Prm['CWORD2'] = 0x0004|CWORD2_MASK           #WPTP coeffs
         st192Prm['BACKOFF_HTR_DAC'] = 20
         oProcess.St(st192Prm)

         st192Prm = TP.prm_192_base.copy()
         if (self.dut.isDriveDualHeater == 1):
            st192Prm['CWORD2'] = 0x0001|CWORD2_MASK           #READER coeffs
            st192Prm['DUAL_HEATER_CONTROL'] = (1,0xFF)        #HO coeffs
            oProcess.St(st192Prm)

            st192Prm['DUAL_HEATER_CONTROL'] = (0,0xFF)        #WRITER coeffs
            st192Prm['CWORD2'] = 0x0002|CWORD2_MASK           #WPH coeffs
         else:
            st192Prm['CWORD2'] = 0x0001|0x0002|CWORD2_MASK    #Both HO & WPH coeffs

         if testSwitch.IN_DRIVE_AFH_COEFF_PER_HEAD_GENERATION_SUPPORT_DATA_COLLECTION:
            st192Prm['CWORD2'] = st192Prm['CWORD2']&0xF0FF
         oProcess.St(st192Prm)
      else:
         st192Prm['CWORD2'] = 0x0010|CWORD2_MASK              #Adj wph measured clr
         oProcess.St(st192Prm)
         if not testSwitch.IN_DRIVE_AFH_COEFF_PER_HEAD_GENERATION_SUPPORT_DATA_COLLECTION:
            # adjust AFH1 data for TCS calculation in CRT2
            from AFH_SIM import CAFH_Frames
            self.frm = CAFH_Frames()
            from MathLib import CAFH_Computations
            self.mth = CAFH_Computations()

            afhModesToAdjust = [ AFH_MODE, AFH_MODE_TEST_135_INTERPOLATED_DATA, AFH_MODE_TEST_135_EXTREME_ID_OD_DATA ]

            # expect the frames data is already loaded
            for frame in self.frm.dPesSim.DPES_FRAMES:
               if (frame['mode'] in afhModesToAdjust ): # check to make sure it is AFH data
                  iHead = frame['LGC_HD']
                  cyl = frame['Cylinder']

                  if testSwitch.IS_DH_CODE_ENABLED == 1:
                     if ( frame['Heater Element'] == WRITER_HEATER_INDEX ):
                        frame['Write Clearance'] = self.mth.fromClrToInDrvAdjClr(iHead, cyl, frame['Write Clearance'], "WrtClr")
                        #if self.dut.isDriveDualHeater == 1:
                        #   frame['Read Clearance']  = self.mth.fromClrToInDrvAdjClr(iHead, cyl, frame['Read Clearance'], "WrtClr")
                        #else:
                        #   frame['Read Clearance']  = self.mth.fromClrToInDrvAdjClr(iHead, cyl, frame['Read Clearance'], "RdClr")

                     #if ( frame['Heater Element'] == READER_HEATER_INDEX ):
                        # READER_HEATER WrtClr we do NOT adjust.
                     #   frame['Read Clearance']  = self.mth.fromClrToInDrvAdjClr(iHead, cyl, frame['Read Clearance'], "RdClr")
                  else:
                     # if SH code finds READER_HEATER data then it will adjust it.
                     #frame['Read Clearance']  = self.mth.fromClrToInDrvAdjClr(iHead, cyl, frame['Read Clearance'], "RdClr")
                     frame['Write Clearance'] = self.mth.fromClrToInDrvAdjClr(iHead, cyl, frame['Write Clearance'], "WrtClr")
                  objMsg.printMsg("wrtClr = %d" % frame['Write Clearance'])
            self.frm.display_frames(3)

      #objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1) # add powercycle here to avoid hang?
      oProcess.St({'test_num':172, 'prm_name':'P172_AFH_PTP_COEF', 'timeout': 800, 'CWORD1': 15, 'spc_id':2000})
      oProcess.St({'test_num':172, 'prm_name':'P172_AFH_CLEARANCE', 'timeout': 800, 'CWORD1': 5, 'spc_id':2000})
      oProcess.St({'test_num':172, 'prm_name':'P172_AFH_WORKING_ADAPTS', 'timeout': 800, 'CWORD1': 4, 'spc_id':2000})


#----------------------------------------------------------------------------------------------------------
class CMeasureAR(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params

      depList = [ 'AGC_JOG', 'AFH2' ]


      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      objMsg.printMsg("RUN_T191_HIRP_OPEN_LOOP = %d" % testSwitch.RUN_T191_HIRP_OPEN_LOOP)

      import AR2
      from AFH import CAFH
      self.oAR = AR2.CAR()
      self.oAFH = CAFH()

      self.oAR.lmt.maxDAC = (2 ** TP.dpreamp_number_bits_DAC.get(self.dut.PREAMP_TYPE, 0)) - 1
      coefs = self.oAFH.getClrCoeff(TP.clearance_Coefficients, self.dut.PREAMP_TYPE, self.dut.AABType)

      if testSwitch.FE_0174845_379676_HUMIDITY_SENSOR_CALIBRATION:
         from Temperature import CTemperature
         self.oTemp = CTemperature()
         self.oTemp.measureHumidity(spc_id=205)

      if testSwitch.FE_0139388_341036_AFH_DUAL_HEATER_V32_ABOVE == 1:
         self.oAFH.getDHStatus( self.dut.PREAMP_TYPE, self.dut.AABType, TP.clearance_Coefficients )
         if testSwitch.BF_0187702_340210_SNGL_HTR_2_PASS == 1 and not self.dut.isDriveDualHeater: #only for not DH drives
            singleHtr2Pass = 1
         else:
            singleHtr2Pass = 0
         self.oAR.measureAR_DH(TP.AR_params, self.params.get('exec231', 0), singleHtr2Pass)
      else:
         if testSwitch.BF_0187702_340210_SNGL_HTR_2_PASS == 1 :
            singleHtr2Pass = 1
         else:
            singleHtr2Pass = 0
         self.oAR.measureAR(TP.prm_191_0002, TP.AR_params, TP.test178_scale_offset, self.params.get('exec231', 0), singleHtr2Pass)

      if testSwitch.FE_0174845_379676_HUMIDITY_SENSOR_CALIBRATION:
         self.oTemp.measureHumidity(spc_id=205)

      # ++++++++++++++++++++++ Apply HIRP correction to All AFH Data ++++++++++++++++++++++++++++++++++++++

      import AFH_mainLoop
      self.oAFH_test135 = AFH_mainLoop.CAFH_test135()
      self.oAFH_test135.displayClearanceAndHeatUsingTest172AndSaveRAPtoFLASH( self.oAR.spcID )
      self.oAFH_test135.St({ 'test_num':172, 'prm_name':'P172_CLR_COEF_ADJ', 'timeout': 1800, 'CWORD1': (20,), 'spc_id': self.oAR.spcID + 101 })
      self.oAFH_test135 = None
      self.oAR = None      # Allow Garbage Collection


#----------------------------------------------------------------------------------------------------------
class CCleanUpBadPattern(CState):
   """
   Class that do AFH Clean up state prior auto replug, to prevent bad pattern from previous AFH4 test track leak to next state.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      try:
         objMsg.printMsg('Drive fail after AFH4 and do not pass AFH Clean up yet. AFH Clean up require before fail drive')
         objPwrCtrl.powerCycle(useESlip=1)
         # dnld TGT code
         from Serial_Download import CDnldCode
         oDnldF3Code = CDnldCode(self.dut,{'CODES': ['TGT','OVL'],})
         oDnldF3Code.run()
         # AFH Clean up
         from base_TccCal import CTrackCleanup
         oAFHCleanUp = CTrackCleanup(self.dut,{})
         oAFHCleanUp.run()
      except Exception, e:
         import traceback
         objMsg.printMsg('Exception in AFH cleanup')
         objMsg.printMsg(traceback.format_exc())


#----------------------------------------------------------------------------------------------------------
class CPrepareReRun_AFH2(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from AFH import CdPES
      from AFH_constants import stateTableToAFH_internalStateNumberTranslation      

      self.odPES = CdPES(TP.masterHeatPrm_11, TP.defaultOCLIM)
      self.odPES.mFSO.getZoneTable() # get number of heads and zones on drive
      self.odPES.frm.readFramesFromCM_SIM()

      objMsg.printMsg("moveAFHStateInfoFromStateX_toStateY")
      self.odPES.frm.moveAFHStateInfoFromStateX_toStateY(
         stateTableToAFH_internalStateNumberTranslation["AFH2"] , "AFH2",
         stateTableToAFH_internalStateNumberTranslation["AFH2A"], "AFH2A")

      self.odPES.frm.writeFramesToCM_SIM()
      self.odPES.frm.display_frames( 2 )


#----------------------------------------------------------------------------------------------------------
class T74PrintOut(CState):
   """
   Display T74 Parameter file
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from Process import CProcess
      oProcess = CProcess()
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      oProcess.St(TP.prm_display_fafh_parm_file_074_06)


#----------------------------------------------------------------------------------------------------------
class FAFHparamInit_Write(CState):
   """
   Initialize the FAFH parameter file and Write into the SIM
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from Process import CProcess
      oProcess = CProcess()
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      oProcess.St(TP.prm_init_fafh_param_file_074_07)
      oProcess.St(TP.prm_write_fafh_param_file_074_08)
            