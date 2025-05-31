#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Implements Full Read and Write pack tests
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/FullPackReadWrite.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/FullPackReadWrite.py#1 $
# Level:3

from Constants import *
from TestParamExtractor import TP
import ScrCmds
import time
from math import floor
from Process import CProcess
import MessageHandler as objMsg
from IntfErrorHandle import CIntfErrorHandle
from LBARegions import CLBARegions
from ICmdFactory import ICmd


class CFullPackReadWrite(CProcess):
   """
   Implements IO Read Write feature.
   """
   #-------------------------------------------------------------------------------------------------------#
   def __init__(self, dut):
      CProcess.__init__(self)
      self.paramData = {}
      self.paramData["zone_readStartLBA"] = []
      self.paramData["zone_readEndLBA"] = []
      self.paramData["zone_readthruput"] = []
      self.paramData["zone_writeStartLBA"] = []
      self.paramData["zone_writeEndLBA"] = []
      self.paramData["zone_writethruput"] = []
      self.paramData["zone_WRStartLBA"] = []
      self.paramData["zone_WREndLBA"] = []
      self.paramData["zone_WRthruput"] = []
      self.dut = dut
      self.oErrorHandle = CIntfErrorHandle(self.dut)
      self.OK = 0

   #-------------------------------------------------------------------------------------------------------#
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

   #-------------------------------------------------------------------------------------------------------#
   def fullPackRead(self, prm_IntfTest):
      """
      Performs fullpack Read in DMA mode
      @param xfer_key: based on UDMA xfer speed; xfer_key=0x45 for UDMA speed=100; xfer_key=0x44 for UDMA speed=66
      @param zoneTuple: Iterable of (minLBA, maxLBA) for the large zone to generate mini-zones
      @return
      """

      step_lba = 256
      sect_cnt = 256
      read_starttime = time.time()
      self.read_myRegion = CLBARegions(self.dut.maxLBA, prm_IntfTest["Read_maxLBAPercent"])
      self.read_zoneTuple = self.read_myRegion.regions(prm_IntfTest["Read_zoneLocation"])
      minizones = self.getMiniZones(prm_IntfTest["Read_numZones"], self.read_zoneTuple)

      #do minizones need to be randomized?
      ICmd.ClearBinBuff(BWR = 3)
      objMsg.printMsg("Clear Bin Buffer")

      data = ICmd.SetFeatures(0x03, prm_IntfTest["Read_xfer_key"])
      if data['LLRET'] != self.OK:
         ScrCmds.raiseException(13421, "SetFeatures failed in fullpackRead %s" % str(data))
      for zone in minizones:

         zone_read_stime = time.time()
         num_blocks = (zone[1]-zone[0])/sect_cnt
         timeout = self.calculateTimeout(zone, step_lba, sect_cnt)
         #Actual number of blocks read is Term2. Size of each block is Term 1
         data = ICmd.SequentialReadDMAExt(zone[0],zone[1], step_lba, sect_cnt, timeout, exc=0)

         if data['LLRET'] != self.OK:
            self.oErrorHandle.handleReadFailure(data)
         zone_read_etime = time.time()

         self.paramData["zone_readStartLBA"].append(zone[0])
         self.paramData["zone_readEndLBA"].append(zone[1])
         self.paramData["zone_readthruput"].append((step_lba * num_blocks)/(zone_read_etime-zone_read_stime))
         self.makeDBLOutput("INTF_SEQREAD_THRUPUT")
      read_endtime = time.time()
      read_time = read_endtime - read_starttime

   #-------------------------------------------------------------------------------------------------------#
   def fullPackWrite(self, prm_IntfTest):
      """
      Performs fullpack Write in DMA mode
      @param xfer_key: based on UDMA xfer speed; xfer_key=0x45 for UDMA speed=100; xfer_key=0x44 for UDMA speed=66
      @param zoneTuple: Iterable of (minLBA, maxLBA) for the large zone to generate mini-zones
      @return
      """

      step_lba = 256
      sect_cnt = 256
      write_starttime = time.time()
      write_myRegion = CLBARegions(self.dut.maxLBA, prm_IntfTest["Write_maxLBAPercent"])
      zoneTuple = self.write_myRegion.regions[prm_IntfTest["Write_zoneLocation"]]

      minizones = self.getMiniZones(prm_IntfTest["Write_numZones"], zoneTuple)
      ICmd.ClearBinBuff(WBF=1)

      data = ICmd.SetFeatures(0x03, xfer_key, exc=0)
      if data['LLRET'] != self.OK:
         ScrCmds.raiseException(13421, "SetFeatures failed in fullpackwrite %s" % str(data))

      for zone in minizones:

         zone_write_stime = time.time()

         num_blocks = (zone[1] - zone[0])/sect_cnt
         timeout = self.calculateTimeout(zone, step_lba, sect_cnt)

         data = ICmd.SequentialWriteDMAExt(zone[0], zone[1], step_lba, sect_cnt, timeout, exc=0)

         if data['LLRET'] != self.OK:
            self.oErrorHandle.handleWriteFailure(data)
         zone_write_etime = time.time()

         self.paramData["zone_writeStartLBA"].append(zone[0])
         self.paramData["zone_writeEndLBA"].append(zone[1])
         self.paramData["zone_writethruput"].append((num_blocks * step_lba)/(zone_write_etime-zone_write_stime))
         self.makeDBLOutput("INTF_SEQWRITE_THRUPUT")

      write_endtime = time.time()
      write_time = write_endtime - write_starttime

   #-------------------------------------------------------------------------------------------------------#
   def fullPackWriteRead(self,zoneTuple, numMiniZones, xfer_key = 0x45, step_lba=256, sect_cnt=256, stamp_flag=0, comp_flag=1):
      """
      Performs fullpack WriteRead in DMA mode
      @param xfer_key: based on UDMA xfer speed; xfer_key=0x45 for UDMA speed=100; xfer_key=0x44 for UDMA speed=66
      @param zoneTuple: Iterable of (minLBA, maxLBA) for the large zone to generate mini-zones
      @return
      """

      WR_starttime = time.time()
      minizones = self.getMiniZones(numMiniZones, zoneTuple)
      ICmd.ClearBinBuff(WBF=1)
      data = ICmd.SetFeatures(0x03, xfer_key, exc=0)
      if data['LLRET'] != self.OK:
         ScrCmds.raiseException(13421, "SetFeatures failed in fullpackWriteRead %s" % str(data))
      for zone in minizones:
         zone_WR_stime = time.time()
         num_blocks = (zone[1]-zone[0])/sect_cnt
         timeout = self.calculateTimeout(zone, step_lba, sect_cnt)
         data = ICmd.SequentialWRDMAExt(zone[0], zone[1], step_lba, sect_cnt,stamp_flag,  comp_flag, timeout, exc =0 )
         if data['LLRET'] != self.OK:
            ScrCmds.raiseException(13422, 'SequentialWRDMAExt failed %s' % str(data))
         zone_WR_etime = time.time()

         self.paramData["zone_WRStartLBA"].append(zone[0])
         self.paramData["zone_WREndLBA"].append(zone[1])
         self.paramData["zone_WRthruput"].append((num_blocks * step_lba)/(zone_WR_etime-zone_WR_stime))
         self.makeDBLOutput("INTF_SEQWR_THRUPUT")

   #-------------------------------------------------------------------------------------------------------#
   def calculateTimeout(self, zone, step_lba, sect_cnt):
      num_blocks = (zone[1] - zone[0])/sect_cnt
      timeout = num_blocks * step_lba * prm_IntfTest["Default CPC Cmd Timeout"]*1000 #(assuming 1 sec timeout per LBA)
      return timeout

   #-------------------------------------------------------------------------------------------------------#
   def makeDBLOutput(self, tableName):
      objMsg.printDict(self.paramData)

      dblogObj = self.dut.dblData

      if tableName == 'INTF_SEQREAD_THRUPUT':
         objMsg.printMsg("%s,%s,%s" % (self.paramData["zone_readStartLBA"], self.paramData["zone_readEndLBA"], self.paramData["zone_readthruput"]))

         dblogObj.Tables(tableName).addRecord(
            {
            'START_LBA':self.paramData["zone_readStartLBA"],
            'END_LBA': self.paramData["zone_readEndLBA"],
            'SEQREAD_THRUPUT': self.paramData["zone_readthruput"]
            })

      elif tableName == 'INTF_SEQWRITE_THRUPUT':
         objMsg.printMsg("%s,%s,%s" % (self.paramData["zone_readStartLBA"], self.paramData["zone_readEndLBA"], self.paramData["zone_readthruput"]))

         dblogObj.Tables(tableName).addRecord(
            {
            'START_LBA':self.paramData["zone_writeStartLBA"],
            'END_LBA': self.paramData["zone_writeEndLBA"],
            'SEQWRITE_THRUPUT': self.paramData["zone_writethruput"]
            })

      elif tableName == 'INTF_SEQWR_THRUPUT':
         objMsg.printMsg("%s,%s,%s" % (self.paramData["zone_readStartLBA"], self.paramData["zone_readEndLBA"], self.paramData["zone_readthruput"]))

         dblogObj.Tables(tableName).addRecord(
            {
            'START_LBA':self.paramData["zone_WRStartLBA"],
            'END_LBA': self.paramData["zone_WREndLBA"],
            'SEQWR_THRUPUT': self.paramData["zone_WRthruput"]
            })

      else:
         objMsg.printMsg("DBLog TableName %s is not found" % tableName)
