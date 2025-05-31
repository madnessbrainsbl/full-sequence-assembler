#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2009, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: AFH Module
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/SWD_Base.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/SWD_Base.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#

from Constants import *
from TestParamExtractor import TP
from AFH_constants import *
from Process import CProcess
from Temperature import CTemperature
from FSO import dataTableHelper
from Drive import objDut
import MessageHandler as objMsg
from array import array
import types
from Utility import CUtility


#----------------------------------------------------------------------------------------------------------
class CSkipWriteDetect(CProcess):
   """
      SkipWriteDetect class provides methods and attributes for evaluating
         the skip-write-detection calibrations, clearance verification,
         and clearance error adjustment
   """
   TEMPERATURE_OFFSET  = 0
   RDCLR_DELTA_OFFSET  = 1
   WRTCLR_DELTA_OFFSET = 2
   RDCLR_PERC_OFFSET   = 3
   WRTCLR_PERC_OFFSET  = 4

   #-------------------------------------------------------------------------------------------------------
   def __init__(self, masterHeatPrm, defOCLIM = 16):
      CProcess.__init__(self)

      from VBAR_Zones import CVbarTestZones

      self.vbarZoneGroups = CVbarTestZones()
      self.oUtility = CUtility()
      self.temp = CTemperature()
      self.curHDATemp = self.temp.retHDATemp()
      self.dth = dataTableHelper()
      self.swdAdjustDict = {}    # Master dictionary holding all Clr values
      self.headList = range(objDut.imaxHead)   # getZoneTable()  # needs to be called prior to the init so that this is valid

   #-------------------------------------------------------------------------------------------------------
   def SWD_Cal(self, inPrm = None):
      "Calibrate the skip write detectors for no heat trigger"

      if inPrm == None:
         cPrm = {
            'test_num'                 : 198,
            'prm_name'                 : 'SWD_Cal_198',
            'timeout'                  : 1800,
            'spc_id'                   : 1,
            'CWORD1'                   : (0x2000,),
         }
      else:
         cPrm = dict(inPrm)

      if testSwitch.extern.FE_0127369_009410_OPEN_OCLIM_DURING_T198_SWD_CALIBRATION == 1:
         SWD_T198_ENABLE_OPEN_UP_OCLIM = 0x1000
         cword1 = cPrm['CWORD1']
         if type(cword1) == types.TupleType:
            cword1 = cword1[0]
         if type(cword1) == types.ListType:
            cword1 = cword1[0]
         cPrm['CWORD1'] = cword1 | SWD_T198_ENABLE_OPEN_UP_OCLIM

      try:
         CProcess().St(cPrm)
      except ScriptTestFailure, (failuredata):
         raise

      self.report_SWD_Adapts()

   #-------------------------------------------------------------------------------------------------------
   def report_SWD_Adapts(self):
      CProcess().St({'test_num':172, 'prm_name':'SWD Drive Adapts Dump', 'timeout': 1800, 'CWORD1': (8,), 'spc_id':1})

   #-------------------------------------------------------------------------------------------------------
   def printAdjustedVBARZones(self, vbarAdjMatrix):
      outputFmt = "%20s%20s%20s"
      objMsg.printMsg("VBAR ZONE SWD Driven Clearance Adjustments")
      objMsg.printMsg(outputFmt % ("HEAD", "VBAR ZONE", "PERCENT ADJUSTMENT"))
      lineStrings = []
      for head in vbarAdjMatrix.keys():
         for item in vbarAdjMatrix[head].items():
            lineStrings.append((head, item[0], item[1]))
      for line in lineStrings:
         objMsg.printMsg(outputFmt % line)


   #######################################################################################################################
   #
   #               Function:  getUserZoneAndCorrespondingVBAR_zoneList
   #
   #        Original Author:  Michael T. Brady
   #
   #            Description:
   #
   #                          Produce a mapping as 2 lists.  The VBAR zone list is the nth VBAR zone.
   #                          The user zone list is the user zone where the corresponding VBAR zone starts.
   #                          This is to be used as an input parameter then in test 227
   #
   #          Prerrequisite:
   #
   #                  Input:  VBAR_measureZoneToListOfUserZonesDict(dict)
   #                          Example:  {0: [0, 1], 8: [5, 6, 7, 8, 9, 10, 11], 2: [2, 3, 4], 14: [12, 13, 14], 16: [15, 16, 17]}
   #
   #                 Return:
   #
   #######################################################################################################################
   def getUserZoneAndCorrespondingVBAR_zoneList(self, VBAR_measureZoneToListOfUserZonesDict):
      userZoneList = []

      for userZoneGroup in VBAR_measureZoneToListOfUserZonesDict.values():
         userZoneList.append( int(min(userZoneGroup)) )
      userZoneList.sort()

      vbarZoneList = [0 for i in range(0,len(userZoneList))]

      # These parameters have to be 10 elements long.
      if len(vbarZoneList) < 10:
         vbarZoneList = vbarZoneList + [-1 for i in range(len(vbarZoneList),10)]
         userZoneList = userZoneList + [-1 for i in range(len(userZoneList),10)]
      else:
         vbarZoneList = vbarZoneList[0:10]
         userZoneList = userZoneList[0:10]

      return vbarZoneList, userZoneList


   #######################################################################################################################
   #
   #               Function:  SWD_AdjustFlyHeight
   #
   #            Description:  Actually calls test 227 to adjust FH
   #
   #          Prerrequisite:
   #
   #                  Input:
   #
   #                 Return:
   #
   #######################################################################################################################
   def call_SWD_T227_toAdjustFlyHeight_DH(self, inPrm ):
      if self.dut.numZones < 32:
         inPrm['ZONE_MASK'] = self.oUtility.ReturnTestCylWord(self.oUtility.setZoneMask(range(self.dut.numZones)))
         inPrm['ZONE_MASK_EXT'] = (0,0)
      else:
         inPrm['ZONE_MASK'] = (0xffff, 0xffff)
         inPrm['ZONE_MASK_EXT'] = self.oUtility.ReturnTestCylWord(self.oUtility.setZoneMask(range(self.dut.numZones - 32)))


      if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT == 1:
         VBAR_measureZoneToListOfUserZonesDict = self.vbarZoneGroups.getTestZoneMap()
         vbarZoneList, userZoneList = self.getUserZoneAndCorrespondingVBAR_zoneList(VBAR_measureZoneToListOfUserZonesDict)
         inPrm['TEST_LIMITS_2ND_10'] = userZoneList
         inPrm['TEST_LIMITS_1ST_10'] = vbarZoneList

      CProcess().St(inPrm)

      # place holder - pull new table to set the re-VBAR status in the StateTable.py

   #-------------------------------------------------------------------------------------------------------
   def SWD_AdjustFlyHeight(self, inPrm, coefs, heatMode, afhZoneTargets):
      #inPrm['ZONE_MASK'] = self.oUtility.ReturnTestCylWord(self.oUtility.setZoneMask(range(self.dut.numZones)))
      if self.dut.numZones < 32:
         inPrm['ZONE_MASK'] = self.oUtility.ReturnTestCylWord(self.oUtility.setZoneMask(range(self.dut.numZones)))
         inPrm['ZONE_MASK_EXT'] = (0,0)
      else:
         inPrm['ZONE_MASK'] = (0xffff, 0xffff)
         inPrm['ZONE_MASK_EXT'] = self.oUtility.ReturnTestCylWord(self.oUtility.setZoneMask(range(self.dut.numZones - 32)))

      tableNames = [i[0] for i in self.dut.dblData.Tables()]

      if 'P227_FLY_HEIGHT_ADJ' in tableNames and not testSwitch.virtualRun:
         startIndex = len(self.dut.dblData.Tables('P227_FLY_HEIGHT_ADJ').tableDataObj())
      else:
         startIndex = 0

      self.curTemp = self.temp.retHDATemp()

      CProcess().St(inPrm)

      swdTweaks = self.dut.dblData.Tables('P227_FLY_HEIGHT_ADJ').tableDataObj()[startIndex:]

      vbarZoneAdjMaxGroups = self.get_SWD_Tweak_Table(swdTweaks, afhZoneTargets)

      applyAdjustment = 1     # legacy
      self.applySWDAdjustment(1,afhZoneTargets)

      return vbarZoneAdjMaxGroups, applyAdjustment

   #-------------------------------------------------------------------------------------------------------
   def get_SWD_Tweak_Table(self, tweakTable, afhZoneTargets, negAdjustmentAllowed = 0):

      vbarZoneAdjMaxGroups = {}

      for head in xrange(self.dut.imaxHead):
         headScaler = head * (self.dut.numZones) # doesn't have system zone
         vbarZoneAdjMaxGroups[head] = {}
         for zoneGroupNum, zones in self.vbarZoneGroups.getTestZoneMap().items():
            maxZoneAdj = 0
            #Remove system area from iterable zones
            if self.dut.numZones in zones:
               zones.remove(self.dut.numZones)

            #Compute maximum zone tweak
            for zone in zones:
               adjustmentVal = -(int(tweakTable[headScaler+zone]['PCT_CORRECTION_APPLIED']))

               # If adjustment is less than (more negative) the maxadjustment then save off new value
               if maxZoneAdj > adjustmentVal:
                  maxZoneAdj = adjustmentVal
               elif maxZoneAdj < adjustmentVal and negAdjustmentAllowed == 1:
                  maxZoneAdj = adjustmentVal
            ############################

            objMsg.printMsg("Maximum zone adjustment for head %1d vbar zone %2d found to be %3d" % (head, zoneGroupNum, maxZoneAdj))
            vbarZoneAdjMaxGroups[head][zoneGroupNum] = maxZoneAdj
            # Calculate and update by zone dictionary
            for zone in zones:

               self.swdDictUpd(head, zone, self.curHDATemp, \
                  float(afhZoneTargets['TGT_PREWRT_CLR'][zone]) * (maxZoneAdj/float(100.0)), \
                  float(afhZoneTargets['TGT_WRT_CLR'][zone]) * (maxZoneAdj/float(100.0)), \
                  maxZoneAdj, \
                  maxZoneAdj)

               # Is this the system area? if so then clone the last user zone
               if zone == self.dut.systemAreaUserZones[head]:

                  self.swdDictUpd(head, self.dut.systemZoneNum, self.curHDATemp, \
                     float(afhZoneTargets['TGT_PREWRT_CLR'][self.dut.systemZoneNum]) * (maxZoneAdj/float(100.0)), \
                     float(afhZoneTargets['TGT_WRT_CLR'][self.dut.systemZoneNum]) * (maxZoneAdj/float(100.0)), \
                     maxZoneAdj, \
                     maxZoneAdj)
      return vbarZoneAdjMaxGroups

   #-------------------------------------------------------------------------------------------------------
   def applySWDAdjustment(self, percent = 1, afhZoneTargets = []):
      if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT == 1:
         P172_AFH_CLEARANCE_tableName = 'P172_AFH_DH_CLEARANCE'
      else:
         P172_AFH_CLEARANCE_tableName = 'P172_AFH_CLEARANCE'

      CProcess().St({'test_num':172, 'prm_name':"%s" % ( P172_AFH_CLEARANCE_tableName ), 'timeout': 1800, 'CWORD1': (5,), 'spc_id': -99})

      clrTbl = self.dut.dblData.Tables( P172_AFH_CLEARANCE_tableName ).tableDataObj()

      for head in xrange(self.dut.imaxHead):
         #Iterate over all zones including the system zone as each data structure accounts for it
         for zone in xrange(self.dut.numZones+1):
            #Decrease the measured read clearance so less heat is applied
            # adjustment value should come out as a negative number
            if percent:
               adjustVal_rd = float(afhZoneTargets['TGT_PREWRT_CLR'][zone])*(self.swdAdjustDict[head][zone][self.RDCLR_PERC_OFFSET]/float(100.0))
               adjustVal_wr = float(afhZoneTargets['TGT_WRT_CLR'][zone])*(self.swdAdjustDict[head][zone][self.WRTCLR_PERC_OFFSET]/float(100.0))

            if testSwitch.extern.FE_0144956_009410_T227_DUAL_HEATER == 1:
               if adjustVal_wr == 0:
                  continue #skip the clearance adjust if there is no adjustment to make

            if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT == 1:
               if testSwitch.extern.FE_0144956_009410_T227_DUAL_HEATER == 1:
                  rdClrColumnName = 'PRE_HEAT_CLRNC'
                  wrtClrColumnName = 'WRT_HEAT_CLRNC'
               else:
                  rdClrColumnName = 'READ_HEAT_CLRNC'
                  wrtClrColumnName = 'WRT_HEAT_CLRNC'
            else:
               rdClrColumnName = 'HEAT_CLRNC'
               wrtClrColumnName = 'WRT_HEAT_CLRNC'

            rdClr  = float(self.dth.getRowFromTable(clrTbl, head, zone)[rdClrColumnName]) / 254.0
            wrtClr = float(self.dth.getRowFromTable(clrTbl, head, zone)[wrtClrColumnName]) / 254.0

            newRdClr = rdClr + adjustVal_rd
            newWrtClr = wrtClr + adjustVal_wr

            self.setContactClr(zone, head, newWrtClr, newRdClr)

            if (adjustVal_rd > (getattr(TP, 'deltaRdAdj', .32) * rdClr  )) or \
               (adjustVal_rd > (getattr(TP, 'deltaWrtAdj', .32) * wrtClr)):
               self.dut.stateTransitionEvent = 'reRunVBAR'

      if self.dut.stateTransitionEvent == 'reRunVBAR':
         # Check to make sure we haven't exceeded our VBAR rerun limit
         self.dut.rerunVbar += 1
         self.dut.objData.update({'RERUN_VBAR':self.dut.rerunVbar})
         if self.dut.rerunVbar > 1:
            import ScrCmds
            ScrCmds.raiseException(14799, "Attempting to start restart VBAR more than once. Fail to avoid infinite loop")

   #-------------------------------------------------------------------------------------------------------
   def swdDictUpd(self, head, zone, \
      temperature, RdClr_delta, WrtClr_delta, RdClr_perc, WrtClr_perc):
      """
      Structure is list of lists for storage with indicies as the

      """
      if temperature == None:
         numRetry = 0
         temperature = self.temp.retHDATemp(0, numRetry, TP.tempDiodeMultRtry['driveTempDiodeRangeLimit'])
      if len(self.swdAdjustDict.get(head, {})) == 0:
         self.swdAdjustDict[head] = {}
      self.swdAdjustDict[head][zone] = array('f', [temperature, RdClr_delta, WrtClr_delta, RdClr_perc, WrtClr_perc])

   #-------------------------------------------------------------------------------------------------------
   def createSWDAdjustTable(self):
      for head in xrange(self.dut.imaxHead):
         for zone in self.swdAdjustDict[head].keys():
            self.dut.dblData.Tables('P_SWD_ADJUSTMENT').addRecord(
                  {
                  'HD_PHYS_PSN':          self.dut.LgcToPhysHdMap[int(head)],
                  'DATA_ZONE':            int(zone),
                  'SPC_ID':               self.dut.objSeq.curRegSPCID,
                  'OCCURRENCE':           self.dut.objSeq.getOccurrence(),
                  'SEQ':                  self.dut.objSeq.curSeq,
                  'TEST_SEQ_EVENT':       self.dut.objSeq.getTestSeqEvent(227),
                  'HD_LGC_PSN':           int(head),
                  'DIODE_TEMP':           self.swdAdjustDict[head][zone][self.TEMPERATURE_OFFSET],
                  'RD_CLR_ADJ':         self.oUtility.setDBPrecision(self.swdAdjustDict[head][zone][self.RDCLR_DELTA_OFFSET],8,5),
                  'WRT_CLR_ADJ':        self.oUtility.setDBPrecision(self.swdAdjustDict[head][zone][self.WRTCLR_DELTA_OFFSET],8,5),
                  'RD_CLR_ADJ_PCT':     self.oUtility.setDBPrecision(self.swdAdjustDict[head][zone][self.RDCLR_PERC_OFFSET],6,2),
                  'WRT_CLR_ADJ_PCT':    self.oUtility.setDBPrecision(self.swdAdjustDict[head][zone][self.WRTCLR_PERC_OFFSET],6,2),
                  })
      objMsg.printMsg(self.dut.dblData.Tables('P_SWD_ADJUSTMENT'))

   #-------------------------------------------------------------------------------------------------------
   def setContactClr( self, zone, head, WH, RH ):
      if DEBUG == 1:
         objMsg.printMsg("zone: %s, head: %s, WH Clr: %s, RH Clr: %s" % (str(zone), str(head), str(WH), str(RH)))

      #Detect if we have a type issue before calling the St API which can't handle type defects.
      if type(WH) == types.StringType or \
         type(RH) == types.StringType:
         WH = float(WH)
         RH = float(RH)
         zone_mask_low = 0
         zone_mask_high = 0
         if zone < 32:
             zone_mask_low |= (1 << zone)
         else:
             zone_mask_high |= (1 << (zone - 32))

      self.St({
        'test_num':178,
        'prm_name': 'Set Contact Pts',
        'CWORD1': 0x2200,
        'CWORD2': 0x1800,
        'HEAD_RANGE':(2**head),
        #'BIT_MASK': self.oUtility.ReturnTestCylWord(2**zone),
        'BIT_MASK': self.oUtility.ReturnTestCylWord(zone_mask_low),
        'BIT_MASK_EXT': self.oUtility.ReturnTestCylWord(zone_mask_high),
        'MEASURED_HEAT_CLR':int(round(RH*AFH_ANGSTROMS_PER_MICROINCH)),
        'MEASURED_WRT_HEAT_CLR':int(round(WH*AFH_ANGSTROMS_PER_MICROINCH)),
      })
