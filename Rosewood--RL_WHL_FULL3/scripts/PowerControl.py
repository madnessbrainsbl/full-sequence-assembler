#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Implements generic drive power control classes for serial and I/O testing
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/06 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/PowerControl.py $
# $Revision: #2 $
# $DateTime: 2016/05/06 00:36:23 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/PowerControl.py#2 $
# Level:3
#---------------------------------------------------------------------------------------------------------#

from Constants import *
from TestParamExtractor import TP
import time, traceback, re
from Rim import theRim, objRimType, SAS_RiserBase
from Carrier import theCarrier
from Cell import theCell
import ScrCmds
import MessageHandler as objMsg
from Drive import objDut
from SerialCls import baseComm
from PIFHandler import CPIFHandler
from TestParameters import prm_PowerControl
try:
   #Not all CM's support the following functions
   SPortToInitiator
except NameError:
   def SPortToInitiator( flag):
      pass
   def DisableStaggeredStart( flag):
      pass
import base_BaudFunctions, sptCmds
from Exceptions import SeaSerialRequired, CRaiseException

DEBUG = 0

###########################################################################################################
###########################################################################################################
class CBasePowerControl:

   def __init__(self, readyTimeLimit=15000):
      self.dut = objDut

      if testSwitch.BF_0169635_231166_P_USE_CERT_OPER_DUT:
         self.certOper = self.dut.certOper
      else:
         self.certOper = self.dut.nextOper in getattr(TP,'CertOperList', ['PRE2', 'CAL2', 'FNC2', 'SDAT2', 'CRT2','SPSC2'])
      self.readyTimeLimit = readyTimeLimit
      self.onTime = 10
      self.offTime = 10
      self.downloadActive = False
      self.ICmd = None
      self.drvATASpeed = 0

   #------------------------------------------------------------------------------------------------------#
   def DisablePowerCycle(self, *args, **kwargs):
      """
         Disable drive power cycle (eg after SDOD test)
      """
      if self.powerCycle == self.DisablePowerCycle:
         objMsg.printMsg("Drive power cycle/on has been disabled")
      else:
         objMsg.printMsg("Disabling drive power cycle/on from now on...")
         self.powerCycle = self.DisablePowerCycle
         self.powerOn = self.DisablePowerCycle

   def EnablePowerCycle(self, *args, **kwargs):
      """
      Enable power cycle prior to GIO/MQM
      """
      self.powerCycle = CPowerCtrl().powerCycle
      self.powerOn = CPowerCtrl().powerOn

   #------------------------------------------------------------------------------------------------------#
   def powerCycle(self, set5V=5000, set12V=12000, offTime=10, onTime=10, baudRate=PROCESS_HDA_BAUD, useESlip=0, driveOnly=0, ataReadyCheck = False):
      """

      """
      self.powerOff(offTime, driveOnly)
      self.powerOn(set5V, set12V, onTime, baudRate, useESlip, driveOnly)

   #-------------------------------------------------------------------------------------------------------
   def powerOff(self, offTime=10, driveOnly=0):
      """
         Powers off the drive/port
      """
      # Override the default power off time with a test parm-specifiec time, if available
      #offTime = getattr(TP, 'prm_PowerControl',{}).get('powerOffTime_sec', offTime)
      offTime = getattr(TP, 'prm_PowerOffTime',{}).get('seconds', offTime)

      theCarrier.powerOffPort(offTime, driveOnly)
      theCell.setBaud()
      self.dut.baudRate = DEF_BAUD
      objDut.eslipMode = 0    # reset eslip mode flag

   def powerOn(self, set5V=5000, set12V=12000, onTime=10, baudRate=PROCESS_HDA_BAUD, useESlip=0, driveOnly=0, spinUpFlag = 0):
      """
         Powers on drive
      """
      onTime = max(getattr(TP, 'prm_PowerOnTime',  {}).get('seconds', 0),  onTime)

      if testSwitch.FE_0110517_347506_ADD_POWER_MODE_TO_DCM_CONFIG_ATTRS and spinUpFlag:
         timeout = 30000
         data = ICmd.PowerOnTiming(timeout+(onTime*1000), spinUpFlag) # These 3 Commands must be together, Nothing in between
         theCarrier.powerOnPort(set5V, set12V, onTime = onTime)

         data = ICmd.StatusCheck()                             # This gets Ready check time from the NIOS.
         if data['LLRET'] != OK:
            msg = 'ATA Ready Failed GetPowerOnTime Data = %s' % data
            objMsg.printMsg(msg)
            ScrCmds.raiseException(13424, msg)
      else:
         theCarrier.powerOnPort(set5V, set12V, onTime, driveOnly)

   def TCGCheckUnlock(self):
      """
         Checking and unlocking serial and interface port for TCG drive in ATA mode
      """
      if self.dut.driveattr['FDE_DRIVE'] == 'FDE':
         from TCG import CTCGPrepTest
         oTCG = CTCGPrepTest(self.dut)

         try:
            oTCG.CheckFDEState()
   
            if self.dut.LifeState == "80" and not self.dut.TCGComplete:
               objMsg.printMsg("Drive is in USE state, will unlock ports.")
               objMsg.printMsg("TCGComplete = %s" % (self.dut.TCGComplete,))
               oTCG.UnlockDiagUDE()
            else:
               objMsg.printMsg("Drive is NOT in USE state, unlock is not required")
         finally:
            if testSwitch.BF_0180787_231166_P_REMOVE_FDE_CALLBACKS_FOR_CHECKFDE:
               oTCG.RemoveCallback()

   def changeBaud(self, baudRate, powerOnTuple = (5000, 12000, 10, 1), pwrRetries = 5):
      """
      Changes the drives baud rate using SDBP. Invokes power cycle retries and increments the onTime in each loop to
         give the drive additional time to be *ready*
      """
      powerOnTuple = list(powerOnTuple)

      for powerInc in xrange(pwrRetries):

         try:
            base_BaudFunctions.changeBaud(baudRate)
            break
         except SeaSerialRequired:
            raise
         except:
            objMsg.printMsg("Error In changeBaud: %s" % (traceback.format_exc(),))
            powerOnTuple[2] += 10

            theCarrier.powerOffPort(self.offTime, powerOnTuple[3])
            # since driveonly is 0 both cell and drive baudRates need to be reset
            if powerOnTuple[3] == 0:
               theCell.setBaud()
            self.dut.baudRate = DEF_BAUD
            theCarrier.powerOnPort(*powerOnTuple)
            sptCmds.disableAPM()
      else:
         ScrCmds.raiseException(10340, "All changeBaud retries exhausted")

      self.dut.baudRate = baudRate

   #------------------------------------------------------------------------------------------------------#
   def eslipToggleRetry(self):
      pass

   def incrementLifetimePowerCycleCounter(self):
      self.dut.driveattr['PWR_CYC_COUNT'] = str(int(self.dut.driveattr['PWR_CYC_COUNT']) + 1)
      objMsg.printMsg("Drive lifetime power cycle count: %s" % self.dut.driveattr['PWR_CYC_COUNT'],objMsg.CMessLvl.VERBOSEDEBUG)

   #------------------------------------------------------------------------------------------------------#
   def powerCycleTiming_SPT(self, set5V=5000, set12V=12000, offTime=10, onTime=0, ataReadyCheck = False):

      interruptReady = "Rst"
      readySignOn = 'ATA St 80'
      readySignOn2 = 'SATA Reset'
      genericReady = 'Ready'
      asciiOnlineString = 'ASCII Online mode'

      interruptTimeout = 5 + onTime
      oSerial = baseComm()
      self.onTime = onTime
      timeout = 30 + onTime
      failedReady = False
      set3V = 0
      self.setVoltages = (set3V,set5V,set12V)

      SPTreadyTimeMeanAdjustment = 0.3

      for retry in range(0,3):
         self.powerOff(offTime)

         theCell.disableESlip()

         masterRes = ''
         theCell.setBaud(DEF_BAUD)
         accum = oSerial.PChar('')
         endTime = None

         #Increase start time to accomodate mean shift for using SPT ready times
         startTime = time.time() + SPTreadyTimeMeanAdjustment + onTime

         theCarrier.powerOnPort(set5V, set12V, onTime, 0)

         for res in accum:
            if testSwitch.virtualRun:
               res = interruptReady
            if res.find(interruptReady) > -1:
               break

            if time.time() - startTime > interruptTimeout:
               break

         #Disable APM... safe to send regardless
         oSerial.PChar(ESC)

         masterRes += res
         if DEBUG > 0:
            objMsg.printMsg("Interrupt Ready Status: %s" % masterRes)

         for retry in xrange(3):
            time.sleep(0.5)
            accum = oSerial.PChar(CTRL_R)
            for res in accum:
               if testSwitch.virtualRun:
                  res = asciiOnlineString
               if res.find(asciiOnlineString) > -1 or\
                  masterRes.find(asciiOnlineString) > -1:
                  break

               if time.time() - startTime > (2*interruptTimeout):
                  break
            else:
               continue
            break

         masterRes += res
         if DEBUG > 0:
            objMsg.printMsg("Passed Online Parse: %s" % masterRes)

         time.sleep(0.5)

         accum = oSerial.PChar('~')
         acc = iter(accum)

         while time.time() - startTime < timeout:
            time.sleep(0.5)
            res = acc.next()
            if testSwitch.virtualRun:
               res = readySignOn

            if res.find(readySignOn) > -1 or res.find(readySignOn2) > -1 or res.find(genericReady) > -1 or\
               masterRes.find(readySignOn) > -1 or masterRes.find(readySignOn2) > -1 or masterRes.find(genericReady) > -1:
               endTime = time.time()
               break

            if DEBUG > 0:
               objMsg.printMsg("Incremental Buffer: %s" % res)

            accum = oSerial.PBlock('~.', noTerminator = 1)
            acc = iter(accum)


         else:
            masterRes += res
            if DEBUG > 0:
               objMsg.printMsg("Failed Parse: %s" % masterRes)



         if endTime:
            #drive is ready
            break
      else:
         failedReady = True
         endTime = startTime



      readyTime = endTime - startTime - onTime

      if DEBUG > 0 or failedReady:
         objMsg.printMsg("Drive ATA ready from SPT Result in %f seconds. SPT Buffer dump:\n%s" % (readyTime,masterRes))
      readyTime = readyTime * 1000 #Convert to Msec

      if (ataReadyCheck and not self.downloadActive) or not testSwitch.BF_0160098_231166_P_DISABLE_READY_VAR_CHECK_DISABLED:
         self.logPowerOn_Information(readyTime, 0, {'ERR':0,'STS':80})
      self.incrementLifetimePowerCycleCounter()

      if failedReady or readyTime > self.readyTimeLimit:
         ScrCmds.raiseException(13424, "Drive failed to power on and come ready in interface mode within spec time. %f/%f" % (readyTime,self.readyTimeLimit))
      else:
         objMsg.printMsg('ATA Ready Passed in %d Msec. Limit = %d ' % (readyTime, self.readyTimeLimit))

   def logPowerOn_Information(self, readyTime, spinUpFlag, intfReadyData):
      """
      Log the maximum ready time to the drive attribute TIME_TO_READY for this interface testing sequence
      Log the current time to ready in P_TIME_TO_READY
      """
      if not testSwitch.FE_0007406_402984_USE_INTFTTR_MAX_VALUE:      
         self.dut.driveattr['TIME_TO_READY'] = max(self.dut.driveattr.get('TIME_TO_READY',0),readyTime)
      if DEBUG > 0:
         objMsg.printMsg("TIME_TO_READY Attr set to %s" % self.dut.driveattr['TIME_TO_READY'])

      curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
      self.dut.objSeq.curRegSPCID = 1

      (mV3,mA3),(mV5,mA5),(mV12,mA12)  = GetDriveVoltsAndAmps()
      if testSwitch.virtualRun: self.setVoltages = (3000,5000,12000)
      #self.setVoltages is a tuple of (3v, 5v, 12v)
      self.dut.dblData.Tables('P_TIME_TO_READY').addRecord(
         {
         'SPC_ID': 1,
         'OCCURRENCE':occurrence,
         'SEQ':curSeq,
         'TEST_SEQ_EVENT': testSeqEvent,
         'SET_3V': int(self.setVoltages[0]),
         'SET_5V': int(self.setVoltages[1]),
         'SET_12V': int(self.setVoltages[2]),
         'SENSE_VOLTAGE_3V': int(mV3),
         'SENSE_VOLTAGE_5V': int(mV5),
         'SENSE_VOLTAGE_12V': int(mV12),
         'SENSE_CURRENT_3V': int(mA3),
         'SENSE_CURRENT_5V': int(mA5),
         'SENSE_CURRENT_12V': int(mA12),
         'POWER_OPTIONS': spinUpFlag,
         'DEVICE_ERROR_RGSTR': int(intfReadyData.get('ERR','0')),
         'DEVICE_STATUS_RGSTR': int(intfReadyData.get('STS','0')),
         'SPIN_UP_TIME_TO_READY': int(readyTime),
         })

      if DEBUG > 0:
         objMsg.printDblogBin(self.dut.dblData.Tables('P_TIME_TO_READY'), spcId32 = 1)

   def CheckInitiator(self):pass

   def getSpinUpFlag(self):
      if objRimType.IOInitRiser() and testSwitch.FE_0133860_372897_ADD_PARA_TEST_FUNCTION_FOR_T528 :
         if (ConfigVars[CN].has_key('Power On Hard Reset') and ConfigVars[CN]['Power On Hard Reset'] == 'ON') and \
             (ConfigVars[CN].has_key('Power On Set Feature') and ConfigVars[CN]['Power On Set Feature'] == 'ON'):
            objMsg.printMsg('This Config is set for Power On Hard Reset and Power On Set Features')
            spinUpFlag = 0x03
         elif ConfigVars[CN].has_key('Power On Hard Reset') and ConfigVars[CN]['Power On Hard Reset'] == 'ON':
            objMsg.printMsg('This Config is set for Power On Hard Reset to come ready')
            spinUpFlag = 0x01
         else:
            objMsg.printMsg('This Config is Not set for Power On Hard Reset or Power On Set Features')
            spinUpFlag = 0x00
      else:
         if ConfigVars[CN].has_key('Power On FlushCache') and ConfigVars[CN]['Power On FlushCache'] == 'ON':
            objMsg.printMsg('This Config is set for Power On Set Features with FlushCache to come ready')
            spinUpFlag = 0x0A
         elif ConfigVars[CN].has_key('Power On HRst FCache') and ConfigVars[CN]['Power On HRst FCache'] == 'ON':
            objMsg.printMsg('This Config is set for Power On Hard Reset with FlushCache to come ready')
            spinUpFlag = 0x09
         elif (ConfigVars[CN].has_key('Power On Hard Reset') and ConfigVars[CN]['Power On Hard Reset'] == 'ON') and \
             (ConfigVars[CN].has_key('Power On Set Feature') and ConfigVars[CN]['Power On Set Feature'] == 'ON'):
            objMsg.printMsg('This Config is set for Power On Hard Reset and Power On Set Features')
            spinUpFlag = 0x03
         elif ConfigVars[CN].has_key('Power On Set Feature') and ConfigVars[CN]['Power On Set Feature'] == 'ON':
            objMsg.printMsg('This Config is set for Power On Set Features to come ready')
            spinUpFlag = 0x02
         elif ConfigVars[CN].has_key('Power On Hard Reset') and ConfigVars[CN]['Power On Hard Reset'] == 'ON':
            objMsg.printMsg('This Config is set for Power On Hard Reset to come ready')
            spinUpFlag = 0x01
         else:
            objMsg.printMsg('This Config is Not set for Power On Hard Reset or Power On Set Features')
            spinUpFlag = 0x00
      return spinUpFlag

###########################################################################################################
###########################################################################################################
class CPowerControlSerial(CBasePowerControl):
   """
      Power Control class for serial mode testing
      This class overrides the base CPowerControl class to implement serial-only specific commands
   """
   def __init__(self, readyTimeLimit=15000 ):
      CBasePowerControl.__init__(self,readyTimeLimit)

   #------------------------------------------------------------------------------------------------------#
   def powerCycle(self, set5V=5000, set12V=12000, offTime=10, onTime=10, baudRate=PROCESS_HDA_BAUD, useESlip=1, ataReadyCheck = False):
      """
`
      """
      if objRimType.IOInitRiser():
         DisableStaggeredStart(True)
         
      # In SPFIN2 and CCV2, use lower 38K baud rate
      if testSwitch.FE_0320895_502689_P_RUN_SPIO_LOW_BAUD and testSwitch.NoIO and self.dut.nextOper in ['FIN2', 'CUT2', 'CCV2']:
         baudRate = Baud38400
      self.powerOff(offTime)
      self.powerOn(set5V, set12V, onTime, baudRate, useESlip)

   #------------------------------------------------------------------------------------------------------#
   def powerOn(self, set5V=5000, set12V=12000, onTime=5, baudRate=PROCESS_HDA_BAUD, useESlip=1, spinUpFlag = 0):
      """
         Powers on drive
      """

      self.onTime = max(onTime, getattr(TP,'APMTime', 0))
      if testSwitch.virtualRun:
         CBasePowerControl().powerOn(set5V, set12V, self.onTime, baudRate, useESlip, spinUpFlag = spinUpFlag)
      else:
         CBasePowerControl.powerOn(self,set5V, set12V, self.onTime, baudRate, useESlip, spinUpFlag = spinUpFlag) #should be this way but causes import/disassociation

      if useESlip:
         theCell.enableESlip()

      self.TCGCheckUnlock()
      if sptCmds.objComMode.getMode() != sptCmds.objComMode.availModes.mctBase or \
         self.dut.f3Active or \
         int(self.dut.driveattr['PWR_CYC_COUNT']) == int(DriveAttributes.get('PWR_CYC_COUNT', 0)):

         sptCmds.disableAPM()
      if not testSwitch.FE_0249024_356922_CTRLZ_Y2_RETRY and self.dut.IsSDI == False and self.dut.SkipY2 == False and testSwitch.NoIO and self.dut.nextOper in ['FIN2', 'CUT2', 'FNG2'] and not self.dut.nextState in ['INIT', 'CLEAR_EWLM']:
         self.changeBaud(baudRate, (set5V, set12V, onTime, 0), pwrRetries = 2)
         self.Chg_SP_Retry()
      else:
         self.changeBaud(baudRate, (set5V, set12V, onTime, 0), pwrRetries = 1)
      self.incrementLifetimePowerCycleCounter()

   #------------------------------------------------------------------------------------------------------#
   def Chg_SP_Retry(self):
      """
         Change serial port retry level to match IO retry
      """

      import sdbpComm
      sdbpComm.NEW_ESLIP_DIAG = False

      for i in xrange(3):
         try:
            objMsg.printMsg("Chg_SP_Retry /FY2 start /FY2Loop=%s" % i)
            sptCmds.enableDiags(retries = 3)
            sptCmds.sendDiagCmd("/F", printResult = True)
            sptCmds.sendDiagCmd("/FY2,,,,10000000018", printResult = True)

            try:
               sptCmds.sendDiagCmd("/T", printResult = True)
            except:
               sptCmds.sendDiagCmd(CTRL_Z, printResult = True, raiseException = 0, DiagErrorsToIgnore=['Invalid Diag Cmd'], Ptype='PChar')

            objMsg.printMsg("Chg_SP_Retry /FY2 end")
            break
         except:
            objMsg.printMsg("Error In Chg_SP_Retry: %s" % (traceback.format_exc(),))

################################################################################
################################################################################
class CPowerControlInterface(CBasePowerControl):
   """
      Power control class for ATA drive testing in initiator interface mode
      This class overrides the base CPowerControl class to implement serial-only specific commands
   """
   def __init__(self, readyTimeLimit=15000):
      CBasePowerControl.__init__(self)
      self.readyTimeLimit = readyTimeLimit

      self.firstPowerCycleFailed = False
      if self.certOper:
         self.saveMode = sptCmds.objComMode.availModes.mctBase


   #----------------------------------------------------------------------------
   def callBack(self,data,currentTemp,drive5,drive12,collectParametric):
      pass


   def CheckInitiator(self):
      objMsg.printMsg('Checking Initiator type...')
      SPortToInitiator(True)
      errInitiator = False

      for x in xrange(3):
         try:
            theCell.enableESlip(False)
            if testSwitch.BF_0156515_231166_P_EXT_ON_TIME_INIT_PWR_ON:
               theRim.powerCycleRim(onTime = 10)
            else:
               theRim.powerCycleRim()
            base_BaudFunctions.sendBaudCmd(DEF_BAUD, PROCESS_HDA_BAUD)

            prm_535_InitiatorRev = {
                 "TEST_OPERATING_MODE" : (0x0002,),
                 "TEST_FUNCTION" :       (0x8800,),
              }

            st(535,prm_535_InitiatorRev,  timeout=30)

            sptCmds.objComMode.setMode(sptCmds.objComMode.availModes.intBase)

            break

         except:
            errInitiator = True
            objMsg.printMsg("Exception occurred in CheckInitiator but it is ignored...\n%s" % (traceback.format_exc(),))

            try:
               objMsg.printMsg("Using RawBootLoader to flash initiator cell.")
               from RawBootLoader import CFlashLoad
               ofls = CFlashLoad(tpmTXTFileKey = 'INC_TPM', binFileKey = 'INC_BIN', initiator = True)
               ofls.flashBoard()

               theCell.enableESlip(False)
               theRim.powerCycleRim()
               base_BaudFunctions.sendBaudCmd(DEF_BAUD, PROCESS_HDA_BAUD)
               break
            except:
               objMsg.printMsg("Using INC file to flash initiator cell.")
               if testSwitch.USE_ICMD_DOWNLOAD_RIM_CODE:
                  from ICmdFactory import ICmd
                  ICmd.downloadIORimCode()
               else:
                  try:
                     from PackageResolution import PackageDispatcher
                     op = PackageDispatcher(self.dut, 'INC')
                     incCode = op.getFileName()

                     for baud in [Baud1228000, Baud390000, DEF_BAUD]:
                        theRim.powerCycleRim()

                        try:
                           base_BaudFunctions.sendBaudCmd(DEF_BAUD, baud)
                           st(8, 0, 0, 0, 0, dlfile = (CN, incCode), timeout = 600) # download initiator code, some initiator cells need longer download time
                           break
                        except:
                           pass
                     else:
                        raise
                  except:
                     theRim.powerCycleRim()
                     base_BaudFunctions.sendBaudCmd(DEF_BAUD, PROCESS_HDA_BAUD)

               sptCmds.objComMode.setMode(sptCmds.objComMode.availModes.intBase)
               break
      else:
         raise

      if errInitiator:
         objMsg.printMsg("Verifying initiator cell after flash.")  
         try:  # Verify initiator after flashing  
            st(535,prm_535_InitiatorRev,  timeout=30)
            sptCmds.objComMode.setMode(sptCmds.objComMode.availModes.intBase)
         except:
            if testSwitch.FAIL_ON_INITIATOR_REVISION_CHECK_FAILURE:
               # WARNING: receiveBuffer failed for timeout - NO_SRQ. readFrame without SRQ!  
               ScrCmds.raiseException(10108, "Bad response from initiator.")

   #-------------------------------------------------------------------------------------------------------
   def powerOff(self, offTime=10, driveOnly=0):
      """
         Powers off the drive/port
      """
      self.offTime = offTime

      if self.certOper:
         self.saveMode = sptCmds.objComMode.getMode()

         theCarrier.powerOffPort(offTime, driveOnly=0)
         sptCmds.objComMode.setMode(sptCmds.objComMode.availModes.intBase)
         theCell.setBaud()


      else:
         theCarrier.powerOffPort(offTime, driveOnly=driveOnly)
         if driveOnly == 0:
            #If we power cycled the rim and drive then reset the RIM baud
            theCell.setBaud()
            #We power cycled the RIM as well so we are now talking to initiator again
            sptCmds.objComMode.setMode(sptCmds.objComMode.availModes.intBase)


      #If we just power cycled the drive then reset the drive baud only
      # Don't modify whom we are talking to as that hasn't changed
      self.dut.baudRate = DEF_BAUD

      objDut.eslipMode = 0    # reset eslip mode flag

   #----------------------------------------------------------------------------
   def powerOn(self, set5V=5000, set12V=12000, onTime=10, baudRate=PROCESS_HDA_BAUD, useESlip=0, driveOnly=0, readyTimeLimit=15000, ataReadyCheck = False):
      """
         Powers on drive
      """
      self.onTime = max(onTime, getattr(TP,'APMTime', 0))
      if useESlip:
         theCell.enableESlip(False)

      if self.certOper:

         for x in xrange(5):
            try:

               theCarrier.powerOnPort(set5V, set12V, self.onTime, driveOnly = 0)
               base_BaudFunctions.sendBaudCmd(theCell.getBaud(), PROCESS_HDA_BAUD)

               objMsg.printMsg("disabling initcomm")
               sptCmds.DisableInitiatorCommunication()
               objMsg.printMsg("just disabled int comm")

               if self.saveMode != sptCmds.objComMode.availModes.intBase:
                  sptCmds.objComMode.setMode(self.saveMode)

               time.sleep(5)
               driveOnly = 1
                  #if we didn't except then let's abort the retry loop
               break
            except (FOFSerialCommError, CRaiseException):
               if not testSwitch.FE_0125484_231166_ADD_INIT_PWRON_COMM_RETRIES:
                  #if the feature isn't on then just raise
                  raise
               else:
                  #ok 1 retry
                  objMsg.printMsg("Error communicating to initiator:\n%s" % traceback.format_exc())
                  theCarrier.powerOffPort(self.offTime, driveOnly = 0)
                  #out of seq power off's require implementation to reset the baud rates of initiator and drive
                  self.dut.baudRate = DEF_BAUD
                  theCell.setBaud(DEF_BAUD)
                  sptCmds.objComMode.setMode(sptCmds.objComMode.availModes.intBase)

         else:
            #all retries exhausted so fail
            raise

      else:
         theCarrier.powerOnPort(set5V, set12V, self.onTime, driveOnly)

         if driveOnly == 0:
            #initiate communication to initiator
            for x in xrange(5):
               try:
                  theCell.enableESlip(False) #Force enableEslip before change baudrate
                  base_BaudFunctions.sendBaudCmd(theCell.getBaud(), PROCESS_HDA_BAUD)
                  break
               except (FOFSerialCommError, CRaiseException):
                  objMsg.printMsg("Error communicating to initiator:\n%s" % traceback.format_exc())
                  # power cycle rim
                  theRim.powerCycleRim()
                  if testSwitch.BF_0165552_231166_P_RESET_COM_PWRCYCLE_INITIATOR:
                     sptCmds.objComMode.setMode(sptCmds.objComMode.availModes.intBase)
            else:
               # we didn't break so there is still an exception
               raise


      if self.certOper or useESlip:
         #if not (testSwitch.BF_0132023_161897_SATA_INITIATOR_CRT2_11087 and self.certOper) :
         #   sptCmds.DisableInitiatorCommunication()
         sptCmds.disableAPM()
         #Set baud rate to drive
         if self.certOper:#testSwitch.BF_0166867_231166_P_FIX_CRT2_SF3_INIT_DRV_INFO_DETCT:
            sptCmds.objComMode.setMode(sptCmds.objComMode.availModes.mctBase, determineCodeType = True)
         self.changeBaud(baudRate, (set5V, set12V, onTime, driveOnly))

      self.incrementLifetimePowerCycleCounter()


   def processRequest_PowerOnCallback(self, requestData, *args, **kargs):
      """
      Script power cycle callback request handler to implement smaller power on wait times
      """
      requestKey = ord(requestData[0])
      if DEBUG:
         objMsg.printMsg("processRequest_PowerOnCallback: block_request: %s" % requestKey)

      if requestKey in [14,15]:
         #onTime is 0 here since initiator is monitoring interface line for minimum TTR
         theCarrier.powerOnPort(set5V=5000, set12V=12000, onTime=0, driveOnly=1)

      elif requestKey in [13,]:
         theCarrier.powerOffPort(offTime = getattr(self, 'offTime', 10), driveOnly = 1)
         if testSwitch.FE_0165113_231166_P_SIC_PHY_READY_TTR:
            self.dut.baudRate = DEF_BAUD

   def initiatorDriveReadyPwrCycle(self, ttrMode=False):

      RegisterResultsCallback(self.processRequest_PowerOnCallback,[13,14,15],useCMLogic=0)

      try:
         if objRimType.baseType in SAS_RiserBase:
            HardReset = {
               #'test_num'          : 599,
               #'prm_name'          : "base_prm_599_SasHardReset",
               'spc_id'            :  1,
               'timeout':600,
               'PARAMETER_10' : (0x0000,),
               'PARAMETER_9' : (0x0000,),
               'PARAMETER_8' : (0x0000,),
               'PARAMETER_3' : (0x0000,),
               'PARAMETER_2' : (0x0002,),
               'PARAMETER_1' : (0x0000,),
               'PARAMETER_7' : (0x0000,),
               'PARAMETER_6' : (0x0000,),
               'PARAMETER_5' : (0x0000,),
               'PARAMETER_4' : (0x0000,),
            }

            if sptCmds.objComMode.getMode() != sptCmds.objComMode.availModes.intBase:
               theRim.EnableInitiatorCommunication(sptCmds.objComMode)

            driveOnlyPwrCycle = True

            if testSwitch.WA_0141203_357552_FULL_POWER_CYCLE_AFTER_CODE_LOAD:
               DriveOff(self.offTime)
               self.dut.baudRate = DEF_BAUD
               RimOff()
               RimOn()
               theCell.setBaud(DEF_BAUD)
               DriveOn(5000,12000,self.onTime)
               self.dut.sptActive.setMode(self.dut.sptActive.availModes.intBase)
               base_BaudFunctions.changeBaud(PROCESS_HDA_BAUD)
               driveOnlyPwrCycle = False

            if testSwitch.FE_0137957_357552_POWER_CYCLE_FOR_CODE_LOADS and driveOnlyPwrCycle:
               DriveOff(self.offTime)
               self.dut.baudRate = DEF_BAUD
               DriveOn(5000,12000,self.onTime)

            if testSwitch.WA_0130599_357466_T528_EC10124:
               prm_517_01 = {
                   "SENSE_DATA_8" : (0x0000,0x0000,0x0000,0x0000,),
                   "MAX_REQS_CMD_CNT" : (0x000F,),
                   "SENSE_DATA_4" : (0x0000,0x0000,0x0000,0x0000,),
                   "SENSE_DATA_1" : (0x0000,0x0000,0x0000,0x0000,),
                   "TEST_FUNCTION" : (0x0000,),
                   "SENSE_DATA_3" : (0x0000,0x0000,0x0000,0x0000,),
                   "CHK_FRU_CODE" : (0x0000,),
                   "SENSE_DATA_5" : (0x0000,0x0000,0x0000,0x0000,),
                   "SENSE_DATA_6" : (0x0000,0x0000,0x0000,0x0000,),
                   "SENSE_DATA_7" : (0x0000,0x0000,0x0000,0x0000,),
                   "ACCEPTABLE_SNS_DATA" : (0x0000,),
                   "RPT_SEL_SNS_DATA" : (0x0000,),
                   "SRVO_LOOP_CODE" : (0x0000,),
                   "CHK_SRVO_LOOP_CODE" : (0x0000,),
                   "SEND_TUR_CMDS_ONLY" : (0x0001,),
                   "RPT_REQS_CMD_CNT" : (0x0000,),
                   "SENSE_DATA_2" : (0x0000,0x0000,0x0000,0x0000,),
                   "OMIT_DUP_ENTRY" : (0x0000,),
                   "ACCEPTABLE_IF_MATCH" : (0x0000,),
               }


               prm_538_SpinUp = {
               	#'test_num':538,
               	#'prm_name':'prm_538_SpinUp',
               	'timeout':600,
               	'TEST_FUNCTION' : (0x0000,),
               	'SELECT_COPY' : (0x0000,),
               	'READ_CAPACITY' : (0x0000,),
               	'CHK_OPEN_LATCH_RETRY_CNT' : (0x0000,),
               	'SUPRESS_RESULTS' : (0x0000,),
               	'USE_CMD_ATTR_TST_PARMS' : (0x0000,),
               	'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
               	'COMMAND_WORD_1' : (0x1B00,),
               	'COMMAND_WORD_2' : (0x0000,),
               	'COMMAND_WORD_3' : (0x0100,),
               	'COMMAND_WORD_4' : (0x0000,),
               	'COMMAND_WORD_5' : (0x0000,),
               	'COMMAND_WORD_6' : (0x0000,),
               	'SECTOR_SIZE' : (0x0000,),
               	'TRANSFER_OPTION' : (0x0000,),
               	'TRANSFER_LENGTH' : (0x0000,),
               }
               if testSwitch.FE_0157843_426568_P_CUSTOM_SPIN_UP_TIMEOUT:
                  prm_538_SpinUp['timeout'] = getattr(TP,'SpinUpTimeOut_538',600)
               prm_507_D_Sense = {
               	#'test_num':507,
               	#'prm_name':'prm_507_D_Sense',
                  'timeout':600,
                  'DESCRPTIVE_SENSE_OPTION' : (0x0001,),
               }
               prm_518_SetDSense = {
               #   'test_num' : 518,
               #   'prm_name' : 'prm_518_SetDSense',
                  'timeout' : 600,
               	"MODE_COMMAND" : (0x0001,),
               	"MODE_SENSE_OPTION" : (0x0003,),
               	"DATA_TO_CHANGE" : (0x0001),  #Bit change mode
               	#Set Byte 2, bit 2 (D_SENSE) to 1
               	"PAGE_BYTE_AND_DATA34" : (0x0221,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,),
               	"PAGE_CODE" : (0x000A,),  #Control Mode Page
               	"SAVE_MODE_PARAMETERS" : (0x0001,),
               }

               try:
                  st(517, prm_517_01)  #clear sense
               except:
                  DriveOff(self.offTime)
                  self.dut.baudRate = DEF_BAUD
                  RimOff()
                  RimOn()
                  theCell.setBaud(DEF_BAUD)
                  DriveOn(5000,12000,self.onTime)
                  self.dut.sptActive.setMode(self.dut.sptActive.availModes.intBase)
                  base_BaudFunctions.changeBaud(PROCESS_HDA_BAUD)
                  if not testSwitch.BF_0145059_231166_P_REMOVE_517_EXCEPT_CASE_SAS_PWR_RETRY:
                     st(517, prm_517_01)  #clear sense



               if testSwitch.WA_0135289_357552_DSENSE_BIT_NOT_DEFAULT_ON_34_BIT_LBA:
                  try:

                     if not testSwitch.BF_0143903_357552_P_SED_PERSONALIZE_BEFORE_CUST_CFG:
                        st(517, prm_517_01)
                     else:
                        st(538, prm_538_SpinUp)

                  except ScriptTestFailure, (failuredata):
                     if failuredata[0][2] in [11107]:
                        #If T538 failed for EC11107, need to set D_Sense for 34-LBA space in Control Mode Page
                        if testSwitch.FE_0145513_357552_P_IF3_IGNORE_11107_ERRORS:
                           st(507,prm_507_D_Sense,BYPASS_FAILURE = 0x3) #Always skip failing for 11107
                        else:
                           st(507,prm_507_D_Sense)
                           st(518,prm_518_SetDSense)
                     else:
                        if failuredata[0][2] in [10124] and testSwitch.FE_0145513_357552_P_IF3_IGNORE_11107_ERRORS:
                           st(504, TEST_FUNCTION=0x8000) #Read sense codes
                        DriveOff(10)
                        self.dut.baudRate = DEF_BAUD
                        RimOff()
                        RimOn()
                        theCell.setBaud(DEF_BAUD)
                        DriveOn(5000,12000,30)
                        self.dut.sptActive.setMode(self.dut.sptActive.availModes.intBase)
                        base_BaudFunctions.changeBaud(PROCESS_HDA_BAUD)
                        if testSwitch.FE_0145513_357552_P_IF3_IGNORE_11107_ERRORS:
                           st(517, prm_517_01)  #clear sense
                           st(507,prm_507_D_Sense,BYPASS_FAILURE = 0x3) #Always skip failing for 11107

                     st(517, prm_517_01)  #clear sense
                  except FOFSerialTestTimeout:
                     if testSwitch.WA_0145880_231166_P_FIX_INIT_HANG_BDG_DL:
                        DriveOff(10)
                        self.dut.baudRate = DEF_BAUD
                        RimOff()
                        RimOn()
                        theCell.setBaud(DEF_BAUD)
                        DriveOn(5000,12000,30)
                        self.dut.sptActive.setMode(self.dut.sptActive.availModes.intBase)
                        base_BaudFunctions.changeBaud(PROCESS_HDA_BAUD)
                        try:
                           st(517, prm_517_01)  #clear sense
                        except:
                           objMsg.printMsg("Ignoring clear sense failure")
                     else:
                        raise

               else:
                  try:
                     st(517, prm_517_01)
                  except:
                     DriveOff(10)
                     self.dut.baudRate = DEF_BAUD
                     RimOff()
                     RimOn()
                     theCell.setBaud(DEF_BAUD)
                     DriveOn(5000,12000,30)
                     self.dut.sptActive.setMode(self.dut.sptActive.availModes.intBase)
                     base_BaudFunctions.changeBaud(PROCESS_HDA_BAUD)
                     st(517, prm_517_01)  #clear sense

            else:
               try:
                  st(599,  HardReset)
                  st(528,

                     {
                           'timeout':600,
                           'spc_id':1,
                           'TEST_OPERATING_MODE' : (0,),  # 0=Power Cycle, 1=Start/Stop Unit Command
                           'ALLOW_SPEC_STATUS_COND' : (0x0000,),
                           'UNIT_READY' : (0x0000,), #0 wait for unit ready at beginning of test
                           'SPIN_DOWN_WAIT_TIME' : getattr(self,  'offTime',  30),
                           'MIN_POWER_SPIN_UP_TIME' : (2,),
                           'TEST_FUNCTION' : (0x0000,),
                           'SENSE_DATA_3' : (0x0000,0x0000,0x0000,0x0000,),
                           'SENSE_DATA_1' : (0x0000,0x0000,0x0000,0x0000,),
                           'SKP_SPINUP_AFTER_SPINDWN' : (0x0000,),
                           'MIN_POWER_SPIN_DOWN_TIME' : (10,),
                           'SENSE_DATA_2' : (0x0000,0x0000,0x0000,0x0000,),
                           'MAX_POWER_SPIN_DOWN_TIME' : 30,
                           'MAX_POWER_SPIN_UP_TIME' : int(self.readyTimeLimit/1000.0),
                           }
                     )
               except:
                  DriveOff(10)
                  self.dut.baudRate = DEF_BAUD
                  RimOff(10)
                  RimOn(30)
                  DriveOn(5000,12000,30)
                  prm_517_01 = {
                      "SENSE_DATA_8" : (0x0000,0x0000,0x0000,0x0000,),
                      "MAX_REQS_CMD_CNT" : (0x000F,),
                      "SENSE_DATA_4" : (0x0000,0x0000,0x0000,0x0000,),
                      "SENSE_DATA_1" : (0x0000,0x0000,0x0000,0x0000,),
                      "TEST_FUNCTION" : (0x0000,),
                      "SENSE_DATA_3" : (0x0000,0x0000,0x0000,0x0000,),
                      "CHK_FRU_CODE" : (0x0000,),
                      "SENSE_DATA_5" : (0x0000,0x0000,0x0000,0x0000,),
                      "SENSE_DATA_6" : (0x0000,0x0000,0x0000,0x0000,),
                      "SENSE_DATA_7" : (0x0000,0x0000,0x0000,0x0000,),
                      "ACCEPTABLE_SNS_DATA" : (0x0000,),
                      "RPT_SEL_SNS_DATA" : (0x0000,),
                      "SRVO_LOOP_CODE" : (0x0000,),
                      "CHK_SRVO_LOOP_CODE" : (0x0000,),
                      "SEND_TUR_CMDS_ONLY" : (0x0001,),
                      "RPT_REQS_CMD_CNT" : (0x0000,),
                      "SENSE_DATA_2" : (0x0000,0x0000,0x0000,0x0000,),
                      "OMIT_DUP_ENTRY" : (0x0000,),
                      "ACCEPTABLE_IF_MATCH" : (0x0000,),
                  }
                  st(517, prm_517_01)  #clear sense

                  prm_538_SpinUp = {
                  	#'test_num':538,
                  	#'prm_name':'prm_538_SpinUp',
                  	'timeout':600,
                  	'TEST_FUNCTION' : (0x0000,),
                  	'SELECT_COPY' : (0x0000,),
                  	'READ_CAPACITY' : (0x0000,),
                  	'CHK_OPEN_LATCH_RETRY_CNT' : (0x0000,),
                  	'SUPRESS_RESULTS' : (0x0000,),
                  	'USE_CMD_ATTR_TST_PARMS' : (0x0000,),
                  	'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
                  	'COMMAND_WORD_1' : (0x1B00,),
                  	'COMMAND_WORD_2' : (0x0000,),
                  	'COMMAND_WORD_3' : (0x0100,),
                  	'COMMAND_WORD_4' : (0x0000,),
                  	'COMMAND_WORD_5' : (0x0000,),
                  	'COMMAND_WORD_6' : (0x0000,),
                  	'SECTOR_SIZE' : (0x0000,),
                  	'TRANSFER_OPTION' : (0x0000,),
                  	'TRANSFER_LENGTH' : (0x0000,),
                  }
                  if testSwitch.FE_0157843_426568_P_CUSTOM_SPIN_UP_TIMEOUT:
                     prm_538_SpinUp['timeout'] = getattr(TP,'SpinUpTimeOut_538',600)
                  st(538, prm_538_SpinUp)

            #st(599,  HardReset)

         else:
            # SIC T528 implementation. 
            
            if testSwitch.BF_0185696_231166_P_DRIVEON_BEFORE_528:
               DriveOn(self.setVoltages[1], self.setVoltages[2], self.onTime)

            DisableStaggeredStart(True)
            if sptCmds.objComMode.getMode() != sptCmds.objComMode.availModes.intBase:
               theRim.EnableInitiatorCommunication(sptCmds.objComMode)

            self.dut.objSeq.suppressresults = 0 #disable any previous suppression as these are only st not St funcs
            if testSwitch.FE_0133860_372897_ADD_PARA_TEST_FUNCTION_FOR_T528 :
               spinUpFlag = self.getSpinUpFlag()
               sptCmds.objComMode.setMode(sptCmds.objComMode.availModes.intBase)
               try:
                  spinupOptionsExt = 0
                  if testSwitch.FE_0165113_231166_P_SIC_PHY_READY_TTR:
                     OverrideMinSpinDownTime = 0x10
                     PhyDetect = 0x1000
                     spinupOptionsExt = spinUpFlag | PhyDetect | OverrideMinSpinDownTime

                  st(528, {
                           'MAX_POWER_SPIN_UP_TIME': int(self.readyTimeLimit/1000.0),
                           'MILLISECOND_SCALE': 1,
                           'SPIN_DOWN_WAIT_TIME': getattr(self,  'offTime',  30),
                           'timeout': 600,
                           'MIN_POWER_SPIN_UP_TIME': 0,
                           'TEST_FUNCTION': spinUpFlag | spinupOptionsExt,
                           }
                     )


               except ScriptTestFailure, (failureData):
                  ec =failureData[0][2]
                  if ec == 10200 :
                     objMsg.printMsg("Ignoring TTR from 528 for parametric adjustment.")
                  else:
                     raise

               self.dut.baudRate = DEF_BAUD

               if not self.downloadActive:
                  if testSwitch.virtualRun:
                     self.readyTime = 1
                  else:
                     self.readyTime = int(float(self.dut.dblData.Tables('P528_TIMED_PWRUP').tableDataObj()[-1]['POWERUP_TIME']) * 1000)
                     
                  Offset = float(getattr(TP, 'T528_OFFSET', 0))
                  if Offset != 0:
                     self.readyTime = int(self.readyTime + Offset)
                     objMsg.printMsg("T528 new self.readyTime:%s Offset=%s" % (self.readyTime, Offset))

                  if testSwitch.FE_0165113_231166_P_SIC_PHY_READY_TTR:
                     std_dev_ratio = getattr(TP, 'TTR_std_dev_ratio', 0.238095)
                     MeanAdjustment = getattr(TP, 'TTR_MeanAdjustment', 0.7)
                     TTR_Mean = getattr(TP, 'TTR_Mean', self.readyTime) #sentosa was 5.77 sec

                     if TTR_Mean != self.readyTime:
                        TTR_Mean = (( -1*( self.readyTime- TTR_Mean )) * std_dev_ratio) + self.readyTime


                     readyTimeAdj = TTR_Mean - MeanAdjustment
                     objMsg.printMsg("Actual Ready time %s; adjusted = %f" % (self.readyTime, readyTimeAdj,))
                     self.readyTime = readyTimeAdj

                  if testSwitch.BF_0157675_231166_P_FIX_SIC_TTR_SCALER_TO_MS or testSwitch.FE_0165113_231166_P_SIC_PHY_READY_TTR:
                     self.readyTime *= 1000 # scale to Msec

                  self.logPowerOn_Information(self.readyTime,spinUpFlag,{})
            else:
               sptCmds.objComMode.setMode(sptCmds.objComMode.availModes.intBase)

               if testSwitch.FE_0160608_395340_P_FIX_FAILURE_FROM_T514_ON_SIC:
                  #Set transfer rate before T528 P'Supitcha SIC
                  self.powerOff(offTime = 10,  driveOnly = 0)
                  self.powerOn(set5V=5000, set12V=12000, onTime=10, baudRate=PROCESS_HDA_BAUD, useESlip=0,  driveOnly = 0,  readyTimeLimit = self.readyTimeLimit, ataReadyCheck = 0)
                  st([535], [], {'TEST_OPERATING_MODE': (11,), 'timeout': 600, 'spc_id': 1})

               try:
                  st(528, {
                        'TEST_FUNCTION': 0x1010,
                        'MILLISECOND_SCALE': 1,
                        'MAX_POWER_SPIN_UP_TIME': self.readyTimeLimit,
                        'SPIN_DOWN_WAIT_TIME': getattr(self,  'offTime',  30),
                        'timeout': 600,
                        'MIN_POWER_SPIN_UP_TIME': 0,
                        }
                  )
               except ScriptTestFailure, (failureData):
                  ec =failureData[0][2]
                  if ec == 10200 and self.downloadActive:
                     objMsg.printMsg("TTR failures ignored during download code.")
                  else:
                     raise
               self.dut.baudRate = DEF_BAUD

               if not self.downloadActive or not testSwitch.FE_0165086_231166_P_INGORE_TTR_IN_FIN2_DL:
                  if testSwitch.virtualRun:
                     self.readyTime = 1
                  else:
                     self.readyTime = int(float(self.dut.dblData.Tables('P528_TIMED_PWRUP').tableDataObj()[-1]['POWERUP_TIME']) * 1000)

                  if testSwitch.BF_0157675_231166_P_FIX_SIC_TTR_SCALER_TO_MS:
                     self.readyTime *= 1000 # scale to Msec
					 
                  Offset = float(getattr(TP, 'T528_OFFSET', 0))
                  if Offset != 0:
                     self.readyTime = int(self.readyTime + Offset)
                     objMsg.printMsg("T528 new self.readyTime:%s Offset=%s" % (self.readyTime, Offset))

                  spinUpFlag = self.getSpinUpFlag()
                  self.logPowerOn_Information(self.readyTime,spinUpFlag,{})

         if not testSwitch.WA_0124652_231166_DISABLE_SET_XFER_SPEED and not ttrMode:
            self.setXferRate()
      finally:
         # UnRegistered Resume normal 15 calls
         RegisterResultsCallback('', [13,14,15])

      self.incrementLifetimePowerCycleCounter()

   def setXferRate(self):
      if testSwitch.BF_0177886_231166_P_FIX_XFR_RATE_DIAG_TRANSITION:
         return self.ICmd.setMaxXferRate()
      else:
         if objRimType.baseType in SAS_RiserBase:
            speedLookup = [(4, 6, 8), #6.0Gbs
                           (2, 3, 4), #3.0Gbs
                           (1, 1.5, 2), #1.5Gbs
                           ]
         else:
            speedLookup = [
                           (6, 6, 8), #6.0Gbs
                           (3, 3, 4), #3.0Gbs
                           (1, 1.5, 2), #1.5Gbs
                           ]
   
         if self.drvATASpeed == 0:
            from IntfClass import CIdentifyDevice
            self.drvATASpeed = CIdentifyDevice(force = True).ID['SATACapabilities']
   
         MaxCellSpeed = max(theRim.getValidRim_IOSpeedList())
         objMsg.printMsg("MaxCellSpeed=%s" % MaxCellSpeed)
   
         for enum,rate,bitmask in speedLookup:
            if (self.drvATASpeed & bitmask) and (rate <= MaxCellSpeed):
               objMsg.printMsg("Setting transfer rate: enum=%s,rate=%2.2fGbs,bitmask=%s" % (enum,rate,bitmask))
   
               # st(533,  FC_SAS_TRANSFER_RATE = enum, timeout = 100)

               try:     # YarraR 6G workaround
                  st(533,  FC_SAS_TRANSFER_RATE = enum, timeout = 100)
               except:
                  objMsg.printMsg("Power cycle workaround. Error In T533 : %s" % (traceback.format_exc(),))
                  DriveOff(pauseTime=10)
                  DriveOn(pauseTime=10)
                  st(533,  FC_SAS_TRANSFER_RATE = enum, timeout = 100)

               st(535,  FC_SAS_TRANSFER_RATE = enum, TEST_OPERATING_MODE = 9, timeout = 100)

               self.dut.driveattr['XFER_CAP'] = rate
               break
         else:
            if not testSwitch.virtualRun:
               ScrCmds.raiseException(12413, "Unable to match/set xfer rate. ID SATACapabilities=%s" % self.drvATASpeed)

   #----------------------------------------------------------------------------
   def powerCycle(self, set5V=5000, set12V=12000, offTime=10, onTime=10, baudRate=PROCESS_HDA_BAUD, useESlip=0, ataReadyCheck = True):
      self.setVoltages = (3000,set5V,set12V)
      #Enable the disable staggered start function so drive will come ready sooner- this has to do with default
      # Initiator wiring for the staggered start PIN11 for SATA- SAS interaction not defined
      DisableStaggeredStart(True)
      if (ataReadyCheck and not self.certOper) or ataReadyCheck == 'force':
         try:
            self.initiatorDriveReadyPwrCycle()
            self.TCGCheckUnlock()
            return
         except (FOFSerialCommError, ScriptTestFailure,FOFSerialTestTimeout):
            if self.firstPowerCycleFailed:
               raise
            else:
               self.firstPowerCycleFailed = True
               objMsg.printMsg("FAILED!\n%s" % (traceback.format_exc(),))
               ataReadyCheck = 0


      self.powerOff(offTime,  driveOnly = ataReadyCheck)
      self.powerOn(set5V,  set12V,  onTime,  baudRate,  useESlip,  driveOnly = ataReadyCheck,  readyTimeLimit = self.readyTimeLimit, ataReadyCheck = ataReadyCheck)

      if not self.certOper:
         if objRimType.baseType in SAS_RiserBase or not testSwitch.BF_0155580_231166_P_DISABLE_517_PWR_CYCLE_SATA:
            prm_517_01 = {
             "SENSE_DATA_8" : (0x0000,0x0000,0x0000,0x0000,),
             "MAX_REQS_CMD_CNT" : (0x00FF,),
             "SENSE_DATA_4" : (0x0000,0x0000,0x0000,0x0000,),
             "SENSE_DATA_1" : (0x0000,0x0000,0x0000,0x0000,),
             "TEST_FUNCTION" : (0x0000,),
             "SENSE_DATA_3" : (0x0000,0x0000,0x0000,0x0000,),
             "CHK_FRU_CODE" : (0x0000,),
             "SENSE_DATA_5" : (0x0000,0x0000,0x0000,0x0000,),
             "SENSE_DATA_6" : (0x0000,0x0000,0x0000,0x0000,),
             "SENSE_DATA_7" : (0x0000,0x0000,0x0000,0x0000,),
             "ACCEPTABLE_SNS_DATA" : (0x0000,),
             "RPT_SEL_SNS_DATA" : (0x0001,),
             "SRVO_LOOP_CODE" : (0x0000,),
             "CHK_SRVO_LOOP_CODE" : (0x0000,),
             "SEND_TUR_CMDS_ONLY" : (0x0001,),
             "RPT_REQS_CMD_CNT" : (0x0001,),
             "SENSE_DATA_2" : (0x0000,0x0000,0x0000,0x0000,),
             "OMIT_DUP_ENTRY" : (0x0000,),
             "ACCEPTABLE_IF_MATCH" : (0x0000,),
             "SEND_TUR_CMDS_ONLY": 1,
                  }
            SetFailSafe()
            st(517, prm_517_01)  #clear sense
            prm_517_RequestSense5 = {
                "ACCEPTABLE_IF_MATCH" : (0x0000,),
                "ACCEPTABLE_SNS_DATA" : (0x0000,),
                "CHK_FRU_CODE" : (0x0000,),
                "CHK_SRVO_LOOP_CODE" : (0x0000,),
                "MAX_REQS_CMD_CNT" : (0x0005,),
                "OMIT_DUP_ENTRY" : (0x0000,),
                "RPT_REQS_CMD_CNT" : (0x0000,),
                "RPT_SEL_SNS_DATA" : (0x0000,),
                "SEND_TUR_CMDS_ONLY" : (0x0000,),
                "SENSE_DATA_1" : (0x0002,0x0000,0x00FF,0x0004,),
                "SENSE_DATA_2" : (0x0004,0x0000,0x00FF,0x001C,),
                "SENSE_DATA_3" : (0x0004,0x0000,0x00FF,0x0042,),
                "SENSE_DATA_4" : (0x0001,0x0000,0x00FF,0x005D,),
                "SENSE_DATA_5" : (0x0000,0x0000,0x0000,0x0000,),
                "SENSE_DATA_6" : (0x0000,0x0000,0x0000,0x0000,),
                "SENSE_DATA_7" : (0x0000,0x0000,0x0000,0x0000,),
                "SENSE_DATA_8" : (0x0000,0x0000,0x0000,0x0000,),
                "SRVO_LOOP_CODE" : (0x0000,),
                "TEST_FUNCTION" : (0x0000,),
            }
            st(517, prm_517_RequestSense5)
            ClearFailSafe()

         self.TCGCheckUnlock()


###########################################################################################################
###########################################################################################################
class CPowerControlATA(CPowerControlSerial):
   """
      Powers Control class for ATA drive testing in interface mode
      This class overrides the base CPowerControl class to implement ATA interface specific commands
   """
   def __init__(self, readyTimeLimit=15000,):
      CPowerControlSerial.__init__(self,readyTimeLimit)

      objMsg.printMsg('ATA Ready Time Limit: %d' %  self.readyTimeLimit)

   #------------------------------------------------------------------------------------------------------#
   def __ataIdentify(self):
      res = IntfClass.CIdentifyDevice().ID                   # Read device settings with identify device
      self.eslipToggleRetry(setACKOff = True)
      return res

   #------------------------------------------------------------------------------------------------------#
   def eslipToggleRetry(self, setACKOff = False):
      # If older CPC revision - not all params supported - skip it
      base_BaudFunctions.eslipToggleRetry(setACKOff = setACKOff)


   #------------------------------------------------------------------------------------------------------#
   def powerCycle(self, set5V=5000, set12V=12000, offTime=10, onTime=10, baudRate=PROCESS_HDA_BAUD, useESlip=0, ataReadyCheck = True):
      self.setVoltages = (3000,set5V,set12V)
      self.powerOff(offTime)
      if testSwitch.BF_0145507_231166_P_FIX_ATA_READY_IN_CERT_OPER:
         if self.certOper:
            ataReadyCheck = False
      self.powerOn(set5V, set12V, onTime, baudRate, useESlip, ataReadyCheck)
      
      if not testSwitch.WA_0124652_231166_DISABLE_SET_XFER_SPEED and not self.certOper and ataReadyCheck:
         self.setXferRate()
      
   #-----------------------------------------------------------------------------------------#
   def setXferRate(self):
      """ Set max transfer rate in CPC """ 
      speedLookup = [
                     (2, 3, 4),   #3.0Gbs
                     (1, 1.5, 2), #1.5Gbs
                     ]
      if self.drvATASpeed == 0:
         from IntfClass import CIdentifyDevice
         self.drvATASpeed = CIdentifyDevice().ID['SATACapabilities']
         
      MaxCellSpeed = max(theRim.getValidRim_IOSpeedList())
      objMsg.printMsg("MaxCellSpeed=%s" % MaxCellSpeed)
                     
      for enum,rate,bitmask in speedLookup:
         if self.drvATASpeed & bitmask and rate <= MaxCellSpeed:
            objMsg.printMsg("Setting transfer rate: enum=%s,rate=%2.2fGbs,bitmask=%s" % (enum,rate,bitmask))
            st(533,  INTERFACE_SPEED = enum, CTRL_WORD1 = 0x0100, timeout = 100)
            st(535,  CTRL_WORD1 = 3, timeout = 100)
            self.dut.driveattr['XFER_CAP'] = rate
            break
      else:
         if not testSwitch.virtualRun:
            ScrCmds.raiseException(12413, "Unable to match/set xfer rate. ID SATACapabilities=%s" % self.drvATASpeed)

   #-----------------------------------------------------------------------------------------#
   def ATAReadyCheck(self, driveOnTime=0):
      data = {}
      readyTimeLoop  = 30


      if driveOnTime == 0:
         driveOnTime = time.time()

      for self.readyTime in range(3, readyTimeLoop):       # Temp timming work around
         data = ICmd.TestUnitReady(1)
         if data.has_key('STS') == 0:
            data['STS'] = -1      # To avoid 11044
         if data.has_key('LLRET') == 0:
            data['LLRET'] = -1
         if data['LLRET'] == OK and data['STS'] == '80':
            break

      endTime = time.time()
      elapsed_time = str(endTime - driveOnTime)
      elapsed = float(elapsed_time)

      objMsg.printMsg('ATA Ready Check Time = %d sec' % elapsed)
      objMsg.printMsg('ATA Ready Check, data=%s' % `data`)

      self.readyTime = elapsed * 1000      # Msec

      if data['LLRET'] == OK and data['STS'] == '80':
         if self.readyTime <= self.readyTimeLimit:
            objMsg.printMsg('ATA Ready Passed in %d Msec. Limit = %d ' % (self.readyTime, self.readyTimeLimit))
            error = 0
         else:
            objMsg.printMsg('ATA Ready Failed in %d Msec. Limit = %d ' % (self.readyTime, self.readyTimeLimit))
            error = 1

      else: # each loop takes approx 2 seconds
         objMsg.printMsg('Drive did NOT come Ready in %d Seconds' % readyTimeLoop)
         error = 1

      return error,data

   #-----------------------------------------------------------------------------------------#
   def spinUpOnPower(self, set5V=5000, set12V=12000, selection ='SetFeatures'):
      theCarrier.powerOnPort(set5V, set12V, onTime=0)
      data = ICmd.SetIntfTimeout(1000)
      if selection == 'HardReset':
         objMsg.printMsg('Script issue HardReset')
         time.sleep(1)
         driveOnTime = time.time()
         data = ICmd.HardReset()
      else:
         objMsg.printMsg('Script issue SetFeatures 0x07')
         time.sleep(1)
         driveOnTime = time.time()
         ICmd.SetFeatures(0x07, 0x45)

      error = self.ATAReadyCheck(driveOnTime)
      return error,data

   #------------------------------------------------------------------------------------------------------#
   def powerOn(self, set5V=5000, set12V=12000, onTime=10, baudRate=PROCESS_HDA_BAUD, useESlip=0, ataReadyCheck = True):
      """
         Powers on drive in ATA interface mode
      """

      if useESlip == 1 or (self.certOper and testSwitch.BF_0160549_342996_P_FIX_ATA_READY_IN_CERT_OPER_ADDN): # Allow Cert Process to complete on CPC cell for LPMULE
         if testSwitch.FE_0110517_347506_ADD_POWER_MODE_TO_DCM_CONFIG_ATTRS:
            spinUpFlag = self.getSpinUpFlag()
            CPowerControlSerial.powerOn(self,set5V, set12V, onTime, baudRate, useESlip = 1, spinUpFlag = spinUpFlag)
         else:
            CPowerControlSerial.powerOn(self,set5V, set12V, onTime, baudRate, useESlip = 1)
      else:
         self.dut.sptActive.setMode(self.dut.sptActive.availModes.intBase)
         
         theCell.disableESlip()
         theCell.setBaud()
         set3V = 0
         self.setVoltages = (set3V,set5V,set12V)
         self.onTime = max(onTime, getattr(TP,'APMTime', 0))

         timeout = 150000
         err = 1; retry = 2; loop = 0
         while loop <= retry:
            loop = loop + 1


            spinUpFlag = self.getSpinUpFlag()
            if spinUpFlag == 0:
               theCarrier.powerOnPort(set5V, set12V, onTime = self.onTime)

               self.incrementLifetimePowerCycleCounter()

               time.sleep(15)
               ICmd.HardReset()
               err,data = self.ATAReadyCheck()
               if not testSwitch.FE_0163871_336764_P_DO_LOGPOWERON_AFTER_COMPLETE_FULL_PWC_RETRY:
                  if ( ataReadyCheck and not self.downloadActive) or not testSwitch.BF_0160098_231166_P_DISABLE_READY_VAR_CHECK_DISABLED:
                     self.logPowerOn_Information(self.readyTime,spinUpFlag,data)
               break

            else:
               data = ICmd.PowerOnTiming(timeout+(self.onTime*1000), spinUpFlag) # These 3 Commands must be together, Nothing in between
               theCarrier.powerOnPort(set5V, set12V, onTime = self.onTime)

               data = ICmd.StatusCheck()                             # This gets Ready check time from the NIOS.
               if data['LLRET'] != OK:
                  objMsg.printMsg('ATA Ready Failed GetPowerOnTime Data = %s' % data)
                  self.powerOff()
                  continue

               self.readyTime = int(data['SpinUpTm'])                # mSec - String to Int

               if not testSwitch.FE_0163871_336764_P_DO_LOGPOWERON_AFTER_COMPLETE_FULL_PWC_RETRY:
                  if ( ataReadyCheck and not self.downloadActive) or not testSwitch.BF_0160098_231166_P_DISABLE_READY_VAR_CHECK_DISABLED:
                     self.logPowerOn_Information(self.readyTime,spinUpFlag,data)

               if ( self.readyTime <= self.readyTimeLimit ) or ( ataReadyCheck == False or self.downloadActive == True ):
                  objMsg.printMsg('ATA Ready Passed in %d Msec. Limit = %d ' % (self.readyTime, self.readyTimeLimit))
                  err = 0
                  break

               objMsg.printMsg('ATA Ready Failed in %d Msec. Limit = %d ' % (self.readyTime, self.readyTimeLimit))
               if ataReadyCheck:
                  self.powerOff()

         if testSwitch.FE_0163871_336764_P_DO_LOGPOWERON_AFTER_COMPLETE_FULL_PWC_RETRY:
            if ( ataReadyCheck and not self.downloadActive) or not testSwitch.BF_0160098_231166_P_DISABLE_READY_VAR_CHECK_DISABLED:
               self.logPowerOn_Information(self.readyTime,spinUpFlag,data)

         self.KwaiCheckUnlock()
         if testSwitch.FE_0121834_231166_PROC_TCG_SUPPORT:
            self.TCGCheckUnlock()
         sptCmds.disableAPM()
         
         objPwrCtrl.eslipToggleRetry(setACKOff = True) # F3 code doesn't support extra ack

         ICmd.CRCErrorRetry(IO_CRC_RETRY_VAL)

         if err:
            msg = "Drive failed to power on and come ready in interface mode"

            if ataReadyCheck and not self.downloadActive:
               ScrCmds.raiseException(13424, msg)
            else:
               objMsg.printMsg("Ignored failure occured: %s" % msg)
               theCarrier.powerOnPort(set5V, set12V, onTime = self.onTime)


   #------------------------------------------------------------------------------------------------------#
   def KwaiCheckUnlock(self):
      """
         Checking and unlocking serial and interface port for FDE drive in ATA mode
      """
      kwaiPrep = self.dut.objData.retrieve('KwaiPrepDone')

      if kwaiPrep == 1:    # Post KwaiPrep support for FDE drives - knl 3Apr08
         objMsg.printMsg("CPowerControlATA powerCycle unlocking FDE Serial Port")
         from KwaiPrep import CKwaiPrepTest
         import serialScreen
         oSerial = serialScreen.sptDiagCmds()
         data = sptCmds.execOnlineCmd(DOT, timeout = 10, waitLoops = 100)
         objMsg.printMsg("Data returned from DOT command - data = %s" % `data`)

         if (data.find("Serial Port Disabled") > -1):
            objMsg.printMsg("Serial Port Disabled. Proceed with CTRL_Z and UnlockSerialPort")
            data = sptCmds.execOnlineCmd(CTRL_Z, timeout = 10, waitLoops = 100)
            objMsg.printMsg("Data returned from CtrlZ command - data = %s" % `data`)

            if testSwitch.FE_0121834_231166_PROC_TCG_SUPPORT:
               if oSerial.isSeaCosLocked(data) == True:
                  #from KwaiPrep import *
                  result = CKwaiPrepTest(self.dut).UnlockSerialPort(0)
                  objMsg.printMsg("Serial port unlock result = %s" % result)
               else:
                  objMsg.printMsg("FDE Serial port unlock error")
            else:
               if oSerial.isLocked(data) == True:
                  #from KwaiPrep import *
                  result = CKwaiPrepTest(self.dut).UnlockSerialPort(0)
                  objMsg.printMsg("Serial port unlock result = %s" % result)
               else:
                  objMsg.printMsg("FDE Serial port unlock error")
         else:
            objMsg.printMsg("Serial Port is enabled. Unlock not required")

         objMsg.printMsg("CPowerControlATA powerCycle unlocking FDE Interface Port")
         oKwaiPrep = CKwaiPrepTest(self.dut)
         # Only drive KwaiPrep with FDE Card issued can unlock the Interface
         if oKwaiPrep.PREBOOT:
            try:
               oKwaiPrep.UnlockInterface()
            except:
               objMsg.printMsg("CPowerControlATA: Drive failed to unlock interface mode")
               ScrCmds.raiseException(14725, "Drive failed to unlock interface mode")
         else:
            objMsg.printMsg("Interface unlock not required")

   #------------------------------------------------------------------------------------------------------#





################################################################################
################################################################################
class CPowerCtrl(object):
   """
   ContextClass to deploy abstraction for pwrObject to allow for dynamic creation of the power objects in VE. Intra slot only 1 class is ever created.
   """
   def __init__(self):
      self.__pwrObjectSerial = None
      self.__pwrObjectATA = None
      self.__pwrObjectInterface = None
      objDut.driveattr['ATA_ReadyTimeout'] = 'default'
   #----------------------------------------------------------------------------
   def getobj(self):
      #Implement dynamic binding on power objects in case RIM changes mid-test (VE consideration- should be minimal execution impact (1 compare and 1 ref set)

      readyTimeLimit = self.getReadyTimeLimit()

      if objRimType.SerialOnlyRiser() or testSwitch.NoIO:
         if self.__pwrObjectSerial == None:
            self.__pwrObjectSerial = CPowerControlSerial(readyTimeLimit)
         pwrObject = self.__pwrObjectSerial
      elif objRimType.CPCRiser():
         if self.__pwrObjectATA == None:
            from ICmdFactory import ICmd
            self.__pwrObjectATA = CPowerControlATA(readyTimeLimit)
            self.__pwrObjectATA.ICmd = ICmd
         pwrObject = self.__pwrObjectATA
      elif objRimType.IOInitRiser():
         if self.__pwrObjectInterface == None:
            from ICmdFactory import ICmd
            self.__pwrObjectInterface = CPowerControlInterface(readyTimeLimit)
            self.__pwrObjectInterface.ICmd = ICmd
         pwrObject = self.__pwrObjectInterface

      pwrObject.readyTimeLimit = readyTimeLimit
      
      return pwrObject
   
   #----------------------------------------------------------------------------
   def getReadyTimeLimit(self):
      """ Implements readyTimeLimit based on customer """

      # Don't query from DCM during cert oper and non-production mode.
      # if objDut.certOper and not ConfigVars[CN].get('PRODUCTION_MODE',0):
      readyTimeLimit = CBasePowerControl().readyTimeLimit
      # else:
         # PIFHandler = CPIFHandler(useDCM = testSwitch.FE_0155581_231166_PROCESS_CUSTOMER_SCREENS_THRU_DCM)
         # customer = PIFHandler.Customer(objDut.partNum)
         # if customer is None:
            # readyTimeLimit = CBasePowerControl().readyTimeLimit
         # elif objDut.readyTimeLimit is None:
            # # Set TTR from DCM as first priority
            # if testSwitch.FE_0155581_231166_PROCESS_CUSTOMER_SCREENS_THRU_DCM:
               # try:               
                  # readyTimeLimit = int(objDut.driveConfigAttrs.get("TIME_TO_READY",("=",''))[1])
                  # objDut.readyTimeLimit = readyTimeLimit
                  # return readyTimeLimit
               # except ValueError:    # No entry from DCM
                  # pass
            
            # # If no DCM TIME_TO_READY, set TTR as per partnumber                  
            # if hasattr(TP, 'prm_TTR_ByPn'):
               # partNum = objDut.partNum
               # for pn in TP.prm_TTR_ByPn:   # PN wildcard support
                  # mat = re.compile(pn)
                  # if mat.search(partNum):
                     # readyTimeLimit = TP.prm_TTR_ByPn.get(pn)
                     # if not ConfigVars[CN].get('PRODUCTION_MODE',0): #for development phase only. Check whether dcm has SC1 customer test.
                        # from CustomCfg import CCustomCfg
                        # CustConfig = CCustomCfg()
                        # dcm_data = CustConfig.getDriveConfigAttributes()

                        # if 'SC1' in dcm_data.get('CUST_TESTNAME',('=','NONE'))[1]:
                           # readyTimeLimit = getattr(TP, 'SBS_TTR_Spec', 6000)
                           # objMsg.printMsg("Drive will be configured as low current spin up drive")
                        # else:
                           # objMsg.printMsg("Drive will be configured as normal spin up drive")

                     # objDut.readyTimeLimit = readyTimeLimit
                     # return readyTimeLimit

            # # Otherwise set TTR limits based on RPM, interface type, customer, and number of heads    
            # from base_IntfTest import CZoneXferTest
            # CZoneXferTest(objDut).set_rpm()                    
            # rpm = objDut.driveattr.get('SPINDLE_RPM','NONE')
            # usb_intf = {'N':"NON_USB",'Y':"USB"}.get(objDut.driveattr.get('USB_INTF','N'))
            # readyTimeLimit = prm_PowerControl.get(rpm)[usb_intf][customer][objDut.imaxHead]
   
         # else:
            # readyTimeLimit = objDut.readyTimeLimit      
   
      objDut.readyTimeLimit = readyTimeLimit
      return readyTimeLimit 
      
   #----------------------------------------------------------------------------
   def __getattr__(self,name):

      pwrObject = self.getobj()
      return getattr(pwrObject,name)

   #----------------------------------------------------------------------------
   def __setattr__(self,name,value):
      print "Setting %s to %s" % (name, value)
      if not name in ['_CPowerCtrl__pwrObjectInterface', '_CPowerCtrl__pwrObjectATA', '_CPowerCtrl__pwrObjectSerial']:
         pwrObject = self.getobj()
         setattr(pwrObject,name,value)
      else:
         super(CPowerCtrl,self).__setattr__(name,value)


objPwrCtrl =  CPowerCtrl()
