#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: base Serial Port CAL states
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
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_qualityMQM.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_qualityMQM.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
from State import CState
import MessageHandler as objMsg
from PowerControl import objPwrCtrl
#from serialScreen import serialScreen
import sptCmds
import ScrCmds
import traceback
import time
import re
import string

#----------------------------------------------------------------------------------------------------------
class CSFMT_MQMBEATUP(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      # Do beat up by total entries number of V40
      self.oSerial = sptDiagCmds()
      forceBeatup = 0
      try:
         objPwrCtrl.powerCycle(useESlip=1)
         self.oSerial.enableDiags()
         TotalEntries = self.oSerial.dumpV40TotalEntries()
         objMsg.printMsg('Return TotalEntries = %s' % TotalEntries)
      except:
         objMsg.printMsg('Exception when get V40 entries.')
         objMsg.printMsg(traceback.format_exc())
         try:
            TotalEntries = self.oSerial.dumpNonResidentGList()
         except:
            pass
         forceBeatup = 1
      if forceBeatup or TotalEntries['numEntries'] > 100:
         self.oSerial.enableDiags()
         self.ObjEncroTest = CEncroTestByZone(self.dut)
         self.ObjEncroTest.fullpackBeatUp()
      return


#----------------------------------------------------------------------------------------------------------
class CEncroTestByZone(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      self.dut = dut
      depList = []
      CState.__init__(self, dut, depList)

      self.oSerial = sptDiagCmds()
      self.startcyl = []
      self.endcyl = []
      self.headnum = []
      self.Span = []
      self.headnum_sp = []
      self.zone_sp = []
      self.startcyl_sp = []
      self.endcyl_sp = []
      self.start_end = []         # Record max cylinder by head.
      self.ignoreDiag = ['00003003', '00003000', '00003010']
      self.ignoreRWerror = ['00000080', '00000000']
      self.bIsNeedG2P = False
      self.fullpackwriteonly = 0
      self.errCnt = 0
      self.retry = 'Y6,F'
      if self.dut.partNum[5] in ['C']:
         self.LDPC = 'D03,00'
      else:
         self.LDPC = 'D02,01'

   #-------------------------------------------------------------------------------------------------------
   def setCylList(self, startcyl, endcyl, headnum, Span):
      self.startcyl = startcyl
      self.endcyl = endcyl
      self.headnum = headnum
      self.Span = Span
      if (len(self.startcyl) != len(self.endcyl)) or (len(self.endcyl) != len(self.headnum)) or (len(self.headnum) != len(self.Span)):
         ScrCmds.raiseException(11044, "Input parameter error.")

   #-------------------------------------------------------------------------------------------------------
   def setHDZNList(self, headznList={}):
      for hd in headznList.keys():
         for zn in headznList[hd]:
            self.headnum_sp.append(int(hd))
            self.zone_sp.append(int(zn))
      objMsg.printMsg('headnum_sp=%s, zone_sp=%s' % (self.headnum_sp, self.zone_sp))
      for retry in range(3):
         self.oSerial.enableDiags()
         numCyls_sum, zones_sum = self.oSerial.getZoneInfo(printResult = True)
         objMsg.printMsg('numCyls=%s, zones=%s' % (numCyls_sum, zones_sum))
         # eg. zones={1: {0: 0}}
         if self.dut.imaxHead != TP.numHeads:
            objMsg.printMsg('GET ZONE TABLE NOT CORRECT, RETRY')
         else:
            break
      for num in range(len(self.headnum_sp)):
         self.startcyl_sp.append(zones_sum[self.headnum_sp[num]][self.zone_sp[num]])
         try:
            self.endcyl_sp.append(zones_sum[self.headnum_sp[num]][self.zone_sp[num]+1] - 1)
         except:
            self.endcyl_sp.append(numCyls_sum[self.headnum_sp[num]])                     # If set zone+1 exception, then use current head max cylinder.
      objMsg.printMsg('After translate, special test head and zone list as below:')
      objMsg.printMsg('SP HEAD LIST = %s' % self.headnum_sp)
      objMsg.printMsg('SP START CYLINDER LIST = %s' % self.startcyl_sp)
      objMsg.printMsg('SP END CYLINDER LIST = %s' % self.endcyl_sp)
      if (len(self.startcyl_sp) != len(self.endcyl_sp)) or (len(self.endcyl_sp) != len(self.headnum_sp)):
         ScrCmds.raiseException(11044, "Input parameter error.")

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      self.oSerial.enableDiags()
      length = len(self.headnum)+len(self.headnum_sp)
      if length > 0 :
         self.setupErrorLogging()
         self.getStartEndCyl()
         self.WriteReadByZone()
         if self.startcyl_sp != []:
            self.WriteReadByZone_SP()
         self.checkError()

         if self.bIsNeedG2P:
            objMsg.printMsg('Has defect trk, need run G2P and Full pack write')
            self.addLBA2AltList()
            self.G2P()
            self.SequentialWrite()
      else:
         objMsg.printMsg("Skip do MQM,because of no defect!")

   #-------------------------------------------------------------------------------------------------------
   def fullpackBeatUp(self):
      self.oSerial.enableDiags()
      self.setupErrorLogging()
      for i in range(2):
         try:
            self.getStartEndCyl()
            self.WriteReadFullPack()
            break
         except:
            objMsg.printMsg('BEATUP WRITE READ EXCEPT, RERUN.')
            objMsg.printMsg(traceback.format_exc())
            objPwrCtrl.powerCycle(5000,12000,10,30)
            self.oSerial.enableDiags()
            self.setupErrorLogging()
      else:
         objMsg.printMsg('BEATUP WRITE READ EXCEPT HAPPEN, FORCE RUN FULL PACK WRITE.')
         self.fullpackwriteonly = 1
      self.checkError()

      if self.bIsNeedG2P:
         objMsg.printMsg('Has defect trk, need run G2P and Full pack write')
         self.addLBA2AltList()
         self.G2P()
         self.SequentialWrite()
      elif self.fullpackwriteonly:
         self.SequentialWrite()

   #-------------------------------------------------------------------------------------------------------
   def GetDefectZone(self):
      bIsNeedScreen = True
      DELTA_RATE = self.params.get('DELTA_RATE', 2.0)
      objMsg.printMsg('DELTA_RATE : %.2f' % DELTA_RATE)
      try:
         berTable = self.dut.dblData.Tables('P_FORMAT_ZONE_ERROR_RATE').tableDataObj()
      except:
         objMsg.printMsg('Attention!!! Can not fine P_table: P_FORMAT_ZONE_ERROR_RATE')
         bIsNeedScreen = False
         return bIsNeedScreen

      for item in berTable:
         if (float(item['BITS_READ_LOG10'])-float(item['HARD_ERROR_RATE']) >= DELTA_RATE):
            self.Defect_Zone[int(item['HD_PHYS_PSN'])].append(int(item['DATA_ZONE']))

      objMsg.printMsg('Defect_Zone: %s' % self.Defect_Zone)

      objMsg.printMsg('Check the Defect_Zone if is empty')
      checklen = 0
      for hd in self.Defect_Zone:
         checklen = checklen + len(self.Defect_Zone[hd])

      if checklen == 0:
         bIsNeedScreen = False
         objMsg.printMsg('Defect_Zone is empty, no reed run screen')

      return bIsNeedScreen

   #-------------------------------------------------------------------------------------------------------
   def setupErrorLogging(self, nLog = 0x10):
      """
      This function will be used to record error for mapping use
      """
      objMsg.printMsg("Setting up error logging")
      self.oSerial.flush()
      time.sleep(1)
      self.oSerial.gotoLevel('L')

      self.oSerial.flush()
      time.sleep(5)
      self.oSerial.sendDiagCmd('c%X,0,0,240000'%nLog, printResult = True)
      self.oSerial.flush()
      time.sleep(5)
      self.oSerial.sendDiagCmd('E%X'%nLog, printResult = True)
      self.oSerial.flush()
      time.sleep(5)
      res = self.oSerial.sendDiagCmd('i%X'%nLog, printResult = True)
      self.oSerial.flush()
      time.sleep(5)
      try:
         self.oSerial.sendDiagCmd('I\r', timeout=60, printResult = True)
      except:
         time.sleep(5)
         self.oSerial.flush()
         objMsg.printMsg("command I failed")
         try:     self.oSerial.sendDiagCmd('\r', printResult = True)
         except:
            accumulator = self.oSerial.PBlock(CTRL_Z)
            time.sleep(1)
            data = sptCmds.promptRead(10,0,accumulator = accumulator)
      self.oSerial.flush()
      time.sleep(5)
      self.errLoggingEnabled = 1
      self.oSerial.sendDiagCmd('E0', printResult = True)

   #-------------------------------------------------------------------------------------------------------
   def WriteReadByZone(self):
      loop = 1
      self.oSerial.sendDiagCmd('E10', printResult = True)
      for num in range(len(self.headnum)):
         objMsg.printMsg("head = %x, Span = %x" %(self.headnum[num], self.Span[num]))
         if self.Span[num] <= 8:
            start_cyl = max(0, self.startcyl[num]-50)
            end_cyl = min(self.endcyl[num]+50, self.start_end[self.headnum[num]])
         elif self.Span[num] > 8 and self.Span[num] <= 30 and self.start_end[self.headnum[num]] != 0:
            start_cyl = max(0, self.startcyl[num]-50)
            end_cyl = min(self.endcyl[num]+50, self.start_end[self.headnum[num]])
         elif self.Span[num] > 30 and self.start_end[self.headnum[num]] != 0:
            start_cyl = max(0, self.startcyl[num]-50)
            end_cyl = min(self.endcyl[num]+50, self.start_end[self.headnum[num]])
         else:
            start_cyl = self.startcyl[num]
            end_cyl = self.endcyl[num]

         self.oSerial.sendDiagCmd('AD', printResult = True)
         #set range
         objMsg.printMsg("start_cyl = %x, end_cyl = %x" %(start_cyl, end_cyl))
         self.oSerial.sendDiagCmd('A8,%x,,%x' % (start_cyl, self.headnum[num]), printResult = True, DiagErrorsToIgnore = self.ignoreDiag, RWErrorsToIgnore = self.ignoreRWerror)
         self.oSerial.sendDiagCmd('A9,%x,,%x' % (end_cyl, self.headnum[num]), printResult = True, DiagErrorsToIgnore = self.ignoreDiag, RWErrorsToIgnore = self.ignoreRWerror)

         for i in range(loop):
            # self.oSerial.sendDiagCmd('E0', printResult = True)
            self.Write('odd', start_cyl, int(self.headnum[num]))
         self.oSerial.gotoLevel('L')
         self.oSerial.sendDiagCmd('E10', printResult = True)
         self.Read('even', start_cyl, int(self.headnum[num]))
         self.oSerial.gotoLevel('L')
         self.oSerial.sendDiagCmd('E0', printResult = True)
         for i in range(loop):
            self.Write('even', start_cyl, int(self.headnum[num]))
         self.oSerial.gotoLevel('L')
         self.oSerial.sendDiagCmd('E10', printResult = True)
         self.Read('odd', start_cyl, int(self.headnum[num]))
   
   #-------------------------------------------------------------------------------------------------------
   def WriteReadByZone_SP(self):
      loop = 2
      self.oSerial.sendDiagCmd('E10', printResult = True)
      for num in range(len(self.headnum_sp)):
         objMsg.printMsg("head = %x" %(self.headnum_sp[num]))
         self.oSerial.sendDiagCmd('AD', printResult = True)
         #set range
         start_cyl = self.startcyl_sp[num]
         end_cyl = self.endcyl_sp[num]

         objMsg.printMsg("start_cyl = %x, end_cyl = %x" %(start_cyl, end_cyl))
         self.oSerial.sendDiagCmd('A8,%x,,%x' % (start_cyl, self.headnum_sp[num]), printResult = True, DiagErrorsToIgnore = self.ignoreDiag, RWErrorsToIgnore = self.ignoreRWerror)
         self.oSerial.sendDiagCmd('A9,%x,,%x' % (end_cyl, self.headnum_sp[num]), printResult = True, DiagErrorsToIgnore = self.ignoreDiag, RWErrorsToIgnore = self.ignoreRWerror)

         for i in range(loop):
            # self.oSerial.sendDiagCmd('E0', printResult = True)
            self.Write('odd', start_cyl, int(self.headnum_sp[num]))
         self.oSerial.gotoLevel('L')
         self.oSerial.sendDiagCmd('E10', printResult = True)
         self.Read('even', start_cyl, int(self.headnum_sp[num]))
         self.oSerial.gotoLevel('L')
         self.oSerial.sendDiagCmd('E0', printResult = True)
         for i in range(loop):
            self.Write('even', start_cyl, int(self.headnum_sp[num]))
         self.oSerial.gotoLevel('L')
         self.oSerial.sendDiagCmd('E10', printResult = True)
         self.Read('odd', start_cyl, int(self.headnum_sp[num]))
   
   #-------------------------------------------------------------------------------------------------------
   def WriteReadFullPack(self):
      loop = 1
      start_cyl = 0
      self.oSerial.sendDiagCmd('E10', printResult = True)
      for num in range(self.dut.imaxHead):
         objMsg.printMsg("head = %x" %(num))
         self.oSerial.sendDiagCmd('AD', printResult = True)

         for i in range(loop):
            objMsg.printMsg("write odd!")
            self.Write('odd', start_cyl, int(num))
         self.oSerial.gotoLevel('L')
         self.oSerial.sendDiagCmd('E10', printResult = True)
         objMsg.printMsg("read even!")
         self.Read('even', start_cyl, int(num))
         self.oSerial.gotoLevel('L')
         self.oSerial.sendDiagCmd('E0', printResult = True)
         for i in range(loop):
            objMsg.printMsg("write even!")
            self.Write('even', start_cyl, int(num))
         self.oSerial.gotoLevel('L')
         self.oSerial.sendDiagCmd('E10', printResult = True)
         objMsg.printMsg("read odd!")
         self.Read('odd', start_cyl, int(num))
   
   #-------------------------------------------------------------------------------------------------------
   def getStartEndCyl(self,):
      self.start_end = []
      time.sleep(5)
      self.oSerial.flush()
      self.oSerial.gotoLevel('T')
      res = self.oSerial.sendDiagCmd('AD', 60, printResult = True, stopOnError = False)

      MAXcyl=[]
      m = re.search("Hd 0 Cyls", res)
      if m != None:
         cyl_list = res[m.start():].split('\r\n')
         for hd in range(self.dut.imaxHead):
            if cyl_list[hd].find('Hd %d' % hd) >= 0:
               self.start_end.append(int(cyl_list[hd].split(' - ')[1],16))
            else:
               self.start_end.append(0)
      return 0

   #-------------------------------------------------------------------------------------------------------
   def Write(self, opt='odd', startcyl=0, hd=0):
      fullPackTimeout = 60*40*TP.numHeads   #40 mins per hd
      self.oSerial.gotoLevel('2')
      self.oSerial.sendDiagCmd('S%x,%x' % (startcyl, hd), printResult = True, DiagErrorsToIgnore = self.ignoreDiag, RWErrorsToIgnore = self.ignoreRWerror)
      self.oSerial.sendDiagCmd('P0,0', printResult = True, DiagErrorsToIgnore = self.ignoreDiag, RWErrorsToIgnore = self.ignoreRWerror)
      if opt == 'odd':
         self.oSerial.sendDiagCmd('A22', printResult = True, DiagErrorsToIgnore = self.ignoreDiag, RWErrorsToIgnore = self.ignoreRWerror)
      elif opt == 'even':
         self.oSerial.sendDiagCmd('A12', printResult = True, DiagErrorsToIgnore = self.ignoreDiag, RWErrorsToIgnore = self.ignoreRWerror)
      else:
         self.oSerial.sendDiagCmd('A2', printResult = True, DiagErrorsToIgnore = self.ignoreDiag, RWErrorsToIgnore = self.ignoreRWerror)
      self.oSerial.sendDiagCmd('L41', printResult = True, DiagErrorsToIgnore = self.ignoreDiag, RWErrorsToIgnore = self.ignoreRWerror)
      try:
         self.oSerial.sendDiagCmd('W,,,,1', timeout = fullPackTimeout, printResult = True, stopOnError = True, DiagErrorsToIgnore = self.ignoreDiag, RWErrorsToIgnore = self.ignoreRWerror)
      except:
         self.oSerial.sendDiagCmd('W,,,,1', timeout = fullPackTimeout, printResult = True, stopOnError = False, DiagErrorsToIgnore = self.ignoreDiag, RWErrorsToIgnore = self.ignoreRWerror)
   
   #-------------------------------------------------------------------------------------------------------
   def Read(self, opt='odd', startcyl=0, hd=0):
      fullPackTimeout = 60*40*TP.numHeads   #40 mins per hd
      self.oSerial.gotoLevel('2')
      self.oSerial.sendDiagCmd('S%x,%x' % (startcyl, hd), printResult = True, DiagErrorsToIgnore = self.ignoreDiag, RWErrorsToIgnore = self.ignoreRWerror)
      self.oSerial.sendDiagCmd(self.retry, printResult = True, DiagErrorsToIgnore = self.ignoreDiag, RWErrorsToIgnore = self.ignoreRWerror)
      # self.oSerial.sendDiagCmd(self.LDPC, printResult = True, DiagErrorsToIgnore = self.ignoreDiag, RWErrorsToIgnore = self.ignoreRWerror)
      if opt == 'odd':
         self.oSerial.sendDiagCmd('A22', printResult = True, DiagErrorsToIgnore = self.ignoreDiag, RWErrorsToIgnore = self.ignoreRWerror)
      elif opt == 'even':
         self.oSerial.sendDiagCmd('A12', printResult = True, DiagErrorsToIgnore = self.ignoreDiag, RWErrorsToIgnore = self.ignoreRWerror)
      else:
         self.oSerial.sendDiagCmd('A2', printResult = True, DiagErrorsToIgnore = self.ignoreDiag, RWErrorsToIgnore = self.ignoreRWerror)
      self.oSerial.sendDiagCmd('L41', printResult = True, DiagErrorsToIgnore = self.ignoreDiag, RWErrorsToIgnore = self.ignoreRWerror)
      self.oSerial.sendDiagCmd('R,,,,1', timeout = fullPackTimeout, printResult = True, stopOnError = False, DiagErrorsToIgnore = self.ignoreDiag, RWErrorsToIgnore = self.ignoreRWerror)

   #-------------------------------------------------------------------------------------------------------
   def checkError(self):
      result = -1
      cnt = 0
      objMsg.printMsg("Check Error Count")

      time.sleep(5)
      self.oSerial.flush()
      try:
         objMsg.printMsg("Check Error Count -- goto level L")
         self.oSerial.gotoLevel('L')
      except:
         objMsg.printMsg("Check Error Count ctrl z")
         time.sleep(5)
         self.oSerial.flush()
         accumulator = self.oSerial.PBlock(CTRL_Z)
         time.sleep(1)
         data = sptCmds.promptRead(10,0,accumulator = accumulator)
         objMsg.printMsg("Check Error Count -- goto level L")
         time.sleep(5)
         self.oSerial.flush()
         self.oSerial.gotoLevel('L')
      time.sleep(5)
      self.oSerial.flush()
      res = self.oSerial.sendDiagCmd('E0',60, printResult = True)
      time.sleep(5)
      self.oSerial.flush()
      res = self.oSerial.sendDiagCmd('D\r', 600, printResult = True)
      if testSwitch.virtualRun:
         res = """
               Count DIAGERR  RWERR    LBA      PBA      SFI      WDG  LLL CHS         PLP CHS         Partition
               ----- -------- -------- -------- -------- -------- ---- --------------- --------------- ---------
               0A9C  00003010 00000000 000000000000 000000000000 00000009 0000 000059F2.0.0000 00000000.0.0000 User
               """

      m = re.search("Partition", res)
      if m != None:
         m = res[m.end():]
         cnt = string.count(res, "User")
         if cnt == 0:
            result = OK
         else:
            m = m.splitlines()
            for line in m:
               if line.find("User")>=0:
                  line = line.split()
                  if line[2][:2] == '40' or line[2] == '00000000' or line[2] == '00000080':
                     cnt = cnt - 1
            if cnt == 0:
               result = OK

      if result != OK:
         self.bIsNeedG2P = True
      self.errCnt = cnt
      if cnt > getattr(TP,'Read_Error_Cnt_SFT', 200) and not testSwitch.virtualRun:
         ScrCmds.raiseException(12345, "Read Error Cnt Out Of Limit")

      return 0
   
   #-------------------------------------------------------------------------------------------------------
   def addLBA2AltList(self):
      """
      Added LBA to Alternate List
      """
      objMsg.printMsg("Exec D10 defect processing")
      try:
         self.oSerial.gotoLevel('L')
      except:
         self.oSerial.PChar(CTRL_Z)
         time.sleep(1)
         self.oSerial.gotoLevel('L')
      self.oSerial.sendDiagCmd('E0', printResult = True, stopOnError = False)
      res = self.oSerial.sendDiagCmd('D\r', 600, printResult = True, stopOnError = False)
      if testSwitch.virtualRun:
         res = """
               Count DIAGERR  RWERR    LBA      PBA      SFI      WDG  LLL CHS         PLP CHS         Partition
               ----- -------- -------- -------- -------- -------- ---- --------------- --------------- ---------
               0A9C  00003010 00000000 000000000000 000000000000 00000009 0000 000059F2.0.0000 00000000.0.0000 User
               """

      m = re.search("Partition", res)
      if m != None:
         m = res[m.end():]
         m = string.split(m)
         cnt = string.count(res, "User")

         time.sleep(5)
         try:
            self.oSerial.gotoLevel('2')
            time.sleep(5)
         except:
            objMsg.printMsg("REPEAT GO TO LEVEL 2")
            self.oSerial.gotoLevel('2')
            time.sleep(5)
            self.oSerial.gotoLevel('2')

         for i in range(cnt):
            objMsg.printMsg("m[%d]: %s" % (12+i*10,m[12+i*10]), objMsg.CMessLvl.IMPORTANT)
            objMsg.printMsg("m[%d]: %s" % (13+i*10,m[13+i*10]), objMsg.CMessLvl.IMPORTANT)
            if m[12+i*10] == '00000000' or m[12+i*10] == '00000080' or m[12+i*10][:2] == '40':
               continue
            lba = int(m[13+i*10], 16)
            cmd = 'F%X,A1'%lba
            try:
               self.oSerial.sendDiagCmd(cmd, timeout=10, printResult = True, stopOnError = True)
            except:
               pass
      else:
         if not testSwitch.virtualRun:
            ScrCmds.raiseException(12346, "Cannot find keyword 'Partition'")

   #-------------------------------------------------------------------------------------------------------
   def G2P(self):
      objMsg.printMsg('Run G2P')
      retries = self.params.get('G2P_retries', 2)
      for i in range(retries+1):
         try:
            self.oSerial.gotoLevel('T')
            self.oSerial.sendDiagCmd('V4', printResult = True)
            G2P_Time = 600*(i+1)
            self.oSerial.sendDiagCmd('m0,6,3,,,,,22', timeout = G2P_Time, printResult = True)
            break
         except:
            objMsg.printMsg('G2P Failed, rerun!')
            objPwrCtrl.powerCycle(5000,12000,10,30)
            self.oSerial.enableDiags()
      else:
         ScrCmds.raiseException(12346, "G2P FAIL")
   
   #-------------------------------------------------------------------------------------------------------
   def SequentialWrite(self):
      objMsg.printMsg('Full Pack LBA Write After G2P')
      fullPackTimeout = 60*150*self.dut.imaxHead   #100 mins per hd
      retries = self.params.get('SeqW_retries', 3)

      for i in range(retries):
         try:
            # self.oSerial.gotoLevel('L')
            # self.oSerial.sendDiagCmd('E10', printResult = True)
            self.oSerial.gotoLevel('2')
            self.oSerial.sendDiagCmd('AD', printResult = True)
            self.oSerial.sendDiagCmd('P0,0', printResult = True)
            self.oSerial.gotoLevel('A')
            self.oSerial.sendDiagCmd('W,,,11', timeout = fullPackTimeout, printResult = True, stopOnError = True, DiagErrorsToIgnore = self.ignoreDiag, RWErrorsToIgnore = self.ignoreRWerror)
            # self.oSerial.gotoLevel('L')
            # self.oSerial.sendDiagCmd('E0', printResult = True)
            break
         except:
            objMsg.printMsg('Sequential write Failed, rerun!')
            objPwrCtrl.powerCycle(5000,12000,10,30)
            self.oSerial.enableDiags()
            time.sleep(5)
      else:
         ScrCmds.raiseException(12346, "Sequential write Failed")