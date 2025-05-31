#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: This module holds all related classes and functions for performing optimizations
#              related to VBAR and format selection
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/VBAR_Slim.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/VBAR_Slim.py#1 $
# Level: 34
#---------------------------------------------------------------------------------------------------------#
import os, time
import types, traceback, operator, cPickle
import math, struct, bisect
from array import array

from Test_Switches import testSwitch
from Constants import *
from ScrCmds import raiseException, CRaiseException, getSystemPCPath, getSystemResultsPath, HostSetPartnum
from TestParamExtractor import TP
from State import CState
from Process import CProcess
from DesignPatterns import Singleton
from Drive import objDut
from PowerControl import objPwrCtrl
from dbLogUtilities import DBLogReader
from bpiFile import CBpiFile
from FSO import CFSO
from Utility import CUtility, CSpcIdHelper, getPrintDbgMsgFunction
from PIF import nibletTable
from MathLib import linreg, Fit_2ndOrder
import MessageHandler as objMsg

from sys import version
ver = version.split()[0].split('.')
objMsg.printMsg('Python %s cell detected' % version)
if int(ver[0]) <= 2 and int(ver[1]) <= 4 and (len(ver) <= 2 or int(ver[2]) <= 3):
   deepcopy = CUtility.copy
   objMsg.printMsg('deepcopy = CUtility.copy')
else:
   from copy import deepcopy

verbose = 0       # Set to a value greater than 0 for various levels of debug output in the log.
verifyPicker = 0  # Set to 1 to enable auto-VE to run in the CPicker class, (Note: Tons of added data to the log)
debug_VE = 0
debug_LBR = 0 and testSwitch.FE_0261758_356688_LBR
debug_RF = 0

Q0toQ15Factor = 32768
Q0toQ14Factor = 16384

# Define a constant that will be used to prevent infinite loops due to rounding error associated with DBLog
# floating data that has been truncated to 4 digits for a string, and converted back to a float for comparison.
RndErrCorrFactor = 1e-7

# Defines from T210_prv.h that can be used for BPI and TPI format adjustment
# CWORD1
SET_BPI =                     0x0001
SET_TPI =                     0x0002

# CWORD2
CW2_SET_TRACK_PITCH =         0x0010
CW2_SET_TRACK_GUARD =         0x0020
CW2_SET_WRT_FAULT_THRESHOLD = 0x0040
CW2_SET_SQUEEZE_MICROJOG =    0x0080
CW2_SET_SHINGLED_DIRECTION =  0x0100
CW2_SET_TRACKS_PER_BAND =     0x0200

SHINGLE_DIRECTION_OD_TO_ID =  0
SHINGLE_DIRECTION_ID_TO_OD =  1

T210_PARM_NUM_HEADS        =  16

TPI_MAX = TP.TPI_MAX
BPI_MAX = TP.BPI_MAX
TPI_MIN = TP.TPI_MIN
BPI_MIN = TP.BPI_MIN


###########################################################################################################
################################# V B A R   S E T T I N G S ###############################################
###########################################################################################################

# ATPI Picker error codes
ATPI_PASS                  = 0
ATPI_FAIL_CAPABILITY       = 1
ATPI_FAIL_PERFORMANCE      = 2
ATPI_FAIL_CAPACITY         = 3
ATPI_FAIL_HEAD_COUNT       = 4
ATPI_FAIL_SATURATION       = 5
ATPI_DEPOP_RESTART         = 6
ATPI_FAIL_NO_NIBLET        = 7
ATPI_FAIL_HMS_CAPABILITY   = 8
ATPI_FAIL_MINIMUM_THRUPUT  = 9
ATPI_FAIL_IMBALANCED_HEAD  = 10
ATPI_INVALID_DATA          = 100.00
ATPI_FAIL_OTC              = 11

maxBPI = {}
if testSwitch.FE_0163083_410674_RETRIEVE_P_VBAR_NIBLET_TABLE_AFTER_POWER_RECOVERY and \
   testSwitch.FE_0164322_410674_RETRIEVE_P_VBAR_TABLE_AFTER_POWER_RECOVERY:
   dblogOccCnt = \
   {
      'P211_VBAR_CAPS_WPPS'      : 1,
      'P_VBAR_NIBLET'            : objDut.OCC_VBAR_NIBLET,
      'P_VBAR_SUMMARY2'          : 1,
      'P_VBAR_MEASUREMENTS'      : 1,
      'VBAR_PICKER_DATA'         : 1,
      'P_WRT_PWR_PICKER'         : objDut.OCC_PWR_PICKER,
      'P_WRT_PWR_TRIPLETS'       : objDut.OCC_PWR_TRIPLETS,
      'P_SETTLING_SUMMARY'       : 1,
      'P_VBAR_PICKER_FMT_ADJUST' : 1,
      'P_VBAR_PICKER_RESULTS'    : 1,
      'P_VBAR_CLRNC_ADJUST'      : 1,
      'P_SMR_FORMAT_SUMMARY'     : 1,
   }
else:
   dblogOccCnt = \
   {
      'P211_VBAR_CAPS_WPPS'      : 1,
      'P_VBAR_NIBLET'            : 1,
      'P_VBAR_SUMMARY2'          : 1,
      'P_VBAR_MEASUREMENTS'      : 1,
      'VBAR_PICKER_DATA'         : 1,
      'P_WRT_PWR_PICKER'         : 1,
      'P_WRT_PWR_TRIPLETS'       : 1,
      'P_SETTLING_SUMMARY'       : 1,
      'P_VBAR_PICKER_FMT_ADJUST' : 1,
      'P_VBAR_PICKER_RESULTS'    : 1,
      'P_VBAR_CLRNC_ADJUST'      : 1,
      'P_SMR_FORMAT_SUMMARY'     : 1,
   }

printDbgMsg = getPrintDbgMsgFunction()
vbarGlobalClass = {}
vbarGlobalVar = {
   'formatReload'    : True,
}

###########################################################################################################
######################### I N T E R N A L   D E B U G   F L A G S #########################################
###########################################################################################################
# NOTE: All these flags here should be zero for production
# Validate with external tools if necessary
_DEBUG_PF3_CAPACITY_CALCULATION = 0

###########################################################################################################
################################# H E L P E R   F U N C T I O N S #########################################
###########################################################################################################

#-------------------------------------------------------------------------------------------------------
def mean(lst, trim=False):
   """ Return the average of all entries in the list, optionally trimming the highest and lowest"""
   lst_sum = sum(lst)
   lst_len = len(lst)
   if trim and lst_len >= 3:
      lst_sum = lst_sum - max(lst) - min(lst)
      lst_len -= 2
   return float(lst_sum)/lst_len

#-------------------------------------------------------------------------------------------------------
def t210PrmName(cmd, ByZone = 0):
   prm_name = []
   prm_name.append("H%04X" % cmd.get('HEAD_MASK', cmd.get('HEAD_RANGE', 0x00ff)))
   prm_name.append("Z%04X" % cmd.get('ZONE', 0x00FF))
   if ByZone: 
      length = T210_PARM_NUM_HEADS
   else:
      length = objDut.imaxHead
   bpi = cmd.get("BPI_GROUP_EXT", None)
   if bpi:
      prm_name.append("BPI %s" % str(bpi[:length]))

   tpi = cmd.get("TPI_GROUP_EXT", None)
   if tpi:
      prm_name.append("TPI %s" % str(tpi[:length]))

   return " ".join(prm_name)

#----------------------------------------------------------------------------------------------------------
def get_clearances(heads, zones, suppressLogOutput = 0):
   '''Return a dictionary of current clearances.  Key is (hd,zn), value is dict of clearances.'''

   # Retrieve the current clearances
   tableData = getVbarGlobalClass(CFSO).getAFHTargetClearances( 0, suppressLogOutput, retrieveData = True )

   # Recover the DBLog data
   if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT:
      prheatCol = 'PRE_HEAT_TRGT_CLRNC'
      wtheatCol = 'WRT_HEAT_TRGT_CLRNC'
      rdheatCol = 'READ_HEAT_TRGT_CLRNC'
   else:
      prheatCol = 'PRE_WRT_CLRNC_TRGT'
      wtheatCol = 'WRT_CLRNC_TRGT'
      rdheatCol = 'RD_CLRNC_TRGT'

   clearancesByHdZn = {}
   for row in reversed(tableData):
      hd = int(row['HD_LGC_PSN'])
      phtc = int(row[prheatCol])
      whtc = int(row[wtheatCol])
      rhtc = int(row[rdheatCol])

      if testSwitch.extern.FE_0255966_357263_T172_AFH_SUMMARY_TBL:
         startZone = int(row['START_ZONE'])
         endZone   = int(row['END_ZONE'])
      else:
         startZone = endZone = int(row['DATA_ZONE'])

      for zn in range(endZone, startZone-1, -1):
         if hd in heads and zn in zones:
            clearancesByHdZn[(hd,zn)] = {'phtc':phtc, 'whtc':whtc, 'rhtc':rhtc}

      # Only read the most recent results
      if hd==0 and zn==0:
         break

   return clearancesByHdZn

#----------------------------------------------------------------------------------------------------------
def MatchTargetClrUnit(clrnc):
   # The zero-heat clearance is reported by T211 in microinches.
   # The units need to match the target clearance structure maintained by the AFH guys.
   if testSwitch.AFH_ENABLE_ANGSTROMS_SCALER_USE_254:
      from AFH_constants import AFH_MICRO_INCHES_TO_ANGSTROMS
      return clrnc * AFH_MICRO_INCHES_TO_ANGSTROMS
   else:
      return clrnc

#----------------------------------------------------------------------------------------------------------
def buildZnMasksByHdList(hdzns):
   # hdzns is a list of (head, zone) tuples.
   # The output of this function is a head ordered list of (head,zonemap) tuples.
   zn_masks = {}
   for hd, zn in hdzns:
      zn_masks.setdefault(hd, 0)
      zn_masks[hd] |= (1 << zn)

   # Sort to ensure the pairs are basically in head-increasing order
   pairs = [(hd, zn_mask) for hd, zn_mask in zn_masks.items()]
   pairs.sort()

   return pairs

#----------------------------------------------------------------------------------------------------------
def optimizeHdZnMasks(hdzns):
   # hdzns is a list of (head, zone) tuples.
   # The output of this function is a list of (headmap,zonemap) tuples, where each tuple
   # is a bitwise map of heads that share a common zonemap for zones to be tested.
   # This is useful for calling tests that take a single zone map of zones to be tested,
   # and can use a head map to reduce the number of test calls.

   # Set up a head masks dictionary by collecting identical zone masks
   # Said another way, this is a dictionary of zn_mask:hd_mask where hd_mask
   # is a bitwise map of heads that share a common zone mask.
   hd_masks = {}
   for hd, zn_mask in buildZnMasksByHdList(hdzns):
      hd_masks.setdefault(zn_mask, 0)
      hd_masks[zn_mask] |= (1 << hd)

   # Convert the new dictionary to a list and sort to ensure the pairs are
   # basically in head-increasing order
   pairs = [(hd_mask, zn_mask) for zn_mask, hd_mask in hd_masks.items()]
   pairs.sort()

   return pairs

#----------------------------------------------------------------------------------------------------------
def getHdZnsWithBPIChange(measurements):
   # Reduces the general set of heads and zones to a subset list of head,zone tuples that need to be retested
   # due to the BPI being altered for that head/zone combination since the last measurement was taken.
   hdznsTestLst = []
   for hd,zn in [(hd, zn) for hd in range(objDut.imaxHead) for zn in range(objDut.numZones)]:
      if measurements.getRecord('BPIChanged', hd, zn) == 'T':
         hdznsTestLst.append((hd, zn))

   return hdznsTestLst

#----------------------------------------------------------------------------------------------------------
def getHdAndZnCnt((hd_mask,zn_mask)):
   # This function will return the head count and zone count associated with a
   # (hd_mask,zn_mask) tuple that it takes as an input parameter.
   hdCnt = 0
   tmpHdMask = hd_mask
   while tmpHdMask != 0:
      if tmpHdMask & 0x01:
         hdCnt += 1
      tmpHdMask = tmpHdMask >> 1

   znCnt = 0
   tmpZnMask = zn_mask
   while tmpZnMask != 0:
      if tmpZnMask & 0x01:
         znCnt += 1
      tmpZnMask = tmpZnMask >> 1

   return hdCnt, znCnt

#----------------------------------------------------------------------------------------------------------
def convertHdZnMasksToList((hd_mask,zn_mask)):
   # This function takes a (hd_mask,zn_mask) tuple, parses the pair, and returns an
   # expanded list containing all of the hd/zn combinations represented by the mask pair.
   hdLst = []
   hd = 0
   tmpHdMask = hd_mask
   while tmpHdMask != 0:
      if tmpHdMask & 0x01:
         hdLst.append(hd)
      tmpHdMask = tmpHdMask >> 1
      hd += 1

   znLst = []
   zn = 0
   tmpZnMask = zn_mask
   while tmpZnMask != 0:
      if tmpZnMask & 0x01:
         znLst.append(zn)
      tmpZnMask = tmpZnMask >> 1
      zn += 1

   hdznLst = []
   for hd,zn in [(hd, zn) for hd in hdLst for zn in znLst]:
      hdznLst.append((hd,zn))

   return hdznLst


#----------------------------------------------------------------------------------------------------------
def dumpDebugData(stepMarker=None,dataDict=None):
   objMsg.printMsg('%s, Dict Type = %s' % (stepMarker,dataDict.dictType))
   names = [name for name in dataDict.getNameList() if not name.startswith('cfg')]
   names.sort()
   for hd in xrange(1):
      for zn in xrange(objDut.numZones):
         if dataDict.dictType == 'WP':
            for wp in xrange(8):
               for name in names:
                  objMsg.printMsg('%s: %s' % ((hd,zn,wp), dataDict.getRecord(name, hd, zn, wp)))
         else:
            for name in names:
               objMsg.printMsg('%s: %s' % ((hd,zn), dataDict.getRecord(name, hd, zn)))

def displayBPINominalTable(dumpTable = 0):
   bpiFile = getVbarGlobalClass(CBpiFile)
   numUserZones = bpiFile.getNumUserZones()
   nominalFormat = bpiFile.getNominalFormat()
   maxBpiProfiles = bpiFile.getNumBpiFormats()
   BPIMinFormat = bpiFile.getMinFormat()
   BPIMaxFormat = bpiFile.getMaxFormat()
   BPINominal_Table = list(list(list() for pf in xrange(maxBpiProfiles)) for hd in xrange(bpiFile.bpiNumHeads))

   objMsg.printMsg('nominalFormat: %s' % (nominalFormat))
   objMsg.printMsg('maxBpiProfiles: %s' % (maxBpiProfiles))
   objMsg.printMsg('MinFormat: %s' % (BPIMinFormat))
   objMsg.printMsg('MaxFormat: %s' % (BPIMaxFormat))

   if not dumpTable:
      return

   # Calculate and fill-in 'BPINominal_Table' table with format freq ratios.
   objMsg.printMsg('-- Displaying BPINominal_Table --')
   tmpstr1 = '\nBPI_CFG'
   for zn in xrange(numUserZones): 
      tmpstr1 += str("    Zn%2d" % (zn))
   tmpstr2 = ''
   for hd in xrange(bpiFile.bpiNumHeads):
      for idx, pf in enumerate(xrange(BPIMinFormat,BPIMaxFormat+1)):
         tmpstr2 += str('\n "%2d" :(' % (idx))
         for zn in xrange(numUserZones):  # Including sys_zone
            nominalFrequency = bpiFile.getFrequencyByFormatAndZone(0,zn,hd)   # TODO: optimize this routine?
            ZnFormatFreq = bpiFile.getFrequencyByFormatAndZone(pf,zn,hd)
            FreqRatio = ZnFormatFreq/nominalFrequency
            BPINominal_Table[hd][idx].append(FreqRatio)
            tmpstr2 += str(' %.4f,' % (FreqRatio))
         tmpstr2 += '),'
      tmpstr2 += '\n'
   objMsg.printMsg('%s%s' % (tmpstr1, tmpstr2))

#----------------------------------------------------------------------------------------------------------
def getVbarGlobalClass(cls, param = {}):
   if debug_RF: objMsg.printMsg('get %s' % cls.__name__)
   if cls.__name__ not in vbarGlobalClass:
      vbarGlobalClass[cls.__name__] = cls(**param)
      if debug_RF: objMsg.printMsg('new %s' % cls.__name__)
   return vbarGlobalClass[cls.__name__]

#----------------------------------------------------------------------------------------------------------
def getVbarGlobalVar():
   return vbarGlobalVar
            
#-------------------------------------------------------------------------------------------------------
def getBpiHeadIndex(hd):
   if testSwitch.FE_0269922_348085_P_SIGMUND_IN_FACTORY:
      return hd
   else:
      return 0

###########################################################################################################
################################### H E L P E R   C L A S S E S ###########################################
###########################################################################################################
class CRapTcc(Singleton):

   def __init__(self):
      # Initialize some basic utilities
      self.dut = objDut

      self.prm_wp_178 = {'test_num': 178, 'prm_name': 'prm_wp_178', 'timeout': 1200, 'spc_id': 0,}

      self.oUtility = getVbarGlobalClass(CUtility)

      if testSwitch.FE_0120024_340210_ATI_IN_WRT_PWR_PICKER:
         WPTable = TP.VbarWpTable[self.dut.PREAMP_TYPE]
         try:
            ATITable = TP.ATIWpTable[self.dut.PREAMP_TYPE]
         except:
            if testSwitch.virtualRun:
               ATITable = TP.ATIWpTable[TP.ATIWpTable.keys()[0]]
            else:
               raiseException(11044, "ATIWpTable not found in TestParameters and is needed for FE_0120024_340210_ATI_IN_WRT_PWR_PICKER feature")
      else:
         self.VbarWPTable = TP.VbarWpTable[self.dut.PREAMP_TYPE]

      # Build the triplet list by zone
      self.TripletZnGroups = []
      if testSwitch.FE_0114310_340210_ZONE_GRPS_4_TRIPLETS:
         TripletZoneMap = getattr(TP,'TripletZoneMap',{self.dut.PREAMP_TYPE: {'ALL': 0}})

         # Reverse dictionary
         tripletdict = {}
         for k, v in TripletZoneMap[self.dut.PREAMP_TYPE].items():
            tripletdict[v] = k
         triplet_zgroups = tripletdict.keys()
         triplet_zgroups.sort()

         Tzonemap = CVbarTestZones().getTestZoneMap()
         tzones = Tzonemap.keys()
         tzones.sort()

         index = 0
         tindex = 0
         self.ATITable = {}
         self.TripletZnGroups.append([])
         for zone in xrange(self.dut.numZones+1):
            if zone not in Tzonemap[tzones[index]]:
               index = index + 1

            if tindex < len(triplet_zgroups) - 1:
               if index >= triplet_zgroups[tindex+1]:
                  tindex = tindex + 1
                  self.TripletZnGroups.append([])

            if testSwitch.FE_0120024_340210_ATI_IN_WRT_PWR_PICKER:
               self.TripletZnGroups[tindex].append(zone)
               WPTable[zone] = WPTable[tripletdict[triplet_zgroups[tindex]]]
               self.ATITable[zone] = ATITable[tripletdict[triplet_zgroups[tindex]]]
            else:
               self.VbarWPTable[zone] = self.VbarWPTable[tripletdict[triplet_zgroups[tindex]]]
               self.TripletZnGroups[tindex].append(zone)

      else:
         TripletZoneMap = getattr(TP,'TripletZoneMap',{'N_USER_ZONES': 17, self.dut.PREAMP_TYPE: {'ALL': 0}})

         tripletdict = {}
         for k, v in TripletZoneMap[self.dut.PREAMP_TYPE].items():  #reverse dictionary
            tripletdict[v] = k


         startZoneList = tripletdict.keys()
         startZoneList.sort()

         ODcount = 0
         count = 0

         for v in startZoneList:  #adjust for actual number of zones different from TestP input
            if tripletdict[v] == 'OD':
               ODcount = count

            if count == ODcount + 1:
               nStartZone = TripletZoneMap[self.dut.PREAMP_TYPE][tripletdict[v]] - (TripletZoneMap['N_USER_ZONES'] - self.dut.numZones)
               TripletZoneMap[self.dut.PREAMP_TYPE][tripletdict[v]] = nStartZone
               if testSwitch.FE_0120024_340210_ATI_IN_WRT_PWR_PICKER:
                  WPTable[nStartZone] = WPTable[tripletdict[v]]
               else:
                  self.VbarWPTable[nStartZone] = self.VbarWPTable[tripletdict[v]]
            else:
               if testSwitch.FE_0120024_340210_ATI_IN_WRT_PWR_PICKER:
                  WPTable[v] = WPTable[tripletdict[v]]
               else:
                  self.VbarWPTable[v] = self.VbarWPTable[tripletdict[v]]
            count += 1

         adjStartZnList = TripletZoneMap[self.dut.PREAMP_TYPE].values()
         adjStartZnList.sort()

         count = -1

         for zone in xrange(self.dut.numZones+1):
            if zone in adjStartZnList:
               count += 1
               sZone = adjStartZnList[count]

               if count > 0:
                  self.TripletZnGroups.append(zoneList)
               zoneList = [sZone,]
            else:
               if testSwitch.FE_0120024_340210_ATI_IN_WRT_PWR_PICKER:
                  WPTable[zone] = WPTable[sZone]
               else:
                  self.VbarWPTable[zone] = self.VbarWPTable[sZone]
               zoneList.append(zone)
         if testSwitch.FE_0120024_340210_ATI_IN_WRT_PWR_PICKER:
            if zoneList not in self.TripletZnGroups:
               self.TripletZnGroups.append(zoneList)
         else:
            self.TripletZnGroups.append(zoneList)

      # Set up NUM_WRITE_POWERS
      if testSwitch.FE_0120024_340210_ATI_IN_WRT_PWR_PICKER:
         self.VbarWPTable = {}
         for hd in range(self.dut.imaxHead):
            self.VbarWPTable[hd] = {}
            for zn in range(self.dut.numZones+1):
               self.VbarWPTable[hd][zn] = WPTable[zn]

         self.NUM_WRITE_POWERS = len(self.VbarWPTable[0][0])
      else:
         self.NUM_WRITE_POWERS = len(self.VbarWPTable[self.VbarWPTable.keys()[0]])

      # Target write clearances for VBAR measurements
      if testSwitch.FE_0169232_341036_ENABLE_AFH_TGT_CLR_CANON_PARAMS == 1:
         from AFH_canonParams import getTargetClearance
         afhZoneTargets = getTargetClearance()
      else:
         afhZoneTargets = TP.afhZoneTargets
      self.tgtWrClr = [afhZoneTargets['TGT_WRT_CLR'][zn] for zn in range(self.dut.numZones+1)]

   #----------------------------------------------------------------------------------------------------------
   def updateWP(self, hd, zn, wp, wcoc=0, wcoh=0, working_set=0, setAllZonesHeads = 0, stSuppress=testSwitch.FE_0147058_208705_SHORTEN_VBAR_LOGS):
      """
         Modify WP value in RAP based on input value wp which must be in range [0, 7]
         *If zn is a tuple/list of zones and setAllZonesHeads = 0 then those zones will be updated for that head.
      """
      prm = self.prm_wp_178.copy()
      zn_mask_low = 0
      zn_mask_high = 0
      if setAllZonesHeads == 0:
         hd_mask = 0x3FF & (1<<hd) # write to one head at a time

         if type(zn) in [tuple, list]:

            #If the zone in question is in this triplet group then set all zones in that triplet
            for znGroup in self.TripletZnGroups:
               #Create a set
               updateIntersect = set(znGroup)
               #Update all zones in the mask that are for this triplet zone
               updateIntersect.intersection_update(set(zn))
               zn_mask_low = 0
               zn_mask_high = 0
               #Convert the intersection back to a list for iteration and slicing
               updateIntersect = list(updateIntersect)
               if len(updateIntersect) > 0:
                  #If we had zones in common to update then update the RAP
                  #zn_mask = self.oUtility.ReturnTestCylWord(self.oUtility.setZoneMask(updateIntersect))
                  for zone in updateIntersect:
                     if zone < 32:
                        zn_mask_low |= (1<<zone)
                     else:
                        zn_mask_high |= (1<<(zone - 32))
                  if testSwitch.FE_0120024_340210_ATI_IN_WRT_PWR_PICKER:
                     wc, ovs, ovd = self.VbarWPTable[hd][updateIntersect[0]][wp]
                  else:
                     wc, ovs, ovd = self.VbarWPTable[updateIntersect[0]][wp]

                  prm.update({
                     'prm_name'             : "Set WP H%04X Z%08X%08X WP (%d,%d,%d)" % (hd_mask, zn_mask_low, zn_mask_high, wc, ovs, ovd),
                     'CWORD1'               : 0x0200,
                     'CWORD2'               : 0x1107,
                     #'BIT_MASK'             : zn_mask,
                     'BIT_MASK'             : self.oUtility.ReturnTestCylWord(zn_mask_low),
                     'BIT_MASK_EXT'             : self.oUtility.ReturnTestCylWord(zn_mask_high),
                     'HEAD_RANGE'           : hd_mask,
                     'WRITE_CURRENT'        : wc,
                     'DAMPING'              : ovs,
                     'DURATION'             : ovd,
                     'WRITE_CURRENT_OFFSET' : (wcoc,wcoh),
                  })

                  if stSuppress:
                     prm.update({
                        'stSuppressResults' : ST_SUPPRESS__ALL,
                     })

                  getVbarGlobalClass(CProcess).St(prm)
         else:
            # Just update the specific zone requested
            #zn_mask = self.oUtility.ReturnTestCylWord(self.oUtility.setZoneMask(zn))
            zn_mask_low = 0
            zn_mask_high = 0
            if zn < 32:
               zn_mask_low = (1<<zn)
            else:
               zn_mask_high = (1<<(zn - 32))
            if testSwitch.FE_0120024_340210_ATI_IN_WRT_PWR_PICKER:
               wc, ovs, ovd = self.VbarWPTable[hd][zn][wp]
            else:
               wc, ovs, ovd = self.VbarWPTable[zn][wp]

            prm.update({
               #'prm_name'             : "Set WP H%04X Z%04X%04X WP (%d,%d,%d)" % (hd_mask, zn_mask[1], zn_mask[0], wc, ovs, ovd),
               'prm_name'             : "Set WP H%04X Z%08X%08X WP (%d,%d,%d)" % (hd_mask, zn_mask_low, zn_mask_high, wc, ovs, ovd),
               'CWORD1'               : 0x0200,
               'CWORD2'               : 0x1107,
               #'BIT_MASK'             : zn_mask,
               'BIT_MASK'             : self.oUtility.ReturnTestCylWord(zn_mask_low),
               'BIT_MASK_EXT'             : self.oUtility.ReturnTestCylWord(zn_mask_high),
               'HEAD_RANGE'           : hd_mask,
               'WRITE_CURRENT'        : wc,
               'DAMPING'              : ovs,
               'DURATION'             : ovd,
               'WRITE_CURRENT_OFFSET' : (wcoc,wcoh),
            })

            if stSuppress:
               prm.update({
                  'stSuppressResults' : ST_SUPPRESS__ALL,
               })

            getVbarGlobalClass(CProcess).St(prm)
      else:
         hd_mask = 0x3FF
         #Set a mask and update for each triplet zone group
         for znGroup in self.TripletZnGroups:
            #Since each triplet zone group has the same wp settings just grab the 1st zone to use as index
            if testSwitch.FE_0120024_340210_ATI_IN_WRT_PWR_PICKER:
               wc, ovs, ovd = self.VbarWPTable[hd][znGroup[0]][wp]
            else:
               wc, ovs, ovd = self.VbarWPTable[znGroup[0]][wp]

            prm.update({
               #'prm_name'            : "Set WP H%04X Z%04X%04X WP (%d,%d,%d)" % (hd_mask, zn_mask[0], zn_mask[1], wc, ovs, ovd),
               'prm_name'             : "Set WP", # H%04X Z%08X%08X WP (%d,%d,%d)" % (hd_mask, zn_mask_low, zn_mask_high, wc, ovs, ovd),
               'CWORD1'              : 0x0200,
               'CWORD2'              : 0x1107,
               #'BIT_MASK'            : zn_mask,
               #'BIT_MASK'            : self.oUtility.ReturnTestCylWord(zn_mask_low),
               #'BIT_MASK_EXT'            : self.oUtility.ReturnTestCylWord(zn_mask_high),
               'HEAD_RANGE'          : hd_mask,
               'WRITE_CURRENT'       : wc,
               'DAMPING'             : ovs,
               'DURATION'            : ovd,
               'WRITE_CURRENT_OFFSET': (wcoc,wcoh),
            })

            if stSuppress:
               prm.update({
                  'stSuppressResults' : ST_SUPPRESS__ALL,
               })

            if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
               #bit mask & bit mask ext param is no longer supported
               if 'BIT_MASK' in prm:     del prm['BIT_MASK'] 
               if 'BIT_MASK_EXT' in prm: del prm['BIT_MASK_EXT']
               if testSwitch.extern.FE_0270095_504159_SUPPORT_LOOPING_ZONE_T178:                  
                  for startZn, endZn in \
                     self.oUtility.convertZoneListToZoneRange(znGroup):
                     prm['ZONE'] = ( startZn << 8) + endZn
                     prm['prm_name'] = prm['prm_name'] + ' %d' % (prm['ZONE'])
                     getVbarGlobalClass(CProcess).St(prm)
               else:
                  for zn in znGroup:
                     prm['ZONE'] = zn
                     getVbarGlobalClass(CProcess).St(prm)
            else:
               prm['BIT_MASK_EXT'], prm['BIT_MASK'] = self.oUtility.convertListTo64BitMask(znGroup)
               getVbarGlobalClass(CProcess).St(prm)


            #zn_mask = self.oUtility.ReturnTestCylWord(self.oUtility.setZoneMask(znGroup))

   #----------------------------------------------------------------------------------------------------------
   def commitRAP(self):
      """
         This method should be executed at the end of a series of updates to RAP, so that all changes
         are actually committed to the flash, i.e. the flash copy is udpated
      """
      prm = self.prm_wp_178.copy()
      prm.update({'CWORD1':0x0220}) # write RAP data to flash
      getVbarGlobalClass(CProcess).St(prm)
      getVbarGlobalClass(CProcess).St({'test_num':172, 'prm_name':"Retrieve WP's", 'CWORD1':12, 'timeout':100, 'spc_id': 1})  # Read after write
   #----------------------------------------------------------------------------------------------------------
   def saveRAPtoPCFile(self):
      """
         Saves RAP data to PC file
      """
      prm = self.prm_wp_178.copy()
      prm.update({'CWORD1':0x0208}) # save RAP data to PC file
      getVbarGlobalClass(CProcess).St(prm)

   #----------------------------------------------------------------------------------------------------------
   def recovRAPfromPCFile(self):
      """
         Recovers RAP from a PC file, updated RAM copy
      """
      prm = self.prm_wp_178.copy()
      prm.update({'CWORD1':0x0201}) # recover RAP (RAM copy) from PC file
      getVbarGlobalClass(CProcess).St(prm)

   #----------------------------------------------------------------------------------------------------------
   def printWpTable(self):
      objMsg.printMsg('PreAmp Type: %s' % (self.dut.PREAMP_TYPE,))
      objMsg.printMsg('Write Triplets Table:')
      objMsg.printDict(self.VbarWPTable, colWidth = 15)

   def updateDblogWpTable(self):
      dblogOccCnt['P_WRT_PWR_TRIPLETS']+=1
      self.dut.OCC_PWR_TRIPLETS = dblogOccCnt['P_WRT_PWR_TRIPLETS']

      if testSwitch.FE_0120024_340210_ATI_IN_WRT_PWR_PICKER:
         for hd in self.VbarWPTable.keys():
            for zGroup in self.VbarWPTable[hd]:
               for wp_idx in range(self.NUM_WRITE_POWERS):
                  dblog_record = {
                           'WRT_PWR_NDX'              : wp_idx,
                           'ZONE_TYPE'                : zGroup,
                           'SPC_ID'                   : 0,
                           'OCCURRENCE'               : dblogOccCnt['P_WRT_PWR_TRIPLETS'],
                           'SEQ'                      : self.dut.objSeq.getSeq(),
                           'TEST_SEQ_EVENT'           : 1,
                           'WRT_CUR'                  : self.VbarWPTable[hd][zGroup][wp_idx][0],
                           'OVRSHT'                   : self.VbarWPTable[hd][zGroup][wp_idx][1],
                           'OVRSHT_DUR'               : self.VbarWPTable[hd][zGroup][wp_idx][2],
                        }
                  self.dut.dblData.Tables('P_WRT_PWR_TRIPLETS').addRecord(dblog_record)
                  if testSwitch.FE_0164322_410674_RETRIEVE_P_VBAR_TABLE_AFTER_POWER_RECOVERY:
                     self.dut.wrt_pwr_triplets.append(dblog_record)
      else:
         for zGroup in self.VbarWPTable.keys():
            for wp_idx in range(self.NUM_WRITE_POWERS):
               dblog_record = {
                        'WRT_PWR_NDX'              : wp_idx,
                        'ZONE_TYPE'                : zGroup,
                        'SPC_ID'                   : 0,
                        'OCCURRENCE'               : dblogOccCnt['P_WRT_PWR_TRIPLETS'],
                        'SEQ'                      : self.dut.objSeq.getSeq(),
                        'TEST_SEQ_EVENT'           : 1,
                        'WRT_CUR'                  : self.VbarWPTable[zGroup][wp_idx][0],
                        'OVRSHT'                   : self.VbarWPTable[zGroup][wp_idx][1],
                        'OVRSHT_DUR'               : self.VbarWPTable[zGroup][wp_idx][2],
                     }
               self.dut.dblData.Tables('P_WRT_PWR_TRIPLETS').addRecord(dblog_record)
               if testSwitch.FE_0164322_410674_RETRIEVE_P_VBAR_TABLE_AFTER_POWER_RECOVERY:
                  self.dut.wrt_pwr_triplets.append(dblog_record)

###########################################################################################################
###########################################################################################################
class CVbarTestZones(Singleton):
   def __init__(self):
      self.dut = objDut

      if testSwitch.FE_0157921_357260_P_VBAR_ZONEMAP_IN_TESTPARAMETERS and not testSwitch.virtualRun:
         self.zoneMap = TP.VbarZoneMap.copy()
      else:
         numUserZones = self.dut.numZones
         self.zoneMap = {}
         OD_ID = numUserZones/7
         ONE_THREE = numUserZones*2/9
         self.zoneMap[0] = range(0, OD_ID)
         self.zoneMap[OD_ID] = range(OD_ID, OD_ID + ONE_THREE)
         self.zoneMap[(numUserZones/2)] = range(OD_ID + ONE_THREE, numUserZones -  OD_ID - ONE_THREE)
         self.zoneMap[numUserZones - OD_ID - 1] = range(numUserZones -  OD_ID - ONE_THREE, numUserZones -  OD_ID)
         self.zoneMap[numUserZones - 1] = range(numUserZones -  OD_ID, numUserZones)

      if debug_VE: objMsg.printMsg('frm CVbarTestZones - numUserZones : %d' % numUserZones)

      mFSO = getVbarGlobalClass(CFSO)
      mFSO.getZoneTable()

      colDict = self.dut.dblData.Tables(TP.zone_table['resvd_table_name']).columnNameDict()
      sysZt = self.dut.dblData.Tables(TP.zone_table['resvd_table_name']).rowListIter({colDict['HD_LGC_PSN']:'0'}).next()
      sysZone = int(sysZt[colDict['ZN']])
      if debug_RF: objMsg.printMsg('CVbarTestZones.__init__ sysZone: %d %s %s' % (sysZone, sysZt[colDict['HD_LGC_PSN']], str(sysZt[colDict['HD_LGC_PSN']]=='0')))

      sysZoneLoc = mFSO.findSysAreaClosestDataZone()
      nearestDataZone = sysZoneLoc[0]
      self.zoneMap[self.getTestZnforZn(nearestDataZone)].append(sysZone)

      self.testZones = self.zoneMap.keys()
      self.testZones.sort()

   #----------------------------------------------------------------------------------------------------------
   def getTestZones(self):
      return self.testZones # list

   #----------------------------------------------------------------------------------------------------------
   def getTestZoneMap(self):
      return self.zoneMap # dict

   def getTestZnforZn(self, zone):
      for zn in self.zoneMap:
         if zone in self.zoneMap[zn]:
            return zn

###########################################################################################################
###########################################################################################################
class CVbarFormatScaler(object):
   _inst = None
    
   def __new__(cls, *args, **kwargs):
      if debug_RF: objMsg.printMsg('CVbarFormatScaler: __new__')
      if not cls._inst:
         cls._inst = super(CVbarFormatScaler, cls).__new__(cls, *args, **kwargs)
         if debug_RF: objMsg.printMsg('CVbarFormatScaler: new')
      else:
         def __dummyFunc(cls, *args, **kwargs): pass
         cls.__init__ = __dummyFunc
         if getVbarGlobalVar()['formatReload']:
            cls._inst.load()
      return cls._inst
   
   def __init__(self):
      self.bpiFile = getVbarGlobalClass(CBpiFile)

      if testSwitch.extern.FE_0161563_208705_TPI_FMT_RELATIVE_UNITS:
         if testSwitch.DESPERADO:
            self.RelativeToFormatScaler = int(1e6)
         else:
            self.RelativeToFormatScaler = self.bpiFile.getNominalTracksPerSerpent()

      self.load()

   def load(self):
      prm = {'test_num' : 210,
               'prm_name' : 'prm_vbar_formats_210',
               'CWORD1'   : 0x0000,
               'CWORD2'   : 0x0001,
               #'dlfile'   : (CN,self.bpiFile.bpiFileName),
               'timeout'  : 60,
               'spc_id'   : 0,
               'DblTablesToParse' : ['P210_VBAR_FORMATS'],
            }
      if not testSwitch.FE_0269922_348085_P_SIGMUND_IN_FACTORY:
         prm.update({
               'dlfile'   : (CN,self.bpiFile.bpiFileName),
               })

      if testSwitch.DESPERADO:
         prm.update({
               'CWORD1'            : 0x0100,
               })

      if testSwitch.WA_0152247_231166_P_POWER_CYCLE_RETRY_SIM_ERRORS:
         prm.update({
               'retryECList'       : [10335],
               'retryCount'        : 3,
               'retryMode'         : POWER_CYCLE_RETRY,
               })

         if testSwitch.TRUNK_BRINGUP: #trunk code see 10451 also
             prm.update({
                'retryECList'       : [10335,10451,10403,10468],
                })


      if testSwitch.MEASURE_TMR:
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1) # power cycle in case drive was hung

      if testSwitch.WA_0256539_480505_SKDC_M10P_BRING_UP_DEBUG_OPTION:
         prm.update({
               'timeout'  : 600,
               })

      getVbarGlobalClass(CProcess).St(prm)

      # Build the translation table
      self.formats = {}

      # TODO: optimize SuprsDblObject later
      if testSwitch.virtualRun:
         table = objDut.dblData.Tables('P210_VBAR_FORMATS').tableDataObj()
      else:
         table = objDut.objSeq.SuprsDblObject['P210_VBAR_FORMATS']

      for row in reversed(table):
         hd = int(row['HD_LGC_PSN'])
         zn = int(row['DATA_ZONE'])
         bpi = int(row['BPI_FMT']) - self.bpiFile.getNominalFormat()
         if testSwitch.extern.FE_0161563_208705_TPI_FMT_RELATIVE_UNITS:
            tpi = int(round(float(row['TPI_FMT'])*self.RelativeToFormatScaler))-self.RelativeToFormatScaler
         else:
            tpi = int(row['TPI_FMT'])-self.bpiFile.getNominalTracksPerSerpent()

         if self.bpiFile.getMinFormat() <= bpi <= self.bpiFile.getMaxFormat():
            self.formats.setdefault(hd, {})[zn] = {'BPI':bpi, 'TPI':tpi}
         else:
            self.formats.setdefault(hd, {})[zn] = {'BPI':0, 'TPI':0}

         # Only read the most recent results
         if hd==0 and zn==0:
            break
            
      getVbarGlobalVar()['formatReload'] = False
      if debug_RF: objMsg.printMsg('CVbarFormatScaler: reload')

   def getFormat(self, hd, zn, bpi_or_tpi):
      return self.formats[hd][zn][bpi_or_tpi]

   def getBPIPick(self, hd, zn):
      nominalFreq = self.bpiFile.getFrequencyByFormatAndZone(0,zn,hd)
      currentFreq = self.bpiFile.getFrequencyByFormatAndZone(self.getFormat(hd,zn,'BPI'),zn,hd)
      return float(currentFreq)/nominalFreq

   def getTPIPick(self, hd, zn):
      if testSwitch.extern.FE_0161563_208705_TPI_FMT_RELATIVE_UNITS:
         return float(self.getFormat(hd, zn, 'TPI') + self.RelativeToFormatScaler) / self.RelativeToFormatScaler
      else:
         nominalTracks = self.bpiFile.getNominalTracksPerSerpent()
         currentTracks = nominalTracks + self.getFormat(hd, zn, 'TPI')
         return float(currentTracks)/nominalTracks

   def scaleBPI(self, hd, zn, unscaled_bpi):
      return unscaled_bpi * self.getBPIPick(hd, zn)

   def unscaleBPI(self, hd, zn, scaled_bpi):
      return scaled_bpi / self.getBPIPick(hd, zn)

   def scaleTPI(self, hd, zn, unscaled_tpi):
      if testSwitch.FE_0215591_007867_COMPUTE_TPIC_AS_RATIO_MERGE_CL537310:
         return unscaled_tpi * self.getTPIPick(hd, zn)
      else:
         return 2.0 - (2.0 - unscaled_tpi) / self.getTPIPick(hd, zn)

   def unscaleTPI(self, hd, zn, scaled_tpi):
      if testSwitch.FE_0215591_007867_COMPUTE_TPIC_AS_RATIO_MERGE_CL537310:
         return scaled_tpi / self.getTPIPick(hd, zn)
      else:
         return 2.0 - (2.0 - scaled_tpi) * self.getTPIPick(hd, zn)

###########################################################################################################
############################### V B A R   C O R E   C L A S S E S #########################################
###########################################################################################################
class CVbarDataStore(object):
   #--------------------------------------------------------------------------------------------
   def __init__(self, initData = None):
      '''
      initData is a dict with the following format:
      {name: (typeCode, defaultValue),}
      '''
      self.niblet = None
      self.initData = initData
      self.store = {}
      
   #--------------------------------------------------------------------------------------------
   def buildStore(self, numOfHd = None, numOfZn = None, znList = None, numOfWp = None, loadData = None, initDone = True):
      if loadData is not None:
         self.store = loadData
      else:
         self.store['cfgNumOfHd'] = numOfHd
         if testSwitch.FE_0168027_007867_USE_PHYS_HDS_IN_VBAR_DICT:
            self.store['cfgHdMap'] = [objDut.LgcToPhysHdMap[hd] for hd in xrange(numOfHd)]
         else:
            self.store['cfgHdMap'] = range(numOfHd)
         if testSwitch.virtualRun:
            self.store['cfgNumOfZn'] = objDut.numZones   # TODO: fix this
            self.store['cfgZnIdx'] = None
         else:
            if znList is not None:
               self.store['cfgNumOfZn'] = len(znList)
               self.store['cfgZnIdx'] = {}
               for idx, zn in enumerate(znList):
                  self.store['cfgZnIdx'][zn] = idx
            else:
               self.store['cfgNumOfZn'] = numOfZn
               self.store['cfgZnIdx'] = None
         self.store['cfgNumOfWp'] = numOfWp
         self.store['cfgWpIdx'] = {}
         if self.store['cfgNumOfWp'] is not None:
            size = self.store['cfgNumOfZn']*self.store['cfgNumOfHd']*self.store['cfgNumOfWp']
         else:
            size = self.store['cfgNumOfZn']*self.store['cfgNumOfHd']
         for key, value in self.initData.items():
            self.store[key] = array(value[0], [value[1]]*size)
         if debug_RF: objMsg.printMsg('buildStore: initDone %s' % str(initDone))
         if initDone:
            self.initData = None
      
   #--------------------------------------------------------------------------------------------
   def getStore(self):
      return self.store
      
   #--------------------------------------------------------------------------------------------
   def __getitem__(self, name):
      return self.store[name]
      
   #--------------------------------------------------------------------------------------------
   def __setitem__(self, name, value):
      self.store[name] = value
      
   #--------------------------------------------------------------------------------------------
   def addItems(self, data):
      '''
      data is a dict with the following format:
      {name: (typeCode, defaultValue),}
      '''
      if self.store['cfgNumOfWp'] is not None:
         size = self.store['cfgNumOfZn']*self.store['cfgNumOfHd']*self.store['cfgNumOfWp']
      else:
         size = self.store['cfgNumOfZn']*self.store['cfgNumOfHd']
      for key, value in data.items():
         self.store[key] = array(value[0], [value[1]]*size)
         
   #--------------------------------------------------------------------------------------------
   def addWpEntry(self, numOfEntry, numOfHd = None, numOfZn = None, znList = None):
      if not self.store:
         self.buildStore(numOfHd, numOfZn, znList, numOfEntry, initDone = False)
      else:
         incSize = self.store['cfgNumOfZn']*self.store['cfgNumOfHd']*numOfEntry
         for key, value in self.initData.items():
            self.store[key].extend(array(value[0], [value[1]]*incSize))
      if debug_RF: objMsg.printMsg('addWpEntry: numOfEntry %d' % (numOfEntry))
         
   #--------------------------------------------------------------------------------------------
   def getNameList(self):
      return self.store.keys()
      
   #--------------------------------------------------------------------------------------------
   def useNiblet(self, niblet=None):
      self.niblet = niblet
      
   #--------------------------------------------------------------------------------------------
   def getRecord(self, name, hd, zn, wp = None):
      hd = self.store['cfgHdMap'][hd]
      try:
         if self.store['cfgZnIdx']:
            zn = self.store['cfgZnIdx'][zn]
         offset = self.store['cfgNumOfZn']*hd+zn
         if wp:
            offset += self.store['cfgWpIdx'][wp]
         return self.store[name][offset]
      except:
         objMsg.printMsg('getRecord: None') 
         return None
         
   #--------------------------------------------------------------------------------------------
   def setRecord(self, name, value, hd, zn, wp = None):
      hd = self.store['cfgHdMap'][hd]
      if self.store['cfgZnIdx']:
         zn = self.store['cfgZnIdx'][zn]
      offset = self.store['cfgNumOfZn']*hd+zn
      if wp:
         if wp not in self.store['cfgWpIdx']:
            idx = len(self.store['cfgWpIdx'])
            self.store['cfgWpIdx'][wp] = idx
         else:
            idx = self.store['cfgWpIdx'][wp]
         offset += idx
      try:
         self.store[name][offset] = value
      except TypeError:
         objMsg.printMsg('setRecord: %s %s (%d, %d, %s)' % (name, str(value), hd, zn, str(wp))) 
         raise
   
   #--------------------------------------------------------------------------------------------     
   def getRecordForHead(self, name, hd, wp = None):
      if wp:
         raise NotImplementedError('Not yet implemneted getRecordForHead with wp')
      hd = self.store['cfgHdMap'][hd]
      try:
         offset1 = self.store['cfgNumOfZn']*hd
         offset2 = self.store['cfgNumOfZn']*(hd+1)
         return self.store[name][offset1:offset2]
      except:
         objMsg.printMsg('getRecordForHead: None') 
         return None
   
   #--------------------------------------------------------------------------------------------
   def getNibletizedRecord(self, hd, zn, idx = None, niblet = None):
      ''' 
      Allow the passed-in niblet to override the active niblet, but just for this call
      '''
      if not niblet:
         if self.niblet:
            niblet = self.niblet
         else:
            return None

      record = {}
      hd = self.store['cfgHdMap'][hd]
      if self.store['cfgZnIdx']:
         zn = self.store['cfgZnIdx'][zn]
      offset = self.store['cfgNumOfZn']*hd+zn
      if idx:
         offset += idx
      for key, value in self.store.items():
         if key.startswith('cfg'):
            continue
         try:
            record[key] = value[offset]
         except:
            objMsg.printMsg('getNibletizedRecord: no %s' % (key)) 
      if not record:
         objMsg.printMsg('getNibletizedRecord: None') 
         return None

      if record['BPI'] > 0.0:
         record['BPI'] += niblet.settings['BPIMeasurementMargin'][zn]
      if record['TPI'] > 0.0:
         if testSwitch.FE_0215591_007867_COMPUTE_TPIC_AS_RATIO_MERGE_CL537310:
            record['TPI'] *= ((1 - niblet.settings['WriteFaultThreshold'][zn]) / (1 - niblet.settings['TPIMeasurementMargin'][zn] * record['TPI']))
         else:
            record['TPI'] += niblet.settings['TPIMeasurementMargin'][zn] - niblet.settings['WriteFaultThreshold'][zn]

      # SMR support
      if testSwitch.FAST_2D_S2D_TEST: #S2D
         if record.get('TPI_IDSS2D',-1) > 0.0:
            record['TPI_IDSS2D'] *= ((1 - 2 * niblet.settings['WriteFaultThresholdSlimTrack'][zn]) / (1 - 2 * niblet.settings['TPIMeasurementMargin'][zn] * record['TPI_IDSS2D']))
         if record.get('TPI_ODSS2D',-1) > 0.0:
            record['TPI_ODSS2D'] *= ((1 - 2 * niblet.settings['WriteFaultThresholdSlimTrack'][zn]) / (1 - 2 * niblet.settings['TPIMeasurementMargin'][zn] * record['TPI_ODSS2D']))

      # SMR support
      elif testSwitch.SMR:
         if record.get('TPI_IDSS',-1) > 0.0:
            if testSwitch.FE_0215591_007867_COMPUTE_TPIC_AS_RATIO_MERGE_CL537310:
               record['TPI_IDSS'] *= ((1 - 2 * niblet.settings['WriteFaultThresholdSlimTrack'][zn]) / (1 - 2 * niblet.settings['TPIMeasurementMargin'][zn] * record['TPI_IDSS']))
            else:
               record['TPI_IDSS'] += (2 * (niblet.settings['TPIMeasurementMargin'][zn] - niblet.settings['WriteFaultThresholdSlimTrack'][zn]))
         if record.get('TPI_ODSS',-1) > 0.0:
            if testSwitch.FE_0215591_007867_COMPUTE_TPIC_AS_RATIO_MERGE_CL537310:
               record['TPI_ODSS'] *= ((1 - 2 * niblet.settings['WriteFaultThresholdSlimTrack'][zn]) / (1 - 2 * niblet.settings['TPIMeasurementMargin'][zn] * record['TPI_ODSS']))
            else:
               record['TPI_ODSS'] += (2 * (niblet.settings['TPIMeasurementMargin'][zn] - niblet.settings['WriteFaultThresholdSlimTrack'][zn]))

      return record
      
###########################################################################################################
###########################################################################################################
class CVbarDataHelper:
   def __init__(self, store, hd, zn, wp = None):
      self.store = store
      self.hd = hd
      self.zn = zn
      self.wp = wp
      
   def __getitem__(self, name):
      return self.store.getRecord(name, self.hd, self.zn, self.wp)
      
   def __setitem__(self, name, value):
      self.store.setRecord(name, value, self.hd, self.zn, self.wp)

###########################################################################################################
###########################################################################################################
class CVbarWpMeasurement(CVbarDataStore):
   """
   This dictionary is used for determination of appropriate write power picks only.  It is based on hd/zn/wp
   indexing, so it will naturally have a large number of records.  In practical usage, not all hd/zn/wp records
   will be populated.  Once write power picks have been determined, this information is passed to the
   CVbarMeasurement class, without write power indexing, as only the records for the picked write powers are
   transferred.  The selected write power, (WP), become an entry in each CVbarMeasurement record.
   """
   def __init__(self, testZones = None, initStore = False, numOfWp = None):
      self.dictType = 'WP'  # Small overhead flag used for debug purposes
      if not testZones:
         self.objTestZones = CVbarTestZones()
      else:
         self.objTestZones = testZones
      data = {
         'BPI'             : ('f',  -1.0  ), 
         'BPIH'            : ('f',  -1.0  ), 
         'BPIR'            : ('f',  -1.0  ), 
         'TPI'             : ('f',  -1.0  ), 
         'BPIAdj'          : ('f',  0.0   ), 
         'Interp'          : ('c',  'F'   ), #False
         'BPIChanged'      : ('c',  'F'   ), #False
         'zHtClr'          : ('f',  -1.0  ),
      }
      CVbarDataStore.__init__(self, data)
      if initStore:
         if isinstance(self.objTestZones, CVbarTestZones): 
            znList = []
            for value in self.objTestZones.getTestZoneMap().values():
               znList += value
         else:
            znList = self.objTestZones
         self.buildStore(numOfHd=objDut.imaxHead, znList=znList, numOfWp=numOfWp)

   #--------------------------------------------------------------------------------------------
   def refreshTPIdata(self, measAllZns):
      ''' 
      This routine will copy TPI data from the AllZns dictionary to the dictionary in this class, (WpZns).
      '''
      for hd in xrange(objDut.imaxHead): 
         for zn in xrange(objDut.numZones):
            wp = objDut.wrPwrPick[hd][self.objTestZones.getTestZnforZn(zn)]
            self.store.setRecord('TPI', measAllZns.getRecord('TPI', hd, zn), hd, zn, wp)

###########################################################################################################
###########################################################################################################
class CVbarMeasurement(CVbarDataStore):
   """
   This dictionary is used for all aspects of VBAR, once the write power picks have been selected.  It is based
   on hd/zn indexing, contain all available metrics, and be populated for all heads and zones, although some
   of the zones may contain interpolated, rather than actual measured, values.  The write power pick becomes
   a value in each record.  This is the dictionary that gets uploaded to the SIM.
   """
   def __init__(self, initStore = False):
      self.dictType = 'All'  # Small overhead flag used for debug purposes
      # Dictionary of ALL metrics with defaults.  All new metrics should be added here.
      data = {
         'WP'              : ('i',  -1    ), 
         'BPI'             : ('f',  -1.0  ), 
         'TPI'             : ('f',  -1.0  ), 
         'HMS'             : ('f',  -1.0  ), 
         'HMSP'            : ('f',  0.0   ), 
         'BPIAdj'          : ('f',  0.0   ), 
         'Interp'          : ('c',  'F'   ), #False
         'BPIPick'         : ('f',  0.0   ), 
         'TPIPick'         : ('f',  0.0   ),
         'BPIChanged'      : ('c',  'T'   ), #True
         'TWC'             : ('f',  0.0   ), 
         'RD_OFST_IDSS'    : ('f',  0.0   ), 
         'RD_OFST_ODSS'    : ('f',  0.0   ), 
         'TPI_IDSS'        : ('f',  -1.0  ), 
         'TPI_ODSS'        : ('f',  -1.0  ), 
         'TPIPickEffective': ('f',  -1.0  ), #None
         'TPIFmtEffective' : ('f',  -1.0  ), #None
         'BPIH'            : ('f',  -1.0  ), 
         'BPIR'            : ('f',  -1.0  ), 
         'BPIMS'           : ('f',  -1.0  ),
         'BPISlopeHd'      : ('f',  -1.0  ), 
         'BPIConstHd'      : ('f',  -1.0  ), 
         'RSqHd'           : ('f',  -1.0  ), 
         'BPIMF'           : ('f',  -1.0  ),
         'BPISlope'        : ('f',  -1.0  ), 
         'BPIConst'        : ('f',  -1.0  ), 
         'RSq'             : ('f',  -1.0  ), 
         'BPIMH'           : ('f',  -1.0  ),
         'BPI_HMS'         : ('f',  -1.0  ), 
         'TPIMA'           : ('f',  0.0   ),
      }
      if testSwitch.FAST_2D_VBAR:
         data.update({
            'BPISlope'        : ('f',  1.0   ), 
            'BPIConst'        : ('f',  1.0   ), 
            'RSq'             : ('f',  0.0   ),
            'BPISlopeHd'      : ('f',  1.0   ), 
            'BPIConstHd'      : ('f',  1.0   ), 
            'RSqHd'           : ('f',  0.0   ),
            'TGT_SFR_IDX'     : ('i',  0     ),
            'TRACK_PER_BAND'  : ('i',  1     ),
            'TPI_OTC'         : ('f',  -1.0  ),
            'SNGL_DIR'        : ('i',  1     ),
            'RD_OFST_OTC'     : ('f',  0.0   ),
            'TPI_DSS'         : ('f',  -1.0  ),
            'TPI_IDSS2D'      : ('f',  -1.0  ),
            'TPI_ODSS2D'      : ('f',  -1.0  ),
            'SQZ_BPI'         : ('f',  -1.0  ),
         })
      if testSwitch.FE_0293889_348429_VBAR_MARGIN_BY_OTCTP:
         data.update({
            'TPI_INTER'       : ('f',  -1.0  ),
            'TPI_INTRA'       : ('f',  -1.0  ),
            'TPI_UMP'         : ('f',  -1.0  ),
         })
      CVbarDataStore.__init__(self, data)
      if initStore:
         self.buildStore(numOfHd=objDut.imaxHead, numOfZn=objDut.numZones)
      # Identify the metrics that will need to be interpolated across to fill out the database.
      if testSwitch.SMR:
         self.keysToInterpolate = ('BPI', 'TPI', 'TPI_IDSS', 'TPI_ODSS', 'RD_OFST_IDSS', 'RD_OFST_ODSS')
      else:
         self.keysToInterpolate = ('BPI', 'TPI',)

   #--------------------------------------------------------------------------------------------
   def serialize(self):
      return cPickle.dumps(self.getStore(), -1)

   #--------------------------------------------------------------------------------------------
   def unserialize(self, data):
      try:
         self.buildStore(loadData=cPickle.loads(data))
      except:
         objMsg.printMsg('Unserialize VBAR data failed')
         objMsg.printMsg(traceback.format_exc())

###########################################################################################################
###########################################################################################################

class CMeasureBPIAndTPI:
   """
   This class is a base class for CMeasureBPIAndTPIinAllZones and CMeasureBPIAndTPIinWpZones. It is not
   really intended for use stand alone.  This class requires a CVbarMeasurement or CVbarWpMeasurement class
   to be passed in, it will not create its own on the fly as it use to. Both CMeasureBPIAndTPIinAllZones and
   CMeasureBPIAndTPIinWpZones have an 'opMode' specifier as one of their members, which will be used to
   determine which course of action will be taken in these common functions.
   """
   def __init__(self, measurements):
      self.dut = objDut
      self.objRapTcc = CRapTcc()
      self.NUM_WRITE_POWERS = self.objRapTcc.NUM_WRITE_POWERS
      self.spcIdHlpr = getVbarGlobalClass(CSpcIdHelper, {'dut':self.dut})
      self.measurements = measurements

      self.oUtility = getVbarGlobalClass(CUtility)
      self.bpiFile = getVbarGlobalClass(CBpiFile)
      self.numHeads = self.dut.imaxHead
      self.numUserZones = self.dut.numZones
      if debug_VE: objMsg.printMsg('frm CMeasureBPIAndTPI- self.numUserZones : %d self.numHeads : %d' % (self.numUserZones,self.numHeads))
      self.objTestZones = CVbarTestZones()
      self.formatScaler = CVbarFormatScaler()

      # Get the target clearance on all heads
      self.clearances = get_clearances(range(self.numHeads), range(self.numUserZones), ST_SUPPRESS__ALL)

      self.param_list = ['TPI','TPI_DSS','TPI_ODSS','TPI_IDSS','RD_OFST_ODSS','RD_OFST_IDSS']
      self.header_title = 'Hd  Zn  TGT_SFR  BPI_2D  SQZ_DSS  SQZ_IDSS SQZ_ODSS  DIR   TPI_SSS  EFF_TPI  EFF_ADC  CMR_ADC  SMR_ADC  RD_OFST'

   #-------------------------------------------------------------------------------------------------------
   def measureBPIAndTPI(self, znLst, zapOTF=0):

      zone_mask_low = 0
      zone_mask_high = 0
      zone_mask_low, zone_mask_high = self.oUtility.convertZoneListtoZoneMask(znLst)
      hdMask = 0
      for hd in range(self.numHeads):
         hdMask |= 1 << hd
      prm = {
             'test_num'           : 211,
             'prm_name'           : 'Measure BPI and TPI',
             'timeout'            : 3600 * ( 1 + self.numHeads/2),
             'spc_id'             : 0,
             'NUM_TRACKS_PER_ZONE': 6,
             'ZONE_POSITION'      : TP.VBAR_ZONE_POS,
             'BPI_MAX_PUSH_RELAX' : TP.VbarBpiMaxPushRelax,
             'NUM_SQZ_WRITES'     : TP.num_sqz_writes,
             #'ZONE_MASK'          : self.oUtility.ReturnTestCylWord(znMask),
             'ZONE_MASK'          : self.oUtility.ReturnTestCylWord(zone_mask_low),
             'ZONE_MASK_EXT'          : self.oUtility.ReturnTestCylWord(zone_mask_high),
             'HEAD_RANGE'         : hdMask,
             'CWORD1'             : 0x3,   #run HMS, TPI, BPI
             'CWORD2'             : 0x0010,   # turn on BIE in BPI capability measurement
             'ADJ_BPI_FOR_TPI'    : TP.VbarAdjBpiForTpi,
             'DblTablesToParse'   : ['P211_WRT_PWR_TBL'],
             'TARGET_SER'         : TP.VbarTargetSER,
             'TPI_TARGET_SER'     : 5,
             'TPI_TLEVEL'         : TP.TPI_TLEVEL,
             'TLEVEL'             : 0,
             'THRESHOLD'          : 65,
             'RESULTS_RETURNED'   : 0,
      }

      if not testSwitch.extern.BF_0168996_007867_VBAR_REPLACE_INACCURATE_WP_TBL:
         # Oops, still older firmware - still using older table.
         prm['DblTablesToParse'] = ['P211_WP_TBL']

      #if self.opMode == 'AllZones':
      #   prm['RESULTS_RETURNED'] = 0x0006

      if self.opMode == 'AllZones':
         prm.update(getattr(TP, 'MeasureBPITPI_ZN_211', {}))
      else:
         prm.update(getattr(TP, 'MeasureBPITPI_WP_211', {}))

      if not self.opMode == 'AllZones':
         prm['CWORD1'] |= 0x0100 #use wp from (dlfile)rather from memory.
         #prepare write power triplets to be sent to the drive
         RegisterResultsCallback(self.processMemoryDataAsPCFile, [81,], 0)

      if zapOTF == 1:
         prm.update(TP.prm_ZAP_OTF)
         prm['CWORD1'] |= 0x800
         prm['TRACK_LIMIT'] = 0x0101
         prm['timeout'] = 3*prm['timeout']/2

      if testSwitch.extern.BF_0168996_007867_VBAR_REPLACE_INACCURATE_WP_TBL:
         # This fw flag supports a new table with a HD_LGC_PSN col, containing logical head values.
         table = DBLogReader(self.dut, 'P211_WRT_PWR_TBL', suppressed = True)
         colName = 'HD_LGC_PSN'
      else:
         table = DBLogReader(self.dut, 'P211_WP_TBL', suppressed = True)
         colName = 'HD_PHYS_PSN'
      table.ignoreExistingData()

      # Run the test
      getVbarGlobalClass(CProcess).St(prm)

      for record in table.iterRows():
         hd = int(record[colName])
         zn = int(record['DATA_ZONE'])

         if self.opMode == 'WpZones':
            wp = int(record['WPOWER'])
         _wp = self.opMode == 'WpZones' and wp or None
         meas = CVbarDataHelper(self.measurements, hd, zn, _wp)

         meas['BPI'] = self.formatScaler.scaleBPI(hd, zn, float(record['BPICAP']))
         if testSwitch.BPICHMS:
            meas['BPIR'] = self.formatScaler.scaleBPI(hd, zn, float(record['BPICAP']))
         meas['TPI'] = self.formatScaler.scaleTPI(hd, zn, float(record['TPICAP']))
         meas['Interp'] = 'F'

         if testSwitch.Enable_BPIC_ZONE_0_BY_FSOW_AND_SEGMENT == 1:
            if self.opMode == 'WpZones' and zn == 0 :
               wp_zn0 = int(record['WPOWER'])

      #####################   Measure BPIC at Higher Target Clearance   #######################
      # TODO: not optimized due to BPICHMS is off
      if testSwitch.BPICHMS and self.opMode != 'WpZones':

         self.__adjustTGTCLR()
         #prm.update( {'CWORD1': 0x0001} ) # BPIC only
         getVbarGlobalClass(CProcess).St(prm)
         self.__restoreTGTCLR()
         for record in table.iterRows():
            hd = int(record[colName])
            zn = int(record['DATA_ZONE'])

            self.measurements.setRecord('BPIH', self.formatScaler.scaleBPI(hd, zn, float(record['BPICAP'])), hd, zn)
            objMsg.printMsg('DBG: BPIMarginThreshold')
      #####################   Measure BPIC by FSOW and BPIC by Segemnt   #######################
      #Only do if the zone 0 is required to measure
      if testSwitch.Enable_BPIC_ZONE_0_BY_FSOW_AND_SEGMENT == 1:
          zn = 0
          znMask = 1 << zn
          measList             = [[] for hd in range(self.numHeads)]
          minBPI               = [[] for hd in range(self.numHeads)]
          minBPI_uncorrected   = [[] for hd in range(self.numHeads)]
          origTPI              = [[] for hd in range(self.numHeads)]
          finalTPI             = [[] for hd in range(self.numHeads)]
          if zn in znLst:
              for hd in xrange(self.numHeads):
                 #Need to add the full track BPIC_ID of zn 0
                 _wp = self.opMode == 'WpZones' and wp_zn0 or None
                 bpic = self.measurements.getRecord('BPI', hd, zn, _wp)
                 raw_bpiID = self.formatScaler.unscaleBPI(hd, zn, bpic)
                 measList[hd].append(raw_bpiID)

                 # Measure FSOW
                 prm.update( {'prm_name': 'Measure BPI FSOW'} )
                 prm.update( {'TEST_HEAD': hd} )
                 prm.update( {'ZONE_MASK': self.oUtility.ReturnTestCylWord(znMask)} )
                 prm.update( {'ZONE_MASK_EXT': self.oUtility.ReturnTestCylWord(0)} )
                 prm.update( {'ZONE_POSITION': 1} )
                 prm.update( {'CWORD1': 0x0001} ) # BPIC only
                 prm.update( {'CWORD2': 0x0080} ) # BPIC based on first sector
                 # Run FSOW test
                 getVbarGlobalClass(CProcess).St(prm)
                 colDict = self.dut.dblData.Tables('P211_BPI_CAP_AVG').columnNameDict()
                 row = self.dut.dblData.Tables('P211_BPI_CAP_AVG').rowListIter(index=len(self.dut.dblData.Tables('P211_BPI_CAP_AVG'))-1).next()
                 bpic = float(row[colDict['BPI_CAP_AVG']])
                 measList[hd].append(bpic)

                 # Measure BPIC by Segment
                 prm.update( {'prm_name': 'Measure BPI SEGMENT'} )
                 prm.update( {'TEST_HEAD': hd} )
                 prm.update( {'ZONE_MASK': self.oUtility.ReturnTestCylWord(znMask)} )
                 prm.update( {'ZONE_MASK_EXT': self.oUtility.ReturnTestCylWord(0)} )
                 prm.update( {'ZONE_POSITION': 1} )
                 prm.update( {'CWORD1': 0x0001} ) # BPIC only
                 prm.update( {'CWORD2': 0x0040} ) # BPIC based on segment of NUM_REGIONS_LIMIT
                 prm.update( {'NUM_REGIONS_LIMIT': 20} ) # Num of segment
                 # Run BER by segment test
                 getVbarGlobalClass(CProcess).St(prm)
                 row = self.dut.dblData.Tables('P211_BPI_CAP_AVG').rowListIter(index=len(self.dut.dblData.Tables('P211_BPI_CAP_AVG'))-1).next()
                 bpic = float(row[colDict['BPI_CAP_AVG']])
                 measList[hd].append(bpic)

                 # get the min of n readings
                 minBPI[hd]             = min(measList[hd])
                 minBPI_uncorrected[hd] = minBPI[hd]

                 objMsg.printMsg('measList = %s, minBPI = %s' % (str(measList[hd]),str(minBPI[hd])))
                 if ((minBPI[hd] - raw_bpiID) <= -0.04):
                    minBPI[hd] += -0.05
                 elif ((minBPI[hd] - raw_bpiID) <= -0.03):
                    minBPI[hd] += -0.03
                 elif ((minBPI[hd] - raw_bpiID) <= -0.02):
                    minBPI[hd] += -0.01
                 objMsg.printMsg('minBPI(after correction) = %s' % (str(minBPI[hd])))

                 # Get the original TPIC
                 _wp = self.opMode == 'WpZones' and wp or None
                 tpic = self.measurements.getRecord('TPI', hd, zn, _wp)
                 raw_tpiID = self.formatScaler.unscaleTPI(hd, zn, tpic)
                 origTPI[hd]  = float(raw_tpiID)
                 objMsg.printMsg('minBPI = %f raw_bpiID = %f' % (minBPI[hd],raw_bpiID))

                 if abs(minBPI[hd] - raw_bpiID) > 0.001:
                     objMsg.printMsg('Need to remeasure the TPIC as the BPIC had been changed !!!!')

                     # Add back the BPC to the database
                     self.measurements.setRecord('BPI', self.formatScaler.scaleBPI(hd, zn, float(minBPI[hd])), hd, zn, _wp)
                     # Remeasure the TPIC if the BPIC had been changed
                     prm.update( {'HEAD_MASK': 1 << hd} )
                     prm.update( {'ZONE_MASK': self.oUtility.ReturnTestCylWord(znMask)} )
                     prm.update( {'ZONE_MASK_EXT': self.oUtility.ReturnTestCylWord(0)} )
                     prm.update( {'CWORD1': 0x0002} ) # TPIC only
                     prm.update( {'ADJ_BPI_FOR_TPI': self.calcBPIBackoff(hd, zn, TP.VbarAdjBpiForTpi) } )
                     getVbarGlobalClass(CProcess).St(prm)
                     colDict = self.dut.dblData.Tables('P211_TPI_CAP_AVG').columnNameDict()
                     row = self.dut.dblData.Tables('P211_TPI_CAP_AVG').rowListIter(index=len(self.dut.dblData.Tables('P211_TPI_CAP_AVG'))-1).next()
                     tpic = float(row[colDict['TPI_CAP_AVG']])
                     objMsg.printMsg('tpic = %s' % (str(tpic)))

                     # Add back the TPIC to the database
                     self.measurements.setRecord('TPI', self.formatScaler.scaleTPI(hd, zn, float(tpic)), hd, zn, _wp)
                     # Done
                     finalTPI[hd]  = float(tpic)
                 else:
                     finalTPI[hd]  = origTPI[hd]
                     objMsg.printMsg('No change on the BPIC on zone 0. Do not need to remeasure the tpic!!!')


              # e.g. objMsg.printMsg("%2s  %2s  %8s  %8s  %18s  %18s  %18s" %("Hd", "Zn", "BpiC", "TpiC", "sectorsPerTrack", "TracksPerZone", "znCapacity", ))
              # e.g. objMsg.printMsg("%2d  %2d  %8.4f  %8.4f  %18.4f  %18.4f  %18.4f  " %(hd, zn, bpic, tpic,...
              # Display result
              objMsg.printMsg('P_VBAR_FORMAT_SUMMARY_ZN0')
              objMsg.printMsg("%4s %4s %9s %9s %9s %9s %9s %15s %15s %9s %9s %15s %15s" \
                             % ("HEAD", "ZONE", "BPIC_ORIG", "BPIC_FSOW", "BPIC_SEGM", "BPIC_MINM", "BPIC_FINL", "BPIC_ORIG_SCALE", \
                             "BPIC_FINL_SCALE", "TPIC_ORIG", "TPIC_FINL", "TPIC_ORIG_SCALE", "TPIC_FINL_SCALE") )
              for hd in range(self.numHeads):
                 objMsg.printMsg("%4.2d %4.2d %9.4f %9.4f %9.4f %9.4f %9.4f %15.4f %15.4f %9.4f %9.4f %15.4f %15.4f" \
                             % (hd, zn, measList[hd][0], measList[hd][1], measList[hd][2], minBPI_uncorrected[hd], minBPI[hd], \
                             self.formatScaler.scaleBPI(hd, zn, float(measList[hd][0])), self.formatScaler.scaleBPI(hd, zn, float(minBPI[hd])), \
                             origTPI[hd], finalTPI[hd], self.formatScaler.scaleTPI(hd, zn, float(origTPI[hd])), self.formatScaler.scaleTPI(hd, zn, float(finalTPI[hd])) ))
                 # Log the table
                 spcId = 1
                 self.dut.dblData.Tables('P_VBAR_FORMAT_SUMMARY_ZN0').addRecord({
                                'SPC_ID'          : spcId,
                                'OCCURRENCE'      : 1,#dblogOccCnt['P_VBAR_MEASUREMENTS'],
                                'SEQ'             : self.dut.objSeq.getSeq(),
                                'TEST_SEQ_EVENT'  : 1,
                                'HD_PHYS_PSN'     : self.dut.LgcToPhysHdMap[hd],
                                'HD_LGC_PSN'      : hd,
                                'DATA_ZONE'       : zn,
                                'BPIC_ORIG'       : round(measList[hd][0], 4),
                                'BPIC_FSOW'       : round(measList[hd][1], 4),
                                'BPIC_SEGM'       : round(measList[hd][2], 4),
                                'BPIC_MINM'       : round(minBPI_uncorrected[hd], 4),
                                'BPIC_FINL'       : round(minBPI[hd], 4),
                                'BPIC_ORIG_SCALE' : round(self.formatScaler.scaleBPI(hd, zn, float(measList[hd][0])), 4),
                                'BPIC_FINL_SCALE' : round(self.formatScaler.scaleBPI(hd, zn, float(minBPI[hd])), 4),
                                'TPIC_ORIG'       : round(origTPI[hd], 4),
                                'TPIC_FINL'       : round(finalTPI[hd], 4),
                                'TPIC_ORIG_SCALE' : round(self.formatScaler.scaleTPI(hd, zn, float(origTPI[hd])) , 4),
                                'TPIC_FINL_SCALE' : round(self.formatScaler.scaleTPI(hd, zn, float(finalTPI[hd])) , 4),
                             })
              objMsg.printDblogBin(self.dut.dblData.Tables('P_VBAR_FORMAT_SUMMARY_ZN0'), spcId)
              #################################################################################################################################################################################################################################################
      # Display results
      hdzns = [(hd,zn) for hd in range(self.numHeads) for zn in znLst]
      self.printMeasurements(hdzns)

      return self.measurements
   #-------------------------------------------------------------------------------------------------------
   def measureSegmented_BPIMargin(self, oMeas, znLst, zapOTF=0):
      zone_mask_low = 0
      zone_mask_high = 0
      for zn in znLst:
         if zn < 32:
            zone_mask_low |= (1 << zn)
         else:
            zone_mask_high |= (1 << (zn -32))
      hdMask = 0
      for hd in range(self.numHeads):
         hdMask |= 1 << hd

      prm = {
             'test_num'           : 211,
             'prm_name'           : 'Measure BPI Slope',
             'timeout'            : 3600 * ( 1 + self.numHeads/2),
             'spc_id'             : 0,
             'NUM_TRACKS_PER_ZONE': 6,
             'ZONE_POSITION'      : TP.VBAR_ZONE_POS,
             'BPI_MAX_PUSH_RELAX' : TP.VbarBpiMaxPushRelax,
             'NUM_SQZ_WRITES'     : TP.num_sqz_writes,
             'ZONE_MASK'          : self.oUtility.ReturnTestCylWord(zone_mask_low),
             'ZONE_MASK_EXT'          : self.oUtility.ReturnTestCylWord(zone_mask_high),
             'HEAD_RANGE'         : hdMask,
             'CWORD1'             : 0x3,   #run HMS, TPI, BPI
             'CWORD2'             : 0x0010,   # turn on BIE in BPI capability measurement
             'ADJ_BPI_FOR_TPI'    : TP.VbarAdjBpiForTpi,
             'DblTablesToParse'   : ['P211_WRT_PWR_TBL'],
             'TARGET_SER'         : TP.VbarTargetSER,
             'TPI_TARGET_SER'     : 5,
             'TPI_TLEVEL'         : TP.TPI_TLEVEL,
             'TLEVEL'             : 0,
             'THRESHOLD'          : 65,
            }

      if not testSwitch.extern.BF_0168996_007867_VBAR_REPLACE_INACCURATE_WP_TBL:
         # Oops, still older firmware - still using older table.
         prm['DblTablesToParse'] = ['P211_WP_TBL']


      if self.opMode == 'AllZones':
         prm.update(getattr(TP, 'MeasureBPITPI_ZN_211', {}))
      else:
         prm.update(getattr(TP, 'MeasureBPITPI_WP_211', {}))

      if not self.opMode == 'AllZones':
         prm['CWORD1'] |= 0x0100 #use wp from (dlfile)rather from memory.
         #prepare write power triplets to be sent to the drive
         RegisterResultsCallback(self.processMemoryDataAsPCFile, [81,], 0)

      if zapOTF == 1:
         prm.update(TP.prm_ZAP_OTF)
         prm['CWORD1'] |= 0x800
         prm['TRACK_LIMIT'] = 0x0101
         prm['timeout'] = 3*prm['timeout']/2

      if testSwitch.extern.BF_0168996_007867_VBAR_REPLACE_INACCURATE_WP_TBL:
         # This fw flag supports a new table with a HD_LGC_PSN col, containing logical head values.
         table = DBLogReader(self.dut, 'P211_WRT_PWR_TBL', suppressed = True)
         colName = 'HD_LGC_PSN'
      else:
         table = DBLogReader(self.dut, 'P211_WP_TBL', suppressed = True)
         colName = 'HD_PHYS_PSN'
      table.ignoreExistingData()

      #####################           Measure Segmented BPIC   #######################
      # TODO: not optimized due to FE_SEGMENTED_BPIC is off
      if testSwitch.FE_SEGMENTED_BPIC and self.opMode != 'WpZones':
         segment_bpi_debug = 0
         # Set Parameters
         prm_segmentedBPI = prm.copy() # just make another copy so safe to the rest of the testitems
         prm_segmentedBPI.update( {'CWORD1': 0x0001} ) # BPIC only
         prm_segmentedBPI['RESULTS_RETURNED'] = 16


         # Set BPI Table index
         try:
            if (testSwitch.extern.SRC_11K_M):
                bpiMeasIndex = len(self.dut.dblData.Tables('P211_M11K_BPI_MEASUREMENT'))
            elif (testSwitch.MARVELL_SRC):
                bpiMeasIndex = len(self.dut.dblData.Tables('P211_M_BPI_MEASUREMENT'))
            else:
                bpiMeasIndex = len(self.dut.dblData.Tables('P211_BPI_MEASUREMENT'))
         except:
            bpiMeasIndex = 0

         # Run the test for -3.2
         prm_segmentedBPI.update( {'TARGET_SER': TP.SOVABER_SWEEP1} ) # -3.2
         SetFailSafe()
         getVbarGlobalClass(CProcess).St(prm_segmentedBPI)
         ClearFailSafe()

         # Run the test for -.2
         prm_segmentedBPI.update( {'TARGET_SER': TP.SOVABER_SWEEP2} ) # -2.2
         SetFailSafe()
         getVbarGlobalClass(CProcess).St(prm_segmentedBPI)
         ClearFailSafe()

         # Get the BER vs BPIC Slope
         slopeList2 ={}
         if (testSwitch.extern.SRC_11K_M):
             table4 = self.dut.dblData.Tables('P211_M11K_BPI_MEASUREMENT').tableDataObj()
         elif (testSwitch.MARVELL_SRC):
             table4 = self.dut.dblData.Tables('P211_M_BPI_MEASUREMENT').tableDataObj()
         else:
             table4 = self.dut.dblData.Tables('P211_BPI_MEASUREMENT').tableDataObj()
         if segment_bpi_debug:
            objMsg.printMsg('SlopeData')
            objMsg.printMsg('Hd    Zn      Track      BPI       BPIS       SOVA_BER')
         for hd in range(self.numHeads):
            dataList2[hd,'BPI'] = []
            dataList2[hd,'BER'] = []
            for zn in range(self.numUserZones):
               dataList2[hd,zn,'BPI'] = []
               dataList2[hd,zn,'BER'] = []
               for datarow in range(bpiMeasIndex, len(table4)):
                  if hd == int(table4[datarow][colName]) and zn == int(table4[datarow]['DATA_ZONE']):
                     trk = int(table4[datarow]['TRK_NUM'])
                     bpi_pct = 1.0 + float(table4[datarow]['DELTA_BPI_PCT']) / 100
                     bpi_pct_s = self.formatScaler.scaleBPI(hd, zn, bpi_pct)
                     ser_log = math.log10( max(0.0001, float( table4[datarow]['SECTOR_ERROR_RATE'] )) )
                     dataList2[hd, zn, 'BPI'].append(bpi_pct_s)
                     dataList2[hd, zn, 'BER'].append(ser_log)
                     dataList2[hd, 'BPI'].append(bpi_pct_s)
                     dataList2[hd, 'BER'].append(ser_log)
                     if segment_bpi_debug:
                        objMsg.printMsg('%d    %2d       %5d   %3.4f     %3.4f        %3.4f' % (hd, zn, trk, bpi_pct, bpi_pct_s, ser_log))

               meas = CVbarDataHelper(self.measurements, hd, zn)
               meas['BPISlope'],meas['BPIConst'],meas['RSq'] = linreg(dataList2[hd,zn,'BER'],dataList2[hd,zn,'BPI'])


            BPISlope, BPIConst, RSq = linreg(dataList2[hd,'BER'],dataList2[hd,'BPI'])
            for zn in range(self.numUserZones):
               meas = CVbarDataHelper(self.measurements, hd, zn)
               meas['BPISlopeHd'], meas['BPIConstHd'], meas['RSqHd'] = BPISlope, BPIConst, RSq

         if segment_bpi_debug:
            objMsg.printMsg('===================================')
            objMsg.printMsg('Hd        Slope          Constant        Rsq')
            for hd in range(self.numHeads):
               meas = CVbarDataHelper(self.measurements, hd, zn)
               objMsg.printMsg('%d    %4.8f        %4.8f     %3.4f' % (hd, meas['BPISlopeHd'], meas['BPIConstHd'], meas['RSqHd']))

            objMsg.printMsg('==========================================')
            objMsg.printMsg('Hd    Zn         Slope          Constant        Rsq')
            for hd in range(self.numHeads):
               for zn in range(self.numUserZones):
                  meas = CVbarDataHelper(self.measurements, hd, zn)
                  objMsg.printMsg('%d    %2d     %4.8f        %4.8f     %3.4f' % (hd, zn, meas['BPISlope'], meas['BPIConst'], meas['RSq']))

         # Set Segmented BER Parameters
         segmented_Prm = TP.prm_OAR_ErrRate_250['base'].copy()


         segmented_Prm['NUM_TRACKS_PER_ZONE'] = TP.NUM_TRACKS_TO_MEASURE
         segmented_Prm['timeout'] = self.numHeads * 3600
         if type(segmented_Prm['CWORD2']) in [types.TupleType,types.ListType]:
            segmented_Prm['CWORD2'] = segmented_Prm['CWORD2'][0]
         segmented_Prm['CWORD2'] = segmented_Prm['CWORD2'] | 0x312 # Adjust and collect all error

         # Set SEGMENTED BER Table index
         try:
            SegBERMeasIndex = len(self.dut.dblData.Tables('P250_SEGMENT_BER_SUM'))
         except:
            SegBERMeasIndex = 0

         # Run Segmented BER Parameters
         SetFailSafe()
         # Run on Position 0, zones 0,1
         segmented_Prm['ZONE_MASK'] = (0, 0x0003)#(128L, 0)
         getVbarGlobalClass(CProcess).St(segmented_Prm)#P211_ELT_ERROR
         # Run on Position 198, zones 1 to ID
         segmented_Prm['ZONE_MASK'] = (0xFFFF, 0xFFFE)#(128L, 0)
         segmented_Prm['ZONE_POSITION'] = 198
         getVbarGlobalClass(CProcess).St(segmented_Prm)#P211_ELT_ERROR

         ClearFailSafe()

         #objMsg.printMsg('=======================================')
         #objMsg.printMsg('SEG_DBG:Hd    Zn    BPIM_SEG          BPIM_FSOW     CURBPI    BPIC')
         table4 = self.dut.dblData.Tables('P250_SEGMENT_BER_SUM').tableDataObj()
         curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
         if table4:
            for hd in range(self.numHeads):
               for zn in range(self.numUserZones):
                  meas = CVbarDataHelper(self.measurements, hd, zn)
                  meas['BPIMS'] = -1.0
                  meas['BPIMF'] = -1.0

                  # Get Current Format
                  curFrequency = self.bpiFile.getFrequencyByFormatAndZone(oMeas.formatScaler.getFormat(hd,zn,'BPI'),zn,hd)
                  nominalFrequency = self.bpiFile.getFrequencyByFormatAndZone(0,zn,hd)
                  curformat = float(curFrequency)/nominalFrequency
                  deltaformat = curformat - meas['BPI'] # This accounts for the difference in existing BPI Format and BPIC

                  for datarow in range(SegBERMeasIndex, len(table4)):
                     if hd == int(table4[datarow]['HD_PHYS_PSN']) and zn == int(table4[datarow]['DATA_ZONE']):
                        worse_seg_err_rate = float(table4[datarow]['WORST_SEG_ERR_RATE'])
                        worse_fsow_seg_err_rate = float(table4[datarow]['WORST_FSOW_ERR_RATE'])
                        ave_err_rate = float(table4[datarow]['AVE_ERR_RATE'])
                        if meas['BPIConstHd'] > meas['RSq']:
                           slope = meas['BPISlopeHd']
                        else:
                           slope = meas['BPISlope']
                        intercept = meas['BPIConst']
                        bpic_seg = slope * worse_seg_err_rate + intercept
                        bpic_fsow = slope * worse_fsow_seg_err_rate + intercept
                        bpic_ave = slope * ave_err_rate + intercept
                        bpic_tgt = slope * TP.TARGET_MINIMUM_SOVA_BER + intercept

                        meas['BPIMS'] = max(meas['BPIMS'],bpic_seg - bpic_tgt - deltaformat)
                        meas['BPIMF'] = max(meas['BPIMF'],bpic_fsow - bpic_tgt - deltaformat)
                        #objMsg.printMsg('SEG_DBG:%d    %2d     %4.8f        %4.8f        %4.8f        %4.8f' % (hd, zn, meas['BPIMS'], meas['BPIMF'], curformat, meas['BPI']))

                  dblog_record = {
                     'SPC_ID'          : 200,
                     'OCCURRENCE'      : occurrence,
                     'SEQ'             : curSeq,
                     'TEST_SEQ_EVENT'  : testSeqEvent,
                     'HD_PHYS_PSN'     : self.dut.LgcToPhysHdMap[hd],
                     'DATA_ZONE'       : zn,
                     'HD_LGC_PSN'      : hd,
                     'BPI_SLOPE'       : round(meas['BPISlope'], 5),
                     'BPI_INTCPT'      : round(meas['BPIConst'], 5),
                     'BPI_RSQ'         : round(meas['RSq'], 3),
                     'BPIM_RSEG'       : round(meas['BPIMS'], 4),
                     'BPIM_RFSW'       : round(meas['BPIMF'], 4),
                     'BPI_CUR'         : round(curformat, 4),
                     'BPI_CAP'         : round(meas['BPI'], 4),
                     }
                  self.dut.dblData.Tables('P_VBAR_BPI_SLOPE_SUMMARY').addRecord(dblog_record)
            objMsg.printDblogBin(self.dut.dblData.Tables('P_VBAR_BPI_SLOPE_SUMMARY'))
      return self.measurements

   #-------------------------------------------------------------------------------------------------------
   def printMeasurements(self, hdzns, spcId = None):
      dblogOccCnt['P_VBAR_MEASUREMENTS'] += 1
      if spcId == None:
         spcId = self.spcIdHlpr.getSpcId('P_VBAR_FORMAT_SUMMARY')

      sumADC = [0.0000] * self.numHeads
      countADC = [0] * self.numHeads

      for hd, zn in hdzns:
         if self.opMode == 'AllZones':
            wps = [self.dut.wrPwrPick[hd][self.objTestZones.getTestZnforZn(zn)]]
         else:
            # Special write power dictionary uses keys of (hd,zn,wp).
            wps = range(self.NUM_WRITE_POWERS)

         for wp in wps:
            _wp = self.opMode == 'WpZones' and wp or None
            meas = CVbarDataHelper(self.measurements, hd, zn, _wp)
            if self.opMode == 'WpZones':
               hmsCap = -1.0
            else:
               wp = meas['WP']
               hmsCap = round(meas['HMS'], 4)

            # Accumulate ADCs
            adc = meas['BPI'] * meas['TPI']
            sumADC[hd] += adc
            countADC[hd] += 1

            # Log the table
            self.dut.dblData.Tables('P_VBAR_MEASUREMENTS').addRecord({
                           'SPC_ID'          : spcId,
                           'OCCURRENCE'      : dblogOccCnt['P_VBAR_MEASUREMENTS'],
                           'SEQ'             : self.dut.objSeq.getSeq(),
                           'TEST_SEQ_EVENT'  : 1,
                           'HD_PHYS_PSN'     : self.dut.LgcToPhysHdMap[hd],
                           'HD_LGC_PSN'      : hd,
                           'DATA_ZONE'       : zn,
                           'WRT_PWR_NDX'     : wp,
                           'BPI_CAP'         : round(meas['BPI'], 4),
                           'TPI_CAP'         : round(meas['TPI'], 4),
                           'HMS_CAP'         : hmsCap,
                           'ADC'             : round(adc, 4),
                           'BPICHMS'         : round(meas['BPIH'], 4),
                        })

      if testSwitch.FE_0152775_420281_P_DISPLAY_ADC_FOR_ADG_CAPTURE_POOR_HEAD:
         for hd in range(self.numHeads):
            self.dut.avgADC[hd] = sumADC[hd]/countADC[hd]

      if not testSwitch.CM_REDUCTION_REDUCE_PRINTDBLOGBIN:
         objMsg.printDblogBin(self.dut.dblData.Tables('P_VBAR_MEASUREMENTS'), spcId)

   #-------------------------------------------------------------------------------------------------------
   def measureTPI(self, hd, zn, tpiFeedForward = 0.0, wp=None, prm_override=getattr(TP, 'MeasureTPI_211', {}), zapOTF=0, target_SFR = 0.0, mode = "SFR"): #ccyy
      ############# Set up parameter block ##############
      if mode == "OTC":
         prm_TPI_211 = deepcopy(TP.prm_TPI_211_OTC)
         prm_TPI_211.update({'TEST_HEAD': hd, 'ZONE': zn})
         if 'HEAD_RANGE' in prm_TPI_211: del prm_TPI_211['HEAD_RANGE']
      else:
         prm_TPI_211 = {'test_num'           : 211,
                        'prm_name'           : 'MeasureTPI_211',
                        'TEST_HEAD'          : hd,
                        'ZONE'               : zn,
                        'NUM_TRACKS_PER_ZONE': 6,
                        'NUM_SQZ_WRITES'     : TP.num_sqz_writes,
                        'ZONE_POSITION'      : TP.VBAR_ZONE_POS,
                        'CWORD1'             : 0x0036,   #Enable multi-track mode
                        'CWORD2'             : 0x0000,
                        'SET_OCLIM'          : 655,
                        'TARGET_SER'         : 5,
                        'TPI_TARGET_SER'     : 5,
                        'RESULTS_RETURNED'   : 0x0006,
                        'timeout'            : 3600,
                        'spc_id'             : 0,
         }
      prm_TPI_211.update(prm_override)     #ccyy

      if testSwitch.SMR and (mode != "OTC"):
         prm_TPI_211['ADJ_BPI_FOR_TPI'] = self.calcBPIBackoff(hd, zn, 0, wp, target_SFR)
      else:
         prm_TPI_211['ADJ_BPI_FOR_TPI'] = self.calcBPIBackoff(hd, zn, -5, wp)
      printDbgMsg("BPIForTPI  %d " % prm_TPI_211['ADJ_BPI_FOR_TPI'])

      if zapOTF == 1:
         prm_TPI_211.update(TP.prm_ZAP_OTF)
         prm_TPI_211['CWORD1'] |= 0x800
         prm_TPI_211['TRACK_LIMIT'] = 0x0101
         prm_TPI_211['timeout'] = 3*prm_TPI_211['timeout']/2


      # if the write powers have already been selected, do the measurements at nominal clearance
      if self.opMode == 'AllZones':
         prm_TPI_211['CWORD1'] &= 0xFFAF

      #Scale the TPI capability from the last measurement up to servo dacs of capabilty
      # TPI Cap in Servo Dacs = (TPI capability(relative to nominal = 1.0) - 1.0) * 256
      #Set the starting point for the TPI margin feedback

      if testSwitch.FAST_2D_VBAR_TPI_FF:
         prm_TPI_211['START_OT_FOR_TPI'] = int(round((tpiFeedForward-1)*256,0))
      else:
         prm_TPI_211['START_OT_FOR_TPI'] = int(round((tpiFeedForward-1)*256,0)) - 10



      ############# Run the measurement ##############

      table_TpiCap = DBLogReader(self.dut, 'P211_TPI_CAP_AVG')
      table_TpiCap.ignoreExistingData()

      if testSwitch.SMR:
         #read offset has been merged into one tpi table for tpi measurement
         if testSwitch.T211_MERGE_READ_OFFSET_TBL_INTO_TPI_MEAS_TBL:
            table_RdOfst = table_TpiCap 
         else:
            table_RdOfst = DBLogReader(self.dut, 'P211_RD_OFST_AVG')
            table_RdOfst.ignoreExistingData()

      if mode == "OTC":
         try: tpiMeasIndex = len(self.dut.dblData.Tables('P211_TPI_MEASUREMENT3'))
         except: tpiMeasIndex = 0
         objMsg.printMsg('tpiMeasIndex %d' % tpiMeasIndex)

      try: getVbarGlobalClass(CProcess).St(prm_TPI_211)
      except:
         if mode == "OTC": pass
         else: raise

      row = table_TpiCap.findRow({'HD_LGC_PSN':hd, 'DATA_ZONE':zn})
      if row:
         tpi = float(row['TPI_CAP_AVG'])
      else: tpi = 0.0

      if mode == "OTC" and testSwitch.MEASURE_TMR:
         self.measureTMR(tpiMeasIndex)

      if testSwitch.SMR:
         row = table_RdOfst.findRow({'HD_LGC_PSN':hd, 'DATA_ZONE':zn})
         if row: 
            rd_ofst = float(row['RD_OFST_AVG'])
         else: 
            rd_ofst = 0.0
         return tpi, rd_ofst
      else: return tpi
   
   #-------------------------------------------------------------------------------------------------------
   def measureTMR(self, startIndex):
      # TODO: test
      from Servo import CServoFunc
      oSrvFunc   = CServoFunc()
      newPrm_33 = deepcopy(TP.tmrMeasurePrm_2)
      endIndex = len(self.dut.dblData.Tables('P211_TPI_MEASUREMENT3'))
      colDict = self.dut.dblData.Tables('P211_TPI_MEASUREMENT3').columnNameDict()
      table4 = self.dut.dblData.Tables('P211_TPI_MEASUREMENT3').rowListIter(index=startIndex)
      prevtrk = -1
      length = endIndex-startIndex
      for idx, row in enumerate(table4):
         hd = int(row[colDict['HD_PHYS_PSN']])
         zn = int(row[colDict['DATA_ZONE']])
         trk = int(row[colDict['TRK_NUM']])
         if (prevtrk != trk and prevtrk != -1):
            oSrvFunc.St(newPrm_33)
         elif idx == length-1:
            oSrvFunc.St(newPrm_33)
            break

         dir = int(row[colDict['DIR']])
         offsetleft = int(float(row[colDict['N_OFST']]))
         offsetright = int(float(row[colDict['P_OFST']]))

         newPrm_33.update({'TEST_HEAD': hd})
         newPrm_33.update({'ZONE': zn})
         newPrm_33.update({'TEST_CYL': self.oUtility.ReturnTestCylWord(trk-1)})
         newPrm_33.update({'END_CYL': self.oUtility.ReturnTestCylWord(trk+2)})
         newPrm_33.update({'S_OFFSET': (offsetright - offsetleft) / 2})
         prevtrk = trk

   #-------------------------------------------------------------------------------------------------------
   def measureBPI(self, hd, zn, wp, prm_override=getattr(TP, 'MeasureBPI_211', {})):
      ############# Set up parameter block ##############
      if testSwitch.FE_0120024_340210_ATI_IN_WRT_PWR_PICKER :
         wc, ovs, ovd = self.objRapTcc.VbarWPTable[hd][zn][wp]
      else:
         wc, ovs, ovd = self.objRapTcc.VbarWPTable[zn][wp]

      prm_BPI_211 = {'test_num'           : 211,
                     'prm_name'           : 'MeasureBPI_211',
                     'TEST_HEAD'          : hd,
                     'ZONE'               : zn,
                     'NUM_TRACKS_PER_ZONE': 6,
                     'ZONE_POSITION'      : TP.VBAR_ZONE_POS,
                     'BPI_MAX_PUSH_RELAX' : TP.VbarBpiMaxPushRelax,
                     'CWORD1'             : 0x0015, #Enable multi-track mode
                     'CWORD2'             : 0x0010, #Enable bie error rate in T211
                     'SET_OCLIM'          : 655,
                     'WRITE_CURRENT'      : wc,
                     'DAMPING'            : ovs,
                     'DURATION'           : ovd,
                     'RESULTS_RETURNED'   : 0x000E,
                     'timeout'            : 3600,
                     'spc_id'             : 0,
                     }

      prm_BPI_211.update(prm_override)


      # if the write powers have already been selected,
      # do the measurements at nominal clearance
      if self.opMode == 'AllZones':
         prm_BPI_211['CWORD1'] &= 0xFFAF

      if testSwitch.FE_0119998_231166_FACTORY_VBAR_ADC_ENHANCEMENTS:
         # if EC13409 rerun vbar, back off from 40% to 20%
         if self.dut.driveattr['WTF_CTRL'] == 'VBAR_13409' and prm_BPI_211['CWORD1'] & 0x10:
            prm_BPI_211['CWORD1'] &= 0xFFEF
            prm_BPI_211['CWORD1'] |= 0x20

      ############# Run the measurement ##############
      table = DBLogReader(self.dut, 'P211_BPI_CAP_AVG')
      table.ignoreExistingData()

      getVbarGlobalClass(CProcess).St(prm_BPI_211)

      row = table.findRow({'HD_LGC_PSN':hd, 'DATA_ZONE':zn})
      if row:
         bpi = float(row['BPI_CAP_AVG'])
      else:
         bpi = 0.0
      objMsg.printMsg("Hd %s BPI  %s" % (str(hd), str(bpi)))

      return bpi

   #-------------------------------------------------------------------------------------------------------
   def calcBPIBackoff(self, hd, zn, adjustment, wp = None, target_SFR = 0.0):
      # According to the algorithm, we need to use BPI capability minus the BPI margin to test TPI capability
      if self.opMode == 'WpZones':
         bpic = self.measurements.getRecord('BPI', hd, zn, wp)
      elif target_SFR != 0.0: # Calculate based on Linear Regression
         if testSwitch.FAST_2D_VBAR_XFER_PER_HD:
            slope = self.measurements.getRecord('BPISlopeHd', hd, zn)
            const = self.measurements.getRecord('BPIConstHd', hd, zn)
            if testSwitch.FAST_2D_VBAR_XFER_PER_HD_DELTA_BPI:
               bpic1 = slope * target_SFR + const
               bpic2 = slope * TP.TargetSFR_T211_BPIC + const # TP.TargetSFR_T211_BPIC is used as Target SFR of T211 that injects BPI on dictionary
               delta_bpic = bpic1 - bpic2
               bpic = self.measurements.getRecord('BPI', hd, zn) + delta_bpic
            else:
               bpic = slope * target_SFR + const

         else:
            slope = self.measurements.getRecord('BPISlope', hd, zn)
            const = self.measurements.getRecord('BPIConst', hd, zn)
            bpic = slope * target_SFR + const
      else:
         bpic = self.measurements.getRecord('BPI', hd, zn)

      raw_bpic = self.formatScaler.unscaleBPI(hd, zn, bpic)

      if not testSwitch.FAST_2D_VBAR:
         adjBpiForTpi = int(100.0*raw_bpic)+adjustment-100
      else:
         adjBpiForTpi = int(100.0*raw_bpic+adjustment-100.0)
         if target_SFR != 0.0: # make sure the adjust is rounded of to nearest integer
            adjBpiForTpi = int(round(100.0*raw_bpic+adjustment-100.0,0))
         printDbgMsg("Hd %d Zn %d  BPI  %4f  BPIR  %4f  SFR  %4f ADJ_BPI %d" % (hd, zn, bpic, raw_bpic, target_SFR, adjBpiForTpi))
      return adjBpiForTpi

#----------------------------------------------------------------------------------------------------------
   def calculateBestTargetSFR(self, niblet, znLst, meas_2D):

      spcId = self.spcIdHlpr.getSpcId('P_VBAR_2D_SUMMARY')
      self.InitBPINominalTable(debug_output = 0)

      printDbgMsg('Banded TPI 2D')
      printDbgMsg('%s'% (self.header_title))

      tracksPerBand = niblet.settings['TracksPerBand']
      if testSwitch.FAST_2D_VBAR_XFER_PER_HD:
         ADCMatrix = {}
         for hd in range(self.numHeads):
            ADCMatrix[hd] = {}
            ADCMatrix[hd]['BPIC'] = []
            ADCMatrix[hd]['TPIC_S'] = []
            ADCMatrix[hd]['ADC_S'] = []

            for target_index in range(len(TP.Target_SFRs)):
               ADCMatrix[hd]['BPIC'].append(0)
               ADCMatrix[hd]['TPIC_S'].append(0)
               ADCMatrix[hd]['ADC_S'].append(0)

      self.BestTargetSFRIndex_Hd= {}

      for hd in range(self.numHeads):
         for zn in znLst:
            meas = CVbarDataHelper(self.measurements, hd, zn)
            meas_idx = meas_2D[hd,zn]
            MaxEffectiveADC = 0.0
            BestTargetSFRIndex = 0
            for target_index in range(len(TP.Target_SFRs)):

               bpic = self.getBPI_from_Xfer(hd, zn, target_index)
               backoffDS = niblet.settings['WriteFaultThreshold'][zn] - niblet.settings['TPIMeasurementMargin'][zn]
               backoffSS = 2 * niblet.settings['WriteFaultThresholdSlimTrack'][zn] - 2 * niblet.settings['TPIMeasurementMargin'][zn]

               # Special Case for backward compatability
               if tracksPerBand[zn] == 1:
                  tpi_sss = meas_idx['TPI_DSS' + str(target_index)]
                  backoffSS = backoffDS
                  direction = 'IDSS'
                  ShingleDirection = SHINGLE_DIRECTION_OD_TO_ID
                  ReadOffset = 0

               elif meas_idx['TPI_ODSS' + str(target_index)] > meas_idx['TPI_IDSS' + str(target_index)]:
                  tpi_sss = meas_idx['TPI_ODSS' + str(target_index)]
                  direction = 'ODSS'
                  ShingleDirection = SHINGLE_DIRECTION_ID_TO_OD
                  ReadOffset = int(meas_idx['RD_OFST_ODSS' + str(target_index)])

               else:
                  tpi_sss = meas_idx['TPI_IDSS' + str(target_index)]
                  direction = 'IDSS'
                  ShingleDirection = SHINGLE_DIRECTION_OD_TO_ID
                  ReadOffset = int(meas_idx['RD_OFST_IDSS' + str(target_index)])

               # Another Special Case, if single sided capability is less than double sided, set everything to double sided
               if (tpi_sss - backoffSS) <= (meas_idx['TPI_DSS' + str(target_index)] - backoffDS) and (meas_idx['TPI_DSS' + str(target_index)] >= 2):
                  tpi_sss = meas_idx['TPI_DSS' + str(target_index)]
                  backoffSS = backoffDS
                  direction = 'IDSS'
                  ShingleDirection = SHINGLE_DIRECTION_OD_TO_ID
                  ReadOffset = 0

               sp = float(niblet.settings['ShingledProportion'][zn])
               tpb = float(tracksPerBand[zn])
               effectiveTpic = (tpb - TP.TG_Coef)/tpb * sp * (tpi_sss - backoffSS) + ( 1 - sp + sp * TP.TG_Coef/tpb) * (meas_idx['TPI_DSS' + str(target_index)] - backoffDS)
               effectiveADC = bpic * effectiveTpic
               adc_cmr = meas_idx['TPI_DSS' + str(target_index)]* bpic
               adc_smr = tpi_sss * bpic
               #dont include UMP to calculate best SFR
               if testSwitch.FAST_2D_VBAR_XFER_PER_HD and tracksPerBand[zn] > 1:
                  ADCMatrix[hd]['BPIC'][target_index] += bpic
                  ADCMatrix[hd]['TPIC_S'][target_index] += tpi_sss
                  ADCMatrix[hd]['ADC_S'][target_index] += adc_smr


               if (adc_smr - MaxEffectiveADC) > TP.ADC_Saturation and target_index >= TP.Minimum_Target_SFR_Idx:
                  #Populate dictionary if ADC gap is higher than saturation limit
                  if not testSwitch.FAST_2D_VBAR_XFER_PER_HD and not testSwitch.FAST_2D_VBAR_XFER_PER_HD_DELTA_BPI:
                     meas['BPI'] = bpic # Do not override bpi just yet
                  for param in self.param_list:
                     meas[param] = meas_idx[param + str(target_index)]

                  MaxEffectiveADC = adc_smr
                  BestTargetSFRIndex = target_index

               self.dump_zone_data(hd, zn, target_index, direction, tpi_sss, effectiveTpic, effectiveADC, adc_cmr, adc_smr, ReadOffset, meas_idx, bpic)


            #Update Best SFR in Dictionary
            meas['TGT_SFR_IDX'] = BestTargetSFRIndex

      if testSwitch.FAST_2D_VBAR_XFER_PER_HD:
         smr_zones = [ zn for zn in znLst if tracksPerBand[zn] > 1 ]
         try: 1 / len(smr_zones) # to ensure smr_zones length > 0
         except: 
            objMsg.printMsg("All tpb of zones are 1")
            smr_zones = znLst # case all zones are 1 tracks per band
         printDbgMsg('========================')
         printDbgMsg('2D VBAR HEAD SUMMARY')
         if testSwitch.FAST_2D_VBAR_XFER_PER_HD_FILTER:
            printDbgMsg('Hd  TGT_SFR   BPIC   BPIC_F   TPIC_S   TPIC_F    ADC_SMR')
         else:
            printDbgMsg('Hd  TGT_SFR_IDX  BPIC   TPIC_S   ADC_SMR')
         for hd in range(self.numHeads):
            MaxEffectiveADC = 0.0
            BestTargetSFRIndex = 0
            for target_index in range(len(TP.Target_SFRs)):
               ADCMatrix[hd]['BPIC'][target_index] /= len(smr_zones)
               ADCMatrix[hd]['TPIC_S'][target_index] /= len(smr_zones)
               ADCMatrix[hd]['ADC_S'][target_index] /= len(smr_zones)

            if testSwitch.FAST_2D_VBAR_XFER_PER_HD_FILTER:
               ADCMatrix[hd]['BPIC_F'] = self.polyfit(TP.Target_SFRs, ADCMatrix[hd]['BPIC'])
               ADCMatrix[hd]['TPIC_F'] = self.polyfit(TP.Target_SFRs, ADCMatrix[hd]['TPIC_S'])

            for target_index in range(len(TP.Target_SFRs)):
               if testSwitch.FAST_2D_VBAR_XFER_PER_HD_FILTER:
                  adc_smr = ADCMatrix[hd]['BPIC_F'][target_index] * ADCMatrix[hd]['TPIC_F'][target_index]
                  printDbgMsg('%2d     %.4f   %.4f     %.4f     %.4f     %.4f       %.4f' % (hd, TP.Target_SFRs[target_index], ADCMatrix[hd]['BPIC'][target_index], ADCMatrix[hd]['BPIC_F'][target_index], ADCMatrix[hd]['TPIC_S'][target_index], ADCMatrix[hd]['TPIC_F'][target_index], adc_smr))
               else:
                  adc_smr = ADCMatrix[hd]['ADC_S'][target_index]
                  printDbgMsg('%2d        %.4f   %.4f     %.4f       %.4f' % (hd, TP.Target_SFRs[target_index], ADCMatrix[hd]['BPIC'][target_index], ADCMatrix[hd]['TPIC_S'][target_index], adc_smr))

               if (adc_smr - MaxEffectiveADC) > TP.ADC_Saturation and target_index >= TP.Minimum_Target_SFR_Idx:
                  if self.checkMinBpiformat(target_index,hd): #update sova if all even zones meet min bpi format to prevent low bpi fail
                     MaxEffectiveADC = adc_smr
                     BestTargetSFRIndex = target_index

            #Update the dictionary for later usage
            self.BestTargetSFRIndex_Hd[hd] = BestTargetSFRIndex

            #Update the VBAR dicationary of each Zone based on Best Target SFR Index
            for zn in znLst:
               meas = CVbarDataHelper(self.measurements, hd, zn)
               meas_idx = meas_2D[hd,zn]
               if tracksPerBand[zn] == 1 and testSwitch.FAST_2D_VBAR_UMP_FIX_BEST_TARGET_SOVA_BER:
                  BestTargetSFRIndexZn = 0 #bpic update inside handleUMPZones functions to avoid wrong bpic calculation
               else:
                  BestTargetSFRIndexZn = BestTargetSFRIndex
                  meas['BPI'] = self.getBPI_from_Xfer(hd, zn, BestTargetSFRIndexZn)
               meas['TGT_SFR_IDX'] = BestTargetSFRIndexZn
               for param in self.param_list:
                  meas[param] = meas_idx[param + str(BestTargetSFRIndexZn)]
         
         printDbgMsg('===================')

      self.handleUMPZones(znLst, meas_2D, tracksPerBand)

      self.copyTarget_SOVA_2_Unvisited_Zone(znLst, tracksPerBand)

      self.dumpBestSova_AllZones()

      if not testSwitch.CM_REDUCTION_REDUCE_PRINTDBLOGBIN:
         objMsg.printDblogBin(self.dut.dblData.Tables('P_VBAR_2D_SUMMARY'))
         objMsg.printDblogBin(self.dut.dblData.Tables('P_VBAR_2D_BEST_SOVA_BY_ZONES'))

   #-------------------------------------------------------------------------------------------------------
   #dummy for normal mode
   def handleUMPZones(self, znLst, meas_2D, tracksPerBand):
      return

   #-------------------------------------------------------------------------------------------------------
   def dumpBestSova_AllZones(self):
      curSeq, occurrence, testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
      occurrence = 0  # reset the occurrence so we can avoid PK issues.
      debugStr = ""
      debugStr += "Hd  Zn BEST_TGT_SFR BPIC\n"

      for hd in xrange(self.numHeads):
         for zn in xrange(self.numUserZones):
            meas = CVbarDataHelper(self.measurements, hd, zn)
            debugStr += "%2d  %2d        %.2f %.4f \n" % (hd, zn, TP.Target_SFRs[meas['TGT_SFR_IDX']],meas['BPI'])
            dblog_record = {
                     'SPC_ID'          : 1,
                     'OCCURRENCE'      : occurrence,
                     'SEQ'             : curSeq,
                     'TEST_SEQ_EVENT'  : testSeqEvent,
                     'HD_PHYS_PSN'     : self.dut.LgcToPhysHdMap[hd],
                     'DATA_ZONE'       : zn,
                     'HD_LGC_PSN'      : hd,
                     'BEST_SOVA'       : round(TP.Target_SFRs[meas['TGT_SFR_IDX']], 2),
                     'BPIC'            : round(meas['BPI'], 4),
            }
            self.dut.dblData.Tables('P_VBAR_2D_BEST_SOVA_BY_ZONES').addRecord(dblog_record)
      if verbose: objMsg.printMsg("%s" % debugStr)

   #-------------------------------------------------------------------------------------------------------
   def copyTarget_SOVA_2_Unvisited_Zone(self, znLst, tracksPerBand):
      for hd in xrange(self.numHeads):
         for zn in xrange(self.numUserZones):
            if zn in znLst:
               continue
            meas = CVbarDataHelper(self.measurements, hd, zn)
            meas['TGT_SFR_IDX'] = self.measurements.getRecord('TGT_SFR_IDX', hd, zn-1)
            if testSwitch.WA_0256539_480505_SKDC_M10P_BRING_UP_DEBUG_OPTION:
               # Patch setting the BPI of UMP Zones omitted on interlaced setting
               if tracksPerBand[zn] == 1 and testSwitch.FAST_2D_VBAR_INTERLACE and testSwitch.FAST_2D_VBAR_UMP_FIX_BEST_TARGET_SOVA_BER:
                  meas['TGT_SFR_IDX'] = 0 # BestTargetSFRIndexZn = 0 for UMP zones
            # Calculate BPIC for Final Reporting
            meas['BPI'] = self.getBPI_from_Xfer(hd,zn,meas['TGT_SFR_IDX'])

   #-------------------------------------------------------------------------------------------------------
   def polyfit(self, indexList, dataList):

      finalList = []
      finalList.extend(dataList)
      filterList = []
      filterList.extend(dataList)
      N=0
      s1=0
      s2=0
      s3=0
      s4=0
      t1=0
      t2=0
      t3=0
      for index in range(len(dataList)):
         N=N+1
         s1=s1+indexList[index]
         s2=s2+indexList[index]*indexList[index]
         s3=s3+indexList[index]*indexList[index]*indexList[index]
         s4=s4+indexList[index]*indexList[index]*indexList[index]*indexList[index]
         t1=t1+float(filterList[index])
         t2=t2+indexList[index]*float(filterList[index])
         t3=t3+indexList[index]*indexList[index]*float(filterList[index])
      d=N*s2*s4 - N*s3*s3 - s1*s1*s4 - s2*s2*s2 + 2*s1*s2*s3
      A=(N*s2*t3 - N*s3*t2 - s1*s1*t3 - s2*s2*t1 + s1*s2*t2 + s1*s3*t1)/d
      B=(N*s4*t2 - N*s3*t3 - s2*s2*t2 - s1*s4*t1 + s1*s2*t3 + s2*s3*t1)/d
      C=(s1*s3*t3 -s1*s4*t2 -s2*s2*t3 - s3*s3*t1 + s2*s3*t2 + s2*s4*t1)/d
      #apply equation to all values
      for index in range(len(dataList)):
         finalList[index]=A*indexList[index]*indexList[index]+B*indexList[index]+C
      #objMsg.printMsg('finalList2:%s' % finalList)
      return finalList
   #-------------------------------------------------------------------------------------------------------
   def measureTPI_2D(self, znLst):
      meas_2D = {}
      for hd,zn in [(hd, zn) for hd in range(self.numHeads) for zn in znLst]:
         # get the tpiFeedForwardValue
         wp = None
         meas_2D[hd, zn] = {}
         meas = meas_2D[hd, zn]

         if zn == znLst[0]: # temporary rectify until Wp integrated
            tpiFeedForward_DSS = 1.0
            tpiFeedForward_IDSS = 1.0
            tpiFeedForward_ODSS = 1.0

         # do id single sided measurement
         prmOverride = deepcopy(TP.MeasureTPI_211)

         if testSwitch.T211_TURNOFF_REPORT_OPTIONS_DURING_2DVBAR_TPIC_MEAS:
            prmOverride.update({'RESULTS_RETURNED' : 0x000F,})   # DO NOT REPORT DETAILS

         for target_index, target_SFR in enumerate(TP.Target_SFRs):
            #do double sided measurement
            prmOverride.update({'NUM_SQZ_WRITES': TP.num_sqz_writes, 'CWORD2':0})
            if testSwitch.FE_0246199_504159_INJECT_VCM_NOISE:
               prmOverride.update(TP.VCM_ST_PARM['ST_PARM_OFF_VCM'])
            meas['TPI' + str(target_index)], dummyOffset = self.measureTPI(hd,zn,tpiFeedForward_DSS,wp,prm_override=prmOverride,target_SFR=target_SFR)
            meas['TPI' + str(target_index)] = self.formatScaler.scaleTPI(hd,zn,meas['TPI'+ str(target_index)])
            meas['TPI_DSS' + str(target_index)] = meas['TPI' + str(target_index)]

            prmOverride.update({'NUM_SQZ_WRITES':0x8000 + TP.num_sqz_writes, 'CWORD2':8})
            if testSwitch.FE_0246199_504159_INJECT_VCM_NOISE:
               prmOverride.update(TP.VCM_ST_PARM['ST_PARM_ON_VCM'])
            # do id single sided measurement
            meas['TPI_IDSS' + str(target_index)], meas['RD_OFST_IDSS' + str(target_index)] = self.measureTPI(hd,zn,tpiFeedForward_IDSS,wp,prm_override=prmOverride,target_SFR=target_SFR)
            meas['TPI_IDSS' + str(target_index)] = self.formatScaler.scaleTPI(hd,zn,meas['TPI_IDSS'+ str(target_index)])

            # do od single sided measurement
            prmOverride.update({'NUM_SQZ_WRITES':0x4000 + TP.num_sqz_writes,'CWORD2':8})
            meas['TPI_ODSS' + str(target_index)], meas['RD_OFST_ODSS' + str(target_index)] = self.measureTPI(hd,zn,tpiFeedForward_ODSS,wp,prm_override=prmOverride,target_SFR=target_SFR)
            meas['TPI_ODSS' + str(target_index)] = self.formatScaler.scaleTPI(hd,zn,meas['TPI_ODSS' + str(target_index)])

            meas = self.measureSingleSidedTPI_S2D(prmOverride, hd, zn, wp, meas, str(target_index))

            if testSwitch.FAST_2D_VBAR_INTERLACE:
               #copy dictionary to next zone
               meas_2D[hd, zn+1] = {}
               meas_next = meas_2D[hd, zn+1]

               # Copy the dictionary to other zones to make data keys consistent
               meas_next['TPI' + str(target_index)] = meas['TPI' + str(target_index)]
               meas_next['TPI_DSS' + str(target_index)] = meas['TPI_DSS' + str(target_index)]
               meas_next['TPI_IDSS' + str(target_index)] = meas['TPI_IDSS' + str(target_index)]
               meas_next['RD_OFST_IDSS' + str(target_index)] = meas['RD_OFST_IDSS' + str(target_index)]
               meas_next['TPI_ODSS' + str(target_index)] = meas['TPI_ODSS' + str(target_index)]
               meas_next['RD_OFST_ODSS' + str(target_index)] = meas['RD_OFST_ODSS' + str(target_index)]

            # Feed Forward per Target SFR
            if testSwitch.FAST_2D_VBAR_TPI_FF:
               tpiFeedForward_DSS = meas['TPI' + str(target_index)] + 0.02
               tpiFeedForward_IDSS = meas['TPI_IDSS' + str(target_index)] + 0.05
               tpiFeedForward_ODSS = meas['TPI_ODSS' + str(target_index)] + 0.05


         # Feed Forward to Next Zone, Use data of first Target SFR
         if testSwitch.FAST_2D_VBAR_TPI_FF:
            tpiFeedForward_DSS = meas['TPI' + str(0)] + 0.02
            tpiFeedForward_IDSS = meas['TPI_IDSS' + str(0)] + 0.05
            tpiFeedForward_ODSS = meas['TPI_ODSS' + str(0)] + 0.05

      return meas_2D

   #-------------------------------------------------------------------------------------------------------
   def measureTPI_OTCV3(self, znLst, update_zn):
      debug_otc_tpuin = 0
      ## ignore all previous state data ##
      table_OTC = DBLogReader(self.dut, 'P211_TPI_MEASUREMENT3')
      if not testSwitch.virtualRun:
         table_OTC.ignoreExistingData()
      spcid = 20
      
      # Build list
      # TODO: optimize this routine
      otc_dict = {}
      for hd in xrange(self.numHeads):
         for zn in znLst:
            if not otc_dict.has_key((hd,zn)):
               otc_dict[hd,zn] = {}

      # Set up Override Options
      prm_TPI_211_OTC = deepcopy(TP.prm_TPI_211_OTC)
      for col in ['TEST_HEAD', 'ZONE', 'THRESHOLD', 'TARGET_SER']:
         if col in prm_TPI_211_OTC:
            del prm_TPI_211_OTC[col]
            
      # CWORD3 Options
      cword3 = 0x0001         # OTC Measurement Mode
      cword3 |= 0x0020        # use Low Level BER
      cword3 |= 0x0002        # Just measure baseline, no need to iterate squeeze offsets
      cword3 |= 0x0400        # ODSS/IDSS Test
      cword3 |= 0x0800        # Measure baseline OTC
      if testSwitch.OTC_REV_CONTROL: 
         cword3 |= 0x0004     # Faster Test Time
      if testSwitch.FAST_2D_VBAR_TESTTRACK_CONTROL:
         cword3 |= 0x0008     # Test Track Control
      else:
         cword3 &= 0xFFF7     # off the test track control to align test track
         
      prm_TPI_211_OTC.update({
         'CWORD3'                : cword3,
         'NUM_SQZ_WRITES'        : 0x0000 + 1,
         'START_OT_FOR_TPI'      : 0,
         'LIMIT'                 : 150,
         'CWORD2'                : 8,
         'CWORD4'                : 0,
         'spc_id'                : 40,
         'NUM_TRACKS_PER_ZONE'   : 3,
         'RESULTS_RETURNED'      : prm_TPI_211_OTC['RESULTS_RETURNED'] | 0x0008,    # Turn off P211_TPI_INIT / P211_HEADER_INFO
         })
      #prmOverride['ASYMMETRIC_SQZ_WRT_CNT'] = (1000,30) # (Interband DOS, Partial Bro DOS)

      MaskList = self.oUtility.convertListToZoneBankMasks(znLst)
      for bank, list in MaskList.iteritems():
         if list:
            prm_TPI_211_OTC['ZONE_MASK_EXT'], prm_TPI_211_OTC['ZONE_MASK'] = \
               self.oUtility.convertListTo64BitMask(list)
            if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
               prm_TPI_211_OTC['ZONE_MASK_BANK'] = bank
            try:
               CProcess().St(prm_TPI_211_OTC)
            except: 
               pass
            
      # Get Measurement Results
      otc_dict.update(self.otc_get_offsets(table_OTC, debug_otc_tpuin))
         
      for hd in xrange(self.numHeads): 
         for zn in znLst:
            # get the tpiFeedForwardValue
            meas = CVbarDataHelper(self.measurements, hd, zn)
            wp = meas['WP']
            
            # Calculate Read Offsets
            meas['RD_OFST_IDSS'] = otc_dict[hd,zn]['RD_OFST_IDSS']
            meas['RD_OFST_ODSS'] = otc_dict[hd,zn]['RD_OFST_ODSS']
         
      if debug_otc_tpuin:
         curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
         for number_of_writes in [1]: #[1,IntraBand_writes,InterBand_writes]:
            for hd in xrange(self.numHeads): 
               for zn in znLst:
                  dblog_record = {
                     'SPC_ID'          : 1,
                     'OCCURRENCE'      : occurrence,
                     'SEQ'             : curSeq,
                     'TEST_SEQ_EVENT'  : testSeqEvent,
                     'HD_PHYS_PSN'     : self.dut.LgcToPhysHdMap[hd],
                     'DATA_ZONE'       : zn,
                     'HD_LGC_PSN'      : hd,
                     'NUM_WRITE'       : number_of_writes ,
                     'NOSS_N_OFFSET'   : round(otc_dict[hd,zn]['NOSS_N_OTC'], 4),
                     'NOSS_P_OFFSET'   : round(otc_dict[hd,zn]['NOSS_P_OTC'], 4),
                     'IDSS_N_OFFSET'   : round(otc_dict[hd,zn]['IDSS_N_OTC'], 4),
                     'IDSS_P_OFFSET'   : round(otc_dict[hd,zn]['IDSS_P_OTC'], 4),
                     'ODSS_N_OFFSET'   : round(otc_dict[hd,zn]['ODSS_N_OTC'], 4),
                     'ODSS_P_OFFSET'   : round(otc_dict[hd,zn]['ODSS_P_OTC'], 4),
                  }
                  self.dut.dblData.Tables('P_VBAR_OTC_RAW_OFFSET').addRecord(dblog_record)
         objMsg.printDblogBin(self.dut.dblData.Tables('P_VBAR_OTC_RAW_OFFSET'), 1)
      
      # Filter Read Offsets
      self.filterMeasurements('RD_OFST_IDSS', base_zn_list = znLst, Fit_2ndOrder = 0, save_zn_list = update_zn)
      self.filterMeasurements('RD_OFST_ODSS', base_zn_list = znLst, Fit_2ndOrder = 0, save_zn_list = update_zn)
      
      # Calculate Results
      for hd in xrange(self.numHeads): 
         for zn in znLst:
            meas = CVbarDataHelper(self.measurements, hd, zn)
            # Calculate OTC width in Absolute uinch for each Squeeze Type
            otc_dict[hd,zn]['ODSS_OTC'] = otc_dict[hd,zn]['ODSS_P_OTC'] - otc_dict[hd,zn]['ODSS_N_OTC']
            otc_dict[hd,zn]['IDSS_OTC'] = otc_dict[hd,zn]['IDSS_P_OTC'] - otc_dict[hd,zn]['IDSS_N_OTC']
            otc_dict[hd,zn]['NOSS_OTC'] = otc_dict[hd,zn]['NOSS_P_OTC'] - otc_dict[hd,zn]['NOSS_N_OTC']
            
            # Calculate Erase band width in Absolute uinch
            otc_dict[hd,zn]['OD_EF'] = otc_dict[hd,zn]['CUR_TRACK_PITCH'] + otc_dict[hd,zn]['NOSS_N_OTC'] - otc_dict[hd,zn]['IDSS_P_OTC']
            otc_dict[hd,zn]['ID_EF'] = otc_dict[hd,zn]['CUR_TRACK_PITCH'] - otc_dict[hd,zn]['NOSS_P_OTC'] + otc_dict[hd,zn]['ODSS_N_OTC']
            
            # Calculate Intraband TPIC for each squeeze direction
            otc_dict[hd,zn]['TPI_INTRA_ODSSOTC'] = otc_dict[hd,zn]['CUR_TRACK_PITCH'] / (otc_dict[hd,zn]['CUR_TRACK_PITCH'] + (TP.Target_Intra_Track_Pitch - otc_dict[hd,zn]['ODSS_OTC']))
            otc_dict[hd,zn]['TPI_INTRA_IDSSOTC'] = otc_dict[hd,zn]['CUR_TRACK_PITCH'] / (otc_dict[hd,zn]['CUR_TRACK_PITCH'] + (TP.Target_Intra_Track_Pitch - otc_dict[hd,zn]['IDSS_OTC']))
            
            # Calculate Interband TPIC, take worse EB so can cater both shingle direction
            #otc_dict[hd,zn]['TPI_INTER_OTC'] = otc_dict[hd,zn]['CUR_TRACK_PITCH'] / (otc_dict[hd,zn]['NOSS_OTC'] + max(otc_dict[hd,zn]['OD_EF'],otc_dict[hd,zn]['ID_EF']))
            otc_dict[hd,zn]['TPI_INTER_ODSSOTC'] = otc_dict[hd,zn]['CUR_TRACK_PITCH'] / (otc_dict[hd,zn]['CUR_TRACK_PITCH'] + (TP.Target_Inter_Track_Pitch - TP.Target_Intra_Track_Pitch + otc_dict[hd,zn]['NOSS_P_OTC'] - otc_dict[hd,zn]['IDSS_P_OTC']))
            otc_dict[hd,zn]['TPI_INTER_IDSSOTC'] = otc_dict[hd,zn]['CUR_TRACK_PITCH'] / (otc_dict[hd,zn]['CUR_TRACK_PITCH'] + (TP.Target_Inter_Track_Pitch - TP.Target_Intra_Track_Pitch + otc_dict[hd,zn]['ODSS_N_OTC'] - otc_dict[hd,zn]['NOSS_N_OTC']))
            
            # Calculate UMP TPIC, take worse of Double squeze
            otc_dict[hd,zn]['TPI_UMP_OTC'] = otc_dict[hd,zn]['CUR_TRACK_PITCH'] / max(otc_dict[hd,zn]['NOSS_P_OTC'] + otc_dict[hd,zn]['ID_EF'] + TP.Target_UMP_Track_Pitch * 0.5,
                                                  abs(otc_dict[hd,zn]['IDSS_N_OTC'] - otc_dict[hd,zn]['OD_EF'] - TP.Target_UMP_Track_Pitch * 0.5))
            
            if meas['SNGL_DIR'] == 1: # OD to ID
               tpi_otc_intra = otc_dict[hd,zn]['TPI_INTRA_IDSSOTC']
               tpi_otc_inter = otc_dict[hd,zn]['TPI_INTER_IDSSOTC']
               if testSwitch.FE_0293889_348429_VBAR_MARGIN_BY_OTCTP_USE_MULTI_WRITES:
                  tpi_otc_intra = otc_dict[hd,zn]['TPI_INTRA_IDSSOTC_MULTI']
                  tpi_otc_inter = otc_dict[hd,zn]['TPI_INTER_IDSSOTC_MULTI']
            else:
               tpi_otc_intra = otc_dict[hd,zn]['TPI_INTRA_ODSSOTC']
               tpi_otc_inter = otc_dict[hd,zn]['TPI_INTER_ODSSOTC']
               if testSwitch.FE_0293889_348429_VBAR_MARGIN_BY_OTCTP_USE_MULTI_WRITES:
                  tpi_otc_intra = otc_dict[hd,zn]['TPI_INTRA_ODSSOTC_MULTI']
                  tpi_otc_inter = otc_dict[hd,zn]['TPI_INTER_ODSSOTC_MULTI']

            # Update Dictionary
            if tpi_otc_intra < 0.5: # use a predefined margin backoff if OTC can not measure
               meas['TPI_INTRA'] = max(meas['TPI_IDSS'],meas['TPI_ODSS']) - TP.Overide_OTC_Margin
            else:
               meas['TPI_INTRA'] = tpi_otc_intra
            if tpi_otc_inter < 0.5: # use a predefined margin backoff if OTC can not measure
               meas['TPI_INTER'] = meas['TPI'] - TP.Overide_OTC_Margin
            else:
               meas['TPI_INTER'] = tpi_otc_inter
            meas['TPI_UMP'] = otc_dict[hd,zn]['TPI_UMP_OTC']
            meas['TPI_INTRA'] = self.formatScaler.scaleTPI(hd,zn,meas['TPI_INTRA'])
            meas['TPI_INTER'] = self.formatScaler.scaleTPI(hd,zn,meas['TPI_INTER'])
            meas['TPI_UMP'] = self.formatScaler.scaleTPI(hd,zn,meas['TPI_UMP'])
         
      # Filter Final Measurements
      self.filterMeasurements('TPI_INTRA', base_zn_list = znLst, Fit_2ndOrder = 0, save_zn_list = update_zn)
      self.filterMeasurements('TPI_INTER', base_zn_list = znLst, Fit_2ndOrder = 0, save_zn_list = update_zn)
      self.filterMeasurements('TPI_UMP'  , base_zn_list = znLst, Fit_2ndOrder = 0, save_zn_list = update_zn)
      
      #Take care of read offset for all update zones
      for hd in xrange(self.numHeads): 
         for zn in update_zn:
            meas = CVbarDataHelper(self.measurements, hd, zn)
            if meas['SNGL_DIR'] == 1: # OD to ID
               meas['RD_OFST_OTC'] = meas['RD_OFST_IDSS']
            else:
               meas['RD_OFST_OTC'] = meas['RD_OFST_ODSS']
      
      
      curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
      if debug_otc_tpuin:
         objMsg.printMsg('Banded TPI OTCV2')
         objMsg.printMsg('Hd  Zn  BPIC    TPI_DSS  TPI_IDSS TPI_ODSS  DIR   RD_OFST     TPI_INTRA TPI_INTER TPI_UMP   OTC_NOSS  OTC_IDSS  OTC_ODSS  INTRA_IDSS  INTRA_ODSS  ID_EF     OD_EF     CUR_TP    TRG_TP      NOSS_N_OTC  NOSS_P_OTC  ODSS_N_OTC  IDSS_P_OTC')
      for hd in xrange(self.numHeads): 
         for zn in update_zn:
            if self.opMode == 'WpZones':
               wp = self.dut.wrPwrPick[hd][self.objTestZones.getTestZnforZn(zn)]
               meas = self.measurements.getNibletizedRecord(hd, zn, wp)
            else:
               meas = self.measurements.getNibletizedRecord(hd, zn)
               wp = meas['WP']
               
            dblog_record = {
               'SPC_ID'          : spcid,
               'OCCURRENCE'      : occurrence,
               'SEQ'             : curSeq,
               'TEST_SEQ_EVENT'  : testSeqEvent,
               'HD_PHYS_PSN'     : self.dut.LgcToPhysHdMap[hd],
               'DATA_ZONE'       : zn,
               'HD_LGC_PSN'      : hd,
               'BPIC'            : round(meas['BPI'], 4),
               'TPI_DSS'         : round(meas['TPI'], 4),
               'TPI_IDSS'        : round(meas['TPI_IDSS'], 4),
               'TPI_ODSS'        : round(meas['TPI_ODSS'], 4),
               'TPI_INTER'       : round(meas['TPI_INTER'], 4),
               'TPI_INTRA'       : round(meas['TPI_INTRA'], 4),
               'TPI_UMP'         : round(meas['TPI_UMP'], 4),
            }
            if otc_dict.has_key((hd,zn)):
               if debug_otc_tpuin:
                  objMsg.printMsg('%2d  %-3d  %.4f  %.4f   %.4f   %.4f     %-3d      %-4d    %.4f    %.4f    %.4f    %.4f    %.4f    %.4f    %.4f      %.4f      %.4f    %.4f    %.4f    %.4f      %.4f      %.4f      %.4f      %.4f' %
                            (hd, zn, meas['BPI'], meas['TPI'], meas['TPI_IDSS'], meas['TPI_ODSS'], meas['SNGL_DIR'],
                             meas['RD_OFST_OTC'], meas['TPI_INTRA'], meas['TPI_INTER'], meas['TPI_UMP'],
                             otc_dict[hd,zn]['NOSS_OTC'], otc_dict[hd,zn]['IDSS_OTC'], otc_dict[hd,zn]['ODSS_OTC'],
                             otc_dict[hd,zn]['TPI_INTRA_IDSSOTC'], otc_dict[hd,zn]['TPI_INTRA_ODSSOTC'],
                             otc_dict[hd,zn]['ID_EF'], otc_dict[hd,zn]['OD_EF'],
                             otc_dict[hd,zn]['CUR_TRACK_PITCH'], TP.Target_Intra_Track_Pitch,
                             otc_dict[hd,zn]['NOSS_N_OTC'], otc_dict[hd,zn]['NOSS_P_OTC'],
                             otc_dict[hd,zn]['ODSS_N_OTC'], otc_dict[hd,zn]['IDSS_P_OTC'],))
               dblog_record.update(
                  {
                  'INTRA_IDSS'      : round(otc_dict[hd,zn]['TPI_INTRA_IDSSOTC'], 4),
                  'INTRA_ODSS'      : round(otc_dict[hd,zn]['TPI_INTRA_ODSSOTC'], 4),
                  'OTC_NOSS'        : round(otc_dict[hd,zn]['NOSS_OTC'], 4),
                  'OTC_IDSS'        : round(otc_dict[hd,zn]['IDSS_OTC'], 4),
                  'OTC_ODSS'        : round(otc_dict[hd,zn]['ODSS_OTC'], 4),
                  'OD_EF'           : round(otc_dict[hd,zn]['OD_EF'], 4),
                  'ID_EF'           : round(otc_dict[hd,zn]['ID_EF'], 4),
                  'RD_OFFSET'       : meas['RD_OFST_OTC'],
                  'DIR'             : meas['SNGL_DIR'],
                  })
            else:
               if debug_otc_tpuin:
                  objMsg.printMsg('%2d  %-3d  %.4f  %.4f   %.4f   %.4f     %-3d      %-4d    %.4f    %.4f    %.4f' %
                            (hd, zn, meas['BPI'], meas['TPI'], meas['TPI_IDSS'], meas['TPI_ODSS'], meas['SNGL_DIR'],
                             meas['RD_OFST_OTC'], meas['TPI_INTRA'], meas['TPI_INTER'], meas['TPI_UMP'],))
               dblog_record.update(
                  {
                  'INTRA_IDSS'      : -1,
                  'INTRA_ODSS'      : -1,
                  'OTC_NOSS'        : -1,
                  'OTC_IDSS'        : -1,
                  'OTC_ODSS'        : -1,
                  'OD_EF'           : -1,
                  'ID_EF'           : -1,
                  'RD_OFFSET'       : meas['RD_OFST_OTC'],
                  'DIR'             : meas['SNGL_DIR'],
                  })
            self.dut.dblData.Tables('P_VBAR_OTC_SUMMARY2').addRecord(dblog_record)
      if not testSwitch.CM_REDUCTION_REDUCE_PRINTDBLOGBIN:
         objMsg.printDblogBin(self.dut.dblData.Tables('P_VBAR_OTC_SUMMARY2'), spcid)

   #-------------------------------------------------------------------------------------------------------
   def otc_get_offsets(self, table_OTC, debug_otc_tpuin = 0):
      items = ['NOSS_P', 'NOSS_N', 'ODSS_P', 'ODSS_N', 'IDSS_P', 'IDSS_N']
      # param_otc = [item + '_OTC' for item in items]
      param_list = [item + '_OFFSET_LST' for item in items]
      # param_offset = [item + '_OFFSET' for item in items]
      noss_p_ofst = 256
      noss_n_ofst = -256
      otc_dict = {}
      final_otc_dict = {}
      NOSS_BEST_SFR = 1.0
      
      for record in table_OTC.iterRows():
         if debug_otc_tpuin: objMsg.printMsg('OTCV2_DBG:  record %s' % record)
         if float(record.get('OFST_SER')) != -6.5: # get only 6.5 BER
            continue
         if record.get('OTC_INCH') == 'nan':
            printDbgMsg('OTCV2_DBG: Abnormal OTC')
            continue
         # identify Hd/zn
         hd = int(record.get('HD_LGC_PSN'))
         zn = int(record.get('DATA_ZONE'))
         if not otc_dict.has_key((hd, zn)):
            otc_dict[hd, zn] = {}
            for param in param_list:
               otc_dict[hd, zn][param] = []
         # evaluate ktpi
         otc_ktpi = float(record.get('KTPI'))
         otc_dict[hd, zn]['CUR_TRACK_PITCH'] = 1.0/otc_ktpi * 1000.0
         smr_dir = int(record.get('DIR'))
         # Get Squeeze Data
         p_ofset = int(record.get('P_OFST'))
         n_ofset = int(record.get('N_OFST'))
         BEST_SFR = float(record.get('BEST_SFR'))
         if smr_dir == 0:
            # Get No Squeeze Data
            if max(abs(p_ofset),abs(n_ofset)) < 256: # make sure does not exceed
               otc_dict[hd, zn]['NOSS_P_OFFSET_LST'].append(p_ofset)
               otc_dict[hd, zn]['NOSS_N_OFFSET_LST'].append(n_ofset)
               NOSS_BEST_SFR = BEST_SFR
         else:
            if otc_dict[hd, zn]['NOSS_P_OFFSET_LST'] and otc_dict[hd, zn]['NOSS_N_OFFSET_LST']:
               # Evaluate Contigency to handle abnormal results using No squeeze data
               # Contingency #1, if the SFR did not saturate, lets assume worse case
               if BEST_SFR - NOSS_BEST_SFR > 1.0 and NOSS_BEST_SFR != 1.0:
                  printDbgMsg('OTCV2_DBG: Unsaturated Bucket hd/zn %d/%d %4f: ' % (hd, zn, BEST_SFR))
                  if smr_dir == -1 and noss_p_ofst != 256:
                     p_ofset = noss_p_ofst
                     n_ofset = noss_p_ofst
                  elif smr_dir == 1 and noss_n_ofst != -256:
                     p_ofset = noss_n_ofst
                     n_ofset = noss_n_ofst
                  else:
                     continue
               # Contingency #2, if there is strange gap on NOSS, don't add the dictionary
               elif otc_dict[hd,zn]['NOSS_N_OFFSET_LST'] and n_ofset < mean(otc_dict[hd,zn]['NOSS_N_OFFSET_LST']) - 15:
                  printDbgMsg('OTCV2_DBG: NoSqueeze Exceeded NOFSET hd/zn %d/%d %d: ' % (hd, zn, n_ofset))
                  continue
               elif otc_dict[hd,zn]['NOSS_P_OFFSET_LST'] and p_ofset > mean(otc_dict[hd,zn]['NOSS_P_OFFSET_LST']) + 15:
                  printDbgMsg('OTCV2_DBG: NoSqueeze Exceeded POFSET hd/zn %d/%d %d: ' % (hd, zn, p_ofset))
                  continue
               # Contingency 3, if p_ofset < n_ofset or n_ofset > p_ofset, don't add the dictionary
               elif n_ofset >= p_ofset or p_ofset <= n_ofset:
                  printDbgMsg('OTCV2_DBG:  hd/zn %d/%d n_ofset %d p_ofset %d exceed each other: ' % (hd, zn, n_ofset, p_ofset))
                  continue
            else:
               # if no squeeze is empty, use the ODSS/IDSS data
                  if smr_dir == -1:
                     otc_dict[hd, zn]['NOSS_P_OFFSET_LST'].append(p_ofset)
                  elif smr_dir == 1:
                     otc_dict[hd, zn]['NOSS_N_OFFSET_LST'].append(n_ofset)
            # After Checking data, add to the list of offset
            if smr_dir == -1:
               otc_dict[hd,zn]['ODSS_P_OFFSET_LST'].append(p_ofset)
               otc_dict[hd,zn]['ODSS_N_OFFSET_LST'].append(n_ofset)
            elif smr_dir == 1:
               otc_dict[hd,zn]['IDSS_P_OFFSET_LST'].append(p_ofset)
               otc_dict[hd,zn]['IDSS_N_OFFSET_LST'].append(n_ofset)
               
      if debug_otc_tpuin:
         objMsg.printMsg('OTCV2_DBG: otc_dict %s' % otc_dict)
         objMsg.printMsg('OTCV2_DBG:  hd   zn     NOSS_P      NOSS_N      ODSS_P     ODSS_N     IDSS_P     IDSS_N     CUR_TP')
      # Calculate Average Offsets
      for hd, zn in sorted(otc_dict.keys()):
         for param in param_list:
            offset_average = None
            if otc_dict[hd,zn][param]: # if the param offset list is not empty
               # Get the average of each offset
               temp_list = list(otc_dict[hd,zn][param])
               while temp_list:
                  average_offset = mean(temp_list)
                  # Get oelnly data that is within +/-20 offset of the average
                  delta = [abs(item-average_offset) for item in temp_list]
                  max_delta = max(delta)
                  if max_delta < 20: break
                  idx = delta.index(max_delta)
                  printDbgMsg('OTCV2_DBG:  offset out of range %d list: %s' % (temp_list[idx], otc_dict[hd,zn][param]))
                  temp_list = temp_list[:idx]+temp_list[idx+1:]
               offset_average = int(mean(temp_list))
            # Get average of the offset data
            parm2 = param[:-len('_OFFSET_LST')]+'_OFFSET'
            if offset_average:
               otc_dict[hd,zn][parm2] = offset_average
            else: # if empty, assume worse case
               if param in ['NOSS_P_OFFSET_LST']:
                  otc_dict[hd,zn][parm2] = 256.0
               elif param in ['NOSS_N_OFFSET_LST']:
                  otc_dict[hd,zn][parm2] = -256.0
               elif param in ['ODSS_P_OFFSET_LST', 'IDSS_P_OFFSET_LST']:
                  otc_dict[hd,zn][parm2] = otc_dict[hd,zn]['NOSS_P_OFFSET']
               elif param in ['ODSS_N_OFFSET_LST', 'IDSS_N_OFFSET_LST']:
                  otc_dict[hd,zn][parm2] = otc_dict[hd,zn]['NOSS_N_OFFSET']
            
            if not final_otc_dict.has_key((hd,zn)):
               final_otc_dict[hd, zn] = {}
            parm3 = param[:-len('_OFFSET_LST')]+'_OTC'
            final_otc_dict[hd,zn][parm3] = otc_dict[hd,zn][parm2] / 256.0 * otc_dict[hd,zn]['CUR_TRACK_PITCH']
         if debug_otc_tpuin:
            #objMsg.printMsg('OTCV2_DBG:  hd   zn     NOSS_P      NOSS_N      ODSS_P     ODSS_N     IDSS_P     IDSS_N')
            objMsg.printMsg('OTCV2_DBG:  %d   %3d    %7.2f     %7.2f     %7.2f    %7.2f    %7.2f    %7.2f    %7.2f' % (hd,zn,  otc_dict[hd, zn]['NOSS_P_OFFSET']
                                                                                                            , otc_dict[hd, zn]['NOSS_N_OFFSET']
                                                                                                            , otc_dict[hd, zn]['ODSS_P_OFFSET']
                                                                                                            , otc_dict[hd, zn]['ODSS_N_OFFSET']
                                                                                                            , otc_dict[hd, zn]['IDSS_P_OFFSET']
                                                                                                            , otc_dict[hd, zn]['IDSS_N_OFFSET']
                                                                                                            , otc_dict[hd, zn]['CUR_TRACK_PITCH']))
         final_otc_dict[hd,zn]['RD_OFST_IDSS'] = int((otc_dict[hd,zn]['IDSS_P_OFFSET'] + otc_dict[hd,zn]['IDSS_N_OFFSET']) / 2) 
         final_otc_dict[hd,zn]['RD_OFST_ODSS'] = int((otc_dict[hd,zn]['ODSS_P_OFFSET'] + otc_dict[hd,zn]['ODSS_N_OFFSET']) / 2)
         final_otc_dict[hd,zn]['CUR_TRACK_PITCH'] = otc_dict[hd, zn]['CUR_TRACK_PITCH']
      
      del otc_dict
      return final_otc_dict

   #-------------------------------------------------------------------------------------------------------
   def measure_InterbandOTC(self, znLst):
      debug_data = 0
      ## ignore all previous state data ##
      table_OTC = dbLogUtilities.DBLogReader(self.dut, 'P211_TPI_MEASUREMENT3')
      table_OTC.ignoreExistingData()
      
      #znLst = [0,35,75,115,148]
            
      # Set up Test Parameter
      prm_TPI_211_OTC = deepcopy(TP.prm_TPI_211_OTC)
      if 'TEST_HEAD' in prm_TPI_211_OTC:  del prm_TPI_211_OTC['TEST_HEAD']
      if 'ZONE' in prm_TPI_211_OTC:       del prm_TPI_211_OTC['ZONE']
      if 'THRESHOLD' in prm_TPI_211_OTC:  del prm_TPI_211_OTC['THRESHOLD']
      if 'TARGET_SER' in prm_TPI_211_OTC: del prm_TPI_211_OTC['TARGET_SER']
      prm_TPI_211_OTC['ASYMMETRIC_SQZ_WRT_CNT'] = (1, 1) # (Interband DOS, Partial Bro DOS)
      
      if testSwitch.CM_REDUCTION_REDUCE_PRINTMSG:
         prm_TPI_211_OTC['RESULTS_RETURNED'] = prm_TPI_211_OTC['RESULTS_RETURNED'] | 0x0008 # Turn off P211_TPI_INIT / P211_HEADER_INFO
      
      MaskList = self.oUtility.convertListToZoneBankMasks(znLst)
      for bank, list in MaskList.iteritems():
         if list:
            prm_TPI_211_OTC['ZONE_MASK_EXT'], prm_TPI_211_OTC['ZONE_MASK'] = \
               self.oUtility.convertListTo64BitMask(list)
            if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
               prm_TPI_211_OTC['ZONE_MASK_BANK'] = bank
            try:
               CProcess().St(prm_TPI_211_OTC)
            except: pass
            
      curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
      prevzn = -1
      for record in table_OTC.iterRows():
         if float(record.get('OFST_SER')) != -8.0: # get only 8.0 BER
            continue
         #obtain result data
         hd = int(record.get('HD_LGC_PSN'))
         zn = int(record.get('DATA_ZONE'))
         ofset_ser = float(record.get('OFST_SER'))
         otc_uinch = float(record.get('OTC_INCH'))
         test_track = int(record.get('TRK_NUM'))
         dir = int(record.get('DIR'))
         printDbgMsg('OTCV2_DBG:  hd %d zn %d track %d ofset_ser %.4f otc_uinch: %f  dir %d' % (hd, zn, test_track, ofset_ser, otc_uinch, dir))
         
         meas = CVbarDataHelper(self.measurements, hd, zn)
         if prevzn == -1 or prevzn != zn:
            if prevzn != -1:
               printDbgMsg('OTCV2_DBG: Summary Data')
               # if zone shifted, summarize data and add to table
               if len(noss_data): noss = sum(noss_data) / len(noss_data)
               if len(fat_track_data): fat_track = sum(fat_track_data) / len(fat_track_data)
               if len(first_slim_track_data): first_slim_track = sum(first_slim_track_data) / len(first_slim_track_data)
               if len(last_slim_track_data): last_slim_track = sum(last_slim_track_data) / len(last_slim_track_data)
               
               dblog_record = {
                     'SPC_ID'          : 0,
                     'OCCURRENCE'      : occurrence,
                     'SEQ'             : curSeq,
                     'TEST_SEQ_EVENT'  : testSeqEvent,
                     'HD_PHYS_PSN'     : self.dut.LgcToPhysHdMap[hd],
                     'DATA_ZONE'       : zn,
                     'HD_LGC_PSN'      : hd,
                     'OTC_NOSS'        : round(noss, 4),
                     'OTC_FAT'         : round(fat_track, 4),
                     'OTC_FSLIM'       : round(first_slim_track, 4),
                     'OTC_LSLIM'       : round(last_slim_track, 4),
                     'DIR'             : meas['SNGL_DIR'],
                  }
               self.dut.dblData.Tables('P_VBAR_OTC_BAND_SCRN').addRecord(dblog_record)
            # Reset data
            noss_data = []
            fat_track_data = []
            last_slim_track_data = []
            first_slim_track_data = []
            noss = -1.0
            fat_track = -1.0
            first_slim_track = -1.0
            last_slim_track = -1.0
         
         if dir == 0: # baseline no sqz
            fat_track = test_track
            noss_data.append(otc_uinch)
            printDbgMsg('OTCV2_DBG:  Get Fat Track %d  Noss OTC: %f' % (test_track, otc_uinch))
         else:
            if test_track == fat_track: # Fat Track Squeeze data
               fat_track_data.append(otc_uinch)
               printDbgMsg('OTCV2_DBG:  Get Fat Track %d  Sqz OTC: %f' % (test_track, otc_uinch))
            elif meas['SNGL_DIR'] == 1: # OD to ID
               if test_track == fat_track - 1: # last Slim Track data
                  last_slim_track_data.append(otc_uinch)
                  printDbgMsg('OTCV2_DBG:  Get Last Slim Track %d  Sqz OTC: %f' % (test_track, otc_uinch))
               elif fat_track + 1 == test_track: # first Slim Track data
                  first_slim_track_data.append(otc_uinch)
                  printDbgMsg('OTCV2_DBG:  Get First Slim Track %d  Sqz OTC: %f' % (test_track, otc_uinch))
            elif meas['SNGL_DIR'] == -1: # ID to OD
               if fat_track - 1 == test_track: #first Slim Track data
                  first_slim_track_data.append(otc_uinch)
                  printDbgMsg('OTCV2_DBG:  Get First Slim Track %d  Sqz OTC: %f' % (test_track, otc_uinch))
               elif fat_track + 1 == test_track: # last Slim Track data
                  last_slim_track_data.append(otc_uinch)
                  printDbgMsg('OTCV2_DBG:  Get Last Slim Track %d  Sqz OTC: %f' % (test_track, otc_uinch))
                  
         prevzn = zn

      if not testSwitch.CM_REDUCTION_REDUCE_PRINTDBLOGBIN:
         objMsg.printDblogBin(self.dut.dblData.Tables('P_VBAR_OTC_BAND_SCRN'), 0)

   #-------------------------------------------------------------------------------------------------------
   def measureTPI_OTC(self, smr_znLst):
      znLst = range(self.numUserZones)
      if testSwitch.OTC_BUCKET_LINEAR_FIT:
         try:
            tpiMeasIndex = len(self.dut.dblData.Tables('P211_TPI_MEASUREMENT3'))
         except:
            tpiMeasIndex = 0
      if testSwitch.FE_0288274_348429_OTC_MARGIN_MULTIZONE:
         # Consolidate multiple test zones into ST single call
         self.measure_allZoneOTC(smr_znLst, update_TPIOTC = 1)
      else:
         for hd,zn in [(hd, zn) for hd in range(self.numHeads) for zn in smr_znLst]:
            # get the tpiFeedForwardValue
            _wp = self.opMode == 'WpZones' and self.dut.wrPwrPick[hd][self.objTestZones.getTestZnforZn(zn)] or None
            meas = CVbarDataHelper(self.measurements, hd, zn, _wp)
            wp = self.opMode == 'WpZones' and _wp or meas['WP']
   
            tpiFeedForward = meas['TPI'] + .05   # single sided should be easier then double sided
            if zn == 0: # temporary rectify until Wp integrated
               tpiFeedForward_OTC = 1.0
   
            prmOverride = deepcopy(TP.MeasureTPI_211)
            prmOverride.update({
               'LIMIT'                 : 150,   # Open Up coverage for Baseline Measurement
               'CWORD2'                : 8,
               'NUM_TRACKS_PER_ZONE'   : 3,
               })
            # CWORD3 Options
            prmOverride['CWORD3'] = 0x0001 # OTC Measurement Mode
            prmOverride['CWORD3'] = prmOverride['CWORD3'] | 0x0010  # Limit Sweep Range Squeeze Offset 7% as the TMR becomes worse by then
            prmOverride['CWORD3'] = prmOverride['CWORD3'] | 0x0020  # Use OTF BER at 6.5 to define the Bucket
            if testSwitch.OTC_REV_CONTROL: # Faster Test Time
               prmOverride['CWORD3'] = prmOverride['CWORD3'] | 0x0004
            if testSwitch.FAST_2D_VBAR_TESTTRACK_CONTROL:
               prmOverride['CWORD3'] = prmOverride['CWORD3'] | 0x0008 # Test Track Control
            else:
               prmOverride['CWORD3'] = prmOverride['CWORD3'] & 0xFFF7 #temporary off the test track control to align test track
            
            if meas['SNGL_DIR'] == 1:
               # do id single sided measurement
               prmOverride.update({'NUM_SQZ_WRITES':0x8000 + TP.num_sqz_writes, 'CWORD2':8})
            else:
               # do od single sided measurement
               prmOverride.update({'NUM_SQZ_WRITES':0x4000 + TP.num_sqz_writes,'CWORD2':8})
   
            if not testSwitch.VBAR_2D_DEBUG_MODE:
   
               tpi_otc, rd_ofst_otc  = self.measureTPI(hd,zn,tpiFeedForward_OTC,wp,prm_override = prmOverride, mode = "OTC")
            else:
               tpi_otc = 1.1
               rd_ofst_otc = 2.0*(zn-(self.numUserZones/2.0))
               objMsg.printMsg('[211] 2D VBAR OTC FOR %2d  %2d  = %.4f  %.4f##################################################################################' % (hd, zn, tpi_otc, rd_ofst_otc))
   
            objMsg.printMsg('TPI OTC MEASUREMENT Hd %d  Zn %d  TPIOTC %4f' % (hd,zn,tpi_otc))
            if tpi_otc < 0.5: # use a predefined margin backoff if OTC can not measure
               meas['TPI_OTC'] = max(meas['TPI_IDSS'],meas['TPI_ODSS']) - TP.Overide_OTC_Margin
               objMsg.printMsg('TPI OTC MEASUREMENT OVERIDE Hd %d  Zn %d  TPIOTC %4f' % (hd,zn,meas['TPI_OTC']))
            else:
               meas['TPI_OTC'] = tpi_otc
               meas['RD_OFST_OTC'] = rd_ofst_otc
            meas['TPI_OTC'] = self.formatScaler.scaleTPI(hd,zn,meas['TPI_OTC'])
            objMsg.printMsg('SCALED TPI OTC MEASUREMENT Hd %d  Zn %d  TPIOTC %4f' % (hd,zn,meas['TPI_OTC']))
         
      objMsg.printMsg('Banded TPI OTC')
      objMsg.printMsg('Hd  Zn  SQZ_DSS  SQZ_IDSS  SQZ_ODSS  DIR  RD_OFST  SQZ_OTC')
      for hd in xrange(self.numHeads): 
         for zn in znLst:
            _wp = self.opMode == 'WpZones' and self.dut.wrPwrPick[hd][self.objTestZones.getTestZnforZn(zn)] or None
            meas = self.measurements.getNibletizedRecord(hd, zn, _wp)
            objMsg.printMsg('%2d  %-2d  %.4f   %.4f   %.4f     %d      %.4f    %.4f' % (hd,zn,meas['TPI'],meas['TPI_IDSS'],meas['TPI_ODSS'],meas['SNGL_DIR'],meas['RD_OFST_OTC'],meas['TPI_OTC']))
      self.updatedBandedDBLOGTable(spcid = 3)

      # TODO: not optimized due to OTC_BUCKET_LINEAR_FIT is off
      if testSwitch.OTC_BUCKET_LINEAR_FIT:
         OTC_Linear_R = {}
         table4 = self.dut.dblData.Tables('P211_TPI_MEASUREMENT3').tableDataObj()
         for hd in range(self.numHeads):
            OTC_Linear_R[hd] ={}
            # another one for head, use high as it has better repeatability
            Hd_H_OTF_OTC_PCT_List =[]
            Hd_H_OTF_RD_OFST_List =[]
            Hd_H_OTF_SqzList =[]

            for zn in znLst:
               OTC_Linear_R[hd, zn] ={}
               H_OTF_OTC_PCT_List =[]
               H_OTF_RD_OFST_List =[]
               H_OTF_SqzList=[]

               L_OTF_OTC_PCT_List =[]
               L_OTF_RD_OFST_List =[]
               L_OTF_SqzList =[]

               for datarow in range(tpiMeasIndex, len(table4)):
                  if hd == int(table4[datarow]['HD_PHYS_PSN']) and int(table4[datarow]['DIR']) != 0:
                     #dont include UMP zone in head linear regression array
                     if float(table4[datarow]['OFST_SER']) == -6.5 and table4[datarow]['DATA_ZONE'] in smr_znLst:
                        Hd_H_OTF_OTC_PCT_List.append(float(table4[datarow]['OTC_PCT']))
                        Hd_H_OTF_RD_OFST_List.append(float(table4[datarow]['RD_OFST']))
                        Hd_H_OTF_SqzList.append(float(table4[datarow]['SQZ_PCT']))

                     if zn == int(table4[datarow]['DATA_ZONE']):
                        if int(table4[datarow]['DIR']) == 1: # For KTPI , move to next track to ensure slim track calculation
                           OTC_Linear_R[hd, zn]['TRACK'] = int(table4[datarow]['TRK_NUM']) + 1
                        else:
                           OTC_Linear_R[hd, zn]['TRACK'] = int(table4[datarow]['TRK_NUM'])
                        if float(table4[datarow]['OFST_SER']) == -6.5:
                           H_OTF_OTC_PCT_List.append(float(table4[datarow]['OTC_PCT']))
                           H_OTF_RD_OFST_List.append(float(table4[datarow]['RD_OFST']))
                           H_OTF_SqzList.append(float(table4[datarow]['SQZ_PCT']))
                        else:
                           L_OTF_OTC_PCT_List.append(float(table4[datarow]['OTC_PCT']))
                           L_OTF_RD_OFST_List.append(float(table4[datarow]['RD_OFST']))
                           L_OTF_SqzList.append(float(table4[datarow]['SQZ_PCT']))

               objMsg.printMsg('H_OTF_OTC_PCT_List Hd%d Zn%d %s' % (hd,zn,H_OTF_OTC_PCT_List))
               #objMsg.printMsg('H_OTF_RD_OFST_List %s' % H_OTF_RD_OFST_List)
               objMsg.printMsg('H_OTF_SqzList Hd%d Zn%d  %s' % (hd,zn,H_OTF_SqzList))
               #objMsg.printMsg('L_OTF_OTC_PCT_List %s' % L_OTF_OTC_PCT_List)
               #objMsg.printMsg('L_OTF_RD_OFST_List %s' % L_OTF_RD_OFST_List)
               #objMsg.printMsg('L_OTF_SqzList %s' % L_OTF_SqzList)

               if len(H_OTF_OTC_PCT_List) > 1:
                  OTC_Linear_R[hd, zn]['H_OTCSlope'], OTC_Linear_R[hd, zn]['H_OTCIntrcpt'], OTC_Linear_R[hd, zn]['H_OTCRsq'] = linreg(H_OTF_SqzList,H_OTF_OTC_PCT_List)
                  OTC_Linear_R[hd, zn]['H_RdOfstSlope'], OTC_Linear_R[hd, zn]['H_RdOfstIntrcpt'], OTC_Linear_R[hd, zn]['H_RdOfstRsq'] = linreg(H_OTF_SqzList,H_OTF_RD_OFST_List)
                  OTC_Linear_R[hd, zn]['L_OTCSlope'], OTC_Linear_R[hd, zn]['L_OTCIntrcpt'], OTC_Linear_R[hd, zn]['L_OTCRsq'] = linreg(L_OTF_SqzList,L_OTF_OTC_PCT_List)
                  OTC_Linear_R[hd, zn]['L_RdOfstSlope'], OTC_Linear_R[hd, zn]['L_RdOfstIntrcpt'], OTC_Linear_R[hd, zn]['L_RdOfstRsq'] = linreg(L_OTF_SqzList,L_OTF_RD_OFST_List)
               else:
                  OTC_Linear_R[hd, zn]['H_OTCSlope'], OTC_Linear_R[hd, zn]['H_OTCIntrcpt'], OTC_Linear_R[hd, zn]['H_OTCRsq'] = 1,0,0
                  OTC_Linear_R[hd, zn]['H_RdOfstSlope'], OTC_Linear_R[hd, zn]['H_RdOfstIntrcpt'], OTC_Linear_R[hd, zn]['H_RdOfstRsq'] = 1,0,0
                  OTC_Linear_R[hd, zn]['L_OTCSlope'], OTC_Linear_R[hd, zn]['L_OTCIntrcpt'], OTC_Linear_R[hd, zn]['L_OTCRsq'] = 1,0,0
                  OTC_Linear_R[hd, zn]['L_RdOfstSlope'], OTC_Linear_R[hd, zn]['L_RdOfstIntrcpt'], OTC_Linear_R[hd, zn]['L_RdOfstRsq'] = 1,0,0

            # Summary for Head
            OTC_Linear_R[hd]['H_OTCSlope'], OTC_Linear_R[hd]['H_OTCIntrcpt'], OTC_Linear_R[hd]['H_OTCRsq'] = linreg(Hd_H_OTF_SqzList,Hd_H_OTF_OTC_PCT_List)
            OTC_Linear_R[hd]['H_RdOfstSlope'], OTC_Linear_R[hd]['H_RdOfstIntrcpt'], OTC_Linear_R[hd]['H_RdOfstRsq'] = linreg(Hd_H_OTF_SqzList,Hd_H_OTF_RD_OFST_List)

         # Do one more round check
         objMsg.printMsg('OTC Fitting Data Head')
         objMsg.printMsg('OTC_FIT: Hd  H_OTC_S  H_OTC_I  H_OTC_RSQ  H_OFS_S  H_OFS_I  H_OFS_RSQ')
         for hd in range(self.numHeads):
            objMsg.printMsg('OTC_FIT: %2d  %.4f   %.4f   %.4f   %.4f   %.4f   %.4f ' % (hd,OTC_Linear_R[hd]['H_OTCSlope'],OTC_Linear_R[hd]['H_OTCIntrcpt'],OTC_Linear_R[hd]['H_OTCRsq']
                                                                                          ,OTC_Linear_R[hd]['H_RdOfstSlope'],OTC_Linear_R[hd]['H_RdOfstIntrcpt'],OTC_Linear_R[hd]['H_RdOfstRsq']))
         for hd in range(self.numHeads):
            for zn in znLst:
               if OTC_Linear_R[hd, zn]['H_OTCRsq'] < 0.6 or OTC_Linear_R[hd, zn]['H_OTCSlope'] == 0: # Override the slope with head overall slope
                  objMsg.printMsg('poor Rsq Replace: Hd %d Zn %d OTC Rsq %.4f OTCSlope %.4f' % (hd,zn,OTC_Linear_R[hd, zn]['H_OTCRsq'],OTC_Linear_R[hd, zn]['H_OTCSlope']))
                  OTC_Linear_R[hd, zn]['H_OTCSlope'] = OTC_Linear_R[hd]['H_OTCSlope']
                  OTC_Linear_R[hd, zn]['H_RdOfstSlope'] = OTC_Linear_R[hd]['H_RdOfstSlope']
                  if OTC_Linear_R[hd, zn]['H_OTCSlope'] == 0:
                     OTC_Linear_R[hd, zn]['H_OTCIntrcpt'] == OTC_Linear_R[hd]['H_OTCIntrcpt']

         objMsg.printMsg('OTC Fitting Data Zone')
         objMsg.printMsg('OTC_FIT: Hd  Zn  H_OTC_S  H_OTC_I  H_OTC_RSQ   L_OTC_S  L_OTC_I  L_OTC_RSQ  H_OFS_S  H_OFS_I  H_OFS_RSQ   L_OFS_S  L_OFS_I  L_OFS_RSQ')
         for hd in xrange(self.numHeads):
            for zn in znLst:
               objMsg.printMsg('OTC_FIT: %2d  %-2d  %.4f   %.4f   %.4f   %.4f   %.4f   %.4f   %.4f   %.4f   %.4f   %.4f   %.4f   %.4f' % \
               (hd,zn,OTC_Linear_R[hd, zn]['H_OTCSlope'],OTC_Linear_R[hd, zn]['H_OTCIntrcpt'],OTC_Linear_R[hd, zn]['H_OTCRsq'],\
               OTC_Linear_R[hd, zn]['L_OTCSlope'],OTC_Linear_R[hd, zn]['L_OTCIntrcpt'],OTC_Linear_R[hd, zn]['L_OTCRsq'],\
               OTC_Linear_R[hd, zn]['H_RdOfstSlope'],OTC_Linear_R[hd, zn]['H_RdOfstIntrcpt'],OTC_Linear_R[hd, zn]['H_RdOfstRsq'],\
               OTC_Linear_R[hd, zn]['L_RdOfstSlope'],OTC_Linear_R[hd, zn]['L_RdOfstIntrcpt'],OTC_Linear_R[hd, zn]['L_RdOfstRsq']))
         for hd in xrange(self.numHeads):
            for zn in znLst:
               _wp = self.opMode == 'WpZones' and self.dut.wrPwrPick[hd][self.objTestZones.getTestZnforZn(zn)] or None
               meas = CVbarDataHelper(self.measurements, hd, zn, _wp)

               if OTC_Linear_R[hd, zn]['H_OTCRsq'] > 0 and OTC_Linear_R[hd, zn]['H_OTCSlope'] != 0:
                  #if OTC_Linear_R[hd, zn]['H_OTCRsq'] > OTC_Linear_R[hd, zn]['L_OTCRsq']:
                  meas['TPI_OTC'] = 1 / (1 - ((TP.Target_OTC_Bucket - OTC_Linear_R[hd, zn]['H_OTCIntrcpt']) / OTC_Linear_R[hd, zn]['H_OTCSlope']))
                  #else:
                  #   meas['TPI_OTC'] = 1 / (1- ((0.25 - OTC_Linear_R[hd, zn]['L_OTCIntrcpt'])  / OTC_Linear_R[hd, zn]['L_OTCSlope']))
                  #if OTC_Linear_R[hd, zn]['H_RdOfstRsq'] > OTC_Linear_R[hd, zn]['L_RdOfstRsq']:
                  #meas['RD_OFST_OTC'] = (0.25 -OTC_Linear_R[hd, zn]['H_RdOfstIntrcpt']) /  OTC_Linear_R[hd, zn]['H_RdOfstSlope']
                  #else:
                  #   meas['RD_OFST_OTC'] = (0.25 * OTC_Linear_R[hd, zn]['L_RdOfstIntrcpt']) / OTC_Linear_R[hd, zn]['L_RdOfstSlope']

                  objMsg.printMsg('TPI OTC MEASUREMENT Hd %d  Zn %d  TPIOTC %4f' % (hd,zn,meas['TPI_OTC']))
                  meas['TPI_OTC'] = self.formatScaler.scaleTPI(hd,zn,meas['TPI_OTC'])
                  objMsg.printMsg('SCALED TPI OTC MEASUREMENT Hd %d  Zn %d  TPIOTC %4f' % (hd,zn,meas['TPI_OTC']))

         objMsg.printMsg('Banded TPI OTC Fitted')
         objMsg.printMsg('Hd  Zn  SQZ_DSS  SQZ_IDSS  SQZ_ODSS  DIR  RD_OFST  SQZ_OTC')
         for hd in xrange(self.numHeads):
            for zn in znLst:
               _wp = self.opMode == 'WpZones' and self.dut.wrPwrPick[hd][self.objTestZones.getTestZnforZn(zn)] or None
               meas = CVbarDataHelper(self.measurements, hd, zn, _wp)
               objMsg.printMsg('%2d  %-2d  %.4f   %.4f   %.4f     %d      %.4f    %.4f' % (hd,zn,meas['TPI'],meas['TPI_IDSS'],meas['TPI_ODSS'],meas['SNGL_DIR'],meas['RD_OFST_OTC'],meas['TPI_OTC']))

         if testSwitch.OTC_BUCKET_ZONE_POLYFITTED:
            for hd in xrange(self.numHeads):
               TPI_OTC_list = []
               objMsg.printMsg("ccyy SMR ZONES: %s" % str(smr_znLst))
               for zn in znLst:
                  _wp = self.opMode == 'WpZones' and self.dut.wrPwrPick[hd][self.objTestZones.getTestZnforZn(zn)] or None
                  meas = CVbarDataHelper(self.measurements, hd, zn, _wp)
                  TPI_OTC_list.append(meas['TPI_OTC'])
               TPI_OTC_list = self.polyfit(smr_znLst, TPI_OTC_list)
               for index in len(smr_znLst):
                  _wp = self.opMode == 'WpZones' and self.dut.wrPwrPick[hd][self.objTestZones.getTestZnforZn(smr_znLst[index])] or None
                  meas = CVbarDataHelper(self.measurements, hd, zn, _wp)
                  meas['TPI_OTC'] = TPI_OTC_list[index]

            objMsg.printMsg('Banded TPI OTC Zone Fitted')
            objMsg.printMsg('Hd  Zn  SQZ_DSS  SQZ_IDSS  SQZ_ODSS  DIR  RD_OFST  SQZ_OTC')
            for hd in xrange(self.numHeads):
               for zn in znLst:
                  _wp = self.opMode == 'WpZones' and self.dut.wrPwrPick[hd][self.objTestZones.getTestZnforZn(zn)] or None
                  meas = CVbarDataHelper(self.measurements, hd, zn, _wp)
                  objMsg.printMsg('%2d  %-2d  %.4f   %.4f   %.4f     %d      %.4f    %.4f' % (hd,zn,meas['TPI'],meas['TPI_IDSS'],meas['TPI_ODSS'],meas['SNGL_DIR'],meas['RD_OFST_OTC'],meas['TPI_OTC']))

   #-------------------------------------------------------------------------------------------------------
   def updatedBandedDBLOGTable(self, spcid = 1):
      curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
      for hd in xrange(self.numHeads): 
         for zn in xrange(self.numUserZones):
            meas = CVbarDataHelper(self.measurements, hd, zn)
            dblog_record = {
               'SPC_ID'          : spcid,
               'OCCURRENCE'      : occurrence,
               'SEQ'             : curSeq,
               'TEST_SEQ_EVENT'  : testSeqEvent,
               'HD_PHYS_PSN'     : self.dut.LgcToPhysHdMap[hd],
               'DATA_ZONE'       : zn,
               'HD_LGC_PSN'      : hd,
               'BPIC'            : round(meas['BPI'], 4),
               'TPI_DSS'         : round(meas['TPI'], 4),
               'TPI_IDSS'        : round(meas['TPI_IDSS'], 4),
               'TPI_ODSS'        : round(meas['TPI_ODSS'], 4),
               'TPI_EFF'         : -1,
               'TPI_MAX'         : round(meas['TPI_OTC'], 4),
               'RD_OFFSET'       : meas['RD_OFST_OTC'],
               'DIR'             : meas['SNGL_DIR'],
            }
            self.dut.dblData.Tables('P_VBAR_BANDED_FORMAT_SUMMARY').addRecord(dblog_record)
      objMsg.printDblogBin(self.dut.dblData.Tables('P_VBAR_BANDED_FORMAT_SUMMARY'), spcid)

   #-------------------------------------------------------------------------------------------------------
   def measureSingleSidedTPI(self, znLst, znLst_skip_tpi_sss = []):
      if testSwitch.extern.FE_0285939_504159_P_PASS_ADJ_BPI_FOR_TPI_BY_SIM:
         from RdWr import CAdjBpiFile
         #update adjustment of bpi for tpi measurement inside SIM only once
         oCAdjBpiFile = CAdjBpiFile()
         ar = [ self.calcBPIBackoff(hd, zn, 0) for hd, zn in [(hd, zn) for hd in range(self.numHeads) for zn in range(self.numUserZones)] ]
         tmp_Array = array('h', ar)
         oCAdjBpiFile.arrayToFile(tmp_Array)
         oCAdjBpiFile.fileToDisc()
         table_TpiCap = DBLogReader(self.dut, 'P211_TPI_CAP_AVG')
         table_TpiCap.ignoreExistingData()
         if testSwitch.T211_MERGE_READ_OFFSET_TBL_INTO_TPI_MEAS_TBL:
            table_RdOfst = table_TpiCap 
         else:
            table_RdOfst = DBLogReader(self.dut, 'P211_RD_OFST_AVG')
            table_RdOfst.ignoreExistingData()

         tpi_meas_ar = {'TPI' : {'NUM_SQZ_WRITES': TP.num_sqz_writes, 'CWORD2':0},
                        'TPI_IDSS': {'NUM_SQZ_WRITES':0x8000 + TP.num_sqz_writes, 'CWORD2':8},
                        'TPI_ODSS': {'NUM_SQZ_WRITES':0x4000 + TP.num_sqz_writes,'CWORD2':8},
         }
         for tpic_meas in tpi_meas_ar:
            test_zone = deepcopy(znLst)
            if tpic_meas != 'TPI': 
               test_zone = list(set(test_zone)- set(znLst_skip_tpi_sss))
            prm_TPI_211 = {'test_num'           : 211,
                           'prm_name'           : 'MeasureTPI_211',
                           'NUM_TRACKS_PER_ZONE': 6,
                           'NUM_SQZ_WRITES'     : TP.num_sqz_writes,
                           'ZONE_POSITION'      : TP.VBAR_ZONE_POS,
                           'CWORD1'             : 0x0026,   #Enable multi-track mode
                           'CWORD2'             : 0x0000,
                           'SET_OCLIM'          : 655,
                           'TPI_TARGET_SER'     : 5,
                           'RESULTS_RETURNED'   : 0x0000,
                           'timeout'            : 3600*len(test_zone)*self.numHeads,
                           'spc_id'             : 0,
                           'HEAD_RANGE'         : sum([1 << hd for hd in range(self.numHeads)]),
                           'CWORD6'             : 0x2, #turn on get adj bpi from file
            }
            prm_TPI_211.update(tpi_meas_ar[tpic_meas]) #update cword2 for different tpic meas
            prm_TPI_211.update(TP.MeasureTPI_211) #update the threshold of tpic meas
            # if the write powers have already been selected, do the measurements at nominal clearance
            if self.opMode == 'AllZones': prm_TPI_211['CWORD1'] &= 0xFFAF
            # currently off first for debugging
            #if testSwitch.T211_TURNOFF_REPORT_OPTIONS_DURING_2DVBAR_TPIC_MEAS:
            #   prm_TPI_211.update({'RESULTS_RETURNED' : 0x000F,})   # DO NOT REPORT DETAILS
            MaskList = self.oUtility.convertListToZoneBankMasks(test_zone)
            for bank, list_zone in MaskList.iteritems():
               if list_zone:
                  prm_TPI_211['ZONE_MASK_EXT'], prm_TPI_211['ZONE_MASK'] = \
                     self.oUtility.convertListTo64BitMask(list_zone)
                  if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
                     prm_TPI_211['ZONE_MASK_BANK'] = bank
                  getVbarGlobalClass(CProcess).St(prm_TPI_211)
                  #process data
                  for record in table_TpiCap.iterRows():
                     hd = int(record.get('HD_LGC_PSN'))
                     zn = int(record.get('DATA_ZONE'))
                     meas = CVbarDataHelper(self.measurements, hd, zn)
                     meas[tpic_meas] = self.formatScaler.scaleTPI(hd, zn, float(record.get('TPI_CAP_AVG', 0.0)))
                     if testSwitch.SMR and tpic_meas != 'TPI':  
                        meas["RD_OFST_" +(tpic_meas.split('_')[1])] = \
                           int(table_RdOfst.findRow({'HD_LGC_PSN':hd, 'DATA_ZONE':zn}).get('RD_OFST_AVG', 0))
         return
      #else path
      # if passing adjustment bpi for tpi measurement by sim is off
      for hd in xrange(self.numHeads): 
         for zn in znLst:
            # get the tpiFeedForwardValue
            _wp = self.opMode == 'WpZones' and self.dut.wrPwrPick[hd][self.objTestZones.getTestZnforZn(zn)] or None
            meas = CVbarDataHelper(self.measurements, hd, zn, _wp)
            wp = self.opMode == 'WpZones' and _wp or meas['WP']

            tpiFeedForward = meas['TPI'] + .05   # single sided should be easier then double sided

            if testSwitch.FAST_2D_VBAR:
               prmOverride = deepcopy(TP.MeasureTPI_211)
                  
               if zn == znLst[0]: # temporary rectify until Wp integrated
                  tpiFeedForward_DSS = 1.0
                  tpiFeedForward_IDSS = 1.0
                  tpiFeedForward_ODSS = 1.0

               if testSwitch.T211_TURNOFF_REPORT_OPTIONS_DURING_2DVBAR_TPIC_MEAS:
                  prmOverride.update({'RESULTS_RETURNED' : 0x000F,})   # DO NOT REPORT DETAILS
               
               #do double sided measurement
               prmOverride.update({'NUM_SQZ_WRITES': TP.num_sqz_writes, 'CWORD2':0})
               meas['TPI'], dummyOffset = self.measureTPI(hd,zn,tpiFeedForward_DSS,wp,prm_override = prmOverride)
               meas['TPI'] = self.formatScaler.scaleTPI(hd,zn,meas['TPI'])

               if zn not in znLst_skip_tpi_sss:
                  if testSwitch.FE_0246199_504159_INJECT_VCM_NOISE:
                     prmOverride.update(TP.VCM_ST_PARM['ST_PARM_ON_VCM'])
                  prmOverride.update({'NUM_SQZ_WRITES':0x8000 + TP.num_sqz_writes, 'CWORD2':8})
                  # do id single sided measurement
                  meas['TPI_IDSS'], meas['RD_OFST_IDSS'] = self.measureTPI(hd,zn,tpiFeedForward_IDSS,wp,prm_override = prmOverride)
                  meas['TPI_IDSS'] = self.formatScaler.scaleTPI(hd,zn,meas['TPI_IDSS'])
      
                  # do od single sided measurement
                  prmOverride.update({'NUM_SQZ_WRITES':0x4000 + TP.num_sqz_writes,'CWORD2':8})
                  meas['TPI_ODSS'], meas['RD_OFST_ODSS'] = self.measureTPI(hd,zn,tpiFeedForward_ODSS,wp,prm_override = prmOverride)
                  meas['TPI_ODSS'] = self.formatScaler.scaleTPI(hd,zn,meas['TPI_ODSS'])

               meas = self.measureSingleSidedTPI_S2D(prmOverride, hd, zn, wp, meas)
            else:
               # do id single sided measurement
               prmOverride = TP.MeasureTPI_211.copy()
               prmOverride.update({'NUM_SQZ_WRITES':0x8000 + TP.num_sqz_writes, 'CWORD2':8})
               meas['TPI_IDSS'], meas['RD_OFST_IDSS'] = self.measureTPI(hd,zn,tpiFeedForward,wp,prm_override = prmOverride)
               meas['TPI_IDSS'] = self.formatScaler.scaleTPI(hd,zn,meas['TPI_IDSS'])

               # do od single sided measurement
               prmOverride.update({'NUM_SQZ_WRITES':0x4000 + TP.num_sqz_writes ,'CWORD2':8})
               meas['TPI_ODSS'], meas['RD_OFST_ODSS'] = self.measureTPI(hd,zn,tpiFeedForward,wp,prm_override = prmOverride)
               meas['TPI_ODSS'] = self.formatScaler.scaleTPI(hd,zn,meas['TPI_ODSS'])

   #-------------------------------------------------------------------------------------------------------
   def Process_TPINOMINAL(self, znlist, dss_only ):
      if dss_only:
         param_list = ['TPI']
      else:
         param_list = ['TPI','TPI_IDSS','TPI_ODSS']
         
      average_param = {}
      
      for hd in xrange(self.numHeads):
         for param in param_list :
            meas_rec = []
            for zn in znlist:
               meas_rec.append(self.measurements.getRecord(param, hd, zn))
               
            if verbose == 1:
               objMsg.printMsg('List %s %s' % (param, meas_rec))
               
            average_param[param] = float(sum(meas_rec) - max(meas_rec) - min(meas_rec)) / (len(meas_rec) - 2)

         # update dictionary
         for zn in xrange(self.numUserZones):
            for param in param_list :
               self.measurements.setRecord(param, average_param[param], hd, zn)
               
         if dss_only:
            objMsg.printMsg('TPINOMINAL_DBG Hd: %d MEAN TPI_DSS: %3.4f' % (hd, average_param['TPI']))
         else:
            objMsg.printMsg('TPINOMINAL_DBG Hd: %d MEAN TPI_DSS: %3.4f  TPI_IDSS: %3.4f  TPI_ODSS: %3.4f' % (hd, average_param['TPI'], average_param['TPI_IDSS'], average_param['TPI_ODSS']))
         
   #-------------------------------------------------------------------------------------------------------
   def InitBPINominalTable(self, debug_output = 0):
      self.numUserZones = self.bpiFile.getNumUserZones()
      nominalFormat = self.bpiFile.getNominalFormat()
      maxBpiProfiles = self.bpiFile.getNumBpiProfiles()
      BPIMinFormat = self.bpiFile.getMinFormat()
      BPIMaxFormat = self.bpiFile.getMaxFormat()
      self.BPINominal_Table = list(list(list() for pf in xrange(maxBpiProfiles)) for hd in xrange(self.bpiFile.bpiNumHeads))

      if debug_output:
         objMsg.printMsg('nominalFormat:%s' % (nominalFormat))
         objMsg.printMsg('maxBpiProfiles:%s' % (maxBpiProfiles))
         objMsg.printMsg('MinFormat:%s' % (BPIMinFormat))
         objMsg.printMsg('MaxFormat:%s' % (BPIMaxFormat))
         objMsg.printMsg('self.numHeads:%d' % (self.numHeads))

      # Calculate and fill-in 'BPINominal_Table' table with format freq ratios.
      if debug_output:
         objMsg.printMsg('-- Displaying BPINominal_Table --')
         tmpstr1 = '\nBPI_CFG'
         for zn in xrange(numUserZones): 
            tmpstr1 += str("    Zn%2d" % (zn))
         tmpstr2 = ''
      for hd in xrange(self.bpiFile.bpiNumHeads):
         for idx, pf in enumerate(xrange(BPIMinFormat,BPIMaxFormat+1)):
            if debug_output:
               tmpstr2 += str('\n "%2d" :(' % (idx))
            for zn in xrange(self.numUserZones):  # Including sys_zone
               nominalFrequency = self.bpiFile.getFrequencyByFormatAndZone(0,zn,hd)   # TODO: optimize this routine?
               ZnFormatFreq = self.bpiFile.getFrequencyByFormatAndZone(pf,zn,hd)
               FreqRatio = ZnFormatFreq/nominalFrequency
               self.BPINominal_Table[hd][idx].append(FreqRatio)
               if debug_output:
                  tmpstr2 += str(' %.4f,' % (FreqRatio))
            if debug_output:
               tmpstr2 += '),'
         if debug_output:
            tmpstr2 += '\n'
      if debug_output:
         objMsg.printMsg('%s%s' % (tmpstr1, tmpstr2))

   #-------------------------------------------------------------------------------------------------------
   def getBPI_from_Xfer(self, hd, zn, tgt_index):
      meas = CVbarDataHelper(self.measurements, hd, zn)
      if testSwitch.FAST_2D_VBAR_XFER_PER_HD:
         if testSwitch.FAST_2D_VBAR_XFER_PER_HD_DELTA_BPI:
            bpic1 = meas['BPISlopeHd'] * TP.Target_SFRs[tgt_index] + meas['BPIConstHd']
            bpic2 = meas['BPISlopeHd'] * TP.TargetSFR_T211_BPIC + meas['BPIConstHd'] # TP.TargetSFR_T211_BPIC is used as Target SFR of T211 that injects BPI on dictionary
            delta_bpic = bpic1 - bpic2
            bpic = meas['BPI'] + delta_bpic
         else:
            bpic = meas['BPISlopeHd'] * TP.Target_SFRs[tgt_index] + meas['BPIConstHd']
      else:
         bpic = meas['BPISlope'] * TP.Target_SFRs[tgt_index] + meas['BPIConst']

      return bpic

   #-------------------------------------------------------------------------------------------------------
   def checkMinBpiformat(self, target_index, hd = 0):
      if target_index == TP.Minimum_Target_SFR_Idx: #minimum sova can be pick
         return True
      for zn in xrange(self.numUserZones):
         bpic_zn = self.getBPI_from_Xfer(hd, zn, target_index)
         bpi_format = self.BPINominal_Table[getBpiHeadIndex(hd)][0][zn]

         if bpic_zn < bpi_format: #bpic less than bpi format
            objMsg.printMsg('target sfr not met %f, hd %d, zn %d, bpic %f, bpi_min %f' \
               % (TP.Target_SFRs[target_index], hd, zn, bpic_zn, bpi_format) )
            return False
      return True

   #-------------------------------------------------------------------------------------------------------
   def Reset_Read_offset(self):
      prm_210 = {'test_num': 210,
                 'prm_name': 'Reset_Read_Offset',
                 'timeout' : 1800,
                 #'dlfile'  : (CN, self.bpiFile.bpiFileName),
                 'spc_id'  : 0,
                 'CWORD2'  : 0x0080,
                 'CWORD1'  : 0x0102,
                 'MICROJOG_SQUEEZE'  : [0,]*T210_PARM_NUM_HEADS,
      }
      if not testSwitch.FE_0269922_348085_P_SIGMUND_IN_FACTORY:
         prm_210.update({
                 'dlfile'   : (CN,self.bpiFile.bpiFileName),
                 })
      getVbarGlobalClass(CProcess).St(prm_210)

      # Write RAP and SAP data to flash
      getVbarGlobalClass(CProcess).St({'test_num': 178, 'prm_name': 'Save RAP and SAP to Flash', 'CWORD1':0x0620, 'timeout': 1200, 'spc_id': 0,})

   #-------------------------------------------------------------------------------------------------------
   def __adjustTGTCLR(self):
      # TODO: test
      self.TgtClrData = {}
      for head in range(self.numHeads):
         self.TgtClrData[head] = {}
         for zone in xrange(self.numUserZones):
            self.TgtClrData[head][zone] = {}

      try:
         colDict = self.dut.dblData.Tables('P172_AFH_DH_CLEARANCE').columnNameDict()
         TgtClrDataTable = self.dut.dblData.Tables('P172_AFH_DH_CLEARANCE').rowListIter()
      except:
         try:
            colDict = self.dut.dblData.Tables('P172_AFH_CLEARANCE').columnNameDict()
            TgtClrDataTable = self.dut.dblData.Tables('P172_AFH_CLEARANCE').rowListIter()
         except:
            objMsg.printMsg("Unable to get Clearance Table")
            raise

      for row in TgtClrDataTable:
         head = int(row[colDict['HD_LGC_PSN']])
         zone = int(row[colDict['DATA_ZONE']])
         if zone < self.numUserZones:
            try:
               self.TgtClrData[head][zone]['WRT_HEAT_TRGT_CLRNC'] = int(row[colDict['WRT_HEAT_TRGT_CLRNC']])
               self.TgtClrData[head][zone]['READ_HEAT_TRGT_CLRNC'] = int(row[colDict['READ_HEAT_TRGT_CLRNC']])
               self.TgtClrData[head][zone]['PRE_HEAT_TRGT_CLRNC'] = int(row[colDict['PRE_HEAT_TRGT_CLRNC']])
               self.TgtClrData[head][zone]['MAINT_CLRNC_TRGT'] = int(row[colDict['PRE_HEAT_TRGT_CLRNC']])
            except:
               self.TgtClrData[head][zone]['WRT_HEAT_TRGT_CLRNC'] = int(row[colDict['WRT_CLRNC_TRGT']])
               self.TgtClrData[head][zone]['READ_HEAT_TRGT_CLRNC'] = int(row[colDict['RD_CLRNC_TRGT']])
               self.TgtClrData[head][zone]['PRE_HEAT_TRGT_CLRNC'] = int(row[colDict['PRE_WRT_CLRNC_TRGT']])
               self.TgtClrData[head][zone]['MAINT_CLRNC_TRGT'] = int(row[colDict['MAINT_CLRNC_TRGT']])

      for clrAdjust in [TP.BPIMarginClrBackoff]:
         setPrm = {}
         setPrm.update(TP.afhTargetClearance_by_zone)

         ClearanceTarget = self.TgtClrData[0][0]['WRT_HEAT_TRGT_CLRNC']
         self.FlatClearance = 1
         for head in xrange(self.numHeads):
            for zone in xrange(self.numUserZones):
               if ClearanceTarget != self.TgtClrData[head][zone]['WRT_HEAT_TRGT_CLRNC'] or \
                     ClearanceTarget != self.TgtClrData[head][zone]['MAINT_CLRNC_TRGT'] or \
                     ClearanceTarget != self.TgtClrData[head][zone]['PRE_HEAT_TRGT_CLRNC'] or \
                     ClearanceTarget != self.TgtClrData[head][zone]['READ_HEAT_TRGT_CLRNC']:
                        self.FlatClearance = 0
                        break

         if self.FlatClearance:
            setPrm["BIT_MASK"] = (0xFFFF,0xFFFF,)
            setPrm["TGT_WRT_CLR"] = (self.TgtClrData[0][0]['WRT_HEAT_TRGT_CLRNC'] + clrAdjust,)
            setPrm["TGT_MAINTENANCE_CLR"] = (self.TgtClrData[0][0]['MAINT_CLRNC_TRGT'] + clrAdjust,)
            setPrm["TGT_PREWRT_CLR"] = (self.TgtClrData[0][0]['PRE_HEAT_TRGT_CLRNC'] + clrAdjust,)
            setPrm["TGT_RD_CLR"] = (self.TgtClrData[0][0]['READ_HEAT_TRGT_CLRNC'] + clrAdjust,)
            getVbarGlobalClass(CProcess).St(setPrm)
         else:
            for head in xrange(self.numHeads):
               for zone in xrange(self.numUserZones):
                  setPrm["TGT_WRT_CLR"] = (self.TgtClrData[head][zone]['WRT_HEAT_TRGT_CLRNC'] + clrAdjust,)
                  setPrm["TGT_MAINTENANCE_CLR"] = (self.TgtClrData[head][zone]['MAINT_CLRNC_TRGT'] + clrAdjust,)
                  setPrm["TGT_PREWRT_CLR"] = (self.TgtClrData[head][zone]['PRE_HEAT_TRGT_CLRNC'] + clrAdjust,)
                  setPrm["TGT_RD_CLR"] = (self.TgtClrData[head][zone]['READ_HEAT_TRGT_CLRNC'] + clrAdjust,)
                  setPrm["BIT_MASK"] = self.oUtility.ReturnTestCylWord(2**zone)
                  getVbarGlobalClass(CProcess).St(setPrm)

         getVbarGlobalClass(CProcess).St({'test_num':178, 'prm_name':[], 'timeout': 600, 'CWORD1': 544}) # Save to Flash
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
         getVbarGlobalClass(CProcess).St({'test_num':172, 'prm_name':[],'timeout': 1800, 'CWORD1': (5,)}) # Dump Data
         getVbarGlobalClass(CProcess).St({'test_num':172, 'prm_name':[],'timeout': 1800, 'CWORD1': (4,)}) # Dump Data
         #try:
         #   hdMsk = (hd << 8) + hd
         #   TP.prm_quickSER_250_TCC_ClrAdj.update({'TEST_HEAD':hdMsk})
         #   getVbarGlobalClass(CProcess).St(TP.prm_quickSER_250_TCC_ClrAdj)
         #except:
         #   pass

   #-------------------------------------------------------------------------------------------------------
   def __restoreTGTCLR(self):
      setPrm = {}
      setPrm.update(TP.afhTargetClearance_by_zone)
      if self.FlatClearance:
         setPrm["BIT_MASK"] = (0xFFFF,0xFFFF,)
         setPrm["TGT_WRT_CLR"] = (self.TgtClrData[0][0]['WRT_HEAT_TRGT_CLRNC'],)
         setPrm["TGT_MAINTENANCE_CLR"] = (self.TgtClrData[0][0]['MAINT_CLRNC_TRGT'],)
         setPrm["TGT_PREWRT_CLR"] = (self.TgtClrData[0][0]['PRE_HEAT_TRGT_CLRNC'],)
         setPrm["TGT_RD_CLR"] = (self.TgtClrData[0][0]['READ_HEAT_TRGT_CLRNC'],)
         getVbarGlobalClass(CProcess).St(setPrm)
      else:
         for head in xrange(self.numHeads):
            for zone in xrange(self.numUserZones):
               setPrm["TGT_WRT_CLR"] = (self.TgtClrData[head][zone]['WRT_HEAT_TRGT_CLRNC'] ,)
               setPrm["TGT_MAINTENANCE_CLR"] = (self.TgtClrData[head][zone]['MAINT_CLRNC_TRGT'] ,)
               setPrm["TGT_PREWRT_CLR"] = (self.TgtClrData[head][zone]['PRE_HEAT_TRGT_CLRNC'] ,)
               setPrm["TGT_RD_CLR"] = (self.TgtClrData[head][zone]['READ_HEAT_TRGT_CLRNC'] ,)
               setPrm["BIT_MASK"] = self.oUtility.ReturnTestCylWord(2**zone)
               getVbarGlobalClass(CProcess).St(setPrm)

      getVbarGlobalClass(CProcess).St({'test_num':178, 'prm_name':[], 'timeout': 600, 'CWORD1': 544}) # Save to Flash
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      getVbarGlobalClass(CProcess).St({'test_num':172, 'prm_name':[],'timeout': 1800, 'CWORD1': (5,)}) # Dump Data
      getVbarGlobalClass(CProcess).St({'test_num':172, 'prm_name':[],'timeout': 1800, 'CWORD1': (4,)}) # Dump Data

   def Dummy_dblog_data(self):

       for hd in xrange(self.numHeads):
          for zn in xrange(self.numUserZones):
                  self.dut.dblData.Tables('P211_WRT_PWR_TBL').addRecord({
                      'HD_PHYS_PSN'        : hd,
                      'HD_LGC_PSN'         : hd,
                      'DATA_ZONE'          : zn,
                      'WPOWER'             : 0,
                      'ZEROHEATCLR'        : 0.3333,
                      'CLRWWHT'            : 0,
                      'WPWGHT'             : 0,
                      'BPICAP'             : 1,
                      'FBPICAP'            : 0,
                      'TPICAP'             : 1,
                      'FTPICAP'            : 0,
                      'SATURATION'         : 0,
                      'CAPCTY'             : 0,
                      })



       for hd in xrange(self.numHeads):
          for zn in xrange(self.numUserZones):
                  self.dut.dblData.Tables('P211_BPI_MEASUREMENT').addRecord({
                      'HD_PHYS_PSN'        : hd,
                      'DATA_ZONE'          : zn,
                      'HD_LGC_PSN'         : hd,
                      'TRK_NUM'            : 0,
                      'DELTA_BPI_PCT'      : 5,
                      'M_VAL'              : 0,
                      'F_VAL'              : 0,
                      'SECTOR_ERROR_RATE'  : 0.0053,
                      'BANDWIDTH'          : 0,
                      'BANDWIDTH_RNG'      : 0,
                      'TW_3'               : 0,
                      'TW_5'               : 0,
                      'PRECOMP'            : 0,
                      'BOOST'              : 0,
                      })

                  self.dut.dblData.Tables('P211_BPI_MEASUREMENT').addRecord({
                      'HD_PHYS_PSN'        : hd,
                      'DATA_ZONE'          : zn,
                      'HD_LGC_PSN'         : hd,
                      'TRK_NUM'            : 0,
                      'DELTA_BPI_PCT'      : 6,
                      'M_VAL'              : 0,
                      'F_VAL'              : 0,
                      'SECTOR_ERROR_RATE'  : 0.0062,
                      'BANDWIDTH'          : 0,
                      'BANDWIDTH_RNG'      : 0,
                      'TW_3'               : 0,
                      'TW_5'               : 0,
                      'PRECOMP'            : 0,
                      'BOOST'              : 0,
                      })
                  self.dut.dblData.Tables('P211_BPI_MEASUREMENT').addRecord({
                      'HD_PHYS_PSN'        : hd,
                      'DATA_ZONE'          : zn,
                      'HD_LGC_PSN'         : hd,
                      'TRK_NUM'            : 0,
                      'DELTA_BPI_PCT'      : 7,
                      'M_VAL'              : 0,
                      'F_VAL'              : 0,
                      'SECTOR_ERROR_RATE'  : 0.0073,
                      'BANDWIDTH'          : 0,
                      'BANDWIDTH_RNG'      : 0,
                      'TW_3'               : 0,
                      'TW_5'               : 0,
                      'PRECOMP'            : 0,
                      'BOOST'              : 0,
                      })
                  self.dut.dblData.Tables('P211_BPI_MEASUREMENT').addRecord({
                      'HD_PHYS_PSN'        : hd,
                      'DATA_ZONE'          : zn,
                      'HD_LGC_PSN'         : hd,
                      'TRK_NUM'            : 0,
                      'DELTA_BPI_PCT'      : 8,
                      'M_VAL'              : 0,
                      'F_VAL'              : 0,
                      'SECTOR_ERROR_RATE'  : 0.0089,
                      'BANDWIDTH'          : 0,
                      'BANDWIDTH_RNG'      : 0,
                      'TW_3'               : 0,
                      'TW_5'               : 0,
                      'PRECOMP'            : 0,
                      'BOOST'              : 0,
                      })
                  self.dut.dblData.Tables('P211_BPI_MEASUREMENT').addRecord({
                      'HD_PHYS_PSN'        : hd,
                      'DATA_ZONE'          : zn,
                      'HD_LGC_PSN'         : hd,
                      'TRK_NUM'            : 0,
                      'DELTA_BPI_PCT'      : 5,
                      'M_VAL'              : 0,
                      'F_VAL'              : 0,
                      'SECTOR_ERROR_RATE'  : 0.0055,
                      'BANDWIDTH'          : 0,
                      'BANDWIDTH_RNG'      : 0,
                      'TW_3'               : 0,
                      'TW_5'               : 0,
                      'PRECOMP'            : 0,
                      'BOOST'              : 0,
                      })
                  self.dut.dblData.Tables('P211_BPI_MEASUREMENT').addRecord({
                      'HD_PHYS_PSN'        : hd,
                      'DATA_ZONE'          : zn,
                      'HD_LGC_PSN'         : hd,
                      'TRK_NUM'            : 0,
                      'DELTA_BPI_PCT'      : 6,
                      'M_VAL'              : 0,
                      'F_VAL'              : 0,
                      'SECTOR_ERROR_RATE'  : 0.0064,
                      'BANDWIDTH'          : 0,
                      'BANDWIDTH_RNG'      : 0,
                      'TW_3'               : 0,
                      'TW_5'               : 0,
                      'PRECOMP'            : 0,
                      'BOOST'              : 0,
                      })
                  self.dut.dblData.Tables('P211_BPI_MEASUREMENT').addRecord({
                      'HD_PHYS_PSN'        : hd,
                      'DATA_ZONE'          : zn,
                      'HD_LGC_PSN'         : hd,
                      'TRK_NUM'            : 0,
                      'DELTA_BPI_PCT'      : 7,
                      'M_VAL'              : 0,
                      'F_VAL'              : 0,
                      'SECTOR_ERROR_RATE'  : 0.0076,
                      'BANDWIDTH'          : 0,
                      'BANDWIDTH_RNG'      : 0,
                      'TW_3'               : 0,
                      'TW_5'               : 0,
                      'PRECOMP'            : 0,
                      'BOOST'              : 0,
                      })
                  self.dut.dblData.Tables('P211_BPI_MEASUREMENT').addRecord({
                      'HD_PHYS_PSN'        : hd,
                      'DATA_ZONE'          : zn,
                      'HD_LGC_PSN'         : hd,
                      'TRK_NUM'            : 0,
                      'DELTA_BPI_PCT'      : 4,
                      'M_VAL'              : 0,
                      'F_VAL'              : 0,
                      'SECTOR_ERROR_RATE'  : 0.0046,
                      'BANDWIDTH'          : 0,
                      'BANDWIDTH_RNG'      : 0,
                      'TW_3'               : 0,
                      'TW_5'               : 0,
                      'PRECOMP'            : 0,
                      'BOOST'              : 0,
                      })
                  self.dut.dblData.Tables('P211_BPI_MEASUREMENT').addRecord({
                      'HD_PHYS_PSN'        : hd,
                      'DATA_ZONE'          : zn,
                      'HD_LGC_PSN'         : hd,
                      'TRK_NUM'            : 0,
                      'DELTA_BPI_PCT'      : -6,
                      'M_VAL'              : 0,
                      'F_VAL'              : 0,
                      'SECTOR_ERROR_RATE'  : 0.0009,
                      'BANDWIDTH'          : 0,
                      'BANDWIDTH_RNG'      : 0,
                      'TW_3'               : 0,
                      'TW_5'               : 0,
                      'PRECOMP'            : 0,
                      'BOOST'              : 0,
                      })
                  self.dut.dblData.Tables('P211_BPI_MEASUREMENT').addRecord({
                      'HD_PHYS_PSN'        : hd,
                      'DATA_ZONE'          : zn,
                      'HD_LGC_PSN'         : hd,
                      'TRK_NUM'            : 0,
                      'DELTA_BPI_PCT'      : -5,
                      'M_VAL'              : 0,
                      'F_VAL'              : 0,
                      'SECTOR_ERROR_RATE'  : 0.0011,
                      'BANDWIDTH'          : 0,
                      'BANDWIDTH_RNG'      : 0,
                      'TW_3'               : 0,
                      'TW_5'               : 0,
                      'PRECOMP'            : 0,
                      'BOOST'              : 0,
                      })
                  self.dut.dblData.Tables('P211_BPI_MEASUREMENT').addRecord({
                      'HD_PHYS_PSN'        : hd,
                      'DATA_ZONE'          : zn,
                      'HD_LGC_PSN'         : hd,
                      'TRK_NUM'            : 0,
                      'DELTA_BPI_PCT'      : -4,
                      'M_VAL'              : 0,
                      'F_VAL'              : 0,
                      'SECTOR_ERROR_RATE'  : 0.0012,
                      'BANDWIDTH'          : 0,
                      'BANDWIDTH_RNG'      : 0,
                      'TW_3'               : 0,
                      'TW_5'               : 0,
                      'PRECOMP'            : 0,
                      'BOOST'              : 0,
                      })
                  self.dut.dblData.Tables('P211_BPI_MEASUREMENT').addRecord({
                      'HD_PHYS_PSN'        : hd,
                      'DATA_ZONE'          : zn,
                      'HD_LGC_PSN'         : hd,
                      'TRK_NUM'            : 0,
                      'DELTA_BPI_PCT'      : -3,
                      'M_VAL'              : 0,
                      'F_VAL'              : 0,
                      'SECTOR_ERROR_RATE'  : 0.0015,
                      'BANDWIDTH'          : 0,
                      'BANDWIDTH_RNG'      : 0,
                      'TW_3'               : 0,
                      'TW_5'               : 0,
                      'PRECOMP'            : 0,
                      'BOOST'              : 0,
                      })
                  self.dut.dblData.Tables('P211_BPI_MEASUREMENT').addRecord({
                      'HD_PHYS_PSN'        : hd,
                      'DATA_ZONE'          : zn,
                      'HD_LGC_PSN'         : hd,
                      'TRK_NUM'            : 0,
                      'DELTA_BPI_PCT'      : -6,
                      'M_VAL'              : 0,
                      'F_VAL'              : 0,
                      'SECTOR_ERROR_RATE'  : 0.0009,
                      'BANDWIDTH'          : 0,
                      'BANDWIDTH_RNG'      : 0,
                      'TW_3'               : 0,
                      'TW_5'               : 0,
                      'PRECOMP'            : 0,
                      'BOOST'              : 0,
                      })
                  self.dut.dblData.Tables('P211_BPI_MEASUREMENT').addRecord({
                      'HD_PHYS_PSN'        : hd,
                      'DATA_ZONE'          : zn,
                      'HD_LGC_PSN'         : hd,
                      'TRK_NUM'            : 0,
                      'DELTA_BPI_PCT'      : -5,
                      'M_VAL'              : 0,
                      'F_VAL'              : 0,
                      'SECTOR_ERROR_RATE'  : 0.0010,
                      'BANDWIDTH'          : 0,
                      'BANDWIDTH_RNG'      : 0,
                      'TW_3'               : 0,
                      'TW_5'               : 0,
                      'PRECOMP'            : 0,
                      'BOOST'              : 0,
                      })
                  self.dut.dblData.Tables('P211_BPI_MEASUREMENT').addRecord({
                      'HD_PHYS_PSN'        : hd,
                      'DATA_ZONE'          : zn,
                      'HD_LGC_PSN'         : hd,
                      'TRK_NUM'            : 0,
                      'DELTA_BPI_PCT'      : -4,
                      'M_VAL'              : 0,
                      'F_VAL'              : 0,
                      'SECTOR_ERROR_RATE'  : 0.0013,
                      'BANDWIDTH'          : 0,
                      'BANDWIDTH_RNG'      : 0,
                      'TW_3'               : 0,
                      'TW_5'               : 0,
                      'PRECOMP'            : 0,
                      'BOOST'              : 0,
                      })
                  self.dut.dblData.Tables('P211_BPI_MEASUREMENT').addRecord({
                      'HD_PHYS_PSN'        : hd,
                      'DATA_ZONE'          : zn,
                      'HD_LGC_PSN'         : hd,
                      'TRK_NUM'            : 0,
                      'DELTA_BPI_PCT'      : -3,
                      'M_VAL'              : 0,
                      'F_VAL'              : 0,
                      'SECTOR_ERROR_RATE'  : 0.0015,
                      'BANDWIDTH'          : 0,
                      'BANDWIDTH_RNG'      : 0,
                      'TW_3'               : 0,
                      'TW_5'               : 0,
                      'PRECOMP'            : 0,
                      'BOOST'              : 0,
                      })

   #-------------------------------------------------------------------------------------------------------
   #dummy S2D function
   def measureSingleSidedTPI_S2D(self, prmOverride, hd, zn, wp, meas, target_index = ''):
      return meas
   
   #-------------------------------------------------------------------------------------------------------
   def measure_allZoneOTC(self, znTst, update_TPIOTC = 0):
      prm_TPI_211_OTC = deepcopy(TP.prm_TPI_211_OTC)
      ## ignore all previous state data ##
      if update_TPIOTC:
         table_TpiCap = DBLogReader(self.dut, 'P211_TPI_CAP_AVG')
         table_TpiCap.ignoreExistingData()
      if testSwitch.T211_MERGE_READ_OFFSET_TBL_INTO_TPI_MEAS_TBL:
         tableRetrieveRdOfset = 'P211_TPI_CAP_AVG'
      else: tableRetrieveRdOfset = 'P211_RD_OFST_AVG'
      table_rdOfset = DBLogReader(self.dut, tableRetrieveRdOfset)
      table_rdOfset.ignoreExistingData()
      ##                                ##
      if 'TEST_HEAD' in prm_TPI_211_OTC:  del prm_TPI_211_OTC['TEST_HEAD']
      if 'ZONE' in prm_TPI_211_OTC:       del prm_TPI_211_OTC['ZONE']
      if 'THRESHOLD' in prm_TPI_211_OTC:  del prm_TPI_211_OTC['THRESHOLD']
      if 'TARGET_SER' in prm_TPI_211_OTC: del prm_TPI_211_OTC['TARGET_SER']
      
      if testSwitch.CM_REDUCTION_REDUCE_PRINTMSG:
         prm_TPI_211_OTC['RESULTS_RETURNED'] = prm_TPI_211_OTC['RESULTS_RETURNED'] | 0x0008 # Turn off P211_TPI_INIT / P211_HEADER_INFO
               
      MaskList = self.oUtility.convertListToZoneBankMasks(znTst)
      for bank, list in MaskList.iteritems():
         if list:
            prm_TPI_211_OTC['ZONE_MASK_EXT'], prm_TPI_211_OTC['ZONE_MASK'] = \
               self.oUtility.convertListTo64BitMask(list)
            if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
               prm_TPI_211_OTC['ZONE_MASK_BANK'] = bank
            getVbarGlobalClass(CProcess).St(prm_TPI_211_OTC)
      for record in table_rdOfset.iterRows():
         hd = int(record.get('HD_LGC_PSN'))
         zn = int(record.get('DATA_ZONE'))
         meas = CVbarDataHelper(self.measurements, hd, zn)
         meas['RD_OFST_OTC'] = float(record.get('RD_OFST_AVG'))
         if update_TPIOTC:
            tpi_otc  = float(record.get('TPI_CAP_AVG'))
            if tpi_otc < 0.5: # use a predefined margin backoff if OTC can not measure
               meas['TPI_OTC'] = max(meas['TPI_IDSS'],meas['TPI_ODSS']) - TP.Overide_OTC_Margin
               objMsg.printMsg('TPI OTC MEASUREMENT OVERIDE Hd %d  Zn %d  TPIOTC %4f' % (hd, zn, meas['TPI_OTC']))
            else:
               meas['TPI_OTC'] = tpi_otc
            meas['TPI_OTC'] = self.formatScaler.scaleTPI(hd,zn,meas['TPI_OTC'])
            objMsg.printMsg('SCALED TPI OTC MEASUREMENT Hd %d  Zn %d  TPIOTC %4f' % (hd,zn,meas['TPI_OTC']))
###########################################################################################################
###########################################################################################################

class CMeasureBPIAndTPIinWpZones(CMeasureBPIAndTPI):
   def __init__(self, measurements):
      self.opMode = 'WpZones'

      CMeasureBPIAndTPI.__init__(self, measurements)

   #-------------------------------------------------------------------------------------------------------
   def measureBPINominal(self, hd_mask, testZones, prm_override=getattr(TP, 'MeasureBPI_211', {}),use_wp_in_rap=False):
      ############# Set up parameter block ##############
      # Note: It is assumed that the write power triplet for hd zero, zn zero, is applicable
      # to all heads and zones.  This is a requirement for doing multiple heads and zones
      # with a single call to Test 211.  The BPI Nominal write power test parameter will be used.
      if testSwitch.FE_0120024_340210_ATI_IN_WRT_PWR_PICKER :
         wc, ovs, ovd = self.objRapTcc.VbarWPTable[0][0][TP.WPForVBPINominalMeasurements]
      else:
         wc, ovs, ovd = self.objRapTcc.VbarWPTable[0][TP.WPForVBPINominalMeasurements]

      prm_BPI_211 = {'test_num'           : 211,
                     'prm_name'           : 'MeasureBPINominal_211',
                     'HEAD_MASK'          : hd_mask,
                     'NUM_TRACKS_PER_ZONE': 6,
                     'ZONE_POSITION'      : TP.VBAR_ZONE_POS,
                     'BPI_MAX_PUSH_RELAX' : TP.VbarBpiMaxPushRelax,
                     'CWORD1'             : 0x0015, #Enable multi-track mode
                     'CWORD2'             : 0x0010, #Enable BIE for BPIC
                     'SET_OCLIM'          : 655,
                     'WRITE_CURRENT'      : wc,
                     'DAMPING'            : ovs,
                     'DURATION'           : ovd,
                     'RESULTS_RETURNED'   : 0x000E,
                     'timeout'            : 3600,
                     'spc_id'             : 0,
                     }

      if use_wp_in_rap:
         prm_BPI_211 = {'test_num'           : 211,
               'prm_name'           : 'MeasureBPINominal_211',
               'HEAD_MASK'          : hd_mask,
               'NUM_TRACKS_PER_ZONE': 6,
               'ZONE_POSITION'      : TP.VBAR_ZONE_POS,
               'BPI_MAX_PUSH_RELAX' : TP.VbarBpiMaxPushRelax,
               'CWORD1'             : 0x0015, #Enable multi-track mode
               'CWORD2'             : 0x0010, #Enable BIE for BPIC
               'SET_OCLIM'          : 655,
               'RESULTS_RETURNED'   : 0x000E,
               'timeout'            : 3600,
               'spc_id'             : 0,
               }
      prm_BPI_211.update(prm_override)


      if testSwitch.FE_0119998_231166_FACTORY_VBAR_ADC_ENHANCEMENTS:
         # if EC13409 rerun vbar, back off from 40% to 20%
         if self.dut.driveattr['WTF_CTRL'] == 'VBAR_13409' and prm_BPI_211['CWORD1'] & 0x10:
            prm_BPI_211['CWORD1'] &= 0xFFEF
            prm_BPI_211['CWORD1'] |= 0x20

      ############# Run the measurement ##############
      table = DBLogReader(self.dut, 'P211_BPI_CAP_AVG')
      table.ignoreExistingData()

      if testSwitch.extern.FE_0284077_007867_SGL_CALL_250_ZN_VBAR_SUPPORT:
         prm_BPI_211['ZONE_MASK_BLOCK'] = self.oUtility.setZoneMaskBlock(testZones)
         getVbarGlobalClass(CProcess).St(prm_BPI_211)
      else:
         MaskList = self.oUtility.convertListToZoneBankMasks(testZones)
         for bank, list in MaskList.iteritems():
            if list:
               prm_BPI_211 ['ZONE_MASK_EXT'], prm_BPI_211 ['ZONE_MASK'] = self.oUtility.convertListTo64BitMask(list)
               if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
                  prm_BPI_211 ['ZONE_MASK_BANK'] = bank
               getVbarGlobalClass(CProcess).St(prm_BPI_211)

      if testSwitch.FE_0269922_348085_P_SIGMUND_IN_FACTORY:
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

         
      # Multiple heads and zones have just been measured.  Go ahead and collect the data
      # to make it available at a higher level.
      for record in table.iterRows():
         if testSwitch.FE_0168027_007867_USE_PHYS_HDS_IN_VBAR_DICT:
            hd = int(record['HD_LGC_PSN'])
         else:
            hd = int(record['HD_PHYS_PSN'])

         zn = int(record['DATA_ZONE'])

         meas = CVbarDataHelper(self.measurements, hd, zn, TP.WPForVBPINominalMeasurements)

         if testSwitch.BF_0170582_208705_BPI_NOMINAL_CAPS:
            # Scale the BPI measurement to account for the underlying format picks
            if float(record['BPI_CAP_AVG']) < (1-float(TP.VbarBpiMaxPushRelax+10)/100) : #if the reading is too low, almost less than our max relaxed value
               meas["BPI"] = self.formatScaler.scaleBPI(hd, zn, 0.8) # set it to a value of 1.0 to give it a nominal reading (benifit of doubt).
            else:
               meas["BPI"] = self.formatScaler.scaleBPI(hd, zn, float(record['BPI_CAP_AVG']))
         else:
            meas["BPI"] = float(record['BPI_CAP_AVG'])

   #-------------------------------------------------------------------------------------------------------
   def measureBPIAndTPIByHead(self, hd, znLst):
      #Reset the feedforward amount for each head to target capacity
      tpiCap_FeedForward = 1.0

      for wp in xrange(self.NUM_WRITE_POWERS):
         if testSwitch.FE_0120024_340210_ATI_IN_WRT_PWR_PICKER:
            self.objRapTcc.updateWP(hd, znLst, wp, setAllZonesHeads = 0)
         else:
            self.objRapTcc.updateWP(hd, 0, wp, setAllZonesHeads = 1)

         # Measure BPI
         for zn in znLst:
            meas = CVbarDataHelper(self.measurements, hd, zn, wp)

            meas['BPI'] = self.measureBPI(hd, zn, wp)
            meas['BPI'] = self.formatScaler.scaleBPI(hd, zn, meas['BPI'])

            meas['Interp'] = 'F'

         # Measure TPI
         for zn in znLst:
            meas = CVbarDataHelper(self.measurements, hd, zn, wp)
            if meas['BPI'] != -1.0:

               if testSwitch.SMR:
                  # Both TPI and RD_OFST returned here, just want TPI
                  meas['TPI'] = tpiCap_FeedForward = self.measureTPI(hd, zn, tpiCap_FeedForward,wp)[0]
               else:
                  meas['TPI'] = tpiCap_FeedForward = self.measureTPI(hd, zn, tpiCap_FeedForward,wp)

               meas['TPI'] = self.formatScaler.scaleTPI(hd, zn, meas['TPI'])

               if meas['TPI'] == -1.0:
                  meas['BPI'] = -1.0
                  tpiCap_FeedForward = 1.0
            else:
               meas['TPI'] = -1.0

   #-------------------------------------------------------------------------------------------------------
   def processMemoryDataAsPCFile(self, requestData, *args, **kargs):
      if requestData[0] == chr(81):
         # Write power file values
         FILE_FORMAT = 1
         MAJOR_REV = 1
         MINOR_REV = 0
         NUM_PREAMP = 10
         PREAMP_ID = 0
         PREAMP_MASK = 0

         NUM_WPS = self.NUM_WRITE_POWERS
         NUM_ZONE_FRAMES = len(self.objRapTcc.TripletZnGroups)

         WP_HEADER_SIZE = 48
         PREAMP_FRAME_SIZE = 8
         ZN_FRAME_SIZE = 6 + 4 * NUM_WPS
         ZONE_FRAME_OFFSET = WP_HEADER_SIZE + NUM_PREAMP * PREAMP_FRAME_SIZE

         # Build WP file, in reverse order

         # Zone frames
         zone_frames = ""
         for zones in self.objRapTcc.TripletZnGroups:
            # Get the list of write powers for the given zone group
            if testSwitch.FE_0120024_340210_ATI_IN_WRT_PWR_PICKER:
               wpList = self.objRapTcc.VbarWPTable[0][min(zones)] # Assume head 0 until WP file supports differences by head
            else:
               wpList = self.objRapTcc.VbarWPTable[min(zones)]

            zone_frames += struct.pack("2B2H", min(zones), max(zones), len(wpList), ZN_FRAME_SIZE)

            for wc,ovs,dur in wpList:
               zone_frames += struct.pack("3Bx", wc, ovs, dur)

         # Preamp frames
         preamp_frame = ""
         for i in range(NUM_PREAMP):
            preamp_frame += struct.pack("3Bx2H", PREAMP_ID, PREAMP_MASK, NUM_ZONE_FRAMES, ZONE_FRAME_OFFSET, ZN_FRAME_SIZE)

         # WP file header
         length = len(zone_frames) + len(preamp_frame) + WP_HEADER_SIZE
         header = struct.pack("4BH42s", FILE_FORMAT, MAJOR_REV, MINOR_REV, NUM_PREAMP, length, "WP file built by PF3")

         # Set up full file, including Gemini protocol header
         returnData = struct.pack("3B", 81, 0, 0) + header + preamp_frame + zone_frames
         SendBuffer(returnData)
      else:
         raise ScriptTestFailure,"processMemoryDataAsPCfile: Invalid request: %s" % (`requestData[0]`,)

      RegisterResultsCallback('', 81,)    # Resume normal 81 calls


###########################################################################################################
###########################################################################################################

class CMeasureBPIAndTPIinAllZones(CMeasureBPIAndTPI):
   def __init__(self, measurements):
      self.opMode = 'AllZones'

      CMeasureBPIAndTPI.__init__(self, measurements)

      if testSwitch.FE_0165256_208705_VBAR_STORE_TEMP:
         from Temperature import CTemperature
         # Store Temperature
         self.temperature = CTemperature().retHDATemp()

   #-------------------------------------------------------------------------------------------------------
   def measureAllHMS(self, MeasureHMS_211_Parms, zapOTF=0, spcId=None, adjBPIforTPI = 0, report_option = 0):
      # Measure the HMS capabilities for requested zones.  This function only supports the
      # general VBAR data dictionary.  It does not support the special write power dictionary.

      # Initialize a variable to be used for display purposes,
      # keeping track of which hd/zone locations were measured.
      locations = []

      if testSwitch.FE_0166516_007867_PF3_VBAR_CONSOLIDATED_T211_CALLS:
         # With the new capabilities of Test 211, multiple heads can be selected in a head mask parameter
         # and multiple zones can be selected in a zone mask parameter.  Group heads together that have
         # identical zone masks for testing associated with them, to reduce the number of Test 211 calls.

         # Start by identifying the head/zone combinations that require testing based on BPI changes.
         hdznsWithBPIChange = getHdZnsWithBPIChange(self.measurements)

         # Build a list of (head map, zone map) tuples where head maps for heads with identical zone maps
         # contain multiple heads.  Note that this may result in 'out of order' testing of heads.
         condensedHdznList = optimizeHdZnMasks(hdznsWithBPIChange)

         for hd_mask, zn_mask in condensedHdznList:
            # Create a list of head, zone combinations to be tested on this pass, based on the head and zone masks.
            currentHdznLst = convertHdZnMasksToList((hd_mask, zn_mask))

            ############# Set up parameter block ##############

            # Determine the number of head/zone combinations to be tested in this call,
            # so a proper timeout value can be computed.
            hdCnt,znCnt = getHdAndZnCnt((hd_mask,zn_mask))

            # Same logic for zone position as TPI
            prm_HMS_211 = {'test_num'           : 211,
                           'prm_name'           : 'MeasureHMS_211',
                           'HEAD_MASK'          : hd_mask,
                           'ZONE_POSITION'      : TP.VBAR_ZONE_POS,
                           'NUM_TRACKS_PER_ZONE': 6,
                           'HMS_MAX_PUSH_RELAX' : 300,
                           'HMS_STEP'           : 1,
                           'ADJ_BPI_FOR_TPI'    : TP.VbarAdjBpiForTpi,
                           'THRESHOLD'          : 90,
                           'CWORD1'             : 0x4008,
                           'SET_OCLIM'          : 655,
                           'TARGET_SER'         : 5,
                           'TLEVEL'             : 7,
                           'NUM_SQZ_WRITES'     : 0,
                           'RESULTS_RETURNED'   : 0x0006,
                           'timeout'            : 3600*hdCnt*znCnt,
                           'spc_id'             : 0,
                          }

            if testSwitch.FE_0172018_208705_P_ENABLE_HMS_2PT:
               prm_HMS_211.update({
                           'CWORD1'             : 0x600C,
                        })
            if adjBPIforTPI != 0:
               prm_HMS_211.update({
                           'ADJ_BPI_FOR_TPI'    : adjBPIforTPI,
                        })
            if report_option !=0:
               prm_HMS_211.update({
                           'RESULTS_RETURNED'    : report_option,
                        })

            if spcId!=None:
               prm_HMS_211.update({
                           'spc_id'             : spcId,
                        })
            # Update from Test Parameters
            prm_HMS_211.update(getattr(TP, MeasureHMS_211_Parms, {}))

            # objMsg.printMsg('nextState %s' % self.dut.nextState)
            # if testSwitch.VBAR_HMS_MEAS_ONLY and self.dut.nextState in ['HMSC_SOVA','HMSC_SOVA2']: # SOVA MODE
               # prm_HMS_211.update({
                           # 'TARGET_SER'             : 0x001c,
                           # 'CWORD2'                 : 0x0013,
                           # 'TLEVEL'                 : 0x0000,
                        # })

            if zapOTF == 1:
               prm_HMS_211.update(TP.prm_ZAP_OTF)
               prm_HMS_211['CWORD1'] |= 0x800
               prm_HMS_211['TRACK_LIMIT'] = 0x0101
               prm_HMS_211['timeout'] = 3*prm_HMS_211['timeout']/2

            ############# Run the measurement ##############

            if testSwitch.extern.FE_0155984_208705_VBAR_HMS_BER_PENALTY and 'BER_PENALTY' in prm_HMS_211:
               table = DBLogReader(self.dut, 'P211_HMS_CAP_AVG2')
            else:
               table = DBLogReader(self.dut, 'P211_HMS_CAP_AVG')

            table.ignoreExistingData()
            
            znlist = self.oUtility.deMaskList(zn_mask, self.numUserZones, 2)
            if testSwitch.extern.FE_0284077_007867_SGL_CALL_250_ZN_VBAR_SUPPORT:
               prm_HMS_211['ZONE_MASK_BLOCK'] = self.oUtility.setZoneMaskBlock(znlist)
               getVbarGlobalClass(CProcess).St(prm_HMS_211)
            else:
               MaskList = self.oUtility.convertListToZoneBankMasks(znlist)
               for bank, list in MaskList.iteritems():
                  if list:
                     prm_HMS_211['ZONE_MASK_EXT'], prm_HMS_211['ZONE_MASK'] = self.oUtility.convertListTo64BitMask(list)
                     if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
                        prm_HMS_211['ZONE_MASK_BANK'] = bank
                     getVbarGlobalClass(CProcess).St(prm_HMS_211)

            ############# Log the data ##############

            # HMS data has just been measured across multiple heads and zones, collect the data and update
            # the meas dictionary, before moving on to the next set of heads and zones.
            for record in table.iterRows():
               if testSwitch.FE_0168027_007867_USE_PHYS_HDS_IN_VBAR_DICT:
                  hd = int(record['HD_LGC_PSN'])
               else:
                  hd = int(record['HD_PHYS_PSN'])
               zn = int(record['DATA_ZONE'])

               if testSwitch.virtualRun:
                  # Make sure the current record in the 'canned' data is valid for this run.
                  # If not, just move on to the next record.
                  if (hd, zn) not in hdznsWithBPIChange:
                     continue

               meas = CVbarDataHelper(self.measurements, hd, zn)

               meas['HMS'] = float(record['HMS_CAP_AVG'])
               if testSwitch.extern.FE_0155984_208705_VBAR_HMS_BER_PENALTY and 'BER_PENALTY' in prm_HMS_211:
                  meas['HMSP'] = float(record['CAP_PENALTY'])
               else:
                  meas['HMSP'] = 0.0

               meas['TWC'] = self.clearances[(hd, zn)]['whtc'] / ANGS_PER_NM

               # Store for display below
               locations.append((hd,zn))

               # Clear the reset flag - measurements have been redone
               meas['BPIChanged'] = 'F'

               meas['BPIPick'] = self.formatScaler.getBPIPick(hd, zn)
               meas['TPIPick'] = self.formatScaler.getTPIPick(hd, zn)

      else: # not testSwitch.FE_0166516_007867_PF3_VBAR_CONSOLIDATED_T211_CALLS

         locations = []
         for hd in xrange(self.numHeads): 
            for zn in xrange(self.numUserZones):
               meas = CVbarDataHelper(self.measurements, hd, zn)

               # Measure only if the BPI pick has changed
               if meas['BPIChanged'] == 'T':
                  meas['HMS'], meas['HMSP'] = self.measureHMS(hd, zn, MeasureHMS_211_Parms, zapOTF=zapOTF)

                  meas['TWC'] = self.clearances[(hd, zn)]['whtc'] / ANGS_PER_NM

                  # Store for display below
                  locations.append((hd,zn))

                  # Clear the reset flag - measurements have been redone
                  meas['BPIChanged'] = 'F'

               meas['BPIPick'] = self.formatScaler.getBPIPick(hd, zn)
               meas['TPIPick'] = self.formatScaler.getTPIPick(hd, zn)

   # ------------ Common ---------------
   # ------------ Common ---------------
      self.printMeasurements(locations,spcId=spcId)

   #-------------------------------------------------------------------------------------------------------
   def measureHMS(self, hd, zn, MeasureHMS_211_Parms, zapOTF=0):
      ############# Set up parameter block ##############

      # Same logic for zone position as TPI
      prm_HMS_211 = {'test_num'           : 211,
                     'prm_name'           : 'MeasureHMS_211',
                     'TEST_HEAD'          : hd,
                     'ZONE'               : zn,
                     'ZONE_POSITION'      : TP.VBAR_ZONE_POS,
                     'NUM_TRACKS_PER_ZONE': 6,
                     'HMS_MAX_PUSH_RELAX' : 300,
                     'HMS_STEP'           : 5,
                     'ADJ_BPI_FOR_TPI'    : TP.VbarAdjBpiForTpi,
                     'THRESHOLD'          : 90,
                     'CWORD1'             : 0x400C,
                     'SET_OCLIM'          : 655,
                     'TARGET_SER'         : 5,
                     'TLEVEL'             : 7,
                     'NUM_SQZ_WRITES'     : 0,
                     'RESULTS_RETURNED'   : 0x0006,
                     'timeout'            : 3600,
                     'spc_id'             : 0,
                    }

      if testSwitch.FE_0172018_208705_P_ENABLE_HMS_2PT:
         prm_HMS_211.update({
                     'CWORD1'             : 0x600C,
                  })

      # Update from Test Parameters
      prm_HMS_211.update(getattr(TP, MeasureHMS_211_Parms, {}))

      # Feed-forward the previous HMS capability as a starting point
      meas = CVbarDataHelper(self.measurements, hd, zn)

      hms_unpenalized = meas['HMS'] + meas['HMSP']
      if hms_unpenalized > 0.0:
         prm_HMS_211['HMS_START'] = int( hms_unpenalized * 10 )   # Convert to angstroms

      if zapOTF == 1:
         prm_HMS_211.update(TP.prm_ZAP_OTF)
         prm_HMS_211['CWORD1'] |= 0x800
         prm_HMS_211['TRACK_LIMIT'] = 0x0101
         prm_HMS_211['timeout'] = 3*prm_HMS_211['timeout']/2

      ############# Run the measurement ##############
      if testSwitch.extern.FE_0155984_208705_VBAR_HMS_BER_PENALTY and 'BER_PENALTY' in prm_HMS_211:
         table = DBLogReader(self.dut, 'P211_HMS_CAP_AVG2')
      else:
         table = DBLogReader(self.dut, 'P211_HMS_CAP_AVG')

      table.ignoreExistingData()

      getVbarGlobalClass(CProcess).St(prm_HMS_211)

      row = table.findRow({'HD_LGC_PSN':hd, 'DATA_ZONE':zn})
      if row:
         hms = float(row['HMS_CAP_AVG'])
         if testSwitch.extern.FE_0155984_208705_VBAR_HMS_BER_PENALTY and 'BER_PENALTY' in prm_HMS_211:
            penalty = float(row['CAP_PENALTY'])
         else:
            penalty = 0.0
      else:
         hms = 0.0
         penalty = 0.0

      return hms, penalty

   #-------------------------------------------------------------------------------------------------------
   def measureAllTPI(self, znLst, zapOTF=0):
      if testSwitch.FE_0166516_007867_PF3_VBAR_CONSOLIDATED_T211_CALLS:
         # With the new capabilities of Test 211, multiple heads can be selected in a head mask parameter
         # and multiple zones can be selected in a zone mask parameter.  Group heads together that have
         # identical zone masks for testing associated with them, to reduce the number of Test 211 calls.

         # Build a head mask comprised of all heads on the drive.
         hd_mask = 0
         for hd in range(self.numHeads):
            hd_mask |= (1 << hd)

         # Build a similar zone mask for all zones required to be tested.
         #zn_mask = 0
         #for zn in znLst:
         #   zn_mask |= (1 << zn)
         zone_mask_low = 0
         zone_mask_high = 0
         for zn in znLst:
            if zn < 32:
               zone_mask_low |= (1 << zn)
            else:
               zone_mask_high |= (1 << (zn -32))
         ############# Set up the standard parameter block ##############

         if testSwitch.SMR_2D_VBAR_OTC_BASED:

            prm_TPI_211 = {'test_num'           : 211,
                           'prm_name'           : 'MeasureTPI_211',
                           'HEAD_MASK'          : hd_mask,
                           #'ZONE_MASK'          : self.oUtility.ReturnTestCylWord(zn_mask),
                           'ZONE_MASK'          : self.oUtility.ReturnTestCylWord(zone_mask_low),
                           'ZONE_MASK_EXT'          : self.oUtility.ReturnTestCylWord(zone_mask_high),
                           'NUM_TRACKS_PER_ZONE': 6,
                           'NUM_SQZ_WRITES'     : TP.num_sqz_writes,
                           'ZONE_POSITION'      : TP.VBAR_ZONE_POS,
                           'ADJ_BPI_FOR_TPI'    : 0,
                           'CWORD1'             : 0x0032,   #Enable multi-track mode
                           'CWORD2'             : 0x0000,   #Enable multi-track mode
                           'SET_OCLIM'          : 655,
                           'TARGET_SER'         : 5,
                           'TPI_TARGET_SER'     : 5,
                           'RESULTS_RETURNED'   : 0x0006,
                           'timeout'            : 3600*self.numHeads*len(znLst),
                           'spc_id'             : 0,
                           }

         else:
            prm_TPI_211 = {'test_num'           : 211,
                           'prm_name'           : 'MeasureTPI_211',
                           'HEAD_MASK'          : hd_mask,
                           #'ZONE_MASK'          : self.oUtility.ReturnTestCylWord(zn_mask),
                           'ZONE_MASK'          : self.oUtility.ReturnTestCylWord(zone_mask_low),
                           'ZONE_MASK_EXT'          : self.oUtility.ReturnTestCylWord(zone_mask_high),
                           'NUM_TRACKS_PER_ZONE': 6,
                           'NUM_SQZ_WRITES'     : TP.num_sqz_writes,
                           'ZONE_POSITION'      : TP.VBAR_ZONE_POS,
                           'ADJ_BPI_FOR_TPI'    : 0,
                           'CWORD1'             : 0x0032,   #Enable multi-track mode
                           'SET_OCLIM'          : 655,
                           'TARGET_SER'         : 5,
                           'TPI_TARGET_SER'     : 5,
                           'RESULTS_RETURNED'   : 0x0006,
                           'timeout'            : 3600*self.numHeads*len(znLst),
                           'spc_id'             : 0,
                           }

         # Load in any override parameters that the user has defined in a test parameters file.
         prm_TPI_211.update(TP.MeasureTPIOnly_211)

         # Since write powers have already been selected, set CWORD1 to do the measurements at nominal clearance.
         prm_TPI_211['CWORD1'] &= 0xFFAF

         # Load/update parameters to support ZAP.
         if zapOTF == 1:
            prm_TPI_211.update(TP.prm_ZAP_OTF)
            prm_TPI_211['CWORD1'] |= 0x800
            prm_TPI_211['TRACK_LIMIT'] = 0x0101
            prm_TPI_211['timeout'] = 3*prm_TPI_211['timeout']/2

         ############# Run the measurement ##############

         table = DBLogReader(self.dut, 'P211_TPI_CAP_AVG')
         table.ignoreExistingData()

         getVbarGlobalClass(CProcess).St(prm_TPI_211)

         ############# Log the data ##############

         for record in table.iterRows():
            if testSwitch.FE_0168027_007867_USE_PHYS_HDS_IN_VBAR_DICT:
               hd = int(record['HD_LGC_PSN'])
            else:
               hd = int(record['HD_PHYS_PSN'])

            zn = int(record['DATA_ZONE'])

            meas = CVbarDataHelper(self.measurements, hd, zn)

            meas['TPI'] = float(record['TPI_CAP_AVG'])
            if meas['TPI'] != -1.0:
               meas['TPI'] = self.formatScaler.scaleTPI(hd, zn, meas['TPI'])

      else: # not testSwitch.FE_0166516_007867_PF3_VBAR_CONSOLIDATED_T211_CALLS
         for hd in range(self.numHeads):
            #Reset the feedforward amount for each head to target capacity
            tpiCap_FeedForward = 1.0

            # Measure TPI
            for zn in znLst:
               meas = CVbarDataHelper(self.measurements, hd, zn)

               if testSwitch.SMR:
                  meas['TPI'] = tpiCap_FeedForward = self.measureTPI(hd, zn, tpiCap_FeedForward, prm_override=TP.MeasureTPIOnly_211, zapOTF=zapOTF)[0]
               else:
                  meas['TPI'] = tpiCap_FeedForward = self.measureTPI(hd, zn, tpiCap_FeedForward, prm_override=TP.MeasureTPIOnly_211, zapOTF=zapOTF)

               if meas['TPI'] == -1.0:
                  tpiCap_FeedForward = 1.0
               else:
                  meas['TPI'] = self.formatScaler.scaleTPI(hd, zn, meas['TPI'])

   # ------------ Common ---------------

      # Display results
      hdzns = [(hd,zn) for hd in range(self.numHeads) for zn in znLst]
      self.printMeasurements(hdzns)

      return self.measurements

   ## Currently it is written to filter TPI measurement only, if need to filter BPI, the lumpData function need to change.
   ## TODO: write it to allow filtering of BPI or both BPI and TPI measurements
   def filterMeasurements (self, BpiOrTpi='TPI'):

      for hd in xrange(self.numHeads):
         dataList = []
         for zn in xrange(self.numUserZones):
            dataList.append(self.measurements.getRecord(BpiOrTpi, hd, zn))
         lumpRequired, lumpedData = self.lumpData(BpiOrTpi, dataList)
         if lumpRequired or BpiOrTpi == 'TPI'or BpiOrTpi == 'TPI_IDSS'or BpiOrTpi == 'TPI_ODSS':
            filteredList = self.quadraticMedianfilter(lumpedData)
            for zn in xrange(self.numUserZones):
               self.measurements.setRecord(BpiOrTpi, filteredList[zn], hd, zn)

   def lumpData(self, BpiOrTpi, dataList):
      lumpRequired = 0
      lumpedData = []
      lumpedData.extend(dataList)

      if BpiOrTpi.upper() == 'BPI':
         metric_min = TP.BPI_MIN
      elif (BpiOrTpi.upper() == 'TPI' or BpiOrTpi.upper() == 'TPI_IDSS' or BpiOrTpi.upper() == 'TPI_ODSS'):
         metric_min = TP.TPI_MIN
      else:
         return [lumpRequired, lumpedData]

      for index in range(len(dataList)):
         if metric_min > dataList[index]:
            lumpRequired = 1
            if index == 0:
               # Find the next point with good value
               nextGoodTpi = -1
               for index2 in range(1,len(dataList)):
                  if dataList[index2] > metric_min:
                     nextGoodTpi = dataList[index2]
                     break
               if nextGoodTpi != -1:
                  lumpedData[index] = nextGoodTpi
               else:
                  lumpedData[index] = metric_min
            else:
               if (metric_min > lumpedData[index]) and (lumpedData[index-1] >= metric_min):
                  lumpedData[index] = lumpedData[index-1]
      if lumpRequired: objMsg.printMsg('lumped%sData:%s' % (BpiOrTpi,lumpedData))
      return [lumpRequired, lumpedData]
   #-------------------------------------------------------------------------------------------------------
   def lumpData_by_mean(self, BpiOrTpi, dataList):
      lumpRequired = 0
      lumpedData = []
      lumpedData.extend(dataList)

      if BpiOrTpi.upper() in ['BPI','TPI','TPI_DSS','TPI_IDSS','TPI_ODSS'] and len(dataList):
         metric_mean = float(sum(dataList))/float(len(dataList))
      else:
         return [lumpRequired, lumpedData]

      for index in range(len(dataList)):
         if metric_mean - dataList[index] > 0.10:
            lumpRequired = 1
            if index == 0:
               # Find the next point with good value
               nextGoodPoint = -1
               for index2 in range(1,len(dataList)):
                  if metric_mean - dataList[index2] < 0.10:
                     nextGoodPoint = dataList[index2]
                     break
               if nextGoodPoint != -1:
                  lumpedData[index] = nextGoodPoint
               else:
                  lumpedData[index] = metric_mean # Adjust to mean
            else:
               if (metric_mean - lumpedData[index] > 0.10) and (metric_mean - lumpedData[index-1] < 0.10):
                  lumpedData[index] = lumpedData[index-1] # Copy the previous good point
      if lumpRequired: objMsg.printMsg('lumped%sData:%s' % (BpiOrTpi,lumpedData))
      return [lumpRequired, lumpedData]
   #-------------------------------------------------------------------------------------------------------
   def linear_fit(self, base_zn_list, dataList):
      # replace dataList data with the Liner Fitting based on base_zn_list
      for index in range(len(base_zn_list)-1):
         zn1 = base_zn_list[index]
         zn2 = base_zn_list[index + 1]
         if zn1 + 1 != zn2: # Zones are not consecutive
            meas1 = dataList[zn1]
            meas2 = dataList[zn2]
            for zn in range(zn1,zn2):
               dataList[zn] = meas2 - ((meas2 - meas1) * (zn2 - zn) / (zn2 - zn1))
         if index == 0 and zn1 != 0:
            for zn in range(0,zn1): # in case the first zones were not measured
               dataList[zn] = meas2 - ((meas2 - meas1) * (zn2 - zn) / (zn2 - zn1))
         elif index == len(base_zn_list)-2 and zn2 != self.numUserZones - 1:
            if zn1 + 1 == zn2: #exception case
               meas1 = dataList[zn1]
               meas2 = dataList[zn2]
            for zn in range(zn2,self.numUserZones): # in case the last zones were not measured
               dataList[zn] = meas2 - ((meas2 - meas1) * (zn2 - zn) / (zn2 - zn1))
      return dataList
   #-------------------------------------------------------------------------------------------------------
   def lumpData_by_2ndOrderFit(self, znList, dataList):
      
      # Get 2nd order polynomial
      a, b, c = Fit_2ndOrder(znList, dataList)
      
      if a == -1 and b == -1 and c == -1:
         objMsg.printMsg('Unable to filter by 2nd order')
      else:
         evalData = list(dataList) # make another copy of the list that will be used for iteration
         evalZone = list(znList) # make another copy of the list that will be used for iteration
         errorZones = [] # list to store detected anomalous zone
         iter = 0 # keep iteration counter  for debug
         while 1:
            if verbose: objMsg.printMsg('evalZone %s' % evalZone)
            if verbose: objMsg.printMsg('evalData %s' % evalData)
            contEval = False
            goodData = []
            goodZone = []
            for item in range(len(evalZone)):
               fittedData = (a * evalZone[item] * evalZone[item]) + (b * evalZone[item]) + c
               if abs(fittedData - evalData[item]) < 0.15: # hard code criteria for now in detecting anomalous zone
                  goodZone.append(evalZone[item])
                  goodData.append(evalData[item])
                  if verbose: objMsg.printMsg('zn %d fittedData  %.4f  evalData %.4f' % (evalZone[item], fittedData, evalData[item]))
               else:
                  contEval = True
                  errorZones.append(znList[item])
                  printDbgMsg('zn %d fittedData  %.4f  evalData %.4f FitError > 0.15' % (evalZone[item], fittedData, evalData[item]))
            
            if verbose: 
               objMsg.printMsg('iter %d goodZone %s' % (iter, goodZone))
               objMsg.printMsg('iter %d goodData %s' % (iter, goodData))
               objMsg.printMsg('iter %d errorZones %s' % (iter, errorZones))
            
            if contEval == True and len(goodData) > 6: # need at least 6 zones to fit, another bit of hard code here
               a, b, c = Fit_2ndOrder(goodZone, goodData)  #recalculate polynomials for next iteration
               # Update the Eval Data and Zone for next iteration
               evalData = list(goodData)
               evalZone = list(goodZone)
            else: break # exit the loop
            iter += 1
            
         if len(errorZones): # if there are any zones detected as anomalous
            for item in range(len(znList)):
               if znList[item] in errorZones:
                  dataList[item] = (a * znList[item] * znList[item]) + (b * znList[item]) + c # replace data with the final polynomial
         if verbose: objMsg.printMsg('final 2nd_order Filtered Data %s' % dataList)
         
      return dataList
   #-------------------------------------------------------------------------------------------------------
   def quadraticMedianfilter(self, dataList):

      finalList = []
      finalList.extend(dataList)
      filterList = []
      filterList.extend(dataList)
      objMsg.printMsg('finalList1:%s' % finalList)
      #first do 5 point median filter
      for index in range(len(dataList)):
         temparray=[]
         if index == 0:
            filterList[index] = dataList[index]
         elif index == 1:
            temparray.append(dataList[0])
            for index2 in range (1,5):
               temparray.append(dataList[index2])
            temparray.sort()
            filterList[index]=float(temparray[2])
         elif index == (len(dataList) -2):
            for index2 in range(0,4):
               temparray.append(dataList[len(dataList)-index2-2])
            temparray.append(dataList[len(dataList)-1])
            temparray.sort()
            filterList[index]=float(temparray[2])
         elif index == (len(dataList) -1):
            filterList[index] = dataList[index]
         else:
            for index2 in range(0,5):
               temparray.append(dataList[index + index2 - 2])
            temparray.sort()
            filterList[index]=float(temparray[2])
         #now make quadratic equation of filtered values
         N=0
         s1=0
         s2=0
         s3=0
         s4=0
         t1=0
         t2=0
         t3=0
      objMsg.printMsg('filterList2:%s' % filterList)
      for index in range(len(dataList)):
         N=N+1
         s1=s1+index
         s2=s2+index*index
         s3=s3+index*index*index
         s4=s4+index*index*index*index
         t1=t1+float(filterList[index])
         t2=t2+index*float(filterList[index])
         t3=t3+index*index*float(filterList[index])
      d=N*s2*s4 - N*s3*s3 - s1*s1*s4 - s2*s2*s2 + 2*s1*s2*s3
      A=(N*s2*t3 - N*s3*t2 - s1*s1*t3 - s2*s2*t1 + s1*s2*t2 + s1*s3*t1)/d
      B=(N*s4*t2 - N*s3*t3 - s2*s2*t2 - s1*s4*t1 + s1*s2*t3 + s2*s3*t1)/d
      C=(s1*s3*t3 -s1*s4*t2 -s2*s2*t3 - s3*s3*t1 + s2*s3*t2 + s2*s4*t1)/d
      #apply equation to all values
      for index in range(len(dataList)):
         finalList[index]=A*index*index+B*index+C
      objMsg.printMsg('finalList2:%s' % finalList)
      return finalList
   #-------------------------------------------------------------------------------------------------------

   def dump_zone_data(self, hd, zn, target_index, direction, tpi_sss, effectiveTpic, effectiveADC, adc_cmr, adc_smr, ReadOffset, meas_data, bpic):
      printDbgMsg('%2d  %-2d  %.4f  %.4f  %.4f   %.4f   %.4f   %s   %.4f   %.4f   %.4f   %.4f   %.4f       %-2d' %
      (hd, zn, TP.Target_SFRs[target_index], bpic, meas_data['TPI_DSS' + str(target_index)], meas_data['TPI_IDSS' + str(target_index)], meas_data['TPI_ODSS' + str(target_index)], direction, tpi_sss, effectiveTpic, effectiveADC, adc_cmr, adc_smr, ReadOffset))

      curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
      occurrence = 0  # reset the occurrence so we can avoid PK issues.
      dblog_record = {
                  'SPC_ID'          : 1,
                  'OCCURRENCE'      : occurrence,
                  'SEQ'             : curSeq,
                  'TEST_SEQ_EVENT'  : testSeqEvent,
                  'HD_PHYS_PSN'     : self.dut.LgcToPhysHdMap[hd],
                  'DATA_ZONE'       : zn,
                  'HD_LGC_PSN'      : hd,
                  'TARGET_SFR'      : round(TP.Target_SFRs[target_index], 4),
                  'BPIC'            : round(bpic, 4),
                  'TPI_DSS'         : round(meas_data['TPI_DSS' + str(target_index)], 4),
                  'TPI_IDSS'        : round(meas_data['TPI_IDSS' + str(target_index)], 4),
                  'TPI_ODSS'        : round(meas_data['TPI_ODSS'+ str(target_index)], 4),
                  'TPI_EFF'         : round(effectiveTpic, 4),
                  'ADC_EFF'         : round(effectiveADC, 4),
                  'ADC_CMR'         : round(adc_cmr, 4),
                  'ADC_SMR'         : round(adc_smr, 4),
                  'RD_OFFSET'       : ReadOffset,
                  'DIR'             : direction,
      }
      self.dut.dblData.Tables('P_VBAR_2D_SUMMARY').addRecord(dblog_record)

class CMeasureBPIAndTPIinAllZones_2DVBAR(CMeasureBPIAndTPIinAllZones):
   def __init__(self, measurements, measureBPIOnly = 0):
      CMeasureBPIAndTPIinAllZones.__init__(self, measurements)
      self.measureBPIOnly =  measureBPIOnly

   #overrriding original function
   def measureBPIAndTPI(self, znLst, zapOTF=0):
      import math

      znLst.sort()
      if self.measureBPIOnly:
         dbl_table_parse = 'P211_BPI_CAP_AVG'
         col_bpic        = 'BPI_CAP_AVG'
         zero_heat_col   = 'ZERO_HEAT_CLR'
      else:
         dbl_table_parse = 'P211_WRT_PWR_TBL'
         col_bpic        = 'BPICAP'
         zero_heat_col   = 'ZEROHEATCLR'

      if (testSwitch.extern.SRC_11K_M):
         table_BPI_MSR = 'P211_M11K_BPI_MEASUREMENT'
      elif testSwitch.MARVELL_SRC:
         table_BPI_MSR = 'P211_M_BPI_MEASUREMENT'
      else: #karnak 
         table_BPI_MSR = 'P211_BPI_MEASUREMENT'
      
      hdMask = 0
      for hd in range(self.numHeads):
         hdMask |= 1 << hd
      cword1 = self.measureBPIOnly and 0x0001 or 0x0003

      prm = {
             'test_num'           : 211,
             'prm_name'           : 'Measure_BPI',
             'timeout'            : 3600 * ( 1 + self.numHeads/2),
             'spc_id'             : 0,
             'NUM_TRACKS_PER_ZONE': 6,
             'ZONE_POSITION'      : TP.VBAR_ZONE_POS,
             'BPI_MAX_PUSH_RELAX' : TP.VbarBpiMaxPushRelax,
             'NUM_SQZ_WRITES'     : TP.num_sqz_writes,
             'HEAD_RANGE'         : hdMask,
             'CWORD1'             : cword1,   #refer to cword1 variable declared above
             'CWORD2'             : 0x2010,   # turn on BIE in BPI capability measurement & turn off feed forward
             'ADJ_BPI_FOR_TPI'    : TP.VbarAdjBpiForTpi,
             'DblTablesToParse'   : [dbl_table_parse],
             'TARGET_SER'         : TP.VbarTargetSER,
             'TPI_TARGET_SER'     : 5,
             'TPI_TLEVEL'         : TP.TPI_TLEVEL,
             'TLEVEL'             : 0,
             'THRESHOLD'          : 65,
             'RESULTS_RETURNED'   : 0,
      }
      
      if testSwitch.CM_REDUCTION_REDUCE_PRINTMSG:
         prm['RESULTS_RETURNED'] = prm['RESULTS_RETURNED'] | 0x000E

      if not testSwitch.extern.BF_0168996_007867_VBAR_REPLACE_INACCURATE_WP_TBL:
         # Oops, still older firmware - still using older table.
         prm['DblTablesToParse'] = ['P211_WP_TBL']

      if self.opMode == 'AllZones':
         prm.update(getattr(TP, 'MeasureBPITPI_ZN_211', {}))
      else:
         prm.update(getattr(TP, 'MeasureBPITPI_WP_211', {}))

      if not self.opMode == 'AllZones':
         prm['CWORD1'] |= 0x0100 #use wp from (dlfile)rather from memory.
         #prepare write power triplets to be sent to the drive
         RegisterResultsCallback(self.processMemoryDataAsPCFile, [81,], 0)

      if zapOTF == 1:
         prm.update(TP.prm_ZAP_OTF)
         prm['CWORD1'] |= 0x800
         prm['TRACK_LIMIT'] = 0x0101
         prm['timeout'] = 3*prm['timeout']/2

      try: bpiMeasIndex = len(self.dut.dblData.Tables(table_BPI_MSR))
      except: bpiMeasIndex = 0
      if testSwitch.virtualRun: bpiMeasIndex = 0
      objMsg.printMsg('bpiMeasIndex %d' % bpiMeasIndex)
      if testSwitch.FAST_2D_VBAR_2DIR_SWEEP:
         prm['TARGET_SER'] = 63 # Trigger Poorer Target SFR first
         prm['prm_name'] = 'MeasureBPI_%.2f' % (math.log10(prm['TARGET_SER']/10000.0))
         # Run the test
         if not testSwitch.VBAR_2D_DEBUG_MODE:
            if testSwitch.extern.FE_0284077_007867_SGL_CALL_250_ZN_VBAR_SUPPORT:
               prm['ZONE_MASK_BLOCK'] = self.oUtility.setZoneMaskBlock(znLst)
               getVbarGlobalClass(CProcess).St(prm)
            else:
               MaskList = self.oUtility.convertListToZoneBankMasks(znLst)
               for bank,zlist in MaskList.iteritems():
                  if zlist:
                     prm ['ZONE_MASK_EXT'], prm ['ZONE_MASK'] = self.oUtility.convertListTo64BitMask(zlist)
                     if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
                        prm ['ZONE_MASK_BANK'] = bank
                     getVbarGlobalClass(CProcess).St(prm)
         else:
            objMsg.printMsg('[211] 2D BPIC TEST TARGET_SER 63###########################')

         prm['TARGET_SER'] = 12 # Then Trigger Better Target SFR
         prm.update({'spc_id' : 12,})
         prm['prm_name'] = 'MeasureBPI_%.2f' % (math.log10(prm['TARGET_SER']/10000.0))
      # Run the test
      if not testSwitch.VBAR_2D_DEBUG_MODE:
         if testSwitch.extern.FE_0284077_007867_SGL_CALL_250_ZN_VBAR_SUPPORT:
            prm['ZONE_MASK_BLOCK'] = self.oUtility.setZoneMaskBlock(znLst)
            getVbarGlobalClass(CProcess).St(prm)
         else:
            MaskList = self.oUtility.convertListToZoneBankMasks(znLst)
            for bank,zlist in MaskList.iteritems():
               if zlist:
                  prm ['ZONE_MASK_EXT'], prm ['ZONE_MASK'] = self.oUtility.convertListTo64BitMask(zlist)
                  if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
                     prm ['ZONE_MASK_BANK'] = bank
                  getVbarGlobalClass(CProcess).St(prm)
      else:
         objMsg.printMsg('[211] 2D BPIC TEST TARGET_SER 12##############################')
         self.Dummy_dblog_data()
         for hd in xrange(self.numHeads):
            for zn in znLst:
               self.measurements.setRecord('BPI', 1, hd, zn)
               self.measurements.setRecord('TPI', 1, hd, zn)

      table = self.dut.dblData.Tables(dbl_table_parse).chopDbLog('SPC_ID', 'match',str(prm['spc_id']))
      colName = 'HD_LGC_PSN'

      for record in table:
         hd = int(record.get(colName)) #hd = int(record[colName])
         zn = int(record.get('DATA_ZONE')) #zn = int(record['DATA_ZONE'])

         _wp = self.opMode == 'WpZones' and int(record.get('WPOWER')) or None
         meas = CVbarDataHelper(self.measurements, hd, zn, _wp)
         meas['BPI'] = self.formatScaler.scaleBPI(hd, zn, float(record[col_bpic]))
         if testSwitch.BPICHMS:
            meas['BPIR'] = self.formatScaler.scaleBPI(hd, zn, float(record[col_bpic]))
         if not self.measureBPIOnly :
            meas['TPI'] = self.formatScaler.scaleTPI(hd, zn, float(record['TPICAP']))
         meas['Interp'] = 'F'

      # Get the BER vs BPIC Slope
      colDict4 = self.dut.dblData.Tables(table_BPI_MSR).columnNameDict()
      table4 = self.dut.dblData.Tables(table_BPI_MSR).rowListIter(index=bpiMeasIndex)
      bpi_by_hd_zn = list(list(list() for zn in znLst) for i in xrange(self.numHeads))
      ber_by_hd_zn = list(list(list() for zn in znLst) for i in xrange(self.numHeads))
      if testSwitch.FAST_2D_VBAR_XFER_PER_HD:
         bpi_by_hd = list(list() for i in xrange(self.numHeads))
         ber_by_hd = list(list() for i in xrange(self.numHeads))

      if verbose: debugStr = "" #empty Str
      if verbose: debugStr += "SlopeData\n"
      if verbose: debugStr += "Hd    Zn      Track      BPI       BPIS       SOVA_BER\n"
      # loop through table
      for row in table4:
         if not float(row[colDict4['SECTOR_ERROR_RATE']]): continue   #prevent math error
         zn = int(row[colDict4['DATA_ZONE']])
         try:
            idx = znLst.index(zn)
         except ValueError:
            continue
         hd = int(row[colDict4['HD_LGC_PSN']])
         trk = int(row[colDict4['TRK_NUM']])
         bpi_pct = 1.0 + float(row[colDict4['DELTA_BPI_PCT']]) / 100
         bpi_pct_s = self.formatScaler.scaleBPI(hd, zn, bpi_pct)
         ser_log = math.log10(float(row[colDict4['SECTOR_ERROR_RATE']]))
         bpi_by_hd_zn[hd][idx].append(bpi_pct_s)
         ber_by_hd_zn[hd][idx].append(ser_log)
         if verbose: debugStr += "%d    %2d       %5d   %3.4f     %3.4f        %3.4f\n" \
                                 % (hd, zn, trk, bpi_pct, bpi_pct_s, ser_log)   
      # loop through hd, zn
      for hd in xrange(self.numHeads):
         for idx, zn in enumerate(znLst):
            meas = CVbarDataHelper(self.measurements, hd, zn)
            meas['BPISlope'], meas['BPIConst'], meas['RSq'] = linreg(ber_by_hd_zn[hd][idx], bpi_by_hd_zn[hd][idx])
            if testSwitch.FAST_2D_VBAR_XFER_PER_HD:
               if meas['RSq'] > 0.9: #improve slope of hd in order more accurate bpic
                  bpi_by_hd[hd].extend(bpi_by_hd_zn[hd][idx])
                  ber_by_hd[hd].extend(ber_by_hd_zn[hd][idx])
         if testSwitch.FAST_2D_VBAR_XFER_PER_HD:
            BPISlope, BPIConst, RSq = linreg(ber_by_hd[hd], bpi_by_hd[hd])
            for zn in xrange(self.numUserZones):
               meas = CVbarDataHelper(self.measurements, hd, zn)
               meas['BPISlopeHd'], meas['BPIConstHd'], meas['RSqHd'] = BPISlope, BPIConst, RSq
      
      if verbose: objMsg.printMsg('%s' % debugStr) #cut the log size
      printDbgMsg('==========================================')
      printDbgMsg('Hd        Slope          Constant        Rsq')
      for hd in xrange(self.numHeads):
         meas = CVbarDataHelper(self.measurements, hd, 0)
         printDbgMsg('%d    %4.8f        %4.8f     %3.4f' % (hd, meas['BPISlopeHd'], meas['BPIConstHd'], meas['RSqHd']))

      printDbgMsg('==========================================')
      printDbgMsg('Hd    Zn         Slope          Constant        Rsq')
      for hd in xrange(self.numHeads):
         for zn in znLst:
            meas = CVbarDataHelper(self.measurements, hd, zn)
            printDbgMsg('%d    %2d     %4.8f        %4.8f     %3.4f' % (hd, zn, meas['BPISlope'], meas['BPIConst'], meas['RSq']))

      # Display results
      hdzns = [(hd,zn) for hd in range(self.numHeads) for zn in znLst]
      self.printMeasurements(hdzns)

      return self.measurements

   def measureSQZBPIC(self, znLst):
      #Run adjacent write b4 measurement to correlate b4 and after
      if not testSwitch.FE_0299849_356688_P_CM_REDUCTION_REDUCE_PRINT:
         prm_sqz_write = TP.prm_PrePostOptiAudit_250_2.copy()
         prm_sqz_write.update({'CWORD2': prm_sqz_write['CWORD2'] & 0xF7FF}) #do not  reset read offset
         if not testSwitch.FAST_2D_VBAR_TESTTRACK_CONTROL:
            prm_sqz_write.update({'CWORD2': prm_sqz_write['CWORD2'] | 0x1000}) # turn on test track mode
         prm_sqz_write['NUM_SQZ_WRITES'] = 1
         prm_sqz_write.update({'spc_id':400})
         prm_sqz_write.update({'MINIMUM' :  -10}) #fail safe
         prm_sqz_write.update({'CWORD1': prm_sqz_write['CWORD1'] | 0x4000}) # Squeeze Write
      
         SetFailSafe()
         MaskList = self.oUtility.convertListToZoneBankMasks(znLst)
         for bank,list in MaskList.iteritems():
            if list:
               prm_sqz_write['ZONE_MASK_EXT'], prm_sqz_write['ZONE_MASK'] = self.oUtility.convertListTo64BitMask(list)
               if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
                  prm_sqz_write['ZONE_MASK_BANK'] = bank
               getVbarGlobalClass(CProcess).St(prm_sqz_write)
         ClearFailSafe()

      hdMask = 0
      for hd in range(self.numHeads):
         hdMask |= 1 << hd

      prm_SQZBPI = {
          'test_num'           : 211,
          'prm_name'           : 'Measure SQZBPIC',
          'timeout'            : 3600 * ( 1 + self.numHeads/2),
          'spc_id'             : 0,
          'NUM_TRACKS_PER_ZONE': 6,
          'ZONE_POSITION'      : TP.VBAR_ZONE_POS,
          'BPI_MAX_PUSH_RELAX' : TP.VbarBpiMaxPushRelax,
          'NUM_SQZ_WRITES'     : TP.num_sqz_writes,
          #'ZONE_MASK'          : self.oUtility.ReturnTestCylWord(zone_mask_low),
          #'ZONE_MASK_EXT'      : self.oUtility.ReturnTestCylWord(zone_mask_high),
          'HEAD_RANGE'         : hdMask,
          'CWORD1'             : 0x0001,   #refer to cword1 variable declared above
          'CWORD2'             : 0x0010,   # turn on BIE in BPI capability measurement
          'ADJ_BPI_FOR_TPI'    : TP.VbarAdjBpiForTpi,
          'DblTablesToParse'   : ['P211_BPI_CAP_AVG'],
          'TARGET_SER'         : TP.SQZBPI_SER,# defined inside TestParameter.py
          'TLEVEL'             : 0,
          'THRESHOLD'          : 65,
          'RESULTS_RETURNED'   : 0,
          'CWORD3'             : 0x0008, #turn on test track control
          'ASYMMETRIC_SQZ_WRT_CNT': (1, 0), #adjacent write
          'ASYMMETRIC_SQZ_OFFSET': (0, 0), #zero offset
      }
      
      if testSwitch.CM_REDUCTION_REDUCE_PRINTMSG:
         prm_SQZBPI['RESULTS_RETURNED'] = prm_SQZBPI['RESULTS_RETURNED'] | 0x000E
         
      # Ignore the previous records
      table = DBLogReader(self.dut, 'P211_BPI_CAP_AVG', suppressed = True)
      table.ignoreExistingData()

      if testSwitch.FAST_2D_VBAR_TESTTRACK_CONTROL:
         prm_SQZBPI['CWORD3'] = prm_SQZBPI['CWORD3'] | 0x0008 #turn on test track control
      else:
         prm_SQZBPI['CWORD3'] = prm_SQZBPI['CWORD3'] & 0xFFF7 #turn off test track control

      MaskList = self.oUtility.convertListToZoneBankMasks(znLst)
      for bank,list in MaskList.iteritems():
         if list:
            prm_SQZBPI['ZONE_MASK_EXT'], prm_SQZBPI['ZONE_MASK'] = self.oUtility.convertListTo64BitMask(list)
            if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
               prm_SQZBPI['ZONE_MASK_BANK'] = bank
            getVbarGlobalClass(CProcess).St(prm_SQZBPI)
            self.update_sqzBPITable(table)

      if not testSwitch.CM_REDUCTION_REDUCE_PRINTDBLOGBIN:
         objMsg.printDblogBin(self.dut.dblData.Tables('P_SQZ_BPIC_SUMMARY'))
      
   def update_sqzBPITable(self, table):
      # init for table P_SQZ_BPIC_SUMMARY
      self.spcIdHlpr.getSetIncrSpcId('P_SQZ_BPIC_SUMMARY', startSpcId = 0, increment = 0, useOpOffset = 1)
      curSeq, occurrence, testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
      spcId = self.spcIdHlpr.getSpcId('P_SQZ_BPIC_SUMMARY')      

      for record in table.iterRows():
         hd = int(record.get('HD_LGC_PSN'))
         zn = int(record.get('DATA_ZONE'))
         meas = CVbarDataHelper(self.measurements, hd, zn)

         meas['SQZ_BPI'] = self.formatScaler.scaleBPI(hd, zn, float(record.get('BPI_CAP_AVG')))
         #compute bpic margin by using current bpip - sqzbpic
         bpimargin = meas['BPI'] - meas['SQZ_BPI']
         self.dut.dblData.Tables('P_SQZ_BPIC_SUMMARY').addRecord(
         {
                     'SPC_ID'          : spcId,
                     'OCCURRENCE'      : occurrence,
                     'SEQ'             : curSeq,
                     'TEST_SEQ_EVENT'  : testSeqEvent,
                     'HD_PHYS_PSN'     : self.dut.LgcToPhysHdMap[hd],
                     'DATA_ZONE'       : zn,
                     'BPIC'            : "%.5f" % meas['BPI'],
                     'SQZBPIC'         : "%.5f" % meas['SQZ_BPI'],
                     'BPIM'            : "%.5f" % bpimargin,
         })
         
class CMeasureBPIAndTPIinAllZones_UnvisitedZones(CMeasureBPIAndTPIinAllZones_2DVBAR):
   def __init__(self, measurements, measureBPIOnly = 0):
      CMeasureBPIAndTPIinAllZones_2DVBAR.__init__(self, measurements, measureBPIOnly)

   def quadraticMedianfilter(self, dataList, Fit_2ndOrder = 1):

      finalList = []
      finalList.extend(dataList)
      filterList = []
      filterList.extend(dataList)
      if verbose: objMsg.printMsg('finalList1:%s' % finalList)
      if testSwitch.FE_0253509_348429_UVZ_IMPROVE_FILTERING1 or testSwitch.FE_0289797_348429_ZONE_ALIGN_IMPROVE_FILTERING:
         skip_index_lst = [0, 1, (len(dataList) -2), (len(dataList) -1)] # skip first 2 and last 2 data
      else:
         skip_index_lst = [0, (len(dataList) -1)] # skip first and last data
      #first do 5 point median filter
      for index in range(len(dataList)):
         temparray=[]
         if index in skip_index_lst: # handle those skip zones first, copy same as original data
            filterList[index] = dataList[index]
         elif index == 1:
            temparray.append(dataList[0])
            for index2 in range (1,5):
               temparray.append(dataList[index2])
            temparray.sort()
            filterList[index]=float(temparray[2])
         elif index == (len(dataList) -2):
            for index2 in range(0,4):
               temparray.append(dataList[len(dataList)-index2-2])
            temparray.append(dataList[len(dataList)-1])
            temparray.sort()
            filterList[index]=float(temparray[2])
         elif index == (len(dataList) -1):
            filterList[index] = dataList[index]
         else:
            for index2 in range(0,5):
               temparray.append(dataList[index + index2 - 2])
            temparray.sort()
            filterList[index]=float(temparray[2])
      #now make quadratic equation of filtered values
      N=0
      s1=0
      s2=0
      s3=0
      s4=0
      t1=0
      t2=0
      t3=0
      if verbose: objMsg.printMsg('filterList2:%s' % filterList)
      if Fit_2ndOrder == 0:
         return filterList
      for index in range(len(dataList)):
         N=N+1
         s1=s1+index
         s2=s2+index*index
         s3=s3+index*index*index
         s4=s4+index*index*index*index
         t1=t1+float(filterList[index])
         t2=t2+index*float(filterList[index])
         t3=t3+index*index*float(filterList[index])
      d=N*s2*s4 - N*s3*s3 - s1*s1*s4 - s2*s2*s2 + 2*s1*s2*s3
      A=(N*s2*t3 - N*s3*t2 - s1*s1*t3 - s2*s2*t1 + s1*s2*t2 + s1*s3*t1)/d
      B=(N*s4*t2 - N*s3*t3 - s2*s2*t2 - s1*s4*t1 + s1*s2*t3 + s2*s3*t1)/d
      C=(s1*s3*t3 -s1*s4*t2 -s2*s2*t3 - s3*s3*t1 + s2*s3*t2 + s2*s4*t1)/d
      #apply equation to all values
      for index in range(len(dataList)):
         finalList[index]=A*index*index+B*index+C
      if verbose:objMsg.printMsg('finalList2:%s' % finalList)
      return finalList

   def filterMeasurements (self, BpiOrTpi='TPI', base_zn_list = [], Fit_2ndOrder = 1, save_zn_list = [], input_data = [], input_hd = -1):
      if len(base_zn_list) == 0: # set all zones if base zone is empty
         base_zn_list = range(self.numUserZones)
      base_zn_list = sorted(base_zn_list) #force to sorted, order of zone is important

      if len(save_zn_list) == 0: # set all zones if save zone is empty
         save_zn_list = range(self.numUserZones)
      save_zn_list = sorted(save_zn_list) #force to sorted, order of zone is important

      if verbose:
         objMsg.printMsg('base_zn_list:%s' % base_zn_list)
         objMsg.printMsg('save_zn_list:%s' % save_zn_list)
         
      if input_hd == -1: # set all heads if no input head given
         hd_range = xrange(self.numHeads)
      else:
         hd_range = [input_hd]

      for hd in hd_range:
         dataList = [] # this will contain data for all zones, those not in base zone will be placed in -1 value
         base_dataList = [] # this will contain data for zones in base zone list only, use for filtering in FE_0289797_348429_ZONE_ALIGN_IMPROVE_FILTERING
         if input_hd == -1:
            for zn in range(self.numUserZones):
               if zn in base_zn_list:
                  meas = self.measurements.getRecord(BpiOrTpi, hd, zn) # get the data from record
                  dataList.append(meas)
                  base_dataList.append(meas)
               else:
                  dataList.append(-1.0)
         else:
            dataList.extend(input_data)
            for zn in xrange(self.numUserZones):
               if zn in base_zn_list: 
                  base_dataList.append(dataList[zn]) # build the base_dataList from input_data

         if verbose: objMsg.printMsg('hd %d dataList %s :%s' % (hd, BpiOrTpi, dataList))
         if testSwitch.FE_0289797_348429_ZONE_ALIGN_IMPROVE_FILTERING:
            dataList_raw = list(dataList) # for Printing
            #########################################################
            # 2nd order fit to filter extreme out of range values   #
            #########################################################
            if BpiOrTpi.upper() in ['TPI','TPI_DSS','TPI_IDSS','TPI_ODSS']: # applies only to TPI related metric
               base_dataList = self.lumpData_by_2ndOrderFit(base_zn_list, base_dataList)
               if verbose: objMsg.printMsg('hd %d base_dataList2ndorder %s :%s' % (hd, BpiOrTpi, base_dataList))
               for item in range(len(base_zn_list)): #Update only base data
                  dataList[base_zn_list[item]] = base_dataList[item]
            dataList_2ndorder = list(dataList) # for Printing
            if verbose: objMsg.printMsg('hd %d dataList_2ndorder %s :%s' % (hd, BpiOrTpi, dataList_2ndorder))
            
            #####################################
            #   median filter for finer values  #
            #####################################
            base_dataList = self.quadraticMedianfilter(base_dataList, Fit_2ndOrder = Fit_2ndOrder)
            if verbose: objMsg.printMsg('hd %d base_dataListMedia %s :%s' % (hd, BpiOrTpi, base_dataList))
            for item in range(len(base_zn_list)): #Update only base data
               dataList[base_zn_list[item]] = base_dataList[item]
            dataList_median = list(dataList) # for Printing
            if verbose: objMsg.printMsg('hd %d dataList_median %s :%s' % (hd, BpiOrTpi, dataList_median))
            
            ########################################
            # linear fit for the unmeasured zones  #
            ########################################
            filteredList = self.linear_fit(base_zn_list, dataList)
            
            # print for debug, turn on for now
            printDbgMsg('%s Filtered Results' % (BpiOrTpi))
            printDbgMsg('hd    zn     Raw_Data  2ndOrder_Fit  Median_Fit   Linear_fit   Save_Zone')
            for zn in range(self.numUserZones):
               save_zone = (zn in save_zn_list) and 'Y' or 'N'
               printDbgMsg(' %d   %3d   %10.4f   %10.4f   %10.4f   %10.4f   %s' % (hd, zn, dataList_raw[zn], dataList_2ndorder[zn], dataList_median[zn], filteredList[zn], save_zone))
         else:
            if len(base_zn_list) != self.numUserZones:
               dataList = self.linear_fit(base_zn_list, dataList)
               objMsg.printMsg('dataList2 %s :%s' % (BpiOrTpi,dataList))
            if testSwitch.FE_0253509_348429_UVZ_IMPROVE_FILTERING1:
               lumpRequired, lumpedData = self.lumpData_by_mean(BpiOrTpi, dataList)
            else:
               lumpRequired, lumpedData = self.lumpData(BpiOrTpi, dataList)
            
            filteredList = self.quadraticMedianfilter(lumpedData, Fit_2ndOrder = Fit_2ndOrder)
            
         if input_hd == -1:
            for zn in save_zn_list:
               self.measurements.setRecord(BpiOrTpi, filteredList[zn], hd, zn)

         #### fix virtual run script msg ####
         if testSwitch.virtualRun and (self.numUserZones-1 not in save_zn_list):
            self.measurements.setRecord(BpiOrTpi, filteredList[self.numUserZones-1], hd, self.numUserZones-1)

         if input_hd != -1: # return the filtered data
            return filteredList

   def copyTarget_SOVA_2_Unvisited_Zone(self, znLst, tracksPerBand):
      for hd in xrange(self.numHeads):
         for zn in xrange(self.numUserZones):
            if zn in znLst:
               continue
            meas = CVbarDataHelper(self.measurements, hd, zn)
            if testSwitch.FAST_2D_VBAR_UMP_FIX_BEST_TARGET_SOVA_BER and tracksPerBand[zn] == 1:
               meas['TGT_SFR_IDX'] = 0 # lets fix to zero, the data can be later filtered measurements
               continue # there is no data for this zone

            meas['TGT_SFR_IDX'] = self.BestTargetSFRIndex_Hd[hd]
            meas['BPI'] = self.getBPI_from_Xfer(hd,zn,meas['TGT_SFR_IDX'])

   def handleUMPZones(self, znLst, meas_2D, tracksPerBand):
      if not testSwitch.FAST_2D_VBAR_UMP_FIX_BEST_TARGET_SOVA_BER:
         return
      self.param_list += ['BPI']
      # This will linearly interpolate data for UMP ZOnes Using target sfr index zero
      for hd in xrange(self.numHeads):
         for param in self.param_list:
            if param != 'BPI':
               dataList = []
               for zn in xrange(self.numUserZones):
                  if zn in znLst:
                     meas_idx = meas_2D[hd,zn]
                     #if param != 'BPI':
                     dataList.append(meas_idx[param + '0'])
                     #else:
                     #   bpic = self.getBPI_from_Xfer(hd,zn,0)
                     #   dataList.append(bpic)
                  else:
                     dataList.append(-1)
               if verbose:
                  objMsg.printMsg('dataListA %s :%s' % (param,dataList))

               for index in range(len(znLst)-1):
                  zn1 = znLst[index]
                  zn2 = znLst[index + 1]
                  if zn1 + 1 != zn2: # Zones are not consecutive
                     meas1 = dataList[zn1]
                     meas2 = dataList[zn2]
                     for zn in range(zn1,zn2):
                        dataList[zn] = meas2 - ((meas2 - meas1) * (zn2 - zn) / (zn2 - zn1))
                  if index == 0 and zn1 != 0:
                     for zn in range(0,zn1): # in case the first zones were not measured
                        dataList[zn] = meas2 - ((meas2 - meas1) * (zn2 - zn) / (zn2 - zn1))
                  elif index == len(znLst)-2 and zn2 != self.numUserZones - 1:
                     for zn in range(zn2,self.numUserZones): # in case the last zones were not measured
                        dataList[zn] = meas2 - ((meas2 - meas1) * (zn2 - zn) / (zn2 - zn1))
               if verbose:
                  objMsg.printMsg('dataListB %s :%s' % (param,dataList))
            for zn in xrange(self.numUserZones):
               if tracksPerBand[zn] == 1:
                  meas = CVbarDataHelper(self.measurements, hd, zn)
                  if param != 'BPI':
                     meas[param] = dataList[zn]
                  else: meas[param] = self.getBPI_from_Xfer(hd, zn, 0)
                  if verbose:
                     objMsg.printMsg('%s Zn %d :%4f' % (param, zn, meas[param]))

   def measureTPI_DSS_UMP(self, ump_zones):
      from base_SerialTest import CRdOpti
      for zn in ump_zones:
         #set low 0.7 tpic only for all heads
         track_pitch = [ int( (1/0.7) * Q0toQ15Factor) for hd in range(self.numHeads) ]

         prm_210  =    {'test_num':210, 'spc_id': 13,
                        'ZONE': zn<<8| zn, 'HEAD_MASK': 0xffff,
                        'SHINGLED_DIRECTION': [0]*16,
                        'CWORD2': 0x3B0,
                        'TRK_GUARD_TBL': [0]*16,
                        'MICROJOG_SQUEEZE': [0]*16,
                        'timeout': 1800,
                        'TRK_PITCH_TBL': track_pitch + [46811]*(16- self.numHeads),
                        'TRACKS_PER_BAND': [1]*16,
                        'CWORD1': 0x102}

         if not testSwitch.FE_0269922_348085_P_SIGMUND_IN_FACTORY:
            prm_210.update({
                 'dlfile': (CN, self.bpiFile.bpiFileName)
                  })

         getVbarGlobalClass(CProcess).St(prm_210)

      getVbarGlobalClass(CFSO).saveRAPSAPtoFLASH()
      objVbarOpti = CRdOpti(self.dut, {'ZONES': list( set(ump_zones) & set(TP.Unvisited_Zones) )})
      zapped_track_limit = 0x031E #zap range zoneposition-30, zoneposition+3
      objVbarOpti.optiZAP(ump_zones, trackLimit=zapped_track_limit)
      self.formatScaler.load() #reload format
      objMsg.printMsg("========= TPI_DSS UMP ================")
      for hd in xrange(self.numHeads): 
         for zn in xrange(self.numUserZones):
            if zn not in ump_zones:
               continue #skip the zone
            meas = CVbarDataHelper(self.measurements, hd, zn) #get measurement zone
            #measure tpi_dss with disable tpi feed foward scheme
            tpi_dss, dummyOffset = self.measureTPI(hd, zn, 1.0, meas['WP'], prm_override = {'NUM_SQZ_WRITES':TP.num_sqz_writes, 'CWORD2':0x2000, 'TPI_TLEVEL' : 10})
            #scale back the tpi_dss to nominal tpic
            tpi_dss = self.formatScaler.scaleTPI(hd, zn, tpi_dss)
            if tpi_dss: #avoid zero tpic_dss
               objMsg.printMsg("previous tpi_dss %s, measured tpi_dss %s, delta: %s ,hd %d, zn %d" \
                  %(str(meas['TPI']), str(tpi_dss), str(tpi_dss-meas['TPI']), hd, zn) )
               if testSwitch.FE_0267792_504159_USE_LOWER_KTPI_START_POINT_MEASUREMENT:
                  #Get the lowest from fitting tpic_dss and tpic_dss with lower ktpi start point measurement
                  if float(tpi_dss)- meas['TPI']> -0.07:
                     meas['TPI'] = min(float(tpi_dss), meas['TPI']) #Replace the tpic_dss with lower ktpi start point measurement
      objMsg.printMsg("========= END TPI_DSS UMP ================")

class CMeasureBPIAndTPIinAllZones_S2D(CMeasureBPIAndTPIinAllZones_UnvisitedZones):
   def __init__(self, measurements):
      CMeasureBPIAndTPIinAllZones_UnvisitedZones.__init__(self, measurements)
      self.param_list = ['TPI','TPI_DSS','TPI_ODSS','TPI_IDSS','RD_OFST_ODSS','RD_OFST_IDSS', 'TPI_IDSS2D','TPI_ODSS2D']
      self.header_title = 'Hd  Zn  TGT_SFR  BPI_2D  SQZ_DSS  SQZ_IDSS SQZ_ODSS  DIR   TPI_SSS  EFF_TPI  EFF_ADC  CMR_ADC  SMR_ADC  RD_OFST   SQZ_IDSS2D  SQZ_ODSS2D'

   def dump_zone_data(self, hd, zn, target_index, direction, tpi_sss, effectiveTpic, effectiveADC, adc_cmr, adc_smr, ReadOffset, meas_data, bpic):
      objMsg.printMsg('%2d  %-2d  %.4f  %.4f  %.4f   %.4f   %.4f   %s   %.4f   %.4f   %.4f   %.4f   %.4f       %-2d       %.4f     %.4f' %
      (hd, zn, TP.Target_SFRs[target_index], bpic, meas_data['TPI_DSS' + str(target_index)], meas_data['TPI_IDSS' + str(target_index)], meas_data['TPI_ODSS' + str(target_index)], direction, tpi_sss, effectiveTpic, effectiveADC, adc_cmr, adc_smr, ReadOffset, meas_data['TPI_IDSS2D' + str(target_index)], meas_data['TPI_ODSS2D' + str(target_index)]))

      curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
      occurrence = 0  # reset the occurrence so we can avoid PK issues.
      dblog_record = {
                  'SPC_ID'          : 1,
                  'OCCURRENCE'      : occurrence,
                  'SEQ'             : curSeq,
                  'TEST_SEQ_EVENT'  : testSeqEvent,
                  'HD_PHYS_PSN'     : self.dut.LgcToPhysHdMap[hd],
                  'DATA_ZONE'       : zn,
                  'HD_LGC_PSN'      : hd,
                  'TARGET_SFR'      : round(TP.Target_SFRs[target_index], 4),
                  'BPIC'            : round(bpic, 4),
                  'TPI_DSS'         : round(meas_data['TPI_DSS' + str(target_index)], 4),
                  'TPI_IDSS'        : round(meas_data['TPI_IDSS' + str(target_index)], 4),
                  'TPI_ODSS'        : round(meas_data['TPI_ODSS'+ str(target_index)], 4),
                  'TPI_EFF'         : round(effectiveTpic, 4),
                  'ADC_EFF'         : round(effectiveADC, 4),
                  'ADC_CMR'         : round(adc_cmr, 4),
                  'ADC_SMR'         : round(adc_smr, 4),
                  'RD_OFFSET'       : ReadOffset,
                  'DIR'             : direction,
      }
      self.dut.dblData.Tables('P_VBAR_2D_SUMMARY').addRecord(dblog_record)

   def measureSingleSidedTPI_S2D(self, prmOverride, hd, zn, wp, meas, target_index = ''):
      # TODO: test
      try:
         startIndex = len(self.dut.dblData.Tables('P211_TPI_MEASUREMENT2'))
      except:
         startIndex = 0
         pass
      prmOverride2 = prmOverride.copy()
      prmOverride2.update({'TPI_TLEVEL': TP.MaxIteration, 'TPI_TARGET_SER' : 30, 'RESULTS_RETURNED' : 0x0})

      prmOverride2['CWORD3'] = 0x8000
      prm_list = ['TPI_IDSS2D','TPI_ODSS2D']
      for prm in prm_list:
         if prm == 'TPI_IDSS2D':# do id single sided measurement
            prmOverride2.update({'NUM_SQZ_WRITES':0x8000 + TP.num_sqz_writes, 'CWORD2':8})
            prmOverride2.update({'prm_name'           : 'MeasureTPI_IDSS2D'})
         else:# do od single sided measurement
            prmOverride2.update({'NUM_SQZ_WRITES':0x4000 + TP.num_sqz_writes,'CWORD2':8})
            prmOverride2.update({'prm_name'           : 'MeasureTPI_ODSS2D'})
         if target_index == '':
            dummytpi, dummyrdoffset = self.measureTPI(hd,zn,1,wp,prm_override = prmOverride2)
         else:
            dummytpi, dummyrdoffset = self.measureTPI(hd,zn,1,wp,prm_override = prmOverride2, target_SFR = TP.Target_SFRs[int(target_index)])

         endIndex = len(self.dut.dblData.Tables('P211_TPI_MEASUREMENT2'))
         if endIndex != startIndex:
            startIndex = endIndex
            SQZ_PCT_LIST =[]
            DELTA_SER_LIST =[]
            colDict = self.dut.dblData.Tables('P211_TPI_MEASUREMENT2').columnNameDict()
            tpitable = self.dut.dblData.Tables('P211_TPI_MEASUREMENT2').rowListIter(index=startIndex)
            for row in tpitable:
               DELTA_SER = float(row[colDict['DELTA_SER']])
               if DELTA_SER > 0.01 and DELTA_SER < 1.0:
                  SQZ_PCT_LIST.append(float(row[colDict['SQZ_PCT']]))
                  DELTA_SER_LIST.append(math.log10(DELTA_SER))
            if len(SQZ_PCT_LIST):
               a,b,c = Fit_2ndOrder(DELTA_SER_LIST, SQZ_PCT_LIST)
               if a==-1 and b==-1 and c==-1:
                  meas[prm + target_index] = -1
               else:
                  SqzPctFin = 0.0
                  ErrRate = max(DELTA_SER_LIST)
                  while 1:
                     SqzPct = (a * ErrRate * ErrRate) + (b * ErrRate) + c
                     if ErrRate == max(DELTA_SER_LIST):
                        SqzPctFin = SqzPct
                     elif SqzPct > SqzPctFin:
                           break
                     else:
                        SqzPctFin = SqzPct
                     objMsg.printMsg('S2D_PDBG : Sqz %4f ErrRate %4f' % (SqzPctFin,ErrRate))
                     ErrRate -= 0.10
                     if ErrRate < -2.5: break

                  objMsg.printMsg('%s:%4f' % (prm, SqzPctFin))
                  #meas['TPI_IDSS2' + str(target_index)] = MathLib.SolveQuadratic(a,b,c)
                  meas[prm + target_index] = self.formatScaler.scaleTPI(hd,zn,float(1.0/(1.0-SqzPctFin)))
            else: meas[prm + target_index] = -1
            objMsg.printMsg('%s :%4f' % (prm, meas[prm + target_index]))

      return meas

###########################################################################################################
###########################################################################################################
class CDisplayBpiBinFile(CState):
   """
   Dump out bpi format versus bpic for SIF/Normal for reference
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params

      depList = []

      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      displayBPINominalTable(dumpTable = 1)

###########################################################################################################
###########################################################################################################
class CVariableBPINominal(CState):
   """
      Description:
         Nominal BPI index Optimization Routines for head start BPI index selection by head performance.
       so drvie can automatically select start Nominal BPI index by head average BPIC of OD,MD and ID with write power 2.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      CVBAR(self.params).BPINominalBHBZV2()

###########################################################################################################
###########################################################################################################
class CReloadBPINominal(CState):
   """
      Description:
         Nominal BPI index Optimization Routines for head start BPI index selection by head performance.
       so drvie can automatically select start Nominal BPI index by head average BPIC of OD,MD and ID with write power 2.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if self.params.has_key('FORMAT_TO_SET'):
         CVBAR().ReloadNewBpiNominalByHdByZn(self.params['FORMAT_TO_SET'])
      else:
         CVBAR().ReloadNewBpiNominalByHdByZn()
         
###########################################################################################################
###########################################################################################################
class CReloadZBNominal(CState):   
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):      
      CVBAR().ReloadZBNominal2RAP()

###########################################################################################################
###########################################################################################################
class CVBAR:
   """Master VBAR algorithm class"""
   def __init__(self, params={}):
      self.mFSO = getVbarGlobalClass(CFSO)
      self.mFSO.getZoneTable() # get number of heads and zones on drive
      self.dut = objDut

      self.numHeads = self.dut.imaxHead
      self.numUserZones = self.dut.numZones
      self.oUtility = getVbarGlobalClass(CUtility)
      self.objTestZones = CVbarTestZones()
      self.nibletIndex = 0
      self.objRapTcc = CRapTcc()
      self.NUM_WRITE_POWERS = self.objRapTcc.NUM_WRITE_POWERS
      self.params = dict(params)
      self.bpiFile = getVbarGlobalClass(CBpiFile)
      self.spcIdHlpr = getVbarGlobalClass(CSpcIdHelper, {'dut':self.dut})
      if debug_VE: objMsg.printMsg('frm CVBAR - self.numUserZones : %d' % self.numUserZones)
      # Load persistent data
      self.loadData()
      getVbarGlobalClass(CProcess).St({'test_num':210},CWORD1=(0x0020)) # Save BPI/TPI settings to PC file

      self.setMaxBPIWithClearance()

      # Set max TPI to avoid rolling over in the RAP
      global TPI_MAX
      TPI_MAX = min(TPI_MAX, 255.0 / self.bpiFile.getNominalTracksPerSerpent())
      if testSwitch.FAST_2D_VBAR:
         #Override to 2.0   # 2D_VBAR
         TPI_MAX = 2.0

   def getParam(self, name, default):
      value = self.params.get(name, default)

      if type(value) in (list, tuple):
         return value[self.dut.vbar_iterations]

      return value


   def loadData(self):
      if self.dut.vbar_wpmeas:
         self.measWPZns = CVbarWpMeasurement()
         self.measWPZns.buildStore(loadData=self.dut.vbar_wpmeas)
      else:
         self.measWPZns = CVbarWpMeasurement(initStore=True)

      if self.dut.vbar_znmeas:
         self.measAllZns = CVbarMeasurement()
         self.measAllZns.buildStore(loadData=self.dut.vbar_znmeas)
      else:
         self.measAllZns = CVbarMeasurement(initStore=True)

      if testSwitch.extern.FE_0164615_208705_T211_STORE_CAPABILITIES:
         # If the dut.wrPwrPick or meas dictionaries are currently empty, read up
         # the VBAR_DATA SIM file and use any data that may be preserved there.
         if not self.dut.wrPwrPick or not self.measAllZns.getStore():
            try:
               from SIM_FSO import CSimpleSIMFile
               data = CSimpleSIMFile("VBAR_DATA").read()
               wpp, storeData = cPickle.loads(data)

               if self.dut.wrPwrPick == {}:
                  self.dut.wrPwrPick = wpp

               if not self.measAllZns.getStore():
                  self.measAllZns.unserialize(storeData)

            except:
               objMsg.printMsg(traceback.format_exc())

      # Initialize WP picks if necessary
      if self.dut.wrPwrPick == {}:
         for hd in xrange(self.numHeads):
            self.dut.wrPwrPick[hd] = {}
            for zn in self.objTestZones.getTestZones():
               self.dut.wrPwrPick[hd][zn] = 100

   def saveData(self):
      self.dut.vbar_wpmeas = self.measWPZns.getStore()
      self.dut.vbar_znmeas = self.measAllZns.getStore()

      if testSwitch.extern.FE_0164615_208705_T211_STORE_CAPABILITIES:
         from SIM_FSO import CSimpleSIMFile
         objs = (self.dut.wrPwrPick, self.measAllZns.serialize())

         data = cPickle.dumps(objs, 2)
         CSimpleSIMFile("VBAR_DATA").write(data)

      if not testSwitch.FE_0134030_347506_SAVE_AND_RESTORE:
         self.dut.objData['vbar_wpmeas'] = self.dut.vbar_wpmeas

         self.dut.objData['vbar_znmeas'] = self.dut.vbar_znmeas

         self.dut.objData['wrPwrPick'] = self.dut.wrPwrPick

         if testSwitch.FE_0111183_340210_SAT_FAIL_MINIMAL_RETRY:
            self.dut.objData['satFail_HdsZns'] = self.dut.satFail_HdsZns


         self.dut.objData['vbar_iterations'] = self.dut.vbar_iterations

         self.dut.objData['BPIMarginThresholdAdjust']      = self.dut.BPIMarginThresholdAdjust
         self.dut.objData['TPIMarginThresholdAdjust']      = self.dut.TPIMarginThresholdAdjust

   def resetForWaterfall(self):
      # Reset iterations to 0
      self.dut.vbar_iterations = 0 # Reset for future states to use

      # Ensure the format picker is running
      self.params['FMT_PICKER'] = True

      # Save these changes for PLR
      self.saveData()

   def run(self):
      if verbose:
         dumpDebugData('VBAR-run()',self.measAllZns)
         if testSwitch.VBAR_2D_DEBUG_MODE:
            objMsg.printMsg('2D VBAR DEBUG DATA RESET')
            self.dut.vbar_znmeas = {}
            self.measAllZns.buildStore(loadData=self.dut.vbar_znmeas)

            dumpDebugData('VBAR-run()',self.measAllZns)

      # Set up unique spc_ids for each call, with a major/minor revisioning scheme.
      # Minor revision (001s digit) will be updated and major revision (100s digit)
      # will be inremented each time this function is run
      try:
         self.spcIdHlpr.incrementRevision('P058_STATUS', 100)  # Increment the major revision each time through this function
      except TypeError: # The first time through this function the spc_id won't exist, and we need to set the starting spc_id
         self.spcId = self.spcIdHlpr.getSetIncrSpcId('P058_STATUS', startSpcId = 100, increment = 1, useOpOffset = 1)

      if testSwitch.DISPLAY_SMR_FMT_SUMMARY:
         try:
            self.spcIdHlpr.incrementRevision('P_SMR_FORMAT_SUMMARY', 10)  # Increment the major revision each time through this function
         except TypeError: # The first time through this function the spc_id won't exist, and we need to set the starting spc_id
            self.spcId = self.spcIdHlpr.getSetIncrSpcId('P_SMR_FORMAT_SUMMARY', startSpcId = 20050, increment = 1, useOpOffset = 1)

      try:
         self.pick()
      except CRaiseException,exceptionData:
         objMsg.printMsg(traceback.format_exc())
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1) # power cycle in case drive was hung
         return self.nibletIndex, exceptionData[0][2]

      # reset drive after rap changes (if any)
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

      #Delete file pointers
      self.dut.dblData.Tables('P211_TPI_CAP_AVG').deleteIndexRecords(1)
      self.dut.dblData.Tables('P211_BPI_CAP_AVG').deleteIndexRecords(1)

      #Delete RAM objects
      self.dut.dblData.delTable('P211_TPI_CAP_AVG')
      self.dut.dblData.delTable('P211_BPI_CAP_AVG')

      return self.nibletIndex, ATPI_PASS

   def pick(self):
      #### BPI Nominal ####
      if self.getParam('BPI_NOM', False):
         if verbose:
            objMsg.printMsg('pick() parm:BPI_NOM')
         self.BPINominalBHBZV2()

      testZones = TP.VBAR_measured_Zones

      #### Niblet Loop ####
      status = ATPI_FAIL_NO_NIBLET
      for self.nibletIndex, nib in enumerate(TP.VbarNibletCluster):
         niblet = CNiblet(nib,self.params)
         # Relax margin thresholds if selected
         if self.getParam('NO_MARGIN_SPEC', False):
            if verbose:
               objMsg.printMsg('pick() parm:NO_MARGIN_SPEC')

            if testSwitch.BPICHMS or testSwitch.FE_CONSOLIDATED_BPI_MARGIN:
               for hd in xrange(self.numHeads):
                  for zn in xrange(self.numUserZones):
                     niblet.settings['BPIMarginThreshold'][hd][zn] = BPI_MIN - BPI_MAX
                     niblet.settings['TPIMarginThreshold'][zn] = TPI_MIN - TPI_MAX
            else:
               for zn in range(self.numUserZones):
                  niblet.settings['BPIMarginThreshold'][zn] = BPI_MIN - BPI_MAX
                  niblet.settings['TPIMarginThreshold'][zn] = TPI_MIN - TPI_MAX

         # Relax margin thresholds for HMS to control margins
         elif self.getParam('ADJ_MARGIN_SPEC', False):
            if verbose:
               objMsg.printMsg('pick() parm:ADJ_MARGIN_SPEC')
            if testSwitch.BPICHMS or testSwitch.FE_CONSOLIDATED_BPI_MARGIN:
               for hd in xrange(self.numHeads):
                  for zn in xrange(self.numUserZones):
                     niblet.settings['BPIMarginThreshold'][hd][zn] += niblet.settings['VbarHMSBPIMTAdjust']
               for zn in xrange(self.numUserZones):
                  niblet.settings['TPIMarginThreshold'][zn] += niblet.settings['VbarHMSTPIMTAdjust']
            else:
               for zn in xrange(self.numUserZones):
                  niblet.settings['BPIMarginThreshold'][zn] += niblet.settings['VbarHMSBPIMTAdjust']
                  niblet.settings['TPIMarginThreshold'][zn] += niblet.settings['VbarHMSTPIMTAdjust']

         # Set up scaling of measurements by niblet settings.  These settings will be used
         # whenever the getNibletizedRecord function is called to get measurement data.
         self.measWPZns.useNiblet(niblet)
         self.measAllZns.useNiblet(niblet)

         #Check head count and configure head mask
         status = self.selectHeads(self.measWPZns, niblet.settings['NumHeads'])
         if status == ATPI_DEPOP_RESTART:
            printDbgMsg('***************************** %s : %s *****************************'% self.lookupFailureInfo(status))
            self.resetForWaterfall()
            break
         elif status == ATPI_FAIL_HEAD_COUNT:
            printDbgMsg('***************************** %s : %s *****************************'% self.lookupFailureInfo(status))
            self.resetForWaterfall()
            continue

         if verbose > 1:
            dumpDebugData('WPZns-3',self.measWPZns)
         #############################################################################################
         #### Auto Triplet Tuning. Scp version                   ####
         #############################################################################################
         if self.getParam('AUTO_TRIPLET_MEAS', False):
            objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
            if testSwitch.SMR_TRIPLET_OPTI_WITH_EFFECTIVE_TPIC:
               if self.nibletIndex == 0:
                  printDbgMsg('AUTO_TRIPLET_MEAS: Measure BPI and TPI in Write Power Zones')
                  runTripletSweep = CTripletPicker(niblet, self.measAllZns)
                  if testSwitch.SMR_TRIPLET_OPTI_SET_BPI_TPI: #off set to drive
                      self.measAllZns = runTripletSweep.run()
                  else:
                      runTripletSweep.run()
                  printDbgMsg('self.measAllZns.store = %s' % str(self.measAllZns.getStore()))
            else:
               printDbgMsg('AUTO_TRIPLET_MEAS: Measure BPI and TPI in Write Power Zones')
               runTripletSweep = CTripletPicker()
               runTripletSweep.run()
         #############################################################################################

         #### Opti in all zones ####
         if self.getParam('ZN_OPTI', False):
            from base_SerialTest import SimpleOpti
            if verbose:
               objMsg.printMsg('pick() parm:ZN_OPTI')
            params = {'ZONES':testZones, 'ZONE_POS':TP.VBAR_ZONE_POS, 'DISABLE_ZAP': False,
               'COPY_2_ADJACENT' : testSwitch.FAST_2D_VBAR_UNVISITED_ZONE}
            
            if testSwitch.FE_0274346_356688_ZONE_ALIGNMENT:               
               params.update({'BER_ZONES': TP.BERInVBAR_ZN, 
                              'param': 'simple_OptiPrm_251_short_tune_znAlign'
               })

            if testSwitch.FE_0144101_208705_P_NO_TARGET_OPTI_IN_VBAR_ZN:
               params['param'] = 'simple_OptiPrm_251_No_Target_Opti'

            if testSwitch.TTR_REDUCED_PARAMS_T251:
               #  update to same as TP.base_ReducedPrm_251
               params['param'] = 'base_ReducedPrm_251'

            if testSwitch.FE_0150693_409401_P_KORAT_ZAP_OTF:
               SimpleOpti(self.dut, params).run(zapOtfZN=1)
            else:
               SimpleOpti(self.dut, params).run()

            if testSwitch.GA_0115421_231166_MEASURE_BER_POST_WP_OPTI_NOM_FMT:
               self.measureBER()

         #### Measure BPI and BER Transfer Function ####
         if self.getParam('BPI_TRANSFER_MEAS', False):
            if verbose:
               objMsg.printMsg('Measure BPI and BER Transfer Function')
               objMsg.printMsg('pick() parm:ZN_MEAS')
               
            measureBPIOnly = 1 #measure bpi only
            if testSwitch.FAST_2D_VBAR_UNVISITED_ZONE:
               oMeas = CMeasureBPIAndTPIinAllZones_UnvisitedZones(self.measAllZns, measureBPIOnly = measureBPIOnly)
            else:
               oMeas = CMeasureBPIAndTPIinAllZones_2DVBAR(self.measAllZns, measureBPIOnly = measureBPIOnly)
               
            self.measAllZns = oMeas.measureBPIAndTPI(testZones)
            
            #Apply Filter
            if testSwitch.FAST_2D_VBAR_UNVISITED_ZONE:
               oMeas.filterMeasurements('BPI', base_zn_list = testZones, Fit_2ndOrder = 0)
            else : oMeas.filterMeasurements('BPI')
            hdzns = [(hd,zn) for hd in range(self.numHeads) for zn in range(self.numUserZones)]
            printDbgMsg('After applying filter to TPI/BPI Measurements')
            oMeas.printMeasurements(hdzns, spcId=3000)

         #### Measure BPI and TPI in all zones ####
         if self.getParam('ZN_MEAS', False):
            if verbose:
               objMsg.printMsg('Measure BPI and TPI in all zones')
               objMsg.printMsg('pick() parm:ZN_MEAS')

            if testSwitch.FE_0158815_208705_VBAR_ZN_MEAS_ONLY:
               oMeas = CMeasureBPIAndTPIinAllZones(CVbarMeasurement(initStore=True))
               if testSwitch.FE_0150693_409401_P_KORAT_ZAP_OTF:
                  oMeas.measureBPIAndTPI(range(self.numUserZones), zapOTF=1)
               else:
                  oMeas.measureBPIAndTPI(range(self.numUserZones))
            else:
               if testSwitch.FAST_2D_VBAR: #2d vbar path
                  measureBPIOnly = 1 #measure bpi only
                  if testSwitch.FAST_2D_VBAR_UNVISITED_ZONE:
                     oMeas = CMeasureBPIAndTPIinAllZones_UnvisitedZones(self.measAllZns, measureBPIOnly = measureBPIOnly)
                  else:
                     oMeas = CMeasureBPIAndTPIinAllZones_2DVBAR(self.measAllZns, measureBPIOnly = measureBPIOnly)
               else : #1d vbar path
                  measureBPIOnly = 0 #measure bpi and tpi
                  oMeas = CMeasureBPIAndTPIinAllZones(self.measAllZns)
               if testSwitch.FE_0150693_409401_P_KORAT_ZAP_OTF:
                  self.measAllZns = oMeas.measureBPIAndTPI(range(self.numUserZones),zapOTF=1)
               else:
                  self.measAllZns = oMeas.measureBPIAndTPI(testZones)
               #Apply the filtering function to TPI measurements, this will change the original measurements data
               if not measureBPIOnly: oMeas.filterMeasurements('TPI')
               if testSwitch.FAST_2D_VBAR_UNVISITED_ZONE:
                  oMeas.filterMeasurements('BPI', base_zn_list = testZones, Fit_2ndOrder = 0)
               else : oMeas.filterMeasurements('BPI')
               hdzns = [(hd,zn) for hd in range(self.numHeads) for zn in range(self.numUserZones)]
               printDbgMsg('After applying filter to TPI/BPI Measurements')
               oMeas.printMeasurements(hdzns, spcId=3000)

               if testSwitch.FE_0111183_340210_SAT_FAIL_MINIMAL_RETRY:
                  status = self.testSatFail(self.measAllZns)
                  if status != ATPI_PASS:
                     printDbgMsg('***************************** %s : %s *****************************' % self.lookupFailureInfo(status))
                     self.resetForWaterfall()
                     if testSwitch.WA_0115472_208705_DISALLOW_13409_WATERFALL:
                        break
                     else:
                        continue

               if testSwitch.FE_0135314_208705_DELTA_BPIC_SCREEN:
                  status = self.deltaBPICScreen()
                  if status != ATPI_PASS:
                     printDbgMsg('***************************** %s : %s *****************************' % self.lookupFailureInfo(status))
                     self.resetForWaterfall()
                     continue

               # Pharaoh Head Screen from the factory
               if testSwitch.FE_0119998_231166_FACTORY_VBAR_ADC_ENHANCEMENTS:
                  self.checkOEMWTF()

            if verbose:
               objMsg.printMsg('Measure BPI and TPI in all zones')
               if verbose > 1:
                  dumpDebugData('Measure BPI and TPI in all zones - WPZns-9',self.measAllZns)

            if testSwitch.BPICHMS:
               for hd in xrange(self.numHeads):
                  TgtClrBPIMarginBackOff = 0
                  for zn in xrange(self.numUserZones):
                     meas = CVbarDataHelper(self.measAllZns, hd, zn)
                     TgtClrBPIMarginBackOff += meas['BPIR'] - meas['BPIH']
                  TgtClrBPIMarginBackOff = TgtClrBPIMarginBackOff / self.numUserZones

                  printDbgMsg('DBG: TgtClrBPIMarginBackOff Hd %d: %4f' % (hd, TgtClrBPIMarginBackOff))
                  if TgtClrBPIMarginBackOff > TP.BPIClrMarginThreshold:
                     if TgtClrBPIMarginBackOff > 0.05:
                        znComp = range(self.numUserZones)
                     elif TgtClrBPIMarginBackOff > 0.02:
                        znComp = [0, 1, 2, 3, self.numUserZones - 4, self.numUserZones - 3, self.numUserZones - 2,self.numUserZones - 1]
                     elif TgtClrBPIMarginBackOff > 0.012:
                        znComp = [0, 1, 2, self.numUserZones - 3, self.numUserZones - 2,self.numUserZones - 1]
                     else:
                        znComp = [0, 1, self.numUserZones - 2, self.numUserZones - 1]

                     printDbgMsg('%s\t%s\t%s\t%s\t%s' % ('DBG: TCMC Hd','Zn','BpicR','BpicH','BPIMAdj'))
                     for zn in znComp:
                        meas = CVbarDataHelper(self.measAllZns, hd, zn)
                        niblet.settings['BPIMarginThreshold'][hd][zn] = max(niblet.settings['BPIMarginThreshold'][hd][zn],TgtClrBPIMarginBackOff)
                        printDbgMsg('DBG: TCMC %d\t%d\t%4f\t%4f\t%4f' % (hd,zn,meas['BPIR'],meas['BPIH'],niblet.settings['BPIMarginThreshold'][hd][zn]))

         ### SCP implementaion of HMS without changing format ###
         if self.getParam('FAST_SCP_HMS', False) and self.nibletIndex == 0: ## Execute HMS only on first niblet level
            limits = {
                  'MAX_BPI_STEP'       : self.getParam('MAX_BPI_STEP', 100.0) + niblet.settings['MAX_BPI_STEP_ADJ'],
                  'MAX_BPI_PICKER_ADJ' : self.getParam('MAX_BPI_PICKER_ADJ', 100.0),
                  'MAX_TPI_PICKER_ADJ' : self.getParam('MAX_TPI_PICKER_ADJ', 100.0),
                  }
            if verbose:
               objMsg.printMsg('pick() HMS capability  parm:SCP_HMS_MEAS2-1')

            allowFailures = 1 #self.getParam('HMS_FAIL', False)
            allowAdjustments = 1 # self.getParam('HMS_ADJ', False)
            BPIperHMS = self.getParam('BPI_PER_HMS', None)
            MAX_HMS_ITERATIONS = TP.MAX_HMS_ITERATIONS
            HMS_BPI_STEP = TP.HMS_BPI_STEP
            VbarHMSMinZoneSpec  = niblet.settings['VbarHMSMinZoneSpec'] + 0.3
            oMeas = CMeasureBPIAndTPIinAllZones(self.measAllZns)

            #*******Measure HMS All hd/zones first
            self.hmsPicker = CPicker(niblet, self.measAllZns, limits)
            dataList2 = {}
            slopeList2 ={}
            # TODO: optimize this routine
            for hd in xrange(self.numHeads):
               dataList2[hd,'BPI'] = []
               dataList2[hd,'HMS'] = []
               slopeList2[hd] ={}
               for zn in xrange(self.numUserZones):
                  dataList2[hd,zn,'BPI'] = []
                  dataList2[hd,zn,'HMS'] = []
                  #make a copy of original BPI into BPI_HMS
                  meas = CVbarDataHelper(self.measAllZns, hd, zn)
                  meas['BPI_HMS'] = meas['BPI']
                  meas['BPIAdj'] = 0.00 # Initialize
                  meas['BPIChanged'] = 'T' # so that next measurement will trigger

            hmsspcId = 200
            iterations = 0
            for adjustment in range(-4,5,1):
               oMeas.measureAllHMS(self.getParam('MEAS_HMS_211_PARMS', 'MeasureHMS_211'),spcId=hmsspcId + iterations, adjBPIforTPI= adjustment, report_option = 0x000F)
               HMSStatus = self.processSCPHMS(allowFailures, allowAdjustments, niblet, BPIperHMS,iterations,oMeas,HMS_BPI_STEP, adjustment = adjustment)
               for hd in xrange(self.numHeads):
                  for zn in xrange(self.numUserZones):
                     bpi_pct = 1.0 + float(adjustment) / 100
                     bpi_pct_s = oMeas.formatScaler.scaleBPI(hd, zn, bpi_pct)
                     meas = CVbarDataHelper(self.measAllZns, hd, zn)
                     meas['BPIChanged'] = 'T' # so that next measurement will trigger
                     dataList2[hd, zn, 'BPI'].append(bpi_pct_s)
                     dataList2[hd, zn, 'HMS'].append(meas['HMS'])
               iterations +=1

            # Process data into HMS Margin
            self.fastprocessSCPHMS(dataList2, VbarHMSMinZoneSpec)

            if not testSwitch.CM_REDUCTION_REDUCE_PRINTDBLOGBIN:
               objMsg.printDblogBin(self.dut.dblData.Tables('P_VBAR_HMS_ADJUST'))
            for hd in xrange(self.numHeads):
               for zn in xrange(self.numUserZones):
                  meas = CVbarDataHelper(self.measAllZns, hd, zn)
                  meas['BPIChanged'] = 'F' ##set everything to false now, later HMS measurement will measure nothing then.
                  meas['BPIAdj'] = 0.00 # reset to 0, other routine appear to use this for other purpose
                  if verbose:
                     objMsg.printMsg('HMSC_DBG: hd %d zn %d HMSC1: %4f HMSMARGIN1: %4f' % (hd,zn,meas['HMS'],meas['BPIMH']))

            ## set BPIC-HMS Margin into drives and verify results
            if testSwitch.FAST_SCP_HMS_VERIFY:
               self.hmsPicker['BpiCapability'] = deepcopy(self.measAllZns['BPI']) #reset to original
               self.hmsPicker['AdjustedBpiFormat'] = array('c', ['T']*self.numUserZones*self.numHeads)
               for hd in xrange(self.numHeads):
                  for zn in xrange(self.numUserZones):
                     pickerData = CVbarDataHelper(self.hmsPicker, hd, zn)
                     meas = CVbarDataHelper(self.measAllZns, hd, zn)
                     pickerData['BpiFormat'] = self.hmsPicker.getClosestBPITable(pickerData['BpiCapability']-meas['BPIMH'],zn,hd)
               #=== Set new BPIC format to drive
               self.hmsPicker.sendFormatToDrive = 1
               self.hmsPicker.BpiFileCapacityCalc = 0
               self.hmsPicker.setFormat('BPI',movezoneboundaries=True)
               self.hmsPicker['AdjustedBpiFormat'] = array('c', ['F']*self.numUserZones*self.numHeads)
               self.measAllZns['BPIChanged'] = array('c', ['T']*self.numUserZones*self.numHeads) # so that next measurement will trigger
               oMeas.formatScaler.load()
               #=== Save RAP and SAP to flash
               prm = {'test_num': 178, 'prm_name': 'prm_wp_178', 'timeout': 1200, 'spc_id': 0,}
               prm.update({'CWORD1':0x0620})
               getVbarGlobalClass(CProcess).St(prm)
               if testSwitch.FE_0269922_348085_P_SIGMUND_IN_FACTORY:
                  self.HMS_RdGap_Zap_Opti(['RD_OPTI'])
               else:
                  self.HMS_RdGap_Zap_Opti(['GAP_CAL','RD_OPTI'])
               oMeas.measureAllHMS(self.getParam('MEAS_HMS_211_PARMS', 'MeasureHMS_211'),spcId=300, report_option = 0x000F)

         #### Opti in HMS zones ####
         if self.getParam('HMS_OPTI', False):
            from base_SerialTest import SimpleOpti
            if verbose:
               objMsg.printMsg('pick() parm:HMS_OPTI')

            # Create a list of (head, zone) tuples, consisting of only those zones where the BPI has changed.
            hdznsWithBPIChange = getHdZnsWithBPIChange(self.measAllZns)

            # Create a dictionary with heads as keys and a list of test zones as their associated values.
            hms_zones = {}
            for hd, zn in hdznsWithBPIChange:
               hms_zones.setdefault(hd, []).append(zn)

            # Zones to be optied vary by head, so make individual Opti calls for each head, with the appropriate zone mask.

            if testSwitch.RUN_T176_INSIDE_VBAR_HMS and hms_zones: #got active zones
               from base_SerialTest import CReadWriteGapCal
               params_writer_reader_gap = {'SKIP_SYS_ZONE' : 1, 'spc_id': self.dut.vbar_iterations, 'ZONE_MASK': hms_zones}
               CReadWriteGapCal(self.dut, params_writer_reader_gap).run()

            for hd in hms_zones:
               params = {'HEAD':hd, 'ZONES':hms_zones[hd], 'ZONE_POS':TP.VBAR_ZONE_POS, 'DISABLE_ZAP': False}

               if testSwitch.FE_0138035_208705_P_NO_TARGET_OPTI_IN_VBAR_HMS:
                  params['param'] = 'simple_OptiPrm_251_No_Target_Opti'

               if testSwitch.FE_0150693_409401_P_KORAT_ZAP_OTF:
                  SimpleOpti(self.dut, params).run(zapOtfHMS=1)
               else:
                  SimpleOpti(self.dut, params).run()
                  
         ##################################
         #### 2D VBAR SMR Measurements ####
         ##################################
         if self.getParam('2D_VBAR_MEAS', False):
            oMeas = CMeasureBPIAndTPIinAllZones_UnvisitedZones(self.measAllZns)
            
            # Set up Test Zones
            if testSwitch.FAST_2D_VBAR_UNVISITED_ZONE:
               meas_zones = TP.Measured_2D_Zones
            elif testSwitch.FAST_2D_VBAR_INTERLACE:
               meas_zones = range(0,self.numUserZones,2)
            else: #all zones
               meas_zones = range(self.numUserZones)
               
            # Reset Read Offset
            oMeas.Reset_Read_offset()

            #measure bpi & tpi to for determining best sova
            meas_2D = oMeas.measureTPI_2D(meas_zones)
            #determine the best sova
            oMeas.calculateBestTargetSFR(niblet, meas_zones, meas_2D)
            
         ######################################
         #### 1D VBAR TPI NOMINAL SMR Measurements ####
         ######################################
         if self.getParam('TPINOMINAL', False):
            limits = {
                  'MAX_BPI_STEP'       : self.getParam('MAX_BPI_STEP', 100.0) + niblet.settings['MAX_BPI_STEP_ADJ'],
                  'MAX_BPI_PICKER_ADJ' : self.getParam('MAX_BPI_PICKER_ADJ', 100.0),
                  'MAX_TPI_PICKER_ADJ' : self.getParam('MAX_TPI_PICKER_ADJ', 100.0),
                  'UPDATE_SQUEEZE_MICROJOG' : self.getParam('UPDATE_SQUEEZE_MICROJOG',0),
                  'UPDATE_SHINGLE_DIRECTION' : self.getParam('UPDATE_SHINGLE_DIRECTION',0)
                  }
            oMeas = CMeasureBPIAndTPIinAllZones_UnvisitedZones(self.measAllZns)
            # Set up Test Zones
            znlist = eval(str(self.getParam('TPI_NOMINAL_MEAS_ZONES', "TP.Measured_BPINOMINAL_Zones")))
            if self.getParam('DSS_MEASUREMENT_ONLY',0):
               # Trigger Measurements
               oMeas.measureSingleSidedTPI(znlist, znlist) # Skip Single Sided TPI
            else:
               # Trigger Measurements
               oMeas.measureSingleSidedTPI(znlist)
            

            if self.getParam('PREVENT_FMT_SUM_TBL_LD_TO_EDW', False):
               SendVbarFmtSummaryToEDW = False
            else:
               SendVbarFmtSummaryToEDW = True
               
            if testSwitch.FE_0232067_211428_VBAR_USE_DESPERADO_PLUS_FORMAT_PICKER:
               self.objPicker = CDesperadoPlusPicker(niblet, self.measAllZns, limits, SendVbarFmtSummaryToEDW)
            elif testSwitch.DESPERADO:
               self.objPicker = CDesperadoPicker(niblet, self.measAllZns, limits, SendVbarFmtSummaryToEDW)
            else:
               self.objPicker = CPicker(niblet, self.measAllZns, limits, SendVbarFmtSummaryToEDW)
               
            if not self.getParam('DSS_MEASUREMENT_ONLY',0):
               #=== Get SMR Direction Shift when TPI SSS is also measured
               shift_Zone = self.objPicker.get_SMR_Direction_Shift(znlist)
               
            #===  Process the TPI_NOMINAL data
            oMeas.Process_TPINOMINAL(znlist, self.getParam('DSS_MEASUREMENT_ONLY',0))
            
            #=== Get the Zone to update from input params, set all zones if not defined
            znlist = eval(str(self.getParam('TPI_NOMINAL_SET_FMT_ZONES', "range(self.numUserZones)")))
            #=== Set TPIC format
            for hd in xrange(self.numHeads):
               for zn in znlist:
                  if self.getParam('DSS_MEASUREMENT_ONLY',0):
                     # for TPINOMINAL1, use the UMP Write Fault Threshold of first UMP Zone, have to manually calculate below
                     pickerData = CVbarDataHelper(self.objPicker, hd, zn)
                     meas = self.measAllZns.getRecord('TPI', hd, zn)
                     if testSwitch.FE_0215591_007867_COMPUTE_TPIC_AS_RATIO_MERGE_CL537310:
                        pickerData['TpiCapability'] = meas * (1 - niblet.settings['WriteFaultThreshold'][TP.UMP_ZONE[self.numUserZones][0]])
                     else:
                        pickerData['TpiCapability'] = meas - niblet.settings['WriteFaultThreshold'][TP.UMP_ZONE[self.numUserZones][0]]
                  else:
                     # for TPINOMINAL2, use the niblet write fault threshold setting
                     pickerData = CVbarDataHelper(self.objPicker, hd, zn)
                     meas = self.measAllZns.getNibletizedRecord(hd, zn) # use write fault threshold for Triplet Opti
                     if niblet.settings['TracksPerBand'][zn] == 1: # use TPI DSS for UMP Zones
                        pickerData['TpiCapability'] = meas['TPI']
                     elif zn >= shift_Zone[hd]: # Use TPI ODSS for zones equal to or beyond the shift zone
                        pickerData['TpiCapability'] = meas['TPI_ODSS']
                     else: # Use TPI IDSS for zones before shift zone
                        pickerData['TpiCapability'] = meas['TPI_IDSS']
                  pickerData['AdjustedTpiFormat'] = 'T'
                  
            self.objPicker.sendFormatToDrive = 1
            self.objPicker.setFormat('TPI', set_one_tpb = 1)
            if verbose:
               getVbarGlobalVar()['formatReload'] = True
               CVbarFormatScaler() #for debuging purpose, to display the format after the above format setting
               getVbarGlobalClass(CProcess).St({'test_num':172,'prm_name':'Retrieve Zone Table Info','CWORD1':0x0002, 'spc_id':10, 'stSuppressResults': 0,'timeout': 100, })

            #=== Save RAP and SAP to flash
            prm = {'test_num': 178, 'prm_name': 'prm_wp_178', 'timeout': 1200, 'spc_id': 0,}
            prm.update({'CWORD1':0x0620})
            getVbarGlobalClass(CProcess).St(prm)
               
            if testSwitch.FE_0184102_326816_ZONED_SERVO_SUPPORT:
               self.objPicker.syncZoneServoBoundary()
         
         ######################################
         #### 1D VBAR TPI SMR Measurements ####
         ######################################
         if self.getParam('1D_VBAR_MEAS', False):
            oMeas = CMeasureBPIAndTPIinAllZones_UnvisitedZones(self.measAllZns)
            self.tracksPerBand = niblet.settings['TracksPerBand']
            # Set up Test Zones
            znLst_skip_tpi_sss = []
            if testSwitch.FAST_2D_VBAR_UNVISITED_ZONE:
               meas_2Dzones = TP.Measured_2D_Zones
               meas_1Dzones = [] #remaining zones 
               # build the znlist to measure in 1D VBAR
               for zn in xrange(self.numUserZones):
                  if zn not in (meas_2Dzones + TP.Unvisited_Zones):
                     meas_1Dzones.append(zn)
                  if niblet.settings['TracksPerBand'][zn] == 1:
                     znLst_skip_tpi_sss.append(zn)
            elif testSwitch.FAST_2D_VBAR_INTERLACE:
               meas_2Dzones = range(0,self.numUserZones,2)
               meas_1Dzones = [zn + 1 for zn in range(0,self.numUserZones-1,2)]
            else: #all zones
               meas_2Dzones = range(self.numUserZones)
               meas_1Dzones = [] # all zones should have been measured in 2D VBAR
            
            oMeas.measureSingleSidedTPI(meas_1Dzones, znLst_skip_tpi_sss)
            
            # Take care of the filter
            if testSwitch.APPLY_FILTER_ON_SMR_TPI:
               if len(TP.Unvisited_Zones) and testSwitch.FAST_2D_VBAR_UNVISITED_ZONE:
                  visited_zn = [] # this zones will be used to generate the filtered values
                  update_zn =[]   # this zones will be updated with the filtered values
                  for zn in range(self.numUserZones):
                     
                     if testSwitch.FAST_2D_VBAR_UMP_FIX_BEST_TARGET_SOVA_BER:
                        if niblet.settings['TracksPerBand'][zn] != 1:
                           update_zn.append(zn) # update filtered values to only smr zones
                           if zn in meas_2Dzones + meas_1Dzones:
                              visited_zn.append(zn) # base zone list from measured zones
                     else:
                        update_zn.append(zn) # update all zones with filter values
                        if zn in meas_2Dzones + meas_1Dzones:
                           visited_zn.append(zn) # base zone list from measured zones
                        
                  param_list = ['TPI', 'TPI_DSS', 'TPI_ODSS', 'TPI_IDSS', 'RD_OFST_ODSS', 'RD_OFST_IDSS']
                     
                  for param in param_list:
                     oMeas.filterMeasurements(param, base_zn_list = visited_zn, Fit_2ndOrder = 0, save_zn_list = update_zn)
               else:
                  param_list = ['TPI', 'TPI_IDSS', 'TPI_ODSS']
                  if testSwitch.FAST_2D_S2D_TEST:
                     param_list += ['TPI_ODSS2D','TPI_IDSS2D']
                  for param in param_list:
                     oMeas.filterMeasurements(param)
                        

         ##########################
         #### SMR Measurements ####
         ##########################
         if self.getParam('SMR_MEAS', False):
            if verbose: objMsg.printMsg('pick() parm:SMR_MEAS')

            # otherwise measure all zones
            objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

            if testSwitch.FAST_2D_S2D_TEST:
               oMeas = CMeasureBPIAndTPIinAllZones_S2D(self.measAllZns)
            elif testSwitch.FAST_2D_VBAR_UNVISITED_ZONE:
               oMeas = CMeasureBPIAndTPIinAllZones_UnvisitedZones(self.measAllZns)
            else:
               oMeas = CMeasureBPIAndTPIinAllZones(self.measAllZns)

            if testSwitch.FAST_2D_VBAR_UNVISITED_ZONE:
               meas_zones = TP.Measured_2D_Zones
               znlist = [] #remaing visited zones
               for zn in range(self.numUserZones):
                  if zn not in (TP.Measured_2D_Zones + TP.Unvisited_Zones):
                     if not (testSwitch.FAST_2D_VBAR_UMP_FIX_BEST_TARGET_SOVA_BER and \
                        niblet.settings['TracksPerBand'][zn] == 1):
                        znlist.append(zn)
            elif testSwitch.FAST_2D_VBAR_INTERLACE:
               meas_zones = range(0,self.numUserZones,2)
               znlist = [zn + 1 for zn in range(0,self.numUserZones-1,2)]
            else: #all zones
               meas_zones = range(self.numUserZones)
               znlist = []

            if testSwitch.FAST_2D_VBAR:
               # Reset the Rd Offset for now in order to be consistent
               if testSwitch.OTC_RESET_RD_OFFSET_BEFORE_TUNE:
                  oMeas.Reset_Read_offset()
               objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

               #measure bpi & tpi to for determining best sova
               meas_2D = oMeas.measureTPI_2D(meas_zones)
               #determine the best sova
               oMeas.calculateBestTargetSFR(niblet, meas_zones, meas_2D)
               objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
               #measuring remaining zones using 1d vbar
               oMeas.measureSingleSidedTPI(znlist)

            else: 
               objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
               oMeas.measureSingleSidedTPI(range(self.numUserZones))

            if self.getParam('PARAMS_FILTER', False):
               smr_zones = [zn for zn in range(self.numUserZones) if niblet.settings['TracksPerBand'][zn] > 1]
               if len(TP.Unvisited_Zones) and testSwitch.FAST_2D_VBAR_UNVISITED_ZONE:
                  visited_zn = []
                  update_zn =[]
                  for zn in range(self.numUserZones):
                     if testSwitch.FAST_2D_VBAR_UMP_FIX_BEST_TARGET_SOVA_BER and zn in smr_zones:
                        update_zn.append(zn) # update filter to only smr zones
                     if (zn in TP.Measured_2D_Zones) or (zn not in TP.Unvisited_Zones):
                        if not testSwitch.FAST_2D_VBAR_UMP_FIX_BEST_TARGET_SOVA_BER:
                           visited_zn.append(zn)
                        # if switch FAST_2D_VBAR_UMP_FIX_BEST_TARGET_SOVA_BER, need to make sure zn is in SMR zone
                        elif zn in smr_zones: 
                           visited_zn.append(zn)
                  param_list = ['BPI', 'TPI', 'TPI_ODSS', 'TPI_IDSS', 'RD_OFST_ODSS', 'RD_OFST_IDSS']
                  if testSwitch.FAST_2D_S2D_TEST:
                     param_list += ['TPI_ODSS2D','TPI_IDSS2D']
                  for param in param_list:
                     oMeas.filterMeasurements(param, base_zn_list = visited_zn, Fit_2ndOrder = 0, save_zn_list = update_zn)
               else:
                  param_list = ['TPI', 'TPI_IDSS', 'TPI_ODSS']
                  if testSwitch.FAST_2D_S2D_TEST:
                     param_list += ['TPI_ODSS2D','TPI_IDSS2D']
                  for param in param_list:
                     oMeas.filterMeasurements(param)

         ###### Read Offset Measurement #####
         if self.getParam('RD_OFT_MEAS', False):
            oMeas = CMeasureBPIAndTPIinAllZones(self.measAllZns)
            if testSwitch.OTC_RESET_RD_OFFSET_BEFORE_TUNE: #reset read offset
               oMeas.Reset_Read_offset()
            #consolidate zone calling to one call
            oMeas.measure_allZoneOTC([zn for zn in xrange(self.numUserZones) if niblet.settings['TracksPerBand'][zn] > 1])
            
         ###### Special Measurement of TPI_DSS of the UMP Zones #####
         if self.getParam('TPI_DSS_MEAS', False):
            oMeas = CMeasureBPIAndTPIinAllZones_UnvisitedZones(self.measAllZns)
            test_zones = [zn for zn in xrange(self.numUserZones) if niblet.settings['TracksPerBand'][zn] == 1]
            oMeas.measureTPI_DSS_UMP(test_zones)

         if verbose > 1:
            dumpDebugData('Post-Interpolate - AllZns',self.measAllZns)

         #### HMS capability ####
         if self.getParam('HMS_MEAS', False):
            if verbose:
               objMsg.printMsg('pick() HMS capability  parm:HMS_MEAS-1')
            oMeas = CMeasureBPIAndTPIinAllZones(self.measAllZns)
            if testSwitch.VBAR_HMS_MEAS_ONLY and self.dut.nextState in ['HMSC_DATA']:
               self.measAllZns['BPIChanged'] = array('c', ['T']*self.numUserZones*self.numHeads) # so that next measurement will trigger

            if testSwitch.FE_0150693_409401_P_KORAT_ZAP_OTF:
               oMeas.measureAllHMS(self.getParam('MEAS_HMS_211_PARMS', 'MeasureHMS_211'),zapOTF=1)
            else:
               oMeas.measureAllHMS(self.getParam('MEAS_HMS_211_PARMS', 'MeasureHMS_211'))

         #### Adjust for HMS capability ####
         if self.getParam('HMS_MEAS', False):
            if verbose:
               objMsg.printMsg('pick() Adjust for HMS capability  parm:HMS_MEAS-2')
            allowFailures = self.getParam('HMS_FAIL', False)
            allowAdjustments = self.getParam('HMS_ADJ', False)
            BPIperHMS = self.getParam('BPI_PER_HMS', None)
            objMsg.printMsg("BPIperHMS=%s" % BPIperHMS)
            status = self.processHMS(allowFailures, allowAdjustments, niblet, BPIperHMS)

            if testSwitch.VBAR_HMS_MEAS_ONLY and self.dut.nextState in ['HMSC_DATA']:
               objMsg.printMsg('ccccyyyy hms data collection only !!!!!!!!!!!!!!!!!!!!1111')
               return

            if status != ATPI_PASS:
               objMsg.printMsg('***************************** %s : %s *****************************'% self.lookupFailureInfo(status))
               self.resetForWaterfall()
               continue

         #### Set ADC Format to Drive, Channel Tune/ RW GAP CAL / MiniZAP ####
         if self.getParam('SET_ADC_FMT', False) and self.nibletIndex == 0: ## Execute SET_FMT only on first niblet level
            limits = {
               'MAX_BPI_STEP'       : self.getParam('MAX_BPI_STEP', 100.0) + niblet.settings['MAX_BPI_STEP_ADJ'],
               'MAX_BPI_PICKER_ADJ' : self.getParam('MAX_BPI_PICKER_ADJ', 100.0),
               'MAX_TPI_PICKER_ADJ' : self.getParam('MAX_TPI_PICKER_ADJ', 100.0),
               'UPDATE_SQUEEZE_MICROJOG' : self.getParam('UPDATE_SQUEEZE_MICROJOG',0),
               'UPDATE_SHINGLE_DIRECTION' : self.getParam('UPDATE_SHINGLE_DIRECTION',0)
               }
            
            if self.getParam('OTC_MARGIN_MEAS', False) or self.getParam('SQZ_BPIC_MEAS', False):
               limits.update({
                  'UPDATE_SHINGLE_DIRECTION' : self.getParam('UPDATE_SHINGLE_DIRECTION', 1),
                  'SPC_ID_BANDED_TPI' : TP.SPC_ID_BANDED_TPI_OTC_PICKER,
                  'RD_OFST' : TP.RD_OFST_SEL_OTC_PICKER,
               })
               
            if verbose:
               objMsg.printMsg('pick() Set ADC format  parm:SET_ADC_FMT')
            
            #===  Set up the Object Picker
            if testSwitch.FE_0115422_340210_FORMATS_BY_MARGIN or self.getParam('CONST_MARGIN', False):
               if testSwitch.SMR or testSwitch.DESPERADO:
                  self.objPicker = CSmrMarginPicker(niblet, self.measAllZns, limits)
               else:
                  # Note: One of two different functions will be run here, depending on the
                  # setting of the FE_0115422_340210_FORMATS_BY_MARGIN flag.
                  self.objPicker = CMarginPicker(niblet, self.measAllZns, limits)

            # --- Choose Fmt Picker for Normal Format Picker mode ---
            else:
               if self.getParam('PREVENT_FMT_SUM_TBL_LD_TO_EDW', False):
                  SendVbarFmtSummaryToEDW = False
               else:
                  SendVbarFmtSummaryToEDW = True

               #reset prior picker so as to start from capability
               for hd in xrange(self.numHeads): 
                  for zn in xrange(self.numUserZones):
                     meas = CVbarDataHelper(self.measAllZns, hd, zn)
                     meas['TPIPickEffective'] = -1.0
                     meas['BPIAdj'] = 0
                     if self.getParam('OTC_MARGIN_MEAS', False) and niblet.settings['TracksPerBand'][zn] > 1:
                        if self.getParam('OTC_MARGIN_V2', False):
                           meas['TPI_INTER'] = -1.0
                           meas['TPI_INTRA'] = -1.0
                           meas['TPI_UMP'] = -1.0
                        else:
                           meas['TPI_OTC'] = -1.0
                     if self.getParam('SQZ_BPIC_MEAS', False) and niblet.settings['TracksPerBand'][zn] > 1:
                        meas['SQZ_BPI'] = -1.0
                     if self.getParam('ATI_MEAS', False) and niblet.settings['TracksPerBand'][zn] == 1:
                        meas['TPIMA'] = 0
               if testSwitch.FE_0232067_211428_VBAR_USE_DESPERADO_PLUS_FORMAT_PICKER:
                  self.objPicker = CDesperadoPlusPicker(niblet, self.measAllZns, limits, SendVbarFmtSummaryToEDW)
               elif testSwitch.DESPERADO:
                  self.objPicker = CDesperadoPicker(niblet, self.measAllZns, limits, SendVbarFmtSummaryToEDW)
               else:
                  self.objPicker = CPicker(niblet, self.measAllZns, limits, SendVbarFmtSummaryToEDW)
            
            #===  Pick BPI / TPI and Set Format
            if testSwitch.DESPERADO:
               self.objPicker['BpiMarginTarget'] = array('f', [0.0]*self.numUserZones*self.numHeads)
               self.objPicker['TpiMarginTarget'] = array('f', [0.0]*self.numUserZones*self.numHeads)
               self.tracksPerBand = niblet.settings['TracksPerBand']
               self.objPicker.pickTPI()
               self.objPicker.pickBPI()
               self.objPicker.sendFormatToDrive = True
               self.objPicker.BpiFileCapacityCalc = False
               
               self.objPicker['AdjustedBpiFormat'] = array('c', ['F']*self.numUserZones*self.numHeads)
               if verbose:
                  self.objPicker.displayCapability()
               self.objPicker.setFormat(metric = "BOTH", maximize_zone = testSwitch.FE_0184102_326816_ZONED_SERVO_SUPPORT, \
                        consolidateByZone = testSwitch.FE_0262424_504159_ST210_SETTING_FORMAT_IN_ZONE)                  

            else: # settle with the CMR legacy picker
               #=== Get TPIC format
               for hd in xrange(self.numHeads):
                  for zn in xrange(self.numUserZones):
                     pickerData  = CVbarDataHelper(self.objPicker, hd, zn)
                     pickerData['BpiFormat'] = self.objPicker.getClosestBPITable(pickerData['BpiCapability'],zn,hd)
                     pickerData['TpiCapability'] -= TP.TPIAdjustDuringVBART51
                     pickerData['TpiFormat'] = self.objPicker.getClosestTPITable(pickerData['TpiCapability'])
               self.objPicker['AdjustedBpiFormat'] = array('c', ['T']*self.numUserZones*self.numHeads)
               self.objPicker['AdjustedTpiFormat'] = array('c', ['T']*self.numUserZones*self.numHeads)
               
               #=== Set TPIC & BPIC format to drive
               self.objPicker.sendFormatToDrive = 1
               self.objPicker.BpiFileCapacityCalc = 0
               self.objPicker.setFormat('BPI',movezoneboundaries=True)
               self.objPicker.setFormat('TPI')
            
            #=== Save RAP and SAP to flash
            prm = {'test_num': 178, 'prm_name': 'Save RAP and SAP to Flash', 'timeout': 1200, 'spc_id': 0, 'CWORD1':0x0620}
            getVbarGlobalClass(CProcess).St(prm)

            #print out the values in objPicker.data after the format is set
            if verbose:
               objMsg.printMsg('\nVBAR_DEBUG: MEASURED BPIC & TPIC')
               objMsg.printMsg('='*58)
               objMsg.printMsg("%2s  %2s  %15s  %15s  %15s" %("Hd", "Zn", "MeasBpi", "BpiFormatOfs", "MeasTpi"))
               objMsg.printMsg('='*58)
               for hd in xrange(self.numHeads):
                  for zn in xrange(self.numUserZones):
                     pickerData = CVbarDataHelper(self.objPicker, hd, zn)
                     objMsg.printMsg("%2d  %2d  %15.4f  %15d  %15.4f" %(hd, zn, \
                        pickerData['BpiCapability'], pickerData['BpiFormat'], pickerData['TpiCapability']))
               self.mFSO.getZoneTable(newTable = 1, delTables = 1, supressOutput = 0, spc_id = 10)

            #=== Setup Tuning and miniZAP when margins are On
            if self.getParam('OTC_MARGIN_MEAS', False) or self.getParam('ATI_MEAS', False) or \
                  self.getParam('SQZ_BPIC_MEAS', False):
               if testSwitch.DESPERADO:
                  zap_zones = eval(str(self.getParam('MINIZAP_ZONES', "range(self.numUserZones)")))
                  opti_zones = eval(str(self.getParam('ON_TRK_BER_ZONES', "range(self.numUserZones)")))
                  if not (self.getParam('OTC_MARGIN_MEAS', False) or self.getParam('SQZ_BPIC_MEAS', False)) and \
                     self.getParam('ATI_MEAS', False):
                     zap_zones = TP.prm_VBAR_ATI_51['ZONES'] # Only ATI zones if OTC is is false
                     opti_zones = TP.prm_VBAR_ATI_51['ZONES'] # Only ATI zones if OTC is is false
                     
                  if testSwitch.FE_0184102_326816_ZONED_SERVO_SUPPORT:
                     self.objPicker.syncZoneServoBoundary()
   
                  from SerialTest import CReadWriteGapCal, CRdOpti_2DVBAR, CPrecoder
                  if testSwitch.RUN_T176_IN_VBAR and not testSwitch.FE_0269922_348085_P_SIGMUND_IN_FACTORY:
                     #Gap CAL
                     CReadWriteGapCal(self.dut, {'SKIP_SYS_ZONE' : 1}).run()
                  #=== ZAP and ReOpti
                  objVbarOpti = CRdOpti_2DVBAR(self.dut, \
                     {'ZONES' : opti_zones, 'BAND_WRITE_251' : self.getParam('BAND_WRITE_251', 0), 'RST_OFFSET' : 1})
                  zapped_track_limit = self.getParam('ZAP_LIMIT', 0x0A32) ##zap range zoneposition-50, zoneposition+10
                  objVbarOpti.optiZAP(zap_zones, trackLimit=zapped_track_limit)
                  
                  if testSwitch.FE_0262764_514721_RUN_PRECODER_IN_CAL2:
                     CPrecoder(self.dut).run()
                     
                  if testSwitch.FE_0293167_356688_VBAR_MARGIN_ZONE_COPY:
                     from base_SerialTest import CRdOptiZoneInsertion
                     CRdOptiZoneInsertion(self.dut).run()
                  objVbarOpti.run()
               else: # not touch legacy CMR mode first
                  from base_SerialTest import CRdOpti, CReadWriteGapCal
                  if testSwitch.RUN_T176_IN_VBAR and not testSwitch.FE_0269922_348085_P_SIGMUND_IN_FACTORY:
                     #Gap CAL
                     CReadWriteGapCal(self.dut, {'SKIP_SYS_ZONE' : 1}).run()
                  
                  if testSwitch.RUN_FINE_UJOG_IN_VBAR:
                     from base_SerialTest import CFineReadWriteOpti
                     # Run CQM uJog in vbar
                     CFineReadWriteOpti(self.dut).run()
                     
                  #=== ZAP and ReOpti
                  zapped_track_limit = 0x031E #zap range zoneposition-30, zoneposition+3
                  if self.getParam('SEG_BER_MEAS', False):
                     objVbarOpti = CRdOpti(self.dut, {'ZONES':range(self.numUserZones)})
                     # ZAP all Zones Position 198
                     objVbarOpti.optiZAP(range(self.numUserZones),trackLimit=zapped_track_limit)
                     # ZAP all Zones0,1 Position 0
                     objVbarOpti.optiZAP([0,1],trackLimit=0x001E,zonePos=0)
                  else:
                     objVbarOpti = CRdOpti(self.dut, {'ZONES':TP.prm_VBAR_ATI_51['ZONES']})
                     objVbarOpti.optiZAP(TP.prm_VBAR_ATI_51['ZONES'],trackLimit=zapped_track_limit)
                  if testSwitch.VBART51_MEASURE_ODTRACK:
                     objVbarOpti.optiZAP(TP.prm_VBAR_ATI_51['ZONES_WITH_OD_POSITION'],trackLimit=zapped_track_limit,zonePos=1)#The additional position is done on OD zones, refer to TP.prm_VBAR_ATI_51['ZONEPOS'].
                     
                  #=== ReOpti
                  objVbarOpti.run()
         
         # Report the ADC Summary Table, need SET_ADC_FMT
         if self.getParam('ADC_SUMMARY', False):
            limits = {
               'MAX_BPI_STEP'             : self.getParam('MAX_BPI_STEP', 100.0) + niblet.settings['MAX_BPI_STEP_ADJ'],
               'MAX_BPI_PICKER_ADJ'       : self.getParam('MAX_BPI_PICKER_ADJ', 100.0),
               'MAX_TPI_PICKER_ADJ'       : self.getParam('MAX_TPI_PICKER_ADJ', 100.0),
               'UPDATE_SQUEEZE_MICROJOG'  : self.getParam('UPDATE_SQUEEZE_MICROJOG',0),
               'UPDATE_SHINGLE_DIRECTION' : self.getParam('UPDATE_SHINGLE_DIRECTION',1),
               'SPC_ID_BANDED_TPI'        : 25,
               'RD_OFST'                  : TP.RD_OFST_SEL_FMT_PICKER,
            }
            if self.getParam('PREVENT_FMT_SUM_TBL_LD_TO_EDW', False):
               SendVbarFmtSummaryToEDW = False
            else:
               SendVbarFmtSummaryToEDW = True
               
            if testSwitch.FE_0232067_211428_VBAR_USE_DESPERADO_PLUS_FORMAT_PICKER:
               self.objPicker = CDesperadoPlusPicker(niblet, self.measAllZns, limits, SendVbarFmtSummaryToEDW)
            elif testSwitch.DESPERADO:
               self.objPicker = CDesperadoPicker(niblet, self.measAllZns, limits, SendVbarFmtSummaryToEDW)
            else:
               self.objPicker = CPicker(niblet, self.measAllZns, limits, SendVbarFmtSummaryToEDW)
            
            if not testSwitch.FE_0184102_326816_ZONED_SERVO_SUPPORT:
               self.objPicker.reportADCSummary()
            else:
               self.objPicker.reportZSADCSummary()
            
         #### Adjust BPI Margin Threshold by SEGMENTED BER ####
         if self.getParam('SEG_BER_MEAS', False) and self.nibletIndex == 0 and not testSwitch.virtualRun: ## Execute SEG_BER only on first niblet level
            if verbose:
               objMsg.printMsg('Measure Segmented BER in all zones')
               objMsg.printMsg('pick() parm:SEG_BER_MEAS')

            oMeas = CMeasureBPIAndTPIinAllZones(self.measAllZns)
            if testSwitch.FE_0150693_409401_P_KORAT_ZAP_OTF:
               self.measAllZns = oMeas.measureSegmented_BPIMargin(oMeas, range(self.numUserZones), zapOTF=1)
            else:
               self.measAllZns = oMeas.measureSegmented_BPIMargin(oMeas, range(self.numUserZones))
         
         #### Measure Measure squeeze BPI and Adjust BPI Margin, need SET_ADC_FMT
         if self.getParam('SQZ_BPIC_MEAS', False):
            if self.nibletIndex == 0 :
               oMeas = CMeasureBPIAndTPIinAllZones_UnvisitedZones(self.measAllZns)
               if self.params.get('SQZ_BPIC_ZONES'):
                  NumZone = eval(str(self.params.get('SQZ_BPIC_ZONES')))
                  smr_zones = [zn for zn in NumZone if niblet.settings['TracksPerBand'][zn] > 1]
                  save_znlist = [zn for zn in xrange(self.numUserZones) if niblet.settings['TracksPerBand'][zn] > 1 and zn not in TP.MC_ZONE]
               else:
                  smr_zones = [zn for zn in xrange(self.numUserZones) if niblet.settings['TracksPerBand'][zn] > 1]
                  save_znlist = smr_zones
               if verbose:
                  objMsg.printMsg("SQZ_BPI base_zn_list: %s" % smr_zones)
                  objMsg.printMsg("SQZ_BPI save_zn_list: %s" % save_znlist)
               oMeas.measureSQZBPIC(smr_zones)
               oMeas.filterMeasurements('SQZ_BPI', base_zn_list = smr_zones, Fit_2ndOrder = 0, save_zn_list = save_znlist)
            else:
               printDbgMsg('BYPASS SQUEEZE BPI ===================================================================')

         #### Measure OTC and Adjust TPI Margin, need SET_ADC_FMT ####
         if self.getParam('OTC_MARGIN_MEAS', False) and self.nibletIndex == 0:
            #=== Run VBAR OTC & get Tpi Margin Threshold scale by zone by head
            oMeas = CMeasureBPIAndTPIinAllZones_UnvisitedZones(self.measAllZns)
            # Reset the Rd Offset for now in order to be consistent
            if testSwitch.OTC_RESET_RD_OFFSET_BEFORE_TUNE or self.dut.currentState in ['VBAR_ZN','VBAR_MARGIN']:
               oMeas.Reset_Read_offset()
               
            meas_zones = eval(str(self.getParam('OTC_MARGIN_ZONES', "range(self.numUserZones)")))
            znlist = [zn for zn in meas_zones if niblet.settings['TracksPerBand'][zn] > 1]
            update_zn = [zn for zn in xrange(self.numUserZones) if niblet.settings['TracksPerBand'][zn] > 1]
               
            if verbose:
               objMsg.printMsg("TPI_OTC base_zn_list: %s" % smr_znLst)
               objMsg.printMsg("TPI_OTC save_zn_list: %s" % save_znlist)
            
            if self.getParam('OTC_MARGIN_V2', False): # Track Pitch based OTC
               oMeas.measureTPI_OTCV3(znlist, update_zn)
            else: # Chengai OTC Mode
               oMeas.measureTPI_OTC(znlist)
               if testSwitch.FE_0293167_356688_VBAR_MARGIN_ZONE_ALIGNMENT:
                  oMeas.filterMeasurements('TPI_OTC', base_zn_list = znlist, Fit_2ndOrder = 0, save_zn_list = update_zn)
                  
         #### Measure OTC and Adjust TPI Margin and/or Reader offset ####
         if self.getParam('OTC_INTERBANDMEAS', False):
            if verbose:
               objMsg.printMsg('pick() OTC Interband Measurements')
            
            if testSwitch.FAST_2D_VBAR_UNVISITED_ZONE: 
               oMeas = CMeasureBPIAndTPIinAllZones_UnvisitedZones(self.measAllZns)
            else:
               oMeas = CMeasureBPIAndTPIinAllZones(self.measAllZns)
               
            # Reset the Rd Offset for now in order to be consistent
            #if testSwitch.OTC_RESET_RD_OFFSET_BEFORE_TUNE:
            #   oMeas.Reset_Read_offset()
                  
            meas_zones = eval(str(self.getParam('ZONES', "range(self.numUserZones)")))
            znlist = [zn for zn in meas_zones if niblet.settings['TracksPerBand'][zn] > 1]
            #=== Run VBAR Interband OTC Test
            oMeas.measure_InterbandOTC(znlist)

         if self.getParam('ZIPPER_ZONE_UPDATE', False):
            limits = {
                  'MAX_BPI_STEP'             : self.getParam('MAX_BPI_STEP', 100.0) + niblet.settings['MAX_BPI_STEP_ADJ'],
                  'MAX_BPI_PICKER_ADJ'       : self.getParam('MAX_BPI_PICKER_ADJ', 100.0),
                  'MAX_TPI_PICKER_ADJ'       : self.getParam('MAX_TPI_PICKER_ADJ', 100.0),
                  'UPDATE_SQUEEZE_MICROJOG'  : self.getParam('UPDATE_SQUEEZE_MICROJOG',0),
                  'UPDATE_SHINGLE_DIRECTION' : self.getParam('UPDATE_SHINGLE_DIRECTION',1),
                  'SPC_ID_BANDED_TPI'        : TP.SPC_ID_BANDED_TPI_FMT_PICKER,
                  'RD_OFST'                  : TP.RD_OFST_SEL_FMT_PICKER,
            }
            SendVbarFmtSummaryToEDW = False
            if testSwitch.FE_0232067_211428_VBAR_USE_DESPERADO_PLUS_FORMAT_PICKER:
               self.objPicker = CDesperadoPlusPicker(niblet, self.measAllZns, limits, SendVbarFmtSummaryToEDW)
            elif testSwitch.DESPERADO:
               self.objPicker = CDesperadoPicker(niblet, self.measAllZns, limits, SendVbarFmtSummaryToEDW)
            else:
               self.objPicker = CPicker(niblet, self.measAllZns, limits, SendVbarFmtSummaryToEDW)
            # Get the zone which the sector per track at BPI.bin is unreliable.
            ExecuteTestT172 = not self.getParam('ADC_SUMMARY', False)
            self.dut.dataZonesWithZipperZones = self.objPicker.getDataZoneWithZipperZones(ExecuteTestT172) # can fine tune the zone table
            for hd in range(self.numHeads):
               for index in range(len(TP.DEFAULT_ZONES_WITH_ZIPPER)):
                  if TP.DEFAULT_ZONES_WITH_ZIPPER[index] not in self.dut.dataZonesWithZipperZones[hd]:
                     self.dut.dataZonesWithZipperZones[hd].append(TP.DEFAULT_ZONES_WITH_ZIPPER[index])
            objMsg.printMsg('self.dut.dataZonesWithZipperZones %s' % (str(self.dut.dataZonesWithZipperZones)))
            
         #### Adjust TPI Margin Threshold by ATI test ####
         if self.getParam('ATI_MEAS', False):
            if self.nibletIndex == 0:
               #=== Run T51 & get Tpi Margin Threshold scale by zone by head
               self.TpiMrgnThresScaleByHdByZn = {}
               CTpiMrgnThresScaler(self.TpiMrgnThresScaleByHdByZn,pickerData = self.objPicker, TPIMThreshold = TP.TPIAdjustDuringVBART51,otfBERThreshold = niblet.settings['ATITargetOTFBER'])
               if verbose:
                  objMsg.printMsg("TPIMrgnThresScaleByHdByZn after VBAR ATI:%s" % self.TpiMrgnThresScaleByHdByZn)

            elif self.nibletIndex == 1 and not testSwitch.SMR:
               NativeTpiMrgnThresScaleByHdByZn = self.TpiMrgnThresScaleByHdByZn.copy()
               CTpiMrgnThresScaler(self.TpiMrgnThresScaleByHdByZn,pickerData=self.objPicker, TPIMThreshold=TP.TPIAdjustDuringVBART51,otfBERThreshold=niblet.settings['ATITargetOTFBER'])
               for hd in range(self.numHeads):
                  for zn in range(self.numUserZones):
                     self.TpiMrgnThresScaleByHdByZn['TPIM'][hd,zn] += NativeTpiMrgnThresScaleByHdByZn['TPIM'][hd,zn]
               printDbgMsg("TPIMrgnThresScaleByHdByZn after VBAR ATI for SBS:%s" % self.TpiMrgnThresScaleByHdByZn)
            
            for hd in xrange(self.numHeads):
               for zn in xrange(self.numUserZones):
                  self.measAllZns.setRecord('TPIMA', self.TpiMrgnThresScaleByHdByZn['TPIM'].get((hd,zn),0), hd, zn)
                     
         #### Adjust TPI Margin Threshold by ATI test (used for HMS process only, ATI_MEAS and ATI_MEAS_HMS should be mutually exclusive)####
         if self.getParam('ATI_MEAS_HMS', False):
            if self.nibletIndex == 0 :
               from base_SerialTest import CRdOpti
               limits = {
                  'MAX_BPI_STEP'       : self.getParam('MAX_BPI_STEP', 100.0) + niblet.settings['MAX_BPI_STEP_ADJ'],
                  'MAX_BPI_PICKER_ADJ' : self.getParam('MAX_BPI_PICKER_ADJ', 100.0),
                  'MAX_TPI_PICKER_ADJ' : self.getParam('MAX_TPI_PICKER_ADJ', 100.0),
                  'UPDATE_SQUEEZE_MICROJOG' : self.getParam('UPDATE_SQUEEZE_MICROJOG',0),
                  'UPDATE_SHINGLE_DIRECTION' : self.getParam('UPDATE_SHINGLE_DIRECTION',0)
                  }
               if verbose:
                  objMsg.printMsg('pick() ATI Test  parm:ATI_MEAS_HMS')

               self.objPicker = CPicker(niblet,self.measAllZns,limits) #the the data in the ojbPicker will have the measurement adjusted by MeasurementMargin and WriteFaultThreshold already

               #=== Set TPIC & BPIC format to drive
               self.objPicker.sendFormatToDrive = 1
               self.objPicker.BpiFileCapacityCalc = 0
               self.objPicker.setFormat('BPI',movezoneboundaries=True)
               self.objPicker.setFormat('TPI')
               getVbarGlobalVar()['formatReload'] = True
               CVbarFormatScaler() #for debuging purpose, to display the format after the above format setting

               #print out the values in objPicker.data after the format is set
               if 1:#verbose:
                  objMsg.printMsg('=======VBAR_ATI, After new format is set:========')
                  names = [name for name in self.objPicker.getNameList() if not name.startswith('cfg')]
                  names.sort()
                  for hd in xrange(self.numHeads):
                     for zn in xrange(self.numUserZones):
                        for name in names:
                           objMsg.printMsg('CPicker_Init %d, %d %s: %s' % (hd, zn, name, self.objPicker.getRecord(name, hd, zn)))
               #=== Save RAP and SAP to flash
               prm = {'test_num': 178, 'prm_name': 'prm_wp_178', 'timeout': 1200, 'spc_id': 0,}
               prm.update({'CWORD1':0x0620})
               getVbarGlobalClass(CProcess).St(prm)

               if testSwitch.RUN_T176_IN_VBAR and not testSwitch.FE_0269922_348085_P_SIGMUND_IN_FACTORY:
                  from base_SerialTest import CReadWriteGapCal
                  #Gap CAL
                  CReadWriteGapCal(self.dut, {'SKIP_SYS_ZONE' : 1}).run()

               #=== ZAP and ReOpti
               objVbarOpti = CRdOpti(self.dut, {'ZONES':TP.prm_VBAR_ATI_51['ZONES']})
               zapped_track_limit = 0x031E #zap range zoneposition-30, zoneposition+3
               objVbarOpti.optiZAP(TP.prm_VBAR_ATI_51['ZONES'],trackLimit=zapped_track_limit)
               if testSwitch.VBART51_MEASURE_ODTRACK:
                  objVbarOpti.optiZAP([0,2,6],trackLimit=zapped_track_limit,zonePos=1)#The additional position is done on OD zones, refer to TP.prm_VBAR_ATI_51['ZONEPOS'].

               #=== ReOpti
               #objVbarOpti = CRdOpti(self.__dut, {'ZONES':TP.prm_VBAR_ATI_51['ZONES']})
               objVbarOpti.run()

               #=== Run T51 & get Tpi Margin Threshold scale by zone by head
               self.TpiMrgnThresScaleByHdByZn = {}
               CTpiMrgnThresScaler(self.TpiMrgnThresScaleByHdByZn,pickerData = self.objPicker, TPIMThreshold = 0,otfBERThreshold = niblet.settings['ATITargetOTFBER'])
               objMsg.printMsg("TPIMrgnThresScaleByHdByZn after VBAR ATI:%s" % self.TpiMrgnThresScaleByHdByZn)

            elif self.nibletIndex == 1 :
               CTpiMrgnThresScaler(self.TpiMrgnThresScaleByHdByZn,pickerData = self.objPicker, TPIMThreshold = 0,otfBERThreshold = niblet.settings['ATITargetOTFBER'])
               objMsg.printMsg("TPIMrgnThresScaleByHdByZn after VBAR ATI for SBS:%s" % self.TpiMrgnThresScaleByHdByZn)
            for hd in xrange(self.numHeads):
               for zn in xrange(self.numUserZones):
                  tpima = self.measAllZns.getRecord('TPIMA',hd,zn) + self.TpiMrgnThresScaleByHdByZn['TPIM'].get((hd,zn),0)
                  self.measAllZns.setRecord('TPIMA', tpima, hd, zn)

         #### Measurements are complete; skip them for future niblets ####
         self.params.update({'ZN_OPTI' : 0, 'ZN_MEAS' : 0, 'OTC_MARGIN_MEAS' : 0, 
                             'SMR_MEAS' : 0, 'SQZ_BPIC_MEAS' : 0, 'TPI_DSS_MEAS': 0, 
                             'ADC_SUMMARY': 0, 'ZIPPER_ZONE_UPDATE': 0, 'RD_OFT_MEAS': 0,
                           })

         #### Run the format picker ####
         if self.getParam('FMT_PICKER', False):
            limits = {
               'MAX_BPI_STEP'               : self.getParam('MAX_BPI_STEP', 100.0) + niblet.settings['MAX_BPI_STEP_ADJ'],
               'MAX_BPI_PICKER_ADJ'         : self.getParam('MAX_BPI_PICKER_ADJ', 100.0),
               'MAX_TPI_PICKER_ADJ'         : self.getParam('MAX_TPI_PICKER_ADJ', 100.0),
               'UPDATE_SQUEEZE_MICROJOG'    : self.getParam('UPDATE_SQUEEZE_MICROJOG',0),
               'UPDATE_SHINGLE_DIRECTION'   : self.getParam('UPDATE_SHINGLE_DIRECTION',0),
               'RD_OFST'                    : TP.RD_OFST_SEL_FMT_PICKER,
               'SPC_ID_BANDED_TPI'          : TP.SPC_ID_BANDED_TPI_FMT_PICKER,
               'DUMP_BANDED_TPI_TBL'        : (self.nibletIndex == 0) and 1 or 0,
               'DUMP_MAX_FORMAT_SUMMARY_TBL': (self.nibletIndex == 0) and 1 or 0,
            }
            if verbose:
               objMsg.printMsg('pick() Run the format picker  parm:FMT_PICKER')

            # Consolidate the BPI Margins
            niblet.settings['Niblet_Index'] = self.nibletIndex
            for hd in xrange(self.numHeads):
               for zn in xrange(self.numUserZones):
                  meas = CVbarDataHelper(self.measAllZns, hd, zn)
                  Final_SEG_BPIM = 0
                  bpim_sqzbpic = 0 
                  if testSwitch.FE_SEGMENTED_BPIC:
                     if meas['BPIMS'] > TP.MIN_SEGMENTED_BPIM_ADJUST and zn in TP.SEGMENTED_ZN_ADJUST:
                        Final_SEG_BPIM = max(meas['BPIMS'],Final_SEG_BPIM)
                     if meas['BPIMF'] > TP.MIN_SEGMENTED_BPIM_ADJUST and zn in TP.FSOW_ZN_ADJUST:
                        Final_SEG_BPIM = max(meas['BPIMF'],Final_SEG_BPIM)
                        
                  if testSwitch.FE_0254388_504159_SQZ_BPIC:
                     if meas['SQZ_BPI'] > 0: bpim_sqzbpic = meas['BPI'] - meas['SQZ_BPI']

                  # Update to the niblet if this switch is ON, else, everything will just be data collection
                  if testSwitch.FE_CONSOLIDATED_BPI_MARGIN:
                     if testSwitch.SCP_HMS:
                        niblet.settings['BPIMarginThreshold'][hd][zn] = \
                           max(niblet.settings['BPIMarginThreshold'][hd][zn], meas['BPIMH'])
                     if testSwitch.FE_0254388_504159_SQZ_BPIC:
                        niblet.settings['BPIMarginThreshold'][hd][zn] = \
                           max(niblet.settings['BPIMarginThreshold'][hd][zn], min(bpim_sqzbpic, TP.MAX_SQZBPI_MARGIN))
                     if testSwitch.FE_SEGMENTED_BPIC:
                        niblet.settings['BPIMarginThreshold'][hd][zn] = \
                           max(niblet.settings['BPIMarginThreshold'][hd][zn], Final_SEG_BPIM)
                        
            # --- Choose Fmt Picker for Constant margin mode ---
            if testSwitch.FE_0115422_340210_FORMATS_BY_MARGIN or self.getParam('CONST_MARGIN', False):
               if testSwitch.DESPERADO:
                  picker = CSmrMarginPicker(niblet, self.measAllZns, limits)
               else:
                  # Note: One of two different functions will be run here, depending on the
                  # setting of the FE_0115422_340210_FORMATS_BY_MARGIN flag.
                  picker = CMarginPicker(niblet, self.measAllZns, limits)

            # --- Choose Fmt Picker for Normal Format Picker mode ---
            else:
               if self.getParam('PREVENT_FMT_SUM_TBL_LD_TO_EDW', False):
                  SendVbarFmtSummaryToEDW = False
               else:
                  SendVbarFmtSummaryToEDW = True

               if testSwitch.FE_0232067_211428_VBAR_USE_DESPERADO_PLUS_FORMAT_PICKER:
                  picker = CDesperadoPlusPicker(niblet, self.measAllZns, limits, SendVbarFmtSummaryToEDW)
               elif testSwitch.DESPERADO:
                  picker = CDesperadoPicker(niblet, self.measAllZns, limits, SendVbarFmtSummaryToEDW)
               else:
                  picker = CPicker(niblet, self.measAllZns, limits, SendVbarFmtSummaryToEDW)

            # Consolidate the BPI Margins for Printing
            if testSwitch.FE_SEGMENTED_BPIC:
               picker['BPIMS'] = deepcopy(self.measAllZns['BPIMS'])
               picker['BPIMF'] = deepcopy(self.measAllZns['BPIMF'])
            else:
               picker['BPIMS'] = array('f', [0.0]*self.numUserZones*self.numHeads)
               picker['BPIMF'] = array('f', [0.0]*self.numUserZones*self.numHeads)
               
            if testSwitch.SCP_HMS:
               picker['BPIMH'] = deepcopy(self.measAllZns['BPIMH'])
            else:
               picker['BPIMH'] = array('f', [0.0]*self.numUserZones*self.numHeads)
               
            if testSwitch.FE_0254388_504159_SQZ_BPIC and meas['SQZ_BPI'] > 0:
               for hd in xrange(self.numHeads):
                  for zn in xrange(self.numUserZones):
                     meas = CVbarDataHelper(self.measAllZns, hd, zn)
                     picker.setRecord('BPIMSQZ',meas['BPI']-meas['SQZ_BPI'],hd,zn)
            else:
               picker['BPIMSQZ'] = array('f', [0.0]*self.numUserZones*self.numHeads)

            # Consolidate the TPI Margins
            if testSwitch.FAST_2D_VBAR:
               if testSwitch.RUN_ATI_IN_VBAR:
                  for hd in range(self.numHeads):
                     for zn in TP.prm_VBAR_ATI_51['ZONES']:
                        pickerData = CVbarDataHelper(picker, hd, zn)
                        if testSwitch.VBAR_TPIM_SLOPE_CAL and zn not in TP.prm_VBAR_ATI_51['ZONE_FOR_COLLECTION'] \
                           and meas['TPIMA'] is not None:
                           pickerData['TpiMarginThresScale'] = max(meas['TPIMA'],niblet.settings['TPIMarginThreshold'][zn])
                        else:
                           pickerData['TpiMarginThresScale'] = 0.0
               if testSwitch.FAST_2D_S2D_TEST:
                  for hd in range(self.numHeads):
                     for zn in range(self.numUserZones):
                        pickerData = CVbarDataHelper(picker, hd, zn)
                        meas = self.measAllZns.getNibletizedRecord(hd,zn)
                        if niblet.settings['TracksPerBand'][zn] == 1:
                           pickerData['TpiMarginThresScale'] = 0.0
                        else:
                           if meas['TPI_ODSS'] > meas['TPI_IDSS']:
                              max_tpi = meas['TPI_ODSS2D']
                           else:
                              max_tpi = meas['TPI_IDSS2D']
                           pickerData['TpiMarginThresScale'] = max(meas['TPI_IDSS'],meas['TPI_ODSS']) - max_tpi

               elif testSwitch.VBAR_MARGIN_BY_OTC and self.dut.currentState in ['VBAR_ZN','VBAR_FMT_PICKER','VBAR_OTC', 'VBAR_OTC2']:
                  for hd in xrange(self.numHeads):
                     for zn in xrange(self.numUserZones):
                        pickerData = CVbarDataHelper(picker, hd, zn)
                        meas = self.measAllZns.getNibletizedRecord(hd, zn)
                        if niblet.settings['TracksPerBand'][zn] == 1:
                           if not testSwitch.RUN_ATI_IN_VBAR:
                              pickerData['TpiMarginThresScale'] = 0.0
                        elif testSwitch.FE_0293889_348429_VBAR_MARGIN_BY_OTCTP:
                           pickerData['TpiMarginThresScale'] = 0.0   # Will use another parameter
                        else: #SMR zone
                           pickerData['TpiMarginThresScale'] = max( max(meas['TPI_IDSS'],meas['TPI_ODSS']) - meas['TPI_OTC'],niblet.settings['TPIMarginThreshold'][zn])
               
               ### Consolidate Printing tpi margin scale inside desperado picker class ###
               if verbose: picker.dumpTpiMarginScale()
               
            else:
               if testSwitch.VBAR_TPI_MARGIN_THRESHOLD_BY_HD_BY_ZN and (testSwitch.RUN_ATI_IN_VBAR or self.getParam('ATI_MEAS_HMS', False)):
                  for hd in xrange(self.numHeads):
                     for zn in xrange(self.numUserZones):
                        pickerData = CVbarDataHelper(picker, hd, zn)
                        if testSwitch.VBAR_TPIM_SLOPE_CAL:
                           pickerData['TpiMarginThresScale'] = max(self.TpiMrgnThresScaleByHdByZn['TPIM'][hd,zn],niblet.settings['TPIMarginThreshold'][zn])
                        else:
                           pickerData['TpiMarginThresScale'] = self.TpiMrgnThresScaleByHdByZn[hd,zn]

            if self.dut.currentState in ['VBAR_OTC', 'VBAR_OTC2']:
               printDbgMsg('SetFormat_UJOG')
               picker['AdjustedTpiFormat'] = array('c', ['T']*self.numUserZones*self.numHeads)

               picker.sendFormatToDrive = True
               picker.setFormat('UJOG', consolidateByZone = testSwitch.FE_0262424_504159_ST210_SETTING_FORMAT_IN_ZONE)
               picker.sendFormatToDrive = False
               status = ATPI_PASS
               # Write RAP and SAP data to flash
               getVbarGlobalClass(CProcess).St({'test_num': 178, 'prm_name': 'Save SAP AND RAP to Flash', 'CWORD1':0x0620, 'timeout': 1200, 'spc_id': 0,})
            else:
               if self.getParam('LBR', False):                  
                  picker.getZB('RAP')
                  picker.FindNZB = 1

               # --- Run the chosen Picker ---
               status = picker.pickBPITPI()
               
               if status != ATPI_PASS and self.getParam('LBR', False):
                  objMsg.printMsg('*'*40 + ' Last Band Recovery triggered ' + '*'*40)                  
                  picker.LBR = 1
                  self.params.update({'LBR': 0,})
                  status = picker.pickBPITPI()
                  
               if status == ATPI_PASS and testSwitch.FE_0184102_326816_ZONED_SERVO_SUPPORT:
                  picker.syncZoneServoBoundary()

            if status != ATPI_PASS:
               printDbgMsg('***************************** %s : %s *****************************'% self.lookupFailureInfo(status))
               self.resetForWaterfall()
               continue

         if status == ATPI_PASS:
            # Print final status
            printDbgMsg('***************************** %s : %s *****************************'% self.lookupFailureInfo(status))
            break  # Done, found niblet that works

      #### Handle final decision ####
      msg, errCode = self.lookupFailureInfo(status)
      printDbgMsg('='*35)
      printDbgMsg('ATPI/ABPI Picker Decision: %s' % msg)

      #### Save persistent data ####
      self.saveData()
      if self.getParam('HANDLE_NIBLET', True):
         if status == ATPI_PASS:
            if not testSwitch.CM_REDUCTION_REDUCE_PRINTMSG:
               objMsg.printMsg('SUCCESSFUL NIBLET:')
               niblet.printTable()
            niblet.printDbLog()
   
            if testSwitch.FE_0119998_231166_FACTORY_VBAR_ADC_ENHANCEMENTS:
               DriveAttributes["BPI_MIN_AVERAGE"] =  niblet.settings['BPIMinAvg']
               DriveAttributes["BPI_MAX_AVERAGE"] =  niblet.settings['BPIMaxAvg']
   
            if testSwitch.FE_0115422_340210_FORMATS_BY_MARGIN:
               niblet.settings['DRIVE_CAPACITY'] = self.getCapacity()
            if testSwitch.CONDITIONAL_RUN_HMS:
               objMsg.printMsg('5.skip the rest of the HMS, skipHMS=%s' % self.dut.skipHMS)
            self.setMaxLBA(niblet)
   
            # HMS Iteration Control
            num_iterations = self.getParam('ITERATIONS', 0)
            if num_iterations:
               self.dut.vbar_iterations += 1
               if testSwitch.CONDITIONAL_RUN_HMS:
                  objMsg.printMsg('vbar_iterations=%d num_iter=%d skipHMS=%s' %(self.dut.vbar_iterations,num_iterations,self.dut.skipHMS))
               if self.dut.vbar_iterations < num_iterations:
                  self.dut.stateTransitionEvent = 'reRunVBAR'
               else:
                  self.dut.vbar_iterations = 0 # Reset for future states to use
                  if testSwitch.CONDITIONAL_RUN_HMS:
                     objMsg.printMsg("next_State=%s" % self.dut.nextState)
         else:
            if not testSwitch.virtualRun:
               raiseException(errCode)

   #-------------------------------------------------------------------------------------------------------
   def BPINominalBHBZV2(self):
      from base_SerialTest import SimpleOpti
      testZones = TP.Measured_BPINOMINAL_Zones
      bpiparams = {}
      if testSwitch.TTR_REDUCED_PARAMS_T251:
         # do opti tune based on TP.base_ReducedPrm_251
         if (testSwitch.TTR_BPINOMINAL_V2 and self.dut.nextState == 'BPINOMINAL'):
            bpiparams = TP.base_FirstOptiPrm_251.copy()     # v2: full params in bpinominal 1, 2-pt only
            if (self.numUserZones < 32):
               testZones = [4, 28]
            else:
               if (self.numUserZones == 120):
                  testZones = [8, 110]
               elif (self.numUserZones == 150):
                  testZones = [10, 138]
               elif (self.numUserZones == 180):
                  testZones = [12, 165]
               else:
                  testZones = [4, 55]
         else: bpiparams = TP.base_ReducedPrm_251.copy()       #  partial zone/params in 2nd bpinominal

      # Build a head mask comprised of all heads on the drive.
      hd_mask = 0
      for hd in range(self.numHeads):
         hd_mask |= (1 << hd)

      bpiparams.update({'ZONES':testZones, 'ZONE_POS':TP.VBAR_ZONE_POS, 'DISABLE_ZAP': False})
      SimpleOpti(self.dut, bpiparams).run()
      if testSwitch.FE_0262766_480561_RUN_MRBIAS_OPTI_T251 and self.params.get('RUN_MRBIAS_OPTI', 0):
         from RdWr import CRdWrOpti
         oRdWr = CRdWrOpti(self.params)

         optiPrm = self.params.get('param', 'mrbias_OptiPrm_251')
         oRdWr.phastOpti(getattr(TP, optiPrm).copy(), maxRetries = 3)
         
         SetFailSafe()
         prm_PrePostOptiAudit_250_local = TP.prm_PrePostOptiAudit_250.copy()
         if (self.params.get('ZONES') and \
            (len(self.params.get('ZONES')) < (self.numUserZones)) ):
            zone_mask_list = self.oUtility.convertZoneListtoZoneMask(self.params['ZONES'])
            prm_PrePostOptiAudit_250_local['ZONE_MASK'] = self.oUtility.ReturnTestCylWord(zone_mask_list[0])
            prm_PrePostOptiAudit_250_local['ZONE_MASK_EXT'] = self.oUtility.ReturnTestCylWord(zone_mask_list[1])
         if (self.params.get('HEAD', -1) != -1):
            prm_PrePostOptiAudit_250_local['TEST_HEAD'] = self.oUtility.converttoHeadRangeMask(self.params.get('HEAD'), self.params.get('HEAD'))
         getVbarGlobalClass(CProcess).St(prm_PrePostOptiAudit_250_local)
         ClearFailSafe()

      #Step1: Measure BPI for all the testZones for all heads
      # oMeas will have a newly created CVbarWpMeasurement dictionary, which will be tossed upon exit from this function.
      objMsg.printMsg("NUM_WRITE_POWERS %d" % (self.NUM_WRITE_POWERS))
      oMeas = CMeasureBPIAndTPIinWpZones(CVbarWpMeasurement(initStore=True, numOfWp=self.NUM_WRITE_POWERS))
      # Measure BPI Nominal on all heads in BPI Nominal zones.
      #oMeas.measureBPINominal(hd_mask, zn_mask, use_wp_in_rap=True)
      oMeas.measureBPINominal(hd_mask, testZones, use_wp_in_rap=True)

      #Step2: Interpolate the BPI value for all other zones and populate them into the records in CVbarWpMeasurement
      if (testSwitch.TTR_BPINOMINAL_V2_CONST_AVG and self.dut.nextState == 'BPINOMINAL'):
         # TODO: optimize this routine
         for hd in xrange(self.numHeads):
            sumBPI = 0.0
            for zn in testZones:
               sumBPI += oMeas.measurements.getRecord('BPI',hd,zn,TP.WPForVBPINominalMeasurements)
            aveBPI = sumBPI / len(testZones)
            #objMsg.printMsg("===== Hd=%d Sum=%f Avg=%f =====" % (hd,sumBPI,aveBPI))
            for zn in range(self.numUserZones):
               oMeas.measurements.setRecord('BPI',aveBPI,hd,zn,TP.WPForVBPINominalMeasurements)

      else:
         for hd in xrange(self.numHeads):
            for idx in xrange(len(testZones)-1):
               measX1 = oMeas.measurements.getRecord('BPI', hd, testZones[idx], TP.WPForVBPINominalMeasurements)
               measX2 = oMeas.measurements.getRecord('BPI', hd, testZones[idx+1], TP.WPForVBPINominalMeasurements)
               slope = (measX2 - measX1) / (testZones[idx+1] - testZones[idx])
               if idx == 0 and testZones[idx] > 0:   # extrapolate to zone 0 if needed
                  objMsg.printMsg(">> Extrapolate to Zone 0. <<")
                  scale = slope
                  for zn in range(testZones[idx]):
                     oMeas.measurements.setRecord('BPI', measX1 - scale, hd, zn, TP.WPForVBPINominalMeasurements)
                     scale += slope
               scale = slope
               for zn in range(testZones[idx]+1,testZones[idx+1]):
                  oMeas.measurements.setRecord('BPI', measX1 + scale, hd, zn, TP.WPForVBPINominalMeasurements)
                  scale += slope
               if idx == (len(testZones)-2) and testZones[idx+1] < (self.numUserZones-1):   # extrapolate to last zone if needed
                  objMsg.printMsg(">> Extrapolate to Zone %d. <<" % (self.numUserZones-1))
                  scale = slope
                  for zn in xrange(testZones[len(testZones)-1] + 1, self.numUserZones):
                     #scale = slope * count
                     oMeas.measurements.setRecord('BPI', measX2 + scale, hd, zn, TP.WPForVBPINominalMeasurements)
                     scale += slope

      
      for hd in xrange(self.numHeads):
         for zn in xrange(self.numUserZones):
            meas_wp  = oMeas.measurements.getRecord('BPI', hd, zn, TP.WPForVBPINominalMeasurements)
            #copy to measurement dictionary for storage inside system
            self.measAllZns.setRecord('BPI', meas_wp, hd, zn)
            if verbose:
               #debug printing
               objMsg.printMsg("hd=%d Zn=%d BPI=%f %s" % (hd,zn, meas_wp, TP.WPForVBPINominalMeasurements))

      # Find the format table that is just higher than the desired scale factor
      objFormat = CDriveFormat(oMeas.measurements)
      objFormat.getBpiTpiTables('BPI') #this will populate the objFormat.data[hd][zn]['BpiFormat'] with format by looking up the BPI Format Table
      #Force to update by head by zone the BPI config as the T176 need all zone SgateToRgate timing reload back to default
      if testSwitch.FORCE_UPDATE_BPI_ALL_HEADS_ALL_ZONES:
         objFormat['AdjustedBpiFormat'] = array('c', ['T']*self.numUserZones*self.numHeads)
      else:
         for hd in xrange(self.numHeads):
            for zn in xrange(self.numUserZones):
               pickerData  = CVbarDataHelper(objFormat, hd, zn)
               # If the zone has been changed, set flag to update the format
               if pickerData['BpiFormat'] != oMeas.formatScaler.getFormat(hd, zn, 'BPI'):
                  pickerData['AdjustedBpiFormat'] = 'T'
               else:
                  pickerData['AdjustedBpiFormat'] = 'F'
      objFormat.updateDriveFormat('BPI')

      if verbose:
         # Print result
         objMsg.printMsg("NEW_BPI_NOMINAL" + "\n" + "="*30)
         objMsg.printMsg("%2s  %2s  %6s  %6s" %("Hd", "Zn", "BpiCap", "BpiFmt") + "\n" + "="*30)
         for hd in xrange(self.numHeads):
            for zn in xrange(self.numUserZones):
               pickerData  = CVbarDataHelper(objFormat, hd, zn)
               objMsg.printMsg("%2d  %2d  %6.4f  %6d" %(hd, zn, pickerData['BpiCapability'], pickerData['BpiFormat']))

   #-------------------------------------------------------------------------------------------------------
   #SCP routine to detect the current nominal by looking up ZoneTable and set it to the drive
   #this is useful when the default NRZ frequency is not the nominal value as indicated in the BPI file.
   def ReloadNewBpiNominalByHdByZn(self, format_to_set=None):
      # if testSwitch.virtualRun:
         # return
      self.defaultbpiformats = {}
      hdBpiFormat = []            #format to be set to each head , in the format of [-40,-40]
      metric = ['BPI', 'TPI', 'SET_MAX_LBA'] # default all
      # Display the BPI Fmt table for reference
      displayBPINominalTable()
      #=== Get Bpi info
      maxBpiProfiles = self.bpiFile.getNumBpiFormats()
      maxBpiFormat = self.bpiFile.getMaxFormat()
      nominalFormat = self.bpiFile.getNominalFormat()
      objMsg.printMsg("maxBpiProfiles=%d maxBpiFormat=%d nominalFormat=%d" % (maxBpiProfiles,maxBpiFormat,nominalFormat))

      if format_to_set == 'BPI_NOMINAL_FORMAT':
         format_to_set = nominalFormat
         metric = ['BPI']
      if (format_to_set != None):
         format_to_set = int(format_to_set) #convert to integer just in case it is passed in as string
         objMsg.printMsg("Force BPI to profile %d" % format_to_set)
         hdBpiFormat = [format_to_set - nominalFormat for hd in xrange(self.numHeads)]
         for head in xrange(self.numHeads):
            for zone in xrange(self.numUserZones):
               self.defaultbpiformats.setdefault(head, {})[zone] = {'BPIformat':format_to_set}
      else:
         #=== Get zone table
         # TODO: not optimized due to cannot test this routine
         try:
            self.__dut.dblData.Tables(TP.zone_table['table_name']).deleteIndexRecords(confirmDelete = 1)
            self.__dut.dblData.delTable(TP.zone_table['table_name'], forceDeleteDblTable = 1)
         except:
            pass
         getVbarGlobalClass(CFSO).getZoneTable(newTable=1, delTables =1, supressOutput =0)
         zt = self.dut.dblData.Tables(TP.zone_table['table_name']).tableDataObj()
         if debug_RF: objMsg.printMsg('TODO: ReloadNewBpiNominalByHdByZn: format_to_set == None')
         #=== Loop thru heads and zones
         for head in xrange(self.numHeads):
            for zone in xrange(self.numUserZones):
               #=== Get zone freq
               Index  = self.dth.getFirstRowIndexFromTable_byZone(zt, head, zone)
               nrzFreq = int(zt[Index]['NRZ_FREQ'])
               if verbose:
                  objMsg.printMsg("hd=%d zn=%d nrz=%d" % (head,zone,nrzFreq))
               fmt = maxBpiFormat
               #=== Get zone fmt
               for i in xrange(maxBpiProfiles):
                  fmtFreq = int(self.bpiFile.getFrequencyByFormatAndZone(fmt,zone,head))
                  if verbose:
                     objMsg.printMsg("i=%d fmt=%d zn=%d fmtFreq=%d" % (i,fmt,zone,fmtFreq))
                  if nrzFreq == fmtFreq:
                     break
                  fmt -= 1
               if verbose:
                  objMsg.printMsg("nominal=%d fmt=%d" % (nominalFormat,fmt))
               #if the fmt is too small, limit it to smallest fmt
               if (fmt < -nominalFormat ):
                   fmt = -nominalFormat
               bpiformat = nominalFormat + fmt
               if verbose:
                  objMsg.printMsg("bpiformat=%d" % bpiformat)
               self.defaultbpiformats.setdefault(head, {})[zone] = {'BPIformat':bpiformat}
         #find a average of fmt for the head
         for hd in xrange(self.numHeads):
            bpiFmtLst=[]
            for zn in xrange(self.numUserZones):
               bpiFmtLst.append(self.defaultbpiformats[hd][zn]['BPIformat'])
            if verbose:
               objMsg.printMsg("bpiFmtLst=%s" % bpiFmtLst)
            hdBpiFormat.append(int(mean(bpiFmtLst))-nominalFormat)
         if verbose:
            objMsg.printMsg("hdBpiFormat=%s" % hdBpiFormat)

      #set the drive BPI format
      self.setFormats(hdBpiFormat, metric)
      if verbose:
         #=== Print result
         objMsg.printMsg('INITIAL BPI NOMINAL')
         objMsg.printMsg('='*30)
         objMsg.printMsg("%2s  %2s  %10s" %("Hd", "Zn", "BpiNominal"))
         objMsg.printMsg('='*30)
         for head in xrange(self.numHeads):
            for zone in xrange(self.numUserZones):
               objMsg.printMsg("%2d  %2d  %10s" %(head, zone, self.defaultbpiformats[head][zone]['BPIformat']))
               
  #-------------------------------------------------------------------------------------------------------
  # Class method
   def ReloadZBNominal2RAP(self):
      if debug_LBR:
         getVbarGlobalClass(CProcess).St(TP.DisplayUserZB)
      objMsg.printMsg("systemAreaUserZones %s" % str(self.dut.systemAreaUserZones))
            
      NominalZB = list(list(dict() for y in xrange(self.numUserZones)) for x in xrange(self.numHeads))
      # get nominal trk from bpiFile
      for hd in xrange(self.numHeads): 
         for zn in xrange(self.numUserZones):
            NominalZB[hd][zn]['TRK_NUM'] = self.bpiFile.getNumNominalTracksInZone(0,zn)
         
      # find zn_start_cyl
      getVbarGlobalClass(CProcess).St(TP.DisplaySysZB)
      colDict = self.dut.dblData.Tables('P172_MISC_INFO').columnNameDict()
      row = self.dut.dblData.Tables('P172_MISC_INFO').rowListIter(index=len(self.dut.dblData.Tables('P172_MISC_INFO'))-1).next()
      SysZnNumNomTrk = int(row[colDict['VALUE']])
      objMsg.printMsg("SystemZoneNumNominalTracks %d" % (SysZnNumNomTrk))
      
      for hd,zn in [(hd, zn) for hd in range(self.numHeads) for zn in range(self.numUserZones)]:
         if zn == 0:
            NominalZB[hd][zn]['ZN_START_CYL'] = 0         
         elif zn == (self.dut.systemAreaUserZones[hd] + 1):
            NominalZB[hd][zn]['ZN_START_CYL'] = NominalZB[hd][zn-1]['ZN_START_CYL'] + NominalZB[hd][zn-1]['TRK_NUM'] + SysZnNumNomTrk
         else:
            NominalZB[hd][zn]['ZN_START_CYL'] = NominalZB[hd][zn-1]['ZN_START_CYL'] + NominalZB[hd][zn-1]['TRK_NUM']
            
      objMsg.printMsg("Zone Boundary from bpiFile")
      objMsg.printMsg("Hd  Zn  ZN_START_CYL  TRK_NUM")
      for hd in xrange(self.numHeads): 
         for zn in xrange(self.numUserZones):
            objMsg.printMsg("%2d  %2d  %12d  %d" % (hd, zn, NominalZB[hd][zn]['ZN_START_CYL'], NominalZB[hd][zn]['TRK_NUM']))
         
      # set nominal ZB to RAP      
      skipUpdateZn = TP.ZB_remain      
      skipUpdateZnStartCyl = [self.dut.systemAreaUserZones[hd]+1 for hd in xrange(self.numHeads)]
      
      if testSwitch.extern.FE_0270714_356688_ZB_UPDATE:
         updateZB_prm = deepcopy(TP.updateZB_178)
         UPDATE_SIZE = 30
         for hd in xrange(self.numHeads):
            ZoneNum           = [0xFFFF,] * (UPDATE_SIZE)            
            StartNominalTrack = [0xFFFF,] * (UPDATE_SIZE*2)
            NumNominalTracks  = [0xFFFF,] * (UPDATE_SIZE*2)
            NumUpdate = 0
            for zn in xrange(self.numUserZones):                  
               if zn in skipUpdateZn:
                  continue
                  
               if debug_LBR: objMsg.printMsg("set zone %d" % (zn))            
               if zn not in skipUpdateZnStartCyl:                  
                  StartNominalTrack[(NumUpdate*2)+1] = NominalZB[hd][zn]['ZN_START_CYL'] & 0xFFFF
                  StartNominalTrack[NumUpdate*2]     = (NominalZB[hd][zn]['ZN_START_CYL']>>16 ) & 0xFFFF
               else:                  
                  objMsg.printMsg("skip ZN_START_CYL update at zn %d" % (zn))
                  
               NumNominalTracks[(NumUpdate*2)+1] = NominalZB[hd][zn]['TRK_NUM'] & 0xFFFF
               NumNominalTracks[NumUpdate*2]     = (NominalZB[hd][zn]['TRK_NUM']>>16 ) & 0xFFFF
               ZoneNum[NumUpdate] = zn
               NumUpdate += 1
               if NumUpdate == UPDATE_SIZE:
                  updateZB_prm['TEST_HEAD']         = hd
                  updateZB_prm['ZONE_NUM']          = ZoneNum                  
                  updateZB_prm['START_NOMINAL_TRK'] = StartNominalTrack
                  updateZB_prm['NUM_NOMINAL_TRK']   = NumNominalTracks                  
                  getVbarGlobalClass(CProcess).St(updateZB_prm)
                  ZoneNum           = [0xFFFF,] * (UPDATE_SIZE)                  
                  StartNominalTrack = [0xFFFF,] * (UPDATE_SIZE*2)
                  NumNominalTracks  = [0xFFFF,] * (UPDATE_SIZE*2)
                  NumUpdate = 0
            if ZoneNum[0] != 0xFFFF:
               updateZB_prm['TEST_HEAD']         = hd
               updateZB_prm['ZONE_NUM']          = ZoneNum               
               updateZB_prm['START_NOMINAL_TRK'] = StartNominalTrack
               updateZB_prm['NUM_NOMINAL_TRK']   = NumNominalTracks                  
               getVbarGlobalClass(CProcess).St(updateZB_prm)
         getVbarGlobalClass(CProcess).St({'test_num': 178, 'prm_name': 'prm_178_Save_RAP_to_flash', 'timeout': 1200, 'spc_id': 0, 'CWORD1':0x0220})
      else:
         raiseException(11044,"Failed to update RAP, please turn on FE_0270714_356688_ZB_UPDATE in SF3")
               
      if debug_LBR:
         getVbarGlobalClass(CProcess).St(TP.DisplayUserZB)
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      
  #-------------------------------------------------------------------------------------------------------         
   def checkOEMWTF(self):
      #determine if a head is narrow head or not
      for hd in xrange(self.numHeads):
         BPI_Max = 0
         TPI_Max = 0
         for zn in xrange(self.numUserZones):
            bpi = self.measAllZns.getRecord('BPI', hd, zn)
            if BPI_Max < bpi:
               BPI_Max = bpi
            tpi = self.measAllZns.getRecord('TPI', hd, zn)
            if TPI_Max < tpi:
               TPI_Max = tpi

         if BPI_Max < 0.85 or TPI_Max > 1.12  or TPI_Max < 0.90:
            testSwitch.OEM_Waterfall_Enable = 1

   def testSatFail(self, AllZonesMeasurements):
      objMsg.printMsg("Remeasure for possible 13409 failures")

      for hd, zn in self.dut.satFail_HdsZns:
         wp = self.dut.wrPwrPick[hd][self.objTestZones.getTestZnforZn(zn)]

         if wp == self.NUM_WRITE_POWERS:
            return ATPI_FAIL_SATURATION

         else:
            bpiOrig = AllZonesMeasurements.getRecord('BPI', hd, zn)

            # Could use either a CVbarMeasurement or a CVbarWpMeasurement class for this purpose, which ever is
            # most convenient.  The CVbarWpMeasurement class is the smaller of the two.
            bpiLowWP = CMeasureBPIAndTPIinWpZones(CVbarWpMeasurement(initStore=True, numOfWp=self.NUM_WRITE_POWERS)).measureBPI(hd, zn, wp+1)

            if bpiOrig - bpiLowWP > TP.WCSAT_BPIMARGIN:
               return ATPI_FAIL_SATURATION

      return ATPI_PASS

   def deltaBPICScreen(self):
      """Check BPIC between WP and ZN measurements, fail if too many zones exceed spec"""
      thresholds = TP.VBARDeltaBPICThresholds
      zoneFailureLimit = TP.VBARDeltaBPICZoneFailureLimit

      objMsg.printMsg("Delta BPIC Screen")
      objMsg.printMsg("HD  ZN  BPIC_WP  BPIC_ZN    DELTA  STATUS")
      test_status = ATPI_PASS
      for hd in range(self.numHeads):
         failures = 0
         for zn in self.objTestZones.getTestZones():
            wp = self.dut.wrPwrPick[hd][zn]
            bpicwp = self.measWPZns.getNibletizedRecord(hd, zn, wp)['BPI']
            bpiczn = self.measAllZns.getNibletizedRecord(hd, zn)['BPI']

            delta = bpicwp - bpiczn

            if testSwitch.FE_0148140_426568_P_FAIL_BPIC_DELTA_GREATER_EQUAL_TO_THRESHOLD:
               if delta >= thresholds[zn]:
                  failures += 1
                  zone_status = "F"
               else:
                  zone_status = "P"
            else:
               if delta < thresholds[zn]:
                  failures += 1
                  zone_status = "F"
               else:
                  zone_status = "P"

            objMsg.printMsg("%2d  %2d  %7.4f  %7.4f  %7.4f  %6s" % (hd, zn, bpicwp, bpiczn, delta, zone_status))

         if failures >= zoneFailureLimit:
            test_status = ATPI_FAIL_HMS_CAPABILITY

      return test_status

   def measureBER(self):
      defPrm = {
            'test_num'                 : 250,
            'prm_name'                 : 'base_intraVBAR_BER_prm_250',
            'spc_id'                   : 1,
            'timeout'                  : 2500 * TP.numHeads,
            'retryECList'              : [10522],
            'retryCount'               : 3,
            'retryMode'                : POWER_CYCLE_RETRY,
            'ZONE_MASK'                : (0xFFFF,0xFFFF),
            'ZONE_MASK_EXT'                : (0xFFFF,0xFFFF),
            'TEST_HEAD'                : 0xFF,
            'WR_DATA'                  : (0x00),
            'ZONE_POSITION'            : TP.VBAR_ZONE_POS,
            'MAX_ERR_RATE'             : -70,
            "CWORD1"                   : 0x0803,
            'NUM_TRACKS_PER_ZONE'      : 10,
            'RETRIES'                  : 50,
            'SKIP_TRACK'               : 200,
            'MINIMUM'                  : 2,
            'MAX_ITERATION'            : 24,
         }


      intraVBAR_BER_prm_250 = getattr(TP, 'intraVBAR_BER_prm_250', defPrm)

      SetFailSafe()
      getVbarGlobalClass(CProcess).St(intraVBAR_BER_prm_250)
      ClearFailSafe()

   def HMS_RdGap_Zap_Opti(self,operations):
      hdznsWithBPIChange = getHdZnsWithBPIChange(self.measAllZns)
      # Create a dictionary with heads as keys and a list of test zones as their associated values.
      hms_zones = {}
      for hd, zn in hdznsWithBPIChange:
         hms_zones.setdefault(hd, []).append(zn)


      if 'GAP_CAL' in operations:
         if hms_zones: #got active zones
            from base_SerialTest import CReadWriteGapCal
            params_writer_reader_gap = {'SKIP_SYS_ZONE' : 1, 'spc_id': self.dut.vbar_iterations, 'ZONE_MASK': hms_zones}
            CReadWriteGapCal(self.dut, params_writer_reader_gap).run()
            objMsg.printMsg('hms_zone=%s' % hms_zones)

      # Zones to be optied vary by head, so make individual Opti calls for each head, with the appropriate zone mask.
      if 'ZAP' in operations:
         from Servo import CServoOpti
         oSrvOpti = CServoOpti()
         #hms_zones[0]= [1,2,3]
         #hms_zones[1]= [4,5,6]

         VbarZap = deepcopy(TP.zapbasic_175)
         VbarZap['prm_name'] = "Vbar ZAP"
         VbarZap['CWORD2'] = 0x0014
         numTestCyls = int(VbarZap.get('numTestCyls',30))

         for hd in hms_zones:
            objMsg.printMsg(  "CCCCCCCCCCCClenOfhmsZone:%d" % len(hms_zones[hd])  )
            hdMsk = (hd << 8) + hd
            VbarZap["HEAD_RANGE"] = (hdMsk)
            VbarZap['CWORD2'] = VbarZap['CWORD2'] | 0x40
            VbarZap['ZONE_POSITION'] = TP.VBAR_ZONE_POS
            zone_mask_low = 0
            zone_mask_high = 0
            for zone in hms_zones[hd]:
               if zone < 32:
                  zone_mask_low |= (1<<zone)
               else:
                  zone_mask_high |= (1<<(zone - 32))
            #VbarZap['ZONE_MASK'] = self.oUtility.ReturnTestCylWord(self.oUtility.setZoneMask(hms_zones[hd]))
            VbarZap['ZONE_MASK'] = self.oUtility.ReturnTestCylWord(zone_mask_low)
            VbarZap['ZONE_MASK'] = self.oUtility.ReturnTestCylWord(zone_mask_high)
            VbarZap['TRACK_LIMIT'] = 0x0A1E
            oSrvOpti.zap(VbarZap)

      if 'RD_OPTI' in operations:
         from base_SerialTest import SimpleOpti
         for hd in hms_zones:
            params = {'HEAD':hd, 'ZONES':hms_zones[hd], 'ZONE_POS':TP.VBAR_ZONE_POS, 'DISABLE_ZAP': False}

            if testSwitch.FE_0138035_208705_P_NO_TARGET_OPTI_IN_VBAR_HMS:
               params['param'] = 'simple_OptiPrm_251_No_Target_Opti'

            if testSwitch.FE_0150693_409401_P_KORAT_ZAP_OTF:
               SimpleOpti(self.dut, params).run(zapOtfHMS=1)
            else:
               SimpleOpti(self.dut, params).run(T250Audit=0)

   def processSCPHMS(self, allowFailure, allowAdjustments, niblet, BPIperHMS,iterations,oMeas,bpi_step,adjustment=100):
      status = ATPI_PASS

      # Calculate average HMS capability and confirm the need to adjust
      adjust = False
      avgHMSbyHead = [0.0] * self.numHeads
      for hd in xrange(self.numHeads): 
         for zn in xrange(self.numUserZones):
            hms = self.measAllZns.getRecord('HMS', hd, zn)
            avgHMSbyHead[hd] += hms
            if hms < TP.VbarHMSMaxPassLimit and allowAdjustments:
               adjust = True
      avgHMSbyHead = [avg / self.numUserZones for avg in avgHMSbyHead]
      avgHMS = mean(avgHMSbyHead)

      # Constrain the mean HMS capability to allow HMS vs TPI trade-offs
      mintargetHMS = self.getParam('MIN_TARGET_HMSCAP',  0.0)
      maxtargetHMS = self.getParam('MAX_TARGET_HMSCAP', 10.0)

      avgHMS = max(avgHMS, mintargetHMS)
      avgHMS = min(avgHMS, maxtargetHMS)

      # Set up for DBLog table
      curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
      spcId = self.spcIdHlpr.getSpcId('P_VBAR_FORMAT_SUMMARY')
      spcIdBase = (int(spcId) / 100) * 100
      localspcId = spcIdBase + (iterations+1) * 100
      occurrence += iterations
      # Reduce log output by grabbing local references
      HMSMarginTaper      = TP.HMSMarginTaper
      VbarMaxBpiAdjperHMS = TP.VbarMaxBpiAdjperHMS
      VbarMinBpiAdjperHMS = TP.VbarMinBpiAdjperHMS
      VbarHMSThreshold    = TP.VbarHMSThreshold
      VbarHMSMinZoneSpec  = niblet.settings['VbarHMSMinZoneSpec'] + 0.3
      VbarHMSMinHeadSpec  = niblet.settings['VbarHMSMinHeadSpec']
      objMsg.printMsg("VbarHMSMinZoneSpec= %f VbarHMSMinHeadSpec= %f" % (VbarHMSMinZoneSpec,VbarHMSMinHeadSpec))
      # Print the table, perform adjustments, check failure limits
      activeZones = 0

      # Now, adjust all zones
      for hd in xrange(self.numHeads):
         for zn in xrange(self.numUserZones):
            pickerData = CVbarDataHelper(self.hmsPicker, hd, zn)
            meas = CVbarDataHelper(self.measAllZns, hd, zn)

            # Calculate HMS margin
            hmsMargin = meas['HMS'] - VbarHMSMinZoneSpec

            if hmsMargin < 0.00:
               if not BPIperHMS == None:
                  bpiAdj = BPIperHMS[zn] * hmsMargin
               else:
                  bpiAdj = hmsMargin
               cumAdj = meas['BPIAdj']

               # Invoke a BPI Change by force:
               curFrequency = self.bpiFile.getFrequencyByFormatAndZone(oMeas.formatScaler.getFormat(hd, zn, 'BPI'),zn,hd)
               nominalFrequency = self.bpiFile.getFrequencyByFormatAndZone(0,zn,hd)
               curcapability = float(curFrequency)/nominalFrequency
               curbpiformat = self.hmsPicker.getClosestBPITable(curcapability,zn,hd)
               if adjustment == 100:
                  objMsg.printMsg("Hd %d Zn %d curbpiformat %d curcapability %4f calculated_adj %4f minimum_adjust %4f" % (hd,zn,curbpiformat,curcapability,bpiAdj,bpi_step))
               newbpiformat = curbpiformat
               while 1:
                  newbpiformat -= 1
                  if newbpiformat < self.bpiFile.getMinFormat():
                     break
                  newFrequency = self.bpiFile.getFrequencyByFormatAndZone(newbpiformat,zn,hd)
                  actual_adjust = (curFrequency - newFrequency) / nominalFrequency
                  if adjustment == 100:
                     objMsg.printMsg("Hd %d Zn %d newbpiformat %d actual_adjust %4f" % (hd,zn,newbpiformat,actual_adjust))
                  if actual_adjust > max(abs(bpiAdj),bpi_step):
                     #self.hmsPicker.data[hd][zn]['AdjustedBpiFormat'] = True
                     bpiAdj = -actual_adjust
                     break

               if abs(bpiAdj) < bpi_step: #0.00125:
                  bpiAdj = -bpi_step

               # Clip if necessary
               maxBpiAdjLimit = VbarMaxBpiAdjperHMS[zn]
               minBpiAdjLimit = VbarMinBpiAdjperHMS[zn]
               if bpiAdj + cumAdj < minBpiAdjLimit or bpiAdj + cumAdj > maxBpiAdjLimit:
                  if adjustment == 100:
                     objMsg.printMsg("HMS_DBG: BpiAdjLimit Exceeded!! Hd %d Zn %d Iter %d BPIC %4f HMSC %4f TOT_ADJ %4f NEXT_ADJ %4f" % (hd,zn,iterations,meas['BPI_HMS'],meas['HMS'],meas['BPIAdj'], bpiAdj))
                  bpiAdj = 0 # Do not do anymore adjustment
                  active = 0 # Record as inactive zone


               # Make the adjustment
               elif testSwitch.BF_0224594_358501_LIMIT_MIN_BPIC_SET_DURING_HMSADJ:
                  nominalFrequency = self.bpiFile.getFrequencyByFormatAndZone(0,zn,hd)
                  bpimin_allowed =  self.bpiFile.getFrequencyByFormatAndZone(self.bpiFile.getMinFormat(),zn,hd) / nominalFrequency 
                  if adjustment == 100:
                     objMsg.printMsg("HMS_DBG: Hd %d Zn %d Iter %d BPIC %4f HMSC %4f TOT_ADJ %4f NEXT_ADJ %4f" % (hd,zn,iterations,meas['BPI_HMS'],meas['HMS'],meas['BPIAdj'], bpiAdj))

                  if (meas['BPI_HMS']+ bpiAdj) > bpimin_allowed:
                     # Make the adjustment
                     meas['BPI_HMS'] += bpiAdj
                     meas['BPIAdj'] += bpiAdj
                     ## modify the capability of hmspicker object
                     #objMsg.printMsg('BpiCapability=%f' % self.hmsPicker.data[hd][zn]['BpiCapability'])
                     pickerData['BpiCapability'] += bpiAdj
                     #newbpiformat = self.hmsPicker.getClosestBPITable(self.hmsPicker.data[hd][zn]['BpiCapability'], zn )
                     # If the zone has been changed, set flag to update the format
                     if newbpiformat != oMeas.formatScaler.getFormat(hd, zn, 'BPI'):
                        pickerData['BpiFormat'] = newbpiformat
                        pickerData['AdjustedBpiFormat'] = 'T'
                     else:
                        objMsg.printMsg('Waste one iterations oldformat=%d, newbpiformat=%d' % (oMeas.formatScaler.getFormat(hd, zn, 'BPI'),newbpiformat) )
                        pickerData['AdjustedBpiFormat'] = 'F'

                     # Mark zone as active
                     activeZones += 1
                     active = 1
                  else:
                     bpiAdj = 0.0
                     active = 0
               else:
                  # Make the adjustment
                  meas['BPI_HMS'] += bpiAdj
                  meas['BPIAdj'] += bpiAdj

                  # Mark zone as active
                  activeZones += 1
                  active = 1
            else:
               bpiAdj = 0.0
               active = 0

            # Check measurements against spec
            specs = ""
            if meas['HMS'] < VbarHMSMinZoneSpec:
               specs += "Z"
               status = ATPI_FAIL_HMS_CAPABILITY
            #if avgHMSbyHead[hd] < VbarHMSMinHeadSpec:
            #   specs += "H"
            #   status = ATPI_FAIL_HMS_CAPABILITY

            # Record DBLog data
            meas = self.measAllZns.getNibletizedRecord(hd, zn)
            if adjustment == 100:
               CUM_BPI_ADJ = round(meas['BPIAdj'], 4)
               BPI_PICK = round(meas['BPIPick'], 4)
            else:
               bpi_pct = 1.0 + float(adjustment) / 100
               bpi_pct_s = oMeas.formatScaler.scaleBPI(hd, zn, bpi_pct)
               CUM_BPI_ADJ = round(meas['BPI'] - bpi_pct_s, 4)
               BPI_PICK = round(bpi_pct_s, 4)
            dblog_record = {
                  'SPC_ID'          : localspcId,
                  'OCCURRENCE'      : occurrence,
                  'SEQ'             : curSeq,
                  'TEST_SEQ_EVENT'  : testSeqEvent,
                  'HD_PHYS_PSN'     : self.dut.LgcToPhysHdMap[hd],
                  'HD_LGC_PSN'      : hd,
                  'DATA_ZONE'       : zn,
                  'ITERATION'       : iterations+1,
                  'HMS_CAP'         : round(meas['HMS'], 4),
                  'HMS_MRGN'        : round(hmsMargin, 4),
                  'BPI_ADJ'         : round(bpiAdj, 4),
                  'CUM_BPI_ADJ'     : CUM_BPI_ADJ,
                  'BPI_CAP'         : round(meas['BPI_HMS'], 4),
                  'BPI_PICK'        : BPI_PICK,
                  'TPI_PICK'        : round(meas['TPIPick'], 4),
                  'ACTIVE_ZONE'     : active,
                  'OUT_OF_SPEC'     : specs,
                  'TPI_CAP'         : round(meas['TPI'], 4),
                  'TGT_WRT_CLR'     : meas['TWC'],
               }


            if testSwitch.extern.FE_0155984_208705_VBAR_HMS_BER_PENALTY:
               dblog_record.update({
                  'CAP_PENALTY'     : round(meas['HMSP'], 4),
               })

            # Grab the highest 3 digits from the spc_id and add them to iteration
            # This aids log-based FA, since SPC_ID is missing in text logs
            #iteration = spcIdBase + self.dut.vbar_iterations
            #dblog_record.update({
            #      'SPC_ID'       : spcId,
            #   })
            self.dut.dblData.Tables('P_VBAR_HMS_ADJUST').addRecord(dblog_record)

            if testSwitch.FE_0164322_410674_RETRIEVE_P_VBAR_TABLE_AFTER_POWER_RECOVERY:
               self.dut.vbar_hms_adjust.append(dblog_record)

      #objMsg.printDblogBin(self.dut.dblData.Tables('P_VBAR_HMS_ADJUST'), localspcId)

      # If all zones converged, stop iterating, check for failures and skip the picker
      if activeZones == 0 and adjust:
         self.dut.vbar_iterations = self.getParam('ITERATIONS', 0)
         allowFailure = True
         status = ATPI_PASS

      if allowFailure:
         objMsg.printMsg("ProcessSCPHMS status=%s" % status)
         return status
      else:
         objMsg.printMsg("ProcessSCPHMS passed")
         return ATPI_PASS

   def processHMS(self, allowFailure, allowAdjustments, niblet, BPIperHMS):
      status = ATPI_PASS

      # Calculate average HMS capability and confirm the need to adjust
      adjust = False
      avgHMSbyHead = [0.0] * self.numHeads
      for hd in xrange(self.numHeads): 
         for zn in xrange(self.numUserZones):
            hms = self.measAllZns.getRecord('HMS', hd, zn)
            avgHMSbyHead[hd] += hms
            if hms < TP.VbarHMSMaxPassLimit and allowAdjustments:
               adjust = True
      avgHMSbyHead = [avg / self.numUserZones for avg in avgHMSbyHead]
      avgHMS = mean(avgHMSbyHead)

      # Constrain the mean HMS capability to allow HMS vs TPI trade-offs
      mintargetHMS = self.getParam('MIN_TARGET_HMSCAP',  0.0)
      maxtargetHMS = self.getParam('MAX_TARGET_HMSCAP', 10.0)

      avgHMS = max(avgHMS, mintargetHMS)
      avgHMS = min(avgHMS, maxtargetHMS)

      # Set up for DBLog table
      curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
      spcId = self.spcIdHlpr.getSpcId('P_VBAR_FORMAT_SUMMARY')

      # Reduce log output by grabbing local references
      HMSMarginTaper      = TP.HMSMarginTaper
      VbarMaxBpiAdjperHMS = TP.VbarMaxBpiAdjperHMS
      VbarMinBpiAdjperHMS = TP.VbarMinBpiAdjperHMS
      VbarHMSThreshold    = TP.VbarHMSThreshold
      VbarHMSMinZoneSpec  = niblet.settings['VbarHMSMinZoneSpec']
      VbarHMSMinHeadSpec  = niblet.settings['VbarHMSMinHeadSpec']
      objMsg.printMsg("VbarHMSMinZoneSpec= %f VbarHMSMinHeadSpec= %f" % (VbarHMSMinZoneSpec,VbarHMSMinHeadSpec))
      # Print the table, perform adjustments, check failure limits
      activeZones = 0
      if testSwitch.FE_0162444_208705_ASYMMETRIC_VBAR_HMS:
         # Calculate the total low zones' adjustments
         totalLowAdjustment = 0.0
         lowZoneCount = 0
         highZoneCount = 0
         for hd in xrange(self.numHeads): 
            for zn in xrange(self.numUserZones):
               meas = CVbarDataHelper(self.measAllZns, hd, zn)

               # Calculate HMS margin
               if meas['HMS'] < avgHMS + HMSMarginTaper[zn]:
                  hmsMargin = meas['HMS'] - avgHMS - HMSMarginTaper[zn]
                  lowZoneCount += 1
               else:
                  hmsMargin = 0.0
                  highZoneCount += 1

               # Adjust BPI if it's allowed and the measurement is above the threshold
               if adjust and hmsMargin > 0.00 or hmsMargin < -VbarHMSThreshold:
                  bpiAdj = BPIperHMS[zn] * hmsMargin
                  cumAdj = meas['BPIAdj']

                  # Clip if necessary
                  maxBpiAdjLimit = VbarMaxBpiAdjperHMS[zn]
                  minBpiAdjLimit = VbarMinBpiAdjperHMS[zn]

                  # Clip if necessary
                  if bpiAdj + cumAdj < minBpiAdjLimit:
                     bpiAdj = minBpiAdjLimit - cumAdj
                  elif bpiAdj + cumAdj > maxBpiAdjLimit:
                     bpiAdj = maxBpiAdjLimit - cumAdj

                  # Accumulate the low adjustment
                  totalLowAdjustment += bpiAdj

      # Now, adjust all zones
      for hd in xrange(self.numHeads):
         for zn in xrange(self.numUserZones):
            meas = CVbarDataHelper(self.measAllZns, hd, zn)

            # Calculate HMS margin
            if testSwitch.FE_0162444_208705_ASYMMETRIC_VBAR_HMS and ( meas['HMS'] > avgHMS + HMSMarginTaper[zn] ):
               hmsMargin = ( -totalLowAdjustment / highZoneCount ) / BPIperHMS[zn]
            else:
               hmsMargin = meas['HMS'] - avgHMS - HMSMarginTaper[zn]

            # Adjust BPI if it's allowed and the measurement is above the threshold
            if ( (     testSwitch.FE_0162444_208705_ASYMMETRIC_VBAR_HMS and ( adjust and hmsMargin > 0.00 or hmsMargin < -VbarHMSThreshold ) ) or
                 ( not testSwitch.FE_0162444_208705_ASYMMETRIC_VBAR_HMS and ( adjust and abs(hmsMargin) > VbarHMSThreshold ) ) ):
               bpiAdj = BPIperHMS[zn] * hmsMargin
               cumAdj = meas['BPIAdj']

               # Clip if necessary
               maxBpiAdjLimit = VbarMaxBpiAdjperHMS[zn]
               minBpiAdjLimit = VbarMinBpiAdjperHMS[zn]
               if bpiAdj + cumAdj < minBpiAdjLimit:
                  bpiAdj = minBpiAdjLimit - cumAdj
               elif bpiAdj + cumAdj > maxBpiAdjLimit:
                  bpiAdj = maxBpiAdjLimit - cumAdj

               # Make the adjustment
               if testSwitch.BF_0224594_358501_LIMIT_MIN_BPIC_SET_DURING_HMSADJ:
                  nominalFrequency = self.bpiFile.getFrequencyByFormatAndZone(0,zn,hd)
                  bpimin_allowed =  self.bpiFile.getFrequencyByFormatAndZone(self.bpiFile.getMinFormat(),zn,hd) / nominalFrequency
                  objMsg.printMsg("Zn %d Min Allowed BPI=%f" % (zn,bpimin_allowed))

                  if (meas['BPI']+ bpiAdj) > bpimin_allowed:
                     # Make the adjustment
                     meas['BPI'] += bpiAdj
                     meas['BPIAdj'] += bpiAdj

                     # Mark zone as active
                     activeZones += 1
                     active = 1
                  else:
                     bpiAdj = 0.0
                     active = 0
               else:
                  # Make the adjustment
                  meas['BPI'] += bpiAdj
                  meas['BPIAdj'] += bpiAdj

                  # Mark zone as active
                  activeZones += 1
                  active = 1
            else:
               bpiAdj = 0.0
               active = 0

            # Check measurements against spec
            specs = ""
            if meas['HMS'] < VbarHMSMinZoneSpec:
               specs += "Z"
               status = ATPI_FAIL_HMS_CAPABILITY
            if avgHMSbyHead[hd] < VbarHMSMinHeadSpec:
               specs += "H"
               status = ATPI_FAIL_HMS_CAPABILITY

            # Record DBLog data
            meas = self.measAllZns.getNibletizedRecord(hd, zn)

            dblog_record = {
                  'SPC_ID'          : spcId,
                  'OCCURRENCE'      : occurrence,
                  'SEQ'             : curSeq,
                  'TEST_SEQ_EVENT'  : testSeqEvent,
                  'HD_PHYS_PSN'     : self.dut.LgcToPhysHdMap[hd],
                  'HD_LGC_PSN'      : hd,
                  'DATA_ZONE'       : zn,
                  'ITERATION'       : self.dut.vbar_iterations+1,
                  'HMS_CAP'         : round(meas['HMS'], 4),
                  'HMS_MRGN'        : round(hmsMargin, 4),
                  'BPI_ADJ'         : round(bpiAdj, 4),
                  'CUM_BPI_ADJ'     : round(meas['BPIAdj'], 4),
                  'BPI_CAP'         : round(meas['BPI'], 4),
                  'BPI_PICK'        : round(meas['BPIPick'], 4),
                  'TPI_PICK'        : round(meas['TPIPick'], 4),
                  'ACTIVE_ZONE'     : active,
                  'OUT_OF_SPEC'     : specs,
                  'TPI_CAP'         : round(meas['TPI'], 4),
                  'TGT_WRT_CLR'     : meas['TWC'],
               }


            if testSwitch.extern.FE_0155984_208705_VBAR_HMS_BER_PENALTY:
               dblog_record.update({
                  'CAP_PENALTY'     : round(meas['HMSP'], 4),
               })

            # Grab the highest 3 digits from the spc_id and add them to iteration
            # This aids log-based FA, since SPC_ID is missing in text logs
            spcIdBase = (int(spcId) / 100) * 100
            iteration = spcIdBase + self.dut.vbar_iterations
            dblog_record.update({
                  'ITERATION'       : iteration,
               })
            if (not testSwitch.SCP_HMS) or (testSwitch.SCP_HMS and iteration >= 100):
               self.dut.dblData.Tables('P_VBAR_HMS_ADJUST').addRecord(dblog_record)

               if testSwitch.FE_0164322_410674_RETRIEVE_P_VBAR_TABLE_AFTER_POWER_RECOVERY:
                  self.dut.vbar_hms_adjust.append(dblog_record)

      # Display the latest table
      if not testSwitch.CM_REDUCTION_REDUCE_PRINTDBLOGBIN:
         objMsg.printDblogBin(self.dut.dblData.Tables('P_VBAR_HMS_ADJUST'), spcId)

      # If all zones converged, stop iterating, check for failures and skip the picker
      if activeZones == 0 and adjust:
         self.dut.vbar_iterations = self.getParam('ITERATIONS', 0)
         allowFailure = True
         self.params['FMT_PICKER'] = False

      if testSwitch.VBAR_HMS_MEAS_ONLY and self.dut.nextState in ['HMSC_DATA']:
         return ATPI_PASS
      else:
         if allowFailure:
            objMsg.printMsg("ProcessHMS status=%s" % status)
            return status
         else:
            objMsg.printMsg("ProcessHMS passed")
            return ATPI_PASS

   #-------------------------------------------------------------------------------------------------------
   def fastprocessSCPHMS(self, dataList2, VbarHMSMinZoneSpec):
      if verbose:
         objMsg.printMsg('SlopeData')
         objMsg.printMsg('Hd    Zn   BPIC      HMSC')
         for hd in range(self.numHeads):
            for zn in range(self.numUserZones):
               for idx in range(len(dataList2[hd, zn, 'BPI'])):
                  objMsg.printMsg('%d    %2d   %3.4f        %3.4f' % (hd, zn,dataList2[hd, zn, 'BPI'][idx], dataList2[hd, zn, 'HMS'][idx]))

      curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
      for hd in xrange(self.numHeads):
         # Normalize BPIC before getting Linear Regression by Head
         minBpic = 2
         for zn in range(self.numUserZones):
            minBpic =min(minBpic, min(dataList2[hd,zn,'BPI']))

         for zn in range(self.numUserZones):
            for idx in range(len(dataList2[hd, zn, 'BPI'])):
               dataList2[hd, 'BPI'].append(dataList2[hd,zn,'BPI'][idx] - minBpic)
            dataList2[hd, 'HMS'].extend(dataList2[hd, zn, 'HMS'])
         if not testSwitch.virtualRun:
            HMSSlopeHd, HMSConstHd, HMSRSqHd = linreg(dataList2[hd,'HMS'],dataList2[hd,'BPI'])
         else:
            HMSSlopeHd, HMSConstHd, HMSRSqHd = 0.5, 1,1
         HMSConstHd += minBpic
         if verbose:
            objMsg.printMsg('===================================')
            objMsg.printMsg('Hd    HMSSlope          Constant       Rsq       minBPIC')
            objMsg.printMsg('%d    %4.8f        %4.8f     %3.4f     %3.4f' % (hd, HMSSlopeHd, HMSConstHd, HMSRSqHd, minBpic))
            objMsg.printMsg('==========================================')
            objMsg.printMsg('Hd    Zn     HMSSlope          Constant       Rsq        BPICHMS')
         for zn in xrange(self.numUserZones):
            meas = CVbarDataHelper(self.measAllZns, hd, zn)
            if not testSwitch.virtualRun:
               HMSSlope, HMSConst, HMSRSq = linreg(dataList2[hd,zn,'HMS'],dataList2[hd,zn,'BPI'])
            else:
               HMSSlope, HMSConst, HMSRSq = 0.5, 1,1
            slope = HMSSlope
            intercept = HMSConst

            # cater for poor RSq
            if HMSRSqHd > HMSRSq:
               slope = HMSSlopeHd
               if not HMSSlope < 0: # also copy intercept if slope is zero or positive
                  intercept = HMSConstHd

            if not slope < 0: # if the final slope is zero or positive, lets reset to a default
               meas['HMS'] = -1
               if len(dataList2[hd, zn, 'HMS']) > 0 and sum(dataList2[hd, zn, 'HMS']) / len(dataList2[hd, zn, 'HMS']) > VbarHMSMinZoneSpec:
                  bpi_target_hms = meas['BPI'] # Set adjustment to zero if overall HMS > VbarHMSMinZoneSpec
               else:
                  bpi_target_hms = meas['BPI'] - TP.SCP_MAX_HMSC_BPIADJ # Otherwise, set adjustment to max
            else:
               bpi_target_hms = slope * VbarHMSMinZoneSpec + intercept
               meas['HMS'] = (meas['BPI'] - intercept) / slope # HMSC at BPIC
            if meas['HMS'] < VbarHMSMinZoneSpec:
               active = 1
               specs = "Z"
            else:
               active = 0
               specs = ""
            meas['BPIMH'] = max(meas['BPI'] -  bpi_target_hms, 0)   #Limit to positive
            meas['BPIMH'] = min(meas['BPIMH'], TP.SCP_MAX_HMSC_BPIADJ) #Limit to 0.15 max
            if verbose:
               objMsg.printMsg('%d    %2d     %4.8f        %4.8f     %3.4f     %3.4f' % (hd, zn, HMSSlope,HMSConst, HMSRSq, bpi_target_hms))
            if 0:
               dblog_record = {
                  'SPC_ID'          : 200,
                  'OCCURRENCE'      : occurrence,
                  'SEQ'             : curSeq,
                  'TEST_SEQ_EVENT'  : testSeqEvent,
                  'HD_PHYS_PSN'     : self.dut.LgcToPhysHdMap[hd],
                  'HD_LGC_PSN'      : hd,
                  'DATA_ZONE'       : zn,
                  'ITERATION'       : 299,
                  'HMS_CAP'         : round(meas['HMS'], 4),
                  'HMS_MRGN'        : round(meas['HMS'] - VbarHMSMinZoneSpec, 4),
                  'BPI_ADJ'         : round(meas['BPI'] -  bpi_target_hms, 4),
                  'CUM_BPI_ADJ'     : round(meas['BPIMH'], 4),
                  'BPI_CAP'         : round(meas['BPI'], 4),
                  'BPI_PICK'        : round(meas['BPI'] - meas['BPIMH'], 4),
                  'TPI_PICK'        : round(meas['TPIPick'], 4),
                  'ACTIVE_ZONE'     : active,
                  'OUT_OF_SPEC'     : specs,
                  'TPI_CAP'         : round(meas['TPI'], 4),
                  'TGT_WRT_CLR'     : meas['TWC'],
                  'CAP_PENALTY'     : 0.0,
               }
               self.dut.dblData.Tables('P_VBAR_HMS_ADJUST').addRecord(dblog_record)
            dblog_record = {
               'SPC_ID'          : 200,
               'OCCURRENCE'      : occurrence,
               'SEQ'             : curSeq,
               'TEST_SEQ_EVENT'  : testSeqEvent,
               'HD_PHYS_PSN'     : self.dut.LgcToPhysHdMap[hd],
               'DATA_ZONE'       : zn,
               'HD_LGC_PSN'      : hd,
               'HMS_SLOPE'       : round(HMSSlope, 5),
               'HMS_INTCPT'      : round(HMSConst, 5),
               'HMS_RSQ'         : round(HMSRSq, 4),
               'BPIM_RHMS'       : round(meas['BPIMH'], 4),
               'HMS_CAP'         : round(meas['HMS'], 4),
            }
            self.dut.dblData.Tables('P_VBAR_HMS_SLOPE_SUMMARY').addRecord(dblog_record)
      objMsg.printDblogBin(self.dut.dblData.Tables('P_VBAR_HMS_SLOPE_SUMMARY'))

   #-------------------------------------------------------------------------------------------------------
   # Class method
   def getCapacityFromDrive(self):
      getVbarGlobalClass(CProcess).St({'test_num':210,'CWORD1':8, 'SCALED_VAL': int(0.9985 * 10000)})
      colDict = self.dut.dblData.Tables('P210_CAPACITY_DRIVE').columnNameDict()
      row = self.dut.dblData.Tables('P210_CAPACITY_DRIVE').rowListIter(index=len(self.dut.dblData.Tables('P210_CAPACITY_DRIVE'))-1).next()
      return row[colDict['DRV_CAPACITY']]

   def getCapacity(self):
      """Return actual capacity of drive in GB"""
      prm_210 = {
         'test_num'     : 210,
         'prm_name'     : 'Check Capacity',
         'timeout'      : 1800,
         'spc_id'       : 0,
         'CWORD1'       : (0x0008,),
         'SECTOR_SIZE'  : (512,),
      }

      getVbarGlobalClass(CProcess).St(prm_210)
      if testSwitch.virtualRun:
         if testSwitch.FE_0125707_340210_CAP_FROM_BPIFILE:
            capGB = self.bpiFile.getNominalCapacity()*self.numHeads
         else:
            capGB = TP.VbarCapacityGBPerHead*self.numHeads
      else:
         capGB = DriveVars["Drivecapacity"]

      return capGB

   #-------------------------------------------------------------------------------------------------------
   # General function to generate the IDEMA max LBA for a given capacity
   if not testSwitch.FE_0139240_208705_P_IMPROVED_MAX_LBA_CALC :
      def IDEMAMaxLBA(self, capacity, sector_size):
         num_lbas = int((97696368 + 1953504 * (capacity - 50.0)) / (sector_size / 512.0) + 1) # always round up
         return num_lbas - 1 # return the max LBA

      def IDEMAMaxLBA_4K(self, capacity):
         return int(round((((97696368 + (1953504 * (capacity - 50.0)))+7)/8)+1))

      def IDEMAMaxLBA_512(self, capacity):
         return int(round(97696368 + (1953504 * (capacity - 50.0))))

   def sendMaxLBACmdBySectorSize(self, lbas, sector_size):
      # This call will silently fail if invoked without the proper flag set true

      prm = {
               'test_num'    : 178,
               'prm_name'    : 'Set Max LBA',
               'timeout'     : 1800,
               'CWORD1'      : 0x260,
               'SECTOR_SIZE' : sector_size,
               'NUM_LBAS'    : self.oUtility.ReturnTestCylWord(lbas & 0xFFFFFFFF),
            }

      if testSwitch.extern.LBA_WIDER_THAN_32_BITS:
         prm['NUM_LBAS_HI'] = self.oUtility.ReturnTestCylWord((lbas>>32) & 0x0000FFFF)

      getVbarGlobalClass(CProcess).St(prm)

   def sendMaxLBACmd(self, lbas, offset):
      prm = {
               'test_num' : 178,
               'prm_name' : 'Set Max LBA',
               'timeout'  : 1800,
               'CWORD1'   : 0x260,
               'OFFSET'   : offset,
               'NUM_LBAS' : self.oUtility.ReturnTestCylWord(lbas & 0xFFFFFFFF),
            }

      if testSwitch.extern.LBA_WIDER_THAN_32_BITS:
         prm['NUM_LBAS_HI'] = self.oUtility.ReturnTestCylWord((lbas>>32) & 0x0000FFFF)

      getVbarGlobalClass(CProcess).St(prm)

   # Class method
   def setMaxLBAForAudit(self):
      # TODO: test
      if not testSwitch.virtualRun:
         numPBAs = self.dut.numPBAs
      else:
         colDict = self.dut.dblData.Tables('P000_DRIVE_PBA_COUNT').columnNameDict()
         row = self.dut.dblData.Tables('P000_DRIVE_PBA_COUNT').rowListIter(index=len(self.dut.dblData.Tables('P000_DRIVE_PBA_COUNT'))-1).next()
         numPBAs = float(row[colDict['DRIVE_NUM_PBAS']])

      max_lba_val = int(0.998*numPBAs)# allow for spares
      self.sendMaxLBACmd(max_lba_val, 0)

   def setMaxLBA(self, niblet=None):
      if niblet:
         media_cache_capacity = niblet.settings['MEDIA_CACHE_CAPACITY']
         capacity    = niblet.settings['DRIVE_CAPACITY']
         if testSwitch.FE_0125707_340210_CAP_FROM_BPIFILE:
            capacity_4K = niblet.settings['NumHeads'] * niblet.settings['CapacityTarget4K'] * self.bpiFile.getNominalCapacity()
         else:
            capacity_4K = niblet.settings['NumHeads'] * niblet.settings['CapacityTarget4K'] * TP.VbarCapacityGBPerHead
         capacity -= media_cache_capacity
         capacity_4K -= media_cache_capacity
      else:
         if testSwitch.FE_0125707_340210_CAP_FROM_BPIFILE:
            capacity    = self.numHeads * self.bpiFile.getNominalCapacity()
            capacity_4K = self.numHeads * self.bpiFile.getNominalCapacity()
         else:
            capacity    = self.numHeads * TP.VbarCapacityGBPerHead
            capacity_4K = self.numHeads * TP.VbarCapacityGBPerHead

      if testSwitch.FE_0139240_208705_P_IMPROVED_MAX_LBA_CALC :
         import lbacalc
         # Use the INTERFACE attribute to determine SAS vs SATA
         if self.dut.drvIntf in TP.WWN_INF_TYPE.get('WW_SAS_ID', []) or self.dut.drvIntf == 'SAS':
            # SAS
            sectorsizes = [(512, capacity), (520, capacity), (524, capacity), (528, capacity), (4096, capacity_4K)]
            lbafunc = lbacalc.sasCapToLba
         else:
            # SATA
            sectorsizes = [(512, capacity), (4096, capacity_4K)]
            lbafunc = lbacalc.sataCapToLba

         # Send the max LBA values to the drive
         for sectorsize, cap in sectorsizes:
            if testSwitch.BF_0144913_208705_P_SET_CAPACITY_NOT_MAX_LBA:
               # F3 actually expects capacity, rather than max LBA, else format issues  can be encountered
               max_lba_val = lbafunc(cap, sectorsize)
            else:
               max_lba_val = lbafunc(cap, sectorsize) - 1
            self.sendMaxLBACmdBySectorSize(max_lba_val, sectorsize)
      else:
         # Set for 512 sectors
         max_lba_val = self.IDEMAMaxLBA_512(capacity)
         self.sendMaxLBACmdBySectorSize(max_lba_val, 512)

         # Set for 4K sectors
         if testSwitch.SGP_4K_MAX_LBA_CALCULATION:
            max_lba_val = int(max_lba_val/8)
         else:
            max_lba_val = self.IDEMAMaxLBA_4K(capacity_4K)

         try:
            self.sendMaxLBACmdBySectorSize(max_lba_val, 4096)
         except ScriptTestFailure:
            objMsg.printMsg("WARNING: second update to SetMAXLBA fails - Possibly 512 sector size. Moving on...")

         if testSwitch.FE_0131645_208705_MAX_LBA_FOR_SAS :
            # This section is attempting to add 520, 524, and 528 byte sector entries into the RAP for SAS drives
            # Given the urgency of the change, I've elected to just make an incremental change to get drives
            # through the process.  Long term, how we manage capacity both in the niblet and in the max LBA fields
            # in the RAP needs to be improved, so there's less hard-coding and implicit assumptions in this section
            # of the code.
            for sector_size in (520, 524, 528):
               max_lba_val = self.IDEMAMaxLBA(capacity, sector_size)
               self.sendMaxLBACmdBySectorSize(max_lba_val, sector_size)


   #-------------------------------------------------------------------------------------------------------
   def setMaxBPIWithClearance(self):
      for hd in range(self.numHeads):
         maxBPI[hd] = BPI_MAX

   #-------------------------------------------------------------------------------------------------------
   def selectHeads(self, measurements, hds):
      """
         Configure the head mask based on VBAR capabilities,
         read clearance, and depop capabilities.
         Based on Bruce Emo's algorithm.
      """
      headsToRemove = self.numHeads - hds

      if headsToRemove == 0 or testSwitch.virtualRun:
         status = ATPI_PASS
         return status

      if headsToRemove < 0:
         return ATPI_FAIL_HEAD_COUNT

      # Avoid niblets whose head count is different from the forced head count, if applicable
      forceHdCount = ConfigVars[CN].get('numHeads',0)

      if forceHdCount and hds != forceHdCount:
         return ATPI_FAIL_HEAD_COUNT

      objMsg.printMsg('Depop %d total' % headsToRemove)

      # Initialize the head rankings with heads that have enough read clearance
      # and display info about the heads for depop decision
      rank = {}
      rankSize = 0

      # Calculate the head's capability density at highest write power
      tzones = self.objTestZones.getTestZones()
      avgDensity = []
      for hd in range(self.numHeads):
         density = []
         for zn in tzones:
            meas = measurements.getNibletizedRecord(hd, zn, 0)
            density.append(meas['BPI'] * meas['TPI'])
         avgDensity.append(mean(density))

      # Find the largest target read clearance across the stroke
      maxTgtRdClr = 0
      if testSwitch.FE_0169232_341036_ENABLE_AFH_TGT_CLR_CANON_PARAMS == 1:
         from AFH_canonParams import getTargetClearance
         afhZoneTargets = getTargetClearance()
      else:
         afhZoneTargets = TP.afhZoneTargets

      for zn in range(self.numUserZones+1):
         if afhZoneTargets['TGT_RD_CLR'][zn] > maxTgtRdClr:
            maxTgtRdClr = afhZoneTargets['TGT_RD_CLR'][zn]

      # Screen heads from consideration that are flying below target read clearance
      objMsg.printMsg('Minimum clearance to depop: %.6f' % maxTgtRdClr)
      objMsg.printMsg('Hd Clearance Density')
      for hd in range(self.numHeads):
         minRdClearance = self.getMinRdClearance(hd)

         if (minRdClearance > maxTgtRdClr) and not (testSwitch.WA_0175502_357260_P_VBAR_DEPOP_DO_NOT_ALLOW_HEAD_ZERO and hd == 0):
            rank[rankSize] = hd
            rankSize = rankSize + 1

         objMsg.printMsg('%2d %9.6f %7.4f' % (hd, minRdClearance, avgDensity[hd]))

      # Sort the ranking in desending order based on capabilities
      for i in range(rankSize):
         for idx in range(rankSize-1):
            # Test capabilities
            if (avgDensity[rank[idx]]) < (avgDensity[rank[idx+1]]):
               (rank[idx+1], rank[idx]) = (rank[idx], rank[idx+1]) # swap positions

      curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
      # Mask off the lowest capable heads
      while (headsToRemove > 0 and rankSize > 0):
         rankSize -= 1
         hd = rank[rankSize]      # Pop a head off the rank array
         headsToRemove -= 1

         self.dut.dblData.Tables('P000_DEPOP_HEADS').addRecord({
               'SPC_ID':1,
               'OCCURRENCE': occurrence,
               'SEQ': curSeq,
               'TEST_SEQ_EVENT': testSeqEvent,
               'HD_PHYS_PSN': self.dut.LgcToPhysHdMap[hd],
               })

         objMsg.printMsg('Depop hd %d' % hd)

      # Log the depop table
      objMsg.printDblogBin(self.dut.dblData.Tables('P000_DEPOP_HEADS'))

      # Check to see if the depop request was satisfied
      if headsToRemove == 0:
         # We were able to handle the request
         status = ATPI_DEPOP_RESTART
      else:
         # Otherwise, fail
         status = ATPI_FAIL_HEAD_COUNT

      return status

   #-----------------------------------------------------------------------------
   def getMinRdClearance(self, hd):
      """
         Return the minimum read clearance for the given head.
         Read clearance in uin
      """
      # TODO: test
      # P035_PHYS_CLR is now obsolete, so we're now using P172_AFH_CLEARANCE instead
      # Note that it lists clearances in angstroms rather than microinches
      from AFH_constants import angstromsScaler
      if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT == 1:
         P172_AFH_CLEARANCE_tableName = 'P172_AFH_DH_CLEARANCE'
         P172_AFH_CLEARANCE_columnName = 'READ_HEAT_CLRNC'
      else:
         P172_AFH_CLEARANCE_tableName = 'P172_AFH_CLEARANCE'
         P172_AFH_CLEARANCE_columnName = 'HEAT_CLRNC'

      # Find the smallest read clearance for the given head
      colDict = self.dut.dblData.Tables(P172_AFH_CLEARANCE_tableName).columnNameDict()
      logdata = self.dut.dblData.Tables(P172_AFH_CLEARANCE_tableName).rowListIter({colDict['HD_LGC_PSN']:str(hd)})
      minClearance = float('inf')
      for row in logdata:
         if row[colDict[P172_AFH_CLEARANCE_columnName]] and (minClearance > float(row[colDict[P172_AFH_CLEARANCE_columnName]])):
            minClearance = float(row[colDict[P172_AFH_CLEARANCE_columnName]])

      # Convert to microinches if necessary
      return minClearance / angstromsScaler

   #-------------------------------------------------------------------------------------------------------
   def lookupFailureInfo(self, status):
      """ Return the description and EC for the given status. """
      defMsg = ('UNKNOWN STATUS (%s)' % status, 14644)
      msgMap = {
         ATPI_PASS                : ('PASS', 0),
         ATPI_FAIL_CAPABILITY     : ('FAILED_CAPABILITY', 13404),
         ATPI_FAIL_PERFORMANCE    : ('FAIL_PERFORMANCE', 13405),
         ATPI_FAIL_CAPACITY       : ('FAIL_CAPACITY', 13406),
         ATPI_FAIL_HEAD_COUNT     : ('FAIL_HEAD_COUNT', 13408),
         ATPI_FAIL_SATURATION     : ('FAIL_SATURATION', 13409),
         ATPI_DEPOP_RESTART       : ('DEPOP_RESTART', 12169),
         ATPI_FAIL_NO_NIBLET      : ('FAIL_NO_NIBLET', 14644),
         ATPI_FAIL_HMS_CAPABILITY : ('FAIL_HMS_CAPABILITY', 11179),
         ATPI_FAIL_MINIMUM_THRUPUT: ('FAIL_MINIMUM_THRUPUT', 13427),
         ATPI_FAIL_IMBALANCED_HEAD: ('FAIL_IMBALANCED_HEAD', 13428),
         }

      return msgMap.get(status, defMsg)

   # Class method
   def resetWritePowers(self):
      self.objRapTcc.updateWP(hd=0, zn=0, wp = 2, working_set = 0, setAllZonesHeads = 1) #Updates all zones and heads for defaults based on pre-amp type
      self.objRapTcc.printWpTable()
      self.objRapTcc.commitRAP()
      self.objRapTcc.updateDblogWpTable()

   def setFormats(self, bpifmts=[], metric = ['BPI','TPI','SET_MAX_LBA']):

      if 'BPI' in metric:
         printDbgMsg("*** Set BPI on all heads/zones ***")

         bpitables = [self.bpiFile.getNominalFormat() for head in range(T210_PARM_NUM_HEADS)]
         for head, offset in enumerate(bpifmts):
            bpitables[head] += offset

         prm = {
                  'test_num'          : 210,
                  'CWORD1'            : SET_BPI,
                  'BPI_GROUP_EXT'     : tuple(bpitables),
                  'HEAD_RANGE'        : 0x00FF,
                  'ZONE'              : 0x00FF,
         }

         if not testSwitch.FE_0269922_348085_P_SIGMUND_IN_FACTORY:
            prm.update({
                  'dlfile'   : (CN,self.bpiFile.bpiFileName),
                  })
         if testSwitch.FE_0147058_208705_SHORTEN_VBAR_LOGS:
            prm.update({
                  'stSuppressResults' : ST_SUPPRESS__ALL,
            })

         if testSwitch.WA_0152247_231166_P_POWER_CYCLE_RETRY_SIM_ERRORS:
            prm.update({
                  'retryECList'       : [10335],
                  'retryCount'        : 3,
                  'retryMode'         : POWER_CYCLE_RETRY,
            })

            if testSwitch.TRUNK_BRINGUP: #trunk code see 10451 also
                prm.update({
                   'retryECList'       : [10335,10451,10403,10468],
                   })

         prm['prm_name'] = t210PrmName(prm)

         getVbarGlobalClass(CProcess).St(prm)
         getVbarGlobalVar()['formatReload'] = True

      if 'TPI' in metric:
         printDbgMsg("*** Set TPI on all heads/zones ***")

         #### YWL: if drive SN exist in the table, do not reset TPI here!!!
         if testSwitch.FE_0165107_163023_P_FIX_TPII_WITH_PRESET_IN_VBAR:
            if HDASerialNumber in TP.TPIsettingPerDriveSN:
               # Reset the max LBA in RAP, and write RAP to flash
               self.setMaxLBA()
               return

         tpitables = [self.bpiFile.getNominalTracksPerSerpent() for head in range(T210_PARM_NUM_HEADS)]

         prm = {
                  'test_num'          : 210,
                  'CWORD1'            : 0x0042,
                  'CWORD2'            : 0x0000,
                  'TPI_GROUP_EXT'     : tuple(tpitables),
                  'HEAD_RANGE'        : 0x00FF,
                  'ZONE'              : 0x00FF,
               }
         if not testSwitch.FE_0269922_348085_P_SIGMUND_IN_FACTORY:
            prm.update({
                  'dlfile'   : (CN,self.bpiFile.bpiFileName),
                  })


         if testSwitch.FE_0147058_208705_SHORTEN_VBAR_LOGS:
            prm.update({
                  'stSuppressResults' : ST_SUPPRESS__ALL,
            })

         if testSwitch.WA_0152247_231166_P_POWER_CYCLE_RETRY_SIM_ERRORS:
            prm.update({
                  'retryECList'       : [10335],
                  'retryCount'        : 3,
                  'retryMode'         : POWER_CYCLE_RETRY,
            })

            if testSwitch.TRUNK_BRINGUP: #trunk code see 10451 also
                prm.update({
                   'retryECList'       : [10335,10451,10403,10468],
                   })

         if testSwitch.extern.FE_0158806_007867_T210_TPI_SMR_SUPPORT:
            prm['CWORD2'] |= ( CW2_SET_TRACK_PITCH | CW2_SET_TRACK_GUARD | CW2_SET_SHINGLED_DIRECTION | CW2_SET_SQUEEZE_MICROJOG | CW2_SET_TRACKS_PER_BAND)
            prm['TRK_PITCH_TBL'] = tuple([Q0toQ15Factor for head in range(T210_PARM_NUM_HEADS)])
            prm['TRK_GUARD_TBL'] = (0,)*T210_PARM_NUM_HEADS
            prm['SHINGLED_DIRECTION'] = (0,)*T210_PARM_NUM_HEADS
            prm['MICROJOG_SQUEEZE'] = (0,)*T210_PARM_NUM_HEADS
            prm['TRACKS_PER_BAND'] = (1,)*T210_PARM_NUM_HEADS
         prm['prm_name'] = t210PrmName(prm)
         getVbarGlobalClass(CProcess).St(prm)
         getVbarGlobalVar()['formatReload'] = True

      if 'SET_MAX_LBA' in metric:
         # Reset the max LBA in RAP
         self.setMaxLBA()

###########################################################################################################
###########################################################################################################
class CNiblet:
   def __init__(self, nib, params):
      if testSwitch.FE_0115422_340210_FORMATS_BY_MARGIN:
         if "BPI_MARGIN_TARGET" not in nib or "TPI_MARGIN_TARGET" not in nib:
            raiseException(11044, "Niblet settings are incorrect for Formats By margin feature" )
            
      # pre-process
      if testSwitch.FE_0125707_340210_CAP_FROM_BPIFILE:
         NominalCapacityGB    = getVbarGlobalClass(CBpiFile).getNominalCapacity()
      else:
         NominalCapacityGB    = TP.VbarCapacityGBPerHead
      DriveCapacityDefault    = self.getNibletAttr(nib,'CAPACITY_TARGET')*self.getNibletAttr(nib,'NUM_HEADS')*NominalCapacityGB
      CapacityTarget4K        = self.getNibletAttr(nib,'CAPACITY_TARGET_4K') or self.getNibletAttr(nib,'CAPACITY_TARGET')
      DriveCapacity4k         = CapacityTarget4K*self.getNibletAttr(nib,'NUM_HEADS')*NominalCapacityGB
      
      # Relax margin thresholds if selected
      if params.get('NO_MARGIN_SPEC', False):
         if verbose: objMsg.printMsg('CNiblet() params:NO_MARGIN_SPEC')
         BPIMarginThreshold   = BPI_MIN - BPI_MAX
         TPIMarginThreshold   = TPI_MIN - TPI_MAX
      else:
         BPIMarginThreshold   = self.getNibletAttr(nib,'BPI_MARGIN_THRESHOLD',0.0)
         TPIMarginThreshold   = self.getNibletAttr(nib,'TPI_MARGIN_THRESHOLD',0.0)

         # Relax margin thresholds for HMS to control margins
         if params.get('ADJ_MARGIN_SPEC', False):
            if verbose: objMsg.printMsg('CNiblet() params:ADJ_MARGIN_SPEC')
            BPIMarginThreshold   += self.getNibletAttr(nib,'VbarHMSBPIMTAdjust',0.0)
            TPIMarginThreshold   += self.getNibletAttr(nib,'VbarHMSTPIMTAdjust',0.0)
            
      # define setting
      settings = [
         #(key,                           value (OR key of VbarNiblet_Base),     default,                byZone,  switch),
         ('CapacityTarget',               'CAPACITY_TARGET',                     None,                   False,   True),
         ('CapacityTarget4K',             CapacityTarget4K,                      None,                   False,   True),
         ('NumHeads',                     'NUM_HEADS',                           None,                   False,   True),
         ('BPIMinAvg',                    'BPI_MINIMUM_AVERAGE',                 None,                   False,   True),
         ('BPIMaxAvg',                    'BPI_MAXIMUM_AVERAGE',                 None,                   False,   True),
         ('TPIMarginFactor',              'TPI_MARGIN_FACTOR',                   None,                   False,   True),
         ('BPIMarginThreshold',           BPIMarginThreshold,                    None,                   True,    True),
         ('TPIMarginThreshold',           TPIMarginThreshold,                    None,                   True,    True),
         ('BPIMeasurementMargin',         'BPI_MEASUREMENT_MARGIN',              None,                   True,    True),
         ('TPIMeasurementMargin',         'TPI_MEASUREMENT_MARGIN',              None,                   True,    True),
         ('WriteFaultThreshold',          'WRITE_FAULT_THRESHOLD',               None,                   True,    True),
         ('WriteFaultThresholdSlimTrack', 'WRITE_FAULT_THRESHOLD_SLIM_TRACK',    None,                   True,    testSwitch.SMR),
         ('BPICompensationFactor',        'BPI_OVERCOMP_FACTOR',                 None,                   False,   True),
         ('TPICompensationFactor',        'TPI_OVERCOMP_FACTOR',                 None,                   False,   True),
         ('BPITPICompensationFactor',     'BPI_TPI_OVERCOMP_FACTOR',             None,                   False,   True),
         ('VWFT_SLOPE',                   'VWFT_SLOPE',                          100,                    False,   True),
         ('VWFT_ADJUSTMENT_CRITERIA',     'VWFT_ADJUSTMENT_CRITERIA',            0,                      False,   True),
         ('VWFT_MAX_ALLOWED_ADJUSTMENT',  'VWFT_MAX_ALLOWED_ADJUSTMENT',         -3,                     False,   True),
         ('VWFT_MIN_ALLOWED_OCLIM',       'VWFT_MIN_ALLOWED_OCLIM',              12,                     False,   True),
         ('NominalCapacityGB',            NominalCapacityGB,                     None,                   False,   True),
         ('DRIVE_CAPACITY',               'DRIVE_CAPACITY',                      DriveCapacityDefault,   False,   True),
         ('DRIVE_CAPACITY_4K',            DriveCapacity4k,                       None,                   False,   True),
         ('BpiTargetMarginAdjustment',    'BPI_MARGIN_ADJUSTMENT_BY_ZONE',       0,                      True,    True),
         ('TpiTargetMarginAdjustment',    'TPI_MARGIN_ADJUSTMENT_BY_ZONE',       0,                      True,    True),
         ('PBA_TO_LBA_SCALER',            'PBA_TO_LBA_SCALER',                   0.9985,                 False,   True),
         ('BPI_MARGIN_TARGET',            'BPI_MARGIN_TARGET',                   0.0,                    True,    True),
         ('TPI_MARGIN_TARGET',            'TPI_MARGIN_TARGET',                   0.0,                    True,    True),
         ('TracksPerBand',                'TRACKS_PER_BAND',                     1,                      True,    True),
         ('ShingledProportion',           'SHINGLE_PROPORTION',                  1.0,                    True,    testSwitch.DESPERADO),
         ('VbarHMSMinZoneSpec',           'VbarHMSMinZoneSpec',                  0,                      False,   True), # default to no Min Zone Spec
         ('VbarHMSMinHeadSpec',           'VbarHMSMinHeadSpec',                  0,                      False,   True), # default to no Min Head Spec
         ('VbarHMSBPIMTAdjust',           'VbarHMSBPIMTAdjust',                  0,                      False,   True), # default to no BPI Margin Threshold Adjustment
         ('VbarHMSTPIMTAdjust',           'VbarHMSTPIMTAdjust',                  0,                      False,   True), # default to no TPI Margin Threshold Adjustment
         ('MAX_BPI_STEP_ADJ',             'MAX_BPI_STEP_ADJ',                    0.0,                    False,   True),
         ('ATITargetOTFBER',              'ATI_TARGET_OTF_BER',                  5.4,                    False,   True),
         ('OD_THRUPUT_LIMIT',             'OD_THRUPUT_LIMIT',                    80.0,                   False,   True),
         ('ID_THRUPUT_LIMIT',             'ID_THRUPUT_LIMIT',                    40.0,                   False,   True),
         ('MEDIA_CACHE_CAPACITY',         'MEDIA_CACHE_CAPACITY',                0,                      False,   True),
         ('MEDIA_CACHE_CAPACITY_SPEC',    'MEDIA_CACHE_CAPACITY_SPEC',           0,                      False,   True),
         ('UMP_CAPACITY',                 'UMP_CAPACITY',                        0,                      False,   True),
         ('UMP_CAPACITY_SPEC',            'UMP_CAPACITY_SPEC',                   0,                      False,   True),
         ('Adaptive_Guard_Band_Margin',   'Adaptive_Guard_Band_Margin',          0,                      False,   True),
         ('MEDIA_CACHE_SIZE_RAP',         'MEDIA_CACHE_SIZE_RAP',                25,                     False,   testSwitch.FE_0258044_348085_WATERFALL_WITH_ONE_TRK_PER_BAND),
      ]
         
      # apply setting
      self.settings = {}
      for item in settings:
         # if debug_RF: objMsg.printMsg('item %s' % str(item))
         if item[4]:    # switch
            if type(item[2]) is str:
               defaultValue = self.getNibletAttr(nib,[item[2]])
            else:
               defaultValue = item[2]
            if type(item[1]) is str:
               setValue = self.getNibletAttr(nib,item[1],defaultValue)
            else:
               setValue = item[1]
            # if debug_RF: objMsg.printMsg('key %s defaultValue %s setValue %s' % (item[0], str(defaultValue), str(setValue)))
            if item[3]: # byZone
               self.settings[item[0]] = self.zonify(item[0], setValue)
               # if debug_RF: objMsg.printMsg('zonify: %s' % str(self.settings[item[0]]))
            else:
               self.settings[item[0]] = setValue
                  
      # modify setting
      if testSwitch.BPICHMS or testSwitch.FE_CONSOLIDATED_BPI_MARGIN: # BPIMarginThreshold by head
         self.settings['BPIMarginThreshold']   = [list(self.settings['BPIMarginThreshold']) for i in xrange(nib['NUM_HEADS'])]

   #-------------------------------------------------------------------------------------------------------
   def getNibletAttr(self, nib, key, default=None):
      value = nib.get(key, default)
      # provide a function to dynamically extract the value
      if type(value) is str:
         value = eval(value)
      return value
      
   #-------------------------------------------------------------------------------------------------------
   def zonify(self, key, value):
      if type(value) in (int, float):
         return [value] * objDut.numZones
      elif type(value) in (tuple, list):
         if len(value) != objDut.numZones:
            msg = "Niblet to setting key %s length (%d) does not match number of zones (%d)" % (key, len(value), objDut.numZones)
            if not testSwitch.virtualRun:
               raiseException(11044, msg)
            else:
               objMsg.printMsg(msg)
         return deepcopy(value)
      elif type(value) is dict:
         if(objDut.numZones in value):
            return deepcopy(value[objDut.numZones])
         else:
            msg = "Niblet to setting key %s length does not match number of zones (%d)" % (key, objDut.numZones)
            raiseException(11044, msg)
      else:
         raiseException(11044, "Niblet to setting key %s missing or invalid" % key)

   #-------------------------------------------------------------------------------------------------------
   def printTable(self):
      objMsg.printMsg(getVbarGlobalClass(CUtility).convertDictToPrintStr(self.settings,'NIBLET'))

   #----------------------------------------------------------------------------
   def printDbLog(self):
      dblogOccCnt['P_VBAR_NIBLET'] += 1
      objDut.OCC_VBAR_NIBLET = dblogOccCnt['P_VBAR_NIBLET']
      if testSwitch.BPICHMS or testSwitch.FE_CONSOLIDATED_BPI_MARGIN:
         recBPIMarginThreshold = self.settings['BPIMarginThreshold'][0][0]
      else:
         recBPIMarginThreshold = self.settings['BPIMarginThreshold'][0],
      dblog_record = {
                        'SPC_ID'                   : 1,
                        'OCCURRENCE'               : dblogOccCnt['P_VBAR_NIBLET'],
                        'SEQ'                      : objDut.objSeq.getSeq(),
                        'TEST_SEQ_EVENT'           : 1,
                        'CAP_TRGT'                 : self.settings['CapacityTarget'],
                        'NUM_HEADS'                : self.settings['NumHeads'],
                        'BPI_MIN_AVG'              : self.settings['BPIMinAvg'],
                        'BPI_MAX_AVG'              : self.settings['BPIMaxAvg'],
                        'TPI_MRGN_FACTOR'          : self.settings['TPIMarginFactor'],
                        'BPI_MRGN_THRSHLD'         : recBPIMarginThreshold,
                        'TPI_MRGN_THRSHLD'         : self.settings['TPIMarginThreshold'][0],
                        'BPI_MEAS_MRGN'            : self.settings['BPIMeasurementMargin'][0],
                        'TPI_MEAS_MRGN'            : self.settings['TPIMeasurementMargin'][0],
                        'BPI_OVERCOMP_FACTOR'      : self.settings['BPICompensationFactor'],
                        'TPI_OVERCOMP_FACTOR'      : self.settings['TPICompensationFactor'],
                        'BPI_TPI_OVERCOMP_FACTOR'  : self.settings['BPITPICompensationFactor'],
                     }
      objDut.dblData.Tables('P_VBAR_NIBLET').addRecord(dblog_record)
      if testSwitch.FE_0163083_410674_RETRIEVE_P_VBAR_NIBLET_TABLE_AFTER_POWER_RECOVERY:
         objDut.vbar_niblet.append(dblog_record)

###########################################################################################################
###########################################################################################################
class CPicker(CVbarDataStore):
   """
      This class is responsible for picking the appropriate BPI/TPI capability picks based on
      measured capabilities and specified margins. The algorithm is implemented as per Bruce Emo's
      specification.
   """
   def __init__(self, niblet, measurements, limits, SendVbarFmtSummaryToEDW=True, active_zones=[]):
      self.tpiMarginCalMethod = 0
      self.dut = objDut
      self.settings = niblet.settings
      self.recordData = {}                           # Dictionary used for displaying picker operartion.
      self.numHeads = self.dut.imaxHead
      self.bpiFile = getVbarGlobalClass(CBpiFile)
      self.numUserZones = self.bpiFile.getNumUserZones()
      self.objTestZones = CVbarTestZones()
      self.TPI_STEP_SIZE = 1.0 / self.bpiFile.getNominalTracksPerSerpent()
      self.spcIdHlpr = getVbarGlobalClass(CSpcIdHelper, {'dut':self.dut})
      if debug_VE: objMsg.printMsg('frm CPicker - self.numUserZones : %d self.numHeads : %d' % (self.numUserZones,self.numHeads))
      # Set up some table reporting overhead.
      if testSwitch.FE_0171684_007867_DISPLAY_PICKER_AS_TBL:
         self.spcId = self.spcIdHlpr.getSpcId('P_VBAR_FORMAT_SUMMARY')
         dblogOccCnt['P_VBAR_PICKER_FMT_ADJUST'] += 1 # increment dblog sequence number to avoid pkey violations when updating oracle
         dblogOccCnt['P_VBAR_PICKER_RESULTS'] += 1    # increment dblog sequence number to avoid pkey violations when updating oracle
         self.recordData['OCCURRENCE'] = dblogOccCnt['P_VBAR_PICKER_FMT_ADJUST']

      self.tracksPerBand = self.settings['TracksPerBand']

      if testSwitch.ADAPTIVE_GUARD_BAND :
         self.mediaCacheZone = range(1,min(TP.UMP_ZONE[self.numUserZones]),1) # start from 1 as the zone 0 is AGB zone
      else:
         self.mediaCacheZone = range(0,min(TP.UMP_ZONE[self.numUserZones]),1)

      self.umpZone = TP.UMP_ZONE[self.numUserZones][0:(len(TP.UMP_ZONE[self.numUserZones])-1)]

      self.userZonesExcludeUMP = range(max(self.umpZone)+1,self.numUserZones,1 )

      printDbgMsg('self.mediaCacheZone = %s' % (str(self.mediaCacheZone)))
      printDbgMsg('self.umpZone = %s' % (str(self.umpZone)))
      printDbgMsg('self.userZonesExcludeUMP = %s' % (str(self.userZonesExcludeUMP)))

      self.VbarHMSMaxPickerStep = limits['MAX_BPI_STEP']
      self.VbarHMSMaxBPIAdjust = limits['MAX_BPI_PICKER_ADJ']
      self.VbarHMSMaxTPIAdjust = limits['MAX_TPI_PICKER_ADJ']
      wifi_adjustment = (self.VbarHMSMaxPickerStep < 0.5)

      # Zone masking - Optionally pass in a list of (hd,zn) tuples for zones that may be changed by the picker
      self.active_zones = active_zones
      if self.active_zones == []:
         self.active_zones = [(hd, zn) for hd in xrange(self.numHeads) for zn in xrange(self.dut.numZones)]

      self.measurements = measurements

      if not testSwitch.CM_REDUCTION_REDUCE_PRINTMSG:
         niblet.printTable()
         self.displayFormatLimits()

      self.baseformat = [0]*self.numHeads

      if self.bpiFile.hasSectorPerTrackInfo():
         self.sendFormatToDrive = False
         self.BpiFileCapacityCalc = True
         # figure out what sector size is used in the bpifile
         if testSwitch.WA_0256539_480505_SKDC_M10P_BRING_UP_DEBUG_OPTION:
           for self.sectorsize in [4096, 512]:
            if self.bpiFile.hasSectorPerTrackInfo(self.sectorsize):
               break
         else:
           for self.sectorsize in [512,4096]:
            if self.bpiFile.hasSectorPerTrackInfo(self.sectorsize):
               break
         if self.sectorsize == 4096:
            self.capacityTarget = self.settings['CapacityTarget4K']
         else:
            self.capacityTarget = self.settings['CapacityTarget']
      else:
         self.sendFormatToDrive = True
         self.BpiFileCapacityCalc = False
         self.capacityTarget = self.settings['CapacityTarget']
         self.sectorsize = 4096 

      self.formatScaler = CVbarFormatScaler()

      # initialize local data
      data = {
         'BpiCapability'         : ('f',  0.0   ), 
         'TpiCapability'         : ('f',  0.0   ), 
         'BpiCapabilityNoAdj'    : ('f',  0.0   ), 
         'BpiMargin'             : ('f',  0.0   ), 
         'TpiMargin'             : ('f',  0.0   ),
         'BpiPick'               : ('f',  0.0   ),
         'TpiPick'               : ('f',  0.0   ),
         'BpiPickInitial'        : ('f',  0.0   ),
         'TpiPickInitial'        : ('f',  0.0   ),
         'BpiFormat'             : ('i',  0     ),
         'TpiFormat'             : ('i',  0     ),
         'BpiMarginTarget'       : ('f',  0.0   ), 
         'TpiMarginTarget'       : ('f',  0.0   ),
         'TpiMarginThresScale'   : ('f',  0.0   ),
         'OkToIncreaseBpi'       : ('c',  'F'   ), #False
         'OkToDecreaseBpi'       : ('c',  'F'   ), #False
         'OkToIncreaseTpi'       : ('c',  'F'   ), #False
         'OkToDecreaseTpi'       : ('c',  'F'   ), #False
         'AdjustedBpiFormat'     : ('c',  'F'   ), #False
         'AdjustedTpiFormat'     : ('c',  'F'   ), #False
         'BpiInterpolated'       : ('c',  'N'   ), 
         'TpiInterpolated'       : ('c',  'N'   ), 
         'BPIMS'                 : ('f',  0.0   ),
         'BPIMF'                 : ('f',  0.0   ),
         'BPIMH'                 : ('f',  0.0   ),
         'BPIMSQZ'               : ('f',  0.0   ),
      }
      CVbarDataStore.__init__(self, data)
      self.buildStore(self.numHeads, self.numUserZones)
      
      # TODO: optimize this routine?
      for hd in xrange(self.numHeads):
         for zn in xrange(self.numUserZones):
            pickerData = CVbarDataHelper(self, hd, zn)
            meas = self.measurements.getNibletizedRecord(hd, zn)
            bpiPick = self.formatScaler.getBPIPick(hd, zn)
            bpiFormat = self.formatScaler.getFormat(hd, zn, 'BPI')
            tpiPick = self.formatScaler.getTPIPick(hd, zn)
            tpiFormat = self.formatScaler.getFormat(hd, zn, 'TPI')

            pickerData['BpiCapability']         = meas['BPI']
            pickerData['TpiCapability']         = meas['TPI']
            pickerData['BpiCapabilityNoAdj']    = meas['BPI'] - meas['BPIAdj']
            pickerData['BpiMargin']             = meas['BPI'] - bpiPick
            pickerData['TpiMargin']             = meas['TPI'] - tpiPick
            pickerData['BpiPick']               = bpiPick
            pickerData['TpiPick']               = tpiPick
            pickerData['BpiPickInitial']        = bpiPick
            pickerData['TpiPickInitial']        = tpiPick
            pickerData['BpiFormat']             = bpiFormat
            pickerData['TpiFormat']             = tpiFormat
            pickerData['TpiMarginThresScale']   = niblet.settings['TPIMarginThreshold'][zn]  # added for VBAR by ATI
            if (hd,zn) in self.active_zones:
               pickerData['OkToIncreaseBpi']    = 'T'
               pickerData['OkToIncreaseTpi']    = 'T'
               pickerData['OkToDecreaseBpi']    = 'T'
               pickerData['OkToDecreaseTpi']    = 'T'
            if meas['Interp'] == 'T':
               pickerData['BpiInterpolated']    = 'Y'
               pickerData['TpiInterpolated']    = 'Y'

      self.initializeMarginMatrix(wifi_adjustment)

   #-------------------------------------------------------------------------------------------------------
   def displayFormatLimits(self):
      objMsg.printMsg('*'*20)
      objMsg.printMsg('FORMAT LIMITS')
      objMsg.printMsg('*'*20)
      objMsg.printMsg('TPI Step: %6.4f' % (self.TPI_STEP_SIZE))
      objMsg.printMsg('TPI %6.4f-%6.4f' % (TPI_MIN,TPI_MAX))
      objMsg.printMsg('BPI %6.4f-%6.4f' % (BPI_MIN, BPI_MAX))
      objMsg.printMsg('*'*20)
      if testSwitch.FE_0152775_420281_P_DISPLAY_ADC_FOR_ADG_CAPTURE_POOR_HEAD:
         objMsg.printMsg('Head  MaxBPI  BPI_MT  TPI_MT  AVG_ADC')
      else:
         objMsg.printMsg('Head  MaxBPI  BPI_MT  TPI_MT')
      for hd in range(self.numHeads):
         if testSwitch.BPICHMS or testSwitch.FE_CONSOLIDATED_BPI_MARGIN:
            bpimt = self.settings['BPIMarginThreshold'][hd][0] + self.dut.BPIMarginThresholdAdjust[hd]
         else:
            bpimt = self.settings['BPIMarginThreshold'][0] + self.dut.BPIMarginThresholdAdjust[hd]
         tpimt = self.settings['TPIMarginThreshold'][0] + self.dut.TPIMarginThresholdAdjust[hd]
         if testSwitch.FE_0152775_420281_P_DISPLAY_ADC_FOR_ADG_CAPTURE_POOR_HEAD:
            adcAvg = self.dut.avgADC[hd]
            objMsg.printMsg('%4d  %6.4f  %6.4f  %6.4f  %6.4f' % (hd, maxBPI[hd], bpimt, tpimt, adcAvg))
         else:
            objMsg.printMsg('%4d  %6.4f  %6.4f  %6.4f' % (hd, maxBPI[hd], bpimt, tpimt))
      
   #-------------------------------------------------------------------------------------------------------
   def initializeMarginMatrix(self, wifi_adjustment):
      """Build the tables of relative frequency thresholds to control when a zone will change BPI tables."""
      numHeads = self.bpiFile.bpiNumHeads
      BPIMinFormat = self.bpiFile.getMinFormat()
      BPIMaxFormat = self.bpiFile.getMaxFormat()
      maxBpiProfiles = self.bpiFile.getNumBpiFormats()
      self.marginChangeFromNominal =   list(list(list(0 for fmt in xrange(maxBpiProfiles)) for zn in xrange(self.numUserZones)) for hd in xrange(numHeads))
      self.marginToIncreasePick =      list(list(list(0 for fmt in xrange(maxBpiProfiles)) for zn in xrange(self.numUserZones)) for hd in xrange(numHeads))
      self.marginToDecreasePick =      list(list(list(0 for fmt in xrange(maxBpiProfiles)) for zn in xrange(self.numUserZones)) for hd in xrange(numHeads))
      
      for hd in xrange(numHeads):
         for zn in xrange(self.numUserZones):
            # Build table of relative frequencies by format table number
            nominalFrequency = self.bpiFile.getFrequencyByFormatAndZone(0,zn,hd)
            for idx, fmt in enumerate(xrange(BPIMinFormat,BPIMaxFormat+1)):
               self.marginChangeFromNominal[hd][zn][idx] = self.bpiFile.getFrequencyByFormatAndZone(fmt,zn,hd)/nominalFrequency
            
            # add sentinels
            self.marginChangeFromNominal[hd][zn].append(2000000)
            self.marginChangeFromNominal[hd][zn].append(-2000000)
            # Put the thresholds at the midpoints
            for idx in xrange(maxBpiProfiles):
               self.marginToIncreasePick[hd][zn][idx] = (self.marginChangeFromNominal[hd][zn][idx+1]-self.marginChangeFromNominal[hd][zn][idx])/2
               self.marginToDecreasePick[hd][zn][idx] = (self.marginChangeFromNominal[hd][zn][idx-1]-self.marginChangeFromNominal[hd][zn][idx])/2
            
            # Increase the threshold required to bump initial picks to minimize big jumps in frequency (WIFI keepout region)
            if wifi_adjustment:
               avgThreshold = mean(self.marginToIncreasePick[hd][zn], trim=True)
               for idx in xrange(maxBpiProfiles):
                  if self.marginToIncreasePick[hd][zn][idx] > avgThreshold * 2:
                     self.marginToIncreasePick[hd][zn][idx] *= 2
                     self.marginToIncreasePick[hd][zn][idx] -= avgThreshold

   #-------------------------------------------------------------------------------------------------------
   def getTracksPerZone(self):
      return [(self.bpiFile.getNominalTracksPerSerpent() + self.getRecord('TpiFormat',hd,zn)) * self.bpiFile.getNumSerpentsInZone(self.baseformat[hd],zn,hd) for hd in xrange(self.bpiFile.bpiNumHeads) for zn in xrange(self.numUserZones)]

   #-------------------------------------------------------------------------------------------------------
   def getDriveCapacity(self, debug_DriveCapacity = 0):
      if self.BpiFileCapacityCalc:
         #calculate the number of sectors per zone
         sectorsPerTrack = [self.bpiFile.getSectorsPerTrack(self.getRecord('BpiFormat',hd,zn),zn,hd) for hd in xrange(self.bpiFile.bpiNumHeads) for zn in xrange(self.numUserZones)]
         TracksPerZone = self.getTracksPerZone()
         if debug_DriveCapacity:
            objMsg.printMsg("self.baseformat %s" % self.baseformat)
            objMsg.printMsg("Hd  Zn  BPI_FMT  TPI_FMT  SptPerZone  SctPerTrack")
            objMsg.printMsg('-'* 50)
            for hd in xrange(self.numHeads):
               for zn in xrange(self.numUserZones):
                  pickerData = CVbarDataHelper(self, hd, zn)
                  num_spt_per_zone = self.bpiFile.getNumSerpentsInZone(self.baseformat[hd],zn,hd) 
                  num_sectors_per_track = self.bpiFile.getSectorsPerTrack(pickerData['BpiFormat'],zn,hd)
                  tpi_fmt = self.bpiFile.getNominalTracksPerSerpent() + pickerData['TpiFormat']
                  bpi_fmt = self.bpiFile.nominalFormat + pickerData['BpiFormat']
                  objMsg.printMsg("%2d  %2d  %7d  %7d  %10d  %11d" % (hd,zn,bpi_fmt,tpi_fmt,num_spt_per_zone,num_sectors_per_track))
         if testSwitch.ADAPTIVE_GUARD_BAND:
            # ignore Z0 capacity if Adaptive Guard Band is run.
            for hd in range(self.numHeads):
               sectorsPerTrack[(hd * self.numUserZones) + 0] = 0
               TracksPerZone[(hd * self.numUserZones) + 0] = 0
         numsectors = sum(map(operator.mul,sectorsPerTrack,TracksPerZone))
         driveCapacity = self.settings['PBA_TO_LBA_SCALER'] * numsectors * self.sectorsize / float(1e9)
         if verbose:
            objMsg.printMsg("B:driveCapacity = %.3f" %driveCapacity)
         if testSwitch.FE_0297446_348429_P_PRECISE_PARITY_ALLOCATION:
            driveCapacity -= (sum(TracksPerZone) * TP.ParitySec_perTrack  * self.sectorsize / float(1e9))
         if verbose:
            objMsg.printMsg("C:driveCapacity = %.3f" %driveCapacity)
         if (testSwitch.ADAPTIVE_GUARD_BAND):
            driveCapacity += self.z0FinalCapacity
            if verbose:
               objMsg.printMsg("self.z0FinalCapacity = %.3f" %self.z0FinalCapacity)
            self.agbDriveCapacity = driveCapacity

         if not testSwitch.FE_0171684_007867_DISPLAY_PICKER_AS_TBL:
            objMsg.printMsg("Calculated capacity = %f GB" % driveCapacity)
         return driveCapacity

      reader = DBLogReader(self.dut, 'P210_CAPACITY_DRIVE', suppressed = True)
      reader.ignoreExistingData()
      getVbarGlobalClass(CProcess).St({'test_num':210,'CWORD1':8, 'SCALED_VAL': int(self.settings['PBA_TO_LBA_SCALER'] * 10000), 'DblTablesToParse': ['P210_CAPACITY_DRIVE'], 'spc_id' : -1})
      return reader.getTableObj()[-1]['DRV_CAPACITY']

   #-------------------------------------------------------------------------------------------------------
   def getAvgDensity(self):
      """Return the average density across all heads"""
      if testSwitch.FE_0125707_340210_CAP_FROM_BPIFILE:
         if testSwitch.FE_0171684_007867_DISPLAY_PICKER_AS_TBL:
            # Update the recordData dictionary for later use in a tabular display of the data.
            self.recordData['COMPUTED_CAP_GB'] = float(self.getDriveCapacity())
            self.recordData['AVE_DENSITY'] = self.recordData['COMPUTED_CAP_GB'] / self.bpiFile.getNominalCapacity()
            return self.recordData['AVE_DENSITY']
         else:
            return float(self.getDriveCapacity()) / self.bpiFile.getNominalCapacity()

      else:
         if testSwitch.FE_0171684_007867_DISPLAY_PICKER_AS_TBL:
            # Update the recordData dictionary for later use in a tabular display of the data.
            self.recordData['COMPUTED_CAP_GB'] = float(self.getDriveCapacity())
            self.recordData['AVE_DENSITY'] = self.recordData['COMPUTED_CAP_GB'] / float(TP.VbarCapacityGBPerHead) / float(self.numHeads)
            return self.recordData['AVE_DENSITY']
         else:
            return (float(self.getDriveCapacity()) / float(TP.VbarCapacityGBPerHead)) / float(self.numHeads)

   #-------------------------------------------------------------------------------------------------------
   def selectMostCommonFormat(self, hd, metric):
      """Returns the format number that is most common across the zones"""
      if metric=='BPI':
         FormatByZone = self.getRecordForHead('BpiFormat',hd)
      else:
         FormatByZone = self.getRecordForHead('TpiFormat',hd)

      # create a dictionary that contains how many times each format is selected
      formatdict = {}
      for format in FormatByZone:
         formatdict[format] = 1 + formatdict.get(format,0)
      baseformat = sorted([(y,x) for x,y in formatdict.items()]).pop()[1]
      return baseformat

   #-------------------------------------------------------------------------------------------------------
   def setFormat(self, metric, hd=0xff, zn=0xff, movezoneboundaries=False):
      """
      setFormat sets the drive BPI and TPI formats to the requested values
      If movezoneboundaries is true, then the BPI format must be set by head, and
      it will set the user zone configuration (zone boundaries).
      Otherwise just the BPI or TPI will be set on the head and zone requested
      """

      if not self.sendFormatToDrive:
         return

      prm_210 = {'test_num': 210,
                 'prm_name': 'Update Formats To Drive',
                 'timeout' : 1800,
                 #'dlfile'  : (CN, self.bpiFile.bpiFileName),
                 'spc_id'  : 0,
                 }
      if not testSwitch.FE_0269922_348085_P_SIGMUND_IN_FACTORY:
         prm_210.update({
                 'dlfile'   : (CN,self.bpiFile.bpiFileName),
                 })
      if testSwitch.WA_0152247_231166_P_POWER_CYCLE_RETRY_SIM_ERRORS:
         prm_210.update({
               'retryECList'       : [10335],
               'retryCount'        : 3,
               'retryMode'         : POWER_CYCLE_RETRY,
               })

         if testSwitch.TRUNK_BRINGUP: #trunk code see 10451 also
             prm_210.update({
                'retryECList'       : [10335,10451,10403,10468],
                })

      if testSwitch.FE_0147058_208705_SHORTEN_VBAR_LOGS:
         prm_210['stSuppressResults'] = ST_SUPPRESS__ALL

      starthead=hd
      endhead=hd
      if hd==0xff:
         endhead = self.numHeads-1
         starthead = 0
      startzone = zn
      endzone = zn
      if zn==0xff:
         startzone=0
         endzone=self.numUserZones-1

      # Container for the format update st calls
      commands = []

      # Iterate through all zones and build the T210 call packets for BPI and TPI
      # If heads/zones haven't changed since the last update, don't set them again
      # Combine zones that are equivalent in all respects
      nominalFormat = self.bpiFile.getNominalFormat()
      nominalTracks = self.bpiFile.getNominalTracksPerSerpent()
      for zn in xrange(startzone,endzone+1):
         bpitables = []
         tpitables = []
         bpi_head_mask = 0
         tpi_head_mask = 0
         
         for hd in xrange(T210_PARM_NUM_HEADS):
            if hd >= starthead and hd <= endhead:
               pickerData = CVbarDataHelper(self, hd, zn)
               # Set up BPI formats
               bpitables.append(nominalFormat+pickerData['BpiFormat']) 
               if testSwitch.extern.FE_0158806_007867_T210_TPI_SMR_SUPPORT:
                  # Set up Track Pitch formats
                  tpitables.append(int(math.ceil((float(nominalTracks)/(nominalTracks+pickerData['TpiFormat']))*Q0toQ15Factor)))
               else:
                  # Set up TPI formats
                  tpitables.append(nominalTracks+pickerData['TpiFormat'])
               # Set up head masks
               if pickerData['AdjustedBpiFormat'] == 'T':
                  bpi_head_mask |= 1 << hd

               if pickerData['AdjustedTpiFormat'] == 'T':
                  tpi_head_mask |= 1 << hd
            else:
               # Set up BPI formats
               bpitables.append(nominalFormat)
               # Set up TPI formats
               tpitables.append(nominalTracks)

         # Issue BPI and TPI separately if the head masks don't match
         if metric == 'BOTH' and bpi_head_mask != tpi_head_mask:
            metrics = ['BPI', 'TPI']
         else:
            metrics = [metric]

         for local_metric in metrics:
            # Build the command packet
            command = {
                           'CWORD1'    : 0x0100,
                           'HEAD_MASK' : 0x0000,
                           'ZONE'      : (zn << 8) | zn,
                           'CWORD2'    : 0x0000,
                         }

            if local_metric in ('BPI', 'BOTH'):
               command['CWORD1'] |= SET_BPI
               command['HEAD_MASK'] |= bpi_head_mask
               command['BPI_GROUP_EXT'] = bpitables

            if local_metric in ('TPI', 'BOTH'):
               command['CWORD1'] |= SET_TPI
               command['HEAD_MASK'] |= tpi_head_mask

               if testSwitch.extern.FE_0158806_007867_T210_TPI_SMR_SUPPORT:
                  command['TRK_PITCH_TBL'] = tpitables
                  # Indicate the track pitch table should be updated in the RAP
                  command['CWORD2'] |= CW2_SET_TRACK_PITCH

               else:
                  command['TPI_GROUP_EXT'] = tpitables


            # If no heads are active, skip the command altogether
            if command['HEAD_MASK'] == 0:
               continue

            # Look for other identical zones
            for previous in commands:
               keys_to_compare = command.keys()
               keys_to_compare.remove("ZONE")  # Don't compare zones - they're always different
               equal = reduce(lambda x, y: x and y, [previous.get(key, None) == command.get(key, None) for key in keys_to_compare])
               if equal and ((previous["ZONE"] & 0xFF) == zn - 1):
                  # Include the new zone and move on
                  previous["ZONE"] &= 0xFF00
                  previous["ZONE"] |= zn
                  break
            else:
               # No matches; add the new command
               commands.append(command)

      # Actually issue the commands
      for command in commands:
         parms = prm_210.copy()
         parms.update(command)
         parms['prm_name'] = t210PrmName(parms)

         getVbarGlobalClass(CProcess).St(parms)

         # Mark these zones as "Reset" so that they get re-optimized and measured
         if command['CWORD1'] & SET_BPI:
            startzn  = (command['ZONE'] & 0xFF00) >> 8
            endzn    = (command['ZONE'] & 0x00FF)
            _wp      = isinstance(self.measurements, CVbarWpMeasurement) and TP.WPForVBPINominalMeasurements or None
            for hd in xrange(starthead, endhead+1):
               if command['HEAD_MASK'] & (1 << hd):
                  for zn in xrange(startzn, endzn+1):
                     self.measurements.setRecord('BPIChanged', 'T', hd, zn, _wp) 

         # Clear the OPTI_ZAP_DONE flag if TPI is changed
         if command['CWORD1'] & SET_TPI:
            self.dut.driveattr['OPTI_ZAP_DONE'] = 0
      getVbarGlobalVar()['formatReload'] = True


   #-----------------------------------------------------------------------------
   def findMargin(self, metric, criteria, inZn=None, inHd=None, report=False):
      """
      Find the head and zone with the smallest margin to target that has
      room to decrease its bpi or tpi
      return list that includes:
      1: True/False if valid zone found
      2: head
      3: zone
      4: whether the zone can change BPI or TPI
      """

      if criteria == 'Best':
         limit = 'OkToIncrease'
         nextformat = 1
      else:
         limit = 'OkToDecrease'
         nextformat = 0

      # restrict the search to certain zones if requested
      if not inZn:
         CandidateZones = xrange(self.numUserZones)
      else:
         CandidateZones = inZn
      if not inHd:
         CandidateHeads = xrange(self.numHeads)
      else:
         CandidateHeads = [inHd]

      if report:
         objMsg.printMsg('Hd, Zn, Limit, Margin')
         
      if criteria != 'Best':
         margin = (float('inf'), -1, -1, '')
         cmpFunc = min
      else:
         margin = (float('-inf'), -1, -1, '')
         cmpFunc = max
      for hd in CandidateHeads:
         for zn in CandidateZones:
            pickerData = CVbarDataHelper(self, hd, zn)
            # if BPI or ANY is requested add bpimargin
            if metric != 'TPI':
               if pickerData[limit+'Bpi']:
                  marginChange = self.marginChangeFromNominal[getBpiHeadIndex(hd)][zn]
                  chgIdx = pickerData['BpiFormat']-self.bpiFile.getMinFormat()+nextformat
                  bpiMargin = pickerData['BpiCapability']-marginChange[chgIdx]-pickerData['BpiMarginTarget']
                  margin = cmpFunc(margin, (bpiMargin,hd,zn,'BPI'))
                  if report:
                     objMsg.printMsg('%2d %3d, %s=%d, %2.4f' % (hd, zn, limit+'Bpi', pickerData[limit+'Bpi'], bpiMargin))
               else:
                  if report:
                     objMsg.printMsg('%2d %3d, %s=%d' % (hd, zn, limit+'Bpi', pickerData[limit+'Bpi']))

            # if TPI or ANY is requested add tpimargin
            if metric != 'BPI':
               if pickerData[limit+'Tpi']:
                  if self.tpiMarginCalMethod == 0:
                     tpiMargin = pickerData['TpiCapability']-pickerData['TpiPick']-pickerData['TpiMarginTarget']
                  else:
                     tpiMargin = pickerData['TpiMargin']-pickerData['TpiMarginTarget']
                  margin = cmpFunc(margin, (tpiMargin,hd,zn,'TPI'))
                  if report:
                     objMsg.printMsg('%2d %3d, %s=%d, %2.4f' % (hd, zn, limit+'Tpi', pickerData[limit+'Tpi'], tpiMargin))
               else:
                  if report:
                     objMsg.printMsg('%2d %3d, %s=%d' % (hd, zn, limit+'Tpi', pickerData[limit+'Tpi']))
                  
      if not margin[3]:
         return (False, -1, -1, metric)
      else:
         return margin

   #-------------------------------------------------------------------------------------------------------
   def adjustTPI(self,hd,worstzone,formatDelta):
      zn = worstzone #the input is just zone not worstzone
      zfi = CVbarDataHelper(self, hd, zn)
      zfi['TpiFormat'] += formatDelta    # TpiFormat is an index value
      zfi['TpiPick'] = 1.0 + zfi['TpiFormat'] * self.TPI_STEP_SIZE

      # If the zone has been changed, set flag to update the format
      if self.bpiFile.hasSectorPerTrackInfo():
         if zfi['TpiFormat'] == self.formatScaler.getFormat(hd, zn, 'TPI'):
            zfi['AdjustedTpiFormat'] = 'F'
         else:
            zfi['AdjustedTpiFormat'] = 'T'
      else:
         if formatDelta != 0:
            zfi['AdjustedTpiFormat'] = 'T'      # Set up sentinel to force format update before getting capacity

      # Define useful terms to make the Increase and Decrease TPI conditionals below, easier to follow.
      TPIPick        = zfi['TpiPick']           # Current track pitch as a percent of nominal.
      TPIPickInitial = zfi['TpiPickInitial']    # Initial track pitch as a percent of nominal, prior to any adjustment.
      TPIC           = zfi['TpiCapability']     # Track pitch capability as a percent of nominal.
      nextTPIPick    = TPIPick + self.TPI_STEP_SIZE # Track pitch at the next higher tpi setting, step size is in % of nominal.
      prevTPIPick    = TPIPick - self.TPI_STEP_SIZE # Track pitch at the next lower tpi setting, relative to nominal.
      marginAtNextTPIPick = TPIC - nextTPIPick      # Margin at next higher track pitch.
      # Effective margin threshold = minimum allowed margin threshold plus a possible adjustment for heads with different write power table.
      if (testSwitch.VBAR_TPI_MARGIN_THRESHOLD_BY_HD_BY_ZN):
         effectiveMarginThreshold = zfi['TpiMarginThresScale'] + self.dut.TPIMarginThresholdAdjust[hd]
      else:
         effectiveMarginThreshold = self.settings['TPIMarginThreshold'][zn] + self.dut.TPIMarginThresholdAdjust[hd]

      # Check to see if it is okay to INCREASE the TPI Pick selection for this hd-zn combination.
      if ( (marginAtNextTPIPick < (effectiveMarginThreshold - RndErrCorrFactor)) or  # limit to user assigned margin threshold.
           (nextTPIPick > TPI_MAX) or                                                # limit track density to prescribed maximum.
           (abs(nextTPIPick - TPIPickInitial) > self.VbarHMSMaxTPIAdjust) or         # limit overall track pitch change.
           ((hd,zn) not in self.active_zones) ):                                     # limit change to user specified hd/zn list.
         zfi['OkToIncreaseTpi'] = 'F'
      else:
         if testSwitch.ADAPTIVE_GUARD_BAND and zn == 0:
            zfi['OkToIncreaseTpi'] = 'F'
         else:
            zfi['OkToIncreaseTpi'] = 'T'

      # Check to see if it is okay to DECREASE the TPI Pick selection for this hd-zn combination.
      if ( (prevTPIPick < TPI_MIN) or                                                # limit track density to prescribed minimum.
           (abs(prevTPIPick - TPIPickInitial) > self.VbarHMSMaxTPIAdjust) or         # limit overall track pitch change.
           ((hd,zn) not in self.active_zones) ):                                     # limit change to user specified hd/zn list.
         zfi['OkToDecreaseTpi'] = 'F'
      else:
         zfi['OkToDecreaseTpi'] = 'T'

   #-------------------------------------------------------------------------------------------------------
   def adjustBPI(self,hd,zn,formatDelta):
      BPIMinFormat = self.bpiFile.getMinFormat()
      BPIMaxFormat = self.bpiFile.getMaxFormat()
      zfi = CVbarDataHelper(self, hd, zn)
      zfi['BpiFormat'] += formatDelta    # BpiFormat is an index value
      chgIdx = zfi['BpiFormat']-BPIMinFormat
      zfi['BpiPick'] = self.marginChangeFromNominal[getBpiHeadIndex(hd)][zn][chgIdx]

      if self.bpiFile.hasSectorPerTrackInfo():
         # If the zone has been changed, set flag to update the format
         if zfi['BpiFormat'] == self.formatScaler.getFormat(hd, zn, 'BPI'):
            zfi['AdjustedBpiFormat'] = 'F'
         else:
            zfi['AdjustedBpiFormat'] = 'T'
      else:
         if formatDelta != 0:
            zfi['AdjustedBpiFormat'] = 'T'   # Set up sentinel to force format update before getting capacity

      # Define useful terms to make the Increase and Decrease BPI conditionals below, easier to follow.
      bpiFormat      = zfi['BpiFormat']           # Current BPI format index into the BPI File.
      bpiPickInitial = zfi['BpiPickInitial']      # Initial BPI frequency pick, relative to nominal frequency.
      BPIC           = zfi['BpiCapabilityNoAdj']  # Current BPI Capability (frequency) pick, relative to nominal frequency.
      currBPIPick = self.marginChangeFromNominal[getBpiHeadIndex(hd)][zn][chgIdx]    # BPI Pick of the current available frequency in the table.
      nextBPIPick = self.marginChangeFromNominal[getBpiHeadIndex(hd)][zn][chgIdx+1]  # BPI Pick of the next available frequency in the table.
      prevBPIPick = self.marginChangeFromNominal[getBpiHeadIndex(hd)][zn][chgIdx-1]  # BPI Pick of the previous available frequency in the table.
      # Effective margin threshold = minimum allowed margin threshold plus a possible adjustment for heads with different write power table.
      if testSwitch.BPICHMS or testSwitch.FE_CONSOLIDATED_BPI_MARGIN:
         effectiveMarginThreshold = self.settings['BPIMarginThreshold'][hd][zn] + self.dut.BPIMarginThresholdAdjust[hd]
      else:
         effectiveMarginThreshold = self.settings['BPIMarginThreshold'][zn] + self.dut.BPIMarginThresholdAdjust[hd]

      # Check to see if it is okay to increase the BPI Pick selection for this hd-zn combination.
      if ((bpiFormat == BPIMaxFormat) or
           # Margin at next available BPI Pick from the frequency table < minimum allowed BPI margin
           (BPIC - nextBPIPick < (effectiveMarginThreshold - RndErrCorrFactor)) or
           (nextBPIPick - currBPIPick > self.VbarHMSMaxPickerStep) or
           (abs(nextBPIPick - bpiPickInitial) > self.VbarHMSMaxBPIAdjust) or
           (hd,zn) not in self.active_zones):
         zfi['OkToIncreaseBpi'] = 'F'
      else:
         if testSwitch.ADAPTIVE_GUARD_BAND and zn == 0:
            zfi['OkToIncreaseBpi'] = 'F'
         else:
            zfi['OkToIncreaseBpi'] = 'T'

      # Check to see if it is okay to decrease the BPI Pick selection for this hd-zn combination.
      if ((bpiFormat == BPIMinFormat) or
           (abs(prevBPIPick - bpiPickInitial) > self.VbarHMSMaxBPIAdjust) or
           ((hd,zn) not in self.active_zones)):
         zfi['OkToDecreaseBpi'] = 'F'
      else:
         zfi['OkToDecreaseBpi'] = 'T'

   #-------------------------------------------------------------------------------------------------------
   def getTpiStepSize(self, zone=None):
      return 1
   #-------------------------------------------------------------------------------------------------------
   def increaseUMPDensity(self, metric):
      return self.increaseDensity(metric,inZone = self.umpZone)

   #-------------------------------------------------------------------------------------------------------
   def increaseMediaCacheDensity(self, metric):
      return self.increaseDensity(metric,inZone = self.mediaCacheZone)

   #-------------------------------------------------------------------------------------------------------
   def increaseDensity(self, metric , inZone = None):
      if (testSwitch.virtualRun and not verifyPicker):
         # In VE, capacity is fixed
         return False

      found, hd, zn, metric = self.findMargin(metric, 'Best', inZone)
      if not found:
         return False

      # Update reporting record with values for head, zone, and metric chosen, and increasing capacity.
      self.recordData.update({'LGC_HD':hd, 'ZONE':zn, 'FMT_TYPE':metric, 'CAP_ADJUST':'Inc'})
      pickerData = CVbarDataHelper(self, hd, zn)

      if metric == 'TPI':
         self.adjustTPI(hd, zn, self.getTpiStepSize(zn))
         if testSwitch.FE_0171684_007867_DISPLAY_PICKER_AS_TBL:
            self.recordData.update({'RELATIVE_PICK':pickerData['TpiPick'], 'SELECTED_FORMAT':pickerData['TpiFormat']})
         else:
            objMsg.printMsg('Increase TPI hd %d zn %d to %6.4f  %d' % (hd, zn, pickerData['TpiPick'],pickerData['TpiFormat']))
      else:
         self.adjustBPI(hd,zn,+1)
         if testSwitch.FE_0171684_007867_DISPLAY_PICKER_AS_TBL:
            self.recordData.update({'RELATIVE_PICK':pickerData['BpiPick'], 'SELECTED_FORMAT':pickerData['BpiFormat']})
         else:
            objMsg.printMsg('Increase BPI hd %d zn %d to %6.4f  %d' % (hd, zn, pickerData['BpiPick'], pickerData['BpiFormat']))
      if testSwitch.FE_0257373_348085_ZONED_SERVO_CAPACITY_CALCULATION:
         self.setFormat(metric,hd,zn, programZonesWithZipperZonesOnly = 1, print_table = 0)
      else:
         self.setFormat(metric,hd,zn)
      return True

   #-------------------------------------------------------------------------------------------------------
   def decreaseDensity(self, metric, inZone = None):
      if (testSwitch.virtualRun and not verifyPicker):
         # In VE, capacity is fixed
         return False

      found, hd, zn, metric = self.findMargin(metric, 'Worst' ,inZone)
      if not found:
         return False

      # Update reporting record with values for head, zone, and metric chosen, and decreasing capacity.
      self.recordData.update({'LGC_HD':hd, 'ZONE':zn, 'FMT_TYPE':metric, 'CAP_ADJUST':'Dec'})
      pickerData = CVbarDataHelper(self, hd, zn)

      if metric == 'TPI':
         self.adjustTPI(hd, zn, -self.getTpiStepSize(zn))
         if testSwitch.FE_0171684_007867_DISPLAY_PICKER_AS_TBL:
            self.recordData.update({'RELATIVE_PICK':pickerData['TpiPick'], 'SELECTED_FORMAT':pickerData['TpiFormat']})
         else:
            objMsg.printMsg('Decrease TPI hd %d zn %d to %6.4f' % (hd, zn, pickerData['TpiPick']))
      else:
         self.adjustBPI(hd,zn,-1)
         if testSwitch.FE_0171684_007867_DISPLAY_PICKER_AS_TBL:
            self.recordData.update({'RELATIVE_PICK':pickerData['BpiPick'], 'SELECTED_FORMAT':pickerData['BpiFormat']})
         else:
            objMsg.printMsg('Decrease BPI hd %d zn %d to %6.4f' % (hd, zn, pickerData['BpiPick']))
      if testSwitch.FE_0257373_348085_ZONED_SERVO_CAPACITY_CALCULATION:
         self.setFormat(metric,hd,zn, programZonesWithZipperZonesOnly = 1, print_table = 0)
      else:
         self.setFormat(metric,hd,zn)
      return True

   #-------------------------------------------------------------------------------------------------------
   def pickTPI(self):
      for hd in xrange(self.numHeads): 
         for zn in xrange(self.numUserZones):
            zfi = CVbarDataHelper(self, hd, zn)
            self.adjustTPI(hd,zn,0)
            while True:
               margin = zfi['TpiCapability'] - zfi['TpiPick'] - zfi['TpiMarginTarget']
               if testSwitch.VBAR_TPI_MARGIN_THRESHOLD_BY_HD_BY_ZN:
                  marginOverThreshold = zfi['TpiCapability'] - zfi['TpiPick'] - (zfi['TpiMarginThresScale'] + self.dut.TPIMarginThresholdAdjust[hd])
               else:
                  marginOverThreshold = zfi['TpiCapability'] - zfi['TpiPick'] - (self.settings['TPIMarginThreshold'][zn] + self.dut.TPIMarginThresholdAdjust[hd])

               if (margin >= self.TPI_STEP_SIZE/2.0) and (zfi['OkToIncreaseTpi'] == 'T'):
                  self.adjustTPI(hd,zn,+1)
               elif ((margin < -self.TPI_STEP_SIZE/2.0) or (marginOverThreshold < - RndErrCorrFactor)) and (zfi['OkToDecreaseTpi'] == 'T'):
                  self.adjustTPI(hd,zn,-1)
               else:
                  break

      # Display initial pick table
      if not testSwitch.FE_0171684_007867_DISPLAY_PICKER_AS_TBL:
         self.displayCapability('TPI')

      self.setFormat('TPI')

   #-------------------------------------------------------------------------------------------------------
   def pickBPI(self):
      for hd in xrange(self.numHeads):
         for zn in xrange(self.numUserZones):
            zfi = CVbarDataHelper(self, hd, zn)   # contains the zone format information
            self.adjustBPI(hd,zn,0)
            while True:
               margin = zfi['BpiCapability']-zfi['BpiPick']-zfi['BpiMarginTarget']
               if testSwitch.BPICHMS or testSwitch.FE_CONSOLIDATED_BPI_MARGIN:
                  marginOverThreshold = zfi['BpiCapabilityNoAdj']-zfi['BpiPick']-(self.settings['BPIMarginThreshold'][hd][zn]+self.dut.BPIMarginThresholdAdjust[hd])
               else:
                  marginOverThreshold = zfi['BpiCapabilityNoAdj']-zfi['BpiPick']-(self.settings['BPIMarginThreshold'][zn]+self.dut.BPIMarginThresholdAdjust[hd])
               idx = zfi['BpiFormat']-self.bpiFile.getMinFormat()
               marginToIncreasePick = self.marginToIncreasePick[getBpiHeadIndex(hd)][zn][idx]   
               marginToDecreasePick = self.marginToDecreasePick[getBpiHeadIndex(hd)][zn][idx]
               if (margin >= marginToIncreasePick) and (zfi['OkToIncreaseBpi'] == 'T'):
                  self.adjustBPI(hd,zn,+1)
               elif ((margin < marginToDecreasePick) or (marginOverThreshold < -RndErrCorrFactor)) and (zfi['OkToDecreaseBpi'] == 'T'):
                  self.adjustBPI(hd,zn,-1)
               else:
                  break

      # Display initial pick table
      if not testSwitch.FE_0171684_007867_DISPLAY_PICKER_AS_TBL:
         self.displayCapability('BPI')

      self.setFormat('BPI', movezoneboundaries=True)

   #-------------------------------------------------------------------------------------------------------
   def checkMinimumCapability(self, TPICap, BPICap, debug_DriveCapacity = 0):
      """
      Screen each head for minimum density requirements.
      Fail if any head fails the minimum check.
      Calculate the minimum density required before the picker algorithm will run.
      This figure is a function of the Capabilities and the Margin Thresholds.
      """



      if testSwitch.LCO_VBAR_PROCESS:

         BPIMT = mean(self.settings['BPIMarginThreshold'])
         BPIMTA = self.dut.BPIMarginThresholdAdjust
         TPIMT = mean(self.settings['TPIMarginThreshold'])
         TPIMTA = self.dut.TPIMarginThresholdAdjust
         maxDensity = mean([(BPICap[hd] - (BPIMT + BPIMTA[hd])) * (TPICap[hd] - (TPIMT + TPIMTA[hd])) for hd in range(self.numHeads)])

         #judge if head is narrow head, if yes, force drive to low capacity
         if testSwitch.OEM_Waterfall_Enable == 1:
            maxDensity = 0.5
            objMsg.printMsg('OEM drive need to be forced to low capacity!')
            testSwitch.OEM_Waterfall_Enable = 0


         objMsg.printMsg('BPICap[hd] = %6.4f, BPIMTA[hd] = %6.4f' % (BPICap[hd], BPIMTA[hd]))
         objMsg.printMsg('TPICap[hd] = %6.4f, TPIMTA[hd] = %6.4f' % (TPICap[hd], TPIMTA[hd]))



         #objMsg.printMsg('MaxDensitycc = %6.4f, TargetDensitycc = %6.4f' % (maxDensity, self.capacityTarget))


         objMsg.printMsg('MaxDensity = %6.4f, TargetDensity = %6.4f' % (maxDensity, self.capacityTarget))

         if verbose:
            for hd in range(self.numHeads):
               objMsg.printMsg('Hd %d: TPICap %1.4f, BPICap %1.4f, BPIMT %1.4f, BPIMTA %1.4f, TPIMT %1.4f, TPIMTA %1.4f' % (hd, TPICap[hd], BPICap[hd], BPIMT, BPIMTA[hd], TPIMT, TPIMTA[hd]))

      else:
         if testSwitch.VBAR_TPI_MARGIN_THRESHOLD_BY_HD_BY_ZN:
            if testSwitch.CAL_TRUE_MAX_CAPACITY:
               tempdata = [0]*self.numHeads
               for hd in range(self.numHeads):
                  tempdata[hd]=[]
                  for zn in range(self.numUserZones):
                     tempdata[hd].append({'Head'           : hd,
                                     'Zone'                : zn,
                                     'BpiFormat'           : 0,
                                     'TpiFormat'           : 0,
                                     })
               if debug_DriveCapacity:
                  objMsg.printMsg("%2s  %2s  %7s  %7s" %("Hd", "Zn", "new BPI_FMT", "new TPI_FMT"))
            else:
               #TPIMT = mean([self.data[hd][zn]['TpiMarginThresScale'] for hd in range(self.numHeads) for zn in range (self.numUserZones)])
               #=== Print table header: Calc max density table
               objMsg.printMsg('\n')
               objMsg.printMsg('CALCULATE MAX DENSITY')
               objMsg.printMsg('=' * 100)
               objMsg.printMsg("%2s  %2s  %9s  %9s  %9s  %9s  %9s  %9s  %9s" %("Hd", "Zn", "Bpic", "Bmt", "adjBpi", "Tpic", "Tmt", "Tmts", "adjTpi"))
            objMsg.printMsg('=' * 100)

            bpicSum = 0.0
            tpicSum = 0.0
            capSum = 0.0
            for hd in xrange(self.numHeads):
               for zn in xrange(self.numUserZones):
                  pickerData = CVbarDataHelper(self, hd, zn)
                  if testSwitch.BPICHMS or testSwitch.FE_CONSOLIDATED_BPI_MARGIN:
                     bpim = self.settings['BPIMarginThreshold'][hd][zn] + self.dut.BPIMarginThresholdAdjust[hd]
                  else:
                     bpim = self.settings['BPIMarginThreshold'][zn] + self.dut.BPIMarginThresholdAdjust[hd]
                  bpic = pickerData['BpiCapability'] - bpim
                  if testSwitch.VBAR_TPIM_SLOPE_CAL:
                     tpim = pickerData['TpiMarginThresScale']
                  else:
                     tpim = pickerData['TpiMarginThresScale'] * self.settings['TPIMarginThreshold'][zn]
                  tpic = pickerData['TpiCapability'] - tpim
                  bpicSum += bpic
                  tpicSum += tpic
                  if testSwitch.CAL_TRUE_MAX_CAPACITY:
                     tempdata[hd][zn]['BpiFormat'] = self.getClosestBPITable(bpic,zn,hd)
                     tempdata[hd][zn]['TpiFormat'] = self.getClosestTPITable(tpic)
                     if debug_DriveCapacity:
                        objMsg.printMsg("%2d  %2d  %11d  %11d" %(hd,zn,tempdata[hd][zn]['BpiFormat'],tempdata[hd][zn]['TpiFormat']))
                  else:
                     #=== Print table content: Calc max density table
                     if testSwitch.BPICHMS or testSwitch.FE_CONSOLIDATED_BPI_MARGIN:
                        objMsg.printMsg("%2d  %2d  %9.4f  %9.4f  %9.4f  %9.4f  %9.4f  %9.4f  %9.4f" %(hd, zn, pickerData['BpiCapability'], self.settings['BPIMarginThreshold'][hd][zn] + self.dut.BPIMarginThresholdAdjust[hd], bpic,\
                                       pickerData['TpiCapability'], self.settings['TPIMarginThreshold'][zn], pickerData['TpiMarginThresScale'], tpic))
                     else:
                        objMsg.printMsg("%2d  %2d  %9.4f  %9.4f  %9.4f  %9.4f  %9.4f  %9.4f  %9.4f" %(hd, zn, pickerData['BpiCapability'], self.settings['BPIMarginThreshold'][zn] + self.dut.BPIMarginThresholdAdjust[hd], bpic,\
                                       pickerData['TpiCapability'], self.settings['TPIMarginThreshold'][zn], pickerData['TpiMarginThresScale'], tpic))
            aveBpic = bpicSum / (self.numUserZones * self.numHeads)
            aveTpic = tpicSum / (self.numUserZones * self.numHeads)
            self.maxDensity = aveBpic * aveTpic
         else:
            BPIMT = mean(self.settings['BPIMarginThreshold'])
            BPIMTA = self.dut.BPIMarginThresholdAdjust
            TPIMT = mean(self.settings['TPIMarginThreshold'])
            TPIMTA = self.dut.TPIMarginThresholdAdjust
            self.maxDensity = mean([(BPICap[hd] - (BPIMT + BPIMTA[hd])) * (TPICap[hd] - (TPIMT + TPIMTA[hd])) for hd in range(self.numHeads)])
            if verbose:
               for hd in range(self.numHeads):
                  objMsg.printMsg('Hd %d: TPICap %1.4f, BPICap %1.4f, BPIMT %1.4f, BPIMTA %1.4f, TPIMT %1.4f, TPIMTA %1.4f' % (hd, TPICap[hd], BPICap[hd], BPIMT, BPIMTA[hd], TPIMT, TPIMTA[hd]))

         aveDensity = self.getAvgDensity()
         if testSwitch.CAL_TRUE_MAX_CAPACITY:
            objMsg.printMsg("%2s  %2s  %9s  %9s  %9s  %9s  %9s  %9s  %9s  %9s" %("Hd", "Zn", "Bpic", "Bmt", "adjBpi", "Tpic", "Tmt", "Tmts", "adjTpi", "adjCap"))
            objMsg.printMsg('=' * 100)
            sectorsPerTrack = [self.bpiFile.getSectorsPerTrack(tempdata[hd][zn]['BpiFormat'],zn,hd) for hd in range(self.numHeads) for zn in range(self.numUserZones)]
            TracksPerZone = [(TP.VbarNomSerpentWidth + tempdata[hd][zn]['TpiFormat']) * self.bpiFile.getNumSerpentsInZone(self.baseformat[hd],zn,hd) for hd in range(self.numHeads) for zn in range(self.numUserZones)]

            for hd in xrange(self.numHeads):
               for zn in xrange(self.numUserZones):
                  pickerData = CVbarDataHelper(self, hd, zn)
                  if testSwitch.BPICHMS or testSwitch.FE_CONSOLIDATED_BPI_MARGIN:
                     bpim = self.settings['BPIMarginThreshold'][hd][zn] + self.dut.BPIMarginThresholdAdjust[hd]
                  else:
                     bpim = self.settings['BPIMarginThreshold'][zn] + self.dut.BPIMarginThresholdAdjust[hd]
                  bpic = pickerData['BpiCapability'] - bpim
                  if testSwitch.VBAR_TPIM_SLOPE_CAL:
                     tpim = pickerData['TpiMarginThresScale']
                  else:
                     tpim = pickerData['TpiMarginThresScale'] * self.settings['TPIMarginThreshold'][zn]
                  tpic = pickerData['TpiCapability'] - tpim
                  adjCap = sectorsPerTrack[hd * self.numUserZones + zn] * TracksPerZone[hd * self.numUserZones + zn] * self.sectorsize/float(1e9)
                  capSum += adjCap
                  #=== Print table content: Calc max density table
                  if testSwitch.BPICHMS or testSwitch.FE_CONSOLIDATED_BPI_MARGIN:
                     objMsg.printMsg("%2d  %2d  %9.4f  %9.4f  %9.4f  %9.4f  %9.4f  %9.4f  %9.4f  %9.4f" %(hd, zn, pickerData['BpiCapability'], self.settings['BPIMarginThreshold'][hd][zn] + self.dut.BPIMarginThresholdAdjust[hd] , bpic,\
                                       pickerData['TpiCapability'], self.settings['TPIMarginThreshold'][zn], pickerData['TpiMarginThresScale'], tpic, adjCap))
                  else:
                     objMsg.printMsg("%2d  %2d  %9.4f  %9.4f  %9.4f  %9.4f  %9.4f  %9.4f  %9.4f  %9.4f" %(hd, zn, pickerData['BpiCapability'], self.settings['BPIMarginThreshold'][zn] + self.dut.BPIMarginThresholdAdjust[hd] , bpic,\
                                       pickerData['TpiCapability'], self.settings['TPIMarginThreshold'][zn], pickerData['TpiMarginThresScale'], tpic, adjCap))
            if debug_DriveCapacity:
               objMsg.printMsg("self.baseformat %s" % self.baseformat)
               objMsg.printMsg("HD  ZN  BPI_FMT  TPI_FMT  SptPerZone  SctPerTrack")
               objMsg.printMsg('*'* 50)
            for hd in range(self.numHeads):
               for zn in range(self.numUserZones):
                  num_spt_per_zone = self.bpiFile.getNumSerpentsInZone(self.baseformat[hd],zn,hd)
                  num_sectors_per_track = self.bpiFile.getSectorsPerTrack(tempdata[hd][zn]['BpiFormat'],zn,hd)
                  tpi_fmt = self.bpiFile.getNominalTracksPerSerpent() + tempdata[hd][zn]['TpiFormat']
                  bpi_fmt = self.bpiFile.nominalFormat + tempdata[hd][zn]['BpiFormat']
                  if debug_DriveCapacity:
                     objMsg.printMsg("%2d  %2d  %7d  %7d  %10d  %11d" % (hd,zn,bpi_fmt,tpi_fmt,num_spt_per_zone,num_sectors_per_track))
            capGB = self.settings['NominalCapacityGB'] * self.numHeads
            true_maxDensity = capSum / capGB  # Hardcoded Value, need to improve later to calculate nominal
            objMsg.printMsg('=' * 75)
            objMsg.printMsg('MAX DENSITY')
            objMsg.printMsg('AveDensity\tMaxDensity\tTargetDensity\tTrueCapacity\tTrueADC10K')
            objMsg.printMsg('=' * 75)
            objMsg.printMsg('%10.4f\t%10.4f\t%13.4f\t%12.2f\t%10.4f' % (aveDensity, self.maxDensity, self.settings['CapacityTarget'], capSum, true_maxDensity))
            self.maxDensity = true_maxDensity #assign the true_maxDensity back to self.maxDensity to be used later by others
         else:
            objMsg.printMsg('=' * 49)
            objMsg.printMsg('MAX DENSITY')
            objMsg.printMsg('AveDensity\tMaxDensity\tTargetDensity')
            objMsg.printMsg('=' * 49)
            objMsg.printMsg('%10.4f\t%10.4f\t%13.4f' % (aveDensity, self.maxDensity, self.settings['CapacityTarget']))
            objMsg.printMsg('=' * 49)
            #objMsg.printMsg('MaxDensity = %6.4f, TargetDensity = %6.4f' % (maxDensity, self.capacityTarget))

         if testSwitch.VBAR_TPI_MARGIN_THRESHOLD_BY_HD_BY_ZN: #scp make use of P_VBAR_SUMMARY2 1st row to display True Capacity
            # Update DBLog
            self.dut.dblData.Tables('P_VBAR_SUMMARY2').addRecord(
                           {
                           'SPC_ID'          : 1,
                           'OCCURRENCE'      : 1,
                           'SEQ'             : self.dut.objSeq.getSeq(),
                           'TEST_SEQ_EVENT'  : 1,
                           'HD_LGC_PSN'      : 0,
                           'HD_PHYS_PSN'     : 0,
                           'BPI_CAP'         : round(aveDensity,4),
                           'BPI_PICK'        : round(self.maxDensity,4),
                           'BPI_MRGN'        : round(self.settings['CapacityTarget'],4),
                           'BPI_TABLE_NUM'   : 0,
                           'TPI_CAP'         : round(capSum / 100,4), # used to display true cap
                           'TPI_PICK'        : 0,
                           'TPI_MRGN'        : 0,
                           'TPI_TABLE_NUM'   : 0,
                           })

            for hd in xrange(self.numHeads):
               for zn in xrange(self.numUserZones):
                  pickerData = CVbarDataHelper(self, hd, zn)
                  if testSwitch.BPICHMS or testSwitch.FE_CONSOLIDATED_BPI_MARGIN:
                     bpim = self.settings['BPIMarginThreshold'][hd][zn] + self.dut.BPIMarginThresholdAdjust[hd]
                  else:
                     bpim = self.settings['BPIMarginThreshold'][zn] + self.dut.BPIMarginThresholdAdjust[hd]
                  bpic = pickerData['BpiCapability'] - bpim
                  if testSwitch.VBAR_TPIM_SLOPE_CAL:
                     tpim = pickerData['TpiMarginThresScale']
                  else:
                     tpim = pickerData['TpiMarginThresScale'] * self.settings['TPIMarginThreshold'][zn]
                  tpic = pickerData['TpiCapability'] - tpim
                  self.dut.dblData.Tables('P_VBAR_SUMMARY2').addRecord(
                           {
                           'SPC_ID'          : 2,
                           'OCCURRENCE'      : zn,
                           'SEQ'             : self.dut.objSeq.getSeq(),
                           'TEST_SEQ_EVENT'  : 1,
                           'HD_LGC_PSN'      : hd,
                           'HD_PHYS_PSN'     : self.dut.LgcToPhysHdMap[hd],
                           'BPI_CAP'         : round(pickerData['BpiCapability'], 4),
                           'BPI_PICK'        : round(bpic, 4),
                           'BPI_MRGN'        : round(bpim, 4),
                           'BPI_TABLE_NUM'   : 0,
                           'TPI_CAP'         : round(pickerData['TpiCapability'], 4),
                           'TPI_PICK'        : round(tpic, 4),
                           'TPI_MRGN'        : round(tpim, 4),
                           'TPI_TABLE_NUM'   : 0,
                           })
                  if testSwitch.FE_CONSOLIDATED_BPI_MARGIN:
                     try:
                        niblet_ref = self.settings['Niblet_Index']
                     except:
                        niblet_ref = 9
                     self.dut.dblData.Tables('P_VBAR_MAX_FORMAT_SUMMARY').addRecord(
                           {
                           'SPC_ID'          : 1,
                           'OCCURRENCE'      : 1,
                           'SEQ'             : self.dut.objSeq.getSeq(),
                           'TEST_SEQ_EVENT'  : 1,
                           'HD_PHYS_PSN'     : self.dut.LgcToPhysHdMap[hd],
                           'DATA_ZONE'       : zn,
                           'HD_LGC_PSN'      : hd,
                           'BPI_CAP'         : round(pickerData['BpiCapability'], 4),
                           'BPIM_SEG'        : round(pickerData['BPIMS'], 4),
                           'BPIM_FSOW'       : round(pickerData['BPIMF'], 4),
                           'BPIM_HMS'        : round(pickerData['BPIMH'], 4),#round(bpim, 4),
                           'BPIM_FINAL'      : round(bpim, 4),
                           'BPIP_MAX'        : round(bpic, 4),
                           'TPI_CAP'         : round(pickerData['TpiCapability'], 4),
                           'TPIM_ATI'        : round(tpim, 4),
                           'TPIP_MAX'        : round(tpic, 4),
                           'ADC_MAX'         : round(tpic * bpic, 4),
                           'NIBLET_IDX'      : niblet_ref,
                           })
            objMsg.printDblogBin(self.dut.dblData.Tables('P_VBAR_SUMMARY2'))
            if testSwitch.FE_CONSOLIDATED_BPI_MARGIN and (not testSwitch.CM_REDUCTION_REDUCE_PRINTDBLOGBIN):
               objMsg.printDblogBin(self.dut.dblData.Tables('P_VBAR_MAX_FORMAT_SUMMARY'))
         #judge if head is narrow head, if yes, force drive to low capacity
         if testSwitch.OEM_Waterfall_Enable == 1:
            self.maxDensity = 0.5
            objMsg.printMsg('OEM drive need to be forced to low capacity!')
            testSwitch.OEM_Waterfall_Enable = 0




      # Verify minimum capabilities on each head
      failed = False

      if testSwitch.FE_0114266_231166_INTERPOLATE_SINGLE_ZONE_FAILED_VBAR_MEASURES:
         maxNumInterpolates = round(0.15 * self.numUserZones,0)
         for hd in xrange(self.numHeads):
            numInterpolates = 0
            for zn in xrange(self.numUserZones):
               marginChangeFromNominal = self.marginChangeFromNominal[getBpiHeadIndex(hd)][zn][0]
               if testSwitch.BPICHMS or testSwitch.FE_CONSOLIDATED_BPI_MARGIN:
                  bpifailed, bpi_interpolated = self.interpolateFailedMeasurement(hd, zn, 'BpiCapability', self.settings['BPIMarginThreshold'][hd][zn] + self.dut.BPIMarginThresholdAdjust[hd], marginChangeFromNominal, 'BpiInterpolated')
               else:
                  bpifailed, bpi_interpolated = self.interpolateFailedMeasurement(hd, zn, 'BpiCapability', self.settings['BPIMarginThreshold'][zn] + self.dut.BPIMarginThresholdAdjust[hd], marginChangeFromNominal, 'BpiInterpolated')
               if testSwitch.VBAR_TPI_MARGIN_THRESHOLD_BY_HD_BY_ZN:
                  tpifailed, tpi_interpolated = self.interpolateFailedMeasurement(hd, zn, 'TpiCapability', self.getRecord('TpiMarginThresScale',hd,zn) + self.dut.TPIMarginThresholdAdjust[hd], TPI_MIN, 'TpiInterpolated')
               else:
                  tpifailed, tpi_interpolated = self.interpolateFailedMeasurement(hd, zn, 'TpiCapability', self.settings['TPIMarginThreshold'][zn] + self.dut.TPIMarginThresholdAdjust[hd], TPI_MIN, 'TpiInterpolated')
               failed = bpifailed or tpifailed or failed
               if tpi_interpolated or bpi_interpolated:
                  numInterpolates += 1

            if numInterpolates > maxNumInterpolates:
               failed = True
               objMsg.printMsg("Number of interpolated zones exceeded %d for head %d" % (maxNumInterpolates,hd))
      else:
         for hd in xrange(self.numHeads):
            for zn in xrange(self.numUserZones):
               pickerData = CVbarDataHelper(self, hd, zn)
               marginChangeFromNominal = self.marginChangeFromNominal[getBpiHeadIndex(hd)][zn][0]
               if testSwitch.BPICHMS or testSwitch.FE_CONSOLIDATED_BPI_MARGIN:
                  if pickerData['BpiCapability'] - (self.settings['BPIMarginThreshold'][hd][zn] + self.dut.BPIMarginThresholdAdjust[hd]) < marginChangeFromNominal:
                     failed = True
                     objMsg.printMsg('BPI capability fail hd %d zn %d' % (hd,zn))
               else:
                  if pickerData['BpiCapability'] - (self.settings['BPIMarginThreshold'][zn] + self.dut.BPIMarginThresholdAdjust[hd]) < marginChangeFromNominal:
                     failed = True
                     objMsg.printMsg('BPI capability fail hd %d zn %d' % (hd,zn))
               if testSwitch.VBAR_TPI_MARGIN_THRESHOLD_BY_HD_BY_ZN:
                  if pickerData['TpiCapability'] - (pickerData['TpiMarginThresScale']) < TPI_MIN:
                     failed = True
                     objMsg.printMsg('TPI capability fail hd %d zn %d' % (hd,zn))
               else:
                  if pickerData['TpiCapability'] - (self.settings['TPIMarginThreshold'][zn] + self.dut.TPIMarginThresholdAdjust[hd]) < TPI_MIN:
                     failed = True
                     objMsg.printMsg('TPI capability fail hd %d zn %d' % (hd,zn))

      return failed

   #-------------------------------------------------------------------------------------------------------
   def checkLimit(self, value, margin, limit):
      """Returns true if check fails"""
      return (value - margin) < limit

   #-------------------------------------------------------------------------------------------------------
   def interpolateFailedMeasurement(self, hd, zn, element, margin, limit, element_interpNotification):
      """Returns the fail status of interpolating this zone if necessary"""
      pickerData = CVbarDataHelper(self, hd, zn)
      failed = self.checkLimit(pickerData[element], margin, limit)
      interpolated = False
      if failed:
         objMsg.printMsg('%s fail hd %d zn %d- Interpolating' % (element, hd,zn))
         if testSwitch.FE_0140674_407749_P_TWO_ZONE_INTERPOLATE:
            zonelimit = 2
            if zn == 0:
               for retrycnt in xrange(1,zonelimit+1):
                  elementData = self.getRecord(element, hd, zn+retrycnt)
                  failed = self.checkLimit(elementData, margin, limit)
                  if not failed:
                     pickerData[element] = elementData
                     break
            elif zn == self.numUserZones -1:
               for retrycnt in xrange(1,zonelimit+1):
                  elementData = self.getRecord(element, hd, zn-retrycnt)
                  failed = self.checkLimit(elementData, margin, limit)
                  if not failed:
                     pickerData[element] = elementData
                     break
            #check on last zone -1
            elif (zn==(self.numUserZones -2)) and self.checkLimit(self.getRecord(element,hd,self.numUserZones-1), margin, limit):
               for retrycnt in xrange(1,zonelimit+1):
                  elementData = self.getRecord(element, hd, zn-retrycnt)
                  failed = self.checkLimit(elementData, margin, limit)
                  if not failed:
                     pickerData[element] = elementData
                     break
            else:
               for retrycnt in xrange(1,zonelimit+1):
                  elementData = self.getRecord(element, hd, zn+retrycnt)
                  Rfailed = self.checkLimit(elementData, margin, limit)
                  if not Rfailed:
                     Rzone=retrycnt
                     break
               for retrycnt in range(1,zonelimit+1):
                  elementData = self.getRecord(element, hd, zn-retrycnt)
                  Lfailed = self.checkLimit(elementData, margin, limit)
                  if not Lfailed:
                     Lzone=retrycnt
                     break
               failed = Lfailed or Rfailed
               if not failed:
                  #((y2-y1)/2) + y1 since 2 zones sep the interp points and delta x is always 1
                  elementData1 = self.getRecord(element, hd, zn+Rzone)
                  elementData2 = self.getRecord(element, hd, zn-Lzone)
                  pickerData[element] = ((elementData1-elementData2)/(Rzone+Lzone))*(Lzone)+elementData2
         else:
            if zn == 0:
               elementData = self.getRecord(element, hd, zn+1)
               failed = self.checkLimit(elementData, margin, limit)
               if not failed:
                  pickerData[element] = elementData
            elif zn == self.numUserZones -1:
               elementData = self.getRecord(element, hd, zn-1)
               failed = self.checkLimit(elementData, margin, limit)
               if not failed:
                  pickerData[element]= elementData
            else:
               elementData1 = self.getRecord(element, hd, zn+1)
               elementData2 = self.getRecord(element, hd, zn-1)
               failed = self.checkLimit(elementData1, margin, limit) or self.checkLimit(elementData2, margin, limit)
               if not failed:
                  #((y2-y1)/2) + y1 since 2 zones sep the interp points and delta x is always 1
                  pickerData[element] = ((elementData1-elementData2)/2.0)+elementData2

         if failed:
            objMsg.printMsg("\tUnable to interpolate using adjacent zones capabilities.")
            interpolated = False
         else:
            objMsg.printMsg("\tInterpolated hd %d zn %d to value %3.3f" % (hd, zn, pickerData[element]))
            self.setRecord(element_interpNotification,'Y',hd,zn)
            interpolated = True

      failed = self.checkLimit(pickerData[element], margin, limit)

      return failed, interpolated

   #-------------------------------------------------------------------------------------------------------
   def performance(self):
      return mean(self.store['BpiPick'])

   #-------------------------------------------------------------------------------------------------------
   def computeMargins(self):
      # Compute BPI and TPI margins, for all heads and zones, based on capabilities and picks.
      for hd in xrange(self.numHeads):
         for zn in xrange(self.numUserZones):
            zfi = CVbarDataHelper(self, hd, zn)
            zfi['BpiMargin'] = zfi['BpiCapability']-zfi['BpiPick']
            zfi['TpiMargin'] = zfi['TpiCapability']-zfi['TpiPick']

   #-------------------------------------------------------------------------------------------------------
   def displayCapability(self, metric=None):
      if not testSwitch.FE_0171684_007867_DISPLAY_PICKER_AS_TBL:
         # Display either BPI or TPI capability data, based on metric selection.
         if metric == 'BPI':
            tableStr = '%2s\t%2s\t%7s\t%7s\t%7s' % ('Hd', 'Zn', 'BPICap', 'BPITbl', 'BPIPck')
            column_3 = 'BpiCapability'
            column_4 = 'BpiFormat'
            column_5 = 'BpiPick'
         else:
            tableStr = '%2s\t%2s\t%7s\t%7s\t%7s' % ('Hd', 'Zn', 'TPICap', 'TPITbl', 'TPIPck')
            column_3 = 'TpiCapability'
            column_4 = 'TpiFormat'
            column_5 = 'TpiPick'

      for hd in xrange(self.numHeads):
         for zn in xrange(self.numUserZones):
            zfi = zfi = CVbarDataHelper(self, hd, zn)
            if testSwitch.FE_0171684_007867_DISPLAY_PICKER_AS_TBL:
               self.dut.dblData.Tables('P_VBAR_INITIAL_PICKS').addRecord({
                  'SPC_ID'            : self.spcId,
                  'OCCURRENCE'        : self.recordData['OCCURRENCE'],
                  'SEQ'               : self.dut.objSeq.getSeq(),
                  'TEST_SEQ_EVENT'    : 1,
                  'HD_LGC_PSN'        : hd,
                  'DATA_ZONE'         : zn,
                  'BPI_CAP'           : round(zfi['BpiCapability'],4),
                  'BPI_TABLE_NUM'     : zfi['BpiFormat'],
                  'BPI_PICK'          : round(zfi['BpiPick'],2),
                  'BPI_MRGN'          : round(zfi['BpiCapability']-zfi['BpiPick'],4),
                  'TPI_CAP'           : round(zfi['TpiCapability'],4),
                  'TPI_TABLE_NUM'     : zfi['TpiFormat'],
                  'TPI_PICK'          : round(zfi['TpiPick'],2),
                  'TPI_MRGN'          : round(zfi['TpiCapability']-zfi['TpiPick'],4),
                 })

            else:
               tableStr += '\n%2d\t%2d\t%7.4f\t%7d\t%7.4f' % (hd, zn, zfi[column_3], zfi[column_4], zfi[column_5])

      if testSwitch.FE_0171684_007867_DISPLAY_PICKER_AS_TBL:
         objMsg.printDblogBin(self.dut.dblData.Tables('P_VBAR_INITIAL_PICKS'), self.spcId)
      else:
         objMsg.printMsg('\n%s' % tableStr)

   #-------------------------------------------------------------------------------------------------------
   def pickBPITPI(self):
      """
      Pick the best BPI/TPgI settings for the given capacity point
      and capability matrix.  Based on Bruce Emo's algorithm
      """
      objMsg.printMsg('*'* 40 + ' FORMAT PICKER ' + '*'*40)

      MARGIN_LIMIT        = 0.24
      MARGIN_FACTOR_LIMIT = 0.5
      MIN_CAP_LIMIT       = 0.12
      MARGIN_INTERCEPT    = 0.12
      MARGIN_SLOPE1       = 6.0
      MARGIN_SLOPE2       = 5.0

      # Calculate the average capabilities for each head
      TPICap = [mean(self.getRecordForHead('TpiCapability',hd)) for hd in xrange(self.numHeads)]
      BPICap = [mean(self.getRecordForHead('BpiCapability',hd)) for hd in xrange(self.numHeads)]

      self.z0FinalCapacity = 0
      self.agbDriveCapacity = 0
      self.finalDriveCapacity = 0

      # Verify that the capabilities provide the target capacity at least
      if self.checkMinimumCapability(TPICap, BPICap):
         objMsg.printMsg('*'*40 + ' FAILED MINIMUM CAPABILITY ' + '*'*40)
         return ATPI_FAIL_CAPABILITY

      # Adjust for non-nominal capacity targets
      NormalizedTPICap = [TPICap[hd]/math.sqrt(self.capacityTarget) for hd in xrange(self.numHeads)]
      NormalizedBPICap = [BPICap[hd]/math.sqrt(self.capacityTarget) for hd in xrange(self.numHeads)]
      for hd in xrange(self.numHeads):
         objMsg.printMsg('TPICap=%.4f, BPICap=%.4f, Capacity=%.4f, RTPICap=%.4f, RBPICap=%.4f' % (TPICap[hd], BPICap[hd], self.capacityTarget, NormalizedTPICap[hd], NormalizedBPICap[hd]))

      # Compute TPI_Margin factor
      DrvMargin = mean(NormalizedTPICap) + mean(NormalizedBPICap) - 2
      objMsg.printMsg('TPIMarginFactor=%.4f DrvMargin=%.4f' % (self.settings['TPIMarginFactor'], DrvMargin))
      TPIMF = self.settings['TPIMarginFactor']  # TPIMarginFactor is set in the Niblet
      if DrvMargin <= MARGIN_LIMIT:
         if TPIMF <= MARGIN_FACTOR_LIMIT:
            Breakpoint = 0.1 + (1.0/(1.0-TPIMF) - 1.0)*0.1
            Slope = MARGIN_SLOPE1 - MARGIN_SLOPE2*(1.0/(1-TPIMF) - 1.0)
         else:
            Breakpoint = 0.1 + (1.0/TPIMF - 1.0) * 0.1;
            Slope = 1.0/(MARGIN_SLOPE1 - MARGIN_SLOPE2 * (1.0/TPIMF - 1.0))
         objMsg.printMsg('Breakpt = %.4f, Slope = %.4f ' % (Breakpoint,Slope))

         if DrvMargin > Breakpoint:
            Offset = MARGIN_INTERCEPT - Slope * MARGIN_INTERCEPT
            TgtBPIM = (DrvMargin - Offset)/(1.0 + Slope)
            TgtTPIM = DrvMargin - TgtBPIM
            TPIMF = TgtTPIM/(TgtTPIM + TgtBPIM)
            objMsg.printMsg('Slope=%.4f, Offset= %.4f, TgtBPIM=%.4f, TgtTPIM=%.4f' % (Slope, Offset, TgtBPIM, TgtTPIM))
      else:
         TPIMF = 0.5
      objMsg.printMsg('TPIMF = %.4f' % TPIMF)

      # Compute BPI_TPI_Compensation factor
      if DrvMargin > MARGIN_LIMIT:
         if mean(NormalizedTPICap) - 1.0 > MIN_CAP_LIMIT and mean(NormalizedBPICap) - 1.0 > MIN_CAP_LIMIT:
            BPITPICompFactor = 0.0
         else:
            Delta = abs(mean(NormalizedTPICap) - mean(NormalizedBPICap))
            if Delta == 0.0:
               Delta = 0.001
            if mean(NormalizedTPICap) > mean(NormalizedBPICap):
               BPITPICompFactor = (MIN_CAP_LIMIT - (mean(NormalizedBPICap) - 1.0))/((1.0 - TPIMF) * Delta)
            else:
               BPITPICompFactor = (MIN_CAP_LIMIT - (mean(NormalizedTPICap) - 1.0))/(TPIMF * Delta)
            if BPITPICompFactor < 0.0:
               BPITPICompFactor = 0.0
            if BPITPICompFactor > self.settings['BPITPICompensationFactor']:
               BPITPICompFactor = self.settings['BPITPICompensationFactor']
            #objMsg.printMsg('Normalized TPIC BPIC Delta = %.4f' % Delta)
      else:
         BPITPICompFactor = self.settings['BPITPICompensationFactor']

      # Compute TPI_Compensation factor
      MinTPICap = min(NormalizedTPICap)
      if (MinTPICap - 1.0) > MIN_CAP_LIMIT:
         if (MinTPICap - 1.0) > MARGIN_LIMIT:
            TPICompFactor = 0.0
         else:
            TPICompFactor = ((MARGIN_LIMIT - (MinTPICap - 1.0)) * self.settings['TPICompensationFactor']) / (MARGIN_LIMIT - MIN_CAP_LIMIT)
      else:
         TPICompFactor = self.settings['TPICompensationFactor']

      # Compute BPI_Compensation factor
      MinBPICap = min(NormalizedBPICap)
      if (MinBPICap - 1.0) > MIN_CAP_LIMIT:
         if (MinBPICap - 1.0) > MARGIN_LIMIT:
            BPICompFactor = 0.0
         else:
            BPICompFactor = ((MARGIN_LIMIT - (MinBPICap - 1.0)) * self.settings['BPICompensationFactor'])/(MARGIN_LIMIT-MIN_CAP_LIMIT)
      else:
         BPICompFactor = self.settings['BPICompensationFactor']

      # Report Compensation factors
      objMsg.printMsg('BPITPICompFactor = %.4f, MinTPICap = %.4f, TPICompFactor = %.4f, MinBPICap = %.4f, BPICompFactor = %.4f' %
                       (BPITPICompFactor,MinTPICap,TPICompFactor,MinBPICap,BPICompFactor))

      # Calculate Adjusted Capabilities
      adjustedBPICap = {}
      adjustedTPICap = {}
      objMsg.printMsg('=' * 49)
      objMsg.printMsg('%2s%8s%11s%8s%11s' % ('Hd','BPICap','AdjBPICap','TPICap','AdjTPICap'))
      objMsg.printMsg('=' * 49)
      for hd in xrange(self.numHeads):
         adjustedTPICap[hd] = ((TPICap[hd]- mean(TPICap))*TPICompFactor) + mean(TPICap)
         adjustedBPICap[hd] = ((BPICap[hd]- mean(BPICap))*BPICompFactor) + mean(BPICap)
         adjustedBPITPIDelta= (adjustedBPICap[hd]-adjustedTPICap[hd]) * (1.0-BPITPICompFactor) / 2.0
         adjustedTPICap[hd] += adjustedBPITPIDelta
         adjustedBPICap[hd] -= adjustedBPITPIDelta
         objMsg.printMsg('%2d%8.4f%9.4f%10.4f%9.4f' % (hd, BPICap[hd], adjustedBPICap[hd], TPICap[hd], adjustedTPICap[hd]))
      objMsg.printMsg('=' * 49)

      # Compute density
      density = mean([adjustedTPICap[hd] * adjustedBPICap[hd] for hd in range(self.numHeads)])
      objMsg.printMsg('Adj density: %6.4f' % density)

      # Calculate TPI margin
      totalMargin = (density / self.capacityTarget) - 1.0
      objMsg.printMsg('Total Margin: %6.4f' % totalMargin)
      R = 1/TPIMF - 1.0 # R = ratio of BPI margin to TPI margin
      TPIMargin = (math.sqrt((1+R)*(1+R)+4*R*totalMargin)-(1+R))/(2*R)
      if TPIMargin < 0.0:
         TPIMargin = R * TPIMargin
      objMsg.printMsg('TPI Margin: %6.4f' % TPIMargin)

      # Calculate BPI Margin
      if TPIMargin > 0.0:
         BPIMargin = R*(TPIMargin)
      else:
         BPIMargin = (TPIMargin)/R
      objMsg.printMsg('BPI Margin: %6.4f' % BPIMargin)

      # Initialize the margin targets
      if testSwitch.VBAR_ADP_EQUAL_ADC: #self.dut.nextState in ['VBAR_WP1','VBAR_WP1_A','VBAR_WP1_B','VBAR_WP1_C','VBAR_QUICK_TPI','VBAR_QUICK_TPI_A','VBAR_QUICK_TPI_B','VBAR_QUICK_TPI_C']:
         self.store['BpiMarginTarget'] = array('f', [0.0]*self.numUserZones*self.numHeads)
         self.store['TpiMarginTarget'] = array('f', [0.0]*self.numUserZones*self.numHeads)
      else:
         for hd in xrange(self.numHeads):
            for zn in xrange(self.numUserZones):
               self.setRecord('BpiMarginTarget', BPIMargin + self.settings['BpiTargetMarginAdjustment'][zn], hd, zn)
               self.setRecord('TpiMarginTarget', TPIMargin + self.settings['TpiTargetMarginAdjustment'][zn], hd, zn)

      if testSwitch.ADAPTIVE_GUARD_BAND:
         maxSectorsPerTrack = []
         maxTracksPerZone = []
         MaxZnCapacity = []
         minZ0Cap = 0
         minCapHd = 0
         Maxz0Capacity = 0
         Maxz1tolastZNCapacity = 0
         
         #=== Print table header: Calc max capacity table
         objMsg.printMsg('\n')
         objMsg.printMsg('CALCULATE MAX CAPACITY Based on stressed Bpi & Tpi format:')
         objMsg.printMsg('=' * 100)
         objMsg.printMsg("%2s  %2s  %9s  %9s  %18s  %18s  %18s  %6s  %6s" %("Hd", "Zn", "adjBpi", "adjTpi", "maxSectorsPerTrack", "maxTracksPerZone", "MaxZnCapacity","bpifmt","tpifmt" ))
         objMsg.printMsg('=' * 100)
         
         #=== Calc max capacity table
         for hd in xrange(self.numHeads):
            for zn in xrange(self.numUserZones):
               pickerData = CVbarDataHelper(self, hd, zn)
               # calculate the number of sectors per zon
               # adjbpic:
               if testSwitch.BPICHMS or testSwitch.FE_CONSOLIDATED_BPI_MARGIN:
                  bpic = pickerData['BpiCapability']-(self.settings['BPIMarginThreshold'][hd][zn]+self.dut.BPIMarginThresholdAdjust[hd])
               else:
                  bpic = pickerData['BpiCapability']-(self.settings['BPIMarginThreshold'][zn]+self.dut.BPIMarginThresholdAdjust[hd])
               # adjtpic:
               #tpic = self.data[hd][zn]['TpiCapability'] - (self.settings['TPIMarginThreshold'][zn] + self.dut.TPIMarginThresholdAdjust[hd])
               if testSwitch.RUN_ATI_IN_VBAR:
                  tpic = pickerData['TpiCapability']-pickerData['TpiMarginThresScale']
               else:
                  tpic = pickerData['TpiCapability']-self.settings['TPIMarginThreshold'][zn]
               bpiFormat = self.getClosestBPITable(bpic,zn,hd)
               tpiFormat = self.getClosestTPITable(tpic)
               temp3 = self.bpiFile.getSectorsPerTrack(bpiFormat,zn,hd)
               temp4 = (self.bpiFile.getNominalTracksPerSerpent()+tpiFormat)*self.bpiFile.getNumSerpentsInZone(self.baseformat[hd],zn,hd)
               maxSectorsPerTrack.append(temp3)
               maxTracksPerZone.append(temp4)
               temp5 = temp3*temp4*self.settings['PBA_TO_LBA_SCALER']*self.sectorsize/float(1e9)
               MaxZnCapacity.append(temp5)
               #=== Print table content: Calc max capacity table
               objMsg.printMsg("%2d  %2d  %9.4f  %9.4f  %18.4f  %18.4f  %18.4f  %6d  %6d" %(hd, zn, bpic, tpic, temp3, temp4, temp5, bpiFormat, tpiFormat))
               
               if zn == 0:
                  if minZ0Cap == 0:
                     minZ0Cap = temp5
                     minCapHd = hd
                  else:
                     if temp5 < minZ0Cap:
                        minZ0Cap = temp5
                        minCapHd = hd
                  Maxz0Capacity += temp5
               else:
                  Maxz1tolastZNCapacity += temp5
         MaxDriveCapacity = sum(MaxZnCapacity)
         objMsg.printMsg("MaxDriveCapacity = %.3f" % MaxDriveCapacity)
         objMsg.printMsg("Maxz1tolastZNCapacity = %.3f" % Maxz1tolastZNCapacity)
         objMsg.printMsg("Maxz0Capacity = %.3f" % Maxz0Capacity)
         objMsg.printMsg("minZ0Cap = %.3f" % minZ0Cap)
         objMsg.printMsg("minCapHd = %d" % minCapHd)
         maxCapDensity = MaxDriveCapacity / float(TP.VbarCapacityGBPerHead) / float(self.numHeads)
         objMsg.printMsg("maxCapDensity [z0 to LastUsrZn] = %.3f" % maxCapDensity)

         znCapacity = []
         sectorsPerTrack = []
         TracksPerZone = []
         z1tolastZNCapacity = 0
         z0Cap = 0
         z0MinHd = 0
         z0Capacity = 0
         z0sectorsPerTrack = 0
         
         objMsg.printMsg('\nCALCULATE CAPACITY Based on BPIC & TPIC format:')
         objMsg.printMsg('=' * 100)
         objMsg.printMsg("%2s  %2s  %8s  %8s  %18s  %18s  %18s" %("Hd", "Zn", "BpiC", "TpiC", "sectorsPerTrack", "TracksPerZone", "znCapacity", ))
         objMsg.printMsg('=' * 100)               
         for hd in xrange(self.numHeads):
            for zn in xrange(self.numUserZones):
               pickerData = CVbarDataHelper(self, hd, zn)
               # calculate the number of sectors per zon
               # bpic:
               bpic = pickerData['BpiCapability']-(self.dut.BPIMarginThresholdAdjust[hd])
               # tpic:
               tpic = pickerData['TpiCapability']-(self.dut.TPIMarginThresholdAdjust[hd])
               bpiFormat = self.getClosestBPITable(bpic,zn,hd)
               tpiFormat = self.getClosestTPITable(tpic)
               temp3 = self.bpiFile.getSectorsPerTrack(bpiFormat,zn,hd)
               temp4 = (self.bpiFile.getNominalTracksPerSerpent()+tpiFormat)*self.bpiFile.getNumSerpentsInZone(self.baseformat[hd],zn,hd)
               sectorsPerTrack.append(temp3)
               TracksPerZone.append(temp4)
               temp5 = temp3*temp4*self.settings['PBA_TO_LBA_SCALER']*self.sectorsize/float(1e9)
               znCapacity.append(temp5)
               #=== Print table content: Calc max capacity table
               objMsg.printMsg("%2d  %2d  %8.4f  %8.4f  %18.4f  %18.4f  %18.4f  " %(hd, zn, bpic, tpic, temp3, temp4, temp5))
               
               if (zn == 0):
                  if (z0Cap == 0):
                     z0Cap = temp5
                     z0MinHd = hd
                  else:
                     if temp5 < z0Cap:
                        z0Cap = temp5
                        z0MinHd = hd
                  z0Capacity += temp5
                  z0sectorsPerTrack += temp3
               else:
                  z1tolastZNCapacity += temp5
         driveCapacity = sum(znCapacity)
         objMsg.printMsg("driveCapacity = %.3f" % driveCapacity)
         objMsg.printMsg("z1tolastZNCapacity = %.3f" % z1tolastZNCapacity)
         objMsg.printMsg("z0Capacity = %.3f" % z0Capacity)
         objMsg.printMsg("z0sectorsPerTrack = %d" % z0sectorsPerTrack)
         objMsg.printMsg("z0Cap = %.3f" % z0Cap)
         objMsg.printMsg("z0MinHd = %d" % z0MinHd)
         self.maxDensity = driveCapacity / float(TP.VbarCapacityGBPerHead) / float(self.numHeads)
         objMsg.printMsg("self.maxDensity [z0 to LastUsrZn] = %.3f" % self.maxDensity)
         ####################################

         znCapacity = []
         sectorsPerTrack = []
         TracksPerZone = []
         Realz1tolastZNCapacity = 0
         checkCapFlag = 0
         
         # Increasing Density try to get the maxZn1~LastUsrZn Capacity
         objMsg.printMsg("Increasing Density try to get the maxZn1~LastUsrZn Capacity")
         #self.increaseDensity will modify both self.data[hd][zn]['BpiFormat'] and ['TpiFormat']
         #Save the original value and restore them back after trying to increase the capacity
         org_bpiformat = deepcopy(self.store['BpiFormat'])
         org_tpiformat = deepcopy(self.store['TpiFormat'])
         #pick initial TPI and BPI to get the format closer to target
         self.pickTPI()
         self.pickBPI()
         while self.getAvgDensity() < self.capacityTarget:
            if not self.increaseDensity('ANY'):
               objMsg.printMsg('*'*35 + ' AGB 1ST TWEAKING FAILED CAPACITY ' + '*'*35)
               break

         driveCapacity = self.agbDriveCapacity
         
         for hd in xrange(self.numHeads):
            for zn in xrange(self.numUserZones):
               pickerData = CVbarDataHelper(self, hd, zn)
               temp1 = self.bpiFile.getSectorsPerTrack(pickerData['BpiFormat'],zn,hd)
               sectorsPerTrack.append(temp1)
               temp2 = (self.bpiFile.getNominalTracksPerSerpent()+pickerData['TpiFormat'])*self.bpiFile.getNumSerpentsInZone(self.baseformat[hd],zn,hd)
               TracksPerZone.append(temp2)
               capacity = temp1*temp2*self.settings['PBA_TO_LBA_SCALER']*self.sectorsize/float(1e9)
               znCapacity.append(capacity)
               if (zn > 0):
                  Realz1tolastZNCapacity += capacity
         objMsg.printMsg("driveCapacity = %.3f" % driveCapacity)
         objMsg.printMsg("Realz1tolastZNCapacity = %.3f" % Realz1tolastZNCapacity)
         ##Restore back to original format
         ##Do not have to restore back the self.data[hd][zn]['BpiPick'] and ['TpiPick'] as they will be set accordingly by self.pickTpi and self.pickBpi
         self.store['BpiFormat'] = org_bpiformat
         self.store['TpiFormat'] = org_tpiformat

         if (Realz1tolastZNCapacity >= self.settings['DRIVE_CAPACITY']):
             # If Cap(Zn1 to LastUsrZn)>=500G
             # Zn0 does not exist.
             checkCapFlag = 3
             objMsg.printMsg("Z1-LastUsrZn meet min drive target cap -> Z0 does not exist. ")
         elif (Realz1tolastZNCapacity < self.settings['DRIVE_CAPACITY'] and MaxDriveCapacity >= self.settings['DRIVE_CAPACITY']):
             # Elseif Cap(Zn1 to LastUsrZn)<500G && maxCap(Zn1 to LastUsrZn)>=500G
             # CapMargin=maxCap(Zn1 to LastUsrZn)-Cap(Zn1 to LastUsrZn), make sure CapMargin<Cap(Zn0)
             # AGB_CapMargin = AGBMF * CapMargin
             # Zn0 track = AGB_CapMargin / SectorPerTrk from BPI_Format(Zn0)
             CapMargin = (self.settings['DRIVE_CAPACITY'] - Realz1tolastZNCapacity)
             objMsg.printMsg("CapMargin = %.3f" % CapMargin)
             if (CapMargin > z0Capacity):
                AGB_CapMargin = z0Capacity
             else:
                AGB_CapMargin = CapMargin
             objMsg.printMsg("AGB_CapMargin = %.3f" % AGB_CapMargin)
             checkCapFlag = 2 # calculate Z0 max tracks
             objMsg.printMsg("Z1-LastUsrZn < drive target cap but MaxCapZ1toLastUsrZn > min cap -> Z0 GB exists")
         elif (MaxDriveCapacity < self.settings['DRIVE_CAPACITY']):
             # Elseif maxCap(Zn1 to LastUsrZn)<500G
             checkCapFlag = 1 # waterfall
             objMsg.printMsg("MaxZ1-LastUsrZn < drive target cap -> waterfall")

         if (checkCapFlag == 1): #waterfall path.
             objMsg.printMsg('*'*40 + ' FAILED MINIMUM CAPABILITY ' + '*'*40)
             return ATPI_FAIL_CAPABILITY

         if (checkCapFlag == 2): #calculate Z0 max tracks
             z0MaxTracks = (AGB_CapMargin / (self.settings['PBA_TO_LBA_SCALER'] *self.sectorsize/float(1e9))) / z0sectorsPerTrack
             objMsg.printMsg('z0MaxTracks = %d'%z0MaxTracks)
             # Retrieve nominal serpent width from zone 0 maxTracksPerZone[0]:
             z0MiniZones = int(z0MaxTracks / self.bpiFile.getNominalTracksPerSerpent()) #TP.VbarNomSerpentWidth

             #self.z0FinalCapacity = self.settings['PBA_TO_LBA_SCALER'] * self.sectorsize * z0MaxTracks * z0sectorsPerTrack /float(1e9)
             self.z0FinalCapacity = AGB_CapMargin
             objMsg.printMsg('z0FinalCapacity = %.3f'%self.z0FinalCapacity)
             self.finalDriveCapacity = self.z0FinalCapacity + Realz1tolastZNCapacity
             objMsg.printMsg('finalDriveCapacity = z0FinalCapacity + Realz1tolastZNCapacity = %.3f'%self.finalDriveCapacity)

             # zone0 minizone = 0x19 = 25
             z0minizoneIndex = 25 - z0MiniZones
             objMsg.printMsg('Z0 MINIZONES = %d'%z0MiniZones)
             objMsg.printMsg("SAVE Z0 MINIZONES INDEX OF %d TO RAP entry 1D4" % (z0minizoneIndex))
             # 0x1D4 = 468 decimal -> 468 / 2 = 234 word offset:
             getVbarGlobalClass(CProcess).St({'test_num':178, 'CWORD1':0x0220, 'RAP_WORD':(234, z0minizoneIndex, 0xFFFF),'prm_name':'Update RAP Entry 1D4'})
             if verbose:
                getVbarGlobalClass(CProcess).St({'test_num':172, 'prm_name':'Display RAP', 'timeout':1800, 'CWORD1':0x9})

         if (checkCapFlag == 3): # Z0 is not present
             self.z0FinalCapacity = 0
             if verbose:
                objMsg.printMsg('self.z0FinalCapacity = %d'%self.z0FinalCapacity)
             self.finalDriveCapacity = self.z0FinalCapacity + driveCapacity
             objMsg.printMsg('self.finalDriveCapacity = %d'%self.finalDriveCapacity)

             # zone0 minizone = 0x19 = 25
             z0minizoneIndex = 25
             objMsg.printMsg('Z0 MINIZONES = 0')
             objMsg.printMsg("SAVE Z0 MINIZONES INDEX OF %d TO RAP entry 1D4" % (z0minizoneIndex))
             # 0x1D4 = 468 decimal -> 468 / 2 = 234 word offset:
             getVbarGlobalClass(CProcess).St({'test_num':178, 'CWORD1':0x0220, 'RAP_WORD':(234, z0minizoneIndex, 0xFFFF),'prm_name':'Update RAP Entry 1D4'})
             if verbose:
                getVbarGlobalClass(CProcess).St({'test_num':172, 'prm_name':'Display RAP', 'timeout':1800, 'CWORD1':0x9})
      ### end of testSwitch.ADAPTIVE_GUARD_BAND ###

      # Pick TPI for each head and zone and display the data
      if not testSwitch.FE_0171684_007867_DISPLAY_PICKER_AS_TBL:
         objMsg.printMsg('Initial Picks')
      self.pickTPI()
      self.pickBPI()
      if testSwitch.FE_0171684_007867_DISPLAY_PICKER_AS_TBL:
         # Display initial pick table
         self.displayCapability()

         objMsg.printMsg("PICKER LIMITS: capacityTarget = %1.4f, BPIMinAve = %1.4f, BPIMaxAve = %1.4f" % (self.capacityTarget,self.settings['BPIMinAvg'],self.settings['BPIMaxAvg']))
         objMsg.printMsg("OP_MODE -> 'C' = Capacity Adjust, 'P' = Performance Adjust, 'CP' = Capacity Adjust for Performance Constraints")

      # Tweak the format, BPI and TPI, to meet capacity and performance specifications.
      if not testSwitch.VBAR_ADP_EQUAL_ADC:

         # remove excess Capacity
         if testSwitch.FE_0171684_007867_DISPLAY_PICKER_AS_TBL:
            self.recordData['OP_MODE'] = 'C'               # Indicate adjustment being made for capacity reasons.
         else:
            objMsg.printMsg("Removing Excess Capacity")

         while (self.getAvgDensity() > self.capacityTarget) and self.decreaseDensity('ANY'):
            if testSwitch.FE_0171684_007867_DISPLAY_PICKER_AS_TBL:
               self.updatePickerFmtAdjustTbl()
            else:
               pass

         # Increase density to meet capacity
         if not testSwitch.FE_0171684_007867_DISPLAY_PICKER_AS_TBL:
            objMsg.printMsg("Increasing Density to meet Capacity")

      objMsg.printMsg('self.z0FinalCapacity = %d' % self.z0FinalCapacity)
      objMsg.printMsg('self.finalDriveCapacity = %d' % self.finalDriveCapacity)
      if not testSwitch.VBAR_ADP_EQUAL_ADC:
         while self.getAvgDensity() < self.capacityTarget:
            if verbose: objMsg.printMsg("getAvgDensity %s" % (self.getAvgDensity()))
            if not self.increaseDensity('ANY'):
               if (testSwitch.ADAPTIVE_GUARD_BAND and self.finalDriveCapacity >= self.settings['DRIVE_CAPACITY']):
                   break
               objMsg.printMsg('*'*40 + ' FAILED CAPACITY ' + '*'*40)
               return ATPI_FAIL_CAPACITY

            if testSwitch.FE_0171684_007867_DISPLAY_PICKER_AS_TBL:
               self.updatePickerFmtAdjustTbl()

         # Increase BPI if Performance isn't met
         if testSwitch.FE_0171684_007867_DISPLAY_PICKER_AS_TBL:
            self.recordData['OP_MODE'] = 'P'               # Indicate adjustment being made for performance reasons.
         else:
            objMsg.printMsg("Checking Performance: %f <= %f <= %f" % (self.settings['BPIMinAvg'],self.performance(),self.settings['BPIMaxAvg']))
         while self.performance() < self.settings['BPIMinAvg']:
            if not self.increaseDensity('BPI'):
               objMsg.printMsg('*'*40 + ' FAILED PERFORMANCE ' + '*'*40)
               return ATPI_FAIL_PERFORMANCE

            if testSwitch.FE_0171684_007867_DISPLAY_PICKER_AS_TBL:
               self.updatePickerFmtAdjustTbl()

         # Decrease BPI if average BPI is greater than max average allowed
         while self.performance() > self.settings['BPIMaxAvg']:
            if not self.decreaseDensity('BPI'):
               break

            if testSwitch.FE_0171684_007867_DISPLAY_PICKER_AS_TBL:
               self.updatePickerFmtAdjustTbl()

         # Increase TPI if average density less than target capacity
         if testSwitch.FE_0171684_007867_DISPLAY_PICKER_AS_TBL:
            self.recordData['OP_MODE'] = 'CP'               # Indicate adjustment being made for capacity reasons.
         while self.getAvgDensity() < self.capacityTarget:
            if not self.increaseDensity('TPI'):
               if (testSwitch.ADAPTIVE_GUARD_BAND and self.finalDriveCapacity >= self.settings['DRIVE_CAPACITY']):
                  break
               objMsg.printMsg('*'*27 + ' FAILED CAPACITY DUE TO PERFORMANCE MAX LIMIT ' + '*'*27)
               return ATPI_FAIL_PERFORMANCE

            if testSwitch.FE_0171684_007867_DISPLAY_PICKER_AS_TBL:
               self.updatePickerFmtAdjustTbl()

         # Decrease TPI (Remove excess TPI) until capacity is just met
         bDecreasedTPI = False
         while self.getAvgDensity() > self.capacityTarget:
            if not self.decreaseDensity('TPI'):
               if (testSwitch.ADAPTIVE_GUARD_BAND and self.finalDriveCapacity >= self.settings['DRIVE_CAPACITY']):
                  break
               break

            if testSwitch.FE_0171684_007867_DISPLAY_PICKER_AS_TBL:
               self.updatePickerFmtAdjustTbl()

         # Undo TPI change until capacity is met
         while self.getAvgDensity() < self.capacityTarget:
            if not self.increaseDensity('TPI'):
               if (testSwitch.ADAPTIVE_GUARD_BAND and self.finalDriveCapacity >= self.settings['DRIVE_CAPACITY']):
                  break
               objMsg.printMsg('*'*27 + ' FAILED CAPACITY DUE TO PERFORMANCE MAX LIMIT ' + '*'*27)
               return ATPI_FAIL_CAPACITY

            if testSwitch.FE_0171684_007867_DISPLAY_PICKER_AS_TBL:
               self.updatePickerFmtAdjustTbl()

         # Check imbalance heads
         if testSwitch.VBAR_CHECK_IMBALANCED_HEAD:
            objMsg.printMsg("Checking imbalanced head based on BPI zone 0s")
            if self.checkImbalancedHead() != ATPI_PASS:
               objMsg.printMsg('*'*40 + ' FAILED IMBALANCED HEAD ' + '*'*40)
               if ConfigVars[CN].get('EN_RESTART_WTF',0) == 1 :
                  if (self.settings['ForceRestartNextWtf'] == 1 or self.settings['RpmRestartNextWtf'] == 1):
                     objMsg.printMsg('*'*40 + ' WATERFALL - RESTART ' + '*'*40)
                     return ATPI_FORCE_RESTART
                  else:
                     return ATPI_FAIL_IMBALANCED_HEAD

         # Check OD & ID minimum thruput
         if testSwitch.VBAR_CHECK_MINIMUM_THRUPUT:
            objMsg.printMsg("Checking OD and ID minimum thruput")
            if self.checkMinimumThruput() != ATPI_PASS:
               objMsg.printMsg('*'*40 + ' FAILED MINIMUM THRUPUT ' + '*'*40)
               return ATPI_FAIL_MINIMUM_THRUPUT

      if testSwitch.FE_0171684_007867_DISPLAY_PICKER_AS_TBL:
         # Report the accumulated picker data.
         objMsg.printDblogBin(self.dut.dblData.Tables('P_VBAR_PICKER_FMT_ADJUST'), self.spcId)
         # Update the log with the final Picker results.
         self.reportPickerResults()
      else:
         objMsg.printMsg('Final Density: %6.4f' % self.getAvgDensity())

      #Force to update by head by zone the BPI config as the T176 need all zone SgateToRgate timing reload back to default
      if testSwitch.FORCE_UPDATE_BPI_ALL_HEADS_ALL_ZONES:
         if self.dut.currentState in ['VBAR_ZN','VBAR_MARGIN','VBAR_FMT_PICKER','TRIPLET_OPTI','TRIPLET_OPTI_V2','VBAR_FMT_PICKER']:
            self.store['AdjustedBpiFormat'] = array('c', ['T']*self.numUserZones*self.numHeads)
      
      self.sendFormatToDrive = True
      self.BpiFileCapacityCalc = False
      self.setFormat("BOTH")

      # Compute and optionally print the data to the log, based on log size reduction switch.
      self.computeMargins()

      if testSwitch.DISPLAY_SMR_FMT_SUMMARY:
         # All heads/zones have been processed.  Dump a summary of the format information for the drive.
         objMsg.printDblogBin(self.dut.dblData.Tables('P_SMR_FORMAT_SUMMARY'), self.spcId_SMR_FMT)

      self.updateSummaryByZone()
      self.updateSummaryByHead()

      self.SetWFT()

      # Write RAP and SAP data to flash
      getVbarGlobalClass(CProcess).St({'test_num': 178, 'prm_name': 'prm_wp_178', 'CWORD1':0x0620, 'timeout': 1200, 'spc_id': 0,})
      # Post final capacity to FIS
      getVbarGlobalClass(CProcess).St({'test_num':210,'CWORD1':8, 'SCALED_VAL': int(self.settings['PBA_TO_LBA_SCALER'] * 10000), 'spc_id':1})

      return ATPI_PASS

   #-------------------------------------------------------------------------------------------------------
   def reportPickerResults(self):

      if self.sectorsize == 4096:
         capacityGB = self.settings['DRIVE_CAPACITY_4K']
      else:
         capacityGB = self.settings['DRIVE_CAPACITY']

      self.dut.dblData.Tables('P_VBAR_PICKER_RESULTS').addRecord({
            'SPC_ID'            : self.spcId,
            'OCCURRENCE'        : self.recordData['OCCURRENCE'],
            'SEQ'               : self.dut.objSeq.getSeq(),
            'TEST_SEQ_EVENT'    : 1,
            'TARGET_CAPACITY'   : round(self.capacityTarget,4),
            'FINAL_DENSITY'     : round(self.getAvgDensity(),4),
            'TARGET_CAP_GB'     : round(capacityGB,4),
            'COMPUTED_CAP_GB'   : round(float(self.getDriveCapacity()),4),
            'MIN_BPI_AVE_LIMIT' : round(self.settings['BPIMinAvg'],2),
            'BPI_AVE'           : round(self.performance(),3),
            'MAX_BPI_AVE_LIMIT' : round(self.settings['BPIMaxAvg'],2)
           })
      if not testSwitch.CM_REDUCTION_REDUCE_PRINTDBLOGBIN:
         objMsg.printDblogBin(self.dut.dblData.Tables('P_VBAR_PICKER_RESULTS'), self.spcId)

   #-------------------------------------------------------------------------------------------------------
   def updatePickerFmtAdjustTbl(self):
      self.dut.dblData.Tables('P_VBAR_PICKER_FMT_ADJUST').addRecord({
            'SPC_ID'          : self.spcId,
            'OCCURRENCE'      : self.recordData['OCCURRENCE'],
            'SEQ'             : self.dut.objSeq.getSeq(),
            'TEST_SEQ_EVENT'  : 1,
            'COMPUTED_CAP_GB' : round(self.recordData['COMPUTED_CAP_GB'],4),
            'AVE_DENSITY'     : round(self.recordData['AVE_DENSITY'],4),
            'HD_PHYS_PSN'     : self.dut.LgcToPhysHdMap[self.recordData['LGC_HD']],
            'HD_LGC_PSN'      : self.recordData['LGC_HD'],
            'DATA_ZONE'       : self.recordData['ZONE'],
            'OP_MODE'         : self.recordData['OP_MODE'],
            'CAP_ADJUST'      : self.recordData['CAP_ADJUST'],
            'FMT_TYPE'        : self.recordData['FMT_TYPE'],
            'RELATIVE_PICK'   : round(self.recordData['RELATIVE_PICK'],4),
            'SELECTED_FORMAT' : self.recordData['SELECTED_FORMAT'],
            'BPI_AVE'         : round(self.performance(),4)
           })

   #-------------------------------------------------------------------------------------------------------
   def updateSummaryByZone(self):
      curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)

      spcId = self.spcIdHlpr.getSpcId('P_VBAR_FORMAT_SUMMARY')

      for hd in xrange(self.numHeads):
         for zn in xrange(self.numUserZones):
            pickerData = CVbarDataHelper(self, hd, zn)
            dblog_record = {
                     'SPC_ID'          : spcId,
                     'OCCURRENCE'      : occurrence,
                     'SEQ'             : curSeq,
                     'TEST_SEQ_EVENT'  : testSeqEvent,
                     'HD_PHYS_PSN'     : self.dut.LgcToPhysHdMap[hd],
                     'DATA_ZONE'       : zn,
                     'HD_LGC_PSN'      : hd,
                     'BPI_CAP'         : round(pickerData['BpiCapability'], 4),
                     'BPI_INTERPOLATED': pickerData['BpiInterpolated'],
                     'BPI_PICK'        : round(pickerData['BpiPick'], 4),
                     'BPI_MRGN'        : round(pickerData['BpiMargin'], 4),
                     'BPI_TABLE_NUM'   : pickerData['BpiFormat'],
                     'TPI_CAP'         : round(pickerData['TpiCapability'], 4),
                     'TPI_INTERPOLATED': pickerData['TpiInterpolated'],
                     'TPI_PICK'        : round(pickerData['TpiPick'], 4),
                     'TPI_MRGN'        : round(pickerData['TpiMargin'], 4),
                     'TPI_TABLE_NUM'   : pickerData['TpiFormat'],
                  }
            self.dut.dblData.Tables('P_VBAR_FORMAT_SUMMARY').addRecord(dblog_record)
            if testSwitch.FE_0164322_410674_RETRIEVE_P_VBAR_TABLE_AFTER_POWER_RECOVERY:
               self.dut.vbar_format_sum.append(dblog_record)


      objMsg.printDblogBin(self.dut.dblData.Tables('P_VBAR_FORMAT_SUMMARY'), spcId)

   #-------------------------------------------------------------------------------------------------------
   def updateSummaryByHead(self):
      curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
      spcId = self.spcIdHlpr.getSpcId('P_VBAR_FORMAT_SUMMARY')  # Share a common spc_id

      #define each attribute name and value.
      if testSwitch.FE_0166720_407749_P_SENDING_ATTR_BPI_TPI_INFO_FOR_ADG_DISPOSE:
         bpi_cap_min = []
         bpi_cap_avg = []
         tpi_cap_min = []
         tpi_cap_avg = []

      for hd in xrange(self.numHeads):
         BpiCap    = self.getRecordForHead('BpiCapability',hd)
         TpiCap    = self.getRecordForHead('TpiCapability',hd)
         BpiMargin = self.getRecordForHead('BpiMargin',hd)
         TpiMargin = self.getRecordForHead('TpiMargin',hd)

         self.dut.dblData.Tables('P_VBAR_CAP_SUMMARY_BY_HD').addRecord(
            {
                     'SPC_ID'          : spcId,
                     'OCCURRENCE'      : occurrence,
                     'SEQ'             : curSeq,
                     'TEST_SEQ_EVENT'  : testSeqEvent,
                     'HD_PHYS_PSN'     : self.dut.LgcToPhysHdMap[hd],
                     'HD_LGC_PSN'      : hd,
                     'BPI_CAP_AVG'     : round(mean(BpiCap), 4),
                     'BPI_CAP_MIN'     : round(min(BpiCap), 4),
                     'BPI_MRGN_AVG'    : round(mean(BpiMargin), 4),
                     'BPI_MRGN_MIN'    : round(min(BpiMargin), 4),
                     'VZB_TABLE'       : self.baseformat[hd],
                     'TPI_CAP_AVG'     : round(mean(TpiCap), 4),
                     'TPI_CAP_MIN'     : round(min(TpiCap), 4),
                     'TPI_MRGN_AVG'    : round(mean(TpiMargin), 4),
                     'TPI_MRGN_MIN'    : round(min(TpiMargin), 4),
            })

         #keep values by head into each attribute
         if testSwitch.FE_0166720_407749_P_SENDING_ATTR_BPI_TPI_INFO_FOR_ADG_DISPOSE:
            bpi_cap_min.append(int(round(min(BpiCap), 4)*100))
            bpi_cap_avg.append(int(round(mean(BpiCap), 4)*100))
            tpi_cap_min.append(int(round(min(TpiCap), 4)*100))
            tpi_cap_avg.append(int(round(mean(TpiCap), 4)*100))

      # update attribute name and value to FIS.
      if testSwitch.FE_0166720_407749_P_SENDING_ATTR_BPI_TPI_INFO_FOR_ADG_DISPOSE and self.dut.nextState in ['VBAR_WP1']:
         self.dut.driveattr['BPI_CAP_MIN'] = bpi_cap_min
         self.dut.driveattr['BPI_CAP_AVG'] = bpi_cap_avg
         self.dut.driveattr['TPI_CAP_MIN'] = tpi_cap_min
         self.dut.driveattr['TPI_CAP_AVG'] = tpi_cap_avg

   #-------------------------------------------------------------------------------------------------------
   def SetWFT(self):
      if not testSwitch.RUN_VWFT_SUPPORT:
         return
      objMsg.printMsg('VWFT_SUPPORT')

      VWFT_SLOPE = self.settings['VWFT_SLOPE']
      VWFT_ADJUSTMENT_CRITERIA = self.settings['VWFT_ADJUSTMENT_CRITERIA']
      VWFT_MAX_ALLOWED_ADJUSTMENT = self.settings['VWFT_MAX_ALLOWED_ADJUSTMENT']
      VWFT_MIN_ALLOWED_OCLIM = self.settings['VWFT_MIN_ALLOWED_OCLIM']

      writeOCLIMAddress_11 = {
         'test_num'        :11,
         'prm_name'        :'writeOCLIMAddress_11',
         'timeout'         :1000,
         'spc_id'          :1,
         'CWORD1'          :(0x0800),           # Modify a specific head using a sym offset
         'SYM_OFFSET'      :(42),
         'MASK_VALUE'      :(0x0000),           # Bit mask of heads to modify: will be overloaded
         'WR_DATA'         : int(TP.defaultOCLIM*4096/100),   # OCLIM to write
         }

      RdWrHeadXThreshAdjust = [0.0] * self.numHeads
      minTpiMargin = [min(self.getRecordForHead('TpiMargin',hd)) for hd in xrange(self.numHeads)]
      for hd in xrange(self.numHeads):
         if minTpiMargin[hd] < VWFT_ADJUSTMENT_CRITERIA:
            RdWrHeadXThreshAdjust[hd] = (minTpiMargin[hd] - VWFT_ADJUSTMENT_CRITERIA) * VWFT_SLOPE
            if RdWrHeadXThreshAdjust[hd] < VWFT_MAX_ALLOWED_ADJUSTMENT:     # it seems backward, but it is defined as negative
               RdWrHeadXThreshAdjust[hd] = VWFT_MAX_ALLOWED_ADJUSTMENT
               objMsg.printMsg('MAX_ADJUSTMENT TRIGGERED -- Adjustment limited to %.1f%%' % VWFT_MAX_ALLOWED_ADJUSTMENT)
         adjustedOCLIM = TP.defaultOCLIM + RdWrHeadXThreshAdjust[hd]
         if adjustedOCLIM < VWFT_MIN_ALLOWED_OCLIM:
            adjustedOCLIM = VWFT_MIN_ALLOWED_OCLIM
            objMsg.printMsg('MIN OCLIM LIMIT TRIGGERED -- OCLIM limited to %.1f%%' % adjustedOCLIM)
         objMsg.printMsg('Requested adjustment = %.2f Final OCLIM = %.2f%% of track' % (RdWrHeadXThreshAdjust[hd], adjustedOCLIM))

         writeOCLIMAddress_11.update({'WR_DATA' : int(round(adjustedOCLIM*4096/100)), # convert from pct of track to servo dac
                                      'MASK_VALUE' : 1 << hd })                       # update the mask with the head to change

         getVbarGlobalClass(CProcess).St(writeOCLIMAddress_11)
         curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
         spcId = self.spcIdHlpr.getSpcId('P_VBAR_FORMAT_SUMMARY')  # Share a common spc_id
         self.dut.dblData.Tables('P_VBAR_WRT_FAULT_SUMMARY').addRecord({
               'SPC_ID'              :  spcId,
               'OCCURRENCE'          :  occurrence,
               'SEQ'                 :  curSeq,
               'TEST_SEQ_EVENT'      :  testSeqEvent,
               'HD_PHYS_PSN'         :  self.dut.LgcToPhysHdMap[hd],
               'HD_LGC_PSN'          :  hd,
               'TPI_MRGN_MIN'        :  round(minTpiMargin[hd], 4),
               'WRT_FAULT_ADJUSTMENT':  RdWrHeadXThreshAdjust[hd],
               'WRT_FAULT_FINAL'     :  adjustedOCLIM
               })

      objMsg.printDblogBin(self.dut.dblData.Tables('P_VBAR_WRT_FAULT_SUMMARY'), spcId)

   #-------------------------------------------------------------------------------------------------------
   def getClosestTPITable(self, capability):
      """
      Calculate the closest TPI table based on the given
      TPI percentage (ie 1.0000 is nominal)
      """
      return int(round((capability - 1.0000) / self.TPI_STEP_SIZE))

   #-------------------------------------------------------------------------------------------------------
   def getClosestBPITable(self, capability, inZn = -1, inHd = 0):
      """
      Calculate the closest BPI table based on the given
      BPI percentage (ie 1.0000 is nominal)
      """
      # TODO: buffer BPINominal_Table?
      if not testSwitch.FE_0269922_348085_P_SIGMUND_IN_FACTORY:
         inHd = 0
      numUserZones = self.bpiFile.getNumUserZones()
      maxBpiProfiles = self.bpiFile.getNumBpiFormats()
      BPIMinFormat = self.bpiFile.getMinFormat()
      BPIMaxFormat = self.bpiFile.getMaxFormat()
      BPINominal_Table = list(list(list() for pf in xrange(maxBpiProfiles)) for hd in xrange(self.bpiFile.bpiNumHeads))

      # Calculate and fill-in 'BPINominal_Table' table with format freq ratios.
      for hd in xrange(self.bpiFile.bpiNumHeads):
         for idx, pf in enumerate(xrange(BPIMinFormat,BPIMaxFormat+1)):
            for zn in xrange(numUserZones):  # Including sys_zone
               nominalFrequency = self.bpiFile.getFrequencyByFormatAndZone(0,zn,hd)   # TODO: optimize this routine?
               ZnFormatFreq = self.bpiFile.getFrequencyByFormatAndZone(pf,zn,hd)
               FreqRatio = ZnFormatFreq/nominalFrequency
               BPINominal_Table[hd][idx].append(FreqRatio)

      # Get Equivalent Table
      for idx, pf in enumerate(xrange(BPIMinFormat,BPIMaxFormat+1)):
         if inZn == -1: # Zone not specified, get average of All Zones
            BPIZn = mean(BPINominal_Table[inHd][idx])
         else:
            BPIZn = float(BPINominal_Table[inHd][idx][inZn])
         if BPIZn > capability:
            return pf
      else:
         return BPIMaxFormat

   #-------------------------------------------------------------------------------------------------------
   def checkImbalancedHead(self):
      BpiPicks=[self.getRecord('BpiPick',hd,0) for hd in xrange(self.numHeads)]
      BpiPicks.sort()
      objMsg.printMsg('BPI_Z0s: %s' %BpiPicks)
      delta = BpiPicks[-1] - BpiPicks[0]
      objMsg.printMsg('Delta %.4f, limit %.4fd' %(delta, TP.ImbalancedHeadLimit))
      if delta > TP.ImbalancedHeadLimit:
         objMsg.printMsg('Imbalanced Head: FAIL!')
         return ATPI_FAIL_IMBALANCED_HEAD
      objMsg.printMsg('Imbalanced Head: PASS!')
      return ATPI_PASS

   #-------------------------------------------------------------------------------------------------------
   def checkMinimumThruput(self):
      objMsg.printMsg ("checkMinimumThruput: hasSectorPerTrackInfo=%s" % self.bpiFile.hasSectorPerTrackInfo())
      if self.bpiFile.hasSectorPerTrackInfo():
         # Calculate OD thruput
         if testSwitch.ADAPTIVE_GUARD_BAND:
            secPerTrack = [self.bpiFile.getSectorsPerTrack(self.getRecord('BpiFormat',hd,1),1,hd) for hd in xrange(self.numHeads)]
         else:
            secPerTrack = [self.bpiFile.getSectorsPerTrack(self.getRecord('BpiFormat',hd,0),0,hd) for hd in xrange(self.numHeads)]
         aveSecPerTrack = sum(secPerTrack)/float(self.numHeads)
         thruputOD = self.calcThruput(aveSecPerTrack)
         objMsg.printMsg('OD Thruput = %.2f, Limit %.2f, aveSecPerTrack %.2f' %(thruputOD, self.settings['OD_THRUPUT_LIMIT'], aveSecPerTrack))

         # Calculate ID thruput
         secPerTrack = [self.bpiFile.getSectorsPerTrack(self.getRecord('BpiFormat',hd,self.numUserZones-1),self.numUserZones-1,hd) for hd in xrange(self.numHeads)]
         aveSecPerTrack = sum(secPerTrack)/float(self.numHeads)
         thruputID = self.calcThruput(aveSecPerTrack)
         objMsg.printMsg('ID Thruput = %.2f, Limit %.2f, aveSecPerTrack %.2f' %(thruputID, self.settings['ID_THRUPUT_LIMIT'], aveSecPerTrack))

         # Check OD thruput
         if thruputOD < self.settings['OD_THRUPUT_LIMIT']:
            objMsg.printMsg('Minimum OD Thruput: FAIL!')
            return ATPI_FAIL_MINIMUM_THRUPUT
         objMsg.printMsg('Minimum OD Thruput: PASS!')

         # Check ID thruput
         if thruputID < self.settings['ID_THRUPUT_LIMIT']:
            objMsg.printMsg('Minimum ID Thruput: FAIL!')
            return ATPI_FAIL_MINIMUM_THRUPUT
         objMsg.printMsg('Minimum ID Thruput: PASS!')
         return ATPI_PASS
      else:
         objMsg.printMsg('Skip Minimum Thruput Checking!')
         return ATPI_PASS

   #-------------------------------------------------------------------------------------------------------
   def calcThruput(self, secPerTrack):
      if testSwitch.virtualRun:
         self.dut.servoWedges = 256

      cylSkew = 0x22     # for 256 servo wedge HDA
      a = int(self.dut.rpmCategory) / 60.0
      b = float(cylSkew + self.dut.servoWedges) / self.dut.servoWedges
      c = a / b
      thruput = secPerTrack * self.bpiFile.sectorSizes[0] * round(c,1)
      thruput = thruput / 1e6

      return thruput

   #----------------------------------------------------------------------------------------------------------
   #function to print debug message about all hd, zn information
   def debug_values(self, attributes_dict):
      unsupported_attr = []
      tmpStr = ""
      for hd, zn in [(hd, zn) for hd in range(self.numHeads) for zn in range(self.numUserZones)]:
         tmpStr += "%d, %d, " % (hd, zn)
         for attribute in attributes_dict:
            if attribute == "SectorsPerTrack":
               tmpStr += "%d, " %(self.bpiFile.getSectorsPerTrack(self.getRecord('BpiFormat',hd,zn),zn,hd))
            else:
               try:
                  tmpStr += "%f, " % (self.getRecord(attribute,hd,zn))
               except:
                  if attribute not in unsupported_attr:
                     unsupported_attr.append(attribute)               
         tmpStr += "\n"
      title = "=" * 30  #create title
      title += "\nhd, zn, "
      title += ', '.join(set(attributes_dict) - set(unsupported_attr))
      title += "\n"
      tmpStr = title + tmpStr
      objMsg.printMsg("%s" % tmpStr)
      objMsg.printMsg("%s" % "=" * 30)
      if unsupported_attr : #print out the unsupported attributes
         objMsg.printMsg("unsupported attribute : %s\n" % str(unsupported_attr))

   #----------------------------------------------------------------------------------------------------------
   def syncZoneServoBoundary(self):
      getVbarGlobalClass(CProcess).St(TP.PRM_DISPLAY_ZONED_SERVO_CONFIG_TABLE_172)
      getVbarGlobalClass(CProcess).St(TP.PRM_SYNC_ZONE_BOUNDARY_73)
      getVbarGlobalClass(CProcess).St(TP.PRM_DISPLAY_ZONED_SERVO_CONFIG_TABLE_172)

###########################################################################################################
###########################################################################################################
class CMarginPicker(CPicker):
   def pickBPITPI(self):
      """Pick to margin requirements instead of capacity"""

      # -------------------------------------------------------------------------------------
      if not testSwitch.FE_0115422_340210_FORMATS_BY_MARGIN:
      # -------------------------------------------------------------------------------------
         objMsg.printMsg('*'* 30 + ' CONSTANT MARGIN FORMAT PICKER ' + '*'*30)

         # Initialize the margin targets -> Acheive these margin targets if you can.
         self.store['TpiMarginTarget'] = array('f', [float(TP.VTPIConstantMarginTarget)]*self.numUserZones*self.numHeads)

         # Pick for each head and zone and display the data
         objMsg.printMsg('Initial Picks')
         self.pickTPI()   # Step through TPI settings, (heads/zones), till we get as close as possible to the TpiMarginTarget.
         self.pickBPI()   # Step through BPI settings, (heads/zones), till we get as close as possible to the BpiMarginTarget. (BPI will not change here)

         objMsg.printMsg('Final Density: %6.4f' % self.getAvgDensity())

         self.sendFormatToDrive = True
         self.BpiFileCapacityCalc = False

         #Force to update by head by zone the BPI config as the T176 need all zone SgateToRgate timing reload back to default
         if testSwitch.FORCE_UPDATE_BPI_ALL_HEADS_ALL_ZONES:
            self.store['AdjustedBpiFormat'] = array('c', ['T']*self.numUserZones*self.numHeads)

         self.setFormat("BOTH")

         # Compute and optionally print the data to the log, based on log size reduction switch.
         self.computeMargins()

         self.updateSummaryByZone()
         self.updateSummaryByHead()

         # Set the write fault threshold based on the new format.
         self.SetWFT()

         # Write RAP and SAP data to flash
         getVbarGlobalClass(CProcess).St({'test_num': 178, 'prm_name': 'prm_wp_178', 'CWORD1':0x0620, 'timeout': 1200, 'spc_id': 0,})

         # Post final capacity to FIS
         getVbarGlobalClass(CProcess).St({'test_num':210,'CWORD1':8, 'SCALED_VAL': int(self.settings['PBA_TO_LBA_SCALER'] * 10000), 'spc_id':1})

      # -------------------------------------------------------------------------------------
      else:
      # -------------------------------------------------------------------------------------
         # testSwitch.FE_0115422_340210_FORMATS_BY_MARGIN = True (Old Margining Code which likely no longer works)
         prm_210 = {'test_num': 210,
              'prm_name': 'Update Formats To Drive',
              'timeout' : 1800,
              'spc_id'  : 0,
              }
         if not testSwitch.FE_0269922_348085_P_SIGMUND_IN_FACTORY:
            prm.update({
               'dlfile'   : (CN,self.bpiFile.bpiFileName),
               })

         BPIMinFormat = self.bpiFile.getMinFormat()
         maxBpiProfiles = self.bpiFile.getNumBpiFormats()
         for hd in xrange(self.numHeads):
            for zn in xrange(self.numUserZones):
               zfi = CVbarDataHelper(self, hd, zn)
               closest_bpi = 100
               closest_tpi = 100
               bpi_margin_diff = list(0 for fmt in xrange(maxBpiProfiles))
               tpi_margin_diff = list(0 for fmt in xrange(maxBpiProfiles))
               for idx in xrange(maxBpiProfiles):
                  format = idx+BPIMinFormat
                  marginChangeFromNominal = self.marginChangeFromNominal[getBpiHeadIndex(hd)][zn][idx]
                  projected_bpi_margin    = zfi['BpiCapability'] - marginChangeFromNominal
                  bpi_margin_diff[idx]    = (projected_bpi_margin - self.settings['BPI_MARGIN_TARGET'][zn])
                  if bpi_margin_diff[idx] > 0 and bpi_margin_diff[idx] < closest_bpi:
                     zfi['BpiPick']    = marginChangeFromNominal
                     zfi['BpiFormat']  = format
                  projected_tpi_margin    = zfi['TpiCapability'] - (1.0 + format * self.TPI_STEP_SIZE)
                  tpi_margin_diff[idx]    = (projected_tpi_margin - self.settings['TPI_MARGIN_TARGET'][zn])
                  if tpi_margin_diff[idx] > 0 and tpi_margin_diff[idx] < closest_tpi:
                     zfi['TpiPick']    = 1.0 + format * self.TPI_STEP_SIZE
                     zfi['TpiFormat']  = format
                  
         self.baseformat = [self.selectMostCommonFormat(hd,'BPI') for hd in xrange(self.numHeads)]

         for zn in xrange(self.numUserZones):
            zfi = CVbarDataHelper(self, hd, zn)
            prm_210['ZONE'] = zn*256 + zn
            prm_210['HEAD_RANGE'] = 0xFF
            tpigroup=[0]*T210_PARM_NUM_HEADS
            bpigroup=[0]*T210_PARM_NUM_HEADS
            for hd in xrange(self.numHeads):
               bpigroup[hd] = zfi['BpiFormat'] +  self.bpiFile.getNominalFormat()
               tpigroup[hd] = zfi['TpiFormat'] + self.bpiFile.getNominalTracksPerSerpent()
            prm_210['BPI_GROUP_EXT'] = bpigroup
            prm_210['TPI_GROUP_EXT'] = tpigroup
            prm_210['CWORD1'] = 0x301
            getVbarGlobalClass(CProcess).St(prm_210)
            prm_210['CWORD1'] = 0x302
            getVbarGlobalClass(CProcess).St(prm_210)

         prm = {'test_num': 178, 'prm_name': 'prm_wp_178', 'timeout': 1200, 'spc_id': 0,}
         prm.update({'CWORD1':0x0620}) # write RAP and SAP data to flash
         getVbarGlobalClass(CProcess).St(prm)

      # -------------------------------------------------------------------------------------

      return ATPI_PASS


###########################################################################################################
###########################################################################################################
class CDesperadoPicker(CPicker):
   """
      This class is responsible for picking the appropriate BPI/TPI capability picks based on
      measured capabilities and specified margins. The algorithm is implemented as per Bruce Emo's
      specification.
   """
   #def __init__(self, niblet, measurements, limits, active_zones=[]):
   def __init__(self, niblet, measurements, limits, SendVbarFmtSummaryToEDW=True, active_zones=[]):

      # Initialize many of the class variables by calling the parent class initialization routine.
      CPicker.__init__(self, niblet, measurements, limits, active_zones = [])

      self.validateSF3Support()

      self.updateSqueezeMicrojog = limits.get('UPDATE_SQUEEZE_MICROJOG',0)
      self.updateShingleDirection = limits.get('UPDATE_SHINGLE_DIRECTION',0)

      self.SmrOccurrence = 0
      self.use_OTC_Rd_Offset  = limits.get('RD_OFST', 0)
      self.spc_id_banded_tpi  = limits.get('SPC_ID_BANDED_TPI', 1)
      # to control the banded tpi table insertion and printing
      self.dumpBandedTPITable = limits.get('DUMP_BANDED_TPI_TBL', 0)
      # to control the Max format summary table insertion and printing
      self.dumpMaxFormatSummaryTBL = limits.get('DUMP_MAX_FORMAT_SUMMARY_TBL', 1)
      if testSwitch.DISPLAY_SMR_FMT_SUMMARY:
         self.spcId_SMR_FMT = self.spcIdHlpr.incrementSpcId('P_SMR_FORMAT_SUMMARY')
         
      data = {
         'TpiCapabilityMax'      : ('f',  0.0   ), 
         'TpiCapabilitySSS'      : ('f',  1.0   ), 
         'TpiCapabilityDSS'      : ('f',  1.0   ), 
         'ShingleDirection'      : ('H',  SHINGLE_DIRECTION_OD_TO_ID), 
         'ReadOffset'            : ('i',  0     ), 
         'NumBands'              : ('i',  1     ), 
      }
      if testSwitch.FE_0293889_348429_VBAR_MARGIN_BY_OTCTP:
         data.update({
            'TpiM_SSS'           : ('f',  0.0   ),    # to be filled in by calculateBandedTPI
            'TpiM_DSS'           : ('f',  0.0   ),    # to be filled in by calculateBandedTPI
         })
      self.addItems(data)
         
      for hd in xrange(self.numHeads):
         for zn in xrange(self.numUserZones):
            meas = self.measurements.getNibletizedRecord(hd, zn)
            if meas['TPIPickEffective'] >= 0.0:
               pickerData  = CVbarDataHelper(self, hd, zn)
               tpiPick     = meas['TPIPickEffective']
               tpiFormat   = int(round(meas['TPIFmtEffective'])) # TODO: is tpiFormat integer?
               pickerData['TpiMargin']       = meas['TPI'] - tpiPick
               pickerData['TpiPick']         = tpiPick
               pickerData['TpiPickInitial']  = tpiPick
               pickerData['TpiFormat']       = tpiFormat

      self.initializeTpiStepSizeArray()

      self.calculateBandedTPI(measurements)


   #----------------------------------------------------------------------------------------------------------
   def validateSF3Support(self):
      if not testSwitch.extern.FE_0158806_007867_T210_TPI_SMR_SUPPORT:
         raiseException(11044, "CDesperadoPicker requires FE_0158806_007867_T210_TPI_SMR_SUPPORT")
   #-------------------------------------------------------------------------------------------------------
   def get_SMR_Direction_Shift(self, znlist):
      
      param_list = ['TPI_IDSS','TPI_ODSS']
      shift_Zone =[self.dut.numZones - 1 for hd in range(self.numHeads)]
      meas_rec = {}
      for hd in xrange(self.numHeads):
         for param in param_list:
            meas_rec[param] = []
            for zn in znlist:
               meas_rec[param].append(self.measurements.getRecord(param, hd, zn))
               
            if verbose == 1:
               objMsg.printMsg('List %s %s' % (param, meas_rec[param]))
               
            a, b, c = Fit_2ndOrder(znlist, meas_rec[param])
            meas_rec[param] = []
            if a == -1 and b == -1 and c == -1:
               objMsg.printMsg('Unable to detect SMR direction shift')
            else:
               for zn in range(self.dut.numZones):
                  meas_rec[param].append((a * zn * zn) + (b * zn) + c)
                  
         if verbose == 1:
            objMsg.printMsg('hd  zn  TPI_IDSS  TPI_IDSSF  TPI_ODSS  TPI_ODSSF')
         for zn in range(self.dut.numZones):
            if meas_rec['TPI_ODSS'][zn] > meas_rec['TPI_IDSS'][zn] and zn < shift_Zone[hd]:
               shift_Zone[hd] = zn
            if verbose == 1:
               meas = CVbarDataHelper(self.measurements, hd, zn)
               objMsg.printMsg('%d  %2d  %3.4f   %3.4f   %3.4f   %3.4f' % (hd, zn, meas['TPI_IDSS'], meas_rec['TPI_IDSS'][zn], meas['TPI_ODSS'], meas_rec['TPI_ODSS'][zn]))
      if verbose == 1:
         objMsg.printMsg('shift_Zone %s' % shift_Zone)
      return shift_Zone
   #----------------------------------------------------------------------------------------------------------
   def calculateBandedTPI(self,measurements):
      curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
      occurrence = 0  # reset the occurrence so we can avoid PK issues.
      spcId = self.spcIdHlpr.getSpcId('P_VBAR_FORMAT_SUMMARY')
      debugStr = "" #empty str
      if testSwitch.FAST_2D_S2D_TEST:
         headerStr = 'Hd  Zn  SQZ_DSS  SQZ_IDSS SQZ_ODSS  DIR   SQZ_EFF  RD_OFST   SQZ_IDS2D  SQZ_ODS2D  TPIP  MAX_TPI'
      else: headerStr = 'Hd  Zn  SQZ_DSS  SQZ_IDSS  SQZ_ODSS  DIR   SQZ_EFF  RD_OFST'
      debugStr += 'Banded TPI'+"\n"
      debugStr += headerStr+"\n"
      if testSwitch.FE_0281130_348429_ENABLE_SINGULAR_SMR_DIR_SHIFT:
         shift_Zone = self.get_SMR_Direction_Shift([zn for zn in range(self.numUserZones) if self.tracksPerBand[zn] != 1])
      
      for hd in xrange(self.numHeads):
         for zn in xrange(self.numUserZones):
            pickerData = CVbarDataHelper(self, hd, zn)
            meas = measurements.getNibletizedRecord(hd, zn)
            meas_saved = CVbarDataHelper(measurements, hd, zn)

            meas['TPI_DSS'] = meas['TPI']
            meas_saved['TPI_DSS'] = meas_saved['TPI']

            backoffDS = self.settings['WriteFaultThreshold'][zn] - self.settings['TPIMeasurementMargin'][zn]
            backoffSS = 2 * self.settings['WriteFaultThresholdSlimTrack'][zn] - 2 * self.settings['TPIMeasurementMargin'][zn]
            meas_saved['SNGL_DIR'] = 1
            meas_saved['TRACK_PER_BAND'] = self.tracksPerBand[zn]
            
            if testSwitch.FE_0281130_348429_ENABLE_SINGULAR_SMR_DIR_SHIFT:
               if zn >= shift_Zone[hd]:
                  pickerData['ShingleDirection'] = SHINGLE_DIRECTION_ID_TO_OD
               else:
                  pickerData['ShingleDirection'] = SHINGLE_DIRECTION_OD_TO_ID
            else:
               if meas['TPI_ODSS'] > meas['TPI_IDSS']:
                  pickerData['ShingleDirection'] = SHINGLE_DIRECTION_ID_TO_OD
               else:
                  pickerData['ShingleDirection'] = SHINGLE_DIRECTION_OD_TO_ID
                  
            # Special Case for backward compatability
            if self.tracksPerBand[zn] == 1:
               tpi_sss = meas['TPI_DSS']
               backoffSS = backoffDS
               direction = 'IDSS'
               pickerData['ReadOffset'] = 0
            
            elif pickerData['ShingleDirection'] == SHINGLE_DIRECTION_ID_TO_OD:
               tpi_sss = meas['TPI_ODSS']
               direction = 'ODSS'
               pickerData['ReadOffset'] = int(meas['RD_OFST_ODSS'])
               meas_saved['SNGL_DIR'] = -1

            else:
               tpi_sss = meas['TPI_IDSS']
               direction = 'IDSS'
               pickerData['ReadOffset'] = int(meas['RD_OFST_IDSS'])

            if self.use_OTC_Rd_Offset == 1 and self.tracksPerBand[zn] != 1: #use OTC read offset
               pickerData['ReadOffset'] = int(meas['RD_OFST_OTC'])

            # Another Special Case, if single sided capability is less than double sided, set everything to double sided
            if (tpi_sss) <= (meas['TPI_DSS']):
               tpi_sss = meas['TPI_DSS']
               backoffSS = backoffDS
               direction = 'IDSS'
               pickerData['ShingleDirection'] = SHINGLE_DIRECTION_OD_TO_ID
               pickerData['ReadOffset'] = 0

            sp = float(self.settings['ShingledProportion'][zn])
            tpb = float(self.tracksPerBand[zn])
            effectiveTpic = (tpb - TP.TG_Coef)/tpb * sp * (tpi_sss) + ( 1 - sp + sp * TP.TG_Coef/tpb) * (meas['TPI_DSS'])
            pickerData['TpiCapability'] = effectiveTpic
            pickerData['TpiCapabilityMax'] = effectiveTpic
            pickerData['TpiCapabilitySSS'] = tpi_sss
            pickerData['TpiCapabilityDSS'] = meas['TPI_DSS']
            pickerData['TpiMargin'] = effectiveTpic - pickerData['TpiPick']

            if testSwitch.FE_0293889_348429_VBAR_MARGIN_BY_OTCTP and self.tracksPerBand[zn] != 1:
               if meas['TPI_INTRA'] == -1.0:
                  meas['TPI_INTRA'] = tpi_sss
               if meas['TPI_INTER'] == -1.0: 
                  meas['TPI_INTER'] = meas['TPI_DSS']
               pickerData['TpiM_SSS'] = tpi_sss - meas['TPI_INTRA']
               pickerData['TpiM_DSS'] = meas['TPI_DSS'] - meas['TPI_INTER']
               if testSwitch.FE_0293889_348429_VBAR_MARGIN_BY_OTCTP_RELAX_ONLY:
                  pickerData['TpiM_SSS'] = max(0.0, pickerData['TpiM_SSS'])
                  pickerData['TpiM_DSS'] = max(0.0, pickerData['TpiM_DSS'])
               effectiveTpicMax = (tpb - TP.TG_Coef)/tpb * sp * (tpi_sss - self.data[hd][zn]['TpiM_SSS']) + ( 1 - sp + sp * TP.TG_Coef/tpb) * (meas['TPI_DSS'])
               pickerData['TpiCapabilityMax'] = effectiveTpicMax
            elif testSwitch.VBAR_MARGIN_BY_OTC and self.tracksPerBand[zn] != 1:
               pickerData['TpiCapabilityMax'] = meas['TPI_OTC']
               debugStr += "%2d  %-2d  %.4f   %.4f   %.4f   %s   %.4f      %-3d \n" \
                  %  (hd, zn, meas['TPI_DSS'], meas['TPI_IDSS'], meas['TPI_ODSS'], direction, effectiveTpic, pickerData['ReadOffset'])
            elif testSwitch.FAST_2D_S2D_TEST and self.tracksPerBand[zn] != 1:
               if not meas.has_key('TPI_IDSS2D'):
                  meas_saved['TPI_IDSS2D'] = -1
               if not meas.has_key('TPI_ODSS2D'):
                  meas_saved['TPI_ODSS2D'] = -1
               if meas['TPI_ODSS'] > meas['TPI_IDSS']:
                  pickerData['TpiCapabilityMax'] = meas['TPI_ODSS2D']
               else: 
                  pickerData['TpiCapabilityMax'] = meas['TPI_IDSS2D']
               debugStr += "%2d  %-2d  %.4f   %.4f   %.4f   %s   %.4f      %-3d    %.4f     %.4f     %.4f   %.4f \n" \
                  % (hd, zn, meas_saved['TPI_DSS'], meas_saved['TPI_IDSS'], meas_saved['TPI_ODSS'], direction, effectiveTpic, pickerData['ReadOffset'], meas_saved['TPI_IDSS2D'], meas_saved['TPI_ODSS2D'], pickerData['TpiPick'], pickerData['TpiCapabilityMax'])
            else:
               debugStr += "%2d  %-2d  %.4f   %.4f   %.4f   %s   %.4f      %-3d \n" \
                  % (hd, zn, meas['TPI_DSS'], meas['TPI_IDSS'], meas['TPI_ODSS'], direction, effectiveTpic, pickerData['ReadOffset'])
            dblog_record = {
               'SPC_ID'          : self.spc_id_banded_tpi,
               'OCCURRENCE'      : self.SmrOccurrence,
               'SEQ'             : curSeq,
               'TEST_SEQ_EVENT'  : testSeqEvent,
               'HD_PHYS_PSN'     : self.dut.LgcToPhysHdMap[hd],
               'DATA_ZONE'       : zn,
               'HD_LGC_PSN'      : hd,
               'BPIC'            : round(meas['BPI'], 4),
               'TPI_DSS'         : round(meas['TPI_DSS'], 4),
               'TPI_IDSS'        : round(meas['TPI_IDSS'], 4),
               'TPI_ODSS'        : round(meas['TPI_ODSS'], 4),
               'TPI_EFF'         : round(effectiveTpic, 4),
               'TPI_MAX'         : round(pickerData['TpiCapabilityMax'], 4),
               'RD_OFFSET'       : pickerData['ReadOffset'],
               'DIR'             : meas_saved['SNGL_DIR'],
            }
            if self.dumpBandedTPITable: 
               self.dut.dblData.Tables('P_VBAR_BANDED_FMT_SUMMARY').addRecord(dblog_record)


            def addSmrMeasurement(bpiCap,sqzType,bpiMsrd,sqzCap):
               self.dut.dblData.Tables('P_VBAR_SMR_MEASUREMENT').addRecord(
                     {
                     'SPC_ID'          : spcId,
                     'OCCURRENCE'      : self.SmrOccurrence,
                     'SEQ'             : curSeq,
                     'TEST_SEQ_EVENT'  : testSeqEvent,
                     'HD_PHYS_PSN'     : objDut.LgcToPhysHdMap[hd],
                     'HD_LGC_PSN'      : hd,
                     'DATA_ZONE'       : zn,
                     'BPI_CAP'         : bpiCap,
                     'SQZ_TYPE'        : sqzType,
                     'MSRD_BPI'        : bpiMsrd,
                     'SQZ_CAP'         : sqzCap,
                     })
               self.SmrOccurrence += 1

            for sqzType,sqzCode in [('TPI_DSS',68),('TPI_IDSS',73),('TPI_ODSS',79),]:
               addSmrMeasurement(meas['BPI'],sqzCode,meas['BPI'],meas[sqzType])
            addSmrMeasurement(meas['BPI'],1,meas['BPI'],meas['TPI_DSS']-(self.settings['WriteFaultThreshold'][zn] - self.settings['TPIMeasurementMargin'][zn]))
            if not testSwitch.FAST_2D_VBAR:
               addSmrMeasurement(meas['BPI'],2,meas['BPI'],meas['TPI_IDSS']- 2*(self.settings['WriteFaultThreshold'][zn] - self.settings['TPIMeasurementMargin'][zn]))
               addSmrMeasurement(meas['BPI'],3,meas['BPI'],meas['TPI_ODSS']- 2*(self.settings['WriteFaultThreshold'][zn] - self.settings['TPIMeasurementMargin'][zn]))
            else:
               addSmrMeasurement(meas['BPI'],2,meas['BPI'],meas['TPI_IDSS']- 2*(self.settings['WriteFaultThresholdSlimTrack'][zn] - self.settings['TPIMeasurementMargin'][zn]))
               addSmrMeasurement(meas['BPI'],3,meas['BPI'],meas['TPI_ODSS']- 2*(self.settings['WriteFaultThresholdSlimTrack'][zn] - self.settings['TPIMeasurementMargin'][zn]))

      if verbose: objMsg.printMsg("%s \n" % debugStr)
      if self.dumpBandedTPITable and (not testSwitch.CM_REDUCTION_REDUCE_PRINTDBLOGBIN): #cut logs by only printing current spc id table
         objMsg.printDblogBin(self.dut.dblData.Tables('P_VBAR_BANDED_FMT_SUMMARY'), spcId32 = self.spc_id_banded_tpi)


   #-------------------------------------------------------------------------------------------------------
   def initializeTpiStepSizeArray(self):
      """ initializeTpiStepSizeArray:
            Since only integral numbers of bands can fit in a data zone, calculate the tpi step size allowable
            in each zone.
            """
      # TODO:
      if testSwitch.FE_0269922_348085_P_SIGMUND_IN_FACTORY:
         self.tpiStepSize = [ [] for hd in range(self.numHeads)]
         for hd in range(self.numHeads) :
            self.tpiStepSize[hd] = [float(self.tracksPerBand[zone])/self.bpiFile.getNumNominalTracksInZone(0,zone,hd) \
                                 for zone in range(self.numUserZones)]
      else:
         self.tpiStepSize = [float(self.tracksPerBand[zone])/self.bpiFile.getNumNominalTracksInZone(0,zone) \
                             for zone in range(self.numUserZones)]

   #-------------------------------------------------------------------------------------------------------
   def getTracksPerZone(self):
      tracks_ar = []
      for hd in xrange(self.numHeads):
         for zn in xrange(self.numUserZones):
            tippick = self.getRecord['TpiPick']
            tracks = (int(round(tippick * self.bpiFile.getNumNominalTracksInZone(self.baseformat[hd],zn,hd))) - (int(round(tippick * self.bpiFile.getNumNominalTracksInZone(self.baseformat[hd],zn,hd)))%self.tracksPerBand[zn]) )
            if self.tracksPerBand[zn] > 1 :
               tracks = tracks - self.tracksPerBand[zn]
            tracks_ar.append(tracks)
      return tracks_ar

   #-------------------------------------------------------------------------------------------------------
   def calculateTrackPitchParameters(self,hd,zn,maximize_zone = 1, print_table = 1):
      """
      calculateTrackPitchParameters sets up the information for a test 210 call with shingled drives.
      It calculates
      TrackPitch
      TrackGuard
      ShingleDirection
      """
      zfi = CVbarDataHelper(self, hd, zn)
      meas = CVbarDataHelper(self.measurements, hd, zn)

      # save off the effective pick for the next iteration of the picker
      meas['TPIPickEffective'] = zfi['TpiPick']
      meas['TPIFmtEffective'] = zfi['TpiPick'] * self.formatScaler.RelativeToFormatScaler - self.formatScaler.RelativeToFormatScaler

      # first calculate the band size from the effective pick
      bandSizePicked = self.tracksPerBand[zn]/zfi['TpiPick']

       # calculate the Track Pitch of the shingled track.
      # taken directly from the TPIc of the single sided measurement


      #objMsg.printMsg("ccccyyyTpiCapabilitySSS = %f, ccccyyyTpiMarginThresScale = %f" % (zfi['TpiCapabilitySSS'],zfi['TpiMarginThresScale']))



      if testSwitch.FE_0215591_007867_COMPUTE_TPIC_AS_RATIO_MERGE_CL537310:
         if testSwitch.FE_0293889_348429_VBAR_MARGIN_BY_OTCTP and self.tracksPerBand[zn] != 1:
            TPs = 1.0 / (zfi['TpiCapabilitySSS'] - zfi['TpiM_SSS'])
         elif testSwitch.FAST_2D_S2D_TEST or testSwitch.VBAR_MARGIN_BY_OTC:
            TPs = 1.0 / (zfi['TpiCapabilitySSS'] - zfi['TpiMarginThresScale'])
         else:
            TPs = 1.0 / zfi['TpiCapabilitySSS']
            
          # get Double sided track pitch
         if testSwitch.RUN_ATI_IN_VBAR and self.tracksPerBand[zn] == 1:
            TPd = 1.0 / (zfi['TpiCapabilityDSS'] - zfi['TpiMarginThresScale'])
         elif testSwitch.FE_0293889_348429_VBAR_MARGIN_BY_OTCTP_INTERBAND_MARGIN and self.tracksPerBand[zn] != 1:
            TPd = 1.0 / (zfi['TpiCapabilityDSS'] - zfi['TpiM_DSS'])
         else:
            TPd = 1.0 / zfi['TpiCapabilityDSS']
      else:
         TPs = 2-zfi['TpiCapabilitySSS']
         # get Double sided track pitch
         TPd = 2-zfi['TpiCapabilityDSS']

      bandSize = (self.tracksPerBand[zn] - TP.TG_Coef) * TPs + TP.TG_Coef * TPd

      # Get the ratio of tpi pick to effective tpi capability.  Another form of margin
      if testSwitch.FAST_2D_VBAR:
         if bandSize == 0:
            bandSize = 1
      ratio = bandSizePicked/bandSize


      shingledProportion = self.settings['ShingledProportion'][zn]
      # when pick is larger than capability trackpitch must be smaller
      #Petes notes  Tp   = Ts  *   P   *      S             +  P    * (1-S)                  * Td
      ShingledTrackPitch = TPs * ratio * shingledProportion + ratio * (1-shingledProportion) * TPd

      if not testSwitch.SMR_NEW_GUARD_TRK_PITCH_ALG:
         #Petes notes Tg = 2 * ( Td-Ts ) *   P   *      S
         GuardTrackPitch = TP.TG_Coef * (TPd-TPs) * ratio * shingledProportion
      else:
         #Petes new Guard Track Pitch algorithm.
         #Petes notes Tg = 2 * (TPd -        Tp         ) *        S
         GuardTrackPitch = 2 * (TPd - ShingledTrackPitch) * shingledProportion
         if GuardTrackPitch < 0:
            GuardTrackPitch = 0

      TrackPitch = int(ShingledTrackPitch * Q0toQ15Factor)
      TrackGuard = int(max(GuardTrackPitch * Q0toQ14Factor,0))

      # limit the values to the 16 bit size.  There is an issue here,
      # in that VBAR is going to underestimate the capacity of the drive and overestimate the margin.
      if TrackPitch > 0xFFFF:
         TrackPitch = 0xFFFF
      if TrackGuard > 0xFFFF:
         TrackGuard = 0xFFFF
      # The amount of space in the zone that we can use is the Number of Nominal Tracks in the zone minus one Guard Pitch
      # We want the guard pitch to avoid a possible squeeze situation at zone boundaries.
      numNominalTracksAlloc = self.bpiFile.getNumNominalTracksInZone(0,zn,hd)
      numBands = int((numNominalTracksAlloc - GuardTrackPitch)/bandSizePicked)

      numLogicalTracks = numBands * self.tracksPerBand[zn]
      numNominalTracksUsed = float((TrackPitch * self.tracksPerBand[zn] + TrackGuard * 2)*numBands + 2*TrackGuard)/Q0toQ15Factor


      if maximize_zone or not testSwitch.OTC_SKIP_ZONE_MAXIMIZATION:

         Modification = 'Pitch'
         # try to use the entire allocated space without going over
         #   we should always be a bit underutilized due to the flooring of the division
         while (numNominalTracksUsed < numNominalTracksAlloc):
            if TrackPitch == 0xFFFF:
               break
            TrackPitch += 1
            numNominalTracksUsed = float((TrackPitch * self.tracksPerBand[zn] + TrackGuard * 2)*numBands + 2*TrackGuard)/Q0toQ15Factor

         # now the zone is a bit too big Ping - Pong between removing pitch and guard
         while (numNominalTracksUsed > numNominalTracksAlloc):
            if Modification == 'Guard':
               if TrackGuard > 0:
                  TrackGuard -= 1
               Modification = 'Pitch'
            else:
               if TrackPitch > 0:
                  TrackPitch -= 1
               Modification = 'Guard'

               numNominalTracksUsed = float((TrackPitch * self.tracksPerBand[zn] + TrackGuard * 2)*numBands + 2*TrackGuard)/Q0toQ15Factor

         if Modification == "Guard":
            # the last modification done was pitch. see if we can increase guard.
            while (numNominalTracksUsed < numNominalTracksAlloc):
               if TrackGuard == 0xFFFF:
                  break
               TrackGuard += 1
               numNominalTracksUsed = float((TrackPitch * self.tracksPerBand[zn] + TrackGuard * 2)*numBands + 2*TrackGuard)/Q0toQ15Factor
            while (numNominalTracksUsed > numNominalTracksAlloc):
               TrackGuard -= 1
               numNominalTracksUsed = float((TrackPitch * self.tracksPerBand[zn] + TrackGuard * 2)*numBands + 2*TrackGuard)/Q0toQ15Factor

      ShingledTrackPitch = float(TrackPitch)/Q0toQ15Factor
      GuardTrackPitch = float(2*TrackGuard)/Q0toQ15Factor
      if testSwitch.DISPLAY_SMR_FMT_SUMMARY:
         if self.use_OTC_Rd_Offset:
            MicrojogSqueeze = int(zfi['ReadOffset'] / 2 )
         else:
            MicrojogSqueeze = int((TrackGuard * 128 / 16384)/4)

         if zfi['ShingleDirection'] == SHINGLE_DIRECTION_OD_TO_ID:
            shingleDir = "OD_TO_ID"
            if not self.use_OTC_Rd_Offset:
               MicrojogSqueeze *= -1
         else:
            shingleDir = "ID_TO_OD"

         if testSwitch.FE_0184102_326816_ZONED_SERVO_SUPPORT: # Debug. Will remove once CH10 is mature.
            objMsg.printMsg("hd = %d, zn = %d" % (hd,zn))
            objMsg.printMsg("TPICs = %f, TPs = %f" % (zfi['TpiCapabilitySSS'],TPs))
            objMsg.printMsg("TPICd = %f, TPd = %f" % (zfi['TpiCapabilityDSS'],TPd))
            objMsg.printMsg("Pick = %f, EffC = %f, ratio = %f" % ( zfi['TpiPick'],zfi['TpiCapability'],ratio))
            objMsg.printMsg("BandSize = %f, Tb = %f, Tg = %f, BS = %f" % (bandSizePicked, ShingledTrackPitch, GuardTrackPitch, ShingledTrackPitch*self.tracksPerBand[zn] + GuardTrackPitch))
            objMsg.printMsg("TP = %d, TG = %d, LogTrks = %d, NomTrksAlloc = %d, NomTrksUsed = %f, numBands = %d" % (TrackPitch,TrackGuard,numLogicalTracks,numNominalTracksAlloc,numNominalTracksUsed,numBands))
         if print_table:
             self.dut.dblData.Tables('P_SMR_FORMAT_SUMMARY').addRecord({
                                    'SPC_ID'            : self.spcId_SMR_FMT,
                                    'OCCURRENCE'        : self.SmrOccurrence,
                                    'SEQ'               : self.dut.objSeq.getSeq(),
                                    'TEST_SEQ_EVENT'    : 1,
                                    'HD_PHYS_PSN'       : self.dut.LgcToPhysHdMap[hd],
                                    'DATA_ZONE'         : zn,
                                    'HD_LGC_PSN'        : hd,
                                    'TPIC_S'            : round(zfi['TpiCapabilitySSS'],6),
                                    'TP_S'              : round(TPs,6),
                                    'TPIC_D'            : round(zfi['TpiCapabilityDSS'],6),
                                    'TP_D'              : round(TPd,6),
                                    'PICK'              : round(zfi['TpiPick'],6),
                                    'EFF_TPIC'          : round(zfi['TpiCapability'],6),
                                    'BANDSIZE_RATIO'    : round(ratio,6),
                                    'BANDSIZE_PICK'     : round(bandSizePicked,6),
                                    'SHINGLE_TRK_PITCH' : round(ShingledTrackPitch,6),
                                    'GUARD_TRK_PITCH'   : '%.8f' % GuardTrackPitch, #round(GuardTrackPitch,8), round was producing scientific notation here.
                                    'SHINGLE_DIR'       : shingleDir,
                                    'UJOG_SQUEEZE'      : round(MicrojogSqueeze,6),
                                    'BANDSIZE_PHY'      : round((ShingledTrackPitch*self.tracksPerBand[zn]) + GuardTrackPitch,6),
                                    'TRK_PITCH'         : round(TrackPitch,6),
                                    'TRK_GUARD'         : round(TrackGuard,6),
                                    'NUM_LGC_TRKS'      : round(numLogicalTracks,6),
                                    'NOM_TRKS_ALLOC'    : round(numNominalTracksAlloc,6),
                                    'NOM_TRKS_USED'     : round(numNominalTracksUsed,6),
                                    'NUM_OF_BANDS'      : round(numBands,6),
                                  })

      else:
         # self.data2['Tb'][hd][zn] = ShingledTrackPitch
         # self.data2['Tg'][hd][zn] = GuardTrackPitch
         objMsg.printMsg("hd = %d, zn = %d" % (hd,zn))
         objMsg.printMsg("TPICs = %f, TPs = %f" % (zfi['TpiCapabilitySSS'],TPs))
         objMsg.printMsg("TPICd = %f, TPd = %f" % (zfi['TpiCapabilityDSS'],TPd))
         objMsg.printMsg("Pick = %f, EffC = %f, ratio = %f" % ( zfi['TpiPick'],zfi['TpiCapability'],ratio))
         objMsg.printMsg("BandSize = %f, Tb = %f, Tg = %f, BS = %f" % (bandSizePicked, ShingledTrackPitch, GuardTrackPitch, ShingledTrackPitch*self.tracksPerBand[zn] + GuardTrackPitch))
         objMsg.printMsg("TP = %d, TG = %d, LogTrks = %d, NomTrksAlloc = %d, NomTrksUsed = %f, numBands = %d" % (TrackPitch,TrackGuard,numLogicalTracks,numNominalTracksAlloc,numNominalTracksUsed,numBands))
      if testSwitch.EFFECTIVE_TPIC_EQUAL_TPIS:
         TrackPitch = int(Q0toQ15Factor / zfi['TpiCapabilitySSS'])

      return (TrackPitch,TrackGuard)

   #-------------------------------------------------------------------------------------------------------
   def setFormat(self, metric, hd=0xff, zn=0xff, movezoneboundaries=False, maximize_zone = 1, \
         programZonesWithZipperZonesOnly = 0, print_table = 1, consolidateByZone = 0, set_one_tpb = 0):
      """
      setFormat sets the drive BPI and TPI formats to the requested values
      If movezoneboundaries is true, then the BPI format must be set by head, and
      it will set the user zone configuration (zone boundaries).
      Otherwise just the BPI or TPI will be set on the head and zone requested
      """

      if not self.sendFormatToDrive:
         return

      if testSwitch.FE_0257373_348085_ZONED_SERVO_CAPACITY_CALCULATION:
         if programZonesWithZipperZonesOnly and (hd != 0xff) and (zn != 0xff):
            if zn not in self.dut.dataZonesWithZipperZones[hd]:
               return

      prm_210 = {'test_num': 210,
                 'prm_name': 'Update Formats To Drive',
                 'timeout' : 1800,
                 #'dlfile'  : (CN, self.bpiFile.bpiFileName),
                 'spc_id'  : 0,
                 }
      if not testSwitch.FE_0269922_348085_P_SIGMUND_IN_FACTORY:
         prm_210.update({
                'dlfile'   : (CN,self.bpiFile.bpiFileName),
                })

      if testSwitch.WA_0152247_231166_P_POWER_CYCLE_RETRY_SIM_ERRORS:
         prm_210.update({
               'retryECList'       : [10335],
               'retryCount'        : 3,
               'retryMode'         : POWER_CYCLE_RETRY,
               })

         if testSwitch.TRUNK_BRINGUP: #trunk code see 10451 also
             prm_210.update({
                'retryECList'       : [10335,10451,10403,10468],
                })

      if testSwitch.FE_0147058_208705_SHORTEN_VBAR_LOGS:
         prm_210['stSuppressResults'] = ST_SUPPRESS__ALL

      starthead=hd
      endhead=hd
      if hd==0xff:
         endhead = self.numHeads-1
         starthead = 0
      startzone = zn
      endzone = zn
      if zn==0xff:
         startzone=0
         endzone=self.numUserZones-1
      
      if consolidateByZone:
         commands = self.consolidateSettingFormatByZone(starthead, endhead, startzone, endzone, print_table, \
            maximize_zone, metric, set_one_tpb)
      else:
         # Container for the format update st calls
         commands = []

         # Iterate through all zones and build the T210 call packets for BPI and TPI
         # If heads/zones haven't changed since the last update, don't set them again
         # Combine zones that are equivalent in all respects
         nominalFormat = self.bpiFile.getNominalFormat()
         nominalTracks = self.bpiFile.getNominalTracksPerSerpent()
         for zn in xrange(startzone,endzone+1):
            if testSwitch.FE_0257373_348085_ZONED_SERVO_CAPACITY_CALCULATION:
               if programZonesWithZipperZonesOnly:
                  for hd in xrange(starthead,endhead+1):
                     if zn in self.dut.dataZonesWithZipperZones[hd]:
                        break
                  else:
                     continue
                     
            bpitables = []
            tpitables = []
            trackGuardTables = []
            shingleDirectionTables = []
            MicrojogSqueezeTables = []
            tracksPerBandTables = [self.tracksPerBand[zn],]*T210_PARM_NUM_HEADS
            bpi_head_mask = 0
            tpi_head_mask = 0
            
            for hd in xrange(T210_PARM_NUM_HEADS):
               if hd >= starthead and hd <= endhead:
                  pickerData = CVbarDataHelper(self, hd, zn)
                  # Set up BPI formats
                  bpitables.append(nominalFormat+pickerData['BpiFormat']) 
                  # Set up Track Pitch formats
                  temp1, temp2 = self.calculateTrackPitchParameters(hd,zn,maximize_zone=maximize_zone,print_table=print_table)
                  tpitables.append(temp1)
                  trackGuardTables.append(temp2)
                  shingleDirectionTables.append(pickerData['ShingleDirection'])
                  if self.use_OTC_Rd_Offset:
                     MicrojogSqueezeTables.append(int(pickerData['ReadOffset']/2))
                  else:
                     if pickerData['ShingleDirection'] == SHINGLE_DIRECTION_OD_TO_ID:
                        MicrojogSqueezeTables.append(int((temp2*128/16384)/4*(-1)))
                     else:
                        MicrojogSqueezeTables.append(int((temp2*128/16384)/4))
                  # Set up head masks
                  adjust = True
                  if testSwitch.FE_0257373_348085_ZONED_SERVO_CAPACITY_CALCULATION:
                     if zn in self.dut.dataZonesWithZipperZones[hd]:
                        self.needToGetZonesWithZipperZonesCapFromSF3 = 1
                     if programZonesWithZipperZonesOnly and (zn not in self.dut.dataZonesWithZipperZones[hd]):
                        adjust = False
                  if adjust:
                     if pickerData['AdjustedBpiFormat'] == 'T':
                        bpi_head_mask |= 1 << hd
                     if pickerData['AdjustedTpiFormat'] == 'T':
                        tpi_head_mask |= 1 << hd
               else:
                  # Set up BPI formats
                  bpitables.append(nominalFormat)
                  # Set up Track Pitch formats
                  tpitables.append(Q0toQ15Factor)     # default to 1.0 Nominal Tracks
                  trackGuardTables.append(0)          # default to 0.0 Nominal Tracks
                  shingleDirectionTables.append(SHINGLE_DIRECTION_OD_TO_ID)
                  MicrojogSqueezeTables.append(0)

            # Issue BPI and TPI separately if the head masks don't match
            if metric == 'BOTH' and bpi_head_mask != tpi_head_mask:
               metrics = ['BPI', 'TPI']
            else:
               metrics = [metric]

            for local_metric in metrics:
               # Build the command packet
               command = {
                           'CWORD1'    : 0x0100,
                           'HEAD_MASK' : 0x0000,
                           'ZONE'      : (zn << 8) | zn,
                           'CWORD2'    : 0x0000,
                         }

               if local_metric in ('BPI', 'BOTH'):
                  command['CWORD1'] |= SET_BPI
                  command['HEAD_MASK'] |= bpi_head_mask
                  command['BPI_GROUP_EXT'] = bpitables

               if local_metric in ('TPI', 'BOTH'):
                  command['CWORD1'] |= SET_TPI

                  command['HEAD_MASK'] |= tpi_head_mask

                  command['CWORD2'] |= CW2_SET_TRACK_PITCH
                  command['TRK_PITCH_TBL'] = tpitables

                  command['CWORD2'] |= CW2_SET_TRACK_GUARD
                  command['TRK_GUARD_TBL'] = trackGuardTables

                  command['CWORD2'] |= CW2_SET_SHINGLED_DIRECTION
                  command['SHINGLED_DIRECTION'] = shingleDirectionTables

                  command['CWORD2'] |= CW2_SET_TRACKS_PER_BAND
                  command['TRACKS_PER_BAND'] = tracksPerBandTables
                  if self.updateShingleDirection:
                     command['CWORD2'] |= CW2_SET_SHINGLED_DIRECTION
                     command['SHINGLED_DIRECTION'] = shingleDirectionTables

                  if self.updateSqueezeMicrojog:
                     command['CWORD2'] |= CW2_SET_SQUEEZE_MICROJOG
                     command['MICROJOG_SQUEEZE'] = MicrojogSqueezeTables
                     for hd in range(starthead,endhead+1):
                        tpi_head_mask |= 1 << hd
                     command['HEAD_MASK'] |= tpi_head_mask
               if local_metric in ('UJOG'):
                  command['CWORD1'] |= SET_TPI
                  command['CWORD2'] |= CW2_SET_SQUEEZE_MICROJOG
                  command['MICROJOG_SQUEEZE'] = MicrojogSqueezeTables
                  for hd in range(starthead,endhead+1):
                     tpi_head_mask |= 1 << hd
                  command['HEAD_MASK'] |= tpi_head_mask


               # If no heads are active, skip the command altogether
               if command['HEAD_MASK'] == 0:
                  continue

               # Look for other identical zones
               for previous in commands:
                  keys_to_compare = command.keys()
                  keys_to_compare.remove("ZONE")  # Don't compare zones - they're always different
                  equal = reduce(lambda x, y: x and y, [previous.get(key, None) == command.get(key, None) for key in keys_to_compare])
                  if equal and ((previous["ZONE"] & 0xFF) == zn - 1):
                     # Include the new zone and move on
                     previous["ZONE"] &= 0xFF00
                     previous["ZONE"] |= zn
                     break
               else:
                  # No matches; add the new command
                  commands.append(command)

      # Actually issue the commands
      for command in commands:
         parms = prm_210.copy()
         parms.update(command)
         parms['prm_name'] = t210PrmName(parms, ByZone=consolidateByZone)

         if not (testSwitch.VBAR_2D_DEBUG_MODE or testSwitch.DO_NOT_SAVE_FORMAT):
            getVbarGlobalClass(CProcess).St(parms)
         else:
            objMsg.printMsg('BYPASS 2D VBAR FORMAT SETTING=================================================================')

         # Mark these zones as "Reset" so that they get re-optimized and measured
         if command['CWORD1'] & SET_BPI:
            startzn = (command['ZONE'] & 0xFF00) >> 8
            endzn   = (command['ZONE'] & 0x00FF)
            for hd in xrange(starthead, endhead+1):
               if command['HEAD_MASK'] & (1 << hd):
                  for zn in xrange(startzn, endzn+1):
                     self.measurements.setRecord('BPIChanged', 'T', hd, zn)

         # Clear the OPTI_ZAP_DONE flag if TPI is changed
         if command['CWORD1'] & SET_TPI:
            self.dut.driveattr['OPTI_ZAP_DONE'] = 0
      getVbarGlobalVar()['formatReload'] = True

   #-----------------------------------------------------------------------------
   def adjustTPI(self,hd,worstzone,pickDelta):
      zn = worstzone #the input is just zone not worstzone
      zfi = CVbarDataHelper(self, hd, zn)
      zfi['TpiPick'] += pickDelta
      zfi['TpiFormat'] = int(round(zfi['TpiPick'] * self.formatScaler.RelativeToFormatScaler))

      # If the zone has been changed, set flag to update the format
      if self.bpiFile.hasSectorPerTrackInfo():
         if zfi['TpiFormat'] == self.formatScaler.getFormat(hd, zn, 'TPI'):
            zfi['AdjustedTpiFormat'] = 'F'
         else:
            zfi['AdjustedTpiFormat'] = 'T'
      else:
         if pickDelta != 0:
            zfi['AdjustedTpiFormat'] = 'T'      # Set up sentinel to force format update before getting capacity

      # Define useful terms to make the Increase and Decrease TPI conditionals below, easier to follow.
      TPIPick        = zfi['TpiPick']           # Current track pitch as a percent of nominal
      TPIPickInitial = zfi['TpiPickInitial']    # Initial track pitch as a percent of nominal, prior to any adjustment.
      TPIC           = zfi['TpiCapability']     # track pitch capability as a percent of nominal.
      if testSwitch.FE_0269922_348085_P_SIGMUND_IN_FACTORY:
         nextTPIPick    = TPIPick + self.tpiStepSize[hd][zn] # Track pitch at the next higher tpi setting, step size is in % of nominal.
         prevTPIPick    = TPIPick - self.tpiStepSize[hd][zn] # Track pitch at the next lower tpi setting, relative to nominal.
         marginAtNextTPIPick = TPIC - TPIPick - self.tpiStepSize[hd][zn]    # Margin at next higher track pitch.
      else:
         nextTPIPick    = TPIPick + self.tpiStepSize[zn] # Track pitch at the next higher tpi setting, step size is in % of nominal.
         prevTPIPick    = TPIPick - self.tpiStepSize[zn] # Track pitch at the next lower tpi setting, relative to nominal.
         marginAtNextTPIPick = TPIC - TPIPick - self.tpiStepSize[zn]    # Margin at next higher track pitch.

      # Effective margin threshold = minimum allowed margin threshold plus a possible adjustment for heads with different write power table.
      if (testSwitch.VBAR_TPI_MARGIN_THRESHOLD_BY_HD_BY_ZN or testSwitch.VBAR_MARGIN_BY_OTC or testSwitch.FAST_2D_S2D_TEST):
         effectiveMarginThreshold = zfi['TpiMarginThresScale'] + self.dut.TPIMarginThresholdAdjust[hd]
      else:
         effectiveMarginThreshold = self.settings['TPIMarginThreshold'][zn] + self.dut.TPIMarginThresholdAdjust[hd]

      # Check to see if it is okay to increase the TPI Pick selection for this hd-zn combination.
      if ( (marginAtNextTPIPick < (effectiveMarginThreshold - RndErrCorrFactor)) or
           (nextTPIPick > TPI_MAX) or
           (abs(nextTPIPick - TPIPickInitial) > self.VbarHMSMaxTPIAdjust) or
           ((hd,zn) not in self.active_zones) ):
         zfi['OkToIncreaseTpi'] = 'F'
      else:
         zfi['OkToIncreaseTpi'] = 'T'

      # Check to see if it is okay to decrease the TPI Pick selection for this hd-zn combination.
      if ( (prevTPIPick < TPI_MIN) or
           (abs(prevTPIPick - TPIPickInitial) > self.VbarHMSMaxTPIAdjust) or
           ((hd,zn) not in self.active_zones) ):
         zfi['OkToDecreaseTpi'] = 'F'
      else:
         zfi['OkToDecreaseTpi'] = 'T'

   #-------------------------------------------------------------------------------------------------------
   def getTpiStepSize(self, zn=None):
      return self.tpiStepSize[zn]

   #-------------------------------------------------------------------------------------------------------
   def getDataZoneWithZipperZones(self, ExecuteTestT172 = 0):
       # TODO: test
       dataZonesWithZipperZones = [[] for hd in range(self.numHeads)]
       iZone =  -1
       previous_zone = -1
       oProcess = getVbarGlobalClass(CProcess)
       if ExecuteTestT172:
          oProcess.St(TP.PRM_DISPLAY_ZONED_SERVO_ZONE_TABLE_172)

       try:
          colDict = self.dut.dblData.Tables(TP.zoned_servo_zn_tbl['table_name']).columnNameDict()
          p172ZonedServoTbl = self.dut.dblData.Tables(TP.zoned_servo_zn_tbl['table_name']).rowListIter()
       except:
          objMsg.printMsg('!!! Tables %s - not found' % TP.zoned_servo_zn_tbl['table_name'])

       for row in p172ZonedServoTbl:
          iZone = int(row[colDict['DATA_ZONE']])
          iHead = int(row[colDict['HD_PHYS_PSN']])
          if iZone == previous_zone and iZone not in dataZonesWithZipperZones[iHead]:
             dataZonesWithZipperZones[iHead].append(iZone)
          previous_zone = iZone
       objMsg.printMsg('dataZonesWithZipperZones = %s'%(str(dataZonesWithZipperZones)))
       return dataZonesWithZipperZones

   #-------------------------------------------------------------------------------------------------------
   def pickTPI(self, marginOverTPIM = 0):
      for hd in xrange(self.numHeads):
         for zn in xrange(self.numUserZones):
            zfi = CVbarDataHelper(self, hd, zn)
            self.adjustTPI(hd,zn,0)
            while True:
               if testSwitch.VBAR_TPI_MARGIN_THRESHOLD_BY_HD_BY_ZN or testSwitch.VBAR_MARGIN_BY_OTC or testSwitch.FAST_2D_S2D_TEST:
                  if marginOverTPIM:
                     margin = zfi['TpiCapability'] - zfi['TpiPick'] - zfi['TpiMarginTarget'] - (zfi['TpiMarginThresScale'] + self.dut.TPIMarginThresholdAdjust[hd])
                  else:
                     margin = zfi['TpiCapability'] - zfi['TpiPick'] - zfi['TpiMarginTarget']
                  marginOverThreshold = zfi['TpiCapability'] - zfi['TpiPick'] - (zfi['TpiMarginThresScale'] + self.dut.TPIMarginThresholdAdjust[hd])
               else:
                  margin = zfi['TpiCapability'] - zfi['TpiPick'] - zfi['TpiMarginTarget']
                  marginOverThreshold = zfi['TpiCapability'] - zfi['TpiPick'] - (self.settings['TPIMarginThreshold'][zn] + self.dut.TPIMarginThresholdAdjust[hd])

               #if (hd == 0) and (zn == 0):
               #   objMsg.printMsg('hd %d, zn %d, margin= %1.4f, marginOverThres= %1.4f, Cap= %1.4f, Pick= %1.4f, Target= %1.4f' %
               #                    (hd, zn, margin, marginOverThreshold, zfi['TpiCapability'], zfi['TpiPick'], zfi['TpiMarginTarget']+1))

               if testSwitch.FE_0269922_348085_P_SIGMUND_IN_FACTORY:
                  tpiStepSize = self.tpiStepSize[hd][zn]
               else:
                  tpiStepSize = self.tpiStepSize[zn]
               if (margin >= tpiStepSize/2.0) and (zfi['OkToIncreaseTpi'] == 'T'):
                  self.adjustTPI(hd,zn,tpiStepSize)
               elif ((margin < -tpiStepSize/2.0) or (marginOverThreshold < - RndErrCorrFactor)) and (zfi['OkToDecreaseTpi'] == 'T'):
                  self.adjustTPI(hd,zn,-tpiStepSize)
               else:
                  break

      # Display initial pick table
      if not testSwitch.FE_0171684_007867_DISPLAY_PICKER_AS_TBL:
         self.displayCapability('TPI')

      self.setFormat('TPI')

   #-------------------------------------------------------------------------------------------------------
   def checkMinimumCapability(self, TPICap, BPICap, debug_DriveCapacity = 0):
      """
      Screen each head for minimum density requirements.
      Fail if any head fails the minimum check.
      Calculate the minimum density required before the picker algorithm will run.
      This figure is a function of the Capabilities and the Margin Thresholds.
      """
      if testSwitch.LCO_VBAR_PROCESS : #LCO version Max Density Computation
         BPIMT = mean(self.settings['BPIMarginThreshold'])
         BPIMTA = self.dut.BPIMarginThresholdAdjust
         TPIMT = mean(self.settings['TPIMarginThreshold'])
         TPIMTA = self.dut.TPIMarginThresholdAdjust
         maxDensity = mean([(BPICap[hd] - (BPIMT + BPIMTA[hd])) * (TPICap[hd] - (TPIMT + TPIMTA[hd])) for hd in range(self.numHeads)])
         if FE_0125707_340210_CAP_FROM_BPIFILE:
            maxDriveCapacity = maxDensity * self.bpiFile.getNominalCapacity()
         else:
            maxDriveCapacity = maxDensity * float(TP.VbarCapacityGBPerHead) * float(self.numHeads)

      else : # ScPk version Max Density Computation
         # init for table P_VBAR_MAX_FORMAT_SUMMARY
         self.spcIdHlpr.getSetIncrSpcId('P_VBAR_MAX_FORMAT_SUMMARY', startSpcId = 0, increment = 0, useOpOffset = 1)
         curSeq, occurrence, testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
         spcId = self.spcIdHlpr.getSpcId('P_VBAR_MAX_FORMAT_SUMMARY')
         
         # copy current value of bpic and tpic to temp space
         tempTpiPick = deepcopy(self.store['TpiPick'])
         tempBpiFormat = deepcopy(self.store['BpiFormat'])
         
         # calculate max bpic and tpic for each zone by factoring in bpi and tpi margin
         for hd in xrange(self.numHeads):
            for zn in xrange(self.numUserZones):
               pickerData = CVbarDataHelper(self, hd, zn)
               #calculate bpic and bpi_margin
               if testSwitch.BPICHMS or testSwitch.FE_CONSOLIDATED_BPI_MARGIN:
                  bpim = self.settings['BPIMarginThreshold'][hd][zn] + self.dut.BPIMarginThresholdAdjust[hd]
               else:
                  bpim = self.settings['BPIMarginThreshold'][zn] + self.dut.BPIMarginThresholdAdjust[hd]
               highest_bpic = pickerData['BpiCapability'] - bpim

               #calculate tpic and tpi margin
               if testSwitch.FE_0293889_348429_VBAR_MARGIN_BY_OTCTP and self.tracksPerBand[zn] != 1:
                  tpim = pickerData['TpiM_SSS']
                  highest_tpic = pickerData['TpiCapabilityMax']
               else:
                  tpim = pickerData['TpiMarginThresScale']
                  highest_tpic = pickerData['TpiCapability'] - tpim

               pickerData['TpiPick'] = highest_tpic
               bpiEntry = self.getClosestBPITable(highest_bpic,zn,hd)
               bpiChanged = pickerData['BpiFormat'] != bpiEntry
               if bpiChanged:
                  pickerData['BpiFormat'] = bpiEntry
                  if testSwitch.FE_0257373_348085_ZONED_SERVO_CAPACITY_CALCULATION:
                     pickerData['AdjustedBpiFormat'] = 'T'
               
               if self.dumpMaxFormatSummaryTBL:
                  self.dut.dblData.Tables('P_VBAR_MAX_FORMAT_SUMMARY').addRecord(
                  {
                        'SPC_ID'          : spcId,
                        'OCCURRENCE'      : occurrence,
                        'SEQ'             : curSeq,
                        'TEST_SEQ_EVENT'  : testSeqEvent,
                        'HD_PHYS_PSN'     : self.dut.LgcToPhysHdMap[hd],
                        'DATA_ZONE'       : zn,
                        'HD_LGC_PSN'      : hd,
                        'BPI_CAP'         : "%.6f" % pickerData['BpiCapability'],
                        'BPIM_SQZBPIC'    : "%.6f" % pickerData['BPIMSQZ'], 
                        'BPIM_FINAL'      : "%.6f" % bpim,
                        'BPIP_MAX'        : "%.6f" % highest_bpic,
                        'TPI_CAP'         : "%.6f" % pickerData['TpiCapability'],
                        'TPIM_ATI'        : "%.6f" % tpim,
                        'TPIP_MAX'        : "%.6f" % highest_tpic,
                        'ADC_MAX'         : "%.6f" % (highest_bpic * highest_tpic),
                        'NIBLET_IDX'      : self.settings['Niblet_Index'],
                  })

         if debug_DriveCapacity :
            self.debug_values(['TpiPick', 'BpiFormat', 'TpiCapability', 'TpiMarginThresScale'])
         if self.dumpMaxFormatSummaryTBL and (not testSwitch.CM_REDUCTION_REDUCE_PRINTDBLOGBIN):
            objMsg.printDblogBin(self.dut.dblData.Tables('P_VBAR_MAX_FORMAT_SUMMARY'), spcId)

         #calculate max density
         if testSwitch.FE_0232067_211428_VBAR_USE_DESPERADO_PLUS_FORMAT_PICKER:
            self.pickTPI(marginOverTPIM = 1) #allow to pick highest tpic plus -ve margin
         if testSwitch.FE_0257373_348085_ZONED_SERVO_CAPACITY_CALCULATION:
            self.sendFormatToDrive = True
            objMsg.printMsg('setFormat: checkMinimumCapability')
            self.setFormat("BOTH", maximize_zone = 1, programZonesWithZipperZonesOnly = 1, print_table = 0) # can only set the data zone with zipper zone..
            self.sendFormatToDrive = False
         maxDensity = self.getAvgDensity(zone0Margin=1)
         if testSwitch.FE_0256852_480505_DISPLAY_VBAR_MAX_CAPACITY_PER_HEAD:
            maxDriveCapacity = self.getDriveCapacity(zone0Margin=1, print_per_hd=1)
         else:
            maxDriveCapacity = self.getDriveCapacity(zone0Margin=1)
         if self.BpiFileCapacityCalc and testSwitch.FE_0261758_356688_LBR and (not testSwitch.CM_REDUCTION_REDUCE_PRINTMSG):
            objMsg.printMsg("sectorPerTrk = %s" % self.sectorPerTrk)
            objMsg.printMsg("TrkPerZone = %s" % self.TrkPerZone)

         # copy back temp space
         self.store['TpiPick'] = tempTpiPick
         self.store['BpiFormat'] = tempBpiFormat

      #judge if head is narrow head, if yes, force drive to low capacity
      if testSwitch.OEM_Waterfall_Enable == 1:
         maxDensity = 0.5
         objMsg.printMsg('OEM drive need to be forced to low capacity!')
         testSwitch.OEM_Waterfall_Enable = 0
      objMsg.printMsg('MaxDensity = %6.4f, TargetDensity = %6.4f, MaxDriveCapacity = %6.4f' % (maxDensity, self.capacityTarget, maxDriveCapacity))

      if maxDensity < self.capacityTarget: #if capacity not met, return fail
         return True


      # Verify minimum capabilities on each head
      failed = False

      if testSwitch.FE_0114266_231166_INTERPOLATE_SINGLE_ZONE_FAILED_VBAR_MEASURES:
         maxNumInterpolates = round(0.15 * self.numUserZones,0)
         for hd in xrange(self.numHeads):
            numInterpolates = 0
            for zn in xrange(self.numUserZones):
               marginChangeFromNominal = self.marginChangeFromNominal[getBpiHeadIndex(hd)][zn][0]
               if testSwitch.BPICHMS or testSwitch.FE_CONSOLIDATED_BPI_MARGIN:
                  bpifailed, bpi_interpolated = self.interpolateFailedMeasurement(hd, zn, 'BpiCapability', self.settings['BPIMarginThreshold'][hd][zn] + self.dut.BPIMarginThresholdAdjust[hd], marginChangeFromNominal, 'BpiInterpolated')
               else:
                  bpifailed, bpi_interpolated = self.interpolateFailedMeasurement(hd, zn, 'BpiCapability', self.settings['BPIMarginThreshold'][zn] + self.dut.BPIMarginThresholdAdjust[hd], marginChangeFromNominal, 'BpiInterpolated')
               tpifailed, tpi_interpolated = self.interpolateFailedMeasurement(hd, zn, 'TpiCapability', self.settings['TPIMarginThreshold'][zn] + self.dut.TPIMarginThresholdAdjust[hd], TPI_MIN, 'TpiInterpolated')
               failed = bpifailed or tpifailed or failed
               if tpi_interpolated or bpi_interpolated:
                  numInterpolates += 1

            if numInterpolates > maxNumInterpolates:
               failed = True
               objMsg.printMsg("Number of interpolated zones exceeded %d for head %d" % (maxNumInterpolates,hd))
      else:
         for hd in xrange(self.numHeads):
            for zn in xrange(self.numUserZones):
               pickerData = CVbarDataHelper(self, hd, zn)
               marginChangeFromNominal = self.marginChangeFromNominal[getBpiHeadIndex(hd)][zn][0]
               if testSwitch.BPICHMS or testSwitch.FE_CONSOLIDATED_BPI_MARGIN:
                  if pickerData['BpiCapability'] - (self.settings['BPIMarginThreshold'][hd][zn] + self.dut.BPIMarginThresholdAdjust[hd]) < marginChangeFromNominal:
                     failed = True
                     objMsg.printMsg('BPI capability fail hd %d zn %d' % (hd, zn))
               else:
                  if pickerData['BpiCapability'] - (self.settings['BPIMarginThreshold'][zn] + self.dut.BPIMarginThresholdAdjust[hd]) < marginChangeFromNominal:
                     failed = True
                     objMsg.printMsg('BPI capability fail hd %d zn %d' % (hd,zn))
               if pickerData['TpiCapability'] - (self.settings['TPIMarginThreshold'][zn] + self.dut.TPIMarginThresholdAdjust[hd]) < TPI_MIN:
                  failed = True
                  objMsg.printMsg('TPI capability fail hd %d zn %d' % (hd,zn))

      return failed

   #-------------------------------------------------------------------------------------------------------
   def performance(self):
      return mean(self.store['BpiPick'])

   #-------------------------------------------------------------------------------------------------------
   def calculateCapacity(self, totalCap = False, zoneCap = False, rawCap = False, nominalCap = False):
      NominalBPIFormat = 0
      sectorsPerTrack = []
      TracksPerZone = []
      ZnCap = []
      RawsectorsPerTrack = []
      RawTracksPerZone = []
      NominalsectorsPerTrack = []
      NominalTracksPerZone = []
      driveCapacityTotal = 0
      driveCapacityRaw = 0
      driveCapacityNominal = 0
      
      for hd in xrange(self.numHeads):
         for zn in xrange(self.numUserZones):
            gNumNominalTracksInZone = self.bpiFile.getNumNominalTracksInZone(self.baseformat[hd],zn,hd)
            gNumNominalSectorsPerTrack = self.bpiFile.getSectorsPerTrack(NominalBPIFormat,zn,hd)
            pickerData = CVbarDataHelper(self, hd, zn)
            pickerData['BpiFormat'] = self.getClosestBPITable(pickerData['BpiCapability'],zn,hd)
            
            if totalCap:
               sectors = self.bpiFile.getSectorsPerTrack(pickerData['BpiFormat'],zn,hd)
               sectorsPerTrack.append(sectors)
               if self.tracksPerBand[zn] > 1 :
                  tracks = (int(pickerData['TpiCapability']*gNumNominalTracksInZone)-(int(pickerData['TpiCapability']*gNumNominalTracksInZone)%self.tracksPerBand[zn]))
               else:
                  tracks = int(pickerData['TpiCapability']*gNumNominalTracksInZone)
               if self.tracksPerBand[zn] > 1 :
                  tracks = tracks-self.tracksPerBand[zn]
               TracksPerZone.append(tracks)
               driveCapacityTotal += sectors*tracks
               
            if zoneCap:
               ZnCap.append(tracks*sectors*self.sectorsize/float(1e9))
            
            if rawCap:
               RawSectors = int(pickerData['BpiCapability']*gNumNominalSectorsPerTrack)
               RawsectorsPerTrack.append(RawSectors)
               Rawtracks = int(pickerData['TpiCapability']*gNumNominalTracksInZone)
               if self.tracksPerBand[zn] > 1:
                  Rawtracks = Rawtracks - self.tracksPerBand[zn]
               RawTracksPerZone.append(Rawtracks)
               driveCapacityRaw += RawSectors*Rawtracks
            
            if nominalCap:
               NominalsectorsPerTrack.append(gNumNominalSectorsPerTrack)
               NominalTracksPerZone.append(gNumNominalTracksInZone)
               driveCapacityNominal += gNumNominalSectorsPerTrack*gNumNominalTracksInZone
            
      if totalCap:
         if verbose: 
            objMsg.printMsg('*'* 38 + ' Get Total Capacity --- ' + '*'*38)
            objMsg.printMsg("sectorsPerTrack = %s" % sectorsPerTrack)
            objMsg.printMsg("TracksPerZone = %s" % TracksPerZone)
         driveCapacityTotal = driveCapacityTotal*self.sectorsize/float(1e9)
         objMsg.printMsg("Calculated Total capacity = %s" % driveCapacityTotal)
         
      if rawCap:
         if verbose: 
            objMsg.printMsg('*'* 38 + ' Get Raw Capacity --- ' + '*'*38)
            nominalFormat = self.bpiFile.getNominalFormat()
            objMsg.printMsg("nominalFormat = %s" % nominalFormat)
            objMsg.printMsg("RawsectorsPerTrack = %s" % RawsectorsPerTrack)
            objMsg.printMsg("RawTracksPerZone = %s" % RawTracksPerZone)
         driveCapacityRaw = driveCapacityRaw*self.sectorsize/float(1e9)
         objMsg.printMsg("Calculated Raw capacity = %s" % driveCapacityRaw)

      if nominalCap:
         if verbose: 
            objMsg.printMsg('*'* 38 + ' Get Nominal Capacity --- ' + '*'*38)
            objMsg.printMsg("NominalsectorsPerTrack = %s" % NominalsectorsPerTrack)
            objMsg.printMsg("NominalTracksPerZone = %s" % NominalTracksPerZone)
         driveCapacityNominal = driveCapacityNominal*self.sectorsize/float(1e9)
         objMsg.printMsg("Calculated Nominal capacity = %s" % driveCapacityNominal)
      
      return driveCapacityTotal, ZnCap, driveCapacityRaw, driveCapacityNominal

   #-------------------------------------------------------------------------------------------------------
   def reportADCSummary(self):
      TableInfo = {}
            
      if verbose: objMsg.printMsg("Bpic = %s" % self.store['BpiCapability'])
      if verbose: objMsg.printMsg("Tpic = %s" % self.store['TpiCapability'])
      
      driveCapacityTotal, ZnCap, driveCapacityRaw, driveCapacityNominal = self.calculateCapacity(True,True,True,True)
      TableInfo.setdefault('Total', driveCapacityTotal)
      TableInfo.setdefault('RAW', driveCapacityRaw)
      TableInfo.setdefault('Nominal', driveCapacityNominal)

      AGBCap   = 0
      SpareCap = 0
      NetMCCap = 0
      RawMCCap = 0
      UMPCap   = 0
      TotalUMPCap   = 0

      if testSwitch.ADAPTIVE_GUARD_BAND:
         for hd in xrange(self.numHeads):
            for zn in [0]:
               AGBCap += ZnCap[(hd * self.numUserZones) + zn]

      if verbose: objMsg.printMsg('mediaCacheZone = %s' % (str(self.mediaCacheZone)))
      if verbose: objMsg.printMsg('All UMP_ZONE = %s' % (str(TP.UMP_ZONE[self.numUserZones])))

      TotalMCSectorsPerHead = []
      for hd in xrange(self.numHeads):
         TotalMCSectorsPerHead.append(sum([ZnCap[(hd * self.numUserZones) + zn] for zn in self.mediaCacheZone]))
         RawMCCap += TotalMCSectorsPerHead[hd]
      NetMCCap = min(TotalMCSectorsPerHead) * self.numHeads

      SpareCap = driveCapacityTotal * (1 - self.settings['PBA_TO_LBA_SCALER'])

      for hd in xrange(self.numHeads):
         for zn in TP.UMP_ZONE[self.numUserZones]:
            TotalUMPCap += ZnCap[(hd * self.numUserZones) + zn]

         for zn in TP.UMP_ZONE[self.numUserZones][0:(len(TP.UMP_ZONE[self.numUserZones])-1)]:
            UMPCap += ZnCap[(hd * self.numUserZones) + zn]

      if NetMCCap < self.settings['MEDIA_CACHE_CAPACITY']:
         NetADC = driveCapacityTotal - NetMCCap - SpareCap - AGBCap
      else:
         NetADC = driveCapacityTotal - self.settings['MEDIA_CACHE_CAPACITY'] - SpareCap - AGBCap
      TableInfo.setdefault('Net', NetADC)
      TableInfo.setdefault('NetMC', NetMCCap)
      TableInfo.setdefault('RawMC', RawMCCap)
      TableInfo.setdefault('AGB', AGBCap)
      TableInfo.setdefault('SpareParity', SpareCap)
      TableInfo.setdefault('UMP', UMPCap)
      TableInfo.setdefault('TotalUMP', TotalUMPCap)
      TableInfo.setdefault('TargetMC', self.settings['MEDIA_CACHE_CAPACITY'])
      TableInfo.setdefault('MaxTarget', self.settings['DRIVE_CAPACITY']-self.settings['MEDIA_CACHE_CAPACITY'])
      TableInfo.setdefault('NetTotal', driveCapacityTotal*self.settings['PBA_TO_LBA_SCALER'])

      try:
         curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
         spcId = self.spcIdHlpr.getSpcId('P_VBAR_ADC_SUMMARY')
         keys  = TableInfo.keys()
         keys.sort()
         for key in keys:
            self.dut.dblData.Tables('P_VBAR_ADC_SUMMARY').addRecord(
                  {
                     'SPC_ID'          : spcId,
                     'OCCURRENCE'      : occurrence,
                     'SEQ'             : curSeq,
                     'TEST_SEQ_EVENT'  : testSeqEvent,
                     'PARAMETER_NAME'  : key,
                     'DRV_CAPACITY'    : round(TableInfo[key], 3),
                  })
         objMsg.printDblogBin(self.dut.dblData.Tables('P_VBAR_ADC_SUMMARY'), spcId)
      except:
         objMsg.printMsg('*'* 38 + ' create P_VBAR_ADC_SUMMARY fail' + '*'*38)
         pass

   #-------------------------------------------------------------------------------------------------------
   def reportZSADCSummary(self):
      # TODO: test
      TableInfo = {}

      if verbose: objMsg.printMsg("Bpic = %s" % self.store['BpiCapability'])
      if verbose: objMsg.printMsg("Tpic = %s" % self.store['TpiCapability'])

      _, _, driveCapacityRaw, driveCapacityNominal = self.calculateCapacity(rawCap=True,nominalCap=True)
      TableInfo.setdefault('RAW', driveCapacityRaw)
      TableInfo.setdefault('Nominal', driveCapacityNominal)

      for table in ['P210_CAPACITY_DRIVE', TP.zoned_servo_zn_tbl['table_name']]:
         try:
            if not testSwitch.virtualRun:
               self.dut.dblData.Tables(table).deleteIndexRecords(1)
               self.dut.dblData.delTable(table, forceDeleteDblTable = 1)
         except: 
            pass
      displayZStable_prm = TP.PRM_DISPLAY_ZONED_SERVO_ZONE_TABLE_172.copy()
      displayZStable_prm.update({ 'spc_id': 10 })
      getVbarGlobalClass(CProcess).St(displayZStable_prm)
      getVbarGlobalClass(CProcess).St({'test_num':210,'CWORD1':8, 'SCALED_VAL': 10000, 'spc_id':10}) # do no apply scale
      colDict = self.dut.dblData.Tables('P210_CAPACITY_DRIVE').columnNameDict()
      row = self.dut.dblData.Tables('P210_CAPACITY_DRIVE').rowListIter(index=len(self.dut.dblData.Tables('P210_CAPACITY_DRIVE'))-1).next()
      DrvCap = float(row[colDict['DRV_CAPACITY']])
      TableInfo.setdefault('Total', DrvCap)
      if verbose: objMsg.printMsg("Total drv capacity(zone servo on) = %s" % DrvCap)

      # from FSO import dataTableHelper
      colDict = self.dut.dblData.Tables(TP.zoned_servo_zn_tbl['table_name']).columnNameDict()
      zstable = self.dut.dblData.Tables(TP.zoned_servo_zn_tbl['table_name']).rowListIter()
      ZnCap = [0,] * (self.numHeads * self.numUserZones)
      totaltracks = 0
      for row in zstable:
         hd = int(row[colDict['HD_LGC_PSN']])
         zn = int(row[colDict['DATA_ZONE']])
         trkNum = int(row[colDict['TRK_NUM']])
         ZnCap[(hd * self.numUserZones) + zn] += int(row[colDict['PBA_TRACK']]) * trkNum * self.sectorsize/float(1e9)
         if testSwitch.FE_0297446_348429_P_PRECISE_PARITY_ALLOCATION:
            totaltracks += trkNum
      if verbose: objMsg.printMsg("ZnCap: %s" % ZnCap)

      AGBCap   = 0
      RawMCCap = 0
      UMPCap   = 0
      TotalUMPCap   = 0
      TotalMCSectorsPerHead = []
      
      for hd in xrange(self.numHeads):
         if testSwitch.ADAPTIVE_GUARD_BAND:
            for zn in [0]:
               AGBCap += ZnCap[(hd * self.numUserZones) + zn]
               
         TotalMCSectorsPerHead.append(sum([ZnCap[(hd * self.numUserZones) + zn] for zn in self.mediaCacheZone]))
         RawMCCap += TotalMCSectorsPerHead[hd]
         
         for zn in TP.UMP_ZONE[self.numUserZones]:
            TotalUMPCap += ZnCap[(hd * self.numUserZones) + zn]
         for zn in TP.UMP_ZONE[self.numUserZones][0:(len(TP.UMP_ZONE[self.numUserZones])-1)]:
            UMPCap += ZnCap[(hd * self.numUserZones) + zn]
      
      if verbose: objMsg.printMsg('mediaCacheZone = %s' % (str(self.mediaCacheZone)))
      if verbose: objMsg.printMsg('All UMP_ZONE = %s' % (str(TP.UMP_ZONE[self.numUserZones])))
      
      NetMCCap = min(TotalMCSectorsPerHead) * self.numHeads
      SpareCap = DrvCap * (1 - self.settings['PBA_TO_LBA_SCALER'])
      if testSwitch.FE_0297446_348429_P_PRECISE_PARITY_ALLOCATION: # add the Parity Size
         if verbose: objMsg.printMsg('paritySize = %s' % (totaltracks * TP.ParitySec_perTrack * self.sectorsize/float(1e9)))
         SpareCap += (totaltracks * TP.ParitySec_perTrack * self.sectorsize/float(1e9))
      
      if NetMCCap < self.settings['MEDIA_CACHE_CAPACITY']:
         NetADC = DrvCap - NetMCCap - SpareCap - AGBCap
      else:
         NetADC = DrvCap - self.settings['MEDIA_CACHE_CAPACITY'] - SpareCap - AGBCap
      TableInfo.setdefault('Net', NetADC)
      TableInfo.setdefault('NetMC', NetMCCap)
      TableInfo.setdefault('RawMC', RawMCCap)
      TableInfo.setdefault('AGB', AGBCap)
      TableInfo.setdefault('SpareParity', SpareCap)
      TableInfo.setdefault('UMP', UMPCap)
      TableInfo.setdefault('TotalUMP', TotalUMPCap)
      TableInfo.setdefault('TargetMC', self.settings['MEDIA_CACHE_CAPACITY'])
      TableInfo.setdefault('MaxTarget', self.settings['DRIVE_CAPACITY']-self.settings['MEDIA_CACHE_CAPACITY'])
      TableInfo.setdefault('NetTotal', DrvCap - SpareCap)

      try:
         curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
         spcId = self.spcIdHlpr.getSpcId('P_VBAR_ADC_SUMMARY')
         keys  = TableInfo.keys()
         keys.sort()
         for key in keys:
            self.dut.dblData.Tables('P_VBAR_ADC_SUMMARY').addRecord(
                  {
                     'SPC_ID'          : spcId,
                     'OCCURRENCE'      : occurrence,
                     'SEQ'             : curSeq,
                     'TEST_SEQ_EVENT'  : testSeqEvent,
                     'PARAMETER_NAME'  : key,
                     'DRV_CAPACITY'    : round(TableInfo[key], 3),
                  })
         objMsg.printDblogBin(self.dut.dblData.Tables('P_VBAR_ADC_SUMMARY'), spcId)
      except:
         objMsg.printMsg('*'* 38 + ' create P_VBAR_ADC_SUMMARY fail' + '*'*38)
         pass
         
      # For More Info in the Log, avoid confusion as the parameter Name are not so meaningful
      objMsg.printMsg('%4.2fGb Total: Total Drive Capacity' % (DrvCap))
      objMsg.printMsg('%4.2fGb NetTotal: Total Drive Capacity excluding Spare and Parity' % (DrvCap - SpareCap))
      objMsg.printMsg('%4.2fGb Net: Total Drive Capacity excluding Spare, Parity and AGB' % (NetADC))
      #objMsg.printMsg('%4.2fGb TotalTarget: Total Needed Capacity for current nibblet including MC, Spare and Parity' % (self.settings['DRIVE_CAPACITY'] / self.settings['PBA_TO_LBA_SCALER']))

   #-------------------------------------------------------------------------------------------------------
   def pickBPITPI(self):
      """
      Pick the best BPI/TPgI settings for the given capacity point
      and capability matrix.  Based on Bruce Emo's algorithm
      """
      pickBPITPI_debug = 0
      printDbgMsg('*'* 38 + ' SMR FORMAT PICKER ' + '*'*38)

      self.zone0Margin = (not testSwitch.ADAPTIVE_GUARD_BAND) and 1 or 0
      self.z0FinalCapacity = 0

      if testSwitch.FE_0257373_348085_ZONED_SERVO_CAPACITY_CALCULATION:
         self.ZonesWithZipperZonesCapacity = 0

      if testSwitch.FE_0261758_356688_LBR and self.FindNZB:
         checkMinimumCapability_status = 0
      
      # Calculate the average capabilities for each head
      TPICap = [mean(self.getRecordForHead('TpiCapability',hd)) for hd in xrange(self.numHeads)]
      BPICap = [mean(self.getRecordForHead('BpiCapability',hd)) for hd in xrange(self.numHeads)]

      # Verify that the capabilities provide the target capacity at least
      if self.checkMinimumCapability(TPICap, BPICap):
         objMsg.printMsg('*'*40 + ' FAILED MINIMUM CAPABILITY ' + '*'*40)
         if testSwitch.FE_0261758_356688_LBR and self.FindNZB:
            checkMinimumCapability_status = ATPI_FAIL_CAPABILITY
         else:
            return ATPI_FAIL_CAPABILITY

      # Adjust for non-nominal capacity targets
      NormalizedTPICap = [TPICap[hd]/math.sqrt(self.capacityTarget) for hd in xrange(self.numHeads)]
      NormalizedBPICap = [BPICap[hd]/math.sqrt(self.capacityTarget) for hd in xrange(self.numHeads)]
      if not testSwitch.CM_REDUCTION_REDUCE_PRINTMSG:
         for hd in xrange(self.numHeads):
            objMsg.printMsg('TPICap=%.4f, BPICap=%.4f, Capacity=%.4f, RTPICap=%.4f, RBPICap=%.4f' % (TPICap[hd], BPICap[hd], self.capacityTarget, NormalizedTPICap[hd], NormalizedBPICap[hd]))

      # Compute TPI_Margin factor
      DrvMargin = mean(NormalizedTPICap) + mean(NormalizedBPICap) - 2
      objMsg.printMsg('TPIMarginFactor=%.4f DrvMargin=%.4f' % (self.settings['TPIMarginFactor'], DrvMargin))
      TPIMF = self.settings['TPIMarginFactor']  # TPIMarginFactor is set in the Niblet

      # Compute BPI_TPI_Compensation factor
      BPITPICompFactor = self.settings['BPITPICompensationFactor']
      objMsg.printMsg('BPITPICompFactor = %.4f' % BPITPICompFactor)

      # Compute TPI_Comp factor
      TPICompFactor = self.settings['TPICompensationFactor']
      objMsg.printMsg('TPICompFactor=%.4f' % TPICompFactor)

      # Compute BPI_Comp factor
      BPICompFactor = self.settings['BPICompensationFactor']

      # Report Compensation factors
      #objMsg.printMsg('BPITPICompFactor = %.4f, TPICompFactor = %.4f, BPICompFactor = %.4f' %
      #                 (BPITPICompFactor,TPICompFactor,BPICompFactor))

      # Calculate Adjusted Capabilities
      adjustedBPICap = {}
      adjustedTPICap = {}
      objMsg.printMsg('%2s%8s%11s%8s%11s' % ('Hd','BPICap','AdjBPICap','TPICap','AdjTPICap'))

      for hd in xrange(self.numHeads):
         adjustedTPICap[hd] = ((TPICap[hd]- mean(TPICap))*TPICompFactor) + mean(TPICap)
         adjustedBPICap[hd] = ((BPICap[hd]- mean(BPICap))*BPICompFactor) + mean(BPICap)
         adjustedBPITPIDelta= (adjustedBPICap[hd]-adjustedTPICap[hd]) * (1.0-BPITPICompFactor) / 2.0
         adjustedTPICap[hd] += adjustedBPITPIDelta
         adjustedBPICap[hd] -= adjustedBPITPIDelta
         objMsg.printMsg('%2d%8.4f%9.4f%10.4f%9.4f' % (hd, BPICap[hd], adjustedBPICap[hd], TPICap[hd], adjustedTPICap[hd]))

      # Compute density
      density = mean([adjustedTPICap[hd] * adjustedBPICap[hd] for hd in xrange(self.numHeads)])
      objMsg.printMsg('Adj density: %6.4f' % density)
      
      # Because 1.0 does not always equal to the native target capacity, need to scale so that the excess margin
      # will not be too far away
      _, _, _, driveCapacityNominal = self.calculateCapacity(nominalCap=True)
      objMsg.printMsg('Approximate Capacity: %6.4f' % (density * driveCapacityNominal))
      density *= driveCapacityNominal / 1000.0
      objMsg.printMsg('Scaled density: %6.4f' % density)
      
      # Calculate TPI margin
      totalMargin = (density / self.capacityTarget) - 1.0
      objMsg.printMsg('Total Margin: %6.4f' % totalMargin)
      if testSwitch.FE_0297451_348429_P_USE_ACTUAL_DENSITY_IN_INITIAL_PICKER:
         # This routine will invoke initial picker with zero margin adjustment so as to be able to get the actual density
         for hd in xrange(self.numHeads):
            for zn in xrange(self.numUserZones):
               pickerData = CVbarDataHelper(self, hd, zn)
               pickerData['BpiMarginTarget'] = 0.0
               pickerData['TpiMarginTarget'] = 0.0
         self.pickTPI()
         self.pickBPI()
         density = self.getAvgDensity(zone0Margin=1) # this already takes into consideration spare/parity
          
         objMsg.printMsg('Using Accurate Density: %6.4f' % density)
         totalMargin = (density / self.capacityTarget) - 1.0
         objMsg.printMsg('Total Accurate Margin: %6.4f' % totalMargin)
          
      R = 1/TPIMF - 1.0 # R = ratio of BPI margin to TPI margin
      TPIMargin = (math.sqrt((1+R)*(1+R)+4*R*totalMargin)-(1+R))/(2*R)
      if TPIMargin < 0.0:
         TPIMargin = R * TPIMargin
      objMsg.printMsg('TPI Margin: %6.4f' % TPIMargin)

      # Calculate BPI Margin
      if TPIMargin > 0.0:
         BPIMargin = R*(TPIMargin)
      else:
         BPIMargin = (TPIMargin)/R
      objMsg.printMsg('BPI Margin: %6.4f' % BPIMargin)

      if not testSwitch.FAST_2D_VBAR:
         # Initialize the margin targets
         for hd in xrange(self.numHeads):
            for zn in xrange(self.numUserZones):
               pickerData = CVbarDataHelper(self, hd, zn)
               pickerData['BpiMarginTarget'] = BPIMargin + self.settings['BpiTargetMarginAdjustment'][zn]
               pickerData['TpiMarginTarget'] = TPIMargin + self.settings['TpiTargetMarginAdjustment'][zn]
      else:
         # Initialize the margin targets
         if not testSwitch.VBAR_ADP_EQUAL_ADC:
            for hd in xrange(self.numHeads):
               for zn in xrange(self.numUserZones):
                  pickerData = CVbarDataHelper(self, hd, zn)
                  pickerData['BpiMarginTarget'] = BPIMargin + self.settings['BpiTargetMarginAdjustment'][zn]
                  pickerData['TpiMarginTarget'] = TPIMargin + self.settings['TpiTargetMarginAdjustment'][zn] - pickerData['TpiMarginThresScale']
         else:
            self.store['BpiMarginTarget'] = array('f', [0.0]*self.numUserZones*self.numHeads)
            self.store['TpiMarginTarget'] = array('f', [0.0]*self.numUserZones*self.numHeads)

      # Pick TPI for each head and zone and display the data
      printDbgMsg('Initial Picks')
      self.pickTPI( marginOverTPIM = testSwitch.VBAR_ADP_EQUAL_ADC )
      self.pickBPI()
      if testSwitch.FE_0261758_356688_LBR and self.FindNZB:
         if debug_LBR:
            bpiFilegetNumNominalTracksInZone = []
            objMsg.printMsg("Hd  Zn  Tpic      Tpip      BsizeP     TPs       TPd       TPB  NBands  STrkPitch  GTrkPitch  TrkPitch  TrkGuard  NNomTrkU  NNomTrk  NLogTrk  SMargin   OPNNomTrkU  OPTPitch  OPTGuard")
            for hd in xrange(self.numHeads):
               for zn in xrange(self.numUserZones):
                  bpiFilegetNumNominalTracksInZone.append(self.bpiFile.getNumNominalTracksInZone(0,zn))
                  self.calculatenumNominalTracksUsed(hd, zn, self.NominalZB[hd][zn]['TRK_NUM'], self.getRecord('NumBands',hd,zn))
            objMsg.printMsg("bpiFilegetNumNominalTracksInZone = %s" % bpiFilegetNumNominalTracksInZone)
         maxDensity = self.getAvgDensity(zone0Margin=1)
         maxDriveCapacity = self.getDriveCapacity(zone0Margin=1)
         printDbgMsg("OldZB: sectorPerTrk = %s" % self.sectorPerTrk)
         printDbgMsg("OldZB: TrkPerZone = %s" % self.TrkPerZone)
         objMsg.printMsg('OldZB: MaxDensity = %6.4f, TargetDensity = %6.4f, MaxDriveCapacity = %6.4f' % (maxDensity, self.capacityTarget, maxDriveCapacity))                           
         self.FindNewZnBoundary()
         self.FindNZB = 0         
         if checkMinimumCapability_status != 0:
            return checkMinimumCapability_status
            
      if testSwitch.FE_0261758_356688_LBR and self.LBR:
         maxDensity = self.getAvgDensity(zone0Margin=1)
         maxDriveCapacity = self.getDriveCapacity(zone0Margin=1)
         printDbgMsg("NEWZB: sectorPerTrk = %s" % self.sectorPerTrk)
         printDbgMsg("NEWZB: TrkPerZone = %s" % self.TrkPerZone)
         objMsg.printMsg('NEWZB: MaxDensity = %6.4f, TargetDensity = %6.4f, MaxDriveCapacity = %6.4f' % (maxDensity, self.capacityTarget, maxDriveCapacity))      
         
      if testSwitch.FE_0257373_348085_ZONED_SERVO_CAPACITY_CALCULATION:
         self.sendFormatToDrive = True
         objMsg.printMsg('pickBPITPI: setFormat')
         self.setFormat("BOTH", maximize_zone = 1, programZonesWithZipperZonesOnly = 1, print_table = 0)
      if testSwitch.VBAR_ADP_EQUAL_ADC and testSwitch.FE_0243269_348085_FIX_BPI_TPI_WATERFALL and self.getAvgDensity(zone0Margin=1) < self.capacityTarget:
         return ATPI_FAIL_CAPACITY
      #If AGB is on, zone 0 is excluded from tuning capacity
      start_zone = testSwitch.ADAPTIVE_GUARD_BAND and 1 or 0
      if testSwitch.FE_0299263_348429_P_USE_FULL_AGB_CAPACITY_BY_DEFAULT:
         start_zone = 0 # Override to zone 0
         self.zone0Margin = 1 # Override the Zone0Margin to be 1 so as to always use full extent of AGB
         self.z0FinalCapacity = self.calculateAGBSize() 
      self.active_zones = [(hd, zn) for hd in xrange(objDut.imaxHead) for zn in xrange(start_zone, objDut.numZones)]
      active_tuned_zones = [zn for zn in xrange(start_zone, objDut.numZones)]

      if pickBPITPI_debug:
         objMsg.printMsg('self.active_zones %s' % str(self.active_zones))
         objMsg.printMsg('active_tuned_zones %s' % str(active_tuned_zones))
      if not testSwitch.VBAR_ADP_EQUAL_ADC: 
         objMsg.printMsg("PICKER LIMITS: capacityTarget = %1.4f, BPIMinAve = %1.4f, BPIMaxAve = %1.4f" % (self.capacityTarget,self.settings['BPIMinAvg'],self.settings['BPIMaxAvg']))
         objMsg.printMsg("OP_MODE -> 'C'  = Capacity Adjust   , 'P' = Performance Adjust, 'CP'  = Capacity Adjust for Performance Constraints")
         objMsg.printMsg("OP_MODE -> 'M'  = Media Cache Adjust, 'U' = UMP Adjust        , 'CMU' = Capacity Adjust for Media Cache and UMP Constraints")
         objMsg.printMsg("OP_MODE -> 'CA' = AGB adjust")
         # --------------------------------------------------------------------------------
         # Tweak the format, BPI and TPI, to meet capacity and performance specifications.
         # --------------------------------------------------------------------------------

         # remove excess Capacity without zone 0
         printDbgMsg("Removing Excess Capacity")
         self.recordData['OP_MODE'] = 'C'               # Indicate adjustment being made for capacity reasons.
         while (self.getAvgDensity(self.zone0Margin) > self.capacityTarget) and self.decreaseDensity('ANY', active_tuned_zones):  # a bit hokey.  Relying on conditional execution
            if testSwitch.FE_0171684_007867_DISPLAY_PICKER_AS_TBL:
               self.getAvgDensity(self.zone0Margin)  # to reflex the updated capacity
               self.updatePickerFmtAdjustTbl()
            else:
               pass

         status = ATPI_PASS

         # Increase density to meet capacity exclude zone 0
         printDbgMsg("Increasing Density to meet Capacity exclude zone 0")
         while self.getAvgDensity(self.zone0Margin) < self.capacityTarget:
            if not self.increaseDensity('ANY', active_tuned_zones):
               status = ATPI_FAIL_CAPACITY
               break
            if testSwitch.FE_0171684_007867_DISPLAY_PICKER_AS_TBL:
               self.getAvgDensity(self.zone0Margin)  # to reflex the updated capacity
               self.updatePickerFmtAdjustTbl()

         if status == ATPI_FAIL_CAPACITY :
            printDbgMsg("Using zone0 ")
            if testSwitch.ADAPTIVE_GUARD_BAND and not testSwitch.FE_0299263_348429_P_USE_FULL_AGB_CAPACITY_BY_DEFAULT:
               #evaluate capacity with max AGB zone 0 meeting capacity
               self.zone0Margin = 1
               self.recordData['OP_MODE'] = 'CA'               # Indicate adjustment being made for capacity reasons.
               printDbgMsg("AGB: self.zone0Margin %f, self.getAvgDensity(self.zone0Margin) %f" % (self.zone0Margin, self.getAvgDensity(self.zone0Margin)))
               #round down to 6 decimal points for density calculation to avoid short of capacity latter part
               if (float(int(self.getAvgDensity(self.zone0Margin)*1000000))/1000000) >= self.capacityTarget:
                  if testSwitch.FE_0125707_340210_CAP_FROM_BPIFILE:
                     excess_agb_capacity = ( (float(int(self.getAvgDensity(self.zone0Margin)*1000000))/1000000) - self.capacityTarget  ) * self.bpiFile.getNominalCapacity()
                  else:
                     excess_agb_capacity = ( (float(int(self.getAvgDensity(self.zone0Margin)*1000000))/1000000) - self.capacityTarget ) * float(TP.VbarCapacityGBPerHead) * float(self.numHeads)

                  # Calculate required G needed from AGB zone
                  self.z0FinalCapacity = self.calculateAGBSize() - (excess_agb_capacity)
                  self.zone0Margin = self.z0FinalCapacity/self.calculateAGBSize()

                  #if testSwitch.FE_0171684_007867_DISPLAY_PICKER_AS_TBL:
                  #   self.getAvgDensity(self.zone0Margin)  # to reflex the updated capacity
                  #   self.updatePickerFmtAdjustTbl()

                  status = ATPI_PASS
                  printDbgMsg("AGB: excess_agb_capacity %f" % excess_agb_capacity)
                  printDbgMsg("AGB: self.zone0Margin %f, self.getAvgDensity(self.zone0Margin) %f, self.capacityTarget %6.4f" % (self.zone0Margin, self.getAvgDensity(self.zone0Margin), self.capacityTarget))
               else : #with AGB zone 0 still not able to meet capacity
                  return status

            else : #not AGB return failure
               return status

         printDbgMsg("Final: AGB self.zone0Margin %f, self.z0FinalCapacity %f" % (self.zone0Margin, self.z0FinalCapacity))
         # Validate that we have met the media cache requirement.
         # if low, then increase density in the media cache zone
         if (self.settings['MEDIA_CACHE_CAPACITY'] > 0):
            self.recordData['OP_MODE'] = 'M'               # Indicate adjustment being made for capacity reasons.
            while self.calculateMediaCacheSize() < self.settings['MEDIA_CACHE_CAPACITY']:
               if not self.increaseMediaCacheDensity('ANY'):
                  if verbose:
                     self.findMargin('ANY','Best',report=True)

                  objMsg.printMsg('*'*40 + ' FAILED MEDIA CACHE CAPACITY ' + '*'*40)

                  if self.calculateMediaCacheSize() < self.settings['MEDIA_CACHE_CAPACITY_SPEC']:
                     if not testSwitch.CM_REDUCTION_REDUCE_PRINTDBLOGBIN:
                        objMsg.printDblogBin(self.dut.dblData.Tables('P_VBAR_PICKER_FMT_ADJUST'), self.spcId)
                     return ATPI_FAIL_CAPACITY
                  else:
                     objMsg.printMsg('*'*40 + ' LET GO AS STILL MEETING MEDIA_CACHE_CAPACITY_SPEC ' + '*'*40)
                     break
               if testSwitch.FE_0171684_007867_DISPLAY_PICKER_AS_TBL:
                  self.calculateMediaCacheSize() # to reflex the updated capacity for MC
                  self.updatePickerFmtAdjustTbl()

         if (self.settings['UMP_CAPACITY'] > 0):
            self.recordData['OP_MODE'] = 'U'               # Indicate adjustment being made for capacity reasons.
            while self.calculateUMPSize() < self.settings['UMP_CAPACITY']:
               if not self.increaseUMPDensity('ANY'):
                  if verbose:
                     self.findMargin('ANY','Best',report=True)

                  objMsg.printMsg('*'*40 + ' FAILED UMP CAPACITY = %2.1f' % self.calculateUMPSize() + '*'*40)

                  if self.calculateUMPSize() < self.settings['UMP_CAPACITY_SPEC']:
                     if not testSwitch.CM_REDUCTION_REDUCE_PRINTDBLOGBIN:
                        objMsg.printDblogBin(self.dut.dblData.Tables('P_VBAR_PICKER_FMT_ADJUST'), self.spcId)
                     return ATPI_FAIL_CAPACITY
                  else:
                     objMsg.printMsg('*'*40 + ' LET GO AS STILL MEETING UMP_CAPACITY_SPEC ' + '*'*40)
                     break

               if testSwitch.FE_0171684_007867_DISPLAY_PICKER_AS_TBL:
                  self.calculateUMPSize()  # to reflex the updated capacity for UMP
                  self.updatePickerFmtAdjustTbl()

         # Freeze the MC and UMP zones.
         zonesToAdjust = self.userZonesExcludeUMP

         printDbgMsg("Removing Excess Capacity. (Optimizing Capacity After MC and UMP).")
         self.recordData['OP_MODE'] = 'CMU'               # Indicate adjustment being made for capacity reasons.
         # Return back the margin to others zone if the MC zone or UMP capacity is being increased.
         while (self.getAvgDensity(self.zone0Margin) > self.capacityTarget) and self.decreaseDensity('ANY',zonesToAdjust):  # a bit hokey.  Relying on conditional execution
            if testSwitch.FE_0171684_007867_DISPLAY_PICKER_AS_TBL:
               self.getAvgDensity(self.zone0Margin)
               self.updatePickerFmtAdjustTbl()
            else:
               pass

         # Increase density to meet capacity exclude zone 0
         printDbgMsg("Increasing Density to meet Capacity (Optimizing Capacity After MC and UMP)")
         while self.getAvgDensity(self.zone0Margin) < self.capacityTarget:
            if not self.increaseDensity('ANY',zonesToAdjust):
               status = ATPI_FAIL_CAPACITY
               break
            if testSwitch.FE_0171684_007867_DISPLAY_PICKER_AS_TBL:
               self.getAvgDensity(self.zone0Margin)
               self.updatePickerFmtAdjustTbl()

         self.recordData['OP_MODE'] = 'P'               # Indicate adjustment being made for capacity reasons.
         # Increase BPI if Performance isn't met
         objMsg.printMsg("Checking Performance: %f <= %f <= %f" % (self.settings['BPIMinAvg'],self.performance(),self.settings['BPIMaxAvg']))
         while self.performance() < self.settings['BPIMinAvg']:
            if not self.increaseDensity('BPI'):
               objMsg.printMsg('*'*40 + ' FAILED PERFORMANCE ' + '*'*40)
               return ATPI_FAIL_PERFORMANCE
            if testSwitch.FE_0171684_007867_DISPLAY_PICKER_AS_TBL:
               self.getAvgDensity(self.zone0Margin)
               self.updatePickerFmtAdjustTbl()

         # Decrease BPI if average BPI is greater than max average allowed
         while self.performance() > self.settings['BPIMaxAvg']:
            if not self.decreaseDensity('BPI',zonesToAdjust):
               break
            if testSwitch.FE_0171684_007867_DISPLAY_PICKER_AS_TBL:
               self.getAvgDensity(self.zone0Margin)
               self.updatePickerFmtAdjustTbl()

         # Increase TPI if average density less than target capacity
         self.recordData['OP_MODE'] = 'CP'               # Indicate adjustment being made for capacity reasons.
         while self.getAvgDensity(self.zone0Margin) < self.capacityTarget:
            if not self.increaseDensity('TPI', zonesToAdjust):
               objMsg.printMsg('*'*27 + ' FAILED CAPACITY DUE TO PERFORMANCE MAX LIMIT ' + '*'*27)
               return ATPI_FAIL_PERFORMANCE
            if testSwitch.FE_0171684_007867_DISPLAY_PICKER_AS_TBL:
               self.getAvgDensity(self.zone0Margin)
               self.updatePickerFmtAdjustTbl()

         # Decrease TPI (Remove excess TPI) until capacity is just met
         bDecreasedTPI = False
         while self.getAvgDensity(self.zone0Margin) > self.capacityTarget:
            if not self.decreaseDensity('TPI', zonesToAdjust):
               break
            if testSwitch.FE_0171684_007867_DISPLAY_PICKER_AS_TBL:
               self.getAvgDensity(self.zone0Margin)
               self.updatePickerFmtAdjustTbl()

         # undo TPI change until capacity is met
         while self.getAvgDensity(self.zone0Margin) < self.capacityTarget:
            if not self.increaseDensity('TPI', zonesToAdjust):
               objMsg.printMsg('*'*27 + ' FAILED CAPACITY DUE TO PERFORMANCE MAX LIMIT ' + '*'*27)
               return ATPI_FAIL_CAPACITY
            if testSwitch.FE_0171684_007867_DISPLAY_PICKER_AS_TBL:
               self.getAvgDensity(self.zone0Margin)
               self.updatePickerFmtAdjustTbl()

      if testSwitch.FE_0171684_007867_DISPLAY_PICKER_AS_TBL:
         # Report the accumulated picker data.
         if pickBPITPI_debug == 1 and (not testSwitch.CM_REDUCTION_REDUCE_PRINTDBLOGBIN):
            objMsg.printDblogBin(self.dut.dblData.Tables('P_VBAR_PICKER_FMT_ADJUST'), self.spcId)
         # Update the log with the final Picker results.
         self.reportPickerResults()
      else:
         objMsg.printMsg('Final Density: %6.4f' % self.getAvgDensity(self.zone0Margin))
            
      if testSwitch.FE_0261758_356688_LBR and self.LBR:
         self.SetZnBoundary()   # update new zone boundary to RAP
                   
      self.sendFormatToDrive = True
      self.BpiFileCapacityCalc = False

      #Force to update by head by zone the BPI config as the T176 need all zone SgateToRgate timing reload back to default
      if testSwitch.FORCE_UPDATE_BPI_ALL_HEADS_ALL_ZONES:
         self.store['AdjustedBpiFormat'] = array('c', ['T']*self.numUserZones*self.numHeads)

      if testSwitch.FAST_2D_S2D_TEST:
         self.setFormat("BOTH", maximize_zone = 0, \
            consolidateByZone = testSwitch.FE_0262424_504159_ST210_SETTING_FORMAT_IN_ZONE)
      else:
         self.setFormat("BOTH", consolidateByZone = testSwitch.FE_0262424_504159_ST210_SETTING_FORMAT_IN_ZONE)

      # Compute and optionally print the data to the log, based on log size reduction switch.
      self.computeMargins()

      if testSwitch.DISPLAY_SMR_FMT_SUMMARY and (not testSwitch.CM_REDUCTION_REDUCE_PRINTDBLOGBIN):
         # All heads/zones have been processed.  Dump a summary of the format information for the drive.
         objMsg.printDblogBin(self.dut.dblData.Tables('P_SMR_FORMAT_SUMMARY'), self.spcId_SMR_FMT)

      self.updateSummaryByZone()
      self.updateSummaryByHead()
      self.SetWFT()

      if testSwitch.FE_0279297_348085_PROG_MC_UMP_IN_RAP:
         # Program the MC and UMP size...
         getVbarGlobalClass(CProcess).St({'test_num': 172, 'prm_name': 'prm_default_mc_ump_size_172', 'CWORD1':57, 'timeout': 1200,})
         getVbarGlobalClass(CProcess).St({'test_num': 178, 'prm_name': 'prm_prog_mc_178', 'CWORD1':0x0220, 'MEDIA_CACHE_SIZE': int(self.settings['MEDIA_CACHE_SIZE_RAP']),'UMP_SIZE': int(self.settings['UMP_CAPACITY_RAP']), 'timeout': 1200, 'spc_id': 0,})
         getVbarGlobalClass(CProcess).St({'test_num': 172, 'prm_name': 'prm_mc_size_172', 'CWORD1':57, 'timeout': 1200,})

      # Write RAP and SAP data to flash
      getVbarGlobalClass(CProcess).St({'test_num': 178, 'prm_name': 'SAVE SAP AND RAP to Flash', 'CWORD1':0x0620, 'timeout': 1200, 'spc_id': 0,})

      # Post final capacity to FIS
      getVbarGlobalClass(CProcess).St({'test_num':210,'CWORD1':8, 'SCALED_VAL': int(self.settings['PBA_TO_LBA_SCALER'] * 10000), 'spc_id':1})

      return ATPI_PASS

   #-------------------------------------------------------------------------------------------------------
   def reportPickerResults(self):

      if self.sectorsize == 4096:
         capacityGB = self.settings['DRIVE_CAPACITY_4K']
      else:
         capacityGB = self.settings['DRIVE_CAPACITY']

      self.dut.dblData.Tables('P_VBAR_PICKER_RESULTS').addRecord({
            'SPC_ID'            : self.spcId,
            'OCCURRENCE'        : self.recordData['OCCURRENCE'],
            'SEQ'               : self.dut.objSeq.getSeq(),
            'TEST_SEQ_EVENT'    : 1,
            'TARGET_CAPACITY'   : round(self.capacityTarget,4),
            'FINAL_DENSITY'     : round(self.getAvgDensity(self.zone0Margin),4),
            'TARGET_CAP_GB'     : round(capacityGB,4),
            'COMPUTED_CAP_GB'   : round(float(self.getDriveCapacity(self.zone0Margin)),4),
            'MIN_BPI_AVE_LIMIT' : round(self.settings['BPIMinAvg'],2),
            'BPI_AVE'           : round(self.performance(),3),
            'MAX_BPI_AVE_LIMIT' : round(self.settings['BPIMaxAvg'],2)
           })
      if not testSwitch.CM_REDUCTION_REDUCE_PRINTDBLOGBIN:
         objMsg.printDblogBin(self.dut.dblData.Tables('P_VBAR_PICKER_RESULTS'), self.spcId)

   #-------------------------------------------------------------------------------------------------------
   def updateSummaryByZone(self):
      curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)

      spcId = self.spcIdHlpr.getSpcId('P_VBAR_FORMAT_SUMMARY')

      for hd in xrange(self.numHeads):
         for zn in xrange(self.numUserZones):
            pickerData = CVbarDataHelper(self, hd, zn)
            if testSwitch.FE_0114266_231166_INTERPOLATE_SINGLE_ZONE_FAILED_VBAR_MEASURES:
               self.dut.dblData.Tables('P_VBAR_FORMAT_SUMMARY').addRecord(
                     {
                        'SPC_ID'          : spcId,
                        'OCCURRENCE'      : occurrence,
                        'SEQ'             : curSeq,
                        'TEST_SEQ_EVENT'  : testSeqEvent,
                        'HD_PHYS_PSN'     : self.dut.LgcToPhysHdMap[hd],
                        'DATA_ZONE'       : zn,
                        'HD_LGC_PSN'      : hd,
                        'BPI_CAP'         : round(pickerData['BpiCapability'], 4),
                        'BPI_INTERPOLATED': pickerData['BpiInterpolated'],
                        'BPI_PICK'        : round(pickerData['BpiPick'], 4),
                        'BPI_MRGN'        : round(pickerData['BpiMargin'], 4),
                        'BPI_TABLE_NUM'   : pickerData['BpiFormat'],
                        'TPI_CAP'         : round(pickerData['TpiCapability'], 4),
                        'TPI_INTERPOLATED': pickerData['TpiInterpolated'],
                        'TPI_PICK'        : round(pickerData['TpiPick'], 4),
                        'TPI_MRGN'        : round(pickerData['TpiMargin'], 4),
                        'TPI_TABLE_NUM'   : pickerData['TpiFormat'],
                     })
            else:
               self.dut.dblData.Tables('P_VBAR_FORMAT_SUMMARY').addRecord(
                     {
                        'SPC_ID'          : spcId,
                        'OCCURRENCE'      : occurrence,
                        'SEQ'             : curSeq,
                        'TEST_SEQ_EVENT'  : testSeqEvent,
                        'HD_PHYS_PSN'     : self.dut.LgcToPhysHdMap[hd],
                        'DATA_ZONE'       : zn,
                        'HD_LGC_PSN'      : hd,
                        'BPI_CAP'         : round(pickerData['BpiCapability'], 4),
                        'BPI_INTERPOLATED': 'N',
                        'BPI_PICK'        : round(pickerData['BpiPick'], 4),
                        'BPI_MRGN'        : round(pickerData['BpiMargin'], 4),
                        'BPI_TABLE_NUM'   : pickerData['BpiFormat'],
                        'TPI_CAP'         : round(pickerData['TpiCapability'], 4),
                        'TPI_INTERPOLATED': 'N',
                        'TPI_PICK'        : round(pickerData['TpiPick'], 4),
                        'TPI_MRGN'        : round(pickerData['TpiMargin'], 4),
                        'TPI_TABLE_NUM'   : pickerData['TpiFormat'],
                     })
      if not testSwitch.CM_REDUCTION_REDUCE_PRINTDBLOGBIN:
         objMsg.printDblogBin(self.dut.dblData.Tables('P_VBAR_FORMAT_SUMMARY'), spcId)

   #-------------------------------------------------------------------------------------------------------
   def updateSummaryByHead(self):
      curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
      spcId = self.spcIdHlpr.getSpcId('P_VBAR_FORMAT_SUMMARY')  # Share a common spc_id
      for hd in xrange(self.numHeads):
         BpiCap    = self.getRecordForHead('BpiCapability',hd)
         TpiCap    = self.getRecordForHead('TpiCapability',hd)
         BpiMargin = self.getRecordForHead('BpiMargin',hd)
         TpiMargin = self.getRecordForHead('TpiMargin',hd)


         self.dut.dblData.Tables('P_VBAR_CAP_SUMMARY_BY_HD').addRecord(
            {
                     'SPC_ID'          : spcId,
                     'OCCURRENCE'      : occurrence,
                     'SEQ'             : curSeq,
                     'TEST_SEQ_EVENT'  : testSeqEvent,
                     'HD_PHYS_PSN'     : self.dut.LgcToPhysHdMap[hd],
                     'HD_LGC_PSN'      : hd,
                     'BPI_CAP_AVG'     : round(mean(BpiCap), 4),
                     'BPI_CAP_MIN'     : round(min(BpiCap), 4),
                     'BPI_MRGN_AVG'    : round(mean(BpiMargin), 4),
                     'BPI_MRGN_MIN'    : round(min(BpiMargin), 4),
                     'VZB_TABLE'       : self.baseformat[hd],
                     'TPI_CAP_AVG'     : round(mean(TpiCap), 4),
                     'TPI_CAP_MIN'     : round(min(TpiCap), 4),
                     'TPI_MRGN_AVG'    : round(mean(TpiMargin), 4),
                     'TPI_MRGN_MIN'    : round(min(TpiMargin), 4),
            })

   #-------------------------------------------------------------------------------------------------------
   def getDataZonesWithZipperZonesDriveCapacity(self):
      #getVbarGlobalClass(CProcess).St(TP.PRM_DISPLAY_ZONED_SERVO_ZONE_TABLE_172) # debug only
      params = {'test_num':210,'CWORD2':0x800, 'SCALED_VAL': int(self.settings['PBA_TO_LBA_SCALER'] * 10000), 'spc_id' : -1}
      zone_mask_low = 0
      zone_mask_high = 0
      for zone in TP.DEFAULT_ZONES_WITH_ZIPPER:
         if zone < 32:
            zone_mask_low |= (1 << zone)
         else:
            zone_mask_high |= (1 << (zone - 32))

      params['ZONE_MASK'] = getVbarGlobalClass(CUtility).ReturnTestCylWord(zone_mask_low)
      params['ZONE_MASK_EXT'] = getVbarGlobalClass(CUtility).ReturnTestCylWord(zone_mask_high)
      getVbarGlobalClass(CProcess).St(params)
      colDict = self.dut.dblData.Tables('P210_CAPACITY_ZWZ_DRIVE').columnNameDict()
      row = self.dut.dblData.Tables('P210_CAPACITY_ZWZ_DRIVE').rowListIter(index=len(self.dut.dblData.Tables('P210_CAPACITY_ZWZ_DRIVE'))-1).next()
      return float(row[colDict['CAPACITY']])

   #-------------------------------------------------------------------------------------------------------
   ###########Override parent getDriveCapacity#############################################################
   def getDriveCapacity(self, zone0Margin = 1, debug_capacity =0, print_per_hd=0):
      if self.BpiFileCapacityCalc:
         #calculate the number of sectors per zone
         sectorsPerTrack = [self.bpiFile.getSectorsPerTrack(self.getRecord('BpiFormat',hd,zn),zn,hd) for hd in xrange(self.numHeads) for zn in xrange(self.numUserZones)]
         TracksPerZone = self.getTracksPerZone()
         numSectorInZone0 = 0

         if testSwitch.FE_0261758_356688_LBR:
            self.sectorPerTrk = deepcopy(sectorsPerTrack)
            self.TrkPerZone = deepcopy(TracksPerZone)
         
         if testSwitch.FE_0256852_480505_DISPLAY_VBAR_MAX_CAPACITY_PER_HEAD and print_per_hd:
            curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
            spcId = self.spcIdHlpr.getSpcId('P_VBAR_FORMAT_SUMMARY')  # Share a common spc_id
            for hd in range(self.numHeads) :
               hd_sectorsPerTrack=sectorsPerTrack[hd*self.numUserZones:(hd+1)*self.numUserZones]
               hd_TracksPerZone=TracksPerZone[hd*self.numUserZones:(hd+1)*self.numUserZones]
               numsectors = sum(map(operator.mul, hd_sectorsPerTrack, hd_TracksPerZone))
               driveCapacity = self.settings['PBA_TO_LBA_SCALER'] * numsectors
               if testSwitch.FE_0297446_348429_P_PRECISE_PARITY_ALLOCATION:
                  driveCapacity -= sum(hd_TracksPerZone)*TP.ParitySec_perTrack
               driveCapacity = driveCapacity*self.sectorsize/float(1e9)
               #objMsg.printMsg("Hd %d Capa = %f GB" % (hd,driveCapacity))
               self.dut.dblData.Tables('P210_CAPACITY_HD2').addRecord({
                     'SPC_ID'            : spcId,
                     'OCCURRENCE'        : occurrence,
                     'SEQ'               : curSeq,
                     'TEST_SEQ_EVENT'    : testSeqEvent,
                     'HD_PHYS_PSN'       : self.dut.LgcToPhysHdMap[hd],
                     'HD_LGC_PSN'        : hd,
                     'HD_CAPACITY'       : round(driveCapacity,4)
                    })
            objMsg.printMsg("MaxCapa per Hd")
            objMsg.printDblogBin(self.dut.dblData.Tables('P210_CAPACITY_HD2'), spcId)

         if testSwitch.ADAPTIVE_GUARD_BAND:
            # ignore Z0 capacity if Adaptive Guard Band is run.
            for hd in range(self.numHeads):
               numSectorInZone0 += sectorsPerTrack[(hd * self.numUserZones) + 0] * TracksPerZone[(hd * self.numUserZones) + 0]
            # Get the number of sectors excluding zone 0 sectors multipled by the zone0Margin
            numsectors = sum(map(operator.mul, sectorsPerTrack, TracksPerZone)) - int(round(numSectorInZone0 * (1-zone0Margin),0))
         else:
            numsectors = sum(map(operator.mul, sectorsPerTrack, TracksPerZone))
         if testSwitch.FE_0257373_348085_ZONED_SERVO_CAPACITY_CALCULATION:
             numSectorInZonesWithZipperZones = 0
             # Exclude the capacity calculated by script at data zones with zipper zones
             for hd in range(self.numHeads):
                for zn in self.dut.dataZonesWithZipperZones[hd]:
                   numSectorInZonesWithZipperZones += sectorsPerTrack[(hd * self.numUserZones) + zn] * TracksPerZone[(hd * self.numUserZones) + zn]
             numsectors -= numSectorInZonesWithZipperZones
         driveCapacity = self.settings['PBA_TO_LBA_SCALER'] * numsectors
         if testSwitch.FE_0297446_348429_P_PRECISE_PARITY_ALLOCATION:
            if verbose: objMsg.printMsg("PPA_DBG Calculated capacity = %f GB" % driveCapacity)
            driveCapacity -= TP.ParitySec_perTrack * sum(TracksPerZone)
            driveCapacity = driveCapacity * self.sectorsize / float(1e9)
            if verbose: objMsg.printMsg("PPA_DBG Calculated capacity after remove Parity = %f GB" % driveCapacity)
            if testSwitch.ADAPTIVE_GUARD_BAND and zone0Margin > 0:
               agbzone = [0]
               driveCapacity -= (self.calculateParitySectorSize(agbzone, TracksPerZone) * zone0Margin)
               if verbose: objMsg.printMsg("PPA_DBG Calculated capacity after remove Parity from AGB = %f GB zone0Margin = %.4f" % (driveCapacity,zone0Margin))
         else:
            driveCapacity = driveCapacity * self.sectorsize / float(1e9)
         if testSwitch.FE_0257373_348085_ZONED_SERVO_CAPACITY_CALCULATION:
            if self.needToGetZonesWithZipperZonesCapFromSF3 == 1:
                self.ZonesWithZipperZonesCapacity = self.getDataZonesWithZipperZonesDriveCapacity()
                self.needToGetZonesWithZipperZonesCapFromSF3 = 0
            #    objMsg.printMsg("Need to pull from drive: self.ZonesWithZipperZonesCapacity = %f GB" % self.ZonesWithZipperZonesCapacity)
            #else:
            #    objMsg.printMsg("Do not need to get from drive: self.ZonesWithZipperZonesCapacity = %f GB" % self.ZonesWithZipperZonesCapacity)
            driveCapacity += (self.ZonesWithZipperZonesCapacity * self.settings['PBA_TO_LBA_SCALER'])
         if debug_capacity :
            self.debug_values(['BpiFormat', 'SectorsPerTrack'])

         if not testSwitch.FE_0171684_007867_DISPLAY_PICKER_AS_TBL:
            objMsg.printMsg("Calculated capacity = %f GB" % driveCapacity)

         return driveCapacity

      #calling SF3 to calculate capacity

      reader = DBLogReader(self.dut, 'P210_CAPACITY_DRIVE', suppressed = True)
      reader.ignoreExistingData()
      getVbarGlobalClass(CProcess).St({'test_num':210,'CWORD1':8, 'SCALED_VAL': int(self.settings['PBA_TO_LBA_SCALER'] * 10000), 'DblTablesToParse': ['P210_CAPACITY_DRIVE'], 'spc_id' : -1})
      return float(reader.getTableObj()[-1]['DRV_CAPACITY'])

   #-------------------------------------------------------------------------------------------------------
   ###########Override parent getAvgDensity################################################################
   def getAvgDensity(self, zone0Margin = 1):
      """Return the average density across all heads"""
      if testSwitch.FE_0125707_340210_CAP_FROM_BPIFILE:
         if testSwitch.FE_0171684_007867_DISPLAY_PICKER_AS_TBL:
            # Update the recordData dictionary for later use in a tabular display of the data.
            self.recordData['COMPUTED_CAP_GB'] = float(self.getDriveCapacity(zone0Margin))
            self.recordData['AVE_DENSITY'] = self.recordData['COMPUTED_CAP_GB'] / self.bpiFile.getNominalCapacity()
            return self.recordData['AVE_DENSITY']
         else:
            return float(self.getDriveCapacity(zone0Margin)) / self.bpiFile.getNominalCapacity()
      else:
         if testSwitch.FE_0171684_007867_DISPLAY_PICKER_AS_TBL:
            # Update the recordData dictionary for later use in a tabular display of the data.
            self.recordData['COMPUTED_CAP_GB'] = float(self.getDriveCapacity(zone0Margin))
            self.recordData['AVE_DENSITY'] = self.recordData['COMPUTED_CAP_GB'] \
               / float(TP.VbarCapacityGBPerHead) / float(self.numHeads)
            return self.recordData['AVE_DENSITY']
         else:
            return (float(self.getDriveCapacity(zone0Margin)) \
               / float(TP.VbarCapacityGBPerHead)) / float(self.numHeads)

  #-------------------------------------------------------------------------------------------------------
   def calculateMediaCacheSize(self):
      TracksPerZone = self.getTracksPerZone()
      if testSwitch.FE_0250539_348085_MEDIA_CACHE_WITH_CAPACITY_ALIGNED:

          TotalMCSectorsPerHead = []
          for hd in xrange(self.numHeads):
             TotalMCSectorsPerHead.append(sum([TracksPerZone[(hd * self.numUserZones) + zn] * self.bpiFile.getSectorsPerTrack(self.getRecord('BpiFormat',hd,zn),zn,hd) for zn in self.mediaCacheZone]))
          sectors = min(TotalMCSectorsPerHead) * self.numHeads

          if testSwitch.FE_0297446_348429_P_PRECISE_PARITY_ALLOCATION:
             # Calculate the number of tracks allocated for MC
             TotalParityTracks  = 0
             for hd in xrange(self.numHeads):
                TotalSectors = 0
                TotalTracks  = 0
                for zn in self.mediaCacheZone:
                   SectorsperTrackZn = self.bpiFile.getSectorsPerTrack(self.getRecord('BpiFormat',hd,zn),zn,hd)
                   TotalSectorsZn = TracksPerZone[(hd * self.numUserZones) + zn] * SectorsperTrackZn
                   if verbose: objMsg.printMsg("PPA_DBG hd %d zn %d tracksperZn %d sectorsperTrack %d TotalMCsectors %d TotalTracks %d TotalSectors %d" % (hd, zn, TracksPerZone[(hd * self.numUserZones) + zn], SectorsperTrackZn, sectors, TotalTracks, TotalSectors))
                   if TotalSectors + TotalSectorsZn > sectors / 2: # If exceed MC Sectors, calculate the remaining tracks
                      remainingSectors = sectors - TotalSectors
                      remainingTracks = int(remainingSectors / SectorsperTrackZn) + 1
                      TotalTracks += remainingTracks
                      break
                   else: # just add when not yet exceed MC sectors
                      TotalTracks += TracksPerZone[(hd * self.numUserZones) + zn]
                      TotalSectors += TotalSectorsZn

                TotalParityTracks += TotalTracks
             TotalParitySectors = TotalParityTracks * TP.ParitySec_perTrack
             sectors -= TotalParitySectors
             if verbose: objMsg.printMsg("PPA_DBG TotalParitySectors %d" % TotalParitySectors)
      else:
          lastMCZone = max(self.mediaCacheZone)
          lastMCZoneTracksList = []

          # Find the shortest stroke among the head for the last media cache zone
          for hd in xrange(self.numHeads):
             lastMCZoneTracksList.append(TracksPerZone[(hd * self.numUserZones) + lastMCZone])

          minLastMCZoneTrack = min(lastMCZoneTracksList)
          sectors = sum([minLastMCZoneTrack * self.bpiFile.getSectorsPerTrack(self.getRecord('BpiFormat',hd,lastMCZone),lastMCZone,hd) for hd in xrange(self.numHeads)])

          if len(self.mediaCacheZone) > 1:
             sectors += sum([TracksPerZone[(hd * self.numUserZones) + zn] * self.bpiFile.getSectorsPerTrack(self.getRecord('BpiFormat',hd,zn),zn,hd) for hd in xrange(self.numHeads) for zn in self.mediaCacheZone[0:(len(self.mediaCacheZone)-1)]])

      # convert to GB
      capMC = (sectors / 1.0e9) * self.sectorsize * self.settings['PBA_TO_LBA_SCALER']
      self.recordData['COMPUTED_CAP_GB'] = capMC
      #objMsg.printMsg("MC Size %f GB" % capMC)
      return capMC

   #-------------------------------------------------------------------------------------------------------
   def calculateRawMediaCacheSize(self):
      TracksPerZone = self.getTracksPerZone()
      sectors = sum([TracksPerZone[(hd * self.numUserZones) + zn] * self.bpiFile.getSectorsPerTrack(self.getRecord('BpiFormat',hd,zn),zn,hd) for hd in xrange(self.numHeads)for zn in self.mediaCacheZone])
      # convert to GB
      capMC = (sectors / 1.0e9) * self.sectorsize * self.settings['PBA_TO_LBA_SCALER'] - self.calculateParitySectorSize(self.mediaCacheZone, TracksPerZone)
      return capMC

   #-------------------------------------------------------------------------------------------------------
   def calculateUMPSize(self):
      TracksPerZone = self.getTracksPerZone()
      sectors = sum([TracksPerZone[(hd * self.numUserZones) + zn] * self.bpiFile.getSectorsPerTrack(self.getRecord('BpiFormat',hd,zn),zn,hd) for hd in xrange(self.numHeads)for zn in self.umpZone])
      # convert to GB
      capUMP = (sectors / 1.0e9) * self.sectorsize * self.settings['PBA_TO_LBA_SCALER'] - self.calculateParitySectorSize(self.umpZone, TracksPerZone)
      self.recordData['COMPUTED_CAP_GB'] = capUMP
      #objMsg.printMsg("UMP Size %f GB" % capUMP)
      return capUMP

   #-------------------------------------------------------------------------------------------------------
   def calculateSpareZoneSize(self):
      spareZone = [self.numUserZones-1]
      TracksPerZone = self.getTracksPerZone()
      sectors = sum([TracksPerZone[(hd * self.numUserZones) + zn] * self.bpiFile.getSectorsPerTrack(self.getRecord('BpiFormat',hd,zn),zn,hd) for hd in xrange(self.numHeads)for zn in spareZone])
      # convert to GB
      capSpare = (sectors / 1.0e9) * self.sectorsize * self.settings['PBA_TO_LBA_SCALER'] - self.calculateParitySectorSize(spareZone, TracksPerZone)
      #self.recordData['COMPUTED_CAP_GB'] = capUMP
      #objMsg.printMsg("UMP Size %f GB" % capUMP)
      return capSpare

   #-------------------------------------------------------------------------------------------------------
   def calculateAGBSize(self):
      agbZone = [0]
      TracksPerZone = self.getTracksPerZone()
      sectors = sum([TracksPerZone[(hd * self.numUserZones) + zn] * self.bpiFile.getSectorsPerTrack(self.getRecord('BpiFormat',hd,zn),zn,hd) for hd in xrange(self.numHeads)for zn in agbZone])
      # convert to GB
      capAGB = (sectors / 1.0e9) * self.sectorsize * self.settings['PBA_TO_LBA_SCALER'] - self.calculateParitySectorSize(agbZone, TracksPerZone)
      self.recordData['COMPUTED_CAP_GB'] = capAGB
      objMsg.printMsg("AGB Size %f GB" % capAGB)
      return capAGB
   
   #-------------------------------------------------------------------------------------------------------
   def calculateParitySectorSize(self, zonelist = [], TracksPerZone = []):
      paritysectors = 0
      if not testSwitch.FE_0297446_348429_P_PRECISE_PARITY_ALLOCATION:
         return paritysectors
      if not len(TracksPerZone):
         TracksPerZone = self.getTracksPerZone()
      if not zonelist:
         range(self.numUserZones)
      for hd in xrange(self.numHeads):
         for zn in zonelist:
            paritysectors += TracksPerZone[(hd * self.numUserZones) + zn] * TP.ParitySec_perTrack
      cap_parity = (paritysectors / 1.0e9) * self.sectorsize
      return cap_parity

   #-------------------------------------------------------------------------------------------------------
   def dumpTpiMarginScale(self):
      objMsg.printMsg('Hd   Zn   TPI_DSS   TPI_IDSS   TPI_ODSS   TPIM      THRSHOLD')
      for hd in xrange(self.numHeads):
         for zn in xrange(self.numUserZones):
            meas = self.measurements.getNibletizedRecord(hd, zn)
            thresScale = self.getRecord('TpiMarginThresScale',hd,zn)
            objMsg.printMsg('%d    %d   %4f   %4f   %4f   %4f   %4f' \
               % (hd, zn, meas['TPI'], meas['TPI_IDSS'], meas['TPI_ODSS'], \
                  thresScale, self.settings['TPIMarginThreshold'][zn]))
            ### Record cert summary data ###
            if testSwitch.ENABLE_CERT_SUMMARY_DATA:
               self.dut.OTCbackoff.append(thresScale)
      
      if testSwitch.ENABLE_CERT_SUMMARY_DATA:
         objMsg.printMsg('ccyy  self.dut.OTCbackoff = %s' % str(self.dut.OTCbackoff))
   
   #-------------------------------------------------------------------------------------------------------
   def consolidateSettingFormatByZone(self, starthead, endhead, startzone, endzone, print_table, \
      maximize_zone, metric, set_one_tpb):
      # Container for the format update st calls
      commands = []
      # Iterate over 
      for hd in xrange(starthead, endhead+1):
         for zn in xrange(startzone, endzone+1, T210_PARM_NUM_HEADS):
             # Set up BPI formats
            bpitables = [self.bpiFile.getNominalFormat(), ] * T210_PARM_NUM_HEADS
            tpitables = [Q0toQ15Factor,] * T210_PARM_NUM_HEADS    # default to 1.0 Nominal Tracks
            trackGuardTables = [0,] * T210_PARM_NUM_HEADS         # default to 0.0 Nominal Tracks
            shingleDirectionTables = [SHINGLE_DIRECTION_OD_TO_ID,] * T210_PARM_NUM_HEADS
            MicrojogSqueezeTables = [0,] * T210_PARM_NUM_HEADS
            if not set_one_tpb:
               tracksPerBandTables = [self.tracksPerBand[0],]* T210_PARM_NUM_HEADS
            else:
               tracksPerBandTables = [1,]* T210_PARM_NUM_HEADS
            for znIncrement in xrange(T210_PARM_NUM_HEADS):
               pickerData = CVbarDataHelper(self, hd, zn+znIncrement)
               if (zn + znIncrement) > endzone:
                  break
               bpitables[znIncrement] += pickerData['BpiFormat']
               if not set_one_tpb:
                  (tpitables[znIncrement], trackGuardTables[znIncrement], MicrojogSqueezeTables[znIncrement]) = \
                     self.calculateTrackPitchParameters(hd, zn + znIncrement, maximize_zone = maximize_zone, print_table = print_table)
                  shingleDirectionTables[znIncrement] = pickerData['ShingleDirection']
                  tracksPerBandTables[znIncrement] = self.tracksPerBand[zn + znIncrement]
               else:
                  tpitables[znIncrement] = int(Q0toQ15Factor / pickerData['TpiCapability'])
                  tracksPerBandTables[znIncrement] = 1
                  
               if self.use_OTC_Rd_Offset:
                  MicrojogSqueezeTables[znIncrement] = int(pickerData['ReadOffset']/2 )
                  
            metrics = [metric]
            for local_metric in metrics:
               # Build the command packet
               command = {
                           'CWORD1'    : 0x0100,
                           'HEAD_MASK' : 0x0000,
                           'CWORD2'    : TP.SetByZnCword,
                         }
               zoneend = ((zn + T210_PARM_NUM_HEADS - 1) > endzone) and endzone or (zn + T210_PARM_NUM_HEADS - 1)
               command['ZONE'] = (zn << 8 ) | zoneend
               if local_metric in ('BPI', 'BOTH'):
                  command['CWORD1'] |= SET_BPI
                  command['BPI_GROUP_EXT'] = bpitables

               if local_metric in ('TPI', 'BOTH'):
                  command['CWORD1'] |= SET_TPI

                  command['CWORD2'] |= CW2_SET_TRACK_PITCH
                  command['TRK_PITCH_TBL'] = tpitables

                  command['CWORD2'] |= CW2_SET_TRACK_GUARD
                  command['TRK_GUARD_TBL'] = trackGuardTables

                  command['CWORD2'] |= CW2_SET_SHINGLED_DIRECTION
                  command['SHINGLED_DIRECTION'] = shingleDirectionTables

                  command['CWORD2'] |= CW2_SET_TRACKS_PER_BAND
                  command['TRACKS_PER_BAND'] = tracksPerBandTables

                  if self.updateSqueezeMicrojog:
                     command['CWORD2'] |= CW2_SET_SQUEEZE_MICROJOG
                     command['MICROJOG_SQUEEZE'] = MicrojogSqueezeTables
                  
                  self.bTPIchangedReloadZoneTbl = True
            
               if local_metric in ('UJOG'):
                  command['CWORD1'] |= SET_TPI
                  command['CWORD2'] |= CW2_SET_SQUEEZE_MICROJOG
                  command['MICROJOG_SQUEEZE'] = MicrojogSqueezeTables
               
               command['HEAD_MASK'] = 1 << hd
               commands.append(command)
      
      return commands
   
#----------------------------------------------------------------------------------------------------------
class CDesperadoPlusPicker(CDesperadoPicker):
   """
      This class is a reformulation of the picker to work on Bands and calculate TPI Margin based on bands
      per zone.
   """

   def __init__(self, niblet, measurements, limits, SendVbarFmtSummaryToEDW=True, active_zones=[]):
      CDesperadoPicker.__init__(self, niblet, measurements, limits, SendVbarFmtSummaryToEDW, active_zones=[])
      self.tpiMarginCalMethod = 1
      
      if testSwitch.FE_0261758_356688_LBR:
         self.LBR     = 0
         self.FindNZB = 0         

      data = {
         'NumNominalTracks'      : ('l',  0     ), 
      }
      if testSwitch.VBAR_TPI_MARGIN_THRESHOLD_BY_HD_BY_ZN or testSwitch.VBAR_MARGIN_BY_OTC or testSwitch.FAST_2D_S2D_TEST:
         data.update({
            'TpiMarginThresScalebyTP'  : ('f',  0.0   ), 
         })
      self.addItems(data)
      for hd in xrange(self.numHeads):
         for zn in xrange(self.numUserZones):
            pickerData  = CVbarDataHelper(self, hd, zn)
            pickerData['NumNominalTracks'] = self.bpiFile.getNumNominalTracksInZone(0,zn,hd)
            pickerData['NumBands'] = int(round(pickerData['TpiPickInitial'] * self.bpiFile.getNumNominalTracksInZone(0,zn,hd) / self.tracksPerBand[zn]))
      self.extraBandSpacing = 0

   #-------------------------------------------------------------------------------------------------------
   def getTpiStepSize(self, zone=None):
      return 1

   #-------------------------------------------------------------------------------------------------------
   def selectShingledDirection(self):
      """
      selectShingledDirection locates the best zone for switching the shingled direction on a by head basis.
      It enforces that there can only be one switch per head.
      It works by performing a linear fit to the delta between the two shingle tpi measurements
      """
      for hd in xrange(self.numHeads):
         S = 0
         Sx = 0
         Sxx = 0
         Sxy = 0
         Sy = 0

         for zn in xrange(self.numUserZones):
            meas = self.measurements.getNibletizedRecord(hd,zn)
            y = meas['TPI_IDSS'] - meas['TPI_ODSS']
            S += 1
            Sx += zn
            Sxx += (zn*zn)
            Sxy += zn * y
            Sy += y

         if (S*Sxy - Sx*Sy) == 0:
            # To prevent a divide by zero exception, just pick the middle zone.
            switchZone = int(self.numUserZones/2)
         else:
            # Make the normal regression based pick.
            switchZone = ( Sx*Sxy - Sxx*Sy ) / ( S*Sxy - Sx*Sy )

         if verbose:
            objMsg.printMsg("hd %d  S %f Sx %f Sxx %f Sxy %f Sy %f Switch at %f" % (hd,S,Sx,Sxx,Sxy,Sy, switchZone) )

         for zn in xrange(self.numUserZones):
            if zn >= switchZone:
               self.setRecord('ShingleDirection',SHINGLE_DIRECTION_ID_TO_OD,hd,zn)
            else:
               self.setRecord('ShingleDirection',SHINGLE_DIRECTION_OD_TO_ID,hd,zn)

   #-------------------------------------------------------------------------------------------------------
   def calculateBandedTPI_LCO(self,measurements):

      if testSwitch.SMR_SGL_SHINGLE_DIRECTION_SWITCH:
         self.selectShingledDirection()

      for hd in xrange(self.numHeads):
         for zn in xrange(self.numUserZones):
            pickerData = CVbarDataHelper(self, hd, zn)
            meas = measurements.getNibletizedRecord(hd, zn)
            meas['TPI_DSS'] = meas['TPI']

            if testSwitch.SMR_SGL_SHINGLE_DIRECTION_SWITCH:
               # Special Case for backward compatability
               if self.tracksPerBand[zn] == 1:
                  tpi_sss = meas['TPI_DSS']
                  pickerData['ReadOffset'] = 0

               elif pickerData['ShingleDirection'] == SHINGLE_DIRECTION_ID_TO_OD:
                  tpi_sss = meas['TPI_ODSS']
                  pickerData['ReadOffset'] = int(meas['RD_OFST_ODSS'])

               else:
                  tpi_sss = meas['TPI_IDSS']
                  pickerData['ReadOffset'] = int(meas['RD_OFST_IDSS'])

               # Another Special Case, if single sided capability is less than double sided, set everything to double sided
               if tpi_sss <= meas['TPI_DSS']:
                  tpi_sss = meas['TPI_DSS']
                  pickerData['ReadOffset'] = 0
            else:
               # Special Case for backward compatability
               if self.tracksPerBand[zn] == 1:
                  tpi_sss = meas['TPI_DSS']
                  direction = 'IDSS'
                  pickerData['ShingleDirection'] = SHINGLE_DIRECTION_OD_TO_ID
                  pickerData['ReadOffset'] = 0

               elif meas['TPI_ODSS'] > meas['TPI_IDSS']:
                  tpi_sss = meas['TPI_ODSS']
                  direction = 'ODSS'
                  pickerData['ShingleDirection'] = SHINGLE_DIRECTION_ID_TO_OD
                  pickerData['ReadOffset'] = int(meas['RD_OFST_ODSS'])

               else:
                  tpi_sss = meas['TPI_IDSS']
                  direction = 'IDSS'
                  pickerData['ShingleDirection'] = SHINGLE_DIRECTION_OD_TO_ID
                  pickerData['ReadOffset'] = int(meas['RD_OFST_IDSS'])

               # Another Special Case, if single sided capability is less than double sided, set everything to double sided
               if tpi_sss <= meas['TPI_DSS']:
                  tpi_sss = meas['TPI_DSS']
                  direction = 'IDSS'
                  pickerData['ShingleDirection'] = SHINGLE_DIRECTION_OD_TO_ID
                  pickerData['ReadOffset'] = 0
            # end of SMR_SGL_SHINGLE_DIRECTION_SWITCH

            sp = float(self.settings['ShingledProportion'][zn])
            tpb = float(self.tracksPerBand[zn])

            effectiveTpic = (tpb - TP.TG_Coef)/tpb * sp * (tpi_sss) + ( 1 - sp + sp * TP.TG_Coef/tpb) * (meas['TPI_DSS'])

            pickerData['TpiCapability'] = effectiveTpic
            pickerData['TpiCapabilitySSS'] = tpi_sss * sp + ( 1 - sp ) * meas['TPI_DSS']
            pickerData['TpiCapabilityDSS'] = meas['TPI_DSS']
            pickerData['TpiMargin'] = effectiveTpic - pickerData['TpiPick']

   #-------------------------------------------------------------------------------------------------------
   def initializeTpiStepSizeArray(self):
      """ initializeTpiStepSizeArray:
            Since only integral numbers of bands can fit in a data zone, calculate the tpi step size allowable
            in each zone.
            """
      if testSwitch.FE_0269922_348085_P_SIGMUND_IN_FACTORY:
         self.tpiStepSize = [ [] for hd in range(self.numHeads)]
         for hd in range(self.numHeads):
            self.tpiStepSize[hd] = [1,] * self.numUserZones
      else:
         self.tpiStepSize = [1,] * self.numUserZones

   #-------------------------------------------------------------------------------------------------------
   def getTracksPerZone(self):
      if testSwitch.FE_0261758_356688_LBR and self.LBR:         
         return [int(round(self.getRecord('TpiPick',hd,zn) * self.NewZB[hd][zn]['TRK_NUM'])) for hd in xrange(self.numHeads) for zn in xrange(self.numUserZones)]
      else:
         return [int(round(self.getRecord('TpiPick',hd,zn) * self.bpiFile.getNumNominalTracksInZone(self.baseformat[hd],zn,hd))) for hd in xrange(self.numHeads) for zn in xrange(self.numUserZones)]
        
   #-------------------------------------------------------------------------------------------------------
   def getRAWTracksPerZone(self):
      return [int(self.getRecord('TpiCapability',hd,zn) * self.bpiFile.getNumNominalTracksInZone(self.baseformat[hd],zn,hd)) for hd in xrange(self.numHeads) for zn in xrange(self.numUserZones)]
         
   #-------------------------------------------------------------------------------------------------------
   def getZB(self, metric):
      # TODO: test
      try:
         self.dut.dblData.Tables(TP.zone_table['table_name'])
      except:
         getVbarGlobalClass(CProcess).St({'test_num':172, 'prm_name':'Retrieve Zone Table Info', 'CWORD1':0x0002, 'spc_id':1, 'stSuppressResults': 0, 'timeout': 100, })         
      printDbgMsg("systemAreaUserZones %s" % str(self.dut.systemAreaUserZones))
      
      self.NominalZB = {}
      for hd in xrange(self.numHeads):
         self.NominalZB[hd] = {}
         for zn in range(self.numUserZones):
            self.NominalZB[hd][zn] = {}
            
      if metric == 'RAP':
         printDbgMsg("get ZB from RAP")
         if not testSwitch.virtualRun: #wg
            for table in ['P172_ZB_INFO']:
               try:
                  self.dut.dblData.Tables(table).deleteIndexRecords(1)
                  self.dut.dblData.delTable(table, forceDeleteDblTable = 1)
               except: pass         
         getVbarGlobalClass(CProcess).St(TP.DisplayUserZB)
         colDict = self.dut.dblData.Tables('P172_ZB_INFO').columnNameDict()
         rowIter = self.dut.dblData.Tables('P172_ZB_INFO').rowListIter()
         for row in rowIter:
            hd = int(row[colDict['HD_LGC_PSN']])
            zn = int(row[colDict['DATA_ZONE']])
            self.NominalZB[hd][zn]['ZN_START_CYL'] = int(row[colDict['ZN_START_CYL']])
            self.NominalZB[hd][zn]['TRK_NUM']      = int(row[colDict['TRK_NUM']])
      else:
         objMsg.printMsg("get ZB from BPI file")
         # get nominal trk from BPI
         for hd in xrange(self.numHeads):
            for zn in xrange(self.numUserZones):
               self.NominalZB[hd][zn]['TRK_NUM'] = self.bpiFile.getNumNominalTracksInZone(0,zn)         
         
         # find zn_start_cyl
         getVbarGlobalClass(CProcess).St(TP.DisplaySysZB)
         colDict = self.dut.dblData.Tables('P172_MISC_INFO').columnNameDict()
         row = self.dut.dblData.Tables('P172_MISC_INFO').rowListIter(index=len(self.dut.dblData.Tables('P172_MISC_INFO'))-1).next()
         SysZnNumNomTrk = int(row[colDict['VALUE']])
         objMsg.printMsg("SystemZoneNumNominalTracks %d" % (SysZnNumNomTrk))
      
         for hd in xrange(self.numHeads):
            for zn in xrange(self.numUserZones):
               if zn == 0:
                  self.NominalZB[hd][zn]['ZN_START_CYL'] = 0         
               elif zn == (self.dut.systemAreaUserZones[hd] + 1):
                  self.NominalZB[hd][zn]['ZN_START_CYL'] = self.NominalZB[hd][zn-1]['ZN_START_CYL'] + self.NominalZB[hd][zn-1]['TRK_NUM'] + SysZnNumNomTrk
               else:
                  self.NominalZB[hd][zn]['ZN_START_CYL'] = self.NominalZB[hd][zn-1]['ZN_START_CYL'] + self.NominalZB[hd][zn-1]['TRK_NUM']
               
      if debug_LBR:         
         objMsg.printMsg("Nominal Zone Boundary")
         objMsg.printMsg("Hd  Zn  ZN_START_CYL  TRK_NUM")
         for hd in xrange(self.numHeads):
            for zn in xrange(self.numUserZones):
               objMsg.printMsg("%2d  %2d  %12d  %d" % (hd, zn, self.NominalZB[hd][zn]['ZN_START_CYL'], self.NominalZB[hd][zn]['TRK_NUM']))
            
      ZnStartCyl = []
      TrkNum = []
      for hd in xrange(self.numHeads):
         for zn in xrange(self.numUserZones):
            ZnStartCyl.append(self.NominalZB[hd][zn]['ZN_START_CYL'])
            TrkNum.append(self.NominalZB[hd][zn]['TRK_NUM'])
      printDbgMsg("Nominal ZN_START_CYL: %s" % ZnStartCyl)
      printDbgMsg("Nominal TRK_NUM: %s" % TrkNum)
         
   #-------------------------------------------------------------------------------------------------------
   def SetZnBoundary(self):
      objMsg.printMsg("Set Zone Boundary")      
      skipUpdateZn = TP.ZB_remain
      skipUpdateZnStartCyl = [self.dut.systemAreaUserZones[hd]+1 for hd in xrange(self.numHeads)]      
         
      if testSwitch.extern.FE_0270714_356688_ZB_UPDATE:
         updateZB_prm = deepcopy(TP.updateZB_178)
         UPDATE_SIZE = 30
         for hd in xrange(self.numHeads):
            ZoneNum           = [0xFFFF,] * (UPDATE_SIZE)            
            StartNominalTrack = [0xFFFF,] * (UPDATE_SIZE*2)
            NumNominalTracks  = [0xFFFF,] * (UPDATE_SIZE*2)
            NumUpdate = 0
            for zn in range(self.numUserZones):                  
               if zn in skipUpdateZn:
                  continue
                  
               if debug_LBR: objMsg.printMsg("set zone %d" % (zn))            
               if zn not in skipUpdateZnStartCyl:                  
                  StartNominalTrack[(NumUpdate*2)+1] = self.NewZB[hd][zn]['ZN_START_CYL'] & 0xFFFF
                  StartNominalTrack[NumUpdate*2]     = (self.NewZB[hd][zn]['ZN_START_CYL']>>16 ) & 0xFFFF
               else:                  
                  objMsg.printMsg("skip ZN_START_CYL update at zn %d" % (zn))
                  
               NumNominalTracks[(NumUpdate*2)+1] = self.NewZB[hd][zn]['TRK_NUM'] & 0xFFFF
               NumNominalTracks[NumUpdate*2]     = (self.NewZB[hd][zn]['TRK_NUM']>>16 ) & 0xFFFF
               ZoneNum[NumUpdate] = zn
               NumUpdate += 1
               if NumUpdate == UPDATE_SIZE:
                  updateZB_prm['TEST_HEAD']         = hd
                  updateZB_prm['ZONE_NUM']          = ZoneNum                  
                  updateZB_prm['START_NOMINAL_TRK'] = StartNominalTrack
                  updateZB_prm['NUM_NOMINAL_TRK']   = NumNominalTracks                  
                  getVbarGlobalClass(CProcess).St(updateZB_prm)
                  ZoneNum           = [0xFFFF,] * (UPDATE_SIZE)                  
                  StartNominalTrack = [0xFFFF,] * (UPDATE_SIZE*2)
                  NumNominalTracks  = [0xFFFF,] * (UPDATE_SIZE*2)
                  NumUpdate = 0
            if ZoneNum[0] != 0xFFFF:
               updateZB_prm['TEST_HEAD']         = hd
               updateZB_prm['ZONE_NUM']          = ZoneNum               
               updateZB_prm['START_NOMINAL_TRK'] = StartNominalTrack
               updateZB_prm['NUM_NOMINAL_TRK']   = NumNominalTracks                  
               getVbarGlobalClass(CProcess).St(updateZB_prm)
         getVbarGlobalClass(CProcess).St({'test_num': 178, 'prm_name': 'prm_178_Save_RAP_to_flash', 'timeout': 1200, 'spc_id': 0, 'CWORD1':0x0220})
      else:
         raiseException(11044,"Failed to update RAP, please turn on FE_0270714_356688_ZB_UPDATE in SF3")
               
      if debug_LBR:
         DisplayUserZB_prm = deepcopy(TP.DisplayUserZB)
         DisplayUserZB_prm['spc_id'] = 2
         getVbarGlobalClass(CProcess).St(DisplayUserZB_prm)
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      ZnStartCyl = []
      TrkNum = []
      for hd,zn in [(hd, zn) for hd in range(self.numHeads) for zn in range(self.numUserZones)]:
         ZnStartCyl.append(self.NewZB[hd][zn]['ZN_START_CYL'])
         TrkNum.append(self.NewZB[hd][zn]['TRK_NUM'])
      objMsg.printMsg("New ZN_START_CYL: %s" % ZnStartCyl)
      objMsg.printMsg("New TRK_NUM: %s" % TrkNum)
      
   #-------------------------------------------------------------------------------------------------------
   def calculateTrackPitches(self,hd,zn,numBands=None,NumNominalTracks=None,debug=None):
      """
      calculateTrackPitch performs the shingled track pitch calculations.
      It calculates (in nominal track pitch)
      TrackPitch
      TrackGuard
      SquezeMicrojog
      """
      zfi = CVbarDataHelper(self, hd, zn)
      if numBands == None:
         numBands = zfi['NumBands']
      if NumNominalTracks == None:
         if testSwitch.FE_0261758_356688_LBR and self.LBR:
            NumNominalTracks = self.NewZB[hd][zn]['TRK_NUM']
         else:
            NumNominalTracks = zfi['NumNominalTracks']
            
      if verbose: #print out conditionally
         objMsg.printMsg("ccccyyyyyyTpiCapabilitySSS = %f, ccccyyyyyyTpiMarginThresScale = %f" % \
            (zfi['TpiCapabilitySSS'],zfi['TpiMarginThresScale']))
      # calculate the Track Pitch of the shingled track.
      # taken directly from the TPIc of the single sided measurement.
      if testSwitch.FE_0215591_007867_COMPUTE_TPIC_AS_RATIO_MERGE_CL537310:
         if testSwitch.FE_0293889_348429_VBAR_MARGIN_BY_OTCTP and self.tracksPerBand[zn] != 1:
            TPs = 1.0 / (zfi['TpiCapabilitySSS'] - zfi['TpiM_SSS'])
            # get Double sided track pitch
            if testSwitch.FE_0293889_348429_VBAR_MARGIN_BY_OTCTP_INTERBAND_MARGIN:
               TPd = 1.0 / (zfi['TpiCapabilityDSS'] - zfi['TpiM_DSS'])
            else:
               TPd = 1.0 / zfi['TpiCapabilityDSS'] 
         elif testSwitch.RUN_ATI_IN_VBAR and self.tracksPerBand[zn] == 1: 
            TPs = 1.0 / (zfi['TpiCapabilitySSS'] - zfi['TpiMarginThresScale'])
            TPd = 1.0 / zfi['TpiCapabilityDSS']
         else:
            TPs = 1.0 / zfi['TpiCapabilitySSS']
            # get Double sided track pitch
            TPd = 1.0 / zfi['TpiCapabilityDSS']
      else:
         TPs = 2-zfi['TpiCapabilitySSS']
         # get Double sided track pitch
         TPd = 2-zfi['TpiCapabilityDSS']
      if testSwitch.VBAR_TPI_MARGIN_THRESHOLD_BY_HD_BY_ZN:
         if testSwitch.FE_0293889_348429_VBAR_MARGIN_BY_OTCTP and self.tracksPerBand[zn] != 1:
            zfi['TpiMarginThresScalebyTP'] = (1.0 / (zfi['TpiCapabilitySSS'] - zfi['TpiM_SSS'])) - (1.0 / zfi['TpiCapabilitySSS'])
         else: # For UMP Zones
            zfi['TpiMarginThresScalebyTP'] = (1.0 / (zfi['TpiCapabilitySSS'] - zfi['TpiMarginThresScale'])) - (1.0 / zfi['TpiCapabilitySSS'])
      if self.tracksPerBand[zn] == 1:
         denominator = self.tracksPerBand[zn] * numBands
         ShingledTrackPitch = NumNominalTracks / float( denominator )
         GuardTrackPitch = 0
      else:
         denominator = (self.tracksPerBand[zn] * numBands - numBands - 1)
         ShingledTrackPitch = (NumNominalTracks - (TP.TG_Coef * (TPd - TPs) + TPs + self.extraBandSpacing) * (numBands + 1)) / denominator
         GuardTrackPitch = (TP.TG_Coef * (TPd - TPs) + TPs + self.extraBandSpacing) - ShingledTrackPitch

      if GuardTrackPitch < 0:
         GuardTrackPitch = 0
         ShingledTrackPitch = NumNominalTracks / float(self.tracksPerBand[zn] * numBands)

      SqueezeMicrojog = (TPd - TPs) / 2

      ShingledPitchMargin = ShingledTrackPitch - TPs
      
      if (debug_LBR and debug == 1):         
         objMsg.printMsg("%2d  %2d  %6d  %3d  %f  %f  %f  %f  %f  %7d  %f" % (hd, zn, numBands, self.tracksPerBand[zn], zfi['TpiPick'], TPd, TPs, ShingledTrackPitch, GuardTrackPitch, NumNominalTracks, ShingledPitchMargin))

      return (ShingledTrackPitch, GuardTrackPitch, SqueezeMicrojog, ShingledPitchMargin)
   #-------------------------------------------------------------------------------------------------------
   def calculateTrackPitchMargin(self,hd,zn,numBands=None):
      """
      calculateTrackPitchMargin calculates the TPI margin for a shingled zone.
      """
      _, _, _, ShingledPitchMargin = self.calculateTrackPitches(hd,zn,numBands,None,1)
      return ShingledPitchMargin
   #-------------------------------------------------------------------------------------------------------
   #def calculateTrackPitchParameters(self,hd,zn):
   def calculateTrackPitchParameters(self,hd ,zn, maximize_zone = 1, print_table = 1):
      """
      calculateTrackPitchParameters sets up the information for a test 210 call with shingled drives.
      It calculates
      TrackPitch
      TrackGuard
      ShingleDirection
      """

      (ShingledTrackPitch, GuardTrackPitch, SqueezeMicrojog, ShingledMargin) = self.calculateTrackPitches(hd,zn,None)

      # save off the effective pick for the next iteration of the picker
      meas = CVbarDataHelper(self.measurements, hd, zn)
      zfi = CVbarDataHelper(self, hd, zn)
      meas['TPIPickEffective'] = zfi['TpiPick']
      meas['TPIFmtEffective'] = zfi['TpiPick'] * self.formatScaler.RelativeToFormatScaler - self.formatScaler.RelativeToFormatScaler

      if testSwitch.FE_0215591_007867_COMPUTE_TPIC_AS_RATIO_MERGE_CL537310:
         if testSwitch.FE_0293889_348429_VBAR_MARGIN_BY_OTCTP and self.tracksPerBand[zn] != 1:
            TPs = 1.0 / (zfi['TpiCapabilitySSS'] - zfi['TpiM_SSS'])
         elif testSwitch.FAST_2D_S2D_TEST or testSwitch.VBAR_MARGIN_BY_OTC or (testSwitch.RUN_ATI_IN_VBAR and self.tracksPerBand[zn] == 1):
            TPs = 1.0 / (zfi['TpiCapabilitySSS'] - zfi['TpiMarginThresScale'])
         else:
            TPs = 1.0 / zfi['TpiCapabilitySSS']
         # get Double sided track pitch
         if testSwitch.FE_0293889_348429_VBAR_MARGIN_BY_OTCTP_INTERBAND_MARGIN and self.tracksPerBand[zn] != 1:
            TPd = 1.0 / (zfi['TpiCapabilityDSS'] - zfi['TpiM_DSS'])
         else:
            TPd = 1.0 / zfi['TpiCapabilityDSS']
      else:
         TPs = 2-zfi['TpiCapabilitySSS']
         # get Double sided track pitch
         TPd = 2-zfi['TpiCapabilityDSS']

      # first calculate the band size from the effective pick
      bandSizePicked = self.tracksPerBand[zn]/zfi['TpiPick']

      TrackPitch = int(ShingledTrackPitch * Q0toQ15Factor)
      TrackGuard = int(max(GuardTrackPitch * Q0toQ14Factor,0))

      # limit the values to the 16 bit size.  There is an issue here,
      # in that VBAR is going to underestimate the capacity of the drive and overestimate the margin.
      if TrackPitch > 0xFFFF:
         TrackPitch = 0xFFFF
      if TrackGuard > 0xFFFF:
         TrackGuard = 0xFFFF

      # The amount of space in the zone that we can use is the Number of Nominal Tracks in the zone minus one Guard Pitch
      # We want the guard pitch to avoid a possible squeeze situation at zone boundaries.
      if testSwitch.FE_0261758_356688_LBR and self.LBR:
         numNominalTracksAlloc = self.NewZB[hd][zn]['TRK_NUM']         
      else:
         numNominalTracksAlloc = self.bpiFile.getNumNominalTracksInZone(0,zn,hd)
      numBands = zfi['NumBands']

      numLogicalTracks = numBands * self.tracksPerBand[zn]
      numNominalTracksUsed = float((TrackPitch * self.tracksPerBand[zn] + TrackGuard * 2)*numBands + 2*TrackGuard)/Q0toQ15Factor
      if debug_LBR:
         objMsg.printMsg("%2d  %2d  %f  %f  %f  %f  %f  %3d  %6d  %.7f  %.7f  %8d  %8d  %.2f  %7d  %7d  %.6f" % (hd, zn, \
            zfi['TpiCapability'], zfi['TpiPick'], bandSizePicked, TPs, TPd, self.tracksPerBand[zn], \
            numBands, ShingledTrackPitch, GuardTrackPitch, TrackPitch, TrackGuard, numNominalTracksUsed, \
            numNominalTracksAlloc, numLogicalTracks, ShingledMargin))
            
      if maximize_zone or not testSwitch.OTC_SKIP_ZONE_MAXIMIZATION:
         Modification = 'Pitch'
         # try to use the entire allocated space without going over
         #   we should always be a bit underutilized due to the flooring of the division
         while (numNominalTracksUsed < numNominalTracksAlloc):
            if TrackPitch == 0xFFFF:
               break
            TrackPitch += 1
            numNominalTracksUsed = float((TrackPitch * self.tracksPerBand[zn] + TrackGuard * 2)*numBands + 2*TrackGuard)/Q0toQ15Factor

         # now the zone is a bit too big Ping - Pong between removing pitch and guard
         while (numNominalTracksUsed > numNominalTracksAlloc):
            if Modification == 'Guard':
               if TrackGuard > 0:
                  TrackGuard -= 1
               Modification = 'Pitch'
            else:
               if TrackPitch > 0:
                  TrackPitch -= 1
               Modification = 'Guard'

               numNominalTracksUsed = float((TrackPitch * self.tracksPerBand[zn] + TrackGuard * 2)*numBands + 2*TrackGuard)/Q0toQ15Factor

         if Modification == "Guard":
            # the last modification done was pitch. see if we can increase guard.
            while (numNominalTracksUsed < numNominalTracksAlloc):
               if TrackGuard == 0xFFFF:
                  break
               TrackGuard += 1
               numNominalTracksUsed = float((TrackPitch * self.tracksPerBand[zn] + TrackGuard * 2)*numBands + 2*TrackGuard)/Q0toQ15Factor
            while (numNominalTracksUsed > numNominalTracksAlloc):
               TrackGuard -= 1
               numNominalTracksUsed = float((TrackPitch * self.tracksPerBand[zn] + TrackGuard * 2)*numBands + 2*TrackGuard)/Q0toQ15Factor

      if testSwitch.DISPLAY_SMR_FMT_SUMMARY:
         MicrojogSqueeze = int(SqueezeMicrojog * 128 + .5)

         if zfi['ShingleDirection'] == SHINGLE_DIRECTION_OD_TO_ID:
            shingleDir = "OD_TO_ID"
            MicrojogSqueeze *= -1
         else:
            shingleDir = "ID_TO_OD"

         #override calculated rd offset with rd offset 211 or otc rd offset
         #to be shown in the P_SMR_FORMAT_SUMMARY table
         if self.use_OTC_Rd_Offset:
            tempMicrojog = MicrojogSqueeze
            if self.tracksPerBand[zn] == 1:
               MicrojogSqueeze = 0
            elif testSwitch.FE_0293889_348429_VBAR_MARGIN_BY_OTCTP_RD_OFFSET_CALC:
               tpip = 1/ShingledTrackPitch
               Adj_RO = 128*(1-1/tpip)
               if zfi['ShingleDirection'] == SHINGLE_DIRECTION_OD_TO_ID:
                  New_RO = zfi['ReadOffset']-Adj_RO
               else:
                  New_RO = zfi['ReadOffset']+Adj_RO
               Scaled_RO = New_RO*(256+Adj_RO)/256
               MicrojogSqueeze = int(round(Scaled_RO,0))
            else:
               MicrojogSqueeze = int(zfi['ReadOffset']/2)

         if print_table:
            self.dut.dblData.Tables('P_SMR_FORMAT_SUMMARY').addRecord({
                                    'SPC_ID'            : self.spcId_SMR_FMT,
                                    'OCCURRENCE'        : self.SmrOccurrence,
                                    'SEQ'               : self.dut.objSeq.getSeq(),
                                    'TEST_SEQ_EVENT'    : 1,
                                    'HD_PHYS_PSN'       : self.dut.LgcToPhysHdMap[hd],
                                    'DATA_ZONE'         : zn,
                                    'HD_LGC_PSN'        : hd,
                                    'TPIC_S'            : round(zfi['TpiCapabilitySSS'],6),
                                    'TP_S'              : round(TPs,6),
                                    'TPIC_D'            : round(zfi['TpiCapabilityDSS'],6),
                                    'TP_D'              : round(TPd,6),
                                    'PICK'              : round(zfi['TpiPick'],6),
                                    'EFF_TPIC'          : round(zfi['TpiCapability'],6),
                                    'BANDSIZE_RATIO'    : round(zfi['NumBands'],6),
                                    'BANDSIZE_PICK'     : round(bandSizePicked,6),
                                    'SHINGLE_TRK_PITCH' : round(ShingledTrackPitch,6),
                                    'GUARD_TRK_PITCH'   : '%.8f' % GuardTrackPitch, #round(GuardTrackPitch,8), round was producing scientific notation here.
                                    'SHINGLE_DIR'       : shingleDir,
                                    'UJOG_SQUEEZE'      : round(MicrojogSqueeze,6),
                                    'BANDSIZE_PHY'      : round((ShingledTrackPitch*self.tracksPerBand[zn]) + GuardTrackPitch,6),
                                    'TRK_PITCH'         : round(TrackPitch,6),
                                    'TRK_GUARD'         : round(TrackGuard,6),
                                    'NUM_LGC_TRKS'      : round(numLogicalTracks,6),
                                    'NOM_TRKS_ALLOC'    : round(numNominalTracksAlloc,6),
                                    'NOM_TRKS_USED'     : round(numNominalTracksUsed,6),
                                    'NUM_OF_BANDS'      : round(numBands,6),
                                  })

         #revert back previously value
         if self.use_OTC_Rd_Offset:
            MicrojogSqueeze = tempMicrojog

      else:
         objMsg.printMsg("hd = %d, zn = %d" % (hd,zn))
         objMsg.printMsg("TPICs = %f, TPs = %f" % (zfi['TpiCapabilitySSS'],TPs))
         objMsg.printMsg("TPICd = %f, TPd = %f" % (zfi['TpiCapabilityDSS'],TPd))
         objMsg.printMsg("Pick = %f, EffC = %f, ratio = %f" % ( zfi['TpiPick'],zfi['TpiCapability'],ratio))
         objMsg.printMsg("BandSize = %f, Tb = %f, Tg = %f, BS = %f" % (bandSizePicked,ShingledTrackPitch,GuardTrackPitch,ShingledTrackPitch*self.tracksPerBand[zn]+GuardTrackPitch))
         objMsg.printMsg("TP = %d, TG = %d, LogTrks = %d, NomTrksAlloc = %d, NomTrksUsed = %f, numBands = %d" % (TrackPitch,TrackGuard,numLogicalTracks,numNominalTracksAlloc,numNominalTracksUsed,numBands))

      if testSwitch.EFFECTIVE_TPIC_EQUAL_TPIS:
         TrackPitch = int(Q0toQ15Factor/zfi['TpiCapabilitySSS'])
         
      if testSwitch.FE_0293889_348429_VBAR_MARGIN_BY_OTCTP_OVERRIDE_TP_TG and self.tracksPerBand[zn] != 1:
         objMsg.printMsg("OTV2_Override hd: %d, zn: %d Orig_TP: %d Orig_TG: %d New_TP: %d New_TG: %d" % (hd,zn,TrackPitch,TrackGuard,int(Q0toQ15Factor/meas['TPI_INTRA']),int(max(Q0toQ14Factor*((1/meas['TPI_INTER'])-(1/meas['TPI_INTRA'])),0))))
         TrackPitch = int(Q0toQ15Factor/meas['TPI_INTRA'])
         TrackGuard = int(max(Q0toQ14Factor * ((1/meas['TPI_INTER']) - (1/meas['TPI_INTRA'])),0))

      return (TrackPitch,TrackGuard,MicrojogSqueeze)

  #-------------------------------------------------------------------------------------------------------
   def calculatenumNominalTracksUsed(self, hd, zn, numNominalTracksAlloc, numBands):      
      (ShingledTrackPitch, GuardTrackPitch, SqueezeMicrojog, ShingledMargin) = self.calculateTrackPitches(hd, zn, numBands, numNominalTracksAlloc)
      
      # save off the effective pick for the next iteration of the picker
      meas = CVbarDataHelper(self.measurements, hd, zn)
      zfi = CVbarDataHelper(self, hd, zn)
      meas['TPIPickEffective']= zfi['TpiPick']
      meas['TPIFmtEffective'] = zfi['TpiPick'] * self.formatScaler.RelativeToFormatScaler - self.formatScaler.RelativeToFormatScaler
      
      if testSwitch.FE_0215591_007867_COMPUTE_TPIC_AS_RATIO_MERGE_CL537310:
         if testSwitch.FE_0293889_348429_VBAR_MARGIN_BY_OTCTP and self.tracksPerBand[zn] != 1:
            TPs = 1.0 / (zfi['TpiCapabilitySSS'] - zfi['TpiM_SSS'])
            # get Double sided track pitch
            if testSwitch.FE_0293889_348429_VBAR_MARGIN_BY_OTCTP_INTERBAND_MARGIN:
               TPd = 1.0 / (zfi['TpiCapabilityDSS'] - zfi['TpiM_DSS'])
            else:
               TPd = 1.0 / zfi['TpiCapabilityDSS']
         elif testSwitch.RUN_ATI_IN_VBAR and self.tracksPerBand[zn] == 1: 
            TPs = 1.0 / (zfi['TpiCapabilitySSS'] - zfi['TpiMarginThresScale'])
            TPd = 1.0 / zfi['TpiCapabilityDSS']
         else:
            TPs = 1.0 / zfi['TpiCapabilitySSS']
            # get Double sided track pitch
            TPd = 1.0 / zfi['TpiCapabilityDSS']
      else:
         TPs = 2-zfi['TpiCapabilitySSS']
         # get Double sided track pitch
         TPd = 2-zfi['TpiCapabilityDSS']
         
      # first calculate the band size from the effective pick
      bandSizePicked = self.tracksPerBand[zn]/zfi['TpiPick']
      
      TrackPitch = int(TPs * Q0toQ15Factor) #int(ShingledTrackPitch * Q0toQ15Factor)
      
      if self.tracksPerBand[zn] == 1:
         TrackGuard = 0
      else:
         TrackGuard = TP.TG_Coef * (TPd - TPs) + self.extraBandSpacing
         TrackGuard = int(max(TrackGuard * Q0toQ14Factor,0))        # TrackGuard = int(max(GuardTrackPitch * Q0toQ14Factor,0))
      
      OPTrackPitch = int(ShingledTrackPitch * Q0toQ15Factor)
      OPTrackGuard = int(max(GuardTrackPitch * Q0toQ14Factor,0))
      
      # limit the values to the 16 bit size.  There is an issue here,
      # in that VBAR is going to underestimate the capacity of the drive and overestimate the margin.
      if TrackPitch > 0xFFFF:
         TrackPitch = 0xFFFF
      if TrackGuard > 0xFFFF:
         TrackGuard = 0xFFFF
         
      numNominalTracksUsedList =[]      
      numLogicalTracks = numBands * self.tracksPerBand[zn]      
      numNominalTracksUsed = float((TrackPitch * self.tracksPerBand[zn] + TrackGuard * 2)*numBands + 2*TrackGuard)/Q0toQ15Factor
      numNominalTracksUsedList.append(numNominalTracksUsed)
      OPnumNominalTracksUsed = float((OPTrackPitch * self.tracksPerBand[zn] + OPTrackGuard * 2)*numBands + 2*OPTrackGuard)/Q0toQ15Factor
      printDbgMsg("%2d  %2d  %f  %f  %f  %f  %f  %3d  %6d  %.7f  %.7f  %8d  %8d  %.2f  %7d  %7d  %.6f  %.4f  %8d  %8d" % (hd, zn, \
         zfi['TpiCapability'], zfi['TpiPick'],bandSizePicked, TPs, TPd, self.tracksPerBand[zn], \
         numBands, ShingledTrackPitch, GuardTrackPitch, TrackPitch, TrackGuard, numNominalTracksUsed, \
         numNominalTracksAlloc, numLogicalTracks, ShingledMargin, OPnumNominalTracksUsed, OPTrackPitch, OPTrackGuard))
      while numNominalTracksUsed <= numNominalTracksAlloc:
         numBands += 1
         numNominalTracksUsed = float((TrackPitch * self.tracksPerBand[zn] + TrackGuard * 2)*numBands + 2*TrackGuard)/Q0toQ15Factor
         numNominalTracksUsedList.append(numNominalTracksUsed)
         
         (ShingledTrackPitch, GuardTrackPitch, SqueezeMicrojog, ShingledMargin) = self.calculateTrackPitches(hd, zn, numBands, numNominalTracksAlloc)
         OPTrackPitch = int(ShingledTrackPitch * Q0toQ15Factor)
         OPTrackGuard = int(max(GuardTrackPitch * Q0toQ14Factor,0))
         OPnumNominalTracksUsed = float((OPTrackPitch * self.tracksPerBand[zn] + OPTrackGuard * 2)*numBands + 2*OPTrackGuard)/Q0toQ15Factor
         numLogicalTracks = numBands * self.tracksPerBand[zn]
         printDbgMsg("%2d  %2d  %f  %f  %f  %f  %f  %3d  %6d  %.7f  %.7f  %8d  %8d  %.2f  %7d  %7d  %.6f  %.4f  %8d  %8d" % (hd, zn, \
            zfi['TpiCapability'], zfi['TpiPick'],bandSizePicked, TPs, TPd, self.tracksPerBand[zn], \
            numBands, ShingledTrackPitch, GuardTrackPitch, TrackPitch, TrackGuard, numNominalTracksUsed, \
            numNominalTracksAlloc, numLogicalTracks, ShingledMargin, OPnumNominalTracksUsed, OPTrackPitch, OPTrackGuard))      
      return numNominalTracksUsedList
      
   #-------------------------------------------------------------------------------------------------------     
   def FindNewZnBoundary(self):
      objMsg.printMsg("Find New Zn Boundary")
      self.NewZB = {}
      for hd in xrange(self.numHeads):
         self.NewZB[hd] = {}
         for zn in xrange(self.numUserZones):
            self.NewZB[hd][zn] = {}
            
      NomTrkadjRecord =[]
      numNominalTracksUsedList = []
      printDbgMsg("Hd  Zn  Tpic      Tpip      BsizeP     TPs       TPd       TPB  NBands  STrkPitch  GTrkPitch  TrkPitch  TrkGuard  NNomTrkU  NNomTrk  NLogTrk  SMargin   OPNNomTrkU  OPTPitch  OPTGuard")
      for hd in xrange(self.numHeads):         
         NomTrkadj = 0         
         for zn in xrange(self.numUserZones):    
            pickerData = CVbarDataHelper(self, hd, zn)
            
            if zn in [0, self.dut.systemAreaUserZones[hd]+1]:            
               self.NewZB[hd][zn]['ZN_START_CYL'] = self.NominalZB[hd][zn]['ZN_START_CYL']               
            else:
               self.NewZB[hd][zn]['ZN_START_CYL'] = self.NewZB[hd][zn-1]['ZN_START_CYL'] + self.NewZB[hd][zn-1]['TRK_NUM']
            numNominalTracksAlloc = self.NominalZB[hd][zn]['TRK_NUM'] - int(NomTrkadj)     # OD adjust
            
            if (self.tracksPerBand[zn] > 1 and zn not in [self.dut.systemAreaUserZones[hd]] + TP.ZB_remain + TP.ZB_IDremain):            
               numNominalTracksUsedList = self.calculatenumNominalTracksUsed(hd, zn, numNominalTracksAlloc, pickerData['NumBands'])
               NomTrkDelta = numNominalTracksAlloc - numNominalTracksUsedList[len(numNominalTracksUsedList)-2]
               
               if zn in [0]:
                  BoundaryAdj = 'dec'
               elif self.NewZB[hd][zn]['ZN_START_CYL'] < self.NominalZB[hd][zn]['ZN_START_CYL']:
                  BoundaryAdj = 'inc'
               elif self.NewZB[hd][zn]['ZN_START_CYL'] > self.NominalZB[hd][zn]['ZN_START_CYL']:
                  BoundaryAdj = 'dec'
               else:
                  if abs(NomTrkDelta) > (self.tracksPerBand[zn]/pickerData['TpiPick'])/2:      # increase boundary of current zn                     
                     BoundaryAdj = 'inc'                    
                  else:                                         # decrease boundary of current zn
                     BoundaryAdj = 'dec'
                     
               if NomTrkDelta <= 0:
                  if BoundaryAdj == 'inc':
                     numBands = pickerData['NumBands']
                     NomTrkadj = -int(NomTrkDelta)
                     if NomTrkDelta < 0:
                        if NomTrkDelta < int(NomTrkDelta):
                           NomTrkadj = -int(NomTrkDelta) + 1
                     else:
                        NomTrkadj = 0
                  else:
                     numBandsDecrease = 0
                     while(NomTrkDelta < 0):
                        numBandsDecrease += 1
                        numNominalTracksUsedList = self.calculatenumNominalTracksUsed(hd, zn, numNominalTracksAlloc, pickerData['NumBands']-numBandsDecrease)
                        NomTrkDelta = numNominalTracksAlloc - numNominalTracksUsedList[len(numNominalTracksUsedList)-2]
                     numBands = pickerData['NumBands'] - numBandsDecrease
                     if NomTrkDelta >= 1:
                        NomTrkadj = -int(NomTrkDelta)
                     else:
                        NomTrkadj = 0
               else:
                  if BoundaryAdj == 'inc':
                     numBands = pickerData['NumBands'] + len(numNominalTracksUsedList)-1                                      
                     NomTrkadj = numNominalTracksUsedList[len(numNominalTracksUsedList)-1] - numNominalTracksAlloc                  
                     if NomTrkadj > int(NomTrkadj):
                        NomTrkadj = int(NomTrkadj) + 1
                     elif NomTrkadj == int(NomTrkadj):
                        NomTrkadj = int(NomTrkadj)
                  else:
                     numBands = pickerData['NumBands'] + len(numNominalTracksUsedList)-2
                     if NomTrkDelta >= 1:
                        NomTrkadj = -int(NomTrkDelta)
                     else:
                        NomTrkadj = 0
            else:
               numBands = pickerData['NumBands']
               NomTrkadj = 0
               
            NomTrkadjRecord.append(NomTrkadj)            
            self.NewZB[hd][zn]['TRK_NUM'] = numNominalTracksAlloc + int(NomTrkadj)    # ID adjust
            if debug_LBR:
               objMsg.printMsg("Hd %d  zn %d  numNominalTracksUsedList %s  ZnStartCyl %d  NewZnStartCyl %d  numTrk %d  NewnumTrk %d  NomTrkadj %d" % (hd, zn, numNominalTracksUsedList, self.NominalZB[hd][zn]['ZN_START_CYL'], \
                                                                                             self.NewZB[hd][zn]['ZN_START_CYL'], self.NominalZB[hd][zn]['TRK_NUM'], self.NewZB[hd][zn]['TRK_NUM'], int(NomTrkadj))) 
            numNominalTracksUsedList = self.calculatenumNominalTracksUsed(hd, zn, self.NewZB[hd][zn]['TRK_NUM'], numBands)   # just to display data after zn boundary adjust                        
               
      if not testSwitch.CM_REDUCTION_REDUCE_PRINTMSG:         
         objMsg.printMsg("HD  ZN  NomTrkAdj  ZN_START_CYL  TRK_NUM  NZN_START_CYL  NTRK_NUM")      
         for hd in xrange(self.numHeads):
            for zn in xrange(self.numUserZones):
               objMsg.printMsg("%2d  %2d  %9d  %12d  %7d  %13d  %8d" % (hd, zn, NomTrkadjRecord[(hd * self.numUserZones) + zn], \
                                                                        self.NominalZB[hd][zn]['ZN_START_CYL'], self.NominalZB[hd][zn]['TRK_NUM'], \
                                                                        self.NewZB[hd][zn]['ZN_START_CYL'], self.NewZB[hd][zn]['TRK_NUM']))
                                                                     
   #-----------------------------------------------------------------------------
   def adjustTPI(self,hd,worstzone,pickDelta):
      zn = worstzone #the input is just zone not worstzone
      zfi = CVbarDataHelper(self, hd, zn)
      if testSwitch.FE_0261758_356688_LBR and self.LBR:
         NumNominalTracks = self.NewZB[hd][zn]['TRK_NUM']         
      else:
         NumNominalTracks = zfi['NumNominalTracks']
         
      if debug_LBR: objMsg.printMsg("hd  zn  NBands  TPB  TpiP      TPd       TPs       STPitch   GTPitch   NNomTrk  SMargin")
      
      zfi['NumBands'] += pickDelta
      zfi['TpiPick'] = (zfi['NumBands'] * self.tracksPerBand[zn]) / float(NumNominalTracks)
      zfi['TpiFormat'] = int(round(zfi['TpiPick'] * self.formatScaler.RelativeToFormatScaler))
      # If the zone has been changed, set flag to update the format
      if self.bpiFile.hasSectorPerTrackInfo():
         zfi['AdjustedTpiFormat'] = (zfi['TpiFormat'] != self.formatScaler.getFormat(hd, zn, 'TPI')) and 'T' or 'F'
      else:
         if pickDelta != 0:
            zfi['AdjustedTpiFormat'] = 'T'      # Set up sentinel to force format update before getting capacity

      # Define useful terms to make the Increase and Decrease TPI conditionals below, easier to follow.
      TPIPickInitial = zfi['TpiPickInitial']   # Initial track pitch as a percent of nominal, prior to any adjustment.
      nextTPIPick    = float((zfi['NumBands']+1) * self.tracksPerBand[zn]) / NumNominalTracks # TPI at next higher setting
      prevTPIPick    = float((zfi['NumBands']-1) * self.tracksPerBand[zn]) / NumNominalTracks # TPI at next lower  setting
      marginAtNextTPIPick = self.calculateTrackPitchMargin(hd,zn,zfi['NumBands']+1)    # Margin at next higher track pitch.
      marginAtPrevTPIPick = self.calculateTrackPitchMargin(hd,zn,zfi['NumBands']-1)    # Margin at next lower track pitch.
      zfi['TpiMargin'] = self.calculateTrackPitchMargin(hd,zn,zfi['NumBands'])
      if testSwitch.FE_0269922_348085_P_SIGMUND_IN_FACTORY:
         self.tpiStepSize[hd][zn] = zfi['TpiMargin'] - marginAtNextTPIPick
      else:
         self.tpiStepSize[zn] = zfi['TpiMargin'] - marginAtNextTPIPick

      # Effective margin threshold = minimum allowed margin threshold plus a possible adjustment for heads with different write power table.
      if (testSwitch.VBAR_TPI_MARGIN_THRESHOLD_BY_HD_BY_ZN or testSwitch.VBAR_MARGIN_BY_OTC or testSwitch.FAST_2D_S2D_TEST):
         effectiveMarginThreshold = zfi['TpiMarginThresScalebyTP'] + self.dut.TPIMarginThresholdAdjust[hd]
      else:
         effectiveMarginThreshold = self.settings['TPIMarginThreshold'][zn] + self.dut.TPIMarginThresholdAdjust[hd]

      # Check to see if it is okay to increase the TPI Pick selection for this hd-zn combination.
      if ( (marginAtNextTPIPick < (effectiveMarginThreshold - RndErrCorrFactor)) or
           (nextTPIPick > TPI_MAX) or
           (abs(nextTPIPick - TPIPickInitial) > self.VbarHMSMaxTPIAdjust) or
           ((hd,zn) not in self.active_zones) ):
         zfi['OkToIncreaseTpi'] = 'F'
      else:
         zfi['OkToIncreaseTpi'] = 'T'

      # Check to see if it is okay to decrease the TPI Pick selection for this hd-zn combination.
      if ( (prevTPIPick < TPI_MIN) or
           (abs(prevTPIPick - TPIPickInitial) > self.VbarHMSMaxTPIAdjust) or
           ((hd,zn) not in self.active_zones) ):
         zfi['OkToDecreaseTpi'] = 'F'
      else:
         zfi['OkToDecreaseTpi'] = 'T'

      return (zfi['TpiMargin'] - marginAtNextTPIPick, marginAtPrevTPIPick - zfi['TpiMargin'])

   #-------------------------------------------------------------------------------------------------------
   def pickTPIForAHeadZone(self,hd,zn):
      zfi = CVbarDataHelper(self, hd, zn)
      (marginUp, marginDown) = self.adjustTPI(hd,zn,0)
      while True:
         margin = zfi['TpiMargin'] - zfi['TpiMarginTarget']
         marginOverThreshold = zfi['TpiMargin'] - (self.settings['TPIMarginThreshold'][zn] + self.dut.TPIMarginThresholdAdjust[hd])
         objMsg.printMsg("hd/zn %d %d tpimargin %f  tpiMTarg %f margin %f" % (hd,zn,zfi['TpiMargin'] , zfi['TpiMarginTarget'], margin))
         time.sleep(.1)
         if (margin >= marginUp/2.0) and (zfi['OkToIncreaseTpi'] == 'T'):
            (marginUp, marginDown) = self.adjustTPI(hd,zn,+1)
         elif ((margin < -marginDown/2.0) or (marginOverThreshold < - RndErrCorrFactor)) and (zfi['OkToDecreaseTpi'] == 'T'):
            (marginUp, marginDown) = self.adjustTPI(hd,zn,-1)
         else:
            break

   #-------------------------------------------------------------------------------------------------------
   def pickTPI(self, marginOverTPIM = 0):
      for hd in xrange(self.numHeads):
         if testSwitch.FE_0228288_336764_P_PAUSE_CRITICAL_LOCATION_AT_VBAR_FOR_LA_CM_REDUCTION:
            LoadAVG = None
            try:
               LoadAVG = int(GetLoadAverage()[0])
            except:
               try:
                  LoadAVG = int(GetCMLoadAvg()[0])
               except:
                  pass
            if LoadAVG:
               printDbgMsg("Load average = %d" % (LoadAVG))
               if LoadAVG >= 10:
                  time.sleep(30)
            else:
               objMsg.printMsg("Fail to get load average")
               
         for zn in xrange(self.numUserZones):
            zfi = CVbarDataHelper(self, hd, zn)
            (marginUp, marginDown) = self.adjustTPI(hd,zn,0)

            while True:
               if testSwitch.VBAR_TPI_MARGIN_THRESHOLD_BY_HD_BY_ZN or testSwitch.VBAR_MARGIN_BY_OTC or testSwitch.FAST_2D_S2D_TEST:
                  if marginOverTPIM:
                     margin = zfi['TpiMargin'] - zfi['TpiMarginTarget'] - (zfi['TpiMarginThresScalebyTP'] + self.dut.TPIMarginThresholdAdjust[hd])
                  else:
                     margin = zfi['TpiMargin'] - zfi['TpiMarginTarget']
                  marginOverThreshold = zfi['TpiMargin'] - (zfi['TpiMarginThresScalebyTP'] + self.dut.TPIMarginThresholdAdjust[hd])
               else:
                  margin = zfi['TpiMargin'] - zfi['TpiMarginTarget']
                  marginOverThreshold = zfi['TpiMargin'] - (self.settings['TPIMarginThreshold'][zn] + self.dut.TPIMarginThresholdAdjust[hd])

               if (margin >= marginUp/2.0) and (zfi['OkToIncreaseTpi'] == 'T'):
                  (marginUp, marginDown) = self.adjustTPI(hd,zn,+1)
               elif ((margin < -marginDown/2.0) or (marginOverThreshold < - RndErrCorrFactor)) and (zfi['OkToDecreaseTpi'] == 'T'):
                  (marginUp, marginDown) = self.adjustTPI(hd,zn,-1)
               else:
                  break

      self.setFormat('TPI')
   
   #-------------------------------------------------------------------------------------------------------
   def setFormat(self, metric, hd=0xff, zn=0xff, movezoneboundaries=False, maximize_zone = 1, \
         programZonesWithZipperZonesOnly = 0, print_table = 1, consolidateByZone = 0, set_one_tpb = 0):

      """
      setFormat sets the drive BPI and TPI formats to the requested values
      """

      if not self.sendFormatToDrive:
         return

      if testSwitch.FE_0257373_348085_ZONED_SERVO_CAPACITY_CALCULATION:
         if programZonesWithZipperZonesOnly and (hd != 0xff) and (zn != 0xff):
            if zn not in self.dut.dataZonesWithZipperZones[hd]:
               return

      prm_210 = {'test_num': 210,
                 'prm_name': 'Update Formats To Drive',
                 'timeout' : 1800,
                 #'dlfile'  : (CN, self.bpiFile.bpiFileName),
                 'spc_id'  : 0,
                 }
      if not testSwitch.FE_0269922_348085_P_SIGMUND_IN_FACTORY:
         prm_210.update({
                'dlfile'   : (CN,self.bpiFile.bpiFileName),
                })

      if testSwitch.WA_0152247_231166_P_POWER_CYCLE_RETRY_SIM_ERRORS:
         prm_210.update({
               'retryECList'       : [10335],
               'retryCount'        : 3,
               'retryMode'         : POWER_CYCLE_RETRY,
               })

         if testSwitch.TRUNK_BRINGUP: #trunk code see 10451 also
             prm_210.update({
                'retryECList'       : [10335,10451,10403,10468],
                })

      if testSwitch.FE_0147058_208705_SHORTEN_VBAR_LOGS:
         prm_210['stSuppressResults'] = ST_SUPPRESS__ALL

      starthead=hd
      endhead=hd
      if hd==0xff:
         endhead = self.numHeads-1
         starthead = 0
      startzone = zn
      endzone = zn
      if zn==0xff:
         startzone=0
         endzone=self.numUserZones-1
         
      if debug_LBR: objMsg.printMsg("Hd  Zn  Tpic      Tpip      BsizeP     TPs       TPd       TPB  NBands  STrkPitch  GTrkPitch  TrkPitch  TrkGuard  NNomTrkU  NNomTrk  NLogTrk  SMargin")
      
      # Consolidate the setting format by zone instead of head
      if consolidateByZone:
         commands = self.consolidateSettingFormatByZone(starthead, endhead, startzone, endzone, print_table, \
            maximize_zone, metric, set_one_tpb)
      else:
         # Container for the format update st calls
         commands = []

         # Iterate through all zones and build the T210 call packets for BPI and TPI
         # If heads/zones haven't changed since the last update, don't set them again
         # Combine zones that are equivalent in all respects
         nominalFormat = self.bpiFile.getNominalFormat()
         for zn in xrange(startzone,endzone+1):
            if testSwitch.FE_0257373_348085_ZONED_SERVO_CAPACITY_CALCULATION:
               if programZonesWithZipperZonesOnly:
                  for hd in xrange(starthead,endhead+1):
                     if zn in self.dut.dataZonesWithZipperZones[hd]:
                        break
                  else:
                     continue

            bpitables = []
            tpitables = []
            trackGuardTables = []
            shingleDirectionTables = []
            MicrojogSqueezeTables = []
            if not set_one_tpb:
               tracksPerBandTables = [self.tracksPerBand[zn],]*T210_PARM_NUM_HEADS
            else:
               tracksPerBandTables = [1,]*T210_PARM_NUM_HEADS

            bpi_head_mask = 0
            tpi_head_mask = 0
            
            for hd in xrange(T210_PARM_NUM_HEADS):
               pickerData = CVbarDataHelper(self, hd, zn)
               if hd >= starthead and hd <= endhead:
                  # BPI formats
                  bpitables.append(nominalFormat+pickerData['BpiFormat'])
                  # Track Pitch formats
                  if not set_one_tpb:
                     temp1, temp2, temp3 = self.calculateTrackPitchParameters(hd,zn,maximize_zone=maximize_zone,print_table=print_table)
                     tpitables.append(temp1)
                     trackGuardTables.append(temp2)
                     squeeze = temp3
                     shingleDirectionTables.append(pickerData['ShingleDirection'])
                  else:
                     tpitables.append(int(Q0toQ15Factor/pickerData['TpiCapability']))
                     trackGuardTables.append(0)
                     squeeze = 0
                     shingleDirectionTables.append(SHINGLE_DIRECTION_OD_TO_ID)
                  if self.use_OTC_Rd_Offset:
                     squeeze = int(pickerData['ReadOffset']/2)
                  MicrojogSqueezeTables.append(squeeze)
                  # head masks
                  if testSwitch.FE_0257373_348085_ZONED_SERVO_CAPACITY_CALCULATION:
                     if programZonesWithZipperZonesOnly:
                        if zn in self.dut.dataZonesWithZipperZones[hd]:
                           if pickerData['AdjustedBpiFormat'] == 'T':
                              bpi_head_mask |= 1 << hd
                              #objMsg.printMsg("setformat (BPI)of ZWZ hd = %d zn = %d" % (hd, zn ))
                           if pickerData['AdjustedTpiFormat'] == 'T':
                              tpi_head_mask |= 1 << hd
                              self.bTPIchangedReloadZoneTbl = True  # TPI has changed, indicate the current zone table is now invalid and will need to be refreshed.
                              #objMsg.printMsg("setformat (TPI)of ZWZ hd = %d zn = %d" % (hd, zn ))
                     else:
                        if pickerData['AdjustedBpiFormat'] == 'T':
                           bpi_head_mask |= 1 << hd
                           #objMsg.printMsg("setformat (BPI)of not ZWZ hd = %d zn = %d" % (hd, zn ))
                        if pickerData['AdjustedTpiFormat'] == 'T':
                           tpi_head_mask |= 1 << hd
                           self.bTPIchangedReloadZoneTbl = True  # TPI has changed, indicate the current zone table is now invalid and will need to be refreshed.
                           #objMsg.printMsg("setformat (TPI)of not ZWZ hd = %d zn = %d" % (hd, zn ))
                     if zn in self.dut.dataZonesWithZipperZones[hd]:
                        self.needToGetZonesWithZipperZonesCapFromSF3 = 1
                  else:
                     if pickerData['AdjustedBpiFormat'] == 'T':
                        bpi_head_mask |= 1 << hd

                     if pickerData['AdjustedTpiFormat'] == 'T':
                        tpi_head_mask |= 1 << hd
                        self.bTPIchangedReloadZoneTbl = True  # TPI has changed, indicate the current zone table is now invalid and will need to be refreshed.

               else:
                  # BPI formats
                  bpitables.append(nominalFormat)
                  # Track Pitch formats
                  tpitables.append(Q0toQ15Factor)           # default to 1.0 Nominal Tracks
                  trackGuardTables.append(0)                # default to 0.0 Nominal Tracks
                  shingleDirectionTables.append(SHINGLE_DIRECTION_OD_TO_ID)
                  MicrojogSqueezeTables.append(0)
               
            # Issue BPI and TPI separately if the head masks don't match
            if metric == 'BOTH' and bpi_head_mask != tpi_head_mask:
               metrics = ['BPI', 'TPI']
            else:
               metrics = [metric]

            for local_metric in metrics:
               # Build the command packet
               command = {
                           'CWORD1'    : 0x0100,
                           'HEAD_MASK' : 0x0000,
                           'ZONE'      : (zn << 8) | zn,
                           'CWORD2'    : 0x0000,
                         }

               if local_metric in ('BPI', 'BOTH'):
                  command['CWORD1'] |= SET_BPI
                  command['HEAD_MASK'] |= bpi_head_mask
                  command['BPI_GROUP_EXT'] = bpitables

               if local_metric in ('TPI', 'BOTH'):
                  command['CWORD1'] |= SET_TPI

                  command['HEAD_MASK'] |= tpi_head_mask

                  command['CWORD2'] |= CW2_SET_TRACK_PITCH
                  command['TRK_PITCH_TBL'] = tpitables

                  command['CWORD2'] |= CW2_SET_TRACK_GUARD
                  command['TRK_GUARD_TBL'] = trackGuardTables

                  command['CWORD2'] |= CW2_SET_SHINGLED_DIRECTION
                  command['SHINGLED_DIRECTION'] = shingleDirectionTables

                  command['CWORD2'] |= CW2_SET_TRACKS_PER_BAND
                  command['TRACKS_PER_BAND'] = tracksPerBandTables

                  if self.updateShingleDirection:
                     command['CWORD2'] |= CW2_SET_SHINGLED_DIRECTION
                     command['SHINGLED_DIRECTION'] = shingleDirectionTables

                  if self.updateSqueezeMicrojog:
                     command['CWORD2'] |= CW2_SET_SQUEEZE_MICROJOG
                     command['MICROJOG_SQUEEZE'] = MicrojogSqueezeTables
                     for hd in range(starthead,endhead+1):
                        tpi_head_mask |= 1 << hd
                     command['HEAD_MASK'] |= tpi_head_mask
               if local_metric in ('UJOG'):
                  command['CWORD1'] |= SET_TPI
                  command['CWORD2'] |= CW2_SET_SQUEEZE_MICROJOG
                  command['MICROJOG_SQUEEZE'] = MicrojogSqueezeTables
                  for hd in range(starthead,endhead+1):
                     tpi_head_mask |= 1 << hd
                  command['HEAD_MASK'] |= tpi_head_mask

               # If no heads are active, skip the command altogether
               if command['HEAD_MASK'] == 0:
                  continue

               # Look for other identical zones
               for previous in commands:
                  keys_to_compare = command.keys()
                  keys_to_compare.remove("ZONE")  # Don't compare zones - they're always different
                  equal = reduce(lambda x, y: x and y, [previous.get(key, None) == command.get(key, None) for key in keys_to_compare])
                  if equal and ((previous["ZONE"] & 0xFF) == zn - 1):
                     # Include the new zone and move on
                     previous["ZONE"] &= 0xFF00
                     previous["ZONE"] |= zn
                     break
               else:
                  # No matches; add the new command
                  commands.append(command)

      # Actually issue the commands
      for command in commands:
         parms = prm_210.copy()
         parms.update(command)
         parms['prm_name'] = t210PrmName(parms, ByZone=consolidateByZone)

         if not (testSwitch.VBAR_2D_DEBUG_MODE or testSwitch.DO_NOT_SAVE_FORMAT):
            getVbarGlobalClass(CProcess).St(parms)
         else:
            objMsg.printMsg('BYPASS 2D VBAR FORMAT SETTING=================================================================')

         # Mark these zones as "Reset" so that they get re-optimized and measured
         if command['CWORD1'] & SET_BPI:
            startzn = (command['ZONE'] & 0xFF00) >> 8
            endzn   = (command['ZONE'] & 0x00FF)
            for hd in xrange(starthead, endhead+1):
               if command['HEAD_MASK'] & (1 << hd):
                  for zn in xrange(startzn, endzn+1):
                     self.measurements.setRecord('BPIChanged', 'T', hd, zn)

         # Clear the OPTI_ZAP_DONE flag if TPI is changed
         if command['CWORD1'] & SET_TPI:
            self.dut.driveattr['OPTI_ZAP_DONE'] = 0
      getVbarGlobalVar()['formatReload'] = True

###########################################################################################################
###########################################################################################################
class CSmrMarginPicker(CDesperadoPicker):
   def pickBPITPI(self):
      """
      Pick to margin requirements instead of capacity.
      """
      objMsg.printMsg('*'* 30 + ' CONSTANT MARGIN FORMAT PICKER ' + '*'*30)

      # Initialize the margin targets -> Acheive these margin targets if you can.
      self.store['TpiMarginTarget'] = array('f', [float(TP.VTPIConstantMarginTarget)]*self.numUserZones*self.numHeads)

      # Pick TPI for each head and zone and display the data
      objMsg.printMsg('Initial Picks')
      self.pickTPI()   # Step through TPI settings, (heads/zones), till we get as close as possible to the TpiMarginTarget.
      self.pickBPI()   # Step through BPI settings, (heads/zones), till we get as close as possible to the BpiMarginTarget. (BPI will not change here)

      objMsg.printMsg('Final Density: %6.4f' % self.getAvgDensity())

      self.sendFormatToDrive = True
      self.BpiFileCapacityCalc = False

      #Force to update by head by zone the BPI config as the T176 need all zone SgateToRgate timing reload back to default
      if testSwitch.FORCE_UPDATE_BPI_ALL_HEADS_ALL_ZONES:
         self.store['AdjustedBpiFormat'] = array('c', ['T']*self.numUserZones*self.numHeads)

      self.setFormat("BOTH")

      # Compute and optionally print the data to the log, based on log size reduction switch.
      self.computeMargins()

      self.updateSummaryByZone()
      self.updateSummaryByHead()

      # Set the write fault threshold based on the new format.
      self.SetWFT()

      # Write RAP and SAP data to flash
      getVbarGlobalClass(CProcess).St({'test_num': 178, 'prm_name': 'prm_wp_178', 'CWORD1':0x0620, 'timeout': 1200, 'spc_id': 0,})

      # Post final capacity to FIS
      getVbarGlobalClass(CProcess).St({'test_num':210,'CWORD1':8, 'SCALED_VAL': int(self.settings['PBA_TO_LBA_SCALER'] * 10000), 'spc_id':1})

      return ATPI_PASS

###########################################################################################################
###########################################################################################################
###########################################################################################################
class CTripletPicker:
   """
   Measure Triplet vs ADC
   """
   def __init__(self, niblet = None, measurements = None):
      objMsg.printMsg('--- WRITE TRIPLET OPTI ---')
      self.__dut = objDut
      self.numHeads = self.__dut.imaxHead
      self.BurnishFailedHeads = self.__dut.BurnishFailedHeads
      self.__numUserZones = self.__dut.numZones
      self.oUtility = getVbarGlobalClass(CUtility)
      self.formatScaler = CVbarFormatScaler()
      self.measWPZns = CVbarWpMeasurement(TP.Triplet_Zones)
      printDbgMsg('TEST ZONE %s' % self.measWPZns.objTestZones)
   if testSwitch.SMR_TRIPLET_OPTI_WITH_EFFECTIVE_TPIC:
         self.settings = niblet.settings
         self.tracksPerBand = self.settings['TracksPerBand']
         self.measurements = measurements
         self.opMode = 'WpZones'

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from PreAmp import CPreAmp
      if testSwitch.FE_0251897_505235_STORE_WPC_RANGE_IN_SIM:
         from RdWr import CWpcRangeFile
         self.oWpcRangeFile = CWpcRangeFile()
      self.oPreamp = CPreAmp()
      headvendor = str(self.__dut.HGA_SUPPLIER)
      self.oProc = getVbarGlobalClass(CProcess)
      Def_Triplet = list(TP.VbarWpTable[self.__dut.PREAMP_TYPE]['ALL'][2])
      if testSwitch.extern._128_REG_PREAMPS:
         Def_Triplet[0] = (Def_Triplet[0] - 20) / 7
         Def_Triplet[1] /= 2
         Def_Triplet[2] /= 2

      self.MinIwAdjust = {}
      self.MaxIwAdjust = {}
      for hd in range(self.numHeads):
         self.MinIwAdjust[hd] = {}
         self.MaxIwAdjust[hd] = {}
         if testSwitch.FE_348429_0247869_TRIPLET_INTEGRATED_ATISTE:
            self.MaxIwAdjust[hd] = TP.IwMaxCap[0]
         else:
            self.MaxIwAdjust[hd] = TP.IwMaxCap

      # Get EWAC Data
      Hd_EWAC_Data = {}
      if testSwitch.FE_348429_0247869_TRIPLET_INTEGRATED_ATISTE and not testSwitch.RUN_TPINOMINAL1:
         Hd_EWAC_Data = self.getHeadWPE_IwMax()
      elif not (testSwitch.SMR):
         self.getHeadWPE_IwMax()

      #Get DIBIT Data
      if not (testSwitch.SMR):
         self.getHeadDibit_IwMin()

      #------------------------------------------------------------------------------------
      # WPC Process Settings
      self.__prmTripletMeasWPC = {'test_num'           : 211,
                           'prm_name'           : 'MeasureTripletWPC_211',
                           'timeout'            : TP.VbarMeasNumTrksPerZone*TP.VbarMeasTrkTimeout,
                           'spc_id'             : 0,
                           'NUM_TRACKS_PER_ZONE': TP.VbarMeasNumTrksPerZone,
                           'ZONE_POSITION'      : 198, # work around for FLASH_LED issues in st 211 originally 199
                           'BPI_MAX_PUSH_RELAX' : TP.VbarBpiMaxPushRelax,
                           'CWORD1'             : 0x1001 ,
                           'CWORD2'             : 0x0010 ,
                           'CWORD3'             : 0x8000 ,
                           'TLEVEL'             : 0,
                           'TARGET_SER'         : TP.VbarTargetSER,
                           'THRESHOLD'          : 65,
                           'SET_OCLIM'          : 655,
                           'REVS'               : 1,
         }
      #------------------------------------------------------------------------------------
      # BPI Process Settings
      self.__prmTripletMeasBPI = {'test_num'           : 211,
                           'prm_name'           : 'MeasureTripletBPI_211',
                           'timeout'            : TP.VbarMeasNumTrksPerZone*TP.VbarMeasTrkTimeout,
                           'spc_id'             : 0,
                           'NUM_TRACKS_PER_ZONE': TP.VbarMeasNumTrksPerZone,
                           'ZONE_POSITION'      : 198, # work around for FLASH_LED issues in st 211 originally 199
                           'BPI_MAX_PUSH_RELAX' : TP.VbarBpiMaxPushRelax,
                           'CWORD1'             : 0x01 ,
                           'CWORD2'             : 0x0010 ,
                           'TLEVEL'             : 0,
                           'TARGET_SER'         : TP.VbarTargetSER,
                           'THRESHOLD'          : 65,
                           'SET_OCLIM'          : 655,
                           'REVS'               : 1,
         }
      #------------------------------------------------------------------------------------
      # TPI Process Settings
      self.__prmTripletMeasTPI = {'test_num'           : 211,
                           'prm_name'           : 'MeasureTripletTPI_211',
                           'timeout'            : TP.VbarMeasNumTrksPerZone*TP.VbarMeasTrkTimeout,
                           'spc_id'             : 0,
                           'NUM_TRACKS_PER_ZONE': TP.VbarMeasNumTrksPerZone,
                           'NUM_SQZ_WRITES'     : TP.VbarMeasNumSqzWrites,
                           'ZONE_POSITION'      : 198,# work around for FLASH_LED issues in st 211 originally 199
                           'ADJ_BPI_FOR_TPI'    : TP.VbarAdjBpiForTpi, # According to the algorithm, we need to use BPI capability minus the BPI margin to test TPI capability
                           'CWORD1'             : 0x2 ,
                           'TPI_TARGET_SER'     : 5,
                           'TPI_TLEVEL'         : TP.TPI_TLEVEL,
                           'SET_OCLIM'          : 655,
                           'REVS'               : 1,
                           'THRESHOLD'          : 65,
                           'RESULTS_RETURNED'   : 0xF,
         }
      #------------------------------------------------------------------------------------
      #oFSO.getAFHWorkingAdaptives(100, self.__dut.numZones)
      #headvendor = str(self.__dut.HGA_SUPPLIER)
      #if not headvendor == 'RHO':
      #   self.__prmTripletMeasTPI.update( {'TARGET_SER': 10, } )

      #ZnLumping = {0:(0,1,2,3,4)}#, 12:(5,6,7,8,9,10,11,12,13,14,15,16,17,18,24), 23:(19,20,21,22,23)}
      #ZnLumping = {0:(0,1), 2:(2,3,4), 12:(5,6,7,8,9,10,11,12,13,14,15,16,17,18), 21:(19,20,21), 23:(22,23,24)}
      #ZnLumping = CVbarTestZones().getTestZoneMap()
      #ZnLumping = {0: [0, 1, 2], 4: [3, 4, 5, 6, 7], 12: [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 24], 21: [19, 20, 21], 23: [22, 23]}
      #ZnLumping = {0: [0], 1: [1], 2: [2], 3: [3], 4: [4], 5: [5], 6: [6], 7: [7], 8: [8], 9: [9], 10: [10], 11: [11], 12: [12, 24], 13: [13], 14: [14], 15: [15], 16: [16], 17: [17], 18: [18], 19: [19], 20: [20], 21: [21], 22: [22], 23: [23]}
      ZnLumping = {}
      for zone in range(self.__numUserZones):
          ZnLumping[zone] = [zone]
      if 0 in self.__dut.systemAreaUserZones: # just use head 0 value
         ZnLumping[self.__dut.systemAreaUserZones[0]].append(self.__numUserZones)
      else: raise

      ZnOrder = self.measWPZns.objTestZones
      Level1MeasZoneCount = 2
      Level2MeasZoneCount = 5
      printDbgMsg('ZnLumping: %s' % ZnLumping)

      # Cater for Head Range when re-AFH2
      if testSwitch.SMR_TRIPLET_OPTI_WITH_EFFECTIVE_TPIC == 1:
         self.FinalBPICandTPIC ={}
         self.tempFinalBPICandTPIC ={}
      if len(self.BurnishFailedHeads) != 0 and testSwitch.AFH2_FAIL_BURNISH_RERUN_AFH1:
         headRange = self.BurnishFailedHeads
         T172_spc_id = 202
      else:
         headRange = range(self.numHeads)
         T172_spc_id = 102

      ##########################
      #    Start WPC TUNING    #
      ##########################
      if testSwitch.FE_TRIPLET_WPC_TUNING and not testSwitch.KARNAK and (len(self.BurnishFailedHeads) == 0):
         curSeq,occurrence,testSeqEvent = self.__dut.objSeq.registerCurrentTest(0)

         wpc_zn = sorted(ZnOrder)
         wpc_zn_lumping = {}
         wpc_triplet = list(Def_Triplet)
         # build the zone lumping based on test zones
         for index in range(len(wpc_zn)):
            if index != len(wpc_zn) - 1:
               mid_zn = wpc_zn[index] + int((wpc_zn[index+1] - wpc_zn[index]) / 2)
               for zones in range(wpc_zn[index], mid_zn):
                  if not wpc_zn_lumping.has_key(wpc_zn[index]):
                     wpc_zn_lumping[wpc_zn[index]] = []
                  wpc_zn_lumping[wpc_zn[index]].append(zones)
               for zones in range(mid_zn, wpc_zn[index+1]):
                  if not wpc_zn_lumping.has_key(wpc_zn[index+1]):
                     wpc_zn_lumping[wpc_zn[index+1]] = []
                  wpc_zn_lumping[wpc_zn[index+1]].append(zones)
            else:
               wpc_zn_lumping[wpc_zn[index]].append(wpc_zn[index])
         objMsg.printMsg('wpc_zn_lumping: %s' % (wpc_zn_lumping))

         if testSwitch.FE_TRIPLET_WPC_TUNING_PF3_VERSION:
            if mfr == "TI":
               wpc_triplet[1] = 3 # override OSA
            if headvendor != 'RHO':
               wpc_triplet[0] = 7 # override IW
               #if mfr == "TI":
               #   Def_Triplet[0] = 4 # use lower Iw sweep for TI
            wpc_triplet[0] = min(11, wpc_triplet[0]) # make sure have enough sweep range
            wpc_ref = self.__measureTripletWPC_PF3(headRange , wpc_zn, wpc_triplet)
            if headvendor != 'RHO': # impletment WPC CAP only for Non RHO at the moment.
               for hd in headRange:
                  for zn in wpc_zn:
                     Wpc_Cap = max(wpc_ref[hd][zn]['WPC_CAP'],1)

                     slope_Cap = wpc_ref[hd][zn]['SLOPE']
                     intercept_Cap = wpc_ref[hd][zn]['INTERCEPT']
                     Rsq_Cap = wpc_ref[hd][zn]['RSQ']
                     for zns in wpc_zn_lumping[zn]:
                        self.__dut.dblData.Tables('P_TRIPLET_WPC').addRecord({
                        #{
                           'SPC_ID'          : T172_spc_id,
                           'OCCURRENCE'      : occurrence,
                           'SEQ'             : curSeq,
                           'TEST_SEQ_EVENT'  : testSeqEvent,
                           'HD_PHYS_PSN'     : self.__dut.LgcToPhysHdMap[hd],
                           'DATA_ZONE'       : zns,
                           'HD_LGC_PSN'      : hd,
                           'WRT_CUR'         : wpc_triplet[0],
                           'OVRSHT'          : wpc_triplet[1],
                           'OVRSHT_DUR'      : wpc_triplet[2],
                           'WPC'             : Wpc_Cap,
                           'SLOPE'           : round(slope_Cap, 5),
                           'INTERCEPT'       : round(intercept_Cap, 4),
                           'RSQ'             : round(Rsq_Cap, 2)
                        })
         else:
            # Start the WPC Measurements
            for hd in headRange:
               Wpc_Max = 20
               for zn in wpc_zn:
                  #if mfr == "TI":
                  #   Def_Triplet[1] = 3 # override OSA
                  if headvendor != 'RHO':
                     wpc_triplet[0] = 7 # override IW
                     if mfr == "TI":
                        wpc_triplet[0] = 4 # use lower Iw sweep for TI
                  Wpc_Cap, slope_Cap, intercept_Cap, Rsq_Cap = self.__measureTripletWPC(hd , zn, Def_Triplet)
                  Wpc_Cap = max(Wpc_Cap,1) # Make sure it is at least 1
                  for zns in wpc_zn_lumping[zn]:
                     self.__dut.dblData.Tables('P_TRIPLET_WPC').addRecord({
                     #{
                        'SPC_ID'          : T172_spc_id,
                        'OCCURRENCE'      : occurrence,
                        'SEQ'             : curSeq,
                        'TEST_SEQ_EVENT'  : testSeqEvent,
                        'HD_PHYS_PSN'     : self.__dut.LgcToPhysHdMap[hd],
                        'DATA_ZONE'       : zns,
                        'HD_LGC_PSN'      : hd,
                        'WRT_CUR'         : wpc_triplet[0],
                        'OVRSHT'          : wpc_triplet[1],
                        'OVRSHT_DUR'      : wpc_triplet[2],
                        'WPC'             : Wpc_Cap,
                        'SLOPE'           : round(slope_Cap, 5),
                        'INTERCEPT'       : round(intercept_Cap, 4),
                        'RSQ'             : round(Rsq_Cap, 2)
                     })

         objMsg.printDblogBin(self.__dut.dblData.Tables('P_TRIPLET_WPC'), T172_spc_id)

         # Tune the Write Precomm using T251
            # Get WPC Reference Table
         tableData = None
         try:
            colDict = self.__dut.dblData.Tables('P_TRIPLET_WPC').columnNameDict()
            tableData = self.__dut.dblData.Tables('P_TRIPLET_WPC').rowListIter()
         except: pass
         if tableData:
            WPC_table = {}
            for row in tableData:
               hd = int(tableData[colDict['HD_PHYS_PSN']])
               zn = int(tableData[colDict['DATA_ZONE']])
               WPC_table[hd,zn] = int(tableData[colDict['WPC']])
            objMsg.printMsg('WPC_table: %s' % (WPC_table))
            
            if testSwitch.FE_0251897_505235_STORE_WPC_RANGE_IN_SIM:
               # Save WPC range to SIM file
               self.oWpcRangeFile.Save_WpcRange(tableData, True)

            # Tune per same WPC
            wpcT251_prm = TP.WPC_OptiPrm_251.copy()
            for hd in headRange:
               testZones=[]
               testZones = sorted(ZnOrder)

               while len(testZones) > 0:
                  objMsg.printMsg('testZones Start: %s' % (testZones))
                  wpc = WPC_table[hd,testZones[0]]
                  objMsg.printMsg('wpc: %d' % (wpc))
                  curtestZones = []
                  pendingzone = []
                  for zn_idx in range(len(testZones)):
                     if wpc == WPC_table[hd,testZones[0]]:
                        curtestZones.append(testZones.pop(0))
                     else:
                        pendingzone.append(testZones.pop(0))
                  objMsg.printMsg('curtestZones: %s' % (curtestZones))
                  objMsg.printMsg('pendingzone: %s' % (pendingzone))

                  Wpc_Start = 0
                  if wpc < 5:
                     Wpc_Start = wpc

                  zone_mask_low = 0
                  zone_mask_high = 0
                  for zone in curtestZones:
                     if zone < 32:
                        zone_mask_low |= (1 << zone)
                     else:
                        zone_mask_high |= (1 << (zone - 32))

                  wpcT251_prm.update({'BIT_MASK':self.oUtility.ReturnTestCylWord(zone_mask_low),
                                      'BIT_MASK_EXT':self.oUtility.ReturnTestCylWord(zone_mask_high),
                                      'REG_TO_OPT1': (0x155, wpc, Wpc_Start, -1), 'TEST_HEAD': hd ,
                                      'REG_TO_OPT2': (0x152, 0, 14, 1) ,
                                      'REG_TO_OPT2_EXT': (0x10, 1, 0x1440)})
                  self.oProc.St(wpcT251_prm)

                  testZones = list(pendingzone)
                  objMsg.printMsg('testZones post: %s' % (testZones))

            #update everything to Flash
            self.oProc.St({'test_num':178, 'prm_name':'Save RAP and SAP in RAM to FLASH', 'CWORD1':0x620})

         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1) # power cycle to reset WPC
         #return
      ##########################
      #    End WPC TUNING    #
      ##########################
      # Get min OSA/OSD
      if testSwitch.FE_ENHANCED_TRIPLET_OPTI and headvendor != 'RHO' and (len(self.BurnishFailedHeads) == 0):
         curSeq,occurrence,testSeqEvent = self.__dut.objSeq.registerCurrentTest(0)
         wpc_zn = sorted(ZnOrder)
         # build the zone lumping based on test zones
         wpc_zn_lumping = {}
         for index in range(len(wpc_zn)):
            if index != len(wpc_zn) - 1:
               mid_zn = wpc_zn[index] + int((wpc_zn[index+1] - wpc_zn[index]) / 2)
               for zones in range(wpc_zn[index], mid_zn):
                  if not wpc_zn_lumping.has_key(wpc_zn[index]):
                     wpc_zn_lumping[wpc_zn[index]] = []
                  wpc_zn_lumping[wpc_zn[index]].append(zones)
               for zones in range(mid_zn, wpc_zn[index+1]):
                  if not wpc_zn_lumping.has_key(wpc_zn[index+1]):
                     wpc_zn_lumping[wpc_zn[index+1]] = []
                  wpc_zn_lumping[wpc_zn[index+1]].append(zones)
            else:
               wpc_zn_lumping[wpc_zn[index]].append(wpc_zn[index])
         objMsg.printMsg('wpc_zn_lumping: %s' % (wpc_zn_lumping))
         wpc_triplet = TP.START_TRIPLET #list(Def_Triplet)
         wpc_triplet[0] = min(11, wpc_triplet[0])
         osa_osd_limit = self.getMin_OsaOsd(headRange, wpc_zn, wpc_triplet, Osa_max = TP.OSA_MAX_SWEEP, Osd_max = TP.OSD_MAX_SWEEP, wpc_slope_limt = TP.WPC_SLOPE_LIMIT, wpc_intercept_limit = TP.WPC_INTERCEPT_LIMIT)
         for hd in headRange:
            for zn in wpc_zn:
               for zns in wpc_zn_lumping[zn]:
                  if not osa_osd_limit.has_key((hd,zns)):
                     osa_osd_limit[hd,zns] ={}
                  osa_osd_limit[hd,zns]['OSA_CAP'] = osa_osd_limit[hd,zn]['OSA_CAP']
                  osa_osd_limit[hd,zns]['OSD_CAP'] = osa_osd_limit[hd,zn]['OSD_CAP']
                  osa_osd_limit[hd,zns]['SLOPE'] = osa_osd_limit[hd,zn]['SLOPE']
                  osa_osd_limit[hd,zns]['INTERCEPT'] = osa_osd_limit[hd,zn]['INTERCEPT']
                  osa_osd_limit[hd,zns]['RSQ'] = osa_osd_limit[hd,zn]['RSQ']
                  self.__dut.dblData.Tables('P_TRIPLET_OSA_OSD').addRecord({
                  #{
                     'SPC_ID'          : T172_spc_id,
                     'OCCURRENCE'      : occurrence,
                     'SEQ'             : curSeq,
                     'TEST_SEQ_EVENT'  : testSeqEvent,
                     'HD_PHYS_PSN'     : self.__dut.LgcToPhysHdMap[hd],
                     'DATA_ZONE'       : zns,
                     'HD_LGC_PSN'      : hd,
                     'WRT_CUR'         : wpc_triplet[0],
                     'OVRSHT'          : osa_osd_limit[hd,zns]['OSA_CAP'],
                     'OVRSHT_DUR'      : osa_osd_limit[hd,zns]['OSD_CAP'],
                     'SLOPE'           : round(osa_osd_limit[hd,zns]['SLOPE'], 5),
                     'INTERCEPT'       : round(osa_osd_limit[hd,zns]['INTERCEPT'], 4),
                     'RSQ'             : round(osa_osd_limit[hd,zns]['RSQ'], 2)
                  })
         objMsg.printDblogBin(self.__dut.dblData.Tables('P_TRIPLET_OSA_OSD'), 0)

      ##############################
      #    Start ATI/STE TUNING    #
      ##############################
      if testSwitch.FE_348429_0247869_TRIPLET_INTEGRATED_ATISTE:
         WP_index = self.find_max_triplet_integrated_ATISTE(headRange, TP.Triplet_ATI_STE_Test_Zone, Def_Triplet, Hd_EWAC_Data)
         for hd in headRange:
            if WP_index[hd] == len(TP.IwMaxCap):
               # Raise Exception here
               if 0: 
                  raiseException(14635,"hd %d Triplet ATI STE failed." %(hd))
               objMsg.printMsg('hd %d Triplet ATI STE failed.' % (hd))
               WP_index[hd] = len(TP.IwMaxCap) -1
      #return
      ##############################
      #    End ATI/STE TUNING      #
      ##############################

      sweepList_Cross = {}
      nIndex = 0
      self.tpiCap_FeedForward = -1

      self.nPwrIndex = -1
      self.FinalTripletPick={}
      self.tempFinalTripletPick={}
      self.TripletMeas = {}
      # ------------------- INITIAL SWEEP
      # Assemble the Initial Sweep List
      Stage1Matrix = TP.Stage1Matrix
      tIndex = 0
      for nWc in Stage1Matrix:
         for nOa in range(len(Stage1Matrix[nWc])):
            if Stage1Matrix[nWc][nOa] == 1:
               sweepList_Cross[tIndex] = nWc, nOa + 1, Def_Triplet[2]
               tIndex += 1
      
      if testSwitch.FE_348429_0247869_TRIPLET_INTEGRATED_ATISTE:
         # copy the default sweeplist
         sweepList_Cross_default = deepcopy(sweepList_Cross)
         # define max cap per head so as not disturb main code for now
         IwMaxCap_hd = {}
         OaMaxCap_hd = {}
         
      for hd in headRange:
         if testSwitch.FE_348429_0247869_TRIPLET_INTEGRATED_ATISTE:
            # Set Max IW/OA
            IwMaxCap = TP.IwMaxCap[WP_index[hd]] - TP.Iw_Add_Mgn # additional backoff
            OaMaxCap = TP.OaMaxCap[WP_index[hd]] - TP.Osa_Add_Mgn # put 1DAC Margin as per request by RSS
            
            # Define the 4 points to be tested on initial sweep
            Iw_pts  = [TP.IwMinCap, int( round(( IwMaxCap - TP.IwMinCap ) / 3.0, 0)) + TP.IwMinCap, int( round(( IwMaxCap - TP.IwMinCap ) * 2 / 3.0, 0)) + TP.IwMinCap , IwMaxCap]
            Osa_pts = [TP.OaMinCap, int( round(( OaMaxCap - TP.OaMinCap ) / 3.0, 0)) + TP.OaMinCap, int( round(( OaMaxCap - TP.OaMinCap ) * 2 / 3.0, 0)) + TP.OaMinCap , OaMaxCap]
            printDbgMsg('Hd %d Use ATI STE Max Triplet:' % (hd))
            
            # build initial sweep list from 4 points
            self.Areas, sweepList_Cross = self.build_Initial_Sweeplist(Iw_pts, Osa_pts, Def_Triplet[2])
         else:
            IwMaxCap = TP.IwMaxCap
            OaMaxCap = TP.OaMaxCap
         
         IwMinCap = TP.IwMinCap
         OaMinCap = TP.OaMinCap
         OdMinCap = TP.OdMinCap
         
         if self.MaxIwAdjust and not testSwitch.WA_0256539_480505_SKDC_M10P_BRING_UP_DEBUG_OPTION:
            if self.MaxIwAdjust[hd] < IwMaxCap:
               objMsg.printMsg('Override Iw Max by EWAC Hd:%d  MaxIw:%s  NewMaxIw:%s' %(hd, IwMaxCap, self.MaxIwAdjust[hd]))
               IwMaxCap = self.MaxIwAdjust[hd]

         if testSwitch.FE_348429_0247869_TRIPLET_INTEGRATED_ATISTE:
            # define another copy here for capping the filtered values
            IwMaxCap_hd[hd] = IwMaxCap
            OaMaxCap_hd[hd] = OaMaxCap
            
         Osd = Def_Triplet[2]
         self.FinalTripletPick[hd] = {}
         self.tempFinalTripletPick[hd] = {}
         if testSwitch.SMR_TRIPLET_OPTI_WITH_EFFECTIVE_TPIC == 1:
            self.FinalBPICandTPIC[hd] = {}
            self.tempFinalBPICandTPIC[hd] = {}
         nX1 = 99
         MeasZone = 0
         for zn in ZnOrder:

            # Set Min IW/OA
            if self.MinIwAdjust[hd]:
               if self.MinIwAdjust[hd][zn] > IwMaxCap:
                  objMsg.printMsg('Dibit Iw Min is more than EWAC Iw Max Hd:%d EWACMaxIw:%d DibitMinIw:%d' %(hd,IwMaxCap,self.MinIwAdjust[hd][zn]))
               elif self.MinIwAdjust[hd][zn] < IwMinCap:
                  objMsg.printMsg('Override Iw Min by Dibit Hd:%d MinIw:%d NewMinIw:%d' %(hd,IwMinCap,self.MinIwAdjust[hd][zn]))
                  IwMinCap = self.MinIwAdjust[hd][zn]
               
            MeasZone += 1

            # Initialize Sweep List
            sweepList_Oa = {}
            sweepList_Iw = {}
            sweepList_Osd = {}
            if MeasZone > Level1MeasZoneCount:
               if MeasZone > Level2MeasZoneCount:
                  ZnMinRef = 0
                  ZnMaxRef = self.__numUserZones
                  for nZone in range(self.__numUserZones):
                     if self.FinalTripletPick[hd].has_key(nZone):
                        if nZone > ZnMinRef and nZone < zn:
                           ZnMinRef = nZone
                        if nZone < ZnMaxRef and nZone > zn:
                           ZnMaxRef = nZone
                  deltaIw = abs(self.tempFinalTripletPick[hd][ZnMinRef][0] - self.tempFinalTripletPick[hd][ZnMaxRef][0])
                  deltaOa = abs(self.tempFinalTripletPick[hd][ZnMinRef][1] - self.tempFinalTripletPick[hd][ZnMaxRef][1])
                  objMsg.printMsg('Iw Delta ZnMin %d  ZnMax %d  Delta: %d' % (ZnMinRef,ZnMaxRef,deltaIw))
                  objMsg.printMsg('Oa Delta ZnMin %d  ZnMax %d  Delta: %d' % (ZnMinRef,ZnMaxRef,deltaOa))
                  if  deltaIw < 3 and deltaOa < 3:
                     objMsg.printMsg('Delta within Threshold, skipping sweep on Zn %d' % zn)
                     continue
                  #OPtimize Test HeadZone
                  #objVbarOpti = CRdOpti(self.__dut, {'ZONES':[zn],'TEST_HEAD':[hd]})
                  #objVbarOpti.run()

               TripletPick_Cross = self.tempFinalTripletPick[hd][zn][0],self.tempFinalTripletPick[hd][zn][1],self.tempFinalTripletPick[hd][zn][2]


            else:
               # Execute the Sweep
               self.spcid = 0
               measData_Cross = {}
               self.measWPZns.addWpEntry(len(sweepList_Cross), numOfHd=self.numHeads, znList=self.measWPZns.objTestZones)
               adcData_Cross, measData_Cross = self.__AdcSweep(hd,zn,sweepList_Cross)

               # Pick the Best ADC from the Initial Sweep List
               TripletPick_Cross = {}
               TripletPick_Cross = self.__LocateBestArea(hd, zn, TP.NPow, Osd, self.TripletMeas)

            nWc,nOa,nOd = TripletPick_Cross
            if MeasZone > Level1MeasZoneCount:
               Osd = nOd

            if (nWc != -1) and (nOa != -1) and (nOd != -1):
               if not testSwitch.CM_REDUCTION_REDUCE_PRINTMSG:
                  objMsg.printMsg('Initial Sweep Pick:')
                  objMsg.printMsg(TripletPick_Cross)
                  objMsg.printMsg('nWc %d,nOa %d,nOd %d' %(nWc,nOa,nOd))

               if nWc > IwMaxCap: nWc = IwMaxCap
               if nWc < IwMinCap: nWc = IwMinCap
               if nOa > OaMaxCap: nOa = OaMaxCap
               if nOa < OaMinCap: nOa = OaMinCap
               printDbgMsg('Capped nWc %d,nOa %d,nOd %d' %(nWc,nOa,nOd))

               if not MeasZone > Level1MeasZoneCount:
                  # Get the average for use in TPI
                  AveList = []
                  for nData in adcData_Cross:
                     if measData_Cross[nData]['BPI']> 0.7 and measData_Cross[nData]['TPI'] > 0.7:
                        AveList.append(measData_Cross[nData]['BPI'] + measData_Cross[nData]['TPI'])
                  if len(AveList) != 0:
                     nAve = sum(AveList) / len(AveList)
                     if nAve > 1.5:
                        self.tpiCap_FeedForward = nAve

               # ------------------- Oa Sweep
               # Assemble the Oa Sweep List

               if (headvendor == 'RHO' or testSwitch.extern._128_REG_PREAMPS) and not testSwitch.ROSEWOOD7:   # Override for RHO Heads or 3G preamps
                  nOa = 3
               if testSwitch.FE_ENHANCED_TRIPLET_OPTI and headvendor != 'RHO' and (len(self.BurnishFailedHeads) == 0):
                  nOa = max(nOa, osa_osd_limit[hd,zn]['OSA_CAP'] + 2) #Override default OSA if lower than cap limit
                  nOa = min(nOa,15)
                  nOd = max(nOd, osa_osd_limit[hd,zn]['OSD_CAP']) #Override default OSD if lower than cap limit
               tIndex = 0

               if nOa < 5:
                  OaMin = 2 #2 - (nOa % 2)
                  OaMax = OaMin + 4 #8

               elif nOa > OaMaxCap - 2:
                  OaMax = OaMaxCap #14 + (nOa % 2)
                  OaMin = OaMax -4 # - 8

               else:
                  OaMin = nOa - 2
                  OaMax = nOa + 2

               for nData in range(OaMin,OaMax + 1,1):
                  sweepList_Oa[tIndex] = nWc,nData,Osd
                  tIndex += 1

               # Execute the Sweep
               measData_Oa = {}
               self.measWPZns.addWpEntry(len(sweepList_Oa))
               adcData_Oa, measData_Oa = self.__AdcSweep(hd,zn,sweepList_Oa)

               # Pick the Best ADC from the Oa List
               TripletPick_Oa = {}
               bestIndex = self.__PickBestADC(sweepList_Oa, adcData_Oa, True)
               if bestIndex != -1:
                  TripletPick_Oa = sweepList_Oa[bestIndex]
               else:
                  TripletPick_Oa = -1, -1, -1

               if testSwitch.SMR_TRIPLET_OPTI_WITH_EFFECTIVE_TPIC :
                  self.FinalBPICandTPIC[hd][zn] = measData_Oa[bestIndex].copy()

               # ------------------- Iw Sweep
               # Assemble the Iw Sweep List
               nWc,nOa,nOd = TripletPick_Oa
               if (nWc != -1) and (nOa != -1) and (nOd != -1):
                  #if nOa == 1: nOa = 3
                  printDbgMsg('nWc %d,nOa %d,nOd %d' %(nWc,nOa,nOd))
                  if nOa > OaMaxCap: nOa = OaMaxCap
                  if nOa < OaMinCap: nOa = OaMinCap
                  if testSwitch.FE_ENHANCED_TRIPLET_OPTI and headvendor != 'RHO' and (len(self.BurnishFailedHeads) == 0):
                     nOa = max(nOa, osa_osd_limit[hd,zn]['OSA_CAP']) #Override default OSA if lower than cap limit
                  printDbgMsg('Capped nWc %d,nOa %d,nOd %d' %(nWc,nOa,nOd))
                  #if nOa == 15: nOa =13
                  tIndex = 0

                  if nWc < 5:
                     IwMin = 2 #2 - (nWc % 2)
                     IwMax = IwMin + 4 #8

                  elif nWc > IwMaxCap - 2:
                     IwMax = IwMaxCap #14 + (nWc % 2)
                     IwMin = IwMax - 4 #- 8

                  else:
                     IwMin = nWc - 2
                     IwMax = nWc + 2

                  for nData in range(IwMin,IwMax + 1,1):
                     sweepList_Iw[tIndex] = nData,nOa,Osd
                     tIndex += 1

                  # Execute the Sweep
                  measData_Iw = {}
                  self.measWPZns.addWpEntry(len(sweepList_Iw))
                  adcData_Iw, measData_Iw = self.__AdcSweep(hd,zn,sweepList_Iw)

                  # Pick the Best ADC from the Oa List
                  TripletPick_Iw ={}
                  bestIndex = self.__PickBestADC(sweepList_Iw, adcData_Iw, True)
                  TripletPick_Iw = sweepList_Iw[bestIndex]

                  #Filter for BPIC Avalanche, Do not pick Iw that is adjacent to BPI drop > 5%
                  if bestIndex != len(sweepList_Iw)-1 and headvendor == 'RHO': # if already maxed out, can not move to higher Iw
                     bestIndex = self.__PickBestBPIC(sweepList_Iw,measData_Iw, bestIndex)
                     TripletPick_Iw = sweepList_Iw[bestIndex]

                  ##Filter for No slope BPIC, Set to Default Triplet if found
                  bestIndex = self.__CheckNoSlopeBPIC(sweepList_Iw,measData_Iw, bestIndex)
                  if bestIndex == -1:
                     TripletPick_Iw = -1, -1, -1


                  # ------------------- Osd Sweep
                  # Assemble the Osd Sweep List
                  nWc,nOa,nOd = TripletPick_Iw
                  if (nWc !=-1) and (nOa != -1) and (nOd != -1) and not MeasZone > Level1MeasZoneCount:
                     printDbgMsg('nWc %d,nOa %d,nOd %d' %(nWc,nOa,nOd))
                     if nWc > IwMaxCap: nWc = IwMaxCap
                     if nWc < IwMinCap: nWc = IwMinCap
                     printDbgMsg('Capped nWc %d,nOa %d,nOd %d' %(nWc,nOa,nOd))
                     tIndex = 0
                     
                     if testSwitch.FE_ENHANCED_TRIPLET_OPTI and headvendor != 'RHO' and (len(self.BurnishFailedHeads) == 0):
                        nOd = max(nOd, osa_osd_limit[hd,zn]['OSD_CAP'] + 2) #Override default OSD if lower than cap limit
                        nOd = min(nOd, 15)
                     
                     osdSweepStep = 1
                     osdStepRange = TP.osdStepRange
                     if testSwitch.FE_ENHANCED_TRIPLET_OPTI or testSwitch.SMR: # Variable Range
                        if testSwitch.SMR and not testSwitch.ROSEWOOD7: # Rosewood request by RSS to maintain step 1
                           osdSweepStep = 2
                        if nOd < 5:
                           OsdMin = 2 
                           OsdMax = OsdMin + osdStepRange * osdSweepStep 
                        elif nOd > 15 - osdStepRange * osdSweepStep:
                           OsdMax = 15
                           OsdMin = OsdMax - osdStepRange * osdSweepStep
                        else:
                           OsdMin = nOd - osdStepRange * osdSweepStep
                           OsdMax = nOd + osdStepRange * osdSweepStep
                     else: # Fix Range
                        OsdMin = 4
                        OsdMax = 8

                     for nData in range(OsdMin, OsdMax + 1 ,osdSweepStep):
                        sweepList_Osd[tIndex] = nWc,nOa,nData
                        tIndex += 1

                     # Execute the Sweep
                     measData_Osd = {}
                     self.measWPZns.addWpEntry(len(sweepList_Osd))
                     adcData_Osd, measData_Osd = self.__AdcSweep(hd,zn,sweepList_Osd)

                     # Pick the Best ADC from the Oa List
                     TripletPick_Osd ={}
                     bestIndex = self.__PickBestADC(sweepList_Osd, adcData_Osd, True)
                     if bestIndex != -1:
                        TripletPick_Osd = sweepList_Osd[bestIndex]
                     else:
                        TripletPick_Osd = -1, -1, -1


                     self.FinalTripletPick[hd][zn] = TripletPick_Osd
                     if not testSwitch.CM_REDUCTION_REDUCE_PRINTMSG:
                        objMsg.printMsg('adcData_Osd= %s' % (str(adcData_Osd)))
                        objMsg.printMsg('sweepList_Osd= %s' % (str(sweepList_Osd)))
                        objMsg.printMsg('TripletPick_Osd= %s' % (str(TripletPick_Osd)))
                     nWc,nOa,nOd = TripletPick_Osd

                     if testSwitch.SMR_TRIPLET_OPTI_WITH_EFFECTIVE_TPIC :
                        self.FinalBPICandTPIC[hd][zn] = measData_Osd[bestIndex].copy()

                  elif (nWc !=-1) and (nOa != -1) and (nOd != -1) and MeasZone > Level1MeasZoneCount:
                     self.FinalTripletPick[hd][zn] = TripletPick_Iw
                     if testSwitch.SMR_TRIPLET_OPTI_WITH_EFFECTIVE_TPIC :
                        self.FinalBPICandTPIC[hd][zn] = measData_Iw[bestIndex].copy()


            if (nWc == -1) and (nOa == -1) and (nOd == -1):
               printDbgMsg('No Slope or Saturation found, aborting optimization and setting default triplet:')
               self.FinalTripletPick[hd][zn] = Def_Triplet
               printDbgMsg(self.FinalTripletPick[hd][zn])

            # ------------------- Display data
            printDbgMsg('*' * 92)
            printDbgMsg('%s%s' % (' '* 40, 'WRITE TRIPLET OPTI'))
            if not MeasZone > Level1MeasZoneCount:
               printDbgMsg('INITIAL LIST')
               self.__PrintADClist(hd,zn,sweepList_Cross, adcData_Cross,measData_Cross,TripletPick_Cross, 'O')

            if len(sweepList_Oa) > 0:
               printDbgMsg('OA SWEEP LIST')
               self.__PrintADClist(hd,zn,sweepList_Oa, adcData_Oa,measData_Oa, TripletPick_Oa, 'O')

            if len(sweepList_Iw) > 0:
               printDbgMsg('IW SWEEEP LIST')
               self.__PrintADClist(hd,zn,sweepList_Iw, adcData_Iw,measData_Iw, TripletPick_Iw, 'O')

            if len(sweepList_Osd) > 0:
               printDbgMsg('OSD SWEEEP LIST')
               self.__PrintADClist(hd,zn,sweepList_Osd, adcData_Osd,measData_Osd, TripletPick_Osd, 'P')

            printDbgMsg('CENTER OF GRAVITY')
            #CIw,COa,COd = self.__LocateCenterofGravity(hd, zn, TP.NPow, nOd, self.TripletMeas)
            if not testSwitch.CM_REDUCTION_REDUCE_PRINTMSG:
               objMsg.printMsg('*' * 40)
               objMsg.printMsg('Best Pick        : Iw  Oa  Od')
               if testSwitch.extern._128_REG_PREAMPS:
                  objMsg.printMsg('Sweep Method     : %2d %2d %2d' % (self.FinalTripletPick[hd][zn][0]* 7 + 20,self.FinalTripletPick[hd][zn][1]*2,self.FinalTripletPick[hd][zn][2]*2))
               else:
                  objMsg.printMsg('Sweep Method     : %2d %2d %2d' % (self.FinalTripletPick[hd][zn][0],self.FinalTripletPick[hd][zn][1],self.FinalTripletPick[hd][zn][2]))
               #objMsg.printMsg('Center of Gravity: %2d %2d %2d' % (CIw,COa,COd))
               if testSwitch.SMR_TRIPLET_OPTI_WITH_EFFECTIVE_TPIC == 1:
                  objMsg.printMsg('BPI: %0.4f' % (self.FinalBPICandTPIC[hd][zn]['BPI']))
                  objMsg.printMsg('TPI: %0.4f' % (self.FinalBPICandTPIC[hd][zn]['TPI']))
                  objMsg.printMsg('TpiCapability: %0.4f' % (self.FinalBPICandTPIC[hd][zn]['TpiCapability'])) #effective tpic
                  objMsg.printMsg('TPI_IDSS: %0.4f' % (self.FinalBPICandTPIC[hd][zn]['TPI_IDSS']))
                  objMsg.printMsg('TPI_ODSS: %0.4f' % (self.FinalBPICandTPIC[hd][zn]['TPI_ODSS']))
                  objMsg.printMsg('RD_OFST_IDSS: %0.4f' % (self.FinalBPICandTPIC[hd][zn]['RD_OFST_IDSS']))
                  objMsg.printMsg('RD_OFST_ODSS: %0.4f' % (self.FinalBPICandTPIC[hd][zn]['RD_OFST_ODSS']))
               objMsg.printMsg('*' * 40)

            #Build INterpolated Values
            if MeasZone >= Level1MeasZoneCount:
               #objMsg.printMsg("self.FinalTripletPick[hd]")
               #objMsg.printMsg(self.FinalTripletPick[hd])
               if testSwitch.SMR_TRIPLET_OPTI_WITH_EFFECTIVE_TPIC == 1:
                  printDbgMsg("self.FinalBPICandTPIC[hd]")
                  printDbgMsg(self.FinalBPICandTPIC[hd])
               for nZone in range(self.__numUserZones):
                  if self.FinalTripletPick[hd].has_key(nZone):
                     #objMsg.printMsg("nZone %d" %nZone)
                     if nX1 == 99:
                        nY1Iw = self.FinalTripletPick[hd][nZone][0]
                        nY1Oa = self.FinalTripletPick[hd][nZone][1]
                        nY1Od = self.FinalTripletPick[hd][nZone][2]
                        if testSwitch.SMR_TRIPLET_OPTI_WITH_EFFECTIVE_TPIC == 1:
                           #BPIC/TPIC/TPI_IDSS/TPI_ODSS
                           nY1BPIC = self.FinalBPICandTPIC[hd][nZone]['BPI']
                           nY1TPIC = self.FinalBPICandTPIC[hd][nZone]['TPI']
                           nY1TPI_IDSS = self.FinalBPICandTPIC[hd][nZone]['TPI_IDSS']
                           nY1TPI_ODSS = self.FinalBPICandTPIC[hd][nZone]['TPI_ODSS']
                           nY1RD_OFST_IDSS = self.FinalBPICandTPIC[hd][nZone]['RD_OFST_IDSS']
                           nY1RD_OFST_ODSS = self.FinalBPICandTPIC[hd][nZone]['RD_OFST_ODSS']
                        nX1 = nZone
                     else:
                        nY2Iw = self.FinalTripletPick[hd][nZone][0]
                        nY2Oa = self.FinalTripletPick[hd][nZone][1]
                        nY2Od = self.FinalTripletPick[hd][nZone][2]
                        nX2 = nZone
                        if testSwitch.SMR_TRIPLET_OPTI_WITH_EFFECTIVE_TPIC == 1:
                           #BPIC/TPIC/TPI_IDSS/TPI_ODSS
                           nY2BPIC = self.FinalBPICandTPIC[hd][nZone]['BPI']
                           nY2TPIC = self.FinalBPICandTPIC[hd][nZone]['TPI']
                           nY2TPI_IDSS = self.FinalBPICandTPIC[hd][nZone]['TPI_IDSS']
                           nY2TPI_ODSS = self.FinalBPICandTPIC[hd][nZone]['TPI_ODSS']
                           nY2RD_OFST_IDSS = self.FinalBPICandTPIC[hd][nZone]['RD_OFST_IDSS']
                           nY2RD_OFST_ODSS = self.FinalBPICandTPIC[hd][nZone]['RD_OFST_ODSS']
                           nStepBPIC = float(float(nY2BPIC - nY1BPIC) / float(nX2 - nX1))
                           nStepTPIC = float(float(nY2TPIC - nY1TPIC) / float(nX2 - nX1))
                           nStepTPI_IDSS = float(float(nY2TPI_IDSS - nY1TPI_IDSS) / float(nX2 - nX1))
                           nStepTPI_ODSS = float(float(nY2TPI_ODSS - nY1TPI_ODSS) / float(nX2 - nX1))
                           nStepRD_OFST_IDSS = float(float(nY2RD_OFST_IDSS - nY1RD_OFST_IDSS) / float(nX2 - nX1))
                           nStepRD_OFST_ODSS = float(float(nY2RD_OFST_ODSS - nY1RD_OFST_ODSS) / float(nX2 - nX1))
                           if not testSwitch.CM_REDUCTION_REDUCE_PRINTMSG:
                              objMsg.printMsg("nStepBPIC %0.4f" %nStepBPIC)
                              objMsg.printMsg("nStepTPIC %0.4f" %nStepTPIC)
                              objMsg.printMsg("nStepTPI_IDSS %0.4f" %nStepTPI_IDSS)
                              objMsg.printMsg("nStepTPI_ODSS %0.4f" %nStepTPI_ODSS)
                              objMsg.printMsg("nStepRD_OFST_IDSS %0.4f" %nStepRD_OFST_IDSS)
                              objMsg.printMsg("nStepRD_OFST_ODSS %0.4f" %nStepRD_OFST_ODSS)
                        nStepIw = float(float(nY2Iw - nY1Iw) / float(nX2 - nX1))
                        #objMsg.printMsg("nStepIw %0.4f" %nStepIw)
                        nStepOa = float(float(nY2Oa - nY1Oa) / float(nX2 - nX1))
                        #objMsg.printMsg("nStepOa %0.4f" %nStepOa)
                        nStepOs = float(float(nY2Od - nY1Od) / float(nX2 - nX1))
                        for yZone in range(nX1,nX2+1):
                           self.tempFinalTripletPick[hd][yZone] = {}
                           self.tempFinalTripletPick[hd][yZone][0] = int(round(nY1Iw + float(nStepIw * (yZone - nX1)),0))
                           self.tempFinalTripletPick[hd][yZone][1] = int(round(nY1Oa + float(nStepOa * (yZone - nX1)),0))
                           self.tempFinalTripletPick[hd][yZone][2] = int(round(nY1Od + float(nStepOs * (yZone - nX1)),0))
                           if testSwitch.SMR_TRIPLET_OPTI_WITH_EFFECTIVE_TPIC == 1:
                               self.tempFinalBPICandTPIC[hd][yZone] = {}
                               self.tempFinalBPICandTPIC[hd][yZone]['BPI'] = round(nY1BPIC + float(nStepBPIC * (yZone - nX1)),4)
                               self.tempFinalBPICandTPIC[hd][yZone]['TPI'] = round(nY1TPIC + float(nStepTPIC * (yZone - nX1)),4)
                               self.tempFinalBPICandTPIC[hd][yZone]['TPI_IDSS'] = round(nY1TPI_IDSS + float(nStepTPI_IDSS * (yZone - nX1)),4)
                               self.tempFinalBPICandTPIC[hd][yZone]['TPI_ODSS'] = round(nY1TPI_ODSS + float(nStepTPI_ODSS * (yZone - nX1)),4)
                               self.tempFinalBPICandTPIC[hd][yZone]['RD_OFST_IDSS'] = round(nY1RD_OFST_IDSS + float(nStepRD_OFST_IDSS * (yZone - nX1)),4)
                               self.tempFinalBPICandTPIC[hd][yZone]['RD_OFST_ODSS'] = round(nY1RD_OFST_ODSS + float(nStepRD_OFST_ODSS * (yZone - nX1)),4)

                           #objMsg.printMsg("Hd %d,  Zn %d,  nX1 %d,  nX2 %d,  nY1Iw %d,  nY2Iw %d,  Iw %d,  Oa %d,  Od %d" % (hd, yZone, nX1, nX2, nY1Iw ,nY2Iw , self.tempFinalTripletPick[hd][yZone][0],self.tempFinalTripletPick[hd][yZone][1],self.tempFinalTripletPick[hd][yZone][2]))
                        nX1 = nX2
                        nY1Iw = nY2Iw
                        nY1Oa = nY2Oa
                        nY1Od = nY2Od
                        if testSwitch.SMR_TRIPLET_OPTI_WITH_EFFECTIVE_TPIC == 1:
                           nY1BPIC = nY2BPIC
                           nY1TPIC = nY2TPIC
                           nY1TPI_IDSS = nY2TPI_IDSS
                           nY1TPI_ODSS = nY2TPI_ODSS
                           nY1RD_OFST_IDSS  = nY2RD_OFST_IDSS
                           nY1RD_OFST_ODSS  = nY2RD_OFST_ODSS
               #objMsg.printMsg("self.tempFinalTripletPick")
               #objMsg.printMsg(self.tempFinalTripletPick)
               if testSwitch.SMR_TRIPLET_OPTI_WITH_EFFECTIVE_TPIC == 1:
                  if verbose: objMsg.printMsg("self.tempFinalBPICandTPIC %s" % self.tempFinalBPICandTPIC)



      # Apply Quad Median Poly Fit
      for hd in headRange:
         for index in range(3):
            dataList = []
            for zn in range(self.__numUserZones):
               dataList.append(self.tempFinalTripletPick[hd][zn][index])
            filteredList = self.quadraticMedianfilter(dataList)
            
            for zn in range(self.__numUserZones):
               if index == 0:
                  # Make sure Iw after Poly fit does not exceed Max Setting
                  if testSwitch.FE_348429_0247869_TRIPLET_INTEGRATED_ATISTE:
                     self.tempFinalTripletPick[hd][zn][index] = min(IwMaxCap_hd[hd], int(round(filteredList[zn], 0)))
                  else:
                     self.tempFinalTripletPick[hd][zn][index] = min(TP.IwMaxCap,self.MaxIwAdjust[hd],int(round(filteredList[zn],0)))
                  # Make sure Iw after Poly fit does not go below Min Setting
                  if self.MinIwAdjust[hd] and self.MinIwAdjust[hd].has_key(zn) and self.MinIwAdjust[hd][zn] > TP.IwMinCap:
                     self.tempFinalTripletPick[hd][zn][index] = max(self.MinIwAdjust[hd][zn],self.tempFinalTripletPick[hd][zn][index])
                  else:
                     self.tempFinalTripletPick[hd][zn][index] = max(TP.IwMinCap,self.tempFinalTripletPick[hd][zn][index])
               elif index == 1:
                  # Make sure Max Oa after Poly fit does not exceed Max Setting
                  if testSwitch.FE_348429_0247869_TRIPLET_INTEGRATED_ATISTE:
                     self.tempFinalTripletPick[hd][zn][index] = min(OaMaxCap_hd[hd], int(round(filteredList[zn],0)))
                  else:
                     self.tempFinalTripletPick[hd][zn][index] = min(TP.OaMaxCap,int(round(filteredList[zn],0)))
                  # Make sure Max Oa after Poly fit does not go below min Setting
                  self.tempFinalTripletPick[hd][zn][index] = max(TP.OaMinCap,self.tempFinalTripletPick[hd][zn][index])
                  if testSwitch.FE_ENHANCED_TRIPLET_OPTI and headvendor != 'RHO' and (len(self.BurnishFailedHeads) == 0):
                     self.tempFinalTripletPick[hd][zn][index] = max(osa_osd_limit[hd,zn]['OSA_CAP'],self.tempFinalTripletPick[hd][zn][index])
               elif index == 2:
                  if testSwitch.FE_ENHANCED_TRIPLET_OPTI and headvendor != 'RHO' and (len(self.BurnishFailedHeads) == 0):
                     self.tempFinalTripletPick[hd][zn][index] = max(osa_osd_limit[hd,zn]['OSD_CAP'],self.tempFinalTripletPick[hd][zn][index])

      # Dump Final Picks
      self.__dumpTripletOutput(headRange)

      if testSwitch.SMR_TRIPLET_OPTI_WITH_EFFECTIVE_TPIC == 1:
         self.__dumpVBARData(headRange)


      if testSwitch.SMR_TRIPLET_OPTI_WITH_EFFECTIVE_TPIC == 1:
         for hd in headRange:
            keysToInterpolate = ['BPI', 'TPI', 'TPI_IDSS', 'TPI_ODSS', 'RD_OFST_IDSS', 'RD_OFST_ODSS']
            for index in range(len(keysToInterpolate)):
               key = keysToInterpolate[index]
               dataList = []
               for zn in range(self.__numUserZones):
                  dataList.append(self.tempFinalBPICandTPIC[hd][zn][key])
               filteredList = self.quadraticMedianfilter(dataList)
               objMsg.printMsg('%s filteredList_output = %s' % (key, filteredList))
               for zn in range(self.__numUserZones):
                   self.tempFinalBPICandTPIC[hd][zn][key] = filteredList[zn]

         if verbose:
            objMsg.printMsg("self.tempFinalBPICandTPIC:post quadraticMedianfilter")
            objMsg.printMsg(self.tempFinalBPICandTPIC)
      
      # Set Triplet to the RAP
      prm_178 = {'test_num': 178, 'prm_name': 'prm_wp_178', 'timeout': 1200, 'spc_id': 0,}

      for hd in headRange:
         saveData = {} #init empty dict
         hd_mask = 0x3FF & (1<<hd) # write to one head at a time
         for zn in sorted(ZnLumping):
            triplet = (self.tempFinalTripletPick[hd][zn][0], self.tempFinalTripletPick[hd][zn][1], \
               self.tempFinalTripletPick[hd][zn][2])
            if not triplet in saveData: #init
               saveData[triplet] = []
            for zone in ZnLumping[zn]:
               saveData[triplet].append(zone)
         for triplet in saveData:
            if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
               #bit mask & bit mask ext param is no longer supported
               if 'BIT_MASK' in prm_178:     del prm_178['BIT_MASK'] 
               if 'BIT_MASK_EXT' in prm_178: del prm_178['BIT_MASK_EXT']
               if testSwitch.extern.FE_0270095_504159_SUPPORT_LOOPING_ZONE_T178:
                  for startZn, endZn in \
                     self.oUtility.convertZoneListToZoneRange(saveData[triplet]):
                     prm_178['ZONE'] = (startZn << 8) + endZn
                     prm_178['prm_name'] = 'prm_wp_178_0x%04x_%s_%s_%s' % (prm_178['ZONE'], triplet[0], triplet[1], triplet[2])
                     self.setTriplet(prm_178, triplet, hd_mask)
               else:
                  for zn in saveData[triplet]:
                     prm_178['ZONE'] = zn
                     self.setTriplet(prm_178, triplet, hd_mask)
            else:
               prm_178['BIT_MASK_EXT'], prm_178['BIT_MASK'] = self.oUtility.convertListTo64BitMask(saveData[triplet])
               self.setTriplet(prm_178, triplet, hd_mask)

         if testSwitch.WA_0256539_480505_SKDC_M10P_BRING_UP_DEBUG_OPTION: # system zone triplet update 
            prm_178.update({
               'CWORD1':0x0200, 'CWORD2':0x1107, 
               'BIT_MASK':(0L,0), 'BIT_MASK_EXT':(4096L,0),
               'HEAD_RANGE':hd_mask,
               'WRITE_CURRENT':80, 'DAMPING':0, 'DURATION':0,
               })
            self.oProc.St(prm_178)

      self.oProc.St({'test_num':178, 'prm_name':'Save RAP in RAM to FLASH', 'CWORD1':0x220})

      # dump triplet values to verify settings
      getVbarGlobalClass(CFSO).getWritePowers(T172_spc_id, supressOutput = 0)
      if testSwitch.SMR_TRIPLET_OPTI_SET_BPI_TPI ==1  and  testSwitch.SMR_TRIPLET_OPTI_WITH_EFFECTIVE_TPIC ==1:
         #Populate the data.
         for hd in headRange:
            for zn in xrange(self.__numUserZones):
               meas = CVbarDataHelper(self.measurements, hd, zn)
               meas['BPI']      = self.tempFinalBPICandTPIC[hd][zn]['BPI']
               meas['TPI']      = self.tempFinalBPICandTPIC[hd][zn]['TPI']
               meas['TPI_IDSS'] = self.tempFinalBPICandTPIC[hd][zn]['TPI_IDSS']
               meas['TPI_ODSS'] = self.tempFinalBPICandTPIC[hd][zn]['TPI_ODSS']
               meas['RD_OFST_IDSS'] = self.tempFinalBPICandTPIC[hd][zn]['RD_OFST_IDSS']
               meas['RD_OFST_ODSS'] = self.tempFinalBPICandTPIC[hd][zn]['RD_OFST_ODSS']

         return self.measurements
   
   #-------------------------------------------------------------------------------------------------------
   def __dumpVBARData(self, headRange):
      str_vbar = ""
      str_vbar += "*" * 90 + "\n"
      str_vbar += "*" * 90 + "\n"
      str_vbar += "SMR Final BPIC/TPI Pick\n"
      str_vbar += "%s\t%s\t%s\t%s\t%s\t%s\n" % ('Hd','Zn','BPI','TPI','TPI_IDSS','TPI_ODSS')
      for hd in headRange:
         for zn in range(self.__numUserZones):
            str_vbar += "%2d\t%2d\t%0.4f\t%0.4f" % (hd,zn,self.tempFinalBPICandTPIC[hd][zn]['BPI'],self.tempFinalBPICandTPIC[hd][zn]['TPI'])
            str_vbar += "%0.4f\t%0.4f\n" % (self.tempFinalBPICandTPIC[hd][zn]['TPI_IDSS'],self.tempFinalBPICandTPIC[hd][zn]['TPI_ODSS'])
      if verbose: objMsg.printMsg("%s" % str_vbar) #cut logs by not dumping the final vbar picks, can refer to smr format summary
      
   #-------------------------------------------------------------------------------------------------------
   def __dumpTripletOutput(self, headRange):
      # Dump Final Picks
      str_triplet = ""
      str_triplet += ('*' * 40) + "\n"
      str_triplet += "FINAL PICK\n"
      str_triplet += "%s\t%s\t%s\t%s\t%s\n" % ('Hd','Zn','Iw','Oa','Od')
      for hd in headRange:
         for zn in range(self.__numUserZones):
            if testSwitch.extern._128_REG_PREAMPS:
               str_triplet += ("%2d\t%2d\t%2d\t%2d\t%2d\n" 
                  % (hd,zn,self.tempFinalTripletPick[hd][zn][0]* 7 + 20,self.tempFinalTripletPick[hd][zn][1]*2,self.tempFinalTripletPick[hd][zn][2]*2))
            else:
               str_triplet += ("%2d\t%2d\t%2d\t%2d\t%2d\n" 
                  % (hd,zn,self.tempFinalTripletPick[hd][zn][0],self.tempFinalTripletPick[hd][zn][1],self.tempFinalTripletPick[hd][zn][2]))
      str_triplet += ('*' * 40) + "\n"
      if verbose: objMsg.printMsg("%s" % str_triplet) #cut logs by not dumping the final picks, can refer to final triplet table
      
   #-------------------------------------------------------------------------------------------------------
   def setTriplet(self, prm_178, triplet, hd_mask):
      cword1 = 0x0200  # update RAM copy
      wcoc = TP.VBAR_TCC["WC_COLD_OFFSET"]
      wcoh = TP.VBAR_TCC["WC_HOT_OFFSET"]
      if testSwitch.extern._128_REG_PREAMPS:
         prm_178.update({'CWORD1':cword1, 'CWORD2':0x1107, 'HEAD_RANGE':hd_mask,\
            'WRITE_CURRENT':triplet[0]*7+20, 'DAMPING':triplet[1]*2, 'DURATION':triplet[2]*2})
      else:
         prm_178.update({'CWORD1':cword1, 'CWORD2':0x1107, 'HEAD_RANGE':hd_mask, \
            'WRITE_CURRENT':triplet[0], 'DAMPING':triplet[1], 'DURATION':triplet[2]})
      if triplet[0] + wcoc < 16 and triplet[0] + wcoh < 16:
         prm_178.update({'WRITE_CURRENT_OFFSET':(wcoc, wcoh)})   
      if testSwitch.FE_0147058_208705_SHORTEN_VBAR_LOGS:
         prm_178['stSuppressResults'] = ST_SUPPRESS__ALL
      self.oProc.St(prm_178)
      
   #-------------------------------------------------------------------------------------------------------
   def __PrintADClist(self,hd,zn,tripletList, adcList, measList, tPick, nTag):
      self.spcid += 1
      printDbgMsg('IWH\t%s\t%s\t%s\t%s\t%s\t %s\t %s\t %s\t %s\t' % ('Hd','Zn','Iw','Oa','Od','BPI','TPI','zHtClr', 'ADC'))
      if not testSwitch.SMR_TRIPLET_OPTI_WITH_EFFECTIVE_TPIC:
         printDbgMsg('*' * 92)
         for nData in adcList:
            Iw_adj = 0
            Oa_adj = 0
            Od_adj= 0
            if testSwitch.extern._128_REG_PREAMPS:
               Iw_adj = tripletList[nData][0] * 7 + 20 - tripletList[nData][0]
               Oa_adj = tripletList[nData][1]
               Od_adj = tripletList[nData][2]

            if tPick == tripletList[nData]:
               printDbgMsg('IWC\t%2d\t%2d\t%2d\t%2d\t%2d\t %0.4f\t %0.4f\t %0.4f\t %0.4f\t %s' % (hd,zn,tripletList[nData][0]+Iw_adj,tripletList[nData][1]+Oa_adj,tripletList[nData][2]+Od_adj,measList[nData]['BPI'],measList[nData]['TPI'],measList[nData]['zHtClr'],adcList[nData], nTag))
               nPick = nTag
            else:
               printDbgMsg('IWC\t%2d\t%2d\t%2d\t%2d\t%2d\t %0.4f\t %0.4f\t %0.4f\t %0.4f\t' % (hd,zn,tripletList[nData][0]+Iw_adj,tripletList[nData][1]+Oa_adj,tripletList[nData][2]+Od_adj,measList[nData]['BPI'],measList[nData]['TPI'],measList[nData]['zHtClr'],adcList[nData]))
               nPick = ''
            #Update DBLOG Tables
            self.nPwrIndex += 1
            self.__dut.dblData.Tables('P_WRT_PWR_PICKER').addRecord({
                                 'HD_PHYS_PSN'           : hd,
                                 'DATA_ZONE'             : zn,
                                 'SPC_ID'                : self.spcid,
                                 'OCCURRENCE'            : hd,
                                 'SEQ'                   : self.__dut.objSeq.getSeq(),
                                 'TEST_SEQ_EVENT'        : 1,
                                 'HD_LGC_PSN'            : hd,
                                 'WRT_PWR_NDX'           : self.nPwrIndex,
                                 'WRT_HEAT_CLRNC'        : measList[nData]['zHtClr'],
                                 'CLRNC_WGHT_FUNC'       : 0,
                                 'STRTN_PWR_WGHT_FUNC'   : 0,
                                 'FITNESS_PWR_WGHT_FUNC' : 0,
                                 'BPI_CAP'               : measList[nData]['BPI'],
                                 'FLTR_BPI_CAP'          : measList[nData]['BPI'],
                                 'TPI_CAP'               : measList[nData]['TPI'],
                                 'FLTR_TPI_CAP'          : measList[nData]['TPI'],
                                 'SATURATION_PEAK'       : 0,
                                 'CAPACITY_CALC'         : adcList[nData],
                                 'SATURATION_PICK'       : nPick,
                                 'CAPACITY_PICK'         : nPick,
                  })

            self.__dut.dblData.Tables('P_WRT_PWR_TRIPLETS').addRecord(
                  {
                           'WRT_PWR_NDX'              : self.nPwrIndex,
                           'ZONE_TYPE'                : zn,
                           'SPC_ID'                   : self.spcid,
                           'OCCURRENCE'               : hd,
                           'SEQ'                      : self.__dut.objSeq.getSeq(),
                           'TEST_SEQ_EVENT'           : 1,
                           'WRT_CUR'                  : tripletList[nData][0]+Iw_adj,
                           'OVRSHT'                   : tripletList[nData][1]+Oa_adj,
                           'OVRSHT_DUR'               : tripletList[nData][2]+Od_adj,
                  })

      else:
         printDbgMsg('IWH\t%s\t%s\t%s\t%s\t%s\t %s\t %s\t %s\t %s\t %s\t %s\t %s\t\t' % ('Hd','Zn','Iw','Oa','Od','BPI','TPI', 'TpiCapability', 'TPI_ODSS', 'TPI_IDSS','zHtClr', 'ADC'))
         printDbgMsg('*' * 92)
         for nData in adcList:
            Iw_adj = 0
            Oa_adj = 0
            Od_adj= 0
            if testSwitch.extern._128_REG_PREAMPS:
               Iw_adj = tripletList[nData][0] * 7 + 20 - tripletList[nData][0]
               Oa_adj = tripletList[nData][1]
               Od_adj = tripletList[nData][2]

            if tPick == tripletList[nData]:
               printDbgMsg('IWC\t%2d\t%2d\t%2d\t%2d\t%2d\t %0.4f\t %0.4f\t %0.4f\t\t %0.4f\t\t %0.4f\t\t %0.4f\t %0.4f\t %s' % (hd,zn,tripletList[nData][0]+Iw_adj,tripletList[nData][1]+Oa_adj,tripletList[nData][2]+Od_adj,measList[nData]['BPI'],measList[nData]['TPI'], measList[nData]['TpiCapability'], measList[nData]['TPI_ODSS'],measList[nData]['TPI_IDSS'], measList[nData]['zHtClr'],adcList[nData], nTag))
               nPick = nTag
            else:
               printDbgMsg('IWC\t%2d\t%2d\t%2d\t%2d\t%2d\t %0.4f\t %0.4f\t %0.4f\t\t %0.4f\t\t %0.4f\t\t %0.4f\t %0.4f\t' % (hd,zn,tripletList[nData][0]+Iw_adj,tripletList[nData][1]+Oa_adj,tripletList[nData][2]+Od_adj,measList[nData]['BPI'],measList[nData]['TPI'], measList[nData]['TpiCapability'], measList[nData]['TPI_ODSS'],measList[nData]['TPI_IDSS'],measList[nData]['zHtClr'],adcList[nData]))
               nPick = ''
            #Update DBLOG Tables
            self.nPwrIndex += 1
            self.__dut.dblData.Tables('P_WRT_PWR_PICKER').addRecord({
                                 'HD_PHYS_PSN'           : hd,
                                 'DATA_ZONE'             : zn,
                                 'SPC_ID'                : self.spcid,
                                 'OCCURRENCE'            : hd,
                                 'SEQ'                   : self.__dut.objSeq.getSeq(),
                                 'TEST_SEQ_EVENT'        : 1,
                                 'HD_LGC_PSN'            : hd,
                                 'WRT_PWR_NDX'           : self.nPwrIndex,
                                 'WRT_HEAT_CLRNC'        : measList[nData]['zHtClr'],
                                 'CLRNC_WGHT_FUNC'       : 0,
                                 'STRTN_PWR_WGHT_FUNC'   : 0,
                                 'FITNESS_PWR_WGHT_FUNC' : 0,
                                 'BPI_CAP'               : measList[nData]['BPI'],
                                 'FLTR_BPI_CAP'          : measList[nData]['BPI'],
                                 'TPI_CAP'               : measList[nData]['TPI'],
                                 'FLTR_TPI_CAP'          : measList[nData]['TPI'],
                                 'SATURATION_PEAK'       : 0,
                                 'CAPACITY_CALC'         : adcList[nData],
                                 'SATURATION_PICK'       : nPick,
                                 'CAPACITY_PICK'         : nPick,
                  })

            self.__dut.dblData.Tables('P_WRT_PWR_TRIPLETS').addRecord(
                  {
                           'WRT_PWR_NDX'              : self.nPwrIndex,
                           'ZONE_TYPE'                : zn,
                           'SPC_ID'                   : self.spcid,
                           'OCCURRENCE'               : hd,
                           'SEQ'                      : self.__dut.objSeq.getSeq(),
                           'TEST_SEQ_EVENT'           : 1,
                           'WRT_CUR'                  : tripletList[nData][0]+Iw_adj,
                           'OVRSHT'                   : tripletList[nData][1]+Oa_adj,
                           'OVRSHT_DUR'               : tripletList[nData][2]+Od_adj,
                  })

      printDbgMsg('*' * 92)

   #-------------------------------------------------------------------------------------------------------
   def __PickBestADC(self,tripletList, adcList, FilterSaturation = False):

      bestAdc = 0
      bestWtTriplet = []

      for nData in adcList:
         if adcList[nData] > bestAdc:
            bestIndex = nData
            bestAdc = adcList[bestIndex]

      # if non of the Adc > 0, fail
      if bestAdc == 0:
         # return invalid value 100 to indicate failure to find any good measurement results
         return -1
         # raiseException(13409, "No saturation point found")

      if FilterSaturation == True:
         #Special Filter for Max Picks
         #if pick happens to be the max, slide down to the next best ADC
         #if bestIndex == len(adcList) - 1:
         #   nWc,nOa,nOd = tripletList[bestIndex]
         #   if nWc == 15 or nOa == 15: #Max Picks
         #      while bestIndex != 1:
         #         bestIndex -= 1 # Slide down to the next index
         #         bestAdc = adcList[bestIndex]
         #         if bestAdc > adcList[bestIndex - 1]:
         #            break

         if bestIndex != 0 and bestIndex != len(adcList) - 1:
            #if the gap between the best triplet ADC and the next higher ADC is  more than 5.7% step
            # and that next lower triplet ADC has a gap of within 0.25% to the best ADC
            # then use the next lower triplet ADC
            if bestAdc - adcList[bestIndex + 1] > TP.SteepSatThreshold and bestAdc - adcList[bestIndex - 1] < TP.FlatSatThreshold:
                  bestIndex -= 1
                  bestAdc = adcList[bestIndex]


         if bestIndex != 0:
            # If the gap between the best triplet ADC and the next lower triplet ADC is not more than 0.25%
            # then use the next lower triplet ADC
            origBestAdc = bestAdc
            for nData in range(0,bestIndex):
               if float(origBestAdc - bestAdc) > 2* TP.FlatSatThreshold: # don't allow ADC to drop 2 x the FlatTreshold
                  break
               if bestAdc - adcList[bestIndex - 1] < TP.FlatSatThreshold:
                  bestIndex -= 1
                  bestAdc = adcList[bestIndex]


         if bestIndex != 0 and bestIndex != len(adcList) - 1:
            # if gap between best triplet and the next lower triplet ADC is greater than 5.7%
            # and that the next higher triplet ADC is greater than current ADC
            # increase the best triplet to the next higher triplet.
            # Basically, don't allow triplet pick to be adjacent to a steep slope ADC
            for nData in range(bestIndex,len(adcList) - 1):
               if (bestAdc - adcList[nData - 1] > TP.SteepSatThreshold) and (adcList[nData + 1] > bestAdc):
                  bestIndex = nData + 1
                  bestAdc = adcList[bestIndex]


      return bestIndex

   #-------------------------------------------------------------------------------------------------------
   def __PickBestBPIC(self, sweepList, measData, bestIndex):
      objMsg.printMsg('BPIC Avalanche Filter')
      objMsg.printMsg('CurrentBestIndex: %d' % bestIndex)
      BPIList=[]
      newBestIndex = bestIndex
      for nTriplet in sweepList:
         BPIList.append(measData[nTriplet]['BPI'])

      if bestIndex == 0:
         objMsg.printMsg('Lowest Triplet Pick Found, BPI delta to next index: %4f ' % (BPIList[1] - BPIList[0]))
         if BPIList[1] - BPIList[0] > TP.BPIAvalancheThreshold:
            objMsg.printMsg('... and it is at BPI avalanche point, moving to next higher Triplet')
            bestIndex = 1
         else:
            objMsg.printMsg('... and it is not BPI avalanche point. Do nothing.')

      if bestIndex != 0:
         for nIndex in range(bestIndex,len(sweepList)):
            objMsg.printMsg('Index %d  BPICurIndex %4f  BPILowerIndex %4f  Delta %f' % (nIndex, BPIList[nIndex], BPIList[nIndex - 1], BPIList[nIndex] - BPIList[nIndex - 1]))
            if (BPIList[nIndex] - BPIList[nIndex - 1] > TP.BPIAvalancheThreshold):
               if nIndex == len(sweepList) - 1:
                  objMsg.printMsg('reached last point, break out')
                  break                 
               objMsg.printMsg('The current pick is adjacent to BPI avalanche point, moving to next higher Triplet')
               newBestIndex = nIndex + 1
            else:
               objMsg.printMsg('Not adjacent to BPI avalanche point, stop adjusting.')
               break

      objMsg.printMsg('NewBestIndex: %d' % newBestIndex)
      return newBestIndex
   #-------------------------------------------------------------------------------------------------------
   def __CheckNoSlopeBPIC(self, sweepList, measData, bestIndex):
      printDbgMsg('BPIC Slope Filter')
      printDbgMsg('CurrentBestIndex: %d' % bestIndex)
      BPIList=[]
      newBestIndex = bestIndex
      for nTriplet in sweepList:
         BPIList.append(measData[nTriplet]['BPI'])

      # Check for Flat BPIC
      if max(BPIList) == min(BPIList):
         printDbgMsg('No Slope Detected on BPIC, Reverting to Default Triplet')
         newBestIndex = -1

      printDbgMsg('NewBestIndex: %d' % newBestIndex)
      return newBestIndex

   #-------------------------------------------------------------------------------------------------------
   def __AdcSweep_yarra(self,hd,zn,nList):
      _measData = {}
      _AdcData = {}
      #Reset the feedforward amount for each head to target capacity
      tpiCap_FeedForward = 1

      for nTriplet in nList:
         _measData[nTriplet] = {}
         _measData[nTriplet] = {'BPI': -1, 'TPI': -1, 'zHtClr': 0}
         nTag = 'hd' + str(hd) + 'zn' + str(zn) + 'Iw' + str(nList[nTriplet][0]) + 'Oa' + str(nList[nTriplet][1])+ 'Od' + str(nList[nTriplet][2])
         if self.TripletMeas.has_key(nTag):
            _AdcData[nTriplet] = self.TripletMeas[nTag]['ADC']
            _measData[nTriplet] = self.TripletMeas[nTag].copy()
         else:
            _measData[nTriplet]['BPI'], _measData[nTriplet]['zHtClr'] = self.__measureTripletBPI(hd, zn, nList[nTriplet])

            if _measData[nTriplet]['BPI'] != -1.0 and _measData[nTriplet]['BPI'] > 0.70:
               if self.tpiCap_FeedForward != -1.0:
                  tpiCap_FeedForward = self.tpiCap_FeedForward - _measData[nTriplet]['BPI']
                  if abs(tpiCap_FeedForward -1) > 0.2: # if too far from Nominal then just start sweep from nominal
                     tpiCap_FeedForward = 1
                  objMsg.printMsg('AdjustingFeedForward:%4.4f' % tpiCap_FeedForward)
               _measData[nTriplet]['TPI'] = tpiCap_FeedForward = self.__measureTripletTPI(hd, zn, _measData[nTriplet]['BPI'], nList[nTriplet], tpiCap_FeedForward)

            else:
               _measData[nTriplet]['TPI'] = -1.0

            if _measData[nTriplet]['TPI'] == -1.0:
               tpiCap_FeedForward = 1

            _AdcData[nTriplet] = _measData[nTriplet]['BPI'] * _measData[nTriplet]['TPI'] #  * Clr Weighting Function
            if _measData[nTriplet]['BPI'] == -1 and _measData[nTriplet]['TPI'] == -1:
               _AdcData[nTriplet] = -1
            self.TripletMeas[nTag] = {}
            self.TripletMeas[nTag] = _measData[nTriplet].copy()

            self.TripletMeas[nTag]['ADC'] = _AdcData[nTriplet]
            self.TripletMeas[nTag]['IW'], self.TripletMeas[nTag]['OA'], self.TripletMeas[nTag]['OD']  = nList[nTriplet]

      return _AdcData, _measData

   #-------------------------------------------------------------------------------------------------------
   def __AdcSweep(self,hd,zn,nList):
      _measData = {}
      _AdcData = {}
      #Reset the feedforward amount for each head to target capacity
      #tpiCap_FeedForward = 1

      for nTriplet in nList:
         _measData[nTriplet] = {}
         if testSwitch.SMR_TRIPLET_OPTI_WITH_EFFECTIVE_TPIC == 1:
            _measData[nTriplet] = {'BPI':-1.0, 'TPI':-1.0, 'TPI_IDSS':-1.0, 'TPI_ODSS':-1.0, 'TPI_DSS':-1.0, 'TpiCapability':-1.0, 'TpiCapabilitySSS':-1.0, 'TpiCapabilityDSS':-1.0, 'RD_OFST_ODSS':0.0, 'RD_OFST_IDSS':0.0, 'ShingleDirection':SHINGLE_DIRECTION_OD_TO_ID, 'zHtClr':0.0}
         else:
            _measData[nTriplet] = {'BPI': -1.0, 'TPI': -1.0, 'zHtClr': 0.0}
         nTag = 'hd' + str(hd) + 'zn' + str(zn) + 'Iw' + str(nList[nTriplet][0]) + 'Oa' + str(nList[nTriplet][1])+ 'Od' + str(nList[nTriplet][2])
         if self.TripletMeas.has_key(nTag):
            _AdcData[nTriplet] = self.TripletMeas[nTag]['ADC']
            _measData[nTriplet] = self.TripletMeas[nTag].copy()
         else:
            _measData[nTriplet]['BPI'], _measData[nTriplet]['TPI'], _measData[nTriplet]['zHtClr'] = self.measureBPIAndTPI(hd, zn, nList[nTriplet])

            if testSwitch.SMR_TRIPLET_OPTI_WITH_EFFECTIVE_TPIC == 1:
               _measData[nTriplet]['TPI_ODSS'], _measData[nTriplet]['TPI_IDSS'],  _measData[nTriplet]['RD_OFST_ODSS'], _measData[nTriplet]['RD_OFST_IDSS'] = self.measureSingleSidedTPI(hd, zn, nList[nTriplet])
               _measData[nTriplet]['TPI_DSS'] = _measData[nTriplet]['TPI']
               backoffDS = self.settings['WriteFaultThreshold'][zn] - self.settings['TPIMeasurementMargin'][zn]
               backoffSS = 2 * self.settings['WriteFaultThresholdSlimTrack'][zn] - 2 * self.settings['TPIMeasurementMargin'][zn]
               objMsg.printMsg('track_per_band = %s backoffDS = %s  backoffSS = %s zn = %s' % (str(self.tracksPerBand[zn]),str(backoffDS),str(backoffSS), str(zn)))
               # Special Case for backward compatability
               if self.tracksPerBand[zn] == 1:
                  tpi_sss = _measData[nTriplet]['TPI_DSS']
                  backoffSS = backoffDS
                  direction = 'IDSS'
                  _measData[nTriplet]['ShingleDirection'] = SHINGLE_DIRECTION_OD_TO_ID
                  #_measData[nTriplet]['ReadOffset'] = 0

               elif _measData[nTriplet]['TPI_ODSS'] > _measData[nTriplet]['TPI_IDSS']:
                  tpi_sss = _measData[nTriplet]['TPI_ODSS']
                  direction = 'ODSS'
                  _measData[nTriplet]['ShingleDirection']  = SHINGLE_DIRECTION_ID_TO_OD
                  #_measData[nTriplet]['ReadOffset'] = meas['RD_OFST_ODSS']

               else:
                  tpi_sss = _measData[nTriplet]['TPI_IDSS']
                  direction = 'IDSS'
                  _measData[nTriplet]['ShingleDirection']  = SHINGLE_DIRECTION_OD_TO_ID
                  #_measData[nTriplet]['ReadOffset'] = meas['RD_OFST_IDSS']

               # Another Special Case, if single sided capability is less than double sided, set everything to double sided
               #if (tpi_sss - backoffSS) <= (_measData[nTriplet]['TPI_DSS'] - backoffDS):
               #   tpi_sss = _measData[nTriplet]['TPI_DSS']
               #   backoffSS = backoffDS
               #   direction = 'IDSS'
               #   _measData[nTriplet]['ShingleDirection'] = SHINGLE_DIRECTION_OD_TO_ID
               #   #self.data[hd][zn]['ReadOffset'] = 0
               objMsg.printMsg('tpi_sss = %s TPI_DSS = %s backoffSS = %s backoffDS = %s' % (str(tpi_sss), str(_measData[nTriplet]['TPI_DSS']),str(backoffSS),str(backoffDS)))
               sp = float(self.settings['ShingledProportion'][zn])
               tpb = float(self.tracksPerBand[zn])
               effectiveTpic = (tpb - TP.TG_Coef)/tpb * sp * (tpi_sss - backoffSS) + ( 1 - sp + sp * TP.TG_Coef/tpb) * (_measData[nTriplet]['TPI_DSS'] - backoffDS)
               _measData[nTriplet]['TpiCapability'] = effectiveTpic
               #_measData[nTriplet]['TPI'] = effectiveTpic. still remain the double size tpic
               _measData[nTriplet]['TpiCapabilitySSS'] = tpi_sss - backoffSS
               _measData[nTriplet]['TpiCapabilityDSS'] = _measData[nTriplet]['TPI_DSS'] - backoffDS

            _AdcData[nTriplet] = _measData[nTriplet]['BPI'] * _measData[nTriplet]['TPI'] #  * Clr Weighting Function
            if _measData[nTriplet]['BPI'] == -1 and _measData[nTriplet]['TPI'] == -1:
               _AdcData[nTriplet] = -1
            self.TripletMeas[nTag] = {}
            self.TripletMeas[nTag] = _measData[nTriplet].copy()

            self.TripletMeas[nTag]['ADC'] = _AdcData[nTriplet]
            self.TripletMeas[nTag]['IW'], self.TripletMeas[nTag]['OA'], self.TripletMeas[nTag]['OD']  = nList[nTriplet]

      return _AdcData, _measData

   def calcBPIBackoff(self, hd, zn, adjustment, wp=None):
      # According to the algorithm, we need to use BPI capability minus the BPI margin to test TPI capability
      _wp = self.opMode == 'WpZones' and wp or None
      bpic = self.measWPZns.getRecord('BPI', hd, zn, _wp)
      raw_bpic = self.formatScaler.unscaleBPI(hd, zn, bpic)
      
      #objMsg.printMsg("Hd %s zn %s raw_bpic %s adjustment %s self.opMode %s bpic %s" % (str(hd), str(zn), str(raw_bpic), str(adjustment),str(self.opMode),str(bpic)))
      adjBpiForTpi = int(100*raw_bpic) + adjustment - 100

      return adjBpiForTpi

   #-------------------------------------------------------------------------------------------------------
   def measureTPI(self, hd, zn, tpiFeedForward, wp=None, prm_override=getattr(TP, 'MeasureTPI_211', {}), zapOTF=0):
      ############# Set up parameter block ##############
      prm_TPI_211 = {'test_num'           : 211,
                     'prm_name'           : 'MeasureTPI_211',
                     'TEST_HEAD'          : hd,
                     'ZONE'               : zn,
                     'NUM_TRACKS_PER_ZONE': 6,
                     'NUM_SQZ_WRITES'     : TP.num_sqz_writes,
                     'ZONE_POSITION'      : TP.VBAR_ZONE_POS,
                     'CWORD1'             : 0x1002,   #Update W+Heat, tpic_measurement
                     'SET_OCLIM'          : 655,
                     'TARGET_SER'         : 5,
                     'TPI_TARGET_SER'     : 5,
                     'RESULTS_RETURNED'   : 0x000F,
                     'timeout'            : 3600,
                     'spc_id'             : 0,
                     'TPI_TLEVEL'         : TP.TPI_TLEVEL,
      }

      if testSwitch.SMR:
         prm_TPI_211.update({'ADJ_BPI_FOR_TPI' : self.calcBPIBackoff(hd, zn, 0, wp)})
      else:
         prm_TPI_211.update({'ADJ_BPI_FOR_TPI' : self.calcBPIBackoff(hd, zn, -5, wp)})

      prm_TPI_211.update(prm_override)

      if zapOTF == 1:
         prm_TPI_211.update(TP.prm_ZAP_OTF)
         prm_TPI_211['CWORD1'] |= 0x800
         prm_TPI_211['TRACK_LIMIT'] = 0x0101
         prm_TPI_211['timeout'] = 3*prm_TPI_211['timeout']/2

      # if the write powers have already been selected, do the measurements at nominal clearance
      if self.opMode == 'AllZones':
         prm_TPI_211['CWORD1'] &= 0xFFAF

      #Scale the TPI capability from the last measurement up to servo dacs of capabilty
      # TPI Cap in Servo Dacs = (TPI capability(relative to nominal = 1.0) - 1.0) * 256
      #Set the starting point for the TPI margin feedback
      prm_TPI_211['START_OT_FOR_TPI'] = int(round((tpiFeedForward-1)*256,0)) - 10

      ############# Run the measurement ##############

      table_TpiCap = DBLogReader(self.__dut, 'P211_TPI_CAP_AVG')
      table_TpiCap.ignoreExistingData()

      if testSwitch.SMR:
         if testSwitch.T211_MERGE_READ_OFFSET_TBL_INTO_TPI_MEAS_TBL:
            table_RdOfst = table_TpiCap
         else:
            table_RdOfst = DBLogReader(self.__dut, 'P211_RD_OFST_AVG')
            table_RdOfst.ignoreExistingData()

      self.oProc.St(prm_TPI_211)
      row = table_TpiCap.findRow({'HD_LGC_PSN':hd, 'DATA_ZONE':zn})
      if row:
         tpi = float(row['TPI_CAP_AVG'])
      else:
         tpi = 0.0
      if testSwitch.SMR:
         row = table_RdOfst.findRow({'HD_LGC_PSN':hd, 'DATA_ZONE':zn})
         if row:
            rd_ofst = float(row['RD_OFST_AVG'])
         else:
            rd_ofst = 0.0
         objMsg.printMsg('tpi = %s rd_ofst = %s' % (str(tpi),str(rd_ofst)))
         return tpi, rd_ofst
      else:
         objMsg.printMsg('kkktpi = %s ' % (str(tpi)))
         return tpi


   def measureSingleSidedTPI(self, hd, zn, wrTriplet):

      wc, ovs, ovd = wrTriplet
      if testSwitch.extern._128_REG_PREAMPS:
         wc = wc * 7 + 20
         ovs = ovs * 2
         ovd = ovd * 2

      objMsg.printMsg('measureSingleSidedTPI:wrTriplet = %s' % (str(wrTriplet)))
      meas = CVbarDataHelper(self.measWPZns, hd, zn, wrTriplet)

      tpiFeedForward = meas['TPI'] + .05   # single sided should be easier then double sided

      # do id single sided measurement
      prmOverride = deepcopy(TP.MeasureTPI_211)
      prmOverride.update( {'CWORD1' : 0x1002} ) #override default 
      prmOverride.update( {'TEST_HEAD': hd, 'ZONE': zn, 'WRITE_CURRENT':wc, 'DAMPING':ovs, 'DURATION':ovd} )
      prmOverride.update({'NUM_SQZ_WRITES':0x8000 + TP.num_sqz_writes, 'CWORD2':8})
      meas['TPI_IDSS'], meas['RD_OFST_IDSS'] = self.measureTPI(hd,zn,tpiFeedForward,wrTriplet,prm_override = prmOverride)
      meas['TPI_IDSS'] = self.formatScaler.scaleTPI(hd,zn,meas['TPI_IDSS'])

      # do od single sided measurement
      prmOverride.update({'NUM_SQZ_WRITES':0x4000 + TP.num_sqz_writes,'CWORD2':8})
      meas['TPI_ODSS'], meas['RD_OFST_ODSS'] = self.measureTPI(hd,zn,tpiFeedForward,wrTriplet,prm_override = prmOverride)
      meas['TPI_ODSS'] = self.formatScaler.scaleTPI(hd,zn,meas['TPI_ODSS'])

      return meas['TPI_ODSS'], meas['TPI_IDSS'], meas['RD_OFST_ODSS'], meas['RD_OFST_IDSS']


   #-------------------------------------------------------------------------------------------------------
   def measureBPIAndTPI(self, hd, zn, wrTriplet):
      zapOTF = 0
      wc, ovs, ovd = wrTriplet

      prm = {
             'test_num'           : 211,
             'prm_name'           : 'Triplet Opti Measure BPI and TPI',
             'timeout'            : 3600 * ( 1 + self.numHeads/2),
             'spc_id'             : 0,
             'NUM_TRACKS_PER_ZONE': 6,
             'ZONE_POSITION'      : TP.VBAR_ZONE_POS,
             'BPI_MAX_PUSH_RELAX' : TP.VbarBpiMaxPushRelax,
             'NUM_SQZ_WRITES'     : TP.num_sqz_writes,
             'CWORD1'             : 0x1003,   #run HMS, TPI, BPI
             'CWORD2'             : 0x0010,   #BPIC by BIE
             'ADJ_BPI_FOR_TPI'    : 0, #TP.VbarAdjBpiForTpi,
             'DblTablesToParse'   : ['P211_WRT_PWR_TBL'],
             'TARGET_SER'         : TP.VbarTargetSER,
             'TPI_TARGET_SER'     : 5,
             'TPI_TLEVEL'         : TP.TPI_TLEVEL,
             'TLEVEL'             : 0,
             'THRESHOLD'          : 65,
             'RESULTS_RETURNED'   : 0x000F, #cut log size
      }

      if testSwitch.extern._128_REG_PREAMPS:
         wc = wc * 7 + 20
         ovs = ovs * 2
         ovd = ovd * 2

      prm.update( {'TEST_HEAD': hd, 'ZONE': zn, 'WRITE_CURRENT':wc, 'DAMPING':ovs, 'DURATION':ovd} )

      if not testSwitch.extern.BF_0168996_007867_VBAR_REPLACE_INACCURATE_WP_TBL:
         # Oops, still older firmware - still using older table.
         prm['DblTablesToParse'] = ['P211_WP_TBL']

      #if self.opMode == 'AllZones':
      #   prm['RESULTS_RETURNED'] = 0x0006

      if zapOTF == 1:
         prm.update(TP.prm_ZAP_OTF)
         prm['CWORD1'] |= 0x800
         prm['TRACK_LIMIT'] = 0x0101
         prm['timeout'] = 3*prm['timeout']/2

      if testSwitch.extern.BF_0168996_007867_VBAR_REPLACE_INACCURATE_WP_TBL:
         # This fw flag supports a new table with a HD_LGC_PSN col, containing logical head values.
         table = DBLogReader(self.__dut, 'P211_WRT_PWR_TBL', suppressed = True)
         colName = 'HD_LGC_PSN'
      else:
         table = DBLogReader(self.__dut, 'P211_WP_TBL', suppressed = True)
         colName = 'HD_PHYS_PSN'
      #table.ignoreExistingData()

      # Run the test
      self.oProc.St(prm)

      record = table.getTableObj()[-1]

      hd = int(record[colName])
      zn = int(record['DATA_ZONE'])
      meas = CVbarDataHelper(self.measWPZns, hd, zn, wrTriplet)
      meas['BPI'] = self.formatScaler.scaleBPI(hd, zn, float(record['BPICAP']))
      meas['TPI'] = self.formatScaler.scaleTPI(hd, zn, float(record['TPICAP']))

      if meas['BPI'] < 0.5: meas['BPI'] = 0.5
      if meas['TPI'] < 0.5: meas['TPI'] = 0.5

      meas['zHtClr'] = MatchTargetClrUnit(float(record['ZEROHEATCLR']))
      meas['Interp'] = 'F'

      return meas['BPI'], meas['TPI'], meas['zHtClr']

  #-------------------------------------------------------------------------------------------------------
   def __measureTripletTPI(self, hd, zn, nBpi, wrTriplet, tpiFeedForward):

      prm = self.__prmTripletMeasTPI.copy()
      # According to the algorithm, we need to use BPI capability minus the BPI margin to test TPI capability
      # But for Triplet Opti, need to set adjustment to 0
      adjBpiForTpi = int(100* nBpi) - 100 # offset from nominal

      prm.update( {'TEST_HEAD':hd, 'ZONE':zn, 'ADJ_BPI_FOR_TPI':adjBpiForTpi})

      wc, ovs, ovd = wrTriplet
      prm.update( {'WRITE_CURRENT':wc, 'DAMPING':ovs, 'DURATION':ovd})


      #Scale the TPI capability from the last measurement up to servo dacs of capabilty
      # TPI Cap in Servo Dacs = (TPI capability(relative to nominal = 1.0) - 1.0) * 256
      if not hasattr(TP,'TPI_Feedback_Margin'):
         TPI_Feedback_Margin = 2
      else:
         TPI_Feedback_Margin = TP.TPI_Feedback_Margin

      #Set the starting point for the TPI margin feedback
      prm['START_OT_FOR_TPI'] = int(round((tpiFeedForward-1)*256,0)) - TPI_Feedback_Margin

      try:
         startIndex = len(self.__dut.dblData.Tables('P211_TPI_CAP_AVG'))
      except:
         #No data available
         startIndex = 0

      #For repeatability options loop through the zone measurement TP.VbarNumMeasPerZone times
      tpi = -1.0
      cnt = 0; retries = 0; succ = 0
      # retry loop for measurement exceptions
      while cnt<=retries:
         cnt += 1
         objMsg.printMsg('TPI MEASUREMENT: WP:%s, Hd:%d, Zn:%d, ATTEMPT:%d,' % (wrTriplet, hd, zn, cnt,))
         try:
            self.oProc.St(prm, failSafe=1)
            try:
               endIndex = len(self.__dut.dblData.Tables('P211_TPI_CAP_AVG'))
            except:
               #No data available
               endIndex = 0
            if startIndex <> endIndex:
               colDict = self.__dut.dblData.Tables('P211_TPI_CAP_AVG').columnNameDict()
               row = self.__dut.dblData.Tables('P211_TPI_CAP_AVG').rowListIter(index=len(self.__dut.dblData.Tables('P211_TPI_CAP_AVG'))-1).next()
               tpi = float(row[colDict['TPI_CAP_AVG']])
            else:
               objMsg.printMsg('TPI MEASUREMENT EXCEPTION!! : WP:%s, Hd:%d, Zn:%d' % (wrTriplet, hd, zn))
               objMsg.printMsg('--- POWER CYCLE ---')
               objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1) # power cycle to overcome the measurement (T211) exception

         except ScriptTestFailure, (failureData):
            ec = failureData[0][2]
            objMsg.printMsg(traceback.format_exc())
            objMsg.printMsg('TPI MEASUREMENT EXCEPTION!! : WP:%s, Hd:%d, Zn:%d' % (wrTriplet, hd, zn))
            objMsg.printMsg('--- POWER CYCLE RETRY ---')
            objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1) # power cycle to overcome the measurement (T211) exception
         else:
            succ = 1
            break

      ## fail drive if measurement failed ONLY for Flash LED issues
      if not succ and ec in [11087,11231]:
         objMsg.printMsg("Fail code ec %s" % str(ec))
         raiseException(ec, 'TPI Measurement Failed for Flash_LED issue in self test 211')

      return tpi
   #-------------------------------------------------------------------------------------------------------
   def __measureTripletBPI(self, hd, zn, wrTriplet):

      prm = self.__prmTripletMeasBPI.copy()
      wc, ovs, ovd = wrTriplet
      bpi = -1
      zHtClr = 0
      prm.update( {'TEST_HEAD': hd, 'ZONE': zn, 'WRITE_CURRENT':wc, 'DAMPING':ovs, 'DURATION':ovd} )

      measList = []
      try:
         startIndex = len(self.__dut.dblData.Tables('P211_BPI_CAP_AVG'))
      except:
         #No data available
         startIndex = 0

      #For repeatability options loop through the zone measurement TP.VbarNumMeasPerZone times
      # retry loop for measurement exceptions
      cnt = 0; retries = 0; succ = 0
      while cnt<=retries:
         cnt += 1
         objMsg.printMsg('BPI MEASUREMENT: WP:%s, Hd:%d, Zn:%d, ATTEMPT:%d,' % (wrTriplet, hd, zn, cnt,))

         try:
            self.oProc.St(prm, failSafe=1)
            try:
               endIndex = len(self.__dut.dblData.Tables('P211_BPI_CAP_AVG'))
            except:
               #No data available
               endIndex = 0
            if startIndex <> endIndex:
               colDict = self.__dut.dblData.Tables('P211_BPI_CAP_AVG').columnNameDict()
               row = self.__dut.dblData.Tables('P211_BPI_CAP_AVG').rowListIter(index=len(self.__dut.dblData.Tables('P211_BPI_CAP_AVG'))-1).next()
               zHtClr = float(row[colDict['ZERO_HEAT_CLR']])
               bpi = float(row[colDict['BPI_CAP_AVG']])
               objMsg.printMsg('bpi: %4f   Ht:%4f' % (bpi,zHtClr))
               measList.append(bpi)
            else:
               objMsg.printMsg('BPI MEASUREMENT EXCEPTION!! : WP:%s, Hd:%d, Zn:%d' % (wrTriplet, hd, zn))
               objMsg.printMsg('--- POWER CYCLE ---')
               objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1) # power cycle to overcome the measurement (T211) exception

         except ScriptTestFailure, (failureData):
            ec = failureData[0][2]
            objMsg.printMsg(traceback.format_exc())
            objMsg.printMsg('BPI MEASUREMENT EXCEPTION!! : WP:%s, Hd:%d, Zn:%d' % (wrTriplet, hd, zn))
            objMsg.printMsg('--- POWER CYCLE RETRY ---')
            objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1) # power cycle to overcome the measurement (T211) exception
         else:
            succ = 1
            break

      ## fail drive if measurement failed ONLY for Flash LED issues
      if not succ and ec in [11087,11231]:
         objMsg.printMsg("Fail code ec %s" % str(ec))
         raiseException(ec, 'BPI Measurement Failed for Flash_LED issue in self test 211')

      return bpi, zHtClr
   
   #-------------------------------------------------------------------------------------------------------
   def build_Initial_Sweeplist(self, Iw_pts, Osa_pts, Osd):
      printDbgMsg('Iw_pts: %s' % (Iw_pts))
      printDbgMsg('Osa_pts: %s' % (Osa_pts))
      sweepList_Cross = {}
      #tIndex = 0
      #for nWc in Iw_pts:
      #   for nOa in Osa_pts:
      #      sweepList_Cross[tIndex] = nWc, nOa, Def_Triplet[2]
      #      tIndex += 1
      
      # Define the intial points 
      sweepList_Cross[0] = Iw_pts[0], Osa_pts[0], Osd
      sweepList_Cross[1] = Iw_pts[0], Osa_pts[3], Osd
      sweepList_Cross[2] = Iw_pts[1], Osa_pts[1], Osd
      sweepList_Cross[3] = Iw_pts[1], Osa_pts[2], Osd
      sweepList_Cross[4] = Iw_pts[2], Osa_pts[1], Osd
      sweepList_Cross[5] = Iw_pts[2], Osa_pts[2], Osd
      sweepList_Cross[6] = Iw_pts[3], Osa_pts[0], Osd
      sweepList_Cross[7] = Iw_pts[3], Osa_pts[3], Osd
      
      printDbgMsg('sweepList_Cross: %s' % sweepList_Cross)
      # Define the Areas
      Areas = {
            'S01': [(Iw_pts[0],Osa_pts[0]),(Iw_pts[1],Osa_pts[1]),(Iw_pts[1],Osa_pts[2])],
            'S02': [(Iw_pts[0],Osa_pts[0]),(Iw_pts[1],Osa_pts[1]),(Iw_pts[2],Osa_pts[1])],
            'S03': [(Iw_pts[0],Osa_pts[0]),(Iw_pts[1],Osa_pts[2]),(Iw_pts[0],Osa_pts[3])],
            'S04': [(Iw_pts[0],Osa_pts[0]),(Iw_pts[2],Osa_pts[1]),(Iw_pts[3],Osa_pts[0])],
            'S05': [(Iw_pts[1],Osa_pts[2]),(Iw_pts[1],Osa_pts[1]),(Iw_pts[2],Osa_pts[1])],
            'S06': [(Iw_pts[2],Osa_pts[2]),(Iw_pts[1],Osa_pts[2]),(Iw_pts[1],Osa_pts[1])],
            'S07': [(Iw_pts[1],Osa_pts[1]),(Iw_pts[2],Osa_pts[1]),(Iw_pts[2],Osa_pts[2])],
            'S08': [(Iw_pts[2],Osa_pts[1]),(Iw_pts[2],Osa_pts[2]),(Iw_pts[1],Osa_pts[2])],
            'S09': [(Iw_pts[0],Osa_pts[3]),(Iw_pts[1],Osa_pts[2]),(Iw_pts[1],Osa_pts[1])],
            'S10': [(Iw_pts[0],Osa_pts[3]),(Iw_pts[2],Osa_pts[2]),(Iw_pts[1],Osa_pts[2])],
            'S11': [(Iw_pts[3],Osa_pts[0]),(Iw_pts[2],Osa_pts[1]),(Iw_pts[1],Osa_pts[1])],
            'S12': [(Iw_pts[3],Osa_pts[0]),(Iw_pts[2],Osa_pts[2]),(Iw_pts[2],Osa_pts[1])],
            'S13': [(Iw_pts[3],Osa_pts[0]),(Iw_pts[3],Osa_pts[3]),(Iw_pts[2],Osa_pts[2])],
            'S14': [(Iw_pts[3],Osa_pts[3]),(Iw_pts[2],Osa_pts[2]),(Iw_pts[1],Osa_pts[2])],
            'S15': [(Iw_pts[3],Osa_pts[3]),(Iw_pts[2],Osa_pts[1]),(Iw_pts[2],Osa_pts[2])],
            'S16': [(Iw_pts[3],Osa_pts[3]),(Iw_pts[1],Osa_pts[2]),(Iw_pts[0],Osa_pts[3])],
         }
      if not testSwitch.CM_REDUCTION_REDUCE_PRINTMSG:
         for area in sorted(Areas.keys()):
            objMsg.printMsg('Area: %s  Combination: %s' % (area, Areas[area]))
      
      return Areas, sweepList_Cross
   
   #-------------------------------------------------------------------------------------------------------
   def find_max_triplet_integrated_ATISTE(self,headRange, test_zones, Def_Triplet, Hd_EWAC_Data):
      
      if testSwitch.extern._128_REG_PREAMPS:
         Tpi_triplet = [Def_Triplet[0] * 7 + 20, Def_Triplet[1] * 2, Def_Triplet[2] *2]
      else:
         Tpi_triplet = list(Def_Triplet)
      ati_param = deepcopy(TP.prm_Triplet_ATI_STE)
      wpcT178_prm = deepcopy(TP.WPC_TripletPrm_178)
      
      if 0: # For Debug purpose only
         # Reset Write Power
         if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
            if 'BIT_MASK' in wpcT178_prm:     del wpcT178_prm['BIT_MASK'] 
            if 'BIT_MASK_EXT' in wpcT178_prm: del wpcT178_prm['BIT_MASK_EXT']
            if testSwitch.extern.FE_0270095_504159_SUPPORT_LOOPING_ZONE_T178:   
               wpcT178_prm['ZONE'] = self.__numUserZones - 1 #dont update system zone
               wpcT178_prm['prm_name'] = 'prm_wp_178_0x%04x' % wpcT178_prm['ZONE']
               self.setTriplet(wpcT178_prm, Def_Triplet, 0x3FF)
            else:
               for zn in test_zones:
                  wpcT178_prm['ZONE'] = zn
                  self.setTriplet(wpcT178_prm, Def_Triplet, 0x3FF)
         else:
            wpcT178_prm.update({'BIT_MASK': (65535L, 65535L), 'BIT_MASK_EXT': (8191L, 65535)})
            self.setTriplet(wpcT178_prm, Def_Triplet, 0x3FF)
         self.oProc.St({'test_num':178, 'prm_name':'Save RAP in RAM to FLASH', 'CWORD1':0x220})
      
      max_ati_ste_triplet = {}
      
      meas_data = {}
      fail_list = {}
      final_WP_index = {}
      for hd in headRange:
         meas_data[hd] = {}
         final_WP_index[hd] = len(TP.IwMaxCap)
         fail_list[hd] = []
         for zn in test_zones:
            fail_list[hd].append(zn)
            meas_data[hd][zn] = {}
            meas_data[hd][zn]['OFFSET'] = 0
      
      if testSwitch.FE_0273368_348429_ENABLE_TPINOMINAL or testSwitch.FE_0273368_348429_TEMP_ENABLE_TPINOMINAL_FOR_ATI_STE:
         ati_param['CWORD1'] = ati_param['CWORD1'] & 0xBFFF # reset to zero
      else:
         ###################
         # Set up TPI Data #
         ###################
         for hd in headRange:
            max_ati_ste_triplet[hd] = {}
            if not Hd_EWAC_Data.has_key(hd) or not (Hd_EWAC_Data[hd] > 1.0 and Hd_EWAC_Data[hd] < 4.0):
               Hd_EWAC_Data[hd] = TP.TPI_EWAC_Coeff['NOMINAL']
            meas_data[hd]['TPI_EWAC'] = (Hd_EWAC_Data[hd] - TP.TPI_EWAC_Coeff['INTERCEPT']) / TP.TPI_EWAC_Coeff['SLOPE']
            offset = int((1 - (1/meas_data[hd]['TPI_EWAC'])) * 256)
            #objMsg.printMsg("Hd_EWAC_DBG Hd: %d EWAC: %4f TPI %4f Offset %d" % (hd,Hd_EWAC_Data[hd], tpic, offset))
            
            for zn in test_zones:
               meas_data[hd][zn]['TPI_MEAS'] = self.__measureTripletTPI(hd, zn, 1, Tpi_triplet, meas_data[hd]['TPI_EWAC'])
               meas_data[hd][zn]['TPI_MEAS'] = self.formatScaler.scaleTPI(hd, zn, meas_data[hd][zn]['TPI_MEAS'])
               meas_data[hd][zn]['TPI_MEAS'] *= ( 1 - TP.TPI_Write_Fault_Threshold )
               if meas_data[hd][zn]['TPI_MEAS'] > 0.0: #Take T211 if valid meas, else retain EWAC TPIC
                  tpic = meas_data[hd][zn]['TPI_MEAS']
                  
               else:
                  tpic = meas_data[hd]['TPI_EWAC']
                  
               meas_data[hd][zn]['OFFSET'] = int((1 - (1.0/tpic)) * 256)
               objMsg.printMsg("Hd_EWAC_DBG2 Hd: %d EWAC: %4f TPI %4f Offset %d" % (hd,Hd_EWAC_Data[hd], tpic, offset))
      
      for WP_index in range(len(TP.IwMaxCap)):
         ######################################
         # Update Write Power all Zones, test 1 DAC Above the Limits
         ######################################
         for hd in sorted(fail_list.keys()):
            hd_mask = 0x3FF & (1<<hd) # write to one head at a time
            if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
               if 'BIT_MASK' in wpcT178_prm:     del wpcT178_prm['BIT_MASK'] 
               if 'BIT_MASK_EXT' in wpcT178_prm: del wpcT178_prm['BIT_MASK_EXT']
               if testSwitch.extern.FE_0270095_504159_SUPPORT_LOOPING_ZONE_T178:   
                  wpcT178_prm['ZONE'] = self.__numUserZones - 1 #dont update system zone
                  wpcT178_prm['prm_name'] = 'prm_wp_178_0x%04x_%s_%s_%s' % (wpcT178_prm['ZONE'], TP.IwMaxCap[WP_index], TP.OaMaxCap[WP_index], Def_Triplet[2])
                  self.setTriplet(wpcT178_prm, [TP.IwMaxCap[WP_index], TP.OaMaxCap[WP_index], Def_Triplet[2]], hd_mask)
               else:
                  for zn in test_zones:
                     wpcT178_prm['ZONE'] = zn
                     self.setTriplet(wpcT178_prm, [TP.IwMaxCap[WP_index], TP.OaMaxCap[WP_index], Def_Triplet[2]], hd_mask)
            else:
               wpcT178_prm.update({'BIT_MASK': (65535L, 65535L), 'BIT_MASK_EXT': (8191L, 65535)})
               self.setTriplet(wpcT178_prm, [TP.IwMaxCap[WP_index], TP.OaMaxCap[WP_index], Def_Triplet[2]], hd_mask)
         # update Flash
         self.oProc.St({'test_num':178, 'prm_name':'Save RAP in RAM to FLASH', 'CWORD1':0x220})
         # Dump Data
         #self.oProc.St({'test_num':172,'spc_id': 100, 'prm_name':'dispWorkingAdapts', 'CWORD1':4})
         ######################################
         # Setup TableIndex
         ######################################
         try: startIndex = len(self.__dut.dblData.Tables('P051_ERASURE_BER'))
         except: startIndex = 0 #No data available
         # VE Data
         if testSwitch.virtualRun:
            colDict = self.__dut.dblData.Tables('P051_ERASURE_BER').columnNameDict()
            tableData = self.__dut.dblData.Tables('P051_ERASURE_BER').rowListIter()
            for idx, row in enumerate(tableData):
               if int(row[colDict['SPC_ID']]) == 7000:
                  startIndex = idx
                  break

         ######################################
         # Execute Test 51 on fail heads/zones
         ######################################
         for hd in sorted(fail_list.keys()):
            for zn in fail_list[hd]:
               # Set up Dictionary
               meas_data[hd][zn][WP_index] = {}
               meas_data[hd][zn][WP_index]['erasure'] = {}
               meas_data[hd][zn][WP_index]['baseline'] = {}
               # Set up Parmeters
               ati_param['TEST_HEAD'] = hd
               ati_param['ZONE'] = zn
               if not testSwitch.FE_0273368_348429_TEMP_ENABLE_TPINOMINAL_FOR_ATI_STE:
                  ati_param['OFFSET'] = -1 * meas_data[hd][zn]['OFFSET']
               
               try: self.oProc.St(ati_param)
               except: 
                  # power cycle when t51 report reading system failure
                  objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
                  pass
               
         ######################################
         # Retreive ATI/STE Data
         ######################################
         try: endIndex = len(self.__dut.dblData.Tables('P051_ERASURE_BER'))
         except: endIndex = startIndex #No data available
         # VE Data
         if testSwitch.virtualRun:
            tableData = self.__dut.dblData.Tables('P051_ERASURE_BER').rowListIter()
            for idx, row in enumerate(tableData):
               if int(row[colDict['SPC_ID']]) > 7000:
                  startIndex = idx-1
                  break

         if endIndex != startIndex:
            colDict = self.__dut.dblData.Tables('P051_ERASURE_BER').columnNameDict()
            tableData = self.__dut.dblData.Tables('P051_ERASURE_BER').rowListIter(index=startIndex)
            for row in tableData:
               hd = int(row[colDict['HD_LGC_PSN']])
               zn = int(row[colDict['DATA_ZONE']])
               RRAW_BER = float(row[colDict['RRAW_BER']])
               BITS_IN_ERROR_BER = float(row[colDict['BITS_IN_ERROR_BER']])
               TEST_TYPE = row[colDict['TEST_TYPE']]
               TRK_INDEX = int(row[colDict['TRK_INDEX']])
               meas_data[hd][zn][WP_index][TEST_TYPE][TRK_INDEX] = RRAW_BER
                  
         ######################################
         # Process ATI/STE Data
         ######################################
         new_fail_list = {}
         for hd in sorted(fail_list.keys()):
            for zn in fail_list[hd]:
               meas_data[hd][zn][WP_index]['STATUS'] = 'PASS' # Set Initially to Pass
               if meas_data[hd][zn][WP_index]['erasure'] == {} or meas_data[hd][zn][WP_index]['baseline'] == {}:
                  # If no data, add hd,zn to the new list of failures
                  if not new_fail_list.has_key(hd):
                     new_fail_list[hd] = [zn]
                  else:
                     new_fail_list[hd].append(zn)
                     
                  # Update data for dblog reporting
                  meas_data[hd][zn][WP_index]['STATUS'] = 'NO_DATA'
                  meas_data[hd][zn][WP_index]['WorseBER_BASE'] = -1
                  meas_data[hd][zn][WP_index]['WorseBER_ATI'] = -1
                  meas_data[hd][zn][WP_index]['MaxDelta_ATI'] = -1
                  meas_data[hd][zn][WP_index]['WorseBER_STE'] = -1
                  meas_data[hd][zn][WP_index]['MaxDelta_STE'] = -1
               else:
                  # Get the worse Baseline BER
                  for TRK_INDEX in meas_data[hd][zn][WP_index]['baseline'].keys():
                     if not meas_data[hd][zn][WP_index].has_key('WorseBER_BASE'):
                        meas_data[hd][zn][WP_index]['WorseBER_BASE'] = meas_data[hd][zn][WP_index]['baseline'][TRK_INDEX]
                     elif meas_data[hd][zn][WP_index]['baseline'][TRK_INDEX] < meas_data[hd][zn][WP_index]['WorseBER_BASE']:
                        meas_data[hd][zn][WP_index]['WorseBER_BASE'] = meas_data[hd][zn][WP_index]['baseline'][TRK_INDEX]
                        
                  # Get the worse ATI/STE BER and Delta
                  for TRK_INDEX in meas_data[hd][zn][WP_index]['erasure'].keys():
                     delta_ber = meas_data[hd][zn][WP_index]['baseline'][TRK_INDEX] - meas_data[hd][zn][WP_index]['erasure'][TRK_INDEX]
                     
                     if TRK_INDEX in [1,-1]:  # ATI Track index
                        # Record the max delta BER
                        if not meas_data[hd][zn][WP_index].has_key('MaxDelta_ATI'):
                           meas_data[hd][zn][WP_index]['MaxDelta_ATI'] = delta_ber
                        elif meas_data[hd][zn][WP_index]['MaxDelta_ATI'] < delta_ber:
                           meas_data[hd][zn][WP_index]['MaxDelta_ATI'] = delta_ber
                        # Record the worse erasure BER
                        if not meas_data[hd][zn][WP_index].has_key('WorseBER_ATI'):
                           meas_data[hd][zn][WP_index]['WorseBER_ATI'] = meas_data[hd][zn][WP_index]['erasure'][TRK_INDEX]
                        elif meas_data[hd][zn][WP_index]['WorseBER_ATI'] > meas_data[hd][zn][WP_index]['erasure'][TRK_INDEX]:
                           meas_data[hd][zn][WP_index]['WorseBER_ATI'] = meas_data[hd][zn][WP_index]['erasure'][TRK_INDEX]
                     else: # STE Track Index
                        # Record the max delta BER
                        if not meas_data[hd][zn][WP_index].has_key('MaxDelta_STE'):
                           meas_data[hd][zn][WP_index]['MaxDelta_STE'] = delta_ber
                        elif meas_data[hd][zn][WP_index]['MaxDelta_STE'] < delta_ber:
                           meas_data[hd][zn][WP_index]['MaxDelta_STE'] = delta_ber
                        # Record the worse erasure BER
                        if not meas_data[hd][zn][WP_index].has_key('WorseBER_STE'):
                           meas_data[hd][zn][WP_index]['WorseBER_STE'] = meas_data[hd][zn][WP_index]['erasure'][TRK_INDEX]
                        elif meas_data[hd][zn][WP_index]['WorseBER_STE'] > meas_data[hd][zn][WP_index]['erasure'][TRK_INDEX]:
                           meas_data[hd][zn][WP_index]['WorseBER_STE'] = meas_data[hd][zn][WP_index]['erasure'][TRK_INDEX]
                     
                  if WP_index > 0:
                     # Check if the ATI BER did become worse compared to previous Write Power
                     if TP.TRIPLET_CRITERIA_ATI_STE_51['poorer_ber_delta_limit'][0]:
                        if meas_data[hd][zn][WP_index - 1].has_key('WorseBER_ATI'):
                           # cater for when BER is droping due to lower write power rather than improve ATI
                           if meas_data[hd][zn][WP_index - 1]['WorseBER_ATI'] - meas_data[hd][zn][WP_index]['WorseBER_ATI'] >= TP.TRIPLET_CRITERIA_ATI_STE_51['poorer_ber_delta_limit'][1] and meas_data[hd][zn][WP_index - 1]['WorseBER_ATI'] > 5.0: 
                              meas_data[hd][zn][WP_index]['STATUS'] = 'FAIL_BASE_ATI'
                     # Check if the STE BER did become worse compared to previous Write Power
                     if TP.TRIPLET_CRITERIA_ATI_STE_51['poorer_ber_delta_limit'][2] and meas_data[hd][zn][WP_index]['STATUS'] == 'PASS':
                        if meas_data[hd][zn][WP_index - 1].has_key('WorseBER_STE'):
                           # cater for when BER is droping due to lower write power rather than improve STE
                           if meas_data[hd][zn][WP_index - 1]['WorseBER_STE'] - meas_data[hd][zn][WP_index]['WorseBER_STE'] >= TP.TRIPLET_CRITERIA_ATI_STE_51['poorer_ber_delta_limit'][3] and meas_data[hd][zn][WP_index - 1]['WorseBER_STE'] > 5.0: 
                              meas_data[hd][zn][WP_index]['STATUS'] = 'FAIL_BASE_STE'
                        
                  # Check Data against Specs
                  if meas_data[hd][zn][WP_index]['STATUS'] == 'PASS':
                     
                     if TP.TRIPLET_CRITERIA_ATI_STE_51['delta_limit'][0]:
                        # Check Delta ATI BER against specs
                        if meas_data[hd][zn][WP_index]['MaxDelta_ATI'] > TP.TRIPLET_CRITERIA_ATI_STE_51['delta_limit'][1]:
                           meas_data[hd][zn][WP_index]['STATUS'] = 'FAIL_DELTA_ATI_'
                           
                     if TP.TRIPLET_CRITERIA_ATI_STE_51['worse_ber_limit'][0] and meas_data[hd][zn][WP_index]['STATUS'] == 'PASS':
                        # Check Worse ATI BER against specs
                        if meas_data[hd][zn][WP_index]['WorseBER_ATI'] < TP.TRIPLET_CRITERIA_ATI_STE_51['worse_ber_limit'][1]:
                           meas_data[hd][zn][WP_index]['STATUS'] = 'FAIL_ATI_BER'
                           
                     if TP.TRIPLET_CRITERIA_ATI_STE_51['delta_limit'][2] and meas_data[hd][zn][WP_index]['STATUS'] == 'PASS':
                        # Check Worse ATI BER against specs
                        if meas_data[hd][zn][WP_index]['MaxDelta_STE'] > TP.TRIPLET_CRITERIA_ATI_STE_51['delta_limit'][3]:
                           meas_data[hd][zn][WP_index]['STATUS'] = 'FAIL_DELTA_STE'
                     
                     if TP.TRIPLET_CRITERIA_ATI_STE_51['worse_ber_limit'][2] and meas_data[hd][zn][WP_index]['STATUS'] == 'PASS':
                        # Check Worse ATI BER against specs
                        if meas_data[hd][zn][WP_index]['WorseBER_STE'] < TP.TRIPLET_CRITERIA_ATI_STE_51['worse_ber_limit'][3]:
                           meas_data[hd][zn][WP_index]['STATUS'] = 'FAIL_STE_BER'
                           
                  
                  # Finally Add to Fail dictionary of zone is not pass
                  if meas_data[hd][zn][WP_index]['STATUS'] != 'PASS':
                     if not new_fail_list.has_key(hd):
                        new_fail_list[hd] = [zn]
                     else:
                        new_fail_list[hd].append(zn)
                  
               # Update DB Log Table
               if testSwitch.extern._128_REG_PREAMPS:
                  Iw = TP.IwMaxCap[WP_index] * 7 + 20
                  Osa = TP.OaMaxCap[WP_index] * 2
                  Osd = Def_Triplet[2] * 2
               else:
                  Iw = TP.IwMaxCap[WP_index]
                  Osa = TP.OaMaxCap[WP_index]
                  Osd = Def_Triplet[2]
                  
               self.__dut.dblData.Tables('P_TRIPLET_ATI_STE_TEST').addRecord({
                              'HD_PHYS_PSN'           : self.__dut.LgcToPhysHdMap[hd],
                              'DATA_ZONE'             : zn,
                              'SPC_ID'                : self.__dut.objSeq.getSeq(),
                              'OCCURRENCE'            : WP_index,
                              'SEQ'                   : self.__dut.objSeq.getSeq(),
                              'TEST_SEQ_EVENT'        : 1,
                              'HD_LGC_PSN'            : hd,
                              'WP_INDEX'              : WP_index,
                              'WRT_CUR'               : Iw,
                              'OVRSHT_AMP'            : Osa,
                              'OVRSHT_DUR'            : Osd,
                              'WORSE_BASE_BER'        : meas_data[hd][zn][WP_index]['WorseBER_BASE'],
                              'WORSE_ATI_BER'         : meas_data[hd][zn][WP_index]['WorseBER_ATI'],
                              'DELTA_ATI_BER'         : meas_data[hd][zn][WP_index]['MaxDelta_ATI'],
                              'WORSE_STE_BER'         : meas_data[hd][zn][WP_index]['WorseBER_STE'],
                              'DELTA_STE_BER'         : meas_data[hd][zn][WP_index]['MaxDelta_STE'],
                              'STATUS'                : meas_data[hd][zn][WP_index]['STATUS'],
               })
               
         for hd in sorted(fail_list.keys()):
            if hd not in new_fail_list.keys() and final_WP_index[hd] == len(TP.IwMaxCap):
               final_WP_index[hd] = WP_index
               
         # copy to main dictionary
         fail_list = new_fail_list.copy()
         if fail_list == {}:
            break
         
      ######################################
      # Print Summary Table
      ######################################
      if not testSwitch.CM_REDUCTION_REDUCE_PRINTMSG:
         objMsg.printMsg("ATI_STE_DBG: Hd  Zn     WP_IDX   WRT_CUR   OVRSHT_AMP   OVRSHT_DUR  WORSE_BASE   WORSE_ATI    DELTA_ATI    WORSE_STE   DELTA_STE     STATUS")
         for hd in headRange:
            for zn in test_zones:
               for WP_index in range(len(TP.IwMaxCap)):
                  if meas_data[hd][zn].has_key(WP_index):
                     if testSwitch.extern._128_REG_PREAMPS:
                        Iw = TP.IwMaxCap[WP_index] * 7 + 20
                        Osa = TP.OaMaxCap[WP_index] * 2
                        Osd = Def_Triplet[2] * 2
                     else:
                        Iw = TP.IwMaxCap[WP_index]
                        Osa = TP.OaMaxCap[WP_index]
                        Osd = Def_Triplet[2]
                    #objMsg.printMsg("ATI_STE_DBG: Hd   Zn   WP_IDX   WRT_CUR   OVRSHT_AMP   OVRSHT_AMP   WORSE_ATI   DELTA_ATI   WORSE_STE   DELTA_STE   STATUS")
                                     #ATI_STE_DBG:  0   0   0      125       30          14          6.4200       2.4800       8.9000       0.0000        PASS
                     objMsg.printMsg("ATI_STE_DBG: %2d  %3d   %2d        %3d       %2d           %2d          %0.4f       %0.4f       %0.4f       %0.4f       %0.4f        %s" %
                                     (hd, zn, WP_index, Iw, Osa, Osd, meas_data[hd][zn][WP_index]['WorseBER_BASE'], meas_data[hd][zn][WP_index]['WorseBER_ATI'],
                                      meas_data[hd][zn][WP_index]['MaxDelta_ATI'], meas_data[hd][zn][WP_index]['WorseBER_STE'], meas_data[hd][zn][WP_index]['MaxDelta_STE'],
                                      meas_data[hd][zn][WP_index]['STATUS']))
         objMsg.printDblogBin(self.__dut.dblData.Tables('P_TRIPLET_ATI_STE_TEST'), self.__dut.objSeq.getSeq())
      
      # Reset Write Power
      for hd in headRange:
         hd_mask = 0x3FF & (1<<hd) # write to one head at a time
         # Reset Write Power
         if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
            if 'BIT_MASK' in wpcT178_prm:     del wpcT178_prm['BIT_MASK'] 
            if 'BIT_MASK_EXT' in wpcT178_prm: del wpcT178_prm['BIT_MASK_EXT']
            if testSwitch.extern.FE_0270095_504159_SUPPORT_LOOPING_ZONE_T178:   
               wpcT178_prm['ZONE'] = self.__numUserZones - 1 #dont update system zone
               wpcT178_prm['prm_name'] = 'prm_wp_178_0x%04x_%s_%s_%s' % (wpcT178_prm['ZONE'], Def_Triplet[0], Def_Triplet[1], Def_Triplet[2])
               self.setTriplet(wpcT178_prm, Def_Triplet, hd_mask)
            else:
               for zn in test_zones:
                  wpcT178_prm['ZONE'] = zn
                  self.setTriplet(wpcT178_prm, Def_Triplet, hd_mask)
         else: 
            wpcT178_prm.update({'BIT_MASK': (65535L, 65535L), 'BIT_MASK_EXT': (8191L, 65535)})
            self.setTriplet(wpcT178_prm, Def_Triplet, hd_mask)
         
      # update Flash
      self.oProc.St({'test_num':178, 'prm_name':'Save RAP in RAM to FLASH', 'CWORD1':0x220})
      # Dump Data
      #self.oProc.St({'test_num':172,'spc_id': 100, 'prm_name':'dispWorkingAdapts', 'CWORD1':4})
      
      return final_WP_index

   #-------------------------------------------------------------------------------------------------------

   def __measureTripletWPC_PF3(self, headRange, wpc_zn, wrTriplet):
      # TODO: test
      zone_mask_low = 0
      zone_mask_high = 0
      for zone in wpc_zn:
         if zone < 32:
            zone_mask_low |= (1 << zone)
         else:
            zone_mask_high |= (1 << (zone - 32))

      Zone_Mask = self.oUtility.ReturnTestCylWord(zone_mask_low)
      Zone_Mask_Ext = self.oUtility.ReturnTestCylWord(zone_mask_high)


      wpcT251_prm = TP.WPC_OptiPrm_251.copy()
      wpcT250_prm = TP.prm_PrePostOptiAudit_250_2.copy()
      wpcT250_prm.update({'ZONE_MASK': Zone_Mask,'ZONE_MASK_EXT': Zone_Mask_Ext, 'CWORD2' : 5, 'MAX_ERR_RATE': -80, 'MINIMUM': 1})
      wpcT178_prm = TP.WPC_TripletPrm_178.copy()
      wpc_ref = {}
      # set defaults
      for hd in headRange:
         wpc_ref[hd] = {}
         for zn in wpc_zn:
            wpc_ref[hd][zn] = {}
            wpc_ref[hd][zn]['WPC_CAP'] = -1
            wpc_ref[hd][zn]['SLOPE'] = 0
            wpc_ref[hd][zn]['INTERCEPT'] = 0
            wpc_ref[hd][zn]['RSQ'] = 0
            wpc_ref[hd][zn]['RAW'] = {}
            for wpc in range(0,22,2):
               wpc_ref[hd][zn]['RAW'][wpc] = {}
               for wpc_Iw in range(wrTriplet[0],wrTriplet[0] + 5):
                  wpc_ref[hd][zn]['RAW'][wpc][wpc_Iw] = 0

      wpc = 20
      while wpc > 0:
         # Run Tuning
         wpcT251_prm.update({'RESULTS_RETURNED': 0, 'BIT_MASK_EXT': Zone_Mask_Ext, 'BIT_MASK': Zone_Mask, 'REG_TO_OPT1': (0x155, wpc, wpc, -1), })
         self.oProc.St(wpcT251_prm)

         for wpc_Iw in range(wrTriplet[0],wrTriplet[0] + 5):
            # Update Triplet
            wpcT178_prm.update({'BIT_MASK': Zone_Mask, 'BIT_MASK_EXT': Zone_Mask_Ext, 'WRITE_CURRENT': wpc_Iw, 'DURATION': wrTriplet[2], 'DAMPING': wrTriplet[1],})
            self.oProc.St(wpcT178_prm)

            try:
               startIndex = len(self.__dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE'))
            except:
               #No data available
               startIndex = 0
            SetFailSafe()
            self.oProc.St(wpcT250_prm)
            ClearFailSafe()

            try:
               endIndex = len(self.__dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE'))
            except:
               #No data available
               endIndex = startIndex

            if endIndex != startIndex:
               colDict = self.__dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').columnNameDict()
               tableData = self.__dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').rowListIter(index=startIndex)
               for row in tableData:
                  hd = int(tableData[row['HD_LGC_PSN']])
                  zn = int(tableData[row['DATA_ZONE']])
                  sova_ber = float(tableData[row['RAW_ERROR_RATE']])
                  if not wpc_ref.has_key(hd):
                     wpc_ref[hd] = {}
                  if not wpc_ref[hd].has_key(zn):
                     wpc_ref[hd][zn] = {}
                     wpc_ref[hd][zn]['RAW'] = {}
                  if not wpc_ref[hd][zn]['RAW'] .has_key(wpc):
                     wpc_ref[hd][zn]['RAW'] [wpc] = {}
                  wpc_ref[hd][zn]['RAW'][wpc][wpc_Iw] = abs(sova_ber)

         #calculate regression
         fail_locations = 0
         for hd in headRange:
            for zn in wpc_zn:
               BER_data = []
               for wpc_Iw in range(wrTriplet[0],wrTriplet[0] + 5):
                  BER_data.append(wpc_ref[hd][zn]['RAW'][wpc][wpc_Iw])

               # get slope/intercept
               slope, intercept, Rsq = linreg(range(wrTriplet[0],wrTriplet[0] + 5),BER_data)
               intercept = wrTriplet[0] * slope + intercept # get starting iw BER

               if slope < 0.5 and intercept > 1.0:
                  if wpc_ref[hd][zn]['WPC_CAP'] == -1:
                     #update dictionary
                     objMsg.printMsg('WPC_DBG: Hd:%d   Zn:%2d   WP:%s   Wpc_Cap: %d   Ave_Slope:%4f   Ave_Y_Intercept:%4f   Ave_Rsquared:%2f Update '  % (hd,zn,wrTriplet,wpc,slope,intercept,Rsq))
                     wpc_ref[hd][zn]['WPC_CAP'] = wpc
                     wpc_ref[hd][zn]['SLOPE'] = slope
                     wpc_ref[hd][zn]['INTERCEPT'] = intercept
                     wpc_ref[hd][zn]['RSQ'] = Rsq
                  else:
                     objMsg.printMsg('WPC_DBG: Hd:%d   Zn:%2d   WP:%s   Wpc_Cap: %d   Ave_Slope:%4f   Ave_Y_Intercept:%4f   Ave_Rsquared:%2f'  % (hd,zn,wrTriplet,wpc,slope,intercept,Rsq))
               else:
                  objMsg.printMsg('WPC_DBG: Hd:%d   Zn:%2d   WP:%s   Wpc_Cap: %d   Ave_Slope:%4f   Ave_Y_Intercept:%4f   Ave_Rsquared:%2f Fail'  % (hd,zn,wrTriplet,wpc,slope,intercept,Rsq))
                  fail_locations += 1
         if fail_locations == 0:
            break
         wpc = wpc - 2

      return wpc_ref

   #-------------------------------------------------------------------------------------------------------
   def __measureTripletWPC(self, hd, zn, wrTriplet):
      # TODO: test
      prm = self.__prmTripletMeasWPC.copy()
      wc, ovs, ovd = wrTriplet
      bpi = -1
      zHtClr = 0
      prm.update( {'TEST_HEAD': hd, 'ZONE': zn, 'WRITE_CURRENT':wc, 'DAMPING':ovs, 'DURATION':ovd} )

      #measList = array.array('f', []) # array of float types
      measList = {}
      try:
         startIndex = len(self.__dut.dblData.Tables('P211_WPC_SUMMARY'))
      except:
         #No data available
         startIndex = 0

      #For repeatability options loop through the zone measurement TP.VbarNumMeasPerZone times
      # retry loop for measurement exceptions
      cnt = 0; retries = 0; succ = 0
      Wpc_Cap = -1
      slope_Cap = -1
      intercept_Cap = -1
      Rsq_Cap = -1
      while cnt<=retries:
         cnt += 1
         objMsg.printMsg('WPC MEASUREMENT: WP:%s, Hd:%d, Zn:%d, ATTEMPT:%d,' % (wrTriplet, hd, zn, cnt,))

         try:
            self.oProc.St(prm, failSafe=1)
            try:
               endIndex = len(self.__dut.dblData.Tables('P211_WPC_SUMMARY'))
            except:
               #No data available
               endIndex = 0

            if endIndex != startIndex:
               colDict = self.__dut.dblData.Tables('P211_WPC_SUMMARY').columnNameDict()
               tableData = self.__dut.dblData.Tables('P211_WPC_SUMMARY').rowListIter(index=startIndex)
               for row in tableData:
                  Fit_Slope = float(row[colDict['FIT_SLOPE']])
                  Y_Intercept = 7 * Fit_Slope + float(row[colDict['INTERCEPT']])
                  Wpc = int(row[colDict['PRECOMP']])
                  Rsq = float(row[colDict['R_SQUARED']])
                  if not measList.has_key(Wpc):
                     measList[Wpc] ={}
                     measList[Wpc]['Slope'] =[]
                     measList[Wpc]['Intercept'] =[]
                     measList[Wpc]['Rsq'] =[]
                  measList[Wpc]['Slope'].append(Fit_Slope)
                  measList[Wpc]['Intercept'].append(Y_Intercept)
                  measList[Wpc]['Rsq'].append(Rsq)
               Wpc_list = measList.keys()
               Wpc_list.sort(reverse = 1)

               for Wpc in Wpc_list:
                  if len(measList[Wpc]['Slope']) and len(measList[Wpc]['Slope']):
                     ave_slope = sum(measList[Wpc]['Slope']) / len(measList[Wpc]['Slope'])
                     ave_Intercept = sum(measList[Wpc]['Intercept']) / len(measList[Wpc]['Intercept'])
                     ave_Rsq = sum(measList[Wpc]['Rsq']) / len(measList[Wpc]['Rsq'])
                     objMsg.printMsg('WPC_DBG: Hd:%d   Zn:%d   WP:%s   Wpc_Cap: %4f   Ave_Slope:%4f   Ave_Y_Intercept:%4f   Ave_Rsquared:%2f'  % (hd,zn,wrTriplet,Wpc,ave_slope,ave_Intercept,ave_Rsq))
                     if ave_slope < 0.4 and ave_Intercept > 1.0 and Wpc_Cap == -1:
                        Wpc_Cap = Wpc
                        slope_Cap = ave_slope
                        intercept_Cap = ave_Intercept
                        Rsq_Cap = ave_Rsq
                        #break
               if Wpc_Cap == -1: # no selection
                  Wpc_Cap = 1
               objMsg.printMsg('WPC_DBG: Pick Hd:%d   Zn:%d   WP:%s   Wpc_Cap: %4f   Ave_Slope:%4f   Ave_Y_Intercept:%4f    Ave_Rsquared:%2f ' % (hd,zn,wrTriplet,Wpc_Cap,slope_Cap,intercept_Cap,Rsq_Cap))
            else:
               objMsg.printMsg('WPC MEASUREMENT EXCEPTION!! : WP:%s, Hd:%d, Zn:%d' % (wrTriplet, hd, zn))
               objMsg.printMsg('--- POWER CYCLE ---')
               objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1) # power cycle to overcome the measurement (T211) exception

         except ScriptTestFailure, (failureData):
            ec = failureData[0][2]
            objMsg.printMsg(traceback.format_exc())
            objMsg.printMsg('WPC MEASUREMENT EXCEPTION!! : WP:%s, Hd:%d, Zn:%d' % (wrTriplet, hd, zn))
            objMsg.printMsg('--- POWER CYCLE RETRY ---')
            objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1) # power cycle to overcome the measurement (T211) exception
         else:
            succ = 1
            break

      ## fail drive if measurement failed ONLY for Flash LED issues
      if not succ and ec in [11087,11231]:
         objMsg.printMsg("Fail code ec %s" % str(ec))
         raiseException(ec, 'WPC Measurement Failed for Flash_LED issue in self test 211')

      #objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1) # power cycle to overcome the measurement (T211) exception
      return Wpc_Cap,slope_Cap,intercept_Cap, Rsq_Cap
   #-------------------------------------------------------------------------------------------------------
   def __LocateBestArea(self, hd, zn, NPow = 15, Osd = 7, TripletMeasData = {}):
      if testSwitch.FE_348429_0247869_TRIPLET_INTEGRATED_ATISTE:
         Areas = self.Areas
      else:
         Areas = TP.TripletAreas
      MaxSum = -3.0
      BestArea = 'S01'
      sorted_keys = Areas.keys()
      sorted_keys.sort()
      for Area in sorted_keys:
         nSum = 0.0
         for Points in Areas[Area]:
            nTag = 'hd' + str(hd) + 'zn' + str(zn) + 'Iw' + str(Points[0]) + 'Oa' + str(Points[1]) + 'Od' + str(Osd)
            nSum += TripletMeasData[nTag]["ADC"]
         if nSum > MaxSum:
            BestArea = Area
            MaxSum = nSum
         objMsg.printMsg("%s: %0.4f" % (Area,nSum))
      objMsg.printMsg("BestArea :%s" % (BestArea))

      if MaxSum == -3.0:
         return -1, -1, -1

      FilterMeas = {}
      TPIC_Sum = 0
      BPIC_Sum = 0
      iTems = 0
      for Points in Areas[BestArea]:
         nTag = 'hd' + str(hd) + 'zn' + str(zn) + 'Iw' + str(Points[0]) + 'Oa' + str(Points[1]) + 'Od' + str(Osd)
         FilterMeas[nTag] = TripletMeasData[nTag]
         TPIC_Sum += TripletMeasData[nTag]["TPI"]
         BPIC_Sum += TripletMeasData[nTag]["BPI"]
         iTems +=1

      TPIC_Ave = TPIC_Sum / iTems
      BPIC_Ave = BPIC_Sum / iTems
      objMsg.printMsg("TPIC_Ave :%4f  BPIC_Ave:%4f" % (TPIC_Ave,BPIC_Ave))
      return self.__LocateCenterofGravity(hd, zn, TP.NPow, Osd, FilterMeas)

   #-------------------------------------------------------------------------------------------------------
   def __LocateCenterofGravity(self, hd, zn, NPow = 15, Osd = 7, TripletMeasData = {}, nPrint = True):

      nMatrix = {}
      ADCNList = []

      # Display Collected ADC data
      if nPrint:
         objMsg.printMsg('*' * 142)
         objMsg.printMsg("Iw:Oa\t0\t1\t2\t3\t4\t5\t6\t7\t8\t9\t10\t11\t12\t13\t14\t15")
         for row in range(0,16):
            nText = str(row) + ":"
            for col in range(0,16):
               nTag = 'hd' + str(hd) + 'zn' + str(zn) + 'Iw' + str(row) + 'Oa' + str(col) + 'Od' + str(Osd)
               if TripletMeasData.has_key(nTag):
                  nText= nText + "\t" + str(round(TripletMeasData[nTag]["ADC"],4))
               else:
                  nText= nText + "\t0"
            objMsg.printMsg(nText)
         objMsg.printMsg('*' * 142)

      for nTag in TripletMeasData:
         if 'hd' + str(hd) + 'zn' + str(zn) == nTag[:len('hd' + str(hd) + 'zn' + str(zn))]:
            if not nMatrix.has_key(TripletMeasData[nTag]["IW"]):
               nMatrix[TripletMeasData[nTag]["IW"]] = {}
            nMatrix[TripletMeasData[nTag]["IW"]][TripletMeasData[nTag]["OA"]] = pow(TripletMeasData[nTag]["ADC"],NPow)
            ADCNList.append(pow(TripletMeasData[nTag]["ADC"],NPow))

      nSum = sum(ADCNList)

      RowSum = 0
      ColSum = 0
      for nRow in nMatrix:
         for nCol in nMatrix[nRow]:
            nMatrix[nRow][nCol] = nMatrix[nRow][nCol] / nSum
            RowSum += nMatrix[nRow][nCol] * nRow
            ColSum += nMatrix[nRow][nCol] * nCol

      return int(round(RowSum,0)), int(round(ColSum,0)), Osd

   #-------------------------------------------------------------------------------------------------------
   def quadraticMedianfilter(self, dataList):

      finalList = []
      finalList.extend(dataList)
      filterList = []
      filterList.extend(dataList)
      printDbgMsg('finalList1:%s' % finalList)
      #first do 5 point median filter
      for index in range(len(dataList)):
         temparray=[]
         if index == 0:
            filterList[index] = dataList[index]
         elif index == 1:
            temparray.append(dataList[0])
            for index2 in range (1,5):
               temparray.append(dataList[index2])
            temparray.sort()
            filterList[index]=float(temparray[2])
         elif index == (len(dataList) -2):
            for index2 in range(0,4):
               temparray.append(dataList[len(dataList)-index2-2])
            temparray.append(dataList[len(dataList)-1])
            temparray.sort()
            filterList[index]=float(temparray[2])
         elif index == (len(dataList) -1):
            filterList[index] = dataList[index]
         else:
            for index2 in range(0,5):
               temparray.append(dataList[index + index2 - 2])
            temparray.sort()
            filterList[index]=float(temparray[2])
         #now make quadratic equation of filtered values
         N=0
         s1=0
         s2=0
         s3=0
         s4=0
         t1=0
         t2=0
         t3=0
      printDbgMsg('filterList2:%s' % filterList)
      for index in range(len(dataList)):
         N=N+1
         s1=s1+index
         s2=s2+index*index
         s3=s3+index*index*index
         s4=s4+index*index*index*index
         t1=t1+float(filterList[index])
         t2=t2+index*float(filterList[index])
         t3=t3+index*index*float(filterList[index])
      d=N*s2*s4 - N*s3*s3 - s1*s1*s4 - s2*s2*s2 + 2*s1*s2*s3
      A=(N*s2*t3 - N*s3*t2 - s1*s1*t3 - s2*s2*t1 + s1*s2*t2 + s1*s3*t1)/d
      B=(N*s4*t2 - N*s3*t3 - s2*s2*t2 - s1*s4*t1 + s1*s2*t3 + s2*s3*t1)/d
      C=(s1*s3*t3 -s1*s4*t2 -s2*s2*t3 - s3*s3*t1 + s2*s3*t2 + s2*s4*t1)/d
      #apply equation to all values
      for index in range(len(dataList)):
         finalList[index]=A*index*index+B*index+C
      printDbgMsg('finalList2:%s' % finalList)
      return finalList
   #-------------------------------------------------------------------------------------------------------
   def linreg(self, X, Y):
      """
      Summary
         Linear regression of y = ax + b
      Usage
         real, real, real = linreg(list, list)
      Returns coefficients to the regression line "y=ax+b" from x[] and y[], and R^2 Value

      Test data
      X=[1,2,3,4]
      Y=[357.14,53.57,48.78,10.48]
      print linreg(X,Y)
      should be:
      Slope  Y-Int   R
      -104.477   378.685 0.702499064
      """

      if len(X) != len(Y):
         raise ValueError, 'unequal length'
      N = len(X)
      Sx = Sy = Sxx = Syy = Sxy = 0.0
      for x, y in map(None, X, Y):
         Sx = Sx + x
         Sy = Sy + y
         Sxx = Sxx + x*x
         Syy = Syy + y*y
         Sxy = Sxy + x*y
      det = Sxx * N - Sx * Sx

      #print "Sxx= %4.3f  Sx= %4.3f  N= %d  det= %4.3f  Sxy= %4.3f  Sy= %4.3f" % (Sxx,Sx,N,det,Sxy,Sy)

      a, b = (Sxy * N - Sy * Sx)/det, (Sxx * Sy - Sx * Sxy)/det
      meanerror = residual = 0.0
      for x, y in map(None, X, Y):
         meanerror += (y - Sy/N)**2
         residual += (y - a * x - b)**2

      # Protect against all data points having the same value, (divide by zero error)
      if not meanerror == 0.0:
         RR = 1.0 - residual/meanerror
      else:
         RR = 1.0

      #ss = residual / (N-2)
      #Var_a, Var_b = ss * N / det, ss * Sxx / det
      #print "y=ax+b"
      #print "N= %d" % N
      #print "a= %g \\pm t_{%d;\\alpha/2} %g" % (a, N-2, math.sqrt(Var_a))
      #print "b= %g \\pm t_{%d;\\alpha/2} %g" % (b, N-2, math.sqrt(Var_b))
      #print "R^2= %g" % RR
      #print "s^2= %g" % ss
      return a, b, RR
   #-------------------------------------------------------------------------------------------------------
   def getMin_OsaOsd(self, headRange, test_zn, wrTriplet, Osa_max = 15, Osd_max = 15, wpc_slope_limt = 0.5, wpc_intercept_limit = 1.0):
      zone_mask_low = 0
      zone_mask_high = 0
      for zone in test_zn:
         if zone < 32:
            zone_mask_low |= (1 << zone)
         else:
            zone_mask_high |= (1 << (zone - 32))

      Zone_Mask = self.oUtility.ReturnTestCylWord(zone_mask_low)
      Zone_Mask_Ext = self.oUtility.ReturnTestCylWord(zone_mask_high)

      #wpcT251_prm = TP.WPC_OptiPrm_251.copy()
      wpcT250_prm = TP.prm_PrePostOptiAudit_250_2.copy()
      wpcT250_prm.update({'ZONE_MASK': Zone_Mask,'ZONE_MASK_EXT': Zone_Mask_Ext, 'CWORD2' : 5, 'MAX_ERR_RATE': -80, 'MINIMUM': 1})
      wpcT178_prm = TP.WPC_TripletPrm_178.copy()
      # set defaults
      wpc_ref = {}
      # set defaults
      for hd in headRange:
         for zn in test_zn:
            wpc_ref[hd,zn] = {}
            wpc_ref[hd,zn]['OSA_CAP'] = -1

      sweep_step = 2
      while 1:
         for wpc_Iw in range(wrTriplet[0],wrTriplet[0] + 5):
            # Update Triplet
            wpcT178_prm.update({'BIT_MASK': Zone_Mask, 'BIT_MASK_EXT': Zone_Mask_Ext, 'WRITE_CURRENT': wpc_Iw, 'DURATION': wrTriplet[2], 'DAMPING': wrTriplet[1],})
            self.oProc.St(wpcT178_prm)
            try:
               startIndex = len(self.__dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE'))
            except:
               #No data available
               startIndex = 0
            SetFailSafe()
            self.oProc.St(wpcT250_prm)
            ClearFailSafe()

            try:
               endIndex = len(self.__dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE'))
            except:
               #No data available
               endIndex = startIndex

            for err_data in range(startIndex,endIndex):
               hd = int(tableData[err_data]['HD_LGC_PSN'])
               zn = int(tableData[err_data]['DATA_ZONE'])
               sova_ber = float(tableData[err_data]['RAW_ERROR_RATE'])
               if not wpc_ref.has_key((hd,zn,wpc_Iw,wrTriplet[1],wrTriplet[2])):
                  wpc_ref[hd,zn,wpc_Iw,wrTriplet[1],wrTriplet[2]] = {}
               wpc_ref[hd,zn,wpc_Iw,wrTriplet[1],wrTriplet[2]] = abs(sova_ber)

         #calculate regression
         fail_locations = 0
         for hd in headRange:
            for zn in test_zn:
               BER_data = []
               for wpc_Iw in range(wrTriplet[0],wrTriplet[0] + 5):
                  BER_data.append(wpc_ref[hd,zn,wpc_Iw,wrTriplet[1],wrTriplet[2]])

               # get slope/intercept
               slope, intercept, Rsq = linreg(range(wrTriplet[0],wrTriplet[0] + 5),BER_data)
               intercept = wrTriplet[0] * slope + intercept # get starting iw BER

               if slope < wpc_slope_limt and intercept > wpc_intercept_limit:
                  if wpc_ref[hd,zn]['OSA_CAP'] == -1:
                     #update dictionary
                     wpc_ref[hd,zn]['OSA_CAP'] = wrTriplet[1]
                     wpc_ref[hd,zn]['OSD_CAP'] = wrTriplet[2]
                     wpc_ref[hd,zn]['SLOPE'] = slope
                     wpc_ref[hd,zn]['INTERCEPT'] = intercept
                     wpc_ref[hd,zn]['RSQ'] = Rsq
                     objMsg.printMsg('OSAD_DBG: Hd:%d   Zn:%2d   OSA:%2d   OSD: %2d   Ave_Slope:%4f   Ave_Y_Intercept:%4f   Ave_Rsquared:%2f Update '  % (hd,zn,wrTriplet[1],wrTriplet[2],slope,intercept,Rsq))
                  else:
                     objMsg.printMsg('OSAD_DBG: Hd:%d   Zn:%2d   OSA:%2d   OSD: %2d   Ave_Slope:%4f   Ave_Y_Intercept:%4f   Ave_Rsquared:%2f'  % (hd,zn,wrTriplet[1],wrTriplet[2],slope,intercept,Rsq))

               elif ((wrTriplet[1] + sweep_step) > Osa_max or (wrTriplet[2] + sweep_step) > Osd_max): # break if next step exceeds osa/osd limit and still not meet specs
                  if wpc_ref[hd,zn]['OSA_CAP'] == -1: # Update if not been updated
                     wpc_ref[hd,zn]['OSA_CAP'] = wrTriplet[1]
                     wpc_ref[hd,zn]['OSD_CAP'] = wrTriplet[2]
                     wpc_ref[hd,zn]['SLOPE'] = slope
                     wpc_ref[hd,zn]['INTERCEPT'] = intercept
                     wpc_ref[hd,zn]['RSQ'] = Rsq
                     objMsg.printMsg('OSAD_DBG: Hd:%d   Zn:%2d   OSA:%2d   OSD: %2d   Ave_Slope:%4f   Ave_Y_Intercept:%4f   Ave_Rsquared:%2f Update Limit '  % (hd,zn,wrTriplet[1],wrTriplet[2],slope,intercept,Rsq))

               else:
                  objMsg.printMsg('OSAD_DBG: Hd:%d   Zn:%2d   OSA:%2d   OSD: %2d   Ave_Slope:%4f   Ave_Y_Intercept:%4f   Ave_Rsquared:%2f Fail '  % (hd,zn,wrTriplet[1],wrTriplet[2],slope,intercept,Rsq))
                  fail_locations += 1

         if fail_locations == 0: # Break if no more fail location
            break

         wrTriplet[1] += sweep_step
         wrTriplet[2] += sweep_step

      return wpc_ref
   #-------------------------------------------------------------------------------------------------------
   def getHeadWPE_IwMax(self):
      if testSwitch.FE_348429_0247869_TRIPLET_INTEGRATED_ATISTE:
         Hd_EWAC_Data = {}
      try:
         objMsg.printMsg('Get IW Max Adjust based on WPE')
         colDict = self.__dut.dblData.Tables('P069_EWAC_DATA').columnNameDict()
         ewacData = self.__dut.dblData.Tables('P069_EWAC_DATA').rowListIter()
         if testSwitch.FE_348429_0247869_TRIPLET_INTEGRATED_ATISTE:
            Hd_EWAC_Data[Head] = Ewac
         for row in ewacData:
            Head = int(row[colDict['HD_LGC_PSN']])
            Ewac = float(row[colDict['EWAC']])
            if not testSwitch.FE_348429_0247869_TRIPLET_INTEGRATED_ATISTE:
               if testSwitch.ENABLE_MIN_HEAT_RECOVERY == 1 and Head in self.__dut.MaxIwByAFH.keys():
                  objMsg.printMsg('ENABLE_MIN_HEAT_RECOVERY enabled and actived')
                  objMsg.printMsg('Head: %d, MaxIwByAFH:%d' % (Head,self.__dut.MaxIwByAFH[Head]))
                  self.MaxIwAdjust[Head] = min(int(TP.EwacIWSlope * Ewac + TP.EwacIWFactor),15, self.__dut.MaxIwByAFH[Head])
               else:
                  self.MaxIwAdjust[Head] = min(int(TP.EwacIWSlope * Ewac + TP.EwacIWFactor),15)
               self.MaxIwAdjust[Head] = max(self.MaxIwAdjust[Head],2)
      except:
         objMsg.printMsg('Unable to get EWAC DATA')
         pass
      if testSwitch.FE_348429_0247869_TRIPLET_INTEGRATED_ATISTE:
         return Hd_EWAC_Data
         
   #-------------------------------------------------------------------------------------------------------
   def getHeadDibit_IwMin(self):
      try:
         objMsg.printMsg('Get IW Min Adjust based on DIBIT')
         colDict = self.__dut.dblData.Tables('P_MIN_WC_BASED_ON_DIBIT').columnNameDict()
         dibitData = self.__dut.dblData.Tables('P_MIN_WC_BASED_ON_DIBIT').rowListIter()
         for row in dibitData:
            Head = int(row[colDict['HD_LGC_PSN']])
            Zone = int(row[colDict['DATA_ZONE']])
            IwMinDibit = int(row[colDict['MIN_WC']])
            self.MinIwAdjust[Head][Zone] = IwMinDibit

         objMsg.printMsg(self.MinIwAdjust)
         tempMinIwAdjust = {}

         for Head in range(self.numHeads):
            tempMinIwAdjust[Head] = {}
            for Zone in range(self.__numUserZones):
               if not self.MinIwAdjust[Head].has_key(Zone):
                  for index in sorted(self.MinIwAdjust[Head]):
                     IwMinDibit = self.MinIwAdjust[Head][index]
                     tempMinIwAdjust[Head][Zone] = IwMinDibit
                     if index >= Zone:
                        objMsg.printMsg('Head %d Zone %d MinIw %d' % (Head,Zone,tempMinIwAdjust[Head][Zone]))
                        break
               else:
                  tempMinIwAdjust[Head][Zone] = self.MinIwAdjust[Head][Zone]
         self.MinIwAdjust = tempMinIwAdjust.copy()
         objMsg.printMsg(self.MinIwAdjust)

      except:
         objMsg.printMsg('Unable to get DIBIT DATA')
         pass

###########################################################################################################
class CDriveFormat(CPicker):
   def __init__(self, measurements):
      self.dut = objDut
      self.numHeads = self.dut.imaxHead
      self.bpiFile = getVbarGlobalClass(CBpiFile)
      self.numUserZones = self.bpiFile.getNumUserZones()
      self.TPI_STEP_SIZE = 1.0/self.bpiFile.getNominalTracksPerSerpent()
      self.baseformat = [0]*self.numHeads
      self.sendFormatToDrive = True
      self.BpiFileCapacityCalc = False
      self.measurements = measurements
      
      # initialize local data
      data = {
         'BpiCapability'         : ('f',  0.0   ), 
         'TpiCapability'         : ('f',  0.0   ), 
         'BpiFormat'             : ('i',  0     ),
         'TpiFormat'             : ('i',  0     ),
         'AdjustedBpiFormat'     : ('c',  'F'   ), #False
         'AdjustedTpiFormat'     : ('c',  'F'   ), #False
      }
      CVbarDataStore.__init__(self, data)
      self.buildStore(self.numHeads, self.numUserZones)
      
      if verbose:
         objMsg.printMsg('TPIC of measAllZns in CDriveFormat')
      for hd in xrange(self.numHeads):
         for zn in xrange(self.numUserZones):
            pickerData = CVbarDataHelper(self, hd, zn)
            meas = CVbarDataHelper(self.measurements, hd, zn, TP.WPForVBPINominalMeasurements)
            pickerData['BpiCapability']         = meas['BPI']
            pickerData['TpiCapability']         = meas['TPI']
            if verbose:
               objMsg.printMsg("hd %d zn %d tpic %f" % (hd, zn, pickerData['TpiCapability']))

   #-------------------------------------------------------------------------------------------------------
   def getRelativeFreqs(self):
      # Find average scale factor relative to nominal for each format in the BPI file
      relativeFreqs = list(list() for hd in xrange(self.bpiFile.bpiNumHeads))
      for hd in xrange(self.bpiFile.bpiNumHeads):
         for fmt in xrange(self.bpiFile.getMinFormat(),self.bpiFile.getMaxFormat()+1):
            tempSum = 0
            for zn in xrange(self.numUserZones):
               tempSum += self.bpiFile.getFrequencyByFormatAndZone(fmt,zn,hd)/float(self.bpiFile.getFrequencyByFormatAndZone(0,zn,hd))
            relativeFreqs[hd].append(tempSum/self.numUserZones)
      printDbgMsg("BPIFile Relative Frequencies: %s" % relativeFreqs)
      return relativeFreqs

   #-------------------------------------------------------------------------------------------------------
   def getBpiTable(self):
      # Find the BPI format table that is just higher than the desired scale factor
      relativeFreqs = self.getRelativeFreqs()
      for hd in xrange(self.numHeads):
         for zn in xrange(self.numUserZones):
            pickerData = CVbarDataHelper(self, hd, zn)
            fmt_index = bisect.bisect_left(relativeFreqs[getBpiHeadIndex(hd)], pickerData['BpiCapability'])
            if fmt_index == len(relativeFreqs[getBpiHeadIndex(hd)]):
               fmt_index -= 1
            pickerData['BpiFormat'] = fmt_index - self.bpiFile.getNominalFormat()

   #-------------------------------------------------------------------------------------------------------
   def getTpiTable(self):
      # Find the closest TPI table
      nominalTracksPerSerpent = self.bpiFile.getNominalTracksPerSerpent()
      maxTracksPerSerpent = 255 # RAP only caters 1 byte for serpent size.
      for hd in xrange(self.numHeads):
         for zn in xrange(self.numUserZones):
            tpiFormat = int(round((self.getRecord('TpiCapability',hd,zn)-1.0000)/self.TPI_STEP_SIZE))
            tpiFormat = max(tpiFormat,-nominalTracksPerSerpent)
            tpiFormat = min(tpiFormat,maxTracksPerSerpent-nominalTracksPerSerpent)
            self.setRecord('TpiFormat',tpiFormat,hd,zn)

   #-------------------------------------------------------------------------------------------------------
   def getBpiTpiTables(self, metric = 'BOTH'):
      if metric == 'BOTH':
         self.getBpiTable()
         self.getTpiTable()
         return
      if metric == 'BPI':
         self.getBpiTable()
         return
      if metric == 'TPI':
         self.getTpiTable()
         return

   #-------------------------------------------------------------------------------------------------------
   def updateDriveFormat(self, metric = 'BOTH'):
      self.sendFormatToDrive = True
      self.BpiFileCapacityCalc = False
      if metric == 'BOTH':
         self.setFormat('BPI',movezoneboundaries=True)
         self.setFormat('TPI')
         #return
      if metric == 'BPI':
         self.setFormat('BPI',movezoneboundaries=True)
         #return
      if metric == 'TPI':
         self.setFormat('TPI')
         #return
      getVbarGlobalClass(CFSO).saveRAPSAPtoFLASH()

###########################################################################################################
class CTpiMrgnThresScaler:
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, TpiMrgnThresScaleByHdByZn, pickerData = None, TPIMThreshold = -0.07, otfBERThreshold = 6.5):
      self.oProcess = getVbarGlobalClass(CProcess)
      self.dut = objDut

      self.TpiMrgnThresScaleByHdByZn = TpiMrgnThresScaleByHdByZn
      self.pickerData = pickerData
      self.TPIMThreshold = TPIMThreshold
      self.otfBERThreshold = otfBERThreshold
      try:
         self.erasureOtf = self.TpiMrgnThresScaleByHdByZn['OTFE'].copy()
         self.startOtf = self.TpiMrgnThresScaleByHdByZn['OTFS'].copy()
         self.TPMargin = self.TpiMrgnThresScaleByHdByZn['TPIM'].copy()
         self.TPMarginRaw = self.TpiMrgnThresScaleByHdByZn['TPIMR'].copy()
      except:
         self.erasureOtf = {}

      self.TpiMrgnThresScaleByHdByZn['TPIM'] = {}
      self.TpiMrgnThresScaleByHdByZn['TPIMR'] = {}
      self.TpiMrgnThresScaleByHdByZn['OTFE'] = {}
      self.TpiMrgnThresScaleByHdByZn['OTFS'] = {}
      self.testZones = TP.prm_VBAR_ATI_51['ZONES']
      self.testPos = TP.prm_VBAR_ATI_51['ZONEPOS']
      self.numHeads = range(self.dut.imaxHead)

      if testSwitch.VBAR_T51_ITERATION:
         if self.erasureOtf == {}:
            self.vbarAtiMeasurementIter()
         else:
            self.getTpiMrgnThresScaler()

      else:
         self.vbarAtiMeasurement()
         self.getTpiMrgnThresScaler()

   #-------------------------------------------------------------------------------------------------------
   def vbarAtiMeasurementIter(self):
      printDbgMsg("vbarAtiMeasurementIter")

      OffsetDelta = 0.0
      T51MeasData = []
      erasureOtf = {}

      T51Debug = 1
      startErasureOtf = {}
      worsePos  = {}
      T51Iter = {}

      if testSwitch.VBAR_T51_STEP_FOLLOW_SERPENT:
         tpiResolution = 1.0/200 * 100 # # 1/200 * 100 = 0.5
      else:
         tpiResolution = 1.0

      # Set Max Sweep Range align to TPI Margin Threshold in VBAR Nibblets
      try:
         MaxOffsetDelta = (self.objNiblet.settings['TPIMarginThreshold'] * (-1)) + 2 # TPI margin Threshold + 2%
      except:
         MaxOffsetDelta = 10.0

      if T51Debug:
         T51PredictedOffset = {}
         T51FinalOffset = {}

      #=== Delete table
      try:
         self.dut.dblData.Tables('P051_ERASURE_BER').deleteIndexRecords(1)#del file pointers
         self.dut.dblData.delTable('P051_ERASURE_BER')#del RAM objects
      except:
         pass

      tempTpiMrgnThresScaleByHdByZn = {}
      try:
         startIndex = len(self.dut.dblData.Tables('P051_ERASURE_BER'))
      except:
         #No data available
         startIndex = 0

      #=== Init variables
      prm = TP.prm_VBAR_ATI_51['base']
      #=== Run Ati T51
      SetFailSafe()
      for hd in self.numHeads:
         prm['TEST_HEAD'] = hd

         for zn in self.testZones:
            data = CVbarDataHelper(self.pickerData, hd, zn)
            for znpos in self.testPos[zn]:
               prm['ZONE'] = zn
               prm['ZONE_POSITION'] = znpos
               prm['OFFSET'] = 0
               prm['APPLIED_OFFSET'] = 0
               prm['spc_id'] = 1
               prm['CWORD1'] = 0x0040 | testSwitch.USE_ZERO_LATENCY_WRITE_IN_T50_T51
               if testSwitch.FE_0285640_348429_VBAR_ATI_CHECK_FOR_STE:
                  prm['BAND_SIZE'] = 5 # Initial Check include +/-2Tracks
               worstOTFOtherSide = 0.0

               tempTpiMrgnThresScaleByHdByZn[hd,zn,znpos] = 0
               T51Iter[hd,zn,znpos] = 0
               T51PredictedOffset[hd,zn,znpos] = 0
               T51FinalOffset[hd,zn,znpos] = 0

               T51offset = data['TpiFormat']
               # Start with 9 Offset from capability
               try:
                  self.oProcess.St(prm)
                  T51Iter[hd,zn,znpos] += 1
               except:
                  pass

               #Get T51 Data
               if testSwitch.FE_0285640_348429_VBAR_ATI_CHECK_FOR_STE:
                  worstOTF, sideToCheck, otfDirection, endIndex, worseSTE = self.getT51MeasInfo(startIndex, checkSTE = 1)
               else:
                  worstOTF,sideToCheck,otfDirection,endIndex = self.getT51MeasInfo(startIndex)
               objMsg.printMsg("T51_SWEEP: Hd:%2d  Zn%2d  OffsetDelta:%4f  worstOTF:%9.4f" %(hd,zn,OffsetDelta,worstOTF))
               erasureOtf[hd,zn,znpos] = worstOTF
               startErasureOtf[hd,zn,znpos] = worstOTF
               if zn in TP.prm_VBAR_ATI_51['ZONE_FOR_COLLECTION']:
                  startIndex = endIndex
                  continue
               if testSwitch.FE_0268922_504159_VBAR_ATI_ONLY_RELAX_DIR and \
                  worstOTF > self.otfBERThreshold: # stop looping if only to be relaxed
                  startIndex = endIndex
                  objMsg.printMsg("Stop sweeping as zn %d of hd %d zn pos %d worst OTF:%9.4f above threshold %9.4f" % \
                     (zn, hd, znpos, worstOTF, self.otfBERThreshold) )
                  continue
               if testSwitch.FE_0285640_348429_VBAR_ATI_CHECK_FOR_STE and worseSTE < 8.0: # STE Detection
                  startIndex = endIndex
                  objMsg.printMsg("Stop sweeping as zn %d of hd %d zn pos %d worst STE OTF:%9.4f below threshold 8.0db" % \
                     (zn, hd, znpos, worseSTE) )
                  
                  continue
               if worstOTF > 0:
                  if worstOTF > 8.0 and testSwitch.VBAR_T51_ITER_OPTIMIZATION:
                     OffsetDelta = TP.OffsetAdjustDuringVBART51
                     T51Mode = "Predict"
                  else:
                     # Predict the offset where the T51 would achieve otfBERThreshold
                     worstOTF, OffsetDelta = self.getPredictedOffset(hd,zn,worstOTF,tpiResolution, otfDirection)
                     T51Mode = "Course"

                     if T51Debug:
                        T51PredictedOffset[hd,zn,znpos] = OffsetDelta

                  prm['CWORD1'] = 0x0840 | testSwitch.USE_ZERO_LATENCY_WRITE_IN_T50_T51
                  prm['BAND_SIZE'] = 3 # set to 3 prior to iteration
                  while 1:
                     startIndex = endIndex
                     # Normalize the Offset needed based on the set TPI
                     prm['OFFSET'] = int(round(float(OffsetDelta/100.0/float(data['TpiCapability'])*256.0),0)) * sideToCheck
                     prm['APPLIED_OFFSET'] = sideToCheck
                     if not testSwitch.SMR:
                        objMsg.printMsg("VbarNomSerpentWidth: %d" % 200)# TP.VbarNomSerpentWidth) Kent: has to be replaced later
                     if not testSwitch.CM_REDUCTION_REDUCE_PRINTMSG:
                        objMsg.printMsg("TpiFormat: %f" % data['TpiCapability'])
                        objMsg.printMsg("OffsetDelta: %4f" % OffsetDelta)
                        objMsg.printMsg("MaxOffsetDelta: %4f" % MaxOffsetDelta)
                        objMsg.printMsg("Offset: %d" % prm['OFFSET'])
                        objMsg.printMsg("sideToCheck: %d" % sideToCheck)
                        objMsg.printMsg("otfDirection: %s" % otfDirection)
                        objMsg.printMsg("T51Mode: %s" % T51Mode)
                        objMsg.printMsg("worstOTF: %f" % erasureOtf[hd,zn,znpos])

                     try:
                        prm['spc_id'] += 1
                        self.oProcess.St(prm)
                        T51Iter[hd,zn,znpos] += 1
                     except:
                        pass

                     #Get T51 Data
                     worstOTF,sideToCheck,otfDirection,endIndex  = self.getT51MeasInfo(startIndex,sideToCheck,otfDirection)
                     printDbgMsg("T51_SWEEP: Hd:%2d  Zn%2d  OffsetDelta:%4f  worstOTF:%9.4f  T51Mode:%s  sideToCheck:%2d  otfDirection: %s" %(hd,zn,OffsetDelta,worstOTF,T51Mode,sideToCheck,otfDirection))

                     if worstOTF == 0:
                        erasureOtf[hd,zn,znpos] = 0
                        startErasureOtf[hd,zn,znpos] = worstOTF
                        tempTpiMrgnThresScaleByHdByZn[hd,zn,znpos] = TP.Default_TmtScale
                        break

                     elif T51Mode == "Predict": #Do one more round of prediction
                        #Reset Direction
                        otfDirection = "relax"
                        if worstOTF > self.otfBERThreshold: # if worstOTF is better than target OTF, stress towards the worse OTF side
                           otfDirection = "stress"

                        worstOTF, NewOffsetDelta = self.getPredictedOffset(hd,zn,worstOTF,tpiResolution,otfDirection)
                        OffsetDelta += NewOffsetDelta
                        T51Mode = "Course"
                        if T51Debug:
                           T51PredictedOffset[hd,zn,znpos] = OffsetDelta

                     else:
                        if otfDirection == "stress":
                           if worstOTF < self.otfBERThreshold: # Tripped Threshold
                              if T51Mode == "Course":
                                 if abs(OffsetDelta) == tpiResolution:
                                    OffsetDelta -= OffsetDelta

                                    # Check other side
                                    if worstOTFOtherSide == 0.0:
                                       sideToCheck *= -1
                                       prm['OFFSET'] = int(round(float(OffsetDelta/100.0/float(data['TpiCapability'])*256.0),0))*sideToCheck
                                       prm['APPLIED_OFFSET'] = sideToCheck
                                       startIndex = endIndex
                                       try:
                                          prm['spc_id'] += 1
                                          self.oProcess.St(prm)
                                          T51Iter[hd,zn,znpos] += 1
                                       except:
                                          pass
                                       worstOTFOtherSide,sideToCheck,otfDirection,endIndex  = self.getT51MeasInfo(startIndex,sideToCheck,otfDirection)
                                       objMsg.printMsg("worstOTF_OtherSide: %f" % worstOTFOtherSide)
                                       if worstOTFOtherSide < self.otfBERThreshold: # Other Side Tripped Threshold
                                          OffsetDelta -= tpiResolution
                                          otfDirection = "relax"
                                          worstOTF = worstOTFOtherSide
                                          erasureOtf[hd,zn,znpos] = worstOTF
                                       else:
                                          if worstOTFOtherSide < worstOTF:
                                             erasureOtf[hd,zn,znpos] = worstOTFOtherSide
                                          break
                                    else:
                                       break

                                 else:
                                    OffsetDelta -= tpiResolution
                                    otfDirection = "relax"
                              elif T51Mode == "Fine":
                                 OffsetDelta -= tpiResolution
                                 # Check other side
                                 if worstOTFOtherSide == 0.0:
                                    sideToCheck *= -1
                                    prm['OFFSET'] = int(round(float(OffsetDelta/100.0/float(data['TpiCapability'])*256.0),0))*sideToCheck
                                    prm['APPLIED_OFFSET'] = sideToCheck
                                    startIndex = endIndex
                                    try:
                                       prm['spc_id'] += 1
                                       self.oProcess.St(prm)
                                       T51Iter[hd,zn,znpos] += 1
                                    except:
                                       pass
                                    worstOTFOtherSide,sideToCheck,otfDirection,endIndex  = self.getT51MeasInfo(startIndex,sideToCheck,otfDirection)
                                    objMsg.printMsg("worstOTF_OtherSide: %f" % worstOTFOtherSide)
                                    if worstOTFOtherSide < self.otfBERThreshold: # Other Side Tripped Threshold
                                       otfDirection = "relax"
                                       OffsetDelta -= tpiResolution
                                       worstOTF = worstOTFOtherSide
                                       erasureOtf[hd,zn,znpos] = worstOTF
                                    else:
                                       if worstOTFOtherSide < worstOTF:
                                          erasureOtf[hd,zn,znpos] = worstOTFOtherSide
                                       break
                                 else:
                                    break

                           else:                          # Not Tripped Threshold
                              OffsetDelta += tpiResolution
                              if abs(worstOTF - self.otfBERThreshold) > 1.5 and T51Mode == "Course":
                                 OffsetDelta += tpiResolution

                           erasureOtf[hd,zn,znpos] = worstOTF
                        elif otfDirection == "relax":
                           erasureOtf[hd,zn,znpos] = worstOTF
                           if worstOTF > self.otfBERThreshold: # Tripped Threshold
                              if T51Mode == "Course":
                                 if abs(OffsetDelta) == tpiResolution:
                                    # Check other side
                                    if worstOTFOtherSide == 0.0:
                                       sideToCheck *= -1
                                       prm['OFFSET'] = int(round(float(OffsetDelta/100.0/float(data['TpiCapability'])*256.0),0))*sideToCheck
                                       prm['APPLIED_OFFSET'] = sideToCheck
                                       startIndex = endIndex
                                       try:
                                          prm['spc_id'] += 1
                                          self.oProcess.St(prm)
                                          T51Iter[hd,zn,znpos] += 1
                                       except:
                                          pass
                                       worstOTFOtherSide,sideToCheck,otfDirection,endIndex  = self.getT51MeasInfo(startIndex,sideToCheck,otfDirection)
                                       objMsg.printMsg("worstOTF_OtherSide: %f" % worstOTFOtherSide)
                                       if worstOTFOtherSide < self.otfBERThreshold: # Other Side Tripped Threshold
                                          OffsetDelta -= tpiResolution
                                          worstOTF = worstOTFOtherSide
                                          erasureOtf[hd,zn,znpos] = worstOTF
                                       else:
                                          if worstOTFOtherSide < worstOTF:
                                             erasureOtf[hd,zn,znpos] = worstOTFOtherSide
                                          break
                                    else:
                                       break
                                 else:
                                    OffsetDelta += tpiResolution
                                    T51Mode = "Fine"
                                    otfDirection = "stress"
                              elif T51Mode == "Fine":
                                 # Check other side
                                 if worstOTFOtherSide == 0.0:
                                    sideToCheck *= -1
                                    prm['OFFSET'] = int(round(float(OffsetDelta/100.0/float(data['TpiCapability'])*256.0),0))*sideToCheck
                                    prm['APPLIED_OFFSET'] = sideToCheck
                                    startIndex = endIndex
                                    try:
                                       prm['spc_id'] += 1
                                       self.oProcess.St(prm)
                                       T51Iter[hd,zn,znpos] += 1
                                    except:
                                       pass
                                    worstOTFOtherSide,sideToCheck,otfDirection,endIndex  = self.getT51MeasInfo(startIndex,sideToCheck,otfDirection)
                                    objMsg.printMsg("worstOTF_OtherSide: %f" % worstOTFOtherSide)
                                    if worstOTFOtherSide < self.otfBERThreshold: # Other Side Tripped Threshold
                                       OffsetDelta -= tpiResolution
                                       worstOTF = worstOTFOtherSide
                                       erasureOtf[hd,zn,znpos] = worstOTF
                                    else:
                                       if worstOTFOtherSide < worstOTF:
                                          erasureOtf[hd,zn,znpos] = worstOTFOtherSide
                                       break
                                 else:
                                    break
                           else:                          # Not Tripped Threshold
                              OffsetDelta -= tpiResolution
                              if abs(worstOTF - self.otfBERThreshold) > 1.0 and T51Mode == "Course":
                                 OffsetDelta -= tpiResolution

                        T51Mode = "Fine"
                     #erasureOtf[hd,zn] = worstOTF
                     #if abs(worstOTF - otfBERThreshold) > 0.5:
                     #   OffsetDelta += 4
                     #elif abs(worstOTF - otfBERThreshold) > 0.3:
                     #   OffsetDelta += 2
                     #else:
                     #   OffsetDelta += 1

                     #break if not getting any progress
                     if (OffsetDelta > MaxOffsetDelta or OffsetDelta < -20.0)  and (T51Mode != "Course"):
                        objMsg.printMsg('Reached offset Threshold!')
                        break


                  tempTpiMrgnThresScaleByHdByZn[hd,zn,znpos] = float(-1.0 * OffsetDelta/100.0)
                  objMsg.printMsg("Target OTF BER meet Hd:%d   Zn:%d T51_Calls:%d  OffsetDelta: %4f  TPIM %9.4f " % (hd,zn,T51Iter[hd,zn,znpos],OffsetDelta,tempTpiMrgnThresScaleByHdByZn[hd,zn,znpos]))
                  if T51Debug:
                     T51FinalOffset[hd,zn,znpos] = OffsetDelta

               else:
                  erasureOtf[hd,zn,znpos] = 0
                  tempTpiMrgnThresScaleByHdByZn[hd,zn,znpos] = TP.Default_TmtScale

      # Get more positive margin in case more than one measurement position in one Zone
      if not testSwitch.CM_REDUCTION_REDUCE_PRINTMSG:
         objMsg.printMsg('OTF & POSITION')
         objMsg.printMsg('='*78)
         objMsg.printMsg("%2s  %2s  %3s  %9s  %8s  %9s  %8s  %8s  %7s" %("Hd", "Zn", "Pos" ,"START_OTF", "END_OTF", "TPIM", "T51_ITER", "PRED_OFF","ACT_OFF"))
      for hd in self.numHeads:
         for zn in self.testZones:
            if zn in TP.prm_VBAR_ATI_51['ZONE_FOR_COLLECTION']:
               continue
            worsePos[hd,zn] = -1
            for znpos in self.testPos[zn]:
               if worsePos[hd,zn] == -1 or tempMargin < tempTpiMrgnThresScaleByHdByZn[hd,zn,znpos]:
                  tempMargin = tempTpiMrgnThresScaleByHdByZn[hd,zn,znpos]
                  worsePos[hd,zn] = znpos
               printDbgMsg("%2d  %2d  %3d  %9.4f  %8.4f  %9.4f  %8d  %8d  %7d" %(hd, zn, znpos, startErasureOtf[hd,zn,znpos],erasureOtf[hd,zn,znpos], tempTpiMrgnThresScaleByHdByZn[hd,zn,znpos], T51Iter[hd,zn,znpos],T51PredictedOffset[hd,zn,znpos],T51FinalOffset[hd,zn,znpos]))
            tempTpiMrgnThresScaleByHdByZn[hd,zn] = tempMargin
            startErasureOtf[hd,zn] = startErasureOtf[hd,zn,worsePos[hd,zn]]
            erasureOtf[hd,zn] = erasureOtf[hd,zn,worsePos[hd,zn]]
            T51Iter[hd,zn] =  T51Iter[hd,zn,worsePos[hd,zn]]
            T51PredictedOffset[hd,zn] = T51PredictedOffset[hd,zn,worsePos[hd,zn]]
            T51FinalOffset[hd,zn] = T51FinalOffset[hd,zn,worsePos[hd,zn]]
      printDbgMsg('='*78)

      printDbgMsg('='*78)
      for hd in self.numHeads:
         for zn in self.testZones:
            if zn in TP.prm_VBAR_ATI_51['ZONE_FOR_COLLECTION']:
               continue
            for znMap in TP.prm_VBAR_ATI_51['ZONE_MAP'][zn]:
               self.TpiMrgnThresScaleByHdByZn['TPIM'][hd,znMap] = tempTpiMrgnThresScaleByHdByZn[hd,zn] + self.TPIMThreshold
               self.TpiMrgnThresScaleByHdByZn['TPIMR'][hd,znMap] = tempTpiMrgnThresScaleByHdByZn[hd,zn]
               self.TpiMrgnThresScaleByHdByZn['OTFS'][hd,znMap] = startErasureOtf[hd,zn]
               self.TpiMrgnThresScaleByHdByZn['OTFE'][hd,znMap] = erasureOtf[hd,zn]
               #if self.TpiMrgnThresScaleByHdByZn[hd,znMap] < self.TPIMThreshold:
               #   self.TpiMrgnThresScaleByHdByZn[hd,znMap] = self.TPIMThreshold

         printDbgMsg('ZONELUMP')
         printDbgMsg("%2s  %2s  %9s" %("Hd", "Zn", "TPIMF"))
         for zn in range(self.dut.numZones):
            if self.TpiMrgnThresScaleByHdByZn['TPIM'].has_key((hd,zn)):
               printDbgMsg("%2d  %2d  %9.4f" %(hd, zn, self.TpiMrgnThresScaleByHdByZn['TPIM'][hd,zn]))
            else:
               self.TpiMrgnThresScaleByHdByZn['TPIM'][hd,zn] = 0.0

         printDbgMsg('END_ZONELUMP')

         if testSwitch.TPIM_SMOOTH:
            nX1=99
            for zn in self.testZones:
               if nX1 == 99:
                  nY1 = self.TpiMrgnThresScaleByHdByZn['TPIM'][hd,zn]
                  nX1 = zn
               else:
                  nY2 = self.TpiMrgnThresScaleByHdByZn['TPIM'][hd,zn]
                  nX2 = zn
                  nStep = float(float(nY2 - nY1) / float(nX2 - nX1))

                  objMsg.printMsg("nStep %0.4f" %nStep)
                  for yZone in range(nX1,nX2+1):
                     self.TpiMrgnThresScaleByHdByZn['TPIM'][hd,yZone] = (round(nY1 + float(nStep * (yZone - nX1)),2))
                  nX1 = nX2
                  nY1 = nY2
            #objMsg.printMsg('LINEAR_POLATE')
            #objMsg.printMsg("%2s  %2s  %9s" %("Hd", "Zn", "TPIMF"))
            #for zn in range(self.dut.numZones):
            #   objMsg.printMsg("%2d  %2d  %9.4f" %(hd, zn, self.TpiMrgnThresScaleByHdByZn['TPIM'][hd,zn]))
            #objMsg.printMsg('END_LINEAR_POLATE')

            dataList = []
            for zn in range(self.dut.numZones):
               dataList.append(self.TpiMrgnThresScaleByHdByZn['TPIM'][hd,zn])
            filteredList = self.quadraticMedianfilter(dataList)
            objMsg.printMsg('QUAD_POLATE')
            objMsg.printMsg("%2s  %2s  %9s" %("Hd", "Zn", "TPIMF"))
            for zn in range(self.dut.numZones):
               self.TpiMrgnThresScaleByHdByZn['TPIM'][hd,zn] = filteredList[zn]
               objMsg.printMsg("%2d  %2d  %9.4f" %(hd, zn, self.TpiMrgnThresScaleByHdByZn['TPIM'][hd, zn]))
            objMsg.printMsg('END_QUAD_POLATE')
      if not testSwitch.CM_REDUCTION_REDUCE_PRINTMSG:
         objMsg.printMsg('OTF & TMTSCALE')
         objMsg.printMsg('='*78)
         if T51Debug:
            objMsg.printMsg("%2s  %2s  %9s  %8s  %9s  %9s  %8s  %8s  %8s  %8s" %("Hd", "Zn", "START_OTF", "END_OTF", "TPIM", "TPIMF", "T51_ITER", "PRED_OFF","ACT_OFF","WORSEPOS"))
         else:
            objMsg.printMsg("%2s  %2s  %9s  %8s  %9s  %8s" %("Hd", "Zn", "START_OTF", "END_OTF", "TPIM", "T51_ITER"))
         for hd in self.numHeads:
            for zn in self.testZones:
               if zn in TP.prm_VBAR_ATI_51['ZONE_FOR_COLLECTION']:
                  continue
            #=== Print table content: OTF & TMTSCALE
               objMsg.printMsg("%2d  %2d  %9.4f  %8.4f  %9.4f  %9.4f  %8d  %8d  %7d  %7d" \
                  %(hd, zn, startErasureOtf[hd,zn],erasureOtf[hd,zn], tempTpiMrgnThresScaleByHdByZn[hd,zn], self.TpiMrgnThresScaleByHdByZn['TPIM'][hd,zn], T51Iter[hd,zn],T51PredictedOffset[hd,zn],T51FinalOffset[hd,zn], worsePos[hd,zn]))

      ClearFailSafe()
   #-------------------------------------------------------------------------------------------------------
   def getPredictedOffset(self,hd,zn,worstOTF,tpiResolution, otfDirection):
      T51slope = 0.15
      T51factor = 0.55
      T51StepFactor = 0.85
      OffsetDelta = 0.0
      if otfDirection == "stress":
         objMsg.printMsg("Above Limit")
         while 1:
            deltaOTF = (worstOTF * T51slope - T51factor) * T51StepFactor
            objMsg.printMsg("%2d  %2d  %9.4f  %9.4f" % (hd, zn, worstOTF, deltaOTF))
            worstOTF -= deltaOTF
            if worstOTF < self.otfBERThreshold:
               if OffsetDelta == 0: OffsetDelta = tpiResolution
               break
            OffsetDelta += tpiResolution
      elif otfDirection == "relax":
         objMsg.printMsg("Below Limit")
         while 1:
            otfn = ((1/T51StepFactor * worstOTF) - T51factor) / ((1/T51StepFactor) - T51slope)
            deltaOTF = otfn - worstOTF
            objMsg.printMsg("%2d  %2d  %9.4f  %9.4f" % (hd, zn, otfn, deltaOTF))
            OffsetDelta -= tpiResolution
            if otfn >= self.otfBERThreshold:
               if OffsetDelta == 0: OffsetDelta = -(tpiResolution)
               break
            worstOTF = otfn
      return worstOTF, OffsetDelta
   #-------------------------------------------------------------------------------------------------------
   def getT51MeasInfo(self, startIndex, sideToCheck=0, otfDirection="", checkSTE = 0):
      if checkSTE:
         worseSTE = 11.0
      worstOTF =0
      TestType_Str = 'erasure'

      try:
         endIndex = len(self.dut.dblData.Tables('P051_ERASURE_BER'))
      except:
         #No data available
         endIndex = 0

      if testSwitch.virtualRun:
         startIndex = 0
         objMsg.printMsg("startIndex=%d endIndex=%d" %(startIndex,endIndex))

      if endIndex != startIndex:
         colDict = self.dut.dblData.Tables('P051_ERASURE_BER').columnNameDict()
         T51MeasData = self.dut.dblData.Tables('P051_ERASURE_BER').rowListIter(index=startIndex)
         try:
            for row in T51MeasData:
               if row[colDict['TEST_TYPE']] == TestType_Str:
                   if row[colDict['TRK_INDEX']] == "-1":
                      OTFBERTrackIndex_m1 = float(row[colDict['RRAW_BER']])
                      NumOfERrorsTrackIndex_m1 = (int(row[colDict['HARD_ERR_CNT']])*300) + (int(row[colDict['ONE_PLUS_RTY_CNT']])*200) + (int(row[colDict['SIX_PLUS_RTY_CNT']])*100) + int(row[colDict['ONE_PLUS_ECC_CNT']])
                      try:
                         SOVABERTrackIndex_m1 = float(row[colDict['BITS_IN_ERROR_BER']])
                      except:
                         SOVABERTrackIndex_m1 = 0
                   elif row[colDict['TRK_INDEX']] == "1":
                     OTFBERTrackIndex_p1 = float(row[colDict['RRAW_BER']])
                     NumOfERrorsTrackIndex_p1 = (int(row[colDict['HARD_ERR_CNT']])*300) + (int(row[colDict['ONE_PLUS_RTY_CNT']])*200) + (int(row[colDict['SIX_PLUS_RTY_CNT']])*100) + int(row[colDict['ONE_PLUS_ECC_CNT']])
                     try:
                        SOVABERTrackIndex_p1 = float(row[colDict['BITS_IN_ERROR_BER']])
                     except:
                        SOVABERTrackIndex_p1 = 0
                   elif checkSTE: # check for STE
                     worseSTE = min(worseSTE, float(row[colDict['RRAW_BER']]))
             
            zn = int(row[colDict['DATA_ZONE']])
            if sideToCheck == -1: # if check only one side:
               worstOTF = OTFBERTrackIndex_m1
               #worstSova = SOVABERTrackIndex_m1
            elif sideToCheck == 1:
               worstOTF = OTFBERTrackIndex_p1
               #worstSova = SOVABERTrackIndex_p1
            else:
               worstOTF = min(OTFBERTrackIndex_m1,OTFBERTrackIndex_p1)
               sideToCheck = 1
               
               if (SOVABERTrackIndex_m1 < SOVABERTrackIndex_p1) and (NumOfERrorsTrackIndex_m1 > NumOfERrorsTrackIndex_p1): # if ID Track is worse, offset towards OD
                  sideToCheck = -1
               if (SOVABERTrackIndex_m1 < SOVABERTrackIndex_p1) and abs(SOVABERTrackIndex_m1 - SOVABERTrackIndex_p1) > 0.02: # if ID Track is worse, offset towards OD
                  sideToCheck = -1
               if (SOVABERTrackIndex_m1 > SOVABERTrackIndex_p1) and abs(SOVABERTrackIndex_m1 - SOVABERTrackIndex_p1) > 0.02: # if OD Track is worse, offset towards ID
                  sideToCheck = 1
               elif zn > TP.MD_Data_Zn_Before_Sys_Zn: # if offset towards OD by default
                  sideToCheck = -1

               otfDirection = "relax"
               if worstOTF > self.otfBERThreshold: # if worstOTF is better than target OTF, stress towards the worse OTF side
                  otfDirection = "stress"
                   
            if testSwitch.virtualRun:
               objMsg.printMsg("worstOTF=%d sideToCheck=%d otfDirection=%s endIndex=%d" % (worstOTF,sideToCheck,otfDirection,endIndex))

         except: pass

      else:
        objMsg.printMsg("startIndex=%d endIndex=%d" %(startIndex,endIndex))
        objMsg.printMsg("worstOTF=%d sideToCheck=%d otfDirection=%s endIndex=%d" % (worstOTF,sideToCheck,otfDirection,endIndex))
      if checkSTE:
         return worstOTF, sideToCheck, otfDirection, endIndex, worseSTE
      else:
         return worstOTF,sideToCheck,otfDirection,endIndex

   #-------------------------------------------------------------------------------------------------------

   def vbarAtiMeasurement(self):
      #=== Delete table
      try:
         self.dut.dblData.Tables('P051_ERASURE_BER').deleteIndexRecords(1)#del file pointers
         self.dut.dblData.delTable('P051_ERASURE_BER')#del RAM objects
      except:
         pass

      #=== Init variables
      prm = TP.prm_VBAR_ATI_51['base']

      #=== Run Ati T51
      SetFailSafe()
      for hd in self.numHeads:
         prm['TEST_HEAD'] = hd
         for zn in self.testZones:
            prm['ZONE'] = zn
            try:
               self.oProcess.St(prm)
            except:
               pass
      ClearFailSafe()
   #-------------------------------------------------------------------------------------------------------
   def getTpiMrgnThresScaler(self):
      startOtf = {}
      if self.erasureOtf == {}:
         #=== Retrieve OTFs from table
         try:
            colDict = self.__dut.dblData.Tables('P051_ERASURE_BER').columnNameDict()
            table = self.__dut.dblData.Tables('P051_ERASURE_BER').rowListIter()
         except:
            objMsg.printMsg("Unable to retrieve P051_ERASURE_BER")
            return

         #=== erasureOtf[hd,zn]
         temperasureOtf = {}
         for row in table:
            if 'erasure' in row[colDict['TEST_TYPE']]:
               hdzn = int(row[colDict['HD_LGC_PSN']]), int(row[colDict['DATA_ZONE']])
               if row[colDict['RRAW_BER']] != '-inf':
                  temperasureOtf.setdefault(hdzn,[]).append(float(row[colDict['RRAW_BER']]))

         for hd in self.numHeads:
            for zn in self.testZones:
               try:
                  erasureOtf[hd,zn] = min(erasureOtf[hd,zn])
               except:
                  erasureOtf[hd,zn] = 0.0
      else:
         erasureOtf = self.erasureOtf.copy()
         startOtf = self.startOtf.copy()

      #=== tempTpiMrgnThresScaler[hd,zn]
      tempTpiMrgnThresScaleByHdByZn = {}

      if testSwitch.VBAR_TPIM_SLOPE_CAL:
         objMsg.printMsg('OTF and DELTAOTF')
         objMsg.printMsg('='*58)
         if (startOtf != {}):
            objMsg.printMsg("%2s  %2s  %9s  %9s  %9s  %9s" %("Hd", "Zn", "START_OTF", "END_OTF", "TPIM", "TPIM2"))
         else:
            objMsg.printMsg("%2s  %2s  %9s  %9s" %("Hd", "Zn", "OTF", "DELTAOTF"))
         T51slope = 0.15
         T51factor = 0.55
         T51StepFactor = 0.85

      for hd in self.numHeads:
         for zn in self.testZones:
            if (startOtf != {}):
               if (startOtf[hd,zn] != erasureOtf[hd,zn]):
                  tempTpiMrgnThresScaleByHdByZn[hd,zn] = ( erasureOtf[hd,zn] - self.otfBERThreshold ) *  ( self.TPMarginRaw[hd,zn] / (startOtf[hd,zn] - erasureOtf[hd,zn]))
                  if tempTpiMrgnThresScaleByHdByZn[hd,zn] < 0:
                     tempTpiMrgnThresScaleByHdByZn[hd,zn] = max(tempTpiMrgnThresScaleByHdByZn[hd,zn],-0.04)
                  elif tempTpiMrgnThresScaleByHdByZn[hd,zn] > 0:
                     tempTpiMrgnThresScaleByHdByZn[hd,zn] = min(tempTpiMrgnThresScaleByHdByZn[hd,zn],0.04)
               else:
                  tempTpiMrgnThresScaleByHdByZn[hd,zn] = 0
               objMsg.printMsg("%2d  %2d  %9.4f  %9.4f  %9.4f  %9.4f" % (hd, zn, startOtf[hd,zn], erasureOtf[hd,zn], self.TPMarginRaw[hd,zn],tempTpiMrgnThresScaleByHdByZn[hd,zn]))
            else:
               tempTpiMrgnThresScaleByHdByZn[hd,zn] = 0
               try:
                  otf = erasureOtf[hd,zn]
                  if testSwitch.VBAR_TPIM_SLOPE_CAL:
                     if otf >= self.otfBERThreshold:
                        objMsg.printMsg("Above Limit")
                        while 1:
                           deltaOTF = (otf * T51slope - T51factor) * T51StepFactor
                           objMsg.printMsg("%2d  %2d  %9.4f  %9.4f" % (hd, zn, otf, deltaOTF))
                           otf -= deltaOTF
                           if otf < self.otfBERThreshold:
                              break
                           tempTpiMrgnThresScaleByHdByZn[hd,zn] -= 0.01
                     elif otf < self.otfBERThreshold:
                        objMsg.printMsg("Below Limit")
                        while 1:
                           otfn = (((1/T51StepFactor) * otf) - T51factor) / ((1/T51StepFactor) - T51slope)
                           deltaOTF = otfn - otf
                           objMsg.printMsg("%2d  %2d  %9.4f  %9.4f" % (hd, zn, otfn, deltaOTF))
                           tempTpiMrgnThresScaleByHdByZn[hd,zn] += 0.01
                           if otfn >= self.otfBERThreshold:
                              break
                           otf = otfn
                  else:
                     tempTpiMrgnThresScaleByHdByZn[hd,zn] = self.TpiMrgnThresScaler(otf)

               except:
                  otf = 0.0
                  erasureOtf[hd,zn] = 0.0
                  tempTpiMrgnThresScaleByHdByZn[hd,zn] = TP.Default_TmtScale
      #=== self.TpiMrgnThresScaler[hd,zn]
      for hd in self.numHeads:
         for zn in self.testZones:
            for znMap in TP.prm_VBAR_ATI_51['ZONE_MAP'][zn]:
               self.TpiMrgnThresScaleByHdByZn['TPIM'][hd,znMap] = tempTpiMrgnThresScaleByHdByZn[hd,zn]
               self.TpiMrgnThresScaleByHdByZn['OTFE'][hd,znMap] = erasureOtf[hd,zn]

         if testSwitch.TPIM_SMOOTH:
            nX1=99
            for zn in self.testZones:
               if nX1 == 99:
                  nY1 = self.TpiMrgnThresScaleByHdByZn['TPIM'][hd,zn]
                  nX1 = zn
               else:
                  nY2 = self.TpiMrgnThresScaleByHdByZn['TPIM'][hd,zn]
                  nX2 = zn
                  nStep = float(float(nY2 - nY1) / float(nX2 - nX1))

                  objMsg.printMsg("nStep %0.4f" %nStep)
                  for yZone in range(nX1,nX2+1):
                     self.TpiMrgnThresScaleByHdByZn['TPIM'][hd,yZone] = (round(nY1 + float(nStep * (yZone - nX1)),2))
                  nX1 = nX2
                  nY1 = nY2

            #objMsg.printMsg('LINEAR_POLATE')
            #objMsg.printMsg("%2s  %2s  %9s" %("Hd", "Zn", "TPIMF"))
            #for zn in range(self.dut.numZones):
            #   objMsg.printMsg("%2d  %2d  %9.4f" %(hd, zn, self.TpiMrgnThresScaleByHdByZn['TPIM'][hd,zn]))
            #objMsg.printMsg('END_LINEAR_POLATE')

            dataList = []
            for zn in range(self.dut.numZones):
               dataList.append(self.TpiMrgnThresScaleByHdByZn['TPIM'][hd,zn])
            filteredList = self.quadraticMedianfilter(dataList)
            objMsg.printMsg('QUAD_POLATE')
            objMsg.printMsg("%2s  %2s  %9s" %("Hd", "Zn", "TPIMF"))
            for zn in range(self.dut.numZones):
               self.TpiMrgnThresScaleByHdByZn['TPIM'][hd,zn] = filteredList[zn]
               objMsg.printMsg("%2d  %2d  %9.4f" %(hd, zn, self.TpiMrgnThresScaleByHdByZn['TPIM'][hd, zn]))
            objMsg.printMsg('END_QUAD_POLATE')

      #=== Print table header: OTF & TMTSCALE
      objMsg.printMsg('OTF & TMTSCALE')
      objMsg.printMsg('='*58)
      objMsg.printMsg("%2s  %2s  %9s  %9s" %("Hd", "Zn", "OTF", "TMTSCALE"))
      objMsg.printMsg('='*58)
      for hd in self.numHeads:
         for zn in self.testZones:
            #=== Print table content: OTF & TMTSCALE
            objMsg.printMsg("%2d  %2d  %9.4f  %9.4f" %(hd, zn, erasureOtf[hd,zn], tempTpiMrgnThresScaleByHdByZn[hd,zn]))

   #-------------------------------------------------------------------------------------------------------
   def TpiMrgnThresScaler (self, otf):
   	for scaler in TP.Otf_TmtScaler:
   		if scaler['OtfBerLowerLimit'] < otf <= scaler['OtfBerUpperLimit']:
   			return scaler['TmtScaler']

   #-------------------------------------------------------------------------------------------------------
   def quadraticMedianfilter(self, dataList):

      finalList = []
      finalList.extend(dataList)
      filterList = []
      filterList.extend(dataList)
      objMsg.printMsg('finalList1:%s' % finalList)
      #first do 5 point median filter
      for index in range(len(dataList)):
         temparray=[]
         if index == 0:
            filterList[index] = dataList[index]
         elif index == 1:
            temparray.append(dataList[0])
            for index2 in range (1,5):
               temparray.append(dataList[index2])
            temparray.sort()
            filterList[index]=float(temparray[2])
         elif index == (len(dataList) -2):
            for index2 in range(0,4):
               temparray.append(dataList[len(dataList)-index2-2])
            temparray.append(dataList[len(dataList)-1])
            temparray.sort()
            filterList[index]=float(temparray[2])
         elif index == (len(dataList) -1):
            filterList[index] = dataList[index]
         else:
            for index2 in range(0,5):
               temparray.append(dataList[index + index2 - 2])
            temparray.sort()
            filterList[index]=float(temparray[2])
         #now make quadratic equation of filtered values
         N=0
         s1=0
         s2=0
         s3=0
         s4=0
         t1=0
         t2=0
         t3=0
      objMsg.printMsg('filterList2:%s' % filterList)
      for index in range(len(dataList)):
         N=N+1
         s1=s1+index
         s2=s2+index*index
         s3=s3+index*index*index
         s4=s4+index*index*index*index
         t1=t1+float(filterList[index])
         t2=t2+index*float(filterList[index])
         t3=t3+index*index*float(filterList[index])
      d=N*s2*s4 - N*s3*s3 - s1*s1*s4 - s2*s2*s2 + 2*s1*s2*s3
      A=(N*s2*t3 - N*s3*t2 - s1*s1*t3 - s2*s2*t1 + s1*s2*t2 + s1*s3*t1)/d
      B=(N*s4*t2 - N*s3*t3 - s2*s2*t2 - s1*s4*t1 + s1*s2*t3 + s2*s3*t1)/d
      C=(s1*s3*t3 -s1*s4*t2 -s2*s2*t3 - s3*s3*t1 + s2*s3*t2 + s2*s4*t1)/d
      #apply equation to all values
      for index in range(len(dataList)):
         finalList[index]=A*index*index+B*index+C
      objMsg.printMsg('finalList2:%s' % finalList)
      return finalList


class CFormat2File(CProcess):
   """
   Class to create and use a SIM file which holds RAW values from READ_SCRN2
   test and later use for TCC Cal using BER.
   """

   def __init__(self):
      """
      @param prm186: T186 input to measure and return head mr resistances
      @param deltaLim: Integer. Absolute value of maximum allowed MR resistance change
      """
      self.oFSO = getVbarGlobalClass(CFSO)
      self.VBARFormat_Path = os.path.join(getSystemPCPath(), self.pcFileName, self.oFSO.getFofFileName(0))
      self.genericVBARFormatPath = os.path.join(getSystemResultsPath(), self.oFSO.getFofFileName(0), self.genVBARFmtName)
      # init super
      CProcess.__init__(self)

   def Save_VBAR_Format(self, array = []):
      if array != []:
          self.arrayToFile(array)
      else:
         self.arrayToFile(self.Gather_VBAR_Format())
      self.fileToDisc()

   def Retrieve_VBAR_Format(self, Flag = False):
      # Get the original values
      ogPcPath = self.SimToPcFile()
      file = open(ogPcPath,'r')
      Array_VBARFormt = array('f', file.read())
      List_VBARFormat = Array_VBARFormt.tolist()

      iMaxHead = self.dut.imaxHead
      numofzone = self.dut.numZones
      for head in range(iMaxHead):
         for izone in range(numofzone):
            myFmtB = List_VBARFormat[(head*numofzone)*2 + izone*2]
            myFmtT = List_VBARFormat[(head*numofzone)*2 + izone*2 + 1]
            objMsg.printMsg("H[%d] Zn[%d] BPIT%4.2f BPIT%4.2f" % (head, izone, myFmtB, myFmtT))

      return List_VBARFormat

   def Gather_VBAR_Format(self):
      """
      Gather MR values from P186_BIAS_CAL table and return as an array object.
      """
      # TODO: test
      colDict = self.__dut.dblData.Tables('P_VBAR_FORMAT_SUMMARY').columnNameDict()
      RawTable = self.__dut.dblData.Tables('P_VBAR_FORMAT_SUMMARY').rowListIter({colDict['SPC_ID']:'2'})
      iMaxHead = self.dut.imaxHead
      numofzone = self.dut.numZones

      # Create an empty table and fill in with actual VBAR format
      tmp_List = [0,]*iMaxHead*numofzone

      for row in RawTable:
         if row[colDictp['ERROR_RATE_TYPE']].strip() != 'SECTOR': continue
         myHead = int(row[colDict['HD_LGC_PSN']])
         myZone = int(row[colDict['DATA_ZONE']])
         myTrack = int(row[colDict['START_TRK_NUM']])
         myRRAW = float(row[colDict['RAW_ERROR_RATE']])
         tmp_List[myHead*numofzone+myZone] = myRRAW
         objMsg.printMsg("H[%d] Zn[%d] Trk[%d] RRAW=%4.2f" % (myHead, myZone, myTrack, myRRAW))

      tmp_Array = array('f', tmp_List)

      return tmp_Array

   def SimToPcFile(self):
      """
      Pull the MR resitance SIM file and place it in a pcfile.  Return the path
      to the pcfile.
      """
      from SIM_FSO import objSimArea
      record = objSimArea['VBAR_FORMAT0']  #CCCYYY
      if not testSwitch.virtualRun:
         path = self.oFSO.retrieveHDResultsFile(record)
      else:
         path = os.path.join('.', self.genericVBARFormatPath)
      return path

   def arrayToFile(self, array1):
      """
      Write the array object to the pcfile
      """
      VBARformatFile = GenericResultsFile(self.genVBARFmtName)
      VBARformatFile.open('w')
      arStr = array1.tostring()  # GenericResultsFile won't work with arrays, so we have to output to a string instead
      VBARformatFile.write(arStr)
      VBARformatFile.close()

   def fileToDisc(self):
      """
      Write the file containing  values to disc, using test 231.
      """
      from SIM_FSO import objSimArea
      record = objSimArea['VBAR_FORMAT0'] #CCCYYY Debug

      # First, look for the generic results file that is created in MDW cals.  If
      #  that is not there, assume that we have a pcfile that can be written to disc
      if os.path.exists(self.genericVBARFormatPath):
         filePath = self.genericVBARFormatPath
      elif os.path.exists(self.VBARFormat_Path):
         filePath = self.VBARFormat_Path
      else:
         raiseException(11044, "VBAR FORMAT File does not exist")

      #Write data to drive SIM
      objMsg.printMsg("Saving VBAR Format File to drive SIM.  File Path: %s" % filePath, objMsg.CMessLvl.DEBUG)
      self.oFSO.saveResultsFileToDrive(1, filePath, 0, record, 1)

      #Verify data on drive SIM
      if not testSwitch.virtualRun:
         path = self.oFSO.retrieveHDResultsFile(record)
         file = open(path,'rb')
         try:
            file.seek(0,2)  # Seek to the end
            fileLength = file.tell()
         finally:
            file.close()
         objMsg.printMsg("Re-Read of drive SIM File %s had size %d" % (record.name,fileLength), objMsg.CMessLvl.DEBUG)
         if fileLength == 0:
            raiseException(11044, "VBAR FORMAT SIM readback of 0 size.")

class CFormat2File1(CFormat2File):
   def __init__(self):
      self.pcFileName = 'vfmt0'
      self.genVBARFmtName = 'vfmt0'
      # init super
      CFormat2File.__init__(self)

class CFormat2File2(CFormat2File):
   def __init__(self):
      self.pcFileName = 'vfmt1'
      self.genVBARFmtName = 'vfmt1'
      # init super
      CFormat2File.__init__(self)

###########################################################################################################
class CWaterfallTest(CState):

   def __init__(self, dut, params={}):
      self.dut = dut
      self.params = params
      depList = ['AFH1']
      CState.__init__(self, dut, depList)

      # Initialize the SPC_ID
      getVbarGlobalClass(CSpcIdHelper, {'dut':self.dut}).getSetIncrSpcId('P_VBAR_FORMAT_SUMMARY', startSpcId = 0, increment = 0, useOpOffset = 1)

   def run(self):

      self.dut.pn_backup = self.dut.driveattr['PART_NUM']
      printDbgMsg("CWaterfallTest: Begin with part number %s " %self.dut.pn_backup )
      self.buildClusterList()

      if self.dut.currentState in ['HMSC_DATA']:
         try:
            hms_table_start = len(self.dut.dblData.Tables('P_VBAR_HMS_ADJUST'))
         except: 
            hms_table_start = 0
      #
      if self.params.get('ENABLE_ZAP', 1):
         if testSwitch.FE_SGP_OPTIZAP_ADDED: #turn on the ZAP
            from Servo import CServoOpti
            printDbgMsg("Waterfall: Tuning on ZAP")
            oSrvOpti = CServoOpti()
            if testSwitch.ENABLE_T175_ZAP_CONTROL:
               oSrvOpti.St(TP.zapPrm_175_zapOn)
            else:
               oSrvOpti.St(TP.setZapOnPrm_011)
               oSrvOpti.St({'test_num':178, 'prm_name':'Save SAP in RAM to FLASH', 'CWORD1':0x420})

      # call vbar from here
      if not testSwitch.CM_REDUCTION_REDUCE_PRINTMSG:
         objMsg.printMsg("calling vbar")
         for niblet in self.VbarNibletCluster:
            objMsg.printMsg("local vbar cluster: %s " % str(niblet))

      if verbose: #cut logs
         for niblet in TP.VbarNibletCluster:
            objMsg.printMsg(getVbarGlobalClass(CUtility).convertDictToPrintStr(niblet,'global vbar cluster',False,False))

      for i in xrange(len(TP.VbarPartNumCluster)):
         if TP.VbarPartNumCluster[i] == '': break
         objMsg.printMsg("TP.VbarPartNumCluster[%d]: %s " %(i, TP.VbarPartNumCluster[i]))

      oVbarTuning = CVbarTuning(self.dut,self.params)
      nibletIndex, vbarResult = oVbarTuning.run()
      
      if not self.params.get('NO_DISABLE_ZAP', 0):
         from Servo import CServoOpti
         printDbgMsg("Waterfall: Tuning off ZAP upon exiting")
         oSrvOpti = CServoOpti()
         if testSwitch.ENABLE_T175_ZAP_CONTROL:
            oSrvOpti.St(TP.zapPrm_175_zapOff)
         else:
            oSrvOpti.St(TP.setZapOffPrm_011)
            if not testSwitch.BF_0119055_231166_USE_SVO_CMD_ZAP_CTRL:
               oSrvOpti.St({'test_num':178, 'prm_name':'Save SAP in RAM to FLASH', 'CWORD1':0x420})
      
      if self.params.get('HANDLE_WTF_EXT', 1) and \
         self.dut.currentState not in ['HMSC_DATA']:
         # Display vbar result
         self.keyCounter, self.nibletString = self.VbarNibletCluster[nibletIndex]

         objMsg.printMsg("From_Vbar")
         objMsg.printMsg("EC        : %s  nibletIndex: %s" % (vbarResult, nibletIndex))
         objMsg.printMsg("keyCounter: %s  nibletString: %s" % (self.keyCounter, self.nibletString))

         #update partnumber and WTF attributes
         self.updateWTF(vbarResult == 12169)

         self.updateATTR(self.partNum,self.keyCounter)

         if vbarResult == 0:
            # Update family info in the drive
            hdCount = TP.VbarNibletCluster[nibletIndex]['NUM_HEADS']
            getVbarGlobalClass(CFSO).setFamilyInfo(TP.familyInfo,TP.famUpdatePrm_178, forceHdCount=hdCount)
            objMsg.printMsg("Waterfall vbar passed, exit")
            self.dut.VbarDone = 1   # for depop use

            if testSwitch.FE_SGP_EN_REPORT_WTF_FAILURE and ((self.dut.pn_backup != self.dut.driveattr['PART_NUM']) or self.dut.VbarRestarted) and not testSwitch.virtualRun:
               # if 500G OEM to 500G SBS waterfall, keep *EC48451/48452 as unyielded *EC48451/48452
               if testSwitch.EN_REPORT_SAME_CAPACITY_WTF and (self.dut.pn_backup[5] == self.dut.driveattr['PART_NUM'][5]):  #no capacity changed
                  if self.dut.driveattr['DESTROKE_REQ'] == 'DSD' or self.dut.driveattr['DESTROKE_REQ'] == 'DSD_NEW_RAP':
                     tmpEC = 48452        #destroke drive
                  else:
                     tmpEC = 48451
                  self.dut.driveattr["DNGRADE_ON_FLY"] = '%s_%s_%s'%(self.dut.nextOper, self.dut.pn_backup[-3:], str(tmpEC))
               else:
                  if self.dut.driveattr['DESTROKE_REQ'] == 'DSD' or self.dut.driveattr['DESTROKE_REQ'] == 'DSD_NEW_RAP':
                     tmpEC = 48453        #destroke drive
                  else:
                     tmpEC = 12168
               self.WTF_Unyielded(ec=tmpEC)

         elif vbarResult == 'DEPOP_RESTART':
            objMsg.printMsg('*'*100)
            objMsg.printMsg("DEPOP REQUESTED")
            objMsg.printMsg('*'*100)
            WTFDisposition(self.dut).run(WtfRequest =WTFDisposition.dispoEnum.DEPOP)

         #elif vbarResult == 91919 :
         elif vbarResult == 'RPM_RESTART':
            objMsg.printMsg('*'*100)
            objMsg.printMsg("RPM RESTART REQUESTED")
            objMsg.printMsg('*'*100)
            self.resetWTFAttr()
            WTFDisposition(self.dut).run(WtfRequest =WTFDisposition.dispoEnum.RPM_RESTART)

         else:
            objMsg.printMsg("ERROR: Waterfall vbar failed, exit")

            if testSwitch.FE_SGP_EN_REPORT_WTF_FAILURE and ((self.dut.pn_backup != self.dut.driveattr['PART_NUM']) or self.dut.VbarRestarted) and not testSwitch.virtualRun:
               # if 500G OEM to 500G SBS waterfall, keep *EC48451/48452 as unyielded *EC48451/48452
               if testSwitch.EN_REPORT_SAME_CAPACITY_WTF and (self.dut.pn_backup[5] == self.dut.driveattr['PART_NUM'][5]):  #no capacity changed
                  if self.dut.driveattr['DESTROKE_REQ'] == 'DSD' or self.dut.driveattr['DESTROKE_REQ'] == 'DSD_NEW_RAP':
                     tmpEC = 48452        #destroke drive
                  else:
                     tmpEC = 48451
               else:
                  if self.dut.driveattr['DESTROKE_REQ'] == 'DSD' or self.dut.driveattr['DESTROKE_REQ'] == 'DSD_NEW_RAP':
                     tmpEC = 48453        #destroke drive
                  else:
                     tmpEC = 12168
               self.WTF_Unyielded(ec=tmpEC)

            if not testSwitch.virtualRun:
               raiseException(vbarResult, "ERROR: VBAR failure, exit")


      if self.dut.currentState in ['HMSC_DATA']:
         from MathLib import stDev_standard, mean
         
         listHMScap = list(list() for i in xrange(self.dut.imaxHead))
         WkWrtEC = 14805

         try:
            colDict = self.dut.dblData.Tables('P_VBAR_HMS_ADJUST').columnNameDict()
            pHMSTbl = self.dut.dblData.Tables('P_VBAR_HMS_ADJUST').rowListIter(index=hms_table_start)
         except:
            objMsg.printMsg('WARNING...P_VBAR_HMS_ADJUST NOT FOUND')
            return

         objMsg.printMsg("testSwitch.ENABLE_HMSCAP_SCREEN = %d" % testSwitch.ENABLE_HMSCAP_SCREEN)
         objMsg.printMsg("MEAN_HMSCap_REQUIRED = %.3f" % TP.HMSCapScrnSpec['MEAN_HMSCap_REQUIRED'])
         objMsg.printMsg("MIN_HMSCap_REQUIRED = %.3f" % TP.HMSCapScrnSpec['MIN_HMSCap_REQUIRED'])
         objMsg.printMsg("StdDev_HMSCap_REQUIRED = %.3f" % TP.HMSCapScrnSpec['StdDev_HMSCap_REQUIRED'])

         # loop through table
         for row in pHMSTbl:
            listHMScap[int(row[colDict['HD_LGC_PSN']])].append(float(row[colDict['HMS_CAP']]))
         # loop through hd
         for hd in xrange(self.dut.imaxHead): 
            MinHMScap = min(listHMScap[hd])
            MeanHMScap = mean(listHMScap[hd])
            StdDevHMScap = stDev_standard(listHMScap[hd])
            objMsg.printMsg("head: %d, listHMScap %s." % (hd, listHMScap[hd]))
            objMsg.printMsg("MeanHMScap = %.3f" % MeanHMScap)
            objMsg.printMsg("MinHMScap = %.3f" % MinHMScap)
            objMsg.printMsg("StdDevHMScap = %.3f" % StdDevHMScap)
            if MeanHMScap < TP.HMSCapScrnSpec['MEAN_HMSCap_REQUIRED'] and MinHMScap < TP.HMSCapScrnSpec['MIN_HMSCap_REQUIRED']:
               objMsg.printMsg("Hd %d fail HMS spec EC%d" % (hd, WkWrtEC+hd) )
               if not testSwitch.virtualRun and testSwitch.ENABLE_HMSCAP_SCREEN:
                  raiseException(48536, "HMS Capability Out Of Spec")

   #-------------------------------------------------------------------------------------------------------
   def WTF_Unyielded(self, ec= 12168):
      objMsg.printMsg("Capacity waterfall with no restart/failure - sending unyielded failcode to FIS")

      #send test time for EC reporting
      self.dut.driveattr['TEST_TIME']  = "0"
      DriveAttributes['TEST_TIME'] = self.dut.driveattr['TEST_TIME']

      #send WTF for EC reporting
      self.dut.driveattr['WTF'] = self.dut.WTF_EC_Backup
      DriveAttributes['WTF'] = self.dut.driveattr['WTF']

      if testSwitch.FE_SGP_EN_REPORT_RESTART_FAILURE and not (testSwitch.EN_REPORT_SAME_CAPACITY_WTF and (self.dut.pn_backup[5] == self.dut.driveattr['PART_NUM'][5])):
         evalOper = "%s" % self.dut.nextOper    #Send the data under the Oper run
      else:
         evalOper = "*%s" % self.dut.nextOper   #Send the data under the *Oper run

      objMsg.printMsg("evalOper=%s self.dut.pn_backup=%s self.dut.driveattr['PART_NUM']=%s" % (evalOper, self.dut.pn_backup, self.dut.driveattr['PART_NUM']))

      try:
         tmp_pn = DriveAttributes['PART_NUM']
         DriveAttributes.update({'CMS_CONFIG':'NONE'}) 
         DriveAttributes.update({'CMS_CONFIG':self.dut.driveattr["CMS_CONFIG"],'LOOPER_COUNT':1, 'PART_NUM': self.dut.pn_backup, 'DNGRADE_ON_FLY':self.dut.driveattr["DNGRADE_ON_FLY"]}) # LOOPER_COUNT to "disable" ADG
         ReportErrorCode(ec)
         RequestService('SetOperation',(evalOper,))
         RequestService('SendRun',(0,))
      finally:
         DriveAttributes['PART_NUM'] = tmp_pn
         DriveAttributes['LOOPER_COUNT'] = '0'                 # "enable" ADG
         ReportErrorCode(0)
         RequestService('SetOperation',(self.dut.nextOper,))   #Reset to the primary operation

      #restore WTF
      self.dut.driveattr['WTF'] = self.dut.WTF
      DriveAttributes['WTF'] = self.dut.driveattr['WTF']

   #-------------------------------------------------------------------------------------------------------
   def buildClusterList(self, updateWTF = 0):
      from base_GOTF import CGOTFGrading
      from StateMachine import CBGPN
      from CommitServices import isTierPN
      self.partNum = self.dut.partNum
      printDbgMsg("self.partNum: %s" %(self.partNum))
      self.oGOTF = CGOTFGrading()
      self.objBGPN = CBGPN(self.oGOTF)

      if testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT:
         if (self.dut.driveattr['ORG_TIER'] in [TIER1, TIER2, TIER3]) or isTierPN( self.dut.partNum ):
            self.objBGPN.GetBGPN(reset_Manual_GOTF = 1)
      else:
         self.objBGPN.GetBGPN()

      self.keyCounter = 0

      self.nibletString = self.dut.serialnum[1:3] + '_'

      if not testSwitch.CM_REDUCTION_REDUCE_PRINTMSG:
         self.displayAttr()
      self.partNum = self.searchPN(self.partNum)


      if self.dut.Waterfall_Req == 'NONE' and not self.dut.depopMask:
      #if self.dut.Waterfall_Req[0] == 'N':
         printDbgMsg("Native, Waterfall_Req: %s " % (self.dut.Waterfall_Req ))
         waterfallType= 'Native'

         # Build niblet string for native waterfall
         if nibletTable[self.partNum][waterfallType][0]:
            self.nibletString += nibletTable[self.partNum][waterfallType][0]
            printDbgMsg("nibletString: %s" %(self.nibletString))
            printDbgMsg("Waterfall_Req found in nibletTable: %s " % (self.nibletString[3:5]))
            capacity = nibletTable[self.partNum]['Capacity'][self.keyCounter]
            if not '_' in capacity:    # a must to have the drive sector size.
               if testSwitch.WTFCheckSectorSize:
                  raiseException(12150, "ERROR: Drv_Sector_Size not defined at index %s in nibletTable" % self.keyCounter)
            self.nibletString += '_'
            self.nibletString += capacity
            printDbgMsg("Capacity found in nibletTable: %s " % (capacity))
            #=== Add part number to TP.VbarPartNumCluster
            self.BuildVbarPartNumCluster(self.partNum, self.keyCounter)
         else:
            printDbgMsg("ERROR: Can not find %s in nibletTable for PN %s" % (waterfallType, self.partNum))
            if not testSwitch.CM_REDUCTION_REDUCE_PRINTMSG:
               self.displayAttr()
            raiseException(12150, "ERROR: Can not find Waterfall_Req in nibletTable")

      else:
         # Handle non-native waterfall requests
         printDbgMsg("self.dut.depopMask: %s" % (self.dut.depopMask))
         printDbgMsg("self.dut.Waterfall_Req[0]: %s" %( str(self.dut.Waterfall_Req[0])))

         # Choose the right row in the nibletTable
         if self.dut.Waterfall_Req[0] == 'R':
            if self.dut.depopMask:
               raiseException(12150, "ERROR: Waterfall_Req conflicts with Depop_Req")

            # set Waterfall_Req to matching value as in nibletTable
            if testSwitch.FORCE_WTF_SET_ATTR_BY_NIBLET_TABLE and self.dut.Waterfall_Req == 'REZONE':
               for nibletindex in range( len(nibletTable[self.partNum]['Capacity']) ):
                  rezone   = nibletTable[self.partNum]['Rezone'][nibletindex]
                  capacity = nibletTable[self.partNum]['Capacity'][nibletindex].split('_')[0]
                  if rezone == '': continue
                  if capacity not in TP.Native_Capacity:
                     self.dut.Waterfall_Req = rezone[0:2]
                     break

            printDbgMsg("Rezone, Waterfall_Req: %s" %( self.dut.Waterfall_Req))
            waterfallType= 'Rezone'
         #elif self.dut.Waterfall_Req[0] == 'D':
         elif self.dut.Waterfall_Req[0] == 'D' or self.dut.depopMask:
            waterfallType = 'Depop'
            printDbgMsg("self.dut.Depop_Done: %s" %(str(self.dut.Depop_Done)))
            if self.dut.Depop_Done == 'NONE':
               numPhysHds = self.dut.Servo_Sn_Prefix_Matrix[self.dut.serialnum[1:3]]['PhysHds']
               self.dut.Waterfall_Req = 'D' + str(numPhysHds - len(self.dut.depopMask))
               self.dut.driveattr['DEPOP_DONE'] = 'DONE'    # This could be set to done from previous run or this current run
               self.dut.Depop_Done = 'DONE'                 # This tells us if we have depopped during this operation
               # For rewrite AFH_SIM.bin when depop after AFH
               DriveAttributes['OTF_DEPOP_MASK'] = self.dut.depopMask[0]

               printDbgMsg("Depop Heads: %s" %(self.dut.depopMask))
               printDbgMsg("Depop, Waterfall_Req: %s" %(self.dut.Waterfall_Req))
               printDbgMsg("Depop, Depop_Req: %s" %(self.dut.Depop_Req))
         else:
            printDbgMsg("ERROR: Bad Waterfall_Req: %s" % (self.dut.Waterfall_Req))
            if not testSwitch.CM_REDUCTION_REDUCE_PRINTMSG:
               self.displayAttr()
            raiseException(12150, "ERROR: Bad Waterfall_Req")

         printDbgMsg("%s, Waterfall_Req: %s" %(waterfallType, self.dut.Waterfall_Req))

         foundMatch = 0
         # Find the niblet key that matches the waterfall request
         for nibletkey in nibletTable[self.partNum][waterfallType]:
            printDbgMsg("keycounter:%s nibletKey: %s " % (self.keyCounter, nibletkey))
            printDbgMsg("Looping, Waterfall_Req: %s" %( self.dut.Waterfall_Req))
            if self.dut.Waterfall_Req in nibletkey:
               if len(nibletTable[self.partNum]['Capacity']) > self.keyCounter:
                  capacity = nibletTable[self.partNum]['Capacity'][self.keyCounter]
                  printDbgMsg("Capacity found in nibletTable: %s " % (capacity))
                  if '_' in capacity:
                     Drv_Sector_Size = capacity.split('_')[1]
                     if Drv_Sector_Size == self.dut.Drv_Sector_Size:
                        foundMatch = 1
                        break
                     elif not testSwitch.WTFCheckSectorSize:
                        printDbgMsg("NOT WTFCheckSectorSize")
                        foundMatch = 1
                        break
                  else:
                     if testSwitch.WTFCheckSectorSize:
                        raiseException(12150, "ERROR: Drv_Sector_Size not defined at index %s in nibletTable for ADG/Rerun drive" % self.keyCounter)

               else:
                  raiseException(12150, "ERROR: Capacity not defined at index %s in nibletTable for ADG/Rerun drive" % self.keyCounter)

            self.keyCounter += 1

         if foundMatch:
            printDbgMsg("Waterfall_Req(%s) and Drv_sector_Size(%s) found in nibletTable" % (nibletkey, self.dut.Drv_Sector_Size))
            self.nibletString += nibletkey + '_'
            if nibletkey.find('L')> -1:
               self.dut.Niblet_Level = nibletkey.split('L')[-1]
         else:
            if not testSwitch.CM_REDUCTION_REDUCE_PRINTMSG:
               self.displayAttr()
            raiseException(12150, "ERROR: Waterfall_Req or Drv_sector_Size not found in nibletTable for ADG/Rerun drive")

         # Add the capacity to the niblet string
         if len(nibletTable[self.partNum]['Capacity']) > self.keyCounter:
            capacity = nibletTable[self.partNum]['Capacity'][self.keyCounter]
            printDbgMsg("Capacity found in nibletTable: %s " % (capacity))
            self.nibletString += capacity
            if '_' in capacity:
               self.dut.Drv_Sector_Size = capacity.split('_')[1]
            elif testSwitch.WTFCheckSectorSize:
               raiseException(12150, "ERROR: Drv_Sector_Size not defined at index %s in nibletTable for ADG/Rerun drive" % self.keyCounter)
            #=== Add part number to TP.VbarPartNumCluster
            printDbgMsg("PN=%s, keyCounter=%d" % (self.partNum, self.keyCounter) )
            self.BuildVbarPartNumCluster(self.partNum, self.keyCounter)
         else:
            raiseException(12150, "ERROR: Capacity not defined at index %s in nibletTable for ADG/Rerun drive" % self.keyCounter)

      # Check for nibletLibrary in TP object first.  This allows the selection
      # of the proper nibletLibrary based on certain attributes like head type.
      nibletLibrary = getattr(TP, "nibletLibrary", None)
      if nibletLibrary is not None:
         printDbgMsg("Using nibletLibrary from TP")
      else:
         from PIF import nibletLibrary as nibletLibrary
         printDbgMsg("Using nibletLibrary from PIF")

      # Build the niblet cluster based on niblet strings
      TP.VbarNibletCluster = []     # List of niblets used by VBAR code
      self.VbarNibletCluster = []   # List of niblet data to help locate niblet in nibletTable
      while True:
         printDbgMsg("nibletString: %s" %(self.nibletString))

         # Validate presence of niblet string in niblet table
         if nibletLibrary.has_key(self.nibletString):
            printDbgMsg("keyCounter: %s Complete nibletstring found: %s" %(str(self.keyCounter),self.nibletString))
         else:
            printDbgMsg("Can not find complete nibletstring: %s in nibletLibrary" %(self.nibletString))

            if len(self.VbarNibletCluster) == 0 :
               if not testSwitch.CM_REDUCTION_REDUCE_PRINTMSG:
                  self.displayAttr()
               raiseException(12150, "ERROR: Can not find complete niblet string in nibletLibrary")
            else:
               printDbgMsg("No more niblet, break")
               break

         # Add niblet to cluster structures
         if testSwitch.BF_0274769_321126_ALLOW_EMPTY_PN_FOR_NIBLETTABLE:
            # not native capacity if keyCounter > 0. Then need check if having demand for lower capacity
            if self.keyCounter == 0 or self.isValidNiblet(self.keyCounter):   
               TP.VbarNibletCluster.append(nibletLibrary[self.nibletString])
               self.VbarNibletCluster.append((self.keyCounter, self.nibletString))
         else:
            TP.VbarNibletCluster.append(nibletLibrary[self.nibletString])
            self.VbarNibletCluster.append((self.keyCounter, self.nibletString))

         #Abort loop if only native capacity is allowed
         if ConfigVars[CN].get('NativeWTFOnly',0) == 1:
            printDbgMsg("NativeWTFOnly, break")
            break

         self.keyCounter += 1    # Allow all niblets to be found

         # Search for the next niblet table entry
         for index,item in enumerate(nibletTable[self.partNum]['Capacity'][self.keyCounter:]):
            if DEBUG:
               objMsg.printMsg("waterfall: Index = %s" %(str(index)))
               objMsg.printMsg("waterfall: item = %s" %(str(item)))
               objMsg.printMsg("waterfall: keyCounter = %s" %(str(self.keyCounter)))

            if (self.dut.Waterfall_Req == 'NONE' or self.dut.Waterfall_Req[0] == 'R') and \
               nibletTable[self.partNum].get('Rezone','') and nibletTable[self.partNum]['Rezone'][self.keyCounter]:  # To skip some empty D/R request
                  waterfallType = 'Rezone'
                  if DEBUG:  objMsg.printMsg("waterfallType: Rezone")
            elif self.dut.Waterfall_Req[0] == 'D' and \
               nibletTable[self.partNum].get('Depop','') and nibletTable[self.partNum]['Depop'][self.keyCounter]:
               waterfallType = 'Depop'
               if DEBUG:  objMsg.printMsg("waterfallType: Depop")
            elif (self.dut.Waterfall_Req == 'NONE' or self.dut.Waterfall_Req[0] == 'R') and \
               nibletTable[self.partNum].get('Depop','') and nibletTable[self.partNum]['Depop'][self.keyCounter] and \
               testSwitch.SKIPZONE and self.dut.nextState == 'DEZONE':
               waterfallType = 'Depop'
               if DEBUG:  objMsg.printMsg("waterfallType: Depop")
            else:
               self.keyCounter += 1
               if DEBUG:   objMsg.printMsg("waterfallType: Not found")
               continue

            self.nibletString = self.dut.serialnum[1:3]
            self.nibletString += '_'
            self.nibletString += nibletTable[self.partNum][waterfallType][self.keyCounter]
            capacity = nibletTable[self.partNum]['Capacity'][self.keyCounter]
            if not '_' in capacity:    # a must to have the drive sector size.
               if testSwitch.WTFCheckSectorSize:
                  raiseException(12150, "ERROR: Drv_Sector_Size not defined at index %s in nibletTable" % self.keyCounter)
            self.nibletString += '_'
            self.nibletString += capacity

            printDbgMsg("Counter: %s" %(str(self.keyCounter)))
            #=== Add part number to TP.VbarPartNumCluster
            self.BuildVbarPartNumCluster(self.partNum, self.keyCounter)
            break

         # Abort loop if exhausted all the niblet table entries
         if testSwitch.SKIPZONE and self.dut.nextState == 'DEZONE':
            if (self.keyCounter == len(nibletTable[self.partNum]['Capacity'])):
               printDbgMsg("SKIPZONE: Auto rezone/depop, exiting loop for more nibletString")
               break
         else:
            if (self.keyCounter == len(nibletTable[self.partNum]['Capacity'])) or ((waterfallType=='Depop') and (self.dut.Depop_Done =='NONE')):
               printDbgMsg("Auto rezone/depop, exiting loop for more nibletString")
               break

      #if only native capacity is allowed
      if ConfigVars[CN].get('NativeWTFOnly',0) == 1:
         printDbgMsg("NativeWTFOnly = 1")
         self.updateWTF()
         if not testSwitch.CM_REDUCTION_REDUCE_PRINTMSG:
            self.displayAttr()
         if not self.dut.WTF == 'D0R0':
            printDbgMsg("WTF: %s which is not DORO for EN_WATERFALL = 0" % (self.dut.WTF))
            raiseException(12150, "ERROR: WTF is not DORO for NativeWTFOnly = 1")

      # to update WTF only
      if updateWTF:
         self.keyCounter, self.nibletString = self.VbarNibletCluster[0]
         self.updateWTF()
         if not testSwitch.CM_REDUCTION_REDUCE_PRINTMSG:
            self.displayAttr()
   #------------------------------------------------------------------------------------------------------#
   if testSwitch.BF_0274769_321126_ALLOW_EMPTY_PN_FOR_NIBLETTABLE:
      def isValidNiblet(self, nibletIndex):
         valid = False
         
         newPN = nibletTable[self.partNum]['Part_num'][nibletIndex].rstrip()
         if nibletIndex > 0 and len(newPN) > 0:
            valid = True
         elif nibletIndex == 0:
            valid = True
         
         return valid
   #------------------------------------------------------------------------------------------------------#
   #
   def searchPN(self,partNum):
      printDbgMsg("searchPN: Search for valid PN")

      PN_found = 0

      if nibletTable.has_key(partNum):    #check for 9 digit PN 1st
         printDbgMsg("9 digits PN found: %s" % (partNum))
         PN_found = 1
      else:                               #check for 6 digit model number
         for item in nibletTable:
            if len(item) in [6,7] and partNum[0:len(item)] == item:
               partNum = item
               printDbgMsg("6 digits PN found: %s " % (partNum))
               if DEBUG:   objMsg.printMsg("nibletTable: %s " % (nibletTable[partNum]))
               PN_found = 1
               break

      if PN_found == 0:
         printDbgMsg("ERROR: PN: %s not found" %(partNum))
         if not testSwitch.CM_REDUCTION_REDUCE_PRINTMSG:
            self.displayAttr()
         raiseException(12150, "ERROR: PN not found")

      return partNum

   #------------------------------------------------------------------------------------------------------#
   #
   def BuildVbarPartNumCluster(self, pn, cnt):
      newPN = nibletTable[pn]['Part_num'][cnt]
      if len(newPN):
         if len(newPN) in [6, 7]:
            TP.VbarPartNumCluster[cnt] = newPN.split('-')[0] + '-' + self.dut.partNum.split('-')[1]
         else:
            TP.VbarPartNumCluster[cnt] = newPN
      else:
         if testSwitch.BF_0274769_321126_ALLOW_EMPTY_PN_FOR_NIBLETTABLE:
            if len(TP.VbarPartNumCluster) - 1 < cnt:
               TP.VbarPartNumCluster.extend(['' for i in range(len(TP.VbarPartNumCluster), cnt + 1)])
            if cnt == 0: TP.VbarPartNumCluster[cnt] = self.dut.partNum
            else: TP.VbarPartNumCluster[cnt] = newPN
         elif cnt > 0:
            raiseException(12150, "No Waterfall Demmand")
         
      printDbgMsg("TP.VbarPartNumCluster[%d]: %s " % (cnt,TP.VbarPartNumCluster[cnt]))

   #------------------------------------------------------------------------------------------------------#
   #
   def updateWTF(self, restart=False):
      from PIF import WTFTable, WTF_rpmTable
      objMsg.printMsg("updateWTF: WTF, Waterfall_Req, Waterfall_Done and Niblet_Level")

      self.dut.WTF_EC_Backup = self.dut.WTF

      ns_found = 0
      for wtfKey in WTFTable:
         if wtfKey[0:5] == self.nibletString[0:5]:
            objMsg.printMsg("WTF entry found: %s  WTF: %s" %(wtfKey,WTFTable[wtfKey]))
            self.dut.WTF = WTFTable[wtfKey]
            try:
               self.dut.WTF += WTF_rpmTable[self.dut.serialnum[1:3]][self.dut.driveattr['SPINDLE_RPM']]
            except:
               pass

            if self.dut.Depop_Req_Backup != 'NONE':
               self.dut.WTF = self.dut.WTF[0] + 'A' + self.dut.WTF[2:]

            if self.dut.Waterfall_Req_Backup != 'NONE':
               self.dut.WTF = self.dut.WTF[0:3] + 'A'

            self.dut.driveattr['WTF'] = self.dut.WTF
            ns_found = 1
            break

      if ns_found == 0:
         objMsg.printMsg("ERROR: Can not find WTF entry: %s in WTFTable" %(self.nibletString[0:5]))
         if not testSwitch.CM_REDUCTION_REDUCE_PRINTMSG:
            self.displayAttr()
         raiseException(12150, "ERROR: Can not find WTF entry in WTFTable")
      if self.dut.nextState == 'INIT':
         return

      # If the drive is native or a depop restart was requested, keep waterfall_req set to NONE
      if self.dut.Waterfall_Req == 'NONE' and (self.keyCounter == 0):   # Native
         self.dut.Waterfall_Done = 'NONE'
      elif restart:
         self.dut.Waterfall_Done = 'NONE'
         self.dut.Waterfall_Req = self.nibletString[3:5]
      else:
         self.dut.Waterfall_Done = 'DONE'
         self.dut.Waterfall_Req = self.nibletString[3:5]

      self.dut.Niblet_Level = self.nibletString[6]
      self.dut.Drv_Sector_Size = self.nibletString.split('_')[3]
      self.dut.driveattr['WATERFALL_DONE'] = self.dut.Waterfall_Done
      self.dut.driveattr['WATERFALL_REQ'] = self.dut.Waterfall_Req
      self.dut.driveattr['NIBLET_LEVEL'] = self.dut.Niblet_Level
      self.dut.driveattr['DRV_SECTOR_SIZE'] = self.dut.Drv_Sector_Size
      self.dut.driveattr['DEPOP_REQ'] = self.dut.Depop_Req
   #------------------------------------------------------------------------------------------------------#
   def updateATTR(self, partNum, keyCounter):
      from base_GOTF import CGOTFGrading
      from StateMachine import CBGPN
      objMsg.printMsg("updateATTR: updating the Partnumber/Business group")

      self.partNumOrg = self.dut.partNum
      self.oGOTF = CGOTFGrading()
      self.objBGPN = CBGPN(self.oGOTF)

      if (keyCounter != 0):
         if len(nibletTable[partNum]['Part_num'][keyCounter]) >2:   # need to change PN
            self.dut.partNum =  nibletTable[partNum]['Part_num'][keyCounter]
            if len(self.dut.partNum) in [6,7,10]:
               objMsg.printMsg("Len of PN(%s): %s " %(self.dut.partNum,len(self.dut.partNum)))
            else:
               objMsg.printMsg("ERROR: len of PN %s in nibletTable is not 6,7 or 10" %(self.dut.partNum))
               if not testSwitch.CM_REDUCTION_REDUCE_PRINTMSG:
                  self.displayAttr()
               raiseException(12150, "ERROR: len of PN in nibletTable is not 6,7 or 10")
            if len(self.dut.partNum) in [6,7]:
               objMsg.printMsg("PN %s " %(self.dut.partNum))
               self.dut.partNum += self.partNumOrg[len(self.dut.partNum):10]

            if testSwitch.RELOAD_DEMAND_TABLE_ON_WTF:    # Reload DemandTable from PIF.py upon waterfall
               self.dut.demand_table = self.dut.DEMAND_TABLE[:]   # force demand table reload

            try: self.objBGPN.GetBGPN() # update BG
            except:
               try:
                  objMsg.printMsg("Looking for alternate PN")
                  if len(nibletTable[self.partNum]['altPart_num'][self.keyCounter]) == 10:
                     self.dut.partNum =  nibletTable[self.partNum]['altPart_num'][self.keyCounter]
                     self.objBGPN.GetBGPN() # update BG
                  else :      # no PN
                     objMsg.printMsg("ERROR: No altPN for PN update")
                     if not testSwitch.CM_REDUCTION_REDUCE_PRINTMSG:
                        self.displayAttr()
                     raiseException(12150, "ERROR: No PN for PN update")
               except:
                  objMsg.printMsg("Waterfall: Part number %s not found in Manual_GOTF" % self.dut.partNum)
                  raiseException(13425, "Part number not found in Manual_GOTF")
            if self.oGOTF.gotfTestGroup(self.dut.BG) == False:
               objMsg.printMsg("ERROR: Wrong BG: %s while changing PN" %(self.dut.BG))
               if not testSwitch.CM_REDUCTION_REDUCE_PRINTMSG:
                  self.displayAttr()
               raiseException(12150, "ERROR: Wrong BG while changing PN")

            self.dut.driveattr['PART_NUM'] = self.dut.partNum
            self.dut.setDriveCapacity()
            objMsg.printMsg('After WTF self.CAPACITY=%s' % self.dut.CAPACITY_PN)
            objMsg.printMsg('After WTF self.CAPACITY_CUS=%s' % self.dut.CAPACITY_CUS)
            HostSetPartnum(self.dut.partNum)
         else :      # no PN
            objMsg.printMsg("ERROR: No PN for PN update")
            if not testSwitch.CM_REDUCTION_REDUCE_PRINTMSG:
               self.displayAttr()
            raiseException(12150, "ERROR: No PN for PN update")
      else :
         objMsg.printMsg("No need to update PN")

      if not testSwitch.CM_REDUCTION_REDUCE_PRINTMSG:
         self.displayAttr()

   #------------------------------------------------------------------------------------------------------#

   #------------------------------------------------------------------------------------------------------#
   def displayAttr(self):
      objMsg.printMsg("--*******************--")
      objMsg.printMsg("SN              : %s " %(self.dut.serialnum) )
      objMsg.printMsg("PN              : %s " %(self.dut.partNum) )
      objMsg.printMsg("BG              : %s " %(self.dut.BG) )
      objMsg.printMsg("Waterfall_Req   : %s " %(self.dut.Waterfall_Req))
      objMsg.printMsg("Depop_Req       : %s " %(self.dut.Depop_Req))
      objMsg.printMsg("Depop_Done      : %s " %(self.dut.Depop_Done))
      objMsg.printMsg("depopMask       : %s " %(self.dut.depopMask))
      objMsg.printMsg("Niblet_Level    : %s " %(self.dut.Niblet_Level))
      objMsg.printMsg("Drv_Sector_Size : %s " %(self.dut.Drv_Sector_Size))
      objMsg.printMsg("Waterfall_Done  : %s " %(self.dut.Waterfall_Done))
      objMsg.printMsg("WTF             : %s " %(self.dut.WTF))
      objMsg.printMsg("--*******************--")

   #------------------------------------------------------------------------------------------------------#
   def resetWTFAttr(self):

      objMsg.printMsg("Reset WTF attributes")

      self.dut.WTF               = 'NONE'
      self.dut.Waterfall_Req     = 'NONE'
      self.dut.Waterfall_Done    = 'NONE'
      self.dut.Niblet_Level      = 'NONE'
      self.dut.Drv_Sector_Size   = 'NONE'
      self.dut.Depop_Req         = 'NONE'

      self.dut.driveattr['WTF']              = self.dut.WTF
      self.dut.driveattr['WATERFALL_DONE']   = self.dut.Waterfall_Done
      self.dut.driveattr['WATERFALL_REQ']    = self.dut.Waterfall_Req
      self.dut.driveattr['NIBLET_LEVEL']     = self.dut.Niblet_Level
      self.dut.driveattr['DRV_SECTOR_SIZE']  = self.dut.Drv_Sector_Size
      self.dut.driveattr['DEPOP_REQ']        = self.dut.Depop_Req

      if not testSwitch.CM_REDUCTION_REDUCE_PRINTMSG:
         self.displayAttr()
###########################################################################################################
class CDestrokeWaterfall(CWaterfallTest):

   def __init__(self, dut, params={}):
      objMsg.printMsg("CDestrokeWaterfall: Init ")
      self.dut = dut
      self.params = params
      CState.__init__(self, dut)

   def run(self):
      objMsg.printMsg('*'*100)
      objMsg.printMsg("DESTROKE WITH NEW RAP REQUESTED")
      objMsg.printMsg('*'*100)

      self.buildClusterList()
      for keyCounter, nibletString in self.VbarNibletCluster:
         if nibletString.find('320G') > -1:
            self.nibletString = nibletString
            self.keyCounter = keyCounter
            self.dut.Waterfall_Req = nibletString[3:5]
            break

      partNumNew = nibletTable[self.dut.partNum]['Part_num'][self.keyCounter]
      self.dut.partNum = partNumNew
      self.dut.driveattr['PART_NUM'] = self.dut.partNum

      if not testSwitch.FE_0190240_007955_USE_FILE_LIST_FUNCTIONS_FROM_DUT_OBJ:
         from Setup import CSetup
         objSetup = CSetup()
         objSetup.buildFileList()  #update file list after update new partno
      else:
         self.dut.buildFileList()

      self.updateWTF()
      if not testSwitch.CM_REDUCTION_REDUCE_PRINTMSG:
         self.displayAttr()
      WTFDisposition(self.dut).run(WtfRequest =WTFDisposition.dispoEnum.DESTROKE)

###########################################################################################################
class CDepopWaterfall(CWaterfallTest):

   def __init__(self, dut, params={}):
      self.dut = dut
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)


   def run(self):
      objMsg.printMsg("CDepopWaterfallTest: Run ")
      self.dut.pn_backup = self.dut.driveattr['PART_NUM']

      self.buildClusterList()
      if testSwitch.virtualRun :return
      if not testSwitch.virtualRun and self.dut.depopMask != []:
         for hd in self.dut.depopMask:
             if hd in self.dut.LgcToPhysHdMap:
                objMsg.printMsg("Physical Heads: %s, Depop Mask %s" %(self.dut.LgcToPhysHdMap, self.dut.depopMask))
                raiseException(12150, "ERROR: DepopReq not fulfilled before VBAR")
      # call vbar from here

      for niblet in self.VbarNibletCluster:
         objMsg.printMsg("local vbar cluster: %s " % str(niblet))

      Index = 0
      nibletIndex = 0xFF
      for niblet in TP.VbarNibletCluster:
         objMsg.printMsg(getVbarGlobalClass(CUtility).convertDictToPrintStr(niblet,'global vbar cluster',False,False))
         objMsg.printMsg("global vbar cluster: %s " %niblet)
         objMsg.printMsg("index: %d target_capacity: %d " %(Index,TP.VbarNibletCluster[Index]['DRIVE_CAPACITY']))
         self.objNiblet = CNiblet(niblet)
         #self.objPicker = CPicker(self.objNiblet,measAllZns,limits)
         #drive_capacity = float(self.objPicker.getCapacityFromDrive())
         drive_capacity = float(CVBAR().getCapacityFromDrive())
         objMsg.printMsg("drive_capacity %f" % ((drive_capacity)))
         objMsg.printMsg("target_capacity %d" % ((TP.VbarNibletCluster[Index]['DRIVE_CAPACITY'])))
         if drive_capacity > TP.VbarNibletCluster[Index]['DRIVE_CAPACITY']:
            #objTPIBPIPicker = CTPIBPIPicker()
            #objTPIBPIPicker.objNiblet = CNiblet(niblet)
            #niblet.settings['DRIVE_CAPACITY'] = TP.VbarNibletCluster[Index]['DRIVE_CAPACITY']
            CVBAR().setMaxLBA()
            nibletIndex = Index
            objMsg.printMsg("Found capacity match!!!!!!! nibletIndex: %d" % (nibletIndex))
            break
         Index = Index + 1


      if nibletIndex == 0xFF:
         objMsg.printMsg("No capacity match!!!!!!!")
         return 1
      self.keyCounter, self.nibletString = self.VbarNibletCluster[nibletIndex]
      #self.keyCounter = self.VbarNibletCluster[nibletIndex*2]
      #self.nibletString = self.VbarNibletCluster[(nibletIndex*2)+1]

      objMsg.printMsg("nibletIndex: %s" % (nibletIndex))
      objMsg.printMsg("keyCounter: %s  nibletString: %s" % (self.keyCounter, self.nibletString))

      #update partnumber and WTF attributes
      self.updateWTF()
      self.updateATTR(self.partNum,self.keyCounter)
      getVbarGlobalClass(CFSO).setFamilyInfo(TP.familyInfo,TP.famUpdatePrm_178,self.dut.depopMask)
      return 0

###########################################################################################################
class CRestartVBAR(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

      if testSwitch.FE_0142897_208705_BPI_NOMINAL_IN_RESTART_VBAR:
         self.params['BPI_NOM'] = 1

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from PreAmp import CPreAmp
      self.oSrvFunc = CServoFunc()
      self.oFSO = CFSO()
      self.oPreamp = CPreAmp()
      self.oFSO.getZoneTable() # get number of heads and zones on drive

      objVbar = CVBAR(self.params)
      objVbar.resetWritePowers()
      objVbar.setFormats()

      # run ivbar routine now
      objWTF = CWaterfallTest(self.dut, self.params)
      objWTF.run()

      self.oFSO.getZoneTable(newTable = 1, delTables = 0, supressOutput = 0)
      self.dut.maxServoTrack  = self.oSrvFunc.readServoSymbolTable(['maxServoTrack'],TP.ReadPVDDataPrm_11, TP.getServoSymbolPrm_11, TP.getSymbolViaAddrPrm_11 )
      #Disable ZAP in flash so no remenant zap is read in subsequent operations
      self.oFSO.St(TP.zapPrm_175_zapOff)

      self.odPES  = AFH.CdPES(TP.masterHeatPrm_11, TP.defaultOCLIM)
      self.odPES.frm.readFramesFromCM_SIM()

      objMsg.printMsg("moveAFHStateInfoFromStateX_toStateY")

      from AFH_constants import stateTableToAFH_internalStateNumberTranslation
      self.odPES.frm.moveAFHStateInfoFromStateX_toStateY(
         stateTableToAFH_internalStateNumberTranslation["AFH2"] , "AFH2",
         stateTableToAFH_internalStateNumberTranslation["AFH2A"], "AFH2A")
      self.odPES.frm.writeFramesToCM_SIM()
      self.odPES.frm.display_frames( 2 )

###########################################################################################################
class CVbarBase(CState):
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

      # Default SPC_ID behavior
      self.bump_spcid_before = 0
      self.bump_spcid_after  = 0
      self.skip_state        = 0

      # Load actions - virtual call to avoid loading from TP at import time
      self.loadActions()

      # Update with State Table parms
      self.actions.update(self.params)

      if testSwitch.FE_0165107_163023_P_FIX_TPII_WITH_PRESET_IN_VBAR:
         #!!!! for Charlie's TPI fix SNR experiment only!!!!  YWL
         if HDASerialNumber in TP.TPIsettingPerDriveSN:
            self.actions.update({
                               'MAX_TPI_PICKER_ADJ' : 0.00,
                                })

      # Ensure spc_id is initialized
      self.spcHelper = getVbarGlobalClass(CSpcIdHelper, {'dut':objDut})
      self.spcHelper.getSetIncrSpcId('P_VBAR_FORMAT_SUMMARY', startSpcId = 0, increment = 0, useOpOffset = 1)
      self.spcHelper.getSetIncrSpcId('P_VBAR_ADC_SUMMARY', startSpcId = 0, increment = 0, useOpOffset = 1)

   def bump_spcid(self):
      self.spcHelper.incrementRevision('P_VBAR_FORMAT_SUMMARY')

   def run(self):
      if self.bump_spcid_before:
         self.bump_spcid()

      if testSwitch.FE_0258044_348085_WATERFALL_WITH_ONE_TRK_PER_BAND and self.skip_state:
         return

      CWaterfallTest(self.dut, self.actions).run()

      # Increment the minor revision
      self.spcHelper.getSetIncrSpcId('P_VBAR_FORMAT_SUMMARY', startSpcId = 0, increment = 1, useOpOffset = 1)

      if self.bump_spcid_after:
         self.bump_spcid()

class CVbarFormatPicker(CVbarBase):
   def loadActions(self):
      self.bump_spcid_after  = 1
      self.actions = {
                  'LBR'            : testSwitch.FE_0261758_356688_LBR and not testSwitch.virtualRun, # Adjust Zone Boundery during Picker routine
                  'FMT_PICKER'     : 1,
      }

class CVbarTripletOpti(CVbarBase):
   def loadActions(self):
      self.actions = {
                  'AUTO_TRIPLET_MEAS': 1,                  
                  'NO_MARGIN_SPEC'   : 0,# testSwitch.SMR_TRIPLET_OPTI_SET_BPI_TPI, #1, # off the save BPI/TPI
                  'FMT_PICKER'       : testSwitch.SMR_TRIPLET_OPTI_SET_BPI_TPI,       #1, # off the save BPI/TPI
                  'ITERATIONS'       : 0,
                  'HANDLE_WTF_EXT'   : 0, #Dont update PCBA, fam, SAP, CAP, PFM_ID
                  'REFRESH_ZONE_TBL' : False, #dont refresh zone table
                  'HANDLE_NIBLET'    : False, #Dont set Max LBA
      }
      
class CTPINom(CVbarBase):
   def loadActions(self):
      self.bump_spcid_before = 1
      self.bump_spcid_after  = 1

      self.actions = {
                  'TPINOMINAL'         : 1,
                  'HANDLE_WTF_EXT'     : 0, #Dont update PCBA, fam, SAP, CAP, PFM_ID
                  'HANDLE_NIBLET'      : False, #Dont set Max LBA
      }

class CBPINom(CVbarBase):
   def loadActions(self):
      self.actions = {
                  'BPI_NOM'            : 1,
                  'HANDLE_WTF_EXT'     : 0, #Dont update PCBA, fam, SAP, CAP, PFM_ID
                  'REFRESH_ZONE_TBL'   : False, #dont refresh zone table 
                  'HANDLE_NIBLET'      : False, #Dont set Max LBA
      }

class C2DVbarZn(CVbarBase):
   def loadActions(self):
      self.bump_spcid_before = 1
      self.bump_spcid_after  = 1

      self.actions = {
                  'BPI_TRANSFER_MEAS'  : 1,
                  '2D_VBAR_MEAS'       : 1,
                  #'1D_VBAR_MEAS'       : 1,
                  'HANDLE_WTF_EXT'     : 0, #Dont update PCBA, fam, SAP, CAP, PFM_ID
                  'REFRESH_ZONE_TBL'   : False, #dont refresh zone table 
                  'HANDLE_NIBLET'      : False, #Dont set Max LBA
      }
      
class C1DVbarZn(CVbarBase):
   def loadActions(self):
      self.bump_spcid_before = 1
      self.bump_spcid_after  = 1

      self.actions = {
                  '1D_VBAR_MEAS'       : 1,
                  'TPI_DSS_MEAS'       : testSwitch.FE_0257372_504159_TPI_DSS_UMP_MEASURMENT,
                  'HANDLE_WTF_EXT'     : 0, #Dont update PCBA, fam, SAP, CAP, PFM_ID
                  'REFRESH_ZONE_TBL'   : False, #dont refresh zone table 
                  'HANDLE_NIBLET'      : False, #Dont set Max LBA
      }
      
class CVbarMargin(CVbarBase):
   def loadActions(self):
      self.bump_spcid_before = 1
      self.bump_spcid_after  = 1

      self.actions = {
                  'ADC_SUMMARY'        : testSwitch.FE_0253362_356688_ADC_SUMMARY,
                  'ZIPPER_ZONE_UPDATE' : testSwitch.FE_0257373_348085_ZONED_SERVO_CAPACITY_CALCULATION,
                  'ATI_MEAS'           : testSwitch.RUN_ATI_IN_VBAR,
                  'OTC_MARGIN_MEAS'    : testSwitch.VBAR_MARGIN_BY_OTC,
                  'OTC_MARGIN_V2'      : testSwitch.FE_0293889_348429_VBAR_MARGIN_BY_OTCTP,
                  'SQZ_BPIC_MEAS'      : testSwitch.FE_0254388_504159_SQZ_BPIC,
                  'HANDLE_WTF_EXT'     : 0, #Dont update PCBA, fam, SAP, CAP, PFM_ID
                  'REFRESH_ZONE_TBL'   : False, #dont refresh zone table
                  'SET_ADC_FMT'        : testSwitch.VBAR_MARGIN_BY_OTC | testSwitch.FE_0254388_504159_SQZ_BPIC | \
                                         testSwitch.FE_0253362_356688_ADC_SUMMARY | testSwitch.RUN_ATI_IN_VBAR,
                  'HANDLE_NIBLET'      : False, #Dont set Max LBA
      }

class CVbarZn(CVbarBase):
   def loadActions(self):
      self.bump_spcid_before = 1
      self.bump_spcid_after  = 1

      self.actions = {
                  'ZN_OPTI'        : not testSwitch.VBAR_2D_DEBUG_MODE,
                  'ATI_MEAS'       : testSwitch.RUN_ATI_IN_VBAR,
                  'ZN_MEAS'        : 1,
                  'HMS_OPTI'       : 0,
                  'SMR_MEAS'       : testSwitch.SMR,
                  'FMT_PICKER'     : 1,
                  'ITERATIONS'     : 0,
                  'OTC_MARGIN_MEAS': testSwitch.VBAR_MARGIN_BY_OTC,
                  'SQZ_BPIC_MEAS'  : testSwitch.FE_0254388_504159_SQZ_BPIC,
                  'OTC_MARGIN_V2'  : testSwitch.FE_0293889_348429_VBAR_MARGIN_BY_OTCTP,
                  'ADC_SUMMARY'    : testSwitch.FE_0253362_356688_ADC_SUMMARY,
                  'LBR'            : testSwitch.FE_0261758_356688_LBR and not testSwitch.virtualRun,
                  'TPI_DSS_MEAS'   : testSwitch.FE_0257372_504159_TPI_DSS_UMP_MEASURMENT,
                  'ZIPPER_ZONE_UPDATE' : testSwitch.FE_0257373_348085_ZONED_SERVO_CAPACITY_CALCULATION,
                  'PARAMS_FILTER'  : testSwitch.APPLY_FILTER_ON_SMR_TPI,
                  'SET_ADC_FMT'    : testSwitch.VBAR_MARGIN_BY_OTC | testSwitch.FE_0254388_504159_SQZ_BPIC | \
                                     testSwitch.FE_0253362_356688_ADC_SUMMARY | testSwitch.RUN_ATI_IN_VBAR,
      }

      if testSwitch.FE_0158815_208705_VBAR_ZN_MEAS_ONLY:
         self.actions.update({
                  'NO_MARGIN_SPEC': 1,
                  'MAX_BPI_PICKER_ADJ' : 0.00,
                  'MAX_TPI_PICKER_ADJ' : 0.00,
         })

class CVbarOTC(CVbarBase):
   def loadActions(self):
      self.bump_spcid_before = 1
      self.bump_spcid_after  = 1
      self.skip_state        = 0

      if (testSwitch.TRUNK_BRINGUP or testSwitch.ROSEWOOD7) and not testSwitch.extern.SFT_TEST_0271:
         objMsg.printMsg('WARNING: VBAR OTC requires SFT_TEST_0271')
         self.actions = {}
         return

      self.actions = {
         'RD_OFT_MEAS'        : testSwitch.OTC_BASED_RD_OFFSET, 
         'FMT_PICKER'         : 1,
         'HANDLE_WTF_EXT'     : 0, #Dont update PCBA, fam, SAP, CAP, PFM_ID
         'REFRESH_ZONE_TBL'   : False, #dont refresh zone table
         'HANDLE_NIBLET'      : False, #Dont set Max LBA
      }

      if testSwitch.FE_0258044_348085_WATERFALL_WITH_ONE_TRK_PER_BAND:
         objMsg.printMsg("VBAR_OTC: Partnumber=%s" % self.dut.driveattr['PART_NUM'])
         part1, part2 = self.dut.driveattr['PART_NUM'].split('-')
         if part1[-1] in ['C','c']:
            objMsg.printMsg("Skip state = %s" % (self.dut.currentState))
            self.skip_state = 1

class CVbarInterbandScrn(CVbarBase):
   def loadActions(self):
      self.actions = {
         'OTC_INTERBANDMEAS'  : 1,
         'HANDLE_NIBLET'      : False, #Dont set Max LBA
      }

class CVbarHMS_ZapOffEnd(CVbarBase):
   def loadActions(self):

      if testSwitch.VBAR_HMS_MEAS_ONLY:
         self.actions = {
                     'HMS_MEAS'           : 1,
                     'HMS_OPTI'           : [0,1],
                     'ADJ_MARGIN_SPEC'    : 0,
                     'FMT_PICKER'         : 0,
                     'ITERATIONS'         : 1,
                     'BPI_PER_HMS'        : TP.BPIperHMS1,
                     'MAX_BPI_STEP'       : [0.07, 0.06],
                     'MAX_TPI_PICKER_ADJ' : 0.00,
                     'NO_DISABLE_ZAP'     : 0,
                     'REFRESH_ZONE_TBL'   : False, #dont refresh zone table 
                     'HANDLE_NIBLET'      : False, #Dont set Max LBA
         }
      else:
         self.actions = {
                     'HMS_OPTI'           : [0,1],
                     'HMS_MEAS'           : 1,
                     'HMS_ADJ'            : 1,
                     'HMS_FAIL'           : 0,
                     'ADJ_MARGIN_SPEC'    : 1,
                     'FMT_PICKER'         : 1,
                     'ITERATIONS'         : 2,
                     'BPI_PER_HMS'        : TP.BPIperHMS1,
                     'MAX_BPI_STEP'       : [0.07, 0.06],
                     'MAX_TPI_PICKER_ADJ' : 0.00,
                     'NO_DISABLE_ZAP'     : 0,
         }
      

      if testSwitch.shortProcess:
         self.actions.update({
            'ITERATIONS'         : 1,
         })

      if testSwitch.FE_0158815_208705_VBAR_ZN_MEAS_ONLY:
         self.actions.update({
                  'NO_MARGIN_SPEC': 1,
         })

      if testSwitch.FE_0162444_208705_ASYMMETRIC_VBAR_HMS:
         self.actions.update({
                  'MIN_TARGET_HMSCAP'  : TP.VbarHMSMinTargetHMSCap,
                  'MAX_TARGET_HMSCAP'  : TP.VbarHMSMaxTargetHMSCap,
         })

      elif testSwitch.ADJUST_HMS_FOR_CONSTANT_MARGIN:
         self.actions.update({
                  'MIN_TARGET_HMSCAP'  : TP.VHMSConstantMarginTarget,  # VBAR HMS Constant Margin testing mode,
                  'MAX_TARGET_HMSCAP'  : TP.VHMSConstantMarginTarget,  # VHMSConstantMarginTarget is set in base_TestParameters.py.
         })

class CVbarTuning(CState):
   """
      Description:
         VBAR (Variable Bit Aspect Ratio) Optimization Routines for head/zone write power settings
         and head bpi & tpi formats (for both single and multiple heads)
         This routine runs the iVBAR (integrated VBAR)
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from Servo import CServoFunc
      from PreAmp import CPreAmp
      self.oSrvFunc = CServoFunc()
      self.oFSO = getVbarGlobalClass(CFSO)
      self.oPreamp = CPreAmp()
      self.oFSO.getZoneTable() # get number of heads and zones on drive

      if testSwitch.WA_0111716_007955_POWERCYCLE_AT_VBAR_START:
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

      # run ivbar routine now
      objVbar = CVBAR(self.params)
      nibletIndex, vbarResult = objVbar.run()  #vbarResult = EC

      self.oFSO.getZoneTable(newTable = self.params.get('REFRESH_ZONE_TBL', True), delTables = 0, supressOutput = 0)
      if self.params.get('REFRESH_ZONE_TBL', True):
         self.dut.maxServoTrack  = \
            self.oSrvFunc.readServoSymbolTable(['maxServoTrack'],TP.ReadPVDDataPrm_11, TP.getServoSymbolPrm_11, TP.getSymbolViaAddrPrm_11 )

      return nibletIndex, vbarResult

