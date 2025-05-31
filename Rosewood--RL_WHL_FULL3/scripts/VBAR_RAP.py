#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Vbar RAP Tools Module
#  - Contains various RAP related functions
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
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/VBAR_RAP.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/VBAR_RAP.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
from Drive import objDut
from DesignPatterns import Singleton
from Process import CProcess
import MessageHandler as objMsg
from ScrCmds import raiseException
import time
from VBAR_Constants import *
from VBAR_Zones import CVbarTestZones


#----------------------------------------------------------------------------------------------------------
class CRapTcc(Singleton):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self):
      # Initialize some basic utilities
      self.dut = objDut

      self.prm_wp_178 = {'test_num': 178, 'prm_name': 'prm_wp_178', 'timeout': 1200, 'spc_id': 0,}

      self.oProc = CProcess()

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
         for hd in xrange(self.dut.imaxHead):
            self.VbarWPTable[hd] = {}
            for zn in xrange(self.dut.numZones+1):
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
      self.tgtWrClr = [afhZoneTargets['TGT_WRT_CLR'][zn] for zn in xrange(self.dut.numZones+1)]

   #-------------------------------------------------------------------------------------------------------
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
                  #zn_mask = self.oProc.oUtility.ReturnTestCylWord(self.oProc.oUtility.setZoneMask(updateIntersect))
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
                     'BIT_MASK'             : self.oProc.oUtility.ReturnTestCylWord(zn_mask_low),
                     'BIT_MASK_EXT'         : self.oProc.oUtility.ReturnTestCylWord(zn_mask_high),
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

                  self.oProc.St(prm)
         else:
            # Just update the specific zone requested
            #zn_mask = self.oProc.oUtility.ReturnTestCylWord(self.oProc.oUtility.setZoneMask(zn))
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
               'BIT_MASK'             : self.oProc.oUtility.ReturnTestCylWord(zn_mask_low),
               'BIT_MASK_EXT'         : self.oProc.oUtility.ReturnTestCylWord(zn_mask_high),
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

            self.oProc.St(prm)
      else: #if setAllZonesHeads == 1:
         hd_mask = 0x3FF
         #Set a mask and update for each triplet zone group
         if not testSwitch.FE_0334525_348429_INTERPOLATED_DEFAULT_TRIPLET:
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
                  #'BIT_MASK'            : self.oProc.oUtility.ReturnTestCylWord(zn_mask_low),
                  #'BIT_MASK_EXT'        : self.oProc.oUtility.ReturnTestCylWord(zn_mask_high),
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
                        self.oProc.oUtility.convertZoneListToZoneRange(znGroup):
                        prm['ZONE'] = ( startZn << 8) + endZn
                        prm['prm_name'] = prm['prm_name'] + ' %d' % (prm['ZONE'])
                        self.oProc.St(prm)
                  else:
                     for zn in znGroup:
                        prm['ZONE'] = zn
                        self.oProc.St(prm)
               else:
                  prm['BIT_MASK_EXT'], prm['BIT_MASK'] = self.oProc.oUtility.convertListTo64BitMask(znGroup)
                  self.oProc.St(prm)


               #zn_mask = self.oProc.oUtility.ReturnTestCylWord(self.oProc.oUtility.setZoneMask(znGroup))
         else: #if testSwitch.FE_0334525_348429_INTERPOLATED_DEFAULT_TRIPLET:
            if self.VbarWPTable.has_key('ALL'):
               objMsg.printMsg('All is provided')
               OD_WP = self.VbarWPTable['ALL'][wp]
               ID_WP = self.VbarWPTable['ALL'][wp]
            else:
               objMsg.printMsg('OD/ID is provided')
               OD_WP = self.VbarWPTable['OD'][wp]
               ID_WP = self.VbarWPTable['ID'][wp]
            
            
            TripletZnGroups = []
            VbarWPTable = []
            
            for zn in xrange(self.dut.numZones + 1): # Create Zone Groups dynamically
               # Calculate for the interpolated value of the triplet
               Iw = int(round(OD_WP[0] - float(OD_WP[0]-ID_WP[0])/self.dut.numZones * zn))
               Osa = int(round(OD_WP[1] - float(OD_WP[1]-ID_WP[1])/self.dut.numZones * zn))
               Osd = int(round(OD_WP[2] - float(OD_WP[2]-ID_WP[2])/self.dut.numZones * zn))
               #objMsg.printMsg('Zn %d Triplet %s' % (zn, [Iw, Osa, Osd]))
               if zn == 0: # append the first zone before iteration
                  zn_list = [0]
                  triplet = [Iw, Osa, Osd]
                  continue
               elif zn == self.dut.numZones:# take care of the last zone iteration    
                  TripletZnGroups.append(zn_list)
                  VbarWPTable.append(triplet)
                  continue
               elif zn == self.dut.systemAreaUserZones[0]: # Take care of System Zone
                  sys_triplet = [Iw, Osa, Osd]

               if triplet == [Iw, Osa, Osd]:
                  zn_list.append(zn)
               else:
                  #set existing zone
                  TripletZnGroups.append(zn_list)
                  VbarWPTable.append(triplet)

                  #update to new one
                  zn_list = [zn]
                  triplet = [Iw, Osa, Osd]

            # Add another ZoneGroup for System ZoneGroup
            TripletZnGroups.append([self.dut.numZones])
            VbarWPTable.append(sys_triplet)

            # Setup Test parameters
            hd_mask = 0x3FF
            prm_178 = {'test_num': 178, 'prm_name': 'prm_wp_178', 'timeout': 1200, 'spc_id': 0,'CWORD1' : 0x0200, 'CWORD2' : 0x1107, 'WRITE_CURRENT_OFFSET': (wcoc,wcoh), 'HEAD_RANGE' : hd_mask,}
            if stSuppress:
               prm_178.update({
                  'stSuppressResults' : ST_SUPPRESS__ALL,
               })

            #for idx in xrange(len(TripletZnGroups)):
            #   objMsg.printMsg('Index: %3d Triplet: %s TripletZnGroups: %s' % (idx, VbarWPTable[idx], TripletZnGroups[idx]))
            for idx in xrange(len(TripletZnGroups)):
               objMsg.printMsg('Index: %3d Triplet: %s TripletZnGroups: %s' % (idx, VbarWPTable[idx], TripletZnGroups[idx]))
               prm_178['prm_name'] = 'prm_wp_178_0x%04x_%s_%s_%s' % (TripletZnGroups[idx][0], VbarWPTable[idx][0], VbarWPTable[idx][1], VbarWPTable[idx][2])
               prm_178.update({'WRITE_CURRENT':VbarWPTable[idx][0], 'DAMPING':VbarWPTable[idx][1], 'DURATION':VbarWPTable[idx][2]})
               if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
                  if testSwitch.extern.FE_0270095_504159_SUPPORT_LOOPING_ZONE_T178:
                     startZn = sorted(TripletZnGroups[idx])[0]
                     endZn = sorted(TripletZnGroups[idx])[-1]
                     prm_178['ZONE'] = (startZn << 8) + endZn
                     self.oProc.St(prm_178)
                  else:
                     for startZn in sorted(TripletZnGroups[idx][0]):
                        prm_178['ZONE'] = startZn
                        self.oProc.St(prm_178)
               else:
                  prm_178['BIT_MASK_EXT'], prm_178['BIT_MASK'] = self.oUtility.convertListTo64BitMask(sorted(TripletZnGroups[idx][0]))
                  self.oProc.St(prm_178)
               prm_178.update({ # Update to suppress after first iteration
                  'stSuppressResults' : ST_SUPPRESS__ALL,
               })
            # For Debug Printout
            #self.oProc.St({'test_num': 178,'timeout': 600, 'CWORD1': 544})
            #self.oProc.St({'test_num': 172, 'timeout': 100, 'spc_id': 1, 'CWORD1': 12})
   #-------------------------------------------------------------------------------------------------------
   def commitRAP(self):
      """
         This method should be executed at the end of a series of updates to RAP, so that all changes
         are actually committed to the flash, i.e. the flash copy is udpated
      """
      prm = self.prm_wp_178.copy()
      prm.update({'CWORD1':0x0220}) # write RAP data to flash
      self.oProc.St(prm)
      self.oProc.St({'test_num':172, 'prm_name':"Retrieve WP's", 'CWORD1':12, 'timeout':100, 'spc_id': 1})  # Read after write
   
   #-------------------------------------------------------------------------------------------------------
   def saveRAPtoPCFile(self):
      """
         Saves RAP data to PC file
      """
      prm = self.prm_wp_178.copy()
      prm.update({'CWORD1':0x0208}) # save RAP data to PC file
      self.oProc.St(prm)

   #-------------------------------------------------------------------------------------------------------
   def recovRAPfromPCFile(self):
      """
         Recovers RAP from a PC file, updated RAM copy
      """
      prm = self.prm_wp_178.copy()
      prm.update({'CWORD1':0x0201}) # recover RAP (RAM copy) from PC file
      self.oProc.St(prm)

   #-------------------------------------------------------------------------------------------------------
   def printWpTable(self):
      objMsg.printMsg('PreAmp Type: %s' % (self.dut.PREAMP_TYPE,))
      objMsg.printMsg('Write Triplets Table:')
      objMsg.printDict(self.VbarWPTable, colWidth = 15)

   #-------------------------------------------------------------------------------------------------------
   def updateDblogWpTable(self):
      dblogOccCnt['P_WRT_PWR_TRIPLETS']+=1
      self.dut.OCC_PWR_TRIPLETS = dblogOccCnt['P_WRT_PWR_TRIPLETS']

      if testSwitch.FE_0120024_340210_ATI_IN_WRT_PWR_PICKER:
         for hd in self.VbarWPTable.keys():
            for zGroup in self.VbarWPTable[hd]:
               for wp_idx in xrange(self.NUM_WRITE_POWERS):
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
            for wp_idx in xrange(self.NUM_WRITE_POWERS):
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
