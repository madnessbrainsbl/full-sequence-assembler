#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Module to hold smart access functions and classes
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/SmartFuncs.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/SmartFuncs.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from DesignPatterns import Singleton
import time, os, struct, binascii
import MessageHandler as objMsg

from ICmdFactory import ICmd


BASIC = 0
TWO_K = 1

fmtList_1k = [
                  ( 'FHFreqOD',          'HH',)   ,
                  ( 'FHFreqID',          'HH',)   ,
                  ( 'Resistance',        'H', )   ,
                  ( 'WriteFaults',       'H', )   ,
                  ( 'ReadErrorsVis',     'H', )   ,
                  #( 'ARRECount',         'B',  )  ,
                  #( 'AWRECount',         'B',  )  ,
                  #( 'Reassigns',         'B',  )  ,
                  #( 'TACount',           'B',  )  ,
                  ( 'GListEntries',      'H',  )  ,
                  #( 'SListEntries',      'H',  )  ,
                  ( 'SectorsRead',       'L',  )  ,
                  ( 'SectorsWritten',    'L',  )  ,
                  ( 'ReadSeekCount',     'H',  )  ,
                  ( 'WriteSeekCount',    'H',  )  ,
                  ( 'SeekErrors',        'H',  )  ,
                  #( 'MultiRetrySkerr',   'H',  )  ,
                  ( 'BdSampCnt',         'H',  )  ,
                  ( 'TNoTmdCnt',         'H',  )  ,
                  ( 'VNoTmdCnt',         'H',  )  ,
                  ( 'Unsafes',           'H',  )  ,
                  ( 'OCLIM_5_to_10',     'H',  )  ,
                  ( 'OCLIM_10_to_15',    'H',  )  ,
                  ( 'OCLIM_15_plus',     'H',  )  ,
                  ( 'ServoAGCDeltaAvg',  'H',  )  ,
                  ( 'ServoAGCAvgRun',    'H',  )  ,
                  ( 'ServoAGCFilteredAvg', 'H',  ),
                  ( 'HeaterResistance',  'H',  )  ,
                  ( 'ServoACFFx1Sin',    'b',  )  ,
                  ( 'ServoACFFx1Cos',    'b',  )  ,
                  ( 'ConvertedRAWSector','B',  )  ,
                  ( 'MultiRetrySkerr',   'B',  )  ,
                  ( 'ATSSeeksCount',     'H',  )  ,
                  ( 'ATSSeekRetryCount', 'B',  )  ,
                  ( 'Reserve1',          'B',  )  ,
                  ( 'EccOnTheFly',       'H',  )  ,
                  ( 'EBMSCDErrorDuringRead',  'B',  ),
                  ( 'EBMSCDErrorDuringWrite', 'B',  ),
                ]

class CSmartFrameAccess(Singleton):

   def __init__(self):
      Singleton.__init__(self)
      self.SmartFrames = []
      self.smartFrameFormat = BASIC

   def loadSmartFrames(self):

      ICmd.SetIntfTimeout(30000)
      ICmd.HardReset()
      data = ICmd.GetSmartFrames()

      if DEBUG:
         objMsg.printMsg(repr(data))

      smartVersion = struct.unpack('>H', data[16:18])[0]
      if smartVersion & 0x1000: #2k smart frame
         self.smartFrameFormat = TWO_K


      smartNumHeads = struct.unpack('B', data[19])[0]
      objMsg.printMsg("SMART_FRAME_VERSION: 0x%X" % smartVersion)
      objMsg.printMsg("SMART_NUM_HEADS:     0x%X" % smartNumHeads)


      # fixed offset for smart_head data in smart_frame struct defined in smart.h


      if self.smartFrameFormat == TWO_K:
         #raise Exception, "unhandled"
         smartHeadOffset = struct.unpack('B', data[38:39])[0]
         self.fmtSize_Head = struct.unpack('B', data[39:40])[0]
         self.fmtList = '>' + ''.join([i[1] for i in fmtList_1k])
         #smartHeadOffset = 768 #SMART_FRAME_DRIVE_DATA offset

      else:
         # Should start on line 32 or 32*16
         smartHeadOffset = 512 #SMART_FRAME_DRIVE_DATA offset

         #fmt for head smart frame non 2k and SMART_FAAFH_DATA = 0
         self.fmtList = '>' + ''.join([i[1] for i in fmtList_1k])
         self.fmtSize_Head = struct.calcsize(self.fmtList)
         self.keys = [i[0] for i in fmtList_1k]


      self.SmartFrames = []
      data = data[smartHeadOffset:]
      #parse data from buffer
      for head in xrange(smartNumHeads):
         smart_head = data[:struct.calcsize(self.fmtList)]
         if DEBUG:
            objMsg.printMsg("Len frame: %d" % len(smart_head))
         dataVals = struct.unpack(self.fmtList, smart_head)

         #parse head frame into dict
         self.SmartFrames.append(dict(zip(self.keys, dataVals)))
         if DEBUG:
            objMsg.printMsg(self.SmartFrames[-1])

         #truncate results for next head
         data = data[self.fmtSize_Head:]



   def getSeekErrors(self):
      if self.SmartFrames == []:
         self.loadSmartFrames()
      seekErrorsPerHead = []
      for frame in self.SmartFrames:
         seekErrorsPerHead.append(frame['SeekErrors'])
      return seekErrorsPerHead


class CSmartAttrAccess(Singleton):
   """
   SMART spec at
   //depot/LCO/FW document/SMART Internal Specification.rtf
   or
   https://wiki.seagate.com/confluence/display/Firmware/SMART
   """
   def __init__(self):
      Singleton.__init__(self)
      self.LogData = None


   def loadSmartLog(self, force = False):
      if self.LogData == None or force:

         sctr = ICmd.SmartReadData(exc=1)

         data = ICmd.GetBuffer(RBF, 0, 512)
         self.LogData = data.get('DATA','')#sctr['GETBUFFER']

      return self.LogData

   def ReadSmartAttrIOEDC(self ):
      return self.ReadSmartAttribute(0xB8)['Raw']


   def ReadSeekErrors(self):
      smartRaw = self.ReadSmartAttribute(0x7)['Raw']
      if DEBUG:
         objMsg.printMsg( "!!! smartRaw :: %s"%smartRaw)
      Seeks = smartRaw &  0x0000FFFFFFFF # bytes 0:3 are seeks
      Errors = (smartRaw & 0xFFFF00000000) >> (2**5) # bytes 5:4 are errors
      return Seeks, Errors

   def ReadRetiredSectorCount(self):
      """
      attribute 0x5, 5
      GList aka Alternated Sectors aka alts
      Raw [1 ? 0] = Current Retired Sector Count
      Raw [3 - 2]  = Current Retired Sector Count since SMART was last reset.+
      """
      smartRaw = self.ReadSmartAttribute(0x05)['Raw']
      if DEBUG:
         objMsg.printMsg( "!!! smartRaw :: %s" % smartRaw)
      retiredSectorCount = smartRaw & 0xFFFF # bytes 1:0
      #retiredSpareCountSinceReset = (smartRaw & 0xFFFF0000) >> 16 # B 3:2
      return retiredSectorCount

   def ReadPendingSpareCount(self):
      """
      attribute 0xC5, 197
      PList aka Pending
      Raw [1 ? 0] = Current Pending Spare Count
      Raw [3 -  2] = Current Pending Spare Count since SMART was last reset.+
      """
      smartRaw = self.ReadSmartAttribute(0xC5)['Raw']
      if DEBUG:
         objMsg.printMsg( "!!! smartRaw :: %s" % smartRaw)
      pendingSpareCount = smartRaw & 0xFFFF # bytes 1:0
      #pendingSpareCountSinceReset = (smartRaw & 0xFFFF0000) >> 16 # B 3:2
      return pendingSpareCount

   def UncorrectableSectorsCount(self):
      """
      attribute 0xC6, 198
      PList aka Pending
      Raw [3 ? 0] = Current uncorrectable sector Count
      """
      smartRaw = self.ReadSmartAttribute(0xc6)['Raw']
      if DEBUG:
         objMsg.printMsg( "!!! smartRaw :: %s" % smartRaw)
      currentPendingSpareCount = smartRaw & 0xFFFFFFFFFFFFFFFF # bytes 3:0
      return currentPendingSpareCount

   def ReadSpareCountWhenLastResetSmart(self):
      """
      410:411	Spare Count when Last reset Smart
      """
      self.loadSmartLog()
      if testSwitch.virtualRun:
         return 0
      else:
         # little end-ian unsigned short
         return struct.unpack("<H", self.LogData[410:412])[0]

   def ReadPendingSpareCountWhenLastResetSmart(self):
      """
      412:413	Spare Count when Last reset Smart
      """
      self.loadSmartLog()
      if testSwitch.virtualRun:
         return 0
      else:
         # little end-ian unsigned short
         return struct.unpack("<H", self.LogData[412:414])[0]

   def ReadSmartAttribute(self, attrNum = None):

      attrValue,bytes = -1, 0
      #the attribute sector attribute secion is an array [currently 30 members]
      # of attribute structs defined as per below in core.h in F3 code
      # we pull the raw value for this IOEDC analysis
      """
         typedef struct attribute
         {
            // AttributeNum is the number of the attribute.
            uint8 AttributeNum;              //[u8]

            // FlagsLow is the low byte of the attribute flags.
            uint8 FlagsLow;                  //[u8]

            // FlagsHigh is the high byte of the attribute flags.
            uint8 FlagsHigh;                 //[u8]

            // Normalized is the scaled value of the attribute.
            uint8 Normalized;                //[u8]

            // WorstEver is the worst value yet seen.
            uint8 WorstEver;                 //[u8]

            // Raw is unscaled attribute data.
            uint8 Raw[7];                    //[u8,7]

         } attribute;

         RAW[0] and RAW[1] hold the current new count
      """

      sctr = self.loadSmartLog()

      names = ['AttributeNum', 'FlagsLow', 'FlagsHigh', 'Normalized', 'WorstEver', 'Raw']

      attrFmt = 'BBBBB7s'
      attrSize = struct.calcsize(attrFmt)
      attrOffset = struct.calcsize('H') # first uint16 is the structure version
      MAX_NUM_SMART_ATTRIBUTES = 30
      attribute = {'AttributeNum':0, 'FlagsLow':0, 'FlagsHigh':0, 'Normalized':0, 'WorstEver':0, 'Raw':0}

      if testSwitch.virtualRun:
         return attribute


      if sctr:
         for bytes in xrange(attrOffset,MAX_NUM_SMART_ATTRIBUTES*attrSize+attrOffset,attrSize):
            attributeValues = struct.unpack(attrFmt, sctr[bytes:bytes+attrSize])
            attribute = dict(zip(names, attributeValues))
            if attribute['AttributeNum'] == attrNum:
               attrValue = attrNum

               #Can't unpack 7 bytes so pad the extra value
               if DEBUG:
                  objMsg.printMsg("Found attr %s\nRaw:\n%s" % (attrNum, binascii.hexlify(attribute['Raw'])))

               #attribute['Raw'] = struct.unpack('>Q','\x00' + attribute['Raw'])[0]
               attribute['Raw'] = struct.unpack('<Q',attribute['Raw'] + '\x00')[0]
               break

      if attrValue == -1:
         objMsg.printMsg( "Unable to find Attribute (%X) in the Log" % attrNum )
         objMsg.printMsg( "Buffer data" )
         objMsg.printBin(sctr)

      return attribute


class CEWLM(Singleton):
   """
   Enhance Work Load Management
   """

   def __init__(self):
      Singleton.__init__(self)
      self.LogData = None

   def clearWorkLogPage(self):
      """ Requires CPC 2.247 and above """
      prm_638_EWLM_Control = {
         'test_num'              : 638,
         'prm_name'              : 'Clear log page B6h',
         'DFB_WORD_0'            : 29697,
         'DFB_WORD_1'            : 256,
         'DFB_WORD_2'            : 256,
         'DFB_WORD_3'            : 256,
         'timeout'               : 3600,
         'spc_id'                : 1,
         'stSuppressResults'     : ST_SUPPRESS__ALL,
         }
      ICmd.St(prm_638_EWLM_Control)

   def readWorkLogPage(self):
      """
      Read work load log page B6
      """
      prm_538_SmartWorkLog = {
         'test_num'              : 538,
         'prm_name'              : 'Read log page B6h',
         'timeout'               : 600,
         'COMMAND'               : 47,
         'FEATURES'              : 0,
         'PARAMETER_0'           : 8192,
         'SECTOR_COUNT'          : 1,
         'LBA_HIGH'              : 0,
         'LBA_MID'               : 0,
         'LBA_LOW'               : 182,
         'stSuppressResults'     : ST_SUPPRESS__ALL,
         }
      try:
         ICmd.HardReset()                 # required to reflect correct HP EWLM signature
         ICmd.St(prm_538_SmartWorkLog)
      except:
         ICmd.UnlockFactoryCmds()         # non-hp drive
         ICmd.St(prm_538_SmartWorkLog)
      self.displayReadBuffer()

   def displayReadBuffer(self):
      """
      Display the read buffer
      """
      DisplayBufferData = {
         'test_num'              : 508,
         'prm_name'              : 'Display read buffer',
         'timeout'               : 600,
         'CTRL_WORD1'            : 0x0005,
         'BUFFER_LENGTH'         : (0, 512),
         'stSuppressResults'     : ST_SUPPRESS__ALL,
         }
      ICmd.St(DisplayBufferData)
      self.displayWorkLoadInfo()

   def displayWorkLoadInfo(self):
      """
      Display work load info
      """
      data = ICmd.GetBuffer(RBF, 0, 512*1)['DATA']
      if int(binascii.hexlify(data[7]),16) == 0x3c :
         objMsg.printMsg('Work Load Status Parameter 0x0000 - Revision 1')
         self.workLoadData(data[4:],1)
      elif int(binascii.hexlify(data[7]),16) == 0x7c :
         objMsg.printMsg('Work Load Status Parameter 0x0000 - Revision 3')
         self.workLoadData(data[4:],3)
      else:
         objMsg.printMsg('Work Load Status Parameter 0x0000 - Revision Unknown')


   def workLoadData(self,data,rev=1):
      """
      Dump work load data
      """
      objMsg.printMsg('*'*60)
      objMsg.printMsg('DU                                    = %r'%(not(0x80 & int(binascii.hexlify(data[2]),16))))
      objMsg.printMsg('TSD                                   = %r'%(not(0x20 & int(binascii.hexlify(data[2]),16))))
      objMsg.printMsg('ETC                                   = %r'%(not(0x10 & int(binascii.hexlify(data[2]),16))))
      objMsg.printMsg('TMC                                   = %r'%(not(0x0C & int(binascii.hexlify(data[2]),16))))
      objMsg.printMsg('FORMAT & LINKING                      = %r'%(not(0x03 & int(binascii.hexlify(data[2]),16))))
      objMsg.printMsg('SIGNATURE                             = %s'%(data[4:8]))
      objMsg.printMsg('RWLE                                  = %r'%(not(0x20 & int(binascii.hexlify(data[10]),16))))
      objMsg.printMsg('DEFER                                 = %r'%(not(0x01 & int(binascii.hexlify(data[10]),16))))
      objMsg.printMsg('SMART                                 = %r'%(not(0x08 & int(binascii.hexlify(data[10]),16))))
      objMsg.printMsg('EDCERR                                = %r'%(not(0x04 & int(binascii.hexlify(data[10]),16))))
      objMsg.printMsg('WLME                                  = %r'%(not(0x02 & int(binascii.hexlify(data[10]),16))))
      objMsg.printMsg('PWR                                   = %r'%(not(0x01 & int(binascii.hexlify(data[10]),16))))
      if rev == 1:
         objMsg.printMsg('STANDBY                               = %r'%(not(0x02 & int(binascii.hexlify(data[11]),16))))
         objMsg.printMsg('METHOD                                = %r'%(not(0x01 & int(binascii.hexlify(data[11]),16))))
         objMsg.printMsg('POWER ON HOUR TO PARAMETER CODE RATIO = %d'%(int(binascii.hexlify(data[12:14]),16)))
         objMsg.printMsg('RATED WORK LOAD PERCENTAGE            = %d'%(int(binascii.hexlify(data[16]),16)))
         objMsg.printMsg('POWER ON HOURS TO DETERMINE WORK LOAD = %d'%(int(binascii.hexlify(data[18:20]),16)))
         objMsg.printMsg('IDLE TIME RESOLUTION                  = %d'%(int(binascii.hexlify(data[20]),16)))
         objMsg.printMsg('LAST PARAMETER CODE                   = %d'%(int(binascii.hexlify(data[24:26]),16)))
         objMsg.printMsg('VERSION                               = %s'%(data[60:64]))
      elif rev == 3:
         objMsg.printMsg('FIFO                                  = %r'%(not(0x08 & int(binascii.hexlify(data[11]),16))))
         objMsg.printMsg('POH                                   = %r'%(not(0x04 & int(binascii.hexlify(data[11]),16))))
         objMsg.printMsg('STANDBY                               = %r'%(not(0x02 & int(binascii.hexlify(data[11]),16))))
         objMsg.printMsg('POWER ON HOUR TO PARAMETER CODE RATIO = %d'%(int(binascii.hexlify(data[12:14]),16)))
         objMsg.printMsg('POWER ON HOURS                        = %d'%(int(binascii.hexlify(data[14:16]),16)))
         objMsg.printMsg('RATED WORK LOAD PERCENTAGE            = %d'%(int(binascii.hexlify(data[16]),16)))
         objMsg.printMsg('IDLE TIME RESOLUTION                  = %d'%(int(binascii.hexlify(data[20]),16)))
         objMsg.printMsg('LAST PARAMETER CODE                   = %d'%(int(binascii.hexlify(data[24:26]),16)))
         objMsg.printMsg('MAX NUMBER OF DATA PARAMETERS         = %d'%(int(binascii.hexlify(data[26:28]),16)))
         objMsg.printMsg('TOTAL NUMBER OF OTHER COMMANDS        = %d'%(int(binascii.hexlify(data[28:32]),16)))
         objMsg.printMsg('TOTAL NUMBER OF LBAs READ             = %d'%(int(binascii.hexlify(data[32:40]),16)))
         objMsg.printMsg('TOTAL NUMBER OF LBAs WRITTEN          = %d'%(int(binascii.hexlify(data[40:48]),16)))
         objMsg.printMsg('TOTAL NUMBER OF UNREC READ ERRORS     = %d'%(int(binascii.hexlify(data[48:52]),16)))
         objMsg.printMsg('TOTAL NUMBER OF UNREC WRITE ERRORS    = %d'%(int(binascii.hexlify(data[52:56]),16)))
         objMsg.printMsg('TOTAL NUMBER OF TASK MANAGEMENT OPS   = %d'%(int(binascii.hexlify(data[56:60]),16)))
         objMsg.printMsg('VERSION                               = %s'%(data[60:64]))
         objMsg.printMsg('TOTAL NUMBER OF READ COMMANDS         = %d'%(int(binascii.hexlify(data[64:72]),16)))
         objMsg.printMsg('TOTAL NUMBER OF WRITE COMMANDS        = %d'%(int(binascii.hexlify(data[72:80]),16)))
         objMsg.printMsg('TOTAL NUMBER OF RANDOM READS          = %d'%(int(binascii.hexlify(data[80:88]),16)))
         objMsg.printMsg('TOTAL NUMBER OF RANDOM WRITES         = %d'%(int(binascii.hexlify(data[88:96]),16)))
         objMsg.printMsg('TOTAL THROTTLE MINUTES                = %d'%(int(binascii.hexlify(data[112:116]),16)))

      objMsg.printMsg('*'*60)


smartAttrObj = CSmartAttrAccess()
smartFrameObj = CSmartFrameAccess()
smartEWLM = CEWLM()