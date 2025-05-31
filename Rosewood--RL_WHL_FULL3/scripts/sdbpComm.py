#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: serialScreen Module
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/sdbpComm.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/sdbpComm.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#

from Constants import *

DEBUG = 0
from Rim import objRimType
import MessageHandler as objMsg
from SLIP_transport import CslipTransport
from Cell import theCell
from Test_Switches import testSwitch
import struct, binascii, time, traceback
from Rim import objRimType
if objRimType.CPCRiser() and not testSwitch.FORCE_SERIAL_ICMD:
   from ICmdFactory import ICmd

import ScrCmds
INTERFACE_MODE = False
NEW_ESLIP_DIAG = False
DETS_DFB_ID = 7
DITS_DFB_ID = 1
UDS_DFB_ID = 6
slip = CslipTransport(512)

def resetDUTState():
   if DEBUG > 0:
      print "Reseting dut statemachine with 8*\\x20"
   if testSwitch.winFOF:
      Send(END*8)
   elif objRimType.CPCRiser() and not objRimType.CPCRiserNewSpt():
      ICmd.ESync()
   else:
      PChar(END*8)

def getCellBuffer(overrideDEBUG = False):
   if objRimType.CPCRiser() and not objRimType.CPCRiserNewSpt():
      buf = ICmd.GetBuffer(CPC_SERIAL_BUFFER, 0, 512)['DATA'] #Fixes CPC SDBP cmds
      if (DEBUG > 0 or overrideDEBUG):
         objMsg.printBin(buf)
         objMsg.printBinAscii(buf)
         ICmd.ClearSerialBuffer()

def sendNAK():
   ESLIP_NAK = END+NAK
   if testSwitch.winFOF:
      Send(ESLIP_NAK)
   elif objRimType.CPCRiser() and not objRimType.CPCRiserNewSpt():
      ICmd.SerialNoTimeout(ESLIP_NAK, 2)
   else:
      PChar(ESLIP_NAK)

class extrensicState:
   DITS_STATE = False
   DETS_STATE = False

   def setState(self,cmdType = DITS_DFB_ID):
      if cmdType == DITS_DFB_ID and self.DITS_STATE == False:
         UseESlip()
         UseHardSRQ(0)
         unlockDits()
         self.DITS_STATE = True
      elif cmdType == DETS_DFB_ID and self.DETS_STATE == False:
         UseESlip()
         UseHardSRQ(0)
         unlockDets()
         self.DETS_STATE = True
###########
## DIT/DET tracker
testServiceState = extrensicState()
###########

def unlockDits():
   data = sdbpDFB(0xffff, struct.pack('L',0x034F329A), 1, dfbIdentifier = DITS_DFB_ID, stateCmd = True, timeout = 10)

def unlockDets():
   sdbpDFB(0x1, '', 1, dfbIdentifier = DETS_DFB_ID, stateCmd = True, timeout = 10) #enable online mode requests
   sdbpDFB(0x3, '', 1, dfbIdentifier = DETS_DFB_ID, stateCmd = True, timeout = 10) #enable diagnostic mode requests

def setMultiSrqMode(Client = DETS_DFB_ID, enable = True):
   if enable:
      cmds = [0x102, 0x202]
   else:
      cmds = [0x101, 0x201]
   for enVal in cmds: #Enable srq and multi packet
      sendData = struct.pack('HH', 0,  enVal)
      SendBuffer(sendData,fromAddress=0x8001,toAddress=0x8000 + Client,checkSRQ=0,maxRetries=1)
      buf = ReceiveBuffer(fromAddress=0x8000 + Client,toAddress=0x8001,timeout=5,maxRetries=1 )#, checkSRQ=1)
      status = struct.unpack('HH', buf)[1]
      if status != 0x1003:
         objMsg.printMsg("Failed to send %X" % enVal)
         return False
   if DEBUG:
      objMsg.printMsg("Multi packet and SRQ set to %s" % enable)

   return True

def enableESLIPDiags():
   global NEW_ESLIP_DIAG

   NEW_ESLIP_DIAG = setMultiSrqMode(Client = DETS_DFB_ID, enable = True)
   NEW_ESLIP_DIAG &= setMultiSrqMode(Client = DITS_DFB_ID, enable = True)

def DitsCommand(FunctionID, data, RevID=1, timeout = 300):
   return sdbpDFB(FunctionID, data, RevID, dfbIdentifier = DITS_DFB_ID, timeout = timeout)


def DetsCommand(FunctionID, data, RevID=1, timeout = 300):
   return sdbpDFB(FunctionID, data, RevID, dfbIdentifier = DETS_DFB_ID, timeout = timeout)

def UDSCommand(FunctionID, data, RevID=1, timeout = 300):
   return sdbpDFB(FunctionID, data, RevID, dfbIdentifier = UDS_DFB_ID, timeout = timeout)

def sdbpDFB(FunctionID, data, RevID=1, dfbIdentifier = DITS_DFB_ID, stateCmd = False, timeout = 300):

   if not stateCmd:
      testServiceState.setState(dfbIdentifier)

   sdata = struct.pack("<2H",FunctionID,RevID) + data

   data = ''
   numBlocks = 0xFFFF

   state = "SEND"
   complete = False
   retry = 0
   retryLimit = 2
   sendRetries = 2
   fmt = 'HH'

   checkSRQSend = 0
   if NEW_ESLIP_DIAG:

    checkSRQReceive = 1
   else:
    checkSRQReceive = 0

   if DEBUG:
      objMsg.printMsg("checkSRQReceive %d" % checkSRQReceive)

   received = 0

   if not INTERFACE_MODE:
      UseESlip()

   while not complete:

      if state == "SEND":
         sendRetries -= 1
         retry = 0

         if sendRetries <= 0:
            raise

         if DEBUG > 0:
            objMsg.printMsg("sending %s" % repr(sdata))

         SendBuffer(sdata, checkSRQ=checkSRQSend, toAddress=dfbIdentifier, fromAddress=dfbIdentifier)

         getCellBuffer()

         state = "RECEIVE"


      elif state == "RECEIVE":

         try:

            if NEW_ESLIP_DIAG and 0:
               objMsg.printMsg("now receiving from 0x%X" % dfbIdentifier)

            if DEBUG:
               objMsg.printMsg("now waiting for response for %d seconds" % timeout)

            try:
               incrBuff = ReceiveBuffer(checkSRQ=checkSRQReceive, fromAddress=dfbIdentifier, toAddress=dfbIdentifier, timeout = timeout, maxRetries=7)
            except Exception, exInst:#FOFSerialCommError, exInst:
               exData = str(exInst)

               #could be from any provider...
               if exData.find('fromAddr: x800%d' % dfbIdentifier)> -1 or exData.find('received: (x800%d' % dfbIdentifier) > -1:

                  lastPacket = binascii.unhexlify(exData.split(':')[-1].strip())
                  lastData = lastPacket[struct.calcsize('HHL'):] # peel off the sdbp header from/to/length
                  status, sdbpPacketCode = struct.unpack(fmt, lastData[0:struct.calcsize(fmt)])


                  if sdbpPacketCode == 0x2000:   #long form not usedstruct.unpack('h', lastpacket[0:2]) == lastpackresp:
                     state = "END"#"COMPLETE_PACKET"
                     if DEBUG:
                        objMsg.printMsg("Last packet ID sent")
                     complete = True
                     break
                  else:
                     sendnak()

               else:
                  raise



            data += incrBuff

            if DEBUG > 0:
               objMsg.printMsg("received %s" % repr(data))

            if not NEW_ESLIP_DIAG:
               #print "old packet type complete"
               state = "END"
               complete = True


         except Exception, exInst:#FOFSerialCommError, exInst:

            exData = str(exInst)
            if DEBUG:
               objMsg.printMsg(traceback.format_exc())

            if retry > retryLimit:
               #raise
               resetDUTState()
               state = "SEND"

            retry += 1

            if exData.find('SHORT BUFFER') > -1:
               #bad packet.. possibly overrun data
               resetDUTState()
               sendNAK()

            elif exData.find('fromAddr: x8002')> -1:
               #invalid packet length sent
               resetDUTState()
               state = "SEND"

            elif exData.find('fromAddr: x8001')> -1:
               #drive not ready
               time.sleep(1)
               state = "SEND"

            elif 'TIMEOUT' in exData.upper() or 'SER_CHKSUM_ERR' in exData.upper() or 'SER_NO_ESLIP_FRAME' in exData.upper() or\
            'FOFSerialCommError' in traceback.format_exc():
               if DEBUG > 0:
                  objMsg.printMsg("NAK bad frame!\n'%s'" % exData)
               #resetDUTState()
               if 'SER_NO_ESLIP_FRAME' in exData.upper():
                  override = True
               else:
                  override = False

               getCellBuffer(override)

               sendNAK()

            else:
               objMsg.printMsg("Error in dfb %d command %d: %s" % (dfbIdentifier, FunctionID, exData))
               raise

   if DEBUG: objMsg.printMsg("Number of retries: %d" % retry)
   if testSwitch.virtualRun:
      data = '\x00'*80
   if dfbIdentifier == DITS_DFB_ID or dfbIdentifier == UDS_DFB_ID:
      dsb = data
      dataBlock = data[16:]
      error = extractDitsError(dsb)
   else:
      dataBlock = data[8:]
      error = struct.unpack('L',data[4:8])[0]

   if not error == 0:
      raise Exception, "Error in dfb 0x%x command 0x%x: 0x%x" % (dfbIdentifier, FunctionID, error)


   return data, error, dataBlock

def extractDitsError(dsb):
   senseKey =  (ord(dsb[1]) & 0x0F) << 24
   senseCode = (ord(dsb[2]) & 0xFF) << 16
   senseQual = (ord(dsb[3]) & 0xFF) << 8
   FRU =       (ord(dsb[11]) & 0xFF)
   return  senseKey + senseCode + senseQual + FRU

def extrBinSegment(data, segmentInfo):
   """
   Exracts data in input dict
   'name' = (start,format) of binary segment
   format is the structure def
   """
   retData = {}
   for key,val in segmentInfo.items():
      retData[key] = struct.unpack(val[1],data[val[0]:struct.calcsize(val[1]) + val[0]])
   return retData

def evalRwSense(dataBlock):
   sense = extrBinSegment(dataBlock,{'RwSenseStatus':(0,'B'),'RwSenseEC':(4,'H')})
   if not sense['RwSenseEC'][0] == 0x80:
      raise Exception, "Cmd failed for sense code %x" % sense['RwSenseEC'][0]
   return sense['RwSenseEC'][0]

