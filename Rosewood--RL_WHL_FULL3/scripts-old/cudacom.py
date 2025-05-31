
import sys
import binascii
import struct
import time
import os
import stat
import types
import math
import traceback

from os.path import join
from math import log10, pow

print "===================================================================="
print "$Workfile:   cudacom.py  $",
print "$Revision: #1 $",
print "$Date: 2016/09/20 $"
print "===================================================================="
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/09/20 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
#      $Author: chiliang.woo $

###################################################################################################
#  Cudacom Globals
###################################################################################################
# File messages
READ_FILE = chr(81)

DEBUG = 0
FileLength = 0
FileObj = 0
dblData = {}
"""
Global file length and file object vars
"""
gHead = 0
gZone = 0
gCylinder = 0
gPhysicalTrack = 0
"""
Global location values for cudacom. These are set by seeks only.
"""

print "\nCudacom globals gHead, gCylinder, and gZone are cleared on a load or reload of cudacom."
print "A seek must be performed to set these variables."
pcFileLocation = r"C:\var\merlin\pcfiles"

"""
Global macro definitions
"""
AGERE = 0
MARVELL = 1

REQUEST_CURRENT_DATE = 31

FAIL_RESP = '\x00\x00\x00'

SocSelected = 0;

###################################################################################################
#  Cudacom Private Functions
###################################################################################################
def fn(*args,**kwargs):
    import struct, binascii
    # Send and MCT function block.
    # If there's no function number then we have nothing to do.
    if DEBUG:
       print "args: %s" % (args,)
       print "kwargs: %s" % (kwargs,)
    if not args: return

    timeout = kwargs.pop('timeout',90000)
    receive = kwargs.pop('receive',1)

    # There should be one function number and up to ten parameters.
    if len(args) > 11: raise "Too many arguments to fn()."

    # Prefix is a code '7', and a BigEndian function number.
    fmt = ">BH"
    prefix = struct.pack(fmt,7,args[0])

    # Pad up to 10 parms with zeroes.
    parms = args[1:]
    parms = parms + (10-len(parms))*(0,)

    # Build the complete command string, prefix plus parms.
    fmt = ">%ds%dH" % (len(prefix),len(parms),)
    TxBuffer = struct.pack(fmt,prefix,*parms)

    if DEBUG:
      print "Tx Buffer = %s"%binascii.hexlify(TxBuffer)

    # Send the function request block.
    ret = SendBuffer(TxBuffer,checkSRQ=0,**kwargs)
    if DEBUG:
       if not ret == None:
         print "Rx from Tx = %s" % binascii.hexlify(ret)

    if receive:
       if DEBUG:
         print "Internal receive"
       buf, ec = __ReceiveResults(timeout = timeout)

       if __isOverlayRequest(buf):
          while __isOverlayRequest(buf):
             if DEBUG:
                print "OverlayRequest"
             processRequest70(buf)
             buf, ec = __ReceiveResults(timeout = timeout)


    return buf, ec
    # Now the caller must collect any response that the drive might send.
if not 'processRequest70' in locals():
   def processRequest70(requestData, *args, **kargs):
     # requestData is a string from the UUT asking for a block from a file
     # return a frame, raise an exception on error
     global OvFileName

     if not OvFileName:
      msg = "Drive requests file data from overlay but there is no file registered as overlay."
      raise FOFFileIsMissing,msg

     if not os.path.isfile(OvFileName):
       msg = "Missing File: %s" % OvFileName
       raise FOFFileIsMissing,msg
     requestKey = ord(requestData[0])
     # code 6 typically requests a block of data from the download file;  get_data_file()
     if requestKey == 70:
       blockSize = (int(ord(requestData[3]))<<8) + int(ord(requestData[2]))
       requestHI = requestData[5]
       requestLO = requestData[4]
       requestBlock = (int(ord(requestHI))<<8) + int(ord(requestLO))
     else:
       str = "Unsupported requestKey in processRequest70==>",requestKey
       raise Exception,str

     if requestBlock == 1:
        print "Overlay Request handled-> %s" % OvFileName
     # look up the file size, and validate the block request
     fileSize = os.stat(OvFileName)[stat.ST_SIZE]

     # *Every* file has a last block called the runt block, and the runt block will be sized from 0 to (blockSize-1) (e.g. 0 to 511)
     # It is legal for the firmware to request the runt block, but no blocks beyond that.
     # If the firmware requests the runt block, we'll read a partial block from the file, and set the 'notAFullRead' flag in the response packet.
     runtBlock = fileSize / blockSize
     runtSize = fileSize % blockSize

     #print "Sending Block: %d of %d"%(requestBlock+1, runtBlock) #YWL:DBG

     if requestBlock < runtBlock:
       readSize = blockSize
       notAFullRead = chr(0)
     elif requestBlock == runtBlock:
       readSize = runtSize
       notAFullRead = chr(1)
     else:
       str = "processRequest70(): Request for block %s is beyond than last block %s." % (requestBlock,runtBlock)
       print str
       raise FOFParameterError,str

     # read from their file
     fileObj = open(OvFileName,"rb")
     if DEBUG:
        print "Overlay request block %d" % requestBlock
     fileObj.seek(requestBlock*blockSize)
     data = fileObj.read(readSize)
     fileObj.close()

     returnData = requestData[0] + notAFullRead + requestLO + requestHI + data

     SendBuffer(returnData)

if not 'RegisterOvCall' in locals():
   def SetOVLFile(ovlTuple):
      import os, types
      global OvFileName
      #UserDownloadPath = r'C:\var\merlin\dlfiles'

      if type(ovlTuple) in [types.TupleType,types.ListType] and len(ovlTuple) > 1:
         subDir = ovlTuple[0]
         fname = ovlTuple[1]
         if subDir == '':
            OvFileName = os.path.join(UserDownloadsPath,fname)
         else:
            OvFileName = os.path.join(UserDownloadsPath,subDir,fname)
      else:
         OvFileName = ovlTuple


      if not os.path.isfile(OvFileName):
           msg = "Missing File: %s" % OvFileName
           print msg
           raise FOFFileIsMissing,msg

      # intercept request key 16 from core code
      RegisterResultsCallback(processRequest70, 70, 0)

   def RegisterOvCall(fileName=None):
      global OvFileName

      if fileName:
        OvFileName = fileName
      if not os.path.isfile(OvFileName):
        msg = "Missing File: %s" % OvFileName
        print msg
        raise FOFFileIsMissing,msg

      # intercept request key 16 from core code
      RegisterResultsCallback(processRequest70, 70, 0)


def __displayBuffer(buf):
  """
  Print a binary string buffer to the string in "pretty" format- bit seperated hex
  """
  try:
    data = binascii.hexlify(buf)
    i1=0
    cnt=0
    print "   ",
    for i2 in range(2,len(data),2):
      print data[i1:i2],
      i1=i2
      cnt+=1
      if cnt == 8 or cnt == 16 or cnt == 24:
        print "  ",
      if cnt == 32:
        cnt=0
        print "\n   ",
    print data[i1:]
  except:
    pass
    #print("Print Failed %s" % str(data))
####################################################################

def __displayMemory(buf, baseAddr=0, addressableUnit=1, unitsPerLine=16, groupSize=4, startingByte=0, forceLen=0):
  """
  Print a binary string buffer to the string in a "memory dump" format::
      address     hex data for 0..(N-1)
      address+N   hex data for N..(2N-1)
      address+2N  hex data for 2n..(3N-1)
      etc.
  @param buf:               Buffer to display
  @param baseAddr:          Base address to display
  @param addressableUnit:   Number of bytes per Address value
  @param unitsPerLine:      Number of address values displayed per line
  @param groupSize:         Number of addressable units to display per grouping
  @param startingByte:      Starting byte of data to display
  @param forceLen:          Total Number of bytes to display (overwrites natural length of the input data)
  """
  data = binascii.hexlify(buf)
  forceLen *= 2             # convert to ASCII (2 memory bytes per ascii character)
  startingByte *= 2
  bytesToDisplay = len(data) - startingByte

  # Overwirte the natural data length, if requested
  if forceLen > 0 and forceLen < bytesToDisplay:
    bytesToDisplay = forceLen

  cnt=0
  print "Address   Data\n",
  # Convert addressableUnit from bytes to nibbles
  addressableUnit*=2
  print '%08x ' % baseAddr,
  for i2 in range(startingByte,startingByte+bytesToDisplay,addressableUnit):
    print data[i2:i2+addressableUnit],
    cnt+=1
    if cnt % groupSize == 0:
      print " ",
    if cnt == unitsPerLine and i2 < (startingByte + bytesToDisplay) - addressableUnit:
      cnt=0
      print "\n",
      baseAddr += unitsPerLine
      print '%08x ' % baseAddr,
  print ''
####################################################################

def displayVisMux(buf):
  """
  Display the contents of the visibility mux buffer passed.
  Buffer Contents::
      byte 0..7   Select Registers 0..7
      byte 8-9    Enable Register
  """
  result = struct.unpack('BBBBBBBBH', buf)

  print "Sel[0] = 0x%x" % result[0]
  print "Sel[1] = 0x%x" % result[1]
  print "Sel[2] = 0x%x" % result[2]
  print "Sel[3] = 0x%x" % result[3]
  print "Sel[4] = 0x%x" % result[4]
  print "Sel[5] = 0x%x" % result[5]
  print "Sel[6] = 0x%x" % result[6]
  print "Sel[7] = 0x%x" % result[7]
  print "Enable = %x" % result[8]
####################################################################

def __isCompletionPacket(buf):
  """
  Check to see if the packet passed is the completion packet.
  Completion packet is 0xbeefcafe followed by the 2 byte error code.
  Return 1 if packet is a completion packet, 0 otherwise.
  """
  if (len(buf) == 6):
    if buf[0] == '\xbe':
      if buf[1] == '\xef':
        if buf[2] == '\xca':
          if buf[3] == '\xfe':
            return 1
  return 0
####################################################################


def __isOverlayRequest(buf):
   if buf[0:3] == '\x46\x00\x00':
      return True
   else:
      return False

def __ReceiveResults(timeout=90000,displayError=1):
  """
  Get the result (of a preceeding fn call) from the serial port.
  Optionally pass a timeout value (default = 5 seconds)
  Optionally pass displayError=0 to supress displaying a nonzero error code.
  Returns a tuple (<result data>, <error code>)
  """
  global OverlayTuple
  bfrList = []
  finalPacket = 0
  while finalPacket == 0:
    try:
      buf = ReceiveBuffer(timeout=timeout,maxRetries=1) #fromAddress=0x8001,toAddress=0x8001,checkSRQ=2,
      #buf = ReceiveBuffer(timeout)
      if DEBUG:
         print "Receive buffer"
         __displayBuffer(buf)

      if __isOverlayRequest(buf):
         return buf,0
      if __isCompletionPacket(buf) == 1:
        finalPacket = 1
        result = struct.unpack(">H",buf[4:6])
        errorCode  = result[0]
        if errorCode != 0 and displayError == 1:
          print "Error code %d reported" % errorCode
        break
      else:
        bfrList.append(buf)
    except:
      print "Receive Buffer error, no response"
      return ''.join(bfrList), 0xFFFF
  return ''.join(bfrList), errorCode
####################################################################

def __dbg(msg):
  """
  Print Stub
  @param msg: String input to print to stdout
  """
  print msg
####################################################################

def __bytes(the_word):
  """
  @return: tuple of bytes from a word
  """
  return ((the_word>>8)&0xFF,the_word&0xFF)
####################################################################

def __lbytes(the_lword):
  """
  @return: tuple of bytes from long/double word
  """
  return ((the_lword>>24)&0xFF,(the_lword>>16)&0xFF,(the_lword>>8)&0xFF,the_lword&0xFF)
####################################################################

def __lwords(the_lword):
  """
  @return: tuple of words from long/double word
  """
  return (((the_lword>>16)&0xFFFF),the_lword&0xFFFF)
####################################################################

def __llwords(the_llword):
  """
  @return: tuple of words from long long word (64-bits)
  """
  Bits32To63 = (the_llword & 0xffffffff00000000) >> 32
  Bits31To0  = the_llword & 0x00000000ffffffff
  msll, lsll = __lwords(Bits32To63)
  msl, lsl = __lwords(Bits31To0)
  return (msll, lsll, msl, lsl)

####################################################################


####################################################################
# Change Baud Rates
# (via SetESlipXxBaud functions, do not use fn)
####################################################################
def ESlipHiBaud():
   """
   Set the drive and host to Hi Baud (390K)
   """
   SetESlipHiBaud()

def ESlipMidBaud():
   """
   Set the drive and host to Mid Baud ( 115.2K )
   """
   SetESlipMidBaud()

def ESlipLoBaud():
   """
   Set the drive and host to Mid Baud ( 38.4K )
   """
   SetESlipLoBaud()
####################################################################

###################################################################################################
#  Cudacom Public Commands
###################################################################################################
# Note: if unsure of how to correctly display ePyDoc documentation, please see go to the following
#       link:  http://epydoc.sourceforge.net/epytext.html
###################################################################################################

def ledon():
  """
  Turn on PCBA LED
  @return: Error code
  """
  buf, errorCode = fn(1201)
  #buf, errorCode = __ReceiveResults()
  return errorCode
####################################################################

def ledoff():
  """
  Turn off PCBA LED
  @return: Error code
  """
  buf, errorCode = fn(1200)
  #buf, errorCode = __ReceiveResults()
  return errorCode
####################################################################
################## Charlie to return tracknow ##################################################

def getActiveTrackk(quietMode = 0):
  """
  Get Active Track. Display current cylinder and head.
  @return: Error code
  """
  global gHead
  global gCylinder
  global gZone
  global gPhysicalTrack
  global tracknow

  buf, errorCode = fn(1362)
  result = struct.unpack(">LB",buf)
  tracknow = result[0]
  if quietMode == 0:
    print "Firmware Globals: Cylinder: %u " % result[0] + " Head: %u " % (result[1])
    print "Cudacom globals:  head %u " % gHead + "zone %u" % gZone  + " cylinder %u " % gCylinder + "physical cylinder %u" % gPhysicalTrack
  #return errorCode
  return tracknow
###############################################################
def setActiveTrack(cylinder, head, quietMode = 0):
  """
  Set Active Logical Track (cylinder and head) for CudaCom commands -
  twrite, tread, writetrack, readtrack, fz, DCEraseTrack, ber, ser
  @param cylinder: Cylinder of Active Track
  @param head: Head of Active Track
  @return: Error code
  """
  mCylinder, lCylinder = __lwords(cylinder)
  buf, errorCode = fn(1357, lCylinder, mCylinder, head)
  if quietMode == 0:
    print "Note: Cudacom global cylinder, head, and track are only set by seek commands"
  return getActiveTrack(quietMode)
####################################################################

def getActiveTrack(quietMode = 0):
  """
  Get Active Track. Display current cylinder and head.
  @return: Error code
  """
  global gHead
  global gCylinder
  global gZone
  global gPhysicalTrack

  buf, errorCode = fn(1362)
  result = struct.unpack(">LB",buf)
  if quietMode == 0:
    print "Firmware Globals: Cylinder: %u " % result[0] + " Head: %u " % (result[1])
    print "Cudacom globals:  head %u " % gHead + "zone %u" % gZone  + " cylinder %u " % gCylinder + "physical cylinder %u" % gPhysicalTrack
  return errorCode

#####################################################################

def sram(startAddress, byteData="", writeFlag=0):
  """
  Read/Write to RAM
  @param startAddress: Address to begin read/write operations
  @param byteData: Iterable containing byte data
  @param writeFlag: Set to enable write mode
                    If zero or not present, read 64 bytes
  @return: Error code
  """
  if writeFlag == 1:             ## Write RAM
    numBytes=len(byteData)
    if type(startAddress) != type(1):
      print "Error: Address should be a integer\n"
      return

    if type(byteData) != type("\x00"): ###
      print "Error: data should be an array\n"
      return

    print "Writing %d bytes at address %x \n"%(numBytes, startAddress,)
    buf, errorCode = fn(1290, 1, startAddress&0xffff, startAddress>>16, numBytes)
    SendBuffer(byteData)
    __ReceiveResults(20)

  ## Read 64 bytes at the address
  ## (for writes, echo back 64 bytes, starting at the address writen)
  if type(startAddress) != type(1):
    print "Error: Address should be a integer\n"
    return

  buf, errorCode = fn(1290, 0, startAddress&0xffff,startAddress>>16 , 64, timeout = 20)
  #buf, errorCode = __ReceiveResults(20)
  __displayMemory(buf,startAddress)
  return errorCode

#####################################################################

def reg(address, size = 16, writeFlag = 0, data = 0):
  """
  Read or write to memory mapped registers
  @param address: Address to read or write
  @param data: Data to write
  @param size: Size in bits of the controller register, 8, 16, and 32 are valid entries
  @param writeFlag: Set to enable write mode, defaults to zero for read mode
  @return: Error code
  """
  global SocSelected

  if size != 8 and size != 16 and size != 32:
      print "Invalid size parameter"
      print size
      return 0
  lswData = data
  mswData = 0
  if size == 32:
      mswData, lswData = __lwords(data)
  mswAddress, lswAddress = __lwords(address)
  buf, errorCode = fn(1216, lswAddress, mswAddress, size, writeFlag, lswData, mswData)
  
  if SocSelected !=0 :
     print "SoC", SocSelected, "->"

  #buf, errorCode = __ReceiveResults()
  if size == 8:
      result = struct.unpack("BBBB",buf)
  if size == 16:
      result = struct.unpack("HH",buf)
  if size == 32:
      result = struct.unpack("L",buf)
  print "Hex: %x  " % result[0:1] + "Dec: %d" % result[0:1]
  data = result[0:1]
  return int(data[0])

####################################################################

def svram(svAddrIndex, offset = 0, size = 16, addressMode = "INDIRECT", wrFlag = "READ", wData = 0):
  """
  Read/Write Servo RAM
  @param svAddrIndex: Index into array of servo RAM addresses to begin read/write operations
                      or high half of 32-bit address if addressMode == "PASS"
  @param offset: Offset into table from beginning address times length (ie addr+0, addr+2 etc. for word length)
                 or low half of 32-bit address if addressMode == "PASS"
  @param size: Operation length: 8 (byte), 16 (default word), or 32 (long word)
  @param addressMode: Address servo RAM via read_servo_ram (INDIRECT) or directly through the variable name
                      or "PASS": 32-bit address pass through(address = svAddrIndex<<16 + offset) 
  @param wrFlag: Set to anything besides "READ" to enable write mode
  @param wData: Data to write when in write mode
  @return: Binary response from drive
  """

  if size != 8 and size != 16 and size != 32:
      print "Invalid size parameter"
      print size
      return 0
  writeFlag = 0     # Default to read
  addrMode = 0      # Default to INDIRECT mode (read_servo_ram)

  if addressMode.upper() == "PASS":
      addrMode = 2
  else:
      if addressMode != "INDIRECT":
          addrMode = 1  # Address the servo var directly
          if wrFlag != "READ":
              print "Cannot use direct mode with writes"
              return 0

  if wrFlag == "WRITE":
      writeFlag = 1 # Write servo RAM
      if size == 32:
         msData, lsData = __lwords(wData)
         buf, errorCode = fn(1291, svAddrIndex, offset, size, addrMode, writeFlag, lsData, msData)
      else:
         buf, errorCode = fn(1291, svAddrIndex, offset, size, addrMode, writeFlag, wData)
      #buf, errorCode = __ReceiveResults()

  # Read the data (echo if write cmd)
  buf, errorCode = fn(1291, svAddrIndex, offset, size, addrMode, 0, wData)
  #buf, errorCode = __ReceiveResults()
  if size == 8:
      result = struct.unpack("BBBB",buf)
  if size == 16:
      result = struct.unpack("HH",buf)
  if size == 32:
      result = struct.unpack("L",buf)
  print "Hex: %x  " % result[0:1] + "Dec: %d" % result[0:1]
  data = result[0:1]
  return int(data[0])
####################################################################

def dram(section=0, address=0):
  """
  Read buffer memory
  @param section: Selects a base address defined within SFT Firmware.
                  Section 0 is the dummy cache and most common location.
                  Data from tread or ssar command is placed in the dummy cache base.
  @param address: Address within section to read
  @return: Error code
  """

  if type(section) != type(1) or section < 0 or section > 11:
    print "dram usage: dram(section, address)"
    print "section should be between 0 and 11"
    return

  mword, lword = __lwords(address)
  buf, errorCode = fn(1288, 0, section, lword, mword, 512)
  #buf, errorCode = __ReceiveResults()
  __displayMemory(buf,address)
  return errorCode
####################################################################

def dset(section=0, offset=0, pattern=0xC6, count=32):
  """
  Write buffer memory
  @param section: Selects a base address defined within SFT Firmware. Section 0 is the dummy cache and most common location.  Data from
                 a read command is placed in the dummy cache base.
  @param offset: Offset from base.
  @param pattern: Pattern to write to the buffer
  @param count: Number of bytes to write.
  @return: Error code
  """

  if type(section) != type(1) or section < 0 or section > 11:
    print "dset usage: dset(section, offset, pattern, byte_count)"
    print "section should be between 0 and 11"
    return

  mOffset, lOffset = __lwords(offset)
  mBytes,  lBytes  = __lwords(count)

  buf, errorCode = fn(1286, section, lOffset, mOffset, pattern, lBytes, mBytes)
  #buf, errorCode = __ReceiveResults()
  return errorCode
####################################################################

def ofs(offset=0):
  """
  Set servo offset on current servo tracking position
  @param offset: Servo offset in dac counts [-127,127]
  @return: Error code
  """
  global SocSelected

  if type(offset) != type(1):
     print "ofs usage: ofs(offset)"
     print "Offset between -127 and 127"
     return

  buf, errorCode = fn(1211, offset)

  if SocSelected != 0:
     print "SoC", SocSelected, "->"
  #buf, errorCode = __ReceiveResults()
  return errorCode
####################################################################

def esk( cyl, head, seektype, displayOptions):
  """
  Generic embedded seek command. Display status and sense code from
  drive. Set cudacom globals (gHead, gCylinder, gZone) upon completion.
  @param cyl: Target cylinder
  @param head: Target head
  @param seektype: Read/Write/Format/Read Physical/WritePhysical = ['r','w','f','p','s']
  @param seekWithHeat:  If the Drive allows it will allow seeking with heat
                        0: Default Behavior
                        1: Seek with heat, leave heat on
                        2: Directly Pass RWOptions
  @return: Error code
  """
  global gHead
  global gCylinder
  global gZone
  global gPhysicalTrack

  if type(cyl) != type(1) or type(head) != type(1) or  \
    type(seektype) != type("") or seektype not in ['r', 'w', 'f', 'p', 's']:
     print "esk usage: esk(cylinder, head, seektype(= 'r'|'w'|'f'|'p'|'s'))\n"
     return

  dir = {'r': 0x15, # Read Seek Data Tracks
         'w': 0x25, # Write Seek Data Tracks
         'f': 0x05, # Format Seek Data Tracks
         'p': 0x18, # Read Seek Servo Tracks
         's': 0x28  # Write Seek Servo Tracks
        }
  mode = dir.get(seektype,0x15)
  mCylinder, lCylinder = __lwords(cyl)
  buf, errorCode = fn(1243, lCylinder, mCylinder, head, mode)
  #buf, errorCode = __ReceiveResults()

  
  # Note: result[1:2] is unused (leftover pad for quad alignment)
  if len(buf) > 8:
     result = struct.unpack("HHLHHL",buf)
  else:
     result = struct.unpack("HHL",buf)
     
  
  print "result[]=", result
  status = result[0:1]
  if status[0] == 0:
      sts = 'pass with retry'
  if status[0] == 1:
      sts = 'pass'
  if status[0] == 2:
      sts = 'fail'
  print "Seek Sense: %x " % (result[2:3])
  if sts != 'pass':
      print "Seek Status: %s" % (sts)

  if len(buf) > 8:
    status = result[3:4]
    print "reader 2:"
    if status[0] == 0:
        sts = 'pass with retry'
    if status[0] == 1:
        sts = 'pass'
    if status[0] == 2:
        sts = 'fail'
    print "Seek Sense: %x " % (result[5:6])
    if sts != 'pass':
      print "Seek Status: %s" % (sts)

  # Set cudacom globals
  gHead = head
  gCylinder = cyl
  if seektype == 'p' or seektype == 's':
      gCylinder = ConvertPhysToLog(cyl, head, 1)
      gPhysicalTrack = cyl
      setActiveTrack(gCylinder[0], gHead, 1)
  elif displayOptions != 0:
      gPhysicalTrack = ConvertLogToPhys(cyl, head, 1)
  gZone = fz(1)
  if seektype == 'p' or seektype == 's' or displayOptions != 0:
      print "head %u " % gHead + "zone %u " % gZone  + "cylinder %u " % gCylinder + "physical cylinder %u" % gPhysicalTrack
  else:
      print "head %u " % gHead + "zone %u " % gZone  + "cylinder %u " % gCylinder
  return errorCode

####################################################################

def wsk(cyl, head, displayPhysLoc = 0):
  """
  Write seek logical/Data tracks. Display status and sense code from drive.
  Set cudacom globals (gHead, gCylinder, gZone) upon completion.
  @param cyl: Target cylinder
  @param head: Target head
  @return: Error code
  """
  return esk(cyl, head, 'w', displayPhysLoc)
####################################################################

def rsk(cyl, head, displayPhysLoc = 0):
  """
  Read seek logical/data tracks. Display status and sense code from drive.
  Set cudacom globals (gHead, gCylinder, gZone) upon completion.
  @param cyl: Target cylinder
  @param head: Target head
  @return: Error code
  """
  return esk(cyl, head, 'r', displayPhysLoc)

####################################################################

def ws(cyl, head):
  """
  Write seek physical/servo tracks. Display status and sense code from drive.
  Set cudacom globals (gHead, gCylinder, gZone) upon completion.
  @param cyl: Target cylinder
  @param head: Target head
  @return: Error code
  """
  return esk(cyl, head, 's', 1)

####################################################################

def rs(cyl, head):
  """
  Read seek physical/servo tracks. Display status and sense code from drive.
  Set cudacom globals (gHead, gCylinder, gZone) upon completion.
  @param cyl: Target cylinder
  @param head: Target head
  @return: Error code
  """
  return esk(cyl, head, 'p', 1)

####################################################################

def fz(quietMode = 0):
  """
  Find current zone drive is in.
  fz() can only tell the zone change performed by cudacom commands, such as wsk, rsk, esk.
  @param quietMode: Non-zero quietMode supresses printing of the current zone
  @return: zone number
  """
  buf, errorCode = fn(1204)
  #buf, errorCode = __ReceiveResults()
  hZone = binascii.hexlify(buf)
  zone = int(hZone, 16)
  if quietMode == 0:
      print "Current Zone = %u" % zone
  return zone

####################################################################

def GetNumHeadsZones (quietMode = 0):
    """
    Get the number heads and the number of user zones for a drive
    """
    buf, errorCode = fn(1230)
    result = struct.unpack("BB",buf)
    if quietMode == 0:
        print "Number of Heads = %d  " % result[0:1] + "Number of User Zones = %d" % result[1:2]
    hexdata = binascii.hexlify(buf)
    data = int(hexdata, 16)
    heads, zones = __bytes(data)
    return (heads, zones)

####################################################################

def tread(start=0, number=-1):
  """
  Read PBA's
  @param start: Starting LBA
  @param number: Number of sectors to read from Starting LBA. Enter -1 for full track.
  @return: Error code
  """
  if type(start) != type(1) or type(number) != type(1):
    print "tread usage: tread(starting_lba, num_sectors)\n"
    return

  mlba, llba = __lwords(start)
  buf, errorCode = fn(1206, mlba, llba, number)
  #buf,errorCode = __ReceiveResults()
  __displayBuffer(buf)
  return errorCode
####################################################################

def twrite(start=0, number=-1, echo =1):
  """
  Write PBA
  @param start: Starting LBA
  @param number: Number of sectors to read from Starting LBA. Enter -1 for full track.
  @param echo: Display buffer data.
  @return: Error code
  """
  if type(start) != type(1) or type(number) != type(1):
    print "twrite usage: twrite(start, number)\n"
    return

  mlba, llba = __lwords(start)
  buf, errorCode = fn(1215, mlba, llba, number)
  #buf,errorCode = __ReceiveResults()
  if ( echo == 1 ):
    __displayBuffer(buf)
  return errorCode
####################################################################

def slowwrite(total_pba=0, echo =0):
  """
  Slow Write PBA One Track
  @param total_pba: Number of pbas to do the slow write
  @param echo: Display buffer data.
  @return: Error code
  """
  if type(total_pba) != type(1):
    print "slow write usage: slowwrite(total_pba)\n"
    return
  start_pba=0
  errorCode = 0
  if total_pba == 0:
    buf, errorCode = fn(1371)
    #buf,errorCode = __ReceiveResults()
    result = struct.unpack(">H",buf[0:2])
    total_pba = result[0]
  print "totol_pba:%d " % total_pba
  while start_pba < total_pba:
      errorCode = twrite(start_pba, 1, echo)
      if (errorCode != 0):
        print "fail pba:%d"% start_pba
        break
      start_pba += 1
  if errorCode == 0:
    print "slow write pass"
  return errorCode
####################################################################

def tveri(start=0, number=-1):
  """
  Read Verify PBAs
  @param start: Starting LBA
  @param number: Number of sectors to read. Enter -1 for full track.
  @return: Error code
  """
  if type(start) != type(1) or type(number) != type(1):
    print "tveri usage: tveri(starting_lba, num_sectors)\n"
    return

  mlba, llba = __lwords(start)
  buf, errorCode = fn(1319, mlba, llba, number)
  #buf,errorCode = __ReceiveResults()
  __displayBuffer(buf)
  return errorCode
####################################################################


def Write_STCircularBuf(NO_SEEK=0, cyl=0xFFFFFFFF, head=0xFFFF, delay=0, offset=0, writeVal= 0x00):
  """
  Seek , then Write uisng ST_WriteCircularBuf function
  Set cudacom globals (gHead, gCylinder, gZone) upon completion.
  @parm NO_SEEK: Set to a non-zero value to skip the seek
  @parm head: Head to Write
  @parm cyl: Cylinder to Write
  @parm delay: Delay in ms between seek and write
  @parm offset: Servo offset
  @param writeVal: byte value to be written
  @return: Error code
  """
  global gHead
  global gCylinder
  global gZone
  global gPhysicalTrack

  mCylinder, lCylinder = __lwords(cyl)
  buf, errorCode = fn(1378, lCylinder, mCylinder, head, delay, offset, NO_SEEK, writeVal)
  #buf,errorCode = __ReceiveResults()
  if NO_SEEK != 0:
	  __displayBuffer(buf)
  else:
	  result = struct.unpack("LL",buf)
	  SeekSenseData = result[0:1]
	  WriteSenseData = result[1:2]
	  if cyl != 0xFFFFFFFF:
		  gCylinder = cyl
	  if head != 0xFFFF:
		  gHead = head
	  gZone = fz(1)
	  print "Seek Sense Data: %x " % SeekSenseData + "Write Sense Data: %x " % WriteSenseData
	  print "gHead: %u " % gHead + "gCylinder: %u " % gCylinder + "gZone: %u " % gZone

  return errorCode
####################################################################
#################### Super Sector Commands #########################

# XfrOptions bit definitions
RW_SUPER_SECTOR_DISABLE_SEEK                             = 0x0001
RW_SUPER_SECTOR_USE_USER_FAULT_MASK                      = 0x0002
RW_SUPER_SECTOR_ENABLE_FORMATTED_XFR                     = 0x0004
RW_SUPER_SECTOR_ENABLE_DISC_RANDOMIZATION                = 0x0008
RW_SUPER_SECTOR_INPUT_BUFFER_FILE_PTR                    = 0x0010
RW_SUPER_SECTOR_FAST_IO                                  = 0x0020
RW_SUPER_SECTOR_READ_AFTER_WRITE                         = 0x0040
RW_SUPER_SECTOR_ADJ_WEDGE_SIZE_FOR_SHORTENED_SGATE       = 0x0080
RW_SUPER_SECTOR_ENABLE_SMART_DATA_GENERATION             = 0x0100
RW_SUPER_SECTOR_ENCODED_DATA                             = 0x0200
RW_SUPER_SECTOR_SWAPDATA                                 = 0x0400
RW_SUPER_SECTOR_BYPASS_READ_CHANNEL_PROGRAMMING          = 0x0800
RW_SUPER_SECTOR_BYPASS_READ_CHANNEL_CODERATEREG_PROGRAMMING   = 0x1000
RW_SUPER_SECTOR_XFR_BUFFER_DATA_WITH_SYNC                = 0x4000


# WedgeSSOptions
RW_SUPER_SECTOR_LIMIT_WEDGE_XFR_SIZE                      = 0x0001
RW_SUPER_SECTOR_ACCESS_READ_CHANNEL                       = 0x0002
RW_SUPER_SECTOR_XFR_BUFFER_DATA                           = 0x0004
RW_SUPER_SECTOR_START_XFR_ON_FIRST_AVAILABLE_WEDGE        = 0x0008
RW_SUPER_SECTOR_SKIP_WEDGES_BETWEEN_XFR                   = 0x0010
RW_SUPER_SECTOR_WRITE_XFR_IGNORE_NRZ                      = 0x0020
RW_SUPER_SECTOR_START_XFR_ON_FIRST_AVAILABLE_EVEN_WEDGE   = 0x0040
RW_SUPER_SECTOR_START_XFR_ON_FIRST_AVAILABLE_ODD_WEDGE    = 0x0080

####################################################################
def ssw(firstWedge=0, wedgeCount=-1,
        XfrOptions = RW_SUPER_SECTOR_ENABLE_FORMATTED_XFR | RW_SUPER_SECTOR_ENABLE_DISC_RANDOMIZATION,
        WedgeSSOptions = RW_SUPER_SECTOR_XFR_BUFFER_DATA,
        Pattern = 0xC6C6,
        Echo =1,
        NumNrzSymbols = 0 ):
  """
  Super Sector Digital Write
  @param firstWedge: Starting wedge to write
  @param wedgeCount: Number of wedges to write
  @param XfrOptions: Control word for RW API.
  @param WedgeSSOptions: Control word for RW API.
  @param Pattern:    Pattern to write.
  @param Echo:       Display buffer data.
  @param NumNrzSymbols : Number of NRZ symbols to write
  @return: Drive Status
  """

  if type(firstWedge) != type(1) or type(wedgeCount) != type(1):
      print "ssw usage: ssw(firstWedge, wedgeCount)\n"
      return

  buf, errorCode = fn(1283, 3, firstWedge, wedgeCount, XfrOptions, WedgeSSOptions, Pattern,NumNrzSymbols )
  #buf,errorCode = __ReceiveResults()
  if ( Echo == 1 ):
     __displayBuffer(buf)
  return buf
####################################################################

def ssr(firstWedge=0, wedgeCount=-1,
        XfrOptions = RW_SUPER_SECTOR_ENABLE_FORMATTED_XFR | RW_SUPER_SECTOR_ENABLE_DISC_RANDOMIZATION,
        WedgeSSOptions = RW_SUPER_SECTOR_XFR_BUFFER_DATA,
        Echo =1,
        NumNrzSymbols = 0):
  """
  Super Sector Digital Read
  @param firstWedge: Starting wedge to read
  @param wedgeCount: Number of wedges to read
  @param XfrOptions: Control word for RW API.
  @param WedgeSSOptions: Control word for RW API.
  @param Echo:       Display buffer data.
  @param NumNrzSymbols : Number of NRZ symbols to read
  @return: Drive Status
  """

  if type(firstWedge) != type(1) or type(wedgeCount) != type(1):
      print "ssr usage: ssr(firstWedge, wedgeCount)\n"
      return

  buf, errorCode = fn(1283, 5, firstWedge, wedgeCount, XfrOptions, WedgeSSOptions, 0,NumNrzSymbols )
  #buf,errorCode = __ReceiveResults()
  if ( Echo == 1 ):
     __displayBuffer(buf)
  return buf
####################################################################

### Super Sector Digital - Verify
def ssv(firstWedge=0, wedgeCount=-1,
        XfrOptions = RW_SUPER_SECTOR_ENABLE_FORMATTED_XFR | RW_SUPER_SECTOR_ENABLE_DISC_RANDOMIZATION,
        WedgeSSOptions = RW_SUPER_SECTOR_XFR_BUFFER_DATA,
        Pattern = 0xC6C6,
        Echo =1):
  """
  Super Sector Digital Verify
  @param firstWedge: Starting wedge to read
  @param wedgeCount: Number of wedges to read
  @param XfrOptions: Control word for RW API.
  @param WedgeSSOptions: Control word for RW API.
  @param Pattern:    Pattern expected to read.
  @param Echo:       Display buffer data.
  @return: Drive Status
  """

  if type(firstWedge) != type(1) or type(wedgeCount) != type(1):
      print "ssv usage: ssr(firstWedge, wedgeCount)\n"
      return

  buf, errorCode = fn(1283, 4, firstWedge, wedgeCount, XfrOptions, WedgeSSOptions, Pattern)
  #buf,errorCode = __ReceiveResults()
  if ( Echo == 1 ):
     __displayBuffer(buf)
  return buf
####################################################################

### Super Sector Analog - Write
def ssaw(firstWedge=0, wedgeCount=-1,
         XfrOptions = 0,
         WedgeSSOptions = RW_SUPER_SECTOR_XFR_BUFFER_DATA,
         Pattern = 0xCCCC,
         Echo =1):
  """
  Super Sector Analog Write
  @param firstWedge: Starting wedge to write
  @param wedgeCount: Number of wedges to write
  @param XfrOptions: Control word for RW API.
  @param WedgeSSOptions: Control word for RW API.
  @param Pattern:    Pattern to write. Defaults to 2T.
  @param Echo:       Display buffer data.
  @return: Drive Status
  """

  if type(firstWedge) != type(1) or type(wedgeCount) != type(1):
      print "ssaw usage: ssw(firstWedge, wedgeCount)\n"
      return

  buf, errorCode = fn(1283, 6, firstWedge, wedgeCount, XfrOptions, WedgeSSOptions, Pattern)
  if ( Echo == 1 ):
     __displayBuffer(buf)
  return buf
####################################################################

### Super Sector Analog - Read
def ssar(firstWedge=0, wedgeCount=-1,
         XfrOptions = 0,
         WedgeSSOptions = RW_SUPER_SECTOR_XFR_BUFFER_DATA,
         Echo =1,
         Mode=8):
  """
  Super Sector Analog Read
  @param firstWedge: Starting wedge to read
  @param wedgeCount: Number of wedges to read
  @param XfrOptions: Control word for RW API.
  @param WedgeSSOptions: Control word for RW API.
  @param Echo:       Display buffer data.
  @param Mode: Command Type. 8 = simply read, 12 = cert read mode.
  @return: Drive Status
  """

  if type(firstWedge) != type(1) or type(wedgeCount) != type(1):
      print "ssar usage: ssr(firstWedge, wedgeCount)\n"
      return

  buf, errorCode = fn(1283, Mode, firstWedge, wedgeCount, XfrOptions, WedgeSSOptions, 0)
  if ( Echo == 1 ):
     __displayBuffer(buf)
  return buf
####################################################################

### Super Sector Analog - Verify
def ssav(firstWedge=0, wedgeCount=-1,
         XfrOptions = 0,
         WedgeSSOptions = RW_SUPER_SECTOR_XFR_BUFFER_DATA,
         Pattern = 0x0000,
         Echo =1):
  """
  Super Sector Analog Verify
  @param firstWedge: Starting wedge to verify
  @param wedgeCount: Number of wedges to verify
  @param XfrOptions: Control word for RW API.
  @param WedgeSSOptions: Control word for RW API.
  @param Pattern:    Pattern expected to read.
  @param Echo:       Display buffer data.
  @return: Drive Status
  """

  if type(firstWedge) != type(1) or type(wedgeCount) != type(1):
      print "ssav usage: ssr(firstWedge, wedgeCount)\n"
      return

  buf, errorCode = fn(1283, 7, firstWedge, wedgeCount, XfrOptions, WedgeSSOptions, Pattern)
  #buf,errorCode = __ReceiveResults()
  if ( Echo == 1 ):
     __displayBuffer(buf)
  return buf


####################################################################
### SelfTest Version of Diag Write Wedge
def WriteWedge(firstWedge=0, wedgeCount=-1):
  """
  Self-Test version of write wedge diagnostic command
  @param firstWedge: Starting wedge to write
  @param wedgeCount: Number of wedges to write
  @return: Error code
  """

  if type(firstWedge) != type(1) or type(wedgeCount) != type(1):
    print "WriteWedge usage: WriteWedge(firstWedge, wedgeCount)\n"
    return

  mode = 10    # Diag Write Wedge
  buf, errorCode = fn(1283, mode, firstWedge, wedgeCount)
  #buf,errorCode = __ReceiveResults()
  __displayBuffer(buf)
  return errorCode
####################################################################

def ReadWedge(firstWedge=0, wedgeCount=-1):
  """
  Self-Test version of read wedge diagnostic command
  @param firstWedge: Starting wedge to read
  @param wedgeCount: Number of wedge to read
  @return: Error code
  """

  if type(firstWedge) != type(1) or type(wedgeCount) != type(1):
    print "ReadWedge usage: ReadWedge(firstWedge, wedgeCount)\n"
    return

  mode = 9     # Diag Write Wedge
  buf, errorCode = fn(1283, mode, firstWedge, wedgeCount)
  #buf,errorCode = __ReceiveResults()
  __displayBuffer(buf)
  return errorCode
####################################################################

def digwrite(firstWedge=0, wedgeCount=-1):
  """
  Super Sector Digital Write with no Sync Mark
  @param firstWedge: Starting wedge of command
  @param wedgeCount: Number of commands to execute operation on
  @return: Error code
  """

  if type(firstWedge) != type(1) or type(wedgeCount) != type(1):
    print "digwrite usage: digwrite(firstWedge, wedgeCount)\n"
    return

  mode = 11    # Digital Write No Sync
  buf, errorCode = fn(1283, mode, firstWedge, wedgeCount)
  #buf,errorCode = __ReceiveResults()
  __displayBuffer(buf)
  return errorCode

####################################################################

def WriteWedgePRBS(Channel = MARVELL, StartWedge = 0, NumberWedges = 0):
  """
  Write a psuedo-random binary sequence in wedge mode one PRBS sector per wedge???
  Must seek to the target track to set the head and zone.
  @param Channel: AGERE or MARVELL
  @param StartSector: Wedge at which to start writing
  @param NumberWedges: Number of wedges to write, 0 indicates write all wedges
  @return: Error code
  """
  buf, errorCode = fn(1240, Channel, StartWedge, NumberWedges)
  __displayBuffer(buf)
  return errorCode

####################################################################

def ReadWedgePRBS(Channel = MARVELL, StartWedge = 0, NumberWedges = 0):
  """
  Read the psuedo-random binary sequence in wedge mode one PRBS sector per wedge???
  Must seek to the target track to set the head and zone.
  @param Channel: AGERE or MARVELL
  @param StartSector: Wedge at which to start reading
  @param NumberWedges: Number of wedges to read, 0 indicates write all wedges
  @return: Error code
  """
  buf, errorCode = fn(1241, Channel+1, StartWedge, NumberWedges) # 0 and 1 are LSI for ReadWedge and 2 is Marvell for Channel
  __displayBuffer(buf)
  return errorCode

####################################################################

def readbuf(offset = 0):
  """
  Display the read/write buffer in 512 byte chunks
  @param offset: Offset into the read/write buffer to start reading the 512 bytes
  @return: Error code
  """
  buf, errorCode = fn(1213,offset>>16, offset & 0xffff)
  #buf, errorCode = __ReceiveResults()
  __displayMemory(buf,0)
  return errorCode

####################################################################

def fillbuff(pattern):
  """
  Load pattern buffer into drive's dummy cache. 4,549,740 bytes are set.
  @param pattern: Pattern to write
  @return: Error code
  """
  buf, errorCode = fn(1214,pattern)
  #buf, errorCode = __ReceiveResults()
  return errorCode
####################################################################

def rrc(Address, Echo = 1):
  """
  Read and display Channel register
  @param Address: Channel register to read
  @param Echo:     Display buffer data.
  @return: Error code
  """
  buf, errorCode = fn(1308, Address)
  if SocSelected != 0:
     print "Read SoC", SocSelected, "-> "
  #buf,errorCode = __ReceiveResults()
  if ( Echo == 1 ):
     __displayMemory(buf,Address,addressableUnit=2)
  return errorCode
#####################################################################

def wrc(Address, Data, Address2=-1, Data2=-1, Mask = 0xFFFF, Echo = 1):
  """
  Write Channel register(s)
  Optional 3rd & 4th arguments will write a 2nd channel register.
  @param Address:  Channel register to write
  @param Data:     Data written to channel address.
  @param Address2: 2nd channel register to write
  @param Data2:    Data written to channel 2nd address.
  @param Mask:     Bits set are modified.
  @param Echo:     Display buffer data.
  @return: Error code
  """
  global SocSelected

  buf, errorCode = fn(1269, Address, Data, Address2, Data2, Mask)

  if SocSelected != 0:
     print "Write channel SoC", SocSelected, "-> "

  #buf,errorCode = __ReceiveResults()
  if ( Echo == 1):
    __displayMemory(buf,Address,addressableUnit=2,forceLen=2)
    if (Address2 != -1):   # Show 2nd address written, if applicable
      __displayMemory(buf,Address2,addressableUnit=2,startingByte=2,forceLen=2)
  return errorCode
####################################################################

def rrcf_ram(registerID, zone, head):
  """
  Read Read Channel Feature from RAM copy of RAP
  @param registerID: Channel feature to read
  @param head: head offset in RAP
  @param zone: zone offset in RAP
  @return: Error code
  """

  global SocSelected

  buf, errorCode = fn(1336, registerID, head, zone)
  #buf,errorCode = __ReceiveResults()

  if SocSelected != 0:
     print "Read channel rrcf_ram SoC", SocSelected, "-> "

  result = struct.unpack("HH",buf)
  status = result[1:2]
  print "dec: %u " % (result[0:1]) + "hex: %x " % (result[0:1])
  if status[0] != 1:   # 1 is PASS
    print "Read Channel RAM Failed, status = %x" % (result[1:2])
  return errorCode
####################################################################

def wrcf_ram(registerID, data, zone, head):
  """
  Write Read Channel Feature to RAM copy of RAP
  @param registerID: Channel feature to write
  @param data: Data written to channel feature.
  @param head: head offset in RAP
  @param zone: zone offset in RAP
  @return: Error code
  """
  global SocSelected
  
  buf, errorCode = fn(1337, registerID, data, head, zone)

  if SocSelected != 0:
     print "Write channel wrcf_ram SoC", SocSelected, "-> "

  #buf,errorCode = __ReceiveResults()
  result = struct.unpack("H",buf)
  status = result[0:1]
  if status[0] != 1:   # 1 is PASS
    print "Write Channel RAM Failed, status = %x" % (result[0:1])
  return errorCode
####################################################################

def rrcf(registerID, QuietMode = 0):
  """
  Read Read Channel Feature from the channel
  @param registerID: Channel feature to read
  @return: Error code
  """
  global SocSelected
  
  buf, errorCode = fn(1338, registerID)
  #buf,errorCode = __ReceiveResults()

  if SocSelected != 0:
     print "Read channel rrcf SoC", SocSelected, "-> "

  result = struct.unpack("HH",buf)
  status = result[1:2]
  if QuietMode == 0:
      print "dec: %u " % (result[0:1]) + "hex: %x " % (result[0:1])
      if status[0] != 1:   # 1 is PASS
        print "Read Channel Failed, status = %x" % (result[1:2])
  return result[0]
####################################################################

def wrcf(registerID, data, zone, head):
  """
  Write Read Channel Feature to RAM copy of RAP and the channel
  @param registerID: Channel feature to write
  @param data: Data written to channel feature.
  @param head: head offset in RAP
  @param zone: zone offset in RAP
  @return: Error code
  """
  global SocSelected
  
  buf, errorCode = fn(1339, registerID, data, head, zone)
  #buf,errorCode = __ReceiveResults()

  if SocSelected != 0:
     print "Write channel wrcf SoC", SocSelected, "-> "

  result = struct.unpack("H",buf)
  status = result[0:1]
  if status[0] != 1:   # 1 is PASS
    print "Write Channel and RAM Failed, status = %x" % (result[0:1])
  return errorCode
####################################################################

def wrcf_chan(registerID, data):
  """
  Write Read Channel Feature to channel
  @param registerID: Channel feature to write
  @param data: Data written to channel feature.
  @return: Error code
  """
  global SocSelected
  
  buf, errorCode = fn(1340, registerID, data)
  #buf,errorCode = __ReceiveResults()

  if SocSelected != 0:
     print "Write channel wrcf_chan SoC", SocSelected, "-> "

  result = struct.unpack("H",buf)
  status = result[0:1]
  if status[0] != 1:   # 1 is PASS
    print "Write Channel and RAM Failed, status = %x" % (result[0:1])
  return errorCode
####################################################################

def RunChannelList( List = 12, Restore = 0 ):
   """
   Sends a list of channel settings to the channel.  Channels lists are used by many tests
   to configure the channel for a specific operation, for example media certification.
   Existings lists in Firmware 02/15/2008:
   CSMSetupList,                           // 0
   CSMSetupListRap,                        // 1
   DisableAdaptiveFIRList,                 // 2
   DisableAdaptiveFIRListRap,              // 3
   VGAAdaptationList,                      // 4
   VGAAdaptationListRap,                   // 5
   AnalogThresholdList,                    // 6
   EnableAnalogFlawScanList,               // 7
   lockChannelForHSCList,                  // 8
   harmonicSensorCircuitList,              // 9
   EnableAFSTunedDriveList,                // 10
   EnableAFSListRap,                       // 11
   EnableAnalogFlawScanListBWM,            // 12
   DisableFIR10Thru7List,                  // 13
   DisableNPMLArrayList,                   // 14
   DisableNyquistGainArrayList,            // 15
   DisableNyquistGainListRap,              // 16
   DisableAsymmGainArrayList,              // 17
   DisableVGAAutoRangeListRap,             // 18
   TASetupList,                            // 19
   TAThresholdList,                        // 20
   LockVGAList,                            // 21
   LockChannelAdaptivesList,               // 22
   UnstableHdTADetectionList,              // 23
   InitFirListRap,                         // 24
   InitNpmlListRap                         // 25
   """
   buf, errorCode = fn(1205, List, Restore)
   #buf, errorCode = __ReceiveResults()
   return errorCode
####################################################################

def ser(TLevel = 0, DumpBciData = 0, quietMode = 0):
  """
  Run the VBAR sector error rate command using ActiveHead and ActiveCylinder for the target location
  Display Sector Error Rate, Data Errors, Sync Errors, Total Errors, #Sectors Read, and Sense Code
  @param Tlevel: TLevel for PRML channels or iteration count at which to read bits in error count for LDPC channels
  @param DumpBciData: Dump BCI if this flag is not zero, LDPC channels only
  @param quietMode: Supress printing of results
  @return: Error code
  """
  buf, errorCode = fn(1341, TLevel)
  result = struct.unpack("fHHHHLLLLL",buf)
  resultDict = {'SER': result[0:1][0], 'DataErrors' : result[1:2][0], 'SyncErrors':result[2:3][0], 'TotalErrors': result[3:4][0], 'NumSectors': result[4:5][0],'SenseData':result[5:6][0]}
  if quietMode == 0:
      print "SER = %f " % (resultDict['SER']) + "Data Errors = %u " % (resultDict['DataErrors']) + "Sync Errors = %u " % (resultDict['SyncErrors']) + \
      "Total Errors = %u " % (resultDict['TotalErrors']) + "#Sectors = %u " % (resultDict['NumSectors']) + "Sense Data = %x" % (resultDict['SenseData'])
  if DumpBciData != 0:   # If requested, dump the BCI Data also
      print " "      # \n
      NumberOfSectors = result[4:5]
      # Get number of codewords from the channel
      buf, errorCode = fn(1338, 0x100)   # rrcf(0xf8) command and rrcf(0x100) with BF_0126362_357267_FIX_DUPLICATE_REGISTER_IDS
      CodewordsPerSector = struct.unpack("HH",buf)
      GetAndDisplayBCILogData(NumberOfSectors[0], CodewordsPerSector[0])
      FreeBciBuffer()   # Free the BCI Data Pointer after dumping the data
  return errorCode
####################################################################

def GetMargin(NumIterations = 0, IterationLoadCount = 0, ExecutionFlags = 0,  BERTarget = 0, RequiredNumTrackReads = 0, IterationCountThreshold = 0, DumpBciData = 0, quietMode = 0):
  """
  Run the GetMargin() function using ActiveHead and ActiveCylinder for the target location
  @param NumIterations: The number of iterations, defaulted to zero
  @param IterationLoadCount: The iteration load count, defaulted to zero(DEFAULT_ITER_LOAD_COUNT)
  @param ExecutionFlags: Used to control algorithm flow, defaulted to zero to use the default flag settings
  @param BERTarget: Target the BER precision (70 = 1E7 bits read or 10 errs occurred, whichever first), defaulted to zero to use the default BERTarget
  @param IterationCountThreshold: The Iteration Count value at which a sector will be called a failure for SFR computation,
                                  defaulted to zero to use the default IterationCountThreshold
  @param RequiredNumTrackReads: Number of required track reads before we terminate the reads, defaulted to zero to use the default RequiredNumTrackReads
  @param DumpBciData: Dump BCI if this flag is not zero, LDPC channels only
  @param quietMode: Supress printing of results
  @return: Status, BitErrorRate, BitsInError, SenseCode(This is a tuple)

  The execution flags for GetMargin:
  #define GET_MARGIN_DISABLE_COMPUTE_BIE_PER_SECTOR                   0x00000001UL   // If TRUE does not compute (time saving)
  #define GET_MARGIN_DISABLE_COMPUTE_TMEAN_VGAR                       0x00000002UL   // If TRUE does not compute Trimmed Mean VGAR, just uses the value from last good sector.
  #define GET_MARGIN_DISABLE_COMPUTE_TMEAN_FIR                        0x00000004UL   // If TRUE does not compute Trimmed Mean FIR, just uses the value from last good sector.
  #define GET_MARGIN_ALLOW_MULTI_REV_MEASUREMENTS                     0x00000008UL   // If TRUE does enough reads to meet BERTarget
  #define GET_MARGIN_DISABLE_FIR_SETTLING_SAMPLING                    0x00000010UL   // If TRUE does not analyze for FIR settling, simply returns metrics from convergence pt.
  #define GET_MARGIN_DISABLE_QUALIFY_READ_FOR_ADAPTIVES_CAPTURE       0x00000020UL   // If TRUE disables the qualification of the sector from which adaptives are sampled.
  #define GET_MARGIN_RESET_FIR_BEFORE_READ                            0x00000040UL   // if TRUE resets the FIR to Init values
  #define GET_MARGIN_WRITE_TRACK                                      0x00000080UL   // If TRUE writes the target & side tracks
  #define GET_MARGIN_DISABLE_FORCE_READ_CONTINUOUS                    0x00000100UL   // If TRUE disable read continuous
  #define GET_MARGIN_DISABLE_PROCESS_SLE_STATISTICS                   0x00000200UL   // If TRUE disable collecting and computing BCI SLE's
  #define GET_MARGIN_DISABLE_PROCESS_ERROR_STATISTICS                 0x00000400UL   // If TRUE disable collecting error statistics
  #define GET_MARGIN_READ_TRACK                                       0x00000800UL   // If TRUE reads the target track and collects error statistics
  #define GET_MARGIN_DISABLE_MONITORED_HARDWARE_ACCESS                0x00001000UL   // If TRUE disables the monitored hardware access data collection
  #define GET_MARGIN_DISABLE_ROBUST_FIR_SETTLING                      0x00002000UL   // If TRUE disables anaylsis of FIR taps to determine when they have settled
  #define GET_MARGIN_DISABLE_SHORTEST_NUMBER_OF_REVS                  0x00004000UL   // If TRUE disables measuring margin with the shortest number of revs and uses the BER target instead.
  #define GET_MARGIN_LBA_READ                                         0x00008000UL   // If TRUE reads are performed in LBA mode
  #define GET_MARGIN_DISABLE_ZERO_LATENCY_MODE                        0x00010000UL   // If TRUE disables ZLR mode
  #define GET_MARGIN_PBA_READ                                         0x00020000UL   // If TRUE reads are performed in PBA mode
  #define GET_MARGIN_RW_NO_SEEK                                       0x00040000UL   // If TRUE stops servo from seeking during reads and writes
  """

  ExecutionFlagsUW, ExecutionFlagsLW = __lwords(ExecutionFlags)

  #Set default values to zero.
  BitErrorRate = 0
  BitsInError = 0
  SenseCode = 0

  buf, Status = fn(1390, NumIterations, IterationLoadCount, ExecutionFlagsUW, ExecutionFlagsLW, BERTarget, RequiredNumTrackReads, IterationCountThreshold);

  result = struct.unpack("fffLLLLLLHHHH", buf)

  if Status == 10288:
     print "Malloc failed\n"
  else:
     SenseCode = result[8]
     if quietMode == 0:
        # Report only if the test passed or if there were read errors
        if Status == 0 or Status == 10402:
            print "ComputedBER = %f " % result[0] + "SFR = %f " % result[1] + "NumBitsTransferred = %f " % result[2] + \
            "SumSLEBitErrors = %u " % result[3] + "NumValidSLEs = %u " % result[4] + "NumTotalSLEs = %u " % result[5] + \
            "SumSyncErrors = %u " % result[6] + "SumUnrecoverableErrors = %u " % result[7] + "SumICSFCount = %u "  % result[9] + \
            "NumRevsProcessed = %u " % result[10] + "NumRevsOfValidData = %u " % result[11] + "Number of Sectors = %u" % result[12]
            BitErrorRate = result[0]
            BitsInError = result[3]
            # Dump BCI data only if the Test passed
            if Status == 0:
               if DumpBciData != 0:   # If requested, dump the BCI Data also
                  print " "
                  NumberOfSectors = result[12]
                  # Get number of codewords from the channel
                  buf, errorCode = fn(1338, 0x100)   # rrcf(0xf8) command and rrcf(0x100) with BF_0126362_357267_FIX_DUPLICATE_REGISTER_IDS
                  CodewordsPerSector = struct.unpack("HH",buf)
                  GetAndDisplayBCILogData(NumberOfSectors, CodewordsPerSector[0])
                  FreeBciBuffer()   # Free the BCI Data Pointer after dumping the data """

  print "Status: %u  " % Status + "BitErrorRate: %f  " % result[0] + "Bits In Error: %u  " % result[3] + "SenseCode: 0x%x " % SenseCode
  """
  To collect data following the function call to GetMargin the format which can be followed is:
  Status, BitErrorRate, BitsInError, SenseCode = GetMargin()
  """
  return (Status, BitErrorRate, BitsInError, SenseCode)
####################################################################

def rrcf_hd(registerID, head):
  """
  Display Channel Feature from RAM copy of RAP for all zones on a head
  @param registerID: Channel feature to read
  @param head: head offset in RAP
  @return: Error code
  """
  zone = 0
  errorCode = 0
  while zone<18 and errorCode == 0:
      errorCode = rrcf_ram(registerID, zone, head)
      zone += 1
  return errorCode

####################################################################

def ReadNld(Zone = 0, Head = 0, Options = 0, Means = 0xe0f0, F1Var = 0x1005, F3F2 = 0x00ff):
    """
    Read or Write NLD parameters from the channel or RAP. When writing, only one states worth of
    parameters is input and those values are copied to all 16 states.

    Valid Options from selftest-channel.h:

    #define TAP_OPT_NO_OPTIONS                0x0000   // Read from channel
    #define TAP_OPT_UPDATE_CHANNEL            0x0001   // Write to channel
    #define TAP_OPT_UPDATE_DZH_TABLE          0x0002   // Write to RAP
    #define TAP_OPT_USE_CALLERS_TAP_VALUES    0x0004   // Write using passed in values
    #define TAP_OPT_READ_DHZ_TABLE            0x0008   // Read tap values from RAP

    @param Zone: zone offset in RAP
    @param Head: head offset in RAP
    @param Options: Options for ReadWriteNLDEstimationParms - see above bit definitions
    @param Means: Values for Mean1 (MSB) and Mean0 (LSB)
    @param F1Var: Values for tap F1 (MSB) and Variance (LSB)
    @param F3F2: Values for taps F3 (MSB) and F2 (LSB)
    @return: Error code
    """
    # Initialize lists
    mean0 = [0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5]
    mean1 = [0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5]
    var = [0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5]
    f1 = [0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5]
    f2 = [0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5]
    f3 = [0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5]
    buf, errorCode = fn(1238, Head, Zone, Options, Means, F1Var, F3F2)    # Call ReadWriteNLDEstimationParms
    if (Options & 0x0004) == 4:
        print "Writing NLD Estimation Parameters"
    else:
        nld = struct.unpack("48H",buf)
        for count in range (0, 16, 1):
           mean0[count] =  nld[count] & 0x00ff
           mean1[count] = (nld[count] & 0xff00) >> 8
           var[count]   =  nld[count+16] & 0x00ff
           f1[count]    = (nld[count+16] & 0xff00) >> 8
           f2[count]    =  nld[count+32] & 0x00ff
           f3[count]    = (nld[count+32] & 0xff00) >> 8
        print "          Mean0 Mean1 Var F1  f2   F3"
        for count in range (0, 16, 1):
           print "State = %d " % count + " %2.2x" % (mean0[count]) + "%5.2x" % (mean1[count]) + "%5.2x" % (var[count]) + \
                 "%5.2x" % (f1[count]) + "%5.2x" % (f2[count]) + "%5.2x" % (f3[count])

####################################################################

def RwNptCorrSync(Options = 2, Targ0 = 4, Targ1 = 7, Targ2 = 0, Zone = 0, Head = 0, SMPattern = 0xabcd, SMThreshold = 100, SMOffset = 0x0a00):
    """
    Read or Write Noise Predictive Targets and Correlation Sync Mark Parameters from the channel or RAP for the Marvell 9200 Channel.

    Valid Options from t251_pub.h:

    #define NPT_WRITE_CHANNEL          0x0001  // Write the NPT Target values to the Channel.
    #define NPT_READ_CHANNEL           0x0002  // Read the NPT Target values from the Channel.
    #define NPT_WRITE_RAP_RAM          0x0004  // Write the NPT Target values to the Ram copy of the RAP.
    #define NPT_READ_RAP_RAM           0x0008  // Read the NPT Target values from the Ram copy of the RAP.
    #define NPT_USE_DEFAULT_SM_PATTERN 0x0010  // Use the default syncmark pattern passed in as a parameter.
    #define NPT_SKIP_CORR_SYNC_MARK    0x0020  // Do not write the correlation sync mark parameters

    @param Targ0: Noise Predictive Target 0
    @param Targ1: Noise Predictive Target 1
    @param Targ2: Noise Predictive Target 2
    @param Zone: zone offset in RAP
    @param Head: head offset in RAP
    @param Options: Options for ReadWriteNoisePredictiveTargets - see above bit definitions
    @param SMPattern: First 16 bits of 20 bit sync mark pattern
    @param SMThreshold: Sync mark threshold
    @param SMOffset: Offset pattern to be repeated for all 9 sync mark offsets. This is intended only for channel write verification.
                     Actual sync mark offsets must be entered manually currently.
    @return: Error code
    """
    Target0Target1 = ((Targ0 << 8) + (Targ1 & 0x00ff)) & 0xffff
    HeadZone = (Head << 8) + Zone
    buf, errorCode = fn(1239, Target0Target1, Targ2, HeadZone, Options, SMPattern, SMThreshold, SMOffset)    # Call ReadWriteNoisePredictiveTargets
    if Options & 0x003a:    # Read Options only
        result = struct.unpack("bbbblHHHHHHHHHH",buf)
        print "Targ0 = %d " % result[0:1] + "Targ1 = %d " % result[1:2] + "Targ2 = %d " % result[2:3] + "SmPattern = %d " % result[4:5] + "SmThresh = %d" % result[5:6]
        print "Correlation Sync Mark Detector Offsets 0 - 9: %d" % result[6:7] + " %d " % result[7:8] + " %d " % result[8:9] + " %d " % result[9:10] + " %d " % result[10:11] + " %d " % result[11:12] + \
              " %d " % result[12:13] + " %d " % result[13:14] + " %d " % result[14:15]

####################################################################

def fir(zone = 256, head = 256):
    """
    Read FIR values directly from the channel or from the RAM RAP (Agere Copperhead Lite).
    Display values read.
    @param zone: zone offset in RAP (default zone == 256 sets mode to channel)
    @param head: head offset in RAP (default head == 256 sets mode to channel)
    @return: Error code
    """
    mode = "RAM"
    if zone == 256 or head == 256:
        mode = "CHANNEL"
    tap = 0x31
    errorCode = 0
    taps = ()
    while tap < 0x3b and errorCode == 0:
        if mode == "CHANNEL":
            buf, errorCode = fn(1338,tap)    # Read channel feature from channel
        else: # mode must be RAM
            buf, errorCode = fn(1336,tap,head,zone)  # Read channel feature from RAP
        #buf,errorCode = __ReceiveResults()
        result = struct.unpack("HH",buf)
        taps = taps + result[0:1]
        status = result[1:2]
        if status[0] != 1:   # 1 is PASS
            print "Read Channel Failed, status = %x" % (result[1:2])
        tap += 1
        if tap == 0x34:
            tap = 0x35
    tap = 0x8e
    while tap < 0x92 and errorCode == 0:
        if mode == "CHANNEL":
            buf, errorCode = fn(1338,tap)    # Read channel feature from channel
        else: # mode must be RAM
            buf, errorCode = fn(1336,tap,head,zone)  # Read channel feature from RAP
        #buf,errorCode = __ReceiveResults()
        result = struct.unpack("HH",buf)
        taps = taps + result[0:1]
        status = result[1:2]
        if status[0] != 1:   # 1 is PASS
            print "Read Channel Failed, status = %x" % (result[1:2])
        tap += 1
        if tap == 0x90:
            tap = 0x91
    print "TW1 TW2 TW3 TW5 TW6 TW7 TW8 TW9 TWX TNY  TDC TDTARG"
    print " %x  " % (taps[0:1]) + "%x  " % (taps[1:2]) + "%x  " % (taps[2:3]) + \
           "%x  " % (taps[3:4]) + "%x  " % (taps[4:5]) + "%x  " % (taps[5:6]) + \
           "%x  " % (taps[6:7]) + "%x  " % (taps[7:8]) + "%x  " % (taps[8:9]) + \
           "%x  " % (taps[9:10]) + "%x  " % (taps[10:11]) + "%x  " % (taps[11:12])
    return errorCode
####################################################################

def npml(zone = 256, head = 256):
    """
    Read NPML TAP values directly from the channel or the RAM RAP (Agere Copperhead Lite)
    @param zone: zone offset in RAP (default zone == 256 sets mode to channel)
    @param head: head offset in RAP (default head == 256 sets mode to channel)
    @return: Error code
    """
    mode = "RAM"
    if zone == 256 or head == 256:
        mode = "CHANNEL"
    tap = 0xa4
    errorCode = 0
    taps = ()
    while tap < 0xaf and errorCode == 0:       # Read NPTAP0_7 -- _0 and NPTAP1_7 -- _0
        if mode == "CHANNEL":
            buf, errorCode = fn(1338,tap)    # Read channel feature from channel
        else: # mode must be RAM
            buf, errorCode = fn(1336,tap,head,zone)  # Read channel feature from RAP
        #buf,errorCode = __ReceiveResults()
        result = struct.unpack("HH",buf)
        taps = taps + result[0:1]
        status = result[1:2]
        if status[0] != 1:   # 1 is PASS
            print "Read Channel RAM Failed, status = %x" % (result[1:2])
        tap += 1
        if tap == 0xa7:
            tap = 0xab
    tap = 0xa7
    while tap < 0xab and errorCode == 0:       # Read NPTAP2_7 -- _0
        if mode == "CHANNEL":
            buf, errorCode = fn(1338,tap)    # Read channel feature from channel
        else: # mode must be RAM
            buf, errorCode = fn(1336,tap,head,zone)  # Read channel feature from RAP
        #buf,errorCode = __ReceiveResults()
        result = struct.unpack("HH",buf)
        taps = taps + result[0:1]
        status = result[1:2]
        if status[0] != 1:   # 1 is PASS
            print "Read Channel RAM Failed, status = %x" % (result[1:2])
        tap += 1
    tap = 0xa1
    while tap < 0xa4 and errorCode == 0:       # Read NPTAP3_7 -- _0
        if mode == "CHANNEL":
            buf, errorCode = fn(1338,tap)    # Read channel feature from channel
        else: # mode must be RAM
            buf, errorCode = fn(1336,tap,head,zone)  # Read channel feature from RAP
        #buf,errorCode = __ReceiveResults()
        result = struct.unpack("HH",buf)
        taps = taps + result[0:1]
        status = result[1:2]
        if status[0] != 1:   # 1 is PASS
            print "Read Channel RAM Failed, status = %x" % (result[1:2])
        tap += 1

    print "NPML Taps (hex row followed by temp decimal row for opti)"
    print "NT0_7 NT0_654 NT0_321 NT1_76 NT1_54 NT1_32 NT1_10 NT2_76 NT2_54 NT2_32 NT2_10 NT3_765 NT3_432 NT3_10"
    print " %4x " % (taps[0:1]) + " %5x " % (taps[1:2]) + " %6x " % (taps[2:3]) + \
           " %5x " % (taps[3:4]) + " %5x " % (taps[4:5]) + " %5x " % (taps[5:6]) + \
           " %5x " % (taps[6:7]) + " %5x " % (taps[7:8]) + " %5x " % (taps[8:9]) + \
           " %5x " % (taps[9:10]) + " %5x " % (taps[10:11]) + " %6x " % (taps[11:12]) + \
           " %6x " % (taps[12:13]) + " %5x " % (taps[13:14])
    print "%3d  " % (taps[0:1]) + "  %5d  " % (taps[1:2]) + " %5d " % (taps[2:3]) + \
           " %5d " % (taps[3:4]) + " %5d " % (taps[4:5]) + " %5d " % (taps[5:6]) + \
           " %5d " % (taps[6:7]) + " %5d" % (taps[7:8]) + "%5d " % (taps[8:9]) + \
           " %5d " % (taps[9:10]) + " %5d " % (taps[10:11]) + " %5d " % (taps[11:12]) + \
           " %5d " % (taps[12:13]) + " %5d " % (taps[13:14])
    return errorCode
####################################################################

def ber(targetBer, numRevs, TLevel, ldpc=0, globalIterations = 0, localIterations = 0, zeroLatency=0):
  """
  Run the BER test, seek to target track using ActiveHead and ActiveCylinder and measure raw BER.
  Display Bit Error Rate, Data Errors, Sync Errors, Other Errors, Sectors Per Rev, Sense Code, and failed sector if other error.
  @param targetBer: Target BER limit (times 10) to measure. Number of revs are calculated internally to meet the target BER.
  @param numRevs: Number of revs to read in the BER test. Will override the targetBer if numRevs is non-zero.
  @param TLevel: ECC Level (0 to 30 by 2's -- See TLEVEL define below in setEccLevel). Non-LDPC channels only.
  @param ldpc: Low Density Parity Encoding (iterative) channel if set else PRML channel. 0x0001 = LDPC SFR, 0x0002 = LDPC BER.
               0x0004 = LDPC BER Mode with data error handling (need to set bit 0x0002 also).
  @param globalIterations: Set to 1 to enable global iterations. LDPC channels only.
  @param localIterations: Number of local iterations to run. LDPC channels only.
  @param zeroLatency: Enable zero latency read if set to 1
  @return: Error code
  """
  if ((TLevel % 2) != 0) or ((TLevel > 30) and (TLevel != 100)):
    print "Invalid TLevel Entered!"
    return
  if ldpc & 2:
      zeroLatency |= 2   # Use this flag to set the BER option for execfunc.c
  if ldpc & 4:
      zeroLatency |= 4   # Use this flag to set the BER option with data error accounting in error counts
  buf, errorCode = fn(1342, targetBer, numRevs, TLevel, globalIterations, localIterations,  zeroLatency)
  if ldpc != 0:
      result = struct.unpack("fLLLLHHLL",buf)
  else:
      result = struct.unpack("fLLLHHLLL",buf)
  if ldpc != 0:
      other_errors = result[4:5]
      print "BER = %f " % (result[0:1]) + "Bits in Error = %u " % (result[1:2]) + "Data Errors = %u " % (result[2:3]) + "Sync Errors = %u " % (result[3:4]) + \
      "Other Errors = %u " % (result[4:5]) + "Sectors per Rev = %u " % (result[5:6]) + "Sense Data = %x " % (result[7:8])
  else:
      other_errors = result[3:4]
      print "BER = %f " % (result[0:1]) + "Data Errors = %u " % (result[1:2]) + "Sync Errors = %u " % (result[2:3]) + \
      "Other Errors = %u " % (result[3:4]) + "Sectors per Rev = %u " % (result[4:5]) + "Sense Data = %x " % (result[6:7])
  if other_errors[0] > 0:
      if ldpc != 0:
          print "Failed Sector = %u" % (result[8:9])
      else:
          print "Failed Sector = %u" % (result[7:8])
  measure_ber = (result[0:1])
  ber = float(measure_ber[0])
  return ber

####################################################################

def LbaTrackErrorRate(Revs = 1, IterationCount = 32, PercentLBAs = 50, Mode = 0):
    """
    Run an LBA BCI based BER test. Seek to target track to set ActiveHead and ActiveCylinder and then measure raw BER.
    Read on tracks worth of LBA's or PBA's on the target track as specified by ActiveHead and ActiveCylinder
    and display error rate statistics based on the BCI data received back.
    @param Revs: Number of revs to read
    @param IterationCount: Number of local iteration for the channel to use. If not zero, then Global Iterations are TRUE.
    @param PercentLBAs: Minumum percent of sectors on the track that are LBAs (not mapped out) for this test to run.
    @param mode: Bit Flag - 0 = LBA mode, 1 = PBA mode
    """
    buf, errorCode = fn(1236, Revs, IterationCount, PercentLBAs, Mode)
    if errorCode == 0:
        result = struct.unpack("fLLLLLQH",buf)
        MeanBitsInError = float(result[1])/100
        MeanIterationcount = float(result[4])/100
        print "BER = %f " % (result[0:1]) + "Mean Bits in Error = " + str(MeanBitsInError) + " Data Errors = %u " % (result[2:3]) + "Sync Errors = %u " % (result[3:4]) + \
            "Mean Iteration Count = " + str(MeanIterationcount)
        print " Sense Data = %x " % (result[5:6]) + "Failed LBA = %lu " % (result[6:7]) + "Codewords Read = %d " % (result[7:8])

####################################################################

def LbaErrorRate(lba, xferlen, mode = 0):
    """
    Read specified number of LBA's or PBA's and display error rate statistics
    @param lba: Starting LBA or PBA
    @param xferlen: Number of LBAs to read
    @param mode: Bit Flag - 0 = LBA mode, 1 = PBA mode, 2 = Single shot mode else all zones, 4 = Include ID of zone stats else full zone only
    @return: Error code
    """
    print "lba = %d " % lba
    Bits63to48, Bits47To32, Bits31To16, Bits15To0 = __llwords(lba)
    buf, errorCode = fn(1227, Bits63to48, Bits47To32, Bits31To16, Bits15To0, xferlen, mode)
    result = struct.unpack("QL",buf)
    print "Failed PBA = %u " % (result[0:1]) + "Sense Code = %x " % (result[1:2])
    Chunksize = 17
    if (mode & 2) == 2: # Single read mode, all data in one structure
        print "Single Read Mode"
        DumpLbaErrorRateData(StartingZone = 0, Chunksize = 1, mode = 2)
    else:
        DumpLbaErrorRateData(StartingZone = 0, Chunksize = 17, mode = 0)
    if (mode & 4) == 4: # Get ID of zone data also
        print " "
        print "******************************"
        print "* ID of Zone Error Rate Data *"
        print "******************************"
        DumpLbaErrorRateData(StartingZone = 0, Chunksize = 17, mode = 4)
    return errorCode

####################################################################

def DumpLbaErrorRateData(StartingZone = 0, Chunksize = 17, mode = 0):
  """
  Display error rate statistics raw data which is logged by zone which may include the system zone.
  @param StartingZone: Log index by zone to begin displaying data from
  @param Chunksize: Number of records to transfer per call. Default to 18 zones per head.
  @param mode: Bit Flag - 0 = LBA mode, 1 = PBA mode, 2 = Single shot mode else all zones, 4 = Include ID of zone stats else full zone only
  """
  NumHeads, NumZones = GetNumHeadsZones(1)
  Zone = StartingZone
  ActualZone = 0
  Head = 0
  BitsInError = 0.0 # Init to float
  TotalZones = NumHeads * NumZones
  if (mode & 2) == 2: # Single read mode, all data in one structure
      TotalZones = 1
  # Get bits read information
  # bits_per_trk = BITS_PER_SYMBOL * CodewordSizeInSymbols * CodewordsPerSector * sect_per_trk;
  BITS_PER_SYMBOL = 12.0                # For Bonanza
  CodewordSizeInSymbols = rrcf(0xff,1)  # Get from channel (regid changes with BF_0126362_357267_FIX_DUPLICATE_REGISTER_IDS)
  CodewordsPerSector = rrcf(0x100,1)     # Get from channel
  print "Bits per Symbol = %d " % BITS_PER_SYMBOL + "Codeword Size in Symbols = %d " % CodewordSizeInSymbols + \
        "Codewords per Sector = %d" % CodewordsPerSector
  print " " # Next line...
  print "Zone Head Bits in Error  Non-Converged Codewords  Data Sync Errors  Iterations  Codewords    BER"
  print "======================================================================================================"
  # Get LBA Error Rate records in chunks
  while Zone < TotalZones :
      buf, errorCode = fn(1229, Zone, Chunksize, mode)
      # Display the data
      Record = 0
      for Record in range(0, Chunksize, 1):
          ActualZone = int( (Record + Zone) / NumHeads )
          Head = int(Record + (Chunksize * Zone)) % NumHeads
          ErrorRateData = struct.unpack("QLLLL",buf[(Record * 24):((Record * 24)+24)])
          NumberOfSectorsRead = ErrorRateData[4]
          if NumberOfSectorsRead > 0:   # Compute error rate if we have sectors read
              BitsInError = ErrorRateData[0]
              if BitsInError == 0:
                  BitsInError = 0.5
              ErrorRate = BitsInError / (NumberOfSectorsRead * CodewordsPerSector * CodewordSizeInSymbols * BITS_PER_SYMBOL)
              ErrorRate = log10(ErrorRate)
          else:
              ErrorRate = 0 # No data read, leave at zero
          if (mode & 2) == 2: # Single read mode, all data in one structure, no head zone info
              print "         " + " %7u " % (ErrorRateData[0:1]) + " %18u " % (ErrorRateData[1:2]) + \
              " %20u " % (ErrorRateData[2:3]) + " %15u " % (ErrorRateData[3:4]) + " %10u " % (ErrorRateData[4:5]) + \
              " %10f " % ErrorRate
          else:
              print "%3d " % ActualZone + "%4u " % Head + " %7u " % (ErrorRateData[0:1]) + " %18u " % (ErrorRateData[1:2]) + \
              " %20u " % (ErrorRateData[2:3]) + " %15u " % (ErrorRateData[3:4]) + " %10u " % (ErrorRateData[4:5]) + \
              " %10f " % ErrorRate
      Zone += Chunksize

####################################################################

def LbaWrite(lba, xferlen, mode = 0):
  """
  Write specified number of LBA's or PBA's
  @param lba: Starting LBA or PBA
  @param xferlen: Number of LBAs to write
  @param mode: 0 = LBA mode, 1 = PBA mode
  @return: Error code
  """
  Bits63to48, Bits47To32, Bits31To16, Bits15To0 = __llwords(lba)
  buf, errorCode = fn(1228, Bits63to48, Bits47To32, Bits31To16, Bits15To0, xferlen, mode)
  result = struct.unpack("QL",buf)
  print "Failed PBA = %lu " % (result[0:1]) + "Sense Code = %x " % (result[1:2])
  return errorCode

####################################################################

def AccessServoRegister(register, function = 0, value = 0):
  """
  Read or write to servo (non-memory mapped) registers. Default setting is read.
  @param register: Address of register to be accessed
  @param function: 0 to read, 1 to write
  @param value: Write value, if applicable
  """
  if (register < 0x30) or (register > 0x7F):
    print "%u " % register + "is not a valid register"
    return 0

  if (register <= 0x59) and (register >= 0x40):
    if register % 2:
      print "16 bit register must be even-numbered"
      return 0
    if (register >= 0x40) and (register <= 0x4f) and function:
      print "attempted to write a read-only register"
      return 0

  buf, errorCode = fn(1372, function, register, value)
  #buf,errorCode = __ReceiveResults();

  if (register <= 0x58) and (register >= 0x40):
    result = struct.unpack("HH",buf)
  else:
    result = struct.unpack("BBBB",buf)

  if function:
    print "Wrote %x" % result[0:1] + " to register %x" %register
  else:
    print "Register %x" % register + " = %x" % (result[0:1])

  return errorCode
####################################################################

def ReadRetryBuckets(Tlevel = 20, mode = 0x08, timeout = 30):
  """
  Run ReadRetryBuckets. Display error rate, sectors in error, and number of retries
  Indicate hard or soft error
  @param Tlevel: ECC Level (0 to 30 by 2's -- See TLEVEL define below in setEccLevel). Default is 10.
  @param mode: Set to 1 to use LBA mode, set to 0 to use PBA mode. Default is RETRY_BUCKETS_ENABLE_DATA_COLLECTION.

              Description                Available flag options                         Value
             ________________________________________________________________________________
               LBA mode        |      RETRY_BUCKETS_ENABLE_LBA_FORMAT            |       0x01
                               |      RETRY_BUCKETS_ENABLE_ZERO_LATENCY          |       0x02
                               |      RETRY_BUCKETS_CONSTANT_SEED_SELECTED       |       0x04
               Default         |      RETRY_BUCKETS_ENABLE_DATA_COLLECTION       |       0x08
  """
  test = 1
  head = 0xffff
  cylinder = 0xffffffff
  mCylinder, lCylinder = __lwords(cylinder)
  buf, errorCode = fn(1374, head, lCylinder, mCylinder, Tlevel, mode)
  #__displayBuffer(buf)
  print "Length of buf = %d" % len(buf)
  if len(buf) == 222:#222 = 22 bytes of count data + 50 * 4 bytes of sector-specific data
     result = struct.unpack("LLLLLH",buf[0:22])
     print "Number of sectors Read with No Retries or On The Fly Correction: %d" % result[0]
     print "Number of sectors Read with No Retries but On The Fly Correction needed: %d" % result[1]
     print "Number of sectors Read with at least one but fewer than the threshold number of retries: %d" % result[2]
     print "Number of sectors that were Readable but required Threshold or more Retries: %d" % result[3]
     print "Number of sectors that were Unreadable: %d" % result[4]
     print "Sectors per Rev is: %d" % result[5]
     print ""
     #buffer offset of individual tracks
     i = 22
  elif len(buf) == 238 or len(buf) == 242:#238 = 38 bytes of count data + 50 * 4 bytes of sector-specific data
     if len(buf) == 238:
         result = struct.unpack("LLLLLLLLLH",buf[0:38])
     else:
         result = struct.unpack("LLLLLLLLLHHH",buf[0:42])
     print "Number of sectors Read with No Retries or On The Fly Correction: %d" % result[0]
     print "Number of sectors Read with No Retries but On The Fly Correction needed: %d" % result[1]
     print "Number of sectors Read with at least one but fewer than the threshold number of retries: %d" % result[2]
     print "Number of sectors that were Readable but required Threshold or more Retries: %d" % result[3]
     print "Number of sectors that were Unreadable: %d" % result[4]
     print "Number of Bits in Error: %d" % result[5]
     print "Number of CodeWords: %d" % result[6]
     print "Number of Non-Convergent CodeWords: %d" % result[7]
     print "Number of Sync Errors: %d" % result[8]
     print "Sectors per Rev is: %d" % result[9]
     if len(buf) == 242:
         print "Number of Sectors with Greater Than DOS Retry Count Retries: %d" % result[10]
         print "DOS Retry Count: %d" % result[11]
     print ""
     #buffer offset of individual tracks
     i = 38
  else:  #if the buff size is incorrect then something went wrong so just end
     return errorCode
  j = 0
  while i<len(buf):
    result = struct.unpack("HH",buf[i:i+4])
    i += 4
    j += 1
    if result[0] == 0:
      print "Sector %d" % result[0] + " OK "
      # break -- Remove break to allow zero cases to continue.
    else:
      if result[1] == 1:
        print "Sector %d" % result[0] + " is unreadable"
      elif result[1] == 2:
        print "Sector %d" % result[0] + " has soft error"
      elif result[1] == 3:
        print "Sector %d" % result[0] + " has hard error"
  return errorCode
####################################################################

def ujog(start_offset, end_offset, step_size, mode = "BER"):
  """
  Microjog: Measure BER or CQM versus offtrack percent on the ActiveHead, ActiveCylinder.
  Display offtrack, BER or CQM, Data Errors, Sync Errors, Other Errors, and Sense Code.
  @param start_offset: starting offtrack - OD side
  @param end_offset: ending offtrack - ID side
  @param step_size: offtrack step size
  @param mode: BER (default) or CQM to be used as the metric
  @return: Error code
  """
  errorCode = 0
  if (start_offset < -128) or (end_offset > 128):
    print "Offset out of range, +/-128 allowed (+/-50%)"
    return 0xFFFF
  if (start_offset > end_offset):
    print "Start must be less than end offset"
    return 0xFFFF
  offset = start_offset
  while end_offset >= offset and errorCode == 0:
    ofs(offset)
    offtrack = offset / 2.56
    if mode == "BER":
      buf, errorCode = fn(1342, 70, 0, 0)    # BER test
      #buf,errorCode = __ReceiveResults()
      result = struct.unpack("fHHHHLLLLL",buf)
      other_errors = result[3:4]
      print "Servo Offset: %3u" % offset + " Offtrack Pct: %7.3f" % offtrack + " BER: %5.2f" % (result[0:1]) + " Data Errors: %u " % (result[1:2]) + "Sync Errors: %u" % (result[2:3])
      if other_errors[0] > 0:
          print "Failed Sector = %u" % (result[6:7]) + "Sense Data = %x" % (result[5:6])
    else: # mode must be CQM
      cqmResult = cqmAgere(50,1) # Measure CQM over 50 sectors in quiet mode
      print "Servo Offset: %3u" % offset + " Offtrack Pct: %7.3f" % offtrack + " CQM: %7u" % cqmResult
    offset = offset + step_size
  return errorCode
####################################################################

def sweep(reg, start_val, end_val, step_size, mode = 0):
  """
  Run a sweep on input parm vs BER or CQM at the cudacom global head and cylinder values.
  Display Parm value tested, BER or CQM, Data Errors, Sync Errors, Other Errors, and Sense Code.
  @param start_val: starting parameter value
  @param end_val: ending parameter value
  @param step_size: step size
  @param mode: BER (0) or CQM (1) to be used as the metric, writes required (2) (def: BER, no writes)
  @return: Error code
  """
  global gHead
  global gCylinder
  global gZone

  errorCode = 0
  testMode = "BER"
  if (mode & 1) == 1:   # 0000 BER,  0001 CQM
      testMode = "CQM"
  numWrites = 0
  if (mode & 2) == 2:   # 0000 no writes,  0002 writes required
      numWrites = 1
  parmVal = start_val
  while parmVal < end_val and errorCode == 0:
      wrcf(reg, parmVal, gZone, gHead)
      if numWrites > 0:
          writetrack()
      if testMode == "BER":
          # Retire non-LDPC code (not used very often)
          #buf, errorCode = fn(1342, 70, 0, 0)    # BER test
          #buf,errorCode = __ReceiveResults()
          #result = struct.unpack("fHHHHLLLLL",buf)
          buf, errorCode = fn(1342, 0, 1, 0, 1, 24, 0x6)    # 0x6 = BER with data errors
          result = struct.unpack("fLLLLHHLL",buf)
          other_errors = result[4:5]
          print "Parm Value: %3u" % parmVal + " BER: %5.2f" % (result[0:1])
          if other_errors[0] > 0:
              print "Failed Sector = %u" % (result[6:7]) + "Sense Data = %x" % (result[5:6])
      else: # mode must be CQM
          cqmResult = cqmAgere(50,1) # Measure CQM over 50 sectors in quiet mode
          print "Parm Value: %3u" % parmVal + " CQM: %7u" % cqmResult
      parmVal = parmVal + step_size
  return errorCode
####################################################################

def readcont(startSector, numSectors, quietMode = 0, flag=0):
  """
  Execute the f/w ReadSectors function in continuous mode (ignores ECC errors)
  Display Sense Code and failed sector.
  @param startSector: Sector at which to start the reads.
  @param numSectors: Number of sectors to read
  @param quietMode: Supress sense data on PASS status of quiet mode not default or zero
  @param flag: 0 = Ignore Errors   1 = Stop On Error
  @return: Error code
  """
  buf, errorCode = fn(1343, startSector, numSectors, flag)
  #buf,errorCode = __ReceiveResults()
  result = struct.unpack("LL",buf)
  senseData = result[0:1]
  if quietMode == 0:    # Display sense data always if not quiet mode
      print "Sense Data = %x " % (result[0:1])
  if senseData[0] != 0x00000080:
      if quietMode == 0:
          print "Last Sector = %u" % (result[1:2])
      else:
          print "Sense Data = %x " % (result[0:1]) + "Last Sector = %u" % (result[1:2])
  return errorCode
####################################################################

def cqmAgere(numSectors, quietMode = 0):
  """
  Issue a read continuous and get the 24-bit channel quality monitor result
  @param numSectors: Number of sectors to read
  @param quietMode: Supress printing of CQM result if not default of zero
  @return: Channel quality monitor 24 bit result
  """
  # Set up quality monitor
  # QM_READ for RG1 only, Freeze QM_OVER, QM_MODE set to RMS error mode
  buf, errorCode = fn(1269, 0xe0, 0x5010)    # Write channel
  #buf,errorCode = __ReceiveResults()
  # Read continuous quiet mode
  readcont(0, numSectors, 1)
  # Read QM High
  buf, errorCode = fn(1308, 0xe3)            # Read Channel
  #buf,errorCode = __ReceiveResults()
  result = struct.unpack(">H",buf)
  cqmResult = result[0:1]
  qmRes = int(cqmResult[0])
  qmRes = qmRes << 8
  # Read QM Low
  buf, errorCode = fn(1308, 0xe4)            # Read Channel
  #buf,errorCode = __ReceiveResults()
  result = struct.unpack(">H",buf)
  cqmResultLow = result[0:1]
  qmResLow = int(cqmResultLow[0])
  qmRes += qmResLow     # Return 24-bit result
  if quietMode == 0:    # Print result if not quiet mode
      print "CQM = %u" % qmRes
  return qmRes
####################################################################

def rpreAPI(FeatureID):
  """
  Read Preamp Feature Value
  @param FeatureID: The preamp feature ID e.g: For Head Selection Bits of
	            Preamp PREAMP_HEAD_SELECTION feature ID = 3
  @return: Error code
  """
  buf, errorCode = fn(1329, FeatureID) #Read from the Preamp Register based on the Feature specified
  Result = struct.unpack('H',buf)

  if Result[0] == 0xFFFE:
      print"Invalid Feature ID"
  elif Result[0] == 0xFFFD:
      print"Servo Command Error"
  elif Result[0] == 0xFFFC:
      print"Unknown Error"
  else :
      print "dec: %u" % Result[0],
      print " hex: %02x" % Result[0] # Value of the feature within the register
  return errorCode
###################################################################

def rpre(RegisterNum):
  """
  Read Preamp Register Value
  @param RegisterNum: The Preamp register number to read from
  @return: Error code
  """
  buf, errorCode = fn(1391, RegisterNum) #Read from the Preamp Register based on the Feature specified
  Result = struct.unpack('HH',buf)

  if Result[0] == 0x0011:
      print"PREAMP_API_INVALID_REGISTER"
  elif Result[0] == 0x0012:
      print"PREAMP_API_SERVO_CMD_FAILED"
  elif Result[0] == 0x0013:
      print"PREAMP_API_SERVO_UNKNOWN_ERROR"
  elif Result[0] == 0x0016:
      print"PREAMP_API_ABORT"
  elif Result[0] == 0x0017:
      print"PREAMP_API_UNKNOWN_PREAMP"
  elif Result[0] != 0x0000:
      print"Unknown Error"
  else:
      print "dec: %u" % Result[1],
      print " hex: %02x" % Result[1] # Value of the feature within the register

  return errorCode
###################################################################

def getMFRName():
  """
  Read Preamp Manufacturer Name
  @return: Error code
  """
  buf, errorCode = fn(1389)
  Result = struct.unpack('BB',buf)

  if Result[0] == 0xE8:
	print "Manufacturer Name: LSI"
  if Result[0] == 0x9D:
	print "Manufacturer Name: TI"
  return errorCode
####################################################################

def wpreAPI(FeatureID, Data):
  """
  Write Preamp Feature Value
  @param FeatureID: The preamp feature ID e.g: For Head Selection Bits of
	                Preamp PREAMP_HEAD_SELECTION feature ID = 3
  @param Data: The data to be written into the preamp register
  @return: Error code
  """
  buf, errorCode = fn(1330, FeatureID, Data) #Write to Preamp Register based on the Feature specified
  Result = struct.unpack('H',buf)

  if Result[0] == 0xFFFE:
      print"Invalid Feature ID"
  elif Result[0] == 0xFFFD:
      print"Servo Command Error"
  elif Result[0] == 0xFFFC:
      print"Unknown Error"
  elif Result[0] == 0xFFFB:
      print"Read Only Registers, Writes not allowed"
  else :
      rpreAPI(FeatureID)
  return errorCode
####################################################################

def wpre(RegisterNum, RegisterData):
  """
  Write Preamp Register Value
  @param RegisterNum: The Preamp register number to read from
  @param RegisterNum: The Data to write to the preamp register
  @return: Error code
  """
  buf, errorCode = fn(1392, RegisterNum, RegisterData) #Read from the Preamp Register based on the Feature specified
  Result = struct.unpack('H',buf)

  if Result[0] == 0x0011:
      print"PREAMP_API_INVALID_REGISTER"
  elif Result[0] == 0x0012:
      print"PREAMP_API_SERVO_CMD_FAILED"
  elif Result[0] == 0x0013:
      print"PREAMP_API_SERVO_UNKNOWN_ERROR"
  elif Result[0] == 0x0014:
      print"PREAMP_API_WRITE_TO_READ_ONLY_LOCATION"
  elif Result[0] == 0x0015:
      print"PREAMP_API_WRITE_FAILED"
  elif Result[0] == 0x0016:
      print"PREAMP_API_ABORT"
  elif Result[0] == 0x0017:
      print"PREAMP_API_UNKNOWN_PREAMP"
  elif Result[0] != 0x0000:
      print"Unknown Error"
  else:
     rpre(RegisterNum)
  return errorCode
###################################################################

def dumpPreamp(StartAddress=0,EndAddress=31, BytesPerReg=1):
  """
  Dump Preamp registers
  @param StartAddress: Starting preamp register
  @param EndAddress: Ending preamp register, defaulted to 31, set to >= 32 for dumping the second page of 64 preamps
  @return: Error code
  """
  buf, errorCode = fn(1332, StartAddress, EndAddress)
  __displayMemory(buf,StartAddress,BytesPerReg)
  return errorCode

####################################################################

def enableChannelDefectScan (defectLength, UpperThreshold, LowerThreshold, TAThreshold, enableOrRestore, enableTADetection, NRZDivisor):
   """
   Enable or Disable the Channel Defect Scan
   @param defectLength: Defect Length sent R1:3B[5:0]
   @param UpperThreshold: Drop out, amplitude loss threshold
   @param LowerThreshold: Drop in, amplitude gain
   @param TAThreshold: The TA threshold
   @param enableOrRestor: 0 for enable or 1 for restore
   @param enableTADetection: 0 to disable or 1 to enable
   @param NRZDivisor: Drive SoC specific [8:0] so must be between 511 and 1
   @return: Error code
   """
   if NRZDivisor < 1 or NRZDivisor > 511:
      print "Invalid NRZDivisor %d - must be between 1 and 511" % NRZDivisor
      return 
   buf, errorCode=fn(1394, defectLength, UpperThreshold, LowerThreshold, TAThreshold, enableOrRestore, enableTADetection, NRZDivisor)
   return errorCode

###################################################################

def rpref(preampFeatureID):
  """
  Read Preamp Feature from the Preamp
  @param preampFeatureID: Preamp feature to read
  @return: Error code
  """
  buf, errorCode = fn(1347, preampFeatureID)
  #__displayBuffer(buf)
  result = struct.unpack("BB",buf)
  status = result[0:1]
  print "dec: %u " % (result[1:2]) + "hex: %x " % (result[1:2])
  if status[0] != 0:   # 0 is PASS
    print "Read Preamp Failed, status = %x" % (result[0:1])
  return errorCode

####################################################################

def wpref(preampFeatureID, value):
  """
  Write Preamp Feature from the Preamp
  @param preampFeatureID: Preamp feature to write
  @param value: Value to write to preamp feature
  @return: Error code
  """
  buf, errorCode = fn(1348, preampFeatureID, value)
  result = struct.unpack("BB",buf)
  status = result[0:1]
  if status[0] != 0:   # 0 is PASS
    print "Write Preamp Failed, status = %x" % (result[0:1])
  rpref(preampFeatureID)
  return errorCode

####################################################################

def reloadRap(type=0, option=0, SectorSize = 512):
  """
  Reload RAP
  @param type: ::
            0 (default): (RW_NORMAL_TRACK_FORMAT_TYPE) Multiple sectors per wedge with splits
            1:           (RW_NO_SPLIT_SECTOR_TRACK_FORMAT_TYPE) Multiple sectors per wedge without splits
            2:           (RW_SINGLE_SECTOR_PER_WEDGE_TRACK_FORMAT_TYPE) Single sector per wedge format type
  @param option: ::
            0 (default): (RW_NO_TRACK_FORMAT_CHANGE) Use existing track formats
            1:           (RW_UPDATE_TRACK_FORMAT_WITH_NO_TYPE_CHANGE) Recalculate track format, without format type change.
            2:           (RW_UPDATE_TRACK_FORMAT_WITH_SPECIFIED_TYPE) Recalculate track format, based on specified track format type.
  @param type:
  @param SectorSize:     Sector size in bytes
  @return: Error code
  """
  buf, errorCode = fn(1333, type, option, SectorSize)
  #buf,errorCode = __ReceiveResults()
  return errorCode
####################################################################

def setEccLevel(level=30):
  """
  Set Override ECC Level and enable override.
  @param level: Override ECC level 0..30 (default=30)::
     DISABLE_ECC  = 0,           // T Level 0
     TLEVEL_2     = 2,           // T Level 2
     TLEVEL_4     = 4,           // T Level 4
     TLEVEL_6     = 6,           // T Level 6
     TLEVEL_8     = 8,           // T Level 8
     TLEVEL_10    = 10,          // T Level 10
     TLEVEL_12    = 12,          // T Level 12
     TLEVEL_14    = 14,          // T Level 14
     TLEVEL_16    = 16,          // T Level 16
     TLEVEL_18    = 18,          // T Level 18
     TLEVEL_20    = 20,          // T Level 20
     TLEVEL_22    = 22,          // T Level 22
     TLEVEL_24    = 24,          // T Level 24
     TLEVEL_26    = 26,          // T Level 26
     TLEVEL_28    = 28,          // T Level 28
     TLEVEL_30    = 30           // T Level 30
  @return: Error code
  """
  if ((level % 2) != 0) or (level > 30):
      print "Invalid TLevel Entered!  ECC Level not changed!"
      return
  buf, errorCode = fn(1334, level)
  #buf,errorCode = __ReceiveResults()
  return errorCode
####################################################################

def restoreEccLevel():
  """
  Restore ECC to normal operation, e.e, disable ECC override.
  No parameters
  @return: Error code
  """
  buf, errorCode = fn(1335)
  #buf,errorCode = __ReceiveResults()
  return errorCode
####################################################################

def disableEcc():
  """
  Disable ECC
  No parameters
  @return: Error code
  """
  buf, errorCode = fn(1334, 0)
  #buf,errorCode = __ReceiveResults()
  return errorCode
####################################################################

def writetrack():
  """
  Write the current track
  @return: Error code
  """
  buf, errorCode = fn(1355)
  #buf,errorCode = __ReceiveResults()
  __displayBuffer(buf)
  return errorCode
####################################################################

def lwritetrack(LoopWriteCount=1,WriteFlag=0,StopOnError=0):
  """
  Write current track with the following options
  @param LoopWriteCount: Number of loop to write
  @param WriteFlag: To access the low level write flag option
  @param StopOnError: If set to 1 , will stop on write error
  @return: Error code
  """
  buf, errorCode = fn(1373,LoopWriteCount,WriteFlag,StopOnError)
  __displayBuffer(buf)
  return errorCode
####################################################################

def readtrack(StopOnError=0):
  """
  Read the current track
  @param StopOnError: If set to 1, will stop on read error
  @return: Error code
  """
  buf, errorCode = fn(1356,StopOnError)
  #buf,errorCode = __ReceiveResults()
  __displayBuffer(buf)
  return errorCode
####################################################################

def lreadtrack(LoopReadCount=1,ReadFlag=0,StopOnError=0):
  """
  Read current track with the following options
  @param LoopReadCount: Number of loop to write
  @param ReadFlag: To access the low level read flag option
  @param StopOnError: If set to 1, will stop on read error
  @return: Error code
  """
  buf, errorCode = fn(1377,LoopReadCount,ReadFlag,StopOnError)
  #buf,errorCode = __ReceiveResults()
  __displayBuffer(buf)
  return errorCode
####################################################################

def DCEraseTrack():
  """
  DCErase the current track
  @return: Error code
  """
  buf, errorCode = fn(1250, 0)
  #buf,errorCode = __ReceiveResults()
  __displayBuffer(buf)
  return errorCode
####################################################################

def ACEraseTrack():
  """
  ACErase the current track
  @return: Error code
  """
  buf, errorCode = fn(1250, 1)
  #buf,errorCode = __ReceiveResults()
  __displayBuffer(buf)
  return errorCode
####################################################################

def dumpBank(bank=0):
  """
  Dump the specified channel registers bank
  @param bank: Bank number to dump
  @return: Error code
  """
  buf,errorCode = fn(1324,bank)
  #buf,errorCode = __ReceiveResults()
  print "Bank %xh" % bank
  __displayMemory(buf, 0, addressableUnit=2)
  return errorCode

####################################################################

def dumpChannel():
  """
  Dump the channel registers to stdout: Reg 0x80:0xFF
  @return: Error code
  """
  buf,errorCode = fn(1325)
  #buf,errorCode = __ReceiveResults()
  return errorCode
####################################################################

def DLResultsFile(fileName,fileLen=0):
  """
  Download the input file to the drive and store process SIM. Uses st(231).
  @param fileName: FilePth to download
  @param fileLen: Optional length of file to download must be <= len(file)
  """
  global FileLength, FileObj

  try:
    FileLength = fileLen   # copy local value to global
    print "Downloading SPT file %s to drive ..." % FileName
    if FileLength == 0:
      if not os.path.isfile(FileName):
        msg = "Missing File: %s" % FileName
        print msg
        raise FOFFileIsMissing,msg
      else:
        FileLength = os.stat(FileName)[stat.ST_SIZE]

    print "DL file len = " , FileLength
    FileObj = open(FileName,"rb")
    print "File %s open OK" % FileName

    # intercept request key 16 from core code
    RegisterResultsCallback(processRequest16, 16, 0)

    st(231,CWORD1=0, DL_FILE_LEN=(FileLength>>16, FileLength & 0x0000ffff),timeout=3600)

    FileObj.close()

    #release the interception
    RegisterResultsCallback(0, 16, 0)

  except:
    print "Cannot download results file!!"
####################################################################

def DLAfhFile(fileName,fileLen=0):
  """
  Download the AFH SIM file in binary format to the drive and store process SIM. Uses st(231).
  @param fileName: FilePth to download
  @param fileLen: Optional length of file to download must be <= len(file)
  """
  global FileLength, FileObj

  try:
    FileLength = fileLen   # copy local value to global
    print "Downloading AFH file %s to drive ..." % FileName
    if FileLength == 0:
      if not os.path.isfile(FileName):
        msg = "Missing File: %s" % FileName
        print msg
        raise FOFFileIsMissing,msg
      else:
        FileLength = os.stat(FileName)[stat.ST_SIZE]

    print "DL file len = " , FileLength
    FileObj = open(FileName,"rb")
    print "File %s open OK" % FileName

    # intercept request key 16 from core code
    RegisterResultsCallback(processRequest16, 16, 0)

    st(231,CWORD1=0x10, DL_FILE_LEN=(FileLength>>16, FileLength & 0x0000ffff),timeout=3600)

    FileObj.close()

    #release the interception
    RegisterResultsCallback(0, 16, 0)

  except:
    print "Cannot download AFH file!!"
####################################################################

#def UploadResultsFile(*args):
   # TO BE IMPLEMENTED
####################################################################

def DLCurrResultsFile():
  """
  Download the binary process results file to the drive and store process SIM. Uses st(231).
  """
  global FileLength, ResultsFile, FileObj

  try:

     ResultsFile.open()
     ResultsFile.seek(0,2)  # Seek to the end
     FileLength = ResultsFile.tell()
     ResultsFile.seek(0)    # Seek to the start
     print "DL file len = " , FileLength

     FileObj = ResultsFile  # pass the file object to processRequest16
     # intercept request key 16 from core code
     RegisterResultsCallback(processRequest16, 16, 0)

     st(231,CWORD1=0, DL_FILE_LEN=(FileLength>>16, FileLength & 0x0000ffff),timeout=3600)

     ResultsFile.close()

     #release the interception
     RegisterResultsCallback(0, 16, 0)

  except:
     str = "Cannot download results file!!"
     raise ScriptTestFailure,str
###########################################################################

def processRequest16(requestData, *args, **kargs):
  """
  Process callback for handling of block code requests for test 231 call.
  Uses FileLength and FileObj globals to reference the dlfile.
  FileLength must be = the parameter passed to the drive in the st(231) call.
  """
  # requestData is a string from the UUT asking for a block from a file
  # return a frame, raise an exception on error

  #if not self.dlfile:
  #  msg = "Drive requests file data but there is no dlfile."
  #  raise FOFFileIsMissing,msg
  # print "fl, fobj = " , FileLength, FileObj

  requestKey = ord(requestData[0])
  # code 6 typically requests a block of data from the download file;  get_data_file()
  if requestKey == 16:
    blockSize = (int(ord(requestData[3]))<<8) + int(ord(requestData[2]))
    requestHI = requestData[5]
    requestLO = requestData[4]
    requestBlock = (int(ord(requestHI))<<8) + int(ord(requestLO))
  else:
    str = "Unsupported requestKey in processRequest16==>",requestKey
    raise FOFParameterError,str

  # look up the file size, and validate the block request
  #fileSize = self.getFileSize()
  fileSize = FileLength # a global from above

  # *Every* file has a last block called the runt block, and the runt block will be sized from 0 to (blockSize-1) (e.g. 0 to 511)
  # It is legal for the firmware to request the runt block, but no blocks beyond that.
  # If the firmware requests the runt block, we'll read a partial block from the file, and set the 'notAFullRead' flag in the response packet.
  runtBlock = fileSize / blockSize
  runtSize = fileSize % blockSize

  #print "Sending Block: %d of %d"%(requestBlock+1, runtBlock) #YWL:DBG

  #if (self.ScriptEnv.DebugMode==2):
  #print "Sending results block: %d of %d"%(requestBlock+1, runtBlock)
     #if (requestBlock+1 == runtBlock):
        #print "Sent Block: %d of %d. Waiting for Reset..."%(requestBlock+1, runtBlock)

  if requestBlock < runtBlock:
    readSize = blockSize
    notAFullRead = chr(0)
  elif requestBlock == runtBlock:
    readSize = runtSize
    notAFullRead = chr(1)
  else:
    str = "processRequest16(): Request for block %s is beyond than last block %s." % (requestBlock,runtBlock)
    raise FOFParameterError,str

  # read from their file
  #fileObj = self.dlfile[FILEOBJ]
  fileObj = FileObj
  fileObj.seek(requestBlock*blockSize)
  data = fileObj.read(readSize)

  returnData = requestData[0] + notAFullRead + requestLO + requestHI + data

  SendBuffer(returnData)
  #return returnData
###########################################################################

def getVisMux():
  """
  Display the AGERE Vismux test output registers.
  @return: Error code
  """
  buf, errorCode = fn(1358,0xFF,0)
  #buf,errorCode = __ReceiveResults()
  displayVisMux(buf)
  return errorCode
###########################################################################

def setVisMux(visMuxNum = None, signalName = None):
  """
  Set the AGERE Vismux test output pins to the requested output signal.
    - Abstraction stub based on cudacom 1358 by Scott States.
    - Current Implementation based on Delta Channel
    - Default input's will return the list of valid signal names to program the mux's to.
  @param visMuxNum: VisMux output pin to tie controller value to. Use 0xFF to just read the vis mux registers.
  @param signalName: Name or value of controller output to tie to the specified pin. 0xFF disables the output.
  @return: Error code
  """

  nameAbs = {
'NRZ(0)':   0,
'NRZ(1)':   1,
'NRZ(2)':   2,
'NRZ(3)':   3,
'NRZ(4)':   4,
'NRZ(5)':   5,
'NRZ(6)':   6,
'NRZ(7)':   7,
'NRZ(8)':   8,
'NRZ(9)':   9,
'ReadGate': 10,
'WriteGate':   11,
'ServoGate':   12,
'SDATA(channel)': 13,
'SCLK(channel)':  14,
'SDEN(channel)':  15,
'RCLK':  16,
'ErasureFlag': 17,
'SRVOUT1P': 18,
'ChannelDoze': 19,
'HDAWG': 20,
'InternalErasure Flag': 21,
'SRVOUT0P': 22,
'PBM_DIAG_BUS(0)':   23,
'PBM_DIAG_BUS(1)':   24,
'PBM_DIAG_BUS(2)':   25,
'PBM_DIAG_BUS(3)':   26,
'PBM_DIAG_BUS(4)':   27,
'PBM_DIAG_BUS(5)':   28,
'PBM_DIAG_BUS(6)':   29,
'PBM_DIAG_BUS(7)':   30,
'PPS_DIAG_BUS(0)':   31,
'PPS_DIAG_BUS(1)':   32,
'PPS_DIAG_BUS(2)':   33,
'PPS_DIAG_BUS(3)':   34,
'PPS_DIAG_BUS(4)':   35,
'PPS_DIAG_BUS(5)':   36,
'PPS_DIAG_BUS(6)':   37,
'PPS_DIAG_BUS(7)':   38,
'CF_DIAG_BUS(0)': 39,
'CF_DIAG_BUS(1)': 40,
'CF_DIAG_BUS(2)': 41,
'CF_DIAG_BUS(3)': 42,
'CF_DIAG_BUS(4)': 43,
'CF_DIAG_BUS(5)': 44,
'CF_DIAG_BUS(6)': 45,
'CF_DIAG_BUS(7)': 46,
'AETOS_DIAG_BUS(0)': 47,
'AETOS_DIAG_BUS(1)': 48,
'AETOS_DIAG_BUS(2)': 49,
'AETOS_DIAG_BUS(3)': 50,
'AETOS_DIAG_BUS(4)': 51,
'AETOS_DIAG_BUS(5)': 52,
'AETOS_DIAG_BUS(6)': 53,
'AETOS_DIAG_BUS(7)': 54,
'TC_DIAG_BUS(0)': 55,
'TC_DIAG_BUS(1)': 56,
'TC_DIAG_BUS(2)': 57,
'TC_DIAG_BUS(3)': 58,
'TC_DIAG_BUS(4)': 59,
'TC_DIAG_BUS(5)': 60,
'TC_DIAG_BUS(6)': 61,
'TC_DIAG_BUS(7)': 62,
'SP_DIAG_BUS(0)': 63,
'SP_DIAG_BUS(1)': 64,
'SP_DIAG_BUS(2)': 65,
'SP_DIAG_BUS(3)': 66,
'SP_DIAG_BUS(4)': 67,
'SP_DIAG_BUS(5)': 68,
'SP_DIAG_BUS(6)': 69,
'SP_DIAG_BUS(7)': 70,
'CLKRST_DIAG_BUS(0)':   71,
'CLKRST_DIAG_BUS(1)':   72,
'CLKRST_DIAG_BUS(2)':   73,
'CLKRST_DIAG_BUS(3)':   74,
'CLKRST_DIAG_BUS(4)':   75,
'CLKRST_DIAG_BUS(5)':   76,
'CLKRST_DIAG_BUS(6)':   77,
'CLKRST_DIAG_BUS(7)':   78,
'HOST_DIAG_BUS(0)':  79,
'HOST_DIAG_BUS(1)':  80,
'HOST_DIAG_BUS(2)':  81,
'HOST_DIAG_BUS(3)':  82,
'HOST_DIAG_BUS(4)':  83,
'HOST_DIAG_BUS(5)':  84,
'HOST_DIAG_BUS(6)':  85,
'HOST_DIAG_BUS(7)':  86,
'ChannelNRZ(10)': 87,
'ChannelNRZ(11)': 88,

  }

  if visMuxNum == None and signalName == None:
    print("Output Options available...")
    mKeys = nameAbs.keys()
    mKeys.sort()
    for key in mKeys:
      print(str(key))
    return None

  if type(signalName) == types.IntType or \
    type(signalName) == types.IntType:
      setSig = signalName
  else:
    try:
      setSig = nameAbs[signalName]
    except KeyError:
      print("Invalid ouput signal entered.")
      return None

  print("Setting visMux: %d to %s" % (visMuxNum,str(signalName)))
  buf, errorCode = fn(1358,visMuxNum,setSig)
  #buf,errorCode = __ReceiveResults()
  displayVisMux(buf)
  return errorCode
###########################################################################

def logver( cyl, code_hd, pos, len, pattern):
  """
  Log Verified Defect - Add verified defects to the DBI log

  @param cyl:      [31:0]
  @param code_hd:  [15:0] where -
                   -Code[15:8] is: 1=Data, 2=Servo, 3=TA
                   -Head Number [7:0]
  @param pos:     [15:0] (In symbols, not bytes!)
  @param len:     [15:0] (In symbols, not bytes!)
  @param pattern: [15:0]

  @return: Error code
  """
  mCylinder, lCylinder = __lwords(cyl)
  mPosition, lPosition = __lwords(pos)
  buf,errorCode = fn(1322, mCylinder, lCylinder, code_hd, mPosition, lPosition, len, pattern)
  #buf,errorCode = __ReceiveResults()
  __displayBuffer(buf)
  return errorCode
###########################################################################

def xlateWOtoSFI( wedge, offset, cyl, head ):
  """
  Translate Wedge/Offset to Symbols-from-Index -
  Convert a wedge number and an offset (in symbols) to
  the number of symbols from index.
  Display Symbols from Index [31:0].

  Note: offset is from forced sync mark

  @param wedge:  Wedge Number[15:0]
  @param offset: Offset[15:0] (In symbols, not bytes!)
  @param cyl:    Cylinder[31:0]
  @param head:   Head[15:0]

  @return: Error code
  """
  mCyl, lCyl = __lwords(cyl)
  buf,errorCode = fn(1321, wedge, offset, mCyl, lCyl, head)
  #buf,errorCode = __ReceiveResults()
  __displayBuffer(buf)
  return errorCode
###########################################################################

def xlateSFItoWO( sfi, cyl, head ):
  """
  Translate Symbols-from-Index to Wedge/Offset -
  Convert the number of symbols from index to its
  corresponding wedge number plus remaining offset.

  Display Wedge Number[15:0], Offset[15:0] (In symbols, not bytes!)

  Note: offset is from forced sync mark

  @param sfi:  Symbols-From-Index[31:0]
  @param cyl:  Cylinder[31:0]
  @param head: Head[15:0]

  @return: Error code
  """
  mCyl, lCyl = __lwords(cyl)
  mSfi, lSfi = __lwords(sfi)
  head = head | 0x8000     #sets mode bit
  buf,errorCode = fn(1321, mSfi, lSfi, mCyl, lCyl, head)
  #buf,errorCode = __ReceiveResults()
  __displayBuffer(buf)
  return errorCode
###########################################################################

def ReadCLParm(listid, regadrs, shiftval, maskval):
  """
  Read channel parameter from selected channel list.
  Note: Refer to channelSetupLists.c for specific
  list and parameter values.

  Display parameter value currently stored in channel list.

  @param listid:   Channel list ID (index)
  @param regadrs:  Channel register address
  @param shiftval: Parameter shift value (0, 1, 2, 3, ...)
  @param maskval:  Parameter mask (1, 3, 5, 7, ...)

  @return: Error code
  """

  buf, errorCode = fn(1359, 0, listid, regadrs, shiftval, maskval)
  #buf,errorCode = __ReceiveResults()
  __displayBuffer(buf)
  return buf
###########################################################################

def WriteCLParm(listid, regadrs, shiftval, maskval, newval):
  """
  Write channel parameter to selected channel list.
  Note: Refer to channelSetupLists.c for specific
  list and parameter values.

  Display new value written.

  @param listid:   Channel list ID (index)
  @param regadrs:  Channel register address
  @param shiftval: Parameter shift value (0, 1, 2, 3, ...)
  @param maskval:  Parameter mask (1, 3, 5, 7, ...)
  @param newval:   Parameter value to be stored in channel list
  @return: Error code
  """

  buf, errorCode = fn(1359, 1, listid, regadrs, shiftval, maskval, newval)
  #buf,errorCode = __ReceiveResults()
  ReadCLParm(listid, regadrs, shiftval, maskval)     ## echo it back
  return errorCode
####################################################################

def SetDebugMux(MuxSelect,SignalNumber):
  """
  Set the specified Tycho debug mux output to the specified Tycho debug mux input signal number.
  Display all debug muxes after specified mux is setup.
  Display 8 debug mux values (bytes) as a binary string.
  @param MuxSelect: Mux Select Number (0..7); 0xFFFF forces read-only
  @param SignalNumber: Signal Number (0..63, refer to the Tycho Debug Mux Spec)
  @return: Error code
  """
  buf,errorCode = fn(1360, MuxSelect, SignalNumber)
  #buf, errorCode = __ReceiveResults()

  data = binascii.hexlify(buf)
  print "Debug Mux   Signal\n",
  print "Select No.  Number\n",
  for i2 in range(0,len(data),2):
    print '%02x          ' % (i2/2),
    print data[i2:i2+2],
    print "\n",
  return errorCode
####################################################################

def GetDebugMux():
  """
  Read and display the Tycho debug mux settings.
  @return: Error code
  """
  return SetDebugMux(0xFFFF,0)
####################################################################

def Set8830DebugMux(SigNumber=0):
  """
  Set the 8830 debug mux to display SOC level signals on the HS_DIAG_XX pins
  @param SigNumber:  Number between 0-4
  @return: Error code
  """

  # check that setting is between 0 and 4, per Marvell spec
  if SigNumber > 4 or SigNumber < 0 :
    print "SigNumber %d" % SigNumber + " is invalid. Must be >= 0 and <= 4"
    return
  else:
    buf,errorCode = fn(1381, SigNumber, )

  return errorCode
####################################################################

def Get8830DebugMux ():
  """
  Display 8830 debug mux
  @return: Error code
  """
  buf,errorCode = fn(1382)
  result = struct.unpack("BB",buf[0:2])
  print "mux: 0x%x" % result[0]

  return errorCode

####################################################################
def setaux(aux = 1, varaddr = None, shift = 0, dispmode = 0):

  """
  Selects the specified output signal to be displayed on the
  specified Mirkwood output pin
  @param aux:      AUX port to set
  @param varaddr:  Address of the display signal from the servo symbol table
  @param shift:    Number of shifts to apply to the signal value
  @param dispmode: Display mode default
                      0 (track follow)
                      1 (velocity)
                      2 (track width?)
  @return: Error code
  """

  if varaddr == None:
    print("Signal address number must be entered...")
    return

  if type(varaddr) != int:
    print("Invalid ouput signal address...")
    return

  if ((dispmode <= 2) and (aux <= 4) and (aux > 0 )):
    buf,errorCode = fn(1363, aux, varaddr, shift, dispmode)
    #buf,errorCode = __ReceiveResults()
    print("SetAux: %d to 0x%x" % (aux,varaddr))
  else:
    print("Invalid mode or port entered.")
  return errorCode
###########################################################################

def dspzt(head=0):
  """
  Display Zone Table for head specified by the input param, including 4 items at present:
  Head     Zone#       StartCyl        EndCyl
  Item "Head" will display only when VBAR supported.
  @param head: limited by buffer size, it displays zone table for only one head each time when VBAR supported.
  @return: Error code
  """
  buf, errorCode = fn(1361, head)
  #buf,errorCode = __ReceiveResults()

  firstbyte = struct.unpack('BB',buf[0:2])
  head, zone = firstbyte
  if head == 255:        #!VBAR_SUPPORT
    print "    \tZONE#\t\tStartCYL\t\tEndCYL"
  elif head == 127:
    print "input value is too large"
    return buf
  else:                  #VBAR_SUPPORT
    print "Head\tZONE#\t\tStartCYL\t\tEndCYL"

  for i in range(0, len(buf), 10):
    line1 = struct.unpack('BB', buf[i : i+2])    #'BBLL' does not work, so split it into two lines
    hd, zn = line1
    line2 = struct.unpack('LL', buf[i+2 : i+10])
    starCyl, endCyl = line2
    if hd == 255:
      print " ",
    else:
      print hd,
    print "\t",zn,"\t\t",starCyl,"\t\t\t",endCyl
  return errorCode

####################################################################

def swdErrorRate (startCyl, endCyl, head):
  """
  Measure the skip write detect error rate across a range of cylinders. Randomly seeks from
  startCyl to endCyl on input head and writes each track and looks for skip write detect errors.
  @param startCyl: Defines the starting range of cylinders to test
  @param endCyl: Defines the end range of cylinders to test
  @param head: Head to test
  @return: Error code
  """
  mstartCyl, lstartCyl = __lwords(startCyl)
  mendCyl, lendCyl = __lwords(endCyl)
  buf, errorCode = fn(1344, lstartCyl, mstartCyl, lendCyl, mendCyl, head)
  #buf,errorCode = __ReceiveResults(320)
  swdData = struct.unpack("fhhhhL",buf)
  print "Skip Write Detect Error Rate =  %f" % (swdData[0:1]) + "      Error Counts:"
  print "dVgas = %u" % (swdData[1:2]) + "  rVgas = %u" % (swdData[2:3]) + "  fVgas = %u" % (swdData[3:4]) + \
        "  Other Write Errors = %u" % (swdData[4:5])
  print "Last Non-SWD Sense Code = %x" % (swdData[5:6])
  if errorCode != 0:
      print "Test Failed !!!"
  return errorCode

####################################################################

def setFlyHeight (cylinder, head, flyHeightPct = 0, options = "W"):
  """
  Sets the fly height as a percentage from nominal. Sets the vars in the
  working AFH table.
  @param cylinder: Cylinder to set the fly height on
  @param head: Head to set the fly height on
  @param flyHeightPct: Percentage delta from nominal to set the fly height (50 = 50%)
  @param options: Set the write fly height "W", read fly height "R", or both "RW", prepend "S" for system area
                  for example "SW" for system area write fly height and "SRW" system area both.
  @return: Sense Data
  """
  mstartCyl, lstartCyl = __lwords(cylinder)
  if (flyHeightPct > 128) or (flyHeightPct < -100):
      print "Fly height percent entered is out of range!!! Command Failed!!!"
      print "Fly Height Value is an 8-bit signed integer with a f/w enforced min of nominal - 40%"
      return
  if options == "R":
      flag = 1
  elif options == "W":
      flag = 2
  elif options == "RW":
      flag = 3
  elif options == "SR":
      flag = 5
  elif options == "SW":
      flag = 6
  elif options == "SRW":
      flag = 7
  else:
      print "Invalid option flag entered!"
      print "Valid options are R, W, RW, SR, SW, and SRW, see documentation"
      return
  buf, errorCode = fn(1345, lstartCyl, mstartCyl, head, flyHeightPct, flag)
  #buf,errorCode = __ReceiveResults()
  fhData = struct.unpack("L",buf)
  print "Sense Code = %x" % (fhData[0:1])
  if errorCode != 0:
      print "Test Failed !!!"
  return errorCode

####################################################################

def sectorRead (startSector = 0, numberOfSectors = 1):
  """
  Read the the sectors specified by startSector and numberOfSectors at
  the current cylinder and head position as specified by the last seek.
  It displays the error counts per sector. Each sector is read one at a time.
  @param startSector: Defines the starting sector to begin reading
  @param numberOfSectors: Defines the number of sectors to read
  @return: Sense data
  """
  # Call SingleSectorErrorRate
  buf, errorCode = fn(1346, startSector, numberOfSectors)
  formatString = 'hhhhLL'
  formatString *= numberOfSectors
  retData = struct.unpack(formatString,buf)
  print "Sector   VGAR    Hard Error    OTF Count    Sense Code       Pad"
  for n in range(0,numberOfSectors,1):
        i = n * 6
        print "    %u" % (retData[i:i+1]) + "     %u  " % (retData[i+1:i+2]) + "      %u       " % (retData[i+2:i+3]) + \
        "     %u    " % (retData[i+3:i+4]) + "       %.8x" % (retData[i+4:i+5]) + "         %u" % (retData[i+5:i+6])
  print "Return Code = %u" % errorCode
  return errorCode

####################################################################

def howareyou():
  """
  To check if the drive is in Flashing LED state. Drive should respond string
  "FINE!" if it's not in flashing LED state, and will respond a string with
  fail code and address if in flashing LED state.
  @return: Error code
  """
  buf,errorCode = buf, errorCode = fn(9900, timeout = 2)
  ##buf,errorCode = __ReceiveResults()
  print buf
  return errorCode
####################################################################

def setEchoServoCmdOn( enable = 1 ):
  """
  Enable a flag in SF3 code to echo every servo command sent to servo.
  Bit 0: enables / disables Echo Servo Command.
  Bit 1: enables / disables filtering Servo memory access command display (servo cmd 0xXX01)
  Both bits 0 and 1 must be set to enable display filter
  It will be direct output to WinFOF with following format:
  SRVO: xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx
        xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx
  @return: Error code
  """
  buf,errorCode = fn(9901,enable)
  #buf,errorCode = __ReceiveResults()

  if errorCode == 0:
     print "Echo Servo Command ON"
  return errorCode
####################################################################

def matlab():
  """
  Start the matlab shell. The matlab shell replaces the controller
  firmware executing on the drive, and takes over the serial port.
  This effectively disables the cudacom interface, and you must
  shut down the current application (typically WinFOF) and run matlab
  to communicate with the drive.

  This command will spin down the drive if necessary before starting
  the matlab shell.

  @return: Nothing. The Matlab shell controls the serial interface.
  """
  fn(9902, receive = 0)
  print "The Matlab shell has been started. Close this application to avoid COM port conflicts.\n"
  return
####################################################################

def setEchoServoCmdOff():
  """
  Disable the servo command echo
  @return: Error code
  """
  buf,errorCode = fn(9901,0)
  #buf,errorCode = __ReceiveResults()

  if errorCode == 0:
     print "Echo Servo Command OFF"
  return errorCode
####################################################################

def AddServoFlaw( cylinder, head, wedge, saveToDisc = 0):
  """
  Add a servo flaw to the Active Servo Flaw Table (ASFT).  This does not add a servo flaw to the
  System Servo Flaw List on the disc.
  @param cylinder: Cylinder for added servo flaw
  @param head: Head for added servo flaw
  @param wedge: wedge for added servo flaw
  @return: Error code
  """

  mCylinder, lCylinder = __lwords(cylinder)
  buf, errorCode = fn( 1314, mCylinder, lCylinder, head, wedge, saveToDisc)
  #buf,errorCode = __ReceiveResults()
  __displayBuffer(buf)
  return errorCode
####################################################################

def GetMonitorData(skip_sectors=0, channel=AGERE):
  """
  Collect and display standard monitored data parameters for a full track of burst data.
  Ignore the first skip_sectors of data to allow VGA and TAPs to adjust.
  Standard data includes QM, VGAR and Fir Tap values. This command assumes that the format
  is set for single sector per wedge (reloadRap(2,2)).
  @param skip_sectors: Number of initial sectors to ignore to allow for TAPs to settle
  @param channel: Set to 0 for Agere/LSI by default, change to 1 to display Marvell
  @return: Error code
  """
  buf, errorCode = fn( 1364 )
  #buf,errorCode = __ReceiveResults()
  if errorCode != 0:
   result = struct.unpack("4B", buf[2:6])
   print " Sense Code: %X" % result[0] + "  %X" % result[1] + "  %X" % result[2]+ "  %X" % result[3]
  else:
   QM = []
   VGAR = []

   if channel == 1:
    print "\nBURST\t\tQM\t\tD_AGC_GAIN\tFIR"
   else:
    print "\nBURST\t\tQM\t\tVGAR\t\tFIR"
   print   "-----\t\t--\t\t----\t\t---"
   for i in range(skip_sectors*8,len(buf),8):
      burst = i/8
      result = struct.unpack("LHH",buf[i : i+8])
      print "%03X" % burst + "\t\t%lX" % result[0] + "\t\t%04X" % result[1] + "\t\t%04X  " % result[2],
      tap = burst%5
      if channel == MARVELL:
       if tap == 0:
          print "T1/T0"
       elif tap == 1:
          print "T3/T2"
       elif tap == 2:
         print "T5/T4"
       elif tap == 3:
         print "T7/T6"
       else:
          print "T9/T8"
      elif channel == AGERE:
       if tap == 0:
          print "T2/T1"
       elif tap == 1:
          print "T5/T3"
       elif tap == 2:
         print "T7/T6"
       elif tap == 3:
         print "T9/T8"
       else:
          print "NF/TX"
      else:
       print "This channel not yet supported"

      QM.append(result[0])
      VGAR.append(result[1])
   QM.sort()
   VGAR.sort()
#
#  print "\nBURST\t\tQM\t\tVGAR"
#  print   "-----\t\t--\t\t----"
#  for i in range(0,len(buf)/8,1):
#     print "%03X" % i + "\t\t%lX" % QM[i] + "\t\t%04X" % VGAR[i]
#
   nument = len(buf)/8                                                        # number of elements in QM and VGAR arrays
   trim = 0.20                                                                # trim percentage value
   ntrim = int(nument*trim+0.01)                                              # compute number of samples to trim from each end
   QMsum = 0.0                                                                # compute trimmed mean, skip ntrim samples on each end
   QMsumsqd = 0.0                                                             # also accumulate data^2 since it will be needed to calculate stddev
   VGARsum = 0.0
   VGARsumsqd = 0.0

   for i in range(ntrim,nument-1-ntrim,1):
      QMsum = QMsum + QM[i]
      QMsumsqd = QMsumsqd + (QM[i]*QM[i])
      VGARsum = VGARsum + VGAR[i]
      VGARsumsqd = VGARsumsqd + (VGAR[i]*VGAR[i])
   QMmean = QMsum/(nument - 2*ntrim)
   VGARmean = VGARsum/(nument - 2*ntrim)
   print   "-----\t\t----\t\t----"
#  print "ntrim = %d" % ntrim
   print "Trm Mean (hex)\t%lX" % QMmean + "\t\t%04X" % VGARmean
   print "Trm Mean (dec)\t%ld" % QMmean + "\t\t%04d" % VGARmean

   for i in range(0,ntrim-1,1):                                               # add winsorized samples to sum
      QMsum = QMsum + QM[ntrim]                                               # add first data value not skipped for each data point below skipped value
      QMsumsqd = QMsumsqd + (QM[ntrim]*QM[ntrim])
      VGARsum = VGARsum + VGAR[ntrim]
      VGARsumsqd = VGARsumsqd + (VGAR[ntrim]*VGAR[ntrim])

   for i in range(nument-ntrim,nument-1,1):                                   # add winsorized samples to sum
      QMsum = QMsum + QM[nument-1-ntrim]                                      # add last data value not skipped for each data point above skipped value
      QMsumsqd = QMsumsqd + (QM[nument-1-ntrim]*QM[nument-1-ntrim])
      VGARsum = VGARsum + VGAR[nument-1-ntrim]
      VGARsumsqd = VGARsumsqd + (VGAR[nument-1-ntrim]*VGAR[nument-1-ntrim])
#  print "Winz Sqr\t%.0f" % QMsumsqd + "\t\t%.0f" % VGARsumsqd

   QMwinvar = (QMsumsqd-(QMsum*QMsum/nument))/(nument-1)                      # compute sample winsorized variance
   VGARwinvar = (VGARsumsqd-(VGARsum*VGARsum/nument))/(nument-1)
#   print "Winz Var\t%.0f" % QMwinvar + "\t\t%.0f" % VGARwinvar

   if QMwinvar < 0.0:                                                         # compute winsorized standard deviation
      QMstddev = 0.0
   else:
      QMstddev = math.sqrt(QMwinvar)/(1.0-(2.0*ntrim)/nument)
   if VGARwinvar < 0.0:
      VGARstddev = 0.0
   else:
      VGARstddev = math.sqrt(VGARwinvar)/(1.0-(2.0*ntrim)/nument);
   print "Winz StdDev\t%.0f" % QMstddev + "\t\t%.0f" % VGARstddev


  return errorCode
####################################################################

def GetFitness(flags =0, channel=AGERE):
  """
  Collect QM values for a full revolution of MSE data. Calculate the trimmed and weighted fitness value according to
  Pete Harlee's Phast Opti algorithm and display the statistical results. The flag bits are used to disable some calculations
  in order to speed up the function. This command assumes that the format is set for single sector per wedge (reloadRap(2,2)).

  @param flags: User input for command options:

    // optidata flag definitions (From rwapi_pub.h)
    //---------------------------
    #define FITNESS_NO_VGAR                0x0001     // Do not calculate VGAR statistics (for faster operation)
    #define FITNESS_NO_TAPS                0x0002     // Do not calculate TAP statistics  (for faster operation)
    #define FITNESS_IGNORE_ECC_ERR         0x0004     // Process Fitness data even if rd/wrt returns RW_EDAC_HW_UNCORR_ERR.
    #define FITNESS_DO_TRAINING_RD         0x0008     // Do a track read prior to calling get_mse_data, to allow more time for taps to adapt.
    #define FITNESS_RELAX_TAP_LIMITS       0x0010     // Open min and max tap limits from 48 - 207, to 2 - 253.
    #define FITNESS_DISABLE_ROBUST_FIR_TRAINING_AND_SAMPLING 0x0020 // Set this to disable the robust FIR training & sampling
    #define FITNESS_SUPPRESS_SYNC_ERR_INFO 0x1000     // Set this to reduce the amount of sync error reporting - Used by Test 238 Phast Microjog.
    #define FITNESS_GET_ERROR_COUNT        0x2000     // Process Sector Error Count data, return info in signed_value field.
    #define FITNESS_DUMP_FITNESS_DATA      0x4000     // User is requesting fitness data dumped to the report - originally for T238 bucket data.
    #define FITNESS_AGC_MODE               0x8000

  @param channel: Set to 0 for Agere/LSI by default, change to 1 to display Marvell
  @return: Error code
  """

  buf, errorCode = fn( 1365, flags)
  if errorCode == 0:

   print "\nFitness Result"
   print   "--------------"
   result = struct.unpack("2H 2L 2h 12B 3H L 8H 2L",buf[2:66])
   if channel == MARVELL:
    print "   Fitness %ld" %result[2] + "\n   Winz Std Dev %ld" % result[3]
    print "   TAP0  %X" % result[6] + "\n   TAP1  %X" % result[7] + "\n   TAP2  %X" % result[8] + "\n   TAP3  %X" % result[9]
    print "   TAP4  %X" % result[10] + "\n   TAP5  %X" % result[11] + "\n   TAP6  %X" % result[12] + "\n   TAP7  %X" % result[13]
    print "   TAP8  %X" % result[14] + "\n   TAP9  %X" % result[15]
    print "   D_VGA_GAIN  %X" % result[18]
    print "   Flags %X" % result[20]
    print "   Total Errors %d" % result[21]
    MeanIterationCount = float(result[22])/100
    print "   Mean Iteration Count " + str(MeanIterationCount)
    MeanBitsInError = float(result[23])/100
    print "   Mean Bits in Error " + str(MeanBitsInError)
    print "   Low LLR Count %d" % result[24]
    print "   Soft Sum %d" % result[25]
    print "   Number of Samples %d" % result[26]
    MeanBitsInErrorSigma = float(result[27])/100
    print "   Bits in Error Sigma " + str(MeanBitsInErrorSigma)
    print "   Soft Sum Sigma %d" % result[28]
    print "   Low LLR Count Sigma %d" % result[29]
    print "   BCI Fitness = %d " % result[30]
    print "   BCI Fitness Sigma = %d " % result[31]
   elif channel == AGERE:
    result = struct.unpack("2H 2L 2h 10B 3H L 9H 2L",buf[2:66])
    print "   Fitness %ld" %result[2] + "\n   Winz Std Dev %ld" % result[3]
    print "   TAP1  %X" % result[6] + "\n   TAP2  %X" % result[7] + "\n   TAP3  %X" % result[8] + "\n   TAP5  %X" % result[9]
    print "   TAP6  %X" % result[10] + "\n   TAP7  %X" % result[11] + "\n   TAP8  %X" % result[12] + "\n   TAP9  %X" % result[13]
    print "   TAPX  %X" % result[14] + "\n   NLFR  %X" % result[15]
    print "   VGAR  %X" % result[16]
    print "   Flags %X" % result[18]
    print "   Total Errors %ld" % result[19]
    vgarsigma = float(result[20])/100
    print "   VGAR Sigma " + str(vgarsigma)
    MeanIterationCount = float(result[21])/100
    print "   Mean Iteration Count " + str(MeanIterationCount)
    MeanBitsInError = float(result[22])/100
    print "   Mean Bits in Error " + str(MeanBitsInError)
    print "   Low LLR Count %d" % result[23]
    print "   Soft Sum %d" % result[24]
    print "   Number of Samples %d" % result[25]
    MeanBitsInErrorSigma = float(result[26])/100
    print "   Bits in Error Sigma " + str(MeanBitsInErrorSigma)
    print "   Soft Sum Sigma %d" % result[27]
    print "   Low LLR Count Sigma %d" % result[28]
    print "   QM %ld" % result[29]
   else:
    print "This channel not yet supported"

  else:
   result = struct.unpack("4B", buf[2:6])
   print " Sense Code: %X" % result[0] + "  %X" % result[1] + "  %X" % result[2]+ "  %X" % result[3]

  return errorCode

####################################################################

def GetVGA(channel=AGERE):
  """
  Collect and display the voltage gain values. This function uses a full revolution of Phast Opti
  data to calculate the trimmed mean values for VGAR and VGAS. This command assumes that the format
  is set for single sector per wedge (reloadRap(2,2)).

  @param channel: Set to 0 for Agere/LSI by default, change to 1 to display Marvell

  @return: Error code
  """

  buf, errorCode = fn( 1366 )
  #buf,errorCode = __ReceiveResults()
  if errorCode == 0:
   if channel == MARVELL:
    print "\nD_AGC_GAIN\tS_AGC_GAIN"
    result = struct.unpack("2H",buf[2:6])
    print "%X" % result[0] + "\t\t%X" % result[1] + "\n"

   elif channel == AGERE:
    print "\nVGAR\t\tVGAS"
    result = struct.unpack("2H",buf[2:6])
    print "%X" % result[0] + "\t\t%X" % result[1] + "\n"

   else:
    print "This channel not yet supported"

  else:
   result = struct.unpack("4B", buf[2:6])
   print " Sense Code: %X" % result[0] + "  %X" % result[1] + "  %X" % result[2]+ "  %X" % result[3]

  return errorCode
####################################################################


def GetRegData(Reg0 =0, Reg1 =0, Reg2 =0, Reg3 =0, Reg4 =0, Reg5 =0):
  """
  Collect and display selected register data for a full revolution of single sector per track format.
  Any number of registers can be entered up to 6. A hardware register is designated by setting the
  most significant bit (0x8000) of the register value. This command assumes that the format is set for
  single sector per wedge (reloadRap(2,2)).

  @param Reg0 : HW/Channel register value
  @param Reg1 : HW/Channel register value
  @param Reg2 : HW/Channel register value
  @param Reg3 : HW/Channel register value
  @param Reg4 : HW/Channel register value
  @param Reg5 : HW/Channel register value
  @return: Error code
  """
  REG = []
  REG.append(Reg0)
  REG.append(Reg1)
  REG.append(Reg2)
  REG.append(Reg3)
  REG.append(Reg4)
  REG.append(Reg5)

  buf, errorCode = fn( 1367, Reg0, Reg1, Reg2, Reg3, Reg4, Reg5)
  #buf,errorCode = __ReceiveResults()
  if errorCode == 0:

   result = struct.unpack("H",buf[4:6])
   reg_cnt = result[0]

   cnt_lines = int((len(buf)-6)/(2*reg_cnt))

   for i in range(0,reg_cnt,1):
    if REG[i] != 0:
     if REG[i] > 0x8000:
       print "\tH%X" % (REG[i] & 0x7fff),
     else:
       print "\t%X" % (REG[i]),
   print ""

   buf_offset = 6
   for i in range(0,cnt_lines,1):
      print "%X" % i,
      result = struct.unpack('%dH' % (reg_cnt),buf[ (buf_offset):(buf_offset + (reg_cnt*2)) ])
      for j in range(0,reg_cnt,1):
         print "\t%X" % result[j],
      buf_offset += (reg_cnt*2)
      print ""

  else:
   result = struct.unpack("4B", buf[2:6])
   print " Sense Code: %X" % result[0] + "  %X" % result[1] + "  %X" % result[2]+ "  %X" % result[3]

  return errorCode
####################################################################

def OptiATTN(mode = 0):
  """
  Optimize the Attenuation adaptive parameters
  @param mode:      0 = ATTR cal only,  1 = Cal both ATTR and Servo
  @return: Error code
  """

  buf, errorCode = fn( 1368, mode )
  #buf,errorCode = __ReceiveResults()
  if errorCode == 0:

   result = struct.unpack("6H",buf[2:14])
   print "ATTC=%d  " % result[0] + "ATT2S=%d  " % result[1] + "ATT2R=%d  " % result[2],
   print "PGAIN=%d  " % result[3] + "VGAS=%X  " % result[4] + "VGAR=%X  " % result[5]

  return errorCode
####################################################################

def ShockSensorEnable():
   """
   Enable shock sensor
   May require SpinUpDrive() command prior to use
   """
   buf, errorCode = fn(1379, 0)
   result = struct.unpack("HH",buf)
   if result[0] == 0:
      print "Shock Sensor Enabled"
   else:
      # Servo loop code for unsupported command is 0x6f17
      if result[0] == 0x6f17:
         print "Shock Sensor Not Installed!"
      print "Shock Sensor Enable Failed"
      print "Loop code: %x" % result[0]
   return errorCode

####################################################################

def ShockSensorDisable():
   """
   Disable shock sensor
   May require SpinUpDrive() command prior to use
   """
   buf, errorCode = fn(1379, 1)
   result = struct.unpack("HH",buf)
   if result[0] == 0:
      print "Shock Sensor Disabled"
   else:
      # Servo loop code for unsupported command is 0x6f17
      if result[0] == 0x6f17:
         print "Shock Sensor Not Installed!"
      print "Shock Sensor Disable Failed"
      print "Loop code: %x" % result[0]
   return errorCode

####################################################################

def ShockSensorCheck():
   """
   Check shock sensor status
   May require SpinUpDrive() command prior to use
   """
   buf, errorCode = fn(1379, 2)
   result = struct.unpack("HH",buf)
   if result[0] == 0:
      if result[1] == 0:
            print "Shock Sensor Disabled"
      elif result[1] == 1:
         print "Shock Sensor Enabled"
      else:
         print "Bad status"
   else:
      print "Shock Sensor Error"
      # Servo loop code for unsupported command is 0x6f17
      if result[0] == 0x6f17:
         print "Shock Sensor Not Installed!"
      print "Loop Code: %x" % result[0]
   print "Shock Sensor Status: %x" % result[1]

   return errorCode

####################################################################

class fileType:
   SAP = 0x400
   RAP = 0x200
   CAP = 0x100
   BIN = 0x800    # This value is not used.  BIN was added for file type consistency.

def saveAll (targetfile):
    """
    Save the RAP, Sap and CAP to PC files located in c:\var\merlin\results
    Please note that with WinFOF 2.5 it is necessary to enable the "Append to Result file" option to prevent the application
    from deleting all files form the current results directory. These directories are searched for the saved RAP,SAP,CAP files
    in order to restore the RAP,SAP,CAP tables on the drive.

    @param targetfile: Name of the target binary file for the results (filetype is automatically
    appended)
    """

    saveRap (targetfile)
    saveSap (targetfile)
    saveCap (targetfile)

####################################################################

def saveRap (targetfile):
    """
    Save the RAP to a PC file located in c:\var\merlin\results
    Please note that with WinFOF 2.5 it is necessary to enable the "Append to Result file" option to prevent the application
    from deleting all files form the current results directory. These directories are searched for the saved RAP,SAP,CAP files
    in order to restore the RAP,SAP,CAP tables on the drive.

    @param targetfile: Name of the target binary file for the results (filetype is automatically
    generated to be .rap)
    """

    saveAP (targetfile + '.rap', fileType.RAP)

####################################################################

def saveSap (targetfile):
    """
    Save the SAP to a PC file located in c:\var\merlin\results
    Please note that with WinFOF 2.5 it is necessary to enable the "Append to Result file" option to prevent the application
    from deleting all files form the current results directory. These directories are searched for the saved RAP,SAP,CAP files
    in order to restore the RAP,SAP,CAP tables on the drive.

    @param targetfile: Name of the target binary file for the results (filetype is automatically
    generated to be .sap)
    """

    saveAP (targetfile + '.sap', fileType.SAP)

####################################################################

def saveCap (targetfile):
    """
    Save the CAP to a PC file located in c:\var\merlin\results
    Please note that with WinFOF 2.5 it is necessary to enable the "Append to Result file" option to prevent the application
    from deleting all files form the current results directory. These directories are searched for the saved RAP,SAP,CAP files
    in order to restore the RAP,SAP,CAP tables on the drive.

    @param targetfile: Name of the target binary file for the results (filetype is automatically
    generated to be .cap)
    """

    saveAP (targetfile + '.cap', fileType.CAP)

####################################################################

def saveFlash (targetfile):
    """
    Save the flash image to a PC file located in c:\var\merlin\results
    Please note that with WinFOF 2.5 it is necessary to enable the "Append to Result file" option to prevent the application
    from deleting all files form the current results directory. The flash image has a generic header prepended to satisfy
    SeaSerial.

    @param targetfile: Name of the target binary file for the results (filetype is automatically
    generated to be .bin)
    """

    saveAP (targetfile + '.bin', fileType.BIN)

####################################################################

def saveAP (targetfile, rcsFile):
    """
    Save the adaptive parameters file of type rcsFile to a PC file located in c:\var\merlin\results
    @param targetfile: Name of the target binary file for the results (filetype automatically appended).
    @param rcsFile: File type to transfer (CAP, RAP, SAP, BIN)
    """

    filefound = 0
    path = 'c:\\var\\merlin\\results\\'
    for root, dirs, files in os.walk( path ):
      if( dirs == [] ):
			for file in files:
			   if( targetfile == file ):
			      filefound = 1
			      break
      if filefound == 1:
         break

    if filefound == 1:
        filePath = join(root, targetfile)
        raise Exception("%s already exists" % filePath)

    if rcsFile == fileType.RAP or rcsFile == fileType.SAP or rcsFile == fileType.CAP:
       st(178,CWORD1= rcsFile | 0x0008, timeout=100)     # save the data from flash to the PC file
    elif rcsFile == fileType.BIN:
       st(178,CWORD4=0x0001)                             # save the flash image to the PC file

    PCfile = '%d' % CellIndex
    PCfile = PCfile + '-' + '%d' % TrayIndex
    if rcsFile == fileType.RAP:
      binf = open('c:\\var\\merlin\\pcfiles\\rapdata\\' + PCfile,'rb')
    elif rcsFile == fileType.SAP:
      binf = open('c:\\var\\merlin\\pcfiles\\sapdata\\' + PCfile,'rb')
    elif rcsFile == fileType.CAP:
      binf = open('c:\\var\\merlin\\pcfiles\\capdata\\' + PCfile,'rb')
    elif rcsFile == fileType.BIN:
      binf = open('c:\\var\\merlin\\pcfiles\\flashimg\\' + PCfile,'rb')

    f = GenericResultsFile(targetfile)
    f.open('wb')
    f.write(binf.read())
    f.close()
    print 'File saved in C:\\var\\merlin\\results\\' + PCfile + '\\' + targetfile

####################################################################

def restoreAll (targetfile):
    """
    Restores the RAP, SAP and CAP from the PC files located in c:\var\merlin\results of filename [targetfile].rap,sap,cap
    @param targetfile: Name of the target binary file where the RAP,SAP,CAP is stored.
    """

    restoreRap (targetfile)
    restoreCap (targetfile)
    restoreSap (targetfile)

####################################################################

def restoreRap (targetfile):
    """
    Restores the RAP from a PC file located in c:\var\merlin\results of filename [targetfile].rap
    @param targetfile: Name of the target binary file where the RAP is stored.
    """

    restoreAP (targetfile + '.rap', fileType.RAP)

####################################################################

def restoreSap (targetfile):
    """
    Restores the SAP from a PC file located in c:\var\merlin\results of filename [targetfile].sap
    @param targetfile: Name of the target binary file where the SAP is stored.
    """

    restoreAP (targetfile + '.sap', fileType.SAP)

####################################################################

def restoreCap (targetfile):
    """
    Restores the CAP from a PC file located in c:\var\merlin\results of filename [targetfile].cap
    @param targetfile: Name of the target binary file where the CAP is stored.
    """

    restoreAP (targetfile + '.cap', fileType.CAP)

####################################################################


def restoreAP (targetfile, rcsFile):
    """
    Restores the adaptive parameters file of type rcsFile from a PC file located in c:\var\merlin\results of filename [targetfile].rap,sap,cap
    @param targetfile: Name of the target binary file where the AP data is stored.
    @param rcsFile: File type to transfer (CAP, RAP, SAP, BIN)
    """
    global FileLength,FileObj
    FileLength = ''
    FileObj = ''

    filefound = 0
    path = 'c:\\var\\merlin\\results\\'
    for root, dirs, files in os.walk( path ):
      if( dirs == [] ):
			for file in files:
			   if( targetfile == file ):
			      filefound = 1
			      break
      if filefound == 1:
         break

    if filefound == 0:
      raise Exception("%s not found" % targetfile)
    else:
      filePath = join(root, targetfile)
      print 'Found file ' + filePath

      FileLength = os.stat(filePath)[stat.ST_SIZE]
      FileObj = open(filePath,"rb")

      RegisterResultsCallback(procRequest, 81, 0)                             #Intercept callbacks

      st(178, CWORD1= rcsFile | 0x0021, timeout=100)                          # read the target data and save to flash

      RegisterResultsCallback(0, 81, 0)                                       # Restore callbacks
      FileObj.close()

      st(178, CWORD1= rcsFile | 0x000c, timeout=100)                          # save the data from flash to the PC file


####################################################################

def procRequest(requestData, *args, **kargs):
   global FileLength,FileObj

      # Get the four byte BigEndian file address.
   readAddress = requestData[1:5]
   if not 4==len(readAddress): raise FOFResultsProcessingFailure,"Bad or Missing File Address: %s." % (`readAddress`,)
   readAddress = struct.unpack('>I',readAddress)[0]

      # Get the two byte BigEndian read count.
   readCount = requestData[5:7]
   if not 2==len(readCount): raise FOFResultsProcessingFailure,"Bad or Missing Read Count: %s." % (`readCount`,)
   readCount = struct.unpack('>H',readCount)[0]
   if readCount>512: raise FOFResultsProcessingFailure,"Read count of %s is greater than 512." % (readCount,)

   data = FileObj.read(readCount) # Notice that this may read less than readCount.
   returnData = "%s\x00\x00%s" % (READ_FILE,data,)

   SendBuffer(returnData)

########################################################################################################
####################################################################
def RWF(Head = 0):
    """
    Read target head Channel Parameters from RAP buffer RAM (Agere Copperhead Lite).
    This function has been tested on Crockett ONLY!! (by Weiming ScPk)
    @param Head: Target head to display (all zones, all parms)
    @return: Error code
    """
    errorCode = 0
    BegZone = 0
    EndZone = 0
    Mode = 0
    buf, errorCode = fn(1369, Head, BegZone, EndZone, Mode)
    #buf,errorCode = __ReceiveResults()
    strfmt = str(len(buf)/2) + "H"
    RWFParmTuple = struct.unpack(strfmt,buf)
    UserZones = RWFParmTuple[0]
    SystemZones = RWFParmTuple[1]
    TotalZones = UserZones + SystemZones
    MaxHeadInRAP = RWFParmTuple[2]
    MaxParmPerFrame = RWFParmTuple[3]
    print " "
    print " %30s = %02d " % ( "Head", Head )
    print " %30s = %02d " % ( "Total User Zones", UserZones )
    print " %30s = %02d " % ( "Total System Zones", SystemZones )
    print " %30s = %02d " % ( "Maximum Head In RAP File", MaxHeadInRAP )
    print " %30s = %03d " % ( "Maximum Parameter Per Frame", MaxParmPerFrame )
    #print " TotalParameters = %04d " % (len(buf)/2)

    RWFTable_List = [
                    'Reg_85'        ,
                    'Reg_86'        ,
                    'Reg_87'        ,
                    'LATE012R_89'   ,
                    'LATE012F_8A'   ,
                    'WP_EN_8B'      ,
                    'ZFR_93'        ,
                    'CTFFR_94'      ,
                    'ACCR_96'       ,
                    'VGARSH_97'     ,
                    'TAP21_B0'      ,
                    'TAP53_B1'      ,
                    'TAP76_B2'      ,
                    'TAP98_B3'      ,
                    'NLFR_TAPX_B4'  ,
                    'NYTAPR_B5'     ,
                    'DCTAPR_B6'     ,
                    'TDTARGR_B9'    ,
                    'BLC_BETA_BB'   ,
                    'NPTAP3_76_C0'  ,
                    'NPTAP3_54_C1'  ,
                    'NPTAP3_32_C2'  ,
                    'NPTAP3_10_C3'  ,
                    'NPTAP2_76_C4'  ,
                    'NPTAP2_54_C5'  ,
                    'NPTAP2_32_C6'  ,
                    'NPTAP2_10_C7'  ,
                    'NPTAP1_76_C8'  ,
                    'NPTAP1_54_C9'  ,
                    'NPTAP1_32_CA'  ,
                    'NPTAP1_10_CB'  ,
                    'NPTAP0_76_CC'  ,
                    'NPTAP0_54_CD'  ,
                    'NPTAP0_32_CE'  ,
                    'NPTAP0_1B_CF'  ,
                    'BIAS_EDC_D0'   ]

    RWFTable_Dict = {}
    for ParmKey in RWFTable_List:
        RWFTable_Dict[ParmKey] = []

    for znlp in range(0,TotalZones,1):
        RWFParmTuple = ()
        Mode = 1
        BegZone = EndZone = znlp
        buf, errorCode = fn(1369, Head, BegZone, EndZone, Mode)
        #buf,errorCode = __ReceiveResults()
        strfmt = str(len(buf)/2) + "H"
        RWFParmTuple = struct.unpack(strfmt,buf)
        ParmOffset = 0
        for ParmKey in RWFTable_List:
            RWFTable_Dict[ParmKey].append(RWFParmTuple[ParmOffset])
            ParmOffset += 1

    #######################
    ## Print Zone Header ##
    #######################
    strRWFTable = "%13s   " % "Zone"
    for znlp in range(0,UserZones,1):
        strRWFTable += " %02d " % znlp + " "
    for znlp in range(0,SystemZones,1):
        strRWFTable += "Sys%d " % (znlp+1)
    strRWFTable += "\n"

    #############################
    ## Print Horizontal Border ##
    #############################
    for Cnt in range(0,101,1):
        strRWFTable += "="
    strRWFTable += "\n"

    #################################################################
    ## Print Channel Parameter with Row[Parm], Column[Zone] format ##
    #################################################################
    for ww in RWFTable_List:
        strRWFTable += "%13s  " % ww + " "
        for ll in range(0,len(RWFTable_Dict[ww]),1):
            #print "%04X" % RWFTable_Dict[ww][ll] ,
            strRWFTable += "%04X" % RWFTable_Dict[ww][ll] + " "
        strRWFTable += "\n"

    #########################################
    ## Send RWF Table to WInFOF Serial Out ##
    #########################################
    print " "
    print strRWFTable

    return errorCode
####################################################################

def ConvertNominalTrack(track,head):
    """
    Calls ST_CalcTrackPos ==> CalculateTrackPositionRequest to
    convert the specified Nominal Track to Logical Track and
    Radius (as a Q4 number in miliinches, decimal milli inches,
    and floating point inches).
    @param track: Nominal Track to convert
    @param head: Logical Head of Track to convert
    @return: Error code
    """

    mCylinder, lCylinder = __lwords(track)
    buf, errorCode = fn(1370, lCylinder, mCylinder, head, 1)
    #buf,errorCode = __ReceiveResults()
    if errorCode == 0:
        result = struct.unpack(">LLH", buf)

        print "Logical Track : %u (%8xh)" % (result[0],result[0])
        print "Nominal Track : %u (%8xh)" % (result[1],result[1])
        print "Radius (Q4 milli inches) : %xh" % (result[2])
        print "Radius (milli inches)    : %u"  % (result[2]/16)
        print "Radius (inches)          : %0.4f"  % (result[2]/(16.0*1000.0))

    return errorCode

####################################################################

def ConvertLogicalTrack(track,head):
    """
    Calls ST_CalcTrackPos ==> CalculateTrackPositionRequest to
    convert the specified Logical Track to Nominal Track and
    Radius (as a Q4 number in miliinches, decimal milli inches,
    and floating point inches).
    @param track: Logical Track to convert
    @param head: Logical Head of Track to convert
    @return: Error code
    """

    mCylinder, lCylinder = __lwords(track)
    buf,errorCode = buf, errorCode = fn(1370, lCylinder, mCylinder, head, 0)
    ##buf,errorCode = __ReceiveResults()
    if errorCode == 0:
        result = struct.unpack(">LLH", buf)

        print "Logical Track : %u (%8xh)" % (result[0],result[0])
        print "Nominal Track : %u (%8xh)" % (result[1],result[1])
        print "Radius (Q4 milli inches) : %xh" % (result[2])
        print "Radius (milli inches)    : %u"  % (result[2]/16)
        print "Radius (inches)          : %0.4f"  % (result[2]/(16.0*1000.0))

    return errorCode

####################################################################

def ConvertRadiusQ4(radius,head):
    """
    Calls ST_CalcTrackPos ==> CalculateTrackPositionRequest to
    convert the specified Radius (in Q4 milli inches) to Logical Track and
    Nominal Track.
    @param radius: Radial position of track to convert
    @param head: Logical Head of Track to convert
    @return: Error code
    """

    buf, errorCode = fn(1370, radius, 0, head, 2)
    #buf,errorCode = __ReceiveResults()
    if errorCode == 0:
        result = struct.unpack(">LLH", buf)

        print "Logical Track : %u (%8xh)" % (result[0],result[0])
        print "Nominal Track : %u (%8xh)" % (result[1],result[1])
        print "Radius (Q4 milli inches) : %xh" % (result[2])
        print "Radius (milli inches)    : %u"  % (result[2]/16)
        print "Radius (inches)          : %0.4f"  % (result[2]/(16.0*1000.0))

    return errorCode

####################################################################

def ConvertLogToPhys (track, head, quietMode = 0):
  """
  Convert the entered logical or data track to physical or servo track.
  @param track: Data track to convert to physical track
  @param head: Head for the above track
  @return: Physical track
  """
  mCylinder, lCylinder = __lwords(track)
  buf,errorCode = buf, errorCode = fn(1217, lCylinder, mCylinder, head)
  ##buf,errorCode = __ReceiveResults()
  if not errorCode:
     physical_track = struct.unpack("L",buf)
     if quietMode == 0:
         print "Physical Track = %d" % (physical_track[0:1])
     if errorCode != 0:
         print "Test Failed !!!"
     return physical_track

####################################################################

def ConvertPhysToLog (track, head, quietMode = 0):
  """
  Convert the entered physical or servo track to logical or data track.
  @param track: physical track to convert to Data track
  @param head: Head for the above track
  @return: Logical track
  """
  mCylinder, lCylinder = __lwords(track)
  buf, errorCode = fn(1218, lCylinder, mCylinder, head)
  #buf,errorCode = __ReceiveResults()
  logical_track = struct.unpack("l",buf)
  if quietMode == 0:
      print "Logical Track = %d" % (logical_track[0:1])
  if errorCode != 0:
      print "Test Failed !!!"
  return logical_track

####################################################################
#
def ConvertSmrTrack(track, head):
   """
   Convert the entered data track to logical track.
   @param track: Data track to logical track
   @param head: Head for the above track
   @return: Error code
   """
   mCylinder, lCylinder = __lwords(track)
   buf, errorCode = fn(1400, lCylinder, mCylinder, head)
   result = struct.unpack(">LLH", buf)
   data_track, log_track, zone = result
   if errorCode == 0:
      print "Zone = %d" %zone
      print "Data_Track = %d" %data_track
      print "Log_Track = %d" %log_track
   return errorCode

####################################################################

def ConvertPhysSFI (track, head, sfi, len):
  """
  Convert the entered physical track to logical track.
  @param track: physical track to convert to Data track
  @param head: Head for the above track
  @param sfi: Symbols from index
  @param len: Length (in symbols) of defect
  @return: PBA, PCyl, PHead, PSctr, NumSctr
  """
  mCylinder, lCylinder = lwords(track)
  mSfi, lSfi = lwords(sfi)
  buf, errorCode = fn(1388, mCylinder, lCylinder, head, mSfi, lSfi, len)
  #buf,errorCode = __ReceiveResults()
  if errorCode == 0:
      result = struct.unpack("QLHHH", buf)
      print "Cyl = %u " % track + "Hd = %u " % head + "SFI = %u " % sfi + "Len = %u " % len
      print "PBA = %u " % (result[0:1])
      print "PCyl = %u " % (result[1:2])
      print "PHd = %u " % (result[2:3])
      print "PSctr = %u " % (result[3:4])
      print "NumSctrs = %u " % (result[4:5])


####################################################################

def BlockType (BlockAddrType):
    """
    Convert a blocktype C enum to a string as defined in system.h below.
    // Defined Block Address Types.
    typedef enum block_addr_type
    {
       USER_LBA,               // LBA           - User data partition.
       USER_ALTERNATE,         // Alternate     - User data partition.
       USER_PBA,               // PBA           - User data partition.
       USER_RESERVED_PBA,      // Reserved PBA  - User data partition.
       USER_RESERVED_PBA_REALLOCATED, // Reserved PBA reallocated - User data partition
       SYSTEM_LBA,             // LBA           - System data partition.
       SYSTEM_PBA,             // PBA           - System data partition.
       SYSTEM_RESERVED_PBA     // Reserved PBA  - System data partition.
    } block_addr_type;
    @param BlockAddrType: Block type number as defined above
    @return: Sting indicating the block address type
    """
    if BlockAddrType == 0:
        return 'User LBA'
    elif BlockAddrType == 1:
        return 'User Alt LBA'
    elif BlockAddrType == 2:
        return 'User PBA'
    elif BlockAddrType == 3:
        return 'User Rsvd PBA'
    elif BlockAddrType == 4:
        return 'User Rsvd PBA Re-Allocated'
    elif BlockAddrType == 5:
        return 'System LBA'
    elif BlockAddrType == 6:
        return 'System PBA'
    elif BlockAddrType == 7:
        return 'System Rsvd LBA'
    else:
        return 'Unknown Block Type!'

####################################################################

def ConvertLbaToPba (Lba, quietMode = 0):
    """
    Convert an LBA to a PBA
    @param Lba: LBA to convert
    @return: PBA
    """
    Bits63to48, Bits47To32, Bits31To16, Bits15To0 = __llwords(Lba)
    buf, errorCode = fn(1231, Bits63to48, Bits47To32, Bits31To16, Bits15To0)
    Pba = struct.unpack("Q",buf)
    if quietMode == 0:
        print "PBA = %lu " % (Pba[0:1])
    return long(Pba[0])

####################################################################

def ConvertPbaToCHS (Pba, quietMode = 0):
    """
    Convert PBA to the physical cylinder, head, sector
    @param Pba: PBA to convert
    @return: Cylinder, head, and sector
    """
    Bits63to48, Bits47To32, Bits31To16, Bits15To0 = __llwords(Pba)
    buf, errorCode = fn(1232, Bits63to48, Bits47To32, Bits31To16, Bits15To0)
    CHS = struct.unpack(">LHB",buf)
    if quietMode == 0:
        print "Cylinder = %d " % (CHS[0:1]) + "Head = %d " % (CHS[2:3]) + "Sector = %u " % (CHS[1:2])
    return ( long(CHS[0]), long(CHS[2]), long(CHS[1]) )

####################################################################

def ConvertCHSToPba (Cylinder, Head, Sector, quietMode = 0):
    """
    Convert the physical cylinder, head, and sector to a PBA
    @param Cylinder: Cylinder
    @param Head: Head
    @param Sector: Sector
    @return: PBA
    """
    mCylinder, lCylinder = lwords(Cylinder)
    buf, errorCode = fn(1233, lCylinder, mCylinder, Head, Sector)
    Pba = struct.unpack("QB",buf)
    BlockAddrType = BlockType(Pba[1])
    if quietMode == 0:
        print "PBA = %lu " % (Pba[0:1]) + "Block Address Type is " + BlockAddrType
    return long(Pba[0])

####################################################################

def ConvertLbaToCHS (Lba):
    """
    Convert an LBA to the physical cylinder, head, sector
    @param Lba: LBA to convert
    @return: Cylinder, head, and sector
    """
    Pba = ConvertLbaToPba(Lba, 1)
    Cylinder, Head, Sector = ConvertPbaToCHS(Pba)
    print "Cylinder = %d " % Cylinder + "Head = %d " % Head + "Sector = %u " % Sector
    return (Cylinder, Head, Sector)

####################################################################

def ConvertCHSToLba (Cylinder, Head, Sector, quietMode = 0):
    """
    Convert the physical cylinder, head, and sector to an LBA
    if possible.
    @param Cylinder: Cylinder
    @param Head: Head
    @param Sector: Sector
    @return: PBA
    """
    mCylinder, lCylinder = lwords(Cylinder)
    buf, errorCode = fn(1234, lCylinder, mCylinder, Head, Sector)
    Lba = struct.unpack("QB",buf)
    BlockAddrType = BlockType(Lba[1])
    if (BlockAddrType != 'User LBA') and (BlockAddrType != 'System LBA'):
        print "Invalid LBA Type Returned !!!"
    if quietMode == 0:
        print "LBA = %lu " % (Lba[0:1]) + "Block Address Type is " + BlockAddrType
    return long(Lba[0])

####################################################################

def ConvertPbaToLba (Pba):
    """
    Convert a PBA to an LBA
    @param Pba: PBA to convert
    @return: LBA
    """
    Cylinder, Head, Sector = ConvertPbaToCHS(Pba, 1)
    Lba = ConvertCHSToLba (Cylinder, Head, Sector, 1)
    print "LBA = %lu " % Lba
    return Lba

####################################################################

def GetTrackLbaInfo (Track, Head):
    """
    Get the number of LBAs and PBAs on a given track. Get the starting
    LBA and PBA for a track.
    @param Track: Track
    @param Head: Head
    @return: Number of LBAs and PBAs on the track plus starting LBA nad PBA.
    """
    mTrack, lTrack = lwords(Track)
    buf, errorCode = fn(1235, lTrack, mTrack, Head)
    LbaInfo = struct.unpack("QQHH",buf)
    print "Start PBA = %lu " % LbaInfo[0:1] + "Num PBAs = %d" % LbaInfo[2:3]
    print "Start LBA = %lu " % LbaInfo[1:2] + "Num LBAs = %d" % LbaInfo[3:4]

####################################################################

def GetSovaIterations ():
  """
  Read the number of SOVA iterations from the channel.
  @return: Number of iterations
  """
  buf, errorCode = fn(1219)
  #buf,errorCode = __ReceiveResults()
  try:
   iterations = struct.unpack("f",buf)
   print "Number of SOVA iterations = %1.1f" % (iterations[0:1])
  except:
     __displayBuffer(buf)
  if errorCode != 0:
      print "Test Failed, error code = %d" % errorCode

####################################################################

def SetSovaIterations (iterations):
  """
  Set the number of SOVA iterations for the Anaconda Channel
  @param iterations: Number of iterations.
  @return: Number of iterations
  """
  if iterations != 0.5 and iterations != 1.5 and iterations != 2.0 and iterations != 2.5:
      print "Invalid number SOVA iterations entered!"
      return
  iterations_int = int(iterations * 10)
  buf, errorCode = fn(1220, iterations_int)
  #errorCode = __ReceiveResults()
  if errorCode[1] != 0:
      print "Test Failed, error code = %d" % errorCode[1]
  GetSovaIterations()

####################################################################

def GetIterationCount ():
  """
  Read the number of local iterations from the full LDPC channel. Read the global
  iterations enable bit.
  @return: Number of iterations
  """
  buf, errorCode = fn(1308, 0x224)      # Read SMB_DEC_CMD_DATA1
  numIterationsHigh = struct.unpack(">H",buf)
  iterationsHigh = int(numIterationsHigh[0]);
  iterationsHigh &= 0x0007              # Bits 2-0 are bits 9-7 of the iteration count
  buf, errorCode = fn(1308, 0x223)      # Read SMB_DEC_CMD_DATA0
  numIterationsLow  = struct.unpack(">H",buf)
  iterationsLow = int(numIterationsLow[0]);
  iterationsLow &= 0xfe00               # Bits 15-9 are bits 6-0 of the iteration count
  iterations = (iterationsHigh << 5) + (iterationsLow >> 9)
  buf, errorCode = fn(1308, 0x204)      # Read RSM_CTRL
  readStateMachineControl = struct.unpack(">H",buf)
  globalIterationEnable = int(readStateMachineControl[0])
  globalIterationEnable &= 0x0002       # Bit 1 is the global iteration control
  if globalIterationEnable and 0x0002:
      print "Global Iterations Enabled, Number of local iterations = %d" % iterations
  else:
      print "Global Iterations Disabled, Number of local iterations = %d" % iterations
  return iterations

####################################################################

def SetIterationCount (iterations, localOverride = 1, enableGlobalIteration = 1, globalOverrideEnable = 1):
  """
  Set the number of local iterations for the full LDPC Channels. Concurrent global iterations may also
  be enabled and disabled via the enableGlobalIteration flag.
  Flags are passed to firmware as TRUE = 1 to enable and FALSE = 0 to disable.
  @param iterations: Number of iterations.
  @param localOverride: Override the FW #iterations and use the iterations count above. Default = TRUE.
  @param enableGlobalIteration: Enable global iterations. Default = enabled.
  @param globalOverrideEnable: Override the FW global iterations enable/disable switch. Default = TRUE.
  @return: Nothing
  """

  buf, errorCode = fn(1221, iterations, localOverride, enableGlobalIteration, globalOverrideEnable)

####################################################################

def ConfigureBCIControlRegister (Options, LLIStatusThresh, BitsInErrThresh, IterationCntThresh, LowLLRThresh, LLRSoftSumThresh, ErasureCntThresh):
  """
  Configure the Read Channel BCI Control Register for SLE (Status List Entries) data logging.  This also starts
  the BCI hardware, albeit in the paused state.  The BCILoggingMode function can be called to resume the hardware.

  @param : Option and Trigger Bits  -  bit 0  WrapMode
                                    -  bit 1  ThreshMode
                                    -  bit 2  TriggerOnMissedSync
                                    -  bit 3  TriggerOnMarginalMissedSync
                                    -  bit 4  TriggerOnCodeViolation
                                    -  bit 5  TriggerOnTA
                                    -  bit 6  TriggerOnErasure
  @param : LLIStatusThresh
  @param : BitsInErrThresh
  @param : IterationCntThresh
  @param : LowLLRThresh
  @param : LLRSoftSumThresh
  @param : ErasureCntThresh
  @return: Nothing
  """
  global SocSelected

  buf, errorCode = fn(1222, Options, LLIStatusThresh, BitsInErrThresh, IterationCntThresh, LowLLRThresh, LLRSoftSumThresh, ErasureCntThresh)
  if SocSelected !=0 :
     print "Config BCI control for SOC", SocSelected, "->"

  if errorCode == 10253:
     print "Channel feature not supported."
  if errorCode == 10532:    # Using OUT_OF_MEMORY return code when not using self test buffer
     print "SIM file will be used for BCI logging."
  if errorCode == 0:
     print "Self Test malloc'd buffer space will be used for BCI logging."


####################################################################

def SetBCILoggingMode (Selection = 0, NumberOfTracks = 1):
  """
  Pause/Resume the BCI hardware operations.  If the hardware is currently stopped, it will be started, and placed in
  the appropriate paused or resumed state.  Note that starting the hardware, resets the SLE pointers.
  The BCI offline and online commands are required for the malloc and free of the BCI storage required for logging. Not
  putting the BCI back online will leave the offline storage malloc'd until the next power cycle. The FreeBciBuffer
  command may also be used to free the offline malloc's storage.

  @param : Selection  -   0  Display the list of selection modes. (Default)
                          1  Pause BCI logging and report status.
                          2  Resume BCI logging and report status.
                          3  Start or Restart the hardware in diagnostic mode, (Resets the SLE pointers).
                          4  Stop the hardware and put back online.
                          5 - Take BCI offline, (diag mode). Also, malloc's storage for BCI data.
                          6 - Put BCI online, (interface control mode). Also, frees storage from above BCI offline command.
                          7 - Report current status only.
  @param:  NumberOfTracks - Buffer size to malloc for BCI data storage. Used only for option 5 (BCI offline).
  @return: BCI Status
  """
  global SocSelected
  

  if Selection == 0:
     print "0  Display the list of selection modes."
     print "1  Pause BCI logging and report state."
     print "2  Resume BCI logging and report state."
     print "3  Start or Restart the hardware in diagnostic mode, (Resets the SLE pointers)."
     print "4  Stop the hardware and put back online."
     print "5  Take BCI offline, (diag mode). Also, malloc's storage for BCI data."
     print "6  Put BCI online, (interface control mode). Also, frees storage from above BCI offline command."
     print "7  Report current status only."

  else:
     buf, errorCode = fn(1223, Selection, NumberOfTracks)
     if SocSelected !=0 :
        print "Set BCI for SOC", SocSelected, "->"

     if errorCode == 10253:
        print "Channel feature not supported."
     else:
        if Selection == 5:
           if errorCode == 10288:
              print "Malloc Failed!"
           if errorCode == 10214:
              print "Number of sectors requested, %d track(s) worth of data, is greater than 65535! No malloc attempted!" % NumberOfTracks
           if errorCode == 0:
              print "Self Test BCI buffer allocated successfully for %d track(s) worth of data." % NumberOfTracks
              print "Exit Diag Mode to free the buffer."
           else:
              print "SIM file will be used - the first 2048 sectors will be logged to the BCI buffer!"
           OfflineStatus = struct.unpack("H",buf)
           if OfflineStatus[0] & 1:
              print "BCI Offline - Diag or Self Test owns the BCI"
           else:
              print "BCI Online - FW owns the BCI"
           return
        if Selection == 6:
           print "Self Test BCI buffer freed."
           OfflineStatus = struct.unpack("H",buf)
           if OfflineStatus[0] & 1:
              print "BCI Offline - Diag or Self Test owns the BCI"
           else:
              print "BCI Online - FW owns the BCI"
           return
        if Selection != 4 and Selection != 5 and Selection != 6:
           format = "3L"
           results = struct.unpack(format,buf[0:12])
           print "BCIControlReg\t%8Xh" % results[0],
           print "\tBCIStatusReg\t%8Xh" % results[1],
           print "\tCurrentSLEPtr\t%8Xh" % results[2]

           offset = struct.calcsize(format)
           format = "6HB"
           log_status = struct.unpack(format,buf[offset:offset + struct.calcsize(format)])
           if log_status[0] & 1:
              print "Wrap Mode\t     TRUE",
           else:
              print "Wrap Mode\t    FALSE",
           if (log_status[0] >> 1) & 1:
              print "\tLog Overflow\tTRUE",
           else:
              print "\tLog Overflow\tFALSE",
           if (log_status[0] >> 2) & 1:
              print "\t\tFIFO Overflow\t     TRUE"
           else:
              print "\t\tFIFO Overflow\t    FALSE"

           print "Codewords per Sector\t%d" % log_status[1],
           print "\tBuffer Size\t%u" %log_status[2],
           print "\t\tNumber Wrap Times\t%u" % log_status[3]
           print "Current Entry Ptr\t%u" % log_status[4]
           print "Total Entries\t\t%u" % log_status[5]
           if log_status[6] & 1:
              print "BCI Offline - Diag or Self Test owns the BCI"
           else:
              print "BCI Online - FW owns the BCI"

####################################################################

def BCITrackRead (Cyl, Head, StartSector = 0, NumberOfSectors = -1, Options = 0):
  """
  This function will start BCI logging and collect the SLE data for up to one full
  track.  As an option, the track can be written first, though it is suggested that
  the user prewrite the track as errors may occur during the write process.  Upon
  successful completion, BCI logging will be stopped and the SLE data will be available
  in the BCI log.
  Note: The controller must be appropriately configured before calling this function,
        or set the option bit to load the default configuration.

  @param : Target Cylinder
  @param : Target Head
  @param : Number of sectors to read
  @param : Options - bit 0  Write track first.
                   - bit 1  Set default BCI configuration:
                               calls ConfigureBCIControlRegister(0,0,0,0,0,0,0,0)
  """

  # Check to see if the track needs to be written first.
  if Options & 0x0001:
     # Perform Write Seek to the desired track, quite mode.
     errorCode = esk(Cyl, Head, 'w', 0)
     if errorCode:
        if errorCode == 10427:
           print "Write Seek Failure"
        return errorCode

     # Seek successful, write the track.
     else:
        buf, errorCode = fn(1355)
        if errorCode:
           print "Write Failure"
           return errorCode
        else:
           print "Track Write Successful"

  # Perform Read Seek to the desired track, quite mode.
  errorCode = esk(Cyl, Head, 'r', 0)
  if errorCode:
     if errorCode == 10427:
        print "Read Seek Failure"
     return errorCode

  # Seek successful, set up for BCI logging.
  # Seek successful, prepare the BCI for logging.
  #   Note: Requesting that logging be placed in resume mode will put
  #         the hardware in diag mode if necessary and start it as well.
  if Options & 0x0002:
     ConfigureBCIControlRegister(0,0,0,0,0,0,0)

  buf, errorCode = fn(1223, 2)  # Start hardware if not started and Resume
  if errorCode == 10253:
     print "Channel feature not supported."
     return errorCode

  # BCI logging is now ready, read the track.
  errorCode = tread(StartSector, NumberOfSectors)
  if errorCode:
     print "Read Failure"
     return errorCode
  else:
     print "TRead Successful"
     SetBCILoggingMode (1)        # Pause
     buf, errorCode = fn(1223, 4) #SetBCILoggingMode (4) (Stop)

  # Report the final status
  SetBCILoggingMode (7)

  return 0

####################################################################

def DumpBCILogData (FirstSLE = 0, NumberOfSLEs = 0xFFFF, SizeOfCodeword = 8):
  """
  Dump the BCI Log (Status List Entrys) data in formatted output.

  @param : FirstSLE - First SLE to be reported.  Default to 0
  @param : NumberOfSLEs - Number of SLE records to report.  Default to all available
  @param : SizeofCodeword - Number of bytes per codeword.  Default to 8 bytes
  @return: SLE record data
  """
  global SocSelected

  # Get the BCI status to determine the number of entries that can be reported.
  buf, errorCode = fn(1223, 7)
  if errorCode == 10253:
     print "Channel feature not supported."
  else:
     if SocSelected !=0 :
        print "Dump BCI Log for SOC", SocSelected, "->"

     # Offset past unwanted data.
     format1 = "3L"
     offset = struct.calcsize(format1)

     # Parse through the remaining data to get the important pieces.
     format2 = "6H"
     log_status = struct.unpack(format2,buf[offset:offset + struct.calcsize(format1)])
     CodewordsPerSector = log_status[1]
     print "Codewords per Sector   %d" % CodewordsPerSector,
#     print "\tBuffer Size\t%u" %log_status[2],
#     print "Current Entry Ptr\t%u" % log_status[4]
     TotalEntries = log_status[5]
     print "\tTotal Entries   %u" % TotalEntries
     if TotalEntries == 0:
        print "No Data to Process! DumpBCILogData Terminated!"
        return
     # Data to process, call GetAndDisplayBCILogData to display the data
     GetAndDisplayBCILogData(TotalEntries, CodewordsPerSector)

####################################################################

def GetAndDisplayBCILogData(TotalEntries, CodewordsPerSector = 1, FirstSLE = 0, NumberOfSLEs = 0xFFFF, SizeOfCodeword = 8):
     """
     Dump the BCI Log (Status List Entrys) data in formatted output.
     @param : TotalEntries - Number of codewords to be processed
     @param : CodewordsPerSector - Number of codewords per sector
     @param : FirstSLE - First SLE to be reported.  Default to 0
     @param : NumberOfSLEs - Number of SLE records to report.  Default to all available
     @param : SizeofCodeword - Number of bytes per codeword.  Default to 8 bytes
     @return: SLE record data
     """

     # Now go read and report the requested number of SLE records.
     format1 = "6B"
     format2 = "H"

     # Set up outer loop variable, limit to number of SLE records available.
     if NumberOfSLEs > TotalEntries - FirstSLE:
        NumberOfSLEsToGo = TotalEntries - FirstSLE
     else:
        NumberOfSLEsToGo = NumberOfSLEs

     # Set up value that will be used for computing averages.
     NumEntriesProcessed = NumberOfSLEsToGo

     # Initialize the Start SLE indicator
     StartSLE = FirstSLE

     # Determine the maximum number of SLEs that can be transferred in the 512 byte communication buffer.
     MaxSLEsPerBlock = 512 / SizeOfCodeword / CodewordsPerSector

     # Print the SLE Table header
     print("SLE  SyncMiss SyncMrg LBDispl LLIStatus ErrType FifoOvl ErasureCnt SoftSum LowLLRCnt BitsInErr IterCnt")

     IterCnt = 0.0
     BIE = 0.0
     LowLLRCnt = 0.0
     SoftSum = 0.0
     ErasureCnt = 0.0

     AveIterCnt = 0.0
     AveBIE = 0.0
     AveLowLLRCnt = 0.0
     AveSoftSum = 0.0
     AveErasureCnt = 0.0
     AveLLIStatus = 0.0

     # Main transfer loop
     while (NumberOfSLEsToGo):

        if NumberOfSLEsToGo > MaxSLEsPerBlock:
           SLERecordCnt = MaxSLEsPerBlock
        else:
           SLERecordCnt = NumberOfSLEsToGo

        # Request the data
        buf, errorCode = fn(1225, StartSLE, CodewordsPerSector, SLERecordCnt)

        # Display the data
        for entry in range(SLERecordCnt):
           SLE = struct.unpack(format1,buf[(entry * 8):((entry * 8)+6)])
           LBATagAndSync = struct.unpack(format2, buf[((entry * 8)+6):((entry * 8)+8)])

           # Create an integer from the tuple, so I can mask and shift the data.
           LBAData = LBATagAndSync[0]

           LBATag = LBAData & 0x3FFF
           SyncMrg = (LBAData >> 14) & 0x01
           SyncMiss = (LBAData >> 15) & 0x01

           # Expand SLE data using 8 bit radix 4 format with 2 bit exponent and 6 bit mantissa
           IterCnt = (SLE[0] & 0x3F) << (2 * ((SLE[0] >> 6) & 0x03))
           BIE = (SLE[1] & 0x3F) << (2 * ((SLE[1] >> 6) & 0x03))
           LowLLRCnt = (SLE[2] & 0x3F) << (2 * ((SLE[2] >> 6) & 0x03))
           SoftSum = (SLE[3] & 0x3F) << (2 * ((SLE[3] >> 6) & 0x03))
           ErasureCnt = (SLE[4] & 0x3F) << (2 * ((SLE[4] >> 6) & 0x03))

           LLIStatus = (SLE[5] >> 4) & 0x0F
           ErrType = (SLE[5] >> 1) & 0x07
           FifoOvl = SLE[5] & 0x01

           print("%03d: %7d %7d %7d %7X %7d %7d %9d %9d %8d %8d %8d" % ((StartSLE + entry),SyncMiss,SyncMrg,LBATag,LLIStatus,ErrType,FifoOvl,ErasureCnt,SoftSum,LowLLRCnt,BIE,IterCnt))

           AveIterCnt += IterCnt
           AveBIE += BIE
           AveLowLLRCnt += LowLLRCnt
           AveSoftSum += SoftSum
           AveErasureCnt += ErasureCnt
           AveLLIStatus += LLIStatus

        NumberOfSLEsToGo -= SLERecordCnt
        StartSLE += SLERecordCnt

     print("%s" % "="*102)
     print("Average\t\t\t\t %2.2f\t\t\t%8.3f %9.3f %8.3f %9.3f %8.3f" % (AveLLIStatus/NumEntriesProcessed,AveErasureCnt/NumEntriesProcessed,AveSoftSum/NumEntriesProcessed,AveLowLLRCnt/NumEntriesProcessed,AveBIE/NumEntriesProcessed,AveIterCnt/NumEntriesProcessed))
     print("%s" % "="*102)

####################################################################

def FreeBciBuffer():
    """
    Frees the BCI buffer created in ConfigureBCIControlRegister
    """
    buf, errorCode = fn(1226)
    print " Malloc'd BCI buffer is freed. "

####################################################################

def WriteTrackHarmonicSensor(diameter, pattern=2, UserGeneratedPattern=0):
     """
     Write the harmonic data sensor pattern to the active head and cylinder. It also erases the target and adjacent tracks before the write.
     @param : diameter - OD, MD, ID position for writing, OD = 1, MD = 4, Id = 2
     @param : pattern - The fixed pattern to be written to the track. 2 for 2T, 4 for 4T etc.
     @param : UserGeneratedPattern - Set to one for user generated pattern else it's a channel generated pattern
     @return: Sense Data
     """
     buf, errorCode = fn(1242, diameter, pattern, UserGeneratedPattern)

     result = struct.unpack(">LH",buf)
     print "Diag Status = %x " % result[1:2] + "Sense Code = %x" % result[0:1]

####################################################################

def ReadTrackHarmonicSensor(diameter, HeaterDac=0, Att2r=-1, AttRd=-1, Vgar=-1):
     """
     Read the harmonic data sensor pattern previously written to the active head and cylinder
     @param : diameter - OD, MD, ID position for writing, OD = 1, MD = 4, Id = 2
     @param : HeaterDac - Heater DAC value to read at, default to current heater DAC.
     @param : Att2r - Att2r setting for read if greater than zero else use the current channel setting. Defaults to current channel value.
     @param : AttRd - AttRd setting for read if greater than zero else use the current channel setting. Defaults to current channel value.
     @param : Vgar - Vgar setting for read if greater than zero else use the current channel setting. Defaults to current channel value.
     @return: Sense Data
     """
     buf, errorCode = fn(1244, diameter, HeaterDac, Att2r, AttRd, Vgar)
     #__displayBuffer(buf)

     result = struct.unpack("LHHffffhhh",buf)
     print "Att2r = %d " % result[7:8] + "AttcRd = %d " % result[8:9] + "Vgar = %d " % result[9:10]
     print "Diag Status = %x " % result[1:2] + "Sense Code = %x " % result[0:1] + "TargetDac = %u " % result[2:3] + "HF = %f " % result[3:4] + "LF = %f " % result[4:5] + "AR = %f " % result[5:6] + "HIRP = %f " % result[6:7]
     HighFrequencyUnNormalized = result[3:4]
     LowFrequencyUnNormalized = result[4:5]
     print "Raw HF = %f " % (HighFrequencyUnNormalized[0] * 13680.0) + "Raw LF = %f " % (LowFrequencyUnNormalized[0] * 13680.0)

####################################################################

def SetFafhParmfileContactDac(head, diameter, TemperatureIndex, ReadHeatContactDac=0):
     """
     Write the specified contact DAC to the FAFH Parameter File. Entering a DAC value of 0 causes no updates to occur for that DAC. WARNING: entering the wrong
     value for any DAC may cause the head to contact the media.
     @param : head - Head for FAFH Parm file update.
     @param : diameter - OD, MD, ID position for DAC update in FAFH Parm file, OD = 0, ID = 1, MD = 2
     @param : TemperatureIndex - 0 for hot and 1 for cold contact DAC.
     @param : ReadHeatContactDac - Read heater contact DAC value from AFH. Defaults to 0 for no update.
     @return: Self test error code or 0 for success.
     """
     print "Warning! This command can cause the head to hit the disc if the wrong contact DAC value is entered!"
     if (ReadHeatContactDac==0):
         print "Invalid DAC Value Entered"
         errorCode = 14962  # INVALID_CUDACOM_PARAM_RANGE
     else:
         buf, errorCode = fn(1245, head, diameter, TemperatureIndex, ReadHeatContactDac)
     #__displayBuffer(buf)
     if errorCode == 0:
         print "Success! Buffer copy of FAFH Parameter File is updated."
     else:
         print "FAFH Parameter File not Updated. Self Test Error Code = %d" % errorCode

####################################################################

def AccessFafhSerpents(access=0):
     """
     Access the FAFH test serpents is granted when access is 1. Setting access to 0 disables the FAFH test 
     serpent access.
     @param : access - 1 for FAFH test serpent access, 0 for no FAFH test serpent access.
     @return: None
     """
     buf, errorCode = fn(1246, access)
     if (access==0):
         print "FAFH Test Serpent Access Disabled"
     else:
         print "FAFH Test Serpent Access Enabled"

####################################################################

def SetHead(head=0):
    """
    Set number of heads in drive CAP and SAP
    @param head: number of heads (follow servo convention, i.e. 0 for 1 header drive)
    """
    #CAP
    st([178], [], {'HD_COUNT': [head+1], 'timeout': 1200, 'spc_id': 1,'CWORD1': 288,})
    #SAP
    st([178], [], {'timeout': 600, 'MAX_HEAD': head, 'SAP_HDA_SN': [], 'CWORD1': 1056})

####################################################################

def getZoneFrequency(Head = 0xFF, Zone = 0xFF):
  """
  Get Zone NRZ Data Frequency. Display the zone frequency in MegaHertz.
  If a head and zone values are entered, the NRZ data rate from the
  RAP will be reported for that head/zone combination.  If they are
  left to default values, the NRZ data rate for the currently active
  head/zone combination will be reported from the RAP.
  @return: Error code
  """
  if Head == 0xFF:
     buf, errorCode = fn(1362)         # GET_ACTIVE_CHS
     result = struct.unpack(">LB",buf)
     Head = result[1]

  if Zone == 0xFF:
     buf, errorCode = fn(1204)         # FIND_ZONE
     result = struct.unpack(">H",buf)
     Zone = result[0]

  buf, errorCode = fn(1380, Head, Zone)
  zoneFreq = struct.unpack("L", buf[0:4])
  print "Head: %u " % (Head) + " Zone: %u " % (Zone) + " Zone Frequency: %lu " % (zoneFreq[0])

  return errorCode

####################################################################

def RapAddress(quietMode=0):
  """
  Display the RAP Address
  @return: The RAP Address
  """
  buf, errorCode = fn(1237)
  ##buf,errorCode = __ReceiveResults()
  #__displayBuffer(buf)
  RapAddr = struct.unpack(">L",buf)
  if quietMode == 0:
      print "RAP Address = 0x%x " % (RapAddr[0])
  return RapAddr[0]

####################################################################

def servocmd(cmd=1,parm0=0, parm1=0, parm2=0, parm3=0):
    """
    Issue servo command in WinFOF
    @param cmd: servo command
    @param parm0: command parameter 0 (default:0)
    @param parm1: command parameter 1 (default:0)
    @param parm2: command parameter 2 (default:0)
    @param parm3: command parameter 3 (default:0)
    """
    st([11], [], {'timeout': 120, 'PARAM_0_4': (cmd,parm0,parm1,parm2,parm3)})

def FullServoCmd(  Parms = [] ):
    """
    @Description: This will call a servocmd with only up to 8 parameters, it will use
    the execfunction, or with all 32 parameters
    @param Parms
        type: a numpy array of 32 words
        default: None, must be specified
        description: the parms to fill the servocmd register
    @return CmdStatus,DiagStatus,DiagResp
    """     
    import ctypes
    import numpy
    FAIL_STATUS = -1
    SEND_FULL_CMD_FLAG = 1
    RAPID_SERVO_COMMAND   = 1396

    lessThan7Parameters  = numpy.sum(numpy.equal( Parms[ 7 : 31], 0)) == 24
    class servoCmdParmStructure(ctypes.Structure):
        _pack_ = 1;
        _fields_ = [
            ('CmdParam', uint16 * 32),
            ]
    class servoCmdResponceStructure(ctypes.Structure):
        _fields_ = [
            ('CmdStatus', uint16),
            ('DiagStatus', uint16),
            ('DiagResponce', uint16 * 32),
            ]
    
    sendPacket = servoCmdParmStructure()
    for i in range(len(Parms)):
        sendPacket.CmdParam[i] = int(Parms[i])
    if lessThan7Parameters:
        fn(RAPID_SERVO_COMMAND, sendPacket.CmdParam[0], 
                                sendPacket.CmdParam[1], 
                                sendPacket.CmdParam[2], 
                                sendPacket.CmdParam[3], 
                                sendPacket.CmdParam[4], 
                                sendPacket.CmdParam[5], 
                                sendPacket.CmdParam[6],
                                receive = 0)
        buf, errorCode = __ReceiveResults( SERVO_CMD_TIMEOUT )
        if buf[0:3] == OVERLAY_REQUEST:
            endbuf = ReceiveBuffer( timeout = SERVO_RAM_TIMEOUT, maxRetries = 1 )  #Flush Last ExecFunction end Packet
        
    else:
        #Call A full 32 word servocmd
        buf, errorCode = cudacom.fn(RAPID_SERVO_COMMAND, 501, 0, 0, 0, 0, 0, 0, SEND_FULL_CMD_FLAG, receive = 0) #The Header is ignored when Full command is used
        ByteArray = ctypes.string_at(ctypes.addressof(sendPacket), ctypes.sizeof(sendPacket))
        SendBuffer(ByteArray)
        buf, errorCode = __ReceiveResults( SERVO_CMD_TIMEOUT )
        if buf[0:3] == OVERLAY_REQUEST:
            endbuf = ReceiveBuffer(timeout = SERVO_RAM_TIMEOUT, maxRetries = 1)  #Flush Last ExecFunction end Packet
    if errorCode:
        return (FAIL_STATUS, FAIL_STATUS, FAIL_STATUS)  #Make sure unpacks are always the same size
    returnPacket = servoCmdResponceStructure()
    if len(buf) >= ctypes.sizeof(returnPacket):
        ctypes.memmove(ctypes.addressof(returnPacket), buf, ctypes.sizeof(returnPacket))
    else:
        raise Exception('ExecFunction Did not deliver a full packet')
    CmdStatus = int( returnPacket.CmdStatus )
    DiagStatus = int( returnPacket.DiagStatus )
    DiagResponce = numpy.array( returnPacket.DiagResponce, dtype = numpy.uint16 )
    return ( CmdStatus, DiagStatus, DiagResponce )

####################################################################
def OverlayInfo():
  """
  Retrieve the overlay code information from drive
  @return: Error code
  """
  #addrSizePkt = ""
  #overlayHeaderPkt = ""
  #print "Sending 9903"
  buf,errorCode = fn(9903)
  #print "Receiving results"
  #buf,errorCode = __ReceiveResults(timeout = 3)

  addrsizePkt = buf[0:10]

  ovlyExist = struct.unpack('H',buf[0:2])
  addrInfo  = struct.unpack('L',buf[2:6])
  sizeInfo  = struct.unpack('L',buf[6:10])

  if ovlyExist[0] <> 0:
    print "Overlay is loaded and present at addr=0x%08x, size=%d(0x%x)" % (addrInfo[0], sizeInfo[0], sizeInfo[0])
    print "header info:"
    __displayBuffer(buf[10:])
  else:
    print "Overlay is not loaded yet!!!"

  return errorCode

####################################################################
def LoadOverlayFromDisc():
  """
  Load overlay from Disc if overlay is present in system area
  @return: Error code
  """
  #addrSizePkt = ""
  #overlayHeaderPkt = ""
  print "Spinup drive ..."
  st(1)
  print "Loading ..."
  buf,errorCode =fn(1375)
  #buf,errorCode = __ReceiveResults()

  if errorCode == 0:
    print "OVerlay code loaded from disc to execution memory"
    OverlayInfo()
  else:
    print "Unable to load overlay from disc, error code = ", errorCode

  return errorCode


####################################################################

def SpinUpDrive():
  """
  Spins up drive to run Cudacom commands.  MDW cals need to be complete
  and ETF initialized for this function to work properly.
  @return: Error code
  """

  print "Manually spinning up drive!"
  buf, errorCode = fn(1376)
  ##buf,errorCode = __ReceiveResults()


  if errorCode == 0:
    print "Drive successfully spun up."
  else:
    print "Drive had a problem spinning up, returned error code = ", errorCode

  return errorCode

####################################################################
def convertStrToBinaryWords(inStr, padChar = '0', leftJustify = 0):
      """
      Return string as a tuple of words in binary converted ascii
      """

      if leftJustify == 1:
         fillVal ='%-12s' % inStr
      else:
         fillVal ='%12s' % inStr
      rawWord = []
      asciiSpace = ord(' ')


      for ch in fillVal:
         if DEBUG == 1: print(ch)
         chVal = int(binascii.hexlify(ch),16)
         if chVal == asciiSpace:
            chVal = int(binascii.hexlify(padChar),16)
         rawWord.append(chVal)

      if DEBUG == 1: print(str(rawWord))

      mctBlock = []
      index = 0
      for word in range(6):
         byteBlock = []
         for byte in range(2):
            byteBlock.append(rawWord[word*2+byte])
         if DEBUG == 1: print(str(byteBlock))
         mctBlock.append((byteBlock[0]) + (byteBlock[1]<<8))
      if DEBUG == 1: print(str(mctBlock))
      return mctBlock

####################################################################
def ConvertLogToPhysHd (head, quietMode = 0):
  buf,errorCode = fn(1397, head)

  if not errorCode:
     physical_hd = struct.unpack("BB",buf)
     if quietMode == 0:
         print "Physical Head = %d" % (physical_hd[0])
     if errorCode != 0:
         print "Test Failed !!!"
     return physical_hd[0]


####################################################################
def ConvertPhysCylAndOffsetToDataTrack(PhysicalCyl, PhyscialOffset, LogHead, quietMode = 0):
    """
    @Description: This will call a servocmd with only up to 8 parameters, it will use
    the execfunction, or with all 32 parameters
    @param PhysicalCyl
        type: an uint32
        default: None, must be specified
        description: The Physical Cyl
    @param PhyscialOffset
        type: a floating point or Q12 fixed pointer offset
        default: None, must be specified
        description: The Offset from the Physical Cyl
    @param LogHead
        type: uint8 or int
        default: None, must be specified
        description: The current head
    @return a ctypes packet of PhysicalCyl,TotalOffset,LogicalTrack,DataTrack,Head
    """   
    class headPosition(ctypes.Structure):
        _fields_ = [
            ('PhysicalCyl', uint32),
            ('TotalOffset', int32),
            ('LogicalTrack', uint32),
            ('DataTrack', uint32),
            ('Head', uint8)
            ]

    PHYS_AND_OFFSET_TO_UNI_LOG_CONV_AND_DATA_TRK = 9904
    PhysicalCylLSW = PhysicalCyl & 0x0000FFFF
    PhysicalCylMSW = PhysicalCyl >> 16
    PhyscialOffsetLSW = PhyscialOffset & 0x0000FFFF
    PhyscialOffsetMSW = PhysicalOffset >> PhyscialOffset
    returnPacket = headPosition()

    buf, errorCode = fn( PHYS_AND_OFFSET_TO_UNI_LOG_CONV_AND_DATA_TRK, PhysicalCylLSW, PhysicalCylMSW, PhyscialOffsetLSW, PhyscialOffsetMSW )
    ctypes.memmove(ctypes.addressof(returnPacket), buf, ctypes.sizeof(returnPacket))
    return returnPacket

####################################################################
def dumpLogsFromDrive(folderName = 'SptReslt', mctSize = 4):
   """
   Command to extract the test process logs from the drive and dump into the binary results file for translation by dex or mkrep.
   @param folderName: Used to change the name of folder to pull the SF3 results from after the file request
   @param mctSize:   Used to change the word size to communicte to SF3 for folder name
   """
   st(231,CWORD1 = 2, PASS_INDEX=1,FOLDER_NAME = convertStrToBinaryWords(folderName,padChar = '\x00',leftJustify = 1)[:mctSize], timeout = 100)
   data = open(os.path.join(pcFileLocation,folderName,'%d-%s' % (int(CellIndex),TrayIndex)),'rb').read()
   WriteToResultsFile(data)
   del data
   print "Dump to results file complete run dex or mk_rep to view logs"

####################################################################
def saveDbilog():
   """
   Save DBILog as PC file named as cellindex number eg. 1003-1. Does not support user specified filename.
   """
   st(130,CWORD2 = 0x8100, timeout = 1000)

   print "File saved at c:/var/merlin/pcfiles/DBIlog"

####################################################################
def restoreDbilog():
   """
   Restore saved DBILog from c:/var/merlin/pcfiles/DBIlog/<cellindex#>
   back to the disc
   """
   st(130,CWORD2 = 0x0100, timeout = 1000)

####################################################################
def parseTestResults(data,currentTemp,drive5,drive12,collectParametric):
   """
   Parser callback for DBLOG data parsing.
   """
   global dblData
   if 'dexParserOn' in globals():
      global dexHandler
      if dexHandler == None:
         dexHandler = getDexHandler()
      dexHandler(data,currentTemp,drive5,drive12,collectParametric)
   dbLogBlockCodes = [ 11000, 11002]
   dblDelim = ','

   tableNameOff = 0
   colOff = 1
   colWidthOff = 2
   tableTypeOff = 5

   tableInfoBlock = {
                     'codes':[11000],
                     'format':"H"
      }
   tableDataRowBlock = {
                     'codes':[9002,10002, 11002],
                     'format':"HH"
   }
   try:
      from dex.tabledictionary import tableHeaders
   except:
      print "Unable to find tabledictionary for translation in paths %s" % (sys.path,)
      DBlogParserOff()
      return
   length = len(data)                                      # Obtains Length of binary data stream

   index = 25     # Initialize index of binary data stream to 25 jump over the command portion of the results.
                  # For all binary results, the first 25 bytes are made up of a single byte block code,
                  # Two bytes containing the test number, Two bytes containing the Error code,
                  # and Two bytes for each of the Ten Parameters, totaling 25 bytes.

   while index < (length-4):

      format = "HH"
      Block_Size,Block_Value = struct.unpack(format,data[index:index+struct.calcsize(format)])
      if DEBUG > 0:
         print("Block_Value: %s" % str(Block_Value))
      if Block_Value not in dbLogBlockCodes:
         if Block_Size == 0:
            Block_Size = 1 #Prevent the case of bad block header causing an infinite loop

      else:
         if Block_Value in tableInfoBlock['codes'] or Block_Value in tableDataRowBlock['codes']:
            if Block_Value in tableInfoBlock['codes']:
               formatA = tableInfoBlock['format']               # Establishes the format for the Struct module to unpack the data in.
               tableCode, = struct.unpack(formatA,data[index+4:index+4+struct.calcsize(formatA)]) # unpaks the revision Type from the data list
               DriveVars['tableCode'] = tableCode
               binDataStartLoc = index+struct.calcsize(format)+struct.calcsize(formatA)
            else:
               tableCode = DriveVars['tableCode']
               binDataStartLoc = index + struct.calcsize(format)

            binData = data[binDataStartLoc:index+Block_Size]

            if DEBUG >1:
               print("Table Info: tableCode=%s" % str(tableCode))
               print("row data: %s" % (binData,))

            try:
               tableName = tableHeaders[tableCode][tableNameOff]
               abort = 0
            except KeyError:
               tableName = ''
               print("DBLOG Block code %s not defined in tabledictionary.py" % str(tableCode))
               abort = 1

            if not abort:
               rowData = binData.split(dblDelim)

               tableColumns = tableHeaders[tableCode][colOff].split(dblDelim)

               if len(rowData) > len(tableColumns):
                  #expand tableColumns with dummy cols so user has some access to data.
                  dummyCols = ['dummyCol%s' % (i,) for i in range(len(tableColumns),len(rowData))]
                  tableColumns.extend(dummyCols)

               #expand with nuls if more cols than row output
               rowData.extend(range(len(rowData),len(tableColumns)))

               dblData.setdefault(tableName,[]).append(dict(zip(tableColumns,rowData)))
      # Block Size, So index will now reference the start of the next data block.
      index = index+Block_Size


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Calculate a CRC the same way the CM/script code & self-test/IO code does
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def calcCRC(data,sizein,crc):
  for i in range(0,sizein):
    c1 = crc & 0x00AA
    c2 = c1 ^ ord(data[i])
    crc = crc + (c2 & 0x00FF)
  return crc


def parseTestResultsNewHeader(data,currentTemp,drive5,drive12,collectParametric):
   """
   Parser callback for DBLOG data parsing.
   """
   global dblData
   if 'dexParserOn' in globals():
      global dexHandler
      if dexHandler == None:
         dexHandler = getDexHandler()
      dexHandler(data,currentTemp,drive5,drive12,collectParametric)
   dbLogBlockCodes = [ 11000, 11002]
   dblDelim = ','

   tableNameOff = 0
   colOff = 1
   colWidthOff = 2
   tableTypeOff = 5

   tableInfoBlock = {
                     'codes':[11000],
                     'format':"H"
      }
   tableDataRowBlock = {
                     'codes':[9002,10002, 11002],
                     'format':"HH"
   }
   try:
      from dex.tabledictionary import tableHeaders
   except:
      print "Unable to find tabledictionary for translation in paths %s" % (sys.path,)
      DBlogParserOff()
      return

   # Cut off the one byte results key
   resultsSector = data[1:]

   # Assume this is a new 5 byte firmware header
   # Every firmware header has 2 bytes test number, 2 bytes error code and 1 byte block type
   firmareHeaderFormat = ">hHb"
   firmareHeaderSize = struct.calcsize(firmareHeaderFormat)

   # Validate the size
   if len(resultsSector) < firmareHeaderSize:
     print "Invalid firmware header.  received: %s bytes, expected: >= %s bytes." % (len(resultsSector),firmareHeaderSize)
     return

   testNumber, errorCode, blockType = struct.unpack(firmareHeaderFormat,resultsSector[:firmareHeaderSize])

   # Is this a new style firmware header?
   if blockType in (1,):
     # On a new style record, the firmware CRC is the last 2 bytes of the firmware record
     crcFormat = ">H"
     crcSize = struct.calcsize(crcFormat)
     firmwareCRCCheck = struct.unpack(crcFormat,resultsSector[len(resultsSector)-crcSize:])[0]

     # Calculate the firmware CRC
     # First two bytes (test num) and last two bytes (firmware CRC) are not included in the CRC calculation
     rec = resultsSector[2:-crcSize]
     # Pass the same arbitrary seed value (604 == throwing missiles) as firmware & tester do to ensure a CRC of 0's does not equal 0
     crc = calcCRC(rec,len(rec),604)
     # Our function returns a 32 bit value, but firmware function returns a 16 bit value so mask it to get a 16 bit value
     crc = crc & 0xFFFF

     # There is a slim chance an old header would be in this loop by mistake.  Compare our calculated CRC with the firmware calculated CRC
     # If the CRC check fails, try to process the old style header
     if firmwareCRCCheck != crc:
        # Initialize index of binary data stream to 25 jump over the command portion of the results.
        # For all binary results, the first 25 bytes are made up of a single byte block code,
        # Two bytes containing the test number, Two bytes containing the Error code,
        # and Two bytes for each of the Ten Parameters, totaling 25 bytes.
        data = data[25:]

     # New style 5 byte firmware record
     else:
        # From the data set, remove the firmware header from the beginning and the firmware CRC check at the end
        data  = resultsSector[firmareHeaderSize:-crcSize]

   # Old style 24 byte firmware header
   # Initialize index of binary data stream to 25 jump over the command portion of the results.
   # For all binary results, the first 25 bytes are made up of a single byte block code,
   # Two bytes containing the test number, Two bytes containing the Error code,
   # and Two bytes for each of the Ten Parameters, totaling 25 bytes.
   else: data = data[25:]

   length = len(data)                                      # Obtains Length of binary data stream

   index = 0

   while index < (length-4):

      format = "HH"
      Block_Size,Block_Value = struct.unpack(format,data[index:index+struct.calcsize(format)])
      if DEBUG > 0:
         print("Block_Value: %s" % str(Block_Value))
      if Block_Value not in dbLogBlockCodes:
         if Block_Size == 0:
            Block_Size = 1 #Prevent the case of bad block header causing an infinite loop

      else:
         if Block_Value in tableInfoBlock['codes'] or Block_Value in tableDataRowBlock['codes']:
            if Block_Value in tableInfoBlock['codes']:
               formatA = tableInfoBlock['format']               # Establishes the format for the Struct module to unpack the data in.
               tableCode, = struct.unpack(formatA,data[index+4:index+4+struct.calcsize(formatA)]) # unpaks the revision Type from the data list
               DriveVars['tableCode'] = tableCode
               binDataStartLoc = index+struct.calcsize(format)+struct.calcsize(formatA)
            else:
               tableCode = DriveVars['tableCode']
               binDataStartLoc = index + struct.calcsize(format)

            binData = data[binDataStartLoc:index+Block_Size]

            if DEBUG >1:
               print("Table Info: tableCode=%s" % str(tableCode))
               print("row data: %s" % (binData,))

            try:
               tableName = tableHeaders[tableCode][tableNameOff]
               abort = 0
            except KeyError:
               tableName = ''
               print("DBLOG Block code %s not defined in tabledictionary.py" % str(tableCode))
               abort = 1

            if not abort:
               rowData = binData.split(dblDelim)

               tableColumns = tableHeaders[tableCode][colOff].split(dblDelim)

               if len(rowData) > len(tableColumns):
                  #expand tableColumns with dummy cols so user has some access to data.
                  dummyCols = ['dummyCol%s' % (i,) for i in range(len(tableColumns),len(rowData))]
                  tableColumns.extend(dummyCols)

               #expand with nuls if more cols than row output
               rowData.extend(range(len(rowData),len(tableColumns)))

               dblData.setdefault(tableName,[]).append(dict(zip(tableColumns,rowData)))
      # Block Size, So index will now reference the start of the next data block.
      index = index+Block_Size


####################################################################

def EnableSFTRuntimeTweaking():
   """
   Enable shock sensor
   May require SpinUpDrive() command prior to use
   """
   buf, errorCode = fn(1393, 0)
   result = struct.unpack("H",buf)
   if result[0] == 1:
      print "SFT Runtime Tweaking Enabled"
   return errorCode

def DisableSFTRuntimeTweaking():
   """
   Disable shock sensor
   May require SpinUpDrive() command prior to use
   """
   buf, errorCode = fn(1393, 1)
   result = struct.unpack("H",buf)
   if result[0] == 0:
      print "SFT Runtime Tweaking Disabled"
   return errorCode

def CheckSFTRuntimeTweaking():
   """
   Check shock sensor status
   May require SpinUpDrive() command prior to use
   """
   buf, errorCode = fn(1393, 2)
   result = struct.unpack("H",buf)
   if result[0] == 1:
      print "SFT Runtime Tweaking Enabled"
   elif result[0] == 0:
      print "SFT Runtime Tweaking Disabled"
   return errorCode

####################################################################

def DBlogParserOn():
   """
   Enable automatic parsing of dblog data into variable dblData.
      @return: dblData is a dictionary of tables. Each dict value is a list of dicts where the dictionary is a column-name:value
   """
   print("WARNING: Variable dblData will grow in RAM with every test call. enter dblData = {} to clear out the RAM.")
   #RegisterResultsCallback(parseTestResults)
   RegisterResultsCallback(parseTestResultsNewHeader)

def DBlogParserOff():
   """
   Disables parsing of data into dblData dictionary
   """
   RegisterResultsCallback(None)
   global dexParserEnabled
   if 'dexParserOn' in globals() and dexParserEnabled:
      dexParserOn()


def St(*args,**kwargs):
    import copy
    prm = copy.copy(args[0])
    prm.update(kwargs)

    test_num = prm.pop('test_num', 0)
    timeout  = prm.pop('timeout', 600)
    prm.pop('prm_name', '')
    st(test_num, prm, timeout=timeout)


def processREQUEST_CURRENT_DATE(requestData,currentTemp= 0,drive5 = 0,drive12= 0,collectParametric = 1):
   """
   Process request callback for time request REQUEST_CURRENT_DATE = 31 that returns the
      current integer value of seconds from EPOCH to drive and date_time

      taken from core_datetime.h
      typedef struct date_and_time
         {
            uint16 Year;    // no rules
            uint8  Month;   // 1-12
            uint8  Day;     // 1-31
            uint8  Hour;    // 0-23
            uint8  Minute;  // 0-59
            uint8  Second;  // 0-59
         } date_and_time;
   """
   resultsKey = 0
   try:
      resultsKey = ord(requestData[0])
   except:
      traceback.print_exc()
      print("Error in attempting results key parsing for %s" % (requestData,))


   if DEBUG:
      print("Got request for %d" % (resultsKey,))

   if resultsKey == REQUEST_CURRENT_DATE:
      refTime = time.time()

      date = time.localtime(refTime)

      if DEBUG:
         print("time:%d" % refTime)
         print("date:%02d/%02d/%04d %02d:%02d:%02d" % (date[1],date[2],date[0],date[3],date[4],date[5]))

      resp = struct.pack('B',  REQUEST_CURRENT_DATE, )
      resp += struct.pack('Q', int(refTime))
      resp += struct.pack('HBBBBB', *date[0:6])

      if DEBUG:
         print("Returning %s" % (binascii.hexlify(resp),))
      SendBuffer(resp)

   else:
      SendBuffer(FAIL_RESP)
      print("Invalid resultsKey: %s" % (repr(resultsKey),))

RegisterResultsCallback(processREQUEST_CURRENT_DATE, REQUEST_CURRENT_DATE, useCMLogic=0)
###########################################################################
def FlashUpdate(ApToFlash=0):
   """
   Save CAP/RAP/SAP from DRAM to flash depending on flag setting:
   0x1 = CAP
   0x2 = RAP
   0x4 = SAP
   ApToFlash = 0x7 will update all 3 CAP/RAP/SAP to flash
   """
   global SocSelected;

   if ApToFlash:
      print "Flash Updat to SoC -> ", SocSelected
      print "Writing (",
      if ApToFlash & 1:
         print "CAP,",
      if ApToFlash & 2:
         print "RAP,",
      if ApToFlash & 4:
         print "SAP",
      print ") from DRAM to flash and reset drive.\n"

      buf, errorCode = fn(1398, ApToFlash, timeout=180) #the flash update should not be longer than 3 minutes!
      if errorCode==0:
         result = struct.unpack("HHH",buf)
         print "returned values=",result
      else:
         print ("Flash Update failed!\n")
   else:
      print("None AP specified to save to flash! 1=CAP, 2=RAP, 4=SAP")


##############################################################################
#  MSMR Functions  
##############################################################################

def SwitchSoc(SocSelect=1):
   """
   For MSMR mule only, used to select which SoC to do following operations.
   Legal values is 1 or 2 only.
   """
   global SocSelected;

   buf, errorCode = fn(2000, SocSelect, timeout=10) 
   if errorCode==0:
      result = struct.unpack("H",buf)
      SocSelected = result[0]
      print "SoC selected = ", SocSelected
   else:
      print ("SwitchSoc failed!\n")

   return SocSelected

def CheckSoc2():
   """
   For MSMR mule only, used to check if SOC2 is alive.
   
   """

   buf, errorCode = fn(2001, timeout=1000000) 
   if errorCode==0:
      #result = struct.unpack("H",buf)
      print "SoC2 is alive!"
   else:
      print ("SOC2 is not responding!\n")


def ReadNonFbiReg(Addr=0x47E):
   """
   For MSMR mule only, Read Non FBI register, currently on 0x47E, 0x480, and 0x482 register supported:
   0x47e = MSMR_mailbox_strb
   0x480 = MSMR_mailbox_rd
   0x482 = MSMR_mailbox_wr
   
   Should be effective for both SOC, reading a 0x482 (MSMR_mailbox_wr) register is meaningless  
   """

   buf, errorCode = fn(2002, Addr, timeout=100) 

   if errorCode==0:
      result = struct.unpack("HH",buf)
      print "Non FBI reg addr=0x%x, value=0x%x" % (result[0],result[1])
   else:
      print "Read non FBI reg failed addr = 0x%x" % (Addr)


def WriteNonFbiReg(Addr=0x482, Data=0):
   """
   For MSMR mule only, Write Non FBI register, currently on 0x47E, 0x480, and 0x482 register supported:
   0x47e = MSMR_mailbox_strb
   0x480 = MSMR_mailbox_rd
   0x482 = MSMR_mailbox_wr
   
   Should be effective for both SOC, Writing a 0x480 (MSMR_mailbox_rd) register is meaningless  
   """
   buf, errorCode = fn(2003, Addr, Data, timeout=100) 

   if errorCode==0:
      result = struct.unpack("HH",buf)
      print "Non FBI reg write, addr=0x%x, value=0x%x" % (result[0],result[1])
   else:
      print "Write non FBI reg failed addr = 0x%x" % (Addr)


####################################################################

def sync_readtrack(StopOnError=0):
  """
  MSMR sync read version of the readtrack command
  Read the current track
  @param StopOnError: If set to 1, will stop on read error
  @return: Error code
  """
  buf, errorCode = fn(2005,StopOnError)  # SYNC_ST_READ_TRACK
  #buf,errorCode = __ReceiveResults()
  __displayBuffer(buf)
  return errorCode

####################################################################

def sync_readcont(startSector, numSectors, quietMode = 0, flag=0, MsmrFpgaSid=0):
  """
  This is the MSMR sync read version of the readcont command, please refer to readcont for
  command detail
  @param startSector: Sector at which to start the reads.
  @param numSectors: Number of sectors to read
  @param quietMode: Supress sense data on PASS status of quiet mode not default or zero
  @param flag: 0 = Ignore Errors   1 = Stop On Error
  @param MsmrFpgaSid: 0 = Disable FPGA SID   1 = Enable FPGA SID
  @return: Error code
  """
  buf, errorCode = fn(2006, startSector, numSectors, flag, MsmrFpgaSid) # SYNC_READ_CONT
  #buf,errorCode = __ReceiveResults()
  result = struct.unpack("LLLL",buf)
  print "Reader 1:"
  senseData = result[0:1]
  if quietMode == 0:    # Display sense data always if not quiet mode
      print "Sense Data = %x " % (result[0:1])
  if senseData[0] != 0x00000080:
      if quietMode == 0:
          print "Last Sector = %u" % (result[1:2])
      else:
          print "Sense Data = %x " % (result[0:1]) + "Last Sector = %u" % (result[1:2])

  print "Reader 2:"
  senseData = result[2:3]
  if quietMode == 0:    # Display sense data always if not quiet mode
      print "Sense Data = %x " % (result[2:3])
  if senseData[0] != 0x00000080:
      if quietMode == 0:
          print "Last Sector = %u" % (result[3:4])
      else:
          print "Sense Data = %x " % (result[2:3]) + "Last Sector = %u" % (result[3:4])

  return errorCode

def sync_ber(targetBer, numRevs, TLevel, ldpc=0, globalIterations = 0, localIterations = 0, zeroLatency=0):
  """
  Run the BER test, seek to target track using ActiveHead and ActiveCylinder and measure raw BER.
  Display Bit Error Rate, Data Errors, Sync Errors, Other Errors, Sectors Per Rev, Sense Code, and failed sector if other error.
  @param targetBer: Target BER limit (times 10) to measure. Number of revs are calculated internally to meet the target BER.
  @param numRevs: Number of revs to read in the BER test. Will override the targetBer if numRevs is non-zero.
  @param TLevel: ECC Level (0 to 30 by 2's -- See TLEVEL define below in setEccLevel). Non-LDPC channels only.
  @param ldpc: Low Density Parity Encoding (iterative) channel if set else PRML channel. 0x0001 = LDPC SFR, 0x0002 = LDPC BER.
               0x0004 = LDPC BER Mode with data error handling (need to set bit 0x0002 also).
  @param globalIterations: Set to 1 to enable global iterations. LDPC channels only.
  @param localIterations: Number of local iterations to run. LDPC channels only.
  @param zeroLatency: Enable zero latency read if set to 1
  @return: Error code
  """
  if ((TLevel % 2) != 0) or ((TLevel > 30) and (TLevel != 100)):
    print "Invalid TLevel Entered!"
    return
  if ldpc & 2:
      zeroLatency |= 2   # Use this flag to set the BER option for execfunc.c
  if ldpc & 4:
      zeroLatency |= 4   # Use this flag to set the BER option with data error accounting in error counts
  buf, errorCode = fn(2007, targetBer, numRevs, TLevel, globalIterations, localIterations,  zeroLatency)
  if ldpc != 0:
      result = struct.unpack("fLLLLHHLLfLLLLHHLL",buf)
  else:
      result = struct.unpack("fLLLHHLLLfLLLHHLLL",buf)

  print "Reader 1:"
  if ldpc != 0:
      other_errors = result[4:5]
      print "BER = %f " % (result[0:1]) + "Bits in Error = %u " % (result[1:2]) + "Data Errors = %u " % (result[2:3]) + "Sync Errors = %u " % (result[3:4]) + \
      "Other Errors = %u " % (result[4:5]) + "Sectors per Rev = %u " % (result[5:6]) + "Sense Data = %x " % (result[7:8])
  else:
      other_errors = result[3:4]
      print "BER = %f " % (result[0:1]) + "Data Errors = %u " % (result[1:2]) + "Sync Errors = %u " % (result[2:3]) + \
      "Other Errors = %u " % (result[3:4]) + "Sectors per Rev = %u " % (result[4:5]) + "Sense Data = %x " % (result[6:7])
  if other_errors[0] > 0:
      if ldpc != 0:
          print "Failed Sector = %u" % (result[8:9])
      else:
          print "Failed Sector = %u" % (result[7:8])
  sctrs_rev = (result[5:6])
  cw_rev = 2*int(sctrs_rev[0])
  sctr_errors = (result[2:3])
  cw_errors_R1=2*int(sctr_errors[0])
  measure_ber = (result[0:1])
  ber = float(measure_ber[0])
  #### Reader 2 results
  print "Reader 2:"
  if ldpc != 0:
      other_errors = result[13:14]
      print "BER = %f " % (result[9:10]) + "Bits in Error = %u " % (result[10:11]) + "Data Errors = %u " % (result[11:12]) + "Sync Errors = %u " % (result[12:13]) + \
      "Other Errors = %u " % (result[13:14]) + "Sectors per Rev = %u " % (result[14:15]) + "Sense Data = %x " % (result[16:17])
  else:
      other_errors = result[12:13]
      print "BER = %f " % (result[9:10]) + "Data Errors = %u " % (result[10:11]) + "Sync Errors = %u " % (result[11:12]) + \
      "Other Errors = %u " % (result[12:13]) + "Sectors per Rev = %u " % (result[13:14]) + "Sense Data = %x " % (result[15:16])
  if other_errors[0] > 0:
      if ldpc != 0:
          print "Failed Sector = %u" % (result[17:18])
      else:
          print "Failed Sector = %u" % (result[16:17])
  sctr_errors = (result[11:12])
  cw_errors_R2=2*int(sctr_errors[0])
  measure_ber = (result[9:10])
  ber2 = float(measure_ber[0])

  return ber, ber2, cw_errors_R1, cw_errors_R2, cw_rev

####################################################################
def StartBCI():
    """
    Setup and start BCI Logging
    """
    SetBCILoggingMode(3)    # Start BCI
    SetBCILoggingMode(2)    # Resume BCI
    SetBCILoggingMode(5)    # Self Test owns the BCI (malloc instead of SIM File)
    ConfigureBCIControlRegister(0,0,0,0,0,0,0)  # Log everything

#####################################################################
def StopBCI():
    """
    Stop BCI
    """
    SetBCILoggingMode(1)    # Pause BCI
    SetBCILoggingMode(4)    # Stop BCI


############## calculate cnts to for offset step parameter ######################  
def step(offset): 
  #print "offset = %d"%(offset)
  if (offset < 0):
    steps = 65535 + int((offset*255)/100)
  if (offset > 0):
    steps= int(offset*255/100)  
  if (offset == 0):
    steps = 0
  #print "steps = %d"% steps
  return(steps);  
##############################
def SOVAtubs():
   count=0
   error_rates=[]
   offsets=[]
   #offset=[0,5,10,15,20,25,30,35,40,45,50,0,-5,-10,-15,-20,-25,-30,-35,-40,0]
   offset=[0,5,10,15,20,25,30,35,40,45,50,0,-5,-10,-15,-20,-25,-30,-35,-40,-45,-50,0]
   #offset =[0,5,10,15,20,0,-5,-10,-15,-20,0]
   for n in offset:      
         cnts = step(n) # convert desired offset to DAC cnts
         print "offset = %d, DACcnts= %d"%(n,cnts)
         ofs(cnts)
         rsk(gCylinder,gHead)
         #ber(0,10,0,6,0,200)
         #sync_readcont(0,200) # do a training read
         #sync_readtrack() # do a training read
         SOVA1=sync_ber(0,10,0,6,0,200)
         error_rates.append(SOVA1)
         offsets.append(n)
         count=count+1
   print"back on track center"

   for i in range(count):
     #print"percent off trk = %d, SOVA1= %f"%(offsets[i], error_rates[i])
     print"percent off trk = %d, SOVA1= %f,%f,%d,%d,%d"%(offsets[i], error_rates[i][0],error_rates[i][1],error_rates[i][2],error_rates[i][3],error_rates[i][4])
################################################################################### 


def ReadNRB(Zone = 0, Head = 0, Options = 0, C1C0 = 0, C3C2 = 0):
    """
    Read or Write NRBD parameters from the channel or RAP. When writing, only one states worth of
    parameters is input and those values are copied to all 16 states.

    Valid Options from selftest-channel.h:

    #define TAP_OPT_NO_OPTIONS                0x0000   // Read from channel
    #define TAP_OPT_UPDATE_CHANNEL            0x0001   // Write to channel
    #define TAP_OPT_UPDATE_DZH_TABLE          0x0002   // Write to RAP
    #define TAP_OPT_USE_CALLERS_TAP_VALUES    0x0004   // Write using passed in values
    #define TAP_OPT_READ_DHZ_TABLE            0x0008   // Read tap values from RAP

    @param Zone: zone offset in RAP
    @param Head: head offset in RAP
    @param Options: Options for ReadWriteNRBParms - see above bit definitions
    @param C1C0: C1(MSB), C0(LSB)
    @param C3C2: C3(MSB), C2(LSB)
    @return: Error code
    """
    # Initialize lists
    C0 = [0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5]
    C1 = [0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5]
    C2 = [0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5]
    print "Options=%d" % Options
    buf, errorCode = fn(2008, Head, Zone, Options, C1C0, C3C2)    # Call ReadWriteNLDEstimationParms
    if (Options & 0x0004) == 4:
        print "Writing NLD Estimation Parameters"
    else:
        NRB = struct.unpack("33H",buf)
        for count in range (0, 16, 1):
            C0[count] =  NRB[count+1] & 0x00ff
            C1[count] = (NRB[count+1] & 0xff00) >> 8
            C2[count]   = (NRB[count+1+16] & 0xff00) >> 8
        print "              C0     C1    C3"
        #print "return status %4X" % NRB[0]
        for count in range (0, 16, 1):
           print "State = %2d " % count + " %4X" % (C0[count]) + "   %4X" % (C1[count]) + "  %4X" % (C2[count]) 
           #print "State = %d " % count + "%4X"%NRB[count+1] + "%4X" % NRB[count+16+1]

################################################################################### 

def Load_Precoder(Zone = 0, Head = 0, Precoder = 0x76543210, Option=0):

   """
   if Option!=0 write precoder to precoder memory, and then SRC and SID
   if Option==0 read precoder from precoder memory to get current precoder
   @param Zone: zone offset in RAP
   @param Head: head offset in RAP
   @param Precoder: precoder to load in SID and SRC
   @Option:  0: read current precoder from firmware;  1: write to firmware
   @return: Error code
   """

   buf, errorCode = fn(2009, Head, Zone, Precoder>>16, Precoder&0xFFFF, Option)    
   precoder=struct.unpack("3H", buf)
   if errorCode:
      print "error accessing precoder memory %d" % errorCode
   else:
      if Option == 0:
         print "Read from drive precoderHi 0x%4X "%precoder[1]+ "precoderLow 0x%4X"%precoder[2] 
      else:
         print "Write to drive precoderHi 0x%4X "%precoder[1]+ "precoderLow 0x%4X"%precoder[2] 


