#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
import DbLog
import ScrCmds
from Process import CProcess

import MessageHandler as objMsg
from PowerControl import objPwrCtrl
from Drive import objDut
from IOEDC import ChkIOEDC
from ICmdFactory import ICmd
import IntfClass
from IntfClass import HardReset
from base_SATA_ICmd_Params import *
from base_IntfTest import *
import serialScreen, sptCmds

from Utility import CUtility

from ReliFunction import *
from ReliRamTest import *
from ReliFileCompare import *
from ReliFailCode import *
from ReliTCG import *


import os
import time
import random
from random import randint
import re
from Rim import objRimType
GLOBAL_MQM_BEGIN_OTF_H0=0
GLOBAL_MQM_BEGIN_OTF_H1=0
GLOBAL_MQM_BEGIN_RAW_H0=0
GLOBAL_MQM_BEGIN_RAW_H1=0
GLOBAL_MQM_END_OTF_H0=0
GLOBAL_MQM_END_OTF_H1=0
GLOBAL_MQM_END_RAW_H0=0
GLOBAL_MQM_END_RAW_H1=0


##############################################################################################################


wordTuple = CUtility.ReturnTestCylWord
lbaTuple = CUtility.returnStartLbaWords

OK = 0
FAIL = -1
ON = 1
OFF = 0

##############################################################################################################
def timetostring(testtime):
    h = testtime / 3600
    m = ((testtime / 60) % 60)
    s = testtime % 60
    timestring = '%02d:%02d:%02d' % (h, m, s)
    return timestring

##############################################################################################################
class gioTestException(Exception):
   def __init__(self,data):
      self.data = data
      objMsg.printMsg('GIO Test Exception')

##############################################################################################################
class CGIOTest(CProcess):
   #------------------------------  IDT Test Setup Section  ---------------------------------#
   #IDT_RAMP_FIN_TEMP          = ON               # IDT Ramp Slot to FIN Temperature in Config.
   #Turn OFF Temp Ramp as per TechKhoon - MQM_UNF21D2_3 (Base:MQM_UNF21D2_2) - 12-Jan-2012
   IDT_RAMP_TEMP               = OFF               # IDT Ramp Slot to Hot/Ambient Temperature in Config.
   IDT_GET_IDENTIFY            = ON               # IDE Get Identify data sector from drive.
   IDT_CHECK_ATA_REV           = OFF              # IDE Check ATA rev, drive vs. config.
   IDT_CHECK_CONGEN_REV        = OFF              # IDE Check Congen rev, drive vs. config.
   IDT_RETRY_TEST_STEPS        = ON               # IDE Retry failures, for specific tests
   IDT_CHECK_SMART_C_E         = OFF              # IDE Verify SMART, Check Critical Events

   # Switches for F.A. Debug
   IDT_FA_RESET_SMART          = OFF              # IDE Reset Smart, ON/OFF,  Before DST
   IDT_FA_VERIFY_SMART_1       = OFF              # IDE Verify Smart, ON/OFF, Before DST
   IDT_FA_DEBUG_FULL_DST       = OFF              # IDE Run Full DST Read, ON for F.A. Debug
   IDT_FA_VERIFY_SMART_2       = OFF              # IDE Verify Smart, ON/OFF, After DST

   # Section #1 - Integration
   IDT_WRT_RD_PERFORM          = ON               # IDE Weak Write, Read Performance test.
   IDT_VERIFY_SMART_IDE        = ON               # IDE Verify SMART, Reset with L1/N1
   IDT_SYSTEM_FILE_LOAD        = ON               # IDE Diagnostic Program load test.
   IDT_WRITE_TEST_MOBILE       = OFF              # IDE Write Test for Mobile drives.
   IDT_IMAGE_FILE_COPY         = ON               # IDE Single/Multi Sector write/read.
   IDT_IMAGE_FILE_READ         = ON               # IDE Multi Sector read.
   IDT_VOLTAGE_HIGH_LOW        = ON               # IDE Power Cycle X times at Nom, High, Low.
   IDT_SHORT_DST_IDE           = ON               # IDE Drive Self Test, Short.
   IDT_READ_TEST_MOBILE        = ON               # IDE Read Test for Mobile drives.
   IDT_READ_TEST_DRIVE         = ON               # IDE Read Test for all drives.
   IDT_LOW_DUTY_CYCLE          = ON               # IDE Occasional Random Length write/reads.
   IDT_OS_WRITE_TEST           = ON               # IDE 16 Sector Xfers, Seeded Random Pattern.
   IDT_OS_READ_COMPARE         = ON               # IDE Read Compare. Seeded Random Pattern
   IDT_OS_READ_REVERSE         = ON               # IDE Read Compare. Seeded Random Pattern
   IDT_WRITE_PATTERN           = ON               # IDE Write Fixed Pattern to the Drive.
   IDT_READ_PATTERN_FORWARD    = ON               # IDE Read Fixed Pattern from the Drive Forward.
   IDT_READ_PATTERN_RANDOM     = OFF               # IDE Read Fixed Pattern from the Drive Random.
   IDT_DELAY_WRT               = ON               # IDE Delay Write
   IDT_MS_SUS_TXFER_RATE       = ON               # IDE MSFT Sustain Transfer Rate
   IDT_ENCROACHMENT_EUP        = ON               # IDE Encroachment EUP
   IDT_PM_BLUENUNSCAN          = OFF#OFF          # IDE Bluenun Scan
   IDT_PM_BLUENUNSLIDE         = OFF#OFF          # IDE Bluenun Slide
   IDT_PM_ZONETHRUPUT          = ON               # IDE Perf Measure - Zonal Thruput Degrade


   # Section #2 - Customer Specific               # ConfigVar 'Apple CST Screen' to turn ON/OFF
   IDT_DST_INTERRUPT           = OFF              # IDE Remove power during DST.
   IDT_UNLOAD_IMMEDIATE        = OFF              # IDE Unload Immediate and Retract.
   IDT_MULTIMODE_WRITE         = OFF              # IDE Multiple Mode Write Test.
   IDT_UDMA_MULTI_SWITCH       = OFF              # IDE UDMA Multiple Mode Switch Test.
   IDT_MULTI_WR_SINGLE_RD      = OFF              # IDE Multiple Write Single Read Test.
   IDT_WRITE_SIMULATION        = OFF              # IDE Copy Station Simulation Test.

   #RT010811: if DVR testing applies, LongDST is performed after ReadZeroCompare
   #RT090911: this value is now controlled by config
   #IDT_DVR_TEST                         = OFF          #DVR settings apply

   # Section #3 - Seagate Specific
   IDT_RANDOM_WRITE_TEST       = ON               # IDE Random Location writes, ATA I/O.
   IDT_FULL_DST_IDE            = ON               # IDE Drive Self Test, Full/Long.
   IDT_MISCOMP_RAM_TEST        = ON               # IDE Drive Miscompare RAM Test.
   IDT_GET_SMART_LOGS          = ON               # IDE Get SMART Logs A1, A8, A9.
   IDT_WRITE_DRIVE_ZERO        = ON               # IDE Write 0x00 Pattern to the Drive.
   IDT_READ_ZERO_VERIFY        = OFF#OFF          # IDE Read Verify 0x00(Read Verify ATA command).
   IDT_READ_ZERO_COMPARE       = ON               # IDE Read Compare 0x00(Read Compare CPC function).
   IDT_IDLE_APM_TEST           = ON               # IDE Test Drive APM in Idle Mode.
   IDT_IDLE_APM_TTR_TEST       = OFF#OFF          # IDE Idle APM TTR S3/S4 Test
   #Turn OFF IDT_STM_IDLE_TEST as per TechKhoon - MQM_UNF21D2_4 (Base:MQM_UNF21D2_3) - 18-Jan-2012
   IDT_STM_IDLE_TEST           = OFF               # IDE STM Idle Test
   #Turn OFF IDT_ODTATI_TEST as per TechKhoon - MQM_UNF21D2_3 (Base:MQM_UNF21D2_2) - 12-Jan-2012
   IDT_ODTATI_TEST             = OFF               # IDE ATI Test
   IDT_SERIAL_SDOD_TEST        = ON               # IDE SDOD Serial Test
   IDT_MOA_SDOD_LUL_TEST       = OFF#OFF          # IDE MOA SDOD LUL Test

   # Section #4 - Data Collection
   IDT_RESULT_FILE_DATA        = OFF              # Collect and Send Result file Data
   IDT_SEND_ST_ATTR            = ON               # Send the Seatrack Attributes
   IDT_SEND_ST_PARAM           = OFF              # Send the Seatrack Parametrics
   IDT_POWER_CYCLE_DATA        = OFF              # Collect and send Power Cycle Data
   IDT_OUTPUT_FILE_DATA        = OFF              # Collect and Send Output file Data

   # Section 5 - Save for Future Use              # Do Not Remove these Switches
   IDT_POWER_CYCLE_1           = 'NONE'           # IDE Power Cycle and Ready Check.
   IDT_POWER_CYCLE_2           = 'NONE'           # Power Cycle and Ready Check.
   IDT_POWER_CYCLE_3           = 'NONE'           # Power Cycle, Future Use, Do Not Remove
   IDT_POWER_CYCLE_4           = 'NONE'           # Power Cycle, Future Use, Do Not Remove
   IDT_POWER_MULTIPLE          = 'NONE'           # Power Multi, Future Use, Do Not Remove
   #IDT_CHECK_SMART_C_E        = 'NONE'           # IDE Verify SMART, Check Critical Events
   IDT_SEQ_READ_BY_ZONE        = 'NONE'           # IDE Performance by zone, LBA's/16=zone.
   #IDT_READ_ZERO_VERIFY       = 'NONE'           # IDE Read Verify 0x00(Read Verify ATA command).
   IDT_SEEK_INTERRUPT          = 'NONE'           # IDE Remove power during SEEK.
   IDT_BUTTERFLY_SEEK_TIME     = 'NONE'           # IDE Butterfly Seek Time Measurements.
   IDT_TWO_POINT_SEEK_TIME     = 'NONE'           # IDE Two Point Seek Time Measurements.
   IDT_NON_DESTRUCT_WRITE      = 'NONE'           # IDE Non-Destructive Write Test.
   IDT_DESTRUCTIVE_WRITE       = 'NONE'           # IDE Destructive Write Test.

   #---------------------------------------------------------------------------------------------------------#
   def __init__(self, dut, params=[],isCPC=0):
      objMsg.printMsg('GIO Test Begin')
      CProcess.__init__(self)
      CE,CP,CN,CV = ConfigId
      self.ConfigName = CN

      self.testStartTime = time.time()
      self.driveAttr = {}
      self.reliAttr =()

      self.scriptInfo = \
      {
         'IDT Script Rev'           : 'MQM Unified 2.1d2_9f',
         'IDT SW Date'              : '2012.09.19',
      }

      #Init params
      result = OK
      self.printTestName('IDT Test Init - Script Rev %s' % self.scriptInfo['IDT Script Rev'])

      self.currentStep = ''
      self.testCmdCount = 0
      self.testCmdTime = 0
      self.testTimeSec = 0
      self.failCode = 0
      self.failStep = ''
      self.failLBA = 0
      self.failLLRET = 'NIL'
      self.failStatus = 'NIL'
      self.blockSize = 512
      # Reli function
      #self.oRF = ReliFunction.CReliFunction(self.testStartTime)
      self.isCPC = isCPC

      self.MQMV = 0

      # DT081110 Standardize ReliFunction
#      if (isCPC == 0):
#         self.oRF = CReliFunction(self.testStartTime)
#      else:
#         self.oRF = CReliFunction_CPC(self.testStartTime)

      self.oRF = CReliFunction(self.testStartTime)
      self.oFC = CReliFailCode()

      # test
      self.testName = 'GIO Init'
      self.sectorCount = 256
      self.minLBA = 0
      self.maxLBA = self.oRF.IDAttr['MaxLBA']
      self.stampFlag   = 0
      self.compareFlag = 0

      self.FLAG=0
      # CM Timeout
      #RT230911: reduce timeout to 5hrs to make it more relevant to NSG context
      #self.CMTimeOut = 60 * 60 * 10
      self.CMTimeOut = 60 * 60 * 5

      #RT: N2 support, use N2 ambient temperature setting
      if cellTypeString == 'Neptune2':
         self.AmbTemp = prm_GIOSettings['IDT N2 Ambient Temp']
      else :
         self.AmbTemp = prm_GIOSettings['IDT Ambient Temp']

      self.HotTemp = prm_GIOSettings['IDT Hot Temp']

      if DriveAttributes.has_key('FNC_TEST_DONE') == 0:
         self.driveAttr['FNC_TEST_DONE'] = 'NONE'

      #RT220911: SET_OPER setting shifted to setup.py
      #if DriveAttributes.has_key('SET_OPER'):
      #   self.driveAttr['SET_OPER'] = 'NONE'

      if ConfigVars[CN].has_key('DRV_RIDE'):
         self.driveAttr['DRV_RIDE'] = ConfigVars[CN].get('DRV_RIDE','N')             # Initialise to 'N'. For GIO post-AUD flow, Not related to powerloss recovery


      self.driveAttr['HoldDrive'] = ConfigVars[CN].get('holdDrive', 1)             # Initialise to 'N'. For GIO post-AUD flow, Not related to powerloss recovery

      if prm_GIOSettings.has_key('IDT Oper') and prm_GIOSettings['IDT Oper'] == 'CST2':
         self.driveAttr["LODT"] = 'NONE'


      self.driveAttr['MQM_SCRIPT_REV'] = self.scriptInfo['IDT Script Rev']
      self.driveAttr['IDT_SCRIPT_REV'] = self.scriptInfo['IDT Script Rev']
      self.driveAttr['MQM_TEST_TYPE'] = prm_GIOSettings['IDT Type']
      self.driveAttr['MQM_START_TIME'] = self.testStartTime
      self.driveAttr['MQM_CONFIG_NAME'] = self.ConfigName
      self.driveAttr['MQM_FIRMWARE_VER'] = self.oRF.IDAttr['FirmwareRev']
      self.driveAttr['PROC_CTRL22'] = 'NONE'

      #RT 15062011 Shift celltype and platformtype here from idttestend, QA request to see these attributes even when exception occurs in script locations beyond CGIOTest
      #RT 28102010 Add attribute to indicate the cell that was used
      #RT 30032011 Rewrite to leverage on method in ReliFunction
      self.driveAttr['IDT_CELL_TYPE'] = self.oRF.getCellType()

      #RT250511: Add attribute to indicate the platform the test was running on
      self.driveAttr['IDT_PLATFORM_TYPE'] = self.oRF.getPlatformType()
      self.driveAttr['MQM_TEST_DONE'] = 'PENDING'

      objMsg.printMsg('*'*50)
      objMsg.printMsg('*** GIO Script Rev=%s Dated[%s]' % (self.driveAttr['MQM_SCRIPT_REV'], self.scriptInfo['IDT SW Date']))
      objMsg.printMsg('*** GIO Test Type=%s' % self.driveAttr['MQM_TEST_TYPE'])
      objMsg.printMsg('*** GIO Config Name=%s' % self.driveAttr['MQM_CONFIG_NAME'])
      objMsg.printMsg('*** GIO Hot Temp=%d DegC' % self.HotTemp)
      objMsg.printMsg('*** GIO Ambient Temp=%d DegC' % self.AmbTemp)
      objMsg.printMsg('*** GIO Hold Drive=%d' %  self.driveAttr['HoldDrive'])
      objMsg.printMsg('IDT_CELL_TYPE=%s' % self.driveAttr['IDT_CELL_TYPE'])
      objMsg.printMsg('IDT_PLATFORM_TYPE=%s' % self.driveAttr['IDT_PLATFORM_TYPE'])

      if ConfigVars[CN].has_key('CM TIMEOUT') and ConfigVars[CN]['CM TIMEOUT'] != UNDEF:
         self.CMTimeOut = ConfigVars[CN].get('CM TIMEOUT', self.CMTimeOut)

      # DT SIC
      if objRimType.CPCRiser() and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION: #SetRFECmdTimeout only for Intrinsic function
         ICmd.SetRFECmdTimeout(self.CMTimeOut)
         objMsg.printMsg('*** Set CM Timeout = %d' % self.CMTimeOut)

      objMsg.printMsg('*'*50)
      DriveAttributes.update(self.driveAttr)

      self.dut = objDut

      #RT110811: CE dump switch
      self.doCEDump = ConfigVars[CN].get('CE_DUMP','YES')  #default it to dump, override it in config to switch off

   #---------------------------------------------------------------------------------------------------------#
   def idtTestSetup(self):

      return 0

   #---------------------------------------------------------------------------------------------------------#
   def idtTestInit(self):

      result = OK
      self.printTestName('IDT Test Init - Script Rev %s' % self.scriptInfo['IDT Script Rev'])

      self.currentStep = ''
      self.testCmdCount = 0
      self.testCmdTime = 0
      self.testTimeSec = 0
      self.failCode = 0
      self.failStep = ''
      self.failLBA = 0
      self.failLLRET = 'NIL'
      self.failStatus = 'NIL'
      self.blockSize = 512


      self.idtTestLoops = prm_GIOSettings['IDT Loops']

      ICmd.InterfaceCmdCount(reset=1)

      # Set TTR
      objMsg.printMsg("Set Spin Up Time Limit to %d ms" % prm_GIOSettings['IDT Ready Limit'])
      objPwrCtrl.readyTimeLimit = prm_GIOSettings['IDT Ready Limit']

      # Pre GIO Screen
      result = self.oRF.preGIOScreen()
      if result == OK:
         objMsg.printMsg("GIO Pre-Test Screen passed")
         self.driveAttr['MQM_PRE_SCREEN'] = 'PASS'
      else:
         objMsg.printMsg("GIO Pre-Test Screen failed")
         self.driveAttr['MQM_PRE_SCREEN'] = 'FAIL'
         self.updateFailureAttr()

      # DT140910 (Shelved)
      #self.oRF.clearlogforODTV(0)
      return result

   #---------------------------------------------------------------------------------------------------------#
   def idtTestEnd(self, testStatus):
      self.printTestName('IDT Test End - Test %s' % testStatus, setTestStep='OFF')

      self.testEndTime = time.time()
      self.driveAttr['MQM_TEST_DONE'] = testStatus
      self.driveAttr['MQM_END_TIME'] = timetostring(self.testEndTime)
      self.driveAttr['MQM_TEST_TIME'] = timetostring(self.testEndTime-self.testStartTime)
      self.driveAttr['TEST_TIME'] = '%.2f' % (time.time() - self.dut.birthtime)

      objMsg.printMsg('MQM_TEST_DONE=%s' % self.driveAttr['MQM_TEST_DONE'])
      objMsg.printMsg('MQM_END_TIME=%s' % self.driveAttr['MQM_END_TIME'])
      objMsg.printMsg('MQM_TEST_TIME=%s' % self.driveAttr['MQM_TEST_TIME'])


      if testStatus == 'FAIL':
         self.driveAttr['MQM_FAIL_TTF'] = timetostring(self.testEndTime-self.testStartTime)
         self.driveAttr['MQM_FAIL_SEQ'] = self.currentStep
         self.driveAttr['MQM_FAIL_LBA'] = self.failLBA
         self.driveAttr['MQM_FAIL_CODE'] = self.failCode
         self.driveAttr['MQM_FAIL_LLRET'] = self.failLLRET
         self.driveAttr['MQM_FAIL_STATUS'] = self.failStatus
      else:
         self.driveAttr['MQM_FAIL_TTF'] = 'NIL'
         self.driveAttr['MQM_FAIL_SEQ'] = 'NIL'
         self.driveAttr['MQM_FAIL_LBA'] = 'NIL'
         self.driveAttr['MQM_FAIL_CODE'] = 'NIL'
         self.driveAttr['MQM_FAIL_LLRET'] = 'NIL'
         self.driveAttr['MQM_FAIL_STATUS'] = 'NIL'


      objMsg.printMsg('MQM_FAIL_TTF=%s' % self.driveAttr['MQM_FAIL_TTF'])
      objMsg.printMsg('MQM_FAIL_SEQ=%s' % self.driveAttr['MQM_FAIL_SEQ'])
      objMsg.printMsg('MQM_FAIL_LBA=%s' % self.driveAttr['MQM_FAIL_LBA'])
      objMsg.printMsg('MQM_FAIL_CODE=%s' % self.driveAttr['MQM_FAIL_CODE'])
      objMsg.printMsg('MQM_FAIL_LLRET=%s' % self.driveAttr['MQM_FAIL_LLRET'])
      objMsg.printMsg('MQM_FAIL_STATUS=%s' % self.driveAttr['MQM_FAIL_STATUS'])
      objMsg.printMsg('PROC_CTRL22=%s' % self.driveAttr['PROC_CTRL22'])

      # standard
      self.driveAttr['MQM_TEST_LOOPS'] = self.idtTestLoops
      self.driveAttr['MQM_FAIL_LOOP'] = self.currentIDTLoop
      objMsg.printMsg('MQM_TEST_LOOPS=%s' % self.driveAttr['MQM_TEST_LOOPS'])
      objMsg.printMsg('MQM_FAIL_LOOP=%s' % self.driveAttr['MQM_FAIL_LOOP'])



      DriveAttributes.update(self.driveAttr)

      return 0

   #---------------------------------------------------------------------------------------------------------#
   def dGIOTest(self):
      result =  OK
      data = {}
      objMsg.printMsg(">>>>>>>>>> Start GIO Test")

      try:
         self.idtTestSetup()
         result = self.idtTestInit()
         for loop in range(1,self.idtTestLoops+2):

            objMsg.printMsg('Start IDT Test loop=%d self.idtTestLoops=%d' % (loop, self.idtTestLoops))

            self.currentIDTLoop = loop
            if self.idtTestLoops > 1 and result == OK:
               self.printTestName('IDT Test Loop %d of %d' % (self.currentIDTLoop, self.idtTestLoops), setTestStep='OFF')

            try:
               if ConfigVars[CN]['BenchTop']:

                  if loop == 1:
                     dummy  # simulate exception!!!
                     result = -1

                  objMsg.printMsg('Benchtop dummy MQM test here...')

               else:

                  #YHN
                  objMsg.printMsg('save self.IDT_RAMP_TEMP before temperature ramp to Ambient Temp')
                  self.temp_IDT_RAMP_TEMP = self.IDT_RAMP_TEMP
                  self.IDT_RAMP_TEMP = ON

                  if self.IDT_RAMP_TEMP == ON and not ConfigVars[CN]['BenchTop'] and result == OK:
                     # DT081210 Added for Multi-LODT loop
                     ICmd.FlushCache()
                     ICmd.StandbyImmed()
                     objMsg.printMsg('FlushCache and StandbyImmed')
                     DriveOff()
                     objMsg.printMsg('Drive power off prior Temperature Ramping to ambient')
                     self.oRF.rampTemp(self.AmbTemp)

                  #YHN
                  objMsg.printMsg('Restore self.IDT_RAMP_TEMP')
                  self.IDT_RAMP_TEMP = self.temp_IDT_RAMP_TEMP

                  #Loop IDT_WRT_RD_PERFORM & IDT_SYSTEM_FILE_LOAD sequence 5x times.
                  #As per TechKhoon - MQM_UNF21D2_4 (Base:MQM_UNF21D2_3) - 18-Jan-2012
                  for i in range(5):
                     #Do 5x "SystemFileLoad"  immediately after "VerifySmart" module.
                     #As per TechKhoon - MQM_UNF21D2_3 (Base:MQM_UNF21D2_2) - 12-Jan-2012
                     if self.IDT_SYSTEM_FILE_LOAD == ON and result == OK:
                        result = self.doSystemFileLoad()
                        if self.doCEDump == 'YES' :
                           # Display Smart Logs
                           self.oRF.checkSmartLogs([0xA1, 0xA8, 0xA9], OFF)
                           # Display Smart Attr
                           self.oRF.checkSmartAttr(OFF)

                     if self.IDT_WRT_RD_PERFORM == ON and result == OK:
                        result,data = self.doWriteReadPerform()

                     if self.IDT_VERIFY_SMART_IDE == ON and result == OK:
                        result = self.oRF.verifySmart()
                        if result != OK: self.updateFailureAttr()
                        if result == OK:
                           self.oRF.checkSmartLogs([0xA1, 0xA8, 0xA9])
                           result = self.oRF.Status
                        if result != OK: self.updateFailureAttr()

                     # DT141211 Add Drive Off
                     if self.IDT_RAMP_TEMP == ON and result == OK:

                        if (self.oRF.selectDrvTempRamp() == 'YES'):
                           #RT081111: add flushcache standbyimmediate
                           ICmd.FlushCache()
                           ICmd.StandbyImmed()
                           objMsg.printMsg('FlushCache and StandbyImmed')
                           #RT251011: drive off prior to temp ramping
                           DriveOff()
                           self.oRF.rampTemp(self.HotTemp, OFF, 600, 3, 3)
                           self.driveAttr['TEMP_RAMP'] = 'YES'
                        else:
                           if not cellTypeString == 'Neptune2':
                              ReleaseTheHeater()
                           self.oRF.rampTemp(self.AmbTemp, ON, 600, 3, 3)
                           if not cellTypeString == 'Neptune2':
                             ReleaseTheFans()
                           self.driveAttr['TEMP_RAMP'] = 'NO'

                        DriveAttributes.update(self.driveAttr)

                  #Add another "IdleAPMTest" immediately after this 5x of  "SystemFileLoad" test.
                  #As per TechKhoon - MQM_UNF21D2_3 (Base:MQM_UNF21D2_2) - 12-Jan-2012
                  if self.IDT_IDLE_APM_TEST == ON and result == OK:
                     result = self.doIdleAPMTest()
                     if self.doCEDump == 'YES' :
                        # Display Smart Logs
                        self.oRF.checkSmartLogs([0xA1, 0xA8, 0xA9], OFF)
                        # Display Smart Attr
                        self.oRF.checkSmartAttr(OFF)

                  self.doServoRecall()
                  self.doBERByZone(self.FLAG)

                  if self.IDT_WRITE_TEST_MOBILE == ON and result == OK:
                     #RT220911: requested by James Teng, CM Timeout set to 15mins prior to Write Mobile
                     #WriteMobileTimeout = 15*60
                     #RT230911: change to 30mins, 4K sect drives require more time to complete
                     WriteMobileTimeout = 30*60
                     ICmd.SetRFECmdTimeout(WriteMobileTimeout)
                     objMsg.printMsg('*** Set CM Timeout = %d' % WriteMobileTimeout)
                     result,data = self.doWriteTestMobile()
                     ICmd.SetRFECmdTimeout(self.CMTimeOut)
                     objMsg.printMsg('*** Set CM Timeout = %d' % self.CMTimeOut)

                     if self.doCEDump == 'YES' :
                        # DT240211 PE
                        # Display Smart Logs
                        self.oRF.checkSmartLogs([0xA1, 0xA8, 0xA9], OFF)
                        # Display Smart Attr
                        self.oRF.checkSmartAttr(OFF)

                  if self.IDT_IMAGE_FILE_COPY == ON and result == OK:
                     result,data = self.doImageFileCopy()

                     if self.doCEDump == 'YES' :
                        # DT240211 PE
                        # Display Smart Logs
                        self.oRF.checkSmartLogs([0xA1, 0xA8, 0xA9], OFF)
                        # Display Smart Attr
                        self.oRF.checkSmartAttr(OFF)

                  if self.IDT_IMAGE_FILE_READ == ON and result == OK:
                     result,data = self.doImageFileRead()

                     if self.doCEDump == 'YES' :
                        # DT240211 PE
                        # Display Smart Logs
                        self.oRF.checkSmartLogs([0xA1, 0xA8, 0xA9], OFF)
                        # Display Smart Attr
                        self.oRF.checkSmartAttr(OFF)

                  #RT020811: Shift to perform right after ATI
                  #if self.IDT_VOLTAGE_HIGH_LOW == ON and result == OK:
                  #   self.doVoltageHighLow()
                  if self.IDT_SHORT_DST_IDE == ON and result == OK:
                     result = self.DSTTest_IDE('Short')

                     if self.doCEDump == 'YES' :
                        # DT240211 PE
                        # Display Smart Logs
                        self.oRF.checkSmartLogs([0xA1, 0xA8, 0xA9], OFF)
                        # Display Smart Attr
                        self.oRF.checkSmartAttr(OFF)

                  if self.IDT_READ_TEST_MOBILE == ON and result == OK:
                     result,data = self.doReadTestMobile()

                     if self.doCEDump == 'YES' :
                        # DT240211 PE
                        # Display Smart Logs
                        self.oRF.checkSmartLogs([0xA1, 0xA8, 0xA9], OFF)
                        # Display Smart Attr
                        self.oRF.checkSmartAttr(OFF)

                  if self.IDT_READ_TEST_DRIVE == ON and result == OK:
                     result,data = self.doReadTestDrive()

                     if self.doCEDump == 'YES' :
                        # DT240211 PE
                        # Display Smart Logs
                        self.oRF.checkSmartLogs([0xA1, 0xA8, 0xA9], OFF)
                        # Display Smart Attr
                        self.oRF.checkSmartAttr(OFF)

                  if self.IDT_LOW_DUTY_CYCLE == ON and result == OK:
                     result,data = self.doLowDutyCycle()

                     if self.doCEDump == 'YES' :
                        # DT240211 PE
                        # Display Smart Logs
                        self.oRF.checkSmartLogs([0xA1, 0xA8, 0xA9], OFF)
                        # Display Smart Attr
                        self.oRF.checkSmartAttr(OFF)

                  ###### as requested by TK: no more temp ramp
                  if 0 and self.IDT_RAMP_TEMP == ON and result == OK:
                     if self.driveAttr['TEMP_RAMP'] == 'NO':
                        # DT090709 More preventive measures for aborted write
                        ICmd.FlushCache()
                        #ICmd.IdleImmediate()   # DT290710 To replace with standbyImmed
                        ICmd.StandbyImmed()
                        #time.sleep(3)     # DT290710 To remove by request from DE
                        objMsg.printMsg('FlushCache and StandbyImmed')
                        objMsg.printMsg('>>>> Ramp to 22deg with Wait for NonTempProfile - DriveOff, ReleaseHeater/Fan')
                        DriveOff()
                        if not cellTypeString == 'Neptune2':
                           ReleaseTheHeater()
                        self.oRF.rampTemp(self.AmbTemp, ON, 600, 3, 3)
                        if not cellTypeString == 'Neptune2':
                           ReleaseTheFans()
                  ###### as requested by TK: no more temp ramp

                  if self.IDT_OS_WRITE_TEST == ON and result == OK:
                     result,data = self.doOSWriteDrive()

                     if self.doCEDump == 'YES' :
                        # DT240211 PE
                        # Display Smart Logs
                        self.oRF.checkSmartLogs([0xA1, 0xA8, 0xA9], OFF)
                        # Display Smart Attr
                        self.oRF.checkSmartAttr(OFF)

                  if self.IDT_VERIFY_SMART_IDE == ON and result == OK:
                     result = self.oRF.verifySmart()
                     result = self.oRF.Status
                     if result != OK: self.updateFailureAttr()

                  if self.IDT_GET_SMART_LOGS == ON and result == OK:
                     self.printTestName('GET SMART LOGS', 'OFF')
                     self.oRF.checkSmartLogs([0xA1, 0xA8, 0xA9])
                     result = self.oRF.Status
                     if result != OK: self.updateFailureAttr()
                     if result == OK:
                        self.oRF.checkSmartAttr()
                        result = self.oRF.Status
                        if result != OK: self.updateFailureAttr()



                  if self.IDT_OS_READ_COMPARE == ON and result == OK:
                     result,data = self.doOSReadDrive()

                     if self.doCEDump == 'YES' :
                        # DT240211 PE
                        # Display Smart Logs
                        self.oRF.checkSmartLogs([0xA1, 0xA8, 0xA9], OFF)
                        # Display Smart Attr
                        self.oRF.checkSmartAttr(OFF)

                  if self.IDT_OS_READ_REVERSE == ON and result == OK:
                     result,data = self.doOSReadReverse()

                     if self.doCEDump == 'YES' :
                        # DT240211 PE
                        # Display Smart Logs
                        self.oRF.checkSmartLogs([0xA1, 0xA8, 0xA9], OFF)
                        # Display Smart Attr
                        self.oRF.checkSmartAttr(OFF)

                  if self.IDT_WRITE_PATTERN == ON and result == OK:
                     if ConfigVars[CN].get('IDT Disable Cell', 'OFF') == 'ON':           # Disable Cell during Extensive Writes
                        RequestService('DisableCell')
                     result,data = self.doWritePattern()

                     if self.doCEDump == 'YES' :
                        # DT240211 PE
                        # Display Smart Logs
                        self.oRF.checkSmartLogs([0xA1, 0xA8, 0xA9], OFF)
                        # Display Smart Attr
                        self.oRF.checkSmartAttr(OFF)

                     if ConfigVars[CN].get('IDT Disable Cell', 'OFF') == 'ON':
                        RequestService('EnableCell')

                  if self.IDT_READ_PATTERN_FORWARD == ON and result == OK:
                     result,data = self.doReadPattForward()

                     if self.doCEDump == 'YES' :
                        # DT240211 PE
                        # Display Smart Logs
                        self.oRF.checkSmartLogs([0xA1, 0xA8, 0xA9], OFF)
                        # Display Smart Attr
                        self.oRF.checkSmartAttr(OFF)

                  ###### as requested by TK: no more temp ramp
                  if 0 and self.IDT_RAMP_TEMP == ON and not ConfigVars[CN]['BenchTop'] and result == OK:
                     if self.driveAttr['TEMP_RAMP'] == 'NO':
                        # DT090709 More preventive measures for aborted write
                        ICmd.FlushCache()
                        #ICmd.IdleImmediate()   # DT290710 To replace with standbyImmed
                        ICmd.StandbyImmed()
                        #time.sleep(3)     # DT290710 To remove by request from DE
                        objMsg.printMsg('FlushCache and StandbyImmed')
                        objMsg.printMsg('Ramp to 22deg with Wait for NonTempProfile - DriveOff, ReleaseHeater/Fan')
                        DriveOff()
                        if not cellTypeString == 'Neptune2':
                           ReleaseTheHeater()
                        self.oRF.rampTemp(self.AmbTemp, ON, 600, 3, 3)
                        if not cellTypeString == 'Neptune2':
                           ReleaseTheFans()
                  ###### as requested by TK: no more temp ramp

                  if self.IDT_ODTATI_TEST == ON and result == OK and (not ConfigVars[CN].has_key('IDT_ATI_TEST') or (ConfigVars[CN].has_key('IDT_ATI_TEST') and ConfigVars[CN]['IDT_ATI_TEST'] != UNDEF and ConfigVars[CN]['IDT_ATI_TEST'] == 'ON')):
                     if ConfigVars[CN].get('IDT Disable Cell', 'OFF') == 'ON':           # Disable Cell during Extensive Writes
                        RequestService('DisableCell')
                     result,data = self.doODTATI()

                     if self.doCEDump == 'YES' :
                        # DT240211 PE
                        # Display Smart Logs
                        self.oRF.checkSmartLogs([0xA1, 0xA8, 0xA9], OFF)
                        # Display Smart Attr
                        self.oRF.checkSmartAttr(OFF)

                     if ConfigVars[CN].get('IDT Disable Cell', 'OFF') == 'ON':
                        RequestService('EnableCell')

                  #RT020811: Shift to perform right after ATI
                  if self.IDT_VOLTAGE_HIGH_LOW == ON and result == OK:
                     self.doVoltageHighLow()

                     if self.doCEDump == 'YES' :
                        # DT240211 PE
                        # Display Smart Logs
                        self.oRF.checkSmartLogs([0xA1, 0xA8, 0xA9], OFF)
                        # Display Smart Attr
                        self.oRF.checkSmartAttr(OFF)


                  if self.IDT_RAMP_TEMP == ON and result == OK:
                     if self.driveAttr['TEMP_RAMP'] == 'YES':
                        objMsg.printMsg('Ramp to 22deg NoWait, ReleaseHeater/Fan')
                        if not cellTypeString == 'Neptune2':
                           ReleaseTheHeater()
                        self.oRF.rampTemp(self.AmbTemp, OFF, 600, 3, 3)                             # Ramp Slot to Temperature
                        if not cellTypeString == 'Neptune2':
                           ReleaseTheFans()
                     else:
                        # DT090709 More preventive measures for aborted write
                        ICmd.FlushCache()
                        #ICmd.IdleImmediate()   # DT290710 To replace with standbyImmed
                        ICmd.StandbyImmed()
                        #time.sleep(3)     # DT290710 To remove by request from DE
                        objMsg.printMsg('FlushCache and StandbyImmed')
                        objMsg.printMsg('Ramp to 22deg with Wait - DriveOff, ReleaseHeater/Fan')
                        DriveOff()
                        if not cellTypeString == 'Neptune2':
                           ReleaseTheHeater()
                        self.oRF.rampTemp(self.AmbTemp, ON, 600, 3, 3)
                        if not cellTypeString == 'Neptune2':
                           ReleaseTheFans()

                  #Add another "5x of "SystemFileLoad" just before the "RandomWrite" module.
                  #As per TechKhoon - MQM_UNF21D2_3 (Base:MQM_UNF21D2_2) - 12-Jan-2012
                  for i in range(5):
                     if self.IDT_SYSTEM_FILE_LOAD == ON and result == OK:
                        result = self.doSystemFileLoad()
                        if self.doCEDump == 'YES' :
                           # Display Smart Logs
                           self.oRF.checkSmartLogs([0xA1, 0xA8, 0xA9], OFF)
                           # Display Smart Attr
                           self.oRF.checkSmartAttr(OFF)

                  #Add IDT_PM_ZONETHRUPUT test before RandomWrite test.
                  #As per TechKhoon - MQM_UNF21D2_5 (Base:MQM_UNF21D2_4) - 04-Apr-2012
                  if self.IDT_PM_ZONETHRUPUT == ON and result == OK:
                     if ConfigVars[CN].get('IDT Disable Cell', 'OFF') == 'ON':
                        RequestService('DisableCell')
                     result = self.doPerfMeasureZoneDegrade()

                     if self.doCEDump == 'YES' :
                        # DT240211 PE
                        # Display Smart Logs
                        self.oRF.checkSmartLogs([0xA1, 0xA8, 0xA9], OFF)
                        # Display Smart Attr
                        self.oRF.checkSmartAttr(OFF)

                     if ConfigVars[CN].get('IDT Disable Cell', 'OFF') == 'ON':
                        RequestService('EnableCell')


                  if self.IDT_RANDOM_WRITE_TEST == ON and result == OK:
                     if ConfigVars[CN].get('IDT Disable Cell', 'OFF') == 'ON':           # Disable Cell during Extensive Writes
                        RequestService('DisableCell')
                     result,data = self.doRandomWrite()

                     if self.doCEDump == 'YES' :
                        # DT240211 PE
                        # Display Smart Logs
                        self.oRF.checkSmartLogs([0xA1, 0xA8, 0xA9], ON)
                        # Display Smart Attr
                        self.oRF.checkSmartAttr(ON)

                     if ConfigVars[CN].get('IDT Disable Cell', 'OFF') == 'ON':
                        RequestService('EnableCell')

                  # DT031210 Request by PE
                  ###### as requested by TK: no more temp ramp
                  if 0 and self.IDT_RAMP_TEMP == ON and result == OK:
                     # DT060808 Power off drive before temp ramping
                     # DT080709 Set Ramp Temp to Ambient at later stage
                     # DT090709 More preventive measures for aborted write
                     ICmd.FlushCache()
                     #ICmd.IdleImmediate()   # DT290710 To replace with standbyImmed
                     ICmd.StandbyImmed()
                     #time.sleep(3)     # DT290710 To remove by request from DE
                     objMsg.printMsg('FlushCache and StandbyImmed')
                     objMsg.printMsg('Ramp to 22deg with Wait - DriveOff, ReleaseHeater/Fan')
                     DriveOff()
                     if not cellTypeString == 'Neptune2':
                        ReleaseTheHeater()
                     self.oRF.rampTemp(self.AmbTemp, ON, 600, 3, 3)
                     if not cellTypeString == 'Neptune2':
                        ReleaseTheFans()
                  ###### as requested by TK: no more temp ramp

                  #Remove IdleAPM test after RandomWrite test.
                  #As per TechKhoon - MQM_UNF21D2_5 (Base:MQM_UNF21D2_4) - 04-Apr-2012
      ##            if self.IDT_IDLE_APM_TEST == ON and result == OK:
      ##               # input(Type)
      ##               result = self.doIdleAPMTest()
      ##
      ##               if self.doCEDump == 'YES' :
      ##                  # DT240211 PE
      ##                  # Display Smart Logs
      ##                  self.oRF.checkSmartLogs([0xA1, 0xA8, 0xA9], OFF)
      ##                  # Display Smart Attr
      ##                  self.oRF.checkSmartAttr(OFF)

                  if self.IDT_STM_IDLE_TEST == ON and result == OK:
                     result = self.doSTMIdle()

                     if self.doCEDump == 'YES' :
                        # DT240211 PE
                        # Display Smart Logs
                        self.oRF.checkSmartLogs([0xA1, 0xA8, 0xA9], OFF)
                        # Display Smart Attr
                        self.oRF.checkSmartAttr(OFF)

                  # DT031210 Request by PE
                  ###### as requested by TK: no more temp ramp
                  if 0 and self.IDT_RAMP_TEMP == ON and result == OK:
                     # DT060808 Power off drive before temp ramping
                     # DT080709 Set Ramp Temp to Ambient at later stage
                     # DT090709 More preventive measures for aborted write
                     ICmd.FlushCache()
                     #ICmd.IdleImmediate()   # DT290710 To replace with standbyImmed
                     ICmd.StandbyImmed()
                     #time.sleep(3)     # DT290710 To remove by request from DE
                     objMsg.printMsg('FlushCache and StandbyImmed')
                     objMsg.printMsg('Ramp to 22deg with Wait - DriveOff, ReleaseHeater/Fan')
                     DriveOff()
                     if not cellTypeString == 'Neptune2':
                        ReleaseTheHeater()
                     self.oRF.rampTemp(self.AmbTemp, ON, 600, 3, 3)
                     if not cellTypeString == 'Neptune2':
                        ReleaseTheFans()
                  ###### as requested by TK: no more temp ramp

                  ###### as requested by TK: Insert "DSTTest_IDE" in front of WriteZeroPattern
                  if self.IDT_FULL_DST_IDE == ON and result == OK and (not ConfigVars[CN].has_key('IDT_DVR_TEST') or (ConfigVars[CN].has_key('IDT_DVR_TEST') and ConfigVars[CN]['IDT_DVR_TEST'] != UNDEF and ConfigVars[CN]['IDT_DVR_TEST'] == 'OFF')):
                     result = self.DSTTest_IDE('Long')

                     if self.doCEDump == 'YES' :
                        # DT240211 PE
                        # Display Smart Logs
                        self.oRF.checkSmartLogs([0xA1, 0xA8, 0xA9], OFF)
                        # Display Smart Attr
                        self.oRF.checkSmartAttr(OFF)
                  ###### as requested by TK: Insert "DSTTest_IDE" in front of WriteZeroPattern


                  ###### as requested by TK: Insert "WriteZeroPattern" in front of the DST_Long
                  #run doBerByZone
                  self.doBERByZone()
                  if self.IDT_WRITE_DRIVE_ZERO == ON and result == OK:
                     if ConfigVars[CN].get('IDT Disable Cell', 'OFF') == 'ON':           # Disable Cell during Extensive Writes
                        RequestService('DisableCell')
                     #Change IDT Write Zero Patt from Full Drive to 300,000 LBA.
                     #As per TechKhoon request- MQM_UNF21D2_4 (Base:MQM_UNF21D2_3) - 18-Jan-2012
                     result,data = self.doWriteZeroPatt(NumLBA=300000)

                     if self.doCEDump == 'YES' :
                        # DT240211 PE
                        # Display Smart Logs
                        self.oRF.checkSmartLogs([0xA1, 0xA8, 0xA9], OFF)
                        # Display Smart Attr
                        self.oRF.checkSmartAttr(OFF)

                     if ConfigVars[CN].get('IDT Disable Cell', 'OFF') == 'ON':
                        RequestService('EnableCell')
                  ###### as requested by TK: Insert "WriteZeroPattern" in front of the DST_Long

                  #RT010811: if DVR testing applies, LongDST is performed after ReadZeroCompare
                  #if self.IDT_FULL_DST_IDE == ON and result == OK and (not ConfigVars[CN].has_key('IDT_DVR_TEST') or (ConfigVars[CN].has_key('IDT_DVR_TEST') and ConfigVars[CN]['IDT_DVR_TEST'] != UNDEF and ConfigVars[CN]['IDT_DVR_TEST'] == 'OFF')):
                  #   result = self.DSTTest_IDE('Long')
                  #   if self.doCEDump == 'YES' :
                  #      # DT240211 PE
                  #      # Display Smart Logs
                  #      self.oRF.checkSmartLogs([0xA1, 0xA8, 0xA9], OFF)
                  #      # Display Smart Attr
                  #      self.oRF.checkSmartAttr(OFF)

                  #Replace Second Long DST module to SequentialReadDMAExt from 0 - 400,000 LBA.
                  #As per TechKhoon request- MQM_UNF21D2_4 (Base:MQM_UNF21D2_3) - 18-Jan-2012
                  #if result == OK:
                  #   result,data = self.doReadPattForward(TestType='IDT', Pattern=0x00, Location='OD', NumLBA=400000, SectCnt=256, Compare=0)
                  #   if self.doCEDump == 'YES' :
                        # DT240211 PE
                        # Display Smart Logs
                  #      self.oRF.checkSmartLogs([0xA1, 0xA8, 0xA9], OFF)
                        # Display Smart Attr
                  #      self.oRF.checkSmartAttr(OFF)

                  #Replace SequentialReadDMAExt 400K before SDOD to Zero Check 400K OD and ID
                  #As per WUXI request- MQM_UNF21D2_6 (Base:MQM_UNF21D2_5) - 27-Apr-2012
                  if self.IDT_READ_ZERO_COMPARE == ON and result == OK:
                     result = self.doReadZeroCompareGuard(LBABand = 400000)         # ReadZeroCompare only to 1st and last 400K LBA
                     if self.doCEDump == 'YES' :
                        self.oRF.checkSmartLogs([0xA1, 0xA8, 0xA9], OFF)
                        self.oRF.checkSmartAttr(OFF)

                  self.doServoRecall()
                  if self.IDT_SERIAL_SDOD_TEST == ON and result == OK:
                     result = self.doSerialSDODCheck()

                     if self.doCEDump == 'YES' :
                        # DT240211 PE
                        # Display Smart Logs
                        self.oRF.checkSmartLogs([0xA1, 0xA8, 0xA9], OFF)
                        # Display Smart Attr
                        self.oRF.checkSmartAttr(OFF)

                  if self.IDT_GET_SMART_LOGS == ON and result == OK:
                     self.printTestName('GET SMART LOGS', 'OFF')
                     self.oRF.checkSmartLogs([0xA1, 0xA8, 0xA9])
                     result = self.oRF.Status
                     if result != OK: self.updateFailureAttr()
                     if result == OK:
                        self.oRF.checkSmartAttr()
                        result = self.oRF.Status
                        if result != OK: self.updateFailureAttr()


                  if result == OK:

                     result = self.oRF.postGIOScreen()
                     if result != OK: self.updateFailureAttr()

            except:
               objMsg.printMsg('idtTestEnd Exception=%s' % (traceback.format_exc()))
               if self.doVerifyMQMfail(loop) == OK:
                  continue

               raise

            # end non-benchtop test - Loke
            objMsg.printMsg('idtTestEnd loop=%s idtTestLoops=%s result=%s' % (loop, self.idtTestLoops, result))

            if result == OK:
               self.idtTestEnd('PASS')

               if loop >= self.idtTestLoops:
                  break
            else:
               if self.doVerifyMQMfail(loop) == OK:
                  continue

               self.idtTestEnd('FAIL')
               self.GIOCleanup()
               ScrCmds.raiseException(self.failCode)

      except gioTestException, M:
         self.printTestName('GIO TEST FAILED',setTestStep='OFF')

         if M.data.has_key('LBA') == 0: M.data['LBA'] = '0'
         if M.data.has_key('STS') == 0: M.data['STS'] = '00'
         if M.data.has_key('ERR') == 0: M.data['ERR'] = '00'
         if self.isCPC == 1:
            if M.data.has_key('LLRET'):   self.failLLRET = M.data['RESULT']
         else:
            if M.data.has_key('LLRET'):   self.failLLRET = M.data['LLRET']

         self.currentStep = self.testName
         self.failStep = self.testName
         self.failLBA = M.data['LBA']
         self.failCode = self.oFC.getFailCode(self.testName)    #self.failCodeDict[self.currentStep]
         self.failStatus = ('STS%s-ERR%s' % ( int(M.data['STS']), int(M.data['ERR']) ))

         # DT211210
         #self.GetSerialPortData()
         self.getSerialPortData()
         # DT140910 Log fail data to Smart Log 8F (Shelved)
         #self.oRF.logODTVFailData(self.failCode, self.failLBA, self.failLLRET, M.data['ERR'])

         self.idtTestEnd('FAIL')

         self.GIOCleanup()
         ScrCmds.raiseException(self.failCode, M.data)
   def doServoRecall(self):
      TestType='IDT'
      dataDic = {}
      result = OK
      timeout = 60
      self.testName = ('%s Servo Recall' % TestType)       # Test Name for file formatting
      self.printTestName(self.testName)

      self.oRF.powerCycle('TCGUnlock')
      self.oRF.disableAPM('GetSerialPortData')
      sptCmds.enableDiags()
      try:
         objMsg.printMsg('*****************************************************************************')
         sptCmds.gotoLevel('T')
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
         objMsg.printMsg("Warning:No matter what is RAM DATA value there,all pass.")

      self.oRF.powerCycle('TCGUnlock')



   def doBERByZone(self,FLAG=1):
      TestType='IDT'
      self.testName = ('%s BER By Zone' % TestType)       # Test Name for file formatting
      self.printTestName(self.testName)
      oSerial = serialScreen.sptDiagCmds()
      sptCmds.enableDiags()

      # ** Display Zone Table and collect last cyl of the zone **
      numCyls,zones = oSerial.getZoneInfo(False,0) #Kinta getZoneInfo method only has max 3 argus
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
      for hd in zones.keys():
          num1=zones[hd]
          sptCmds.gotoLevel('2')
          sptCmds.sendDiagCmd('A2', timeout = 500, altPattern = None, printResult = True)
          for zn in num1.keys():
              if(zn==0):continue
              num2=num1[zn]-1
              num3=num2-100
              try:
                  sptCmds.gotoLevel('2')
                  sptCmds.sendDiagCmd("P0000,0000", timeout = 500, altPattern = None, printResult = True)
                  sptCmds.sendDiagCmd("S%X,%d"%(num3,hd) ,timeout = 1000,printResult = True)
                  sptCmds.sendDiagCmd("L,30" ,timeout = 1000,printResult = True)
                  sptCmds.sendDiagCmd("Q", timeout = 500, printResult = True, stopOnError = 0)
              except:
                  continue
          numCyls[hd]-=100
          sptCmds.sendDiagCmd("P0000,0000", timeout = 500, altPattern = None, printResult = True)
          sptCmds.sendDiagCmd("S%X,%d"%(numCyls[hd],hd) ,timeout = 1000,printResult = True)
          sptCmds.sendDiagCmd("L,30" ,timeout = 1000,printResult = True)
          sptCmds.sendDiagCmd("Q", timeout = 500, printResult = True, stopOnError = 0)

      #**Display Zone BER summary
      results_ZoneBER= sptCmds.execOnlineCmd(SHIFT_4, timeout = 20, waitLoops = 100)
      objMsg.printMsg('Display Zone BER summary: '+ str(results_ZoneBER))
      oSerial=serialScreen.sptDiagCmds()
      information=oSerial.getZoneBERData_SMMY()
      MQM_BEGIN_OTF_H0=0
      MQM_BEGIN_RAW_H0=0
      MQM_BEGIN_OTF_H1=0
      MQM_BEGIN_RAW_H1=0
      MQM_END_OTF_H0=0
      MQM_END_RAW_H0=0
      MQM_END_OTF_H1=0
      MQM_END_RAW_H1=0
      global GLOBAL_MQM_BEGIN_OTF_H0
      global GLOBAL_MQM_BEGIN_OTF_H1
      global GLOBAL_MQM_BEGIN_RAW_H0
      global GLOBAL_MQM_BEGIN_RAW_H1
      if FLAG==0:
          GLOBAL_MQM_BEGIN_OTF_H0=information[1]['Avg'].get('0', 0)
          GLOBAL_MQM_BEGIN_OTF_H1=information[1]['Avg'].get('1', 0)
          GLOBAL_MQM_BEGIN_RAW_H0=information[2]['Avg'].get('0', 0)
          GLOBAL_MQM_BEGIN_RAW_H1=information[2]['Avg'].get('1', 0)
          objMsg.printMsg('MQM_BEGIN_OTF_H0= '+str(GLOBAL_MQM_BEGIN_OTF_H0))
          objMsg.printMsg('MQM_BEGIN_OTF_H1= '+str(GLOBAL_MQM_BEGIN_OTF_H1))
          objMsg.printMsg('MQM_BEGIN_RAW_H0= '+str(GLOBAL_MQM_BEGIN_RAW_H0))
          objMsg.printMsg('MQM_BEGIN_RAW_H1= '+str(GLOBAL_MQM_BEGIN_RAW_H1))
      else:
          MQM_END_OTF_H0=information[1]['Avg'].get('0', 0)
          MQM_END_OTF_H1=information[1]['Avg'].get('1', 0)
          MQM_END_RAW_H0=information[2]['Avg'].get('0', 0)
          MQM_END_RAW_H1=information[2]['Avg'].get('1', 0)
          objMsg.printMsg('MQM_END_OTF_H0= '+str(MQM_END_OTF_H0))
          objMsg.printMsg('MQM_END_OTF_H1= '+str(MQM_END_OTF_H1))
          objMsg.printMsg('MQM_END_RAW_H0= '+str(MQM_END_RAW_H0))
          objMsg.printMsg('MQM_END_RAW_H1= '+str(MQM_END_RAW_H1))
          MQM_DELTA_OTF_H0=float(MQM_END_OTF_H0)-float(GLOBAL_MQM_BEGIN_OTF_H0)
          MQM_DELTA_RAW_H0=float(MQM_END_RAW_H0)-float(GLOBAL_MQM_BEGIN_RAW_H0)
          MQM_DELTA_OTF_H1=float(MQM_END_OTF_H1)-float(GLOBAL_MQM_BEGIN_OTF_H1)
          MQM_DELTA_RAW_H1=float(MQM_END_RAW_H1)-float(GLOBAL_MQM_BEGIN_RAW_H1)
          objMsg.printMsg('MQM_DELTA_OTF_H0= '+str(MQM_DELTA_OTF_H0))
          objMsg.printMsg('MQM_DELTA_RAW_H0= '+str(MQM_DELTA_RAW_H0))
          objMsg.printMsg('MQM_DELTA_OTF_H1= '+str(MQM_DELTA_OTF_H1))
          objMsg.printMsg('MQM_DELTA_RAW_H1= '+str(MQM_DELTA_RAW_H1))

          if (abs(float(MQM_END_RAW_H0)) > 0 and abs(float(MQM_END_RAW_H0))<2.15) or (abs(float(MQM_END_RAW_H1)) > 0 and abs(float(MQM_END_RAW_H1))<2.15): #check RAW value
             failure='IDT BER By Zone'
             self.failCode = self.oFC.getFailCode(failure)
             ScrCmds.raiseException(self.failCode,'Failed RAW value')


      #**Display Active Error log
      sptCmds.gotoLevel('2')
      results_OTF_RAW=sptCmds.sendDiagCmd("E", timeout = 1000, printResult = True)

      self.oRF.powerCycle('TCGUnlock')



   def doVerifyMQMfail(self, loop):

      result = -1

      if self.MQMV == 0 and loop == 1:
         self.MQMV += 1

         numEntries = -1
         try:
            self.oRF.powerCycle('TCGUnlock')
            self.oRF.disableAPM('GetSerialPortData')
            sptCmds.enableDiags()

            sptCmds.gotoLevel('T')
            data = sptCmds.sendDiagCmd("V4",timeout = 300, printResult = True, loopSleepTime=0)

            pat = 'Entries:\s*(?P<NUMBER_OF_TOTALALTS>[a-fA-F\d]+),'
            match = re.search(pat, data)

            numEntries = int(match.groupdict()['NUMBER_OF_TOTALALTS'],16)
            objMsg.printMsg('rlist count=%s' % numEntries)
         except:
            objMsg.printMsg('doVerifyMQMfail Exception=%s' % (traceback.format_exc()))

         if testSwitch.virtualRun or ConfigVars[CN]['BenchTop']:
            objMsg.printMsg('resul11t= '+str(result))
            numEntries = 0

         if numEntries == 0:
            objMsg.printMsg('Running DST Long...')

            if ConfigVars[CN]['BenchTop']:
               result = self.DSTTest_IDE('Short')
            else:
               result = self.DSTTest_IDE('Long')

            objMsg.printMsg('DST Long result=%s' % result)

      self.driveAttr['PROC_CTRL22'] = self.MQMV

      return result


   def doSystemFileLoad(self):
      TestType='IDT'
      SysMinLBA=0
      SysMaxLBA=3906
      DiagMinLBA=64298
      DiagMaxLBA=203716
      SectCnt=16
      RandCount=5000

      P_Msg = ON      # Performance Message
      F_Msg = ON      # Failure Message
      B_Msg = ON      # Buffer Message
      data = {}
      result = OK
      self.testCmdTime = 0
      self.testName = ('%s Sys File Load' % TestType)       # Test Name for file formatting
      self.printTestName(self.testName)

      #RT010611: T510 issues DITS commands, unlock serial port on FDE drives
      #objPwrCtrl.powerCycle()
      self.oRF.powerCycle('TCGUnlock')

      # Setup Parameters
      Delay = 7
      MinSectCount = 1
      SectPerBlock = 1
      Pattern1 = 0x22222222
      Pattern2 = 0x33333333
      self.sectorCount = SectCnt
      self.numBlocks = (DiagMaxLBA-DiagMinLBA)/self.sectorCount
      self.timeout = self.calculateTimeout(self.numBlocks,self.sectorCount)

      objMsg.printMsg('%s SYS Start LBA=%d/0x%X End LBA=%d/0x%X SectCnt=%d Pattern1=%x RandCount=%d' % \
                     (self.testName,SysMinLBA,SysMinLBA,SysMaxLBA,SysMaxLBA,SectCnt,Pattern1,RandCount))
      objMsg.printMsg('%s DIAG Start LBA=%d/0x%X End LBA=%d/0x%X SectCnt=%d Pattern2=%x SectPerBlock=%d Delay=%d Sec' % \
                     (self.testName,DiagMinLBA,DiagMinLBA,DiagMaxLBA,DiagMaxLBA,SectCnt,Pattern2,SectPerBlock,Delay))

      self.pattern = Pattern1

      SystemTrackWriteSim = {
         'test_num'   : 654,
         'prm_name'   : "SystemTrackWriteSim",
         'timeout' : 252000,
         'LBA' : lbaTuple(SysMinLBA),
         'MULTI_SECTORS_BLOCK' : SectPerBlock,
         'SECTOR_COUNT' : SectCnt,
         'DATA_PATTERN0' : wordTuple(Pattern1),
      }

      stat = ICmd.St(SystemTrackWriteSim)
      data = ICmd.translateStReturnToCPC(stat)
      result = data['LLRET']

      self.testCmdTime += float(data.get('CT','0'))/1000

      if result != OK:
         objMsg.printMsg("%s SystemTrackWriteSim Failed - Data: %s" % (self.testName,data))
      else:
         objMsg.printMsg("%s SystemTrackWriteSim Passed - Data: %s" % (self.testName,data))
         self.pattern = Pattern2
         #RT 01102010: script level implementation of CPC equivalent of LoadTestFileSim

         #RT120112: change due to CPC intrinsic removal
         if (self.oRF.CellType.find('CPC') < 0) or ((self.oRF.CellType.find('CPC') >= 0) and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION): #SI or intrinsic CPC
            LoadTestFileSim_SequentialWRDMAExt = {
                  'test_num'   : 510,
                  'prm_name'   : "LoadTestFileSim_SequentialWRDMAExt",
                  'spc_id'     : 1,
                  'timeout' : 18000,
                  'WRITE_READ_MODE' : (0x00), #Write/Read Mode
                  'STARTING_LBA' : lbaTuple(DiagMinLBA),
                  'MAXIMUM_LBA' : lbaTuple(DiagMaxLBA),
                  'BLKS_PER_XFR' : SectCnt,
                  'DATA_PATTERN0' : wordTuple(Pattern2),
                  'PATTERN_MODE'  : (0x80),
                  'ENABLE_HW_PATTERN_GEN': 1,
                  'COMPARE_OPTION': 1
            }
         else: #non-intrinsic CPC
               #RT150312: replacement to T551 as recommended by Kumanan since T510 with compare is not working
               LoadTestFileSim_SequentialWRDMAExt = {
                  'test_num'   : 551,
                  'prm_name'   : "LoadTestFileSim_SequentialWRDMAExt",
                  'spc_id'     : 1,
                  'timeout' : 18000,
                  'CTRL_WORD1' : (0x000), #Write/Read Mode
                  'STARTING_LBA' : lbaTuple(DiagMinLBA),
                  'TOTAL_BLKS_TO_XFR64' : lbaTuple(DiagMaxLBA - DiagMinLBA),
                  'MAX_NBR_ERRORS' : 0,
                  'DATA_PATTERN0' : wordTuple(Pattern2),
                  'PATTERN_MODE':0x80,
               }
         stat = ICmd.St(LoadTestFileSim_SequentialWRDMAExt)
         data = ICmd.translateStReturnToCPC(stat)
         result = data['LLRET']

         if result == OK:
            ICmd.FlushCache()
            ICmd.IdleImmediate()
            time.sleep(Delay)

            LBArange = DiagMaxLBA - DiagMinLBA + 1
            LastScnt = LBArange % SectCnt

            if LastScnt == 0:
               LastScnt = SectCnt

            LastLBA = DiagMaxLBA -LastScnt + 1
            LBALow = LastLBA & 0x00000000000000FF
            LBAMid = (LastLBA & 0x000000000000FF00) >> 8
            LBAHigh = (LastLBA & 0x0000000000FF0000) >> 12

            LoadTestFileSim_ReadDMAExt = {
               'test_num'   : 538,
               'prm_name'   : "LoadTestFileSim_ReadDMAExt",
               'FEATURES' : 0,
               'LBA_LOW' : LBALow,
               'COMMAND' : 0x0025,
               'SECTOR_COUNT': LastScnt,
               'LBA_HIGH' : LBAHigh,
               'DEVICE' : 0x0040,
               'PARAMETER_0' : 0x2000,
               'LBA_MID' : LBAMid
            }
            stat = ICmd.St(LoadTestFileSim_ReadDMAExt)
            data = ICmd.translateStReturnToCPC(stat)
            result = data['LLRET']

            if result != OK:
               raise gioTestException(data)

            LoadTestFileSim_SequentialReadDMAExt = {
               'test_num'   : 510,
               'prm_name'   : "SequentialReadDMAExt",
               'spc_id'     : 1,
               'timeout' : 252000,
               'WRITE_READ_MODE' : (0x01), #Read Mode
               'STARTING_LBA' : lbaTuple(SysMinLBA),
               'MAXIMUM_LBA' : lbaTuple(SysMaxLBA),
               'CTRL_WORD2' : 0x0080,
               'BLKS_PER_XFR' : SectCnt,
            }
            stat = ICmd.St(LoadTestFileSim_SequentialReadDMAExt)
            data = ICmd.translateStReturnToCPC(stat)
            result = data['LLRET']

            if result != OK:
               raise gioTestException(data)

            data = ICmd.RandomReadDMAExt(SysMinLBA, SysMaxLBA, SectCnt, SectCnt, RandCount) #Kinta ICmd.RandomReadDMAExt already includes translateStReturnToCPC()
            result = data['LLRET']

            if result != OK:
               raise gioTestException(data)

            LoadTestFileSim_SequentialReadDMAExt["STARTING_LBA"] = lbaTuple(DiagMinLBA)
            LoadTestFileSim_SequentialReadDMAExt["MAXIMUM_LBA"] = lbaTuple(DiagMaxLBA)
            LoadTestFileSim_SequentialReadDMAExt["BLKS_PER_XFR"] = MinSectCount
            #RT120112: change due to CPC intrinsic removal
            if (self.oRF.CellType.find('CPC') < 0) or ((self.oRF.CellType.find('CPC') >= 0) and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION): #SI or intrinsic CPC
               LoadTestFileSim_SequentialReadDMAExt["ENABLE_HW_PATTERN_GEN"] = 0

            stat = ICmd.St(LoadTestFileSim_SequentialReadDMAExt)
            data = ICmd.translateStReturnToCPC(stat)
            result = data['LLRET']


         self.testCmdTime += float(data.get('CT','0'))/1000
         if result != OK:
            objMsg.printMsg("%s LoadTestFileSim Failed - Data: %s" % (self.testName,data))
         else:
            objMsg.printMsg("%s LoadTestFileSim Passed - Data: %s" % (self.testName,data))

      #self.blocksXfrd = 12*Count
      #self.numCmds = self.blocksXfrd / self.sectorCount
      #self.displayPerformance(self.testName,numCmds,blocksXfrd,blockSize,self.testCmdTime)
      #self.displayCmdTimes(self.testName,'CPC',self.testCmdTime,self.sectorCount)

      if result != OK:
         objMsg.printMsg('%s Failed Result=%s Data=%s' % (self.testName, result, data))

         raise gioTestException(data)
      else:
         objMsg.printMsg('%s Test Passed' % self.testName)

      return result


   def doWritePattern(self):
      objMsg.printMsg("doWritePattern BEGIN")
      self.testName = 'IDT Write Pattern'
      self.dut.testName = 'IDT Write Pattern'
      self.printTestName(self.testName)

      #RT010611: T510 issues DITS commands, unlock serial port on FDE drives
      #objPwrCtrl.powerCycle()
      if testSwitch.IO_MQM_SIC_TESTTIME_OPTIMIZATION:
         self.oRF.powerCycle('TCGUnlock', driveOnly=1)
      else:
         self.oRF.powerCycle('TCGUnlock')

      Pattern = 0x00
      objMsg.printMsg('Start LBA: %d' % 0)
      objMsg.printMsg('End LBA: %d' % 10000000)
      objMsg.printMsg('pattern: 0x%X' % Pattern)
      ICmd.ClearBinBuff(WBF)
      ICmd.ClearBinBuff(RBF)
      stat = ()


      #RT120112: change due to CPC intrinsic removal
      if (self.oRF.CellType.find('CPC') < 0) or ((self.oRF.CellType.find('CPC') >= 0) and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION): #SI or intrinsic CPC
         SequentialWriteDMAExt = {
               'test_num'   : 510,
               'prm_name'   : "SequentialWriteDMAExt",
               'spc_id'     : 1,
               'timeout' : 18000,
               'WRITE_READ_MODE' : (0x02), #Write Mode
               'STARTING_LBA' : (0,0,0,0),
               'MAXIMUM_LBA' : lbaTuple(10000000),
               'BLKS_PER_XFR' : 256,
               'DATA_PATTERN0' : wordTuple(Pattern),
               'PATTERN_MODE'  : (0x80),
               'ENABLE_HW_PATTERN_GEN': 1,
         }
      else: #non-intrinsic CPC
         SequentialWriteDMAExt = {
               'test_num'   : 551,
               'prm_name'   : "SequentialWriteDMAExt",
               'spc_id'     : 1,
               'timeout' : 18000,
               'WRITE_READ_MODE' : (2), #PN: Write Mode
               'STARTING_LBA' : (0,0,0,0),
               'TOTAL_BLKS_TO_XFR64' : lbaTuple(10000000),
               'BLKS_PER_XFR' : 256,
               'DATA_PATTERN0' : wordTuple(Pattern),
               'PATTERN_MODE'  : (0x80),
         }
      try:
         #stat = ICmd.SequentialWriteDMAExt(0, 10000000,DATA_PATTERN0=0x06060606)
         stat = ICmd.St(SequentialWriteDMAExt)
      except Exception, e:
         stat = e[0]
         objMsg.printMsg("doWritePattern Exception data : %s"%e)
      data = ICmd.translateStReturnToCPC(stat)
      result = data['LLRET']
      result = OK
      objMsg.printMsg("doWritePattern data : %s"%data)

      if result != OK:
         raise gioTestException(data)
      #if result == OK:
         #ICmd.FlushCache()
         #time.sleep(3)
         #ICmd.StandbyImmed()
      #else:
         #self.GetSerialPortData()
         #raise gioTestException(data)

      objMsg.printMsg("doWritePattern END")
      return result,data

   def doReadPattForward(self, TestType='IDT', Pattern=0x00, Location='OD', NumLBA=10000000, SectCnt=256, Compare=1):
      self.testName = 'IDT Read Pattern'
      self.dut.testName = 'IDT Read Pattern'
      self.printTestName(self.testName)

      #RT010611: T510 issues DITS commands, unlock serial port on FDE drives
      #objPwrCtrl.powerCycle()
      if testSwitch.IO_MQM_SIC_TESTTIME_OPTIMIZATION:
         self.oRF.powerCycle('TCGUnlock', driveOnly=1)
      else:
         self.oRF.powerCycle('TCGUnlock')

      objMsg.printMsg('Start LBA: %d' % 0)
      objMsg.printMsg('End LBA: %d' % NumLBA)
      objMsg.printMsg('pattern: 0x%X' % Pattern)
      ICmd.ClearBinBuff(WBF)
      ICmd.ClearBinBuff(RBF)
      stat = ()

      #RT120112: change due to CPC intrinsic removal
      if (self.oRF.CellType.find('CPC') < 0) or ((self.oRF.CellType.find('CPC') >= 0) and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION): #SI or non-intrinsic CPC
         SequentialReadDMAExt = {
               'test_num'   : 510,
               'prm_name'   : "SequentialReadDMAExt",
               'spc_id'     : 1,
               'timeout' : 18000,
               'WRITE_READ_MODE' : (0x01), #Read Mode
               'STARTING_LBA' : (0,0,0,0),
               'MAXIMUM_LBA' : lbaTuple(NumLBA),
               'CTRL_WORD2' : 0x0080,
               #'ENABLE_HW_PATTERN_GEN': 1, 
               'BLKS_PER_XFR' : 256,
               'DATA_PATTERN0' : wordTuple(Pattern),
               'PATTERN_MODE'  : (0x80),
         }
      else:#non-intrinsic CPC
         #RT150312: replacement to T551 as recommended by Kumanan since T510 with compare is not working
         SequentialReadDMAExt = {
            'test_num'   : 551,
            'prm_name'   : "SequentialReadDMAExt",
            'spc_id'     : 1,
            'timeout' : 18000,
            'CTRL_WORD1' : (0x0010), #Read Mode
            'STARTING_LBA' : (0,0,0,0),
            'TOTAL_BLKS_TO_XFR64' : lbaTuple(NumLBA),
            'BLKS_PER_XFR' : 256,
            'DATA_PATTERN0' :wordTuple(Pattern),
            'MAX_NBR_ERRORS' : 0,
            'PATTERN_MODE'  : (0x80),
         }
      try:
         #stat = ICmd.SequentialReadDMAExt(0, 10000000,DATA_PATTERN0=0xCC000000,COMPARE_FLAG=1)
         if Compare and (self.oRF.CellType.find('CPC') < 0) or ((self.oRF.CellType.find('CPC') >= 0) and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION): #SI or intrinsic CPC
            SequentialReadDMAExt.update({'ENABLE_HW_PATTERN_GEN': 1})
         stat = ICmd.St(SequentialReadDMAExt)
      except Exception, e:
         stat = e[0]
         objMsg.printMsg("doReadPattForward Exception data : %s"%e)
      data = ICmd.translateStReturnToCPC(stat)
      result = data['LLRET']
      objMsg.printMsg("doReadPattForward data : %s"%data)

      if result != OK:
         raise gioTestException(data)
      #if result == OK:
         #ICmd.FlushCache()
         #time.sleep(3)
         #ICmd.StandbyImmed()
      #else:
         #self.GetSerialPortData()
         #raise gioTestException(data)


      objMsg.printMsg("doReadPattForward END")
      return result,data

   def doReadTestMobile(self):
      self.testName = "IDT Read Mobile"
      self.dut.testName = "IDT Read Mobile"
      self.printTestName(self.testName)
      #objPwrCtrl.powerCycle()
      if testSwitch.IO_MQM_SIC_TESTTIME_OPTIMIZATION:
         self.oRF.powerCycle(useHardReset = 1)
      else:
         self.oRF.powerCycle()
      #tempPrm = prm_650_ReadTestSim2.copy()
      #Change for Kinta branch
      READTESTMOBLE = 0x00
      maxLBA  = 0x31BC4
      maxLBA0 = maxLBA & 0xffff
      maxLBA1 = (maxLBA >> 16) & 0xffff
      maxLBA2 = (maxLBA >> 32) & 0xffff
      maxLBA3 = (maxLBA >> 24)

      minLBA  = 0xFB2A
      minLBA0 = minLBA & 0xffff
      minLBA1 = (minLBA >> 16) & 0xffff
      minLBA2 = (minLBA >> 32) & 0xffff
      minLBA3 = (minLBA >> 24)

      tempPrm = {                                        
         'test_num':650,
         'prm_name':'ReadTestSim2',
         'STARTING_LBA'        : (minLBA3,minLBA2,minLBA1,minLBA0),       #  starting LBA
         'MAXIMUM_LBA'         : (maxLBA3,maxLBA2,maxLBA1,maxLBA0),   #  maximum LBA
         'LOOP_COUNT'          : (24),                                 #  test loop
         'READ_LOOPS'          : (0,0x0004),                          #  read/read/flush loop
         'RANDOM_ACCESS_COUNT' : (5),                                 #  random read count
         'DELAY_TIME'          : (100),                               #  standby delay
         'RANDOM_SEED'         : (1),                                 #  random number seed
         'TEST_FUNCTION'       : (READTESTMOBLE)                      # ReadTestSim2()
      }

      if (self.oRF.CellType.find('CPC') < 0) or ((self.oRF.CellType.find('CPC') >= 0) and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION): #SI or intrinsic CPC
         tempPrm['DATA_PATTERN0'] = wordTuple(0x00000000)
      para = "tempPrm = %s"%tempPrm
      objMsg.printMsg(para)
      stat = ()
      try:
         stat = ICmd.St(tempPrm)
      except Exception, e:
         stat = e[0]
         objMsg.printMsg("doReadTestMobile Exception data : %s"%e)

      data = ICmd.translateStReturnToCPC(stat)
      result = data['LLRET']
      objMsg.printMsg("ReadTestSim2e data : %s"%data)
      if result != OK:
         raise gioTestException(data)
      #if result == OK:
         #ICmd.FlushCache()
         #time.sleep(3)
         #ICmd.StandbyImmed()
      #else:
         #self.GetSerialPortData()
         #raise gioTestException(data)


      objMsg.printMsg("doReadTestMobile END")
      return result,data

   def doReadTestDrive(self):
      self.testName = "IDT Read Drive"
      self.dut.testName = 'IDT Read Drive'
      self.printTestName(self.testName)
      #objPwrCtrl.powerCycle()
      if testSwitch.IO_MQM_SIC_TESTTIME_OPTIMIZATION:
         self.oRF.powerCycle(useHardReset = 1)
      else:
         self.oRF.powerCycle()

      #Change for Kinta branch
      READTESTDRIVE = 0x01 

      maxLBA  = 0x31BC4
      maxLBA0 = maxLBA & 0xffff
      maxLBA1 = (maxLBA >> 16) & 0xffff
      maxLBA2 = (maxLBA >> 32) & 0xffff
      maxLBA3 = (maxLBA >> 24)

      minLBA  = 0xFB2A
      minLBA0 = minLBA & 0xffff
      minLBA1 = (minLBA >> 16) & 0xffff
      minLBA2 = (minLBA >> 32) & 0xffff
      minLBA3 = (minLBA >> 24)
       
      prm_650_ReadTestSim = {                                         # CPC Parmaeters ----------------------------
         'test_num':650,
         'prm_name':'ReadTestSim',
         'STARTING_LBA'        : (minLBA3,minLBA2,minLBA1,minLBA0),       #  starting LBA
         'MAXIMUM_LBA'         : (maxLBA3,maxLBA2,maxLBA1,maxLBA0),   #  maximum LBA
         'LOOP_COUNT'          : (3000),                                 #  test loop
         'RANDOM_ACCESS_COUNT' : (30),                                 #  random read count
         'RANDOM_SEED'         : (1),                                 #  random number seed
         'TEST_FUNCTION'       : (READTESTDRIVE),                      # ReadTestSim()
         'timeout': 120000,
      }
      try:
         stat = ICmd.St(prm_650_ReadTestSim)
      except Exception, e:
         stat = e[0]
         objMsg.printMsg("doReadTestDrive Exception data : %s"%e)

      data = ICmd.translateStReturnToCPC(stat)
      result = data['LLRET']
      objMsg.printMsg("doReadTestDrive data : %s"%data)
      if result != OK:
         raise gioTestException(data)
      #if result == OK:
         #ICmd.FlushCache()
         #time.sleep(3)
         #ICmd.StandbyImmed()
      #else:
         #self.GetSerialPortData()
         #raise gioTestException(data)


      objMsg.printMsg("doReadTestDrive END")
      return result,data

   def doRandomWrite(self):
      TestType = 'IDT'
      TestName = ('Random Write')
      self.testName = ('%s %s' % (TestType,TestName))
      self.dut.testName = TestName
      self.printTestName(self.testName)

      #RT010611: T510 issues DITS commands, unlock serial port on FDE drives
      #objPwrCtrl.powerCycle()
      if testSwitch.IO_MQM_SIC_TESTTIME_OPTIMIZATION:
         self.oRF.powerCycle('TCGUnlock', driveOnly=1)
      else:
         self.oRF.powerCycle('TCGUnlock')

      flushCacheFlag = 1
      loopCnt=250000
      minSectorCnt=256
      maxSectorCnt=256
      #RT050911: don't use ACCESS_MODE to specify mode
      #RT120112: change due to CPC intrinsic removal
      if (self.oRF.CellType.find('CPC') < 0) or ((self.oRF.CellType.find('CPC') >= 0) and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION): #SI or intrinsic CPC
         RandomWriteDMAExt = {
               'test_num'   : 510,
               'prm_name'   : "RandomWriteDMAExt",
               'spc_id'     : 1,
               'timeout' : 18000,
               #'WRITE_READ_MODE' : (0x02),  #Write Mode
               #'ACCESS_MODE' : (0x01),      #Random
               'STARTING_LBA' : lbaTuple(0),
               'MAXIMUM_LBA' : lbaTuple(self.maxLBA - 256),
               'TOTAL_BLKS_TO_XFR64': lbaTuple(64000000),
               'BLKS_PER_XFR' : 256,
               'CTRL_WORD1':0x0021,
               'CTRL_WORD2':0x0001,
               #'DATA_PATTERN0': (0,0)
               #'ENABLE_HW_PATTERN_GEN': 1,
         }
      else: #non-intrinsic CPC
         RandomWriteDMAExt = {
            'test_num'   : 510,
            'prm_name'   : "RandomWriteDMAExt",
            'spc_id'     : 1,
            'timeout' : 18000,
            #'WRITE_READ_MODE' : (0x02),  #Write Mode
            #'ACCESS_MODE' : (0x01),      #Random
            'STARTING_LBA' : lbaTuple(0),
            'MAXIMUM_LBA' : lbaTuple(self.maxLBA - 256),
            'TOTAL_BLKS_TO_XFR64': lbaTuple(64000000),
            'BLKS_PER_XFR' : 256,
            'CTRL_WORD1':0x0021,
            'CTRL_WORD2':0x0001,
         }

      stat = ()
      try:
         stat = ICmd.St(RandomWriteDMAExt)
      except Exception, e:
         stat = e[0]
         objMsg.printMsg("RandomWrite Exception data : %s"%e)

      data = ICmd.translateStReturnToCPC(stat)
      result = data['LLRET']
      objMsg.printMsg("RandomWrite data : %s"%data)
      if result != OK:
         raise gioTestException(data)
      #if result == OK:
         #ICmd.FlushCache()
         #time.sleep(3)
         #ICmd.StandbyImmed()
      #else:
         #self.GetSerialPortData()
         #raise gioTestException(data)


      objMsg.printMsg('RandomWrite END')
      return result,data

   def doWriteTestMobile(self):
      self.testName = 'IDT Write Mobile'
      self.dut.testName = 'IDT Write Mobile'
      self.printTestName(self.testName)

      #RT220911: FDE unlock prior to T643 TFunc0x00 call
      self.oRF.powerCycle('TCGUnlock')

      MultiSPB = self.oRF.IDAttr['MultLogSect']
      objMsg.printMsg('Start LBA: %d' % 0)
      objMsg.printMsg('Mid LBA: %d' % 1000000)
      objMsg.printMsg('End LBA: %d' % 4194303)
      objMsg.printMsg('loopCnt: %d' % 5000)
      objMsg.printMsg('Min Sector Count: %d' % 256)
      objMsg.printMsg('Max Sector Count: %d' % 256)
      stat = ()
      WriteTestSim2 = {
         'test_num':643,
         'prm_name':'doWriteTestMobile',
         'timeout': 120000,
         "TEST_FUNCTION" : (0x0000,),
         "COMPARE_OPTION" : (0x01,),
         "MULTI_SECTORS_BLOCK" : (MultiSPB,),
         "DATA_PATTERN0" : wordTuple(0x00000000),
         "LOOP_COUNT" : 5000,
         "FIXED_SECTOR_COUNT" : 63,
         "SINGLE_LBA" : wordTuple(256),
         "MAX_LBA" : wordTuple(4194303),
         "MID_LBA" : wordTuple(1000000),
         "MIN_LBA" : wordTuple(64),
       }
      try:
         stat = ICmd.St(WriteTestSim2)
      except Exception, e:
         stat = e[0]
         objMsg.printMsg("doWriteTestMobile Exception data : %s"%e)

      data = ICmd.translateStReturnToCPC(stat)
      result = data['LLRET']
      objMsg.printMsg("doWriteTestMobile data : %s"%data)
      if result != OK:
         raise gioTestException(data)
      #if result == OK:
         #ICmd.FlushCache()
         #time.sleep(3)
         #ICmd.StandbyImmed()
      #else:
         #self.GetSerialPortData()
         #raise gioTestException(data)


      objMsg.printMsg("doWriteTestMobile end")
      return result,data

   def doReadZeroVerify(self):
      objMsg.printMsg("doReadZeroVerify BEGIN")
      self.testName = "IDT Read Zero Verify"
      self.dut.testName = "IDT Read Zero Verify"
      self.printTestName(self.testName)

      #RT010611: T510 issues DITS commands, unlock serial port on FDE drives
      #objPwrCtrl.powerCycle()
      self.oRF.powerCycle('TCGUnlock')

      objMsg.printMsg('Start LBA: %d' % 0)
      objMsg.printMsg('End LBA: %d' % self.maxLBA)
      objMsg.printMsg('pattern: 0x%X' % 0x00)
      ICmd.ClearBinBuff(WBF)
      ICmd.ClearBinBuff(RBF)
      patt = 0x00
      SequentialReadDMAExt = {
            'test_num'   : 510,
            'prm_name'   : "SequentialReadDMAExt",
            'spc_id'     : 1,
            'timeout' : 252000,
            'WRITE_READ_MODE' : (0x01), #Read Mode
            'STARTING_LBA' : (0,0,0,0),
            'MAXIMUM_LBA' : lbaTuple(self.maxLBA),
            'CTRL_WORD2' : 0x0080,
            'ENABLE_HW_PATTERN_GEN': 1,
            'BLKS_PER_XFR' : 256,
            'DATA_PATTERN0' : wordTuple(patt),
            'PATTERN_MODE'  : (0x80),
      }
      #ReliFunction.startRWStats()

      stat = ()
      try:
         #stat = ICmd.SequentialReadDMAExt(0, self.maxLBA,DATA_PATTERN0=0x00,COMPARE_FLAG=1)
         stat = ICmd.St(SequentialReadDMAExt)
      except Exception, e:
         stat = e[0]
         objMsg.printMsg("doReadZeroVerify Exception data : %s"%e)

      data = ICmd.translateStReturnToCPC(stat)
      result = data['LLRET']
      objMsg.printMsg("doReadZeroVerify data : %s"%data)
      if result != OK:
         raise gioTestException(data)
      #if result == OK:
         #ICmd.FlushCache()
         #time.sleep(3)
         #ICmd.StandbyImmed()
      #else:
         #self.GetSerialPortData()
         #raise gioTestException(data)


      objMsg.printMsg("doReadZeroVerify END")
      return result,data

   def doWriteZeroPatt(self, NumLBA='MaxLBA'):
      objMsg.printMsg("doWriteZeroPatt BEGIN")
      self.testName = 'IDT Write Zero Patt'
      self.dut.testName = 'IDT Write Zero Patt'
      self.printTestName(self.testName)

      #RT010611: T510 issues DITS commands, unlock serial port on FDE drives
      #objPwrCtrl.powerCycle()
      if testSwitch.IO_MQM_SIC_TESTTIME_OPTIMIZATION:
         self.oRF.powerCycle('TCGUnlock', driveOnly=1)
      else:
         self.oRF.powerCycle('TCGUnlock')

      if NumLBA == ('MaxLBA'):
         EndLBA = self.oRF.IDAttr['MaxLBA']
      else: EndLBA = NumLBA

      patt = 0x00
      objMsg.printMsg('Start LBA: %d' % 0)
      objMsg.printMsg('End LBA: %d' % EndLBA)
      objMsg.printMsg('pattern: 0x%X' % patt)
      ICmd.ClearBinBuff(WBF|RBF)
      #ReliFunction.startRWStats()

      #RT120112: change due to CPC intrinsic removal
      if (self.oRF.CellType.find('CPC') < 0) or ((self.oRF.CellType.find('CPC') >= 0) and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION): #SI or intrinsic CPC
         SequentialWriteDMAExt = {
               'test_num'   : 510,
               'prm_name'   : "SequentialWriteDMAExt",
               'spc_id'     : 1,
               'timeout' : 18000,
               'WRITE_READ_MODE' : (0x02), #Write Mode
               'STARTING_LBA' : (0,0,0,0),
               'MAXIMUM_LBA' : lbaTuple(EndLBA),
               'BLKS_PER_XFR' : 256,
               'DATA_PATTERN0' : wordTuple(patt),
               'PATTERN_MODE'  : (0x80),
               'ENABLE_HW_PATTERN_GEN': 1,
         }
      else: #no-intrinsic CPC
         SequentialWriteDMAExt = {
               'test_num'   : 510,
               'prm_name'   : "SequentialWriteDMAExt",
               'spc_id'     : 1,
               'timeout' : 18000,
               'WRITE_READ_MODE' : (0x02), #Write Mode
               'STARTING_LBA' : (0,0,0,0),
               #'MAXIMUM_LBA' : lbaTuple(self.maxLBA),
               'MAXIMUM_LBA' : lbaTuple(EndLBA), 
               'BLKS_PER_XFR' : 256,
               'DATA_PATTERN0' : wordTuple(patt),
               'PATTERN_MODE'  : (0x80),
         }

      stat = ()
      try:
         #stat = ICmd.SequentialWriteDMAExt(0, self.maxLBA,DATA_PATTERN0=0x00)
         stat = ICmd.St(SequentialWriteDMAExt)
      except Exception, e:
         stat = e[0]
         objMsg.printMsg("doWriteZeroPatt Exception data : %s"%e)

      data = ICmd.translateStReturnToCPC(stat)
      result = data['LLRET']
      objMsg.printMsg("doWriteZeroPatt data : %s"%data)
      if result != OK:
         raise gioTestException(data)
      #if result == OK:
         #ICmd.FlushCache()
         #time.sleep(3)
         #ICmd.StandbyImmed()
      #else:
         #self.GetSerialPortData()
         #raise gioTestException(data)


      objMsg.printMsg("doWriteZeroPatt END")
      return result,data


   def doOSWriteDrive(self):
      self.testName = 'IDT OS Write Test'
      self.dut.testName = 'IDT OS Write Test'
      self.printTestName(self.testName)

      #RT010611: T510 issues DITS commands, unlock serial port on FDE drives
      #objPwrCtrl.powerCycle()
      self.oRF.powerCycle('TCGUnlock')

      ICmd.ClearBinBuff(WBF)
      ICmd.ClearBinBuff(RBF)
      ICmd.SetFeatures(0x03, 0x45)
      StartLBA = 0
      EndLBA = StartLBA + ((5*1000000000) / 512)
      stat = ()

      try:
         data = ICmd.SequentialWriteDMAExt(StartLBA, EndLBA,16,16,DATA_PATTERN0=0x00000000) #Change for Kinta branch
      except Exception, e:
         data = e[0]
         objMsg.printMsg("doOSWriteDrive Exception data : %s"%e)

      objMsg.printMsg('data: %s'%data)
      result = data['LLRET']
      objMsg.printMsg("doOSWriteDrive data : %s"%data)
      if result != OK:
         raise gioTestException(data)
      #if result == OK:
         #ICmd.FlushCache()
         #time.sleep(3)
         #ICmd.StandbyImmed()
      #else:
         #self.GetSerialPortData()
         #raise gioTestException(data)


      objMsg.printMsg("doOSWriteDrive END")
      return result,data

   def doOSReadDrive(self):
      self.testName = 'IDT OS Read Test'
      self.dut.testName = 'IDT OS Read Test'
      self.printTestName(self.testName)

      #RT010611: T510 issues DITS commands, unlock serial port on FDE drives
      #objPwrCtrl.powerCycle()
      if testSwitch.IO_MQM_SIC_TESTTIME_OPTIMIZATION:
         self.oRF.powerCycle('TCGUnlock', driveOnly =1)
      else:
         self.oRF.powerCycle('TCGUnlock')

      ICmd.SetFeatures(0x03, 0x45)
      stat = ()

      try:
         data = ICmd.SequentialReadDMAExt(0, 10485760,64,64) #Change for Kinta branch
      except Exception, e:
         data = e[0] 
         objMsg.printMsg("doOSReadDrive Exception data : %s"%e)

      result = data['LLRET']
      objMsg.printMsg("doOSReadDrive data : %s"%data)
      if result != OK:
         raise gioTestException(data)
      #if result == OK:
         #ICmd.FlushCache()
         #time.sleep(3)
         #ICmd.StandbyImmed()
      #else:
         #self.GetSerialPortData()
         #raise gioTestException(data)


      objMsg.printMsg("doOSReadDrive END")
      return result,data

   def doOSReadReverse(self):
      self.testName = 'IDT OS Read Rev'
      self.dut.testName = 'IDT OS Read Rev'
      self.printTestName(self.testName)

      #RT010611: T510 issues DITS commands, unlock serial port on FDE drives
      #objPwrCtrl.powerCycle()
      self.oRF.powerCycle('TCGUnlock')

      smartReturnStatusData = ICmd.SmartReturnStatus()
      objMsg.printMsg("SmartReturnStatus data: %s" % smartReturnStatusData, objMsg.CMessLvl.IMPORTANT)
      objMsg.printMsg("SmartReturnStatus value: %x" % int(smartReturnStatusData['LBA']), objMsg.CMessLvl.IMPORTANT)
      if int(smartReturnStatusData['LBA']) != 0xc24f00:
         ScrCmds.raiseException(13455, 'Failed Smart Threshold Value')
      ICmd.SetFeatures(0x03, 0x45)
      maxLBA  = 0xA00000
      maxLBA0 = maxLBA & 0xffff
      maxLBA1 = (maxLBA >> 16) & 0xffff
      maxLBA2 = (maxLBA >> 32) & 0xffff
      maxLBA3 = (maxLBA >> 48) & 0xffff
      #140000000
      reverseRead = {
            'test_num'   : 510,
            'prm_name'   : "ReverseReadDMAExt",
            'spc_id'     : 1,
            'timeout' : 252000,
            'WRITE_READ_MODE' : (0x01), #Read Mode
            'STARTING_LBA' : (0,0,0,0),
            'MAXIMUM_LBA' : (maxLBA3,maxLBA2,maxLBA1,maxLBA0),   #  maximum LBA
            'BLKS_PER_XFR' : 64,
            'DATA_PATTERN0' : (0,0),
            'PATTERN_MODE'  : (0x80),
            #RT050911: don't use ACCESS_MODE to specify mode
            #'ACCESS_MODE' : (0x200),      #reverse
            'CTRL_WORD1': 0x200,      #reverse
	    #'DATA_PATTERN0' : (0,0xAAAA),
      }
      stat = ()

      try:
         stat = ICmd.St(reverseRead)
      except Exception, e:
         stat = e[0]
         objMsg.printMsg("doOSReadReverse Exception data : %s"%e)

      data = ICmd.translateStReturnToCPC(stat)
      result = data['LLRET']
      objMsg.printMsg("doOSReadReverse data : %s"%data)
      if result != OK:
         raise gioTestException(data)
      #if result == OK:
         #ICmd.FlushCache()
         #time.sleep(3)
         #ICmd.StandbyImmed()
      #else:
         #self.GetSerialPortData()
         #raise gioTestException(data)


      objMsg.printMsg("doOSReadReverse END")
      return result,data

   def doWriteReadPerform(self):
      objMsg.printMsg("doWriteReadPerform BEGIN")
      self.testName = 'IDT Wrt Rd Perform'
      self.dut.testName = 'IDT Wrt Rd Perform'
      self.printTestName(self.testName)
      #objPwrCtrl.powerCycle()
       #RT130911: SI/N2 powercycle without prepower sequence
      self.oRF.powerCycle('TCGUnlock') #Required for non-intrinsic code TCG drive
      wwf = {
      'test_num' : 643,
      'prm_name' : "WeakWriteTest",
      'TEST_FUNCTION'         : 0x20,
      'OPTIONS'               : 0,
      'FIXED_SECTOR_COUNT'    : 0x0100,
      'DATA_PATTERN0'         : wordTuple(0x00000000),
      }
      stat = ()
      try:
         stat = ICmd.St(wwf)
      except Exception, e:
         stat = e[0]
         objMsg.printMsg("doWriteReadPerform Exception data : %s"%e)

      data = ICmd.translateStReturnToCPC(stat)
      result = data['LLRET']
      objMsg.printMsg("doWriteReadPerform data : %s"%data)
      if result != OK:
         raise gioTestException(data)
      #if result == OK:
         #ICmd.FlushCache()
         #time.sleep(3)
         #ICmd.StandbyImmed()
      #else:
         #self.GetSerialPortData()
         #raise gioTestException(data)


      objMsg.printMsg("doWriteReadPerform END")
      return result,data

   def doImageFileCopy(self):
      self.testName = 'IDT Image FileCopy'
      self.dut.testName = 'IDT Image FileCopy'
      self.printTestName(self.testName)
      if testSwitch.IO_MQM_SIC_TESTTIME_OPTIMIZATION:
         self.oRF.powerCycle(useHardReset = 1)
      else:
         self.oRF.powerCycle()
      #ICmd.SetFeatures(0x03, 0x45)
      #<P0>     MIN_SEQ_LBA       8 maximum LBA, fixed sector count
      #<P1>     MAX_SEQ_LBA       8 minimum LBA, fixed sector count
      #<P2>     BLKS_PER_XFR      2  fixed sector count
      #<P3>     STARTING_LBA      8 starting LBA, random sector count
      #<P5>     DATA_PATTERN0     4 data_pattern, fixed sector count
      #<P6>     DATA_PATTERN1     4 data pattern, random sector count
      #ImageFileRead('IDT',10000,14999,256,1000000,1080000,256) # input(Type,FATMin,FATMax,FATSectCnt,DataMin,DataMax,DataSectCnt)
      #ImageFileCopy(TestType, FAT_Min=10000, FAT_Max=14999, FAT_SectCnt=256, Data_Min=1000000, Data_Max=1080000, Data_SectCnt=256)
      #CPCFileCopySim1(FAT_Min,FAT_Max,FAT_SectCnt,Data_Min,UDMA_Speed,Pattern1,Pattern2)
      data = {}
      result = OK
      stat = ()
      FileTestSim1  = {
         'test_num'   : 653,
         'prm_name'   : "FileTestSim1",
         'spc_id'     : 1,
         'MIN_SEQ_LBA' : lbaTuple(10000),
         'MAX_SEQ_LBA' : lbaTuple(14999),
         'BLKS_PER_XFR' : 256,
         'STARTING_LBA' :lbaTuple(1000000),
         'DATA_PATTERN0'       : (0,0),
         'DATA_PATTERN1'       : (0,0),
      }
      try:
         stat = ICmd.St(FileTestSim1)
      except Exception, e:
         stat = e[0]
         objMsg.printMsg("FileTestSim1 Exception data : %s"%e)
      data = ICmd.translateStReturnToCPC(stat)
      result = data['LLRET']
      objMsg.printMsg("FileTestSim1 data : %s"%data)

      if result != OK:
         raise gioTestException(data)


      objMsg.printMsg("Image File Copy END")
      return result,data

   def doImageFileRead(self):
      self.testName = 'IDT Image FileRead'
      self.dut.testName = 'IDT Image FileRead'
      self.printTestName(self.testName)

      #RT010611: T510 issues DITS commands, unlock serial port on FDE drives
      #objPwrCtrl.powerCycle()
      if testSwitch.IO_MQM_SIC_TESTTIME_OPTIMIZATION:
         self.oRF.powerCycle('TCGUnlock', driveOnly=1)
      else:
         self.oRF.powerCycle('TCGUnlock')

      #ImageFileRead('IDT',10000,14999,256,1000000,1080000,256) # input(Type,FATMin,FATMax,FATSectCnt,DataMin,DataMax,DataSectCnt)
      data = {}
      result = OK
      stat = ()

      startLBA1 = 10000
      endLBA1 =   14999

      startLBA2 = 1000000
      endLBA2   = 1080000

      sequentialRead = {
         'test_num'   : 510,
         'prm_name'   : "SequentialReadDMAExt",
         'spc_id'     : 1,
         'timeout' : 252000,
         'WRITE_READ_MODE' : (0x01), #Read Mode
         'STARTING_LBA' : (0,0,0,0),
         'BLKS_PER_XFR' : 256,
         'DATA_PATTERN0' : (0,0),
         'PATTERN_MODE'  : (0x80),
      }
      reverseRead = {
         'test_num'   : 510,
         'prm_name'   : "ReverseReadDMAExt",
         'spc_id'     : 1,
         'timeout' : 252000,
         'WRITE_READ_MODE' : (0x01), #Read Mode
         'STARTING_LBA' : (0,0,0,0),
         'BLKS_PER_XFR' : 64,
         'DATA_PATTERN0' : (0,0),
         'PATTERN_MODE'  : (0x80),
         #RT050911: don't use ACCESS_MODE to specify mode
         #'ACCESS_MODE' : (0x200),      #reverse
         'CTRL_WORD1': 0x200,      #reverse
      }
      sequentialRead['STARTING_LBA'] = lbaTuple(startLBA1)
      sequentialRead['MAXIMUM_LBA'] = lbaTuple(endLBA1)

      try:
         stat = ICmd.St(sequentialRead)
      except Exception, e:
         stat = e[0]
         objMsg.printMsg("doImageFileRead test, SequentialReadDMAExt Exception data : %s"%e)

      data = ICmd.translateStReturnToCPC(stat)
      result = data['LLRET']
      objMsg.printMsg("doImageFileRead test, SequentialReadDMAExt data : %s"%data)

      reverseRead['STARTING_LBA'] = lbaTuple(startLBA1)
      reverseRead['MAXIMUM_LBA'] = lbaTuple(endLBA1)

      if result == OK:
         try:
            stat = ICmd.St(reverseRead)
         except Exception, e:
            stat = e[0]
            objMsg.printMsg("doImageFileRead test, ReverseReadDMAExt Exception data : %s"%e)

      data = ICmd.translateStReturnToCPC(stat)
      result = data['LLRET']
      objMsg.printMsg("doImageFileRead test, ReverseReadDMAExt data : %s"%data)

      sequentialRead['STARTING_LBA'] = lbaTuple(startLBA2)
      sequentialRead['MAXIMUM_LBA'] = lbaTuple(endLBA2)

      if result == OK:
         try:
            stat = ICmd.St(sequentialRead)
         except Exception, e:
            stat = e[0]
            objMsg.printMsg("doImageFileRead test, SequentialReadDMAExt Exception data : %s"%e)

      data = ICmd.translateStReturnToCPC(stat)
      result = data['LLRET']
      objMsg.printMsg("doImageFileRead test, SequentialReadDMAExt data : %s"%data)

      reverseRead['STARTING_LBA'] = lbaTuple(startLBA2)
      reverseRead['MAXIMUM_LBA'] = lbaTuple(endLBA2)

      if result == OK:
         try:
            stat = ICmd.St(reverseRead)
         except Exception, e:
            stat = e[0]
            objMsg.printMsg("doImageFileRead test, ReverseReadDMAExt Exception data : %s"%e)

      data = ICmd.translateStReturnToCPC(stat)
      result = data['LLRET']
      objMsg.printMsg("doImageFileRead test, ReverseReadDMAExt data : %s"%data)

      if result != OK:
         raise gioTestException(data)

      objMsg.printMsg("Image File Read END")
      return result,data


   #RT30122010: Adapted new ODT algo from Gen2.2A
   def doODTATI(self):
      self.testName = 'IDT ODT ATI Test'
      self.dut.testName = 'IDT ODT ATI Test'
      self.printTestName(self.testName)

      #RT010611: T510 issues DITS commands, unlock serial port on FDE drives
      #objPwrCtrl.powerCycle()
      self.oRF.powerCycle('TCGUnlock')

      numLogSect = self.oRF.IDAttr['NumLogSect']
      objMsg.printMsg("numLogSect = %s"%numLogSect)

      OffsetLBA0 = self.oRF.IDAttr['OffSetLBA0']
      objMsg.printMsg("OffsetLBA0 = %s"%OffsetLBA0)

      data = {}
      result = OK
      DoRetry = ON

      SectCount = 256
      StampFlag = 0
      CompareFlag = 0
      CmdLoop = 2500 # loop 2x

      TestLoop = 50
      StartLBA = 0
      EndLBA = 400
      InterLoop = 2
      MaxLBA = self.maxLBA

      StepLBA = MaxLBA/400
      BlockSize = 512

      ICmd.ClearBinBuff(WBF)
      ICmd.ClearBinBuff(RBF)
      ICmd.SetFeatures(0x03, 0x45)
      ICmd.SetFeatures(0x82)

      objMsg.printMsg('%s Write on %d locations %d times' % (self.testName,TestLoop,CmdLoop))
      stat = ()

      # DT241110 Mod ATI
      for loop in range (0, TestLoop/2, 1):
         for cnt in range(InterLoop):
            if result == OK:
               StartLBA = loop * StepLBA
               objMsg.printMsg('%d write on 400 LBA starting %d' % (CmdLoop, StartLBA))

               # DT170709 Apply offset calculation
               if self.oRF.IDAttr['NumLogSect'] > 1:
                  # Adjust for number of physical sector per logical sector
                  StartLBA = StartLBA - (StartLBA % self.oRF.IDAttr['NumLogSect'])
                  if self.oRF.IDAttr['OffSetLBA0'] > 0:
                     if StartLBA == 0:    # Avoid negative LBA range, proceed to next block
                        StartLBA = StartLBA + self.oRF.IDAttr['NumLogSect']
                     # Adjust for alignment of Log Block in Phy Block
                     StartLBA = StartLBA - self.oRF.IDAttr['OffSetLBA0']

               EndLBA = StartLBA + 400

            if result == OK:
               objMsg.printMsg('%d write location(%d) adjusted from start=%d to end=%d, with offset=%d' % (CmdLoop, loop+1, StartLBA, EndLBA, self.oRF.IDAttr['OffSetLBA0']))

               totalBlocksXfr = CmdLoop * (EndLBA - StartLBA)
               #RT120112: change due to CPC intrinsic removal
               if (self.oRF.CellType.find('CPC') < 0) or ((self.oRF.CellType.find('CPC') >= 0) and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION): #SI or intrinsic CPC
                  SequentialWriteDMAExt = {
                     'test_num'   : 510,
                     'prm_name'   : "SequentialWriteDMAExt",
                     'spc_id'     : 1,
                     'timeout' : 18000,
                     'WRITE_READ_MODE' : (0x02), #Write Mode
                     'STARTING_LBA' : lbaTuple(StartLBA),
                     'MAXIMUM_LBA' : lbaTuple(EndLBA),
                     'BLKS_PER_XFR' : 256,
                     'TOTAL_BLKS_TO_XFR64' : lbaTuple(totalBlocksXfr),
                     'DATA_PATTERN0' : wordTuple(0x00000000),
                     'PATTERN_MODE'  : (0x80),
                     'ENABLE_HW_PATTERN_GEN': 1,
                     'stSuppressResults': ST_SUPPRESS__ALL
                  }
               else: #non-intrinsic CPC
                  SequentialWriteDMAExt = {
                     'test_num'   : 510,
                     'prm_name'   : "SequentialWriteDMAExt",
                     'spc_id'     : 1,
                     'timeout' : 18000,
                     'WRITE_READ_MODE' : (0x02), #Write Mode
                     'STARTING_LBA' : lbaTuple(StartLBA),
                     'MAXIMUM_LBA' : lbaTuple(EndLBA),
                     'BLKS_PER_XFR' : 256,
                     'TOTAL_BLKS_TO_XFR64' : lbaTuple(totalBlocksXfr),
                     'DATA_PATTERN0' : wordTuple(0x00000000),
                     'PATTERN_MODE'  : (0x80),
                     'stSuppressResults': ST_SUPPRESS__ALL
                  }
               try:
                  stat = ICmd.St(SequentialWriteDMAExt)
               except Exception, e:
                  stat = e[0]
                  objMsg.printMsg("ATI Write Exception data : %s"%e)

               data = ICmd.translateStReturnToCPC(stat)
               result = data['LLRET']
               if result != OK:
                  objMsg.printMsg('SequentialCmdLoop failed at loop %d, result=%s' % (TestLoop,data))
                  break

            if result == OK:
               StartLBA = (loop+TestLoop/2) * StepLBA
               objMsg.printMsg('%d write on 400 LBA starting %d' % (CmdLoop, StartLBA))

               # DT170709 Apply offset calculation
               if self.oRF.IDAttr['NumLogSect'] > 1:
                  # Adjust for number of physical sector per logical sector
                  StartLBA = StartLBA - (StartLBA % self.oRF.IDAttr['NumLogSect'])
                  if self.oRF.IDAttr['OffSetLBA0'] > 0:
                     if StartLBA == 0:    # Avoid negative LBA range, proceed to next block
                        StartLBA = StartLBA + self.oRF.IDAttr['NumLogSect']
                     # Adjust for alignment of Log Block in Phy Block
                     StartLBA = StartLBA - self.oRF.IDAttr['OffSetLBA0']

               EndLBA = StartLBA + 400

            if result == OK:
               objMsg.printMsg('%d write location(%d) adjusted from start=%d to end=%d, with offset=%d' % (CmdLoop, loop+1, StartLBA, EndLBA, self.oRF.IDAttr['OffSetLBA0']))

               totalBlocksXfr = CmdLoop * (EndLBA - StartLBA)
               #RT120112: change due to CPC intrinsic removal
               if (self.oRF.CellType.find('CPC') < 0) or ((self.oRF.CellType.find('CPC') >= 0) and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION): #SI or intrinsic CPC
                  SequentialWriteDMAExt = {
                     'test_num'   : 510,
                     'prm_name'   : "SequentialWriteDMAExt",
                     'spc_id'     : 1,
                     'timeout' : 18000,
                     'WRITE_READ_MODE' : (0x02), #Write Mode
                     'STARTING_LBA' : lbaTuple(StartLBA),
                     'MAXIMUM_LBA' : lbaTuple(EndLBA),
                     'BLKS_PER_XFR' : 256,
                     'TOTAL_BLKS_TO_XFR64' : lbaTuple(totalBlocksXfr),
                     'DATA_PATTERN0' : wordTuple(0x00000000),
                     'PATTERN_MODE'  : (0x80),
                     'ENABLE_HW_PATTERN_GEN': 1,
                     'stSuppressResults': ST_SUPPRESS__ALL
                  }
               else: #non-intrinsic CPC
                  SequentialWriteDMAExt = {
                     'test_num'   : 510,
                     'prm_name'   : "SequentialWriteDMAExt",
                     'spc_id'     : 1,
                     'timeout' : 18000,
                     'WRITE_READ_MODE' : (0x02), #Write Mode
                     'STARTING_LBA' : lbaTuple(StartLBA),
                     'MAXIMUM_LBA' : lbaTuple(EndLBA),
                     'BLKS_PER_XFR' : 256,
                     'TOTAL_BLKS_TO_XFR64' : lbaTuple(totalBlocksXfr),
                     'DATA_PATTERN0' : wordTuple(0x00000000),
                     'PATTERN_MODE'  : (0x80),
                     'stSuppressResults': ST_SUPPRESS__ALL
                  }
               try:
                  stat = ICmd.St(SequentialWriteDMAExt)
               except Exception, e:
                  stat = e[0]
                  objMsg.printMsg("ATI Write Exception data : %s"%e)

               data = ICmd.translateStReturnToCPC(stat)
               result = data['LLRET']
               if result != OK:
                  objMsg.printMsg('SequentialCmdLoop failed at loop %d, result=%s' % (TestLoop,data))
                  break

         # end for

      if result == OK:
         ICmd.SetFeatures(0x02)
         Pattern = 0x00
         StartLBA = 0
         EndLBA = MaxLBA/8
         CompareFlag = 1
         objMsg.printMsg('%s Start LBA=%d End LBA=%d Sect Count=%d Pattern=0x%2X' % \
                 (self.testName, StartLBA, EndLBA, SectCount, Pattern))
         ICmd.FlushCache()
         ICmd.ClearBinBuff(WBF)
         ICmd.ClearBinBuff(RBF)
         objMsg.printMsg('%s Sequential Read on first eighth of the disk' % (self.testName))
         try:
            stat = ICmd.SequentialReadDMAExt(StartLBA, EndLBA)
         except Exception, e:
            stat = e[0]
            objMsg.printMsg("Sequential Read Exception data : %s"%e)
         data = ICmd.translateStReturnToCPC(stat)
         result = data['LLRET']

      if result == OK:
         SequentialWriteDMAExt = {
            'test_num'   : 510,
            'prm_name'   : "SequentialWriteDMAExt",
            'spc_id'     : 1,
            'timeout' : 252000,
            'WRITE_READ_MODE' : (0x02), #Write Mode
            'STARTING_LBA' : lbaTuple(StartLBA),
            'MAXIMUM_LBA' : lbaTuple(EndLBA),
            'BLKS_PER_XFR' : 256,
            'DATA_PATTERN0' : wordTuple(Pattern),
            'PATTERN_MODE'  : (0x80),
         }
         objMsg.printMsg('%s Sequential Write on first eighth of the disk' % (self.testName))
         try:
            stat = ICmd.St(SequentialWriteDMAExt)
         except Exception, e:
            stat = e[0]
            objMsg.printMsg("Sequential Write Exception data : %s"%e)
         data = ICmd.translateStReturnToCPC(stat)
         result = data['LLRET']

      if result == OK:
         patt = 0x00
         #RT120112: change due to CPC intrinsic removal
         if (self.oRF.CellType.find('CPC') < 0) or ((self.oRF.CellType.find('CPC') >= 0) and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION): #SI or intrinsic CPC
            SequentialReadDMAExt = {
               'test_num'   : 510,
               'prm_name'   : "SequentialReadDMAExt",
               'spc_id'     : 1,
               'timeout' : 18000,
               'WRITE_READ_MODE' : (0x01), #Read Mode
               'STARTING_LBA' : lbaTuple(StartLBA),
               'MAXIMUM_LBA' : lbaTuple(EndLBA),
               'CTRL_WORD2' : 0x0080,
               'ENABLE_HW_PATTERN_GEN': 1,
               'BLKS_PER_XFR' : 256,
               'DATA_PATTERN0' : wordTuple(patt),
               'PATTERN_MODE'  : (0x80),
            }
         else: #non-intrinsic CPC
            #RT150312: replacement to T551 as recommended by Kumanan since T510 with compare is not working
            SequentialReadDMAExt = {
               'test_num'   : 551,
               'prm_name'   : "SequentialReadDMAExt",
               'spc_id'     : 1,
               'timeout' : 18000,
               'CTRL_WORD1' : (0x010), #Read Mode
               'STARTING_LBA' : lbaTuple(StartLBA),
               'TOTAL_BLKS_TO_XFR64' : lbaTuple(EndLBA - StartLBA),
               'DATA_PATTERN0' : wordTuple(patt),
               'MAX_NBR_ERRORS' : 0,
            }

         objMsg.printMsg('%s Sequential Read on first eighth of the disk with compare' % (self.testName))

         try:
            stat = ICmd.St(SequentialReadDMAExt)
         except Exception, e:
            stat = e[0]
            objMsg.printMsg("Sequential Read Exception data : %s"%e)

         data = ICmd.translateStReturnToCPC(stat)
         result = data['LLRET']

      if result != OK:
         raise gioTestException(data)
      #if result == OK:
         #ICmd.FlushCache()
         #time.sleep(3)
         #ICmd.StandbyImmed()
      #else:
         #self.GetSerialPortData()
         #raise gioTestException(data)


      objMsg.printMsg("ATI TEST END")

      return result,data

   def doODTRamTest(self):
      objMsg.printMsg("RAMTest BEGIN")
      self.testName = 'IDT Ram Miscompare'
      self.dut.testName = 'IDT Ram Miscompare'
      self.printTestName(self.testName)

      #RT010611: T510 issues DITS commands, unlock serial port on FDE drives
      #objPwrCtrl.powerCycle()
      self.oRF.powerCycle('TCGUnlock')

      ICmd.SetFeatures(0x03, 0x45)

      DRamFiles=[
          "fs_aaaa.pat",
          "fs_ff00.pat",
          "fs_aa55.pat",
          "fs_aa00.pat",
          "fs_55aa.pat",
          "fs_00ff.pat",
          "fs_00aa.pat",
       ]
      data = {}
      result = OK
      stat = ()

      #-------------------------------------------------------------------------------------------------
      patterndata = 0
      loopBreak = False
      for patternfile in DRamFiles:
         if result != OK or loopBreak:
            break
         #RT120112: change due to CPC intrinsic removal
         if (self.oRF.CellType.find('CPC') < 0) or ((self.oRF.CellType.find('CPC') >= 0) and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION): #SI or intrinsic CPC

            filename = os.path.join(UserDownloadsPath, self.ConfigName, patternfile)
            patternfile = open(filename,'rb')
            try:
               patterndata = patternfile.read()
               objMsg.printMsg("Read Pattern File= %s" % filename)
            finally:
               patternfile.close()
               objMsg.printMsg("Close File")

            ICmd.ClearBinBuff(BWR)
            ICmd.FillBufferRAMTest(WBF, 0, patterndata)
         else: #non-intrinsic CPC
            filename = os.path.join(UserDownloadsPath, self.ConfigName, patternfile)
            #patternfile = open(filename,'rb')
            #try:
            #   patterndata = patternfile.read()
            #   objMsg.printMsg("Read Pattern File= %s" % filename)
            #   objMsg.printMsg("Pattern Data= %s" % patterndata)
            #finally:
            #   patternfile.close()
            #   objMsg.printMsg("Close File")

            for i in range(0, 8):
               tempPrm = {
                     'test_num'   : 508,
                     'prm_name'   : "Write File Pattern to Write Buffer",
                     'spc_id'     : 1,
                     'timeout' : 18000,
                     'CTRL_WORD1' : (0x000A,),
                     'BYTE_OFFSET' : wordTuple(i*0x4000),
                     'BUFFER_LENGTH' : wordTuple(0x20000),
                     'dlfile' : ('current', filename),
                     'stSuppressResults' : ST_SUPPRESS__ALL
               }
               try:
                  stat = ICmd.St(tempPrm)
               except Exception, e:
                  stat = e[0]
                  objMsg.printMsg("write file pattern to buffer Exception data : %s"%e)

            tempPrm = {
                  'test_num'   : 508,
                  'spc_id'     : 1,
                  'timeout' : 18000,
            }
            tempPrm['CTRL_WORD1'] = (0x0004,)
            tempPrm['prm_name'] = 'Dump Write Buffer'
            tempPrm['BUFFER_LENGTH'] = wordTuple(0x200)
            try:
               stat = ICmd.St(tempPrm)
            except Exception, e:
               stat = e[0]
               objMsg.printMsg("dump write buffer Exception data : %s"%e)

            tempPrm['CTRL_WORD1'] = (0x0005,)
            tempPrm['prm_name'] = 'Dump Read Buffer'
            tempPrm['BUFFER_LENGTH'] = wordTuple(0x200)
            try:
               stat = ICmd.St(tempPrm)
            except Exception, e:
               stat = e[0]
               objMsg.printMsg("dump read buffer Exception data : %s"%e)

         minLBA = 0
         maxLBA = self.maxLBA
         minSectorCnt = 23
         maxSectorCnt = 256
         totalLBAs = 32768
         stampFlag = 0
         flushCacheFlag = 0
         compareFlag = 1
         #RT120112: change due to CPC intrinsic removal
         if (self.oRF.CellType.find('CPC') < 0) or ((self.oRF.CellType.find('CPC') >= 0) and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION): #SI or intrinsic CPC
            RandomWriteDMAExt = {
               'test_num'   : 510,
               'prm_name'   : "RandomWriteDMAExt",
               'spc_id'     : 1,
               'timeout' : 18000,
               'STARTING_LBA' : lbaTuple(minLBA),
               'MAXIMUM_LBA' : lbaTuple(maxLBA),
               'BLKS_PER_XFR': randint(minSectorCnt, maxSectorCnt),
               'TOTAL_BLKS_TO_XFR64' : lbaTuple(totalLBAs),  
               'COMPARE_OPTION' : 0x0001,
               'WRITE_READ_MODE' : 0,  
               'CTRL_WORD2' : 0x04,
               'CTRL_WORD1' : 0x01,
            }
            SequentialWriteDMAExt = {
               'test_num'   : 510,
               'prm_name'   : "SequentialWriteDMAExt",
               'spc_id'     : 1,
               'timeout' : 18000,
               'WRITE_READ_MODE' : 0,  #Write Mode
               'STARTING_LBA' : lbaTuple(minLBA),
               'MAXIMUM_LBA' : lbaTuple(maxLBA),
               'BLKS_PER_XFR': randint(minSectorCnt, maxSectorCnt),
               'TOTAL_BLKS_TO_XFR64' : lbaTuple(totalLBAs),  
               'COMPARE_OPTION' : 0x0001,
               'CTRL_WORD2' : 0x04,
            }

         else: #non-intrinsic CPC
            RandomWriteDMAExt = {
               'test_num'   : 551,
               'prm_name'   : "RandomWriteDMAExt",
               'spc_id'     : 1,
               'timeout' : 18000,
               'STARTING_LBA' : lbaTuple(minLBA),
               'BLKS_PER_XFR': randint(minSectorCnt, maxSectorCnt),
               'TOTAL_BLKS_TO_XFR64' : lbaTuple(totalLBAs),  
               'ACCESS_MODE' : 0x01,
               'CTRL_WORD1' : 0x03,
               'FILL_WRITE_BUFFER': 1
            }
            SequentialWriteDMAExt = {
               'test_num'   : 551,
               'prm_name'   : "SequentialWriteDMAExt",
               'spc_id'     : 1,
               'timeout' : 18000,
               'STARTING_LBA' : lbaTuple(minLBA),
               'BLKS_PER_XFR': randint(minSectorCnt, maxSectorCnt),
               'TOTAL_BLKS_TO_XFR64' : lbaTuple(totalLBAs),  
               'CTRL_WORD1' : 0x00,
               'FILL_WRITE_BUFFER': 1
            }

         for testloop in range(3):
            if loopBreak: break
            objMsg.printMsg("Loop %d of Random Write"%(testloop+1))
            startTime = time.time()
            endTime = startTime+30
            while time.time() < endTime and result == OK:
               xferLen = randint(minSectorCnt, maxSectorCnt)
               #RT070211: correction to upper end of random range, to ensure full 32k write if upper bound value was hit
               startLBA = random.randint(1, self.maxLBA-(32*1024+1))
               RandomWriteDMAExt['BLKS_PER_XFR'] = xferLen
               RandomWriteDMAExt['STARTING_LBA'] = lbaTuple(startLBA)
               #RT120112: change due to CPC intrinsic removal
               if (self.oRF.CellType.find('CPC') < 0) or ((self.oRF.CellType.find('CPC') >= 0) and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION): #SI or intrinsic CPC
                  RandomWriteDMAExt['MAXIMUM_LBA'] = lbaTuple(maxLBA)
               RandomWriteDMAExt['TOTAL_BLKS_TO_XFR64'] = lbaTuple(32*1024)
               objMsg.printMsg("Random Write start LBA %d ,end LBA %d ,tranfer length %d "%(startLBA,maxLBA,xferLen))
               objMsg.printMsg("RandomWriteDMAExt Parameter = %s "%RandomWriteDMAExt)
               try:
                  stat = ICmd.St(RandomWriteDMAExt) #write
               except Exception, e:
                  stat = e[0]
                  objMsg.printMsg("Random Write Exception data : %s"%e)
                  loopBreak = True
               if loopBreak:
                  data = ICmd.translateStReturnToCPC(stat)
                  result = data['LLRET']
                  break

            objMsg.printMsg("Sequential Write 256k LBA Begin")
            objMsg.printMsg("Loop %d of Sequential Write 256k LBA"%(testloop+1))

            if result == OK:
               startTime = time.time()
               endTime = startTime+30

               while time.time() < endTime:
                   startLBA = random.randint(1, self.maxLBA-300000)
                   xferLen = randint(minSectorCnt, maxSectorCnt)
                   SequentialWriteDMAExt['BLKS_PER_XFR'] = xferLen
                   SequentialWriteDMAExt['STARTING_LBA'] = lbaTuple(startLBA)
                   SequentialWriteDMAExt['TOTAL_BLKS_TO_XFR64'] = lbaTuple(256*1024)
                   objMsg.printMsg("Sequential Write start LBA %d ,Transfer Length %d"%(startLBA,xferLen))
                   objMsg.printMsg("SequentialWriteDMAExt Parameter = %s "%SequentialWriteDMAExt)
                   try:
                      stat = ICmd.St(SequentialWriteDMAExt)
                   except Exception, e:
                      stat = e[0]
                      objMsg.printMsg("Sequential Write Exception data : %s"%e)
                      loopBreak = True
                   if loopBreak:
                      data = ICmd.translateStReturnToCPC(stat)
                      result = data['LLRET']
                      break

      if result != OK:
         raise gioTestException(data)
      #if result == OK:
         #ICmd.FlushCache()
         #time.sleep(3)
         #ICmd.StandbyImmed()
      #else:
         #self.GetSerialPortData()
         #raise gioTestException(data)


      objMsg.printMsg("RAMTest END")
      return result,data


   def doVoltageHighLow(self):
      self.testName = 'Voltage High Low'
      self.dut.testName = 'Voltage High Low'
      self.printTestName(self.testName)
      loops = 2
      nominal_5v   = 5000
      nominal_12v  = 12000
      margin_5v    = -1            # -1(off), 0.0(no margin)
      margin_12v   = -1           # 0.10(10%), 0.05(5%)
      if ConfigVars[CN].has_key('Fin 5vMargin'):
         margin_5v    = ConfigVars[CN]['Fin 5vMargin']
      if ConfigVars[CN].has_key('Fin 12vMargin'):
         margin_12v    = ConfigVars[CN]['Fin 12vMargin']

      if margin_5v  == -1:
         nominal_5v = 0.0
         high_5v= 0
         low_5v = 0
      else:
         high_5v      = nominal_5v  + (nominal_5v  * margin_5v)
         low_5v       = nominal_5v  - (nominal_5v  * margin_5v)

      if margin_12v == -1:
         nominal_12v = 0.0
         high_12v = 0
         low_12v =0
      else:
         high_12v     = nominal_12v + (nominal_12v * margin_12v)
         low_12v      = nominal_12v - (nominal_12v * margin_12v)

      f_nom_5v=nominal_5v/1000;   f_high_5v=high_5v/1000;   f_low_5v=low_5v/1000
      f_nom_12v=nominal_12v/1000; f_high_12v=high_12v/1000; f_low_12v=low_12v/1000

      objMsg.printMsg('Voltage Nom  Margin - 5v = %2.2f - 12v = %2.2f' % (f_nom_5v,  f_nom_12v))
      objMsg.printMsg('Voltage High Margin - 5v = %2.2f - 12v = %2.2f' % (f_high_5v, f_high_12v))
      objMsg.printMsg('Voltage Low  Margin - 5v = %2.2f - 12v = %2.2f' % (f_low_5v,  f_low_12v))

      name = {
      "test1" :(('Voltage High Low Test - %2.2f - %2.2f' % (f_nom_5v,  f_nom_12v)),  'IDT Volt N_N'),
      "test2" :(('Voltage High Low Test - %2.2f - %2.2f' % (f_low_5v,  f_low_12v)),  'IDT Volt L_L'),
      "test3" :(('Voltage High Low Test - %2.2f - %2.2f' % (f_high_5v, f_high_12v)), 'IDT Volt H_H') }

      test = {}
      test['1_5']  = nominal_5v;  test['1_12']  = nominal_12v
      test['2_5']  = low_5v;      test['2_12']  = low_12v
      test['3_5']  = high_5v;     test['3_12']  = high_12v
      for testname in range(1,(len(name)+1)):        #for 3 types of volt range
         for loop in range(loops):                  #powercycle for each type of volt range
            volts5   = ('%d_5'  % testname)   # volt5  = 1_5 to 10_5
            volts12  = ('%d_12' % testname)   # volt12 = 1_12 to 10_12
            name_key = ('test%d' % testname)  # test1 to test10
            objMsg.printMsg(name[name_key][0])
         objMsg.printMsg('test[volts5] %s, test[volts12] %s '%(test[volts5],test[volts12]))
         if testSwitch.IO_MQM_SIC_TESTTIME_OPTIMIZATION:
            objPwrCtrl.powerCycle(test[volts5],test[volts12], driveOnly =1)
         else:
            objPwrCtrl.powerCycle(test[volts5],test[volts12])
      objMsg.printMsg("Voltage High Low END")

   def doLowDutyCycle(self):
       #result =  LowDutyCycle('IDT',10000,14999,1000000,100,2,0.5)      # input(Type, StartLBA, MidLBA, EndLBA, loops, SectCnt, Sec's delay)
       #data = CPCLowDutyRead(StartLBA,EndLBA,StartLBA,StartLBA,EndLBA,SectCnt,Loops,UDMA_Speed,Pattern,(Delay*1000))
       self.testName = 'IDT Low Duty Cycle'
       self.dut.testName = 'IDT Low Duty Cycle'
       self.printTestName(self.testName)
       startLBA = 10000
       midLBA = 14999
       endLBA = 1000000
       loops = 100
       SectCnt = 2
       delay = 0.5
       data = {}
       result = OK
       stat = ()

       #RT010611: T510 issues DITS commands, unlock serial port on FDE drives
       #objPwrCtrl.powerCycle()
       if testSwitch.IO_MQM_SIC_TESTTIME_OPTIMIZATION:
          self.oRF.powerCycle('TCGUnlock', driveOnly=1)
       else:
          self.oRF.powerCycle('TCGUnlock')

       ICmd.SetFeatures(0x03, 0x45)
       ICmd.ClearBinBuff(WBF)
       ICmd.ClearBinBuff(RBF)
       nextSeqLBA = endLBA

       for loop in range(loops):
          randomLBA = randint(startLBA, endLBA)
          objMsg.printMsg("%s loop %d"%(self.testName,loop))
          try:
             data = ICmd.SequentialReadDMAExt(randomLBA, randomLBA+SectCnt,STEP_LBA=SectCnt,BLKS_PER_XFR=SectCnt,stSuppressResults=ST_SUPPRESS__ALL) #Change for Kinta branch
          except Exception, e:
             data = e[0]
             objMsg.printMsg("Exception data : %s"%e)
          result = data['LLRET']
          if result != OK:
             break
          time.sleep(delay)
          try:
             data = ICmd.SequentialWriteDMAExt(randomLBA, randomLBA+SectCnt,STEP_LBA=SectCnt,BLKS_PER_XFR=SectCnt,DATA_PATTERN0=0x00000000,stSuppressResults=ST_SUPPRESS__ALL) #Change for Kinta branch
          except Exception, e:
             data = e[0]
             objMsg.printMsg("Exception data : %s"%e)
          result = data['LLRET']
          if result != OK:
             break
          time.sleep(delay)
          randScnt = randint(1, 256)
          try:
             data = ICmd.SequentialReadDMAExt(nextSeqLBA, nextSeqLBA+randScnt,STEP_LBA=randScnt,BLKS_PER_XFR=randScnt,stSuppressResults=ST_SUPPRESS__ALL) #Change for Kinta branch
          except Exception, e:
             data  = e[0]
             objMsg.printMsg("Exception data : %s"%e)
          result = data['LLRET']
          time.sleep(delay)
          nextSeqLBA = nextSeqLBA+randScnt

       #RT070211: a sequentialread reverse is required here after the end of loop
       if result == OK:
          SequentialReadRev = {
            'test_num'   : 510,
            'prm_name'   : "SequentialReadDMAExtRev",
            'spc_id'     : 1,
            'timeout'    : 252000,
            'STARTING_LBA' : lbaTuple(startLBA),
            'MAXIMUM_LBA' : lbaTuple(endLBA),
            'BLKS_PER_XFR': SectCnt,
            'TOTAL_BLKS_TO_XFR64' : lbaTuple(endLBA-startLBA+1),
            'CTRL_WORD1' : 0x0210,
            'CTRL_WORD2' : 0x0080
          }
          try:
             stat = ICmd.St(SequentialReadRev)
          except Exception, e:
             stat = e[0]
             objMsg.printMsg("SequentialReadDMAExtRev Exception data : %s"%e)
          data = ICmd.translateStReturnToCPC(stat)
          result = data['LLRET']
       if result != OK:
          raise gioTestException(data)
      #if result == OK:
         #ICmd.FlushCache()
         #time.sleep(3)
         #ICmd.StandbyImmed()
      #else:
         #self.GetSerialPortData()
         #raise gioTestException(data)


       objMsg.printMsg("Low Duty Cycle END")
       return result,data

   def CheckSmartLogs(self,Check=ON):
       objMsg.printMsg("Check Smart Logs BEGIN,Check = %s"%Check)
       AttrCheck = OFF
       if ConfigVars[CN].has_key('SMART CHECK ATTR') and ConfigVars[CN]['SMART CHECK ATTR'] == 'ON':
          AttrCheck = ON
       if AttrCheck == OFF:
          return
       objPwrCtrl.powerCycle(5000,12000,10,30)
       TestType = 'IDT'
       TestName = 'Check SMART Log'
       AttrCheck = ON
       Check_B410 = ON
       Check_B412 = ON
       result = OK
       smartList = CSmartDefectList(self.dut,{'failForLimits': 1,'CHECK':Check})
       smartLogDefects, smartAttrDefects = smartList.run()

       if ConfigVars[CN].has_key('SMART CHECK B410') and ConfigVars[CN]['SMART CHECK B410'] == 'OFF':
          Check_B410 = OFF
       if ConfigVars[CN].has_key('SMART CHECK B412') and ConfigVars[CN]['SMART CHECK B412'] == 'OFF':
          Check_B412 = OFF

       if Check == ON and (smartAttrDefects['GLIST'] > TP.prm_SmartDefectList.get('GList Limit', 0)):
          objMsg.printMsg('Retired Sector Count(Attr5) exceeded Glist limit')
          failure = ('%s %s' % (TestType, 'A8 LOG'))
          #driveattr['failcode'] = failcode[failure]
          result = FAIL

       if Check == ON and (smartAttrDefects['PENDING'] > TP.prm_SmartDefectList.get('PList Limit', 0)):
          objMsg.printMsg('Pending Spare Count(Attr197) exceeded Plist limit')
          failure = ('%s %s' % (TestType, 'A9 LOG'))
          #driveattr['failcode'] = failcode[failure]
          result = FAIL

       if Check == ON and Check_B410 == ON and (smartAttrDefects['SPARES_BEFORE_RESET'] > TP.prm_SmartDefectList.get('GList Limit', 0)):
          objMsg.printMsg('Spare Count(410) when last SmartReset exceeded Glist limit')
          failure = ('%s %s' % (TestType, 'A8 LOG'))
          #driveattr['failcode'] = failcode[failure]
          result = FAIL

       if Check == ON and Check_B412 == ON and (smartAttrDefects['PENDING_BEFORE_RESET'] > TP.prm_SmartDefectList.get('PList Limit', 0)):
          objMsg.printMsg('Pending Spare Count(412) when last SmartReset exceeded Plist limit')
          failure = ('%s %s' % (TestType, 'A9 LOG'))
          #driveattr['failcode'] = failcode[failure]
          result = FAIL

       #check A1
       objMsg.printMsg('Check A1')
       CEDisplay = CCriticalEvents(self.dut,{'CHECK':Check})
       CEDisplay.run()
       if Check == ON and result == OK:
          objMsg.printMsg('Smart Attribute Check passed')

       objMsg.printMsg("Check Smart Logs END")
       return result

   def GetSerialPortData(self):
       #if Get_SERIAL_PORT_DATA != ON:
	   #return
       timeout = 60000
       objMsg.printMsg('*****************************************************************************')
       objMsg.printMsg('*                       Serial Port Debug Info                              *')
       objMsg.printMsg('*****************************************************************************')
       self.oRF.disableAPM('GetSerialPortData')
       objMsg.printMsg('Serial Port Data :')

       objMsg.printMsg('*****************************************************************************')
       objMsg.printMsg('SMART Data :')
       smartEnableOperData = ICmd.SmartEnableOper()
       self.CheckSmartLogs(OFF)
       #oSerial = serialScreen.sptDiagCmds()
       self.oRF.powerCycle('TCGUnlock')
       self.oRF.disableAPM('GetSerialPortData')
       sptCmds.enableDiags()
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
          objMsg.printMsg("Data returned from ^E command - data = %s" % `data`)

          #Ctrl('S', matchStr='\r')
          #objMsg.printMsg('Ctrl S :')
          #WriteToResultsFile(GetBuffer(SBF, 0, 10240)['DATA'] + '\n')

          objMsg.printMsg('*****************************************************************************')
          objMsg.printMsg('Command History Ctrl X :')
          data = sptCmds.execOnlineCmd(CTRL_X, timeout = timeout, waitLoops = 100)
          objMsg.printMsg("Data returned from Ctrl-X command:\n%s" % data)

          objMsg.printMsg('*****************************************************************************')
          sptCmds.gotoLevel('T')
          objMsg.printMsg('Defect Alt List V4 :')
          data = sptCmds.sendDiagCmd("V4",timeout = timeout, printResult = True, loopSleepTime=0)
          objMsg.printMsg('Servo Flaw List :')
          data = sptCmds.sendDiagCmd("V8",timeout = timeout, printResult = True, loopSleepTime=0)
          objMsg.printMsg('Primary Servo Flaw List :')
          data = sptCmds.sendDiagCmd("V10",timeout = timeout, printResult = True, loopSleepTime=0)
          objMsg.printMsg('Defective Track List :')
          data = sptCmds.sendDiagCmd("V800",timeout = timeout, printResult = True, loopSleepTime=0)


          objMsg.printMsg('*****************************************************************************')
          objMsg.printMsg('Diode Temperature :')
          data = sptCmds.execOnlineCmd(CTRL_B, timeout = timeout, waitLoops = 100)
          objMsg.printMsg("Data returned from CTRL_B command:\n%s" % data)
          Pat = re.compile(', (?P<thermistor>\d+)d\r\n')
          Mat = Pat.search(data)
          thermistor = -1
          if Mat:
             thermistor = int(Mat.groupdict()['thermistor'])
          objMsg.printMsg('Diode Temp Reading=%s' % thermistor)

          objMsg.printMsg('*****************************************************************************')
          objMsg.printMsg('Servo Data :')
          sptCmds.gotoLevel('4')
          objMsg.printMsg('Servo Event Log :')
          data = sptCmds.sendDiagCmd('q', timeout=timeout, altPattern='4>', printResult=True)
          data = sptCmds.sendDiagCmd('g', timeout=timeout, altPattern='4>', printResult=True)

          objMsg.printMsg('*****************************************************************************')
          objMsg.printMsg('Smart Data :')
          sptCmds.gotoLevel('1')
          # Dump Smart Attribute
          data = sptCmds.sendDiagCmd('N5', printResult = True)
          # Dump Smart CE
          data = sptCmds.sendDiagCmd('N8', printResult = True)
          # Dump Smart RList
          data = sptCmds.sendDiagCmd('N18', printResult = True)
       except Exception, e:
          objMsg.printMsg("Serial Port Exception data : %s"%e)

       objPwrCtrl.powerCycle(5000,12000,10,30)

       objMsg.printMsg('*****************************************************************************')
       objMsg.printMsg('*                       Serial Port Debug End                               *')
       objMsg.printMsg('*****************************************************************************')


   def doEncroachmentEUP(self):

      import random
      B_Msg = ON      # Buffer Message

      TestType = ('IDT')
      TestName = ('ENC EUP')
      self.testName = ('%s %s' % (TestType, TestName))                       # Test Name for file formatting
      self.printTestName(self.testName)

      result = OK
      data = {}

      startLBA = 0
      stepLBA = 3024
      sectCnt = 256

      WrtLoop = 5000
      pattern = 0x00000000#0xFAFAFAFA
      maxLBA = self.maxLBA

      #driveattr['testseq'] = TestName.replace(' ','_')
      ICmd.SetIntfTimeout(10000)

      ENCROACHMENT_EUP = ON

      if ENCROACHMENT_EUP == ON:
         self.testCmdTime = 0

         #RT010611: T510 issues DITS commands, unlock serial port on FDE drives
         #objPwrCtrl.powerCycle()
         self.oRF.powerCycle('TCGUnlock')
         tempPrm = WritePatternToBuffer.copy()

         tempPrm['DATA_PATTERN0'] = wordTuple(pattern)
         tempPrm['DATA_PATTERN1'] = wordTuple(pattern)

         ICmd.ClearBinBuff(WBF)
         ICmd.St(tempPrm)

         if B_Msg:
            objMsg.printMsg('%s Write Buffer Data ----------------------------------------' % TestName)
            wb_data = ICmd.GetBuffer(WBF, 0, 550)['DATA']
            objMsg.printMsg('%s %s' % (TestName, wb_data[0:20]))
            objMsg.printMsg('%s %s' % (TestName, wb_data[512:532]))

         objMsg.printMsg('%s running %d loops. StartLBA=%d StepLBA=%d sectCnt=%d Pattern=%X' % \
                              (TestName, WrtLoop, startLBA, stepLBA, sectCnt, int(pattern)))

         EncroachmentEUP = {
            'test_num'   : 643,
            'prm_name'   : "EncroachmentEUP",
            'timeout' : 252000,
            'WRITE_READ_MODE' : (0x01), #Write Mode
            'STARTING_LBA' : lbaTuple(startLBA),
            'STEP_SIZE' : lbaTuple(stepLBA),
            'FIXED_SECTOR_COUNT' : sectCnt,
            'LOOP_COUNT' : WrtLoop,
            'TEST_FUNCTION' : 0x60,
         }
         stat = ICmd.St(EncroachmentEUP)
         data = ICmd.translateStReturnToCPC(stat)
         result = data['LLRET']

            # DT150310 Add SeqRead
         if result == OK:
            objMsg.printMsg('%s Flush Cache, Clear Buffers, Fill 0x%2X Data' % (TestName, int(pattern)))
            result = ICmd.FlushCache()
            ICmd.ClearBinBuff(RBF)
            startLBA = 0
            #RT300311 Sync up with Gen2.2B3
            #endLBA = maxLBA - 200000
            endLBA = maxLBA
            stepLBA = sectCnt
            stampFlag = 0
            compFlag = 0   # can not do compare. cause pattern is only written to random locations.

            tempPrm = SequentialReadDMAExt.copy()
            tempPrm['MAXIMUM_LBA'] = lbaTuple(endLBA)

            #stat = ICmd.SequentialReadDMAExt(startLBA, endLBA, stepLBA, sectCnt, stampFlag, compFlag)
            stat = ICmd.St(tempPrm)
            data = ICmd.translateStReturnToCPC(stat)
            result = data['LLRET']
            objMsg.printMsg('%s SeqRead Data=%s Result=%s' % (TestName, data, result))

         if B_Msg or data['LLRET'] != OK:
            objMsg.printMsg('%s Read Buffer Data ----------------------------------------' % TestName)
            rb_data = ICmd.GetBuffer(RBF, 0, 550)['DATA']
            objMsg.printMsg('%s %s' % (TestName, rb_data[0:20]))
            objMsg.printMsg('%s %s' % (TestName, rb_data[512:532]))

          # end
         if result != OK:
            raise gioTestException(data)
         #if result == OK:
            #ICmd.FlushCache()
            #time.sleep(3)
            #ICmd.StandbyImmed()
         #else:
            #self.GetSerialPortData()
            #raise gioTestException(data)


      return result

   def doReadZeroCompare(self, NumLBA='MaxLBA'):
      P_Msg = ON      # Performance Message
      F_Msg = ON      # Failure Message
      B_Msg = OFF      # Buffer Message
      data = {}
      result = OK
      TestType = ('IDT')
      TestName = ('Read Zero Compare')                       # Test Name for file formatting
      self.testName = ('%s %s' % (TestType, TestName))
      self.dut.testName = self.testName

      self.printTestName(self.testName)

      #RT010611: T510 issues DITS commands, unlock serial port on FDE drives
      #objPwrCtrl.powerCycle()
      if testSwitch.IO_MQM_SIC_TESTTIME_OPTIMIZATION:
         self.oRF.powerCycle('TCGUnlock', driveOnly=1)
      else:
         self.oRF.powerCycle('TCGUnlock')

      # Setup Parameters
      UDMA_Speed = 0x45
      Pattern = str(0x0000)
      OneMegByte = 1048576                                        # 1024 * 1024
      BlockSize  = 512                                            # Sector Size
      NumMegByte = 5                                              # Number of MegaBytes
      StepLBA = 256
      SectCount = 256
      StampFlag = 0
      CompFlag = 1
      BufferSizeByte = OneMegByte*NumMegByte                      # Buffer Size in Bytes
      BufferSizeSect = BufferSizeByte/BlockSize                   # Buffer Size in Sectors
      StartLBA = 0
      if NumLBA == ('MaxLBA'):
         EndLBA = self.maxLBA
      else:
         EndLBA = (NumLBA)

      self.udmaSpeed = UDMA_Speed
      self.pattern = Pattern
      self.sectorCount = SectCount
      self.numBlocks = EndLBA/SectCount
      self.timeout = self.calculateTimeout(self.numBlocks,self.sectorCount)
      objMsg.printMsg('%s Start LBA=%d End LBA=%d Sector Count=%d Pattern=0x%2X' % \
                     (TestName, StartLBA, EndLBA, BufferSizeSect, int(Pattern)))

      objMsg.printMsg('%s Make Alternate Buffer Size %d MB' % (self.testName, NumMegByte))
      ICmd.MakeAlternateBuffer(1, BufferSizeSect)
      objMsg.printMsg('%s Flush Cache, Clear Buffers, Fill 0x%2X Data' % (self.testName, int(Pattern)))
      ICmd.FlushCache(); ICmd.ClearBinBuff(WBF, wordTuple(BufferSizeByte)); ICmd.ClearBinBuff(RBF, wordTuple(BufferSizeByte))
      #ICmd.FillBuffByte(RBF,Pattern,0,BufferSizeByte)

      if B_Msg:
         objMsg.printMsg('%s Write Buffer Data ----------------------------------------' % self.testName)
         wb_data = ICmd.GetBuffer(WBF, 0, 550)['DATA']
         objMsg.printMsg('%s %s' % (self.testName, wb_data[0:20]))
         objMsg.printMsg('%s %s' % (self.testName, wb_data[512:532]))
         objMsg.printMsg('%s Write Buffer Data ----------------------------------------' % self.testName)
         wb_data = ICmd.GetBuffer(RBF, BufferSizeByte-512, BufferSizeByte)['DATA']
         objMsg.printMsg('%s %s' % (self.testName, wb_data[0:20]))
         objMsg.printMsg('%s %s' % (self.testName, wb_data[512:532]))

      result = ICmd.SetFeatures(0x03,UDMA_Speed)['LLRET']
      if result != OK:
         objMsg.printMsg('%s Failed SetFeatures - Transfer Rate = UDMA-%d' % (self.testName, self.getUDMASpeed(UDMA_Speed)))
      else:
         objMsg.printMsg('%s Passed SetFeatures - Transfer Rate = UDMA-%d' % (self.testName, self.getUDMASpeed(UDMA_Speed)))

         #RT120112: change due to CPC intrinsic removal
         if (self.oRF.CellType.find('CPC') < 0) or ((self.oRF.CellType.find('CPC') >= 0) and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION): #SI or intrinsic CPC
            SeqReadCompare = {
               'test_num'   : 510,
               'prm_name'   : "SeqReadCompare",
               'spc_id'     : 1,
               'timeout' : 18000,
               'WRITE_READ_MODE' : (0x01), #Read Mode
               'STARTING_LBA' : lbaTuple(StartLBA),
               'TOTAL_BLKS_TO_XFR64': lbaTuple(EndLBA - StartLBA),
               'BLKS_PER_XFR' : SectCount,
               'DATA_PATTERN0' : (0,0),
               'PATTERN_MODE'  : (0x80),
               'ENABLE_HW_PATTERN_GEN' : 0x1
            }
         else: #non-intrinsic CPC
            #RT150312: replacement to T551 as recommended by Kumanan since T510 with compare is not working
            SeqReadCompare = {
               'test_num'   : 551,
               'prm_name'   : "SeqReadCompare",
               'spc_id'     : 1,
               'timeout' : 18000,
               'CTRL_WORD1' : (0x010), #Read Mode
               'STARTING_LBA' : lbaTuple(StartLBA),
               'TOTAL_BLKS_TO_XFR64' : lbaTuple(EndLBA - StartLBA),
               'DATA_PATTERN0' : (0,0),
               'MAX_NBR_ERRORS' : 0,
            }
         #stat = ICmd.SequentialReadDMAExt(StartLBA, EndLBA, StepLBA, SectCount, COMPARE_FLAG = CompFlag, STAMP_FLAG = StampFlag )
         stat = ICmd.St(SeqReadCompare)
         self.testCmdTime += float(data.get('CT','0'))/1000
         data = ICmd.translateStReturnToCPC(stat)
         result = data['LLRET']
         if result != OK:
            objMsg.printMsg("%s SequentialReadDMA Failed - Data: %s" % (self.testName, data))
         else:
            objMsg.printMsg("%s SequentialReadDMA Passed - Data: %s" % (self.testName, data))
      if B_Msg or result != OK:
         objMsg.printMsg('%s Read Buffer Data ----------------------------------------' % TestName)
         rb_data = ICmd.GetBuffer(2, 0, 550)['DATA']
         objMsg.printMsg('%s %s' % (self.testName, rb_data[0:20]))
         objMsg.printMsg('%s %s' % (self.testName, rb_data[512:532]))

      # DT141010
      objMsg.printMsg('Restore Primary Buffer')
      ICmd.RestorePrimaryBuffer(WBF)

      #self.displayCmdTimes(self.testName,'CPC',self.testCmdTime,self.sectorCount)
      if result == OK:
         if P_Msg:
               BlocksXfrd=EndLBA;NumCmds=(EndLBA/SectCount)
               #self.displayPerformance(TestName,NumCmds,BlocksXfrd,BlockSize,self.testCmdTime)
         objMsg.printMsg('%s Test Passed' % self.testName)
      else:
         objMsg.printMsg('%s Failed Result=%s Data=%s' % (self.testName, result, data))

         raise gioTestException(data)

      if result != OK:
         raise gioTestException(data)
      #if result == OK:
         #ICmd.FlushCache()
         #time.sleep(3)
         #ICmd.StandbyImmed()
      #else:
         #self.GetSerialPortData()
         #raise gioTestException(data)


      return result


   def doReadZeroCompareGuard(self, NumLBA='MaxLBA', LBABand = 20971520):
      P_Msg = ON      # Performance Message
      F_Msg = ON      # Failure Message
      B_Msg = OFF      # Buffer Message
      data = {}
      result = OK
      TestType = ('IDT')
      TestName = ('Read Zero Compare')                       # Test Name for file formatting
      self.testName = ('%s %s' % (TestType, TestName))
      self.dut.testName = self.testName

      self.printTestName(self.testName)

      #RT010611: T510 issues DITS commands, unlock serial port on FDE drives
      #objPwrCtrl.powerCycle()
      self.oRF.powerCycle('TCGUnlock')

      # Setup Parameters
      UDMA_Speed = 0x45
      Pattern = str(0x0000)
      OneMegByte = 1048576                                        # 1024 * 1024
      BlockSize  = 512                                            # Sector Size
      NumMegByte = 5                                              # Number of MegaBytes
      StepLBA = 256
      SectCount = 256
      StampFlag = 0
      CompFlag = 1

      # DT120909 Reduce buffer size
      #BufferSizeByte = OneMegByte*NumMegByte                      # Buffer Size in Bytes
      #BufferSizeSect = BufferSizeByte/BlockSize                   # Buffer Size in Sectors
      BufferSizeByte = 5 * 512 * 512             # Buffer Size in Bytes
      BufferSizeSect = 512 * 5                   # Buffer Size in Sectors

      # DT221009 for 1st and last 20M sector
      ODStartLBA = 0
      ODEndLBA = ODStartLBA + LBABand
      IDStartLBA = self.oRF.IDAttr['MaxLBA'] - LBABand
      IDEndLBA = self.oRF.IDAttr['MaxLBA']
      TotalLBA = 2 * LBABand


      self.udmaSpeed = UDMA_Speed
      self.pattern = Pattern
      self.sectorCount = SectCount
      self.numBlocks = TotalLBA/SectCount
      self.timeout = self.calculateTimeout(self.numBlocks,self.sectorCount)

      objMsg.printMsg('%s Make Alternate Buffer Size %d MB' % (self.testName, NumMegByte))
      ICmd.MakeAlternateBuffer(1, BufferSizeSect)
      objMsg.printMsg('%s Flush Cache, Clear Buffers, Fill 0x%2X Data' % (self.testName, int(Pattern)))
      ICmd.FlushCache(); ICmd.ClearBinBuff(WBF, wordTuple(BufferSizeByte)); ICmd.ClearBinBuff(RBF, wordTuple(BufferSizeByte))
      #ICmd.FillBuffByte(RBF,Pattern,0,BufferSizeByte)

      if B_Msg:
         objMsg.printMsg('%s Write Buffer Data ----------------------------------------' % self.testName)
         wb_data = ICmd.GetBuffer(WBF, 0, 550)['DATA']
         objMsg.printMsg('%s %s' % (self.testName, wb_data[0:20]))
         objMsg.printMsg('%s %s' % (self.testName, wb_data[512:532]))
         objMsg.printMsg('%s Write Buffer Data ----------------------------------------' % self.testName)
         wb_data = ICmd.GetBuffer(RBF, BufferSizeByte-512, BufferSizeByte)['DATA']
         objMsg.printMsg('%s %s' % (self.testName, wb_data[0:20]))
         objMsg.printMsg('%s %s' % (self.testName, wb_data[512:532]))

      result = ICmd.SetFeatures(0x03,UDMA_Speed)['LLRET']
      if result != OK:
         objMsg.printMsg('%s Failed SetFeatures - Transfer Rate = UDMA-%d' % (self.testName, self.getUDMASpeed(UDMA_Speed)))
      else:
         objMsg.printMsg('%s Passed SetFeatures - Transfer Rate = UDMA-%d' % (self.testName, self.getUDMASpeed(UDMA_Speed)))
         #RT120112: change due to CPC intrinsic removal
         if (self.oRF.CellType.find('CPC') < 0) or ((self.oRF.CellType.find('CPC') >= 0) and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION): #SI or intrinsic CPC
            SeqReadCompare = {
               'test_num'   : 510,
               'prm_name'   : "SeqReadCompare",
               'spc_id'     : 1,
               'timeout' : 18000,
               'WRITE_READ_MODE' : (0x01), #Read Mode
               'STARTING_LBA' : lbaTuple(ODStartLBA),
               'TOTAL_BLKS_TO_XFR64': lbaTuple(ODEndLBA - ODStartLBA),
               'BLKS_PER_XFR' : SectCount,
               'DATA_PATTERN0' : (0,0),
               'PATTERN_MODE'  : (0x80),
               'COMPARE_OPTION' : 0x1,
               'ENABLE_HW_PATTERN_GEN' : 0x1
            }
         else : #non-intrinsic CPC
            #RT150312: replacement to T551 as recommended by Kumanan since T510 with compare is not working
            SeqReadCompare = {
               'test_num'   : 551,
               'prm_name'   : "SeqReadCompare",
               'spc_id'     : 1,
               'timeout' : 18000,
               'CTRL_WORD1' : (0x010), #Read Mode
               'STARTING_LBA' : lbaTuple(ODStartLBA),
               'TOTAL_BLKS_TO_XFR64': lbaTuple(ODEndLBA - ODStartLBA),
               'DATA_PATTERN0' : (0,0),
               'MAX_NBR_ERRORS' : 0,
               'PATTERN_MODE'  : (0x80),
            }

         objMsg.printMsg('%s Start LBA=%d End LBA=%d Sector Count=%d Pattern=0x%2X' % \
                     (TestName, ODStartLBA, ODEndLBA, BufferSizeSect, int(Pattern)))

         stat = ICmd.St(SeqReadCompare)
         self.testCmdTime += float(data.get('CT','0'))/1000
         data = ICmd.translateStReturnToCPC(stat)
         result = data['LLRET']

         if result == OK:
            SeqReadCompare['STARTING_LBA'] = lbaTuple(IDStartLBA)
            SeqReadCompare['TOTAL_BLKS_TO_XFR64'] = lbaTuple(IDEndLBA - IDStartLBA)
            objMsg.printMsg('%s Start LBA=%d End LBA=%d Sector Count=%d Pattern=0x%2X' % \
                     (TestName, IDStartLBA, IDEndLBA, BufferSizeSect, int(Pattern)))

            stat = ICmd.St(SeqReadCompare)
            self.testCmdTime += float(data.get('CT','0'))/1000
            data = ICmd.translateStReturnToCPC(stat)
            result = data['LLRET']

      if result != OK:
         objMsg.printMsg("%s SequentialReadDMA Failed - Data: %s" % (self.testName, data))
      else:
         objMsg.printMsg("%s SequentialReadDMA Passed - Data: %s" % (self.testName, data))
      if B_Msg or result != OK:
         objMsg.printMsg('%s Read Buffer Data ----------------------------------------' % TestName)
         rb_data = ICmd.GetBuffer(2, 0, 550)['DATA']
         objMsg.printMsg('%s %s' % (self.testName, rb_data[0:20]))
         objMsg.printMsg('%s %s' % (self.testName, rb_data[512:532]))

      # DT141010
      objMsg.printMsg('Restore Primary Buffer')
      ICmd.RestorePrimaryBuffer(WBF)

      #self.displayCmdTimes(self.testName,'CPC',self.testCmdTime,self.sectorCount)
      if result == OK:
         if P_Msg:
               BlocksXfrd=TotalLBA;NumCmds=(TotalLBA/SectCount)
               #self.displayPerformance(TestName,NumCmds,BlocksXfrd,BlockSize,self.testCmdTime)
         objMsg.printMsg('%s Test Passed' % self.testName)
      else:
         objMsg.printMsg('%s Failed Result=%s Data=%s' % (self.testName, result, data))

         raise gioTestException(data)

      if result != OK:
         raise gioTestException(data)
      #if result == OK:
         #ICmd.FlushCache()
         #time.sleep(3)
         #ICmd.StandbyImmed()
      #else:
         #self.GetSerialPortData()
         #raise gioTestException(data)


      return result

   def doIdleAPMTest(self):
      P_Msg = ON      # Performance Message
      F_Msg = ON      # Failure Message
      B_Msg = ON      # Buffer Message
      mode2848 = 48
      data = {}
      result = OK
      DoRetry = ON

      TestType = ('IDT')
      TestName = ('Idle APM Test')                       # Test Name for file formatting
      #driveattr['testseq'] = TestName.replace(' ','_')
      #driveattr['eventdate'] = time.time()

      self.testName = ('%s %s' % (TestType, TestName))


      if self.oRF.IDAttr['APM_MODE'] == 'OFF':
         IDLE_APM_TEST = OFF
      else:
         IDLE_APM_TEST = ON

      if IDLE_APM_TEST == ON:
         # Determine whether NVC is supported
         self.testCmdTime = 0
         self.printTestName(self.testName)
         #objPwrCtrl.powerCycle()
         if testSwitch.IO_MQM_SIC_TESTTIME_OPTIMIZATION:
            self.oRF.powerCycle(useHardReset = 1)
         else:
            self.oRF.powerCycle()

         if result == OK:
            #StartTime(TestName, 'funcstart')
            #SetRdWrStatsIDE(TestName, 'On',CollectBER='ON')
            #TestNum = SetTestNumber(TestType)
            #SetIntfTimeout(ConfigVars['Intf Timeout'])
            Pattern = 0x00                                            # Number of MegaBytes
            StepLBA = 256
            SectCount = 256
            StampFlag = 0
            CompFlag = 1
            StartLBA = 0

            if self.oRF.IDAttr['APM_MODE'] == 'ON':
               apmDrive = 1
               apmMsg = 'supported'
               objMsg.printMsg('%s APM supported' % TestName)
            else:
               apmDrive = 0
               apmMsg = 'not supported'
               objMsg.printMsg('%s APM Not supported' % TestName)

            minLBA = 0 #ID_data['Min_lba']
            objMsg.printMsg('%s minLBA: %s' % (TestName, minLBA))
            #Change all idleAPM modules with MaxLBA = 200,000 LBA.
            #As per TechKhoon request- MQM_UNF21D2_4 (Base:MQM_UNF21D2_3) - 18-Jan-2012
            #maxLBA = self.oRF.IDAttr['MaxLBA'] - 256
            maxLBA = 200000
            objMsg.printMsg('%s maxLBA: %s' % (TestName, maxLBA))
            #RT250511: IRSata.359011 fixes the parameter
            #loopTime = 900*1000*1000   #RT210411 bug in SIC test 652 warrants a parameter change here
            loopTime = 900
            objMsg.printMsg('%s Loop Time: %d sec' % (TestName,loopTime))
            apmWaitMin = 30
            apmWaitMax = 600
            napmWait = 7

            if ConfigVars[CN].has_key('MOA SDOD LUL') and ConfigVars[CN]['MOA SDOD LUL'] != UNDEF and ConfigVars[CN]['MOA SDOD LUL'] == 'ON':
               MOA_SDOD = ON
            else:
               MOA_SDOD = OFF

            objMsg.printMsg('%s APM is %s, StartLBA=%d, EndLBA=%d, LoopTime=%d sec, apmWaitMin=%d, apmWaitMax=%d, napmWait=%d' % \
                   (TestName, apmMsg, minLBA, maxLBA, loopTime, apmWaitMin, apmWaitMax, napmWait))

            Retry = 1
            IdleAPM = {
               'test_num'   : 652,
               'prm_name'   : "IdleAPM",
               'timeout' : 252000,
               'MIN_RAND_LBA' : lbaTuple(minLBA),
               'MAX_RAND_LBA' : lbaTuple(maxLBA),
               'LOOP_TIME' : wordTuple(loopTime),
               #RT250511: IRSata.359011 fixes the parameter
               #'APM_WAIT_MAX' : wordTuple(apmWaitMax * 1000), #RT210411 bug in SIC test 652 warrants a parameter change here
               #'APM_WAIT_MIN' : wordTuple(apmWaitMin  * 1000), #RT210411 bug in SIC test 652 warrants a parameter change here
               'APM_WAIT_MAX' : wordTuple(apmWaitMax), #RT210411 bug in SIC test 652 warrants a parameter change here
               'APM_WAIT_MIN' : wordTuple(apmWaitMin), #RT210411 bug in SIC test 652 warrants a parameter change here
               'LULST_WAIT' : (0,0),
               'TEST_FUNCTION' : 1
            }
            for loop in range(Retry+1):

               if result == OK:
                  # DT081008 IdleAPMTest with LULSTB

                  if MOA_SDOD == ON:
                     # DT200709 Improve IdleAPM + LUL
                     LULSTBWait = 300      # sec

                     objMsg.printMsg('%s SDOD LUL is ON, Enable LULSTB in IdleAPMTest' % TestName)
                     objMsg.printMsg('%s with LULSTB, StartLBA=%d, EndLBA=%d, LoopTime=%d sec, apmWaitMin=%d, apmWaitMax=%d, napmWait=%d, LULSTBWait=%d' % \
                            (TestName, minLBA, maxLBA, loopTime, apmWaitMin, apmWaitMax, napmWait, LULSTBWait))

                     IdleAPM['DATA_PATTERN0'] = wordTuple(0x00000000)#(0xB5B5B5B5)
                     IdleAPM['LULST_WAIT'] = wordTuple(LULSTBWait)
                     #data = ICmd.IdleAPMTest(apmDrive,minLBA,maxLBA,loopTime,apmWaitMin,apmWaitMax,napmWait,0xB5B5,LULSTBWait)
                     stat = ICmd.St(IdleAPM)
                  else:   # normal IdleAPMTest w/o LULSTB
                     #data = ICmd.IdleAPMTest(apmDrive,minLBA,maxLBA,loopTime,apmWaitMin,apmWaitMax,napmWait,udmaSpeed,mode2848)
                     stat = ICmd.St(IdleAPM)

                  data = ICmd.translateStReturnToCPC(stat)
                  result = data['LLRET']
                  if result != OK:
                     objMsg.printMsg('%s Failed, Returned Data=%s' % (TestName, data))
#               if result == OK and NVCEnabled:
#                  objMsg.printMsg('%s NV Cache PM Supported, Return from Power Management Mode' % TestName)
#                  data = PassThroughExt(0,0xB6,0,0,0x01,0)
#                  result = data['LLRET']
#                  if result != OK:
#                     objMsg.printMsg('%s Return from Power Management Mode Failed, Returned Msg: %s' % (TestName,data))
               if result != OK and DoRetry == ON:
                  #RT210911: fix syntax error
                  #RetryTest = CheckRetryTest(data['RESULT'], data.get('STS','NIL'), data.get('ERR','NIL'), loop)
                  RetryTest = self.checkRetryTest(data['RESULT'], data.get('STS','NIL'), data.get('ERR','NIL'), loop)
                  if RetryTest != ON: break
                  # DT070709 LLRetry
                  SaveFailureAttributes(data, TestType, TestName)

                  objMsg.printMsg('CPCIdleAPMTest - Loop Number %d of %d Failed - Do Retry' % (loop+1, Retry+1))
                  objMsg.printMsg('CPCIdleAPMTest - Retry - Power Cycle and Re-issue CPC Embedded Command')
                  self.GetSerialPortData()
                  #objPwrCtrl.powerCycle()
                  self.oRF.powerCycle()
                  #if result == OK:
                     #SetRdWrStatsIDE(TestName, 'On')
                  #else: break
                  if result != OK: break
               else: break

         if result != OK:
            objMsg.printMsg('%s Failed Result=%s Data=%s' % (TestName, result, data))
            raise gioTestException(data)

         else:
            objMsg.printMsg('%s Test Passed' % TestName)

         #EndTime(TestName, 'funcstart', 'funcfinish', 'functotal')
         #DisplayCmdTimes(TestName, 'CPC', float(data.get('CT',0))/1000, SectCount)

      else:
         objMsg.printMsg('%s Test OFF' % TestName)

      return result

#---------------------------------------------------------------------------------------------------------#
   def doPerfMeasureZoneDegrade(self):
      D_Msg = ON      # Performance Message
      T_Msg = ON      # Failure Message
      data = {}
      TestType = ('IDT')
      TestName = ('ZONEDEGRADE')
      self.testName = ('%s %s' % (TestType, TestName))                       # Test Name for file formatting

      self.printTestName(self.testName)

      result = OK
      NumZone = 16
      MaxLBA = self.maxLBA - (self.maxLBA % NumZone)
      ZoneStep = MaxLBA / NumZone
      UDMA_Speed = 0x45
      SectCnt = 256
      TxSet1 = {}
      TxSet2 = {}
      ZONETHRUPUT = ON

      #driveattr['testseq'] = TestName.replace(' ','_')
      #ICmd.SetIntfTimeout(ConfigVars[CN]['Intf Timeout'])
      ICmd.SetIntfTimeout(10000)

      if ZONETHRUPUT == ON:

         if result == OK:
            #StartTime(TestName, 'funcstart')
            #driveattr['eventdate'] = time.time()
            self.testCmdTime = 0

            #objPwrCtrl.powerCycle()
            if testSwitch.IO_MQM_SIC_TESTTIME_OPTIMIZATION:
               pass
            else:
               self.oRF.powerCycle()

         if result == OK:
            xfer_key = ('%s_wrt_xfer' % TestType)
            data = ICmd.SetFeatures(0x03, UDMA_Speed)
            result = data['LLRET']
            if result == OK:
               objMsg.printMsg('%s SetFeature Transfer Rate passed' % TestName)
            else:
               objMsg.printMsg('%s SetFeature Transfer Rate failed' % TestName)

         if result == OK:
            StartLBA = 0
            EndLBA = StartLBA + ZoneStep - 1

            for i in range(1, NumZone+1):
               #RT 06072010 Prep the test param
               ReadPrm = TransferRate.copy()
               #RT 30092010 Increase timeout to cater to larger capacity drive (500G and above)
               ReadPrm['timeout'] = 2000
               ReadPrm['STARTING_LBA'] = lbaTuple(StartLBA)
               ReadPrm['TOTAL_BLKS_TO_XFR64'] = lbaTuple(EndLBA - StartLBA)

               WritePrm = ReadPrm.copy()
               WritePrm['WRITE_READ_MODE'] = 1
               #RT120112: change due to CPC intrinsic removal
               if (self.oRF.CellType.find('CPC') < 0) or ((self.oRF.CellType.find('CPC') >= 0) and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION): #SI or intrinsic CPC
                  WritePrm['ENABLE_HW_PATTERN_GEN'] = 1 

               # seq read
               if (result == OK) and (i==1 or i==NumZone):
                  #stat = ICmd.ReadDMAExtTransRate(StartLBA, EndLBA - StartLBA, SectCnt)
                  stat = ICmd.St(ReadPrm)
                  resultObj = self.dut.objSeq.SuprsDblObject.copy()
                  data = ICmd.translateStReturnToCPC(stat)

                  result = data['LLRET']
                  if result == OK:
                     TxRate = int(resultObj['P641_DMAEXT_TRANSFER_RATE'][0]['XFER_RATE_MB_PER_SEC'])
                     objMsg.printMsg('%s MaxLBA=%d ReadDMA Zone=%d StartLBA=%d EndLBA=%d SectCnt=%d TxRate=%d' % \
                                    (TestName, MaxLBA, i, StartLBA, EndLBA, SectCnt, TxRate))
                     TxSet1['ZoneRead%d'% i] = TxRate
                  else:
                     objMsg.printMsg('%s Zone(%d) ReadDMATxRate failed. Result=%s Data=%s' % (TestName, i, result, data))
                     break

               # seq write
               if (result == OK) and (i==1 or i==NumZone):
                  stat = ICmd.St(WritePrm)
                  resultObj = self.dut.objSeq.SuprsDblObject.copy()
                  data = ICmd.translateStReturnToCPC(stat)
                  result = data['LLRET']
                  if result == OK:
                     TxRate = int(resultObj['P641_DMAEXT_TRANSFER_RATE'][0]['XFER_RATE_MB_PER_SEC'])
                     objMsg.printMsg('%s MaxLBA=%d WriteDMA Zone=%d StartLBA=%d EndLBA=%d SectCnt=%d TxRate=%d' % \
                                    (TestName, MaxLBA, i, StartLBA, EndLBA, SectCnt, TxRate))
                     TxSet1['ZoneWrt%d'% i] = TxRate
                  else:
                     objMsg.printMsg('%s Zone(%d) WriteDMATxRate failed. Result=%s Data=%s' % (TestName, i, result, data))
                     break


               StartLBA = StartLBA + ZoneStep
               EndLBA = StartLBA + ZoneStep - 1
               # end for

            StartLBA = 0
            EndLBA = StartLBA + ZoneStep - 1

            for i in range(1, NumZone+1):

               # Bug! ReadPrm needs to be updated with new start and end lba. FMC 12/09/2012
               if testSwitch.IO_MQM_SIC_TESTTIME_OPTIMIZATION:
                  ReadPrm.update(
                     {'STARTING_LBA' : lbaTuple(StartLBA),
                     'TOTAL_BLKS_TO_XFR64' : lbaTuple(EndLBA - StartLBA)}
                     )
                  WritePrm = ReadPrm.copy()
                  #RT120112: change due to CPC intrinsic removal
                  if (self.oRF.CellType.find('CPC') < 0) or ((self.oRF.CellType.find('CPC') >= 0) and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION): #SI or intrinsic CPC
                     WritePrm.update(
                                     {'WRITE_READ_MODE' : 1,
                                     'ENABLE_HW_PATTERN_GEN' : 1
                                    })

               # seq read
               if (result == OK) and (i==1 or i==NumZone):
                  stat = ICmd.St(ReadPrm)
                  resultObj = self.dut.objSeq.SuprsDblObject.copy()
                  data = ICmd.translateStReturnToCPC(stat)
                  result = data['LLRET']
                  if result == OK:
                     TxRate = int(resultObj['P641_DMAEXT_TRANSFER_RATE'][0]['XFER_RATE_MB_PER_SEC'])
                     objMsg.printMsg('%s MaxLBA=%d ReadDMA Zone=%d StartLBA=%d EndLBA=%d SectCnt=%d TxRate=%d' % \
                                    (TestName, MaxLBA, i, StartLBA, EndLBA, SectCnt, TxRate))
                     TxSet2['ZoneRead%d'% i] = TxRate

                  else:
                     objMsg.printMsg('%s Zone(%d) ReadDMATxRate failed. Result=%s Data=%s' % (TestName, i, result, data))
                     break

               # seq write
               if (result == OK) and (i==1 or i==NumZone):
                  stat = ICmd.St(WritePrm)
                  resultObj = self.dut.objSeq.SuprsDblObject.copy()
                  data = ICmd.translateStReturnToCPC(stat)
                  result = data['LLRET']
                  if result == OK:
                     TxRate = int(resultObj['P641_DMAEXT_TRANSFER_RATE'][0]['XFER_RATE_MB_PER_SEC'])
                     objMsg.printMsg('%s MaxLBA=%d WriteDMA Zone=%d StartLBA=%d EndLBA=%d SectCnt=%d TxRate=%d' % \
                                    (TestName, MaxLBA, i, StartLBA, EndLBA, SectCnt, TxRate))
                     TxSet2['ZoneWrt%d'% i] = TxRate
                  else:
                     objMsg.printMsg('%s Zone(%d) WriteDMATxRate failed. Result=%s Data=%s' % (TestName, i, result, data))
                     break

               StartLBA = StartLBA + ZoneStep
               EndLBA = StartLBA + ZoneStep - 1

               # end for

         if result == OK:
            keys1 = TxSet1.keys()
            keys1.sort()
            keys2 = TxSet2.keys()
            keys2.sort()
            for key in TxSet1.keys():
               if TxSet1[key] >= TxSet2[key]:
                  skew = (TxSet1[key] - TxSet2[key]) / TxSet1[key]
               else:
                  skew = (TxSet2[key] - TxSet1[key]) / TxSet2[key]
               objMsg.printMsg('%s Key=%s TxRate1=%d TxRate2=%d' % (TestName, key, TxSet1[key], TxSet2[key]))
               if skew > 0.2:
                  objMsg.printMsg('%s Test failed.' % TestName)
                  result = FAIL
                  break

         if result != OK:
            raise gioTestException(data)
         #if result == OK:
            #ICmd.FlushCache()
            #time.sleep(3)
            #ICmd.StandbyImmed()
         #else:
            #self.GetSerialPortData()
            #raise gioTestException(data)


         #EndTime(TestName, 'funcstart', 'funcfinish', 'functotal')

      return result

   #---------------------------------------------------------------------------------------------------------#
   # DST Start
   #---------------------------------------------------------------------------------------------------------#
   def DSTTest_IDE(self, TestLength):
      D_Msg = OFF
      result = OK
      SMART_DST_IDE_TEST = ON
      TestType = 'IDT'
      #RT060511: amend test name to enable failure code retrieval if test fails
      #TestName = ('DST_%s_IDE' % TestLength)                  # Test Name for file formatting
      TestName = ('%s %s DST' % (TestType, TestLength))                  # Test Name for file formatting

      self.testName = TestName
      self.printTestName(self.testName)
      self.driveAttr['testseq'] = TestName.replace(' ','_')
      self.driveAttr['eventdate'] = time.time()
      if SMART_DST_IDE_TEST == ON:
         #ResetATAMode(TestType)
         #self.oRF.powerCycle('TCGUnlock')
         if testSwitch.IO_MQM_SIC_TESTTIME_OPTIMIZATION:
            self.oRF.powerCycle(useHardReset = 1)
         else:
            self.oRF.powerCycle()
         #self.oRF.disableAPM(TestName)
         ##StartTime(TestName, 'funcstart')
         #self.oRF.setRdWrStatsIDE(TestName, 'On')
         ##TestNum = SetTestNumber(TestType)

         if TestLength == 'Short':
               ConfigVars[CN]['Fin DSTTest'] = 'SHORT'
         else: ConfigVars[CN]['Fin DSTTest'] = 'FULL'
         if result == OK:
            result, data = self.RunDSTTest()
         if result != OK:

            #objMsg.printMsg('%s Test Failed - failcode = %s' % (TestName, self.driveAttr['failcode'][0]))
            #objMsg.printMsg('%s Test Failed - failcode=%s' % (TestName, self.failCode))
            # The failcodes below can be commented out to get true DST "Final" test failcodes.
            if TestLength == 'Short':
               failure = ('%s Short DST' % TestType)
               #self.driveAttr['failcode'] = failcode[failure]

            else:
               failure = ('%s Long DST' % TestType)
               #self.driveAttr['failcode'] = failcode[failure]

            self.failCode = self.oFC.getFailCode(failure)
            # DT050510
            objMsg.printMsg('%s Test Failed - failcode=%s' % (TestName, self.failCode))
            self.currentStep = self.testName
            self.failstep = self.testName

            #RT070211
            raise gioTestException(data)
         else:
            if D_Msg: objMsg.printMsg('%s Test Passed' % TestName)

         ##EndTime(TestName, 'funcstart', 'funcfinish', 'functotal')
         if TestLength == 'Short':
            self.displayCmdTimes(self.testName, 'DST_Short')
         else:
            self.displayCmdTimes(self.testName, 'DST')

         ##if result == OK and IDT_RESULT_FILE_DATA == ON:
            ##TestTime = timetostring(testtime['functotal'])
            ##if TestType != 'MQM':
               ##CollectData(result, TestType, TestNum, TestName, TestTime)

      else:
         objMsg.printMsg('%s Test OFF' % TestName)

      return result
   #---------------------------------------------------------------------------------------------------------#
   def RunDSTTest(self):
      #
      #  Run drive self test
      #
      test_type = ConfigVars[CN]['Fin DSTTest']

      if test_type == 'FULL':
         DST_Test = 2
         objMsg.printMsg('SMART DST Full Read test - Running')
      else:
         DST_Test = 1
         objMsg.printMsg('SMART DST Short Read test - Running')

      if (self.oRF.CellType.find('CPC') >= 0) and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION: #only intrinsic CPC
         ICmd.ReadSectors(100,0,1,0)
      else: #SI and non-intrinsic CPC
         ICmd.ReadSectors(100,1)
      result, data = self.DSTStart(DST_Test)
      ##
      if result['RESULT'] == FAIL:
         return FAIL, data
      else:
         DST_Timeout = result['DST_TIMEOUT']
         DST_Log_Index = result['DST_LOG_INDEX']
      ICmd.SetIntfTimeout(60000)
      result = self.DSTLoop(DST_Test,DST_Timeout)

      if result['RESULT'] == FAIL:
         return FAIL, data
      else:
         DST_Status = result['DST_STATUS']

      if DST_Status >= 1 and DST_Status <= 7:
         self.DSTAnalyzeLog(DST_Test,DST_Log_Index)
         return FAIL, data

      return OK, data

   #--------------------------------  DST Analysis Test  ------------------------------------#
   def DSTAnalyzeLog(self,DST_Test,pre_test_log_index):
      D_Msg = ON
      result = self.GetDSTLogIndex()
      if result['RESULT'] == FAIL: return

      post_test_log_index = result['DST_LOG_INDEX']
      if D_Msg: objMsg.printMsg('SMART Log 6 (DST Log) current index pointer = %d (0-21 valid)' % post_test_log_index)

      if pre_test_log_index == 21:
         old_index = 1
         new_index = post_test_log_index
      else:
         old_index = pre_test_log_index
         new_index = post_test_log_index - 1

      if old_index != new_index:
         objMsg.printMsg('SMART Log 6 (DST Log) failure: no new DST entry posted: current index = %d, previous = %d' % (post_test_log_index,pre_test_log_index))
         objMsg.printMsg('SMART Log 6 (DST Log) data below is probably not valid due to the index problem above:')

      if post_test_log_index != 0:
         byte_index = (post_test_log_index - 1)* 24 + 2
      else:
         byte_index = post_test_log_index * 24 + 2

      data_byte = ord(result['DST_LOG_DATA'][byte_index])
      objMsg.printMsg('SMART Log 6 (DST Log) test type = %d' % data_byte)

      if data_byte != DST_Test:
         objMsg.printMsg('SMART Log 6 (DST Log) failure: invalid or wrong test type (%d)' % data_byte)

      status_byte = ord(result['DST_LOG_DATA'][byte_index+1])
      status = status_byte >> 4
      # DT290710 Add DST status reporting
      self.failStatus = ('DST STS%d' % ( status))

      if status == 0:
         objMsg.printMsg('SMART problem status: DST Log 6 status = PASS (%d) / Read Attrib. DST status = FAIL' % status)
      elif status >= 1 and status <=7:
         if status == 1:
            status_text = 'SELF TEST ABORTED BY HOST'
         elif status == 2:
            status_text = 'SELF TEST INTERRUPTED BY HOST WITH HARD OR SOFT RESET'
         elif status == 3:
            status_text = 'SELF TEST QUIT - UNKNOWN FATAL ERROR'
         elif status == 4:
            status_text = 'SELF TEST COMPLETED - UNKNOWN ERROR'
         elif status == 5:
            status_text = 'SELF TEST COMPLETED - ELECTRICAL TEST ELEMENT ERROR'
         elif status == 6:
            status_text = 'SELF TEST COMPLETED - SERVO TEST ELEMENT ERROR'
         elif status == 7:
            status_text = 'SELF TEST COMPLETED - READ TEST ELEMENT ERROR'
         objMsg.printMsg(('SMART DST Log 6 status %d = ' % status) + status_text)
      elif status >= 8 and status <=14:
         objMsg.printMsg('SMART DST Log 6 status %d = INVALID SMART SELF-TEST STATUS' % status)
      elif status == 15:
         objMsg.printMsg('SMART DST Log 6 status %d = SELF TEST ROUTINE IN PROGRESS' % status)

      percent_remaining = (status_byte & 0x0f) * 10
      objMsg.printMsg('SMART Log 6 (DST Log): SelfTest time remaining until DST completion = %d percent' % percent_remaining)

      error_lba = 0L

      data_byte = ord(result['DST_LOG_DATA'][byte_index+5])
      error_lba = error_lba | data_byte

      data_byte = ord(result['DST_LOG_DATA'][byte_index+6])
      error_lba = error_lba | (data_byte << 8)

      data_byte = ord(result['DST_LOG_DATA'][byte_index+7])
      error_lba = error_lba | (data_byte << 16)

      data_byte = ord(result['DST_LOG_DATA'][byte_index+8])
      error_lba = error_lba | (data_byte << 24)

      objMsg.printMsg('SMART Log 6 (DST Log): failing LBA = %u (0x%08x)' % (error_lba, error_lba))

      return

   #---------------------------------  Loop DST Test  ---------------------------------------#
   def DSTLoop(self,DST_Test,DST_Timeout):
      D_Msg = ON

      timeEnd = time.time() + DST_Timeout

      while (time.time() < timeEnd):
         ICmd.ClearSerialBuffer()
         data = ICmd.SmartReadData()
         result = data['LLRET']

         if result != OK:
            objMsg.printMsg('failed SMART DST 1st time - SmartReadData() - result = %d' % result)
            objMsg.printMsg('data=%s' % `data`)
            data = ICmd.SmartReadData()
            result = data['LLRET']

            if result != OK:
               objMsg.printMsg('SMART DST failed 2nd time - SmartReadData() - result = %d' % result)
               #self.driveAttr['failcode'] = failcode['Fin DST Time']
               failure = 'Fin DST Time'
               self.failCode = self.oFC.getFailCode(failure)
               return {'RESULT':FAIL}
         smartData = ICmd.GetBuffer(RBF, 0, 512*1)['DATA']
         status_byte = ord(smartData[363])

         percent_remaining = (status_byte & 0x0f) * 10
         if D_Msg: objMsg.printMsg('%d percent left' % percent_remaining)

         status = status_byte >> 4

         if status == 0:
            if DST_Test == 2:
               objMsg.printMsg('SMART DST Full Read test - Passed')
            else:
               objMsg.printMsg('SMART DST Short Read test -  Passed')
            return {'RESULT':OK,'DST_STATUS':status}

         if status >= 1 and status <= 7:
            if status == 1:
               status_text = 'SELF TEST ABORTED BY HOST'
            elif status == 2:
               status_text = 'SELF TEST INTERRUPTED BY HOST WITH HARD OR SOFT RESET'
            elif status == 3:
               status_text = 'SELF TEST QUIT - UNKNOWN FATAL ERROR'
            elif status == 4:
               status_text = 'SELF TEST COMPLETED - UNKNOWN ERROR'
            elif status == 5:
               status_text = 'SELF TEST COMPLETED - ELECTRICAL TEST ELEMENT ERROR'
            elif status == 6:
               status_text = 'SELF TEST COMPLETED - SERVO TEST ELEMENT ERROR'
            elif status == 7:
               status_text = 'SELF TEST COMPLETED - READ TEST ELEMENT ERROR'

            objMsg.printMsg(('SMART DST status %d = ' % status) + status_text)
            #self.driveAttr['failcode'] = failcode['Fin DST Time']
            failure = 'Fin DST Time'
            self.failCode = self.oFC.getFailCode(failure)
            return {'RESULT':OK,'DST_STATUS':status}

         if status >= 8 and status <= 14:
            objMsg.printMsg('SMART Loop failed - invalid SMART self-test status: %d' % status)
            return {'RESULT':FAIL}

         # status is 15
         # debug if D_Msg: objMsg.printMsg('SMART Loop in progress')

         if DST_Test == 1:
            ScriptPause(5)
         else:
            ScriptPause(300)

      objMsg.printMsg('SMART DST did NOT finish - 200 Percent Polling Timeout reached')
      #self.driveAttr['failcode'] = failcode['Fin DST Time']
      failure = 'Fin DST Time'
      self.failCode = self.oFC.getFailCode(failure)

      return {'RESULT':FAIL}

   #--------------------------------  Start DST Test  ---------------------------------------#
   def DSTStart(self,DST_Test):
      data = ICmd.SmartEnableOper()
      result = data['LLRET']

      if result != OK:
         objMsg.printMsg('SMART Start failed - SmartEnableOper() - result = %d' % result)
         #self.driveAttr['failcode'] = failcode['Fin DST Start']
         failure = 'Fin DST Start'
         self.failCode = self.oFC.getFailCode(failure)
         return {'RESULT':FAIL}, data

      result = self.GetDSTLogIndex()

      if result['RESULT'] == FAIL:
         return {'RESULT':FAIL}, data
      else:
         log_index = result['DST_LOG_INDEX']

      result = self.GetDSTTimeout(DST_Test)

      if result['RESULT'] == FAIL:
         return {'RESULT':FAIL}, data
      else:
         timeout = result['DST_TIMEOUT']
         if DST_Test == 1 and ConfigVars[CN].has_key('Short DST Timeout'):
            timeout = ConfigVars[CN]['Short DST Timeout']
            objMsg.printMsg('Short DST Timeout reset to %d Seconds according to CMS' % timeout)

      #RT120911: update DST parameters to factor in SMART timeout value
      if DST_Test == 1:
         DSTPara = {
            'test_num'    : 600,
            'prm_name'    : "ShortDST",
            'timeout'   : timeout,
            'MAX_COMMAND_TIME'     : timeout,
            'spc_id'      : 1,
            'TEST_FUNCTION' : (1), # 1=short DST 2=long DST
            #'TEST_OPERATING_MODE' : 1,
            'STATUS_CHECK_DELAY' : (10),
         }
      else:
         DSTPara = {
            'test_num'    : 600,
            'prm_name'    : "LongDST",
            'timeout'   : timeout,
            'MAX_COMMAND_TIME'     : timeout,
            'spc_id'      : 1,
            'TEST_FUNCTION' : (2), # 1=short DST 2=long DST
            #'TEST_OPERATING_MODE' : 2,
            'STATUS_CHECK_DELAY' : (300),
         }
      stat = ()
      try:
         stat = ICmd.St(DSTPara)
      except Exception, e:
         stat = e[0]
         objMsg.printMsg("%s DST Exception data : %s"%(DST_Test, e))

      data = ICmd.translateStReturnToCPC(stat)
      result = data['LLRET']
      objMsg.printMsg("%s DST data : %s"%(DST_Test, data))

      if result != OK:
         return {'RESULT':FAIL}, data

      # set drive timeout to 30 sec.

      return {'RESULT':OK,'DST_LOG_INDEX':log_index,'DST_TIMEOUT':timeout}, data

   #---------------------------------------------------------------------------------------------------------#
   def GetDSTLogIndex(self):
      D_Msg = ON
      ICmd.ClearSerialBuffer()
      data = ICmd.SmartReadLogSec(6,1)
      result = data['LLRET']

      if result != OK:
         objMsg.printMsg('SMART Get Log Index failed - SmartReadLogSec(6,1) - result = %d' % result)
         #self.driveAttr['failcode'] = failcode['Fin DST Log']
         failure = 'Fin DST Log'
         self.failCode = self.oFC.getFailCode(failure)

         return {'RESULT':FAIL}
      smartData = ICmd.GetBuffer(RBF, 0, 512*1)['DATA']
      revision = ord(smartData[0])
      if revision != 1:
         objMsg.printMsg('SMART Get Log Index failed - Log 6 (DST Log) revision check failed, expected = 1, found = %d' % revision)
         #self.driveAttr['failcode'] = failcode['Fin DST Log']
         failure = 'Fin DST Log'
         self.failCode = self.oFC.getFailCode(failure)

         return {'RESULT':FAIL}

      log_index = ord(smartData[508])
      if log_index > 21:
         objMsg.printMsg('SMART Get Log Index failed - invalid Log 6 (DST Log) index pointer = %d ( >21 )' % log_index)
         #self.driveAttr['failcode'] = failcode['Fin DST Log']
         failure = 'Fin DST Log'
         self.failCode = self.oFC.getFailCode(failure)

         return {'RESULT':FAIL}

      if D_Msg: objMsg.printMsg('SMART Log 6 (DST Log) index pointer = %d' % log_index)

      return {'RESULT':OK,'DST_LOG_INDEX':log_index,'DST_LOG_DATA':smartData}

   #----------------------------------------------------------------------------------------#
   def GetDSTTimeout(self,DST_Test):
      ICmd.ClearSerialBuffer()
      data = ICmd.SmartReadData()
      result = data['LLRET']

      if result != OK:
         objMsg.printMsg('SMART Get DST Timeout failed - SmartReadData() - result = %d' % result)
         #self.driveAttr['failcode'] = failcode['Fin DST Time']
         failure = 'Fin DST Time'
         self.failCode = self.oFC.getFailCode(failure)

         return {'RESULT':FAIL}
      smartData = ICmd.GetBuffer(RBF, 0, 512*1)['DATA']
      if DST_Test == 1:
         poll_time = ord(smartData[372])
         if poll_time == 0:
            objMsg.printMsg('SMART Get DST Timeout failed - optimal Short DST time is not supported by SMART code')
            objMsg.printMsg('Timeout returned from SMART LOG = %d minutes' % poll_time)
            #self.driveAttr['failcode'] = failcode['Fin DST Time']
            failure = 'Fin DST Time'
            self.failCode = self.oFC.getFailCode(failure)

            return {'RESULT':FAIL}
         else:
            objMsg.printMsg('Timeout returned from SMART LOG = %d minutes - Short DST polling timeout set to = %d minutes' % (poll_time, poll_time * 2))
            return {'RESULT':OK,'DST_TIMEOUT':poll_time * 120}   # Set Short DST polling to 200% optimal in seconds
      elif DST_Test == 2:
         poll_time = ord(smartData[373])
         if poll_time == 0:
            objMsg.printMsg('SMART Get DST Timeout failed - optimal Long DST time is not supported by SMART code')
            objMsg.printMsg('Timeout returned from SMART LOG = %d minutes' % poll_time)
            #self.driveAttr['failcode'] = failcode['Fin DST Time']
            failure = 'Fin DST Time'
            self.failCode = self.oFC.getFailCode(failure)

            return {'RESULT':FAIL}
         else:
            objMsg.printMsg('Timeout returned from SMART LOG = %d minutes - Long DST polling timeout set to = %d minutes' % (poll_time, poll_time * 2))
            return {'RESULT':OK,'DST_TIMEOUT':poll_time * 120}   # Set Long DST polling to 200% optimal in seconds
      else:
         return {'RESULT':FAIL}

   #---------------------------------------------------------------------------------------------------------#
   # DST End
   #---------------------------------------------------------------------------------------------------------#
   #RT30122010: Adapted new DelayWrite algo from Gen2.2A
   def doDelayWrite(self):
      D_Msg = ON
      T_Msg = ON
      result = OK
      TestType = ('IDT')
      TestName = ('DELAYWRT')
      self.testName = ('%s %s' % (TestType, TestName))                       # Test Name for file formatting
      self.printTestName(self.testName)

      minLBA = startLBA = endLBA = 0
      maxLBA = self.oRF.IDAttr['MaxLBA']

      stepLBA = 256
      sectCnt = 256

      DELAYWRT = ON
      #DelayWrtLoop = 1
      DelayWrtLoop = 1000
      #Pattern = 0x22
      StampFlag = 0
      #minDelay = 100  #ms
      minDelay = 200  #ms
      # DT181110
      #maxDelay = 900  #ms
      #maxDelay = 2000  #ms
      maxDelay = 400  #ms
      stepDelay = 100 #ms
      #GrpCnt = 200
      GrpCnt = 1
      #LBAMode = 28    # from 5M to 10M
      LBAMode = 48     # not use
      DelayStepLba = ((maxDelay - minDelay) / stepDelay + 2) * sectCnt * GrpCnt    #+2 to ensure all delay time execute.
      ICmd.SetIntfTimeout(5000)        # Interface timout 5 sec

      #if ConfigVars[CN].has_key('DELAY WRT') and ConfigVars[CN]['DELAY WRT'] != UNDEF and ConfigVars[CN]['DELAY WRT'] == 'ON':
      #   DELAYWRT = ON
      #else:
      #   DELAYWRT = OFF

      if DELAYWRT == ON:
         self.testCmdTime = 0

         #SetRdWrStatsIDE(TestName, 'On')
         #ICmd.ReceiveSerialCtrl(1)
         #driveattr['testseq'] = TestName.replace(' ','_')
         #driveattr['eventdate'] = time.time()
         SeqDelayWR = {
            'test_num':643,
            'prm_name':'DelayWrite',
            'TEST_FUNCTION': 0x0030,
            'timeout': 30000,
            'GROUP_SIZE': GrpCnt,
            'STARTING_LBA': lbaTuple(minLBA),
            'MIN_DELAY_TIME': minDelay,
            'FIXED_SECTOR_COUNT': sectCnt,
            'WRITE_READ_MODE': 1,
            'TOTAL_BLKS_TO_XFR64': lbaTuple(maxLBA - minLBA),
            'STEP_DELAY_TIME': stepDelay,
            'MAX_DELAY_TIME': maxDelay,
            'stSuppressResults': ST_SUPPRESS__ALL
          }

         if result == OK:
            self.oRF.powerCycle()

         # set APM to C0
         if result == OK:
            data = ICmd.SetFeatures(0x05, 0xC0)
            result = data['LLRET']
            objMsg.printMsg('%s Set APM to 0xC0. Result=%s Data=%s' % (TestName, result, data))

         # disable write cache
         if result == OK:
            data = ICmd.SetFeatures(0x82)
            result = data['LLRET']
            objMsg.printMsg('%s Disable write cache. Result=%s Data=%s' % (TestName, result, data))

         # disable read look ahead
         if result == OK:
            data = ICmd.SetFeatures(0x55)
            result = data['LLRET']
            objMsg.printMsg('%s Disable read look-ahead. Result=%s Data=%s' % (TestName, result, data))

         for i in range(DelayWrtLoop):
            if result == OK:
               startLBA = random.randint(minLBA, maxLBA - DelayStepLba)
               #objMsg.printMsg('%s Randomised StartLBA=%d' % (TestName, startLBA))
               # DT181110 Apply 4K alignment
               # DT170909 Apply offset calculation for multi-sector drive
               if self.oRF.IDAttr['NumLogSect'] > 1:
                  # Adjust for number of physical sector per logical sector
                  startLBA = startLBA - (startLBA % self.oRF.IDAttr['NumLogSect'])
                  #objMsg.printMsg('%s Adjust for multi-sector drive, LogSect/PhySect=%d' % (TestName, self.oRF.IDAttr['NumLogSect']))
                  if self.oRF.IDAttr['OffSetLBA0'] > 0:
                     objMsg.printMsg('%s Adjust for LogBlk in PhyBlk alignment, offset=%d' % (TestName, self.oRF.IDAttr['OffSetLBA0']))
                     if startLBA == 0:    # Avoid negative LBA range, proceed to next block
                        startLBA = startLBA + self.oRF.IDAttr['NumLogSect']
                     # Adjust for alignment of Log Block in Phy Block
                     startLBA = startLBA - self.oRF.IDAttr['OffSetLBA0']

               #objMsg.printMsg('%s Adjusted StartLBA=%d' % (TestName, startLBA))
               #endLBA = startLBA + 5000000
               endLBA =  startLBA + DelayStepLba

               #objMsg.printMsg('%s StartLBA=%d EndLBA=%d SectCnt=%d MinDelay=%d MaxDelay=%d StepDelay=%d GrpCnt=%d' % \
               #               (TestName, minLBA, maxLBA, sectCnt, minDelay, maxDelay, stepDelay, GrpCnt))
               objMsg.printMsg('%s (%d) StartLBA=%d EndLBA=%d SectCnt=%d MinDelay=%d MaxDelay=%d StepDelay=%d GrpCnt=%d' % \
                              (TestName, (i+1), startLBA, endLBA, sectCnt, minDelay, maxDelay, stepDelay, GrpCnt))

               SeqDelayWR['STARTING_LBA'] = lbaTuple(startLBA)
               SeqDelayWR['TOTAL_BLKS_TO_XFR64'] = lbaTuple(endLBA - startLBA)

               stat = ICmd.St(SeqDelayWR)
               data = ICmd.translateStReturnToCPC(stat)
               result = data['LLRET']

            if result != OK:
               objMsg.printMsg('%s SeqDelayWR failed. Result=%s Data=%s' % (TestName, result, data))
               break


         self.testCmdTime += float(data.get('CT','0'))/1000
         #self.displayCmdTimes(self.testName,'CPC',self.testCmdTime,self.sectorCount)

         if result != OK:
            raise gioTestException(data)
         #if result == OK:
            #ICmd.FlushCache()
            #time.sleep(3)
            #ICmd.StandbyImmed()
         #else:
            #self.GetSerialPortData()
            #raise gioTestException(data)


         #EndTime(TestName, 'funcstart', 'funcfinish', 'functotal')

      return result

   #-------------------------------------------------------------------------------------------------------
   def ReadScan(self, TestName, IDStartLBA, ODStartLBA, blockSize, SectCount):

      StampFlag = 0
      CompareFlag = 0
      result = OK

      self.oRF.powerCycle()

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
   def doMSSustainTferRate(self):

      result = OK
      loop = 2
      MS_SUS_TXFER_RATE = ON

      objMsg.printMsg('CGIOTest.py doMSSustainTferRate - non CPC')

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
                  objMsg.printMsg('Re-run MSSTR')
                  loop -= 1 # re-run MSSTR
               else:
                  break # UDE error, fail the drive
            else:
               break # pass

         if result != OK:
            if testSwitch.virtualRun:
               objMsg.printMsg('GIO Test Exception')
            else:
               raise gioTestException(data)

      return result

   #---------------------------------------------------------------------------------------------------------#
   def MSSTR_dblog(self, loopcnt, StartLBA, TotalLBA, WrRate, RdRate): # Loke

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
   def doMSSustainTferRateTest(self):
      D_Msg = ON      # Performance Message
      T_Msg = ON      # Failure Message
      data = {}
      TestType = ('IDT')
      TestName = ('MSSTR')
      self.testName = ('%s %s' % (TestType, TestName))                       # Test Name for file formatting
      self.printTestName(self.testName)

      result = OK
      STRLoop = 15
      #blockSize = 0x5000      # 20480 sectors = 10M bytes
      blockSize = 0x20000      # change to 20K hex
      sectCnt = 256
      TxHead = 0
      TxRate = 0
      TxLBA = 0
      IDStartLBA = self.maxLBA - blockSize
      ODStartLBA = 0

      #RT300311 Sync up with TGen1.3b5   # DT100111 Revised ID TxRate to 14
      IDTxRate = 14    #17
      ODTxRate = 30    #30
      MS_SUS_TXFER_RATE = ON

      #driveattr['testseq'] = TestName.replace(' ','_')

      if MS_SUS_TXFER_RATE == ON:


         #if result == OK:
            #StartTime(TestName, 'funcstart')
            #driveattr['eventdate'] = time.time()
            #SetRdWrStatsIDE(TestName, 'On')
            #ReceiveSerialCtrl(1)
         self.testCmdTime = 0

         #objPwrCtrl.powerCycle()
         self.oRF.powerCycle()
         # DT251109 Add FlushCache to make throughput measurement correct
         ICmd.FlushCache()

         if result == OK:
            objMsg.printMsg('%s (ID)StartLBA=%d (OD)StartLBA=%d BlockSize=%d SectCnt=%d' % \
                           (TestName, IDStartLBA, ODStartLBA, blockSize, sectCnt))

            if testSwitch.virtualRun:
               result = OK # dummy test

               if result == OK:
                  objMsg.printMsg('%s STR Test passed!' % TestName)
               else:
                  objMsg.printMsg('%s Test failed!' % self.testName)
               return (result, data, TestName, IDStartLBA, ODStartLBA, blockSize, sectCnt)

            ReadPrm = TransferRate.copy()

            ReadPrm['stSuppressResults'] = ST_SUPPRESS__ALL
            ReadPrm['TOTAL_BLKS_TO_XFR64'] = lbaTuple(blockSize)

            # RT191110 Enable HW Patt Gen for Read
            #RT120112: change due to CPC intrinsic removal
            if (self.oRF.CellType.find('CPC') < 0) or ((self.oRF.CellType.find('CPC') >= 0) and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION): #only applicable for SIC
               ReadPrm['ENABLE_HW_PATTERN_GEN'] = 1
            WritePrm = ReadPrm.copy()
            WritePrm['WRITE_READ_MODE'] = 1

            # RT191110 Have to 'preload', otherwise the first Read will fail
            WritePrm['STARTING_LBA'] = lbaTuple(IDStartLBA)
            stat = ICmd.St(WritePrm)
            WritePrm['STARTING_LBA'] = lbaTuple(ODStartLBA)
            stat = ICmd.St(WritePrm)

            for i in range(1, STRLoop+1):

               # read ID
               if result == OK:
                  #data = ICmd.ReadDMAExtTransRate(IDStartLBA, blockSize, sectCnt)
                  ReadPrm['STARTING_LBA'] = lbaTuple(IDStartLBA)
                  stat = ICmd.St(ReadPrm)
                  resultObj = self.dut.objSeq.SuprsDblObject.copy()
                  data = ICmd.translateStReturnToCPC(stat)
                  result = data['LLRET']
               if result != OK:
                  objMsg.printMsg('%s Read(ID)(%d) failed. Result=%s Data=%s' % (TestName, i, result, data))
                  break
               else:
                  #TxRate = int(data['TXRATE'])
                  TxRate = int(resultObj['P641_DMAEXT_TRANSFER_RATE'][0]['XFER_RATE_MB_PER_SEC'])
                  readIDRate = TxRate
                  TxHead = int(data['DEV'])
                  #RT120112: change due to CPC intrinsic removal
                  if (self.oRF.CellType.find('CPC') < 0) or ((self.oRF.CellType.find('CPC') >= 0) and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION): #SI or CPCv2.24
                     TxLBA = int(resultObj['P641_DMAEXT_TRANSFER_RATE'][0]['END_LBA'])
                  else: #CPCv3.3
                     TxLBA = int(resultObj['P641_DMAEXT_TRANSFER_RATE'][0]['END_LBA'], 16) #CPC displaying in hex
                  objMsg.printMsg('%s Read(ID)(%d) TxRate=%d MB/s TxHead=%d LastLBA=%s' % (TestName, i, TxRate, TxHead, TxLBA))

                  if TxRate >= IDTxRate:
                     objMsg.printMsg('%s Read(ID) passed. TxRate=%d MB/s' % (TestName, TxRate))
                  else:
                     objMsg.printMsg('%s Read(ID) TxRate(%d MB/s) < %d, Test failed!' % (TestName, TxRate, IDTxRate))
                     #objMsg.printMsg('%s Read(ID) failed! TxRate(%d MB/s) < %d, TxHead=%d, TxLBA=%d' % (TestName, TxRate, IDTxRate, TxHead, TxLBA))
                     result = FAIL
                     break

               # read OD
               if result == OK:
                  #data = ICmd.ReadDMAExtTransRate(ODStartLBA, blockSize, sectCnt)
                  ReadPrm['STARTING_LBA'] = lbaTuple(ODStartLBA)
                  stat = ICmd.St(ReadPrm)
                  resultObj = self.dut.objSeq.SuprsDblObject.copy()
                  data = ICmd.translateStReturnToCPC(stat)
                  result = data['LLRET']

               if result != OK:
                  objMsg.printMsg('%s Read(OD)(%d) failed. Result=%s Data=%s' % (TestName, i, result, data))
                  break
               else:
                  TxRate = int(resultObj['P641_DMAEXT_TRANSFER_RATE'][0]['XFER_RATE_MB_PER_SEC'])
                  readODRate = TxRate
                  TxHead = int(data['DEV'])
                  #RT120112: change due to CPC intrinsic removal
                  if (self.oRF.CellType.find('CPC') < 0) or ((self.oRF.CellType.find('CPC') >= 0) and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION): #for SIC
                     TxLBA = int(resultObj['P641_DMAEXT_TRANSFER_RATE'][0]['END_LBA'])
                  else: #non-intrinsic CPC
                     TxLBA = int(resultObj['P641_DMAEXT_TRANSFER_RATE'][0]['END_LBA'], 16) #CPC displaying in hex
                  objMsg.printMsg('%s Read(OD)(%d) TxRate=%d MB/s TxHead=%d LastLBA=%s' % (TestName, i, TxRate, TxHead, TxLBA))

                  if TxRate >= ODTxRate:
                     objMsg.printMsg('%s Read(OD) passed. TxRate=%d MB/s' % (TestName, TxRate))
                  else:
                     objMsg.printMsg('%s Read(OD) TxRate(%d MB/s) < %d, Test failed!' % (TestName, TxRate, ODTxRate))
                     result = FAIL
                     break


               # write ID
               if result == OK:
                  #data = ICmd.WriteDMAExtTransRate(IDStartLBA, blockSize, sectCnt)
                  WritePrm['STARTING_LBA'] = lbaTuple(IDStartLBA)
                  stat = ICmd.St(WritePrm)
                  resultObj = self.dut.objSeq.SuprsDblObject.copy()
                  data = ICmd.translateStReturnToCPC(stat)
                  result = data['LLRET']

               if result != OK:
                  objMsg.printMsg('%s Write(ID)(%d) failed. Result=%s Data=%s' % (TestName, i, result, data))
                  break
               else:
                  TxRate = int(resultObj['P641_DMAEXT_TRANSFER_RATE'][0]['XFER_RATE_MB_PER_SEC'])
                  TxHead = int(data['DEV'])
                  #RT120112: change due to CPC intrinsic removal
                  if (self.oRF.CellType.find('CPC') < 0) or ((self.oRF.CellType.find('CPC') >= 0) and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION): #SIC
                     TxLBA = int(resultObj['P641_DMAEXT_TRANSFER_RATE'][0]['END_LBA'])
                  else: #non-intrinsic CPC
                     TxLBA = int(resultObj['P641_DMAEXT_TRANSFER_RATE'][0]['END_LBA'], 16) #CPC displaying in hex
                  objMsg.printMsg('%s Write(ID)(%d) TxRate=%d MB/s TxHead=%d LastLBA=%s' % (TestName, i, TxRate, TxHead, TxLBA))

                  if TxRate >= IDTxRate:
                     objMsg.printMsg('%s Write(ID) passed. TxRate=%d MB/s' % (TestName, TxRate))
                  else:
                     objMsg.printMsg('%s Write(ID) TxRate(%d MB/s) < %d, Test failed!' % (TestName, TxRate, IDTxRate))
                     result = FAIL
                     break

               self.MSSTR_dblog(i, IDStartLBA, blockSize, TxRate, readIDRate)

               # write OD
               if result == OK:
                  #data = ICmd.WriteDMAExtTransRate(ODStartLBA, blockSize, sectCnt)
                  WritePrm['STARTING_LBA'] = lbaTuple(ODStartLBA)
                  stat = ICmd.St(WritePrm)
                  resultObj = self.dut.objSeq.SuprsDblObject.copy()
                  data = ICmd.translateStReturnToCPC(stat)
                  result = data['LLRET']

               if result != OK:
                  objMsg.printMsg('%s Write(OD)(%d) failed. Result=%s Data=%s' % (TestName, i, result, data))
                  break
               else:
                  TxRate = int(resultObj['P641_DMAEXT_TRANSFER_RATE'][0]['XFER_RATE_MB_PER_SEC'])
                  TxHead = int(data['DEV'])
                  #RT120112: change due to CPC intrinsic removal
                  if (self.oRF.CellType.find('CPC') < 0) or ((self.oRF.CellType.find('CPC') >= 0) and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION): #SIC
                     TxLBA = int(resultObj['P641_DMAEXT_TRANSFER_RATE'][0]['END_LBA'])
                  else: #non-intrinsic CPC
                     TxLBA = int(resultObj['P641_DMAEXT_TRANSFER_RATE'][0]['END_LBA'], 16) #CPC displaying in hex
                  objMsg.printMsg('%s Write(OD)(%d) TxRate=%d MB/s TxHead=%d LastLBA=%s' % (TestName, i, TxRate, TxHead, TxLBA))

                  if TxRate >= ODTxRate:
                     objMsg.printMsg('%s Write(OD) passed. TxRate=%d MB/s' % (TestName, TxRate))
                  else:
                     objMsg.printMsg('%s Write(OD) TxRate(%d MB/s) < %d, Test failed!' % (TestName, TxRate, ODTxRate))
                     result = FAIL
                     break

               self.MSSTR_dblog(i, ODStartLBA, blockSize, TxRate, readODRate)

            try:   
               objMsg.printDblogBin(self.dut.dblData.Tables('P_SUSTAINED_TRANSFER_RATE'))
            except: 
               pass

            #if result != OK:
            #   raise gioTestException(data)
            #if result == OK:
               #ICmd.FlushCache()
               #time.sleep(3)
               #ICmd.StandbyImmed()
            #else:
               #self.GetSerialPortData()
               #raise gioTestException(data)


         #EndTime(TestName, 'funcstart', 'funcfinish', 'functotal')

      #return result
      return result, data, TestName, IDStartLBA, ODStartLBA, blockSize, sectCnt

 #-----------------------------------------------------------------------------------------#
   def doSTMIdle(self):
      D_Msg = ON
      T_Msg = ON
      result = OK
      TestType = ('IDT')
      TestName = ('STM IDLE')
      self.testName = ('%s %s' % (TestType, TestName))       # Test Name for file formatting
      self.printTestName(self.testName)

      minLBA = 0
      maxLBA = self.maxLBA
      sectCnt = 256
      rndCnt = 10
      STM_IDLE = ON
      STMIdleLoop = 3

      ICmd.SetIntfTimeout(10000)

      #if ConfigVars[CN].has_key('STM IDLE') and ConfigVars[CN]['STM IDLE'] != UNDEF and ConfigVars[CN]['STM IDLE'] == 'ON':
      #   STM_IDLE = ON
      #else:
      #   STM_IDLE = OFF

      if STM_IDLE == ON:
         if ConfigVars[CN].has_key('STM IDLE LOOPCNT') and ConfigVars[CN]['STM IDLE LOOPCNT'] != UNDEF:
            STMIdleLoop = ConfigVars[CN].get('STM IDLE LOOPCNT', STMIdleLoop)


         self.testCmdTime = 0
         self.printTestName(self.testName)

         #ICmd.ReceiveSerialCtrl(1)

         for i in range(STMIdleLoop):
            # DT090709 More preventive measures for aborted write
            ICmd.FlushCache()
            ICmd.IdleImmediate()
            time.sleep(3)
            objMsg.printMsg('FlushCache, IdleImmediate and sleep 3 sec')

            # DT110110
            #objMsg.printMsg('PowerOnOptions =%s ' % ConfigVars[CN]['Power On Options'])
            #DriveOff(3)  # power off and pause 3 sec

#            if driveattr['SF_SpinUp_Congen'] == 'ON':
#               SpinUpFlag = 0x0B
#               objMsg.printMsg('PowerOnTiming SpinUpFlag =%s ' % SpinUpFlag)
#               PowerOnTiming(30000, SpinUpFlag)

            #self.oRF.powerCycleVoltageTimer(3, 0, 4750, 12000)
            #RT010611: T510 issues DITS commands, unlock serial port on FDE drives
            #objPwrCtrl.powerCycle(4750,12000,3,0)
            self.oRF.powerCycleVoltageTimer(3, 0, 4750, 12000, 'TCGUnlock')

            ICmd.ClearBinBuff(WBF|RBF)
            #DriveOn(4750,12000) # power on with 4.75v and 12v

            # DT270709 Add Unlocking for Trusted Drive
#            if ConfigVars[CN].has_key('Kwai Unlock') and ConfigVars[CN]['Kwai Unlock'] != UNDEF and ConfigVars[CN]['Kwai Unlock'] == 'ON':
#               result = UnlockDrive()

            objMsg.printMsg('STMIdle Loop(%i) - Sleep 10min' % int(i+1))
            time.sleep(10*60)    # sleep for 10min
            ICmd.ClearBinBuff(RBF)

            if result == OK:
               #RT050911: don't use ACCESS_MODE to specify mode
               RandomRead = {
                  'test_num'   : 510,
                  'prm_name'   : "RandomWriteDMAExt",
                  'spc_id'     : 1,
                  'timeout' : 252000,
                  'STARTING_LBA' : lbaTuple(100),
                  'MAXIMUM_LBA' : lbaTuple(maxLBA - 256),
                  'TOTAL_BLKS_TO_XFR64': lbaTuple(rndCnt*sectCnt),
                  'BLKS_PER_XFR' : sectCnt,
                  'CTRL_WORD1':0x0011,
                  'CTRL_WORD2':0x0,
               }
               #stat = ICmd.RandomReadDMAExt(100, maxLBA - 256, sectCnt, sectCnt, rndCnt)   # random read 10x
               stat = ICmd.St(RandomRead)
               data = ICmd.translateStReturnToCPC(stat)
               result = data['LLRET']
               objMsg.printMsg('RandomRead 10 times, Data=%s Result=%d' % (data, result))

            if result != OK:
               objMsg.printMsg('RandomRead failed, STMIdle loop aborted.')
               break

         if result == OK:
            # DT090709 More preventive measures for aborted write
            ICmd.FlushCache()
            ICmd.IdleImmediate()
            time.sleep(3)
            objMsg.printMsg('FlushCache, IdleImmediate and Sleep 3 sec')
            #objPwrCtrl.powerCycle()
            self.oRF.powerCycle()
            #DriveOff()
            #objMsg.printMsg('Drive power off!')
            objMsg.printMsg('STM_Idle check passed! Result=%s' % result)
            #DriveOn()

         else:
            objMsg.printMsg('STM_Idle check failed! Data=%s, Result=%s' % (data, result))
            raise gioTestException(data)

         #EndTime(TestName, 'funcstart', 'funcfinish', 'functotal')


      return result

   #---------------------------------------------------------------------------------------------------------#
   def doSerialSDODCheck(self):
      D_Msg = ON
      T_Msg = ON
      data = {}
      result = FAIL
      TestType = ('IDT')
      TestName = ('SDOD CHECK')
      self.testName = ('%s %s' % (TestType, TestName))                       # Test Name for file formatting
      SERIAL_SDOD = OFF
      retry = OFF

      timeout = 60
      ICmd.SetIntfTimeout(10000)

      if ConfigVars[CN].has_key('SDOD Spin Check') and ConfigVars[CN]['SDOD Spin Check'] != UNDEF and ConfigVars[CN]['SDOD Spin Check'] == 'ON':
         SERIAL_SDOD = ON
      else:
         SERIAL_SDOD = OFF

      if SERIAL_SDOD == ON:
         self.testCmdTime = 0
         self.printTestName(self.testName)
         #ICmd.ReceiveSerialCtrl(1)

         if testSwitch.IO_MQM_SIC_TESTTIME_OPTIMIZATION:
            self.oRF.powerCycle('TCGUnlock', driveOnly=1)
         else:
            self.oRF.powerCycle('TCGUnlock')
         self.oRF.disableAPM(self.testName)

         sptCmds.enableDiags()

         for i in range(2):
            objMsg.printMsg('%s Initiating Serial SDOD, Attempt = %s' % (TestName, i+1))
            try:
               #data = ICmd.Ctrl('Z', matchStr='T>')
               data = sptCmds.execOnlineCmd(CTRL_Z, timeout = timeout, waitLoops = 100)
               #objMsg.printMsg('%s Ctrl Z Data=%s' % (TestName, data))

               #data = ICmd.SerialCommand('/2\r', matchStr='F3 2>')
               sptCmds.gotoLevel('2')

               #RT070711: spindown the drive first

               #data = ICmd.SerialCommand('Z\r', matchStr='F3 2>')
               data = sptCmds.sendDiagCmd("Z\r",timeout = timeout, printResult = True, loopSleepTime=0)
               #objMsg.printMsg('%s SerialCmd Z(Spindown) Data=%s' % (TestName, data))

               #data = ICmd.SerialCommand('U3\r', matchStr='F3 2>')
               data = sptCmds.sendDiagCmd("U3\r",timeout = timeout, printResult = True, loopSleepTime=0)
               #objMsg.printMsg('%s SerialCmd U3(Spinup) Data=%s' % (TestName, data))

               #data = ICmd.SerialCommand('Z\r', matchStr='F3 2>')
               data = sptCmds.sendDiagCmd("Z\r",timeout = timeout, printResult = True, loopSleepTime=0)
               #objMsg.printMsg('%s SerialCmd Z(Spindown) Data=%s' % (TestName, data))
            except Exception, e:
               objMsg.printMsg("Serial Port Exception data : %s"%e)
               objMsg.printMsg('%s Serial SDOD Check failed attempt %d' % (TestName, i+1))
            else:
               result = OK
               objMsg.printMsg('%s Serial SDOD Check Passed' % TestName)
               break

         # end retry loop
         if result != OK:
            objMsg.printMsg('%s Serial SDOD Check Failed' % TestName)
            raise gioTestException(data)

         #EndTime(TestName, 'funcstart', 'funcfinish', 'functotal')

      return result
   #---------------------------------------------------------------------------------------------------------#
   def calculateTimeout(self, num_blocks, step_lba):
      timeout = num_blocks * step_lba #(assuming 1 sec timeout per LBA)

      return timeout

#---------------------------------------------------------------------------------------------------------#
   def getUDMASpeed(self, xferKey):
      if xferKey == 0x45: UDMASpeed = 100
      elif xferKey == 0x44: UDMASpeed = 66
      else: UDMASpeed = 33
      return UDMASpeed

#---------------------------------------------------------------------------------------------------------#
   def printTestName(self, testName, setTestStep='ON'):
      objMsg.printMsg('')
      objMsg.printMsg('')
      objMsg.printMsg('*'*50)
      objMsg.printMsg(testName)
      objMsg.printMsg('*'*50)
      if setTestStep == 'ON':
         # initialize test parameter
         self.stepStartTime = time.time()
         self.testCmdTime = 0
         self.udmaSpeed = 0x45
         self.pattern = 0x00
         self.currentStep = testName

   #---------------------------------------------------------------------------------------------------------#
   def updateFailureAttr(self):
      if self.oRF.DrvAttr.has_key('MQM_FAIL_SEQ'):
         self.currentStep = self.oRF.DrvAttr['MQM_FAIL_SEQ']
      if self.oRF.DrvAttr.has_key('MQM_FAIL_LBA'):
         self.failLBA = self.oRF.DrvAttr['MQM_FAIL_LBA']
      if self.oRF.DrvAttr.has_key('MQM_FAIL_CODE'):
         self.failCode = self.oRF.DrvAttr['MQM_FAIL_CODE']
      if self.oRF.DrvAttr.has_key('MQM_FAIL_LLRET'):
         self.failLLRET = self.oRF.DrvAttr['MQM_FAIL_LLRET']
      if self.oRF.DrvAttr.has_key('MQM_FAIL_STATUS'):
         self.failStatus = self.oRF.DrvAttr['MQM_FAIL_STATUS']

   #---------------------------------------------------------------------------------------------------------#
   def displayCmdTimes(self, testName='GIO IOPS', testType='CPC', stepTimeSec=0, xferLength=256):
      if testType == 'DST_Short':
         stepCmdCount = 10000
      elif testType == 'DST':
         stepCmdCount = self.oRF.IDAttr['MaxLBA']/xferLength
      else:
         ICCdata = ICmd.InterfaceCmdCount(reset=0)
         stepCmdCount = int(ICCdata['CNT'])

      self.testCmdCount += stepCmdCount
      self.testTimeSec += stepTimeSec

      if stepTimeSec == 0:
         objMsg.printMsg('%s Test Step Command Time = 0, No IOPS Calculated' % self.testName)
         return -1

      objMsg.printMsg('---------------------------- GIO Command IOPS -------------------------------')
      if self.testName != 'OVERALL':
         objMsg.printMsg('%s GIO Step Total - Transfer Length = %d' % (self.testName, xferLength))
         objMsg.printMsg('%s GIO Step Total - Step Command Time = %.3f' % (self.testName, stepTimeSec))
         objMsg.printMsg('%s GIO Step Total - Step Command Count = %d' % (self.testName, stepCmdCount))
         objMsg.printMsg('%s GIO Step Total - Step Commands per Second = %.3f' % \
                        (self.testName, stepCmdCount / stepTimeSec))
         objMsg.printMsg('-----------------------------------------------------------------------------')

      objMsg.printMsg('%s GIO Test Total - Test Command Time = %.3f' % (self.testName, self.testTimeSec))
      objMsg.printMsg('%s GIO Test Total - Test Command Count = %d' % (self.testName, self.testCmdCount))
      objMsg.printMsg('%s GIO Test Total - Test Commands per Second = %.3f' % \
                     (self.testName, self.testCmdCount / self.testTimeSec))
      objMsg.printMsg('-----------------------------------------------------------------------------')

      return OK

#---------------------------------------------------------------------------------------------------------#
   def checkRetryTest(self, failure, status, error):
      retry = OFF
      objMsg.printMsg('---------------------------- Check Retry Test -------------------------------')
      objMsg.printMsg('Failure=%s Status=%s Error=%s' % (failure, status, error))
      objMsg.printMsg('Retry for AAU_TIMEOUT')
      objMsg.printMsg('Retry for ATA_NOTREADY')
      objMsg.printMsg('Retry for Status 81/0x51 and Error 132/0x84')
      if failure == 'AAU_TIMEOUT:AAU timeout' or \
         failure == 'ATA_NOTREADY:Not ready to check status' or \
         (status == '81' and error == '132'):                 # string-81=0x51 string-132=0x84
         objMsg.printMsg('Retry ON - Do Script CPC Level Retry')
         retry = ON
      else:
         objMsg.printMsg('Retry OFF - Retry Criteria Not Matched, No Script CPC Level Retry')
      objMsg.printMsg('-----------------------------------------------------------------------------')

      return retry

#---------------------------------------------------------------------------------------------------------#
   def GIOCleanup(self):
      #DT160408 - release of heater to allow temp control for other tray
      ReleaseTheHeater()
      ReleaseTheFans()
      objMsg.printMsg('Drive Failed - Release heater/fan control for other slot')
      objMsg.printMsg('Cell Temperature=%s ' % (ReportTemperature() / 10))

      # DT041109 Assign holddrive to restartflag
      # DT141210
      #ReportRestartFlags({'holdDrive':1})
      # DT090709 More preventive measures for aborted write
      ICmd.FlushCache()
      ICmd.IdleImmediate()
      time.sleep(3)
      objMsg.printMsg('FlushCache, IdleImmediate and sleep 3 sec')
      DriveOff()

   #---------------------------------------------------------------------------------------------------------#
   def getSerialPortData(self):

      # DT120911 Change timeout to 60 as measurement is in ms
      #timeout = 60000
      timeout = 60
      self.TestName = 'Get Serial Port Data'
      self.oRF.printTestName(self.TestName)

      # DT270510
      #self.oRF.powerCycle('TCGUnlock')
      #RT050511: change unlocking sequence to cater for both FDE and TCG
      #if self.oRF.UnlockDiag == 'ON':
      #   ReliUnlockDiagUDE()
      if self.oRF.UnlockDiag == 'ON':
         objMsg.printMsg('>>>>> TCG Unlocking Diag!' )
         ReliUnlockDiagUDE()
      if self.oRF.UnlockFDE == 'ON':
         objMsg.printMsg('>>>>> FDE Unlocking Diag!')
         from KwaiPrep import CKwaiPrepTest
         oKwaiPrep = CKwaiPrepTest(objDut)
         result = oKwaiPrep.UnlockSerialPort()
         objMsg.printMsg("FDE SerialPort Unlock result=%s" % result)
      #RT291111: add exception handling so that the codes below can still continue in event of failure
      try:
         if self.oRF.CellType.find('CPC') >= 0:
            ICmd.SetSerialTimeout(60000)  
      except:
         pass

      # DT280711 Remove as enableDiags has implicit disable APM
      #self.oRF.disableAPM(self.TestName)

      objMsg.printMsg('[Serial Port Data]')

      objMsg.printMsg('*****************************************************************************')
      # DT280711 Add retry to handle drive hang
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
               # Powercycle with unlocking and no pre-power sequence
               # DT120911 Remove the extra pre-power cycle
               #self.oRF.powerCycle('TCGUnlock', 'NO')
               #self.oRF.powerCycle('TCGUnlock')
               #RT130911: SI/N2 powercycle without prepower sequence
               self.oRF.powerCycle('TCGUnlock', 0)
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
#         objMsg.printMsg('Servo Flaw List :')
#         data = sptCmds.sendDiagCmd("V8",timeout = timeout, printResult = True, loopSleepTime=0)
#         objMsg.printMsg('Primary Servo Flaw List :')
#         data = sptCmds.sendDiagCmd("V10",timeout = timeout, printResult = True, loopSleepTime=0)
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
      self.oRF.checkSmartLogs([0xA1, 0xA8, 0xA9], OFF)
      # Display Smart Attr
      self.oRF.checkSmartAttr(OFF)

      self.oRF.printTestName('Get Serial Port Data End')

#---------------------------------------------------------------------------------------------------------#
#RT 22072010 Inherit CGIOTest_CPC from CGIOTest to use parent defined functions

# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/CGIOTest.py#1 $


class CGIOTest_CPC(CGIOTest):
   def __init__(self, dut, params=[]):
      objMsg.printMsg('GIO for CPC Test Begin')
      CGIOTest.__init__(self, dut, params=[], isCPC=1)

   ##################################################################
   # These methods are used by both Intrinsic-CPC and nonIntrinsic-PC
   # 1) doVoltageHighLow
   # 2) RampTemp
   # 3) WriteRead
   # 4) endTestStep
   # 5) postPowerCycleSequence
   # 6) displayPerformance
   # 7) getServoData
   ###################################################################

   def doVoltageHighLow(self, TestType='IDT', loops=2):
      D_Msg = OFF
      ready_time = 0
      #RT150711: initialize data
      data = {}
      result = OK
      TestName = ('Volts High Low')                       # Test Name for file formatting
      self.testName = ('%s %s' % (TestType,TestName))
      self.printTestName(self.testName)

      # Setup Parameters
      nominal_5v   = 5000
      nominal_12v  = 12000
      margin_5v    = prm_GIOSettings['IDT 5vMargin']            # -1(off), 0.0(no margin)
      margin_12v   = prm_GIOSettings['IDT 12vMargin']           # 0.10(10%), 0.05(5%)

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
      if D_Msg: objMsg.printMsg('%s Voltage Nom  Margin - 5v = %2.2f - 12v = %2.2f' % (self.testName,f_nom_5v,f_nom_12v))
      if D_Msg: objMsg.printMsg('%s Voltage High Margin - 5v = %2.2f - 12v = %2.2f' % (self.testName,f_high_5v,f_high_12v))
      if D_Msg: objMsg.printMsg('%s Voltage Low  Margin - 5v = %2.2f - 12v = %2.2f' % (self.testName,f_low_5v,f_low_12v))

      name = {
      "test1" :(('%s - %2.2f - %2.2f' % (self.testName,f_nom_5v,f_nom_12v)),  'IDT Volt N_N'),
      "test2" :(('%s - %2.2f - %2.2f' % (self.testName,f_low_5v,f_low_12v)),  'IDT Volt L_L'),
      "test3" :(('%s - %2.2f - %2.2f' % (self.testName,f_high_5v,f_high_12v)), 'IDT Volt H_H') }

      test = {}
      test['1_5']  = nominal_5v;  test['1_12']  = nominal_12v
      test['2_5']  = low_5v;      test['2_12']  = low_12v
      test['3_5']  = high_5v;     test['3_12']  = high_12v

      for testname in range(1,(len(name)+1)):        #for 3 types of volt range
         for loop in range(1,loops+1):                  #powercycle for each type of volt range
            volts5   = ('%d_5'  % testname)   # volt5  = 1_5 to 10_5
            volts12  = ('%d_12' % testname)   # volt12 = 1_12 to 10_12
            name_key = ('test%d' % testname)  # test1 to test10
            self.volts5 = test[volts5]; self.volts12 = test[volts12]
            #objMsg.printMsg('-------------------- Volts - 5.00 - 12.00 - Loop No. 3 ----------------------')
            #objMsg.printMsg('---------------------- Volts Setting 1 - Loop No. 3 -------------------------')
            #objMsg.printMsg('-------------------- Volts - %2.2f - %2.2f - Loop No. %d ----------------------' % \
            #               (self.volts5/1000.0,self.volts12/1000.0,loop))
            objMsg.printMsg('---------------------- Volts Setting %d - Loop No. %d -------------------------' % (testname,loop))
            objMsg.printMsg(name[name_key][0])
            # DT120511 Bug fix
            objMsg.printMsg(name[name_key][1])
            #self.oRF.powerCycle()
            self.oRF.powerCycleVoltageTimer(v5=self.volts5,v12=self.volts12)
            self.postPowerCycleSequence()
            if result == OK:
               result = self.WriteRead(Msg=OFF)
            if result != OK: break
         if result != OK: break

      #self.displayCmdTimes(self.testName,'CPC',self.testCmdTime,self.sectorCount)

      if result != OK:
         objMsg.printMsg('%s Failed' % self.testName)
         # DT120511 Set Test Name
         self.testName = name[name_key][1]
         raise gioTestException(data)
      else:
         objMsg.printMsg('%s Test Passed' % self.testName)

      return result

   #---------------------------------------------------------------------------------------------------------#
   def RampTemp(self, temp, Wait=ON, MaxH=600, UpRate=40, DownRate=10):

      if self.IDT_RAMP_TEMP == ON:
         #CheckSlotType()
         SetTemperatureLimits(MaxH, UpRate, DownRate)
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


   #         if ConfigVars.has_key('DDCell Max Temp Diff') and ConfigVars['DDCell Max Temp Diff'] > 0:
   #            objMsg.printMsg('Releasing Heater Control')
   #            ReleaseTheHeater()

         try:    ReleaseTheFans()  # Release Fan control
         except: pass

      else:
         objMsg.printMsg('Ramp To Temperature OFF')
      return 0

   #---------------------------------------------------------------------------------------------------------#
   def WriteRead(self, Msg=ON):
      D_Msg = ON
      result = OK
      sec_count  = 1
      addr_tags  = 1
      comp_data  = 1
      buf_offset = 0
      byte_count = 8
      no_data    = ''
      inc_data   = 'INC'
      dec_data   = 'DEC'
      wr_pattern = 'NONE'
      rd_pattern = 'NONE'
      seq_lba = 0

      ICmd.ClearBinBuff(1); ICmd.ClearBinBuff(2)
      IntfClass.CIdentifyDevice()
      if D_Msg: objMsg.printMsg('Write/Read LBA=%d SecCount=%d AddrTags=%d CompData=%d' % \
                               (seq_lba, sec_count, addr_tags, comp_data))
      if D_Msg:
         try: objMsg.printMsg(ICmd.GetSerialBuffer())
         except: pass
      # Stamp LBA, stamp the entire write buffer
      #ICmd.FillBuffStamp(1,seq_lba,0,256)
      # DT060510 replace
      # Write Sectors
      #data = ICmd.WriteSectors(seq_lba,sec_count)
      data = ICmd.WriteSectorsExt(seq_lba,sec_count)
      result = data['LLRET']
      if D_Msg:
         try: objMsg.printMsg(ICmd.GetSerialBuffer())
         except: pass
      if D_Msg:
         wr_pattern = ICmd.GetBuffer(1,buf_offset,byte_count)['DATA']
         objMsg.printMsg('WriteRead WriteSectorsLBA lba=%d write=%s result=%d' % (seq_lba,wr_pattern,result))
      ICmd.FlushCache()
      if result ==  OK:
         # DT060510 replace
         # Read Sectors
         #data = ICmd.ReadSectors(seq_lba,sec_count)
         data = ICmd.ReadSectorsExt(seq_lba,sec_count)
         result  = data['LLRET']
      if (self.oRF.CellType.find('CPC') < 0) or ((self.oRF.CellType.find('CPC') >= 0) and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION): #Only check this for intrinsic CPC

         if result == OK and data['RESULT'].find('EK_OK') != -1:
         # Compare Buffers
            data = ICmd.CompareBuffers(0,sec_count*512)
            if data['RESULT'].find('EK_OK') == -1:
               result = FAIL
            if D_Msg:
               rd_pattern = ICmd.GetBuffer(2,buf_offset,byte_count)['DATA']
               objMsg.printMsg('WriteRead ReadSectorsLBA lba=%d read=%s result=%d' % (seq_lba,rd_pattern,result))

      if result != OK:
         objMsg.printMsg('WriteRead WriteSectorsLBA lba=%d write=%s result=%d' % (seq_lba,wr_pattern,result))
         objMsg.printMsg('WriteRead ReadSectorsLBA lba=%d read=%s result=%d' % (seq_lba,rd_pattern,result))
         objMsg.printMsg('WriteRead LBAs Failed lba=%d Result=%s' % (seq_lba,data['RESULT']))
         objMsg.printMsg('WriteRead LBAs Failed lba=%d data=%s' % (seq_lba,data))
         if comp_data == 1 and data.has_key('COMPAREBUFFERS') == 1:
            objMsg.printMsg('WriteRead LBAs Failed Compare = %s' % (data['COMPAREBUFFERS']['RESULT']))
      else:
         if Msg: objMsg.printMsg('WriteRead LBAs Passed lba=%d' % seq_lba)

      return result

   #---------------------------------------------------------------------------------------------------------#
   def endTestStep(self, testName, setTestStep='ON'):
      objMsg.printMsg('')
      objMsg.printMsg('')
      objMsg.printMsg('*'*50)
      objMsg.printMsg(testName)
      objMsg.printMsg('*'*50)
      if setTestStep == 'ON':
         # initialize test parameter
         self.testCmdTime = 0
         self.udmaSpeed = 0x45
         self.pattern = 0x00
         self.currentStep = testName

      return 0

   #---------------------------------------------------------------------------------------------------------#
   def postPowerCycleSequence(self):

      # Disable APM
#      objMsg.printMsg("%s Disable APM" % self.testName)
#      self.oRF.disableAPM(self.testName)

      # Set RW Status
#      objMsg.printMsg("%s Set RW Status to ON" % self.testName)
#      self.oRF.setRdWrStatsIDE(self.testName, 'On')
#
      # Set Interface Timeout
      objMsg.printMsg("%s Set Interface Timeout to %d ms" % (self.testName, prm_GIOSettings["IDT IntfTimeout"]))
      data = ICmd.SetIntfTimeout(prm_GIOSettings["IDT IntfTimeout"])
      objMsg.printMsg('data: %s'%data) #PN
      #if data['LLRET'] != OK: #PN: SetInftTimeout doesnot return 
      #   objMsg.printMsg("%s Set Intface Timeout Failed - data = %s" % (self.testName, str(data)))
      #   raise gioTestException(data)

      # Receive Serial Ctrl
      #ICmd.ReceiveSerialCtrl(1)

      return OK

   #---------------------------------------------------------------------------------------------------------#
   def displayPerformance(self, testName, numCmds, blocksXfrd, blockSize, cmdTime):
      totalBlock    = (cmdTime / blocksXfrd * 1000000)
      totalKBytes   = (blocksXfrd * (blockSize / cmdTime) / 1000)
      totalMBytes   = (totalKBytes / 1000)
      objMsg.printMsg('---------------------------- Wrt/Rd Performance  ----------------------------')
      objMsg.printMsg('%s Num Cmds           = %d' % (self.testName, numCmds))
      objMsg.printMsg('%s Blocks Xfrd        = %d' % (self.testName, blocksXfrd))
      objMsg.printMsg('%s Block Size         = %d' % (self.testName, blockSize))
      objMsg.printMsg('%s Total Time(sec)    = %f' % (self.testName, cmdTime))
      objMsg.printMsg('%s Total Block(us)    = %f' % (self.testName, totalBlock))
      objMsg.printMsg('%s Total MBytes/Sec   = %f' % (self.testName, totalMBytes))
      objMsg.printMsg('%s Total KBytes/Sec   = %f' % (self.testName, totalKBytes))
      objMsg.printMsg('-----------------------------------------------------------------------------')

      return 0

   #---------------------------------------------------------------------------------------------------------#
   def getServoData(self):
      self.TestName = 'Get Servo Data'
      self.oRF.printTestName(self.TestName)

#      data = ICmd.SetFeatures(0x85)
#      self.Status = data['LLRET']
#      if self.Status == OK:
#         objMsg.printMsg('SetFeature(0x85) Disable APM passed, data=%s' % (str(data)))
#      else:
#         objMsg.printMsg('SetFeature(0x85) Disable APM failed, data=%s' % (str(data)))
#
#      ICmd.ClearSerialBuffer()
#
#      if self.Status == OK:
#         data = ICmd.Ctrl('Z', matchStr='T>')
#         self.Status = data['LLRET']
#         objMsg.printMsg('CtrlZ Data=%s' % str(data))
#
      # PES Collection
#      if self.Status == OK:
#         data = ICmd.SerialCommand('/3\r', matchStr='3>')
#         self.Status = data['LLRET']
#         objMsg.printMsg('/3 Cmd Data=%s' % str(data))
#
#      if self.Status == OK:
#         data = ICmd.SerialCommand('f0,20\r', matchStr='3>')       # servo trace - 20
#         self.Status = data['LLRET']
#         objMsg.printMsg('/3 Cmd Data=%s' % str(data))
#         serialBuffer = ICmd.GetBuffer(SBF, 0, 10240)['DATA']
#         objMsg.printMsg('Result=%s serialBuffer=%s' % (self.Status, str(serialBuffer)))

      ICmd.ClearSerialBuffer()
      # Plot PES
      data = ICmd.SerialCommand('/4\r', matchStr='4>')
      self.Status = data['LLRET']
      objMsg.printMsg('/4 Cmd Data=%s' % str(data))

      data = ICmd.SerialCommand('U100D\r', matchStr='4>')
      self.Status = data['LLRET']
      objMsg.printMsg('/4 Cmd Data=%s' % str(data))

      try: objMsg.printMsg('\n' + ICmd.GetBuffer(4, 0, 102400)['DATA'] + '\n')
      except: objMsg.printMsg("Serial Buffer is Empty")

   #---------------------------------------------------------------------------------------------------------#

   #######################################################
   #
   # The following methods are used by Intrinsic-CPC ONLY
   #
   #######################################################
   if testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION == 0:
      def doWriteReadPerform(self, TestType='IDT', SectCnt=256, Count=2700, Step=65000, Reverse=0):
         P_Msg = ON      # Performance Message
         F_Msg = ON      # Failure Message
         B_Msg = OFF     # Buffer Message
         data = {}
         result = OK
         DoRetry = ON
         self.testCmdTime = 0
         self.testName = ('%s Wrt Rd Perform' % TestType)                       # Test Name for file formatting
         self.printTestName(self.testName)

         self.oRF.powerCycle()

         # Setup Parameters
         self.udmaSpeed = 0x45
         self.pattern = '0000'#'1111'
         if TestType == 'MQM':
            self.pattern = 0x00
         IDMaxLBA = self.oRF.IDAttr['MaxLBA']
         ID1=(IDMaxLBA - 2000000)
         MD1=(IDMaxLBA / 2)
         if Reverse == 1:
            OD1=2000000
         else:
            OD1=0
         self.sectorCount = SectCnt
         self.numBlocks = 12*Count/self.sectorCount
         self.timeout = self.calculateTimeout(self.numBlocks,self.sectorCount)

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
               data = ICmd.WeakWrite(LocationsALL, self.sectorCount, self.udmaSpeed, self.pattern, timeout=self.timeout, exc=0)
               self.testCmdTime += float(data.get('CT','0'))/1000
               result = data['LLRET']

               if result == OK:
                  objMsg.printMsg("%s CPCWeakWrite Passed - Data: %s" % (self.testName, data))
                  break
               else:
                  objMsg.printMsg("%s CPCWeakWrite Failed - Data: %s" % (self.testName, data))
               if DoRetry == ON:
                  RetryTest = self.checkRetryTest(data['RESULT'], data.get('STS','NIL'), data.get('ERR','NIL'))
                  if RetryTest != ON: break
                  objMsg.printMsg('CPCWeakWrite - Loop Number %d of %d Failed - Do Retry' % (loop+1, Retry+1))
                  objMsg.printMsg('CPCWeakWrite - Retry - Power Cycle and Re-issue CPC Embedded Command')
                  self.getSerialPortData()
                  self.oRF.powerCycle()
                  self.postPowerCycleSequence()
               else: break
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

         self.blocksXfrd = 12*Count
         self.numCmds = self.blocksXfrd / self.sectorCount
         self.displayPerformance(self.testName,self.numCmds,self.blocksXfrd,self.blockSize,self.testCmdTime)
         self.displayCmdTimes(self.testName,'CPC',self.testCmdTime,self.sectorCount)

         if result != OK:
            objMsg.printMsg('%s Failed Result=%s Data=%s' % (self.testName, result, data))
            raise gioTestException(data)
         else:
            objMsg.printMsg('%s Test Passed' % self.testName)

            #EndTime(self.testName, 'funcstart', 'funcfinish', 'functotal')


            #if result == OK and IDT_RESULT_FILE_DATA == ON:
            #   TestTime = timetostring(testtime['functotal'])
            #   CollectData(result, TestType, TestNum, self.testName, TestTime)
            #objMsg.printMsg('*****************************************************************************')

         return result, data

      #---------------------------------------------------------------------------------------------------------#
      def doSystemFileLoad(self, TestType='IDT', SysMinLBA=0, SysMaxLBA=3906, DiagMinLBA=64298, DiagMaxLBA=203716, SectCnt=16, RandCount=5000):
         P_Msg = ON      # Performance Message
         F_Msg = ON      # Failure Message
         B_Msg = ON      # Buffer Message
         data = {}
         result = OK
         self.testCmdTime = 0
         self.testName = ('%s Sys File Load' % TestType)       # Test Name for file formatting
         self.printTestName(self.testName)

         self.oRF.powerCycle()
         # Setup Parameters
         UDMA_Speed = 0x45
         self.udmaSpeed = UDMA_Speed
         Delay = 70*100
         MinSectCount = 1
         SectPerBlock = 1
         Pattern1 = '2222'
         Pattern2 = '3333'
         self.sectorCount = SectCnt
         self.numBlocks = (DiagMaxLBA-DiagMinLBA)/self.sectorCount
         self.timeout = self.calculateTimeout(self.numBlocks,self.sectorCount)
         if TestType == 'MQM':
            Pattern1 = 0x00
            Pattern2 = 0x00
         objMsg.printMsg('%s SYS Start LBA=%d/0x%X End LBA=%d/0x%X SectCnt=%d Pattern1=%s RandCount=%d UDMA_Speed=0x%X' % \
                        (self.testName,SysMinLBA,SysMinLBA,SysMaxLBA,SysMaxLBA,SectCnt,Pattern1,RandCount,UDMA_Speed))
         objMsg.printMsg('%s DIAG Start LBA=%d/0x%X End LBA=%d/0x%X SectCnt=%d Pattern2=%s SectPerBlock=%d Delay=%d Sec' % \
                        (self.testName,DiagMinLBA,DiagMinLBA,DiagMaxLBA,DiagMaxLBA,SectCnt,Pattern2,SectPerBlock,(Delay/100)))

         self.pattern = Pattern1
         data = ICmd.SystemTrackWriteSim(SysMinLBA, SectCnt, SectPerBlock, Pattern1, timeout=self.timeout, exc=0)
         self.testCmdTime += float(data.get('CT','0'))/1000
         result = data['LLRET']
         if result != OK:
            objMsg.printMsg("%s SystemTrackWriteSim Failed - Data: %s" % (self.testName,data))
         else:
            objMsg.printMsg("%s SystemTrackWriteSim Passed - Data: %s" % (self.testName,data))
            self.pattern = Pattern2
            data = ICmd.LoadTestFileSim(DiagMinLBA,DiagMaxLBA,SectCnt,SysMinLBA,SysMaxLBA,SectCnt, \
                                        SysMinLBA,SysMaxLBA,SectCnt,RandCount,DiagMinLBA,DiagMaxLBA, \
                                        MinSectCount,Pattern2,UDMA_Speed,Delay, timeout=self.timeout, exc=0)
            self.testCmdTime += float(data.get('CT','0'))/1000
            result = data['LLRET']
            if result != OK:
               objMsg.printMsg("%s LoadTestFileSim Failed - Data: %s" % (self.testName,data))
            else:
               objMsg.printMsg("%s LoadTestFileSim Passed - Data: %s" % (self.testName,data))

         #self.blocksXfrd = 12*Count
         #self.numCmds = self.blocksXfrd / self.sectorCount
         #self.displayPerformance(self.testName,numCmds,blocksXfrd,blockSize,self.testCmdTime)
         self.displayCmdTimes(self.testName,'CPC',self.testCmdTime,self.sectorCount)

         if result != OK:
            objMsg.printMsg('%s Failed Result=%s Data=%s' % (self.testName, result, data))

            raise gioTestException(data)
         else:
            objMsg.printMsg('%s Test Passed' % self.testName)

         return result

      #---------------------------------------------------------------------------------------------------------#
      def doWriteTestMobile(self, TestType='IDT', StartLBA=64, MidLBA=1000000, EndLBA=4194303, SectCnt=63, Loops=5000):
         D_Msg = OFF     # Debug Message
         B_Msg = ON      # Buffer Message
         F_Msg = ON      # Failure Message
         data = {}
         result = OK
         DoRetry = ON
         TestName = ('Write Mobile')                       # Test Name for file formatting
         self.testName = ('%s %s' % (TestType,TestName))
         self.printTestName(self.testName)

         # To add TD auto-detection and turn off this test for TD
         #if ConfigVars.has_key('Kwai Unlock') and ConfigVars['Kwai Unlock'] == 'ON':
         #   WRITE_TEST_MOBILE = OFF


         self.oRF.powerCycle()

         # DT220310
         MultiSPB = self.oRF.IDAttr['MultLogSect']
         # Setup Parameters
         MinLBA  = 0
         Pattern = '0000'#'EEEE'
         if TestType == 'MQM':
            Pattern = 0x00
         self.pattern = Pattern
         self.sectorCount = SectCnt
         self.numBlocks = EndLBA/SectCnt+4*Loops
         self.timeout = self.calculateTimeout(self.numBlocks,self.sectorCount)
         objMsg.printMsg('%s Start LBA=%d/0x%X Mid LBA=%d/0x%X End LBA=%d/0x%X SecCnt=%d Loops=%d Pattern=%s MultiSPB=%s ' % \
                        (self.testName,StartLBA,StartLBA,MidLBA,MidLBA,EndLBA,EndLBA,SectCnt,Loops,Pattern,MultiSPB))

         Retry = 2
         for loop in range(Retry+1):
            # DT230310 Remove the timeout
            #data = ICmd.WriteTestSim2(StartLBA,MidLBA,EndLBA,MinLBA,SectCnt,Loops,Pattern,timeout=self.timeout,exc=0)
            data = ICmd.WriteTestSim2(StartLBA,MidLBA,EndLBA,MinLBA,SectCnt,Loops,Pattern,MultiSPB)
            self.testCmdTime += float(data.get('CT','0'))/1000
            result = data['LLRET']
            if result == OK:
               objMsg.printMsg("%s WriteTestSim2 Passed - Data: %s" % (self.testName, data))
               break
            else:
               objMsg.printMsg("%s WriteTestSim2 Failed - Data: %s" % (self.testName, data))
            if DoRetry == ON:
               RetryTest = self.checkRetryTest(data['RESULT'], data.get('STS','NIL'), data.get('ERR','NIL'))
               if RetryTest != ON: break
               objMsg.printMsg('WriteTestSim2 - Loop Number %d of %d Failed - Do Retry' % (loop+1, Retry+1))
               objMsg.printMsg('WriteTestSim2 - Retry - Power Cycle and Re-issue CPC Embedded Command')
               self.getSerialPortData()
               self.oRF.powerCycle()
               self.postPowerCycleSequence()
            else: break

         #self.blocksXfrd = 12*Count
         #self.numCmds = self.blocksXfrd / self.sectorCount
         #self.displayPerformance(self.testName,numCmds,blocksXfrd,blockSize,self.testCmdTime)
         self.displayCmdTimes(self.testName,'CPC',self.testCmdTime,self.sectorCount)

         if result != OK:
            objMsg.printMsg('%s Failed Result=%s Data=%s' % (self.testName, result, data))

            raise gioTestException(data)
         else:
            objMsg.printMsg('%s Test Passed' % self.testName)

         return result,data

      #---------------------------------------------------------------------------------------------------------#
      def doImageFileCopy(self, TestType='IDT', FAT_Min=10000, FAT_Max=14999, FAT_SectCnt=1, Data_Min=1000000, Data_Max=1080000, Data_SectCnt=16):
         D_Msg = OFF     # Debug Message
         B_Msg = ON      # Buffer Message
         F_Msg = ON      # Failure Message
         data = {}
         result = OK
         DoRetry = ON
         TestName = ('Image FileCopy')                       # Test Name for file formatting
         self.testName = ('%s %s' % (TestType,TestName))
         self.printTestName(self.testName)


         self.oRF.powerCycle()

         # Setup Parameters
         UDMA_Speed = 0x45
         self.udmaSpeed = UDMA_Speed
         Pattern1 = '0000'#'00FF'
         Pattern2 = '0000'#'6666'
         if TestType == 'MQM':
            Pattern1 = 0x00
            Pattern2 = 0x00
         if Data_Max == ('MaxLBA'):
            Data_Max = self.maxLBA

         self.pattern = Pattern1+' OR '+Pattern2
         self.sectorCount = FAT_SectCnt
         self.numBlocks = (FAT_Max-FAT_Min)/FAT_SectCnt*2
         self.timeout = self.calculateTimeout(self.numBlocks,self.sectorCount)
         objMsg.printMsg('%s FAT Min=%d/0x%X   FAT Max=%d/0x%X   FAT Sector Count=%d UDMA_Speed=0x%X Pattern1=%s' % \
                        (self.testName,FAT_Min,FAT_Min,FAT_Max,FAT_Max,FAT_SectCnt,UDMA_Speed,Pattern1))
         objMsg.printMsg('%s Data Min=%d/0x%X  Data Max=%d/0x%X  Data Sector Count=%d UDMA_Speed=0x%X Pattern2=%s' % \
                        (self.testName,Data_Min,Data_Min,Data_Max,Data_Max,Data_SectCnt,UDMA_Speed,Pattern2))

         Retry = 2
         for loop in range(Retry+1):
            data = ICmd.FileCopySim1(FAT_Min,FAT_Max,FAT_SectCnt,Data_Min,UDMA_Speed,Pattern1,Pattern2,timeout=self.timeout,exc=0)
            self.testCmdTime += float(data.get('CT','0'))/1000
            result = data['LLRET']
            if result == OK:
               objMsg.printMsg("%s FileCopySim1 Passed - Data: %s" % (self.testName, data))
               break
            else:
               objMsg.printMsg("%s FileCopySim1 Failed - Data: %s" % (self.testName, data))
            if DoRetry == ON:
               RetryTest = self.checkRetryTest(data['RESULT'], data.get('STS','NIL'), data.get('ERR','NIL'))
               if RetryTest != ON: break
               objMsg.printMsg('FileCopySim1 - Loop Number %d of %d Failed - Do Retry' % (loop+1, Retry+1))
               objMsg.printMsg('FileCopySim1 - Retry - Power Cycle and Re-issue CPC Embedded Command')
               self.getSerialPortData()
               self.oRF.powerCycle()
               self.postPowerCycleSequence()
            else: break

         #self.blocksXfrd = 12*Count
         #self.numCmds = self.blocksXfrd / self.sectorCount
         #self.displayPerformance(self.testName,numCmds,blocksXfrd,blockSize,self.testCmdTime)
         self.displayCmdTimes(self.testName,'CPC',self.testCmdTime,self.sectorCount)

         if result != OK:
            objMsg.printMsg('%s Failed Result=%s Data=%s' % (self.testName, result, data))

            raise gioTestException(data)
         else:
            objMsg.printMsg('%s Test Passed' % self.testName)

         return result,data

      #---------------------------------------------------------------------------------------------------------#
      def doImageFileRead(self, TestType='IDT', FAT_Min=10000, FAT_Max=14999, FAT_SectCnt=256, Data_Min=1000000, Data_Max=1080000, Data_SectCnt=256):
         P_Msg = ON      # Performance Message
         F_Msg = ON      # Failure Message
         B_Msg = ON      # Buffer Message
         data = {}
         result = OK
         DoRetry = ON
         TestName = ('Image FileRead')                       # Test Name for file formatting
         self.testName = ('%s %s' % (TestType,TestName))
         self.printTestName(self.testName)


         self.oRF.powerCycle()
         # Setup Parameters
         UDMA_Speed = 0x45
         self.udmaSpeed = UDMA_Speed
         Pattern1 = '0000'#'00FF'
         Pattern2 = '0000'#'6666'
         if TestType == 'MQM':
            Pattern1 = 0x00
            Pattern2 = 0x00
         if Data_Max == ('MaxLBA'):
            Data_Max = self.maxLBA

         self.pattern = Pattern1+' OR '+Pattern2
         self.sectorCount = FAT_SectCnt
         self.numBlocks = (FAT_Max-FAT_Min)/FAT_SectCnt*2
         self.timeout = self.calculateTimeout(self.numBlocks,self.sectorCount)
         objMsg.printMsg('%s FAT Min=%d/0x%X   FAT Max=%d/0x%X   FAT Sector Count=%d UDMA_Speed=0x%X Pattern1=%s' % \
                        (self.testName,FAT_Min,FAT_Min,FAT_Max,FAT_Max,FAT_SectCnt,UDMA_Speed,Pattern1))
         objMsg.printMsg('%s Data Min=%d/0x%X  Data Max=%d/0x%X  Data Sector Count=%d UDMA_Speed=0x%X Pattern2=%s' % \
                        (self.testName,Data_Min,Data_Min,Data_Max,Data_Max,Data_SectCnt,UDMA_Speed,Pattern2))

         Retry = 2
         for loop in range(Retry+1):
            data = ICmd.FileCopySim2(FAT_Min,FAT_Max,FAT_SectCnt,Data_Min,Data_Max,Data_SectCnt,UDMA_Speed,timeout=self.timeout,exc=0)
            self.testCmdTime += float(data.get('CT','0'))/1000
            result = data['LLRET']
            if result == OK:
               objMsg.printMsg("%s FileCopySim2 Passed - Data: %s" % (self.testName, data))
               break
            else:
               objMsg.printMsg("%s FileCopySim2 Failed - Data: %s" % (self.testName, data))
            if DoRetry == ON:
               RetryTest = self.checkRetryTest(data['RESULT'], data.get('STS','NIL'), data.get('ERR','NIL'))
               if RetryTest != ON: break
               objMsg.printMsg('FileCopySim2 - Loop Number %d of %d Failed - Do Retry' % (loop+1, Retry+1))
               objMsg.printMsg('FileCopySim2 - Retry - Power Cycle and Re-issue CPC Embedded Command')
               self.getSerialPortData()
               self.oRF.powerCycle()
               self.postPowerCycleSequence()
            else: break

         #self.blocksXfrd = 12*Count
         #self.numCmds = self.blocksXfrd / self.sectorCount
         #self.displayPerformance(self.testName,numCmds,blocksXfrd,blockSize,self.testCmdTime)
         self.displayCmdTimes(self.testName,'CPC',self.testCmdTime,self.sectorCount)

         if result != OK:
            objMsg.printMsg('%s Failed Result=%s Data=%s' % (self.testName, result, data))

            raise gioTestException(data)
         else:
            objMsg.printMsg('%s Test Passed' % self.testName)

         return result,data

      #---------------------------------------------------------------------------------------------------------#
      def doReadTestMobile(self, TestType='IDT', SeqStartLBA=64298, SeqEndLBA=203716, SeqSectCnt=16, RandRdCount=30, OuterLoops=24, InnerLoops=4):
         data = {}
         result = OK
         DoRetry = ON
         TestName = ('Read Mobile')                       # Test Name for file formatting
         self.testName = ('%s %s' % (TestType,TestName))
         self.printTestName(self.testName)

         self.oRF.powerCycle()
         # Setup Parameters
         UDMA_Speed = 0x45
         self.udmaSpeed = UDMA_Speed
         Pattern = '0000'#'8888'
         if TestType == 'MQM':
            Pattern = 0x00
         self.pattern = Pattern
         Delay = 30*100
         RandStartLBA = 0
         RandEndLBA = self.maxLBA
         self.sectorCount = SeqSectCnt
         self.numBlocks = (SeqEndLBA-SeqStartLBA)/SeqSectCnt
         self.timeout = self.calculateTimeout(self.numBlocks,self.sectorCount)
         objMsg.printMsg('%s SeqStart=%d/0x%X SeqEnd=%d/0x%X SeqSectCount=%d InnerLoops=%d OuterLoops=%d' % \
                        (self.testName,SeqStartLBA,SeqStartLBA,SeqEndLBA,SeqEndLBA,SeqSectCnt,InnerLoops,OuterLoops))
         objMsg.printMsg('%s RandStart=%d/0x%X RandEnd=%d/0x%X RandRdCount=%d UDMA_Speed=0x%X Pattern=%s Delay=%d' % \
                        (self.testName,RandStartLBA,RandStartLBA,RandEndLBA,RandEndLBA,RandRdCount,UDMA_Speed,Pattern,(Delay/100)))

         Retry = 2
         for loop in range(Retry+1):
            data = ICmd.ReadTestSim2(SeqStartLBA,SeqEndLBA,SeqSectCnt,RandStartLBA,RandEndLBA,RandRdCount, \
                                     InnerLoops,OuterLoops,UDMA_Speed,Pattern,Delay,timeout=self.timeout,exc=0)
            self.testCmdTime += float(data.get('CT','0'))/1000
            result = data['LLRET']
            if result == OK:
               objMsg.printMsg("%s ReadTestSim2 Passed - Data: %s" % (self.testName, data))
               break
            else:
               objMsg.printMsg("%s ReadTestSim2 Failed - Data: %s" % (self.testName, data))
            if DoRetry == ON:
               RetryTest = self.checkRetryTest(data['RESULT'], data.get('STS','NIL'), data.get('ERR','NIL'))
               if RetryTest != ON: break
               objMsg.printMsg('ReadTestSim2 - Loop Number %d of %d Failed - Do Retry' % (loop+1, Retry+1))
               objMsg.printMsg('ReadTestSim2 - Retry - Power Cycle and Re-issue CPC Embedded Command')
               self.getSerialPortData()
               self.oRF.powerCycle()
               self.postPowerCycleSequence()
            else: break

         if result == OK:
            objMsg.printMsg('%s ReadTestSim2 Test Passed - Call Write/Read' % self.testName)
            result = self.WriteRead(Msg=ON)

         self.displayCmdTimes(self.testName,'CPC',self.testCmdTime,self.sectorCount)

         if result != OK:
            objMsg.printMsg('%s Failed Result=%s Data=%s' % (self.testName, result, data))
            raise gioTestException(data)
         else:
            objMsg.printMsg('%s Test Passed' % self.testName)

         return result , data

      #---------------------------------------------------------------------------------------------------------#
      def doReadTestDrive(self, TestType='IDT', SeqStartLBA=64298, SeqEndLBA=203716, SeqSectCnt=16, Loops=3000, RandRdCount=30):
         data = {}
         result = OK
         DoRetry = ON
         TestName = ('Read Drive')                       # Test Name for file formatting
         self.testName = ('%s %s' % (TestType,TestName))
         self.printTestName(self.testName)


         self.oRF.powerCycle()
         # Setup Parameters
         UDMA_Speed = 0x45
         self.udmaSpeed = UDMA_Speed
         Pattern = '0000'#'7777'
         if TestType == 'MQM':
            Pattern = 0x00
         self.pattern = Pattern
         RandStartLBA = 0
         RandEndLBA = self.maxLBA
         self.sectorCount = SeqSectCnt
         self.numBlocks = (SeqEndLBA-SeqStartLBA)/SeqSectCnt
         self.timeout = self.calculateTimeout(self.numBlocks,self.sectorCount)
         objMsg.printMsg('%s SeqStart=%d/0x%X SeqEnd=%d/0x%X SeqSectCount=%d Pattern=%s Loops=%d' % \
                        (self.testName,SeqStartLBA,SeqStartLBA,SeqEndLBA,SeqEndLBA,SeqSectCnt,Pattern,Loops))
         objMsg.printMsg('%s RandStart=%d/0x%X RandEnd=%d/0x%X RandRdCount=%d UDMA_Speed=0x%X' % \
                        (self.testName,RandStartLBA,RandStartLBA,RandEndLBA,RandEndLBA,RandRdCount,UDMA_Speed))

         Retry = 2
         for loop in range(Retry+1):
            data = ICmd.ReadTestSim(SeqStartLBA,SeqEndLBA,SeqSectCnt,SeqSectCnt,RandStartLBA,RandEndLBA,\
                                    Loops,RandRdCount,UDMA_Speed,Pattern,timeout=self.timeout,exc=0)
            self.testCmdTime += float(data.get('CT','0'))/1000
            result = data['LLRET']
            if result == OK:
               objMsg.printMsg("%s ReadTestSim Passed - Data: %s" % (self.testName, data))
               break
            else:
               objMsg.printMsg("%s ReadTestSim Failed - Data: %s" % (self.testName, data))
            if DoRetry == ON:
               RetryTest = self.checkRetryTest(data['RESULT'], data.get('STS','NIL'), data.get('ERR','NIL'))
               if RetryTest != ON: break
               objMsg.printMsg('ReadTestSim - Loop Number %d of %d Failed - Do Retry' % (loop+1, Retry+1))
               objMsg.printMsg('ReadTestSim - Retry - Power Cycle and Re-issue CPC Embedded Command')
               self.getSerialPortData()
               self.oRF.powerCycle()
               self.postPowerCycleSequence()
            else: break
         self.displayCmdTimes(self.testName,'CPC',self.testCmdTime,self.sectorCount)

         if result != OK:
            objMsg.printMsg('%s Failed Result=%s Data=%s' % (self.testName, result, data))

            raise gioTestException(data)
         else:
            objMsg.printMsg('%s Test Passed' % self.testName)

         return result, data

      #---------------------------------------------------------------------------------------------------------#
      def doLowDutyCycle(self, TestType='IDT', StartLBA=10000, MidLBA=14999, EndLBA=1000000, Loops=100, SectCnt=2, Delay=0.5):
         D_Msg = OFF     # Debug Message
         F_Msg = ON      # Failure Message
         B_Msg = ON      # Buffer Message
         data = {}
         result = OK
         DoRetry = ON
         TestName = ('Low Duty Cycle')                       # Test Name for file formatting
         self.testName = ('%s %s' % (TestType,TestName))
         self.printTestName(self.testName)

         self.oRF.powerCycle()
         # Setup Parameters
         UDMA_Speed = 0x45
         self.udmaSpeed = UDMA_Speed
         Pattern = '0000'#'9999'
         if TestType == 'MQM':
            Pattern = 0x00
         self.pattern = Pattern
         self.sectorCount = SectCnt
         self.numBlocks = (EndLBA-StartLBA)/SectCnt*Loops
         self.timeout = self.calculateTimeout(self.numBlocks,self.sectorCount)
         objMsg.printMsg('%s StartLBA=%d/0x%X MidLBA=%d/0x%X EndLBA=%d/0x%X' % \
                        (self.testName, StartLBA, StartLBA, MidLBA, MidLBA, EndLBA, EndLBA))
         objMsg.printMsg('%s Loops=%d SectCnt=%d UDMA_Speed=0x%X Pattern=%s Delay=%1.1f' % \
                        (self.testName, Loops, SectCnt, UDMA_Speed, Pattern, Delay))
         result = ICmd.SetFeatures(0x02)['LLRET']
         if result != OK:
            objMsg.printMsg('%s Failed SetFeatures - Enable Write Cache' % (self.testName))
         else:
            objMsg.printMsg('%s Passed SetFeatures - Enable Write Cache' % (self.testName))

         Retry = 2
         for loop in range(Retry+1):
            data = ICmd.LowDutyRead(StartLBA,EndLBA,StartLBA,StartLBA,EndLBA,SectCnt,Loops,UDMA_Speed,\
                                    Pattern,(Delay*1000),timeout=self.timeout,exc=0)
            self.testCmdTime += float(data.get('CT','0'))/1000
            result = data['LLRET']
            if result == OK:
               objMsg.printMsg("%s LowDutyRead Passed - Data: %s" % (self.testName, data))
               break
            else:
               objMsg.printMsg("%s LowDutyRead Failed - Data: %s" % (self.testName, data))
            if DoRetry == ON:
               RetryTest = self.checkRetryTest(data['RESULT'], data.get('STS','NIL'), data.get('ERR','NIL'))
               if RetryTest != ON: break
               objMsg.printMsg('LowDutyRead - Loop Number %d of %d Failed - Do Retry' % (loop+1, Retry+1))
               objMsg.printMsg('LowDutyRead - Retry - Power Cycle and Re-issue CPC Embedded Command')
               self.getSerialPortData()
               self.oRF.powerCycle()
               self.postPowerCycleSequence()
            else: break
         self.displayCmdTimes(self.testName,'CPC',self.testCmdTime,self.sectorCount)

         if result != OK:
            objMsg.printMsg('%s Failed Result=%s Data=%s' % (self.testName, result, data))

            raise gioTestException(data)
         else:
            objMsg.printMsg('%s Test Passed' % self.testName)

         return result, data

      #---------------------------------------------------------------------------------------------------------#
      def doOSWriteDrive(self, TestType='IDT', SectCnt=16, Gbytes=5.0):
         data = {}
         result = OK
         DoRetry = ON
         TestName = ('OS Write Test')                       # Test Name for file formatting
         self.testName = ('%s %s' % (TestType,TestName))
         self.printTestName(self.testName)

         self.oRF.powerCycle()
         # Setup Parameters
         UDMA_Speed = 0x45
         self.udmaSpeed = UDMA_Speed
         Pattern = '0000'#'BBBB'
         if TestType == 'MQM':
            Pattern = 0x00
         self.pattern = Pattern
         StartLBA = 0
         EndLBA = StartLBA + ((Gbytes*1000000000) / 512)
         NumLBA = EndLBA - StartLBA
         self.sectorCount = SectCnt
         self.numBlocks = NumLBA/SectCnt
         self.timeout = self.calculateTimeout(self.numBlocks,self.sectorCount)
         objMsg.printMsg('%s Start LBA=%d End LBA=%d Sect Count=%d Num GBytes=%3.3f UDMA_Speed=0x%X Pattern=%s' % \
                        (self.testName, StartLBA, EndLBA, SectCnt, (NumLBA*512/1000000000), UDMA_Speed, Pattern))

         Retry = 2
         for loop in range(Retry+1):
            data = ICmd.OSCopySim1(StartLBA,EndLBA,SectCnt,UDMA_Speed,Pattern,timeout=self.timeout,exc=0)
            self.testCmdTime += float(data.get('CT','0'))/1000
            result = data['LLRET']
            if result == OK:
               objMsg.printMsg("%s OSCopySim1 Passed - Data: %s" % (self.testName, data))
               break
            else:
               objMsg.printMsg("%s OSCopySim1 Failed - Data: %s" % (self.testName, data))
            if DoRetry == ON:
               RetryTest = self.checkRetryTest(data['RESULT'], data.get('STS','NIL'), data.get('ERR','NIL'))
               if RetryTest != ON: break
               objMsg.printMsg('OSCopySim1 - Loop Number %d of %d Failed - Do Retry' % (loop+1, Retry+1))
               objMsg.printMsg('OSCopySim1 - Retry - Power Cycle and Re-issue CPC Embedded Command')
               self.getSerialPortData()
               self.oRF.powerCycle()
               self.postPowerCycleSequence()
            else: break
         self.displayCmdTimes(self.testName,'CPC',self.testCmdTime,self.sectorCount)

         if result != OK:
            objMsg.printMsg('%s Failed Result=%s Data=%s' % (self.testName, result, data))

            raise gioTestException(data)
         else:
            objMsg.printMsg('%s Test Passed' % self.testName)

         return result, data

      #---------------------------------------------------------------------------------------------------------#
      def doOSReadDrive(self, TestType='IDT', SectCnt=64, Gbytes=5.0):
         data = {}
         result = OK
         DoRetry = ON
         TestName = ('OS Read Test')                       # Test Name for file formatting
         self.testName = ('%s %s' % (TestType,TestName))
         self.printTestName(self.testName)

         self.oRF.powerCycle()
         # Setup Parameters
         UDMA_Speed = 0x45
         self.udmaSpeed = UDMA_Speed
         Pattern = '0000'#'AAAA'
         if TestType == 'MQM':
            Pattern = 0x00
         self.pattern = Pattern
         StartLBA = 0
         EndLBA = StartLBA + ((Gbytes*1000000000) / 512)
         NumLBA = EndLBA - StartLBA
         self.sectorCount = SectCnt
         self.numBlocks = NumLBA/SectCnt
         self.timeout = self.calculateTimeout(self.numBlocks,self.sectorCount)
         objMsg.printMsg('%s Start LBA=%d End LBA=%d Sect Count=%d Num GBytes=%3.3f UDMA_Speed=0x%X Pattern=%s' % \
                        (self.testName, StartLBA, EndLBA, SectCnt, (NumLBA*512/1000000000), UDMA_Speed, Pattern))

         Retry = 2
         for loop in range(Retry+1):
            data = ICmd.OSCopySim2(StartLBA,EndLBA,SectCnt,UDMA_Speed,timeout=self.timeout,exc=0)
            self.testCmdTime += float(data.get('CT','0'))/1000
            result = data['LLRET']
            if result == OK:
               objMsg.printMsg("%s OSCopySim2 Passed - Data: %s" % (self.testName, data))
               break
            else:
               objMsg.printMsg("%s OSCopySim2 Failed - Data: %s" % (self.testName, data))
            if DoRetry == ON:
               RetryTest = self.checkRetryTest(data['RESULT'], data.get('STS','NIL'), data.get('ERR','NIL'))
               if RetryTest != ON: break
               objMsg.printMsg('OSCopySim2 - Loop Number %d of %d Failed - Do Retry' % (loop+1, Retry+1))
               objMsg.printMsg('OSCopySim2 - Retry - Power Cycle and Re-issue CPC Embedded Command')
               self.getSerialPortData()
               self.oRF.powerCycle()
               self.postPowerCycleSequence()
            else: break
         self.displayCmdTimes(self.testName,'CPC',self.testCmdTime,self.sectorCount)

         if result != OK:
            objMsg.printMsg('%s Failed Result=%s Data=%s' % (self.testName, result, data))

            raise gioTestException(data)
         else:
            objMsg.printMsg('%s Test Passed' % self.testName)

         return result, data

      #---------------------------------------------------------------------------------------------------------#
      def doOSReadReverse(self, TestType='IDT', SectCnt=64, Gbytes=5.0):
         data = {}
         result = OK
         DoRetry = ON
         TestName = ('OS Read Rev')                       # Test Name for file formatting
         self.testName = ('%s %s' % (TestType,TestName))
         self.printTestName(self.testName)


         self.oRF.powerCycle()
         # Setup Parameters
         UDMA_Speed = 0x45
         self.udmaSpeed = UDMA_Speed
         Pattern = '0000'#'AAAA'
         if TestType == 'MQM':
            Pattern = 0x00
         self.pattern = Pattern
         StartLBA = 0
         EndLBA = StartLBA + ((Gbytes*1000000000) / 512)
         NumLBA = EndLBA - StartLBA
         self.sectorCount = SectCnt
         self.numBlocks = NumLBA/SectCnt
         self.timeout = self.calculateTimeout(self.numBlocks,self.sectorCount)
         objMsg.printMsg('%s Start LBA=%d End LBA=%d Sect Count=%d Num GBytes=%3.3f UDMA_Speed=0x%X Pattern=%s' % \
                        (self.testName, StartLBA, EndLBA, SectCnt, (NumLBA*512/1000000000), UDMA_Speed, Pattern))
         result = ICmd.SetFeatures(0x02)['LLRET']
         if result != OK:
            objMsg.printMsg('%s Failed SetFeatures - Enable Write Cache' % (self.testName))
         else:
            objMsg.printMsg('%s Passed SetFeatures - Enable Write Cache' % (self.testName))

         Retry = 2
         for loop in range(Retry+1):
            data = ICmd.OSCopySim3(StartLBA,EndLBA,SectCnt,UDMA_Speed,timeout=self.timeout,exc=0)
            self.testCmdTime += float(data.get('CT','0'))/1000
            result = data['LLRET']
            if result == OK:
               objMsg.printMsg("%s OSCopySim3 Passed - Data: %s" % (self.testName, data))
               break
            else:
               objMsg.printMsg("%s OSCopySim3 Failed - Data: %s" % (self.testName, data))
            if DoRetry == ON:
               RetryTest = self.checkRetryTest(data['RESULT'], data.get('STS','NIL'), data.get('ERR','NIL'))
               if RetryTest != ON: break
               objMsg.printMsg('OSCopySim3 - Loop Number %d of %d Failed - Do Retry' % (loop+1, Retry+1))
               objMsg.printMsg('OSCopySim3 - Retry - Power Cycle and Re-issue CPC Embedded Command')
               self.getSerialPortData()
               self.oRF.powerCycle()
               self.postPowerCycleSequence()
            else: break
         self.displayCmdTimes(self.testName,'CPC',self.testCmdTime,self.sectorCount)

         if result != OK:
            objMsg.printMsg('%s Failed Result=%s Data=%s' % (self.testName, result, data))

            raise gioTestException(data)
         else:
            objMsg.printMsg('%s Test Passed' % self.testName)

         return result, data

      #---------------------------------------------------------------------------------------------------------#
      def doWritePattern(self, TestType='IDT', Pattern=0x00, StartLBA=0, EndLBA=10000000):
         P_Msg = ON      # Performance Message
         F_Msg = ON      # Failure Message
         B_Msg = ON      # Buffer Message
         data = {}
         result = OK
         TestName = ('Write Pattern')                       # Test Name for file formatting
         self.testName = ('%s %s' % (TestType,TestName))
         self.printTestName(self.testName)


         self.oRF.powerCycle()
         # Setup Parameters
         UDMA_Speed = 0x45
         StepLBA = 256
         SectCount = 256
         BlockSize = 512
         StampFlag = 0
         if EndLBA == ('MaxLBA'):
            EndLBA = self.oRF.IDAttr['MaxLBA']
         self.udmaSpeed = UDMA_Speed
         self.pattern = Pattern
         self.sectorCount = SectCount
         self.numBlocks = (EndLBA-StartLBA)/SectCount
         self.timeout = self.calculateTimeout(self.numBlocks,self.sectorCount)
         objMsg.printMsg('%s Start LBA=%d End LBA=%d Sect Count=%d Pattern=0x%X' % \
                        (self.testName, StartLBA, EndLBA, SectCount, Pattern))

         objMsg.printMsg('%s Flush Cache, Clear Buffers, Fill 0x%2X Data' % (self.testName, Pattern))
         ICmd.FlushCache(); ICmd.ClearBinBuff(1); ICmd.ClearBinBuff(2)
         ICmd.FillBuffByte(1, Pattern)
         if B_Msg:
            objMsg.printMsg('%s Write Buffer Data ----------------------------------------' % self.testName)
            wb_data = ICmd.GetBuffer(1, 0, 550)['DATA']
            objMsg.printMsg('%s %s' % (self.testName, wb_data[0:20]))
            objMsg.printMsg('%s %s' % (self.testName, wb_data[512:532]))

         result = ICmd.SetFeatures(0x03, UDMA_Speed)['LLRET']
         if result != OK:
            objMsg.printMsg('%s Failed SetFeatures - Transfer Rate = UDMA-%d' % (self.testName, self.getUDMASpeed(UDMA_Speed)))
         else:
            objMsg.printMsg('%s Passed SetFeatures - Transfer Rate = UDMA-%d' % (self.testName, self.getUDMASpeed(UDMA_Speed)))
         result = ICmd.SetFeatures(0x02)['LLRET']
         if result != OK:
            objMsg.printMsg('%s Failed SetFeatures - Enable Write Cache' % (self.testName))
         else:
            objMsg.printMsg('%s Passed SetFeatures - Enable Write Cache' % (self.testName))

            CmdStartTime = time.time()
            if self.oRF.IDAttr['Support48Bit'] == 'ON':
               data = ICmd.SequentialWriteDMAExt(StartLBA, EndLBA, StepLBA, SectCount, StampFlag,timeout=self.timeout,exc=0)
            else:
               data = ICmd.SequentialWriteDMA(StartLBA, EndLBA, StepLBA, SectCount, StampFlag,timeout=self.timeout,exc=0)
            CmdEndTime = time.time()
            self.testCmdTime = CmdEndTime-CmdStartTime
            result = data['LLRET']
            if result == OK:
               # DT270510
               self.getSerialPortData()
               objMsg.printMsg("%s SequentialWriteDMA Passed - Data: %s" % (self.testName, data))
            else:
               objMsg.printMsg("%s SequentialWriteDMA Failed - Data: %s" % (self.testName, data))

         self.displayCmdTimes(self.testName,'CPC',self.testCmdTime,self.sectorCount)
         if result == OK:
            if P_Msg:
               NumCmds=(EndLBA/SectCount); BlocksXfrd=EndLBA; CmdTime=(CmdEndTime-CmdStartTime)
               self.displayPerformance(TestName,NumCmds,BlocksXfrd,BlockSize,CmdTime)
            objMsg.printMsg('%s Test Passed' % self.testName)
         else:
            objMsg.printMsg('%s Failed Result=%s Data=%s' % (self.testName, result, data))

            raise gioTestException(data)

         return result,data

      #---------------------------------------------------------------------------------------------------------#
      #RT300311: Sync up with Gen2.2b3
      #def doReadPattForward(self, TestType='IDT', Pattern=0xCC, Location='OD', NumLBA=1000000, SectCnt=256):
      def doReadPattForward(self, TestType='IDT', Pattern=0x00, Location='OD', NumLBA=10000000, SectCnt=256, Compare=1):
         P_Msg = ON      # Performance Message
         F_Msg = ON      # Failure Message
         B_Msg = ON      # Buffer Message
         data = {}
         result = OK
         TestName = ('Read Pattern')                       # Test Name for file formatting
         self.testName = ('%s %s' % (TestType,TestName))
         self.printTestName(self.testName)


         self.oRF.powerCycle()
         # Setup Parameters
         UDMA_Speed = 0x45
         StepLBA = SectCnt
         BlockSize = 512
         StampFlag = 0
         CompFlag = 0
         if Compare:
            CompFlag = 1
         IDMaxLBA = self.oRF.IDAttr['MaxLBA']
         if Location == 'ID':
            StartLBA = (IDMaxLBA - NumLBA)
         elif Location == 'MD':
            StartLBA = ((IDMaxLBA/2) - NumLBA)
         else: # 'OD'
            StartLBA = 0
         EndLBA = StartLBA + NumLBA
         self.udmaSpeed = UDMA_Speed
         self.pattern = Pattern
         self.sectorCount = SectCnt
         self.numBlocks = NumLBA/SectCnt
         self.timeout = self.calculateTimeout(self.numBlocks,self.sectorCount)
         objMsg.printMsg('%s Start LBA=%d End LBA=%d Sect Count=%d Num LBAs=%d' % \
                        (self.testName, StartLBA, EndLBA, SectCnt, NumLBA))

         objMsg.printMsg('%s Flush Cache, Clear Buffers, Fill 0x%2X Data' % (self.testName, Pattern))
         ICmd.FlushCache(); ICmd.ClearBinBuff(1); ICmd.ClearBinBuff(2)
         ICmd.FillBuffByte(1, Pattern)
         if B_Msg:
            objMsg.printMsg('%s Write Buffer Data ----------------------------------------' % self.testName)
            wb_data = ICmd.GetBuffer(1, 0, 550)['DATA']
            objMsg.printMsg('%s %s' % (self.testName, wb_data[0:20]))
            objMsg.printMsg('%s %s' % (self.testName, wb_data[512:532]))

         result = ICmd.SetFeatures(0x03,UDMA_Speed)['LLRET']
         if result != OK:
            objMsg.printMsg('%s Failed SetFeatures - Transfer Rate = UDMA-%d' % (self.testName, self.getUDMASpeed(UDMA_Speed)))
         else:
            objMsg.printMsg('%s Passed SetFeatures - Transfer Rate = UDMA-%d' % (self.testName, self.getUDMASpeed(UDMA_Speed)))

            CmdStartTime = time.time()
            if self.oRF.IDAttr['Support48Bit']== 'ON':
               data = ICmd.SequentialReadDMAExt(StartLBA, EndLBA, StepLBA, SectCnt, StampFlag, CompFlag,timeout=self.timeout,exc=0)
            else:
               data = ICmd.SequentialReadDMA(StartLBA, EndLBA, StepLBA, SectCnt, StampFlag, CompFlag,timeout=self.timeout,exc=0)
            CmdEndTime = time.time()
            self.testCmdTime = CmdEndTime-CmdStartTime
            result = data['LLRET']
            if result == OK:
               objMsg.printMsg("%s SequentialReadDMA Passed - Data: %s" % (self.testName, data))
            else:
               objMsg.printMsg("%s SequentialReadDMA Failed - Data: %s" % (self.testName, data))
            if B_Msg or result != OK:
               objMsg.printMsg('%s Read Buffer Data ----------------------------------------' % self.testName)
               rb_data = ICmd.GetBuffer(2, 0, 550)['DATA']
               objMsg.printMsg('%s %s' % (self.testName, rb_data[0:20]))
               objMsg.printMsg('%s %s' % (self.testName, rb_data[512:532]))

         self.displayCmdTimes(self.testName,'CPC',self.testCmdTime,self.sectorCount)
         if result == OK:
            if P_Msg:
               NumCmds=(NumLBA/SectCnt); BlocksXfrd=NumLBA; CmdTime=(CmdEndTime-CmdStartTime)
               self.displayPerformance(TestName,NumCmds,BlocksXfrd,BlockSize,CmdTime)
            objMsg.printMsg('%s Test Passed' % self.testName)
         else:
            objMsg.printMsg('%s Failed Result=%s Data=%s' % (self.testName, result, data))

            raise gioTestException(data)

         return result, data

      #---------------------------------------------------------------------------------------------------------#
      def doRandomWrite(self, TestType='IDT', NumWrites=250000):
         P_Msg = ON      # Performance Message
         F_Msg = ON      # Failure Message
         B_Msg = ON      # Buffer Message
         data = {}
         result = OK
         DoRetry = ON
         TestName = ('Random Write')                       # Test Name for file formatting
         self.testName = ('%s %s' % (TestType,TestName))
         self.printTestName(self.testName)


         self.oRF.powerCycle()
         # Setup Parameters
         UDMA_Speed = 0x45
         Min_LBA = 0
         Max_LBA = (self.oRF.IDAttr['MaxLBA'] - 256)
         Min_Sect_Cnt = 256
         Max_Sect_Cnt = 256
         BlockSize = 512

         self.udmaSpeed = UDMA_Speed
         self.pattern = '0000'#'RANDOM'
         self.sectorCount = Max_Sect_Cnt
         self.numBlocks = NumWrites
         self.timeout = self.calculateTimeout(self.numBlocks,self.sectorCount)
         objMsg.printMsg('%s Min LBA=%d Max LBA=%d Num Writes=%d' % \
                        (self.testName, Min_LBA, Max_LBA, NumWrites))

         objMsg.printMsg('%s Flush Cache, Clear Buffers, Fill Random Data' % self.testName)
         ICmd.FlushCache(); ICmd.ClearBinBuff(1); ICmd.ClearBinBuff(2)
         #if TestType != 'MQM': ICmd.FillBuffRandom(1)
         if B_Msg:
            objMsg.printMsg('%s Write Buffer Data ----------------------------------------' % self.testName)
            wb_data = ICmd.GetBuffer(1, 0, 550)['DATA']
            # DT250710 Remove for Truncated Log
            #objMsg.printMsg('%s %s' % (self.testName, wb_data[0:20]))
            #objMsg.printMsg('%s %s' % (self.testName, wb_data[512:532]))

         result = ICmd.SetFeatures(0x03,UDMA_Speed)['LLRET']
         if result != OK:
            objMsg.printMsg('%s Failed SetFeatures - Transfer Rate = UDMA-%d' % (self.testName, self.getUDMASpeed(UDMA_Speed)))
         else:
            objMsg.printMsg('%s Passed SetFeatures - Transfer Rate = UDMA-%d' % (self.testName, self.getUDMASpeed(UDMA_Speed)))
         result = ICmd.SetFeatures(0x02)['LLRET']
         if result != OK:
            objMsg.printMsg('%s Failed SetFeatures - Enable Write Cache' % (self.testName))
         else:
            objMsg.printMsg('%s Passed SetFeatures - Enable Write Cache' % (self.testName))

         Retry = 1
         for loop in range(Retry+1):
            #CmdStartTime = time.time()
            if self.oRF.IDAttr['Support48Bit'] == 'ON':
               data = ICmd.RandomWriteDMAExt(Min_LBA, Max_LBA, Min_Sect_Cnt, Max_Sect_Cnt, NumWrites,timeout=self.timeout,exc=0)
            else:
               data = ICmd.RandomWriteDMA(Min_LBA, Max_LBA, Min_Sect_Cnt, Max_Sect_Cnt, NumWrites,timeout=self.timeout,exc=0)
            #CmdEndTime = time.time()
            #self.testCmdTime = CmdEndTime-CmdStartTime
            self.testCmdTime += float(data.get('CT','0'))/1000
            result = data['LLRET']
            if result == OK:
               # DT270510
               self.getSerialPortData()
               objMsg.printMsg("%s RandomWriteDMA Passed - Data: %s" % (self.testName, data))
               break
            else:
               objMsg.printMsg("%s RandomWriteDMA Failed - Data: %s" % (self.testName, data))
            if DoRetry == ON:
               RetryTest = self.checkRetryTest(data['RESULT'], data.get('STS','NIL'), data.get('ERR','NIL'))
               if RetryTest != ON: break
               objMsg.printMsg('RandomWriteDMA - Loop Number %d of %d Failed - Do Retry' % (loop+1, Retry+1))
               objMsg.printMsg('RandomWriteDMA - Retry - Power Cycle and Re-issue CPC Embedded Command')
               self.getSerialPortData()
               self.oRF.powerCycle()
               self.postPowerCycleSequence()

         self.displayCmdTimes(self.testName,'CPC',self.testCmdTime,self.sectorCount)
         if result == OK:
            if P_Msg:
                  BlocksXfrd=NumWrites*self.sectorCount
                  self.displayPerformance(TestName,NumWrites,BlocksXfrd,BlockSize,self.testCmdTime)
            objMsg.printMsg('%s Test Passed' % self.testName)
         else:
            objMsg.printMsg('%s Failed Result=%s Data=%s' % (self.testName, result, data))

            raise gioTestException(data)

         return result, data

      #-----------------------------------------------------------------------------------------#
      # DT241110 Modified ATI
      #
      def doODTATI(self, TestType='IDT'):
         P_Msg = ON      # Performance Message
         F_Msg = ON      # Failure Message
         B_Msg = ON      # Buffer Message
         data = {}
         result = OK
         DoRetry = ON
         UDMA_Speed = 0x45

         TestName = ('ODT ATI Test')                       # Test Name for file formatting
   #      driveattr['testseq'] = TestName.replace(' ','_')
   #      driveattr['eventdate'] = time.time()
         self.testName = ('%s %s' % (TestType,TestName))
         self.printTestName(self.testName)

         self.oRF.powerCycle()
         self.postPowerCycleSequence()
         if result == OK:
            data = {}
            Pattern = 0x0000#0x1234
            #StepLBA = 256
            SectCount = 256
            StampFlag = 0
            CompareFlag = 0
            # DT151009 Reduce 10K write to 5K
            #CmdLoop = 10000
            CmdLoop = 2500 # loop 2x

            TestLoop = 50
            StartLBA = 0
            EndLBA = 400
            InterLoop = 2
            MaxLBA = self.oRF.IDAttr['MaxLBA']

            StepLBA = MaxLBA/400

            #if driveattr['NumLogSect'] > 1:
            #   MaxLBA = MaxLBA - (MaxLBA % driveattr['NumLogSect'])

            #StepLBA = (MaxLBA/3200) * 8
            BlockSize = 512
            CmdTime = 0

            objMsg.printMsg('%s Start LBA=%d End LBA=%d Sect Count=%d Pattern=0x%2X' % \
                           (TestName, StartLBA, EndLBA, SectCount, Pattern))

            objMsg.printMsg('%s Flush Cache, Clear Buffers, Fill 0x%2X Data' % (TestName, Pattern))
            data = ICmd.FlushCache()
            result = data['LLRET']
            objMsg.printMsg('%s Flush Cache. Result=%s' % (TestName, str(result)))
            if result != OK:
               return result
            ICmd.ClearBinBuff(WBF);  ICmd.ClearBinBuff(RBF)
            ICmd.FillBuffByte(WBF, Pattern)
            if B_Msg:
               objMsg.printMsg('%s Write Buffer Data ----------------------------------------' % TestName)
               wb_data = ICmd.GetBuffer(WBF, 0, 550)['DATA']
               objMsg.printMsg('%s %s' % (TestName, wb_data[0:20]))
               objMsg.printMsg('%s %s' % (TestName, wb_data[512:532]))

            result = ICmd.SetFeatures(0x03,UDMA_Speed)['LLRET']
            if result != OK:
               objMsg.printMsg('%s Failed SetFeatures - Transfer Rate = UDMA-%d' % (self.testName, self.getUDMASpeed(UDMA_Speed)))
            else:
               objMsg.printMsg('%s Passed SetFeatures - Transfer Rate = UDMA-%d' % (self.testName, self.getUDMASpeed(UDMA_Speed)))

            result = ICmd.SetFeatures(0x82)['LLRET']
            if result != OK:
               objMsg.printMsg('%s Failed SetFeatures - Disable Write Cache' % (TestName))
            else:
               objMsg.printMsg('%s Passed SetFeatures - Disable Write Cache' % (TestName))

            CmdStartTime = time.time()
            objMsg.printMsg('%s Write on first %d locations %d times' % (TestName, TestLoop, CmdLoop))

            # DT241110 Mod ATI
            for loop in range (0, TestLoop/2, 1):
               for cnt in range(InterLoop):
                  if result == OK:
                     StartLBA = loop * StepLBA
                     objMsg.printMsg('%d write on 400 LBA starting %d' % (CmdLoop, StartLBA))

                     # DT170709 Apply offset calculation
                     if self.oRF.IDAttr['NumLogSect'] > 1:
                        # Adjust for number of physical sector per logical sector
                        StartLBA = StartLBA - (StartLBA % self.oRF.IDAttr['NumLogSect'])
                        if self.oRF.IDAttr['OffSetLBA0'] > 0:
                           if StartLBA == 0:    # Avoid negative LBA range, proceed to next block
                              StartLBA = StartLBA + self.oRF.IDAttr['NumLogSect']
                           # Adjust for alignment of Log Block in Phy Block
                           StartLBA = StartLBA - self.oRF.IDAttr['OffSetLBA0']

                     EndLBA = StartLBA + 400

                  if result == OK:
                     objMsg.printMsg('%d write location(%d) adjusted from start=%d to end=%d, with offset=%d' % (CmdLoop, loop+1, StartLBA, EndLBA, self.oRF.IDAttr['OffSetLBA0']))

                     if self.oRF.IDAttr['Support48Bit'] == 'ON':
                        data = ICmd.SequentialCmdLoop(0x35,StartLBA,EndLBA,SectCount,SectCount,CmdLoop,1)
                     else:
                        data = ICmd.SequentialCmdLoop(0xCA,StartLBA,EndLBA,SectCount,SectCount,CmdLoop,1)

                     result = data['LLRET']
                     if result != OK:
                        objMsg.printMsg('SequentialCmdLoop failed at loop %d, result=%s' % (TestLoop,data))
                        break

                  if result == OK:
                     StartLBA = (loop+TestLoop/2) * StepLBA
                     objMsg.printMsg('%d write on 400 LBA starting %d' % (CmdLoop, StartLBA))

                     # DT170709 Apply offset calculation
                     if self.oRF.IDAttr['NumLogSect'] > 1:
                        # Adjust for number of physical sector per logical sector
                        StartLBA = StartLBA - (StartLBA % self.oRF.IDAttr['NumLogSect'])
                        if self.oRF.IDAttr['OffSetLBA0'] > 0:
                           if StartLBA == 0:    # Avoid negative LBA range, proceed to next block
                              StartLBA = StartLBA + self.oRF.IDAttr['NumLogSect']
                           # Adjust for alignment of Log Block in Phy Block
                           StartLBA = StartLBA - self.oRF.IDAttr['OffSetLBA0']

                     EndLBA = StartLBA + 400
                  if result == OK:
                     objMsg.printMsg('%d write location(%d) adjusted from start=%d to end=%d, with offset=%d' % (CmdLoop, loop+1, StartLBA, EndLBA, self.oRF.IDAttr['OffSetLBA0']))

                     if self.oRF.IDAttr['Support48Bit'] == 'ON':
                        data = ICmd.SequentialCmdLoop(0x35,StartLBA,EndLBA,SectCount,SectCount,CmdLoop,1)
                     else:
                        data = ICmd.SequentialCmdLoop(0xCA,StartLBA,EndLBA,SectCount,SectCount,CmdLoop,1)

                     result = data['LLRET']
                     if result != OK:
                        objMsg.printMsg('SequentialCmdLoop failed at loop %d, result=%s' % (TestLoop,data))
                        break

            # end for

            CmdEndTime = time.time()
            CmdTime += CmdEndTime-CmdStartTime

            if result == OK:
               result = ICmd.SetFeatures(0x02)['LLRET']
               if result != OK:
                  objMsg.printMsg('%s Failed SetFeatures - Enable Write Cache' % (TestName))
               else:
                  objMsg.printMsg('%s Passed SetFeatures - Enable Write Cache' % (TestName))
            if result == OK:
               Pattern = 0x00
               StartLBA = 0
               EndLBA = MaxLBA/8
               CompareFlag = 1
               objMsg.printMsg('%s Start LBA=%d End LBA=%d Sect Count=%d Pattern=0x%2X' % \
                              (TestName, StartLBA, EndLBA, SectCount, Pattern))
               objMsg.printMsg('%s Flush Cache, Clear Buffers, Fill 0x%2X Data' % (TestName, Pattern))
               result = ICmd.FlushCache()['LLRET']
               if result != OK:
                  return result
               ICmd.ClearBinBuff(WBF);  ICmd.ClearBinBuff(RBF)
               ICmd.FillBuffByte(WBF, Pattern)
               if B_Msg:
                  objMsg.printMsg('%s Write Buffer Data ----------------------------------------' % TestName)
                  wb_data = ICmd.GetBuffer(WBF, 0, 550)['DATA']
                  objMsg.printMsg('%s %s' % (TestName, wb_data[0:20]))
                  objMsg.printMsg('%s %s' % (TestName, wb_data[512:532]))

               CmdStartTime = time.time()
               objMsg.printMsg('%s Sequential Read on first eighth of the disk' % (TestName))
               data = ICmd.SequentialReadDMAExt(StartLBA, EndLBA, SectCount, SectCount, StampFlag)

               CmdEndTime = time.time()
               CmdTime += CmdEndTime-CmdStartTime
               result = data['LLRET']

            if result == OK:
               CmdStartTime = time.time()
               objMsg.printMsg('%s Sequential Write on first eighth of the disk' % (TestName))
               data = ICmd.SequentialWriteDMAExt(StartLBA, EndLBA, SectCount, SectCount, StampFlag)

               CmdEndTime = time.time()
               CmdTime += CmdEndTime-CmdStartTime
               result = data['LLRET']

            # DT220110 AAU eval
            # DT310510 Remove retry as CPC v2.23 added retry for AAU timeout
            Retry = 0  # 1
            if result == OK:
               for loop in range(Retry+1):
                  CmdStartTime = time.time()
                  objMsg.printMsg('%s Sequential Read on first eighth of the disk with compare' % (TestName))
                  data = ICmd.SequentialReadDMAExt(StartLBA, EndLBA, SectCount, SectCount, StampFlag, CompareFlag)

                  CmdEndTime = time.time()
                  CmdTime += CmdEndTime-CmdStartTime
                  result = data['LLRET']

                  # DT22011O AAU Retry
                  # DT310510 Remove retry as CPC v2.23 added retry for AAU timeout
   #               if result != OK and DoRetry == ON:
   #                  RetryTest = CheckRetryTest(data['RESULT'], data.get('STS','NIL'), data.get('ERR','NIL'), loop)
   #                  if RetryTest != ON: break
   #                  # DT070709 LLRetry
   #                  #SaveFailureAttributes(data, TestType, TestName)
   #                  objMsg.printMsg('SequentialReadDMAExt w/compare - Loop Number %d of %d Failed - Do Retry' % (loop+1, Retry+1))
   #                  objMsg.printMsg('SequentialReadDMAExt w/compare - Retry - Power Cycle and Re-issue CPC Embedded Command')
   #                  self.getSerialPortData()
   #                  self.oRF.powerCycle()
   #                  self.postPowerCycleSequence()
   #               else: break
                  # DT310510 Remove retry as CPC v2.23 added retry for AAU timeout
                  if result == OK: break

         if result != OK:
            objMsg.printMsg('%s Failed Result=%s Data=%s' % (TestName, result, data))
            raise gioTestException(data)
         else:
            if P_Msg:
               objMsg.printMsg('%s Write Performance ------------------------------------' % TestName)
               NumCmds=(EndLBA/SectCount); BlocksXfrd=EndLBA
               self.displayPerformance(TestName,NumCmds,BlocksXfrd,BlockSize,CmdTime)
               self.displayCmdTimes(TestName, 'CPC', CmdTime, SectCount)

   #      if result == OK and IDT_RESULT_FILE_DATA == ON:
   #         TestTime = timetostring(testtime['functotal'])
   #         CollectData(result, TestType, TestNum, TestName, TestTime, CheckBER=0)

         return result, data

   #   #-----------------------------------------------------------------------------------------#
   #   def doODTATI(self, TestType):
   #      P_Msg = ON      # Performance Message
   #      F_Msg = ON      # Failure Message
   #      B_Msg = ON      # Buffer Message
   #      data = {}
   #      result = OK
   #      DoRetry = ON
   #      UDMA_Speed = 0x45
   #
   #      TestName = ('ODT ATI Test')                       # Test Name for file formatting
   ##      driveattr['testseq'] = TestName.replace(' ','_')
   ##      driveattr['eventdate'] = time.time()
   #      self.testName = ('%s %s' % (TestType,TestName))
   #      self.printTestName(self.testName)
   #
   #      self.oRF.powerCycle()
   #      self.postPowerCycleSequence()
   #      if result == OK:
   #         data = {}
   #         Pattern = 0x1234
   #         #StepLBA = 256
   #         SectCount = 256
   #         StampFlag = 0
   #         CompareFlag = 0
   #         # DT151009 Reduce 10K write to 5K
   #         #CmdLoop = 10000
   #         CmdLoop = 5000
   #         TestLoop = 50
   #         StartLBA = 0
   #         EndLBA = 400
   #         MaxLBA = self.oRF.IDAttr['MaxLBA']
   #
   #         StepLBA = MaxLBA/400
   #
   #         #if driveattr['NumLogSect'] > 1:
   #         #   MaxLBA = MaxLBA - (MaxLBA % driveattr['NumLogSect'])
   #
   #         #StepLBA = (MaxLBA/3200) * 8
   #         BlockSize = 512
   #         CmdTime = 0
   #
   #         objMsg.printMsg('%s Start LBA=%d End LBA=%d Sect Count=%d Pattern=0x%2X' % \
   #                        (TestName, StartLBA, EndLBA, SectCount, Pattern))
   #
   #         objMsg.printMsg('%s Flush Cache, Clear Buffers, Fill 0x%2X Data' % (TestName, Pattern))
   #         data = ICmd.FlushCache()
   #         result = data['LLRET']
   #         objMsg.printMsg('%s Flush Cache. Result=%s' % (TestName, str(result)))
   #         if result != OK:
   #            return result
   #         ICmd.ClearBinBuff(WBF);  ICmd.ClearBinBuff(RBF)
   #         ICmd.FillBuffByte(WBF, Pattern)
   #         if B_Msg:
   #            objMsg.printMsg('%s Write Buffer Data ----------------------------------------' % TestName)
   #            wb_data = ICmd.GetBuffer(WBF, 0, 550)['DATA']
   #            objMsg.printMsg('%s %s' % (TestName, wb_data[0:20]))
   #            objMsg.printMsg('%s %s' % (TestName, wb_data[512:532]))
   #
   #         result = ICmd.SetFeatures(0x03,UDMA_Speed)['LLRET']
   #         if result != OK:
   #            objMsg.printMsg('%s Failed SetFeatures - Transfer Rate = UDMA-%d' % (self.testName, self.getUDMASpeed(UDMA_Speed)))
   #         else:
   #            objMsg.printMsg('%s Passed SetFeatures - Transfer Rate = UDMA-%d' % (self.testName, self.getUDMASpeed(UDMA_Speed)))
   #
   #         result = ICmd.SetFeatures(0x82)['LLRET']
   #         if result != OK:
   #            objMsg.printMsg('%s Failed SetFeatures - Disable Write Cache' % (TestName))
   #         else:
   #            objMsg.printMsg('%s Passed SetFeatures - Disable Write Cache' % (TestName))
   #
   #         CmdStartTime = time.time()
   #         objMsg.printMsg('%s Write on first %d locations %d times' % (TestName, TestLoop, CmdLoop))
   #         for loop in range (0, TestLoop, 1):
   #            StartLBA = loop * StepLBA
   #            objMsg.printMsg('10k write on 400 LBA starting %d' % StartLBA)
   #
   #            # DT170709 Apply offset calculation
   #            if self.oRF.IDAttr['NumLogSect'] > 1:
   #               # Adjust for number of physical sector per logical sector
   #               StartLBA = StartLBA - (StartLBA % self.oRF.IDAttr['NumLogSect'])
   #               if self.oRF.IDAttr['OffSetLBA0'] > 0:
   #                  if StartLBA == 0:    # Avoid negative LBA range, proceed to next block
   #                     StartLBA = StartLBA + self.oRF.IDAttr['NumLogSect']
   #                  # Adjust for alignment of Log Block in Phy Block
   #                  StartLBA = StartLBA - self.oRF.IDAttr['OffSetLBA0']
   #
   #            EndLBA = StartLBA + 400
   #            objMsg.printMsg('10K write location(%d) adjusted from start=%d to end=%d, with offset=%d' % (loop+1, StartLBA, EndLBA, self.oRF.IDAttr['OffSetLBA0']))
   #
   #            if self.oRF.IDAttr['Support48Bit'] == 'ON':
   #               data = ICmd.SequentialCmdLoop(0x35,StartLBA,EndLBA,SectCount,SectCount,CmdLoop,1)
   #            else:
   #               data = ICmd.SequentialCmdLoop(0xCA,StartLBA,EndLBA,SectCount,SectCount,CmdLoop,1)
   #            result = data['LLRET']
   #            if result != OK:
   #               objMsg.printMsg('SequentialCmdLoop failed at loop %d, result=%s' % (TestLoop,data))
   #               break
   #         # end for
   #         CmdEndTime = time.time()
   #         CmdTime += CmdEndTime-CmdStartTime
   #
   #         if result == OK:
   #            result = ICmd.SetFeatures(0x02)['LLRET']
   #            if result != OK:
   #               objMsg.printMsg('%s Failed SetFeatures - Enable Write Cache' % (TestName))
   #            else:
   #               objMsg.printMsg('%s Passed SetFeatures - Enable Write Cache' % (TestName))
   #         if result == OK:
   #            Pattern = 0x00
   #            StartLBA = 0
   #            EndLBA = MaxLBA/8
   #            CompareFlag = 1
   #            objMsg.printMsg('%s Start LBA=%d End LBA=%d Sect Count=%d Pattern=0x%2X' % \
   #                           (TestName, StartLBA, EndLBA, SectCount, Pattern))
   #            objMsg.printMsg('%s Flush Cache, Clear Buffers, Fill 0x%2X Data' % (TestName, Pattern))
   #            result = ICmd.FlushCache()['LLRET']
   #            if result != OK:
   #               return result
   #            ICmd.ClearBinBuff(WBF);  ICmd.ClearBinBuff(RBF)
   #            ICmd.FillBuffByte(WBF, Pattern)
   #            if B_Msg:
   #               objMsg.printMsg('%s Write Buffer Data ----------------------------------------' % TestName)
   #               wb_data = ICmd.GetBuffer(WBF, 0, 550)['DATA']
   #               objMsg.printMsg('%s %s' % (TestName, wb_data[0:20]))
   #               objMsg.printMsg('%s %s' % (TestName, wb_data[512:532]))
   #
   #            CmdStartTime = time.time()
   #            objMsg.printMsg('%s Sequential Read on first eighth of the disk' % (TestName))
   #            data = ICmd.SequentialReadDMAExt(StartLBA, EndLBA, SectCount, SectCount, StampFlag)
   #
   #            CmdEndTime = time.time()
   #            CmdTime += CmdEndTime-CmdStartTime
   #            result = data['LLRET']
   #
   #         if result == OK:
   #            CmdStartTime = time.time()
   #            objMsg.printMsg('%s Sequential Write on first eighth of the disk' % (TestName))
   #            data = ICmd.SequentialWriteDMAExt(StartLBA, EndLBA, SectCount, SectCount, StampFlag)
   #
   #            CmdEndTime = time.time()
   #            CmdTime += CmdEndTime-CmdStartTime
   #            result = data['LLRET']
   #
   #         # DT220110 AAU eval
   #         # DT310510 Remove retry as CPC v2.23 added retry for AAU timeout
   #         Retry = 0  # 1
   #         if result == OK:
   #            for loop in range(Retry+1):
   #               CmdStartTime = time.time()
   #               objMsg.printMsg('%s Sequential Read on first eighth of the disk with compare' % (TestName))
   #               data = ICmd.SequentialReadDMAExt(StartLBA, EndLBA, SectCount, SectCount, StampFlag, CompareFlag)
   #
   #               CmdEndTime = time.time()
   #               CmdTime += CmdEndTime-CmdStartTime
   #               result = data['LLRET']
   #
   #               # DT22011O AAU Retry
   #               # DT310510 Remove retry as CPC v2.23 added retry for AAU timeout
   ##               if result != OK and DoRetry == ON:
   ##                  RetryTest = CheckRetryTest(data['RESULT'], data.get('STS','NIL'), data.get('ERR','NIL'), loop)
   ##                  if RetryTest != ON: break
   ##                  # DT070709 LLRetry
   ##                  #SaveFailureAttributes(data, TestType, TestName)
   ##                  objMsg.printMsg('SequentialReadDMAExt w/compare - Loop Number %d of %d Failed - Do Retry' % (loop+1, Retry+1))
   ##                  objMsg.printMsg('SequentialReadDMAExt w/compare - Retry - Power Cycle and Re-issue CPC Embedded Command')
   ##                  self.getSerialPortData()
   ##                  self.oRF.powerCycle()
   ##                  self.postPowerCycleSequence()
   ##               else: break
   #               # DT310510 Remove retry as CPC v2.23 added retry for AAU timeout
   #               if result == OK: break
   #
   #      if result != OK:
   #         objMsg.printMsg('%s Failed Result=%s Data=%s' % (TestName, result, data))
   #         raise gioTestException(data)
   #      else:
   #         if P_Msg:
   #            objMsg.printMsg('%s Write Performance ------------------------------------' % TestName)
   #            NumCmds=(EndLBA/SectCount); BlocksXfrd=EndLBA
   #            self.displayPerformance(TestName,NumCmds,BlocksXfrd,BlockSize,CmdTime)
   #            self.displayCmdTimes(TestName, 'CPC', CmdTime, SectCount)
   #
   ##      if result == OK and IDT_RESULT_FILE_DATA == ON:
   ##         TestTime = timetostring(testtime['functotal'])
   ##         CollectData(result, TestType, TestNum, TestName, TestTime, CheckBER=0)
   #
   #      return result
      #---------------------------------------------------------------------------------------------------------#
      #def doODTRamTest(self, TestType='IDT'):
      #   P_Msg = ON      # Performance Message
      #   F_Msg = ON      # Failure Message
      #   B_Msg = ON      # Buffer Message
      #   data = {}
      #   failure = ''
      #   result = OK
      #   TestName = ('Ram Miscompare')                       # Test Name for file formatting
      #   self.testName = ('%s %s' % (TestType, TestName))
      #   self.printTestName(self.testName)

      #   self.oRF.powerCycle()

         # Setup Parameters
      #   UDMA_Speed = 0x45

      #   ICmd.SetIntfTimeout(90000)
      #   result = ICmd.SetFeatures(0x03,UDMA_Speed)['LLRET']
      #   if result != OK:
      #      objMsg.printMsg('%s Failed SetFeatures - Transfer Rate = UDMA-%d' % (self.testName, self.getUDMASpeed(UDMA_Speed)))
      #   else:
      #      objMsg.printMsg('%s Passed SetFeatures - Transfer Rate = UDMA-%d' % (self.testName, self.getUDMASpeed(UDMA_Speed)))

      #   if result == OK:
      #      result = ICmd.SetFeatures(0x55)['LLRET']   # Disable read look ahead
      #   if result == OK:
      #      result = ICmd.SetFeatures(0x02)['LLRET']   # Enable write cache

      #   if result == OK:
      #      result, data, failure = CDramScreenTest(self.oRF.IDAttr['MaxLBA']).run()
      #      if result != OK:
      #         self.testName = failure
      #         raise gioTestException(data)

      #   if result == OK:
      #      result, data, failure = Compare(self.oRF.IDAttr['MultLogSect']).Loop()
      #      if result != OK:
      #         self.testName = failure
      #         if data.has_key('citnumverify'):
      #            #RT140711: Bugfix DriveAttributes accepts a list type
      #            #DriveAttributes.update(data['citnumverify'])
      #            #DriveAttributes.update(data['citnumfailed'])
      #            DriveAttributes.update(data)
      #         result = FAIL
      #         objMsg.printMsg('DRAM Miscompare Test Failed - NumVerify=%d NumFailed=%d' % \
      #                        ( data['citnumverify'], data['citnumfailed'] ))
      #         objMsg.printMsg('DRAM Miscompare Test Failed - Failcode=%s' % self.oFC.getFailCode(failure) )
      #         raise gioTestException(data)
      #      else:
      #         objMsg.printMsg('DRAM Miscompare Test Passed - Result = %d' % result)

      #   return result,data

      #-----------------------------------------------------------------------------------------#
      def doODTRamTest(self, TestType='IDT'):

         data = {}
         result = OK
         LLRetry = 'NO'
         DRamFiles=[
             "fs_aaaa.pat",
             "fs_ff00.pat",
             "fs_aa55.pat",
             "fs_aa00.pat",
             "fs_55aa.pat",
             "fs_00ff.pat",
             "fs_00aa.pat",
         ]
         minLBA = 0
         maxLBA = self.oRF.IDAttr['MaxLBA']
         startLBA = endLBA = 0
         minSectCnt = 23
         maxSectCnt = 256
         totalRndWrRdLBA = 32 * 1024
         totalSeqWrRdLBA = 256 * 1024
         stampFlag = 0
         compareFlag = 1

         self.testName = 'IDT Ram Miscompare'
         self.printTestName(self.testName)

         self.oRF.powerCycle()
         self.postPowerCycleSequence()


         # loop through pattern files
         for patternfile in DRamFiles:
            if result != OK: break
            filename = os.path.join(UserDownloadsPath, self.ConfigName, patternfile)
            patternfile = open(filename,'rb')
            try:
               patterndata = patternfile.read()
               objMsg.printMsg('%s Read Pattern File=%s' % (self.testName, filename))
               ICmd.ClearBinBuff(WBF)     # CPC specific
               ICmd.FillBuffer(WBF, 0, patterndata)   # default buffer size 128K bytes

               # Random Write/Read/Compare 32K LBA(random transfer length and start LBA)
               #for retry in range(self.LLRetryCount+1):
               if result != OK: break
               ICmd.ClearBinBuff(RBF)
               objMsg.printMsg('%s RandomWrtRdCompare 32K LBA for 30sec' % self.testName)
               endTime = time.time()+ 30         # 30sec
               while ( time.time() < endTime):
                  if result != OK: break
                  sectCnt = random.randint(minSectCnt, maxSectCnt)
                  startLBA = random.randint(1, self.maxLBA-(32*1024+1))
                  endLBA = startLBA + totalRndWrRdLBA - 1
                  objMsg.printMsg('%s RandomWrtRdComp 32K StartLBA=%d EndLBA=%d StepCnt=%d SectCount=%d' % \
                                 (self.testName, startLBA, endLBA, sectCnt, sectCnt))
                  data = ICmd.SequentialWRDMAExt(startLBA, endLBA, sectCnt, sectCnt, stampFlag, compareFlag)
                  self.testCmdTime += float(data.get('CT','0'))/1000
                  result = data['LLRET']
                  objMsg.printMsg('%s RandomWrtRdComp 32K data=%s' % (self.testName, data))

               if result == OK:
                  objMsg.printMsg('%s RandomWrtRdComp 32K test passed!' % self.testName)
               else:
                  objMsg.printMsg('%s RandomWrtRdComp 32K test failed!' % self.testName)

               # Random Write/Read/Compare 256K LBA(random transfer length and start LBA)
               #for retry in range(self.LLRetryCount+1):
               if result != OK: break
               ICmd.ClearBinBuff(RBF)
               objMsg.printMsg('%s SequentialWriteReadCompare 256K LBA for 30sec' % self.testName)

               endTime = time.time()+ 30         # 30sec
               while ( time.time() < endTime):
                  if result != OK: break
                  sectCnt = random.randint(minSectCnt, maxSectCnt)
                  startLBA = random.randint(0, maxLBA - totalSeqWrRdLBA +1)
                  endLBA = startLBA + totalSeqWrRdLBA - 1
                  objMsg.printMsg('%s SequentialWriteDMAExt 256K StartLBA=%d endLBA=%d sectCnt=%d numLBA=%d' % \
                                 (self.testName, startLBA, endLBA, sectCnt, totalSeqWrRdLBA))
                  data = ICmd.SequentialWriteDMAExt(startLBA, endLBA, sectCnt, sectCnt)
                  self.testCmdTime += float(data.get('CT','0'))/1000
                  result = data['LLRET']
                  objMsg.printMsg('%s SequentialWriteDMAExt 256K Data=%s' % (self.testName, data))

                  if result == OK:
                     data = ICmd.SequentialReadDMAExt(startLBA, endLBA, sectCnt, sectCnt, stampFlag, compareFlag)
                     result = data['LLRET']
                     objMsg.printMsg('%s SequentialReadDMAExt 256K Data=%s' % (self.testName, data))

               if result == OK:
                  objMsg.printMsg('%s SequentialReadDMAExt 256K test passed!' % self.testName)
               else:
                  objMsg.printMsg('%s SequentialReadDMAExt 256K test failed!' % self.testName)

            finally:
               patternfile.close()
               objMsg.printMsg('Pattern File %s Closed' % filename)

         self.displayCmdTimes(self.testName,'CPC',self.testCmdTime,sectCnt)
         # for each pattern file
         self.printTestName(self.testName + ' End')
         if result == OK:
            objMsg.printMsg('%s Test Passed!' % self.testName)
         else:
            objMsg.printMsg('%s Test Failed!' % self.testName)
            raise gioTestException(data)

         return result,data

      #---------------------------------------------------------------------------------------------------------#
      def doWriteZeroPatt(self, TestType='IDT', NumLBA='MaxLBA'):
         P_Msg = ON      # Performance Message
         F_Msg = ON      # Failure Message
         B_Msg = ON      # Buffer Message
         data = {}
         result = OK
         DoRetry = ON
         TestName = ('Write Zero Patt')                       # Test Name for file formatting
         self.testName = ('%s %s' % (TestType,TestName))
         self.printTestName(self.testName)


         self.oRF.powerCycle()
         # Setup Parameters
         UDMA_Speed = 0x45
         Pattern = 0x00
         StepLBA = 256
         SectCount = 256
         StampFlag = 0
         StartLBA = 0
         BlockSize = 512
         if NumLBA == ('MaxLBA'):
            EndLBA = self.oRF.IDAttr['MaxLBA']
         else: EndLBA = NumLBA

         self.udmaSpeed = UDMA_Speed
         self.pattern = Pattern
         self.sectorCount = SectCount
         self.numBlocks = EndLBA/SectCount
         self.timeout = self.calculateTimeout(self.numBlocks,self.sectorCount)
         objMsg.printMsg('%s Start LBA=%d End LBA=%d Sect Count=%d Pattern=0x%2X' % \
                        (self.testName, StartLBA, EndLBA, SectCount, Pattern))

         objMsg.printMsg('%s Flush Cache, Clear Buffers, Fill 0x%2X Data' % (self.testName, Pattern))
         ICmd.FlushCache(); ICmd.ClearBinBuff(1); ICmd.ClearBinBuff(2)
         ICmd.FillBuffByte(1,Pattern)
         if B_Msg:
            objMsg.printMsg('%s Write Buffer Data ----------------------------------------' % self.testName)
            wb_data = ICmd.GetBuffer(1, 0, 550)['DATA']
            objMsg.printMsg('%s %s' % (self.testName, wb_data[0:20]))
            objMsg.printMsg('%s %s' % (self.testName, wb_data[512:532]))

         result = ICmd.SetFeatures(0x03,UDMA_Speed)['LLRET']
         if result != OK:
            objMsg.printMsg('%s Failed SetFeatures - Transfer Rate = UDMA-%d' % (self.testName, self.getUDMASpeed(UDMA_Speed)))
         else:
            objMsg.printMsg('%s Passed SetFeatures - Transfer Rate = UDMA-%d' % (self.testName, self.getUDMASpeed(UDMA_Speed)))
         result = ICmd.SetFeatures(0x02)['LLRET']
         if result != OK:
            objMsg.printMsg('%s Failed SetFeatures - Enable Write Cache' % (self.testName))
         else:
            objMsg.printMsg('%s Passed SetFeatures - Enable Write Cache' % (self.testName))

         Retry = 1
         for loop in range(Retry+1):
            #CmdStartTime = time.time()
            if self.oRF.IDAttr['Support48Bit'] == 'ON':
               data = ICmd.SequentialWriteDMAExt(StartLBA, EndLBA, StepLBA, SectCount, StampFlag,timeout=self.timeout,exc=0)
            else:
               data = ICmd.SequentialWriteDMA(StartLBA, EndLBA, StepLBA, SectCount, StampFlag,timeout=self.timeout,exc=0)
            #CmdEndTime = time.time()
            #self.testCmdTime = CmdEndTime-CmdStartTime
            self.testCmdTime += float(data.get('CT','0'))/1000
            result = data['LLRET']
            if result == OK:
               # DT270510
               self.getSerialPortData()
               objMsg.printMsg("%s SequentialWriteDMA Passed - Data: %s" % (self.testName, data))
               break
            else:
               objMsg.printMsg("%s SequentialWriteDMA Failed - Data: %s" % (self.testName, data))
            if DoRetry == ON:
               RetryTest = self.checkRetryTest(data['RESULT'], data.get('STS','NIL'), data.get('ERR','NIL'))
               if RetryTest != ON: break
               objMsg.printMsg('SequentialWriteDMA - Loop Number %d of %d Failed - Do Retry' % (loop+1, Retry+1))
               objMsg.printMsg('SequentialWriteDMA - Retry - Power Cycle and Re-issue CPC Embedded Command')
               self.getSerialPortData()
               self.oRF.powerCycle()
               self.postPowerCycleSequence()

         self.displayCmdTimes(self.testName,'CPC',self.testCmdTime,self.sectorCount)
         if result == OK:
            if P_Msg:
               BlocksXfrd=EndLBA;NumCmds=(EndLBA/SectCount)
               self.displayPerformance(TestName,NumCmds,BlocksXfrd,BlockSize,self.testCmdTime)
            objMsg.printMsg('%s Test Passed' % self.testName)
         else:
            objMsg.printMsg('%s Failed Result=%s Data=%s' % (self.testName, result, data))

            raise gioTestException(data)

         return result, data

      #---------------------------------------------------------------------------------------------------------#
      def doWriteZeroPattGuard(self, TestType = 'IDT', LBABand = 20971520):
         P_Msg = ON      # Performance Message
         F_Msg = ON      # Failure Message
         B_Msg = ON      # Buffer Message
         data = {}
         result = OK
         DoRetry = OFF
         TestName = ('Write Zero Patt')                       # Test Name for file formatting
         self.testName = ('%s %s' % (TestType,TestName))
         self.printTestName(self.testName)


         self.oRF.powerCycle()
         # Setup Parameters
         UDMA_Speed = 0x45
         Pattern = 0x00
         StepLBA = 256
         SectCount = 256
         StampFlag = 0
         StartLBA = 0
         BlockSize = 512

         # DT221009 for 1st and last 20M sector
         ODStartLBA = 0
         ODEndLBA = ODStartLBA + LBABand
         IDStartLBA = self.oRF.IDAttr['MaxLBA'] - LBABand
         IDEndLBA = self.oRF.IDAttr['MaxLBA']
         TotalLBA = 2 * LBABand

         self.udmaSpeed = UDMA_Speed
         self.pattern = Pattern
         self.sectorCount = SectCount
         self.numBlocks = TotalLBA/SectCount
         self.timeout = self.calculateTimeout(self.numBlocks,self.sectorCount)


         objMsg.printMsg('%s Flush Cache, Clear Buffers, Fill 0x%2X Data' % (self.testName, Pattern))
         ICmd.FlushCache(); ICmd.ClearBinBuff(1); ICmd.ClearBinBuff(2)
         ICmd.FillBuffByte(1,Pattern)
         if B_Msg:
            objMsg.printMsg('%s Write Buffer Data ----------------------------------------' % self.testName)
            wb_data = ICmd.GetBuffer(1, 0, 550)['DATA']
            objMsg.printMsg('%s %s' % (self.testName, wb_data[0:20]))
            objMsg.printMsg('%s %s' % (self.testName, wb_data[512:532]))

         result = ICmd.SetFeatures(0x03,UDMA_Speed)['LLRET']
         if result != OK:
            objMsg.printMsg('%s Failed SetFeatures - Transfer Rate = UDMA-%d' % (self.testName, self.getUDMASpeed(UDMA_Speed)))
         else:
            objMsg.printMsg('%s Passed SetFeatures - Transfer Rate = UDMA-%d' % (self.testName, self.getUDMASpeed(UDMA_Speed)))
         result = ICmd.SetFeatures(0x02)['LLRET']
         if result != OK:
            objMsg.printMsg('%s Failed SetFeatures - Enable Write Cache' % (self.testName))
         else:
            objMsg.printMsg('%s Passed SetFeatures - Enable Write Cache' % (self.testName))

         Retry = 1
         for loop in range(Retry+1):

            #CmdStartTime = time.time()
            if self.oRF.IDAttr['Support48Bit'] == 'ON':
               if result == OK:
                  objMsg.printMsg('%s WriteOD ODStartLBA=%d ODEndLBA=%d SectCount=%d Pattern=0x%2X' % \
                                 (self.testName, ODStartLBA, ODEndLBA, SectCount, Pattern))
                  data = ICmd.SequentialWriteDMAExt(ODStartLBA, ODEndLBA, StepLBA, SectCount, StampFlag, timeout=self.timeout, exc=0)
                  result = data['LLRET']

               if result == OK:
                  objMsg.printMsg('%s WriteID IDStartLBA=%d IDEndLBA=%d SectCount=%d Pattern=0x%2X' % \
                                 (self.testName, IDStartLBA, IDEndLBA, SectCount, Pattern))
                  data = ICmd.SequentialWriteDMAExt(IDStartLBA, IDEndLBA, StepLBA, SectCount, StampFlag, timeout=self.timeout, exc=0)
                  result = data['LLRET']

            else:
               if result == OK:
                  objMsg.printMsg('%s WriteOD ODStartLBA=%d ODEndLBA=%d SectCount=%d Pattern=0x%2X' % \
                                 (self.testName, ODStartLBA, ODEndLBA, SectCount, Pattern))
                  data = ICmd.SequentialWriteDMA(ODStartLBA, ODEndLBA, StepLBA, SectCount, StampFlag, timeout=self.timeout, exc=0)
                  result = data['LLRET']
               if result == OK:
                  objMsg.printMsg('%s WriteID IDStartLBA=%d IDEndLBA=%d SectCount=%d Pattern=0x%2X' % \
                                 (self.testName, IDStartLBA, IDEndLBA, SectCount, Pattern))
                  data = ICmd.SequentialWriteDMA(IDStartLBA, IDEndLBA, StepLBA, SectCount, StampFlag, timeout=self.timeout, exc=0)
                  result = data['LLRET']

            #CmdEndTime = time.time()
            #self.testCmdTime = CmdEndTime-CmdStartTime
            self.testCmdTime += float(data.get('CT','0'))/1000
            result = data['LLRET']
            if result == OK:
               # DT270510
               self.getSerialPortData()
               objMsg.printMsg("%s SequentialWriteDMAExt Passed - Data: %s" % (self.testName, data))
               break
            else:
               objMsg.printMsg("%s SequentialWriteDMAExt Failed - Data: %s" % (self.testName, data))
            if DoRetry == ON:
               RetryTest = self.checkRetryTest(data['RESULT'], data.get('STS','NIL'), data.get('ERR','NIL'))
               if RetryTest != ON: break
               objMsg.printMsg('SequentialWriteDMAExt - Loop Number %d of %d Failed - Do Retry' % (loop+1, Retry+1))
               objMsg.printMsg('SequentialWriteDMAExt - Retry - Power Cycle and Re-issue CPC Embedded Command')
               self.getSerialPortData()
               self.oRF.powerCycle()
               self.postPowerCycleSequence()

         self.displayCmdTimes(self.testName,'CPC',self.testCmdTime,self.sectorCount)
         if result == OK:
            if P_Msg:
                  BlocksXfrd=TotalLBA;NumCmds=(TotalLBA/SectCount)
                  self.displayPerformance(TestName,NumCmds,BlocksXfrd,BlockSize,self.testCmdTime)
            objMsg.printMsg('%s Test Passed' % self.testName)
         else:
            objMsg.printMsg('%s Failed Result=%s Data=%s' % (self.testName, result, data))

            raise gioTestException(data)

         return result

      #---------------------------------------------------------------------------------------------------------#
      def doReadZeroVerify(self, TestType='IDT', NumLBA=35000):
         P_Msg = ON      # Performance Message
         F_Msg = ON      # Failure Message
         B_Msg = ON      # Buffer Message
         data = {}
         result = OK
         TestName = ('Read Zero Verify')                       # Test Name for file formatting
         self.testName = ('%s %s' % (TestType,TestName))
         self.printTestName(self.testName)


         self.oRF.powerCycle()
         # Setup Parameters
         UDMA_Speed = 0x45
         Pattern = 0x00
         StepLBA = 256
         SectCount = 256
         StampFlag = 0
         CompFlag = 1
         StartLBA = 0
         BlockSize = 512
         if NumLBA == ('MaxLBA'):
            EndLBA = int(self.oRF.IDAttr['MaxLBA']/10)
            templba = EndLBA
         else:
            EndLBA = (NumLBA/10)
            templba = EndLBA

         self.udmaSpeed = UDMA_Speed
         self.pattern = Pattern
         self.sectorCount = SectCount
         self.numBlocks = EndLBA/SectCount
         self.timeout = self.calculateTimeout(self.numBlocks,self.sectorCount)
         objMsg.printMsg('%s Start LBA=%d End LBA=%d Sect Count=%d Pattern=0x%2X' % \
                        (self.testName, StartLBA, EndLBA, SectCount, Pattern))

         objMsg.printMsg('%s Flush Cache, Clear Buffers, Fill 0x%2X Data' % (self.testName, Pattern))
         ICmd.FlushCache(); ICmd.ClearBinBuff(1); ICmd.ClearBinBuff(2)
         ICmd.FillBuffByte(1,Pattern)
         if B_Msg:
            objMsg.printMsg('%s Write Buffer Data ----------------------------------------' % self.testName)
            wb_data = ICmd.GetBuffer(1, 0, 550)['DATA']
            objMsg.printMsg('%s %s' % (self.testName, wb_data[0:20]))
            objMsg.printMsg('%s %s' % (self.testName, wb_data[512:532]))

         result = ICmd.SetFeatures(0x03,UDMA_Speed)['LLRET']
         if result != OK:
            objMsg.printMsg('%s Failed SetFeatures - Transfer Rate = UDMA-%d' % (self.testName, self.getUDMASpeed(UDMA_Speed)))
         else:
            objMsg.printMsg('%s Passed SetFeatures - Transfer Rate = UDMA-%d' % (self.testName, self.getUDMASpeed(UDMA_Speed)))

         for loop in range(10):
            objMsg.printMsg('StartLBA %d = EndLBA = %d' % (StartLBA, EndLBA))
            if self.oRF.IDAttr['Support48Bit'] == 'ON':
               data = ICmd.SequentialReadDMAExt(StartLBA, EndLBA, StepLBA, SectCount, StampFlag, CompFlag,timeout=self.timeout,exc=0)
            else:
               data = ICmd.SequentialReadDMA(StartLBA, EndLBA, StepLBA, SectCount, StampFlag, CompFlag,timeout=self.timeout,exc=0)
            StartLBA = EndLBA + 1
            EndLBA = EndLBA + templba
            self.testCmdTime += float(data.get('CT','0'))/1000
            result = data['LLRET']
            if result != OK:
               objMsg.printMsg("%s SequentialReadDMA Failed - Data: %s" % (self.testName, data))
               break
            #else:
            #   objMsg.printMsg("%s SequentialReadDMA Passed - Data: %s" % (self.testName, data))
         if B_Msg or result != OK:
            objMsg.printMsg('%s Read Buffer Data ----------------------------------------' % TestName)
            rb_data = ICmd.GetBuffer(2, 0, 550)['DATA']
            objMsg.printMsg('%s %s' % (self.testName, rb_data[0:20]))
            objMsg.printMsg('%s %s' % (self.testName, rb_data[512:532]))
         self.displayCmdTimes(self.testName,'CPC',self.testCmdTime,self.sectorCount)
         if result == OK:
            if P_Msg:
               BlocksXfrd=EndLBA;NumCmds=(EndLBA/SectCount)
               self.displayPerformance(TestName,NumCmds,BlocksXfrd,BlockSize,self.testCmdTime)
            objMsg.printMsg('%s Test Passed' % self.testName)
         else:
            objMsg.printMsg('%s Failed Result=%s Data=%s' % (self.testName, result, data))

            raise gioTestException(data)

         return result, data

      #---------------------------------------------------------------------------------------------------------#
      def doReadZeroCompare(self, TestType='IDT', NumLBA='MaxLBA'):
         P_Msg = ON      # Performance Message
         F_Msg = ON      # Failure Message
         B_Msg = ON      # Buffer Message
         data = {}
         result = OK
         TestName = ('Read Zero Compare')                       # Test Name for file formatting
         self.testName = ('%s %s' % (TestType,TestName))
         self.printTestName(self.testName)


         self.oRF.powerCycle()
         # Setup Parameters
         UDMA_Speed = 0x45
         Pattern = 0x00
         OneMegByte = 1048576                                        # 1024 * 1024
         BlockSize  = 512                                            # Sector Size
         NumMegByte = 5                                              # Number of MegaBytes
         StepLBA = 256
         SectCount = 256
         StampFlag = 0
         CompFlag = 1

         # DT080911 - Use ZeroCheck Avoid AAU buffer
         ZeroCheckSect = 0x800

         # DT120909 Reduce buffer size
         #BufferSizeByte = OneMegByte*NumMegByte                      # Buffer Size in Bytes
         #BufferSizeSect = BufferSizeByte/BlockSize                   # Buffer Size in Sectors
         BufferSizeByte = 5 * 512 * 512             # Buffer Size in Bytes
         BufferSizeSect = 512 * 5                   # Buffer Size in Sectors

         StartLBA = 0
         if NumLBA == ('MaxLBA'):
            EndLBA = self.oRF.IDAttr['MaxLBA']
         else:
            EndLBA = (NumLBA)

         self.udmaSpeed = UDMA_Speed
         self.pattern = Pattern
         self.sectorCount = SectCount
         self.numBlocks = EndLBA/SectCount
         self.timeout = self.calculateTimeout(self.numBlocks,self.sectorCount)
         #objMsg.printMsg('%s Start LBA=%d End LBA=%d Sector Count=%d Pattern=0x%2X' % \
         #               (TestName, StartLBA, EndLBA, BufferSizeSect, Pattern))
         # DT080911 - Use ZeroCheck Avoid AAU buffer
         #objMsg.printMsg('%s Make Alternate Buffer Size %d MB' % (self.testName, NumMegByte))
         #ICmd.MakeAlternateBuffer(WBF, BufferSizeSect)

         objMsg.printMsg('%s Flush Cache, Clear Buffers, Fill 0x%2X Data' % (self.testName, Pattern))
         ICmd.FlushCache(); ICmd.ClearBinBuff(WBF); ICmd.ClearBinBuff(RBF)
         ICmd.FillBuffByte(WBF,Pattern,0,BufferSizeByte)
         #if B_Msg:
         #   objMsg.printMsg('%s Write Buffer Data ----------------------------------------' % self.testName)
         #   wb_data = ICmd.GetBuffer(1, 0, 550)['DATA']
         #   objMsg.printMsg('%s %s' % (self.testName, wb_data[0:20]))
         #   objMsg.printMsg('%s %s' % (self.testName, wb_data[512:532]))
         #   objMsg.printMsg('%s Write Buffer Data ----------------------------------------' % self.testName)
         #   wb_data = ICmd.GetBuffer(1, BufferSizeByte-512, BufferSizeByte)['DATA']
         #   objMsg.printMsg('%s %s' % (self.testName, wb_data[0:20]))
         #   objMsg.printMsg('%s %s' % (self.testName, wb_data[512:532]))

         result = ICmd.SetFeatures(0x03,UDMA_Speed)['LLRET']
         if result != OK:
            objMsg.printMsg('%s Failed SetFeatures - Transfer Rate = UDMA-%d' % (self.testName, self.getUDMASpeed(UDMA_Speed)))
         else:
            objMsg.printMsg('%s Passed SetFeatures - Transfer Rate = UDMA-%d' % (self.testName, self.getUDMASpeed(UDMA_Speed)))

            if self.oRF.IDAttr['Support48Bit'] == 'ON':
               # DT080911 - Use ZeroCheck Avoid AAU buffer
               #data = ICmd.SeqReadCompareExt(StartLBA, EndLBA, BufferSizeSect, UDMA_Speed,timeout=self.timeout,exc=0)
               data = ICmd.ZeroCheck(StartLBA, EndLBA, ZeroCheckSect)
            else:
               # DT080911 - Use ZeroCheck Avoid AAU buffer
               #data = ICmd.SequentialReadDMA(StartLBA, EndLBA, StepLBA, SectCount, StampFlag, CompFlag,timeout=self.timeout,exc=0)
               data = ICmd.ZeroCheck(StartLBA, EndLBA, ZeroCheckSect)

            self.testCmdTime += float(data.get('CT','0'))/1000
            result = data['LLRET']
            if result != OK:
               objMsg.printMsg("%s SequentialReadDMA Failed - Data: %s" % (self.testName, data))
            else:
               objMsg.printMsg("%s SequentialReadDMA Passed - Data: %s" % (self.testName, data))
         if B_Msg or result != OK:
            objMsg.printMsg('%s Read Buffer Data ----------------------------------------' % TestName)
            rb_data = ICmd.GetBuffer(2, 0, 550)['DATA']
            objMsg.printMsg('%s %s' % (self.testName, rb_data[0:20]))
            objMsg.printMsg('%s %s' % (self.testName, rb_data[512:532]))

         # DT080911 - Use ZeroCheck Avoid AAU buffer
         # DT141010
         """
         objMsg.printMsg('Restore Primary Buffer')
         ICmd.RestorePrimaryBuffer(WBF)
         """

         self.displayCmdTimes(self.testName,'CPC',self.testCmdTime,self.sectorCount)
         if result == OK:
            if P_Msg:
               BlocksXfrd=EndLBA;NumCmds=(EndLBA/SectCount)
               self.displayPerformance(TestName,NumCmds,BlocksXfrd,BlockSize,self.testCmdTime)
            objMsg.printMsg('%s Test Passed' % self.testName)
         else:
            objMsg.printMsg('%s Failed Result=%s Data=%s' % (self.testName, result, data))

            raise gioTestException(data)

         return result


      #---------------------------------------------------------------------------------------------------------#
      #RT240811(ZeroCheck): Implementation of using ZeroCheck() instead of SeqReadCompareExt
      def doReadZeroCompareGuard(self, TestType='IDT', LBABand = 20971520):
         P_Msg = ON      # Performance Message
         F_Msg = ON      # Failure Message
         B_Msg = ON      # Buffer Message
         data = {}
         result = OK
         TestName = ('Read Zero Compare')                       # Test Name for file formatting
         self.testName = ('%s %s' % (TestType,TestName))
         self.printTestName(self.testName)


         self.oRF.powerCycle()
         # Setup Parameters
         UDMA_Speed = 0x45
         Pattern = 0x00
         OneMegByte = 1048576                                        # 1024 * 1024
         BlockSize  = 512                                            # Sector Size
         NumMegByte = 5                                              # Number of MegaBytes
         StepLBA = 256
         SectCount = 256
         StampFlag = 0
         CompFlag = 1

         #RT240811(ZeroCheck)
         ZeroCheckSect = 0x800

         # DT120909 Reduce buffer size
         #BufferSizeByte = OneMegByte*NumMegByte                      # Buffer Size in Bytes
         #BufferSizeSect = BufferSizeByte/BlockSize                   # Buffer Size in Sectors
         BufferSizeByte = 5 * 512 * 512             # Buffer Size in Bytes
         BufferSizeSect = 512 * 5                   # Buffer Size in Sectors




         # DT221009 for 1st and last 20M sector
         ODStartLBA = 0
         ODEndLBA = ODStartLBA + LBABand
         IDStartLBA = self.oRF.IDAttr['MaxLBA'] - LBABand
         IDEndLBA = self.oRF.IDAttr['MaxLBA']
         TotalLBA = 2 * LBABand


         self.udmaSpeed = UDMA_Speed
         self.pattern = Pattern
         self.sectorCount = SectCount
         self.numBlocks = TotalLBA/SectCount
         self.timeout = self.calculateTimeout(self.numBlocks,self.sectorCount)

         #objMsg.printMsg('%s Start LBA=%d End LBA=%d Sector Count=%d Pattern=0x%2X' % \
         #               (TestName, StartLBA, EndLBA, BufferSizeSect, Pattern))

         #RT240811(ZeroCheck)
         #objMsg.printMsg('%s Make Alternate Buffer Size %d MB' % (self.testName, NumMegByte))
         #ICmd.MakeAlternateBuffer(WBF, BufferSizeSect)

         objMsg.printMsg('%s Flush Cache, Clear Buffers, Fill 0x%2X Data' % (self.testName, Pattern))
         ICmd.FlushCache(); ICmd.ClearBinBuff(WBF); ICmd.ClearBinBuff(RBF)
         ICmd.FillBuffByte(WBF,Pattern,0,BufferSizeByte)
         #if B_Msg:
         #   objMsg.printMsg('%s Write Buffer Data ----------------------------------------' % self.testName)
         #   wb_data = ICmd.GetBuffer(WBF, 0, 550)['DATA']
         #   objMsg.printMsg('%s %s' % (self.testName, wb_data[0:20]))
         #   objMsg.printMsg('%s %s' % (self.testName, wb_data[512:532]))
         #   objMsg.printMsg('%s Write Buffer Data ----------------------------------------' % self.testName)
         #   wb_data = ICmd.GetBuffer(WBF, BufferSizeByte-512, BufferSizeByte)['DATA']
         #   objMsg.printMsg('%s %s' % (self.testName, wb_data[0:20]))
         #   objMsg.printMsg('%s %s' % (self.testName, wb_data[512:532]))

         result = ICmd.SetFeatures(0x03,UDMA_Speed)['LLRET']
         if result != OK:
            objMsg.printMsg('%s Failed SetFeatures - Transfer Rate = UDMA-%d' % (self.testName, self.getUDMASpeed(UDMA_Speed)))
         else:
            objMsg.printMsg('%s Passed SetFeatures - Transfer Rate = UDMA-%d' % (self.testName, self.getUDMASpeed(UDMA_Speed)))

            if self.oRF.IDAttr['Support48Bit'] == 'ON':
               if result == OK:
                  #RT240811(ZeroCheck)
                  #objMsg.printMsg('%s ReadOD ODStartLBA=%d ODEndLBA=%d SectCount=%d Pattern=0x%2X' % \
                  #               (self.testName, ODStartLBA, ODEndLBA, BufferSizeSect, Pattern))
                  #data = ICmd.SeqReadCompareExt(ODStartLBA, ODEndLBA, BufferSizeSect, UDMA_Speed, timeout=self.timeout, exc=0)
                  objMsg.printMsg('%s ReadOD ODStartLBA=%d ODEndLBA=%d SectCount=%d Pattern=0x%2X' % \
                                 (self.testName, ODStartLBA, ODEndLBA, ZeroCheckSect, Pattern))
                  data = ICmd.ZeroCheck(ODStartLBA, ODEndLBA, ZeroCheckSect)

                  result = data['LLRET']
               if result == OK:
                  #RT240811(ZeroCheck)
                  #objMsg.printMsg('%s ReadID IDStartLBA=%d IDEndLBA=%d SectCount=%d Pattern=0x%2X' % \
                  #               (self.testName, IDStartLBA, IDEndLBA, BufferSizeSect, Pattern))
                  #data = ICmd.SeqReadCompareExt(IDStartLBA, IDEndLBA, BufferSizeSect, UDMA_Speed, timeout=self.timeout, exc=0)
                  objMsg.printMsg('%s ReadID IDStartLBA=%d IDEndLBA=%d SectCount=%d Pattern=0x%2X' % \
                                 (self.testName, IDStartLBA, IDEndLBA, ZeroCheckSect, Pattern))
                  data = ICmd.ZeroCheck(IDStartLBA, IDEndLBA, ZeroCheckSect)

                  result = data['LLRET']
            else:
               if result == OK:
                  objMsg.printMsg('%s ReadOD ODStartLBA=%d ODEndLBA=%d StepLBA=%d SectCount=%d Pattern=0x%2X' % \
                                 (self.testName, ODStartLBA, ODEndLBA, StepLBA, SectCount, Pattern))
                  data = ICmd.SequentialReadDMA(ODStartLBA, ODEndLBA, StepLBA, SectCount, StampFlag, CompFlag, timeout=self.timeout, exc=0)
                  result = data['LLRET']
               if result == OK:
                  objMsg.printMsg('%s ReadID IDStartLBA=%d IDEndLBA=%d StepLBA=%d SectCount=%d Pattern=0x%2X' % \
                                 (self.testName, IDStartLBA, IDEndLBA, StepLBA, SectCount, Pattern))
                  data = ICmd.SequentialReadDMA(IDStartLBA, IDEndLBA, StepLBA, SectCount, StampFlag, CompFlag, timeout=self.timeout, exc=0)
                  result = data['LLRET']

            self.testCmdTime += float(data.get('CT','0'))/1000
            result = data['LLRET']
            if result != OK:
               objMsg.printMsg("%s SequentialReadDMA Failed - Data: %s" % (self.testName, data))
            else:
               objMsg.printMsg("%s SequentialReadDMA Passed - Data: %s" % (self.testName, data))
         if B_Msg or result != OK:
            objMsg.printMsg('%s Read Buffer Data ----------------------------------------' % TestName)
            rb_data = ICmd.GetBuffer(RBF, 0, 550)['DATA']
            objMsg.printMsg('%s %s' % (self.testName, rb_data[0:20]))
            objMsg.printMsg('%s %s' % (self.testName, rb_data[512:532]))

         # DT141010
         #objMsg.printMsg('Restore Primary Buffer')
         #ICmd.RestorePrimaryBuffer(WBF)
         self.displayCmdTimes(self.testName,'CPC',self.testCmdTime,self.sectorCount)
         if result == OK:
            if P_Msg:
                  BlocksXfrd=TotalLBA;NumCmds=(TotalLBA/SectCount)
                  self.displayPerformance(TestName,NumCmds,BlocksXfrd,BlockSize,self.testCmdTime)
            objMsg.printMsg('%s Test Passed' % self.testName)
         else:
            objMsg.printMsg('%s Failed Result=%s Data=%s' % (self.testName, result, data))

            raise gioTestException(data)

         return result

      #---------------------------------------------------------------------------------------------------------#
      def doIdleAPMTest(self, TestType='IDT'):
         P_Msg = ON      # Performance Message
         F_Msg = ON      # Failure Message
         B_Msg = ON      # Buffer Message
         mode2848 = 48
         data = {}
         result = OK
         DoRetry = ON

         TestName = ('Idle APM Test')                       # Test Name for file formatting
         #driveattr['testseq'] = TestName.replace(' ','_')
         #driveattr['eventdate'] = time.time()
         self.testName = ('%s %s' % (TestType, TestName))


         if self.oRF.IDAttr['APM_MODE'] == 'OFF':
            IDLE_APM_TEST = OFF
         else:
            IDLE_APM_TEST = ON

         if IDLE_APM_TEST == ON:
            # Determine whether NVC is supported
            self.testCmdTime = 0
            self.printTestName(self.testName)
            if testSwitch.IO_MQM_SIC_TESTTIME_OPTIMIZATION and objRimType.IOInitRiser():
               self.oRF.powerCycle(useHardReset = 1)
            else:
               self.oRF.powerCycle()

   # DT
   #         NVCEnabled = 0
   #         NVCData = IdentifyDevice()
   #         objMsg.printMsg( "IDNVCEnabled: %s, IDNVCMaxLBA: %s"%(`NVCData.get( 'IDNVCEnabled','' )`,`NVCData.get( 'IDNVCMaxLBA','' )` ) )
   #         if NVCData.get( 'IDNVCEnabled','' ) and NVCData.get( 'IDNVCMaxLBA','' ):    #2bytes(Enabled?) + 8Bytes(LBA)
   #            NVCEnabled = ( ( (  NVCData['IDNVCEnabled']& 0x00F0)>>4 )&0x1 )
   #            objMsg.printMsg( "DRIVE SUPPORTS NVC:  %d (1-Yes/0-No)"%NVCEnabled )
   #         self.oRF.powerCycle()


            if result == OK:
               #StartTime(TestName, 'funcstart')
               #SetRdWrStatsIDE(TestName, 'On',CollectBER='ON')
               #TestNum = SetTestNumber(TestType)
               #SetIntfTimeout(ConfigVars['Intf Timeout'])
               ICmd.ReceiveSerialCtrl(1)
               UDMA_Speed = 0x45
               Pattern = 0x00                                            # Number of MegaBytes
               StepLBA = 256
               SectCount = 256
               StampFlag = 0
               CompFlag = 1
               StartLBA = 0

               if self.oRF.IDAttr['APM_MODE'] == 'ON':
                  apmDrive = 1
                  apmMsg = 'supported'
                  objMsg.printMsg('%s APM supported' % TestName)
               else:
                  apmDrive = 0
                  apmMsg = 'not supported'
                  objMsg.printMsg('%s APM Not supported' % TestName)

               minLBA = 0 #ID_data['Min_lba']
               objMsg.printMsg('%s minLBA: %s' % (TestName, minLBA))
               #Change all idleAPM modules with MaxLBA = 200,000 LBA
               #As per TechKhoon request- MQM_UNF21D2_4 (Base:MQM_UNF21D2_3) - 18-Jan-2012
               #maxLBA = self.oRF.IDAttr['MaxLBA'] - 256
               maxLBA = 200000
               objMsg.printMsg('%s maxLBA: %s' % (TestName, maxLBA))
               loopTime = 900
               objMsg.printMsg('%s Loop Time: %d sec' % (TestName,loopTime))
               apmWaitMin = 30
               apmWaitMax = 600
               napmWait = 7
               udmaSpeed = 0x45

               if ConfigVars[CN].has_key('MOA SDOD LUL') and ConfigVars[CN]['MOA SDOD LUL'] != UNDEF and ConfigVars[CN]['MOA SDOD LUL'] == 'ON':
                  MOA_SDOD = ON
               else:
                  MOA_SDOD = OFF

               objMsg.printMsg('%s APM is %s, StartLBA=%d, EndLBA=%d, LoopTime=%d sec, apmWaitMin=%d, apmWaitMax=%d, napmWait=%d, UDMA_Speed=0x%X' % \
                      (TestName, apmMsg, minLBA, maxLBA, loopTime, apmWaitMin, apmWaitMax, napmWait, udmaSpeed))

               Retry = 1
               for loop in range(Retry+1):

   #               if result == OK and NVCEnabled:
   #                  objMsg.printMsg('%s NV Cache PM Supported, Set Power Management Mode' % TestName)
   #                  data = PassThroughExt(0,0xB6,0,0x05,0x00,0)
   #                  result = data['LLRET']
   #                  if result != OK:
   #                     objMsg.printMsg('%s Set Power Management Mode Failed, Returned Msg: %s' % (TestName,data))
                  if result == OK:
                     # DT081008 IdleAPMTest with LULSTB
                     if self.oRF.IDAttr['Support48Bit'] == 'ON':
                        mode2848 = 48
                     else:
                        mode2848 = 28
                     if MOA_SDOD == ON:
                        # DT200709 Improve IdleAPM + LUL
                        LULSTBWait = 300      # sec

                        objMsg.printMsg('%s SDOD LUL is ON, Enable LULSTB in IdleAPMTest' % TestName)
                        objMsg.printMsg('%s with LULSTB, StartLBA=%d, EndLBA=%d, LoopTime=%d sec, apmWaitMin=%d, apmWaitMax=%d, napmWait=%d, UDMA_Speed=0x%X, 2848mode=%d, LULSTBWait=%d' % \
                               (TestName, minLBA, maxLBA, loopTime, apmWaitMin, apmWaitMax, napmWait, udmaSpeed, mode2848, LULSTBWait))

                        data = ICmd.IdleAPMTest(apmDrive,minLBA,maxLBA,loopTime,apmWaitMin,apmWaitMax,napmWait,udmaSpeed,mode2848,0xB5B5,LULSTBWait)
                     else:   # normal IdleAPMTest w/o LULSTB
                        data = ICmd.IdleAPMTest(apmDrive,minLBA,maxLBA,loopTime,apmWaitMin,apmWaitMax,napmWait,udmaSpeed,mode2848)

                     result = data['LLRET']
                     if result != OK:
                        objMsg.printMsg('%s Failed, Returned Data=%s' % (TestName, data))
   #               if result == OK and NVCEnabled:
   #                  objMsg.printMsg('%s NV Cache PM Supported, Return from Power Management Mode' % TestName)
   #                  data = PassThroughExt(0,0xB6,0,0,0x01,0)
   #                  result = data['LLRET']
   #                  if result != OK:
   #                     objMsg.printMsg('%s Return from Power Management Mode Failed, Returned Msg: %s' % (TestName,data))
                  if result != OK and DoRetry == ON:
                     RetryTest = self.checkRetryTest(data['RESULT'], data.get('STS','NIL'), data.get('ERR','NIL'))
                     if RetryTest != ON: break
                     # DT070709 LLRetry
                     objMsg.printMsg('CPCIdleAPMTest - Loop Number %d of %d Failed - Do Retry' % (loop+1, Retry+1))
                     objMsg.printMsg('CPCIdleAPMTest - Retry - Power Cycle and Re-issue CPC Embedded Command')
                     self.getSerialPortData()
                     self.oRF.powerCycle()
                     #if result == OK:
                        #SetRdWrStatsIDE(TestName, 'On')
                     #else: break
                     if result != OK: break
                  else: break

            if result != OK:
               objMsg.printMsg('%s Failed Result=%s Data=%s' % (TestName, result, data))
               raise gioTestException(data)

            else:
               objMsg.printMsg('%s Test Passed' % TestName)

            #EndTime(TestName, 'funcstart', 'funcfinish', 'functotal')
            #DisplayCmdTimes(TestName, 'CPC', float(data.get('CT',0))/1000, SectCount)

         else:
            objMsg.printMsg('%s Test OFF' % TestName)

         return result

      #-----------------------------------------------------------------------------------------#
      def doIdleAPM_TTR(self, TestType='IDT', TestName='IdleAPM_TTR'):
         D_Msg = ON
         T_Msg = ON
         result = OK
         #TestType = ('IDT')
         #TestName = ('IdleAPM_TTR')

         self.testName = ('%s %s' % (TestType, TestName))                       # Test Name for file formatting

         minLBA = 0
         maxLBA = self.oRF.IDAttr['MaxLBA']
         delay = 7
         sectCnt = 256
         loopCnt = 10      # original 10
         IDLEAPM_TTR = OFF

         if ConfigVars[CN].has_key('IdleAPM TTR') and ConfigVars[CN]['IdleAPM TTR'] != UNDEF and ConfigVars[CN]['IdleAPM TTR'] == 'ON':
            IDLEAPM_TTR = ON
         else:
            IDLEAPM_TTR = OFF

         if IDLEAPM_TTR == ON:

            self.testCmdTime = 0
            self.printTestName(self.testName)
            if result == OK:
               ICmd.ReceiveSerialCtrl(1)
               #driveattr['testseq'] = TestName.replace(' ','_')
               #driveattr['eventdate'] = time.time()
               objMsg.printMsg('10 Loops IdleAPM_TTR Delay=%d, MinLBA=%d, MaxLBA=%d, SectCount=%d, LoopCount=%d' % \
                              (delay, minLBA, maxLBA, sectCnt, loopCnt))

               for i in range(10):
                  ICmd.FlushCache()
                  #ICmd.IdleImmediate()   # DT290710 To replace with standbyImmed
                  ICmd.StandbyImmed()
                  #time.sleep(3)     # DT290710 To remove by request from DE
                  objMsg.printMsg('FlushCache and StandbyImmed')

                  #result = FinPowerOn(ON,'IDT')
                  #result = PowerCycleOffOn(off_time=6, on_time=0, Msg=ON)
                  #DriveOff(6)
                  #DriveOn(0)
                  self.oRF.powerCycleTimer(6, 0)


                  objMsg.printMsg('After PowerOn')

                  # DT270709 Add Unlocking for Trusted drive
   #               if result == OK:
   #                  if ConfigVars.has_key('Kwai Unlock') and ConfigVars['Kwai Unlock'] != UNDEF and ConfigVars['Kwai Unlock'] == 'ON':
   #                     UnlockDrive()


                  objMsg.printMsg('IdleAPM_TTR(%d) Delay=%d, MinLBA=%d, MaxLBA=%d, SectCount=%d, LoopCount=%d' % \
                                 (i+1, delay, minLBA, maxLBA, sectCnt, loopCnt))

                  data = ICmd.IdleAPM_TTR(delay, minLBA, maxLBA, sectCnt, loopCnt)
                  self.testCmdTime += float(data.get('CT','0'))/1000

                  result = data['LLRET']
                  if result != OK: break

               self.displayCmdTimes(self.testName,'CPC',self.testCmdTime,self.sectorCount)
               if result == OK:
                  objMsg.printMsg('IdleAPM_TTR check passed! Result=%s' % result)
               else:

                  objMsg.printMsg('IdleAPM_TTR check failed! Data=%s, Result=%s' % (data, result))
                  raise gioTestException(data)

         return result

      #-----------------------------------------------------------------------------------------#
      def doSTMIdle(self, TestType='IDT', TestName='STM IDLE'):
         D_Msg = ON
         T_Msg = ON
         result = OK
         #TestType = ('IDT')
         #TestName = ('STM IDLE')

         minLBA = 0
         maxLBA = self.oRF.IDAttr['MaxLBA']
         sectCnt = 256
         rndCnt = 10
         STM_IDLE = OFF
         STMIdleLoop = 3
         self.testName = ('%s %s' % (TestType, TestName))       # Test Name for file formatting
         ICmd.SetIntfTimeout(10000)

         if ConfigVars[CN].has_key('STM IDLE') and ConfigVars[CN]['STM IDLE'] != UNDEF and ConfigVars[CN]['STM IDLE'] == 'ON':
            STM_IDLE = ON
         else:
            STM_IDLE = OFF

         if STM_IDLE == ON:
            if ConfigVars[CN].has_key('STM IDLE LOOPCNT') and ConfigVars[CN]['STM IDLE LOOPCNT'] != UNDEF:
               STMIdleLoop = ConfigVars[CN].get('STM IDLE LOOPCNT', STMIdleLoop)


            self.testCmdTime = 0
            self.printTestName(self.testName)

            ICmd.ReceiveSerialCtrl(1)

            for i in range(STMIdleLoop):
               # DT090709 More preventive measures for aborted write
               ICmd.FlushCache()
               #ICmd.IdleImmediate()   # DT290710 To replace with standbyImmed
               ICmd.StandbyImmed()
               #time.sleep(3)     # DT290710 To remove by request from DE
               objMsg.printMsg('FlushCache and StandbyImmed')

               # DT110110
               #objMsg.printMsg('PowerOnOptions =%s ' % ConfigVars[CN]['Power On Options'])
               #DriveOff(3)  # power off and pause 3 sec

   #            if driveattr['SF_SpinUp_Congen'] == 'ON':
   #               SpinUpFlag = 0x0B
   #               objMsg.printMsg('PowerOnTiming SpinUpFlag =%s ' % SpinUpFlag)
   #               PowerOnTiming(30000, SpinUpFlag)

               self.oRF.powerCycleVoltageTimer(3, 0, 4750, 12000)
               #DriveOn(4750,12000) # power on with 4.75v and 12v

               # DT270709 Add Unlocking for Trusted Drive
   #            if ConfigVars[CN].has_key('Kwai Unlock') and ConfigVars[CN]['Kwai Unlock'] != UNDEF and ConfigVars[CN]['Kwai Unlock'] == 'ON':
   #               result = UnlockDrive()

               objMsg.printMsg('STMIdle Loop(%i) - Sleep 10min' % int(i+1))
               time.sleep(10*60)    # sleep for 10min
               ICmd.ClearBinBuff(RBF)

               if result == OK:
                  # DT160410 Replace with 48bit RandomReadDMAExt
                  #data = ICmd.RandomReadDMA(100, maxLBA - 256, sectCnt, sectCnt, rndCnt)   # random read 10x
                  data = ICmd.RandomReadDMAExt(100, maxLBA - 256, sectCnt, sectCnt, rndCnt)   # random read 10x
                  result = data['LLRET']
                  objMsg.printMsg('RandomRead 10 times, Data=%s Result=%d' % (data, result))

               if result != OK:
                  objMsg.printMsg('RandomRead failed, STMIdle loop aborted.')
                  break

            if result == OK:
               # DT090709 More preventive measures for aborted write
               ICmd.FlushCache()
               #ICmd.IdleImmediate()   # DT290710 To replace with standbyImmed
               ICmd.StandbyImmed()
               #time.sleep(3)     # DT290710 To remove by request from DE
               objMsg.printMsg('FlushCache and StandbyImmed')
               self.oRF.powerCycle()
               #DriveOff()
               #objMsg.printMsg('Drive power off!')
               objMsg.printMsg('STM_Idle check passed! Result=%s' % result)
               #DriveOn()

            else:
               objMsg.printMsg('STM_Idle check failed! Data=%s, Result=%s' % (data, result))
               raise gioTestException(data)

            #EndTime(TestName, 'funcstart', 'funcfinish', 'functotal')


         return result


      #---------------------------------------------------------------------------------------------------------#
      # DT081110 Modified SDOD serial function calls
      def doSerialSDODCheck(self, TestType='IDT', TestName='SDOD CHECK'):
         D_Msg = ON
         T_Msg = ON
         data = {}
         result = FAIL
         #TestType = ('IDT')
         #TestName = ('SDOD CHECK')
         self.testName = ('%s %s' % (TestType, TestName))                       # Test Name for file formatting
         SERIAL_SDOD = ON  #OFF
         retry = OFF

         timeout = 60  # serial timeout
         ICmd.SetIntfTimeout(10000)

         # DT301110 Remove all CMS switch
   #      if ConfigVars[CN].has_key('SDOD Spin Check') and ConfigVars[CN]['SDOD Spin Check'] != UNDEF and ConfigVars[CN]['SDOD Spin Check'] == 'ON':
   #         SERIAL_SDOD = ON
   #      else:
   #         SERIAL_SDOD = OFF

         if SERIAL_SDOD == ON:
            self.testCmdTime = 0
            self.printTestName(self.testName)
            #ICmd.ReceiveSerialCtrl(1)

            self.oRF.powerCycle('TCGUnlock')
            self.oRF.disableAPM(self.testName)

            sptCmds.enableDiags()

            for i in range(2):
               objMsg.printMsg('%s Initiating Serial SDOD, Attempt = %s' % (TestName, i+1))
               try:
                  #data = ICmd.Ctrl('Z', matchStr='T>')
                  data = sptCmds.execOnlineCmd(CTRL_Z, timeout = timeout, waitLoops = 100)
                  #objMsg.printMsg('%s Ctrl Z Data=%s' % (TestName, data))

                  #data = ICmd.SerialCommand('/2\r', matchStr='F3 2>')
                  sptCmds.gotoLevel('2')

                  #RT070711: spindown the drive first
                  data = sptCmds.sendDiagCmd("Z\r",timeout = timeout, printResult = True, loopSleepTime=0)

                  #data = ICmd.SerialCommand('U5\r', matchStr='F3 2>')
                  data = sptCmds.sendDiagCmd("U5\r",timeout = timeout, printResult = True, loopSleepTime=0)
                  #objMsg.printMsg('%s SerialCmd U5(Spinup) Data=%s' % (TestName, data))

                  #data = ICmd.SerialCommand('Z\r', matchStr='F3 2>')
                  data = sptCmds.sendDiagCmd("Z\r",timeout = timeout, printResult = True, loopSleepTime=0)
                  #objMsg.printMsg('%s SerialCmd Z(Spindown) Data=%s' % (TestName, data))

                  #data = ICmd.SerialCommand('U3\r', matchStr='F3 2>')
                  data = sptCmds.sendDiagCmd("U3\r",timeout = timeout, printResult = True, loopSleepTime=0)
                  #objMsg.printMsg('%s SerialCmd U3(Spinup) Data=%s' % (TestName, data))

                  #data = ICmd.SerialCommand('Z\r', matchStr='F3 2>')
                  data = sptCmds.sendDiagCmd("Z\r",timeout = timeout, printResult = True, loopSleepTime=0)
                  #objMsg.printMsg('%s SerialCmd Z(Spindown) Data=%s' % (TestName, data))
               except Exception, e:
                  objMsg.printMsg("Serial Port Exception data : %s"%e)
                  objMsg.printMsg('%s Serial SDOD Check failed attempt %d' % (TestName, i+1))

               else:
                  result = OK
                  objMsg.printMsg('%s Serial SDOD Check Passed' % TestName)
                  break

            # end retry loop
            if result != OK:
               objMsg.printMsg('%s Serial SDOD Check Failed' % TestName)
               raise gioTestException(data)

            #EndTime(TestName, 'funcstart', 'funcfinish', 'functotal')

         return result

      #--------------------------------  Start DST Test  ---------------------------------------#
      def DSTStart(self,DST_Test):
         data = ICmd.SmartEnableOper()
         result = data['LLRET']

         if result != OK:
            objMsg.printMsg('SMART Start failed - SmartEnableOper() - result = %d' % result)
            #self.driveAttr['failcode'] = failcode['Fin DST Start']
            failure = 'Fin DST Start'
            self.failCode = self.oFC.getFailCode(failure)
            return {'RESULT':FAIL}, data

         result = self.GetDSTLogIndex()

         if result['RESULT'] == FAIL:
            return {'RESULT':FAIL}, data
         else:
            log_index = result['DST_LOG_INDEX']

         result = self.GetDSTTimeout(DST_Test)

         if result['RESULT'] == FAIL:
            return {'RESULT':FAIL}, data
         else:
            timeout = result['DST_TIMEOUT']
            if DST_Test == 1 and ConfigVars[CN].has_key('Short DST Timeout'):
               timeout = ConfigVars[CN]['Short DST Timeout']
               objMsg.printMsg('Short DST Timeout reset to %d Seconds according to CMS' % timeout)

         data = ICmd.SmartOffLineImmed(DST_Test)
         result = data['LLRET']

         if result != OK:
            objMsg.printMsg('SMART Start failed - SmartOffLineImmed(%d): data=%s' % (DST_Test, data))
            #self.driveAttr['failcode'] = failcode['Fin DST Start']
            failure = 'Fin DST Start'
            self.failCode = self.oFC.getFailCode(failure)

            return {'RESULT':FAIL}, data

         # set drive timeout to 30 sec.

         return {'RESULT':OK,'DST_LOG_INDEX':log_index,'DST_TIMEOUT':timeout}, data

      #---------------------------------------------------------------------------------------------------------#
      def doMOASDODCheck(self, TestType='IDT', TestName='MOA SDOD LUL'):
         D_Msg = ON
         T_Msg = ON
         data = {}

         #TestType = ('IDT')
         #TestName = ('MOA SDOD LUL')
         self.testName = ('%s %s' % (TestType, TestName))                       # Test Name for file formatting
         result = OK

         Delay = 100         # ms
         LoopNum = 6
         MaxDelay = LoopNum * Delay     # default
         LULLoop = 1000
         RndLoop = 100

         minLBA = 0 #ID_data['Min_cyl' ]
         maxLBA = self.oRF.IDAttr['MaxLBA']
         SectCnt = 256
         minSectCnt = SectCnt
         maxSectCnt = SectCnt
         StepLBA = SectCnt
         StdbyImmedMode = 0xE0
         IdleImmedMode = 0xE1
         SleepMode = 0xE6
         MaxOD = long(0.08 * maxLBA)
         MinID = long(0.92 * maxLBA)
         ReadDMAExtOpCode = 0x25
         ReadMultiExtOpCode = 0x29
         ReadSectExtOpCode = 0x24
         ReadVerifyExtOpCode = 0x42
         WriteDMAExtOpCode = 0x35
         WriteMultiExtOpCode = 0x39
         WriteSectExtOpCode = 0x34
         odCount = 10000
         idCount = 10000
         cycleCount = 2
         StampFlag = 0
         CompFlag = 0
         NumWrites = 25000   #250000

         ICmd.SetIntfTimeout(10000)
         ICmd.SetSerialTimeout(10000)

         if ConfigVars[CN].has_key('MOA SDOD LUL') and ConfigVars[CN]['MOA SDOD LUL'] != UNDEF and ConfigVars[CN]['MOA SDOD LUL'] == 'ON':
            MOA_SDOD = ON
         else:
            MOA_SDOD = OFF

         if ConfigVars[CN].has_key('MOA SDOD LOOPCNT') and ConfigVars[CN]['MOA SDOD LOOPCNT'] != UNDEF:
            LULLoop = ConfigVars[CN].get('MOA SDOD LOOPCNT', LULLoop)

         if ConfigVars[CN].has_key('MOA SDOD RNDCNT') and ConfigVars[CN]['MOA SDOD RNDCNT'] != UNDEF:
            RndLoop = ConfigVars[CN].get('MOA SDOD RNDCNT', RndLoop)

         # Control number of loops in each LUL
         if ConfigVars[CN].has_key('MOA SDOD LOOPNUM') and ConfigVars[CN]['MOA SDOD LOOPNUM'] != UNDEF:
            LoopNum = ConfigVars[CN].get('MOA SDOD LOOPNUM', LoopNum)
            MaxDelay = LoopNum * Delay

         if MOA_SDOD == ON:

            #StartTime( TestName, 'funcstart')
            self.testCmdTime = 0
            self.printTestName(self.testName)
            self.oRF.powerCycle()


            ICmd.ReceiveSerialCtrl(1)
            #driveattr['testseq'] = TestName.replace(' ','_')
            #driveattr['eventdate'] = time.time()

            objMsg.printMsg('%s LUL LoopNumber=%d, LoopCount=%d, RandomCount=%d' % (TestName, LoopNum, LULLoop, RndLoop))
            # LULSTB loop

            if result == OK:
               objMsg.printMsg('%s LULSTB Loop, time start = %.2f' % (TestName, time.time()/3600))
               objMsg.printMsg('%s Mode=0x%X Delay=%d MaxDelay=%d minLBA=%d maxLBA=%d' % \
                      (TestName, StdbyImmedMode, Delay, MaxDelay, minLBA, maxLBA))
               objMsg.printMsg('%s minSectCnt=%d maxSectCnt=%d rndLoop=%d LULLoop=%d' % \
                      (TestName, minSectCnt, maxSectCnt, RndLoop, LULLoop))

               #data = CPCSDOD_LUL(IdleImmedMode,Delay,MaxDelay,minLBA,maxLBA,minSectCnt,maxSectCnt,RndLoop,LULLoop)
               data = ICmd.SDOD_LUL(StdbyImmedMode,Delay,MaxDelay,minLBA,maxLBA,minSectCnt,maxSectCnt,RndLoop,LULLoop)
               self.testCmdTime += float(data.get('CT','0'))/1000
               result = data['LLRET']
               if result == OK:
                  objMsg.printMsg('%s LULSTB passed' % TestName)
               else:

                  objMsg.printMsg('%s LULSTB failed. Result=%s Data=%s' % (TestName, result, data))
                  result = FAIL
                  raise gioTestException(data)
            # End LULSTB loop

            # LULSLP Loop
   #       if result == OK:
   #          objMsg.printMsg('%s LULSLP Loop' % TestName)
   #          objMsg.printMsg('%s Mode=0x%X Delay=%d MaxDelay=%d minLBA=%d maxLBA=%d' % \
   #                 (TestName, SleepMode, Delay, MaxDelay, minLBA, maxLBA))
   #          objMsg.printMsg('%s minSectCnt=%d maxSectCnt=%d rndLoop=%d LULLoop=%d' % \
   #                 (TestName, minSectCnt, maxSectCnt, RndLoop, LULLoop))
   #
   #          data = CPCSDOD_LUL(SleepMode,Delay,MaxDelay,minLBA,maxLBA,minSectCnt,maxSectCnt,RndLoop,LULLoop)
   #          result = data['LLRET']
   #          if result == OK:
   #             objMsg.printMsg('%s LULSLP passed' % TestName)
   #          else:
   #             objMsg.printMsg('%s LULSLP failed. Result=%s Data=%s' % (TestName, result, data))
   #             if data.has_key('LBA') == 0: data['LBA'] = '0'
   #             if data.has_key('STS') == 0: data['STS'] = '00'
   #             if data.has_key('ERR') == 0: data['ERR'] = '00'
   #             driveattr['faillba'] = data['LBA']
   #             failure = ('%s %s' % (TestType, TestName))
   #             driveattr['failcode'] = failcode[failure]
   #             failstatus = ('%s-%s-%s' % (driveattr['failcode'][0],int(data['STS']),int(data['ERR'])))
   #             driveattr['failstatus'] = failstatus
   #             result = FAIL
            # End LULSLP loop

            #-----------------------------------------------------------------------------
            # ID/OD Stressor test
            #-----------------------------------------------------------------------------

            if result == OK:
               objMsg.printMsg('%s ID/OD Stressor Test' % TestName)
               # RandomWriteDMAExt for 10min
               data = ICmd.StopCmdOnTime(10,0)    # original - StopCmdOnTime(30,0)
               result = data['LLRET']

               objMsg.printMsg('%s RandomWriteDMAExt 10min TimeStamp=%.2f minLBA=%d maxLBA=%d minSectCnt=%d maxSectCnt=%d NumWrites=%d' % \
                      (TestName, time.time()/3600, minLBA, maxLBA, minSectCnt, maxSectCnt, NumWrites))
               data = ICmd.RandomWriteDMAExt(minLBA, maxLBA, minSectCnt, maxSectCnt, NumWrites)
               self.testCmdTime += float(data.get('CT','0'))/1000
               result, timeout = data['LLRET'], data['RESULT']
               if result == -1 and timeout == 'IFX_USERABORT:User abort':
                  objMsg.printMsg('%s RandomWriteDMAExt 10min lapsed/passed, Result=%s Data=%s' % (TestName, result, data))
                  result = OK
               elif result == -1:
                  objMsg.printMsg('%s RandomWriteDMAExt 10min failed, Result=%s Data=%s' % (TestName, result, data))
               elif result == OK:
                  objMsg.printMsg('%s RandomWriteDMAExt 10min passed, Result=%s Data=%s' % (TestName, result, data))

            # SequentialReadDMAExt ID
            if result == OK:
               objMsg.printMsg('%s SeqReadDMAExt-ID TimeStamp=%.2f MinID=%d maxLBA=%d StepLBA=%d SectCnt=%d StampFlag=%d CompFlag=%d' % \
                      (TestName, time.time()/3600, MinID, maxLBA, StepLBA, SectCnt, StampFlag, CompFlag))
               data = ICmd.SequentialReadDMAExt(MinID, maxLBA, StepLBA, SectCnt, StampFlag, CompFlag)
               self.testCmdTime += float(data.get('CT','0'))/1000
               result = data['LLRET']
               if result != OK:
                  objMsg.printMsg('%s SeqReadDMAExt-ID failed, Result=%s Data=%s' % (TestName, result, data))
               else:
                  objMsg.printMsg('%s SeqReadDMAExt-ID passed' % TestName)

            # RandomFullStrokeWrite OD/ID for 15min
            if result == OK:
               data = ICmd.StopCmdOnTime(15,0)    # original - StopCmdOnTime(30,0)
               result = data['LLRET']
               objMsg.printMsg('%s RndFullStrokeWrite 15min TimeStamp=%.2f MaxOD=%d MinID=%d minSectCnt=%d maxSectCnt=%d odCnt=%d idCnt=%d CycCnt=%d' % \
                      (TestName, time.time()/3600, MaxOD, MinID, minSectCnt, maxSectCnt, odCount, idCount, cycleCount))

               data = ICmd.RandomFullStroke(WriteDMAExtOpCode, MaxOD, MinID, minSectCnt, maxSectCnt, odCount, idCount, cycleCount)
               self.testCmdTime += float(data.get('CT','0'))/1000
               result, timeout = data['LLRET'], data['RESULT']
               if result == -1 and timeout == 'IFX_USERABORT:User abort':
                  objMsg.printMsg('%s RandomFullStrokeWrite OD/ID 15min lapsed/passed, Result=%s Data=%s' % (TestName, result, data))
                  result = OK
               elif result == -1:
                  objMsg.printMsg('%s RandomFullStrokeWrite OD/ID 15min failed, Result=%s Data=%s' % (TestName, result, data))
               elif result == OK:
                  objMsg.printMsg('%s RandomFullStrokeWrite OD/ID 15min passed, Result=%s Data=%s' % (TestName, result, data))


            # SequentialReadDMAExt OD
            if result == OK:
               objMsg.printMsg('%s SeqReadDMAExt-OD TimeStamp=%.2f minLBA=%d MaxOD=%d StepLBA=%d SectCnt=%d StampFlag=%d CompFlag=%d' % \
                      (TestName, time.time()/3600, minLBA, MaxOD, StepLBA, SectCnt, StampFlag, CompFlag))

               data = ICmd.SequentialReadDMAExt(minLBA, MaxOD, StepLBA, SectCnt, StampFlag, CompFlag)
               self.testCmdTime += float(data.get('CT','0'))/1000
               result = data['LLRET']
               if result != OK:
                  objMsg.printMsg('%s SequentialReadDMAExt OD failed, Result=%s Data=%s' % (TestName, result, data))
               else:
                  objMsg.printMsg('%s SeqReadDMAExt-OD passed' % TestName)

            # SequentialReadDMAExt ID
            if result == OK:
               objMsg.printMsg('%s SeqReadDMAExt-ID TimeStamp=%.2f MinID=%d maxLBA=%d StepLBA=%d SectCnt=%d StampFlag=%d CompFlag=%d' % \
                      (TestName, time.time()/3600, MinID, maxLBA, StepLBA, SectCnt, StampFlag, CompFlag))

               data = ICmd.SequentialReadDMAExt(MinID, maxLBA, StepLBA, SectCnt, StampFlag, CompFlag)
               self.testCmdTime += float(data.get('CT','0'))/1000
               result = data['LLRET']
               if result != OK:
                  objMsg.printMsg('%s SequentialReadDMAExt ID failed, Result=%s Data=%s' % (TestName, result, data))
               else:
                  objMsg.printMsg('%s SequentialReadDMAExt ID passed' % TestName)

            self.displayCmdTimes(self.testName,'CPC',self.testCmdTime,self.sectorCount)
            if result == OK:
               objMsg.printMsg('%s ID Stressor Test passed' % TestName)
            else:
               objMsg.printMsg('%s ID Stressor Test failed' % TestName)
               result = FAIL
               raise gioTestException(data)

            # End all
            #EndTime(TestName, 'funcstart', 'funcfinish', 'functotal')

         return result

      #---------------------------------------------------------------------------------------------------------#
      # DT241110 Mod Delay Write
      # Change start LBA to random
      # Delay change from 100 - 900 to 200 - 400ms
      # Write 1000x of 4*256 LBA each
      #---------------------------------------------------------------------------------------------------------#
      def doDelayWrite(self, TestType='IDT', TestName='DELAYWRT'):
         D_Msg = ON
         T_Msg = ON
         result = OK
         #TestType = ('IDT')
         #TestName = ('DELAYWRT')
         self.testName = ('%s %s' % (TestType, TestName))                       # Test Name for file formatting

         #minLBA = 5000000
         #maxLBA = 10000000   #ID_data['Max_48lba']

         minLBA = startLBA = endLBA = 0
         maxLBA = self.oRF.IDAttr['MaxLBA']

         stepLBA = 256
         sectCnt = 256

         DELAYWRT = ON
         #DelayWrtLoop = 1
         DelayWrtLoop = 1000
         #Pattern = 0x22
         StampFlag = 0
         #minDelay = 100  #ms
         minDelay = 200  #ms
         # DT181110
         #maxDelay = 900  #ms
         #maxDelay = 2000  #ms
         maxDelay = 400  #ms
         stepDelay = 100 #ms
         #GrpCnt = 200
         GrpCnt = 1
         #LBAMode = 28    # from 5M to 10M
         LBAMode = 48     # not use
         DelayStepLba = ((maxDelay - minDelay) / stepDelay + 2) * sectCnt * GrpCnt    #+2 to ensure all delay time execute.

         ICmd.SetIntfTimeout(5000)        # Interface timout 5 sec

   #      if ConfigVars[CN].has_key('DELAY WRT') and ConfigVars[CN]['DELAY WRT'] != UNDEF and ConfigVars[CN]['DELAY WRT'] == 'ON':
   #         DELAYWRT = ON
   #      else:
   #         DELAYWRT = OFF

         if DELAYWRT == ON:
            self.testCmdTime = 0
            self.printTestName(self.testName)

            #SetRdWrStatsIDE(TestName, 'On')
            ICmd.ReceiveSerialCtrl(1)
            #driveattr['testseq'] = TestName.replace(' ','_')
            #driveattr['eventdate'] = time.time()

            if result == OK:
               self.oRF.powerCycle()

            # set APM to C0
            if result == OK:
               data = ICmd.SetFeatures(0x05, 0xC0)
               result = data['LLRET']
               objMsg.printMsg('%s Set APM to 0xC0. Result=%s Data=%s' % (TestName, result, data))

            # disable write cache
            if result == OK:
               data = ICmd.SetFeatures(0x82)
               result = data['LLRET']
               objMsg.printMsg('%s Disable write cache. Result=%s Data=%s' % (TestName, result, data))

            # disable read look ahead
            if result == OK:
               data = ICmd.SetFeatures(0x55)
               result = data['LLRET']
               objMsg.printMsg('%s Disable read look-ahead. Result=%s Data=%s' % (TestName, result, data))

            for i in range(DelayWrtLoop):
               if result == OK:
                  # DT181110 Set random start LBA
                  #startLBA = random.randint(minLBA, maxLBA)
                  startLBA = random.randint(minLBA, maxLBA - DelayStepLba)
                  objMsg.printMsg('%s Randomised StartLBA=%d' % (TestName, startLBA))
                  # DT181110 Apply 4K alignment
                  # DT170909 Apply offset calculation for multi-sector drive
                  if self.oRF.IDAttr['NumLogSect'] > 1:
                     # Adjust for number of physical sector per logical sector
                     startLBA = startLBA - (startLBA % self.oRF.IDAttr['NumLogSect'])
                     #objMsg.printMsg('%s Adjust for multi-sector drive, LogSect/PhySect=%d' % (TestName, self.oRF.IDAttr['NumLogSect']))
                     if self.oRF.IDAttr['OffSetLBA0'] > 0:
                        objMsg.printMsg('%s Adjust for LogBlk in PhyBlk alignment, offset=%d' % (TestName, self.oRF.IDAttr['OffSetLBA0']))
                        if startLBA == 0:    # Avoid negative LBA range, proceed to next block
                           startLBA = startLBA + self.oRF.IDAttr['NumLogSect']
                        # Adjust for alignment of Log Block in Phy Block
                        startLBA = startLBA - self.oRF.IDAttr['OffSetLBA0']

                  objMsg.printMsg('%s Adjusted StartLBA=%d' % (TestName, startLBA))
                  #endLBA = startLBA + 5000000
                  endLBA =  startLBA + DelayStepLba

                  # DT181110
                  #objMsg.printMsg('%s StartLBA=%d EndLBA=%d SectCnt=%d MinDelay=%d MaxDelay=%d StepDelay=%d GrpCnt=%d' % \
                  #               (TestName, minLBA, maxLBA, sectCnt, minDelay, maxDelay, stepDelay, GrpCnt))
                  objMsg.printMsg('%s StartLBA=%d EndLBA=%d SectCnt=%d MinDelay=%d MaxDelay=%d StepDelay=%d GrpCnt=%d' % \
                                 (TestName, startLBA, endLBA, sectCnt, minDelay, maxDelay, stepDelay, GrpCnt))
                  # DT020610 Use 48bit
                  #data = ICmd.SeqDelayWR(minLBA, maxLBA, sectCnt, minDelay, maxDelay, stepDelay, GrpCnt, LBAMode)
                  # DT181110 Mod Delay Write
                  #data = ICmd.SeqDelayWR(minLBA, maxLBA, sectCnt, minDelay, maxDelay, stepDelay, GrpCnt)
                  data = ICmd.SeqDelayWR(startLBA, endLBA, sectCnt, minDelay, maxDelay, stepDelay, GrpCnt)
                  result = data['LLRET']

               if result != OK:
                  objMsg.printMsg('%s SeqDelayWR failed. Result=%s Data=%s' % (TestName, result, data))
                  break

            self.testCmdTime += float(data.get('CT','0'))/1000
            self.displayCmdTimes(self.testName,'CPC',self.testCmdTime,self.sectorCount)
            if result == OK:
               objMsg.printMsg('Delay Write test passed!')

            else:
               objMsg.printMsg('Delay Write test failed!')
               raise gioTestException(data)

            #EndTime(TestName, 'funcstart', 'funcfinish', 'functotal')

         return result

      #-------------------------------------------------------------------------------------------------------
      def ReadScan(self, TestName, IDStartLBA, ODStartLBA, blockSize, SectCount):

         StampFlag = 0
         CompareFlag = 0
         result = OK

         self.oRF.powerCycle()

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
      def doMSSustainTferRate(self, TestType='IDT', TestName='MSSTR'):

         result = OK
         loop = 2
         MS_SUS_TXFER_RATE = ON

         objMsg.printMsg('CGIOTest.py doMSSustainTferRate - CPC')

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
                     objMsg.printMsg('Re-run MSSTR')
                     loop -= 1 # re-run MSSTR
                  else:
                     break # UDE error, fail the drive
               else:
                  break # pass

            if result != OK:
               if testSwitch.virtualRun:
                  objMsg.printMsg('GIO Test Exception')
               else:
                  raise gioTestException(data)

         return result

      #---------------------------------------------------------------------------------------------------------#
      def doMSSustainTferRateTest(self, TestType='IDT', TestName='MSSTR'):
         D_Msg = ON      # Performance Message
         T_Msg = ON      # Failure Message
         data = {}
         #TestType = ('IDT')
         #TestName = ('MSSTR')
         self.testName = ('%s %s' % (TestType, TestName))                       # Test Name for file formatting
         result = OK
         STRLoop = 15  # 15
         # DT080410 change to 20K hex

         #blockSize = 0x5000      # 20480 sectors = 10M bytes
         blockSize = 0x20000      # change to 20K hex


         sectCnt = 256
         TxHead = 0
         TxRate = 0
         TxLBA = 0
         IDStartLBA = self.oRF.IDAttr['MaxLBA'] - blockSize
         ODStartLBA = 0
         #RT300311 Sync up with TGen1.3b5   # DT100111 Revised ID TxRate to 14
         IDTxRate = 14    #17
         ODTxRate = 30    #30
         MS_SUS_TXFER_RATE = ON

         #driveattr['testseq'] = TestName.replace(' ','_')

         if MS_SUS_TXFER_RATE == ON:

            #if result == OK:
               #StartTime(TestName, 'funcstart')
               #driveattr['eventdate'] = time.time()
               #SetRdWrStatsIDE(TestName, 'On')
               #ReceiveSerialCtrl(1)
            self.testCmdTime = 0
            self.printTestName(self.testName)

            self.oRF.powerCycle()
            # DT251109 Add FlushCache to make throughput measurement correct
            ICmd.FlushCache()

            if result == OK:
               objMsg.printMsg('%s (ID)StartLBA=%d (OD)StartLBA=%d BlockSize=%d SectCnt=%d' % \
                              (TestName, IDStartLBA, ODStartLBA, blockSize, sectCnt))

               if testSwitch.virtualRun:
                  result = OK # dummy test

                  if result == OK:
                     objMsg.printMsg('%s STR Test passed!' % TestName)
                  else:
                     objMsg.printMsg('%s Test failed!' % self.testName)
                  return (result, data, TestName, IDStartLBA, ODStartLBA, blockSize, sectCnt)

               for i in range(1, STRLoop+1):

                  # read ID
                  if result == OK:
                     data = ICmd.ReadDMAExtTransRate(IDStartLBA, blockSize, sectCnt)
                     result = data['LLRET']

                  if result != OK:
                     objMsg.printMsg('%s Read(ID)(%d) failed. Result=%s Data=%s' % (TestName, i, result, data))
                     break
                  else:
                     TxRate = int(data['TXRATE'])
                     readIDRate = TxRate
                     TxHead = int(data['DEV'])
                     TxLBA = data['ENDLBA']      # string
                     objMsg.printMsg('%s Read(ID)(%d) TxRate=%d MB/s TxHead=%d LastLBA=%s' % (TestName, i, TxRate, TxHead, TxLBA))

                     if TxRate >= IDTxRate:
                        objMsg.printMsg('%s Read(ID) passed. TxRate=%d MB/s' % (TestName, TxRate))
                     else:
                        objMsg.printMsg('%s Read(ID) TxRate(%d MB/s)<%d, Test failed! TxHead=%d Data=%s' % (TestName, TxRate, IDTxRate, TxHead, data))
                        #objMsg.printMsg('%s Read(ID) failed! TxRate(%d MB/s) < %d, TxHead=%d, TxLBA=%d' % (TestName, TxRate, IDTxRate, TxHead, TxLBA))
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
                     TxRate = int(data['TXRATE'])
                     readODRate = TxRate
                     TxHead = int(data['DEV'])
                     TxLBA = data['ENDLBA']
                     objMsg.printMsg('%s Read(OD)(%d) TxRate=%d MB/s TxHead=%d LastLBA=%s' % (TestName, i, TxRate, TxHead, TxLBA))

                     if TxRate >= ODTxRate:
                        objMsg.printMsg('%s Read(OD) passed. TxRate=%d MB/s' % (TestName, TxRate))
                     else:
                        objMsg.printMsg('%s Read(OD) TxRate(%d MB/s)<%d, Test failed! TxHead=%d Data=%s' % (TestName, TxRate, ODTxRate, TxHead, data))
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
                     TxRate = int(data['TXRATE'])
                     TxHead = int(data['DEV'])
                     TxLBA = data['ENDLBA']
                     objMsg.printMsg('%s Write(ID)(%d) TxRate=%d MB/s TxHead=%d LastLBA=%s' % (TestName, i, TxRate, TxHead, TxLBA))

                     if TxRate >= IDTxRate:
                        objMsg.printMsg('%s Write(ID) passed. TxRate=%d MB/s' % (TestName, TxRate))
                     else:
                        objMsg.printMsg('%s Write(ID) TxRate(%d MB/s)<%d, Test failed! TxHead=%d Data=%s' % (TestName, TxRate, IDTxRate, TxHead, data))
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
                     TxRate = int(data['TXRATE'])
                     TxHead = int(data['DEV'])
                     TxLBA = data['ENDLBA']
                     objMsg.printMsg('%s Write(OD)(%d) TxRate=%d MB/s TxHead=%d LastLBA=%s' % (TestName, i, TxRate, TxHead, TxLBA))

                     if TxRate >= ODTxRate:
                        objMsg.printMsg('%s Write(OD) passed. TxRate=%d MB/s' % (TestName, TxRate))
                     else:
                        objMsg.printMsg('%s Write(ID) TxRate(%d MB/s)<%d, Test failed! TxHead=%d Data=%s' % (TestName, TxRate, ODTxRate, TxHead, data))
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

   #               if data.has_key('LBA') == 0: data['LBA'] = '0'
   #               if data.has_key('STS') == 0: data['STS'] = '00'
   #               if data.has_key('ERR') == 0: data['ERR'] = '00'
   #
   #               self.currentStep = self.testName
   #               self.failLBA = data['LBA']
   #               self.failCode = self.oFC.getFailCode(self.testName)
   #               self.failLLRET = data['LLRET']
   #               self.failStatus = ('STS%s-ERR%s' % ( int(data['STS']), int(data['ERR']) ))

                  objMsg.printMsg('%s Test failed!' % self.testName)
                  ##raise gioTestException(data)

            #EndTime(TestName, 'funcstart', 'funcfinish', 'functotal')

         #return result
         return result, data, TestName, IDStartLBA, ODStartLBA, blockSize, sectCnt

      #---------------------------------------------------------------------------------------------------------#
      def doEncroachmentEUP(self, TestType='IDT', TestName='ENC EUP'):

         import random
         B_Msg = ON      # Buffer Message

         #TestType = ('IDT')
         #TestName = ('ENC EUP')
         self.testName = ('%s %s' % (TestType, TestName))                       # Test Name for file formatting
         result = OK
         data = {}

         stepLBA = 3024
         sectCnt = 256


         WrtLoop = 5000
         pattern = 0x0000#0xFAFA
         maxLBA = self.oRF.IDAttr['MaxLBA']

         #driveattr['testseq'] = TestName.replace(' ','_')
         ICmd.SetIntfTimeout(10000)

         ENCROACHMENT_EUP = ON

         if ENCROACHMENT_EUP == ON:
            self.testCmdTime = 0
            self.printTestName(self.testName)

            self.oRF.powerCycle()

            ICmd.ClearBinBuff(WBF)
            ICmd.FillBuffByte(WBF, pattern)

            if B_Msg:
               objMsg.printMsg('%s Write Buffer Data ----------------------------------------' % TestName)
               wb_data = ICmd.GetBuffer(WBF, 0, 550)['DATA']
               objMsg.printMsg('%s %s' % (TestName, wb_data[0:20]))
               objMsg.printMsg('%s %s' % (TestName, wb_data[512:532]))

            if result == OK:
               for i in range(1, WrtLoop+1):
                  startLBA = random.randint(0, maxLBA - 200000)
                  objMsg.printMsg('%s Randomised StartLBA=%d' % (TestName, startLBA))
                  # DT170909 Apply offset calculation for multi-sector drive
                  if self.oRF.IDAttr['NumLogSect'] > 1:
                     # Adjust for number of physical sector per logical sector
                     startLBA = startLBA - (startLBA % self.oRF.IDAttr['NumLogSect'])
                     #objMsg.printMsg('%s Adjust for multi-sector drive, LogSect/PhySect=%d' % (TestName, self.oRF.IDAttr['NumLogSect']))
                     if self.oRF.IDAttr['OffSetLBA0'] > 0:
                        objMsg.printMsg('%s Adjust for LogBlk in PhyBlk alignment, offset=%d' % (TestName, self.oRF.IDAttr['OffSetLBA0']))
                        if startLBA == 0:    # Avoid negative LBA range, proceed to next block
                           startLBA = startLBA + self.oRF.IDAttr['NumLogSect']
                        # Adjust for alignment of Log Block in Phy Block
                        startLBA = startLBA - self.oRF.IDAttr['OffSetLBA0']

                  endLBA = startLBA + 200000


                  objMsg.printMsg('%s Loop(%d) StartLBA=%d EndLBA=%d StepLBA=%d SectCnt=%d Pattern=%X' % \
                                 (TestName, i, startLBA, endLBA, stepLBA, sectCnt, pattern))

                  data = ICmd.SequentialWriteDMAExt(startLBA, endLBA, stepLBA, sectCnt, 0)
                  result = data['LLRET']
                  if result != OK:
                     objMsg.printMsg('%s SeqWriteDMAExt failed. Result=%s Data=%s' % (TestName, result, data))
                     break

               # end for
               # DT150310 Add SeqRead
               if result == OK:
                  objMsg.printMsg('%s Flush Cache, Clear Buffers, Fill 0x%2X Data' % (TestName, pattern))
                  ICmd.FlushCache()
                  ICmd.ClearBinBuff(RBF)
                  startLBA = 0
                  # DT011210 Bug Fix
                  #endLBA = maxLBA - 200000
                  endLBA = maxLBA
                  stepLBA = sectCnt
                  stampFlag = 0
                  compFlag = 0   # can not do compare. cause pattern is only written to random locations.
                  data = ICmd.SequentialReadDMAExt(startLBA, endLBA, stepLBA, sectCnt, stampFlag, compFlag)
                  result = data['LLRET']
                  objMsg.printMsg('%s SeqRead Data=%s Result=%s' % (TestName, data, result))

               if B_Msg or data['LLRET'] != OK:
                  objMsg.printMsg('%s Read Buffer Data ----------------------------------------' % TestName)
                  rb_data = ICmd.GetBuffer(RBF, 0, 550)['DATA']
                  objMsg.printMsg('%s %s' % (TestName, rb_data[0:20]))
                  objMsg.printMsg('%s %s' % (TestName, rb_data[512:532]))

               # end
               if result == OK:
                  objMsg.printMsg('%s Test passed!' % TestName)
               else:

                  objMsg.printMsg('%s Test failed!' % TestName)
                  raise gioTestException(data)
            #EndTime(TestName, 'funcstart', 'funcfinish', 'functotal')

         return result

      #---------------------------------------------------------------------------------------------------------#
      def doPerfMeasureZoneDegrade(self, TestType='IDT', TestName='ZONEDEGRADE'):
         D_Msg = ON      # Performance Message
         T_Msg = ON      # Failure Message
         data = {}
         #TestType = ('IDT')
         #TestName = ('ZONEDEGRADE')

         self.testName = ('%s %s' % (TestType, TestName))                       # Test Name for file formatting
         result = OK
         NumZone = 16
         MaxLBA = self.oRF.IDAttr['MaxLBA'] - (self.oRF.IDAttr['MaxLBA'] % NumZone)
         ZoneStep = MaxLBA / NumZone
         UDMA_Speed = 0x45
         SectCnt = 256
         TxSet1 = {}
         TxSet2 = {}
         ZONETHRUPUT = ON

         #driveattr['testseq'] = TestName.replace(' ','_')
         #ICmd.SetIntfTimeout(ConfigVars[CN]['Intf Timeout'])
         ICmd.SetIntfTimeout(10000)

         if ZONETHRUPUT == ON:

            if result == OK:
               #StartTime(TestName, 'funcstart')
               #driveattr['eventdate'] = time.time()
               self.testCmdTime = 0
               self.printTestName(self.testName)

               self.oRF.powerCycle()

            #Clear Write/Read Buffer
            ICmd.ClearBinBuff(WBF)
            ICmd.ClearBinBuff(RBF)
            if result == OK:
               xfer_key = ('%s_wrt_xfer' % TestType)
               data = ICmd.SetFeatures(0x03, UDMA_Speed)
               result = data['LLRET']
               if result == OK:
                  objMsg.printMsg('%s SetFeature Transfer Rate passed' % TestName)
               else:
                  objMsg.printMsg('%s SetFeature Transfer Rate failed' % TestName)

            if result == OK:
               StartLBA = 0
               EndLBA = StartLBA + ZoneStep - 1
               for i in range(1, NumZone+1):
                  # seq read
                  if (result == OK) and (i==1 or i==NumZone):
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
                  if (result == OK) and (i==1 or i==NumZone):
                     data = ICmd.WriteDMAExtTransRate(StartLBA, EndLBA - StartLBA, SectCnt)
                     result = data['LLRET']
                     if result == OK:
                        TxRate = int(data['TXRATE'])
                        objMsg.printMsg('%s MaxLBA=%d WriteDMA Zone=%d StartLBA=%d EndLBA=%d SectCnt=%d TxRate=%d' % \
                                       (TestName, MaxLBA, i, StartLBA, EndLBA, SectCnt, TxRate))
                        TxSet1['ZoneWrt%d'% i] = TxRate
                     else:
                        objMsg.printMsg('%s Zone(%d) WriteDMATxRate failed. Result=%s Data=%s' % (TestName, i, result, data))
                        break


                  StartLBA = StartLBA + ZoneStep
                  EndLBA = StartLBA + ZoneStep - 1
                  # end for

               StartLBA = 0
               EndLBA = StartLBA + ZoneStep - 1

               for i in range(1, NumZone+1):
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
                  if (result == OK) and (i==1 or i==NumZone):
                     data = ICmd.WriteDMAExtTransRate(StartLBA, EndLBA - StartLBA, SectCnt)
                     result = data['LLRET']
                     if result == OK:
                        TxRate = int(data['TXRATE'])
                        objMsg.printMsg('%s MaxLBA=%d WriteDMA Zone=%d StartLBA=%d EndLBA=%d SectCnt=%d TxRate=%d' % \
                                       (TestName, MaxLBA, i, StartLBA, EndLBA, SectCnt, TxRate))
                        TxSet2['ZoneWrt%d'% i] = TxRate
                     else:
                        objMsg.printMsg('%s Zone(%d) WriteDMATxRate failed. Result=%s Data=%s' % (TestName, i, result, data))
                        break

                  StartLBA = StartLBA + ZoneStep
                  EndLBA = StartLBA + ZoneStep - 1

                  # end for

            if result == OK:
               keys1 = TxSet1.keys()
               keys1.sort()
               keys2 = TxSet2.keys()
               keys2.sort()
               for key in TxSet1.keys():
                  if TxSet1[key] >= TxSet2[key]:
                     skew = (TxSet1[key] - TxSet2[key]) / TxSet1[key]
                  else:
                     skew = (TxSet2[key] - TxSet1[key]) / TxSet2[key]
                  objMsg.printMsg('%s Key=%s TxRate1=%d TxRate2=%d' % (TestName, key, TxSet1[key], TxSet2[key]))
                  if skew > 0.2:
                     objMsg.printMsg('%s Test failed.' % TestName)
                     result = FAIL
                     break


            if result == OK:
               objMsg.printMsg('%s Test passed!' % TestName)
            else:
               objMsg.printMsg('%s Test failed!' % TestName)
               raise gioTestException(data)
            #EndTime(TestName, 'funcstart', 'funcfinish', 'functotal')

         return result

      #---------------------------------------------------------------------------------------------------------#
   #   def timetostring(self,testtime):
   #      h = testtime / 3600
   #      m = ((testtime / 60) % 60)
   #      s = testtime % 60
   #      timestring = '%02d:%02d:%02d' % (h, m, s)
   #
   #      return timestring

   #---------------------------------------------------------------------------------------------------------#
   #---------------------------------------------------------------------------------------------------------#
   #---------------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------------#
# End
#---------------------------------------------------------------------------------------------------------#

