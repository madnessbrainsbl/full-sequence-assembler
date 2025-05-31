#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: GIO Tests
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/GIO.py $
# $Revision: #12 $
# $DateTime: 2016/12/19 20:01:56 $
# $Author: yihua.jiang $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/GIO.py#12 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
# Rev:1 
# - Initial release based on GIO_CST_18CVM.
# Rev:2
# - Sync up with GIO package GIO_CST_UNF21D.
# - SDOD Test (Added Z command before "U5" - Spin Down Drive First).
# - FullPack Zero Compare to First and Last 10GB of the Drive.
# - Change ShortDST timeout to 150 sec. 
# - Minor change in WR_RD_PERFORM algo to avoid Batch File Loss.
# Rev:3
# - Batch File Optimization to resolve "RW-Command Failure" due to Data Loss.
# - Temp Ramp Support.
# - SMART log support (But Turned-OFF).
# Rev:4 (21-Oct-2011)
# - BugFix: Added PowerCycle at the beginning of FullDST. 
# Rev:5 (25-Oct-2011)
# - Turn ON SMART features.
# Rev:6 (26-Oct-2011)
# - Bug Fix in SMART algo.
# - Attr#5 need to take only Last 2 Bytes. 
# Rev:7 (04-Nov-2011)
# - Optimize ENCROACHMENT_EUP & DELAY_WRT tests to avoid CM loading.
# - Enhance FailCode reporting. 
# Rev:8 (11-Nov-2011)
# - Enhance FailCode reporting. 
# Rev:9 (18-Nov-2011)
# - Reset Congen for SMART DST failure drives. 
# Rev:10 (13-Dec-2011)
# - Sync up with GIO package GIO_CST_UNF22B2. 
# ...DriveOff before Temperature Ramp up.
# ...Turn On SMART check for all modules.
# Rev:11 (13-Dec-2011)
# - Sync up with MQM package flow MQM_UNF22B2. 
# Rev:12 (28-Dec-2011)
# - Sync up with MQM package flow MQM_UNF21D2_2.
# ...Added LongDST after Write_Drive_Zero module.
# Rev:13 (04-Jan-2012)
# - Added getSerialPortData debug function from IO MQM.
#   Debug Information Contains:
#    - 'DOT', '~', 'CTRL_E', 'CTRL_X', 'CTRL_B'  online command
#    - 'T> V4, V800' command
#    - '4> s, g' command
#    - '1> N5, N8, N18' command
#    - Display SMART logs and Attribute 
#---------------------------------------------------------------------------------------------------------#
 
from Constants import *
from State import CState
import MessageHandler as objMsg
import ScrCmds
import re, struct, traceback, time, random, binascii, types

from TestParamExtractor import TP
from Test_Switches import testSwitch
from SATA_SetFeatures import *
from PowerControl import objPwrCtrl
from Drive import objDut
import serialScreen, sptCmds
from SerialCls import baseComm
from ReliSmart import CSmartAttributes
from CTMX import CTMX
from SPT_ICmd import ICmd
from Exceptions import CRaiseException

PASS_RETURN = {'LLRET':OK}
FAIL_RETURN = {'LLRET':NOT_OK}
OK = 0
FAIL = -1
ON = 1
OFF = 0
UNDEF = 'UNDEF'
###########################################################################################################
###########################################################################################################
class CGIO(CState):
   """
      Provide a single call to run GIO tests. 
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      self.IDT_RAMP_TEMP = 'OFF'
      self.doCEDump = 'YES'
      self.TestMode = "MQM"
      CState.__init__(self, dut, depList)
      self.oSerial = serialScreen.sptDiagCmds()

   #---------------------------------------------------------------------------------------------------------#
   def powerCycle(self, pwrOption = "pwrCtrlZOnly"):
      if pwrOption == "pwrDefault":
         self.pwrDefault()
      elif pwrOption == "pwrCtrlZOnly":
         self.pwrCtrlZOnly()
      elif pwrOption == "pwrDriveOnly":
         DriveOff(pauseTime=5)
         DriveOn(pauseTime=5)
         self.pwrCtrlZOnly()

      if testSwitch.FE_0246520_356922_SPMQM_Y2_RETRY:
         self.Y2Retry()

   #---------------------------------------------------------------------------------------------------------#
   def Y2Retry(self):
      for i in xrange(3):
         try:
            sptCmds.gotoLevel('F')
            sptCmds.sendDiagCmd("/F", printResult = True)   # for AngsanaH, must ensure Level F is reached first. Otherwise, FlashLED
            sptCmds.sendDiagCmd("/FY2,,,,10000000018", printResult = True)
            return
         except:
            objMsg.printMsg("Error In SPMQM Y2: %s" % (traceback.format_exc(),))
            sptCmds.enableDiags(retries = 2)

      ScrCmds.raiseException(11044, "Setting Y2 Retry failed")

   #---------------------------------------------------------------------------------------------------------#
   def Y2TighterRetry(self):
      for i in xrange(3):
         try:
            sptCmds.gotoLevel('F')
            sptCmds.sendDiagCmd("/F", printResult = True)   # for AngsanaH, must ensure Level F is reached first. Otherwise, FlashLED
            sptCmds.sendDiagCmd("/FY2,,3,,10000000018", printResult = True)
            return
         except:
            objMsg.printMsg("Error In SPMQM Y2Tighter retry: %s" % (traceback.format_exc(),))
            sptCmds.enableDiags(retries = 2)

      ScrCmds.raiseException(11044, "Setting Y2Tighter Retry failed")

   #---------------------------------------------------------------------------------------------------------#
   def pwrDefault(self):
      objPwrCtrl.powerCycle(5000,12000,10,10,baudRate=Baud38400,ataReadyCheck=False)
      self.oSerial.enableDiags(retries = 2)
      ICmd.ClearBinBuff()
      ICmd.FillBuffer(1,0,'0000')
      sptCmds.gotoLevel('T')

   #---------------------------------------------------------------------------------------------------------#
   def pwrCtrlZOnly(self):
      try:
         try:
            baseComm.flush()
            accumulator = baseComm.PChar(CTRL_Z)
            promptStatus = sptCmds.promptRead(5, accumulator = accumulator)
         except:
            time.sleep(5)
            baseComm.flush()
            accumulator = baseComm.PChar(CTRL_Z)
            promptStatus = sptCmds.promptRead(5, accumulator = accumulator)
      except:
         objMsg.printMsg("Doing full power cycle. Error in CTRL_Z: %s" % traceback.format_exc())
         self.pwrDefault()

   #-------------------------------------------------------------------------------------------------------
   def run(self):     

      objMsg.printMsg('SPMQM start time')
      self.real_start = time.time()

      spmqm_enable = (int(ConfigVars[ConfigId[2]].get('SPMQM_ENABLE',0)) and self.dut.AABType not in ['501.42']) or \
                     (int(ConfigVars[ConfigId[2]].get('LCT_SPMQM_ENABLE',0)) and self.dut.AABType in ['501.42'])
      objMsg.printMsg('ConfigVars SPMQM_ENABLE=%s' % spmqm_enable)
      if spmqm_enable == 0:
         return

      self.scriptInfo = \
      {
         'IDT Script Rev'           : 'SP MQM Unified 2.1d2_9v',
         'IDT SW Date'              : '2013.04.30',
      }

      #objMsg.printMsg('*** SP MQM Script Rev=%s Dated[%s]' % (self.scriptInfo['IDT Script Rev'], self.scriptInfo['IDT SW Date']))
      #self.dut.driveattr['SPMQM_SCRIPT_REV'] = self.scriptInfo['IDT Script Rev']
     
      objMsg.printMsg("SPMQM Version = %s" % TP.prm_GIOVersion['GIOVer'])
      self.dut.driveattr['SPMQM_SCRIPT_REV'] = TP.prm_GIOVersion['GIOVer']

      #Start GIO tests
      CInit_Testing(self.dut, params={}).run()
      
      Modules = [ ('IDT_RAMP_TEMP'              , 'ON'), 
                  ('IDT_WRT_RD_PERFORM'         , 'ON'),
                  ('IDT_VERIFY_SMART_IDE'       , 'ON'), 
                  ('IDT_WRITE_TEST_MOBILE'      , 'ON'),
                  ('IDT_IMAGE_FILE_COPY'        , 'ON'),
                  ('IDT_IMAGE_FILE_READ'        , 'ON'),
                  ('IDT_SHORT_DST_IDE'          , 'ON'),
                  ('IDT_READ_TEST_DRIVE'        , 'ON'),
                  ('IDT_LOW_DUTY_CYCLE'         , 'ON'),
                  ('IDT_OS_WRITE_TEST'          , 'ON'),
                  ('IDT_VERIFY_SMART_ONLY'      , 'ON'),                   
                  ('IDT_GET_SMART_LOGS'         , 'ON'),
                  ('IDT_OS_READ_COMPARE'        , 'ON'),
                  ('IDT_OS_READ_REVERSE'        , 'ON'),
                  ('IDT_WRITE_PATTERN'          , 'ON'),
                  ('IDT_READ_PATTERN_FORWARD'   , 'ON'),
                  ('IDT_ODTATI_TEST'            , 'ON'),
                  ('IDT_VOLTAGE_HIGH_LOW'       , 'ON'),
                  ('IDT_RANDOM_WRITE_TEST'      , 'ON'),
                  ('IDT_FULL_DST_IDE'           , 'ON'),
                  ('IDT_GET_SMART_LOGS'         , 'ON'),
                  ('IDT_DELAY_WRT'              , 'ON'),
                  ('IDT_MS_SUS_TXFER_RATE'      , 'ON'),
                  ('IDT_PM_ZONETHRUPUT'         , 'ON'),
                  ('IDT_ENCROACHMENT_EUP'       , 'ON'),
                  ('IDT_SERIAL_SDOD_TEST'       , 'ON'),
                  ('IDT_WRITE_DRIVE_ZERO'       , 'ON'),
                  ('IDT_READ_ZERO_COMPARE'      , 'ON'),
                  ('IDT_GET_SMART_LOGS'         , 'ON')]

      GIO_Modules = getattr(TP,"prm_GIOModules",Modules)
      self.doCEDump = ConfigVars[CN].get('CE_DUMP','YES')  #default it to dump, override it in config to switch off

      self.AmbTemp = TP.prm_GIOSettings['IDT Ambient Temp']
      self.HotTemp = TP.prm_GIOSettings['IDT Hot Temp']      
      self.oTemp = CRampTemp(self.dut, params={})
      try:
         self.RunModules(GIO_Modules)
      finally:
         self.elapsed_time = time.time() - self.real_start
         objMsg.printMsg('SPMQM elapsed time = %0.2f' % (self.elapsed_time))
         self.dut.driveattr['SPMQM_TIME'] = '%0.2f' % (self.elapsed_time)

   def needG2P(self):
      try:
         self.oSerial.enableDiags(retries = 2)
         if self.oSerial.dumpReassignedSectorList()['NUMBER_OF_TOTALALTS'] > 0:
            self.oSerial.sendDiagCmd('m0,6,3,,,,,22', timeout = 10*60, printResult = True)
            return True
         else:
            return False
      except:
         return False
   #-------------------------------------------------------------------------------------------------------
   def RunModules(self, GIO_Modules):

      self.skip_nxt_module = False
      ModCounter = 0
      spmqm_plr = self.dut.objData.get('spmqm_plr', 0)
      if spmqm_plr:
         objMsg.printMsg('Power Loss Recovery detected=%d' % spmqm_plr)
                                                
      for items in iter(GIO_Modules):
         module = items[0]
         status = items[1]
         module_pass = True
        
         if status == 'OFF': 
            continue

         if self.skip_nxt_module:
            objMsg.printMsg("Skipping %s module" % (module,))
            self.skip_nxt_module = False
            continue
         op_dict = {}
         if len(items) >= 3 and type(items[2]) == types.DictType:
            op_dict = items[2]
            objMsg.printMsg('SPMQM op_dict=%s' % op_dict)
            
         ##########################################################################
         self.dut.ctmxState.IsCustCfg = True
         ctmx = CTMX('STATE', module[3:])
         ##########################################################################

         if int(op_dict.get('DISABLE_CELL','0')):
            objMsg.printMsg('SPMQM DisableCell')
            RequestService('DisableCell')
         try:
            NumRetry = min(int(op_dict.get('NUM_RETRY','0')), 5)
            for i in xrange(NumRetry + 1):
               self.dut.RetryCnt = i
               try:
                  if (ModCounter < spmqm_plr) and not (testSwitch.FE_0296361_402984_DEFECT_LIST_TRACKING_FROM_CRT2 and module is "IDT_FULL_DST_IDE"):
                     objMsg.printMsg('PLR skipping=%s' % module)
                  else:
                     self.dut.SubNextState = op_dict.get('OPS_CAUSE',module)  # Loke
                     if module == 'IDT_FULL_DST_IDE':
                        CShortScreen(self.dut).run()
                     self.TestModules(module, status)
                  ModCounter += 1
                  self.dut.objData.update({'spmqm_plr': ModCounter})
                  break

               except CRaiseException, (failureData):
                  objMsg.printMsg("Count: %s Failed SPMQM %s: %s" % (i, module, traceback.format_exc()))
                  if i < NumRetry:
                     objMsg.printMsg("Retrying SPMQM %s" % module)
                     self.powerCycle(pwrOption = "pwrDefault")
                     if failureData[0][2] == 10569:  # If OpShock event, do full pack write before retrying
                        CWriteDriveZero(self.dut, params={}).doWriteZeroPatt('MQM', 'MaxLBA')
                     # Workaround for EDAC issue. Pending new F3 code to fix this problem
                     if self.dut.BG in ['SBS'] and failureData[0][2] == 13069:  # If OpShock event, do full pack write before retrying
                        if self.needG2P():
                           try:
                              CWriteDriveZero(self.dut, params={}).doWriteZeroPatt('MQM', 'MaxLBA')
                           except:
                              module_pass = False
                              raise failureData
                        else:
                           module_pass = False
                           raise failureData
                     continue

                  spmqm_ec = op_dict.get('SPMQM_EC', '')
                  if len(spmqm_ec) == 5 and str(spmqm_ec).isdigit():
                     self.dut.driveattr['SPMQM_EC'] = failureData[0][2]
                     if failureData[0][2] == 10569:  #SPMQM test failed due to OpShock event ec10569
                        module_pass = False
                        ScrCmds.raiseException(10569, "SPMQM Failed OpShock " + module)
                     else:                        
                        module_pass = False                        
                        ScrCmds.raiseException(int(spmqm_ec), "SPMQM Failed " + module)
                  else:
                     module_pass = False
                     raise

               except:
                  objMsg.printMsg("Count: %s Other SPMQM error %s: %s" % (i, module, traceback.format_exc()))
                  module_pass = False
                  raise

         finally:
            self.dut.spmqm_module = "SPMQM" + module.split('IDT')[1]    # get SPMQM module name
            
            if int(op_dict.get('DISABLE_CELL','0')):
               objMsg.printMsg('SPMQM EnableCell')
               RequestService('EnableCell')

            ##########################################################################
            self.dut.seqNum += 1       # Debug: Will cause wrong TEST_TIME_BY_STATE SEQ?
            objMsg.printMsg('self.dut.seqNum=%s' % self.dut.seqNum)
   
            ctmx.endStamp()
            ctmx.writeDbLog()      
            del ctmx

            if not module_pass:
               self.dut.seqNum -= 1    # Fix TEST_TIME_BY_STATE SEQ. 
            ##########################################################################

      else:
         self.dut.seqNum -= 1    # decrement seqNum because stateMachine will increment
         objMsg.printMsg('TEST_TIME_BY_STATE dblog=')
         objMsg.printDblogBin(self.dut.dblData.Tables('TEST_TIME_BY_STATE'), spcId32 = 1)
         self.dut.objData.update({'spmqm_plr': 0})
   #-------------------------------------------------------------------------------------------------------
   def TestModules(self, module, status):
         ReportStatus('%s --- %s' % ("SPMQM", module))

######################################### Test -1 #########################################################
         if module == 'IDT_RAMP_TEMP' and status == 'ON' and not ConfigVars[CN]['BenchTop']:
            DriveOff()                                          
            objMsg.printMsg('Drive power off prior Temperature Ramping to ambient')
            self.oTemp.rampTemp(self.AmbTemp)
            self.IDT_RAMP_TEMP = 'ON'

######################################### Test -2 #########################################################
         if module == 'IDT_WRT_RD_PERFORM' and status == 'ON':
            result = CWrRd_Perform(self.dut, params={}).doWriteReadPerform('MQM', 256, 2700, 65000, 0)
            if self.doCEDump == 'YES' :
                  objMsg.printMsg("***** Dump SMART Logs and Attributes *****")
                  CGetSMARTLogs(self.dut, params={}).checkSmartLogs([0xA1, 0xA8, 0xA9]) 
                  CGetSMARTLogs(self.dut, params={}).checkSmartAttr()

######################################### Test -3 #########################################################
         if module == 'IDT_WRITE_TEST_MOBILE' and status == 'ON':
            result = CWriteTestMobile(self.dut, params={}).doWriteTestMobile('MQM', 64, 1000000, 4194303, 63, 5000)
            if self.doCEDump == 'YES' :
                  objMsg.printMsg("***** Dump SMART Logs and Attributes *****")
                  CGetSMARTLogs(self.dut, params={}).checkSmartLogs([0xA1, 0xA8, 0xA9]) 
                  CGetSMARTLogs(self.dut, params={}).checkSmartAttr()

######################################### Test -4 #########################################################   
         if module == 'IDT_IMAGE_FILE_COPY' and status == 'ON':
            result = CImageFileCopy(self.dut, params={}).doImageFileCopy()
            if self.doCEDump == 'YES' :
                  objMsg.printMsg("***** Dump SMART Logs and Attributes *****")
                  CGetSMARTLogs(self.dut, params={}).checkSmartLogs([0xA1, 0xA8, 0xA9]) 
                  CGetSMARTLogs(self.dut, params={}).checkSmartAttr()

######################################### Test -5 #########################################################   
         if module == 'IDT_IMAGE_FILE_READ' and status == 'ON': 
            result = CImageFileRead(self.dut, params={}).doImageFileRead()
            if self.doCEDump == 'YES' :
                  objMsg.printMsg("***** Dump SMART Logs and Attributes *****")
                  CGetSMARTLogs(self.dut, params={}).checkSmartLogs([0xA1, 0xA8, 0xA9]) 
                  CGetSMARTLogs(self.dut, params={}).checkSmartAttr()

######################################### Test -6 #########################################################   
         if module == 'IDT_SHORT_DST_IDE' and status == 'ON':
            result = CSmartDST_SPT(self.dut, params={}).DSTTest_IDE('MQM', 'Short')
            if self.doCEDump == 'YES' :
                  objMsg.printMsg("***** Dump SMART Logs and Attributes *****")
                  CGetSMARTLogs(self.dut, params={}).checkSmartLogs([0xA1, 0xA8, 0xA9]) 
                  CGetSMARTLogs(self.dut, params={}).checkSmartAttr()

######################################### Test -7 #########################################################   
         if module == 'IDT_READ_TEST_DRIVE' and status == 'ON':
            result = CReadTestDrive(self.dut, params={}).doReadTestDrive()
            if self.doCEDump == 'YES' :
                  objMsg.printMsg("***** Dump SMART Logs and Attributes *****")
                  CGetSMARTLogs(self.dut, params={}).checkSmartLogs([0xA1, 0xA8, 0xA9]) 
                  CGetSMARTLogs(self.dut, params={}).checkSmartAttr()

######################################### Test -8 #########################################################   
         if module == 'IDT_LOW_DUTY_CYCLE' and status == 'ON':
            result = CLowDutyRead(self.dut, params={}).doLowDutyCycle('MQM', 10000, 14999, 1000000, 100, 2, 0.5)
            if self.doCEDump == 'YES' :
                  objMsg.printMsg("***** Dump SMART Logs and Attributes *****")
                  CGetSMARTLogs(self.dut, params={}).checkSmartLogs([0xA1, 0xA8, 0xA9]) 
                  CGetSMARTLogs(self.dut, params={}).checkSmartAttr()
            if self.IDT_RAMP_TEMP == 'ON' and not ConfigVars[CN]['BenchTop'] and result == OK:   
               if self.dut.driveattr['TEMP_RAMP'] == 'NO':
                  objMsg.printMsg('>>>> Ramp to 22deg with Wait for NonTempProfile - DriveOff, ReleaseHeater/Fan')      
                  DriveOff()                                       
                  if not self.dut.chamberType == 'NEPTUNE': 
                     ReleaseTheHeater()
                  self.oTemp.rampTemp(self.AmbTemp, ON, 600, 3, 3)  
                  if not self.dut.chamberType == 'NEPTUNE':
                     ReleaseTheFans()

######################################### Test -9 #########################################################
         if module == 'IDT_OS_WRITE_TEST' and status == 'ON':      
            result = COSWriteTest(self.dut, params={}).doOSWriteDrive('MQM', 16, 5.0)
            if self.doCEDump == 'YES' :
                  objMsg.printMsg("***** Dump SMART Logs and Attributes *****")
                  CGetSMARTLogs(self.dut, params={}).checkSmartLogs([0xA1, 0xA8, 0xA9]) 
                  CGetSMARTLogs(self.dut, params={}).checkSmartAttr()

######################################### Test -10 ########################################################         
         if module == 'IDT_OS_READ_COMPARE' and status == 'ON':
            result = COSReadCompare(self.dut, params={}).doOSReadDrive()
            if self.doCEDump == 'YES' :
                  objMsg.printMsg("***** Dump SMART Logs and Attributes *****")
                  CGetSMARTLogs(self.dut, params={}).checkSmartLogs([0xA1, 0xA8, 0xA9]) 
                  CGetSMARTLogs(self.dut, params={}).checkSmartAttr()

######################################### Test -11 ########################################################   
         if module == 'IDT_OS_READ_REVERSE' and status == 'ON':
            result = COS_ReadReverse(self.dut, params={}).doOSReadReverse('MQM', 64, 5.0)
            if self.doCEDump == 'YES' :
                  objMsg.printMsg("***** Dump SMART Logs and Attributes *****")
                  CGetSMARTLogs(self.dut, params={}).checkSmartLogs([0xA1, 0xA8, 0xA9]) 
                  CGetSMARTLogs(self.dut, params={}).checkSmartAttr()

######################################### Test -12 ########################################################   
         if module == 'IDT_WRITE_PATTERN' and status == 'ON':
            result = CWritePattern(self.dut, params={}).doWritePattern('MQM', '00', 0, 10000000)
            if self.doCEDump == 'YES' :
                  objMsg.printMsg("***** Dump SMART Logs and Attributes *****")
                  CGetSMARTLogs(self.dut, params={}).checkSmartLogs([0xA1, 0xA8, 0xA9]) 
                  CGetSMARTLogs(self.dut, params={}).checkSmartAttr()

######################################### Test -13 ########################################################   
         if module == 'IDT_READ_PATTERN_FORWARD' and status == 'ON':
            result = CReadPatternForward(self.dut, params={}).doReadPattForward()
            if self.doCEDump == 'YES' :
                  objMsg.printMsg("***** Dump SMART Logs and Attributes *****")
                  CGetSMARTLogs(self.dut, params={}).checkSmartLogs([0xA1, 0xA8, 0xA9]) 
                  CGetSMARTLogs(self.dut, params={}).checkSmartAttr()
            if self.IDT_RAMP_TEMP == 'ON' and not ConfigVars[CN]['BenchTop'] and result == OK:
               if self.dut.driveattr['TEMP_RAMP'] == 'NO':
                  objMsg.printMsg('>>>> Ramp to 22deg with Wait for NonTempProfile - DriveOff, ReleaseHeater/Fan')      
                  DriveOff()                                       
                  if not self.dut.chamberType == 'NEPTUNE': 
                     ReleaseTheHeater()
                  self.oTemp.rampTemp(self.AmbTemp, ON, 600, 3, 3)  
                  if not self.dut.chamberType == 'NEPTUNE':
                     ReleaseTheFans()

######################################### Test -14 ########################################################   
         if module == 'IDT_ODTATI_TEST' and status == 'ON':
            result = CODTATI(self.dut, params={}).doODTATI('MQM')
            if self.doCEDump == 'YES' :
                  objMsg.printMsg("***** Dump SMART Logs and Attributes *****")
                  CGetSMARTLogs(self.dut, params={}).checkSmartLogs([0xA1, 0xA8, 0xA9]) 
                  CGetSMARTLogs(self.dut, params={}).checkSmartAttr()

######################################### Test -15 ########################################################   
         if module == 'IDT_VOLTAGE_HIGH_LOW' and status == 'ON':
            result = CVoltageHighLow(self.dut, params={}).doVoltageHighLow('MQM', 2) 
            if self.doCEDump == 'YES' :
                  objMsg.printMsg("***** Dump SMART Logs and Attributes *****")
                  CGetSMARTLogs(self.dut, params={}).checkSmartLogs([0xA1, 0xA8, 0xA9]) 
                  CGetSMARTLogs(self.dut, params={}).checkSmartAttr()
            if self.IDT_RAMP_TEMP == 'ON' and not ConfigVars[CN]['BenchTop'] and result == OK:
               if self.dut.driveattr['TEMP_RAMP'] == 'YES':
                  objMsg.printMsg('Ramp to 22deg NoWait, ReleaseHeater/Fan')      
                  if not self.dut.chamberType == 'NEPTUNE': 
                     ReleaseTheHeater()
                  DriveOff()   
                  self.oTemp.rampTemp(self.AmbTemp, OFF, 600, 3, 3)                             # Ramp Slot to Temperature
                  if not self.dut.chamberType == 'NEPTUNE': 
                     ReleaseTheFans()
               else:
                  objMsg.printMsg('Ramp to 22deg with Wait - DriveOff, ReleaseHeater/Fan')      
                  DriveOff()                                       
                  if not self.dut.chamberType == 'NEPTUNE': 
                     ReleaseTheHeater()
                  self.oTemp.rampTemp(self.AmbTemp, ON, 600, 3, 3)  
                  if not self.dut.chamberType == 'NEPTUNE': 
                     ReleaseTheFans()

######################################### Test -16 ########################################################   
         if module == 'IDT_RANDOM_WRITE_TEST' and status == 'ON':      
            result = CRandom_Write(self.dut, params={}).doRandomWrite('MQM', 10000)
            if result == SKIP:
               self.skip_nxt_module = True
            if self.doCEDump == 'YES' :
                  objMsg.printMsg("***** Dump SMART Logs and Attributes *****")
                  CGetSMARTLogs(self.dut, params={}).checkSmartLogs([0xA1, 0xA8, 0xA9]) 
                  CGetSMARTLogs(self.dut, params={}).checkSmartAttr()
            if self.IDT_RAMP_TEMP == 'ON' and not ConfigVars[CN]['BenchTop'] and result == OK:
               objMsg.printMsg('Ramp to 22deg with Wait - DriveOff, ReleaseHeater/Fan')      
               DriveOff()              
               if not self.dut.chamberType == 'NEPTUNE':
                  ReleaseTheHeater()
               self.oTemp.rampTemp(self.AmbTemp, ON, 600, 3, 3)  
               if not self.dut.chamberType == 'NEPTUNE':
                  ReleaseTheFans()

######################################### Test -16b ########################################################   
         if module == 'IDT_RANDOM_READ_TEST' and status == 'ON':      
            result = CRandom_Read(self.dut, params={}).doRandomRead('MQM', 250000)
            if self.doCEDump == 'YES' :
                  objMsg.printMsg("***** Dump SMART Logs and Attributes *****")
                  CGetSMARTLogs(self.dut, params={}).checkSmartLogs([0xA1, 0xA8, 0xA9]) 
                  CGetSMARTLogs(self.dut, params={}).checkSmartAttr()
            if self.IDT_RAMP_TEMP == 'ON' and not ConfigVars[CN]['BenchTop'] and result == OK:
               objMsg.printMsg('Ramp to 22deg with Wait - DriveOff, ReleaseHeater/Fan')      
               DriveOff()              
               if not self.dut.chamberType == 'NEPTUNE':
                  ReleaseTheHeater()
               self.oTemp.rampTemp(self.AmbTemp, ON, 600, 3, 3)  
               if not self.dut.chamberType == 'NEPTUNE':
                  ReleaseTheFans()

######################################### Test -17 ########################################################   
         if module == 'IDT_FULL_DST_IDE' and status == 'ON':
            objMsg.printMsg("Dump V4 entry before LDST")
            Init_entry = 0
            Init_entry = self.oSerial.dumpReassignedSectorList()['NUMBER_OF_TOTALALTS']

            from Temperature import CTemperature
            oTemp = CTemperature()
            SOCtemp = oTemp.getDeviceTemp(devSelect=3)
            HDAtemp = oTemp.getDeviceTemp(devSelect=2)
            cellTemp = "%0.1f" % (ReportTemperature()/10.0)
            objMsg.printMsg("Before LongDST: SOC temperature = %s degC, HDA temperature = %s degC, Cell temperature = %s" % (SOCtemp, HDAtemp, cellTemp))   
            self.dut.dblData.Tables('P_TEMPERATURES').addRecord(
                     {
                     'SPC_ID'       : 4,
                     'OCCURRENCE'   : 1,
                     'SEQ'          : self.dut.seqNum+1,
                     'TEST_SEQ_EVENT': 0,
                     'STATE_NAME'   : self.dut.nextState,
                     'DRIVE_TEMP'   : HDAtemp,
                     'CELL_TEMP'    : cellTemp,
                     'ELEC_TEMP'    : SOCtemp,
                     })
            result = CSmartDST_SPT(self.dut, params={}).DSTTest_IDE('MQM', 'Long')
            SOCtemp = oTemp.getDeviceTemp(devSelect=3)
            HDAtemp = oTemp.getDeviceTemp(devSelect=2)
            cellTemp = "%0.1f" % (ReportTemperature()/10.0)
            objMsg.printMsg("After LongDST: SOC temperature = %s degC, HDA temperature = %s degC, Cell temperature = %s" % (SOCtemp, HDAtemp, cellTemp))  
            self.dut.dblData.Tables('P_TEMPERATURES').addRecord(
                     {
                     'SPC_ID'       : 4,
                     'OCCURRENCE'   : 2,
                     'SEQ'          : self.dut.seqNum+1,
                     'TEST_SEQ_EVENT': 0,
                     'STATE_NAME'   : self.dut.nextState,
                     'DRIVE_TEMP'   : HDAtemp,
                     'CELL_TEMP'    : cellTemp,
                     'ELEC_TEMP'    : SOCtemp,
                     })
            objMsg.printMsg("Dump V4 entry after LDST")
            End_entry = 0
            End_entry = self.oSerial.dumpReassignedSectorList()['NUMBER_OF_TOTALALTS']

            if (End_entry - Init_entry) > 0:
               objMsg.printMsg("Additional V4 entry after LDST")
               ScrCmds.raiseException(13069,'IDT_FULL_DST_IDE Failed')
            if self.doCEDump == 'YES' :
                  objMsg.printMsg("***** Dump SMART Logs and Attributes *****")
                  CGetSMARTLogs(self.dut, params={}).checkSmartLogs([0xA1, 0xA8, 0xA9]) 
                  CGetSMARTLogs(self.dut, params={}).checkSmartAttr()
            if self.IDT_RAMP_TEMP == 'ON' and not ConfigVars[CN]['BenchTop'] and result == OK:
               objMsg.printMsg('Ramp to 22deg with Wait - DriveOff, ReleaseHeater/Fan')      
               DriveOff()              
               if not self.dut.chamberType == 'NEPTUNE':
                  ReleaseTheHeater()
               self.oTemp.rampTemp(self.AmbTemp, ON, 600, 3, 3)  
               if not self.dut.chamberType == 'NEPTUNE':
                  ReleaseTheFans()

######################################### Test -18 ########################################################   
         if module == 'IDT_DELAY_WRT' and status == 'ON':
            result = CDelay_Write(self.dut, params={}).doDelayWrite('MQM', 'DELAYWRT')
            if self.doCEDump == 'YES' :
                  objMsg.printMsg("***** Dump SMART Logs and Attributes *****")
                  CGetSMARTLogs(self.dut, params={}).checkSmartLogs([0xA1, 0xA8, 0xA9]) 
                  CGetSMARTLogs(self.dut, params={}).checkSmartAttr()
            if self.IDT_RAMP_TEMP == 'ON' and not ConfigVars[CN]['BenchTop'] and result == OK:
               objMsg.printMsg('Ramp to 22deg with Wait - DriveOff, ReleaseHeater/Fan')      
               DriveOff()              
               if not self.dut.chamberType == 'NEPTUNE':
                  ReleaseTheHeater()
               self.oTemp.rampTemp(self.AmbTemp, ON, 600, 3, 3)  
               if not self.dut.chamberType == 'NEPTUNE':
                  ReleaseTheFans()

######################################### Test -19 ########################################################   
         if module == 'IDT_MS_SUS_TXFER_RATE' and status == 'ON':
            result = CMSSusTxferRate(self.dut, params={}).doMSSustainTferRate()
            if self.doCEDump == 'YES' :
                  objMsg.printMsg("***** Dump SMART Logs and Attributes *****")
                  CGetSMARTLogs(self.dut, params={}).checkSmartLogs([0xA1, 0xA8, 0xA9]) 
                  CGetSMARTLogs(self.dut, params={}).checkSmartAttr()
            if self.IDT_RAMP_TEMP == 'ON' and not ConfigVars[CN]['BenchTop'] and result == OK:
               objMsg.printMsg('Ramp to 22deg with Wait - DriveOff, ReleaseHeater/Fan')      
               DriveOff()              
               if not self.dut.chamberType == 'NEPTUNE':
                  ReleaseTheHeater()
               self.oTemp.rampTemp(self.AmbTemp, ON, 600, 3, 3)  
               if not self.dut.chamberType == 'NEPTUNE':
                  ReleaseTheFans()

######################################### Test -20 ########################################################   
         if module == 'IDT_PM_ZONETHRUPUT' and status == 'ON':
            result = CPMZoneThroughPut(self.dut, params={}).doPerfMeasureZoneDegrade()
            if result == SKIP:
               self.skip_nxt_module = True
            if self.doCEDump == 'YES' :
                  objMsg.printMsg("***** Dump SMART Logs and Attributes *****")
                  CGetSMARTLogs(self.dut, params={}).checkSmartLogs([0xA1, 0xA8, 0xA9]) 
                  CGetSMARTLogs(self.dut, params={}).checkSmartAttr()
            if self.IDT_RAMP_TEMP == 'ON' and not ConfigVars[CN]['BenchTop'] and result == OK:
               objMsg.printMsg('Ramp to 22deg with Wait - DriveOff, ReleaseHeater/Fan')      
               DriveOff()              
               if not self.dut.chamberType == 'NEPTUNE':
                  ReleaseTheHeater()
               self.oTemp.rampTemp(self.AmbTemp, ON, 600, 3, 3)  
               if not self.dut.chamberType == 'NEPTUNE':
                  ReleaseTheFans()

######################################### Test -21 ########################################################   
         if module == 'IDT_ENCROACHMENT_EUP' and status == 'ON':
            result = CEncroachment_EUP(self.dut, params={}).doEncroachmentEUP('MQM', 'ENC EUP')
            if self.doCEDump == 'YES' :
                  objMsg.printMsg("***** Dump SMART Logs and Attributes *****")
                  CGetSMARTLogs(self.dut, params={}).checkSmartLogs([0xA1, 0xA8, 0xA9]) 
                  CGetSMARTLogs(self.dut, params={}).checkSmartAttr()

######################################### Test -22 ########################################################   
         if module == 'IDT_SERIAL_SDOD_TEST' and status == 'ON':
            result = CSerialSDOD(self.dut, params={}).doSerialSDODCheck(TestType=self.TestMode)
            if result <> OK:
               raise "IDT_SERIAL_SDOD_TEST Failed"         
            if self.doCEDump == 'YES' and self.TestMode != "MODE_SPFIN":
                  objMsg.printMsg("***** Dump SMART Logs and Attributes *****")
                  CGetSMARTLogs(self.dut, params={}).checkSmartLogs([0xA1, 0xA8, 0xA9]) 
                  CGetSMARTLogs(self.dut, params={}).checkSmartAttr()

######################################### Test -23 ########################################################   
         if module == 'IDT_BEATUP_WR_RD' and status == 'ON':
            result = CBeatupWrRd(self.dut, params={}).doWriteRead()
            if self.doCEDump == 'YES' :
                  objMsg.printMsg("***** Dump SMART Logs and Attributes *****")
                  CGetSMARTLogs(self.dut, params={}).checkSmartLogs([0xA1, 0xA8, 0xA9]) 
                  CGetSMARTLogs(self.dut, params={}).checkSmartAttr()

######################################### Test -23 ########################################################   
         if module == 'IDT_WRITE_DRIVE_ZERO' and status == 'ON':
            result = CWriteDriveZero(self.dut, params={}).doWriteZeroPatt('MQM', 'MaxLBA')
            #result = CWriteDriveZero(self.dut, params={}).doWriteZeroPatt('MQM', NumLBA=300000)
            if self.doCEDump == 'YES' :
                  objMsg.printMsg("***** Dump SMART Logs and Attributes *****")
                  CGetSMARTLogs(self.dut, params={}).checkSmartLogs([0xA1, 0xA8, 0xA9]) 
                  CGetSMARTLogs(self.dut, params={}).checkSmartAttr()

######################################### Test -24 ########################################################   
         if module == 'IDT_READ_ZERO_COMPARE' and status == 'ON':
            if ConfigVars[CN].get('FULLPACK READZERO', 'OFF') == 'ON':
               result = CRead_ZeroCompare(self.dut, params={}).doReadZeroCompare('MQM', 'MaxLBA')
            else:
               result = CRead_ZeroCompare(self.dut, params={}).doReadZeroCompareGuard()  # ReadZeroCompare only to 1st and last 20M LBA                
            if self.doCEDump == 'YES' :
                  objMsg.printMsg("***** Dump SMART Logs and Attributes *****")
                  CGetSMARTLogs(self.dut, params={}).checkSmartLogs([0xA1, 0xA8, 0xA9]) 
                  CGetSMARTLogs(self.dut, params={}).checkSmartAttr()

######################################### Test -25 ########################################################
         if module == 'IDT_VERIFY_SMART_ONLY' and status == 'ON':
            ScrCmds.insertHeader("IDT_VERIFY_SMART_ONLY",headChar='#')              
            result = CVerifySMART(self.dut, params={}).verifySmart()

######################################### Test -26 ########################################################
         if module == 'IDT_VERIFY_SMART_IDE' and status == 'ON':
            ScrCmds.insertHeader("IDT_VERIFY_SMART_IDE",headChar='#')              
            result = CVerifySMART(self.dut, params={}).verifySmart()
            result = CGetSMARTLogs(self.dut, params={}).checkSmartLogs([0xA1, 0xA8, 0xA9])
            #Temperature Ramp to HOT if PASS
            if self.IDT_RAMP_TEMP == 'ON' and not ConfigVars[CN]['BenchTop'] and result == OK:
               if (self.oTemp.selectDrvTempRamp() == 'YES'):
                  objMsg.printMsg('Ramp to %sdeg with NO Wait' %self.HotTemp)  
                  DriveOff()
                  self.oTemp.rampTemp(self.HotTemp, OFF, 600, 3, 3)
                  self.dut.driveattr['TEMP_RAMP'] = 'YES'
               else:
                  objMsg.printMsg('Ramp to %sdeg with Wait' %self.AmbTemp)  
                  if not self.dut.chamberType == 'NEPTUNE':  
                     ReleaseTheHeater()
                  self.oTemp.rampTemp(self.AmbTemp, ON, 600, 3, 3)  
                  if not self.dut.chamberType == 'NEPTUNE': 
                    ReleaseTheFans()
                  self.dut.driveattr['TEMP_RAMP'] = 'NO'
               DriveAttributes.update(self.dut.driveattr)

######################################### Test -27 ########################################################
         if module == 'IDT_GET_SMART_LOGS' and status == 'ON': 
            ScrCmds.insertHeader("IDT_GET_SMART_LOGS",headChar='#')  
            result = CGetSMARTLogs(self.dut, params={}).runSmart([0xA1, 0xA8, 0xA9])

######################################### Test -28 ########################################################
         if module == 'IDT_SERVO_RECALL_TEST' and status == 'ON': 
            ScrCmds.insertHeader("IDT_SERVO_RECALL_TEST",headChar='#')  
            result = CServoRecall(self.dut, params={}).doServoRecall()

######################################### Test -29 ########################################################
         if module == 'IDT_RESET_SMART' and status == 'ON': 
            ScrCmds.insertHeader("IDT_RESET_SMART",headChar='#')  
            result = CResetSMART(self.dut, params={}).ResetSmart()

######################################### Test -29 ########################################################
         if module == 'IDT_CHECK_SMART_ATTR' and status == 'ON': 
            ScrCmds.insertHeader("IDT_CHECK_SMART_ATTR",headChar='#')  
            result = CGetSMARTLogs(self.dut, params={}).checkSmartAttr()

######################################### Test -30 ########################################################
         if module == 'IDT_BER_BY_ZONE' and status == 'ON': 
            ScrCmds.insertHeader("IDT_BER_BY_ZONE",headChar='#')  
            result = CBERByZone(self.dut, params={}).doBERByZone(self.dut.FLAG)
            self.dut.FLAG = 1

######################################### Test -31 ########################################################
         if module == 'IDT_IDLE_APM_TEST' and status == 'ON': 
            ScrCmds.insertHeader("IDT_IDLE_APM_TEST",headChar='#')  
            result = CIdleAPMTest(self.dut, params={}).doIdleAPMTest()

######################################### Test -32 ########################################################
         if module == 'IDT_SUPER_PARITY_CLEANUP' and status == 'ON':
            ScrCmds.insertHeader("IDT_SUPER_PARITY_CLEANUP",headChar='#')  
            result = CSuperParityCleanUp(self.dut, params={}).doSuperParityCleanUp()

###########################################################################################################
###########################################################################################################
class CSPFIN2(CGIO):
   #-------------------------------------------------------------------------------------------------------
   def run(self, prm_spfin2 = []):
      self.TestMode = "MODE_SPFIN"

      Modules = [       ('IDT_SHORT_DST_IDE'          , 'ON'),
                        ('IDT_GET_SMART_LOGS'         , 'ON'),
                        ('IDT_VERIFY_SMART_IDE'       , 'OFF'),
                        ('IDT_VERIFY_SMART_ONLY'      , 'ON'),
                        ('IDT_RESET_SMART'            , 'ON'),
                        ('IDT_CHECK_SMART_ATTR'       , 'ON'),
                        ('IDT_SERIAL_SDOD_TEST'       , 'OFF')]

      FINModules = getattr(TP,"prm_FINModules",Modules)
      if self.dut.nextState is 'LONG_DST':
         FINModules = [
                        ('IDT_GET_SMART_LOGS'         , 'ON', {"SPMQM_EC": "13089"}),   # Check SMART log before start of SPFIN2
                        ('IDT_FULL_DST_IDE'           , 'ON', {"SPMQM_EC": "13069", "OPS_CAUSE": "SPMQM_FDI"}),
                      ]

      # in FNG2, need full pack read LongDST
      if self.dut.nextOper == 'FNG2' and ('IDT_FULL_DST_IDE', 'ON') not in FINModules:
         FINModules.insert( 0, ('IDT_FULL_DST_IDE', 'ON'))

      if len(prm_spfin2) > 0:
         FINModules = prm_spfin2

      objMsg.printMsg("CSPFIN2 FINModules: %s" % FINModules)
      CInit_Testing(self.dut, params={}).run()
      self.RunModules(FINModules)
      objMsg.printMsg("CSPFIN2 FINModules end")

###########################################################################################################
###########################################################################################################
class CInit_Testing(CState):
   """
      Class that contain intialize GIO test state. 
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      self.dut.RetryCnt = 0
      self.dut.FLAG = 0
      self.dut.MQM_BEGIN_OTF_H0=0
      self.dut.MQM_BEGIN_OTF_H1=0
      self.dut.MQM_BEGIN_RAW_H0=0
      self.dut.MQM_BEGIN_RAW_H1=0

      CState.__init__(self, dut, depList)
      self.oGIO = CGIO(self.dut, params={})
      self.oSerial = serialScreen.sptDiagCmds()
   #---------------------------------------------------------------------------------------------------------#
   def run(self):
      ScrCmds.insertHeader("IDT Init Testing",headChar='#')
      self.oGIO.powerCycle(pwrOption = "pwrDefault")
      
      if self.dut.sptActive.getMode() == self.dut.sptActive.availModes.mctBase:
         ScrCmds.raiseException(11044, "Drive in SF3 mode. F3 mode is required" )
      
      #Get MAX_LBA and MediaCache Offset
      ICmd.SPGetMaxLBA() 
      ICmd.BufferStatus()
      
###########################################################################################################
def getSerialPortData():
   timeout = 60
   ScrCmds.insertHeader("Get Serial Port Data",headChar='#') 
   objMsg.printMsg('*****************************************************************************')
   for i in range (3):
      try:
         objMsg.printMsg('[Enabling Drive Diagnostic Mode(%d)]' % (i+1))
         time.sleep(5)
         prompt = sptCmds.enableDiags(5, raiseException = 0)   
      except Exception, e:
         objMsg.printMsg('Enable Diagnostic Exception Data=%s' %e)      
      else:   
         if prompt.find ('T>') > -1:
            objMsg.printMsg('[Drive Diagnostic Mode Enabled!]')
            break
         else: 
            objMsg.printMsg('[Drive Diagnostic Mode Enabled Failed.  Apply Power Cycle!]')
            CGIO(objDut, params={}).powerCycle()
            continue

   try: 
      objMsg.printMsg('*****************************************************************************')
      objMsg.printMsg('Dot command :')
      data = sptCmds.execOnlineCmd(DOT, timeout = timeout, waitLoops = 100)
      objMsg.printMsg("Data returned from DOT command - data = %s" % `data`)
         
      objMsg.printMsg('Native Interface Command State :')
      data = sptCmds.execOnlineCmd('~', timeout = timeout, waitLoops = 100)
      objMsg.printMsg("Data returned from ~ command - data = %s" % `data`)
        
      objMsg.printMsg('*****************************************************************************')
      objMsg.printMsg('Drive ATA Status :')
      data = sptCmds.execOnlineCmd(CTRL_E, timeout = timeout, waitLoops = 100)
      objMsg.printMsg("Data returned from Ctrl-E command - data = %s" % `data`) 
       
      objMsg.printMsg('*****************************************************************************')
      objMsg.printMsg('Command History Ctrl X :')
      data = sptCmds.execOnlineCmd(CTRL_X, timeout = timeout, waitLoops = 100)
      objMsg.printMsg("Data returned from Ctrl-X command:\n%s" % data)
       
      objMsg.printMsg('*****************************************************************************')
      sptCmds.gotoLevel('T')
      objMsg.printMsg('Defect Alt List V4 :')
      data = sptCmds.sendDiagCmd("V4",timeout = timeout, printResult = True, loopSleepTime=0)
      objMsg.printMsg('Defective Track List :')
      data = sptCmds.sendDiagCmd("V800",timeout = timeout, printResult = True, loopSleepTime=0)
    
      objMsg.printMsg('*****************************************************************************')
      objMsg.printMsg('Diode Temperature :')
      data = sptCmds.execOnlineCmd(CTRL_B, timeout = timeout, waitLoops = 100)
      objMsg.printMsg("Data returned from CTRL-B command:\n%s" % data)
      Pat = re.compile(', (?P<thermistor>\d+)d\r\n')
      Mat = Pat.search(data)
      thermistor = -1
      if Mat:
         thermistor = int(Mat.groupdict()['thermistor'])
      objMsg.printMsg('Diode Temp Reading=%s' % thermistor)
       
      objMsg.printMsg('*****************************************************************************')
      objMsg.printMsg('[Servo Data]')
      sptCmds.gotoLevel('4')
      objMsg.printMsg('Servo Sector Error Count :')
      data = sptCmds.sendDiagCmd("s", timeout=timeout, altPattern='4>', printResult=True)
      objMsg.printMsg('Servo Sector Error Log :')
      data = sptCmds.sendDiagCmd("g", timeout=timeout, altPattern='4>', printResult=True)
         
      objMsg.printMsg('*****************************************************************************')
      objMsg.printMsg('[Smart Data]')
      sptCmds.gotoLevel('1')
      # Dump Smart Attribute
      objMsg.printMsg('Smart Attributes :')
      data = sptCmds.sendDiagCmd('N5', printResult = True) 
      # Dump Smart CE 
      objMsg.printMsg('CE Log :')
      data = sptCmds.sendDiagCmd('N8', printResult = True)
      # Dump Smart RList
      objMsg.printMsg('RList Count :')
      data = sptCmds.sendDiagCmd('N18', printResult = True)
   except Exception, e:
      objMsg.printMsg("Serial Port Exception data : %s"%e)   
    
   objMsg.printMsg('*****************************************************************************')
   # Display Smart Logs
   CGetSMARTLogs(objDut, params={}).runSmart([0xA1, 0xA8, 0xA9], OFF)

   ScrCmds.insertHeader('Get Serial Port Data End',headChar='#') 

###########################################################################################################
###########################################################################################################
class CWrRd_Perform(CState):
   """
      Class that contain GIO test modules. 
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)
      self.oGIO = CGIO(self.dut, params={})
   #---------------------------------------------------------------------------------------------------------#
   def doWriteReadPerform(self, TestType, SectCnt, Count, Step, Reverse=1):
      ScrCmds.insertHeader("IDT_WRT_RD_PERFORM",headChar='#')
      data = {}
      result = OK
      self.testCmdTime = 0
      self.testName = TestType
      
      self.oGIO.powerCycle()
      
      # Setup Parameters
      self.udmaSpeed = 0x45
      self.pattern = '1111'
      if TestType == 'MQM':
         self.pattern = '0000'
      IDMaxLBA = self.dut.driveattr['Max LBA']
      ID1=(IDMaxLBA - 2000000)
      MD1=(IDMaxLBA / 2)
      if Reverse == 1:
         OD1=2000000
      else:
         OD1=0
      self.sectorCount = SectCnt
      self.numBlocks = 12*Count/self.sectorCount
      
      for testloop in range(2):
         if Reverse == 1:  # Read in Reverse order, ID-MD-OD, Step from High LBA's to Low LBA's 
            ID2=ID1-Step; ID3=ID2-Step; ID4=ID3-Step;
            LocationsID = ("%d,%d,%d,%d,%d,%d,%d,%d," % \
                          (ID1, ID1+Count, ID2, ID2+Count, ID3, ID3+Count, ID4, ID4+Count)) 
            MD2=MD1-Step; MD3=MD2-Step; MD4=MD3-Step;
            LocationsMD = ("%d,%d,%d,%d,%d,%d,%d,%d," % \
                          (MD1, MD1+Count, MD2, MD2+Count, MD3, MD3+Count, MD4, MD4+Count)) 
            OD2=OD1-Step; OD3=OD2-Step; OD4=OD3-Step;
            LocationsOD = ("%d,%d,%d,%d,%d,%d,%d,%d," % \
                          (OD1, OD1+Count, OD2, OD2+Count, OD3, OD3+Count, OD4, OD4+Count)) 
            LocationsALL = LocationsID + LocationsMD + LocationsOD
            objMsg.printMsg('%s SectCnt=%s UDMA_Speed=0x%X Patten=%s WRCount=%s Step=%s' % \
                           (self.testName,self.sectorCount,self.udmaSpeed,self.pattern,Count,Step)) 
            objMsg.printMsg('%s Locations ID=%s' % (self.testName, LocationsID)) 
            objMsg.printMsg('%s Locations MD=%s' % (self.testName, LocationsMD)) 
            objMsg.printMsg('%s Locations OD=%s' % (self.testName, LocationsOD)) 
            
         else:             # Read in Forward order, OD-MD-ID, Step from Low LBA's to High LBA's
            OD2=OD1+Step; OD3=OD2+Step; OD4=OD3+Step;
            LocationsOD = ("%d,%d,%d,%d,%d,%d,%d,%d," % \
                          (OD1, OD1+Count, OD2, OD2+Count, OD3, OD3+Count, OD4, OD4+Count)) 
            MD2=MD1+Step; MD3=MD2+Step; MD4=MD3+Step;
            LocationsMD = ("%d,%d,%d,%d,%d,%d,%d,%d," % \
                          (MD1, MD1+Count, MD2, MD2+Count, MD3, MD3+Count, MD4, MD4+Count)) 
            ID2=ID1+Step; ID3=ID2+Step; ID4=ID3+Step;
            LocationsID = ("%d,%d,%d,%d,%d,%d,%d,%d," % \
                          (ID1, ID1+Count, ID2, ID2+Count, ID3, ID3+Count, ID4, ID4+Count)) 
            LocationsALL = LocationsOD + LocationsMD + LocationsID
            objMsg.printMsg('%s SectCnt=%s UDMA_Speed=0x%X Patten=%s WRCount=%s Step=%s' % \
                           (self.testName,self.sectorCount,self.udmaSpeed,self.pattern,Count,Step)) 
            objMsg.printMsg('%s Locations OD=%s' % (self.testName, LocationsOD)) 
            objMsg.printMsg('%s Locations MD=%s' % (self.testName, LocationsMD)) 
            objMsg.printMsg('%s Locations ID=%s' % (self.testName, LocationsID))
            
         Retry = 2
         for loop in range(Retry+1):
            if testSwitch.virtualRun:
               data = {'LLRET': 0, 'LBA': '0x000000003A1CD5F2', 'ERR': '0', 'RES': '', 'DEV': '64', 'SCNT': '0', 'RESULT': 'IEK_OK:No error', 'STS': '80', 'CT': '2065'}
            else:               
               data = ICmd.WeakWrite(eval(LocationsALL), self.sectorCount, self.udmaSpeed, self.pattern,Count)
            result = data['LLRET']
            
            if result == OK:
               objMsg.printMsg("%s CPCWeakWrite Passed - Data: %s" % (self.testName, data))
               break
            else:
               objMsg.printMsg("%s CPCWeakWrite Failed - Data: %s" % (self.testName, data))
            # End of CPCWeakWrite loop
         if result != OK: break
         if Reverse == 1:
            OD1=OD4-Step 
            MD1=MD4-Step
            ID1=ID4-Step
         else:
            OD1=OD4+Step 
            MD1=MD4+Step
            ID1=ID4+Step
         # End of Test loop
      
      if result != OK:
         objMsg.printMsg('%s Failed Result=%s Data=%s' % (self.testName, result, data))
         getSerialPortData()
         ScrCmds.raiseException(13060, 'IDT_WRT_RD_PERFORM Failed')
      else:
         objMsg.printMsg('%s Test Passed' % self.testName)
         
      return result
   
###########################################################################################################
class CDelay_Write(CState):
   """
      Class that performs IDT_DELAY_WRT test. 
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)
      self.oGIO = CGIO(self.dut, params={})
   #-------------------------------------------------------------------------------------------------------
   def doDelayWrite(self, TestType, TestName):
      ScrCmds.insertHeader("IDT_DELAY_WRT",headChar='#')
      result = OK
      self.testName = ('%s %s' % (TestType, TestName))                       # Test Name for file formatting

      minLBA = startLBA = endLBA = 0 
      maxLBA = self.dut.driveattr['Max LBA']
      
      stepLBA = 256
      sectCnt = 256
      
      DELAYWRT = ON
      DelayWrtLoop = 1000
      minDelay = 200  #ms
      maxDelay = 400 #ms
      stepDelay = 100 #ms
      GrpCnt = 1
      DelayStepLba = ((maxDelay - minDelay) / stepDelay + 2) * sectCnt * GrpCnt    #+2 to ensure all delay time execute.
  
      if DELAYWRT == ON:
         self.oGIO.powerCycle()
         ICmd.ClearBinBuff()
         ICmd.FillBuffer(1,0,'0000')
         
         if result == OK:
            startLBA = minLBA
            endLBA = maxLBA - DelayStepLba
            objMsg.printMsg('%s Random(StartLBA=%d EndLBA=%d) SectCnt=%d MinDelay=%d MaxDelay=%d StepDelay=%d GrpCnt=%d DelayStepLba=%d, DelayWrtLoop=%d' % \
                              (TestName, startLBA, endLBA, sectCnt, minDelay, maxDelay, stepDelay, GrpCnt, DelayStepLba, DelayWrtLoop))
            data = ICmd.SeqDelayWR(startLBA, endLBA, sectCnt, minDelay, maxDelay, stepDelay, GrpCnt, DelayStepLba, DelayWrtLoop)
            result = data['LLRET']
          
         if result != OK:
            objMsg.printMsg('%s SeqDelayWR failed. Result=%s Data=%s' % (TestName, result, data))

         if result == OK:
            objMsg.printMsg('Delay Write test passed!')
         else:
            objMsg.printMsg('Delay Write test failed!')
            getSerialPortData()
            ScrCmds.raiseException(13156, 'IDT_DELAY_WRT Failed')
          
      return result       

###########################################################################################################
class CRandom_Write(CState):
   """
      Class that performs IDT_RANDOM_WRITE_TEST test. 
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)
      self.oGIO = CGIO(self.dut, params={})
   #-------------------------------------------------------------------------------------------------------
   def doRandomWrite(self, TestType, NumWrites):
      ScrCmds.insertHeader("IDT_RANDOM_WRITE_TEST",headChar='#')
      data = {}
      result = OK
      TestName = ('Random Write')                       # Test Name for file formatting
      self.testName = ('%s %s' % (TestType,TestName))
      oSerial = serialScreen.sptDiagCmds()

      # Setup Parameters
      Min_Sect_Cnt = 2048
      Max_Sect_Cnt = 2048
      Min_LBA = 0
      Max_LBA = self.dut.driveattr['Max LBA'] - Max_Sect_Cnt
      objMsg.printMsg("##### Random write at 10% OD #####")
      self.oGIO.powerCycle()
      RanMin_LBA = 0
      RanMax_LBA = int (Max_LBA * 0.10)
      self.sectorCount = Max_Sect_Cnt
      self.numBlocks = NumWrites
      objMsg.printMsg('Min LBA=%d Max LBA=%d Sector Count=%d Num Writes=%d' % (RanMin_LBA, RanMax_LBA, Max_Sect_Cnt, NumWrites))
      
      objMsg.printMsg('%s Clear Buffers, Fill Random Data' % self.testName)
      ICmd.ClearBinBuff()
      #Rosewood MQM do random write with non-zero unique pattern
      self.pattern = '7777'
      ICmd.FillBuffer(1,0,'7777')
      Retry = 1
      for loop in range(Retry+1):
         objMsg.printMsg("MC before Random write")
         oSerial.GetCtrl_A()
         
         try:
            data = ICmd.RandomWriteDMAExt(RanMin_LBA, RanMax_LBA, Min_Sect_Cnt, Max_Sect_Cnt, NumWrites)
         except:
            objMsg.printMsg("Random write at OD fail, Do not fail the drive and skip the following LDST") #RW1D Core team request to salvage yield loss
            result = SKIP
            return result

         objMsg.printMsg("MC after Random write")
         oSerial.GetCtrl_A()
         
         result = data['LLRET']
         if result == OK:
            getSerialPortData()
            objMsg.printMsg("%s RandomWrite Passed - Data: %s" % (self.testName, data))
            break

      objMsg.printMsg("##### Random write at 10% ID #####")
      self.oGIO.powerCycle()

      RanMin_LBA = int (Max_LBA * 0.90)
      RanMax_LBA = int (Max_LBA * 1.00)
      
      self.sectorCount = Max_Sect_Cnt
      self.numBlocks = NumWrites
      objMsg.printMsg('Min LBA=%d Max LBA=%d Sector Count=%d Num Writes=%d' % (RanMin_LBA, RanMax_LBA, Max_Sect_Cnt, NumWrites))
      
      objMsg.printMsg('%s Clear Buffers, Fill Random Data' % self.testName)
      ICmd.ClearBinBuff()

      #Rosewood MQM do random write with non-zero unique pattern
      self.pattern = '7777'
      ICmd.FillBuffer(1,0,'7777')

      Retry = 1
      for loop in range(Retry+1):
         objMsg.printMsg("MC before Random write")
         oSerial.GetCtrl_A()

         try:
            data = ICmd.RandomWriteDMAExt(RanMin_LBA, RanMax_LBA, Min_Sect_Cnt, Max_Sect_Cnt, NumWrites)
         except:
            objMsg.printMsg("Random write at ID fail, Do not fail the drive and skip the following LDST") #RW1D Core team request to salvage yield loss
            result = SKIP
            return result

         objMsg.printMsg("MC after Random write")
         oSerial.GetCtrl_A()

         result = data['LLRET']
         if result == OK:
            getSerialPortData()
            objMsg.printMsg("%s RandomWrite Passed - Data: %s" % (self.testName, data))
            break

      return result   
###########################################################################################################
class CRandom_Read(CState):
   """
      Class that performs IDT_RANDOM_READ_TEST test. 
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)
      self.oGIO = CGIO(self.dut, params={})
   #-------------------------------------------------------------------------------------------------------
   def doRandomRead(self, TestType, NumWrites):
      ScrCmds.insertHeader("IDT_RANDOM_READ_TEST",headChar='#')
      data = {}
      result = OK
      TestName = ('Random Read')                       # Test Name for file formatting
      self.testName = ('%s %s' % (TestType,TestName))
      

      self.oGIO.powerCycle()
      # Setup Parameters
      Min_LBA = 0
      Max_LBA = self.dut.driveattr['Max LBA'] - 256
      Min_Sect_Cnt = 256
      Max_Sect_Cnt = 256
      BlockSize = 512
      
      if testSwitch.KARNAK:     # As requested by LeongCheng, use MD area and reduced loops
         NumWrites = 200000
         Min_LBA = int(Max_LBA * 0.33)
         Max_LBA = int(Max_LBA * 0.66)
      

      self.sectorCount = Max_Sect_Cnt
      self.numBlocks = NumWrites
      
      objMsg.printMsg('%s Flush Cache, Clear Buffers, Fill Random Data' % self.testName)
      ICmd.ClearBinBuff()

      if TestType == 'MQM':
         self.pattern = '0000'
         ICmd.FillBuffer(1,0,'0000')
      else:
         self.pattern = 'RANDOM'
         ICmd.FillBuffRandom()

      Retry = 1
      for loop in range(Retry+1):
         #data = ICmd.RandomReadDMAExt(Min_LBA, Max_LBA, Min_Sect_Cnt, Max_Sect_Cnt, NumWrites)         

         #CL1052044 changes from 1hr random read to random read by NumWrites. Revert change to run 1hr of random read in MQM2
         self.oSerial = serialScreen.sptDiagCmds()
         if int(self.dut.DRV_SECTOR_SIZE) == 4096:
            Min_LBA = (Min_LBA + self.dut.driveattr['MC Offset'])/8
            Max_LBA = ICmd.GetLBACeil(Max_LBA)
         if testSwitch.SMRPRODUCT: 
            try:
               self.oSerial.randLBAs(startLBA = Min_LBA, endLBA = Max_LBA, duration = 60)  # emulate 1 hr of random read 
               data = PASS_RETURN
            except:
               data = FAIL_RETURN

         result = data['LLRET']
         if result == OK:
            getSerialPortData()
            objMsg.printMsg("%s RandomRead Passed - Data: %s" % (self.testName, data))
            break
         else:
            objMsg.printMsg("%s RandomRead Failed - Data: %s" % (self.testName, data))
            
      if result == OK:
         objMsg.printMsg('%s Test Passed' % self.testName)         
      else:
         objMsg.printMsg('%s Failed Result=%s Data=%s' % (self.testName, result, data))
         getSerialPortData()
         ScrCmds.raiseException(13086,'IDT_RANDOM_READ_TEST Failed')
      
      return result

###########################################################################################################
class CRead_ZeroCompare(CState):
   """
      Class that performs IDT_READ_ZERO_COMPARE test. 
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)
      self.oGIO = CGIO(self.dut, params={})
   #-------------------------------------------------------------------------------------------------------
   def doReadZeroCompare(self, TestType, NumLBA):
      ScrCmds.insertHeader("IDT_READ_ZERO_COMPARE",headChar='#')
      data = {}
      result = OK
      TestName = ('Read Zero Compare')                       # Test Name for file formatting
      self.testName = ('%s %s' % (TestType,TestName))

      self.oGIO.powerCycle()
      Pattern = 0x00
      SectCount = 256
      CompFlag = 1

      StartLBA = 0
      if NumLBA == ('MaxLBA'):
         EndLBA = self.dut.driveattr['Max LBA'] - 1
      else:
         EndLBA = (NumLBA)
      
      self.sectorCount = SectCount
      self.numBlocks = EndLBA/SectCount
      objMsg.printMsg('%s Start LBA=%d End LBA=%d Sector Count=%d Pattern=0x%2X' % \
                     (TestName, StartLBA, EndLBA, SectCount, Pattern))

      ICmd.ClearBinBuff()
      data = ICmd.SequentialReadDMAExt(StartLBA, EndLBA, SectCount, SectCount, 0, CompFlag)
      result = data['LLRET']
      if result != OK:
         objMsg.printMsg("%s SequentialRead Failed - Data: %s" % (self.testName, data))
      else:
         objMsg.printMsg("%s SequentialRead Passed - Data: %s" % (self.testName, data))
      
      if result == OK or testSwitch.virtualRun:
         objMsg.printMsg('%s Test Passed' % self.testName)         
      else:
         objMsg.printMsg('%s Failed Result=%s Data=%s' % (self.testName, result, data))
         getSerialPortData()
         ScrCmds.raiseException(13099,'IDT_READ_ZERO_COMPARE Failed')
      
      return result

   #---------------------------------------------------------------------------------------------------------#
   def doReadZeroCompareGuard(self, TestType='MQM', LBABand = 20971520):
      ScrCmds.insertHeader("IDT_READ_ZERO_COMPARE",headChar='#')
      data = {}
      result = OK
      TestName = ('Read Zero Compare')                       # Test Name for file formatting
      self.testName = ('%s %s' % (TestType,TestName))

      self.oGIO.powerCycle()
      Pattern = 0x00
      SectCount = 256
      CompFlag = 1

      ODStartLBA = 0
      ODEndLBA = ODStartLBA + LBABand
      IDStartLBA = self.dut.driveattr['Max LBA'] - LBABand
      IDEndLBA = self.dut.driveattr['Max LBA'] - 1
      TotalLBA = 2 * LBABand       
      
      self.pattern = Pattern
      self.sectorCount = SectCount
      
      ICmd.ClearBinBuff()
      if result == OK:
         objMsg.printMsg('%s ReadOD ODStartLBA=%d ODEndLBA=%d SectCount=%d Pattern=0x%2X' % \
                        (self.testName, ODStartLBA, ODEndLBA, SectCount, Pattern)) 
         data = ICmd.SequentialReadDMAExt(ODStartLBA, ODEndLBA, SectCount, SectCount, 0, CompFlag)
         result = data['LLRET']
      if result == OK:   
         objMsg.printMsg('%s ReadID IDStartLBA=%d IDEndLBA=%d SectCount=%d Pattern=0x%2X' % \
                        (self.testName, IDStartLBA, IDEndLBA, SectCount, Pattern)) 
         data = ICmd.SequentialReadDMAExt(IDStartLBA, IDEndLBA, SectCount, SectCount, 0, CompFlag)
         result = data['LLRET']

      if result != OK:
         objMsg.printMsg("%s SequentialReadDMA Failed - Data: %s" % (self.testName, data))
      else:
         objMsg.printMsg("%s SequentialReadDMA Passed - Data: %s" % (self.testName, data))
            
      if result == OK or testSwitch.virtualRun:
         objMsg.printMsg('%s Test Passed' % self.testName)         
      else:
         objMsg.printMsg('%s Failed Result=%s Data=%s' % (self.testName, result, data))
         getSerialPortData()
         ScrCmds.raiseException(13099,'IDT_READ_ZERO_COMPARE Failed')
      
      return result

###########################################################################################################
class CWritePattern(CState):
   """
      Class that performs IDT_WRITE_PATTERN test. 
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)
      self.oGIO = CGIO(self.dut, params={})
   #-------------------------------------------------------------------------------------------------------
   def doWritePattern(self, TestType, Pattern, StartLBA, EndLBA):
      ScrCmds.insertHeader("IDT_WRITE_PATTERN",headChar='#')
      data = {}
      result = OK
      TestName = ('Write Pattern')                       # Test Name for file formatting
      self.testName = ('%s %s' % (TestType,TestName))

      self.oGIO.powerCycle()
      # Setup Parameters
      StepLBA = 256 
      SectCount = 256
      BlockSize = 512
      StampFlag = 0
      if EndLBA == ('MaxLBA'):
         EndLBA = self.dut.driveattr['Max LBA']
      self.pattern = Pattern
      self.sectorCount = SectCount
      self.numBlocks = (EndLBA-StartLBA)/SectCount
      objMsg.printMsg('%s Start LBA=%d End LBA=%d Sect Count=%d Pattern=0x%s' % \
                     (self.testName, StartLBA, EndLBA, SectCount, Pattern))
      
      objMsg.printMsg('%s Clear Buffers, Fill 0x%2s Data' % (self.testName, Pattern))
      ICmd.ClearBinBuff()
      ICmd.FillBuffer(WBF,0,Pattern)
      if testSwitch.virtualRun:
         data = {'IDPIOTransTime': 512, 'FDE': 8, 'IDVendorUnique52': 512, 'SATACapabilities': 34574, 'MediaCacheEnabled': 32768, 'IDCurLogicalSctrs': 63, \
         'IDSeaCosFDE': 8, 'IDLogInPhyIndex': 16384, 'IDVendorUnique9': 0, 'IDUDMASupportedMode': 127, 'IDCurLogicalHds': 16, 'IDReserved48': 16384, 'IDWorldWideName': \
         '5000C5000BA310A3', 'IDLogSectPerPhySect': 24579, 'ATASignalSpeedSupport': 34574, 'LLRET': 0, 'POIS_Enabled': 48201, 'LPS_LogEnabled': False, 'POIS_Supported': 32105, \
         'IDRWMultIntrPerSctr': 32784, 'IDReserved2': 51255, 'IDCommandSet7': 16414, 'IDCommandSet6': 16739, 'IDCommandSet5': 48201, 'IDCurLogicalCyls': 16383, 'IDCommandSet3': 16739, \
         'IDLogicalSctrs': 63, 'IDCommandSet1': 29803, 'LogToPhysSectorSize': 24579, 'IDAddSupported': 0, 'IDSATACapabilities': 34574, 'IDCommandSet2': 32105, 'IDVendorUnique7': 0, \
         'IDModel': 'ST720XX028-1KK162', 'IDMediaCacheEnabled': 32768, 'IDLogicalHeads': 16, 'IDATAATAPIMinorVer': 31, 'IDSeaCOSCmdsSupport': 8, 'IDHardwareResetRes': 0, \
         'IDMultipleSctrs': 272, 'IDLogicalCyls': 16383, 'IDVendorUnique8': 0, 'DrivePairing': 0, 'SCTBIST_Supported': 12341, 'IDFirmwareRev': '0001', 'IDConfiguration': 3162, \
         'IDReserved50': 16384, 'LogicalSectorSize': 0, 'IDObsolete5': 0, 'IDObsolete4': 0, 'IDQDepth': 31, 'IDRWLongVendorBytes': 0, 'IDCurParmsValid': 7, 'IDCommandSet4': 29801, \
         'IDSerialNumber': 'Q6700ADH', 'IDCurLBAs': 16514064, 'ATA_SignalSpeed': 0, 'MediaCacheSupport': 12341, 'IDDefaultLBAs': 268435455, 'IDATAATAPIMajorVer': 1008, \
         'IDCapabilities': 12032, 'IDReserved243': 3, 'IDObsolete20': 0, 'IDObsolete21': 16384, 'IDReserved159': 32768, 'RMW_LogEnabled': False, 'IDCurrAPMValue': 32896, \
         'IDDefault48bitLBAs': 1406544048}
      else:                          
         data = ICmd.SequentialWriteDMAExt(StartLBA, EndLBA, StepLBA, SectCount)
      result = data['LLRET']
      if result == OK:
         getSerialPortData()
         objMsg.printMsg("%s SequentialWrite Passed - Data: %s" % (self.testName, data))
      else:
         objMsg.printMsg("%s SequentialWrite Failed - Data: %s" % (self.testName, data))
      
      if result == OK:
         objMsg.printMsg('%s Test Passed' % self.testName)
      else:
         objMsg.printMsg('%s Failed Result=%s Data=%s' % (self.testName, result, data))
         getSerialPortData()
         ScrCmds.raiseException(13080,'IDT_WRITE_PATTERN Failed')
      
      return result

###########################################################################################################
class CODTATI(CState):
   """
      Class that performs IDT_ODTATI_TEST test. 
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)
      self.oGIO = CGIO(self.dut, params={})
   #-----------------------------------------------------------------------------------------#
   def doODTATI(self, TestType):
      ScrCmds.insertHeader("IDT_ODTATI_TEST",headChar='#')
      data = {}
      result = OK
      DoRetry = OFF
    
      TestName = ('ODT ATI Test')                       # Test Name for file formatting
      self.testName = ('%s %s' % (TestType,TestName))

      self.oGIO.powerCycle()
      if result == OK:
         data = {}
         Pattern = '1234'  
         SectCount = 256
         CompareFlag = 0
         CmdLoop = 2500 # loop 2x
         if testSwitch.SMR:         # ATI capability at slim track can be as low as 50 according to RSS.
            CmdLoop = 50
         UDMA_Speed = 0x45
   
         TestLoop = 50
         StartLBA = 0
         EndLBA = 400
         InterLoop = 2
         MaxLBA = self.dut.driveattr['Max LBA'] 
         StepLBA = MaxLBA/400

         BlockSize = 512
         CmdTime = 0

         objMsg.printMsg('%s Start LBA=%d End LBA=%d Sect Count=%d Pattern=%s' % \
                        (TestName, StartLBA, EndLBA, SectCount, Pattern))
         
         ICmd.ClearBinBuff()
         ICmd.FillBuffer(1,0,Pattern)

         for loop in range (0, TestLoop/2, 1):
            for cnt in range(InterLoop):
               if result == OK:
                  StartLBA = loop * StepLBA
                  objMsg.printMsg('%d write on 400 LBA starting %d' % (CmdLoop, StartLBA))                           
                  EndLBA = StartLBA + 400
                  
               if result == OK:
                  objMsg.printMsg('%d write location(%d) adjusted from start=%d to end=%d' % (CmdLoop, loop+1, StartLBA, EndLBA))
                  data = ICmd.SequentialCmdLoop(0x35,StartLBA,EndLBA,SectCount,SectCount,CmdLoop,1)
                  result = data['LLRET']
                  if result != OK:
                     objMsg.printMsg('SequentialCmdLoop failed at loop %d, result=%s' % (TestLoop,data))
                     break
                     
               if result == OK:
                  StartLBA = (loop+TestLoop/2) * StepLBA
                  objMsg.printMsg('%d write on 400 LBA starting %d' % (CmdLoop, StartLBA))
                  EndLBA = StartLBA + 400
                      
               if result == OK:
                  objMsg.printMsg('%d write location(%d) adjusted from start=%d to end=%d' % (CmdLoop, loop+1, StartLBA, EndLBA))
                  data = ICmd.SequentialCmdLoop(0x35,StartLBA,EndLBA,SectCount,SectCount,CmdLoop,1)
                  result = data['LLRET']
                  if result != OK:
                     objMsg.printMsg('SequentialCmdLoop failed at loop %d, result=%s' % (TestLoop,data))
                     break

         if result == OK:
            Pattern = '0000'
            StartLBA = 0
            EndLBA = MaxLBA/8
            CompareFlag = 1
            objMsg.printMsg('%s Start LBA=%d End LBA=%d Sect Count=%d Pattern=%s' % \
                           (TestName, StartLBA, EndLBA, SectCount, Pattern))
            objMsg.printMsg('%s Flush Cache, Clear Buffers, Fill %s Data' % (TestName, Pattern))
            ICmd.ClearBinBuff()
            ICmd.FillBuffer(1,0,Pattern)

            objMsg.printMsg('%s Sequential Read on first eighth of the disk' % (TestName))
            data = ICmd.SequentialReadDMAExt(StartLBA, EndLBA, SectCount, SectCount)
            result = data['LLRET']
 
         if result == OK:
            objMsg.printMsg('%s Sequential Write on first eighth of the disk' % (TestName))
            data = ICmd.SequentialWriteDMAExt(StartLBA, EndLBA, SectCount, SectCount)
            result = data['LLRET']

         Retry = 0  # 1
         if result == OK:
            for loop in range(Retry+1):
               objMsg.printMsg('%s Sequential Read on first eighth of the disk with compare' % (TestName))
               data = ICmd.SequentialReadDMAExt(StartLBA, EndLBA, SectCount, SectCount, 0, CompareFlag)
               result = data['LLRET']
               if result == OK: break
        
      if result != OK:
         objMsg.printMsg('%s Failed Result=%s Data=%s' % (TestName, result, data))
         getSerialPortData()
         ScrCmds.raiseException(13050,'IDT_ODTATI_TEST Failed')

      return result

###########################################################################################################
class CWriteTestMobile(CState):
   """
      Class that performs IDT_WRITE_TEST_MOBILE test. 
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)
      self.oGIO = CGIO(self.dut, params={})
   #---------------------------------------------------------------------------------------------------------#
   def doWriteTestMobile(self, TestType, StartLBA, MidLBA, EndLBA, SectCnt, Loops):
      ScrCmds.insertHeader("IDT_WRITE_TEST_MOBILE",headChar='#')
      data = {}
      result = OK
      TestName = ('Write Mobile')                       # Test Name for file formatting
      self.testName = ('%s %s' % (TestType,TestName))
  
      self.oGIO.powerCycle()

      # Setup Parameters
      MinLBA  = 0
      Pattern = 'EEEE'
      if TestType == 'MQM':
         Pattern = '0000'
      self.pattern = Pattern
      if SectCnt > self.dut.driveattr['DiagBufferSize']: SectCnt = self.dut.driveattr['DiagBufferSize']
      self.sectorCount = SectCnt
      self.numBlocks = EndLBA/SectCnt+4*Loops
      objMsg.printMsg('%s Start LBA=%d/0x%X Mid LBA=%d/0x%X End LBA=%d/0x%X SecCnt=%d Loops=%d Pattern=%s ' % \
                     (self.testName,StartLBA,StartLBA,MidLBA,MidLBA,EndLBA,EndLBA,SectCnt,Loops,Pattern))

      Retry = 2
      for loop in range(Retry+1):
         data = ICmd.WriteTestSim2(StartLBA,MidLBA,EndLBA,MinLBA,SectCnt,Loops,Pattern)
         result = data['LLRET']
         if result == OK:
            objMsg.printMsg("%s WriteTestSim2 Passed - Data: %s" % (self.testName, data))
            break
         else:
            objMsg.printMsg("%s WriteTestSim2 Failed - Data: %s" % (self.testName, data))
      
      if result != OK:
         objMsg.printMsg('%s Failed Result=%s Data=%s' % (self.testName, result, data))
         getSerialPortData()
         ScrCmds.raiseException(13063,'IDT_WRITE_TEST_MOBILE Failed')
      else:
         objMsg.printMsg('%s Test Passed' % self.testName)
         
      return result
   
###########################################################################################################
class COS_ReadReverse(CState):
   """
      Class that performs IDT_OS_READ_REVERSE test. 
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)
      self.oGIO = CGIO(self.dut, params={})
   #---------------------------------------------------------------------------------------------------------#
   def doOSReadReverse(self, TestType, SectCnt, Gbytes):
      ScrCmds.insertHeader("IDT_OS_READ_REVERSE",headChar='#')
      data = {}
      result = OK
      TestName = ('OS Read Rev')                       # Test Name for file formatting
      self.testName = ('%s %s' % (TestType,TestName))
      
      self.oGIO.powerCycle()
      # Setup Parameters
      UDMA_Speed = 0x45 
      Pattern = 'AAAA'
      if TestType == 'MQM':
         Pattern = '0000'
      self.pattern = Pattern
      StartLBA = 0
      EndLBA = StartLBA + ((Gbytes*1000000000) / 512)
      NumLBA = EndLBA - StartLBA
      self.sectorCount = SectCnt
      objMsg.printMsg('%s Start LBA=%d End LBA=%d Sect Count=%d Num GBytes=%3.3f Pattern=%s' % \
                     (self.testName, StartLBA, EndLBA, SectCnt, (NumLBA*512/1000000000), Pattern))

      ICmd.ClearBinBuff()
      ICmd.FillBuffer(1,0,Pattern)
      
      SectCnt = 256
      Retry = 2
      for loop in range(Retry+1):
         if testSwitch.virtualRun:
            data = {'LLRET': 0, 'LBA': '0x0000000000000078', 'ERR': '0', 'RES': '', 'DEV': '64', 'SCNT': '0', 'RESULT': 'IEK_OK:No error', 'STS': '80', 'CT': '168408'}
         else:            
            data = ICmd.OSCopySim3(StartLBA,EndLBA,SectCnt,UDMA_Speed)   
         result = data['LLRET'] 
         if result == OK:
            objMsg.printMsg("%s OSCopySim3 Passed - Data: %s" % (self.testName, data))
            break
         else:
            objMsg.printMsg("%s OSCopySim3 Failed - Data: %s" % (self.testName, data))
         
      if result != OK:
         objMsg.printMsg('%s Failed Result=%s Data=%s' % (self.testName, result, data))
         getSerialPortData()
         ScrCmds.raiseException(13098,'IDT_OS_READ_REVERSE Failed')
      else:
         objMsg.printMsg('%s Test Passed' % self.testName)
         
      return result

###########################################################################################################
class CEncroachment_EUP(CState):
   """
      Class that performs IDT_ENCROACHMENT_EUP test. 
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)
      self.oGIO = CGIO(self.dut, params={})
   #---------------------------------------------------------------------------------------------------------#
   def doEncroachmentEUP(self, TestType, TestName):
      ScrCmds.insertHeader("IDT_ENCROACHMENT_EUP",headChar='#')    
      import random
      
      self.testName = ('%s %s' % (TestType, TestName))                       # Test Name for file formatting
      result = OK
      data = {}
    
      stepLBA = 3024
      sectCnt = 256
     
      if testSwitch.virtualRun:
         WrtLoop = 100
      else:   
         WrtLoop = 5000
      pattern = 'FAFA'  
      maxLBA = self.dut.driveattr['Max LBA']

      ENCROACHMENT_EUP = ON

      if ENCROACHMENT_EUP == ON:
         self.testCmdTime = 0
         self.oGIO.powerCycle()

         ICmd.ClearBinBuff()
         ICmd.FillBuffer(WBF, 0, pattern)
       
         if result == OK:         
            TotalBlks = 200000
            startLBA = 0
            maxLBA = maxLBA - 200000
            objMsg.printMsg('%s Random(StartLBA=%d MaxLBA=%d) StepLBA=%d SectCnt=%d Pattern=%s WrtLoop=%d TotalBlks=%d' % \
                              (TestName, startLBA, maxLBA, stepLBA, sectCnt, pattern ,WrtLoop ,TotalBlks))                
            data = ICmd.SequentialWriteDMAExt_EUP(startLBA, maxLBA, stepLBA, sectCnt,WrtLoop,TotalBlks)
            result = data['LLRET']
            if result != OK: 
               objMsg.printMsg('%s SeqWrite_EUP failed. Result=%s Data=%s' % (TestName, result, data))
                         
          
            if result == OK:
               objMsg.printMsg('%s Flush Cache, Clear Buffers, Fill %s Data' % (TestName, pattern))
               ICmd.ClearBinBuff(RBF)
               startLBA = 0
               endLBA = maxLBA - 200000
               stepLBA = sectCnt
               stampFlag = 0
               compFlag = 0   # can not do compare. cause pattern is only written to random locations.
               data = ICmd.SequentialReadDMAExt(startLBA, endLBA, stepLBA, sectCnt, stampFlag, compFlag)
               result = data['LLRET']
               objMsg.printMsg('%s SeqRead Data=%s Result=%s' % (TestName, data, result))
  
            if result == OK:
               objMsg.printMsg('%s Test passed!' % TestName)  
            else:
               objMsg.printMsg('%s Test failed!' % TestName)  
               getSerialPortData()
               ScrCmds.raiseException(13158,'IDT_ENCROACHMENT_EUP Failed')

      return result

###########################################################################################################
class CBeatupWrRd(CState):
   """
      Class that performs Beatup Write Read test. 
      Beat up at these two Host LBA range:
      Range 1 (in dec) : 70000000*8 to 140000000*8
      Range 2 (in dec) : 200000000*8 to 230000000*8
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)
      self.oGIO = CGIO(self.dut, params={})
   #---------------------------------------------------------------------------------------------------------#
   def doWriteRead(self,):

      ScrCmds.insertHeader("IDT_BEATUP_WRITE_READ",headChar='#')   

      maxLBA = int(ICmd.GetMaxLBA()['MAX48'],16)-1
      drvCap = (maxLBA * 512)/(10**9)
      objMsg.printMsg("maxLBA: %s drvCap: %s GB" % (maxLBA, drvCap))
      if drvCap <= 500:
         objMsg.printMsg("Drive capacity is <= 500 GB. Skip beatup test")
         return

      data = {}
      result = OK
      self.oGIO.powerCycle()
      import math
      MDStartLBA = min(560000000, maxLBA)
      MDEndLBA = min(1120000000, maxLBA)
      IDStartLBA = min(1600000000, maxLBA)
      IDEndLBA = min(1840000000, maxLBA)
      loop = 1

      StepLBA = 256 
      SectCount = 256
      StampFlag = 0
      BlockSize = 512
       
      for iter in range(loop):
         objMsg.printMsg("Loop num %s" % (iter+1))
         if iter == 0:
            objMsg.printMsg("### Beatup first loop with unique pattern 0xaaaa ###")
            self.Pattern = 'aaaa'
         elif iter == 1:
            objMsg.printMsg("### Beatup second loop with unique pattern 0x5555 ###")
            self.Pattern = '5555'
         ICmd.ClearBinBuff() 
         ICmd.FillBuffer(1,0, self.Pattern)

         if testSwitch.virtualRun:
            data = {'IDPIOTransTime': 512, 'FDE': 8, 'IDVendorUnique52': 512, 'SATACapabilities': 34574, 'MediaCacheEnabled': 32768, 'IDCurLogicalSctrs': 63, \
            'IDSeaCosFDE': 8, 'IDLogInPhyIndex': 16384, 'IDVendorUnique9': 0, 'IDUDMASupportedMode': 127, 'IDCurLogicalHds': 16, 'IDReserved48': 16384, 'IDWorldWideName': \
            '5000C5000BA310A3', 'IDLogSectPerPhySect': 24579, 'ATASignalSpeedSupport': 34574, 'LLRET': 0, 'POIS_Enabled': 48201, 'LPS_LogEnabled': False, 'POIS_Supported': 32105, \
            'IDRWMultIntrPerSctr': 32784, 'IDReserved2': 51255, 'IDCommandSet7': 16414, 'IDCommandSet6': 16739, 'IDCommandSet5': 48201, 'IDCurLogicalCyls': 16383, \
            'IDCommandSet3': 16739, 'IDLogicalSctrs': 63, 'IDCommandSet1': 29803, 'LogToPhysSectorSize': 24579, 'IDAddSupported': 0, 'IDSATACapabilities': 34574, \
            'IDCommandSet2': 32105, 'IDVendorUnique7': 0, 'IDModel': 'ST720XX028-1KK162', 'IDMediaCacheEnabled': 32768, 'IDLogicalHeads': 16, 'IDATAATAPIMinorVer': 31, \
            'IDSeaCOSCmdsSupport': 8, 'IDHardwareResetRes': 0, 'IDMultipleSctrs': 272, 'IDLogicalCyls': 16383, 'IDVendorUnique8': 0, 'DrivePairing': 0, 'SCTBIST_Supported': 12341, \
            'IDFirmwareRev': '0001', 'IDConfiguration': 3162, 'IDReserved50': 16384, 'LogicalSectorSize': 0, 'IDObsolete5': 0, 'IDObsolete4': 0, 'IDQDepth': 31, 'IDRWLongVendorBytes': 0, \
            'IDCurParmsValid': 7, 'IDCommandSet4': 29801, 'IDSerialNumber': 'Q6700ADH', 'IDCurLBAs': 16514064, 'ATA_SignalSpeed': 0, 'MediaCacheSupport': 12341, 'IDDefaultLBAs': 268435455, \
            'IDATAATAPIMajorVer': 1008, 'IDCapabilities': 12032, 'IDReserved243': 3, 'IDObsolete20': 0, 'IDObsolete21': 16384, 'IDReserved159': 32768, 'RMW_LogEnabled': False, \
            'IDCurrAPMValue': 32896, 'IDDefault48bitLBAs': 1406544048}
         else:
            #RW7-1D Version 2.3
            self.SeqPatternWr(MDStartLBA, MDEndLBA, StepLBA, SectCount)
            self.SeqPatternWr(IDStartLBA, IDEndLBA, StepLBA, SectCount)

            #self.SeqPatternRd(MDStartLBA, MDEndLBA, StepLBA, SectCount)
            #self.SeqPatternRd(IDStartLBA, IDEndLBA, StepLBA, SectCount)
      
      return

   #---------------------------------------------------------------------------------------------------------#
   def SeqPatternWr(self, StartLBA, EndLBA, StepLBA, SectCount):
      objMsg.printMsg('Seq Pattern Write Host Start LBA=%d End Host LBA=%d Sect Count=%d Pattern=%s' % (StartLBA, EndLBA, SectCount, self.Pattern))
      data = ICmd.SequentialWriteDMAExt(StartLBA, EndLBA, StepLBA, SectCount)
      result = data['LLRET']
      if result == OK:
         getSerialPortData()
         objMsg.printMsg("SequentialWrite Passed - Data: %s" % (data,))
         return
      else:
         objMsg.printMsg("SequentialWrite Failed - Data: %s" % (data,))
         getSerialPortData()
         ScrCmds.raiseException(13351,'IDT_BEATUP_WRITE_READ Failed')

   #---------------------------------------------------------------------------------------------------------#
   def SeqPatternRd(self, StartLBA, EndLBA, StepLBA, SectCount):
      objMsg.printMsg('Seq Read Start Host LBA=%d End Host LBA=%d Sect Count=%d' % (StartLBA, EndLBA, SectCount))
      data = ICmd.SequentialReadDMAExt(StartLBA, EndLBA, StepLBA, SectCount)
      result = data['LLRET']
      if result == OK:
         getSerialPortData()
         objMsg.printMsg("SequentialRead Passed - Data: %s" % (data,))
         return
      else:
         objMsg.printMsg("SequentialRead Failed - Data: %s" % (data,))
         getSerialPortData()
         ScrCmds.raiseException(13351,'IDT_BEATUP_WRITE_READ Failed')

###########################################################################################################
class CWriteDriveZero(CState):
   """
      Class that performs IDT_WRITE_DRIVE_ZERO test. 
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)
      self.oGIO = CGIO(self.dut, params={})
   #---------------------------------------------------------------------------------------------------------#
   def doWriteZeroPatt(self, TestType, NumLBA):
      ScrCmds.insertHeader("IDT_WRITE_DRIVE_ZERO",headChar='#')    
      data = {}
      result = OK
      TestName = ('Write Zero Patt')                       # Test Name for file formatting
      self.testName = ('%s %s' % (TestType,TestName))

      self.oGIO.powerCycle()
      objMsg.printMsg("Tighten Servo CTF cmd and wr/rd retry level before full pack write")
      # Tighten Servo CTF cmd
      sptCmds.gotoLevel('7')
      sptCmds.sendDiagCmd("s1,4D,C088", printResult = True)
      sptCmds.sendDiagCmd("t1,4D", printResult = True)

      # Tighten retry level
      self.oGIO.Y2TighterRetry()
      # Setup Parameters
      Pattern = '0000'
      StepLBA = 256 
      SectCount = 256
      StampFlag = 0
      StartLBA = 0
      BlockSize = 512
      if NumLBA == ('MaxLBA'):
         EndLBA = self.dut.driveattr['Max LBA'] - 1
      else: EndLBA = NumLBA
      self.pattern = Pattern
      self.sectorCount = SectCount
	  
      G2P_Merge = True
      NumZones = 1 #default is full pack write with single zone
      if G2P_Merge: #Overcome drive buffer overflow with smaller zone size
         NumZones = 10
      ZoneSize = EndLBA / NumZones
      objMsg.printMsg("ZoneSize = %d" % (ZoneSize,))
      for i in range(NumZones):
         zStartLBA = i * ZoneSize
         zEndLBA = zStartLBA + ZoneSize - 1
         if i == NumZones - 1: #last zone covers all remaining LBAs
            zEndLBA = EndLBA

         objMsg.printMsg("ZoneNum=%s, zStartLBA=%d zEndLBA=%d Sect Count=%d Pattern=%s" % \
						 (i, zStartLBA, zEndLBA, SectCount, Pattern))
         ICmd.ClearBinBuff() 
         ICmd.FillBuffer(1,0,Pattern)
               
         Retry = 1
         for loop in range(Retry+1):
            if testSwitch.virtualRun:
               data = {'IDPIOTransTime': 512, 'FDE': 8, 'IDVendorUnique52': 512, 'SATACapabilities': 34574, 'MediaCacheEnabled': 32768, 'IDCurLogicalSctrs': 63, \
			   'IDSeaCosFDE': 8, 'IDLogInPhyIndex': 16384, 'IDVendorUnique9': 0, 'IDUDMASupportedMode': 127, 'IDCurLogicalHds': 16, 'IDReserved48': 16384, 'IDWorldWideName': \
			   '5000C5000BA310A3', 'IDLogSectPerPhySect': 24579, 'ATASignalSpeedSupport': 34574, 'LLRET': 0, 'POIS_Enabled': 48201, 'LPS_LogEnabled': False, 'POIS_Supported': 32105, \
			   'IDRWMultIntrPerSctr': 32784, 'IDReserved2': 51255, 'IDCommandSet7': 16414, 'IDCommandSet6': 16739, 'IDCommandSet5': 48201, 'IDCurLogicalCyls': 16383, \
			   'IDCommandSet3': 16739, 'IDLogicalSctrs': 63, 'IDCommandSet1': 29803, 'LogToPhysSectorSize': 24579, 'IDAddSupported': 0, 'IDSATACapabilities': 34574, \
			   'IDCommandSet2': 32105, 'IDVendorUnique7': 0, 'IDModel': 'ST720XX028-1KK162', 'IDMediaCacheEnabled': 32768, 'IDLogicalHeads': 16, 'IDATAATAPIMinorVer': 31, \
			   'IDSeaCOSCmdsSupport': 8, 'IDHardwareResetRes': 0, 'IDMultipleSctrs': 272, 'IDLogicalCyls': 16383, 'IDVendorUnique8': 0, 'DrivePairing': 0, 'SCTBIST_Supported': 12341, \
			   'IDFirmwareRev': '0001', 'IDConfiguration': 3162, 'IDReserved50': 16384, 'LogicalSectorSize': 0, 'IDObsolete5': 0, 'IDObsolete4': 0, 'IDQDepth': 31, 'IDRWLongVendorBytes': 0, \
			   'IDCurParmsValid': 7, 'IDCommandSet4': 29801, 'IDSerialNumber': 'Q6700ADH', 'IDCurLBAs': 16514064, 'ATA_SignalSpeed': 0, 'MediaCacheSupport': 12341, 'IDDefaultLBAs': 268435455, \
			   'IDATAATAPIMajorVer': 1008, 'IDCapabilities': 12032, 'IDReserved243': 3, 'IDObsolete20': 0, 'IDObsolete21': 16384, 'IDReserved159': 32768, 'RMW_LogEnabled': False, \
			   'IDCurrAPMValue': 32896, 'IDDefault48bitLBAs': 1406544048}
            else:
               # Seq write logical zone
               data = ICmd.SequentialWriteDMAExt(zStartLBA, zEndLBA, StepLBA, SectCount, G2P_Merge = G2P_Merge)
               if data['LLRET'] == 'WRAGAIN': #After G2P merge, write the current logical zone again
                  objMsg.printMsg("Relax Servo CTF cmd and wr/rd retry before post-G2P-merged write pass")
                  # Relax Servo CTF cmd
                  sptCmds.gotoLevel('7')
                  sptCmds.sendDiagCmd("s1,4D,C048", printResult = True)
                  sptCmds.sendDiagCmd("t1,4D", printResult = True)

                  # Relax retry level
                  self.oGIO.Y2Retry()#During G2P merge, retry level has been tighten
                  
                  objMsg.printMsg("Post-G2P-merged, write pass the current logical zone")
                  ICmd.ClearBinBuff() 
                  ICmd.FillBuffer(1,0,Pattern)
                  data = ICmd.SequentialWriteDMAExt(zStartLBA, zEndLBA, StepLBA, SectCount, G2P_Merge = False)

                  objMsg.printMsg("Tighten Servo CTF cmd and wr/read retry after post-G2P-merged write pass")
                  # Tighten Servo CTF cmd
                  sptCmds.gotoLevel('7')
                  sptCmds.sendDiagCmd("s1,4D,C088", printResult = True)
                  sptCmds.sendDiagCmd("t1,4D", printResult = True)

                  # Tighten retry level
                  self.oGIO.Y2TighterRetry()

               result = data['LLRET']
            if result == OK:
               objMsg.printMsg("SeqWrite at ZoneNum %s Passed. Data: %s" % (i, data))
               break
            else:
               objMsg.printMsg("SeqWrite at ZoneNum %s Failed - Data: %s" % (i, data))

      objMsg.printMsg("Relax Servo CTF cmd and wr/rd retry level after full pack write")
      # Relax Servo CTF cmd
      sptCmds.gotoLevel('7')
      sptCmds.sendDiagCmd("s1,4D,C048", printResult = True)
      sptCmds.sendDiagCmd("t1,4D", printResult = True)

      # Relax retry level
      self.oGIO.Y2Retry()
      if result == OK:
         objMsg.printMsg('%s Test Passed' % self.testName)         
      else:
         objMsg.printMsg('%s Failed Result=%s Data=%s' % (self.testName, result, data))
         getSerialPortData()
         ScrCmds.raiseException(13091,'IDT_WRITE_DRIVE_ZERO Failed')
      
      return result

###########################################################################################################
class CLowDutyRead(CState):
   """
      Class that performs IDT_LOW_DUTY_CYCLE test. 
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)
      self.oGIO = CGIO(self.dut, params={})
   #---------------------------------------------------------------------------------------------------------#
   def doLowDutyCycle(self, TestType, StartLBA, MidLBA, EndLBA, Loops, SectCnt, Delay):
      ScrCmds.insertHeader("IDT_LOW_DUTY_CYCLE",headChar='#')    
      data = {}
      result = OK
      DoRetry = OFF
      TestName = ('Low Duty Cycle')                       # Test Name for file formatting
      self.testName = ('%s %s' % (TestType,TestName))
      
      self.oGIO.powerCycle()
      # Setup Parameters  
      Pattern = '9999'  
      if TestType == 'MQM':
         Pattern = '0000'
      self.pattern = Pattern
      self.sectorCount = SectCnt
      objMsg.printMsg('%s StartLBA=%d/0x%X MidLBA=%d/0x%X EndLBA=%d/0x%X' % \
                     (self.testName, StartLBA, StartLBA, MidLBA, MidLBA, EndLBA, EndLBA))
      objMsg.printMsg('%s Loops=%d SectCnt=%d Pattern=%s Delay=%1.1f' % \
                     (self.testName, Loops, SectCnt, Pattern, Delay))
      
      Retry = 2
      for loop in range(Retry+1):
         if testSwitch.virtualRun:
            data = {'LLRET': 0, 'LBA': '0x0000000000002711', 'CNT': '100', 'ERR': '0', 'RES': '', 'DEV': '64', 'SCNT': '0', 'RESULT': 'IEK_OK:No error', 'STS': '80', 'CT': '328174'}
         else:            
            data = ICmd.LowDutyRead(StartLBA,EndLBA,StartLBA,StartLBA,EndLBA,SectCnt,Loops,Pattern,(Delay*1000)) 
         result = data['LLRET'] 
         if result == OK:
            objMsg.printMsg("%s LowDutyRead Passed - Data: %s" % (self.testName, data))
            break
         else:
            objMsg.printMsg("%s LowDutyRead Failed - Data: %s" % (self.testName, data))
      
      if result != OK:
         objMsg.printMsg('%s Failed Result=%s Data=%s' % (self.testName, result, data))
         getSerialPortData()
         ScrCmds.raiseException(13075,'IDT_LOW_DUTY_CYCLE Failed')
      else:
         objMsg.printMsg('%s Test Passed' % self.testName)
         
      return result
   
###########################################################################################################
class COSWriteTest(CState):
   """
      Class that performs IDT_OS_WRITE_TEST test. 
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)
      self.oGIO = CGIO(self.dut, params={})
   #---------------------------------------------------------------------------------------------------------#
   def doOSWriteDrive(self, TestType, SectCnt, Gbytes):
      ScrCmds.insertHeader("IDT_OS_WRITE_TEST",headChar='#')    
      data = {}
      result = OK
      TestName = ('OS Write Test')                       # Test Name for file formatting
      self.testName = ('%s %s' % (TestType,TestName))
      
      self.oGIO.powerCycle()
      # Setup Parameters  
      UDMA_Speed = 0x45
      Pattern = 'BBBB'
      if TestType == 'MQM':
         Pattern = '0000'
      self.pattern = Pattern
      StartLBA = 0
      EndLBA = StartLBA + ((Gbytes*1000000000) / 512)
      NumLBA = EndLBA - StartLBA
      self.sectorCount = SectCnt
      objMsg.printMsg('%s Start LBA=%d End LBA=%d Sect Count=%d Num GBytes=%3.3f Pattern=%s' % \
                     (self.testName, StartLBA, EndLBA, SectCnt, (NumLBA*512/1000000000), Pattern))

      objMsg.printMsg('%s Clear Buffers, Fill %s Data' % (self.testName, Pattern))

      SectCnt = 256
      Retry = 2
      for loop in range(Retry+1):
         if testSwitch.virtualRun:
            data = {'LLRET': 0, 'LBA': '0x00000000009502F9', 'CNT': '1', 'ERR': '0', 'RES': '', 'DEV': '64', 'SCNT': '0', 'RESULT': 'IEK_OK:No error', 'STS': '80', 'CT': '81726'}
         else:            
            data = ICmd.OSCopySim1(StartLBA,EndLBA,SectCnt,Pattern)
         result = data['LLRET'] 
         if result == OK:
            objMsg.printMsg("%s OSCopySim1 Passed - Data: %s" % (self.testName, data))
            break
         else:
            objMsg.printMsg("%s OSCopySim1 Failed - Data: %s" % (self.testName, data))
      
      if result != OK:
         objMsg.printMsg('%s Failed Result=%s Data=%s' % (self.testName, result, data))         
         getSerialPortData()
         ScrCmds.raiseException(13076,'IDT_OS_WRITE_TEST Failed')
      else:
         objMsg.printMsg('%s Test Passed' % self.testName)
         
      return result
    
###########################################################################################################
class CVoltageHighLow(CState):
   """
      Class that performs IDT_VOLTAGE_HIGH_LOW test. 
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)
      self.oGIO = CGIO(self.dut, params={})
   #---------------------------------------------------------------------------------------------------------#
   def doVoltageHighLow(self, TestType, loops):
      ScrCmds.insertHeader("IDT_VOLTAGE_HIGH_LOW",headChar='#')    
      ready_time = 0
      result = OK
      TestName = ('Volts High Low')                       # Test Name for file formatting
      self.testName = ('%s %s' % (TestType,TestName))
      
      # Setup Parameters
      nominal_5v   = 5000
      nominal_12v  = 12000
      margin_5v    = TP.prm_GIOSettings['IDT 5vMargin']            # -1(off), 0.0(no margin)
      margin_12v   = TP.prm_GIOSettings['IDT 12vMargin']           # 0.10(10%), 0.05(5%)
      
      if margin_5v  == -1:
         nominal_5v,  high_5v,  low_5v  = 0.0
      else:
         high_5v      = nominal_5v  + (nominal_5v  * margin_5v)
         low_5v       = nominal_5v  - (nominal_5v  * margin_5v)
      if margin_12v == -1:
         nominal_12v, high_12v, low_12v = 0.0
      else:
         high_12v     = nominal_12v + (nominal_12v * margin_12v)
         low_12v      = nominal_12v - (nominal_12v * margin_12v)
      
      f_nom_5v=nominal_5v/1000;   f_high_5v=high_5v/1000;   f_low_5v=low_5v/1000
      f_nom_12v=nominal_12v/1000; f_high_12v=high_12v/1000; f_low_12v=low_12v/1000
      
      name = {
      "test1" :(('%s - %2.2f - %2.2f' % (self.testName,f_nom_5v,f_nom_12v)),  'IDT Volt N_N'),
      "test2" :(('%s - %2.2f - %2.2f' % (self.testName,f_low_5v,f_low_12v)),  'IDT Volt L_L'),
      "test3" :(('%s - %2.2f - %2.2f' % (self.testName,f_high_5v,f_high_12v)), 'IDT Volt H_H') }
      
      test = {}
      test['1_5']  = nominal_5v;  test['1_12']  = nominal_12v
      test['2_5']  = low_5v;      test['2_12']  = low_12v
      test['3_5']  = high_5v;     test['3_12']  = high_12v
   
      self.oSerial = serialScreen.sptDiagCmds()
      for testname in range(1,(len(name)+1)):        #for 3 types of volt range
         for loop in range(1,loops+1):                  #powercycle for each type of volt range
            volts5   = ('%d_5'  % testname)   # volt5  = 1_5 to 10_5
            volts12  = ('%d_12' % testname)   # volt12 = 1_12 to 10_12
            name_key = ('test%d' % testname)  # test1 to test10
            self.volts5 = test[volts5]; self.volts12 = test[volts12]
            objMsg.printMsg('---------------------- Volts Setting %d - Loop No. %d -------------------------' % (testname,loop))
            objMsg.printMsg(name[name_key][0])
            objPwrCtrl.powerCycle(self.volts5,self.volts12,10,10,baudRate=Baud38400)
            if result == OK:
               self.oSerial.enableDiags()
               ICmd.ClearBinBuff()
               data = ICmd.SequentialWRDMAExt(0,8,8,8,0,1,timeout=30)
               result = data['LLRET']
            if result != OK: break
         if result != OK: break
        
      if result != OK:
         objMsg.printMsg('%s Failed' % self.testName)
         if testname == 1: errorcode = 13070
         if testname == 2: errorcode = 13071
         if testname == 3: errorcode = 13072
         getSerialPortData()
         ScrCmds.raiseException(errorcode,'IDT_VOLTAGE_HIGH_LOW Failed')
      else:
         objMsg.printMsg('%s Test Passed' % self.testName)
         
      return result

###########################################################################################################
class CSmartDST_SPT(CState):
   """
      Class that performs IDT_SHORT_DST_IDE and IDT_FULL_DST_IDE tests. 
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)
      self.oGIO = CGIO(self.dut, params={})
      self.oSerial = serialScreen.sptDiagCmds()

   #---------------------------------------------------------------------------------------------------------#
   def GetDSTTimeout(self, dst_cmd):
      sptCmds.gotoLevel('T')
      data = sptCmds.sendDiagCmd("r137,,,174,2,100", printResult = True)
      match = re.search('00000170\s*(?P<ShortDSTTimeout>[\dA-F]+)\s*(?P<LongDSTTimeout>[\dA-F]+)', data)

      if match:
         ShortDSTTimeout = int(match.groupdict()['ShortDSTTimeout'],16)
         LongDSTTimeout = int(match.groupdict()['LongDSTTimeout'],16)

         if testSwitch.FE_0112188_345334_HEAD_RANGE_SUPPORT_10_HEADS:
            if LongDSTTimeout == 255: # offset 375 (0x177) if MinutesToPerformLongSelfTest is FF (ExtendedMinutesToPerformLongSelfTestLow)
               data = sptCmds.sendDiagCmd("r137,,,177,2,100", printResult = True)
               match = re.search('00000170\s*(?P<LongDSTTimeoutLow>[\dA-F]+)\s*(?P<LongDSTTimeoutHigh>[\dA-F]+)', data)
               if match:
                  LongDSTTimeout = int(match.groupdict()['LongDSTTimeoutHigh'] + match.groupdict()['LongDSTTimeoutLow'],16)
                  objMsg.printMsg("LongDSTTimeout : %s"%LongDSTTimeout)
               else:
                  objMsg.printMsg("unable to find dst timeout")
                  return 0

         if dst_cmd == "MaxDSTSelfTestTime":
            return LongDSTTimeout * 60
         else:
            return ShortDSTTimeout * 60
      else:
         objMsg.printMsg("unable to find dst timeout")
         return 0

   #---------------------------------------------------------------------------------------------------------#
   def DSTTest_IDE(self, TestType, TestLength):
      try:
         self.runDSTTest_IDE(TestType, TestLength)
      except CRaiseException,exceptionData:
         objMsg.printMsg("runDSTTest_IDE exception: %s" % traceback.format_exc())
         if exceptionData[0][2] in [10566]:
            try:
               objMsg.printMsg('PROC_CTRL30 before=%s' % self.dut.driveattr['PROC_CTRL30'])
               self.dut.driveattr['PROC_CTRL30'] = "0X%X" % (int(self.dut.driveattr['PROC_CTRL30'], 16) | 0x1000)
            except:
               objMsg.printMsg("PROC_CTRL30 Exception: %s" % traceback.format_exc())
               self.dut.driveattr['PROC_CTRL30'] = "0X1000"

            objMsg.printMsg('EC10566 runDSTTest_IDE rerun. PROC_CTRL30=%s' % self.dut.driveattr['PROC_CTRL30'])
            self.oGIO.powerCycle(pwrOption = "pwrDefault")
            self.runDSTTest_IDE(TestType, TestLength)
         else:
            raise

   #---------------------------------------------------------------------------------------------------------#
   def runDSTTest_IDE(self, TestType, TestLength):
      result = OK
      TestName = ('DST_%s_IDE' % TestLength)                  # Test Name for file formatting
      
      if TestLength == 'Short': 
         ScrCmds.insertHeader("IDT_SHORT_DST_IDE",headChar='#')
         Command = '/1NB'    
         wait = 30
         timeout = 180
         dst_cmd = "DSTShortTestTimeLimit"
      elif TestLength == 'Long': 
         ScrCmds.insertHeader("IDT_FULL_DST_IDE",headChar='#')
         Command = '/1NC'
         wait = 300
         timeout = self.dut.imaxHead*60*60
         dst_cmd = "MaxDSTSelfTestTime"

      self.oGIO.powerCycle()

      try:
         dst_timeout = self.GetDSTTimeout(dst_cmd)
         if dst_timeout > 0:
            timeout = dst_timeout * 1.2  # to allow 20% more time
      except:
         pass

      if testSwitch.WA_0264977_321126_WAIT_UNTIL_DST_COMPLETION:
         self.dut.objData.update({'dst': timeout})
      
      self.oSerial.sendDiagCmd('''/TF"CurrentAPMValue",FEFE''',altPattern="T>",printResult=True)
      if testSwitch.IS_SDnD or self.dut.driveattr['FDE_DRIVE'] == 'FDE':
         self.oGIO.powerCycle(pwrOption = "pwrDefault")
      else:
         self.oGIO.powerCycle(pwrOption = "pwrDriveOnly")
      
      # Tighten Servo CTF cmd
      objMsg.printMsg("Before DST Tighten Servo CTF cmd...")
      self.oSerial.gotoLevel('7')
      self.oSerial.sendDiagCmd("t1,4D", printResult = True)
      self.oSerial.sendDiagCmd("s1,4D,C088", printResult = True)
      self.oSerial.sendDiagCmd(Command, printResult = True)
      self.oSerial.execOnlineCmd(CTRL_R)

      sleep_delay = int(timeout / 2)
      objMsg.printMsg('Sleeping %s s...' % sleep_delay)
      time.sleep(sleep_delay) # insert delay before polling for DST status
      accumulator = ''

      for retry in range((int(timeout)/wait) + 1):
         accumulator = self.oSerial.sendDiagCmd(CTRL_Y,timeout=timeout,altPattern="status",maxRetries=3)
         objMsg.printMsg(accumulator)
         if re.search('Total process 100% complete',accumulator) and re.search('status  0',accumulator):
            result = PASS_RETURN['LLRET']
            break
         else:
            result = FAIL_RETURN['LLRET']
         time.sleep(wait)   

      if testSwitch.WA_0264977_321126_WAIT_UNTIL_DST_COMPLETION:
         self.dut.objData.update({'dst': 0})
      
      if testSwitch.virtualRun:
         result = PASS_RETURN['LLRET']

      self.oSerial.sendDiagCmd(CTRL_Z,altPattern="T>")
      self.oSerial.sendDiagCmd('F,,22',altPattern="T>",printResult=True)
      if testSwitch.IS_SDnD or self.dut.driveattr['FDE_DRIVE'] == 'FDE':
         self.oGIO.powerCycle(pwrOption = "pwrDefault")
      else:
         self.oGIO.powerCycle(pwrOption = "pwrDriveOnly")
         
      objMsg.printMsg("After DST check CTF cmd register...")
      self.oSerial.gotoLevel('7')
      self.oSerial.sendDiagCmd("t1,4D", printResult = True)
      if result != OK:
         if TestLength == 'Short':
            failure = ('%s Short DST' % TestType)
            FailCode = 13068
         else:
            failure = ('%s Long DST' % TestType)
            FailCode = 13069
         objMsg.printMsg('%s Failed' % TestName)
         getSerialPortData()
         ScrCmds.raiseException(FailCode,'%s Failed' %failure)
      else:
         objMsg.printMsg('%s Test Passed' % TestName)
  
      return result       

###########################################################################################################
class COSReadCompare(CState):
   """
      Class that performs IDT_OS_READ_COMPARE test. 
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)
      self.oGIO = CGIO(self.dut, params={})
   #---------------------------------------------------------------------------------------------------------#
   def doOSReadDrive(self, TestType='MQM', SectCnt=64, Gbytes=5.0):
      ScrCmds.insertHeader("IDT_OS_READ_COMPARE",headChar='#')      
      data = {}
      TestName = ('OS Read Test')                       # Test Name for file formatting
      self.testName = ('%s %s' % (TestType,TestName))
      
      self.oGIO.powerCycle()
      # Setup Parameters 
      Pattern = 'AAAA'
      if TestType == 'MQM':
         Pattern = '0000'
      self.pattern = Pattern
      StartLBA = 0
      EndLBA = StartLBA + ((Gbytes*1000000000) / 512)
      NumLBA = EndLBA - StartLBA
      objMsg.printMsg('%s Start LBA=%d End LBA=%d Sect Count=%d Num GBytes=%3.3f Pattern=%s' % \
                     (self.testName, StartLBA, EndLBA, SectCnt, (NumLBA*512/1000000000), Pattern))

      Retry = 2
      for loop in range(Retry+1):
         if testSwitch.virtualRun:
            data = {'LLRET': 0, 'LBA': '0x00000000009502F9', 'CNT': '1', 'ERR': '0', 'RES': '', 'DEV': '64', 'SCNT': '0', 'RESULT': 'IEK_OK:No error', 'STS': '80', 'CT': '45383'}
         else:           
            data = ICmd.OSCopySim2(StartLBA,EndLBA,SectCnt)
         result = data['LLRET'] 
         if result == OK:
            objMsg.printMsg("%s OSCopySim2 Passed - Data: %s" % (self.testName, data))
            break
         else:
            objMsg.printMsg("%s OSCopySim2 Failed - Data: %s" % (self.testName, data))
      
      if result != OK:
         objMsg.printMsg('%s Failed Result=%s Data=%s' % (self.testName, result, data))
         getSerialPortData()
         ScrCmds.raiseException(13078,'IDT_OS_READ_COMPARE Failed')
      else:
         objMsg.printMsg('%s Test Passed' % self.testName)
         
      return result
   
###########################################################################################################
class CReadTestDrive(CState):
   """
      Class that performs IDT_READ_TEST_DRIVE test. 
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)
      self.oGIO = CGIO(self.dut, params={})
   #---------------------------------------------------------------------------------------------------------#
   def doReadTestDrive(self, TestType='MQM', SeqStartLBA=64298, SeqEndLBA=203716, SeqSectCnt=16, Loops=3000, RandRdCount=30):
      ScrCmds.insertHeader("IDT_READ_TEST_DRIVE",headChar='#')
      data = {}
      TestName = ('Read Drive')                       # Test Name for file formatting
      self.testName = ('%s %s' % (TestType,TestName))
      

      self.oGIO.powerCycle()
      # Setup Parameters            
      Pattern = '7777'
      if TestType == 'MQM':
         Pattern = '0000'
      self.pattern = Pattern
      RandStartLBA = 0
      RandEndLBA = self.dut.driveattr['Max LBA'] - 256
      objMsg.printMsg('%s SeqStart=%d/0x%X SeqEnd=%d/0x%X SeqSectCount=%d Pattern=%s Loops=%d' % \
                     (self.testName,SeqStartLBA,SeqStartLBA,SeqEndLBA,SeqEndLBA,SeqSectCnt,Pattern,Loops))
      objMsg.printMsg('%s RandStart=%d/0x%X RandEnd=%d/0x%X RandRdCount=%d' % \
                     (self.testName,RandStartLBA,RandStartLBA,RandEndLBA,RandEndLBA,RandRdCount,))
      
      Retry = 2
      for loop in range(Retry+1):
         if testSwitch.virtualRun:
            data = {'LLRET': 0, 'LBA': '0x0000000015C89C2B', 'CNT': '3000', 'ERR': '0', 'RES': '', 'DEV': '64', 'SCNT': '0', 'RESULT': 'IEK_OK:No error', 'STS': '80', 'CT': '65054'}
         else:   
            data = ICmd.ReadTestSim(SeqStartLBA,SeqEndLBA,SeqSectCnt,SeqSectCnt,RandStartLBA,RandEndLBA,\
                                 Loops,RandRdCount,Pattern) 
         result = data['LLRET']
         if result == OK:
            objMsg.printMsg("%s ReadTestSim Passed - Data: %s" % (self.testName, data))
            break
         else:
            objMsg.printMsg("%s ReadTestSim Failed - Data: %s" % (self.testName, data))
      
      if result != OK:
         objMsg.printMsg('%s Failed Result=%s Data=%s' % (self.testName, result, data))
         getSerialPortData()
         ScrCmds.raiseException(13074,'IDT_READ_TEST_DRIVE Failed')
      else:
         objMsg.printMsg('%s Test Passed' % self.testName)
         
      return result
    
###########################################################################################################
class CReadPatternForward(CState):
   """
      Class that performs IDT_READ_PATTERN_FORWARD test. 
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)
      self.oGIO = CGIO(self.dut, params={})
   #---------------------------------------------------------------------------------------------------------#
   def doReadPattForward(self, TestType='MQM', Pattern='0000', Location='OD', NumLBA=10000000, SectCnt=256):
      ScrCmds.insertHeader("IDT_READ_PATTERN_FORWARD",headChar='#') 
      data = {}
      result = OK
      TestName = ('Read Pattern')                       # Test Name for file formatting
      self.testName = ('%s %s' % (TestType,TestName))

      self.oGIO.powerCycle()
      # Setup Parameters
      StepLBA = SectCnt
      BlockSize = 512
      CompFlag = 1
      IDMaxLBA = self.dut.driveattr['Max LBA']
      if Location == 'ID':
         StartLBA = (IDMaxLBA - NumLBA)
      elif Location == 'MD':
         StartLBA = ((IDMaxLBA/2) - NumLBA)
      else: # 'OD'
         StartLBA = 0
      EndLBA = StartLBA + NumLBA
      self.pattern = Pattern
      objMsg.printMsg('%s Start LBA=%d End LBA=%d Sect Count=%d Num LBAs=%d' % \
                     (self.testName, StartLBA, EndLBA, SectCnt, NumLBA))
      
      objMsg.printMsg('%s Flush Cache, Clear Buffers, Fill %s Data' % (self.testName, Pattern))
      ICmd.ClearBinBuff()
      ICmd.FillBuffer(1,0,Pattern)
      
      if testSwitch.virtualRun:
         data = {'LLRET': 0, 'LBA': '0x0000000000989680', 'CNT': '1', 'AAU_FAULT': '0', 'ERR': '0', 'RES': '', \
         'RPT_AAU_FAULT': '0', 'RPT_AAU_FAULT_LIMIT': '10', 'SCNT': '0', 'RESULT': 'IEK_OK:No error', 'STS': '80', 'DEV': '64', 'CT': '89880'}
      else:                  
         data = ICmd.SequentialReadDMAExt(StartLBA, EndLBA, StepLBA, SectCnt, 0, CompFlag)
      result = data['LLRET']
      if result == OK:
         objMsg.printMsg("%s SequentialReadDMA Passed - Data: %s" % (self.testName, data))
      else:
         objMsg.printMsg("%s SequentialReadDMA Failed - Data: %s" % (self.testName, data))
         getSerialPortData()
         ScrCmds.raiseException(13081,'IDT_READ_PATTERN_FORWARD Failed')
      
      return result
   
###########################################################################################################
class CImageFileCopy(CState):
   """
      Class that performs IDT_IMAGE_FILE_COPY test. 
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)
      self.oGIO = CGIO(self.dut, params={})
   #---------------------------------------------------------------------------------------------------------#
   def doImageFileCopy(self, TestType='MQM', FAT_Min=10000, FAT_Max=14999, FAT_SectCnt=1, Data_Min=1000000, Data_Max=1080000, Data_SectCnt=16):
      ScrCmds.insertHeader("IDT_IMAGE_FILE_COPY",headChar='#') 
      data = {}
      result = OK
      TestName = ('Image FileCopy')                       # Test Name for file formatting
      self.testName = ('%s %s' % (TestType,TestName))

      self.oGIO.powerCycle()

      # Setup Parameters
      Pattern1 = '00FF'
      Pattern2 = '6666'
      if TestType == 'MQM':
         Pattern1 = '0000'
         Pattern2 = '0000'
      if Data_Max == ('MaxLBA'):
         Data_Max = self.dut.driveattr['Max LBA'] - 1

      self.pattern = Pattern1+' OR '+Pattern2
      self.sectorCount = FAT_SectCnt
      objMsg.printMsg('%s FAT Min=%d/0x%X   FAT Max=%d/0x%X   FAT Sector Count=%d Pattern1=%s' % \
                     (self.testName,FAT_Min,FAT_Min,FAT_Max,FAT_Max,FAT_SectCnt,Pattern1))
      objMsg.printMsg('%s Data Min=%d/0x%X  Data Max=%d/0x%X  Data Sector Count=%d Pattern2=%s' % \
                     (self.testName,Data_Min,Data_Min,Data_Max,Data_Max,Data_SectCnt,Pattern2))
      
      Retry = 2
      for loop in range(Retry+1):
         data = ICmd.FileCopySim1(FAT_Min,FAT_Max,FAT_SectCnt,Data_Min,Pattern1,Pattern2)
         result = data['LLRET']
         if result == OK:
            objMsg.printMsg("%s FileCopySim1 Passed - Data: %s" % (self.testName, data))
            break
      
      if result != OK:
         objMsg.printMsg('%s Failed Result=%s Data=%s' % (self.testName, result, data))
         getSerialPortData()
         ScrCmds.raiseException(13066,'IDT_IMAGE_FILE_COPY Failed')
      else:
         objMsg.printMsg('%s Test Passed' % self.testName)
         
      return result

###########################################################################################################
class CImageFileRead(CState):
   """
      Class that performs IDT_IMAGE_FILE_READ test. 
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)
      self.oGIO = CGIO(self.dut, params={})
   #---------------------------------------------------------------------------------------------------------#
   def doImageFileRead(self, TestType='MQM', FAT_Min=10000, FAT_Max=14999, FAT_SectCnt=256, Data_Min=1000000, Data_Max=1080000, Data_SectCnt=256):
      ScrCmds.insertHeader("IDT_IMAGE_FILE_READ",headChar='#') 
      data = {}
      result = OK
      TestName = ('Image FileRead')                       # Test Name for file formatting
      self.testName = ('%s %s' % (TestType,TestName))

      self.oGIO.powerCycle()
            
      # Setup Parameters
      Pattern1 = '00FF'
      Pattern2 = '6666'
      if TestType == 'MQM':
         Pattern1 = '0000'
         Pattern2 = '0000'
      if Data_Max == ('MaxLBA'):
         Data_Max = self.dut.driveattr['Max LBA'] - 1
         
      self.pattern = Pattern1+' OR '+Pattern2
      self.sectorCount = FAT_SectCnt
      objMsg.printMsg('%s FAT Min=%d/0x%X   FAT Max=%d/0x%X   FAT Sector Count=%d Pattern1=%s' % \
                     (self.testName,FAT_Min,FAT_Min,FAT_Max,FAT_Max,FAT_SectCnt,Pattern1))
      objMsg.printMsg('%s Data Min=%d/0x%X  Data Max=%d/0x%X  Data Sector Count=%d Pattern2=%s' % \
                     (self.testName,Data_Min,Data_Min,Data_Max,Data_Max,Data_SectCnt,Pattern2))
      
      Retry = 2
      for loop in range(Retry+1):
         if testSwitch.virtualRun:
            data = {'LLRET': 0, 'LBA': '0x00000000000F42BF', 'ERR': '0', 'RES': '', 'DEV': '64', 'SCNT': '0', 'RESULT': 'IEK_OK:No error', 'STS': '80', 'TSCNT': '0x0000000000001388', 'CT': '1975'}
         else:            
            data = ICmd.FileCopySim2(FAT_Min,FAT_Max,FAT_SectCnt,Data_Min,Data_Max,Data_SectCnt)
         result = data['LLRET']
         if result == OK:
            objMsg.printMsg("%s FileCopySim2 Passed - Data: %s" % (self.testName, data))
            break
         else:
            objMsg.printMsg("%s FileCopySim2 Failed - Data: %s" % (self.testName, data))
      
      if result != OK:
         objMsg.printMsg('%s Failed Result=%s Data=%s' % (self.testName, result, data))
         getSerialPortData()
         ScrCmds.raiseException(13067,'IDT_IMAGE_FILE_READ Failed')
      else:
         objMsg.printMsg('%s Test Passed' % self.testName)
         
      return result      

###########################################################################################################
class CMSSusTxferRate(CState):
   """
      Class that performs IDT_MS_SUS_TXFER_RATE test. 
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)
      self.oGIO = CGIO(self.dut, params={})

   #-------------------------------------------------------------------------------------------------------
   def ReadScan(self, TestName, IDStartLBA, ODStartLBA, blockSize, SectCount):

      StampFlag = 0
      CompareFlag = 0
      result = OK

      self.oGIO.powerCycle()

      # read ID
      if result == OK:
         EndLBA = IDStartLBA + blockSize - 1

         objMsg.printMsg('%s SeqReadDMAExt-ID minLBA=%d MaxLBA=%d StepLBA=%d SectCnt=%d StampFlag=%d CompFlag=%d' % \
         (TestName, IDStartLBA, EndLBA, SectCount, SectCount, StampFlag, CompareFlag))

         data = ICmd.SequentialReadDMAExt(IDStartLBA, EndLBA, SectCount, SectCount, StampFlag, CompareFlag)
         result = data['LLRET']
         if result != OK:
            objMsg.printMsg('%s SequentialReadDMAExt ID failed, Result=%s Data=%s' % (TestName, result, data))
         else:
            objMsg.printMsg('%s SeqReadDMAExt-ID passed' % TestName)

      # read OD
      if result == OK:
         EndLBA = ODStartLBA + blockSize - 1
         objMsg.printMsg('%s SeqReadDMAExt-OD minLBA=%d MaxLBA=%d StepLBA=%d SectCnt=%d StampFlag=%d CompFlag=%d' % \
         (TestName, ODStartLBA, EndLBA, SectCount, SectCount, StampFlag, CompareFlag))

         data = ICmd.SequentialReadDMAExt(ODStartLBA, EndLBA, SectCount, SectCount, StampFlag, CompareFlag)
         result = data['LLRET']

         if testSwitch.virtualRun:
            result = OK #found UDE

         if result != OK:
            objMsg.printMsg('%s SequentialReadDMAExt OD failed, Result=%s Data=%s' % (TestName, result, data))
         else:
            objMsg.printMsg('%s SeqReadDMAExt-OD passed' % TestName)

      return result

   #---------------------------------------------------------------------------------------------------------#
   def MSSTR_dblog(self, loopcnt, StartLBA, TotalLBA, WrRate, RdRate):

      seqNum,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)

      self.dut.dblData.Tables('P_SUSTAINED_TRANSFER_RATE').addRecord({
                              'SPC_ID' : str(loopcnt),
                              'OCCURRENCE': occurrence,
                              'SEQ' : seqNum,
                              'TEST_SEQ_EVENT': testSeqEvent,
                              'START_LBA': StartLBA,
                              'TOTAL_TEST_LBAS': TotalLBA,
                              'WRITE_XFER_RATE': WrRate,
                              'READ_XFER_RATE':  RdRate,
                              })

   #---------------------------------------------------------------------------------------------------------#
   def doOffset(self, TPKey, OrgValue):
      ret = int(OrgValue + float(getattr(TP, TPKey, 0)))
      objMsg.printMsg('MSSTR Offset... before=%s after=%s' % (OrgValue, ret))
      return ret

   #---------------------------------------------------------------------------------------------------------#
   def doMSSustainTferRate(self, TestType='MQM', TestName='MSSTR'):
      result = OK
      loop = 2
      MS_SUS_TXFER_RATE = ON

      if MS_SUS_TXFER_RATE == ON:
         while loop:
            result, data, TestName, IDStartLBA, ODStartLBA, blockSize, SectCnt = self.doMSSustainTferRateTest()

            if result != OK:
               if loop == 1:
                  break # failed MSSTR
               # perform read scan using ICmd.SequentialReadDMAExt to check any UDE
               objMsg.printMsg('%s IDStartLBA=%d ODStartLBA=%d blockSize=%d SectCnt=%d' % \
               (TestName, IDStartLBA, ODStartLBA, blockSize, SectCnt))

               res = self.ReadScan(TestName, IDStartLBA, ODStartLBA, blockSize, SectCnt)
               if res == OK:
                  objMsg.printMsg('Re-run IDT_MS_SUS_TXFER_RATE')
                  loop -= 1 # re-run MSSTR
               else:
                  break # UDE error, fail the drive
            else:
               break # pass

         if result != OK:
            if testSwitch.virtualRun:
               objMsg.printMsg('IDT_MS_SUS_TXFER_RATE Failed')
            else:
               getSerialPortData()
               ScrCmds.raiseException(13157,'IDT_MS_SUS_TXFER_RATE Failed')

      return result

   #---------------------------------------------------------------------------------------------------------#
   def doMSSustainTferRateTest(self, TestType='MQM', TestName='MSSTR'):
      ScrCmds.insertHeader("IDT_MS_SUS_TXFER_RATE",headChar='#') 
      data = {}
      self.testName = ('%s %s' % (TestType, TestName))                       # Test Name for file formatting
      result = OK
      STRLoop = 15  # 15    
      blockSize = 0x20000      # change to 20K hex
    
      
      sectCnt = 256
      TxRate = 0
      IDStartLBA = (self.dut.driveattr['Max LBA'] -1 ) - blockSize
      ODStartLBA = 0
      IDTxRate = 14    #17
      ODTxRate = 30    #30
      MS_SUS_TXFER_RATE = ON
    
      if MS_SUS_TXFER_RATE == ON:
         self.testCmdTime = 0
         self.oGIO.powerCycle()
         ICmd.ClearBinBuff()
         ICmd.FillBuffer(1,0,'0000')
       
         if result == OK:         
            objMsg.printMsg('%s (ID)StartLBA=%d (OD)StartLBA=%d BlockSize=%d SectCnt=%d' % \
                           (TestName, IDStartLBA, ODStartLBA, blockSize, sectCnt))    
          
            for i in range(1, STRLoop+1):
          
               # read ID
               if result == OK:
                  data = ICmd.ReadDMAExtTransRate(IDStartLBA, blockSize, sectCnt)
                  result = data['LLRET']
             
               if result != OK:
                  objMsg.printMsg('%s Read(ID)(%d) failed. Result=%s Data=%s' % (TestName, i, result, data))
                  break     
               else:
                  TxRate = self.doOffset("MSSTR_RDID_OFFSET", int(data['TXRATE']))
                  readIDRate = TxRate
                  TxLBA = data['ENDLBA']      # string
                  objMsg.printMsg('%s Read(ID)(%d) TxRate=%d MB/s LastLBA=%s' % (TestName, i, TxRate, TxLBA))
                
                  if TxRate >= IDTxRate:
                     objMsg.printMsg('%s Read(ID) passed. TxRate=%d MB/s' % (TestName, TxRate))  
                  else:    
                     objMsg.printMsg('%s Read(ID) TxRate(%d MB/s)<%d, Test failed! Data=%s' % (TestName, TxRate, IDTxRate, data))
                     result = FAIL
                     break

               # read OD
               if result == OK:
                  data = ICmd.ReadDMAExtTransRate(ODStartLBA, blockSize, sectCnt)
                  result = data['LLRET']
             
               if result != OK:
                  objMsg.printMsg('%s Read(OD)(%d) failed. Result=%s Data=%s' % (TestName, i, result, data))
                  break
               else:
                  TxRate = self.doOffset("MSSTR_RDOD_OFFSET", int(data['TXRATE']))
                  readODRate = TxRate
                  TxLBA = data['ENDLBA']      # string                 
                  objMsg.printMsg('%s Read(OD)(%d) TxRate=%d MB/s LastLBA=%s' % (TestName, i, TxRate, TxLBA))
                
                  if TxRate >= ODTxRate:
                     objMsg.printMsg('%s Read(OD) passed. TxRate=%d MB/s' % (TestName, TxRate)) 
                  else:    
                     objMsg.printMsg('%s Read(OD) TxRate(%d MB/s)<%d, Test failed! Data=%s' % (TestName, TxRate, ODTxRate, data))
                     result = FAIL
                     break
                   

               # write ID
               if result == OK:
                  data = ICmd.WriteDMAExtTransRate(IDStartLBA, blockSize, sectCnt)
                  result = data['LLRET']
             
               if result != OK:
                  objMsg.printMsg('%s Write(ID)(%d) failed. Result=%s Data=%s' % (TestName, i, result, data))
                  break     
               else:
                  TxRate = self.doOffset("MSSTR_WRID_OFFSET", int(data['TXRATE']))
                  TxLBA = data['ENDLBA']      # string                 
                  objMsg.printMsg('%s Write(ID)(%d) TxRate=%d MB/s LastLBA=%s' % (TestName, i, TxRate, TxLBA))
                
                  if TxRate >= IDTxRate:
                     objMsg.printMsg('%s Write(ID) passed. TxRate=%d MB/s' % (TestName, TxRate))
                  else:
                     objMsg.printMsg('%s Write(ID) TxRate(%d MB/s)<%d, Test failed! Data=%s' % (TestName, TxRate, IDTxRate, data))
                     result = FAIL
                     break

               self.MSSTR_dblog(i, IDStartLBA, blockSize, TxRate, readIDRate)

               # write OD
               if result == OK:
                  data = ICmd.WriteDMAExtTransRate(ODStartLBA, blockSize, sectCnt)
                  result = data['LLRET']
             
               if result != OK:
                  objMsg.printMsg('%s Write(OD)(%d) failed. Result=%s Data=%s' % (TestName, i, result, data))
                  break     
               else:
                  TxRate = self.doOffset("MSSTR_WROD_OFFSET", int(data['TXRATE']))
                  TxLBA = data['ENDLBA']      # string                 
                  objMsg.printMsg('%s Write(OD)(%d) TxRate=%d MB/s LastLBA=%s' % (TestName, i, TxRate, TxLBA))
                
                  if TxRate >= ODTxRate:
                     objMsg.printMsg('%s Write(OD) passed. TxRate=%d MB/s' % (TestName, TxRate)) 
                  else:   
                     objMsg.printMsg('%s Write(ID) TxRate(%d MB/s)<%d, Test failed! Data=%s' % (TestName, TxRate, ODTxRate, data))
                     result = FAIL
                     break

               self.MSSTR_dblog(i, ODStartLBA, blockSize, TxRate, readODRate)

            try:   
               objMsg.printDblogBin(self.dut.dblData.Tables('P_SUSTAINED_TRANSFER_RATE'))
            except: 
               pass

            if result == OK:
               objMsg.printMsg('%s STR Test passed!' % TestName)  
            else:
               objMsg.printMsg('%s Test failed!' % self.testName)  
               #if not testSwitch.virtualRun:    
               #   getSerialPortData()
               #   ScrCmds.raiseException(13157,'IDT_MS_SUS_TXFER_RATE Failed')

      #return result
      return result, data, TestName, IDStartLBA, ODStartLBA, blockSize, sectCnt

###########################################################################################################
class CPMZoneThroughPut(CState):
   """
      Class that performs IDT_PM_ZONETHRUPUT test. 
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)
      self.oGIO = CGIO(self.dut, params={})

   #---------------------------------------------------------------------------------------------------------#
   def doWriteTest(self, TestName, MaxLBA, i, StartLBA, EndLBA, SectCnt):
      TxRate = 0
      result = FAIL
      ICmd.ClearBinBuff()
      ICmd.FillBuffer(1,0,'0000')
  
      if testSwitch.ROSEWOOD7 and testSwitch.IS_2D_DRV == 1: #For RW2D
         try:
            data = ICmd.WriteDMAExtTransRate(StartLBA, EndLBA - StartLBA, SectCnt)
         except:
            objMsg.printMsg("Sequential write fail, do not fail the drive and skip random read test and proceed to full pack write") #RW2D Core team request to salvage yield loss
            objMsg.printMsg("doWriteTest() exception:\n%s" % traceback.format_exc())
            result = SKIP
            return result, TxRate
      else:
         data = ICmd.WriteDMAExtTransRate(StartLBA, EndLBA - StartLBA, SectCnt)

      result = data['LLRET']
      if result == OK:
         TxRate = int(data['TXRATE'])
         objMsg.printMsg('%s MaxLBA=%d WriteDMA Zone=%d StartLBA=%d EndLBA=%d SectCnt=%d TxRate=%d' % \
                        (TestName, MaxLBA, i, StartLBA, EndLBA, SectCnt, TxRate))
      else:
         objMsg.printMsg('%s Zone(%d) WriteDMATxRate failed. Result=%s Data=%s' % (TestName, i, result, data))

      return result, TxRate

   #---------------------------------------------------------------------------------------------------------#
   def doPerfMeasureZoneDegrade(self, TestType='MQM', TestName='ZONEDEGRADE'):
      ScrCmds.insertHeader("IDT_PM_ZONETHRUPUT",headChar='#') 
      data = {}
      
      self.testName = ('%s %s' % (TestType, TestName))                       # Test Name for file formatting
      result = OK
      UDMA_Speed = 0x45
      NumZone = 16   
      MaxLBA = self.dut.driveattr['Max LBA'] - (self.dut.driveattr['Max LBA'] % NumZone)
      ZoneStep = MaxLBA / NumZone
      SectCnt = 256    
      TxSet1 = {}
      TxSet2 = {}
      ZONETHRUPUT = ON

      if ZONETHRUPUT == ON and not testSwitch.virtualRun:

         if result == OK:
            self.testCmdTime = 0
            self.oGIO.powerCycle()

            if self.dut.RetryCnt > 0:
               sptCmds.gotoLevel('F')
               data = sptCmds.sendDiagCmd("/FY0", printResult = True)
         
         if result == OK:
            StartLBA = 0
            EndLBA = StartLBA + ZoneStep - 1
            for i in range(1, NumZone+1):       
               # seq write   
               if (testSwitch.FE_0255791_356922_SPMQM_ZONETRUPUT_WRITE_READ) and (result == OK) and (i==1 or i==NumZone):
                  result, TxRate = self.doWriteTest(TestName, MaxLBA, i, StartLBA, EndLBA, SectCnt)
                  if result == OK:
                     TxSet1['ZoneWrt%d'% i] = TxRate
                  else:
                     break

               # seq read
               if (result == OK) and (i==1 or i==NumZone):
                  objMsg.printMsg('RetryCnt=%s ReadDMAExtTransRate=%s %s %s' % (self.dut.RetryCnt, StartLBA, EndLBA - StartLBA, SectCnt))

                  data = ICmd.ReadDMAExtTransRate(StartLBA, EndLBA - StartLBA, SectCnt)
                  result = data['LLRET']
                  if result == OK:
                     TxRate = int(data['TXRATE'])
                     objMsg.printMsg('%s MaxLBA=%d ReadDMA Zone=%d StartLBA=%d EndLBA=%d SectCnt=%d TxRate=%d' % \
                                    (TestName, MaxLBA, i, StartLBA, EndLBA, SectCnt, TxRate))
                     TxSet1['ZoneRead%d'% i] = TxRate             
                  else:
                     objMsg.printMsg('%s Zone(%d) ReadDMATxRate failed. Result=%s Data=%s' % (TestName, i, result, data))
                     break     
                
               # seq write   
               if (not testSwitch.FE_0255791_356922_SPMQM_ZONETRUPUT_WRITE_READ) and (result == OK) and (i==1 or i==NumZone):
                  result, TxRate = self.doWriteTest(TestName, MaxLBA, i, StartLBA, EndLBA, SectCnt)
                  if result == OK:
                     TxSet1['ZoneWrt%d'% i] = TxRate
                  else:
                     break
  
               StartLBA = StartLBA + ZoneStep
               EndLBA = StartLBA + ZoneStep - 1    
               # end for

            if result == SKIP:
               return result #RW72D - abort test due to doWriteTest() failure

            StartLBA = 0
            EndLBA = StartLBA + ZoneStep - 1
          
            for i in range(1, NumZone+1):
               # seq write   
               if (testSwitch.FE_0255791_356922_SPMQM_ZONETRUPUT_WRITE_READ) and (result == OK) and (i==1 or i==NumZone):
                  result, TxRate = self.doWriteTest(TestName, MaxLBA, i, StartLBA, EndLBA, SectCnt)
                  if result == OK:
                     TxSet2['ZoneWrt%d'% i] = TxRate
                  else:
                     break        

               # seq read
               if (result == OK) and (i==1 or i==NumZone):
                  data = ICmd.ReadDMAExtTransRate(StartLBA, EndLBA - StartLBA, SectCnt)
                  result = data['LLRET']
                  if result == OK:
                     TxRate = int(data['TXRATE'])
                     objMsg.printMsg('%s MaxLBA=%d ReadDMA Zone=%d StartLBA=%d EndLBA=%d SectCnt=%d TxRate=%d' % \
                                    (TestName, MaxLBA, i, StartLBA, EndLBA, SectCnt, TxRate))
                     TxSet2['ZoneRead%d'% i] = TxRate             
             
                  else:
                     objMsg.printMsg('%s Zone(%d) ReadDMATxRate failed. Result=%s Data=%s' % (TestName, i, result, data))
                     break     
                
               # seq write   
               if (not testSwitch.FE_0255791_356922_SPMQM_ZONETRUPUT_WRITE_READ) and (result == OK) and (i==1 or i==NumZone):
                  result, TxRate = self.doWriteTest(TestName, MaxLBA, i, StartLBA, EndLBA, SectCnt)
                  if result == OK:
                     TxSet2['ZoneWrt%d'% i] = TxRate
                  else:
                     break           
  
               StartLBA = StartLBA + ZoneStep
               EndLBA = StartLBA + ZoneStep - 1    

               # end for             
             
         if result == SKIP:
            return result #RW72D - abort test due to doWriteTest() failure

         if result == OK:
            keys1 = TxSet1.keys()
            keys1.sort()
            keys2 = TxSet2.keys()
            keys2.sort()
            for key in TxSet1.keys():
               if testSwitch.virtualRun:
                  skew = 0
               else:    
                  if TxSet1[key] >= TxSet2[key]:
                     skew = (TxSet1[key] - TxSet2[key]) / (TxSet1[key] * 1.0)
                  else:   
                     skew = (TxSet2[key] - TxSet1[key]) / (TxSet2[key] * 1.0)
                     
               objMsg.printMsg('%s Key=%s TxRate1=%d TxRate2=%d' % (TestName, key, TxSet1[key], TxSet2[key]))   
               if skew > 0.2:
                  objMsg.printMsg('%s Test failed.' % TestName)                      
                  result = FAIL
                  break
      
             
         if result == OK:
            if self.dut.RetryCnt > 0:
               self.oGIO.powerCycle(pwrOption = "pwrDefault")

            objMsg.printMsg('%s Test passed!' % TestName)
         else:
            objMsg.printMsg('%s Test failed!' % TestName)  
            getSerialPortData()
            ScrCmds.raiseException(13160,'IDT_PM_ZONETHRUPUT Failed')

      return result  
   
###########################################################################################################
class CSerialSDOD(CState):
   """
      Class that performs IDT_SERIAL_SDOD_TEST test. 
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)
      self.oGIO = CGIO(self.dut, params={})
   #---------------------------------------------------------------------------------------------------------#
   def doSerialSDODCheck(self, TestType='MQM', TestName='SDOD CHECK'):
      ScrCmds.insertHeader("IDT_SERIAL_SDOD_TEST",headChar='#') 
      data = {}
      result = FAIL
      self.testName = ('%s %s' % (TestType, TestName))                       # Test Name for file formatting
      SERIAL_SDOD = ON 

      timeout = 60  # serial timeout

      if SERIAL_SDOD == ON:    
         self.testCmdTime = 0
         self.oGIO.powerCycle()
         result = OK
         sdod_loop = 1

         if testSwitch.ROSEWOOD7 and testSwitch.IS_2D_DRV == 1 and TestType != "MODE_SPFIN": #For RW2D
            # Hard power cycles to capture any erasure signature in LongDST test
            powercycle_loop = 50
            for i in xrange(powercycle_loop):
               objMsg.printMsg('Initiating power cycle, loop = %s' % (i+1))
               self.oGIO.powerCycle(pwrOption = "pwrDriveOnly")
         else:
            # legacy SDOD algorithm
            if testSwitch.KARNAK and TestType != "MODE_SPFIN":
               sdod_loop = 100

            for i in xrange(sdod_loop):
               if not (i%10):
                  objMsg.printMsg('%s Initiating Serial SDOD, loop = %s' % (TestName, i+1))

               try:
                  sptCmds.gotoLevel('2')
                  data = sptCmds.sendDiagCmd("Z\r",timeout = timeout, printResult = True)               
                  data = sptCmds.sendDiagCmd("U3\r",timeout = timeout, printResult = True)               
                  data = sptCmds.sendDiagCmd("Z\r",timeout = timeout, printResult = True)               
               except Exception, e:
                  objMsg.printMsg("Serial Port Exception data : %s"%e)
                  objMsg.printMsg('%s Serial SDOD Check failed attempt %d' % (TestName, i+1))
                  result = -1
                  break

         if TestType != "MODE_SPFIN":
            if testSwitch.IS_SDnD or self.dut.driveattr['FDE_DRIVE'] == 'FDE':
               self.oGIO.powerCycle(pwrOption = "pwrDefault")
            else:
               self.oGIO.powerCycle(pwrOption = "pwrDriveOnly")

         if result != OK:   
            objMsg.printMsg('%s Serial SDOD Check Failed' % TestName)
            getSerialPortData()
            ScrCmds.raiseException(13151,'IDT_SERIAL_SDOD_TEST FAiled')
         else:
            objMsg.printMsg('%s Serial SDOD Check Passed' % TestName)
            
      return result

###########################################################################################################
class CGetSMARTLogs(CState):
   """
      Class that performs IDT_GET_SMART_LOGS test. 
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)
      self.oGIO = CGIO(self.dut, params={})
      self.oSerial = serialScreen.sptDiagCmds()
      self.GListLimit = 0
      self.PListLimit = 0
      self.RListLimit = 0      
      self.IOEDCLimit = 0
      self.A198Limit = 0      
      self.Status = OK
      self.errorcode = 0
   #-------------------------------------------------------------------------------------------------------
   def runSmart(self, LogList, check=ON):
      result = self.checkSmartLogs(LogList,check)
      result = self.checkSmartAttr(check)
      
   #------------------------------------------------------------------------------------------------------#
   def checkSmartLogs(self, LogList, check=ON):
      """
        Utility check SMART Logs
        #With Reference to SoonYak#
        Log 0xA8 - The raw field of Smart attribute #5 (bytes[1:0]) records the number of reallocation, 
                   which should match the number of entries in log A8.
        Log 0xA9 - The raw field of Smart attribute #197 (bytes[1:0]) records the number of pending spare count, 
                   which should match the number of entries in log A9.
        Log 0xA7 - From revision 278 of Yarra programme onwards, you can use serial port diagnostic mode level '1'; 
                   'N18' command to retrieve log A7 entry count.
        Log 0xA1 - From 1>N8 command.
      """
      if check == ON: self.TestName = 'Check SmartLog'
      else : self.TestName = 'Display SmartLog'         
      objMsg.printMsg(self.TestName)
      self.oGIO.powerCycle()
      if not testSwitch.BYPASS_N2_CMD: #Bypass /1N2 cmd until F3 code ready
         self.oSerial.sendDiagCmd('/1N2', printResult = True)  #Update SMART  
      CriticalEventLogData = self.oSerial.sendDiagCmd('/1N5', printResult = True)
      CELogAttrs = self.oSerial.parseCEAttributes(CriticalEventLogData)
      if testSwitch.virtualRun:
         GList_Entries = 0
         PList_Entries = 0
      else:        
         GList_Entries = CELogAttrs['5']['raw'] & 0xFFFF #Smart attribute #5 (bytes[1:0]) -> G-List Entry
         PList_Entries = CELogAttrs['C5']['raw'] & 0xFFFF #Smart attribute #197 (bytes[1:0]) -> P-List Entry
      
      if testSwitch.NoIO:
         objMsg.printMsg('GList_Entries=%s PList_Entries=%s' % (GList_Entries, PList_Entries))
         seqNum,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
         self.dut.dblData.Tables('P_GROWN_DEFECT_LIST').addRecord(
            {
            'SPC_ID' : getattr(TP,"spcid_SmartDefectList",{}).get(self.dut.nextOper,self.dut.objSeq.curRegSPCID),
            'OCCURRENCE': occurrence,
            'SEQ' : seqNum,
            'TEST_SEQ_EVENT': testSeqEvent,
            'PBA':0,
            'RW_FLAGS':0,
            'ERR_LENGTH': GList_Entries
            })

         self.dut.dblData.Tables('P_PENDING_DEFECT_LIST').addRecord(
            {
            'SPC_ID' : getattr(TP,"spcid_SmartDefectList",{}).get(self.dut.nextOper,self.dut.objSeq.curRegSPCID),
            'OCCURRENCE': occurrence,
            'SEQ' : seqNum,
            'TEST_SEQ_EVENT': testSeqEvent,
            'TOTAL_DFCTS_DRIVE': PList_Entries
            })
      
      if 0xA8 in LogList:     
         objMsg.printMsg('Number of Events in GList:%d' % GList_Entries)
         if GList_Entries > 0:
            objMsg.printMsg('GList Limit:%d' % self.GListLimit)
            if GList_Entries > self.GListLimit:
               objMsg.printMsg('GList Entries Exceeds Limit!')
               if check == ON: 
                  failure = 'IDT Smart attribute #5 (bytes[1:0])'
                  self.Status = FAIL
                  self.errorcode = 13055

      if 0xA9 in LogList:     
         objMsg.printMsg('Number of Events in PList:%d' % PList_Entries)
         if PList_Entries > 0:
            objMsg.printMsg('PList Limit:%d' % self.PListLimit)
            if PList_Entries > self.PListLimit:
               objMsg.printMsg('PList Entries Exceeds Limit!')
               if check == ON: 
                  failure = 'IDT Smart attribute #197 (bytes[1:0])'
                  self.Status = FAIL
                  self.errorcode = 13059

      if 0xA7 in LogList:
         sectors, wedges = self.oSerial.dumpRList()
         numOfEvents = sectors + wedges
         objMsg.printMsg('Number of Events in RList:%d' % numOfEvents)
         if numOfEvents > 0:
            objMsg.printMsg('RList Limit:%d' % self.RListLimit)
            if numOfEvents > self.RListLimit:
               objMsg.printMsg('RList Entries Exceeds Limit!')
               if check == ON: 
                  failure = 'IDT 1>N18'
                  self.Status = FAIL   
                  self.errorcode = 13154      

      if 0xA1 in LogList:
         CELogData, summaryData, ceData = self.oSerial.getCriticalEventLog()
         EventList = [0x2,0x3,0x7,0xB]   # from GIO ReliSmart.py
         ceEventSummary = {}
         for item in ceData:
            EventID = int(re.split(' ',item['Type'])[0].strip(), 16)
            if EventID in EventList:
               ceEventSummary[EventID] =  ceEventSummary.get(EventID,0) + 1 
         numOfCriticalEvents = sum(ceEventSummary.values())

         AllEventList = ceData
         numOfEvents = len(AllEventList)
         objMsg.printMsg('Number of Events in CE Log:%d' % numOfEvents)
         objMsg.printMsg('CE Log Entries %s: %s' % (EventList,ceEventSummary))
         objMsg.printMsg('Number of Critical Events in CE Log:%d' % numOfCriticalEvents)
         if numOfCriticalEvents > 0:
             objMsg.printMsg('CE Log Entries: %s' % AllEventList)
             objMsg.printMsg('CE Log Entries Exceeds Limit: Event Type (2,3,7 or B) exists!')
             if check == ON: 
                failure = 'IDT CE LOG'
                self.Status = FAIL
                self.errorcode = 13053
           
      if check == ON: 
         if self.Status == OK:
            objMsg.printMsg('Smart Logs Check passed!')          
         else:
            objMsg.printMsg('Smart Logs Check failed!')
            if not testSwitch.virtualRun:      
               getSerialPortData()
               ScrCmds.raiseException(self.errorcode, 'IDT_GET_SMART_LOGS Failed' )
    
      return self.Status
   
   #------------------------------------------------------------------------------------------------------#
   def checkSmartAttr(self, check=ON):
       """
         SMART Attribute - Retrieve the Smart attribute data from FileID #137 -> T>r137,3,,,,100.
         Utility check SMART Attribute 
            Attr 5      Retired Sector Count   
            Attr 184    IOEDC 
            Attr 197    Pending Sparing Count
            Attr 198    Uncorrectable Sector Count
            Byte 410    Retired Sector Count when last Smart Reset
            Byte 412    Pending Spare Count when last Smart Reset
       """
       if check == ON: self.TestName = 'Check SmartAttribute'
       else: self.TestName = 'Display SmartAttribute'
       objMsg.printMsg(self.TestName)
       if ConfigVars[CN].has_key('SMART CHECK B410') and ConfigVars[CN]['SMART CHECK B410'] != UNDEF and ConfigVars[CN]['SMART CHECK B410'] == 'OFF':
          Check_B410 = OFF

       if ConfigVars[CN].has_key('SMART CHECK B412') and ConfigVars[CN]['SMART CHECK B412'] != UNDEF and ConfigVars[CN]['SMART CHECK B412'] == 'OFF':   
          Check_B412 = OFF
                
       if ConfigVars[CN].has_key('SMART CHECK IOEDC') and ConfigVars[CN]['SMART CHECK IOEDC'] != UNDEF and ConfigVars[CN]['SMART CHECK IOEDC'] == 'ON':   
          Check_IOEDC = ON

       if ConfigVars[CN].has_key('SMART CHECK A198') and ConfigVars[CN]['SMART CHECK A198'] != UNDEF and ConfigVars[CN]['SMART CHECK A198'] == 'ON':   
          Check_A198 = ON
 

       if self.Status == OK:
          self.oGIO.powerCycle()
          
          MaxRetry = 2
          for i in xrange(MaxRetry):
            try:
                smartData = ''
                if not testSwitch.BYPASS_N2_CMD: #Bypass /1N2 cmd until F3 code ready
                   self.oSerial.sendDiagCmd('/1N2', printResult = True) #Update SMART  
                data = self.oSerial.sendDiagCmd('/Tr137,3,,,200,100', printResult = True)
                rawdata = data.splitlines()
                for line in rawdata:
                  dataspt = line.strip().replace(" ",'')
                  if len(dataspt) == 40:
                     smartData += dataspt[8:]                
                if len(smartData)/2 <> 512:
                   if not testSwitch.virtualRun: 
                      ScrCmds.raiseException(11044, "smartData is not 512 Bytes!" )
                break
            except:
               if i < MaxRetry - 1:
                  objMsg.printMsg("smartData failed. Traceback=%s" % traceback.format_exc())
                  self.oGIO.powerCycle(pwrOption = "pwrDefault")
               else:
                  raise

          smartData = binascii.unhexlify(smartData)   
          if len(smartData) > 0:
             objMsg.printMsg('Smart Attribute File 137 Data: \r%s' %smartData)
             self.Status = OK
          else:
             self.Status = -1   
            
          if self.Status == OK:
             smartAttr = CSmartAttributes(smartData)
  
             smartAttr.decodeAttribute(5)
             A5_RetdSectCnt = smartAttr.Attribute['RawValue'] & 0xFFFF #Bytes [1:0]
             smartAttr.decodeAttribute(197)
             A197_PendSpareCnt = smartAttr.Attribute['RawValue'] & 0xFFFF #Bytes [1:0]
             smartAttr.decodeAttribute(198)
             A198_UncorrSectCnt = smartAttr.Attribute['RawValue']
             smartAttr.decodeAttribute(184)
             A184_IOEDC = smartAttr.Attribute['RawValue']
             
             # Read direct from buffer 
             B410_RepRetdSectCnt = (ord(smartAttr.buffer[410]) & 0xFF) + ((ord(smartAttr.buffer[411]) & 0xFF) << 8)
             B412_RepPendSpareCnt = (ord(smartAttr.buffer[412]) & 0xFF) + ((ord(smartAttr.buffer[413]) & 0xFF) << 8)
             
             objMsg.printMsg('Retired Sector Count(Attr5): %d' % A5_RetdSectCnt)
             objMsg.printMsg('Reported IOEDC Errors(Attr184): %d' % A184_IOEDC) 
             objMsg.printMsg('Pending Spare Count(Attr197): %d' % A197_PendSpareCnt) 
             objMsg.printMsg('Uncorrectable Sector Count(Attr198): %d' % A198_UncorrSectCnt) 
             objMsg.printMsg('Spare Count(B410) when last SmartReset: %d' % B410_RepRetdSectCnt)
             objMsg.printMsg('Pending Spare Count(B412) when last SmartReset: %d' % B412_RepPendSpareCnt)
            
             #################################################################
             smartAttr.decodeAttribute(1)     # Raw Error Rate
             A1_RAW = smartAttr.Attribute['RawValue']
             objMsg.printMsg('Raw Error Rate(Attr1): %d, 0x%X' % ((A1_RAW & 0xFFFFFFFF), A1_RAW))
             
             smartAttr.decodeAttribute(188)     # Cmd Timeout
             A188_CmdTimeout = smartAttr.Attribute['RawValue']
             objMsg.printMsg('Cmd Timeout Count >7.5s (Attr188): %d, 0x%X' % ((A188_CmdTimeout & 0xFFFF00000000), A188_CmdTimeout))
                          
             smartAttr.decodeAttribute(195)     # ECC OTF
             A195_ECCOTF = smartAttr.Attribute['RawValue']
             objMsg.printMsg('ECC On-The-Fly Count(Attr195): %d, 0x%X' % ((A195_ECCOTF & 0xFFFFFFFF), A195_ECCOTF))
             
             smartAttr.decodeAttribute(199)     # UDMA CRC Error Count
             A199_UDMACRCErrCnt = smartAttr.Attribute['RawValue']
             objMsg.printMsg('UDMA ECC Error Count(Attr199): %d, 0x%X' % ((A199_UDMACRCErrCnt & 0xFFFFFFFF), A199_UDMACRCErrCnt))
             
             B422_NumRAWReWrt = (ord(smartAttr.buffer[422]) & 0xFF) + ((ord(smartAttr.buffer[423]) & 0xFF) << 8)
             B438_SysWrtFailCnt = (ord(smartAttr.buffer[438]) & 0xFF) + ((ord(smartAttr.buffer[439]) & 0xFF) << 8)
             objMsg.printMsg('Number of ReadAfterWrite(422) need Rewrite: %d' % B422_NumRAWReWrt)
             objMsg.printMsg('Number of System Write Failures(438): %d' % B438_SysWrtFailCnt)
             
             #################################################################

             if (A5_RetdSectCnt > self.GListLimit):
                objMsg.printMsg('Retired Sector Count(Attr5) exceeded Glist limit')
                if check == ON:
                   failure = 'IDT A8 LOG'
                   self.Status = FAIL
                   self.errorcode = 13055
          
             if (A197_PendSpareCnt > self.PListLimit):
                objMsg.printMsg('Pending Spare Count(Attr197) exceeded Plist limit')
                if check == ON:
                   failure = 'IDT A9 LOG'
                   self.Status = FAIL
                   self.errorcode = 13059

             if (A184_IOEDC > self.IOEDCLimit):
                objMsg.printMsg('Reported IOEDC Errors(Attr184) exceeded IOEDC limit')
                if check == ON:
                   failure = 'IDT A184 IOEDC'
                   self.Status = FAIL
                   self.errorcode = 13150

             if (A198_UncorrSectCnt > self.A198Limit):
                objMsg.printMsg('Uncorrectable Sector Count(Attr198) exceeded A198 limit')
                if check == ON:
                   failure = 'IDT A198 USC'
                   self.Status = FAIL
                   self.errorcode = 13155

             if (B410_RepRetdSectCnt > self.GListLimit):
                objMsg.printMsg('Spare Count(410) when last SmartReset exceeded Glist limit')
                if check == ON:
                   failure = 'IDT A8 LOG'
                   self.Status = FAIL
                   self.errorcode = 13055

             if (B412_RepPendSpareCnt > self.PListLimit):
                objMsg.printMsg('Pending Spare Count(412) when last SmartReset exceeded Plist limit')
                if not (testSwitch.TRUNK_BRINGUP and testSwitch.M10P): # It is temporary code for WA of too many P-List in M10P Trunk Bringup
                   if check == ON:
                      failure = 'IDT A9 LOG'
                      self.Status = FAIL
                      self.errorcode = 13059
          
          if check == ON:   
             if self.Status == OK:
                objMsg.printMsg('Smart Attribute Check passed!')          
             else:
                objMsg.printMsg('Smart Attribute Check failed!')       
                if not testSwitch.virtualRun: 
                   getSerialPortData()
                   ScrCmds.raiseException(self.errorcode, 'SMART Attribute check Failed' )

       return self.Status

###########################################################################################################
class CVerifySMART(CState):
   """
      Class that performs IDT_VERIFY_SMART_IDE test. 
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)
      self.oGIO = CGIO(self.dut, params={})
      self.oSerial = serialScreen.sptDiagCmds()
      self.Status = OK
      self.errorcode = 0
   #------------------------------------------------------------------------------------------------------#
   def verifySmart(self):
       """
         Utility verify SMART
       """
       if testSwitch.BYPASS_N2_CMD: #/1N2 cmd not ready yet
          objMsg.printMsg("VerifySmart return..")
          return

       if self.Status == OK:

          self.oGIO.powerCycle()

          if self.Status == OK: 
             data = self.oSerial.sendDiagCmd('/1N2') #Update SMART 
             CELogData = self.oSerial.sendDiagCmd('N8', printResult = True)

          if self.Status == OK:
             if not testSwitch.virtualRun: 
                res = self.oSerial.sendDiagCmd('N2')
             else:
                res = "SMART_THRESHOLD_NOT_EXCEEDED_LBA_KEY:C24F00"    
             if res: self.Status = OK
             objMsg.printMsg('SmartReturnStatus Data=%s' % str(res))
             data = {'LBA':0}
             data['LBA'] = re.split('LBA_KEY:',res)[1][:6] 

          if self.Status == OK:
             objMsg.printMsg('Smart Verify passed!')            
             if data.has_key('LBA') != 0: 
                data['CYL'] = int(data['LBA'],16) >> 8
                objMsg.printMsg('SmartReturnStatus LBA shifted 8=%d(0x%X)' % (data['CYL'], data['CYL']))               
                cyl = int(data['CYL'])
                cyl_low = cyl & 0xff
                cyl_high = cyl >> 8          
             if data.has_key('CYL') == 0:
                objMsg.printMsg('SMART Verify failed! SmartReturnStatus missing data(CYL). ' % self.Status)
                failure = 'Fin DST Thres'
                self.Status = FAIL
                self.errorcode = 12378
             else:
                cyl = int(data['CYL'])
                cyl_low = cyl & 0xff
                cyl_high = cyl >> 8
          else:
             objMsg.printMsg('Smart Verify failed!')  
             failure = 'IDT Verify Smart'
             self.errorcode = 13061

          if self.Status == OK:
             if (cyl_low == 0xf4) and (cyl_high == 0x2c):
                objMsg.printMsg("SMART Verify failed (threshold exceeded): Cyl=0x2CF4")
                objMsg.printMsg('Serious failure mode, no reruns allowed!')
                failure = 'Fin DST Thres'
                self.Status = FAIL
                self.errorcode = 12378

          if self.Status == OK:
             if data['LBA'] == 'C24F00':
                objMsg.printMsg('SMART Verify passed (thresholds not exceeded):Cyl=0xC24F')
             else:
                objMsg.printMsg("SMART Verify failed (invalid Cyl): not 0x2CF4 or 0xC24F")
                failure = 'Fin DST Thres'
                self.Status = FAIL
                self.errorcode = 12378   
          
          if self.Status != OK:
             objMsg.printMsg('Verify Smart failed!')      
             if not testSwitch.virtualRun:    
                getSerialPortData()
                ScrCmds.raiseException(self.errorcode, 'IDT_VERIFY_SMART_IDE Failed' )
          
       return self.Status

###########################################################################################################
class CRampTemp(CState):
   """
      Class that performs IDT_RAMP_TEMP test. 
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)
   #------------------------------------------------------------------------------------------------------#
   def selectDrvTempRamp(self):
       """
          Utility select drive for temp ramp based on serial number
       """

       select = 'NO'

       SNList = ['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F']
       objMsg.printMsg('Ramp Temp SN List = %s' %  SNList)
       if self.dut.serialnum[7] in SNList:
          objMsg.printMsg('Serial Number Match Selection, Drive test with temperature ramping.')
          select = 'YES'
       else:
          objMsg.printMsg('Ramp to 22deg with Wait - DriveOff, ReleaseHeater/Fan')      
          select = 'NO'          
       
       return select

   #------------------------------------------------------------------------------------------------------#
   def rampTemp(self, temp, Wait=ON, MaxH=600, UpRate=40, DownRate=10):
       """
          Utility to ramp temperature
       """
       SetTemperatureLimits(MaxH, UpRate, DownRate)

       if not self.dut.chamberType == 'NEPTUNE': 
          try:
             objMsg.printMsg('Set Cell Fans Speed - 3100, 2927')
             SetCellFans(3100, 2927)
          except:
             objMsg.printMsg('Set Cell Fans Speed not supported')
             pass

       if Wait == ON:
          objMsg.printMsg('Ramp To Temp %d with wait (Cell Temp=%s)' % (temp, str(ReportTemperature()) ))
          RampToTempWithWait(temp*10, 1)                  # temp in tenths of degrees
       else:
          objMsg.printMsg('Ramp To To Temp %d with No wait (Cell Temp=%s)' % (temp, str(ReportTemperature()) ))
          RampToTempNoWait(temp*10, 1)                    # temp in tenths of degrees

       if not self.dut.chamberType == 'NEPTUNE': 
          try:    ReleaseTheFans()  # Release Fan control
          except: pass

       return 0

###########################################################################################################
class CServoRecall(CState):
   """
      Class that performs IDT_SERVO_RECALL_TEST test. 
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)
      self.oGIO = CGIO(self.dut, params={})
   #---------------------------------------------------------------------------------------------------------#
   def doServoRecall(self, TestType='MQM', TestName='SERVO RECALL'):
      timeout = 60
      self.testName = ('%s %s' % (TestType, TestName))                       # Test Name for file formatting
      self.oGIO.powerCycle()

      try:
         objMsg.printMsg('*****************************************************************************')
         #sptCmds.gotoLevel('T')
         sptCmds.gotoLevel('5')
         objMsg.printMsg('ReCalCoeffBlock.i16_CosCoeff')
         data = sptCmds.sendDiagCmd("r168,2,80",timeout = timeout, printResult = True,)
         objMsg.printMsg('RecalMode : %s' % data[data.find('Servo Symbol'):])
         data = sptCmds.sendDiagCmd("r168,2,82",timeout = timeout, printResult = True,)
         objMsg.printMsg('RecalCount : %s' % data[data.find('Servo Symbol'):])

         objMsg.printMsg('ReCalCoeffBlock.i16_DCError:')
         data = sptCmds.sendDiagCmd("r168,2,0",timeout = timeout, printResult = True,)
         objMsg.printMsg('DCError[Head0][coeff0] : %s' % data[data.find('Servo Symbol'):])
         data = sptCmds.sendDiagCmd("r168,2,2",timeout = timeout, printResult = True,)
         objMsg.printMsg('DCError[Head0][coeff1] : %s' % data[data.find('Servo Symbol'):])
         data = sptCmds.sendDiagCmd("r168,2,4",timeout = timeout, printResult = True,)
         objMsg.printMsg('DCError[Head1][coeff0] : %s' % data[data.find('Servo Symbol'):])
         data = sptCmds.sendDiagCmd("r168,2,6",timeout = timeout, printResult = True,)
         objMsg.printMsg('DCError[Head1][coeff1] : %s' % data[data.find('Servo Symbol'):])

         objMsg.printMsg('ReCalCoeffBlock.i16_SinCoeff')
         data = sptCmds.sendDiagCmd("r168,2,70",timeout = timeout, printResult = True,)
         objMsg.printMsg('ACFF1X[head0][SINCoeff] : %s' % data[data.find('Servo Symbol'):])
         data = sptCmds.sendDiagCmd("r168,2,72",timeout = timeout, printResult = True,)
         objMsg.printMsg('ACFF1X[head1][SINCoeff] : %s' % data[data.find('Servo Symbol'):])

         objMsg.printMsg('ReCalCoeffBlock.i16_CosCoeff')
         data = sptCmds.sendDiagCmd("r168,2,78",timeout = timeout, printResult = True,)
         objMsg.printMsg('ACFF1X[head0][COSCoeff] : %s' % data[data.find('Servo Symbol'):])
         data = sptCmds.sendDiagCmd("r168,2,7A",timeout = timeout, printResult = True,)
         objMsg.printMsg('ACFF1X[head1][COSCoeff] : %s' % data[data.find('Servo Symbol'):])

         if data.find('RAM Data') >= 0:
            RecalCount = int(data[data.find('RAM Data')+len('RAM Data'):].split()[0],16)
            objMsg.printMsg('RecalCount: %d' % RecalCount)
            if RecalCount != 0:
               raise
         objMsg.printMsg('*****************************************************************************')
      except:
         objMsg.printMsg("Error in doServoRecall: %s" % traceback.format_exc())
         objMsg.printMsg("Warning:No matter what is RAM DATA value there,all pass.")

      return 0

###########################################################################################################
class CResetSMART(CState):
   """
      Class that performs Reset SMART
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)
      self.oGIO = CGIO(self.dut, params={})
   #---------------------------------------------------------------------------------------------------------#
   def ResetSmart(self, TestType='MQM', TestName='RESET SMART'):
      self.testName = ('%s %s' % (TestType, TestName))                       # Test Name for file formatting

      self.oGIO.powerCycle()

      self.oSerial = serialScreen.sptDiagCmds()
      data = self.oSerial.sendDiagCmd('/1N1')
      objMsg.printMsg("ResetSMART Done data: %s" % data)

###########################################################################################################


###########################################################################################################
class CBERByZone(CState):
   """
      Class that performs IDT_BER_BY_ZONE test. 
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)
      self.oGIO = CGIO(self.dut, params={})
   #---------------------------------------------------------------------------------------------------------#

   def doBERByZone(self,FLAG=1):
      TestType='IDT'
      self.testName = ('%s BER By Zone' % TestType)       # Test Name for file formatting

      if testSwitch.virtualRun:
         return

      self.oGIO.powerCycle(pwrOption = "pwrDefault")

      #self.printTestName(self.testName)
      #self.oRF.powerCycle('TCGUnlock')
      #self.oRF.disableAPM('GetSerialPortData')
      oSerial = serialScreen.sptDiagCmds()
      sptCmds.enableDiags()

      # ** Display Zone Table and collect last cyl of the zone **
      numCyls,zones = oSerial.getZoneInfoIOMQM(False,0,True)
      sptCmds.gotoLevel('T')
      sptCmds.gotoLevel('2')
      sptCmds.sendDiagCmd('x', timeout = 500, altPattern = None, printResult = True)

      for hd in zones.keys():
          num1=zones[hd]
          for zn in num1.keys():
              if zn==0:continue
              num2=num1[zn]-1
              objMsg.printMsg("last cyl of the head[%d]zone[%d] is %X" % (hd,zn-1,num2))
          objMsg.printMsg("last cyl of the head[%d]zone[%d] is %X" % (hd,zn,numCyls[hd]))

      #**Turn On BER collection **
      results=sptCmds.execOnlineCmd(CTRL_W, timeout = 20, waitLoops = 100)
      objMsg.printMsg('Turn on BER collection '+ str(results))

      #**Enable Error logging
      sptCmds.gotoLevel('L')
      sptCmds.sendDiagCmd("E1", timeout = 1000, altPattern = None, printResult = True)

      #**For each head, and each zone, do Q from last 100 tracks of the zone
      zoneStatus = {}
      for hd in zones.keys():
         zoneStatus[hd] = []
         num1=zones[hd]
         sptCmds.gotoLevel('2')
         sptCmds.sendDiagCmd('A2', timeout = 500, altPattern = None, printResult = True)
         for zn in num1.keys():
            if(zn==0):continue
            zoneStatus[hd].append(0)
            num2=num1[zn]-1
            num3=num2-100
            IS_BER_RETRY=0
            keepRetry=1
            while keepRetry:
               try:
                  sptCmds.gotoLevel('2')
                  sptCmds.sendDiagCmd("P0000,0000", timeout = 500, altPattern = None, printResult = True)
                  sptCmds.sendDiagCmd("S%X,%d"%(num3,hd) ,timeout = 1000,printResult = True)
                  sptCmds.sendDiagCmd("L,30" ,timeout = 1000,printResult = True)
                  sptCmds.sendDiagCmd("Q", timeout = 500, printResult = True, stopOnError = 0)
                  keepRetry=0
                  zoneStatus[hd][-1] = 1
               except:
                  if not IS_BER_RETRY:
                     num3=num2-500
                     IS_BER_RETRY=1
                  else:
                     keepRetry=0

         numCyls[hd]-=100
         keepRetry=1
         IS_BER_RETRY=0
         zoneStatus[hd].append(0)
         while keepRetry:
            try:
               sptCmds.sendDiagCmd("P0000,0000", timeout = 500, altPattern = None, printResult = True)
               sptCmds.sendDiagCmd("S%X,%d"%(numCyls[hd],hd) ,timeout = 1000,printResult = True)
               sptCmds.sendDiagCmd("L,30" ,timeout = 1000,printResult = True)
               sptCmds.sendDiagCmd("Q", timeout = 500, printResult = True, stopOnError = 0)
               keepRetry=0
               zoneStatus[hd][-1] = 1
            except:
               if not IS_BER_RETRY:
                  numCyls[hd]-=400
                  IS_BER_RETRY=1
               else:
                  keepRetry=0

      #**Display Zone BER summary
      results_ZoneBER= sptCmds.execOnlineCmd(SHIFT_4, timeout = 20, waitLoops = 100)
      objMsg.printMsg('Display Zone BER summary: '+ str(results_ZoneBER))
      oSerial=serialScreen.sptDiagCmds()
      information=oSerial.getZoneBERData_SMMY()
      objMsg.printMsg('###informationinformation###='+str(information))
      objMsg.printMsg('zoneStatus=%s' % zoneStatus)

      MQM_END_OTF_H0=0
      MQM_END_RAW_H0=0
      MQM_END_OTF_H1=0
      MQM_END_RAW_H1=0
      HD0_Length=0
      HD1_Length=0
      if FLAG==0:
         for item in information[0]:
            if item['HD_PHYS_PSN']=='0':
               if zoneStatus[int(item['HD_PHYS_PSN'])][int(item['DATA_ZONE'], 16)]:
                  self.dut.MQM_BEGIN_OTF_H0+=float(item['OTF'])
                  self.dut.MQM_BEGIN_RAW_H0+=float(item['RRAW'])
                  HD0_Length += 1
            elif item['HD_PHYS_PSN']=='1':
               if zoneStatus[int(item['HD_PHYS_PSN'])][int(item['DATA_ZONE'], 16)]:
                  self.dut.MQM_BEGIN_OTF_H1+=float(item['OTF'])
                  self.dut.MQM_BEGIN_RAW_H1+=float(item['RRAW'])

                  HD1_Length += 1
         if HD0_Length != 0:
            self.dut.MQM_BEGIN_OTF_H0/=float(HD0_Length)
            self.dut.MQM_BEGIN_RAW_H0/=float(HD0_Length)
            objMsg.printMsg('MQM_BEGIN_OTF_H0= '+str(self.dut.MQM_BEGIN_OTF_H0))
            objMsg.printMsg('MQM_BEGIN_RAW_H0= '+str(self.dut.MQM_BEGIN_RAW_H0))
         if HD1_Length != 0:
            self.dut.MQM_BEGIN_OTF_H1/=float(HD1_Length)
            self.dut.MQM_BEGIN_RAW_H1/=float(HD1_Length)
            objMsg.printMsg('MQM_BEGIN_OTF_H1= '+str(self.dut.MQM_BEGIN_OTF_H1))
            objMsg.printMsg('MQM_BEGIN_RAW_H1= '+str(self.dut.MQM_BEGIN_RAW_H1))
      else:
         objMsg.printMsg('self.dut.MQM_BEGIN_OTF_H0='+str(self.dut.MQM_BEGIN_OTF_H0))
         for item in information[0]:
            if item['HD_PHYS_PSN']=='0':
               if zoneStatus[int(item['HD_PHYS_PSN'])][int(item['DATA_ZONE'], 16)]:
                  MQM_END_OTF_H0+=float(item['OTF'])
                  MQM_END_RAW_H0+=float(item['RRAW'])
                  HD0_Length += 1
            elif item['HD_PHYS_PSN']=='1':
               if zoneStatus[int(item['HD_PHYS_PSN'])][int(item['DATA_ZONE'], 16)]:
                  MQM_END_OTF_H1+=float(item['OTF'])
                  MQM_END_RAW_H1+=float(item['RRAW'])
                  HD1_Length += 1
         if HD0_Length != 0:
            MQM_END_OTF_H0/=float(HD0_Length)
            MQM_END_RAW_H0/=float(HD0_Length)
            objMsg.printMsg('MQM_END_OTF_H0= '+str(MQM_END_OTF_H0))
            objMsg.printMsg('MQM_END_RAW_H0= '+str(MQM_END_RAW_H0))
            MQM_DELTA_OTF_H0=float(MQM_END_OTF_H0)-float(self.dut.MQM_BEGIN_OTF_H0)
            MQM_DELTA_RAW_H0=float(MQM_END_RAW_H0)-float(self.dut.MQM_BEGIN_RAW_H0)
            objMsg.printMsg('MQM_DELTA_OTF_H0= '+str(MQM_DELTA_OTF_H0))
            objMsg.printMsg('MQM_DELTA_RAW_H0= '+str(MQM_DELTA_RAW_H0))
         if HD1_Length != 0:
            MQM_END_OTF_H1/=float(HD1_Length)
            MQM_END_RAW_H1/=float(HD1_Length)
            objMsg.printMsg('MQM_END_OTF_H1= '+str(MQM_END_OTF_H1))
            objMsg.printMsg('MQM_END_RAW_H1= '+str(MQM_END_RAW_H1))
            MQM_DELTA_OTF_H1=float(MQM_END_OTF_H1)-float(self.dut.MQM_BEGIN_OTF_H1)
            MQM_DELTA_RAW_H1=float(MQM_END_RAW_H1)-float(self.dut.MQM_BEGIN_RAW_H1)
            objMsg.printMsg('MQM_DELTA_OTF_H1= '+str(MQM_DELTA_OTF_H1))
            objMsg.printMsg('MQM_DELTA_RAW_H1= '+str(MQM_DELTA_RAW_H1))


         if (abs(float(MQM_END_RAW_H0)) > 0 and abs(float(MQM_END_RAW_H0))<2.15) or (abs(float(MQM_END_RAW_H1)) > 0 and abs(float(MQM_END_RAW_H1))<2.15): #check RAW value
            ScrCmds.raiseException(10632,'Failed RAW value')


      #**Display Active Error log
      sptCmds.gotoLevel('2')
      res=sptCmds.sendDiagCmd("E", timeout = 1000, printResult = True)
      objMsg.printMsg('results_OTF_RAW='+str(res))
      p = 'Log FFFC Entries (?P<Entries>\d)'
      import re
      pat = re.compile(p)
      m=pat.search(res)
      if m:
         n=int(m.groupdict()['Entries'])
         objMsg.printMsg('n='+str(n))
         if not n==0:
            m=re.search("Partition",res)
            if not m == None:
               m = res[m.end():]
               m=m.splitlines()
               for line in m:
                  if line.find("User")>=0:
                     line=line.split()
                     objMsg.printMsg('line[2]='+str(line[2]))
                     if line[2] in ['43110081','C3160080','C4090081','C44400EA','C44400E2' ,'C4090081']:
                        ScrCmds.raiseException(10632,'R/W Test Failed')

      #self.oRF.powerCycle('TCGUnlock')
      self.oGIO.powerCycle(pwrOption = "pwrDefault")


###########################################################################################################
class CIdleAPMTest(CState):
   """
      Class that performs IDT_IDLE_APM_TEST test. 
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)
      self.oGIO = CGIO(self.dut, params={})
   #---------------------------------------------------------------------------------------------------------#
   def doIdleAPMTest(self, TestType='MQM', TestName='Idle APM Test'):
      timeout = 60
      self.testName = ('%s %s' % (TestType, TestName))                       # Test Name for file formatting
      self.oGIO.powerCycle()

      apmMsg = 'supported'
      apmDrive = 0
      minLBA = 0
      maxLBA = 200000
      loopTime = 900
      if not apmDrive:
         loopTime *= 2

      apmWaitMin = 30
      apmWaitMax = 600
      napmWait = 7
      udmaSpeed = 0x45
      mode2848 = 48

      objMsg.printMsg('%s APM is %s, StartLBA=%d, EndLBA=%d, LoopTime=%d sec, apmWaitMin=%d, apmWaitMax=%d, napmWait=%d, UDMA_Speed=0x%X' % \
                   (TestName, apmMsg, minLBA, maxLBA, loopTime, apmWaitMin, apmWaitMax, napmWait, udmaSpeed))

      data = ICmd.IdleAPMTest(apmDrive,minLBA,maxLBA,loopTime,apmWaitMin,apmWaitMax,napmWait,udmaSpeed,mode2848)
      objMsg.printMsg('IdleAPMTest Returned Data=%s' % (data))
                
      result = data['LLRET']
      if result != OK:
         objMsg.printMsg('%s Failed, Returned Data=%s' % (TestName, data))
         ScrCmds.raiseException(13085,'IDT_IDLE_APM_TEST Failed')
      else:
         objMsg.printMsg('%s Test Passed' % TestName)
         return 0

###########################################################################################################
class CSPLongDST(CGIO):
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      self.TestMode = "MODE_SPFIN"

      Modules = [       ('IDT_SHORT_DST_IDE'          , 'OFF'),
                        ('IDT_FULL_DST_IDE'           , 'ON'),
                        ('IDT_SERIAL_SDOD_TEST'       , 'OFF')]

      objMsg.printMsg("CSPLongDST Modules: %s" % Modules)
      CInit_Testing(self.dut, params={}).run()
      self.RunModules(Modules)
      objMsg.printMsg("CSPLongDST Modules end")


###########################################################################################################
class CSuperParityCleanUp(CState):
   """
      Class that performs IDT_SUPER_PARITY_CLEANUP
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)
      self.oGIO = CGIO(self.dut, params={})

   #---------------------------------------------------------------------------------------------------------#
   def doSuperParityCleanUp(self, TestType='MQM', TestName='Super Parity Cleanup'):
      self.testName = ('%s %s' % (TestType, TestName))                       # Test Name for file formatting
      self.oGIO.powerCycle()

      self.oSerial = serialScreen.sptDiagCmds()
      SPRatio = self.oSerial.GetSPRatio(getCTRL_L = True)
      objMsg.printMsg('Before SPRatio=%s' % SPRatio)
      objMsg.printMsg('SPRatio Spec.=%s' % float(getattr(TP, 'SPRatio', 1)))
      self.dut.driveattr['PROC_CTRL7'] = SPRatio

      '''
      if SPRatio == 0:
         objMsg.printMsg('%s Test Passed' % TestName)
         return
      '''

      if SPRatio > float(getattr(TP, 'SPRatio', 1)):
         if testSwitch.INVALID_SUPER_PARITY_FULL_PACK_WRITE:
            # write pass drive, until G>Q,,22 is SMR friendly
            objMsg.printMsg("SPRatio > spec, write pass drive.")
            CWriteDriveZero(self.dut, params={}).doWriteZeroPatt('MQM', 'MaxLBA')
         else:
            sptCmds.gotoLevel('G')

            try:
               data = sptCmds.sendDiagCmd("/GQ,,22",timeout = 5400, printResult = True)
            except:
               objMsg.printMsg("Error in Q,,22: %s" % traceback.format_exc())
               if not ConfigVars[CN]['BenchTop']:
                  raise

         SPRatio = self.oSerial.GetSPRatio(getCTRL_L = True)
         objMsg.printMsg('After SPRatio=%s' % SPRatio)

         if SPRatio > float(getattr(TP, 'SPRatio', 1)):
            ScrCmds.raiseException(48665,'IDT_SUPER_PARITY_CLEANUP Failed')
         else:
            objMsg.printMsg('%s Test Passed' % TestName)
      else:
         objMsg.printMsg('%s Test Passed' % TestName)

###########################################################################################################
class CShortScreen(CState):
   def __init__(self, dut, params=[]):
      self.dut = dut
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.oSerial = serialScreen.sptDiagCmds()
      self.oGIO = CGIO(self.dut, params={})
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if testSwitch.NoIO == 0:
         return
      try:
         if self.dut.driveattr.get('PROC_CTRL51', 'NONE') == 'DONE':
            return
      except:
         pass
      
      self.oGIO.powerCycle()
      try:
         CGetSMARTLogs(self.dut, params={}).checkSmartLogs([0xA1, 0xA8, 0xA9])
      except:
         objMsg.printMsg(traceback.format_exc())

      try:
         sptCmds.enableDiags()
         self.oSerial.dumpReassignedSectorList()
         self.oSerial.dumpActiveServoFlaws()
      except:
         objMsg.printMsg(traceback.format_exc())

      try:
         try:
            CSmartDST_SPT(self.dut, params={}).DSTTest_IDE('SHORT_SCREEN','Short')
         except:
            self.dut.driveattr['PROC_CTRL30'] = '0X%X' % (int(self.dut.driveattr.get('PROC_CTRL30', '0'),16) | TP.Proc_Ctrl30_Def['ShortScreen'])
            objMsg.printMsg(traceback.format_exc())

         try:
            sptCmds.enableDiags()
         except:
            self.oGIO.powerCycle()
            sptCmds.enableDiags()

         self.oSerial.enableRWStats()

         sptCmds.gotoLevel('2')
         randomLoops = 10000 * self.dut.imaxHead
         objMsg.printMsg('Reading from 0 to %s randomly with sector count 256, %d loops'%(self.dut.IdDevice["Max LBA Ext"], randomLoops))
         try:
            res = ICmd.RandomReadDMAExt(0, self.dut.IdDevice["Max LBA Ext"], 256, 256, randomLoops)
         except:
            self.dut.driveattr['PROC_CTRL30'] = '0X%X' % (int(self.dut.driveattr.get('PROC_CTRL30', '0'),16) | TP.Proc_Ctrl30_Def['ShortScreen'])
         if res['LLRET'] != OK:
            objMsg.printMsg('CShortScreen - data: %s'%str(res))
            self.dut.driveattr['PROC_CTRL30'] = '0X%X' % (int(self.dut.driveattr.get('PROC_CTRL30', '0'),16) | TP.Proc_Ctrl30_Def['ShortScreen'])
         
         headData = self.oSerial.getHeadBERData(printResult = True)
         objMsg.printMsg('Shortscreen-BER: %s'% headData)
         for entry in headData:
            if float(entry['OTF']) <= 7.7:
               objMsg.printMsg('Hd %s, Shortscreen-OTF is %s <= 7.7' % (entry['HD_PHYS_PSN'], entry['OTF']))
               self.dut.driveattr['PROC_CTRL30'] = '0X%X' % (int(self.dut.driveattr.get('PROC_CTRL30', '0'),16) | TP.Proc_Ctrl30_Def['ShortScreen'])
         
      except:
         objMsg.printMsg(traceback.format_exc())

      try:
         CGetSMARTLogs(self.dut, params={}).checkSmartLogs([0xA1, 0xA8, 0xA9])
         objMsg.printMsg('get CriticalEvents done')
      except:
         objMsg.printMsg(traceback.format_exc())
      try:
         sptCmds.enableDiags()
         self.oSerial.dumpReassignedSectorList()
         self.oSerial.dumpActiveServoFlaws()
      except:
         objMsg.printMsg(traceback.format_exc())
      self.oGIO.powerCycle()
      self.dut.driveattr['PROC_CTRL51'] = 'DONE'

###########################################################################################################
