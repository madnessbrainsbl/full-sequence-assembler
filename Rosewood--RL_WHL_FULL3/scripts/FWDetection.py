#####################################################################
#
# $RCSfile:  $SED-Serial-Personalize.py
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/12/27 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $Revision: #5 $2.1.0
# $Date: 2016/12/27 $09/24/12
# $Author: hengngi.yeo $brandon.haugrud
#
#####################################################################

# built-in modules
import binascii
import os
import pickle
import struct
import time
import traceback

# custom modules
from Drive import objDut
import MessageHandler as objMsg
from PackageResolution import PackageDispatcher
from PowerControl import objPwrCtrl
import ScrCmds
import SED_Serial
from Serial_Download import CSeaSerialRFWDTPMs
import sptCmds
from Test_Switches import testSwitch
from UartCls import theUart

if testSwitch.virtualRun:
   from cmEmul import ConfigVars, CN, riserType

# The following debug flag creates LOTS of log messages.
#  Disable for production no matter what!
RFWD_DEBUG = False
#RFWD_DEBUG = True


class RFWDetection:

   RFWD_PASSED = 1
   RFWD_FAILED = 0

   RFWD_SEVERITY_DEFAULT                    = 0
   RFWD_SEVERITY_HIGH_PRIORITY_ESCALATION   = 1
   RFWD_SEVERITY_MEDIUM_PRIORITY_ESCALATION = 2
   RFWD_SEVERITY_RETRY_ESCALATION           = 3

   RFWD_EC_CSEFW_DETECTED_SIGNATURE_MISMATCH     = 48970
   RFWD_EC_PICKLE_FILE_EXP_REC_MISMATCH          = 48999
   RFWD_EC_DETECTED_SIG_VS_TRUSTED_SIG_MISMATCH  = 48972
   RFWD_EC_TOO_FEW_SEGMENTS                      = 49000
   RFWD_EC_TOO_MANY_SEGMENTS                     = 49003
   RFWD_EC_PICKLE_FILE_UNAVALIABLE               = 48998
   RFWD_EC_PKLFILE_LODFILE_NAME_MISCOMPARE       = 49030
   RFWD_EC_INIT_TPM_DL_ERROR                     = 49013
   RFWD_EC_EXTRACTION_TPM_DL_ERROR               = 49012
   RFWD_EC_CORRUPTED_OVLY_SYS_FILE               = 49002
   RFWD_EC_CSEFW_DETECTED_SIGNATURE_EXTR_FAILURE = 48971
   RFWD_EC_RFWD_TEST_TIMEOUT                     = 49001
   RFWD_EC_RFWD_STREAM_XFER_ERROR                = 49011
   RFWD_EC_RFWD_CHECKSUM                         = 48997
   RFWD_EC_RWFD_ESLIP_ERROR                      = 48993

   RFWD_EC_SEVERITY_MAP = {
      RFWD_EC_CSEFW_DETECTED_SIGNATURE_MISMATCH     : RFWD_SEVERITY_HIGH_PRIORITY_ESCALATION,
      RFWD_EC_PICKLE_FILE_EXP_REC_MISMATCH          : RFWD_SEVERITY_HIGH_PRIORITY_ESCALATION,
      RFWD_EC_DETECTED_SIG_VS_TRUSTED_SIG_MISMATCH  : RFWD_SEVERITY_HIGH_PRIORITY_ESCALATION,
      RFWD_EC_TOO_FEW_SEGMENTS                      : RFWD_SEVERITY_MEDIUM_PRIORITY_ESCALATION,
      RFWD_EC_TOO_MANY_SEGMENTS                     : RFWD_SEVERITY_MEDIUM_PRIORITY_ESCALATION,
      RFWD_EC_PICKLE_FILE_UNAVALIABLE               : RFWD_SEVERITY_MEDIUM_PRIORITY_ESCALATION,
      RFWD_EC_PKLFILE_LODFILE_NAME_MISCOMPARE       : RFWD_SEVERITY_MEDIUM_PRIORITY_ESCALATION,
      RFWD_EC_INIT_TPM_DL_ERROR                     : RFWD_SEVERITY_MEDIUM_PRIORITY_ESCALATION,
      RFWD_EC_EXTRACTION_TPM_DL_ERROR               : RFWD_SEVERITY_MEDIUM_PRIORITY_ESCALATION,
      RFWD_EC_CORRUPTED_OVLY_SYS_FILE               : RFWD_SEVERITY_MEDIUM_PRIORITY_ESCALATION,
      RFWD_EC_CSEFW_DETECTED_SIGNATURE_EXTR_FAILURE : RFWD_SEVERITY_MEDIUM_PRIORITY_ESCALATION,
      RFWD_EC_RFWD_TEST_TIMEOUT                     : RFWD_SEVERITY_RETRY_ESCALATION,
      RFWD_EC_RFWD_STREAM_XFER_ERROR                : RFWD_SEVERITY_RETRY_ESCALATION,
      RFWD_EC_RFWD_CHECKSUM                         : RFWD_SEVERITY_RETRY_ESCALATION,
      RFWD_EC_RWFD_ESLIP_ERROR                      : RFWD_SEVERITY_RETRY_ESCALATION,
   }

   RFWD_ENG_PN_RANGE_START = 985

   RFWD_SIGS_FILENAME_LENGTH_LIMIT = 96

   keyMapping = {
   '(22,00)' : ('LOD_SEG_TYPE_BOOT_CONT', 'ITCM_SIGN_PATTERN'),
   '(22,01)' : ('LOD_SEG_TYPE_BOOT_CONT', 'IDBA_SIGN_PATTERN'),
   '(22,02)' : ('LOD_SEG_TYPE_BOOT_CONT', 'ALF_SIGN_PATTERN'),
   '(26,00)' : ('LOD_SEG_TYPE_DISC_CONT', 'DISC_SIGN_PATTERN'),
   '(43,00)' : ('LOD_SEG_TYPE_SERVO_CONT', 'SERV_SIGN_PATTERN'),
   '(4A,00)' : ('LOD_SEG_TYPE_OVLY_CONT', 'DITS_OVLY_SIGN_PATTERN'),
   '(4A,01)' : ('LOD_SEG_TYPE_OVLY_CONT', 'DICL_OVLY_SIGN_PATTERN'),
   '(4A,04)' : ('LOD_SEG_TYPE_OVLY_CONT', 'DCMD_OVLY_SIGN_PATTERN'),
   '(4A,05)' : ('LOD_SEG_TYPE_OVLY_CONT', 'DETS_OVLY_SIGN_PATTERN'),
   '(4B,00)' : ('LOD_SEG_TYPE_MLAB_CONT', 'MATL_SIGN_PATTERN'),
   }

   def __init__(self):
      self.dut = objDut
      self.userDataTable = 'P_USER_REQUESTED_DATA'

   def raiseException(self, ec, msg):
      self.dut.driveattr['RFWD_SEVERITY'] = self.RFWD_EC_SEVERITY_MAP.get(ec, self.dut.driveattr.get('RFWD_SEVERITY', 0))
      ScrCmds.raiseException(ec, msg)

   def debugMsg(self, titleOrMsg="", msg=""):
      if RFWD_DEBUG:
         printStr = "RFWD- "
         if msg: # titleOrMsg is title
            printStr += "% 16s: %s" % (titleOrMsg, msg)
         else:   # titleOrMsg is msg
            printStr += str(titleOrMsg)
         objMsg.printMsg(printStr, objMsg.CMessLvl.IMPORTANT)

   def rfwd_PBlock(self, chars):
      self.debugMsg("PBlocking", repr(chars))
      PBlock(chars)

   def rfwd_GChar(self, *args, **kwargs):
      response = GChar(*args, **kwargs)
      self.debugMsg("GChar Response", repr(response))
      return response

   def run(self, RFWDAttemptMax=3, RFWDFirstErr=0):

      objMsg.printMsg("Rogue Firmwware Detect")

      if riserType == 'MIRKWOOD':
         objMsg.printMsg("RFWD cannot run with Mirkwood systems.")
         return self.RFWD_PASSED

      if testSwitch.virtualRun:
         objMsg.printMsg("RFWD cannot run in VE.")
         return self.RFWD_PASSED

      """
      try:
         tab = int(self.dut.partNum[-3:])
         if self.RFWD_ENG_PN_RANGE_START <= tab:
            # Engineering Tab, skip RFWD
            objMsg.printMsg("Engineering Part Number, Skipping RFWD.")
            if RFWD_DEBUG:
               self.debugMsg("Just Kidding! Running RFWD because RFWD_DEBUG is ON.")
            else:
               return self.RFWD_PASSED
      except ValueError:
         # non-integer tab, run RFWD
         pass
      """

      # replace auto assign of '?' to '' if any
      if self.dut.driveattr['RFWD_SIGNATURE_1'] == '?':  
         self.dut.driveattr['RFWD_SIGNATURE_1'] = ''
         #objMsg.printMsg("RFWD_SIGNATURE_1:  %s" % self.dut.driveattr['RFWD_SIGNATURE_1'])
      if self.dut.driveattr['RFWD_SIGNATURE_2'] == '?':  
         self.dut.driveattr['RFWD_SIGNATURE_2'] = ''
         #objMsg.printMsg("RFWD_SIGNATURE_2:  %s" % self.dut.driveattr['RFWD_SIGNATURE_2'])
      if self.dut.driveattr['RFWD_SIGNATURE_3'] == '?':  
         self.dut.driveattr['RFWD_SIGNATURE_3'] = ''
         #objMsg.printMsg("RFWD_SIGNATURE_3:  %s" % self.dut.driveattr['RFWD_SIGNATURE_3'])

      FIS_SigsFilename = self.dut.driveattr.get("RFWD_SIGNATURE_1", '') + \
                         self.dut.driveattr.get("RFWD_SIGNATURE_2", '') + \
                         self.dut.driveattr.get("RFWD_SIGNATURE_3", '')

      # check if using a pre-saved SIGS file else use live value from codes.py
      if FIS_SigsFilename == '':
         sigs = PackageDispatcher(self.dut, 'SIGS').getFileName()

         if not sigs:
            msg = "Rogue Firmware Detect missing SIGS.PKL file"
            objMsg.printMsg(msg)
            self.raiseException(self.RFWD_EC_PICKLE_FILE_UNAVALIABLE, msg)

         if self.RFWD_SIGS_FILENAME_LENGTH_LIMIT < len(sigs):
            failStr = "* * * Target File name too long.  Must be less than 96 characters total.  Reduce TGT code file name size and SIGS file name size."
            self.raiseException(14886, failStr)

         objMsg.printMsg("Codes.py SIGS file used:  %s" % sigs)
      else:
         sigs = FIS_SigsFilename
         objMsg.printMsg("RFWD_SIGNATURE_1,2,3 file used:  %s" % sigs)

      objMsg.printMsg("Rogue Firmware Detect 1.5 Process Running")

      for attempt in range(RFWDAttemptMax):
         try:
            sigsPath = os.path.join(ScrCmds.getSystemDnldPath(), sigs)

            objMsg.printMsg("SIGS Path: %s" % sigsPath)

            pklDB = pickle.load(open(sigsPath,'r'))
         except (OSError, IOError, AttributeError, KeyError), e:
            # OSError, IOError         to cover open()
            # AttributeError, KeyError to cover pickle.load()
            objMsg.printMsg(str(e))
            objMsg.printMsg(traceback.format_exc())
            objMsg.printMsg("Attempt to open pickle file failed.  Failed attempt %s of %s"%(attempt+1,RFWDAttemptMax))
         else:
            break
      else:
         self.raiseException(self.RFWD_EC_PICKLE_FILE_UNAVALIABLE,
                             'Signature Pickle file not available during RFWD')

      tgtPklSigs = self.GetPickleValues(pklDB)

      if RFWD_DEBUG: 
         objMsg.printMsg("Pickle file")
         for key,value in tgtPklSigs.items():
            objMsg.printMsg("Key: %s, Value: %s"%(str(key),str(value)))

      for attempt in range(RFWDAttemptMax):
         try:
            oFlashLoad = CSeaSerialRFWDTPMs(self.dut).SeaSerialRFWDTPMs()

            time.sleep(5)

            pTables = self.CollectSignatures(oFlashLoad)

         except ScriptTestFailure, (failureData):
            objMsg.printMsg("* * * Rogue Firmware Detect Process failed.  Failed attempt %s of %s * * *"%(attempt+1,RFWDAttemptMax))
            ec_code = failureData[0][2]
            if not RFWDFirstErr:
               RFWDFirstErr = ec_code

         except ScrCmds.CRaiseException, (failureData):
            objMsg.printMsg("* * * Rogue Firmware Detect Process failed CRaiseException.  Failed attempt %s of %s * * *"%(attempt+1,RFWDAttemptMax))
            ec_code = failureData[0][2]
            if not RFWDFirstErr:
               RFWDFirstErr = ec_code
         else:
            break    
      else:
         self.raiseException(RFWDFirstErr, 'Initial Error during RFWD retry loop')

      if RFWD_DEBUG: 
         self.debugMsg("All Collected Signatures:")
         for key,value in pTables.items():
            objMsg.printMsg("Key: %s, Value: %s"%(str(key),str(value)))

      self.CompareKeys(tgtPklSigs, pTables)

      objPwrCtrl.powerCycle(ataReadyCheck = False)

      self.dut.driveattr['RFWD_SEVERITY'] = 'PASS'  # Required to set to Pass for completed RFWD passer

      return self.RFWD_PASSED

   def FletcherChecksum32(self,data = ''):
      sum1 = 0xFFFF
      sum2 = 0xFFFF

      for x in range(0,len(data),2):
         d = int(binascii.b2a_hex(data[x:x+2]),16)
         sum1 += d
         sum2 += sum1

      sum1 = (sum1 & 0xFFFF) + (sum1 >> 16)
      sum2 = (sum2 & 0xFFFF) + (sum2 >> 16)

      sum1 = (sum1 & 0xFFFF) + (sum1 >> 16)
      sum2 = (sum2 & 0xFFFF) + (sum2 >> 16)

      return (sum2 << 16) | sum1

   def ParseAndValidateSignature(self, data):
      # - First validate the data is the correct format
      # - If not we need to retry the process

      if RFWD_DEBUG:
         objMsg.printMsg("* * * ParseAndValidateSignature")
         self.debugMsg("data", repr(data))

      if data.count(':') < 4:
         failStr = "Signature streaming issue - Not enough data returned"
         self.raiseException(self.RFWD_EC_RFWD_STREAM_XFER_ERROR, failStr)

      header = data[data.find('('):data.find(')')+1]
      if header in self.keyMapping.keys():
         key = self.keyMapping[header]
         key += 'SYSTEM_COPY_0',
         #Need for verifying checksum
         dataForCalc = header[1:3] + header[4:6]
      else:
         failStr = "Signature streaming issue - Returned header %s could not be mapped" %header
         self.raiseException(self.RFWD_EC_RFWD_STREAM_XFER_ERROR,failStr)

      sigIndx = data.find(':') + 1
      if data.find(':',sigIndx+256) < 0:
         failStr = "Signature streaming issuue - Signature size is too small"
         self.raiseException(self.RFWD_EC_RFWD_STREAM_XFER_ERROR,failStr)
      else:
         signature = binascii.b2a_hex(data[sigIndx:sigIndx+256])
         dataForCalc += signature

      checkSumIndx = data.find(':',sigIndx+256) + 1
      if data.find(':',checkSumIndx+4) < 0:
         failStr = "Returned data did not include full checksum value"
         self.raiseException(self.RFWD_EC_RFWD_STREAM_XFER_ERROR,failStr)
      else:
         checkSum = binascii.b2a_hex(data[checkSumIndx:checkSumIndx+4])

      statusIndx = data.find(':',checkSumIndx+4) + 1
      if data.find(':',statusIndx+1) < 0:
         failStr = "Signature streaming issue - Status indicator iss of the wrong size"
         self.raiseException(self.RFWD_EC_RFWD_STREAM_XFER_ERROR,failStr)
      else:
         status = data[statusIndx:statusIndx+1].upper()

      # Validate Passing Flag
      if status == 'F':
         failStr = "Signature returned a Failing Status"
         self.raiseException(self.RFWD_EC_CSEFW_DETECTED_SIGNATURE_MISMATCH,failStr)
      elif status != 'P':
         failStr = "Signature streaming issue - Returned an invalid status of %s" %status
         self.raiseException(self.RFWD_EC_RFWD_STREAM_XFER_ERROR,failStr)

      # Validate Checksum Matches
      calcCheckSum = self.FletcherChecksum32(binascii.a2b_hex(dataForCalc))
      strCalcCheckSum = binascii.b2a_hex(struct.pack('>HH',calcCheckSum&0xFFFF,calcCheckSum>>16))
      if strCalcCheckSum != checkSum:
         failStr = "Calculated checksum doesn't match returned checksum"
         self.raiseException(self.RFWD_EC_RFWD_STREAM_XFER_ERROR,failStr)

      return key,signature

   def GetInitialSignatures(self, oFlashLoad):

      if RFWD_DEBUG: objMsg.printMsg("* * * GetInitialSignatures")
      collectedSigs = {}

      #start_time = time.time()   #YHN
      numSigsLeft = 5
      RETRIES = 20

      while numSigsLeft:
         self.debugMsg("numSigsLeft", numSigsLeft)
         self.rfwd_PBlock('b')

         start_time = time.time()   #YHN
         serialData = ''
         foundASig = False
         retry = 0

         while not foundASig:

            if (time.time() - start_time) > 5:
               failStr = "Did not find first 5 streaming signatures, %d remaining" % numSigsLeft
               objMsg.printMsg(failStr, objMsg.CMessLvl.IMPORTANT)
               self.debugMsg("serialData", repr(serialData))
               retry += 1
               if retry < RETRIES:           #should reset here
                  start_time = time.time()
                  serialData = ''            #YHN
                  objMsg.printMsg("Retrying %s" %retry)
                  self.rfwd_PBlock('b')
               else:
                  self.raiseException(self.RFWD_EC_RFWD_STREAM_XFER_ERROR, failStr)

            serialData += self.rfwd_GChar()

            # Ignore ':' in data that the drive spewed during bootup like "TCC:"
            start_indx = serialData.find('+(')
            if serialData.count("+(") and serialData[serialData.find('+('):].count(":") >= 4:
               self.debugMsg("Found a Signature!")
               foundASig = True
               # Read few more times to capture the trailing "P:" string
               for i in range(20):
                  if serialData[-3:] in [':P:',':F:'] and len(serialData[start_indx:]) >= 271:
                     break
                  else:
                     time.sleep(1)
                     serialData += self.rfwd_GChar()
                  
               retry = 0     #YHN
               if RFWD_DEBUG: 
                  self.debugMsg("Print serialData")
                  self.debugMsg("serialData", repr(serialData))

         key,sig = self.ParseAndValidateSignature(serialData[serialData.find('+('):])

         if RFWD_DEBUG:
            self.debugMsg("key", repr(key))
            self.debugMsg("sig", repr(sig))

         collectedSigs[key] = sig.upper()

         numSigsLeft -= 1

         if numSigsLeft == 1:
            self.rfwd_PBlock('\x1A')     #YHN
         elif numSigsLeft == 3:
            self.debugMsg("Setting Baud to 38400")
            theUart.setBaud(Baud38400)

      objMsg.printMsg("* * * Collected all 5 Streaming TPM Signatures!")
      if RFWD_DEBUG: 
            self.debugMsg("Collected Signatures - using Streaming TPM:")
            for key,value in collectedSigs.items():
               objMsg.printMsg("Key: %s, Value: %s"%(str(key),str(value)))

      return collectedSigs

   def confirmPrompt(self,msg):
      data = self.rfwd_GChar(readSize=512)
      if msg in data:
         return True
      else:
         return False

   def DitsGetFWSignatures(self):

      if RFWD_DEBUG: objMsg.printMsg("* * * DitsGetFWSignatures")

      SED_Serial.ditsLockUnlock(lockPort = 0)
      signatures = {}

      verifyStatusMapping = {
         1  : 'Current Primary Copy Vaild Verification',
         2  : 'Current Redundant copy 1 failed verifiction',
         3  : 'Current Redundant copy 2 failed verifiction',
         11 : 'Alternate Primary copy failed verification',
         12 : 'Alternate Reduntantt copy 1 failed verification',
         13 : 'Alternate Reduntantt copy 2 failed verification',
      }

      #Iterate through all of the signature segments
      for key in self.keyMapping:
         packet = "\xE8\x01\x01\x00\x01\x00\x00\x00"  + binascii.a2b_hex(key[1:3]) + binascii.a2b_hex(key[4:6])
         sessionType = 'Retrieve Segment and Segment SubType %s' %(key)
         if RFWD_DEBUG:
            SED_Serial.sendPacket(frame = packet, m_type = sessionType,showFrame=1,ditsCommand=1)
         else:
            SED_Serial.sendPacket(frame = packet, m_type = sessionType,showFrame=0,ditsCommand=1)
         time.sleep(1)
         if RFWD_DEBUG:
            signature = SED_Serial.getPacket(m_type = sessionType,showFrame=1,ditsCommand=1,rtnRawPacket=1)
         else:
            signature = SED_Serial.getPacket(m_type = sessionType,showFrame=0,ditsCommand=1,rtnRawPacket=1)
         time.sleep(1)
         if len(signature) > 16:
            #Validate Checksum
            calcCheckSum = self.FletcherChecksum32(signature[16:-4])
            checkSum = binascii.b2a_hex(signature[-4:])
            sigStatus = int(binascii.b2a_hex(signature[-6:-4]))
            strCalcCheckSum = binascii.b2a_hex(struct.pack('>HH',calcCheckSum&0xFFFF,calcCheckSum>>16))
            if sigStatus in verifyStatusMapping:
               failStr = "Signature Mismatch when retrieving signatures - %s" %verifyStatusMapping[sigStatus]
               self.raiseException(self.RFWD_EC_CSEFW_DETECTED_SIGNATURE_MISMATCH,failStr)
            elif strCalcCheckSum != checkSum:
               failStr = "Calculated checksum doesn't match returned checksum"
               self.raiseException(self.RFWD_EC_RFWD_CHECKSUM,failStr)
            elif sigStatus != 0:
               failStr = "Returned back and error status of %d which is not documented" %sigStatus
               self.raiseException(self.RFWD_EC_CSEFW_DETECTED_SIGNATURE_MISMATCH,failStr)
            else:
               signatures[(self.keyMapping[key] + ('SYSTEM_COPY_1',))] = binascii.b2a_hex(signature[22:-6]).upper()

      if RFWD_DEBUG: 
         self.debugMsg("Collected signature using DitsGetFWSignatures:")
         for key,value in signatures.items():
            objMsg.printMsg("Key: %s, Value: %s"%(str(key),str(value)))

      if signatures:
         objMsg.printMsg("* * * Collected Signatures using DITS!")

      return signatures

   def CollectSignatures(self, oFlashLoad):

      if RFWD_DEBUG: objMsg.printMsg("* * * CollectSignatures")
      
      data = ''
      signatureDict = {}

      signatureDict = self.GetInitialSignatures(oFlashLoad)

      #Transition Drive to ESLIP Mode to get remaining signatures via DITS
      self.rfwd_PBlock('\x1A')
      time.sleep(20)
      start_time = time.time()

      while not self.confirmPrompt(msg = 'F3 T>'):
         time.sleep(3)
         if (time.time() - start_time) > 60:
            self.raiseException(self.RFWD_EC_RFWD_STREAM_XFER_ERROR, 'Did not find first 5 signature')
         time.sleep(3)
         self.rfwd_PBlock('\x1A')

      self.rfwd_PBlock('\x14')
      if not self.confirmPrompt(msg = 'ESLIP mode'):
         self.raiseExceptionn(self.RFWD_EC_RWFD_ESLIP_ERROR, 'Fail to set ESLIP')

      try:
         UseHardSRQ(False)
         UseESlip(1)
         theUart.setBaud(Baud38400)
         time.sleep(3)
      except Exception, e:
         self.raiseException(self.RFWD_EC_RWFD_ESLIP_ERROR, 'ESlip Failed to re-establish communications after TPM download during RFWD:\n%s' % str(e))

         
      from TCG import CTCGPrepTest
      oTCG = CTCGPrepTest(self.dut, SPMode = 1)
      oTCG.CheckFDEState(SPMode = 1)
      if self.dut.LifeState == "80":
         objMsg.printMsg("Drive is in USE state, will unlock ports.")
         objMsg.printMsg("TCGComplete = %s" % (self.dut.TCGComplete,))
         oTCG.UnlockDiagUDE(SPMode = 1)
      else:
         objMsg.printMsg("Drive is NOT in USE state, unlock is not required")

      signatureDict.update(self.DitsGetFWSignatures())

      return signatureDict

   def CompareKeys(self, tgtPklSigs, extractedSigs):
      """Verify that all SIGs from the drive (extractedSigs), match up with
      SIGs from the picklefile, with the exception of SIGs that are on the
      bypass list.
      """
      if RFWD_DEBUG: objMsg.printMsg("* * * CompareKeys")

      # RFWD 1.5
      SigBypassList = [  # List of Signatures that are allowed to by bypassed
      ('LOD_SEG_TYPE_MLAB_CONT',  'MATL_SIGN_PATTERN', 'SYSTEM_COPY_0'),
      ('LOD_SEG_TYPE_MLAB_CONT',  'MATL_SIGN_PATTERN', 'SYSTEM_COPY_1'),
      ('LOD_SEG_TYPE_MLAB_CONT',  'MATL_SIGN_PATTERN', 'SYSTEM_COPY_2'),
      ('LOD_SEG_TYPE_SERVO_CONT', 'SERV_SIGN_PATTERN', 'SYSTEM_COPY_0'),
      ('LOD_SEG_TYPE_SERVO_CONT', 'SERV_SIGN_PATTERN', 'SYSTEM_COPY_1'),
      ('LOD_SEG_TYPE_SERVO_CONT', 'SERV_SIGN_PATTERN', 'SYSTEM_COPY_2')]

      failFlag = 0

      for key,value in extractedSigs.items():
         if RFWD_DEBUG:
            objMsg.printMsg("Key: %s, Value: %s"%(str(key),str(value)))

         if key in SigBypassList:
            objMsg.printMsg("Allowed SigBypass:  %s"%(str(key)))
         elif key[:-1] in tgtPklSigs:
            if value == tgtPklSigs[key[:-1]]:
               objMsg.printMsg("Verified Sig:  %s"%(str(key)))
            else:
               failFlag = 1
               objMsg.printMsg('Signature Compare failed: %s' % str(key))
               objMsg.printMsg('Drive Value: %s' % extractedSigs[key])
               objMsg.printMsg('Packaged Value: %s' % tgtPklSigs[key[:-1]])
         else:
            failStr = 'CSEFW Detected Signature Extra Failure. Did not find extracted key %s in PKL file'%str(key)
            self.raiseException(self.RFWD_EC_CSEFW_DETECTED_SIGNATURE_EXTR_FAILURE, failStr)

      if not failFlag:
         objMsg.printMsg('Successful Signature Comparison')
      else:
         self.raiseException(self.RFWD_EC_DETECTED_SIG_VS_TRUSTED_SIG_MISMATCH,
                             'Detected Sig vs Trusted Sig Mismatch')

   def GetPickleValues(self, db):
      """Read the pickle file data then reformat for comparison.
      """

      return {key[1:3]: binascii.b2a_hex(db[key])[-512:].upper() for key in db}

fwDetect = RFWDetection()
