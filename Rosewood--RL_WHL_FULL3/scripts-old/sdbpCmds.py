# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
from Constants import *
import struct, types
from sdbpComm import *

READ_SEEK = 0
WRITE_SEEK = 1
WRITE_HEADER_SEEK = 2

class rwSubCmdEnum:
   READ = 1
   WRITE = 2
   READ_COMPARE = 3

class systemFileEnum:
   SPT_TEST_RESULTS_FILE = 12
   PRIMARY_DEFECT_FILE = 3

def __buildSystemFileDFB(fileNumber, xferLen, startingBlock, SC = 0, sizeSel = 0):
   dfbData = struct.pack('H',fileNumber) #File
   dfbData += struct.pack('H',0) #Transfer Length
   dfbData += struct.pack('HH',0,0) #Starting Block Index
   SC = 0
   sizeSel = 1
   dfbData += struct.pack('B', (SC<<4) + sizeSel)
   return DitsCommand(0x144,dfbData)

def getSystemFileSize(fileNumber):

   data, error, dataBlock = __buildSystemFileDFB(fileNumber, 0, 0, 0, 1)
   return struct.unpack('B',dataBlock)[0]


def readSystemFile(fileNumber = systemFileEnum.SPT_TEST_RESULTS_FILE):
   fileSize = getSystemFileSize(fileNumber)
   if fileSize == 0:
      print "File has 0 size"
      return None
   fbuff = GenericResultsFile('SIM_%d.bin' %  fileNumber)
   fbuff.open('wb')
   try:
      for blockNum in xrange(fileSize):
         data, error, dataBlock = __buildSystemFileDFB(fileNumber, 1, blockNum)
         fbuff.write(dataBlock)
   finally:
      fbuff.close()

   return fbuff

def getHDASN(useDITS = True):
   if useDITS:
      data, error, dataBlock = DitsCommand(0x156, '\x00')

      return dataBlock
   else:
      data, error, dataBlock = DitsCommand(0x0F, '')

def getHDATemp(useDITS = True):
   if useDITS:
      data, error, dataBlock = DitsCommand(0x150, '\x00')
      #print repr(dataBlock)
      #print repr(data)
      temp = struct.unpack('<h',data[0:struct.calcsize('<h')])[0]/10.0
   else:
      data, error, dataBlock = DetsCommand(0x33,'\x00') #get temp
      tempMeas = extrBinSegment(dataBlock,{'temp':(4,'>H')})
      temp = tempMeas['temp'][0]/10.0

   return temp

def clearEWLM():
   """
   Clear SMART work log page.
   """
   data, error, dataBlock = DitsCommand(0x174, '\1\0\1\0')
   return data, error, dataBlock

def spinUpDrive():
   DetsCommand(0x1C,'')

def spinDownDrive():
   DetsCommand(0x1B,'')

def readCAP(useDITS = True, paramID = '\x00'):
   """
   Read cap value at defined paramID
   ParmId is the ID of the CAP Parameter whose value is to be retrieved. It is
   defined as follows and passed in as a binary string (eg '\x01':
   00 = Validation Key
   01 = HDA Serial Number
   02 = PCBA Serial Number
   03 = PCBA Part Number
   04 = Head Count
   05 = Node Name Validation Key
   06 = Node Name
   07 = Product Family ID
   08 = Product Family Member ID
   09 = PCBA Build Code
   0A = ASIC Information
   0B = Firmware Key
   0C = Firmware Key Checksum
   0D = Date of Manufacture
   0E = Destroked Buf Size Index
   0F = Final Mfg Op
   10 = Final Mfg Error Code
   11 = System Area Prep State
   12 = SPT Auto Run Delay
   13 = Reserved Bytes
   14 = Checksum
   """
   if useDITS:
      pass
   else:
      data, error, dataBlock = DetsCommand(0x15,paramID)
      if paramID in ['\x01']:
         lenID = (4,'8s')
      elif paramID in ['\x04']:
         lenID = (4,'B')
      else:
         print "Unsupported retrun data structure"
         lenID = None

      if lenID:
         return extrBinSegment(dataBlock,{'val':lenID})['val'][0]
      else:
         return dataBlock

def rwOptionsPacket(bitMask):
   """
   Bit 0:RwEntireTestSpace, if TRUE, indicates that the specified operation should be performed on the entire Test Space.  If FALSE, the specified operation should only be performed on the sectors / wedges specified by the Target Address andTransfer Length.
   Bit 1:RotateBufferSectorOffset, if TRUE, indicates that the target buffer sector offset will be rotated for every read/write target address diagnostic function. This bit was originally created to help reduce time when writing random data pattern. By rotating the target buffer sector offset, re-filling up the diagnostic buffer with new random data won't be necessary since re-using existing random data pattern at the differenct buffer sector offset will give similar effect in term of read channel point of view.
   Bit 2:UnusedBit2 is an unused bit.
   Bit 3:EnableDynamicSparing, if TRUE, indicates that sectors containing media defects that meet the failure criteria should by spared.
   Bit 4:ContinueOnError, if TRUE, indicates that an attempt should be made to read or write all of the requested sectors and a status packet should be returned for each sector  in error.  If ContinueOnError is FALSE, sequence execution will stop when an error occurs and a single status packet will be returned for the sector in error.
   Bit 5:ContinueOnECCError, if TRUE, indicates that ECC errors should not halt disc transfer and an attempt should be made to read or write all of the requested sectors. If ContinueOnECCError is FALSE, sequence execution will stop when an ECC error occurs and a single status packet will be returned for the sector in error.
   Bit 6:ContinueOnSyncError, if TRUE, indicates that sync mark timeout error should be ignored and sync error count and sync error secotr/wedge list should be provided at the end of the transfer.  If ContinueOnECCError is FALSE, sequence execution will stop when a sync timeout error occurs and a single status packet will be returned for the sector in error.
   """
   return listToMask(bitMask)


def rwSubCmd(cmd, rwOptions = 0, timeout = 300):
   #rwSeqComplete = '\x00\x00\x00\x00\x00\x00\x00\x00'#struct.pack("BxxxL",0,0)
   rwSeqComplete = '\x00'#struct.pack("BxxxL",0,0)
   #rwSeqComplete = ''
   data, error, dataBlock = DetsCommand(0x27,struct.pack('BxxxL',cmd, rwOptions) + rwSeqComplete, timeout = timeout) # per documentation
   evalRwSense(dataBlock)
   return data, error, dataBlock

def writeTrack(rwOptions = 0, timeout = 300):
   data, error, dataBlock = rwSubCmd(rwSubCmdEnum.WRITE, rwOptions)
   objMsg.printBin(dataBlock)
   objMsg.printMsg(repr(data))
   return data, error, dataBlock

def readTrack(rwOptions = 0, timeout = 300):
   return rwSubCmd(rwSubCmdEnum.READ, rwOptions)

def seekTrack(seekType, offset = 0, reloadChannel = True):
   data, error, dataBlock = DetsCommand(0x26,struct.pack('BBHBB', seekType, 0, offset, 0, int(reloadChannel)))
   return evalRwSense(dataBlock)

def setTestSpace(testSpaceParameter, options):
   data, error, dataBlock = DetsCommand(0x24,struct.pack('Bxxx',testSpaceParameter) + options)
   objMsg.printMsg(repr(data))

def setDefaultTestSpace():
   setTestSpace(1,'')

def setLogicalTargetSpace():
   setTestSpace(0x2, chr(0x1))

def setTargetAddressMode_LBA():
   setTestSpace(0x2, chr(0x0))


def setMinMaxLogicalHead(minHead, maxHead):
   setDefaultTestSpace()
   setTestSpace(0xA, struct.pack('B',minHead))
   setTestSpace(0xD,struct.pack('B',maxHead))

def setMinMaxLogicalTrack(minTrack, maxTrack, head):
   setDefaultTestSpace()
   setTestSpace(0x4, struct.pack('LB',minTrack, head))
   setTestSpace(0x7,struct.pack('LB',maxTrack, head))

def setTargetTrack(track, head, sector = 0):
   data, error, dataBlock = DetsCommand(0x25,struct.pack('BBBxLBxBL' ,1,1,2,track,head,sector,track))

def setTargetSectorAndXferLen(sector, transferLength):
   data, error, dataBlock = DetsCommand(0x25,struct.pack('BBBxHxxxxxxBxxxL' ,1,1,5,sector,1,transferLength))


def listToMask(bitMask):
   if type(bitMask) in [types.ListType, types.TupleType]:

      return sum([val<<index for index,val in enumerate(bitMask)])
   else:
      return bitMask

def setSeqRndSpace(bitMask):
   """
   Bit 0:AllHds, if TRUE, all heads (Minimum Head to Maximum Head) will be accessed.  If FALSE, only the current head will be accessed.
   Bit 1:AllCyls, if TRUE, all cylinders (Minimum Cylinder to Maximum Cylinder) will beaccessed.  If FALSE, only the current cylinder will be accessed.
   Bit 2:RandomCylAndHd, if TRUE, the cylinder and head address will be updated randomly.If FALSE, the cylinder and head address will be updated sequentially.
   Bit 3: spare0 is an unused bit.
   Bit 4:EvenCyls, if TRUE, only even numbered cylinders will be accessed.
   Bit 5:OddCyls, if TRUE, only odd numbered cylinders will be accessed.
   Bit 6:SequentialOut, if TRUE, the cylinder and head address will be updated sequentiallyfrom the Inner Diameter to the Outer Diameter.  If FALSE, the cylinder and head address will be updated sequentially from the Outer Diameter to the Inner Diameter.
   Bit 7:RandomData, if TRUE, random data will be used for disk write operations.  If FALSE,the existing buffer data will be used for write operations.
   Bit 8:RandomStartingSector, if TRUE, a random starting sector will be used for read/write operations.  If FALSE, read/write operations will start at sector 0.
   Bit 9:RandomTransferLength, if TRUE, a random transfer length will be used for read/write operations.
   Bit 10:spare1 is an unused bit.
   Bit 11:Sequential80Random20, if TRUE, the cylinder and head address will be updated sequentially 80% of the time and randomly 20% of the time.
   Bits 12-31:spare2 is a collection of unused bits.
   """
   bitMask = listToMask(bitMask)
   setTestSpace(0x3, struct.pack('L',bitMask))

def setRetries(mode = False, options = False, maxReadRetryLevelAllowed = False, maxWriteRetryLevelAllowed = False, selectedRetryStep = False, selectedOtfEccSetting = False, maxReadRetryCount = False, maxWriteRetryCount = False):
   Pad = -1
   selBitsVal = [mode, Pad, Pad, options, maxReadRetryLevelAllowed, maxWriteRetryLevelAllowed, selectedRetryStep, selectedOtfEccSetting, Pad, maxReadRetryCount, maxWriteRetryCount]
   selBitsMask =['B', 'B', 'B', 'L', 'B', 'B', 'H', 'B', 'B', 'H', 'H']
   selbits = struct.pack('BBBBBBBB', *[int(i>0) for i in selBitsVal if not i == -1])

   loc = selBitsVal.index(-1)
   while -1 in selBitsVal:
      selBitsVal[selBitsVal.index(-1)] = 0

   selBitsBin = ''.join([struct.pack(fmt,val) for fmt, val in zip(selBitsMask, selBitsVal)])
   data, error, dataBlock = DetsCommand(0x2E,selbits + '\x00' + selBitsBin)


def setNormalRetries():
   setRetries(mode = 2)

def setMaxRetries():
   setRetries(mode = 1)

def getGList(list_type = (1<<0)):
   #define  USER_DDT_LIST_MASK            BIT0
   #define  SYSTEM_DDT_LIST_MASK          BIT1
   #define  USER_RST_LIST_MASK            BIT2
   #define  SERVO_FLAWS_LIST_MASK         BIT3
   #define  PLIST_MASK                    BIT4
   #define  PRIMARY_SERVO_FLAWS_LIST_MASK BIT5
   #define  G_LIST_NONRESIDENT_MASK       BIT6
   #define  G_LIST_RESIDENT_MASK          BIT7
   #define  PRIMARY_DST_LIST_MASK         BIT8
   #define  LIST_BY_INDEX_AND_COUNT       BIT15

   #SDB returns for list type
   #Resident_DST = 0
   #Primary_DST = 1
   #Grown_DST = 2

   listMask = list_type
   chosenHead = 0
   defLogCyl = 0
   index = 0
   elementCount = 1
   cylinders = 1
   indicies = 1
   extraSummaryRequested = 0

   data, error, dataBlock = DetsCommand(0xAE,struct.pack('LLLLLLB',listMask, chosenHead, defLogCyl, index, cylinders, indicies, extraSummaryRequested))
   dsb = {  'numEntries':(4,'L'),
            'numEntriesOnDrive':(8,'L'),
            'fileType': (12,'B')
         }
   defInfo = extrBinSegment(dataBlock,dsb)
   print "numEntries %d" % defInfo['numEntriesOnDrive']

def readDriveTable(driveTableNum = 21, memOffset = 0, transferLength = 0, address = True, Flash = True):
   return DitsCommand(0x14B,data = struct.pack('BBxxLxxH',((int(address)<<1) + (int(Flash)<<0)), driveTableNum, memOffset, transferLength))

def readLogExtended(logNumber, blockOffset = 0, blockXferLen = 1, logSpecific = 0):
   """
   Reads a smart log from disc
   """
   # logSpecific,BlockCount,LogAddress(num),x,PageNum(BlockOffset)

   smartLogFmt = 'HHBxH'
   data, error, dataBlock = DetsCommand(0xF5, struct.pack(smartLogFmt, logSpecific, blockXferLen, logNumber, blockOffset ))
   if testSwitch.virtualRun:
      return dataBlock[8:]
   objMsg.printMsg("Dets data: %s, len: %s" % (data,len(data)))
   outFmt = 'HHHH%ss' % (512*blockXferLen) # dataBlock format => DSB length 8B + Data 512B
   output = struct.unpack(outFmt, dataBlock)
   
   return output[4]

def readPPID ():
    # Command reads smart log but for now functionality is only for PPID
   data, error, dataBlock = DetsCommand(0x326, struct.pack('3HB',0,0x17,0,1))
   PPID = data[15:39]
   return PPID
   
def writePPID (writePPID ):
     # Command writes smart log but right now functionality is only for PPID
   data, error, dataBlock = DetsCommand(0x327, struct.pack('3HB23s', 0, 0x17, 0, 1, writePPID))
   return data, error, dataBlock

def setATASpeed (speed, functionCode = 0x3):
   ''' This command sets the BIST Speed Control Setting. (other BIST functionality is not supported yet) 
       functionCode = 3 - SET_SATA_PHY_SPEED - Changes the max allowable negotiation speed.  
   '''
   objMsg.printMsg("sdbpCmds.py setATASpeed=%s" % speed)
   data, error, dataBlock = DetsCommand(0x328, struct.pack("B7L", functionCode, 0, 0, 0, 0, 0, 0, speed))
   objMsg.printMsg("setATASpeed data=%s" % repr(data))

def readDriveTableAddress(driveTableNum = 21, memOffset = 0, transferLength = 0, address = True, Flash = True):
   data, error, dataBlock = readDriveTable(driveTableNum , memOffset , transferLength , address , Flash )
   return extrBinSegment(dataBlock,{'startAddress':(0,'L'), 'size':(4,'L')} )

def writeFlashToFile(fobj):
   """fobj must be an open file object... open as 'wb'"""
   flashFileNum = 21
   flashInfo = readDriveTableAddress(driveTableNum =flashFileNum)
   blockSize = 512
   for index, blockStart in enumerate(range(flashInfo['startAddress'][0],flashInfo['size'][0],blockSize)):
      data, error, dataBlock = readDriveTable(driveTableNum = flashFileNum, memOffset = blockStart, transferLength = blockSize, address = False, Flash = True)
      if index % 10 == 0:
         print "Writing block number %d" % index
      fobj.write(dataBlock)

def initializeDefectList(userSlipList = 0, userAltList = 0, SaveToDisc = 0):
   data, error, dataBlock = DitsCommand(0x3F, data = struct.pack('L', (userSlipList<<0) + (userAltList<<2) + (SaveToDisc<<31)))

def getDriveGeometry():
   data, error, dataBlock = DetsCommand(0x31, '')
   numHeads = struct.unpack('B',dataBlock[9])
   cylLimits = {}
   cylSize = struct.calcsize('L')
   for head in xrange(numHeads):
      cylLimits[head] = (struct.unpack(dataBlock[4*head+12:4*head+12+cylSize], 'L'), struct.unpack(dataBlock[4*head+60:4*head+60+cylSize], 'L'))

   return numHeads, cylLimits

def getDriveBasicInformation():
   data, error, dataBlock = DetsCommand(0x80,'')
   return extrBinSegment(dataBlock, {'BufferSizeInBytes':(580,'L'), 'IoedcEnabled':(823,'B'),'IoeccEnabled':(824,'B')})

def getSmartFrameSize():
   data, error, dataBlock = DitsCommand(0x152, struct.pack('<BxHxxxxxxxx', 0xF, 1))
   return struct.unpack('L', dataBlock[:struct.calcsize('L')])

def getCurrentSmartFrame():
   data, error, dataBlock = DitsCommand(0x152, '\x03')
   return dataBlock

def drivePairing(cmd, keysToSet):
   import binascii
   validKey = struct.pack('17s','SeagateDPS')
   data, error, dataBlock = DetsCommand(0xD1,struct.pack('Hxx',cmd) + validKey + binascii.unhexlify(keysToSet), RevID=2) # per documentation
   return data, error, dataBlock

def SeaCorder():
   return UDSCommand(0x8, struct.pack("L",0x300919C1))

def resetUDS():
   data, error, dataBlock = UDSCommand(0x8, struct.pack("L",0x06091901))
   return dataBlock

def binData(data, binSize = 1000, numberOfBins = 50):
   # Returns a list of counts for each bin based on inputs
   binSize = int(binSize)
   bins = [0,]* numberOfBins#( (max(data)/binSize) + 1)

   for item in data:
      index = item/binSize
      if index >= numberOfBins:
         bins[-1] += 1 #put the count in the last bin
      else:
         bins[index] += 1

   return bins
   

def fullPackSequentialTiming(xferType, startLBA, endLBA, XferLenInHostBlks = 0xFFFF, StepSize = 0xFFFF, SampleCount = 0xFFFF, ErrorFlag = 0, timeout = None):
   maxLbaRange = 0xFFFF
   totalResults = []
   #for startRangeLba in xrange(startLBA, endLBA, maxLbaRange):
   startRangeLba = startLBA
   noGap = False
   if StepSize == XferLenInHostBlks:
      noGap = True
   while startRangeLba < endLBA:

      #if the requested transfer length is longer than we can handle in one transfer
      if noGap:
         thisMaxLba = min(startRangeLba + maxLbaRange, endLBA)
         res = lbaSequentialTiming(xferType, startRangeLba, thisMaxLba, XferLenInHostBlks, SampleCount, ErrorFlag, timeout)
         totalResults.extend(res)

         #since we have transferred these blocks but increment from the start of each transfer reset
         startRangeLba += (thisMaxLba-startRangeLba)
   
      else:
         subXfr = XferLenInHostBlks
         while subXfr > 0:
            xfrLen = min( XferLenInHostBlks, maxLbaRange)
            res = lbaSequentialTiming(xferType, startRangeLba, min(startRangeLba + xfrLen, endLBA), xfrLen, SampleCount, ErrorFlag, timeout)
            startRangeLba += xfrLen
            subXfr -= xfrLen
            totalResults.extend(res)

         #since we have transferred these blocks but increment from the start of each transfer reset
         startRangeLba -= XferLenInHostBlks
   
         startRangeLba += StepSize
   return totalResults


def lbaSequentialTiming(xferType, startLBA, endLBA, XferLenInHostBlks = 0xFFFF, SampleCount = 0xFFFF, ErrorFlag = 0, timeout = None):
   #maxidema = 24630D9B0

   if timeout == None:
      scaler = XferLenInHostBlks * 0.02 # 100 retries at 5400RPM as a scaler.. if xfer len is to small this doesn't work
      timeout = (endLBA - startLBA)/float(XferLenInHostBlks) * scaler   
      
   #objMsg.printMsg( "Using timeout of %f" % timeout )
   #objMsg.printMsg( "Using SampleCount of 0x%X" % SampleCount )


   Options = ErrorFlag & 0xFE
   #objMsg.printMsg( " xferType, Options = %s %s " % ( xferType, Options ))
  
   binData = struct.pack('<BBHQQL', xferType, Options, SampleCount, startLBA, endLBA, XferLenInHostBlks )

   data, error, dataBlock = DetsCommand(0x30E, binData, timeout = timeout)
   dsbRev = struct.unpack("<H", data[2:4])[0]

   respPat = '<QLL'
   if testSwitch.virtualRun:
      dataBlock = struct.pack(respPat, 0, 512, 15000)
   respSize = struct.calcsize(respPat)
   measData = []

   if dsbRev > 1:
      for index in xrange(0, len(dataBlock), respSize):
         measData.append(struct.unpack(respPat, dataBlock[index:index+respSize]))
           
   else:  # rev 1 reports disc LBAs instead of expected host LBAs, so we need to multiply the lba by 8 
      for index in xrange(0, len(dataBlock), respSize):
         resTuple = struct.unpack(respPat, dataBlock[index:index+respSize])
         measData.append((resTuple[0] * 8, resTuple[1],resTuple[2]))
       
   return measData


def writeSmartLog(logNumber, logData, valueForOptions = None):
   """
   Writes a smart log to disc
   """
   # logNum, ByteXferlen, Offset, Options (), value for Options, FileData
   valueForOptionsLen = 64
   if valueForOptions == None:
      valueForOptions = ' ' * valueForOptionsLen
   Options = 0 #specified log number
   byteXferLen = len(logData)
   smartLogFmt = 'HHHB%ds%ds' % (valueForOptionsLen, byteXferLen)

   data, error, dataBlock = DetsCommand(0x327, struct.pack(smartLogFmt, logNumber, byteXferLen, 0, Options, valueForOptions, logData ))
   return error

def readLogExtended(logNumber, blockOffset = 0, blockXferLen = 1, logSpecific = 0):
   """
   Reads a smart log from disc
   """
   # logSpecific,BlockCount,LogAddress(num),x,PageNum(BlockOffset)

   smartLogFmt = 'HHBxH'
   data, error, dataBlock = DetsCommand(0xF5, struct.pack(smartLogFmt, logSpecific, blockXferLen, logNumber, blockOffset ))
   if testSwitch.virtualRun:
      return dataBlock[8:]
   outFmt = 'HHHH%ss' % (512*blockXferLen)
   output = struct.unpack(outFmt, dataBlock)

   return output[4]

def getCAPsettings (ParmID = 0x00):
   data, error, dataBlock = DetsCommand(0x0015, struct.pack('Bxxx',ParmID))
   return data, error, dataBlock

