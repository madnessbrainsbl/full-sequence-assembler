#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Module containing SLIP Transport protocol class and functions
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/SLIP_transport.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/SLIP_transport.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#

from Constants import *
from time import time, sleep
import MessageHandler as objMsg
import struct
import ScrCmds
from Rim import objRimType

from SerialCls import baseComm
from Utility import timoutCallback
if objRimType.CPCRiser() and not testSwitch.FORCE_SERIAL_ICMD:
   from ICmdFactory import ICmd

DEBUG = 0

class CslipTransport(baseComm):
   def __init__(self, blockSize,protocolInPython=0):
      """
      Basic class for wrapping and transmitting serial data via SLIP (not eslip) to the dut
      """
      self.blockSize = blockSize
      self.protocolInPython = protocolInPython
      if self.protocolInPython :
         #objMsg.printMsg("XXXXXXX=%s "%str(CN))
         #FOFexecfile((CN, 'legacyProtocol.py'))
         from legacyProtocol import LegacyProtocol
         self.serObj = LegacyProtocol()

   def sendSLIPFrame(self, requestBlock, fileSize, filePtr):
      """
      Transmit a SLIP frame from a file to the dut via the serial object.
      @param requestBlock: Block number to send to dut (increments based on self.blockSize)
      @param fileSize: total fileSize to send to drive
      @param filePtr: File pointer object for reading from Needs to be open as read binary
      """
      # *Every* file has a last block called the runt block, and the runt block will be sized from 0 to (blockSize-1) (e.g. 0 to 511)
      # It is legal for the firmware to request the runt block, but no blocks beyond that.
      # If the firmware requests the runt block, we'll read a partial block from the file, and set the 'notAFullRead' flag in the response packet.
      runtBlock = (fileSize / self.blockSize)   #start from Block 0 
      runtSize = fileSize % self.blockSize

      if requestBlock < runtBlock:
         readSize = self.blockSize
         notAFullRead = chr(0)
      elif requestBlock == runtBlock:
         readSize = runtSize
         notAFullRead = chr(1)
      else:
         dstrOut = "Request for block %s is beyond than last block %s." % (requestBlock,runtBlock)
         ScrCmds.raiseException(11047,dstrOut)

      if DEBUG > 0:
         printMod = 1
      else:
         printMod = 200
      if requestBlock % printMod == 0:
         objMsg.printMsg( "Sending Block: %d of %d: Size=%d"%(requestBlock, runtBlock, readSize)) #YWL:DBG

      fileObj = filePtr
      fileObj.seek(requestBlock*self.blockSize)
      data = fileObj.read(readSize)

      if (objRimType.CPCRiser(ReportReal = True) or objRimType.isNeptuneRiser() ):
         #CPC doesn't support simple SLIP so process must construct the SLIP frame
         #  As well as synchronize the SLIP frame and send buffer.
         returnData = self.wrapSLIPFrame(data)

         self.syncFrame(10)

         size = bytesToSend = totalBlockSize = len(returnData)
         start = 0
         while bytesToSend > 0:
            block = returnData[start:start+size]
            try:
               if objRimType.CPCRiserNewSpt() or objRimType.isNeptuneRiser():
                  acc = self.PBlock(block, noTerminator = 1)  
                  if not requestBlock == runtBlock:
                     try:
                        self.waitForChar(SACK,10,accumulator = acc)
                     except:
                        pass
                  else:     
                     objMsg.printMsg("runtBlock") 

               else:
                  ret = ICmd.SerialNoTimeout( block, len(block))#, exc=1)
                  #CPC will return -1 for failure and 0 for pass
                  if ret['LLRET']:
                     objMsg.printMsg("Data sent to buffer failed... len=%s; data=%s" % (len(returnData),repr(stData),))
                     ScrCmds.raiseException(11044, "Send Frame failed: %s" % (ret,))

                  acc = self.PChar('')
                  self.waitForChar(SACK,10,accumulator = acc)
               
               start += size
               start = min(totalBlockSize, start)
               bytesToSend -= size

            except:
               size -= 1

         if DEBUG > 0:
            objMsg.printMsg("Optimal size %d" % (size,))


      else:
         res = ''
         try:
            if self.protocolInPython :
               self.serObj.SendBuffer(data)
            else :
               res = SendBuffer(data, checkSRQ=0, timeout=5)
         except:
            import traceback
            objMsg.printMsg("Exception in sendbuffer: %s" % traceback.format_exc())
            objMsg.printMsg("Binary response from drive:")
            objMsg.printBin(res)
            raise

   def rawSendFrame(self, data):
      returnData = self.wrapSLIPFrame(data)
      #self.syncFrame(10)
      if objRimType.CPCRiser() and not objRimType.CPCRiserNewSpt():
         ret = ICmd.SerialNoTimeout( returnData, len(returnData), exc=1)
         acc = self.PChar('')
      else:
         acc = self.PBlock(returnData)

      self.waitForChar(SACK,10,accumulator = acc)


   def rawReceiveFrame(self,timeout):
      tmo = timoutCallback(timeout, ScrCmds.raiseException, 11049)#, "TMO in receive frame"))
      from array import array
      block = array('c')
      done = False
      state = "AWAIT_FRAME"
      checkSum = 0
      acc = self.PChar('')
      index = -1
      theChar = ''

      for buff in acc:
         try:
            tmo()
         except:
            objMsg.printMsg("block: %s" % repr(block))
            objMsg.printMsg("state: %s" % state)
            objMsg.printMsg("buffer:%s" % repr(buff))
            objMsg.printMsg("Index: %s" % index)
            raise

         if len(buff):
            try:
               theChar = buff[index]
            except IndexError:
               index -= 1
               theChar = buff[index]

         if state == "AWAIT_FRAME":
            if theChar:
               if theChar == END:
                  state = "STRIP_ENDS"
                  index += 1
               else:
                  #through junk
                  index += 1
            else:
               sleep(0.1)
         elif state == "STRIP_ENDS":
            if theChar != END:
               state = "CHAR_IN"
            else:
               index += 1
         elif state == "CHAR_IN":
            block.append(theChar)
            checkSum += ord(theChar)
            state = "IN_FRAME"
         elif state == "IN_FRAME":
            if theChar == END:
               state = "CSUM_LO"
            else:
               state = "CHAR_IN"
         elif state == "CSUM_LO":
            csumLo = ord(theChar)
            state = "CSUM_HI"
         elif state == "CSUM_HI":
            csumHi = ord(theChar)
            state = "COMPLETE"
         elif state == "COMPLETE":
            if not checkSum == ((csumHi<<8) + csumLo):
               ScrCmds.raiseException(11087, 'Checksum mismatch on receive frame.')
            break
      return ''.join(block)

   def wrapSLIPFrame(self, data):
      """
      Wrap a SLIP frame with frame header and footer
      Frame Header (payload size)   = Size of frame payload not including checksum in 2 bytes HibyteLoByte
      Frame Footer (checksum)       = Checksum of header + payload. CheckSum = Sum of the ordinal of the binary data bytes
      """
      readSize = len(data)
      #readSize += 2 #Add checkSum Bytes for length calculation
      sizeHi = chr(((readSize) >> 8) & 0xff )
      sizeLo = chr(( (readSize) & 0xff ))

      #objMsg.printMsg("Sending %d bytes of data" % readSize)

      chckData = self.calcSLIPChksum(sizeHi + sizeLo + data)

      chckHi = chr(( chckData >> 8 ) & 0xff)
      chckLo = chr(chckData & 0xff)

      #objMsg.printMsg("Verified length of data: %d" % len(data+chckHi + chckLo))
      #objMsg.printMsg("Checksum calculated: %d" % chckData)

      return sizeHi + sizeLo + data + chckHi + chckLo


   def addSDBPHeader(self,buffer,**kwargs):
      """
      SDBP Header wrapper stolen from CM transport class
      """
      fromAddress = kwargs.get("fromAddress",2)  # default is MCT port 2.
      toAddress   = kwargs.get("toAddress",2)    # default is MCT port 2.

      # SDBP header: Two bytes 'from address', two bytes 'to address', four bytes buffer length; all LittleEndian.
      #fmt = "HHL%ds" % (len(buffer),)
      fmt = "HHH%ds" % (len(buffer),) #For DETS, boot loader

      buf = struct.pack(fmt,fromAddress,toAddress,len(buffer),buffer)

      return buf

   def waitForChar(self, c, timeout = 10, accumulator = None):
      """
      Single Char wait state to synchronize on ACK and ETX requests to dut
      @param c: Char to wait for
      @param timeout: Maximum seconds to wait before raising exception
      """
      startTime = time()
      try:
         for resp in accumulator:
            if resp.find(c) > -1 or c in resp:
               break
            else:
               if time() - startTime > timeout:
                  if len(resp) > 0:
                     objMsg.printMsg("Output data:")
                     objMsg.printBin(resp)
                     objMsg.printMsg("%s" % (repr(resp),))
                  ScrCmds.raiseException(10566, "Timeout waiting for char %d" % ord(c))
      finally:
         del accumulator

   def syncFrame(self, retries = 10):
      """
      Frame synchronization function
      Implements Protocol
      ===================
      HOST     DUT
      ====     ===
      ENQ   ->
            <- ETX
      ACK   ->
      STX   ->
            <- ACK
      """

      for x in xrange(retries):
         try:
            accumulator = self.PChar(ENQ)
            if DEBUG > 3:
               objMsg.printMsg('ENQ->')

            self.waitForChar(ETX, 10,accumulator = accumulator)
            if DEBUG > 3:
               objMsg.printMsg('<-ETX')

            accumulator = self.PChar(SACK)
            del accumulator
            if DEBUG > 3:
               objMsg.printMsg('ACK->')

            accumulator = self.PChar(STX)
            if DEBUG > 3:
               objMsg.printMsg('STX->')

            self.waitForChar(SACK,10,accumulator = accumulator)
            if DEBUG > 3:
               objMsg.printMsg('<-ACK')
         except:
            continue
         return True
      else:
         ScrCmds.raiseException(10566, "Failed to synchronize SLIP")


   def calcSLIPChksum(self, dataPtr):
      """
      Calculate the SLIP Checksum
      Algorithm
      =========
      for all bytes in data
         sum += byte_ordinal (ascii code value)
      return checksum truncated to 1 word
      """
      checksum  = 0
      for dItem in dataPtr:
         checksum += ord(dItem)

      #checksum += (recordsiz & 0xff)
      #checksum += (recordsiz >> 8)
      checksum = checksum & 0xffff

      return checksum
