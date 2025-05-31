# --------------------------------------------------------------------------------------- #
#                                                                                         #
#                                   Seagate Confidential                                  #
#                                                                                         #
# --------------------------------------------------------------------------------------- #

# ******************************************************************************
#
# VCS Information:
#                 $File: //depot/TCO/DEX/writeresultsfunctions.py $
#                 $Revision: #2 $
#                 $Change: 319143 $
#                 $Author: rebecca.r.hepper $
#                 $DateTime: 2010/12/16 07:36:23 $
#
# ******************************************************************************
import struct,time,types,array


def ESGSaveResults(data,collectParametric=0):
  # Save results data to the 'binary' file.  This function is utilized by the manufacturing engineering FOF scripts
  
  # Calculate the size of the entire record, including four bytes header, plus data, plus two crc.
  # The equation below, as well as the array following, look odd because we move the first byte of data into the header.
  lenData = len(data)
  recordSize = 5 + lenData  # 4 + (data - 1) + 2

  # This array will hold the entire record: header, data, and crc.
  a1 = array.array('B',struct.pack('<Hb %ssH'%lenData,recordSize,0,data,0))

  # Take the 'results key' off the first byte of data and put it into the header.
  a1[2] = a1[3]

  # Put the parametric flag into the header.
  a1[3] = collectParametric

  # SET HI BIT IN TEST NUMBER IF THIS IS PARTIAL RESULTS
  # Strictly speaking, this is a hack, because we are tampering with the user's data.  Regardless, this step is required.
  if a1[2]==3: a1[4] |= 0x80

  # Calculate a CRC using a CM ScriptService and put it at the end of the record.
  # The CRC function returns a 32 bit value, but we pack it into a 16 bit value. in order to make a smaller overall record.
  # Use an arbitrary CRC seed value (604 == 'throwing missiles') because with a seed of 0 and data of all zeroes this 'CRC' will return a 0.
  crc = ScriptTools.calcCRCBlock(a1.tostring(),len(a1)-2,604)

  a1[-2] = (crc>>8)&0xFF  # High Byte
  a1[-1] = crc&0xFF       # Low Byte

  # CM ScriptService to write data to the results file
  WriteToResultsFile(a1.tostring())


def writeInterpDataBlock(blockCode,data,resultsKey,testNum=9999,collectParametric=0):  
  # Write a block of interpreted data to the results file.  This function is utilized by the manufacturing engineering FOF scripts. 

  dataBlockTemplate = "%s"

  # Make sure the data is a string
  blockData = ""   
  for piece in data:
     if not isinstance(piece,types.StringType):
        piece = `piece`
     blockData  = blockData  + piece

  # Set up size & blockcode for interpreted data; size is 2 bytes block size, 2 bytes block code plus the actual data 
  size = 4 + len(blockData)  
  str1 = struct.pack("HH",size,blockCode)
  blockData = "%s%s" % (str1,blockData) 

  # Set up length of the template
  tlen = len(dataBlockTemplate)    
  # Maximum length of our comment chunk
  cspace = 512-tlen     

  # Header data set up as 1 byte resultsKey, 2 bytes test number
  header1 = struct.pack(">bh",resultsKey,testNum) 
  # Additional header is 2 bytes fault code (hardcoded to 0), 1 byte block type (hardcoded to 1)
  header2 = "\000\000\001"
  
  # Use low nibble only, and set the COLLECT_PARAMETRIC (0x40) bit just like CM code does
  collectParametric = collectParametric | 0x40

  # Write chunks of data until data is exhausted
  while 1:
    if not blockData: break
    chunk = blockData[:cspace]
    blockData = blockData[cspace:]

    blockDataFormatted = dataBlockTemplate % chunk
    
    # Calculate a CRC using a CM ScriptService and put it at the end of the record.
    # The CRC function returns a 32 bit value, but we pack it into a 16 bit value. in order to make a smaller overall record.
    # Use an arbitrary CRC seed value (604 == 'throwing missiles') because with a seed of 0 and data of all zeroes this 'CRC' will return a 0.
    crcData = header2+blockDataFormatted
    crc = ScriptTools.calcCRCBlock(crcData,len(crcData),604)

    ESGSaveResults("".join((header1,crcData,struct.pack('>H',crc),)),collectParametric=collectParametric)


def writeSummaryTable(compCode=0,failingSeq="",failingTestNum="",failingTemp="",failingv5="",failingv12="",powerLossCnt=0):   
  # Write data for P_EVENT_SUMMARY parametric table to results file.  This function is utilized by the manufacturing engineering FOF scripts. 

  # ConfigId is a CM script environment variable
  configEquip,configProduct,configName,configVersion = ConfigId

  # Table code for P_EVENT_SUMMARY per table_cd.h
  summaryTableCode = 65000      
  tableCode = struct.pack("H",summaryTableCode)    

  # Some values are passed in, some are CM script environment variables and the ?number items are populated by DEX when it is run against the results file
  # FAILING_PORTID ?1; FAILING_EVENT ?2; FAILING_SQ_EVT ?3; FAILING_TST_EVT ?4; FAILING_TS_EVT ?5;  DBLOG_VER ?6; RUN_TIME ?7; PARAM_DICTIONARY_VER ?8
  tableData = "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % \
              ("?7",str(CellNumber),compCode,failingSeq,failingTestNum,0,"?1","?2","?3","?4","?5",failingv5,failingv12,failingTemp,SBR,HOST_ID,CMCodeVersion,HostVersion,configName,configVersion,"?6",powerLossCnt,"?8")  

  data = "%s%s" % (tableCode,tableData)
    
  # The last block of data from a test always has a results key of 2 - this will set the partial results flag to 0, otherwise it is set to 1
  writeInterpDataBlock(11000,data,resultsKey=2,collectParametric=1)
