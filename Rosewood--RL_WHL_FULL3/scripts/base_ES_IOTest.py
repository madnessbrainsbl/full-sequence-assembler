#-------------------------------------------------------------------------------
# Property of Seagate Technology, Copyright 2010, All rights reserved
#-------------------------------------------------------------------------------
# Description: ES IO Tests
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_ES_IOTest.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_ES_IOTest.py#1 $
# Level: 2
#-------------------------------------------------------------------------------

from Constants import *
from TestParamExtractor import TP
from State import CState
from PowerControl import objPwrCtrl
import MessageHandler as objMsg
from Process import CProcess
from ICmdFactory import ICmd
import serialScreen, sptCmds


###########################################################################################################
class CPerformance(CState):
   def __init__(self, dut, params=[]):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):

      if testSwitch.FE_0140980_231166_P_SUPPORT_TAG_Q_SI_0_QD:
         oProc = ICmd
      else:
         oProc = CProcess()

      TraceMessage("Performance Test")
      objPwrCtrl.powerCycle(5000,12000,10,30) #Drive Power Saving

      if testSwitch.FE_0144926_426568_P_DIAG_DISABLE_BGMS_IN_PERFORMANCE:
         oSerial = serialScreen.sptDiagCmds()
         sptCmds.enableDiags()
         if oSerial.BGMS_EnabledInCode():
            oSerial.changeAMPS("BGMS_ENABLE", 0, mask = 1)
            oSerial.changeAMPS("BGMS_PRESCAN", 0, mask = 1)
            sptCmds.enableESLIP()
      elif testSwitch.FE_0144660_426568_DISABLE_BGMS_IN_PERFORMANCE:
         if testSwitch.FE_0148237_357552_P_ADD_HP_SPECIFIC_BGMS_DISABLE:
            ICmd.disableBGMS()
         else:
            oProc.St(TP.prm_518_Disable_PrescanBGMS)

      if testSwitch.BF_0130425_357466_FIX_T597_DOS_VER:
         oProc.St(TP.prm_518_WCE_1_RCD_0)
         oProc.St(TP.prm_597_RdmWrt, IOPS_LOWER_LIM=0, QUEUE_DEPT=1, spc_id=1)
         oProc.St(TP.prm_518_WCE_0_RCD_0)
         oProc.St(TP.prm_597_RdmWrt, IOPS_LOWER_LIM=0, QUEUE_DEPT=1, spc_id=3)
         oProc.St(TP.prm_597_RdmRd, IOPS_LOWER_LIM=0, QUEUE_DEPT=1, spc_id=8)
         if testSwitch.FE_0175785_357360_EXTRA_597_IOPS_TESTING:
            import PIF
            from Utility import CUtility
            if hasattr(PIF,'t597WriteOverrides') and PIF.t597WriteOverrides.has_key(self.dut.partNum):
               writeParams = CUtility.copy(TP.prm_597_RdmWrt)
               writeParams.update(PIF.t597WriteOverrides[self.dut.partNum])
               oProc.St(writeParams)
            if hasattr(PIF,'t597ReadOverrides') and PIF.t597ReadOverrides.has_key(self.dut.partNum):
               readParams = CUtility.copy(TP.prm_597_RdmRd)
               readParams.update(PIF.t597ReadOverrides[self.dut.partNum])
               oProc.St(readParams)
      else:
         SetFailSafe()  # MLW dont want it to fail for now
         result = ICmd.SetFeatures(0x02)['LLRET']  ###### MLW enable write cache ########
         oProc.St(TP.prm_597_RdmWrt, IOPS_LOWER_LIM=0, CTRL_WORD1 = 0x11, spc_id=1)
         #oProc.St(TP.prm_518_WCE_0_RCD_0)
         oProc.St({'test_num':508}, CTRL_WORD1 = 0, PATTERN_TYPE = 1)
         oProc.St(TP.T508_2)         # read and display write buffer
         ######  oProc.St(TP.prm_597_RdmWrt,IOPS_LOWER_LIM=0,CTRL_WORD1 = 0x11,spc_id=2)
         result = ICmd.SetFeatures(0x82,0x00)      ###### MLW disable write cache ########
         oProc.St(TP.prm_597_RdmWrt, IOPS_LOWER_LIM=0, CTRL_WORD1 = 0x11, spc_id=3)
         oProc.St({'test_num':508}, CTRL_WORD1 = 0, PATTERN_TYPE = 1)
         oProc.St(TP.T508_2)         # read and display write buffer
         ######  oProc.St(TP.prm_597_RdmWrt,IOPS_LOWER_LIM=0,CTRL_WORD1 = 0x11,spc_id=4)
         ######  oProc.St(TP.prm_597_RdmWrt,IOPS_LOWER_LIM=0,CTRL_WORD1 = 0x11,spc_id=5)
         ######  oProc.St(TP.prm_597_RdmRd,IOPS_LOWER_LIM=0,CTRL_WORD1 = 0x22,spc_id=6)
         ######  oProc.St(TP.prm_597_RdmRd,IOPS_LOWER_LIM=0,CTRL_WORD1 = 0x22,spc_id=7)
         oProc.St(TP.prm_597_RdmRd, IOPS_LOWER_LIM=0, CTRL_WORD1 = 0x21, spc_id=8)
         ######  oProc.St(TP.prm_597_RdmRd,IOPS_LOWER_LIM=0,CTRL_WORD1 = 0x22,spc_id=9)
         ClearFailSafe()  # MLW dont want to fail for now, clearing...

      #oProc.St(TP.prm_518_WCE_0_RCD_0)
      #oProc.St(TP.prm_518_Disable_AWRE)
      ############ mlw new section ###################
      if testSwitch.FE_0132880_7955_CREATE_P597_SPEC_LIMIT_TABLE and not testSwitch.virtualRun:
         """
         for use in GOTF, check NUM_FAIL_COLS

         """

         P597_TABLE = self.dut.dblData.Tables('P597_ADV_TAG_Q').tableDataObj()

         curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)

         col_fail_cnt = 0

         if self.dut.imaxHead < 8:  # it's a 2 disk
            wce_spec = self.params.get('2DSK_WCE_SPEC',  0)
            wcd_spec = self.params.get('2DSK_WCD_SPEC',  0)
            read_spec = self.params.get('2DSK_READ_SPEC',  0)
         else: # it's a 4 disk
            wce_spec = self.params.get('4DSK_WCE_SPEC',  0)
            wcd_spec = self.params.get('4DSK_WCD_SPEC',  0)
            read_spec = self.params.get('4DSK_READ_SPEC',  0)

         wce_fail = 0
         wcd_fail = 0
         read_fail = 0
         wce = 99999
         wcd = 99999
         read = 99999

         for record in range(len(P597_TABLE)): #maybe typecast values into int

            if int(P597_TABLE[record]['SPC_ID']) == 1:
               wce = int(P597_TABLE[record]['IOPS'])      # wrt cache enable
               if wce < wce_spec:
                  wce_fail = 1
            elif int(P597_TABLE[record]['SPC_ID']) == 3:
               wcd = int(P597_TABLE[record]['IOPS'])      # wrt cache disable
               if wcd < wcd_spec:
                  wcd_fail = 1
            elif int(P597_TABLE[record]['SPC_ID']) == 8:
               read = int(P597_TABLE[record]['IOPS'])     # read
               if read < read_spec:
                  read_fail = 1

            col_fail_cnt = wce_fail + wcd_fail + read_fail

            self.dut.dblData.Tables('P597_SPEC_LIMIT').addRecord(
               {
                  'SPC_ID': -1,
                  'OCCURRENCE' : occurrence,
                  'SEQ' : curSeq,
                  'TEST_SEQ_EVENT' : testSeqEvent,
                  'WCE_SPEC': wce_spec,
                  'WCE' : wce,
                  'WCD_SPEC': wcd_spec,
                  'WCD' : wcd,
                  'READ_SPEC' : read_spec,
                  'READ' : read,
                  'NUM_FAIL_COLS': col_fail_cnt,
               })
         objMsg.printDblogBin(self.dut.dblData.Tables('P597_SPEC_LIMIT'))
      if testSwitch.FE_0144926_426568_P_DIAG_DISABLE_BGMS_IN_PERFORMANCE:
         from base_IntfTest import CResetAMPS
         ResetAmps = CResetAMPS(dut =self.dut, params = {})
         ResetAmps.run()
         del ResetAmps
      objPwrCtrl.powerCycle(5000,12000,10,30) #Drive Power Saving


###########################################################################################################
class HPMeatGrinderScreen(CState):

   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      oProc = CProcess()
      objPwrCtrl.powerCycle(5000,12000,10,30)
      ICmd.HardReset()

      oProc.St({'test_num':535},0)
      oProc.St({'test_num':533}, CTRL_WORD1 = 0x0001)              #  RESET
      oProc.St({'test_num':514}, CTRL_WORD1 = 1)

      SetFailSafe()  # MLW dont want it to fail for now
      try:

         oProc.St(TP.T508_0000FFFF)  # Write pattern to the write buffer - fixed pattern 0000FFFF
         oProc.St(TP.T508_2)         # read and display write buffer
         #res = ICmd.ReceiveSerialCtrl(1)
         #result = ICmd.SetFeatures(0x82,0x00)         ###### MLW disable write cache ########
         #if result['LLRET'] == OK:
         #   objMsg.printMsg("Write Cache disabled")
         #else:
         #   objMsg.printMsg("Warning : Disable Write Cache Failed")
         #res = ICmd.ReceiveSerialCtrl(0,100)
         #objMsg.printMsg("Buffer data received from Disable Write Cache : \n\n %s"%res)
         oProc.St({'test_num':597}, spc_id = 1, timeout = 90000,  RANDOM_SEED = 620, MAXIMUM_LBA = (0, 0, 0, 0), MINIMUM_LBA = (0, 0, 0, 0),MIN_SECTOR_COUNT = 1, MAX_SECTOR_COUNT = 1, LOOP_COUNT = 0x4000, CTRL_WORD1 = 0x11, CTRL_WORD2 = 0)
         oProc.St({'test_num':508}, CTRL_WORD1 = 0, PATTERN_TYPE = 1)
         oProc.St(TP.T508_2)         # read and display write buffer
         oProc.St({'test_num':597}, spc_id = 2, timeout = 90000,  RANDOM_SEED = 620, MAXIMUM_LBA = (0, 0, 0, 0), MINIMUM_LBA = (0, 0, 0, 0),MIN_SECTOR_COUNT = 1, MAX_SECTOR_COUNT = 1, LOOP_COUNT = 0x4000, CTRL_WORD1 = 0x21, CTRL_WORD2 = 0)
         oProc.St(TP.T508_0000FFFF)  # Write pattern to the write buffer - fixed pattern 0000FFFF
         oProc.St(TP.T508_2)         # read and display write buffer
         oProc.St({'test_num':597}, spc_id = 3, timeout = 90000,  RANDOM_SEED = 620, MAXIMUM_LBA = (0, 0, 0, 0), MINIMUM_LBA = (0, 0, 0, 0),MIN_SECTOR_COUNT = 1, MAX_SECTOR_COUNT = 1, LOOP_COUNT = 0x4000, CTRL_WORD1 = 0x31, CTRL_WORD2 = 0)

      except:
         oProc.St({'test_num':504}, timeout = 3600)

      ClearFailSafe()  # MLW dont want to fail for now, clearing...

###########################################################################################################
class CSAS_Regrade(CState):
   """
   Class that re-grades sas drives
   1. download TGTP
   2. pull and regrade
   3. download TGTA
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from base_IntfTest import CDnlduCode
      from base_GOTF import CDblFile


      objPwrCtrl.powerCycle(5000,12000,10,30, ataReadyCheck = True) #Drive Power Saving
      #Download TGTP with diags
      dnldCls = CDnlduCode(dut =self.dut, params = {'CODES': ['TGT','OVL']})
      dnldCls.run()
      del dnldCls

      objPwrCtrl.powerCycle(5000,12000,10,30, ataReadyCheck = False) #Drive Power Saving

      #pull the file from system area for re-grade post state transition
      odblFile = CDblFile()
      odblFile.readGOTFdblFile(self.dut.dblData)

      objPwrCtrl.powerCycle(5000,12000,10,30, ataReadyCheck = False) #Drive Power Saving
      objPwrCtrl.powerCycle(5000,12000,10,30, ataReadyCheck = True) #Drive Power Saving


      #Download customer code again
      dnldCls = CDnlduCode(dut =self.dut, params = {'CODES': ['TGT2','OVL2',]})
      dnldCls.run()
      del dnldCls

###########################################################################################################
class CMeasureTTR(CState):
   """
   Measures TTR and updates attr
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      oProc = CProcess()
      ICmd.ClearSense()
      readyTimeLimit = objPwrCtrl.readyTimeLimit

      if testSwitch.BF_0142781_231166_P_FIX_SAS_TTR_PARAMETERS_FOR_START_STOP:
         prmSpinup = {
                  'test_num': 528,
                  'prm_name': "Measure TTR",
                  'timeout':600,
                  'spc_id':1,
                  'TEST_OPERATING_MODE' : (1,),  # 0=Power Cycle, 1=Start/Stop Unit Command

                  'ALLOW_SPEC_STATUS_COND' : (0x0000,),
                  'UNIT_READY' : 1, #0 wait for unit ready at beginning of test
                  'SPIN_DOWN_WAIT_TIME' : getattr(objPwrCtrl,  'offTime',  30),
                  #'DELAY_TIME':
                  'TEST_FUNCTION' : (0x0000,),

                  'SENSE_DATA_3' : (0x0000,0x0000,0x0000,0x0000,),
                  'SENSE_DATA_2' : (0x0000,0x0000,0x0000,0x0000,),
                  'SENSE_DATA_1' : (0x0000,0x0000,0x0000,0x0000,),

                  'SKP_SPINUP_AFTER_SPINDWN' : (0x0000,), # 0 = don't skip spinup after spindown
                  'MIN_POWER_SPIN_DOWN_TIME' : 0,
                  'MIN_POWER_SPIN_UP_TIME' : 2,
                  'MAX_POWER_SPIN_DOWN_TIME' : 30,
                  'MAX_POWER_SPIN_UP_TIME' : int(readyTimeLimit/1000.0),
                  'DblTablesToParse': ['P528_SPINUPDOWN','P528_TIMED_PWRUP']
                  }
         spinupTTR_Prm = getattr(TP, 'spinupTTR_Prm', prmSpinup)

         oProc.St(prmSpinup)

         if testSwitch.virtualRun:
            ttrVal = 5.00
         else:
            if 'P528_TIMED_PWRUP' in self.dut.objSeq.SuprsDblObject:
               ttrVal = float(self.dut.objSeq.SuprsDblObject['P528_TIMED_PWRUP'][-1]['POWERUP_TIME'])
            else:
               ttrVal = float(self.dut.objSeq.SuprsDblObject['P528_SPINUPDOWN'][-1]['SPINUP_TIME'])

         objPwrCtrl.logPowerOn_Information( int(round(ttrVal*1000, 0)),  0, {'ERR':0,'STS':80})
      else:
         oProc.St(
            {     'test_num': 528,
                  'prm_name': "Measure TTR",
                  'timeout':600,
                  'spc_id':1,
                  'TEST_OPERATING_MODE' : (0,),  # 0=Power Cycle, 1=Start/Stop Unit Command
                  'ALLOW_SPEC_STATUS_COND' : (0x0000,),
                  'UNIT_READY' : (0x0000,), #0 wait for unit ready at beginning of test
                  'SPIN_DOWN_WAIT_TIME' : getattr(objPwrCtrl,  'offTime',  30),
                  'MIN_POWER_SPIN_UP_TIME' : (2,),
                  'TEST_FUNCTION' : (0x0000,),
                  'SENSE_DATA_3' : (0x0000,0x0000,0x0000,0x0000,),
                  'SENSE_DATA_1' : (0x0000,0x0000,0x0000,0x0000,),
                  'SKP_SPINUP_AFTER_SPINDWN' : (0x0000,),
                  'MIN_POWER_SPIN_DOWN_TIME' : (10,),
                  'SENSE_DATA_2' : (0x0000,0x0000,0x0000,0x0000,),
                  'MAX_POWER_SPIN_DOWN_TIME' : 30,
                  'MAX_POWER_SPIN_UP_TIME' : int(readyTimeLimit/1000.0),
                  }
            )
         self.dut.driveattr["TIME_TO_READY"] = float(self.dut.dblData.Tables('P528_TIMED_PWRUP').tableDataObj()[-1]['POWERUP_TIME'])


