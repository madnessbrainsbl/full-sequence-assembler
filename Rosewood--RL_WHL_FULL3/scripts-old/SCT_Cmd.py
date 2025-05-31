#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# $RCSfile: IntfClass.py,v $
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/SCT_Cmd.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/SCT_Cmd.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#

from Constants import *
import ScrCmds, re
from Rim import objRimType
import MessageHandler as objMsg
from Drive import objDut   # usage is objDut
from TestParamExtractor import TP

from ICmdFactory import ICmd
from Utility import CUtility

DEBUG = 0


from IntfClass import CInterface
oIntf = CInterface()


def SetSctValue(actionCode, functionCode, value = None, byteOffset = (0,0), retStatus = None):
   """
   Execute the SCT command using the actioncode and functioncode provided
   Optional is the tuple value, offset to indicate a value to set in write buffer
   Optional is the retStatus to dump the 0xE0 smart log after the command
   """

   ret = ''
   oIntf.writeUniformPatternToBuffer('write')  #write one sector of zeros

   #update byteOffset 0 to indicate BIST command and update byteOffset 2 to indicate speed control mode
   oIntf.writeBytesToBuffer((actionCode, functionCode))
   if value != None:
      oIntf.writeBytesToBuffer(value, byteOffset = offset)

   oIntf.displayBuffer('write')

   try:
      objMsg.printMsg("Issuing SCT command")
      oIntf.WriteOrReadSmartLog(0xe0,'write')
      ######################################
   finally:
      if retStatus:
         oIntf.WriteOrReadSmartLog(0xe0,'read')
         ret = oIntf.displayBuffer('read' , numBytes = 512, byteOffset = (0,0), sendToFile = False)

   return ret

def VerifyMC():
   try:
      ICmd.SetIntfTimeout(240*1000)
      ret = SetSctValue(0x08c0, 0x0501, retStatus = True)
   finally:
      ICmd.SetIntfTimeout(TP.prm_IntfTest["Default CPC Cmd Timeout"]*1000)
   return ret

def SetBistSpeed(speed):
   return SetSctValue(0x0700, 0x0300, value = (speed, 0x0000), byteOffset = (0, 0x1C), retStatus = True)
