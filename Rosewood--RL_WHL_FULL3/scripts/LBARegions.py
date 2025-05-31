#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Class provides method to clean up the region with zeroes as this is an action step required by customer.
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/LBARegions.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/LBARegions.py#1 $
# Level:3
#---------------------------------------------------------------------------------------------------------#
from Constants import *

class CLBARegions:
   """
   Class takes in a range of LBAs, creates four blocks (regions) at OD, MD1, MD2, ID, size of each block
   being specified percentage of the size of the LBA range specified (default being 2%).
   Also a max cutoff for the max size of the block (in %) can be specified (default being 10%.)
   Class provides method to clean up the region with zeroes as this is an action step required by customer.
   """
   #--------------------------------------------------------------------------------------
   def __init__(self, maxLBAs, size=2.0, maxSize=100.0):
      """
      NOTE:
         - maxLBAs is the maximum number of LBAs on drive, to be determined with IdentifyDevice
         - input size argument is in % of maximum number of LBAs
      """
      self.locations = ['OD', 'MD1', 'MD2', 'ID']
      self.numLocns = len(self.locations)
      self.maxLBAs  = maxLBAs
      size = min(size, maxSize) # set max size to 10%
      self.size = long(maxLBAs * float(size/100.0)) # input size is in % max_size, so convert that to equivalent sectors
      TraceMessage('Max LBAs to be Covered on Disk   : %ld' % (self.maxLBAs))
      TraceMessage('Block Size in Percent of Max LBAs: %.1f' % (size,))
      TraceMessage('Block Size in Sectors            : %ld' % (self.size,))
      self.regions = {} # this is the dict to be accessed by all I/O functions in software
      self.createRegions()
      TraceMessage('%s' % (self.regions,))
   #--------------------------------------------------------------------------------------
   def createRegions(self):
      """ method defines Region bounds """
      mid = self.maxLBAs / 2
      end = self.maxLBAs - 1
      # determine OD bounds
      start = 0
      self.regions['OD']  = (start, start+self.size)
      # determine MD1 bounds
      start = mid - self.maxLBAs/6
      self.regions['MD1'] = (start, start+self.size)
      # determine MD2 bounds
      start = mid + self.maxLBAs/6 - self.size
      self.regions['MD2'] = (start, start+self.size)
      # determine ID bounds
      start = end - self.size
      self.regions['ID']  = (start, start+self.size)
   #--------------------------------------------------------------------------------------
   def getRandRegion(self):
      """ method returns one of the random regions defined """
      randIndex = random.randint(0, self.numLocns-1) # randomly choose between the defined regions
      TraceMessage('Random Index: %d' % randIndex)
      TraceMessage('Random Region Index: %s' % self.locations[randIndex])
      region = self.regions[ self.locations[randIndex] ]
      TraceMessage('Random Region: %s' % `randRegion`)
      return region
   #--------------------------------------------------------------------------------------
   def clearWriteZero(self):
      """ Plan to obsolete this method. Use clearAllRegions() instead """
      TraceMessage('Clear all regions(OD, MD1, MD2, ID) with Zeroes')
      ClearBinBuff(WBF) # write zeros to buffer
      for (locn, zone) in self.regions.items():
         startLBA, endLBA = zone
         stepLBA = sectorCount = 256; stampFlag = 0
         SequentialWriteDMAExt(startLBA, endLBA, stepLBA, sectorCount, stampFlag)
   #--------------------------------------------------------------------------------------
   def clearRegion(self, locn):
      """ method clears specified region with zero pattern """
      if not self.regions.has_key(locn):
         TraceMessage('Specified Invalid Region to be Cleared')
         return
      TraceMessage('Clear %s Region with Zeroes' % locn)
      ClearBinBuff(WBF) # write zeros to buffer
      startLBA, endLBA = self.regions[locn]
      stepLBA = sectorCount = 256
      SequentialWriteDMAExt(startLBA, endLBA, stepLBA, sectorCount, stampFlag=0)
   #--------------------------------------------------------------------------------------
   def clearAllRegions(self):
      """ method clears previously defined regions with zero pattern """
      TraceMessage('Clear all regions(OD, MD1, MD2, ID) with Zeroes')
      ClearBinBuff(WBF) # write zeros to buffer
      for (locn, zone) in self.regions.items():
         startLBA, endLBA = zone
         stepLBA = sectorCount = 256; stampFlag = 0
         SequentialWriteDMAExt(startLBA, endLBA, stepLBA, sectorCount, stampFlag)

#------------------------------------------------------------------------------------------------------------#
