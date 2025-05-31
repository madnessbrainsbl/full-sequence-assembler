#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: SWD Tuning Module
#
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/SWD_Tuning.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/SWD_Tuning.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#

from Constants import *
from TestParamExtractor import TP
from State import CState
import ScrCmds
import SWD_Base
from PowerControl import objPwrCtrl
from FSO import CFSO
import MessageHandler as objMsg

#----------------------------------------------------------------------------------------------------------
class CSkipWriteDetectEnable(CState):
   """
   Permanently enable Skip Write Detect
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      oFSO = CFSO()
      oFSO.St(TP.enableSWDFaults_11)
      oFSO.saveSAPtoFLASH()

#----------------------------------------------------------------------------------------------------------
class CSkipWriteDetectSwitch(CState):
   """
   Enable or Disable Skip Write Detect. Default ON
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      self.mode = self.params.get('MODE', 'ON')
      oFSO = CFSO()

      if self.mode == 'OFF':
         oFSO.St(TP.disableSWDFaults_11)
      else:
         oFSO.St(TP.enableSWDFaults_11)

      oFSO.saveSAPtoFLASH()


#----------------------------------------------------------------------------------------------------------
class CSkipWriteDetectAdjustment(CState):
   """
   Adjust or verify the clearance profile in all zones based on the state parameter MODE which has valid
      values of 'ADJUST' for clearance adjusment or 'VERIFY' for clearance verfication and failure.
      *Default mode is ADJUST
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      import SWD_Base
      from AFH import CdPES
      from PreAmp import CPreAmp
      
      mSWD = SWD_Base.CSkipWriteDetect(TP.masterHeatPrm_11, TP.defaultOCLIM)
      oPreamp = CPreAmp()
      oFSO = CFSO()
      oFSO.getZoneTable()

      odPES  = CdPES(TP.masterHeatPrm_11, TP.defaultOCLIM)

      odPES.setMasterHeat(TP.masterHeatPrm_11, setMHeatOn = 1) #enable master heat
      coefs = odPES.getClrCoeff(TP.clearance_Coefficients, self.dut.PREAMP_TYPE, self.dut.AABType)

      if getattr(TP, 'Test_Flags', {}).get("T_227",None) == 0:
         objMsg.printMsg("T227 DISABLED")
         return
      objMsg.printMsg("T_227 ENABLED")
      if self.params.get('MODE','ADJUST') == 'ADJUST':

         mSWD.St(TP.enableAGCUnsafes_11)

         if testSwitch.FE_0169232_341036_ENABLE_AFH_TGT_CLR_CANON_PARAMS == 1:
            from AFH_canonParams import *
            afhZoneTargets = getTargetClearance()
         else:
            afhZoneTargets = TP.afhZoneTargets

         vbarZoneAdjustments,swdAdjustReq = mSWD.SWD_AdjustFlyHeight(TP.SkipWriteDetectorAdjustment_227, \
            coefs, TP.PRE_AMP_HEATER_MODE, \
            afhZoneTargets)

         mSWD.St(TP.disableAGCUnsafes_11)

         if swdAdjustReq:

            test49_CWORD1_EQUALS_6 = {
               # call setHeatersInRAPBasedOnPassiveClearanceInRAP() in test 049.
              'test_num':  49,
              'prm_name':  'setHeatersInRAP',
              "CWORD1" :   (0x0006,),
            }

            # add test 49 CWORD1=6 call.
            mSWD.St(test49_CWORD1_EQUALS_6)
            mSWD.St({'test_num': 172, 'prm_name':'displayClearanceTable', 'timeout':1200, 'spc_id': -9, 'CWORD1':5,})
            mSWD.St({'test_num': 172, 'prm_name':'P172_AFH_WORKING_ADAPTS', 'timeout':1200, 'spc_id': -9, 'CWORD1':4,})
            oFSO.saveRAPtoFLASH()
            objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
            mSWD.St({'test_num': 172, 'prm_name':'displayClearanceTable', 'timeout':1200, 'spc_id': 317, 'CWORD1':5,})
            mSWD.St({'test_num': 172, 'prm_name':'P172_AFH_WORKING_ADAPTS', 'timeout':1200, 'spc_id': 317, 'CWORD1':4,})

         oFSO.saveRAPtoFLASH()

         mSWD.printAdjustedVBARZones(vbarZoneAdjustments)
         mSWD.createSWDAdjustTable()
      elif self.params.get('MODE','') == "VERIFY":
         #Use test 227 to evaluate the current clearance profile and pass/fail the drive
         if testSwitch.FE_0161719_470833_P_ADD_PWC_RETRY_TO_SWD_TEST_227:
            #Added power cycle to beginning of test, and a retry if EC10469 occurs
            retries = 1
            while 1:
               try:
                  objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1) #perform power cycle before this test
                  mSWD.St(TP.enableAGCUnsafes_11)
                  mSWD.St(TP.SkipWriteDetectorVerification_227)
                  mSWD.St(TP.disableAGCUnsafes_11)
                  break #passed with no error code
               except ScriptTestFailure, (failureData): #catch EC10469, retry if it occurs
                  if failureData[0][2] in [10469] and retries > 0:
                     objMsg.printMsg("EC:10469 - Retrying T227. Num Retries left %d \n" % retries)
                     retries -= 1
                  else: #not EC10469 or no retries remaining
                     raise
               except:
                  raise
         else:
            try:
               mSWD.St(TP.enableAGCUnsafes_11)

               mSWD.St(TP.SkipWriteDetectorVerification_227)

               mSWD.St(TP.disableAGCUnsafes_11)
            except:
               raise
      if self.dut.nextOper == "FNC2":
         DriveAttributes["TEST_BLOCK"] = "2"


#----------------------------------------------------------------------------------------------------------
class CDualHeater_SWDAdjust(CState):
   """
   Call Test 227 to possibly adjust the pre-heat clearance and the write heat clearance based on test 227 SWD results.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if not (testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT == 1):
         ScrCmds.raiseException(11044, "DH SWD state called with non-DH code support.")

      oFSO = CFSO()
      import SWD_Base
      from AFH import CdPES
      mSWD = SWD_Base.CSkipWriteDetect(TP.masterHeatPrm_11, TP.defaultOCLIM)
      oFSO.getZoneTable()

      
      odPES  = CdPES(TP.masterHeatPrm_11, TP.defaultOCLIM)
      odPES.setMasterHeat(TP.masterHeatPrm_11, setMHeatOn = 1) #enable master heat

      coefs = odPES.getClrCoeff(TP.clearance_Coefficients, self.dut.PREAMP_TYPE, self.dut.AABType)

      mSWD.St(TP.enableAGCUnsafes_11)
      mSWD.call_SWD_T227_toAdjustFlyHeight_DH(TP.SkipWriteDetectorAdjustment_227)
      mSWD.St(TP.disableAGCUnsafes_11)

      mSWD.St({'test_num': 172, 'prm_name':'displayClearanceTable', 'timeout':1200, 'spc_id': -9, 'CWORD1':5,})
      mSWD.St({'test_num': 172, 'prm_name':'P172_AFH_WORKING_ADAPTS', 'timeout':1200, 'spc_id': -9, 'CWORD1':4,})
      oFSO.saveRAPtoFLASH()
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      mSWD.St({'test_num': 172, 'prm_name':'displayClearanceTable', 'timeout':1200, 'spc_id': 317, 'CWORD1':5,})
      mSWD.St({'test_num': 172, 'prm_name':'P172_AFH_WORKING_ADAPTS', 'timeout':1200, 'spc_id': 317, 'CWORD1':4,})


#----------------------------------------------------------------------------------------------------------
class CDualHeaterSWDVerify(CState):
   """
       SWD Verify State for DH.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if not (testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT == 1):
         ScrCmds.raiseException(11044, "DH SWD state called with non-DH code support.")

      if testSwitch.FE_0159624_220554_P_POWER_CYCLE_AT_BEGINNING_OF_SWDVERIFY:
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1) ## mlw added ##
      from AFH import CdPES
      odPES  = CdPES(TP.masterHeatPrm_11, TP.defaultOCLIM)
      odPES.setMasterHeat(TP.masterHeatPrm_11, setMHeatOn = 1) #enable master heat

      #Use test 227 to evaluate the current clearance profile and pass/fail the drive
      odPES.St(TP.enableAGCUnsafes_11)

      odPES.St(TP.SkipWriteDetectorVerification_227)

      odPES.St(TP.disableAGCUnsafes_11)


#----------------------------------------------------------------------------------------------------------
class CSetSWD_AGCUnsafes(CState):
   """
   Class that will use T11 to turn on/off SWD thru AGCUnSafes
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from Process import CProcess
      oProc = CProcess()

      # Enable - Disable SWD
      mode = self.params.get('MODE', 'ON')
      if mode == 'ON':
         oProc.St(TP.enableAGCUnsafes_11)
      elif mode == 'OFF':
         oProc.St(TP.disableAGCUnsafes_11)
