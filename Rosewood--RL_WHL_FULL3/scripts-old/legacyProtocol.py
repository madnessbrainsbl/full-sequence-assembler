# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
import traceback
import time
ENQ = chr(5)
ACK = chr(6)
NAK = chr(21)
ETX = chr(3)
STX = chr(2)

class LegacyProtocol:
  def __init__(self):
    self.cellTray = CellIndex, TrayIndex
  
  def bytes(self,the_word):
    return ((the_word>>8)&0xFF,the_word&0xFF)

  
  def __buildBlock(self,theBlock):

    # get the block size
    blockLen = len(theBlock)
    sizeHi,sizeLo = self.bytes(blockLen) # returns (hi_byte,lo_byte)

    # compute checksum
    checksum = reduce(lambda x,y:x+ord(y),theBlock,0)

    # add block size into checksum too
    checksum = checksum + sizeHi + sizeLo
    (chkHi,chkLo) = self.bytes(checksum) # returns (hi_byte,lo_byte)

    # Build the complete block: block size, the block, and the block checksum
    theBlock = chr(sizeHi) + chr(sizeLo) + theBlock + chr(chkHi) + chr(chkLo)

    return theBlock
    

  def SendBuffer(self,theData,**kwargs):

    theData = self.__buildBlock(theData)

    # optimistic protocol!
    # Send the response to the ETX before it arrives
    # Send the data before the ACK arrives
    theData = ENQ + ACK + STX + theData
    PBlock(theData)

    # Now this data will take some time to get through Linux, USB, and the cell before it completely gets to the drive
    # byte time at 38400 baud is ~286 us, USB time is ~1 ms each way
    # this is an optimization factor that we may never completely get right...
    pauseTime = 0.150
    ScriptPause(pauseTime)

    # expect ETX
    # Filter 'noise' characters from the front of the frame
    try:
      filteredChars = []
      loopStartTime = time.time()
      while 1:
        charIn = GChar(readSize=1)  # Ignore cell buffer overflows in the NAK filter.
        # Filter all characters except ETX and STX; This is our NAK filter
        if charIn not in [ETX,STX]:
          filteredChars.append(charIn)
          loopTime = time.time() - loopStartTime
          if loopTime <= 4:   # avoid endless loop
            continue
        break

      if ETX != charIn:
        msg = "esgtransport.sendFrame(): cellTray: %s  Sent ENQ, non-ETX = x%02X, filteredChars = %s" % (self.cellTray,ord(charIn),map(lambda x: 'x%02X'%ord(x),filteredChars))
        raise FOFSerialCommError, msg
    except:
      msg = "esgtransport.sendFrame(): cellTray: %s   Sent ENQ, no response...  filteredChars = %s    XXX  %s" % (self.cellTray,filteredChars,traceback.format_exc())
      raise  FOFSerialTestTimeout, msg

    # Special Handling for High-Speed Transfer Mode
    #if self.serialPort.isHighSpeedMode():
    #  charIn = self.serialPort.read()  # High speed mode, sends two extra nulls
    #  charIn = self.serialPort.read()

    # expect ACK
    charIn = GChar(readSize=1)

    if ACK != charIn:
      # NOTE:  In this case, if the charIn is not NAK, you may want to send down an 'illegal' frame, ie a short frame with a bad checksum
      # so that the drive will continue - otherwise it may be waiting there for you to send characters.
      # This may be a workaround for this particular protocol bug.

      msg = "esgtransport.sendFrame(): cellTray: %s   Sent STX, non-ACK = x%02X" % (self.cellTray,ord(charIn))
      raise FOFSerialCommError, msg

    # expect ACK
    charIn = GChar(readSize=1)

    if ACK != charIn:
      # NOTE:  If this char is not ACK or NAK, how do you decide if it is a garbled ACK, or NAK, or something else?
      # If the drive actually sent an ACK, it thinks it's completed this transaction, and it will proceed to the next transaction and further retries on sendFrame are futile.
      # To work around this Protocol bug, you could consider *assuming* that this is an ACK (and flush).  What's most likely?

      msg = "esgtransport.sendFrame(): cellTray: %s  Sent BLOCK, non-ACK = x%02X" % (self.cellTray,ord(charIn))
      raise FOFSerialCommError, msg


