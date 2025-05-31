#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2011, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Diagnostics External Test Service (DETS) Function Collection
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2011 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/DETS.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/DETS.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#

from Constants import *
from Process import CProcess
import MessageHandler as objMsg
from ICmdFactory import ICmd
import re
from Utility import CUtility

DEBUG = 0
REVISION_ID = 0x0100    # Rev 1 (Big Endian)

if DEBUG:
   SUPPRESS_OPTION = 0
else:
   SUPPRESS_OPTION = ST_SUPPRESS__ALL

wordTuple = CUtility.ReturnTestCylWord

class CDETS(object):
   def __init__(self, dut):
      self.oProcess = CProcess()
      self.dut = dut
      self.bcol = re.compile('^\d[\da-fA-F]')

   def extractBufferDblog(self, buffDict):
      """
         Extract DBLog buffer.
         @type buffDict: dictionary
         @param buffDict: DBLog buffer
         @return data: string of hexadecimal buffer
         Input:
            [
               {'OCCURRENCE': 12, 'SPC_ID': None, '0B': '4E', '0C': '30', '0A': '41', '0F': '30', '0D': '30', '0E': '30', 'TEST_SEQ_EVENT': 3, '04': '51', '02': 'FF', '03': 'FF', '00': 'FF', '01': 'FF', '06': '5A', '07': '30', 'SEQ': 0, '05': '30', '08': '30', '09': '50', 'ADDRESS': '0'}, 
            ]
         Output:
            "FFFFFFFF51305A303050414E30303030"
      """
      data = ''
      for row in buffDict:
         for key in sorted(row.keys()):
            if self.bcol.match(key):
               try:
                  data += row[key]
               except:
                  objMsg.printMsg("Error: data:'%s' ; val: '%s', key: '%s'" % (data, row[key], key))
                  raise
      return data

   @staticmethod
   def enableOnlineModeRequests():
      prm_T638_enableOnlineModeRequests = {
         'test_num'           : 638,
         'prm_name'           : 'prm_T638_enableOnlineModeRequests',
         'stSuppressResults'  : SUPPRESS_OPTION,
         'CTRL_WORD1'         : 0x0008, # Command Supplied is a DETS Command
         'DFB_WORD_0'         : 0x0100, # 0x0001      : FunctionId (Enable Online Mode Requests)
         'DFB_WORD_1'         : REVISION_ID,
      }
      oProcess = CProcess()
      oProcess.St(prm_T638_enableOnlineModeRequests, timeout=10)

   @staticmethod
   def disableOnlineModeRequests():
      prm_T638_disableOnlineModeRequests = {
         'test_num'           : 638,
         'prm_name'           : 'prm_T638_disableOnlineModeRequests',
         'stSuppressResults'  : SUPPRESS_OPTION,
         'CTRL_WORD1'         : 0x0008, # Command Supplied is a DETS Command
         'DFB_WORD_0'         : 0x0200, # 0x0002      : FunctionId (Disable Online Mode Requests)
         'DFB_WORD_1'         : REVISION_ID,
      }
      oProcess = CProcess()
      oProcess.St(prm_T638_disableOnlineModeRequests, timeout=10)
   
   def sendDETS(self, cmd = "", receiveLength = 1024):
      """
      070007004403000055000200000000005941343138412E53444D312E4341303536302E3030
      303153444D310000000000002D2D2D2D2D2D2D2D2D00000000000000000000000000000000
      00000000000000003834000000000000000000000000000000000000000000000000000000
      0000000031322F32312F323031310000000000000000000000000000000000000000000000
      31313A33373A34330000000000000000000000000000000000000000000000000059413431
      2E53444D312E30303431353834352E38343030000000000000000000004138323300000000
      000000000000000000000000000000000000000000000000002D2D2D2D0000000000000000
      0000000000000000000000000000000000000000002D2D2D2D000000000000000000000000
      00000000000000000000000000000000002D2D2D2D00000000000000000000000000000000
      000000000000000000000000000059415252414250204C4D39335F315F3120534552564F32
      353620524150323220346B205642415220535444204D6F62696C0000000000000000000000
      000000005F0E51305430303242390000000000000000000000000000000000000000000000
      00B0420020150001010000002E8BA3033030303053323234355A4838000000000000000000
      00000000000000000000004C55584F524D39335F315F312846464646292846462D46462D46
      462D46462900FFFF00004D415256454C4C5F39333131000000000000000000000000000000
      00000000004D434B494E4C4559204D4F42494C4520504C5553000000000000000000000000
      150000000000000131322F32312F3230313100000000000000000000000000000000000000
      00000031313337343300000000000000000000000000000000000000000000000000003030
      303830363033000000000000000000000000000000000000000000000000594134312E5344
      4D310000000000000000000000000000000000000000000000303034313538343500000000
      00000000000000000000000000000000000000003035363030303031000000000000000000
      00000000000000000000000000000030303031000000000000000000000000000000000000
      000000000000000000004CA40116025D400204050101010101010101010000000000000000
      00000000000000000000000000
      """      
      res = ICmd.PutBuffByte(WBF, cmd, 0)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(12345, "PutBuffByte is fail")
   
      prm_T538_sendSDBPPacketCommand = {
         'test_num'           : 538,
         'prm_name'           : 'prm_T538_sendSDBPPacketCommand',
         'stSuppressResults'  : SUPPRESS_OPTION,
         'FEATURES'           : 0x00,
         'SECTOR_COUNT'       : 1,
         'LBA_LOW'            : 0x00BE,
         'LBA_MID'            : 0x2459,
         'LBA_HIGH'           : 0x0000,
         'COMMAND'            : 0x3F,
         'PARAMETER_0'        : 0x2000,
         'DEVICE'             : 0x40,
      }           
      self.oProcess.St(prm_T538_sendSDBPPacketCommand, timeout=10)

      prm_T538_retrieveSDBPPacketCommand = {
         'test_num'           : 538,
         'prm_name'           : 'prm_T538_retrieveSDBPPacketCommand',
         'stSuppressResults'  : SUPPRESS_OPTION,
         'FEATURES'           : 0x00,
         'SECTOR_COUNT'       : 2,
         'LBA_LOW'            : 0x00BF,
         'LBA_MID'            : 0x2459,
         'LBA_HIGH'           : 0x0000,
         'COMMAND'            : 0x2F,
         'PARAMETER_0'        : 0x2000,
         'DEVICE'             : 0x40,
      }           
      self.oProcess.St(prm_T538_retrieveSDBPPacketCommand, timeout=10)
      
      prm_T508_getReadBuffer = {
         'test_num'           : 508,
         'prm_name'           : 'prm_T508_getReadBuffer',
         'DblTablesToParse'   : ['P508_BUFFER_DATA',],
         'stSuppressResults'  : SUPPRESS_OPTION,
         'CTRL_WORD1'         : (0x0005,),
         'BUFFER_LENGTH'      : wordTuple(receiveLength),
      }
      self.oProcess.St(prm_T508_getReadBuffer, timeout=10)
      
      if testSwitch.virtualRun:
         return self.sendDETS.__doc__
      return self.extractBufferDblog(self.dut.objSeq.SuprsDblObject['P508_BUFFER_DATA'])

   # Basic Drive Information
   def getBasicDriveInformation(self):
      return self.CBasicDriveInformation(self.sendDETS("070007000400000080000100", 856))

   class CBasicDriveInformation(str):
      def getFirmwarePackageInfo(self):
         """
            Get firmware package information
            @return firmwarePackageInfo: string of characters
            Example result: "YA418A.SDM1.CA0568.0001SDM1"
         """
         # Firmware Package Info is at offset 16 to 48
         return self[32:98].split('00')[0].decode("hex")
      def getServoFirmwareRev(self):
         """
            Get servo firmware revision
            @return servoFirmwareRev: little-endian string of hexadecimal characters
            Example result: "A453"
         """
         # Servo Firmware Revision is at offset 824 and 825 (little endian)
         # offset 833 for AngsanaH
         if testSwitch.KARNAK:
            return CUtility.convertEndianStrHexChar(self[1666:1670])
         else:
            return CUtility.convertEndianStrHexChar(self[1648:1652])
      def getUdr2Info(self):
         """
            Get UDR2 information
            @return udr2Info: hexadecimal characters
            Example result: "00"
         """
         if testSwitch.virtualRun:
            return CUtility.convertEndianStrHexChar(self[1684:1686])
         # UDR2 information is at offset 842 (0x34A)
         # offset 850 for AngsanaH and Chengai
         if (testSwitch.KARNAK or testSwitch.CHENGAI or testSwitch.M10P):
            return CUtility.convertEndianStrHexChar(self[1708:1710])
         else:
            return CUtility.convertEndianStrHexChar(self[1684:1686])

   # Hardware Jumper Setting
   def getHardwareJumperSetting(self):
      return self.CHardwareJumperSetting(self.sendDETS("0700070008000000C700010000000000", 24))

   class CHardwareJumperSetting(str):
      def getJumperInstalled(self):
         """
            Get hardware jumper setting
            @return jumperInstalled: little-endian string of hexadecimal characters
            Example result: "00000000"
         """
         # Jumper Installed information is at offset 20 to 23
         return CUtility.convertEndianStrHexChar(self[40:48])

   # R/W Zone Information
   def getRWZoneInformation(self):
      return self.CRWZoneInformation(self.sendDETS("0700070004000000BF000100", 220))

   class CRWZoneInformation(str):
      def getNumUserZones(self):
         """
            Get number of user zones
            @return numUserZones: little-endian string of hexadecimal characters
            Example result: "00000060"
         """
         # Number of User Zones is at offset 16 to 19
         return CUtility.convertEndianStrHexChar(self[32:40])

