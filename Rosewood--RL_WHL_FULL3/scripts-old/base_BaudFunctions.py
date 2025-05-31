#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Implements low level power handling functions
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_BaudFunctions.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_BaudFunctions.py#1 $
# Level:3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
import traceback

import time
from Cell import theCell
from Carrier import theCarrier
from Rim import objRimType, theRim
from TestParamExtractor import TP
from SerialCls import baseComm
from Exceptions import CRaiseException, BaudRateRejected, SeaSerialRequired
import sptCmds
from TestParamExtractor import TP
import RimTypes
import ScrCmds
import MessageHandler as objMsg
from Drive import objDut as dut

E0_Pad_List = [0, 1, 2, 3]
oSerial = baseComm()
global baudSeq



#------------------------------------------------------------------------------------------------------#
def basicPowerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, driveOnly=0):

   if testSwitch.BF_0169635_231166_P_USE_CERT_OPER_DUT:
      certOper = dut.certOper
   else:
      certOper = dut.nextOper in getattr(TP,'CertOperList', ['PRE2', 'CAL2', 'FNC2', 'SDAT2', 'CRT2','SPSC2'])

   offTime = getattr(TP, 'prm_PowerOffTime', {}).get('seconds', offTime)
   theCarrier.powerOffPort(offTime, driveOnly)
   theCell.setBaud()
   dut.baudRate = DEF_BAUD
   onTime = max(getattr(TP, 'prm_PowerOnTime',  {}).get('seconds', 0),  onTime)

   if driveOnly == 0 or certOper:
      if objRimType.IOInitRiser():
         #Reset the object to talk to initiator
         sptCmds.objComMode.setMode(sptCmds.objComMode.availModes.intBase)

   theCarrier.powerOnPort(set5V, set12V, onTime, driveOnly)
   if certOper:
      sptCmds.DisableInitiatorCommunication()
      theCell.setBaud(DEF_BAUD)
      time.sleep(5)



def eslipToggleRetry(setACKOff = False):
   theRim.eslipToggleRetry(setACKOff)

#------------------------------------------------------------------------------------------------------#
def eslipBaudCmd(baudString):
   # send ESLIP-SDBP command to set baud rate on drive
   return theRim.eslipBaudCmd(baudString)

   return res


#------------------------------------------------------------------------------------------------------#
def sendBaudCmd(cellBaud, inbaudRate):
   """
   Sends an SDBP baud request to the drive. Recovers to lower baud if drive rejects baud rate.
   """

   # Limit Bench process to a lower baud rate as some Hyperport boards don't support higher Bauds
   if testSwitch.winFOF and cellBaud > Baud460800:
      cellBaud = Baud460800

   # Set baud rate on Gemini
   if theCell.getBaud() != cellBaud:
      theCell.setBaud(cellBaud)

   baudList, baudRate = theRim.getValidRimBaudList(inbaudRate)
   if inbaudRate != baudRate:
      objMsg.printMsg("Cell doesn't support %s changing baud request to %s" % (inbaudRate, baudRate))
   baudList = list(baudList)
   baudIndex = baudList.index(baudRate)

   objMsg.printMsg("Set BaudRate on Drive to %s" % baudRate)
   if theCell.eslipMode != 1:
      theCell.enableESlip(True)
   if theCell.eslipMode == 1:
      # send ESLIP-SDBP command to set baud rate on drive
      #theCell.enableESlip(False)
      while baudIndex > -1:
         try:
            baudRate = baudList[baudIndex]
            baudString = baudSet[baudRate]
            res = eslipBaudCmd(baudString)
            break
         except BaudRateRejected:
            #if baud rate was rejected try a lower baud
            baudIndex -= 1
         except:
            if testSwitch.FE_0112289_231166_REMOVE_INEFFICIENT_RETRIES_IN_ESLIP_BAUD_RETRIES:
               raise
            else:
               #see if drive is really at the baud and just didn't respond to the 1st packet
               try:
                  time.sleep(0.5)
                  theCell.setBaud(baudRate)
                  res = eslipBaudCmd(baudString)
                  break
               except:
                  #If not then reset the cell baud
                  theCell.setBaud(cellBaud)
                  raise
      else:
         raise

      objMsg.printMsg("Eslip communication established at %s" % baudRate)
   else:
      # we don't have non-ESLIP drives for platform at this stage
      # once we get such drives, use appropriate commands to set baud rate on drive
      msg = "NON ESLIP sendBaudCmd Issued"
      objMsg.printMsg('%s\n%s' % (msg, traceback.format_exc()))
      ScrCmds.raiseException(11044, msg)

   # now we update the baud rate on cell/CPC to match the drive baud rate since drive baud was changed
   #TraceMessage("Update Cell/CPC BaudRate to match Drive Baud Rate of %s" % baudRate)
   theCell.setBaud(baudRate) # Update baud rate on Gemini

def asciiDebugESLIP_AnyCellBaudRetry(cellBaud, inbaudRate):
   if (testSwitch.winFOF or testSwitch.virtualRun):
      return

   objMsg.printMsg("Attempting ASCII Debug ESLIP recovery- anybaud.")

   baudList, baudRate = theRim.getValidRimBaudList(inbaudRate)
   baudList = list(baudList)
   #try the existing baud first
   baudList.insert(0, cellBaud)


   for baud in baudList:
      # Set baud rate on Gemini
      theCell.setBaud(baud)

      #Disable APM
      sptCmds.disableAPM()

      #Wait for APM to be off... this should be <1sec
      time.sleep(0.5)

      printResult = True

      try:
         #Initiate DIAG Mode- this has a higher priority in FW task handling than SDBP packets
         sptCmds.sendDiagCmd(CTRL_Z, timeout = 2, altPattern = 'S?F3+[\s_]*(?P<LEVEL>[\dA-Za-z])>',maxRetries = 3, Ptype='PChar', raiseException = True, printResult = printResult)
         break
      except SeaSerialRequired:
         raise
      except:
         objMsg.printMsg("Unable to perform ascii online abort.\n%s" % (traceback.format_exc(), ))

   else:
      ScrCmds.raiseException(10340, "Unable to perform ascii online abort.")

   #EnableEslip will send CTRL-T to enable the eslip mode out of diag mode
   sptCmds.enableESLIP( retries = 10, timeout = 10, printResult = printResult, raiseException=True, suppressExitErrorDump = True)

   time.sleep(5)                    # Wait 5 seconds for resource state restoration
   sendBaudCmd(baud, baudRate)      # Now change the baud


def asciiDebugESLIPRetry(cellBaud, baudRate):
   if (testSwitch.winFOF or testSwitch.virtualRun):
      return

   objMsg.printMsg("Attempting ASCII Debug ESLIP recovery.")

   if testSwitch.BF_0123402_231166_SET_CELL_BAUD_BEF_ASCII_DBG:
      # Set baud rate on Gemini
      theCell.setBaud(cellBaud)


   #Disable APM
   sptCmds.disableAPM()

   #Wait for APM to be off... this should be <1sec
   time.sleep(0.5)

   if DEBUG and testSwitch.FE_0112289_231166_REMOVE_INEFFICIENT_RETRIES_IN_ESLIP_BAUD_RETRIES:
      printResult = True
   else:
      printResult = False

   try:
      #Initiate DIAG Mode- this has a higher priority in FW task handling than SDBP packets
      if not dut.IsSDI:
         sptCmds.sendDiagCmd(CTRL_Z, timeout = 10, altPattern = 'S?F3+[\s_]*(?P<LEVEL>[\dA-Za-z])>',maxRetries = 3, Ptype='PChar', raiseException = True, printResult = printResult)
   except SeaSerialRequired:
      raise
   except:
      ScrCmds.raiseException(10340, "Unable to perform ascii online abort.")


   sptCmds.enableESLIP( retries = 10, timeout = 10, printResult = printResult, raiseException=True, suppressExitErrorDump = True)

   time.sleep(5)                          # Wait 5 seconds for resource state restoration
   sendBaudCmd(cellBaud, baudRate)        # Now change the baud

#------------------------------------------------------------------------------------------------------#
def detectBootRomPrompt(*args, **kwargs):
   objMsg.printMsg("Detecting boot prompt.")
   bpDetected = False
   accum = oSerial.PChar('?')
   time.sleep(.5)
   retry = 0
   for res in accum:

      if res.find('Boot Cmds:') > -1 or res.find('Bad cmd:') > -1:
         objMsg.printMsg("Boot Prompt detected... bypassing eslip communication.")
         bpDetected = True
         break
      else:
         objMsg.printMsg("Data at SPT: %s" % res)
      time.sleep(.5)
      if retry > 1:
         bpDetected = False
         break
      retry += 1

   if bpDetected:
      ScrCmds.raiseException(10340, "Seaserial required", SeaSerialRequired)
   else:
      ScrCmds.raiseException(10340, "Unable to detect boot prompt.")

if testSwitch.FE_0122298_231166_ASCII_DEBUG_FIRST_BAUD_CMD:
   baudSeq = [asciiDebugESLIPRetry, sendBaudCmd, asciiDebugESLIP_AnyCellBaudRetry, detectBootRomPrompt]
else:
   baudSeq = [sendBaudCmd, asciiDebugESLIPRetry, asciiDebugESLIP_AnyCellBaudRetry, detectBootRomPrompt]

#------------------------------------------------------------------------------------------------------#
def changeBaud(baudRate=PROCESS_HDA_BAUD):
   """
   Desc: New function for setting baud rate for eSlip.  Must be called after every PowerOn.
          NOTE:  CANNOT CALL BACK TO BACK PowerOn's must have PowerOff in between or BaudRate will fail in eslip mode.
   """
   global baudSeq
   objMsg.printMsg("Target Baud Rate: %s" % baudRate)

   retries = 4
   seaSerialRequired = False


   # since we do not know the initial baud rate of the cell/CPC we loop through possible cell/CPC baudrates
   #for baud in cellBaudList:
   #
   cellBaud = dut.baudRate


   #Try the asciiDebug ESLIP retry
   for cnter in xrange(len(baudSeq)):
      func = baudSeq[0]

      try:
         if testSwitch.FE_0139319_336764_P_DELAY_BEFORE_SET_BAUDRATE_FOR_SATA_ON_SAS_SLOT and riserType in RimTypes.intfTypeMatrix['SAS']['riserTypeMatrix']['SerialOnlyList']:
            time.sleep(5)
         func(cellBaud, baudRate)
         dut.baudRate = baudRate
         break
      except SeaSerialRequired:
         raise
      except:
         objMsg.printMsg(traceback.format_exc())
         objMsg.printMsg('Exception occured on changeBaud (ReqBaud: %s, CellBaud: %s)' % (baudRate, cellBaud))
         baudSeq.append(baudSeq.pop(0)) #Move unsuccessful item to the end
         if testSwitch.FE_SGP_402984_POWER_CYCLE_ON_UNSUCCESSFUL_CHANGE_BAUD:
            objMsg.printMsg("Trying to power cycle drive to correct change baud failures.")
            DriveOff(10)
            dut.baudRate = DEF_BAUD
            DriveOn(pauseTime=10)
   else:
      raise
#------------------------------------------------------------------------------------------------------#
def changeBaud_once(baudRate=PROCESS_HDA_BAUD):
   """
   Desc: New function for setting baud rate for eSlip.  Must be called after every PowerOn.
          NOTE:  CANNOT CALL BACK TO BACK PowerOn's must have PowerOff in between or BaudRate will fail in eslip mode.
   """
   global baudSeq
   objMsg.printMsg("Target Baud Rate: %s" % baudRate)

   retries = 4
   seaSerialRequired = False

   # since we do not know the initial baud rate of the cell/CPC we loop through possible cell/CPC baudrates
   #for baud in cellBaudList:
   #
   cellBaud = dut.baudRate

   #Try the asciiDebug ESLIP retry
   for cnter in xrange(len(baudSeq)):
      func = baudSeq[0]

      try:
         if testSwitch.FE_0139319_336764_P_DELAY_BEFORE_SET_BAUDRATE_FOR_SATA_ON_SAS_SLOT and riserType in RimTypes.intfTypeMatrix['SAS']['riserTypeMatrix']['SerialOnlyList']:
            time.sleep(5)
         func(cellBaud, baudRate)
         dut.baudRate = baudRate
         break
      except SeaSerialRequired:
         raise
      except:
         objMsg.printMsg(traceback.format_exc())
         objMsg.printMsg('Exception occured on changeBaud (ReqBaud: %s, CellBaud: %s) Raised' % (baudRate, cellBaud))
         #baudSeq.append(baudSeq.pop(0)) #Move unsuccessful item to the end
         raise

   else:
      raise