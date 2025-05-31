#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Creates low overhead parsers for inLineDblog and various other required functions
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Parsers.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Parsers.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#

from Constants import *
from TestParamExtractor import TP
import DBLogDefs, stat, os, traceback
import ScrCmds, time, Utility
import struct
import types
import MessageHandler as objMsg
from DbLogAlias import dbLogTableAliases, dbLogTableAliasesMaster
from tabledictionary import *

objMsg.printMsg("Using tabledictionary for translation")

DEBUG = 0

class DbLogParser:
   """
   Class that handles parsing of dblog data structures from binary format and putting them in the required
   python memory structures and disc files (debug and binary) for later usage by the process.
   """

   BenchMark = 0
   raiseExceptions = 0

   ################ Module level constants
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
   procTranslation = {'S':0,'V':1,'M':2,}
   defProcTransl = 0
   ResultsFilePath = os.path.join(ScrCmds.getSystemResultsPath(),ScrCmds.getFofFileName(1))

   procHeaders = {'cols':['SPC_ID',   'OCCURRENCE',  'SEQ',   'TEST_SEQ_EVENT'],
                 'types':['V',        'N',           'N',     'N']}
   ################

   def __init__(self,dut):
      self.dut = dut
      self.objDbLogIndex = DbLogIndexFile()
      self.dblTableMaster = dbLogTableAliasesMaster

   def getRowData(self, data, processHeaderData, tableCode):
      """
      inserts the process header data into a raw row data output from the drive
      """
      data = data.split(self.dblDelim)
      # Insert the data 1 item at a time in reverse order so it ends up in the correct order

      processHeaderData = list(processHeaderData)
      processHeaderData.reverse()
      for item in processHeaderData:
         data.insert(self.procTranslation[tableHeaders[tableCode][self.tableTypeOff]], item)
      return data

   def addDbLogRow(self,data, tableCode, tableDef = {}, processHeaderData = [],returnRowDataonly = 0):
      """
      Function that returns the fully descibed python dblog row from a drive dblog string and table code.
      """
      try:
         rowData = self.getRowData(data, processHeaderData, tableCode)

         if DEBUG >2:
            objMsg.printMsg(str(rowData))

         try:
            tableName = tableHeaders[tableCode][self.tableNameOff]
         except KeyError:
            if self.raiseExceptions == 1:
               ScrCmds.raiseException(11044,"DBLOG Block code not defined: %s" % str(tableCode))
            else:
               objMsg.printMsg("DBLOG Block code not defined: %s" % str(tableCode))
               return

         tableColumns = self.getTableColumns(tableCode)


         if len(rowData) > len(tableColumns):
            tableColumns.extend(range(len(tableColumns), len(rowData)))
         elif len(tableColumns) > len(rowData):
            #Expand w/ Nulls if non DBLOG full row put string
            if testSwitch.BF_0136275_341036_DBLOG_FIX_NULL_DATA_INJECTION_ERROR == 1:
               DBLOG_NULL_DATA = ""
               rowData.extend([DBLOG_NULL_DATA for i in range(len(rowData),len(tableColumns))])
            else:
               rowData.extend(range(len(rowData),len(tableColumns)))

         if tableDef == {}:
            if DEBUG >0:
               objMsg.printMsg("Creating new tableDef %s" % str(tableDef))

            colTypes = self.getColTypes(tableCode,len(rowData))
            if DEBUG > 0:
               objMsg.printMsg(str(colTypes))
            tableDef = self.createDbLogDef(tableCode,tableColumns,colTypes)


         #Add the data to the dictionary for storage
         rowDict = dict(zip(tableColumns,rowData))


         if DEBUG > 0:
            objMsg.printMsg(str(rowData))
            objMsg.printMsg(str(rowDict))

            objMsg.printMsg(str(tableDef))
         if returnRowDataonly == 1:
            return rowDict
         ######################## Update global dbLog data
         if DEBUG >0:
            objMsg.printMsg("Now saving values to dbl tables...")

         self.dut.dblData.Tables(tableName, tableDef).addRecord(rowDict, tableDef)

         if DEBUG >0:
            objMsg.printMsg("Completed saving values to dbl tables...")
         ########################
         return tableDef

      except:
         objMsg.printMsg("Traceback: %s" % str(traceback.format_exc()))
         raise

   def getTableColumns(self,tableCode):
      """
      Function that extracts the table colums from tableheaders and adds the process headers
      """
      tableColumns = tableHeaders[tableCode][self.colOff].split(self.dblDelim)
      for index in xrange(tableColumns.count('')):
         tableColumns.remove('')

      procColHeaders = self.procHeaders['cols']
      #procColHeaders.reverse()

      for item in xrange(len(procColHeaders)):
         tableColumns.insert(self.procTranslation[tableHeaders[tableCode][self.tableTypeOff]], procColHeaders[-1-item])
         if DEBUG > 0:
            objMsg.printMsg("data during procHeader col insert: %s" % (tableColumns,))

      return tableColumns

   def getColTypes(self,tableCode, RowDataLength):
      """
      Function that extracts the column types from the tableheaders and adds the process header types
      """
      colTypes = tableHeaders[tableCode][3].split(self.dblDelim)
      if colTypes == [] or len(colTypes) != RowDataLength:
         colTypes = ['V' for i in xrange(RowDataLength)]

      procTypeHeaders = self.procHeaders['types']
      procTypeHeaders.reverse()

      for item in procTypeHeaders:
         colTypes.insert(self.procTranslation[tableHeaders[tableCode][self.tableTypeOff]], item)

      return colTypes

   def createDbLogDef(self,tableCode,tableColumns,colTypes):
      """
      Function creates a pythonic dblog table definition from the input table descriptors
      """

      tableDef = {
      'type': tableHeaders[tableCode][self.tableTypeOff] ,
      'fieldList': []
                 }

      counter = 0
      for col in tableColumns:
         try:
            #Add definitions per spec DBLogDefs.DbLogColumn('TEST_NAME', 'V', colMask),
            if DEBUG > 1:
               objMsg.printMsg("Adding Column: %s" % str(col))

            temp = DBLogDefs.DbLogColumn(col, colTypes[counter], 0)
            tableDef['fieldList'].append(temp)

            if DEBUG >2:
               objMsg.printMsg("TableDef in line: %s" % str(tableDef['fieldList']))
               objMsg.printMsg("Column instance...%s" % str(temp))
               for subIt in tableDef['fieldList']:
                  objMsg.printMsg(str(subIt))

            del temp
         except IndexError:
            objMsg.printMsg(traceback.format_exc())
            objMsg.printMsg("Error in colType detection: %s: %s" % (str(col),str(counter)))
            objMsg.printMsg("Coltypes: %s" % str(colTypes))
         counter = counter + 1
      return tableDef

   def checkCRCBlock(self,data, sizeIn, crc):
      """
      Function that validates the CRC on a dblog data block
      returns True for valid and False for invalid
      """
      ocrc1 = ord(data[sizeIn+1])
      ocrc2 = ord(data[sizeIn+2])
      ocrc = (ocrc1<<8 | ocrc2)

      #First five bytes (test num) and last two bytes (firmware CRC) are not included in the CRC calculation
      for i in xrange(sizeIn-2):
         c1 = crc & 0x00AA
         c2 = c1 ^ ord(data[i+3])
         crc = (crc + (c2 & 0x00FF)) & 0xFFFF #Protect data overflow.

      if (ocrc == crc):
         return True
      else:
         return False

   def parseHeader(self,data,currentTemp,drive5,drive12,collectParametric):
      """
      Function that parses the incoming data results packet from the drive and handles the resultsKey parsed
      * May add dblog data
      * May write to results file
      * May create debug data
      """
      from FSO import CFSO   
 
      resultsKey = ord(data[0])
      ########################################################################################################
      if 2==resultsKey:  #check for a special signature see if we have to power cycle the drive
         #objMsg.printMsg("ord5=%d, ord6=%d" % (ord(data[5]), ord(data[6])) )
         if 0xBE==ord(data[5]) and 0xBE==ord(data[6]):
            objMsg.printMsg("Update flash completed!!!")

            import base_BaudFunctions
            from Cell import theCell
            from Process import CProcess
            waitTime = 5    #org=30
            objMsg.printMsg("Delay %d sec for flashwrite and reset..." % waitTime)
            time.sleep(waitTime)
            try:
               objMsg.printMsg("Try establising eslip comm without pwrcyc...")
               theCell.enableESlip()
               if testSwitch.FE_SGP_81592_TRIGGER_PWR_CYL_ON_1_RETRY_OF_ESLIP_RECOVERY:
                  base_BaudFunctions.changeBaud_once(PROCESS_HDA_BAUD)
               else:
                  base_BaudFunctions.changeBaud(PROCESS_HDA_BAUD)
                  
               if testSwitch.ADD_SPINUP_AFTER_UPDATING_FLASH:
                  CProcess().St(TP.spinupPrm_1)
            except:
               objMsg.printMsg("Performing pwr cycle to recover from flash corruption...")
               base_BaudFunctions.basicPowerCycle()
               theCell.enableESlip()
               base_BaudFunctions.changeBaud(PROCESS_HDA_BAUD)
               if testSwitch.ADD_SPINUP_AFTER_UPDATING_FLASH:
                  CProcess().St(TP.spinupPrm_1)

         if testSwitch.WA_SAVE_SAP_BY_PCFILE:
             if 0xBD==ord(data[5]) and 0xBD==ord(data[6]):
                objMsg.printMsg("Drive save SAP to PC file. Reload from PC file to drive flash")
    
                import base_BaudFunctions
                from Cell import theCell
                from Process import CProcess
                
                try:
                   objMsg.printMsg("Pwrcyc then retrive the sap from PCfile")
                   base_BaudFunctions.basicPowerCycle()
                   theCell.enableESlip()
                   base_BaudFunctions.changeBaud(PROCESS_HDA_BAUD)
                   if testSwitch.ADD_SPINUP_AFTER_UPDATING_FLASH:
                      CProcess().St(TP.spinupPrm_1)
                   CFSO().recoverSAPfromPCtoFLASH()
                except:
                   objMsg.printMsg("Performing pwr cycle to recover from flash corruption...")
                   base_BaudFunctions.basicPowerCycle()
                   theCell.enableESlip()
                   base_BaudFunctions.changeBaud(PROCESS_HDA_BAUD)
                   if testSwitch.ADD_SPINUP_AFTER_UPDATING_FLASH:
                      CProcess().St(TP.spinupPrm_1)
                   CFSO().recoverSAPfromPCtoFLASH()			
                return # no more action required
				  
				  
      ##########################################################################################################

      if testSwitch.BF_0124988_231166_FIX_SUPPR_CONST_IMPL:
         if (self.dut.objSeq.curRegTest not in testSwitch.disableTestDataOutput) or ((self.dut.objSeq.suppressresults & ST_SUPPRESS__ALL) == ST_SUPPRESS__ALL):
            self.ESGSaveResults(data,currentTemp,drive5,drive12,collectParametric)
      else:
         if (self.dut.objSeq.curRegTest not in testSwitch.disableTestDataOutput) or (self.dut.objSeq.suppressresults):
            self.ESGSaveResults(data,currentTemp,drive5,drive12,collectParametric)

      self.curSize = self.getResultsFileSize()
      length = len(data)                                      # Obtains Length of binary data stream

      if testSwitch.FE_0142099_407749_P_NEW_HEADER_FILE_FORMAT:
         if ord(data[5]) == 1:
            index = 6
            #First five bytes (test num) and last two bytes (firmware CRC) are not included in the CRC calculation
            if (not self.checkCRCBlock(data, length-3 , 0x025C)): #0x025C, It's constant for CRC encoder.
               ScrCmds.raiseException(11044,"Sent back data from drive failed CRC check")
         else:
            index = 25     # Initialize index of binary data stream to 25 jump over the command portion of the results.
            # For all binary results, the first 25 bytes are made up of a single byte block code,
            # Two bytes containing the test number, Two bytes containing the Error code,
            # and Two bytes for each of the Ten Parameters, totaling 25 bytes.
      else:
         index = 25     # Initialize index of binary data stream to 25 jump over the command portion of the results.
         # For all binary results, the first 25 bytes are made up of a single byte block code,
         # Two bytes containing the test number, Two bytes containing the Error code,
         # and Two bytes for each of the Ten Parameters, totaling 25 bytes.

      while index < (length-4):

         format = "HH"
         Block_Size,Block_Value = struct.unpack(format,data[index:index+struct.calcsize(format)])
         if DEBUG > 0:
            objMsg.printMsg("Block_Value: %s" % str(Block_Value))
         if Block_Value not in self.dbLogBlockCodes:
            if Block_Size == 0:
               Block_Size = 1 #Prevent the case of bad block header causing an infinite loop

         else:
            if Block_Value in self.tableInfoBlock['codes'] or Block_Value in self.tableDataRowBlock['codes']:
               if Block_Value in self.tableInfoBlock['codes']:
                  formatA = self.tableInfoBlock['format']               # Establishes the format for the Struct module to unpack the data in.
                  tableCode, = struct.unpack(formatA,data[index+4:index+4+struct.calcsize(formatA)]) # unpaks the revision Type from the data list
                  DriveVars['tableCode'] = tableCode
                  binDataStartLoc = index+struct.calcsize(format)+struct.calcsize(formatA)
               else:
                  tableCode = DriveVars['tableCode']
                  binDataStartLoc = index + struct.calcsize(format)
               binData = data[binDataStartLoc:index+Block_Size]

               if DEBUG >1:
                  objMsg.printMsg("Table Info: tableCode=%s" % str(tableCode), objMsg.CMessLvl.DEBUG)

               try:
                  tableName = tableHeaders[tableCode][self.tableNameOff]
               except KeyError:
                  tableName = ''
                  if self.raiseExceptions == 1:
                     ScrCmds.raiseException(11044,"DBLOG Block code not defined: %s" % str(tableCode))
                  else:
                     objMsg.printMsg("DBLOG Block code %s not defined in tabledictionary.py" % str(tableCode))

               if self.dut.objSeq.tablesToParse and not (tableName == '') and tableName in self.dut.objSeq.tablesToParse:
                  processHeaderData = (self.dut.objSeq.curRegSPCID, self.dut.objSeq.occurrence, self.dut.seqNum, self.dut.objSeq.testSeqEvent)
                  procBinData = self.getRowData(binData, processHeaderData, tableCode)
##                  objMsg.printMsg("TableName= %s, procBinDat is %s" % (tableName,repr(procBinData)))

                  if self.dut.objSeq.SuprsDblObject.has_key(tableName) and type(self.dut.objSeq.SuprsDblObject[tableName]) != types.DictionaryType:
                     del self.dut.objSeq.SuprsDblObject[tableName]

                  if not self.dut.objSeq.SuprsDblObject.has_key(tableName):
                     self.dut.objSeq.SuprsDblObject[tableName]={}
                     self.dut.objSeq.SuprsDblObject[tableName]['tableCols'] = self.getTableColumns(tableCode)
                     self.dut.objSeq.SuprsDblObject[tableName]['tableData'] = []

                  self.dut.objSeq.SuprsDblObject[tableName]['tableData'].append(procBinData)
                  #objMsg.printMsg("TableName[%s]: %s" % (tableName,objMsg.getMemVals())) #MGM DEBUG
               if testSwitch.BF_0124988_231166_FIX_SUPPR_CONST_IMPL:
                  processBlock = (tableName in self.dblTableMaster) and (self.dut.objSeq.curRegTest not in testSwitch.disableTestDataOutput) and (not self.dut.objSeq.suppressresults)
               else:
                  processBlock = (tableName in self.dblTableMaster) and (self.dut.objSeq.curRegTest not in testSwitch.disableTestDataOutput) and (not ((self.dut.objSeq.suppressresults & ST_SUPPRESS__ALL) == ST_SUPPRESS__ALL))
               if processBlock:
                  if DEBUG > 0:
                     objMsg.printMsg("Adding Rec Index for table code %s" % (tableCode))
                  # calc file pointer
                  #  add the current results file size (data already written)
                  #  Subtract the lenght of the full data packet
                  #  Add the offset into the data packet of this binary segment
                  #  Subtract the offset for 0th byte


                  dataLen = len(data)

                  filePtr = self.curSize - dataLen + binDataStartLoc + 1 - 2
                  if DEBUG > 0:
                     objMsg.printMsg("Adding Rec at bin offset = %d" % (filePtr))
                     objMsg.printMsg("-----------------------------")
                     objMsg.printMsg("Results size             = %d" % self.curSize)
                     objMsg.printMsg("binDataStartLoc          = %d" % binDataStartLoc)
                     objMsg.printMsg("len(data)                = %d" % dataLen)
                     objMsg.printMsg("-----------------------------")
                     objMsg.printMsg("Block_Value              = %d" % Block_Value )
                     objMsg.printMsg("formatSize               = %d" % struct.calcsize(format) )
                     if Block_Value in self.tableInfoBlock['codes']:
                        objMsg.printMsg("formatASize              = %d" % struct.calcsize(formatA) )
                  #Now add to dblog table object

                  self.objDbLogIndex.addRecordIndex(tableCode,filePtr,len(binData), self.dut.objSeq.curRegSPCID, self.dut.objSeq.occurrence, self.dut.seqNum, self.dut.objSeq.testSeqEvent)

                  # We must add an entry into the dut.dblData dblog object so the system knows it exists and it can be deleted if necessary
                  self.dut.dblData.Tables(tableName, {})

                  if tableName not in self.dut.stateDBLogInfo[self.dut.currentState]:
                     self.dut.stateDBLogInfo[self.dut.currentState].append(tableName)
               else:
                  if DEBUG > 0:
                     if tableName in self.dblTableMaster:
                        objMsg.printMsg("Test output disabled. No parsing can occur.")
                     else:
                        objMsg.printMsg("Not parsing... %s not in %s" % (tableName, str(self.dblTableMaster)))

         index = index+Block_Size  # Block Size, So index will now reference the start of the next data block.
         #End of While Loop


   def stp5Volt(self,voltage):
      """Returns STP 5 Volt value"""
      return (voltage/1000.0 - 5.0)/0.014668 + 86  # Strange equation pulled from STP report generator file c_rep.cpp

   def stp12Volt(self,voltage):
      """Returns STP 12 Volt value"""
      return (voltage/1000.0 - 12.0)/0.0324774 + 115  # Strange equation pulled from STP report generator file c_rep.cpp

   def ScriptComment(self, comment):
      """ Write chunks of comment until comment is exhausted."""
      scriptTimeFmt = "%b %d %Y-%H:%M:%S"

      header = "\002\xFF\xD4" + 22*" "  # 1 byte block code, 2 bytes test number (-44), 2 bytes fault code, 20 bytes parms
      comment = "\n%s  %s" % (time.strftime(scriptTimeFmt),comment,)

      while comment:
         commentChunk = comment[:512]
         comment = comment[512:]
         self.ESGSaveResults("%s%s" % (header,commentChunk,))

   def ESGSaveResults(self,data,currentTemp=0,drive5=0,drive12=0,collectParametric=0, returnFilePtr = 0):
      """
      Saves results data to binary results file in the STP format.
      * May update the debug data file
      """
      size = len(data) + 10
      currentTime = int(time.time())
      v5 = self.stp5Volt(drive5)
      v12 = self.stp12Volt(drive12)

      if v5 < 0:
         v5   = 0  # rpt gen does not handle negative values here
      if v12 < 0:
         v12 = 0  # rpt gen does not handle negative values here

      from Rim import objRimType, theRim
      if objRimType.IsPSTRRiser():
          currentTemp = 0
      rptTemp = currentTemp/10 # convert decivolts to volts; Centigrade

      # WRITE THESE VALUES INTO A BINARY STRING
      str1 = struct.pack('<HLbbbb',size,currentTime,v5,v12,collectParametric,rptTemp)

      # SET HI BIT IN TEST NUMBER IF THIS IS PARTIAL RESULTS
      block_code = data[0]
      char_1 = ord(data[1])
      if '\003'==block_code:
         char_1 = char_1 | 0x80

      # WE DON'T SAVE THE FIRST BYTE OF DATA
      data = chr(char_1) + data[2:]
      # CREATE AN ARRAY OF BYTES SO WE CAN WRITE IT TO THE FILE
      str2 = data
      str3 = "\000"  # ALIGNMENT BYTE

      if returnFilePtr:
         #Get the last position of the results file
         lastPosition = self.getResultsFileSize()

      if self.dut.objSeq.suppressresults & ST_SUPPRESS_RECOVER_LOG_ON_FAILURE:
         self.dut.supprResultsFile.writeDebugData(str1+str2+str3)
      elif self.dut.objSeq.suppressresults == 0:
         WriteToResultsFile(str1+str2+str3)

      if returnFilePtr:
         # Return the offset into the file where the actual data starts for this data block
         return len(str1) + lastPosition
      else:
         return 0

   def getResultsFileSize(self):
      """
      Returns the current binary results file size
      """
      try:
         size = ResultsFile.size()
      except AttributeError:
         size = os.stat(ResultsFilePath)[stat.ST_SIZE]
      return size

class DbLogIndexFile:
   """
   Implements teh DblogIndex File used to keep pointers to data in the binary results file as well as process header data
   """
   RECORD_SZ_FMT       = "H"
   TABLE_CODE_FMT      = "H"
   FILE_PSN_FMT        = "L"
   SPC_ID_FMT          = 'l'
   OCCURRENCE_FMT      = 'H'
   SEQ_FMT             = 'H'
   TEST_SEQ_EVENT_FMT  = 'H'
   PROC_HDR            = SPC_ID_FMT + OCCURRENCE_FMT + SEQ_FMT + TEST_SEQ_EVENT_FMT
   INDEX_FMT = TABLE_CODE_FMT + FILE_PSN_FMT + RECORD_SZ_FMT + PROC_HDR

   def __init__(self, loadPrevRecords = True):
      self.indexFileName = "dblogIndex.bin"
      self.indexFile = GenericResultsFile(self.indexFileName)
      self.initIndex()

      # Establish power loss/restart status
      try:
         if loadPrevRecords:
            self.reloadIndexFile()
         else:
            self.indexFile.open('wb')
            self.indexFile.write('')
            self.indexFile.close()

      except:
         objMsg.printMsg("No previous dblog index data found.",  objMsg.CMessLvl.VERBOSEDEBUG)


   def initIndex(self):
      """
      Initializes the dblog indicies
      """
      self.indicies = {}
      self.indexSync = {}

   def addRecordIndex(self, tableCode, filePosition, dataLength, spc_id, occurrence, seq, test_seq_event):
      """
      Adds a record index to the index location in python memory as well as the disc copy
      """
      if not self.indicies.has_key(tableCode):
         self.indicies[tableCode]  = []
         self.indexSync[tableCode] = 0

      if spc_id == None:
         spc_id = -1
      try:
         spc_id = int(spc_id)
      except:
         objMsg.printMsg("WARNING!!: spc_id input was NAN (%s) converting to -1" % (spc_id,), objMsg.CMessLvl.CRITICAL)
         spc_id = -1

      self.indicies[tableCode].append([filePosition, dataLength, spc_id, occurrence, seq, test_seq_event])

   def getResultsFileSize(self):
      """
      Returns the current binary file size of the dblog index file
      """
      try:
         sz = self.indexFile.size()
      except AttributeError:
         sz = os.stat(os.path.join(ScrCmds.getSystemResultsPath(),ScrCmds.getFofFileName(1),self.indexFileName))[stat.ST_SIZE]
      return sz

   def reloadIndexFile(self):
      """
      Reloads the index file and updates the python index data in memory
      """
      fsize = self.getResultsFileSize()
      if fsize == 0:
         raise Exception, "Dblog index file empty"

      self.initIndex()
      self.indexFile.open('rb')
      try:
         while self.indexFile.tell() < fsize:
            tableCode, filePosition, dataLength, spc_id, occurrence, seq, test_seq_event = self.getDiscRecord()

            if tableCode or filePosition or dataLength:
               self.addRecordIndex(tableCode, filePosition, dataLength, spc_id, occurrence, seq, test_seq_event)
      except:
         objMsg.printMsg("Error in reloading Index file: %s" % traceback.format_exc())

   def streamIndexFile(self):
      """
      Flushes (stream) the index memory information to the HD on the CM for power loss recovery
      """
      self.indexFile.open('wb')
      if DEBUG > 0:
         objMsg.printMsg("indicies %s " % str(self.indicies))
      try:
         for key in self.indicies:
            for recTuple in self.indicies[key]:
               if key or recTuple[0] or recTuple[1]:
                  recTuple = list(recTuple)
                  recTuple.insert(0,key)
                  self.writeRecordToDisc(recTuple)
      finally:
         self.indexFile.close()

   def writeRecordToDisc(self,args):
      """
      Writes a single dblog index record to the dblog index file
      """
      self.indexFile.seek(0,2) #Seek to end of file
      #Write data to file
      if DEBUG > 0:
         objMsg.printMsg("FMT:  %s" % self.INDEX_FMT)
         objMsg.printMsg("args: %s" % args)
         objMsg.printBin(struct.pack(self.INDEX_FMT, *args))
      try:
         self.indexFile.write(struct.pack(self.INDEX_FMT, *args))
      except:
         objMsg.printMsg("Unable to write index data!! Power Loss recovery compromised! Fsize = %d\n%s" % (self.indexFile.tell() , traceback.format_exc()), objMsg.CMessLvl.IMPORTANT )
         raise

   def getDiscRecord(self):
      """
      Reads a single dblog index record from the dblog index file
      """
      #Read in the data from the file
      record = self.indexFile.read(struct.calcsize(self.INDEX_FMT))
      #Unpack the data structure
      if DEBUG > 0:
         objMsg.printBin(record)
      return struct.unpack(self.INDEX_FMT,record)

   def __del__(self):
      self.indexFile.close()
