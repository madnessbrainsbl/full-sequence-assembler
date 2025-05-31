#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Error handling functionality
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/IntfErrorHandle.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/IntfErrorHandle.py#1 $
# Level:3
from Constants import *

import ScrCmds
import MessageHandler as objMsg


class CIntfErrorHandle:
   """
   Handles different error modes and sets appropriate failure codes
   """
   def __init__(self, dut):
      self.dut = dut

   def handleWriteFailure(self,data):
      """
      Indicates failure mode of all CPC write commands based on error and status register returned by CPC command
      @param status: string of 2 digits (=8 bit register value in decimal)
      @param error: string of 2 digits (=8 bit register value in decimal)
      @return: NULL
      """
      status = int(data['STS'])
      error = int(data['ERR'])

      error_found = 0

      if ((status & 1) == 1) and ((error & 128) == 1):
         objMsg.printMsg("CRC Write Failure")
         ScrCmds.raiseException(13410, "CRC Write error: %s" % str(data))
         error_found = 1

      if ((status & 1) == 1) and ((error & 16) == 1):
         objMsg.printMsg("Write address outside user-accessible range of addresses")
         ScrCmds.raiseException(13411, "Write IDNF bit set %s" % str(data))
         error_found = 1

      if ((status & 1) == 1) and ((error & 4) == 1):
         objMsg.printMsg("Write Command aborted")
         ScrCmds.raiseException(13412, "ABRT bit set %s" % str(data))
         error_found = 1

      if error_found == 0:
         objMsg.printMsg("Undetermined write failure")
         ScrCmds.raiseException(13413, "Undetermined write error %s" % str(data))

      return

   #-------------------------------------------------------------------------------------------------------#

   def handleReadFailure(self,data):
      """
      Indicates failure mode of all CPC read commands based on error and status register returned by CPC command
      @param status: string of 2 digits (=8 bit register value in decimal)
      @param error: string of 2 digits (=8 bit register value in decimal)
      @return: NULL
      """

      status = int(data['STS'])
      error = int(data['ERR'])

      error_found = 0

      if ((status & 1) == 1) and ((error & 128) == 1):
         objMsg.printMsg("CRC read Failure")
         ScrCmds.raiseException(13414, "CRC read error %s" % str(data))
         error_found = 1

      if ((status & 1) == 1) and ((error & 64) == 1):
         objMsg.printmsg("Uncorrectable data during read")
         ScrCmds.raiseException(13415, "UNC error bit set %s" % str(data))
         error_found = 1

      if ((status & 1) == 1) and ((error & 16) == 1):
         objMsg.printMsg("Read address outside user-accessible range of addresses")
         ScrCmds.raiseException(13416, "IDNF error bit set %s" % str(data))
         error_found = 1

      if ((status & 1) == 1) and ((error & 4) == 1):
         objMsg.printMsg("Read Command aborted")
         ScrCmds.raiseException(13417, "ABRT error bit set %s" % str(data) )
         error_found = 1

      if error_found == 0:
         objMsg.printMsg("Undetermined read failure")
         ScrCmds.raiseException(13418, "Undetermined read error %s" % str(data))

      return
