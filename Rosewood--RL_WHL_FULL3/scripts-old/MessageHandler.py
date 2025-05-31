#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Handles all printing routines in common object that has global verbosity and formatting controls
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/MessageHandler.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/MessageHandler.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#

from Constants import *
import re, os, binascii, types, struct, string, traceback
from tabledictionary import tableHeaders
global processorStatsSupported, iCurrentMsgLevel

processorStatsSupported = 1
crcConst = 604 # arbitrary seed value

memParse = re.compile("(?P<Sz>\d+)\s*(?P<RSS>\d+)\s*(?P<Size>\d+)\s*(?P<DRS>\d+)\s*(?P<VSZ>\d+)")
ALL_CHARACTERS = string.maketrans('','')
NON_PRINTABLE_CHARACTERS = ALL_CHARACTERS.translate(ALL_CHARACTERS,string.printable)
PRINTABLE_TRANSLATE = "".join((ch in string.printable) and ch or '.' for ch in string.maketrans('',''))

if testSwitch.virtualRun:
   try:
      import winPyProcessInfo
      import os
      pid = os.getpid()

      hProcess = winPyProcessInfo.getProcessHandle(pid)
   except:
      processorStatsSupported = 0

class CMessLvl:
   """
   CMessLvl
      @cvar CRITICAL: Failure Information
      @cvar IMPORTANT: Retry Information
      @cvar DEBUG: Process flow documentation and status messages.
      @cvar VERBOSEDEBUG: Simple Data output and boolean logic results.
   """
   RESULTSLOG      = 1 * ConfigVars[CN].get('resultsLog',1)
   REPORTSTATUS    = 2 * ConfigVars[CN].get('reportstatus',0)
   TRACELOG        = 4 * ConfigVars[CN].get('traceLog',0)
   ANOTHERLOG      = 8 * ConfigVars[CN].get('anotherLog',0)

   CRITICAL        = RESULTSLOG + REPORTSTATUS
   IMPORTANT       = RESULTSLOG + TRACELOG
   DEBUG           = RESULTSLOG + TRACELOG + REPORTSTATUS
   VERBOSEDEBUG = RESULTSLOG + TRACELOG + ANOTHERLOG

#------------------------------------------------------------------#
def CreateTableDictByName():
   tabledict = {}
   for code, tableinfo in tableHeaders.items():
      tabledict[tableinfo[0]] = code
   return tabledict

#------------------------------------------------------------------#
def setMessageLevel( iMsgLevel):
   global iCurrentMsgLevel
   if iMsgLevel <= 1+2+4+8: #CMessLvl.VERBOSEDEBUG:
      iCurrentMsgLevel = iMsgLevel
      #print("Setting message level to: " + str(iMsgLevel))
   else:
      ScriptComment("ERROR: Invalid message level= " + str(iMsgLevel))
      raise Exception("ERROR: Invalid message level= " + str(iMsgLevel))
   return iMsgLevel

#------------------------------------------------------------------#

codeByNamedict = CreateTableDictByName()

try:
   iCurrentMsgLevel = setMessageLevel(ConfigVars[CN]['MessageOutputLevel'])
except:
   ScriptComment("Attempted: %s" % (ConfigVars[CN]['MessageOutputLevel'],))
   if ConfigVars[CN].get('PRODUCTION_MODE',0):
      iCurrentMsgLevel = setMessageLevel(CMessLvl.IMPORTANT)
   else:
      TraceMessage("Invalid Messaging level attempted...Setting to default: VERBOSEDEBUG")
      ScriptComment("Invalid Messaging level attempted...Setting to default: VERBOSEDEBUG")
      iCurrentMsgLevel = setMessageLevel(CMessLvl.VERBOSEDEBUG)

#------------------------------------------------------------------#
def setFormating( sMsg, iMsgLevel, leftAdder = ''):
   """
   Format the message appropriate to the notification level
   """

   if iMsgLevel == CMessLvl.CRITICAL:
      sMsg = sMsg.upper()

##      if iMsgLevel == CMessLvl.IMPORTANT:
##         pass
##      if iMsgLevel == CMessLvl.DEBUG:
##         pass
##      if iMsgLevel == CMessLvl.VERBOSEDEBUG:
##         pass
   return sMsg

#------------------------------------------------------------------#
def printMsg( sMsg, iMsgLevel = 7, rawWrite = 0, leftAdder = ''):
   """
      Print Message if that level of messaging is enabled.
      Inputs: String sMsg and integer iMsgLevel
   """

   global iCurrentMsgLevel
   sMsg = str(sMsg)

   # Fast method to chose character if printable or hex repr if not printable
   PRINTABLE = string.printable
   sMsg = "".join([(ch in PRINTABLE) and ch or '_x%02X_' % ord(ch) for ch in sMsg])

   sMsg = setFormating(sMsg,iMsgLevel, leftAdder)

   if (iCurrentMsgLevel >= iMsgLevel):
      if iMsgLevel & CMessLvl.RESULTSLOG:
         try:
            if rawWrite == 0:
               ScriptComment(sMsg)
            else:
               WriteToResultsFile(sMsg)
         except:
            ScriptComment("Failed to print message")
      if iMsgLevel & CMessLvl.REPORTSTATUS:
         try:
            if not ConfigVars[CN].get('PRODUCTION_MODE',0):
               ReportStatus(sMsg)   #Report Critical messages to the host status screen
         except:
            ReportStatus("Failed to print message")
      if iMsgLevel & CMessLvl.TRACELOG:
         try:
            if not testSwitch.virtualRun == 1: TraceMessage(sMsg)
         except:
            TraceMessage("Failed to print message")
      if iMsgLevel & CMessLvl.ANOTHERLOG:
         #Placeholder for immediate expansion
         pass

#------------------------------------------------------------------#
def __renderDict( inputDict, left = ''):
   if type(inputDict) == types.DictType:
      outData = ""
      for (key,value) in inputDict.iteritems():
         if type(value) == types.DictType:
            outData += "\n%s%s : %s" % (left, key,__renderDict(value, '\t'+left))
         else:
            outData += "\n%s%s : %s" % (left,key, value)
      return outData
   else:
      return "%s%s" % (left,inputDict)

#------------------------------------------------------------------#
def printDict( inputDict, iMsgLevel = 7, colWidth = 7, keyExtract = '', leftAdder = ''):
   printMsg(__renderDict(inputDict))

#------------------------------------------------------------------#
def printBin(binData,lineWidth = 32, iMsgLevel = 7):
   """
   Description: Prints out binary data as text string to results file.
   Implementation: based on Sumit Gupta's WinFOF routine.
   """
   chars = [binascii.hexlify(ch) for ch in binData]
   __printBin(chars,lineWidth, iMsgLevel = 7)

#------------------------------------------------------------------#
def printBinAscii(binData,lineWidth = 32, iMsgLevel = 7):
   """
   Description: Prints out binary data as text string to results file.
   Implementation: based on Sumit Gupta's WinFOF routine.
   """

   binData = binData.translate(PRINTABLE_TRANSLATE)
   __printBin(binData,lineWidth, iMsgLevel = 7)

#------------------------------------------------------------------#
def __printBin( chars,lineWidth, iMsgLevel = 7):
   result = ""
   while chars:
      for group in xrange(lineWidth/8):
         charSet,chars = chars[:8],chars[8:]
         result = "%s%s   " % (result," ".join(charSet),)

         if not chars: break

      result = "%s\n" % (result.strip(),)

   printMsg(result, iMsgLevel = 7)

#------------------------------------------------------------------#
def cleanASCII(data):
   return data.translate(ALL_CHARACTERS,NON_PRINTABLE_CHARACTERS)

#------------------------------------------------------------------#
def isPrintable(inString):
   """
   Function returns whether string is printable- all printable ascii chars or not
   """
   return inString == cleanASCII(inString)

#------------------------------------------------------------------#
def getMemVals(force = False):
   if ConfigVars[CN].get("PRODUCTION_MODE",False) and force == False:
      matchDict = {'Sz':'', 'RSS':'', 'VSZ':''}
   else:
      try:
         memStr = memoryCheck()
         matches = memParse.search(memStr)
         if not matches == None:
            matchDict = matches.groupdict()
         else:
            printMsg("ERROR in getMemVals: CM returned '%s'" % str(memStr))
            matchDict = {}

         if testSwitch.virtualRun:

            if processorStatsSupported:
               #test out parser for real running
               global hProcess
               dret = winPyProcessInfo.getProcessMemoryInfo(hProcess)
               matchDict = {'VSZ':dret.WorkingSetSize/1024.0, 'Sz':dret.WorkingSetSize/1024.0, 'RSS':dret.PagefileUsage/1024.0}
      except:
         if testSwitch.virtualRun:printMsg(traceback.format_exc())
         printMsg("ERROR in getMemVals: CM returned '%s'" % str(memStr))
         matchDict = {}
   return matchDict

#------------------------------------------------------------------#
def getCpuEt(force = False):
   """
   Return the amount of CPU time used by the current process so far.

   This function accesses Linux's 'proc' pseudo file system to get the CPU
   time.  It reads the line that's in the 'stat' pseudo file.  The line
   read from the 'stat' pseudo file is a string which has a number of fields
   all chained together.  The format is taken from the Linux documentation
   which lists the names and meanings of the fields in order.  Two of these
   fields, utime and stime, are extracted and summed together for generating
   the elapsed CPU time.  The position in the stat string in which these two
   fields occur is assumed by this function.

   The utime and stime data are in units of 'jiffies'.  This function has
   built into it an assumption about the number of jiffies per second so
   that the result it returns is in seconds.

   See the Linux man page on 'proc' for background info on utime and stime.

   The entire function is stubbed and returns zero if running in virtual
   execution mode or in winFOF or in PRODUCTION_MODE
   """
   global processorStatsSupported
   if processorStatsSupported:

      if testSwitch.virtualRun or testSwitch.winFOF:
         try:
            if processorStatsSupported:
               global hProcess
               usertime, kernelTime = winPyProcessInfo.getProcessTimes(hProcess)
               cpuEt = usertime
               processorStatsSupported = 1
            else:
               processorStatsSupported = 0
               cpuEt = 0.0
         except:
            processorStatsSupported = 0
            cpuEt = 0.0
         return cpuEt


      if (ConfigVars[CN].get("PRODUCTION_MODE",False) and force == False):
         cpuEt = 0.0
      else:
         IDX_UTIME = 13    # assume index to utime is 13
         IDX_STIME = 14    # assume index to stime is 14
         JPS = 100.0       # assume 100 "jiffies" per second
         try:
            proc_stats = open('/proc/self/stat').read().split()
            utime = int(proc_stats[IDX_UTIME])/JPS
            stime = int(proc_stats[IDX_STIME])/JPS
            cpuEt = utime + stime
         except:
            printMsg("processor stats not supported.")
            processorStatsSupported = 0
            cpuEt = 0.0
   else:
      cpuEt = 0.0

   return cpuEt

#------------------------------------------------------------------#
def convToInt(dataVal):
   if type(dataVal) == types.StringType:
      return int(eval(dataVal)) #Remove multiple sets of quotes for VE
   else:
      return int(dataVal)

#------------------------------------------------------------------#
def getTableData(tableName):
   """Load table data from tabledictionary.py"""

   # Find entry in tabledictionary
   tableCode = codeByNamedict[tableName]
   tableEntry = tableHeaders[tableCode]

   # Parse
   tableName = tableEntry[0]
   columnNames = tableEntry[1].split(',')
   columnWidths = list(tableEntry[4])
   return tableName, columnNames, columnWidths

def justify(text, width):
   return text.rjust(width)

def lineFormat(data, widths):
   """Format the DBLog row and return the complete string"""

   # Pad missing data with ???
   if len(data) < len(widths):
      data = data + ["???"] * ( len( widths ) - len( data ) )

   # Assume widths of 5 for extra columns
   elif len(data) > len(widths):
      widths = widths + [5] * ( len( data ) - len( widths ) )

   # Convert data to strings
   stringData = map(str, data)

   # Justify the columns
   justified = map(justify, stringData, widths)

   # Pad the columns and create a single string
   return " " + "  ".join(justified)

#------------------------------------------------------------------#
def printDblogBin( objdblTable, parseSpcId=[None], spcId32=None, testTimeSec=0):
   """
   Prints DbLog Object data to test results file in binary. ASCII data optionally
   printed for use by DEX. SPC_ID32 should be used for > 4 bits in desired spc_id
      @type objdblTable: Object
      @param objdblTable: Data object formatted using DBLog class
      @type parseSpcId: Int or List
      @param parseSpcId: List of spc_id's to constrain data set. This functionality
            is OVERRIDDEN by spcId32 use to prevent DbLog/DEX conflict.
      @type spcId32: Integer
      @param spcId32: SPC_ID32 to print to results file in ASCII
      @type testTimeSec: Float
      @param testTimeSec: Test time in seconds to print to results file in ASCII
   """
   setPartial = lambda testNumber: testNumber | 0x8000

   from Parsers import DbLogParser
   from Drive import objDut

   if not codeByNamedict.has_key(objdblTable.tableName):
      printMsg("Table Code not found in tabledictionary")
      printMsg(str(objdblTable))
      return

   procTestNumber = 887
   errorCode = 0
   dummyParams = [0,]*10

   nrecords = len(objdblTable)

   # capitalized is unsigned.
   resultsHeaderFormat = ( # 4-byte tester record header
      "<"                  # little endian
      "H"                  # 2-byte - Size of entire record (bytes)
      "b"                  # 1-byte - Results Key, 2:Send test completion results to tester, 3:Send intermediate test results to tester, and others
      "B"                  # 1-byte - Collect parametric flag
      )
   dataHeaderFormat = (    # 5-byte firmware record header
      ">"                  # big endian
      "H"                  # 2-byte - Test number
      "H"                  # 2-byte - Error code
      "b"                  # 1-byte - Block type, The block type is a hardcoded value of 1. This field is for future use.
      )

   crcFormat = ">H"        # 2-byte CRC check, big endian
   tableCodeFormat = "H" #2 bytes

   bindata = []

   def sendBlock(blockRecords, recDataLen, partial = False, spc_id = None):
      if spc_id == None:
         spc_id = objDut.objSeq.curRegSPCID
         if spc_id == None:
            spc_id = -1
      # if 32bit spc_id upper bytes only filled need to fill a lower byte to get btr to allow dex to collect parametrics
      #  until the spc_id32 in results file is added to this code
      if type(spc_id) != type(1):
         try:
            spc_id = int(spc_id)
         except:
            printMsg("Invalid spc_id passed to sendBlock %s" % (spc_id,))
            spc_id = -1

      if spc_id >= 0:
         if (spc_id & 0xF) == 0:
            spc_id |= 1 #enable collection
         spc_id_val = int(spc_id) | 0x40 #Add script added spcid val
         spc_id_val &= 0x7F # truncate to 'b' format
      else:
         spc_id_val = spc_id & 0xFF
      

      # If the "Transfer type" from the firmware record indicates intermediate results,
      #  the tester sets the high bit of the test number in the firmware record header.
      # If the "Transfer type" indicates final results, the test number is left alone.
      if partial:
         testNum = procTestNumber | 0x8000
      else:
         testNum = procTestNumber

      blockType = 1
      if testSwitch.virtualRun:
         try:
            dataHeader = struct.pack(dataHeaderFormat, testNum, errorCode, blockType)
         except:
            # ignore bad data.
            printMsg("sendBlock/ BAD DATA - dataHeaderFormat: %s, testNum: %s, errorCode: %s, blockType: %s" % (dataHeaderFormat, testNum, errorCode, blockType) )
      else:
         dataHeader = struct.pack(dataHeaderFormat, testNum, errorCode, blockType)

      size = len(dataHeader) + recDataLen + struct.calcsize(resultsHeaderFormat) + 2*struct.calcsize(crcFormat)
      ##ScriptComment("sending block size of %d" % size)
      if partial:      # resultsKey = 3 if partial == 0 else 2
         resultsKey = 3
      else:
         resultsKey = 2
      ##ScriptComment("resultsKey %d" % resultsKey)

      if testSwitch.virtualRun:
         try:
            resultsHeader = struct.pack(resultsHeaderFormat, size, resultsKey, spc_id_val)
         except:
            # ignore bad data.
            printMsg("sendBlock/ BAD DATA - resultsHeaderFormat: %s, size: %s, resultsKey: %s, spc_id_val: %s" % (resultsHeaderFormat, size, resultsKey, spc_id_val) )
      else:
         resultsHeader = struct.pack(resultsHeaderFormat, size, resultsKey, spc_id_val)

      blockRecords.insert(0, dataHeader)
      blockRecords = ["".join(blockRecords)]
      # Calculate the firmware/data CRC
      # First two bytes (test num) are not included in the CRC calculation
      rec = blockRecords[0][2:]
      # Pass the same arbitrary seed value (604 == throwing missiles) as firmware & tester do to ensure a CRC of 0's does not equal 0
      dataCRC = struct.pack(crcFormat, calcCRC(rec, len(rec), crcConst) & 0xFFFF)
      blockRecords.append(dataCRC)
      blockRecords.insert(0, resultsHeader)
      blockRecords = ["".join(blockRecords)]
      # Calculate the results/tester CRC
      rec = blockRecords[0]
      resultCRC = struct.pack(crcFormat, calcCRC(rec, len(rec), crcConst) & 0xFFFF)
      blockRecords.append(resultCRC)

      """
      Full Data block format is
      results header
         test data headers
            blockcode1: tablecode/data
            blockcoden: tablecode/data

      """

      #combine all of the data for output
      blockRecords = "".join(blockRecords)

      if testSwitch.virtualRun:
         pass
      else:
         #printBin(blockRecords)
         WriteToResultsFile(blockRecords)

   tableCode = struct.pack(tableCodeFormat, codeByNamedict[objdblTable.tableName])

   procCols = objDut.dblParser.procHeaders['cols']

   remCols = []
   spc_id_pos = -1
   for index, columnObj in enumerate(objdblTable.tableDef['fieldList']):
      curColname = columnObj.getName()
      if 'SPC_ID' == curColname:
         spc_id_pos = index

      if curColname in procCols:
         remCols.append(curColname)

   # Set this true to chop out the "header" columns like SPC_ID
   if len(remCols) > 0:
      processHeaderColumnsInData = True
   else:
      processHeaderColumnsInData = False

   recDataLength = 0
   firstBlockCode = True
   spc_id = None

   #Want to print ASCII SPC_ID32 for DEX to pick up later
   if spcId32 != None and type(spcId32) in (types.IntType,types.StringType): #Only single value allowed
      parseSpcId = [convToInt(spcId32)]  #Override parseSpcId to prevent collision of DBLog vs. DEX translation
      ScriptComment('')
      ScriptComment("Parameters==>  ([%s, 0, 0, 0], [],)" %objDut.objSeq.curRegTest)
      ScriptComment("**SPC_ID32=%s  CMT=None" %parseSpcId[0])

   if type(parseSpcId) not in (types.ListType,types.TupleType):
      parseSpcId = [parseSpcId]

   for rec_idx, record in enumerate(objdblTable.Records()):

      record = list(record)
      recdata = ""

      if spc_id_pos > -1:
         spc_id = convToInt(record[spc_id_pos])

      # Find the location of the process columns
      if processHeaderColumnsInData:
         pcol_idx = objDut.dblParser.procTranslation[tableHeaders[codeByNamedict[objdblTable.tableName]][objDut.dblParser.tableTypeOff]]
         pcol_cnt = len(remCols)
         del record[pcol_idx:pcol_idx+pcol_cnt]

      recdata = ",".join(map(str, record))

      #Only add data to results file if spc_id in user-supplied list
      if (parseSpcId[0] != None) and (spc_id not in parseSpcId):
         continue

      if testSwitch.virtualRun:
         # Display the table in VE for binary difference checking
         name, columns, widths = getTableData(objdblTable.tableName)
         if firstBlockCode:
            printMsg(name)
            printMsg(lineFormat(columns, widths))
         printMsg(lineFormat(record, widths))

      rowData, firstBlockCode, blockCode =  __getRowData(tableCode,recdata,firstBlockCode)

      blockData = __getBlockData(blockCode,rowData)

      bindata.append(blockData)

      recDataLength = __getRecDataLen(bindata)
      if recDataLength > 511:
         del bindata[-1]
         recDataLength = __getRecDataLen(bindata)
         sendBlock(bindata, recDataLength, True, spc_id)

         #Recreate blockData so it has the appropriate block code
         rowData, firstBlockCode, blockCode =  __getRowData(tableCode,recdata,firstBlockCode)
         blockData = __getBlockData(blockCode, rowData)

         bindata = [blockData,]
         firstBlockCode = False

   recDataLength = __getRecDataLen(bindata)
   if recDataLength > 0:
      sendBlock(bindata, recDataLength, spc_id=spc_id)


def __getRecDataLen(bindata):
   return sum(map(len,bindata))


def __getBlockData(blockCode, rowData):
   blockCodeFormat = "HH" #blockSize, blockCode, 4 bytes (2, 2)
   blockCodeFormatSize = struct.calcsize(blockCodeFormat)

   blockSize =  blockCodeFormatSize + len(rowData)
   blockData = struct.pack(blockCodeFormat, blockSize, blockCode) + rowData
   return blockData


def __getRowData(tableCode, recdata, firstBlockCode):
   if firstBlockCode:
      blockCode = 11000
      rowData = tableCode + recdata

      firstBlockCode = False
   else:
      blockCode = 11002
      rowData = recdata
   return rowData, firstBlockCode, blockCode


def calcCRC(data, sizein, crc):
   for i in map(ord, data[0: sizein]):
      crc += (crc & 0x00AA) ^ i
   return crc