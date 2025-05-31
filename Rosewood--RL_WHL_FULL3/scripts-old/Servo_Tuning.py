#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Servo Tuning State Module
#  - PRE2 Servo state classes
#
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/12/28 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Servo_Tuning.py $
# $Revision: #40 $
# $DateTime: 2016/12/28 20:13:05 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Servo_Tuning.py#40 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
import Constants
from Constants import *
from TestParamExtractor import TP
from State import CState
import MessageHandler as objMsg
from PowerControl import objPwrCtrl
import ScrCmds
from FSO import CFSO
from Process import CProcess
from Utility import CUtility


#----------------------------------------------------------------------------------------------------------
class CMdwCal(CState):
   """
      Description: Class that will perform a 1 stop Servo Calibration
      Base: Standard MDW cals, with the option to run T43 radial cals for MD drives
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = ['HEAD_CAL']
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def Clear_MDW_OFST_WithRetry(self, prm = TP.ClearMDWOffset_73, retrycnt = 0):
      while 1:
         try:
            #self.oSrvOpti.St(TP.spinupPrm_1)
            self.oSrvOpti.St(prm)
            break # passed with no error code
         except:
            if retrycnt > 0:
               objMsg.printMsg("PwrCycle & retry Test73. Num Retries left %d \n" % retrycnt)
               objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
               retrycnt -= 1
               if 'T73_RETRY' in TP.Proc_Ctrl30_Def:
                  self.dut.driveattr['PROC_CTRL30'] = '0X%X' % (int(self.dut.driveattr.get('PROC_CTRL30', '0'),16) | TP.Proc_Ctrl30_Def['T73_RETRY'])
            else: # no retries remaining
               raise

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from Servo import CServoOpti
      self.oSrvOpti = CServoOpti()
      self.oFSO = CFSO()
      
      objMsg.printMsg("Using class frm base.")

      if testSwitch.FE_0120496_231166_DISABLEZAP_IN_MDWCALS:
         self.oSrvOpti.St(TP.zapPrm_175_zapOff)

      # Set channel registers through SAP
      if testSwitch.extern.FE_0115982_357915_SET_CHANNEL_REG_IN_SAP:
         self.oSrvOpti.setChannelRegistersInSAP()
      self.oSrvOpti.setQuietSeek(TP.quietSeekPrm_11, setQSeekOn = 0) #disable quiet seek
      #Start servo calibrations
      self.oSrvOpti.setOClim({},TP.mdwOCLIM,updateFlash = 1)

      self.oSrvOpti.St(TP.spindownPrm_2)
      self.oSrvOpti.St(TP.spinupPrm_1)

      if testSwitch.shockSensorTestEnabled:
         self.oSrvOpti.St(TP.shocksensorPrm)

      from base_SerialTest import CCustUniqSAPCfg
      ZGS_pn = CCustUniqSAPCfg(self.dut,{}).ZGSEnabled(self.dut.partNum)
      if ZGS_pn=='enabled' or testSwitch.ZGS_Enabled:
         try: self.oSrvOpti.zgsTest(TP.zgsPrm_52)
         except: pass
         zgsHlthVal = int(self.dut.dblData.Tables('P052_ZGS_CAL_DATA').tableDataObj()[-1]['ZGS_HLTH'])

         if zgsHlthVal == 2:
            self.dut.driveattr['ZERO_G_SENSOR'] = "1"
            objMsg.printMsg("Zero G Sensor detected and working.")
         else:
            self.dut.driveattr['ZERO_G_SENSOR'] = "0"
            objMsg.printMsg("Drive unable to support Zero G sensor")
            if ZGS_pn == 'enabled' and testSwitch.FE_0122938_231166_FAIL_IF_ZGS_REQ_BY_PN:
               ScrCmds.raiseException(14582, "ZGS Sensor Failed with health %s != 2 for HDA PN %s" % (zgsHlthVal,self.dut.partNum))
      else:
         self.dut.driveattr['ZERO_G_SENSOR'] = "NA"

      if testSwitch.FE_0143702_325269_P_PRESSURE_SENSOR_SUPPORT:
         if testSwitch.virtualRun:
            import cmEmul
            cmEmul.ErrorCode = 0


         from st054Params_AFH import getSelfTest054Dictionary

         if testSwitch.BF_0166991_231166_P_USE_PROD_MODE_DEV_PROD_HOSTSITE_FIX:
            if ConfigVars[CN]['PRODUCTION_MODE'] == 0:
               siteName = 'LCO'
            else:
               siteName = 'OTHER'
         else:
            # Returns-> ('GetSiteconfigSetting', {'CMSHostSite': 'LCO'})
            siteName = RequestService('GetSiteconfigSetting','CMSHostSite')[1].get('CMSHostSite','NA')

         headVendor = self.dut.HGA_SUPPLIER

         if testSwitch.FE_0139633_341036_AFH_NEW_PROGRAM_NAME_FUNCTION == 1:
            from ProgramName import getProgramNameGivenTestSwitch
            programName = getProgramNameGivenTestSwitch( testSwitch )
         else:
            programName = TP.program


         # Note to D. Klingbeil - this shouldn't be there, but for some reason Muskie is the programName during VE.
         if testSwitch.virtualRun:
            if programName == 'Muskie':
               programName = 'Tambora'

         pressureSensorCalParams = getSelfTest054Dictionary(programName, self.dut.AABType, siteName, headVendor)
         if testSwitch.FE_0159615_448877_P_ALLOW_T054_TO_FAIL:
            self.oSrvOpti.St(pressureSensorCalParams)              # Calibrate the Pressure Sensor
         else:
            try:
               self.oSrvOpti.St(pressureSensorCalParams)              # Calibrate the Pressure Sensor
            except:
               objPwrCtrl.powerCycle(5000,12000,10,10, useESlip=1)         # Any failure ... go ahead and power cycle so we can continue. Should be temporary?
               pass

      if testSwitch.pressureSensorEnabled:
         self.oSrvOpti.St(TP.prm_54_001)

      if testSwitch.ENABLE_SINGLE_STAGE_IN_DAULSTAGE_DRV:
         self.oSrvOpti.St(TP.enableSingleStage)
         #self.oSrvOpti.St(TP.pztCal_232)
         self.oFSO.saveSAPtoFLASH()

      if testSwitch.pztCalTestEnabled:
         self.oSrvOpti.St(TP.pztCal_332_2)
      if not testSwitch.FE_0162081_007955_MDWCAL_RUN_T163_T335_AFTER_T185:
         if testSwitch.FE_0134715_211118_ENABLE_TEST_335: # Enable MDW scan in test process
            if testSwitch.WA_0162362_007955_SPLIT_TEST_335_INTO_2_CALLS: # 1st run OD/MD, 2nd run ID ( w/ error limits applied )
               self.oSrvOpti.St(TP.MDW_SCAN_OD_MD_Prm_335)
               self.oSrvOpti.St(TP.MDW_SCAN_ID_Prm_335)
            else:
               self.oSrvOpti.St(TP.MDW_SCAN_Prm_335)
         if testSwitch.FE_0158632_357260_P_ENABLE_TEST_163_MDW_QUALITY_CHECK:
            self.oSrvOpti.St(TP.prm_163_MDW_QLTY_OD)
            self.oSrvOpti.St(TP.prm_163_MDW_QLTY_ID)

      import time
      from Rim import objRimType
      if testSwitch.FE_SGP_81592_ENABLE_FLEX_BIAS_CAL_T136_IN_MDWCAL:
         try:
            self.oSrvOpti.St(TP.flexBiasCalibration_136_MDW)
         except:
            if objRimType.IsLowCostSerialRiser():
               try:
                  objMsg.printMsg('Retry by PowerCycle() with ESlip for fixing EC11049 SP HDSTR')
                  time.sleep(60)
                  objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
                  TP.flexBiasCalibration_136_MDW['timeout'] = TP.flexBiasCalibration_136_MDW['timeout']*2
                  self.oSrvOpti.St(TP.flexBiasCalibration_136_MDW)
                  TP.flexBiasCalibration_136_MDW['timeout'] = TP.flexBiasCalibration_136_MDW['timeout']/2
               except:
                  objMsg.printMsg('Retry again by PowerCycle()with ESlip for fixing EC11049 SP HDSTR')
                  time.sleep(60)
                  objPwrCtrl.powerCycle()
                  TP.flexBiasCalibration_136_MDW['timeout'] = TP.flexBiasCalibration_136_MDW['timeout']*2
                  self.oSrvOpti.St(TP.flexBiasCalibration_136_MDW)
                  TP.flexBiasCalibration_136_MDW['timeout'] = TP.flexBiasCalibration_136_MDW['timeout']/2
            else: raise

      if testSwitch.FE_0123983_399481_SNO_IN_MDW:
         self.oSrvOpti.doSNO(TP.mdw_152, TP.mdw_notches_152)

      if testSwitch.TRUNK_BRINGUP:   # add for trunk code only for T47 failure
         self.oSrvOpti.St(TP.spindownPrm_2)
         self.oSrvOpti.St(TP.spinupPrm_1)
               
      RampDetectTestPrmDsd = TP.RampDetectTestPrm_185.copy()
      if testSwitch.AGC_SCRN_DESTROKE ==1 or (testSwitch.AGC_SCRN_DESTROKE_FOR_SBS == 1 and self.dut.BG in ['SBS']):
         origPaddingSize = TP.RampDetectTestPrm_185['ID_PAD_TK_VALUE']
         import types
         if type(origPaddingSize) == types.TupleType:
            origPaddingSize = origPaddingSize[0]
         RampDetectTestPrmDsd['ID_PAD_TK_VALUE'] = origPaddingSize + self.dut.IDExtraPaddingSize

      try:
         self.oSrvOpti.St(TP.vCatCal_Internal_47)
      except:
         objPwrCtrl.powerCycle(5000,12000,10,10, useESlip=1)

      if testSwitch.FE_0184102_326816_ZONED_SERVO_SUPPORT:
         if testSwitch.CHEOPSAM_LITE_SOC:
            # add another T73 calibration to find better track offset accuracy
            self.Clear_MDW_OFST_WithRetry(TP.ClearMDWOffset_73_2)
      
      if testSwitch.extern.FE_0118730_010200_T47_AND_T189_MDW_CAL_TTR == 0:
         for i in range(2):
            try:
               self.oSrvOpti.St(TP.tmffCalPrm_13)
               break
            except ScriptTestFailure, failureData:
               if i == 0 and self.dut.driveattr.get('PROC_CTRL9') != '1' and failureData[0][2] in [10427,11216] and \
                  testSwitch.ENABLE_ON_THE_FLY_DOWNGRADE and self.downGradeOnFly(1, failureData[0][2]):
                  self.dut.driveattr['PROC_CTRL9'] = '1'
               else:
                  raise failureData

      for i in range(2):
         try:
            self.oSrvOpti.St(TP.radialCalPrm_43)
            break
         except ScriptTestFailure, failureData:
            if i == 0 and self.dut.driveattr.get('PROC_CTRL9') != '1' and failureData[0][2] in [10427,11216] and \
               testSwitch.ENABLE_ON_THE_FLY_DOWNGRADE and self.downGradeOnFly(1, failureData[0][2]):
               self.dut.driveattr['PROC_CTRL9'] = '1'
            else:
               raise failureData   
         except Exception, e:
            if objRimType.IsLowCostSerialRiser():
               try:
                  objMsg.printMsg('Retry by PowerCycle() with ESlip for fixing EC11049 SP HDSTR')
                  time.sleep(60)
                  objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
                  TP.radialCalPrm_43['timeout'] = TP.radialCalPrm_43['timeout']*2
                  self.oSrvOpti.St(TP.radialCalPrm_43)
                  TP.radialCalPrm_43['timeout'] = TP.radialCalPrm_43['timeout']/2
                  break
               except:
                  objMsg.printMsg('Retry again by PowerCycle()with ESlip for fixing EC11049 SP HDSTR')
                  time.sleep(60)
                  objPwrCtrl.powerCycle()
                  TP.radialCalPrm_43['timeout'] = TP.radialCalPrm_43['timeout']*2
                  self.oSrvOpti.St(TP.radialCalPrm_43)
                  TP.radialCalPrm_43['timeout'] = TP.radialCalPrm_43['timeout']/2
                  break
            else:
               raise e
      try:
         self.oSrvOpti.St(TP.headSkewCalPrm_43)
      except:
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      if testSwitch.IS_2D_DRV:
         try:
            self.oSrvOpti.St(TP.srvSectorOffsetPrm_45)
         except:
            self.oSrvOpti.St(TP.srvSectorOffsetPrm_45) # retry and raise if still fail
         self.oSrvOpti.St(TP.vCatCal_02Prm_47)

      
      if testSwitch.FE_0131794_426568_RUN_T25_BEFORE_T185:
         # add a call to test 25 L/UL before calling test 185 for better ramp detection after excercising Head Stack
         self.oSrvOpti.St(TP.pre185_LULsweep_25)

      # RAMP detection...
      if self.dut.driveattr['SCOPY_TYPE'] != 'MDW':
         objMsg.printMsg("ASSW(MDSW) Media detected. Modify RAMP detect parameters.")
         RampDetectTestPrmDsd['PAD_TK_VALUE'] = 4000
         RampDetectTestPrmDsd['ID_PAD_TK_VALUE'] = 1900
         RampDetectTestPrmDsd['GB_BY_RAMP_CYL_P1'] = 5000
         RampDetectTestPrmDsd['GB_BY_RAMP_CYL_P2'] = 4000
         RampDetectTestPrmDsd['MIN_RAMPCYL_REQ'] = 550
      self.RampDetect(RampDetectTestPrmDsd)


      if testSwitch.FE_0162081_007955_MDWCAL_RUN_T163_T335_AFTER_T185:
         if testSwitch.FE_0134715_211118_ENABLE_TEST_335 == 1:
            if testSwitch.WA_0162362_007955_SPLIT_TEST_335_INTO_2_CALLS:
               self.oSrvOpti.St(TP.MDW_SCAN_OD_MD_Prm_335)
               self.oSrvOpti.St(TP.MDW_SCAN_ID_Prm_335)
            else:
               self.oSrvOpti.St(TP.MDW_SCAN_Prm_335)

         if testSwitch.FE_0158632_357260_P_ENABLE_TEST_163_MDW_QUALITY_CHECK:
            self.oSrvOpti.St(TP.prm_163_MDW_QLTY_OD)
            self.oSrvOpti.St(TP.prm_163_MDW_QLTY_ID)

      if testSwitch.FE_0111377_345334_RUN_T43_BEFORE_T189 :
         self.oSrvOpti.St(TP.headSkewCalPrm_43)

#      if testSwitch.WA_0256539_480505_SKDC_M10P_BRING_UP_DEBUG_OPTION:
#         self.oSrvOpti.St(TP.MDW_QUALITY_SCAN_Prm_335)

      try:
         if testSwitch.extern.FE_0118730_010200_T47_AND_T189_MDW_CAL_TTR and hasattr(TP, 'dcSkewCalTTRPrm_189'):
            self.oSrvOpti.St(TP.dcSkewCalTTRPrm_189)
         else:
            self.dut.driveattr['PROC_CTRL55'] = '0'
            for i in range(2):
               try:
                  self.oSrvOpti.St(TP.dcSkewCalPrm_189)
                  break
               except:
                  objPwrCtrl.powerCycle(5000,12000,10,10, useESlip=1)
      except ScriptTestFailure, (failureData): 
         if testSwitch.extern.FE_0118730_010200_T47_AND_T189_MDW_CAL_TTR and hasattr(TP, 'dcSkewCalTTRPrm_189'):
            self.dut.stateTransitionEvent = 'reRunMDW'
            objMsg.printMsg('dcSkewCalPrm_189 fail, rerun')
            return
         elif failureData[0][2] in [10806]:
            if 'T189_10806' in TP.Proc_Ctrl30_Def and not (int(self.dut.driveattr['PROC_CTRL30'],16) & TP.Proc_Ctrl30_Def['T189_10806']):
               self.dut.driveattr['PROC_CTRL30'] = '0X%X' % (int(self.dut.driveattr.get('PROC_CTRL30', '0'),16) | TP.Proc_Ctrl30_Def['T189_10806'])
               self.dut.stateTransitionEvent = 'restartAtState'
               self.dut.nextState = 'DNLD_CODE'
               return
            else:
               raise
         else:
            raise

      if testSwitch.M11P_BRING_UP or testSwitch.M11P:
         self.oSrvOpti.St(TP.pesMeasurePrm_33_M11P)
         self.oSrvOpti.St(TP.Enable_High_BW_Controller_1)
         self.oSrvOpti.St(TP.enableHiBWController_Single_Cal)

      if testSwitch.pztCalTestEnabled:
         self.oSrvOpti.St(TP.pztCal_332)
      self.oSrvOpti.MDWCalComplete()

      self.oSrvOpti.enableFaskSeekMode()
      if testSwitch.modifyRunTimeServoController:
         if testSwitch.FE_0122163_357915_DUAL_STAGE_ACTUATOR_SUPPORT:
            if testSwitch.FE_0112192_345334_ADD_T56_FOR_PZT_CAL:
               if testSwitch.FE_0112311_345334_ADD_SERVO_SPINUP_BEFORE_T56:
                  self.oSrvOpti.St(TP.spinupPrm_1)
               self.oSrvOpti.St(TP.enableHiBWController_Single)
               self.oSrvOpti.St(TP.enableHiBWController_Single_Cal)
               self.oSrvOpti.St(TP.enableHiBWController_Dual_Cal)
            else:
               self.oSrvOpti.St(TP.enableHiBWController_Dual)
         else:
            self.oSrvOpti.St(TP.enableHiBWController)

      if testSwitch.M11P_BRING_UP or testSwitch.M11P:
#         self.oSrvOpti.St(TP.Enable_High_BW_Controller_2)    # Temporary comment until phase cal tuning is complete.
         newPrm_33 = TP.pesMeasurePrm_33_M11P.copy()
         newPrm_33['spc_id'] = 2
         self.oSrvOpti.St(newPrm_33)
      self.oFSO.saveSAPtoFLASH()

      if not testSwitch.FE_SGP_81592_MOVE_MDW_TUNING_TO_SVO_TUNE_STATE:
         self.oSrvOpti.setOClim({},TP.defaultOCLIM,updateFlash = 1)
         self.oSrvOpti.servoLinCal(TP.servoLinCalPrm_150,TP.CRRO_IRRO_Prm_46, runReal = 1, sampling=1)

         # Start CRRO, IRRO, T33 before chrome cal
         if testSwitch.WA_0256539_480505_SKDC_M10P_BRING_UP_DEBUG_OPTION:
            
            self.oSrvOpti.St(TP.CRRO_IRRO_Prm_46) #CRRO,IRRO
            self.oSrvOpti.St(TP.CRRO_IRRO_RealMode_Prm_46) #CRRO,IRRO
            self.oSrvOpti.St(TP.prm_257_WirroMeas_SKDC_SERVO_TEST)

            newPrm_33_test_cyl = 0x0100
            newPrm_33_end_cyl = min( self.dut.maxTrack) - 0x0100
            newPrm_33 = TP.pesMeasurePrm_33.copy()
            newPrm_33.update({
                              'TEST_CYL': self.oSrvOpti.oUtility.ReturnTestCylWord(newPrm_33_test_cyl),
                              'END_CYL' : self.oSrvOpti.oUtility.ReturnTestCylWord(newPrm_33_end_cyl),
                              'NUM_SAMPLES' : ((newPrm_33_end_cyl - newPrm_33_test_cyl) / 0x1000), #"AUD_FREQ",0x1000
                              "MAX_RRO_LIMIT"             : (2000,),
                              "MAX_NRRO_LIMIT"            : (500,),
            })
            if testSwitch.FE_0139688_395340_P_T56_T33_TO_CAPTURE_EC14787_HIGH_NRRO:
               self.oSrvOpti.St(TP.prm_056_uAct_Dual_Stage)
            self.oSrvOpti.St( newPrm_33 )

            self.oSrvOpti.St(TP.prm_56_PZT_cal_SKDC_SERVO_TEST)
            self.oSrvOpti.St( newPrm_33 )
         # End of CRRO, IRRO, T33

         try:
            self.oSrvOpti.chromeCal(TP.chromeCalPrm_193)
         except ScriptTestFailure, (failureData):
            ec = failureData[0][2]
            if ec in [10414] and testSwitch.ENABLE_BYPASS_T193_EC10414:
               pass
            else:
               raise

         if testSwitch.ENABLE_DESTROKE_BASE_ON_T193_CHROME and not testSwitch.virtualRun:
            try:
               objMsg.printMsg("ENABLE_DESTROKE_BASE_ON_T193_CHROME is enabled.")
               objMsg.printMsg("MABS_CRRO_LIMIT_LO = %.3f" % TP.DestrokeByT193ChromeSpec['MABS_CRRO_LIMIT_LO'])
               objMsg.printMsg("FIXED_DESTROKE_TRKS_LO = %d" % TP.DestrokeByT193ChromeSpec['DESTROKE_TRKS_FIXED_LO'])
               objMsg.printMsg("MABS_CRRO_LIMIT_UP = %.3f" % TP.DestrokeByT193ChromeSpec['MABS_CRRO_LIMIT_UP'])
               objMsg.printMsg("FIXED_DESTROKE_TRKS_UP = %d" % TP.DestrokeByT193ChromeSpec['DESTROKE_TRKS_FIXED_UP'])
               objMsg.printMsg("self.dut.IDExtraPaddingSize = %d" % self.dut.IDExtraPaddingSize)
            #p193CrroMeasTbl = self.dut.dblData.Tables('P193_CRRO_MEASUREMENT2').chopDbLog('SPC_ID', 'match',str(TP.chromeCalPrm_193["spc_id"]))
               p193CrroMeasTbl = self.dut.dblData.Tables('P193_CRRO_MEASUREMENT2').tableDataObj()
               for head in range(self.dut.imaxHead):
                  maxAbsCrro = 0.0
                  for entry in p193CrroMeasTbl:
                     if head == int(entry.get('HD_LGC_PSN')) and int(entry.get('ITER')) == 99:
                        maxAbsCrro = float(entry.get('MABS_CRRO'))   # assume the last one is the ID zone
                  objMsg.printMsg("Head:%d, last trk, MABS_CRRO=%.3f" % (head, maxAbsCrro))
                  if maxAbsCrro >= TP.DestrokeByT193ChromeSpec['MABS_CRRO_LIMIT_UP']:
                     self.dut.IDExtraPaddingSize = max(self.dut.IDExtraPaddingSize, TP.DestrokeByT193ChromeSpec['DESTROKE_TRKS_FIXED_UP'])
                     objMsg.printMsg("Trigger Destroke:DESTROKE_TRKS = %d" % self.dut.IDExtraPaddingSize)
                     try:
                        self.dut.objData.update({'IDExtraPaddingSize':self.dut.IDExtraPaddingSize})
                     except:
                        objMsg.printMsg("Fail to save IDExtraPaddingSize to objdata")
                  elif maxAbsCrro >= TP.DestrokeByT193ChromeSpec['MABS_CRRO_LIMIT_LO']:
                     extraPaddingSizeTemp =int(TP.DestrokeByT193ChromeSpec['DESTROKE_TRKS_FIXED_LO']+ \
                                            (TP.DestrokeByT193ChromeSpec['DESTROKE_TRKS_FIXED_UP'] - TP.DestrokeByT193ChromeSpec['DESTROKE_TRKS_FIXED_LO'])*(maxAbsCrro - TP.DestrokeByT193ChromeSpec['MABS_CRRO_LIMIT_LO'])/(TP.DestrokeByT193ChromeSpec['MABS_CRRO_LIMIT_UP'] - TP.DestrokeByT193ChromeSpec['MABS_CRRO_LIMIT_LO']))
                     self.dut.IDExtraPaddingSize = max(self.dut.IDExtraPaddingSize, extraPaddingSizeTemp)
                     objMsg.printMsg("Trigger Destroke:DESTROKE_TRKS = %d" % self.dut.IDExtraPaddingSize)
                     try:
                        self.dut.objData.update({'IDExtraPaddingSize':self.dut.IDExtraPaddingSize})
                     except:
                        objMsg.printMsg("Fail to save IDExtraPaddingSize to objdata")
            except:
               objMsg.printMsg("Failed to load table:P193_CRRO_MEASUREMENT2.")
               pass

         # Run MDW ZONE OFFSET BOUNDARY CAL
         if testSwitch.FE_0184102_326816_ZONED_SERVO_SUPPORT:
            prmT73 = self.oSrvOpti.oUtility.copy(TP.ZoneBoundaryCal_73)
            if testSwitch.extern.FE_0297957_356996_T73_USE_FLOATING_POINT_FREQ == 1:
               if testSwitch.CHEOPSAM_LITE_SOC:
                  prmT73['FREQ'] = 11980
               else:
                  prmT73['FREQ'] = 11875
            self.oSrvOpti.St(TP.spinupPrm_1)
            self.oSrvOpti.St(prmT73)

         if testSwitch.AGC_SCRN_DESTROKE and not testSwitch.AGC_SCRN_DESTROKE_WITH_NEW_RAP:
         # Reprogram Sync Marc Window for low stroke drives
            T185Data = self.dut.dblData.Tables('P185_TRK_0_V3BAR_CALHD').tableDataObj()
            PhysMaxCyl = 0
            for index in range(len(T185Data)):
               hd =int(T185Data[index]['HD_LGC_PSN'])
               if hd == 0 or PhysMaxCyl == 0:
                  PhysMaxCyl = int(T185Data[index]['PHYS_MAX_CYL'])
               else:
                  PhysMaxCyl = min(PhysMaxCyl,int(T185Data[index]['PHYS_MAX_CYL']))

            objMsg.printMsg("DBG: PhysMaxCyl %d" % PhysMaxCyl)
            if ( not testSwitch.KARNAK): #Karnak is LSI channel, address is different
               if PhysMaxCyl < 255000:
                  self.oSrvOpti.St(TP.RapWordSyncMarcWindow)
                  objMsg.printMsg("DBG: Sync Mark Window Updated")

   #--------------------------------------------------------------------------------------------------------
   def RampDetect(self, inPrm):
      CStop = {}
      for retry in range(3):
         try:
            self.oSrvOpti.St(inPrm)
            T185Data = self.dut.dblData.Tables('P185_TRK_0_V3BAR_CALHD').tableDataObj()
            #if self.dut.numHeads == 1: break
            maxhead = 0
            failHighRampCyl = set()
            if hasattr(TP, 'T185_T25_RDG_Screen_Spec'):
               rampOfstFail = TP.T185_T25_RDG_Screen_Spec.get('UFCO_OffsetFail', 0)
            ofstRampCyl = [0] * self.dut.imaxHead
            h1RampCyl = 0
            for index in range(len(T185Data)):
               hd = int(T185Data[index]['HD_LGC_PSN'])
               CStop[hd] = int(T185Data[index]['CRASH_STOP_CYL'])
               trkDcOfst = int(T185Data[index]['TRK_DC_OFST'])
               rampCyl = int(T185Data[index]['RAMP_CYL'])
               if rampCyl > TP.T185_RDG_Screen_Spec2:
                  objMsg.printMsg("H%d: Ramp cyl %d exceeded %d" % (hd, rampCyl, TP.T185_RDG_Screen_Spec2))
                  failHighRampCyl.add(hd)
               ofstRampCyl[hd] = rampCyl - trkDcOfst
               if hd == 1:
                  h1RampCyl = rampCyl
               if hd > maxhead: maxhead = hd

            if self.dut.imaxHead > 1:
               RampOfst = ofstRampCyl[0] - ofstRampCyl[1]
               objMsg.printMsg("==> Offset = %d\n" % (RampOfst))
               if testSwitch.FE_0365907_305538_P_T185_UFCO_OFFSET_SCREEN:
                  if rampOfstFail and abs(RampOfst) > rampOfstFail and failHighRampCyl:
                     if testSwitch.ENABLE_ON_THE_FLY_DOWNGRADE and self.downGradeOnFly(1, 14873):
                        objMsg.printMsg('Failed for ramp offset spec %d and ramp cyl spec %d, downgrade to %s as %s' % (rampOfstFail, TP.T185_RDG_Screen_Spec2, self.dut.BG, self.dut.partNum))
                     else:
                        ScrCmds.raiseException(14873, "Ramp offset %d exceeded %d and Ramp cyl exceeded %d @ Head : %s " % (RampOfst, rampOfstFail,TP.T185_RDG_Screen_Spec2, str(list(failHighRampCyl))))
            if maxhead ==  3 and testSwitch.FE_0360203_518226_2D_CTU_RDG_RDCLR_COMBO_SCREEN and self.dut.nextState == 'MDW_CAL' and failHighRampCyl:
                  if testSwitch.ENABLE_ON_THE_FLY_DOWNGRADE and self.downGradeOnFly(1, 48400):
                     objMsg.printMsg('Failed for ramp cyl spec, downgrade to %s as %s' % (self.dut.BG, self.dut.partNum))
                  else:
                     ScrCmds.raiseException(48400, "Ramp cyl exceeded %d @ Head : %s" % (TP.T185_RDG_Screen_Spec2, str(list(failHighRampCyl))))

            if maxhead == 0: break
            deltaCStop = 0
            for hd in range(maxhead + 1):
               if hd % 2 and abs(CStop[hd] - CStop[hd - 1]) > deltaCStop:
                  deltaCStop = abs(CStop[hd] - CStop[hd- 1])
            objMsg.printMsg("deltaCStop hd %d and %d : %d" % (hd,hd-1,deltaCStop))
            if deltaCStop < 5000:
               if retry > 0:
                  objMsg.printMsg("DBG: deltaCStop recovered %d" % retry)
               if self.dut.AABType in ['501.42'] and not testSwitch.IS_2D_DRV and h1RampCyl > 3000 and retry < 2 and self.dut.driveattr.get('PROC_CTRL19') != '1':
                  self.dut.driveattr['PROC_CTRL19'] = '1' # Do not retry if h1 ramp cyl > 3000 happened in 3rd running
                  inPrm['GB_BY_RAMP_CYL_P1'] = 9500
                  inPrm['GB_BY_RAMP_CYL_P2'] = 6500
               else:
                  break
            elif retry == 2:
               objMsg.printMsg("DBG: deltaCStop unrecovered %d" % retry)
            else:
               if self.dut.AABType in ['501.42'] and not testSwitch.IS_2D_DRV and h1RampCyl > 3000 and self.dut.driveattr.get('PROC_CTRL19') != '1':
                  self.dut.driveattr['PROC_CTRL19'] = '1'
                  inPrm['GB_BY_RAMP_CYL_P1'] = 9500
                  inPrm['GB_BY_RAMP_CYL_P2'] = 6500
         except:
            raise


#----------------------------------------------------------------------------------------------------------
class CPESScreens(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      audFreq = self.params.get("AUD_FREQ",0x1000)
      SPC_ID = int(self.params.get("SPC_ID", 1))

      from Servo import CServoFunc
      self.oSrvFunc = CServoFunc()

      if self.params.get('ZAP_OFF', 0):
         self.oSrvFunc.St(TP.zapPrm_175_zapOff)

      CFSO().getZoneTable()

      # Set to allow access to FAFH Zones at beginning of STATE
      if testSwitch.IS_FAFH: 
         self.oSrvFunc.St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value
         self.oSrvFunc.St(TP.AllowFAFH_AccessBit_178) # Allow FAFH access for servo test
         self.oSrvFunc.St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value

      if testSwitch.FE_0110581_346294_OCLIM_SCALE_PRE2_CPESSCREENS_T33:
         OCLIMAdj = 0
         try: PES_Scrn_Scaler = TP.PES_Scrn_OCLIM_Scaler #define in ## Servo ## section of TP, ie 1.5 = 150% of defaultOCLIM
         except: PES_Scrn_Scaler =1.0
         if (PES_Scrn_Scaler !=1.0) and (self.dut.nextOper == 'PRE2'):
            PESScrnOCLIM= int(TP.defaultOCLIM*PES_Scrn_Scaler)
            self.oSrvFunc.setOClim({},PESScrnOCLIM)
            OCLIMAdj = 1

      test_cyl = 0x0100
      end_cyl = min( self.dut.maxTrack) - 0x0100
      newPrm_33 = TP.pesMeasurePrm_33.copy()

      if testSwitch.M11P_BRING_UP or testSwitch.M11P:
         newPrm_33['spc_id'] = SPC_ID + 3
      else:
         newPrm_33['spc_id'] = SPC_ID

      if self.params.get("CYL_IS_LOGICAL", 0):
         cword1 = newPrm_33.get('CWORD1',0)
         if type(cword1) is not 'int': cword1 = cword1[0]
         newPrm_33.update({'CWORD1':  cword1 | 0x8000}) # CYL_IS_LOGICAL == TRUE.
      if self.dut.BG in ['SBS'] and self.params.get('disableUnsafeRetry', 0):
         cword1 = newPrm_33.get('CWORD1',0)
         if type(cword1) is not int: cword1 = cword1[0]
         newPrm_33.update({'CWORD1':  cword1 & 0xFFFD}) # Disable CWORD1 bit 1 to disable the unsafe retry
      newPrm_33.update({
                        'TEST_CYL': self.oSrvFunc.oUtility.ReturnTestCylWord(test_cyl),
                        'END_CYL' : self.oSrvFunc.oUtility.ReturnTestCylWord(end_cyl),
                        'NUM_SAMPLES' : ((end_cyl - test_cyl) / audFreq),
      })

      '''
      if self.dut.nextState == 'PES_SCRN2':
         for head in range(self.dut.imaxHead):
            iTrack = self.dut.maxTrack[head]- 1
            TP.pesMeasurePrm_83_agc01.update({'TEST_HEAD': head})
            TP.pesMeasurePrm_83_agc01.update({'END_CYL':  self.oSrvFunc.oUtility.ReturnTestCylWord(iTrack)})
            TP.pesMeasurePrm_83_agc01.update({'TEST_CYL': self.oSrvFunc.oUtility.ReturnTestCylWord(iTrack-101)})
            SetFailSafe()
            self.oSrvFunc.St(TP.pesMeasurePrm_83_agc01)
            ClearFailSafe()
      '''
      if testSwitch.FE_0139688_395340_P_T56_T33_TO_CAPTURE_EC14787_HIGH_NRRO:
         self.oSrvFunc.St(TP.prm_056_uAct_Dual_Stage)
      try:
         self.oSrvFunc.St( newPrm_33 )
      except:
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1) #power cycle #cl

      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1) #power cycle #cl
      if self.dut.nextOper == 'FNC2' and self.dut.BG in ['SBS']:
         if testSwitch.FE_305538_P_T33_REZAP_ON_MAXRRO_EXCEED_LIMIT:
            from dbLogUtilities import DBLogCheck
            dblchk = DBLogCheck(self.dut)
            if (dblchk.checkComboScreen(TP.T33_ReZap_Trigger_Limit, {'spc_id': SPC_ID}) == FAIL):
               try:
                  data = self.dut.dblData.Tables('P033_PES_HD2').tableDataObj()
                  self.dut.dblData.Tables('P033_PES_HD2').deleteIndexRecords(confirmDelete=1)
                  self.dut.dblData.delTable('P033_PES_HD2')
               except:         
                  objMsg.printMsg('Cannot delete P033_PES_HD2 table')
               
               chkFlag = 1
               if ConfigVars[CN].get('ChkStateDepend', 1):
                  if self.dut.statesExec[self.dut.nextOper].count('ZAP') + self.dut.statesExec[self.dut.nextOper].count('RZAP') + self.dut.statesExec[self.dut.nextOper].count('SPF_REZAP') >= 3:
                     chkFlag = 0 # Already run ZAP >= 2 times
               else:
                  if self.dut.statesExec[self.dut.nextOper].count('ZAP') + self.dut.statesExec[self.dut.nextOper].count('RZAP') + self.dut.statesExec[self.dut.nextOper].count('SPF_REZAP') >= 2:
                     chkFlag = 0 # Already run ZAP >= 2 times
               if chkFlag:
                  try:
                     self.dut.objData.retrieve('OFWPESCheck')
                     objMsg.printMsg('Bypass PES checking since already reZAPPed')
                  except:
                     self.dut.objData.update({'OFWPESCheck':1})
                     ScrCmds.raiseException(10414, 'Max RRO exceeded limit @ Head : %s' % str(dblchk.failHead))
      if (self.dut.partNum == '2G3172-900' or self.dut.partNum == '2G2174-900') and self.dut.nextOper == 'FNC2':
         from dbLogUtilities import DBLogCheck
         dblchk = DBLogCheck(self.dut)
         if (dblchk.checkComboScreen(TP.T33_RRO_Check, {'spc_id': SPC_ID}) == FAIL) or (dblchk.checkComboScreen(TP.T33_NRRO_Check, {'spc_id': SPC_ID}) == FAIL):
               if testSwitch.ENABLE_ON_THE_FLY_DOWNGRADE and self.downGradeOnFly(1, 10414):
                  objMsg.printMsg('Max RRO exceeded limit, downgrade to %s as %s' % (self.dut.BG, self.dut.partNum))
               else:
                  ScrCmds.raiseException(10414, 'Max RRO/NRRO exceeded limit @ Head : %s' % str(dblchk.failHead))

      if self.dut.nextOper == 'FNC2':
         newPrm_33_RdPos = newPrm_33.copy()
         newPrm_33_RdPos['prm_name'] = 'pesRdPosMeasPrm_33'
         newPrm_33_RdPos['SEEK_TYPE'] = 0x0015
         newPrm_33_RdPos['spc_id'] = SPC_ID + 1
         self.oSrvFunc.St( newPrm_33_RdPos )

      if testSwitch.FE_0234376_229876_T109_READ_ZFS:
         newPrm_33_RdPos = newPrm_33.copy()
         newPrm_33_RdPos['prm_name'] = 'pesRdPosMeasPrm_33'
         newPrm_33_RdPos['SEEK_TYPE'] = 0x0015
         self.oSrvFunc.St( newPrm_33_RdPos )

      if testSwitch.FE_0125503_357552_T33_RVFF_OFF_AND_ON:
         #Use further down, but copy here, so doesn't get changed accidentally
         prm_33_tenSample = newPrm_33.copy()

      if testSwitch.FE_0110581_346294_OCLIM_SCALE_PRE2_CPESSCREENS_T33:
         if OCLIMAdj :
            self.oSrvFunc.setOClim({},TP.defaultOCLIM)

      if testSwitch.FE_0125503_357552_T33_RVFF_OFF_AND_ON:
         prm_33_tenSample.update({'NUM_SAMPLES' : 10,'prm_name':'prm_33_tenSample'})

         #Retrieve initial RVFF setting
         self.oSrvFunc.St(TP.prm_0011_read_RVFF)
         if not testSwitch.virtualRun:
            orig_RVFF_Val = int(self.dut.objSeq.SuprsDblObject['P011_SV_RAM_RD_BY_OFFSET'][-1]['READ_DATA'],16) & 1  #lsb only
         else:
            orig_RVFF_Val = 1

         #Test with RVFF OFF
         self.oSrvFunc.St(TP.prm_0011_enable_RVFF_current,{'WR_DATA':0})
         if testSwitch.FE_0139688_395340_P_T56_T33_TO_CAPTURE_EC14787_HIGH_NRRO:
            self.oSrvFunc.St(TP.prm_056_uAct_Dual_Stage)
         self.oSrvFunc.St(prm_33_tenSample, {'spc_id':100})

         #Test with RVFF ON
         self.oSrvFunc.St(TP.prm_0011_enable_RVFF_current,{'WR_DATA':1})
         if testSwitch.FE_0139688_395340_P_T56_T33_TO_CAPTURE_EC14787_HIGH_NRRO:
            self.oSrvFunc.St(TP.prm_056_uAct_Dual_Stage)
         self.oSrvFunc.St(prm_33_tenSample, {'spc_id':200})

         #Restore original RVFF setting
         self.oSrvFunc.St(TP.prm_0011_enable_RVFF_current,{'WR_DATA':orig_RVFF_Val})

      # Set to dis-allow access to FAFH Zones at beginning of STATE
      if testSwitch.IS_FAFH: 
         self.oSrvFunc.St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value
         self.oSrvFunc.St(TP.DisallowFAFH_AccessBit_178) # Dis-allow FAFH access after completing servo test
         self.oSrvFunc.St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value


#----------------------------------------------------------------------------------------------------------
class CServoTune(CState):
   """
      Description: Class that will perform a 1 stop Servo Calibration
      Base: Standard MDW cals, with the option to run T43 radial cals for MD drives
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = ['MDW_CAL']
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from Servo import CServoOpti
      self.oSrvOpti = CServoOpti()

      #Servo MDW Tuning
      if  self.dut.nextState != 'STS_CHROME_SCRN' : #only run in normal CERT, exclude from STS oper.
          self.oSrvOpti.setOClim({},TP.defaultOCLIM,updateFlash = 1)
          if testSwitch.FE_0122163_357915_DUAL_STAGE_ACTUATOR_SUPPORT and testSwitch.FE_0122180_357915_T150_DISABLE_UACT:
             self.oSrvOpti.St(TP.enableHiBWController_Single)
          if testSwitch.M11P_BRING_UP or testSwitch.M11P:
             self.oSrvOpti.servoLinCal(TP.servoLinCalPrm_150,TP.CRRO_IRRO_Prm_46, runReal = 1)      
             self.oSrvOpti.St(TP.prm_RepeatableTMR_257)	#Measurement in virtual mode.
          
          # Run T257 with different Harmonic setting
          if testSwitch.ROSEWOOD7 and testSwitch.extern.SFT_TEST_0257:
             self.oSrvOpti.servoLinCal(TP.servoLinCalPrm_150, TP.Incoherent_WIRRO_Meas_H10_257, runReal=1,
                                       sampling=not testSwitch.SCOPY_TARGET)
          
          if testSwitch.FE_0176665_475827_RUN_T246_IN_MDW_CAL:
             self.oSrvOpti.servoLinCal(TP.servoLinCalPrm_150,TP.CRRO_Prm_246, runReal = 1)
          if testSwitch.FE_0122163_357915_DUAL_STAGE_ACTUATOR_SUPPORT and testSwitch.FE_0122180_357915_T150_DISABLE_UACT:
             self.oSrvOpti.St(TP.enableHiBWController_Dual)

          if testSwitch.FE_SGP_COLLECT_SVOAGC_AT_ID:
             # Start AGC Screen before T193 for data collection only
             agc_prm = TP.pesMeasurePrm_83_agc01.copy()
             for head in range(self.dut.imaxHead):
                 iTrack = self.dut.maxTrack[head]- 1
                 agc_prm['TEST_HEAD'] = head
                 agc_prm['END_CYL'] = self.oSrvOpti.oUtility.ReturnTestCylWord(iTrack)
                 agc_prm['TEST_CYL'] = self.oSrvOpti.oUtility.ReturnTestCylWord(iTrack-101)
                 agc_prm['AGC_MINMAX_DELTA'] = 1000  #large value to open spec
                 agc_prm['spc_id'] = 100
                 try:
                     self.oSrvOpti.St(agc_prm)
                 except:
                     pass
             # End of AGC Screen
          NextChromeCal = TP.chromeCalPrm_193.copy()
          if NextChromeCal.has_key('gainRty'):
             NextChromeCal.pop('gainRty')
      else: #for STS only
          NextChromeCal = TP.chromeCalPrm_193.copy()
          if NextChromeCal.has_key('gainRty'):
             NextChromeCal.pop('gainRty')
      if testSwitch.WA_0126987_426568_RUN_TEST_193_TWICE_WITH_NEW_GAIN_VALUE :
         try:
            objMsg.printMsg("Trying First test 193")
            self.oSrvOpti.chromeCal(NextChromeCal)
         except ScriptTestFailure, (failuredata):
            if failuredata[0][2] in [14598,10502]:
               objMsg.printMsg("14598 or 10502 found in test 193: Rerunning with higher gain")
               if TP.chromeCalPrm_193.has_key('gainRty'):
                  NextChromeCal['GAIN'] = TP.chromeCalPrm_193['gainRty']
                  self.oSrvOpti.chromeCal(NextChromeCal)
               else:
                  objMsg.printMsg('gainRty not found')
                  raise
            else:
               objMsg.printMsg('Failure not a 14598 or 10502')
               raise
      else:
         try: self.oSrvOpti.chromeCal(NextChromeCal)
         except ScriptTestFailure, (failureData):
            ec = failureData[0][2]
            if ec in [10414]: pass
            else: objPwrCtrl.powerCycle(5000,12000,10,10, useESlip=1)

      if testSwitch.M11P_BRING_UP or testSwitch.M11P:
         self.oSrvOpti.St(TP.Enable_High_BW_Controller_3)
         self.oSrvOpti.St(TP.Enable_High_BW_Controller_4)
         CFSO().saveSAPtoFLASH()

      if testSwitch.ENABLE_DESTROKE_BASE_ON_T193_CHROME:
         try:
            objMsg.printMsg("ENABLE_DESTROKE_BASE_ON_T193_CHROME is enabled.")
            objMsg.printMsg("MABS_CRRO_LIMIT_LO = %.3f" % TP.DestrokeByT193ChromeSpec['MABS_CRRO_LIMIT_LO'])
            objMsg.printMsg("FIXED_DESTROKE_TRKS_LO = %d" % TP.DestrokeByT193ChromeSpec['DESTROKE_TRKS_FIXED_LO'])
            objMsg.printMsg("MABS_CRRO_LIMIT_UP = %.3f" % TP.DestrokeByT193ChromeSpec['MABS_CRRO_LIMIT_UP'])
            objMsg.printMsg("FIXED_DESTROKE_TRKS_UP = %d" % TP.DestrokeByT193ChromeSpec['DESTROKE_TRKS_FIXED_UP'])
            objMsg.printMsg("self.dut.IDExtraPaddingSize = %d" % self.dut.IDExtraPaddingSize)
            #p193CrroMeasTbl = self.dut.dblData.Tables('P193_CRRO_MEASUREMENT2').chopDbLog('SPC_ID', 'match',str(TP.chromeCalPrm_193["spc_id"]))
            p193CrroMeasTbl = self.dut.dblData.Tables('P193_CRRO_MEASUREMENT2').tableDataObj()
            for head in range(self.dut.imaxHead):
               maxAbsCrro = 0.0
               for entry in p193CrroMeasTbl:
                  if head == int(entry.get('HD_LGC_PSN')) and int(entry.get('ITER')) == 99:
                     maxAbsCrro = float(entry.get('MABS_CRRO'))   # assume the last one is the ID zone
               objMsg.printMsg("Head:%d, last trk, MABS_CRRO=%.3f" % (head, maxAbsCrro))
               if maxAbsCrro >= TP.DestrokeByT193ChromeSpec['MABS_CRRO_LIMIT_UP']:
                  self.dut.IDExtraPaddingSize = max(self.dut.IDExtraPaddingSize, TP.DestrokeByT193ChromeSpec['DESTROKE_TRKS_FIXED_UP'])
                  objMsg.printMsg("Trigger Destroke:DESTROKE_TRKS = %d" % self.dut.IDExtraPaddingSize)
                  try:
                     self.dut.objData.update({'IDExtraPaddingSize':self.dut.IDExtraPaddingSize})
                  except:
                     objMsg.printMsg("Fail to save IDExtraPaddingSize to objdata")
               elif maxAbsCrro >= TP.DestrokeByT193ChromeSpec['MABS_CRRO_LIMIT_LO']:
                  extraPaddingSizeTemp =int(TP.DestrokeByT193ChromeSpec['DESTROKE_TRKS_FIXED_LO']+ \
                                            (TP.DestrokeByT193ChromeSpec['DESTROKE_TRKS_FIXED_UP'] - TP.DestrokeByT193ChromeSpec['DESTROKE_TRKS_FIXED_LO'])*(maxAbsCrro - TP.DestrokeByT193ChromeSpec['MABS_CRRO_LIMIT_LO'])/(TP.DestrokeByT193ChromeSpec['MABS_CRRO_LIMIT_UP'] - TP.DestrokeByT193ChromeSpec['MABS_CRRO_LIMIT_LO']))
                  self.dut.IDExtraPaddingSize = max(self.dut.IDExtraPaddingSize, extraPaddingSizeTemp)
                  objMsg.printMsg("Trigger Destroke:DESTROKE_TRKS = %d" % self.dut.IDExtraPaddingSize)
                  try:
                     self.dut.objData.update({'IDExtraPaddingSize':self.dut.IDExtraPaddingSize})
                  except:
                     objMsg.printMsg("Fail to save IDExtraPaddingSize to objdata")
         except:
            objMsg.printMsg("Failed to load table:P193_CRRO_MEASUREMENT2.")
            pass

      # Run MDW ZONE OFFSET BOUNDARY CAL
      if testSwitch.FE_0184102_326816_ZONED_SERVO_SUPPORT:
         prmT73 = self.oSrvOpti.oUtility.copy(TP.ZoneBoundaryCal_73)
         if testSwitch.extern.FE_0297957_356996_T73_USE_FLOATING_POINT_FREQ == 1:
            if testSwitch.CHEOPSAM_LITE_SOC:
               prmT73['FREQ'] = 11980
            else:
               prmT73['FREQ'] = 11875
         self.oSrvOpti.St(TP.spinupPrm_1)
         self.oSrvOpti.St(prmT73)
         if testSwitch.M11P_BRING_UP or testSwitch.M11P:
            CFSO().saveSAPtoFLASH()

      if not (testSwitch.M11P_BRING_UP or testSwitch.M11P):
         self.oSrvOpti.St(TP.enableViterbi_11['read'])
         VTBit = int(self.dut.dblData.Tables('P011_SV_RAM_RD_BY_OFFSET').tableDataObj()[-1]['READ_DATA'],16)
         objMsg.printMsg("VTBit = %d" % (VTBit))
         
         if VTBit == 0xFFFF:
            objMsg.printMsg("Servo does not support Viterbi feature")
         else:
            self.oSrvOpti.St(TP.prm_263_ViterbiTarget)
      
      # Check for a controller response file in the servo release package.
      # The presence of this file will be used (along with FE_0148755) to determine if T152 or T282 will be used for SNO
      from PackageResolution import PackageDispatcher
      controller_filename = PackageDispatcher(self.dut, 'CTLR_BIN').getFileName()
      if testSwitch.FE_0122163_357915_DUAL_STAGE_ACTUATOR_SUPPORT:
         self.oSrvOpti.St(TP.enableHiBWController_Single)
         if (controller_filename != None) and testSwitch.extern.FE_0148755_010200_SFT_TEST_0282:
            # Initialize the local doSNO parameter to cause a T288 failure if there is no valid override from Servo
            # We want to
            local_doBodeSNO_282 = {'test_num':282, 'timeout':100, 'CWORD1':0x00F8}
            if getattr(TP, 'doBodeSNO_282', 0):
               local_doBodeSNO_282 = TP.doBodeSNO_282.copy()
               local_doBodeSNO_282['dlfile'] = (CN, controller_filename)
            self.oSrvOpti.doSNO(local_doBodeSNO_282, TP.snoNotches_282_VCM)
            self.oSrvOpti.doSNO(local_doBodeSNO_282, TP.snoNotches_282_DAC)
         else:
            self.oSrvOpti.doSNO(TP.doBodeSNO_152, TP.snoNotches_152_VCM)
            self.oSrvOpti.doSNO(TP.doBodeSNO_152, TP.snoNotches_152_DAC)
         if (testSwitch.FE_0113230_345334_REENABLE_DUAL_STAGE_AFTER_SNO_NOTCHES) :
            self.oSrvOpti.St(TP.enableHiBWController_Dual)
         if (testSwitch.FE_0113902_345334_SAVE_SAP_WHEN_CHANGING_DUAL_STAGE) :
            self.oFSO = CFSO()
            self.oFSO.saveSAPtoFLASH()
      else:
         if testSwitch.WO_MULTIRATESNO_TT122:
            if (controller_filename != None) and testSwitch.extern.FE_0148755_010200_SFT_TEST_0282:
               local_doBodeSNO_282 = {'test_num':282, 'timeout':100, 'CWORD1':0x00F8}
               if getattr(TP, 'doBodeSNO_282', 0):
                  local_doBodeSNO_282 = TP.doBodeSNO_282.copy()
                  local_doBodeSNO_282['dlfile'] = (CN, controller_filename)
               self.oSrvOpti.doSNO(local_doBodeSNO_282, TP.snoNotches_282)
            else:
               self.oSrvOpti.doSNO(TP.doBodeSNO_152, TP.snoNotches_152)
            if testSwitch.FE_0149477_007955_P_SAVE_SAP_ON_NON_DUAL_STAGE_ACT:
               self.oFSO = CFSO()
               self.oFSO.saveSAPtoFLASH()

      if testSwitch.plantBodeMeasurement:
         self.oSrvOpti.St(TP.doBodePrm_152) #Structural Bode 500-24kHz

      if testSwitch.SNODataCollection:
         prm1 = TP.tempSNO_152
         self.oSrvOpti.St(prm1) # Plot Type 0
         prm1.update({'START_CYL':(3L, 46940,)})
         prm1.update({'END_CYL':(3L, 46940,)})
         self.oSrvOpti.St(prm1)
         prm1.update({'START_CYL':(0L, 12179,)})
         prm1.update({'END_CYL':(0L, 12179,)})
         prm1.update({'PLOT_TYPE':(1)})
         self.oSrvOpti.St(prm1) # Plot Type 1
         prm1.update({'START_CYL':(3L, 46940,)})
         prm1.update({'END_CYL':(3L, 46940,)})
         self.oSrvOpti.St(prm1)

      if testSwitch.AGC_SCRN_DESTROKE and not testSwitch.AGC_SCRN_DESTROKE_WITH_NEW_RAP:
      # Reprogram Sync Marc Window for low stroke drives
         T185Data = self.dut.dblData.Tables('P185_TRK_0_V3BAR_CALHD').tableDataObj()
         PhysMaxCyl = 0
         for index in range(len(T185Data)):
            hd =int(T185Data[index]['HD_LGC_PSN'])
            if hd == 0 or PhysMaxCyl == 0:
               PhysMaxCyl = int(T185Data[index]['PHYS_MAX_CYL'])
            else:
               PhysMaxCyl = min(PhysMaxCyl,int(T185Data[index]['PHYS_MAX_CYL']))
         objMsg.printMsg("DBG: PhysMaxCyl %d" % PhysMaxCyl)
         if ( not testSwitch.KARNAK): #Karnak is LSI channel, address is different
            if PhysMaxCyl < 255000:
               self.oSrvOpti.St(TP.RapWordSyncMarcWindow)
               objMsg.printMsg("DBG: Sync Mark Window Updated")

      if testSwitch.M11P_BRING_UP or testSwitch.M11P:
         newPrm_33 = TP.pesMeasurePrm_33_M11P.copy()
         newPrm_33['spc_id'] = 3
         self.oSrvOpti.St(newPrm_33)
#----------------------------------------------------------------------------------------------------------
class CServoOptiCal(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      """
      Sub Algorithms
      ==============
         FLEX-FCC from Shirish Bahirat
         ========
            1. Flex Bias Calibration
            2. FCC Cal
            3. Flex Bias Calibration
            4. Optional sensitivity margin scoring
      """
      from Servo import CServo
      from PackageResolution import PackageDispatcher
      self.oServo = CServo()
      
      objMsg.printMsg("Using class frm base.")
      self.oServo.setQuietSeek(TP.quietSeekPrm_11, setQSeekOn = 0) #disable quiet seek

      if testSwitch.pztCalTestEnabled:
            self.oServo.St(TP.pztCal_332)
      if self.dut.nextState == 'SERVO_OPTI':
         # Fetch max track of each hd
         CFSO().getZoneTable()
         self.maxTrack = CFSO().dut.maxTrack   # a list is return
         objMsg.printMsg("Max Cyl for Hd 0 is %d, assumed to be same for all hds" % self.maxTrack[0])
         OD_TestTrk = int(0.05*self.maxTrack[0]) # 5% of stroke
         MD_TestTrk = int(0.5*self.maxTrack[0])  # 50% of stroke
         ID_TestTrk = int(0.95*self.maxTrack[0]) # 95% of stroke
         #objMsg.printMsg('VCM structural, Dual Stage S function and uAct Structural BODE plot begin')
         
         if testSwitch.FE_SGP_REPLACE_T152_WITH_T282:
            SODprm_282 = TP.doBodePrm_282_VCM_structural_OD
            SODprm_282['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(OD_TestTrk)
            SODprm_282['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(OD_TestTrk)
            self.oServo.St(SODprm_282) #single stage vcm structural Bode 500-24kHz
            # disable for test time review
            #SMDprm_282 = TP.doBodePrm_282_VCM_structural_MD
            #self.oServo.St(SMDprm_282) #single stage vcm structuralBode 500-24kHz
            if not (testSwitch.M11P_BRING_UP or testSwitch.M11P):
               SIDprm_282 = TP.doBodePrm_282_VCM_structural_ID
               SIDprm_282['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(ID_TestTrk)
               SIDprm_282['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(ID_TestTrk)
               self.oServo.St(SIDprm_282) #single stage vcm structuralBode 500-24kHz
            objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

            SODprm_282 = TP.doBodePrm_282_XVFF_structural_OD
            SODprm_282['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(OD_TestTrk)
            SODprm_282['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(OD_TestTrk)
            self.oServo.St(SODprm_282) #single stage xVFF structural Bode 500-24kHz
            # disable for test time review
            #SMDprm_282 = TP.doBodePrm_282_XVFF_structural_MD
            #self.oServo.St(SMDprm_282) #single stage vcm structuralBode 500-24kHz
            if not (testSwitch.M11P_BRING_UP or testSwitch.M11P):
               SIDprm_282 = TP.doBodePrm_282_XVFF_structural_ID
               SIDprm_282['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(ID_TestTrk)
               SIDprm_282['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(ID_TestTrk)
               self.oServo.St(SIDprm_282) #single stage xVFF structuralBode 500-24kHz
            objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

            if not testSwitch.ROSEWOOD7: # remove for test time reduction
                SODprm_282 = TP.doBodePrm_282_S_OD
                SODprm_282['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(OD_TestTrk)
                SODprm_282['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(OD_TestTrk)
                SODprm_282['spc_id'] = 4
                if testSwitch.M11P_BRING_UP or testSwitch.M11P:
                   sens_limit_filename = PackageDispatcher(self.dut, 'SVO_BIN').getFileName()
                   SODprm_282['dlfile'] = (CN,sens_limit_filename)
                self.oServo.St(SODprm_282) #dual stage S function Bode 500-24kHz
                # disable for test time review
                #SMDprm_282 = TP.doBodePrm_282_S_MD
                #self.oServo.St(SMDprm_282) #dual stage S function Bode 500-24kHz
            
                if testSwitch.FE_0264856_480505_USE_OL_GAIN_INSTEAD_OF_S_GAIN_IN_282:
                   objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
                   if not (testSwitch.M11P_BRING_UP or testSwitch.M11P):
                      OL_ODprm_282 = TP.doBodePrm_282_OL_OD		# No doBodePrm_282_OL_OD.
                   OL_ODprm_282 = TP.doBodePrm_282_S_OD.copy()
                   OL_ODprm_282.update({ 'prm_name'  : 'doBodePrm_282_OL at OD' })               
                   OL_ODprm_282.update({ 'CWORD1'  : 0x0080 })               

                   OL_ODprm_282['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(OD_TestTrk)
                   OL_ODprm_282['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(OD_TestTrk)
                   self.oServo.St(OL_ODprm_282)
                   if not (testSwitch.M11P_BRING_UP or testSwitch.M11P):
                      OL_IDprm_282 = TP.doBodePrm_282_OL_ID
                      OL_IDprm_282['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(ID_TestTrk)
                      OL_IDprm_282['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(ID_TestTrk)
                      self.oServo.St(OL_IDprm_282)           
                else:   
                   SIDprm_282 = TP.doBodePrm_282_S_ID
                   SIDprm_282['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(ID_TestTrk)
                   SIDprm_282['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(ID_TestTrk)
                   SIDprm_282['spc_id'] = 6
                   self.oServo.St(SIDprm_282) #dual stage S function Bode 500-24kHz
                objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

            SODprm_282 = TP.doBodePrm_282_uAct_structural_OD
            SODprm_282['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(OD_TestTrk)
            SODprm_282['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(OD_TestTrk)
            self.oServo.St(SODprm_282) #dual stage uAct structural Bode 500-24kHz
            if not (testSwitch.ROSEWOOD7 or testSwitch.M11P_BRING_UP or testSwitch.M11P) and not testSwitch.WA_0256539_480505_SKDC_M10P_BRING_UP_DEBUG_OPTION:
               SMDprm_282 = TP.doBodePrm_282_uAct_structural_MD
               SMDprm_282['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(MD_TestTrk)
               SMDprm_282['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(MD_TestTrk)
               self.oServo.St(SMDprm_282) #dual stage uAct structuralBode 500-24kHz
            if not (testSwitch.M11P_BRING_UP or testSwitch.M11P):
               SIDprm_282 = TP.doBodePrm_282_uAct_structural_ID
               SIDprm_282['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(ID_TestTrk)
               SIDprm_282['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(ID_TestTrk)
               self.oServo.St(SIDprm_282) #dual stage uAct structuralBode 500-24kHz
            objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
            
            ### Sensitivity Scoring Plot ###
            sens_limit_filename = PackageDispatcher(self.dut, 'SVO_BIN').getFileName()
            if sens_limit_filename != None and testSwitch.FE_0322256_356996_T282_SENSITIVITY_LIMIT_CHECK:
               #if testSwitch.IS_2D_DRV == 0:
               objMsg.printMsg("\n Sensitivity Limit File = %s" %(sens_limit_filename))
               SODprm_282 = TP.doBodePrm_282_S_Score_OD
               SODprm_282['dlfile'] = (CN,sens_limit_filename)
               SODprm_282['START_CYL'] = CUtility().ReturnTestCylWord(OD_TestTrk)
               SODprm_282['END_CYL'] = CUtility().ReturnTestCylWord(OD_TestTrk)
               try:
                  self.oServo.St(SODprm_282)
               except:
                  objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
               if testSwitch.IS_2D_DRV == 0:
                  CFSO().saveSAPtoFLASH()
               #For ID cyl
               SIDprm_282 = TP.doBodePrm_282_S_Score_ID
               SIDprm_282['dlfile'] = (CN,sens_limit_filename)
               SIDprm_282['START_CYL'] = CUtility().ReturnTestCylWord(ID_TestTrk)
               SIDprm_282['END_CYL'] = CUtility().ReturnTestCylWord(ID_TestTrk)
               try:
                  self.oServo.St(SIDprm_282)
               except:
                  objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
               #elif testSwitch.IS_2D_DRV == 1:
                  #objMsg.printMsg('Drive is RW2D. Skip 282 Sensitivity Limit Check For Now')
               if testSwitch.IS_2D_DRV == 0:
                  CFSO().saveSAPtoFLASH()
               objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
            ### Sensitivity Scoring Plot (End) ###
            else:
               objMsg.printMsg("No Sensitivity Limit file.(SVO_BIN)")
         
         else:
            ODprm_152 = TP.doBodePrm_152_OD
            ODprm_152['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(OD_TestTrk)
            ODprm_152['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(OD_TestTrk)
            self.oServo.St(ODprm_152) #Structural Bode 500-24kHz
            MDprm_152 = TP.doBodePrm_152_MD
            MDprm_152['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(MD_TestTrk)
            MDprm_152['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(MD_TestTrk)
            self.oServo.St(MDprm_152) #Structural Bode 500-24kHz
            IDprm_152 = TP.doBodePrm_152_ID
            IDprm_152['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(ID_TestTrk)
            IDprm_152['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(ID_TestTrk)
            self.oServo.St(IDprm_152) #Structural Bode 500-24kHz
            SODprm_152 = TP.doBodePrm_152_S_OD
            SODprm_152['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(OD_TestTrk)
            SODprm_152['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(OD_TestTrk)
            self.oServo.St(SODprm_152) #S function Bode 500-24kHz
            self.BodeScreenRange(OD_TestTrk, TP.gainFreqFilter_152, TP.doBodePrm_152_S_OD['spc_id'])
            SMDprm_152 = TP.doBodePrm_152_S_MD
            SMDprm_152['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(MD_TestTrk)
            SMDprm_152['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(MD_TestTrk)
            self.oServo.St(SMDprm_152) #S function Bode 500-24kHz
            self.BodeScreenRange(MD_TestTrk, TP.gainFreqFilter_152, TP.doBodePrm_152_S_MD['spc_id'])
            SIDprm_152 = TP.doBodePrm_152_S_ID
            SIDprm_152['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(ID_TestTrk)
            SIDprm_152['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(ID_TestTrk)
            self.oServo.St(SIDprm_152) #S function Bode 500-24kHz
            self.BodeScreenRange(ID_TestTrk, TP.gainFreqFilter_152, TP.doBodePrm_152_S_ID['spc_id'])

            #objMsg.printMsg("P152 table:--> %s" %str(self.dut.dblData.Tables('P152_BODE_GAIN_PHASE')) )
            #Delete file pointers
            try:
                self.dut.dblData.Tables('P152_BODE_GAIN_PHASE').deleteIndexRecords(1)
                #Delete RAM objects
                self.dut.dblData.delTable('P152_BODE_GAIN_PHASE')
            except:pass

      #### Below subsequence suggested by Shirish Bahirat
      if testSwitch.shortProcess:
         abbreviatedBiasCalParam = TP.flexBiasCalibration_136
         abbreviatedBiasCalParam.update({"SEEK_NUMS" : (2000)})
         self.oServo.St(abbreviatedBiasCalParam)
         self.oServo.St(TP.fccCalPrm_10) #Force constant calibration
         self.oServo.St(abbreviatedBiasCalParam)
      else:
         if self.dut.nextState == 'SERVO_OPTI':
            try:
               #### Below subsequence suggested by Shirish Bahirat
               #self.oServo.St(TP.flexBiasCalibration_136, {'BIAS_SPIKE_LIMIT': 5000})
               self.oServo.St(TP.flexBiasCalibration_136)
            except ScriptTestFailure, (failureData):  # allow retry for EC10136 in SERVO_OPTI with ~30mins full stroke 2-pt seek
               if not testSwitch.ROSEWOOD7 or failureData[0][2] not in [10136]:   # only for RW7, only catch EC10136
                  raise
               #=== Full stroke 2-pt seek ===
               objMsg.printMsg('Failed 10136 - Retry with 2-Pt Full Stroke Seek...')
               self.oServo.St(TP.full_stroke_two_point_sweep, {'PASSES': (25000,)})
               objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=1, onTime=5, useESlip=1)
               try:
                  self.oServo.St(TP.flexBiasCalibration_136, {'spc_id': 101})
               except:
                  objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=1, onTime=5, useESlip=1)
            try:
               self.oServo.St(TP.flexBiasCalibration_136_1)
            except:
               objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=1, onTime=5, useESlip=1)
            if testSwitch.M11P_BRING_UP or testSwitch.M11P:
               SetFailSafe() # Set fail safe for M11 & M11_BRING_UP. Need to add fail safe becos test 10 broken
               self.oServo.St(TP.fccCalPrm_10) #Force constant calibration
               ClearFailSafe()
            else:
               try:
                  self.oServo.St(TP.fccCalPrm_10) #Force constant calibration
               except:
                  objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=1, onTime=5, useESlip=1)
         self.oServo.St(TP.flexBiasCalibration_136_2)

      if 0:    #Will remove this portion of code in future for Rosewood product
         if testSwitch.FE_0142952_010200_SFW_PKG_BIN_SENSITIVITY_SCORING_LIMITS:
            # Check for a sensitivity margin limit file in the servo release package.
            from PackageResolution import PackageDispatcher
            limit_filename = PackageDispatcher(self.dut, 'SVO_BIN').getFileName()
            if (limit_filename != None) and testSwitch.extern.FE_0134761_010200_BINARY_DL_SENSITIVITY_SCORING:
               # If a limit file was included in the servo package, run the sensitivity margin scoring screen
               objMsg.printMsg("Perform sensitivity scoring using limit file '%s'." %str(limit_filename))
               if testSwitch.extern.FE_0148755_010200_SFT_TEST_0282:
                  if testSwitch.FE_0122163_357915_DUAL_STAGE_ACTUATOR_SUPPORT:
                     if getattr(TP, 'prm_DS_SensitivityScoring_282', 0):
                        local_prm_SensitivityScoring_282 = TP.prm_DS_SensitivityScoring_282.copy()
                        local_prm_SensitivityScoring_282['dlfile'] = (CN, limit_filename)
                        self.oServo.St(local_prm_SensitivityScoring_282)
                     if testSwitch.FE_0166236_010200_ADD_VCM_SENSITIVITY_ON_DS_PRODUCTS and getattr(TP, 'prm_VCM_SensitivityScoring_282', 0):
                        # For now, we'll use the same limit file.  This will probably need to be a new limit file at some point in the future...
                        local_prm_SensitivityScoring_282 = TP.prm_VCM_SensitivityScoring_282.copy()
                        local_prm_SensitivityScoring_282['dlfile'] = (CN, limit_filename)
                        self.oServo.St(local_prm_SensitivityScoring_282)
                  else:
                     if getattr(TP, 'prm_VCM_SensitivityScoring_282', 0):
                        local_prm_SensitivityScoring_282 = TP.prm_VCM_SensitivityScoring_282.copy()
                        local_prm_SensitivityScoring_282['dlfile'] = (CN, limit_filename)
                        self.oServo.St(local_prm_SensitivityScoring_282)
               else:
                  if testSwitch.FE_0122163_357915_DUAL_STAGE_ACTUATOR_SUPPORT:
                     if getattr(TP, 'prm_DS_SensitivityScoring_288', 0):
                        local_prm_SensitivityScoring_288 = TP.prm_DS_SensitivityScoring_288.copy()
                        local_prm_SensitivityScoring_288['dlfile'] = (CN, limit_filename)
                        self.oServo.St(local_prm_SensitivityScoring_288)
                  else:
                     if getattr(TP, 'prm_VCM_SensitivityScoring_288', 0):
                        local_prm_SensitivityScoring_288 = TP.prm_VCM_SensitivityScoring_288.copy()
                        local_prm_SensitivityScoring_288['dlfile'] = (CN, limit_filename)
                        self.oServo.St(local_prm_SensitivityScoring_288)
         else:
            # Use the original (python based) sensitivity margin screen, if a product specific parameter set exists
            if getattr(TP, 'bodeSensScoringPrm_152', 0):
               from Servo import CServoOpti
               self.oSrvOpti = CServoOpti()
               self.oSrvOpti.bodeSensitivityScoring(TP.bodeSensScoringPrm_152,TP.prm_bodeSensScoringMargins)
               self.oSrvOpti = None  # Allow Garbage Collection

      # Run LUL special screening 
      if testSwitch.extern.FE_0313720_080860_LUL_ODCS_SCREEN and not testSwitch.HAMR:
         try:
            self.oServo.St(TP.lul_prm_CheckReverseIPS_025)
         except:
            objPwrCtrl.powerCycle(5000,12000,10,10, useESlip=1)

      self.oServo.setQuietSeek(TP.quietSeekPrm_11, setQSeekOn = 1) #enable quiet seek

   #-------------------------------------------------------------------------------------------------------
   def BodeScreenRange(self,testCyl = 0, gainFreqFilter_152 = [(8000,23000,  0),], spc_id = 1):
         if not testSwitch.BodeScreen:
            return

         logdata = self.dut.dblData.Tables('P152_BODE_GAIN_PHASE').chopDbLog('SPC_ID', 'match',str(spc_id))
         #objMsg.printMsg("data ==>%s" %str(logdata))
         #objMsg.printMsg("P152 table:--> %s" %str(self.dut.dblData.Tables('P152_BODE_GAIN_PHASE')) )
         self.bodeDict = {}
         for record in logdata:
            freqBode = int(record['FREQUENCY'])
            gainBode = float(record['GAIN'])
            Hd = int(record['HD_LGC_PSN'])
            if not self.bodeDict.has_key(Hd): self.bodeDict[Hd] = {}
            for filterIndex in xrange(len(gainFreqFilter_152)):
               if freqBode >= gainFreqFilter_152[filterIndex][0] and freqBode <= gainFreqFilter_152[filterIndex][1] :
                  if (not self.bodeDict[Hd].has_key(filterIndex)) or (gainBode > self.bodeDict[Hd][filterIndex]):
                     self.bodeDict[Hd][filterIndex] = gainBode

         screenStatus = 1
         if self.bodeDict.values():
            for Hd in self.bodeDict.keys():
               for filterIndex in xrange(len(gainFreqFilter_152)):
                  gainBode = self.bodeDict[Hd][filterIndex]
                  gainStatus = 1
                  if gainFreqFilter_152[filterIndex][2] > 0 and gainBode > gainFreqFilter_152[filterIndex][2]:
                     gainStatus = 0
                     screenStatus = 0
                  self.dut.dblData.Tables('P152_BODE_SCRN_SUM').addRecord({
                     'HD_PHYS_PSN'       : Hd,#self.oFSO.getLgcToPhysHdMap(Hd),
                     'TRACK'             : testCyl,
                     'SPC_ID'            : 0,
                     'OCCURRENCE'        : self.dut.objSeq.getOccurrence(),
                     'SEQ'               : self.dut.objSeq.curSeq,
                     'TEST_SEQ_EVENT'    : self.dut.objSeq.getTestSeqEvent(0),
                     'HD_LGC_PSN'        : Hd,
                     'FILTER_IDX'        : filterIndex,
                     'FREQ_START'        : gainFreqFilter_152[filterIndex][0],
                     'FREQ_END'          : gainFreqFilter_152[filterIndex][1],
                     'MAX_GAIN'          : gainBode,
                     'GAIN_LIMIT'        : gainFreqFilter_152[filterIndex][2],
                     'STATUS'            : gainStatus,
                  })
            objMsg.printDblogBin(self.dut.dblData.Tables('P152_BODE_SCRN_SUM'))
            if not screenStatus and not testSwitch.virtualRun and testSwitch.BodeScreen_Fail_Enabled :
               ScrCmds.raiseException(10137, "Exceed max P152 gain threshold.")

            #MaxGain = max(self.bodeDict.values())
            #if  MaxGain > threshold and not testSwitch.virtualRun:
            #    ScrCmds.raiseException(10137, "exceed max P152 gain threshold %f" %highFreq)
            #else:
            #    objMsg.printMsg("Max Gain %4f %s Hz to %s Hz Bode Screen Passed. " %(MaxGain, str(lowFreq), str(highFreq)))
            #

         return self.bodeDict
         """
P152_BODE_GAIN_PHASE:
 HD_PHYS_PSN FREQUENCY HD_LGC_PSN    GAIN   PHASE
           0       500          0  -10.33  139.85
           0       550          0   -9.86  121.52
           0       600          0   -7.40  127.25
           0       650          0   -6.36  116.93

         """


#----------------------------------------------------------------------------------------------------------
class CSNO(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if not testSwitch.RUN_SNO:
         return
      
      from Servo import CServo
      from Servo import CServoOpti  
      self.oServo = CServo()
      self.oSrvOpti = CServoOpti()
      
      objMsg.printMsg("Using class frm base.")
      self.oServo.setQuietSeek(TP.quietSeekPrm_11, setQSeekOn = 0) #disable quiet seek

      # Fetch max track of each hd
      CFSO().getZoneTable()
      self.maxTrack = CFSO().dut.maxTrack   # a list is return
      objMsg.printMsg("Max Cyl for Hd 0 is %d, assumed to be same for all hds" % self.maxTrack[0])
      OD_TestTrk = int(0.05*self.maxTrack[0]) # 5% of stroke
      ID_TestTrk = int(0.95*self.maxTrack[0]) # 95% of stroke
      #objMsg.printMsg('Dual Stage S function plot begins')

      if not testSwitch.ROSEWOOD7: # remove for test time reduction
          if testSwitch.FE_SGP_REPLACE_T152_WITH_T282 and not (testSwitch.M11P or testSwitch.M11P_BRING_UP):
             SODprm_282 = TP.doBodePrm_282_S_OD
             SODprm_282['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(OD_TestTrk)
             SODprm_282['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(OD_TestTrk)
             SODprm_282['spc_id'] = 104
             self.oServo.St(SODprm_282) #dual stage S function Bode 500-24kHz
              
             if testSwitch.FE_0264856_480505_USE_OL_GAIN_INSTEAD_OF_S_GAIN_IN_282:
                objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
                OL_ODprm_282 = TP.doBodePrm_282_OL_OD
                OL_ODprm_282['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(OD_TestTrk)
                OL_ODprm_282['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(OD_TestTrk)
                self.oServo.St(OL_ODprm_282)
                OL_IDprm_282 = TP.doBodePrm_282_OL_ID
                OL_IDprm_282['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(ID_TestTrk)
                OL_IDprm_282['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(ID_TestTrk)
                self.oServo.St(OL_IDprm_282)           
             else:   
                SIDprm_282 = TP.doBodePrm_282_S_ID
                SIDprm_282['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(ID_TestTrk)
                SIDprm_282['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(ID_TestTrk)
                SIDprm_282['spc_id'] = 106
                self.oServo.St(SIDprm_282) #dual stage S function Bode 500-24kHz
             objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

      
      if testSwitch.CHENGAI or testSwitch.ROSEWOOD7 or testSwitch.M11P or testSwitch.M11P_BRING_UP:
         from  PackageResolution import PackageDispatcher
         controller_filename = PackageDispatcher(self.dut, 'CTLR_BIN').getFileName()      
         if controller_filename == None:
            objMsg.printMsg('Missing Controller file, skip SNO state')
            return # exit this class
         
      if testSwitch.WRITE_HDA_TEMPERATURE_TO_SAP:    
         self.oSrvOpti.St(TP.writeHDATemperaturePrm_11['read'])

      self.oSrvOpti.setQuietSeek(TP.quietSeekPrm_11, setQSeekOn = 0) #disable quiet seek

      
      if testSwitch.CHENGAI or testSwitch.ROSEWOOD7 or testSwitch.M11P or testSwitch.M11P_BRING_UP:
         local_doBodeSNO_282 = {'test_num':282, 'timeout':100, 'CWORD1':0x00F8}
         local_doBodeSNO_282 = TP.doBodeSNO_282.copy()
         local_doBodeSNO_282['dlfile'] = (CN, controller_filename)
         if testSwitch.ROSEWOOD7:
            self.oSrvOpti.doSNO(local_doBodeSNO_282, TP.snoNotches_282_VCM)
            if testSwitch.IS_2D_DRV == 1 and (int(self.dut.driveattr['PROC_CTRL6'][-5:]) == 10137 or self.dut.BTC):
               try:
                  expression = "snoNotches_282_DAC = self.oSrvOpti.oUtility.copy(TP.snoNotches_282_DAC_%s)"%self.dut.driveattr.get('SERVO_INFO', 'XXXX')[0:4].upper()
                  exec(expression)
               except:
                  snoNotches_282_DAC = self.oSrvOpti.oUtility.copy(TP.snoNotches_282_DAC)
            else:
               snoNotches_282_DAC = self.oSrvOpti.oUtility.copy(TP.snoNotches_282_DAC)
            self.oSrvOpti.doSNO(local_doBodeSNO_282, snoNotches_282_DAC)
         else:
            if testSwitch.M11P or testSwitch.M11P_BRING_UP:
               self.oSrvOpti.doSNO(local_doBodeSNO_282, TP.snoNotches_282_VCM1)
               self.oSrvOpti.doSNO(local_doBodeSNO_282, TP.snoNotches_282_VCM2)
               self.oSrvOpti.doSNO(local_doBodeSNO_282, TP.snoNotches_282_VCM3)
               self.oSrvOpti.doSNO(local_doBodeSNO_282, TP.snoNotches_282_VCM4)
               self.oSrvOpti.doSNO(local_doBodeSNO_282, TP.snoNotches_282_VCM5)
               self.oSrvOpti.doSNO(local_doBodeSNO_282, TP.snoNotches_282_VCM6)
               self.oSrvOpti.doSNO(local_doBodeSNO_282, TP.snoNotches_282_VCM7)
               self.oSrvOpti.doSNO(local_doBodeSNO_282, TP.snoNotches_282_VCM8)  
               self.oSrvOpti.doSNO(local_doBodeSNO_282, TP.snoNotches_282_DAC1)
               self.oSrvOpti.doSNO(local_doBodeSNO_282, TP.snoNotches_282_DAC2)
               self.oSrvOpti.doSNO(local_doBodeSNO_282, TP.snoNotches_282_DAC3)
               self.oSrvOpti.doSNO(local_doBodeSNO_282, TP.snoNotches_282_DAC4)
               self.oSrvOpti.doSNO(local_doBodeSNO_282, TP.snoNotches_282_DAC5)
               self.oSrvOpti.doSNO(local_doBodeSNO_282, TP.snoNotches_282_DAC6)
               self.oSrvOpti.doSNO(local_doBodeSNO_282, TP.snoNotches_282_DAC7)
               self.oSrvOpti.doSNO(local_doBodeSNO_282, TP.snoNotches_282_DAC8)
               self.oSrvOpti.doSNO(local_doBodeSNO_282, TP.snoNotches_282_DAC9)
            else:
               self.oSrvOpti.doSNO(local_doBodeSNO_282, TP.snoNotches_282_VCM2)
               self.oSrvOpti.doSNO(local_doBodeSNO_282, TP.snoNotches_282_DAC2)
      else:
         self.oSrvOpti.doSNO(TP.CktSNO_152, TP.CktNotches_152)

      self.oSrvOpti.St(TP.saveSvoRam2Flash_178)        #write to SAP
      if testSwitch.WRITE_HDA_TEMPERATURE_TO_SAP:
         self.oSrvOpti.St(TP.writeHDATemperaturePrm_11['read'])

#----------------------------------------------------------------------------------------------------------
class CSNOPkDetect(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if not testSwitch.RUN_SNO_PD:
         return

      from PackageResolution import PackageDispatcher
      from Servo import CServo
      from Servo import CServoOpti
      self.oServo = CServo()
      self.oSrvOpti = CServoOpti()

      #=== Disable quiet seek
      self.oSrvOpti.setQuietSeek(TP.quietSeekPrm_11, setQSeekOn = 0)
      objMsg.printMsg('Perform SNO with Phase Peak Detection')
  
      CFSO().getZoneTable()
      self.maxTrack = CFSO().dut.maxTrack   # a list is return
      objMsg.printMsg("Max Cyl for Hd 0 is %d, assumed to be same for all hds" % self.maxTrack[0])
      OD_TestTrk = int(0.04*self.maxTrack[0]) # 4% of stroke
      ID_TestTrk = int(0.99*self.maxTrack[0]) # 99% of stroke
      step = int(0.05*self.maxTrack[0]) 
      
      if testSwitch.ROSEWOOD7:
         if testSwitch.extern.FE_0317356_356996_T282_PHASE_PEAK_DETECTION == 1:
            if 0:
               controller_filename = PackageDispatcher(self.dut, 'CTLR_BIN').getFileName()
               objMsg.printMsg("\n Controller File = %s" %(controller_filename))
               ## Only on H0 for RW1D ##
               for hd in range(1):   #(self.dut.imaxHead):
                  localcopyoftestparam = TP.sno_phase_peak_detect_RW1D_282_OD
                  localcopyoftestparam.update({ 'HEAD_RANGE'  : 0x0101 * hd })
                  localcopyoftestparam['dlfile'] = (CN,controller_filename)
                  self.oSrvOpti.doSNO(localcopyoftestparam, TP.CktNotchesPD_RW1D_282_OD)
               ## Only on H0 for RW1D ##
               for hd in range(1):   #(self.dut.imaxHead):
                  localcopyoftestparam = TP.sno_phase_peak_detect_RW1D_282_ID
                  localcopyoftestparam.update({ 'HEAD_RANGE'  : 0x0101 * hd })
                  localcopyoftestparam['dlfile'] = (CN,controller_filename)
                  self.oSrvOpti.doSNO(localcopyoftestparam, TP.CktNotchesPD_RW1D_282_ID)
               ## Save To Flash ##
               CFSO().saveSAPtoFLASH()
         
         objMsg.printMsg('Skip 282 SNO for RW7 1D/2D Now')

         for hd in xrange(self.dut.imaxHead):
            localcopyoftestparam = TP.sno_phase_peak_detect_152_OD
            localcopyoftestparam.update({ 'HEAD_RANGE'  : 0x0101 * hd })
            self.oSrvOpti.doSNO(localcopyoftestparam, TP.CktNotchesPD_152_OD)

            ph_delta = float(self.dut.dblData.Tables('P152_PHASE_PEAK_SUMMARY').tableDataObj()[-1]['PHASE_DELTA'])
            #if ph_delta < TP.SNO_PHASE_DELTA_LIMIT:
            #   ScrCmds.raiseException(10137,' *** Maximum Phase Delta Exceeded *** ')
            if (testSwitch.FE_0308779_356996_SNO_BODE_DATA_VERIFY and (not (testSwitch.virtualRun))):
               self.verifySnoBodeData (localcopyoftestparam, TP.CktNotchesPD_152_OD, localcopyoftestparam["spc_id"], hd)

         for hd in xrange(self.dut.imaxHead):
            localcopyoftestparam = TP.sno_phase_peak_detect_152_OD_1
            localcopyoftestparam.update({ 'HEAD_RANGE'  : 0x0101 * hd })
            self.oSrvOpti.doSNO(localcopyoftestparam, TP.CktNotchesPD_152_OD_1)
			
            ph_delta = float(self.dut.dblData.Tables('P152_PHASE_PEAK_SUMMARY').tableDataObj()[-1]['PHASE_DELTA'])
            #if ph_delta < TP.SNO_PHASE_DELTA_LIMIT:
               #ScrCmds.raiseException(10137,' *** Maximum Phase Delta Exceeded *** ')
            if (testSwitch.FE_0308779_356996_SNO_BODE_DATA_VERIFY and (not (testSwitch.virtualRun))):
               self.verifySnoBodeData (localcopyoftestparam, TP.CktNotchesPD_152_OD_1, localcopyoftestparam["spc_id"], hd)
         
         for hd in xrange(self.dut.imaxHead):
            localcopyoftestparam = TP.sno_phase_peak_detect_152_OD_2
            localcopyoftestparam.update({ 'HEAD_RANGE'  : 0x0101 * hd })
            self.oSrvOpti.doSNO(localcopyoftestparam, TP.CktNotchesPD_152_OD_2)
			
            ph_delta = float(self.dut.dblData.Tables('P152_PHASE_PEAK_SUMMARY').tableDataObj()[-1]['PHASE_DELTA'])
            #if ph_delta < TP.SNO_PHASE_DELTA_LIMIT:
               #ScrCmds.raiseException(10137,' *** Maximum Phase Delta Exceeded *** ')
            if (testSwitch.FE_0308779_356996_SNO_BODE_DATA_VERIFY and (not (testSwitch.virtualRun))):
               self.verifySnoBodeData (localcopyoftestparam, TP.CktNotchesPD_152_OD_2, localcopyoftestparam["spc_id"], hd)
         for hd in xrange(self.dut.imaxHead):
            localcopyoftestparam = TP.sno_phase_peak_detect_152_OD_3
            localcopyoftestparam.update({ 'HEAD_RANGE'  : 0x0101 * hd })
            self.oSrvOpti.doSNO(localcopyoftestparam, TP.CktNotchesPD_152_OD_3)

            ph_delta = float(self.dut.dblData.Tables('P152_PHASE_PEAK_SUMMARY').tableDataObj()[-1]['PHASE_DELTA'])
            #if ph_delta < TP.SNO_PHASE_DELTA_LIMIT:
               #ScrCmds.raiseException(10137,' *** Maximum Phase Delta Exceeded *** ')
            if (testSwitch.FE_0308779_356996_SNO_BODE_DATA_VERIFY and (not (testSwitch.virtualRun))):
               self.verifySnoBodeData (localcopyoftestparam, TP.CktNotchesPD_152_OD_3, localcopyoftestparam["spc_id"], hd)
         
         if testSwitch.CHENGAI: # chengai-mule only collect OD
            return

         for hd in xrange(self.dut.imaxHead):
            localcopyoftestparam = TP.sno_phase_peak_detect_152_ID
            localSnoSettingID = TP.CktNotchesPD_152_ID
            if testSwitch.FE_0335634_228373_WHOLE_SURFACE_SCAN_IN_SNO:
               for TestTrk in range(OD_TestTrk,ID_TestTrk,step):
                  objMsg.printMsg("Test Cyl is %d, assumed to be same for all hds" % TestTrk)
                  localcopyoftestparam['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(TestTrk)
                  localcopyoftestparam['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(TestTrk)
                  localcopyoftestparam.update({ 'HEAD_RANGE'  : 0x0101 * hd })
                  self.oSrvOpti.doSNO(localcopyoftestparam, localSnoSettingID)
            else:
               localcopyoftestparam['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(ID_TestTrk)
               localcopyoftestparam['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(ID_TestTrk)
               localcopyoftestparam.update({ 'HEAD_RANGE'  : 0x0101 * hd })
               self.oSrvOpti.doSNO(localcopyoftestparam, localSnoSettingID)

            ph_delta = float(self.dut.dblData.Tables('P152_PHASE_PEAK_SUMMARY').tableDataObj()[-1]['PHASE_DELTA'])
            #if ph_delta < TP.SNO_PHASE_DELTA_LIMIT:
               #ScrCmds.raiseException(10137,' *** Maximum Phase Delta Exceeded *** ')
            if (testSwitch.FE_0308779_356996_SNO_BODE_DATA_VERIFY and (not (testSwitch.virtualRun))):
               self.verifySnoBodeData (localcopyoftestparam, localSnoSettingID, localcopyoftestparam["spc_id"], hd)

         for hd in xrange(self.dut.imaxHead):
            localcopyoftestparam = TP.sno_phase_peak_detect_152_ID_1
            if testSwitch.FE_0335634_228373_WHOLE_SURFACE_SCAN_IN_SNO:
               for TestTrk in range(OD_TestTrk,ID_TestTrk,step):
                  objMsg.printMsg("Test Cyl is %d, assumed to be same for all hds" % TestTrk)
                  localcopyoftestparam['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(TestTrk)
                  localcopyoftestparam['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(TestTrk)
                  localcopyoftestparam.update({ 'HEAD_RANGE'  : 0x0101 * hd })
                  self.oSrvOpti.doSNO(localcopyoftestparam, TP.CktNotchesPD_152_ID_1)
            else:
               localcopyoftestparam['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(ID_TestTrk)
               localcopyoftestparam['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(ID_TestTrk)
               localcopyoftestparam.update({ 'HEAD_RANGE'  : 0x0101 * hd })
               self.oSrvOpti.doSNO(localcopyoftestparam, TP.CktNotchesPD_152_ID_1)

            ph_delta = float(self.dut.dblData.Tables('P152_PHASE_PEAK_SUMMARY').tableDataObj()[-1]['PHASE_DELTA'])
            #if ph_delta < TP.SNO_PHASE_DELTA_LIMIT:
               #ScrCmds.raiseException(10137,' *** Maximum Phase Delta Exceeded *** ')
            if (testSwitch.FE_0308779_356996_SNO_BODE_DATA_VERIFY and (not (testSwitch.virtualRun))):
               self.verifySnoBodeData (localcopyoftestparam, TP.CktNotchesPD_152_ID_1, localcopyoftestparam["spc_id"], hd)

         for hd in xrange(self.dut.imaxHead):
            localcopyoftestparam = TP.sno_phase_peak_detect_152_ID_2
            if testSwitch.FE_0335634_228373_WHOLE_SURFACE_SCAN_IN_SNO:
               for TestTrk in range(OD_TestTrk,ID_TestTrk,step):
                  objMsg.printMsg("Test Cyl is %d, assumed to be same for all hds" % TestTrk)
                  localcopyoftestparam['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(TestTrk)
                  localcopyoftestparam['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(TestTrk)
                  localcopyoftestparam.update({ 'HEAD_RANGE'  : 0x0101 * hd })
                  self.oSrvOpti.doSNO(localcopyoftestparam, TP.CktNotchesPD_152_ID_2)
            else:
               localcopyoftestparam['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(ID_TestTrk)
               localcopyoftestparam['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(ID_TestTrk)
               localcopyoftestparam.update({ 'HEAD_RANGE'  : 0x0101 * hd })
               self.oSrvOpti.doSNO(localcopyoftestparam, TP.CktNotchesPD_152_ID_2)

            ph_delta = float(self.dut.dblData.Tables('P152_PHASE_PEAK_SUMMARY').tableDataObj()[-1]['PHASE_DELTA'])
            #if ph_delta < TP.SNO_PHASE_DELTA_LIMIT:
               #ScrCmds.raiseException(10137,' *** Maximum Phase Delta Exceeded *** ')
            if (testSwitch.FE_0308779_356996_SNO_BODE_DATA_VERIFY and (not (testSwitch.virtualRun))):
               self.verifySnoBodeData (localcopyoftestparam, TP.CktNotchesPD_152_ID_2, localcopyoftestparam["spc_id"], hd)
      
         for hd in xrange(self.dut.imaxHead):
            localcopyoftestparam = TP.sno_phase_peak_detect_152_ID_3
            if testSwitch.FE_0335634_228373_WHOLE_SURFACE_SCAN_IN_SNO:
               for TestTrk in range(OD_TestTrk,ID_TestTrk,step):
                  objMsg.printMsg("Test Cyl is %d, assumed to be same for all hds" % TestTrk)
                  localcopyoftestparam['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(TestTrk)
                  localcopyoftestparam['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(TestTrk)
                  localcopyoftestparam.update({ 'HEAD_RANGE'  : 0x0101 * hd })
                  self.oSrvOpti.doSNO(localcopyoftestparam, TP.CktNotchesPD_152_ID_3)
            else:
               localcopyoftestparam['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(ID_TestTrk)
               localcopyoftestparam['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(ID_TestTrk)
               localcopyoftestparam.update({ 'HEAD_RANGE'  : 0x0101 * hd })
               self.oSrvOpti.doSNO(localcopyoftestparam, TP.CktNotchesPD_152_ID_3)

            ph_delta = float(self.dut.dblData.Tables('P152_PHASE_PEAK_SUMMARY').tableDataObj()[-1]['PHASE_DELTA'])
            #if ph_delta < TP.SNO_PHASE_DELTA_LIMIT:
               #ScrCmds.raiseException(10137,' *** Maximum Phase Delta Exceeded *** ')
            if (testSwitch.FE_0308779_356996_SNO_BODE_DATA_VERIFY and (not (testSwitch.virtualRun))):
               self.verifySnoBodeData (localcopyoftestparam, TP.CktNotchesPD_152_ID_3, localcopyoftestparam["spc_id"], hd)
      
      else:
         self.oSrvOpti.doSNO(TP.sno_phase_peak_detect_152, TP.CktNotchesPD_152)

         ph_delta = float(self.dut.dblData.Tables('P152_PHASE_PEAK_SUMMARY').tableDataObj()[-1]['PHASE_DELTA'])

         if ph_delta < TP.SNO_PHASE_DELTA_LIMIT:
            ScrCmds.raiseException(10137,' *** Maximum Phase Delta Exceeded *** ')
      
      if not testSwitch.FE_0277874_504159_P_UPDATE_SNO_PHASE_DATA:
         return
         
      try:
         #Get min peak frequency
         head = int(self.dut.dblData.Tables('P152_PHASE_PEAK_SUMMARY').tableDataObj()[-1]['HD_LGC_PSN'])
         pk_freq=int(self.dut.dblData.Tables('P152_PHASE_PEAK_SUMMARY').tableDataObj()[-1]['PEAK_FREQUENCY'])

         #check where this frequency lies and update controller selection
         if (pk_freq < 2560):
            contsel = 3
         elif (pk_freq >2750):
            contsel = 4
         else:
            contsel = 0

         # print controller selection mapping number
         objMsg.printMsg("Controller Selection Mapping number = %d" % (contsel))
         # get headtoControllerMap offset and read Controller Map values
         objMsg.printMsg('Fetching Controller Map values.')
         Cont_Map1, Cont_Map2, Cont_Map3, Cont_Map4 = self.oSrvOpti.fetch_CONTROLLER_MAP_16()
         objMsg.printMsg("Controller Values C1= %d, C2= %d, C3= %d, C4= %d" % (Cont_Map1,Cont_Map2,Cont_Map3,Cont_Map4))

         # write new Controller Selection to Controller byte 3
         objMsg.printMsg('Writing new Controller Map values.')
         self.oSrvOpti.set_cont_map(Cont_Map4, contsel)

         # get index for peak frequency from table
         #logdata = self.dut.dblData.Tables('P152_BODE_GAIN_PHASE').tableDataObj()
         logdata = self.dut.dblData.Tables('P152_BODE_GAIN_PHASE').chopDbLog('SPC_ID', 'match',str(TP.sno_phase_peak_detect_152["spc_id"]))

         for i in xrange (len(logdata)):
            frequency = logdata[i]['FREQUENCY']
            phase = logdata[i]['PHASE']
            objMsg.printMsg("frequency = %d, phase = %f" % (int(frequency),int(float(phase))))
            if int(frequency) == pk_freq:
               peakfreqIDX = i
               objMsg.printMsg("peakfreqIDX found = %d" % (peakfreqIDX))
               objMsg.printMsg("store data for index to SNO_PHASE_DATA sap entry 1 & 2; freq = %d , phase = %d" % (int(frequency),int(float(phase))))
               self.oSrvOpti.set_sno_phase_data(int(float(phase)),int(frequency),0)
               # check data for (peak frequency index - 3) entry and whether it is valid
               if (peakfreqIDX-3) > 0:
                  frequency = logdata[peakfreqIDX-3]['FREQUENCY']
                  phase = logdata[peakfreqIDX-3]['PHASE']
               elif (peakfreqIDX-2) > 0:
                  frequency = logdata[peakfreqIDX-2]['FREQUENCY']
                  phase = logdata[peakfreqIDX-2]['PHASE']
               elif (peakfreqIDX-1) > 0:
                  frequency = logdata[peakfreqIDX-1]['FREQUENCY']
                  phase = logdata[peakfreqIDX-1]['PHASE']
               else:
                  frequency = logdata[peakfreqIDX]['FREQUENCY']
                  phase = logdata[peakfreqIDX]['PHASE']
               objMsg.printMsg("store data for (index-3) to SNO_PHASE_DATA sap entry 3 & 4; freq = %d , phase = %d" % (int(frequency),int(float(phase))))
               self.oSrvOpti.set_sno_phase_data(int(float(phase)),int(frequency),4)
               # check data for (peak frequency index - 2) entry and whether it is valid
               if (peakfreqIDX-2) > 0:
                  frequency = logdata[peakfreqIDX-2]['FREQUENCY']
                  phase = logdata[peakfreqIDX-2]['PHASE']
               elif (peakfreqIDX-1) > 0:
                  frequency = logdata[peakfreqIDX-1]['FREQUENCY']
                  phase = logdata[peakfreqIDX-1]['PHASE']
               else:
                  frequency = logdata[peakfreqIDX]['FREQUENCY']
                  phase = logdata[peakfreqIDX]['PHASE']
               objMsg.printMsg("store data for (index-2) to SNO_PHASE_DATA sap entry 5 & 6; freq = %d , phase = %d" % (int(frequency),int(float(phase))))
               self.oSrvOpti.set_sno_phase_data(int(float(phase)),int(frequency),8)
               # check data for (peak frequency index - 1) entry and whether it is valid
               if (peakfreqIDX-1) > 0:
                  frequency = logdata[peakfreqIDX-1]['FREQUENCY']
                  phase = logdata[peakfreqIDX-1]['PHASE']
               else:
                  frequency = logdata[peakfreqIDX]['FREQUENCY']
                  phase = logdata[peakfreqIDX]['PHASE']
               objMsg.printMsg("store data for (index-1) to SNO_PHASE_DATA sap entry 7 & 8; freq = %d , phase = %d" % (int(frequency),int(float(phase))))
               self.oSrvOpti.set_sno_phase_data(int(float(phase)),int(frequency),12)
               # store data for index entry
               frequency = logdata[peakfreqIDX]['FREQUENCY']
               phase = logdata[peakfreqIDX]['PHASE']
               objMsg.printMsg("store data for (index) to SNO_PHASE_DATA sap entry 9 & 10; freq = %d , phase = %d" % (int(frequency),int(float(phase))))
               self.oSrvOpti.set_sno_phase_data(int(float(phase)),int(frequency),16)
               # check data for (peak frequency index + 1) entry and whether it is valid
               if (peakfreqIDX+1) < len(logdata):
                  frequency = logdata[peakfreqIDX+1]['FREQUENCY']
                  phase = logdata[peakfreqIDX+1]['PHASE']
               else:
                  frequency = logdata[peakfreqIDX]['FREQUENCY']
                  phase = logdata[peakfreqIDX]['PHASE']
               objMsg.printMsg("store data for (index+1) to SNO_PHASE_DATA sap entry 11 & 12; freq = %d , phase = %d" % (int(frequency),int(float(phase))))
               self.oSrvOpti.set_sno_phase_data(int(float(phase)),int(frequency),20)
               # check data for (peak frequency index + 2) entry and whether it is valid
               if (peakfreqIDX+2) < len(logdata):
                  frequency = logdata[peakfreqIDX+2]['FREQUENCY']
                  phase = logdata[peakfreqIDX+2]['PHASE']
               elif (peakfreqIDX+1) < len(logdata):
                  frequency = logdata[peakfreqIDX+1]['FREQUENCY']
                  phase = logdata[peakfreqIDX+1]['PHASE']
               else:
                  frequency = logdata[peakfreqIDX]['FREQUENCY']
                  phase = logdata[peakfreqIDX]['PHASE']
               objMsg.printMsg("store data for (index+2) to SNO_PHASE_DATA sap entry 13 & 14; freq = %d , phase = %d" % (int(frequency),int(float(phase))))
               self.oSrvOpti.set_sno_phase_data(int(float(phase)),int(frequency),24)
               # check data for (peak frequency index + 3) entry and whether it is valid
               if (peakfreqIDX+3) < len(logdata):
                  frequency = logdata[peakfreqIDX+3]['FREQUENCY']
                  phase = logdata[peakfreqIDX+3]['PHASE']
               elif (peakfreqIDX+2) < len(logdata):
                  frequency = logdata[peakfreqIDX+2]['FREQUENCY']
                  phase = logdata[peakfreqIDX+2]['PHASE']
               elif (peakfreqIDX+1) < len(logdata):
                  frequency = logdata[peakfreqIDX+1]['FREQUENCY']
                  phase = logdata[peakfreqIDX+1]['PHASE']
               else:
                  frequency = logdata[peakfreqIDX]['FREQUENCY']
                  phase = logdata[peakfreqIDX]['PHASE']
               objMsg.printMsg("store data for (index+3) to SNO_PHASE_DATA sap entry 15 & 16; freq = %d , phase = %d" % (int(frequency),int(float(phase))))
               self.oSrvOpti.set_sno_phase_data(int(float(phase)),int(frequency),28)
               break
         #=== Save SAP to FLASH
         CFSO().saveSAPtoFLASH()

         #power cycle to update sap
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

         # get headtoControllerMap offset and read Controller Map values
         objMsg.printMsg('Checking Controller Map updated values.')
         Cont_Map1, Cont_Map2, Cont_Map3, Cont_Map4 = self.oSrvOpti.fetch_CONTROLLER_MAP_16()
         objMsg.printMsg("Controller Values C1 %d C2 %d C3 %d C4 %d" % (Cont_Map1,Cont_Map2,Cont_Map3,Cont_Map4))
      except: pass

   def verifySnoBodeData (self, testparamInput, NotchesPdInput, spcid, hd=0):
      """
         This function is to verify if SNO bode data is valid
         Return 1 if bode data is normal
         Return 0 if bode data is bad (Fail)
         Current criteria to validate bode data is pk2pk of gain data (Can check phase data also if necessary in future)
      """
      gainMin = 1000
      gainMax = -1000
      logdataStartRow = 0
      for retryLoop in range(TP.SNO_LOOP_LIMIT):
         #objMsg.printMsg("Hd = %d, SNO Loop No = %d" % (hd,(retryLoop+1)))
         logdata = self.dut.dblData.Tables('P152_BODE_GAIN_PHASE').chopDbLog('SPC_ID', 'match',str(spcid))
         logdataChop = self.dut.dblData.Tables('P152_BODE_GAIN_PHASE').chopDbLog('HD_LGC_PSN','match',str(hd),logdata)
         for iii in xrange (logdataStartRow, len(logdataChop)):
            freqTmp = int(logdataChop[iii]['FREQUENCY'])
            gainTmp = float(logdataChop[iii]['GAIN'])
            #objMsg.printMsg("freqChop = %d %s GainChop = %6.2f" % (freqTmp," ",gainTmp))
            if gainTmp < gainMin:
               gainMin = gainTmp
            if gainTmp > gainMax:
               gainMax = gainTmp
         gainPk2pk = gainMax - gainMin
         objMsg.printMsg("Min_Gain = %6.2f %s Max_Gain = %6.2f %s Pk2pk_Gain = %6.2f" % (gainMin," ",gainMax," ",gainPk2pk))
         logdataStartRow = len(logdataChop)
         if gainPk2pk < TP.SNO_GAIN_PK2PK_LIMIT:
            testStatus = 1
            break
         else:
            objMsg.printMsg("SNO Bode Data verification fail")
            txt159 = "SNO Error Log Hd"+str(hd)+" Loop"+str(retryLoop+1)
            self.oSrvOpti.St({'test_num':159,'prm_name':txt159,"CWORD1":1})
            if retryLoop == (TP.SNO_LOOP_LIMIT - 1):
               testStatus = 0
               objMsg.printMsg("SNO Retry Exhausted!! (verifySnoBodeData)")
               ScrCmds.raiseException(10137,' *** Maximum Phase Delta Exceeded *** @ Head : [%s]' %str(hd))
            else:
               gainMin = 1000
               gainMax = -1000
               objMsg.printMsg("Hd = %d, SNO Retry Loop %d" % (hd,(retryLoop+1)))
               self.oSrvOpti.doSNO(testparamInput, NotchesPdInput)   #Rerun
      return testStatus

#----------------------------------------------------------------------------------------------------------
class CBodeScrnAt72RPM(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.bodeDict = {}

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      """
      Class to run only BODE plot, with additional switch to enable screening
      """
      from Servo import CServo
      self.oServo = CServo()

      #=== Disable quiet seek
      self.oServo.setQuietSeek(TP.quietSeekPrm_11, setQSeekOn = 0) 
      
      if 0: # testSwitch.pztCalTestEnabled: - remove uAct tests due to high failure rate
         self.oServo.St(TP.pztCal_332_2) # stress & chk
         self.oServo.St(TP.pztCal_332)   # calibrate
      # Added MR Resistance measurement as a chk bcos this module is run very early, even b4 FOF_Screen
      self.oServo.St(TP.PresetAGC_InitPrm_186,spc_id=10)

      # Fetch max track of each hd
      CFSO().getZoneTable()
      self.maxTrack = CFSO().dut.maxTrack   # a list is return
      objMsg.printMsg("Max Cyl for Hd 0 is %d, assumed to be same for all hds" % self.maxTrack[0])
      OD_TestTrk = int(0.15*self.maxTrack[0]) # 15% of stroke
      MD_TestTrk = int(0.5*self.maxTrack[0])  # 50% of stroke
      ID_TestTrk = int(0.85*self.maxTrack[0]) # 85% of stroke
      #objMsg.printMsg('VCM structural, Dual Stage S function and uAct Structural begin')
      
      if testSwitch.FE_SGP_REPLACE_T152_WITH_T282:
         ODprm_152 = TP.doBodePrm_282_VCM_structural_OD
      else:
         # Run Test 152 to collect Bode data
         ODprm_152 = TP.doBodePrm_152_OD.copy()
         ODprm_152['prm_name'] = 'Do 7200rpm Bode Prm 152 at OD'
      ODprm_152['spc_id'] = 7200
      ODprm_152['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(OD_TestTrk)
      ODprm_152['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(OD_TestTrk)
      self.oServo.St(ODprm_152) #Structural Bode 500-24kHz

      if testSwitch.FE_SGP_REPLACE_T152_WITH_T282:
         MDprm_152 = TP.doBodePrm_282_VCM_structural_MD
      else:
         MDprm_152 = TP.doBodePrm_152_OD.copy()
         MDprm_152['prm_name'] = 'Do 7200rpm Bode Prm 152 at MD'
      MDprm_152['spc_id'] = 7201
      MDprm_152['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(MD_TestTrk)
      MDprm_152['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(MD_TestTrk)
      self.oServo.St(MDprm_152) #Structural Bode 500-24kHz

      if testSwitch.FE_SGP_REPLACE_T152_WITH_T282:
         IDprm_152 = TP.doBodePrm_282_VCM_structural_ID
      else:
         IDprm_152 = TP.doBodePrm_152_OD.copy()
         IDprm_152['prm_name'] = 'Do 7200rpm Bode Prm 152 at ID'
      IDprm_152['spc_id'] = 7202
      IDprm_152['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(ID_TestTrk)
      IDprm_152['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(ID_TestTrk)
      self.oServo.St(IDprm_152) #Structural Bode 500-24kHz

      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      
      if testSwitch.FE_SGP_REPLACE_T152_WITH_T282:
         SODprm_152 = TP.doBodePrm_282_S_OD
      else:
         SODprm_152 = TP.doBodePrm_152_OD.copy()
         SODprm_152['prm_name'] = 'Do 7200rpm SBode Prm 152 at OD'
         SODprm_152['PLOT_TYPE'] = 2
      SODprm_152['spc_id'] = 7203
      SODprm_152['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(OD_TestTrk)
      SODprm_152['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(OD_TestTrk)
      #self.oServo.St(SODprm_152) #S function Bode 500-24kHz

      if testSwitch.FE_SGP_REPLACE_T152_WITH_T282:
         SMDprm_152 = TP.doBodePrm_282_S_MD
      else:
         SMDprm_152 = TP.doBodePrm_152_OD.copy()
         SMDprm_152['prm_name'] = 'Do 7200rpm SBode Prm 152 at MD'
         SMDprm_152['PLOT_TYPE'] = 2
      SMDprm_152['spc_id'] = 7204
      SMDprm_152['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(MD_TestTrk)
      SMDprm_152['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(MD_TestTrk)
      #self.oServo.St(SMDprm_152) #S function Bode 500-24kHz

      if testSwitch.FE_SGP_REPLACE_T152_WITH_T282:
         SIDprm_152 = TP.doBodePrm_282_S_ID
      else:      
         SIDprm_152 = TP.doBodePrm_152_OD.copy()
         SIDprm_152['prm_name'] = 'Do 7200rpm SBode Prm 152 at ID'
         SIDprm_152['PLOT_TYPE'] = 2
      SIDprm_152['spc_id'] = 7205
      SIDprm_152['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(ID_TestTrk)
      SIDprm_152['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(ID_TestTrk)
      #self.oServo.St(SIDprm_152) #S function Bode 500-24kHz

      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      if testSwitch.FE_SGP_REPLACE_T152_WITH_T282:
         ## uAct Structural plot
         SODprm_282 = TP.doBodePrm_282_uAct_structural_OD
         SODprm_282['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(OD_TestTrk)
         SODprm_282['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(OD_TestTrk)
         SODprm_282['spc_id'] = 7206
         self.oServo.St(SODprm_282) #dual stage uAct structural Bode 500-24kHz
         SMDprm_282 = TP.doBodePrm_282_uAct_structural_MD
         SMDprm_282['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(MD_TestTrk)
         SMDprm_282['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(MD_TestTrk)
         SMDprm_282['spc_id'] = 7207
         self.oServo.St(SMDprm_282) #dual stage uAct structuralBode 500-24kHz
         SIDprm_282 = TP.doBodePrm_282_uAct_structural_ID
         SIDprm_282['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(ID_TestTrk)
         SIDprm_282['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(ID_TestTrk)
         SIDprm_282['spc_id'] = 7208
         self.oServo.St(SIDprm_282) #dual stage uAct structuralBode 500-24kHz
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      
      #objMsg.printMsg("P152 table:--> %s" %str(self.dut.dblData.Tables('P152_BODE_GAIN_PHASE')) )
      #Delete file pointers
      try:
          self.dut.dblData.Tables('P152_BODE_GAIN_PHASE').deleteIndexRecords(1)
          #Delete RAM objects
          self.dut.dblData.delTable('P152_BODE_GAIN_PHASE')
      except:pass

      if 0: # The segment below need some modification before enabling, esp testparms - SWLeow
         # Screen OD
         self.oServo.St(TP.doBode_screen_Prm_152_OD)
         testCyl = (TP.doBode_screen_Prm_152_OD['START_CYL'][0] << 16) + TP.doBode_screen_Prm_152_OD['START_CYL'][1]
         self.BodeScreenRange(testCyl, TP.gainFreqFilter_152)

         # Screen MD
         self.oServo.St(TP.doBode_screen_Prm_152_MD)
         testCyl = (TP.doBode_screen_Prm_152_MD['START_CYL'][0] << 16) + TP.doBode_screen_Prm_152_MD['START_CYL'][1]
         self.BodeScreenRange(testCyl, TP.gainFreqFilter_152)

         # Screen ID
         self.oServo.St(TP.doBode_screen_Prm_152_ID)
         testCyl = (TP.doBode_screen_Prm_152_ID['START_CYL'][0] << 16) + TP.doBode_screen_Prm_152_ID['START_CYL'][1]
         self.BodeScreenRange(testCyl, TP.gainFreqFilter_152)

   #-------------------------------------------------------------------------------------------------------
   def BodeScreenRange(self,testCyl = 0, gainFreqFilter_152 = [(8000,23000,  0),]):

       logdata = self.dut.dblData.Tables('P152_BODE_GAIN_PHASE').tableDataObj()
       #objMsg.printMsg("data ==>%s" %str(logdata))
       #objMsg.printMsg("P152 table:--> %s" %str(self.dut.dblData.Tables('P152_BODE_GAIN_PHASE')) )
       self.bodeDict = {}
       for record in logdata:
          freqBode = int(record['FREQUENCY'])
          gainBode = float(record['GAIN'])
          Hd = int(record['HD_PHYS_PSN'])
          if not self.bodeDict.has_key(Hd): self.bodeDict[Hd] = {}
          for filterIndex in xrange(len(gainFreqFilter_152)):
             if freqBode >= gainFreqFilter_152[filterIndex][0] and freqBode <= gainFreqFilter_152[filterIndex][1] :
                if (not self.bodeDict[Hd].has_key(filterIndex)) or (gainBode > self.bodeDict[Hd][filterIndex]):
                   self.bodeDict[Hd][filterIndex] = gainBode

       screenStatus = 1
       if self.bodeDict.values():
          for Hd in self.bodeDict.keys():
             for filterIndex in xrange(len(gainFreqFilter_152)):
                gainBode = self.bodeDict[Hd][filterIndex]
                gainStatus = 1
                if gainFreqFilter_152[filterIndex][2] > 0 and gainBode > gainFreqFilter_152[filterIndex][2]:
                   gainStatus = 0
                   screenStatus = 0
                self.dut.dblData.Tables('P152_BODE_SCRN_SUM').addRecord({
                   'HD_PHYS_PSN'       : Hd,#self.oFSO.getLgcToPhysHdMap(Hd),
                   'TRACK'             : testCyl,
                   'SPC_ID'            : 0,
                   'OCCURRENCE'        : self.dut.objSeq.getOccurrence(),
                   'SEQ'               : self.dut.objSeq.curSeq,
                   'TEST_SEQ_EVENT'    : self.dut.objSeq.getTestSeqEvent(0),
                   'HD_LGC_PSN'        : Hd,
                   'FILTER_IDX'        : filterIndex,
                   'FREQ_START'        : gainFreqFilter_152[filterIndex][0],
                   'FREQ_END'          : gainFreqFilter_152[filterIndex][1],
                   'MAX_GAIN'          : gainBode,
                   'GAIN_LIMIT'        : gainFreqFilter_152[filterIndex][2],
                   'STATUS'            : gainStatus,
                })
          objMsg.printDblogBin(self.dut.dblData.Tables('P152_BODE_SCRN_SUM'))
          if not screenStatus and not testSwitch.virtualRun:
             ScrCmds.raiseException(10137, "Exceed max P152 gain threshold.")

          #MaxGain = max(self.bodeDict.values())
          #if  MaxGain > threshold and not testSwitch.virtualRun:
          #    ScrCmds.raiseException(10137, "exceed max P152 gain threshold %f" %highFreq)
          #else:
          #    objMsg.printMsg("Max Gain %4f %s Hz to %s Hz Bode Screen Passed. " %(MaxGain, str(lowFreq), str(highFreq)))
          #
       try:
          #Delete file pointers
          self.dut.dblData.Tables('P152_BODE_GAIN_PHASE').deleteIndexRecords(1)
          #Delete RAM objects
          self.dut.dblData.delTable('P152_BODE_GAIN_PHASE')
       except:
          pass

       return self.bodeDict


#----------------------------------------------------------------------------------------------------------
class CuJog(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params=[]):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      self.oProc = CProcess()

      if testSwitch.FE_0159597_357426_DSP_SCREEN == 1:
         if self.dut.nextState == 'AGC_JOG_DSP':
            from SampleMonitor import TD
            T238prm={}
            T238prm.update(TP.base_PHAST_AGC_JOG_238)
            objMsg.printMsg("DSPtruthValue2 is %x" % TD.Truth)
            DSP_Head =  TD.Truth << 8
            objMsg.printMsg("DSPruthValue3 is %x" %  DSP_Head)
            DSP_Head2 = TD.Truth | DSP_Head
            objMsg.printMsg("MODTruthValue is %x" % DSP_Head2)
            T238prm["TEST_HEAD"]=(DSP_Head2,) # add DSP head
            self.oProc.St(T238prm)
         else:
            self.oProc.St(TP.base_PHAST_AGC_JOG_238)
      else:
         base_PHAST_AGC_JOG_238 = TP.base_PHAST_AGC_JOG_238
         for head in range(self.dut.imaxHead):
            base_PHAST_AGC_JOG_238.update({'TEST_HEAD':(head<<8|head)})
            try:
               self.oProc.St(base_PHAST_AGC_JOG_238)
            except:
               #from Cell import theCell
               #import base_BaudFunctions
               #base_BaudFunctions.basicPowerCycle()
               #theCell.enableESlip()
               objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
               self.oProc.St(TP.spindownPrm_2)
               self.oProc.St(TP.spinupPrm_1)
               self.oProc.St(base_PHAST_AGC_JOG_238)


#----------------------------------------------------------------------------------------------------------
class CuJog_hc(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params=[]):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      self.oProc = CProcess()
      
      #self.oProc.St(TP.prm_506_RESET_RUNTIME)
      zntbl = self.dut.dblData.Tables(TP.zone_table['table_name']).tableDataObj()      

      self.oProc.St({'test_num':172, 'prm_name':"Retrieve Heater's", 'timeout': 1800, 'CWORD1': (4,)})
      self.oProc.St({'test_num':172, 'prm_name':"Retrieve Clr's", 'timeout': 1800, 'CWORD1': (5,)})

      #=== Set fly height
      from Process import CCudacom
      self.oCudacom = CCudacom()
      for iHd in range(self.dut.imaxHead):
         for iZn in range(self.dut.numZones):
            #also set fly height
            ttrk = self.getTestTrackZonePosition(iHd, iZn, 198, zntbl) #self.getTestTrackZonePosition(iHd, iZn, TP.ZONE_POS, zntbl)
            buf,errorCode = self.oCudacom.Fn(1345, (ttrk & 0xFFFF), ((ttrk >> 16) & 0xFFFF), iHd, 150, 2)   # set fly height

            #result = struct.unpack("L",buf)
            if errorCode != 0:
               ScrCmds.raiseException(11044, 'setFlyHeight Failed !!!')

      self.oProc.St({'test_num':172, 'prm_name':"Retrieve Heater's", 'timeout': 1800, 'CWORD1': (4,)})
      self.oProc.St({'test_num':172, 'prm_name':"Retrieve Clr's", 'timeout': 1800, 'CWORD1': (5,)})

      if testSwitch.FE_0159597_357426_DSP_SCREEN == 1:
         if self.dut.nextState == 'AGC_JOG_DSP':
            from SampleMonitor import TD
            T238prm={}
            T238prm.update(TP.base_PHAST_AGC_JOG_238)
            objMsg.printMsg("DSPtruthValue2 is %x" % TD.Truth)
            DSP_Head =  TD.Truth << 8
            objMsg.printMsg("DSPruthValue3 is %x" %  DSP_Head)
            DSP_Head2 = TD.Truth | DSP_Head
            objMsg.printMsg("MODTruthValue is %x" % DSP_Head2)
            T238prm["TEST_HEAD"]=(DSP_Head2,) # add DSP head
            self.oProc.St(T238prm)
         else:
            self.oProc.St(TP.base_PHAST_AGC_JOG_238)
      else:
         for head in range(self.dut.imaxHead):
            TP.base_PHAST_AGC_JOG_238.update({'TEST_HEAD':(head<<8|head,)})
            try:
               self.oProc.St(TP.base_PHAST_AGC_JOG_238)
            except:
               #from Cell import theCell
               #import base_BaudFunctions
               #base_BaudFunctions.basicPowerCycle()
               #theCell.enableESlip()
               objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
               self.oProc.St(TP.base_PHAST_AGC_JOG_238)

   #-------------------------------------------------------------------------------------------------------
   def getTestTrackZonePosition(self, iHead, iZone, iZonePos, iZoneTable):
      from FSO import dataTableHelper
      self.dth = dataTableHelper()
      Index = self.dth.getFirstRowIndexFromTable_byZone(iZoneTable, iHead, iZone)
      startTrk = int(iZoneTable[Index]['ZN_START_CYL'])
      numTrk = int(iZoneTable[Index]['TRK_NUM'])
      while Index+1< len(iZoneTable) and int(iZoneTable[Index]['ZN']) == int(iZoneTable[Index+1]['ZN']):
         numTrk += int(iZoneTable[Index+1]['TRK_NUM'])
         Index += 1   
      znPct = (iZonePos)/(199.0)
      return int( (numTrk * znPct) + startTrk )


#----------------------------------------------------------------------------------------------------------
class CZest(CState):
   """
      Run the PRISM/ZEST test (test 287).
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if testSwitch.RUN_ZEST:
         oProc = CProcess()

         if self.params.get('ZEST_OFF', 0):
            oProc.St(TP.zestPrm_11_zestOff)

         if self.params.get('SPIN_UP', 0):
            oProc.St(TP.spinupPrm_1)

         # Set to allow access to FAFH Zones at beginning of STATE
         if testSwitch.IS_FAFH: 
            oProc.St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value
            oProc.St(TP.AllowFAFH_AccessBit_178) # Allow FAFH access for servo test
            oProc.St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value

         if testSwitch.ENABLE_T175_ZAP_CONTROL:
            oProc.St(TP.zapPrm_175_zapOff)
         else:
            oProc.St(TP.setZapOffPrm_011)
            if not testSwitch.BF_0119055_231166_USE_SVO_CMD_ZAP_CTRL:
               oProc.St({'test_num':178, 'prm_name':'Save SAP in RAM to FLASH', 'CWORD1':0x420})

         try:
            oProc.St(TP.prism_zest_287)
         except:
            objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=1, onTime=5, useESlip=1) # Powercycle at the end of the test
            oProc.St(TP.prism_zest_287)

         # Set to dis-allow access to FAFH Zones at end of STATE
         if testSwitch.IS_FAFH: 
            oProc.St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value
            oProc.St(TP.DisallowFAFH_AccessBit_178) # Dis-allow FAFH access after completing servo test
            oProc.St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value

         if testSwitch.FE_0320939_305538_P_T287_ZEST_SCREEN_SPEC:
            from dbLogUtilities import DBLogCheck
            dblchk = DBLogCheck(self.dut)
            if (dblchk.checkComboScreen(TP.Zest_Screen_Spec) == FAIL):
               if testSwitch.ENABLE_ON_THE_FLY_DOWNGRADE and self.downGradeOnFly(1, 48562):
                  objMsg.printMsg('Failed for Zest combo spec, downgrade to %s as %s' % (self.dut.BG, self.dut.partNum))
               else:
                  ScrCmds.raiseException(48562, 'Failed for Zest combo spec @ Head : %s' % str(dblchk.failHead))

         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=1, onTime=5, useESlip=1) # Powercycle at the end of the test


#----------------------------------------------------------------------------------------------------------
class CVCMOffsetScreen(CState):
   """
   Description: Class that will perform spin chip screen
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self,dut,depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      oProc = CProcess()

      # Run T57 spin chip screen
      oProc.St(TP.prm_57_VCM_Offset_Screen)


#----------------------------------------------------------------------------------------------------------
class CTwoT189Cal(CState):
   """
   Two-T189 Cal at CRT2
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      #self.oSrvOpti = CServoOpti()
      oFSO = CFSO()
      objMsg.printMsg("Using class frm base.")

      # Read Master Heat SAP entry
      CFSO().St(TP.masterHeatPrm_11['read'])
      MHBit = int(self.dut.dblData.Tables('P011_SV_RAM_RD_BY_OFFSET').tableDataObj()[-1]['READ_DATA'],16)
      objMsg.printMsg("MHBit = %d" % (MHBit))
      try:
         masterHeatOff = self.dut.objData.retrieve('masterHeatOff')
      except:
         masterHeatOff = 0
      # Disable Master Heat if it is enabled
      if MHBit == 1:
         CFSO().St(TP.masterHeatPrm_11['disable'])
         CFSO().St(TP.masterHeatPrm_11['saveSAP'])
         CFSO().St(TP.masterHeatPrm_11['read'])
         self.dut.objData.update({'masterHeatOff':1}) #for power loss
      # Set to allow access to FAFH Zones at beginning of STATE
      if testSwitch.IS_FAFH: 
         CFSO().St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value
         CFSO().St(TP.AllowFAFH_AccessBit_178) # Allow FAFH access for servo test
         CFSO().St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value 

      try:
         if testSwitch.extern.FE_0118730_010200_T47_AND_T189_MDW_CAL_TTR and hasattr(TP, 'dcSkewCalTTRPrm_189'):
            oFSO.St(TP.dcSkewCalTTRPrm_189)
         else:
            oFSO.St(TP.enableMDWUncalBit_11)
            CProcess().St({'test_num' : 178, 'prm_name' : 'saveSAP2Flash_178', 'CWORD1' : 0x420,})        #write to SAP
            objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1) #perform power cycle before this test
            objMsg.printMsg("Power Cycle Complete")

            oFSO.St(TP.readMDWUncalBit_11)
            #oFSO.St(TP.headSkewCalPrm_43)
            # if there's a saved SAP operation, FAFH_AllowAccessBit will be cleared
            if testSwitch.IS_FAFH: 
               CFSO().St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value
               CFSO().St(TP.AllowFAFH_AccessBit_178) # Allow FAFH access for servo test
               CFSO().St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value 

            oFSO.St(TP.dcSkewCalPrm_189_1)
            oFSO.St(TP.disableMDWUncalBit_11)
            CProcess().St({'test_num' : 178, 'prm_name' : 'saveSAP2Flash_178', 'CWORD1' : 0x420,})        #write to SAP
            objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1) #perform power cycle before this test
            objMsg.printMsg("Power Cycle Complete")
            
            oFSO.St(TP.readMDWUncalBit_11)

      except ScriptTestFailure, (failureData): 
         if testSwitch.extern.FE_0118730_010200_T47_AND_T189_MDW_CAL_TTR and hasattr(TP, 'dcSkewCalTTRPrm_189'):
            self.dut.stateTransitionEvent = 'reRunMDW'
            objMsg.printMsg('dcSkewCalPrm_189 fail, rerun')
            return
         elif failureData[0][2] in [10806]:
            # Set to dis-allow access to FAFH Zones at end of STATE
            if testSwitch.IS_FAFH: 
               CFSO().St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value
               CFSO().St(TP.DisallowFAFH_AccessBit_178) # Dis-allow FAFH access after completing servo test
               CFSO().St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value

            # re-enable Master Heat if it was previously enabled
            if MHBit == 1 or masterHeatOff == 1:
               CFSO().St(TP.masterHeatPrm_11['enable'])
               CFSO().St(TP.masterHeatPrm_11['saveSAP'])
               CFSO().St(TP.masterHeatPrm_11['read'])
            
            if 'T189_10806' in TP.Proc_Ctrl30_Def and not (int(self.dut.driveattr['PROC_CTRL30'],16) & TP.Proc_Ctrl30_Def['T189_10806']):
               self.dut.driveattr['PROC_CTRL30'] = '0X%X' % (int(self.dut.driveattr.get('PROC_CTRL30', '0'),16) | TP.Proc_Ctrl30_Def['T189_10806'])
               self.dut.stateTransitionEvent = 'restartAtState'
               self.dut.nextState = 'DNLD_CODE5'
               return
            else:
               raise
         else:
            raise

      # Set to dis-allow access to FAFH Zones at end of STATE
      if testSwitch.IS_FAFH: 
         CFSO().St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value
         CFSO().St(TP.DisallowFAFH_AccessBit_178) # Dis-allow FAFH access after completing servo test
         CFSO().St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value

      # re-enable Master Heat if it was previously enabled
      if MHBit == 1 or masterHeatOff == 1:
         CFSO().St(TP.masterHeatPrm_11['enable'])
         CFSO().St(TP.masterHeatPrm_11['saveSAP'])
         CFSO().St(TP.masterHeatPrm_11['read'])

#----------------------------------------------------------------------------------------------------------
class CCompareT189Multi(CState):
   """
   Compare T189 Cal Multiplier at PRE2 with CRT2
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from Servo import CServoFunc
      self.oSrvFunc = CServoFunc()
      oFSO = CFSO()
      objMsg.printMsg("Using class frm base.")

      for head in range(self.dut.imaxHead):
         objMsg.printMsg('Fetching Radial Timing Coefficients.')
         Coeff_Multi, Coeff1_Multi = self.oSrvFunc.fetch_TIMINGCOEFF_16(head)
         objMsg.printMsg("Head= %d" % head)
         objMsg.printMsg("Radial Timing Multiplier at PRE2= %d" % Coeff_Multi)
         objMsg.printMsg("Radial Timing Multiplier at CRT2= %d" % Coeff1_Multi)
         if (Coeff_Multi != Coeff1_Multi):
            ScrCmds.raiseException(10443,' *** Compare Multiplier Results Different *** ')   

#----------------------------------------------------------------------------------------------------------
class CBodeScreen(CState):
   """
   Bode Screen at CRT2
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from Servo import CServo
      from PackageResolution import PackageDispatcher
      self.oServo = CServo()

      # Read Master Heat SAP entry
      CFSO().St(TP.masterHeatPrm_11['read'])
      MHBit = int(self.dut.dblData.Tables('P011_SV_RAM_RD_BY_OFFSET').tableDataObj()[-1]['READ_DATA'],16)
      objMsg.printMsg("MHBit = %d" % (MHBit))
      
      if MHBit == 0:
         try:
            MHBitCM = self.dut.objData.retrieve('BodeMH')
         except:
            MHBitCM = 0
      # Disable Master Heat if it is enabled
      if MHBit == 1:
         self.dut.objData.update({'BodeMH':1})
         CFSO().St(TP.masterHeatPrm_11['disable'])
         CFSO().St(TP.masterHeatPrm_11['saveSAP'])
         CFSO().St(TP.masterHeatPrm_11['read'])

      # Set to allow access to FAFH Zones at beginning of STATE
      if testSwitch.IS_FAFH: 
         CFSO().St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value
         CFSO().St(TP.AllowFAFH_AccessBit_178) # Allow FAFH access for servo test
         CFSO().St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value      

      objMsg.printMsg('VCM structural, uAct Structural, and Dual Stage S function BODE plot begin')



    
      SODprm_282 = TP.doBodePrm_282_VCM_structural_OD
      SODprm_282['spc_id'] = 11
      self.oServo.St(SODprm_282) #single stage vcm structural Bode 500-24kHz
      SIDprm_282 = TP.doBodePrm_282_VCM_structural_ID
      SIDprm_282['spc_id'] = 13
      self.oServo.St(SIDprm_282) #single stage vcm structuralBode 500-24kHz
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

      SODprm_282 = TP.doBodePrm_282_uAct_structural_OD
      SODprm_282['spc_id'] = 17
      self.oServo.St(SODprm_282) #single stage vcm structural Bode 500-24kHz
      SIDprm_282 = TP.doBodePrm_282_uAct_structural_ID
      SIDprm_282['spc_id'] = 19
      self.oServo.St(SIDprm_282) #single stage vcm structuralBode 500-24kHz
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
     
      SODprm_282 = TP.doBodePrm_282_S_OD
      SODprm_282['spc_id'] = 14
      self.oServo.St(SODprm_282) #dual stage S function Bode 500-24kHz
      SIDprm_282 = TP.doBodePrm_282_S_ID
      SIDprm_282['spc_id'] = 16
      self.oServo.St(SIDprm_282) #dual stage S function Bode 500-24kHz
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
    
      # Set to dis-allow access to FAFH Zones at end of STATE
      if testSwitch.IS_FAFH: 
         CFSO().St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value
         CFSO().St(TP.DisallowFAFH_AccessBit_178) # Dis-allow FAFH access after completing servo test
         CFSO().St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value

      # re-enable Master Heat if it was previously enabled
      if MHBit == 1 or MHBitCM == 1:
         CFSO().St(TP.masterHeatPrm_11['enable'])
         CFSO().St(TP.masterHeatPrm_11['saveSAP'])
         CFSO().St(TP.masterHeatPrm_11['read'])

#----------------------------------------------------------------------------------------------------------
class CShockSensorScrn(CState):
   """
   Shock Sensor Screen at CRT2
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      #self.oSrvOpti = CServoOpti()
      oFSO = CFSO()

      # Set to allow access to FAFH Zones at beginning of STATE
      if testSwitch.IS_FAFH: 
         CFSO().St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value
         CFSO().St(TP.AllowFAFH_AccessBit_178) # Allow FAFH access for servo test
         CFSO().St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value 

      oFSO.St(TP.ShockSensor_Screen_180) # Shock sensor screen in T180

      # Set to dis-allow access to FAFH Zones at end of STATE
      if testSwitch.IS_FAFH: 
         CFSO().St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value
         CFSO().St(TP.DisallowFAFH_AccessBit_178) # Dis-allow FAFH access after completing servo test
         CFSO().St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value

class CServoOptiCal72(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      """
      Sub Algorithms
      ==============
         FLEX-FCC from Shirish Bahirat
         ========
            1. Flex Bias Calibration
            2. FCC Cal
            3. Flex Bias Calibration
            4. Optional sensitivity margin scoring
      """
      from Servo import CServo
      from PackageResolution import PackageDispatcher
      self.oServo = CServo()
      
      '''
      objMsg.printMsg("Using class frm base.")
      self.oServo.setQuietSeek(TP.quietSeekPrm_11, setQSeekOn = 0) #disable quiet seek

      if testSwitch.pztCalTestEnabled:
         self.oServo.St(TP.pztCal_332)
      '''
      
      if self.dut.nextState == 'SERVO_OPTI72':
         # Fetch max track of each hd
         CFSO().getZoneTable()
         self.maxTrack = CFSO().dut.maxTrack   # a list is return
         objMsg.printMsg("Max Cyl for Hd 0 is %d, assumed to be same for all hds" % self.maxTrack[0])
         OD_TestTrk = int(0.05*self.maxTrack[0]) # 5% of stroke
         MD_TestTrk = int(0.5*self.maxTrack[0])  # 50% of stroke
         ID_TestTrk = int(0.95*self.maxTrack[0]) # 95% of stroke
         #objMsg.printMsg('VCM structural, Dual Stage S function and uAct Structural BODE plot begin')
         
         if testSwitch.FE_SGP_REPLACE_T152_WITH_T282:
            SODprm_282 = TP.doBodePrm_282_VCM_structural_OD
            SODprm_282['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(OD_TestTrk)
            SODprm_282['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(OD_TestTrk)
            self.oServo.St(SODprm_282) #single stage vcm structural Bode 500-24kHz
            # disable for test time review
            #SMDprm_282 = TP.doBodePrm_282_VCM_structural_MD
            #self.oServo.St(SMDprm_282) #single stage vcm structuralBode 500-24kHz
            SIDprm_282 = TP.doBodePrm_282_VCM_structural_ID
            SIDprm_282['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(ID_TestTrk)
            SIDprm_282['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(ID_TestTrk)
            self.oServo.St(SIDprm_282) #single stage vcm structuralBode 500-24kHz
            objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

            SODprm_282 = TP.doBodePrm_282_S_OD
            SODprm_282['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(OD_TestTrk)
            SODprm_282['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(OD_TestTrk)
            self.oServo.St(SODprm_282) #dual stage S function Bode 500-24kHz
            # disable for test time review
            #SMDprm_282 = TP.doBodePrm_282_S_MD
            #self.oServo.St(SMDprm_282) #dual stage S function Bode 500-24kHz
            
            if testSwitch.FE_0264856_480505_USE_OL_GAIN_INSTEAD_OF_S_GAIN_IN_282:
               objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
               OL_ODprm_282 = TP.doBodePrm_282_OL_OD
               OL_ODprm_282['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(OD_TestTrk)
               OL_ODprm_282['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(OD_TestTrk)
               self.oServo.St(OL_ODprm_282)
               OL_IDprm_282 = TP.doBodePrm_282_OL_ID
               OL_IDprm_282['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(ID_TestTrk)
               OL_IDprm_282['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(ID_TestTrk)
               self.oServo.St(OL_IDprm_282)           
            else:   
               SIDprm_282 = TP.doBodePrm_282_S_ID
               SIDprm_282['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(ID_TestTrk)
               SIDprm_282['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(ID_TestTrk)
               self.oServo.St(SIDprm_282) #dual stage S function Bode 500-24kHz
            objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

            SODprm_282 = TP.doBodePrm_282_uAct_structural_OD
            SODprm_282['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(OD_TestTrk)
            SODprm_282['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(OD_TestTrk)
            self.oServo.St(SODprm_282) #dual stage uAct structural Bode 500-24kHz
            if not testSwitch.ROSEWOOD7 and not testSwitch.WA_0256539_480505_SKDC_M10P_BRING_UP_DEBUG_OPTION:
               SMDprm_282 = TP.doBodePrm_282_uAct_structural_MD
               SMDprm_282['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(MD_TestTrk)
               SMDprm_282['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(MD_TestTrk)
               self.oServo.St(SMDprm_282) #dual stage uAct structuralBode 500-24kHz
            SIDprm_282 = TP.doBodePrm_282_uAct_structural_ID
            SIDprm_282['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(ID_TestTrk)
            SIDprm_282['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(ID_TestTrk)
            self.oServo.St(SIDprm_282) #dual stage uAct structuralBode 500-24kHz
            objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
            
            ### Sensitivity Scoring Plot ###
            '''
            sens_limit_filename = PackageDispatcher(self.dut, 'SVO_BIN').getFileName()
            if sens_limit_filename != None and testSwitch.FE_0322256_356996_T282_SENSITIVITY_LIMIT_CHECK:
               #if testSwitch.IS_2D_DRV == 0:
               objMsg.printMsg("\n Sensitivity Limit File = %s" %(sens_limit_filename))
               SODprm_282 = TP.doBodePrm_282_S_Score_OD
               SODprm_282['dlfile'] = (CN,sens_limit_filename)
               SODprm_282['START_CYL'] = CUtility().ReturnTestCylWord(OD_TestTrk)
               SODprm_282['END_CYL'] = CUtility().ReturnTestCylWord(OD_TestTrk)
               self.oServo.St(SODprm_282)
               #For ID cyl
               SIDprm_282 = TP.doBodePrm_282_S_Score_ID
               SIDprm_282['dlfile'] = (CN,sens_limit_filename)
               SIDprm_282['START_CYL'] = CUtility().ReturnTestCylWord(ID_TestTrk)
               SIDprm_282['END_CYL'] = CUtility().ReturnTestCylWord(ID_TestTrk)
               self.oServo.St(SIDprm_282)
               #elif testSwitch.IS_2D_DRV == 1:
                  #objMsg.printMsg('Drive is RW2D. Skip 282 Sensitivity Limit Check For Now')
               objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
            ### Sensitivity Scoring Plot (End) ###
            '''
         
         else:
            ODprm_152 = TP.doBodePrm_152_OD
            ODprm_152['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(OD_TestTrk)
            ODprm_152['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(OD_TestTrk)
            self.oServo.St(ODprm_152) #Structural Bode 500-24kHz
            MDprm_152 = TP.doBodePrm_152_MD
            MDprm_152['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(MD_TestTrk)
            MDprm_152['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(MD_TestTrk)
            self.oServo.St(MDprm_152) #Structural Bode 500-24kHz
            IDprm_152 = TP.doBodePrm_152_ID
            IDprm_152['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(ID_TestTrk)
            IDprm_152['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(ID_TestTrk)
            self.oServo.St(IDprm_152) #Structural Bode 500-24kHz
            SODprm_152 = TP.doBodePrm_152_S_OD
            SODprm_152['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(OD_TestTrk)
            SODprm_152['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(OD_TestTrk)
            self.oServo.St(SODprm_152) #S function Bode 500-24kHz
            self.BodeScreenRange(OD_TestTrk, TP.gainFreqFilter_152, TP.doBodePrm_152_S_OD['spc_id'])
            SMDprm_152 = TP.doBodePrm_152_S_MD
            SMDprm_152['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(MD_TestTrk)
            SMDprm_152['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(MD_TestTrk)
            self.oServo.St(SMDprm_152) #S function Bode 500-24kHz
            self.BodeScreenRange(MD_TestTrk, TP.gainFreqFilter_152, TP.doBodePrm_152_S_MD['spc_id'])
            SIDprm_152 = TP.doBodePrm_152_S_ID
            SIDprm_152['START_CYL'] = self.oServo.oUtility.ReturnTestCylWord(ID_TestTrk)
            SIDprm_152['END_CYL'] = self.oServo.oUtility.ReturnTestCylWord(ID_TestTrk)
            self.oServo.St(SIDprm_152) #S function Bode 500-24kHz
            self.BodeScreenRange(ID_TestTrk, TP.gainFreqFilter_152, TP.doBodePrm_152_S_ID['spc_id'])

            #objMsg.printMsg("P152 table:--> %s" %str(self.dut.dblData.Tables('P152_BODE_GAIN_PHASE')) )
            #Delete file pointers
            try:
                self.dut.dblData.Tables('P152_BODE_GAIN_PHASE').deleteIndexRecords(1)
                #Delete RAM objects
                self.dut.dblData.delTable('P152_BODE_GAIN_PHASE')
            except:pass
      '''
      #### Below subsequence suggested by Shirish Bahirat
      if testSwitch.shortProcess:
         abbreviatedBiasCalParam = TP.flexBiasCalibration_136
         abbreviatedBiasCalParam.update({"SEEK_NUMS" : (2000)})
         self.oServo.St(abbreviatedBiasCalParam)
         self.oServo.St(TP.fccCalPrm_10) #Force constant calibration
         self.oServo.St(abbreviatedBiasCalParam)
      else:
         if self.dut.nextState == 'SERVO_OPTI':
            try:
               #### Below subsequence suggested by Shirish Bahirat
               #self.oServo.St(TP.flexBiasCalibration_136, {'BIAS_SPIKE_LIMIT': 5000})
               self.oServo.St(TP.flexBiasCalibration_136)
            except ScriptTestFailure, (failureData):  # allow retry for EC10136 in SERVO_OPTI with ~30mins full stroke 2-pt seek
               if not testSwitch.ROSEWOOD7 or failureData[0][2] not in [10136]:   # only for RW7, only catch EC10136
                  raise
               #=== Full stroke 2-pt seek ===
               objMsg.printMsg('Failed 10136 - Retry with 2-Pt Full Stroke Seek...')
               self.oServo.St(TP.full_stroke_two_point_sweep, {'PASSES': (25000,)})
               objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=1, onTime=5, useESlip=1)
               self.oServo.St(TP.flexBiasCalibration_136, {'spc_id': 101})
            self.oServo.St(TP.flexBiasCalibration_136_1)
            #SetFailSafe() # Need to add fail safe becos test 10 broken
            self.oServo.St(TP.fccCalPrm_10) #Force constant calibration
            #ClearFailSafe()
         self.oServo.St(TP.flexBiasCalibration_136_2)
         '''
      if 0:    #Will remove this portion of code in future for Rosewood product
         if testSwitch.FE_0142952_010200_SFW_PKG_BIN_SENSITIVITY_SCORING_LIMITS:
            # Check for a sensitivity margin limit file in the servo release package.
            from PackageResolution import PackageDispatcher
            limit_filename = PackageDispatcher(self.dut, 'SVO_BIN').getFileName()
            if (limit_filename != None) and testSwitch.extern.FE_0134761_010200_BINARY_DL_SENSITIVITY_SCORING:
               # If a limit file was included in the servo package, run the sensitivity margin scoring screen
               objMsg.printMsg("Perform sensitivity scoring using limit file '%s'." %str(limit_filename))
               if testSwitch.extern.FE_0148755_010200_SFT_TEST_0282:
                  if testSwitch.FE_0122163_357915_DUAL_STAGE_ACTUATOR_SUPPORT:
                     if getattr(TP, 'prm_DS_SensitivityScoring_282', 0):
                        local_prm_SensitivityScoring_282 = TP.prm_DS_SensitivityScoring_282.copy()
                        local_prm_SensitivityScoring_282['dlfile'] = (CN, limit_filename)
                        self.oServo.St(local_prm_SensitivityScoring_282)
                     if testSwitch.FE_0166236_010200_ADD_VCM_SENSITIVITY_ON_DS_PRODUCTS and getattr(TP, 'prm_VCM_SensitivityScoring_282', 0):
                        # For now, we'll use the same limit file.  This will probably need to be a new limit file at some point in the future...
                        local_prm_SensitivityScoring_282 = TP.prm_VCM_SensitivityScoring_282.copy()
                        local_prm_SensitivityScoring_282['dlfile'] = (CN, limit_filename)
                        self.oServo.St(local_prm_SensitivityScoring_282)
                  else:
                     if getattr(TP, 'prm_VCM_SensitivityScoring_282', 0):
                        local_prm_SensitivityScoring_282 = TP.prm_VCM_SensitivityScoring_282.copy()
                        local_prm_SensitivityScoring_282['dlfile'] = (CN, limit_filename)
                        self.oServo.St(local_prm_SensitivityScoring_282)
               else:
                  if testSwitch.FE_0122163_357915_DUAL_STAGE_ACTUATOR_SUPPORT:
                     if getattr(TP, 'prm_DS_SensitivityScoring_288', 0):
                        local_prm_SensitivityScoring_288 = TP.prm_DS_SensitivityScoring_288.copy()
                        local_prm_SensitivityScoring_288['dlfile'] = (CN, limit_filename)
                        self.oServo.St(local_prm_SensitivityScoring_288)
                  else:
                     if getattr(TP, 'prm_VCM_SensitivityScoring_288', 0):
                        local_prm_SensitivityScoring_288 = TP.prm_VCM_SensitivityScoring_288.copy()
                        local_prm_SensitivityScoring_288['dlfile'] = (CN, limit_filename)
                        self.oServo.St(local_prm_SensitivityScoring_288)
         else:
            # Use the original (python based) sensitivity margin screen, if a product specific parameter set exists
            if getattr(TP, 'bodeSensScoringPrm_152', 0):
               from Servo import CServoOpti
               self.oSrvOpti = CServoOpti()
               self.oSrvOpti.bodeSensitivityScoring(TP.bodeSensScoringPrm_152,TP.prm_bodeSensScoringMargins)
               self.oSrvOpti = None  # Allow Garbage Collection
      '''
      # Run LUL special screening 
      if testSwitch.extern.FE_0313720_080860_LUL_ODCS_SCREEN:
         self.oServo.St(TP.lul_prm_CheckReverseIPS_025)

      self.oServo.setQuietSeek(TP.quietSeekPrm_11, setQSeekOn = 1) #enable quiet seek
      '''
   #-------------------------------------------------------------------------------------------------------
   def BodeScreenRange(self,testCyl = 0, gainFreqFilter_152 = [(8000,23000,  0),], spc_id = 1):
         if not testSwitch.BodeScreen:
            return

         logdata = self.dut.dblData.Tables('P152_BODE_GAIN_PHASE').chopDbLog('SPC_ID', 'match',str(spc_id))
         #objMsg.printMsg("data ==>%s" %str(logdata))
         #objMsg.printMsg("P152 table:--> %s" %str(self.dut.dblData.Tables('P152_BODE_GAIN_PHASE')) )
         self.bodeDict = {}
         for record in logdata:
            freqBode = int(record['FREQUENCY'])
            gainBode = float(record['GAIN'])
            Hd = int(record['HD_LGC_PSN'])
            if not self.bodeDict.has_key(Hd): self.bodeDict[Hd] = {}
            for filterIndex in xrange(len(gainFreqFilter_152)):
               if freqBode >= gainFreqFilter_152[filterIndex][0] and freqBode <= gainFreqFilter_152[filterIndex][1] :
                  if (not self.bodeDict[Hd].has_key(filterIndex)) or (gainBode > self.bodeDict[Hd][filterIndex]):
                     self.bodeDict[Hd][filterIndex] = gainBode

         screenStatus = 1
         if self.bodeDict.values():
            for Hd in self.bodeDict.keys():
               for filterIndex in xrange(len(gainFreqFilter_152)):
                  gainBode = self.bodeDict[Hd][filterIndex]
                  gainStatus = 1
                  if gainFreqFilter_152[filterIndex][2] > 0 and gainBode > gainFreqFilter_152[filterIndex][2]:
                     gainStatus = 0
                     screenStatus = 0
                  self.dut.dblData.Tables('P152_BODE_SCRN_SUM').addRecord({
                     'HD_PHYS_PSN'       : Hd,#self.oFSO.getLgcToPhysHdMap(Hd),
                     'TRACK'             : testCyl,
                     'SPC_ID'            : 0,
                     'OCCURRENCE'        : self.dut.objSeq.getOccurrence(),
                     'SEQ'               : self.dut.objSeq.curSeq,
                     'TEST_SEQ_EVENT'    : self.dut.objSeq.getTestSeqEvent(0),
                     'HD_LGC_PSN'        : Hd,
                     'FILTER_IDX'        : filterIndex,
                     'FREQ_START'        : gainFreqFilter_152[filterIndex][0],
                     'FREQ_END'          : gainFreqFilter_152[filterIndex][1],
                     'MAX_GAIN'          : gainBode,
                     'GAIN_LIMIT'        : gainFreqFilter_152[filterIndex][2],
                     'STATUS'            : gainStatus,
                  })
            objMsg.printDblogBin(self.dut.dblData.Tables('P152_BODE_SCRN_SUM'))
            if not screenStatus and not testSwitch.virtualRun and testSwitch.BodeScreen_Fail_Enabled :
               ScrCmds.raiseException(10137, "Exceed max P152 gain threshold.")

            #MaxGain = max(self.bodeDict.values())
            #if  MaxGain > threshold and not testSwitch.virtualRun:
            #    ScrCmds.raiseException(10137, "exceed max P152 gain threshold %f" %highFreq)
            #else:
            #    objMsg.printMsg("Max Gain %4f %s Hz to %s Hz Bode Screen Passed. " %(MaxGain, str(lowFreq), str(highFreq)))
            #

         return self.bodeDict
         """
P152_BODE_GAIN_PHASE:
 HD_PHYS_PSN FREQUENCY HD_LGC_PSN    GAIN   PHASE
           0       500          0  -10.33  139.85
           0       550          0   -9.86  121.52
           0       600          0   -7.40  127.25
           0       650          0   -6.36  116.93

         """

#----------------------------------------------------------------------------------------------------------
class CResonanceRROScrn(CState):
   """
   Shock Sensor Screen at CRT2
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from Servo import CServoFunc
      self.oSrvFunc = CServoFunc()
      oFSO = CFSO()

      # Set to allow access to FAFH Zones at beginning of STATE
      if testSwitch.IS_FAFH: 
         CFSO().St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value
         CFSO().St(TP.AllowFAFH_AccessBit_178) # Allow FAFH access for servo test
         CFSO().St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value 
      
      audFreq = self.params.get("AUD_FREQ",0x1000)
      test_cyl = 0x0100
      end_cyl = min( self.dut.maxTrack) - 0x0100
      newPrm_33 = TP.pesMeasurePrm_33.copy()
      newPrm_33['spc_id'] = 10

      if self.params.get("CYL_IS_LOGICAL", 0):
         if testSwitch.UPS_PARAMETERS:
             cword1 = newPrm_33.get('Cwrd1',0)
             if type(cword1) is not int: cword1 = cword1[0]
             newPrm_33.update({'Cwrd1':  cword1 | 0x8000}) # CYL_IS_LOGICAL == TRUE.
         else:
            cword1 = newPrm_33.get('CWORD1',0)
            if type(cword1) is not int: cword1 = cword1[0]
            newPrm_33.update({'CWORD1':  cword1 | 0x8000}) # CYL_IS_LOGICAL == TRUE.
      if testSwitch.UPS_PARAMETERS:
          newPrm_33.update({
                         'CylRg': (test_cyl,end_cyl),
                         'SampCnt' : ((end_cyl - test_cyl) / audFreq),
          })
      else:
         newPrm_33.update({
                        'TEST_CYL': self.oSrvFunc.oUtility.ReturnTestCylWord(test_cyl),
                        'END_CYL' : self.oSrvFunc.oUtility.ReturnTestCylWord(end_cyl),
                        'NUM_SAMPLES' : ((end_cyl - test_cyl) / audFreq),
                        'CWORD1': (0x800A,),
                        'REPORT_OPTION': (0x8001,),
         })
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)   
      if not testSwitch.UPS_PARAMETERS:
         oFSO.St( newPrm_33 )
         newPrm_180 = TP.Resonance_RRO_Screen_180.copy()
         newPrm_180.update({'CWORD1':0xA020})
         if testSwitch.IS_2D_DRV == 1:
            newPrm_180.update({'AMPL_LIMIT':(65535, 65535, 65535, 65535, 10000, 65535, 65535),})
         oFSO.St( newPrm_180 )

      # Set to dis-allow access to FAFH Zones at end of STATE
      if testSwitch.IS_FAFH: 
         CFSO().St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value
         CFSO().St(TP.DisallowFAFH_AccessBit_178) # Dis-allow FAFH access after completing servo test
         CFSO().St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value
#----------------------------------------------------------------------------------------------------------
class CATSTuning(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from Servo import CServoOpti
      # Set to allow access to FAFH Zones at beginning of STATE
      if testSwitch.IS_FAFH: 
         CServoOpti().St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value
         CServoOpti().St(TP.AllowFAFH_AccessBit_178) # Allow FAFH access for servo test
         CServoOpti().St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value
         
      SetFailSafe()
      CServoOpti().St(TP.TuneATS_194)
      ClearFailSafe()

      # Set to dis-allow access to FAFH Zones at end of STATE
      if testSwitch.IS_FAFH: 
         CServoOpti().St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value
         CServoOpti().St(TP.DisallowFAFH_AccessBit_178) # Dis-allow FAFH access after completing servo test
         CServoOpti().St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value      