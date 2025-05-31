#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Class to store column definition including name and type
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/ParamDbLogXmlOptimizer.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/ParamDbLogXmlOptimizer.py#1 $
# Level:4
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
import types, ScrCmds
import MessageHandler as objMsg
from StringIO import StringIO
from Drive import objDut

DEBUG = 0

class cmStringIO(StringIO):
   """
   GenericResultsFile *like* wrapper for the StringIO class interface
   """
   def __init__(self,fName):
      self.fName = fName
      StringIO.__init__(self,'')

   def open(self,mode):
      if mode.find('a') > -1:
         self.seek(0,2)
      else:
         self.seek(0)
      return not self.closed

   def close(self,forceClose = False):
      if forceClose:
         StringIO.close(self)

   def delete(self):
      self.close(True)

   def __del__(self):
      self.delete()

   def size(self):
      return self.len


class fileGenerator:
   """
   Object/Class that returns a generator object that will step through a file with
      <parametric_dblog> data in it and return the tableName and byte offset into the file
      that the table starts at. This method is created to it uses a low memory overhead.
      Yes a full read and split would be faster but it is more RAM.
   """
   tableHeader = "TABLE="
   typeHeader = "TYPE="
   headerLength = len(tableHeader)

   def __init__(self,fileObj):
      self.fileObj = fileObj
      self.fileObj.seek(0,2)
      self.fsize = self.fileObj.tell()
      self.fileObj.seek(0)

   def parseTableName(self,inBuff):
      return inBuff[inBuff.find(self.tableHeader) + self.headerLength:inBuff.find(self.typeHeader)].strip()

   def __iter__(self):
      #Initilize the read-ahead size... if this spans 2 tableHeaders the algorithm breaks
      # 10 is a tested number that doesn't break and shows low exec times
      readSize = 10

      #Initialize the string buffer
      tbuff = ''

      #Initialize counters
      tableName = False
      startIndex = False
      byteCounter = 0

      #Iterate while we have bytes left to accumulate
      while byteCounter <= self.fsize:
         #Fill the read buffer
         tbuff += self.fileObj.read(readSize)
         #Increment the file counter.. f.tell() should work as well but only if the object passed in
         # is opened in binary mode.
         byteCounter +=readSize

         if tbuff.find(self.tableHeader) > -1:
            #set the startIndex to the last read position in the file - the header we just parsed
            startIndex = byteCounter - len(tbuff) + tbuff.find(self.tableHeader)#self.headerLength

         if tbuff.find(self.typeHeader) > -1:
            #extract the tableName
            tableName = self.parseTableName(tbuff)
            #Clear the buffer to reduce overhead and begin iteration for next table start
            tbuff = ''
            #return the iterator result
            yield [tableName, startIndex]


def accumulateDbLogIndicies(filePath):
   """
   Iterates through the input path to accumulate the table start and end bytes for the
      parametric tables in the file.
   @return: Dictionary of tableName: List([startByte,endByte],[startByte,endByte],...)
   """
   #Open the file object for reading
   if type(filePath) == types.StringType:
      mfile = open(filePath,'rb')
   else:
      mfile = filePath
      mfile.open('rb')

   try:
      #Get the fileGenerator for this file object
      mgen = fileGenerator(mfile)

      #Initialize variables
      tableDict = {}
      lastTable = None
      mList = []
      #Accumulate start-end and add to master list
      for mList in mgen:
         #If we didn't get a null return... happened in regression on EOF
         if mList:
            if lastTable:
               #If we are on the 2nd+ table then we can begin adding endByte values
               #lastTable[2] = mList[1] # We don't need this explicitly but good for ref
               tableDict.setdefault(lastTable[0],[]).append((lastTable[1], mList[1]))
            #Append the table,
            lastTable = [mList[0], mList[1], 0]

      #Since we're delayed 1 update... update the last item in the list
      #lastTable[2] = mList[1] # We don't need this explicitly but good for ref
      if lastTable: #Make sure we found some data
         tableDict.setdefault(lastTable[0],[]).append((lastTable[1], mList[1]))
         if tableDict[lastTable[0]][-1][0] == tableDict[lastTable[0]][-1][1]:
            #last table is null- extend to start of end tag
            ntuple = list(tableDict[lastTable[0]][-1])
            mfile.seek(ntuple[0])
            data = mfile.read()
            end = data.find('</parametric_dblog>')

            ntuple[1] = ntuple[0] + end
            tableDict[lastTable[0]][-1] = tuple(ntuple)

   finally:
      mfile.close()

   return tableDict


def getTable(fileObj, startIndex, endIndex):
   """
   Function to extract the table rows from a binary slice of a file
   @return: sequence of [Header,data]
   """
   fileObj.seek(startIndex)
   data = fileObj.read(endIndex-startIndex)
   if DEBUG > 1:
      objMsg.printMsg("TableDump in getTable:\n%s" % data)
   data = data.splitlines()
   if DEBUG > 1:
      objMsg.printMsg("LinedTableDump in getTable:\n%s" % data)
   return '\n'.join(data[0:3]).replace('\n',DBLOG_EOL_CHAR), '\n'.join(data[3:]).replace('\n',DBLOG_EOL_CHAR)


def getOutputFile(fname, mode, forceMemFile = False):
   """
   Open file wrapper to create a cm like StringIO file instead of GenericResultsFile
      If create of a GenericResultsFile fails
   """
   try:
      if not forceMemFile:
         if type(fname) == types.StringType:
            oFile = GenericResultsFile(fname)
         else:
            oFile = fname

         oFile.open(mode)
   except:
      forceMemFile = True
      import traceback
      objMsg.printMsg("File creation failed... using stringIO.\n%s" % traceback.format_exc())

   if forceMemFile:
      oFile = cmStringIO(fname)

   return oFile


class dexOpti:
   def __init__(self, processTables, sf3Tables, resFile):
      self.dut = objDut

      self.procTblNames = processTables
      # SF3 tables input here are names and indices, we want to keep both
      self.sf3Tables = sf3Tables
      self.stTblNames = sf3Tables.keys()  # Extract names from sf3Tables
      self.resFile = resFile

      if self.dut.productionFileLimits == None:
         self.dut.productionFileLimits = ScrCmds.getSystemMaximumFileSizes()
      self.maxResultsFileSize, self.DefaultMaxEventSize, self.parametricFileMargin = self.dut.productionFileLimits

      self.skippedTables = []

   def prioritizeTables(self):
      '''
      Create the list of dbLog tables to be sent to FIS.
      If the PRODUCTION_MODE ConfigVar is set and USE_LOAD_ONLY_IN_PRODUCTION is set, the list will just be the productionLoadOnly list.
      Otherwise, the list is created in the following order:
         1) Tables in the priority_parametric_load_list, in order
         2) All tables not in parametric_no_load or priority_parametric_load_list, in random order
         3) Tables in priority_parametric_reload_list in the order listed
         4) parametric_no_load tables in random order
      '''
      from random import shuffle

      # Put together a list of all table names, process and SF3
      allTables = self.procTblNames + self.stTblNames

      # Remove duplicate tables
      allTables = list(set(allTables))

      # Randomize the tables
      shuffle(allTables)

      # Get the load lists
      priority_parametric_load_list = getattr(TP,'priority_parametric_load_list',[])
      priority_parametric_reload_list = getattr(TP,'priority_parametric_reload_list',[])
      productionLoadOnly = getattr(TP,'productionLoadOnly',[])
      parametric_no_load = getattr(TP,'parametric_no_load',[])
      parametric_no_load = [entry[0]for entry in parametric_no_load] # Table names only

      if ConfigVars[CN].get('PRODUCTION_MODE',0) and testSwitch.USE_LOAD_ONLY_IN_PRODUCTION:
         loadList = [tbl for tbl in productionLoadOnly if tbl in allTables]

      else:
         # If a table is in the priority load list, make sure it is not in the no load or reload lists
         for tbl in priority_parametric_load_list:
            if tbl in parametric_no_load:
               parametric_no_load.remove(tbl)
            if tbl in priority_parametric_reload_list:
               priority_parametric_reload_list.remove(tbl)

         # Move the priority_parametric_load_list tables (in order) to the front of the line
         loadList = [tbl for tbl in priority_parametric_load_list if tbl in allTables] +\
            [tbl for tbl in allTables if tbl not in priority_parametric_load_list]

         # If tables in priority_parametric_reload_list are also in parametric_no_load,
         #  remove the duplicates from the no_load list.  In this manner the reload tables will be
         #  placed in line before the no load tables
         for tbl in priority_parametric_reload_list:
            if tbl in parametric_no_load:
               parametric_no_load.remove(tbl)

         # Go through the list and delete all items in the reload and no load lists.  Items in the no load list will be added to a tempList.
         loadList = [tbl for tbl in loadList if tbl not in priority_parametric_reload_list]
         noLoadTables = []
         for tbl in list(loadList):
            if tbl in parametric_no_load:
               loadList.remove(tbl)
               noLoadTables.append(tbl)
         if testSwitch.ADD_PARAMETRICS_TO_LIMITS:
            loadList += [tbl for tbl in priority_parametric_reload_list if tbl in allTables] + noLoadTables

      self.priorityLoadList = loadList
      self.removeEmptyTables()
      if DEBUG:
         objMsg.printMsg("Prioritized load list:\n%s" % self.priorityLoadList)

   def removeEmptyTables(self):
      """Remove the empty PF3 tables from self.priorityLoadList"""

      for table in self.priorityLoadList[:]:
         if table in self.procTblNames:
            if len(self.dut.dblData.Tables(table)) == 0:
               self.priorityLoadList.remove(table)
               if DEBUG:
                  objMsg.printMsg("Removing empty table %s from load list." % table)

   def writeFinalDblogFile(self, outputFile, replaceExistingFile = True):
      """
      Write the final optimized dbLog file to be sent to FIS

      inputFile: the input results file
      """
      extraPad = 10000 # Extra file size limit padding.  Used to ensure we don't loop through all tables trying to write them when we are too close to the limit

      #If input file size is > 2mb there is a chance we can't fit it under 2mb so start with string file
      resFileSize = ScrCmds.getFileSize(self.resFile)

      if resFileSize > self.maxResultsFileSize:
         forceMemFile = True
      else:
         forceMemFile = False

      #Reading files is always allowed- no need to wrapper
      try:
         rFile = open(self.resFile,'rb')
      except:
         rFile = open(self.resFile.name,'rb')

      # -----Prep the output file-----
      # Get a handle for a GenericResultsFile object that has stringIO overload capabilties
      self.oFile = getOutputFile(outputFile,'wb', forceMemFile)

      # Write the xmlResultsFile start tag
      self.oFile.write('<parametric_dblog>')
      self.oFile.close()

      # Append to the file- shown to be faster on windows
      self.oFile.open('ab')

      # Loop through and write the tables we need
      try:
         for table in self.priorityLoadList:
            # Stop writing tables if we are near enough to the limit
            self.currOutFileSize = ScrCmds.getFileSize(self.oFile)
            if (self.currOutFileSize + self.parametricFileMargin + extraPad) > self.DefaultMaxEventSize:
               self.skippedTables += self.priorityLoadList[self.priorityLoadList.index(table):]
               break
            else:
               self.writeTable(rFile, table)
         if len(self.skippedTables) >  0:
            objMsg.printMsg("Aborting parametric data addition in order to keep from exceeding the max event size.")
            objMsg.printMsg("Tables not uploaded to oracle: %s" % (','.join(self.skippedTables)))
      finally:
         # Write closing XML tag
         self.oFile.write('</parametric_dblog>')
         # Close files
         rFile.close()
         self.oFile.close()
         self.currOutFileSize = ScrCmds.getFileSize(self.oFile)
         objMsg.printMsg("Final dbLog file size: %s" % self.currOutFileSize)

      # Set oracle mode to 0
      self.dut.dblData.setOracleMode(oracleOnly = 0)

      if replaceExistingFile:
         #Will overwrite the input file with our optimized file.
         rFile = getOutputFile(self.resFile,'wb')
         try: # Clear the original file
            rFile.write('')
         finally:
            rFile.close()
         rFile = getOutputFile(self.resFile,'ab')
         self.oFile.open('rb')
         try:
            rFile.write(self.oFile.read())
         finally:
            rFile.close()

   def writeTable(self, rFile, table):
      """
      Write the specified table to the xml output file
      """
      # Determine if a table is process or non-process table
      if table in self.procTblNames:
         tableType = 'PF3'
      elif table in self.stTblNames:
         tableType = 'SF3'
      else:
         ScrCmds.raiseException(11044, "Trying to write an unlisted dbLog table.  How did you get here?")

      # Get the table size, if a non-process table, it will gather and prep the temp data to be written
      if tableType == 'PF3':
         pf3TableData = str(self.dut.dblData.Tables(table))
         tableSize = len(pf3TableData)
      elif tableType == 'SF3':
         start = True
         # Build up the SF3 table in a temp file
         tempDblTbl = cmStringIO('tempDblTbl.bin')
         tempDblTbl.open('wb')
         for sIndex,eIndex in self.sf3Tables.get(table,[]):
            #Get the table data out of the file segment
            segData = getTable(rFile, sIndex, eIndex)

            #Null rows in the xmlresults file can create null rows... skip the record
            if '' in segData: continue

            # only write 1 header per table
            if start:
               tempDblTbl.write(segData[0])
               if DEBUG:
                  objMsg.printMsg("Writing SF3 table header: %s" % segData[0])

            tempDblTbl.write(DBLOG_EOL_CHAR)
            tempDblTbl.write(segData[1])
            if DEBUG > 0:
               objMsg.printMsg("Writing SF3 table data: %s" % segData[1])
            #turn off header writing
            start = False
         tempDblTbl.write(DBLOG_EOL_CHAR)
         tableSize = ScrCmds.getFileSize(tempDblTbl)

      if self.currOutFileSize + self.parametricFileMargin + tableSize > self.DefaultMaxEventSize:
         self.skippedTables.append(table)  # Skip the table, as it won't fit
      else:
         if tableType == 'PF3':
            self.dut.dblData.setOracleMode(oracleOnly = 1)  # Oracle mode on for process tables
            self.oFile.write(pf3TableData)
            if DEBUG:
               objMsg.printMsg("Writing PF3 table: %s" % str(self.dut.dblData.Tables(table)))
         elif tableType == 'SF3':
            self.dut.dblData.setOracleMode(oracleOnly = 0)  # Oracle mode off for SF3 tables
            self.oFile.write(tempDblTbl.getvalue())
            tempDblTbl.close()
