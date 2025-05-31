#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Implements low level power handling functions
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/11/30 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/sptCmds.py $
# $Revision: #2 $
# $DateTime: 2016/11/30 23:34:39 $
# $Author: yihua.jiang $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/sptCmds.py#2 $
# Level:3
#---------------------------------------------------------------------------------------------------------#

#--------------------------- IMPORTS -------------------------------------------------------------------#


from Constants import *

import struct, traceback, re, time, types
from SerialCls import baseComm
import ScrCmds, Utility
import MessageHandler as objMsg
from DesignPatterns import Singleton
from Rim import objRimType, theRim
from Exceptions import SeaSerialRequired
from UartCls import theUart
from Drive import objDut as dut
from Constants import UNLOCK_CMD
#--------------------------- MODULE STATIC OBJECTS -------------------------------------------------------------------#
global diagError
global currLevel
global prPat
global rwErrVal

diagError = ""
currLevel = "T"
prPat = re.compile('S?F3+[\s_]*(?P<LEVEL>[\dA-Za-z])>')

diagErrorStatus = re.compile("DiagError (?P<diagError>[\dA-F]+)( R/W Status (?P<rwStat>[\d]+) R/W Error (?P<rwError>[\dA-F]+)){0,1}")
diagErrorStat_2 = re.compile("DiagError (?P<diagError>[\dA-F]+)(R/W Status (?P<rwStat>[\d]+) R/W Error (?P<rwError>[\dA-F]+)){0,1}")

DEBUG = 0
FLASH_CHKSUM_FAIL = 'Flash boot code checksum failure!'

#--------------------------- CLASSES -------------------------------------------------------------------#
class comMode(Singleton):
   class availModes:
      sptDiag = ('sptDiag',1)
      mctBase = ('mctBase',2)
      intBase = ('intBase',3)

   def __init__(self, initMode = availModes.mctBase):
      Singleton.__init__(self)
      self.__activeMode = initMode

   def setMode(self, setMode, determineCodeType = False):
      if determineCodeType:
         dut.f3Active = self.determineCodeType()
         if dut.f3Active:
            if not dut.certOper:
               setMode = self.availModes.intBase
            else:
               setMode = self.availModes.sptDiag

      if type(setMode) == types.TupleType:
         self.__activeMode = setMode
         try:
            ScrCmds.statMsg("Active comm mode set to %s at %s" % (self.__activeMode,StackFrameInfo()))
         except:
            ScrCmds.statMsg(traceback.format_exc())

         if objRimType.CPCRiser() and not objRimType.CPCRiserNewSpt():
            if setMode == self.availModes.intBase or ( setMode == self.availModes.sptDiag ):
               ICmd.EslipRetry(2,1,0) # 2 retries 1 pad and 0 extra acks
            elif setMode == self.availModes.mctBase:
               #2 retries, 3x C0 padding with extra ACK
               ICmd.EslipRetry(2, 3, 0)
      else:
         #print 'Incorrect com mode input: %s' % str(setMode)
         ScrCmds.raiseException(11044, 'Incorrect com mode input: %s' % str(setMode))

   def getMode(self):
      return self.__activeMode

   def determineCodeType(self):
      try:
         f3Active = False

         import sptCmds
         baseComm.flush()
         if testSwitch.FE_0177394_433430_SPINUP_FOR_POIS_ENABLED:
            DisableInitiatorCommunication()
         sptCmds.disableAPM()

         if testSwitch.BF_0143937_357260_P_DELAY_5_SEC_BEFORE_CTRL_Z:
            time.sleep(5)

         if testSwitch.WA_0122681_231166_EXTENDED_BAD_CLUMP_TIMEOUT:
            if testSwitch.BF_0166867_231166_P_FIX_CRT2_SF3_INIT_DRV_INFO_DETCT:
               timeout = 20
               printResult = True
            else:
               timeout = 200
               printResult = False

            result = sptCmds.sendDiagCmd(CTRL_Z, timeout = timeout, altPattern = '>', printResult = printResult, maxRetries = 3, loopSleepTime = 1, raiseException = 0, Ptype = 'PChar', suppressExitErrorDump = True)
         else:

            result = sptCmds.sendDiagCmd(CTRL_Z, timeout = 10, altPattern = '>', printResult = False, maxRetries = 0, loopSleepTime = 1, raiseException = 0, Ptype = 'PChar', suppressExitErrorDump = True)

         if DEBUG:
            objMsg.printMsg( 'CTRL_Z results: %s' %result )

         if testSwitch.BF_0172797_231166_EXACT_MATCH_DETERMINE_CODE_TYPE:
            if result.find('SF3')> -1:
               f3Active = False
               self.__activeMode = self.availModes.mctBase

            elif result.find('F3') > -1:
               f3Active = True
               self.__activeMode = self.availModes.sptDiag
            else:
               f3Active = None

            doF3mod = f3Active
         else:
            doF3mod = ( not testSwitch.virtualRun ) and ( (not result == '' or testSwitch.BF_0166867_231166_P_FIX_CRT2_SF3_INIT_DRV_INFO_DETCT) and not result.find('SF3_') > -1 )
            if doF3mod:
               f3Active = True
               self.__activeMode = self.availModes.sptDiag

         if doF3mod:

            if DEBUG:
               objMsg.printMsg( 'Prompt found')

            if objRimType.CPCRiser() and not objRimType.CPCRiserNewSpt():
               ICmd.EslipRetry(2,1,0) # 2 retries 1 pad and 0 extra acks

            enableESLIP(retries = 0, timeout = 1, printResult = True, suppressExitErrorDump = False)

            if not dut.certOper:
               #we aren't in cert oper so we want to be back talking to SIC
               UseESlip()
               UseHardSRQ(0)
               EnableInitiatorCommunication()

            if DEBUG:
               objMsg.printMsg( 'CTRL_T passed')
         objMsg.printMsg( 'F3 code found on drive? %s' %f3Active)
      except:
         f3Active = False
         ScrCmds.statMsg("Failed to determine code type")
         ScrCmds.statMsg(traceback.format_exc())
      return f3Active


objComMode = comMode() # Static object

#--------------------------- FUNCTIONS -------------------------------------------------------------------#

def CtrlZ_Y2(cmd):
   """
   Issue F>Y2 command when CTRL_Z command is sent to the drive.
   """
   if cmd == CTRL_Z and testSwitch.FE_0249024_356922_CTRLZ_Y2_RETRY \
   and dut.IsSDI == False and dut.SkipY2 == False and testSwitch.NoIO \
   and dut.nextOper in ['FIN2', 'CUT2', 'FNG2'] and not dut.nextState in ['INIT', 'CLEAR_EWLM']:
      global currLevel
      objMsg.printMsg("CtrlZ detected - Issuing /FY2")
      backuplevel = currLevel
      sendDiagCmd("/FY2,,,,10000000018", printResult = True)
      currLevel = ''
      ret = gotoLevel(backuplevel)
      objMsg.printMsg("Restore level %s" % ret)

def sendDiagCmd( cmd, timeout=60, altPattern = None, printResult = False, stopOnError = True, maxRetries = 0, Ptype = 'PBlock',DiagErrorsToIgnore = [], loopSleepTime = 0.1, raiseException = 1, suppressExitErrorDump = 0, RWErrorsToIgnore = []):
   """
   Use this command to send a diagnostic command to the drive and receive it's response.
   ***IMPORTANT OPTIMIZATION STEPS****
      * Please increase the loopSleepTime to the maximum you feel possible w/o loosing data- for long running commands with little data to return or that you care about set this value > 5
      * Do not use this command for "online commands": commands that don't return to a prompt and return large amounts of data in a short period.
         ** Use execOnlineCmd instead.
   """

#CHOOI-16Oct15 OffSpec
   if testSwitch.OOS_Code_Enable == 1:
      return

   global diagError
   retry = 0
   res = ''

   if testSwitch.WA_0256539_480505_SKDC_M10P_BRING_UP_DEBUG_OPTION:
      objMsg.printMsg("**** DiagCmd : [%s], [%s] ****" % ((cmd.replace('\r','[CR]')), ":".join(x.encode('hex') for x in cmd)))

   while retry >= 0:
      resultOk = 1
      diagError = ''
      func = getattr(baseComm, Ptype)
      accumulator = func(cmd)

      try:
         res = promptRead(timeout, raiseException = raiseException, altPattern = altPattern, accumulator = accumulator, suppressExitErrorDump = suppressExitErrorDump, loopSleepTime = loopSleepTime)
      except SeaSerialRequired:
         raise
      except:
         from string import printable

         if len(cmd) > 0 and cmd[0] not in printable:
            objMsg.printMsg("Failed to read prompt for Cmd : %X" % ord(cmd))
         else:
            objMsg.printMsg("Failed to read prompt for Cmd : %s" %(cmd))
         resultOk = 0

      del accumulator


      if res.find("OPShock") > 0:
         tmpattr = DriveAttributes.get('OPS_CAUSE','NONE')

         objMsg.printMsg("Found OPShock. OPS_CAUSE=[%s] cmd=[%s] Res=[%s]" % (tmpattr, repr(cmd), repr(res)))

         if dut.nextState in ["SPMQM",]:
            ModName = dut.SubNextState
         else:
            ModName = dut.nextState

         if tmpattr in ["NONE", "?", ""]:
            tmpattr = ModName
         else:
            tmpattr += ("/" + ModName)

         DriveAttributes['OPS_CAUSE'] = tmpattr[-30:]
         dut.driveattr['OPS_CAUSE'] = DriveAttributes['OPS_CAUSE']
         objMsg.printMsg("New OPS_CAUSE=[%s]" % DriveAttributes['OPS_CAUSE'])

      try:
         try:
            failedCommandSearch(res,stopOnError = stopOnError,DiagErrorsToIgnore = DiagErrorsToIgnore, RWErrorsToIgnore = RWErrorsToIgnore)
         except:
            printResult = 1
            resultOk = 0

      finally:

         if printResult or testSwitch.virtualRun:
            objMsg.printMsg("-"*40)
            objMsg.printMsg("Result from %s cmd:\n%s" % (cmd,res))
            objMsg.printMsg("-"*40)

      if resultOk:
         CtrlZ_Y2(cmd)
         if cmd == CTRL_Z:
            currLevel = ''  #invalidate level so we force new level
            gotoLevel('T')

         return res
      else:
         retry = sendDiagCmdRetries(retry, maxRetries)

   return res

def sendDiagCmdRetries( retry, maxRetries):
   global diagError
   diagErrorRetryList = ['00007001', '00005014']

   if maxRetries == 0:
      retriesAvailable = 4
   else:
      retriesAvailable = maxRetries

   if retry < retriesAvailable:
      if maxRetries > 0:   #retry regardless of error if maxRetries passed in
         retry += 1
      elif diagError in diagErrorRetryList:   #retry if in retryList
         objMsg.printMsg("DiagError %s found in RetryList" %diagError )
         retry += 1
         time.sleep(2)
      else:
         raise
   else:
      raise

   objMsg.printMsg("Issuing retry no. %s of %s" %(retry,retriesAvailable))
   return retry

def failedCommandSearch( data, stopOnError = True, stopOnInvalidDiag = True, stopOnCriticalDiagError = True, DiagErrorsToIgnore = [], RWErrorsToIgnore = []):
   global diagError
   DiagErrorsToAlwaysIgnore = []
   [DiagErrorsToIgnore.append(item) for item in DiagErrorsToAlwaysIgnore]

   if (data.find("DiagError 0000000A") > -1 or data.find("Error 00FD DETSEC 0000000A") > -1):
      diagError = '0000000A'
      if stopOnCriticalDiagError and diagError not in DiagErrorsToIgnore:
         ScrCmds.raiseException(10253,"Critical Diagnostic Error")

   mat = re.search("PLP CHS (\w+\.\w+\.\w+)", data)
   ErrPLPCHS = ''
   if mat:
      ErrPLPCHS = mat.group()
   for line in data.splitlines():
      line = line.strip()
      if line == 'Invalid Diag Cmd' or line == "Invalid Diagnostic Command":
         diagError = 'Invalid Diag Cmd'
         if stopOnInvalidDiag and diagError not in DiagErrorsToIgnore:
            ScrCmds.raiseException(10253,"Invalid Diagnostic Command")

      if testSwitch.FE_0144322_357260_P_CHECK_FOR_DIAG_INPUT_ERROR and line == 'Input_Command_Error':
         diagError = 'Input_Command_Error'
         if stopOnInvalidDiag and diagError not in DiagErrorsToIgnore:
            ScrCmds.raiseException(13426,"Diagnostic Command Error")

      match = diagErrorStat_2.search(line)
      if not match:
         match = diagErrorStatus.search(line)

      if match:
         global rwErrVal
         grDict = match.groupdict()
         rwStatVal = grDict.get('rwStat',0)
         diagErrVal = grDict.get('diagError',0)
         rwErrVal = grDict.get('rwError',0)

         line = '%s %s'%(line, ErrPLPCHS)
         if rwStatVal is not None and int(rwStatVal) == 2:
            diagError = diagErrVal
            if stopOnError and diagError not in DiagErrorsToIgnore:
               if data.find("OPShock") > 0:
                  ScrCmds.raiseException(10569,"OPShock detected on line: '%s'" % line)
               else:
                  ScrCmds.raiseException(13422,"RW Command Failed on line: '%s'" % line)
         elif diagErrVal is not None:
            diagError = diagErrVal
            if stopOnError and (diagError not in DiagErrorsToIgnore) and (rwErrVal not in RWErrorsToIgnore):
               if data.find("OPShock") > 0:
                  ScrCmds.raiseException(10569,"OPShock detected on line: '%s'" % line)
               else:
                  ScrCmds.raiseException(13426,"Diag Command Failed: '%s'" % line)

      if diagError > '':
         if diagError in DiagErrorsToIgnore:
            if DEBUG:
               objMsg.printMsg("Ignoring Diagnostic Error : %s" %diagError)
         elif rwErrVal in RWErrorsToIgnore:
            if DEBUG:
               objMsg.printMsg("Ignoring ReadWrite Error : %s" %rwErrVal)



def promptRead(timeout=30, raiseException = 1, altPattern = None, accumulator = None, suppressExitErrorDump = 0, loopSleepTime = 0.01):

   tmoCallback = Utility.timoutCallback(timeout, ScrCmds.raiseException, (10566, "Reached timeout when trying to find prompt" + str(baseComm.lastCommand)))

   result = ''

   if altPattern == None:
      prompt = prPat
   else:
      prompt = re.compile(altPattern)

   #initialize match objects
   matches = False
   flashInfo = None

#CHOOI-16Oct15 OffSpec
   if testSwitch.OOS_Code_Enable == 1:
      return

   for result in accumulator:
      if testSwitch.virtualRun:
         return result

      if tmoCallback(raiseError = False): #check if we're out of time
         break

      # Sleep for 0.01 second to reduce CM overhead
      # Warning numbers greater than 0.01 were tested (1, 0.1)
      #    But data loss occurred in serial only cells at 38400 baud
      if testSwitch.InitSmart_NeedMoreDelay:
         time.sleep(0.1)
      else:
         time.sleep(loopSleepTime)

      if DEBUG > 0:
         if not result == '':
            objMsg.printMsg('current result = %s' % result,objMsg.CMessLvl.DEBUG)

      matches = prompt.search(result)
      if matches:
         break
      else:
         flashInfo = getFlashCodeMatch(result)
         if flashInfo:
            break

         if testSwitch.FE_0146953_231166_P_DETECT_FLASH_CHECKSUM_FAIL and FLASH_CHKSUM_FAIL in result:
            ScrCmds.raiseException(10340, "Seaserial required", SeaSerialRequired)


   if not matches:
      accumulator = baseComm.PBlock('')
      result += iter(accumulator).next()

      #Make a last ditch effor to find the data
      matches = prompt.search(result)
      if matches:
         return result

      if not suppressExitErrorDump:
         objMsg.printMsg("Data buffer on error exit:\n%s" % result,objMsg.CMessLvl.DEBUG)

      try:
         if flashInfo == None:
            ScrCmds.raiseException(10566, "Reached timeout when trying to find prompt" + str(baseComm.lastCommand))
         else:
            ScrCmds.raiseException(11231, "FlashLED Error %s" % flashInfo.groupdict() + result + baseComm.lastCommand)
      except:
         if raiseException:
            raise
         else:
            return result

   return result

def flashLEDSearch(timeout=600):
   startTime = time.time()
   curTime = time.time()
   buffer = ''
   flashAddr = ''
   flashCode = ''

   accumulator = baseComm.PChar("")
   found = 0
   for result in accumulator:
      if (curTime-startTime) > timeout or testSwitch.virtualRun:
         break

      mat = getFlashCodeMatch(result)
      if mat:
         myDict = mat.groupdict()
         try:
            flashAddr = myDict['flash_addr']
            flashCode = myDict['flash_code']
         finally:
            objMsg.printMsg(str(myDict), objMsg.CMessLvl.DEBUG)
            objMsg.printMsg(str(result), objMsg.CMessLvl.DEBUG)
         found = 1
         break
      curTime = time.time()
      time.sleep(10)
   if not found:
      objMsg.printMsg("FLASH LED not found! Data returned: \n%s" % str(buffer), objMsg.CMessLvl.DEBUG)

   return flashAddr, flashCode

def getFlashCodeMatch(buffer):
   """
   Returns match object (or None if none found) of flash led
   found in buffer.
   .groupdict() will return a dict of {'flass_addr':value,'flash_code':code}
   """
   patt = 'FlashLED\s*-\s*Failure\s*Code:\s*(?P<flash_code>[0-9a-fA-F]+)\s*Failure\s*Address:\s*(?P<flash_addr>[0-9a-fA-F]+)'
   patt2 = 'LED:\s*(?P<flash_code>[0-9a-fA-F]+)\s*FAddr:\s*(?P<flash_addr>[0-9a-fA-F]+)'
   mat = re.search(patt,buffer)
   if mat == None:
      mat = re.search(patt2,buffer)

   return mat

def disPowerChop():
   gotoLevel('2')
   objMsg.printMsg(str("Issuing M0,8 diag to shut off power-chop"),objMsg.CMessLvl.DEBUG)
   if not testSwitch.FE_0111448_357260_NO_SPINDOWN_UP_IN_DISPOWERCHOP:
      result = sendDiagCmd('Z', timeout = 30)
      result = sendDiagCmd('U', timeout = 30)
   result = sendDiagCmd('M0,8', timeout = 30)
   gotoLevel('T')

def disableAPM():
   """
      Disables APM mode following power-on
   """
   if DEBUG > 0:
      objMsg.printMsg('Issuing ESC to clear / disable APM')
   if testSwitch.BF_0162945_231166_P_FIX_APM_DISABLE_DEF_SPIN_PIN:
      accumulator = baseComm.PBlock('a'*10,noTerminator = 1)                # Send ESC to get F3 code out of APM
      if testSwitch.WA_0162966_231166_P_ALLOW_EXT_TIME_DEFERRED_SPIN_BFW_TRANS:
         time.sleep(10)
      else:
         time.sleep(1)
   else:
      accumulator = baseComm.PBlock(ESC*10,noTerminator = 1)                # Send ESC to get F3 code out of APM
   del accumulator

def EnableInitiatorCommunication():
   theRim.EnableInitiatorCommunication(objComMode)

def DisableInitiatorCommunication():
   if testSwitch.BF_0152393_231166_P_RE_ADD_LEGACY_ESLIP_PORT_INCR_TMO:
      theRim.DisableInitiatorCommunication(objComMode, failCommRetries = False)
   else:
      theRim.DisableInitiatorCommunication(objComMode)


def enableESLIP( retries = 10, timeout = 30, printResult = True, raiseException=False, suppressExitErrorDump = True):

   if dut.IsSDI:
      retries = 2
      timeout = 8

   #Enable eslip with CTRL_T and update cell object
   DisableInitiatorCommunication()

   if testSwitch.FE_0155584_231166_P_RUN_ALL_DIAG_CMDS_LOW_BAUD and not testSwitch.WA_0156250_231166_P_DONT_SET_PROC_BAUD_ENABLE_ESLIP:
      syncBaudRate( PROCESS_HDA_BAUD )

   sendDiagCmd(CTRL_T, timeout, "[eslipESLIP]{5}", printResult, True, retries, 'PChar',[],1, raiseException, suppressExitErrorDump)
   disableAPM()

def enableOnlineMode( retries = 10, timeout = 30, printResult = True, raiseException=False, suppressExitErrorDump = True):
   #Enable eslip with CTRL_T and update cell object
   disableAPM()
   DisableInitiatorCommunication()

   sendDiagCmd(CTRL_R, timeout, "ASCII Online mode", printResult, False, retries, 'PChar',[],1, raiseException, suppressExitErrorDump)



def enableDiags( retries = 10, raiseException = 1):

#CHOOI-16Oct15 OffSpec
   if testSwitch.OOS_Code_Enable == 1:
      return

   if dut.IsSDI:
      objMsg.printMsg("SDI skipping enableDiags")
      return

   objMsg.printMsg("Enabling F3 SPT Diagnostic Mode",objMsg.CMessLvl.DEBUG)
   if testSwitch.WA_0122534_231166_DIAGS_UNSUPPORTED:
      objMsg.printMsg("bypass diag calls- diags unsupported")
      if not testSwitch.virtualRun:
         raise Exception
   if testSwitch.WA_0159248_231166_P_DELAY_DIAG_FOR_MC_INIT and testSwitch.extern.FE_0116076_355860_MEDIA_CACHE:
      objMsg.printMsg("Sleeping for 30sec to allow MC to release cache file and init.")
      time.sleep(30)
   theRim.DisableInitiatorCommunication(objComMode, False)

   if not testSwitch.FE_0141320_220554_P_NO_10S_DELAY_IN_ENABLE_DIAGS:
      time.sleep(10)


   failFlag = 0
   baseComm.flush()
   disableAPM()

   for x in range(retries):
      try:
         if DEBUG == 1:
            objMsg.printMsg("Retry #%d" % x, objMsg.CMessLvl.VERBOSEDEBUG)
         try:
            if testSwitch.FE_0117758_231166_NVCACHE_CAL_SUPPORT:
               if testSwitch.WA_0122681_231166_EXTENDED_BAD_CLUMP_TIMEOUT:
                  promptStatus = sendDiagCmd(CTRL_Z, timeout = 200, Ptype='PChar', maxRetries = 3)
               else:
                  promptStatus = sendDiagCmd(CTRL_Z, timeout = 10, Ptype='PChar')
            else:
               accumulator = baseComm.PChar(CTRL_Z)
               promptStatus = promptRead(10, accumulator = accumulator)
               CtrlZ_Y2(CTRL_Z)
         except:
            objMsg.printMsg("Error: %s" % traceback.format_exc())
            if testSwitch.FE_0117758_231166_NVCACHE_CAL_SUPPORT:
               try:
                  promptStatus = sendDiagCmd('\n', timeout = 10)
               except:
                  objMsg.printMsg("Error: %s" % traceback.format_exc())
                  raise
            else:
               raise

         if DEBUG > 0:
            objMsg.printMsg("Get Prompt Status: %s" % promptStatus,objMsg.CMessLvl.DEBUG)

         if testSwitch.FE_0175466_340210_DIAG_UNLOCK:
            try:
               accumulator = baseComm.PChar('\n')
               del accumulator
               time.sleep(0.2)
               accumulator = sendDiagCmd(UNLOCK_CMD, timeout=30)
               del accumulator
               time.sleep(.2)
               promptStatus = sendDiagCmd('\n', timeout = 10)
            except:
               objMsg.printMsg("WARNING: Unlock COmmand did not work")

         currLevel = ''  #invalidate level so we force new level
         gotoLevel('T')

         failFlag = 0

         if ('SF3_T>' in promptStatus) and testSwitch.BF_0167020_231166_P_SF3_DETECTION_ROBUSTNESS:
            objComMode.setMode(objComMode.availModes.mctBase)
         else:
            objComMode.setMode(objComMode.availModes.sptDiag)
         break
      except:
         time.sleep(10)
         if DEBUG == 1:
            objMsg.printMsg(traceback.format_exc(), objMsg.CMessLvl.VERBOSEDEBUG)
         failFlag = 1

      if x > 2:         # If we've already re-tried a couple of times, try another baud
         if theUart.getBaud() == PROCESS_HDA_BAUD:
            theUart.setBaud(DEF_BAUD)
            dut.baudRate = DEF_BAUD
         else:
            theUart.setBaud(PROCESS_HDA_BAUD)
            dut.baudRate = PROCESS_HDA_BAUD


   if failFlag == 1:
      ScrCmds.raiseException(10340)

   if testSwitch.FE_0155584_231166_P_RUN_ALL_DIAG_CMDS_LOW_BAUD:
      syncBaudRate(DEF_BAUD)

   if testSwitch.DIAG_POWER_CHOP_ENABLED:
      try:             #Pharaoh - Matt Robinson request, do not disable power chop.  (03/10/09)
         disPowerChop()
      except:
         if raiseException:
            ScrCmds.raiseException(10340)
   time.sleep(15)
   return promptStatus

if testSwitch.FE_0155584_231166_P_RUN_ALL_DIAG_CMDS_LOW_BAUD:
   def syncBaudRate(baudRate=DEF_BAUD):
      """
      Synchronize baud rate using ASCII diag mode.
      Usage: syncBaudRate(baudRate)
      Where: baudRate = drive supported baud rate value in ASCII diag mode.
      """
      global currLevel

      theBaud = theUart.getBaud()
      diagLevel = currLevel

      if theBaud!=baudRate or testSwitch.BF_0159246_231166_P_ALWAYS_SET_BAUD_SYNC_CMD:
         objMsg.printMsg("Adjusting baud rate from %s to %s." %(theBaud, baudRate))

         currLevel = '' #invalidate level so we force new level

         gotoLevel('T')

         sendDiagCmd('B%s' % baudRate, raiseException = 0, timeout=2, printResult=True)

         #set the cell baud to comm to drive
         theUart.setBaud(baudRate)

         currLevel = '' #invalidate level so we force new level
         gotoLevel(diagLevel)

         #only set drive baud once validated
         dut.baudRate = baudRate

def gotoLevel(level = 'T',maxRetries = 3):
   global currLevel

   prompt = prPat

   if testSwitch.virtualRun:
      currLevel = level
      return level

   retry = 0
   while retry < maxRetries:
      try:
         result = sendDiagCmd("/%s" % level, timeout = 10)
         # Send another CR to verify level
         result = sendDiagCmd('')
         matches = prompt.search(result)

         if matches:
            pr = matches.groupdict()
            if not pr['LEVEL'] == level:
               ScrCmds.raiseException(10566, 'Failed init prompt. Level = %s and expected %s' % (pr['LEVEL'],level))
         else:
            ScrCmds.raiseException(10566, 'Failed to find diagnostic level.')

         if DEBUG == 1:
            objMsg.printMsg("Found level %s" % level, objMsg.CMessLvl.VERBOSEDEBUG)

         currLevel = level
         break
      except:
         objMsg.printMsg("Traceback: %s" % traceback.format_exc())
         retry += 1
   else:
      ScrCmds.raiseException(10566, 'Failed init prompt')

   return currLevel

def execOnlineCmd( cmd, timeout = 30, waitLoops = 100):
   if testSwitch.WA_0122534_231166_DIAGS_UNSUPPORTED:
      objMsg.printMsg("bypass diag calls- diags unsupported")
      if not testSwitch.virtualRun:
         raise Exception
   DisableInitiatorCommunication()

   #Send ber by zone command
   failTimer = Utility.timoutCallback(timeout,ScrCmds.raiseException,(10566,"Failed to retreive all data within timeout for online command %s." % cmd))
   noDataCnter = 0
   lastData_len = 0
   accumulator = baseComm.PChar(cmd)

   for data in accumulator:
      #if no new data then increment the noDataCnter
      if len(data) == lastData_len:
         noDataCnter += 1
      else:
         lastData_len = len(data)
         noDataCnter = 0

      #if we've not received any new data for a certain number of loops then drive must have sent all data.
      if noDataCnter > waitLoops:
         break
      #Evaluate timeout
      failTimer()
   return data


def get_all_levels_info():
   """
   Переключается на каждый уровень и собирает данные.
   :return: Словарь с информацией по каждому уровню.
   """
   levels = ['1', '2', '3', '4', '5', '6', '7', '8', 'A', 'C', 'E', 'F', 'G', 'H', 'L', 'T']
   level_data = {}

   for level in levels:
      try:
         print(f"Переход на уровень {level}...")
         # Переключение на уровень
         gotoLevel(level)

         # Получение данных текущего уровня
         result = sendDiagCmd("", timeout=30)  # Пустая команда для получения статуса уровня

         # Сохранение результата
         level_data[level] = result
         print(f"Данные для уровня {level}: {result}")
      except Exception as e:
         print(f"Ошибка на уровне {level}: {e}")
         level_data[level] = f"Ошибка: {e}"

   return level_data


# Получение информации обо всех уровнях
all_levels_info = get_all_levels_info()

# Вывод результата
for level, data in all_levels_info.items():
   print(f"Уровень {level}:\n{data}\n")
