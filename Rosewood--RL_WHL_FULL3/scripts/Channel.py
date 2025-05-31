#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Read Write Module
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Channel.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Channel.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
import traceback
import MessageHandler as objMsg
from Drive import objDut
from Process import CCudacom
import struct


class CChannelAccess(CCudacom):
   """
   Class for accessing channel register values.
      The class reads in the channel type from TestParameters and imports the channel registers dictionary
      from channelRegs.py. The dictionary is the reference by PN in TestParameters.
      Example in TestParameters: channelType = {'9BD':'AGERE'}
   """

   SOC_Lookup_Table = {
         0x6489: 'YETI_1.0',
         0x6491: 'YETI_2.0',
         0x6499: 'YETI_3.0',
         0x649b: 'YETI_3.2',
         0x63A0: 'TETON_4.0',
         0x63A2: 'TETON_4.2',
         0x6689: 'SPHINX_2.0',
         0x6789: 'SPHINX_12.0',
         0x0100: 'BANSHEE_1.0',
         0x0200: 'BANSHEE_2.0',
         0x5A92: 'LUXORM92',
         0xA653: 'LUXORM9311'
      }

   def __init__(self):
      self.dut = objDut
      self.channelName = self.dut.channelType
      self.chRegs = {}
      self.importChannelRegs()


   def importChannelRegs(self):
      try:
         exec('from channelRegs import %s as chRegs' % str(self.channelName))
         self.chRegs = chRegs
      except:
         self.chRegs = {}


   def setChannelType(self):
      try:
         self.dut.channelType = self.dut.dblData.Tables('P166_CHANNEL_INFO').tableDataObj()[-1]['MFGR_REV'].replace('"','')
         self.dut.dblData.delTable('P166_CHANNEL_INFO')

      except:
         objMsg.printMsg("Unable to detect channel type from P166_CHANNEL_INFO\n%s" % traceback.format_exc())

   def setSOCType(self):
      try:
         socReg = int(self.dut.dblData.Tables('P166_CONTROLLER_REV').tableDataObj()[-1]['REV_REGISTER'].replace('"',''),16)

         self.dut.SOCType = self.SOC_Lookup_Table.get(socReg, None)#'TETON_4.0')
         objMsg.printMsg("SOC %s detected." % self.dut.SOCType)

         self.dut.dblData.delTable('P166_CONTROLLER_REV')
      except:
         objMsg.printMsg("Unable to detect SOC revision from P166_CONTROLLER_REV\n%s" % traceback.format_exc())


   def getMask(self,reg, min, max):
      """
      Retrieve the register value as masked in a field value
      @param val: full register value
      @param min: starting mask bit
      @param max: ending mask bit
      """
      #objMsg.printMsg(str(reg))
      mask = 0
      count = 0
      for x in range(min,max+1):
         if reg & 2**x == 2**x:
            mask = mask + 2**count
         count +=1
      return mask


   def rdChVal(self, regName, default = 15):
      try:
         regVal = self.readChannel(self.chRegs[regName]['reg'])
      except:
         objMsg.printMsg("Err discovered... Using default = %s" % str(default))
         regVal = default
      chVal = self.getMask(regVal, self.chRegs[regName]['min'],self.chRegs[regName]['max'])
      return chVal


   def wrChVal(self, regName, writeData):
      curVal = self.readChannel(self.chRegs[regName]['reg'])
      min = self.chRegs[regName]['min']
      max = self.chRegs[regName]['max']

      hi = self.getMask(curVal,max+1,16) << max + 1
      lo = self.getMask(curVal,0,min-1) << min + 1

      writeVal = hi | lo | (writeData << min)
      regVal = self.writeChannel(self.chRegs[regName]['reg'], writeVal ) #used to be writeData >>self.chRegs[regName]['min']
      chVal = self.getMask(regVal, self.chRegs[regName]['min'],self.chRegs[regName]['max'])
      return chVal


   def readChannel(self, register, bank = 0):
      """
      Read and return Channel register
      @param register: Channel register to read
      @return: Channel Value, Error code
      """
      buf, errorCode = self.Fn(1308, (bank | register))
      return struct.unpack('>H',buf)[0]


   def writeChannel(self, register, writeData, bank = 0):
      """
      Write Channel register(s)
      Optional 3rd & 4th arguments will write a 2nd channel register.
      @param Address: Channel register to write
      @param Data: Data written to channel address.
      [@param Address2]: 2nd channel register to write
      [@param Data2]: Data written to channel 2nd address.
      @return: Error code
      """
      buf, errorCode = self.Fn(1269, (bank | register), writeData)
      return struct.unpack('>H',buf)[0]


   def ReadCLParm(self, listid, regadrs, shiftval, maskval):
      """
      Read channel parameter from selected channel list.
      Note: Refer to channelSetupLists.c for specific
      list and parameter values.
      @param Channel list ID (index)
      @param Channel register address
      @param Parameter shift value (0, 1, 2, 3, ...)
      @param Parameter mask (1, 3, 5, 7, ...)
      @return Parameter value currently stored in channel list, error code
      """
      buf, errorCode = self.Fn(1359, 0, listid, regadrs, shiftval, maskval)
      return buf, errorCode


   def WriteCLParm(self,listid, regadrs, shiftval, maskval, newval):
      """
      Write channel parameter to selected channel list.
      Note: Refer to channelSetupLists.c for specific
      list and parameter values.

      @param Channel list ID (index)
      @param Channel register address
      @param Parameter shift value (0, 1, 2, 3, ...)
      @param Parameter mask (1, 3, 5, 7, ...)
      @param Parameter value to be stored in channel list
      """
      buf, errorCode = self.Fn(1359, 1, listid, regadrs, shiftval, maskval, newval)
      return errorCode
