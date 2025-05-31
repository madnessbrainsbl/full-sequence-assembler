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
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_stHandler.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_stHandler.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
import ScrCmds
import MessageHandler as objMsg
import time
from Drive import objDut

import sptCmds
from PowerControl import objPwrCtrl
from Rim import objRimType, SATA_RiserBase, SAS_RiserBase, theRim
import traceback
from Cell import theCell
from TestParamExtractor import TP
from sptCmds import objComMode
from Exceptions import CFlashCorruptException 
import base_BaudFunctions
#**********************************************************************************************************
#**********************************************************************************************************
class st_HandlerBase:
   """
   Class implements the basic handler for st functions. Including retries and special case detection (flash corruption)
   """
   def __init__(self):
      self.dut = objDut

   def genericHandleException(self, callerRef, exceptType, failureData, ec, pwrCycleRetryList, retry, testNum, retryMode):
      """
      Handle generic exceptions and retries
      """
      self.detectFlashCorruptWrite(ec, testNum)

      if ec in [11049,11087] and testNum == 178 and testSwitch.WA_0299052_517205_RECONNECT_AND_CONTINUE_ON_11049_ERR_FOR_T178:
        objMsg.printMsg("Error occurred! Trying to re-connect")
        objMsg.printMsg("Flash Update retry w/o power cycle. Retry count = %s" % (str(retry)))

        try:
            baudList, baudRate = theRim.getValidRimBaudList(PROCESS_HDA_BAUD)
            baudList = list(baudList)
            cellBaud = self.dut.baudRate
            base_BaudFunctions.sendBaudCmd(min(baudList),self.dut.baudRate)
            objMsg.printMsg("Connection with drive established successfully")
            retry -= 1            
        except:
            objMsg.printMsg("Can't re-connect to drive")
            raise CFlashCorruptException, "Flash corruption detected"
        if retry < 0:
            objMsg.printMsg("Retry Limit exceeded!!! Can't re-connect to drive.")
            raise CFlashCorruptException, "Flash corruption detected"
      elif (ec in pwrCycleRetryList) and (retry) > 0:
         self.retryFunctionHandler(callerRef, retryMode, testNum)
         retry -= 1
         if retry < 0:
            raise exceptType, failureData
      else:
         objMsg.printMsg("ErrorCode(EC) = %s,  CurrentState = %s" %(ec,self.dut.currentState))
         if (testSwitch.FE_SGP_517205_TIMEOUT_REZAP_ATTRIBUTE and  ec == 11049 and self.dut.currentState == 'D_FLAWSCAN' and testNum == 109 ):
            try:
                fmtData = self.dut.dblData.Tables('P126_SRVO_FLAW_TRACE').tableDataObj()
                err_count = {}
                objMsg.printMsg('Total Error Count = %d' % (len(fmtData)))
                for i in xrange(len(fmtData)):
                    D_Head      = int(fmtData[i]['HD_PHYS_PSN'])
                    #DATA_ZONES  = int(fmtData[i]['DATA_ZONE'])
                    ERR_CNT     = int(fmtData[i]['ERRCODE'])
                    err_count.setdefault(D_Head,0)
                    err_count[D_Head] += 1#ERR_CNT
                for keys  in err_count:
                      objMsg.printMsg('Head %d has %d ERRORS' % (keys,err_count[keys]))
                #rezap_head  = int (max(err_count.keys(),key=lambda x:err_count[x]))
                #rezap_head  = int (max(err_count,key=err_count.get))
                rezap_head = 0
                for k in err_count:
                    if err_count[k] == max(err_count.values()):
                        rezap_head = k
                    else:
                        continue
                    objMsg.printMsg('Head with max error =  %d' % rezap_head )
                    if not self.dut.rezapAttr & (1 << rezap_head):
                        self.dut.rezapAttr |= 1 << rezap_head + 8   # forced re_zap on the high error count head
                    else:
                        objMsg.printMsg('Head %d  has already reZAP' % (rezap_head))
                        if error_code in TP.stateRerunParams['states']['D_FLAWSCAN']:
                            TP.stateRerunParams['states']['D_FLAWSCAN'].remove(error_code)


            except:
                raise exceptType, failureData
         raise exceptType, failureData

      return retry
   #------------------------------------------------------------------------------------------------------#
   def detectFlashCorruptWrite(self, ec, testNum):
      """
      Detect 178 causing flash corruption
      """
      if ec in [11049,11087] and testNum == 178 and not testSwitch.WA_0299052_517205_RECONNECT_AND_CONTINUE_ON_11049_ERR_FOR_T178:
         from Exceptions import CFlashCorruptException
         if testSwitch.FE_0112376_231166_RAISE_11049_EC_WITH_CFLASHCORRUPTEXCEPTION:
            ScrCmds.raiseException(11049, "Flash corruption detected", CFlashCorruptException)
         else:
            raise CFlashCorruptException, "Flash corruption detected"

   #------------------------------------------------------------------------------------------------------#
   def handleLastDitchException(self, callerRef, failureData, pwrCycleRetryList, retry, testNum, retryMode):
      """
      Last ditch- for timeout retries
      """
      if ec == 11049 and testSwitch.WA_0112479_231166_POWERCYCLE_AND_CONTINUE_ON_11049_ERR_FOR_BANSHEE_1_0:
         #power cycle and move on
         objPwrCtrl.powerCycle(useESlip=1)
         return -1

      #major hack...
      if ec == 11049 and testSwitch.WA_0112479_231166_POWERCYCLE_AND_CONTINUE_ON_11049_ERR_FOR_BANSHEE_1_0:
         #power cycle and move on
         objPwrCtrl.powerCycle(useESlip=1)
         return -1
      raise Exception, failureData
      #return retry

   #------------------------------------------------------------------------------------------------------#
   def handleScriptTestFailure(self, callerRef, failureData, pwrCycleRetryList, retry, testNum, retryMode):
      """
      Generic failure handler for st calls- loads ec from failureData
      """
      ec = failureData[0][2]

      return self.genericHandleException(callerRef, ScriptTestFailure, failureData, ec, pwrCycleRetryList, retry, testNum, retryMode)

   #------------------------------------------------------------------------------------------------------#
   def parseTestTimeException(self, failureData, pwrCycleRetryList, retry, testNum):
      """
      Parses the test time exception into time used and will raise ScripttestFailure if not raised for easier handling
      """
      ec = 0
      if str(failureData).find('Test Time Expired') > -1 or 'FOFSerialTestTimeout' in failureData \
      or 'FOFSerialTestTimeout' in str(failureData) or \
      'ESLIP ERROR' in str(failureData) or \
      'receiveBlock (ESlip) failed' in str(failureData):
         ec = 11049
         if testNum == 178:
            return ec
         if not ec in pwrCycleRetryList or retry < 0:
            import re
            match = re.search('elapsedTime:\s*(?P<elapsedTime>\d+)',str(failureData))
            if match:
               timeout = match.groupdict()['elapsedTime']
            else:
               timeout = 600
            (mV3,mA3),(mV5,mA5),(mV12,mA12)  = GetDriveVoltsAndAmps()
            raise ScriptTestFailure, (('st',testNum,ec,timeout),(ReportTemperature()/10.0),(mV12,mV5))
      else:
         objMsg.printMsg("Test timeout not found: exception info: %s" % str(failureData))
      return ec

   #------------------------------------------------------------------------------------------------------#
   def parseFOFSerialCommErrorException(self, ec, failureData, testNum):
      """
      Handles FOFSerialCommError raised by CM to raise as ScriptTestFailure for easier handling
      """
      if 'FOFSerialCommError' in failureData or 'FOFSerialCommError' in str(failureData) or isinstance(failureData,FOFSerialCommError) :
         ec = 11087
         if testNum == 178:
            return ec
         (mV3,mA3),(mV5,mA5),(mV12,mA12)  = GetDriveVoltsAndAmps()
         raise ScriptTestFailure, (('st',testNum,ec,600),(ReportTemperature()/10.0),(mV12,mV5))
      return ec

   #------------------------------------------------------------------------------------------------------#
   def handleGenericFailure(self, callerRef, failureData, pwrCycleRetryList, retry, testNum, retryMode):
      """
      Generic handler that sends failure info to subordinate handlers
      """
      ec = self.parseTestTimeException(failureData, pwrCycleRetryList, retry, testNum)

      #major hack...
      if ec in [11044,11049,11087] and testNum == 178 and testSwitch.WA_0112479_231166_POWERCYCLE_AND_CONTINUE_ON_11049_ERR_FOR_BANSHEE_1_0:
         #power cycle and move on
         objPwrCtrl.powerCycle(useESlip=1)
         return -1

      ec = self.parseFOFSerialCommErrorException(ec, failureData, testNum)

      return self.genericHandleException(callerRef, Exception, failureData, ec, pwrCycleRetryList, retry, testNum, retryMode)

   #------------------------------------------------------------------------------------------------------#
   def dnldCode(self, callerRef, codeType, fileName, dnldDict, interfaceDownload = False):
      """
      Placeholder
      """
      pass

   #------------------------------------------------------------------------------------------------------#
   def checkCRCRetries(self):
      """
      Placeholder
      """
      pass

   #------------------------------------------------------------------------------------------------------#
   def basicMctRetry(self, callerRef, retryMode, testNum):
      """
      Simple retry function for MCT tests
      """
      if retryMode == HARD_RESET_RETRY:
         pass
      elif retryMode == POWER_CYCLE_RETRY:
         callerRef.lowLevelFIFODump()
         objPwrCtrl.powerCycle(useESlip=1)
         callerRef.mdwDeferredSpin(testNum)    # Re-spin the drive to re-try

   #------------------------------------------------------------------------------------------------------#
   def dumpLastIOCmd(self, callerRef):
      """
      Save call to execute test 504 for debug data
      """
      callerRef.safeTestWrapper(504,1,{},"Last IO Cmd_504")

   #------------------------------------------------------------------------------------------------------#
   def basicIoRetry(self, callerRef, retryMode, testNum):
      """
      Simple retry function for IO tests- NOT IMPLEMENTED
      """
      if retryMode == HARD_RESET_RETRY:
         pass
      elif retryMode == POWER_CYCLE_RETRY:
         pass

   #------------------------------------------------------------------------------------------------------#
   def retryFunctionHandler(self, callerRef, retryMode, testNum):
      """
      Delegates the retry function to MCT or IO debending on sptActive.getMode
      """
      if self.dut.sptActive.getMode() == self.dut.sptActive.availModes.mctBase:
         self.basicMctRetry(callerRef, retryMode, testNum)
      elif self.dut.sptActive.getMode() in [self.dut.sptActive.availModes.intBase, self.dut.sptActive.availModes.sptDiag]:
         self.basicIoRetry(callerRef, retryMode, testNum)

class SerialCell_st_Handler(st_HandlerBase):
   """
   Child class of st_HandlerBase that implements serial cell versions and ovlerloading of st handler
   """
   def __init__(self):
      st_HandlerBase.__init__(self)

   def dnldCode(self, callerRef, codeType, fileName, dnldDict, interfaceDownload = False):
      """
      Implements downloading of code in a serial cell- including retries
      """
      controlWord = 0x0000

      objMsg.printMsg('Download %s %s' %(codeType,fileName), objMsg.CMessLvl.IMPORTANT)
      try:
         if testSwitch.WA_0262223_480505_FIX_QNR_CODE_DOWNLOAD_ISSUE_FOR_PSTR and codeType in ['ALL3', 'OVL2'] and objRimType.IsLowCostSerialRiser():
            import os, cStringIO, FileXferFactory
            objMsg.printMsg('Using Callback Fn~!')
            filepath=os.path.join(ScrCmds.getSystemDnldPath(), fileName)
            sourcefile = open(filepath, 'rb').read()
            memFile = cStringIO.StringIO(sourcefile)
            ff = FileXferFactory.FileXferFactory(memFile,6,0)
            callerRef.St(dnldDict,0,0,controlWord)
            ff.close()
         else:
            callerRef.St(dnldDict,0,0,controlWord)
      except:
         objMsg.printMsg('Exception Occured with Test 8: %s' % traceback.format_exc())
         #if not codeType == 'TGT': #Need to create single pwrCtrl call
         objPwrCtrl.powerCycle(useESlip=1)
         try:
            callerRef.St(dnldDict,0,0,controlWord)
         except:
            objPwrCtrl.powerCycle(useESlip=1)
            try:
               callerRef.St(dnldDict,0,0,controlWord)
            except:
               objMsg.printMsg("All download attempts failed... Exiting...")
               raise
      callerRef.upLoadAttribute(codeType, fileName) # upload attribute
      objMsg.printMsg(20*'*' + "Download Complete", objMsg.CMessLvl.IMPORTANT)
      return fileName


class CPCCell_st_Handler(st_HandlerBase):
   """
   Child class of st_HandlerBase that implements cpc cell versions and ovlerloading of st handler
   """
   def __init__(self):
      st_HandlerBase.__init__(self)



   #------------------------------------------------------------------------------------------------------#
   def handleGenericFailure(self, callerRef, failureData, pwrCycleRetryList, retry, testNum, retryMode):
      """
      Implements the generic failure handler for CPC. Adds capability to toggle ESIP ACK retries
      """
      ec = self.parseTestTimeException(failureData,pwrCycleRetryList,retry,testNum)
      ec = self.parseFOFSerialCommErrorException(ec, failureData, testNum)

      forceESLIP_Retry = 0
      # handle ESend() or EReceive() failures here
      if ( str(failureData).find('ESend') >= 0 or str(failureData).find('EReceive') >= 0 or str(failureData).find('esgcommand') >= 0 ):
         forceESLIP_Retry = 1
         # get and print objMsg.printMsg retry counts
         ESLSIPRetries = ICmd.EslipRetry()
         objMsg.printMsg("ESend / Receive Failure: Retry Data: %s" % ESLSIPRetries)

         if self.dut.sptActive.getMode() in [self.dut.sptActive.availModes.sptDiag, self.dut.sptActive.availModes.intBase]:
            objPwrCtrl.eslipToggleRetry(setACKOff = True)
         else:
            objPwrCtrl.eslipToggleRetry()

         ESLSIPRetries = ICmd.EslipRetry()
         objMsg.printMsg("Toggled ESlip Retry: Retry Data: %s" % ESLSIPRetries)

         objMsg.printMsg("ESend / Receive Failure: Issuing Resync(synCount=512,clrBuffer=true)")
         try:
            ESLIPSync = ICmd.ESync(512,1)
         except:
            objMsg.printMsg("ESend / Receive Failure: Re-sync Failed")


      #force a retry if we aren't already going to do one
      if forceESLIP_Retry and not ec in pwrCycleRetryList:
         #make a copy so we don't modify the callers list
         pwrCycleRetryList = list(pwrCycleRetryList)
         #force the retry
         pwrCycleRetryList.append(11044)
         ec = 11044

      return self.genericHandleException(callerRef,Exception,failureData,ec,pwrCycleRetryList,retry,testNum,retryMode)


   def __del__(self):
      """
      Standard __del__ implementation but also uploads the ESLIP_RTY_COUNT for tracking
      """
      ESLIPRTYCNT = 2
      self.dut.driveattr['ESLIP_RTY_COUNT']   = ICmd.EslipRetry(ESLIPRTYCNT)['ERTRYCNT']
      ScrCmds.statMsg('ESLIP retry count cleared: %s' % self.dut.driveattr['ESLIP_RTY_COUNT'])

   def dnldCode(self, callerRef, codeType, fileName, dnldDict, interfaceDownload = False):
      """
      Implements downloading of code in a cpc cell- including retries and interface download handling
      """
      objMsg.printMsg('Download %s %s' %(codeType,fileName), objMsg.CMessLvl.IMPORTANT)
      controlWord = 0

      useESlip = int(not interfaceDownload) #interface download must have eslip off

      dnldParms = (dnldDict,0,0,controlWord)

      if not testSwitch.WA_0110375_231166_DISABLE_POWERCYCLE_PRIOR_TO_OVL_DOWNLOAD:
         if codeType == 'OVL' and not interfaceDownload:
            #OVL downloads could be after TGT which needs a power cycle for MCT download
            objPwrCtrl.powerCycle(useESlip = useESlip)

      if testSwitch.FE_0142350_357260_P_ADD_POWERCYCLE_PRIOR_TO_TGT_DOWNLOAD:
         if codeType == 'TGT' and not interfaceDownload:
            objPwrCtrl.powerCycle(useESlip = useESlip)

      retry = 4
      while 1:
         try:
            if interfaceDownload:
               theCell.disableESlip()
            else:
               theCell.enableESlip(sendESLIPCmd = False)
               sptCmds.disableAPM()
            if testSwitch.FE_0141097_357260_P_ADD_DNLD_SLEEP:
               
               objMsg.printMsg('Sleep 30s')
               time.sleep(30)

            callerRef.St(*dnldParms)
            break
         except:
            objMsg.printMsg('Exception Occured with Test 8: %s' % traceback.format_exc())

            retry -= 1
            if retry <= 0:
               objMsg.printMsg("All download attempts failed... Exiting...")
               raise

            if self.dut.sptActive.getMode() in [self.dut.sptActive.availModes.sptDiag, self.dut.sptActive.availModes.intBase] and retry < 2:
               objMsg.printMsg("Attempting to use interface download.")
               interfaceDownload = True
               useESlip = False

            if (codeType == 'TGT' and not interfaceDownload) and testSwitch.FE_0148182_407749_P_RETRIES_CHANGE_LOW_BAUDRATE_IN_CPC_DNLDCODE:
               objPwrCtrl.powerCycle(baudRate=Baud38400, useESlip = useESlip)
            else:
               objPwrCtrl.powerCycle(useESlip = useESlip)

      if codeType.find('TGT') > -1:
         self.dut.sptActive.setMode(self.dut.sptActive.availModes.intBase)

      callerRef.upLoadAttribute(codeType, fileName) # upload attribute
      objMsg.printMsg(20*'*' + "Download Complete", objMsg.CMessLvl.IMPORTANT)
      return fileName

   def checkCRCRetries(self):
      """
      Checks to see if the CRC Error retry counter has surpassed the limit in CPC
      """
      retryData = ICmd.CRCErrorRetry()
      crcRetryCnt = int(retryData['CRCCNT'])
      if crcRetryCnt > 0:
         crcLimit = getattr(TP,'CRC_RETRY_LIMIT',3)
         objMsg.printMsg('ICmd.CRCErrorRetry data=%s CRCCnt=%d CRCLimit=%d' %(retryData,crcRetryCnt,crcLimit))
         self.dut.driveattr['PROC_CTRL5'] = crcRetryCnt
         if crcRetryCnt >= crcLimit:
            ScrCmds.raiseException(14026,"CRC Retry limit exceeded; %d greater than %d" % (crcRetryCnt, crcLimit))

   def basicIoRetry(self, callerRef, retryMode, testNum):
      """
      Basic IO retry mechanism to dump last io commands and perform hard resets and power cycles as requested
      """
      if not testNum == 8:
         self.dumpLastIOCmd(callerRef)
      if retryMode == HARD_RESET_RETRY:
         ICmd.HardReset()
      elif retryMode == POWER_CYCLE_RETRY:
         objPwrCtrl.powerCycle(useESlip = theCell.eslipMode, ataReadyCheck = False)


class InitiatorCell_st_Handler(st_HandlerBase):
   """
   Child class of st_HandlerBase that implements initiator cell versions and ovlerloading of st handler
   """
   def __init__(self):
      st_HandlerBase.__init__(self)

   #------------------------------------------------------------------------------------------------------#
   def dumpLastIOCmd(self, callerRef):
      """
      Dumps the last IO command with test 504
      """
      callerRef.safeTestWrapper(504,1,{'TEST_FUNCTION': 0},"Last IO Cmd_504")

   if testSwitch.BF_0163846_231166_P_SATA_DNLD_ROBUSTNESS:
      #------------------------------------------------------------------------------------------------------#
      def handleGenericFailure(self, callerRef, failureData, pwrCycleRetryList, retry, testNum, retryMode):
         """
         Handles the generic failure case in an initiator cell- more like the MCT version than CPC
         """
         try:
            ec = self.parseTestTimeException(failureData, pwrCycleRetryList, retry, testNum)
         except ScriptTestFailure:
            # We hit a timeout- so the Initiator is hung- need to power cycle it
            theRim.powerCycleRim()
            if testSwitch.BF_0165552_231166_P_RESET_COM_PWRCYCLE_INITIATOR:
               objComMode.setMode(objComMode.availModes.intBase)
            theRim.EnableInitiatorCommunication(objComMode)
            raise

         ec = self.parseFOFSerialCommErrorException(ec, failureData, testNum)

         return self.genericHandleException(callerRef, Exception, failureData, ec, pwrCycleRetryList, retry, testNum, retryMode)

   #------------------------------------------------------------------------------------------------------#
   def basicIoRetry(self, callerRef, retryMode, testNum):
      """
      Handles the basic IO retry but has te added complication of different commands per cell type- sas/sata..etc
      """
      if not testNum == 8:
         self.dumpLastIOCmd(callerRef)
      if retryMode == HARD_RESET_RETRY:
         if objRimType.baseType in SATA_RiserBase:
            from base_SATA_ICmd_Params import HardReset
         elif objRimType.baseType in SAS_RiserBase:
            from base_SAS_ICmd_Params import HardReset
         callerRef.St(HardReset)
      elif retryMode == POWER_CYCLE_RETRY:
         objPwrCtrl.powerCycle(ataReadyCheck = True)

   def dnldCode(self, callerRef, codeType, fileName, dnldDict, interfaceDownload = False):
      """
      Implements download code for an initiator cell. Handles downloading via initiator or to initiator
         depending on objComMode.availModes.intBase
      """
      objMsg.printMsg('Download %s %s' %(codeType,fileName), objMsg.CMessLvl.IMPORTANT)

      UseHardSRQ(0)

      if objComMode.getMode() == objComMode.availModes.intBase or not testSwitch.BF_0126057_231166_FAIL_INVALID_TST_RETURN:
         featureReg = 7
         targetBits = 3
      else:
         featureReg = 0
         targetBits = 0
      try:

         callerRef.St(dnldDict,0,0,targetBits, 0, 0, featureReg)

      except:
         objMsg.printMsg('Exception Occured with Test 8: %s' % traceback.format_exc())
         #if not codeType == 'TGT': #Need to create single pwrCtrl call
         objPwrCtrl.powerCycle(5000,12000,20,20)
         try:

            callerRef.St(dnldDict,0,0,targetBits, 0, 0, featureReg)

         except:
            try:
               callerRef.St(dnldDict,0,0,targetBits, 0, 0, featureReg)
            except:
               objMsg.printMsg("All download attempts failed... Exiting...")
               raise
      callerRef.upLoadAttribute(codeType, fileName) # upload attribute
      objMsg.printMsg(20*'*' + "Download Complete", objMsg.CMessLvl.IMPORTANT)
      return fileName

   #----------------------------------------------------------------------------

#**********************************************************************************************************
#**********************************************************************************************************

##### Singleton creation  ########
## Only create the object we need
if objRimType.CPCRiser():
   st_Handler = CPCCell_st_Handler()
elif objRimType.SerialOnlyRiser() or testSwitch.SI_SERIAL_ONLY:
   st_Handler = SerialCell_st_Handler()
elif objRimType.IOInitRiser():
   st_Handler = InitiatorCell_st_Handler()
else:
   st_Handler = st_HandlerBase()
