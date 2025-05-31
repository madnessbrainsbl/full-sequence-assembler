#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description:
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/CommandSet.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/CommandSet.py#1 $
# Level:3
#---------------------------------------------------------------------------------------------------------#
from Constants import *

import time, random
import DbLog
import ScrCmds
from Process import CProcess
import IntfClass
from TestParamExtractor import TP
from Rim import objRimType
import MessageHandler as objMsg
from ICmdFactory import ICmd

WrRdMode = {
            "PIO 0" :             0x08,
            "PIO 1" :             0x09,
            "PIO 2" :             0x0A,
            "PIO 3" :             0x0B,
            "PIO 4" :             0x0C,
            "UDMA 0" :            0x40,
            "UDMA 1" :            0x41,
            "UDMA 2 (UDMA33)" :   0x42,
            "UDMA 3" :            0x43,
            "UDMA 4 (UDMA66)" :   0x44,
            "UDMA 5 (UDMA100)" :  0x45,
            "UDMA 6 (UDMA133)" :  0x46,
            "UDMA 7 (UDMA150)" :  0x47,
            "UDMA 8 (UDMA300)" :  0x48
         }

##############################################################################################################
##############################################################################################################
class commandSetException(Exception):
   def __init__(self,data):
      self.data = data

##############################################################################################################
##############################################################################################################
class CCommandSetTest(CProcess):
   """
   Test Purpose: Validate drive functionality with the basic ATA command set.
   Test Metrics: Hard errors, CRC Errors, Command Timeouts.
   Patterns: All zero Patterns.
   Basic Algorithm:
   - Non Disk Access Tests
      - Recalibrate
      - WriteBuffer
      - ReadBuffer
   - Seek Tests
      - Seek Max LBA
      - Seek Min LBA
   - PIO Mode Write/Read Testing
      - Write/Read Min LBA
      - Write/Read Max LBA
      - Random Read LBA's
   - UDMA Mode Write/Read Testing
      - Write/Read Min LBA
      - Write/Read Max LBA
      - Random Read LBA's
   - EXT Write/Read Testing
      - Write/Read Min LBA
      - Write/Read Max LBA
      - Random Read LBA's
   Failure: Fail on any hard error, CRC failure, or command timeout.
   """
   #---------------------------------------------------------------------------------------------------------#
   def __init__(self, dut, params=[]):
      objMsg.printMsg('*'*20+"Command Set init" + 20*'*')
      self.ODendLBA = 256                     # Set OD end LBA
      self.ODstartLBA = 0                     # Set OD start LBA, Min LBA
      self.sectorCount = 256                  # Set Sector Count
      self.extendedCount = 1024               # Set Sector Count, extended commands
      self.WrRdMode = WrRdMode['UDMA 7 (UDMA150)']  # Set WrRdMode

      self.setMultiMode = 8
      ret = IntfClass.CIdentifyDevice(refreshBuffer=False).ID # read device settings with identify device
      if testSwitch.FE_0121834_231166_PROC_TCG_SUPPORT:
         if (int(ret['IDSeaCosFDE']) & 0x1010) == 0x1010 : # Check for SeaCOS cmd supported (bit4) and SeaCOS cmd enabled (bit12)
            objMsg.printMsg('SeaCosFDE cmd supported, setMultimode =1')
            self.setMultiMode = 1

         # Check for TCG (including SeaCos) cmds supported - Bit 0 and 14
         # Check for Disk Encryption supported - Bit 14
         if (int(ret['IDReserved48']) & 0x4001) == 0x4001 and (int(ret['IDReserved243']) & 0x4000) == 0x4000 :
            objMsg.printMsg('TCG FDE cmd supported, setMultimode =1')
            self.setMultiMode = 1
      else:
         if (int(ret['FDE']) & 0x1010) == 0x1010 : # Check for SeaCOS cmd supported (bit4) and SeaCOS cmd enabled (bit12)
            self.setMultiMode = 1

      self.IDendLBA = ret['IDDefaultLBAs'] - 1 # default for 28-bit LBA
      if ret['IDCommandSet5'] & 0x400:      # check bit 10
         objMsg.printMsg('Get ID Data 48 bit LBA is supported')
         self.IDendLBA = ret['IDDefault48bitLBAs'] - 1
      objMsg.printMsg('ID End LBA: %d' % self.IDendLBA)
      self.IDstartLBA = self.IDendLBA - 256   # Set ID Start LBA

   #---------------------------------------------------------------------------------------------------------#
   def commandSetTest(self, numLoops=1):
      """
      Execute function loop.
      @return result: Returns OK or FAIL
      """
      objMsg.printMsg('*'*20+"Command Set Test" + 20*'*')
      if numLoops > 1:
         objMsg.printMsg("NumLoops: %s" % numLoops)
      try:
         for loopCnt in range(numLoops):
            if numLoops > 1:
               objMsg.printMsg('Loop: ' + str(loopCnt+1) + '*'*5+"Command Set Test" + 20*'*')

            self.ExecDeviceDiag()
            if not(objRimType.CPCRiser() and testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION):
               self.recalibrate() #This cmd retired in CPCv3x
            self.fluchCache()

            self.bufferCommand('Write')
            self.bufferCommand('Read')

            self.seekLBA(self.IDendLBA)
            self.seekLBA(self.ODstartLBA)

            self.seqWrRdLBA('PIOMode', self.ODstartLBA, self.ODendLBA, self.sectorCount)
            self.seqWrRdLBA('PIOMode', self.IDstartLBA, self.IDendLBA, self.sectorCount)
            if testSwitch.IOWriteReadRemoval or testSwitch.CPCWriteReadRemoval:
               self.randomWrRdLBA('PIOMode', self.ODstartLBA, self.ODendLBA, self.sectorCount)
            else:
               self.randomWrRdLBA('PIOMode', self.ODstartLBA, self.IDendLBA, self.sectorCount)

            self.seqWrRdLBA('UDMAMode', self.ODstartLBA, self.ODendLBA, self.sectorCount)
            self.seqWrRdLBA('UDMAMode', self.IDstartLBA, self.IDendLBA, self.sectorCount)
            if testSwitch.IOWriteReadRemoval or testSwitch.CPCWriteReadRemoval:
               self.randomWrRdLBA('UDMAMode', self.ODstartLBA, self.ODendLBA, self.sectorCount)
            else:
               self.randomWrRdLBA('UDMAMode', self.ODstartLBA, self.IDendLBA, self.sectorCount)

            self.sectWrRdCmpLBA(self.ODstartLBA, self.sectorCount)
            self.multiLBAWrRdCmp(self.ODstartLBA, self.sectorCount)

            # Re-initialise LBA regions to perform Ext cmds
            self.ODendLBA = self.extendedCount
            self.IDstartLBA = self.IDendLBA - self.extendedCount

            self.seqWrRdLBA('EXTMode', self.ODstartLBA, self.ODendLBA, self.extendedCount)
            self.seqWrRdLBA('EXTMode', self.IDstartLBA, self.IDendLBA, self.extendedCount)
            
            if testSwitch.IOWriteReadRemoval or testSwitch.CPCWriteReadRemoval:
               self.randomWrRdLBA('EXTMode', self.ODstartLBA, self.ODendLBA, self.extendedCount)
            else:
               self.randomWrRdLBA('EXTMode', self.ODstartLBA, self.IDendLBA, self.extendedCount)

         result = 0
      except commandSetException, M:
         ScrCmds.raiseException(13452, M.data)

      if testSwitch.IOWriteReadRemoval:
         RWDict = []
         RWDict.append ('Write')
         RWDict.append (self.ODstartLBA)
         RWDict.append (self.sectorCount)
         RWDict.append ('CommandSet')
         objMsg.printMsg('WR_VERIFY appended - %s' % (RWDict))
         TP.RWDictGlobal.append (RWDict)

         RWDict = []
         RWDict.append ('Read')
         RWDict.append (self.ODstartLBA)
         RWDict.append (self.ODendLBA)
         RWDict.append ('CommandSet')
         objMsg.printMsg('WR_VERIFY appended - %s' % (RWDict))
         TP.RWDictGlobal.append (RWDict)

         RWDict = []
         RWDict.append ('Read')
         RWDict.append (self.IDstartLBA)
         RWDict.append (self.IDendLBA)
         RWDict.append ('CommandSet')
         objMsg.printMsg('WR_VERIFY appended - %s' % (RWDict))
         TP.RWDictGlobal.append (RWDict)

         RWDict = []
         RWDict.append ('Read')
         RWDict.append (self.IDstartLBA & 0xFFFFFFF)
         RWDict.append (self.IDendLBA & 0xFFFFFFF)
         RWDict.append ('CommandSet')
         objMsg.printMsg('WR_VERIFY appended - %s' % (RWDict))
         TP.RWDictGlobal.append (RWDict)

      return result

   #---------------------------------------------------------------------------------------------------------#
   def recalibrate(self):
      """
      Algorithm:
         Issue ATA Recalibrate command.
         Fails on ATA command timeout.
      """
      data = ICmd.Recalibrate()
      msg = 'Command Set - Recalibrate Command'
      if data['LLRET'] == 0:
         objMsg.printMsg('%s: Passed' %msg)
      else:
         objMsg.printMsg('%s: Failed' %msg)
         raise commandSetException(data)

   #---------------------------------------------------------------------------------------------------------#
   def fluchCache(self):
      """
      Algorithm:
         Issue ATA FluchCache command.
         Fails on ATA command timeout.
      """
      data = ICmd.FlushCache()
      msg = 'Command Set - FluchCache Command'
      if data['LLRET'] == 0:
         objMsg.printMsg('%s: Passed' %msg)
      else:
         objMsg.printMsg('%s: Failed' %msg)
         raise commandSetException(data)

   #---------------------------------------------------------------------------------------------------------#
   def bufferCommand(self, command="Write"):
      """
      Algorithm:
         Issue ATA Buffer command.
         @param command: Write or Read Buffer.
         Fails on ATA command timeout.
      """
      if command == "Write":
         data = ICmd.WriteBuffer()
      else:
         data = ICmd.ReadBuffer()

      msg = 'Command Set - %s Buffer Command' % command
      if data['LLRET'] == 0:
         objMsg.printMsg('%s: Passed' %msg)
      else:
         objMsg.printMsg('%s: Failed' %msg)
         raise commandSetException(data)

   #---------------------------------------------------------------------------------------------------------#
   def ExecDeviceDiag(self):
      """
      Algorithm:
         Issue ATA command, ExecDeviceDiag
         Fails on ATA command timeout.
      """
      data = ICmd.ExecDeviceDiag()
      msg = 'Command Set - ExecDeviceDiag'
      if data['LLRET'] == 0:
         objMsg.printMsg('%s: Passed' %msg)
      else:
         objMsg.printMsg('%s: Failed' %msg)
         raise commandSetException(data)

   #---------------------------------------------------------------------------------------------------------#
   def seekLBA(self, LBA=0):
      """
      Algorithm:
         Issue ATA command, seek to LBA.
         @param LBA: The LBA to Seek to.
         Fails on ATA command timeout.
      """
      data = ICmd.Seek(LBA)
      msg = 'Command Set - Seek LBA = 0X%X' % LBA
      if data['LLRET'] == 0:
         objMsg.printMsg('%s: Passed' %msg)
      else:
         objMsg.printMsg('%s: Failed' %msg)
         raise commandSetException(data)

   #---------------------------------------------------------------------------------------------------------#
   def seqWrRdLBA(self, mode, startLBA, endLBA, count, stamp=0, compare=0):
      """
      Algorithm:
         Issue ATA command, Write Read LBA.
         @param mode: Mode setting PIOMode, UDMAMode, EXTMode(Extended commands).
         @param startLBA: Minimum OD LBA for Sequential locations.
         @param endLBA: Maximum ID LBA for Sequential locations.
         @param count: Sector count and Step count used for Sequential commands.
         @param stamp: Add LBA sector number to every sector, 0=OFF 1=ON.
         @param compare: Do a CPC buffer compare of the data, 0=OFF 1=ON.
         Fails on CRC error (need specific FC)
         Fails on write or read error
      """
      data = ICmd.ClearBinBuff(BWR)
      msg = 'Clear Bin Buffer'
      msg_sub = ''

      if data['LLRET'] == OK:
         if mode in ['EXTMode', 'UDMAMode']:
            msg = "SetFeatures: Sequential Write Read %s" %mode
            data = ICmd.SetFeatures(0x03, self.WrRdMode)

      if data['LLRET'] == OK:
         msg = 'Command Set - Sequential Write Read Mode=%s LBA=0X%X Count=0X%X' % (mode,endLBA,count)

         if mode == 'PIOMode':
            if objRimType.CPCRiser() and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION:
               data = ICmd.SequentialWR(startLBA, endLBA, count, count, stamp, compare)
            elif objRimType.CPCRiser() and testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION:
               data = ICmd.WriteSectorsExt(startLBA,count)
               data = ICmd.ReadSectorsExt(startLBA,count)   
            elif objRimType.IOInitRiser():
               data = ICmd.WriteSectorsExt(startLBA,count)
               data = ICmd.ReadSectorsExt(startLBA,count)                               

         elif mode == 'UDMAMode':
            data = ICmd.SequentialWRDMA(startLBA, endLBA, count, count, stamp, compare)

         elif mode == 'EXTMode':
            from Utility import CUtility
            cylTuple = CUtility.ReturnTestCylWord
            lbaTuple = CUtility.returnStartLbaWords
            prm_510_EXTSeqWR= {
                           'test_num'              : 510,
                           'prm_name'              : "prm_510_EXTModeWR",
                           'timeout'               : 600,
                           'spc_id'                : 1,
                           'CTRL_WORD1'            : 0x02,           # Seq w/r, display error location
                           'CTRL_WORD2'            : 0x2080,
                           'STARTING_LBA'          : (0, 0, 0, 0),
                           'BLKS_PER_XFR'          : 0x100,
                           'DATA_PATTERN0'         : (0x0000, 0x0000),
                           'RESET_AFTER_ERROR'     : 1,
                           }
            prm_510_EXTSeqWR['BLKS_PER_XFR'] = count
            prm_510_EXTSeqWR['STARTING_LBA'] = lbaTuple(startLBA)
            # prm_510_EXTSeqWR['MAXIMUM_LBA'] = lbaTuple(endLBA)
            prm_510_EXTSeqWR['TOTAL_BLKS_TO_XFR'] = cylTuple(endLBA-startLBA+1)
            try:
               ICmd.St(prm_510_EXTSeqWR)
            except:
               raise commandSetException('T510 ExtSeqWR fail')


      if data['LLRET'] == OK:
         objMsg.printMsg('%s: Passed' %msg)
      else:
         objMsg.printMsg('%s %s: Failed' %(msg, msg_sub))
         objMsg.printMsg("data = %s" % (str(data)))
         raise commandSetException(data)

   #---------------------------------------------------------------------------------------------------------#
   def randomWrRdLBA(self, mode, startLBA, endLBA, count, stamp=0, compare=0):
      """
      Algorithm:
         Issue ATA command, Random Write Read LBA.
         @param mode: Mode setting PIOMode, UDMAMode, EXTMode(Extended commands).
         @param startLBA: Minimum OD LBA for Random locations.
         @param endLBA: Maximum ID LBA for Random locations.
         @param count: Sector count and Step count.
         @param stamp: Add LBA sector number to every sector, 0=OFF 1=ON.
         @param compare: Do a CPC buffer compare of the data, 0=OFF 1=ON.
         Fails on CRC error (need specific FC)
         Fails on write or read error
      """
      data = ICmd.ClearBinBuff(BWR)
      msg = 'Clear Bin Buffer'
      msg_sub = ''

      if data['LLRET'] == OK:
         if mode in ['EXTMode', 'UDMAMode']:
            msg = "SetFeatures: Random Write Read %s" %   mode
            data = ICmd.SetFeatures(0x03, self.WrRdMode)

      if data['LLRET'] == OK:
         msg = 'Command Set - Random Write Read Mode=%s LBA=0X%X Count=0X%X' % (mode,endLBA,count)

         if mode == 'PIOMode':
            if objRimType.CPCRiser() and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION:     
               data = ICmd.RandomWR(startLBA, endLBA, count, count, count, stamp, compare)        

         elif mode == 'UDMAMode':
            data = ICmd.RandomWRDMA(startLBA, endLBA, count, count, count, stamp, compare)            

         elif mode == 'EXTMode':
            from Utility import CUtility
            cylTuple = CUtility.ReturnTestCylWord
            lbaTuple = CUtility.returnStartLbaWords
            prm_510_EXTRdmWR= {
                           'test_num'              : 510,
                           'prm_name'              : "prm_510_EXTModeWR",
                           'timeout'               : 600,
                           'spc_id'                : 1,
                           'CTRL_WORD1'            : 0x03,           # Rdm w/r, display error location
                           'CTRL_WORD2'            : 0x2080,
                           'STARTING_LBA'          : (0, 0, 0, 0),
                           'BLKS_PER_XFR'          : 0x100,
                           'DATA_PATTERN0'         : (0x0000, 0x0000),
                           'RESET_AFTER_ERROR'     : 1,
                           }
            prm_510_EXTRdmWR['BLKS_PER_XFR'] = count
            prm_510_EXTRdmWR['STARTING_LBA'] = lbaTuple(startLBA)
            # prm_510_EXTRdmWR['MAXIMUM_LBA'] = lbaTuple(endLBA)
            prm_510_EXTRdmWR['TOTAL_BLKS_TO_XFR'] = cylTuple(endLBA-startLBA+1)
            try:
               ICmd.St(prm_510_EXTRdmWR)
            except:
               raise commandSetException('T510 ExtRdmWR fail')
            


      if data['LLRET'] == OK:
         objMsg.printMsg('%s: Passed' %msg)
      else:
         objMsg.printMsg('%s %s: Failed' %(msg, msg_sub))
         objMsg.printMsg("data = %s" % (str(data)))
         raise commandSetException(data)

   #---------------------------------------------------------------------------------------------------------#
   def sectWrRdCmpLBA(self, startLBA, count, data='', compare=1):
      """
      Algorithm:
         Issue ATA command, Write Read Sector.
         Fails on CRC error (need specific FC)
         Fails on write or read error
      """
      msg = 'Command Set - Sector Write Read Compare LBA=0X%X Count=0X%X Data=%s Compare=%s' % (startLBA, count, `data`, compare)
      msg_sub = "WriteSectors: ICmd"
      data = ICmd.WriteSectors(startLBA, count)

      if data['LLRET'] == OK:
         msg_sub = "ReadSectors: ICmd"
         data = ICmd.ReadSectors(startLBA, count)

      if data['LLRET'] == OK and compare ==1:
         msg_sub = "ReadSectors: CompareBuffers"
         data = ICmd.CompareBuffers(startLBA, count * 512)

      if data['LLRET'] == OK:
         msg_sub = "ReadVerifySects: ICmd"
         data = ICmd.ReadVerifySects(startLBA, count)

      if data['LLRET'] == OK:
         objMsg.printMsg('%s: Passed' %msg)
      else:
         objMsg.printMsg('%s %s: Failed' %(msg, msg_sub))
         objMsg.printMsg("data = %s" % (str(data)))
         raise commandSetException(data)

   #---------------------------------------------------------------------------------------------------------#
   def multiLBAWrRdCmp(self, startLBA, count, data='', stamp=1, compare=1):
      """
      Algorithm:
         Issue ATA command, Write Read Multiple.
         Fails on CRC error (need specific FC)
         Fails on write or read error
      """
      msg = 'Command Set - Multiple LBA Write Read Compare LBA=0X%X Count=0X%X Data=%s Stamp=%s Compare=%s' % (startLBA, count, `data`, stamp, compare)

      if objRimType.IOInitRiser():      
         ICmd.HardReset()             
         
      msg_sub = 'SetMultipleMode; %d' %self.setMultiMode
      #data = ICmd.SetMultipleMode(8)
      data = ICmd.SetMultipleMode(self.setMultiMode)

      if objRimType.CPCRiser() and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION: 
         if data['LLRET'] == OK and stamp == 1:
            msg_sub = 'WriteMultipleLBA: FillBuffStamp'
            data = ICmd.FillBuffStamp(WBF, startLBA, 0, 256)	#  Stamp the entire buffer            

      if data['LLRET'] == OK:
         msg_sub = "WriteMultipleLBA: ICmd"
         data = ICmd.WriteMultiple(startLBA, count)

      if data['LLRET'] == OK:
         msg_sub = "ReadMultipleLBA: ICmd"
         data = ICmd.ReadMultiple(startLBA, count)

      if data['LLRET'] == OK and compare ==1:
         msg_sub = "ReadMultipleLBA: CompareBuffers"
         data = ICmd.CompareBuffers(startLBA, count * 512)

      if data['LLRET'] == OK:
         objMsg.printMsg('%s: Passed; setMultiMode:%d' %(msg, self.setMultiMode))
      else:
         objMsg.printMsg('%s %s: Failed' %(msg, msg_sub))
         objMsg.printMsg("data = %s" % (str(data)))
         raise commandSetException(data)

   #---------------------------------------------------------------------------------------------------------#
