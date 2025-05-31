# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
from Constants import *
from State import CState
from Drive import objDut
from TestParamExtractor import TP
from PowerControl import objPwrCtrl
from Process import CProcess
from serialScreen import sptDiagCmds
from IntfClass import CIdentifyDevice
from Utility import CUtility
from CustomCfg import CCustomCfg


import sptCmds
import time
import MessageHandler as objMsg
import ScrCmds
import re

#By Sitthipong S.
from Test_Switches import testSwitch
#---------------------------------------------------------------------------------------------------------#
lbaTuple = CUtility.returnStartLbaWords

###########################################################################################################
class CTODT(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params=[]):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      self.oProcess = CProcess()
      self.oSerial = sptDiagCmds()

      self.DisableUDR()

      self.SmartDSTLongTest()                                                 #DST Long

      ret = CIdentifyDevice().ID
      self.maxLBA = ret['IDDefaultLBAs'] - 1
      if ret['IDCommandSet5'] & 0x400:
         self.maxLBA = ret['IDDefault48bitLBAs'] - 1                          #Get Max LBA from drive

      self.cap = int((self.maxLBA*512)/1000000000)

      ttlBlkToXFR, start_LBA = self.TotalBlkToXfr(16, 1)
      self.oProcess.St(TP.prm_510_TODT, prm_name='prm_510_RVerify', CTRL_WORD1=(0x40), CTRL_WORD2=(0x2080), STARTING_LBA=(0,0,0,0), TOTAL_BLKS_TO_XFR=ttlBlkToXFR, BLKS_PER_XFR=(0x250),)  #Sequential Read Verify zone 0 (0 to 1/16*maxLBA)
      self.oProcess.St(TP.prm_510_TODT, prm_name='prm_510_RVerify', CTRL_WORD1=(0x40), CTRL_WORD2=(0x2080), STARTING_LBA=start_LBA,  TOTAL_BLKS_TO_XFR=ttlBlkToXFR, BLKS_PER_XFR=(0x250),)  #Sequential Read Verify zone 15 (15/16*maxLBA to maxLBA)

      ttlBlkToXFR, start_LBA =self.TotalBlkToXfr(16, 2)
      self.oProcess.St(TP.prm_510_TODT, prm_name='prm_510_SeqW', CTRL_WORD1=(0x20), CTRL_WORD2=(0x1), STARTING_LBA=(0,0,0,0), TOTAL_BLKS_TO_XFR=ttlBlkToXFR, BLKS_PER_XFR=(0x250),)  #Sequential Write OD ID zone 0-1 (0 to 2/16*maxLBA) Pattern Random
      self.oProcess.St(TP.prm_510_TODT, prm_name='prm_510_SeqW', CTRL_WORD1=(0x20), CTRL_WORD2=(0x1), STARTING_LBA=start_LBA,  TOTAL_BLKS_TO_XFR=ttlBlkToXFR, BLKS_PER_XFR=(0x250),)  #Sequential Write OD ID zone 14-15 (14/16*maxLBA to maxLBA) Pattern Random

      ttlBlkToXFR, start_LBA =self.TotalBlkToXfr(16, 2)
      self.oProcess.St(TP.prm_510_TODT, prm_name='prm_510_SeqR', CTRL_WORD1=(0x10), CTRL_WORD2=(0x2080), STARTING_LBA=(0,0,0,0), TOTAL_BLKS_TO_XFR=ttlBlkToXFR, BLKS_PER_XFR=(0x250),)  #Sequential Read OD ID zone 0-1 (0 to 2/16*maxLBA)
      self.oProcess.St(TP.prm_510_TODT, prm_name='prm_510_SeqR', CTRL_WORD1=(0x10), CTRL_WORD2=(0x2080), STARTING_LBA=start_LBA,  TOTAL_BLKS_TO_XFR=ttlBlkToXFR, BLKS_PER_XFR=(0x250),)  #Sequential Read OD ID zone 14-15 (14/16*maxLBA to maxLBA)

      self.RndWritex25()  #Stop Start 25xRandomWriteDMAExt

      self.Butterfly()

      BlkPerXFR = self.SetBlkPerXfer()

      ttlBlkToXFR, start_LBA = self.TotalBlkToXfr(16, 1)
      self.oProcess.St(TP.prm_510_TODT, prm_name='prm_510_SeqW', CTRL_WORD1=(0x20), CTRL_WORD2=(0x2080), STARTING_LBA=(0,0,0,0), TOTAL_BLKS_TO_XFR=ttlBlkToXFR, BLKS_PER_XFR=BlkPerXFR, DATA_PATTERN0=(0x0000, 0x0000),)  #Seq Write OD
      self.oProcess.St(TP.prm_510_TODT, prm_name='prm_510_RVerify', CTRL_WORD1=(0x40), CTRL_WORD2=(0x2080), STARTING_LBA=(0,0,0,0), TOTAL_BLKS_TO_XFR=ttlBlkToXFR, BLKS_PER_XFR=BlkPerXFR, DATA_PATTERN0=(0x0000, 0x0000),)  #Seq Read Verify OD

      #ttlBlkToXFR, start_LBA = self.TotalBlkToXfr(16, 15)
      #self.oProcess.St(TP.prm_510_TODT, prm_name='prm_510_SeqW', CTRL_WORD1=(0x20), CTRL_WORD2=(0x2080), STARTING_LBA=start_LBA,  TOTAL_BLKS_TO_XFR=ttlBlkToXFR, BLKS_PER_XFR=BlkPerXFR, DATA_PATTERN0=(0x0000, 0x0000),)  #Seq Write MD ID zone 1-15 (1/16*maxLBA to maxLBA)
      #
      #self.oProcess.St(TP.prm_510_TODT, prm_name='prm_510_SeqR', CTRL_WORD1=(0x10), CTRL_WORD2=(0x2080), STARTING_LBA=(0,0,0,0),  TOTAL_BLKS_TO_XFR=(0x0000,0x0000), BLKS_PER_XFR=BlkPerXFR,)  #Seq Read Full

      self.EnableUDR()

      self.ResetSMART()
   #-------------------------------------------------------------------------------------------------------
   def DisableUDR(self):
      objPwrCtrl.powerCycle()
      sptCmds.enableDiags()

      data = sptCmds.sendDiagCmd(CTRL_L,printResult=True)

      self.udrFlag = 0
      #find UDR support
      if re.findall('LTTC-UDR2 enabled', data) or re.findall('LTTC-UDR2 disabled', data):
         self.udrFlag = 1
         self.oSerial.gotoLevel('T')
         sptCmds.sendDiagCmd('F "LTTCPowerOnHours",0', printResult = True)
         sptCmds.sendDiagCmd(CTRL_L,printResult=True)

      objPwrCtrl.powerCycle(5000,12000,10,30)
   #-------------------------------------------------------------------------------------------------------
   def EnableUDR(self):
      objPwrCtrl.powerCycle()
      sptCmds.enableDiags()

      if self.udrFlag == 1:
         #self.oSerial.gotoLevel('T')
         #sptCmds.sendDiagCmd('F5A7,A')
         sptCmds.sendDiagCmd(CTRL_L,printResult=True)
         self.oSerial.gotoLevel('T')
         sptCmds.sendDiagCmd('F,,22', printResult = True)                          #To reset AMPs, Which will also make LTTCPowerOnHours changed back to default value (0xA)
         self.oSerial.gotoLevel('1')
         sptCmds.sendDiagCmd('N23', printResult = True)

      objPwrCtrl.powerCycle(5000,12000,10,30)
   #-------------------------------------------------------------------------------------------------------
   def ResetSMART(self):
      objPwrCtrl.powerCycle()
      sptCmds.enableDiags()
      self.oSerial.enableDiags()

      self.oSerial.SmartCmd(TP.smartResetParams)
      sptCmds.sendDiagCmd(CTRL_L,printResult=True)
      objPwrCtrl.powerCycle(5000,12000,10,30)
   #-------------------------------------------------------------------------------------------------------
   def SmartDSTLongTest(self):
      objMsg.printMsg('Smart DST Long : START')
      starttime = time.time()

      self.oProcess.St(TP.prm_638_Unlock_Seagate)
      self.oProcess.St(TP.prm_600_long)

      total_time = time.time() - starttime

      objMsg.printMsg('Smart DST Long Test Usage : %d' % total_time)
      objMsg.printMsg('Smart DST Long : END')
   #-------------------------------------------------------------------------------------------------------
   def returnStartLbaWords(self, startLBA):
      lowerWord1 = (startLBA & 0xFFFF0000) >> 16
      lowerWord2 = (startLBA & 0x0000FFFF)

      return (lowerWord1,lowerWord2)
   #-------------------------------------------------------------------------------------------------------
   def TotalBlkToXfr(self, ttlzone, numzonetest):
      ttlBlkToXfr = self.returnStartLbaWords((self.maxLBA/ttlzone)*numzonetest)
      startLBA = lbaTuple(self.maxLBA - ((self.maxLBA/ttlzone)*numzonetest))
      return ttlBlkToXfr, startLBA
   #-------------------------------------------------------------------------------------------------------
   def SetBlkPerXfer(self):
      if self.cap > 755: BlkPerXfer = (0x0250)
      elif self.cap > 505: BlkPerXfer = (0x0128)
      elif self.cap > 255: BlkPerXfer = (0x0094)
      else: BlkPerXfer = (0x004A)
      return BlkPerXfer
   #-------------------------------------------------------------------------------------------------------
   def RndWritex25(self):
      objMsg.printMsg('25x Random Write : START')
      starttime = time.time()

      loop_count = 25
      for n in range(loop_count):
         self.oProcess.St({'test_num':506, 'prm_name':'prm_506_SET_RUNTIME', 'spc_id':1, 'TEST_RUN_TIME':60,})  #1 Min Test Time
         self.oProcess.St(TP.prm_510_TODT, prm_name='prm_510_RndW', CTRL_WORD1=(0x21), CTRL_WORD2=(0x2080), STARTING_LBA=(0,0,0,0),  TOTAL_BLKS_TO_XFR=(0x0000,0xC350), BLKS_PER_XFR=(0x10),)  #Random Write 50000 blks

      total_time = time.time() - starttime
      objMsg.printMsg('25x Random Write Test Usage : %d' % total_time)
      objMsg.printMsg('25x Random Write  : END')
   #-------------------------------------------------------------------------------------------------------
   def Butterfly(self):
      objMsg.printMsg('Butterfly : START')
      starttime = time.time()

      prm_506_SET_RUNTIME = {
         'test_num'          : 506,
         'prm_name'          : "prm_506_SET_RUNTIME",
         'spc_id'            :  1,
         "TEST_RUN_TIME"     :  600,                                            #10 Mins Test Time
      }
      prm_510_BUTTERFLY = {
         'test_num'          : 510,
         'prm_name'          : "prm_510_BUTTERFLY",
         'spc_id'            :  1,
         "CTRL_WORD1"        : (0x0422),                                        #Butterfly Sequencetioal Write;Display Location of errors
         "STARTING_LBA"      : (0,0,0,0),
         "BLKS_PER_XFR"      : (0x10),
         "OPTIONS"           : 0,                                               #Butterfly Converging
         "timeout"           :  3000,                                           #15 Mins Test Time
      }

      if self.cap > 755: loop_count = 1
      elif self.cap > 505: loop_count = 2
      elif self.cap > 255: loop_count = 3
      else: loop_count = 4

      objMsg.printMsg('loop_count : %d' %loop_count)

      for n in range(loop_count):
         objMsg.printMsg("====================== Butterfly Test loop %d ========================="%(n+1))

         self.oProcess.St(prm_506_SET_RUNTIME, TEST_RUN_TIME=600)
         self.oProcess.St(prm_510_BUTTERFLY, prm_name='prm_510_ButterflyInW', CTRL_WORD1=0x0420, OPTIONS=0, BLKS_PER_XFR=(0x10),)  #Butterfly In Write

         self.oProcess.St(prm_506_SET_RUNTIME, TEST_RUN_TIME=600)
         self.oProcess.St(prm_510_BUTTERFLY, prm_name='prm_510_ButterflyInR', CTRL_WORD1=0x0410, OPTIONS=0, BLKS_PER_XFR=(0x10),)  #Butterfly In Read

         self.oProcess.St(prm_506_SET_RUNTIME, TEST_RUN_TIME=1200)
         self.oProcess.St(TP.prm_510_TODT, prm_name='prm_510_RndWRLong', CTRL_WORD1=(0x00), CTRL_WORD2=(0x1), STARTING_LBA=(0,0,0,0),  TOTAL_BLKS_TO_XFR=(0x0000,0xC350), BLKS_PER_XFR=(0x800),)  #Random WR Long >> Pattern Random

         self.oProcess.St(prm_506_SET_RUNTIME, TEST_RUN_TIME=600)
         self.oProcess.St(prm_510_BUTTERFLY, prm_name='prm_510_ButterflyOutW', CTRL_WORD1=0x0420, OPTIONS=1, BLKS_PER_XFR=(0x10),)  #Butterfly Out Write

         self.oProcess.St(prm_506_SET_RUNTIME, TEST_RUN_TIME=600)
         self.oProcess.St(prm_510_BUTTERFLY, prm_name='prm_510_ButterflyInR', CTRL_WORD1=0x0410, OPTIONS=1, BLKS_PER_XFR=(0x10),)  #Butterfly Out Read

         self.oProcess.St(prm_506_SET_RUNTIME, TEST_RUN_TIME=1200)
         self.oProcess.St(TP.prm_510_TODT, prm_name='prm_510_RndWRShort', CTRL_WORD1=(0x00), CTRL_WORD2=(0x1), STARTING_LBA=(0,0,0,0),  TOTAL_BLKS_TO_XFR=(0x0000,0xC350), BLKS_PER_XFR=(0x10),)  #Random WR Short >> Pattern Random

      self.oProcess.St(prm_506_SET_RUNTIME, TEST_RUN_TIME=0)

      total_time = time.time() - starttime
      objMsg.printMsg('Butterfly Test Usage : %d' % total_time)
      objMsg.printMsg('Butterfly : END')

###########################################################################################################
###########################################################################################################
class CFailProc(CState):
   """
      Put in your fail sequence code in this class' run() method
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      objMsg.printMsg('<<< Test failure Handling >>>')
      SetFailSafe()
      #
      # Fail handling code here

      oProcess = CProcess()

      #Used to prevent adjacent drive fail if timeout failure occuring
      if testSwitch.FE_0118805_405392_POWER_CYCLE_AT_FAILPROC_START:
         try:
            objPwrCtrl.powerCycle()
         except:
            pass

      #Display Debug information for all failure drive as per ScPk request
      if testSwitch.EnableDebugLogging:
         try:
            oSerial = serialScreen.sptDiagCmds()
            sptCmds.enableDiags()
            oSerial.dumpReassignedSectorList()
            sptCmds.gotoLevel('1')
            oSerial.getCriticalEventAttributes(30,failOnThresholdViolation=False)
            oSerial.getCriticalEventLog(30)
         except:
            pass

      #Display V4 and N8
      if testSwitch.FE_0145983_409401_P_SEND_ATTR_FOR_CONTROL_DRIVE_ERROR:
         try:
            #objPwrCtrl.powerCycle()
            objMsg.printMsg('Serial Port T>V4 from Drive')
            retry = 1
            noV4 = 0
            harddefect = 0
            while retry >= 0:
               sptCmds.enableDiags()
               sptCmds.gotoLevel('T')
               data = sptCmds.sendDiagCmd('V4', printResult = True)

               if re.search("Pending: [0-9]{4}",data):
                  pending = re.search("Pending: [0-9]{4}",data).group(0).split(" ")[1]
                  break
               else:
                  if retry >= 1: objPwrCtrl.powerCycle()
                  else: noV4 = 1
               retry -=1
            #identify head
            self.dut.driveattr['TODT_FAIL_HEAD'] = ''+'0'*int(DriveAttributes.get('NUM_HEADS',0))

            if noV4 == 0:
               if pending != '0000':
                  harddefect = 1
                  lstData = data.split('\r\n')
                  for i in range(len(lstData)):
                     strData = re.search('\s+\w+\s+\w+\.(?P<head>[a-fA-F\d])\.\w+\s+',lstData[i])
                     if strData != None:
                        idx = int(strData.group('head'))
                        objMsg.printMsg('Hard error at head %d'%idx)
                        dgFailHd = self.dut.driveattr['TODT_FAIL_HEAD']
                        self.dut.driveattr['TODT_FAIL_HEAD'] = dgFailHd[0:idx] + '1' + dgFailHd[idx+1:]
               objMsg.printMsg('TODT failed head is %s'%(self.dut.driveattr['TODT_FAIL_HEAD']))
         except:
            pass

         try:
            objMsg.printMsg('Serial Port 1>N8 from Drive')
            sptCmds.enableDiags()
            sptCmds.gotoLevel('1')
            data = sptCmds.sendDiagCmd('N8', printResult = True)

            if noV4 == 1:
               if re.search('BBM', data):
                  harddefect = 1
                  lstData = data.split('\r\n')
                  for i in range(len(lstData)):
                     if re.search('BBM', lstData[i]):
                        strData = re.search('\w+\s+\-\s+\w+\s+\w+\s+\w+\s+(?P<head>[a-fA-F\d])',lstData[i])
                        if strData != None:
                           idx = int(strData.group('head'))
                           objMsg.printMsg('Hard error at head %d'%idx)
                           dgFailHd = self.dut.driveattr['TODT_FAIL_HEAD']
                           self.dut.driveattr['TODT_FAIL_HEAD'] = dgFailHd[0:idx] + '1' + dgFailHd[idx+1:]
               objMsg.printMsg('TODT failed head is %s'%(self.dut.driveattr['TODT_FAIL_HEAD']))
         except:
            pass

         try:
            if harddefect == 1: self.dut.driveattr['TODT_DEF'] = 'H'
            else: self.dut.driveattr['TODT_DEF'] = 'S'
         except:
            pass

      #Allow for redefine if not imported by program
      TP.basePrm_IO_FailProc_504 = getattr(TP,'basePrm_IO_FailProc_504',{'test_num':504, 'prm_name': 'basePrm_IO_FailProc_504', 'timeout': 60,})

      try:
         # Grab debug data from CPC
         oProcess.St(TP.basePrm_IO_FailProc_504)
      except:
         pass


      if testSwitch.setManufacturingStatus:
         try:
            sptCmds.enableDiags()
            try:
               from serialScreen import sptDiagCmds
               oSer = sptDiagCmds()
               oSer.enableDiags()

               try:
                  ec = self.dut.failureData[0][2]
               except:
                  ec = self.dut.errCode

               oSer.setCurrentManufacturingStatus(self.dut.nextOper, ec)
            except:
               pass
         finally:
            try:
               objPwrCtrl.powerCycle()
            except:
               pass

      objMsg.printDblogBin(self.dut.dblData.Tables('P_TIME_TO_READY'), spcId32 = 1)

      #
      #
      ClearFailSafe()
      #
      # throw an exception next
      #
      self.exitStateMachine() # this will throw exception to be handled by top level code in Setup.py

###########################################################################################################
if testSwitch.FE_0155867_395340_P_FIRST_ODT_SEQUENT_TEST_FOR_SAS:
   ######################################################################################################
   from Carrier import theCarrier
   from Cell import theCell
   from sptCmds import comMode
   from TestParameters import *
   import base_TODT_TestParameters as ODT_TP
   import Setup
   oProc = CProcess()
   ######################################################################################################
   class CODT_Process(CState):
      #--------------------------------------------------------------------------------------------------
      def __init__(self, dut, params=[]):
         import string
         self.params = params
         depList = []
         CState.__init__(self, dut, depList)
         self.st_506 = "Disabled"
         self.st_700 = "Disabled"

      #--------------------------------------------------------------------------------------------------
      def run(self):
         self.dut.driveattr['MQM_SAS_VER'] = '2.5'
         if ConfigVars[CN].get('GenerateCCV', 0):
            self.dut.driveattr['MQM_TEST_DONE'] = 'PASS'
            objCCustomCfg = CCustomCfg()
            rwMQM = objCCustomCfg.SelectRWKMQM()
            if rwMQM == 'Y':
               self.dut.driveattr['MQM_RW'] = 'PASS'
            return
         else:
            self.dut.driveattr['MQM_TEST_DONE'] = 'FAIL'
         objMsg.printMsg("-------------------------------------------------------------------------------------------------")
         objMsg.printMsg("FIRST ODT REV %s" % self.dut.driveattr['MQM_SAS_VER'])
         objMsg.printMsg("-------------------------------------------------------------------------------------------------")

         if testSwitch.FE_0162716_395340_P_MQM_REWORK_FOR_PRE_ODT_SS:
            objCCustomCfg = CCustomCfg()
            rwMQM = objCCustomCfg.SelectRWKMQM()
            if rwMQM == 'Y':
               objMsg.printMsg("This is Drive Rework")
               self.dut.driveattr['MQM_RW'] = 'FAIL'

         self.product = ODT_TP.ODTfamilyInfo.get(self.dut.partNum[0:3],'none')
         if self.product == 'none':
            objMsg.printMsg("---------- No valid partNum '%s' found in ODTfamilyInfo table. ----------"%partNum[0:3])
            ScrCmds.raiseException(11075,"No valid partNum found in ODTfamilyInfo table")

         objMsg.printMsg("Drive type profile: %s"%self.product['DRV_TYPE'])
         objMsg.printMsg("Initiator Codes.py variable call: %s"%self.product['INIT_TYPE'])
         objMsg.printMsg("Number of ODT Loops to run:  %s"%self.product['ODTLOOPS'])
         objMsg.printMsg("Process temperature setting:  %s"%self.product['RUN_TEMP'])
         objMsg.printMsg("Ending temperature setting:  %s"%self.product['END_TEMP'])
         objMsg.printMsg("Allowable G-list entry adds:  %s"%self.product['GLIST_MAX'])
         objMsg.printMsg("Allowed Recoverable Errors per test:  %s"%self.product['ALLOW_REC_ERR'])
         objMsg.printMsg("-------------------------------------------------------------------------------------------------\n")

         #tempset = int(self.product['RUN_TEMP'])
         glistmax = int(self.product['GLIST_MAX'])
         rec_allow = int(self.product['ALLOW_REC_ERR'])

         self.dut.sptActive = comMode(comMode.availModes.intBase)
         #if not ConfigVars[CN].get('BenchTop',0):
         #   theCell.setTemp(tempset,tempset-5,tempset+5,self.dut.objSeq,objDut,'wait') #Breaks bench cell so we don't execute this if BenchTop set true

         oODTsup.Initiator_initialize()  # Initialize initiator
         #Skip by Sitthipong S.
         #self.CCV_InitiatorDL()  # Conditional Initiator download
         #Skip by Sitthipong S.
         self.SpinUp()
         oProc.St(ODT_TP.prm_535_InitiatorInfo)	# Get Initiator Code Rev with store as DriveVars["Initiator Code"]

         objMsg.printMsg("-------------------------------------------------------------------------------------------------")
         objMsg.printMsg("---------------- ODT Process Begin --------------------------------------------------------------")
         objMsg.printMsg("-------------------------------------------------------------------------------------------------")

         if self.product['DRV_TYPE'] == "SED":  # Only run on SED
            if oODTsup.get_drvFDEmode() == "80":
               objMsg.printMsg("Drive is in USE mode.  Will change to MFG mode.")
               oODTsup.FDEmode_MFG()

   #####################################################################################################################################
         objMsg.printMsg("Test 1: Setting up test parameters & Read Glist")
         oProc.St(ODT_TP.prm_518_DisplayCurrentMps)  # Display Current Modepages
         oProc.St(ODT_TP.prm_518_DisplayChangeableMps)  # Display Changeable Modepages
         oProc.St(ODT_TP.prm_518_DisplayDefaultMps)  # Display Default Modepages
         oProc.St(ODT_TP.prm_518_DisplaySavedMps)  # Display SAV Mode Sense
         if not testSwitch.BF_0158268_357360_P_DISABLE_SET_DEF_MODE_PAGES_IN_ODT:
            oProc.St(ODT_TP.prm_537_Set_SAV_To_DEF)  # Set Saved Modes Sense to Default
            if testSwitch.BF_0157606_426568_P_POWER_CYCLE_AFTER_SET_MODE_PAGES_ODT:
               objPwrCtrl.powerCycle(5000,12000,20,30,useESlip=1)
         oProc.St(ODT_TP.prm_518_DisplayCurrentMps)  # Display Current Modepages

         oODTsup.ODT_modeselect()
         oProc.St(ODT_TP.prm_518_DisplayCurrentMps)  # Display Current Modepages
         oProc.St(ODT_TP.prm_529_CheckGrowthDefects,{'prm_name':'Display Glist Flaws - 0 allowed'},MAX_GLIST_ENTRIES=(0x0000,0x0000,))  # Display G-List - 0 Max
   ##      oProc.St(ODT_TP.prm_529_CheckServoDefects,{'prm_name':'Display Servo Flaws - no maximum'},MAX_SERVO_DEFECTS=(0xFFFF,))  # Display Added Servo Flaws - no Max
         oProc.St(ODT_TP.prm_503_Display_Log_Pages,{'prm_name':'Display all Pages - Fail BGMS 30'},PAGE_CODE=(0xFFFF,),BGMS_FAILURES=(0x001E,))  # Display log pages, fail BGMS > 30
         oODTsup.Initiator_initialize()  # Initialize initiator
         self.SpinUp()

         objMsg.printMsg("Read Drive Capacity")
         (LLB,blockSize,Prot) = oODTsup.get_LLB()
         objMsg.printMsg("-" * 60)
         objMsg.printMsg("Last Logical Block: %X    Block Size: %X    Protection Settings: %02X"%(LLB,blockSize,Prot))
         drvCap = int(( LLB * blockSize )/1000000000)
         objMsg.printMsg("Drive Capacity - %dGB"%drvCap)

   #####################################################################################################################################
         #Setup for drive partitioning into 16th sections.
         objMsg.printMsg("-" * 60)
         drvCap_lsbNum = lbaTuple(LLB)
         objMsg.printMsg("maxcap: %04X%04X%04X"%(drvCap_lsbNum[1],drvCap_lsbNum[2],drvCap_lsbNum[3]))

         drvCap1of8 = int(LLB/8)  # 1/8 of the capacity
         drvCap1of8_lsbNum = lbaTuple(drvCap1of8)
         objMsg.printMsg("1of8:   %04X%04X%04X"%(drvCap1of8_lsbNum[1],drvCap1of8_lsbNum[2],drvCap1of8_lsbNum[3]))

         drvCap2of8 = drvCap1of8 * 2  # 2/8 of the capacity
         drvCap2of8_lsbNum = lbaTuple(drvCap2of8)
         objMsg.printMsg("2of8:   %04X%04X%04X"%(drvCap2of8_lsbNum[1],drvCap2of8_lsbNum[2],drvCap2of8_lsbNum[3]))

         drvCap6of8 = drvCap1of8 * 6  # 6/8 of the capacity
         drvCap6of8_lsbNum = lbaTuple(drvCap6of8)
         objMsg.printMsg("6of8:   %04X%04X%04X"%(drvCap6of8_lsbNum[1],drvCap6of8_lsbNum[2],drvCap6of8_lsbNum[3]))

         drvCap7of8 = drvCap1of8 * 7  # 7/8 of the capacity
         drvCap7of8_lsbNum = lbaTuple(drvCap7of8)
         objMsg.printMsg("7of8:   %04X%04X%04X"%(drvCap7of8_lsbNum[1],drvCap7of8_lsbNum[2],drvCap7of8_lsbNum[3]))

         drvCap1of16 = int(LLB/16)  # 1/16 of the capacity
         drvCap1of16_lsbNum = lbaTuple(drvCap1of16)
         objMsg.printMsg("1of16:  %04X%04X%04X"%(drvCap1of16_lsbNum[1],drvCap1of16_lsbNum[2],drvCap1of16_lsbNum[3]))

         drvCap15of16 = drvCap1of16 * 15  # 15/16 of the capacity
         drvCap15of16_lsbNum = lbaTuple(drvCap15of16)
         objMsg.printMsg("15of16: %04X%04X%04X"%(drvCap15of16_lsbNum[1],drvCap15of16_lsbNum[2],drvCap15of16_lsbNum[3]))

   #####################################################################################################################################
   #####################################################################################################################################
   ##### START OF FULL ODT PROCESS LOOPING
         for ODTloop_cnt in range(1,int(self.product['ODTLOOPS'])+1):
            objMsg.printMsg("-" * 60)
            objMsg.printMsg("ODT Process Loop %s of %s"%(ODTloop_cnt,self.product['ODTLOOPS']))
            objMsg.printMsg("-" * 60)
            dict = {}
            dict['ODTLOOPS'] = self.product['ODTLOOPS']
            DriveAttributes.update(dict)

            #####################################################################################################################################
            objMsg.printMsg("Test 1A: Drive Self Test - Extended Test Mode -")
            #Skip by Chris L. recommend
            #oProc.St(ODT_TP.prm_600_DST)  # Drive Self Test (Extended Test Mode)
            #Skip by Chris L. recommend
            #Due to intermittent initiator problems, per Kumanan R., need this initiator power cycle to recover after long DST
            oProc.St(ODT_TP.prm_538_SpinDown)
            oODTsup.Initiator_initialize()  # Initialize initiator
            self.SpinUp()

            #####################################################################################################################################
            #Capacity Based LBA Xfer Control on Section 2 and 3 and 4
            if drvCap > 2000:
               xferblocks = 0x01000;   #New from Sitthipong S.
            elif drvCap > 1005:
               xferblocks = 0x0250;
            elif drvCap > 755:
               xferblocks = 0x0080;
            elif drvCap > 505:
               xferblocks = 0x0060;
            else:
               xferblocks = 0x0040;
            #---------------------------------------------------------------------------------------------------------------------------------------
            objMsg.printMsg("Test 2a: Seq Verify Outer 1/16 -- 0x%x (%d) LBA Xfer"% (xferblocks,xferblocks))
            oProc.St(ODT_TP.prm_510_ODTSeq,{'prm_name':'Seq Verify'},WRITE_READ_MODE=(0x0003,),NUMBER_LBA_PER_XFER=(0x0000,xferblocks,),OPTIONS_WORD1=(0x000A,),START_LBA34=(0x0000,0x0000,0x0000,0x0000,),END_LBA34=drvCap1of16_lsbNum,MAX_RCV_ERRS=(0x0000,rec_allow,))
            #---------------------------------------------------------------------------------------------------------------------------------------
            objMsg.printMsg("Test 2b: Seq Verify Inner 1/16 -- 0x%x (%d) LBA Xfer"% (xferblocks,xferblocks))
            oProc.St(ODT_TP.prm_510_ODTSeq,{'prm_name':'Seq Verify'},WRITE_READ_MODE=(0x0003,),NUMBER_LBA_PER_XFER=(0x0000,xferblocks,),OPTIONS_WORD1=(0x000A,),START_LBA34=drvCap15of16_lsbNum,END_LBA34=drvCap_lsbNum,MAX_RCV_ERRS=(0x0000,rec_allow,))

            #---------------------------------------------------------------------------------------------------------------------------------------
            objMsg.printMsg("Test 3a: Seq Write Outer 1/8 -- 0x%x (%d) LBA Xfer"% (xferblocks,xferblocks))
            oProc.St(ODT_TP.prm_510_ODTSeq,{'prm_name':'Seq Write'},WRITE_READ_MODE=(0x0002,),NUMBER_LBA_PER_XFER=(0x0000,xferblocks,),OPTIONS_WORD1=(0x000A,),START_LBA34=(0x0000,0x0000,0x0000,0x0000,),END_LBA34=drvCap1of8_lsbNum,MAX_RCV_ERRS=(0x0000,rec_allow,))
            #---------------------------------------------------------------------------------------------------------------------------------------
            objMsg.printMsg("Test 3b: Seq Write Inner 1/8 -- 0x%x (%d) LBA Xfer"% (xferblocks,xferblocks))
            oProc.St(ODT_TP.prm_510_ODTSeq,{'prm_name':'Seq Write'},WRITE_READ_MODE=(0x0002,),NUMBER_LBA_PER_XFER=(0x0000,xferblocks,),OPTIONS_WORD1=(0x000A,),START_LBA34=drvCap7of8_lsbNum,END_LBA34=drvCap_lsbNum,MAX_RCV_ERRS=(0x0000,rec_allow,))

            #---------------------------------------------------------------------------------------------------------------------------------------
            objMsg.printMsg("Test 4a: Seq Read Outer 1/8 -- 0x%x (%d) LBA Xfer"% (xferblocks,xferblocks))
            oProc.St(ODT_TP.prm_510_ODTSeq,{'prm_name':'Seq Read'},WRITE_READ_MODE=(0x0001,),NUMBER_LBA_PER_XFER=(0x0000,xferblocks,),OPTIONS_WORD1=(0x000A,),START_LBA34=(0x0000,0x0000,0x0000,0x0000,),END_LBA34=drvCap1of8_lsbNum,MAX_RCV_ERRS=(0x0000,rec_allow,))
            #---------------------------------------------------------------------------------------------------------------------------------------
            objMsg.printMsg("Test 4b: Seq Read Inner 1/8 -- 0x%x (%d) LBA Xfer"% (xferblocks,xferblocks))
            oProc.St(ODT_TP.prm_510_ODTSeq,{'prm_name':'Seq Read'},WRITE_READ_MODE=(0x0001,),NUMBER_LBA_PER_XFER=(0x0000,xferblocks,),OPTIONS_WORD1=(0x000A,),START_LBA34=drvCap7of8_lsbNum,END_LBA34=drvCap_lsbNum,MAX_RCV_ERRS=(0x0000,rec_allow,))

            #####################################################################################################################################
            loopmax = 26
            loopRange = range(1, loopmax)
            xferblocks = 0x0010
            time_in_min = 2
            for loop in loopRange:
   ##            DriveOff(30)
   ##            DriveOn(5000,12000,30)
               oODTsup.Initiator_initialize()  # Initialize initiator - WA_0130599_357466_T528_EC10124
               self.SpinUp()
               oProc.St(ODT_TP.prm_506_SetTest_StopTime,{'prm_name':'Set Test Stop Time = ' + str(time_in_min) + ' min'},TEST_EXE_TIME_SECONDS=(time_in_min*60,))
               objMsg.printMsg("Test 5: Random Write(%s mins) -- 0x%x (%d) LBA Xfer per command; Loop count = %s of %s"% (time_in_min,xferblocks,xferblocks,loop,(loopmax-1)))
               oProc.St(ODT_TP.prm_510_ODTRandom,{'prm_name':'Random Write'},NUMBER_LBA_PER_XFER=(0x0000,xferblocks,),MAX_RCV_ERRS=(0x0000,rec_allow,))

            #####################################################################################################################################
            #Capacity Based Loop Control on Section 6a - 6d
            if drvCap > 755:
               loopmax = 2       #Do 1 loop
            elif drvCap > 505:
               loopmax = 3
            elif drvCap > 255:
               loopmax = 4
            else:
               loopmax = 5
            loopRange = range(1, loopmax)
            for loop in loopRange:
               xferblocks = 0x0010
               time_in_min = 10
               #---------------------------------------------------------------------------------------------------------------------------------------
               oProc.St(ODT_TP.prm_506_SetTest_StopTime,{'prm_name':'Set Test Stop Time = ' + str(time_in_min) + ' min'},TEST_EXE_TIME_SECONDS=(time_in_min*60,))
               objMsg.printMsg("Test 6a: Butterfly Out Write(%s mins) -- 0x%x (%d) LBA Xfer per command; Loop count = %s of %s"% (time_in_min,xferblocks,xferblocks,loop,(loopmax-1)))
               oProc.St(ODT_TP.prm_510_ODTButfly,{'prm_name':'Butterfly Out Write'},WRITE_READ_MODE=(0x0002,),OPTIONS=(0x0001,),NUMBER_LBA_PER_XFER=(0x0000,xferblocks,),MAX_RCV_ERRS=(0x0000,rec_allow,))  # Butterfly Out Write
               #---------------------------------------------------------------------------------------------------------------------------------------
               oProc.St(ODT_TP.prm_506_SetTest_StopTime,{'prm_name':'Set Test Stop Time = ' + str(time_in_min) + ' min'},TEST_EXE_TIME_SECONDS=(time_in_min*60,))
               objMsg.printMsg("Test 6b: Butterfly Out Read(%s mins) -- 0x%x (%d) LBA Xfer per command; Loop count = %s of %s"% (time_in_min,xferblocks,xferblocks,loop,(loopmax-1)))
               oProc.St(ODT_TP.prm_510_ODTButfly,{'prm_name':'Butterfly Out Read'},WRITE_READ_MODE=(0x0001,),OPTIONS=(0x0001,),NUMBER_LBA_PER_XFER=(0x0000,xferblocks,),MAX_RCV_ERRS=(0x0000,rec_allow,))  # Butterfly Out Read
               #---------------------------------------------------------------------------------------------------------------------------------------
               oProc.St(ODT_TP.prm_506_SetTest_StopTime,{'prm_name':'Set Test Stop Time = ' + str(time_in_min) + ' min'},TEST_EXE_TIME_SECONDS=(time_in_min*60,))
               objMsg.printMsg("Test 6c: Butterfly In Write(%s mins) -- 0x%x (%d) LBA Xfer per command; Loop count = %s of %s"% (time_in_min,xferblocks,xferblocks,loop,(loopmax-1)))
               oProc.St(ODT_TP.prm_510_ODTButfly,{'prm_name':'Butterfly In Write'},WRITE_READ_MODE=(0x0002,),OPTIONS=(0x0000,),NUMBER_LBA_PER_XFER=(0x0000,xferblocks,),MAX_RCV_ERRS=(0x0000,rec_allow,))  # Butterfly In Write
               #---------------------------------------------------------------------------------------------------------------------------------------
               oProc.St(ODT_TP.prm_506_SetTest_StopTime,{'prm_name':'Set Test Stop Time = ' + str(time_in_min) + ' min'},TEST_EXE_TIME_SECONDS=(time_in_min*60,))
               objMsg.printMsg("Test 6d: Butterfly In Read(%s mins) -- 0x%x (%d) LBA Xfer per command; Loop count = %s of %s"% (time_in_min,xferblocks,xferblocks,loop,(loopmax-1)))
               oProc.St(ODT_TP.prm_510_ODTButfly,{'prm_name':'Butterfly In Read'},WRITE_READ_MODE=(0x0001,),OPTIONS=(0x0000,),NUMBER_LBA_PER_XFER=(0x0000,xferblocks,),MAX_RCV_ERRS=(0x0000,rec_allow,))  # Butterfly In Read

            #####################################################################################################################################
            #Capacity Based Loop Control on Section 7a - 7b
            #if drvCap > 755:
            #   loopmax = 2
            #elif drvCap > 505:
            #   loopmax = 3
            #elif drvCap > 255:
            #   loopmax = 4
            #else:
            #   loopmax = 5

            for loop in loopRange:
               time_in_min = 20
               #---------------------------------------------------------------------------------------------------------------------------------------
               xferblocks = 0x0010
               oProc.St(ODT_TP.prm_506_SetTest_StopTime,{'prm_name':'Set Test Stop Time = ' + str(time_in_min) + ' min'},TEST_EXE_TIME_SECONDS=(time_in_min*60,))
               objMsg.printMsg("Test 7a: Random Write/Read, short xfers(%s mins) -- 0x%x (%d) LBA Xfer per command; Loop count = %s of %s"% (time_in_min,xferblocks,xferblocks,loop,(loopmax-1)))
               oProc.St(ODT_TP.prm_510_ODTRandom,{'prm_name':'Random WR Short Xfer'},WRITE_READ_MODE=(0x0000,),NUMBER_LBA_PER_XFER=(0x0000,xferblocks,),MAX_RCV_ERRS=(0x0000,rec_allow,))
               #---------------------------------------------------------------------------------------------------------------------------------------
               xferblocks = 0x0800
               oProc.St(ODT_TP.prm_506_SetTest_StopTime,{'prm_name':'Set Test Stop Time = ' + str(time_in_min) + ' min'},TEST_EXE_TIME_SECONDS=(time_in_min*60,))
               objMsg.printMsg("Test 7b: Random Write/Read, long xfers(%s mins) -- 0x%x (%d) LBA Xfer per command; Loop count = %s of %s"% (time_in_min,xferblocks,xferblocks,loop,(loopmax-1)))
               oProc.St(ODT_TP.prm_510_ODTRandom,{'prm_name':'Random WR Long Xfer'},WRITE_READ_MODE=(0x0000,),NUMBER_LBA_PER_XFER=(0x0000,xferblocks,),MAX_RCV_ERRS=(0x0000,rec_allow,))


            #####################################################################################################################################
            objMsg.printMsg("Clear Test 506 run time setting")
            oProc.St(ODT_TP.prm_506_SetTest_StopTime,{'prm_name':'Reset Test Stop Time'},TEST_EXE_TIME_SECONDS=(0x0000,))  # reset counter
            oODTsup.Initiator_initialize()  # Initialize initiator
            self.SpinUp()


            #####################################################################################################################################
            #Capacity Based Loop Control on Section 8 and 9 and 10
            #if drvCap > 755:
            #   xferblocks = 0x0250;
            if drvCap > 2000:
               xferblocks = 0x1000;     #New from Sitthipong S.
            elif drvCap > 755:
               xferblocks = 0x0250;
            elif drvCap > 505:
               xferblocks = 0x0128;
            elif drvCap > 255:
               xferblocks = 0x0094;
            else:
               xferblocks = 0x004A;

            #Skip by Chris L. recommend
            #objMsg.printMsg("Test 8: Seq Write Verify (0/16 to 1/16 Vol) -- 0x%x (%d) LBA Xfer all 00's data"% (xferblocks,xferblocks))
            #oProc.St(ODT_TP.prm_510_ODTSeq,{'prm_name':'Seq Write Verify'},WRITE_AND_VERIFY=(0x0001,),NUMBER_LBA_PER_XFER=(0x0000,xferblocks,),OPTIONS_WORD1=(0x000A,),START_LBA34=(0x0000,0x0000,0x0000,0x0000,),END_LBA34=drvCap1of16_lsbNum,MAX_RCV_ERRS=(0x0000,rec_allow,))  # Sequential Write Verify with 00's data pattern

            #####################################################################################################################################
            #objMsg.printMsg("Test 9: Seq Write (1/16 to 16/16 Vol) -- 0x%x (%d) LBA Xfer all 00's data"% (xferblocks,xferblocks))
            #oProc.St(ODT_TP.prm_510_ODTSeq,{'prm_name':'Seq Write'},NUMBER_LBA_PER_XFER=(0x0000,xferblocks,),OPTIONS_WORD1=(0x000A,),START_LBA34=drvCap1of16_lsbNum,END_LBA34=(0x0000,drvCap_nsb,drvCap_msb,drvCap_lsb,),MAX_RCV_ERRS=(0x0000,rec_allow,))  # Sequential Write with 00's data pattern
            if not testSwitch.FE_0158637_426568_P_REMOVE_FULL_PACK_RW_FROM_ODT and (testSwitch.FE_0162716_395340_P_MQM_REWORK_FOR_PRE_ODT_SS and rwMQM == 'Y'):
               objMsg.printMsg("Test 8: Seq Write (0/16 to 16/16 Vol) -- 0x%x (%d) LBA Xfer all 00's data"% (xferblocks,xferblocks))
               oProc.St(ODT_TP.prm_510_ODTSeq,{'prm_name':'Seq Write'},NUMBER_LBA_PER_XFER=(0x0000,xferblocks,),OPTIONS_WORD1=(0x000A,),MAX_RCV_ERRS=(0x0000,rec_allow,))  # Sequential Write with 00's data pattern

            #####################################################################################################################################
            if not testSwitch.FE_0158637_426568_P_REMOVE_FULL_PACK_RW_FROM_ODT and (testSwitch.FE_0162716_395340_P_MQM_REWORK_FOR_PRE_ODT_SS and rwMQM == 'Y'):
               objMsg.printMsg("Test 9: Fullpack Sequential Read -- 0x%x (%d) LBA Xfer all 00's data"% (xferblocks,xferblocks))
               oProc.St(ODT_TP.prm_510_ODTSeq,{'prm_name':'Seq Read'},WRITE_READ_MODE=(0x0001,),NUMBER_LBA_PER_XFER=(0x0000,xferblocks,),MAX_RCV_ERRS=(0x0000,rec_allow,))  # Fullpack Sequential Read


            oProc.St(ODT_TP.prm_529_CheckGrowthDefects,{'prm_name':'Display Glist Flaws - display only'},MAX_GLIST_ENTRIES=(0x0000,0xFFFF,))  # Display G-List
   ##         oProc.St(ODT_TP.prm_529_CheckServoDefects,{'prm_name':'Display Servo Flaws - display only'},MAX_SERVO_DEFECTS=(0xFFFF,))  # Display Added Servo Flaws
            oProc.St(ODT_TP.prm_503_Display_Log_Pages,{'prm_name':'Display all Pages - display only'},PAGE_CODE=(0xFFFF,),BGMS_FAILURES=(0x00FF,))  # Display log pages

   ##### END OF FULL ODT PROCESS LOOPING
   #####################################################################################################################################
   #####################################################################################################################################


         #####################################################################################################################################
         objMsg.printMsg("Test 10: Read Glist & Spin down Drive")
         oProc.St(ODT_TP.prm_517_RequestSense)
         oProc.St(ODT_TP.prm_529_CheckGrowthDefects,{'prm_name':'Display Glist Flaws - ' + str(glistmax) + ' allowed'},MAX_GLIST_ENTRIES=(0x0000,glistmax,))  # Display G-List
   ##      oProc.St(ODT_TP.prm_529_CheckServoDefects,{'prm_name':'Display Servo Flaws - no maximum'},MAX_SERVO_DEFECTS=(0xFFFF,))  # Display Added Servo Flaws - no Max
         if not testSwitch.BF_0158268_357360_P_DISABLE_SET_DEF_MODE_PAGES_IN_ODT:
            oProc.St(ODT_TP.prm_537_Set_SAV_To_DEF)  # Set Saved Modes Sense to Default
            if testSwitch.BF_0157606_426568_P_POWER_CYCLE_AFTER_SET_MODE_PAGES_ODT:
               objPwrCtrl.powerCycle(5000,12000,20,30,useESlip=1)
         oProc.St(ODT_TP.prm_518_DisplayCurrentMps)  # Display Current Modepages
         oProc.St(ODT_TP.prm_503_Display_Log_Pages,{'prm_name':'Display all Pages - Fail BGMS 30'},PAGE_CODE=(0xFFFF,),BGMS_FAILURES=(0x001E,))  # Display log pages, fail BGMS > 30
         #oProc.St(ODT_TP.prm_538_SpinDown)
         #DriveOff(30)
         self.dut.driveattr['MQM_TEST_DONE'] = 'PASS'
         if rwMQM == 'Y':
            self.dut.driveattr['MQM_RW'] = 'PASS'
         #tempset = int(self.product['END_TEMP'])
         #if not ConfigVars[CN].get('BenchTop',0):
         #   theCell.setTemp(tempset,tempset-5,tempset+5,self.dut.objSeq,objDut,'wait') #Breaks bench cell so we don't execute this if BenchTop set true

         # These attributes are set to 'ODT Cleared' to prevent a drive from being shipped directly after ODT, without
         # an ODT Cleanup and CCV process being run afterwards.  CCV will correctly reset these values.
         #DriveAttributes["DOWNLOAD"]= 'ODT Cleared'
         #DriveAttributes["PROD_REV"]= 'ODT Cleared'
         #DriveAttributes["SCSI_CODE"]= 'ODT Cleared'
         #DriveAttributes["SERVO_CODE"]= 'ODT Cleared'

   ###################################################################################################
   #                          Conditional Initiator Download                                         #
   #                                                                                                 #
   #     This function is used to allow for a conditional Initiator download depending on the        #
   #setting of the variable named "CCV_INIT_DL" to be found in the "LIST DATA" of the config to      #
   #be run.  The following are the options for this setting.                                         #
   #   CCV_INIT_DL == 'ON' - check the existing revision, if different download new code             #
   #   CCV_INIT_DL == 'FORCE' - download the initiator always                                        #
   #   CCV_INIT_DL == <any other value, or variable doesn't exist> - bypass initiator download       #
   ###################################################################################################
      def CCV_InitiatorDL(self):
         #from Drive import comMode  #By Sitthipong S.
         self.dut.sptActive = comMode(comMode.availModes.intBase)

         RInit_Type = self.dut.codes[self.product['INIT_TYPE']]  # Requested initiator

         if ConfigVars[CN].get('CCV_INIT_DL', "ON") == "FORCE":
            try:
               objMsg.printMsg("Force Downloading initiator:  %s"%RInit_Type)
               oProc.St({'test_num':8,'prm_name':'DownLoad Init FW'},0,0,0,0,0,0,0,0,dlfile=(CN, RInit_Type),timeout=1800) # download initiator code
               objPwrCtrl.powerCycle(5000,12000,20,30,useESlip=1)
               self.SpinUp()
            except:
               objPwrCtrl.powerCycle(5000,12000,20,30,useESlip=1)
               #self.SpinUp()
               oProc.St({'test_num':8,'prm_name':'DownLoad Init FW'},0,0,0,0,0,0,0,0,dlfile=(CN, RInit_Type),timeout=1800) # download initiator code
               objPwrCtrl.powerCycle(5000,12000,20,30,useESlip=1)
               self.SpinUp()

         try:
            oProc.St(ODT_TP.prm_535_InitiatorInfo)	# Get Initiator Code Rev with store as DriveVars["Initiator Code"]
         except ScriptTestFailure, failureData:
            if failureData[0][2] == 10264:
               oProc.St({'test_num':535,'prm_name':'DriveVar Initiator Rev'},0x8002,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=1200) # Get Initiator Code Rev with store as DriveVars["Initiator Code"]
            else:
               objMsg.printMsg("Test 535 DriveVar option not supported.\n")
               DriveVars["Initiator Code"] = 'Unknown'
               objPwrCtrl.powerCycle(5000,12000,20,30,useESlip=1)
               self.SpinUp()
               oProc.St(ODT_TP.prm_535_InitiatorInfo)	# Display Initiator Code Rev

         if ConfigVars[CN].get('CCV_INIT_DL', "ON") == "ON":
            CInit_Type = DriveVars["Initiator Code"]   # get the current initiator code rev from DriveVars
            CInit_Type = str(CInit_Type)  # convert it to a string so it can be acted upon
            objMsg.printMsg("##########################################################################################")
            objMsg.printMsg("Current Initiator Code: %s        Requested Initiator Code: %s"%(CInit_Type,RInit_Type))
            if (CInit_Type.upper() == RInit_Type.upper()):
               objMsg.printMsg("The requested initiator code is already on the initiator.  No initiator download required.")
               objMsg.printMsg("##########################################################################################")
            else:
               objMsg.printMsg("Downloading initiator:  %s"%RInit_Type)
               objMsg.printMsg("##########################################################################################")
               try:
                  oProc.St({'test_num':8,'prm_name':'DownLoad Init FW'},0,0,0,0,0,0,0,0,dlfile=(CN, RInit_Type),timeout=1800) # download initiator code
                  objPwrCtrl.powerCycle(5000,12000,20,30,useESlip=1)
                  self.SpinUp()
               except:
                  objPwrCtrl.powerCycle(5000,12000,20,30,useESlip=1)
                  self.SpinUp()
                  oProc.St({'test_num':8,'prm_name':'DownLoad Init FW'},0,0,0,0,0,0,0,0,dlfile=(CN, RInit_Type),timeout=1800) # download initiator code
                  objPwrCtrl.powerCycle(5000,12000,20,30,useESlip=1)
                  self.SpinUp()

         if ConfigVars[CN].get('CCV_OVL_DL', "OFF") == "ON":
            objMsg.printMsg("Download Overlay after Initiator downloaded")
            import FSO
            self.dut.overlayHandler =  FSO.SelfTest_Overlay_Handler(self.dut)

   ###################################################################################################
   #                                           SpinUp                                                #
   #                                                                                                 #
   #     This function is used to powerup and spinup the drive, depending on I/O type.               #
   ###################################################################################################
      def SpinUp(self):
         if self.dut.drvIntf in ['FC','FCV']:
            oProc.St(ODT_TP.prm_608_PortLoginA)  # Clears LIP on Port A for login
            oProc.St(ODT_TP.prm_608_PortLoginB)  # Clears LIP on Port B for login
            oProc.St(ODT_TP.prm_517_RequestSense_Init_Check)
         elif self.dut.drvIntf in ['SS','AS','NS','SATA','SAS']:
            oProc.St(ODT_TP.prm_517_RequestSense)
            oProc.St(ODT_TP.prm_517_RequestSense_Init_Check)
         else:
            ScrCmds.raiseException(11107,'Drive type is not supported on this Line')
         oProc.St(ODT_TP.prm_514_StdInquiryData)
         oProc.St(ODT_TP.prm_514_StdInquiryData,TEST_FUNCTION=(0x9000,))  # Port B
         oProc.St(ODT_TP.prm_514_FwServoInfo)  # FW, Servo Ram, Servo Rom Revs
         oProc.St(ODT_TP.prm_517_RequestSense_Ready_Check)  # Checks for drive not ready conditions
         ScriptPause(20)  # Ensure drive is ready
   ######################################################################################################
   ######################################################################################################
   class CODT_Support:

      #--------------------------------------------------------------------------------------------------
      def __init__(self):
         pass


      #--------------------------------------------------------------------------------------------------
      def run(self):
         pass
   ###################################################################################################
   #                                Initiator_initialize                                             #
   #                                                                                                 #
   #     This function is used to startup initial communications with the initiator.                 #
   ###################################################################################################
      def Initiator_initialize(self):
         objMsg.printMsg("---------- Start Initiator Initialization ------------------------------------------------------------")
         objPwrCtrl.powerCycle(5000,12000,20,30,useESlip=1)
   ###################################################################################################
   #                                        ODT Mode Select                                          #
   #                                                                                                 #
   #     This function is used set the standard mode sense setting for the ODT process.              #
   ###################################################################################################
      def ODT_modeselect(self):

         oProc.St(ODT_TP.prm_518_ModeSelect_Save, {'prm_name':'Set Page 1, byte 2, bit Mdsel'},PAGE_CODE=(0x0001,),DATA_TO_CHANGE=(0x0001,),PAGE_BYTE_AND_DATA34=(0x0250,0x0240,0x0231,0x0221,0x0210,0x0200,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,))  # Set page1->TB=0,RC=0,EER=1,PER=1,DTE=0,DCR=0
         oProc.St(ODT_TP.prm_518_ModeSelect_Save, {'prm_name':'Set Page 7, byte 2, bit Mdsel'},PAGE_CODE=(0x0007,),DATA_TO_CHANGE=(0x0001,),PAGE_BYTE_AND_DATA34=(0x0231,0x0221,0x0210,0x0200,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,))  # Set page7->EER=1,PER=1,DTE=0,DCR=0
         oProc.St(ODT_TP.prm_518_ModeSelect_Save, {'prm_name':'Set Page 8, byte 2, bit Mdsel'},PAGE_CODE=(0x0008,),DATA_TO_CHANGE=(0x0001,),PAGE_BYTE_AND_DATA34=(0x0221,0x0200,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,))  # Set page8->WCE=1,RCD=0
         oProc.St(ODT_TP.prm_518_ModeSelect_Save, {'prm_name':'Set Page 1C, byte 3 = 0x04'},PAGE_CODE=(0x001C,),PAGE_BYTE_AND_DATA34=(0x0304,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,))  # Set SMART MRIE = 4
         oProc.St(ODT_TP.prm_518_Disable_PreScan_and_BGMS,{'prm_name':'Disable PreScan Only'},PAGE_BYTE_AND_DATA34=(0x0005,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,))  # Disable PreScan
         try:  # LA check for Hitachi, may work for others too, so attempt is made
            oProc.St(ODT_TP.prm_518_ModeSelect_Save, {'prm_name':'Set Page 38, byte 0x10, bit Mdsel'},PAGE_CODE=(0x0038,),DATA_TO_CHANGE=(0x0001,),PAGE_BYTE_AND_DATA34=(0x1001,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,))  # Set page38 byte 0x10->LAcheck=1 (bit 0)
         except:  # bypass if it doesn't work.
            objMsg.printMsg("Set Page 38, byte 0x10, bit Mdsel Failed. (Hitachi LAcheck).  OK to proceed.")
   ###################################################################################################
   #                                         get_LLB                                                 #
   #                                                                                                 #
   #     This function is used return the Last Logical Block, block size and Protection Information  #
   #of a drive from the 16 byte Read Capacity Command.                                               #
   ###################################################################################################
      def get_LLB(self):

         import struct
         import binascii

         oProc.St(ODT_TP.prm_538_ReadCapacity,COMMAND_WORD_1=(0x9E10,),COMMAND_WORD_7=(0x0020,),TRANSFER_LENGTH=(0x0020,))  # 16 byte Read Capacity
         oProc.St(ODT_TP.prm_508_Disp_RBuff, {'prm_name':'Display Read Buffer 20h'},PARAMETER_3=(0x0020,))
         bufferData = DriveVars["Buffer Data"]
         y = binascii.unhexlify(bufferData)
         #Modify By Sitthipong S.
         if testSwitch.virtualRun:
            LLB, blockSize, Prot = (5859375000,512,0)
         else:
            LLB, blockSize, Prot = struct.unpack(">QLB",y[:13])
         return (LLB,blockSize,Prot)
   ###################################################################################################
   #                                     FDEmode_MFG                                                 #
   #                                                                                                 #
   #     This function contains the commands to set the FDE mode to MFG the state.                   #
   ###################################################################################################
      def FDEmode_MFG(self):

         import FDE_123

         RegisterResultsCallback(FDE_123.CFDE_Seq().customHandler,[32,33,34,35],useCMLogic=0)
         RegisterResultsCallback(FDE_123.CFDE_Seq().customInitiatorHandler, range(80,85), useCMLogic=1)
         Drv_FDE_mode = self.get_drvFDEmode()
         TraceMessage("Running test 577 - verification of credentials - Saved MSID - Setting DIAG state")
         oProc.St(ODT_TP.prm_577_FdeSetDiag)
         Drv_FDE_mode = self.get_drvFDEmode()
         TraceMessage("Running test 577 - verification of credentials - Saved MSID - Setting SETUP state")
         oProc.St(ODT_TP.prm_577_FdeSetSetup)
         Drv_FDE_mode = self.get_drvFDEmode()
         TraceMessage("Running test 577 - verification of credentials - Saved MSID - Setting MFG state")
         oProc.St(ODT_TP.prm_577_FdeSetMfg)
         Drv_FDE_mode = self.get_drvFDEmode()
   ###################################################################################################
   #                                     get_drvFDEmode                                              #
   #                                                                                                 #
   #     This function is used to return the FDEmode value.                                          #
   ###################################################################################################
      def get_drvFDEmode(self):

         oProc.St(ODT_TP.prm_575_Discovery)	# Discovery
         oProc.St(ODT_TP.prm_508_Disp_RBuff, {'prm_name':'Display Read Buffer 20h'},PARAMETER_3=(0x0020,))
         oProc.St(ODT_TP.prm_508_Disp_RBuff, {'prm_name':'Get FDE mode'},PARAMETER_2=(0x0011,),PARAMETER_3=(0x0001,))
         bufferData = DriveVars["Buffer Data"]

         mode = ''
         if bufferData == "00":
            mode = "SETUP"
         if bufferData == "01":
            mode = "DIAG"
         if bufferData == "80":
            mode = "USE"
         if bufferData == "81":
            mode = "MFG"
         TraceMessage("FDE mode value is = %s (%s)"% (bufferData,mode))
         objMsg.printMsg("FDE mode value is = %s (%s)"% (bufferData,mode))
         return (bufferData)
   #************************************************************************************************#
   #************************************************************************************************#
   oODTsup = CODT_Support()
   #************************************************************************************************#
   #************************************************************************************************#
   class CODT_fail(CState):
      """
         Put in your fail sequence code in this class' run() method
      """
      #-------------------------------------------------------------------------------------------------------
      def __init__(self, dut, params={}):
         self.params = params
         depList = []
         CState.__init__(self, dut, depList)
      #-------------------------------------------------------------------------------------------------------
      def run(self):
         objMsg.printMsg('<<< Test failure Handling >>>')
         try:
            tmpFailData = CUtility.copy(self.dut.failureData)  #Because we want a value copy and it has to be deep/nested
            noFailData = 0
         except:
            noFailData = 1
         SetFailSafe()
         try:
            oProc.St(ODT_TP.prm_504_DisplaySense_LastCommand, spc_id=1)  # Display Sense, Last Cmd, Cyl, Hd, Sec, LBA
            oProc.St(ODT_TP.prm_503_Display_Log_Pages,{'prm_name':'Display log page 6'},PAGE_CODE=(0x0006,),SAVE_PARAMETERS=(0x0001,))  # Display Non-Medium Log Page (0x06)
            oProc.St(ODT_TP.prm_503_Display_Log_Pages,{'prm_name':'Display log page 3A'},PAGE_CODE=(0x003A,),SAVE_PARAMETERS=(0x0001,))  # Display Event Log Page (0x3A)
            oProc.St(ODT_TP.prm_529_CheckGrowthDefects,{'prm_name':'Display Glist Flaws - no maximum'},MAX_GLIST_ENTRIES=(0x0000,0xFFFF,))  # Display G-List - no Max
            oProc.St(ODT_TP.prm_529_CheckServoDefects,{'prm_name':'Display Servo Flaws - no maximum'},MAX_SERVO_DEFECTS=(0xFFFF,))  # Display Added Servo Flaws - no Max
            oProc.St(ODT_TP.prm_508_WRT_bytes_to_WBuff, {'prm_name':'Write 8 bytes to WBuff'}, PARAMETER_2=(0x0000,),PARAMETER_3=(0x0008,),PARAMETER_7=(0x0600,),PARAMETER_8=(0x0008,),PARAMETER_9=(0xFFF0,),PARAMETER_10=(0x0304,))  # Unlock hidden DLD command setup
            oProc.St(ODT_TP.prm_508_WRT_bytes_to_WBuff, {'prm_name':'Write 8 bytes to WBuff'}, PARAMETER_2=(0x0008,),PARAMETER_3=(0x0004,),PARAMETER_7=(0x3397,),PARAMETER_8=(0x0000,),PARAMETER_9=(0x0000,),PARAMETER_10=(0x0000,))  # Unlock hidden DLD command setup
            oProc.St(ODT_TP.prm_508_Disp_WBuff, {'prm_name':'Display 10h bytes WBuff'},PARAMETER_3=(0x0010,))
            oProc.St(ODT_TP.prm_538_GetDLD)  # Hidden DLD data
            oProc.St(ODT_TP.prm_602_DLD)  # Dump DLD data
            oProc.St(ODT_TP.prm_538_GetServoCodes)  # Read Servo Fail Loop Code
            oProc.St(ODT_TP.prm_538_GetServoCodes,COMMAND_WORD_2=(0x0109,))  # Read Servo Error Fifo
            oProc.St(ODT_TP.prm_564_DispCumulativeSmart)
            oProc.St(ODT_TP.prm_538_SpinDown)

         except:
            pass
         ClearFailSafe()
         if noFailData == 0:
            self.dut.failureData = tmpFailData
         try:
            oProc.St(ODT_TP.prm_538_SpinDown)
            DriveOff(10)
         except:
            DriveOff(10)

         dict = {}
         dict['MFG_EVAL'] = '?'
         DriveAttributes.update(dict)

         """
         We want to raise an exception below so that the calling method (Setup.py) can report error to
         host and do other standard failure actions like run STPGPD, send parametric data, run DBLog etc.
         NOTE: It is possible to simply handle failure at this level, if that is what you want,
               then comment out the following line and add your failure handling code.
         """
         self.exitStateMachine() # this will throw exception to be handled by top level code in Setup.py

if testSwitch.FE_0164370_395340_P_FIRST_ODT_SEQUENT_TEST_FOR_SATA:
   from Rim import objRimType
   from base_IntfTest import CPackWrite, CFullZeroCheck
   class CBase_ODT(CState):

      #-------------------------------------------------------------------------------------------------------
      def __init__(self, dut, params=[]):
         self.params = params
         depList = []
         self.dut = dut
         CState.__init__(self, dut, depList)

      #-------------------------------------------------------------------------------------------------------
      def run(self):
         self.oProcess = CProcess()
         self.oSerial = sptDiagCmds()
         if ConfigVars[CN].get('MQM_CUT2', 'OFF') == 'OFF' and ConfigVars[CN].get('MQM_RWK', 'OFF') == 'OFF':
            objMsg.printMsg("DON'T NEED ANY CUT2 MQM")
            return
         self.dut.driveattr['MQM_TEST_DONE'] = 'FAIL'
         self.dut.driveattr['MQM_VER'] = '3.1'

         self.DisableUDR()

         objCCustomCfg = CCustomCfg()
         rwMQM = objCCustomCfg.SelectRWKMQM()

         if rwMQM == 'Y' and ConfigVars[CN].get('MQM_RWK', 'OFF') == 'ON':
            objMsg.printMsg("RWK Sequent Test")
            self.dut.driveattr['MQM_RW'] = 'FAIL'

         ret = CIdentifyDevice().ID
         self.maxLBA = ret['IDDefaultLBAs'] - 1
         if ret['IDCommandSet5'] & 0x400:
            self.maxLBA = ret['IDDefault48bitLBAs'] - 1                          #Get Max LBA from drive

         objMsg.printMsg("self.maxLBA : %s" % self.maxLBA)

         self.cap = int((self.maxLBA*512)/1000000000)
         BlkPerXFR = self.SetBlkPerXfer()

         ttlBlkToXFR, start_LBA, end_LBA = self.TotalBlkToXfr(17, 1)

         if ConfigVars[CN].get('MQM_CUT2', 'OFF') == 'ON':
            objMsg.printMsg("ttlBlkToXFR : %s , start_LBA : %s, end_LBA : %s" % (ttlBlkToXFR,start_LBA,end_LBA))
            if objRimType.CPCRiser():

               self.oProcess.St(TP.prm_510_ODT, prm_name='prm_510_RVerify', CTRL_WORD1=(0x40), CTRL_WORD2=(0x2080), STARTING_LBA=(0,0,0,0), TOTAL_BLKS_TO_XFR=ttlBlkToXFR, BLKS_PER_XFR=BlkPerXFR,)  #Sequential Read Verify zone 0 (0 to 1/16*maxLBA)
               self.oProcess.St(TP.prm_510_ODT, prm_name='prm_510_RVerify', CTRL_WORD1=(0x40), CTRL_WORD2=(0x2080), STARTING_LBA=start_LBA,  TOTAL_BLKS_TO_XFR=ttlBlkToXFR, BLKS_PER_XFR=BlkPerXFR,)  #Sequential Read Verify zone 15 (15/16*maxLBA to maxLBA)

               ttlBlkToXFR, start_LBA, end_LBA =self.TotalBlkToXfr(17, 2)
               objMsg.printMsg("ttlBlkToXFR : %s , start_LBA : %s, end_LBA : %s" % (ttlBlkToXFR,start_LBA,end_LBA))

               self.oProcess.St(TP.prm_510_ODT, prm_name='prm_510_SeqW', CTRL_WORD1=(0x20), CTRL_WORD2=(0x1), STARTING_LBA=(0,0,0,0), TOTAL_BLKS_TO_XFR=ttlBlkToXFR, BLKS_PER_XFR=BlkPerXFR,)  #Sequential Write OD ID zone 0-1 (0 to 2/16*maxLBA) Pattern Random
               self.oProcess.St(TP.prm_510_ODT, prm_name='prm_510_SeqW', CTRL_WORD1=(0x20), CTRL_WORD2=(0x1), STARTING_LBA=start_LBA,  TOTAL_BLKS_TO_XFR=ttlBlkToXFR, BLKS_PER_XFR=BlkPerXFR,)  #Sequential Write OD ID zone 14-15 (14/16*maxLBA to maxLBA) Pattern Random

               ttlBlkToXFR, start_LBA, end_LBA =self.TotalBlkToXfr(17, 2)
               self.oProcess.St(TP.prm_510_ODT, prm_name='prm_510_SeqR', CTRL_WORD1=(0x10), CTRL_WORD2=(0x2080), STARTING_LBA=(0,0,0,0), TOTAL_BLKS_TO_XFR=ttlBlkToXFR, BLKS_PER_XFR=BlkPerXFR,)  #Sequential Read OD ID zone 0-1 (0 to 2/16*maxLBA)
               self.oProcess.St(TP.prm_510_ODT, prm_name='prm_510_SeqR', CTRL_WORD1=(0x10), CTRL_WORD2=(0x2080), STARTING_LBA=start_LBA,  TOTAL_BLKS_TO_XFR=ttlBlkToXFR, BLKS_PER_XFR=BlkPerXFR,)  #Sequential Read OD ID zone 14-15 (14/16*maxLBA to maxLBA)

            else:
               from ICmdFactory import ICmd
               #COMPLETE
               result = ICmd.SequentialReadDMAExt(0, ttlBlkToXFR, BlkPerXFR, BlkPerXFR)#, CTRL_WORD1=(0x40), CTRL_WORD2=(0x2080))
               objMsg.printMsg('prm_510_RVerify - Result %s' %str(result))

               result = ICmd.SequentialReadDMAExt(start_LBA, end_LBA, BlkPerXFR, BlkPerXFR)
               objMsg.printMsg('prm_510_RVerify - Result %s' %str(result))

               ttlBlkToXFR, start_LBA, end_LBA =self.TotalBlkToXfr(17, 2)
               objMsg.printMsg("ttlBlkToXFR : %s , start_LBA : %s, end_LBA : %s" % (ttlBlkToXFR,start_LBA,end_LBA))
               result = ICmd.SequentialWriteDMAExt(0, ttlBlkToXFR, BlkPerXFR, BlkPerXFR)
               objMsg.printMsg('prm_510_SeqW - Result %s' %str(result))

               result = ICmd.SequentialWriteDMAExt(start_LBA, end_LBA, BlkPerXFR, BlkPerXFR)
               objMsg.printMsg('prm_510_SeqW - Result %s' %str(result))

               result = ICmd.SequentialReadDMAExt(0, ttlBlkToXFR, BlkPerXFR, BlkPerXFR)
               objMsg.printMsg('prm_510_SeqW - Result %s' %str(result))

               result = ICmd.SequentialReadDMAExt(start_LBA, end_LBA, BlkPerXFR, BlkPerXFR)
               objMsg.printMsg('prm_510_SeqW - Result %s' %str(result))
               #COMPLETE

         if rwMQM == 'Y' and ConfigVars[CN].get('MQM_RWK', 'OFF') == 'ON':
            self.RndWritex25()  #Stop Start 25xRandomWriteDMAExt

         if ConfigVars[CN].get('MQM_CUT2', 'OFF') == 'ON':
            self.Butterfly()

         if rwMQM == 'Y' and ConfigVars[CN].get('MQM_RWK', 'OFF') == 'ON':
            #Increase FPW and FPR
            objCPackWrite = CPackWrite(self.dut,self.params)
            objCFullZeroCheck = CFullZeroCheck(self.dut,self.params)

            objCPackWrite.run()
            objCFullZeroCheck.run()

         self.EnableUDR()
         self.ResetSMART()

         if ConfigVars[CN].get('MQM_CUT2', 'OFF') == 'ON':
            self.dut.driveattr['MQM_TEST_DONE'] = 'PASS'
         if rwMQM == 'Y' and ConfigVars[CN].get('MQM_RWK', 'OFF') == 'ON':
            self.dut.driveattr['MQM_RW'] = 'PASS'

      #-------------------------------------------------------------------------------------------------------
      def DisableUDR(self):
         objPwrCtrl.powerCycle()
         sptCmds.enableDiags()

         data = sptCmds.sendDiagCmd(CTRL_L,printResult=True)
         if data.find('LTTC-UDR2 compiled off') == -1:
            objMsg.printMsg('Attempting to Disable UDR')
            retries = 3
            while retries > 0:
               self.oSerial.gotoLevel('T')
               sptCmds.sendDiagCmd('F5A7,0')
               self.oSerial.gotoLevel('1')
               sptCmds.sendDiagCmd('N23')
               data = sptCmds.sendDiagCmd(CTRL_L)
               if data.find('LTTC-UDR2 disabled') > -1:
                  objMsg.printMsg('UDR successfully disabled.')
                  retries = 0
               else:
                  retries -= 1
         else:
            objMsg.printMsg('DRIVE DOES NOT SUPPORT UDR')
         objPwrCtrl.powerCycle(5000,12000,10,30)

      #-------------------------------------------------------------------------------------------------------
      def EnableUDR(self):
         objPwrCtrl.powerCycle()
         sptCmds.enableDiags()

         data = sptCmds.sendDiagCmd(CTRL_L,printResult=True)
         if data.find('LTTC-UDR2 compiled off') == -1:
            objMsg.printMsg('Attempting to Enable UDR')
            retries = 3
            while retries > 0:
               self.oSerial.gotoLevel('T')
               sptCmds.sendDiagCmd('F5A7,A')
               sptCmds.sendDiagCmd('F,,22')            # To reset AMPs, Which will also make LTTCPowerOnHours changed back to default value (0xA)
               self.oSerial.gotoLevel('1')
               sptCmds.sendDiagCmd('N1')
               sptCmds.sendDiagCmd('N23')
               data = sptCmds.sendDiagCmd(CTRL_L)
               if data.find('LTTC-UDR2 enabled') > -1:
                  objMsg.printMsg('UDR successfully enabled.')
                  retries = 0
               else:
                  retries -= 1
         else:
            objMsg.printMsg('DRIVE DOES NOT SUPPORT UDR')
         objPwrCtrl.powerCycle(5000,12000,10,30)

      #-------------------------------------------------------------------------------------------------------
      def ResetSMART(self):
         objPwrCtrl.powerCycle()
         sptCmds.enableDiags()

         self.oSerial.SmartCmd(TP.smartResetParams_ODT)
         sptCmds.sendDiagCmd(CTRL_L,printResult=True)
         objPwrCtrl.powerCycle(5000,12000,10,30)

      #-------------------------------------------------------------------------------------------------------
      def SmartDSTLongTest(self):
         objMsg.printMsg('Smart DST Long : START')
         starttime = time.time()
         self.oProcess.St(TP.prm_638_Unlock_Seagate)
         self.oProcess.St(TP.prm_600_long)

         total_time = time.time() - starttime
         objPwrCtrl.powerCycle(5000,12000,10,30)

         objMsg.printMsg('Smart DST Long Test Usage : %d' % total_time)
         objMsg.printMsg('Smart DST Long : END')

      #-------------------------------------------------------------------------------------------------------
      def returnStartLbaWords(self, startLBA):
         lowerWord1 = (startLBA & 0xFFFF0000) >> 16
         lowerWord2 = (startLBA & 0x0000FFFF)

         return (lowerWord1,lowerWord2)

      #-------------------------------------------------------------------------------------------------------
      def TotalBlkToXfr(self, ttlzone, numzonetest):
         if objRimType.CPCRiser():
            ttlBlkToXfr = self.returnStartLbaWords(((self.maxLBA/ttlzone)*numzonetest)-1) #maxLBA = 5860533168,344737245
            startLBA = lbaTuple(self.maxLBA - ((self.maxLBA/ttlzone)*numzonetest))
            endLBA   = (self.maxLBA - ((self.maxLBA/ttlzone)*numzonetest)) + (((self.maxLBA/ttlzone)*numzonetest)-1)
         else:
            ttlBlkToXfr = ((self.maxLBA/ttlzone)*numzonetest)-1 #maxLBA = 5860533168,344737245
            startLBA = self.maxLBA - ((self.maxLBA/ttlzone)*numzonetest)
            endLBA = startLBA+ttlBlkToXfr

         return ttlBlkToXfr, startLBA, endLBA

      #-------------------------------------------------------------------------------------------------------
      def SetBlkPerXfer(self):
         if self.cap > 755: BlkPerXfer = (0x0250)
         elif self.cap > 505: BlkPerXfer = (0x0128)
         elif self.cap > 255: BlkPerXfer = (0x0094)
         else: BlkPerXfer = (0x004A)
         return BlkPerXfer

      #-------------------------------------------------------------------------------------------------------
      def RndWritex25(self):
         objMsg.printMsg('25x Random Write : START')
         starttime = time.time()

         loop_count = 25
         prm_510 = TP.prm_510_ODT.copy()
         del prm_510['TOTAL_BLKS_TO_XFR']
         for n in range(loop_count):
            if objRimType.CPCRiser():
               self.oProcess.St({'test_num':506, 'prm_name':'prm_506_SET_RUNTIME', 'spc_id':1, 'TEST_RUN_TIME':60,})  #1 Min Test Time
               self.oProcess.St(TP.prm_510_ODT, prm_name='prm_510_RndW', CTRL_WORD1=(0x21), CTRL_WORD2=(0x2080), STARTING_LBA=(0,0,0,0),  TOTAL_BLKS_TO_XFR=(0x0000,0xC350), BLKS_PER_XFR=(0x10),)  #Random Write 50000 blks
            else:
               self.oProcess.St({'test_num':506, 'prm_name':'prm_506_SET_RUNTIME', 'spc_id':1, 'TEST_RUN_TIME':0,})  #1 Min Test Time
               self.oProcess.St(prm_510, prm_name='prm_510_RndW', CTRL_WORD1=(0x21), CTRL_WORD2=(0x2080), STARTING_LBA=(0,0,0,0),  TOTAL_BLKS_TO_XFR64=(0,0,0x0000,0xC350), BLKS_PER_XFR=(0x10),)  #Random Write 50000 blks

         total_time = time.time() - starttime
         objMsg.printMsg('25x Random Write Test Usage : %d' % total_time)
         objMsg.printMsg('25x Random Write  : END')

      #-------------------------------------------------------------------------------------------------------
      def Butterfly(self):
         objMsg.printMsg('Butterfly : START')
         starttime = time.time()

         prm_506_SET_RUNTIME = {
            'test_num'          : 506,
            'prm_name'          : "prm_506_SET_RUNTIME",
            'spc_id'            :  1,
            "TEST_RUN_TIME"     :  600,                                            #10 Mins Test Time
         }
         prm_510_BUTTERFLY = {
            'test_num'          : 510,
            'prm_name'          : "prm_510_BUTTERFLY",
            'spc_id'            :  1,
            "CTRL_WORD1"        : (0x0422),                                        #Butterfly Sequencetioal Write;Display Location of errors
            "STARTING_LBA"      : (0,0,0,0),
            "BLKS_PER_XFR"      : (0x10),
            "OPTIONS"           : 0,                                               #Butterfly Converging
            "timeout"           :  3000,                                           #15 Mins Test Time
         }

         if self.cap > 755: loop_count = 1
         elif self.cap > 505: loop_count = 2
         elif self.cap > 255: loop_count = 3
         else: loop_count = 4

         objMsg.printMsg('Butterfly Test loop_count : %d' %loop_count)

         for n in range(loop_count):
            objMsg.printMsg("====================== Butterfly Test loop %d ========================="%(n+1))

            self.oProcess.St(prm_506_SET_RUNTIME, TEST_RUN_TIME=600)
            self.oProcess.St(prm_510_BUTTERFLY, prm_name='prm_510_ButterflyInW', CTRL_WORD1=0x0420, OPTIONS=0, BLKS_PER_XFR=(0x10),)  #Butterfly In Write

            self.oProcess.St(prm_506_SET_RUNTIME, TEST_RUN_TIME=600)
            self.oProcess.St(prm_510_BUTTERFLY, prm_name='prm_510_ButterflyInR', CTRL_WORD1=0x0410, OPTIONS=0, BLKS_PER_XFR=(0x10),)  #Butterfly In Read

            if objRimType.CPCRiser():
               self.oProcess.St(prm_506_SET_RUNTIME, TEST_RUN_TIME=1200)
               self.oProcess.St(TP.prm_510_ODT, prm_name='prm_510_RndWRLong', CTRL_WORD1=(0x00), CTRL_WORD2=(0x1), STARTING_LBA=(0,0,0,0),  TOTAL_BLKS_TO_XFR=(0x0000,0xC350), BLKS_PER_XFR=(0x250),) #0x800 #Random WR Long >> Pattern Random
            else:
               prm_510 = TP.prm_510_ODT.copy()
               del prm_510['TOTAL_BLKS_TO_XFR']
               self.oProcess.St(prm_506_SET_RUNTIME, TEST_RUN_TIME=0)
               self.oProcess.St(prm_510, prm_name='prm_510_RndWRLong', CTRL_WORD1=(0x00), CTRL_WORD2=(0x1), STARTING_LBA=(0,0,0,0),  TOTAL_BLKS_TO_XFR64=(0,0,0x0000,0xC350), BLKS_PER_XFR=(0x250),) #0x800 #Random WR Long >> Pattern Random

            self.oProcess.St(prm_506_SET_RUNTIME, TEST_RUN_TIME=600)
            self.oProcess.St(prm_510_BUTTERFLY, prm_name='prm_510_ButterflyOutW', CTRL_WORD1=0x0420, OPTIONS=1, BLKS_PER_XFR=(0x10),)  #Butterfly Out Write

            self.oProcess.St(prm_506_SET_RUNTIME, TEST_RUN_TIME=600)
            self.oProcess.St(prm_510_BUTTERFLY, prm_name='prm_510_ButterflyInR', CTRL_WORD1=0x0410, OPTIONS=1, BLKS_PER_XFR=(0x10),)  #Butterfly Out Read

            if objRimType.CPCRiser():
               self.oProcess.St(prm_506_SET_RUNTIME, TEST_RUN_TIME=1200)
               self.oProcess.St(TP.prm_510_ODT, prm_name='prm_510_RndWRShort', CTRL_WORD1=(0x00), CTRL_WORD2=(0x1), STARTING_LBA=(0,0,0,0),  TOTAL_BLKS_TO_XFR=(0x0000,0xC350), BLKS_PER_XFR=(0x10),)  #Random WR Short >> Pattern Random
            else:
               self.oProcess.St(prm_506_SET_RUNTIME, TEST_RUN_TIME=0)
               self.oProcess.St(prm_510, prm_name='prm_510_RndWRShort', CTRL_WORD1=(0x00), CTRL_WORD2=(0x1), STARTING_LBA=(0,0,0,0),  TOTAL_BLKS_TO_XFR64=(0,0,0x0000,0xC350), BLKS_PER_XFR=(0x10),)  #Random WR Short >> Pattern Random

         self.oProcess.St(prm_506_SET_RUNTIME, TEST_RUN_TIME=0)

         total_time = time.time() - starttime
         objMsg.printMsg('Butterfly Test Usage : %d' % total_time)
         objMsg.printMsg('Butterfly : END')

      #-------------------------------------------------------------------------------------------------------
      def NLSeqWriteVerify(TestType, TestName, StartLocation, EndLocation, SectCount, Pattern):
         P_Msg = ON      # Performance Message
         F_Msg = ON      # Failure Message
         B_Msg = ON      # Buffer Message
         data = {}
         result = OK
         DoRetry = ON
         NL_SEQ_WRITE_VERIFY = OFF

         driveattr['testseq'] = TestName

         if TestName == 'NL Write Vrfy OD':
            if   TestType == ('IDT') and IDT_NL_SEQ_WRT_VERIFY_OD == ON: NL_SEQ_WRITE_VERIFY = ON
            elif TestType == ('MQM') and IDT_NL_SEQ_WRT_VERIFY_OD == ON: NL_SEQ_WRITE_VERIFY = ON

         elif TestName == 'NL Write Vrfy ID':
            if   TestType == ('IDT') and IDT_NL_SEQ_WRT_VERIFY_ID == ON: NL_SEQ_WRITE_VERIFY = ON
            elif TestType == ('MQM') and IDT_NL_SEQ_WRT_VERIFY_ID == ON: NL_SEQ_WRITE_VERIFY = ON

         if NL_SEQ_WRITE_VERIFY == ON:
            result = FinPowerOn(ON,'IDT')
            if result == OK:
               StartTime(TestName, 'funcstart')
               SetRdWrStatsIDE(TestName, 'On')
               TestNum = SetTestNumber(TestType)
               SetIntfTimeout(ConfigVars['Intf Timeout'])
               ReceiveSerialCtrl(1)
               data = {}

               StepLBA = SectCount
               StampFlag = 0
               CompFlag = 1
               BlockSize = 512

               if SectCount > 256:
                  MakeAlternateBuffer(WBF, SectCount)
                  MakeAlternateBuffer(RBF, SectCount)

               MaxLBA = ID_data['Max_48lba']

               StartLBA = StartLocation * MaxLBA
               EndLBA   = EndLocation   * MaxLBA
               StartLBA = long(StartLBA)
               EndLBA = long(EndLBA)
               StatMsg('%s Start LBA=%d End LBA=%d Sect Count=%d' % \
                      (TestName, StartLBA, EndLBA, SectCount))

               StatMsg('%s Flush Cache, Clear Buffers' % TestName )
               FlushCache(); ClearBinBuff(WBF);  ClearBinBuff(RBF)

               if Pattern == 'Random':
                  StatMsg('%s Fill Random Pattern Data' % TestName )
                  Seed(1); FillBuffRandom(WBF)
               else:
                  StatMsg('%s Fill Zero Pattern Data' % TestName )
                  FillBuffByte(WBF, 0x00)
               if B_Msg:
                  StatMsg('%s Write Buffer Data ----------------------------------------' % TestName)
                  wb_data = GetBuffer(WBF, 0, 550)['DATA']
                  StatMsg('%s %s' % (TestName, wb_data[0:20]))
                  StatMsg('%s %s' % (TestName, wb_data[512:532]))

               xfer_key = ('%s_wrt_xfer' % TestType)
               result = SetFeatures(0x03, ID_data[xfer_key])['LLRET']
               if result != OK:
                  StatMsg('%s Failed SetFeatures - Transfer Rate = UDMA-%d' % (TestName, GetUDMASpeed(xfer_key)))
               else:
                  StatMsg('%s Passed SetFeatures - Transfer Rate = UDMA-%d' % (TestName, GetUDMASpeed(xfer_key)))
               result = SetFeatures(0x02)['LLRET']
               if result != OK:
                  StatMsg('%s Failed SetFeatures - Enable Write Cache' % (TestName))
               else:
                  StatMsg('%s Passed SetFeatures - Enable Write Cache' % (TestName))

               Retry = 1
               for loop in range(Retry+1):
                   CmdStartTime = time.time()
                   if driveattr['48_Bit_Congen'] == 'ON':
                      data = SequentialWRDMAExt(StartLBA, EndLBA, StepLBA, SectCount, StampFlag, CompFlag)
                   else:
                      data = SequentialWriteReadDMALBA(StartLBA, EndLBA, StepLBA, SectCount, StampFlag, CompFlag)
                   CmdEndTime = time.time()
                   StatMsg('%s SequentialWriteReadDMALBA - Returned data: %s' % (TestName, data) )
                   result = data['LLRET']
                   if result != OK and DoRetry == ON:
                      RetryTest = CheckRetryTest(data['RESULT'], data.get('STS','NIL'), data.get('ERR','NIL'))
                      if RetryTest != ON: break
                      StatMsg('%s SequentialWriteReadDMALBA - Loop Number %d of %d Failed - Do Retry' % (TestName, loop+1, Retry+1))
                      StatMsg('%s SequentialWriteReadDMALBA - Retry - Power Cycle and Re-issue CPC Embedded Command' % TestName)
                      GetSerialPortData()
                      result = FinPowerOn(ON,'IDT')
                      if result == OK:
                         SetRdWrStatsIDE(TestName, 'On')
                      else: break
                   else: break

            if result != OK:
               StatMsg('%s Failed Result=%s Data=%s' % (TestName, result, data))
               if data.has_key('LBA') == 0: data['LBA'] = '0'
               if data.has_key('STS') == 0: data['STS'] = '00'
               if data.has_key('ERR') == 0: data['ERR'] = '00'
               driveattr['faillba'] = data['LBA']
               failure = ('%s %s' % (TestType, TestName))
               driveattr['failcode'] = failcode[failure]
               failstatus = ('%s-%s-%s' % (driveattr['failcode'][0],int(data['STS']),int(data['ERR'])))
               driveattr['failstatus'] = failstatus
            else:
               if P_Msg:
                  StatMsg('%s Write Performance ------------------------------------' % TestName)
                  NumCmds=((EndLBA-StartLBA)/SectCount); BlocksXfrd=(EndLBA-StartLBA); CmdTime=(CmdEndTime-CmdStartTime)
                  DisplayPerformance(TestName,NumCmds,BlocksXfrd,BlockSize,CmdTime)

            if SectCount > 256:
               RestorePrimaryBuffer(WBF)
               RestorePrimaryBuffer(RBF)
            EndTime(TestName, 'funcstart', 'funcfinish', 'functotal')
            DisplayCmdTimes(TestName, 'CPC', float(data.get('CT','0'))/1000, SectCount)

            if result == OK and IDT_RESULT_FILE_DATA == ON:
               TestTime = timetostring(testtime['functotal'])
               CollectData(result, TestType, TestNum, TestName, TestTime, CheckBER=0)
            StatMsg('*****************************************************************************')

         else:
            StatMsg('%s Test OFF' % TestName)
            StatMsg('*****************************************************************************')

         return result

      #-------------------------------------------------------------------------------------------------------
      def NLSeqRead(TestType, TestName, StartLocation, EndLocation, SectCount):
         P_Msg = ON      # Performance Message
         F_Msg = ON      # Failure Message
         B_Msg = ON      # Buffer Message
         data = {}
         result = OK
         DoRetry = ON
         NL_SEQ_READ = OFF

         if TestName   == 'NL Read OD':
            if   TestType == ('IDT') and IDT_NL_SEQ_READ_OD == ON: NL_SEQ_READ = ON
            elif TestType == ('MQM') and IDT_NL_SEQ_READ_OD == ON: NL_SEQ_READ = ON

         elif TestName == 'NL Read ID':
            if   TestType == ('IDT') and IDT_NL_SEQ_READ_ID == ON: NL_SEQ_READ = ON
            elif TestType == ('MQM') and IDT_NL_SEQ_READ_ID == ON: NL_SEQ_READ = ON

         elif TestName == 'NL Seq Read Full':
            if   TestType == ('IDT') and IDT_NL_SEQ_READ_FULL == ON: NL_SEQ_READ = ON
            elif TestType == ('MQM') and IDT_NL_SEQ_READ_FULL == ON: NL_SEQ_READ = ON

         driveattr['testseq'] = TestName

         if NL_SEQ_READ == ON:
            result = FinPowerOn(ON,'IDT')
            if result == OK:
               StartTime(TestName, 'funcstart')
               SetRdWrStatsIDE(TestName, 'On')
               TestNum = SetTestNumber(TestType)
               SetIntfTimeout(ConfigVars['Intf Timeout'])
               ReceiveSerialCtrl(1)
               StepLBA = SectCount
               StampFlag = 0
               CompFlag = 0
               BlockSize = 512

               if SectCount > 256:
                  MakeAlternateBuffer(RBF, SectCount)

               MaxLBA = ID_data['Max_48lba']

               StartLBA = StartLocation * MaxLBA
               EndLBA   = EndLocation   * MaxLBA
               StartLBA = long(StartLBA)
               EndLBA = long(EndLBA)
               StatMsg('%s Start LBA=%d End LBA=%d Sect Count=%d' % \
                      (TestName, StartLBA, EndLBA, SectCount))

               StatMsg('%s Flush Cache, Clear Buffers' % TestName)
               FlushCache(); ClearBinBuff(WBF);  ClearBinBuff(RBF)
               if B_Msg:
                  StatMsg('%s Write Buffer Data ----------------------------------------' % TestName)
                  wb_data = GetBuffer(WBF, 0, 550)['DATA']
                  StatMsg('%s %s' % (TestName, wb_data[0:20]))
                  StatMsg('%s %s' % (TestName, wb_data[512:532]))

               xfer_key = ('%s_rd_xfer' % TestType)
               result = SetFeatures(0x03, ID_data[xfer_key])['LLRET']
               if result != OK:
                  StatMsg('%s Failed SetFeatures - Transfer Rate = UDMA-%d' % (TestName, GetUDMASpeed(xfer_key)))
               else:
                  StatMsg('%s Passed SetFeatures - Transfer Rate = UDMA-%d' % (TestName, GetUDMASpeed(xfer_key)))

               Retry = 1
               for loop in range(Retry+1):
                   CmdStartTime = time.time()
                   if driveattr['48_Bit_Congen'] == 'ON':
                      data = SequentialReadDMAExt(StartLBA, EndLBA, StepLBA, SectCount, StampFlag, CompFlag)
                   else:
                      data = SequentialReadDMALBA(StartLBA, EndLBA, StepLBA, SectCount, StampFlag, CompFlag)
                   CmdEndTime = time.time()
                   StatMsg('%s SequentialReadDMALBA - Returned data: %s' % (TestName, data) )
                   result = data['LLRET']
                   if result != OK and DoRetry == ON:
                      RetryTest = CheckRetryTest(data['RESULT'], data.get('STS','NIL'), data.get('ERR','NIL'))
                      if RetryTest != ON: break
                      StatMsg('%s SequentialReadDMALBA - Loop Number %d of %d Failed - Do Retry' % (TestName, loop+1, Retry+1))
                      StatMsg('%s SequentialReadDMALBA - Retry - Power Cycle and Re-issue CPC Embedded Command' % TestName)
                      GetSerialPortData()
                      result = FinPowerOn(ON,'IDT')
                      if result == OK:
                         SetRdWrStatsIDE(TestName, 'On')
                      else: break
                   else: break

                   if B_Msg or result != OK:
                      StatMsg('%s Read Buffer Data ----------------------------------------' % TestName)
                      rb_data = GetBuffer(RBF, 0, 550)['DATA']
                      StatMsg('%s %s' % (TestName, rb_data[0:20]))
                      StatMsg('%s %s' % (TestName, rb_data[512:532]))

            if result != OK:
               StatMsg('%s Test Failed Result=%s' % (TestName, result))
               if data.has_key('LBA') == 0: data['LBA'] = '0'
               if data.has_key('STS') == 0: data['STS'] = '00'
               if data.has_key('ERR') == 0: data['ERR'] = '00'
               if data.has_key('RESULT') == 0: data['RESULT'] = '0'
               if F_Msg: StatMsg('%s Data = %s' % (TestName, data))
               if F_Msg: StatMsg('%s Error = %s' % (TestName, data['ERR']))
               if F_Msg: StatMsg('%s Result = %s' % (TestName, data['RESULT']))
               if F_Msg: StatMsg('%s SequentialReadVerifyLBA lba=%s result=%s' % (TestName, data['LBA'], result))
               driveattr['faillba']  = data['LBA']
               failure = ('%s %s' % (TestType, TestName))
               driveattr['failcode'] = failcode[failure]
               failstatus = ('%s-%s-%s' % (driveattr['failcode'][0],int(data['STS']),int(data['ERR'])))
               driveattr['failstatus'] = failstatus
            else:
               if P_Msg:
                  StatMsg('%s Read Performance -------------------------------------' % TestName)
                  NumCmds=((EndLBA-StartLBA)/SectCount); BlocksXfrd=(EndLBA-StartLBA); CmdTime=(CmdEndTime-CmdStartTime)
                  DisplayPerformance(TestName,NumCmds,BlocksXfrd,BlockSize,CmdTime)

            if SectCount > 256:
               RestorePrimaryBuffer(RBF)
            EndTime(TestName, 'funcstart', 'funcfinish', 'functotal')
            DisplayCmdTimes(TestName, 'CPC', float(data.get('CT','0'))/1000, SectCount)

            if result == OK and IDT_RESULT_FILE_DATA == ON:
               TestTime = timetostring(testtime['functotal'])
               CollectData(result, TestType, TestNum, TestName, TestTime)
            StatMsg('*****************************************************************************')

         else:
            StatMsg('%s Test OFF' % TestName)
            StatMsg('*****************************************************************************')

         return result
