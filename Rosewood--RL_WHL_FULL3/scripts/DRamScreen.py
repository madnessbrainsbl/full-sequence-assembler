#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description:
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/DRamScreen.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/DRamScreen.py#1 $
# Level:3

#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
import os
import ScrCmds
from Process import CProcess
import IntfClass
import MessageHandler as objMsg
from IOEDC import ChkIOEDC
from ICmdFactory import ICmd
from Rim import objRimType


##############################################################################################################
##############################################################################################################
class dramScreenException(Exception):
   def __init__(self,data):
      self.data = data
      objMsg.printMsg('dramScreenException')


##############################################################################################################
##############################################################################################################
class CDRamScreenTest(CProcess):
   """
   Test Purpose: Test the drives DRAM.
   Test Metrics: Verify DRAM.
   Setup/Assumptions: ( CCT @ 30 Secs, ~ 3 minutes )
   Basic Algorithm: Random Write Read PIO
   Failure: Fail on any DRAM error.
   """
   #---------------------------------------------------------------------------------------------------------#
   def __init__(self, dut, params=[]):
      objMsg.printMsg('*'*20+"DRam Screen init" + 20*'*')
      CProcess.__init__(self)

      self.DRamFiles = TP.prm_DRamFiles   # DRam File List
      CE,CP,CN,CV = ConfigId
      self.ConfigName = CN

      ret = IntfClass.CIdentifyDevice().ID            # Read device settings with identify device
      self.maxLBA = ret['IDDefaultLBAs'] - 1          # Default for 28-bit LBA
      if ret['IDCommandSet5'] & 0x400:                # Check bit 10
         objMsg.printMsg('Get ID Data 48 bit LBA is supported')
         self.maxLBA = ret['IDDefault48bitLBAs'] - 1

      self.minLBA = 0
      self.startLBA    = TP.prm_DRamSettings["StartLBA"]
      self.midLBA      = TP.prm_DRamSettings["MidLBA"]
      self.endLBA      = TP.prm_DRamSettings["EndLBA"]
      self.stepCount   = TP.prm_DRamSettings["StepCount"]
      self.sectorCount = TP.prm_DRamSettings["SectorCount"]
      self.stampFlag   = TP.prm_DRamSettings["StampFlag"]
      self.compareFlag = TP.prm_DRamSettings["CompareFlag"]
      self.MaxIoedcCount = TP.prm_DRamSettings.get("MaxIoedcCount",0)

      objMsg.printMsg('Start LBA: %d' % TP.prm_DRamSettings["StartLBA"])
      objMsg.printMsg('Mid LBA: %d' % TP.prm_DRamSettings["MidLBA"])
      objMsg.printMsg('End LBA: %d' % TP.prm_DRamSettings["EndLBA"])
      objMsg.printMsg('Step Count: %d' % TP.prm_DRamSettings["StepCount"])
      objMsg.printMsg('Sector Count: %d' % TP.prm_DRamSettings["SectorCount"])
      objMsg.printMsg('Stamp Flag: %d' % TP.prm_DRamSettings["StampFlag"])
      objMsg.printMsg('Compare Flag: %d' % TP.prm_DRamSettings["CompareFlag"])
      objMsg.printMsg('Min LBA: %d' % self.minLBA)
      objMsg.printMsg('Max LBA: %d' % self.maxLBA)

   #---------------------------------------------------------------------------------------------------------#
   def dRamScreenTest(self, numLoops=1):
      """
      Execute function loop.
      @return result: Returns OK or FAIL
      """
      objMsg.printMsg('*'*20+"DRam Screen Test" + 20*'*')

      IOEdcChk = ChkIOEDC()

      if numLoops > 1:
         objMsg.printMsg("NumLoops: %s" % numLoops)

      if DEBUG > 0:
         objMsg.printMsg("Disabling CRC Retries for DRAM testing.")

      ICmd.CRCErrorRetry(0)

      try:
         for loopCnt in range(numLoops):
            if numLoops > 1:
               objMsg.printMsg('Loop: ' + str(loopCnt+1) + '*'*5+"DRam Screen Test" + 20*'*')
            self.doSeqWriteThenReadDMA()

         result = 0
      except dramScreenException, M:
         ioEDCError = False
         if IOEdcChk.IOEDCEnabled:
            ioEDCError = IOEdcChk.checkIOEDC(M.data)
            if ioEDCError:
               IOEdcChk.ParseErrorAndAssignCode(M.data)

         ScrCmds.raiseException(13460, M.data)

      passData = {'STS':'80'}
      if IOEdcChk.IOEDCEnabled:
         ioEDCError = IOEdcChk.checkIOEDC(passData, self.MaxIoedcCount)
         if ioEDCError:
            IOEdcChk.ParseErrorAndAssignCode(passData)

      ICmd.CRCErrorRetry(1)

      if testSwitch.FE_0120911_347508_DRAMSCREEN_CLEANUP:
         self.doCleanup()  # DRamScreen Cleanup

      if testSwitch.IOWriteReadRemoval:
         RWDict = []
         RWDict.append ('Write')
         RWDict.append (self.startLBA)
         RWDict.append (self.endLBA)
         RWDict.append ('CDRamScreenTest')
         objMsg.printMsg('WR_VERIFY appended - %s' % (RWDict))
         TP.RWDictGlobal.append (RWDict)
      return result

   #----------------------------------------------------------------------------------------------------
   def doSeqWriteThenReadDMA(self):
      data = ICmd.SetFeatures(0x03, 0x45)
      if data['LLRET'] != 0:
         objMsg.printMsg("Write Read UDMA SetFeatures data = %s" % str(data))
         raise dramScreenException(data)
      #-------------------------------------------------------------------------------------------------
      for self.patternfile in self.DRamFiles:
         self.filename = os.path.join(UserDownloadsPath, self.ConfigName, self.patternfile)
         if DEBUG > 0:
            objMsg.printMsg("Create Pattern File Path = %s" % self.filename)

         if not testSwitch.virtualRun:
            self.patternfile = open(self.filename,'rb')

            try:

               self.patterndata = self.patternfile.read()
               objMsg.printMsg("Read Pattern File= %s" % self.filename)

            finally:
               self.patternfile.close()
               #objMsg.printMsg("Close File")
         else:
            self.patterndata = '\x00\x00'

         ICmd.ClearBinBuff(BWR)
         #objMsg.printMsg("Clear Bin Buffer")
         ICmd.FillBuffer(1, 0, self.patterndata)
         #objMsg.printMsg("Fill Write Buffer")

         if objRimType.IOInitRiser():
            data = ICmd.BufferCompareTest( self.startLBA, self.endLBA-self.startLBA, 1, len(self.patterndata), exc = 0)
            if data['LLRET'] == 0:
               objMsg.printMsg('\tDRam Screen Pattern = %s Passed' % self.filename)
            else:
               objMsg.printMsg('\tDRam Screen Pattern = %s Failed' % self.filename)
               raise dramScreenException(data)

         elif objRimType.IOInitRiser():
            internalStep =  MAX_INITIATOR_BUFFER_BLK_SIZE-1
            for startLBA in xrange(self.startLBA,  self.endLBA, internalStep):
               endLBA = min(self.endLBA,  startLBA + internalStep)

               ICmd.HardReset()


               data = ICmd.SequentialWRDMA(startLBA, endLBA, self.stepCount, self.sectorCount, self.stampFlag, self.compareFlag, stSuppressResults = ST_SUPPRESS__CM_OUTPUT)

               objMsg.printMsg("\tWrite Read UDMA data = %s" % str(data))
               if data['LLRET'] != 0:
                  objMsg.printMsg('\tDRam Screen Pattern = %s Failed' % self.filename)
                  raise dramScreenException(data)


            objMsg.printMsg('\tDRam Screen Pattern = %s Passed' % self.filename)

         else:
            data = ICmd.SequentialWRDMA(self.startLBA, self.endLBA, self.stepCount, self.sectorCount, self.stampFlag, self.compareFlag)
            objMsg.printMsg("\tWrite Read UDMA data = %s" % str(data))

            if data['LLRET'] == 0:
               objMsg.printMsg('\tDRam Screen Pattern = %s Passed' % self.filename)
            else:
               objMsg.printMsg('\tDRam Screen Pattern = %s Failed' % self.filename)
               raise dramScreenException(data)

   def doCleanup(self):
      retry = 2
      result = ICmd.ClearBinBuff(WBF)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(11044, "DRamScreen Cleanup - Failed to fill buffer for zero write")
      for i in range(retry):
         result = ICmd.SequentialWriteDMA(self.startLBA, self.endLBA, self.stepCount, self.sectorCount)
         objMsg.printMsg('DRamScreen Cleanup - Result %s' %str(result))
         if result['LLRET'] != 0:
            if i == 0:
               objMsg.printMsg('SequentialWriteDMA retry times 1')
            else:
               ScrCmds.raiseException(12658, "DRamScreen Cleanup Failed!")
         else:
            objMsg.printMsg('DRamScreen Cleanup passed!')
            ICmd.FlushCache()
            break

   #---------------------------------------------------------------------------------------------------------#
   def makeDBLOutput(self, tableName):
      objMsg.printMsg('makeDBLOutput 1')
      #objMsg.printDict(self.paramData)
      dblogObj = self.dut.dblData

      objMsg.printMsg('makeDBLOutput 2')

      objMsg.printMsg("%s - FileNames=%s" %(tableName, self.dRamFiles))
      dblogObj.Tables(tableName).addRecord(
         {
         'FILENAMES': self.dRamFiles,
         })
      objMsg.printMsg('makeDBLOutput 3')


class CPCBA(CProcess):
   def __init__(self, dut, params = []):
      CProcess.__init__(self)

   def getPhysicalDramSize(self):

      if self.dut.sptActive.getMode() == self.dut.sptActive.availModes.mctBase:
         self.St({'test_num':166,'prm_name':'Get_Physical_DRAM_Size','CWORD1':0x10, 'timeout': 300})

         if testSwitch.virtualRun:
            dramSize = 32000000
         else:
            dramSize = int(self.dut.dblData.Tables('P166_DRAM_INFO').tableDataObj()[-1]['DRAM_SIZE'].replace('"',''))
      else:
         import sdbpCmds
         ret = sdbpCmds.getDriveBasicInformation()
         dramSize = ret.get('BufferSizeInBytes',0)

      self.dut.driveattr['DRAM_PHYS_SIZE'] = dramSize
      #objMsg.printMsg('Physical Dram Size = %s' %self.dut.driveattr['DRAM_PHYS_SIZE'])
