#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Head MeasureMent Module
#  - Contains support for heater resistance maesurement states (GMR_RES_* etc.)
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
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Head_Measure_F3.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Head_Measure_F3.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
from State import CState
from Drive import objDut
import MessageHandler as objMsg
from PowerControl import objPwrCtrl
from serialScreen import sptDiagCmds
import sptCmds
import ScrCmds


#----------------------------------------------------------------------------------------------------------
DEBUG_WKWRT = 0
class CSymBer_WeakWrite(CState):
   """
      Description: Class that will screen cold/weak write head.
      
      =========================================================
      MERSING Branch format -> ber_log_start = 27 (YarraBP)
            Rbit Hard Soft  OTF  BER  Wbit  Whrd  Wrty
      Hd 0   7.2  7.2  7.2  7.2  3.57  6.9   6.9   6.9
      Hd 1   7.2  7.2  7.2  7.2  4.32  6.9   6.9   6.9
      =========================================================
      KINTA Branch format -> ber_log_start = 31
            Rbit  Hard  Soft  OTF   BER   Wbit  Whrd  Wrty
      Hd 0   5.4   5.4   5.4   5.4   1.62  7.0   7.0   7.0
      Hd 1   7.4   7.4   7.4   7.4   2.65  7.1   7.1   7.1
      =========================================================     
      LINGGI Branch format -> ber_log_start = 29
              Rbit  Hard Soft OTF  BER   Wbit  Whrd Wrty
      Hd 0    9.3   9.3  9.3  9.3  2.83  9.0   9.0  9.0
      Hd 1    0.0   0.0  0.0  0.0  0.00  0.0   0.0  0.0
      =========================================================      
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

      self.ber_log_start = 31
      if testSwitch.KARNAK:
         self.ber_log_start = 29
      self.ber_data_length = 4
      self.ber_log_end = self.ber_log_start + self.ber_data_length 
      self.weakwrite_ber_limit = 0.0 # 1.0
            
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if not testSwitch.RUN_WEAK_WR_DELTABER:
         return
         
      if testSwitch.PBIC_SUPPORT:
         from PBIC import ClassPBIC
         objPBIC = ClassPBIC()
         pbic_test_enabled = objPBIC.PBIC_Control_bd()
         if pbic_test_enabled == 0:
            objMsg.printMsg("PBIC: test bypassed !!")
            return           
         
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      # Set some default variables
      ColdDownDelay = 60*60*1
      QCmd_LoopCount = 500
      Left_Right_Padding_for_CleanUp = 3
      MediaCacheGuardTracks = 0x28

#======================= S T A R T ========================
#                Collect Testing Parameters
#==========================================================
      if hasattr(TP,'prm_F3_weakwrite_delta_BER'):
         FailSafe = TP.prm_F3_weakwrite_delta_BER['FailSafe']
         ColdDownDelay = TP.prm_F3_weakwrite_delta_BER['ColdDownDelay']
         DeltaBER_Limit = TP.prm_F3_weakwrite_delta_BER['DeltaBER_Limit']
         Minimum_SymBer = TP.prm_F3_weakwrite_delta_BER['Minimum_SymBer']
         Minimum_ColdSymBer = TP.prm_F3_weakwrite_delta_BER['Minimum_ColdSymBer']
         AvgPoints = TP.prm_F3_weakwrite_delta_BER['AvgPoints']
         QCmd_LoopCount = TP.prm_F3_weakwrite_delta_BER['LoopCount']
         FailSafe = TP.prm_F3_weakwrite_delta_BER['FailSafe']
      else:
         ColdDownDelay = self.params.get('param')['ColdDownDelay']
         DeltaBER_Limit = self.params.get('param')['DeltaBER_Limit']
         Minimum_SymBer = self.params.get('param')['Minimum_SymBer']
         Minimum_ColdSymBer = self.params.get('param')['Minimum_ColdSymBer']
         AvgPoints = self.params.get('param')['AvgPoints']
         QCmd_LoopCount = self.params.get('param')['LoopCount']
         FailSafe = self.params.get('param')['FailSafe']

      objMsg.printMsg("ColdDownDelay: %ds" % (ColdDownDelay))
      objMsg.printMsg("DeltaBER_Limit: %.3f" % (DeltaBER_Limit))
      objMsg.printMsg("Minimum_SymBer: %.3f" % (Minimum_SymBer))
      objMsg.printMsg("Minimum_ColdSymBer: %.3f" % (Minimum_ColdSymBer))
      objMsg.printMsg("AvgPoints: %d" % (AvgPoints))
      objMsg.printMsg("QCmd_LoopCount: %d" % (QCmd_LoopCount))
      objMsg.printMsg("FailSafe: %d" % (FailSafe))
      objMsg.printMsg("CleanUp PadSize: %d" % (Left_Right_Padding_for_CleanUp))

#======================= S T A R T ========================
#                  Misc. Initializations
#==========================================================
      oSerial = sptDiagCmds()
      oSerial.enableDiags()
      oSerial.syncBaudRate(Baud38400)

      sptCmds.gotoLevel('2')
      sptCmds.sendDiagCmd("x0", timeout = 500,printResult = True)

      # ** Get Zone Table for each head **
      numCyls,zones = oSerial.getZoneInfo()
      objMsg.printMsg("numCyls %s" %(numCyls))
      objMsg.printMsg("zones %s" %(zones))

      # For Track Qualification.
      MaxQual_Retries = 10          # Maximum no of Retries for Track Qualification
      QualRetry_TrkOffset = 100     # Track Offset to the next retry.
      self.Qualified_Tracks = []    # Array for Track Number @ OD, MD & ID for Weak Write Screening.

      self.TestTracks = {'H0': 0x2070, 'H1': 0x2070, 'H2': 0x2070, 'H3': 0x2070}

      if testSwitch.FE_0112188_345334_HEAD_RANGE_SUPPORT_10_HEADS:
         for head in range(self.dut.imaxHead):
            self.TestTracks['H%s'%head] = 0x2070

      if testSwitch.FE_0250198_348085_AUTO_DETECT_TEST_TRACK_WEAK_WR_DELTABER:
         for head in range(self.dut.imaxHead) :
            zoneInfo = oSerial.getSingleZoneInfo(self.dut.numZones, head, partition = 'User', printResult = True)
            self.TestTracks['H%s'%str(head)] = zoneInfo['LOG_START'] + MediaCacheGuardTracks  # the 0x28 is the MC guard tracks
            objMsg.printMsg("Head %d , TestTracks %xh" %(head, self.TestTracks['H%s'%str(head)]))

      self.Hot_SymBer = {'H0':0.0, 'H1':0.0, 'H2':0.0, 'H3':0.0}
      self.Cold_SymBer = {'H0':0.0, 'H1':0.0, 'H2':0.0, 'H3':0.0}
      self.Head_Status = {'H0':0, 'H1':0, 'H2':0, 'H3':0}
      self.SymBer = []
      self.AdjSymBer = []
      self.AllHds_SymBer = {'H0':[], 'H1':[], 'H2':[], 'H3':[]}
      self.AllHds_AdjSymBer = {'H0':[], 'H1':[], 'H2':[], 'H3':[]}

      if testSwitch.FE_0112188_345334_HEAD_RANGE_SUPPORT_10_HEADS:
         for head in range(self.dut.imaxHead):
            self.Hot_SymBer['H%s'%head] = 0.0
            self.Cold_SymBer['H%s'%head] = 0.0
            self.Head_Status['H%s'%head] = 0
            self.AllHds_SymBer['H%s'%head] = []
            self.AllHds_AdjSymBer['H%s'%head] = []

      if testSwitch.SKIPZONE:
         hdlist = [0,] * self.dut.imaxHead     # init to non skip hd

      if testSwitch.SKIPZONE and not testSwitch.virtualRun:
         try:
            objMsg.printMsg("Skip Zone: %s" % self.dut.skipzn)
            if self.dut.skipzn == []:
               raise
         except:
            try:
               from RdWr import CSkipZnFile
               self.dut.skipzn = CSkipZnFile().Retrieve_SKIPZN(dumpData = 0)
               objMsg.printMsg("SPT_DIAG_RESULTS Skip Zone: %s" % self.dut.skipzn)
               oSerial.enableDiags()
            except:
               ScrCmds.raiseException(11044,"Unable to extract SPT_DIAG_RESULTS")

         sptCmds.gotoLevel('2')
         zonePat = re.compile('\s*Rate\s*(?P<zone>[\dA-Fa-f]+)\s+(?P<minCyl>[\dA-Fa-f]+)-[\dA-Fa-f]+\s+(?P<minLogCyl>[\dA-Fa-f]+)-(?P<maxLogCyl>[\dA-Fa-f]+)')
         minLogCyl = {}
         maxLogCyl = {}
         for hd in range(self.dut.imaxHead):
            for zn in range(self.dut.numZones + 1):
               oSerial.flush()
               accumulator = oSerial.PBlock('x0,%x,%x\n\n' % (hd,zn))
               data = sptCmds.promptRead(100, accumulator = accumulator, loopSleepTime = 0)
               zoneMatch = zonePat.search(data)
               if zoneMatch and not(data.strip().startswith('F3')):
                  tempDict = zoneMatch.groupdict()
                  minLogCyl.setdefault(hd,{})[int(tempDict['zone'],16)] = int(tempDict['minLogCyl'],16)
                  maxLogCyl.setdefault(hd,{})[int(tempDict['zone'],16)] = int(tempDict['maxLogCyl'],16)
         objMsg.printMsg("minLogCyl of zone %s" %(minLogCyl))
         objMsg.printMsg("maxLogCyl of zone %s" %(maxLogCyl))

         if len(self.dut.skipzn) > 1:
            for head in range(self.dut.imaxHead):
               if (head, 1) in self.dut.skipzn:
                  objMsg.printMsg("Head %s zone 1 is skip zone, need to select new test track." %(head))
                  for zn in range(2, self.dut.numZones):
                     if (head, zn) in self.dut.skipzn:
                        objMsg.printMsg("Head %s zone %s is skip zone, need to select new test track." %(head, zn))
                        if zn == (self.dut.numZones -1):
                           if (head, 0) in self.dut.skipzn or testSwitch.ADAPTIVE_GUARD_BAND:
                              objMsg.printMsg("Head %s zone 0 is skip zone." %(head))
                              hdlist[head] = 1
                              objMsg.printMsg("Head %s skipped." %(head))
                           else:
                              NumTrk = maxLogCyl[head][0] - minLogCyl[head][0]
                              self.TestTracks['H' + str(head)] = minLogCyl[head][0] + abs(NumTrk * 0.95)
                              objMsg.printMsg("Head %s TestTracks change to zone 0 track %d" % (head, self.TestTracks['H' + str(head)]))
                     else:
                        NumTrk = maxLogCyl[head][zn] - minLogCyl[head][zn]
                        self.TestTracks['H' + str(head)] = minLogCyl[head][zn] + abs(NumTrk * 0.95)
                        objMsg.printMsg("Head %s TestTracks change to zone %s track %d" % (head, zn, self.TestTracks['H' + str(head)]))
                        break
         elif (len(self.dut.skipzn) == 1 and self.dut.skipzn == [(0, 0)]) or self.dut.skipzn ==[]:
            ScrCmds.raiseException(11044,"Wrong SPT_DIAG_RESULTS extracted")

         objMsg.printMsg("hdlist = %s" %(hdlist))   # 0- non skip hd, 1- skip hd

#======================= S T A R T ========================
#            Qualify Tracks for Writes & Reads
#==========================================================
      for hd in range(self.dut.imaxHead):
         if testSwitch.SKIPZONE and hdlist[hd] == 1:     # skip head
            continue

         Qual_Retry = 1
         QualTrk = self.TestTracks['H' + str(hd)]
         while True:
            objMsg.printMsg("Qualify Hd[%d] Trk[0x%X] Retry[%d]" % (hd, QualTrk, Qual_Retry))

            sptCmds.gotoLevel('2')
            sptCmds.sendDiagCmd("A0", timeout = 500)
            sptCmds.sendDiagCmd("S%X,%d" %(QualTrk, hd), timeout = 500, stopOnError = 0)
            objMsg.printMsg("Set Retry: Y,,,,141C4")
            sptCmds.sendDiagCmd("Y,,,,141C4", timeout = 500)
            self.ShowCurrentCHS()
            sptCmds.sendDiagCmd("P0", timeout = 500)
            Error = self.Write_CheckError(PrintResults = True)
            if Error == 0:
               Error = self.Read_CheckError(PrintResults = True)    # continue to Read if no Write Error.

            if Error and (Qual_Retry < MaxQual_Retries):
               QualTrk += QualRetry_TrkOffset
            else:
               break

            Qual_Retry = Qual_Retry + 1
         # --* while True - Loop
         self.TestTracks['H' + str(hd)] = QualTrk
      # --* for hd in range(self.dut.imaxHead) - Loop

#================================= S T A R T ===================================
#        Perform Exercise Writes before Power-Off (To simulate Serial_Format)
#===============================================================================
      self.SetSpace(self.TestTracks)
      #----------------------------------------------------------------
      # Set up Write/Read settings.
      #----------------------------------------------------------------
      if testSwitch.SKIPZONE:
         for hd in range(self.dut.imaxHead):
            if hdlist[hd] == 0:    # non skip head
               sptCmds.sendDiagCmd("S%X,%d" %(self.TestTracks['H' + str(hd)], hd), timeout = 500, stopOnError = 0)
               break
      else:
         sptCmds.sendDiagCmd("S%X,0" %(self.TestTracks['H0']), timeout = 500, stopOnError = 0)
      objMsg.printMsg("Set Retry: Y,,,,141C4")
      sptCmds.sendDiagCmd("Y,,,,141C4", timeout = 500)
      self.ShowCurrentCHS()

      objMsg.printMsg("Do 500x Write Before Power-Off")
      sptCmds.sendDiagCmd("P0", timeout = 500)                #Force 0 pattern
      sptCmds.sendDiagCmd("L1,500", timeout = 500, stopOnError = 0)
      sptCmds.sendDiagCmd("Q", timeout = 500, stopOnError = 0)
      self.ShowCurrentCHS()

#======================= S T A R T ==========================================
#      Cold-down - Wakeup - Q Cmd - Collect Symbol BER - for every head
#============================================================================
      for hd in range(self.dut.imaxHead):
         self.SymBer = []       # Initialize array to null, no need init to [] by hd
         self.AdjSymBer = []    # Initialize array to null, no need init to [] by hd
         sHd = 'H' + str(hd)
         TestTrack = self.TestTracks[sHd]
         objMsg.printMsg("Target CHS(Hex):%06X:%X:0000" % (TestTrack , hd))

      #========================= S T A R T ==========================
      #         POWER OFF to Cold-Down entire drive system
      #==============================================================
      objMsg.printMsg("=============================================")
      objMsg.printMsg(" >>> Power Off Drive for %d seconds <<<" % ColdDownDelay)
      objMsg.printMsg("=============================================")
      sptCmds.gotoLevel('2')
      sptCmds.sendDiagCmd("U", timeout = 500)
      sptCmds.sendDiagCmd("Z", timeout = 500)
      #objMsg.printMsg(" ==== SpinDown Drive for %d seconds ====" % ColdDownDelay)
      objPwrCtrl.powerOff()
      if DEBUG_WKWRT: ScriptPause(60)
      else: ScriptPause(ColdDownDelay)
      objMsg.printMsg("=================================================")
      objMsg.printMsg(" <<< Wake Up and Continue WeakWrite Screening >>>")
      objMsg.printMsg("=================================================")
      objPwrCtrl.powerOn()
      oSerial = sptDiagCmds()
      oSerial.enableDiags()
      oSerial.syncBaudRate(Baud38400)
      #------ Issuing a dummy cmd to load overlay because 2>U cmd needs overlay to b loaded 1st, otherwise FlashLED
      objMsg.printMsg(" Issuing 7>X cmd to load overlay")
      sptCmds.gotoLevel('7')
      sptCmds.sendDiagCmd("X", timeout = 500)

      sptCmds.gotoLevel('2')
      sptCmds.sendDiagCmd("U", timeout = 500)

      #----------------------------------------------------------------
      # Set up Write/Read settings.
      #self.QCmd_CollectSymBer(hd, TestTrack, self.SymBer, LoopCnt = QCmd_LoopCount)
      if testSwitch.SKIPZONE:
         self.QCmd_AllHds_SymBer(self.TestTracks, self.AllHds_SymBer, hdlist, LoopCnt = QCmd_LoopCount, debug = DEBUG_WKWRT)
      else:
         self.QCmd_AllHds_SymBer(self.TestTracks, self.AllHds_SymBer, LoopCnt = QCmd_LoopCount, debug = DEBUG_WKWRT)
      #=========================== S T A R T ============================
      #                        Data Processing
      #==================================================================
      for hd in range(self.dut.imaxHead):
         sHd = 'H' + str(hd)
         DataCount = len(self.AllHds_SymBer[sHd])
         Hot_Cnt = 0
         Cold_Cnt = 0
         self.Cold_SymBer[sHd] = 0.0
         self.Hot_SymBer[sHd] = 0.0
         for WrCnt in range(DataCount):
            fSum = 0.0
            fAvg = 0.0
            if WrCnt == 0:
               #---------------------------------------------------
               # -- Moving Average at the first Data Point --
               fSum = float(self.AllHds_SymBer[sHd][0]) + float(self.AllHds_SymBer[sHd][1]) + float(self.AllHds_SymBer[sHd][2])
               fAvg = fSum/3
            elif WrCnt == 1:
               #---------------------------------------------------
               # -- Moving Average at the second Data Point --
               fSum = float(self.AllHds_SymBer[sHd][0]) + float(self.AllHds_SymBer[sHd][1]) + float(self.AllHds_SymBer[sHd][2]) + float(self.AllHds_SymBer[sHd][3])
               fAvg = fSum/4
            elif WrCnt == (DataCount - 2):
               #---------------------------------------------------
               # -- Moving Average at the second last Data Point --
               fSum = float(self.AllHds_SymBer[sHd][DataCount-4]) + float(self.AllHds_SymBer[sHd][DataCount-3]) + float(self.AllHds_SymBer[sHd][DataCount-2]) + float(self.AllHds_SymBer[sHd][DataCount-1])
               fAvg = fSum/4
            elif WrCnt == (DataCount - 1):
               #---------------------------------------------------
               # -- Moving Average at the last Data Point --
               fSum = float(self.AllHds_SymBer[sHd][DataCount-3]) + float(self.AllHds_SymBer[sHd][DataCount-2]) + float(self.AllHds_SymBer[sHd][DataCount-1])
               fAvg = fSum/3
            else:
               #----------------------------------------------------
               # -- Moving Average for the rest of the Data Point --
               for DataPt in range(WrCnt-2, WrCnt+3):
                  fSum = fSum + float(self.AllHds_SymBer[sHd][DataPt])
                  fAvg = fSum/5

            self.AllHds_AdjSymBer[sHd].append(str('%.3f' % (fAvg)))
            if WrCnt < AvgPoints:
               Cold_Cnt = Cold_Cnt + 1
               #objMsg.printMsg("H%d Cold fAvg:%.3f" % (hd, fAvg))
               self.Cold_SymBer[sHd] = self.Cold_SymBer[sHd] + fAvg

            if WrCnt > (DataCount - AvgPoints - 1):
               Hot_Cnt = Hot_Cnt + 1
               #objMsg.printMsg("H%d Hot fAvg:%.3f" % (hd, fAvg))
               self.Hot_SymBer[sHd] = self.Hot_SymBer[sHd] + fAvg

         #=========================== S T A R T ============================
         #                    Display Final Head Data
         #==================================================================
         objMsg.printMsg("=================== Final Data For Head %d ====================" % (hd))
         for Data in range(len(self.AllHds_AdjSymBer[sHd])):
            objMsg.printMsg("H[%d] Data[%03d]:Org[%5s] %5s" % (hd, Data, self.AllHds_SymBer[sHd][Data], self.AllHds_AdjSymBer[sHd][Data]))

         #=========================== S T A R T ============================
         #            Calculate Average SymBer for HOT and COLD
         #            from the first and last 5 point respectively.
         #==================================================================
         #--------------------------------------------
         # -- Get the Average SymBer @ COLD --
         if Cold_Cnt != 0:            #when DataCount is none, Cold_Cnt = 0
            self.Cold_SymBer[sHd] = self.Cold_SymBer[sHd]/Cold_Cnt
         objMsg.printMsg("H[%d] Average Cold SymBer(First %3d Points): %.3f" % (hd, Cold_Cnt, self.Cold_SymBer[sHd]))
         #--------------------------------------------
         # -- Get the Average SymBer @ HOT --
         if Hot_Cnt != 0:             #when DataCount is none, Hot_Cnt = 0
            self.Hot_SymBer[sHd] = self.Hot_SymBer[sHd]/Hot_Cnt
         objMsg.printMsg("H[%d] Average Hot SymBer(Last %3d Points)  : %.3f" % (hd, Hot_Cnt, self.Hot_SymBer[sHd]))

      # --* for hd in range(self.dut.imaxHead) - Loop

#================================= S T A R T ===================================
#     Test Tracks Cleanup with '0" pattern (For LODT tests).
#===============================================================================
      objMsg.printMsg("Power Cycle to restore default retry")
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      oSerial = sptDiagCmds()
      oSerial.enableDiags()
      oSerial.syncBaudRate(Baud38400)

      #----------------------------------------------------------------
      # Set up error table.
      #----------------------------------------------------------------
      sptCmds.gotoLevel('L')
      sptCmds.sendDiagCmd("E1", timeout = 500, raiseException = 0)
      sptCmds.sendDiagCmd("iFFFC", timeout = 500, raiseException = 0)

      if testSwitch.FE_0254064_081592_CLEANUP_WKWRT_DELTABER_TRKS_USING_MC_INIT:
         objMsg.printMsg("For SMR product with MC zones at 1st 2 zn, use MCInit to clean up trk")
         oSerial.initMCCache()
      else:
         objMsg.printMsg("Re-Write Test Tracks with 0000 Pattern")
         self.SetSpace(self.TestTracks,Left_Right_Padding_for_CleanUp)
         #----------------------------------------------------------------
         # Set up Write/Read settings.
         #----------------------------------------------------------------
         if testSwitch.SKIPZONE:
            for hd in range(self.dut.imaxHead):
               if hdlist[hd] == 0:      # non skip head
                  sptCmds.sendDiagCmd("S%X,%d" %(self.TestTracks['H' + str(hd)], hd), timeout = 500, stopOnError = 0)
                  break
         else:
            sptCmds.sendDiagCmd("S%X,0" %(self.TestTracks['H0']), timeout = 500, stopOnError = 0)
         self.ShowCurrentCHS()
         sptCmds.sendDiagCmd("P0000,,C", timeout = 500)
         Q_LoopCnt = (Left_Right_Padding_for_CleanUp + 1)*(self.dut.imaxHead)*2
         sptCmds.sendDiagCmd("L1,%X" % Q_LoopCnt, printResult = DEBUG_WKWRT, timeout = 500, stopOnError = 0)
         sptCmds.sendDiagCmd("Q", timeout = 500, stopOnError = 0)
         self.ShowCurrentCHS()
         objMsg.printMsg("Re-Write Completed!\n")

      #----------------------------------------------------------------
      # Check error table for defects.
      #----------------------------------------------------------------
      sptCmds.gotoLevel('L')
      sptCmds.sendDiagCmd("E0", timeout = 500, raiseException = 0)
      result = sptCmds.sendDiagCmd("D", timeout = 500, raiseException = 0, printResult = True)
      offset = result.find('Log FFFC Entries ')
      if offset >= 0: defectCnt = int(result[offset+17:offset+19],16)
      else: defectCnt = 0
      if (defectCnt > 0) :
         result_lines = result.splitlines()
         offset2 = result_lines[3].find('RWERR')
         if offset2 >= 0:
            for i in range(defectCnt):
               if int(result_lines[5 + i][offset2:offset2+8], 16)!=0:
                  if testSwitch.SKIPZONE:
                     offsetCHS = result_lines[3].find('LLL CHS')
                     head = int(result_lines[5 + i][offsetCHS:offsetCHS+15].split('.')[1], 16)
                     objMsg.printMsg('LLL CHS head: %d' % (head))
                     if hdlist[head] == 1:    # do not fail defect skip head
                        objMsg.printMsg('Ignore defect entry: %d, as head %d is skip head' % (i+1, head))
                        continue
                  objMsg.printMsg("Re-Write FAIL !!!!!\n")
                  ScrCmds.raiseException(10566, "Found defects during write pass!!! Test Fail!")
               else:
                  objMsg.printMsg('Entry:%d, RWERR==0, so bypass it!' % (i+1))
         else:
            objMsg.printMsg("Re-Write FAIL !!!!!\n")
            ScrCmds.raiseException(10566, "Found defects during write pass!!! Test Fail!")
#===============================================================================
#     Test Tracks Cleanup with '0" pattern (For LODT tests).
#==========================  E  N  D  ==========================================

#=========================== S T A R T ============================
#                     Fail Criteria Checking
#==================================================================
      objMsg.printMsg("\n\nComparison of first and last %3d points (average). DeltaBER_Limit:%.3f, Minimum_SymBer:%.3f" % (AvgPoints, DeltaBER_Limit, Minimum_SymBer))
      objMsg.printMsg("===============================================")
      objMsg.printMsg("Head      HOT     COLD     DELTA    STATUS")

      FailColdSymBER = 0
      for hd in range(self.dut.imaxHead):
         if testSwitch.SKIPZONE and hdlist[hd] == 1:        # skip head
            continue

         sHd = 'H' + str(hd)
         HOT_COLD_Delta = 0.0
         COLD_Sym = float(self.Cold_SymBer[sHd])
         HOT_Sym = float(self.Hot_SymBer[sHd])
         iStatus = 0
         #--------------------------------------------
         # -- Calculate Delta between HOT and COLD --
         HOT_COLD_Delta = HOT_Sym - COLD_Sym
         #--------------------------------------------
         # -- Fail if exceeded threshold --
         if (HOT_COLD_Delta >= DeltaBER_Limit) and (COLD_Sym < Minimum_SymBer):
            iStatus = 14805 + hd
            self.Head_Status[sHd] = iStatus
         if (COLD_Sym < Minimum_ColdSymBer):
            FailColdSymBER = 1
            iStatus = 14805 + hd
            self.Head_Status[sHd] = iStatus

         objMsg.printMsg("%4d%9.3f%9.3f%10.3f%10d" % (hd, self.Hot_SymBer[sHd], self.Cold_SymBer[sHd], HOT_COLD_Delta, iStatus))
      objMsg.printMsg("===============================================")
      if FailColdSymBER:
         objMsg.printMsg("Fail minimum ColdSymBer spec.")

      # --* for hd in range(self.dut.imaxHead) - Loop

#=========================== S T A R T ============================
# Update Data to DBLog - Temp. Need to update with new DBLog table
#==================================================================
      #try:
      #   self.dut.dblData.delTable('P_AVERAGE_ERR_RATE', forceDeleteDblTable = 1)
      #except:
      #   pass
      ######################## DBLOG Implementaion- Setup
      curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
      ########################
      for hd in range(self.dut.imaxHead):
         if testSwitch.SKIPZONE and hdlist[hd] == 1:   # skip head
            continue

         sHd = 'H' + str(hd)
         TestTrack = self.TestTracks[sHd]
         HOT_COLD_Delta = 0.0
         COLD_Sym = float(self.Cold_SymBer[sHd])
         HOT_Sym = float(self.Hot_SymBer[sHd])
         iStatus = 0
         #--------------------------------------------
         # -- Calculate Delta between HOT and COLD --
         HOT_COLD_Delta = HOT_Sym - COLD_Sym
         #--------------------------------------------
         # -- Fail if exceeded threshold --
         if (HOT_COLD_Delta >= DeltaBER_Limit):
            iStatus += 0x01

         if (COLD_Sym < Minimum_SymBer):
            iStatus += 0x02

         objDut.dblData.Tables('P_AVERAGE_ERR_RATE').addRecord(
                        {
                        'HD_PHYS_PSN': hd,
                        'SPC_ID': 2,
                        'OCCURRENCE': occurrence,
                        'SEQ': curSeq,
                        'TEST_SEQ_EVENT': testSeqEvent,
                        'HD_LGC_PSN': hd,
                        'SUM_QBER': HOT_COLD_Delta,
                        'CNT_QBER': iStatus,
                        'AVG_QBER': COLD_Sym,
                        })

         objDut.dblData.Tables('P_TEMP_WEAK_WRITE_BER').addRecord(
                        {
                        'HD_PHYS_PSN': hd,
                        'TRK_NUM': TestTrack,
                        'SPC_ID': 1,
                        'OCCURRENCE': occurrence,
                        'SEQ': curSeq,
                        'TEST_SEQ_EVENT': testSeqEvent,
                        'HD_LGC_PSN': hd,
                        'COLD_BER10': COLD_Sym,
                        'HOT_BER10': HOT_Sym,
                        'DELTA_BER10': HOT_COLD_Delta,
                        'USL_DELTA_BER10': DeltaBER_Limit,
                        'LSL_COLD_BER10': Minimum_SymBer,
                        'HD_STATUS': iStatus,
                      })
      objMsg.printDblogBin(objDut.dblData.Tables('P_TEMP_WEAK_WRITE_BER'))
      # --* for hd in range(self.dut.imaxHead) - Loop

#=========================== S T A R T ============================
#                   Fail the Drive if Criteria not met.
#==================================================================
      if not FailSafe and not testSwitch.virtualRun:
         for hd in range(self.dut.imaxHead):
            if testSwitch.SKIPZONE and hdlist[hd] == 1:    # skip head
               continue

            sHd = 'H' + str(hd)
            if self.Head_Status[sHd]:
               ScrCmds.raiseException(self.Head_Status[sHd], "Weak Write Fail at Head %d" % (hd))

         # --* for hd in range(self.dut.imaxHead) - Loop


      #ScrCmds.raiseException(14805, "Just Fail the drive here.!")

#==================================================================
#                  Weak Write Screening - Completed
#==================================================================
      objMsg.printMsg("======== Delta BER Weak Write Screening - COMPLETED =========")
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

   #-------------------------------------------------------------------------------------------------------
   if testSwitch.SKIPZONE:
      def QCmd_AllHds_SymBer(self, TestTracks, AllHds_SymBer, hdlist, LoopCnt = 0x100, debug=0):
         oSerial = sptDiagCmds()
         self.SetSpace(TestTracks)

         sptCmds.gotoLevel('2')
         #----------------------------------------------------------------
         # Set up Write/Read settings.
         #----------------------------------------------------------------
         for hd in range(self.dut.imaxHead):
            if hdlist[hd] == 0:
               sptCmds.sendDiagCmd("S%X,%d" %(TestTracks['H' + str(hd)], hd), timeout = 500, printResult = debug, stopOnError = 0)
               break
         objMsg.printMsg("Set Retry: Y,,,,141C4")
         sptCmds.sendDiagCmd("Y,,,,141C4", timeout = 500, printResult = debug)
         self.ShowCurrentCHS()

         #----------------------------------------------------------------
         # Loop Through to Collect Symbol Error Rate.
         #----------------------------------------------------------------
         IdxCnt = 0
         for WR_Loop in range(LoopCnt):
            self.Enable_StatsLog()
            sptCmds.sendDiagCmd("L1,%d" % (self.dut.imaxHead), timeout = 500, printResult = debug, stopOnError = 0)
            sptCmds.sendDiagCmd("Q", timeout = 500, printResult = debug, stopOnError = 0)
            self.Get_SymBer_AllHds(AllHds_SymBer, MaxHead = self.dut.imaxHead)

         for hd in range(self.dut.imaxHead):
            sHd = 'H' + str(hd)
            objMsg.printMsg("H[%d] Total DataPoints: %d" % (hd, len(AllHds_SymBer[sHd])))
   else:
      def QCmd_AllHds_SymBer(self, TestTracks, AllHds_SymBer, LoopCnt = 0x100, debug=0):
         oSerial = sptDiagCmds()
         self.SetSpace(TestTracks)

         sptCmds.gotoLevel('2')
         #----------------------------------------------------------------
         # Set up Write/Read settings.
         #----------------------------------------------------------------
         sptCmds.sendDiagCmd("S%X,0" %(TestTracks['H0']), timeout = 500, printResult = debug, stopOnError = 0)
         objMsg.printMsg("Set Retry: Y,,,,141C4")
         sptCmds.sendDiagCmd("Y,,,,141C4", timeout = 500, printResult = debug)
         self.ShowCurrentCHS()

         #----------------------------------------------------------------
         # Loop Through to Collect Symbol Error Rate.
         #----------------------------------------------------------------
         IdxCnt = 0
         for WR_Loop in range(LoopCnt):
            self.Enable_StatsLog()
            sptCmds.sendDiagCmd("L1,%d" % (self.dut.imaxHead), timeout = 500, printResult = debug, stopOnError = 0)
            sptCmds.sendDiagCmd("Q", timeout = 500, printResult = debug, stopOnError = 0)
            self.Get_SymBer_AllHds(AllHds_SymBer, MaxHead = self.dut.imaxHead)

         for hd in range(self.dut.imaxHead):
            sHd = 'H' + str(hd)
            objMsg.printMsg("H[%d] Total DataPoints: %d" % (hd, len(AllHds_SymBer[sHd])))

   #-------------------------------------------------------------------------------------------------------
   def Get_SymBer_AllHds(self, AllHds_SymBer, MaxHead = 0):
      data = sptCmds.execOnlineCmd('`', timeout=20, waitLoops=100)

      if DEBUG_WKWRT: objMsg.printMsg("` return data = %s" % (data))   #Temp

      for hd in range(MaxHead):
         sHd = 'H' + str(hd)
         SearchString = 'Hd ' + str(hd)
         offset = data.find(SearchString)
         if offset >= 0:
            Sym_string = data[offset + self.ber_log_start : offset + self.ber_log_end]
            Symbol_BER = Sym_string.replace(" ", "")
            Symbol_BER = float(Symbol_BER)
            if Symbol_BER < 10.0 and Symbol_BER >= self.weakwrite_ber_limit:
               AllHds_SymBer[sHd].append(str('%.2f' % (Symbol_BER)))
               #ArrayLen = len(AllHds_SymBer[sHd])
               #objMsg.printMsg("H[%d] SymBER[%d]: %s" % (hd, ArrayLen, AllHds_SymBer[sHd][ArrayLen - 1]))

      sptCmds.sendDiagCmd(CR, timeout = 500)

   #-------------------------------------------------------------------------------------------------------
   def SetSpace(self, TestTracks, NumOfPaddingTracks = 0):
      oSerial = sptDiagCmds()

      sptCmds.gotoLevel('2')
      #----------------------------------------------------------------
      # Set Space for Write/Read on All Heads.
      #----------------------------------------------------------------
      for hd in range(self.dut.imaxHead):
         sHd = 'H' + str(hd)
         # Set Min Cylinder for current hd
         sptCmds.sendDiagCmd("A8,%X,,%d" % (TestTracks[sHd] - NumOfPaddingTracks, hd), printResult = DEBUG_WKWRT, timeout = 500)
         # Set Max Cylinder for current hd
         sptCmds.sendDiagCmd("A9,%X,,%d" % (TestTracks[sHd] + NumOfPaddingTracks, hd), printResult = DEBUG_WKWRT, timeout = 500)
      data = sptCmds.sendDiagCmd("A3", printResult = True, timeout = 500)

   #-------------------------------------------------------------------------------------------------------
   def QCmd_CollectSymBer(self, TgtHd, TgtTrk, SymBerHd, LoopCnt = 0x100):
      #----------------------------------------------------------------
      # Set up Write/Read settings.
      #----------------------------------------------------------------
      sptCmds.gotoLevel('2')
      sptCmds.sendDiagCmd("S%X,%d" %(TgtTrk, TgtHd), timeout = 500, stopOnError = 0)
      sptCmds.sendDiagCmd("A0", timeout = 500)
      sptCmds.sendDiagCmd("P0", timeout = 500)
      objMsg.printMsg("Set Retry: Y,,,,141C4")
      sptCmds.sendDiagCmd("Y,,,,141C4", timeout = 500)
      self.ShowCurrentCHS()

      #----------------------------------------------------------------
      # Loop Through to Collect Symbol Error Rate.
      #----------------------------------------------------------------
      IdxCnt = 0
      for WR_Loop in range(LoopCnt):
         self.Enable_StatsLog()
         sptCmds.sendDiagCmd("Q", timeout = 500, stopOnError = 0)
         SymbolBER = self.Get_Symbol_ErrorRate_From_Stats_Log(TgtHd)
         if SymbolBER >= self.weakwrite_ber_limit:
            SymBerHd.append(str('%.2f' % (SymbolBER)))
            #objMsg.printMsg("H[%d] Loop[%03d]:%s" % (TgtHd, WR_Loop, SymBerHd[IdxCnt]))
            IdxCnt = IdxCnt + 1
         else:
            #SymBerHd.append('0.00')
            objMsg.printMsg("H[%d] Loop[%03d]: --- Error" % (TgtHd, WR_Loop))

      objMsg.printMsg("H[%d] Total DataPoints: %d" % (TgtHd, IdxCnt))

   #-------------------------------------------------------------------------------------------------------
   def Get_Symbol_ErrorRate_From_Stats_Log(self, TgtHd):
      data = sptCmds.execOnlineCmd('`', timeout = 20, waitLoops = 100)
      SearchString = 'Hd ' + str(TgtHd)
      #objMsg.printMsg("%s" % (data))
      offset = data.find(SearchString)
      if offset >= 0:
         #objMsg.printMsg("Found Str: %s" % (SearchString))
         Symbol_ErrorRate = float(data[offset + self.ber_log_start : offset + self.ber_log_end])
         #objMsg.printMsg(" ==> Read Symbol ErrorRate: %-4f" % (Symbol_ErrorRate))

      if Symbol_ErrorRate <= self.weakwrite_ber_limit:
         objMsg.printMsg("%s" % (data))

      sptCmds.sendDiagCmd(CR, timeout = 500)
      return Symbol_ErrorRate

   #-------------------------------------------------------------------------------------------------------
   def Write_CheckError(self, PrintResults = False):
      #data = sptCmds.sendDiagCmd("W", printResult = PrintResults, timeout = 500, stopOnError = 0)
      data = sptCmds.sendDiagCmd("W", timeout = 500, stopOnError = 0)
      offset = data.find('R/W Error ')
      if offset >= 0:
         ErrorCode = data[offset+10:offset+18]
         objMsg.printMsg("Script Captured EC:%s" % (ErrorCode))
         #if ErrorCode == "C4090081":
         return 1
      else:
         return 0

   #-------------------------------------------------------------------------------------------------------
   def Read_CheckError(self, PrintResults = False):
      #data = oSerial.sendDiagCmd("R", printResult = PrintResults, timeout = 500, stopOnError = 0)
      data = sptCmds.sendDiagCmd("R", timeout = 500, stopOnError = 0)
      offset = data.find('R/W Error ')
      if offset >= 0:
         ErrorCode = data[offset+10:offset+18]
         objMsg.printMsg("Script Captured EC:%s" % (ErrorCode))
         #if ErrorCode == "C4090081":
         return 1
      else:
         return 0

   #-------------------------------------------------------------------------------------------------------
   def ShowCurrentCHS(self):
      data = sptCmds.execOnlineCmd(DOT, timeout = 20, waitLoops = 100)
      sptCmds.sendDiagCmd(CR, timeout = 500)
      objMsg.printMsg("%s" % (data))

   #-------------------------------------------------------------------------------------------------------
   def Enable_StatsLog (self):
      data = sptCmds.execOnlineCmd(CTRL_W, timeout = 20, waitLoops = 100)
      Stats_ON = data.find("Rd/Wr stats On")
      if Stats_ON < 0: # Rd/Wr stats NOT ready yet.
         #sptCmds.execOnlineCmd(CTRL_Z, timeout = 10, waitLoops = 100)
         sptCmds.execOnlineCmd(CTRL_W, timeout = 20, waitLoops = 100)
      sptCmds.sendDiagCmd(CR, timeout = 500)

