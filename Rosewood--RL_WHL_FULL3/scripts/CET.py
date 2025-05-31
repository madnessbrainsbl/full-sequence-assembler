#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Customer Emulation Tests
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/CET.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/CET.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from State import CState
import MessageHandler as objMsg
import ScrCmds
import re, struct, traceback, time, random
from TestParamExtractor import TP
from Test_Switches import testSwitch
from SATA_SetFeatures import *
from IntfClass import CIdentifyDevice
from PowerControl import objPwrCtrl
from Utility import CUtility
from ICmdFactory import ICmd
from IntfClass import HardReset   
from Rim import objRimType

from CPCRim import BaseCPCInit
from Process import CProcess

DEBUG = 0
###########################################################################################################
class CAppleWRCTest(CState):
   """
      Description: Apple Write/Read Compare test based on Design Reliability FlexStar Algorithm.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      ScrCmds.insertHeader("Apple WRC Test",headChar='#')
      Tests = [1,246,3,5,7,8,9]
      for i in Tests:
        starttest = time.time()
        func = 'self.WRCTest' + str(i) + '()'
        eval(func)
        endtest = time.time()
        totaltime = endtest - starttest
        objMsg.printMsg("Test Time - Test:%s: %fsec" %(str(i),totaltime))
   #-------------------------------------------------------------------------------------------------------
   def FlushCache(self,testno,start,stop):
      result = ICmd.FlushCache()
      if result['LLRET'] != OK:
         ScrCmds.raiseException(14919, "Apple WRC Test-%d - Failed FlushCache" %testno)
      FlushCache_CmdRange = random.randrange(start,stop)
      FlushCacheCounter = 0
      return FlushCacheCounter,FlushCache_CmdRange
   #-------------------------------------------------------------------------------------------------------
   def ClearBinBuffer(self,testno):
      ICmd.HardReset()
      result = ICmd.ClearBinBuff(BWR)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(14919, "Apple WRC Test-%d - Failed to fill buffer for zero write/read" %testno)
   #-------------------------------------------------------------------------------------------------------
   def SetUDMASpeed(self,testno):
      result = Set_UDMASpeed(0x45, exc = 0)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(14919, "Apple WRC Test-%d - SetFeatures Failure" %testno)
   #-------------------------------------------------------------------------------------------------------

   def WRCTest1(self):
      ScrCmds.insertHeader("WRC Test-1",headChar='*')
      objMsg.printMsg("Performing WRITE operation.")
      self.ClearBinBuffer(1)
      self.SetUDMASpeed(1)

      TestStartLBA = WriteStartLBA = 27343750 #0x01A13B86 - 14GB
      TestEndLBA = 40039302 #0x0262F386 - ~20.5GB
      WriteSkipBlocks = [0x800,0x1000,0x1800] #2048,4096,6144 Blocks
      stepLBA = SectorCnt = 256
      Incrementor = IncrementLBA = EndLBA = 0
      DataCompareSwitch = ['ON','ON','OFF','ON','OFF','OFF']

      while EndLBA < TestEndLBA:
         EndLBA = WriteStartLBA + SectorCnt
         if EndLBA >= TestEndLBA: break
         result = ICmd.SequentialWriteDMAExt(WriteStartLBA, EndLBA, stepLBA, SectorCnt)
         IncrementLBA = WriteSkipBlocks[Incrementor]
         WriteStartLBA = WriteStartLBA + IncrementLBA
         Incrementor = Incrementor + 1
         if Incrementor == 3: Incrementor = 0
         if result['LLRET'] != 0:
            objMsg.printMsg ('SequentialWriteDMAExt:%s' %result)
            ScrCmds.raiseException(14919, "Apple WRC Test-1 Write Failure - StartLBA:%s EndLBA:%s IncrementLBA:%s" %(WriteStartLBA,EndLBA,IncrementLBA))

      objMsg.printMsg("Performing READ operation.")
      Incrementor = 0
      for lba in range(TestStartLBA,TestEndLBA,WriteSkipBlocks[0]):
         if DataCompareSwitch[Incrementor] == 'ON': CompareFlag = 1
         if DataCompareSwitch[Incrementor] == 'OFF': CompareFlag = 0
         result = ICmd.SequentialReadDMAExt(lba,lba+256,stepLBA,SectorCnt,0,CompareFlag)
         if result['LLRET'] != 0:
            objMsg.printMsg ('SequentialReadDMAExt:%s' %result)
            ScrCmds.raiseException(14919, "Apple WRC Test-1 Read Failure - StartLBA:%s EndLBA:%s" %(lba,lba+256))
         Incrementor = Incrementor + 1
         if Incrementor == 6: Incrementor = 0

   #-------------------------------------------------------------------------------------------------------
   def WRCTest246(self):
      ScrCmds.insertHeader("WRC Test-246",headChar='*')

      Zone1_StartLBA = 27343750 #0x01A13B86 - 14GB
      Zone1_EndLBA = 31738281 #0x01E449A9 - 16.25GB
      Zone2_StartLBA = 34667968 #0x0210FDC0 - 17.75GB
      Zone2_EndLBA = 39062500 #0x02540BE4 - 20GB
      ExtOD1_StartLBA = 0
      ExtOD1_EndLBA = 4882812 #0x004A817C - 2.5GB
      ExtOD2_StartLBA = 9765624 #0x009502F8 - 5GB
      ExtOD2_EndLBA = 14648436 #0x00DF8474 - 7.5GB

      self.SetUDMASpeed(246)
      ##########################################################################
      #Test4_6:
      #Repeat step 1 to 4 for 10 times with transfer length = 8 for WRC test 4 and 6.
      ##########################################################################
      def Test4_6():
          for i in range(10):
              objMsg.printMsg('*'*20 + "LOOP:%s - Performing TEST4_6 with transfer length = 8 Blocks" %str(i+1))
              step1(SectorCount=8)
              step2(SectorCount=8)
              step3(SectorCount=8)
              step4(SectorCount=8)
      ##########################################################################

      ##########################################################################
      #Test2_6:
      #Repeat step 1 to 4 for 10 times with transfer length = 256 for WRC test 2 and 6.
      ##########################################################################
      def Test2_6():
          for i in range(10):
              objMsg.printMsg('*'*20 + "LOOP:%s - Performing TEST2_6 with transfer length = 256 Blocks" %str(i+1))
              step1(SectorCount=256)
              step2(SectorCount=256)
              step3(SectorCount=256)
              step4(SectorCount=256)
      ##########################################################################

      ##########################################################################
      #STEP:1 -> Random Write 256 times at Zone-1 and Zone-2
      ##########################################################################
      def step1(SectorCount):
          objMsg.printMsg('STEP:1 -> Random Write 256 times at Zone-1 and Zone-2')
          self.ClearBinBuffer(246)

          SectorCnt = StepLBA = SectorCount
          self.Zone1_StartLBABuffer = []
          self.Zone2_StartLBABuffer = []
          for value in xrange(256):
             step1_StartLBA1 = random.randrange(Zone1_StartLBA,Zone1_EndLBA)
             self.Zone1_StartLBABuffer.append(step1_StartLBA1)
             step1_EndLBA1 = step1_StartLBA1 + SectorCnt
             result = ICmd.SequentialWriteDMAExt(step1_StartLBA1,step1_EndLBA1,StepLBA,SectorCnt,0,0)
             if result['LLRET'] != 0:
                objMsg.printMsg ('Zone1: SequentialWriteDMAExt: %s' % result)
                ScrCmds.raiseException(14919, "Apple WRC Test-246 Zone-1 Write Failure - StartLBA:%s EndLBA:%s" %(step1_StartLBA1,step1_EndLBA1))

             step1_StartLBA2 = random.randrange(Zone2_StartLBA,Zone2_EndLBA)
             self.Zone2_StartLBABuffer.append(step1_StartLBA2)
             step1_EndLBA2 = step1_StartLBA2 + SectorCnt
             result = ICmd.SequentialWriteDMAExt(step1_StartLBA2,step1_EndLBA2,StepLBA,SectorCnt,0,0)
             if result['LLRET'] != 0:
                objMsg.printMsg ('Zone2: SequentialWriteDMAExt: %s' % result)
                ScrCmds.raiseException(14919, "Apple WRC Test-246 Zone-2 Write Failure - StartLBA:%s EndLBA:%s" %(step1_StartLBA2,step1_EndLBA2))
      ##########################################################################

      ##########################################################################
      #STEP:2 -> Flush Cache and Write or Read at extreme OD
      ##########################################################################
      def step2(SectorCount):
          objMsg.printMsg('STEP:2 -> Flush Cache and Write or Read at extreme OD')
          self.ClearBinBuffer(246)
          result = ICmd.FlushCache()
          if result['LLRET'] != OK:
             ScrCmds.raiseException(14919, "Apple WRC Test-246 - Failed FlushCache")

          objMsg.printMsg ('FlushCache: %s' % result)
          step2_StartLBA1 = [random.randrange(ExtOD1_StartLBA,ExtOD1_EndLBA),random.randrange(ExtOD2_StartLBA,ExtOD2_EndLBA)]
          step2_StartLBA1 = random.sample(step2_StartLBA1,1)[0]
          step2_EndLBA1 = step2_StartLBA1 + SectorCount
          objMsg.printMsg('Extreme OD Write: StartLBA: %s EndLBA: %s' %(step2_StartLBA1,step2_EndLBA1))
          result = ICmd.SequentialWriteDMAExt(step2_StartLBA1,step2_EndLBA1,SectorCount,SectorCount,0,0)
          if result['LLRET'] != 0:
               objMsg.printMsg ('SequentialWriteDMAExt: %s' % result)
               ScrCmds.raiseException(14919, "Apple WRC Test-246 Extreme OD Write Failure - StartLBA:%s EndLBA:%s" %(step2_StartLBA1,step2_EndLBA1))
      ##########################################################################

      ##########################################################################
      #STEP:3 -> - Perform Read with Data Compare ON based on STEP:1 Zone-1 and Zone-2 write locations.
      #          - Perform Random Read for Zone-1 and Zone-2 with Data Compare Off.
      ##########################################################################
      def step3(SectorCount):
          objMsg.printMsg('STEP:3 -> Read with Data Compare ON based on STEP:1 Zone-1 and Zone-2 write locations')
          objMsg.printMsg('STEP:3 -> Random Read for Zone-1 and Zone-2 with Data Compare Off')
          self.ClearBinBuffer(246)

          for cnt in xrange(256):
            Step3_StartLBA1 = self.Zone1_StartLBABuffer[cnt]
            Step3_EndLBA1 = Step3_StartLBA1 + SectorCount
            result = ICmd.ZeroCheck(Step3_StartLBA1, Step3_EndLBA1, SectorCount)
            if result['LLRET'] != OK:
               objMsg.printMsg ('Zone1: ZeroCheck: %s' % result)
               ScrCmds.raiseException(14919, "Apple WRC Test-246 - Zone-1 Read Compare Failure - StartLBA:%s EndLBA:%s" %(Step3_StartLBA1,Step3_EndLBA1))

            result = ICmd.RandomReadDMAExt(Zone1_StartLBA,Zone1_EndLBA,SectorCount,SectorCount,1,0,0)
            if result['LLRET'] != 0:
               objMsg.printMsg ('Zone1: RandomReadDMAExt: %s' % result)
               ScrCmds.raiseException(14919, "Apple WRC Test-246 - Zone-1 Read without Compare Failure - StartLBA:%s EndLBA:%s" %(Step3_StartLBA1,Step3_EndLBA1))

            Step3_StartLBA2 = self.Zone2_StartLBABuffer[cnt]
            Step3_EndLBA2 = Step3_StartLBA2 + SectorCount
            result = ICmd.ZeroCheck(Step3_StartLBA2,Step3_EndLBA2, SectorCount)
            if result['LLRET'] != OK:
               objMsg.printMsg ('Zone2: ZeroCheck: %s' % result)
               ScrCmds.raiseException(14919, "Apple WRC Test-246 - Zone-2 Read Compare Failure - StartLBA:%s EndLBA:%s" %(Step3_StartLBA2,Step3_EndLBA2))

            result = ICmd.RandomReadDMAExt(Zone2_StartLBA,Zone2_EndLBA,SectorCount,SectorCount,1,0,0)
            if result['LLRET'] != 0:
               objMsg.printMsg ('Zone2: RandomReadDMAExt: %s' % result)
               ScrCmds.raiseException(14919, "Apple WRC Test-246 - Zone-2 Read without Compare Failure - StartLBA:%s EndLBA:%s" %(Step3_StartLBA2,Step3_EndLBA2))
      ##########################################################################

      ##########################################################################
      #STEP:4 -> - Random Write/Read with Data Compare On at random locations in Zone 1 and Zone 2 for 20sec.
      #          - Also random Write or Read at extreme OD for a few times.
      ##########################################################################
      def step4(SectorCount):
          objMsg.printMsg('STEP:4 -> Random Write/Read with Data Compare ON for Zone-1 and Zone-2 for 20sec each')
          self.ClearBinBuffer(246)

          SectorCnt = StepLBA = SectorCount
          testtime = 20 #20sec
          starttime = time.time()
          endtime = starttime + testtime
          if testSwitch.virtualRun: endtime = starttime
          while time.time() < endtime:
             step4_StartLBA1 = random.randrange(Zone1_StartLBA,Zone1_EndLBA)
             step4_EndLBA1 = step4_StartLBA1 + SectorCnt
             result = ICmd.SequentialWRDMAExt(step4_StartLBA1,step4_EndLBA1,StepLBA,SectorCnt,0,1)
             if result['LLRET'] != 0:
                objMsg.printMsg ('Zone1: SequentialWRDMAExt: %s' % result)
                ScrCmds.raiseException(14919, "Apple WRC Test-246 - Step4 - Zone-1 Write/Read Compare Failure - StartLBA:%s EndLBA:%s" %(step4_StartLBA1,step4_EndLBA1))

          starttime = time.time()
          endtime = starttime + testtime
          if testSwitch.virtualRun: endtime = starttime
          while time.time() < endtime:
             step4_StartLBA2 = random.randrange(Zone2_StartLBA,Zone2_EndLBA)
             step4_EndLBA2 = step4_StartLBA2 + SectorCnt
             result = ICmd.SequentialWRDMAExt(step4_StartLBA2,step4_EndLBA2,StepLBA,SectorCnt,0,1)
             if result['LLRET'] != 0:
                objMsg.printMsg ('Zone2: SequentialWRDMAExt: %s' % result)
                ScrCmds.raiseException(14919, "Apple WRC Test-246 - Step4 - Zone-2 Write/Read Compare Failure - StartLBA:%s EndLBA:%s" %(step4_StartLBA2,step4_EndLBA2))

          objMsg.printMsg('STEP:4 -> Random Read at Extreme OD for 20sec')
          starttime = time.time()
          endtime = starttime + testtime
          if testSwitch.virtualRun: endtime = starttime
          while time.time() < endtime:
             step4_StartLBA3 = [random.randrange(ExtOD1_StartLBA,ExtOD1_EndLBA),random.randrange(ExtOD2_StartLBA,ExtOD2_EndLBA)]
             step4_StartLBA3 = random.sample(step4_StartLBA3,1)[0]
             step4_EndLBA3 = step4_StartLBA3 + SectorCnt
             result = ICmd.SequentialReadDMAExt(step4_StartLBA3,step4_EndLBA3,StepLBA,SectorCnt,0,0)
             if result['LLRET'] != 0:
                objMsg.printMsg ('OD1: SequentialReadDMAExt: %s' % result)
                ScrCmds.raiseException(14919, "Apple WRC Test-246 - Step4 - Extreme OD Read Failure - StartLBA:%s EndLBA:%s" %(step4_StartLBA3,step4_EndLBA3))
      ##########################################################################

      ##########################################################################
      #STEP:5 -> Sequential Read from 0 to 2.5GB for WRC test 6.
      ##########################################################################
      def step5():
          objMsg.printMsg('STEP:5 -> Sequential Read from 0 to 2.5GB.')
          self.ClearBinBuffer(246)

          result = ICmd.SequentialReadDMAExt(ExtOD1_StartLBA,ExtOD1_EndLBA,256,256,0,0)
          objMsg.printMsg ('Zone OD1: SequentialReadDMAExt: %s' % result)
          if result['LLRET'] != 0:
               ScrCmds.raiseException(14919, "Apple WRC Test-246 - OD1 Read Failure")
      ##########################################################################

      ##########################################################################
      #MAIN WRC TEST246 CALL
      ##########################################################################
      Test4_6()
      Test2_6()
      objMsg.printMsg('*'*20 + "Performing TEST-246 - STEP:5")
      step5()
      ##########################################################################

   #-------------------------------------------------------------------------------------------------------
   def WRCTest5(self):
      ScrCmds.insertHeader("WRC Test-5",headChar='*')

      Zone_StartLBA = 27343616 #0x01A13B00 - 14GB
      Zone_EndLBA = 41015808 #0x0271DA00 - 21GB
      StepLBA = SectorCount = 256
      self.SetUDMASpeed(5)

      ##########################################################################
      #STEP:1 -> - Write skip forward: Random skipping between 2k, 4k, 6k, 8k, 10k, 12k, 14k and 16k blocks.
      #          - Randomly issue Flush Cache after 128 ~ 512 commands. Random delay at every 256~512 commands.
      ##########################################################################
      def step1():
          objMsg.printMsg('STEP:1 -> Write skip forward: StartLBA:%s EndLBA:%s' %(Zone_StartLBA,Zone_EndLBA))
          objMsg.printMsg('STEP:1 -> Random skip:[2k,4k,6k,8k,10k,12k,14k,16k], FlushCache_CmdRange:[128,512], Delay_CmdRange:[256,512]')
          self.ClearBinBuffer(5)

          Write_SkipFwd_Blocks = [0x800,0x1000,0x1800,0x2000,0x2800,0x3000,0x3800,0x4000] #2K,4K,6K,8K,10K,12K,14K,16K Blocks
          FlushCache_CmdRange = random.randrange(128,513)
          Delay_CmdRange = random.randrange(256,513)
          StartLBA_Calc = Zone_StartLBA
          EndLBA_Calc = FlushCacheCounter = TimeDelayCounter = 0

          while EndLBA_Calc < Zone_EndLBA:
              skipLBA = random.sample(Write_SkipFwd_Blocks,1)[0]
              StartLBA_Calc = StartLBA_Calc + skipLBA
              EndLBA_Calc = StartLBA_Calc + SectorCount
              if EndLBA_Calc >= Zone_EndLBA: break
              result = ICmd.SequentialWriteDMAExt(StartLBA_Calc,EndLBA_Calc,StepLBA,SectorCount,0,0)
              if result['LLRET'] != 0:
                 objMsg.printMsg ('SequentialWriteDMAExt: %s' % result)
                 ScrCmds.raiseException(14919, "Apple WRC Test-5 Write Failure - StartLBA:%s EndLBA:%s skipLBA:%s" %(StartLBA_Calc,EndLBA_Calc,skipLBA))
              else:
                  FlushCacheCounter = FlushCacheCounter + 1
                  TimeDelayCounter = TimeDelayCounter + 1

              if FlushCacheCounter >= FlushCache_CmdRange:
                 FlushCacheCounter,FlushCache_CmdRange = self.FlushCache(5,128,513)

              if TimeDelayCounter >= Delay_CmdRange:
                 sleeptime = random.randrange(2,12) #2-12sec
                 time.sleep(sleeptime)
                 Delay_CmdRange = random.randrange(256,513)
                 TimeDelayCounter = 0
      ##########################################################################

      ##########################################################################
      #STEP:2 -> - Write skip forward: Random skipping between 2k, 4k and 6k blocks.
      #          - Randomly issue Flush Cache after 128 ~ 512 commands.
      ##########################################################################
      def step2():
          objMsg.printMsg('STEP:2 -> Write skip forward: StartLBA:%s EndLBA:%s' %(Zone_StartLBA,Zone_EndLBA))
          objMsg.printMsg('STEP:2 -> Random skip:[2k,4k,6k], FlushCache_CmdRange:[128,512]')
          self.ClearBinBuffer(5)

          Write_SkipFwd_Blocks = [0x800,0x1000,0x1800] #2K,4K,6K Blocks
          FlushCache_CmdRange = random.randrange(128,513)
          StartLBA_Calc = Zone_StartLBA
          EndLBA_Calc = FlushCacheCounter = 0

          while EndLBA_Calc < Zone_EndLBA:
              skipLBA = random.sample(Write_SkipFwd_Blocks,1)[0]
              StartLBA_Calc = StartLBA_Calc + skipLBA
              EndLBA_Calc = StartLBA_Calc + SectorCount
              if EndLBA_Calc >= Zone_EndLBA: break
              result = ICmd.SequentialWriteDMAExt(StartLBA_Calc,EndLBA_Calc,StepLBA,SectorCount,0,0)
              if result['LLRET'] != 0:
                 objMsg.printMsg ('SequentialWriteDMAExt: %s' % result)
                 ScrCmds.raiseException(14919, "Apple WRC Test-5 Write Failure - StartLBA:%s EndLBA:%s skipLBA:%s" %(StartLBA_Calc,EndLBA_Calc,skipLBA))
              else:
                 FlushCacheCounter = FlushCacheCounter + 1

              if FlushCacheCounter >= FlushCache_CmdRange:
                 FlushCacheCounter,FlushCache_CmdRange = self.FlushCache(5,128,513)
      ##########################################################################

      ##########################################################################
      #STEP:3 -> - Write Read Compare:
      #  -  Write the 1st 192k blocks: Random skipping between 2k, 4k and 6k blocks.
      #     Save the LBA locations in the buffer.
      #  -  With 192k blocks offset, Write on the new locations and save the location
      #     in the buffer while retrieve the previous locations from the buffer and read with Data Compare ON.
      #  -  Read the last 192k blocks with Data Compare On.
      #  -  Randomly issue Flush Cache after 128 ~ 512 commands. Random delay at every 256~512 commands.

      ##########################################################################
      def step3():
          objMsg.printMsg('STEP:3 -> Write skip forward-192K blocks: StartLBA:%s EndLBA:%s' %(Zone_StartLBA,Zone_EndLBA))
          objMsg.printMsg('STEP:3 -> Random skip:[2k,4k,6k], FlushCache_CmdRange:[128,512], Delay_CmdRange:[256,512]')
          objMsg.printMsg('STEP:3 -> Read Compare Written LBA locations')
          self.ClearBinBuffer(5)

          Write_SkipFwd_Blocks = [0x800,0x1000,0x1800] #2K,4K,6K Blocks
          Blocks_192K = 0x30000 #192K
          FlushCache_CmdRange = random.randrange(128,513)
          Delay_CmdRange = random.randrange(256,513)
          StartLBA_Calc = Zone_StartLBA
          EndLBA_192K = Zone_StartLBA
          EndLBA_Calc = FlushCacheCounter = TimeDelayCounter = 0

          while EndLBA_192K < Zone_EndLBA:
             Write_location = []
             StartLBA_Calc = EndLBA_192K
             EndLBA_192K = EndLBA_192K + Blocks_192K
             if EndLBA_192K >= Zone_EndLBA: break
             while EndLBA_Calc < EndLBA_192K:
                skipLBA = random.sample(Write_SkipFwd_Blocks,1)[0]
                StartLBA_Calc = StartLBA_Calc + skipLBA
                EndLBA_Calc = StartLBA_Calc + SectorCount
                if EndLBA_Calc >= EndLBA_192K: break
                result = ICmd.SequentialWriteDMAExt(StartLBA_Calc,EndLBA_Calc,StepLBA,SectorCount,0,0)
                if result['LLRET'] != 0:
                   objMsg.printMsg ('SequentialWriteDMAExt: %s' % result)
                   ScrCmds.raiseException(14919, "Apple WRC Test-5 Write Failure - StartLBA:%s EndLBA:%s skipLBA:%s" %(StartLBA_Calc,EndLBA_Calc,skipLBA))
                else:
                   FlushCacheCounter = FlushCacheCounter + 1
                   TimeDelayCounter = TimeDelayCounter + 1
                   Write_location.append(StartLBA_Calc)

                if FlushCacheCounter >= FlushCache_CmdRange:
                   FlushCacheCounter,FlushCache_CmdRange = self.FlushCache(5,128,513)

                if TimeDelayCounter >= Delay_CmdRange:
                   sleeptime = random.randrange(2,12)#2-12sec
                   time.sleep(sleeptime)
                   Delay_CmdRange = random.randrange(256,513)
                   TimeDelayCounter = 0

             for value in Write_location:
                Step3_StartLBA1 = value
                Step3_EndLBA1 = Step3_StartLBA1 + SectorCount
                result = ICmd.ZeroCheck(Step3_StartLBA1, Step3_EndLBA1, SectorCount)
                if result['LLRET'] != OK:
                   objMsg.printMsg ('ZeroCheck: %s' % result)
                   ScrCmds.raiseException(14919, "Apple WRC Test-5 Read Failure - StartLBA:%s EndLBA:%s" %(Step3_StartLBA1,Step3_EndLBA1))
                else:
                   FlushCacheCounter = FlushCacheCounter + 1
                   TimeDelayCounter = TimeDelayCounter + 1

                if FlushCacheCounter >= FlushCache_CmdRange:
                   FlushCacheCounter,FlushCache_CmdRange = self.FlushCache(5,128,513)

                if TimeDelayCounter >= Delay_CmdRange:
                   sleeptime = random.randrange(2,12)#2-12sec
                   time.sleep(sleeptime)
                   Delay_CmdRange = random.randrange(256,513)
                   TimeDelayCounter = 0
      ##########################################################################

      ##########################################################################
      #MAIN WRC TEST5 CALL
      ##########################################################################
      objMsg.printMsg('*'*20 + "Performing Test-5 : STEP-1")
      step1()
      objMsg.printMsg('*'*20 + "Performing Test-5 : STEP-2")
      step2()
      objMsg.printMsg('*'*20 + "Performing Test-5 : STEP-3")
      step3()
      ##########################################################################

   #-------------------------------------------------------------------------------------------------------
   def WRCTest7(self):
      ScrCmds.insertHeader("WRC Test-7",headChar='*')

      Zone_StartLBA = 27343616 #0x01A13B00 - 14GB
      Zone_EndLBA = 32226560 #0x01EBBD00 - 16.5GB
      StepLBA = SectorCount = 256
      self.SetUDMASpeed(7)

      ##########################################################################
      #STEP:1 -> - Write skip forward: Random skipping between 2k, 4k, 6k, 8k, 10k and 12k blocks.
      #          - Randomly issue Flush Cache after 256 ~ 512 commands.
      #          - Randomly issue delay after 256 ~ 512 commands.
      #          - Save the alternate written locations into Buffer 0.
      ##########################################################################
      def step1():
          objMsg.printMsg('STEP:1 -> Write skip forward: StartLBA:%s EndLBA:%s' %(Zone_StartLBA,Zone_EndLBA))
          objMsg.printMsg('STEP:1 -> Random skip:[2k,4k,6k,8k,10k,12k], FlushCache_CmdRange:[256,512], Delay_CmdRange:[256,512]')
          self.ClearBinBuffer(7)

          Write_SkipFwd_Blocks = [0x800,0x1000,0x1800,0x2000,0x2800,0x3000] #2K,4K,6K,8K,10K,12K Blocks
          FlushCache_CmdRange = random.randrange(256,513)
          Delay_CmdRange = random.randrange(256,513)
          StartLBA_Calc = Zone_StartLBA
          EndLBA_Calc = FlushCacheCounter = TimeDelayCounter = CommandCount = 0
          self.Write_Altlocation = []

          while EndLBA_Calc < Zone_EndLBA:
              skipLBA = random.sample(Write_SkipFwd_Blocks,1)[0]
              StartLBA_Calc = StartLBA_Calc + skipLBA
              EndLBA_Calc = StartLBA_Calc + SectorCount
              if EndLBA_Calc >= Zone_EndLBA: break
              result = ICmd.SequentialWriteDMAExt(StartLBA_Calc,EndLBA_Calc,StepLBA,SectorCount,0,0)
              if result['LLRET'] != 0:
                 objMsg.printMsg ('SequentialWriteDMAExt: %s' % result)
                 ScrCmds.raiseException(14919, "Apple WRC Test-7 Write Failure - StartLBA:%s EndLBA:%s skipLBA:%s" %(StartLBA_Calc,EndLBA_Calc,skipLBA))
              else:
                 FlushCacheCounter = FlushCacheCounter + 1
                 TimeDelayCounter = TimeDelayCounter + 1
                 CommandCount = CommandCount + 1
                 if (CommandCount % 2.0) == 0:
                    self.Write_Altlocation.append(StartLBA_Calc)

              if FlushCacheCounter >= FlushCache_CmdRange:
                 FlushCacheCounter,FlushCache_CmdRange = self.FlushCache(7,256,513)

              if TimeDelayCounter >= Delay_CmdRange:
                 sleeptime = random.randrange(2,12) #2-12sec
                 time.sleep(sleeptime)
                 Delay_CmdRange = random.randrange(256,513)
                 TimeDelayCounter = 0
      ##########################################################################

      ##########################################################################
      #STEP:2 -> - Read skip forward: Retrieve from the buffer 0 and read with Data Compare On.
      #          - Random skipping between 2k, 4k, 6k, 8k, 10k and 12k blocks and read with Data Compare Off.
      #          - Repeat until last buffer index.
      ##########################################################################
      def step2():
          objMsg.printMsg('STEP:2 -> Read with Data Compare based on STEP:1 write locations')
          objMsg.printMsg('STEP:2 -> Random Read without Data Compare')
          self.ClearBinBuffer(7)

          Read_SkipFwd_Blocks = [0x800,0x1000,0x1800,0x2000,0x2800,0x3000] #2K,4K,6K,8K,10K,12K Blocks
          for value in self.Write_Altlocation:
            Step2_StartLBA1 = value
            Step2_EndLBA1 = Step2_StartLBA1 + SectorCount
            result = ICmd.SequentialReadDMAExt(Step2_StartLBA1,Step2_EndLBA1,SectorCount,SectorCount,0,1)
            if result['LLRET'] != 0:
               objMsg.printMsg ('SequentialReadDMAExt: %s' % result)
               ScrCmds.raiseException(14919, "Apple WRC Test-7 - Read Compare Failure - StartLBA:%s EndLBA:%s" %(Step2_StartLBA1,Step2_EndLBA1))

            skipLBA = random.sample(Read_SkipFwd_Blocks,1)[0]
            StartLBA_Calc = Step2_StartLBA1 + skipLBA
            EndLBA_Calc = StartLBA_Calc + SectorCount
            result = ICmd.SequentialReadDMAExt(StartLBA_Calc,EndLBA_Calc,SectorCount,SectorCount,0,0)
            if result['LLRET'] != 0:
               objMsg.printMsg ('SequentialReadDMAExt: %s' % result)
               ScrCmds.raiseException(14919, "Apple WRC Test-7 - Read without Compare Failure - StartLBA:%s EndLBA:%s" %(StartLBA_Calc,EndLBA_Calc))
      ##########################################################################

      ##########################################################################
      #STEP:3 -> - Repeat Step 1 and 2 with different data patterns.
      #            ..Random data (LBA seed)
      #            ..Byte-wise incrementing data pattern.
      #            ..Byte-wise decrementing data pattern.
      #            ..Walking 1's data pattern (0x80, 0x40, 0x20, etc...)
      #            ..Walking 0's data pattern (0x7F, 0xBF, 0xDF, etc...)
      #            ..Fixed pattern: 65E2
      ##########################################################################
      def step3():
         import os
         CE,CP,CN,CV = ConfigId
         ConfigName = CN
         PatternList = ['RANDOM','BITWISE_INC','BITWISE_DEC','WALKONE.PAT','WALKZERO.PAT','65E2']

         for patternname in PatternList:
            self.ClearBinBuffer(7)
            if re.search('.PAT',str(patternname)):
               if testSwitch.virtualRun: continue
               filename = os.path.join(UserDownloadsPath, ConfigName, patternname)
               patternfile = open(filename,'rb')
               try:
                   patterndata = patternfile.read()
                   ICmd.FillBuffer(1, 0, patterndata)
                   ICmd.FillBuffer(2, 0, patterndata)
               finally:
                   patternfile.close()
            else:
                if patternname == '65E2':
                   ICmd.FillBuffByte(1,patternname,0)
                   ICmd.FillBuffByte(2,patternname,0)
                if patternname == 'RANDOM':
                   ICmd.FillBuffRandom(1,0)
                   data = ICmd.GetBuffer(1,0,512)['DATA']
                   ICmd.FillBuffer(2,0,data)
                if patternname == 'BITWISE_INC':
                   ICmd.FillBuffInc(1,0)
                   ICmd.FillBuffInc(2,0)
                if patternname == 'BITWISE_DEC':
                   ICmd.FillBuffDec(1,0)
                   ICmd.FillBuffDec(2,0)

            objMsg.printMsg('*'*20 + "Performing Test-7 : STEP-1 with Data Pattern:%s" %patternname)
            step1()
            objMsg.printMsg('*'*20 + "Performing Test-7 : STEP-2 with Data Pattern:%s" %patternname)
            step2()
      ##########################################################################

      ##########################################################################
      #MAIN WRC TEST7 CALL
      ##########################################################################
      step3()
      ##########################################################################

   #-------------------------------------------------------------------------------------------------------
   def WRCTest3(self):
      ScrCmds.insertHeader("WRC Test-3",headChar='*')

      Zone_StartLBA = 40039168 #0x0262F300 - 20.5GB
      Zone_EndLBA = 27343616 #0x01A13B00 - 14GB
      StepLBA = SectorCount = 256
      self.SetUDMASpeed(3)

      ##########################################################################
      #STEP:1 -> - Starting from 20.5BG location, write skip forward for one to three times,
      #            write skip backward for one time.
      #          - Flush Cache after 80 ~ 240 write and delay after 20 ~120 write.
      #          - Delay amount is increment by (number of write / 100) sec starting from 2sec.
      #          - Write up to 4096 times or until write location is less than 14Gb.
      #          - Save written LBA locations into the buffer.
      ##########################################################################
      def step1():
          objMsg.printMsg('STEP:1 -> Reverse Write: StartLBA:%s EndLBA:%s' %(Zone_EndLBA,Zone_StartLBA))
          self.ClearBinBuffer(3)

          Write_SkipFwd_Blocks = [0x800,0x1000] #2K,4K Blocks
          Write_SkipBwd_Blocks = [0x2800,0x3000,0x3800] #10K,12K,14K Blocks
          FlushCache_CmdRange = random.randrange(80,241)
          WriteDelay_CmdRange = random.randrange(20,121)
          WriteDelay_Time = sleeptime = 2 #2sec
          StartLBA_Calc = EndLBA_Calc = Zone_StartLBA
          FlushCacheCounter = TimeDelayCounter = CommandCount = 0
          self.Write_location = []

          #write skip forward for one to three times - Reverse
          objMsg.printMsg('STEP:1 -> Write_SkipFwd_Blocks:[0x800,0x1000], Write_SkipBwd_Blocks:[0x2800,0x3000,0x3800],FlushCache_CmdRange:[80,240], Delay_CmdRange:[20,120]')
          while EndLBA_Calc > Zone_EndLBA:
             for i in range(random.randrange(1,4)):
                skipLBA = random.sample(Write_SkipFwd_Blocks,1)[0]
                StartLBA_Calc = StartLBA_Calc + skipLBA
                EndLBA_Calc = StartLBA_Calc + SectorCount
                if EndLBA_Calc <= Zone_EndLBA: break
                result = ICmd.SequentialWriteDMAExt(StartLBA_Calc,EndLBA_Calc,StepLBA,SectorCount,0,0)
                if result['LLRET'] != 0:
                   ScrCmds.raiseException(14919, "Apple WRC Test-3 Reverse Write Failure - StartLBA:%s EndLBA:%s skipLBA:%s" %(StartLBA_Calc,EndLBA_Calc,skipLBA))
                   objMsg.printMsg ('SequentialWriteDMAExt: %s' % result)
                else:
                   FlushCacheCounter = FlushCacheCounter + 1
                   TimeDelayCounter = TimeDelayCounter + 1
                   CommandCount = CommandCount + 1
                   self.Write_location.append ((StartLBA_Calc,EndLBA_Calc))

                if FlushCacheCounter >= FlushCache_CmdRange:
                   FlushCacheCounter,FlushCache_CmdRange = self.FlushCache(3,80,241)

                if TimeDelayCounter >= WriteDelay_CmdRange:
                   time.sleep(sleeptime)
                   sleeptime = sleeptime + (TimeDelayCounter/1000.0)
                   WriteDelay_CmdRange = random.randrange(20,121)
                   TimeDelayCounter = 0

             if EndLBA_Calc <= Zone_EndLBA: break
             skipLBA = random.sample(Write_SkipBwd_Blocks,1)[0]
             StartLBA_Calc = StartLBA_Calc - skipLBA
             EndLBA_Calc = StartLBA_Calc - SectorCount             
             if objRimType.CPCRiser():  
                result = ICmd.ReverseWriteDMAExt(StartLBA_Calc,EndLBA_Calc,SectorCount,0,0)                
             elif objRimType.IOInitRiser():
                result = ICmd.ReverseWriteDMAExt(EndLBA_Calc,StartLBA_Calc,StepLBA,SectorCount,0,0)     
             if result['LLRET'] != 0:
                objMsg.printMsg ('ReverseWriteDMAExt: %s' % result)
                ScrCmds.raiseException(14919, "Apple WRC Test-3 Reverse Write Failure - StartLBA:%s EndLBA:%s skipLBA:%s" %(StartLBA_Calc,EndLBA_Calc,skipLBA))
             else:
                FlushCacheCounter = FlushCacheCounter + 1
                TimeDelayCounter = TimeDelayCounter + 1
                CommandCount = CommandCount + 1
                self.Write_location.append ((StartLBA_Calc,EndLBA_Calc))

             if FlushCacheCounter >= FlushCache_CmdRange:
                FlushCacheCounter,FlushCache_CmdRange = self.FlushCache(3,80,241)

             if TimeDelayCounter >= WriteDelay_CmdRange:
                time.sleep(sleeptime)
                sleeptime = sleeptime + (TimeDelayCounter/1000.0)
                WriteDelay_CmdRange = random.randrange(20,121)
                TimeDelayCounter = 0

      ##########################################################################

      ##########################################################################
      #STEP:2 -> - Retrieve the locations from the buffer and read with Data Compare ON.
      #            Read skip backward: 0x400 or 0x800 or 0xC00 or 0x1000
      #          - Read skip backward for one to three times with Data Compare Off.
      #          - Delay after 20 ~100 read. Delay amount is increment by (number of read / 100) sec starting from 2sec.
      #          - Read for all LBA locations in the buffer.
      ##########################################################################
      def step2():
          objMsg.printMsg('STEP:2 -> Read with Data Compare based on STEP:1 write locations')
          objMsg.printMsg('STEP:2 -> Reverse Read without Data Compare')
          self.ClearBinBuffer(3)

          Read_SkipBwd_Blocks = [0x400,0x800,0xC00,0x1000] #1K,2K,3K,4K Blocks
          ReadDelay_Time = sleeptime = 2 #2sec
          ReadDelay_CmdRange = random.randrange(20,101)
          TimeDelayCounter = CommandCount = 0

          for value in self.Write_location:
            Step2_StartLBA = value[0]
            Step2_EndLBA = value[1]
            if Step2_StartLBA < Step2_EndLBA:
               result = ICmd.SequentialReadDMAExt(Step2_StartLBA,Step2_EndLBA,SectorCount,SectorCount,0,1)
               msg = 'SequentialReadDMAExt: %s' % result
            else:            
               result = ICmd.ReverseReadDMAExt(Step2_StartLBA,Step2_EndLBA,SectorCount,0,1)
               msg = 'ReverseReadDMAExt: %s' % result
            if result['LLRET'] != 0:
               objMsg.printMsg (msg)
               ScrCmds.raiseException(14919, "Apple WRC Test-3 - Read Compare Failure - StartLBA:%s EndLBA:%s" %(Step2_StartLBA,Step2_EndLBA))
            else:
               TimeDelayCounter = TimeDelayCounter + 1
               CommandCount = CommandCount + 1

            if TimeDelayCounter >= ReadDelay_CmdRange:
               time.sleep(sleeptime)
               sleeptime = sleeptime + (TimeDelayCounter/1000.0)
               ReadDelay_CmdRange = random.randrange(20,101)
               TimeDelayCounter = 0

            StartLBA_Calc = Step2_StartLBA
            for i in range(random.randrange(1,4)):
               skipLBA = random.sample(Read_SkipBwd_Blocks,1)[0]
               StartLBA_Calc = StartLBA_Calc - skipLBA
               EndLBA_Calc = StartLBA_Calc - SectorCount
               result = ICmd.ReverseReadDMAExt(StartLBA_Calc,EndLBA_Calc,SectorCount,0,0)
               if result['LLRET'] != 0:
                  objMsg.printMsg ('ReverseReadDMAExt: %s' % result)
                  ScrCmds.raiseException(14919, "Apple WRC Test-3 - Read without Compare Failure - StartLBA:%s EndLBA:%s" %(StartLBA_Calc,EndLBA_Calc))
               else:
                  TimeDelayCounter = TimeDelayCounter + 1
                  CommandCount = CommandCount + 1

               if TimeDelayCounter >= ReadDelay_CmdRange:
                  time.sleep(sleeptime)
                  sleeptime = sleeptime + (TimeDelayCounter/1000.0)
                  ReadDelay_CmdRange = random.randrange(20,101)
                  TimeDelayCounter = 0
      ##########################################################################

      ##########################################################################
      #MAIN WRC TEST3 CALL
      ##########################################################################
      step1()
      step2()
      ##########################################################################

   #-------------------------------------------------------------------------------------------------------
   def WRCTest8(self):
      ScrCmds.insertHeader("WRC Test-8",headChar='*')

      Zone_StartLBA = 27343616 #0x01A13B00 - 14GB
      Zone_EndLBA = 41015808 #0x0271DA00 - 21GB
      StepLBA = SectorCount = 256
      self.SetUDMASpeed(8)

      ##########################################################################
      #STEP:1 -> - Write skip backward: Random skipping between 4k, 2k, -6k, -10k, -12k, -14k blocks.
      #          - Randomly issue Flush Cache after 256 ~ 1024 commands
      ##########################################################################
      def step1():
          objMsg.printMsg('STEP:1 -> Write skip backward: StartLBA:%s EndLBA:%s' %(Zone_StartLBA,Zone_EndLBA))
          objMsg.printMsg('STEP:1 -> Random skip:[4K,2K,-6K,-10K,-12K,-14K], FlushCache_CmdRange:[256,1024]')
          self.ClearBinBuffer(8)

          Write_SkipBwd_Blocks = [0x1000,0x800,-(0x1800),-(0x2800),-(0x3000),-(0x3800)] #4K,2K,-6K,-10K,-12K,-14K Blocks
          FlushCache_CmdRange = random.randrange(256,1025)
          StartLBA_Calc = EndLBA_Calc = Zone_EndLBA
          FlushCacheCounter = 0

          while EndLBA_Calc > Zone_StartLBA:
              skipLBA = random.sample(Write_SkipBwd_Blocks,1)[0]
              StartLBA_Calc = StartLBA_Calc + skipLBA
              EndLBA_Calc = StartLBA_Calc + SectorCount
              if EndLBA_Calc <= Zone_StartLBA: break
              result = ICmd.SequentialWriteDMAExt(StartLBA_Calc,EndLBA_Calc,StepLBA,SectorCount,0,0)
              if result['LLRET'] != 0:
                 objMsg.printMsg ('SequentialWriteDMAExt: %s' % result)
                 ScrCmds.raiseException(14919, "Apple WRC Test-8 Write Failure - StartLBA:%s EndLBA:%s skipLBA:%s" %(StartLBA_Calc,EndLBA_Calc,skipLBA))
              else:
                  FlushCacheCounter = FlushCacheCounter + 1

              if FlushCacheCounter >= FlushCache_CmdRange:
                 FlushCacheCounter,FlushCache_CmdRange = self.FlushCache(8,256,1025)
      ##########################################################################

      ##########################################################################
      #STEP:2 -> - Write skip backward: Random skipping between -2k, -4k and -6k blocks.
      #          - Randomly issue Flush Cache after 256 ~ 1024 commands.
      ##########################################################################
      def step2():
          objMsg.printMsg('STEP:2 -> Write skip backward: StartLBA:%s EndLBA:%s' %(Zone_StartLBA,Zone_EndLBA))
          objMsg.printMsg('STEP:2 -> Random skip:[-2k,-4k,-6k], FlushCache_CmdRange:[256,1024]')
          self.ClearBinBuffer(8)

          Write_SkipBwd_Blocks = [0x800,0x1000,0x1800] #2K,4K,6K Blocks
          FlushCache_CmdRange = random.randrange(256,1025)
          StartLBA_Calc = EndLBA_Calc = Zone_EndLBA
          FlushCacheCounter = 0

          while EndLBA_Calc > Zone_StartLBA:
              skipLBA = random.sample(Write_SkipBwd_Blocks,1)[0]
              StartLBA_Calc = StartLBA_Calc - skipLBA
              EndLBA_Calc = StartLBA_Calc - SectorCount
              if EndLBA_Calc <= Zone_StartLBA: break              
              if objRimType.CPCRiser():  
                 result = ICmd.SequentialWriteDMAExt(StartLBA_Calc,EndLBA_Calc,StepLBA,SectorCount,0,0)                 
              elif objRimType.IOInitRiser():
                 result = ICmd.SequentialWriteDMAExt(EndLBA_Calc,StartLBA_Calc,StepLBA,SectorCount,0,0)     
              if result['LLRET'] != 0:
                 objMsg.printMsg ('SequentialWriteDMAExt: %s' % result)
                 ScrCmds.raiseException(14919, "Apple WRC Test-8 Write Failure - StartLBA:%s EndLBA:%s skipLBA:%s" %(StartLBA_Calc,EndLBA_Calc,skipLBA))
              else:
                 FlushCacheCounter = FlushCacheCounter + 1

              if FlushCacheCounter >= FlushCache_CmdRange:
                 FlushCacheCounter,FlushCache_CmdRange = self.FlushCache(8,256,1025)
      ##########################################################################

      ##########################################################################
      #STEP:3 -> - Write Read Compare:
      #          - Write the 1st 200k blocks: Write couple of locations 2k block apart.
      #          - Write decrement with random skipping between 12k and 14k blocks. Save the LBA locations in the buffer.
      #          - With 200k blocks offset, Write on the new locations and save the location in the buffer while retrieve the previous locations from the buffer and read with Data Compare ON.
      #          - Read decrement with random skipping between -64, -128 and -192 blocks. Read with Data Compare Off on the non-written locations.
      #          - Read the last 200k blocks: Retrieve the written locations from buffer and read with Data Compare On.
      #          - Read decrement with random skipping between -64, -128 and -192 blocks. Read with Data Compare Off on the non-written locations.
      #          - Randomly issue Flush Cache after 256 ~ 1024 commands.
      ##########################################################################
      def step3():
          objMsg.printMsg('STEP:3 -> Write skip forward-200K blocks offset: StartLBA:%s EndLBA:%s' %(Zone_StartLBA,Zone_EndLBA))
          objMsg.printMsg('STEP:3 -> Write Decrement skip:[12k,14k],Read Decrement skip:[64,128,192],FlushCache_CmdRange:[256,1024]')
          objMsg.printMsg('STEP:3 -> Read Compare on Written LBA locations')
          objMsg.printMsg('STEP:3 -> Read Decrement without Compare on Non-Written locations')
          self.ClearBinBuffer(8)

          Write_Decrement_Blocks = [0x3000,0x3800] #12K,14K Blocks
          Read_Decrement_Blocks = [0x40,0x80,0xC0] #64,128,192 Blocks
          Blocks_200K = 0x32000 #200K
          FlushCache_CmdRange = random.randrange(256,1025)
          StartLBA_Calc = EndLBA_200K = EndLBA_Calc = Zone_EndLBA
          FlushCacheCounter = 0

          while EndLBA_200K > Zone_StartLBA:
             Write_location = []
             StartLBA_Calc = EndLBA_200K
             EndLBA_200K = EndLBA_200K - Blocks_200K
             if EndLBA_200K <= Zone_StartLBA: break
             while EndLBA_Calc > EndLBA_200K:
                for cnt in range(2):
                    StartLBA_Calc = StartLBA_Calc + 2048 #2K
                    EndLBA_Calc = StartLBA_Calc + SectorCount
                    if EndLBA_Calc <= EndLBA_200K: break
                    result = ICmd.SequentialWriteDMAExt(StartLBA_Calc,EndLBA_Calc,StepLBA,SectorCount,0,0)
                    if result['LLRET'] != 0:
                       objMsg.printMsg ('SequentialWriteDMAExt: %s' % result)
                       ScrCmds.raiseException(14919, "Apple WRC Test-8 Write Failure - StartLBA:%s EndLBA:%s skipLBA:%s" %(StartLBA_Calc,EndLBA_Calc,skipLBA))
                    else:
                       FlushCacheCounter = FlushCacheCounter + 1
                       Write_location.append((StartLBA_Calc,EndLBA_Calc))

                    if FlushCacheCounter >= FlushCache_CmdRange:
                       FlushCacheCounter,FlushCache_CmdRange = self.FlushCache(8,256,1025)

                skipLBA = random.sample(Write_Decrement_Blocks,1)[0]
                StartLBA_Calc = StartLBA_Calc - skipLBA
                EndLBA_Calc = StartLBA_Calc - SectorCount
                if EndLBA_Calc <= EndLBA_200K: break                
                if objRimType.CPCRiser(): 
                   result = ICmd.ReverseWriteDMAExt(StartLBA_Calc,EndLBA_Calc,SectorCount,0,0)                   
                elif objRimType.IOInitRiser():  
                   result = ICmd.ReverseWriteDMAExt(EndLBA_Calc,StartLBA_Calc,StepLBA,SectorCount,0,0)
                if result['LLRET'] != 0:
                   objMsg.printMsg ('ReverseWriteDMAExt: %s' % result)
                   ScrCmds.raiseException(14919, "Apple WRC Test-8 Write Failure - StartLBA:%s EndLBA:%s skipLBA:%s" %(StartLBA_Calc,EndLBA_Calc,skipLBA))
                else:
                   FlushCacheCounter = FlushCacheCounter + 1
                   Write_location.append((StartLBA_Calc,EndLBA_Calc))

                if FlushCacheCounter >= FlushCache_CmdRange:
                   FlushCacheCounter,FlushCache_CmdRange = self.FlushCache(8,256,1025)

             for value in Write_location:
                Step3_StartLBA1 = value[0]
                Step3_EndLBA1 = value[1]
                if Step3_StartLBA1 < Step3_EndLBA1:
                   result = ICmd.SequentialReadDMAExt(Step3_StartLBA1,Step3_EndLBA1,SectorCount,SectorCount,0,1)
                   msg = 'SequentialReadDMAExt: %s' % result
                else:
                   result = ICmd.ReverseReadDMAExt(Step3_StartLBA1,Step3_EndLBA1,SectorCount,0,1)
                   msg = 'ReverseReadDMAExt: %s' % result
                if result['LLRET'] != 0:
                   objMsg.printMsg (msg)
                   ScrCmds.raiseException(14919, "Apple WRC Test-8 Read Failure - StartLBA:%s EndLBA:%s" %(Step3_StartLBA1,Step3_EndLBA1))
                else:
                   FlushCacheCounter = FlushCacheCounter + 1

                if FlushCacheCounter >= FlushCache_CmdRange:
                   FlushCacheCounter,FlushCache_CmdRange = self.FlushCache(8,256,1025)

                skipLBA = random.sample(Read_Decrement_Blocks,1)[0]
                Step3_StartLBA2 = Step3_StartLBA1 - skipLBA
                Step3_EndLBA2 = Step3_StartLBA2 - SectorCount
                result = ICmd.ReverseReadDMAExt(Step3_StartLBA2,Step3_EndLBA2,SectorCount,0,0)
                if result['LLRET'] != 0:
                   objMsg.printMsg ('ReverseReadDMAExt: %s' % result)
                   ScrCmds.raiseException(14919, "Apple WRC Test-8 Read Failure - StartLBA:%s EndLBA:%s" %(Step3_StartLBA2,Step3_EndLBA2))
                else:
                   FlushCacheCounter = FlushCacheCounter + 1

                if FlushCacheCounter >= FlushCache_CmdRange:
                   FlushCacheCounter,FlushCache_CmdRange = self.FlushCache(8,256,1025)
      ##########################################################################

      ##########################################################################
      #MAIN WRC TEST8 CALL
      ##########################################################################
      objMsg.printMsg('*'*20 + "Performing Test-8 : STEP-1")
      step1()
      objMsg.printMsg('*'*20 + "Performing Test-8 : STEP-2")
      step2()
      objMsg.printMsg('*'*20 + "Performing Test-8 : STEP-3")
      step3()
      ##########################################################################

   #-------------------------------------------------------------------------------------------------------
   def WRCTest9(self):
      ScrCmds.insertHeader("WRC Test-9",headChar='*')

      Zone_StartLBA = 27343616 #0x01A13B00 - 14GB
      Zone_EndLBA = 41015808 #0x0271DA00 - 21GB
      Zone1_StartLBA = 27394048 #0x01A20000 - 14GB
      Zone1_EndLBA = 31653888 #0x01E30000 - 16.2GB
      Zone2_StartLBA = 34734080 #0x02120000 - 17.8GB
      Zone2_EndLBA = 38993920 #0x02530000 - 20GB
      StepLBA = SectorCount = 256
      self.SetUDMASpeed(9)

      ##########################################################################
      #STEP:1 -> - Write skip forward: Random skipping between 2k, 4k, 6k, 8k and 10k blocks.
      #          - Randomly issue Flush Cache after 512 ~ 1536 commands.
      #          - Save the written locations fall within Zone 1 into Buffer 0.
      #          - Save the written locations fall within Zone 2 into Buffer 1.
      ##########################################################################
      def step1():
          objMsg.printMsg('STEP:1 -> Write skip forward: StartLBA:%s EndLBA:%s' %(Zone_StartLBA,Zone_EndLBA))
          objMsg.printMsg('STEP:1 -> Random skip:[2k,4k,6k,8k,10k], FlushCache_CmdRange:[512,1536]')
          self.ClearBinBuffer(9)

          Write_SkipFwd_Blocks = [0x800,0x1000,0x1800,0x2000,0x2800] #2K,4K,6K,8K,10K Blocks
          FlushCache_CmdRange = random.randrange(512,1537)
          StartLBA_Calc = Zone_StartLBA
          EndLBA_Calc = FlushCacheCounter = CommandCount = 0
          self.Write_Zone1_location = []
          self.Write_Zone2_location = []

          while EndLBA_Calc < Zone_EndLBA:
              skipLBA = random.sample(Write_SkipFwd_Blocks,1)[0]
              StartLBA_Calc = StartLBA_Calc + skipLBA
              EndLBA_Calc = StartLBA_Calc + SectorCount
              if EndLBA_Calc >= Zone_EndLBA: break
              result = ICmd.SequentialWriteDMAExt(StartLBA_Calc,EndLBA_Calc,StepLBA,SectorCount,0,0)
              if result['LLRET'] != 0:
                 objMsg.printMsg ('SequentialWriteDMAExt: %s' % result)
                 ScrCmds.raiseException(14919, "Apple WRC Test-9 Write Failure - StartLBA:%s EndLBA:%s skipLBA:%s" %(StartLBA_Calc,EndLBA_Calc,skipLBA))
              else:
                 FlushCacheCounter = FlushCacheCounter + 1
                 CommandCount = CommandCount + 1
                 if (StartLBA_Calc >= Zone1_StartLBA) and (EndLBA_Calc <= Zone1_EndLBA):
                    self.Write_Zone1_location.append(StartLBA_Calc)
                 if (StartLBA_Calc >= Zone2_StartLBA) and (EndLBA_Calc <= Zone2_EndLBA):
                    self.Write_Zone2_location.append(StartLBA_Calc)

              if FlushCacheCounter >= FlushCache_CmdRange:
                 FlushCacheCounter,FlushCache_CmdRange = self.FlushCache(9,512,1537)
      ##########################################################################

      ##########################################################################
      #STEP:2 -> - Read skip forward with Data Compare Off:
      #          - Random skipping between 2k, 4k, 6k, 8k and 10k blocks.
      ##########################################################################
      def step2():
          objMsg.printMsg('STEP:2 -> Read skip forward without Data Compare: StartLBA:%s EndLBA:%s' %(Zone_StartLBA,Zone_EndLBA))
          objMsg.printMsg('STEP:2 -> Random skip:[2k,4k,6k,8k,10k]')
          self.ClearBinBuffer(9)

          Read_SkipFwd_Blocks = [0x800,0x1000,0x1800,0x2000,0x2800] #2K,4K,6K,8K,10K Blocks
          StartLBA_Calc = Zone_StartLBA
          EndLBA_Calc = 0

          while EndLBA_Calc < Zone_EndLBA:
              skipLBA = random.sample(Read_SkipFwd_Blocks,1)[0]
              StartLBA_Calc = StartLBA_Calc + skipLBA
              EndLBA_Calc = StartLBA_Calc + SectorCount
              if EndLBA_Calc >= Zone_EndLBA: break
              result = ICmd.SequentialReadDMAExt(StartLBA_Calc,EndLBA_Calc,SectorCount,SectorCount,0,0)
              if result['LLRET'] != 0:
                 objMsg.printMsg ('SequentialReadDMAExt: %s' % result)
                 ScrCmds.raiseException(14919, "Apple WRC Test-9 - Sequential Read Failure - StartLBA:%s EndLBA:%s" %(StartLBA_Calc,EndLBA_Calc))
      ##########################################################################

      ##########################################################################
      #STEP:3 -> - Random Read:
      #          - Read random locations in Zone 1 for 10x times with Data Compare Off.
      #          - Retrieve random location from Buffer 0 and Read with Data Compare On.
      #          - Read random locations in Zone 2 for 10x times with Data Compare Off.
      #          - Retrieve random location from Buffer 1 and Read with Data Compare On.
      ##########################################################################
      def step3():
          objMsg.printMsg('STEP:3 -> Read random locations in Zone-1 for 10x times with Data Compare Off.')
          self.ClearBinBuffer(9)

          EndLBA_Calc = 0
          for cnt in range(10):
             StartLBA_Calc = random.randrange(Zone1_StartLBA,Zone1_EndLBA)
             EndLBA_Calc = StartLBA_Calc + SectorCount
             result = ICmd.SequentialReadDMAExt(StartLBA_Calc,EndLBA_Calc,SectorCount,SectorCount,0,0)
             if result['LLRET'] != 0:
                objMsg.printMsg ('SequentialReadDMAExt: %s' % result)
                ScrCmds.raiseException(14919, "Apple WRC Test-9 - Sequential Read Failure - StartLBA:%s EndLBA:%s" %(StartLBA_Calc,EndLBA_Calc))

          objMsg.printMsg('STEP:3 -> Retrieve random location from Step:1 - Zone:1 Buffer and Read with Data Compare On.')
          EndLBA_Calc = 0
          for cnt in range(10):
             StartLBA_Calc = random.sample(self.Write_Zone1_location,1)[0]
             EndLBA_Calc = StartLBA_Calc + SectorCount
             result = ICmd.SequentialReadDMAExt(StartLBA_Calc,EndLBA_Calc,SectorCount,SectorCount,0,1)
             if result['LLRET'] != 0:
                objMsg.printMsg ('SequentialReadDMAExt: %s' % result)
                ScrCmds.raiseException(14919, "Apple WRC Test-9 - Sequential Read Failure - StartLBA:%s EndLBA:%s" %(StartLBA_Calc,EndLBA_Calc))

          objMsg.printMsg('STEP:3 -> Read random locations in Zone-2 for 10x times with Data Compare Off.')
          EndLBA_Calc = 0
          for cnt in range(10):
             StartLBA_Calc = random.randrange(Zone2_StartLBA,Zone2_EndLBA)
             EndLBA_Calc = StartLBA_Calc + SectorCount
             result = ICmd.SequentialReadDMAExt(StartLBA_Calc,EndLBA_Calc,SectorCount,SectorCount,0,0)
             if result['LLRET'] != 0:
                objMsg.printMsg ('SequentialReadDMAExt: %s' % result)
                ScrCmds.raiseException(14919, "Apple WRC Test-9 - Sequential Read Failure - StartLBA:%s EndLBA:%s" %(StartLBA_Calc,EndLBA_Calc))

          objMsg.printMsg('STEP:3 -> Retrieve random location from Step:1 - Zone:2 Buffer and Read with Data Compare On.')
          EndLBA_Calc = 0
          for cnt in range(10):
             StartLBA_Calc = random.sample(self.Write_Zone2_location,1)[0]
             EndLBA_Calc = StartLBA_Calc + SectorCount
             result = ICmd.SequentialReadDMAExt(StartLBA_Calc,EndLBA_Calc,SectorCount,SectorCount,0,1)
             if result['LLRET'] != 0:
                objMsg.printMsg ('SequentialReadDMAExt: %s' % result)
                ScrCmds.raiseException(14919, "Apple WRC Test-9 - Sequential Read Failure - StartLBA:%s EndLBA:%s" %(StartLBA_Calc,EndLBA_Calc))
      ##########################################################################
      ##########################################################################
      #MAIN WRC TEST9 CALL
      ##########################################################################
      objMsg.printMsg('*'*20 + "Performing Test-9 : STEP-1")
      step1()
      objMsg.printMsg('*'*20 + "Performing Test-9 : STEP-2")
      step2()
      objMsg.printMsg('*'*20 + "Performing Test-9 : STEP-3")
      step3()
      ##########################################################################

###########################################################################################################
class CHpIntgSim(CState):
   """
      HP Integration Simulation Test. This test contains:
       - test one   (Primary OS Creation Simulation)
       - test two   (Recovery Partition Creation OS Simulation)
       - test three (Restore Partition to Primary OS Simulation for Customer Image)
       - test four  (Burn-In Test Simulation)
       - test five  (Read Scan Whole Drive)
   """
   def __init__(self, dut, params={}):
      self.params = params
      self.dut = dut
      depList = []
      CState.__init__(self, dut, depList)

   def run(self):
      oIdentifyDevice = CIdentifyDevice()
      self.maxLBA = oIdentifyDevice.getMaxLBA()
      ICmd.FillBuffRandom(WBF, 0, 512 * 256, exc = 1)
      test_to_run = TP.prm_HP_INTG_SIM.get('TEST_TO_RUN', None)

      if 'OS_CREATION' in test_to_run:
         ScrCmds.statMsg("--- Create Primary OS Simulation ---------------------")
         startLBA    = 0
         endLBA      = 19531250
         stepLBA     = 63
         sectorCount = stepLBA
         CHelper().sequentialWriteDMAExt(startLBA, endLBA, stepLBA, sectorCount, 14852)

      if 'RP_CREATION' in test_to_run:
         ScrCmds.statMsg("--- Create Recovery Partition Simulation -------------")
         startLBA    = self.maxLBA - 20531250
         endLBA      = startLBA + 19531240
         stepLBA     = 63
         sectorCount = stepLBA
         CHelper().sequentialWriteDMAExt(startLBA, endLBA, stepLBA, sectorCount, 14852)

      if 'RP_RESTORATION' in test_to_run:
         ScrCmds.statMsg("--- Restore Partition to Primary OS Simulation for Customer Image ---")
         startRdLBA    = self.maxLBA - 21531250
         startWrLBA    = 0
         rangeLBA      = 9765620
         sectorCount   = 63
         CHelper().sequentialWRCopy(startRdLBA, startWrLBA, rangeLBA, sectorCount, 14852)

      if 'BURN_IN_TEST' in test_to_run:
         ScrCmds.statMsg("--- Burn In Test -------------------------------------")
         random.seed()
         # random (write/read, read/write) at OD
         startRdLBA    = 0
         startWrLBA    = startRdLBA
         rangeLBA      = 19521250
         stepLBA       = 256
         sectorCount   = stepLBA
         rRW = random.randint(0, 1)
         if rRW == 0:
            res = ICmd.SequentialWRDMAExt(startWrLBA, rangeLBA, stepLBA, sectorCount)
            if res['LLRET'] != OK:
               ScrCmds.statMsg("Result: %s" % res)
               ScrCmds.raiseException(14852, "Sequential W/R DMA Ext at OD fail!")
         else:
            CHelper().sequentialWRCopy(startRdLBA, startWrLBA, rangeLBA, sectorCount, 14852)
         # random (write/read, read/write) at ID
         tenPercentMaxLBA = self.maxLBA / 10
         startRdLBA    = self.maxLBA - tenPercentMaxLBA
         startWrLBA    = startRdLBA
         rangeLBA      = tenPercentMaxLBA
         stepLBA       = 256
         sectorCount   = stepLBA
         rRW = random.randint(0, 1)
         if rRW == 0:
            res = ICmd.SequentialWRDMAExt(startWrLBA, self.maxLBA, stepLBA, sectorCount)
            if res['LLRET'] != OK:
               ScrCmds.statMsg("Result: %s" % res)
               ScrCmds.raiseException(14852, "Sequential W/R DMA Ext at ID fail!")
         else:
            CHelper().sequentialWRCopy(startRdLBA, startWrLBA, rangeLBA, sectorCount, 14852)

      if 'READ_SCAN' in test_to_run:
         ScrCmds.statMsg("--- Read Scan Whole Drive ----------------------------")
         startLBA    = 0
         endLBA      = self.maxLBA
         stepLBA     = 256
         sectorCount = stepLBA
         CHelper().sequentialReadDMAExt(startLBA, endLBA, stepLBA, sectorCount, 14852)

###########################################################################################################
class CAppleStoneCutter(CState):
   """
   Apple Stone Cutter Test contains:
    - SC Test  1: Read Sequential
    - SC Test  2: Random Read
    - SC Test  3: Static Read
    - SC Test  4: Read Reverse
    - SC Test  5: Read Sequential with Random Skip
    - SC Test  6: Read Sequential with Random and Random Skip
    - SC Test 11: Read Write
    - SC Test 12: Write Read Random
    - SC Test 13: Write Read Static
    - SC Test 14: Read Write, Reverse
    - SC Test 15: Read Write Sequential with Random
    - SC Test 16: R/W Sequential with Random and Random Skip
    - SC Test 21: Write
    - SC Test 23: Static Write
    - SC Test 26: Write, Sequential with Random Skip
   """
   def __init__(self, dut, params={}):
      self.params = params
      self.dut = dut
      depList = []
      CState.__init__(self, dut, depList)
      
      self.helper = CHelper()

   def run(self):
      # self.__T1_readSeq()
      self.__T2_readRnd(40)
      self.__T3_readStc(25)
      self.__T4_readRev(25)
      # self.__T5_readSeq_wRndSkip()
      # self.__T6_readSeq_wRndAndRndSkip()
      # self.__T11_rw()
      self.__T12_rwRnd(6)
      self.__T13_rwStc(21)
      self.__T14_rwRev()
      self.__T15_rwSeq_wRnd()
      # self.__T16_rwSeq_wRndAndRndSkip()
      # self.__T21_write()
      self.__T23_writeStc(620)
      # self.__T26_writeSeq_wRndSkip()

   def __T2_readRnd(self, testTime = 40):
      """
      SC Test  2: Random Read.

      @type testTime: integer
      @param testTime: test time in second

      Do entire drive random read with random band delay for testTime long.
      """
      ScrCmds.statMsg("--- SC Test  2: Random Read. -------------------------")
      if testSwitch.virtualRun: testTime = 0
      oIdentifyDevice = CIdentifyDevice()
      endLBA = oIdentifyDevice.getMaxLBA() - 1
      ScrCmds.statMsg("End LBA: %s" % endLBA)

      # random band delay component
      # delay time bands is in second
                                    # no delay has 10x possibility than 1nd band
      delayTB = [[0.01, 0.03],      # 1st band has 20x possibility than 2nd band
                 [0.03, 0.11]]      # 2nd band

      random.seed()
      readNum   = 0                    # total reading process in times
      startTime = time.time()
      stopTime  = startTime + testTime
      while True:
         loc = random.randint(0, endLBA)
         CHelper().readDMAExt(loc, 1, 14853)
         readNum += 1
         # random band delay
         pTB = random.randint(0, 30)   # possibility of time band
         if pTB < 10:                  # no delay
            pass
         else:
            if pTB < 30:               # 1st band delay
               delay = random.uniform(delayTB[0][0], delayTB[0][1])
            else:                      # 2nd band delay
               delay = random.uniform(delayTB[1][0], delayTB[1][1])
            time.sleep(delay)
         # end
         if (time.time() > stopTime): break

      ScrCmds.statMsg("Number of Loop = %s times" % readNum)

   def __T3_readStc(self, testTime = 25):
      """
      SC Test  3: Static Read.

      @type testTime: integer
      @param testTime: test time in second

      Do static read at LBA 0 with specified delay locations for testTime long.
      """
      ScrCmds.statMsg("--- SC Test  3: Static Read. -------------------------")
      if testSwitch.virtualRun: testTime = 0
      # random delay location component
      # delay location is in second
      delayTB = [0.002,    # 1st location: possibility is 20 out of all
                 0.004,    # 2nd location: possibility is 15 out of all
                 0.017,    # 3rd location: possibility is  1 out of all
                 0.033]    # 4th location: possibility is  8 out of all
                           # ------------------- total is 44

      random.seed()
      readNum   = 0                    # total reading process in times
      startTime = time.time()
      stopTime  = startTime + testTime
      while True:
         # read static at LBA 0         
         CHelper().readDMAExt(0, 1, 14853)

         readNum += 1
         # random delay locations
         pTB = random.randint(0, 43)   # possibility of delay location
         if   pTB < 20: delay = delayTB[0]   # 1st location
         elif pTB < 35: delay = delayTB[1]   # 2nd location
         elif pTB < 36: delay = delayTB[2]   # 3rd location
         else:          delay = delayTB[3]   # 4th location
         time.sleep(delay)
         # end
         if (time.time() > stopTime): break

      ScrCmds.statMsg("Number of Loop = %s times" % readNum)

   def __T4_readRev(self, testTime = 25):
      """
      SC Test  4: Read Reverse.

      @type testTime: integer
      @param testTime: test time in second

      Do reverse read from LBA 3500 to LBA 0 with skipping 250 LBAs for
      testTime long.
      """
      ScrCmds.statMsg("--- SC Test  4: Read Reverse -------------------------")
      if testSwitch.virtualRun: testTime = 0
      startTime = time.time()
      stopTime  = startTime + testTime
      while True:
         ret = ICmd.ReverseReadDMAExt(3500, 0, 250, 1)
         if ret['LLRET'] != OK:
            ScrCmds.raiseException(14853, "Reverse Read DMA Ext fail")
         # end
         if (time.time() > stopTime): break
      elapsedTime = time.time() - startTime
      ScrCmds.statMsg("Elapsed Time   = %s minutes %s seconds" % \
                      (int(elapsedTime / 60), int(elapsedTime % 60)))


   def __T12_rwRnd(self, testTime = 6):
      """
      SC Test 12: Write Read Random.

      @type testTime: integer
      @param testTime: test time in second

      Do random read/write at random two locations for testTime long.
      One location is at LBA 0, the other is at LBA 4200000 (~2GB).
      """
      ScrCmds.statMsg("--- SC Test 12: Write Read Random --------------------")
      if testSwitch.virtualRun: testTime = 0
      random.seed()
      readNum   = 0                    # total reading process in times
      writeNum  = 0                    # total writing process in times
      startTime = time.time()
      stopTime  = startTime + testTime
      while True:
         rProc = random.randint(0, 1)  # random reading or writng process
         rLoc  = random.randint(0, 1)  # random locations

         if rLoc == 0:  loc = 0
         else:          loc = 4200000

         if rProc == 0:
            CHelper().readDMAExt(loc, 1, 14853)
            readNum += 1
         else:
            CHelper().writeDMAExt(loc, 1, 14853)
            writeNum += 1

         # end
         if (time.time() > stopTime): break

      ScrCmds.statMsg("Number of Read  Loop = %5s times" % readNum)
      ScrCmds.statMsg("Number of Write Loop = %5s times" % writeNum)

   def __T13_rwStc(self, testTime = 21):
      """
      SC Test 13: Write Read Static.

      @type testTime: integer
      @param testTime: test time in second

      Do static read at LBA 0 and static write at LBA 3305392 (~1.58GB) for
      21 seconds.
      """
      ScrCmds.statMsg("--- SC Test 13: Write Read Static --------------------")
      if testSwitch.virtualRun: testTime = 0
      loopNum   = 0                    # total reading/writing process in times
      readLoc   = 0
      writeLoc  = 3305392
      startTime = time.time()
      stopTime  = startTime + testTime
      while True:
         loopNum += 1
         CHelper().readDMAExt(readLoc, 1, 14853)
         CHelper().writeDMAExt(writeLoc, 1, 14853)
         if (time.time() > stopTime): break

      ScrCmds.statMsg("Number of Read/Write Loop = %5s times" % loopNum)

   def __T23_writeStc(self, testTime = 620):
      """
      SC Test 23: Static Write.

      @type testTime: integer
      @param testTime: test time in second

      Do static write at LBA 3305648 (~1.58GB) and random (every one second)
      write at LBA 0. Total test time 620 seconds.
      """
      ScrCmds.statMsg("--- SC Test 23: Static Write -------------------------")
      if testSwitch.virtualRun: testTime = 0
      writeLoc1  = 3305648             # writing location 1
      writeNum1  = 0                   # total writing process 1 in times
      writeLoc2  = 0                   # writing location 1
      writeNum2  = 0                   # total writing process 2 in times
      startTime  = time.time()
      stopTime   = startTime + testTime
      oneSecTime = time.time()         # one second time
      randFlg    = 1                   # random flag for write or not write
      while True:
         CHelper().writeDMAExt(writeLoc1, 1, 14853)
         writeNum1 += 1

         # get new random flag every one second
         if time.time() > oneSecTime + 1:
            randFlg = random.randint(0, 1)
            oneSecTime = time.time()

         if randFlg:
            CHelper().writeDMAExt(writeLoc2, 1, 14853)
            writeNum2 += 1
         if (time.time() > stopTime): break

      ScrCmds.statMsg("Number of Loop = %5s times" % writeNum1)

   def __T14_rwRev(self):
      """
      SC Test 14: Read Write, Reverse.

      The algorithm for this test as follow:
      1) Do sequential read from LBA 0h to 1F40h (8000d) with 256 sector size.
      2) Do read, write, write, read, and write process. Keep looping this
         step for 60 seconds. Count writing process until 3000 times then go
         to step 4).
      3) Increase delay by 100ms. Reset to zero if more than 15 sec. Loop
         back step 2)
      4) Do sequential read from LBA 3270B0h (3305648d) to 3400B0h (3408048d)
         with 256 sector size.

      Write : Each writing process writes only to one LBA location start
              form first LBA 3270B0h. Another call for writing process will
              write to another sequential LBA location skipped by 800h from
              last location. Keep do sequential write to 50 different LBA
              location and restart again from first LBA.
      Read  : Reverse read from LBA E00h to 0 with skipping every 100h LBA.
      """
      ScrCmds.statMsg("--- SC Test 14: Read Write, Reverse ------------------")

      # 1) Do sequential read from LBA 0h to 1F40h (8000d) with 256 sector size.
      ScrCmds.statMsg("- Do sequential read from LBA 0h to 1F40h (8000d) with 256 sector size.")
      startTime   = time.time()
      ScrCmds.statMsg("Start Time     = %s" % startTime)
      CHelper().sequentialReadDMAExt(0, 8000, 256, 256, 14853)
      self.__endTestInfo(startTime = startTime, endTime = time.time())

      # 2) Do read, write, write, read, and write process. Keep looping this
      #    step for 60 seconds. Count writing process until 3000 times then go
      #    to step 4).
      # 3) Increase delay by 100ms. Reset to zero if more than 15 sec. Loop
      #    back step 2)
      ScrCmds.statMsg("- Do read, write, write, read, and write process.")

      startTime = time.time()
      ScrCmds.statMsg("Start Time     = %s" % startTime)
      startLBAWrite = [0x3270B0]
      startLBARead  = [0xE00]
      writeNum      = [0]
      delay         = 0
      # set 60 seconds timer
      startTime60   = time.time()
      stopTime60    = startTime60 + 60   # 60 seconds
      while True:
         self.__T14_read(startLBARead)
         if self.__T14_write(startLBAWrite, writeNum): 
            break
         if self.__T14_write(startLBAWrite, writeNum): 
            break
         
         self.__T14_read(startLBARead)
         if self.__T14_write(startLBAWrite, writeNum): 
            break

         if (time.time() > stopTime60):
            delay += 0.1               # increase delay by 100ms
            if (delay > 15): delay = 0 # reset delay if it's more than 15 seconds
            time.sleep(delay)
            # reset 60 seconds timer
            startTime60 = time.time()
            stopTime60  = startTime60 + 60 # 60 seconds

      endTime = time.time()
      self.__endTestInfo(startTime = startTime, endTime = endTime, \
                         loopNum = writeNum)

      # 4) Do sequential read from LBA 3270B0h (3305648d) to 3400B0h (3408048d)
      #    with 256 sector size.
      ScrCmds.statMsg("- Do sequential read from LBA 3270B0h (3305648d) to 3400B0h (3408048d) with 256 sector size.")
      startTime   = time.time()
      ScrCmds.statMsg("Start Time     = %s" % startTime)
      CHelper().sequentialReadDMAExt(3305648, 3408048, 256, 256, 14853)
      self.__endTestInfo(startTime = startTime, endTime = time.time())

   def __T14_write(self, startLBAWrite, writeNum):
      """
      Writing function for test number 14. This function returns True if
      writing number reaches 3000 times or more and returns False if it less.

      Write : Each writing process writes only to one LBA location start
              form first LBA 3270B0h. Another call for writing process will
              write to another sequential LBA location skipped by 800h from
              last location. Keep do sequential write to 50 different LBA
              location and restart again from first LBA.
      """
      CHelper().writeDMAExt(startLBAWrite[0], 1, 14853)
      writeNum[0] += 1
      # endLBA = startLBA + (50 * 800h) = 3270B0h + 19000h = 3400B0h
      startLBAWrite[0] += 0x800
      if startLBAWrite[0] > 0x3400B0:
         startLBAWrite[0] = 0x3270B0
         # stop the test if the number of write reaches 3000 times

         if writeNum[0] >= 3000:
            return True
         else:
            return False

   def __T14_read(self, startLBARead):
      """
      Read  : Reverse read from LBA E00h to 0 with skipping every 100h LBA.
      """
      CHelper().readDMAExt(startLBARead[0], 1, 14853)
      startLBARead[0] -= 0x100
      if startLBARead[0] < 0: startLBARead[0] = 0xE00

   def __T15_rwSeq_wRnd(self):
      """
      SC Test 15: Read Write Sequential with Random

      The algorithm for this test as follow:
      1) Do sequential read from LBA 0h to 1F40h (8000d) with 256 sector size.
      2) Do read, write, write, read, and write process. Keep looping this
         step for 60 seconds. Count writing process until 3000 times then go
         to step 4).
      3) Increase delay by 100ms. Reset to zero if more than 15 sec. Loop
         back step 2)
      4) Do sequential read from LBA 3270B0h (3305648d) to 3400B0h (3408048d)
         with 256 sector size.

      Write : Each writing process writes only to one LBA location start
              form first LBA 3270B0h. Another call for writing process will
              write to another sequential LBA location skipped by 800h from
              last location. Keep do sequential write to 50 different LBA
              location and restart again from first LBA.
      Read  : Sequential read from LBA 0 to E00h with skipping every 100h LBA.
      """
      ScrCmds.statMsg("--- SC Test 15: Read Write Sequential with Random ----")

      # 1) Do sequential read from LBA 0h to 1F40h (8000d) with 256 sector size.
      ScrCmds.statMsg("- Do sequential read from LBA 0h to 1F40h (8000d) with 256 sector size.")
      startTime   = time.time()
      ScrCmds.statMsg("Start Time     = %s" % startTime)
      CHelper().sequentialReadDMAExt(0, 8000, 256, 256, 14853)
      self.__endTestInfo(startTime = startTime, endTime = time.time())

      # 2) Do read, write, write, read, and write process. Keep looping this
      #    step for 60 seconds. Count writing process until 3000 times then go
      #    to step 4).
      # 3) Increase delay by 100ms. Reset to zero if more than 15 sec. Loop
      #    back step 2)
      ScrCmds.statMsg("- Do read, write, write, read, and write process.")

      startTime = time.time()
      ScrCmds.statMsg("Start Time     = %s" % startTime)
      startLBAWrite = [0x3270B0]
      startLBARead  = [0]
      writeNum      = [0]
      delay         = 0
      # set 60 seconds timer
      startTime60   = time.time()
      stopTime60    = startTime60 + 60   # 60 seconds
      while True:
         self.__T15_read(startLBARead)
         if self.__T15_write(startLBAWrite, writeNum): 
            break
         if self.__T15_write(startLBAWrite, writeNum): 
            break
         self.__T15_read(startLBARead)
         if self.__T15_write(startLBAWrite, writeNum): 
            break

         if (time.time() > stopTime60):
            delay += 0.1               # increase delay by 100ms
            if (delay > 15): delay = 0 # reset delay if it's more than 15 seconds
            time.sleep(delay)
            # reset 60 seconds timer
            startTime60 = time.time()
            stopTime60  = startTime60 + 60 # 60 seconds

      endTime = time.time()
      self.__endTestInfo(startTime = startTime, endTime = endTime, \
                         loopNum = writeNum)

      # 4) Do sequential read from LBA 3270B0h (3305648d) to 3400B0h (3408048d)
      #    with 256 sector size.
      ScrCmds.statMsg("- Do sequential read from LBA 3270B0h (3305648d) to 3400B0h (3408048d) with 256 sector size.")
      startTime   = time.time()
      ScrCmds.statMsg("Start Time     = %s" % startTime)
      CHelper().sequentialReadDMAExt(3305648, 3408048, 256, 256, 14853)
      self.__endTestInfo(startTime = startTime, endTime = time.time())

   def __T15_write(self, startLBAWrite, writeNum):
      """
      Writing function for test number 14. This function returns True if
      writing number reaches 3000 times or more and returns False if it less.

      Write : Each writing process writes only to one LBA location start
              form first LBA 3270B0h. Another call for writing process will
              write to another sequential LBA location skipped by 800h from
              last location. Keep do sequential write to 50 different LBA
              location and restart again from first LBA.
      """
      return self.__T14_write(startLBAWrite, writeNum)

   def __T15_read(self, startLBARead):
      """
      Read  : Sequential read from LBA 0 to E00h with skipping every 100h LBA.
      """
      CHelper().readDMAExt(startLBARead[0], 1, 14853)
      startLBARead[0] += 0x100
      if startLBARead[0] > 0xE00: startLBARead[0] = 0

   def __endTestInfo(self, startTime, endTime = None, loopNum = None):
      # display end time
      if endTime == None:
         endTime = time.time()
      ScrCmds.statMsg("End Time       = %s" % endTime)
      # display elapsed time
      elapsedTime = endTime - startTime
      ScrCmds.statMsg("Elapsed Time   = %s minutes %s seconds" % \
                      (int(elapsedTime / 60), int(elapsedTime % 60)))
      # display loop number
      if loopNum != None:
         ScrCmds.statMsg("Number of Loop = %s times" % loopNum)

###########################################################################################################
class CSIE_FITS_WRC_Test(CState):
   """
   SIE FITS Write Read Compare Test
    - Delay Write with DIPM Enable
    - Mtest1
    - Creshndo (Wrt/Rd Compare)
    - Inchworm (Wrt/Rd Compare)
   """
   def __init__(self, dut, params={}):
      self.params = params
      self.dut = dut
      depList = []
      CState.__init__(self, dut, depList)

   def run(self):
      objPwrCtrl.powerCycle(5000, 12000, 10, 30)
      self.startTestLba = 0
      self.maxTestLba = 10000000
      if testSwitch.virtualRun: self.maxTestLba = 1000
      self.endTestLba = (self.startTestLba + self.maxTestLba) - 1

      oIdentifyDevice = CIdentifyDevice()
      self.maxLBA = oIdentifyDevice.getMaxLBA()
      # check if the maximum test LBA exceeds maximum drive LBA
      ScrCmds.statMsg("Start Test LBA               : %s" % self.startTestLba)
      ScrCmds.statMsg("End Test LBA                 : %s" % self.endTestLba)
      if self.endTestLba > (self.maxLBA - 1):
         ScrCmds.raiseException(14833, 'Maximum Test LBA exceeds Maximum Drive LBA')

      self.__delay_write_DIPM()
      self.__mtest1()
      self.__creshndo()
      self.__inchworm()
      objPwrCtrl.powerCycle(5000, 12000, 10, 30)

   # ------------------------------------------ Delay Write with DIPM Enable ---
   def __delay_write_DIPM(self):
      ScrCmds.statMsg("--------------------------------- Delay Write DIPM ---")
      # Enable DIPM
      res = enable_DIPM(exc = 0)
      ScrCmds.statMsg("Enable DIPM result: %s" % res)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14833, 'Fail SetFeatures 0x10, 0x03')

      # Set APM 0xCO
      res = enable_APM(0xC0, exc = 0)
      ScrCmds.statMsg("Set APM 0xC0 result: %s" % res)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14833, 'Fail SetFeatures 0x05, 0xC0')

      # Disable Write Cache
      res = disable_WriteCache(exc = 0)
      ScrCmds.statMsg("Disable Write Cache result: %s" % res)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14833, 'Fail SetFeatures 0x82')

      # Disable Read Look Ahead
      res = disable_ReadLookAhead(exc = 0)
      ScrCmds.statMsg("Disable Read Look Ahead result: %s" % res)
      if res['LLRET'] != 0:
         ScrCmds.raiseException(14833, 'Fail SetFeatures 0x55')

      # fill buffer with byte wise increment (0x00, 0x01, 0x02, ..., 0xFF)
      ScrCmds.statMsg("Fill buffer with byte wise increment (0x00, 0x01, 0x02, ..., 0xFF).")
      res = ICmd.FillBuffInc(WBF, 0x00, 512 * 256, 0x00)
      ScrCmds.statMsg("Result: %s" % res)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14833, 'Fill Buffer Increment Failed!')

      # do writing with increment delay
      minDelay  = 100      # ms
      maxDelay  = 1000     # ms
      stepDelay = 100      # ms
      CHelper().seqDelayWrite(self.startTestLba, self.endTestLba, 256, \
                              minDelay, maxDelay, stepDelay, 14833)

      # Disable DIPM
      res = disable_DIPM(exc = 0)
      ScrCmds.statMsg("Disable DIPM result: %s" % res)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14833, 'Fail SetFeatures 0x90, 0x03')

      # Disable APM
      res = disable_APM(exc = 0)
      ScrCmds.statMsg("Disable APM result: %s" % res)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14833, 'Fail SetFeatures 0x85')

      # Enable Write Cache
      res = enable_WriteCache(exc = 0)
      ScrCmds.statMsg("Enable Write Cache result: %s" % res)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14833, 'Fail SetFeatures 0x02')

      # Enable Read Look Ahead
      res = enable_ReadLookAhead(exc = 0)
      ScrCmds.statMsg("Enable Read Look Ahead result: %s" % res)
      if res['LLRET'] != 0:
         ScrCmds.raiseException(14833, 'Fail SetFeatures 0xAA')

      objPwrCtrl.powerCycle(5000, 12000, 10, 30)

   # ---------------------------------------------------------------- Mtest1 ---
   def __mtest1(self):
      ScrCmds.statMsg("------------------------------------------- Mtest1 ---")
      random.seed()
      # fill buffer with byte wise increment (0x00, 0x01, 0x02, ..., 0xFF)
      res = ICmd.FillBuffInc(WBF, 0x00, 512 * 256, 0x00)
      if res['LLRET'] != OK:
         ScrCmds.statMsg("Result: %s" % res)
         ScrCmds.raiseException(14833, 'Fill Buffer Increment Failed!')

      loop = 5000
      if testSwitch.virtualRun: loop = 2
      t1_R_idx = 0
      t1_blkSize = 1
      t2_RW_idx = 1000
      t3_blkSize = 4
      t4_loop_ctr = 1
      t4_startLBA = random.randint(self.startTestLba, self.endTestLba - 63)
      t5_loop_ctr = 1
      t5_startLBA = random.randint(self.startTestLba, self.endTestLba - 3)

      compare_flg = True
      ctr = 1
      while True:
         try:
            # thread 1
            CHelper().sequentialReadCmpDMAExt(t1_R_idx, t1_R_idx + (t1_blkSize - 1), t1_blkSize, t1_blkSize, compare_flg, 14833)
            t1_R_idx += t1_blkSize
            if (ctr % 10) == 0:
               t1_blkSize += 1
               if t1_blkSize > 128: t1_blkSize = 1

            # thread 2
            self.__mtest1_t2(compare_flg, t2_RW_idx)
            t2_RW_idx += 1
            if t2_RW_idx > 5000: t2_RW_idx = 1000

            # thread 3
            self.__mtest1_t3(compare_flg, t3_blkSize)
            if (ctr % 15) == 0:
               t3_blkSize += 4
               if t3_blkSize > 128: t3_blkSize = 4

            # thread 4
            self.__mtest1_t4(compare_flg, t4_startLBA)
            t4_loop_ctr += 1
            if t4_loop_ctr > 20:
               t4_loop_ctr = 1
               t4_startLBA = random.randint(self.startTestLba, self.endTestLba - 63)

            # thread 5
            self.__mtest1_t5(compare_flg, t5_startLBA)
            t5_loop_ctr += 1
            if t5_loop_ctr > 3:
               t5_loop_ctr = 1
               t5_startLBA = random.randint(self.startTestLba, self.endTestLba - 3)

            # loop counting
            ctr += 1
            if ctr > loop: break
            if ctr % 20 == 0: compare_flg = not compare_flg
         except:
            ScrCmds.statMsg("Loop Counter = %s" % ctr)
            raise

   def __mtest1_t2(self, compare_flg = False, RW_idx = 1000):
      random.seed()
      if random.randint(1, 100) <= 40:
         # 40% probability for writing process
         CHelper().sequentialWriteDMAExt(RW_idx, RW_idx, 1, 1, 14833)
      else:
         # 60% probability for reading process
         CHelper().sequentialReadCmpDMAExt(RW_idx, RW_idx, 1, 1, compare_flg, 14833)

   def __mtest1_t3(self, compare_flg = False, blkSize = 1):
      random.seed()
      idxLBA = random.randint(self.startTestLba, self.endTestLba - blkSize)
      CHelper().sequentialReadCmpDMAExt(idxLBA, idxLBA + (blkSize - 1), blkSize, blkSize, compare_flg, 14833)

   def __mtest1_t4(self, compare_flg = False, startLBA = 0):
      random.seed()
      if random.randint(1, 100) <= 50:
         # 50% probability for writing process
         CHelper().sequentialWriteDMAExt(startLBA, startLBA + 63, 64, 64, 14833)
      else:
         # 50% probability for reading process
         CHelper().sequentialReadCmpDMAExt(startLBA, startLBA + 63, 64, 64, compare_flg, 14833)

   def __mtest1_t5(self, compare_flg = False, startLBA = 0):
      random.seed()
      if random.randint(1, 100) <= 50:
         # 50% probability for writing process
         CHelper().sequentialWriteDMAExt(startLBA, startLBA + 3, 4, 4, 14833)
      else:
         # 50% probability for reading process
         CHelper().sequentialReadCmpDMAExt(startLBA, startLBA + 3, 4, 4, compare_flg, 14833)

   # --------------------------------------------- Creshndo (Wrt/Rd Compare) ---
   def __creshndo(self):
      ScrCmds.statMsg("------------------------ Creshndo (Wrt/Rd Compare) ---")
      # fill buffer with byte wise increment (0x00, 0x01, 0x02, ..., 0xFF)
      res = ICmd.FillBuffInc(WBF, 0x00, 512 * 256, 0x00)
      if res['LLRET'] != OK:
         ScrCmds.statMsg("Result: %s" % res)
         ScrCmds.raiseException(14833, 'Fill Buffer Increment Failed!')

      loop = 10000
      if testSwitch.virtualRun: loop = 2
      ScrCmds.statMsg("Running Full Stroke Write with Contracting Seek.")
      self.__creshndo_full_sw_cs(loop)
      ScrCmds.statMsg("Running Full Stroke Read with Contracting Seek.")
      self.__creshndo_full_sr_cs(loop)
      ScrCmds.statMsg("Running 1/3 Stroke Write.")
      self.__creshndo_1_3rd_sw(loop)
      ScrCmds.statMsg("Running 1/3 Stroke Read.")
      self.__creshndo_1_3rd_sr(loop)
      ScrCmds.statMsg("Running 1/4 Stroke Write.")
      self.__creshndo_1_4th_sw(loop)
      ScrCmds.statMsg("Running 1/4 Stroke Read.")
      self.__creshndo_1_4th_sr(loop)

   def __creshndo_full_sw_cs(self, loop = 10000):
      idIdx = self.maxLBA - 63
      odIdx = 0
      for ctr in xrange(loop):
         CHelper().sequentialWriteDMAExt(idIdx, idIdx + 62, 63, 63, 14833)
         idIdx -= 63
         CHelper().sequentialWriteDMAExt(odIdx, odIdx + 62, 63, 63, 14833)
         odIdx += 63

   def __creshndo_full_sr_cs(self, loop = 10000):
      idIdx = self.maxLBA - 63
      odIdx = 0
      for ctr in xrange(loop):
         CHelper().sequentialReadCmpDMAExt(idIdx, idIdx + 62, 63, 63, True, 14833)
         idIdx -= 63
         CHelper().sequentialReadCmpDMAExt(odIdx, odIdx + 62, 63, 63, True, 14833)
         odIdx += 63

   def __creshndo_1_3rd_sw(self, loop = 10000):
      idIdx = (self.maxLBA / 3) - 1
      odIdx = 0
      for ctr in xrange(loop):
         CHelper().sequentialWriteDMAExt(idIdx, idIdx, 1, 1, 14833)
         idIdx += 1
         CHelper().sequentialWriteDMAExt(odIdx, odIdx, 1, 1, 14833)
         odIdx += 1

   def __creshndo_1_3rd_sr(self, loop = 10000):
      idIdx = (self.maxLBA / 3) - 1
      odIdx = 0
      for ctr in xrange(loop):
         CHelper().sequentialReadCmpDMAExt(idIdx, idIdx, 1, 1, True, 14833)
         idIdx += 1
         CHelper().sequentialReadCmpDMAExt(odIdx, odIdx, 1, 1, True, 14833)
         odIdx += 1

   def __creshndo_1_4th_sw(self, loop = 10000):
      idIdx = (self.maxLBA / 4) - 1
      odIdx = 0
      for ctr in xrange(loop):
         CHelper().sequentialWriteDMAExt(idIdx, idIdx, 1, 1, 14833)
         idIdx += 1
         CHelper().sequentialWriteDMAExt(odIdx, odIdx, 1, 1, 14833)
         odIdx += 1

   def __creshndo_1_4th_sr(self, loop = 10000):
      idIdx = (self.maxLBA / 4) - 1
      odIdx = 0
      for ctr in xrange(loop):
         CHelper().sequentialReadCmpDMAExt(idIdx, idIdx, 1, 1, True, 14833)
         idIdx += 1
         CHelper().sequentialReadCmpDMAExt(odIdx, odIdx, 1, 1, True, 14833)
         odIdx += 1

   # --------------------------------------------- Inchworm (Wrt/Rd Compare) ---
   def __inchworm(self):
      ScrCmds.statMsg("------------------------ Inchworm (Wrt/Rd Compare) ---")
      random.seed()
      # fill buffer with byte wise increment (0x00, 0x01, 0x02, ..., 0xFF)
      res = ICmd.FillBuffInc(WBF, 0x00, 512 * 256, 0x00)
      if res['LLRET'] != OK:
         ScrCmds.statMsg("Result: %s" % res)
         ScrCmds.raiseException(14833, 'Fill Buffer Increment Failed!')

      loop = 25000
      if testSwitch.virtualRun: loop = 2
      idxLba1 = 5000000
      idxLba2 = 5000000
      idxLba3 = 5000000
      idxLba4 = 5000000
      idxLba5 = 5000000
      for ctr in xrange(loop):
         randNum = random.randint(1, 100)
         if randNum <= 20:
            self.__inchworm_t1(idxLba1)
            idxLba1 += 8
         elif randNum <= 40:
            self.__inchworm_t2(idxLba2)
            idxLba2 += 8
         elif randNum <= 60:
            self.__inchworm_t3(idxLba3)
            idxLba3 += 8
         elif randNum <= 80:
            self.__inchworm_t4(idxLba4)
            idxLba4 += 8
         else:
            for ctr_t5 in xrange(3):
               self.__inchworm_t5(idxLba5)
               idxLba5 += 4

         randDly = random.randint(10, 96)
         delay = randDly * 0.003              # 1 milliseconds
         time.sleep(delay)

   def __inchworm_t1(self, idxLba = 0):
      CHelper().sequentialWriteDMAExt(idxLba, idxLba + 15, 16, 16, 14833)

   def __inchworm_t2(self, idxLba = 0):
      CHelper().sequentialWriteDMAExt(idxLba, idxLba + 7, 8, 8, 14833)

   def __inchworm_t3(self, idxLba = 0):
      CHelper().sequentialReadCmpDMAExt(idxLba, idxLba + 15, 16, 16, True, 14833)

   def __inchworm_t4(self, idxLba = 0):
      CHelper().sequentialReadCmpDMAExt(idxLba, idxLba + 7, 8, 8, True, 14833)

   def __inchworm_t5(self, idxLba = 0):
      CHelper().sequentialReadCmpDMAExt(idxLba, idxLba + 7, 8, 8, True, 14833)

###########################################################################################################
class CMayhem_Test(CState):
   """
   Mayhem File Copy Compare Simulation Test
    - Sequential Write with CNQ
    - Read at Region1, Write at Region2
    - Read at Region1, Read at Region2
   """
   def __init__(self, dut, params={}):
      self.params = params
      self.dut = dut
      depList = []
      CState.__init__(self, dut, depList)

   def run(self):
      objPwrCtrl.powerCycle(5000, 12000, 10, 30)
      self.startTestLba = 0
      self.maxTestLba = 50000000
      self.endTestLba = (self.startTestLba + self.maxTestLba) - 1
      self.region1 = 100000
      self.region2 = self.endTestLba - 665248

      rPtrn = CUtility.getRandomPattern(64)
      res = ICmd.FillBuffByte(WBF, rPtrn, 0, 512 * 256)
      if res['LLRET'] != OK:
         ScrCmds.statMsg("Result: %s" % res)
         ScrCmds.raiseException(14834, 'Fill Buff Byte fail')

      self.__write_ncq()
      self.__r1read_r2write()
      self.__r1read_r2read()
      objPwrCtrl.powerCycle(5000, 12000, 10, 30)

   # --------------------------------------------- Sequential Write with CNQ ---
   def __write_ncq(self):
      ScrCmds.statMsg("------------------------ Sequential Write with CNQ ---")
      ScrCmds.statMsg("Executing CPC NCQSequentialWriteDMA command.")
      CHelper().NCQSequentialWriteDMA(self.startTestLba, self.endTestLba, 256, 256, 14834)

   # ------------------------------------- Read at Region1, Write at Region2 ---
   def __r1read_r2write(self):
      ScrCmds.statMsg("---------------- Read at Region1, Write at Region2 ---")
      random.seed(5)
      loop = 1024
      if testSwitch.virtualRun: loop = 2

      idx_r1 = self.region1
      idx_r2 = self.region2
      for ctr in xrange(loop):
         # file
         rFile = random.randint(1, 7)
         for idxFile in xrange(rFile):
            CHelper().sequentialReadCmpDMAExt(idx_r1, idx_r1 + 63, 32, 32, True, 14834)
            idx_r1 += 64
            CHelper().sequentialWriteDMAExt(idx_r2, idx_r2 + 63, 32, 32, 14834)
            idx_r2 += 64
         # fragment
         rFragment = random.randint(1, 32)
         CHelper().sequentialReadCmpDMAExt(idx_r1, idx_r1 + (rFragment - 1), rFragment, rFragment, False, 14834)
         idx_r1 += 32
         CHelper().sequentialWriteDMAExt(idx_r2, idx_r2 + (rFragment - 1), rFragment, rFragment, 14834)
         idx_r2 += 32

   # -------------------------------------- Read at Region1, Read at Region2 ---
   def __r1read_r2read(self):
      ScrCmds.statMsg("----------------- Read at Region1, Read at Region2 ---")
      random.seed(5)
      loop = 1024
      if testSwitch.virtualRun: loop = 2

      idx_r1 = self.region1
      idx_r2 = self.region2
      for ctr in xrange(loop):
         # file
         rFile = random.randint(1, 7)
         for idxFile in xrange(rFile):
            CHelper().sequentialReadCmpDMAExt(idx_r1, idx_r1 + 63, 32, 32, True, 14834)
            idx_r1 += 64
            CHelper().sequentialReadCmpDMAExt(idx_r2, idx_r2 + 63, 32, 32, True, 14834)
            idx_r2 += 64
         # fragment
         rFragment = random.randint(1, 32)
         CHelper().sequentialReadCmpDMAExt(idx_r1, idx_r1 + (rFragment - 1), rFragment, rFragment, True, 14834)
         idx_r1 += 32
         CHelper().sequentialReadCmpDMAExt(idx_r2, idx_r2 + (rFragment - 1), rFragment, rFragment, True, 14834)
         idx_r2 += 32

###########################################################################################################
class CCache_Sim_Test(CState):
   """
   Fitness Cache Simulation Test
    - Cache 1 (Read Cache Test)
    - Cache 2 (Write Cache Test)
      Ability to change from large block to small block count
    - Cache 3 (Read Cache Test)
      Ability to change from large block to small block count
   """
   def __init__(self, dut, params={}):
      self.params = params
      self.dut = dut
      depList = []
      CState.__init__(self, dut, depList)
      self.helper = CHelper() # optimize CHelper init

   def run(self):
      objPwrCtrl.powerCycle(5000, 12000, 10, 30)
      ICmd.MakeAlternateBuffer(BWR, 1024)
      ICmd.ClearBinBuff(BWR)
      try:
         oIdentifyDevice = CIdentifyDevice()
         self.maxLBA = oIdentifyDevice.getMaxLBA()
         self.startTestLba = int(self.maxLBA * 0.8)      # 80% Max LBA
         ScrCmds.statMsg("Start Test LBA               : %s" % self.startTestLba)
         self.endTestLba = self.maxLBA - 1
         ScrCmds.statMsg("End Test LBA                 : %s" % self.endTestLba)
         
         if objRimType.IOInitRiser():
            # Need to reset CM timeout since direct call will be used in SI   
            ICmd.SetRFECmdTimeout(0)

         self.__setMode()
         self.__setDataPattern()
         self.__cache1()
         self.__cache2()
         self.__cache3()
      finally:
         self.__resetMode()
         ICmd.RestorePrimaryBuffer(BWR)

      objPwrCtrl.powerCycle(5000, 12000, 10, 30)

   def __setMode(self):
      ScrCmds.statMsg("------------------------------------ Set Test Mode ---")
      # Set APM 0xFE
      res = enable_APM(0xFE, exc = 0)
      ScrCmds.statMsg("Set APM 0xFE result: %s" % res)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14835, 'Fail SetFeatures 0x05, 0xFE')

      # Set UDMA speed
      res = Set_UDMASpeed(0x46, exc = 0)
      ScrCmds.statMsg("Set UDMA Mode = 6; result: %s" % res)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14835, 'Fail SetFeatures 0x03, 0x46')

      # Enable Read Look Ahead
      res = enable_ReadLookAhead(exc = 0)
      ScrCmds.statMsg("Enable Read Look Ahead result: %s" % res)
      if res['LLRET'] != 0:
         ScrCmds.raiseException(14835, 'Fail SetFeatures 0xAA')

      # Enable Write Cache
      res = enable_WriteCache(exc = 0)
      ScrCmds.statMsg("Enable Write Cache result: %s" % res)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14835, 'Fail SetFeatures 0x02')

   def __resetMode(self):
      ScrCmds.statMsg("---------------------------------- Reset Test Mode ---")
      # Disable APM
      res = disable_APM(exc = 0)
      ScrCmds.statMsg("Disable APM result: %s" % res)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14833, 'Fail SetFeatures 0x85')

   def __setDataPattern(self):
      ScrCmds.statMsg("--------------------------------- Set Data Pattern ---")
      # fill buffer with byte wise increment (0x00, 0x01, 0x02, ..., 0xFF)
      ScrCmds.statMsg("Fill buffer with byte wise increment (0x00, 0x01, 0x02, ..., 0xFF).")
      res = ICmd.FillBuffInc(WBF, 0x00, 512 * 256, 0x00)
      ScrCmds.statMsg("Result: %s" % res)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14835, 'Fill Buffer Increment Failed!')

   def __cache1(self):
      ScrCmds.statMsg("------------------------ Cache 1 (Read Cache Test) ---")
      random.seed()
      loop = 3000
      if testSwitch.virtualRun: loop = 2
      idxLBA = self.startTestLba

      for ctr in xrange(loop):
         self.helper.sequentialReadDMAExt(idxLBA, idxLBA, 1, 1, 14835)
         rNum = random.randint(1, 1023)
         idxLBA += 4
         self.helper.sequentialReadDMAExt(idxLBA, idxLBA + (rNum - 1), rNum, rNum, 14835)
         idxLBA += 1

   def __cache2(self):
      ScrCmds.statMsg("----------------------- Cache 2 (Write Cache Test) ---")
      random.seed()
      loop = 1500
      if testSwitch.virtualRun: loop = 2
      for ctr in xrange(loop):
         rLoc = random.randint(self.startTestLba + 1, self.endTestLba - 1023)
         rBlk = random.randint(62, 1023)
         self.helper.sequentialWriteDMAExt(rLoc, rLoc + (rBlk - 1), rBlk, rBlk, 14835)
         rLoc -= 1
         self.helper.sequentialWriteDMAExt(rLoc, rLoc, 1, 1, 14835)
         self.helper.sequentialReadCmpDMAExt(rLoc, rLoc + 62, 63, 63, True, 14835)

   def __cache3(self):
      ScrCmds.statMsg("------------------------ Cache 3 (Read Cache Test) ---")
      random.seed()
      loop = 1500
      if testSwitch.virtualRun: loop = 2
      for ctr in xrange(loop):
         rLoc = random.randint(self.startTestLba, self.endTestLba - 1023)
         rBlk = random.randint(127, 1023)
         self.helper.sequentialReadDMAExt(rLoc, rLoc + (rBlk - 1), rBlk, rBlk, 14835)
         rBlk = random.randint(1, 8)
         self.helper.sequentialReadDMAExt(rLoc, rLoc + (rBlk - 1), rBlk, rBlk, 14835)
         

###########################################################################################################
class CFour_Stream_Test(CState):
   """
   Four Stream Test. It's part of SIE FITS CE Test.
   """
   def __init__(self, dut, params={}):
      self.params = params
      self.dut = dut
      depList = []
      CState.__init__(self, dut, depList)

   def run(self):
      objPwrCtrl.powerCycle(5000, 12000, 10, 30)
      ICmd.MakeAlternateBuffer(BWR, 512)
      ICmd.ClearBinBuff(BWR)

      try:
         oIdentifyDevice = CIdentifyDevice()
         maxLBA = oIdentifyDevice.getMaxLBA()
         self.startLBA = 0
         self.endLBA = maxLBA - 1
         self.midLBA = self.endLBA / 2
         ScrCmds.statMsg("Start LBA                    : %s blocks" % self.startLBA)
         ScrCmds.statMsg("Middle LBA                   : %s blocks" % self.midLBA)
         ScrCmds.statMsg("End LBA                      : %s blocks" % self.endLBA)

         transferBlocks = [1, 2, 4, 8, 16, 32, 64, 128, 256 ,512]
         ScrCmds.statMsg("--- UDMA 2 (UDMA33) ----------------------------------")
         Set_UDMASpeed(0x42, exc = 1) # UDMA 2 (UDMA33)
         self.__collectCCT(transferBlocks, True)
         ScrCmds.statMsg("--- UDMA 4 (UDMA66) ----------------------------------")
         Set_UDMASpeed(0x44, exc = 1) # UDMA 4 (UDMA66)
         self.__collectCCT(transferBlocks, True)
      finally:
         ICmd.RestorePrimaryBuffer(BWR)

      objPwrCtrl.powerCycle(5000, 12000, 10, 30)

   def __collectCCT(self, transferBlocks = [], printResult = True):
      """
      Collect Command Completion Time (CCT)

      @type transferBlocks:  array of integers
      @param transferBlocks: list of transfer blocks size to be used
      @type printResult:  boolean
      @param printResult: if True, print CCT on the log file; otherwise don't
                          print
      """

      ScrCmds.statMsg("    Blocks    : txRate(MB/s) :    CCT(ms)   ")
      for transferBlock in transferBlocks:
         res = ICmd.ReadDMAExtTransRate(self.endLBA - (transferBlock - 1), transferBlock, transferBlock)
         if res['LLRET'] != OK: ScrCmds.raiseException(14840, "Read DMA Ext Transfer Rate fail!")
         txRate1 = float(res['TXRATE'])
         if txRate1 == 0.0: txRate1 = 0.9    # avoiding divide by zero

         res = ICmd.WriteDMAExtTransRate(self.startLBA, transferBlock, transferBlock)
         if res['LLRET'] != OK: ScrCmds.raiseException(14840, "Write DMA Ext Transfer Rate fail!")
         txRate2 = float(res['TXRATE'])
         if txRate2 == 0.0: txRate2 = 0.9    # avoiding divide by zero

         res = ICmd.WriteDMAExtTransRate(self.midLBA, transferBlock, transferBlock)
         if res['LLRET'] != OK: ScrCmds.raiseException(14840, "Write DMA Ext Transfer Rate fail!")
         txRate3 = float(res['TXRATE'])
         if txRate3 == 0.0: txRate3 = 0.9    # avoiding divide by zero

         res = ICmd.ReadDMAExtTransRate(self.startLBA, transferBlock, transferBlock)

         if res['LLRET'] != OK: ScrCmds.raiseException(14840, "Read DMA Ext Transfer Rate fail!")
         txRate4 = float(res['TXRATE'])
         if txRate4 == 0.0: txRate4 = 0.9    # avoiding divide by zero

         # CCT in s/MB
         cct_s_MB = (1/txRate1) + (1/txRate2) + (1/txRate3) + (1/txRate4)
         # transfer rate in MB/s
         txRate = 1 / cct_s_MB
         # CCT in ms/B
         cct_ms_B = cct_s_MB / 1048.576
         # CCT in ms/total transfer block in Byte
         # 2048 = 512 Bytes/block * 4 commands(2 read and 2 write)
         cct  = cct_ms_B * (transferBlock * 2048)
         if printResult:
            ScrCmds.statMsg(" %12d : %12.3f : %12.3f" % (transferBlock, txRate, cct))

###########################################################################################################
class CFjsHddDiag(CState):
   """
      Fujitsu HDD Diagnostic Test. This test contains:
       - Single Sector Write with 10 Seconds Delay
       - Sequential Write/Read with 30 Seconds Standby
       - Random Write/Read
       - Sequential Write/Read with 30 Seconds Sleep
       - Single Side Track Erase Test
       - Double Side Track Erase Test
   """
   def __init__(self, dut, params={}):
      self.params = params
      self.dut = dut
      depList = []
      CState.__init__(self, dut, depList)

   def run(self):
      objPwrCtrl.powerCycle(5000, 12000, 10, 30)
      oIdentifyDevice = CIdentifyDevice()
      self.maxLBA = oIdentifyDevice.getMaxLBA()

      self.__writeSingleSector_10SecDelay()
      self.__sequentialWriteRead_30SecStandby()
      self.__randomWriteRead()
      self.__sequentialWriteRead_30SecSleep()
      self.__randomWriteRead()
      self.__eraseSingleSideTrack()
      self.__sequentialWriteRead_30SecStandby()
      self.__randomWriteRead()
      self.__sequentialWriteRead_30SecSleep()
      self.__randomWriteRead()
      self.__eraseDoubleSideTrack()
      objPwrCtrl.powerCycle(5000, 12000, 10, 30)

   def __writeSingleSector_10SecDelay(self):
      ScrCmds.statMsg("--- Single Sector Write with 10 Seconds Delay ---------")
      ptrn = "AAAA5555AAAA101000000005"
      ScrCmds.statMsg("Write Pattern = %s" % ptrn)
      ICmd.FillBuffByte(WBF, ptrn, 0, 512)
      ScrCmds.statMsg("Writing 64 Blocks")
      blockNum = 64
      if testSwitch.virtualRun:
         blockNum = 2
      for blkOff in range(0, blockNum):
         CHelper().sequentialWriteDMAExt(blkOff, blkOff + 1, 1, 1, 14843)
         time.sleep(10)
      ScrCmds.statMsg("Writing at LBA 0")
      CHelper().sequentialWriteDMAExt(0, 1, 1, 1, 14843)

   def __sequentialWriteRead_30SecStandby(self):
      ScrCmds.statMsg("--- Sequential Write/Read with 30 Seconds Standby -----")
      ScrCmds.statMsg("Reading LBA 0")
      CHelper().sequentialReadDMAExt(0, 1, 1, 1, 14843)

      random.seed()
      stepLBA     = 256
      sectorCount = stepLBA
      rangeLBA    = 64000

      ICmd.FillBuffRandom(WBF, 0, 512 * sectorCount, exc = 1)
      ttlTestTime = 15 * 60            # 15 minutes
      if testSwitch.virtualRun:
         ttlTestTime = 0               # 0 second
      startTime   = time.time()
      while True:
         startLBA    = random.randint(0, self.maxLBA - rangeLBA)
         endLBA      = startLBA + rangeLBA
         ICmd.StandbyImmed()
         time.sleep(30)
         CHelper().sequentialWriteDMAExt(startLBA, endLBA, stepLBA, sectorCount, 14843)
         ICmd.StandbyImmed()
         time.sleep(30)
         CHelper().sequentialReadDMAExt(startLBA, endLBA, stepLBA, sectorCount, 14843)
         endTime = time.time()
         if (endTime > (startTime + ttlTestTime)): break

   def __randomWriteRead(self):
      ScrCmds.statMsg("--- Random Write/Read ---------------------------------")
      ScrCmds.statMsg("Reading LBA 0")
      CHelper().sequentialReadDMAExt(0, 1, 1, 1, 14843)

      random.seed()
      stepLBA     = 256
      sectorCount = stepLBA
      ttlTestTime = 10 * 60            # 10 minutes
      if testSwitch.virtualRun:
         ttlTestTime = 0               # 0 seconds
      startTime   = time.time()
      while True:
         rangeLBA    = random.randint(1, 999)
         startLBA    = random.randint(0, self.maxLBA - rangeLBA)
         endLBA      = startLBA + rangeLBA
         if random.randint(0, 1) == 0:
            CHelper().sequentialWriteDMAExt(startLBA, endLBA, stepLBA, sectorCount, 14843)
         else:
            CHelper().sequentialReadDMAExt(startLBA, endLBA, stepLBA, sectorCount, 14843)
         endTime = time.time()
         if (endTime > (startTime + ttlTestTime)): break

   def __sequentialWriteRead_30SecSleep(self):
      ScrCmds.statMsg("--- Sequential Write/Read with 30 Seconds Sleep -------")
      ScrCmds.statMsg("Reading LBA 0")
      CHelper().sequentialReadDMAExt(0, 1, 1, 1, 14843)

      random.seed()
      stepLBA     = 256
      sectorCount = stepLBA
      rangeLBA    = 64000

      ICmd.FillBuffRandom(WBF, 0, 512 * sectorCount, exc = 1)
      ttlTestTime = 15 * 60            # 15 minutes
      if testSwitch.virtualRun:
         ttlTestTime = 0               # 0 second
      startTime   = time.time()
      while True:
         startLBA    = random.randint(0, self.maxLBA - rangeLBA)
         endLBA      = startLBA + rangeLBA
         ICmd.Sleep()
         time.sleep(30)
         objPwrCtrl.powerCycle(5000, 12000, 10, 30)
         CHelper().sequentialWriteDMAExt(startLBA, endLBA, stepLBA, sectorCount, 14843)

         ICmd.Sleep()
         time.sleep(30)
         objPwrCtrl.powerCycle(5000, 12000, 10, 30)
         CHelper().sequentialReadDMAExt(startLBA, endLBA, stepLBA, sectorCount, 14843)

         endTime = time.time()
         if (endTime > (startTime + ttlTestTime)): break

   def __eraseSingleSideTrack(self):
      ScrCmds.statMsg("--- Single Side Track Erase Test ---------------------")

      ScrCmds.statMsg("Reading LBA 0")
      CHelper().sequentialReadDMAExt(0, 1, 1, 1, 14843)

      # Disable Read Look Ahead
      res = disable_ReadLookAhead(exc = 0)
      ScrCmds.statMsg("Disable Read Look Ahead result: %s" % res)
      if res['LLRET'] != 0:
         ScrCmds.raiseException(14843, 'Fail SetFeatures Disable Read Look Ahead (0x55)')

      # Disable Write Cache
      res = disable_WriteCache(exc = 0)
      ScrCmds.statMsg("Disable Write Cache result: %s" % res)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14843, 'Fail SetFeatures Disable Write Cache (0x82)')

      stepLBA     = 256
      sectorCount = stepLBA

      zDataIDLoc = 'ID'
      zDataIDSecTrack = 520
      zDataIDSttBlk = 0

      zDataMDLoc = 'MD'
      zDataMDSecTrack = 660
      zDataMDSttBlk = self.maxLBA / 2

      zDataODLoc = 'OD'
      zDataODSecTrack = 800
      zDataODSttBlk = self.maxLBA - ((322 * zDataODSecTrack) + 1)

      ScrCmds.statMsg("Zone ID Location     : %s" % zDataIDLoc)
      ScrCmds.statMsg("Zone ID Sector/Track : %s" % zDataIDSecTrack)
      ScrCmds.statMsg("Zone ID Start Block  : %s" % zDataIDSttBlk)
      ScrCmds.statMsg("Zone MD Location     : %s" % zDataMDLoc)
      ScrCmds.statMsg("Zone MD Sector/Track : %s" % zDataMDSecTrack)
      ScrCmds.statMsg("Zone MD Start Block  : %s" % zDataMDSttBlk)
      ScrCmds.statMsg("Zone OD Location     : %s" % zDataODLoc)
      ScrCmds.statMsg("Zone OD Sector/Track : %s" % zDataODSecTrack)
      ScrCmds.statMsg("Zone OD Start Block  : %s" % zDataODSttBlk)

      rPtrn = "0000"
      ScrCmds.statMsg("Write Pattern = %s" % rPtrn)
      ICmd.FillBuffByte(WBF, rPtrn, 0, 512 * sectorCount)

      zDataSetSeq = [
         [zDataODLoc, zDataODSttBlk, 322 * zDataODSecTrack],
         [zDataMDLoc, zDataMDSttBlk, 322 * zDataMDSecTrack],
         [zDataIDLoc, zDataIDSttBlk, 322 * zDataIDSecTrack],
      ]

      for zDataSeq in zDataSetSeq:
         ScrCmds.statMsg("Writing 322 tracks at %s" % zDataSeq[0])
         CHelper().sequentialWriteDMAExt(zDataSeq[1], zDataSeq[1] + zDataSeq[2], stepLBA, sectorCount, 14843)

      for zDataSeq in zDataSetSeq:
         ScrCmds.statMsg("Reading 322 tracks at %s" % zDataSeq[0])
         CHelper().sequentialReadDMAExt(zDataSeq[1], zDataSeq[1] + zDataSeq[2], stepLBA, sectorCount, 14843)

      rPtrn = "0000FFFF0000FFFF0000FFFF"
      ScrCmds.statMsg("Write Pattern = %s" % rPtrn)
      ICmd.FillBuffByte(WBF, rPtrn, 0, 512 * sectorCount)

      ScrCmds.statMsg("Writing for 10000 loop.")
      startLBAOD = zDataODSttBlk + 128000
      startLBAMD = zDataMDSttBlk + 105600
      startLBAID = zDataIDSttBlk +  83200
      zDataSetSt = [
         [startLBAOD, startLBAOD + zDataODSecTrack, zDataODLoc],
         [startLBAMD, startLBAMD + zDataMDSecTrack, zDataMDLoc],
         [startLBAID, startLBAID + zDataIDSecTrack, zDataIDLoc],
      ]
      for ctr in range(0, 10000):
         for zDataSt in zDataSetSt:
            CHelper().sequentialWriteDMAExt(zDataSt[0], zDataSt[1], stepLBA, sectorCount, 14843)

      for zDataSeq in zDataSetSeq:
         ScrCmds.statMsg("Reading 322 tracks at %s" % zDataSeq[0])
         CHelper().sequentialReadDMAExt(zDataSeq[1], zDataSeq[1] + zDataSeq[2], stepLBA, sectorCount, 14843)

      for zDataSeq in zDataSetSeq:
         ScrCmds.statMsg("Writing 322 tracks at %s" % zDataSeq[0])
         CHelper().sequentialWriteDMAExt(zDataSeq[1], zDataSeq[1] + zDataSeq[2], stepLBA, sectorCount, 14843)

      for zDataSeq in zDataSetSeq:
         ScrCmds.statMsg("Reading 322 tracks at %s" % zDataSeq[0])
         CHelper().sequentialReadDMAExt(zDataSeq[1], zDataSeq[1] + zDataSeq[2], stepLBA, sectorCount, 14843)

      # Enable Write Cache
      res = enable_WriteCache(exc = 0)
      ScrCmds.statMsg("Enable Write Cache result: %s" % res)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14843, 'Fail SetFeatures 0x02')

      # Enable Read Look Ahead
      res = enable_ReadLookAhead(exc = 0)
      ScrCmds.statMsg("Enable Read Look Ahead result: %s" % res)
      if res['LLRET'] != 0:
         ScrCmds.raiseException(14843, 'Fail SetFeatures 0xAA')

   def __eraseDoubleSideTrack(self):
      ScrCmds.statMsg("--- Double Side Track Erase Test ---------------------")

      ScrCmds.statMsg("Reading LBA 0")
      CHelper().sequentialReadDMAExt(0, 1, 1, 1, 14843)

      # Disable Read Look Ahead
      res = disable_ReadLookAhead(exc = 0)
      ScrCmds.statMsg("Disable Read Look Ahead result: %s" % res)
      if res['LLRET'] != 0:
         ScrCmds.raiseException(14843, 'Fail SetFeatures Disable Read Look Ahead (0x55)')

      # Disable Write Cache
      res = disable_WriteCache(exc = 0)
      ScrCmds.statMsg("Disable Write Cache result: %s" % res)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14843, 'Fail SetFeatures Disable Write Cache (0x82)')

      stepLBA     = 256
      sectorCount = stepLBA

      zDataIDLoc = 'ID'
      zDataIDSecTrack = 520
      zDataIDSttBlk = 0

      zDataMDLoc = 'MD'
      zDataMDSecTrack = 660
      zDataMDSttBlk = self.maxLBA / 2

      zDataODLoc = 'OD'
      zDataODSecTrack = 800
      zDataODSttBlk = self.maxLBA - ((322 * zDataODSecTrack) + 1)

      ScrCmds.statMsg("Zone ID Location     : %s" % zDataIDLoc)
      ScrCmds.statMsg("Zone ID Sector/Track : %s" % zDataIDSecTrack)
      ScrCmds.statMsg("Zone ID Start Block  : %s" % zDataIDSttBlk)
      ScrCmds.statMsg("Zone MD Location     : %s" % zDataMDLoc)
      ScrCmds.statMsg("Zone MD Sector/Track : %s" % zDataMDSecTrack)
      ScrCmds.statMsg("Zone MD Start Block  : %s" % zDataMDSttBlk)
      ScrCmds.statMsg("Zone OD Location     : %s" % zDataODLoc)
      ScrCmds.statMsg("Zone OD Sector/Track : %s" % zDataODSecTrack)
      ScrCmds.statMsg("Zone OD Start Block  : %s" % zDataODSttBlk)

      rPtrn = "0000"
      ScrCmds.statMsg("Write Pattern = %s" % rPtrn)
      ICmd.FillBuffByte(WBF, rPtrn, 0, 512 * sectorCount)

      zDataSetSeq = [
         [zDataODLoc, zDataODSttBlk, 322 * zDataODSecTrack],
         [zDataMDLoc, zDataMDSttBlk, 322 * zDataMDSecTrack],
         [zDataIDLoc, zDataIDSttBlk, 322 * zDataIDSecTrack],
      ]

      for zDataSeq in zDataSetSeq:
         ScrCmds.statMsg("Writing 322 tracks at %s" % zDataSeq[0])
         CHelper().sequentialWriteDMAExt(zDataSeq[1], zDataSeq[1] + zDataSeq[2], stepLBA, sectorCount, 14843)

      for zDataSeq in zDataSetSeq:
         ScrCmds.statMsg("Reading 322 tracks at %s" % zDataSeq[0])
         CHelper().sequentialReadDMAExt(zDataSeq[1], zDataSeq[1] + zDataSeq[2], stepLBA, sectorCount, 14843)

      rPtrn = "0000FFFF0000FFFF0000FFFF"
      ScrCmds.statMsg("Write Pattern = %s" % rPtrn)
      ICmd.FillBuffByte(WBF, rPtrn, 0, 512 * sectorCount)

      ScrCmds.statMsg("Writing for 10000 loop.")
      startLBAOD1 = zDataODSttBlk + 128000
      startLBAOD2 = zDataODSttBlk + 129600
      startLBAMD1 = zDataMDSttBlk + 105600
      startLBAMD2 = zDataMDSttBlk + 106920
      startLBAID1 = zDataIDSttBlk +  83200
      startLBAID2 = zDataIDSttBlk +  84240
      zDataSetSt = [
         [startLBAOD1, startLBAOD1 + zDataODSecTrack, zDataODLoc],
         [startLBAOD2, startLBAOD2 + zDataODSecTrack, zDataODLoc],
         [startLBAMD1, startLBAMD1 + zDataMDSecTrack, zDataMDLoc],
         [startLBAMD2, startLBAMD2 + zDataMDSecTrack, zDataMDLoc],
         [startLBAID1, startLBAID1 + zDataIDSecTrack, zDataIDLoc],
         [startLBAID2, startLBAID2 + zDataIDSecTrack, zDataIDLoc],
      ]
      loopNum = 10000
      if testSwitch.virtualRun:
         loopNum = 2
      for ctr in range(0, loopNum):
         for zDataSt in zDataSetSt:
            CHelper().sequentialWriteDMAExt(zDataSt[0], zDataSt[1], stepLBA, sectorCount, 14843)

      for zDataSeq in zDataSetSeq:
         ScrCmds.statMsg("Reading 322 tracks at %s" % zDataSeq[0])
         CHelper().sequentialReadDMAExt(zDataSeq[1], zDataSeq[1] + zDataSeq[2], stepLBA, sectorCount, 14843)

      for zDataSeq in zDataSetSeq:
         ScrCmds.statMsg("Writing 322 tracks at %s" % zDataSeq[0])
         CHelper().sequentialWriteDMAExt(zDataSeq[1], zDataSeq[1] + zDataSeq[2], stepLBA, sectorCount, 14843)

      for zDataSeq in zDataSetSeq:
         ScrCmds.statMsg("Reading 322 tracks at %s" % zDataSeq[0])
         CHelper().sequentialReadDMAExt(zDataSeq[1], zDataSeq[1] + zDataSeq[2], stepLBA, sectorCount, 14843)

      # Enable Write Cache
      res = enable_WriteCache(exc = 0)
      ScrCmds.statMsg("Enable Write Cache result: %s" % res)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14843, 'Fail SetFeatures 0x02')

      # Enable Read Look Ahead
      res = enable_ReadLookAhead(exc = 0)
      ScrCmds.statMsg("Enable Read Look Ahead result: %s" % res)
      if res['LLRET'] != 0:
         ScrCmds.raiseException(14843, 'Fail SetFeatures 0xAA')

###########################################################################################################
class CCopyStationScreen(CState):
   """
      Description:
         - Generate random number for 600 loops.
         - If random number is even perform sequential write (or)
           If random number is odd perform random write.
         - Write to be done for random 32-128K Blocks(16-64MB) @ 128 Blocks per transfer.
         - Reset Drive for every 1/5 random loops.
         - Insert Variable time delay between 0.1-16sec for each loop.
         - Repeat the loop for 600 times (~20GB of Data)
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      ScrCmds.insertHeader("Copy Station Test",headChar='*')
      ret = CIdentifyDevice().ID
      self.maxLBA = ret['IDDefaultLBAs'] - (1024 * 128)
      if ret['IDCommandSet5'] & 0x400:
         self.maxLBA = ret['IDDefault48bitLBAs'] - (1024 * 128)

      for value in xrange(0,600):
         randomno = random.randrange(0,600)
         StartLBA = random.randrange(0,self.maxLBA)
         TotalBlocks = random.randrange(256,1024)
         EndLBA = StartLBA + (TotalBlocks * 128)
         if randomno%2 == 0:
             self.SequentialWrite(StartLBA,EndLBA)
         else:
             self.RandomWrite(StartLBA,EndLBA,TotalBlocks)
         randomreset = random.randrange(1,5)
         if randomreset == 1:
            data = ICmd.HardReset()
         randomdelay = random.randrange(0.1,16,1,float)
         time.sleep(randomdelay)

      objPwrCtrl.powerCycle(5000,12000,10,30)
   #-------------------------------------------------------------------------------------------------------
   def SequentialWrite(self,StartLBA,EndLBA):      
      objMsg.printMsg('.....SequentialWrite(%d,%d,128,128,0,0)' %(StartLBA,EndLBA)) 
      result = ICmd.SequentialWrite(StartLBA,EndLBA,128,128,0,0)
      if result['LLRET'] != 0:
         objMsg.printMsg ('SequentialWrite: %s' % result)
         ScrCmds.raiseException(14831, "Copy Station Test - SequentialWrite Failure")
   #-------------------------------------------------------------------------------------------------------
   def RandomWrite(self,StartLBA,EndLBA,TotalBlocks):
      objMsg.printMsg('.....RandomWrite(%d,%d,128,128,%d,0,0)' %(StartLBA,EndLBA,TotalBlocks)) 
      result = ICmd.RandomWrite(StartLBA,EndLBA,128,128,TotalBlocks,0,0)
      if result['LLRET'] != 0:
         objMsg.printMsg ('RandomWrite: %s' % result)
         ScrCmds.raiseException(14831, "Copy Station Test - RandomWrite Failure")

###########################################################################################################
class CAsusS4HibernationTest(CState):
   """
      Description: Asus S4 Hibernation test is to test the Hard Drive for System Hibernation Mode.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      ScrCmds.insertHeader("ASUS S4 - Hibernation Test",headChar='*')
      ret = CIdentifyDevice().ID
      IDmaxLBA = ret['IDDefaultLBAs']
      if ret['IDCommandSet5'] & 0x400:
         IDmaxLBA = ret['IDDefault48bitLBAs']
      self.maxLBA = IDmaxLBA - 1

      result = ICmd.SetFeatures(0x3,0x45)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(14829, "ASUS S4 Hibernation Test - SetFeatures Failure")

      self.PreHibernationTest()
      self.HibernationTest()
      self.PostHibernationTest()

      objPwrCtrl.powerCycle(5000,12000,10,30)
   #-------------------------------------------------------------------------------------------------------
   def VariableDelay(self):
      Delay_Counter = 0
      Delay_Range = random.randrange(1,96)
      while Delay_Counter < Delay_Range:
         time.sleep(0.1)
         Delay_Counter = Delay_Counter + 1
   #-------------------------------------------------------------------------------------------------------
   def PreHibernationTest(self):
      objMsg.printMsg (":Pre Hibernate Mode Test")
      ZoneLength = self.maxLBA / 3
      StartLBAOD = 0
      EndLBAOD = ZoneLength
      StartLBAMD = ZoneLength
      EndLBAMD = ZoneLength * 2
      StartLBAID = ZoneLength * 2
      EndLBAID = ZoneLength * 3
      self.PreHibernateData = []

      ICmd.HardReset()
      result = ICmd.ClearBinBuff(BWR)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(14829, "ASUS S4 Hibernation Test - ClearBinBuff Failure")

      result = ICmd.NCQSequentialWriteDMA(StartLBAOD,StartLBAOD+0x1000,256,256)
      if result['LLRET'] != 0:
         objMsg.printMsg ('NCQSequentialWriteDMA @ OD: %s' % result)
         ScrCmds.raiseException(14829, "ASUS S4 Hibernation Test - NCQSequentialWriteDMA Failure")

      result = ICmd.NCQSequentialWriteDMA(StartLBAMD,StartLBAMD+0x1000,256,256)
      if result['LLRET'] != 0:
         objMsg.printMsg ('NCQSequentialWriteDMA @ MD: %s' % result)
         ScrCmds.raiseException(14829, "ASUS S4 Hibernation Test - NCQSequentialWriteDMA Failure")

      result = ICmd.NCQSequentialWriteDMA(StartLBAID,StartLBAID+0x1000,256,256)
      if result['LLRET'] != 0:
         objMsg.printMsg ('NCQSequentialWriteDMA @ ID: %s' % result)
         ScrCmds.raiseException(14829, "ASUS S4 Hibernation Test - NCQSequentialWriteDMA Failure")

      ICmd.FillBuffByte(1,'A55A',0)
      ICmd.FillBuffByte(2,'A55A',0)
      if testSwitch.virtualRun:
         TestTime = 1
      else:
         TestTime = 180 #3min = 3 * 60 sec
      starttime = time.time()
      endtime = starttime + TestTime
      while time.time() < endtime:
         #SectorCount = random.sample([128,256],1)[0]
         SectorCount = random.randrange(2,512)
         StartLBA_Calc = random.randrange(0,self.maxLBA-512)
         EndLBA_Calc = StartLBA_Calc + SectorCount
         result = ICmd.SequentialWRDMA(StartLBA_Calc,EndLBA_Calc,SectorCount,SectorCount,0,1)
         if result['LLRET'] != 0:
            objMsg.printMsg ('SequentialWRDMA: %s' % result)
            ScrCmds.raiseException(14829, "ASUS S4 Hibernation Test - SequentialWRDMA Failure")

      if testSwitch.virtualRun:
         TestTime = 1
      else:
         TestTime = 60 #1min = 1 * 60 sec
      starttime = time.time()
      endtime = starttime + TestTime
      while time.time() < endtime:
         SectorCount = random.randrange(2,512)
         StartLBA_Calc = random.randrange(StartLBAOD,EndLBAOD-512)
         EndLBA_Calc = StartLBA_Calc + SectorCount
         result = ICmd.NCQSequentialReadDMA(StartLBA_Calc,EndLBA_Calc,SectorCount,SectorCount)
         if result['LLRET'] != 0:
            objMsg.printMsg ('NCQSequentialReadDMA @ OD: %s' % result)
            ScrCmds.raiseException(14829, "ASUS S4 Hibernation Test - NCQSequentialReadDMA Failure")

      if testSwitch.virtualRun:
         TestTime = 1
      else:
         TestTime = 60 #1min = 1 * 60 sec
      starttime = time.time()
      endtime = starttime + TestTime
      while time.time() < endtime:
         SectorCount = random.randrange(2,512)
         StartLBA_Calc = random.randrange(StartLBAMD,EndLBAMD-512)
         EndLBA_Calc = StartLBA_Calc + SectorCount
         result = ICmd.NCQSequentialReadDMA(StartLBA_Calc,StartLBA_Calc,SectorCount,SectorCount)
         if result['LLRET'] != 0:
            objMsg.printMsg ('NCQSequentialReadDMA @ MD: %s' % result)
            ScrCmds.raiseException(14829, " ASUS S4 Hibernation Test - NCQSequentialReadDMA Failure")

      if testSwitch.virtualRun:
         TestTime = 1
      else:
         TestTime = 60 #1min = 1 * 60 sec
      starttime = time.time()
      endtime = starttime + TestTime
      while time.time() < endtime:
         SectorCount = random.randrange(2,512)
         StartLBA_Calc = random.randrange(StartLBAID,EndLBAID-512)
         EndLBA_Calc = StartLBA_Calc + SectorCount
         result = ICmd.NCQSequentialReadDMA(StartLBA_Calc,EndLBA_Calc,SectorCount,SectorCount)
         if result['LLRET'] != 0:
            objMsg.printMsg ('NCQSequentialReadDMA @ ID: %s' % result)
            ScrCmds.raiseException(14829, "ASUS S4 Hibernation Test - NCQSequentialReadDMA Failure")

      ICmd.FillBuffByte(1,'9669',0)
      ICmd.FillBuffByte(2,'9669',0)
      if testSwitch.virtualRun:
         TestTime = 1
      else:
         TestTime = 180 #3min = 3 * 60 sec
      starttime = time.time()
      endtime = starttime + TestTime
      while time.time() < endtime:
         SectorCount = random.randrange(2,512)
         result = ICmd.NCQRandomWriteDMA(0,self.maxLBA-512,SectorCount,SectorCount,1)
         if result['LLRET'] != 0:
            objMsg.printMsg ('NCQRandomWriteDMA: %s' % result)
            ScrCmds.raiseException(14829, "ASUS S4 Hibernation Test - NCQRandomWriteDMA Failure")

      if testSwitch.virtualRun:
         TestTime = 1
      else:
         TestTime = 180 #3min = 3 * 60 sec
      starttime = time.time()
      endtime = starttime + TestTime
      while time.time() < endtime:
         SectorCount = random.randrange(2,512)
         result = ICmd.NCQRandomReadDMA(0,self.maxLBA-512,SectorCount,SectorCount,1)
         if result['LLRET'] != 0:
            objMsg.printMsg ('NCQRandomReadDMA: %s' % result)
            ScrCmds.raiseException(14829, "ASUS S4 Hibernation Test - NCQRandomReadDMA Failure")

      ICmd.FillBuffByte(1,'AAAA555510100505',0)
      ICmd.FillBuffByte(2,'AAAA555510100505',0)
      StartLBA_Calc = EndLBA_Calc = StartLBAOD
      EndLBA = StartLBAOD + 0x200
      while StartLBA_Calc < EndLBA:
         StartLBA_Calc = EndLBA_Calc
         EndLBA_Calc = StartLBA_Calc + 8
         result = ICmd.NCQSequentialWriteDMA(StartLBA_Calc,EndLBA_Calc,8,8)
         self.PreHibernateData.append ((StartLBA_Calc,EndLBA_Calc))
         if result['LLRET'] != 0:
            objMsg.printMsg ('NCQSequentialWriteDMA @ OD: %s' % result)
            ScrCmds.raiseException(14829, "ASUS S4 Hibernation Test - NCQSequentialWriteDMA Failure")

      StartLBA_Calc = EndLBA_Calc = StartLBAMD
      EndLBA = StartLBAMD + 0x200
      while StartLBA_Calc < EndLBA:
         StartLBA_Calc = EndLBA_Calc
         EndLBA_Calc = StartLBA_Calc + 8
         result = ICmd.NCQSequentialWriteDMA(StartLBA_Calc,EndLBA_Calc,8,8)
         self.PreHibernateData.append ((StartLBA_Calc,EndLBA_Calc))
         if result['LLRET'] != 0:
            objMsg.printMsg ('NCQSequentialWriteDMA @ MD: %s' % result)
            ScrCmds.raiseException(14829, "ASUS S4 Hibernation Test - NCQSequentialWriteDMA Failure")

      StartLBA_Calc = EndLBA_Calc = StartLBAID
      EndLBA = StartLBAID + 0x200
      while StartLBA_Calc < EndLBA:
         StartLBA_Calc = EndLBA_Calc
         EndLBA_Calc = StartLBA_Calc + 8
         result = ICmd.NCQSequentialWriteDMA(StartLBA_Calc,EndLBA_Calc,8,8)
         self.PreHibernateData.append ((StartLBA_Calc,EndLBA_Calc))
         if result['LLRET'] != 0:
            objMsg.printMsg ('NCQSequentialWriteDMA @ ID: %s' % result)
            ScrCmds.raiseException(14829, "ASUS S4 Hibernation Test - NCQSequentialWriteDMA Failure")

      result = ICmd.ClearBinBuff(BWR)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(14829, "ASUS S4 Hibernation Test - ClearBinBuff Failure")
   #-------------------------------------------------------------------------------------------------------
   def HibernationTest(self):
      objMsg.printMsg (":Hibernate Mode Test")
      result = ICmd.FlushCache()
      if result['LLRET'] != OK:
         ScrCmds.raiseException(14829, "ASUS S4 Hibernation Test - Failed FlushCache")

      result = ICmd.StandbyImmed() #Standby Immediate
      if result['LLRET'] != OK:
         ScrCmds.raiseException(14829, "ASUS S4 Hibernation Test - Failed StandbyImmed")

      time.sleep(30) #Delay 30 sec

      result = ICmd.HardReset() #SATA Reset
      if testSwitch.virtualRun: result = {'LLRET':0}
      if result['LLRET'] != OK:
         ScrCmds.raiseException(14829, "ASUS S4 Hibernation Test - Failed HardReset")

      time.sleep(3.6) #Delay 3.6 sec

      result = ICmd.HardReset() #SATA Reset
      if testSwitch.virtualRun: result = {'LLRET':0}
      if result['LLRET'] != OK:
         ScrCmds.raiseException(14829, "ASUS S4 Hibernation Test - Failed HardReset")

      result = ICmd.HardReset() #SATA Reset
      if testSwitch.virtualRun: result = {'LLRET':0}
      if result['LLRET'] != OK:
         ScrCmds.raiseException(14829, "ASUS S4 Hibernation Test - Failed HardReset")

      CIdentifyDevice()

      result = ICmd.Seek(0)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(14829, "ASUS S4 Hibernation Test - Failed Seek LBA0")

      result = ICmd.HardReset() #SATA Reset
      if testSwitch.virtualRun: result = {'LLRET':0}
      if result['LLRET'] != OK:
         ScrCmds.raiseException(14829, "ASUS S4 Hibernation Test - Failed HardReset")

      result = ICmd.SmartEnableOper()
      if result['LLRET'] != OK:
         ScrCmds.raiseException(14829, "ASUS S4 Hibernation Test - Failed SmartEnableOper")

      result = ICmd.SmartReadData()
      if result['LLRET'] != OK:
         ScrCmds.raiseException(14829, "ASUS S4 Hibernation Test - Failed SmartReadData")

      result = ICmd.HardReset() #SATA Reset
      if testSwitch.virtualRun: result = {'LLRET':0}
      if result['LLRET'] != OK:
         ScrCmds.raiseException(14829, "ASUS S4 Hibernation Test - Failed HardReset")

      CIdentifyDevice()

      result = ICmd.SetFeatures(0x03, 0x46) #Set Transfer Mode = UDMA6
      if result['LLRET'] != OK:
         ScrCmds.raiseException(14829, "ASUS S4 Hibernation Test - Failed SetFeatures")

      result = ICmd.SetFeatures(0x03, 0x46) #Set Transfer Mode = UDMA6
      if result['LLRET'] != OK:
         ScrCmds.raiseException(14829, "ASUS S4 Hibernation Test - Failed SetFeatures")

      time.sleep(2.5) #Delay 2.5 sec

      result = ICmd.SmartReturnStatus()
      if result['LLRET'] != OK:
         ScrCmds.raiseException(14829, "ASUS S4 Hibernation Test - Failed SmartReturnStatus")

      time.sleep(1) #Delay 1 sec

      result = ICmd.HardReset() #SATA Reset
      if testSwitch.virtualRun: result = {'LLRET':0}
      if result['LLRET'] != OK:
         ScrCmds.raiseException(14829, "ASUS S4 Hibernation Test - Failed HardReset")

      result = ICmd.Seek(0)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(14829, "ASUS S4 Hibernation Test - Failed Seek LBA0")

      result = ICmd.Seek(self.maxLBA )
      if result['LLRET'] != OK:
         ScrCmds.raiseException(14829, "ASUS S4 Hibernation Test - Failed Seek maxLBA")

   #-------------------------------------------------------------------------------------------------------
   def PostHibernationTest(self):
      objMsg.printMsg (":Post Hibernate Mode Test")
      ZoneLength = self.maxLBA / 3
      StartLBAOD = 0
      EndLBAOD = ZoneLength
      StartLBAMD = ZoneLength
      EndLBAMD = ZoneLength * 2
      StartLBAID = ZoneLength * 2
      EndLBAID = ZoneLength * 3

      if testSwitch.virtualRun:
         TestTime = 1
      else:
         TestTime = 60 #1min = 1 * 60 sec
      starttime = time.time()
      endtime = starttime + TestTime
      StartLBA_Calc = EndLBA_Calc = StartLBAOD
      while time.time() < endtime:
         StartLBA_Calc = EndLBA_Calc
         EndLBA_Calc = StartLBA_Calc + 1
         result = ICmd.SequentialReadDMAExt(StartLBA_Calc,EndLBA_Calc,0x1,0x1,0,0)
         if result['LLRET'] != 0:
            objMsg.printMsg ('SequentialReadDMAExt @ OD: %s' % result)
            ScrCmds.raiseException(14829, "ASUS S4 Hibernation Test - SequentialReadDMAExt Failure")

      ICmd.FillBuffByte(1,'AAAA555510100505',0)
      for item in self.PreHibernateData:
        StartLBA_Calc = item[0]
        EndLBA_Calc = item[1]
        result = ICmd.NCQSequentialReadDMA(StartLBA_Calc,EndLBA_Calc,0x8,0x8)
        if result['LLRET'] != 0:
           objMsg.printMsg ('NCQSequentialReadDMA: %s' % result)
           ScrCmds.raiseException(14829, "ASUS S4 Hibernation Test - NCQSequentialReadDMA Failure")
        result = ICmd.CompareBuffers(0,8)
        if result['LLRET'] != 0:
           objMsg.printMsg ('CompareBuffers: %s' % result)
           ScrCmds.raiseException(14829, "ASUS S4 Hibernation Test - CompareBuffers Failure")

      ICmd.FillBuffByte(1,'F00F',0)
      ICmd.FillBuffByte(2,'F00F',0)
      if testSwitch.virtualRun:
         TestTime = 1
      else:
         TestTime = 180 #3min = 3 * 60 sec
      starttime = time.time()
      endtime = starttime + TestTime
      while time.time() < endtime:
         SectorCount = random.randrange(2,512)
         result = ICmd.NCQRandomWriteDMA(0,self.maxLBA-512,SectorCount,SectorCount,1)
         if result['LLRET'] != 0:
            objMsg.printMsg ('NCQRandomWriteDMA: %s' % result)
            ScrCmds.raiseException(14829, "ASUS S4 Hibernation Test - NCQRandomWriteDMA Failure")

      #Instead for testing Whole Drive
      #random NCQ read for 5min
      if testSwitch.virtualRun:
         TestTime = 1
      else:
         TestTime = 300 #5min = 5 * 60 sec
      starttime = time.time()
      endtime = starttime + TestTime
      while time.time() < endtime:
         SectorCount = random.randrange(2,512)
         StartLBA_Calc = random.randrange(0,self.maxLBA-512)
         EndLBA_Calc = StartLBA_Calc + SectorCount
         result = ICmd.NCQSequentialReadDMA(StartLBA_Calc,EndLBA_Calc,SectorCount,SectorCount)
         if result['LLRET'] != 0:
            objMsg.printMsg ('NCQSequentialReadDMA: %s' % result)
            ScrCmds.raiseException(14829, "ASUS S4 Hibernation Test - NCQSequentialReadDMA Failure")

      #Sequential NCQ read for 3min - OD
      if testSwitch.virtualRun:
         TestTime = 1
      else:
         TestTime = 180 #3min = 3 * 60 sec
      starttime = time.time()
      endtime = starttime + TestTime
      StartLBA_Calc = EndLBA_Calc = StartLBAOD
      while time.time() < endtime:
         SectorCount = random.randrange(2,512)
         StartLBA_Calc = EndLBA_Calc
         EndLBA_Calc = StartLBA_Calc + SectorCount
         result = ICmd.NCQSequentialReadDMA(StartLBA_Calc,EndLBA_Calc,SectorCount,SectorCount)
         if result['LLRET'] != 0:
            objMsg.printMsg ('NCQSequentialReadDMA: %s' % result)
            ScrCmds.raiseException(14829, "ASUS S4 Hibernation Test - NCQSequentialReadDMA Failure")

      #Sequential NCQ read for 3min - MD
      if testSwitch.virtualRun:
         TestTime = 1
      else:
         TestTime = 180 #3min = 3 * 60 sec
      starttime = time.time()
      endtime = starttime + TestTime
      StartLBA_Calc = EndLBA_Calc = StartLBAMD
      while time.time() < endtime:
         SectorCount = random.randrange(2,512)
         StartLBA_Calc = EndLBA_Calc
         EndLBA_Calc = StartLBA_Calc + SectorCount
         result = ICmd.NCQSequentialReadDMA(StartLBA_Calc,EndLBA_Calc,SectorCount,SectorCount)
         if result['LLRET'] != 0:
            objMsg.printMsg ('NCQSequentialReadDMA: %s' % result)
            ScrCmds.raiseException(14829, "ASUS S4 Hibernation Test - NCQSequentialReadDMA Failure")

      #Sequential NCQ read for 3min - ID
      if testSwitch.virtualRun:
         TestTime = 1
      else:
         TestTime = 180 #3min = 3 * 60 sec
      starttime = time.time()
      endtime = starttime + TestTime
      StartLBA_Calc = EndLBA_Calc = StartLBAID
      while time.time() < endtime:
         SectorCount = random.randrange(2,512)
         StartLBA_Calc = EndLBA_Calc
         EndLBA_Calc = StartLBA_Calc + SectorCount
         result = ICmd.NCQSequentialReadDMA(StartLBA_Calc,EndLBA_Calc,SectorCount,SectorCount)
         if result['LLRET'] != 0:
            objMsg.printMsg ('NCQSequentialReadDMA: %s' % result)
            ScrCmds.raiseException(14829, "ASUS S4 Hibernation Test - NCQSequentialReadDMA Failure")

      result = ICmd.ClearBinBuff(BWR)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(14829, "ASUS S4 Hibernation Test - ClearBinBuff Failure")

###########################################################################################################
class CMultipleIdleModeTest(CState):
   """
      Description: Various Idle Mode test.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      ScrCmds.insertHeader("Various IDLE Mode Test",headChar='*')
      ret = CIdentifyDevice().ID # read device settings with identify device
      IDmaxLBA = ret['IDDefaultLBAs'] # default for 28-bit LBA
      if ret['IDCommandSet5'] & 0x400:      # check bit 10
         IDmaxLBA = ret['IDDefault48bitLBAs']
      self.maxLBA = IDmaxLBA - 1

      result = ICmd.SetFeatures(0x3,0x45)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(14830, "Various IDLE Mode Test - SetFeatures Failure")

      APM_Level = ["Disable","0x01","0x40","0xC0","0xFE","0x80"]
      for i in APM_Level:
         if i == "Disable":
            result = ICmd.SetFeatures(0x85)
            if result['LLRET'] != OK:
               ScrCmds.raiseException(14830, "Various IDLE Mode Test - SetFeatures Failure")
         else:
            Func = "ICmd.SetFeatures(0x5" + "," + i + ")"
            result = eval(Func)
            if result['LLRET'] != OK:
               ScrCmds.raiseException(14830, "Various IDLE Mode Test - SetFeatures Failure")

         for j in range(10):
            self.RandomWriteWithFlushCache()
            result = ICmd.IdleImmediate()
            if result['LLRET'] != OK:
               ScrCmds.raiseException(14830, "Various IDLE Mode Test - IdleImmediate Failure")

            self.VariableDelay()
            self.RandomWriteWithFlushCache()
            self.VariableDelay()
            self.RandomWriteWithFlushCache()
            result = ICmd.StandbyImmed()
            if result['LLRET'] != OK:
               ScrCmds.raiseException(14830, "Various IDLE Mode Test - StandbyImmed Failure")

            self.VariableDelay()
            self.RandomWriteWithFlushCache()
            result = ICmd.IdleImmediate()
            if result['LLRET'] != OK:
               ScrCmds.raiseException(14830, "Various IDLE Mode Test - IdleImmediate Failure")

            self.VariableDelay()
            self.RandomWriteWithFlushCache()
            result = ICmd.Sleep()
            if result['LLRET'] != OK:
               ScrCmds.raiseException(14830, "Various IDLE Mode Test - Sleep Failure")

            self.VariableDelay()
            self.RandomWriteWithFlushCache()
            objPwrCtrl.powerCycle(5000,12000,10,30)
   #-------------------------------------------------------------------------------------------------------
   def RandomWriteWithFlushCache(self):
      ICmd.HardReset()
      result = ICmd.ClearBinBuff(BWR)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(14830, "Various IDLE Mode Test - ClearBinBuff Failure")

      result = ICmd.RandomReadDMAExt(0,self.maxLBA-256,256,256,1,0,0,0)
      if result['LLRET'] != 0:
         objMsg.printMsg ('RandomReadDMAExt: %s' % result)
         ScrCmds.raiseException(14830, "Various IDLE Mode Test - RandomReadDMAExt Failure")

      ICmd.FillBuffRandom(1,0) #Fill Write Buffer with random data pattern
      data = ICmd.GetBuffer(1,0,512)['DATA']
      ICmd.FillBuffer(2,0,data)
      for i in range(5):
         Write_CmdRange = random.randrange(1,32)
         for j in range(Write_CmdRange):
            SectorCount = random.randrange(1,512)
            StartLBA_Calc = random.randrange(0,self.maxLBA-512)
            EndLBA_Calc = StartLBA_Calc + SectorCount
            if (i%2) <> 0:
               NCQWrite = 1
               result = ICmd.NCQSequentialWriteDMA(StartLBA_Calc,EndLBA_Calc,SectorCount,SectorCount)
               if result['LLRET'] != 0:
                  objMsg.printMsg ('NCQSequentialWriteDMA: %s' % result)
                  ScrCmds.raiseException(14830, "Various IDLE Mode Test- NCQSequentialWriteDMA Failure - StartLBA:%s EndLBA:%s" %(StartLBA_Calc,EndLBA_Calc))
            else:
               NCQWrite = 0
               result = ICmd.SequentialWriteDMA(StartLBA_Calc,EndLBA_Calc,SectorCount,SectorCount,0,0)
               if result['LLRET'] != 0:
                  objMsg.printMsg ('SequentialWriteDMA: %s' % result)
                  ScrCmds.raiseException(14830, "Various IDLE Mode Test- SequentialWriteDMA Failure - StartLBA:%s EndLBA:%s" %(StartLBA_Calc,EndLBA_Calc))

         result = ICmd.FlushCache()
         if result['LLRET'] != OK:
            ScrCmds.raiseException(14830, "Various IDLE Mode Test - Failed FlushCache")

         if NCQWrite == 0:
            result = ICmd.SequentialReadDMA(StartLBA_Calc,EndLBA_Calc,SectorCount,SectorCount,0,1)
            if result['LLRET'] != 0:
               objMsg.printMsg ('SequentialReadDMA: %s' % result)
               ScrCmds.raiseException(14830, "Various IDLE Mode Test- SequentialReadDMA Failure - StartLBA:%s EndLBA:%s" %(StartLBA_Calc,EndLBA_Calc))
   #-------------------------------------------------------------------------------------------------------
   def VariableDelay(self):
      Delay_Counter = 0
      Delay_Range = random.randrange(16,96)
      while Delay_Counter < Delay_Range:
         time.sleep(0.1)
         Delay_Counter = Delay_Counter + 1

###########################################################################################################
class CAsusIdle1Test(CState):
   """
      Description: Class that will perform APMIdle test. IdleAPM_TTR is expected in CPC 2.216 onwards
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      imaxLBA = CIdentifyDevice().ID["IDDefault48bitLBAs"]

      loop = 20
      if ConfigVars[CN]['BenchTop']:
         loop = 2

      objMsg.printMsg('IdleAPM_TTR with loop : %d' % loop)
      for i in xrange(loop):
         objPwrCtrl.powerCycle(5000, 12000, 6, 0) # offtime 6sec; ontime 0 sec to let CPC perform delay
         result = ICmd.IdleAPM_TTR(7, 0, imaxLBA, 256, 10) # IdleAPM_TTR(delay,minLba,maxLba,scnt,loopCnt)
         if result['LLRET'] != OK:
            msg = 'Fail IdleAPM_TTR. Return data = %s' % result
            ScrCmds.raiseException(10072, msg)

###########################################################################################################
class CSIEFITSTest(CState):
   """
      Description: SIE FITS Fitness Test (21~26).
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      ScrCmds.insertHeader("SIE FITS Fitness Test",headChar='*')
      ret = CIdentifyDevice().ID # read device settings with identify device
      IDmaxLBA = ret['IDDefaultLBAs'] # default for 28-bit LBA
      if ret['IDCommandSet5'] & 0x400:      # check bit 10
         IDmaxLBA = ret['IDDefault48bitLBAs']
      self.maxLBA = IDmaxLBA - 1

      result = ICmd.SetFeatures(0x3,0x45)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(14832, "SIE FITS Fitness Test - SetFeatures Failure")

      self.Test21()

      objMsg.printMsg("FITS22 Test: Reset Random @ 4.8V")
      objPwrCtrl.powerCycle(4800,12000,10,30) #PowerCycle with 4.8V
      self.Test22()
      time.sleep(2)
      objMsg.printMsg("FITS22 Test: Reset Random @ 5.2V")
      objPwrCtrl.powerCycle(5200,12000,10,30) #PowerCycle with 5.2V
      self.Test22()
      time.sleep(2)

      objMsg.printMsg("FITS23 Test: Reset RW @ 4.8V")
      objPwrCtrl.powerCycle(4800,12000,10,30)
      self.Test23()
      ICmd.HardReset()
      time.sleep(2)
      objMsg.printMsg("FITS23 Test: Reset RW @ 5.2V")
      objPwrCtrl.powerCycle(5200,12000,10,30)
      self.Test23()
      ICmd.HardReset()
      time.sleep(2)

      objPwrCtrl.powerCycle(5000,12000,10,30)
      self.Test24()
      time.sleep(2)

      self.Test26()
      time.sleep(2)

      objPwrCtrl.powerCycle(5000,12000,10,30)
   #-------------------------------------------------------------------------------------------------------
   def VariableDelay(self):
      Delay_Counter = 0
      Delay_Range = random.randrange(10,160)
      while Delay_Counter < Delay_Range:
         time.sleep(0.1)
         Delay_Counter = Delay_Counter + 1
   #-------------------------------------------------------------------------------------------------------
   def Test21(self):
      ZoneLength = self.maxLBA / 3
      StartLBAOD = 0
      EndLBAOD = ZoneLength - 0x80000
      StartLBAMD = ZoneLength
      EndLBAMD = (ZoneLength * 2) - 0x80000
      StartLBAID = ZoneLength * 2
      EndLBAID = (ZoneLength * 3) - 0x80000
      ReadLBARange = 0x80000 #512K LBA

      objMsg.printMsg("FITS21 Test: Screwy Read at OD Zone")
      StartLBA_OD = random.randrange(StartLBAOD,EndLBAOD)
      EndLBA_OD = StartLBA_OD + ReadLBARange
      EndLBA_Calc = StartLBA_OD
      while EndLBA_Calc < EndLBA_OD:
         StartLBA_Calc = EndLBA_Calc
         EndLBA_Calc = StartLBA_Calc + 16
         result = ICmd.SequentialReadDMAExt(StartLBA_Calc,EndLBA_Calc,16,16,0,0)
         if result['LLRET'] != 0:
            objMsg.printMsg ('SequentialReadDMAExt: %s' % result)
            ScrCmds.raiseException(14832, "FITS21 (Screwy Read) Failure - StartLBA:%s EndLBA:%s" %(StartLBA_Calc,EndLBA_Calc))

         result = ICmd.SequentialReadDMAExt(StartLBA_Calc,EndLBA_Calc,8,8,0,0)
         if result['LLRET'] != 0:
            objMsg.printMsg ('SequentialReadDMAExt: %s' % result)
            ScrCmds.raiseException(14832, "FITS21 (Screwy Read) Failure - StartLBA:%s EndLBA:%s" %(StartLBA_Calc,EndLBA_Calc))

   #-------------------------------------------------------------------------------------------------------
   def Test22(self):
      Reset_Drive = ["0x42","0x43","0x44","0x45","0x46"]
      CommandGroups = {
        "Write_Command_Group":["WriteDMAExt","WriteSectorsExt","NCQSequentialWriteDMA"],
        "Read_Command_Group": ["ReadDMAExt","ReadSectorsExt","NCQSequentialReadDMA"],
        #"Read_Command_Group": ["ReadDMAExt","ReadSectorsExt","ReadVerifySectsExt"],
        "Idle_Command_Group": ["IdleImmediate","StandbyImmed","Sleep"],
        "SetFeature_Command_Group": ["0x02","0x82","0x0B","0x8B","0xAA","0x55","0x66"],
        "APM_Command_Group":  ["Disable","0x01","0xFE","0x40","0x80"],
        #"Other_Command_Group":  ["FlushCacheExt","IdentifyDevice","SmartEnableOper","SmartReturnStatus","RandomDelay"]}
        "Other_Command_Group":  ["FlushCacheExt","IdentifyDevice","ExecDeviceDiag","SmartEnableOper","SmartReturnStatus","RandomDelay"]}
      Command_Group = ["Write_Command_Group","Read_Command_Group","Idle_Command_Group",\
                       "SetFeature_Command_Group","APM_Command_Group","Other_Command_Group"]

      LoopTime = 300 #5min = 5 * 60 sec
      Command_Count = 0
      result = {'LLRET':0}
      starttime = time.time()
      endtime = starttime + LoopTime
      while time.time() < endtime:
         Selected_Command_Group = random.sample(Command_Group,1)[0]
         Selected_Command = random.sample(CommandGroups.get(Selected_Command_Group),1)[0]
         if (Selected_Command_Group == "Write_Command_Group") or (Selected_Command_Group == "Read_Command_Group"):
            RndLBA = random.randrange(0,self.maxLBA-512)
            if Selected_Command == "NCQSequentialWriteDMA":
               SectorCnt = random.randrange(2,512)
               Func = "ICmd.NCQSequentialWriteDMA(" + str(RndLBA) + "," + str(RndLBA+SectorCnt) + "," + str(SectorCnt) + "," + str(SectorCnt) + ")"
            elif (Selected_Command == "NCQSequentialReadDMA"):
               SectorCnt = random.randrange(2,512)
               Func = "ICmd.NCQSequentialReadDMA(" + str(RndLBA) + "," + str(RndLBA+SectorCnt) + "," + str(SectorCnt) + "," + str(SectorCnt) + ")"
            else:
               SectorCnt = random.sample([128,256],1)[0]
               Func = "ICmd." + Selected_Command + "(" + str(RndLBA) + "," + str(SectorCnt) + ")"
            result = eval(Func)
            Command_Count = Command_Count + 1
         if (Selected_Command_Group == "Idle_Command_Group"):
            Func = "ICmd." + Selected_Command + "()"
            result = eval(Func)
            if Selected_Command == "Sleep":
               ICmd.HardReset()
            self.VariableDelay()
            Command_Count = Command_Count + 1
         if (Selected_Command_Group == "SetFeature_Command_Group"):
            Func = "ICmd.SetFeatures(" + Selected_Command + ")"
            result = eval(Func)
            Command_Count = Command_Count + 1
         if (Selected_Command_Group == "Other_Command_Group"):
            if Selected_Command == "RandomDelay":
               self.VariableDelay()
            else:
               Func = "ICmd." + Selected_Command + "()"
               result = eval(Func)
            Command_Count = Command_Count + 1
         if (Selected_Command_Group == "APM_Command_Group"):
            if Selected_Command == "Disable":
               Func = "ICmd.SetFeatures(0x85)"
            else:
               Func = "ICmd.SetFeatures(0x05," + Selected_Command + ")"
            result = eval(Func)
            Command_Count = Command_Count + 1

         if result['LLRET'] != 0:
            objMsg.printMsg ('%s: %s' % (Func,result))
            ScrCmds.raiseException(14832, "FITS22 Test: %s Failure" %Func)

         if Command_Count == 5:
            Reset_Command = random.sample(Reset_Drive,1)[0]
            result = ICmd.SetFeatures(0x03, Reset_Command) #Set Transfer Mode = UDMA6
            if result['LLRET'] != OK:
               ScrCmds.raiseException(14832, "FITS22 (Reset Random) - Failed SetFeatures")
            Command_Count = 0
            
         if testSwitch.virtualRun: break
   #-------------------------------------------------------------------------------------------------------
   def Test23(self):
      if testSwitch.virtualRun:
         LBARange = 0x1
      else:
         LBARange = 0x1800 #6144 LBA

      def run():
         Commands = ["NCQSequentialWrite","NCQSequentialRead","NCQRandomWrite","NCQRandomRead"]
         for i in range(10):
             Command_Exec = random.sample(Commands,1)[0]
             if Command_Exec == "NCQSequentialWrite": NCQSequentialWrite()
             if Command_Exec == "NCQSequentialRead": NCQSequentialRead()
             if Command_Exec == "NCQRandomWrite": NCQRandomWrite()
             if Command_Exec == "NCQRandomRead": NCQRandomRead()

      def NCQSequentialWrite():
         objMsg.printMsg("FITS23 Test: Sequential Write with NCQ")
         for j in range(2):
            for i in range(3):
               StartLBA_1 = random.randrange(0,self.maxLBA-0x1800)
               EndLBA_1 = StartLBA_1 + LBARange
               EndLBA_Calc = StartLBA_1
               while EndLBA_Calc < EndLBA_1:
                  SectorCnt = random.randrange(1,128)
                  StartLBA_Calc = EndLBA_Calc
                  EndLBA_Calc = StartLBA_Calc + SectorCnt
                  result = ICmd.NCQSequentialWriteDMA(StartLBA_Calc,EndLBA_Calc,SectorCnt,SectorCnt)
                  if result['LLRET'] != 0:
                     objMsg.printMsg ('NCQSequentialWriteDMA: %s' % result)
                     ScrCmds.raiseException(14832, "FITS23 Test: NCQSequentialWriteDMA Failure - StartLBA:%s EndLBA:%s" %(StartLBA_Calc,EndLBA_Calc))
            ICmd.HardReset()

      def NCQSequentialRead():
         objMsg.printMsg("FITS23 Test: Sequential Read with NCQ")
         for j in range(2):
            for i in range(3):
               StartLBA_1 = random.randrange(0,self.maxLBA-0x1800)
               EndLBA_1 = StartLBA_1 + LBARange
               EndLBA_Calc = StartLBA_1
               while EndLBA_Calc < EndLBA_1:
                  SectorCnt = random.randrange(1,128)
                  StartLBA_Calc = EndLBA_Calc
                  EndLBA_Calc = StartLBA_Calc + SectorCnt
                  result = ICmd.NCQSequentialReadDMA(StartLBA_Calc,EndLBA_Calc,SectorCnt,SectorCnt)
                  if result['LLRET'] != 0:
                     objMsg.printMsg ('NCQSequentialReadDMA: %s' % result)
                     ScrCmds.raiseException(14832, "FITS23 Test: NCQSequentialReadDMA Failure - StartLBA:%s EndLBA:%s" %(StartLBA_Calc,EndLBA_Calc))
            ICmd.HardReset()

      def NCQRandomWrite():
         objMsg.printMsg("FITS23 Test: Random Write with NCQ")
         for j in range(2):
            for i in range(3):
               SectorCnt = random.randrange(1,128)
               result = ICmd.NCQRandomWriteDMA(0,self.maxLBA-128,SectorCnt,SectorCnt,50)
               if result['LLRET'] != 0:
                  objMsg.printMsg ('NCQRandomWriteDMA: %s' % result)
                  ScrCmds.raiseException(14832, "FITS23 Test: NCQRandomWriteDMA Failure - StartLBA:%s EndLBA:%s" %(StartLBA_Calc,EndLBA_Calc))
            ICmd.HardReset()

      def NCQRandomRead():
         objMsg.printMsg("FITS23 Test: Random Read with NCQ")
         for j in range(2):
            for i in range(3):
               SectorCnt = random.randrange(1,128)
               result = ICmd.NCQRandomReadDMA(0,self.maxLBA-128,SectorCnt,SectorCnt,50)
               if result['LLRET'] != 0:
                  objMsg.printMsg ('NCQRandomReadDMA: %s' % result)
                  ScrCmds.raiseException(14832, "FITS23 Test: NCQRandomReadDMA Failure - StartLBA:%s EndLBA:%s" %(StartLBA_Calc,EndLBA_Calc))
            ICmd.HardReset()

      run() #Call main function
   #-------------------------------------------------------------------------------------------------------
   def Test24(self):
      objMsg.printMsg("FITS24 Test: Incremental Block")
      IncrBlock = 1024

      StartLBA_Calc = EndLBA_Calc = 0
      while EndLBA_Calc < self.maxLBA:
         Block_Count = 1
         while Block_Count < (IncrBlock+1):
            StartLBA_Calc = EndLBA_Calc
            EndLBA_Calc = StartLBA_Calc + Block_Count
            if EndLBA_Calc > self.maxLBA: break
            result = ICmd.SequentialReadDMA(StartLBA_Calc,EndLBA_Calc,Block_Count,Block_Count,0,0)
            Block_Count = Block_Count + 1
            if result['LLRET'] != 0:
               objMsg.printMsg ('SequentialReadDMA: %s' % result)
               ScrCmds.raiseException(14832, "FITS24 Test: SequentialReadDMA Failure - StartLBA:%s EndLBA:%s" %(StartLBA_Calc,EndLBA_Calc))

            if testSwitch.virtualRun: break
         if testSwitch.virtualRun: break
   #-------------------------------------------------------------------------------------------------------
   def Test26(self):
      objMsg.printMsg("FITS26 Test: MS Page File Write Simulation")

      StartLBA_Calc = EndLBA_Calc = self.maxLBA
      Block_Count = 4
      if testSwitch.virtualRun:
         forRange = 10
      else:
         forRange = 250000
      for i in range(forRange):
         StartLBA_Calc = EndLBA_Calc
         EndLBA_Calc = StartLBA_Calc - Block_Count         
         if objRimType.CPCRiser():
            result = ICmd.ReverseWriteDMA(StartLBA_Calc,EndLBA_Calc,Block_Count,0,0)            
         elif objRimType.IOInitRiser():
            result = ICmd.ReverseWriteDMA(EndLBA_Calc,StartLBA_Calc,Block_Count,Block_Count,0,0)   
         RandomCheck = random.randrange(1,11)
         if RandomCheck < 4:
            Block_Count = Block_Count + 4
            if Block_Count > 64: Block_Count = 4
         if result['LLRET'] != 0:
            objMsg.printMsg ('ReverseWriteDMA: %s' % result)
            ScrCmds.raiseException(14832, "FITS26 Test: ReverseWriteDMA Failure - StartLBA:%s EndLBA:%s" %(StartLBA_Calc,EndLBA_Calc))

###########################################################################################################
class CWrRdSmt(CState):
   """
   Write/Read SMART (WrRdSmt) test.
   """
   def __init__(self, dut, params={}):
      self.params = params
      self.dut = dut
      depList = []
      CState.__init__(self, dut, depList)

   def run(self):
      # ---------------------------------------------- collecting parameters ---
      oIdentifyDevice = CIdentifyDevice()
      self.maxLBA = oIdentifyDevice.getMaxLBA()
      startLBA    = TP.prm_WrRdSmt.get('START_LBA', 0)
      if startLBA == None: startLBA = 0
      ScrCmds.statMsg("Start LBA       = %s" % startLBA)
      endLBA      = TP.prm_WrRdSmt.get('END_LBA', self.maxLBA)
      if endLBA == None: endLBA = self.maxLBA
      ScrCmds.statMsg("End LBA         = %s" % endLBA)
      sectorCount = TP.prm_WrRdSmt.get('SECTOR_COUNT', 256)
      ScrCmds.statMsg("Sector Count    = %s blocks" % sectorCount)
      stepLBA     = sectorCount
      ScrCmds.statMsg("Step LBA        = %s blocks" % stepLBA)

      # --------------------------------------- running with defined pattern ---
      ptrn = TP.prm_WrRdSmt.get('W_PTRN', "65e2")
      ScrCmds.statMsg("Pattern         = 0x%s" % ptrn)
      res = ICmd.FillBuffByte(WBF, ptrn, 0, 512 * sectorCount)
      if res['LLRET'] != OK: ScrCmds.raiseException(14926, "Fill buffer fail!")
      if objRimType.CPCRiser(): 
         ScrCmds.statMsg("Writing...")
         CHelper().sequentialWriteDMAExt(startLBA, endLBA, stepLBA, sectorCount, 14845)
         ScrCmds.statMsg("Reading with comparing...")
         CHelper().sequentialReadCmpDMAExt(startLBA, endLBA, stepLBA, sectorCount, True, 14845)
      elif objRimType.IOInitRiser():                
         ScrCmds.statMsg("Write/Read with comparing using T643...")
         data = ICmd.BufferCompareTest( startLBA, endLBA-startLBA, 1, 512, exc = 0)
         if data['LLRET'] == -1:
            ScrCmds.raiseException(14845, "T643 - Sequential Write/Read Compare DMA Ext fail!")

      # ---------------------------------------- running with random pattern ---
      ICmd.FillBuffRandom(WBF, 0, 512 * sectorCount, exc = 1)      
      if objRimType.CPCRiser(): 
         ScrCmds.statMsg("Writing...")
         CHelper().sequentialWriteDMAExt(startLBA, endLBA, stepLBA, sectorCount, 14845)
         ScrCmds.statMsg("Reading with comparing...")
         CHelper().sequentialReadCmpDMAExt(startLBA, endLBA, stepLBA, sectorCount, True, 14845)
      elif objRimType.IOInitRiser():                
         ScrCmds.statMsg("Write/Read with comparing using T643...")
         data = ICmd.BufferCompareTest( startLBA, endLBA-startLBA, 1, 512, exc = 0)
         if data['LLRET'] == -1:
            ScrCmds.raiseException(14845, "T643 - Sequential Write/Read Compare DMA Ext fail!")

      # ------------------------------------------- checking VList and PList ---
      ScrCmds.statMsg("Checking VList and PList")
      import serialScreen
      oSerial = serialScreen.sptDiagCmds()      
      if objRimType.IOInitRiser():
         oSerial.enableDiags() 

      retry_ctr = 0
      retry_max = TP.prm_WrRdSmt.get('V_LIST_SP_RETRY', 3)
      while True:
         retry_ctr += 1
         ScrCmds.statMsg("Try #%s:" % retry_ctr)
         try:
            altList = oSerial.getAltListSummary()
            if len(altList['result']) > 0: break
         except:
            pass
         if (retry_ctr > retry_max):
            ScrCmds.raiseException(14926, "Unable to get VList and PList!")
         objPwrCtrl.powerCycle(5000, 12000, 10, 30)

      # check keywords value has to be equal to zero
      altListResult = oSerial.convDictItems(altList['result'], int, [16])
      for val in altListResult.itervalues():
         if val != 0:
            ScrCmds.raiseException(14926, "Not all values are zero!")
      objPwrCtrl.powerCycle(5000, 12000, 10, 30)

      # ---------------------------------------- checking Seagate attributes ---
      ScrCmds.statMsg("Checking Seagate attributes")
      from CustomCfg import CCustomCfg
      custConfig = CCustomCfg()
      custConfig.SMARTReadData(TP.prm_WrRdSmt.get('lCAIDS', {}))

      # ------------------------------------------------------------- ending ---
      objPwrCtrl.powerCycle(5000, 12000, 10, 30)

###########################################################################################################
class CAppleLTOS(CState):
   """
   Apple LTOS test.
   """
   def __init__(self, dut, params={}):
      self.params = params
      self.dut = dut
      depList = []
      CState.__init__(self, dut, depList)

   def run(self):
      # ----------------------------------------------------------- starting ---
      objPwrCtrl.powerCycle(4800, 12000, 10, 30)
      ICmd.SetIntfTimeout(TP.prm_AppleLTOS.get('IFACE_CMD_TO', 5) * 1000)
      # fill writing pattern
      ptrn = TP.prm_AppleLTOS.get('W_PTRN', "0000")
      if ptrn == None: ptrn = "0000"
      ScrCmds.statMsg("Pattern = 0x%s" % ptrn)
      res = ICmd.FillBuffByte(WBF, ptrn, 0, 512 * 256)
      if res['LLRET'] != OK:
         ScrCmds.statMsg("Result: %s" % res)
         ScrCmds.raiseException(14849, "Fill buffer fail!")

      # collecting information
      random.seed()
      oIdentifyDevice = CIdentifyDevice()
      maxLBA = oIdentifyDevice.getMaxLBA()
      lba_range = TP.prm_AppleLTOS.get('LBA_RANGE', 0x61A80)
      self.lba_od_start = 0
      self.lba_od_end   = lba_range
      self.lba_id_start = maxLBA - lba_range
      self.lba_id_end   = maxLBA - 1
      rndm_blk_sz = TP.prm_AppleLTOS.get('RNDM_BLK_SZ', [1, 256])

      ScrCmds.statMsg("Reading and Writing...")
      for loop in xrange(0, TP.prm_AppleLTOS.get('TTL_LOOP', 150)):
         # --------------------------------------------------------- writing ---
         blk_sz = random.randint(rndm_blk_sz[0], rndm_blk_sz[1])
         if blk_sz == 0: blk_sz = 1
         CHelper().sequentialWriteDMAExt(self.lba_od_start, self.lba_od_end, blk_sz, blk_sz, 14849)
         time.sleep(5)
         # --------------------------------------------------------- reading ---
         blk_sz = random.randint(rndm_blk_sz[0], rndm_blk_sz[1])
         if blk_sz == 0: blk_sz = 1
         CHelper().sequentialReadDMAExt(self.lba_id_start, self.lba_id_end, blk_sz, blk_sz, 14849)
         time.sleep(5)
         res = ICmd.StandbyImmed()
         if res['LLRET'] != OK:
            ScrCmds.statMsg("Result: %s" % res)
            ScrCmds.raiseException(14849, "Standby Immediate fail!")
         time.sleep(1)

      # ------------------------------------------------------------- ending ---
      ICmd.SetIntfTimeout(TP.prm_IntfTest["Default CPC Cmd Timeout"] * 1000)
      objPwrCtrl.powerCycle(5000, 12000, 10, 30)

###########################################################################################################
class CDelayRandomRead(CState):
   """
   Delay Random Read Test.
   """
   def __init__(self, dut, params={}):
      self.params = params
      self.dut = dut
      depList = []
      CState.__init__(self, dut, depList)

   def run(self):
      # ----------------------------------------------------------- starting ---
      objPwrCtrl.powerCycle(5000, 12000, 10, 30)
      ICmd.SetIntfTimeout(TP.prm_DLY_RNDM_RD.get('IFACE_CMD_TO', 5) * 1000)
      delay = TP.prm_DLY_RNDM_RD.get('DLY', 600)
      oIdentifyDevice = CIdentifyDevice()
      endLBA = oIdentifyDevice.getMaxLBA() - 1

      # ------------------------------------------------------------ testing ---
      voltage_flg = True
      for i in xrange(0, TP.prm_DLY_RNDM_RD.get('TTL_LOOP', 50)):
         if voltage_flg:   # use 5.250 Volts
            objPwrCtrl.powerCycle(5250, 12000, 10, 30)
            voltage_flg = False
         else:             # use 4.750 Volts
            objPwrCtrl.powerCycle(4750, 12000, 10, 30)
            voltage_flg = True
         time.sleep(delay)
         res = ICmd.RandomReadDMAExt(0, endLBA, 1, 256, 10)
         if res['LLRET'] != OK:
            ScrCmds.statMsg("Result: %s" % res)
            ScrCmds.raiseException(14850, "Random Read fail!")

      # ------------------------------------------------------------- ending ---
      ICmd.SetIntfTimeout(TP.prm_IntfTest["Default CPC Cmd Timeout"] * 1000)
      objPwrCtrl.powerCycle(5000, 12000, 10, 30)

###########################################################################################################
class CHP_WRC(CState):
   """
   HP WRC Test.
   """
   def __init__(self, dut, params={}):
      self.params = params
      self.dut = dut
      depList = []
      CState.__init__(self, dut, depList)

   def run(self):
      # ----------------------------------------------------------- starting ---
      random.seed()
      objPwrCtrl.powerCycle(4800, 12000, 10, 30)
      ICmd.SetIntfTimeout(TP.prm_HP_WRC.get('IFACE_CMD_TO', 5) * 1000)
      self.Z1      = TP.prm_HP_WRC.get('ZONE_1', [0x5A00, 0x6300])
      self.Z2      = TP.prm_HP_WRC.get('ZONE_2', [0x8A00, 0xA300])
      self.txLen   = TP.prm_HP_WRC.get('TX_LEN', [0x1, 0x80])
      self.blkSkip = TP.prm_HP_WRC.get('BLK_SKIP', [0x180, 0x280])
      rSleep       = TP.prm_HP_WRC.get('DLY', [1, 8])
      fixedDP      = TP.prm_HP_WRC.get('DATA_PTRN', '0106')

      # Enable Read Look Ahead
      res = enable_ReadLookAhead(exc = 0)
      ScrCmds.statMsg("Enable Read Look Ahead result: %s" % res)
      if res['LLRET'] != 0:
         ScrCmds.raiseException(14851, 'Fail SetFeatures 0xAA')

      # ------------------------------------------------------------ testing ---
      for i in xrange(0, TP.prm_HP_WRC.get('TTL_LOOP', 2)):
         # random data pattern
         ScrCmds.statMsg("Testing with random data pattern.")
         res = ICmd.FillBuffRandom(WBF, 0, 512 * 256)
         if res['LLRET'] != OK:
            ScrCmds.statMsg("Result: %s" % res)
            ScrCmds.raiseException(14851, "Fill buffer fail!")
         self.__wrRdCmp()
         time.sleep(random.randint(rSleep[0], rSleep[1]))

         # byte-wise incrementing data pattern
         ScrCmds.statMsg("Testing with byte-wise incrementing data pattern.")
         res = ICmd.FillBuffInc(WBF, 0, 512 * 256)
         if res['LLRET'] != OK:
            ScrCmds.statMsg("Result: %s" % res)
            ScrCmds.raiseException(14851, "Fill buffer fail!")
         self.__wrRdCmp()
         time.sleep(random.randint(rSleep[0], rSleep[1]))

         # byte-wise decrementing data pattern
         ScrCmds.statMsg("Testing with byte-wise decrementing data pattern.")
         res = ICmd.FillBuffDec(WBF, 0, 512 * 256)
         if res['LLRET'] != OK:
            ScrCmds.statMsg("Result: %s" % res)
            ScrCmds.raiseException(14851, "Fill buffer fail!")
         self.__wrRdCmp()
         time.sleep(random.randint(rSleep[0], rSleep[1]))

         # walking 1's data pattern (0x80, 0x40, 0x20, etc...)
         ScrCmds.statMsg("Testing with walking 1's data pattern.")
         res = ICmd.FillBuffByte(WBF, '8040201008040201', 0, 512 * 256)
         if res['LLRET'] != OK:
            ScrCmds.statMsg("Result: %s" % res)
            ScrCmds.raiseException(14851, "Fill buffer fail!")
         self.__wrRdCmp()
         time.sleep(random.randint(rSleep[0], rSleep[1]))

         # walking 0's data pattern (0x7F, 0xBF, 0xDF, etc...)
         ScrCmds.statMsg("Testing with walking 0's data pattern.")
         res = ICmd.FillBuffByte(WBF, '7FBFDFEFF7FBFDFE', 0, 512 * 256)
         if res['LLRET'] != OK:
            ScrCmds.statMsg("Result: %s" % res)
            ScrCmds.raiseException(14851, "Fill buffer fail!")
         self.__wrRdCmp()
         time.sleep(random.randint(rSleep[0], rSleep[1]))

         # fixed data pattern
         ScrCmds.statMsg("Testing with fixed data pattern (0x%s)." % fixedDP)
         res = ICmd.FillBuffByte(WBF, fixedDP, 0, 512 * 256)
         if res['LLRET'] != OK:
            ScrCmds.statMsg("Result: %s" % res)
            ScrCmds.raiseException(14851, "Fill buffer fail!")
         self.__wrRdCmp()
         time.sleep(random.randint(rSleep[0], rSleep[1]))

      # ------------------------------------------------------------- ending ---
      ICmd.SetIntfTimeout(TP.prm_IntfTest["Default CPC Cmd Timeout"] * 1000)
      objPwrCtrl.powerCycle(5000, 12000, 10, 30)

   def __wrRdCmp(self):
      wBuff = []
      Z1_end_flg = False
      Z2_end_flg = False
      Z1_off = self.Z1[0]; Z1_end = self.Z1[1]
      Z2_off = self.Z2[0]; Z2_end = self.Z2[1]

      # write and read immediate part
      while(True):
         if Z1_end_flg and Z2_end_flg: break
         r = random.randint(1, 100)
         # |------ 33% ------|--------------------- 67% ---------------------|
         #      W_Z1(Buff)                          W_Z2
         #                   |------- 22% -------|----------- 45% -----------|
         #                           R_Imm                 W_Z2(Buff)
         #                   |-- 11% --|-- 11% --|
         #                      FPDMA   Verify Sector
         # |1       -      33|34  -  44|45  -  55|56           -          100|
         if r <= 33:    # W_Z1(Buff)
            if Z1_end_flg: continue
            sectorCount = random.randint(self.txLen[0], self.txLen[1])
            stepLBA     = random.randint(self.blkSkip[0], self.blkSkip[1])
            CHelper().sequentialWriteDMAExt(Z1_off, Z1_off + sectorCount, sectorCount, sectorCount, 14851)
            wBuff.append([Z1_off, sectorCount])
            Z1_off += stepLBA
            if Z1_off > Z1_end: Z1_end_flg = True
         elif r <= 44:  # W_Z2 - R_Imm - FPDMA
            if Z2_end_flg: continue
            sectorCount = random.randint(self.txLen[0], self.txLen[1])
            stepLBA     = random.randint(self.blkSkip[0], self.blkSkip[1])
            CHelper().sequentialWriteDMAExt(Z2_off, Z2_off + sectorCount, sectorCount, sectorCount, 14851)
            CHelper().NCQSequentialReadDMA(Z2_off, Z2_off + sectorCount, sectorCount, sectorCount, 14851)
            Z2_off += stepLBA
            if Z2_off > Z2_end: Z2_end_flg = True
         elif r <= 55:  # W_Z2 - R_Imm - Verify Sector
            if Z2_end_flg: continue
            sectorCount = random.randint(self.txLen[0], self.txLen[1])
            stepLBA     = random.randint(self.blkSkip[0], self.blkSkip[1])
            CHelper().sequentialWriteDMAExt(Z2_off, Z2_off + sectorCount, sectorCount, sectorCount, 14851)
            CHelper().sequentialReadVerifyExt(Z2_off, Z2_off + sectorCount, sectorCount, sectorCount, 14851)
            Z2_off += stepLBA
            if Z2_off > Z2_end: Z2_end_flg = True
         else:          # W_Z2(Buff)
            if Z2_end_flg: continue
            sectorCount = random.randint(self.txLen[0], self.txLen[1])
            stepLBA     = random.randint(self.blkSkip[0], self.blkSkip[1])
            CHelper().sequentialWriteDMAExt(Z2_off, Z2_off + sectorCount, sectorCount, sectorCount, 14851)
            wBuff.append([Z2_off, sectorCount])
            Z2_off += stepLBA
            if Z2_off > Z2_end: Z2_end_flg = True

      # read based on buffer part
      for rLocCount in wBuff:
         CHelper().sequentialReadCmpDMAExt(rLocCount[0], rLocCount[0] + rLocCount[1], \
                                           rLocCount[1], rLocCount[1], True, 14851)

###########################################################################################################
class CNEC_PFM(CState):
   """
   NEC Performance Test.
   """
   def __init__(self, dut, params={}):
      depList = []
      CState.__init__(self, dut, depList)

   def run(self):
      # ----------------------------------------------------------- starting ---
      objPwrCtrl.powerCycle(5000, 12000, 10, 30)
      oIdentifyDevice = CIdentifyDevice()
      endLBA = oIdentifyDevice.getMaxLBA() - 1
      tx_blk = TP.prm_NEC_PFM.get('TX_BLK', 1)
      ttl_read = TP.prm_NEC_PFM.get('TTL_READ', 9000)
      time_out = TP.prm_NEC_PFM.get('TIME_OUT', 220000)

      StartTime = time.time()
      res = ICmd.RandomReadDMAExt(0, endLBA, tx_blk, tx_blk, ttl_read)      
      EndTime = time.time()      
      CT = EndTime -  StartTime
      ScrCmds.statMsg("Result: %s" % res)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14857, "Random Read DMA Ext fail!")

      if objRimType.CPCRiser():    
         ct = res.get('CT', None)                  
      elif objRimType.IOInitRiser():
         ct = CT    
         
      if testSwitch.virtualRun: ct = "%s" % (time_out - 1)
      if ct == None:
         ScrCmds.raiseException(14857, "Can't find Command Time (CT) from result.")
      elif int(ct) >= time_out:
         ScrCmds.raiseException(14857, "Execution time (%sms) is longer than requirement (%sms)!" % (ct, time_out))

      objPwrCtrl.powerCycle(5000, 12000, 10, 30)

###########################################################################################################
class CHP_Store_Self_Test_Int(CState):
   """
   HP Self Test Interrupt is part of HP Store Test under DST Suite.
   """
   def __init__(self, dut, params={}):
      depList = []
      CState.__init__(self, dut, depList)

   def run(self):
      # -------------------------------------------------------- preparation ---
      objPwrCtrl.powerCycle(4800, 12000, 10, 30)
      try:
         ICmd.SetIntfTimeout(TP.prm_HP_Store_STINT.get('IFACE_CTO', 5) * 1000)
      except:
         ScrCmds.raiseException(14915, "Setting Interface Timeout is failed.")
      self.commonDelay = TP.prm_HP_Store_STINT.get('DLY', 0.5)
      self.mode4LBALen = TP.prm_HP_Store_STINT.get('Mode4LBALen', 0x02545AB8)
      oIdentifyDevice = CIdentifyDevice()
      self.maxLBA = oIdentifyDevice.getMaxLBA()
      # --------------------------------------------------------------- main ---
      for mainLoop in xrange(1, 4):
         ScrCmds.statMsg("---------------------------- loop: %s ---" % mainLoop)
         self.gMainLoop = mainLoop
         res = ICmd.SmartEnableOper()
         if res['LLRET'] != OK:
            ScrCmds.raiseException(14915, "SmartEnableOper() function is failed.")
         res = ICmd.SmartOffLineImmed(0x7F)
         if res['LLRET'] != OK:
            ScrCmds.raiseException(14915, "SmartOffLineImmed(0x7F) function is failed.")
         self.runCases()

      # ------------------------------------------------------------- ending ---
      try:
         res = ICmd.SetIntfTimeout(TP.prm_IntfTest["Default CPC Cmd Timeout"] * 1000)
      except:
         ScrCmds.raiseException(14915, "Setting Interface Timeout to default is failed.")
      objPwrCtrl.powerCycle(5000, 12000, 10, 30)

   # ----------------------------------------------------------------- cases ---
   def runCases(self):
      self.runStandbyImmediate()
      self.runDisableSmart()
      self.runSmartOfflineImmediate()
      self.runSmartAbortDST()
      self.runPIOReadExt()
      self.runPIOWriteExt()
      self.runReadDMAExt()
      self.runWriteDMAExt()
      self.runPIOReadBuffer()
      self.runPIOWriteBuffer()
      self.runIdentifyDevice()
      self.runExecuteDeviceDiag()
      self.runRecalibrate()
      self.runReadVerifyExt()
      self.runSeek()

   def runStandbyImmediate(self):
      ScrCmds.statMsg(" --- runStandbyImmediate ---")
      # Call Pre-process Algorithm.
      self.preProcMain(False)
      # Standby Immediate (Cmd:E0h).
      res = ICmd.StandbyImmed()
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14915, "runStandbyImmediate: StandbyImmed function is failed.")
      # Set interface command time out to 10 seconds.
      try:
         res = ICmd.SetIntfTimeout(TP.prm_HP_Store_STINT.get('IDLE_IMM_CTO', 10) * 1000)
      except:
         ScrCmds.raiseException(14915, "runStandbyImmediate: Setting Interface Timeout to IDLE_IMM_CTO is failed.")
      # Call Post-process Algorithm.
      self.postProcMain(True)
      # Execute random read command to wake up drive.
      res = ICmd.RandomReadDMAExt(0, self.maxLBA - 2, 1, 1, 1,0,0,0)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14915, "runStandbyImmediate: RandomReadDMAExt function is failed.")
      # Set interface command time out back to 5 seconds.
      try:
         res = ICmd.SetIntfTimeout(TP.prm_HP_Store_STINT.get('IFACE_CTO', 5) * 1000)
      except:
         ScrCmds.raiseException(14915, "runStandbyImmediate: Setting Interface Timeout to IFACE_CTO is failed.")

   def runDisableSmart(self):
      ScrCmds.statMsg(" --- runDisableSmart ---")
      # Call Pre-process Algorithm.
      self.preProcMain(True)
      # Disable SMART/DFP (Cmd:B0h, Device:A0h, LBA:C24F01h, Feature:D9h).
      res = ICmd.SmartDisableOper()
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14915, "runDisableSmart: SmartDisableOper function is failed.")
      # Enable SMART/DFP (Cmd:B0h, Device:A0h, LBA:C24F01h, Feature:D8h).
      res = ICmd.SmartEnableOper()
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14915, "runDisableSmart: SmartEnableOper function is failed.")
      # Call Post-process Algorithm.
      self.postProcMain(True)

   def runSmartOfflineImmediate(self):
      ScrCmds.statMsg(" --- runSmartOfflineImmediate ---")
      # Call Pre-process Algorithm.
      self.preProcMain(True)
      # Execute SMART Off-line Immediate (Cmd:B0h, LBA:C24F00h, Feature:D4h).
      res = ICmd.SmartOffLineImmed(0x00)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14915, "runSmartOfflineImmediate: SmartOffLineImmed(0x00) function is failed.")
      # Call Post-process Algorithm.
      self.postProcMain(True)

   def runSmartAbortDST(self):
      ScrCmds.statMsg(" --- runSmartAbortDST ---")
      # Call Pre-process Algorithm.
      self.preProcMain(True)
      # Execute SMART Abort DST (Cmd:B0h, LBA:C24F7Fh, Feature:D4h).
      res = ICmd.SmartOffLineImmed(0x7F)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14915, "runSmartAbortDST: SmartOffLineImmed(0x7F) function is failed.")
      # Call Post-process Algorithm.
      self.postProcMain(True)

   def runPIOReadExt(self):
      ScrCmds.statMsg(" --- runPIOReadExt ---")
      # Call Pre-process Algorithm.
      self.preProcMain(True)
      # Get random LBA from Min LBA to Max LBA - 200h.
      random.seed()
      rndLBA = random.randint(0, self.maxLBA - 0x200)
      # Execute Read Sector Ext for one LBA (Cmd:24h, Device:E0h, LBA:Rnd, Count:01h).
      res = ICmd.ReadSectorsExt(rndLBA, 1)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14915, "runPIOReadExt: ReadSectorsExt function is failed.")
      # Execute Write Buffer PIO (Cmd:E8h).
      res = ICmd.WriteBuffer()
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14915, "runPIOReadExt: WriteBufferCmd function is failed.")
      # Execute Read Buffer PIO (Cmd:E4h).
      res = ICmd.ReadBuffer()
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14915, "runPIOReadExt: ReadBufferCmd function is failed.")
      # Call Post-process Algorithm.
      self.postProcMain(False)

   def runPIOWriteExt(self):
      ScrCmds.statMsg(" --- runPIOWriteExt ---")
      # Call Pre-process Algorithm.
      self.preProcMain(True)
      # Get random LBA from Min LBA to Max LBA - 200h.
      random.seed()
      rndLBA = random.randint(0, self.maxLBA - 0x200)
      # Execute Write Sector Ext for one LBA (Cmd:34h, Device:E0h, LBA:Rnd, Count:01h).
      res = ICmd.WriteSectorsExt(rndLBA, 1)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14915, "runPIOWriteExt: WriteSectorsExt function is failed.")
      # Call Post-process Algorithm.
      self.postProcMain(False)

   def runReadDMAExt(self):
      ScrCmds.statMsg(" --- runReadDMAExt ---")
      # Call Pre-process Algorithm.
      self.preProcMain(True)
      # Get random LBA from Min LBA to Max LBA - 200h.
      random.seed()
      rndLBA = random.randint(0, self.maxLBA - 0x200)
      # Execute Read DMA Ext for one LBA (Cmd:25h, Device:E0h, LBA:Rnd, Count:01h).
      try:
         CHelper().readDMAExt(rndLBA, 1,14915)
      except:
         ScrCmds.raiseException(14915, "runReadDMAExt: ReadDMAExt function is failed.")
      # Execute Write Buffer PIO (Cmd:E8h).
      res = ICmd.WriteBuffer()
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14915, "runReadDMAExt: WriteBufferCmd function is failed.")
      # Execute Read Buffer PIO (Cmd:E4h).
      res = ICmd.ReadBuffer()
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14915, "runReadDMAExt: ReadBufferCmd function is failed.")
      # Call Post-process Algorithm.
      self.postProcMain(False)

   def runWriteDMAExt(self):
      ScrCmds.statMsg(" --- runWriteDMAExt ---")
      # Call Pre-process Algorithm.
      self.preProcMain(True)
      # Get random LBA from Min LBA to Max LBA - 200h.
      random.seed()
      rndLBA = random.randint(0, self.maxLBA - 0x200)
      # Execute Write DMA Ext for one LBA (Cmd:35h, Device:E0h, LBA:Rnd, Count:01h).
      try:
         CHelper().writeDMAExt(rndLBA, 1,14915)    
      except:
         ScrCmds.raiseException(14915, "runWriteDMAExt: WriteDMAExt function is failed.")
      # Call Post-process Algorithm.
      self.postProcMain(False)

   def runPIOReadBuffer(self):
      ScrCmds.statMsg(" --- runPIOReadBuffer ---")
      # Call Pre-process Algorithm.
      self.preProcMain(True)
      # Execute Read Buffer PIO (Cmd:E4h).
      res = ICmd.ReadBuffer()
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14915, "runPIOReadBuffer: ReadBufferCmd function is failed.")
      # Call Post-process Algorithm.
      self.postProcMain(False)

   def runPIOWriteBuffer(self):
      ScrCmds.statMsg(" --- runStanrunPIOWriteBufferdbyImmediate ---")
      # Call Pre-process Algorithm.
      self.preProcMain(True)
      # Execute Write Buffer PIO (Cmd:E8h).
      res = ICmd.WriteBuffer()
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14915, "runPIOWriteBuffer: WriteBufferCmd function is failed.")
      # Call Post-process Algorithm.
      self.postProcMain(False)

   def runIdentifyDevice(self):
      ScrCmds.statMsg(" --- runIdentifyDevice ---")
      # Call Pre-process Algorithm.
      self.preProcMain(True)
      # Execute Identify Device (Cmd:ECh).
      res = ICmd.IdentifyDevice()
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14915, "runIdentifyDevice: IdentifyDevice function is failed.")
      # Call Post-process Algorithm.
      self.postProcMain(False)

   def runExecuteDeviceDiag(self):
      ScrCmds.statMsg(" --- runExecuteDeviceDiag ---")
      # Call Pre-process Algorithm.
      self.preProcMain(True)
      # Execute Device Diagnostic (Cmd:90h).
      res = ICmd.ExecDeviceDiag()
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14915, "runExecuteDeviceDiag: ExecDeviceDiag function is failed.")
      # Call Post-process Algorithm.
      self.postProcMain(False)

   def runRecalibrate(self):
      ScrCmds.statMsg(" --- runRecalibrate ---")
      # Call Pre-process Algorithm.
      self.preProcMain(True)
      # Recalibrate (Cmd:10h)
      res = ICmd.Recalibrate()
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14915, "runRecalibrate: Recalibrate function is failed.")
      # Call Post-process Algorithm.
      self.postProcMain(False)

   def runReadVerifyExt(self):
      ScrCmds.statMsg(" --- runReadVerifyExt ---")
      # Call Pre-process Algorithm.
      self.preProcMain(True)
      # Execute Read Verify Sector Ext at LBA 0 (Cmd:42h, LBA:0h, Count:01h).
      res = ICmd.ReadVerifyExt(0, 1)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14915, "runReadVerifyExt: ReadVerifySectsExt function is failed.")
      # Call Post-process Algorithm.
      self.postProcMain(False)

   def runSeek(self):
      ScrCmds.statMsg(" --- runSeek ---")
      # Call Pre-process Algorithm.
      self.preProcMain(True)
      # Seek to cylinder 1 (Cmd:70h).
      res = ICmd.Seek(1, 0, 1)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14915, "runSeek: Seek function is failed.")
      # Call Post-process Algorithm.
      self.postProcMain(False)

   # ----------------------------------------------------------- pre-process ---
   def preProcMain(self, offLnDatColCapChk = False):
      # Execute SMART Abort DST (Cmd:B0h, LBA:C24F7Fh, Feature:D4h)
      res = ICmd.SmartOffLineImmed(0x7F)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14915, "SmartOffLineImmed(0x7F) function is failed.")

      # Execute SMART Read Data (Cmd:B0h, Device:A0h, LBA:C24F00h, Feature:D0)
      res = ICmd.SmartReadData()
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14915, "SmartReadData function is failed.")
      res = ICmd.GetBuffer(RBF, 0, 512)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14915, "GetBuffer function is failed.")
      # Get SMART Data buffer offset 363 (Self-test execution status byte)
      off363 = ord(res['DATA'][363])
      if testSwitch.virtualRun: off363 = 0x19
      ScrCmds.statMsg("SMART Data Offset 363 pre:  %s" % hex(off363))

      # Checking for "self-test execution status"
      if offLnDatColCapChk:
         if not ((off363 & 0xF0) == 0x10):
            ScrCmds.raiseException(14915, "Self-test execution is not supported.")

      time.sleep(self.commonDelay)

      if self.gMainLoop == 1: self.preProcMode1()
      if self.gMainLoop == 2: self.preProcMode2()
      if self.gMainLoop == 3: self.preProcMode4()

   def preProcMode1(self):
      # Execute SMART Short self-test routine immediately in off-line mode
      # (Cmd:B0h, LBA:C24F01h, Feature:D4h)
      res = ICmd.SmartOffLineImmed(0x01)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14915, "SmartOffLineImmed(0x01) function is failed.")

      time.sleep(self.commonDelay)

   def preProcMode2(self):
      # Execute SMART Extended self-test routine immediately in off-line mode
      # (Cmd:B0h, LBA:C24F02h, Feature:D4h)
      res = ICmd.SmartOffLineImmed(0x02)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14915, "SmartOffLineImmed(0x02) function is failed.")

      time.sleep(self.commonDelay)

   def preProcMode4(self):
      result = ICmd.ClearBinBuff(WBF)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(14829, "Clearing Write Buffer is failed.")

      nonZeroData = ""
      # Byte 0-1 (Data structure revision number) : 0001h
      revNum = CUtility.convertNum2StrHexChar(0x0001, 'L', 8, 16)
      nonZeroData += revNum
      res = ICmd.PutBuffByte(WBF, revNum, 0)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14915, "Filling buffer for Byte 0-1 is failed.")
      # Byte 2-9 (Starting LBA for test span 1) : 00000000h
      startLBA1 = CUtility.convertNum2StrHexChar(0x00, 'L', 8, 64)
      nonZeroData += startLBA1
      res = ICmd.PutBuffByte(WBF, startLBA1, 2)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14915, "Filling buffer for Byte 2-9 is failed.")
      # Byte 10-17 (Ending LBA for test span 1) : 02545AB8h
      endLBA1 = CUtility.convertNum2StrHexChar(self.mode4LBALen, 'L', 8, 64)
      nonZeroData += endLBA1
      res = ICmd.PutBuffByte(WBF, endLBA1, 10)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14915, "Filling buffer for Byte 10-17 is failed.")
      # Byte 18-25 (Starting LBA for test span 2) : max LBA - 02545AB8h
      startLBA2 = CUtility.convertNum2StrHexChar((self.maxLBA - self.mode4LBALen), 'L', 8, 64)
      nonZeroData += startLBA2
      res = ICmd.PutBuffByte(WBF, startLBA2, 18)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14915, "Filling buffer for Byte 18-25 is failed.")
      # Byte 26-33 (Ending LBA for test span 2) : max LBA
      endLBA2 = CUtility.convertNum2StrHexChar(self.maxLBA, 'L', 8, 64)
      nonZeroData += endLBA2
      res = ICmd.PutBuffByte(WBF, endLBA2, 26)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14915, "Filling buffer for Byte 26-33 is failed.")
      # Byte 502-503 (Feature flags) : 0002h
      featureFlag = CUtility.convertNum2StrHexChar(0x0002, 'L', 8, 16)
      nonZeroData += featureFlag
      res = ICmd.PutBuffByte(WBF, featureFlag, 502)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14915, "Filling buffer for Byte 502-503 is failed.")
      # Byte 511 (Data structure checksum) : checksum
      import re
      keyc = re.compile("[0-9A-Fa-f]" * 2)
      sum = 0
      for oneByte in keyc.findall(nonZeroData):
         sum += int(oneByte, 16)
      checksum = "%0.2x" % ((0x100 - (sum % 0x100)) % 0x100)
      res = ICmd.PutBuffByte(WBF, checksum, 511)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14915, "Filling buffer for Byte 511 is failed.")

      if DEBUG:
         res = ICmd.GetBuffer(WBF, 0, 512)
         if res['LLRET'] == OK:
            rdStr = str(res['DATA'])
            ScrCmds.statMsg("Data On Write Buffer = \n%s" % \
                            CUtility.convertStrChar2StrHexChar(str(rdStr), ' '))

      # Fill Selective Self-Test Log with following data
      # (Cmd:B0h, LBA:C24F09h, Count:01h, Feature:D6h).
      res = ICmd.SmartWriteLogSec(0x09, 0x01)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14915, "SmartWriteLogSec(0x09, 0x01) function is failed.")

      # Execute SMART Selective self-test routine immediately in off-line mode
      # (Cmd:B0h, LBA:C24F04h, Feature:D4h).
      res = ICmd.SmartOffLineImmed(0x04)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14915, "SmartOffLineImmed(0x04) function is failed.")

      time.sleep(self.commonDelay)

   # ---------------------------------------------------------- post-process ---
   def postProcMain(self, checkingFlag = True):
      # Execute SMART Read Data (Cmd:B0h, Device:A0h, LBA:C24F00h, Feature:D0)
      res = ICmd.SmartReadData()
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14915, "SmartReadData function is failed.")
      res = ICmd.GetBuffer(RBF, 0, 512)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14915, "GetBuffer function is failed.")
      # Get SMART Data buffer offset 363 (Self-test execution status byte)
      off363 = ord(res['DATA'][363])
      if testSwitch.virtualRun:
         if checkingFlag:  off363 = 0x19
         else:             off363 = 0xF9

      ScrCmds.statMsg("SMART Data Offset 363 post: %s" % hex(off363))
      # Checking
      if checkingFlag:
         # The self-test routine was aborted by the host.
         if not ((off363 & 0xF0) == 0x10):
            ScrCmds.raiseException(14915, "The self-test routine was not aborted by the host.")
      else:
         # Self-test routine in progress.
         if not ((off363 & 0xF0) == 0xF0):
            ScrCmds.raiseException(14915, "Self-test routine is not in progress.")
      
      time.sleep(self.commonDelay)

###########################################################################################################
class CAcerS3(CState):
   """
   Customer Emulation Test (CET) for Acer S3 
   """
   def __init__(self, dut, params={}):
      depList = []
      CState.__init__(self, dut, depList)

   def run(self):
      objPwrCtrl.powerCycle(5000, 12000, 10, 30)

      ttl_test_time = TP.prm_Acer_S3.get('TTL_TEST_TIME', 30)
      
      oIdentifyDevice = CIdentifyDevice()
      self.endLBA = oIdentifyDevice.getMaxLBA() - 1
      self.LBA_range_80 = TP.prm_Acer_S3.get('LBA_RANGE_80', [19531250, 156250000])
      if self.LBA_range_80[0] >= self.endLBA: self.LBA_range_80[0] = 0 
      if self.LBA_range_80[1] > self.endLBA: self.LBA_range_80[1] = self.endLBA
      
      rPtrn = CUtility.getRandomPattern(64)
      res = ICmd.FillBuffByte(WBF, rPtrn, 0, 512 * 256)
      if res['LLRET'] != OK:
         ScrCmds.statMsg("Result: %s" % res)
         ScrCmds.raiseException(14920, 'Fill Buff Byte fail')

      idDev = CIdentifyDevice()
      DMASetupSupport = idDev.ID["SATAFeatures"] & 0x04
      if DEBUG: ScrCmds.statMsg("SATA Features: 0x%x" % idDev.ID["SATAFeatures"])

      startTime = time.time()
      while True:
         if DEBUG: ScrCmds.statMsg("=" * 150)
         # 1. Write FPMDA (NCQ).
         scnt = self.getRandSectorCount()
         startLBA = self.getRandStartLBA(scnt)
         if DEBUG: ScrCmds.statMsg("Write FPDMA: %10s, %10s, %10s" % \
                                   (startLBA, startLBA + scnt, scnt))
         CHelper().NCQSequentialWriteDMA(startLBA, startLBA + scnt, scnt, scnt, 14920)
         # 2. Standby immediate (E0/FF sec cnt=00).
         res = ICmd.StandbyImmed()
         if res['LLRET'] != OK:
            ScrCmds.statMsg("Result: %s" % res)
            ScrCmds.raiseException(14920, "Standby Immediate fail")
         # 3. Write FPDMA(NCQ) 3x.
         for i in xrange(3):
            scnt = self.getRandSectorCount()
            startLBA = self.getRandStartLBA(scnt)
            if DEBUG: ScrCmds.statMsg("Write FPDMA: %10s, %10s, %10s" % \
                                      (startLBA, startLBA + scnt, scnt))
            CHelper().NCQSequentialWriteDMA(startLBA, startLBA + scnt, scnt, scnt, 14920)
         # Saving last start LBA and sector count before long standby immediate  
         last_scnt = scnt
         last_startLBA = startLBA
         # 4. Standby immediate (E0/FF sec cnt=00).
         res = ICmd.StandbyImmed()
         if res['LLRET'] != OK:
            ScrCmds.statMsg("Result: %s" % res)
            ScrCmds.raiseException(14920, "Standby Immediate fail")
         # 5. 60 sec later, Identify Drive .
         if DEBUG: ScrCmds.statMsg("Sleep for 60 seconds")
         time.sleep(60)
         ICmd.IdentifyDevice()
         # 6. Set multiple mode
         res = ICmd.SetMultipleMode(0x00)
         if res['LLRET'] != OK:
            ScrCmds.statMsg("Result: %s" % res)
            ScrCmds.raiseException(14920, "Set Multiple Mode fail")
         # 7. Set Feature (includes: Sata mode, DIPM, and DMA setup)
         res = Set_UDMASpeed(txMode = 0x46, exc = 0)
         if res['LLRET'] != OK:
            ScrCmds.statMsg("Result: %s" % res)
            ScrCmds.raiseException(14920, 'Fail SetFeatures 0x03, 0x46')
         res = enable_DIPM(exc = 0)
         if res['LLRET'] != OK:
            ScrCmds.statMsg("Result: %s" % res)
            ScrCmds.raiseException(14920, 'Fail SetFeatures 0x10, 0x03')
         if DMASetupSupport:
            res = enable_DMASetup(exc = 0)
            if res['LLRET'] != OK:
               ScrCmds.statMsg("Result: %s" % res)
               ScrCmds.raiseException(14920, 'Fail SetFeatures 0x10, 0x02')
         # 8. Idle immediate
         res = ICmd.IdleImmediate()
         if res['LLRET'] != OK:
            ScrCmds.statMsg("Result: %s" % res)
            ScrCmds.raiseException(14920, "Idle Immediate fail")
         # 9. Write/Read FPDMA(NCQ)
         for i in xrange(random.randrange(5, 30)):
            scnt = self.getRandSectorCount()
            startLBA = self.getRandStartLBA(scnt)
            if random.randint(0, 1):
               if DEBUG: ScrCmds.statMsg("Write FPDMA: %10s, %10s, %10s" % \
                                         (startLBA, startLBA + scnt, scnt))
               CHelper().NCQSequentialWriteDMA(startLBA, startLBA + scnt, scnt, scnt, 14920)
            else:
               if DEBUG: ScrCmds.statMsg("Read FPDMA : %10s, %10s, %10s" % \
                                         (startLBA, startLBA + scnt, scnt))
               CHelper().NCQSequentialReadDMA(startLBA, startLBA + scnt, scnt, scnt, 14920)
         # Additional requirement to read back and compare last write FPDMA(NCQ)
         # location before long standby immediate
         if DEBUG: ScrCmds.statMsg("Read Cmp   : %10s, %10s, %10s" % \
                                   (last_startLBA, last_startLBA + last_scnt, last_scnt))
         CHelper().sequentialReadCmpDMAExt(last_startLBA, last_startLBA + last_scnt, \
                                           last_scnt, last_scnt, 1, 14920)
         # After reaching total test time, exit...
         if (time.time() - startTime) > (ttl_test_time * 60): break
         if testSwitch.virtualRun: break

      objPwrCtrl.powerCycle(5000, 12000, 10, 30)

   def getRandSectorCount(self):
      return random.randrange(1, 257)
      
   def getRandStartLBA(self, scnt):
      percentage = random.randrange(1, 11)
      if percentage <= 8:        # 80%
         return random.randrange(self.LBA_range_80[0], \
                                 (self.LBA_range_80[1] - scnt) + 1)
      else:                      # 20%
         return random.randrange(0, (self.endLBA - scnt) + 1)

###########################################################################################################
class CAcerS4(CState):
   """
   Customer Emulation Test (CET) for Acer S4
   """
   def __init__(self, dut, params={}):
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)

   def run(self):
      objPwrCtrl.powerCycle(5000, 12000, 10, 30)

      ttl_test_time = TP.prm_Acer_S4.get('TTL_TEST_TIME', 30)
      
      oIdentifyDevice = CIdentifyDevice()
      self.endLBA = oIdentifyDevice.getMaxLBA() - 1
      self.LBA_range_80 = TP.prm_Acer_S4.get('LBA_RANGE_80', [19531250, 156250000])
      if self.LBA_range_80[0] >= self.endLBA: self.LBA_range_80[0] = 0 
      if self.LBA_range_80[1] > self.endLBA: self.LBA_range_80[1] = self.endLBA
      
      rPtrn = CUtility.getRandomPattern(64)
      res = ICmd.FillBuffByte(WBF, rPtrn, 0, 512 * 256)
      if res['LLRET'] != OK:
         ScrCmds.statMsg("Result: %s" % res)
         ScrCmds.raiseException(14921, 'Fill Buff Byte fail')

      idDev = CIdentifyDevice()
      DMASetupSupport = idDev.ID["SATAFeatures"] & 0x04
      if DEBUG: ScrCmds.statMsg("SATA Features: 0x%x" % idDev.ID["SATAFeatures"])

      log_sect_per_track = self.dut.IdDevice['Physical Sector Size'] / self.dut.IdDevice['Logical Sector Size']
      if DEBUG: ScrCmds.statMsg("log_sect_per_track: %s" % log_sect_per_track)
      
      startTime = time.time()
      while True:
         if DEBUG: ScrCmds.statMsg("=" * 150)
         
         # 1. Write/Read FPMDA.
         for i in xrange(random.randrange(5, 30)):
            scnt = self.getRandSectorCount()
            startLBA = self.getRandStartLBA(scnt)
            if random.randint(0, 1):
               if DEBUG: ScrCmds.statMsg("Write FPDMA: %10s, %10s, %10s" % \
                                         (startLBA, startLBA + scnt, scnt))
               CHelper().NCQSequentialWriteDMA(startLBA, startLBA + scnt, scnt, scnt, 14921)
            else:
               if DEBUG: ScrCmds.statMsg("Read FPDMA : %10s, %10s, %10s" % \
                                         (startLBA, startLBA + scnt, scnt))
               CHelper().NCQSequentialReadDMA(startLBA, startLBA + scnt, scnt, scnt, 14921)
         # Saving last start LBA and sector count before idle immediate
         scnt = self.getRandSectorCount()
         startLBA = self.getRandStartLBA(scnt)
         if DEBUG: ScrCmds.statMsg("Write FPDMA: %10s, %10s, %10s" % \
                                   (startLBA, startLBA + scnt, scnt))
         CHelper().NCQSequentialWriteDMA(startLBA, startLBA + scnt, scnt, scnt, 14921)  
         last_scnt = scnt
         last_startLBA = startLBA
         # 2. Idle Immediate(0xE1).
         res = ICmd.IdleImmediate()
         if res['LLRET'] != OK:
            ScrCmds.statMsg("Result: %s" % res)
            ScrCmds.raiseException(14921, "Idle Immediate fail")
         # Additional requirement to read back and compare last write FPDMA(NCQ)
         # location before idle immediate
         if DEBUG: ScrCmds.statMsg("Read Cmp   : %10s, %10s, %10s" % \
                                   (last_startLBA, last_startLBA + last_scnt, last_scnt))
         CHelper().sequentialReadCmpDMAExt(last_startLBA, last_startLBA + last_scnt, \
                                           last_scnt, last_scnt, 1, 14921)
         # 3. Write DMA /Read DMA.
         for i in xrange(random.randrange(5, 30)):
            scnt = self.getRandSectorCount()
            startLBA = self.getRandStartLBA(scnt)
            if random.randint(0, 1):
               if DEBUG: ScrCmds.statMsg("Write DMA  : %10s, %10s, %10s" % \
                                         (startLBA, startLBA + scnt, scnt))
               CHelper().sequentialWriteDMAExt(startLBA, startLBA + scnt, scnt, scnt, 14921)
            else:
               if DEBUG: ScrCmds.statMsg("Read DMA   : %10s, %10s, %10s" % \
                                         (startLBA, startLBA + scnt, scnt))
               CHelper().sequentialReadDMAExt(startLBA, startLBA + scnt, scnt, scnt, 14921)
         # 4. Flush Cache.
         res = ICmd.FlushCache()
         if res['LLRET'] != OK:
            ScrCmds.statMsg("Result: %s" % res)
            ScrCmds.raiseException(14921, "Flush Cache fail")
         # 5a. Standby immediate (E0/FF sec cnt=00).
         res = ICmd.StandbyImmed()
         if res['LLRET'] != OK:
            ScrCmds.statMsg("Result: %s" % res)
            ScrCmds.raiseException(14921, "Standby Immediate fail")
         # 5b. Identify Drive
         ICmd.IdentifyDevice()
         # 6. Software reset
         res = ICmd.HardReset()
         if res['LLRET'] != OK:
            ScrCmds.statMsg("Result: %s" % res)
            ScrCmds.raiseException(14921, "Hard Reset fail")
         # 7. Set Feature
         res = Set_UDMASpeed(txMode = 0x46, exc = 0)
         if res['LLRET'] != OK:
            ScrCmds.statMsg("Result: %s" % res)
            ScrCmds.raiseException(14921, 'Fail SetFeatures 0x03, 0x46')
         res = enable_DIPM(exc = 0)
         if res['LLRET'] != OK:
            ScrCmds.statMsg("Result: %s" % res)
            ScrCmds.raiseException(14921, 'Fail SetFeatures 0x10, 0x03')
         if DMASetupSupport:
            res = enable_DMASetup(exc = 0)
            if res['LLRET'] != OK:
               ScrCmds.statMsg("Result: %s" % res)
               ScrCmds.raiseException(14921, 'Fail SetFeatures 0x10, 0x02')
         # 8. Software reset
         res = ICmd.HardReset()
         if res['LLRET'] != OK:
            ScrCmds.statMsg("Result: %s" % res)
            ScrCmds.raiseException(14921, "Hard Reset fail")
         # 9. Enable SMART and Check SMART.
         res = ICmd.SmartEnableOper()
         if res['LLRET'] != OK:
            ScrCmds.statMsg("Result: %s" % res)
            ScrCmds.raiseException(14921, "Smart Enable Oper fail")
         res = ICmd.SmartReturnStatus()
         if res['LLRET'] != OK:
            ScrCmds.statMsg("Result: %s" % res)
            ScrCmds.raiseException(14921, "Smart Return Status fail")
         # 10. Initialize device and Calibrate device.
         res = ICmd.InitDeviceParms(self.dut.imaxHead, log_sect_per_track)
         if res['LLRET'] != OK:
            ScrCmds.statMsg("Result: %s" % res)
            ScrCmds.raiseException(14921, "Init Device Parms fail")
         res = ICmd.Recalibrate()
         if res['LLRET'] != OK:
            ScrCmds.statMsg("Result: %s" % res)
            ScrCmds.raiseException(14921, "Recalibrate fail")
         # 11. Read DMA/Write DMA.
         for i in xrange(random.randrange(5, 30)):
            scnt = self.getRandSectorCount()
            startLBA = self.getRandStartLBA(scnt)
            if random.randint(0, 1):
               if DEBUG: ScrCmds.statMsg("Write DMA  : %10s, %10s, %10s" % \
                                         (startLBA, startLBA + scnt, scnt))
               CHelper().sequentialWriteDMAExt(startLBA, startLBA + scnt, scnt, scnt, 14921)
            else:
               if DEBUG: ScrCmds.statMsg("Read DMA   : %10s, %10s, %10s" % \
                                         (startLBA, startLBA + scnt, scnt))
               CHelper().sequentialReadDMAExt(startLBA, startLBA + scnt, scnt, scnt, 14921)
         # 12. Identify 
         ICmd.IdentifyDevice()
         # 13. Set multiple mode (PIO).
         res = ICmd.SetMultipleMode(0x10)
         if res['LLRET'] != OK:
            ScrCmds.statMsg("Result: %s" % res)
            ScrCmds.raiseException(14921, "Set Multiple Mode fail")
         # 14. Set Feature.
         res = Set_UDMASpeed(txMode = 0x46, exc = 0)
         if res['LLRET'] != OK:
            ScrCmds.statMsg("Result: %s" % res)
            ScrCmds.raiseException(14921, 'Fail SetFeatures 0x03, 0x46')
         res = enable_DIPM(exc = 0)
         if res['LLRET'] != OK:
            ScrCmds.statMsg("Result: %s" % res)
            ScrCmds.raiseException(14921, 'Fail SetFeatures 0x10, 0x03')
         if DMASetupSupport:
            res = enable_DMASetup(exc = 0)
            if res['LLRET'] != OK:
               ScrCmds.statMsg("Result: %s" % res)
               ScrCmds.raiseException(14921, 'Fail SetFeatures 0x10, 0x02')
         # 14a. Idle immediate
         res = ICmd.IdleImmediate()
         if res['LLRET'] != OK:
            ScrCmds.statMsg("Result: %s" % res)
            ScrCmds.raiseException(14921, "Idle Immediate fail")
         # 15. Write/Read FPDMA.
         for i in xrange(random.randrange(5, 30)):
            scnt = self.getRandSectorCount()
            startLBA = self.getRandStartLBA(scnt)
            if random.randint(0, 1):
               if DEBUG: ScrCmds.statMsg("Write FPDMA: %10s, %10s, %10s" % \
                                         (startLBA, startLBA + scnt, scnt))
               CHelper().NCQSequentialWriteDMA(startLBA, startLBA + scnt, scnt, scnt, 14921)
            else:
               if DEBUG: ScrCmds.statMsg("Read FPDMA : %10s, %10s, %10s" % \
                                         (startLBA, startLBA + scnt, scnt))
               CHelper().NCQSequentialReadDMA(startLBA, startLBA + scnt, scnt, scnt, 14921)
         # After reaching total test time, exit...
         if (time.time() - startTime) > (ttl_test_time * 60): break
         if testSwitch.virtualRun: break

      objPwrCtrl.powerCycle(5000, 12000, 10, 30)

   def getRandSectorCount(self):
      return random.randrange(1, 257)
      
   def getRandStartLBA(self, scnt):
      percentage = random.randrange(1, 11)
      if percentage <= 8:        # 80%
         return random.randrange(self.LBA_range_80[0], \
                                 (self.LBA_range_80[1] - scnt) + 1)
      else:                      # 20%
         return random.randrange(0, (self.endLBA - scnt) + 1)

###########################################################################################################
class CAcerS5(CState):
   """
   Customer Emulation Test (CET) for Acer S5
   """
   def __init__(self, dut, params={}):
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)

   def run(self):
      objPwrCtrl.powerCycle(5000, 12000, 10, 30)

      ttl_test_time = TP.prm_Acer_S5.get('TTL_TEST_TIME', 30)
      
      oIdentifyDevice = CIdentifyDevice()
      self.endLBA = oIdentifyDevice.getMaxLBA() - 1
      self.LBA_range_80 = TP.prm_Acer_S5.get('LBA_RANGE_80', [19531250, 156250000])
      if self.LBA_range_80[0] >= self.endLBA: self.LBA_range_80[0] = 0 
      if self.LBA_range_80[1] > self.endLBA: self.LBA_range_80[1] = self.endLBA
      
      rPtrn = CUtility.getRandomPattern(64)
      res = ICmd.FillBuffByte(WBF, rPtrn, 0, 512 * 256)
      if res['LLRET'] != OK:
         ScrCmds.statMsg("Result: %s" % res)
         ScrCmds.raiseException(14922, 'Fill Buff Byte fail')

      log_sect_per_track = self.dut.IdDevice['Physical Sector Size'] / self.dut.IdDevice['Logical Sector Size']
      if DEBUG: ScrCmds.statMsg("log_sect_per_track: %s" % log_sect_per_track)

      startTime = time.time()
      while True:
         if DEBUG: ScrCmds.statMsg("=" * 150)
         # 1. Write/Read FPMDA.
         for i in xrange(random.randrange(5, 30)):
            scnt = self.getRandSectorCount()
            startLBA = self.getRandStartLBA(scnt)
            if random.randint(0, 1):
               if DEBUG: ScrCmds.statMsg("Write FPDMA: %10s, %10s, %10s" % \
                                         (startLBA, startLBA + scnt, scnt))
               CHelper().NCQSequentialWriteDMA(startLBA, startLBA + scnt, scnt, scnt, 14922)
            else:
               if DEBUG: ScrCmds.statMsg("Read FPDMA : %10s, %10s, %10s" % \
                                         (startLBA, startLBA + scnt, scnt))
               CHelper().NCQSequentialReadDMA(startLBA, startLBA + scnt, scnt, scnt, 14922)
         scnt = self.getRandSectorCount()
         startLBA = self.getRandStartLBA(scnt)
         if DEBUG: ScrCmds.statMsg("Write FPDMA: %10s, %10s, %10s" % \
                                   (startLBA, startLBA + scnt, scnt))
         CHelper().NCQSequentialWriteDMA(startLBA, startLBA + scnt, scnt, scnt, 14922)
         last_scnt = scnt
         last_startLBA = startLBA
         # 2. Flush Cache.
         res = ICmd.FlushCache()
         if res['LLRET'] != OK:
            ScrCmds.statMsg("Result: %s" % res)
            ScrCmds.raiseException(14922, "Flush Cache fail")
         # 3. Sleep for 5 sec.
         if DEBUG: ScrCmds.statMsg("Sleep for 5 seconds")
         time.sleep(5)
         # 4. Set Feature (disable Software Setting).
         res = disable_SWSetting(exc = 0)
         if res['LLRET'] != OK:
            ScrCmds.statMsg("Result: %s" % res)
            ScrCmds.raiseException(14922, 'Fail SetFeatures 0x90, 0x06')
         # 5. Identify Device.
         ICmd.IdentifyDevice()
         # 6. Security Freeze Lock.
         res = ICmd.SecurityFreezeLock()
         if res['LLRET'] != OK:
            ScrCmds.statMsg("Result: %s" % res)
            ScrCmds.raiseException(14922, "Security Freeze Lock fail")
         # 7. Software reset.
         try:
            res = ICmd.HardReset()
         except:
            ScrCmds.statMsg("Result: %s" % res)
            ScrCmds.raiseException(14922, "Hard Reset fail")
         # 8. Set Feature (Set UDMA Speed).
         res = Set_UDMASpeed(txMode = 0x0C, exc = 0)
         if res['LLRET'] != OK:
            ScrCmds.statMsg("Result: %s" % res)
            ScrCmds.raiseException(14922, 'Fail SetFeatures 0x03, 0x0C')
         res = Set_UDMASpeed(txMode = 0x45, exc = 0)
         if res['LLRET'] != OK:
            ScrCmds.statMsg("Result: %s" % res)
            ScrCmds.raiseException(14922, 'Fail SetFeatures 0x03, 0x45')
         # 9. Set multiple mode.
         try:
            res = ICmd.SetMultipleMode(0x08)
         except:
            ScrCmds.statMsg("Result: %s" % res)
            ScrCmds.raiseException(14922, "Set Multiple Mode fail")
         # 10. Enable SMART and Enable Attribute Autosave.
         try:
            res = ICmd.SmartEnableOper()
         except:
            ScrCmds.statMsg("Result: %s" % res)
            ScrCmds.raiseException(14922, "Smart Enable Oper fail")
         try:   
            res = ICmd.SmartEDAutoSave(0xF1)
         except:
            ScrCmds.statMsg("Result: %s" % res)
            ScrCmds.raiseException(14922, "Smart Enable Attribute Autosave fail")
         # 11. Software reset.
         try:
            res = ICmd.HardReset()
         except:
            ScrCmds.statMsg("Result: %s" % res)
            ScrCmds.raiseException(14922, "Hard Reset fail")
         # 12. Initialize device and Calibrate device.
         try:
            res = ICmd.InitDeviceParms(self.dut.imaxHead, log_sect_per_track)
         except:
            ScrCmds.statMsg("Result: %s" % res)
            ScrCmds.raiseException(14922, "Init Device Parms fail")
         try:   
            res = ICmd.Recalibrate()
         except:
            ScrCmds.statMsg("Result: %s" % res)
            ScrCmds.raiseException(14922, "Recalibrate fail")
         # 13. Set multiple mode.
         try:
            res = ICmd.SetMultipleMode(0x08)
         except:
            ScrCmds.statMsg("Result: %s" % res)
            ScrCmds.raiseException(14922, "Set Multiple Mode fail")
         # Additional requirement to read back and compare last write FPDMA(NCQ)
         # location
         if DEBUG: ScrCmds.statMsg("Read Cmp   : %10s, %10s, %10s" % \
                                   (last_startLBA, last_startLBA + last_scnt, last_scnt))
         CHelper().sequentialReadCmpDMAExt(last_startLBA, last_startLBA + last_scnt, \
                                           last_scnt, last_scnt, 1, 14922)
         # 14. Read DMA.
         for i in xrange(random.randrange(5, 30)):
            scnt = self.getRandSectorCount()
            startLBA = self.getRandStartLBA(scnt)
            if DEBUG: ScrCmds.statMsg("Read DMA   : %10s, %10s, %10s" % \
                                      (startLBA, startLBA + scnt, scnt))
            CHelper().sequentialReadDMAExt(startLBA, startLBA + scnt, scnt, scnt, 14922)
         # After reaching total test time, exit...
         if (time.time() - startTime) > (ttl_test_time * 60): break
         if testSwitch.virtualRun: break

      objPwrCtrl.powerCycle(5000, 12000, 10, 30)

   def getRandSectorCount(self):
      return random.randrange(1, 257)
      
   def getRandStartLBA(self, scnt):
      percentage = random.randrange(1, 11)
      if percentage <= 8:        # 80%
         return random.randrange(self.LBA_range_80[0], \
                                 (self.LBA_range_80[1] - scnt) + 1)
      else:                      # 20%
         return random.randrange(0, (self.endLBA - scnt) + 1)

###########################################################################################################
class CHP_DST_PFM(CState):
   """
   HP DST Performance Test.
   """
   def __init__(self, dut, params={}):
      depList = []
      CState.__init__(self, dut, depList)

   def run(self):
      # Power on drive with 4.8 (-4%) Volts instead of 5 Volts.
      objPwrCtrl.powerCycle(4800, 12000, 10, 30)
      # Interface command time out is 5 seconds.
      ICmd.SetIntfTimeout(TP.prm_HP_DST_PFM.get('IFACE_CMD_TO', 5) * 1000)

      # SMART Enable Operation (Cmd:B0h, Device:A0h, LBA:C24F00h, Feature:D8h).
      res = ICmd.SmartEnableOper()
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14931, "SmartEnableOper() function is failed.")
      # SMART Read Data (Cmd:B0h, Device:A0h, LBA:C24F01h, Feature:D0h).
      res = ICmd.SmartReadData()
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14931, "SmartReadData function is failed.")
      res = ICmd.GetBuffer(RBF, 0, 512)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14931, "GetBuffer function is failed.")
      # Get SMART Data buffer offset 372 (0x174)
      # Short self-test routine recommended polling time (in minutes).
      shortRecomPollTime = ord(res['DATA'][372])
      ScrCmds.statMsg("SMART Data Offset 372 (short time in minutes)   : %s" % shortRecomPollTime)
      # Get SMART Data buffer offset 373 (0x175)
      # Extended self-test routine recommended polling time (in minutes).
      extRecomPollTime = ord(res['DATA'][373])
      ScrCmds.statMsg("SMART Data Offset 373 (extended time in minutes): %s" % extRecomPollTime)

      self.expcLinPtg = 10             # Expected Linear Percentage
      self.lastLinPtg = 0              # Last Linear Percentage
      self.linWarnNum = 0              # Number of Linearity Warnings
      self.linWarnMax = 2              # Maximum Linearity Warnings
      self.invSTTWarnNum = 0           # Number of Invalid STT Warnings
      self.invSTTWarnMax = 1           # Maximum Invalid STT Warnings

      self.ttDST = 0                   # Test Time of DST without Interrupt
      self.ttDSTInt = 0                # Test Time of DST with Interrupt
      self.ttIntDST = 0                # Test Time of Interrupt DST Active
      self.ttInt = 0                   # Test Time of Interrupt DST Inactive

      # Run Short DST Test.
      self.shortDSTTest(shortRecomPollTime)
      # Run Extended DST Test.
      self.extDSTTest(extRecomPollTime)
      # Run Extended with Interrupt DST Test.
      self.extIntDSTTest()
      
      # Power on drive with default 5 Volts.
      ICmd.SetIntfTimeout(TP.prm_IntfTest["Default CPC Cmd Timeout"] * 1000)
      # Set interface command time out to default.
      objPwrCtrl.powerCycle(5000, 12000, 10, 30)

   def shortDSTTest(self, shortRecomPollTime):
      ScrCmds.statMsg("-------------------- Running Short DST Test ---")
      # Set expcLinPtg (Expected Linear Percentage) to 10 (10%).
      self.expcLinPtg = 10             # Expected Linear Percentage
      # Set lastLinPtg (Last Linear Percentage) to 0 (0%).
      self.lastLinPtg = 0              # Last Linear Percentage
      # Set Number of Linearity Warnings (linWarnNum) to 0 with maximum 2 (linWarnMax).
      self.linWarnNum = 0              # Number of Linearity Warnings
      self.linWarnMax = 2              # Maximum Linearity Warnings
      # Set Number of Invalid STT Warnings (invSTTWarnNum) to 0 with maximum 1 (invSTTWarnMax).
      self.invSTTWarnNum = 0           # Number of Invalid STT Warnings
      self.invSTTWarnMax = 1           # Maximum Invalid STT Warnings
      # Delay per Loop (dlyPerLoop) = ((shortRecomPollTime * 60 seconds) / 10) seconds.
      dlyPerLoop = (shortRecomPollTime * 60) / 10  # Delay per loop (in seconds)

      # Running test...
      ScrCmds.statMsg("      exeStatus" + \
                      "     expcLinPtg" + \
                      "     lastLinPtg" + \
                      "     linWarnNum" + \
                      "     linWarnMax" + \
                      "  invSTTWarnNum" + \
                      "  invSTTWarnMax")
      startTime = time.time()
      # Execute SMART Short self-test routine immediately in off-line mode
      # (Cmd:B0h, Device:A0h, LBA:C24F01h, Feature:D4h).
      res = ICmd.SmartOffLineImmed(0x01)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14931, "SmartOffLineImmed(0x01) function is failed.")
      while True:
         time.sleep(dlyPerLoop)
         # SMART Read Data (Cmd:B0h, Device:A0h, LBA:C24F01h, Feature:D0h).
         res = ICmd.SmartReadData()
         if res['LLRET'] != OK:
            ScrCmds.raiseException(14931, "SmartReadData function is failed.")
         res = ICmd.GetBuffer(RBF, 0, 512)
         if res['LLRET'] != OK:
            ScrCmds.raiseException(14931, "GetBuffer function is failed.")
         # Get SMART Data buffer offset 363 (Self-test execution status byte 
         # (exeStatus)).
         exeStatus = ord(res['DATA'][363])
         if testSwitch.virtualRun: exeStatus = 0xF0
         ScrCmds.statMsg("%13s%15s%15s%15s%15s%15s%15s" % \
                         (hex(exeStatus), self.expcLinPtg, self.lastLinPtg, \
                          self.linWarnNum, self.linWarnMax, \
                          self.invSTTWarnNum, self.invSTTWarnMax))
         if exeStatus == 0x00: break
         self.checkStatus(exeStatus)
         if testSwitch.virtualRun: break
      endTime = time.time()
      testTime = endTime - startTime
      ScrCmds.statMsg("Test time (in seconds): %s" % testTime)

      # If Number of Linearity Warnings (linWarnNum) more than maximum 
      # (linWarnMax) that is allowed then Fail Not Linear.
      if self.linWarnNum > self.linWarnMax:
         if testSwitch.virtualRun:
            ScrCmds.statMsg("VE FAIL: Short DST Test Failed: Linearity Warnings.")
         else:
            ScrCmds.raiseException(14931, "Short DST Test Failed: Linearity Warnings.")
      # If Test Time smaller than 90% or bigger than 110% of recommended polling 
      # time then fail for too short or too long.
      if testTime < (dlyPerLoop * 9):
         if testSwitch.virtualRun:
            ScrCmds.statMsg("VE FAIL: Short DST Test Failed: Test time is too short.")
         else:
            ScrCmds.raiseException(14931, "Short DST Test Failed: Test time is too short.")
      if testTime > (dlyPerLoop * 11):
         if testSwitch.virtualRun:
            ScrCmds.statMsg("VE FAIL: Short DST Test Failed: Test time is too long.")
         else:
            ScrCmds.raiseException(14931, "Short DST Test Failed: Test time is too long.")

   def extDSTTest(self, extRecomPollTime):
      ScrCmds.statMsg("-------------------- Running Long DST Test ---")
      # Set expcLinPtg (Expected Linear Percentage) to 10 (10%).
      self.expcLinPtg = 10             # Expected Linear Percentage
      # Set lastLinPtg (Last Linear Percentage) to 0 (0%).
      self.lastLinPtg = 0              # Last Linear Percentage
      # Set Number of Linearity Warnings (linWarnNum) to 0 with maximum 2 (linWarnMax).
      self.linWarnNum = 0              # Number of Linearity Warnings
      self.linWarnMax = 2              # Maximum Linearity Warnings
      # Set Number of Invalid STT Warnings (invSTTWarnNum) to 0 with maximum 1 (invSTTWarnMax).
      self.invSTTWarnNum = 0           # Number of Invalid STT Warnings
      self.invSTTWarnMax = 1           # Maximum Invalid STT Warnings
      # Delay per Loop (dlyPerLoop) = ((extRecomPollTime * 60 seconds) / 20) seconds.
      dlyPerLoop = (extRecomPollTime * 60) / 20    # Delay per loop (in seconds)

      # Running test...
      ScrCmds.statMsg("      exeStatus" + \
                      "     expcLinPtg" + \
                      "     lastLinPtg" + \
                      "     linWarnNum" + \
                      "     linWarnMax" + \
                      "  invSTTWarnNum" + \
                      "  invSTTWarnMax")
      startTime = time.time()
      # Execute SMART Extended self-test routine immediately in off-line mode. 
      # (Cmd:B0h, Device:A0h, LBA:C24F02h, Feature:D4h).
      res = ICmd.SmartOffLineImmed(0x02)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14931, "SmartOffLineImmed(0x02) function is failed.")
      while True:
         # For first and last loop, delay for dlyPerLoop. Other than that, 
         # delay for (dlyPerLoop * 2).
         if (self.expcLinPtg <= 10) or (self.expcLinPtg > 100): 
            time.sleep(dlyPerLoop)
         else:
            time.sleep(dlyPerLoop * 2)
         # SMART Read Data (Cmd:B0h, Device:A0h, LBA:C24F01h, Feature:D0h).
         res = ICmd.SmartReadData()
         if res['LLRET'] != OK:
            ScrCmds.raiseException(14931, "SmartReadData function is failed.")
         res = ICmd.GetBuffer(RBF, 0, 512)
         if res['LLRET'] != OK:
            ScrCmds.raiseException(14931, "GetBuffer function is failed.")
         # Get SMART Data buffer offset 363 (Self-test execution status byte 
         # (exeStatus)).
         exeStatus = ord(res['DATA'][363])
         if testSwitch.virtualRun: exeStatus = 0xF0
         ScrCmds.statMsg("%13s%15s%15s%15s%15s%15s%15s" % \
                         (hex(exeStatus), self.expcLinPtg, self.lastLinPtg, \
                          self.linWarnNum, self.linWarnMax, \
                          self.invSTTWarnNum, self.invSTTWarnMax))
         if exeStatus == 0x00: break
         self.checkStatus(exeStatus)
         if testSwitch.virtualRun: break
      endTime = time.time()
      testTime = endTime - startTime
      ScrCmds.statMsg("Test time (in seconds): %s" % testTime)
      # Save Test Time as Test Time of DST without Interrupt (ttDST).
      self.ttDST = testTime

      # If Number of Linearity Warnings (linWarnNum) more than maximum  
      # (linWarnMax) that is allowed then Fail Not Linear.
      if self.linWarnNum > self.linWarnMax:
         if testSwitch.virtualRun:
            ScrCmds.statMsg("VE FAIL: Extended DST Test Failed: Linearity Warnings.")
         else:
            ScrCmds.raiseException(14931, "Extended DST Test Failed: Linearity Warnings.")
      # If Test Time > (((dlyPerLoop * 2) * 11) + 120 seconds then Fail Too Long.
      if testTime > (((dlyPerLoop * 2) * 11) + 120):
         if testSwitch.virtualRun:
            ScrCmds.statMsg("VE FAIL: Extended DST Test Failed: Test time is too long.")
         else:
            ScrCmds.raiseException(14931, "Extended DST Test Failed: Test time is too long.")

   def extIntDSTTest(self):
      if testSwitch.virtualRun: self.ttDST = 20
      ScrCmds.statMsg("-------------------- Running Extended with Interrupt DST Test ---")
      self.cmdIntNum = 0               # Number of Command Interrupt
      # Set Number of Invalid STT Warnings (invSTTWarnNum) to 0 with maximum 1 (invSTTWarnMax).
      self.invSTTWarnNum = 0           # Number of Invalid STT Warnings
      self.invSTTWarnMax = 1           # Maximum Invalid STT Warnings
      # Delay per Loop (dlyPerLoop) = (ttDST / 10) seconds.
      dlyPerLoop = self.ttDST / 10     # Delay per loop (in seconds)
      
      # Get Maximum LBA
      oIdentifyDevice = CIdentifyDevice()
      self.maxLBA = oIdentifyDevice.getMaxLBA()
      # Clear Write Buffer
      res = ICmd.ClearBinBuff(WBF)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14931, "Clear Write Buffer is failed.")

      # ------------------------------------------------- DST with Interrupt ---
      ScrCmds.statMsg("*** Running: DST with Interrupt.")
      # Get Command Interrupt Random Delay (cmdIntRndDly) from 1 to 10 seconds.
      cmdIntRndDly = random.randrange(1, 11)
      # Running test...
      ScrCmds.statMsg("           flow" + \
                      "      exeStatus" + \
                      "     dlyPerLoop" + \
                      "   cmdIntRndDly" + \
                      "      cmdIntNum" + \
                      "     rwTestTime" + \
                      "          ttDST" + \
                      "       ttDSTInt" + \
                      "       ttIntDST" + \
                      "          ttInt" + \
                      "  invSTTWarnNum" + \
                      "  invSTTWarnMax")
      ScrCmds.statMsg("%13s%15s%15.3f%15.3f%15s%15s%15.3f%15.3f%15.3f%15.3f%15s%15s" % \
                      ("init", '-', dlyPerLoop, cmdIntRndDly, self.cmdIntNum, '-', 
                       self.ttDST, self.ttDSTInt, self.ttIntDST, self.ttInt,
                       self.invSTTWarnNum, self.invSTTWarnMax))
      startTime = time.time()
      # Execute SMART Extended self-test routine immediately in off-line mode 
      # (Cmd:B0h, Device:A0h, LBA:C24F02h, Feature:D4h).
      res = ICmd.SmartOffLineImmed(0x02)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14931, "SmartOffLineImmed(0x02) function is failed.")
      while True:
         # Delay until either/both dlyPerLoop or/and cmdIntRndDly is/are zero.
         if cmdIntRndDly <= dlyPerLoop:
            time.sleep(cmdIntRndDly)
            dlyPerLoop -= cmdIntRndDly
            # Get new Command Interrupt Random Delay (cmdIntRndDly) from 1 to 10
            # seconds.
            cmdIntRndDly = random.randrange(1, 11)

            rwStartTime = time.time()
            # If Number of Command Interrupt (cmdIntNum) is even then run 
            # Write DMA Extended otherwise run Read DMA Extended.
            minLBA  = 0
            maxLBA  = self.maxLBA - 8
            minSCnt = 8
            maxSCnt = 8
            loopCnt = 1
            if self.cmdIntNum % 2:
               # Read DMA Extended
               rwMode = 'R'
               res = ICmd.RandomReadDMAExt(minLBA, maxLBA, minSCnt, maxSCnt, loopCnt)
               if res['LLRET'] != OK:
                  ScrCmds.statMsg("Result: %s" % res)
                  ScrCmds.statMsg(" - Minimum LBA          : %s" % minLBA)
                  ScrCmds.statMsg(" - Maximum LBA          : %s" % maxLBA)
                  ScrCmds.statMsg(" - Minimum Sector Count : %s" % minSCnt)
                  ScrCmds.statMsg(" - Maximum Sector Count : %s" % maxSCnt)
                  ScrCmds.statMsg(" - Loop Count           : %s" % loopCnt)
                  ScrCmds.raiseException(14931, "Random Read DMA is failed!")
            else:
               # Write DMA Extended
               rwMode = 'W'
               res = ICmd.RandomWriteDMAExt(minLBA, maxLBA, minSCnt, maxSCnt, loopCnt)
               if res['LLRET'] != OK:
                  ScrCmds.statMsg("Result: %s" % res)
                  ScrCmds.statMsg(" - Minimum LBA          : %s" % minLBA)
                  ScrCmds.statMsg(" - Maximum LBA          : %s" % maxLBA)
                  ScrCmds.statMsg(" - Minimum Sector Count : %s" % minSCnt)
                  ScrCmds.statMsg(" - Maximum Sector Count : %s" % maxSCnt)
                  ScrCmds.statMsg(" - Loop Count           : %s" % loopCnt)
                  ScrCmds.raiseException(14931, "Random Write DMA is failed!")
            rwEndTime = time.time()
            rwTestTime = rwEndTime - rwStartTime
            self.ttIntDST += rwTestTime

            # Add Number of Command Interrupt (cmdIntNum) with one.
            self.cmdIntNum += 1
            if DEBUG:
               ScrCmds.statMsg("%13s%15s%15.3f%15.3f%15s%15.3f%15.3f%15.3f%15.3f%15.3f%15s%15s" % \
                               ("IntCmd-%s" % rwMode, '-', dlyPerLoop, cmdIntRndDly, self.cmdIntNum, rwTestTime, 
                                self.ttDST, self.ttDSTInt, self.ttIntDST, self.ttInt,
                                self.invSTTWarnNum, self.invSTTWarnMax))

         else:
            time.sleep(dlyPerLoop)
            cmdIntRndDly -= dlyPerLoop
            # Set back dlyPerLoop to (ttDST / 10).
            dlyPerLoop = self.ttDST / 10  # Delay per loop (in seconds)

            # SMART Read Data (Cmd:B0h, Device:A0h, LBA:C24F01h, Feature:D0h).
            res = ICmd.SmartReadData()
            if res['LLRET'] != OK:
               ScrCmds.raiseException(14931, "SmartReadData function is failed.")
            res = ICmd.GetBuffer(RBF, 0, 512)
            if res['LLRET'] != OK:
               ScrCmds.raiseException(14931, "GetBuffer function is failed.")
            # Get SMART Data buffer offset 363 (Self-test execution status byte 
            # (exeStatus)).
            exeStatus = ord(res['DATA'][363])
            if testSwitch.virtualRun: exeStatus = 0x00
            ScrCmds.statMsg("%13s%15s%15.3f%15.3f%15s%15s%15.3f%15.3f%15.3f%15.3f%15s%15s" % \
                            ("DST", hex(exeStatus), dlyPerLoop, cmdIntRndDly, self.cmdIntNum, '-', 
                             self.ttDST, self.ttDSTInt, self.ttIntDST, self.ttInt,
                             self.invSTTWarnNum, self.invSTTWarnMax))
            if exeStatus == 0x00: break
            # If Self-test execution status (exeStatus) is still equal to 0xF0   
            # after sometime then add Number of Invalid STT Warnings 
            # (invSTTWarnNum) with 1.
            if exeStatus == 0xF0: self.invSTTWarnNum += 1
            # If Number of Invalid STT Warnings (invSTTWarnNum) more than maximum 
            # (invSTTWarnMax) that is allowed then Fail Invalid Status.
            if self.invSTTWarnNum > self.invSTTWarnMax:
               if testSwitch.virtualRun:
                  ScrCmds.statMsg("VE FAIL: Check Status Failed: Execution status = 0xF0.")
               else:
                  ScrCmds.raiseException(14931, "Check Status Failed: Execution status = 0xF0.")
            # If offset 363 (Self-test execution status byte (exeStatus)) < 0xF0  
            # then Fail DST.
            if exeStatus < 0xF0:
               if testSwitch.virtualRun:
                  ScrCmds.statMsg("VE FAIL: Check Status Failed: Execution status < 0xF0.")
               else:
                  ScrCmds.raiseException(14931, "Check Status Failed: Execution status < 0xF0.")

      endTime = time.time()
      testTime = endTime - startTime
      ScrCmds.statMsg("Test time (in seconds): %s" % testTime)
      # Save Test Time as Test Time of DST with Interrupt (ttDSTInt).
      self.ttDSTInt = testTime
      # Execute Flush Cache (0xE7) command.
      res = ICmd.FlushCache()
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14931, "Flush Cache is failed.")

      # --------------------------------------------- Interrupt DST Inactive ---
      ScrCmds.statMsg("*** Running: Interrupt DST Inactive.")
      for loopCtr in xrange(self.cmdIntNum):
         # Command Interrupt Random Delay (cmdIntRndDly) from 1 to 10 seconds.
         cmdIntRndDly = random.randrange(1, 11)
         time.sleep(cmdIntRndDly)

         rwStartTime = time.time()
         # Call Random Operation algorithm. Add read/write command time into 
         # Test Time of Interrupt DST Inactive (ttInt).
         minLBA  = 0
         maxLBA  = self.maxLBA - 8
         minSCnt = 8
         maxSCnt = 8
         loopCnt = 1
         if loopCtr % 2:
            # Read DMA Extended
            rwMode = 'R'
            res = ICmd.RandomReadDMAExt(minLBA, maxLBA, minSCnt, maxSCnt, loopCnt)
            if res['LLRET'] != OK:
               ScrCmds.statMsg("Result: %s" % res)
               ScrCmds.statMsg(" - Minimum LBA          : %s" % minLBA)
               ScrCmds.statMsg(" - Maximum LBA          : %s" % maxLBA)
               ScrCmds.statMsg(" - Minimum Sector Count : %s" % minSCnt)
               ScrCmds.statMsg(" - Maximum Sector Count : %s" % maxSCnt)
               ScrCmds.statMsg(" - Loop Count           : %s" % loopCnt)
               ScrCmds.raiseException(14931, "Random Read DMA is failed!")
         else:
            # Write DMA Extended
            rwMode = 'W'
            res = ICmd.RandomWriteDMAExt(minLBA, maxLBA, minSCnt, maxSCnt, loopCnt)
            if res['LLRET'] != OK:
               ScrCmds.statMsg("Result: %s" % res)
               ScrCmds.statMsg(" - Minimum LBA          : %s" % minLBA)
               ScrCmds.statMsg(" - Maximum LBA          : %s" % maxLBA)
               ScrCmds.statMsg(" - Minimum Sector Count : %s" % minSCnt)
               ScrCmds.statMsg(" - Maximum Sector Count : %s" % maxSCnt)
               ScrCmds.statMsg(" - Loop Count           : %s" % loopCnt)
               ScrCmds.raiseException(14931, "Random Write DMA is failed!")
         rwEndTime = time.time()
         rwTestTime = rwEndTime - rwStartTime
         self.ttInt += rwTestTime
         if DEBUG:
            ScrCmds.statMsg("%13s%15s%15s%15.3f%15s%15.3f%15.3f%15.3f%15.3f%15.3f%15s%15s" % \
                            ("IntCmd-%s" % rwMode, '-', '-', cmdIntRndDly, self.cmdIntNum, rwTestTime, 
                             self.ttDST, self.ttDSTInt, self.ttIntDST, self.ttInt,
                             '-', '-'))

      if testSwitch.virtualRun:
         self.cmdIntNum = 836
         self.ttDST = 4675.520
         self.ttDSTInt = 4764.190
         self.ttIntDST = 86.777
         self.ttInt = 71.402
      ScrCmds.statMsg("Number of Command Interrupt (cmdIntNum) : %s" % self.cmdIntNum)
      ScrCmds.statMsg("DST without Interrupt (ttDST)           : %10.3f seconds" % self.ttDST)
      ScrCmds.statMsg("DST with Interrupt (ttDSTInt)           : %10.3f seconds" % self.ttDSTInt)
      ScrCmds.statMsg("Interrupt DST Active (ttIntDST)         : %10.3f seconds" % self.ttIntDST)
      ScrCmds.statMsg("Interrupt DST Inactive (ttInt)          : %10.3f seconds" % self.ttInt)

      # If ttIntDST is smaller than ttInt then Fail Total Interrupt Command Time.
      #if self.ttIntDST < self.ttInt:      
      #   if testSwitch.virtualRun:
      #      ScrCmds.statMsg("VE FAIL: Extended Interrupt DST Test Failed: Total Interrupt Command Time.")
      #   else:
      #      ScrCmds.raiseException(14931, "Extended Interrupt DST Test Failed: Total Interrupt Command Time.")
      # DST Response Time (ttDSTResponse) = (ttIntDST - ttInt) / cmdIntNum.
      # If DST Response Time (ttDSTResponse) bigger than 2 seconds then 
      # Fail Response Time.
      ttDSTResponse = (self.ttIntDST - self.ttInt) / self.cmdIntNum
      if ttDSTResponse > 2:
         if testSwitch.virtualRun:
            ScrCmds.statMsg("VE FAIL: Extended Interrupt DST Test Failed: Response Time.")
         else:
            ScrCmds.raiseException(14931, "Extended Interrupt DST Test Failed: Response Time.")

      # If ttDSTInt is smaller than ttDST then Fail Total DST Time.
      if self.ttDSTInt < self.ttDST:
         if testSwitch.virtualRun:
            ScrCmds.statMsg("VE FAIL: Extended Interrupt DST Test Failed: Total DST Time.")
         else:
            ScrCmds.raiseException(14931, "Extended Interrupt DST Test Failed: Total DST Time.")
      # DST Resume Time (ttDSTResume) = ((ttDSTInt - ttDST) - ttInt) / cmdIntNum.
      # If DST Resume Time (ttDSTResume) bigger than 2 seconds then 
      # Fail Resume Time.
      ttDSTResume = ((self.ttDSTInt - self.ttDST) - self.ttInt) / self.cmdIntNum
      if ttDSTResume > 2:
         if testSwitch.virtualRun:
            ScrCmds.statMsg("VE FAIL: Extended Interrupt DST Test Failed: Resume Time.")
         else:
            ScrCmds.raiseException(14931, "Extended Interrupt DST Test Failed: Resume Time.")

      # Execute Flush Cache (0xE7) command.
      res = ICmd.FlushCache()
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14931, "Flush Cache is failed.")

   def checkStatus(self, exeStatus):
      # If offset 363 (Self-test execution status byte (exeStatus)) < 0xF0 then 
      # Fail DST.
      if exeStatus < 0xF0:
         if testSwitch.virtualRun:
            ScrCmds.statMsg("VE FAIL: Check Status Failed: Execution status < 0xF0.")
         else:
            ScrCmds.raiseException(14931, "Check Status Failed: Execution status < 0xF0.")
      # If expcLinPtg > 10 (10%) then do "Check Invalid DST".
      if self.expcLinPtg > 10:
         # If Self-test execution status (exeStatus) is still equal to 0xF0   
         # after sometime then add Number of Invalid STT Warnings 
         # (invSTTWarnNum) with 1.
         if exeStatus == 0xF0: self.invSTTWarnNum += 1
         # If Number of Invalid STT Warnings (invSTTWarnNum) more than maximum 
         # (invSTTWarnMax) that is allowed then Fail Invalid Status.
         if self.invSTTWarnNum > self.invSTTWarnMax:
            if testSwitch.virtualRun:
               ScrCmds.statMsg("VE FAIL: Check Status Failed: Execution status = 0xF0.")
            else:
               ScrCmds.raiseException(14931, "Check Status Failed: Execution status = 0xF0.")
      # Convert form Self-test execution status to curLinPtg (Current DSP 
      # Percentage).
      curLinPtg = 100 - ((exeStatus - 0xF0) * 10)  # Current Linear Percentage
      # Compare curLinPtg (Current DSP Percentage) with expcLinPtg (Expected 
      # Linear Percentage).
      if curLinPtg != self.expcLinPtg:
         # If curLinPtg (Current DSP Percentage) < lastLinPtg (Last DSP  
         # Percentage) then Fail Reverse.
         if curLinPtg < self.lastLinPtg:
            if testSwitch.virtualRun:
               ScrCmds.statMsg("VE FAIL: Check Status Failed: Reverse.")
            else:
               ScrCmds.raiseException(14931, "Check Status Failed: Reverse.")
         # If (expcLinPtg - 10) or (expcLinPtg + 10) is not equal with curLinPtg 
         # then add linWarnNum by 1.
         if (curLinPtg != (self.expcLinPtg - 10)) or (curLinPtg != (self.expcLinPtg + 10)):
            self.linWarnNum += 1
      # Add expcLinPtg (Expected Linear Percentage) by 10 (10%).
      self.expcLinPtg += 10
      # If expcLinPtg (Expected Linear Percentage) > 100 (100%) then set it back 
      # to 100 (100%).
      if self.expcLinPtg > 100: self.expcLinPtg = 100
      # Set lastLinPtg (Last DSP Percentage) as curLinPtg (Current DSP 
      # Percentage). 
      self.lastLinPtg = curLinPtg

###########################################################################################################
class CGoFlexTV(CState):
   """
   Go Flex TV
   """
   def __init__(self, dut, params={}):
      depList = []
      CState.__init__(self, dut, depList)
      
   def getTP(self):
      self.errCode = 48388
      oIdentifyDevice = CIdentifyDevice()
      self.maxLBA = oIdentifyDevice.getMaxLBA()
      self.onePercentLBA = int(self.maxLBA / 100)     # 1% LBA location
      self.fiftyPercentLBA = int(self.maxLBA / 2)     # 50% LBA location
      self.ttl_play_loop = TP.prm_GO_FLEX_TV.get('TTL_PLAY_LOOP', 5000)
      self.ttl_forward_loop = TP.prm_GO_FLEX_TV.get('TTL_FORWARD_LOOP', 1000)
      self.forward_length = TP.prm_GO_FLEX_TV.get('FORWARD_LENGTH', 5000)
      self.ttl_reverse_loop = TP.prm_GO_FLEX_TV.get('TTL_REVERSE_LOOP', 1000)
      self.ttl_scan_loop = TP.prm_GO_FLEX_TV.get('TTL_SCAN_LOOP', 6000)
      self.scan_half_length = TP.prm_GO_FLEX_TV.get('SCAN_HALF_LENGTH', 2000)

   def run(self):
      self.getTP()
      CHelper().clearBinBuff(WBF, self.errCode)
      self.curLBALoc = 0                              # Current LBA location
      ttl_main_loop = TP.prm_GO_FLEX_TV.get('TTL_MAIN_LOOP', 5000)
      for loopCtr in range(ttl_main_loop):
         if (loopCtr % 1000) == 0:
            ScrCmds.statMsg("At %s loops" % loopCtr)
         sel = random.randint(1, 5)
         if sel == 1:
            self.emulatePlay()
         elif sel == 2:
            self.emulateForward()
         elif sel == 3:
            self.emulateReverse()
         elif sel == 4:
            self.emulatePause()
         else:
            self.emulateUpdate()
      ScrCmds.statMsg("DONE!")
      self.emulateScan()
      
   def emulatePlay(self):
      endLBA = (self.ttl_play_loop * 16) - 1
      CHelper().sequentialReadDMAExt(0, endLBA, 16, 16, self.errCode)
      self.curLBALoc = endLBA
      self.emulateUpdate()
      
   def emulateForward(self):
      self.curLBALoc += self.forward_length
      if self.curLBALoc > (self.maxLBA - 1): self.curLBALoc = self.maxLBA - 1
      endLBA = self.curLBALoc + (self.ttl_forward_loop * 16) - 1
      if endLBA > (self.maxLBA - 1): endLBA = self.maxLBA - 1
      CHelper().sequentialReadDMAExt(self.curLBALoc, endLBA, 16, 16, self.errCode)
      self.curLBALoc = endLBA
      
   def emulateReverse(self):
      endLBA = self.curLBALoc - (self.ttl_reverse_loop * 16)
      if endLBA < 0: endLBA = 0
      CHelper().reverseReadDMAExt(self.curLBALoc, endLBA, 16, self.errCode)
      self.curLBALoc = endLBA + 16
      
   def emulatePause(self):
      time.sleep(random.randint(1, 10))
      
   def emulateUpdate(self):
      CHelper().sequentialWriteDMAExt(self.onePercentLBA, self.onePercentLBA + (20 * 8) - 1, 8, 8, self.errCode)
      CHelper().sequentialWriteDMAExt(self.fiftyPercentLBA, self.fiftyPercentLBA + (20 * 8) - 1, 8, 8, self.errCode)
      self.curLBALoc = self.fiftyPercentLBA + (20 * 8)
      
   def emulateScan(self):
      startLBA = self.onePercentLBA - self.scan_half_length
      CHelper().sequentialReadDMAExt(startLBA, startLBA + (self.ttl_scan_loop * 128) - 1, 128, 128, self.errCode)
      startLBA = self.fiftyPercentLBA - self.scan_half_length
      CHelper().sequentialReadDMAExt(startLBA, startLBA + (self.ttl_scan_loop * 128) - 1, 128, 128, self.errCode)

###########################################################################################################
class CHelper:

   def __init__(self):   
      self.oProc = CProcess()
      self.lbaTuple = CUtility.returnStartLbaWords      
      self.wordTuple = CUtility.ReturnTestCylWord
         
   def clearBinBuff(self, buffFlag, errCode):
      res = ICmd.ClearBinBuff(buffFlag)
      if res['LLRET'] != OK:
         ScrCmds.statMsg(" - Buffer Flag  : %s" % buffFlag)
         ScrCmds.raiseException(errCode, "Clear binary buffer fail")
   
   def readDMAExt(self, startLBA, sectorCount, errCode):   
      res = ICmd.SequentialReadDMAExt(startLBA, startLBA+sectorCount-1, sectorCount, sectorCount)     
      if res['LLRET'] != OK:
         ScrCmds.statMsg(" - Start LBA    : %s" % startLBA)
         ScrCmds.statMsg(" - Sector Count : %s" % sectorCount)
         ScrCmds.raiseException(errCode, "Read DMA Ext fail")

   def sequentialReadDMAExt(self, startLBA, endLBA, stepLBA, sectorCount, errCode):
##      tStart = time.time()
      result = OK
      if objRimType.CPCRiser():
         res = ICmd.SequentialReadDMAExt(startLBA, endLBA, stepLBA, sectorCount)
         result = res['LLRET']
      else:
         try:  # Use direct st call in SI for test time improvement
            SequentialReadDMAExt = {
               'CTRL_WORD1'      : 0x10,        # Read
               'CTRL_WORD2'      : 0x80,        # Fixed pattern
               'STARTING_LBA'    : CUtility.returnStartLbaWords(startLBA),
               'MAXIMUM_LBA'     : CUtility.returnStartLbaWords(endLBA),
               'STEP_SIZE'       : CUtility.returnStartLbaWords(stepLBA),
               'BLKS_PER_XFR'    : sectorCount,
               'DATA_PATTERN0'   : (0,0),
               'ENABLE_HW_PATTERN_GEN': 1,      # For faster read
##               'spc_id'          : 1,               
               'timeout'         : 252000,
               }
            DisableScriptComment(0x0FF0)     # Suppress output   
            st (510, SequentialReadDMAExt)
         except:
            result = NOT_OK
         DisableScriptComment(0)   

      if result != OK:
         ScrCmds.statMsg(" - Start LBA    : %s" % startLBA)
         ScrCmds.statMsg(" - End LBA      : %s" % endLBA)
         ScrCmds.statMsg(" - Step LBA     : %s" % stepLBA)
         ScrCmds.statMsg(" - Sector Count : %s" % sectorCount)
         ScrCmds.raiseException(errCode, "Sequential read DMA Ext fail!")
         
##      objMsg.printMsg("sequentialReadDMAExt completed in %2.3f seconds." %(time.time()-tStart)) 
      
   def sequentialReadCmpDMAExt(self, startLBA, endLBA, stepLBA, sectorCount, compare_flg, errCode):
##      tStart = time.time()
      compare = 0
      if compare_flg: compare = 1
      result = OK
      if objRimType.CPCRiser():      
         res = ICmd.SequentialReadDMAExt(startLBA, endLBA, stepLBA, sectorCount, 0, compare)
         result = res['LLRET']
      else:
         try:
            SequentialReadDMAExt = {
               'CTRL_WORD1'      : 0x10,        # Read
               'CTRL_WORD2'      : 0x80,        # Fixed pattern
               'STARTING_LBA'    : CUtility.returnStartLbaWords(startLBA),
               'MAXIMUM_LBA'     : CUtility.returnStartLbaWords(endLBA),
               'STEP_SIZE'       : CUtility.returnStartLbaWords(stepLBA),
               'BLKS_PER_XFR'    : sectorCount,
               'DATA_PATTERN0'   : (0,0),
               'ENABLE_HW_PATTERN_GEN': 1,      # For faster read
##               'spc_id'          : 1,               
               'timeout'         : 252000,
               }
            DisableScriptComment(0x0FF0)   
            st (510, SequentialReadDMAExt) 
         except:
            result = NOT_OK
         DisableScriptComment(0)      

      if result != OK:
         ScrCmds.statMsg("sequentialReadCmpDMAExt failed!")
         ScrCmds.statMsg(" - Start LBA    : %s" % startLBA)
         ScrCmds.statMsg(" - End LBA      : %s" % endLBA)
         ScrCmds.statMsg(" - Step LBA     : %s" % stepLBA)
         ScrCmds.statMsg(" - Sector Count : %s" % sectorCount)
         ScrCmds.statMsg(" - Compare Flag : %s" % compare_flg)
         ScrCmds.raiseException(errCode, "Sequential Read Compare DMA Ext fail!")
         
##      objMsg.printMsg("sequentialReadCmpDMAExt completed in %2.3f seconds." %(time.time()-tStart))   

   def NCQSequentialReadDMA(self, startLBA, endLBA, sectorCount, stepLBA, errCode):
      res = ICmd.NCQSequentialReadDMA(startLBA, endLBA, sectorCount, stepLBA)
      if res['LLRET'] != OK:
         ScrCmds.statMsg("Result: %s" % res)
         ScrCmds.statMsg(" - Start LBA    : %s" % startLBA)
         ScrCmds.statMsg(" - End LBA      : %s" % endLBA)
         ScrCmds.statMsg(" - Sector Count : %s" % sectorCount)
         ScrCmds.statMsg(" - Step LBA     : %s" % stepLBA)
         ScrCmds.raiseException(errCode, "NCQ Sequential Read DMA fail!")

   def sequentialReadVerifyExt(self, startLBA, endLBA, stepLBA, sectorCount, errCode):
      res = ICmd.SequentialReadVerifyExt(startLBA, endLBA, stepLBA, sectorCount)
      if res['LLRET'] != OK:
         ScrCmds.statMsg("Result: %s" % res)
         ScrCmds.statMsg(" - Start LBA    : %s" % startLBA)
         ScrCmds.statMsg(" - End LBA      : %s" % endLBA)
         ScrCmds.statMsg(" - Step LBA     : %s" % stepLBA)
         ScrCmds.statMsg(" - Sector Count : %s" % sectorCount)
         ScrCmds.raiseException(errCode, "Sequential Read Verify Ext fail!")

   def writeDMAExt(self, startLBA, sectorCount, errCode):
      res = ICmd.SequentialWriteDMAExt(startLBA, startLBA+sectorCount-1, sectorCount, sectorCount)     
      if res['LLRET'] != OK:
         ScrCmds.statMsg(" - Start LBA    : %s" % startLBA)
         ScrCmds.statMsg(" - Sector Count : %s" % sectorCount)
         ScrCmds.raiseException(errCode, "Write DMA Ext fail")

   def sequentialWriteDMAExt(self, startLBA, endLBA, stepLBA, sectorCount, errCode):
##      tStart = time.time()
      result = OK
      if objRimType.CPCRiser():
         res = ICmd.SequentialWriteDMAExt(startLBA, endLBA, stepLBA, sectorCount)
         result = res['LLRET'] 
      else:
         try:
            SequentialWriteDMAExt = {
               'CTRL_WORD1'      : 0x22,  # Write and with error display
               'CTRL_WORD2'      : 0x80,  # Fixed pattern
               'STARTING_LBA'    : CUtility.returnStartLbaWords(startLBA),
               'MAXIMUM_LBA'     : CUtility.returnStartLbaWords(endLBA),
               'STEP_SIZE'       : CUtility.returnStartLbaWords(stepLBA),
               'BLKS_PER_XFR'    : sectorCount,
               'DATA_PATTERN0'   : (0,0),
               'ENABLE_HW_PATTERN_GEN': 1,   # For faster write
##               'spc_id'          : 1,
               'timeout'         : 252000,                              
            }
            DisableScriptComment(0x0FF0)     # Suppress output
            st (510, SequentialWriteDMAExt)
         except:
            result = NOT_OK
         DisableScriptComment(0)   
               
      if result != OK:
         ScrCmds.statMsg(" - Start LBA    : %s" % startLBA)
         ScrCmds.statMsg(" - End LBA      : %s" % endLBA)
         ScrCmds.statMsg(" - Step LBA     : %s" % stepLBA)
         ScrCmds.statMsg(" - Sector Count : %s" % sectorCount)
         ScrCmds.raiseException(errCode, "Sequential write DMA Ext fail!")
##      objMsg.printMsg("sequentialWriteDMAExt completed in %2.3f seconds." %(time.time()-tStart))   

   def NCQSequentialWriteDMA(self, startLBA, endLBA, sectorCount, stepLBA, errCode):
      res = ICmd.NCQSequentialWriteDMA(startLBA, endLBA, sectorCount, stepLBA)
      if res['LLRET'] != OK:
         ScrCmds.statMsg("Result: %s" % res)
         ScrCmds.statMsg(" - Start LBA    : %s" % startLBA)
         ScrCmds.statMsg(" - End LBA      : %s" % endLBA)
         ScrCmds.statMsg(" - Sector Count : %s" % sectorCount)
         ScrCmds.statMsg(" - Step LBA     : %s" % stepLBA)
         ScrCmds.raiseException(errCode, "NCQ Sequential Write DMA fail!")

   def sequentialWRCopy(self, startRdLBA, startWrLBA, rangeLBA, sectorCount, errCode):
      cpcVer = 0
      if objRimType.CPCRiser():
         cpcCheckObj = BaseCPCInit()
         cpcVer = float(cpcCheckObj.stripVer(cpcCheckObj.CPCVer))
      if (cpcVer >= 2.226 and objRimType.CPCRiser()) or objRimType.IOInitRiser():   
         res = ICmd.SequentialWRCopy(startRdLBA, startWrLBA, rangeLBA, sectorCount)
         if res['LLRET'] != OK:
            ScrCmds.statMsg("Result: %s" % res)
            ScrCmds.raiseException(errCode, "Sequential WR Copy fail!")
      else:
         endRdLBA      = startRdLBA
         endWrLBA      = startWrLBA
         stepNum       = rangeLBA / sectorCount
         lastStepLBA   = rangeLBA % sectorCount
         stepLBA       = sectorCount

         ICmd.MakeAlternateBuffer(BReW)
         try:
            for stepCtr in range(0, stepNum + 1):
               # for last step LBA
               if stepCtr == stepNum:
                  sectorCount       = lastStepLBA
               # reading from drive to buffer
               startRdLBA = endRdLBA
               endRdLBA = startRdLBA + sectorCount
               CHelper().sequentialReadDMAExt(startRdLBA, endRdLBA, stepLBA, \
                                              sectorCount, errCode)                                              
               #Copy Read Buffer to Write Buffer     
               if objRimType.IOInitRiser():           
                  ICmd.BufferCopy(WBF,0,RBF,0,512*sectorCount)
               # writing from buffer to drive
               startWrLBA = endWrLBA
               endWrLBA = startWrLBA + sectorCount
               CHelper().sequentialWriteDMAExt(startWrLBA, endWrLBA, stepLBA, \
                                               sectorCount, errCode)
         finally:
            ICmd.RestorePrimaryBuffer(BReW)

   def seqDelayWrite(self, startLBA, endLBA, sectorCount, \
                     minDelay, maxDelay, stepDelay, errCode):
      """
      minDelay, maxDelay, and stepDelay are in millisecond.
      """          
      cpcVer = 0
      if objRimType.CPCRiser():
         cpcCheckObj = BaseCPCInit()
         cpcVer = float(cpcCheckObj.stripVer(cpcCheckObj.CPCVer))

      if (cpcVer >= 2.224 and objRimType.CPCRiser()) or objRimType.IOInitRiser():            
         res = ICmd.SeqDelayWR(startLBA, endLBA, sectorCount, \
                               minDelay, maxDelay, stepDelay, 1, 48)
         if res['LLRET'] != OK:
            ScrCmds.statMsg("Result: %s" % res)
            ScrCmds.raiseException(errCode, "Seq Delay Write fail")
      else:
         maxTestLba = (endLBA - startLBA) + 1
         idxLBA = startLBA
         delay = minDelay
         for ctr in xrange(maxTestLba / sectorCount):
            res = ICmd.SequentialWriteDMAExt(idxLBA, idxLBA + sectorCount, \
                                             sectorCount, sectorCount)
            if res['LLRET'] != OK:
               ScrCmds.statMsg("Result: %s" % res)
               ScrCmds.statMsg(" - Start LBA    : %s" % idxLBA)
               ScrCmds.statMsg(" - End LBA      : %s" % (idxLBA + sectorCount))
               ScrCmds.raiseException(errCode, "Sequential Write DMA Ext fail")
            idxLBA += sectorCount
            # delay
            time.sleep(delay/1000.0)
            delay += stepDelay
            if delay > maxDelay: delay = minDelay

         restLBA = maxTestLba % sectorCount
         if restLBA > 0:
            res = ICmd.SequentialWriteDMAExt(idxLBA, idxLBA + (restLBA - 1), restLBA, restLBA)
            if res['LLRET'] != OK:
               ScrCmds.statMsg("Result: %s" % res)
               ScrCmds.statMsg(" - Start LBA    : %s" % idxLBA)
               ScrCmds.statMsg(" - End LBA      : %s" % (idxLBA + restLBA))
               ScrCmds.raiseException(errCode, "Write fail")

   def reverseReadDMAExt(self, startLBA, endLBA, sectorCount, errCode):
      res = ICmd.ReverseReadDMAExt(startLBA, endLBA, sectorCount)
      if res['LLRET'] != OK:
         ScrCmds.statMsg("Result: %s" % res)
         ScrCmds.statMsg(" - Start LBA    : %s" % startLBA)
         ScrCmds.statMsg(" - End LBA      : %s" % endLBA)
         ScrCmds.statMsg(" - Sector Count : %s" % sectorCount)
         ScrCmds.raiseException(errCode, "Reverse read DMA Ext fail!")

   #-------------------------------------------------------------------------------------------------------                  
   def ConfigureStream(self, streamid = 0x1, cct = 0x64):      
      ConfigureStream = {
                  'test_num' : 538,
                  'prm_name' : "ConfigureStream",
                   'timeout' : 600,
                  'FEATURES' : (cct << 8) | (0x8 << 4) | (streamid), 
              'SECTOR_COUNT' : 0,
                   'COMMAND' : 0x51,
                   'LBA_LOW' : 0,
                   'LBA_MID' : 0,
                  'LBA_HIGH' : 0,         
               'PARAMETER_0' : 0x2000, #enables LBA mode cmd reg defs            
          'stSuppressResults': ST_SUPPRESS__ALL,}

      try:      
         self.oProc.St(ConfigureStream)      
         return PASS_RETURN   
      except:            
         self.oProc.St({'test_num':504,'prm_name':'dumpATAInfo'})
         raise

   #-------------------------------------------------------------------------------------------------------                  
   def WriteStreamDMAExt(self, streamid = 0x1, startLBA = 0, totalBlksPerXfr = 0, sectorcnt = 0, compare = 0, butterfly = 0):            
      try:
         if objRimType.CPCRiser():     
            if not butterfly:     
               res = ICmd.WrStreamDMATransRate(startLBA, totalBlksPerXfr, sectorcnt, streamid)
               objMsg.printMsg('WriteStreamDMAExt: %s' %res)               
               data = {'LLRET':res['LLRET'],'CCT':int(res['TXTIME']),'DATA_RATE':int(res['TXRATE'])}                  
            else:
               res = ICmd.ButterflyScan(1,-4,startLBA,startLBA+totalBlksPerXfr,sectorcnt,sectorcnt,streamid)
               objMsg.printMsg('Write Stream ButterflyScan: %s' %res)          
               data = {'LLRET':res['LLRET']}                      
            if data['LLRET'] != 0: raise       
         elif objRimType.IOInitRiser():     
            tempPrm = {
                        'test_num' : 643,
                        'prm_name' : "WriteStreamDMAExt",
                         'timeout' : 60000,                         
                   'TEST_FUNCTION' : 0x50, #Enable Streaming Write/Read                   
                 'WRITE_READ_MODE' : 0x1, #Write
                    'STARTING_LBA' : self.lbaTuple(int(startLBA)),       
             'TOTAL_BLKS_TO_XFR64' : self.lbaTuple(int(totalBlksPerXfr)),
              'FIXED_SECTOR_COUNT' : sectorcnt,                     
                  'COMPARE_OPTION' : compare, #Buffer Compare            
                         'OPTIONS' : butterfly << 1,
                        'FEATURES' : streamid,                         
                                }                                
            if not butterfly:             
               tempPrm.update({
                'DblTablesToParse' : ['P641_DMAEXT_TRANSFER_RATE',],                  
               'stSuppressResults' : ST_SUPPRESS__ALL,
                  })              

            self.oProc.St(tempPrm)     
            if not butterfly:        
               ret = objDut[PortIndex].objSeq.SuprsDblObject['P641_DMAEXT_TRANSFER_RATE'][-1]
               data = {'LLRET':0, 'TXTIME':int(ret['TIME_ELAPSED_US']),'DATA_RATE':int(ret['TXRATE_MB/S'])}               
            else: data = PASS_RETURN   
      except:            
         self.oProc.St({'test_num':504,'prm_name':'dumpATAInfo'})
         raise

      return data  
   
   #-------------------------------------------------------------------------------------------------------                  
   def ReadStreamDMAExt(self,  streamid = 0x1, startLBA = 0, totalBlksPerXfr = 0, sectorcnt = 0, compare = 0, butterfly = 0):      
      try:
         if objRimType.CPCRiser():          
            if not butterfly:            
               if not compare:
                  res = ICmd.RdStreamDMATransRate(startLBA, totalBlksPerXfr, sectorcnt, streamid)            
                  objMsg.printMsg('ReadStreamDMAExt: %s' %res)               
                  data = {'LLRET':res['LLRET'],'CCT':int(res['TXTIME']),'DATA_RATE':int(res['TXRATE'])}                  
               else:
                  res = ICmd.SequentialReadSTRDMA(startLBA,startLBA+totalBlksPerXfr,sectorcnt,sectorcnt,0,1,1,streamid)            
                  objMsg.printMsg('ReadStreamDMAExt with Compare: %s' %res)               
                  data = {'LLRET':res['LLRET']}
            else:
               res = ICmd.ButterflyScan(1,4,startLBA,startLBA+totalBlksPerXfr,sectorcnt,sectorcnt,streamid)
               objMsg.printMsg('Read Stream ButterflyScan: %s' %res)       
               data = {'LLRET':res['LLRET']}                                         
            if data['LLRET'] != 0: raise            
         elif objRimType.IOInitRiser():     
            tempPrm = {
                        'test_num' : 643,
                        'prm_name' : "ReadStreamDMAExt",
                         'timeout' : 60000,                         
                   'TEST_FUNCTION' : 0x50, #Enable Streaming Write/Read                   
                 'WRITE_READ_MODE' : 0x0, #Read
                    'STARTING_LBA' : self.lbaTuple(int(startLBA)),       
             'TOTAL_BLKS_TO_XFR64' : self.lbaTuple(int(totalBlksPerXfr)),
              'FIXED_SECTOR_COUNT' : sectorcnt,       
                  'COMPARE_OPTION' : compare, #Buffer Compare            
                         'OPTIONS' : butterfly << 1,
                        'FEATURES' : streamid,                         
                  }
            if not butterfly:             
               tempPrm.update({
                'DblTablesToParse' : ['P641_DMAEXT_TRANSFER_RATE',],                  
               'stSuppressResults' : ST_SUPPRESS__ALL,
                  })              

            self.oProc.St(tempPrm)     
            if not butterfly:        
               ret = objDut[PortIndex].objSeq.SuprsDblObject['P641_DMAEXT_TRANSFER_RATE'][-1]           
               data = {'LLRET':0, 'TXTIME':int(ret['TIME_ELAPSED_US']),'DATA_RATE':int(ret['TXRATE_MB/S'])}               
            else: data = PASS_RETURN     
      except:            
         self.oProc.St({'test_num':504,'prm_name':'dumpATAInfo'})
         raise            
                        
      return data

   #-------------------------------------------------------------------------------------------------------                  
   def WRStreamDMAExt(self,  streamid = 0x1, startLBA = 0, totalBlksPerXfr = 0, sectorcnt = 0, compare = 0, butterfly = 0):      
      try:
         if objRimType.CPCRiser():          
            if not butterfly:            
               if compare:
                  res = ICmd.SequentialWRSTRDMA(startLBA,startLBA+totalBlksPerXfr,sectorcnt,sectorcnt,0,1,1,streamid)            
                  objMsg.printMsg('Write/ReadStreamDMAExt with Compare: %s' %res)               
                  data = {'LLRET':res['LLRET']}                  
            else:            
               res = ICmd.ButterflyScan(1,-5,startLBA,startLBA+totalBlksPerXfr,sectorcnt,sectorcnt,streamid)
               objMsg.printMsg('Write/Read Stream ButterflyScan: %s' %res)    
               data = {'LLRET':res['LLRET']}                                                            
            if data['LLRET'] != 0: raise            
         elif objRimType.IOInitRiser():     
            tempPrm = {
                        'test_num' : 643,
                        'prm_name' : "WRStreamDMAExt",
                         'timeout' : 60000,                         
                   'TEST_FUNCTION' : 0x50, #Enable Streaming Write/Read                   
                 'WRITE_READ_MODE' : 0x2, #Write/Read
                    'STARTING_LBA' : self.lbaTuple(int(startLBA)),       
             'TOTAL_BLKS_TO_XFR64' : self.lbaTuple(int(totalBlksPerXfr)),
              'FIXED_SECTOR_COUNT' : sectorcnt,       
                  'COMPARE_OPTION' : compare, #Buffer Compare            
                         'OPTIONS' : butterfly << 1,
                        'FEATURES' : streamid, 
                  }
            if not butterfly:             
               tempPrm.update({
                'DblTablesToParse' : ['P641_DMAEXT_TRANSFER_RATE',],                  
               'stSuppressResults' : ST_SUPPRESS__ALL,
                  })              
               
            self.oProc.St(tempPrm)    
            if not butterfly:        
               ret = objDut[PortIndex].objSeq.SuprsDblObject['P641_DMAEXT_TRANSFER_RATE'][-1]                       
               data = {'LLRET':0, 'TXTIME':int(ret['TIME_ELAPSED_US']),'DATA_RATE':int(ret['TXRATE_MB/S'])}               
            else: data = PASS_RETURN   
      except:            
         self.oProc.St({'test_num':504,'prm_name':'dumpATAInfo'})
         raise            
                        
      return data

   #-------------------------------------------------------------------------------------------------------                  
   def SequentialCCT(self, Cmd1, STARTING_LBA, MAXIMUM_LBA, BLKS_PER_XFR = 256, STEP_LBA = 256, Cmd2 = 0, exc = 1):   
      tempPrm = {}
      if Cmd1 == 0x35 and Cmd2 == 0:                  
         tempPrm['prm_name'] = "SequentialWriteDMAExt"             
         tempPrm['CTRL_WORD1'] = (0x20) #Write         
      elif Cmd1 == 0x25 and Cmd2 == 0:
         tempPrm['prm_name'] = "SequentialReadDMAExt"             
         tempPrm['CTRL_WORD1'] = (0x10) #Read
      elif Cmd1 in [0x35,0x25] and Cmd2 <> 0:
         tempPrm['prm_name'] = "SequentialWRDMAExt"             
         tempPrm['CTRL_WORD1'] = (0x0) #Write/Read         
               
      tempPrm.update({               
                  "test_num" : 510,
                   "timeout" : 252000,
                "CTRL_WORD2" : (0x6080), #Do CCT
              "STARTING_LBA" : self.lbaTuple(int(STARTING_LBA)),       
              "BLKS_PER_XFR" : BLKS_PER_XFR,     
          "CCT_BIN_SETTINGS" : 0x1E64, #30Bins - 100ms range -> Bin Threshold until 3000 msec
             "DATA_PATTERN0" : (0,0),        
            "MAX_NBR_ERRORS" : 0xFFFF, #Collect all data
         "RESET_AFTER_ERROR" : 1,  })                  

      if objRimType.IOInitRiser():
         tempPrm["STEP_SIZE"] = self.lbaTuple(STEP_LBA)         
         tempPrm["TOTAL_BLKS_TO_XFR64"] = self.lbaTuple(int(MAXIMUM_LBA - STARTING_LBA+1))
      elif objRimType.CPCRiser():    
         tempPrm["TOTAL_BLKS_TO_XFR"] = self.wordTuple(int(MAXIMUM_LBA - STARTING_LBA+1))
                              
      try:         
         ret = self.oProc.St(tempPrm)     
         return PASS_RETURN          
      except:
         self.oProc.St({'test_num':504,'prm_name':'dumpATAInfo'})
         raise       
             
###########################################################################################################

class CDVRTest(CState):
   ''' Performs the following DVR tests:   
   1. Streaming test    
   2. Philips AVL test    
   3. 3 streams test  
   4. FCC test   
   '''   

   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):   
      self.params = params
      self.oProc = CProcess()
      self.oHelper = CHelper()            
      depList = []
      CState.__init__(self, dut, depList)
            
   #-------------------------------------------------------------------------------------------------------                  
   def run(self):         
      try:
         objPwrCtrl.powerCycle()      
         oIdentifyDevice = CIdentifyDevice()
                
         self.maxLBA = oIdentifyDevice.getMaxLBA()   
         self.fde_supported = oIdentifyDevice.Is_FDE()
         self.streaming_supported = oIdentifyDevice.Is_Streaming_Supported()
               
         objMsg.printMsg("Debug: self.maxLBA = %s" %self.maxLBA)
         objMsg.printMsg("Debug: self.fde_supported = %s" %self.fde_supported)       
         objMsg.printMsg("Debug: self.streaming_supported = %s" %self.streaming_supported)         

         Tests = [1,2,3,4]
         for i in Tests:
           starttest = time.time()
           func = 'self.Test' + str(i) + '()'
           eval(func)
           endtest = time.time()
           totaltime = endtest - starttest
           objMsg.printMsg("Test Time - Test:%s: %fsec" %(str(i),totaltime))
      except:
         objMsg.printMsg(traceback.format_exc())
         raise                     
   
   #-------------------------------------------------------------------------------------------------------                  
   def Test1(self):
               
      ''' Perform butterfly test using streaming commands.
      @ Write then read 512 sectors from max LBA to LBA 0
      @ Write then read 512 sectors from LBA 0 to max LBA 
      '''               
      ScrCmds.insertHeader("Test1 : Butterfly Streaming Test")

      ICmd.MakeAlternateBuffer(BWR, 512)     
      ICmd.ClearBinBuff(BWR)

      if self.fde_supported:      
         ret = ICmd.SetMultipleMode(1)         
      else:
         ret = ICmd.SetMultipleMode(16)         
      if ret['LLRET'] != OK:         
         ScrCmds.raiseException(11044, "Failed SetMultipleMode")
      
      if not self.streaming_supported:
         # Write then read 512 sectors from top LBA to bottom LBA
         ICmd.ButterflySeek(0,self.maxLBA,512)    
      else:
         self.oHelper.ConfigureStream(0x1)           
         self.oHelper.WRStreamDMAExt(0x1,0,self.maxLBA,512,0,1)

      ICmd.RestorePrimaryBuffer(BWR)                     
   #-------------------------------------------------------------------------------------------------------   
   def Test2(self):
      ''' Perform Philips AVL test.'''       
      ScrCmds.insertHeader("Test2:  Philips AVL Test")      
            
      ICmd.HardReset()
                         
      #write 0x00 from LBA 0 to max LBA with sector length 8192
      ICmd.MakeAlternateBuffer(BWR, 1024 * 8)     
      ICmd.ClearBinBuff(WBF)      
      objMsg.printMsg("write 0x00 from LBA 0 to max LBA with sector length 8192.....") 
      self.oHelper.sequentialWriteDMAExt(0, self.maxLBA, 8192, 8192, 11044)
      ICmd.FlushCache()
      ICmd.RestorePrimaryBuffer(BWR)
      
      #write 0x00 from LBA 0 to max LBA with sector length 256, record the time      
      objMsg.printMsg("write 0x00 from LBA 0 to max LBA with sector length 256, with CCT distribution.....")      
      self.oHelper.SequentialCCT(0x35, 0, self.maxLBA, 256, 256)         
      ICmd.FlushCache()      
            
      #read 0x00 from LBA 0 to max LBA with sector length 256, record the time          
      objMsg.printMsg("read 0x00 from LBA 0 to max LBA with sector length 256, with CCT distribution.....")
      self.oHelper.SequentialCCT(0x25, 0, self.maxLBA, 256, 256)  

      # disable RLA and write cache      
      objMsg.printMsg("disable RLA and write cache.....")
      disable_ReadLookAhead()           
      disable_WriteCache()

      # Random read/write on avl_sectors for 25K loops      
      objMsg.printMsg("Seek to LBA 0.....")
      ICmd.Seek(0)                 # seek LBA 0      

      objMsg.printMsg("Random read/write on avl_sectors for 25K loops.....")
      avl_sectors = [1, 128, 256, 512, 1000, 2048, 4096]      
      loops = 25000
      ICmd.MakeAlternateBuffer(BWR, max(avl_sectors))         
      ICmd.ClearBinBuff(BWR)         
      for x in xrange(loops):            
         lba =  random.randrange(self.maxLBA-4096)
         sector = random.choice(avl_sectors)
         tStart = time.time()                
         self.oHelper.sequentialReadDMAExt(lba, lba+sector-1, sector, sector, 11044)
         tEnd = time.time() - tStart                      
         if (tEnd / 1000) > 200:                     
            objMsg.printMsg("Read from Lba:%s SectorCnt:%s greater than 200ms. tt_read = %s\n" %(lba, sector, (tEnd / 1000)))

      objMsg.printMsg("Seek to LBA 0.....") 
      ICmd.Seek(0)                 # seek LBA 0
      for x in xrange(loops):            
         lba =  random.randrange(self.maxLBA-4096)
         sector = random.choice(avl_sectors)
         tStart = time.time()                
         self.oHelper.sequentialWriteDMAExt(lba, lba+sector-1, sector, sector, 11044)                     
         tEnd = time.time() - tStart                      
         if (tEnd / 1000) > 200:                     
            objMsg.printMsg("Write to Lba:%s SectorCnt:%s greater than 200ms. tt_write = %s\n" %(lba, sector, (tEnd / 1000)))
            
      # Turn on RLA and write cache and read from LBA 0 to max LBA using 256 sectors    
      objMsg.printMsg("enable RLA and write cache.....")      
      enable_ReadLookAhead()          
      enable_WriteCache()      
      objMsg.printMsg("read from LBA 0 to max LBA using 256 sectors, with CCT distribution.....")  
      self.oHelper.SequentialCCT(0x25, 0, self.maxLBA, 256, 256)         
               
      ICmd.RestorePrimaryBuffer(BWR)         
                       
   #-------------------------------------------------------------------------------------------------------               
   def Test3(self):   
      '''SIMULATE 6 STREAM OF DATA,MEASURE TIME TAKEN  TO SERVICE ALL STREAM'''      
      ScrCmds.insertHeader("Test3 - 3 Stream Test")      
      objMsg.printMsg("streams3 Test.....")      
      self.streams3()    
      self.stream3s()   
      self.streamSnj()               
      self.streams4()    
      self.streams6()    
            
   #-------------------------------------------------------------------------------------------------------
   def streams3(self, rw = 0, cct = 0):      
      ICmd.HardReset()      
      if self.streaming_supported:
         if cct == 0:
            self.oHelper.ConfigureStream(0x1)
            self.oHelper.ConfigureStream(0x2)
            self.oHelper.ConfigureStream(0x3)
         else:          
            objMsg.printMsg("CCT value set to: %dsec" %(cct/10))          
            self.oHelper.ConfigureStream(0x1,cct)
            self.oHelper.ConfigureStream(0x2,cct)
            self.oHelper.ConfigureStream(0x3,cct)

      Set_UDMASpeed(4)
      ICmd.MakeAlternateBuffer(BWR, 1536)         
      ICmd.ClearBinBuff(BWR)
      stream1_startlba = 100
      stream2_startlba = self.maxLBA-308200
      stream3_startlba = self.maxLBA/2   
      sectorcnt = 1536
      TotalBlksToXfer = 307200 #1536 * 200      

      if not rw:
         #Write stream 1 & 2 using 1536 sectors                
         #Read stream 3 using 1536 sectors
         objMsg.printMsg("Write/Read 1536 sectors for stream 1,2/3 for 200 loops (1536 * 200 = 307200 sectors)......")                  
         if self.streaming_supported:
            Stream1_DataRate = self.oHelper.WriteStreamDMAExt(0x1,stream1_startlba,TotalBlksToXfer,sectorcnt)['DATA_RATE']         
            Stream2_DataRate = self.oHelper.WriteStreamDMAExt(0x2,stream2_startlba,TotalBlksToXfer,sectorcnt)['DATA_RATE']    
            Stream3_DataRate = self.oHelper.ReadStreamDMAExt(0x3,stream3_startlba,TotalBlksToXfer,sectorcnt)['DATA_RATE']     
         else:         
            Stream1_DataRate = ICmd.WriteDMAExtTransRate(stream1_startlba,TotalBlksToXfer,sectorcnt)['TXRATE']
            Stream2_DataRate = ICmd.WriteDMAExtTransRate(stream2_startlba,TotalBlksToXfer,sectorcnt)['TXRATE']
            Stream3_DataRate = ICmd.ReadDMAExtTransRate(stream3_startlba,TotalBlksToXfer,sectorcnt)['TXRATE']
      else:
         #Read stream 1 & 2 using 1536 sectors                
         #Write stream 3 using 1536 sectors
         objMsg.printMsg("Read/Write 1536 sectors for stream 1,2/3 for 200 loops (1536 * 200 = 307200 sectors)......")
         if self.streaming_supported:
            Stream1_DataRate = self.oHelper.ReadStreamDMAExt(0x1,stream1_startlba,TotalBlksToXfer,sectorcnt)['DATA_RATE']         
            Stream2_DataRate = self.oHelper.ReadStreamDMAExt(0x2,stream2_startlba,TotalBlksToXfer,sectorcnt)['DATA_RATE']    
            Stream3_DataRate = self.oHelper.WriteStreamDMAExt(0x3,stream3_startlba,TotalBlksToXfer,sectorcnt)['DATA_RATE']     
         else:
            Stream1_DataRate = ICmd.ReadDMAExtTransRate(stream1_startlba,TotalBlksToXfer,sectorcnt)['TXRATE']
            Stream2_DataRate = ICmd.ReadDMAExtTransRate(stream2_startlba,TotalBlksToXfer,sectorcnt)['TXRATE']
            Stream3_DataRate = ICmd.WriteDMAExtTransRate(stream3_startlba,TotalBlksToXfer,sectorcnt)['TXRATE']

      objMsg.printMsg("*"*20)                
      Stream_TotalDataRate = (Stream1_DataRate + Stream2_DataRate + Stream3_DataRate)/3                      
      objMsg.printMsg("Data ThroughPut: Stream1-%sMB/s Stream2-%sMB/s Stream3-%sMB/s" 
                   %(Stream1_DataRate,Stream2_DataRate,Stream3_DataRate))     
      objMsg.printMsg("Overall Data ThroughPut: %sMB/s" %Stream_TotalDataRate)     
      objMsg.printMsg("*"*20)  

      ICmd.RestorePrimaryBuffer(BWR)   

   #-------------------------------------------------------------------------------------------------------
   def stream3s(self):               
      objMsg.printMsg("stream3s Test.....") 
      self.streams3(rw = 1) 

   #-------------------------------------------------------------------------------------------------------
   def streamSnj(self):            
      objMsg.printMsg("streamSnj Test.....")        
      self.streams3(cct = 0x14) 

   #-------------------------------------------------------------------------------------------------------
   def streams6(self):            
      objMsg.printMsg("streams6 Test.....")        
      self.streams4(streams6 = 1) 

   #-------------------------------------------------------------------------------------------------------
   def streams4(self, streams6 = 0):         
      ScrCmds.insertHeader("Test3 : streams4 Test")      

      ICmd.HardReset()
      if self.streaming_supported:
         self.oHelper.ConfigureStream(0x1)
         self.oHelper.ConfigureStream(0x2)
         self.oHelper.ConfigureStream(0x3)
         self.oHelper.ConfigureStream(0x4)
         if streams6:         
            self.oHelper.ConfigureStream(0x5)
            self.oHelper.ConfigureStream(0x6)
            
      Set_UDMASpeed(4)      
      ICmd.MakeAlternateBuffer(BWR, 752)               
      ICmd.ClearBinBuff(BWR)
      if streams6:
         stream1_startlba = self.maxLBA/100
         stream2_startlba = (self.maxLBA*20)/100
         stream3_startlba = (self.maxLBA*40)/100   
         stream4_startlba = (self.maxLBA*60)/100
         stream5_startlba = (self.maxLBA*80)/100   
         stream6_startlba = (self.maxLBA*99)/100        
      else:
         stream1_startlba = self.maxLBA/100
         stream2_startlba = (self.maxLBA*33)/100
         stream3_startlba = (self.maxLBA*66)/100   
         stream4_startlba = (self.maxLBA*99)/100
      sectorcnt = 752
      TotalBlksToXfer = 150400 #752 * 200      

      if streams6:      
         objMsg.printMsg("Read/Write 752 sectors for streams 1,2,3,4,5,6 for 200 loops (752 * 200 = 150400 sectors)......")         
      else:   
         objMsg.printMsg("Read/Write 752 sectors for streams 1,2,3,4 for 200 loops (752 * 200 = 150400 sectors)......")                  

      #Read stream 1 & 3 using 752 sectors
      #Write stream 2 & 4 using 752 sectors                
      if self.streaming_supported:
         Stream1_DataRate = self.oHelper.ReadStreamDMAExt(0x1,stream1_startlba,TotalBlksToXfer,sectorcnt)['DATA_RATE']     
         Stream2_DataRate = self.oHelper.WriteStreamDMAExt(0x2,stream2_startlba,TotalBlksToXfer,sectorcnt)['DATA_RATE']         
         Stream3_DataRate = self.oHelper.ReadStreamDMAExt(0x3,stream3_startlba,TotalBlksToXfer,sectorcnt)['DATA_RATE']     
         Stream4_DataRate = self.oHelper.WriteStreamDMAExt(0x4,stream4_startlba,TotalBlksToXfer,sectorcnt)['DATA_RATE']    
      else:         
         Stream1_DataRate = ICmd.ReadDMAExtTransRate(stream1_startlba,TotalBlksToXfer,sectorcnt)['TXRATE']
         Stream2_DataRate = ICmd.WriteDMAExtTransRate(stream2_startlba,TotalBlksToXfer,sectorcnt)['TXRATE']
         Stream3_DataRate = ICmd.ReadDMAExtTransRate(stream3_startlba,TotalBlksToXfer,sectorcnt)['TXRATE']
         Stream4_DataRate = ICmd.WriteDMAExtTransRate(stream4_startlba,TotalBlksToXfer,sectorcnt)['TXRATE']

      if streams6:      
         #Read stream 5 using 752 sectors
         #Write stream 6 using 752 sectors                
         if self.streaming_supported:
            Stream5_DataRate = self.oHelper.ReadStreamDMAExt(0x5,stream5_startlba,TotalBlksToXfer,sectorcnt)['DATA_RATE']     
            Stream6_DataRate = self.oHelper.WriteStreamDMAExt(0x6,stream6_startlba,TotalBlksToXfer,sectorcnt)['DATA_RATE']         
         else:         
            Stream5_DataRate = ICmd.ReadDMAExtTransRate(stream5_startlba,TotalBlksToXfer,sectorcnt)['TXRATE']
            Stream6_DataRate = ICmd.WriteDMAExtTransRate(stream6_startlba,TotalBlksToXfer,sectorcnt)['TXRATE']


      objMsg.printMsg("*"*20)                
      if streams6:      
         Stream_TotalDataRate = (Stream1_DataRate + Stream2_DataRate + Stream3_DataRate + \
                                Stream4_DataRate + Stream5_DataRate + Stream6_DataRate)/6                      
         objMsg.printMsg("Data ThroughPut: Stream1-%sMB/s Stream2-%sMB/s Stream3-%sMB/s Stream4-%sMB/s Stream5-%sMB/s Stream6-%sMB/s"  
                   %(Stream1_DataRate,Stream2_DataRate,Stream3_DataRate,Stream4_DataRate,Stream5_DataRate,Stream6_DataRate))     
      else:
         Stream_TotalDataRate = (Stream1_DataRate + Stream2_DataRate + Stream3_DataRate + Stream4_DataRate)/4
         objMsg.printMsg("Data ThroughPut: Stream1-%sMB/s Stream2-%sMB/s Stream3-%sMB/s Stream4-%sMB/s" 
                   %(Stream1_DataRate,Stream2_DataRate,Stream3_DataRate,Stream4_DataRate))     
      objMsg.printMsg("Overall Data ThroughPut: %sMB/s" %Stream_TotalDataRate)     
      objMsg.printMsg("*"*20)  

      ICmd.RestorePrimaryBuffer(BWR)   

   #-------------------------------------------------------------------------------------------------------
   def Test4(self):
      '''CREATE TEST TO CHECK FOR MISCOMPARE USING STREAMING COMMAND'''
     # self.FCC()
      self.CEFCC()
     # self.SFCC50()
                     
   #-------------------------------------------------------------------------------------------------------
   def FCC(self):
      ScrCmds.insertHeader("Test4 - FCC Test")     

      ICmd.MakeAlternateBuffer(BWR, 4096)       
      ICmd.ClearBinBuff(BWR)  
      TestTime = 86400 #24 hrs      
      StartTime = time.time()      
      EndTime = StartTime + TestTime 
      while time.time() < EndTime: 
         ICmd.FillBuffRandom(WBF,0,4096)      #Set various data pattern in the buffer   
         Set_UDMASpeed(5)           #set UDMA5
   
         if self.streaming_supported: 
            self.oHelper.ConfigureStream(0x1)
            
         #stream write from LBA0 to MAXLBA with 4096 sectors    
         if self.streaming_supported:                  
            self.oHelper.WriteStreamDMAExt(0x1,0,self.maxLBA,4096)
         else:
            self.oHelper.sequentialWriteDMAExt(0,self.maxLBA,4096,4096,11044)          
         
         #stream write from LBA0 to MAXLBA with 4096 sectors            
         ICmd.FlushCache()               
   
         #stream read from LBA0 to MAXLBA with 4096 sectors    
         if self.streaming_supported:         
            self.oHelper.ReadStreamDMAExt(0x1,0,self.maxLBA,4096)
         else:
            self.oHelper.sequentialReadDMAExt(0,self.maxLBA,4096,4096,11044)
                      
      ICmd.RestorePrimaryBuffer(BWR)
   #-------------------------------------------------------------------------------------------------------
   def EFCC(self):
      ScrCmds.insertHeader("Test4 - EFCC Test")     
      self.SFCC(PartitionPercentage = 2, StreamingTest = False)       

   #-------------------------------------------------------------------------------------------------------
   def SFCC50(self):
      ScrCmds.insertHeader("Test4 - SFCC50 Test")     
      self.SFCC(PartitionPercentage = 2)       
      
   #-------------------------------------------------------------------------------------------------------
   def CEFCC(self):
      ScrCmds.insertHeader("Test4 - CEFCC Test")    
      if self.streaming_supported:   
         self.SFCC()                
      else:   
         self.EFCC()
   #-------------------------------------------------------------------------------------------------------
   def SFCC(self, PartitionPercentage = 4, StreamingTest = True):
      ScrCmds.insertHeader("Test4 - SFCC Test")         

      
      #Set UDMA5, write 0x00 to whole dive, flush cache
      Set_UDMASpeed(5)           #set UDMA5      
      ICmd.MakeAlternateBuffer(BWR, 4096)               
      ICmd.ClearBinBuff(BWR)      
      self.oHelper.sequentialWriteDMAExt(0,self.maxLBA,4096,4096,11044) 
      ICmd.FlushCache()               

      PartitionSize = self.maxLBA/11      
      TotalBlksToXfr = (PartitionSize/PartitionPercentage/4096 + 1) * 4096
      Partition_startingLBA = {}
      Partition_startingLBA = dict([(i,PartitionSize *i) for i in range(0,11)])      

      TestTime = 64800 #18 hrs      
      StartTime = time.time()      
      EndTime = StartTime + TestTime 
      while time.time() < EndTime: 
         for mode in ['RLA_OFF','RLA_ON']:   
            #write 5A5A or A5A5 to first 25% of Partition 0 based on LBA evenness per 4096 sectors, flush cache
            ICmd.FillBuffByte(WBF,'A5A5',0,4096) 
            StartLBA = Partition_startingLBA[0]               
            EndLBA = Partition_startingLBA[0] + TotalBlksToXfr
            self.oHelper.sequentialWriteDMAExt(StartLBA,EndLBA,4096,4096,11044)       
            ICmd.FlushCache()      

            #Stream read partition 0, stream write to other partitions. Flush cache   
            if self.streaming_supported and StreamingTest:    
               self.oHelper.ConfigureStream(0x1)     
               self.oHelper.ReadStreamDMAExt(0x1,Partition_startingLBA[0],PartitionSize,4096)         
               for i in range(1,11):          
                  StartLBA = Partition_startingLBA[i]                  
                  if i == 10:                 
                     TotalBlks == self.maxLBA - StartLBA                                           
                  else:    
                     TotalBlks = Partition_startingLBA[i + 1] - StartLBA    
                  self.oHelper.WriteStreamDMAExt(0x1,StartLBA,TotalBlks,4096)
            else:
               self.oHelper.sequentialReadDMAExt(Partition_startingLBA[0],Partition_startingLBA[1],4096,4096,11044)          
               for i in range(1,11):          
                  StartLBA = Partition_startingLBA[i]                  
                  if i == 10:                  
                     EndLBA == self.maxLBA
                  else:    
                     EndLBA = Partition_startingLBA[i + 1] 
                  self.oHelper.sequentialWriteDMAExt(0x1,StartLBA,EndLBA,4096,4096,11044)
            ICmd.FlushCache()        
                  
            #Stream read partition 0 (25%),
            #Stream read other 10 partitions (25%), compare data with those of Partition 0
            if self.streaming_supported and StreamingTest:    
               self.oHelper.ConfigureStream(0x1)     
               self.oHelper.ReadStreamDMAExt(0x1,Partition_startingLBA[0],TotalBlksToXfr,4096)         
               for i in range(1,11):                  
                  self.oHelper.ReadStreamDMAExt(0x1,Partition_startingLBA[i],TotalBlksToXfr,4096,1)
            else:
               self.oHelper.sequentialReadDMAExt(Partition_startingLBA[0],Partition_startingLBA[0]+TotalBlksToXfr,4096,4096,11044)          
               for i in range(1,11):                  
                  StartLBA = Partition_startingLBA[i]     
                  EndLBA == StartLBA + TotalBlksToXfr             
                  self.oHelper.sequentialReadCmpDMAExt(StartLBA,EndLBA,4096,4096,1,11044) 
   
            #repeat above six by turning off RLA and Write Cache
            if mode == 'RLA_OFF':
               objMsg.printMsg("disable RLA and write cache.....")
               disable_ReadLookAhead()           
               disable_WriteCache()
                               
         objMsg.printMsg("enable RLA and write cache.....")      
         enable_ReadLookAhead()          
         enable_WriteCache()
         
      #Set UDMA5, write 0x00 to whole dive, flush cache      
      Set_UDMASpeed(5)           #set UDMA5      
      ICmd.ClearBinBuff(BWR)      
      self.oHelper.sequentialWriteDMAExt(0,self.maxLBA,4096,4096,11044) 
      ICmd.FlushCache()               
      
      ICmd.RestorePrimaryBuffer(BWR)               
           