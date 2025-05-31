#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2008, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: This module holds all related classes and functions for parsing the VBAR Bpi Format file
#              and presenting the information to VBAR for VBAR by zone
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/06 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/bpiFile.py $
# $Revision: #2 $
# $DateTime: 2016/05/06 00:36:23 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/bpiFile.py#2 $
# Level: 1
#---------------------------------------------------------------------------------------------------------#

from Constants import *
import TestParameters as TP
import os, struct
import MessageHandler as objMsg
import ScrCmds
from Drive import objDut
from  PackageResolution import PackageDispatcher
from FSO import CFSO
from SIM_FSO import objSimArea
DEBUG = 0


#-------------------------------------------------------------------------------
class CBpiFile:
   #----------------------------------------------------------------------------
   fmtIndex = {
      'NumSerpents'  : 0,
      'Frequency'    : 1,
   }

   #----------------------------------------------------------------------------
   def __init__(self, bpiFile="BPI", list_by_zone = 0, load_cap_table = 1, load_freq_table = 1, load_min_format = 0, active_zones = [], load_conf_file_only = 0):
      if testSwitch.FE_0269922_348085_P_SIGMUND_IN_FACTORY:
         self.bpiNumHeads = objDut.imaxHead
      else:
         self.bpiNumHeads = 1
      self.numZones = objDut.numZones  # default for current rap.  BPI file will override if available
      self.numBpiProfiles = None
      self.nominalFormat = None
      self.loaded = None
      self.sectorsPerTrack=None
      self.numUzcZones = 24
      self.numTzpZones = 18
      self.list_by_zone = list_by_zone

      if testSwitch.FE_0269922_348085_P_SIGMUND_IN_FACTORY:
         try:
            self.load(bpiFile, active_zones, load_freq_table = load_freq_table, load_cap_table = load_cap_table, load_conf_file_only = load_conf_file_only)
         except:
            # Try to read the bpi.bin from the drives
            if testSwitch.SPLIT_BASE_SERIAL_TEST_FOR_CM_LA_REDUCTION:
               from base_PRETest import CRestoreSifBpiBinToPCFile
            else:
               from base_SerialTest import CRestoreSifBpiBinToPCFile
            CRestoreSifBpiBinToPCFile(objDut, {}).run()
            self.load(bpiFile, active_zones, load_freq_table = load_freq_table, load_cap_table = load_cap_table, load_conf_file_only = load_conf_file_only)
      else:
         self.load(bpiFile, active_zones, load_freq_table = load_freq_table, load_cap_table = load_cap_table, load_conf_file_only = load_conf_file_only)

   #----------------------------------------------------------------------------
   def load(self, bpiFile, active_zones=[], active_heads = [], load_freq_table = 0, load_cap_table = 0, load_min_format = 0, load_conf_file_only = 0):
      #=== Open bpi file
      try:
         if testSwitch.FE_0269922_348085_P_SIGMUND_IN_FACTORY:
            self.bpiNumHeads = objDut.imaxHead
            self.pcFileName = objSimArea['SIF'].name
            self.bpiFilePath = os.path.join(ScrCmds.getSystemPCPath(), self.pcFileName, CFSO().getFofFileName(0))
         else:
            self.bpiNumHeads = 1
            self.bpiFileName = PackageDispatcher(objDut, bpiFile).getFileName()
            self.bpiFilePath = os.path.join(ScrCmds.getSystemDnldPath(),self.bpiFileName)
         objMsg.printMsg("self.bpiFilePath %s" % str(self.bpiFilePath))
         f = open(self.bpiFilePath, 'rb')
      except:
         if testSwitch.virtualRun:
            f = None
            pass
         else:
            ScrCmds.raiseException(10326,"Couldn't open Bpi File")         

      #=== Read bpi file
      try:
         #=== Bpi Configuration File (Bytes 0-15)
         if f == None and testSwitch.virtualRun:
            self.oFSO = CFSO()
            self.oFSO.getZoneTable()
            self.nominalFormat = 150
            maxNumUzcZones = self.oFSO.dut.numZones #objDut.numZones
            maxNumZfbZones = self.oFSO.dut.numZones + 1 # Fixed VE invalid bpi bin bpic values
            self.nominalTracksPerSerpent = 200
            bpiFileFormatVersion = 3
            channelInfo = 0x36
            self.numBpiProfiles = self.nominalFormat * 2
            if testSwitch.FE_0125707_340210_CAP_FROM_BPIFILE:
               self.nominalCapacity = float(objDut.dblData.Tables('P210_CAPACITY_DRIVE').tableDataObj()[-1]['DRV_CAPACITY'])
         else:
            f.seek(0,0)
            bpiConfigurationFile = f.read(16) # <=== Bytes 0-15
            (bpiFileFormatVersion, numTzpRegisters, self.numBpiProfiles, channelInfo) = struct.unpack("BBBB",bpiConfigurationFile[0:4])
            (self.nominalFormat, maxNumUzcZones, maxNumZfbZones) = struct.unpack("BBB",bpiConfigurationFile[4:7])
            if testSwitch.FE_0125707_340210_CAP_FROM_BPIFILE:
               self.nominalCapacity = struct.unpack(">I",  bpiConfigurationFile[8:14]) * 512 * 10**(-9)
               if DEBUG > 0: objMsg.printMsg("NomCap = %s" % self.nominalCapacity)
            (self.nominalTracksPerSerpent,) = struct.unpack("<H",bpiConfigurationFile[14:16])
   
         self.numUzcZones = maxNumUzcZones
         self.numUserZones = self.numUzcZones
         self.numTzpZones = maxNumZfbZones
         self.numSystemZones = self.numTzpZones - self.numUserZones - objDut.numMCZones

         if DEBUG > 0: 
            objMsg.printMsg("NumBPIProf = %d NominalFmt = %d NomTrkPSerp = %s" % (self.numBpiProfiles, self.nominalFormat, self.nominalTracksPerSerpent))
            objMsg.printMsg("bpiFileFormatVersion = %d maxNumUzcZones = %d maxNumZfbZones = %d" % (bpiFileFormatVersion, maxNumUzcZones, maxNumZfbZones))

         if load_conf_file_only:
            return

         #=== select which channel is being used for this bpi file.
         # Note: Sigmund defines the channelCode-to-channel map
         registerSize = (channelInfo & 0x3)
         channelCode = (channelInfo >> 2) & 0x1F
         hasCapacityTable = channelInfo & 0x80
         if channelCode in [9, 11, 12]:    # Emma SRC and Eldora/ Eldora Plus SID
            channel = CEmmaEldoraChannel()
         elif channelCode in [10, 13]: # M10K and M11K
            channel = CMarvell11kGleasonChannel()
         else:
            ScrCmds.raiseException(14573, "Unrecognized channel code: %s" % channelCode)

         #=== Tuned Zone Parameters Address Map File (Bytes 16-31)
         # Get the TZP registers and find the frequency definition
         try:
            tzpAddressMapTable = f.read(16) # <=== Bytes 16-31
            channel.parseTzpAddressMapTable(tzpAddressMapTable)
         except:
            if testSwitch.virtualRun:
               pass
            else:
               raise
         
         #=== Load format table
         if not active_heads:
            active_heads = range(self.bpiNumHeads)
         # initialize the format table
         if self.list_by_zone:
            if not active_zones or testSwitch.virtualRun:
               active_zones = range(self.numZones)
            self.format = list(list(list(None for ifx in xrange(len(CBpiFile.fmtIndex))) for zn in xrange(self.numZones)) for hd in xrange(self.bpiNumHeads))
            for hd in xrange(self.bpiNumHeads):
               for zn in xrange(self.numZones):
                  if zn in active_zones:
                     for ifx in xrange(len(CBpiFile.fmtIndex)):
                        if ifx == CBpiFile.fmtIndex['NumSerpents'] and testSwitch.FE_0311724_348429_P_LOAD_COMMON_TRACK_PER_ZONE:
                           self.format[hd][zn][ifx] = [None]
                        else:
                           self.format[hd][zn][ifx] = list(None for pf in xrange(self.numBpiProfiles))
         else:
            self.format = list(list(list(None for ifx in xrange(len(CBpiFile.fmtIndex))) for pf in xrange(self.numBpiProfiles)) for hd in xrange(self.bpiNumHeads))
         for hd in xrange(self.bpiNumHeads):
            # dummy read for the header and tzpAddressMap
            if hd and not testSwitch.virtualRun:
               dummy = f.read(32)   # dummy read the configuration table and tzp map

            for pf in xrange(self.numBpiProfiles):
               if DEBUG: objMsg.printMsg("head %d Profile %d" % (hd , pf) )
               #pull the data for the bpi profile. Contains the User Zone Configuration Table, the
               #Zone Format Budget Table and the Tuned Zoned Parameters Table
               try:
                  profileData = f.read(self.numUzcZones * 2 + self.numTzpZones * 32)
                  #parse the UZC table for the user zones
                  uzc = list(struct.unpack("<" + "H" * self.numUzcZones, profileData[0:(self.numUzcZones*2)]))
                  if DEBUG: objMsg.printMsg(uzc)
                  # split the tzp table into the frames for each zone. Then calculate the channel frequency for each zone
                  tzpFrames = struct.unpack('16s' * self.numTzpZones,profileData[self.numUzcZones * 2 + self.numTzpZones * 16 : ])
                  frequency = [channel.getChannelFrequencyFromTzp(tzp) for tzp in tzpFrames]
                  if DEBUG: objMsg.printMsg(frequency)
               except:
                  if not testSwitch.virtualRun:
                     ScrCmds.raiseException(10326,"Couldn't read Bpi File")
                  else: # virtualRun mode
                     if maxNumUzcZones == 31:
                        uzc = [15, 48, 36, 47, 49, 42, 53, 46, 38, 38, 44, 41, 34, 35, 32, 39, 47, 40, 35, 35, 31, 37, 35, 42, 34, 38, 43, 43, 35, 33, 31]
                        frequency = [579931.640625, 1176328.125, 1162617.1875, 1149960.9375, 1136250.0, 1120429.6875, 1105664.0625, 1085625.0, 1067695.3125, 1050820.3125, 1033945.3125, 1012851.5625, 992812.5, 975937.5, 958007.8125, 941132.8125, 920039.0625, 894726.5625, 872578.125, 851484.375, 831445.3125, 813515.625, 792421.875, 772382.8125, 748125.0, 728085.9375, 705937.5, 680625.0, 655312.5, 634218.75, 614179.6875, 593261.71875]
                     elif maxNumUzcZones == 60: #dummy data
                        uzc = [15, 48, 36, 47, 49, 42, 53, 46, 38, 38, 44, 41, 34, 35, 32, 39, 47, 40, 35, 35, 31, 37, 35, 42, 34, 38, 43, 43, 35, 33]*2
                        frequency = [579931.640625, 1176328.125, 1162617.1875, 1149960.9375, 1136250.0, 1120429.6875, 1105664.0625, 1085625.0, 1067695.3125, 1050820.3125, 1033945.3125, 1012851.5625, 992812.5, 975937.5, 958007.8125, 941132.8125, 920039.0625, 894726.5625, 872578.125, 851484.375, 831445.3125, 813515.625, 792421.875, 772382.8125, 748125.0, 728085.9375, 705937.5, 680625.0, 655312.5, 634218.75, 614179.6875]*2
                     elif maxNumUzcZones == 120: #dummy data
                        uzc = [15, 48, 36, 47, 49, 42, 53, 46, 38, 38, 44, 41, 34, 35, 32, 39, 47, 40, 35, 35, 31, 37, 35, 42, 34, 38, 43, 43, 35, 33]*4
                        frequency = [579931.640625, 1176328.125, 1162617.1875, 1149960.9375, 1136250.0, 1120429.6875, 1105664.0625, 1085625.0, 1067695.3125, 1050820.3125, 1033945.3125, 1012851.5625, 992812.5, 975937.5, 958007.8125, 941132.8125, 920039.0625, 894726.5625, 872578.125, 851484.375, 831445.3125, 813515.625, 792421.875, 772382.8125, 748125.0, 728085.9375, 705937.5, 680625.0, 655312.5, 634218.75, 614179.6875]*4
                     elif maxNumUzcZones == 150: #dummy data
                        uzc = [15, 48, 36, 47, 49, 42, 53, 46, 38, 38, 44, 41, 34, 35, 32, 39, 47, 40, 35, 35, 31, 37, 35, 42, 34, 38, 43, 43, 35, 33]*5
                        frequency = [579931.640625, 1176328.125, 1162617.1875, 1149960.9375, 1136250.0, 1120429.6875, 1105664.0625, 1085625.0, 1067695.3125, 1050820.3125, 1033945.3125, 1012851.5625, 992812.5, 975937.5, 958007.8125, 941132.8125, 920039.0625, 894726.5625, 872578.125, 851484.375, 831445.3125, 813515.625, 792421.875, 772382.8125, 748125.0, 728085.9375, 705937.5, 680625.0, 655312.5, 634218.75, 614179.6875]*5
                     elif maxNumUzcZones == 180: #dummy data
                        uzc = [15, 48, 36, 47, 49, 42, 53, 46, 38, 38, 44, 41, 34, 35, 32, 39, 47, 40, 35, 35, 31, 37, 35, 42, 34, 38, 43, 43, 35, 33]*6
                        frequency = [579931.640625, 1176328.125, 1162617.1875, 1149960.9375, 1136250.0, 1120429.6875, 1105664.0625, 1085625.0, 1067695.3125, 1050820.3125, 1033945.3125, 1012851.5625, 992812.5, 975937.5, 958007.8125, 941132.8125, 920039.0625, 894726.5625, 872578.125, 851484.375, 831445.3125, 813515.625, 792421.875, 772382.8125, 748125.0, 728085.9375, 705937.5, 680625.0, 655312.5, 634218.75, 614179.6875]*6
                     else: # maxNumUzcZones == 24
                        uzc = [176, 224, 222, 307, 177, 162, 229, 250, 225, 209, 251, 159, 204, 207, 189, 152, 153, 65535, 65535, 65535, 65535, 65535, 65535, 65535]
                        frequency = [580312.5, 1173750.0, 1148437.5, 1125000.0, 1096875.0, 1074375.0, 1047187.5, 1005000.0, 972187.5, 928125.0, 888750.0, 838125.0, 804375.0, 760312.5, 713437.5, 671250.0, 630000.0, 592500.0]
                     frequency = [freq * (1.0 + 0.01 * (pf - self.nominalFormat)) for freq in frequency]

               if load_freq_table and hd in active_heads:
                  if self.list_by_zone:
                     item_list = list(frequency[self.numSystemZones:])
                     for zn in active_zones:
                        self.format[hd][zn][CBpiFile.fmtIndex['Frequency']][pf] = item_list[zn]
                  else:
                     self.format[hd][pf][CBpiFile.fmtIndex['Frequency']] = list(frequency[self.numSystemZones:])

               elif load_min_format:
                  if pf == 0 or pf == self.nominalFormat:
                     if self.list_by_zone:
                        item_list = list(frequency[self.numSystemZones:])
                        for zn in active_zones:
                           self.format[hd][zn][CBpiFile.fmtIndex['Frequency']][pf] = item_list[zn]
                     else:
                        self.format[hd][pf][CBpiFile.fmtIndex['Frequency']] = list(frequency[self.numSystemZones:])
               if load_cap_table:
                  if self.list_by_zone:
                     item_list = list(uzc)
                     for zn in active_zones:
                        if not testSwitch.FE_0311724_348429_P_LOAD_COMMON_TRACK_PER_ZONE or (testSwitch.FE_0311724_348429_P_LOAD_COMMON_TRACK_PER_ZONE and pf==0):
                           self.format[hd][zn][CBpiFile.fmtIndex['NumSerpents']][pf] = item_list[zn]
                  else:
                     self.format[hd][pf][CBpiFile.fmtIndex['NumSerpents']] = list(uzc)

         if DEBUG > 0: 
            for hd in xrange(self.bpiNumHeads):
               if self.list_by_zone:
                  for zn in xrange(self.numZones):
                     if zn in active_zones:
                        for ifx in xrange(len(CBpiFile.fmtIndex)):
                           objMsg.printMsg("head %d zn %d %s" % (hd,zn,self.format[hd][zn]))
               else:
                  for pf in xrange(self.numBpiProfiles):
                     objMsg.printMsg("head %d pf %d %s" % (hd,pf,self.format[hd][pf]))

         if load_min_format:
            self.min_format = list(list() for hd in xrange(self.bpiNumHeads))
            for hd in xrange(self.bpiNumHeads):
               for zn in xrange(self.numZones):
                  if zn in active_zones:
                     self.min_format[hd].append(self.getFrequencyByFormatAndZone(self.getMinFormat(),zn,hd) / self.getFrequencyByFormatAndZone(0,zn,hd))
                  else:
                     self.min_format[hd].append(None)

         if hasCapacityTable and load_cap_table:
            # parse the Capacity File
            capacityFileStart =     (32+self.numBpiProfiles*(2*self.numUzcZones+32*self.numTzpZones))*self.bpiNumHeads
            self.tracksPerZone =    list(list() for hd in xrange(self.bpiNumHeads))
            self.sectorsPerTrack =  list(list() for hd in xrange(self.bpiNumHeads))
            f.seek(capacityFileStart,0)
            for hd in xrange(self.bpiNumHeads):
               if hd not in active_heads:
                  continue # jmt to test out 
               
               capacityFileHeader = f.read(64)
               (numUserZonesPerProfile, numBpiProfiles, self.numSectorSizes) = struct.unpack("BBB",capacityFileHeader[0:3])
               if self.numSectorSizes == 0:
                  self.numSectorSizes = 1
               self.sectorSizes = struct.unpack("H"*self.numSectorSizes,capacityFileHeader[4:(4+2*self.numSectorSizes)])
               tracksPerZoneTable = f.read(4 * self.numUzcZones * self.numBpiProfiles)
               sectorsPerTrackTable = f.read(2 * self.numUzcZones * self.numBpiProfiles * self.numSectorSizes)
               for pf in xrange(self.numBpiProfiles):
                  if not testSwitch.FE_0311724_348429_P_LOAD_COMMON_TRACK_PER_ZONE or (testSwitch.FE_0311724_348429_P_LOAD_COMMON_TRACK_PER_ZONE and pf==0):
                     self.tracksPerZone[hd].append(struct.unpack("<" + "I" * self.numUzcZones,tracksPerZoneTable[pf*4*self.numUzcZones:(pf+1)*4*self.numUzcZones]))
                  self.sectorsPerTrack[hd].append(struct.unpack("<" + "H" * self.numUzcZones,sectorsPerTrackTable[pf*2*self.numUzcZones:(pf+1)*2*self.numUzcZones]))

      finally:
         try:
            f.close()
         except:
            if not testSwitch.virtualRun:
               ScrCmds.raiseException(10326,"Couldn't read Bpi File")
            else:
               pass
               
   #----------------------------------------------------------------------------
   def hasSectorPerTrackInfo(self, sectorSize=None):
      if self.sectorsPerTrack != None:
         if sectorSize != None:
            return sectorSize in self.sectorSizes
         else:
            return True
      else:
         return False

   #----------------------------------------------------------------------------
   def getSectorsPerTrack(self, format, zone, head=0):
      if not testSwitch.FE_0269922_348085_P_SIGMUND_IN_FACTORY:
         head=0

      if self.sectorsPerTrack == None:
         if testSwitch.virtualRun: #Fix VE using hardcoded values
            return 500
         return 0     # this should probably return an exception instead of 0
      return self.sectorsPerTrack[head][format+self.nominalFormat][zone]

   #----------------------------------------------------------------------------
   def getTracksPerZone(self, format, zone, head=0):
      if not testSwitch.FE_0269922_348085_P_SIGMUND_IN_FACTORY:
         head=0
   
      if self.tracksPerZone == None:
         return 0     # again this should probably return an exception

      if testSwitch.FE_0311724_348429_P_LOAD_COMMON_TRACK_PER_ZONE:
         return self.tracksPerZone[head][0][zone]
      else:
         return self.tracksPerZone[head][format+self.nominalFormat][zone]

   #----------------------------------------------------------------------------
   def getFrequencyByFormatAndZone(self, format, zone, head=0):
      if not testSwitch.FE_0269922_348085_P_SIGMUND_IN_FACTORY:
         head=0
   
      profile = format + self.nominalFormat
      try:
         if self.list_by_zone:
            return self.format[head][zone][CBpiFile.fmtIndex['Frequency']][profile]
         else:
            return self.format[head][profile][CBpiFile.fmtIndex['Frequency']][zone]
      except:
         objMsg.printMsg("head = %d profile = %d format = %d zone = %d" % (head, profile, format, zone))
         raise

   #----------------------------------------------------------------------------
   def getNumSerpentsInZone(self, format, zone, head=0):
      if not testSwitch.FE_0269922_348085_P_SIGMUND_IN_FACTORY:
         head=0
   
      profile = format + self.nominalFormat
      if self.list_by_zone:
         if testSwitch.FE_0311724_348429_P_LOAD_COMMON_TRACK_PER_ZONE:
            return self.format[head][zone][CBpiFile.fmtIndex['NumSerpents']][0]
         else:
            return self.format[head][zone][CBpiFile.fmtIndex['NumSerpents']][profile]
      else:
         return self.format[head][profile][CBpiFile.fmtIndex['NumSerpents']][zone]

   #----------------------------------------------------------------------------
   def getNumNominalTracksInZone(self, format, zone, head=0):
      if not testSwitch.FE_0269922_348085_P_SIGMUND_IN_FACTORY:
         head=0
   
      return self.nominalTracksPerSerpent * self.getNumSerpentsInZone(format,zone,head)

   #----------------------------------------------------------------------------
   def getMaxFormat(self):
      """
      Return the maximum allowed bpi format defined in the BpiFile
      """
      return self.numBpiProfiles - self.nominalFormat -1

   #----------------------------------------------------------------------------
   def getMinFormat(self):
      """
      Return the minimum allowed format defined in the BpiFile
      """
      return 0 - self.nominalFormat

   #----------------------------------------------------------------------------
   def getMinBPIPCt(self, hd, zn):
      """
      Return the minimum allowed format defined in the BpiFile
      """
      return self.min_format[hd][zn]
   #----------------------------------------------------------------------------
   def getNominalFormat(self):
      return self.nominalFormat

   #----------------------------------------------------------------------------
   def getNumUserZones(self):
      return self.numUserZones
      
   #----------------------------------------------------------------------------
   def getNumBpiProfiles(self):
      return self.numBpiProfiles

   #----------------------------------------------------------------------------
   def getNumBpiFormats(self):
      return self.numBpiProfiles

   #----------------------------------------------------------------------------
   def getNominalTracksPerSerpent(self):
      return self.nominalTracksPerSerpent

   #----------------------------------------------------------------------------
   def getNominalCapacity(self):
      return self.nominalCapacity


#-------------------------------------------------------------------------------
class CChannel:
   """
   CChannel:
   Base class for the channel frequency calculations
   The base class does not know how to convert the tzp into frequeny for any
   channel.  A subclass should be created from this class and should provide
   it's own definitions of the two functions in the base class.
   """
   #----------------------------------------------------------------------------
   def __init__(self):
      self.freqTzpIndex = 0
      self.freqRegisterAddr = 0;
      self.freqRegisterBank = 0;

   #----------------------------------------------------------------------------
   def parseTzpAddressMapTable(self,TzpAddrTable):
      """
      Parse the TZP Address Map from the BPI file to determine how to find the
      channel frequency information
      """
      pass

   #----------------------------------------------------------------------------
   def getChannelFrequencyFromTzp(self,Tzp):
      """
      getChannelFrequencyFromTzp parses the Tuned Zone Parameter section for
      one zone/profile in the BPI File and returns the channel frequency in kHz.
      It uses the information stored from the parseTzpAddressMapTable function
      to find the correct register index in the table.
      """
      return float(0)


#-------------------------------------------------------------------------------
class CEmmaEldoraChannel(CChannel):
   """
   Provides the functions to parse the TZP frames of the bpifile and calculate
   channel frequency for the Caribou Channel
   """
   #----------------------------------------------------------------------------
   def __init__(self):
       self.freqTzpIndex = 0
       self.freqRegisterAddr = 0x804
       self.freqRegisterBank = 0

   #----------------------------------------------------------------------------
   def parseTzpAddressMapTable(self,TzpAddrTable):
       """
       Parse the TZP Address Map from the BPI file to determine how to find the
       channel frequency information
       """
       for tzp_offset in range(0,16,2):
           (bank,addr) = struct.unpack('BB',TzpAddrTable[tzp_offset:tzp_offset+2])
           regNum = bank * 256 + addr # now bank is the high byte of register num
           if self.freqRegisterAddr == regNum:
               self.freqTzpIndex = tzp_offset/2
   
   #----------------------------------------------------------------------------
   def getChannelFrequencyFromTzp(self,Tzp):
       """
       getChannelFrequencyFromTzp parses the Tuned Zone Parameter section for
       one zone/profile in the BPI File and returns the channel frequency in kHz.
       It uses the information stored from the parseTzpAddressMapTable function
       to find the correct register index in the table.
       """
       freqval = struct.unpack("<H",Tzp[self.freqTzpIndex*2:self.freqTzpIndex*2+2])[0]
       m_div = freqval
    
       freq = (31250 * m_div / 256.0)
       return float(freq)


#-------------------------------------------------------------------------------
class CMarvell11kGleasonChannel(CChannel):
   """
   CMarvell10kEldoraChannel
   Cloned from Marvell 9200, then adjusted based on channel spec, dated 2013Apr02
   For each new channel, update freqCoeffs and the freq equation
   """
   #----------------------------------------------------------------------------
   def __init__(self):
      self.regToOffsetMap = {}

   #----------------------------------------------------------------------------
   def parseTzpAddressMapTable(self,TzpAddrTable):
      """
      Parse the TZP Address Map from the BPI file to determine how to find the
      channel frequency information
      """
      for tzp_offset in xrange(0,16,2):
         (bank,addr) = struct.unpack('BB',TzpAddrTable[tzp_offset:tzp_offset+2])
         self.regToOffsetMap[((bank << 8) | addr)] = tzp_offset

   #----------------------------------------------------------------------------
   def getChannelFrequencyFromTzp(self,Tzp):
      """
      getChannelFrequencyFromTzp parses the Tuned Zone Parameter section for
      one zone/profile in the BPI File and returns the channel frequency in kHz.
      It uses the information stored from the parseTzpAddressMapTable function
      to find the correct register index in the table.
      """
      freqCoeffs = { 'tbg_divsel'   : { 'addr': 0x22, 'bitshift': lambda y:((y & 0x0300) >> 8), },
                     'n_pll_div'    : { 'addr': 0x24, 'bitshift': lambda y:((y & 0x00FF) >> 0), },
                     'r_frac_div'   : { 'addr': 0x23, 'bitshift': lambda y:((y & 0xFE00) >> 9), },
                    #'pll_refclkdiv': { 'addr': 0xa6, 'bitshift': lambda y:((y & 0x0030) >> 4), },
                    }

      for n, info in freqCoeffs.iteritems():
         TzpOffset = self.regToOffsetMap[info['addr']]
         TzpVal = struct.unpack("<H",Tzp[TzpOffset:TzpOffset+2])[0]
         freqCoeffs[n]['FieldVal'] = info['bitshift'](TzpVal)

      # 31250 is hard-coded in firmware for Marvell 9200.  See source/rw/hwctlrs/readchannelctlr/Marvell/calcrwfrequency.c
      # From Marvell 9200 Spec,  NRZ_freq = fref * ( TBGn + (TBGr/128)) / 2 ^TBGd
      # -HFB 2011MAR03
      
      #freq = (31250 * (freqCoeffs['n_pll_div']['FieldVal'] + ((freqCoeffs['r_frac_div']['FieldVal'])/128))) / (1 << (freqCoeffs['tbg_divsel']['FieldVal']+freqCoeffs['pll_refclkdiv']['FieldVal']) )
      freq = (31250.0 * (freqCoeffs['n_pll_div']['FieldVal'] + ((freqCoeffs['r_frac_div']['FieldVal'])/128.0))) / (1 << (freqCoeffs['tbg_divsel']['FieldVal']+0) )
      
      return float(freq)
