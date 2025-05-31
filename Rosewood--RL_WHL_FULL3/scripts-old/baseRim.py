#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: The Rim object is an abstraction of the cell RIM and implements methods to implement
#              to power on/off rim, download CPC/NIOS/Serial code etc.
#              Note that only once instance of rim must exist in the entire test environment.
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/baseRim.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/baseRim.py#1 $
# Level: 4
#---------------------------------------------------------------------------------------------------------#

from Constants import *
from Test_Switches import testSwitch
from Exceptions import CReplugException, BaudRateRejected

import MessageHandler as objMsg
import ScrCmds
import struct
import traceback

BASE_BAUD_LIST = (Baud38400, Baud115200, Baud390000, Baud460800, Baud625000, Baud921600, Baud1228000)

from UartCls import theUart
PRIMARY = 1
SECONDARY = 2

class baseCRim(object):
   def __init__(self, objRimType):
      self.Unlock = None
      self.objRimType = objRimType
      self.workingBaudString = PRIMARY

   def validateCellStatus(self):
      if not IsDrivePlugged():
         if ConfigVars[CN].get('ReplugEnabled',0):
            raise CReplugException
         else:
            ScrCmds.raiseException(11045, "Drive not plugged" )

   #------------------------------------------------------------------------------------------------------#
   def powerCycleRim(self, offTime = 10, onTime = 1):
      self.RimOff(offTime)
      self.RimOn(onTime)

   def RimOff(self, offTime = 10):
      theUart.setBaud(DEF_BAUD)

   def RimOn(self, onTime = 1):
      pass

   #------------------------------------------------------------------------------------------------------#
   def getValidRim_IOSpeedList(self):
      """
      Returns the valid speeds in Gbs that this rim supports
      Possibilities are [1, 3, 6, 12]
      """
      if testSwitch.virtualRun:
         return [1, 3, 6, 12]
      else:
         return [ speed for speed in [1, 3, 6, 12] if speed <= int(riserExtension[4],16)]

   #------------------------------------------------------------------------------------------------------#
   def base_getValidRimBaudList(self, baudRate, cellBaudList):
      """
      base function to return valid baud rates for rim
      """
      if testSwitch.winFOF:
         cellBaudList = BASE_BAUD_LIST

      if not baudRate in cellBaudList:
         #Override to universal support
         baudRate = Baud115200

      return cellBaudList, baudRate

   #------------------------------------------------------------------------------------------------------#
   def initRim(self):
      """
      initRim of baseCRim must be overridden for a valid rim class implementation
      """
      ScrCmds.trcBanner("ERROR - ERROR - INVALID RIM TYPE!!")
      ScrCmds.underLineTrace("   Could not find RIM Type '%s' in any of the following lists:" % riserType)
      TraceMessage  ("   Serial -> %s" % str(self.objRimType.SerialOnlyRiserList()))
      TraceMessage  ("   CPC    -> %s" % str(self.objRimType.CPCRiserList()))
      TraceMessage  ("   IOInit -> %s" % str(self.objRimType.IOInitRiserList()))
      ScrCmds.trcBanner()
      TraceMessage  ("   Make sure the proper RIM Type has been programmed into the EEPROM!!")
      TraceMessage  ("   If this is a new RIM type you must update the appropriate list in CellLists.py!!")
      TraceMessage  ("   NOTE:  You will probably also need updated CM code!!")
      TraceMessage  ("          Contact Seagate for updated CM code!!")
      ScrCmds.trcBanner     ("CELL FAILED")
      ScrCmds.raiseException(11187, "RIMType not found in SerialOnly/CPC/IOInit list")

   def DisableInitiatorCommunication(self, comModeObj = None, failCommRetries = True):
      pass

   def EnableInitiatorCommunication(self, comModeObj = None):
      pass

   def eslipToggleRetry(self, setACKOff = False):
      pass

   def eslipBaudCmd(self, baudString):
      self.base_eslipBaudCmd(baudString)

   #------------------------------------------------------------------------------------------------------#
   def base_eslipBaudCmd(self, baudString):

      if testSwitch.FE_0112289_231166_REMOVE_INEFFICIENT_RETRIES_IN_ESLIP_BAUD_RETRIES:
         try:
            try:
               UseHardSRQ(0)
               if testSwitch.BF_0152393_231166_P_RE_ADD_LEGACY_ESLIP_PORT_INCR_TMO:
                  #MCT from-to... also supported by F3 but invalid in some modes
                  if self.workingBaudString == PRIMARY:
                     SendBuffer(baudString, fromAddress=0x8001, toAddress=0x8002, checkSRQ=0, timeout=baudSet_timeout)
                     res = ReceiveBuffer(fromAddress=0x8002, toAddress=0x8001, timeout=baudSet_timeout, checkSRQ=1)
                  elif self.workingBaudString == SECONDARY:
                     #Works in F3 most of the time but not in MCT... use on exception
                     SendBuffer(baudString, fromAddress=0x8001, toAddress=0x8001, checkSRQ=0, timeout=baudSet_timeout)
                     res = ReceiveBuffer(fromAddress=0x8001, toAddress=0x8001, timeout=baudSet_timeout, checkSRQ=2)
               else:
                  SendBuffer(baudString, fromAddress=0x8001, toAddress=0x8002, checkSRQ=0, timeout=30)
                  res = ReceiveBuffer(fromAddress=0x8002, toAddress=0x8001, timeout=30, checkSRQ=1)

            except:
               if testSwitch.BF_0152393_231166_P_RE_ADD_LEGACY_ESLIP_PORT_INCR_TMO:
                  if self.workingBaudString == PRIMARY:
                     self.workingBaudString = SECONDARY
                  else:
                     self.workingBaudString = PRIMARY

               if DEBUG:
                  objMsg.printMsg(traceback.format_exc())
               raise
         except:
            if DEBUG:
               objMsg.printMsg(traceback.format_exc())
            raise
      else:
         try:
            #MCT from-to... also supported by F3 but invalid in some modes
            SendBuffer(baudString, fromAddress=0x8001, toAddress=0x8002, checkSRQ=0, timeout=2)
            res = ReceiveBuffer(fromAddress=0x8002, toAddress=0x8001, timeout=2, checkSRQ=1)
         except:
            if not (cellTypeString == 'Neptune2' and testSwitch.FE_0163145_470833_P_NEPTUNE_SUPPORT_PROC_CTRL20_21):
               #Works in F3 most of the time but not in MCT... use on exception
               SendBuffer(baudString, fromAddress=0x8001, toAddress=0x8001, checkSRQ=0, timeout=2)
               res = ReceiveBuffer(fromAddress=0x8001, toAddress=0x8001, timeout=2, checkSRQ=2)
            else:
               raise

      if testSwitch.virtualRun:
         return res

      returnData = struct.unpack('HH', res[:struct.calcsize('HH')])
      if not returnData[1] in [0x1003, 0x1001, 0x0310]:# add 0x0310 for Hurricane (byte swap issue with branch)
         objMsg.printMsg("WARNING: Drive reported non-standard baud message.")
         objMsg.printMsg("Baud Return Data(raw)   : %s" % repr(res))
         objMsg.printMsg("Baud Return Data(parsed): %s" % (returnData,))

         ScrCmds.raiseException(10149, "Drive rejected baud request.", BaudRateRejected)

      if DEBUG and testSwitch.FE_0112289_231166_REMOVE_INEFFICIENT_RETRIES_IN_ESLIP_BAUD_RETRIES:
         objMsg.printMsg("Received %s from drive" % repr(returnData))

      return res
