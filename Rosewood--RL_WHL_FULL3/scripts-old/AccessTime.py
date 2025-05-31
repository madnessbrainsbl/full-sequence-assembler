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
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/AccessTime.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/AccessTime.py#1 $
# Level:3
#---------------------------------------------------------------------------------------------------------#

from Constants import *
import time
import DbLog
import ScrCmds
from Process import CProcess
import IntfClass
from TestParamExtractor import TP
import MessageHandler as objMsg
from ICmdFactory import ICmd

##############################################################################################################
##############################################################################################################
class accessTimeException(Exception):
   def __init__(self,data):
      self.data = data
      objMsg.printMsg('accessTimeException')

##############################################################################################################
##############################################################################################################
class CAccessTimeTest(CProcess):
   """
   Test Purpose: Measure Access Time for single, random, and full stroke seeks.
   Test Metrics: Check the measured time against the specified limits.
   Setup/Assumptions: ( CCT @ 30 Secs, ~ 3 minutes )
   Basic Algorithm:
   - Single Seeks
      - Single track seeks at the OD
      - Single track seeks at the ID
   - Random Seeks
      - Random Seeks between LBA 0 and Max LBA
   - Full Stroke Seeks
      - Full stroke seeks from OD to ID
      - Full stroke seeks from ID to OD
   Failure: Fail on any measured seek time above the specified limit.
   """
   #---------------------------------------------------------------------------------------------------------#
   def __init__(self, dut, params=[]):
      objMsg.printMsg('*'*20+"Access Time init" + 20*'*')
      CProcess.__init__(self)
      self.overheadLimit   = TP.prm_AccessTime["Overhead_Limit"]        # Overhead Limit
      self.singleLimit     = TP.prm_AccessTime["Single_Limit"]          # Single Seek Limit
      self.randomLimit     = TP.prm_AccessTime["Random_Limit"]          # Random Seek Limit
      self.fullStrokeLimit = TP.prm_AccessTime["FullStroke_Limit"]      # Full Stroke Seek Limit
      self.loopCount       = TP.prm_AccessTime["Loop_Count"]            # Number of seek commands
      self.tossLimit       = TP.prm_AccessTime["Toss_Limit"]            # Toss excessive values (ms)
      self.seekType        = TP.prm_AccessTime["Seek_Type"]             # seek type - seek, write or read
      self.overheadLBA     = TP.prm_AccessTime["Overhead_LBA"]          # LBA to calculate overhead
      self.single_avg      = 'NONE'                                  # Default Single Seek Avgerage
      self.random_avg      = 'NONE'                                  # Default Random Seek Avgerage
      self.full_oi_avg     = 'NONE'                                  # Default Full OD/ID Avgerage
      self.overheadValue   = 0                                       # Default Overhead value

      ret = IntfClass.CIdentifyDevice().ID # read device settings with identify device
      self.maxLBA = ret['IDDefaultLBAs'] - 1 # default for 28-bit LBA
      if ret['IDCommandSet5'] & 0x400:      # check bit 10
         objMsg.printMsg('Get ID Data 48 bit LBA is supported')
         self.maxLBA = ret['IDDefault48bitLBAs'] - 1
      self.maxCYL = ret['IDLogicalCyls'] - 1
      self.minCYL = 1; self.minLBA = 0
      objMsg.printMsg('Min CYL: %d' % self.minCYL)
      objMsg.printMsg('Max CYL: %d' % self.maxCYL)
      objMsg.printMsg('Min LBA: %d' % self.minLBA)
      objMsg.printMsg('Max LBA: %d' % self.maxLBA)
      objMsg.printMsg('Loop Count: %d' % self.loopCount)
   #---------------------------------------------------------------------------------------------------------#
   def accessTimeTest(self, numLoops=1):
      """
      Execute function loop.
      @return result: Returns OK or FAIL
      """
      objMsg.printMsg('*'*20+"Access Time Test" + 20*'*')
      if numLoops > 1:
         objMsg.printMsg("NumLoops: %s" % numLoops)
      try:
         for loopCnt in range(numLoops):
            if numLoops > 1:
               objMsg.printMsg('Loop: ' + str(loopCnt+1) + '*'*5+"Access Time Test" + 20*'*')
            #self.overheadAccess(self.overheadLBA, self.loopCount, self.tossLimit, self.seekType)
            self.singleSeekAccess(self.minCYL, self.maxCYL, self.loopCount, self.seekType)
            self.randomSeekAccess(self.minLBA, self.maxLBA, self.loopCount, self.seekType)
            self.fullStrokeAccess(self.minLBA, self.maxLBA, self.loopCount, self.seekType)
         result = 0
      except accessTimeException, M:
         #self.makeDBLOutput('ACCESS_TIME')
         objMsg.printMsg('makeDBLOutput complete')
         ScrCmds.raiseException(13450, M.data)

      #self.makeDBLOutput('ACCESS_TIME')
      objMsg.printMsg('makeDBLOutput complete')
      return result

   #---------------------------------------------------------------------------------------------------------#
   def overheadAccess(self, overheadLBA, loopCount, tossLimit, seekType):
      """
      Algorithm:
         Calculates access time overhead reading one LBA.
         @param overheadLBA: LBA to use for the overhead calculations.
         @param loopCount: Number of loops/seeks to issue.
         @param tossLimit: Excessive values to Toss(remove from the total).
         @param seekType: The type of seek - seek, write or read.
         Fails on ATA command timeout.
         Fails on exceeding overhead limit.
      """
      ICmd.SetIntfTimeout(60000)
      objMsg.printMsg('Start ICmd.CommandOverheadCmd')
      self.co_data = ICmd.CommandOverhead(overheadLBA, loopCount, tossLimit, seekType, timeout = 60, exc=0)
      objMsg.printMsg('ICmd.CommandOverheadCmd data= %s' % self.co_data)
      if self.co_data.has_key('OvrHeadTm') == 0:
         self.overheadValue = self.overheadLimit + 1
         objMsg.printMsg('Missing OvrHeadTm key. co_data=%s' % self.co_data)
      else:
         self.overheadValue = float(self.co_data['OvrHeadTm']) * 0.0001
      if self.overheadValue > self.overheadLimit:
         objMsg.printMsg('Failed Command Overhead=%.3f Limit=%.3f' % (self.overheadValue, self.overheadLimit))
         raise accessTimeException(self.co_data)
      else:
         objMsg.printMsg('Passed Command Overhead=%.3f Limit=%.3f' % (self.overheadValue, self.overheadLimit))
      ICmd.SetIntfTimeout(TP.prm_IntfTest["Default CPC Cmd Timeout"]*1000)

   #---------------------------------------------------------------------------------------------------------#
   def singleSeekAccess(self, minCYL, maxCYL, loopCount, seekType):
      """
      Algorithm:
         Calculates single seek access time OD and ID avgeraged.
         @param minCYL: OD Cylinder for single seeks.
         @param maxCYL: ID Cylinder for single Seeks.
         @param loopCount: Number of loops/seeks to issue.
         @param seekType: The type of seek - seek, write or read.
         Fails on ATA command timeout.
         Fails on exceeding single seek limit.
      """
      self.ss_data = ICmd.SingleSeekTime(minCYL, maxCYL, loopCount, seekType, timeout = 60, exc=0)
      if self.ss_data.has_key('SnSkMinTm') == 0:
         objMsg.printMsg('Missing SnSkMinTm key. ss_data=%s' % self.ss_data)
         self.single_min = self.singleLimit + 1
         self.single_max = self.singleLimit + 1
         self.single_avg = self.singleLimit + 1
      else:
         self.single_min = float(self.ss_data['SnSkMinTm']) * 0.0001 - self.overheadValue
         self.single_max = float(self.ss_data['SnSkMaxTm']) * 0.0001 - self.overheadValue
         self.single_avg = float(self.ss_data['SnSkAvgTm']) * 0.0001 - self.overheadValue
      if self.single_avg > self.singleLimit:
         objMsg.printMsg('Failed Single Seek - Min=%.3f Max=%.3f Avg=%.3f Limit=%.3f' % \
                        (self.single_min, self.single_max, self.single_avg, self.singleLimit))
         raise accessTimeException(self.ss_data)
      else:
         objMsg.printMsg('Passed Single Seek - Min=%.3f Max=%.3f Avg=%.3f Limit=%.3f' % \
                        (self.single_min, self.single_max, self.single_avg, self.singleLimit))

   #---------------------------------------------------------------------------------------------------------#
   def randomSeekAccess(self, minLBA, maxLBA, loopCount, seekType):
      """
      Algorithm:
         Calculates random seek access time.
         @param minLBA: OD LBA for random seeks.
         @param maxLBA: ID LBA for random Seeks.
         @param loopCount: Number of loops/seeks to issue.
         @param seekType: The type of seek - seek, write or read.
         Fails on ATA command timeout.
         Fails on exceeding single seek limit.
      """
      self.rs_data = ICmd.RandomSeekTime(minLBA, maxLBA, loopCount, seekType, timeout = 300, exc=0)
      if self.rs_data.has_key('RnSkMinTm') == 0:
         objMsg.printMsg('Missing RnSkMinTm key. rs_data=%s' % self.rs_data)
         self.random_min = self.randomLimit + 1
         self.random_max = self.randomLimit + 1
         self.random_avg = self.randomLimit + 1
      else:
         self.random_min = float(self.rs_data['RnSkMinTm']) * 0.0001 - self.overheadValue
         self.random_max = float(self.rs_data['RnSkMaxTm']) * 0.0001 - self.overheadValue
         self.random_avg = float(self.rs_data['RnSkAvgTm']) * 0.0001 - self.overheadValue
      if self.random_avg > self.randomLimit:
         objMsg.printMsg('Failed Random Seek - Min=%.3f Max=%.3f Avg=%.3f Limit=%.3f' % \
                        (self.random_min, self.random_max, self.random_avg, self.randomLimit))
         raise accessTimeException(self.rs_data)
      else:
         objMsg.printMsg('Passed Random Seek - Min=%.3f Max=%.3f Avg=%.3f Limit=%.3f' % \
                        (self.random_min, self.random_max, self.random_avg, self.randomLimit))

   #---------------------------------------------------------------------------------------------------------#
   def fullStrokeAccess(self, minLBA, maxLBA, loopCount, seekType):
      """
      Algorithm:
         Calculates full storke access time OD-ID and ID-OD.
         @param minLBA: OD LBA for full stroke seeks.
         @param maxLBA: ID LBA for full stroke Seeks.
         @param loopCount: Number of loops/seeks to issue.
         @param seekType: The type of seek - seek, write or read.
         Fails on ATA command timeout.
         Fails on exceeding full stroke limit.
      """
      self.fs_data = ICmd.FullSeekTime(minLBA, maxLBA, loopCount, seekType, timeout = 300, exc=0)
      if self.fs_data.has_key('FuSkMinTmOI') == 0:
         objMsg.printMsg('Missing FuSkMinTmOI key. fs_data=%s' % self.fs_data)
         self.full_oi_min = self.fullStrokeLimit + 1
         self.full_oi_max = self.fullStrokeLimit + 1
         self.full_oi_avg = self.fullStrokeLimit + 1
      else:
         self.full_oi_min = float(self.fs_data['FuSkMinTmOI']) * 0.0001 - self.overheadValue
         self.full_oi_max = float(self.fs_data['FuSkMaxTmOI']) * 0.0001 - self.overheadValue
         self.full_oi_avg = float(self.fs_data['FuSkAvgTmOI']) * 0.0001 - self.overheadValue
      if self.full_oi_avg > self.fullStrokeLimit:
         objMsg.printMsg('Failed Full Seek ODID - Min=%.3f Max=%.3f Avg=%.3f Limit=%.3f' % \
                        (self.full_oi_min, self.full_oi_max, self.full_oi_avg, self.fullStrokeLimit))
         raise accessTimeException(self.fs_data)
      else:
         objMsg.printMsg('Passed Full Seek ODID - Min=%.3f Max=%.3f Avg=%.3f Limit=%.3f' % \
                        (self.full_oi_min, self.full_oi_max, self.full_oi_avg, self.fullStrokeLimit))

      self.full_io_min = float(self.fs_data['FuSkMinTmIO']) * 0.0001 - self.overheadValue
      self.full_io_max = float(self.fs_data['FuSkMaxTmIO']) * 0.0001 - self.overheadValue
      self.full_io_avg = float(self.fs_data['FuSkAvgTmIO']) * 0.0001 - self.overheadValue
      if self.full_io_avg > self.fullStrokeLimit:
         objMsg.printMsg('Failed Full Seek IDOD - Min=%.3f Max=%.3f Avg=%.3f Limit=%.3f' % \
                        (self.full_io_min, self.full_io_max, self.full_io_avg, self.fullStrokeLimit))
         raise accessTimeException(self.fs_data)
      else:
         objMsg.printMsg('Passed Full Seek IDOD - Min=%.3f Max=%.3f Avg=%.3f Limit=%.3f' % \
                        (self.full_io_min, self.full_io_max, self.full_io_avg, self.fullStrokeLimit))

   #---------------------------------------------------------------------------------------------------------#
   def makeDBLOutput(self, tableName):
      objMsg.printMsg('makeDBLOutput 1')
      #objMsg.printDict(self.paramData)
      dblogObj = self.dut.dblData
      dblogObj.getDBL()
      objMsg.printMsg('makeDBLOutput 2')

      objMsg.printMsg("%s - Single=%s Random=%s Full=%s" % \
                     (tableName, self.single_avg, self.random_avg, self.full_oi_avg))
      dblogObj.Tables(tableName).addRecord( {
         'SEEKSING': self.single_avg,
         'SEEKRAND': self.random_avg,
         'SEEKFULL': self.full_oi_avg
         } )
      objMsg.printMsg('makeDBLOutput 3')
