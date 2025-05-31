#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Mack Interface test states (blocks) to go in here
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/SerialCls.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/SerialCls.py#1 $
# Level: 4
#---------------------------------------------------------------------------------------------------------#

from Constants import *
import sys, time,re


import MessageHandler as objMsg
from Rim import objRimType, theRim

import DesignPatterns
import ScrCmds, Utility

try:
   from cStringIO import StringIO
   CStringSupport = True
except:
   CStringSupport = False


DEBUG = 0
DEF_MAX_LOSS_BUFF = 37992
DEF_MAX_BUFFER_SIZE = 20000000 #20Mb maximum buffer size


class serialGenerator(DesignPatterns.Borg):

   def __init__(self,data, parentRef, noTerminator = 0, maxAccTime = 120):
      #initialize class variables
      self.parentRef = parentRef

      if 'activeCollection' not in vars(self):
         self.activeCollection = False

      if self.activeCollection:
         if testSwitch.virtualRun:
            objMsg.printMsg("Overlapping call")
         self.Clear()

      if CStringSupport:
         self.ibuf = StringIO()

      self.buffLen = 0

      self.timer = Utility.timoutCallback(maxAccTime, ScrCmds.raiseException, [11089, "Drive output excessive data"])

      #start the generator for the caller
      self.write(data, noTerminator)


   def write(self,data, noTerminator):
      if DEBUG > 0:
         objMsg.printMsg("sending %s" % repr(data))

      self.activeCollection = True


      if CStringSupport:
         self.parentRef.data = ''
      else:
         self.parentRef.data = []

      if noTerminator:
         PBlock("%s" % (data,))
      else:
         PBlock("%s\n" % (data,))


      if CStringSupport:
         self.getCharStreamCString()
      else:
         self.getCharStreamNonCString()


   def Clear(self):
      GChar() #consume left over chars

      self.activeCollection = False
      self.buffLen = 0

   def __del__(self):
      self.Clear()

   def getCharStreamCString(self):
      #Set up the null object
      itVal = None
      self.timer.resetTimeout()
      #while the drive is spitting out data don't release
      while itVal != '' and not self.timer(raiseError = False):
         itVal = GChar()
         self.ibuf.write(itVal) #update the buffer
         self.buffLen += len(itVal)
         if self.buffLen > DEF_MAX_BUFFER_SIZE:
            ScrCmds.raiseException(11089, "Maximum process ascii buffer size of %d reached." % DEF_MAX_BUFFER_SIZE)

   def getCharStreamNonCString(self):
      itVal = None
      self.timer.resetTimeout()
      while itVal != ''and not self.timer(raiseError = False):
         itVal = GChar()
         self.parentRef.data.append(itVal) #concat item to list...
         self.buffLen += len(itVal)
         if self.buffLen > DEF_MAX_BUFFER_SIZE:
            ScrCmds.raiseException(11089, "Maximum process ascii buffer size of %d reached." % DEF_MAX_BUFFER_SIZE)


   def __iter__(self):

      if CStringSupport:

         while 1:

            self.getCharStreamCString()
            #yield the object
            #self.parentRef.data = self.ibuf.getvalue()
            yield self.ibuf.getvalue() #Strings are immutable so lets return the actual string

      else:

         while 1:

            self.getCharStreamNonCString()
            yield ''.join(self.parentRef.data) # join list significantly faster than += on a string


class serialbaseComm:
   def __init__(self, baud = DEF_BAUD):
      self.data = ''
      self.error = 0
      self.lastCommand = ''
      if testSwitch.virtualRun:
         objMsg.printMsg("Instantiating serialbaseComm")

   def inWaiting(self):
      return 0

   def GChar(self,*args):
      ScrCmds.raiseException(11044,"Depricated function GChar use generator returned by PBlock or PChar")

   def PChar(self,*args):
      self.lastCommand = args[0]
      return serialGenerator(data = args[0],parentRef = self, noTerminator = 1)

   def PBlock(self, data , maxNoLossBuffer = DEF_MAX_LOSS_BUFF, noTerminator = 0):
      self.lastCommand = data
      return serialGenerator(data = data, parentRef = self, noTerminator = noTerminator)

   def flush(self):
      GChar()
      self.data = ''



#----------------------------------
class BaseSerial:
   """BaseSerial: base object for the Serial CPC overwrite"""

   def __init__( self, *args ):
      self.dArgs = args
      self.CtrlCharLst = {}
      self.BaudRateLst = {}
      self.DLFileType  = {}
      self.ret = None
      self.dTime = {}
      self.createCtrlCharLst()
      self.lastCommand = ''
      self.lastMethod = ''
      if testSwitch.virtualRun:
         objMsg.printMsg("Instantiating Base Serial CPC" )

   #----------------------------------
   def _timeCM2CPC( self ):
      """_timeCM2CPC: Do A Time stamp for the serial command"""
      try: prev = self.timeCurr
      except: prev = 0
      self.timeCurr = time.time()
      if prev:
         self.exeTime = self.timeCurr-prev
      return 0

   #----------------------------------
   def _exe( self, cmd='', debug=0,timed=0):
      """
      _exe: Function Evaluates a SerialCmd Captures the exception
      @type cmd: string
      @param cmd: command string to evaluate
      @type debug: integer
      @param debug: to debug onto the TraceMessage the command and results
      @type timed: integer
      @param timed: to time the command execution
      """
      if debug or DEBUG:
         debug = 1
      if timed or TIMED:
         timed = 1
      try:
         self.lastMethod =  `cmd`
         if debug:
            TraceMessage( "CPC Cmd->%s"%`cmd` )
         if timed:
            self._timeCM2CPC()
         self.ret = eval( cmd )
      except:
         self.ret= self._retError(debug)
      if debug:
         TraceMessage( "CPC Cmd Result-> %s"%`self.ret` )
      if timed:
         self._timeCM2CPC()
      if debug and timed:
         TraceMessage(  "Exe Time-> %.02f"%self.exeTime )
      return self.ret

   #----------------------------------
   def _retError( self, debug=0 ):
      """
      _retError: Return the execption value
      @type debug: integer
      @param debug: displays messages regarding the Execption
      """
      etype, evalue = sys.exc_info()[:2]
      if debug:
         TraceMessage( "Exception->%s-%s"%(etype, evalue) )
      # IO Slots expects a dictionary
      ret = {'RESULT':"Exception:%s, %s"%( etype, evalue ),'ERR':-1,'LLRET':-1, 'DATA':'' }
      # Serial slots expexts a return value
      #else: ret = ( -1, '' )
      return ret

   #--------------------------------------------------
   def createCtrlCharLst( self ):
      """
      createCtrlCharLst: Create a Ctrl Char list for comparison when a Ctrl Command is Isssued
      """
      alpha = 0x41 #='A'
      ctrlKey = 1# = CtrlA
      for cnt in range( 1, 27 ):  # from A-Z
         self.CtrlCharLst[ chr( ctrlKey) ] = alpha # { '\x01': 0x41 or 'A'.. }
         ctrlKey += 1
         alpha += 1
      return 0

class CPCSerialGenerator(DesignPatterns.Borg):
   def __init__(self, data, timeout = 5, bytes = None, baseSerialRef = None, maxNoLossBuffer = DEF_MAX_LOSS_BUFF, allowHugeBuffer = 0):
      self.baseSerialRef = baseSerialRef
      self.maxNoLossBuffer = (maxNoLossBuffer*1.05)+8
      self.timeout = timeout

      if 'activeCollection' not in vars(self):
         self.activeCollection = False

      if self.activeCollection:
         if testSwitch.virtualRun:
            objMsg.printMsg("Overlapping call")
         self.Clear()


      if maxNoLossBuffer > DEF_MAX_LOSS_BUFF:
         #Allocate a larger buffer. The buffer allows for 95% accumulation prior to reset and the latentcy is around
         #  a maximum of 8 bytes during the ISR reset so we pre-pad that amount
         #Prevent allocation > 5MB unless allowHugeBuffer is set true
         if self.maxNoLossBuffer > 5242880 and not allowHugeBuffer:
            ScrCmds.raiseException(11044,"CPC buffer allocation request to large %s" % self.maxNoLossBuffer)
         if testSwitch.BF_0155209_231166_P_FIX_SPT_ALT_BUFFER_DATA_SIZE:
            #need to divide by 512 to convert to sectors... sectors is cpc defined as nominal so 512 as no 4k support yet
            ICmd.RestorePrimaryBuffer( CPC_SERIAL_BUFFER )
            ICmd.MakeAlternateBuffer( CPC_SERIAL_BUFFER , int(self.maxNoLossBuffer/512) , exc = 1  )    # 0x04 = serial buffer
         else:
            ICmd.MakeAlternateBuffer( CPC_SERIAL_BUFFER , self.maxNoLossBuffer , exc = 1  )    # 0x04 = serial buffer

      try:
         ICmd.SerialDone(exc=1)
         self.CPCCircularBufferSupport = 1
         if DEBUG > 0:
            objMsg.printMsg("CPC Circular buffer support detected.")
      except:
         SendStop()
         self.CPCCircularBufferSupport = 0

      if self.CPCCircularBufferSupport:
         self.maxDataPacketSize = 2048
      else:
         self.maxDataPacketSize = 4096

      error = self.write(data, self.timeout, bytes)
      self.bytes = bytes
      if error:
         ScrCmds.raiseException(11044,"Invalid data to write to buffer %s;\nCPC Error: %s" % (repr(data),self.ret))

   def write( self, data, timeout, bytes ):
      self.lastCommand = data
      self.activeCollection = True

      if bytes == None:
         bytes = self.maxDataPacketSize

      self.data = ''

      if not self.CPCCircularBufferSupport:
         self.baseSerialRef._exe( "ICmd.SetSerialTimeout(%d, %d)" % (timeout*1000, timeout*1000) )
         self.baseSerialRef._exe( "ICmd.ClearSerialBuffer()" )

      if self.CPCCircularBufferSupport:
         self.ret = self.baseSerialRef._exe( "ICmd.SerialDone(exc=0)")
         self.ret = self.baseSerialRef._exe( "ICmd.SerialNoTimeout( %s)" % (repr(data),))
         if self.ret.get('LLRET',0):
            objMsg.printMsg("Repr failed on write... trying bin xfer")
            self.ret = ICmd.SerialNoTimeout( data, len(data) )
      else:
         self.ret = self.baseSerialRef._exe( "ICmd.SerialCommand( %s,'', 0, %s )" % (repr(data), bytes) )

      #Get the current bytes
      self.data = ''

      if not self.CPCCircularBufferSupport:
         self.data = self.ret.get('DATA','')
         self.baseSerialRef._exe( "ICmd.ReceiveSerialCtrl( 1 )")

      self.buffLen = 0

      self.error = self.ret.get( 'LLRET' , 0 )

      self.res = self.ret.get('CNT',-1)
      return self.error


   def Clear(self):
      if self.CPCCircularBufferSupport:
         self.baseSerialRef._exe("ICmd.SerialDone(exc=0)")
      else:
         self.baseSerialRef._exe( "ICmd.ReceiveSerialCtrl( 1 )")

      ICmd.ClearSerialBuffer()

      if self.maxNoLossBuffer > DEF_MAX_LOSS_BUFF:
         ICmd.RestorePrimaryBuffer( CPC_SERIAL_BUFFER )

      self.data = ''
      self.buffLen = 0

      self.activeCollection = False

   def __del__(self):
      self.Clear()



   #----------------------------------
   def __iter__( self, ):
      """Returns data from the UART of the CPC"""

      self.buffPtr = 0
      self.__accumulateBufferData(self.maxNoLossBuffer,self.maxDataPacketSize)
      localSerialTimer = 0

      #Loop while we're receiving data
      while 1:

         #Reset the serialtimer if it has expired... allow for 2 seconds of callback buffer
         if time.time()-localSerialTimer > (self.timeout-2) and not self.CPCCircularBufferSupport:
            self.baseSerialRef._exe( "ICmd.SetSerialTimeout(%d, %d)" % (self.timeout*1000, self.timeout*1000) )
            localSerialTimer = time.time()

         #Accumulate data at serialPort
         self.__accumulateBufferData(self.maxNoLossBuffer,self.maxDataPacketSize)

         #If we aren't in an loop until complete and we have all
         #  requested bytes then exit loop
         if not self.bytes == None and len(self.data) >= self.bytes:
            # Calling ReceiveSerialCtrl 1 will reset the serial port buffer pointer
            if self.CPCCircularBufferSupport:
               self.baseSerialRef._exe( "ICmd.SerialDone(exc=0)")
            else:
               self.baseSerialRef._exe( "ICmd.ReceiveSerialCtrl( 1 )")             # Restore the flag to store Serial Data

            self.buffPtr = 0
            if DEBUG > 0:
               objMsg.printMsg("Stopping iteration")
            raise StopIteration
         else:
            #Yield the local buffer reference for searching
            #self.baseSerialRef.data = self.data
            yield self.data


   def __accumulateBufferData(self, maxBufferSize = 78000, maxDataPacketSize = 2048):
      # Get any data accumulated since we sent the last command and end of serial timer
      try:
         if self.CPCCircularBufferSupport:
            self.ret = self.baseSerialRef._exe( "ICmd.GetSerialTail(%s)" % maxDataPacketSize)
         else:
            self.ret = self.baseSerialRef._exe(" ICmd.GetBuffer( %s,%s,%s)" % (CPC_SERIAL_BUFFER, self.buffPtr,self.buffPtr+maxDataPacketSize))

         retData = self.ret.get( 'DATA', '')

      except Exception, data:
         if DEBUG > 1:
            objMsg.printMsg("GetBuffer Error: %s" % data)
         if str(data).find("CB_EMPTY")>-1:
            retData = ''
         elif self.ret.get('CNT',-1) == 0:
            retData = ''
         else:
            raise

      if DEBUG > 1:
         objMsg.printMsg("length of cpc getbuffer %s" % len(retData))
         objMsg.printMsg("Current buffer pointer %s" % self.buffPtr)

      self.data += retData

      self.buffPtr += len(retData)

      self.buffLen += len(retData)
      if self.buffLen > DEF_MAX_BUFFER_SIZE:
         ScrCmds.raiseException(11089, "Maximum process ascii buffer size of %d reached." % DEF_MAX_BUFFER_SIZE)

      # If we've exceeded the maximum buffer size and we don't have a circular CPC buffer
      if self.buffPtr >= maxBufferSize:
         if not self.CPCCircularBufferSupport:
            self.baseSerialRef._exe( "ICmd.ReceiveSerialCtrl( 1 )")             # Restore the flag to store Serial Data

         self.buffPtr = 0

      return self.ret.get('LLRET',0)


#----------------------------------
class CPCSerialCom( BaseSerial ):
   """
   CPCSerialCom:  Serial through the CPC, which wraps the Serial Com

   *** WARNING *** You must increase maxNoLossBuffer if you wish to
      receive data larger than the default (DEF_MAX_LOSS_BUFF bytes) and have no
      data loss during the collection. <Only available when SerialNoTimeout function
      is available in CPC.

   @type baud: integer
   @param : Intial baud rate
   """
   def __init__( self, *args,**kwargs ):
      BaseSerial.__init__( self, *args )
      self.error, self.dataLen = 0,0
      self.lastCommand = ''
      try:
         self.Baud = args[0]
      except:
         self.Baud= DEF_BAUD
      self.error = 0

   #----------------------------------
   def inWaiting( self ):
      """inWaiting: oerrides the inWaiting method from the baseComm"""
      return 2048


   #----------------------------------
   def __del__(self):
      #Make sure we turn off serial accumulation
      ICmd.SerialDone(exc=0)

   #----------------------------------
   def PChar( self, data , maxNoLossBuffer = DEF_MAX_LOSS_BUFF):
      """PChar: overrides the PChar method in the baseComm"""
      return CPCSerialGenerator(data,baseSerialRef = self, maxNoLossBuffer = maxNoLossBuffer)


   #----------------------------------
   def PBlock( self, data , maxNoLossBuffer = DEF_MAX_LOSS_BUFF, noTerminator = 0):
      """PBlock: overrides the PBlock method in the baseComm"""
      if noTerminator:
         term = ''
      else:
         term = '\n'
      return CPCSerialGenerator(data+term,baseSerialRef = self, maxNoLossBuffer = maxNoLossBuffer, )


   #----------------------------------
   def GChar( self, numBytes=None , timeout = 30):
      """Returns data from the UART of the CPC"""
      ScrCmds.raiseException(11044,"Depricated function GChar use generator returned by PBlock or PChar")

   #----------------------------------
   def flush( self ):
      """Clears out the Serial buffer in the CPC"""
      self._exe( "ICmd.ClearSerialBuffer( 0x00 )" )
      return


if objRimType.CPCRiser():# and not testSwitch.virtualRun:
   if objRimType.CPCRiserNewSpt():
      bComm = serialbaseComm
   else:
      bComm = CPCSerialCom
else:
   bComm = serialbaseComm

#---------------------------------------------------------------------------
#singleton object- will be reloaded if reload is called to rebind based on cell-type: only used in VE
bc = bComm()

#---------------------------------------------------------------------------
class sptCommInterface(object):
   """
   Interface implementation for static comm class to prevent multiple comm objects
   """

   comm = bc
   lastCommand = comm.lastCommand
   def __init__(self, *args, **kwargs):
      pass

   @classmethod
   def PChar(cls, data , maxNoLossBuffer = DEF_MAX_LOSS_BUFF):
      return cls.comm.PChar(data , maxNoLossBuffer)

   @classmethod
   def PBlock(cls, data , maxNoLossBuffer = DEF_MAX_LOSS_BUFF, noTerminator = 0):
      return cls.comm.PBlock(data , maxNoLossBuffer, noTerminator = noTerminator)

   @classmethod
   def GChar(cls, numBytes=None , timeout = 30):
      return cls.comm.GChar(numBytes , timeout)

   @classmethod
   def flush(cls):
      return cls.comm.flush()



# Static interface class so baseComm can be both inherited and used as an instance w/o instantiation cost
baseComm = sptCommInterface
