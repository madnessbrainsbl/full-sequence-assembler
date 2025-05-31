#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: multiple sequential/random/timed read write tests
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/ZoneWriteStress.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/ZoneWriteStress.py#1 $
# Level:3
#---------------------------------------------------------------------------------------------------------#
from Constants import *

import time
from math import floor
from random import randint
import DbLog
from TestParamExtractor import TP
from ICmdFactory import ICmd

##############################################################################################################
##############################################################################################################
class zoneStressException(Exception):
   def __init__(self,data):
      self.data = data

##############################################################################################################
##############################################################################################################
class zoneStressScreen:
   """
   Test Purpose: Screen marginal write based drive phenomena for quality increase
   Test Metrics: Hard errors, CRC Errors, timed performance in operations.
   Setup/Assumptions: ( CCT @ 30 Secs, Fail on any CRC, target time ~ 1 hour )
   Patterns: All zero Patterns.
   Basic Algorithm:
   Timed Read and Write sequential pass of the zone
      Random or Butterfly seek writes to zone
      Multiple sequential writes across zone
      Dwell writes sequentially across zone
      New latch immediate testing, during DST... Randy/ChuSon's stuff...
   Timed Read and Write sequential pass of the zone
   Fail on any hard error, or CRC failure
   Fail for change in time of Read or Write pass start or any or finish steps  > than TBD
   Fail for outlier to population data for time of Read or Write pass,   TBD
   """
   #---------------------------------------------------------------------------------------------------------#
   def __init__(self,hardFailLimit = 1, zoneLocation = 'ID', commandTMO = 30):
      self.hardFailLimit = hardFailLimit
      self.zoneLocation  = zoneLocation
      self.commandTMO = int(commandTMO)
      self.paramData     = {}
      self.paramData["multiSeqWrites"] = []
      self.paramData["randomWritesInZone"] = []
      self.paramData["DSTAbortScreens"] = []
      self.paramData["dwellWriteSeq"] = []
      self.paramData["timedZoneRead"] = []

   #---------------------------------------------------------------------------------------------------------#
   def __call__(self, numLoops=1):
      """
      Execute function loop.
      @return result: Returns OK or FAIL
      """
      objMsg.printMsg('*'*20+"Zone Write Stress Test" + 20*'*')
      objMsg.printMsg("NumLoops: %s" % numLoops)
      try:
         self.maxLBAs = self.getMaxLBAs()
         self.myRegion = CLBARegions(self.maxLBAs, 2)
         self.zoneTuple = self.myRegion.regions[self.zoneLocation]
         ICmd.SetIntfTimeout(self.commandTMO*1000) #Set command timeout to 30 seconds
         ClearBinBuff(WBF)       #Set up 0's pattern for writes
         for loopCnt in range(numLoops):
            objMsg.printMsg('Loop: ' + str(loopCnt+1) + '*'*5+"Zone Write Stress Test" + 20*'*')
            self.DSTAbortScreens()
            self.randomWritesInZone(self.zoneTuple)
            self.timedZoneRead(self.zoneTuple)
            self.multiSeqWrites(self.zoneTuple,5)
            self.timedZoneRead(self.zoneTuple)
            self.dwellWriteSeq(self.zoneTuple)
            self.timedZoneRead(self.zoneTuple)
         result = 0
         self.myRegion.clearRegion('ID') #If we completed the testing then let's clear everything
      except zoneStressException, M:
         objMsg.printMsg("Failure Traceback: %s,%s,%s" % StackFrameInfo(1))
         objMsg.printMsg("Fail Info: " + str(M.data))
         result = 1
         driveattr['failcode'] = M.data
      except:
         objMsg.printMsg("Failure Traceback: %s,%s,%s" % StackFrameInfo(1))
         objMsg.printMsg("Fail Info: " + str(M.data))
         result = 1
         driveattr['failcode'] = failcode["Zone Write Stress"]

      self.makeDBLOutput()
      ICmd.SetIntfTimeout(TP.prm_IntfTest["Default CPC Cmd Timeout"]*1000)
      return result

   #---------------------------------------------------------------------------------------------------------#
   def makeDBLOutput(self):
      dblogObj = DbLog.DbLog()
      tableName = 'ZN_WRITE_STRESS'
      for key in self.paramData.keys():
         counter = 1
         for item in self.paramData[key]:
            objMsg.printMsg("%s,%s,%s" % (key,counter,item))
            dblogObj.Tables(tableName).addRecord( {
                                                        'TEST_NAME':str(key),
                                                        'RUN_NUM': counter,
                                                        'RUN_TIME': item
                                                        })
            counter +=1
         pass
      objMsg.printMsg(str(dblogObj))
      xrf.addInstance('parametric_dblog', dblogObj)

   #---------------------------------------------------------------------------------------------------------#
   def getMiniZones(self, numZones, inputZone):
      """
      Generates mini-Zones based on input zone.
      @param numZones: Number of miniZones to return
      @param inputZone: Iterable of (minLBA, maxLBA) for the large zone to generate mini-zones
      @return zones: List of tuples containing (minLBA, maxLBA)
      """
      inZoneSize = inputZone[1]-inputZone[0]-1
      miniZoneSize = floor(inZoneSize / numZones)
      zones = []
      zoneMinLBA = inputZone[0]

      for currZone in range(numZones):
         zoneMaxLBA = zoneMinLBA + miniZoneSize
         if zoneMaxLBA > inputZone[1]:
            zoneMaxLBA = inputZone[1]
         zones.append((zoneMinLBA, zoneMaxLBA))
         zoneMinLBA = zones[-1][1]+1

      return zones

   #---------------------------------------------------------------------------------------------------------#
   def randomWritesInZone(self, zoneTuple, numBlks=100, numWrites=250):
      """
      Within the zone input into the function we need to perform random writes in that zone w/ zeros pattern.
      @param zoneTuple  - Gives us starting and ending LBA numbers
      @param numBlks    - Used to calculate step size
      @param numWrites  - Number of writes executed in a single CPC command
      """
      # setup test parameters
      objMsg.printMsg('Random (Butterfly Seek) Writes in Zone')
      #self.paramData["randomWritesInZone"] = []
      startTime = time.time()

      # set the DMA transfer rate
      data = ICmd.SetFeatures(0x03, 0x45) # try UDMA100
      if data['LLRET'] != 0:
         objMsg.printMsg("Last Command Response: %s" % `data`)
         raise zoneStressException(failcode['Cit SetFeature'])

      # setup ATA command parameters
      minLBA, maxLBA = zoneTuple
      minSectCnt = maxSectCnt = 256
      stepLBA = floor((maxLBA-minLBA)/numBlks) # calculate step size based on number of blocks
      ClearBinBuff(WBF) # Set up 0's pattern for writes
      objMsg.printMsg('minLBA=%d maxLBA=%d stepLBA=%d numWrites=%d' % (minLBA, maxLBA, stepLBA, numWrites))

      # Do butterfly seek writes
      leftPtr = minLBA; rightPtr = maxLBA
      error = 0; data = {}
      while leftPtr < maxLBA:
         if leftPtr < rightPtr:
            #print('Random Write DMA Ext: startLBA=%d endLBA=%d minSectCnt=%d maxSectCnt=%d numWrites=%d' % (leftPtr, rightPtr, minSectCnt, maxSectCnt, numWrites))
            data = RandomWriteDMAExt(leftPtr, rightPtr, minSectCnt, maxSectCnt, numWrites)
         else:
            #print('Random Write DMA Ext: startLBA=%d endLBA=%d minSectCnt=%d maxSectCnt=%d numWrites=%d' % (rightPtr, leftPtr, minSectCnt, maxSectCnt, numWrites))
            data = RandomWriteDMAExt(rightPtr, leftPtr, minSectCnt, maxSectCnt, numWrites)
         #print(data)
         if data['LLRET'] != 0: # cmd err check
            error = 1
            break
         leftPtr  = leftPtr  + stepLBA # advance left pointer
         rightPtr = rightPtr - stepLBA # advance right pointer

      # test end actions
      endTime = time.time()
      self.paramData["randomWritesInZone"].append(endTime-startTime)
      objMsg.printMsg("Execution Time: %s" % str(endTime-startTime))

      # check error here
      if error:
         objMsg.printMsg("Last Command Response: %s" % `data`)
         raise zoneStressException(failcode['MQM Random Write'])

   #---------------------------------------------------------------------------------------------------------#
   def multiSeqWrites(self, zoneTuple, numMiniZones = 16):
      """
      Algorithm:
         Break input zone into numMiniZones and perform sequential writes to each mini-zone. Randomize minizone write order at init.
      Use SequentialWRDMAExt
      @param zoneTuple: iterable of (minLBA, maxLBA)
      @param numMiniZones: Number of miniZones to execute the random sequentials in
      @return time: Execution time of the full write pass
      """
      miniZones = self.getMiniZones(numMiniZones,zoneTuple)
      ClearBinBuff(WBF)
      randZones = []
      while len(miniZones)>0:
         rZone = randint(0,len(miniZones)-1)
         randZones.append(miniZones[rZone])
         del miniZones[rZone]
      startTime = time.time()
      objMsg.printMsg("multiSeqWrites Start: %s" % str(startTime))
      try:
         for zone in randZones:
            result = ICmd.SequentialWRDMAExt(zone[0],zone[1],256,256,stampFlag = 0,compareFlag=0)
            if not result['LLRET'] == 0:
               raise zoneStressException(failcode['CUS SeqDMAWrt'])
      finally:
         endTime = time.time()
         objMsg.printMsg("multiSeqWrites End: %s" % str(endTime))
         objMsg.printMsg("multiSeqWrites Execution Time: %s" % str(endTime-startTime))
         self.paramData["multiSeqWrites"].append(endTime-startTime)

   #---------------------------------------------------------------------------------------------------------#
   def DSTAbortScreens(self):
      startTime = time.time()
      objMsg.printMsg("DST Interrupt Start: %s" % str(startTime))
      result = OK
      dstInteruptLoop = 1 # 6
      seekInteruptLoop = 1 # 10
      unloadLoop = 1 # 10
      if result == OK and MQM_DST_INTERRUPT == ON:
         result =  DSTInterrupt(Type='Short',loops=dstInteruptLoop) #6
      if result == OK and MQM_DST_INTERRUPT == ON:
         result =  DSTInterrupt(Type='Long',loops=dstInteruptLoop) #6
      if result == OK and MQM_SEEK_INTERRUPT == ON:
         result =  SeekInterrupt(loops=seekInteruptLoop) #10
      if result == OK and MQM_UNLOAD_IMMEDIATE == ON:
         result =  UnloadImmediate(Type='WRW',head=0xA0,loops=unloadLoop,option=1)
      if result == OK and MQM_UNLOAD_IMMEDIATE == ON:
         result =  UnloadImmediate(Type='RWR',head=0xA0,loops=unloadLoop,option=2)
      if result == OK and MQM_UNLOAD_IMMEDIATE == ON:
         result =  UnloadImmediate(Type='WRW',head=0xA5,loops=unloadLoop,option=3)
      if result == OK and MQM_UNLOAD_IMMEDIATE == ON:
         result =  UnloadImmediate(Type='RWR',head=0xA5,loops=unloadLoop,option=4)

      endTime = time.time()
      objMsg.printMsg("DST Interrupt End: %s" % str(endTime))
      objMsg.printMsg("DST Interrupt Execution Time: %s" % str(endTime-startTime))
      self.paramData["DSTAbortScreens"].append(endTime-startTime)
      if not result == OK:
         raise zoneStressException(driveattr['failcode'])
      return endTime-startTime

   #---------------------------------------------------------------------------------------------------------#
   def dwellWriteSeq(self, zoneTuple, numBlks=50, dwellTime=10):
      """
      @param zoneTupe   : tuple of (minLBA, maxLBA) for test to operate within
      @param numBlks    : number of blocks zone is divided into
      @param dwellTime  : in seconds
      Algorithm:
         Write Sequential across the zone blockwise w/ dwellTime sleeps inbetween blockWrites
      """
      # setup test parameters
      objMsg.printMsg('Dwell Write Sequential')
      #self.paramData["dwellWriteSeq"] = []
      startTime = time.time()

      # set the DMA transfer rate
      data = ICmd.SetFeatures(0x03, 0x45) # try UDMA100
      if data['LLRET'] != 0:
         objMsg.printMsg("Last Command Response: %s" % `data`)
         raise zoneStressException(failcode['Cit SetFeature'])

      # setup ATA command parameters
      minLBA, maxLBA = zoneTuple
      sectCount = stepLBA = 256 # 48bit LBA addressing
      writeBlockSize = long((maxLBA-minLBA)/numBlks) # divide range into fixed size blocks
      ICmd.ClearBinBuff(WBF) #Set up 0's pattern for writes
      objMsg.printMsg('minLBA=%d maxLBA=%d stepLBA=%d numBlks=%d blkSize=%d' % (minLBA, maxLBA, stepLBA, numBlks, writeBlockSize))

      # perform sequential write DMA (ext mode)
      error = 0; data = {}
      startLBA = minLBA # init start LBA pointer
      for i in range(numBlks):
         endLBA = min(startLBA+writeBlockSize, maxLBA) # using "min" function since we should not exceed max LBA of disk
         #print('SEQ Write DMA Ext: startLBA=%s endLBA=%s stepLBA=%s sectorCount=%s stampFlag=0' % (startLBA, endLBA, stepLBA, sectCount))
         data = ICmd.SequentialWriteDMAExt(startLBA, endLBA, stepLBA, sectCount, stampFlag=0)
         #print(data)
         if data['LLRET'] != 0:
            error = 1
            break
         startLBA = endLBA # advance start pointer
         time.sleep(dwellTime) # sleep in seconds

      # test end actions
      endTime = time.time()
      self.paramData["dwellWriteSeq"].append(endTime-startTime)
      objMsg.printMsg("Execution Time: %s" % str(endTime-startTime))

      # error actions
      if error:
         objMsg.printMsg("Last Command Response: %s" % `data`)
         raise zoneStressException(failcode['CUS SeqDMAWrt'])

   #---------------------------------------------------------------------------------------------------------#
   def timedZoneRead(self, zoneTuple):
      """
         Algorithm:
            Use SequentialReadDMAExt to measure performance.
            Must objMsg.printMsg to result file the performance metric and make considerations for sending this data to oracle <return data>
            Fails on CRC error (need specific FC)
            Fails on read error
         @return executionTime: Execution time of zone read operation.
      """
      CmdStartTime = time.time()
      sectCount = stepLBA = 256 # 48bit LBA addressing
      data = ICmd.SequentialReadDMAExt(zoneTuple[0], zoneTuple[1], sectCount, stepLBA, stampFlag=0, compareFlag=0)
      CmdEndTime = time.time()
      CmdTime=(CmdEndTime-CmdStartTime)

      objMsg.printMsg('ZoneWriteStress Read Performance %s' % str(CmdTime))
      self.paramData["timedZoneRead"].append(CmdEndTime-CmdStartTime)
      if data['LLRET'] == OK:
         objMsg.printMsg('ZoneWriteStress Read Performance passes')
      else:
         if data['STS'] == '81' and data['ERR'] == '132':
            objMsg.printMsg('CRC Read error')
            raise zoneStressException(failcode["CRC Sequential Read Failure"] )
         else:
            objMsg.printMsg("Hard Read Error")
            raise zoneStressException(failcode["Sequential Read Failure"])

   #---------------------------------------------------------------------------------------------------------#
   def getMaxLBAs(self):
      """
         Method returns max number of LBAs on disk
         Takes into account if 48-bit LBA is supported
      """
      ret = IdentifyDevice()
      if ret['LLRET'] != 0:
         raise zoneStressException(failcode['Fin ID Data'])

      maxLBAs = ret['IDDefaultLBAs']
      if ret['IDCommandSet5'] & 0x400:      # check bit 10
         objMsg.printMsg('Get ID Data 48 bit LBA is supported')
         maxLBAs =  ret['IDDefault48bitLBAs']

      return maxLBAs
