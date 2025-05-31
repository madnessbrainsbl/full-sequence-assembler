#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: base Interface calibration states
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_MQM.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_MQM.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#

from Constants import *
from TestParamExtractor import TP
import MessageHandler as objMsg
import ScrCmds
import sptCmds
from PowerControl import objPwrCtrl
from Process import CProcess
from State import CState
from Exceptions import CRaiseException
from serialScreen import sptDiagCmds
import Utility
import re
import time
from ICmdFactory import ICmd
from Rim import objRimType

if testSwitch.FE_0158153_231166_P_ALL_SPT_MQM_NO_ATA_RDY:
   ataReadyCheck = False
else:
   ataReadyCheck = True

###########################################################################################################
class CMQM(CState):
   """
      Muskie NL MQM
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut
      self.LBAsAddedToAltList = 0

   #-------------------------------------------------------------------------------------------------------
   def combineUpperLower(self, tMSBsLSBs):
      """
      Combine a tuple of 2 Most Significant Bytes and 2 Least Significant Bytes to a single integer value.
      """
      MSBs = tMSBsLSBs[0] & 0xFFFF
      LSBs = tMSBsLSBs[1] & 0xFFFF
      FourByteNum = (MSBs << 16) + LSBs
      return (FourByteNum)

   #-------------------------------------------------------------------------------------------------------
   def diagAddLBAstoAltList(self, inList,):
      """
      Add LBA to Alternated Sector List from list of diag errors from D10 output.
      Entries whose key has the specified value are merged.
      Returns inList with merged entries removed.
      """
      outList = [] # Currently does nothing
      LBA_List = [] # LBA's that will be added to alternated sector list

      rowsToRemove = []
      for row in inList: # clean out errors that we intend to ignore and not merge.
         #LBA_List.append(row['LBA'])
         for errorType in self.Ignore_Errors:
            if row['RWERR'].find(errorType) >= 0:
               rowsToRemove.append(row)
               break
      for row in rowsToRemove:
         inList.pop(inList.index(row))

      for row in inList: # only add items to DiagErrorList if they are not OK
         LBA_List.append(row['LBA'])
         if not testSwitch.FE_0121012_399481_SUBSTRING_MATCH_MQM_OK_ERRORS:
            if row['RWERR'] not in self.OK_Errors:
               self.DiagErrorList.append(row)
         else:
            errorOK = False
            for errorType in self.OK_Errors:
               if row['RWERR'].find(errorType) >= 0:
                  errorOK = True
            if not errorOK:
               self.DiagErrorList.append(row)

      ErrorCountByRWERR_Type = {}
      for row in self.DiagErrorList:
         if row['RWERR'] in ErrorCountByRWERR_Type.keys():
            ErrorCountByRWERR_Type[row['RWERR']] += 1
         else:
            ErrorCountByRWERR_Type[row['RWERR']] = 1

      fail = False
      failureDict = {}
      for RWERR_Type in ErrorCountByRWERR_Type.keys():
         if ErrorCountByRWERR_Type[RWERR_Type] > self.perRWERR_TypeLimit:
            fail = True
            failureDict[RWERR_Type] = ErrorCountByRWERR_Type[RWERR_Type]

      if fail:
         for RWERR_Type in sorted(failureDict.keys()):
            objMsg.printMsg("%s errors: %d, greater than limit %d"%(RWERR_Type, failureDict[RWERR_Type], self.perRWERR_TypeLimit,))
         ScrCmds.raiseException(13422, "Logged R/W Errors greater than limit %d"%(self.perRWERR_TypeLimit,))

      if LBA_List:
         objMsg.printMsg("About to add following LBAs to Alternated Sector List: %s"%(str(LBA_List),))
         for LBA in LBA_List:
            sptCmds.gotoLevel('2')
            sptCmds.sendDiagCmd('F%s,A1'%(LBA,), printResult = True)
            if testSwitch.FE_0123556_405392_PERFORM_ZERO_WRITE_AFTER_ALT_SECTOR:
               self.oSerial.setZeroPattern()
               sptCmds.gotoLevel('A')
               sptCmds.sendDiagCmd('W%s'%(LBA,), printResult = True)
         sptCmds.gotoLevel('T')
         sptCmds.sendDiagCmd("V4", timeout = 30, printResult = True, loopSleepTime = 0)
         if testSwitch.FE_0122102_399481_GET_CRITICAL_EVENTS_AFTER_G_LIST:
            sptCmds.gotoLevel('1')
            self.oSerial.getCriticalEventLog() # assumes we're in level 1
            sptCmds.gotoLevel('2')

      return outList

   #-------------------------------------------------------------------------------------------------------
   def diagButterflySeeks(self, startPosition = 0.0, endPosition = 1.0, numMinutes = 60):
      """
      4>v Butterfly Seeks.
      """
      objMsg.printMsg(('-'*17+' Start Butterfly Seeks %d Minutes '+17*'-')%(numMinutes))
      startPosition = self.forceValueWithinRange(startPosition, validRange = (0.0, 1.0))
      endPosition = self.forceValueWithinRange(endPosition, validRange = (0.0, 1.0))
      startPosition = int(startPosition * self.lMaxCylinders[0])
      endPosition = int(endPosition * self.lMaxCylinders[0])

      objPwrCtrl.powerCycle(baudRate = Baud38400, ataReadyCheck = ataReadyCheck)
      self.oSerial.enableDiags()
      sptCmds.gotoLevel('4')
      sptCmds.sendDiagCmd('v%X,%X,%X,1' % (startPosition, endPosition, numMinutes*60), timeout = int(round(numMinutes * 1.5 * 60)), printResult = True) # quick ~ 0.1 second rand seek to verify this test works on drive
      objPwrCtrl.powerCycle(baudRate = Baud38400, ataReadyCheck = ataReadyCheck)
      objMsg.printMsg(('-'*17+' End Butterfly Seeks %d Minutes '+17*'-')%(numMinutes))

   #-------------------------------------------------------------------------------------------------------
   def diagDisplayGList(self, spc_id):
      """
      Display the Alternated Sectors list using the V4 diag command.
      """
      objMsg.printMsg(('-'*17+' Start Display G List %d '+17*'-')%(spc_id))

      objMsg.printMsg("Number of LBAs added to Alternated Sectors List: %d"%(self.LBAsAddedToAltList,))
      seq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)

      objPwrCtrl.powerCycle(baudRate = Baud38400, ataReadyCheck = ataReadyCheck)
      sptCmds.enableDiags()
      reassignData = self.oSerial.dumpReassignedSectorList()
      rListSectors, rListWedges = self.oSerial.dumpRList()
      if testSwitch.FE_0122102_399481_GET_CRITICAL_EVENTS_AFTER_G_LIST:
         self.oSerial.getCriticalEventLog() # assumes we're in level 1
      self.dut.dblData.Tables('P000_DEFECTIVE_PBAS').addRecord(
         {
         'SPC_ID'          : spc_id,
         'OCCURRENCE'      : occurrence,
         'SEQ'             : seq,
         'TEST_SEQ_EVENT'  : testSeqEvent,
         'NUMBER_OF_PBAS'  : reassignData['NUMBER_OF_TOTALALTS'],
         'RLIST_SECTORS'   : rListSectors,
         'RLIST_WEDGES'    : rListWedges,
         })

      objMsg.printDblogBin(self.dut.dblData.Tables('P000_DEFECTIVE_PBAS'))
      objPwrCtrl.powerCycle(baudRate = Baud38400, ataReadyCheck = ataReadyCheck)
      objMsg.printMsg(('-'*17+' End Display G List %d '+17*'-')%(spc_id))

   #-------------------------------------------------------------------------------------------------------
   def diagFullPackRead(self, ber_spc_id = 1, SMThresh = None):
      """
      Do a full pack read with BER reporting.  If SMTHresh is defined then the sync mark threshold may be lowered.
      """
      objMsg.printMsg(('-'*17+' Start Diag FullPackRead With BER '+17*'-'))
      self.diagReadWritePortionOfLBAs(RWMode = 'Read', startPosition = 0.0,  endPosition = 1.0, DataPattern = None, ber_spc_id = ber_spc_id, SMThresh = SMThresh)
      objMsg.printMsg(('-'*17+' End Diag FullPackRead With BER '+17*'-'))

   #-------------------------------------------------------------------------------------------------------
   def diagFullPackWrite(self, ber_spc_id = 1, SMThresh = None):
      """
      Do a full pack Write with BER reporting.  If SMTHresh is defined then the sync mark threshold may be lowered.
      """
      objMsg.printMsg(('-'*17+' Start Diag FullPackWrite With BER '+17*'-'))
      self.diagReadWritePortionOfLBAs(RWMode = 'Write', startPosition = 0.0,  endPosition = 1.0, DataPattern = 0x00000000, ber_spc_id = ber_spc_id, SMThresh = SMThresh)
      objMsg.printMsg(('-'*17+' End Diag FullPackWrite With BER '+17*'-'))

   #-------------------------------------------------------------------------------------------------------
   def diagFullPackTrack(self, trackMode = 'Odd', RWMode = 'Write', CylRange = {'mode':'All'}, DataPattern = 0x87654321, ber_spc_id = 1, berByHead = False):
      """
      Does a read or write operation, using the specified pattern, on either the full pack, or a specified range of track.
      The specified range may be a given range, or a given number of tracks at the OD, Md, or ID.
      BER Data is gathered.
      """
      objMsg.printMsg(('-'*17+' Start %s Pack %s Track %s '+17*'-')%(CylRange['mode'], trackMode, RWMode))
      mode = RWMode[0]

      if mode not in ('W','R'):
         ScrCmds.raiseException(11044, "Invalid mode %s requested" % (mode))
      elif trackMode not in ('Odd', 'Even'):
         ScrCmds.raiseException(11044, "Invalid trackMode %s requested" % (trackMode))

      objPwrCtrl.powerCycle(baudRate = Baud38400, ataReadyCheck = ataReadyCheck)
      sptCmds.enableDiags()
      if DataPattern != None:
         self.oSerial.SetRepeatingPattern(DataPattern)
      self.oSerial.initDefectLog(printResult = False) #
      self.oSerial.setErrorLogging(enable = True, printResult = False)    # Enable error logging for all operations
      self.oSerial.enableRWStats(printResult = False)

      self.diagRWTracksCHS(mode = mode, option = trackMode, CylRange = CylRange)
      if not berByHead:
         if testSwitch.FE_0124554_399481_GET_BER_DATA_USING_LEVEL2_B_CMD and testSwitch.BF_0157187_231166_P_FIX_BER_DATA_ZONE_PARSE_RETURN:
            self.oSerial.getBERDataByZone(spc_id = ber_spc_id)
         else:
            self.oSerial.getZoneBERData(maxRetries = 5, spc_id = ber_spc_id, printResult = False, retryPause = 30)
      else:
         self.diagGetBERDataByHead(printResult = True, ber_spc_id = ber_spc_id)


      loggedErrors = self.oSerial.getActiveErrorLog()
      loggedErrors = self.diagAddLBAstoAltList(loggedErrors)

      objMsg.printMsg("\nTotal RW errors logged during %s %s : %d" % (trackMode, RWMode, len(loggedErrors)))
      for entry in loggedErrors:
         objMsg.printMsg("\nDIAGERR: %s"%(entry["DIAGERR"]))

      objPwrCtrl.powerCycle(baudRate = Baud38400, ataReadyCheck = ataReadyCheck)
      objMsg.printMsg(('-'*17+' End %s Pack %s Track %s '+17*'-')%(CylRange['mode'], trackMode, RWMode))
      return len(loggedErrors)

   #-------------------------------------------------------------------------------------------------------
   def diagFSEScreen(self, loops = 3, lbaFraction = 0.10, WrCurIncrease = 4, tweaks = {}, wrtErrLimit = None, rdErrLimit = 0, DataPattern = 0xFEDC, ber_spc_id_start = 20):
      """
      Repeatedly write and read the outer lbaFraction of the drive and fail for hard errors.
      """
      objMsg.printMsg(('-'*17+' Start FSE screen. loops = %d, lbaFraction = %f'+17*'-')%(loops, lbaFraction,))
      objPwrCtrl.powerCycle(baudRate = Baud38400, ataReadyCheck = ataReadyCheck)
      sptCmds.enableDiags()

      if testSwitch.FE_0126515_399481_WRCUR_TWEAK_IN_FSE_SCREEN and not testSwitch.FE_0127688_399481_RAP_AFH_PREAMP_TWEAK_IN_FSE_SCREEN:
         preAmpDataByZone = self.oSerial.getPreampParms(printResult = True)
         preAmpDataByZone = Utility.CUtility.filterDictByKey(preAmpDataByZone, ("WrCur",), keyAction = "keep")
         newPreampVals = Utility.CUtility.operateOnDictVals(preAmpDataByZone, lambda x : x + WrCurIncrease)
         # create function to call prior to each R/W to set new preamp DAC vals.
         preFuncPtr = lambda : self.oSerial.setPreampParms(newPreampVals, printResult = False, verify = True)

      elif testSwitch.FE_0127688_399481_RAP_AFH_PREAMP_TWEAK_IN_FSE_SCREEN:
         """
         tweaks dictionary defines what parm to modify, and by how much.
         example: tweaks = {"WrCur":4, "TargWrClr":-1}
         currently supports
         (P2=0A) RAP Tuned Preamp Parms:    WrCur, WrDamp, WrDampDur, HtRng,
         (P2=0F) RAP AFH Head/Zone Parms:   WplusHtClr, RHtClr, TargWrClr, TargPreClr, TargRdClr, TargMaintClr
         """
         newValDicts = []
         preFuncPtr = None
         if tweaks:
            parmDataList = []
            tweakKeySet = set(tweaks.keys())
            modeKeyDict = {
               "0A"  : set(["WrCur", "WrDamp", "WrDampDur", "HtRng"]),
               "0F"  : set(["WplusHtClr", "RHtClr", "TargWrClr", "TargPreClr", "TargRdClr", "TargMaintClr"]),
               }
            # get data for each mode only if required.
            for mode, keySet in modeKeyDict.items():
               if keySet - tweakKeySet:
                  parmDataList.append(self.oSerial.getRAP_Parms(P2_mode = mode, printResult = True))

            combinedParms = Utility.CUtility.combineListOfHeadZoneDicts(parmDataList, self.dut.imaxHead, self.dut.numZones)
            # keep only the entries that will be changing
            combinedParms = Utility.CUtility.filterDictByKey(combinedParms, tweakKeySet, keyAction = "keep")
            # now update each value according to the desired delta
            for key, value in tweaks.items():
               combinedParms = Utility.CUtility.operateOnDictVals(combinedParms, lambda x : x + value, lambda k, v : k == key)
            # create function to call prior to each R/W to set new preamp DAC vals.
            preFuncPtr = lambda : self.oSerial.setRAP_Parms(combinedParms, printResult = False, verify = True)

      self.oSerial.SetRepeatingPattern(DataPattern)
      for testLoop in xrange(loops):
         if not (testSwitch.FE_0126515_399481_WRCUR_TWEAK_IN_FSE_SCREEN or testSwitch.FE_0127688_399481_RAP_AFH_PREAMP_TWEAK_IN_FSE_SCREEN):
            objMsg.printMsg("Loop %d write."%(testLoop,))
            self.diagReadWritePortionOfLBAs(RWMode = 'Write', startPosition = 0.0,  endPosition = lbaFraction, DataPattern = None, ber_spc_id = ber_spc_id_start + testLoop*2, altLBAs = False, berByHead = True)
            objMsg.printMsg("Loop %d read."%(testLoop,))
            self.diagReadWritePortionOfLBAs(RWMode = 'Read', startPosition = 0.0,  endPosition = lbaFraction, DataPattern = None, ber_spc_id = ber_spc_id_start + testLoop*2+1 , altLBAs = True, berByHead = True)
         else:
            objMsg.printMsg("Loop %d write."%(testLoop,))
            self.diagReadWritePortionOfLBAs(RWMode = 'Write', startPosition = 0.0,  endPosition = lbaFraction, DataPattern = None, ber_spc_id = ber_spc_id_start + testLoop*2, altLBAs = False, berByHead = True, preFunc = preFuncPtr)
            objMsg.printMsg("Loop %d read."%(testLoop,))
            self.diagReadWritePortionOfLBAs(RWMode = 'Read', startPosition = 0.0,  endPosition = lbaFraction, DataPattern = None, ber_spc_id = ber_spc_id_start + testLoop*2+1 , altLBAs = True, berByHead = True, preFunc = preFuncPtr)
      objMsg.printMsg(('-'*17+' End FSE screen. loops = %d, lbaFraction = %f'+17*'-')%(loops, lbaFraction,))

   #-------------------------------------------------------------------------------------------------------
   def diagGetBERDataByHead(self, printResult = True, ber_spc_id = None):
      """
      Returns BER data like so:
      {0: {'Hard': '7.3', 'Wbit': '0.0', 'Rsym': '6.4', 'OTF': '7.3',
         'Rbit': '7.3', 'Raw': '6.5', 'Sym': '5.6', 'Wrty': '0.0',
         'Soft': '7.3', 'Hd': '0', 'Whrd': '0.0'}, 1: {'Hard': '0.0',
         'Wbit': '0.0', 'Rsym': '0.0', 'OTF': '0.0', 'Rbit': '0.0',
         'Raw': '0.0', 'Sym': '0.0', 'Wrty': '0.0', 'Soft': '0.0', 'Hd': '1',
         'Whrd': '0.0'}}
      """
      pat = re.compile(
         "Hd[ \t]+(?P<Hd>[\da-fA-F])[ \t]+"
         "(?P<Rbit>[\d.]+)[ \t]+"
         "(?P<Hard>[\d.]+)[ \t]+"
         "(?P<Soft>[\d.]+)[ \t]+"
         "(?P<OTF>[\d.]+)[ \t]+"
         "(?P<Raw>[\d.]+)[ \t]+"
         "(?P<Rsym>[\d.]+)[ \t]+"
         "(?P<Sym>[\d.]+)[ \t]+"
         "(?P<Wbit>[\d.]+)[ \t]+"
         "(?P<Whrd>[\d.]+)[ \t]+"
         "(?P<Wrty>[\d.]+)")

      if testSwitch.virtualRun:
         data =      ["       Rbit  Hard  Soft  OTF   Raw   Rsym  Sym   Wbit  Whrd  Wrty\n"]
         data.extend(["Hd %X   7.3   7.3   7.3   7.3   6.5   6.4   5.6   0.0   0.0   0.0\n" % head for head in xrange(self.dut.imaxHead)])
         data = "".join(data)
      else:
         data = sptCmds.execOnlineCmd('`', timeout = 120, waitLoops = 100)

      if printResult:
         objMsg.printMsg("Result from '`' command:\n %s" % (data,))

      output = {}
      for line in data.splitlines():
         match = pat.search(line)
         if match:
            output[int(match.group("Hd"), 16)] = match.groupdict()

      if testSwitch.FE_0121994_399481_REPORT_BER_DATA_BY_HEAD_IN_MQM:
         curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
         if ber_spc_id != None:
            for headKey in sorted(output.keys()):
               headBERData = output[headKey]
               self.dut.dblData.Tables('P_HEAD_ERROR_RATE').addRecord(
                  {
                  'SPC_ID'                      : ber_spc_id,
                  'OCCURRENCE'                  : occurrence,
                  'SEQ'                         : curSeq,
                  'TEST_SEQ_EVENT'              : testSeqEvent,
                  'HD_PHYS_PSN'                 : headBERData['Hd'],
                  'HD_LGC_PSN'                  : headBERData['Hd'],
                  'BITS_READ_LOG10'             : headBERData['Rbit'],
                  'HARD_ERROR_RATE'             : headBERData['Hard'],
                  'SOFT_ERROR_RATE'             : headBERData['Soft'],
                  'OTF_ERROR_RATE'              : headBERData['OTF'],
                  'RAW_ERROR_RATE'              : headBERData['Raw'],
                  'SYMBOLS_READ_LOG10'          : headBERData['Rsym'],
                  'SYMBOL_ERROR_RATE'           : headBERData['Sym'],
                  'BITS_WRITTEN_LOG10'          : headBERData['Wbit'],
                  'BITS_UNWRITEABLE_LOG10'      : headBERData['Whrd'],
                  'BITS_WITH_WRT_RETRY_LOG10'   : headBERData['Wrty'],
                  })
            objMsg.printDblogBin(self.dut.dblData.Tables('P_HEAD_ERROR_RATE'))
      return output

   #-------------------------------------------------------------------------------------------------------
   def diagGetCurrentOclim(self, printResult = True):
      """
      returns dict of head:oclim values from 8>C15
      {0:0x241, 1:0x23D}
      """
      startLevel = sptCmds.currLevel
      pat = re.compile(
         "[ \t]*(?P<Hd>[\da-fA-F]{2})[ \t]+"
         "(?P<XThresh>[\da-fA-F]{4})"
         )

      if testSwitch.virtualRun:
         data = "Head  XThresh  VThresh\n"
         for head in xrange(self.dut.imaxHead):
            data += "%.2X    0241\n" % head
      else:
         sptCmds.gotoLevel('8')
         data = sptCmds.sendDiagCmd('C15', printResult = printResult)

      output = {}
      for line in data.splitlines():
         match = pat.search(line)
         if match:
            output[int(match.group("Hd"), 16)] = int(match.group("XThresh"), 16)
      if printResult:
         for head in sorted(output.keys()):
            objMsg.printMsg("Original Write fault threshold on head %d : %.4f" % (head, float(output[head]/4096.0),))
      sptCmds.gotoLevel(startLevel)
      return output

   #-------------------------------------------------------------------------------------------------------
   def diagGetCurrentVTPI(self,):
      """
      get variable TPI multiplier for current head/track.
      return int, (values is Q14)
      """
      servoAddressPat = re.compile("Servo Symbol Table Index [\da-fA-F]{4} Value (?P<Address>[\da-fA-F]{8})")
      servoDataPat = re.compile("Servo Data RAM Addr [\da-fA-F]{8} RAM Data (?P<RAMData>[\da-fA-F]{4})")

      startLevel = sptCmds.currLevel
      if testSwitch.virtualRun:
         servoData = """
         Servo Data RAM Addr 04001874 RAM Data 3FC9
         """
      else:
         sptCmds.gotoLevel('5')
         addressData = sptCmds.sendDiagCmd('iB3', printResult = DEBUG) # Servo Sector Table 179
         addressMatch = servoAddressPat.search(addressData)
         servoData = sptCmds.sendDiagCmd('R%s'%addressMatch.group("Address"), printResult = DEBUG)
      servoDataMatch = servoDataPat.search(servoData)
      sptCmds.gotoLevel(startLevel)
      return int(servoDataMatch.group("RAMData"), 16)

   #-------------------------------------------------------------------------------------------------------
   def diagGetMaxCylinders(self, printResult = True):
      """
      Returns a list of max cylinders for each head.
      """
      objPwrCtrl.powerCycle(baudRate = Baud38400, ataReadyCheck = ataReadyCheck)
      self.oSerial.enableDiags()
      if testSwitch.FE_0154440_007955_P_SYNC_BAUD_RATE_IN_MQM_GET_MAX_CYLS:
         self.oSerial.syncBaudRate()
      numCyls, zones = self.oSerial.getZoneInfo(printResult = printResult)
      objMsg.printMsg("numCyls = %s"%(str(numCyls),))
      objPwrCtrl.powerCycle(baudRate = Baud38400, ataReadyCheck = ataReadyCheck)
      return numCyls, zones

   #-------------------------------------------------------------------------------------------------------
   def diagGetMaxLBA(self, ):
      """
      Parses the number of LBAs from CTRL_L diag, maxLBA = numLBAs - 1
      """
      objPwrCtrl.powerCycle(baudRate = Baud38400, ataReadyCheck = ataReadyCheck)
      self.oSerial.enableDiags()
      data = sptCmds.sendDiagCmd(CTRL_L, altPattern = 'PreampType:', printResult = False)
      if testSwitch.virtualRun:
         data = 'HDA SN: 9WJ00766, RPM: 7202, Wedges: 1A0, Heads: 2, Lbas: 3A386030, PreampType: 58 01'
      sptCmds.sendDiagCmd('/\r', altPattern = 'T>', printResult = False)
      # Get max LBA
      match = re.search('Lbas:', data)
      lbas = data[match.end():].split(',')[0]
      lbas = int(lbas, 16)
      maxLBA = lbas - 1
      objMsg.printMsg("maxLBA = %d"%(maxLBA,))
      objPwrCtrl.powerCycle(baudRate = Baud38400, ataReadyCheck = ataReadyCheck)
      return maxLBA

   #-------------------------------------------------------------------------------------------------------
   def diagInit(self, Version = '', OK_Errors = [], Ignore_Errors = [], perRWERR_TypeLimit = 0, printResult = True):
      """
      Initialize MQM for diag operations using diag commands.
      """
      self.DiagErrorList = []
      self.maxLBA = self.diagGetMaxLBA()
      self.lMaxCylinders, self.zones = self.diagGetMaxCylinders(printResult = printResult)
      self.OK_Errors = OK_Errors
      self.Ignore_Errors = Ignore_Errors
      self.perRWERR_TypeLimit = perRWERR_TypeLimit
      objMsg.printMsg("MQM Version is %s" % (Version,))

   #-------------------------------------------------------------------------------------------------------
   def diagPowerCycles(self, numberPowerCycles, numLULperPowerCycle):
      """
      Do x number of power cycles with y numbers of LUL after each power cycle.
      """
      objMsg.printMsg(('-'*17+' Start Power cycle %dX '+17*'-')%(numberPowerCycles,))
      for powerCycleLoop in xrange(numberPowerCycles):
         objPwrCtrl.powerCycle(baudRate = Baud38400, ataReadyCheck = ataReadyCheck)
         if numLULperPowerCycle > 0:
            sptCmds.enableDiags()
            sptCmds.gotoLevel('3')
            for LUL_Loop in xrange(numLULperPowerCycle):
               sptCmds.sendDiagCmd('b1', printResult = True) # UNLOAD_HEADS_CMD, place head on ramp
               sptCmds.sendDiagCmd('b0', printResult = True) # LOAD_HEADS_CMD, place head over disc

      objMsg.printMsg(('-'*17+' End Power cycle %dX '+17*'-')%(numberPowerCycles,))

   #-------------------------------------------------------------------------------------------------------
   def diagRandomEvenOddReadWriteTracks(self, numMinutesPerHead = 30, DataPattern = 0x11111111, startTrack = 0x1D4C0, endTrack = 0x203A0, oclimFloat = 0.18, loops = 10, mode = "Even"):
      """
      Random writes of weven or odd tracks in on given track range of drive.
      """
      oclim = int(round(oclimFloat*4096.0))
      durationMinutes = int(numMinutesPerHead*len(self.lMaxCylinders))
      objMsg.printMsg(('-'*17+' Start Random Write, OCLIM 0x%X = %.4f, %d loops %d minutes '+17*"-")%(oclim, oclimFloat, loops, durationMinutes))
      if testSwitch.auditTest and testSwitch.FE_0123872_399481_MQM_AUDITTEST_SKIP_INCOMPATIBLE_PARTS:
         objMsg.printMsg('AuditTest, skipping diagRandomEvenOddReadWriteTracks.')
         return
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, baudRate = Baud38400, ataReadyCheck = ataReadyCheck)
      printResult = DEBUG
      self.oSerial.enableDiags()
      self.oSerial.SetRepeatingPattern(DataPattern)
      sptCmds.gotoLevel('8')

      sptCmds.sendDiagCmd('C15,%X'%(oclim,), printResult = printResult)
      sptCmds.gotoLevel('2')
      for loopcount in xrange(loops):
         objMsg.printMsg("Executing Loop: %d" % (loopcount,))
         for head in xrange(len(self.lMaxCylinders)):
            sptCmds.sendDiagCmd('A8,%X,,%X' % (startTrack, head,), printResult = printResult) # set min cyl
            sptCmds.sendDiagCmd('A9,%X,,%X' % (endTrack, head,), printResult = printResult) # set max cyl
         if mode == "Even": # Rnd Start Sctr, Even Cylndr, Rnd Cylndr/Hd, All Clndr, All Hd
            sptCmds.sendDiagCmd('A117', printResult = printResult)
         elif mode == "Odd": # Rnd Start Sctr, Odd Cylndr, Rnd Cylndr/Hd, All Clndr, All Hd
            sptCmds.sendDiagCmd('A127', printResult = printResult)
         else:
            ScrCmds.raiseException(11044, 'Invalid mode "%s" requested' % mode)

         self.oSerial.initDefectLog(printResult = False)
         self.oSerial.setErrorLogging(enable = True, printResult = False)
         self.oSerial.enableRWStats(printResult = False)
         objMsg.printMsg("Starting Random Writes")

         sptCmds.gotoLevel('2')

         sptCmds.sendDiagCmd('L11') # Loop: no display errors, continue on error.

         try:
            sptCmds.sendDiagCmd('W,,,,1', timeout= durationMinutes * 60, maxRetries = 0, printResult = printResult, loopSleepTime = 30)
         except CRaiseException, inst:
            if DEBUG:
               objMsg.printMsg("CRaiseException triggered... %s" % (inst,))
            if inst[0][2] != 10566: #looking for timeout.. we expect one
               raise

         for retryCount in xrange(10):
            try:
               sptCmds.sendDiagCmd(CR, timeout = 30, altPattern='>') # Ctrl-Z to break out of diag loop
               break
            except:
               pass
         else:
            ScrCmds.raiseException(10566, "Timeout when trying to abort random operations.")

         objMsg.printMsg("Starting Read of Test Space")

         sptCmds.sendDiagCmd('AD', printResult = printResult) # reset test space

         for head in xrange(len(self.lMaxCylinders)):
            sptCmds.sendDiagCmd('A8,%X,,%X' % (startTrack, head,), printResult = printResult) # set min cyl
            sptCmds.sendDiagCmd('A9,%X,,%X' % (endTrack, head,), printResult = printResult) # set max cyl
         sptCmds.gotoLevel('2')
         sptCmds.sendDiagCmd('L51', printResult = printResult) # Loop: Enable Stop on Test Space Wrapped, do not display errors, continue on error
         sptCmds.sendDiagCmd('R,,,,1', timeout = self.dut.imaxHead * 7200, printResult = printResult, loopSleepTime = 0.5)
         self.diagGetBERDataByHead(printResult = True)
         loggedErrors = self.oSerial.getActiveErrorLog()
         loggedErrors = self.oSerial.filterListofDicts(loggedErrors, 'DIAGERR', '00000006', include = False)
         self.diagAddLBAstoAltList(loggedErrors)
         ## cleanup
         sptCmds.gotoLevel('2')
         sptCmds.sendDiagCmd('L51', printResult = printResult) # Loop: Enable Stop on Test Space Wrapped, do not display errors, continue on error
         sptCmds.sendDiagCmd('W,,,,1', timeout = self.dut.imaxHead * 7200, printResult = printResult, loopSleepTime = 0.5)

      objPwrCtrl.powerCycle(baudRate = Baud38400, ataReadyCheck = ataReadyCheck)
      objMsg.printMsg(('-'*17+' End Random Write, OCLIM 0x%X = %.4f, %d loops %d minutes '+17*"-")%(oclim, oclimFloat, loops, durationMinutes))

   #-------------------------------------------------------------------------------------------------------
   def diagRandomSeeks(self, numMinutes):
      """
      Call the randseeks function with uses the access time diag to do random seeks for a specified time.
      """
      objMsg.printMsg(('-'*17+' Start Random Seeks %d Minutes '+17*'-')%(numMinutes))
      objPwrCtrl.powerCycle(baudRate = Baud38400, ataReadyCheck = ataReadyCheck)
      self.oSerial.enableDiags()
      self.oSerial.randSeeks(duration = numMinutes)
      objPwrCtrl.powerCycle(baudRate = Baud38400, ataReadyCheck = ataReadyCheck)
      objMsg.printMsg(('-'*17+' End Random Seeks %d Minutes '+17*'-')%(numMinutes))

   #-------------------------------------------------------------------------------------------------------
   def diagRandomWrite(self, numMinutes = 60, DataPattern = 0x12345678, ber_spc_id = 1, berByHead = False, sectorCount = 256, altBadSectors = 1):
      """
      Call the randLBAs function with uses do random writes for a specified time, with the specified pattern.
      """
      if self.dut.powerLossEvent:
         objMsg.printMsg("Write Full surface.")
         self.diagFullPackWrite(dict(ber_spc_id = 15, SMThresh = '0006'))

      objMsg.printMsg(('-'*17+' Start Random Write full surface %d minutes '+17*"-")%(numMinutes))
      objPwrCtrl.powerCycle(baudRate = Baud38400, ataReadyCheck = ataReadyCheck)
      self.oSerial.enableDiags()
      self.oSerial.SetRepeatingPattern(DataPattern)
      self.oSerial.initDefectLog(printResult = False)
      self.oSerial.setErrorLogging(enable = True, printResult = False)
      self.oSerial.enableRWStats(printResult = False)
      self.oSerial.randLBAs(startLBA = 0, endLBA = self.maxLBA, mode = 'W', duration = numMinutes, sectorCount = sectorCount)
      if not berByHead:
         if testSwitch.FE_0124554_399481_GET_BER_DATA_USING_LEVEL2_B_CMD and testSwitch.BF_0157187_231166_P_FIX_BER_DATA_ZONE_PARSE_RETURN:
            self.oSerial.getBERDataByZone(spc_id = ber_spc_id)
         else:
            self.oSerial.getZoneBERData(maxRetries = 10, lowerBaudRate = True, spc_id = ber_spc_id, printResult = False, retryPause = 30)
      else:
         self.diagGetBERDataByHead(printResult = True, ber_spc_id = ber_spc_id)

      loggedErrors = self.oSerial.getActiveErrorLog()
      loggedErrors = self.oSerial.filterListofDicts(loggedErrors, 'DIAGERR', ['00000006'], include = False)
      if altBadSectors:
         loggedErrors = self.diagAddLBAstoAltList(loggedErrors)

      objPwrCtrl.powerCycle(baudRate = Baud38400, ataReadyCheck = ataReadyCheck)
      objMsg.printMsg(('-'*17+' End Random Write full surface %d minutes '+17*'-')%(numMinutes))

   #-------------------------------------------------------------------------------------------------------
   def diagRandomRead(self, numMinutes = 60, ber_spc_id = 1, berByHead = False, sectorCount = 256, altBadSectors = 1):
      """
      Call the randLBAs function with uses do random reads for a specified time
      """

      objMsg.printMsg(('-'*17+' Start Random Read full surface %d minutes '+17*"-")%(numMinutes))
      objPwrCtrl.powerCycle(baudRate = Baud38400, ataReadyCheck = ataReadyCheck)
      self.oSerial.enableDiags()
      self.oSerial.initDefectLog(printResult = False)
      self.oSerial.setErrorLogging(enable = True, printResult = False)
      self.oSerial.enableRWStats(printResult = False)
      self.oSerial.randLBAs(startLBA = 0, endLBA = self.maxLBA, mode = 'R', duration = numMinutes, sectorCount = sectorCount)
      if not berByHead:
         if testSwitch.FE_0124554_399481_GET_BER_DATA_USING_LEVEL2_B_CMD and testSwitch.BF_0157187_231166_P_FIX_BER_DATA_ZONE_PARSE_RETURN:
            self.oSerial.getBERDataByZone(spc_id = ber_spc_id)
         else:
            self.oSerial.getZoneBERData(maxRetries = 10, lowerBaudRate = True, spc_id = ber_spc_id, printResult = False, retryPause = 30)
      else:
         self.diagGetBERDataByHead(printResult = True, ber_spc_id = ber_spc_id)

      loggedErrors = self.oSerial.getActiveErrorLog()
      loggedErrors = self.oSerial.filterListofDicts(loggedErrors, 'DIAGERR', ['00000006'], include = False)
      if altBadSectors:
         loggedErrors = self.diagAddLBAstoAltList(loggedErrors)

      objPwrCtrl.powerCycle(baudRate = Baud38400, ataReadyCheck = ataReadyCheck)
      objMsg.printMsg(('-'*17+' End Random Read full surface %d minutes '+17*'-')%(numMinutes))

   #-------------------------------------------------------------------------------------------------------
   def diagReadWritePortionOfLBAs(self, RWMode = 'Write', startPosition = 0.0, endPosition = 0.125, DataPattern = 0x12345678, ber_spc_id = 1, altLBAs = True, SMThresh = None, berByHead = False, preFunc = None):
      """
      Read or write a specified fraction of LBAs using the given pattern.
      """
      RWModeMasks = {
         'Read'      : 'R',
         'Write'     : 'W',
      }

      startPosition = self.forceValueWithinRange(startPosition, validRange = (0.0, 1.0))
      endPosition = self.forceValueWithinRange(endPosition, validRange = (0.0, 1.0))

      objMsg.printMsg(('-'*17+' Start Sequential %s: %.4f of Max_LBA to %.4f of Max_LBA '+17*'-')%(RWMode, startPosition, endPosition,))
      objPwrCtrl.powerCycle(baudRate = Baud38400, ataReadyCheck = ataReadyCheck)

      StartLBA = int(self.maxLBA * startPosition)
      EndLBA = int(self.maxLBA * endPosition)

      if StartLBA > EndLBA: # then swap StartLBA and EndLBA
         StartLBA = (StartLBA ^ EndLBA)
         EndLBA = (StartLBA ^ EndLBA)
         StartLBA = (StartLBA ^ EndLBA)


      self.oSerial.enableDiags()
      if DataPattern != None:
         self.oSerial.SetRepeatingPattern(DataPattern)
      if preFunc:
         preFunc()

      if SMThresh:
         CMD ='I' + SMThresh + ',1,4,0,25'
         sptCmds.gotoLevel('7')
         sptCmds.sendDiagCmd(CMD, printResult = True)
         sptCmds.gotoLevel('7')
         sptCmds.sendDiagCmd('s1,d7,06', printResult = True)

      self.oSerial.initDefectLog(printResult = False)
      self.oSerial.setErrorLogging(enable = True, printResult = False)
      self.oSerial.enableRWStats(printResult = False)

      Mode = RWModeMasks[RWMode]
      self.oSerial.rw_LBAs(startLBA = StartLBA, endLBA = EndLBA, mode = Mode, timeout = self.dut.imaxHead * 7200, printResult = False, stopOnError = False, DiagErrorsToIgnore = ['00003010', '00005003', '00005004'], loopSleepTime = 30)

      if not berByHead:
         if testSwitch.FE_0124554_399481_GET_BER_DATA_USING_LEVEL2_B_CMD and testSwitch.extern.FE_0123510_210712_DIAG_BER_BY_HEAD_ZONE:
            if not testSwitch.BF_0132183_399481_CORRECT_LOGGEDERRORS_LOGIC:
               loggedErrors = self.oSerial.getActiveErrorLog()
            self.oSerial.getBERDataByZone()
         else:
            self.oSerial.getZoneBERData(maxRetries = 5, spc_id = ber_spc_id, printResult = False, retryPause = 30)
      else:
         self.diagGetBERDataByHead(printResult = True, ber_spc_id = ber_spc_id, )
      if not (testSwitch.FE_0124554_399481_GET_BER_DATA_USING_LEVEL2_B_CMD and testSwitch.extern.FE_0123510_210712_DIAG_BER_BY_HEAD_ZONE) or testSwitch.BF_0132183_399481_CORRECT_LOGGEDERRORS_LOGIC:
         loggedErrors = self.oSerial.getActiveErrorLog()


      if altLBAs:
         self.diagAddLBAstoAltList(loggedErrors)

      objPwrCtrl.powerCycle(baudRate = Baud38400, ataReadyCheck = ataReadyCheck)
      objMsg.printMsg(('-'*17+' End Sequential %s: %.4f of Max_LBA to %.4f of Max_LBA '+17*'-')%(RWMode, startPosition, endPosition,))

   #-------------------------------------------------------------------------------------------------------
   if testSwitch.FE_0143823_357260_P_MQM_WR_TRACKS_BY_HEAD:
      def diagWriteHeadTracks(self, mode = 'W', startTrack = 0, endTrack = 1, headNumber = 0, DataPattern = 0x00000000):
         """
         Write tracks on a specified head with a given pattern.
         """
         read = mode == 'R'
         write = mode =='W'

         objMsg.printMsg(('-'*17+' Start Sequential Write on Head %s, Track %s to %s '+17*'-')%(headNumber, startTrack, endTrack,))
         objPwrCtrl.powerCycle(baudRate = Baud38400, ataReadyCheck = ataReadyCheck)

         self.oSerial.enableDiags()

         self.diagTrackRW(startTrack=startTrack, endTrack=endTrack, headNumber=headNumber, trackOffset = None, DataPattern = DataPattern, Write = write, Read = read)

         objPwrCtrl.powerCycle(baudRate = Baud38400, ataReadyCheck = ataReadyCheck)
         objMsg.printMsg(('-'*17+' End Sequential Write on Head %s, Track %s to %s '+17*'-')%(headNumber, startTrack, endTrack,))

   #-------------------------------------------------------------------------------------------------------
   def diagSetRetries(self, mode = 'R'):
      """
      Unused stub function to change drive retry level if needed.
      """
      #"SetDerpRetries, Y[Mode],[MaxRdRetries],[MaxWrtRetries],[OtcTLevel],[Options]";
      #WriteRetries = '2,8,8,4'
      #ReadRetries = '6,5,8,4'
      WriteRetries = '2,4,4,4' # force errors?
      ReadRetries = '6,4,4,4' #force errors?
      if mode == 'R':
         retries = ReadRetries
      elif mode == 'W':
         retries = WriteRetries
      sptCmds.gotoLevel('T')
      sptCmds.sendDiagCmd('O0')      # Data output mode = Quiet Mode
      sptCmds.gotoLevel('2')
      sptCmds.sendDiagCmd('Y%s' % retries, printResult = True)
      ##sptCmds.sendDiagCmd('Y2,FF,FF,FF', printResult = True) ## Set retries to 'full normal' with 255 W/R retries and full ECC
      sptCmds.gotoLevel('T')
      sptCmds.sendDiagCmd('O')       # Data output mode =    Formatted ASCII Mode

   #-------------------------------------------------------------------------------------------------------
   def diagSpinDownDwell(self, sleepTimeInMinutes):
      """
      Spin down the drive, but keep the power on for a specified time.
      """
      objMsg.printMsg(('-'*17+' Start Spin Down Dwell for %d Minutes '+17*'-')%(sleepTimeInMinutes,))
      objPwrCtrl.powerCycle(baudRate = Baud38400, ataReadyCheck = ataReadyCheck)
      sptCmds.enableDiags()
      sptCmds.gotoLevel('2')
      sptCmds.sendDiagCmd('Z')
      time.sleep(sleepTimeInMinutes * 60)
      objMsg.printMsg(('-'*17+' End Spin Down Dwell for %d Minutes '+17*'-')%(sleepTimeInMinutes,))

   #-------------------------------------------------------------------------------------------------------
   def diagSetOclim(self, newOclim, printResult = False):
      """
      Set OCLIM for all heads, per head is not yet an option.
      """
      startLevel = sptCmds.currLevel
      sptCmds.gotoLevel('8')
      sptCmds.sendDiagCmd("C15,%X" % newOclim, printResult = printResult)
      sptCmds.gotoLevel(startLevel)

   #-------------------------------------------------------------------------------------------------------
   def diagSqueezeScreen(self, DataPatternMiddle = 0x1111, DataPatternLower = 0x2222, DataPatternUpper = 0x3333, cleanup = True, numTestTracks = 4, OTF_Limit = 6.6):
      """
      For each head, for each zone in the middle third of the zones, pick four
      test tracks write to the test track read the test track and measure BER.
      Write adjacent tracks 10x with tracking offset = 0.10 * VPTI for that track.
      Read test track again 10x, measure BER.  Fail for hard errors or OTF <= limit
      """
      objMsg.printMsg(('-'*17+' Start Squeeze Screen '+17*'-'))
      if testSwitch.auditTest and testSwitch.FE_0123872_399481_MQM_AUDITTEST_SKIP_INCOMPATIBLE_PARTS:
         objMsg.printMsg('AuditTest, skipping diagSqueezeScreen')
         return
      printResult = DEBUG
      objPwrCtrl.powerCycle(baudRate = Baud38400, ataReadyCheck = ataReadyCheck)
      self.oSerial.enableDiags()
      numCyls, zones = (self.lMaxCylinders, self.zones,)

      ##zoneRanges is a dict of dicts with the start and end cyls for each zone
      ##and for each head.  Result looks like following:
      ## {0: {0: {'start': 0, 'end': 1000}, 1: {'start': 1001, 'end': 2000}},
      ## 1: {0: {'start': 0, 'end': 1000}, 1: {'start': 1001, 'end': 2000}}}
      zoneRanges = {}
      for head in sorted(zones.keys()):
         zoneRanges[head] = {}
         for zone in sorted(zones[head].keys()):
            if zone == sorted(zones[head].keys())[-1]:
               zoneRanges[head].update( {zone:{"start":zones[head][zone], "end":numCyls[head]-1}})
            else:
               zoneRanges[head].update( {zone:{"start":zones[head][zone], "end":zones[head][zone+1]-1}})

      objMsg.printMsg("numCyls = %s" % (numCyls,))
      objMsg.printMsg("zones = %s" % (zones,))
      objMsg.printMsg("zoneRanges: %s" % (zoneRanges,))
      originalOclim = self.diagGetCurrentOclim()
      maxZone = sorted(zoneRanges[0].keys())[-1]

      ## Define preliminary test tracks, subject to integrity check.
      testTrackTable = {}
      for head in sorted(zoneRanges.keys()):
         testTrackTable[head] = {}
         for zone in sorted(zoneRanges[head].keys()):
            if zone > maxZone / 3 and zone <= ((maxZone * 2)/3):
               #pprint.pprint("Testing head 0x%X = %d, zone 0x%X = %d." % (head, head, zone, zone))
               testTrackTable[head][zone] = []
               for testPosition in range(numTestTracks + 1)[1:]:
                  cylDistIntoZone = (((zoneRanges[head][zone]["end"] - zoneRanges[head][zone]["start"])* testPosition) / (numTestTracks + 1))
                  testTrack = zoneRanges[head][zone]["start"] + cylDistIntoZone
                  testTrackTable[head][zone].append(testTrack)

      ## Clean test tracks, and pick new test tracks if the test area reports any significant hard error failures.
      objMsg.printMsg("Cleaning Test Area and Checking for Test Track Area Cleanliness.")
      findCleanTestTrackAttempLimit = 3
      sptCmds.gotoLevel('2')
      self.oSerial.SetRepeatingPattern(0x0)
      testTrackMoveCount = 0
      for head in sorted(testTrackTable.keys()):
         for zone in sorted(testTrackTable[head].keys()):
            for testTrackIndex in xrange(len(testTrackTable[head][zone])):
               for attempt in xrange(findCleanTestTrackAttempLimit):
                  testTrack = testTrackTable[head][zone][testTrackIndex]
                  self.oSerial.initDefectLog(printResult = False)
                  self.oSerial.setErrorLogging(enable = True, printResult = False)
                  sptCmds.gotoLevel('2')
                  # write
                  if testSwitch.BF_0126695_399481_MQM_CORRECT_TEST_AREA_FINDER:
                     for seekTrack in xrange(testTrack-2, testTrack+3):
                        sptCmds.sendDiagCmd('AD', printResult = printResult)
                        sptCmds.sendDiagCmd('S%X,%X,,,1' % (seekTrack, head,), printResult = printResult, DiagErrorsToIgnore = ['00003003']) # Try to coax 3003 diag error from drive, indicating slipped track.
                  sptCmds.sendDiagCmd('AD', printResult = printResult)
                  sptCmds.sendDiagCmd('AE,%X' % (head,), printResult = printResult) # set min head
                  sptCmds.sendDiagCmd('AA,%X' % (head,), printResult = printResult) # set max head
                  sptCmds.sendDiagCmd('A8,%X,,%X' % (testTrack - 2, head,), printResult = printResult) # set min cyl
                  sptCmds.sendDiagCmd('A9,%X,,%X' % (testTrack + 2, head,), printResult = printResult) # set max cyl
                  sptCmds.sendDiagCmd('L51', printResult = printResult) # Loop: Enable Stop on Test Space Wrapped, do not display errors, continue on error
                  sptCmds.sendDiagCmd('W,,,,1', timeout = 120, printResult = printResult, DiagErrorsToIgnore = ['00003010', '00005003', '00005004'], loopSleepTime = 0.5)
                  # read
                  sptCmds.sendDiagCmd('L51', printResult = printResult) # Loop: Enable Stop on Test Space Wrapped, do not display errors, continue on error
                  sptCmds.sendDiagCmd('R,,,,1', timeout = 120, printResult = printResult, DiagErrorsToIgnore = ['00003010', '00005003', '00005004'], loopSleepTime = 0.5)
                  # get and process error logs
                  loggedErrors = self.oSerial.getActiveErrorLog()
                  # for each row in loggedErrors try to find if RWERR has a substring match in the Ignore_Errors list,
                  # a list of bool results is created then or-reduced to a single value indicating if the RWERR matched
                  # any of the Ignore_Errors matched.  A list of bools for each RWERR then results. Each bool indicates
                  # if the RWERR is ignorable.  Desired output looks like [True, True]
                  ignoreErrorBoolList = map(lambda row : reduce(lambda a, b : a or b, map(lambda errType : (row['RWERR'].find(errType) > -1), self.Ignore_Errors), False), loggedErrors)
                  # and-reduce the list of bools for each RWERR to a single value indicating if test area is clean
                  testTrackAreaClean = reduce(lambda a, b : a and b, ignoreErrorBoolList, True)
                  if testTrackAreaClean:
                     break # no else if break
                  else: # simply move up 20 tracks.
                     objMsg.printMsg("Bad Test Area, moving Head:%d, Zone:%d, testTrack:%d to new spot.")
                     if not testSwitch.BF_0126695_399481_MQM_CORRECT_TEST_AREA_FINDER:
                        testTrackTable[head][zone][testTrackIndex] = testTrack = 20
                     else:
                        testTrackTable[head][zone][testTrackIndex] = testTrack + 20
                     testTrackMoveCount += 1
               else: # attempts exhausted, time to fail.
                  ScrCmds.raiseException(10190, "Failed to find clean test area in %d attempts." % (findCleanTestTrackAttempLimit,)) # Wt/Rd Def's-Error-Free Track Not Found
      objMsg.printMsg("Had to perform %d test track relocations" % (testTrackMoveCount,))

      ## procedure to clean out test area
      def cleanTestArea():
         objMsg.printMsg("Cleaning Test Area.")
         sptCmds.gotoLevel('2')
         self.oSerial.SetRepeatingPattern(0x0)
         head = 0 # just use the first head to get the list of zones, since all heads are the same
         for head in sorted(testTrackTable.keys()):
            for zone in sorted(testTrackTable[head].keys()):
               for testTrack in testTrackTable[head][zone]:
                  sptCmds.sendDiagCmd('AD', printResult = printResult)
                  sptCmds.sendDiagCmd('AE,%X' % (head,), printResult = printResult) # set min head
                  sptCmds.sendDiagCmd('AA,%X' % (head,), printResult = printResult) # set max head
                  sptCmds.sendDiagCmd('A8,%X,,%X' % (testTrack - 2, head,), printResult = printResult) # set min cyl
                  sptCmds.sendDiagCmd('A9,%X,,%X' % (testTrack + 2, head,), printResult = printResult) # set max cyl
                  sptCmds.sendDiagCmd('L51', printResult = printResult) # Loop: Enable Stop on Test Space Wrapped, do not display errors, continue on error
                  sptCmds.sendDiagCmd('W,,,,1', timeout = 120, printResult = printResult, DiagErrorsToIgnore = ['00003010', '00005003', '00005004'], loopSleepTime = 0.5)
      #cleanTestArea()

      self.oSerial.initDefectLog(printResult = False)
      self.oSerial.setErrorLogging(enable = True, printResult = False)

      testCount = 0
      testBERTable = {}
      sptCmds.gotoLevel('2')
      self.oSerial.enableRWStats(printResult = False)

      maxZone = sorted(zoneRanges[0].keys())[-1]
      for head in sorted(testTrackTable.keys()):
         oclimFloat = originalOclim[head]/4096.0
         tightOclimFloat = float(originalOclim[head])/4096.0 * 8.0 / 14.0
         tightOclim = int(round(4096.0 * tightOclimFloat))
         testBERTable[head] = {}
         for zone in sorted(testTrackTable[head].keys()):
            objMsg.printMsg("Testing head 0x%X = %d, zone 0x%X = %d." % (head, head, zone, zone))
            zoneTestData = {}
            for testTrack in testTrackTable[head][zone]:
               lowerTrack = testTrack - 1
               upperTrack = testTrack + 1
               objMsg.printMsg("Testing track 0x%X = %d, zone 0x%X = %d, head 0x%X = %d." % (testTrack, testTrack, zone, zone, head, head))
               self.diagSetOclim(originalOclim[head], printResult = False)
               self.oSerial.enableRWStats(printResult = printResult)
               self.diagTrackRW(startTrack=testTrack, endTrack=testTrack, headNumber=head, trackOffset = None, DataPattern = DataPatternMiddle, Write = True, Read = True)
               initialBER = self.diagGetBERDataByHead(printResult = True)
               self.oSerial.enableRWStats(printResult = printResult)
               sptCmds.gotoLevel('2')
               if not testSwitch.WA_0125062_399481_IGNORE_00003003_IN_MQM_SQUEEZE:
                  sptCmds.sendDiagCmd('S%X,%X,,,1' % (testTrack, head,), printResult = printResult) # write seek
               else:
                  sptCmds.sendDiagCmd('S%X,%X,,,1' % (testTrack, head,), printResult = printResult, DiagErrorsToIgnore = ["00003003"]) # write seek
               vtpi = self.diagGetCurrentVTPI()
               vtpiFloat = float(vtpi/2.0**14.0)
               #oclims = self.diagGetCurrentOclim(printResult = printResult) # oclim here is Q12
               #oclimFloat = oclims[head]/4096.0
               testOffsetFloat = 0.08
               posOffset = int(round(1000.0 * testOffsetFloat * vtpiFloat)) # offset is 0.1% counts
               offsetFloat = posOffset/1000.0
               negOffset = 0xFFFF - posOffset + 1 # 2's complement
               self.diagSetOclim(tightOclim, printResult = printResult)
               objMsg.printMsg("Original WFT on head %d, cyl %d : 0x%X = %.4f" % (head, testTrack, originalOclim[head], oclimFloat))
               objMsg.printMsg("New WFT on head %d, cyl %d : 0x%X = %.4f" % (head, testTrack, tightOclimFloat, tightOclimFloat))
               objMsg.printMsg("VTPI is 0x%X = %.4f" % (vtpi, vtpiFloat,))
               objMsg.printMsg("Offset will be %.4f, +offset: 0x%X, -offset:, 0x%X" % (offsetFloat, posOffset, negOffset,))
               objMsg.printMsg("Write squeeze tracks")
               self.diagTrackRW(startTrack=lowerTrack, endTrack=lowerTrack, headNumber=head, trackOffset=posOffset, DataPattern=DataPatternLower, Write = True, Read = False, writeLoops = 10)
               self.diagTrackRW(startTrack=upperTrack, endTrack=upperTrack, headNumber=head, trackOffset=negOffset, DataPattern=DataPatternUpper, Write = True, Read = False, writeLoops = 10)
               ##self.diagGetBERDataByHead() ## verify BER data is blank
               self.diagSetOclim(originalOclim[head], printResult = False) # reset oclim.
               objMsg.printMsg("Reading squeezed track")
               self.oSerial.enableRWStats(printResult = printResult) # clean out BER data
               sptCmds.gotoLevel('2')
               self.diagTrackRW(startTrack=testTrack, endTrack=testTrack, headNumber=head, trackOffset = None, DataPattern = None, Write = False, Read = True, readLoops = 10)
               finalBER = self.diagGetBERDataByHead(printResult = True)
               self.oSerial.enableRWStats(printResult = printResult) # clean out BER data
               sptCmds.gotoLevel('2')
               objMsg.printMsg("Track 0x%X = %d, Original Raw BER: %s, Final Raw BER: %s.\n" % (testTrack, testTrack, initialBER[head]['Raw'], finalBER[head]['Raw'],))
               zoneTestData.update({testTrack:{
                  "OTF":float(finalBER[head]['OTF']),
                  #"Final_Raw":float(finalBER[head]['Raw']),
                  #"Delta_Raw":float(finalBER[head]['Raw']) - float(initialBER[head]['Raw']),
                  }
               })

            #Final_Raw_List = [zoneTestData[testTrackNumber]["Final_Raw"] for testTrackNumber in zoneTestData.keys()]
            #Final_Raw_List.sort()

            #Delta_List = [zoneTestData[testTrackNumber]["Delta_Raw"] for testTrackNumber in zoneTestData.keys()]
            #Delta_List.sort()

            #zoneTestData["Final_Raw_Score"] = sum(Final_Raw_List[1:])/float(len(Final_Raw_List[1:]))
            #zoneTestData["Delta_Raw_Score"] = sum(Delta_List[1:])/float(len(Delta_List[1:]))

            testBERTable[head][zone] = zoneTestData

      if cleanup:
         cleanTestArea()

      objMsg.printMsg("Test Complete\n testBERTable:\n %s"%(testBERTable,))
      #self.oSerial.getZoneBERData(spc_id = ber_spc_id, printResult = False)
      loggedErrors = self.oSerial.getActiveErrorLog()
      # fail for any number of 43110081 type errors.
      ReadErrors  = self.oSerial.filterListofDicts(loggedErrors, 'DIAGERR', ['3110081'], include = True)
      self.diagAddLBAstoAltList(loggedErrors)

      #if len(loggedErrors) > 0:
      #   ScrCmds.raiseException(13422, "Total Logged R/W Errors %d greater than zero"%(len(loggedErrors),))

      failCount = 0
      if OTF_Limit != None:
         for head in testBERTable.keys():
            for zone in testBERTable[head].keys():
               for track in testBERTable[head][zone].keys():
                  # round to avoid floating point screwups since OTF has only 1 decimal place of precision
                  if round(testBERTable[head][zone][track]['OTF'], 1) <= OTF_Limit:
                     failCount += 1
      if failCount > 0:
         ScrCmds.raiseException(14604, "Fail squeeze screen, %d OTF_Limit violations." % (failCount,)) # ATI_MIN_BER_NOT_MET 14604

      """
      if BER_Limit:
         for head in testBERTable.keys():
            for zone in testBERTable[head].keys():
               if testBERTable[head][zone]["Final_Raw_Score"] < BER_Limit:
                  failCount += 1
      if failCount > 0:
         ScrCmds.raiseException(14604, "Fail squeeze screen, %d BER_Limit violations." % (failCount,)) # ATI_MIN_BER_NOT_MET 14604

      if deltaLimit:
         for head in testBERTable.keys():
            for zone in testBERTable[head].keys():
               if testBERTable[head][zone]["Delta_Raw_Score"] < deltaLimit:
                  failCount += 1
      if failCount > 0:
         ScrCmds.raiseException(11154, "Fail squeeze screen, %d deltaBER violations." % (failCount,)) # BER_DELTA_LIMIT_EXCEEDED 11154
      """
      objPwrCtrl.powerCycle(baudRate = Baud38400, ataReadyCheck = ataReadyCheck)
      objMsg.printMsg(('-'*17+' End Squeeze Screen '+17*'-'))

   #-------------------------------------------------------------------------------------------------------
   def diagSweep(self, numSweeps = 1, StartCyl=None, EndCyl = None, SweepTimeSecs = 5, DwellTimeMilliSecs = 10):
      """
      Sweep from track to track in specified total time, while dwelling on each track for specified time
      DwellTimeMilliSecs less that 7 seem to make test terminate instantly.
      DwellTimeMilliSecs is finicky, test on a real drive before specifiying.
      """
      if StartCyl == None:
         StartCyl = 0
      if EndCyl == None:
         EndCyl = min(self.lMaxCylinders)

      objMsg.printMsg(('-'*17+' Start %d sweeps, cylinder %d to %d of %d seconds each'+17*'-')%(numSweeps, StartCyl, EndCyl, SweepTimeSecs))
      SweepTimeMilliSecs = SweepTimeSecs * 1000
      objPwrCtrl.powerCycle(baudRate = Baud38400, ataReadyCheck = ataReadyCheck)

      self.oSerial.enableDiags()
      sptCmds.gotoLevel('2')
      for sweepLoop in xrange(numSweeps):
         sptCmds.sendDiagCmd('J%X,%X,%X,%X'%(StartCyl, EndCyl, SweepTimeMilliSecs, DwellTimeMilliSecs,), timeout = SweepTimeSecs*4)

      objPwrCtrl.powerCycle(baudRate = Baud38400, ataReadyCheck = ataReadyCheck)
      objMsg.printMsg(('-'*17+' End %d sweeps, cylinder %d to %d of %d seconds each'+17*'-')%(numSweeps, StartCyl, EndCyl, SweepTimeSecs))

   #-------------------------------------------------------------------------------------------------------
   def diagSWOTScreen(self, timeLimitMins = 30.0, writeTimeSecs = 8.0, delayTimeSecs = 5.0, DataPattern = 0x3333):
      """
      For a specified time, loop on following:
         do sequential writes to random areas of the drive, each write meant to last a specified time,
         then pause a specified time
      """
      objMsg.printMsg(('-'*17+' Start %d Minute SWOT Screen '+17*'-')%(timeLimitMins,))
      if testSwitch.auditTest and testSwitch.FE_0123872_399481_MQM_AUDITTEST_SKIP_INCOMPATIBLE_PARTS:
         objMsg.printMsg('AuditTest, skipping SWOT screen.')
         return
      import random

      startTime = time.time()
      numLBAs = int(2.0**20.0 * writeTimeSecs / 8.0)
      UpperLimitLBA = self.maxLBA - numLBAs
      objMsg.printMsg("numLBAs = %d"%(numLBAs,))
      self.oSerial.enableDiags()

      self.oSerial.SetRepeatingPattern(DataPattern)
      self.oSerial.initDefectLog(printResult = False)
      self.oSerial.setErrorLogging(enable = True, printResult = False)
      while time.time() - startTime < timeLimitMins * 60:
         StartLBA = random.randint(0, UpperLimitLBA)
         EndLBA = StartLBA + numLBAs - 1
         self.oSerial.rw_LBAs(startLBA = StartLBA, endLBA = EndLBA, mode = 'W', timeout = writeTimeSecs * 10, printResult = False, stopOnError = False, DiagErrorsToIgnore = ['00003010', '00005003', '00005004'], loopSleepTime = 0.9)
         if testSwitch.virtualRun:
            break
         else:
            objMsg.printMsg("%d second pause."%(delayTimeSecs,))
            time.sleep(delayTimeSecs)

      loggedErrors = self.oSerial.getActiveErrorLog()
      loggedErrors = self.diagAddLBAstoAltList(loggedErrors)

      objMsg.printMsg(('-'*17+' Start %d Minute SWOT Screen '+17*'-')%(timeLimitMins,))

   #-------------------------------------------------------------------------------------------------------
   def diagTrackOpers(self, Sequence, ErrorLimit = 0):
      """
      Execute a list of OddEven Read Write operations.
      """
      if testSwitch.auditTest and testSwitch.FE_0123872_399481_MQM_AUDITTEST_SKIP_INCOMPATIBLE_PARTS:
         objMsg.printMsg('AuditTest, skipping diagTrackOpers')
         return
      totErrs = 0
      for oper in Sequence:
         totErrs += self.diagFullPackTrack(trackMode = oper['trackMode'],  RWMode = oper['RWMode'], CylRange = oper['CylRange'], DataPattern = oper['DataPattern'], ber_spc_id = oper['ber_spc_id'])
      if totErrs > ErrorLimit:
         ScrCmds.raiseException(13422, "Total Logged R/W Errors %d greater than limit %d"%(totErrs , ErrorLimit))
         #define RW_ERROR                        13422   /* 15 Generic Read Write Error */

   #-------------------------------------------------------------------------------------------------------
   def diagTrackRW(self, startTrack, endTrack, headNumber, trackOffset = None, DataPattern = None, Write = True, Read = True, seekBeforeRW = True, writeLoops = 1, readLoops = 1):
      """
      R/W a track range on a given head
      Optionally sets pattern and tracking offset.
      Tracking offset only effects writes on single tracks.
      """
      sptCmds.gotoLevel('2')
      printResult = DEBUG
      if DataPattern != None:
         self.oSerial.SetRepeatingPattern(DataPattern)
      # reset test space
      sptCmds.sendDiagCmd('AD', printResult = printResult)
      sptCmds.sendDiagCmd('AE,%X' % (headNumber,) , printResult = printResult) # set min head
      sptCmds.sendDiagCmd('AA,%X' % (headNumber,)) # set max head
      sptCmds.sendDiagCmd('A8,%X,,%X' % (startTrack, headNumber,), printResult = printResult) # set min cyl
      sptCmds.sendDiagCmd('A9,%X,,%X' % (endTrack, headNumber,), printResult = printResult) # set max cyl
      if seekBeforeRW:
         if not testSwitch.WA_0125062_399481_IGNORE_00003003_IN_MQM_SQUEEZE:
            sptCmds.sendDiagCmd('S%X,%X,,,1' % (startTrack, headNumber,), printResult = printResult) # Wt Sk
         else:
            sptCmds.sendDiagCmd('S%X,%X,,,1' % (startTrack, headNumber,), printResult = printResult, DiagErrorsToIgnore = ["00003003"]) # Wt Sk

      #if trackOffset:
      #   sptCmds.sendDiagCmd("K%X,1,1,1" % trackOffset, printResult = printResult) # persistent tracking offset in 0.1% units
      if Write:
         for loop in xrange(writeLoops):
            if trackOffset:
               sptCmds.sendDiagCmd("K%X,0,1,1" % trackOffset, printResult = printResult) # persistent tracking offset in 0.1% units
            sptCmds.sendDiagCmd('L51', printResult = printResult) # Loop: Enable Stop on Test Space Wrapped, do not display errors, continue on error
            if testSwitch.FE_0143823_357260_P_MQM_WR_TRACKS_BY_HEAD:
               timeout = int((endTrack - startTrack)* 0.050) + 60
               sptCmds.sendDiagCmd('W,,,,1', timeout = timeout, printResult = printResult, DiagErrorsToIgnore = ['00003010', '00005003', '00005004'], loopSleepTime = 0.5)
            else:
               sptCmds.sendDiagCmd('W,,,,1', timeout = 120, printResult = printResult, DiagErrorsToIgnore = ['00003010', '00005003', '00005004'], loopSleepTime = 0.5)
      if Read:
         if seekBeforeRW:
            if not testSwitch.WA_0125062_399481_IGNORE_00003003_IN_MQM_SQUEEZE:
               sptCmds.sendDiagCmd('S%X,%X,,,0' % (startTrack, headNumber,), printResult = printResult) # Rd Sk
            else:
               sptCmds.sendDiagCmd('S%X,%X,,,0' % (startTrack, headNumber,), printResult = printResult, DiagErrorsToIgnore = ["00003003"]) # Rd Sk
         sptCmds.sendDiagCmd('L11,%X' % (readLoops,), printResult = printResult) # Loop: Enable Stop on Test Space Wrapped, do not display errors, continue on error

         if testSwitch.FE_0143823_357260_P_MQM_WR_TRACKS_BY_HEAD:
            timeout = int((endTrack - startTrack)* 0.050) + 60
            sptCmds.sendDiagCmd('R,,,,1', timeout = timeout, printResult = printResult, DiagErrorsToIgnore = ['00003010', '00005003', '00005004'], loopSleepTime = 0.5)
         else:
            sptCmds.sendDiagCmd('R,,,,1', timeout = 120, printResult = printResult, DiagErrorsToIgnore = ['00003010', '00005003', '00005004'], loopSleepTime = 0.5)

      if trackOffset:
         sptCmds.sendDiagCmd("K0,1,,1", printResult = printResult) # reset offset
         if not testSwitch.WA_0125062_399481_IGNORE_00003003_IN_MQM_SQUEEZE:
            sptCmds.sendDiagCmd('S%X,%X,,,1' % (startTrack, headNumber,), printResult = printResult) # Wt Sk
         else:
            sptCmds.sendDiagCmd('S%X,%X,,,1' % (startTrack, headNumber,), printResult = printResult, DiagErrorsToIgnore = ["00003003"]) # Wt Sk

   #-------------------------------------------------------------------------------------------------------
   def diagWeakWriteScreen(self, DataPattern = 0x3333, ber_spc_id = 1, spinDownDwell = None,  weakWriteModes = ({'mode':'OD','numTracksToOffset':0}), berByHead = False, failSafe = 0):
      """
      Performs a long dwell to catch weak writes during head clearance
      stabilzation time. Write the first 3 tracks in the last zone of each head,
      then read them. The dwell must be done using the spinDownDwell argument,
      not an external dwell since the enable diag command will take the heads
      off the ramp several seconds before the write.  There must be no delay
      between the head going off the ramp and the write.  The write command
      itself is meant to get the head off the ramp.
      """
      objMsg.printMsg(('-'*17+' Start Weak Write Screen '+17*'-'))
      if testSwitch.auditTest and testSwitch.FE_0123872_399481_MQM_AUDITTEST_SKIP_INCOMPATIBLE_PARTS:
         objMsg.printMsg('AuditTest, skipping weak write')
         return
      self.oSerial.enableDiags()

      if spinDownDwell:
         objPwrCtrl.powerCycle(baudRate = Baud38400, ataReadyCheck = ataReadyCheck)
         sptCmds.enableDiags()
         if testSwitch.FE_0128496_405392_WRHEAT_TWEAK_IN_WEAK_WRITE_TEST:
            sptCmds.gotoLevel('7')
            sptCmds.sendDiagCmd('U46,,FF,FF,1', printResult = True) # Set temperature to 70C and disable write power tweak
         sptCmds.gotoLevel('2')
         if testSwitch.WA_0126798_357260_FORCE_DIAG_OVERLAY_LOAD:
            sptCmds.sendDiagCmd('P')   # WORKAROUND: Issue overlay cmd before spin-down
         sptCmds.sendDiagCmd('Z')
         objMsg.printMsg("Sleeping for %d minutes."%spinDownDwell)
         time.sleep(spinDownDwell * 60)

      numCyls, zones = (self.lMaxCylinders, self.zones,)

      self.oSerial.SetRepeatingPattern(DataPattern)
      FinalZoneStartCylindersPerHead = {}
      self.oSerial.initDefectLog(printResult = False)
      self.oSerial.setErrorLogging(enable = True, printResult = False)
      self.oSerial.enableRWStats(printResult = False)
      for weakWriteMode in weakWriteModes:
         if weakWriteMode['mode'] == 'ID':
            for head in zones.keys():
               FinalZoneStartCylindersPerHead[head] = zones[head][max(zones[head].keys())]
         elif weakWriteMode['mode']  == 'MD':
            for head in zones.keys():
               FinalZoneStartCylindersPerHead[head] = zones[head][(max(zones[head].keys())/2)]
         elif weakWriteMode['mode']  == 'OD':
            for head in zones.keys():
               if testSwitch.FE_0160686_220554_P_USE_ZONE_1_INSTEAD_OF_0_IN_WEAK_WRITE_SCRN:
                  FinalZoneStartCylindersPerHead[head] = zones[head][min(zones[head].keys()) + 1]
               else:
                  FinalZoneStartCylindersPerHead[head] = zones[head][min(zones[head].keys())]
         else:
            ScrCmds.raiseException(11044, "Invalid mode %s requested" % weakWriteMode)

         sptCmds.gotoLevel('2')
         sptCmds.sendDiagCmd('AD')                  # Reset test space to default (full pack)
         for head in sorted(FinalZoneStartCylindersPerHead.keys()):
            startCylinder = FinalZoneStartCylindersPerHead[head] + weakWriteMode['numTracksToOffset']
            endCylinder = startCylinder + 3
            objMsg.printMsg("Setting up test space to write cylinders %d to %d, on head %d"%(startCylinder, endCylinder, head,))
            sptCmds.sendDiagCmd('A8,%X,,%X'%(startCylinder, head,)) # set min cyl
            sptCmds.sendDiagCmd('A9,%X,,%X'%(endCylinder, head,)) # set max cyl
         if testSwitch.WA_0121752_399481_USE_U_CMD_TO_SPIN_UP_IN_WEAK_WRITE_SCREEN:
            sptCmds.sendDiagCmd('U', timeout = 30, printResult = True, loopSleepTime = 0.0)
         sptCmds.sendDiagCmd('L51') # Loop: Enable Stop on Test Space Wrapped, do not display errors, continue on error
         objMsg.printMsg("Issuing command to begin writes")
         sptCmds.sendDiagCmd('W,,,,1', timeout = 240, printResult = True, DiagErrorsToIgnore = ['00003010', '00005003', '00005004'], loopSleepTime = 0.5)
         sptCmds.sendDiagCmd('L51') # Loop: Enable Stop on Test Space Wrapped, do not display errors, continue on error
         objMsg.printMsg("Issuing command to begin reads")
         if testSwitch.FE_0164094_407749_P_ADD_AUTO_RETRIES_FOR_READ_CMD:
            sptCmds.sendDiagCmd('R,,,,1', timeout = 240, printResult = True, maxRetries = 3, DiagErrorsToIgnore = ['00003010', '00005003', '00005004'], loopSleepTime = 0.5)
         else:
            sptCmds.sendDiagCmd('R,,,,1', timeout = 240, printResult = True, DiagErrorsToIgnore = ['00003010', '00005003', '00005004'], loopSleepTime = 0.5)

      failCount = 0
      if not berByHead:
         if testSwitch.FE_0124554_399481_GET_BER_DATA_USING_LEVEL2_B_CMD and testSwitch.BF_0157187_231166_P_FIX_BER_DATA_ZONE_PARSE_RETURN:
            zoneData = self.oSerial.getBERDataByZone(spc_id = ber_spc_id)
         else:
            zoneData = self.oSerial.getZoneBERData(spc_id = ber_spc_id, printResult = False)
         if testSwitch.virtualRun:
            zoneData = [{'HD_PHYS_PSN': '0', 'RSYM': '9.9', 'DATA_ZONE': '0', 'HARD': '10.8', 'SYM': '5.1', 'OTF': '10.3', 'RBIT': '10.8', 'RRAW': '6.1', 'WRTY': '0.0', 'WBIT': '0.0', 'SOFT': '10.8', 'WHRD': '0.0'},{'HD_PHYS_PSN': '0', 'RSYM': '9.9', 'DATA_ZONE': '0', 'HARD': '10.8', 'SYM': '5.1', 'OTF': '10.3', 'RBIT': '10.8', 'RRAW': '6.1', 'WRTY': '0.0', 'WBIT': '0.0', 'SOFT': '10.8', 'WHRD': '0.0'},]
         objMsg.printMsg("zoneData = \n%s"%zoneData) # debug code, to be removed later
         for entry in zoneData:
            if float(entry['HARD']) < float(entry['RBIT']):
               failCount += 1
      else:
         self.diagGetBERDataByHead(printResult = True, ber_spc_id = ber_spc_id)

      if failCount > 0 and not failSafe:
         ScrCmds.raiseException(14574, "%d Hard < Rbit violations" % failCount)

      loggedErrors = self.oSerial.getActiveErrorLog()
      if not failSafe:
         loggedErrors = self.diagAddLBAstoAltList(loggedErrors)

      objPwrCtrl.powerCycle(baudRate = Baud38400, ataReadyCheck = ataReadyCheck)
      objMsg.printMsg(('-'*17+' End Weak Write Screen '+17*'-'))

   #-------------------------------------------------------------------------------------------------------
   def collectOTFData(self, DataPattern = 0x3333, ber_spc_id = 9, numZones = 30, cylsToBackOffFromZoneID = 200, numCylsToTest = 100, hardwareItrCnt = 58, berByHead = False, failSafe = 0):
         """
         Method for OTF data collection
         """

         objMsg.printMsg(('-'*17+' Start OTF Data Collection '+17*'-'))

         self.oSerial.enableDiags()

         numCyls, zones = (self.lMaxCylinders, self.zones,)

         self.oSerial.SetRepeatingPattern(DataPattern)
         FinalZoneStartCylindersPerHead = {}
         self.oSerial.initDefectLog(printResult = False)
         self.oSerial.setErrorLogging(enable = True, printResult = False)
         self.oSerial.enableRWStats(printResult = False)

         hrdWareItrCntHex = 'D%x'%hardwareItrCnt
         sptCmds.gotoLevel('2')
         sptCmds.sendDiagCmd(hrdWareItrCntHex, printResult = True)
         sptCmds.gotoLevel('7')
         sptCmds.sendDiagCmd('Y6,5', printResult = True)

         if testSwitch.virtualRun:
            numZones = 15

         if testSwitch.FE_0168623_357260_P_HANDLE_LBA_FREE_ZONES:
            for zone in range(0,numZones):                                                            # zones[head][max(zones[head].keys())]
               for head in zones.keys():
                  if zones[head][zone] == 0xFFFFFF:
                     startCyl = 0xFFFFFF
                  elif (zone != self.dut.numZones - 1) and (zones[head][zone+1] != 0xFFFFFF):
                     startCyl = zones[head][zone+1] - (cylsToBackOffFromZoneID + 1)
                  else:
                     startCyl = numCyls[head] - cylsToBackOffFromZoneID

                  FinalZoneStartCylindersPerHead[head] = startCyl

               sptCmds.gotoLevel('2')
               sptCmds.sendDiagCmd('AD')                                                                 # Reset test space to default (full pack)

               for head in sorted(FinalZoneStartCylindersPerHead.keys()):
                  if FinalZoneStartCylindersPerHead[head] == 0xFFFFFF:
                     objMsg.printMsg("Removing head %s from test space"%head)
                     if head == 0:
                        sptCmds.sendDiagCmd('AE,%X'%(head+1))                                            # Set min head
                     elif head == self.dut.imaxHead -1:
                        sptCmds.sendDiagCmd('AA,%X'%(head-1))                                            # Set max head
                     else:
                        ScrCmds.raiseException(11044, "No valid tracks in zone %s, head %s" %(zone, head))
                  else:
                     startCylinder = FinalZoneStartCylindersPerHead[head]                                # + weakWriteMode['numTracksToOffset']
                     endCylinder = startCylinder + numCylsToTest
                     objMsg.printMsg("Setting up test space to read cylinders %d to %d, on head %d"%(startCylinder, endCylinder, head,))
                     sptCmds.sendDiagCmd('A8,%X,,%X'%(startCylinder, head,))                             # Set min cyl
                     sptCmds.sendDiagCmd('A9,%X,,%X'%(endCylinder, head,))                               # Set max cyl

               sptCmds.sendDiagCmd('U')

               sptCmds.sendDiagCmd('L51')                                                             # Loop: Enable Stop on Test Space Wrapped, do not display errors, continue on error
               objMsg.printMsg("Issuing command to begin reads")
               if testSwitch.FE_0164094_407749_P_ADD_AUTO_RETRIES_FOR_READ_CMD:
                  sptCmds.sendDiagCmd('R,,,,1', timeout = 240, printResult = False, maxRetries = 3, DiagErrorsToIgnore = ['00003010', '00005003', '00005004'], loopSleepTime = 0.5)
               else:
                  sptCmds.sendDiagCmd('R,,,,1', timeout = 240, printResult = False, DiagErrorsToIgnore = ['00003010', '00005003', '00005004'], loopSleepTime = 0.5)

         else:    # not(FE_0168623_357260_P_HANDLE_LBA_FREE_ZONES)
            for zone in range(0,numZones):                 # zones[head][max(zones[head].keys())]
               for head in zones.keys():
                  if zone != self.dut.numZones - 1:
                     startCyl = zones[head][zone+1] - (cylsToBackOffFromZoneID + 1)
                  else:
                     startCyl = numCyls[head] - cylsToBackOffFromZoneID

                  FinalZoneStartCylindersPerHead[head] = startCyl

               sptCmds.gotoLevel('2')
               sptCmds.sendDiagCmd('AD')                  # Reset test space to default (full pack)
               for head in sorted(FinalZoneStartCylindersPerHead.keys()):
                  startCylinder = FinalZoneStartCylindersPerHead[head]   # + weakWriteMode['numTracksToOffset']
                  endCylinder = startCylinder + numCylsToTest
                  objMsg.printMsg("Setting up test space to read cylinders %d to %d, on head %d"%(startCylinder, endCylinder, head,))
                  sptCmds.sendDiagCmd('A8,%X,,%X'%(startCylinder, head,)) # set min cyl
                  sptCmds.sendDiagCmd('A9,%X,,%X'%(endCylinder, head,)) # set max cyl
                  sptCmds.sendDiagCmd('U', timeout = 30, printResult = True, loopSleepTime = 0.0)  # this was under WA_0121752_399481_USE_U_CMD_TO_SPIN_UP_IN_WEAK_WRITE_SCREEN:
               #sptCmds.sendDiagCmd('L51') # Loop: Enable Stop on Test Space Wrapped, do not display errors, continue on error
               #objMsg.printMsg("Issuing command to begin writes")
               #sptCmds.sendDiagCmd('W,,,,1', timeout = 240, printResult = True, DiagErrorsToIgnore = ['00003010', '00005003', '00005004'], loopSleepTime = 0.5)
               sptCmds.sendDiagCmd('L51') # Loop: Enable Stop on Test Space Wrapped, do not display errors, continue on error
               objMsg.printMsg("Issuing command to begin reads")
               if testSwitch.FE_0164094_407749_P_ADD_AUTO_RETRIES_FOR_READ_CMD:
                  sptCmds.sendDiagCmd('R,,,,1', timeout = 240, printResult = True, maxRetries = 3, DiagErrorsToIgnore = ['00003010', '00005003', '00005004'], loopSleepTime = 0.5)
               else:
                  sptCmds.sendDiagCmd('R,,,,1', timeout = 240, printResult = True, DiagErrorsToIgnore = ['00003010', '00005003', '00005004'], loopSleepTime = 0.5)

         failCount = 0
         if not berByHead:
            if testSwitch.FE_0124554_399481_GET_BER_DATA_USING_LEVEL2_B_CMD and testSwitch.BF_0157187_231166_P_FIX_BER_DATA_ZONE_PARSE_RETURN:
               zoneData = self.oSerial.getBERDataByZone(spc_id = ber_spc_id)
            else:
               zoneData = self.oSerial.getZoneBERData(spc_id = ber_spc_id, printResult = False)
            if testSwitch.virtualRun:
               zoneData = [{'HD_PHYS_PSN': '0', 'RSYM': '9.9', 'DATA_ZONE': '0', 'HARD': '10.8', 'SYM': '5.1', 'OTF': '10.3', 'RBIT': '10.8', 'RRAW': '6.1', 'WRTY': '0.0', 'WBIT': '0.0', 'SOFT': '10.8', 'WHRD': '0.0'},{'HD_PHYS_PSN': '0', 'RSYM': '9.9', 'DATA_ZONE': '0', 'HARD': '10.8', 'SYM': '5.1', 'OTF': '10.3', 'RBIT': '10.8', 'RRAW': '6.1', 'WRTY': '0.0', 'WBIT': '0.0', 'SOFT': '10.8', 'WHRD': '0.0'},]
            #objMsg.printMsg("zoneData = \n%s"%zoneData) # debug code, to be removed later
            for entry in zoneData:
               if float(entry['HARD']) < float(entry['RBIT']):
                  failCount += 1
         else:
            self.diagGetBERDataByHead(printResult = True, ber_spc_id = ber_spc_id)


         curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)

         tabledata = self.dut.dblData.Tables('P_FORMAT_ZONE_ERROR_RATE').tableDataObj()

         for record in range(len(tabledata)):

            if int(tabledata[record]['SPC_ID']) == ber_spc_id: # write

               deltaOTF = float(tabledata[record]['BITS_READ_LOG10']) - float(tabledata[record]['OTF_ERROR_RATE'])

               self.dut.dblData.Tables('P_DELTA_OTF_TABLE').addRecord({
                     'SPC_ID': -1,
                     'OCCURRENCE' : occurrence,
                     'SEQ' : curSeq,
                     'TEST_SEQ_EVENT' : testSeqEvent,
                     'HD_PHYS_PSN'                 : self.dut.LgcToPhysHdMap[int(tabledata[record]['HD_LGC_PSN'])],
                     'DATA_ZONE'                   : tabledata[record]['DATA_ZONE'],
                     'HD_LGC_PSN'                  : tabledata[record]['HD_LGC_PSN'],
                     'DELTA_OTF'                   : deltaOTF,
                     })

         objMsg.printDblogBin(self.dut.dblData.Tables('P_DELTA_OTF_TABLE'))

         if testSwitch.FE_0170519_407749_P_HSA_BP_ENABLE_DELTA_BURNISH_AND_OTF_CHECK:
            if self.dut.nextOper == 'FNC2':
               delta_otf_tbl = self.dut.dblData.Tables('P_DELTA_OTF_TABLE').tableDataObj()
               for record in delta_otf_tbl:
                  self.dut.dblData.Tables('P_HSA_BP_DELTA_OTF_TABLE').addRecord({
                     'SPC_ID'                      : -1,
                     'OCCURRENCE'                  : occurrence,
                     'SEQ'                         : curSeq,
                     'TEST_SEQ_EVENT'              : testSeqEvent,
                     'HD_PHYS_PSN'                 : self.dut.LgcToPhysHdMap[int(record['HD_LGC_PSN'])],
                     'DATA_ZONE'                   : record['DATA_ZONE'],
                     'HD_LGC_PSN'                  : record['HD_LGC_PSN'],
                     'DELTA_OTF'                   : record['DELTA_OTF'],
                     'HSA_BP_PN'                   : self.dut.HSA_BP_PN,
                     })

         objMsg.printDblogBin(self.dut.dblData.Tables('P_HSA_BP_DELTA_OTF_TABLE'))

         if failCount > 0 and not failSafe:
            ScrCmds.raiseException(14574, "%d Hard < Rbit violations" % failCount)

         loggedErrors = self.oSerial.getActiveErrorLog()
         if not failSafe:
            loggedErrors = self.diagAddLBAstoAltList(loggedErrors)

         objPwrCtrl.powerCycle(baudRate = Baud38400, ataReadyCheck = ataReadyCheck)
         objMsg.printMsg(('-'*17+' End OTF Data Collection '+17*'-'))
   #-------------------------------------------------------------------------------------------------------------


   def diagWeakWriteBERDelta(self, base_spc_id = 7, weak_spc_id = 8, spc_id = 0):
      """
      Calculates delta between normal and cold write write BER data.
       - Data from P_FORMAT_ZONE_ERROR_RATE
       - Generates temporary P_WEAK_WRITE_BER_DELTA table for Grading use only
       Parameters:
         base_spc_id = spc_ID for initial (warm) P_FORMAT_ZONE_ERROR_RATE data
         weak_spc_id = spc_id for cold P_FORMAT_ZONE_ERROR_RATE data
      """
      objMsg.printMsg(('-'*17+' Start Weak Write BER Delta Check '+17*'-'))
      seq, occurrence, testSeqEvent = self.dut.objSeq.registerCurrentTest(0)

      wrBERLog = self.dut.dblData.Tables('P_FORMAT_ZONE_ERROR_RATE').tableDataObj()
      zoneList = ()
      baseBERdata = {}
      objMsg.printMsg('Building Base BER table')
      for item in wrBERLog:
         if int(item['SPC_ID']) == base_spc_id:
            if not baseBERdata.has_key(item['HD_PHYS_PSN']):
               baseBERdata[item['HD_PHYS_PSN']] = {}
            baseBERdata[item['HD_PHYS_PSN']][item['DATA_ZONE']] = item
            if item['DATA_ZONE'] not in zoneList:
               zoneList += (item['DATA_ZONE'],)

      objMsg.printMsg('Building Weak Write Delta BER table')

      for item in wrBERLog:
         if int(item['SPC_ID']) == weak_spc_id:
            if baseBERdata.has_key(item['HD_PHYS_PSN']) and baseBERdata[item['HD_PHYS_PSN']].has_key(item['DATA_ZONE']):
               if testSwitch.FE_0143730_399481_P_SEND_WEAK_WRITE_DELTA_TABLE_TO_DB:
                  self.dut.dblData.Tables('P_WEAK_WRITE_BER_DELTA').addRecord(
                     {
                     'SPC_ID'                      : spc_id,
                     'OCCURRENCE'                  : occurrence,
                     'SEQ'                         : seq,
                     'TEST_SEQ_EVENT'              : testSeqEvent,
                     'HD_PHYS_PSN'                 : item['HD_PHYS_PSN'],
                     'HD_LGC_PSN'                  : item['HD_LGC_PSN'],
                     'DATA_ZONE'                   : item['DATA_ZONE'],
                     'BITS_READ_LOG10'             : item['BITS_READ_LOG10'],
                     'HARD_ERROR_RATE'             : item['HARD_ERROR_RATE'],
                     'HARD_ERROR_DELTA'            : float(baseBERdata[item['HD_PHYS_PSN']][item['DATA_ZONE']]['HARD_ERROR_RATE']) - float(item['HARD_ERROR_RATE']),
                     'OTF_ERROR_RATE'              : item['OTF_ERROR_RATE'],
                     'OTF_ERROR_DELTA'             : float(baseBERdata[item['HD_PHYS_PSN']][item['DATA_ZONE']]['OTF_ERROR_RATE']) - float(item['OTF_ERROR_RATE']),
                     'RAW_ERROR_RATE'              : item['RAW_ERROR_RATE'],
                     'RAW_ERROR_DELTA'             : float(baseBERdata[item['HD_PHYS_PSN']][item['DATA_ZONE']]['RAW_ERROR_RATE']) - float(item['RAW_ERROR_RATE']),
                     })

               else:

                  self.dut.dblData.Tables('P_WEAK_WRITE_BER_DELTA').addRecord(
                     {
                     'SPC_ID'                      : spc_id,
                     'OCCURRENCE'                  : occurrence,
                     'SEQ'                         : seq,
                     'TEST_SEQ_EVENT'              : testSeqEvent,
                     'HEAD'                        : item['HD_PHYS_PSN'],
                     'ZONE'                        : item['DATA_ZONE'],
                     'RBIT'                        : item['BITS_READ_LOG10'],
                     'HARD_ERROR_RATE'             : item['HARD_ERROR_RATE'],
                     'HARD_ERROR_DELTA'            : float(baseBERdata[item['HD_PHYS_PSN']][item['DATA_ZONE']]['HARD_ERROR_RATE']) - float(item['HARD_ERROR_RATE']),
                     'OTF_ERROR_RATE'              : item['OTF_ERROR_RATE'],
                     'OTF_ERROR_DELTA'             : float(baseBERdata[item['HD_PHYS_PSN']][item['DATA_ZONE']]['OTF_ERROR_RATE']) - float(item['OTF_ERROR_RATE']),
                     'RAW_ERROR_RATE'              : item['RAW_ERROR_RATE'],
                     'RAW_ERROR_DELTA'             : float(baseBERdata[item['HD_PHYS_PSN']][item['DATA_ZONE']]['RAW_ERROR_RATE']) - float(item['RAW_ERROR_RATE']),
                     })

      objMsg.printDblogBin(self.dut.dblData.Tables('P_WEAK_WRITE_BER_DELTA'))

      objMsg.printMsg(('-'*17+' End Weak Write BER Delta Check '+17*'-'))

   #-------------------------------------------------------------------------------------------------------
   def diagRWZoneRangeSEQ(self, mode = 'R', option = 'All', CylRange = {'mode':'All'}, zoneRange = None):
      """
      Perform n  Odd/Even/All Read/Write operation on all heads, across a specified cyclinder range.
      """

      """
      Set test space to a given cyclinder range on all heads.
      """
      startZone = zoneRange[0]
      if testSwitch.virtualRun:
         endZone  = 14
      else:
         endZone   = zoneRange[1]
      numHeads = self.dut.imaxHead

      maxCylList, zoneList = self.diagGetMaxCylinders()
      hd0StartTrack = zoneList[0][startZone]
      #sptCmds.sendDiagCmd(CTRL_Z,altPattern='>',printResult=True)
      self.oSerial.enableDiags()
      sptCmds.gotoLevel('2')
      for head in xrange(numHeads):
         startTrack = zoneList[head][startZone]
         endTrack = (zoneList[head][endZone+1]) - 1
         objMsg.printMsg("Setting up test space cylinders %d to %d, on head %d"%(startTrack, endTrack, head,))
         sptCmds.sendDiagCmd('A8,%X,,%X'%(startTrack, head,),timeout = 200) # set min cyl
         sptCmds.sendDiagCmd('A9,%X,,%X'%(endTrack, head,),timeout = 200) # set max cyl
      sptCmds.sendDiagCmd('A3', printResult=True)
      sptCmds.sendDiagCmd('S%X,0'%(hd0StartTrack),printResult=True)                # Seek to startTrack, head 0
      sptCmds.sendDiagCmd('L51', printResult=True)                 # Loop: do not display errors, continue on error, stop at end of test space
      # Send command (Write or Read): continue on error'
      theTimeout = self.dut.imaxHead * 7200 # two hour timeout per head
      objMsg.printMsg("\nTimeout for %s %s tracks set to %d seconds." % (mode, option, theTimeout))
      sptCmds.sendDiagCmd('%s,,,,1' % mode, timeout = theTimeout, printResult = True, DiagErrorsToIgnore = ['00003010', '00005003', '00005004'], loopSleepTime = 30)
      if testSwitch.BF_0176400_475827_P_ENABLE_ESLIP_AFTER_WRT_ZONE_RNG_SEQ:
         sptCmds.enableESLIP()

   def diagRWTracksCHS(self, mode = 'R', option = 'All', CylRange = {'mode':'All'}):
      """
      Perform n  Odd/Even/All Read/Write operation on all heads, across a specified cyclinder range.
      """
      def setCylinderRange(startTrack, endTrack, numHeads):
         """
         Set test space to a given cyclinder range on all heads.
         """
         sptCmds.gotoLevel('2')
         for head in xrange(numHeads):
            objMsg.printMsg("Setting up test space cylinders %d to %d, on head %d"%(startTrack, endTrack, head,))
            sptCmds.sendDiagCmd('A8,%X,,%X'%(startTrack, head,)) # set min cyl
            sptCmds.sendDiagCmd('A9,%X,,%X'%(endTrack, head,)) # set max cyl

      evenCylsAllHeads = "A13"
      oddCylsAllHeads = "A23"
      if mode == 'R' and option in ('All', 'Odd', 'Even',):
         objMsg.printMsg("Performing sequential read pass on %s tracks." % option)
      elif mode == 'W' and option in ('All', 'Odd', 'Even',):
         objMsg.printMsg("Performing sequential write pass on %s tracks." % option)
      else:
         ScrCmds.raiseException(11044, "Invalid mode requested")

      ##self.setRetries(mode) ## not normally to be used.
      sptCmds.gotoLevel('2')
      ##sptCmds.sendDiagCmd('Y2,FF,FF,FF', printResult = True) ## not normally to be used ##Set retries to 'full normal' with 255 W/R retries and full ECC

      if CylRange['mode'] == 'All':
         sptCmds.sendDiagCmd('AD')                  # Reset test space to default (full pack)
         startTrack = 0
      elif CylRange['mode'] == 'OD':
         startTrack = 0
         endTrack = startTrack + CylRange['numCyls'] - 1
      elif CylRange['mode'] == 'MD':
         startTrack = min(self.lMaxCylinders)/2
         endTrack = startTrack + CylRange['numCyls'] - 1
      elif CylRange['mode'] == 'ID':
         endTrack = min(self.lMaxCylinders)
         startTrack = endTrack - CylRange['numCyls'] + 1
      elif CylRange['mode'] == 'Range':
         startTrack = min(CylRange['cylRange'])
         endTrack = max(CylRange['cylRange'])
      else:
         ScrCmds.raiseException(11044, "Invalid cylinder range selected: %s"%(CylRange['mode'],))

      if CylRange['mode'] != 'All':
         setCylinderRange(startTrack, endTrack, self.dut.imaxHead)


      if option == 'Even':
         sptCmds.sendDiagCmd(evenCylsAllHeads)   # Set test space to even tracks only, all heads
      elif option == 'Odd':
         sptCmds.sendDiagCmd(oddCylsAllHeads)    # Set test space to odd tracks only, all heads

      sptCmds.sendDiagCmd('S%X,0'%(startTrack,))                # Seek to startTrack, head 0
      sptCmds.sendDiagCmd('L51')                 # Loop: do not display errors, continue on error, stop at end of test space
      # Send command (Write or Read): continue on error'
      theTimeout = self.dut.imaxHead * 7200 # two hour timeout per head
      objMsg.printMsg("\nTimeout for %s %s tracks set to %d seconds." % (mode, option, theTimeout))
      sptCmds.sendDiagCmd('%s,,,,1' % mode, timeout = theTimeout, printResult = True, DiagErrorsToIgnore = ['00003010', '00005003', '00005004'], loopSleepTime = 30)

   #-------------------------------------------------------------------------------------------------------
   def forceValueWithinRange(self, inValue, validRange = (0.0, 1.0)):
      """
      Limit a value with a given cutoff range.
      """
      if inValue > max(validRange):
         retValue = max(validRange)
      elif inValue < min(validRange):
         retValue = min(validRange)
      else:
         retValue = inValue
      return retValue

   #-------------------------------------------------------------------------------------------------------
   def intfCheckMergeGList(self):
      """
      Call base_IntfTest GList display.
      """
      objMsg.printMsg(('-'*17+' Start CheckMergeGList '+17*'-'))
      from base_IntfTest import CCheckMergeGList
      CCheckMergeGList(self.dut, params = {}).run()
      objMsg.printMsg(('-'*17+' End CheckMergeGList '+17*'-'))

   #-------------------------------------------------------------------------------------------------------
   def intfFullPackRead(self):
      """
      T510 FPR
      """
      objMsg.printMsg(('-'*17+' Start FullPackRead '+17*'-'))
      ICmd.CRCErrorRetry(IO_CRC_RETRY_VAL)
      self.oProcess.St(TP.prm_510_Particle_FPR)
      objMsg.printMsg(('-'*17+' End FullPackRead '+17*'-'))

   #-------------------------------------------------------------------------------------------------------
   def intfLongDST(self):
      """
      T600 FPR
      """
      objMsg.printMsg(('-'*17+' Start Long DST (Drive Self Test) '+17*'-'))
      from base_IntfTest import CSmartDSTLong
      CSmartDSTLong(self.dut, params = {}).run()
      objMsg.printMsg(('-'*17+' End Long DST (Drive Self Test) '+17*'-'))

   #-------------------------------------------------------------------------------------------------------
   def powerOffDwell(self, sleepTimeInMinutes):
      """
      Power down drive for specified time.
      """
      objMsg.printMsg(('-'*17+' Start Power Off Dwell for %d Minutes '+17*'-')%(sleepTimeInMinutes,))
      objPwrCtrl.powerOff()
      time.sleep(sleepTimeInMinutes * 60)
      objPwrCtrl.powerCycle(baudRate = Baud38400, ataReadyCheck = ataReadyCheck)
      objMsg.printMsg(('-'*17+' End Power Off Dwell for %d Minutes '+17*'-')%(sleepTimeInMinutes,))

   #-------------------------------------------------------------------------------------------------------
   def upperLower(self, FourByteNum):
      """
      Split an integer value into a tuple 2 Most Significant Bytes and 2 Least Significant Bytes.
      """
      FourByteNum = FourByteNum & 0xFFFFFFFF # chop off any more than 4 bytes
      MSBs = FourByteNum >> 16
      LSBs = FourByteNum & 0xFFFF
      return (MSBs, LSBs)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      """
      Exec a list of commands specified in Test Parameters variable "MQMCommandTuple".
      Each tuple entry being a string to execute as code.
      """
      self.oSerial = sptDiagCmds()
      self.oProcess = CProcess()
      CommandTuple = self.params.get('CommandTuple', None)
      for command in CommandTuple:
         getattr(self, command[0])(**command[1])

      self.dut.driveattr[str(self.dut.currentState)] = 'PASS'

###########################################################################################################
class CCPCATITest(CState):
   """
      Class that performs ATI Test in CPC
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut
   #-------------------------------------------------------------------------------------------------------
   def run(self):

      result = OK
      data = {}
      deBug       = 0
      pattern     = self.params.get('PATTERN', 0x1234)
      sectCnt     = self.params.get('SECTOR_COUNT', 256)
      stampFlag   = 0
      compareFlag = 0
      cmdLoop     = self.params.get('CMD_LOOP', 1000)
      testLoop    = self.params.get('TEST_LOOP', 50)
      startLBA    = self.params.get('START_LBA', 0)
      endLBA      = self.params.get('END_LBA', 400)
      maxLBA      = int(ICmd.GetMaxLBA()['MAX48'], 16)-1
      stepLBA     = maxLBA/400
      UDMASpeed   = 0x45        # 100Mbs

      ICmd.HardReset()

      data = ICmd.IdentifyDevice()
      if data['LLRET'] != OK:
         ScrCmds.raiseException(13420, "IdentifyDevice failed %s" % str(data))
      else:
         objMsg.printMsg("Identify Device passed")

      #numLogSect = 2 ** (data['IDLogSectPerPhySect'] & 0x0F)
      #numLogSect = 2 ** (data['LogToPhysSectorSize'] & 0x0F)
      #objMsg.printMsg("numLogSect = %d" %numLogSect)
      #offsetLBA0 = data['IDLogInPhyIndex'] & 0x3FFF

      ICmd.FlushCache(); ICmd.ClearBinBuff(WBF); ICmd.ClearBinBuff(RBF)
      result = ICmd.FillBuffByte(WBF, pattern)['LLRET']
      if result != OK:
         objMsg.printMsg('ATI Test Failed to Fill 0x%2X Data' %pattern)
      else:
         if deBug:
            objMsg.printMsg('********** Write Buffer Data **********')
            data = ICmd.GetBuffer(WBF, 0, 550)['DATA']
            objMsg.printMsg('Data Return [0:20]: %s' %data[0:20])
            objMsg.printMsg('Data Return [512:532]: %s' %data[512:532])

      result = ICmd.SetFeatures(0x03, UDMASpeed)['LLRET']
      if result != OK:
         objMsg.printMsg('ATI Test Failed SetFeatures - Transfer Rate = UDMA-100')
      else:
         objMsg.printMsg('ATI Test Passed SetFeatures - Transfer Rate = UDMA-100')
      result = ICmd.SetFeatures(0x82)['LLRET']
      if result != OK:
         objMsg.printMsg('ATI Test Failed SetFeatures - Disable Write Cache')
      else:
         objMsg.printMsg('ATI Test Passed SetFeatures - Disable Write Cache')

      objMsg.printMsg('Write on first %d locations %d times' % (testLoop, cmdLoop))
      for loop in xrange(0, testLoop, 1):
         startLBA = loop * stepLBA
         objMsg.printMsg('%s writes on 400 LBA starting %d' % (cmdLoop, startLBA))

         #if numLogSect > 1:
         #   startLBA = startLBA - (startLBA % numLogSect)
         #   if offsetLBA0 > 0:
         #      if startLBA == 0:
         #         startLBA = startLBA + numLogSect
         #      startLBA = startLBA - offsetLBA0

         endLBA = startLBA + 400
         objMsg.printMsg('%s writes location(%d) adjusted from start=%d to end=%d' % (cmdLoop, loop+1, startLBA, endLBA))

         if testSwitch.BF_0145546_231166_P_SEQUENTIAL_CMD_XLATE_SIC:
            data = ICmd.SequentialWriteDMAExt(startLBA, endLBA, stepLBA, sectCnt, 0, 0, cmdLoop)
         else:
            data = ICmd.SequentialCmdLoop(0x35, startLBA, endLBA, sectCnt, sectCnt, cmdLoop, 1)
         result = data['LLRET']
         if result != OK:
            objMsg.printMsg('SequentialCmdLoop failed at loop %d, result=%s' % (testLoop, result))
            break

      if result == OK:
         result = ICmd.SetFeatures(0x02)['LLRET']
         if result != OK:
            objMsg.printMsg('ATI Test Failed SetFeatures - Enable Write Cache')
         else:
            objMsg.printMsg('ATI Test Passed SetFeatures - Enable Write Cache')

      if result == OK:
         pattern = 0x00
         startLBA = 0
         endLBA = maxLBA/8
         compareFlag = 1

         ICmd.FlushCache(); ICmd.ClearBinBuff(WBF); ICmd.ClearBinBuff(RBF)
         result = ICmd.FillBuffByte(WBF, pattern)['LLRET']
         if result != OK:
            objMsg.printMsg('ATI Test Failed to Fill 0x%2X Data' %pattern)
         else:
            if deBug:
               objMsg.printMsg('********** Write Buffer Data **********')
               data = ICmd.GetBuffer(WBF, 0, 550)['DATA']
               objMsg.printMsg('Data Return [0:20]: %s' %data[0:20])
               objMsg.printMsg('Data Return [512:532]: %s' %data[512:532])

         objMsg.printMsg('Sequential Read on first eighth of the disk')
         data = ICmd.SequentialReadDMAExt(startLBA, endLBA, stepLBA, sectCnt, stampFlag)
         result = data['LLRET']
         if result != OK:
            objMsg.printMsg('ATI Test Failed - Sequential Read')

      if result == OK:
         objMsg.printMsg('Sequential Write on first eighth of the disk')
         data = ICmd.SequentialWriteDMAExt(startLBA, endLBA, stepLBA, sectCnt, stampFlag)
         result = data['LLRET']
         if result != OK:
            objMsg.printMsg('ATI Test Failed - Sequential Write')

      if result == OK:
         objMsg.printMsg('Sequential Read on first eighth of the disk with compare')
         if objRimType.IOInitRiser() and testSwitch.BF_0145751_231166_P_ADD_DATA_PATTERN0_ATI_CMP:
            data = ICmd.SequentialReadDMAExt(startLBA, endLBA, stepLBA, sectCnt, stampFlag, compareFlag, DATA_PATTERN0 = pattern)
         else:
            data = ICmd.SequentialReadDMAExt(startLBA, endLBA, stepLBA, sectCnt, stampFlag, compareFlag)
         result = data['LLRET']
         if result != OK:
            objMsg.printMsg('ATI Test Failed - Sequential Read With Compare')

      if result != OK:
         objMsg.printMsg('ATI Test Failed: Result = %s' %result)
         ScrCmds.raiseException(13050, 'ATI Test Failed')
      else:
         objMsg.printMsg('ATI Test Passed')

      ICmd.FlushCache()

###########################################################################################################
class CCPCWeakWriteTest(CState):
   """
      Class that performs Weak Write Test in CPC
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut
   #-------------------------------------------------------------------------------------------------------
   def run(self):

      result = OK
      data = {}
      pattern = '0000'
      sectCnt = 256
      count = 2700
      step = 65000
      UDMASpeed = 0x45 # 100Mbs
      testLoop = self.params.get('LOOPS', 5)
      retries = 2

      maxLBA = int(ICmd.GetMaxLBA()['MAX48'], 16)-1
      ID1 = (maxLBA - 2000000)
      MD1 = (maxLBA / 2)
      OD1 = 0

      ICmd.HardReset()

      for loopcnt in range(testLoop): # Read in Forward order, OD-MD-ID, Step from Low LBA's to High LBA's
         OD2 = OD1+step; OD3 = OD2+step; OD4 = OD3+step
         locationOD = ("%d,%d,%d,%d,%d,%d,%d,%d," % (OD1, OD1+count, OD2, OD2+count, OD3, OD3+count, OD4, OD4+count))

         MD2 = MD1+step; MD3 = MD2+step; MD4 = MD3+step
         locationMD = ("%d,%d,%d,%d,%d,%d,%d,%d," % (MD1, MD1+count, MD2, MD2+count, MD3, MD3+count, MD4, MD4+count))

         ID2 = ID1+step; ID3 = ID2+step; ID4 = ID3+step
         locationID = ("%d,%d,%d,%d,%d,%d,%d,%d," % (ID1, ID1+count, ID2, ID2+count, ID3, ID3+count, ID4, ID4+count))

         locationAll = locationOD + locationMD + locationID

         objMsg.printMsg('Weak Write Setting: sectCnt=%s UDMASpeed=0x%X pattern=%s WRcount=%s step=%s' %\
                         (sectCnt,UDMASpeed,pattern,count,step))
         objMsg.printMsg('Weak Write Locations OD = %s' %locationOD)
         objMsg.printMsg('Weak Write Locations MD = %s' %locationMD)
         objMsg.printMsg('Weak Write Locations ID = %s' %locationID)

         for retry in xrange(retries+1):
            data = ICmd.WeakWrite(locationAll, sectCnt, UDMASpeed, pattern)

            objMsg.printMsg('Weak Write Return Data: %s' %data)
            result = data['LLRET']
            if result != OK:
               objMsg.printMsg('Weak Write Test - Loop Number %d of %d Failed - Do Retry' %(retry+1, retries+1))
               if retry < (retries+1):
                  objPwrCtrl.powerCycle(5000, 12000, 10, 30)
            else:
               break
            #end of Weak Write Test

         if result != OK:
            break

         OD1 = OD4 + step
         MD1 = MD4 + step
         ID1 = ID4 + step
         #end of test loop

      if result != OK:
         objMsg.printMsg('Weak Write Test Failed: Result = %s' % result)
         ScrCmds.raiseException(13060, 'Weak Write Test Failed')
      else:
         objMsg.printMsg('Weak Write Test Passed')

      ICmd.FlushCache()
###########################################################################################################
###########################################################################################################
class CCPCATIODTest(CState):
   """
      Class that performs ATI OD Test in CPC
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut
   #-------------------------------------------------------------------------------------------------------
   def run(self):

      result = OK
      data = {}
      deBug       = 0
      pattern     = self.params.get('PATTERN', 0x1234)
      sectCnt     = self.params.get('SECTOR_COUNT', 256)
      stampFlag   = 0
      compareFlag = 0
      cmdLoop     = self.params.get('CMD_LOOP', 10000)
      testLoop    = self.params.get('TEST_LOOP', [10,5,5])
      startLBA    = self.params.get('START_LBA', 0)
      endLBA      = self.params.get('END_LBA', 400)
      maxLBA      = int(ICmd.GetMaxLBA()['MAX48'], 16)-1
      objMsg.printMsg("maxLBA  : %s" %maxLBA)
      stepLBA     = maxLBA/400
      objMsg.printMsg("stepLBA  : %s" %stepLBA)
      UDMASpeed   = 0x45        # 100Mbs

      ICmd.HardReset()

      data = ICmd.IdentifyDevice()
      if data['LLRET'] != OK:
         ScrCmds.raiseException(13420, "IdentifyDevice failed %s" % str(data))
      else:
         objMsg.printMsg("Identify Device passed")

      #numLogSect = 2 ** (data['IDLogSectPerPhySect'] & 0x0F)
      #numLogSect = 2 ** (data['LogToPhysSectorSize'] & 0x0F)
      #objMsg.printMsg("numLogSect = %d" %numLogSect)
      #offsetLBA0 = data['IDLogInPhyIndex'] & 0x3FFF

      ICmd.FlushCache(); ICmd.ClearBinBuff(WBF); ICmd.ClearBinBuff(RBF)
      result = ICmd.FillBuffByte(WBF, pattern)['LLRET']
      if result != OK:
         objMsg.printMsg('ATI Test Failed to Fill 0x%2X Data' %pattern)
      else:
         if deBug:
            objMsg.printMsg('********** Write Buffer Data **********')
            data = ICmd.GetBuffer(WBF, 0, 550)['DATA']
            objMsg.printMsg('Data Return [0:20]: %s' %data[0:20])
            objMsg.printMsg('Data Return [512:532]: %s' %data[512:532])

      result = ICmd.SetFeatures(0x03, UDMASpeed)['LLRET']
      if result != OK:
         objMsg.printMsg('ATI Test Failed SetFeatures - Transfer Rate = UDMA-100')
      else:
         objMsg.printMsg('ATI Test Passed SetFeatures - Transfer Rate = UDMA-100')
      result = ICmd.SetFeatures(0x82)['LLRET']
      if result != OK:
         objMsg.printMsg('ATI Test Failed SetFeatures - Disable Write Cache')
      else:
         objMsg.printMsg('ATI Test Passed SetFeatures - Disable Write Cache')

      objMsg.printMsg('\nWrite on first %d locations %d times location 1 - 10' % (testLoop[0], cmdLoop))
      for loop in xrange(0, testLoop[0], 1):
         startLBA = loop * stepLBA
         objMsg.printMsg('%s writes on 400 LBA starting %d' % (cmdLoop, startLBA))

         #if numLogSect > 1:
         #   startLBA = startLBA - (startLBA % numLogSect)
         #   if offsetLBA0 > 0:
         #      if startLBA == 0:
         #         startLBA = startLBA + numLogSect
         #      startLBA = startLBA - offsetLBA0

         endLBA = startLBA + 400
         objMsg.printMsg('%s writes location(%d) adjusted from start=%d to end=%d' % (cmdLoop, loop+1, startLBA, endLBA))

         if testSwitch.BF_0145546_231166_P_SEQUENTIAL_CMD_XLATE_SIC:
            data = ICmd.SequentialWriteDMAExt(startLBA, endLBA, sectCnt, sectCnt, 0, 0, cmdLoop)
         else:
            data = ICmd.SequentialCmdLoop(0x35, startLBA, endLBA, sectCnt, sectCnt, cmdLoop, 1)
         result = data['LLRET']
         if result != OK:
            objMsg.printMsg('SequentialCmdLoop failed at loop %d, result=%s' % (testLoop[0], result))
            break

      if result == OK:
         objMsg.printMsg('\nWrite on first %d locations %d times location 20 - 25' % (testLoop[1], cmdLoop))
         for loop in xrange(19, 20+testLoop[1], 1):
            startLBA = loop * stepLBA
            objMsg.printMsg('%s writes on 400 LBA starting %d' % (cmdLoop, startLBA))

            #if numLogSect > 1:
            #   startLBA = startLBA - (startLBA % numLogSect)
            #   if offsetLBA0 > 0:
            #      if startLBA == 0:
            #         startLBA = startLBA + numLogSect
            #      startLBA = startLBA - offsetLBA0

            endLBA = startLBA + 400
            objMsg.printMsg('%s writes location(%d) adjusted from start=%d to end=%d' % (cmdLoop, loop+1, startLBA, endLBA))

            if testSwitch.BF_0145546_231166_P_SEQUENTIAL_CMD_XLATE_SIC:
               data = ICmd.SequentialWriteDMAExt(startLBA, endLBA, sectCnt, sectCnt, 0, 0, cmdLoop)
            else:
               data = ICmd.SequentialCmdLoop(0x35, startLBA, endLBA, sectCnt, sectCnt, cmdLoop, 1)
            result = data['LLRET']
            if result != OK:
               objMsg.printMsg('SequentialCmdLoop failed at loop %d, result=%s' % (testLoop[1], result))
               break

      if result == OK:
         objMsg.printMsg('\nWrite on first %d locations %d times location 45 - 50' % (testLoop[2], cmdLoop))
         for loop in xrange(44, 45+testLoop[2], 1):
            startLBA = loop * stepLBA
            objMsg.printMsg('%s writes on 400 LBA starting %d' % (cmdLoop, startLBA))

            #if numLogSect > 1:
            #   startLBA = startLBA - (startLBA % numLogSect)
            #   if offsetLBA0 > 0:
            #      if startLBA == 0:
            #         startLBA = startLBA + numLogSect
            #      startLBA = startLBA - offsetLBA0

            endLBA = startLBA + 400
            objMsg.printMsg('%s writes location(%d) adjusted from start=%d to end=%d' % (cmdLoop, loop+1, startLBA, endLBA))

            if testSwitch.BF_0145546_231166_P_SEQUENTIAL_CMD_XLATE_SIC:
               data = ICmd.SequentialWriteDMAExt(startLBA, endLBA, sectCnt, sectCnt, 0, 0, cmdLoop)
            else:
               data = ICmd.SequentialCmdLoop(0x35, startLBA, endLBA, sectCnt, sectCnt, cmdLoop, 1)
            result = data['LLRET']
            if result != OK:
               objMsg.printMsg('SequentialCmdLoop failed at loop %d, result=%s' % (testLoop[2], result))
               break

      if result == OK:
         result = ICmd.SetFeatures(0x02)['LLRET']
         if result != OK:
            objMsg.printMsg('ATI Test Failed SetFeatures - Enable Write Cache')
         else:
            objMsg.printMsg('ATI Test Passed SetFeatures - Enable Write Cache')

      if result == OK:
         pattern = 0x00
         startLBA = 0
         endLBA = int(0.1665*maxLBA)
         stepLBA = sectCnt = 256

         ICmd.FlushCache(); ICmd.ClearBinBuff(WBF); ICmd.ClearBinBuff(RBF)
         result = ICmd.FillBuffByte(WBF, pattern)['LLRET']
         if result != OK:
            objMsg.printMsg('ATI Test Failed to Fill 0x%2X Data' %pattern)
         else:
            if deBug:
               objMsg.printMsg('********** Write Buffer Data **********')
               data = ICmd.GetBuffer(WBF, 0, 550)['DATA']
               objMsg.printMsg('Data Return [0:20]: %s' %data[0:20])
               objMsg.printMsg('Data Return [512:532]: %s' %data[512:532])

         objMsg.printMsg('Sequential Read with zero pattern Zn 0 - 3')
         data = ICmd.SequentialReadDMAExt(startLBA, endLBA, stepLBA, sectCnt)
         objMsg.printMsg('Sequential Read with zero pattern - Result %s' %str(data))
         result = data['LLRET']
         if result != OK:
            objMsg.printMsg('ATI Test Failed - Sequential Read')

      if result != OK:
         objMsg.printMsg('ATI Test Failed: Result = %s' %result)
         ScrCmds.raiseException(13050, 'ATI Test Failed')
      else:
         objMsg.printMsg('ATI Test Passed')

      ICmd.FlushCache()
