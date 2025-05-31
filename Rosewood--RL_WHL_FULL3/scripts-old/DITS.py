#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2011, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Diagnostics Internal Test Service (DITS) Function Collection
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2011 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/DITS.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/DITS.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#

from Constants import *
from Process import CProcess
import MessageHandler as objMsg
from Rim import objRimType
import re

DEBUG = 0
REVISION_ID = 0x0100    # Rev 1 (Big Endian)

if DEBUG:
   SUPPRESS_OPTION = 0
else:
   SUPPRESS_OPTION = ST_SUPPRESS__ALL


class CDITS(object):
   def __init__(self, dut):
      self.oProcess = CProcess()
      self.dut = dut
      self.bcol = re.compile('^\d[\da-fA-F]')

   @staticmethod
   def unlockFactoryCmds():
      """
         Unlock Factory Commands
         This is required preor calling DITS commands.
      """
      prm_T638_unlockFactoryCmds = {
         'test_num'           : 638,
         'prm_name'           : 'prm_T638_unlockFactoryCmds',
         'stSuppressResults'  : SUPPRESS_OPTION,
         'DFB_WORD_0'         : 0xFFFF, # DITS cmd ID (Lock/Unlock Diagnostics Function)
         'DFB_WORD_1'         : REVISION_ID,
         'DFB_WORD_2'         : 0x9A32, # Unlock Seagate Access Key LSW
         'DFB_WORD_3'         : 0x4F03, # Unlock Seagate Access Key MSW
      }
      oProcess = CProcess()
      oProcess.St(prm_T638_unlockFactoryCmds, timeout=10)

   @staticmethod
   def lockFactoryCmds():
      """
         Lock Factory Commands
         This is required after calling DITS commands.
      """
      prm_T638_lockFactoryCmds = {
         'test_num'           : 638,
         'prm_name'           : 'prm_T638_lockFactoryCmds',
         'stSuppressResults'  : SUPPRESS_OPTION,
         'DFB_WORD_0'         : 0xFFFF, # DITS cmd ID (Lock/Unlock Diagnostics Function)
         'DFB_WORD_1'         : REVISION_ID,
         'DFB_WORD_2'         : 0x9A32, # Lock Seagate Access Key LSW
         'DFB_WORD_3'         : 0x4F83, # Lock Seagate Access Key MSW
      }
      oProcess = CProcess()
      oProcess.St(prm_T638_lockFactoryCmds, timeout=10)

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


class CDITSDriveTables(CDITS):
   def __init__(self, dut):
      CDITS.__init__(self, dut)
   
   def readDriveTables(self, tableId, transferLen):
      RAW_A_F = 0x0200 # 0x02 : RAW: 0 = Default Behavior (Return Data Uncompressed) 
                       #        A  : 1 = Return the starting address and length of the specified table
                       #        F  : 0 = Read Drive Tables F Value Definitions from RAM
      prm_T638_readDriveTablesLoc = {
         'test_num'           : 638,
         'prm_name'           : 'prm_T638_readDriveTablesLoc',
         'stSuppressResults'  : SUPPRESS_OPTION,
         'DFB_WORD_0'         : 0x4B01, # 0x014B : Read Drive Tables Function ID
         'DFB_WORD_1'         : REVISION_ID,
         'DFB_WORD_2'         : RAW_A_F + tableId,
      }
      self.oProcess.St(prm_T638_readDriveTablesLoc, timeout=10)
      
      RAW_A_F = 0x0000 # 0x00 : RAW: 0 = Default Behavior (Return Data Uncompressed) 
                       #        A  : 0 = Return the contents of the specified table as specified with "Transfer Length" and "Memory Offset" (normal operation) 
                       #        F  : 0 = Read Drive Tables F Value Definitions from RAM
      prm_T638_readDriveTablesData = {
         'test_num'           : 638,
         'prm_name'           : 'prm_T638_readDriveTablesData',
         'DblTablesToParse'   : ['P000_BUFFER',],
         'stSuppressResults'  : SUPPRESS_OPTION,
         'DFB_WORD_0'         : 0x4B01, # 0x014B : Read Drive Tables Function ID
         'DFB_WORD_1'         : REVISION_ID,
         'DFB_WORD_2'         : RAW_A_F + tableId,
         'DFB_WORD_3'         : 0x0000, # Reserved
         'DFB_WORD_4'         : 0x0000, # 0x0000 : Memory Offset (32-bits, Little Endian)
         'DFB_WORD_5'         : 0x0000, # 0x0000 : Memory Offset (32-bits, Little Endian)
         'DFB_WORD_6'         : 0x0000, # Reserved
         'DFB_WORD_7'         : transferLen,
      }
      self.oProcess.St(prm_T638_readDriveTablesData, timeout=10)
      
      return self.extractBufferDblog(self.dut.objSeq.SuprsDblObject['P000_BUFFER'])
   
   def getCAPTable(self):
      if objRimType.IOInitRiser():
         # For SI cell
         return self.CCAPTable(self.readDriveTables(0x01, 0x0200))
      else:
         # For CPC cell
         return self.CCAPTable(self.readDriveTables(0x01, 0x0000))
   
   class CCAPTable(str):
      def getHeadNum(self):
         """
            Get drive number of heads
            @return headNum: number of heads in hexadecimal characters
            Example result: "04"
         """
         # Number of heads is at offset 0x22 in CAP table
         return self[0x44:0x46]


class CDITSDriveInformation(CDITS):
   def __init__(self, dut):
      CDITS.__init__(self, dut)
   
   def getDriveInformation(self, infoFieldSpc):
      infoFieldSpc = infoFieldSpc << 8
      prm_T638_getDriveInformation = {
         'test_num'           : 638,
         'prm_name'           : 'prm_T638_getDriveInformation',
         'DblTablesToParse'   : ['P000_BUFFER',],
         'stSuppressResults'  : SUPPRESS_OPTION,
         'DFB_WORD_0'         : 0x5601, # 0x0156 : Get Drive Information DFB
         'DFB_WORD_1'         : REVISION_ID,
         'DFB_WORD_2'         : infoFieldSpc,
      }
      res = self.oProcess.St(prm_T638_getDriveInformation, timeout=10)
      
      return self.extractBufferDblog(self.dut.objSeq.SuprsDblObject['P000_BUFFER'])

   # Get Drive Serial Number Field
   def getDriveSNField(self):
      return self.getDriveInformation(0x00)

   def getDriveSN(self):
      """
         Get drive serial number
         @return driveSN: string of characters
         Example result: "W0Z006E0"
      """
      return self.getDriveSNField().decode("hex")

   # Get PCBA Serial Number Field
   def getPcbaSNField(self):
      return self.getDriveInformation(0x01)

   def getPcbaSN(self):
      """
         Get PCBA serial number
         @return pcbaSN: string of characters
         Example result: "0000S2148UJM"
      """
      return self.getPcbaSNField().decode("hex")

