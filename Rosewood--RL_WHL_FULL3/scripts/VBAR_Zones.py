#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Vbar Tools Module
#  - Contains Vbar tools classes for Internal / External VBAR use
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
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/VBAR_Zones.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/VBAR_Zones.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
from Drive import objDut
from DesignPatterns import Singleton
import MessageHandler as objMsg
from FSO import CFSO
from VBAR_Constants import *


#----------------------------------------------------------------------------------------------------------
class CVbarTestZones(Singleton):
   #-------------------------------------------------------------------------------------------------------
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

      mFSO = CFSO()
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

   #-------------------------------------------------------------------------------------------------------
   def getTestZones(self):
      return self.testZones # list

   #-------------------------------------------------------------------------------------------------------
   def getTestZoneMap(self):
      return self.zoneMap # dict

   #-------------------------------------------------------------------------------------------------------
   def getTestZnforZn(self, zone):
      for zn in self.zoneMap:
         if zone in self.zoneMap[zn]:
            return zn
