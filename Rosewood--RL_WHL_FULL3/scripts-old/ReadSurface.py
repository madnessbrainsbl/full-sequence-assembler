#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
#---------------------------------------------------------------------------------------------------------#
# Description: will perform Read Surface test after Write only serial format
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/ReadSurface.py $
# $Revision: #1 $
# $Change: 1047653 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/ReadSurface.py#1 $
# Level: Product

#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
import types, os, time, re
from State import CState
import MessageHandler as objMsg
from PowerControl import objPwrCtrl
import ScrCmds

from AFH_constants import *

from AUTOFA import *



###########################################################################################################
###########################################################################################################
class CReadSurface(CState):
   """
      Description: Class that will perform Read Surface test after Write only serial format
      Base: N/A
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      objMsg.printMsg("Start Read Full Surface")

      if testSwitch.virtualRun:
         objMsg.printMsg("Skip Read Full Surface for VE")
         return

      MCPartitionPattern_2x0 = 'Media\sCache\sPartition.*?\s+LBAs\s(?P<MC_START_LBA>[a-fA-F\d]+)-(?P<MC_END_LBA>[a-fA-F\d]+)'
      MCPartitionPattern_CU  = 'Media\sPartition\sStart.*?\s+Overall.*?\s(?P<MC_START_LBA>[a-fA-F\d]+).*?\s(?P<MC_END_LBA>[a-fA-F\d]+)'
      MaxLBA = 0

      import serialScreen, sptCmds

      oSerial = serialScreen.sptDiagCmds()
      oSerial.enableDiags()

      sptCmds.gotoLevel('2')                      # Set default error recovery mode
      sptCmds.sendDiagCmd('Y0',  timeout = 100, printResult = True)

      oSerial.ToggleRwTracing(error = False, command = False, retry = False)

      sptCmds.gotoLevel('2')                      # Get MediaCacheLBA and MaxLBA
      zoneInfo = sptCmds.sendDiagCmd('x0,0,0,11',  timeout = 100, printResult = True)

      data1 = zoneInfo.replace("\n"," ")
      match = re.search(MCPartitionPattern_2x0, data1)
      if not match:
         sptCmds.gotoLevel('C')                      # Get MediaCacheLBA and MaxLBA
         zoneInfo = sptCmds.sendDiagCmd('U',  timeout = 100, printResult = True)
   
         data1 = zoneInfo.replace("\n"," ")
         match = re.search(MCPartitionPattern_CU, data1)

      if match:
         try:
            tempDict = match.groupdict()
            tempDict = oSerial.convDictItems(tempDict, int, [16,])
            MediaCacheLBA = tempDict['MC_START_LBA']
            MaxLBA        = tempDict['MC_END_LBA']
         except:
            print "fail to try convert MC partition"
            ScrCmds.raiseException(11044,'Read Surface Failed(get MediaCacheLBA, MaxLBA failed)')
      else:
         print "fail to try find MC partition"
         ScrCmds.raiseException(11044,'Read Surface Failed(get MediaCacheLBA, MaxLBA failed)')

##      if MaxLBA == 0:
##         offset = zoneInfo.find('Media Cache Partition')
##         try:
##            MediaCacheLBA = int(zoneInfo[offset+31:offset+43], 16)
##            MaxLBA = int(zoneInfo[offset+44:offset+56], 16)
##         except ValueError:
##            ScrCmds.raiseException(11044,'Read Surface Failed(get MediaCacheLBA, MaxLBA failed)')

      print "MediaCacheLBA = %s MaxLBA = %s"%(MediaCacheLBA,MaxLBA)

      sptCmds.gotoLevel('A')                      # run Read Surface

      objMsg.printMsg("Read Track based Parity area")
      data = sptCmds.sendDiagCmd('R0,%X,,1'%(MediaCacheLBA),  stopOnError = False, timeout = 6000*TP.numHeads, printResult = True)
      offset = data.find('R/W Error ')
      if offset >= 0:
         ErrorCode = data[offset+10:offset+18]
         objMsg.printMsg("Script Captured EC:%s" % (ErrorCode))
#         ScrCmds.raiseException(13081,'Read Surface Failed')

## Skip ISO based Parity area (MC area) for GEN1A
##      objMsg.printMsg("Read ISO based Parity area")
##      data = sptCmds.sendDiagCmd('R%X,%X,,1'%(MediaCacheLBA, MaxLBA - MediaCacheLBA),  stopOnError = False, timeout = 3600*5, printResult = True)
##      offset = data.find('R/W Error ')
##      if offset >= 0:
##         ErrorCode = data[offset+10:offset+18]
##         objMsg.printMsg("Script Captured EC:%s" % (ErrorCode))
###         ScrCmds.raiseException(13081,'Read Surface Failed')

      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

      objMsg.printMsg("Done Read Full Surface")
###########################################################################################################

