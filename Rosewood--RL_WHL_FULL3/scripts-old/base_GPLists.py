#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: base Serial Port calibration states
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_GPLists.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_GPLists.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
from State import CState
import MessageHandler as objMsg


#----------------------------------------------------------------------------------------------------------
class CClearGList(CState):
   """
   sends a level T i40,1,22 command to clear the GList

   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from serialScreen import sptDiagCmds 
      import sptCmds
      oSerial = sptDiagCmds()
      sptCmds.enableDiags()
      oSerial.clearGList()
      sptCmds.enableESLIP()


#----------------------------------------------------------------------------------------------------------
class CInitializeFlawLists(CState):
   """
      Initialize flaw lists
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from MediaScan import CUserFlaw
      self.oUserFlaw = CUserFlaw()
      
      if testSwitch.BF_0120661_357260_ENABLE_ZAP_DURING_INIT_FS:
         if testSwitch.ENABLE_T175_ZAP_CONTROL:
            self.oUserFlaw.St(TP.zapPrm_175_zapOn)
         else:
            self.oUserFlaw.St(TP.setZapOnPrm_011)

      if self.params.get('INIT_PLIST',1):
         self.oUserFlaw.initPList()

      if self.params.get('INIT_SFT',1):
         self.oUserFlaw.initSFT()

      if self.params.get('INIT_TA_LIST',1):
         if testSwitch.SINGLEPASSFLAWSCAN:
            self.oUserFlaw.initTAList()

      if self.params.get('INIT_DBI', 1):
         self.oUserFlaw.initdbi()

      if testSwitch.BF_0120661_357260_ENABLE_ZAP_DURING_INIT_FS:
         if (testSwitch.FE_0155184_345963_P_DISABLE_ZAP_OFF_AFTER_COMPLETED_ZAP) and (self.dut.zapDone != 1):
            if testSwitch.ENABLE_T175_ZAP_CONTROL:
               self.oUserFlaw.St(TP.zapPrm_175_zapOff)
            else:
               self.oUserFlaw.St(TP.setZapOffPrm_011)
               if not testSwitch.BF_0119055_231166_USE_SVO_CMD_ZAP_CTRL:
                  self.oUserFlaw.St({'test_num':178, 'prm_name':'Save SAP in RAM to FLASH', 'CWORD1':0x420})  # update SAP


#----------------------------------------------------------------------------------------------------------
class CVerifyDrive(CState):
   """
      Verify critical values are populated during MCT testing.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from Servo import CServoFunc
      from AFH import CAFH

      oSrvFunc = CServoFunc()
      oAFH = CAFH()

      ################### Set DOS ATI Threshold Settings
      if (testSwitch.DOS_THRESHOLD_BY_BG):
         oSrvFunc.St(TP.prm_setDOSATISTEThreshold_by_BG)
         if testSwitch.SMRPRODUCT:
            oSrvFunc.St(TP.prm_setDOSATISTEThreshold_by_BG_FAT)
            oSrvFunc.St(TP.prm_setDOSATISTEThreshold_by_BG_SLIM)
         oSrvFunc.St({'test_num':178, 'prm_name':'Save RAP in RAM to FLASH', 'CWORD1': 544})
         oSrvFunc.St(TP.prm_getDOSATISTEThreshold)
         if testSwitch.SMRPRODUCT and getattr(TP, 'prm_getDOSATISTEThreshold_fat', {}) != {}:
            oSrvFunc.St(TP.prm_getDOSATISTEThreshold_fat)
         if testSwitch.SMRPRODUCT and getattr(TP, 'prm_getDOSATISTEThreshold_slim', {}) != {}:
            oSrvFunc.St(TP.prm_getDOSATISTEThreshold_slim)
            
      ################### OCLIM verification
      oSrvFunc.checkOCLlimAllHds()  # This will raise a failure if any heads are over the limit
      self.dut.driveattr['OCLIM_CORRECTION'] = 0

      ################### Verify AFH Coefficients
      if not testSwitch.IN_DRIVE_AFH_COEFF_PER_HEAD_GENERATION_SUPPORT and not testSwitch.FE_HEATER_RELIEF_RECONFIG:
         oAFH.verifyIRPCoefs(TP.allowed_PTP_variance, self.dut.PREAMP_TYPE,self.dut.AABType,TP.PRE_AMP_HEATER_MODE,TP.clearance_Coefficients)

      if testSwitch.FE_0137414_357552_CHECK_SLIP_SPACE_FOR_FIELD_REFORMAT:
         #Ensure we have adequate slip space for field re-formats
         from MediaScan import CUserFlaw
         oUserFlaw = CUserFlaw()
         oUserFlaw.checkSpareSpace()

      from base_SerialTest import CCustUniqSAPCfg
      if CCustUniqSAPCfg(self.dut,{}).RVEnabled(self.dut.partNum) == 'enabled':
         oSrvFunc.St(TP.setRVFlagInCapPrm_178)
      elif CCustUniqSAPCfg(self.dut,{}).ZGSEnabled(self.dut.partNum) == 'enabled':
         oSrvFunc.St(TP.setZgsFlagInCapPrm_178)
      else:
         oSrvFunc.St(TP.resetByte227InCapPrm_178)

      # ================== Set CERT Done bit. Requested by servo group.
      oSrvFunc.setCertDoneSap(enable = True)
      # ================== Set Torn Write SAP bit =================
      if testSwitch.FE_0316568_305538_P_ENABLE_TORN_WRITE_PROTECTION:
         if not testSwitch.REDUCE_LOG_SIZE: objMsg.printMsg("Enabling Torn Write Protection...")
         if oSrvFunc.setServoSymbolData('TORN_WRITE_PROTECTION_OFFSET', 0x0001, 0x0001):
            objMsg.printMsg("Torn Write Protection enabled.")
         else:
           objMsg.printMsg("Torn Write Protection already enabled.")

      # Enable RV sensor
      if testSwitch.FE_0246017_081592_ENABLE_RV_SENSOR_IN_CERT_PROCESS:
         oSrvFunc.setSPLVFF(enable = True)

      from adaptivePrmVeri import SP_Aegis
      SP_Aegis(self.dut).run()

      # Pwr cycle
      from PowerControl import objPwrCtrl
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
