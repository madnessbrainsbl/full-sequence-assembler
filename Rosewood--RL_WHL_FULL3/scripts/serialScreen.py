#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: serialScreen Module
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/12/26 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/serialScreen.py $
# $Revision: #11 $
# $DateTime: 2016/12/26 20:52:18 $
# $Author: yihua.jiang $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/serialScreen.py#11 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
try:
   import sys
   sys.path.append(r'C:\var\merlin\scripts\bench')
   sys.path.append(r'C:\Python24\Lib\site-packages\uspp-1.0')
except:
   pass

from PowerControl import objPwrCtrl
from Rim import objRimType
from Cell import theCell
import MessageHandler as objMsg
import time
import re, struct, traceback, binascii
import ScrCmds
from SerialCls import baseComm
from Failcode import translateRwErrorCode
from Drive import objDut
import Utility
from Exceptions import CRaiseException
import sptCmds
import PIF
import string

DEBUG = 0
SHORT_DIAG_DEBUG = 0

class objComm(baseComm):
    def __init__(self, *args, **kwargs):
       super(objComm, self).__init__()

#class sptDiagCmds(baseComm):
class sptDiagCmds(objComm):
   errCntPat = re.compile("Log 10 Entries (?P<errorCount>[\da-fA-F]+)")
   longD10LogPat = re.compile(
      "[ \t]*"
      "(?P<Count>[\da-fA-F]{4})[ \t]+"         # Count
      "(?P<DIAGERR>[\da-fA-F]{8})[ \t]+"       # DIAGERR
      "(?P<RWERR>[\da-fA-F]{8})[ \t]+"         # RWERR
      "(?P<LBA>[\da-fA-F]+)[ \t]+"             # LBA
      "(?P<PBA>[\da-fA-F]+)[ \t]+"             # PBA
      "(?P<SFI>[\da-fA-F]+)[ \t]+"             # SFI
      "(?P<WDG>[\da-fA-F]+)[ \t]+"             # WDG
      "(?P<TRK_LGC_NUM>[\da-fA-F]+)\.(?P<HD_LGC_PSN>[\da-fA-F])\.(?P<SECTOR_LGC>[\da-fA-F]+)[ \t]+" # LLL CHS
      "(?P<TRK_PHYS_NUM>[\da-fA-F]+)\.([\da-fA-F])\.(?P<SECTOR_PHYS>[\da-fA-F]+)[ \t]+"             #PLP CHS
      "(?P<Partition>[\w]+)"
   )
   shortD10LogPat = re.compile(
      "[ \t]*"
      "(?P<Count>[\da-fA-F]{4})[ \t]+"         # Count
      "(?P<DIAGERR>[\da-fA-F]{8})[ \t]*"       # DIAGERR
   )

   CylPattern = re.compile('User\s*(?P<PhyCyl>[\da-fA-F]+)\s*(?P<LogCyl>[\da-fA-F]+)\s*(?P<NomCyl>[\da-fA-F]+)\s*(?P<RadiusMils>[+.\da-fA-F]+)\s*(?P<LogHd>[\da-fA-F]+)\s*(?P<Zn>[\da-fA-F]+)\s*(?P<FirstLba>[\da-fA-F]+)\s*(?P<FirstPba>[\da-fA-F]+)\s*(?P<LogSecs>[\da-fA-F]+)\s*(?P<PhySecs>[\da-fA-F]+)\s*(?P<WdgSk>[\da-fA-F]+)\s*(?P<SecPerFrm>[\da-fA-F]+)\s*(?P<WdgPerFrm>[\da-fA-F]+)')
   # Data pattern return from F3 DisplayTrackInfo diag cmd for various config
   BandInfoPattern = re.compile('Band\sInfo:.*?BandID\s+LogOffset\s+PhyOffset\s+StartLBA\s+StartPBA\s+NumLBAs\s+NumPBAs\s+StartCyl\s+EndCyl\s+ShingDir\s*?(?P<BandID>[0-9a-fA-F]+)\s*(?P<LogOffset>[0-9a-fA-F]+)\s*(?P<PhyOffset>[0-9a-fA-F]+)\s*(?P<StartLBA>[0-9a-fA-F]+)\s*(?P<StartPBA>[0-9a-fA-F]+)\s*(?P<NumLBAs>[0-9a-fA-F]+)\s*(?P<NumPBAs>[0-9a-fA-F]+)\s*(?P<StartCyl>[0-9a-fA-F]+)\s*(?P<EndCyl>[0-9a-fA-F]+)\s*(?P<ShingDir>[a-zA-Z-\>\<]+)\s*')
   F3TrunkInfoPattern = re.compile('Partition\s+PhyCyl\s+LogCyl\s+NomCyl\s+RadiusMils\s+LogHd\s+Zn\s+LogicalTrackNum\s+FirstLba\s+FirstPba\s+LogSecs\s+PhySecs\s+WdgSkw\s+SecPerFrm\s+WdgPerFrm\s*[a-zA-Z]+\s+(?P<PHY_CYL>[a-fA-F\d]+)\s+(?P<LOG_CYL>[a-fA-F\d]+)\s+(?P<NOM_CYL>[a-fA-F\d]+)\s+\S+\s+(?P<LOG_HEAD>[a-fA-F\d]+)\s+(?P<ZONE>[a-fA-F\d]+)\s+(?P<SPI>[a-fA-F\d]+)\s+(?P<FIRST_LBA>[a-fA-F\d]+)\s+(?P<FIRST_PBA>[a-fA-F\d]+)\s+(?P<LOG_SECS>[a-fA-F\d]+)\s+(?P<PHY_SECS>[a-fA-F\d]+)')
   LCOBranchInfoPattern = re.compile('Partition\s+PhyCyl\s+LogCyl\s+NomCyl\s+RadiusMils\s+LogHd\s+Zn\s+FirstLba\s+FirstPba\s+LogSecs\s+PhySecs\s+WdgSkw\s+SecPerFrm\s+WdgPerFrm\s*[a-zA-Z]+\s+(?P<PHY_CYL>[a-fA-F\d]+)\s+(?P<LOG_CYL>[a-fA-F\d]+)\s+(?P<NOM_CYL>[a-fA-F\d]+)\s+\S+\s+(?P<LOG_HEAD>[a-fA-F\d]+)\s+(?P<ZONE>[a-fA-F\d]+)\s+(?P<FIRST_LBA>[a-fA-F\d]+)\s+(?P<FIRST_PBA>[a-fA-F\d]+)\s+(?P<LOG_SECS>[a-fA-F\d]+)\s+(?P<PHY_SECS>[a-fA-F\d]+)')
   SuperParityInfoPattern = re.compile('Super\s+Block\s+Info:.*Partition.*FirstPba\s*[a-zA-Z]+\s+(?P<PHY_CYL>[a-fA-F\d]+)\s+(?P<LOG_CYL>[a-fA-F\d]+)\s+(?P<NOM_CYL>[a-fA-F\d]+)\s+\S+\s+(?P<LOG_HEAD>[a-fA-F\d]+)\s+(?P<ZONE>[a-fA-F\d]+)\s+(?P<LOG_TRACK>[a-fA-F\d]+)\s+(?P<FIRST_LBA>[a-fA-F\d]+)\s+(?P<FIRST_PBA>[a-fA-F\d]+)\s*LogSecs\s+PhySecs\s+WdgSkw\s+SecPerFrm\s+WdgPerFrm\s+(?P<LOG_SECS>[a-fA-F\d]+)\s+(?P<PHY_SECS>[a-fA-F\d]+)')
   SMRInfoPattern = re.compile('BandID.*ShingDir.*Track\sInfo:.*Partition.*WdgPerFrm\s*[a-zA-Z]+\s+(?P<PHY_CYL>[a-fA-F\d]+)\s+(?P<LOG_CYL>[a-fA-F\d]+)\s+(?P<NOM_CYL>[a-fA-F\d]+)\s+\S+\s+(?P<LOG_HEAD>[a-fA-F\d]+)\s+(?P<ZONE>[a-fA-F\d]+)\s+(?P<LOG_TRACK>[a-fA-F\d]+)\s+(?P<FIRST_LBA>[a-fA-F\d]+)\s+(?P<FIRST_PBA>[a-fA-F\d]+)')
   SP_SuperParityInfoPattern = re.compile('Super\s+Block\s+Info:.*Partition.*FirstPba\s*[a-zA-Z]+\s+(?P<PHY_CYL>[a-fA-F\d]+)\s+(?P<LOG_CYL>[a-fA-F\d]+)\s+(?P<NOM_CYL>[a-fA-F\d]+)\s+\S+\s+(?P<LOG_HEAD>[a-fA-F\d]+)\s+(?P<ZONE>[a-fA-F\d]+)\s+(?P<LOG_TRACK>[a-fA-F\d]+)\s+(?P<FIRST_LBA>[a-fA-F\d]+)\s+(?P<FIRST_PBA>[a-fA-F\d]+)\D+(?P<LOG_SECS>[a-fA-F\d]+)')
   SMRZoneInfoPattern = re.compile('User\sPartition.*?\sZn\s+Cylinders\s+Cylinders\s+Track\s+Wedge\s+Track\s+Rate\s*?(?P<ZONE>[a-fA-F\d]+)\s+(?P<PHY_START>[a-fA-F\d]+)-(?P<PHY_END>[a-fA-F\d]+)\s+(?P<LOG_START>[a-fA-F\d]+)-(?P<LOG_END>[a-fA-F\d]+)\s+.*?[(Media\sCache\sPartition),(NumMediaCacheZones)]')


   instance = None
   def __new__(self, *args, **kwargs):
      if self.instance is None:
         self.instance = object.__new__(self, *args, **kwargs)
         self.dataCTRL_L = None                # Create single instance for CTR_L
         self.dataGetZoneInfo = None           # and getZoneInfo data
      return self.instance

   def __init__(self):
      self.currLevel = ''
      #self.baudRate = Baud38400
      self.baudRate = theCell.getBaud()
      #if not testSwitch.virtualRun:
      #baseComm.__init__(self, self.baudRate)
      objComm.__init__(self, self.baudRate)
      self.dut = objDut
      self.BERInfo = {}
      self.prPat = sptCmds.prPat
      self.NumMCZone = 0
      self.skipznDone = 0

   #======================================================================================================================================
   def quickFormatToCalZ0GuardBand(self):
      """
      Calculate Z0 Guard Band using quick format m0,106,,,,,,22.
      """
      if testSwitch.virtualRun:
         pass

      #self.flush()
      sptCmds.gotoLevel('T')

      CMD = 'm0,106,,,,,,22'
      result = sptCmds.sendDiagCmd(CMD, timeout = 300)
      objMsg.printMsg  ("\nQuick Format m0,106,,,,,,22\n%s" % result)

   #======================================================================================================================================
   def spt(sptCmd):
      """
      Decorator to wrap spt cmds to use eslip mode.
      Use this function to wrap your spt command and avoid customary power cycle
      prior to enableDiags to reduce test time.
      ======
      Usage:
      ======
         @spt
         sptCmd
      Where:
         @spt     - calls this function.
         sptCmd   - your serial port command function.
      """
      def sptCmdWrapper(*args, **kwargs):
         if testSwitch.virtualRun:
            sptCmdWrapper.__doc__ = sptCmd.__doc__
         try:
            if not objDut.eslipMode:                        # Switch to ESLIP mode
               objMsg.printMsg("Enabling ESLIP.")
               PBlock(CTRL_T)
               time.sleep(1)
               objDut.eslipMode = 1
            try:
               sptCmds.enableDiags()
            except:
               objPwrCtrl.powerCycle()
               self.quickDiag()
            return sptCmd(*args, **kwargs)
         finally:
            if objRimType.CPCRiser() and objDut.eslipMode:
               objMsg.printMsg("Disabling ESLIP.")
               theCell.disableESlip()
      return sptCmdWrapper

   @staticmethod
   def enableDiags( retries = 10, raiseException = 1):
      """Passthrough function to sptCmds provided as convenience"""
      return sptCmds.enableDiags(retries, raiseException)

   @staticmethod
   def gotoLevel(level = 'T',maxRetries = 3):
      """Passthrough function to sptCmds provided as convenience"""
      return sptCmds.gotoLevel(level, maxRetries)

   @staticmethod
   def sendDiagCmd( cmd, timeout=60, altPattern = None, printResult = False, stopOnError = True, maxRetries = 0, Ptype = 'PBlock',DiagErrorsToIgnore = [], loopSleepTime = 0.1, raiseException = 1, suppressExitErrorDump = 0, RWErrorsToIgnore = []):
      """Passthrough function to sptCmds provided as convenience"""
      return sptCmds.sendDiagCmd( cmd, timeout, altPattern, printResult, stopOnError, maxRetries, Ptype, DiagErrorsToIgnore, loopSleepTime, raiseException, suppressExitErrorDump, RWErrorsToIgnore)

   @staticmethod
   def execOnlineCmd(cmd, timeout = 30, waitLoops = 100):
      """Passthrough function to sptCmds provided as conveniance"""
      return sptCmds.execOnlineCmd( cmd, timeout, waitLoops)

   def OverlayRevCorrect(self):
      """Determine if the overlay loaded on the drive matches the CFW load on the drive
      1.  If OVL matches TGT, buffer data will be returned
      2.  If OVL does not match TGT, Unable to load Diag Cmd Processor Overlay or Invalid Diag Cmd or Flash LED will be returned.
        (The first time you execute a command, you get overlay msg, after that you get Invalid CMD/Flash LED)
      3.  If no OVL exists on disc, RST x.x will be returned
      """

      objMsg.printMsg("Determine if the F3 OVL matches TGT revision")

      sptCmds.enableDiags()
      #issue simple command from Overlay
      sptCmds.gotoLevel('2')

      try:
         bufferData = sptCmds.sendDiagCmd('B',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)
         for line in bufferData.splitlines():
            if 'Buffer' in line:
               objMsg.printMsg("Overlay Revision does match TGT revision.")
               return 1
      except (ScriptTestFailure,CRaiseException):
         objMsg.printMsg("Command error: invalid overlay possible.")

      objMsg.printMsg("Overlay Revision does not match TGT revision.")
      return 0

   #======================================================================================================================================
   def getPList(self,timeout = 300, printResult = False):

      objMsg.printMsg("Extracting Plist")
      plistPat = re.compile("(?P<head>\d+)\s+(?P<logicalCyl>[\dA-F]+)\s+(?P<physCyl>[\dA-F]+)\s+(?P<symLength>[\dA-F]+)\s+(?P<SFI>[\dA-F]+)\s+(?P<Flags>[\dA-F]+)")
      sptCmds.gotoLevel('T')
      pListData = sptCmds.sendDiagCmd('V10',timeout,printResult = printResult, loopSleepTime=0)

      Plist = plistPat.findall(pListData)
      if DEBUG > 0:
         objMsg.printMsg("hd, logCyl, phCyl, symLen, SFI, flags")
         for rec in Plist:
            objMsg.printMsg("%s, %s, %s, %s, %s, %s" % rec)

      objMsg.printMsg("Found %d plist items" % len(Plist))
      return Plist

   def clearGList(self):
      objMsg.printMsg("Clearing Glist")
      sptCmds.gotoLevel('T')
      sptCmds.sendDiagCmd("i40,1,22",timeout = 1800, printResult = True, loopSleepTime=0, DiagErrorsToIgnore = ['00005002'])

   def clearAltList(self):
      objMsg.printMsg("Clearing Reassigned Sectors List or Alt List")
      sptCmds.gotoLevel('T')
      sptCmds.sendDiagCmd("i4,1,22",timeout = 1800, printResult = True, loopSleepTime=0)
      if testSwitch.CLEAR_DATA_SCRUB_TABLE_AFTER_CLEAR_ALT_LIST :
         objMsg.printMsg("Clearing data scrub table")
         sptCmds.sendDiagCmd("i200,1,22",timeout = 1800, printResult = True, loopSleepTime=0)

   #======================================================================================================================================
   def genRangeGroups(self, Plist, padRange = 50, ignoreSlippedTracks = True):

      hdOff = 0
      logCylOff = 1
      phyCylOff = 2

      def indexCompare(val1, val2, index = hdOff):
         if val1[index] > val2[index]:
            return 1
         elif val1[index] < val2[index]:
            return -1
         else:
            return 0

      pListGroups = {}
      start = None
      end = None
      addHead = None

      Plist.sort(indexCompare)

      for recIndex in xrange(len(Plist)):

         curHead = int(Plist[recIndex][hdOff])
         curLogCyl = int(Plist[recIndex][logCylOff],16)
         if curLogCyl == 4294967295: #invalid cyl
            if ignoreSlippedTracks:
               continue
            else:
               curLogCyl = int(Plist[recIndex][phyCylOff],16)

         if addHead == None:
            addHead = curHead
            start = curLogCyl
            end = curLogCyl

         #Check if we can move the end point
         if  curLogCyl < end + padRange and addHead == curHead:
            end = curLogCyl
         else:
            if DEBUG > 0:
               objMsg.printMsg("Creating range for %d to %d group" % (start,end))
            pListGroups.setdefault(addHead,[]).append([start-padRange,end+padRange])
            addHead = curHead
            start = curLogCyl
            end = curLogCyl

      totGrps = 0
      outStr = "\n%4s\t%7s\t%7s\n" % ('Head','start','end')
      for key,val in pListGroups.iteritems():
         totGrps += len(val)
         for item in val:
            outStr += "%4d\t%7x\t%7x\n" % (key,item[0],item[1])

      objMsg.printMsg(outStr)
      objMsg.printMsg("-"*40)
      objMsg.printMsg("Found %d zone groups." % (totGrps,))
      return pListGroups

   def setCurrentManufacturingStatus(self, operation, errorCode):
      objMsg.printMsg("Updating Final Manufacturing status in CAP to Operation = %s, ErrorCode = %d" % (operation,errorCode))
      self.setCAPValue('FINAL_MANUF_OP', str(operation), saveToFlash=False)
      if testSwitch.FE_0180898_231166_OPTIMIZE_ATTR_VAL_FUNCS:
         self.setCAPValue('FINAL_MANUF_EC', int(errorCode), saveToFlash=False)
      else:
         self.setCAPValue('FINAL_MANUF_EC', int(errorCode), saveToFlash=True)

   @spt
   def setCAPValue(self, paramName, value, saveToFlash = False):
      """
      Set the value in the CAP using DIAG commands.
      """
      from types import StringType

      paramEnum = {'VALIDATION_KEY'          :0x0,
                  'HDA_SN'                   :0x1,
                  'NODE_NAME_VALIDATION_KEY' :0x5,
                  'NODE_NAME'                :0x6,
                  'DESTROK_BUF_SZ_INDEX'     :0xE,
                  'FINAL_MANUF_OP'           :0xF,
                  'FINAL_MANUF_EC'           :0x10,
                  'EXTERNAL_MODEL_NUM'       :0x15,
                  'INTERNAL_MODEL_NUM'       :0x16,
                  'IDEMA_CAP'                :0x17,
                  'LENOVO_8S'                :0x19,}

      if testSwitch.ROSEWOOD7:
         paramEnum.update({'LENOVO_8S'    :  0x1A})

      prmKey = paramEnum[paramName]
      sptCmds.gotoLevel('T')
      if type(value) == StringType:
         sptCmds.sendDiagCmd('J"%s",%x' % (value, prmKey), printResult = True)
      else:
         sptCmds.sendDiagCmd('J%x,%x' % (value, prmKey), printResult = True)
      if saveToFlash:
         self.saveSegmentToFlash(0)

   def getCapValue(self, prmKey = None, printResult = True):
      """
      Dump the contents of the CAP J command function
      Parameters
         prmKey = index of the key to dump. Default is all
      Returns: data resulted from command to function caller and log= printResult
      """
      sptCmds.gotoLevel('T')
      if prmKey == None:
         return sptCmds.sendDiagCmd('J' , printResult = printResult)
      else:
         return sptCmds.sendDiagCmd('J,%x' % (prmKey), printResult = printResult)

   def saveSegmentToFlash(self, segmentType):
      """
      segmentType:
         CAP=0
         SAP=1
         RAP=2
         IAP=3
      """

      #must spin down the drive prior to flash write
      sptCmds.gotoLevel('2')
      sptCmds.sendDiagCmd('Z', timeout = 60)

      sptCmds.gotoLevel('T')
      if testSwitch.FE_0180898_231166_OPTIMIZE_ATTR_VAL_FUNCS:
         sptCmds.sendDiagCmd('W%x,,22' % segmentType, timeout = 300, printResult = True)
      else:
         sptCmds.sendDiagCmd('W%x,,22' % segmentType, timeout = 300)

      #Now spin it back up for subsequent operations
      sptCmds.gotoLevel('2')
      sptCmds.sendDiagCmd('U', timeout = 60)

   #======================================================================================================================================
   def fixSysArea(self):
      self.flush()
      sptCmds.gotoLevel('1')
      objMsg.printMsg(str("Performing system area bug fix: 6F"),objMsg.CMessLvl.DEBUG)
      accumulator = self.PBlock('G6F') #Do init writes
      res = sptCmds.promptRead(45, accumulator = accumulator )
      objMsg.printMsg(str(res),objMsg.CMessLvl.DEBUG)

   def prepSystemArea(self):
      self.flush()
      sptCmds.gotoLevel('1')

      ### Needed for CuHd bug- Remove for CuHd Lite: Matt Robinson DE contact
      objMsg.printMsg(str("Performing CuHd bug clearing writes: G6,0,100"),objMsg.CMessLvl.DEBUG)
      accumulator = self.PBlock('G6,0,100') #Do init writes
      res = sptCmds.promptRead(accumulator = accumulator)
      objMsg.printMsg(str(res),objMsg.CMessLvl.DEBUG)
      objMsg.printMsg(str("Performing CuHd bug clearing writes: G6,1,100"),objMsg.CMessLvl.DEBUG)
      accumulator = self.PBlock('G6,1,100') #Do init writes
      res = sptCmds.promptRead(accumulator = accumulator)
      objMsg.printMsg(str(res),objMsg.CMessLvl.DEBUG)
      ###
      objMsg.printMsg(str("Formatting system area: G61"),objMsg.CMessLvl.DEBUG)
      accumulator = self.PBlock('G61,060606') #Format system area
      res = sptCmds.promptRead(300, accumulator = accumulator)
      objMsg.printMsg(str(res),objMsg.CMessLvl.DEBUG)
      objMsg.printMsg(str("Initializing system area files: G6A"),objMsg.CMessLvl.DEBUG)
      accumulator = self.PBlock('G6A') #Init system files
      res = sptCmds.promptRead(300, accumulator = accumulator)
      objMsg.printMsg(str(res),objMsg.CMessLvl.DEBUG)

   def parseErrorLog(self, data):
      dataLines = data.split("\n")
      foundErrors = []
      shortErrors = []
      for row in dataLines:
         match = self.longD10LogPat.match(row)
         if match:
            foundErrors.append(match.groupdict())
         else:
            shortMatch = self.shortD10LogPat.match(row)
            if shortMatch:
               outDict = shortMatch.groupdict()
               shortErrors.append(outDict)
      return foundErrors, shortErrors

   def populateScreenDefectTable(self, data, screenName, spc_id = 1):
      """
      Add defects under the screen name to the table P_SCREEN_DEFECTS
      """
      if len(data) == 0:
         #Only try and print the table if we found defects
         return

      curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)

      for rec in data:
         self.dut.dblData.Tables('P_SCREEN_DEFECTS').addRecord(
            {
            'SPC_ID':               spc_id,
            'OCCURRENCE':           occurrence,
            'SEQ':                  curSeq,
            'TEST_SEQ_EVENT':       testSeqEvent,
            'SCREEN_NAME':          screenName,
            'HD_PHYS_PSN':          int(rec['HD_LGC_PSN']),
            'HD_LGC_PSN':           int(rec['HD_LGC_PSN']),
            'PHYS_TRK_NUM':         int(rec['TRK_PHYS_NUM'],16),
            'LGC_TRK_NUM':          int(rec['TRK_LGC_NUM'],16),
            'PHYS_SECTOR':          int(rec['SECTOR_PHYS'],16),
            'LGC_SECTOR':           int(rec['SECTOR_LGC'],16),
            'LBA':                  int(rec['LBA'],16),
            'RW_SENSE_CODE':        rec['RWERR'],
            'DIAGNOSTIC_ERR_CODE':  rec['DIAGERR'],
            })

      objMsg.printDblogBin(self.dut.dblData.Tables('P_SCREEN_DEFECTS'))

   def injectDefect(self, head, track, sector, readVerify = False):
      objMsg.printMsg("Injecting defect at head:%x; track:%x; sector:%x" % (head, track, sector))
      sptCmds.gotoLevel('2')
      self.seekTrack(track,head)
      sptCmds.sendDiagCmd('W%x,1,,1' % sector)
      if readVerify:
         self.readSector(sector-1,2,1,0)

   def dumpNonResidentGList(self, raiseParseFailure = False):
      """Displays non-resident Glist to results file.
      Returns a dictionary
      {'numEntries': integer, 'entries':[{}]}"""
      sptCmds.gotoLevel('T')
      if testSwitch.BF_0152505_231166_P_USE_V_CMD_FMT_DEF_LIST:

         GPat = re.compile('(?P<PBA>[0-9a-fA-F]+)\s+(?P<ERR_LENGTH>[0-9a-fA-F]+)\s+(?P<RW_FLAGS>\S+)\s+(?P<HD_PHYS_PSN>\S+)\s+(?P<PHYS_TRK_NUM>\S+)\s+(?P<PHYS_SECTOR>\S+)*')

      data = sptCmds.sendDiagCmd("V40",timeout = 300, printResult = True, loopSleepTime=0, DiagErrorsToIgnore = ['00005002'])

      NRG_Cnt_pat = 'Nonresident GList\s*(?P<numEntries>[a-fA-F\d]+)\s*entries returned'
      match = re.search(NRG_Cnt_pat, data)
      retDict = {}
      if testSwitch.virtualRun:
         retDict['numEntries'] = 0
      try:
         retDict['numEntries'] = int(match.groupdict()['numEntries'],16)
      except:
         if data.find("DiagError 00005002") > -1:
            retDict['numEntries'] = 0
         else:
            if not testSwitch.virtualRun and raiseParseFailure:
               objMsg.printMsg(traceback.format_exc())
               ScrCmds.raiseException(11044, "Unable to parse %s from buffer." % NRG_Cnt_pat)
      if testSwitch.BF_0152505_231166_P_USE_V_CMD_FMT_DEF_LIST:
         entries = []
         for line in data.splitlines():
            match = GPat.search(line)
            if match:
               entries.append(match.groupdict())

         retDict['entries'] = entries

      return retDict

   def dumpV40TotalEntries(self, raiseParseFailure = False):
      """Displays non-resident Glist to results file.
      Returns a dictionary
      {'numEntries': integer, 'entries':[{}]}"""
      sptCmds.gotoLevel('T')

      data = sptCmds.sendDiagCmd("V40",timeout = 300, altPattern = 'PhySctr    SFI', printResult = True, loopSleepTime=0.01, DiagErrorsToIgnore = ['00005002'])
      Total_Cnt_pat = 'Total entries available:\s*(?P<numEntries>[a-fA-F\d]+)\s'
      match = re.search(Total_Cnt_pat, data)
      retDict = {}
      if testSwitch.virtualRun:
         retDict['numEntries'] = 0
      try:
         retDict['numEntries'] = int(match.groupdict()['numEntries'],16)
      except:
         if data.find("DiagError 00005002") > -1:
            retDict['numEntries'] = 0
         else:
            if not testSwitch.virtualRun and raiseParseFailure:
               objMsg.printMsg(traceback.format_exc())
               ScrCmds.raiseException(11044, "Unable to parse %s from buffer." % Total_Cnt_pat)

         retDict['entries'] = entries

      return retDict

   def dumpResidentGList(self, raiseParseFailure = False):
      """Displays resident Glist to results file.
      Returns a dictionary
      {'numEntries': integer}"""
      sptCmds.gotoLevel('T')
      data = sptCmds.sendDiagCmd("V80",timeout = 300, printResult = True, loopSleepTime=0, DiagErrorsToIgnore = ['00005002'])
      NRG_Cnt_pat = 'Resident GList\s*(?P<numEntries>[a-fA-F\d]+)\s*entries returned'
      match = re.search(NRG_Cnt_pat, data)
      retDict = {}
      if testSwitch.virtualRun:
         retDict['numEntries'] = 0
      try:
         retDict['numEntries'] = int(match.groupdict()['numEntries'],16)
      except:
         if data.find("DiagError 00005002") > -1:
            retDict['numEntries'] = 0
         else:
            if not testSwitch.virtualRun and raiseParseFailure:
               objMsg.printMsg(traceback.format_exc())
               ScrCmds.raiseException(11044, "Unable to parse %s from buffer." % NRG_Cnt_pat)

      return retDict

   #======================================================================================================================================
   def dumpReassignedSectorList(self, returnAltListLBAS = 0, raiseException = None):
      """Displays RST List to results file"""

      if not testSwitch.unitTest:
         cmdDict = self.getCommandVersion('T','V') #{'majorRev':None,'minorRev':None}
      else:
         cmdDict = getattr(self, 'cmdVersion', {'majorRev': 15})

      sptCmds.gotoLevel('T')
      if raiseException != None and testSwitch.FE_0134462_399481_DUMP_V4_ALLOW_DIAG_NOT_TO_FAIL:
         objMsg.printMsg("Executing V4 command with raiseException = 0")
         data = sptCmds.sendDiagCmd("V4",timeout = 300, printResult = True, loopSleepTime=0, raiseException = raiseException)
      else:
         data = sptCmds.sendDiagCmd("V4",timeout = 300, printResult = True, loopSleepTime=0)

      if returnAltListLBAS:
         AltListLBAS = self.getAltListLBAS(data, cmdDict)

      if cmdDict['majorRev'] <= 14:
         if testSwitch.virtualRun and not testSwitch.unitTest:
            data = 'Total Total Total   0  2  0  0  0   Total'
         data = data.replace("\n","")
         totalDefectPattern = 'Total.*Total.*Total\s*[a-fA-F\d]+\s*(?P<NUMBER_OF_PENDING_ENTRIES>[a-fA-F\d]+)\s*[a-fA-F\d]+\s*[a-fA-F\d]+\s*(?P<NUMBER_OF_TOTALALTS>[a-fA-F\d]+).*Total'
      else:
         if testSwitch.virtualRun and not testSwitch.unitTest:
            data = 'Entries: 0000, Alts: 0000, Removed: 0000, Pending: 0000, BBMs: 0000'
         totalDefectPattern = 'Entries:\s*(?P<NUMBER_OF_TOTALALTS>[a-fA-F\d]+).*Pending:\s*(?P<NUMBER_OF_PENDING_ENTRIES>[a-fA-F\d]+)'
         totalDefectPattern = re.compile(totalDefectPattern, re.DOTALL) # smr support

      match = re.search(totalDefectPattern, data)
      if match:
         tempDict = match.groupdict()
         altListTotals =  self.convDictItems(tempDict, int, [16,])
      else:
         ScrCmds.raiseException(11044, "Unable to parse Reassigned Sector List: \npattern = %s\nbuffer = %s" % (totalDefectPattern, data))

      if returnAltListLBAS:
         return altListTotals, AltListLBAS
      else:
         return altListTotals

   #======================================================================================================================================
   def dumpReassignedSectorList_Apple(self, returnAltListLBAS = 0):
      """Displays RST List to results file"""

      if not testSwitch.unitTest:
         cmdDict = self.getCommandVersion('T','V') #{'majorRev':None,'minorRev':None}
      else:
         cmdDict = getattr(self, 'cmdVersion', {'majorRev': 15})

      sptCmds.gotoLevel('T')
      data = sptCmds.sendDiagCmd("V4",timeout = 300, printResult = True, loopSleepTime=0)

      if testSwitch.virtualRun and not testSwitch.unitTest:
         data = 'Total Total Total   0  2  0  0  0   Total'


      if returnAltListLBAS:
         AltListLBAS = self.getAltListLBAS(data, cmdDict)

      if cmdDict['majorRev'] <= 14:

         data = data.replace("\n","")
         totalDefectPattern = 'Total.*Total.*Total\s*(?P<NUMBER_OF_ALTS>[a-fA-F\d]+)\s*(?P<NUMBER_OF_PENDING_ENTRIES>[a-fA-F\d]+)\s*[a-fA-F\d]+\s*[a-fA-F\d]+\s*(?P<NUMBER_OF_TOTALALTS>[a-fA-F\d]+).*Total'
      else:
         totalDefectPattern = 'Entries:\s*(?P<NUMBER_OF_TOTALALTS>[a-fA-F\d]+).*Pending:\s*(?P<NUMBER_OF_PENDING_ENTRIES>[a-fA-F\d]+)'


      match = re.search(totalDefectPattern, data)
      if match:
         tempDict = match.groupdict()
         altListTotals =  self.convDictItems(tempDict, int, [16,])
      else:
         ScrCmds.raiseException(11044, "Unable to parse Reassigned Sector List: \npattern = %s\nbuffer = %s" % (totalDefectPattern, data))

      if returnAltListLBAS:
         return altListTotals, AltListLBAS
      else:
         return altListTotals

   def getAltListLBAS(self,data, cmdDict):
      'return the LBAs from the ALT list'
      lbaEntries = []

      if testSwitch.virtualRun and not testSwitch.unitTest:
         if testSwitch.FE_0174882_231166_P_PROCESS_PENDING_TO_ALT:
            data = """V4

Reassigned Sectors List
Entries: 0001, Alts: 0005, Removed: 0000, Pending: 0000

Idx  LBA          PBA          LLLCHS of LBA Wdg PLPCHS of PBA SFI    Hours Msecs  Status           BBM Mask
0000 000000000100 00000E9C3FCF 000000.0.0100 0F6 0537AD.0.0064 01BCE4 ----- ------ 0100000100000000 00000000
F3 T>"""
         else:
            data = 'hd sctr SFI \n 0CA00728 0 0 0 \n 1 1 1 \n Alt Pending'



      if cmdDict['majorRev'] <= 14:
         #parse out the lba table data
         lbaDefectPattern = '.*hd\s*sctr\s*SFI(?P<LBA_DATA>[\s\S]+)Alt\s*Pending'
         match = re.search(lbaDefectPattern, data)
         if match:
            #parse out the lbas from the table data
            tempDict =  match.groupdict()
            lbaData =  tempDict['LBA_DATA'].split('\n')
            lbaPattern = '\s*(?P<LBA>[a-fA-F\d]+)'

            for entry in lbaData:
               lbaMatch = re.search(lbaPattern, entry)
               if lbaMatch:
                  tempLBA = lbaMatch.groupdict()
                  tempLBAconv = self.convDictItems(tempLBA, int, [16,])
                  lbaEntries.append(tempLBAconv['LBA'])
      else:
         if testSwitch.FE_0174882_231166_P_PROCESS_PENDING_TO_ALT:

            #parse out the lba table data
            lbaDefectPattern = '(?P<Idx>[a-fA-F\d]+)\s+(?P<LBA>[a-fA-F\d]+)\s+(?P<PBA>[a-fA-F\d]+)\s+(?P<LCHS>[a-fA-F\d\.]+)\s+(?P<WDG>[a-fA-F\d]+)\s+(?P<PCHS>[a-fA-F\d\.]+)\s+(?P<SFI>[a-fA-F\d\.]+)\s+(?P<HRS>[a-fA-F\d-]+)\s+(?P<MSEC>[a-fA-F\d-]+)\s+(?P<STATUS>[01]+)\s+(?P<BBM_MASK>[01]+)'
            lines = data.splitlines()
            for line in lines:
               match = re.search(lbaDefectPattern, line)
               if match:
                  #parse out the lbas from the table data
                  tempDict =  match.groupdict()
                  tempDict['LBA'] = int(tempDict['LBA'], 16)
                  tempDict['PBA'] = int(tempDict['PBA'], 16)
                  tempDict['STATUS'] = int(tempDict['STATUS'], 2)
                  tempDict['BBM_MASK'] = int(tempDict['BBM_MASK'], 2)

                  lbaEntries.append(tempDict)
         else:
            #parse out the lba table data
            lbaDefectPattern = '.*Status\s*BBM\s*Mask(?P<LBA_DATA>[\s\S]+)'
            match = re.search(lbaDefectPattern, data)
            if match:
               #parse out the lbas from the table data
               tempDict =  match.groupdict()
               lbaData =  tempDict['LBA_DATA'].split('\n')
               lbaPattern = '\s*[a-fA-F\d]+\s*(?P<LBA>[a-fA-F\d]+)'

               for entry in lbaData:
                  lbaMatch = re.search(lbaPattern, entry)
                  if lbaMatch:
                     tempLBA = lbaMatch.groupdict()
                     tempLBAconv = self.convDictItems(tempLBA, int, [16,])
                     lbaEntries.append(tempLBAconv['LBA'])

      return lbaEntries

   #======================================================================================================================================
   def dumpRList(self):
      """Displays and returns the R-list sector and wedge counters."""
      objMsg.printMsg('Displaying RList')
      if testSwitch.BF_0171855_475827_SUPPORT_NEW_R_LIST_FORMAT_FOR_R_LIST_DUMP:
         pat_CurrSectors = '\s*CurrSectors\s*=\s*(?P<CURRSECTORS>[0-9a-fA-F]+)'
      pat = 'Sectors\s*=\s*(?P<SECTORS>[0-9a-fA-F]+)\s*Wedges\s*=\s*(?P<WEDGES>[0-9a-fA-F]+)'
      for retry in xrange(3):
         try:
            sptCmds.gotoLevel('1')
            if testSwitch.virtualRun:
               res = 'Sectors =  0\nWedges  =  0\n'
            else:
               try:
                  res = sptCmds.sendDiagCmd('N18', printResult = True,)
               except CRaiseException:
                  return (0,0) # Force error counts to 0 when code doesn't support the R-list
            res = res.replace("\n","")

            searchRes = re.search(pat, res)
            if testSwitch.BF_0171855_475827_SUPPORT_NEW_R_LIST_FORMAT_FOR_R_LIST_DUMP:
               searchResCurrSectors = re.search(pat_CurrSectors, res)
            if searchRes:
               sectors = int(searchRes.group('SECTORS'), 16)
               wedges = int(searchRes.group('WEDGES'), 16)
               return (sectors, wedges)
            elif (testSwitch.BF_0171855_475827_SUPPORT_NEW_R_LIST_FORMAT_FOR_R_LIST_DUMP and searchResCurrSectors):
               sectors = int(searchResCurrSectors.group('CURRSECTORS'), 16)
               wedges = 0
               return (sectors, wedges)
            else:
               ScrCmds.raiseException(11044, "Unable to parse R-List: \npattern = %s\nbuffer = %s" % (pat, res))
         except CRaiseException:
            if not testSwitch.BF_0177881_231166_RETRIES_FOR_R_LIST_DUMP:
               raise
      else:
         ScrCmds.raiseException(11044, "Unable to parse R-List: \npattern = %s\nbuffer = %s" % (pat, res))

   #======================================================================================================================================
   def dumpGrownDefectList(self):
      """
      Dumps the grown defect list to the screen and populates a dblog table using the 1>G79,2 command.
      """
      if not testSwitch.BF_0152505_231166_P_USE_V_CMD_FMT_DEF_LIST:
         GPat = '(?P<PBA>[0-9a-fA-F]+)\s(?P<ERR_LENGTH>[0-9a-fA-F]+)\s(?P<RW_FLAGS>\S+)*'
         grownPattern = re.compile(GPat)
      self.flush()

      if testSwitch.virtualRun:
         return
      if not testSwitch.BF_0152505_231166_P_USE_V_CMD_FMT_DEF_LIST:
         sptCmds.gotoLevel('1')

         res = sptCmds.sendDiagCmd("G79,2",timeout = 100, printResult = True, loopSleepTime=0)

      ######################## DBLOG Implementaion - Setup
      curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
      ########################
      foundGEntries = False
      if testSwitch.BF_0152505_231166_P_USE_V_CMD_FMT_DEF_LIST:

         matches = self.dumpNonResidentGList()['entries']
         res = ''

      else:
         matches = grownPattern.finditer(res)
      for match in matches:
         foundGEntries = True
         if testSwitch.BF_0152505_231166_P_USE_V_CMD_FMT_DEF_LIST:

            recDict = {
               'PBA': int(match['PBA'],16),
               'ERR_LENGTH': int(match['ERR_LENGTH'],16),
               'SPC_ID': 0,
               'OCCURRENCE': occurrence,
               'SEQ': curSeq,
               'TEST_SEQ_EVENT': testSeqEvent,
               'HD_PHYS_PSN': int(match['HD_PHYS_PSN'],16),
               'PHYS_TRK_NUM': int(match['PHYS_TRK_NUM'],16),
               'PHYS_SECTOR': int(match['PHYS_SECTOR'],16),
            }
         else:
            recDict = {}
            recDict.update(match.groupdict())
            recDict = {
               'PBA': int(recDict['PBA'],16),
               'ERR_LENGTH': int(recDict['ERR_LENGTH'],16),
               'SPC_ID': 0,
               'OCCURRENCE': occurrence,
               'SEQ': curSeq,
               'TEST_SEQ_EVENT': testSeqEvent,

            }
         try:
            self.dut.dblData.Tables('P_GROWN_DEFECT_LIST').addRecord(recDict)
         except TypeError:
            pass # Partial row parse

      if foundGEntries:
         objMsg.printDblogBin(self.dut.dblData.Tables('P_GROWN_DEFECT_LIST'))
      else:
         objMsg.printMsg("No Defects found:\n%s" % res)

   #======================================================================================================================================
   def dumpUseSlipList(self, startElement = '', elementCount = '', head = '', summaryOnly = True, printResult = True, spc_id = 1):
      """
      Exectute T> V8001,,,1 byt default to get the total user slips and the available slips
      """

      sptCmds.gotoLevel('T')


      if summaryOnly == True:
         resDict = {'SLIP_LIST_ENTRIES': -1, 'TOTAL_SPARE_SECTORS': -1}
         slipRegex = re.compile("\s*Total\s*Entries\s*(?P<SLIP_LIST_ENTRIES>[a-fA-F0-9]+)\s*Total\s*Slips\s*(?P<TOTAL_SPARE_SECTORS>[a-fA-F0-9]+)")
         result = sptCmds.sendDiagCmd("V8001,,,1", timeout = 120, printResult = printResult)
         if testSwitch.virtualRun:
            result =  """V8001,,,1
           0      0      0     0  0     0   0      0     0        9            0

Head 0: entries    305        slips      484
Head 1: entries    390        slips     4217
  Total Entries    695  Total Slips     469B

F3 T>"""
         match = slipRegex.search(result)
         if match:
            resDict = match.groupdict()

            curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
            self.dut.dblData.Tables('P_USER_SLIP_LIST').addRecord(
                  {
                     'SPC_ID' : spc_id,
                     'OCCURRENCE' : occurrence,
                     'SEQ' : curSeq,
                     'TEST_SEQ_EVENT' : testSeqEvent,
                     'SLIP_LIST_ENTRIES': int(resDict['SLIP_LIST_ENTRIES'],16),
                     'TOTAL_SPARE_SECTORS': int(resDict['TOTAL_SPARE_SECTORS'],16),
                  })
            objMsg.printDblogBin(self.dut.dblData.Tables('P_USER_SLIP_LIST'))
            self.dut.driveattr['SLIP_LIST_ENTRIES'] = int(resDict['SLIP_LIST_ENTRIES'],16)
         return resDict
      else:
         ops = []
         #convert elements for transmission
         for elem in ['1', head, startElement, elementCount]:
            if elem != '':
               elem = hex(elem)
            ops.append(elem)

         result = sptCmds.sendDiagCmd("V%s" % (','.join(ops),), timeout = 1000, printResult = printResult)


         return res

   #======================================================================================================================================
   def dumpActiveServoFlaws(self):
      """
      Dumps the active servo flaw table using the T>V command
      """
      if testSwitch.virtualRun:
         pass

      self.flush()
      sptCmds.gotoLevel('T')
      accumulator = self.PBlock("V8")
      res = sptCmds.promptRead(100,0, accumulator = accumulator)
      objMsg.printMsg  ("\nActive Servo Flaw List\n%s" % res)
      if testSwitch.BF_0136108_231166_P_INCL_ASFT_IN_FORMAT_REQ:
         del accumulator
         ret= {}
         totalMatch = re.search('Total Entries\s+(?P<Total_Entries>\w+)',  res)
         totalDefects = 0
         if totalMatch:
            totalDefects = int(totalMatch.groupdict()['Total_Entries'],16)
         ret['Total Entries'] = totalDefects

         return ret

   def getSmartAttribute(self, attrNum, printResult = False):
      sptCmds.gotoLevel('1')
      data = sptCmds.sendDiagCmd("N5", printResult = printResult)

      attrRow = re.compile('(?P<AttributeNum>[0-9a-fA-F]+)\s+(?P<Flags>[0-9a-fA-F]+)\s+(?P<Normalized>[0-9a-fA-F]+)\s+(?P<WorstEver>[0-9a-fA-F]+)\s+(?P<Raw>[0-9a-fA-F]+)')
      rows = data.splitlines()
      rowDict = retVal = None
      for line in rows:
         match = attrRow.search(line)
         if match:
            rowDict = match.groupdict()
            if DEBUG:
               objMsg.printMsg("rowDict: %s" % (rowDict,))
            if int(rowDict['AttributeNum'], 16) == attrNum: #7 is seek nums
               break
      if rowDict and int(rowDict['AttributeNum'], 16) == attrNum:
         objMsg.printMsg("Found attr %X: results: %s" % (attrNum, rowDict,))
         rowDict['Raw'] = int(rowDict['Raw'],16)
         retVal = rowDict.copy()

      return retVal

   def EnableDisableShockSensor(self, ShockSensorString):
      """
      Enables or disables the shock sensor depending on the string sent
      Uses Level 5> C command with 0x716F or 0x706F
      """
      if int( ( ShockSensorString.split(',') )[0], 16) == 815471:
         objMsg.printMsg("Disable Shock Sensor - Issuing Level 5> %s \n" % ShockSensorString)
      else:
         objMsg.printMsg("Enable Shock Sensor - Issuing Level 5> %s \n" % ShockSensorString)

      if testSwitch.virtualRun:
         pass

      # Goto Level T first
      sptCmds.gotoLevel(level='T')
      #Goto Level 5 and issue the Servo command
      sptCmds.gotoLevel(level='5')
      accumulator = self.PBlock(ShockSensorString)
      result = sptCmds.promptRead(100,0, accumulator = accumulator)
      objMsg.printMsg  ("Shock Sensor State\n%s" % result)


   def CheckNumEntriesInGList(self):
      """
      Pulls the Non-resident G list and the Reassigned Sectors List using the T>T>V40 and TV4 commands
      Parses the return data and sums up all defect list entries (Resident, Non-Resident, Pending etc.
      If unable to query and parse any list count, 0xFFFF will be returned.
      """
      if testSwitch.virtualRun:
         return 5
      else:
         sptCmds.gotoLevel('T')
         try:
            v40 = sptCmds.sendDiagCmd('V40',timeout = 300, printResult = False, loopSleepTime=0, DiagErrorsToIgnore = ['00005002'])
            objMsg.printMsg  ('Non-Resident G List\n%s' % v40)
            NumSplit = (v40.split(':'))[1].split('PBA')
            NumEntries = int((v40.split(':')[1].split('PBA')[0].split('\r')[0]), 16)

            v4 = sptCmds.sendDiagCmd('V4',timeout = 300, printResult = False, loopSleepTime=0, DiagErrorsToIgnore = ['00005002'])
            objMsg.printMsg  ('Reassigned Sectors List\n%s' % v4)
            NumEntries += int((v4.split(':')[1].split(',')[0].split('\r')[0].strip()), 16)
            NumEntries += int((v4.split(':')[2].split(',')[0].split('\r')[0].strip()), 16)
            NumEntries += int((v4.split(':')[4].split('Idx')[0].split('\r')[0].strip()), 16)
            objMsg.printMsg  ('Total List Entry Count:%s' % NumEntries)
            return NumEntries

         except:
            objMsg.printMsg  ('Unable to parse G List')
            return 0xFFFF


   def mediaSyncDefectScreen2(self):
      '''Change SMTRESH detect SM errors in Serial Format more aggressively'''
      self.enableDiags()

      if not self.currLevel == '7':
         self.gotoLevel('7')
      Value = getattr(TP,'mediaSyncDefectScreen2',"0006")
      if not testSwitch.FE_0121280_399481_UPDATE_TO_MEDIA_SYNC_DEFECT_SCREENS:
         CMD ='I' + Value + ',1,4,0,25,,,2'
         result = sptCmds.sendDiagCmd(CMD, timeout = 30)
         objMsg.printMsg('Media Sync Defect Screen2.  Set %s = %s' % (CMD,result))
      else:
         CMD = 'I' + Value + ',1,4,0,25'
         result = sptCmds.sendDiagCmd(CMD, timeout = 30)
         objMsg.printMsg('Media Sync Defect Screen2.  Set %s = %s' % (CMD,result))
         CMD = 's1,d7,06'
         result = sptCmds.sendDiagCmd(CMD, timeout = 30)
         objMsg.printMsg('Media Sync Defect Screen2.  Set %s = %s' % (CMD,result))
      res = sptCmds.sendDiagCmd('t,1,D7', timeout = 100)
      if res.find(Value) > -1 or testSwitch.virtualRun:
         return
      else:
         ScrCmds.raiseException(13426, "Unable to set %s to %s   " % (CMD, Value))

   def mediaSyncDefectScreen(self):
      '''Changes Phase Update Gain slower to detect MSD type defect'''
      self.enableDiags()

      if not self.currLevel == '7':
         self.gotoLevel('7')
      Value = getattr(TP,'mediaSyncDefectScreen',"309A")
      if not testSwitch.FE_0121280_399481_UPDATE_TO_MEDIA_SYNC_DEFECT_SCREENS:
         CMD ='I' + Value + ',1,4,0,17,,,2'
         result = sptCmds.sendDiagCmd(CMD, timeout = 30)
         objMsg.printMsg('Media Sync Defect Screen.   Set %s = %s' % (CMD,result))
      else:
         CMD = 'I' + Value + ',1,4,0,17'
         result = sptCmds.sendDiagCmd(CMD, timeout = 30)
         objMsg.printMsg('Media Sync Defect Screen.   Set %s = %s' % (CMD,result))
         CMD = 's1,A4,' + Value
         result = sptCmds.sendDiagCmd(CMD, timeout = 30)
         objMsg.printMsg('Media Sync Defect Screen.   Set %s = %s' % (CMD,result))

      res = sptCmds.sendDiagCmd('t,1,A4', timeout = 100)

      if res.find(Value) > -1 or testSwitch.virtualRun:
         return
      else:
         ScrCmds.raiseException(13426, "Unable to set %s to %s   " % (CMD, Value))

   if testSwitch.FE_0121272_399481_RESTORE_PHUGR:
      def restorePHUGRToValThree(self):
         '''Restore PHUGR value to 3'''
         self.enableDiags()

         if not self.currLevel == '7':
            self.gotoLevel('7')
         Value = getattr(TP,'mediaSyncDefectScreen',"309B")
         CMD = 'I' + Value + ',1,4,0,17'
         result = sptCmds.sendDiagCmd(CMD, timeout = 30, DiagErrorsToIgnore = ['0000E009'])
         objMsg.printMsg('restorePHUGRToValThree.   Set %s = %s' % (CMD,result))
         CMD = 's1,A4,' + Value
         result = sptCmds.sendDiagCmd(CMD, timeout = 30)
         objMsg.printMsg('restorePHUGRToValThree.   Set %s = %s' % (CMD,result))

   @staticmethod
   def createFormatCmd(formatOptions):
      baseCMD = ['m0','','','','','','','22','','','','']
      baseCMD[1] = '%x'%((formatOptions.get('DisableDataSyncRewrites',0)<<6)\
                        + (formatOptions.get('SeaCOSFormat',0)<<5)\
                        + (formatOptions.get('SkipReFormat',0)<<4)\
                        + (formatOptions.get('EnableLogging',0)<<3)\
                        + (formatOptions.get('DisableCertify',0)<<2)\
                        + (formatOptions.get('DisableWritePass',0)<<1)\
                        + (formatOptions.get('CorruptPrimaryDefects',1)<<0))

      if testSwitch.FE_0153930_007955_P_FMT_CMD_DONT_DEFAULT_DefectListOptions_TO_3:
         if formatOptions.get('DefectListOptions',None) != None:
            baseCMD[2]  = '%x'%formatOptions['DefectListOptions']
      else:
         baseCMD[2] = '%x'%formatOptions.get('DefectListOptions',3)

      if formatOptions.get('MaxWriteRetryCount',None) != None:
         baseCMD[3]  = '%x'%formatOptions['MaxWriteRetryCount']
      if formatOptions.get('MaxReadRetryCnt',None) != None:
         baseCMD[4]  = '%x'%formatOptions['MaxReadRetryCnt']
      if formatOptions.get('MaxIterationCount',None) != None:
         baseCMD[5]  = '%x'%formatOptions['MaxIterationCount']
      if formatOptions.get('CertReWriteThresh',None) != None:
         baseCMD[6]  = '%x'%formatOptions['CertReWriteThresh']
      if formatOptions.get('FormatDataPattern',None) != None:
         baseCMD[8]  = '%x'%formatOptions['FormatDataPattern']

      if testSwitch.extern.RW_FORMAT_APPLY_SECONDARY_ER_MODE:
         if formatOptions.get('MaxWriteRetryCount2',None) != None:
            baseCMD[9]  = '%x'%formatOptions['MaxWriteRetryCount2']
         if formatOptions.get('MaxReadRetryCount2',None) != None:
            baseCMD[10]  = '%x'%formatOptions['MaxReadRetryCount2']
         if formatOptions.get('TLevel2',None) != None:
            baseCMD[11]  = '%x'%formatOptions['TLevel2']
         if formatOptions.get('NumDefectsBeforeSkippingTrack',None) != None:
            baseCMD[12]  = '%x'%formatOptions['NumDefectsBeforeSkippingTrack']
      elif formatOptions.get('NumDefectsBeforeSkippingTrack',None) != None:
         baseCMD[9]  = '%x'%formatOptions['NumDefectsBeforeSkippingTrack']

      baseCMD = (','.join([i for i in baseCMD])).strip(',')
      return baseCMD

   #======================================================================================================================================
   def formatUserPartition(self, formatOptions = {}):
      """
      Format the User Partition using the F3 Diagnostic command

      Format Options
      =======
      OverallTimeout         (Default = 86400 - 24hrs.)  Maximum elapsed time for the entire format operation.
      formatTimeout          (Default = 7200)            Incremental timeout to apply to format; Incoming chars resets timeout counter
      collectBERdata         (Default = 1)               Collect BER data following format

      Format Partition Diagnostic parameters:
         Parameter1:
            DisableDataSyncRewrites  (Default = 0) : Bit 6: Disable Track Re-write for Data Sync Time-out Errors.
            SeaCOSFormat             (Default = 0) : Bit 5: Enable SeaCOS XF Space Format.
            SkipReFormat             (Default = 0) : Bit 4: Enable Zone Re-format Skipping.
            EnableLogging            (Default = 0) : Bit 3: Enable Event-based Format Logging. (Verbose Mode)
            DisableCertify           (Default = 0) : Bit 2: Disable User Partition Certify. (No read pass)
            DisableWritePass         (Default = 0) : Bit 1: Disable User Partition Format. (Quick Format)
            CorruptPrimaryDefects    (Default = 1) : Bit 0: Corrupt User Partition Primary Defects.
         Parameter2:
            DefectListOptions        (Default = 3) : Bit 2: Process Active Log,.Bit 1: Process Primary Lists,.Bit 0: Process Grown Defect Lists.
         Parameter3:
            MaxWriteRetryCount       (Default = None) : Maximum write retries to be applied to an LBA during format
         Parameter4:
            MaxReadRetryCnt          (Default = None) : Maximum LBA certification count/ read retries
         Parameter5:
            MaxIterationCount        (Default = None) : Max iteration count applied during format
         Parameter6:
            CertReWriteThresh        (Default = None) : Track Rewrite During Certify Retry Threshold.
         Parameter8:
            FormatDataPattern        (Default = None) : Data pattern written by format write pass
         Parameter9:
            NumDefectsBeforeSkippingTrack (Default = None) : Number of defects allowed bofore skipping entire track

      @param formatOptions: Input dictionary to define the formating options
      """

      ######################## DBLOG Implementaion- Setup
      curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(511)
      self.format_startTime = time.time()
      ########################
      formatTimeoutEval = Utility.timoutCallback(formatOptions.get('OverallTimeout',86400), ScrCmds.raiseException, (10566,"Maximum timeout in format expired %d" % formatOptions.get('OverallTimeout',86400)))

      formatTimeout = Utility.timoutCallback(formatOptions.get('formatTimeout',7200), ScrCmds.raiseException, (10566,"Incremental response timeout in format expired %d" % formatOptions.get('formatTimeout',7200)))

      self.flush()

      statusPat = '\s*R/W Sense\s*(?P<status>\d{1,9}\s*),\s*R/W Error\s*(?P<error>[0-9A-Za-z]{1,9})'
      pattern = 'User Partition Format'
      pattern_EC = 'User Partition Format Failed - Elapsed Time .*\n*' + statusPat
      pattern_PASS = '\s*User Partition Format Successful - Elapsed Time .*'
      pat2 = 'Process Defect List Error\n*' + statusPat
      formatCmd = 'm0,,,,,,,22'
      percComplPat = 'User Partition Format\s*(?P<pecCompl>[0-9a-fA-F]{1,2})%\s*complete'
      cmdLevel = 'T'

      baseCMD = ['m0','','','','','','','22','','','','','','','']

      if testSwitch.HARD_CODE_SERIAL_FORMAT_CMD:
         #baseCMD = 'm0,89,2,15,a,103,,22,,15,a,103,32,0505,0202'
         if self.dut.BG in ['SBS'] and ConfigVars[CN].get('FormatWWriteOnly', 1):
            drv_fw = self.dut.driveattr.get('CODE_VER', DriveAttributes.get('CODE_VER', 'NONE'))
            pattern12 = '\w+\.\w+\.(?P<FW_VER>[\dA-Fa-f]+)\.\w*'
            match = re.search(pattern12, drv_fw)
            fw_ver = 0
            if match:
               fw_ver = match.groupdict()['FW_VER']
               if 'CD' in fw_ver or 'CC' in fw_ver or 'AA' in fw_ver: #CC4618 #AA7777 #AA6994
                  fw_ver = int(fw_ver[2:6])
               else: #461810
                  fw_ver = int(fw_ver[0:4])
            if fw_ver >= 4638:
               baseCMD[1] = '8D' # Do Write Only
            else:
               baseCMD[1] = '89' # The F3 code is not with EDAC fix.
         else:
            baseCMD[1] = '89'
         
         baseCMD[2] = '3'  # Need to change from 2 to 3 due to new features in skip zone - previously F3 hardcode to 3, so this value doesn't matter
         if self.dut.BG in ['SBS']:
            if int(DriveAttributes.get('PROC_CTRL19', '0')) == 2 or int(self.dut.driveattr.get('PROC_CTRL19', 0)) == 2:
               baseCMD[3] = '1'  # write retry
            else:
               baseCMD[3] = '3'  # write retry
            if len(self.dut.rerunReason) > 1 and self.dut.rerunReason[1] in ['SERIAL_FMT']:
               baseCMD[3] = 'F'  # write retry
         else:
            baseCMD[3] = '3'  # write retry
         baseCMD[4] = 'a'
         baseCMD[5] = TP.formatIteration
         baseCMD[6] = ''
         baseCMD[7] = '22'
         baseCMD[8] = ''
         baseCMD[9] = 'f' #'15'
         baseCMD[10] = 'a'
         baseCMD[11] = TP.formatIteration
         baseCMD[12] = '32'
         baseCMD[13] = '0505'
         baseCMD[14] = '0202'
      else:
         objMsg.printMsg("\nFormating drive with options:\n%s" % ('\n'.join(["\t%-35s:\t%s" % (key,value) for key,value in formatOptions.items()]),))
         self.flush()
         baseCMD[1] = '%x'%((formatOptions.get('DisableTrackRewrite',0)<<7)\
                        + (formatOptions.get('DisableDataSyncRewrites',0)<<6)\
                        + (formatOptions.get('SeaCOSFormat',0)<<5)\
                        + (formatOptions.get('SkipReFormat',0)<<4)\
                        + (formatOptions.get('EnableLogging',0)<<3)\
                        + (formatOptions.get('DisableCertify',0)<<2)\
                        + (formatOptions.get('DisableWritePass',0)<<1)\
                        + (formatOptions.get('CorruptPrimaryDefects',1)<<0))

         baseCMD[2] = '%x'%formatOptions.get('DefectListOptions',3)
         if formatOptions.get('MaxWriteRetryCount',None) != None:
            baseCMD[3]  = '%x'%formatOptions['MaxWriteRetryCount']
         if formatOptions.get('MaxReadRetryCnt',None) != None:
            baseCMD[4]  = '%x'%formatOptions['MaxReadRetryCnt']
         if formatOptions.get('MaxIterationCount',None) != None:
            baseCMD[5]  = '%x'%formatOptions['MaxIterationCount']
         if formatOptions.get('CertReWriteThresh',None) != None:
            baseCMD[6]  = '%x'%formatOptions['CertReWriteThresh']
         if formatOptions.get('FormatDataPattern',None) != None:
            baseCMD[8]  = '%x'%formatOptions['FormatDataPattern']

         if testSwitch.extern.RW_FORMAT_APPLY_SECONDARY_ER_MODE:
            if formatOptions.get('MaxWriteRetryCount2',None) != None:
               baseCMD[9]  = '%x'%formatOptions['MaxWriteRetryCount2']
            if formatOptions.get('MaxReadRetryCount2',None) != None:
               baseCMD[10]  = '%x'%formatOptions['MaxReadRetryCount2']
            if formatOptions.get('TLevel2',None) != None:
               baseCMD[11]  = '%x'%formatOptions['TLevel2']
            if formatOptions.get('NumDefectsBeforeSkippingTrack',None) != None:
               baseCMD[12]  = '%x'%formatOptions['NumDefectsBeforeSkippingTrack']
            if formatOptions.get('BoxPaddingHeight',None) != None:
               baseCMD[13]  = '%04x'%formatOptions['BoxPaddingHeight']
            if formatOptions.get('BoxPaddingWidth',None) != None:
               baseCMD[14]  = '%04x'%formatOptions['BoxPaddingWidth']
         elif formatOptions.get('NumDefectsBeforeSkippingTrack',None) != None:
            baseCMD[9]  = '%x'%formatOptions['NumDefectsBeforeSkippingTrack']

      if testSwitch.SINGLEPASSFLAWSCAN_WRITE_FMT and self.dut.prevOperStatus["%s_TEST_DONE" % (self.dut.nextOper)] != "PASS": # disable certify tracks if SPF and not code upgrade
         objMsg.printMsg("Disable User Partition Certify since Single Pass Flawscan is ON", objMsg.CMessLvl.DEBUG)
         baseCMD[1] = '8d'

      if testSwitch.SKIPZONE: # and self.skipznDone == 1:
         baseCMD[2] = '3'   #  full serial format command.  T>m0,89,3,15,a,103,,22,15,a,103,32,0505,0202

      # Set up command string for format
      baseCMD = (','.join([i for i in baseCMD])).strip(',')

      if formatOptions.get('collectBERdata',1) and not formatOptions.get('DisableCertify',0):
         self.enableRWStats()                  # Enable BER statistics collection during format (only if performing cerify pass)

      objMsg.printMsg("Starting user partition format: ",objMsg.CMessLvl.DEBUG)
      objMsg.printMsg("Sending Command: %s" %baseCMD,objMsg.CMessLvl.VERBOSEDEBUG)


      if testSwitch.FE_0137804_399481_P_BIE_SERIAL_FORMAT and formatOptions["BIE_THRESH"]:
         self.setupBIEThresh(
            formatOptions["BIE_THRESH"],
            formatOptions["ITER_LOAD"],
            printResult = True
            )
         if testSwitch.FE_0163194_395340_P_FIX_ECC_LV_FOR_MAXDELTARAW:
            #----- Turn on Rd/Wr ---- By Pramual HM&RW
            self.enableRWStats()
            #---- End ----

         if not testSwitch.FE_0142146_426568_P_SKIP_BIE_Y_D_COMMANDS:
            sptCmds.gotoLevel('2')
            sptCmds.sendDiagCmd('Y%s' % formatOptions["RETRIES"], printResult = True)
            sptCmds.sendDiagCmd('D%X' % formatOptions["ITER_CNT"], printResult = True)

      if testSwitch.virtualRun and not testSwitch.unitTest:
         return

      sptCmds.gotoLevel(cmdLevel)

      try:
         accumulator = self.PBlock(baseCMD)     # Send Format command
         result = ''
         prompt = re.compile(self.prPat)
         percCom = re.compile(percComplPat)
         lastPerc = ''
         matches = []
         lastResult = ''
         textBufferLimit = -512

         try:
            for result in accumulator:
               formatTimeout()
               formatTimeoutEval()
               time.sleep(10)                                        # Sleep for 10sec to reduce CM overhead

               curRes = result[-20:]                                 # Grab the last 20 chars in the buffer for status updating

               matches = prompt.findall(result[textBufferLimit:])    # Check for prompt.. if found then format is complete
               if len(matches) > 0:
                  break                                              # Exit if we found a completion match
               elif sptCmds.getFlashCodeMatch(result):
                  formatTimeout.forceError()                         # If we flash LED'd then abort

               percMatch = percCom.findall(result[textBufferLimit:]) # Look and see if we received a new percent complete from the drive
               if DEBUG > 0:
                  TraceMessage( "percMatch: %s"%`percMatch` )

               if lastResult != curRes:                              # If we received new data let's optionally print it out and reset the timeout counters
                  if DEBUG > 0:
                     objMsg.printMsg("last 20 chars: %s" % curRes,objMsg.CMessLvl.DEBUG)
                  lastResult = curRes
                  formatTimeout.resetTimeout()

               #If we received a new percent complete different from last then let the user know
               if len(percMatch) > 0 and lastPerc != percMatch[-1]:
                  lastPerc = percMatch[-1]
                  formatTimeout.resetTimeout()

                  try:
                     objMsg.printMsg(str("Format Percent Complete: %s" % str(eval("%s" % percMatch[-1]))),objMsg.CMessLvl.DEBUG)
                  except:
                     objMsg.printMsg(str("exact print failed... %s,len=%d" % (percMatch[-1],len(matches))),objMsg.CMessLvl.DEBUG)

         except:     # We timed out so lets grab all data and perform a full buffer search
            matches = prompt.findall(result)
            if len(matches) == 0:
               accumulator = self.PBlock('')

               result += iter(accumulator).next()
               flashinfo = sptCmds.getFlashCodeMatch(result)
               if flashinfo == None:
                  objMsg.printMsg(str(result),objMsg.CMessLvl.DEBUG)
                  ScrCmds.raiseException(10566, "Reached Timeout")
               else:

                  objMsg.printMsg(result, objMsg.CMessLvl.DEBUG)
                  ScrCmds.raiseException(11231, "FlashLED Error %s" % flashinfo.groupdict() + result + self.lastCommand)

         self.SerialFormatInformation(result)         # Call this function to support New Serial Format Debug Information
         sptCmds.disableAPM()

         match = re.search(pattern,result)            # Lets search for format completion status
         if DEBUG == 1:
            objMsg.printMsg(str(result),objMsg.CMessLvl.DEBUG)

         tempDic = {}

         if not match == None:                        # Search for failure pattern
            match = re.search(pattern_EC,result)
            if match == None:                         # If no failure pattern then lets search for passing pattern
               match = re.search(pattern_PASS,result)
               tempDic = {'status':'1','error':'80'}
            else:                                     # Grab the error code if the 1st match was successfull
               tempDic = match.groupdict()

            try:                                      # Translate the rw error code if there is one.
               rwExpl = translateRwErrorCode(int(tempDic['error'],16))
               objMsg.printMsg("RW Error Descrip: %s=%s" % (tempDic['error'],str(rwExpl)), objMsg.CMessLvl.DEBUG)
            except:
               objMsg.printMsg(traceback.format_exc())

            try:                                      # Let the user know how the format operation went
               objMsg.printMsg(str("Format verification: status=%s; error=%s" % (tempDic['status'],tempDic['error'])),objMsg.CMessLvl.DEBUG)
            except:
               objMsg.printMsg("Parse Error: \n%s\nMatch:\n%s" % (result,str(match)))

            # Check the completion code is 80.. passing status
            if not int(tempDic['status']) == 1 and \
               not eval("int(" + '0x' + tempDic['error'] + ")") == 80:
               objMsg.printMsg(result, objMsg.CMessLvl.DEBUG)
               ScrCmds.raiseException(10219,"Failed User Format; status:%s, error:%s" % (tempDic['status'],tempDic['error']))

         else: # No completion pattern was found lets look for defect list processing failure
            match = re.search(pat2, result)
            if not match == None:
               tempDic = match.groupdict()
               try:
                  rwExpl = translateRwErrorCode(int(tempDic['error'],16))
                  objMsg.printMsg("RW Error Descrip: %s=%s" % (tempDic['error'],str(rwExpl)), objMsg.CMessLvl.DEBUG)
               except:
                  pass
               objMsg.printMsg(str("Defect List Processing: status=%s; error=%s" % (tempDic['status'],tempDic['error'])),objMsg.CMessLvl.DEBUG)
               if not int(tempDic['status']) == 1 and \
                  not  eval("int(" + '0x' + tempDic['error'] + ")") == 80:
                  objMsg.printMsg(result, objMsg.CMessLvl.DEBUG)
                  ScrCmds.raiseException(10219,"Defect List Processing; status:%s, error:%s" % (tempDic['status'],tempDic['error']))
            else:
               objMsg.printMsg(result, objMsg.CMessLvl.DEBUG)
               TraceMessage(result)
               ScrCmds.raiseException(10219,"Unknown Format Failure! Passing Status not recieved: %s" % result[-256:])
      finally:
         ecEx = traceback.format_exc()
         if ecEx.find('None') > -1:
            objMsg.printMsg("Format error: %s" % ecEx)

         ######################## DBLOG Implementaion- Closure
         curTime = time.time()
         self.dut.objSeq.curRegTest = 0

         self.dut.dblData.Tables('TEST_TIME_BY_TEST').addRecord(
               {
               'SPC_ID': 0,
               'OCCURRENCE': occurrence,
               'SEQ':curSeq,
               'TEST_SEQ_EVENT': testSeqEvent,
               'TEST_NUMBER': 511,                 # 511 = Serial Format
               'ELAPSED_TIME': '%.2f' % (curTime-self.format_startTime),
               'PARAMETER_NAME':'SPT Format',
               })

         ########################
         if formatOptions.get('collectBERdata',1) and not formatOptions.get('DisableCertify',0):
         # We need both Write and Read data for GOTF to work so don't send the data if it is a write only format

            zoneData=[]
            try:
               if not ecEx.upper().find('TIMEOUT') > -1:
                  objMsg.printMsg("Enable BER statistics collection during format.")
                  zoneData = self.getZoneBERData(tLevel = formatOptions['MaxIterationCount'], readRetry = formatOptions['MaxReadRetryCnt'], lowerBaudRate = True, spc_id=formatOptions.get('spc_id',1))
                  self.SpareSectorStatistics()
            except:
               objMsg.printMsg("Zone BER Failure: %s" % traceback.format_exc())

            #BER Screening
            if zoneData==[] and len(getattr(TP,"BERScreenList",{}))!= 0:
               ScrCmds.raiseException(11254, "BER Screening Failure - No zoneData returned!")
            else:
               if hasattr(TP,"BERSpecs"):
                  self.getBER(zoneData, 2)
                  self.screenBER(self.BERInfo, TP.BERScreenList, raiseException=True)
            if testSwitch.WA_0147953_395340_P_MAX_DELTA_RAW_ERROR_RATE_AFTER_RE_FORMAT:
               self.getMaxDeltaRAW(printResult = True)

            if testSwitch.FE_0332210_305538_P_SERFMT_OTF_SCREEN and self.dut.BG not in ['SBS']:
               objMsg.printMsg("Screening: OTF_ERROR_RATE <= %s or ( OTF_ERROR_RATE <= %s and RAW_ERROR_RATE <= %s )" % (str(TP.SerFmt_OTF_Spec), str(TP.SerFmt_OTF_Combo_Spec), str(TP.SerFmt_RAW_Combo_Spec)))
               for zoneRec in zoneData:
                  try:
                     curZone = int(zoneRec['DATA_ZONE'], 16)
                     curRbit = float(zoneRec['RBIT'])
                     curOTF  = float(zoneRec['OTF'])
                     curRAW  = float(zoneRec['RRAW'])
                  except ValueError:
                     curRbit = 0 # to skip the screening
                  else:
                     if curRbit <= 0.0 or curOTF <= 0.0 or curRAW <= 0.0: # skip screening if invalid RBIT, OTF or BER values
                        curRbit = 0
                  if curRbit > 0 and curZone in xrange(self.dut.numZones) and curZone not in TP.SerFmt_Screen_Ignore_Zone:
                     if curOTF <= TP.SerFmt_OTF_Spec or (curOTF <= TP.SerFmt_OTF_Combo_Spec and curRAW <= TP.SerFmt_RAW_Combo_Spec):
                        objMsg.printMsg("Screening: OTF = %s, RAW = %s @ Hd %s Zn %d" % (zoneRec['OTF'], zoneRec['RRAW'], zoneRec['HD_PHYS_PSN'], curZone))
                        ScrCmds.raiseException(14651, "Failed for OTF = %s, RAW = %s @ Head : [%s]" % (zoneRec['OTF'], zoneRec['RRAW'], zoneRec['HD_PHYS_PSN']))
               objMsg.printMsg("=== PASS ===")

         if testSwitch.FE_0137804_399481_P_BIE_SERIAL_FORMAT and formatOptions["BIE_THRESH"]:
            self.disableBIEDetector(printResult = True)

         if not ecEx.upper().find('TIMEOUT') > -1:
            self.dumpActiveServoFlaws()
            self.dumpGrownDefectList()
         self.displayHornPlot()
      return tempDic

   #======================================================================================================================================
   if testSwitch.WA_0147953_395340_P_MAX_DELTA_RAW_ERROR_RATE_AFTER_RE_FORMAT:
      def getMaxDeltaRAW(self,printResult = False):
         try:
            p_format = self.dut.dblData.Tables('P_FORMAT_ZONE_ERROR_RATE').tableDataObj()
            if printResult:
               objMsg.printMsg("DATA P_FORMAT_ZONE_ERROR_RATE : %s" % p_format)
            RawDATA1 = []
            RawDATA2 = []
            DeltaRaw = []
            for i in p_format:
               if testSwitch.FE_0163194_395340_P_FIX_ECC_LV_FOR_MAXDELTARAW:
                  if i['ECC_LEVEL'] == 32:
                     if i['RAW_ERROR_RATE'] != '':
                        RawDATA1.append(i['RAW_ERROR_RATE'])
                     else:
                        RawDATA1.append('0.0')
                  else:
                     if i['RAW_ERROR_RATE'] != '':
                        RawDATA2.append(i['RAW_ERROR_RATE'])
                     else:
                        RawDATA2.append('0.0')
               else:
                  if i['ECC_LEVEL'] == '':
                     if i['RAW_ERROR_RATE'] != '':
                        RawDATA1.append(i['RAW_ERROR_RATE'])
                     else:
                        RawDATA1.append('0.0')
                  else:
                     if i['RAW_ERROR_RATE'] != '':
                        RawDATA2.append(i['RAW_ERROR_RATE'])
                     else:
                        RawDATA2.append('0.0')
            for i in range(len(RawDATA1)):
               DeltaRaw.append(float(RawDATA1[i]) - float(RawDATA2[i]))
            if printResult:
               objMsg.printMsg("Delta Raw Error all zone : %s" % DeltaRaw)
            self.dut.driveattr['DELTA_ERROR_RATE'] = float("%.4s" % max(DeltaRaw))
         except:
            objMsg.printMsg("CAN NOT KEEP DATA P_FORMAT_ZONE_ERROR_RATE")
            self.dut.driveattr['DELTA_ERROR_RATE'] = 'NONE'

   #======================================================================================================================================
   def PreSkipZone(self, params = {}):
      from Process import CProcess
      from RdWr import CSkipZnFile
      oSkZnFile = CSkipZnFile()
      self.numUserZones = self.dut.numZones
      objMsg.printMsg("numUserZones = %d" % self.numUserZones)
      self.dut.skipzn = [(0xff, 0xff)]
      oSkZnFile.Save_SKIPZN(self.dut.skipzn)
      self.dut.skipzn = oSkZnFile.Retrieve_SKIPZN(dumpData = 0)
      objMsg.printMsg("SkipZoneReadFromSim: %s" % self.dut.skipzn)
      self.params = params

      try:
         self.dut.dblData.Tables('P140_FLAW_COUNT').tableDataObj()
      except:
         CProcess().St(TP.prm_DBI_Fail_Limits_140)

      try:
         if testSwitch.SMR:
            spcID = TP.SqzWrite_SPC_ID
         else:
            spcID = TP.RdScrn2_SPC_ID
         Rawtable = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').chopDbLog('SPC_ID', 'match',str(spcID))
      except:
         # update test param and run T250
         t250prm = Utility.CUtility().copy(TP.prm_quickSER_250)
         if self.params.get('RST_RD_OFFSET', 0):
            t250prm.update({'CWORD2' : (t250prm['CWORD2'][0] | 0x0800, )})

         if self.params.get('SQZ_WRITE', 0):
            t250prm.update({'NUM_SQZ_WRITES' : 1 })

         if 'NUM_SQZ_WRITES' in t250prm and t250prm['NUM_SQZ_WRITES']>0: #squeeze write
            t250prm.update({'CWORD1' : (t250prm['CWORD1'] | 0x4000, )})
         if testSwitch.SMR:
            t250prm.update({'MAX_ERR_RATE' : self.params.get('MAX_ERR_RATE', -85)})
         t250prm.pop('MODES',['SYMBOL'])
         testZoneList = t250prm['TEST_ZONES']
         del t250prm['TEST_ZONES']
         t250prm.pop('SER_raw_BER_limit')
         t250prm.pop('SER_num_failing_zones_rtry')
         del t250prm['checkDeltaBER_num_failing_zones']
         del t250prm['max_diff']
         t250prm['MINIMUM'] = 0 # do not fail, need to collect data

         MaskList = Utility.CUtility().convertListToZoneBankMasks(testZoneList)
         for bank, list in MaskList.iteritems():
            if list:
               t250prm['ZONE_MASK_EXT'], t250prm['ZONE_MASK'] = Utility.CUtility().convertListTo64BitMask(list)
               if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
                  t250prm ['ZONE_MASK_BANK'] = bank
               SetFailSafe()
               CProcess().St(t250prm)
               ClearFailSafe()

         Rawtable = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').tableDataObj()

      tmptable = [TP.zone_table['table_name'], TP.zoned_servo_zn_tbl['table_name']]
      for table in tmptable:
         try:
            self.dut.dblData.Tables(table).deleteIndexRecords(1)
            self.dut.dblData.delTable(table, forceDeleteDblTable = 1)
         except: pass

      from FSO import CFSO
      CFSO().getZnTblInfo(spc_id = 1, supressOutput = 0)
      zstable = self.dut.dblData.Tables(TP.zone_table['table_name']).tableDataObj()

      ZnSector = [0,] * (self.dut.imaxHead * self.numUserZones)
      for rec in zstable:
         hd = int(rec['HD_LGC_PSN'])
         zn = int(rec['DATA_ZONE'])
         ZnSector[(hd * self.numUserZones) + zn] += int(rec['PBA_TRACK']) * int(rec['TRK_NUM'])
      objMsg.printMsg("ZnSector: %s" % ZnSector)

      if testSwitch.SMR:
         SkipZn_BER = (float)(TP.MIN_SOVA_SQZ_WRT)/10
      else: SkipZn_BER = (float)(TP.prm_quickSER_250['MINIMUM'])/10

      Verlist   = [0,] * (self.dut.imaxHead * self.numUserZones)
      Unverlist = [0,] * (self.dut.imaxHead * self.numUserZones)
      BERList   = [0,] * (self.dut.imaxHead * self.numUserZones)
      SkipList  = []
      for rec in self.dut.dblData.Tables('P140_FLAW_COUNT').tableDataObj():
         head     = int(rec['HD_LGC_PSN'])
         zone     = int(rec['DATA_ZONE'])
         verCnt   = int(rec['VERIFIED_FLAW_COUNT'])
         unverCnt = int(rec['UNVERIFIED_FLAW_COUNT'])
         Verlist[(head * self.numUserZones) + zone]   = (float)(verCnt*100)/(float)(ZnSector[(head * self.numUserZones) + zone])
         Unverlist[(head * self.numUserZones) + zone] = (float)(unverCnt*100)/(float)(ZnSector[(head * self.numUserZones) + zone])

      for rec in Rawtable:
         head     = int(rec['HD_LGC_PSN'])
         zone     = int(rec['DATA_ZONE'])
         BERList[(head * self.numUserZones) + zone]   = float(rec['RAW_ERROR_RATE'])
      objMsg.printMsg("VerList: %s" % Verlist)
      objMsg.printMsg("UnverList: %s" % Unverlist)
      objMsg.printMsg("BERList: %s" % BERList)
      objMsg.printMsg("Skip zone criteria: BER > %2.4f,  VerifyCnt > %s,  UnVerifyCnt > %s" % (SkipZn_BER, TP.SkipZn_Ver, TP.SkipZn_Un))

      self.mediaCacheZone = []
      self.umpZone        = []
      self.spareZone      = []
      if testSwitch.SMR:
         if testSwitch.FE_0385234_356688_P_MULTI_ID_UMP:
            self.mediaCacheZone = TP.MC_ZONE
         else:
            if testSwitch.ADAPTIVE_GUARD_BAND:
               self.mediaCacheZone = range(1,min(TP.UMP_ZONE[self.numUserZones]),1)
            else:
               self.mediaCacheZone = range(0,min(TP.UMP_ZONE[self.numUserZones]),1)
         self.umpZone = TP.UMP_ZONE[self.numUserZones][0:(len(TP.UMP_ZONE[self.numUserZones])-1)]
         self.spareZone = [TP.UMP_ZONE[self.numUserZones][-1]]
         objMsg.printMsg("mediaCacheZone: %s  umpZone: %s  spareZone: %s" % (self.mediaCacheZone, self.umpZone, self.spareZone))

      for head in range(self.dut.imaxHead):
         for zn in range(self.numUserZones):
            if zn not in (self.mediaCacheZone + self.umpZone + self.spareZone):
               if (BERList[(head * self.numUserZones) + zn] > SkipZn_BER) or (Verlist[(head * self.numUserZones) + zn] > TP.SkipZn_Ver) or (Unverlist[(head * self.numUserZones) + zn] > TP.SkipZn_Un):
                  BER   = BERList[(head * self.numUserZones) + zn]
                  Unver = Unverlist[(head * self.numUserZones) + zn]
                  Ver   = Verlist[(head * self.numUserZones) + zn]
                  SkipList.append((head, zn, BER, Ver, Unver))
            else:
               if (BERList[(head * self.numUserZones) + zn] > SkipZn_BER):
                  ScrCmds.raiseException(10632, "Failed BER in hd%d zn%d" % (head, zn))
      objMsg.printMsg("Skip zone: %s" % SkipList)

      if len(SkipList) == 0:
         objMsg.printMsg("No zone to skip!")
         return 0

      from operator import itemgetter
      Unbase   = sorted(SkipList, key=itemgetter(4),reverse=True)         # descending, lesser Unver cnt
      Verbase  = sorted(Unbase, key=itemgetter(3),reverse=True)           # descending, lesser Ver cnt
      SkipList = sorted(Verbase, key=itemgetter(2),reverse=True)          # descending, better BER
      self.dut.skipzn.extend(SkipList)
      objMsg.printMsg("Final Skip zone: %s" % self.dut.skipzn)

      # find number of skip zn in each head
      skipWholehd = 0
      numSkipZnperHd = [0,] * (self.dut.imaxHead)
      if testSwitch.SMR:
         NumZone = self.numUserZones - len(self.mediaCacheZone + self.umpZone + self.spareZone)
      else:
         NumZone = self.numUserZones
      for hd in range(self.dut.imaxHead):
         for i in range(len(SkipList)):
            if SkipList[i][0] == hd:
               numSkipZnperHd[hd] += 1

         if numSkipZnperHd[hd] == NumZone:
            skipWholehd += 1
            if testSwitch.SMR:
               for i in range(len(self.mediaCacheZone)):
                  SkipList.append((hd, self.mediaCacheZone[i]))
                  self.dut.skipzn.append((hd, self.mediaCacheZone[i]))
               for i in range(len(self.umpZone)):
                  SkipList.append((hd, self.umpZone[i]))
                  self.dut.skipzn.append((hd, self.umpZone[i]))
               for i in range(len(self.spareZone)):
                  SkipList.append((hd, self.spareZone[i]))
                  self.dut.skipzn.append((hd, self.spareZone[i]))
               numSkipZnperHd[hd] += len(self.mediaCacheZone + self.umpZone + self.spareZone)
               objMsg.printMsg("Number of skip zone in H%d = %d (Skip whole surface)" % (hd, numSkipZnperHd[hd]))
            else:
               objMsg.printMsg("Number of skip zone in H%d = %d (Skip whole surface)" % (hd, numSkipZnperHd[hd]))
         else:
            objMsg.printMsg("Number of skip zone in H%d = %d " % (hd, numSkipZnperHd[hd]))

      if (testSwitch.SMR) and (skipWholehd) and (not testSwitch.M10P):   # dezone do not support head depop for SMR
         ScrCmds.raiseException(11044,"Failed number of poor head: %d" % skipWholehd)
      if skipWholehd == self.dut.imaxHead:
         ScrCmds.raiseException(11044,"All %d heads skip whole surface" % skipWholehd)
      #
      # get capacity after zone skip
      sectorSize = int(self.dut.Drv_Sector_Size)
      objMsg.printMsg("Drv_Sector_Size = %d" % sectorSize)

      from VBAR import CNiblet
      if testSwitch.SPLIT_VBAR_FOR_CM_LA_REDUCTION:
         from WTF_Tools import CWTF_Tools
         oWaterfall = CWTF_Tools()
      else:
         from base_SerialTest import CWaterfallTest
         oWaterfall = CWaterfallTest(self.dut)
      
      if self.dut.Waterfall_Req[0] == 'D' or self.dut.depopMask: # handle for Depop_Done = 'NONE' as waterfall within dezone will not do depop
         original_depop = self.dut.Depop_Done
         objMsg.printMsg("Original Depop_Done = %s" % self.dut.Depop_Done)
         self.dut.Depop_Done = 'DONE'       # temp set
         oWaterfall.buildClusterList()
         self.dut.Depop_Done = original_depop  # revert
         objMsg.printMsg("Depop_Done = %s" % self.dut.Depop_Done)
      else:
         oWaterfall.buildClusterList()
      objMsg.printMsg("VbarPartNumCluster: %s" % TP.VbarPartNumCluster)
      objMsg.printMsg("TP.VbarNibletCluster: %s" % TP.VbarNibletCluster)
      objMsg.printMsg("VbarNibletCluster: %s" % oWaterfall.VbarNibletCluster)

      FinalSkipList = []
      for i in range(len(SkipList)):
         head = SkipList[i][0] & 0xff
         zone = SkipList[i][1] & 0xff
         FinalSkipList.append((head,zone))
      objMsg.printMsg("FinalSkipList: %s"%(FinalSkipList))

      CapAfterSkipZn = 0
      ZnCap = [0,] * (self.dut.imaxHead * self.numUserZones)
      if testSwitch.SPLIT_VBAR_FOR_CM_LA_REDUCTION:
         self.objNiblet = CNiblet(TP.VbarNibletCluster[0], self.params)
      else:
         self.objNiblet = CNiblet(TP.VbarNibletCluster[0])
      PBA_TO_LBA_SCALER = self.objNiblet.settings['PBA_TO_LBA_SCALER']
      objMsg.printMsg("PBA_TO_LBA_SCALER = %f" % PBA_TO_LBA_SCALER)
      for hd in range(self.dut.imaxHead):
         for zn in range(self.numUserZones):
            ZnCap[(hd * self.numUserZones) + zn] = PBA_TO_LBA_SCALER * sectorSize/float(1e9) * ZnSector[(hd * self.numUserZones) + zn]
            if (hd, zn) not in FinalSkipList: # only find non skip zone cap
               CapAfterSkipZn += ZnCap[(hd * self.numUserZones) + zn]
               objMsg.printMsg("H%d Zn%d Cap = %.3f" % (hd, zn, ZnCap[(hd * self.numUserZones) + zn]))
      objMsg.printMsg("Capacity (after Dezone) = %.3f" % CapAfterSkipZn)
      #
      # find niblet index which meet target cap
      Index = 0
      nibletIndex = 0xFF
      for niblet in TP.VbarNibletCluster:
         objMsg.printMsg("global vbar cluster: %s " %niblet)
         Target_cap = TP.VbarNibletCluster[Index].get('DRIVE_CAPACITY', TP.VbarNibletCluster[Index]['NUM_HEADS'] * TP.VbarCapacityGBPerHead * TP.VbarNibletCluster[Index]['CAPACITY_TARGET'])
         objMsg.printMsg("index: %d target_capacity: %d " %(Index, Target_cap))
         if CapAfterSkipZn > Target_cap:
            nibletIndex = Index
            objMsg.printMsg("Met target capacity, nibletIndex: %d" % (nibletIndex))
            break
         else:
            objMsg.printMsg("Cannot meet target Capacity, look for next.")
         Index = Index + 1
      #
      if nibletIndex == 0xFF: # didn't meet cap
         ScrCmds.raiseException(11044,"Failed Auto Dezone: Cannot meet target capacity %d" % Target_cap)

      oSkZnFile.Save_SKIPZN(self.dut.skipzn)
      self.dut.skipzn = oSkZnFile.Retrieve_SKIPZN(dumpData = 1)
      objMsg.printMsg("SkipZoneReadFromSim: %s" % self.dut.skipzn)

      OriginalPN = self.dut.partNum
      objMsg.printMsg("OldPartNum = %s" % self.dut.partNum)

      oWaterfall.keyCounter, oWaterfall.nibletString = oWaterfall.VbarNibletCluster[nibletIndex]
      objMsg.printMsg("nibletIndex: %s" % (nibletIndex))
      objMsg.printMsg("Selected keyCounter: %s  nibletString: %s" % (oWaterfall.keyCounter, oWaterfall.nibletString))

      # update pn and WTF attributes
      oWaterfall.updateWTF()
      partnum = oWaterfall.searchPN(self.dut.partNum)
      oWaterfall.updateATTR(partnum, oWaterfall.keyCounter) # if hv waterfall, pn and BG will be updated inside here
      #
      if OriginalPN != self.dut.partNum:
         from Setup import CSetup
         from FSO import CFSO
         if not testSwitch.FE_0190240_007955_USE_FILE_LIST_FUNCTIONS_FROM_DUT_OBJ:
            CSetup().buildFileList()  #update file list after update new partno
         else:
            self.dut.buildFileList()
         CFSO().setFamilyInfo(TP.familyInfo, TP.famUpdatePrm_178, self.dut.depopMask, forceHdCount = self.dut.imaxHead)
         objMsg.printMsg("Part number changed to %s" % str(self.dut.partNum))
         import TestParameters
         reload(TestParameters)
         import AFH_params
         reload(AFH_params)

         if testSwitch.SPLIT_VBAR_FOR_CM_LA_REDUCTION:
            from VBAR_LBA import CVBAR_LBA
            oVBAR_LBA = CVBAR_LBA()
         else:
            from VBAR import CVBAR
            oVBAR_LBA = CVBAR()
         CProcess().St({'test_num':210, 'CWORD1':8, 'SCALED_VAL': int(PBA_TO_LBA_SCALER * 10000)})
         Capacity = float(self.dut.dblData.Tables('P210_CAPACITY_DRIVE').tableDataObj()[-1]['DRV_CAPACITY'])
         objMsg.printMsg("Drive_capacity %.3fG" % (Capacity))
         if testSwitch.SPLIT_VBAR_FOR_CM_LA_REDUCTION:
            self.objNiblet = CNiblet(TP.VbarNibletCluster[nibletIndex], self.params)
         else:
            self.objNiblet = CNiblet(TP.VbarNibletCluster[nibletIndex])
         self.objNiblet.settings['DRIVE_CAPACITY'] = TP.VbarNibletCluster[nibletIndex].get('DRIVE_CAPACITY', TP.VbarNibletCluster[nibletIndex]['NUM_HEADS'] * TP.VbarCapacityGBPerHead * TP.VbarNibletCluster[nibletIndex]['CAPACITY_TARGET'])
         objMsg.printMsg("Set maxLBA for %dG" % (self.objNiblet.settings['DRIVE_CAPACITY']))
         oVBAR_LBA.setMaxLBA(self.objNiblet)
      else:
         objMsg.printMsg("PN no change")

      if not testSwitch.SMR:      # non-SMR media cache zone handle
         try:
            RAPMCzn = int(self.dut.dblData.Tables('P172_RAP_TABLE').tableDataObj()[0]['6'], 16)
         except:
            CProcess().St({'test_num':172, 'prm_name':'Display RAP', 'timeout':1800, 'CWORD1':0x9})
            # MCaddress = self.dut.dblData.Tables('P172_RAP_TABLE').tableDataObj()[0]['ADDRESS']
            RAPMCzn = int(self.dut.dblData.Tables('P172_RAP_TABLE').tableDataObj()[0]['6'], 16)
         objMsg.printMsg("MC at zone %d" % RAPMCzn)

         MCzn = RAPMCzn
         while (MCzn < self.numUserZones):
            NumMCZn = 0
            for i in range(len(SkipList)):
               if SkipList[i][1] == MCzn:
                  NumMCZn += 1

            if NumMCZn < self.dut.imaxHead:
               break
            else:
               objMsg.printMsg("All head have skip zone at zone %d" % MCzn)
               MCzn += 1

         if (MCzn != RAPMCzn and MCzn < self.numUserZones):        # save new MC zone to CAP
            CProcess().St({'test_num':178, 'prm_name':'prm_setRAPMediaCacheZone', 'timeout':1200, 'spc_id': 1,"RAP_WORD":(0x0003,MCzn,0x00FF), "CWORD1": 0x0220})
            objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
            objMsg.printMsg("MC move to zone %d" % MCzn)
            CProcess().St({'test_num':172, 'prm_name':'Display RAP', 'timeout':1800, 'CWORD1':0x9})
         else:
            objMsg.printMsg("MC remain at zone %d" % MCzn)
      else:
         objMsg.printMsg("No MC zone adjust for SMR drv")

   #======================================================================================================================================
   def skipZone(self):
      self.skipznDone = 0
      try:
         objMsg.printMsg("Skip Zone: %s" % self.dut.skipzn)
         if self.dut.skipzn == []:
            raise
      except:
         try:
            from RdWr import CSkipZnFile
            self.dut.skipzn = CSkipZnFile().Retrieve_SKIPZN(dumpData = 0)
            objMsg.printMsg("SPT_DIAG_RESULTS Skip Zone: %s" % self.dut.skipzn)
         except:
            ScrCmds.raiseException(11044,"Unable to extract SPT_DIAG_RESULTS")

      sptCmds.enableDiags()
      sptCmds.gotoLevel('T')

      if self.dut.skipzn == [(0xff, 0xff)]:
         objMsg.printMsg("No Zone to skip.")
         sptCmds.sendDiagCmd("i40,3,22",timeout = 300, printResult = True, DiagErrorsToIgnore = ['0000500D']) #removes entries which are generated during zone skip from GList.
         return 0
      elif (len(self.dut.skipzn) == 1 and self.dut.skipzn == [(0, 0)]) or self.dut.skipzn ==[]:
         ScrCmds.raiseException(11044,"Wrong SPT_DIAG_RESULTS extracted")

      pattern   = 'User Partition Format'
      PassPatt  = 'User Partition Format Successful'
      FailPatt  = 'User Partition Format Failed'
      RWErrPatt = 'R/W Error 843200B4'

      quickDFSformatresult = sptCmds.sendDiagCmd('m0,6,2,,,,,22',timeout = 1000, printResult = True)
      if quickDFSformatresult.find(PassPatt) >= 0:
         objMsg.printMsg("Pass quick format.")
      else:
         ScrCmds.raiseException(11044,"Failed User Format from cmd m0,6,2,,,,,22")

      sptCmds.sendDiagCmd("i40,3,22",timeout = 300, printResult = True, DiagErrorsToIgnore = ['0000500D']) #removes entries which are generated during zone skip from GList.

      objMsg.printMsg("SerialFormat Skip zone: %s" % self.dut.skipzn)
      self.flush()
      Hd_ZoneBit = [0,] * self.dut.imaxHead * 4    # store each ZoneBit info for each hd. hv 4 ZoneBit info per hd.
      for i in range(1, len(self.dut.skipzn)):
         if self.dut.skipzn[i][1] >= 0 and self.dut.skipzn[i][1] < 64:                   # ZoneBit63~0
            Hd_ZoneBit[self.dut.skipzn[i][0]*4] |= (1<<self.dut.skipzn[i][1])
         elif self.dut.skipzn[i][1] > 63 and self.dut.skipzn[i][1] < 128:                # ZoneBit127~64
            Hd_ZoneBit[self.dut.skipzn[i][0]*4+1] |= (1<<(self.dut.skipzn[i][1])-64)
         elif self.dut.skipzn[i][1] > 127 and self.dut.skipzn[i][1] < 192:               # ZoneBit191~128
            Hd_ZoneBit[self.dut.skipzn[i][0]*4+2] |= (1<<(self.dut.skipzn[i][1])-128)
         elif self.dut.skipzn[i][1] > 191 and self.dut.skipzn[i][1] < 256:               # ZoneBit255~192
            Hd_ZoneBit[self.dut.skipzn[i][0]*4+3] |= (1<<(self.dut.skipzn[i][1])-192)

      sptCmds.gotoLevel('T')
      j = 4     # to retrieve ZoneBit info. j=4 mean ZoneBit63~0
      subsequentcmdsend = 0
      # m0,206,2, head_num, ZoneBit63~0, ZoneBit127~64, ZoneBit191~128, 22, ZoneBit255~192
      cmd = ['m0','206','2',0,0,0,0,'22',0]
      for AllHdinfo in range(len(Hd_ZoneBit)):    # cmd send start from hd0
         if ((AllHdinfo+1)%4) == 0:
            cmd[8] = "%x" % Hd_ZoneBit[AllHdinfo]     # ZoneBit info
            cmd[3] = ((AllHdinfo + 1)/4) - 1   # head info
            cmd[3] = "%x" % cmd[3]
            j = 4
            if cmd[4] != '0' or cmd[5] != '0' or cmd[6] != '0' or cmd[8] != '0': # ZoneBit info
               if subsequentcmdsend == 1:
                  cmd[2] = '3'

               CMD = (','.join([i for i in cmd])).strip(',')

               if subsequentcmdsend == 0:
                  subsequentcmdsend = 1
               objMsg.printMsg("Sending Quick Format Skipzone Command: %s" %CMD,objMsg.CMessLvl.VERBOSEDEBUG)
               result = sptCmds.sendDiagCmd(CMD,timeout = 1000, printResult = True, DiagErrorsToIgnore = ['0000500D'])

               if result.find(PassPatt) >= 0:
                  objMsg.printMsg("Pass skip zone for hd %d" % (((AllHdinfo + 1)/4) - 1))
               #elif (result.find('DiagError 0000500D') >= 0 ) and (result.find(RWErrPatt) >= 0):
               elif (result.find(FailPatt) >= 0 ):
                  ScrCmds.raiseException(11044,"Failed User Format: not enough spare")
               else:
                  #objMsg.printMsg(result, objMsg.CMessLvl.DEBUG)
                  objMsg.printMsg(traceback.format_exc())
                  ScrCmds.raiseException(11044, "Unable to parse '%s' from buffer." % pattern)
         else:
            cmd[j]="%x" % Hd_ZoneBit[AllHdinfo]   # ZoneBit info
            j += 1

      objMsg.printMsg("END of skip zone.")
      self.skipznDone = 1
      return 1

   def getBER(self, zoneData, zones):
      '''
      Function getBER - updates BERInfo with RAW and OTF entries.
      Where:
         zones = number of zones per head to check.  ScPk Requirement 28/01/2009
      '''
      dictMinOTF={}
      dictMinRaw={}
      dictTemp={}
      head = 'HD_PHYS_PSN'

      for minData in TP.BERSpecs:
         tempList=[]
         for x in xrange(len(zoneData)):
            if int(zoneData[x]['DATA_ZONE'],16)<= (zones-1):
               if x%self.dut.numZones==0:                              # reset tempList every zone max
                  tempList=[]
               if zoneData[x][minData]!= '0.0':                         # append non-zero OTF values to tempList
                  tempList.append(float(zoneData[x][minData]))
               dictTemp[zoneData[x][head]]= tempList
            for k, v in dictTemp.iteritems():
               if len(v)>0:
                  if minData=='OTF':
                     dictMinOTF[k] = min(v)
                  elif minData=='RRAW':
                     dictMinRaw[k] = min(v)
               else:
                  if minData=='OTF':
                     dictMinOTF[k] = None
                  elif minData=='RRAW':
                     dictMinRaw[k] = None

      self.BERInfo['OTF'].update({'Min':dictMinOTF})
      self.BERInfo['RRAW'].update({'Min':dictMinRaw})


   def screenBER(self, berdata, berlist, raiseException=False):
      objMsg.printMsg("*** BER Screening for %s-header drive. ***" %self.dut.imaxHead)
      for ber in berdata:
         for minmax in berdata[ber]:
            if self.IsFailBER(minmax, ber, berdata[ber][minmax], berlist):
               if raiseException==True:
                  ScrCmds.raiseException(11254, "BER Screening Failure.")


   def IsFailBER(self, minmax, ber, data, berlist={}):
      #Display BER
      labels = {'Avg':"Average", 'Min':"Minimum", 'Max':"Maximum"}
      objMsg.printMsg("%s %s" %(labels[minmax], ber))
      for key in sorted(data.iterkeys()):
         objMsg.printMsg("head%s : OTF = %s" %(key, data[key]))
         #Screen BER
         if (not data[key] is None) and (minmax in berlist[ber]):
            if berlist[ber]=='Min' and ((float(data[key]) <= (TP.BERSpecs[ber][minmax]))):       # -> Min
               objMsg.printMsg("*** %s %s Failure detected at head%s. Measured=%s, Limit=%s." %(minmax, ber, key, data[key],TP.BERSpecs[ber][minmax]))
               return True
            elif berlist[ber]=='Max' and ((float(data[key]) >= TP.BERSpecs[ber][minmax])):     # -> Max
               objMsg.printMsg("*** %s %s Failure detected at head%s. Measured=%s, Limit=%s." %(minmax, ber, key, data[key],TP.BERSpecs[ber][minmax]))
               return True
      return False

   def SpareSectorStatistics(self):
      """
      Objective - to determine how many spare sectors have been used for drives, to collect statistics and
      to make decision on how many spare we should assign to each drive
      """
      objMsg.printMsg("Show SpareSectorStatistics:")
      sptCmds.gotoLevel('T')
      sptCmds.sendDiagCmd('V1,,,1', 600, printResult = True, raiseException = 0)

   #======================================================================================================================================
   #Additional Serial Format Debug information
   #Using m0,9 format option
   #As per ScPk request
   def SerialFormatInformation(self,result):
      try:
         DebugList = ['ZW','ZR','WX','RX','ER','SE','HE','User Partition','Total capacity']
         DebugInfoEntries, SoftErrorEntries ,HardErrorEntries = [],[],[]
         Softerrorzoneinfo, Harderrorzoneinfo = {},{}
         Softerrorcodeinfo, Harderrorcodeinfo = {},{}
         outputinfo=re.split('\n',result)
         for item in outputinfo:
            if len(item) >0:
               for inputinfo in DebugList:
                  if re.search(inputinfo,item.strip()):
                     if item.strip()[:2] <> inputinfo:
                        DebugInfoEntries.append(inputinfo + re.split(inputinfo,item.strip())[1])
                     else:
                        DebugInfoEntries.append(item.strip())
         for erroritem in DebugInfoEntries:
            if erroritem[:2] == 'ER':
               if  DebugInfoEntries[DebugInfoEntries.index(erroritem)+1][:2] == 'SE':
                  SoftErrorEntries.append(erroritem)
               if  DebugInfoEntries[DebugInfoEntries.index(erroritem)+1][:2] == 'HE':
                  HardErrorEntries.append(erroritem)
         objMsg.printMsg('***************************************************')
         objMsg.printMsg('        Serial Format Debug Information            ')
         objMsg.printMsg('***************************************************')
         objMsg.printMsg('Ev LBA/Soft XferLen  Zn Trk      Hd Sct  Wdg  PBA      ErrCode')
         for eachitem in DebugInfoEntries:
            objMsg.printMsg(eachitem)
         objMsg.printMsg('***************************************************')
         if len(SoftErrorEntries) <> 0:
            objMsg.printMsg('Soft Error Information:')
            for eachitem in SoftErrorEntries:
               objMsg.printMsg(eachitem)
               SoftZoneNo = re.split(' ',eachitem)[3]
               SoftHeadNo = re.split(' ',eachitem)[5]
               SoftErrorNo = re.split(' ',eachitem)[-1]
               SoftZoneHead = SoftZoneNo + ':' + SoftHeadNo
               SoftErrorCode = SoftErrorNo + ':' + SoftZoneNo + ':' + SoftHeadNo
               if Softerrorzoneinfo.has_key(SoftZoneHead) == 0:
                  Softerrorzoneinfo[SoftZoneHead] = 1
               else:
                  Softerrorzoneinfo[SoftZoneHead] = Softerrorzoneinfo[SoftZoneHead] + 1
               if Softerrorcodeinfo.has_key(SoftErrorCode) == 0:
                  Softerrorcodeinfo[SoftErrorCode] = 1
               else:
                  Softerrorcodeinfo[SoftErrorCode] = Softerrorcodeinfo[SoftErrorCode] + 1
            objMsg.printMsg('Zone  Head  ErrorCount')
            for eachzone in sorted(Softerrorzoneinfo.items()):
               objMsg.printMsg('%s    %s    %d' %(re.split(':',eachzone[0])[0],re.split(':',eachzone[0])[1],Softerrorzoneinfo[eachzone[0]]))
            objMsg.printMsg('ErrorCode  Zone  Head  ErrorCount')
            for eachzone in sorted(Softerrorcodeinfo.items()):
               objMsg.printMsg('%s   %s    %s    %d' %(re.split(':',eachzone[0])[0],re.split(':',eachzone[0])[1],re.split(':',eachzone[0])[2],Softerrorcodeinfo[eachzone[0]]))
            objMsg.printMsg('***************************************************')
         if len(HardErrorEntries) <> 0:
            objMsg.printMsg('Hard Error Information:')
            for eachitem in HardErrorEntries:
               objMsg.printMsg(eachitem)
               HardZoneNo = re.split(' ',eachitem)[3]
               HardHeadNo = re.split(' ',eachitem)[5]
               HardErrorNo = re.split(' ',eachitem)[-1]
               HardZoneHead = HardZoneNo + ':' + HardHeadNo
               HardErrorCode = HardErrorNo + ':' + HardZoneNo + ':' + HardHeadNo
               if Harderrorzoneinfo.has_key(HardZoneHead) == 0:
                  Harderrorzoneinfo[HardZoneHead] = 1
               else:
                  Harderrorzoneinfo[HardZoneHead] = Harderrorzoneinfo[HardZoneHead] + 1
               if Harderrorcodeinfo.has_key(HardErrorCode) == 0:
                  Harderrorcodeinfo[HardErrorCode] = 1
               else:
                  Harderrorcodeinfo[HardErrorCode] = Harderrorcodeinfo[HardErrorCode] + 1
            objMsg.printMsg('Zone  Head  ErrorCount')
            for eachzone in sorted(Harderrorzoneinfo.items()):
               objMsg.printMsg('%s    %s    %d' %(re.split(':',eachzone[0])[0],re.split(':',eachzone[0])[1],Harderrorzoneinfo[eachzone[0]]))
            objMsg.printMsg('ErrorCode  Zone  Head  ErrorCount')
            for eachzone in sorted(Harderrorcodeinfo.items()):
               objMsg.printMsg('%s   %s    %s    %d' %(re.split(':',eachzone[0])[0],re.split(':',eachzone[0])[1],re.split(':',eachzone[0])[2],Harderrorcodeinfo[eachzone[0]]))
            objMsg.printMsg('***************************************************')
      except:
         objMsg.printMsg('Retreving Serial Format Debug Information Failed!')
         objMsg.printMsg("Error: %s" % traceback.format_exc())
         pass

   #======================================================================================================================================
   def rw_LBAs(self, startLBA, endLBA, mode = 'R', timeout = 3600, printResult = False, stopOnError = True, loopSleepTime = 5, DiagErrorsToIgnore = [],):

      if mode == 'R':
         objMsg.printMsg("Performing sequential reads on LBAs: %X - %X." %(startLBA, endLBA))
      elif mode == 'W':
         objMsg.printMsg("Performing sequential writes on LBAs: %X - %X." %(startLBA, endLBA))
      else:
         ScrCmds.raiseException(11044, "Invalid mode requested")

      DiagTTR_Except = getattr(PIF, 'DiagTTR_Except', [])

      if testSwitch.WA_0119554_231166_DIAG_MAX_LBA_LEN_LIMITED:

         from ContinuousSet import cSet
         if testSwitch.BF_0142220_395340_P_FIX_LONG_TIME_RW_ON_DIAG_COMMAND:
            spans = cSet(startLBA, endLBA).split(0x5F5E100) # 100M To reduce testtime per loop
         else:
            spans = cSet(startLBA, endLBA).split(0xFF00)
         for span in spans:
            if not testSwitch.FE_0151068_409401_P_KORAT_TTR_DIAG_CMD or self.dut.partNum in DiagTTR_Except or \
               (testSwitch.FE_0159305_409401_P_KORAT_TTR_DIAG_CMD_BY_OPTI_READ_ONLY and mode == 'W'):
               self.setLBASpace(span.start, span.end)
            if mode == 'R':
               val = 'reads'
            elif mode == 'W':
               val = 'writes'

            if DEBUG:
               objMsg.printMsg("\tPerforming sequential %s on sub-LBAs: %X - %X." %(val, span.start, span.end))

            if not testSwitch.FE_0151068_409401_P_KORAT_TTR_DIAG_CMD or self.dut.partNum in DiagTTR_Except or \
               (testSwitch.FE_0159305_409401_P_KORAT_TTR_DIAG_CMD_BY_OPTI_READ_ONLY and mode == 'W'):
               stat = self.__baseLBAOps(mode, timeout = timeout, printResult = printResult, stopOnError = stopOnError, DiagErrorsToIgnore = DiagErrorsToIgnore, loopSleepTime = 0.01)
            else:
               stat = self.__baseLBAOps_Extend(mode, startLBA, endLBA, timeout = timeout, printResult = printResult, stopOnError = stopOnError, DiagErrorsToIgnore = DiagErrorsToIgnore, loopSleepTime = 0.01)
         return stat
      else:
         if not testSwitch.FE_0151068_409401_P_KORAT_TTR_DIAG_CMD or self.dut.partNum in DiagTTR_Except or \
            (testSwitch.FE_0159305_409401_P_KORAT_TTR_DIAG_CMD_BY_OPTI_READ_ONLY and mode == 'W'):
            self.setLBASpace(startLBA, endLBA)
         if not testSwitch.BF_0121631_399481_NO_SEEKLBA_IN_RWLBAS:
            self.seekLBA(startLBA, mode, printResult, timeout, loopSleepTime, stopOnError)
         if not testSwitch.FE_0151068_409401_P_KORAT_TTR_DIAG_CMD or self.dut.partNum in DiagTTR_Except or \
            (testSwitch.FE_0159305_409401_P_KORAT_TTR_DIAG_CMD_BY_OPTI_READ_ONLY and mode == 'W'):
            return self.__baseLBAOps(mode, timeout = timeout, printResult = printResult, stopOnError = stopOnError, DiagErrorsToIgnore = DiagErrorsToIgnore, loopSleepTime = loopSleepTime)
         else:
            return self.__baseLBAOps_Extend(mode, startLBA, endLBA, timeout = timeout, printResult = printResult, stopOnError = stopOnError, DiagErrorsToIgnore = DiagErrorsToIgnore, loopSleepTime = loopSleepTime)

   def seekLBA(self, lba, mode = 'R', printResult = True, timeout = 300, loopSleepTime = 0.1, stopOnError = True):
      """
      Seek to LBA. mode is 'R', 'W', 'F'

      Diag cmd seekType enums are 0=read position, 1 = write position, 2 = write header position
      """
      seekType = {'R':0, 'W': 1, 'F': 2}[mode.upper()]

      self.gotoLevel('A')
      sptCmds.sendDiagCmd('S%x,,,,%x' % (lba, seekType), timeout = timeout, printResult = printResult, stopOnError = stopOnError, loopSleepTime = loopSleepTime)

   def randLBAs(self, startLBA, endLBA, mode = 'R', duration = 10, sectorCount = 256):
      if mode == 'R':
         objMsg.printMsg("Performing %d minutes of random reads on LBAs: %s to %s.." %(duration, startLBA, endLBA))
      elif mode == 'W':
         objMsg.printMsg("Performing %d minutes of random writes on LBAs: %s to %s.." %(duration, startLBA, endLBA))
      else:
         ScrCmds.raiseException(11044, "Invalid mode requested")

      sptCmds.gotoLevel('A')
      self.setLBASpace(startLBA, endLBA)                       # Set requested test space
      sptCmds.sendDiagCmd('A107')                              # Set test space random operations
      sptCmds.sendDiagCmd('L11')                               # Loop: do not disaply errors, continue on error
      self.PBlock('%s,%x' % (mode, sectorCount))               # Send command (Write or Read with input sector count)
      time.sleep(duration*60)                                  # Sleep for secified time
      for retry in range(10):
         try:
            sptCmds.sendDiagCmd(CR,timeout = 30, altPattern='>')  # Ctrl-Z to break out of diag loop
            break
         except:
            pass
      else:
         ScrCmds.raiseException(10566, "Timeout when trying to abort random operations.")

   def randSeeks(self, mode = 'R', duration = 10):
      if mode == 'R':
         SkType = 0
         objMsg.printMsg("Performing %f minutes of random read seeks." %(duration,))
      elif mode == 'W':
         SkType = 1
         objMsg.printMsg("Performing %f minutes of random write seeks" %(duration,))
      else:
         ScrCmds.raiseException(11044, "Invalid mode requested")

      sptCmds.gotoLevel('3')
      start = time.time()
      done = False
      objMsg.printMsg("Running test of random seek command to verify diag actually works.")
      sptCmds.sendDiagCmd('D0,%d,500' % SkType, timeout = 30, printResult = True)
      sptCmds.sendDiagCmd('L11')    # Loop: do not disaply errors, continue on error
      self.PBlock('D0,%d,500' % SkType)
      time.sleep(duration*60 - (time.time() - start)) # Let seeks run for specified amount of time
      for retry in range(10):
         try:
            sptCmds.sendDiagCmd(CR,timeout = 30, altPattern='>')  # Carriage return to break out of diag loop
            break
         except:
            pass
      else:
         ScrCmds.raiseException(10566, "Timeout when trying to abort random operations.")

   def setCylinderRangeAllHeads(self, startTrack, endTrack):
      """
      Set test space to a given cyclinder range on all heads.
      """
      sptCmds.sendDiagCmd('AD', loopSleepTime = 0)                               # Reset test space to default (full pack)
      for head in xrange(self.dut.imaxHead):
         sptCmds.sendDiagCmd('A8,%X,,%X'%(startTrack, head,), loopSleepTime = 0) # set min cyl
         sptCmds.sendDiagCmd('A9,%X,,%X'%(endTrack, head,), loopSleepTime = 0)   # set max cyl

   def setCylinderRangeSingleHead(self, startTrack, endTrack, head, printResult = False):
      """
      Set test space to a given cylinder range on a head.
      """
      sptCmds.sendDiagCmd('AD', printResult = False, loopSleepTime = 0)                                     # Restore default Test Space
      sptCmds.sendDiagCmd('AE,%X' % (head,), printResult = printResult, loopSleepTime = 0)                  # Set min head
      sptCmds.sendDiagCmd('AA,%X' % (head,), printResult = printResult, loopSleepTime = 0)                  # Set max head
      sptCmds.sendDiagCmd('A8,%X,,%X' % (startTrack, head,), printResult = printResult, loopSleepTime = 0)  # Set min cyl
      sptCmds.sendDiagCmd('A9,%X,,%X' % (endTrack, head,), printResult = printResult, loopSleepTime = 0)    # Set max cyl

   def setLBASpace(self, startLBA, endLBA):
      self.setStateSpace('AD')                                # Restore default Test Space
      self.setStateSpace('AB,%X' %startLBA)                   # Test Space - Set Min User LBA
      self.setStateSpace('AC,%X' %endLBA)                     # Test Space - Set Max User LBA
      return

   #======================================================================================================================================
   def writeTrackRange(self, startCyl, endCyl, head, timeout = 3600, printResult = False, DiagErrorsToIgnore = None, loopSleepTime = 0.1):
      self.setCylinderRangeSingleHead(startCyl, endCyl, head, printResult = printResult)

      seekTrack = self.getTrackInfo(startCyl, head, printResult = printResult, mode = 'physical')['PHY_CYL']   # Seek to Phys track in case outside of LBA space
      if testSwitch.BF_0219840_357260_P_USE_DEFECT_LOG_TO_MANAGE_TRACK_CLEANUP_ERRORS:
         self.initDefectLog(printResult = printResult)
         self.setErrorLogging(enable = True, printResult = printResult)

         self.gotoLevel('2')
         sptCmds.sendDiagCmd('s%X,%X,22' %(seekTrack, head ), printResult = printResult, loopSleepTime = 0.05)    # Seek to start of of test space
         sptCmds.sendDiagCmd('L51', printResult = printResult, loopSleepTime = 0)                              # Ignore errors, disable display, stop on wrap test space
         sptCmds.sendDiagCmd('W', timeout = timeout, printResult = printResult, stopOnError = False, DiagErrorsToIgnore = DiagErrorsToIgnore, loopSleepTime = loopSleepTime)

         loggedErrors = self.filterListofDicts(self.getActiveErrorLog(printResult = False), 'DIAGERR', DiagErrorsToIgnore, include = False)
         if len(loggedErrors) > 0:
            objMsg.printMsg("\nwriteTrackRange - FAILED: Writing Tracks %s to %s, Head %s" % (startCyl, endCyl, head))
            objMsg.printMsg("Diag Errors Logged: %s\n" % loggedErrors)
            ScrCmds.raiseException(11044, 'Script Exception - Failed Track Cleanup Writes')

      else:
         self.gotoLevel('2')
         sptCmds.sendDiagCmd('s%X,%X,22' %(seekTrack, head ), printResult = printResult, loopSleepTime = 0.05)    # Seek to start of of test space
         sptCmds.sendDiagCmd('L41', printResult = printResult, loopSleepTime = 0)                                 # Ignore errors, stop on wrap test space
         sptCmds.sendDiagCmd('W', timeout = timeout, printResult = printResult, DiagErrorsToIgnore = DiagErrorsToIgnore, loopSleepTime = loopSleepTime)

   #======================================================================================================================================
   def rw_CHSTrackRange(self, mode, startCyl, endCyl, head, timeout = 3600, printResult = False, DiagErrorsToIgnore = None, loopSleepTime = 0.1):
      self.setCylinderRangeSingleHead(startCyl, endCyl, head, printResult = printResult)

      seekTrack = self.getTrackInfo(startCyl, head, printResult = printResult, mode = 'physical')['PHY_CYL']   # Seek to Phys track in case outside of LBA space
      self.gotoLevel('2')
      sptCmds.sendDiagCmd('s%X,%X,22' %(seekTrack, head ), printResult = printResult, loopSleepTime = 0.05)    # Seek to start of of test space
      sptCmds.sendDiagCmd('L41', printResult = printResult, loopSleepTime = 0)                                 # Ignore errors, stop on wrap test space
      if mode == 'W':
         sptCmds.sendDiagCmd('W', timeout = timeout, printResult = printResult, DiagErrorsToIgnore = DiagErrorsToIgnore, loopSleepTime = loopSleepTime)
      elif mode == 'R':
         sptCmds.sendDiagCmd('R', timeout = timeout, printResult = printResult, DiagErrorsToIgnore = DiagErrorsToIgnore, loopSleepTime = loopSleepTime)
      else:
         ScrCmds.raiseException(11044, "Invalid mode requested")

   #======================================================================================================================================
   def writeBandRange(self, startBand, bandCount, timeout = None, printResult = False, DiagErrorsToIgnore = None, loopSleepTime = 0.1):
      if not timeout:
         timeout = int(300 + bandCount*0.5)

      if testSwitch.BF_0219840_357260_P_USE_DEFECT_LOG_TO_MANAGE_TRACK_CLEANUP_ERRORS:
         self.initDefectLog(printResult = printResult)
         self.setErrorLogging(enable = True, printResult = printResult)
         sptCmds.sendDiagCmd('AD', loopSleepTime = 0) # Restore default Test Space

         self.gotoLevel('2')     # TODO: Remove level 2 read command once F3 writeband diag cmd (A>'g') is working. This is a workaround.
         sptCmds.sendDiagCmd('R', timeout = timeout, printResult = printResult, DiagErrorsToIgnore = DiagErrorsToIgnore, loopSleepTime = loopSleepTime)

         self.gotoLevel('A')
         sptCmds.sendDiagCmd('g%X,,%X' %( startBand, bandCount ), timeout = timeout, printResult = printResult, stopOnError = False, DiagErrorsToIgnore = DiagErrorsToIgnore, loopSleepTime = loopSleepTime) # Write specified bands
         objMsg.printMsg("Read Verify on same band")
         sptCmds.sendDiagCmd('h%X,,%X' %( startBand, bandCount ), timeout = timeout, printResult = printResult, DiagErrorsToIgnore = DiagErrorsToIgnore, loopSleepTime = loopSleepTime) # Read specified bands
         loggedErrors = self.filterListofDicts(self.getActiveErrorLog(printResult = False), 'DIAGERR', DiagErrorsToIgnore, include = False)

         if len(loggedErrors) > 0:
            objMsg.printMsg("\nwriteTrackRange - FAILED: Writing Tracks %s to %s, Head %s" % (startCyl, endCyl, head))
            objMsg.printMsg("Diag Errors Logged: %s\n" % loggedErrors)
            ScrCmds.raiseException(11044, 'Script Exception - Failed Track Cleanup - Band Writes')

      else:
         sptCmds.sendDiagCmd('AD', loopSleepTime = 0)                                                          # Restore default Test Space

         self.gotoLevel('2')     # TODO: Remove level 2 read command once F3 writeband diag cmd (A>'g') is working. This is a workaround.
         sptCmds.sendDiagCmd('R', timeout = timeout, printResult = printResult, DiagErrorsToIgnore = DiagErrorsToIgnore, loopSleepTime = loopSleepTime)

         self.gotoLevel('A')
         sptCmds.sendDiagCmd('g%X,,%X' %( startBand, bandCount ), timeout = timeout, printResult = printResult, DiagErrorsToIgnore = DiagErrorsToIgnore, loopSleepTime = loopSleepTime) # Write specified bands
         sptCmds.sendDiagCmd('h%X,,%X' %( startBand, bandCount ), timeout = timeout, printResult = printResult, DiagErrorsToIgnore = DiagErrorsToIgnore, loopSleepTime = loopSleepTime) # Read specified bands

   #======================================================================================================================================
   def rw_BandRange(self, mode, startBand, bandCount, timeout = None, printResult = False, DiagErrorsToIgnore = None, loopSleepTime = 0.1):
      if not timeout:
         timeout = int(300 + bandCount*0.5)

      if testSwitch.BF_0219840_357260_P_USE_DEFECT_LOG_TO_MANAGE_TRACK_CLEANUP_ERRORS:
         self.initDefectLog(printResult = printResult)
         self.setErrorLogging(enable = True, printResult = printResult)
         sptCmds.sendDiagCmd('AD', loopSleepTime = 0) # Restore default Test Space

         self.gotoLevel('2')     # TODO: Remove level 2 read command once F3 writeband diag cmd (A>'g') is working. This is a workaround.
         sptCmds.sendDiagCmd('R', timeout = timeout, printResult = printResult, DiagErrorsToIgnore = DiagErrorsToIgnore, loopSleepTime = loopSleepTime)

         self.gotoLevel('A')
         if mode == 'W':
            sptCmds.sendDiagCmd('g%X,,%X' %( startBand, bandCount ), timeout = timeout, printResult = printResult, stopOnError = False, DiagErrorsToIgnore = DiagErrorsToIgnore, loopSleepTime = loopSleepTime) # Write specified bands
            loggedErrors = self.filterListofDicts(self.getActiveErrorLog(printResult = False), 'DIAGERR', DiagErrorsToIgnore, include = False)
         elif mode == 'R':
            #objMsg.printMsg("Read Verify on same band")
            sptCmds.sendDiagCmd('h%X,,%X' %( startBand, bandCount ), timeout = timeout, printResult = printResult, DiagErrorsToIgnore = DiagErrorsToIgnore, loopSleepTime = loopSleepTime) # Read specified bands
            loggedErrors = self.filterListofDicts(self.getActiveErrorLog(printResult = False), 'DIAGERR', DiagErrorsToIgnore, include = False)
         else:
            ScrCmds.raiseException(11044, "Invalid mode requested")

         if len(loggedErrors) > 0:
            if mode == 'W':
               objMsg.printMsg("\nWrite TrackRange - FAILED: Writing Tracks %s to %s, Head %s" % (startCyl, endCyl, head))
            else:
               objMsg.printMsg("\nRead TrackRange - FAILED: Reading Tracks %s to %s, Head %s" % (startCyl, endCyl, head))
            objMsg.printMsg("Diag Errors Logged: %s\n" % loggedErrors)
            ScrCmds.raiseException(11044, 'Script Exception - Failed Track Cleanup - Band Writes')

      else:
         sptCmds.sendDiagCmd('AD', loopSleepTime = 0)                                                          # Restore default Test Space

         self.gotoLevel('2')     # TODO: Remove level 2 read command once F3 writeband diag cmd (A>'g') is working. This is a workaround.
         sptCmds.sendDiagCmd('R', timeout = timeout, printResult = printResult, DiagErrorsToIgnore = DiagErrorsToIgnore, loopSleepTime = loopSleepTime)

         self.gotoLevel('A')
         if mode == 'W':
            sptCmds.sendDiagCmd('g%X,,%X' %( startBand, bandCount ), timeout = timeout, printResult = printResult, DiagErrorsToIgnore = DiagErrorsToIgnore, loopSleepTime = loopSleepTime) # Write specified bands
         elif mode == 'R':
            sptCmds.sendDiagCmd('h%X,,%X' %( startBand, bandCount ), timeout = timeout, printResult = printResult, DiagErrorsToIgnore = DiagErrorsToIgnore, loopSleepTime = loopSleepTime) # Read specified bands
         else:
            ScrCmds.raiseException(11044, "Invalid mode requested")

   #======================================================================================================================================
   def __baseLBAOps(self, mode, timeout = 60, printResult = False, stopOnError = True, DiagErrorsToIgnore = [], loopSleepTime = 5):
      """Perform a base API Lba command
      mode: 'W' == write and 'R' == read"""

      sptCmds.gotoLevel('A')
      if stopOnError:
         return sptCmds.sendDiagCmd('%s,,,10' % mode, timeout = timeout, printResult = printResult, stopOnError = True, DiagErrorsToIgnore = DiagErrorsToIgnore, loopSleepTime = loopSleepTime)
      else:
         return sptCmds.sendDiagCmd('%s,,,11' % mode, timeout = timeout, printResult = printResult, stopOnError = True, DiagErrorsToIgnore = DiagErrorsToIgnore, loopSleepTime = loopSleepTime)

   def writeLBA(self, LBA, printResult = False):
      sptCmds.gotoLevel('A')
      sptCmds.sendDiagCmd('W%X'%(LBA,), printResult = printResult)

   def __baseLBAOps_Extend(self, mode, startLBA, endLBA, timeout = 60, printResult = False, stopOnError = True, DiagErrorsToIgnore = [], loopSleepTime = 5):
      """Perform a base API Lba command
      mode: 'W' == write and 'R' == read"""

      sptCmds.gotoLevel('A')

      xferLength = endLBA - startLBA

      if stopOnError:
         return sptCmds.sendDiagCmd('%s%x,%x,,00' % (mode,startLBA,xferLength), timeout = timeout, printResult = printResult, stopOnError = True, DiagErrorsToIgnore = DiagErrorsToIgnore, loopSleepTime = loopSleepTime)
      else:
         return sptCmds.sendDiagCmd('%s%x,%x,,01' % (mode,startLBA,xferLength), timeout = timeout, printResult = printResult, stopOnError = True, DiagErrorsToIgnore = DiagErrorsToIgnore, loopSleepTime = loopSleepTime)

   def readSector(self, startSector,numSectors,dynamicSparing,contOnError):
      sptCmds.gotoLevel('2')
      self.flush()
      accumulator = self.PBlock('R%x,%x,%s,,%s' % (startSector,numSectors,str(dynamicSparing),str(contOnError)))
      errors = sptCmds.promptRead(2000, accumulator = accumulator)
      if DEBUG == 1:
         objMsg.printMsg(str(errors),objMsg.CMessLvl.DEBUG)
      errPat = 'Error (?P<ErrorCode>\d{4}).*PLP CHS (?P<track>[\d,A-F]{6}).(?P<head>\d).(?P<sector>[\d,A-F]{4})'
      errComp = re.compile(errPat,re.S)
      errs = errors.split("Remaining")
      matches = []
      for lines in errs:
         matches.append(errComp.findall(lines))
      self.flush()
      ser = (numSectors-(len(matches)-1))/numSectors
      self.printErrors(matches)
      return (matches,ser)


   def seekTrack(self, track, head, printResult = False):
      sptCmds.gotoLevel('2')

      results = sptCmds.sendDiagCmd('S%x,%x' % (track,head), printResult = printResult, DiagErrorsToIgnore = ['00003000','00003003'])

      if DEBUG == 1:
         objMsg.printMsg(str(results),objMsg.CMessLvl.DEBUG)

      success = not self.checkIfInvalidTargetAddress(results)
      #Return success boolean
      return success, results

   def checkIfInvalidTargetAddress(self, results):
      if results.find("DiagError 00003000") > -1:
         return True
      else:
         return False

   def mergeG_to_P(self, timeout = 10800):
      """
      Merge the active Grown defect list back into the P list. Usually requires a re-format (write only) of the drive
        to re-map the LBA ECC seeds.
      Also if F3 pad and fill are enabled this command will apply the pad and fill to the existing G lists.
      """
      objMsg.printMsg("Merging G list to P list.", objMsg.CMessLvl.VERBOSEDEBUG)

      sptCmds.gotoLevel('A')

      if testSwitch.FE_0129689_220554_SUPPORT_P_DIAG_PARAMETERS:
         results = sptCmds.sendDiagCmd("P%X,%X,%X" % (TP.prm_mergeG_to_P['RADIAL_PAD_CYLS'], \
                                                      TP.prm_mergeG_to_P['S_WEDGE_DEFECT_PAD'], \
                                                      TP.prm_mergeG_to_P['M_WEDGE_DEFECT_PAD']), \
                                                      timeout = timeout, printResult = True)
      else:
         results = sptCmds.sendDiagCmd('P', timeout = timeout, printResult = True)
      if testSwitch.virtualRun:
         results = "DiagError 0000500E"
      match = re.search('DiagError\s*(?P<diagError>[0-9a-fA-F]+)', results)
      if match:
         error = int(match.groupdict()['diagError'],16)
         if error > 0:
            msg = "Merge G to P failed due to diagError %X" % error
            if testSwitch.virtualRun:
               objMsg.printMsg("VE failure disabled... %s" % msg)
            else:
               ScrCmds.raiseException(10219, msg)

   def addActiveErrorsToClientList(self):
      objMsg.printMsg('Adding Active Errors To Client List')
      objMsg.printMsg('Exec D10 defect processing')
      sptCmds.gotoLevel('L')
      sptCmds.sendDiagCmd('E0', printResult = True)
      loggedErrors = self.getActiveErrorLog()

      if len(loggedErrors) > 0:
         for retry in xrange(3):
            try:
               sptCmds.gotoLevel('T')
               # Add D10 to P List
               results = sptCmds.sendDiagCmd('m0,6,7,,,,,22', timeout = 12000, printResult = True, loopSleepTime = 5)
               pat = 'Process Defect List Error'
               if results.find(pat) > -1:
                  ScrCmds.raiseException(10013, "Error processing defect lists.")
               else:
                  break
            except CRaiseException:
               pass
         else:
            ScrCmds.raiseException(10013, "Error processing defect lists.")

      return loggedErrors

   def listToMask(self,inputList):
      outVal = 0
      for x in xrange(len(inputList)):
         outVal = outVal | (2*int(inputList[x]>0))**x
      return outVal

   def diagLoopCmd(self,loopCount,continueOnError = 0, stopOnNoError = 0, spinDownOnError = 0):
      """
      Sets the Loop Count of the next command
      """
      self.flush()
      opts = [continueOnError, stopOnNoError, spinDownOnError]
      cmd = 'L%x,%x' % (self.listToMask(opts),loopCount)

      if DEBUG > 0:
         objMsg.printMsg("Sending Command %s" % cmd)

      accumulator = self.PBlock(cmd)
      sptCmds.promptRead(5,accumulator = accumulator )

   def getCriticalEventAttributes(self, timeout, failOnThresholdViolation = True, ignoreAttrList = []):
      CriticalEventLogData = sptCmds.sendDiagCmd('N5',timeout=timeout, printResult = True)
      CriticalEventAtributeThresholds = sptCmds.sendDiagCmd('N6', timeout=timeout, printResult = True)

      CELogAttrs = self.parseCEAttributes(CriticalEventLogData)
      CEThresholds = self.parseCEThresholds(CriticalEventAtributeThresholds)
      objMsg.printMsg("Evaluating Smart Attribute Thresholds: Descriptions at http://firmware.seagate.com/smart/ATADocumentation/SMART%20Internal%20Specification.rtf")
      for attrNum,threshold in CEThresholds.items():
         normVal = CELogAttrs.get(attrNum,{'normalized':0})['normalized']
         #if flags bit 0 is set this is a failing attr
         flags = CELogAttrs.get(attrNum,{'flags':0})['flags']
         if normVal > threshold and attrNum not in ignoreAttrList and (flags & 1):
            failMsg = 'Failed Smart Threshold Value attribute %s: %d/%d' % (attrNum, normVal, threshold)
            if failOnThresholdViolation:
               ScrCmds.raiseException(13455, failMsg)
            else:
               objMsg.printMsg(failMsg)

      return CriticalEventLogData

   #======================================================================================================================================
   def parseCEAttributes(self, CEData):
      compPat = re.compile("(?P<attrNum>[\da-fA-F]+)\s*(?P<flags>[\da-fA-F]+)\s*(?P<normalized>[\da-fA-F]+)\s*(?P<worst>[\da-fA-F]+)\s*(?P<raw>[\da-fA-F]+)")
      ceAttrs = []
      for line in CEData.splitlines():
         match = compPat.search(line)
         if match:
            ceAttrs.append(match.groupdict())

      CeAttributeData = {}

      for row in ceAttrs:
         attrNum = row.pop('attrNum')
         CeAttributeData[attrNum] = self.convDictItems(row,int,[16,])
         if testSwitch.FE_0174192_395340_P_USE_C5_C6_TO_CHECK_P_LIST_ON_CUT2 and self.dut.nextOper in ['CUT2']:
            if attrNum == 'C5' and self.dut.nextState in ['RESET_SMART'] and DriveAttributes.get('C5_SCRN',"NONE")=="NONE":
               objMsg.printMsg('Start Screening C5')
               if DEBUG:
                  objMsg.printMsg(CeAttributeData[attrNum])  #Debug by supitcha s.
                  objMsg.printMsg(CeAttributeData[attrNum]['raw'])
               self.dut.driveattr['C5_SCRN'] = 'DONE'
               DriveAttributes['C5_SCRN'] = 'DONE'
               if CeAttributeData[attrNum]['raw'] == 0:
                  objMsg.printMsg('PASS :: Screening for C5')
               else:
                  failMsgC5 = 'Failed Check Pending Spare Count for C5 !!!'
                  ScrCmds.raiseException(13488, failMsgC5)
            elif attrNum == 'C6' and self.dut.nextState in ['RESET_SMART'] and DriveAttributes.get('C6_SCRN',"NONE")=="NONE":
               objMsg.printMsg('Start Screening C6')
               if DEBUG:
                  objMsg.printMsg(CeAttributeData[attrNum])  #Debug by supitcha s.
                  objMsg.printMsg(CeAttributeData[attrNum]['raw'])
               self.dut.driveattr['C6_SCRN'] = 'DONE'
               DriveAttributes['C6_SCRN'] = 'DONE'
               if CeAttributeData[attrNum]['raw'] == 0:
                  objMsg.printMsg('PASS :: Screening for C6')
               else:
                  failMsgC5 = 'Failed Check Pending Spare Count for C6 !!!'
                  ScrCmds.raiseException(13488, failMsgC5)
            else:
               objMsg.printMsg('*** CONTINUE ***')
               if DEBUG:
                  objMsg.printMsg(CeAttributeData[attrNum])  #Debug by supitcha s.
                  objMsg.printMsg(CeAttributeData[attrNum]['raw'])

      return CeAttributeData

   def parseCEThresholds(self,CEData):
      compPat = re.compile("(?P<attrNum>[\da-fA-F]+)\s*(?P<Thresh>[\da-fA-F]+)")
      ceAttrs = []
      for line in CEData.splitlines():
         match = compPat.search(line)
         if match:
            ceAttrs.append(match.groupdict())

      CeThreshData = {}

      for row in ceAttrs:
         attrNum = row.pop('attrNum')
         CeThreshData[attrNum] = int(row['Thresh'],16)

      return CeThreshData

   def getCriticalEventLog(self, timeout = 30, printResult = True):
      sptCmds.gotoLevel('1')

      if testSwitch.virtualRun:
         CELogData = """F3 T>/1N8

                                                          DERP
  dec       dec                                           error DERP
 Hours      Msec        LBA     R  Theta  Z       EC Cmd  type  retry temp count flag type
     0  00001225          3     0      0  0       C0  B0  FF     FF   22     1   00   SMART trip
     0  00001733          7     0      0  0       C0  B0  FF     FF   22     2   00   SMART trip
F3 1>"""
      else:
         CELogData = sptCmds.sendDiagCmd('N8', timeout = timeout, printResult = printResult)

      summaryData, ceData = self.parseCELog(CELogData)
      return CELogData, summaryData, ceData

   def parseCELog(self, CELogData):

      cmdDict = self.getCommandVersion('1','N') #{'majorRev':None,'minorRev':None}

      if testSwitch.virtualRun:
         cmdDict = getattr(self, 'cmdVersion', {'majorRev': 17, 'minorRev': 5})

      if float(cmdDict['majorRev'] + ( cmdDict['minorRev'] / 10.0 )) >= 17.5:
         CEPattern = re.compile('(?P<hours>[\da-fA-F]+)\s*(?P<msec>[\da-fA-F]+)\s*(?P<LBA>[\da-fA-F]+)\s*(?P<R>[\da-fA-F]+)\s*(?P<Theta>[\da-fA-F]+)\s*(?P<Z>[\da-fA-F]+)\s*\s*(?P<EC>[\da-fA-F]+)\s*(?P<Cmd>[\da-fA-F]+)\s*(?P<DERP_ER_TYPE>[\da-fA-F]+)\s*(?P<DERP_RETRY>[\da-fA-F]+)\s*(?P<Temp>[\da-fA-F]+)\s*(?P<Count>[\da-fA-F]+)\s*(?P<Type>.+)')
      else:
         CEPattern = re.compile('(?P<hours>[\da-fA-F]+)\s*-\s*(?P<LBA>[\da-fA-F]+)\s*(?P<R>[\da-fA-F]+)\s*(?P<Theta>[\da-fA-F]+)\s*(?P<Z>[\da-fA-F]+)\s*\s*(?P<EC>[\da-fA-F]+)\s*(?P<Cmd>[\da-fA-F]+)\s*(?P<DERP_ER_TYPE>[\da-fA-F]+)\s*(?P<DERP_RETRY>[\da-fA-F]+)\s*(?P<Temp>[\da-fA-F]+)\s*(?P<Count>[\da-fA-F]+)\s*(?P<Type>.+)')

      ceData = []
      ceSummaryData = {}
      for line in CELogData.splitlines():
         match = CEPattern.search(line)
         if match:
            entry = match.groupdict()
            ceData.append(entry)
            ceSummaryData[entry['EC']] = ceSummaryData.get(entry['EC'],0) + 1
      return ceSummaryData, ceData

   def smartDST(self,timeout = 2*60*60, mode = 'SHORT'):
      sptCmds.gotoLevel('1')

      if mode == 'LONG':
         sptCmds.sendDiagCmd('NC', printResult = True)
      else:
         sptCmds.sendDiagCmd('NB', printResult = True)

      accumulator = self.PChar(CTRL_T)
      result = sptCmds.promptRead(timeout,raiseException = 1, accumulator = accumulator, loopSleepTime = 10)

      objMsg.printMsg("DST Run Log:\n%s" % result)

      self.dumpSmartLog()

   def dumpSmartLog(self, timeout = 30):
      sptCmds.gotoLevel('1')
      result = sptCmds.sendDiagCmd('N8', printResult = True)

   def initDefectLog(self, maxNumberDefects = 1000, printResult = True):
      if printResult:
         objMsg.printMsg("*"*40)
         objMsg.printMsg("Setting up error logging")
      sptCmds.gotoLevel('L')
      errors = self.delActiveErrorLog(printResult = printResult)
      if testSwitch.extern.LBA_WIDER_THAN_32_BITS:
         maxDefectLogSize = maxNumberDefects * 56 # 56 bytes per entry
      else:
         maxDefectLogSize = maxNumberDefects * 48 # 48 bytes per entry
      sptCmds.sendDiagCmd('c10,0,0,%x' % (maxDefectLogSize,), printResult = printResult)
      sptCmds.sendDiagCmd('E10', printResult = printResult)
      sptCmds.sendDiagCmd('i10', printResult = printResult)
      sptCmds.sendDiagCmd('I', printResult = printResult)
      sptCmds.sendDiagCmd('E0', printResult = printResult)

   def setErrorLogging(self, enable = True, printResult = True):
      sptCmds.gotoLevel('L')
      if enable:
         if printResult:
            objMsg.printMsg("Enable error logging.")
         sptCmds.sendDiagCmd('E10', printResult = printResult)
      else:
         if printResult:
            objMsg.printMsg("Disable error logging.")
         sptCmds.sendDiagCmd('E0', printResult = printResult)

   def filterListofDicts(self, inList, key, values, include = True):
      #if type(values) not in (type([]), type(())):
      #   values = [values] # handle single value, non array type case
      outList = []
      subStrMatchFound = lambda res: res > -1
      for row in inList:
         valueMatch = True in map(subStrMatchFound, map(str(row[key]).find, values))
         if valueMatch:
            if include:
               outList.append(row)
         else:
            if not include:
               outList.append(row)
      return outList

   def retrieveLogInPieces(self, printResult = True):
         """
         if failure to retrieve log, then get log in chunks smaller than 512 bytes.
         """
         objMsg.printMsg("Attempting to retrieve D10 log in small chunks.")
         if not testSwitch.extern.FE_0132444_210712_ASCII_LOG_OUTPUT_RANGE:
            objMsg.printMsg("F3 testSwitch FE_0132444_210712_ASCII_LOG_OUTPUT_RANGE not detected, if required F3 code is actually lacking then failure is imminent.")

         baseCmd = cmd + ",,%X,%X"
         # retrieve header to find expected number of lines of data, and to see if log is full
         res = sptCmds.sendDiagCmd(baseCmd % (0,0,), printResult = printResult, DiagErrorsToIgnore = DiagErrorsToIgnore, loopSleepTime = 1)
         if failOnLogFull and res.rfind("Log Full") > -1:
            ScrCmds.raiseException(10278, "D10 Log Full")
         errCntMatch = self.errCntPat.search(res)
         if errCntMatch:
            numEntriesExpected = int(errCntMatch.group("errorCount"), 16)
         else:
            numEntriesExpected = 0
         # initialize the chunk list with the header + 2 lines of data.
         chunkList = [sptCmds.sendDiagCmd(baseCmd % (0,2,), printResult = printResult, DiagErrorsToIgnore = DiagErrorsToIgnore, loopSleepTime = 1)]
         # get rest of D10 log 4 lines at a time
         CHUNK_SIZE = 4
         for startLine in xrange(2, numEntriesExpected, CHUNK_SIZE):
            chunkList.append(sptCmds.sendDiagCmd(baseCmd % (startLine, CHUNK_SIZE,), printResult = True, DiagErrorsToIgnore = DiagErrorsToIgnore, loopSleepTime = 1))
         return "\n".join(chunkList)

   #======================================================================================================================================
   def getActiveErrorLog(self, printResult = True, filterDiagErrors = True, failOnLogFull = True, failOnMissingData = True, retries = 3, clearLog = False):

      if clearLog:
         cmd = 'd10'
         DiagErrorsToIgnore = ['00003010', '00008000']
      else:
         cmd = 'D10'
         DiagErrorsToIgnore = ['00003010']

      sptCmds.gotoLevel('L')
      for retry in xrange(retries):
         if testSwitch.virtualRun:
            res = """Result from D10 cmd:
                     D10
                     Log 10 Entries 5
                     Count DIAGERR  RWERR    LBA          PBA          SFI      WDG  LLL CHS         PLP CHS         Partition
                     ----- -------- -------- ------------ ------------ -------- ---- --------------- --------------- ---------
                     0001  00008000
                     0002  00003000
                     0001  00005004 C4090081 0000092428E7 0000092428E7 000E1059 01AE 00010443.0.0019 00010443.0.0019 User
                     0001  00005004 C4090081 0000092428E8 0000092428E8 000E1CFA 01B0 00010443.0.001A 00010443.0.001A User
                     0001  00005003 43110081 000013DBB7F4 000013F4F3C0 000D5C4B 0159 0001099C.0.0713 0001099C.0.0713 User
                     """
         else:
            if retry != 0:
               res = self.retrieveLogInPieces(printResult = printResult)
            else:
               try: # at first, attempt to get entire log in one shot
                  res = sptCmds.sendDiagCmd(cmd, printResult = printResult, DiagErrorsToIgnore = DiagErrorsToIgnore, loopSleepTime = 0)
               except CRaiseException, exceptionData:
                  errorCode = exceptionData[0][2]
                  if errorCode == 10566:
                     res = self.retrieveLogInPieces(printResult = printResult)
                  else:
                     raise

         if failOnLogFull and res.rfind("Log Full") > -1:
            ScrCmds.raiseException(10278, "D10 Log Full")

         logErrors, shortErrors = self.parseErrorLog(res)
         errCntMatch = self.errCntPat.search(res)
         if errCntMatch:
            numEntriesExpected = int(errCntMatch.group("errorCount"), 16)
         else:
            numEntriesExpected = 0
         numEntriesFound = len(logErrors) + len(shortErrors)
         if not failOnMissingData or numEntriesExpected == numEntriesFound:
            break
         else:
            objMsg.printMsg("Expected %d entries, found %d." % (numEntriesExpected, numEntriesFound))

      else:
         ScrCmds.raiseException(10566, "Failed to retreive D10 Data.")

      if filterDiagErrors:
         logErrors = self.filterListofDicts(logErrors, 'DIAGERR', ['00003010', '00000000', '00000006'], include = False)
      if testSwitch.virtualRun:
         logErrors = []
      return logErrors

   def delActiveErrorLog(self, printResult = True, filterDiagErrors = True):
      return self.getActiveErrorLog(printResult = printResult, filterDiagErrors = filterDiagErrors, failOnLogFull = False, failOnMissingData = False, clearLog = True)

   def readFullPack(self, timeout = 2*60*60, loopSleepTime = 5, spc_id = 1):
      sptCmds.gotoLevel('2')
      self.enableRWStats()
      result = self.sequentialGenericCommand(timeout, 'R', 'read', loopSleepTime = loopSleepTime)
      objMsg.printMsg("Full Pack Results:\n%s" % result)
      zoneData = self.getZoneBERData(spc_id = spc_id)
      self.setStateSpace('AD')
      return zoneData

   def setShortTestSpace(self, maxTrack = 0x100):
      self.setStateSpace('A9,%x' % maxTrack)

   def getCommandVersion(self, level, command, printResult = False):
      """
      Return the command version in decimal
      Valid level inputs are:
         hex = use level
         '^' = online command sent
         '0' = All level command
      """
      if not testSwitch.virtualRun:
         sptCmds.gotoLevel('C')
         res = sptCmds.sendDiagCmd('Q%s,%s' % (str(level),command), printResult = printResult)
      else:
         res = "Level 2 'T': Rev 0015.0000, Overlay, Measure Throughput, T[Opts],[CylSkew],[HeadSkew],[MiniZoneSkew],[SkewStep],[LengthInTracks],[OffsetInTracks],[NumberOfRetries]"

      parsePat = "Rev\s*(?P<majorRev>\d+)\.(?P<minorRev>\d+)"
      match = re.search(parsePat,res)
      if match:
         return self.convDictItems(match.groupdict(),int)
      else:
         objMsg.printMsg("Failed to parse cmd %s level %s rev info: Result: %s" % (command, level, res))
         return {'majorRev':None,'minorRev':None}

   def writeFullPack(self, timeout = 2*60*60, loopSleepTime = 5, spc_id = 1):
      sptCmds.gotoLevel('2')
      self.enableRWStats()
      result = self.sequentialGenericCommand(timeout, 'W', 'write', loopSleepTime = loopSleepTime)
      objMsg.printMsg("Full Pack Results:\n%s" % result)
      self.setStateSpace('AD', printResult = True)
      zoneData = self.getZoneBERData(spc_id = spc_id)
      return zoneData

   def setZeroPattern(self, printResult = False):
      sptCmds.gotoLevel('2')
      sptCmds.sendDiagCmd('P0,0,,1', printResult = printResult)

   def SetRepeatingPattern(self, DataPattern = 0x00000000):
      """
      Sets a repeating pattern with up to 128 bits (0x20).  Patterns longer than
      0x20 bytes are truncated.
      """
      sptCmds.gotoLevel('2')
      cmdPattern = "%x"%(DataPattern,)
      if len(str(DataPattern)) > 32:
         cmdPattern = cmdPattern[0:32].upper()
      else:
         cmdPattern = cmdPattern.upper()
      patternLengthInBits = ("%x"%(4*len(cmdPattern),)).upper()
      cmd = ",".join(['P1818', cmdPattern, patternLengthInBits])
      sptCmds.sendDiagCmd(cmd)

   def getClearances(self, head, rap = 14, printResult = False):
      data = []
      sptCmds.gotoLevel('2')
      if rap == 14:
         rapPat = re.compile('User Zone (?P<zone>[\da-fA-F]+):\s+(?P<WHClr>[\da-fA-F]+)\s+(?P<RHClr>[\da-fA-F]+)\s+(?P<WHClr_targ>[\da-fA-F]+)\s+(?P<PreClr_targ>[\da-fA-F]+)\s+(?P<RHClr_targ>[\da-fA-F]+)\s+(?P<MaintClr_targ>[\da-fA-F]+)')

         res = sptCmds.sendDiagCmd('I,1,F,%x' % head, printResult = printResult)

         for line in res.splitlines():
            match = rapPat.search(line)
            if match:
               data.append(self.convDictItems(match.groupdict(),int,[16,]))

      return data

   def setClearances(self, head, data, paramIndex, rap = 14, printResult = False):
      sptCmds.gotoLevel('2')
      if rap == 14:
         for index,zone in enumerate(data):
            sptCmds.sendDiagCmd('I%x,1,F,%x,%x,%x' % (zone, head, paramIndex, index), printResult = printResult)

   #======================================================================================================================================
   def marginClearanceTarget(self, percentReduction = 0.00, clearanceTarget = 'WRITE', heads = None):
      rap = 14
      numCyls, zones = self.getZoneInfo(printResult = True)

      if clearanceTarget == 'WRITE':
         paramIndex = 5
         paramName = 'WHClr_targ'
      elif clearanceTarget == 'READ':
         paramIndex = 7
         paramName = 'RHClr_targ'
      elif clearanceTarget == 'PRE':
         paramIndex = 6
         paramName = 'PreClr_targ'

      if heads == None:
         heads = range(self.dut.imaxHead)

      for head in heads:
         clearanceTargets = self.getClearances(head,rap = rap, printResult = True)
         # Strip out un-necessary data and margin the clearance
         clearanceTargets = [int(round(i[paramName]*(1-percentReduction))) for i in clearanceTargets]

         objMsg.printMsg("Modified clearanceTargets = %s" % (clearanceTargets,))

         self.setClearances(head, clearanceTargets, paramIndex, rap = rap, printResult = True)

         objMsg.printMsg("Verify settings:")
         clearanceTargets = self.getClearances(head,rap = rap, printResult = True)

      #Enable temp tweaks
##Found to cause servo unsafe errors on current products
##       sptCmds.gotoLevel('7')
##       sptCmds.sendDiagCmd('U,10,ff,ff', printResult = True)
##       sptCmds.sendDiagCmd('U,20,ff,ff', printResult = True)

      try:
         sptCmds.sendDiagCmd(CTRL_T,printResult=True)
      except:
         #Wait for drive to fully reset
         time.sleep(10)
      sptCmds.enableDiags()
      sptCmds.gotoLevel('2')
      #Dump out new working parameters for tweak validation
      sptCmds.sendDiagCmd('I,3', printResult = True)

   #======================================================================================================================================
   def sequentialGenericCommand(self, timeout, command, commandName = None, numLoops = None, startCyl = 0, byHead = False, head = None, loopSleepTime = 5):
      """
      numLoops = none is full pack
      """
      if commandName == None:
         commandName = str(command)

      lCommandRevInfo = self.getCommandVersion('0','L')
      if byHead == False and (lCommandRevInfo['majorRev'] > 1 or (lCommandRevInfo['majorRev'] == 1 and lCommandRevInfo['minorRev'] >= 2)):
         self.seekTrack(startCyl,0, printResult = True)

         self.setStateSpace('A3', printResult = True)
         if SHORT_DIAG_DEBUG or not numLoops == None:
            if numLoops == None:
               numLoops = 0x100
            self.setShortTestSpace(numLoops)

         sptCmds.gotoLevel('2')
         sptCmds.sendDiagCmd('L41', printResult = True)
         objMsg.printMsg("Issuing %s command." % commandName)
         accumulator = self.PBlock(command)
         result = sptCmds.promptRead(timeout, 1, altPattern=None, accumulator = accumulator, loopSleepTime= loopSleepTime)
      else:
         sptCmds.gotoLevel('2')

         numCyls,zones = self.getZoneInfo(printResult = False)

         if head == None:
            heads = range(len(numCyls))
         else:
            heads = [head,]

         for head in heads:
            self.seekTrack(startCyl,head, printResult = True)
            self.setStateSpace('A2', printResult = True)
            if SHORT_DIAG_DEBUG:
               self.setShortTestSpace(0x100)
               numCyls[head] = 100
            if not numLoops == None:
               numCyls[head] = numLoops
            sptCmds.sendDiagCmd('L1,%x' % numCyls[head], printResult = True)
            objMsg.printMsg("Issuing %s command." % commandName)
            accumulator = self.PBlock(str(command))
            result = sptCmds.promptRead(timeout, 1, altPattern=None, accumulator = accumulator, loopSleepTime= loopSleepTime)
            objMsg.printMsg("Command Response:\n%s" % result)
      return result

   def writeSector(self, startSector, numSectors):


      sptCmds.gotoLevel('2')
      self.flush()
      if numSectors == '*':
         accumulator = self.PBlock('W\n')
      else:
         accumulator = self.PBlock('W%x,%x\n' % (startSector,numSectors))
      results = sptCmds.promptRead(30, accumulator = accumulator )
      if DEBUG == 1:
         objMsg.printMsg(str(results),objMsg.CMessLvl.DEBUG)
      self.flush()

   def setStateSpace(self,space = 'A0', printResult = False):
      sptCmds.gotoLevel('2')
      sptCmds.sendDiagCmd(space,30,printResult = printResult, loopSleepTime = 0)
      #sptCmds.gotoLevel('2')
      #sptCmds.sendDiagCmd(space,30,printResult = printResult)

   #======================================================================================================================================
   def SmartCmd(self,smartParams, dumpDEBUGResponses = 0):
      """
      Reset the RAM and SMART Sectors on the RAM and DISC
      @param smartParams: Dictionary of smart parameters defined below

      Parameters
      ==========
         - "options": List of N1 options to execute.
            - EG: [1, 7, 8] #Will init SMART, Dump G list, and Dump critical event log
         - initFastFlushMediaCache: Set to 1 to initialize the Fast Flush and Media Cache on the disk. Valid only w/ "option" 1
         - timeout: Test Timeout alotment for each N command; Default 600 Seconds
         - retries: Allotted retries for the command; Default 2
      Further Documentation
      =====================
          Doc_Link: U{Diagnostic 1>N1 from Mike Mytych <http://firmware.seagate.com/diag/Diag%20Command%20Documentation/RightFrame.html#SMART Control>}
      """
      timeout = smartParams.get('timeout',600)
      retries = smartParams.get('retries',2)
      initFastFlushMediaCache = smartParams['initFastFlushMediaCache']

      options = smartParams['options']

      sucPat = re.compile(self.prPat)
      errPat = re.compile('Error\s*(?P<rwErrCode>[a-f,0-9,A-F]{4})\s*DETSEC\s*(?P<rwExtCode>[a-f,0-9,A-F]{8})')

      for itOp in options:
         objMsg.printMsg("Issuing  Level 1 N%X" %itOp)
         if testSwitch.virtualRun:
            continue
         success = 0
         retry = 0
         while success == 0:
            res = ''


            sptCmds.gotoLevel('1')
            self.flush()
            sendVal = hex(itOp)[2:]
            if itOp == 1 and initFastFlushMediaCache == 1:
               sendVal += ",1"
            accumulator = self.PBlock('N'+ sendVal + '\n')
            res = sptCmds.promptRead(timeout, accumulator = accumulator )
            if dumpDEBUGResponses == 1:
               objMsg.printMsg(str(res), objMsg.CMessLvl.VERBOSEDEBUG)
            if itOp in [7,8]:
               objMsg.printMsg(str(res), objMsg.CMessLvl.DEBUG)
            if len(sucPat.findall(res)) > 0 and \
               len(errPat.findall(res))== 0:
               #Break while loop because we've found the success pattern
               success = 1
            else:
               errResult = errPat.search(res)
               erMsg = "Failed 1>N%s command:\n%s" % (sendVal,res)
               if not errResult == None:
                  erMsg += '\n'
                  erDict = errResult.groupdict()
                  try:
                     rwExpl = translateRwErrorCode(int(erDict['rwExtCode'],16))
                     objMsg.printMsg("RW Error Descrip: %s=%s" % (tempDic['rwExtCode'],str(rwExpl)), objMsg.CMessLvl.DEBUG)
                  except:
                     pass
                  for item in erDict.items():
                     erMsg += '\t%s: %s' % (item[0],item[1])

               objMsg.printMsg(erMsg, objMsg.CMessLvl.DEBUG)
               retry += 1
               if retry > retries:
                  if itOp & (1|4):
                     ScrCmds.raiseException(12965, erMsg)
                  else:
                     ScrCmds.raiseException(10467,erMsg)

   def syncBaudRate(self, baudRate=DEF_BAUD):
      """
      Synchronize baud rate using ASCII diag mode.
      Usage: syncBaudRate(baudRate)
      Where: baudRate = drive supported baud rate value in ASCII diag mode.
      """
      if testSwitch.FE_0155584_231166_P_RUN_ALL_DIAG_CMDS_LOW_BAUD:
         sptCmds.syncBaudRate(baudRate)
      else:
         theBaud = theCell.getBaud()
         diagLevel = sptCmds.currLevel
         if theBaud!=baudRate:
            objMsg.printMsg("Adjusting baud rate from %s to %s." %(theBaud, baudRate))


            sptCmds.gotoLevel('T')
            try:
               sptCmds.sendDiagCmd('B%s' %baudRate, timeout=30, printResult=True)
            except:
               pass
            theCell.setBaud(baudRate)                       # Change the cell baud rate
            sptCmds.gotoLevel(diagLevel)
            self.dut.baudRate = baudRate

   #======================================================================================================================================
   if not testSwitch.FE_0163564_410674_GET_ZONE_INFO_BY_HEAD_AND_BY_ZONE:
      def getZoneInfo(self, printResult = False, partition = 0):
         """
         partition parameter
          User Partion = 0
          System Partition = 1
          SMART OD = 2
          SMART ID = 3
         """


         sptCmds.gotoLevel('2')
         self.flush()
         accumulator = self.PBlock('x%x\n\n' % partition)
         data = sptCmds.promptRead(100, accumulator = accumulator, loopSleepTime = 0)
         if DEBUG > 0 or printResult:
            objMsg.printMsg(data)
         self.flush()
         if testSwitch.FE_0132639_405392_CHANGE_ZONE_DATA_FROM_PHYCYL_TO_LOGCYL:
            zonePat = re.compile('^\s*(?P<zone>[\dA-Fa-f]+)\s+[\dA-Fa-f]+-[\dA-Fa-f]+\s+(?P<minLogCyl>[\dA-Fa-f]+)')
         else:
            zonePat = re.compile('^\s*(?P<zone>[\dA-Fa-f]+)\s+(?P<minCyl>[\dA-Fa-f]+)')
         dataLines = data.split('\n')

         numCyls = []
         zones = {}
         maxLogicalPat = re.compile('Head (?P<head>\d+), PhyCyls [\da-fA-f ]+-[\da-fA-f ]+, LogCyls [\da-fA-f ]+-(?P<MaxLogicalCyl>[\da-fA-f ]+)')

         for line in dataLines:
            line = line.strip()
            logMat = maxLogicalPat.search(line)
            if logMat:
               numCyls.append(int(logMat.groupdict()['MaxLogicalCyl'],16))
               currHead = int(logMat.groupdict()['head'],16)

            zoneMatch = zonePat.match(line)
            if zoneMatch and not(line.strip().startswith('F3')):
               tempDict = zoneMatch.groupdict()
               if len(numCyls) > 0:
                  if testSwitch.FE_0132639_405392_CHANGE_ZONE_DATA_FROM_PHYCYL_TO_LOGCYL:
                     zones.setdefault(currHead,{})[int(tempDict['zone'],16)] = int(tempDict['minLogCyl'],16)
                  else:
                     zones.setdefault(currHead,{})[int(tempDict['zone'],16)] = int(tempDict['minCyl'],16)

         if testSwitch.virtualRun:
            numCyls = [150000,]
            if testSwitch.BF_0119058_399481_NUMCYLS_LIST_LENGTH_EQUAL_TO_NUMHEADS :
               driveInfo = self.dut.dblData.Tables('P172_DRIVE_INFO').tableDataObj()

               self.dut.numZones = int(driveInfo[-1]['NUM_USER_ZONES'])
               #hdcount = int(driveInfo[-1]['MAX_HEAD'])

               maxCylInfo = self.dut.dblData.Tables('P172_MAX_CYL_VBAR').tableDataObj()

               self.dut.maxTrack = [int(item["MAX_CYL_DEC"]) for item in maxCylInfo]
               numCyls = self.dut.maxTrack

               zones = {}
               for head in xrange(len(numCyls)):
                  tmp = {}
                  map(tmp.setdefault, range(0,self.dut.numZones), range(0,numCyls[head],numCyls[head]/self.dut.numZones)[:-1])
                  map(zones.setdefault, [head], [tmp,])
            else:
               tmp = {}
               zones = {}
               map(tmp.setdefault, range(0,17), range(0,17*10000,10000))
               map(zones.setdefault, range(0,2), [tmp,]*2)

         self.dut.imaxHead = len(numCyls) #imaxHead is really numHeads
         objMsg.printMsg("Setting imaxHead to %xh" % self.dut.imaxHead)
         self.dut.numZones = len(zones[0])
         objMsg.printMsg("Setting numZones to %xh" % self.dut.numZones)

         if self.dut.imaxHead == 0 or self.dut.numZones == -1:
            ScrCmds.raiseException(11044, "Failed to identify head-zone config of DUT.")

         return numCyls,zones
   else:
      def getZoneInfo(self, printResult = False, partition = 0):
         """
         partition parameter
          User Partion = 0
          System Partition = 1
          SMART OD = 2
          SMART ID = 3
         """
         if testSwitch.virtualRun:
            PRData0 = '''x0,0,0

User Partition

 LBAs 000000000000-000007470C07
 PBAs 000000000000-0000077FD263
 HdSkew 0078, CylSkew 0021
 ZonesPerHd 1F

 Head 0, PhyCyls 000000-0364DA, LogCyls 000000-0362FB

     Physical      Logical       Sec   Sym   Sym      Data
  Zn Cylinders     Cylinders     Track Wedge Track    Rate
  00 000000-000A39 000010-000A39 016A  1118  00114E00 1267.031
NumMediaCacheZones 00

F3 2>'''
            PRData10 = '''x0,0,a

User Partition

 LBAs 000000000000-000004A85D57
 PBAs 000000000000-000004CB7E8F
 HdSkew 0078, CylSkew 0021
 ZonesPerHd 1F

 Head 0, PhyCyls 000000-030B70, LogCyls 000000-030991

     Physical      Logical       Sec   Sym   Sym      Data
  Zn Cylinders     Cylinders     Track Wedge Track    Rate
  0A 010852-011E3B 010852-011E3B 00CE  09C1  0009EA00  725.976
NumMediaCacheZones 00

F3 2>'''
            PRData21 = '''x0,0,15

User Partition

 LBAs 000000000000-000004A85D57
 PBAs 000000000000-000004CB7E8F
 HdSkew 0078, CylSkew 0021
 ZonesPerHd 1F

 Head 0, PhyCyls 000000-030B70, LogCyls 000000-030991

     Physical      Logical       Sec   Sym   Sym      Data
  Zn Cylinders     Cylinders     Track Wedge Track    Rate
  15 021630-02325F 021450-02307F 00A7  07ED  00081600  592.236
NumMediaCacheZones 00

F3 2>'''
         self.getNumHead()
         self.getNumZone()
         if DEBUG: objMsg.printMsg("GetZnInfo - imaxHead is %d numzn is %d" % (self.dut.imaxHead, self.dut.numZones))
         sptCmds.gotoLevel('2')
         maxLogicalPat = re.compile('Head (?P<head>\d+), PhyCyls [\da-fA-f ]+-[\da-fA-f ]+, LogCyls [\da-fA-f ]+-(?P<MaxLogicalCyl>[\da-fA-f ]+)')
         if testSwitch.FE_0132639_405392_CHANGE_ZONE_DATA_FROM_PHYCYL_TO_LOGCYL:
            #zonePat = re.compile('\s*(?P<zone>[\dA-Fa-f]+)\s+[\dA-Fa-f]+-[\dA-Fa-f]+\s+(?P<minLogCyl>[\dA-Fa-f]+)')
            zonePat = re.compile('\s*Rate\s*(?P<zone>[\dA-Fa-f]+)\s+(?P<minCyl>[\dA-Fa-f]+)-[\dA-Fa-f]+\s+(?P<minLogCyl>[\dA-Fa-f]+)')
         else:
            zonePat = re.compile('\s*Rate\s*(?P<zone>[\dA-Fa-f]+)\s+(?P<minCyl>[\dA-Fa-f]+)')


         numCyls = []
         zones = {}
         for hd in range(self.dut.imaxHead):
            for zn in range(self.dut.numZones):
               self.flush()
               accumulator = self.PBlock('x0,%x,%x\n\n' % (hd,zn))
               data = sptCmds.promptRead(100, accumulator = accumulator, loopSleepTime = 0)
               if testSwitch.virtualRun:
                  data = PRData0
                  if zn==10: data = PRData10
                  if zn==21: data = PRData21
               zoneMatch = zonePat.search(data)
               if DEBUG: objMsg.printMsg("GetZnInfo - accum=%s znmatch=%s" % (accumulator,zoneMatch))
               if zoneMatch and not(data.strip().startswith('F3')):
                  tempDict = zoneMatch.groupdict()
                  if DEBUG: objMsg.printMsg("GetZnInfo - tempDict=%s" % tempDict)
                  if testSwitch.FE_0132639_405392_CHANGE_ZONE_DATA_FROM_PHYCYL_TO_LOGCYL:
                     zones.setdefault(hd,{})[int(tempDict['zone'],16)] = int(tempDict['minLogCyl'],16)
                  else:
                     zones.setdefault(hd,{})[int(tempDict['zone'],16)] = int(tempDict['minCyl'],16)

            logMat = maxLogicalPat.search(data)
            if logMat:
               numCyls.append(int(logMat.groupdict()['MaxLogicalCyl'],16))
         if DEBUG: objMsg.printMsg("GetZnInfo - numCyls=%s zones=%s" % (numCyls,zones))

         if testSwitch.virtualRun:
            numCyls = [150000,]
            if testSwitch.BF_0119058_399481_NUMCYLS_LIST_LENGTH_EQUAL_TO_NUMHEADS :
               driveInfo = self.dut.dblData.Tables('P172_DRIVE_INFO').tableDataObj()

               self.dut.numZones = int(driveInfo[-1]['NUM_USER_ZONES'])
               #hdcount = int(driveInfo[-1]['MAX_HEAD'])

               maxCylInfo = self.dut.dblData.Tables('P172_MAX_CYL_VBAR').tableDataObj()

               self.dut.maxTrack = [int(item["MAX_CYL_DEC"]) for item in maxCylInfo]
               numCyls = self.dut.maxTrack

               zones = {}
               for head in xrange(len(numCyls)):
                  tmp = {}
                  map(tmp.setdefault, range(0,self.dut.numZones), range(0,numCyls[head],numCyls[head]/self.dut.numZones)[:-1])
                  map(zones.setdefault, [head], [tmp,])
            else:
               tmp = {}
               zones = {}
               map(tmp.setdefault, range(0,17), range(0,17*10000,10000))
               map(zones.setdefault, range(0,2), [tmp,]*2)

         objMsg.printMsg("Setting imaxHead to %xh" % self.dut.imaxHead)
         objMsg.printMsg("Setting numZones to %xh" % self.dut.numZones)

         if self.dut.imaxHead == 0 or self.dut.numZones == -1:
            ScrCmds.raiseException(11044, "Failed to identify head-zone config of DUT.")

         return numCyls,zones

   def getNumHead(self):
      data = sptCmds.sendDiagCmd(CTRL_L,printResult=True)
      hdPat = re.compile('Heads:\s+(?P<head>[\dA-Fa-f]+)')
      hdMat = hdPat.search(data)
      if hdMat:
         self.dut.imaxHead = int(hdMat.groupdict()['head'],16)

   def getNumZone(self):
      sptCmds.gotoLevel('2')
      if testSwitch.virtualRun:
         data = '''User Partition

 LBAs 000000000000-000007485760
 PBAs 000000000000-00000782F698
 HdSkew 0078, CylSkew 0021
 ZonesPerHd 20

 Head 0, PhyCyls 000000-03BBF3, LogCyls 000000-03BA14

     Physical      Logical       Sec   Sym   Sym      Data
  Zn Cylinders     Cylinders     Track Wedge Track    Rate
  00 000000-000BD5 000000-000BD5 015C  106B  0010A300 1218.515
NumMediaCacheZones 01
         '''

      else:
         data = sptCmds.sendDiagCmd('x0,0,0',printResult=True)
      maxZonePat = re.compile('ZonesPerHd\s+(?P<max_zone>[\dA-Fa-f]+)')
      maxZoneMat = maxZonePat.search(data)
      if maxZoneMat:
         self.dut.numZones = int(maxZoneMat.groupdict()['max_zone'],16)
         if DEBUG: objMsg.printMsg("Set numzn to %d" % self.dut.numZones)
         # parse data from "NumMediaCacheZones 1"
         mcZones = re.compile('NumMediaCacheZones\s+(?P<mcZones>[\dA-Fa-f]+)').search(data)
         if mcZones:
            self.NumMCZone = int(mcZones.groupdict()['mcZones'], 16)
            self.dut.numZones -= self.NumMCZone
            if DEBUG: objMsg.printMsg("Non-zero MediaCacheZn=%d found! Final numzn set to %d" % (self.NumMCZone, self.dut.numZones))

   def printErrors(self,errors):
      if len(errors) > 1:
         objMsg.printMsg(str('%s\t%s\t%s\t%s' % ('EC','Track','Head','Sector')),objMsg.CMessLvl.DEBUG)
         for err in errors:
            if len(err) > 0:
               objMsg.printMsg(str('%s\t%s\t%s\t%s' % err[0]),objMsg.CMessLvl.DEBUG)

   def enableRWStats(self, maxRetries = 20, printResult = True):
      """
      Enable the online RW diagnostics with the Control-W character and zero BER stats.
      """
      if printResult:
         objMsg.printMsg("Enabling Rd/Wr Statistics", objMsg.CMessLvl.VERBOSEDEBUG)

      retry = 0
      while retry < maxRetries:
         self.flush()
         accumulator = self.PChar(CTRL_W)
         data = sptCmds.promptRead(2,0, altPattern = "Rd/Wr stats", accumulator = accumulator)
         if data.find('Rd/Wr stats On') != -1 or testSwitch.virtualRun:
            if printResult:
               objMsg.printMsg("Passed set Rd/Wr Stats On:%s" % data)
            break
         else:
            objMsg.printMsg("\nFailure Debug Dump:\n%s" % data)
            retry += 1
      else:
         if not testSwitch.virtualRun:
            ScrCmds.raiseException(105666,"Failed to enable Rd/Wr stats")

      self.zeroBERCounters()

   def zeroBERCounters(self,maxRetries = 3):
      retry = 0
      while retry < maxRetries:
         try:
            sptCmds.gotoLevel('L')
            accumulator = self.PBlock('iFFFD')
            sptCmds.promptRead(10,1, accumulator = accumulator )
            break
         except:
            retry += 1
      else:
         if not testSwitch.virtualRun:
            ScrCmds.raiseException(10566,"Failed to zero BER counters.")


   def translateLBA(self, LBA):
      lbaXlatePattern = '\S+\s+User\s+(?P<PHYSICAL_CYL>[a-fA-F\d]+)\s+(?P<LOGICAL_CYL>[a-fA-F\d]+)\s+(?P<NOMINAL_CYL>[a-fA-F\d]+)\s+\S+\s+(?P<LOGICAL_HEAD>[a-fA-F\d]+)'

      sptCmds.gotoLevel('A')

      if not testSwitch.virtualRun:
         data = sptCmds.sendDiagCmd('F%x' % (LBA,))
      else:
         data = """
               Partition PhyCyl   LogCyl   NomCyl   RadiusMils   LogHd Zn FirstLba FirstPba LogSecs PhySecs WdgSkw SecPerFrm WdgPerFrm
               User      0001CEBC 0001CC8C 0001C5A9 +5.730000E+2 01    10 2542E898 2543F123 0218    0369    00D8   0027      000A
               """

      data = data.replace("\n","")
      match = re.search(lbaXlatePattern, data)
      if match:
         tempDict = match.groupdict()
         return self.convDictItems(tempDict, int, [16,])
      else:
         ScrCmds.raiseException(11044, "Unable to parse translate LBA response: \npattern = %s\nbuffer = %s" % (lbaXlatePattern, data))

   #======================================================================================================================================
   def getZoneRangesByHead(self, head):
      '''
      Returns a dictionary for the input head containing the start and end user LBAs and logical cylinders for each zone
      '''
      zoneRange={}
      if testSwitch.virtualRun:
         data = """

User Partition

 LBAs 000000000000-00000A4766E2
 PBAs 000000000000-00000AA1D058
 HdSkew 0078, CylSkew 002B
 ZonesPerHd 3E

 Head 0, PhyCyls 000000-04BE02, LogCyls 000000-04BB92

     Physical      Logical       Sec   Sym   Sym      Data
  Zn Cylinders     Cylinders     Track Wedge Track    Rate
  00 000000-000F3B 000000-000F3B 017F  0CB0  0012F348 1401.977
  01 002134-002134 000F3C-000F3C 017D  0CA1  0012DD40 1395.385
  02 003106-003F15 000F3C-001D4B 017A  0C87  0012B710 1384.399
  03 003F16-005107 001D4C-002F3D 018F  0D3A  0013C0E8 1461.303
  04 005108-005FC0 002F3E-003DF6 018C  0D20  00139C30 1450.317
  05 005FC1-007F64 003DF7-005D9A 0171  0C3C  001248E8 1352.539
  06 007F65-00AF0C 005D9B-008D42 016D  0C19  00121408 1337.158
  07 00AF0D-00CC58 008D43-00AA8E 0169  0BF7  0011E218 1322.875
  08 00CC59-00E3FA 00AA8F-00C230 0167  0BE7  0011CC10 1316.284
  09 00E3FB-0102D6 00C231-00E10C 0163  0BC4  00119730 1300.903
  0A 0102D7-0120B8 00E10D-00FEEE 015F  0BA4  001169A8 1287.719
  0B 0120B9-01434A 00FEEF-012180 015A  0B78  00112908 1269.042
  0C 01434B-015ABA 012181-0138F0 0157  0B60  001105C8 1259.155
  0D 015ABB-01722A 0138F1-015060 0153  0B3D  0010D3D8 1244.873
  0E 01722B-018D82 015061-016BB8 014F  0B1D  0010A360 1230.590
  0F 018D83-01A29A 016BB9-0180D0 014C  0B02  00107D30 1219.604
  10 01A29B-01B7E4 0180D1-01961A 0149  0AE5  00105298 1207.519
  11 01B7E5-01D1DE 01961B-01B014 0145  0AC6  00102510 1194.335
  12 01D1DF-01F182 01B015-01CFB8 0140  0A9E  000FE8D8 1176.757
  13 01F183-020924 01CFB9-01E75A 013C  0A7C  000FB6E8 1162.475
  14 020925-021F9A 01E75B-01FDD0 0139  0A60  000F8DC8 1150.390
  15 021F9B-02325A 01FDD1-021090 0136  0A49  000F6C00 1140.502
  16 02325B-0249CA 021091-022800 0132  0A27  000F3A10 1126.220
  17 0249CB-025AC8 022801-0238FE 012F  0A0D  000F13E0 1115.234
  18 025AC9-027170 0238FF-024FA6 012B  09EC  000EE1F0 1100.952
  19 027171-0280DE 024FA7-025F14 0128  09D2  000EBD38 1089.965
  1A 0280DF-02936C 025F15-0271A2 0125  09BA  000E99F8 1080.078
  1B 02936D-02A91A 0271A3-028750 0121  0997  000E6808 1065.795
  1C 02A91B-02B91E 028751-029754 011E  097E  000E41D8 1054.809
  1D 02B91F-02CD0A 029755-02AB40 011B  0964  000E1BA8 1043.823
  1E 02CD0B-02E8C6 02AB41-02C6FC 0116  093B  000DDF70 1026.245
  1F 02E8C7-030162 02C6FD-02DF98 0112  0919  000DAD80 1011.962
  20 0303D4-0311B1 02DF99-02ED76 010E  08F9  000D7D08  997.680
  21 0311B2-032057 02ED77-02FC1C 010B  08DF  000D56D8  986.694
  22 032058-03305B 02FC1D-030C20 0108  08C4  000D30A8  975.708
  23 03305C-034767 030C21-03232C 0103  089B  000CF470  958.129
  24 034768-035C1B 03232D-0337E0 0100  0881  000CCE40  947.143
  25 035C1C-036AC1 0337E1-034686 00FD  0868  000CA810  936.157
  26 036AC2-037EDF 034687-035AA4 00FA  084C  000C7D78  924.072
  27 037EE0-03945B 035AA5-037020 00F5  0826  000C45A8  907.592
  28 03945C-03A5EF 037021-0381B4 00F2  080C  000C1F78  896.606
  29 03A5F0-03B8E1 0381B5-0394A6 00EE  07E9  000BEC10  882.324
  2A 03B8E2-03C755 0394A7-03A31A 00EB  07CE  000BC468  870.239
  2B 03C756-03D8E9 03A31B-03B4AE 00E7  07AE  000B9568  857.055
  2C 03D8EA-03E8BB 03B4AF-03C480 00E4  0794  000B6F38  846.069
  2D 03E8BC-03F4A5 03C481-03D06A 00E1  077D  000B4D70  836.181
  2E 03F4A6-040607 03D06B-03E1CC 00DD  075B  000B1B80  821.899
  2F 040608-0415D9 03E1CD-03F19E 00DA  0740  000AF260  809.814
  30 0415DA-04244D 03F19F-040012 00D8  072F  000ADAE0  803.222
  31 04244E-042FA1 040013-040B66 00D4  070F  000AAA68  788.940
  32 042FA2-043F73 040B67-041B38 00D0  06EC  000A7878  774.658
  33 043F74-044E7D 041B39-042A42 00CD  06D2  000A5248  763.671
  34 044E7E-045E81 042A43-043A46 00CA  06BB  000A3080  753.784
  35 045E82-046D8B 043A47-044950 00C7  06A1  000A0A50  742.797
  36 046D8C-047B05 044951-0456CA 00C5  068F  0009EFE0  735.107
  37 047B06-048B09 0456CB-0466CE 00C2  0675  0009C9B0  724.121
  38 048B0A-049B0D 0466CF-0476D2 00BF  065D  0009A670  714.233
  39 049B0E-04A94F 0476D3-048514 00BC  0637  00096EA0  697.753
  3A 04A950-04B3DB 048515-048FA0 00BC  0637  00096EA0  697.753
  3B 04B3DC-04BE02 048FA1-0499C7 00C3  067E  0009D9D8  728.515
  3C 000F3C-002133 0499C8-04ABBF 017D  0CA1  0012DD40 1395.385
  3D 002134-003105 04ABC0-04BB91 017A  0C87  0012B710 1384.399
NumMediaCacheZones 02

Spare pool
 Start Logical Cyl: 049D76  Logical Hd: 1
 PBAs: 00000A2FDCC9-00000A3D9624
            """
      else:
         sptCmds.gotoLevel('7')
         data = sptCmds.sendDiagCmd('x00,%x'%head) #grab user zone info
      pattern = '.*?(?P<ZN>[0-9,a-h,A-H]{2})\s+(?P<PHYS_CYL_START>[0-9,a-h,A-H]{6})-(?P<PHYS_CYL_END>[0-9,a-h,A-H]{6})\s+(?P<START_LGC_CYL>[0-9,a-h,A-H]{6})-(?P<END_LGC_CYL>[0-9,a-h,A-H]{6})'
      data = data.replace("\n","")
      data = data.replace("\r","")
      data = data.split('NumMediaCacheZones')[0]
      if re.search(pattern,data):
         matches = re.finditer(pattern,data)
         for i in matches:
            tempDict = i.groupdict()
            startCylInfo = self.getTrackInfo(int(tempDict['START_LGC_CYL'],16), head, mode = 'logical')
            endCylInfo = self.getTrackInfo(int(tempDict['END_LGC_CYL'],16), head, mode = 'logical')
            zoneRange[tempDict['ZN']] = {'START_PHY_CYL' : tempDict['PHYS_CYL_START'],
                                         'END_PHY_CYL'   : tempDict['PHYS_CYL_END'],
                                         'START_LGC_CYL' : tempDict['START_LGC_CYL'],
                                         'END_LGC_CYL'   : tempDict['END_LGC_CYL'],
                                         'START_LBA'     : startCylInfo['FIRST_LBA'],
                                         'END_LBA'       : (endCylInfo['FIRST_LBA'] + endCylInfo['LOG_SECS']- 1)}
      else:
         ScrCmds.raiseException(11044, "Unable to parse zone information: \npattern = %s\nbuffer = %s" % (pattern, data))
      #self.dut.numZones
      return zoneRange

   def getZoneRanges(self):
      '''
      Returns a list (indexed by head) containing a dictionary indexed by zones that returns the start and end LBA and logical cylinders for a given head/zone
      '''
      headZoneRanges=[]
      for head in xrange(self.dut.imaxHead):
         headZoneRanges.append(self.getZoneRangesByHead(head))
      return headZoneRanges

   @spt
   def getLBARange(self):
      lbaXlatePattern = '\S+\s+User\s+LBA\s+Mode\s+LBAs\s(?P<START_LBA>[a-fA-F\d]+)\s-\s(?P<END_LBA>[a-fA-F\d]+)'

      sptCmds.gotoLevel('A')

      if not testSwitch.virtualRun:
         data = sptCmds.sendDiagCmd('AD')
      else:
         data = """
               AD .. User LBA Mode  LBAs 00000000 - 095738AF
               """

      data = data.replace("\n","")
      match = re.search(lbaXlatePattern, data)
      if match:
         tempDict = match.groupdict()
         tempDict = self.convDictItems(tempDict, int, [16,])
         return tempDict['START_LBA'], tempDict['END_LBA']
      else:
         ScrCmds.raiseException(11044, "Unable to parse LBA information: \npattern = %s\nbuffer = %s" % (lbaXlatePattern, data))

   def getLogTrkRanges(self):
      '''
      Return dictionary by head of Minimum and Maximum logical tracks
      '''
      zoneRanges = self.getZoneRanges()

      logCylRanges = {}
      for head in xrange(self.dut.imaxHead):
         for zone in zoneRanges[head].keys():
            if not logCylRanges.has_key(head):
               logCylRanges[head] = {'MIN_LOG_CYL': int(zoneRanges[head][zone]['START_LGC_CYL'],16),\
                                     'MAX_LOG_CYL': int(zoneRanges[head][zone]['END_LGC_CYL'],16)}
               if testSwitch.FE_0228550_357260_P_LIMIT_LOGICAL_TRACK_RANGE_PER_PHYSICAL_MAX:
                  logCylRanges[head].update({'MIN_PHY_CYL': int(zoneRanges[head][zone]['START_PHY_CYL'],16),\
                                             'MAX_PHY_CYL': int(zoneRanges[head][zone]['END_PHY_CYL'],16)})
            else:
               logCylRanges[head].update({'MIN_LOG_CYL' : min(logCylRanges[head]['MIN_LOG_CYL'], int(zoneRanges[head][zone]['START_LGC_CYL'],16)),\
                                     'MAX_LOG_CYL' : max(logCylRanges[head]['MAX_LOG_CYL'], int(zoneRanges[head][zone]['END_LGC_CYL'],16))})
               if testSwitch.FE_0228550_357260_P_LIMIT_LOGICAL_TRACK_RANGE_PER_PHYSICAL_MAX:
                  logCylRanges[head].update({'MIN_PHY_CYL' : min(logCylRanges[head]['MIN_PHY_CYL'], int(zoneRanges[head][zone]['START_PHY_CYL'],16)),\
                                             'MAX_PHY_CYL' : max(logCylRanges[head]['MAX_PHY_CYL'], int(zoneRanges[head][zone]['END_PHY_CYL'],16))})
         if testSwitch.FE_0228550_357260_P_LIMIT_LOGICAL_TRACK_RANGE_PER_PHYSICAL_MAX:
            # Max logical track may exceed max physical is some case (e.g. Media Cache)
            # - Limit Max Logical track to logical track of last physical track
            maxPhysLogTrack = self.getTrackInfo(logCylRanges[head]['MAX_PHY_CYL'], head, mode = 'physical')['LOG_CYL']
            logCylRanges[head]['MAX_LOG_CYL'] = min(maxPhysLogTrack, logCylRanges[head]['MAX_LOG_CYL'])

      return logCylRanges

   #======================================================================================================================================
   def getTrackInfo(self, Track, Head, printResult = False, nominalCylinder = False, mode = 'physical', retries = 5):
      '''
         Query drive for track (logical or physical) information.
          - Uses level 'A' - 'd' (Translate Physical Cylinder) diagnostic for 'mode' = 'physical'
          - Uses level 'A' - 'c' (Translate Logical Cylinder) diagnostic for 'mode' = 'logical'
         Returns dictionary with: 'PHY_CYL', 'LOG_CYL', 'NOM_CYL', 'LOG_HEAD', 'ZONE', 'FIRST_LBA', 'FIRST_PBA', 'LOG_SECS', 'PHY_SECS'
      '''

      if DEBUG > 0:
         printResult = True

      translatePatterns = {   # '<Data Format Type>' : [<Detect Pattern>, <Translate Pattern>]
         'F3Trunk'       : self.F3TrunkInfoPattern,
         'LCOBranch'     : self.LCOBranchInfoPattern,
         #'SuperParity'   : self.SuperParityInfoPattern,
         'SP_SuperParity': self.SP_SuperParityInfoPattern,
         'SMR'           : self.SMRInfoPattern,

#            'F3Trunk'      : 'Partition\s+PhyCyl\s+LogCyl\s+NomCyl\s+RadiusMils\s+LogHd\s+Zn\s+LogicalTrackNum\s+FirstLba\s+FirstPba\s+LogSecs\s+PhySecs\s+WdgSkw\s+SecPerFrm\s+WdgPerFrm\s*[UserSystem]+\s+(?P<PHY_CYL>[a-fA-F\d]+)\s+(?P<LOG_CYL>[a-fA-F\d]+)\s+(?P<NOM_CYL>[a-fA-F\d]+)\s+\S+\s+(?P<LOG_HEAD>[a-fA-F\d]+)\s+(?P<ZONE>[a-fA-F\d]+)\s+(?P<SPI>[a-fA-F\d]+)\s+(?P<FIRST_LBA>[a-fA-F\d]+)\s+(?P<FIRST_PBA>[a-fA-F\d]+)\s+(?P<LOG_SECS>[a-fA-F\d]+)\s+(?P<PHY_SECS>[a-fA-F\d]+)',
#            'LCOBranch'    : 'Partition\s+PhyCyl\s+LogCyl\s+NomCyl\s+RadiusMils\s+LogHd\s+Zn\s+FirstLba\s+FirstPba\s+LogSecs\s+PhySecs\s+WdgSkw\s+SecPerFrm\s+WdgPerFrm\s*[UserSystem]+\s+(?P<PHY_CYL>[a-fA-F\d]+)\s+(?P<LOG_CYL>[a-fA-F\d]+)\s+(?P<NOM_CYL>[a-fA-F\d]+)\s+\S+\s+(?P<LOG_HEAD>[a-fA-F\d]+)\s+(?P<ZONE>[a-fA-F\d]+)\s+(?P<FIRST_LBA>[a-fA-F\d]+)\s+(?P<FIRST_PBA>[a-fA-F\d]+)\s+(?P<LOG_SECS>[a-fA-F\d]+)\s+(?P<PHY_SECS>[a-fA-F\d]+)',
#            'SuperParity'  : 'Super\s+Block\s+Info:.*Partition.*FirstPba\s*[UserSystem]+\s+(?P<PHY_CYL>[a-fA-F\d]+)\s+(?P<LOG_CYL>[a-fA-F\d]+)\s+(?P<NOM_CYL>[a-fA-F\d]+)\s+\S+\s+(?P<LOG_HEAD>[a-fA-F\d]+)\s+(?P<ZONE>[a-fA-F\d]+)\s+(?P<LOG_TRACK>[a-fA-F\d]+)\s+(?P<FIRST_LBA>[a-fA-F\d]+)\s+(?P<FIRST_PBA>[a-fA-F\d]+)',
#            'SMR'          : 'BandID.*ShingDir.*Track\sInfo:.*Partition.*WdgPerFrm\s*[UserSystem]+\s+(?P<PHY_CYL>[a-fA-F\d]+)\s+(?P<LOG_CYL>[a-fA-F\d]+)\s+(?P<NOM_CYL>[a-fA-F\d]+)\s+\S+\s+(?P<LOG_HEAD>[a-fA-F\d]+)\s+(?P<ZONE>[a-fA-F\d]+)\s+(?P<LOG_TRACK>[a-fA-F\d]+)\s+(?P<FIRST_LBA>[a-fA-F\d]+)\s+(?P<FIRST_PBA>[a-fA-F\d]+)',
                          }

      sptCmds.gotoLevel('A')

      if testSwitch.FE_0188217_357260_P_AUTO_DETECT_TRACK_INFO:
         while retries >= 0:
            retries -= 1
            if mode == 'physical':
               data = sptCmds.sendDiagCmd('d%x,%x' % (Track, Head), printResult = printResult, maxRetries = 5, loopSleepTime = 0)
            elif mode == 'logical':
               data = sptCmds.sendDiagCmd('c%x,%x' % (Track, Head), printResult = printResult, maxRetries = 5, loopSleepTime = 0)
            else:
               ScrCmds.raiseException(11044, "getTrackInfo - invalid mode provided : %s" % mode)

            if testSwitch.virtualRun: # Selection of data samples for VE purposes
               # F3 Trunk:
               #data = '''Track Info: Partition PhyCyl LogCyl NomCyl RadiusMils LogHd Zn LogicalTrackNum FirstLba FirstPba LogSecs PhySecs WdgSkw SecPerFrm WdgPerFrm User 00001273 00001000 0000216B +1.749375E+3 01 01 000000004EF3 000003BC1EA5 000003BE6664 0CBE 0CC0 '''
               # LCO Branch:
               #data = '''Track Info: Partition PhyCyl LogCyl NomCyl RadiusMils LogHd Zn FirstLba FirstPba LogSecs PhySecs WdgSkw SecPerFrm WdgPerFrm User 00001000 00001000 00001105 +1.745125E+3 01 00 0000015FA0B8 0000015FA0B8 0B60 0B60 0121 0007 0001 '''
               # Super Parity:
               #data = '''Super Block Info: Track Info: Partition PhyCyl LogCyl NomCyl RadiusMils LogHd Zn LogTrackNum FirstUserLba FirstPba User 00002710 000024A9 000035E8 +1.732374E+3 00 01 000000006CE9 000004DF5341 000004E0B6AB '''
               # SMR:
               data = '''Band Info: BandID LogOffset PhyOffset StartLBA StartPBA NumLBAs NumPBAs StartCyl EndCyl ShingDir Track Info: Partition PhyCyl LogCyl NomCyl RadiusMils LogHd Zn LogicalTrack FirstLba FirstPba LogSecs PhySecs WdgSkw SecPerFrm WdgPerFrm User 00001000 00001000 00001176 +1.770937E+3 01 01 FFFFFFFFFFFF 0000002BA0DC 0000002BAD14 01DA 01DA 001C 0034 002B '''
               # SP Super Parity:
               #data = '''Super Block Info: Track Info: Partition PhyCyl   LogCyl   NomCyl   RadiusMils   LogHd Zn LogTrackNum  FirstUserLba FirstPba      User      0002DCEA 0002DB0A 0002E180 +7.039999E+2 00    12 0000063F3BE6 0000065ED1A3 4039F400000097D8   LogSecs PhySecs WdgSkw SecPerFrm WdgPerFrm  00D6    00D6    0000   0029      0031        '''
            data = data.replace("\n"," ")
            data = data.replace("\r"," ")

            for patternType in translatePatterns.keys():
               #match = re.search(translatePatterns[patternType], data)
               match = translatePatterns[patternType].search(data)
               if match:
                  if DEBUG > 0:
                     objMsg.printMsg('Data pattern match found: %s' %patternType)
                  return self.convDictItems(match.groupdict(), int, [16,])
            else:
               if retries < 0:
                  ScrCmds.raiseException(11044, "Unable to parse Track Information response: buffer = %s" % data)
               else:
                  time.sleep(5)

      else: # NOT FE_0188217_357260_P_AUTO_DETECT_TRACK_INFO
         if testSwitch.FE_0173306_475827_P_SUPPORT_TRUNK_AND_BRANCH_F3_FOR_GET_TRACK_INFO:
            trackXlatePattern_F3trunk = '\S+\s*(?P<PHY_CYL>[a-fA-F\d]+)\s+(?P<LOG_CYL>[a-fA-F\d]+)\s+(?P<NOM_CYL>[a-fA-F\d]+)\s+\S+\s+(?P<LOG_HEAD>[a-fA-F\d]+)\s+(?P<ZONE>[a-fA-F\d]+)\s+(?P<SPI>[a-fA-F\d]+)\s+(?P<FIRST_LBA>[a-fA-F\d]+)\s+(?P<FIRST_PBA>[a-fA-F\d]+)\s+(?P<LOG_SECS>[a-fA-F\d]+)\s+(?P<PHY_SECS>[a-fA-F\d]+)'
            trackXlatePattern_LCObranch =  '\S+\s*(?P<PHY_CYL>[a-fA-F\d]+)\s+(?P<LOG_CYL>[a-fA-F\d]+)\s+(?P<NOM_CYL>[a-fA-F\d]+)\s+\S+\s+(?P<LOG_HEAD>[a-fA-F\d]+)\s+(?P<ZONE>[a-fA-F\d]+)\s+(?P<FIRST_LBA>[a-fA-F\d]+)\s+(?P<FIRST_PBA>[a-fA-F\d]+)\s+(?P<LOG_SECS>[a-fA-F\d]+)\s+(?P<PHY_SECS>[a-fA-F\d]+)'
            detectTrunkBranchF3Pattern = '\s*LogicalTrackNum\s*'
         if testSwitch.FE_0171260_231166_P_F3_CODE_USES_INLINE_PARITY_TRK_OUTPUT_IN_TRK_INFO:
            trackXlatePattern = '\S+\s*(?P<PHY_CYL>[a-fA-F\d]+)\s+(?P<LOG_CYL>[a-fA-F\d]+)\s+(?P<NOM_CYL>[a-fA-F\d]+)\s+\S+\s+(?P<LOG_HEAD>[a-fA-F\d]+)\s+(?P<ZONE>[a-fA-F\d]+)\s+(?P<SPI>[a-fA-F\d]+)\s+(?P<FIRST_LBA>[a-fA-F\d]+)\s+(?P<FIRST_PBA>[a-fA-F\d]+)\s+(?P<LOG_SECS>[a-fA-F\d]+)\s+(?P<PHY_SECS>[a-fA-F\d]+)'
         else:
            trackXlatePattern = '\S+\s*(?P<PHY_CYL>[a-fA-F\d]+)\s+(?P<LOG_CYL>[a-fA-F\d]+)\s+(?P<NOM_CYL>[a-fA-F\d]+)\s+\S+\s+(?P<LOG_HEAD>[a-fA-F\d]+)\s+(?P<ZONE>[a-fA-F\d]+)\s+(?P<FIRST_LBA>[a-fA-F\d]+)\s+(?P<FIRST_PBA>[a-fA-F\d]+)\s+(?P<LOG_SECS>[a-fA-F\d]+)\s+(?P<PHY_SECS>[a-fA-F\d]+)'

         if not testSwitch.virtualRun:
            if mode == 'physical':
               data = sptCmds.sendDiagCmd('d%x,%x' % (Track, Head), printResult = printResult, maxRetries = 5)
            elif mode == 'logical':
               data = sptCmds.sendDiagCmd('c%x,%x' % (Track, Head), printResult = printResult, maxRetries = 5)
            else:
               ScrCmds.raiseException(11044, "getTrackInfo - invalid mode provided : %s" % mode)
         else:
            if testSwitch.FE_0171260_231166_P_F3_CODE_USES_INLINE_PARITY_TRK_OUTPUT_IN_TRK_INFO:
               data = """
                     Partition PhyCyl   LogCyl   NomCyl   RadiusMils   LogHd Zn FirstLba     FirstPba     LogSecs PhySecs WdgSkw SecPerFrm WdgPerFrm
                     User      00001000 00001000 00002530 +1.746249E+3 00    01 FFFFFFFFFFFFFFFF 0000026FAB51 0000026FD190 0D34    0D34    00F6   0041      0008
                     """
            else:
               data = """
                     Partition PhyCyl   LogCyl   NomCyl   RadiusMils   LogHd Zn FirstLba FirstPba LogSecs PhySecs WdgSkw SecPerFrm WdgPerFrm
                     User      00012226 00012000 00012226 +7.930000E+2 00    0A 1A8551BB 1A85E50D 04B9    04B9    00D0   001B      0005
                     """
         data = data.replace("\n","")
         if testSwitch.FE_0173306_475827_P_SUPPORT_TRUNK_AND_BRANCH_F3_FOR_GET_TRACK_INFO:
            detectTrunkF3 = re.search(detectTrunkBranchF3Pattern, data)
            if detectTrunkF3:
               trackXlatePattern = trackXlatePattern_F3trunk
            else:
               trackXlatePattern = trackXlatePattern_LCObranch

         match = re.search(trackXlatePattern, data)
         if match:
            tempDict = match.groupdict()
            return self.convDictItems(tempDict, int, [16,])
         else:
            ScrCmds.raiseException(11044, "Unable to parse Track Information response: \npattern = %s\nbuffer = %s" % (trackXlatePattern, data))

   def getBandInfo(self, Track, head, printResult = False, mode = 'logical', retries = 5):
      '''
      Use level A 'c' command to retrieve Band information
      '''
      if DEBUG > 0:
         printResult = True

      while retries >= 0:
         retries -= 1
         self.gotoLevel('A')
         if mode == 'logical':
            result = sptCmds.sendDiagCmd('c%X,%X' %(Track, head ), printResult = printResult, maxRetries = 5, loopSleepTime = 0)
         elif mode == 'physical':
            result = sptCmds.sendDiagCmd('d%X,%X' %(Track, head ), printResult = printResult, maxRetries = 5, loopSleepTime = 0)
         elif mode == 'lba' and testSwitch.FE_0194980_357260_P_LIMIT_SMR_TRACK_CLEANUP_TO_VALID_BANDS:
            result = sptCmds.sendDiagCmd('F%X,%X'%(Track>>16, Track&0xFFFF), printResult = printResult, maxRetries = 5, loopSleepTime = 0)
         else:
            ScrCmds.raiseException(11044, "getBandInfo - invalid mode requested : %s" % mode)

         if testSwitch.virtualRun:
            result = '''Band Info: BandID   LogOffset PhyOffset StartLBA     StartPBA     NumLBAs  NumPBAs  StartCyl EndCyl   ShingDir 0001ACB9 00000218  00000218  00000C3F2B3F 00000C3FA265 0000053C 0000053C 00044242 0004423E ID->OD  '''

         result = result.replace("\n"," ")
         result = result.replace("\r"," ")
         match = self.BandInfoPattern.search(result)
         if match:
            return self.convDictItems(match.groupdict(), int, [16,], raiseExceptionOnValueErr = False)
         else:
            if retries < 0:
               ScrCmds.raiseException(11044, 'Unable to translate logical track to band ID, Track: %s, Head: %s' %(Track, head ))  # Should never happen
            else:
               time.sleep(5)

   def getSingleZoneInfo(self, zone, head, partition = 'User', printResult = False):
      '''
      Use level 2 'x' command to retrieve Zone information
      '''
      if DEBUG > 0:
         printResult = True

      partitionDict = { 'User' : '00', 'System' : '01'}
      try:
         partionParm = partitionDict[partition]
      except:
         ScrCmds.raiseException(11044, 'Invalid Partition Requested')  # Should never happen

      self.gotoLevel('2')
      result = sptCmds.sendDiagCmd('x%s,%X,%X,2' %(partionParm, head, zone), timeout = 300, printResult = printResult, maxRetries = 5, loopSleepTime = 0)
      if testSwitch.virtualRun:
         result = '''User Partition LBAs 000000000000-00000EA19D7A PBAs 000000000000-00000EBAD1E0 HdSkew 006E, CylSkew 0019 ZonesPerHd 1E Head 0, PhyCyls 000000-057FE7, LogCyls 000000-057DA8 Physical Logical Sec Sym Sym Data Zn Cylinders Cylinders Track Wedge Track Rate 12 036553-038D9D 036313-038B5D 013A  09B5  000F2B40 1491.562 NumMediaCacheZones 00 Media Cache Partition '''
      result = result.replace("\n"," ")
      result = result.replace("\r"," ")

      match = self.SMRZoneInfoPattern.search(result)
      if match:
         return self.convDictItems(match.groupdict(), int, [16,], raiseExceptionOnValueErr = False)
      else:
         ScrCmds.raiseException(11044, 'Unable to retrieve zone info for zone %s, head %s' % ( zone, head ))  # Should never happen


   def getValidBand(self, zone, head, mode = 'first', printResult = False):
      '''
      Finds the first or last valid BandID within the specified zone / head
      '''
      if DEBUG > 0:
         printResult = True

      zoneInfo = self.getSingleZoneInfo(zone, head, partition = 'User', printResult = printResult)
      modeDict = {'first' : 'LOG_START', 'last' : 'LOG_END'}
      track = zoneInfo[modeDict[mode]]
      return self.getBandInfo(track, head, printResult = printResult)['BandID']

   #======================================================================================================================================
   def getBANDRange(self, printResult = False):
      UsrBandPattern = '\S+\s+User\s+Band\s+Mode\s+Bands\s(?P<START_BAND>[a-fA-F\d]+)\s-\s(?P<END_BAND>[a-fA-F\d]+)'
      MCZonePattern = 'User\sPartition.*?\s+ZonesPerHd\s(?P<ZN_PER_HD>[a-fA-F\d]+).*?\s+.*?\s+NumMediaCacheZones\s+(?P<NUM_MCZ>[a-fA-F\d]+)'

      sptCmds.gotoLevel('A')

      if not testSwitch.virtualRun:
         data = sptCmds.sendDiagCmd('AD', printResult = printResult)
      else:
         data = """
               AD Current Addr Mode User LLL CHS Mode, Seq In   Hd 0 Cyls 000000 - 04BB92   Hd 1 Cyls 000000 - 04C9D3  All Addr Modes User LBA Mode   LBAs 000000000000 - 00000A4766E2 System LBA Mode   LBAs 000000000000 - 00000002AF7F User LLL CHS and User LLP CHW Modes   Hd 0 Cyls 000000 - 04BB92   Hd 1 Cyls 000000 - 04C9D3 System LLL CHS and System LLP CHW Modes   Hd 0 Cyls 000000 - 000237   Hd 1 Cyls 000000 - 000237 PLP CHS and PLP CHW Modes   Hd 0 Cyls 000000 - 04BE02   Hd 1 Cyls 000000 - 04CC43 User Band Mode   Bands 00000000 - 00007361  Buffer Sector Offset 8023E9E1
               """
      #Finding last logical BAND ID...............
      data = data.replace("\n"," ")
      match = re.search(UsrBandPattern, data)
      if match:
         tempDict = match.groupdict()
         tempDict = self.convDictItems(tempDict, int, [16,])
         objMsg.printMsg("\nMAX_BAND = %s" % tempDict['END_BAND'])
         LastLogBandID = tempDict['END_BAND']

      #Finding First logical BAND ID..............
      self.gotoLevel('2')
      data1 = sptCmds.sendDiagCmd('x0,0,0,2', timeout = 300, printResult = printResult, maxRetries = 5, loopSleepTime = 0)
      data1 = data1.replace("\n"," ")
      match1 = re.search(MCZonePattern, data1)
      if match1:
         tempDict1 = match1.groupdict()
         tempDict1 = self.convDictItems(tempDict1, int, [16,])
         NumZnPerHead = tempDict1['ZN_PER_HD']
         NumMCZnPerHead = tempDict1['NUM_MCZ']
         objMsg.printMsg("NumOfLogicalZnHd = %d NumofMCZnHd = %d" % (NumZnPerHead,NumMCZnPerHead))
      else:
         NumMCZnPerHead = 2
         NumZnPerHead = 60+NumMCZnPerHead

      LastMCZnInfo = self.getSingleZoneInfo(NumMCZnPerHead, 0, 'User', printResult = printResult)
      LogCyl_4_FirstLogBand = LastMCZnInfo['LOG_START']
      FirstLogBandID = self.getBandInfo(LogCyl_4_FirstLogBand, 0, printResult = printResult)['BandID']
      objMsg.printMsg("\nMIN_BAND = %s" % FirstLogBandID)

      if match and match1:
         return FirstLogBandID, LastLogBandID, (NumZnPerHead-NumMCZnPerHead)
      else:
         objMsg.printMsg("\nLastBandID SearchPattern = %s\n buffer1 = %s" % (UsrBandPattern, data))
         objMsg.printMsg("\nMC SearchPattern = %s\n buffer1 = %s" % (MCZonePattern, data1))
         ScrCmds.raiseException(11044, "Unable to parse BAND information: \npattern = %s\nbuffer = %s" % (UsrBandPattern, data))

   def getHeadBERData(self, printResult = False):
      HeadTablePat = "^Hd\s*(?P<HD_PHYS_PSN>\d+)\s*(?P<RBIT>[\d\.]+)\s*(?P<HARD>[\d\.]+)\s*(?P<SOFT>[\d\.]+)\s*(?P<OTF>[\d\.]+)\s*(?P<RRAW>[\d\.]+)\s*(?P<RSYM>[\d\.]+)?\s+(?P<SYM>[\d.]+)?\s+(?P<WBIT>[\d.]+)\s+(?P<WHRD>[\d\.]+)\s+(?P<WRTY>[\d\.]+)"
      headComp = re.compile(HeadTablePat)

      accumulator = self.PChar('`')
      data = sptCmds.promptRead(5, 0, accumulator= accumulator)
      if printResult:
         objMsg.printMsg("BER Data collected:\n%s" % data)

      headData = []
      for line in data.splitlines():
         match = headComp.search(line)

         if match:
            headData.append(self.convDictItems(match.groupdict(), float, raiseExceptionOnNoneVal = False))

      return headData


   def convDictItems(self, inDict, dataTypeFunction, dataTypeFunctionArgs = [], raiseExceptionOnNoneVal = True, raiseExceptionOnValueErr = True):
      '''
      Convert 'group' object (from Regex search) into dictionary
       - raiseExceptionOnNoneVal = False allows 'None' values to be ignored - that entry is removed
       - raiseExceptionOnValueErr = False allows values non matching dataType to be ignored - that value remains as is (string)
      '''
      inDict = dict(inDict)
      badKeys = []
      for key, val in inDict.items():
         if not val == None:
            if len(dataTypeFunctionArgs) > 0:
               try:
                  inDict[key] = dataTypeFunction(val,*dataTypeFunctionArgs)
               except ValueError:
                  if raiseExceptionOnValueErr:
                     raise
            else:
               inDict[key] = dataTypeFunction(val)
         else:
            if raiseExceptionOnNoneVal:
               ScrCmds.raiseException(11044, 'None value found in %s' % (inDict,))
            else:
               badKeys.append(key)

      for key in badKeys:
         del inDict[key]

      return inDict

   #======================================================================================================================================
   def getZoneBERData(self, maxRetries = 3, allowZeroRBIT = False, tLevel = None, readRetry = None, lowerBaudRate = False, spc_id = 1, printResult = True, retryPause = None):

      retry = 0
      data = ""
      #Compile the zone parsing mask.. the colums aren't auto-detecting so the order must be maintained.

      if testSwitch.BF_0169360_231166_P_ALLOW_CHAR_ROBUST_BER_BY_ZONE:
         zoneTablePat = "^\s*(?P<HD_PHYS_PSN>\d{1,2}?)\s*(?P<DATA_ZONE>[0-9ABCDEF]{1,2}?)\s*(?P<RBIT>[\d\.]{3,4}?)\s*(?P<HARD>[\d\.]{3,4}?)\s*(?P<SOFT>[\d\.]{3,4}?)\s*(?P<OTF>[\d\.]{3,4}?)\s*(?P<RRAW>[\d\.]{3,4}?)\s*(?P<WBIT>[\d\.]{3,4}?)\s*(?P<WHRD>[\d\.]{3,4}?)\s*(?P<WRTY>[\d\.]{3,4}?)"
         zoneTablePat_sym = "^\s*(?P<HD_PHYS_PSN>\d{1,2}?)\s*(?P<DATA_ZONE>[0-9ABCDEF]{1,2}?)\s*(?P<RBIT>[\d\.]{3,4}?)\s*(?P<HARD>[\d\.]{3,4}?)\s*(?P<SOFT>[\d\.]{3,4}?)\s*(?P<OTF>[\d\.]{3,4}?)\s*(?P<RRAW>[\d\.]{3,4}?)\s*(?P<RSYM>[\d\.]{3,4}?)?\s*(?P<SYM>[\d\.]{3,4}?)?\s*(?P<WBIT>[\d\.]{3,4}?)\s*(?P<WHRD>[\d\.]{3,4}?)\s*(?P<WRTY>[\d\.]{3,4}?)"
      else:
         zoneTablePat = "^\s*(?P<HD_PHYS_PSN>\d+)\s*(?P<DATA_ZONE>[0-9ABCDEF]+)\s*(?P<RBIT>[\d\.]+)\s*(?P<HARD>[\d\.]+)\s*(?P<SOFT>[\d\.]+)\s*(?P<OTF>[\d\.]+)\s*(?P<RRAW>[\d\.]+)\s*(?P<WBIT>[\d\.]+)\s*(?P<WHRD>[\d\.]+)\s*(?P<WRTY>[\d\.]+)"
         zoneTablePat_sym = "^\s*(?P<HD_PHYS_PSN>\d+)\s*(?P<DATA_ZONE>[0-9ABCDEF]+)\s*(?P<RBIT>[\d\.]+)\s*(?P<HARD>[\d\.]+)\s*(?P<SOFT>[\d\.]+)\s*(?P<OTF>[\d\.]+)\s*(?P<RRAW>[\d\.]+)\s*(?P<RSYM>[\d\.]+)?\s*(?P<SYM>[\d\.]+)?\s*(?P<WBIT>[\d\.]+)\s*(?P<WHRD>[\d\.]+)\s*(?P<WRTY>[\d\.]+)"
      zoneComp = re.compile(zoneTablePat)
      zoneComp_sym = re.compile(zoneTablePat_sym)

      objMsg.printMsg("Collecting Zone BER Data", objMsg.CMessLvl.VERBOSEDEBUG)

      if testSwitch.virtualRun:
         if testSwitch.FE_0168360_470833_P_REDUCE_ZONE_BER_DATA_OUTPUT:
            objMsg.printMsg("SPC_ID: %s"%spc_id)
            objMsg.printDblogBin(objdblTable = self.dut.dblData.Tables('P_FORMAT_ZONE_ERROR_RATE'), parseSpcId = [spc_id])
         return

      while retry < maxRetries:
         try:
            self.flush()
            # Determine drive heads & zones using getZoneInfo
            self.getZoneInfo(printResult=True)
            drvHeads = self.dut.imaxHead
            drvZones = self.dut.numZones + self.NumMCZone

            #Send ber by zone command
            if self.dut.nextOper == "FNC2" and objRimType.IsLowCostSerialRiser():
               #Send ber by zone command
               objMsg.printMsg("Increase timeout from 20 to 600 on SP_HDSTR")
               data = sptCmds.execOnlineCmd('$',timeout=600, waitLoops = 100)
            else:
               data = sptCmds.execOnlineCmd('$',timeout=20, waitLoops = 100)
            zoneData = []
            dictAvgOTF = {}
            dictAvgRaw = {}
            if "Rsym" in data:
               zc = zoneComp_sym
            else:
               zc = zoneComp

            for line in data.splitlines():

               match = zc.search(line)
               if match:
                  zoneData.append(match.groupdict())
               elif line.strip().upper().startswith('SMRY:'):   # get OTF summary data per head
                  dictAvgOTF[zoneData[len(zoneData)-1]['HD_PHYS_PSN']] = line.split()[4]
                  dictAvgRaw[zoneData[len(zoneData)-1]['HD_PHYS_PSN']] = line.split()[5]
                  self.BERInfo['OTF']={'Avg':dictAvgOTF}
                  self.BERInfo['RRAW']={'Avg':dictAvgRaw}

            if len(zoneData) != (drvHeads * drvZones):
               objMsg.printMsg("\nFailure Debug Dump parsed lines (%d) doesn't match head*zones(%d*%d):\n%s" % (len(zoneData), drvHeads, drvZones, data))
               ScrCmds.raiseException(10566,"Failed to retreive ber by zone data.")
            else:
               break

         except:
            objMsg.printMsg("Traceback %s" % traceback.format_exc())
            retry += 1
            objMsg.printMsg("Serial data losss detected.")
            if lowerBaudRate==True:
               self.syncBaudRate(Baud38400)        #Lower down baud rate to 38.4K
            if retryPause:
               time.sleep(retryPause)

      else:
         ScrCmds.raiseException(10566,"Failed to retreive ber by zone data on all %s attempts." % maxRetries)

      #Once we have all data let's add it to the dblog object
      ######################## DBLOG Implementaion- Setup
      curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
      ########################
      beval = Utility.CUtility.beval
      for zoneRec in zoneData:
         if float(zoneRec['RBIT']) > 0 or allowZeroRBIT:
            self.dut.dblData.Tables('P_FORMAT_ZONE_ERROR_RATE').addRecord(
               {
               'SPC_ID' : spc_id,
               'OCCURRENCE' : occurrence,
               'SEQ' : curSeq,
               'TEST_SEQ_EVENT' : testSeqEvent,
               'HD_PHYS_PSN' : self.dut.LgcToPhysHdMap[int(zoneRec['HD_PHYS_PSN'])],
               'HD_LGC_PSN' : zoneRec['HD_PHYS_PSN'],
               'DATA_ZONE' : int(zoneRec['DATA_ZONE'], 16),
               'ECC_LEVEL' : beval(tLevel==None, '',tLevel),
               'NUM_READ_RETRIES' : beval(readRetry==None,'',readRetry),
               'BITS_READ_LOG10' : zoneRec['RBIT'],
               'HARD_ERROR_RATE' : zoneRec['HARD'],
               'SOFT_ERROR_RATE' : zoneRec['SOFT'],
               'OTF_ERROR_RATE' : zoneRec['OTF'],
               'RAW_ERROR_RATE' : zoneRec['RRAW'],
               'BITS_WRITTEN_LOG10' : zoneRec['WBIT'],
               'BITS_UNWRITEABLE_LOG10' : zoneRec['WHRD'],
               'BITS_WITH_WRT_RETRY_LOG10' : zoneRec['WRTY'],
               'SYMBOLS_READ_LOG10' : zoneRec.get('RSYM',''), #Null-able
               'SYMBOL_ERROR_RATE' : zoneRec.get('SYM', ''), #Null-able
               })
         else:
            if printResult:
               objMsg.printMsg("RBIT 0.. row= %s" % zoneRec)

      if testSwitch.FE_0168360_470833_P_REDUCE_ZONE_BER_DATA_OUTPUT:
         objMsg.printMsg("SPC_ID: %s"%spc_id)
         objMsg.printDblogBin(objdblTable = self.dut.dblData.Tables('P_FORMAT_ZONE_ERROR_RATE'), parseSpcId = [spc_id])
      else:
         objMsg.printDblogBin(self.dut.dblData.Tables('P_FORMAT_ZONE_ERROR_RATE'))

      if (retry > 0) and (lowerBaudRate == True):   # Change back baud rate by doing power cycle
         objMsg.printMsg("Recovering baud rate using power cycle.")
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
         sptCmds.enableDiags()

      return zoneData

   def getBERDataByZone(self, allowZeroRBIT = False, tLevel = None, readRetry = None, lowerBaudRate = True, recoverBaudPwrCycle = False, returnLevel = 'T', spc_id = 1, printResult = False):
      """
      Possible data formats returned by drive:
      Hd Zn  Rbit  Hard  Soft  OTF   Raw   Sym   Wbit  Whrd  Wrty
      Hd Zn  Rbit  Hard  Soft  OTF   Raw   Rsym  Sym   Wbit  Whrd  Wrty
      Hd Zn  Rbit  Hard  Soft  OTF   BER   Wbit  Whrd  Wrty  CWds  Bits BadB itrs  LLR  syn  era  non
      """
      if lowerBaudRate:
         self.syncBaudRate(Baud38400)        #Lower down baud rate to 38.4K
      #startLevel = self.currLevel # self.currLevel doesn't seem to indicate current level.
      #if startLevel != '2':
      self.gotoLevel('2')
      if testSwitch.BF_0166446_231166_P_FIX_ZONE_BER_PARSING_FOR_LARGE_ERROR:
         zoneTablePatterns = {
         "base" : (
            "[ \t]*(?P<HD_PHYS_PSN>[\da-fA-F]{1})[ \t]+"
            "(?P<DATA_ZONE>[\da-fA-F]{1,2})[ \t]+"
            "(?P<RBIT>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<HARD>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<SOFT>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<OTF>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<RRAW>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<WBIT>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<WHRD>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<WRTY>[\d]{1,2}\.[\d]{1})"),
         "Rsym" : ( # this is for when when Rsym and Sym columns are present.
            "[ \t]*(?P<HD_PHYS_PSN>[\da-fA-F]{1})[ \t]+"
            "(?P<DATA_ZONE>[\da-fA-F]{1,2})[ \t]+"
            "(?P<RBIT>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<HARD>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<SOFT>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<OTF>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<RRAW>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<RSYM>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<SYM>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<WBIT>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<WHRD>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<WRTY>[\d]{1,2}\.[\d]{1})"),
         "itr" : ( # this is for when CWds, Bits, BadB, itrs, LLR, syn, era, and non, are present
            "[ \t]*(?P<HD_PHYS_PSN>[\da-fA-F]{1})[ \t]+"
            "(?P<DATA_ZONE>[\da-fA-F]{1,2})[ \t]+"
            "(?P<RBIT>[\d]+\.[\d]{1})[ \t]+"
            "(?P<HARD>[\d]+\.[\d]{1})[ \t]+"
            "(?P<SOFT>[\d]+\.[\d]{1})[ \t]+"
            "(?P<OTF>[\d]+\.[\d]{1})[ \t]+"
            "(?P<RRAW>[\d]+\.[\d]{1})[ \t]+"
            "(?P<WBIT>[\d]+\.[\d]{1})[ \t]+"
            "(?P<WHRD>[\d]+\.[\d]{1})[ \t]+"
            "(?P<WRTY>[\d]+\.[\d]{1})[ \t]+"
            "(?P<CWds>[\d]+\.[\d]{1})[ \t]+"
            "(?P<Bits>[\d]+\.[\d]{1})[ \t]+"
            "(?P<BadB>[\d]+\.[\d]{1})[ \t]+"
            "(?P<itrs>[\d]+\.[\d]{1})[ \t]+"
            "(?P<LLR>[\d]+\.[\d]+)[ \t]+"
            "(?P<syn>[\d]+\.[\d]{1})[ \t]+"
            "(?P<era>[\d]+\.[\d]{1})[ \t]+"
            "(?P<non>[\d]+\.[\d]{1})"
            "[ \t]?(?P<extra>[\d]+\.[\d]+)?"),
         }
      else:
         zoneTablePatterns = {
         "base" : (
            "[ \t]*(?P<HD_PHYS_PSN>[\da-fA-F]{1})[ \t]+"
            "(?P<DATA_ZONE>[\da-fA-F]{1,2})[ \t]+"
            "(?P<RBIT>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<HARD>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<SOFT>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<OTF>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<RRAW>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<WBIT>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<WHRD>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<WRTY>[\d]{1,2}\.[\d]{1})"),
         "Rsym" : ( # this is for when when Rsym and Sym columns are present.
            "[ \t]*(?P<HD_PHYS_PSN>[\da-fA-F]{1})[ \t]+"
            "(?P<DATA_ZONE>[\da-fA-F]{1,2})[ \t]+"
            "(?P<RBIT>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<HARD>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<SOFT>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<OTF>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<RRAW>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<RSYM>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<SYM>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<WBIT>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<WHRD>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<WRTY>[\d]{1,2}\.[\d]{1})"),
         "itr" : ( # this is for when CWds, Bits, BadB, itrs, LLR, syn, era, and non, are present
            "[ \t]*(?P<HD_PHYS_PSN>[\da-fA-F]{1})[ \t]+"
            "(?P<DATA_ZONE>[\da-fA-F]{1,2})[ \t]+"
            "(?P<RBIT>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<HARD>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<SOFT>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<OTF>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<RRAW>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<WBIT>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<WHRD>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<WRTY>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<CWds>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<Bits>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<BadB>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<itrs>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<LLR>[\d]+\.[\d]+)[ \t]+"
            "(?P<syn>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<era>[\d]{1,2}\.[\d]{1})[ \t]+"
            "(?P<non>[\d]{1,2}\.[\d]{1})"
            "[ \t]?(?P<extra>[\d]+\.[\d]+)?"),
         }
      if testSwitch.virtualRun:
         initialData = []
         if not testSwitch.BF_0157187_231166_P_FIX_BER_DATA_ZONE_PARSE_RETURN:
            for head in xrange(self.dut.imaxHead):
               initialData.append("Hd Zn  Rbit  Hard  Soft  OTF   Raw   Rsym  Sym   Wbit  Whrd  Wrty\n")
               initialData.extend([" %1X %2X 10.8  10.8  10.8  10.8   5.4   9.9   4.5   0.0   0.0   0.0\n" % (head, zone) for zone in xrange(self.dut.numZones)])
               initialData.append("Smry:  0.0   0.0   0.0   0.0   0.0   0.0   0.0   0.0   0.0   0.0\n\n")
            initialData = "".join(initialData)
         else:
            initialData = """
b



Hd Zn Rbit Hard Soft  OTF  BER Wbit Whrd Wrty CWds Bits BadB itrs  LLR  syn  era  non

 0  0  7.5  7.5  7.5  7.5  3.0  7.5  7.5  7.5  3.6  7.3  3.0  3.7 429496727.8  3.0  1.5  3.6 429496728.9

 0  1  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0

 0  2  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0

 0  3  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0

 0  4  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0

 0  5  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0

 0  6  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0

 0  7  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0

 0  8  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0

 0  9  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0

 0  A  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0

 0  B  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0

 0  C  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0

 0  D  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0

 0  E  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0

 0  F  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0

 0 10  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0

 0 11  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0

 0 12  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0

 0 13  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0

 0 14  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0

 0 15  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0

 0 16  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0

 0 17  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0

 0 18  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0

 0 19  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0

 0 1A  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0

 0 1B  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0

 0 1C  7.2  7.2  7.2  7.2  2.7  7.2  7.2  7.2  3.3  7.0  2.7  3.7 429496727.4  2.7  1.5  3.3 429496728.6

 0 1D  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0

Smry:  7.7  7.7  7.7  7.7  2.9  7.7  7.7  7.7  3.8  7.5  2.9  3.7 429496727.7  3.2  1.6  3.8 429496728.8

F3 2>"""
      else:
         initialData = sptCmds.sendDiagCmd("b", printResult = True, loopSleepTime = 0)

      if "itrs" in initialData:
         if testSwitch.BF_0157187_231166_P_FIX_BER_DATA_ZONE_PARSE_RETURN:
            rePat = re.compile(zoneTablePatterns['itr'])
         else:
            rePat = re.compile(zoneTablePatterns['itrs'])
      elif "Rsym" in initialData:
         rePat = re.compile(zoneTablePatterns['Rsym'])
      else:
         rePat = re.compile(zoneTablePatterns['base'])

      rowsFound = rePat.finditer(initialData)
      zoneData = {}

      if testSwitch.BF_0164283_007955_FIX_ZONEDATA_DICT_STRUCT:
         for i in xrange(self.dut.imaxHead):
            zoneData[i] = {}

         try:
            for row in rowsFound:
               data = row.groupdict()
               curHead = int(data["HD_PHYS_PSN"],16)
               curZone = int(data["DATA_ZONE"],16)
               zoneData[curHead][curZone] = data
         except: # Could be value or key error or about 10 others... really any error here and we want to force trigger every zone measure
            if not testSwitch.BF_0168507_231166_P_ROBUST_CHANGE_TO_BER_BY_ZONE_PARSE:
               raise
      else:
         map(zoneData.setdefault, range(0, self.dut.imaxHead), [{},] * self.dut.imaxHead)
         for row in rowsFound:
            zoneData[int(row.group("HD_PHYS_PSN"),16)].update({int(row.group("DATA_ZONE"),16) : row.groupdict()})

      if sum([len(headData) for head, headData in  zoneData.items()]) < self.dut.imaxHead * self.dut.numZones:
         # we missed some data, we need to fill in the holes.
         missingHdZn = {} # {{hd,[zn,zn...]), ....}
         headList = range(self.dut.imaxHead)
         zonelist = range(self.dut.numZones)
         for head, headInfo in zoneData.iteritems():
            missingHdZn[head] = set(zonelist) - set(headInfo.keys())
         for head , zonelist in missingHdZn.iteritems():
            for zone in  zonelist:
               data = sptCmds.sendDiagCmd("b%X,%X" % (head, zone), printResult = True, loopSleepTime = 2)
               match = rePat.search(data)
               if match:
                  zoneData[head].update({int(match.group("DATA_ZONE"),16) : match.groupdict()})
      if (sum([len(headData) for head, headData in  zoneData.items()]) < self.dut.imaxHead * self.dut.numZones) and not testSwitch.virtualRun:
         ScrCmds.raiseException(10566, "Failed to retreive ber by zone data.")

      curSeq, occurrence, testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
      beval = Utility.CUtility.beval
      for head in zoneData.keys():
         for zone, zoneRec in zoneData[head].items():
            if float(zoneRec['RBIT']) > 0 or allowZeroRBIT:
               self.dut.dblData.Tables('P_FORMAT_ZONE_ERROR_RATE').addRecord(
               {
                  'SPC_ID'                      : spc_id,
                  'OCCURRENCE'                  : occurrence,
                  'SEQ'                         : curSeq,
                  'TEST_SEQ_EVENT'              : testSeqEvent,
                  'HD_PHYS_PSN'                 : zoneRec['HD_PHYS_PSN'],#self.dut.LgcToPhysHdMap[int(zoneRec['HD_PHYS_PSN'])],
                  'HD_LGC_PSN'                  : zoneRec['HD_PHYS_PSN'],
                  'DATA_ZONE'                   : int(zoneRec['DATA_ZONE'], 16),
                  'ECC_LEVEL'                   : beval(tLevel==None, '',tLevel),
                  'NUM_READ_RETRIES'            : beval(readRetry==None,'',readRetry),
                  'BITS_READ_LOG10'             : zoneRec['RBIT'],
                  'HARD_ERROR_RATE'             : zoneRec['HARD'],
                  'SOFT_ERROR_RATE'             : zoneRec['SOFT'],
                  'OTF_ERROR_RATE'              : zoneRec['OTF'],
                  'RAW_ERROR_RATE'              : zoneRec['RRAW'],
                  'SYMBOLS_READ_LOG10'          : zoneRec.get('RSYM',''), #Null-able
                  'SYMBOL_ERROR_RATE'           : zoneRec.get('SYM', ''), #Null-able
                  'BITS_WRITTEN_LOG10'          : zoneRec['WBIT'],
                  'BITS_UNWRITEABLE_LOG10'      : zoneRec['WHRD'],
                  'BITS_WITH_WRT_RETRY_LOG10'   : zoneRec['WRTY'],
               })
      objMsg.printDblogBin(self.dut.dblData.Tables('P_FORMAT_ZONE_ERROR_RATE'))
      if lowerBaudRate and recoverBaudPwrCycle:   # Change back baud rate by doing power cycle
         objMsg.printMsg("Recovering baud rate using power cycle.")
         objPwrCtrl.powerCycle(useESlip=1)
         sptCmds.enableDiags()
      self.gotoLevel(returnLevel)

      if testSwitch.BF_0157187_231166_P_FIX_BER_DATA_ZONE_PARSE_RETURN:
         #conform data to match the return type of getZoneBERData
         vals = []
         for head, zoneItems in zoneData.items():
            vals.extend(zoneItems.values())
         return vals
      else:
         return zoneData

   if testSwitch.FE_0126515_399481_WRCUR_TWEAK_IN_FSE_SCREEN and not testSwitch.FE_0127688_399481_RAP_AFH_PREAMP_TWEAK_IN_FSE_SCREEN:
      def getPreampParms(self, printResult = True):
         """
         get WrCur, WrDamp, WrDampDur, HtRng for each head/zone.
         Returns dict[head][zone][parm], like so:
         {0: {0: {'HtRng': 'FC', 'WrCur': '09', 'WrDamp': '02', 'WrDampDur': '05'},
              1: {'HtRng': 'FC', 'WrCur': '09', 'WrDamp': '02', 'WrDampDur': '05'},
         """
         headPattern = re.compile("[ \t]*\(P3=[\da-fA-F]{2}\) Head (?P<Head>[\da-fA-F]{2})")
         preAmpPattern = re.compile("[ \t]*\(P5=[\da-fA-F]{2}\)"
         " User Zone (?P<Zone>[\da-fA-F]{2}):"
         "[ \t]*(?P<WrCur>[\da-fA-F]{2})"
         "[ \t]*(?P<WrDamp>[\da-fA-F]{2})"
         "[ \t]*(?P<WrDampDur>[\da-fA-F]{2})"
         "[ \t]*(?P<HtRng>[\da-fA-F]{2})")
         preAmpBasePat = ("[ \t]*\(P5=%.2X\)"
         " User Zone (?P<Zone>%.2X):"
         "[ \t]*(?P<WrCur>[\da-fA-F]{2})"
         "[ \t]*(?P<WrDamp>[\da-fA-F]{2})"
         "[ \t]*(?P<WrDampDur>[\da-fA-F]{2})"
         "[ \t]*(?P<HtRng>[\da-fA-F]{2})")
         if testSwitch.virtualRun:
            initialData = []
            initialData.append("    (P3=00) Head %.2X:\n WrCur   WrDamp  WrDampDur  HtRng\n") # leaving head %X unfilled
            initialData.extend(["       (P5=%.2X) User Zone %.2X:     07      02       05        FC\n" % (zone, zone) for zone in xrange(self.dut.numZones)])
            initialData = "".join(initialData)
         self.gotoLevel('2')
         preampData = {}
         for head in range(self.dut.imaxHead):
            preampData[head] = {}
            if testSwitch.virtualRun:
               data = initialData % head
            else:
               data = sptCmds.sendDiagCmd("I,01,0A,%X"%head, printResult = printResult, loopSleepTime = 0)
            headCheck = [int(match.group("Head"), 16) for match in headPattern.finditer(data)]
            if len(headCheck) != 1 or head not in headCheck:
               # then we either have data for more than 1 head, or the wrong hd
               ScrCmds.raiseException(11044, "Unexpected Preamp Head Data: %s" % data)
            matches = preAmpPattern.finditer(data)
            for match in matches:
               newData = match.groupdict()
               zone = int(newData["Zone"],16)
               if zone in preampData[head].keys():
                  # shouldn't get zone data twice
                  ScrCmds.raiseException(11044, "Unexpected Preamp Zone Data: %s" % data)
               else:
                  newData.pop("Zone")
                  preampData[head][zone] = newData
         if sum([len(zoneData) for zoneData in  preampData.values()]) < self.dut.imaxHead * self.dut.numZones:
            # we missed some data, we need to fill in the holes.
            missingHdZn = {} # {{hd,[zn,zn...]), ....}
            headList = range(self.dut.imaxHead)
            zonelist = range(self.dut.numZones)
            for head, zoneData in preampData.iteritems():
               missingHdZn[head] = set(zonelist) - set(zoneData.keys())
            for head , zonelist in sorted(missingHdZn.iteritems()):
               for zone in  sorted(zonelist):
                  if testSwitch.virtualRun:
                     data = initialData % head
                  else:
                     data = sptCmds.sendDiagCmd("I,01,0A,%X,,%X" % (head, zone), printResult = printResult, loopSleepTime = 2)
                  headCheck = [int(match.group("Head"), 16) for match in headPattern.finditer(data)]
                  if len(headCheck) != 1 or head not in headCheck:
                     # then we either have data for more than 1 head, or the wrong hd
                     ScrCmds.raiseException(11044, "Unexpected Preamp Head Data: %s" % data)
                  newData = re.search(preAmpBasePat%(zone,zone,), data).groupdict()
                  newData.pop("Zone")
                  preampData[head][zone] = newData
                  #zoneCheck = [int(match.group("Zone"), 16) for match in headPattern.finditer(data)]
                  #if len(zoneCheck) != 1 or zone not in zoneCheck:
                  # then we either have data for more than 1 zone, or the wrong zn
                  #   ScrCmds.raiseException(11044, "Unexpected Preamp Zone Data: %s" % data)
         if sum([len(zoneData) for zoneData in  preampData.values()]) < self.dut.imaxHead * self.dut.numZones:
            ScrCmds.raiseException(11044, "Failed to retrieve preAmp data.")
         preampData = Utility.CUtility.operateOnDictVals(preampData, lambda x : int(x, 16),)
         return preampData

   if testSwitch.FE_0126515_399481_WRCUR_TWEAK_IN_FSE_SCREEN and not testSwitch.FE_0127688_399481_RAP_AFH_PREAMP_TWEAK_IN_FSE_SCREEN:
      def setPreampParms(self, preampData, printResult = False, verify = True):
         """
         set new WrCur, WrDamp, WrDampDur, HtRng for each head/zone.
         takes preampData dict[head][zone][Parm] == newVal, like so:
         {0: {0: {'WrCur': 9, 'WrDamp': 2,},
              1: {'WrCur': A',},
         """
         self.gotoLevel('7')
         parmEnum = {
            "WrCur"     : "00",
            "WrDamp"    : "01",
            "WrDampDur" : "02",
            "HtRng"     : "03",
         }
         for head in sorted(preampData.keys()):
            for zone in sorted(preampData[head]):
               for parmKey, parmVal in sorted(preampData[head][zone].items()):
                  sptCmds.sendDiagCmd("I%X,01,0A,%X,%s,%X" % (parmVal, head, parmEnum[parmKey], zone), printResult = printResult, loopSleepTime = 2)
               sptCmds.sendDiagCmd("U,10,%X,%X,1" % (head, zone,), printResult = printResult, loopSleepTime = 2)
         if verify:
            if testSwitch.virtualRun:
               checkVals = preampData
            else:
               checkVals = self.getPreampParms(printResult = printResult)
            for head in sorted(preampData.keys()):
               for zone in sorted(preampData[head]):
                  for parmKey, parmVal in sorted(preampData[head][zone].items()):
                     if checkVals[head][zone][parmKey] != parmVal:
                        objMsg.printMsg("Failure to set preAmp values detected.")
                        if printResult == False: # then force printout of vals for paper FA
                           self.getPreampParms(printResult = True)
                        ScrCmds.raiseException(11044, "Failed to set preAmp values.")

   ## overwrite previous getPreampParms and setPreampParms
   if testSwitch.FE_0127688_399481_RAP_AFH_PREAMP_TWEAK_IN_FSE_SCREEN:
      rapPats = {  # re pats for initial attemp to get all data in one shot
         "0A" : re.compile("[ \t]*\(P5=[\da-fA-F]{2}\)"
            " User Zone (?P<Zone>[\da-fA-F]{2}):"
            "[ \t]*(?P<WrCur>[\da-fA-F]{2})"
            "[ \t]*(?P<WrDamp>[\da-fA-F]{2})"
            "[ \t]*(?P<WrDampDur>[\da-fA-F]{2})"
            "[ \t]*(?P<HtRng>[\da-fA-F]{2})"),
         "0F" : re.compile("[ \t]*\(P5=[\da-fA-F]{2}\)"
            " User Zone (?P<Zone>[\da-fA-F]{2}):"
            "[ \t]*(?P<WplusHtClr>[\da-fA-F]{2})"  # actual key is W+HtClr
            "[ \t]*(?P<RHtClr>[\da-fA-F]{2})"
            "[ \t]*(?P<TargWrClr>[\da-fA-F]{2})"
            "[ \t]*(?P<TargPreClr>[\da-fA-F]{2})"
            "[ \t]*(?P<TargRdClr>[\da-fA-F]{2})"
            "[ \t]*(?P<TargMaintClr>[\da-fA-F]{2})"),
      }
      rapBasePats = {  # re pats for backup retrieval of missing data, one head/zone at a time
         "0A" : ("[ \t]*\(P5=%.2X\)"
            " User Zone (?P<Zone>%.2X):"
            "[ \t]*(?P<WrCur>[\da-fA-F]{2})"
            "[ \t]*(?P<WrDamp>[\da-fA-F]{2})"
            "[ \t]*(?P<WrDampDur>[\da-fA-F]{2})"
            "[ \t]*(?P<HtRng>[\da-fA-F]{2})"),
         "0F" : ("[ \t]*\(P5=%.2X\)"
            " User Zone (?P<Zone>%.2X):"
            "[ \t]*(?P<WplusHtClr>[\da-fA-F]{2})"  # actual key is W+HtClr
            "[ \t]*(?P<RHtClr>[\da-fA-F]{2})"
            "[ \t]*(?P<TargWrClr>[\da-fA-F]{2})"
            "[ \t]*(?P<TargPreClr>[\da-fA-F]{2})"
            "[ \t]*(?P<TargRdClr>[\da-fA-F]{2})"
            "[ \t]*(?P<TargMaintClr>[\da-fA-F]{2})"),
      }


      def getRAP_Parms(self, P2_mode, printResult = True):
         """
         P2_mode = "0A" RAP Tuned Preamp Parms
            get WrCur, WrDamp, WrDampDur, HtRng for each head/zone.
            Returns dict[head][zone][parm], like so:
            {0: {0: {'HtRng': 'FC', 'WrCur': '09', 'WrDamp': '02', 'WrDampDur': '05'},
                 1: {'HtRng': 'FC', 'WrCur': '09', 'WrDamp': '02', 'WrDampDur': '05'},
         P2_mode = "0F" RAP AFH Head/Zone Parms
            similar but WplusHtClr RHtClr TargWrClr TargPreClr TargRdClr TargMaintClr
         """
         headPattern = re.compile("[ \t]*\(P3=[\da-fA-F]{2}\) Head (?P<Head>[\da-fA-F]{2})")
         rapPat = self.rapPats[P2_mode]
         rapBasePat = self.rapBasePats[P2_mode]
         if testSwitch.virtualRun:
            veHeader = {
               "0A" : "    (P3=00) Head %.2X:\n WrCur   WrDamp  WrDampDur  HtRng\n",
               "0F" : "    (P3=00) Head %.2X:\n W+HtClr   RHtClr  TargWrClr TargPreClr TargRdClr  TargMaintClr\n"
            }
            veBody = {
               "0A" : "       (P5=%.2X) User Zone %.2X:     07      02       05        FC\n",
               "0F" : "       (P5=%.2X) User Zone %.2X:     5E       61       14       14          19         19\n",
            }
            initialData = []
            initialData.append(veHeader[P2_mode]) # leaving head %X unfilled
            initialData.extend([veBody[P2_mode] % (zone, zone) for zone in xrange(self.dut.numZones)])
            initialData = "".join(initialData)
         self.gotoLevel('2')
         preampData = {}
         for head in range(self.dut.imaxHead):
            preampData[head] = {}
            if testSwitch.virtualRun:
               data = initialData % head
            else:
               data = sptCmds.sendDiagCmd("I,01,%s,%X" % (P2_mode,head,), printResult = printResult, loopSleepTime = 0)
            #headCheck = [int(match.group("Head"), 16) for match in headPattern.finditer(data)]
            #if len(headCheck) != 1 or head not in headCheck:
            #   # then we either have data for more than 1 head, or the wrong hd
            #   ScrCmds.raiseException(11044, "Unexpected Preamp Head Data: %s" % data)
            matches = rapPat.finditer(data)
            for match in matches:
               newData = match.groupdict()
               zone = int(newData["Zone"],16)
               if zone in preampData[head].keys():
                  # shouldn't get zone data twice
                  ScrCmds.raiseException(11044, "Unexpected Preamp Zone Data: %s" % data)
               else:
                  newData.pop("Zone")
                  preampData[head][zone] = newData
         if sum([len(zoneData) for zoneData in  preampData.values()]) < self.dut.imaxHead * self.dut.numZones:
            # we missed some data, we need to fill in the holes.
            missingHdZn = {} # {{hd,[zn,zn...]), ....}
            headList = range(self.dut.imaxHead)
            zonelist = range(self.dut.numZones)
            for head, zoneData in preampData.iteritems():
               missingHdZn[head] = set(zonelist) - set(zoneData.keys())
            for head , zonelist in sorted(missingHdZn.iteritems()):
               for zone in  sorted(zonelist):
                  if testSwitch.virtualRun:
                     data = initialData % head
                  else:
                     data = sptCmds.sendDiagCmd("I,01,%s,%X,,%X" % (P2_mode, head, zone), printResult = printResult, loopSleepTime = 0)
                  #headCheck = [int(match.group("Head"), 16) for match in headPattern.finditer(data)]
                  #if len(headCheck) != 1 or head not in headCheck:
                  #   # then we either have data for more than 1 head, or the wrong hd
                  #   ScrCmds.raiseException(11044, "Unexpected Preamp Head Data: %s" % data)
                  newData = re.search(rapBasePat%(zone,zone,), data).groupdict()
                  newData.pop("Zone")
                  preampData[head][zone] = newData
                  #zoneCheck = [int(match.group("Zone"), 16) for match in headPattern.finditer(data)]
                  #if len(zoneCheck) != 1 or zone not in zoneCheck:
                  # then we either have data for more than 1 zone, or the wrong zn
                  #   ScrCmds.raiseException(11044, "Unexpected Preamp Zone Data: %s" % data)
         if sum([len(zoneData) for zoneData in  preampData.values()]) < self.dut.imaxHead * self.dut.numZones:
            ScrCmds.raiseException(11044, "Failed to retrieve preAmp data.")
         preampData = Utility.CUtility.operateOnDictVals(preampData, lambda x : int(x, 16),)
         return preampData

      ## key is the P2 mode, val is tuple of ordered P4 parms.
      ## P4 parms must vbe in same order as they appear in I,1 command
      parmsByMode = {
         "0A" : ("WrCur","WrDamp","WrDampDur","HtRng"),
         "0F" : ("WplusHtClr","RHtClr","TargWrClr","TargPreClr","TargRdClr","TargMaintClr"),
      }
      ## create P2 multimap, {'HtRng': '0A', 'RHtClr': '0F', 'TargMaintClr': '0F',} etc.
      P2_mode_lookup = {}
      map(P2_mode_lookup.update, map(lambda (a,b): dict(zip(a,[b]*len(a))), [(v,k) for k,v in parmsByMode.items()]))
      ## create P4 multimap, {'HtRng': '03', 'RHtClr': '01', 'TargMaintClr': '05',} etc.
      P4_mode_lookup = {}
      map(P4_mode_lookup.update, map(lambda v: dict([(v, "%.2X"%i) for i, v in enumerate(v)]), [v for v in parmsByMode.values()]))

      def setRAP_Parms(self, preampData, printResult = False, verify = True):
         """
         set new WrCur, WrDamp, WrDampDur, HtRng for each head/zone.
         takes preampData dict[head][zone][Parm] == newVal, like so:
         {0: {0: {'WrCur': 9, 'WrDamp': 2,},
              1: {'WrCur': A',},
         """
         P2modesTocheck = set() # set of P2 modes that will be checked, to close the loop
         self.gotoLevel('7')
         for head in sorted(preampData.keys()):
            for zone in sorted(preampData[head]):
               for parmKey, parmVal in sorted(preampData[head][zone].items()):
                  sptCmds.sendDiagCmd("I%X,01,%s,%X,%s,%X" % (parmVal, self.P2_mode_lookup[parmKey], head, self.P4_mode_lookup[parmKey], zone), printResult = printResult, loopSleepTime = 2)
                  P2modesTocheck.add(self.P2_mode_lookup[parmKey])
         sptCmds.sendDiagCmd("U,10,FF,FF,1", printResult = printResult)
         if verify:
            if testSwitch.virtualRun:
               checkVals = preampData
            else:
               checkValList = [self.getRAP_Parms(P2_mode, printResult = True) for P2_mode in P2modesTocheck]
               checkVals = Utility.CUtility.combineListOfHeadZoneDicts(checkValList, self.dut.imaxHead, self.dut.numZones)
               #checkVals = checkValList[0]
               #for d in checkValList[1:]:
               #   [[checkVals[head][zone].update(d[head][zone]) for head in xrange(self.dut.imaxHead) for zone in xrange(self.dut.numZones)]]
            for head in sorted(preampData.keys()):
               for zone in sorted(preampData[head]):
                  for parmKey, parmVal in sorted(preampData[head][zone].items()):
                     if checkVals[head][zone][parmKey] != parmVal:
                        objMsg.printMsg("Failure to set preAmp values detected.")
                        if printResult == False: # then force printout of vals for paper FA
                           self.getPreampParms(printResult = True)
                        ScrCmds.raiseException(11044, "Failed to set preAmp values.")

   ## end if testSwitch.FE_0127688_399481_RAP_AFH_PREAMP_TWEAK_IN_FSE_SCREEN:

   if testSwitch.FE_0129198_399481_BIE_THRESH_IN_ENCROACHED_WRITES or testSwitch.FE_0137804_399481_P_BIE_SERIAL_FORMAT:
      def setupBIEThresh(self, bieThresh = 35, iterLoad = 0, printResult = False):
         """
         Adapted from Prasanna's scripts.  Enable Bits In Error detection of flaws
         for diag based odd-even digital flawscan.  Memory/register locations are channel dependent.
         """
         printResult = printResult or DEBUG
         objMsg.printMsg("Setting Up Bits in Error Detector")

         memCmds = TP.setupBIEThresh_Params["memCmds"]
         regCmds = TP.setupBIEThresh_Params["regCmds"]
         bieThreshRegisters = TP.setupBIEThresh_Params["bieThreshRegisters"]
         iterLoadRegisters = TP.setupBIEThresh_Params["iterLoadRegisters"]

         if not testSwitch.BF_0139418_399481_P_NO_CTRL_Z_IN_BIE_SETUP_OR_DISABLE:
            self.enableDiags()
         self.gotoLevel('1')
         [sptCmds.sendDiagCmd("m%X,%X,%X" % cmdInfo, printResult = printResult) for cmdInfo in memCmds]   # Edit Processor Memory Word, m[AddrHi],[AddrLo],[MemValue],
         self.gotoLevel('7')
         [sptCmds.sendDiagCmd("s1,%X,%X" % cmdInfo, printResult = printResult) for cmdInfo in regCmds]    # s1 = Write Read Channel Register, ##s[OpType],[RegAddr],[RegValue]
         [sptCmds.sendDiagCmd("s1,%X,%X" % (reg, bieThresh,), printResult = printResult) for reg in bieThreshRegisters]
         [sptCmds.sendDiagCmd("s1,%X,%X" % (reg, iterLoad + 0x80,), printResult = printResult) for reg in iterLoadRegisters]

      def disableBIEDetector(self, printResult = False):
         """
         Display BIE related registers, and disable BIE detector.
         """
         printResult = printResult or DEBUG
         objMsg.printMsg("Displaying Bits in Error Detector, Disabling BIE Detector")

         regsToDisp = TP.disableBIEDetector_Params["regsToDisp"]
         memCmds = TP.disableBIEDetector_Params["memCmds"]
         regCmds = TP.disableBIEDetector_Params.get("regCmds",[])

         if not testSwitch.BF_0139418_399481_P_NO_CTRL_Z_IN_BIE_SETUP_OR_DISABLE:
            self.enableDiags()
         self.gotoLevel('7')
         [sptCmds.sendDiagCmd("t1, %X" % (reg,), printResult = True) for reg in regsToDisp]
         [sptCmds.sendDiagCmd("s1,%X,%X" % cmdInfo, printResult = printResult) for cmdInfo in regCmds]    # s1 = Write Read Channel Register, ##s[OpType],[RegAddr],[RegValue]
         self.gotoLevel('1')
         [sptCmds.sendDiagCmd("m%X,%X,%X" % cmdInfo, printResult = printResult) for cmdInfo in memCmds]
   ## end if if testSwitch.FE_0129198_399481_BIE_THRESH_IN_ENCROACHED_WRITES:


   def measureThroughPut(self, rwMode = 0, zoneNumber = None, skewSettings = None, sampleTracks = True, timeout = 60000):
      """
      Use level 2>T command to perform full pack throughput
         rwMode = 0 is read and 1 is write
         zoneNumber = Zone to perform measurement in. Default is all zones.
         skewSettings = Tuple of ([minCylSkew,minHeadSkew],[maxCylSkew,maxHeadSkew],skewStepSize)
         sampleTracks = set to false to test entire pack
      """

      objMsg.printMsg("Measuring Drive Throughput")
      zoneMask = 0

      if zoneNumber == None:
         zoneMask = 1
         zoneNumber = 0

      if SHORT_DIAG_DEBUG:
         sampleTracks = True

      if sampleTracks:
         fullPack = 0
      else:
         fullPack = 1

      options = zoneNumber | (zoneMask <<13) | (fullPack<<14) | (rwMode << 15)

      if skewSettings == None:
         skewSettings = ''
      else:
         skewSettings = ",%x,%x,%x" % skewSettings

      self.enableRWStats()

      cmd = "T%x%s" % (options, skewSettings)

      objMsg.printMsg("Sending command %s" % cmd)
      sptCmds.gotoLevel('2')
      res = sptCmds.sendDiagCmd(cmd, timeout, printResult = True)

      throughPutPattern = re.compile("Zone\s*(?P<zone>[0-9A-Fa-f]+)\s*cyl skew (?P<cyl_skew>[0-9A-Fa-f]+)\s*head skew (?P<head_skew>[0-9A-Fa-f]+)\s* throughput LBA:\s*(?P<throughput>[\d\.]+)")
      throughPutData = []
      for line in res.splitlines():
         match = throughPutPattern.search(line)
         if match:
            throughPutData.append(match.groupdict())

      rwModeMneumonic = {0:'READ',1:'WRITE'}
      ######################## DBLOG Implementaion- Setup
      curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
      ########################
      for znData in throughPutData:
         self.dut.dblData.Tables('P_THROUGHPUT_DATA').addRecord(
            {
            'SPC_ID' :           1,
            'OCCURRENCE' :       occurrence,
            'SEQ' :              curSeq,
            'TEST_SEQ_EVENT' :   testSeqEvent,
            'RW_MODE'   :        rwModeMneumonic[rwMode],
            'DATA_ZONE' :        znData['zone'],
            'CYL_SKEW'  :        znData['cyl_skew'],
            'HD_SKEW'   :        znData['head_skew'],
            'THROUGHPUT'   :     znData['throughput'],
            })
      objMsg.printDblogBin(self.dut.dblData.Tables('P_THROUGHPUT_DATA'))
      self.getZoneBERData()

   def clearDOS(self, clearDOSParams):
      """
      Use level 7>m1/m100 commands to perform DOS Display and DOS Clearing
      """
      retry = 0
      while retry < clearDOSParams['maxRetries']:

         revDict = self.getCommandVersion('7','m', printResult = True)
         if revDict['majorRev'] > 8000:
            clrDos = 'm100'
            displDos = 'm'
            objMsg.printMsg("Single Track DOS detected")
         else:
            clrDos = "m100"
            displDos = 'm'
            #displDos = 'm1,0,1000000,1'
            objMsg.printMsg("DOS detected")


         sptCmds.gotoLevel('7')

         if clearDOSParams['displayBefore']:
            try:sptCmds.sendDiagCmd(displDos,timeout = 300,printResult = True, maxRetries = 3, loopSleepTime = 0)
            except:pass

         if clearDOSParams['clearDOS']:
            data = sptCmds.sendDiagCmd(clrDos,timeout = 300,printResult = True, maxRetries = 3, loopSleepTime = 0)
            if data.find('Invalid') == -1:# and data.find('m1') != -1 :
               objMsg.printMsg("Passed DOS Table Clear: %s" % data)
               break
            else:
               objMsg.printMsg("Failed DOS Table Clear: %s" % data)
               retry += 1
         else:
            objMsg.printMsg("Clear DOS Table turned OFF - clearDOS=%s" % clearDOSParams['clearDOS'])
            break

      else:
         if not testSwitch.virtualRun:
            ScrCmds.raiseException(13457,"Failed to Clear DOS")

      if clearDOSParams['verifyAfter']:
         try:
            data = sptCmds.sendDiagCmd(displDos,timeout = 300,printResult = True, maxRetries = 3, loopSleepTime = 0)
         except:
            data = ''
         verifyDataLength = len(data)
         objMsg.printMsg("Verify DOS Table data length: %s" % verifyDataLength)
         if verifyDataLength <= clearDOSParams['clearLength']:    # check DOS clearing, check by length #data.find('m1') != -1 and
            objMsg.printMsg("Passed DOS Table Verify: %s" % data)
         else:
            objMsg.printMsg("Failed DOS Table Verify: %s" % data)
            if not testSwitch.virtualRun:
               ScrCmds.raiseException(13457,"Failed to Verify - Clear DOS")
      else:
         objMsg.printMsg("Display/Verify DOS Table Clear turned OFF - verifyAfter=%s" % clearDOSParams['verifyAfter'])

   def resetAMPs(self):
      objMsg.printMsg("Reset AMPS to default")
      self.changeAMPS()

   def SetAppleTempTransmissionInAMPS(self, enable = True):
      self.changeAMPS("ENABLE_TEMPERATURE_TRANSMISSION", int(enable), mask = 1)

   def changeAMPS(self,AMPSName = "", Value = 0, mask = 0xFFFF):
      def raiseExc():
         ScrCmds.raiseException(14002, "AMPS set command of %s to %x failed" % (AMPSName, Value))

      objMsg.printMsg("Setting AMPS %s to %x" % (AMPSName, Value))
      sptCmds.gotoLevel('T')
      if AMPSName == "":
         acc = self.PBlock("F,,22")
      else:
         acc = self.PBlock('F"%s",%x' % (AMPSName, Value))
      result = sptCmds.promptRead(30,1,accumulator=acc, loopSleepTime = 0)
      del acc
      result = sptCmds.sendDiagCmd('F"%s"' % AMPSName,timeout = 1000, loopSleepTime = 0)
      match = re.search("%s\s*=\s*(?P<val>[\da-fA-F]+)" % AMPSName, result)
      if testSwitch.virtualRun or AMPSName == "":
         return

      if match:
         retDict = match.groupdict()
         if not (int(retDict['val'], 16) & mask) == Value:
            objMsg.printMsg("ErrorDump: \n%s" % result)
            raiseExc()
      else:
         objMsg.printMsg("ErrorDump: \n%s" % result)
         raiseExc()



   def particleSweep(self, sweepOptions = {}):
      """
      Particle sweep algorithm using the Level 2 J command.  This algorithm will sweep from the MD to the OD
      and from the MD to the ID using the dwell time and duration specified in the input test
      parameters.
      """
      # Go to level 2
      sptCmds.gotoLevel('2')

      # Get the max cylinder from the drive
      if not testSwitch.virtualRun:
         numCyls,zones = self.getZoneInfo()
         if DEBUG > 0:
            objMsg.printMsg("numCyls is %s" % numCyls)
         maxCyl = numCyls[0] # We want head 0 max logical cyl, which will be the first match returned
      else:
         maxCyl = 100000  # Dummy value for VE

      minCyl = 0
      mdCyl = (maxCyl - minCyl) / 2

      # Format the inputs appropriately to send into the diag. system
      maxCyl = hex(maxCyl).replace('0x','')
      minCyl = hex(minCyl).replace('0x','')
      mdCyl = hex(mdCyl).replace('0x','')
      duration = hex(sweepOptions['duration']).replace('0x','')
      dwell = hex(sweepOptions['dwell']).replace('0x','')

      baseCmd = 'J' + mdCyl
      swpToID = ','.join((baseCmd, maxCyl, duration, dwell))
      swpToOD = ','.join((baseCmd, minCyl, duration, dwell))
      if DEBUG > 0:
         objMsg.printMsg(" commnd: %s" % swpToID)
         objMsg.printMsg("swpToOD commnd: %s" % swpToOD)

      # Do the sweeps
      for loop in xrange(sweepOptions['sweepCnt']):
         for direction in (swpToOD, swpToID):
            objMsg.printMsg("Sending Command: %s" % direction)
            accumulator = self.PBlock(direction)  #Send sweep command
            sptCmds.promptRead(sweepOptions['timeout'], accumulator = accumulator)

   def BGMS_EnabledInCode(self):
      if testSwitch.extern.CONGEN_SUPPORT:
         """Returns boolean if BGMS compiled into F3 code"""
         sptCmds.gotoLevel('T')
         res = sptCmds.sendDiagCmd('F"BGMS_ENABLE"', printResult = True)

         match = re.search("BGMS_ENABLE\s*=\s*(?P<val>[\da-fA-F]+)", res)

         if match:
            retDict = match.groupdict()
            if int(retDict['val'], 16) > 0:
               return True

         return False
      else:
         return False

   def negTrackWrite(self, inPrm):
      """
      Writes data to tracks outside of track 0.
      Number of tracks to write is determined by the trkCnt input
      """
      trkCnt = inPrm.get('trackCount')  #number of tracks ouside
      lowMIPSSymLoc = inPrm.get('lowMIPSFlagServoSymbolOffset')  # numeric SAP symbol table offset for low MIPS flag.  This is needed to command large servo offsets

      sptCmds.gotoLevel('5')
      sptCmds.sendDiagCmd('w%x,2,0' % lowMIPSSymLoc, printResult=DEBUG)  # clear low MIPS flag
      sptCmds.gotoLevel('2')
      for head in range(self.dut.imaxHead):  # imaxHead is really numHeads
         objMsg.printMsg("Writing %d sequential tracks outside of track 0 on head %d" % (trkCnt,head))
         sptCmds.sendDiagCmd('PCCCC,CCCC,,1', printResult=DEBUG) # Set 2T pattern
         for track in range(trkCnt):
            self.setStateSpace('A0')  #Single track, and head
            self.seekTrack(0,head) # logical seek to track 0
            sptCmds.sendDiagCmd('Y4,,,,10A31C0', printResult=DEBUG, loopSleepTime=0, maxRetries = 3) # enable direct write mode
            sptCmds.sendDiagCmd('K%x,1,0' % (0x10000-0x100*(track+1)), printResult=DEBUG) # change seek offset to -100%*current track (offset is Q8)
            sptCmds.sendDiagCmd('z', printResult=DEBUG) # Write all wedges on the track
            sptCmds.sendDiagCmd('K0,1', printResult=DEBUG) # restore offset to 0
            sptCmds.sendDiagCmd('Y4', printResult=DEBUG, loopSleepTime=0) # set retries to mode 4, "Minimum Normal" retries
         self.setZeroPattern(printResult=DEBUG) # last, re-write zeros to track 0.  This should not be needed
         self.seekTrack(0,head)
         sptCmds.sendDiagCmd('W', printResult=DEBUG)

   def writePackOffTrk(self, inPrm, head = None):
      """
      Writes data to tracks outside of track 0.
      Number of tracks to write is determined by the trkCnt input
      """
      #trkCnt = inPrm.get('trackCount')  #number of tracks ouside
      lowMIPSSymLoc = inPrm.get('lowMIPSFlagServoSymbolOffset')  # numeric SAP symbol table offset for low MIPS flag.  This is needed to command large servo offsets
      sptCmds.gotoLevel('5')
      message_11 = sptCmds.sendDiagCmd('w%x,2,0' % lowMIPSSymLoc, printResult=DEBUG)  # clear low MIPS flag. 5>w0x112,2,0
      objMsg.printMsg("***************          result after sendDiagCmd(w_x,2,0) = %s" % message_11)
      sptCmds.gotoLevel('2')
      objMsg.printMsg("***************       sent   gotoLevel('2')")
      sptCmds.sendDiagCmd('PAAAA,AAAA,,1', printResult=DEBUG) # Set 1T pattern
      sptCmds.sendDiagCmd('PAAAA,AAAA,,1', printResult=DEBUG) # Set 1T pattern
      #self.seekTrack('0,0', printResult=DEBUG) # logical seek to track 0
      sptCmds.sendDiagCmd('S0,0', printResult=DEBUG) # seek track = head = 0
      objMsg.printMsg("***************       sent   sendDiagCmd(S0,0)")
      sptCmds.sendDiagCmd('K0,1', printResult=DEBUG) # restore offset to 0
      self.setStateSpace('A0', printResult=DEBUG)                  # Set space for 1 track only
      message_12 = sptCmds.sendDiagCmd('z,,,,1', printResult=DEBUG)  # Write 1 track
      objMsg.printMsg("***************          results after write 1 track: sendDiagCmd(z,,,,1) = %s" % message_12)

      #write with negative offset so we don't erase system area.

      message_13 = sptCmds.sendDiagCmd('KFF8E,1,0', printResult=DEBUG) # set offset to 44 percent, later use prm_CleanPack
      #positive track offset overwrites system area on max track!
      #message_13 = sptCmds.sendDiagCmd('K70,1,0', printResult=DEBUG) # set offset to 44 percent, later use prm_CleanPack

      objMsg.printMsg("***************          sent sendDiagCmd(K70,1,0) - 44 percent off track = %s" % message_13)
      sptCmds.gotoLevel('8')
      sptCmds.sendDiagCmd('C15,4CD', printResult = DEBUG) #Set write fault threshold to 30%
      sptCmds.gotoLevel('2')
      #self.setStateSpace('A3')              # All tracks, and heads
      ##      message_14 = sptCmds.sendDiagCmd('A3', printResult=DEBUG) # set for all heads, sequencial, all tracks
      ##      objMsg.printMsg("***************          result after sendDiagCmd(A3) %s" % message_14 )
      message_1 = sptCmds.sendDiagCmd('Y3', printResult=DEBUG) # set retries to mode Y3, "Default Full" retries
      objMsg.printMsg("***************          result after sent sendDiagCmd(Y3) = %s" % message_1)
      ##      message_2 = sptCmds.sendDiagCmd('L1,29000', printResult=DEBUG)     # do not stop on error   <<<------ SET 29000H Loops For Test
      ##      #sptCmds.sendDiagCmd('L1,29000', printResult=DEBUG)  # do not stop on error   <<<------ SET 300 Loops For Test
      ##      objMsg.printMsg("***************          result  after sendDiagCmd(L1,29000) = %s" % message_2)
      ##      #message_3 = sptCmds.sendDiagCmd('z,,,,1', timeout=21600, printResult=DEBUG)
      ##      sptCmds.sendDiagCmd('z,,,,1', timeout=21600, printResult=DEBUG)

      self.sequentialGenericCommand(38400,'z,,,,1','WEDGE_WRITE', byHead = True, head = head)
      #objMsg.printMsg("***************         result  after  sendDiagCmd(z,,,,1) = %s" % message_3)
      message_4 = sptCmds.sendDiagCmd('K0,1', printResult=DEBUG) # restore offset to 0
      objMsg.printMsg("***************         result  after  sendDiagCmd(K0,1) = %s" % message_4)

   def isReady(self, data = None):
      """
      This function will return True if the Drive Serial Port is ready to
      execute command and False if it's not ready.

      @type data: string
      @param data: result of Ctrl-Z command

      FDE drive with locked Serial Port will take sometime (about 5 seconds)
      from first command to ready.

      FDE drive will alternatively returns following message for Ctrl-Z
      Command when the Serial Port is not ready:
         - Rst 0x08M, Rst 0x15, or Rst ...
         - (1Ah)-Serial Port Not Ready
         - (P) SATA Reset
            Pass-Through
            SeaCOS 3.3 Build 0
      """
      try:
         if data == None:
            data = sptCmds.execOnlineCmd(CTRL_Z, timeout = 10, waitLoops = 100)
            objMsg.printMsg("Data returned from Ctrl-Z command:\n%s" % data)
         if ("Rst" in data) or \
            ("Serial Port Not Ready" in data) or \
            ("SeaCOS" in data):
            return False
         else:
            return True
      except:
         return False

   def waitForReady(self, max = 10, interval = 1):
      """
      Wait until Serial Port ready. This function will return True if
      Serial Port is ready within the maximum time otherwise it will return
      False.

      @type max: integer
      @param max: maximum time in second
      @type interval: integer
      @param interval: interval time in second
      """
      try:
         import math
         retryMax = int(math.ceil(max / interval))
         for ctr in range(1, retryMax + 1):
            if self.isReady() == True:
               return True
            else:
               time.sleep(interval)
         return False
      except:
         return False

   if testSwitch.FE_0121834_231166_PROC_TCG_SUPPORT:
      def isSeaCosLocked(self, data = None):
         """
         This function will return True if the Drive Serial Port is locked and
         False if it's not.

         @type data: string
         @param data: result of Ctrl-Z command

         FDE drive will alternatively returns following message for Ctrl-Z
         Command when the Serial Port is locked:
            - ?>
            - (1Ah)-Serial Port Disabled
         """
         try:
            if data == None:
               data = sptCmds.execOnlineCmd(CTRL_Z, timeout = 10, waitLoops = 100)
               objMsg.printMsg("Data returned from Ctrl-Z command:\n%s" % data)
            if ("?>" in data) or ("(1Ah)-Serial Port Disabled" in data):
               return True
            else:
               return False
         except:
            return False


      def isTCGLocked(self, data = None):
         """
          This function will return True if the Drive Serial Port is locked and
          False if it's not.

          TCG FDE drive.

          @type data: string
          @param data: result of Ctrl-Z command

          FDE drive will alternatively returns following message for Ctrl-Z
          Command when the Serial Port is locked:
              - &>
              - (1Ah)-TCG Serial Port Disabled
          """
         try:
            if data == None:
               data = sptCmds.execOnlineCmd(CTRL_Z, timeout = 10, waitLoops = 100)
               objMsg.printMsg("Data returned from Ctrl-Z command:\n%s" % data)
            if ("&>" in data) or ("(1Ah)-TCG Serial Port Disabled" in data):
               return True
            else:
               return False
         except:
            return False
   else:
      def isLocked(self, data = None):
         """
         This function will return True if the Drive Serial Port is locked and
         False if it's not.

         @type data: string
         @param data: result of Ctrl-Z command

         FDE drive will alternatively returns following message for Ctrl-Z
         Command when the Serial Port is locked:
            - ?>
            - (1Ah)-Serial Port Disabled
         """
         try:
            if data == None:
               data = sptCmds.execOnlineCmd(CTRL_Z, timeout = 10, waitLoops = 100)
               objMsg.printMsg("Data returned from Ctrl-Z command:\n%s" % data)
            if ("?>" in data) or ("(1Ah)-Serial Port Disabled" in data):
               return True
            else:
               return False
         except:
            return False

   def ToggleRwTracing(self, error = False, command = False, retry = False):
      """
      Toggle R/W Tracing (Online Control D or Control N)
        This command steps through all possible combinations of enabled / disabled states for
        the following three R/W Tracing features:

           Retry Tracing
           Command Tracing
           Error Tracing
      """

      expected = "%d %d %d" % (error, command, retry)

      for i in xrange(20):
         data = sptCmds.sendDiagCmd(CTRL_D, timeout = 1, altPattern = '\d \d \d', printResult = False, raiseException = 0)
         if testSwitch.virtualRun:
            data = expected
         if DEBUG > 0:
            objMsg.printMsg('cmd=CTRL_D data=%s' % (`data`))
         if expected in data:
            break
      else:
         ScrCmds.raiseException(10345, "Unable to turn on R/W Tracing. Expected response: %s" % expected)


   def ProcessTruputData(self, data):
      """
      Process Return Data of Level 2 'T': Rev 0014.0000. Example return data:
         F3 2>T0
                 Cyl   Head  MnZn  Throughput  CalThruput
         Hd  Zn  Skew  Skew  Skew  (MB/s)      (MB/s)      Ratio   StartLBA   EndLBA
         0   00  24    3C    31     79.700      79.750     0.999   00000000   00003C00
      """

      TruputPatStr = '^\s*(?P<Head>[\d])\s+(?P<Zone>[\dA-Fa-f]+)\s+(?P<CylSkew>[\dA-Fa-f]+)\s+(?P<HeadSkew>[\dA-Fa-f]+)\s+(?P<MnZnSkew>[\dA-Fa-f]+)\s+(?P<Truput>[\SA-Fa-f]+)\s+(?P<Cal_Truput>[\SA-Fa-f]+)\s+(?P<Ratio>[\SA-Fa-f]+)\s+(?P<StartLBA>[\dA-Fa-f]+)\s+(?P<EndLBA>[\dA-Fa-f]+)'
      TruputPatStr2 =                 '^\s*(?P<Zone>[\d??])\s+(?P<CylSkew>[\dA-Fa-f]+)\s+(?P<HeadSkew>[\dA-Fa-f]+)\s+(?P<MnZnSkew>[\dA-Fa-f]+)\s+(?P<Truput>[\SA-Fa-f]+)\s+(?P<Cal_Truput>[\SA-Fa-f]+)\s+(?P<Ratio>[\SA-Fa-f]+)\s+(?P<StartLBA>[\dA-Fa-f]+)\s+(?P<EndLBA>[\dA-Fa-f]+)'

      if testSwitch.WA_0256539_480505_SKDC_M10P_BRING_UP_DEBUG_OPTION:
         """     Cyl   Head  MnZn  Throughput  CalThruput
         Hd  Zn  Skew  Skew  Skew  (MB/s)      (MB/s)      Ratio   StartLBA   EndLBA
         0   00  24    3C    31     79.700      79.750     0.999   00000000   00003C00
         7   3C  E     6E    69      0.000      65.673     0.000   FFFFFFFFFFFFFFFF   FFFFFFFFFFFFFFFF invalid address
          RECOV Servo Op=0995 Resp=00059   23  E     6E    69     73.039      91.127     0.801   00002CA53E0A   00002CA5D90A
         9   24  E     6E    69     86.371      89.967     0.960   00002E53C69A   00002E545FBA
         """
         TruputPatStr = '^\s*(RECOV Servo Op=\d{4} Resp=\d{4})?(?P<Head>[\dA-Fa-f]+)\s+(?P<Zone>[\dA-Fa-f]+)\s+(?P<CylSkew>[\dA-Fa-f]+)\s+(?P<HeadSkew>[\dA-Fa-f]+)\s+(?P<MnZnSkew>[\dA-Fa-f]+)\s+(?P<Truput>[\d]+\.[\d]{3})\s+(?P<Cal_Truput>[\d]+\.[\d]{3})\s+(?P<Ratio>[\d]+\.[\d]{3})\s+(?P<StartLBA>[\dA-Fa-f]{8,16})\s+(?P<EndLBA>[\dA-Fa-f]{8,16})( invalid address)?$'
         TruputPatStr2 =                        '^\s*(RECOV Servo Op=\d{4} Resp=\d{4})?(?P<Zone>[\dA-Fa-f]+)\s+(?P<CylSkew>[\dA-Fa-f]+)\s+(?P<HeadSkew>[\dA-Fa-f]+)\s+(?P<MnZnSkew>[\dA-Fa-f]+)\s+(?P<Truput>[\d]+\.[\d]{3})\s+(?P<Cal_Truput>[\d]+\.[\d]{3})\s+(?P<Ratio>[\d]+\.[\d]{3})\s+(?P<StartLBA>[\dA-Fa-f]{8,16})\s+(?P<EndLBA>[\dA-Fa-f]{8,16})( invalid address)?$'


      TruputPat = re.compile(TruputPatStr)
      TruputPat2 = re.compile(TruputPatStr2)

      rwPat = re.compile("RW cmd 0002 req =\s*(?P<Bit1>[\dA-Fa-f]+)\s+(?P<Bit2>[\dA-Fa-f]+)\s+(?P<Bit3>[\dA-Fa-f]+)\s+(?P<Bit4>[\dA-Fa-f]+)")
      TruputLst = []
      rwLst = []

      for line in data.splitlines():
         TruputMatch = TruputPat.match(line)
         if TruputMatch:
            tempDict = TruputMatch.groupdict()
            TruputLst.append(tempDict)
         else:
            TruputMatch = TruputPat2.match(line)
            if TruputMatch:
               tempDict = TruputMatch.groupdict()
               tempDict['Head'] = '0'
               TruputLst.append(tempDict)

         rwMatch = rwPat.match(line)
         if rwMatch:
            tempDict = rwMatch.groupdict()
            lst = rwMatch.groups()
            sLbaAdd = lst[3] + lst[2] + lst[1] + lst[0]
            iLbaAdd = int(sLbaAdd, 16)
            rwLst.append(iLbaAdd)


      if DEBUG > 0:
         objMsg.printMsg('\nTruputLst=%s' % TruputLst)
         objMsg.printMsg('rwLst=%s' % rwLst)

      rwLst=list(set(rwLst))
      rwLst.sort()

      if DEBUG > 0:
         objMsg.printMsg('New rwLst=%s' % rwLst)
         objMsg.printMsg('rwLst TruputLst Len=%s %s' % (len(rwLst), len(TruputLst)))

      if len(rwLst) > 0:
         if len(rwLst) != len(TruputLst) and not testSwitch.virtualRun:
            objMsg.printMsg('rwLst=%s' % rwLst)
            objMsg.printMsg('TruputLst=%s' % TruputLst)
            ScrCmds.raiseException(10345, "TruputLst and wrLst len error %s %s" % (len(rwLst), len(TruputLst)))

         for i in TruputLst:
            j = int(i['Zone'], 16)
            i['Start_LBA'] = int(rwLst[j])

      if DEBUG > 0:
         objMsg.printMsg('New TruputLst=%s' % TruputLst)

      return TruputLst, rwLst

   def GetCtrl_L(self, printResult = True, force = False):
      """"
      CheopsAM.1.0.SATA.Rosewood.Mule.Servo376.Rap30.4K + SMR Despo D
      Product FamilyId: 8C, MemberId: 04
      HDA SN: W93003N6, RPM: 5456, Wedges: 178, Heads: 2, OrigHeads: 4, Lbas: 00000B4BF5C7, PreampType: 82 02
      Bits/Symbol: C, Symbols/UserSector: C49, Symbols/SystemSector: C3D
      PCBA SN: 0000J538QGZP, Controller: CHEOPSM_1_0_SATA(1010), Channel: Unknown, PowerAsic: KONA Rev 6042, BufferBytes: 8000000
      SF ID: EF 14, SF Part Size: 400, Flash Used: 400
      Package Version: RWN100.SDM3.AA0029.0001    , Package P/N: ---------, Package Global ID: 00080603,
      Package Build Date: 04/24/2015, Package Build Time: 18:07:27, Package CFW Version: RWN1.SDM3.00860337.00080603,
      Package SFW1 Version: ----, Package SFW2 Version: ----, Package SFW3 Version: ----, Package SFW4 Version: ----
      Controller FW Rev: 00290001, CustomerRel: 0001, Changelist: 00860337, ProdType: RWN1.SDM3, Date: 04/24/2015, Time: 180727, UserId: 00080603
      Servo FW Rev: A836
      TCG IV Version: n/a
      Package BPN: 7
      RAP FW Implementation Key: 1E, Format Rev: 0106, Contents Rev: 3C 06 01 00
      Active BFW Container: 1
      4K Sys Area: 1
      Features:
      - Quadradic Equation AFH enabled
      - VBAR with adjustable zone boundaries enabled
      - Volume Based Sparing enabled
      - IOEDC enabled
      - IOECC enabled
      - DERP Read Retries enabled v. 5.0.05.0000000000000003
      - LTTC-UDR2 enabled
      - SuperParity 4.1 enabled
         TotalSuperBlks     TotalValidSuperBlks
         0009FC30           0009FC29
      - Humidity Sensor disabled
      - Media Cache Partition enabled
      - Media Cache enabled
      - Background Reli Activity Critical Event Logging enabled
      - Low Current Spin Up Feature enabled
      - Torn Write Protection disabled
      - Zone Remap enabled
      [PLBA:00000000 Len:00534C06 Offset:0A961AAD]
      [PLBA:00534C06 Len:0A961AAD Offset:FFACB3FA]
      [PLBA:0AE966B3 Len:00628F14 Offset:00000000]
      [PLBA:0B4BF5C7 Len:00000001 Offset:00000000]
      - AGB enabled
      - SubRelease:0
      - FAFH 36.1 enabled
      - EWP:0
      - DRAM Mirror:0
      """

      if self.dataCTRL_L is None or force:
         objMsg.printMsg("Acquiring CTR_L data.")
         # example return data {'Wedges': 'F8', 'Heads': '1', 'RPM': '7265', 'SN': '3VF001WD', 'Lbas': 'DF94BB0', 'UDR2': 'compiled'}

         from CodeVer import BaseCodeVersionInfo

         self.quickDiag()

         for retry in xrange(3):
            if retry > 1:
               data = sptCmds.sendDiagCmd(CTRL_L, printResult=bool(DEBUG),maxRetries=3)
            else:
               dummydata = sptCmds.execOnlineCmd(CTRL_L, timeout = 10, waitLoops = 100)  # added by swleow to aviod data lost
               data = sptCmds.execOnlineCmd(CTRL_L, timeout = 10, waitLoops = 100)

            if testSwitch.virtualRun:
               try:
                  from pgm_Constants import pgm_CTRL_L
                  data = pgm_CTRL_L
               except:
                  data = self.GetCtrl_L.__doc__

            Pat = re.compile('SN: (?P<SN>[\dA-Z]+), RPM: (?P<RPM>\d+), Wedges: (?P<Wedges>[\dA-F]+), Heads: (?P<Heads>[\dA-F]+), Lbas: (?P<Lbas>[\dA-F]+)')

            Mat = Pat.search(data)
            if not Mat:
               if not ( testSwitch.M11P or testSwitch.M11P_BRING_UP ):
                  Pat = re.compile('HDA SN: (?P<SN>[\dA-Z]+), RPM: (?P<RPM>\d+), Wedges: (?P<Wedges>[\dA-F]+), Heads: (?P<Heads>[\dA-F]+), OrigHeads: (?P<OrigHeads>[\dA-F]+), Lbas: (?P<Lbas>[\dA-F]+), PreampType: (?P<PreampType>[\dA-Z]+)')
               else:
                  Pat = re.compile('HDA SN: (?P<SN>[\dA-Z]+), RPM: (?P<RPM>\d+), Wedges: (?P<Wedges>[\dA-F]+), Heads: (?P<Heads>[\dA-F]+), OrigHeads: (?P<OrigHeads>[\dA-F]+), ActiveHdMap: (?P<ActiveHdMap>[\dA-F]+), Lbas: (?P<Lbas>[\dA-F]+), PreampType: (?P<PreampType>[\dA-Z]+)')                  
               Mat = Pat.search(data)

            if Mat:
               self.dataCTRL_L = Mat.groupdict()
            else:
               objMsg.printMsg("Warning CTR_L pattern mismatch. data=%s" % data)
               time.sleep(10) # pause if CTRL_L data fails before retry
               continue
            Pat = re.compile(BaseCodeVersionInfo().CTRLL_REGEX)   # append code version
            patMat = Pat.search(data)
            if patMat:
               codeDict = patMat.groupdict()
               self.dataCTRL_L.update(patMat.groupdict())
            else:
               time.sleep(10) # pause if CTRL_L data fails before retry
               continue
            if not (testSwitch.M11P or testSwitch.M11P_BRING_UP): # Temporary block for M11P(Not supported yet)
               # append Zone Remap info
               Pat = re.compile('Remap (?P<Remap>[\wA-Za-z]+)')
               Mat = Pat.search(data)
               if Mat:
                  self.dataCTRL_L.update(Mat.groupdict())
               else:
                  time.sleep(10) # pause if CTRL_L data fails before retry
                  continue
   
               # append AGB info
               Pat = re.compile('AGB (?P<AGB>[\wA-Za-z]+)')
               Mat = Pat.search(data)
               if Mat:
                  self.dataCTRL_L.update(Mat.groupdict())
               else:
                  time.sleep(10) # pause if CTRL_L data fails before retry
                  continue
   
               # append SuperParityRatio info
               Pat = re.compile('\S+\s+TotalValidSuperBlks\s+(?P<TOTALSUPER_BLKS>[a-fA-F\d]+)\s+(?P<TOTALVALIDSUPER_BLKS>[a-fA-F\d]+)')
               Mat = Pat.search(data)
               if Mat:
                  self.dataCTRL_L.update(Mat.groupdict())
               else:
                  time.sleep(10) # pause if CTRL_L data fails before retry
                  continue
   
               # append FAFH info
               #Pat = re.compile('FAFH 36.1 (?P<FAFH>[\wA-Za-z]+)')
               Pat = re.compile('FAFH (?P<FAFH_VER>\S+).(?P<FAFH>[\wA-Za-z]+)')
               Mat = Pat.search(data)
               if Mat:
                  self.dataCTRL_L.update(Mat.groupdict())
               else:
                  time.sleep(10) # pause if CTRL_L data fails before retry
                  continue
   
               # append Low Current Spin Up Feature info
               Pat = re.compile('Low Current Spin Up Feature (?P<LowCurrentSpinUp>[\wA-Za-z]+)')
               Mat = Pat.search(data)
               if Mat:
                  self.dataCTRL_L.update(Mat.groupdict())
               else:
                  time.sleep(10) # pause if CTRL_L data fails before retry
                  continue
   
               # append UDR2 info
               Pat = re.compile('UDR2 (?P<UDR2>[\wA-Fa-f]+)')
               Mat = Pat.search(data)
               if Mat:
                  self.dataCTRL_L.update(Mat.groupdict())
   
                  if DEBUG or printResult:  #only show good data
                     objMsg.printMsg('CTRL_L data=%s' % str(data))
                  theCell.disableESlip()
                  return self.dataCTRL_L
               else:
                  time.sleep(10) # pause if CTRL_L data fails before retry
                  continue

            self.syncBaudRate(Baud38400)
         else:
            ScrCmds.raiseException(12345,"Fail to get CTRL_L data!")
      else:
         objMsg.printMsg("CTR_L data already acquired.")
         return self.dataCTRL_L

   def GetCtrl_A(self):
      """Retruns CTRL+A data"""
      data = sptCmds.sendDiagCmd(CTRL_A, printResult=True)
      if testSwitch.virtualRun:
         data = """
         Prod Desc: KarnakPlus.1.0.SATA.Chengai.Mule.Servo256.Rap30.4K + SMR Despo DFW
         Package Version: CH09E4.SDM1.00658329.00080603
         Serial #: Q6700A4W
         Changelist: 00658329
         Model #: ST720XX028-1KK162
         ID: 100

         TotalHostWrites 00000000
         NumberOfSegWrites 0000
         TotalHPCBROs 00000000
         TotalBWOs 00000000
         MCMTWrites 00000001
         Idle1Count 00000000
         MCSegmentUsed 0000
         MCNodeUsed 00000000
         """
      return data

   def GetDriveRPMWedges(self):
      """
      Get drive RPM/Wedges from Ctrl-L
      """

      data = sptCmds.sendDiagCmd(CTRL_L, altPattern='PreampType:', printResult=False)
      if testSwitch.virtualRun:
         data='\r\n\r\nHDA SN: 3WQ00173, RPM: 7268, Wedges: 120, Heads: 2, Lbas: 1D1C5970, PreampType: 5B 02\r\n'

      if DEBUG > 0:
         objMsg.printMsg('CTRL_L data=%s' % (`data`))

      rpmPat = re.compile('RPM: (?P<rpm>\d+)')
      rpmMat = rpmPat.search(data)

      rpm = -1
      if rpmMat:
         rpm = int(rpmMat.groupdict()['rpm'])

      WedgesPat = re.compile('Wedges: (?P<Wedges>\d+)')
      WedgesMat = WedgesPat.search(data)

      Wedges = -1
      if WedgesMat:
         Wedges = int(WedgesMat.groupdict()['Wedges'])

      return rpm, Wedges


   def GetSecTrack(self):
      """
      Get sector track using 2>x0 command. Supported in rev 0013 and above. Example data:
           Physical      Logical       Sec   Sym   Sym      Data
        Zn Cylinders     Cylinders     Track Wedge Track    Rate
        00 000000-001CE2 000000-001CE2 0700  0A60  000BD7E0  895.166
        01 001CE3-0044ED 001CE3-0044ED 06E9  0A3D  000BB2C0  884.179
        02 0044EE-006797 0044EE-006797 06C0  09E8  000B5200  855.615

      """

      ldict = self.GetCtrl_L()
      numheads = int(ldict['Heads'], 16)

      sptCmds.gotoLevel('2')
      data = sptCmds.sendDiagCmd('x0', printResult=False, loopSleepTime = 0.01)

      if testSwitch.virtualRun:
         data='x0\r\n\r\nUser Partition\r\n\r\n LBAs 00000000-1D1C596F\r\n PBAs 00000000-1D46F36B\r\n HdSkew 0041, CylSkew 0030\r\n ZonesPerHd 18\r\n\r\n Head 0, PhyCyls 000000-02D7BB, LogCyls 000000-02CF99\r\n\r\n     Physical      Logical       Sec   Sym   Sym      Data      \r\n  Zn Cylinders     Cylinders     Track Wedge Track    Rate      \r\n  00 000000-001A93 000000-001A93 06A0  09E0  000B47E0 1139.062  \r\n  01 001A94-0040F7 001A94-0040F7 0690  09C7  000B2BC0 1128.076  \r\n  02 0040F8-005E13 0040F8-005E13 0678  09A4  000B0460 1112.695  \r\n  03 005E14-007805 005E14-007805 0660  097B  000AD760 1095.117  \r\n  04 007806-00A0BB 007806-00A0BB 063D  094F  000AA5E0 1075.341  \r\n  05 00A0BC-00B4C5 00A0BC-00B4C5 0630  0932  000A8540 1062.158  \r\n  06 00B4C6-00D5AD 00B4C6-00D5AD 0600  08F6  000A41C0 1035.791  \r\n  07 00D5AE-00F227 00D5AE-00F227 05E0  08CA  000A1040 1016.015  \r\n  08 00F228-0115CD 00F228-0115CD 05BA  0893  0009D260  991.845  \r\n  09 0115CE-013505 0115CE-013505 05A0  0853  00098A60  963.281  \r\n  0A 013506-015659 013506-015659 056B  0821  00095220  941.308  \r\n  0B 01565A-018857 01565A-018857 052C  07C3  0008E860  899.560  \r\n  0C 018858-01A53D 018858-01A53D 0510  078B  0008AA80  875.390  \r\n  0D 01A53E-01C4AB 01A53E-01C4AB 04E0  074C  00086280  846.826  \r\n  0E 01C4AC-01E81B 01C4AC-01E81B 04B0  070C  00081A80  818.261  \r\n  0F 01E81C-02067B 01E81C-02067B 0480  06A5  0007A580  772.119  \r\n  10 02067C-02164D 02067C-02164D 0480  06A8  0007AB20  774.316  \r\n  11 02164E-022D81 02164E-022D81 0452  0680  00077E20  756.738  \r\n  12 022F68-024FE3 022D82-024DFD 0420  062E  00071FA0  719.384  \r\n  13 024FE4-0269D5 024DFE-0267EF 03F8  05FB  0006E760  697.412  \r\n  14 0269D6-0285E3 0267F0-0283FD 03D3  05BF  0006A3E0  671.044  \r\n  15 0285E4-02A551 0283FE-02A36B 03A0  057A  00065640  640.283  \r\n  16 02A552-02BFE5 02A36C-02BDFF 037A  053F  000613E0  613.916  \r\n  17 02BFE6-02D7BB 02BE00-02D5D5 0360  04FB  0005C640  583.154  \r\n\r\n Head 1, PhyCyls 000000-02E535, LogCyls 000000-02DCD5\r\n\r\n     Physical      Logical       Sec   Sym   Sym      Data      \r\n  Zn Cylinders     Cylinders     Track Wedge Track    Rate      \r\n  00 000000-001B11 000000-001B11 0686  09B9  000B1AE0 1121.484  \r\n  01 001B12-00422B 001B12-00422B 0670  099B  000AFA40 1108.300  \r\n  02 00422C-005FD1 00422C-005FD1 0657  0978  000AD2E0 1092.919  \r\n  03 005FD2-007A3E 005FD2-007A3E 0644  095B  000AB120 1079.736  \r\n  04 007A3F-00A3B5 007A3F-00A3B5 0620  0924  000A7460 1055.566  \r\n  05 00A3B6-00B81E 00A3B6-00B81E 0606  0905  000A5180 1042.382  \r\n  06 00B81F-00D9A2 00B81F-00D9A2 05E8  08D4  000A1A60 1020.410  \r\n  07 00D9A3-00F6A3 00D9A3-00F6A3 05C9  08A8  0009E8E0 1000.634  \r\n  08 00F6A4-011AF2 00F6A4-011AF2 05A0  084E  000983A0  961.083  \r\n  09 011AF3-013ABE 011AF3-013ABE 0579  0834  00096780  950.097  \r\n  0A 013ABF-015CB0 013ABF-015CB0 0551  07FA  00092520  923.730  \r\n  0B 015CB1-018F9B 015CB1-018F9B 0515  07A1  0008C100  884.179  \r\n  0C 018F9C-01AD0A 018F9C-01AD0A 04F3  0769  00088320  860.009  \r\n  0D 01AD0B-01CD0D 01AD0B-01CD0D 04C8  0729  00083B20  831.445  \r\n  0E 01CD0E-01F125 01CD0E-01F125 049A  06E9  0007F320  802.880  \r\n  0F 01F126-021015 01F126-021015 0480  06A5  0007A580  772.119  \r\n  10 021016-022032 021016-022032 045C  0690  00078F00  763.330  \r\n  11 022033-0237D4 022033-0237D4 043C  065F  000756C0  741.357  \r\n  12 0239C4-025AD9 0237D6-0258EB 040C  0615  00070380  708.398  \r\n  13 025ADA-027546 0258EC-027358 03F0  05E2  0006CB40  686.425  \r\n  14 027547-0291D9 027359-028FEB 03C0  059E  00067DA0  655.664  \r\n  15 0291DA-02B1DC 028FEC-02AFEE 0390  055E  000635A0  627.099  \r\n  16 02B1DD-02CCEE 02AFEF-02CB00 0368  0527  0005F7C0  602.929  \r\n  17 02CCEF-02E535 02CB01-02E347 0343  04F0  0005B9E0  578.759  \r\n\r\nF3 2>'

      Mat = re.search('ZonesPerHd (?P<ZonesPerHd>[\dA-F]+)', data)
      ZonesPerHd = 0
      if Mat:
         ZonesPerHd = int(Mat.groupdict()['ZonesPerHd'], 16)

      TrackPat = re.compile('^\s*(?P<Zone>[\dA-Fa-f]+)\s+(?P<PhyCyl>[\SA-Fa-f]+)\s+(?P<LogCyl>[\SA-Fa-f]+)\s+(?P<SecTrack>[\dA-Fa-f]+)')

      SecTrack = []
      ZoneList = []
      for line in data.splitlines():
         if line.find("NumMediaCacheZones") != -1:
            break
         TrackMatch = TrackPat.match(line)
         if TrackMatch:
            SecTrack.append(int(TrackMatch.groupdict()['SecTrack'], 16))
            ZoneList.append(int(TrackMatch.groupdict()['Zone'], 16))

      iZones = max(ZoneList) + 1
      iHead = len(ZoneList) / iZones

      AveScTrk = []
      for i in xrange(iZones):
         HdLst = []
         for j in xrange(iHead):
            HdLst.append(SecTrack[i + (j * iZones)])


         AveScTrk.append(sum(HdLst)/len(HdLst))

      if len(SecTrack) != numheads * ZonesPerHd or numheads != iHead:
         objMsg.printMsg('Suspected data error. iHead=%s numheads=%s ZonesPerHd=%s SecTrack=%s' % (iHead, numheads, ZonesPerHd, SecTrack))
         ScrCmds.raiseException(10566, "Failed to retrieve 2>x0 zone data")

      return (AveScTrk * iHead), SecTrack

   def disableSWD(self, printResult = True):
      sptCmds.gotoLevel('5')
      sptCmds.sendDiagCmd('wb4,,0', printResult = printResult)

   def enableSWD(self, printResult = True):
      sptCmds.gotoLevel('5')
      sptCmds.sendDiagCmd('wb4,,1', printResult = printResult)

   def getAccessTime(self, seekOptions, raiseException=False):
      ''' Function checks for seek read/write access time. '''

      sptCmds.enableDiags()
      sptCmds.gotoLevel('3')

      avgText = 'Avg Time usec = '
      result = 'PASS'
      msg = ''
      avgTime = p = 0
      for seekType, seekVal in seekOptions.iteritems():
         data = sptCmds.sendDiagCmd("D, %s" %seekVal, timeout = 60, printResult = True, altPattern = '>')
         p = data.find(avgText)
         if p > -1:
            p = p + len(avgText)
            avgTime = int(data[p:p+6])/1000.0
            if avgTime > TP.accessTimeLimits[seekType]:
               result = 'FAIL'
               msg += "*** Average '%s' access time %s! Measured = %s msec, Limit = %s msec \n %s" \
                  %(seekType, result, avgTime, TP.accessTimeLimits[seekType], " " * 22)

      objMsg.printMsg ("=" * 80)
      objMsg.printMsg (" Seek Access Time Result  -  %s" %result)
      objMsg.printMsg (" %s" %msg)
      objMsg.printMsg ("-" * 80)
      if result=='FAIL' and raiseException:
         ScrCmds.raiseException(13450, "Access Time out of spec error.")

   def GetPhysicalLogicalSectorSize(self):
      """
      Get PhysicalLogicalSectorSize. Example data:
         F3 T>F"PhysicalLogicalSectorSize"
         Byte:04A2:       PhysicalLogicalSectorSize = 03 60
         Byte:04A2:           Bit:0, TWO_X_LOG_SECTORS_PER_PHY_SECTOR_B0 = 1
         Byte:04A2:           Bit:1, TWO_X_LOG_SECTORS_PER_PHY_SECTOR_B1 = 1
         Byte:04A2:           Bit:2, TWO_X_LOG_SECTORS_PER_PHY_SECTOR_B2 = 0
         Byte:04A2:           Bit:3, TWO_X_LOG_SECTORS_PER_PHY_SECTOR_B3 = 0
         Byte:04A3:           Bit:4, DEV_LOG_SEC_LEN_GREATER_THAN_256W = 0
         Byte:04A3:           Bit:5, DEV_HAS_MUL_LOG_SECTORS_PER_PHY_SECTOR = 1
      """

      sptCmds.gotoLevel('T')
      data = sptCmds.sendDiagCmd('''F"PhysicalLogicalSectorSize"''')
      objMsg.printMsg('PhysicalLogicalSectorSize data=%s' % (`data`))

      Factor = 1
      Mat = re.search('DEV_HAS_MUL_LOG_SECTORS_PER_PHY_SECTOR = (?P<MulLogSectors>\d+)\r\n', data)
      if Mat:
         iLogSectors = int(Mat.groupdict()['MulLogSectors'])
         if iLogSectors == 1:
            Mat = re.search('PhysicalLogicalSectorSize = (?P<LogSectorSize>[\dA-F]+) ', data)
            if Mat:
               log2ratio = int(Mat.groupdict()['LogSectorSize'], 16) & 0x0F
               Factor = pow(2, log2ratio)

      return Factor

   def getSPTResultsHeaderData(self, printResult = False):
      self.syncBaudRate()                    # Set lowest baud
      self.gotoLevel('M')
      data = sptCmds.sendDiagCmd('s2,,22', timeout = 2000, printResult = printResult)
      headerData = []
      headInfo = {}
      headerLine = re.compile('(?P<StartSector>[0-9a-fA-F]+)\s+(?P<SizeSectors>[0-9a-fA-F]+)\s+(?P<LenBytes>[0-9a-fA-F]+)\s+(?P<STATUS>[0-9a-fA-F]+)')
      headerHeader = re.compile('header Vers:\s*(?P<VER>\S+)\s*Key:\s*(?P<KEY>\S+)\s*Entries:\s*(?P<ENTRIES>[\da-fA-F]+)\s*numSectors\s*(?P<NUM_SECTORS>[\da-fA-F]+)')

      for line in data.splitlines():
         match = headerLine.search(line)
         if match:
            headerData.append(match.groupdict())

         match = headerHeader.search(line)
         if match:
            headInfo = match.groupdict()

      return headInfo, headerData


   def getSPTResultsFile(self, index, fName, printResult = False):
      self.syncBaudRate()                    # Set lowest baud
      sptFile = GenericResultsFile(fName)
      sptFile.open('wb')
      self.gotoLevel('M')

      data = sptCmds.sendDiagCmd('s0,%X,22' % index, timeout = 2000, printResult = printResult)

      parse = False
      dataBuff = []
      for lineNo, line in enumerate(data.splitlines()):
         if 'Offset' in line:
            parse = True #next line is start of file
            continue
         if 'F3 M>' in line:
            continue #skip last line
         if parse:
            cols = line[9:(3*16)+9].strip().split(' ')#line.split(' ')[1:17] #Strip off the offset col and the ascii display
            dataBuff.extend([struct.pack('B', int(val,16)) for val in cols])

      sptFile.write(''.join(dataBuff))

      sptFile.close()

   def IsMCClean(self):
      """
      Check MC using CTRL_A MCSegmentUsed and MCNodeUsed.
      If both values are zero means MC is clean
      """
      cleanMC = False
      for retry in xrange(3):       # allow retry if cannot get data
         data = self.GetCtrl_A()
         pattern = 'MCSegmentUsed\s(?P<SEGMENT>\w+)[\s+\S+]+MCNodeUsed\s+(?P<NODE>\w+)'
         match = re.search(pattern, data)
         if match:
            MCSegmentUsed = match.groupdict()['SEGMENT']
            MCNodeUsed = match.groupdict()['NODE']
            if ( int(MCSegmentUsed, 16) + int(MCNodeUsed, 16) ) == 0:
               cleanMC = True
            break
         else:
            time.sleep(5)
            continue
      else:
         ScrCmds.raiseException(11044,"Unable to determine MC data")
      objMsg.printMsg( "Media cache is clean? %s" %cleanMC)
      return cleanMC

   def initMCCache(self):
      if testSwitch.WA_0277152_480505_RUN_QUICK_FORMAT_BEFORE_INITMCCACHE:
         self.gotoLevel('T')
         sptCmds.sendDiagCmd('m0,6,2,,,,,22',timeout = 600, printResult = True)
      self.gotoLevel('C')

      if testSwitch.TRUNK_BRINGUP and testSwitch.M10P:
         data = sptCmds.sendDiagCmd('U2', timeout = 1200, printResult = True, DiagErrorsToIgnore = ['00005004'])
      else:
         data = sptCmds.sendDiagCmd('U2', timeout = 1200, printResult = True)

      return data

   def initMCMT(self):
      """
      Initialize mediacache without actually writing to the MC partition, including initialization of meadiacache management table and and
      associated MCMT buffer pointer.
      """
      self.gotoLevel('C')
      data = sptCmds.sendDiagCmd('U10', timeout = 1200, printResult = True, DiagErrorsToIgnore = ['00005004'])
      return data

   def getMCCacheCount(self):
      self.gotoLevel('C')
      data = sptCmds.sendDiagCmd('U',  timeout = 10,  printResult = True)
      if testSwitch.virtualRun:
         data = """
            F3 C>U
            User Data Base  00991560

            MCInfo

            MCStateFlags 0050
            MCSlowFlags 0000
            MCTExtentCount 0E4F
            MCCandidateCount 00
            MCUntranslatedCount 0000
            DiscDirtySegmentCount 0E58
            SegReadExtentsOutstanding 0000
            MCScanDisableCommandCounter 00
            MCSequenceNumber 00003E90
            MCMessageDecode 00000010
            SegmentRemoveFIFOPtr 0000
            MediaCacheProxyDiscNodePtr 4011985C
            MCBusIdleTime (Probably not useful) 000019D8
            MCFreeRunningTime (Probably not useful) 00001DD0
            SegTailPtr 1971
            SegHeadPtr 04E9
            Power Profile 8100
            """
      match = re.search("MCTExtentCount\s*(?P<count>[a-fA-F0-9]+)",  data)
      if match:
         count = int(match.groupdict()['count'], 16)
      else:
         ScrCmds.raiseException(11044, "Failed to parse MCTExtentCount\n%s" % data)
      return count

   def ResetCustomerCountersForShip(self, fieldsToClear=None):
      self.gotoLevel("T")
      if fieldsToClear != None:
         if testSwitch.DiagOverlayWipeOnly:
            sptCmds.sendDiagCmd('S"HIP",%X' % fieldsToClear, timeout = 600, altPattern='CLEAR_DIAGNOSTIC_OVERLAY 6', printResult = True)
            objMsg.printMsg('Diagnostic Overlap wipe done!')
         else:
            sptCmds.sendDiagCmd('S"HIP",%X' % fieldsToClear, timeout = 600, printResult = True)
      else:
         sptCmds.sendDiagCmd('S"HIP"',timeout = 600, printResult = True)
         objMsg.printMsg('Clear all!')

   def SpinUpDrive(self):
      self.gotoLevel('2')
      sptCmds.sendDiagCmd("U", timeout = 60, printResult = False)

   def getHdCylFromLBA(self,LBAList = []):
      self.gotoLevel('A')
      HdCylSummaryList = []
      WholeDataList = []
      if len(LBAList):
         objMsg.printMsg ("LBAList = %s"%(LBAList))
         for LBA in LBAList:
            if testSwitch.virtualRun:
               data = """FAEE8B803
                  Track Info:
                  Partition PhyCyl   LogCyl   NomCyl   RadiusMils   LogHd Zn FirstLba     FirstPba     LogSecs PhySecs WdgSkw SecPerFrm WdgPerFrm
                  User      00017D1C 00017D1C 00017CB4 +1.461750E+3 07    06 0000AEE8B284 0000AEFCDAD5 0B5F    0B60    007E   0007      0001

                  Sector Info:
                  LBA          PBA          LogSec PhySec Wdg  SFI
                  0000AEE8B803 0000AEFCE055 057F   0580   0147 000F6A25
                  """
            else:
               data = sptCmds.sendDiagCmd('F%s'%LBA,  timeout = 10,  printResult = True)

            entry, HdCylData = self.parseHdCylLog(data)
            objMsg.printMsg ("entry = %s"%str(entry))
            objMsg.printMsg ("HdCylData = %s"%str(HdCylData))
            if HdCylData:
               HdCylSummaryList.append(HdCylData)
               WholeDataList.append(entry)
         objMsg.printMsg ("HdCylSummaryList = %s"%str(HdCylSummaryList))
         objMsg.printMsg ("WholeDataList = %s"%str(WholeDataList))
         return HdCylSummaryList

   def GetLTTCPowerOnHours(self):
      """
      Get LTTCPowerOnHours setting 'F"LTTCPowerOnHours"'. Example
         Byte:057F:       LTTCPowerOnHours = 00
         Byte:057F:       LTTCPowerOnHours = 0A

      """

      sptCmds.gotoLevel('T')
      data = sptCmds.sendDiagCmd('''F"LTTCPowerOnHours"''', printResult=bool(DEBUG))

      poh = 0
      Mat = re.search('LTTCPowerOnHours = ([\da-fA-F]+)', data)
      if Mat:
         poh = int(Mat.group(1), 16)

      return poh


   def GetSerpWidth(self):
      """
      Get Drive_Serp_Width, 2>I,1,11
      Example:      Nominal Serpent Width: C8
      """

      DEBUG = 1
      sptCmds.gotoLevel('2')
      data = sptCmds.sendDiagCmd('I,1,11', printResult=bool(DEBUG))
      if testSwitch.virtualRun:
         data='\r\n  Nominal Serpent Width: C9 '

      Drive_Serp_Width = 0
      Mat = re.search('Nominal Serpent Width: ([\da-fA-F]+)', data)
      if Mat:
         Drive_Serp_Width = int(Mat.group(1), 16)

      return Drive_Serp_Width

   def GetNumZones(self):
      """ Returns number of zones from Lvl2 x0,0,0 spt command."""
      sptCmds.gotoLevel('2')
      self.flush()
      accumulator = self.PBlock('x0,0,0\n\n')
      if testSwitch.virtualRun:
         x0 = '\r\n   ZonesPerHd 20 '
      else:
         x0 = sptCmds.promptRead(60, accumulator = accumulator, loopSleepTime = 0)
      zonePat = re.compile('ZonesPerHd (?P<zones>\w+)')
      zoneMat = zonePat.search(x0)
      if zoneMat:
         return int(zoneMat.groupdict()['zones'],16)
      ScrCmds.raiseException(11044, "Failed to identify zone configuration.")


   def parseHdCylLog(self, CylLogData=''):

      HdCylData = {}
      entry = {}
      match = self.CylPattern.search(CylLogData)
      if match:
         entry = match.groupdict()
         HdCylData['Hd'] = entry['LogHd']
         HdCylData['Cyl'] = entry['PhyCyl']

      return entry, HdCylData

   def dispSlipInfo(self,HdCylSummaryList = [],trkRange = 10):

      self.gotoLevel('T')
      if len(HdCylSummaryList):
         for entry in HdCylSummaryList:
            head = entry['Hd']
            trk = re.split('x',hex(string.atoi(entry['Cyl'],16) - 7))[1]
            sptCmds.sendDiagCmd('V1,%s,%s,%s'%(head,trk,trkRange),  timeout = 60,  printResult = True)

      else:
         objMsg.printMsg ("HdCylSummaryList is empty.. Skip display slip information")

   def addLBAToAltList(self, LBA, printResult = False):
      sptCmds.gotoLevel('2')
      sptCmds.sendDiagCmd('F%X,A1'%(LBA,), printResult = printResult)



   PENDING_BBM = 1 #Bit 0 [0x0001]: Entry has been marked as a bad block.
   #Bit 1 [0x0002]: Entry has been alted and has been marked as a bad block.
   #Bit 2 [0x0004]: Entry has been marked as do not write.
   #Bit 3 [0x0008]: Entry has been marked as do not read.
   #Bit 4 [0x0010]: Entry has been marked as do not report to host.
   #Bit 5 [0x0020]: Entry has been marked as logged by SMART.
   #Bit 6 [0x0040]: Entry has been marked as a DOS WTR entered entry
   #Bit 7 [0x0080]: Entry has been reallocated; data-scrub was bypassed because of limit on number of scrub attempts.
   #Bit 8 [0x0100]: Entry has been previously alted
   #Bit 9  [0x0200]: Entry is alted at write
   #Bit 10 [0x0400]: Entry is alted at read
   #Bit 11 [0x0800]: Entry is alted during BGMS
   #Bit 12 [0x1000]: Entry is alted during DOS
   #Bit 13 [0x2000]: Entry is alted from host command
   ALT_FROM_DIAG = 0x4000 #Bit 14 [0x4000]: Entry is alted from diagnostic command
   #Bit 15 [0x8000]: Entry is alted during ORM

   def addPendingListToAltList(self, printResult = True):
      numAlts, LBA_List1 = self.dumpReassignedSectorList(True, True)
      if numAlts['NUMBER_OF_PENDING_ENTRIES'] == 0:
         objMsg.printMsg("No pending entries to merge to alt list.")
         return numAlts

      objMsg.printMsg("About to add following LBAs to Alternated Sector List: %s"%(str(LBA_List1),))
      self.setZeroPattern()
      for LBA in LBA_List1:
         self.addLBAToAltList(LBA['LBA'], printResult)


      numAlts, LBA_List = self.dumpReassignedSectorList(True, True)

      lbalist = []
      for i in LBA_List:
         lbalist.append(i['LBA'])

      for lbadict in LBA_List1:
         if lbadict['LBA'] in lbalist: #in list for 2nd round
            if (lbadict['STATUS'] & self.PENDING_BBM) == self.PENDING_BBM:
               if (lbadict['STATUS'] & self.ALT_FROM_DIAG) != self.ALT_FROM_DIAG:
                  ScrCmds.raiseException(14718,  "Unable to add pending entries to alt list.")
         else:
            ScrCmds.raiseException(14718,  "Unable to add pending entries to alt list.")
      return numAlts

   @spt
   def getCongen(self):
      """ Returns congen setting. """
      return sptCmds.sendDiagCmd('/TF"CongenConfigurationState"')

   def quickDiag(self):
      """ Utility to quickly switch to spt mode."""
      if not objDut.eslipMode:
         objMsg.printMsg("Switching to ESLIP mode.")
         PBlock(CTRL_T)
         time.sleep(1)
         objDut.eslipMode = 1
      sptCmds.enableDiags()

   def GetUDR2(self, getCTRL_L = False):
      try:
         return self.RunGetUDR2(getCTRL_L = getCTRL_L)
      except:
         objMsg.printMsg("RunGetUDR2 failed. Sleep 30s and retry. Traceback=%s" % traceback.format_exc())
         time.sleep(30)
         return self.RunGetUDR2(getCTRL_L = True)

   def RunGetUDR2(self, getCTRL_L = False):
      """
      Get UDR2 setting from Ctrl-L. Returns:
         True if enabled
         False if disabled
         None if not supported
      """
      udrSate = self.GetCtrl_L(force = getCTRL_L)['UDR2']
      udrDict = {'compiled':None, 'enabled':True, 'disabled':False}
      return udrDict[udrSate]

   def GetSPRatio(self, getCTRL_L = False):
      """
      Get TotalSuperBlks and TotalValidSuperBlksfrom Ctrl-L. Returns:
         SuperParityRatio = 1- (TotalValidSuperBlks/TotalSuperBlks)
      """
      try:
         TOTALSUPER_BLKS = int(self.GetCtrl_L(force = getCTRL_L).get('TOTALSUPER_BLKS'), 16)
         TOTALVALIDSUPER_BLKS = int(self.GetCtrl_L(force = False).get('TOTALVALIDSUPER_BLKS'), 16) #second time no need fresh Ctrl+L
      except:
         objMsg.printMsg("Can't retrieve TotalSuperBlks and TotalValidSuperBlks, Powercycle and retry")
         objPwrCtrl.powerCycle()
         TOTALSUPER_BLKS = int(self.GetCtrl_L(force = getCTRL_L).get('TOTALSUPER_BLKS', '0'), 16)
         TOTALVALIDSUPER_BLKS = int(self.GetCtrl_L(force = False).get('TOTALVALIDSUPER_BLKS', '0'), 16) #second time no need fresh Ctrl+L

      objMsg.printMsg("TOTALSUPER_BLKS: %d" %TOTALSUPER_BLKS)
      objMsg.printMsg("TOTALVALIDSUPER_BLKS: %d" %TOTALVALIDSUPER_BLKS)
      if (TOTALSUPER_BLKS > 0) and (TOTALVALIDSUPER_BLKS > 0):
         SPRatio = round(1 - (float(TOTALVALIDSUPER_BLKS)/ float(TOTALSUPER_BLKS)), 6)
         return SPRatio
      else:
         return None

   @spt
   def guardBand(self):
      """ Returns guard band for T598 starting zone """
      sptCmds.gotoLevel('A')
      data = sptCmds.sendDiagCmd('F0')
      if testSwitch.virtualRun:
         data = "User      00000000 00000000 00000000 +1.195999E+3 00    01 00000000 00000000 014B    014B    0000   0016      0011      04FE      0000     00       CD"
      mat = re.search ('User (.*)', data)
      return int(mat.group(0).split()[6])

   def GetFAFHStatus(self, getCTRL_L = False):
      """
      Get FAFH from Ctrl-L. Returns:
         True if enabled
         False if disabled
         None if not supported
      """
      status = {'enabled':True, 'disabled':False}
      try:
         FAFHStatus = self.GetCtrl_L(force = getCTRL_L)['FAFH']
         objMsg.printMsg("FAFH version: %s" %self.GetCtrl_L(force = getCTRL_L)['FAFH_VER'])
         return status[FAFHStatus]
      except:
         return status['disabled']

   def GetZoneRemapStatus(self, getCTRL_L = False):
      """
      Get ZoneRemapStatus from Ctrl-L. Returns:
         True if enabled
         False if disabled
         None if not supported
      """
      status = {'enabled':True, 'disabled':False}
      try:
         zoneRemapStatus = self.GetCtrl_L(force = getCTRL_L)['Remap']
         return status[zoneRemapStatus]
      except:
         return status['disabled']

   def GetAGBStatus(self, getCTRL_L = False):
      """
      Get AGBStatus from Ctrl-L. Returns:
         True if enabled
         False if disabled
         None if not supported
      """
      status = {'enabled':True, 'disabled':False}
      try:
         AGBStatus = self.GetCtrl_L(force = getCTRL_L)['AGB']
         return status[AGBStatus]
      except:
         return status['disabled']

   def getIdentifyBuffer(self, startByte = 0, endByte = 512):
      try:
         return self.RungetIdentifyBuffer(startByte = startByte, endByte = endByte)
      except:
         objMsg.printMsg("SP getIdentifyBuffer exception=%s" % traceback.format_exc())
         sptCmds.enableDiags()
         return self.RungetIdentifyBuffer(startByte = startByte, endByte = endByte)

   @spt
   def RungetIdentifyBuffer(self, startByte = 0, endByte = 512):
      self.gotoLevel('H')
      result = sptCmds.sendDiagCmd('I%X,%X' % (startByte, endByte-startByte), timeout=150, printResult = True)

      parsing = False
      binbuffer = []

      for idx, line in enumerate(result.splitlines()):

         if parsing:
            try:
               lineItems = binascii.unhexlify(line.replace(' ', ''))
               endByte -= len(lineItems) # Keep track until we have parsed all binary values
               binbuffer.append(lineItems)
               if endByte-startByte <= 0:
                  break
            except TypeError:
               objMsg.printMsg("Error parsing line: %s" % (line,))
               raise


         if 'total identify' in line:
            parsing = True #start on next line

      return ''.join(binbuffer)

   def getZoneInfoIOMQM(self, printResult = False, partition = 0,switchPhyCYLToLogCYL = False):
      getNumZones = self.GetNumZones()
      objMsg.printMsg("getNumZones=%s" % getNumZones)

      MaxRetry = 2
      for i in xrange(MaxRetry):
         try:
            numCyls,zones = self.dogetZoneInfoIOMQM(printResult, partition, switchPhyCYLToLogCYL)
            objMsg.printMsg("zones=%s" % zones)

            Mismatch = False
            for z in zones:
               if len(zones[z]) != getNumZones:
                  Mismatch = True

            if (Mismatch == False and self.dut.numZones == getNumZones) or testSwitch.virtualRun:
               return numCyls,zones
         except:
            objMsg.printMsg("getZoneInfoIOMQM failed. Traceback=%s" % traceback.format_exc())

      ScrCmds.raiseException(11044, "Unable to read zone info")

   def dogetZoneInfoIOMQM(self, printResult = False, partition = 0,switchPhyCYLToLogCYL = False):
      """
      partition parameter
       User Partion = 0
       System Partition = 1
       SMART OD = 2
       SMART ID = 3
      """

      objMsg.printMsg("getZoneInfoIOMQM start")
      sptCmds.gotoLevel('2')
      self.flush()
      accumulator = self.PBlock('x%x\n\n' % partition)
      data = sptCmds.promptRead(500, accumulator = accumulator, loopSleepTime = 0)
      if DEBUG > 0 or printResult: objMsg.printMsg(data)
      self.flush()
      if switchPhyCYLToLogCYL:
         zonePat = re.compile('^\s*(?P<zone>[\dA-Fa-f]+)\s+[\dA-Fa-f]+-[\dA-Fa-f]+\s+(?P<minLogCyl>[\dA-Fa-f]+)')
      else:
         zonePat = re.compile('^\s*(?P<zone>[\dA-Fa-f]+)\s+(?P<minCyl>[\dA-Fa-f]+)')
      dataLines = data.split('\n')

      numCyls = []
      zones = {}
      maxLogicalPat = re.compile('Head (?P<head>\d+), PhyCyls [\da-fA-f ]+-[\da-fA-f ]+, LogCyls [\da-fA-f ]+-(?P<MaxLogicalCyl>[\da-fA-f ]+)')

      for line in dataLines:
         line = line.strip()
         logMat = maxLogicalPat.search(line)
         if logMat:
            numCyls.append(int(logMat.groupdict()['MaxLogicalCyl'],16))
            currHead = int(logMat.groupdict()['head'],16)

         zoneMatch = zonePat.match(line)
         if zoneMatch and not(line.strip().startswith('F3')):
            tempDict = zoneMatch.groupdict()
            if len(numCyls) > 0:
               if switchPhyCYLToLogCYL:
                  zones.setdefault(currHead,{})[int(tempDict['zone'],16)] = int(tempDict['minLogCyl'],16)
               else:
                  zones.setdefault(currHead,{})[int(tempDict['zone'],16)] = int(tempDict['minCyl'],16)

      if testSwitch.virtualRun:
         numCyls = [150000,]
         if testSwitch.BF_0119058_399481_NUMCYLS_LIST_LENGTH_EQUAL_TO_NUMHEADS :
            driveInfo = self.dut.dblData.Tables('P172_DRIVE_INFO').tableDataObj()
            self.dut.numZones = int(driveInfo[-1]['NUM_USER_ZONES'])
            #hdcount = int(driveInfo[-1]['MAX_HEAD'])

            maxCylInfo = self.dut.dblData.Tables('P172_MAX_CYL_VBAR').tableDataObj()
            self.dut.maxTrack = [int(item["MAX_CYL_DEC"]) for item in maxCylInfo]
            numCyls = self.dut.maxTrack

            zones = {}
            for head in xrange(len(numCyls)):
               tmp = {}
               map(tmp.setdefault, range(0,self.dut.numZones), range(0,numCyls[head],numCyls[head]/self.dut.numZones)[:-1])
               map(zones.setdefault, [head], [tmp,])
         elif testSwitch.BF_0116843_399481_CORRECT_ZONEDATA_RETURNED_BY_GETZONEINFO_IN_VE:
            tmp = {}
            zones = {}
            map(tmp.setdefault, range(0,17), range(0,17*10000,10000))
            map(zones.setdefault, range(0,2), [tmp,]*2)
         else:
            zones = {0:[0,]*17}

      self.dut.imaxHead = len(numCyls) #imaxHead is really numHeads
      objMsg.printMsg("getZoneInfoIOMQM Setting imaxHead to %x" % self.dut.imaxHead)
      self.dut.numZones = len(zones[0])
      objMsg.printMsg("getZoneInfoIOMQM Setting numZones to %x" % self.dut.numZones)

      if self.dut.imaxHead == 0 or self.dut.numZones == -1:
         ScrCmds.raiseException(11044, "Failed to identify head-zone config of DUT.")

      return numCyls,zones

   def getZoneBERData_SMMY(self, maxRetries = 3, allowZeroRBIT = False, tLevel = None, readRetry = None, lowerBaudRate = False, printResult = True, retryPause = None):

      retry = 0
      data = ""
      #Compile the zone parsing mask.. the colums aren't auto-detecting so the order must be maintained.

      zoneTablePat = "^\s*(?P<HD_PHYS_PSN>\d+)\s*(?P<DATA_ZONE>[0-9ABCDEF]+)\s*(?P<RBIT>[\d\.]+)\s*(?P<HARD>[\d\.]+)\s*(?P<SOFT>[\d\.]+)\s*(?P<OTF>[\d\.]+)\s*(?P<RRAW>[\d\.]+)\s*(?P<WBIT>[\d\.]+)\s*(?P<WHRD>[\d\.]+)\s*(?P<WRTY>[\d\.]+)"
      zoneTablePat_sym = "^\s*(?P<HD_PHYS_PSN>\d+)\s*(?P<DATA_ZONE>[0-9ABCDEF]+)\s*(?P<RBIT>[\d\.]+)\s*(?P<HARD>[\d\.]+)\s*(?P<SOFT>[\d\.]+)\s*(?P<OTF>[\d\.]+)\s*(?P<RRAW>[\d\.]+)\s*(?P<RSYM>[\d\.]+)?\s*(?P<SYM>[\d\.]+)?\s*(?P<WBIT>[\d\.]+)\s*(?P<WHRD>[\d\.]+)\s*(?P<WRTY>[\d\.]+)"
      zoneComp = re.compile(zoneTablePat)
      zoneComp_sym = re.compile(zoneTablePat_sym)

      objMsg.printMsg("getZoneBERData_SMMY Collecting Zone BER Data", objMsg.CMessLvl.VERBOSEDEBUG)

      if testSwitch.virtualRun:
         return

      while retry < maxRetries:
         try:
            self.flush()
            # Determine drive heads & zones using getZoneInfo
            self.getZoneInfoIOMQM(printResult=True)
            drvHeads = self.dut.imaxHead
            drvZones = self.dut.numZones

            #Send ber by zone command
            data = sptCmds.execOnlineCmd('$',timeout=20, waitLoops = 100)
            zoneData = []
            dictAvgOTF = {}
            dictAvgRaw = {}
            if "Rsym" in data:
                zc = zoneComp_sym
            else:
                zc = zoneComp

            for line in data.splitlines():

               match = zc.search(line)
               if match:
                  zoneData.append(match.groupdict())
               elif line.strip().upper().startswith('SMRY:'):   # get OTF summary data per head
                  dictAvgOTF[zoneData[len(zoneData)-1]['HD_PHYS_PSN']] = line.split()[4]
                  dictAvgRaw[zoneData[len(zoneData)-1]['HD_PHYS_PSN']] = line.split()[5]
                  self.BERInfo['OTF']={'Avg':dictAvgOTF}
                  self.BERInfo['RRAW']={'Avg':dictAvgRaw}

            if len(zoneData) != (drvHeads * drvZones):
               objMsg.printMsg("\nFailure Debug Dump parsed lines (%d) doesn't match head*zones(%d*%d):\n%s" % (len(zoneData), drvHeads, drvZones, data))
               ScrCmds.raiseException(10566,"Failed to retreive ber by zone data.")
            else:
               break

         except:
            objMsg.printMsg("Traceback %s" % traceback.format_exc())
            retry += 1
            objMsg.printMsg("Serial data losss detected.")
            if lowerBaudRate==True:
               self.syncBaudRate(Baud38400)        #Lower down baud rate to 38.4K
            if retryPause:
               time.sleep(retryPause)
      else:
         ScrCmds.raiseException(10566,"Failed to retreive ber by zone data on all %s attempts." % maxRetries)

      #Once we have all data let's add it to the dblog object
      ######################## DBLOG Implementaion- Setup
      curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
      ########################
      # if testSwitch.BF_0115259_231166_SET_NULL_TLEVEL_AND_RETRIES_IN_P_FORMAT_ZONE_BER:
      if 1:
         beval = Utility.CUtility.beval
      for zoneRec in zoneData:
         if (not 1 and (not zoneRec['RBIT'] == 0 or allowZeroRBIT)) or \
            (1 and (float(zoneRec['RBIT']) > 0 or allowZeroRBIT)):
            #if testSwitch.BF_0115259_231166_SET_NULL_TLEVEL_AND_RETRIES_IN_P_FORMAT_ZONE_BER:
            if 1:
               self.dut.dblData.Tables('P_FORMAT_ZONE_ERROR_RATE').addRecord(
               {
                  'SPC_ID' : 1,
                  'OCCURRENCE' : occurrence,
                  'SEQ' : curSeq,
                  'TEST_SEQ_EVENT' : testSeqEvent,
                  'HD_PHYS_PSN' : self.dut.LgcToPhysHdMap[int(zoneRec['HD_PHYS_PSN'])],
                  'HD_LGC_PSN' : zoneRec['HD_PHYS_PSN'],
                  'DATA_ZONE' : int(zoneRec['DATA_ZONE'], 16),
                  'ECC_LEVEL' : beval(tLevel==None, '',tLevel),
                  'NUM_READ_RETRIES' : beval(readRetry==None,'',readRetry),
                  'BITS_READ_LOG10' : zoneRec['RBIT'],
                  'HARD_ERROR_RATE' : zoneRec['HARD'],
                  'SOFT_ERROR_RATE' : zoneRec['SOFT'],
                  'OTF_ERROR_RATE' : zoneRec['OTF'],
                  'RAW_ERROR_RATE' : zoneRec['RRAW'],
                  'BITS_WRITTEN_LOG10' : zoneRec['WBIT'],
                  'BITS_UNWRITEABLE_LOG10' : zoneRec['WHRD'],
                  'BITS_WITH_WRT_RETRY_LOG10' : zoneRec['WRTY'],
                  'SYMBOLS_READ_LOG10' : zoneRec.get('RSYM',''), #Null-able
                  'SYMBOL_ERROR_RATE' : zoneRec.get('SYM', ''), #Null-able
               })
            else:
               self.dut.dblData.Tables('P_FORMAT_ZONE_ERROR_RATE').addRecord(
               {
                  'SPC_ID' : 1,
                  'OCCURRENCE' : occurrence,
                  'SEQ' : curSeq,
                  'TEST_SEQ_EVENT' : testSeqEvent,
                  'HD_PHYS_PSN' : self.dut.LgcToPhysHdMap[int(zoneRec['HD_PHYS_PSN'])],
                  'HD_LGC_PSN' : zoneRec['HD_PHYS_PSN'],
                  'DATA_ZONE' : int(zoneRec['DATA_ZONE'], 16),
                  'ECC_LEVEL' : tLevel,
                  'NUM_READ_RETRIES' : readRetry,
                  'BITS_READ_LOG10' : zoneRec['RBIT'],
                  'HARD_ERROR_RATE' : zoneRec['HARD'],
                  'SOFT_ERROR_RATE' : zoneRec['SOFT'],
                  'OTF_ERROR_RATE' : zoneRec['OTF'],
                  'RAW_ERROR_RATE' : zoneRec['RRAW'],
                  'BITS_WRITTEN_LOG10' : zoneRec['WBIT'],
                  'BITS_UNWRITEABLE_LOG10' : zoneRec['WHRD'],
                  'BITS_WITH_WRT_RETRY_LOG10' : zoneRec['WRTY'],
                  'SYMBOLS_READ_LOG10' : zoneRec.get('RSYM',''), #Null-able
                  'SYMBOL_ERROR_RATE' : zoneRec.get('SYM', ''), #Null-able
               })
         else:
            if printResult:
               objMsg.printMsg("RBIT 0.. row= %s" % zoneRec)

      objMsg.printDblogBin(self.dut.dblData.Tables('P_FORMAT_ZONE_ERROR_RATE'))

      if (retry > 0) and (lowerBaudRate == True):   # Change back baud rate by doing power cycle
         objMsg.printMsg("Recovering baud rate using power cycle.")
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
         sptCmds.enableDiags()

      return zoneData,self.BERInfo['OTF'],self.BERInfo['RRAW']


   def IsOvlWiped(self):
      """
      Utility to detect drive OVL is wiped.
      """
      flashLED = False
      sptCmds.enableDiags()
      try:
         sptCmds.gotoLevel('2')
         result = bool(len(re.findall("Unable to load Diag Cmd Processor Overlay", sptCmds.sendDiagCmd('B0'))))
      except:
         flashLED = result = True  # flash LED

      objMsg.printMsg("Drive overlay wiped? %s" %result)
      return flashLED, result

   def getPackageVersion(self):
      """
      Returns CTRL_A package version info
      """
      objMsg.printMsg("Determining package information from CTRL_A.")
      sptCmds.enableDiags()

      #pat = re.compile('\s*Package Version:*\s*(?P<PackageVersion>[\.a-zA-Z0-9\-]*)')
      pat = re.compile('\s*Version:*\s*(?P<PackageVersion>[\.a-zA-Z0-9\-]*)')
      mat = pat.search(sptCmds.sendDiagCmd(CTRL_A, printResult=True))
      if mat:
         return mat.groupdict().get('PackageVersion')
      else:
         ScrCmds.raiseException(14752, "Unable to determine package version.")

   def initBIGSFirmware(self):
      objMsg.printMsg("Initialising BIGS Firmware...")
      try:
         self.enableDiags()
         self.gotoLevel('T')
         self.sendDiagCmd('Wfefe',timeout=300, printResult = True)
         objMsg.printMsg("SUCCESS - Initialise BIGS Firmware")
      except:
         objMsg.printMsg("ERROR - Cannot initialise BIGS Firmware")
      return

   def ClearBIGSFlash(self):
      objMsg.printMsg("Initialising BIGS Firmware...")
      try:
         self.enableDiags()
         self.gotoLevel('T')
         self.sendDiagCmd('Wfcfc',timeout=300, printResult = True)
         objMsg.printMsg("SUCCESS - Cleared BIGS flash")
      except:
         objMsg.printMsg("ERROR - Cannot clear BIGS flash")
      return

   def CheckForBootFlashMsg(self):
      from SerialCls import baseComm
      from Cell import theCell

      try:
         baudRate=Baud38400
         self.gotoLevel('T')
         self.sendDiagCmd('B%s' %baudRate, timeout=3, printResult=True, raiseException = 0, suppressExitErrorDump = 1)
         theCell.setBaud(baudRate)
         baseComm.flush()
         DriveOff(pauseTime=5)
         DriveOn(pauseTime=0)
         time.sleep(3)
         accumulator = baseComm.PChar(CTRL_Z)
         data = sptCmds.promptRead(10, 0, accumulator = accumulator)
         objMsg.printMsg('Data returned = %s' % data)
         del accumulator
         if testSwitch.virtualRun or "Flash" in data:
            objMsg.printMsg('Flash msg found')
            return True
         else:
            objMsg.printMsg('Warning: Flash msg not found')
      except:
         pass
      return False

   def Get_MCStatus(self, status=None):
      """ Check if drive supports media cache """
      mc_support = None
      mc_status = None
      sptCmds.enableDiags()
      sptCmds.gotoLevel('T')

      ret_data = sptCmds.sendDiagCmd('F"MediaCache"',timeout=300, printResult = True)
      if testSwitch.virtualRun:
         if status is 'enable':
            ret_data = """
               Byte:0499:       MediaCacheControl = 03
               Byte:0499:           Bit:0, ID_BLOCK_MEDIA_CACHE_SUPPORTED = 1
               Byte:0499:           Bit:1, ID_BLOCK_MEDIA_CACHE_ENABLED = 1
               """
         else:
            ret_data = """
               Byte:0499:       MediaCacheControl = 03
               Byte:0499:           Bit:0, ID_BLOCK_MEDIA_CACHE_SUPPORTED = 0
               Byte:0499:           Bit:1, ID_BLOCK_MEDIA_CACHE_ENABLED = 0
               """
      pattern = 'ID_BLOCK_MEDIA_CACHE_SUPPORTED\s+=\s+(?P<MCSUPPORTED>[\d])[\s+\S+]+ID_BLOCK_MEDIA_CACHE_ENABLED\s+=\s+(?P<MCSTATUS>[\d])'
      match = re.search(pattern, ret_data)
      if match:
         mc_support = match.groupdict()['MCSUPPORTED']
         mc_status = match.groupdict()['MCSTATUS']

      if mc_support == '1':
         if mc_status == '1':
            return True
         else:
            return False
      else:
         return None

   def enableMC(self):
      Value = 3
      sptCmds.enableDiags()
      sptCmds.gotoLevel('T')
      sptCmds.sendDiagCmd('F"MediaCacheControl",%x' % Value, timeout = 300, printResult = True)
      objPwrCtrl.powerCycle()

   def Get_NANDFlash_Param(self):
      objMsg.printMsg("Getting NAND Flash Parameters")
      max_slc_ec = None
      max_mlc_ec = None
      bad_clp_cnt = None
      retired_clp_cnt = None

      sptCmds.enableDiags()
      sptCmds.gotoLevel('O')
      ret_data = sptCmds.sendDiagCmd('b',timeout=300, printResult = True)
      pattern = 'Erase Count SLC:\s+Max\s+Min\s+Average\s+Total\s+(?P<SLC_MAX>[a-fA-F\d]+)\s+\S+\s+(?P<SLC_AVG>[a-fA-F\d]+)\s+\S+\s+Erase Count MLC:\s+Max\s+Min\s+Average\s+Total\s+(?P<MLC_MAX>[a-fA-F\d]+)\s+\S+\s+(?P<MLC_AVG>[a-fA-F\d]+)[\s+\S+]+Bad Clump count:\s+(?P<BAD_CLUMP>[a-fA-F\d]+)[\s+\S+]+Retired Clump count:\s+(?P<RETIRED_CLUMP>[a-fA-F\d]+)'
      match = re.search(pattern, ret_data)
      if match:
         max_slc_ec = match.groupdict()['SLC_MAX']
         max_mlc_ec = match.groupdict()['MLC_MAX']
         bad_clp_cnt = match.groupdict()['BAD_CLUMP']
         retired_clp_cnt = match.groupdict()['RETIRED_CLUMP']

      return max_slc_ec, max_mlc_ec, bad_clp_cnt, retired_clp_cnt

   def ShowPreAmpHeadResistance(self):
      objMsg.printMsg("Display Preamp Head Resistance")
      sptCmds.gotoLevel('7')
      sptCmds.sendDiagCmd('X', printResult = True, raiseException = 0)

   def writePPID(self, writePPID, printResult = True):
      """
      Write 23 bytes Dell PPID
      """
      sptCmds.gotoLevel('L')
      sptCmds.sendDiagCmd('W,,,1,"%s"' % (writePPID), printResult = printResult)

   def getPPID(self):
      """
      Returns Dell PPID

      F3 L>R,,,1
      DELL PPID:CN0P6R56212326240023X00
      """
      sptCmds.gotoLevel('L')
      pat = re.compile('\s*DELL PPID:*\s*(?P<PPID>[\.a-zA-Z0-9\-]*)')
      mat = pat.search(sptCmds.sendDiagCmd("R,,,1", printResult=True))
      if mat:
         return mat.groupdict().get('PPID')
      else:
         ScrCmds.raiseException(11044,"Unable to parse DellPPID info")

   def displayHornPlot(self):
      """
      Display Horn Plot

      a) ":" - Set to secondary online cmd
      b) "S?- Dump servo seek failure log
      """
      objMsg.printMsg("Display servo horn plot")
      try:
          self.GetCtrl_L(force = True)
          data = sptCmds.execOnlineCmd(':', timeout=20, waitLoops=100)
          #objMsg.printMsg("Result from ':' cmd =\n %s" % (data))
          data = sptCmds.execOnlineCmd('S', timeout=20, waitLoops=100)
          #objMsg.printMsg("Result from 'S' cmd =\n %s" % (data))
          
          # Have a bug in F3 code. The head info will not be dumped
          # The workaround is to issue :S twice
          data = sptCmds.execOnlineCmd(':', timeout=20, waitLoops=100)
          objMsg.printMsg("Result from ':' cmd =\n %s" % (data))
          data = sptCmds.execOnlineCmd('S', timeout=20, waitLoops=100)
          objMsg.printMsg("Result from 'S' cmd =\n %s" % (data))

          startIndex = data.find('Current Horn Plot Data')
          endIndex = data.find('Horn Plot Log')
          data = data[startIndex+23:endIndex]
          
          ScriptComment('P_HORN_PLOT1:', writeTimestamp = 0)
          ScriptComment('OCLIM_OFFSET1 COUNT1 OCLIM_OFFSET2 COUNT2', writeTimestamp = 0)
          regExpress = '[0-9\-%]{3,}\s+\d+.*'
          for line in data.splitlines():
             if re.search(regExpress, line):
                ScriptComment('%13s%7s%13s%7s'%tuple(line.split()), writeTimestamp = 0)
          
          plot2Data = data[:data.find('Disc')]
          ScriptComment('P_HORN_PLOT2:', writeTimestamp = 0)
          ScriptComment('Head   ERRORS NUM_WRITE_SEEKS', writeTimestamp = 0)
          regExpress = '\d+\s+\d+\s+\d+.*'
          for line in plot2Data.splitlines():
             if re.search(regExpress, line):
                ScriptComment('%4s%9s%16s'%tuple(line.split()), writeTimestamp = 0)
                
          plot3Data = data[data.find('Disc'):]
          ScriptComment('P_HORN_PLOT3:', writeTimestamp = 0)
          ScriptComment('SEGMENT ERRORS NUM_WRITE_SEEKS', writeTimestamp = 0)
          regExpress = '\d+\s+\d+\s+\d+.*'
          for line in plot3Data.splitlines():
             if re.search(regExpress, line):
                ScriptComment('%7s%7s%16s'%tuple(line.split()), writeTimestamp = 0)
          ScriptComment('', writeTimestamp = 0)
      except:
          objMsg.printMsg('Exception from horn plot display')
          pass
         
