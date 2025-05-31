#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Raw Boot Loader Module for negotiating and re-programming serial flash in gemini
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/12/22 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/RawBootLoader.py $
# $Revision: #3 $
# $DateTime: 2016/12/22 00:58:07 $
# $Author: hengngi.yeo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/RawBootLoader.py#3 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#

from Constants import *
from Cell import theCell
import MessageHandler as objMsg
import binascii
import time
import re, os, traceback
import ScrCmds, sptCmds
from SerialCls import baseComm
from Drive import objDut
from FSO import CFSO
from SLIP_transport import CslipTransport
from Rim import objRimType
from Utility import timoutCallback
import serialScreen
from Exceptions import CRaiseException
from  PackageResolution import PackageDispatcher
from ICmdFactory import ICmd
from UartCls import theUart
from UPS import upsObj

CR = '\x0D'
prPat = "(?<!.)\>"
DEBUG = 0

try:
   #Not all CM's support the following functions
   SPortToInitiator
except NameError:
   def SPortToInitiator( flag):
      pass
   def DisableStaggeredStart( flag):
      pass

DEBUG = 0

times_tmo = 1

class objComm(baseComm):
    def __init__(self, *args, **kwargs):
       super(objComm, self).__init__()

#class CFlashLoad(baseComm):
class CFlashLoad(objComm):
   BAD_CMD = 'Bad cmd:'

   def __init__(self, tpmTXTFileKey = None, binFileKey = None, initiator = False, binFilePath = None):
      """
      Base class to implement serial flash programming via TPM text protocol and SLIP binary transmission
      """

      if tpmTXTFileKey is None:
         tpmTXTFileKey ='TXT_TPM'
      if binFileKey is None:
         binFileKey = 'IMG_BIN'

      if objRimType.IsLowCostSerialRiser():
         protocolInPython=1
      else :
         protocolInPython=0
      self.baudRate        = theCell.getBaud()
      #baseComm.__init__(self, self.baudRate)
      objComm.__init__(self, self.baudRate)

      self.initiator = initiator
      self.currLevel       = ''
      self.prPat           = re.compile('\>') #'(?<!.)\>'
      self.dut             = objDut
      self.lastCommand     = ''
      self.blockSize       = 512
      self.slip            = CslipTransport(self.blockSize,protocolInPython)
      self.productionWait  = 0.05
      self.prodWaitMod     = 10
      self.oSerialDiags    = serialScreen.sptDiagCmds()
      if testSwitch.FE_0134030_347506_SAVE_AND_RESTORE:
         self.binFilePath     = binFilePath
      if testSwitch.FE_0117758_231166_NVCACHE_CAL_SUPPORT:

         self.tpmTXTFile = PackageDispatcher(self.dut, tpmTXTFileKey).getFileName()

         self.binFile = PackageDispatcher(self.dut, binFileKey).getFileName()

      if testSwitch.FE_0334158_379676_P_RFWD_FFV_1_POINT_5:
         self.tpmTXTFile = PackageDispatcher(self.dut, tpmTXTFileKey).getFileName()

   def promptRead(self,timeout=30 * times_tmo, raiseException = 1, altPattern = None, accumulator = None, simplePattern = None, bypassDelay = False):
      if testSwitch.virtualRun: return ''
      myTimeout = timoutCallback(timeout,ScrCmds.raiseException,(10566, "Reached timeout when trying to find prompt"))

      result = ''

      if not simplePattern == None:
         prompt = simplePattern
      elif not altPattern == None:
         prompt = re.compile(altPattern)
      else:
         prompt = self.prPat

      matches = False
      for result in accumulator:
         # Sleep for 0.01 second to reduce CM overhead
         # Warning numbers greater than 0.01 were tested (1, 0.1)
         #    But data loss occurred in serial only cells at 38400 baud
         if DEBUG == 0 and bypassDelay == False:
            time.sleep(0.01)

         if not simplePattern == None:
            matches = simplePattern in result
         else:
            matches = prompt.search(result)

         if matches:
            break
         else:
            flashinfo = sptCmds.getFlashCodeMatch(result)
            if flashinfo:
               ScrCmds.raiseException(11231, "FlashLED Error %s" % flashinfo.groupdict() + result + self.lastCommand)
         try:
            myTimeout()
         except:
            if raiseException:
               raise
            else:
               break

      return result

   def promptRead2(self,timeout = 30, raiseException = 1, newPrompt = prPat):
      startTime = time.time()
      curTime = time.time()
      result = ''

      prompt = re.compile(newPrompt)

      while (curTime - startTime) < timeout:
         tmpChar = GChar(readSize = 1)
         result += tmpChar

         matches = prompt.findall(result)
         if len(matches) > 0:
            break
         elif 'FlashLED' in result:
            curTime = startTime + timeout
         else:
            curTime = time.time()
      else:
         if 'FlashLED' not in result and raiseException:
            raise ScriptTestFailure, "Timeout reached waiting for prompt...Recd: %s" % result

         elif 'FlashLED' in result and raiseException:
            raise ScriptTestFailure, "FlashLED Error...Recd: %s" % result

      if DEBUG > 0:
         readTime = curTime - startTime
      return result

   def loadTextTPM(self, TPMfile = None, Signature = None, exitPrompt = None,
                         linesPerPrint = 500, updateBaud = False, verifyPrompt = True, bypassDelay = False):
      """
      Function that transmits the text TPM file instruction set to the serial flash.
      Algorithm
      =========
      Sync Boot prompt to '?' command
      for line in TPM Text file
         @start
         if not line == 'GO'
            nline = strip_whitespace(line) # Remove any EOL characters
            transmit(nline+CR)
            wait for prompt
            if "Bad cmd:" GoTo start
      transmit "GO"
      wait for "Run:0x0000"
      wait for "Send File Now"
      """
      if TPMfile == None:
         if testSwitch.FE_0117758_231166_NVCACHE_CAL_SUPPORT:
            cmdFile = open(os.path.join(ScrCmds.getSystemDnldPath(), self.tpmTXTFile),'r')
         else:
            cmdFile = open(os.path.join(ScrCmds.getSystemDnldPath(), PackageDispatcher(self.dut, 'TXT_TPM').getFileName()),'r')
      else:
         cmdFile = open(os.path.join(ScrCmds.getSystemDnldPath(), TPMfile),'r')

      if exitPrompt == None:
         exitPrompt = 'SEND FILE NOW'

      if verifyPrompt:
         #Put a CR out to sync the comm stucture
         for x in range(10):
            res = ''
            try:
               accumulator = self.PChar('?')
               objMsg.printMsg("Verifying command prompt")
               if DEBUG == 0:
                  time.sleep(1)
               res = self.promptRead(2 * times_tmo,1,altPattern = '>',accumulator = accumulator )

               break
            except:
               objMsg.printMsg(res)
         else:
            ScrCmds.raiseException(10566, "Reached Timeout " + str(self.lastCommand))

      if updateBaud:

         accumulator = self.PBlock('\x42\x52\x20\x35\x0D', noTerminator=1) # BR 36 means "change Baud Rate with a divisor of 0x36=54"
         time.sleep(0.5)
         baudChangeResp = ""
         for data in accumulator:
            baudChangeResp += data
            break

         theUart.setBaud(Baud460800)

         objMsg.printMsg("First Baud Change Response: %s" % repr(baudChangeResp))

         accumulator = self.PBlock('\x42\x52\x20\x35\x0D', noTerminator=1) # BR 36 means "change Baud Rate with a divisor of 0x36=54"
         time.sleep(0.5)
         baudChangeResp = ""
         for data in accumulator:
            baudChangeResp += data
            break

         objMsg.printMsg("Second Baud Change Response: %s" % repr(baudChangeResp))

         time.sleep(1)
      else:
         objMsg.printMsg('No BAUD CHANGE')

      try:
         try:
            if objRimType.IsPSTRRiser():
               objMsg.printMsg("Clearing que")
               self.PBlock(CR * 3)
               data = GChar(readSize = 0)  # will force GChar to wait for 1 sec
               while "Bad cmd:" in data:
                  time.sleep(1)
                  data = GChar(readSize = 0)

            objMsg.printMsg("Sending TPM Text File")
            lineNo = 0
            if DEBUG > 0:
               masterResponse = []
            retries = 0
            for line in cmdFile:
               #Check that we aren't sending blank lines
               if lineNo % linesPerPrint == 0:
                  objMsg.printMsg("Sending line number %d" % lineNo)
               if not line in ['','\n','\r',CR]:
                  if not testSwitch.winFOF and DEBUG == 0:
                     if lineNo % self.prodWaitMod == 0 and bypassDelay == False:
                        time.sleep(self.productionWait)
                  #Give the command 10 retries
                  lineNo += 1

                  for x in range(10):
                     if 'GO' not in line:
                        # send Command
                        startTime = time.time()
                        PBlock(line.strip() + CR)
                        if DEBUG > 0:
                           sendTime = time.time() - startTime
                        # If we didn't tell the TPM to reboot then look for a prompt
                        ret = self.promptRead2(0.5)  # Changed from 2
                        if "Bad cmd:" in ret: retries += 1
                        else: break
                           
                     else:
                        objMsg.printMsg("Reached End of TPM Text File")
                        break
                  else:
                     ScrCmds.raiseException(11044,"TPM Programming command retries exceeded on cmd: %s" % line)

            objMsg.printMsg("Sending GO command for reboot")

            myTimeout = timoutCallback(30 * times_tmo,ScrCmds.raiseException,(10566,  "Failed to receive %s response" % exitPrompt))

            accum = self.PBlock('GO' + CR, noTerminator = 1)
            try:
               for res in accum:
                  if exitPrompt in res:
                     break

                  if Signature != None and Signature in res:
                     objMsg.printMsg("Found Signature %s in %s" % (Signature, `res`))
                     break

                  myTimeout()

            finally:
               objMsg.printMsg("GO Response:\n----------%s\n----------" % res)
               del accum
               if DEBUG > 0:
                  masterResponse.append(res)
         except:
            if DEBUG > 0:
               objMsg.printMsg(''.join(masterResponse))
            raise
      finally:
         objMsg.printMsg("Number of retries: %d" % retries)
         cmdFile.close()


      return res

   def syncBootLoader(self, uSyncCount = 500, syncRetries = 5):
      """
      Power on Loop to insert "U" chars into the UART for Flash to pick up and interrupt boot sequence.
      """
      theUart.setBaud(DEF_BAUD)

      pauseTime = -0.05

      usyncString = uSyncCount*'U'

      for retry in range(5):

         if self.initiator:
            pauseTime += 0.05
            #RimOff(10)
            SetDTRPin(0) == 0
            time.sleep(10)
         else:
            if objRimType.IOInitRiser():
               objMsg.printMsg("Set SPortToInitiator to false")
               SPortToInitiator(False)
               RimOff(10)
            #theCell.powerOff(10)
            SetDTRPin(0) == 0
            time.sleep(10)
         if objRimType.CPCRiser():
            if testSwitch.BF_0164148_321126_IGNORE_GETPWRONSPINUPTIME_FOR_CPSSPTRISER and objRimType.CPCRiserNewSpt(): pass
            else:
               #Notify CPC we want it to send U's at power on
               # 0x10 is 'U' and 0x04 is ESC but the ox04 is also the power on char mode switch in CPC code
               ICmd.GetPwrOnSpinUpTime( 30, 0x14)
         try:
            #Put some output U's on the serial out FIFO
            sTime = time.time()

            
            if self.initiator:
               SPortToInitiator(True)
               data = RimOn(pauseTime = pauseTime, txAfterOn = usyncString)
               SPortToInitiator(True)            
            else:
               if DriveAttributes.get('PCBA_PART_NUM','NONE') in ['100705174','100708196']:
                  testSwitch.SP_TO_POWERBLADE = 1 

               if (testSwitch.SWAPPED_SERIAL_PORT or testSwitch.SP_TO_POWERBLADE):
                  from Carrier import theCarrier
                  theCarrier.configureSPPins()

               if objRimType.IOInitRiser() or objRimType.IsLowCostSerialRiser():
                  objMsg.printMsg("In SIC / Low Cost Tester, use special power on.")
                  time.sleep(0.25)
                  #Neptune2 requires special power on
                  #DriveOn(pauseTime=0,preEscapes=usyncString,postEscapes=usyncString)
                  SetDTRPin(1) == 0
               else:
                  #theCell.powerOn(5000,12000,0)
                  SetDTRPin(1) == 0
               if objRimType.IsPSTRRiser():
                  for x in range(50):
                    self.PBlock(usyncString)
                    time.sleep(.1)
               else: 
                  self.PBlock(usyncString)
               
               if DEBUG > 0:
                  objMsg.printMsg("Send U's %f seconds after power cmd." % (time.time()-sTime))

            #Look for the boot command id
            accumulator = self.PBlock(CR*3)
            #Wait for sync data to be flushed from raw boot loader in flash
            time.sleep(2)
            retData = self.promptRead(10 * times_tmo,1,'Boot Cmds:|Bad cmd:|>',accumulator = accumulator )
            del accumulator
            if DEBUG > 0:
               objMsg.printMsg(retData)
            #set passing status
            objMsg.printMsg("Found Flash program boot prompt")
            objMsg.printMsg("binascii prompt %s" % binascii.b2a_hex(retData))
            objMsg.printMsg("nonbinascii data %s" % retData)
            break
         except:

            objMsg.printMsg("Timeout in Boot syncronizer: %s" % traceback.format_exc())
      else:
         raise


   def loadBinaryImage(self, file=''):
      """
      Function that transmits the binary img file blocks to the dut then waits for "DONE"
      """
      ofso = CFSO()
      theUart.setBaud(Baud115200)
      theCell.disableESlip()
      if file != '':
         FileName = os.path.join(ScrCmds.getSystemDnldPath(), file)
         objMsg.printMsg("Sending Binary IMG File %s" %FileName)
      else:
         if testSwitch.FE_0134030_347506_SAVE_AND_RESTORE and self.binFilePath:
            FileName = self.binFilePath
         elif testSwitch.FE_0117758_231166_NVCACHE_CAL_SUPPORT:
            FileName = os.path.join(ScrCmds.getSystemDnldPath(), self.binFile)
         else:
            FileName = os.path.join(ScrCmds.getSystemDnldPath(), PackageDispatcher(self.dut, 'IMG_BIN').getFileName())

      FileObj = open(FileName,"rb")
      fileSize = ofso.getFileLen(FileName) # a global from above

      objMsg.printMsg("Sending Binary IMG File")
      runtBlock = fileSize % self.blockSize

      for requestBlock in range((fileSize/self.blockSize)+1):
         self.slip.sendSLIPFrame(requestBlock, fileSize, FileObj) # No need resend, retry the entire loadBinaryImage Instead 
         if not testSwitch.winFOF:
            if requestBlock % self.prodWaitMod == 0:
               time.sleep(self.productionWait)

      theUart.setBaud(DEF_BAUD)

      accumulator = self.PBlock('',noTerminator = 1)
      ret = self.promptRead(120 * times_tmo, 0, simplePattern = 'Done', accumulator = accumulator)
      try:
         if not ret.find("Done") > -1:
            ScrCmds.raiseException(10566, "Failed to receive completion status from drive after flash re-programming")
      finally:
         objMsg.printMsg("Return Data:\n%s" % ret)

      if testSwitch.UPS_PARAMETERS:
         upsObj.resetUPS()

   def GetBootPCBASN(self, file):
      pcba_sn = ''
      hda_sn = ''

      objMsg.printMsg("Loading GetBootPCBASN file = %s" % file)

      self.syncBootLoader()
      pcba_sig = 'PCBA S/N:'
      res = self.loadTextTPM(TPMfile = file, Signature = pcba_sig)

      if re.search(pcba_sig, res):
         Mat = re.search('PCBA S/N: ([a-z0-9A-Z]{8,})', res)
         if Mat:
            pcba_sn = Mat.group(1).upper()
            objMsg.printMsg("GetBootPCBASN pcba_sn=%s" % pcba_sn)

         Mat = re.search('HDA\s*S/N\s*: ([a-z0-9A-Z]{8,})', res)
         if Mat and len(Mat.group(1)) >= 8:
            hda_sn = Mat.group(1).upper()
            objMsg.printMsg("GetBootPCBASN hda_sn=%s" % hda_sn)
      else:
         ScrCmds.raiseException(10566, "Cannot find pcba_sn from GetBootPCBASN=%s" % `res`)

      return pcba_sn, hda_sn

   def flashBoard(self):
      """
      Main function that stitches together the different pieces of programming the Serial Flash on the PCBA
      Algorithm
      =========
      Init Dblog
      Syncronize boot up for serial flash programming
      Load Text TPM file
      Load Binary Image file
      Save DbLog Test Time Data
      """
      ######################## DBLOG Implementation- Setup
      curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
      self.dut.objSeq.curRegSPCID = '1'

      ################################################
      try:
         #Power on the drive in bootstrap mode
         startTime = time.time()
         self.syncBootLoader()
         self.dut.sptActive.setMode(self.dut.sptActive.availModes.sptDiag)

         #Put text tpm for binary load
         self.loadTextTPM()

         #Load binary flash image
         self.loadBinaryImage()

      finally:
         execTime = float(time.time()-startTime)
         objMsg.printMsg("Flash Load time: %f" % execTime)

         self.dut.dblData.Tables('TEST_TIME_BY_TEST').addRecord(
            {
            'SPC_ID': self.dut.objSeq.curRegSPCID,
            'OCCURRENCE': occurrence,
            'SEQ':curSeq,
            'TEST_SEQ_EVENT': testSeqEvent,
            'TEST_NUMBER': 1,
            'ELAPSED_TIME': '%.2f' % execTime,
            'PARAMETER_NAME':'FLASH RE-PROGRAM',
            })

         if DEBUG > 0:
            SetShutDownTemperature(None)
   def flashLod(self, filename):
      """
      Main function that stitches together the different pieces of programming the Serial Flash on the PCBA
      Algorithm
      =========
      Init Dblog
      Syncronize boot up for serial flash programming
      Load Text TPM file
      Load Lod file
      Save DbLog Test Time Data
      """
      ######################## DBLOG Implementation- Setup
      curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
      self.dut.objSeq.curRegSPCID = '1'

      ################################################
      try:
         #Power on the drive in bootstrap mode
         startTime = time.time()
         self.syncBootLoader()
         self.dut.sptActive.setMode(self.dut.sptActive.availModes.sptDiag)

         #Put text tpm for binary load
         self.loadTextTPM()
         objMsg.printMsg("loadTextTPM Flash Load time file=%s" %filename)
         #Load lod file
         objMsg.printMsg("loadLodFile file=%s" %filename)
         #self.loadLodFile(filename)
         self.loadBinaryImage(filename)
         objMsg.printMsg("loadLodFile Flash Load time")
      finally:
         execTime = float(time.time()-startTime)
         objMsg.printMsg("Flash Load time: %f" % execTime)

         self.dut.dblData.Tables('TEST_TIME_BY_TEST').addRecord(
                     {
                     'SPC_ID': self.dut.objSeq.curRegSPCID,
                     'OCCURRENCE': occurrence, 
                     'SEQ':curSeq,
                     'TEST_SEQ_EVENT': testSeqEvent,
                     'TEST_NUMBER': 1,
                     'ELAPSED_TIME': '%.2f' % execTime,
                     'PARAMETER_NAME':'FLASH Lod File',
                     })

         if DEBUG > 0:
            SetShutDownTemperature(None)            
