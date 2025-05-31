#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: The Rim object is an abstraction of the cell RIM and implements methods to implement
#              to power on/off rim, download CPC/NIOS/Serial code etc.
#              Note that only once instance of rim must exist in the entire test environment.
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/IORim.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/IORim.py#1 $
# Level: 4
#---------------------------------------------------------------------------------------------------------#

from Constants import *
import ScrCmds, time
import MessageHandler as objMsg
import traceback
from baseRim import baseCRim
from UartCls import theUart
from Drive import objDut as dut
import time

try:
   #Not all CM's support the following functions
   SPortToInitiator
except NameError:
   def SPortToInitiator( flag):
      return False
   def DisableStaggeredStart( flag):
      return False

class IORim(baseCRim):
   def __init__(self, objRimType):
      baseCRim.__init__(self,objRimType)
      if testSwitch.BF_0177886_231166_P_FIX_XFR_RATE_DIAG_TRANSITION:
         ScrCmds.trcBanner("Testing Started on IO Initiator Cell")
         ScrCmds.insertHeader("Testing Started on IO Initiator Cell",length = 40)

      self.mustPowerOn = True
      self.initRimRequired = True

   def initRim(self):
      if testSwitch.BF_0177886_231166_P_FIX_XFR_RATE_DIAG_TRANSITION:
         if getattr(dut, 'certOper', True) == False:
            self.EnableInitiatorCommunication()
         self.initRimRequired = False
      else:
         ScrCmds.trcBanner("Testing Started on IO Initiator Cell")
         ScrCmds.insertHeader("Testing Started on IO Initiator Cell",length = 40)


   def RimOff(self, offTime = 10):
      if testSwitch.BF_0156515_231166_P_EXT_ON_TIME_INIT_PWR_ON:
         RimOff(offTime)
      else:
         RimOff()
      self.mustPowerOn = True
      theUart.setBaud(DEF_BAUD)
      self.initRimRequired = True

   def RimOn(self, onTime = 1):
      if testSwitch.BF_0156515_231166_P_EXT_ON_TIME_INIT_PWR_ON:
         RimOn(onTime)
      else:
         RimOn()
      self.mustPowerOn = False

   #------------------------------------------------------------------------------------------------------#
   def getValidRimBaudList(self, baudRate):
      """
      Returns valid baud rates for rim
      """

      cellBaudList = (Baud38400, Baud115200, Baud390000, Baud460800, Baud625000, Baud921600, Baud1228000)

      cellBaudList, baudRate = self.base_getValidRimBaudList(baudRate, cellBaudList)

      return cellBaudList, baudRate

   def getRimCodeVer(self):
      prm_535_InitiatorRev = {
                  "TEST_OPERATING_MODE" : (0x0002,),
                  "TEST_FUNCTION" :       (0x8800,),
               }
      st(535, **prm_535_InitiatorRev)

   def DisableInitiatorCommunication(self, comModeObj = None, failCommRetries = True):
      objMsg.printMsg("StackFrame: %s" % (StackFrameInfo(),))
      if comModeObj != None:
         objMsg.printMsg("CurrentMode: %s" % (comModeObj.getMode(),))
         if comModeObj.getMode() != comModeObj.availModes.intBase:
            return
      try:
         if not self.objRimType.isNeptuneRiser(): #skip t507 if in Neptune
            st(507, ACTIVE_LED_ON = 2, timeout = 30) #Switch spt end point to drive instead of inititator
         else:
            SPortToInitiator(False)

         time.sleep(15)
      except:
         objMsg.printMsg("Error: %s" % (traceback.format_exc(),))

      #now talking to the drive
      objMsg.printMsg("Setting uart baud to talk to drive back to %d" % dut.baudRate)
      theUart.setBaud(dut.baudRate)

      if True:
         # This algorithm isn't PIOS compatible as we can't come out of pois w/ spt on f3 code
         for retry in xrange(10):

            res = GChar()
            PBlock('a')       # disable apm
            time.sleep(1)
            PBlock(CTRL_Z)    # toggle ASCII Diagnostic Mode
            time.sleep(10)
            if testSwitch.FE_0175466_340210_DIAG_UNLOCK and (comModeObj.getMode() != comModeObj.availModes.mctBase):
               try:
                  accumulator = PChar('\n')
                  del accumulator
                  time.sleep(.2)
                  accumulator = PBlock(UNLOCK_CMD)
                  del accumulator
                  time.sleep(.2)
                  accumulator = PChar('\n')                                             
                  del accumulator               
                  time.sleep(.2)
               except:
                  objMsg.printMsg("WARNING - UNLOCK command did not execute")
            PBlock(CTRL_T)    # toggle ESLIP Mode
            time.sleep(10)
            res += GChar()
            if testSwitch.BF_0188304_340210_SUPPRESS_UNLOCK_IN_SIC:
               res = res.replace(UNLOCK_CMD, '****')
            if not testSwitch.FE_0177176_345172_ENABLE_RETURN_VALUE_CHECKING_FROM_T507 and res != '':
               objMsg.printMsg("Got a response from drive after switch:\n%s" % (res,))
               break
            elif testSwitch.FE_0177176_345172_ENABLE_RETURN_VALUE_CHECKING_FROM_T507 and res != '' and res.find('T>')> -1:
               objMsg.printMsg("Got a response from drive after switch:\n%s" % (res,))
               break
            else:
               self.RimOff()
               SPortToInitiator(False)
               if retry > 6:
                  objMsg.printMsg("Trying power cycle of drive to resurect SPT.")
                  DriveOff()
                  dut.baudRate = DEF_BAUD
                  theUart.setBaud(dut.baudRate)
                  DriveOn()

      if False:#not testSwitch.BF_0162483_426568_P_SKIP_POWER_CYCLES_IN_DISABLE_INITIATOR:
         for retry in xrange(10):
            try:
               dut.baudRate = self.RimSendBaudCmd( PROCESS_HDA_BAUD )
               break
            except:

               objMsg.printMsg("Error in trying to talk to drive: %s" % (traceback.format_exc(),))
               DriveOff()
               dut.baudRate = DEF_BAUD
               if testSwitch.BF_0151621_231166_P_SYNC_BAUD_DIS_INIT_ESLIP_FAIL:
                  theUart.setBaud(dut.baudRate)
               DriveOn()
               if testSwitch.BF_0152393_231166_P_RE_ADD_LEGACY_ESLIP_PORT_INCR_TMO:
                  PBlock(CTRL_Z)
                  time.sleep(5)
                  PBlock(CTRL_T)
                  time.sleep(1)
                  if DEBUG:
                     objMsg.printMsg("response:\n%s" % (GChar(), ))

         else:
            #exhausted retries
            if failCommRetries:
               raise

      if comModeObj:
         if testSwitch.BF_0169635_231166_P_USE_CERT_OPER_DUT:
            if dut.certOper:
               pass#comModeObj.setMode(comModeObj.availModes.mctBase)
            else:
               comModeObj.setMode(comModeObj.availModes.sptDiag)
         else:
            comModeObj.setMode(comModeObj.availModes.sptDiag)

   def RimSendBaudCmd(self, baudRate):
      UseESlip()
      UseHardSRQ(0)
      baudList, baudRate = self.getValidRimBaudList(baudRate)
      self.eslipBaudCmd(baudSet[baudRate])
      theUart.setBaud(baudRate)
      objMsg.printMsg("Set baud passed")
      return baudRate


   def EnableInitiatorCommunication(self, comModeObj = None):
      objMsg.printMsg("Enabling initiator communications.")
      if self.mustPowerOn:
         self.RimOn()
      SPortToInitiatorSupported = SPortToInitiator(True)
      if SPortToInitiatorSupported == False:
         objMsg.printMsg("SPortToInitiatorSupported is %s" % SPortToInitiatorSupported)
         self.powerCycleRim()
         SPortToInitiator(True)
         self.RimSendBaudCmd( PROCESS_HDA_BAUD )
      else:

         baudList, baudRate = self.getValidRimBaudList(PROCESS_HDA_BAUD)
         baudList = list(baudList)
         baudList.insert(0, baudList.pop(baudList.index(baudRate)))  # Use PROCESS_HDA_BAUD

         for baseBaud in baudList:
            theUart.setBaud(baseBaud)
            try:
               #if DEBUG:
               objMsg.printMsg("Trying to comm with initiator at cellbaud %s to set to %s" % (baseBaud, baudRate))
               self.RimSendBaudCmd( baudRate )
               break
            except:
               objMsg.printMsg("Error in trying to talk to initiator: %s" % (traceback.format_exc(),))
         else:
            #We weren't able to communicate so let's try power cycle comm.
            for retry in xrange(10):
               try:
                  self.powerCycleRim()
                  SPortToInitiator(True)
                  self.RimSendBaudCmd( baudRate )
                  break
               except:
                  objMsg.printMsg("Error in trying to talk to initiator: %s" % (traceback.format_exc(),))
            else:
               #we didn't break
               raise


      if comModeObj:
         comModeObj.setMode(comModeObj.availModes.intBase)
      self.getRimCodeVer()

