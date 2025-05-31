#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Class that stores values for one row of data
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/DbLog.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/DbLog.py#1 $
# Level:3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
import string, traceback, types, struct, math
import DBLogDefs
import ScrCmds, Utility
import MessageHandler as objMsg
from tabledictionary import tableHeaders
from Exceptions import CDblogDataMissing

from dbLogUtilities import chopDbLog, chopDbLogLoop, diffDbLog, has_alias_key

from DbLogAlias import reverseTableHeaders, dbLogTableAliases, processTableOverrides, dbLogColAliases, OracleTableOverrides

import cPickle as pickle

oUtil = Utility.CUtility()

dbLogColAliasesReverse = {}
for k, v in dbLogColAliases.items():
   dbLogColAliasesReverse[v] = k

class DbLogTable:

   """
   Represents one table in Oracle.  Used as a collection of DbLogRecord objects that can later be sent as
   parametrics to Oracle.
   """
   maxFsize = 1999488 # 2000000 minus the maximum size of 1 packet
   EOF = 2
   SOF = 0

   def __init__(self, tableName, tableDef = {}, dut = None, markForDeleteCallback = None):
      self.tableName = tableName
      self.tableType = tableDef.get('type','S')
      self.dut = dut
      self.tableDef = tableDef
      self.tableCode = None

      self.__columnNameList = []
      self.__columnTypeList = []
      self.__dbUploadList = []

      if not self.tableDef == {}:
         self.createTableDef(tableDef)

      self.__recordList = []
      self.__oracleTablesOnly = 0
      self.markForDeleteCallback = markForDeleteCallback

      if testSwitch.CACHE_TABLEDATA_OBJ:
         self.__tableDataObj = None

   def clearCachedData(self):
      if testSwitch.CACHE_TABLEDATA_OBJ:
         self.__tableDataObj = None

   def raiseNoValidData(self):
      if not self.markForDeleteCallback == None:
         self.markForDeleteCallback(self.tableName)
         raise CDblogDataMissing, self.tableName

   def setOracleMode(self, oracleOnly = 0):
      self.__oracleTablesOnly = oracleOnly

   def createTableDef(self,tableDef):
      # Save the column name and type lists for later
      if DEBUG > 0:
         objMsg.printMsg("Creating new table definition using %s" % str(tableDef))
      try:
         self.tableType = tableDef['type']
      except KeyError:
         self.raiseNoValidData()

      for columnObj in tableDef['fieldList']:
         self.__columnNameList.append(columnObj.getName())
         self.__columnTypeList.append(columnObj.getType())
         self.__dbUploadList.append(columnObj.getDbUpload())
      self.tableDef = tableDef

   def __str__(self):
      """
      Outputs this table including header and data in the DbLog format.  Note that this output routine
      conforms to the FIS Specification here:
         http://www.netsys.stsv.seagate.com/DBLog/LogDataFormatParametricParserRequirements.doc
      """


      tempColNames = list(self.__columnNameList)
      tempColTypes = list(self.__columnTypeList)

      if self.__oracleTablesOnly == 0:
         #Non oracle data
         tempRecList = list(self.Records())

      else:
         #Oracle data so disable if spc_id == None or < 0
         try:
            #Most tables have spc_id so lets not take the if cost
            SPC_ID_IDX = tempColNames.index('SPC_ID')
         except:
            tempRecList = list(self.Records())
         else:
            tempRecList = []
            for rec in self.Records():
               # AND conditions are checked left to right so while int(None) is an exception
               #     it isn't checked since the 1st conditional is FALSE
               if not rec[SPC_ID_IDX] == None and not int(rec[SPC_ID_IDX]) < 0:
                  tempRecList.append(rec)

      #Make a copy to dis-associate the refs
      tempRecList = list(tempRecList)

      if len(tempRecList) > 0 and len(tempColTypes) > 0:
         # Output the table header
         dbLogStr = "TABLE=%s TYPE=%s%s" % (self.tableName, self.tableType, DBLOG_EOL_CHAR)

         # Now the column name and type lists
         dbLogStr += string.join(tempColNames, ',') + DBLOG_EOL_CHAR
         dbLogStr += string.join(tempColTypes, ',') + DBLOG_EOL_CHAR

         # Now the data itself.  First get the string representations of the records, and then join them with DBLOG_EOL_CHAR's
         recordListAsStrings = map(self.typeData,tempRecList)
         dbLogStr += string.join(recordListAsStrings, DBLOG_EOL_CHAR) + DBLOG_EOL_CHAR
      else:
         dbLogStr = ''
      return dbLogStr

   def typeData(self, data):
      #Create a copy of the input data row so we don't mutate the callable
      data = list(data)

      for item in xrange(len(data)):
         #Remove non printable chars from items
         data[item] = objMsg.cleanASCII(str(data[item]))
         try:
            if self.__columnTypeList[item] == "N":
               #remove ' from numerics but don't type them because they end up as to much precision
               data[item] = str(data[item]).replace("'","").replace('"',"").strip()
            elif self.__columnTypeList[item] == "V":
               if data[item].find(' ') > -1:
                  data[item] = '"%s"' % str(data[item]).replace("'","").replace('"',"").strip()
               else:
                  data[item] = str(data[item]).replace("'","").replace('"',"").strip()
            elif self.__columnTypeList[item]  == "D":
               data[item] = '"%s"' % str(data[item]).replace("'","").replace('"',"").strip()

         except ValueError:
            pass
         except IndexError:
            objMsg.printMsg("Debug info:\ndata: %s\ncolTypes: %s" % (data,self.__columnTypeList))
            ScrCmds.raiseException(11044,"Type list for %s not found" % item)
         if data[item] == " " or data[item] == '""':
            data[item] = ""
      return ','.join(data)

   def __add__(self, other):
      """
      Adds two DbLogTable objects together.  Iterates over each record in the right operand, adding it to the
      left operand.  Returns the DbLogTable object containing the result.
      """

      if (type(self) == type(other)):
         for record in other.Records(references = 1):
            self.__recordList.append(record)

         if testSwitch.CACHE_TABLEDATA_OBJ:
            self.__tableDataObj = None

      return self

   def addRecord(self, recordDataDict, tableDef = {}):
      """
      Instantiate a new record object and add it to this table.
      """

      self.__orderedDataList = []

      if self.tableDef == {}:
         if tableDef == {}:
            # Use-Case: Process wants to add data to an unsync'd SF3 defined table
            # This should fill the self.tableDef if there is data in binary results file available
            if testSwitch.BF_0178970_007955_HANDLE_SF3_TABLES_WRITTEN_TO_MEMORY_VIA_PF3:
               try:
                  self.tableCode = self.preRecordFetch()
               except CDblogDataMissing:
                  self.tableCode = self.getReverseTableHeader()
                  tableColumns = self.dut.dblParser.getTableColumns(self.tableCode)
                  colTypes = self.dut.dblParser.getColTypes(self.tableCode,len(tableColumns))
                  tableDef = self.dut.dblParser.createDbLogDef(self.tableCode,tableColumns,colTypes)
                  self.createTableDef(tableDef)
            else:
               self.preRecordFetch()
         else:
            self.createTableDef(tableDef)

      if not(self.tableName in self.dut.stateDBLogInfo[self.dut.currentState]):
         self.dut.stateDBLogInfo[self.dut.currentState].append(self.tableName)
         if DEBUG > 0:
            objMsg.printMsg("GOTF added table %s to %s" % (str(self.tableName), str(self.dut.stateDBLogInfo[self.dut.currentState])))

      for columnName in self.__columnNameList:
         try:
            self.__orderedDataList.append(recordDataDict[columnName])

         except:
            self.__orderedDataList.append('')

      self.__recordList.append(self.__orderedDataList)

      if testSwitch.BF_0144790_231166_P_FIX_GOTF_DBL_REGRADE_DUP_ROWS:
         #remove table from delete list since we added new rows
         self.markForDeleteCallback(self.tableName, True)
      if DEBUG > 0:
         objMsg.printMsg("Adding Record     %s" % str(self.__orderedDataList))
         objMsg.printMsg("Cur.   Recordlist %s" % str(self.__recordList))

      if testSwitch.CACHE_TABLEDATA_OBJ:
         self.__tableDataObj = None

   def deleteRecord(self):
      del self.__recordList[:]

   def preRecordFetch(self):
      self.tableCode = self.getReverseTableHeader()
      # tableCode is false if this isn't a tabledictionary table
      if self.tableCode:
         if not self.syncTable(self.tableCode):
            if testSwitch.BF_0178970_007955_HANDLE_SF3_TABLES_WRITTEN_TO_MEMORY_VIA_PF3:
               if len(self.__recordList) == 0:
                  if not self.tableName in processTableOverrides:
                     self.raiseNoValidData()
            else:
               if not self.tableName in processTableOverrides:
                  self.raiseNoValidData()


      return self.tableCode

   def Records(self):
      """
      Return all the records that have been added to this instance
      """
      #Syncronize the object data for the requested table
      try:
         self.preRecordFetch()
      except CDblogDataMissing:
         #There might be some process added data
         if testSwitch.FE_0000131_231166_GOTF_REGRADE_SUPPORT:
            if len(self.__recordList) == 0:
               raise
         else:
            raise

      #Yield the rows 1 at a time so we don't have 2 concurrent lists.
      for rec in self.__recordList:
         yield rec

   def rowListIter(self, filter = {}, index = 0):
      """
      Return an iterator of the records with specified filter and from specified index (including) onwards
      Filter format: {columnIndex : matchValue}
      """
      if DEBUG > 0:
         if filter:
            objMsg.printMsg('rowListIter filter: %s' % str(filter))
         if index:
            objMsg.printMsg('rowListIter index: %d' % index)
      idx = 0
      try:
         for rec in self.Records():
            if not rec:
               continue
            if filter:
               hit = True
               for k, v in filter.items():
                  if (rec[k] == v):
                     continue
                  else:
                     hit = False
                     break
               if not hit: 
                  continue
            if idx < index:
               idx += 1
               continue
            yield rec
      except IndexError:
         ScrCmds.raiseException(11044, "Invalid column name index %d" % (k,))
      except:
         ScrCmds.raiseException(11044, "Invalid filter %s or index %s" % (str(filter), str(index)))
      
   def columnNameDict(self):
      """
      Return column name dict
      """
      #Syncronize the object data for the requested table
      try:
         self.preRecordFetch()
      except CDblogDataMissing:
         #There might be some process added data
         if testSwitch.FE_0000131_231166_GOTF_REGRADE_SUPPORT:
            if len(self.__recordList) == 0:
               raise
         else:
            raise
      outDict = {}
      for idx, key in enumerate(self.__columnNameList):
         outDict[key] = idx
         alias = dbLogColAliasesReverse.get(key)
         if alias:
            outDict[alias] = idx
      return outDict

   def getReverseTableHeader(self):
      if DEBUG > 0:
         objMsg.printMsg("Syncronizing %s" % self.tableName)

      tableCode = False

      try:
         tableCode = reverseTableHeaders[self.tableName]
      except KeyError:
         try:
            for key in dbLogTableAliases.get(self.tableName,[]):
               try:
                  if DEBUG > 0:
                     objMsg.printMsg("Looking for %s" % key)
                  tableCode = reverseTableHeaders[key]
                  break
               except KeyError:
                  pass
         except:
            objMsg.printMsg(traceback.format_exc())
            objMsg.printMsg("WARNING: %s not found in tabledictionary.py" % self.tableName)
            return False

      return tableCode

   def __len__(self):
      self.preRecordFetch()
      return len(self.__recordList)

   def __del__(self):
      """
      Cleans up after class instance.
      - Resets the table sync pointer to 0
      """

      if not self.dut == None:
         tableCode = self.getReverseTableHeader()
         self.dut.dblParser.objDbLogIndex.indexSync[tableCode] = 0

   def syncTable(self, tableCode):
      tableDef = self.tableDef
      dataExtracted = True

      newData = False

      if not testSwitch.virtualRun or testSwitch.unitTest:
         ResultsFile.open('rb')
         try:
            if DEBUG > 0:
               objMsg.printMsg("startIndex: %s;Finish Index: %s" % (self.dut.dblParser.objDbLogIndex.indexSync[tableCode], len(self.dut.dblParser.objDbLogIndex.indicies[tableCode])))
            #Read from where we left off to the end... this xrange can be 0 length which means we're already synched
            if testSwitch.FE_0237612_336764_P_ADD_RESULT_FILE_READ_BUFFER_FOR_LA_CM_REDUCTION:
               data_start_index = data_start = self.dut.dblParser.objDbLogIndex.indexSync[tableCode]
               data_end_index   = data_end = len(self.dut.dblParser.objDbLogIndex.indicies[tableCode])
               first_ptr_ref = 0
               first_ptr = 0
               second_ptr = 0
               end_ptr = 0
               read_element_count = 0
   
               for recordIndex in xrange(data_start,data_end):
                  if read_element_count == 0: 
                     for prepare_index in xrange(data_start_index,data_end_index):
                        if first_ptr == 0 :
                           first_ptr_ref = first_ptr = self.dut.dblParser.objDbLogIndex.indicies[tableCode][prepare_index][0]
                        read_element_count += 1   
                        if (data_end_index-1) > prepare_index :
                           second_ptr = self.dut.dblParser.objDbLogIndex.indicies[tableCode][prepare_index+1][0]
                           if second_ptr - first_ptr < 61440 :
                              end_ptr = second_ptr +  self.dut.dblParser.objDbLogIndex.indicies[tableCode][prepare_index+1][1]
                           else :
                              break
                        else :
                           if read_element_count == 0:
                              end_ptr = first_ptr_ref + self.dut.dblParser.objDbLogIndex.indicies[tableCode][prepare_index][1]
                           break
                     
                  if first_ptr != 0 :
                     ResultsFile.seek(first_ptr)
                     data_65K = ResultsFile.read(end_ptr - first_ptr)
                     first_ptr = 0
                  read_element_count -= 1
                  data_start_index = recordIndex+1
                  data_s1 = self.dut.dblParser.objDbLogIndex.indicies[tableCode][recordIndex][0] - first_ptr_ref
                  data_s2 = data_s1+self.dut.dblParser.objDbLogIndex.indicies[tableCode][recordIndex][1]
                  data = data_65K[data_s1:data_s2]
                  tableDef = self.dut.dblParser.addDbLogRow(data,tableCode,tableDef, self.dut.dblParser.objDbLogIndex.indicies[tableCode][recordIndex][2:])
                  self.dut.dblParser.objDbLogIndex.indexSync[tableCode] = recordIndex+1
                  newData = True   
            else:      
               for recordIndex in xrange(self.dut.dblParser.objDbLogIndex.indexSync[tableCode], len(self.dut.dblParser.objDbLogIndex.indicies[tableCode])):
                  ResultsFile.seek(self.dut.dblParser.objDbLogIndex.indicies[tableCode][recordIndex][0])
                  data = ResultsFile.read(self.dut.dblParser.objDbLogIndex.indicies[tableCode][recordIndex][1])
                  tableDef = self.dut.dblParser.addDbLogRow(data,tableCode,tableDef, self.dut.dblParser.objDbLogIndex.indicies[tableCode][recordIndex][2:])
                  self.dut.dblParser.objDbLogIndex.indexSync[tableCode] = recordIndex+1
                  newData = True
         except KeyError:
            dataExtracted = False
         ResultsFile.close()
         if self.tableDef == {}:
            self.createTableDef(tableDef)

      if testSwitch.CACHE_TABLEDATA_OBJ:
         if newData:
            self.__tableDataObj = None

      return dataExtracted

   def deleteIndexRecords(self,confirmDelete = 0):
      """
      Remove all index information about this table from the memory/disc structure.
      Should only be used when you never want to retreive this info again.
      """
      if confirmDelete:
         if not self.tableCode:
            self.tableCode = self.getReverseTableHeader()
         try:
            self.dut.dblParser.objDbLogIndex.indexSync[self.tableCode] = 0
            self.dut.dblParser.objDbLogIndex.indicies[self.tableCode] = []
            try:
               del self.dut.stateDBLogInfo[self.dut.currentState][self.dut.stateDBLogInfo[self.dut.currentState].index(self.tableName)]
            except ValueError:
               pass #Ignore as we probably already removed it in delTable
         except KeyError:
            objMsg.printMsg("Error deleting index records for %s" % self.tableName)

         if testSwitch.CACHE_TABLEDATA_OBJ:
            self.__tableDataObj = None

   if testSwitch.AutoFA_IDDIS_Enabled:
      def tableDataList(self):
           tableDataList = []
           if self.__recordList:
               tableDataList.append(self.__columnNameList)
               tableDataList.extend(self.__recordList)
           return tableDataList
   

   def tableDataObj(self):
      """
      Return data in a list of rows. Each row is a dictionary of column value pairs.
      EG:
         [{Col1:DataC1R1, Col2:DataC2R1...}
          {Col1:DataC1R2, Col2:DataC2R2...}
          ...
         ]
      """
      outList = []

      if DEBUG > 0:
         objMsg.printMsg("tableDataObj requested for %s" % self.tableName)

      if testSwitch.CACHE_TABLEDATA_OBJ:
         self.preRecordFetch()
         if not self.__tableDataObj == None:
            return self.__tableDataObj

      for rec in self.Records():
         if not rec == []:
            rowDict = dbLogListObj(dict(zip(self.__columnNameList,rec)))
            outList.append(rowDict)

      if outList in [[{}],[]]:
         self.raiseNoValidData()

      if DEBUG > 0:
         objMsg.printMsg("datObj= %s" % str(outList))

      if testSwitch.CACHE_TABLEDATA_OBJ:
         self.__tableDataObj = oUtil.copy(outList)

      return outList

   def diffDbLog(self, diffItem, entrySig, sortOrder=None, sigValArg=False, xform=None, xformArgs = [], xformUndef=None):
      """
      Convenience function that calls dbLogUtilities.diffDbLog with self
      """
      return diffDbLog(diffItem, entrySig, sortOrder, sigValArg, xform, xformArgs, xformUndef, self)

   def chopDbLog(self, parseColumn, matchStyle, matchName = None, tbl = None):
      """
      Convenience function that calls dbLogUtilities.chopDbLog with self.tableDataObj
      """
      if tbl == None:
         tbl = self.tableDataObj()
      return chopDbLog(parseColumn, matchStyle, matchName, tbl)

   def chopDbLogLoop(self, testZoneList, colParse, ColMatchStyle, tableName = None):
      """
      Convenience function that calls dbLogUtilities.chopDbLogLoop with self.tableDataObj and self.dut.imaxHead
      """
      if tableName == None:
         tableName = self.tableDataObj()
      return chopDbLogLoop(testZoneList, colParse, ColMatchStyle, tableName, self.dut.imaxHead)
      
   def yieldDblog(self, start = 0):
      if not testSwitch.virtualRun or testSwitch.unitTest:
         self.tableCode = self.getReverseTableHeader()
         recodes = len(self.dut.dblParser.objDbLogIndex.indicies[self.tableCode])
         if start < 0:
            start = recodes + start  
         ResultsFile.open('rb')
         try:
            for recordIndex in xrange(start, recodes):
               ResultsFile.seek(self.dut.dblParser.objDbLogIndex.indicies[self.tableCode][recordIndex][0])
               data = ResultsFile.read(self.dut.dblParser.objDbLogIndex.indicies[self.tableCode][recordIndex][1])
               rowData = self.dut.dblParser.addDbLogRow(data,self.tableCode,self.tableDef, self.dut.dblParser.objDbLogIndex.indicies[self.tableCode][recordIndex][2:],returnRowDataonly =1)
               yield rowData
         except:
            ResultsFile.close()
            self.raiseNoValidData()
         ResultsFile.close()
      else:
         for item in self.tableDataObj():
            yield item

class dbLogListObj(dict):
   """
   Class that provides the dictionary interface but also allows for get routines
      that utilize the dblogColAlias capability.
   """

   def copy(self):
      #Return an object of the same type with the items put into the new copy.
      # The default constructer would return a dict type explicitly which isn't the interface we provide
      return dbLogListObj(self.items())

   def get(self, key, default = None):
      """
      Implements the dict get interface with dblog column alias capability
      """
      #has_alias_key returns an interable
      #  [Bool, key]
      #     bool is the found/not found and
      #     key is the key to extract the actual column data

      if DEBUG > 1:
         objMsg.printMsg("Requested key: %s" % str(key))

      alias = dbLogColAliases.get(key)
      if alias is not None and key not in self:
         key = alias

      return dict.get(self,key, default)


   def __getitem__(self, key):
      return self.get(key)



class DbLog:
   """
   Class to build a DbLog set of parametrics to send to Oracle.

   To Use:
     1. Define table in DBLogDefs.py
     2. Use the following code to add data to your newly defined table:

     dblogObj = DbLog.DbLog()
     dblogObj.Table('ZONE_WRITE_STRESS_SCREEN').addRecord( {
                                                             'TEST_NAME':'DSTAbortScreens',
                                                             'RUN_NUMBER': 1,
                                                             'EXEC_TIME': 642.385
                                                             })

     Note that the dictionary passed to addRecord should be a set of key/value pairs where the keys
     are the column names and the values are the data that you want to store for that column.

     The XML output in DbLog format can be gotten simply by retrieving the string representation
     of an instance of this class.  You might do something like this to add it to the results file:

         WriteToResultsFile(str(dblogObj))
   """

   # Fetch the table definitions as a class variable from the DbLogDefs module.
   # These should be generated by some utility that talks to EDD
   OracleTableDefs = DBLogDefs.DbLogTableDefinitions.OracleTables

   def __init__(self, dut):
      self.__oracleTableDict = {}
      self.__oracleTablesOnly = 0
      self.__toBeDeletedTables = []
      self.dut = dut

   def remLocal(self):
      del self.__oracleTableDict
      self.__oracleTableDict = {}

   def setOracleMode(self, oracleOnly = 0):
      self.__oracleTablesOnly = oracleOnly

   def __add__(self, other):
      """
      Provides the ability to add two DbLog instances together.  This has the benefit of combining
      the data from two copies of the same table into one, thereby saving the overhead of the table
      header, column name list, and column type list when the data is later sent to Oracle.
      """

      if (type(self) == type(other)):
         for tableName, tableObj in other.Tables():

            # If the table from there also exists here, add them together.  Otherwise, just copy.
            if self.__oracleTableDict.has_key(tableName):
               self.__oracleTableDict[tableName] += tableObj
            else:
               self.__oracleTableDict[tableName] = tableObj

      return self

   def delTable(self, tableName, forceDeleteDblTable = 0):
      if not testSwitch.virtualRun == 1 or forceDeleteDblTable == 1:

         if testSwitch.BF_0144993_231166_P_FIX_KEY_ERROR_DBLOG_GOTF_BUG:
            if tableName in self.__oracleTableDict:
               try:
                  self.__oracleTableDict[tableName].deleteRecord()
                  del self.__oracleTableDict[tableName]
               except:
                  pass # missing data at lower level- ok for this purpose
         else:
            self.__oracleTableDict[tableName].deleteRecord()
            del self.__oracleTableDict[tableName]

         try:
            del self.dut.stateDBLogInfo[self.dut.currentState][self.dut.stateDBLogInfo[self.dut.currentState].index(tableName)]
         except ValueError:
            pass #Ignore as we probably already removed it in delTable

   def clearCachedData(self):
      if testSwitch.CACHE_TABLEDATA_OBJ:
         for table in self.__oracleTableDict.values():
            table.clearCachedData()

   def delAllOracleTables(self, confirmDelete=0):
      """
      Remove all index information about this table from the memory/disc structure and remove the table itself.
      Should only be used when you never want to retreive this info again.  Used for extreme cases like Depop Restart
      """
      tbl = self.dut.dblData.Tables()



      deleteExceptions = ['P_EVENT_SUMMARY','TEST_TIME_BY_TEST', 'TESTER_TIMESTAMP', 'TEST_TIME_BY_STATE'] #OracleTableOverrides

      for tblName, tblObj in tbl:
         if not tblName in deleteExceptions:
            try:
               tblObj.deleteIndexRecords(confirmDelete = 1)
               self.dut.dblData.delTable(tblName)
            except:
               self.dut.dblData.delTable(tblName)

      #re-initialize table related variables
      self.dut.GotDrvInfo = 0
      for key in self.dut.stateDBLogInfo:
         self.dut.stateDBLogInfo[key] = []
      objMsg.printMsg('All Oracle tables deleted except the following:')
      objMsg.printMsg(self.dut.dblData.Tables())

   def __str__(self):
      """
      Return the string representation of this DbLog object.  This simply concatenates the string
      representations of each of the contained DbLogTable instances and returns it.
      """

      dbLogStr = ''

      for tableName, tableObj in self.__oracleTableDict.items():
         try:
            tableObj.setOracleMode(self.__oracleTablesOnly)
            dbLogStr += str(tableObj)
         except:
            objMsg.printMsg("Error in str on %s:\n%s" % (tableName, traceback.format_exc()))

      return dbLogStr

   def dblTables(self):
      return self.__oracleTableDict


   def removeMarkedForDeleteTables(self):
      for tbl in self.__toBeDeletedTables:
         self.delTable(tbl)

   def markTableForDelete(self,tableName, removeFromList = False):
      if testSwitch.BF_0144790_231166_P_FIX_GOTF_DBL_REGRADE_DUP_ROWS:
         if removeFromList and tableName in self.__toBeDeletedTables:
            self.__toBeDeletedTables.remove(tableName)
         else:
            self.__toBeDeletedTables.append(tableName)
      else:
         self.__toBeDeletedTables.append(tableName)

   if testSwitch.AutoFA_IDDIS_Enabled:
      def getAllTableDataList(self):
         tables = {}
         for key,value in self.__oracleTableDict.items():
             tableName = has_alias_key( dbLogTableAliases.get(key,[]), self.__oracleTableDict)
             if not tableName:
               continue
             tables[key] = []
             if value != []:
               tables[key] = value.tableDataList()
         return tables

   def Tables(self, tableName = None, tableDef = None):
      """
      Returns the table object specified by tableName.  If the table hasn't previously been used,
      this function will create an instance of the DbLogTable and add it to the internal list.

      If no tableName is specified, returns a list of the tables that have been added to this DbLog instance.
      Returns key/value pairs where the key is the table name, and the value is the corresponding
      DbLogTable instance.

      Oracle Table definitions are of the type...
      'ZN_WRITE_STRESS':
         {
             'type': 'S',
             'fieldList': [
                 DbLogColumn('TEST_NAME', 'V'),
                 DbLogColumn('RUN_NUM', 'N'),
                 DbLogColumn('RUN_TIME', 'N'),
                          ]
         }
      """

      if tableName == None:
         # user wants a full list of tables
         return self.__oracleTableDict.items()
      else:

         # user is trying to add a table or get a table
         tableName = has_alias_key( dbLogTableAliases.get(tableName,[]), self.__oracleTableDict , tableName)

         if not self.__oracleTableDict.has_key(tableName):
            #if we failed to locate a previously added table
            #  then we initialize with the instantiated table sent to function
            if tableDef == None:
               if self.OracleTableDefs.has_key(tableName):
                  #Process defined table
                  self.__oracleTableDict[tableName] = DbLogTable(tableName, self.OracleTableDefs[tableName],\
                                                      self.dut, markForDeleteCallback = self.markTableForDelete)
               else:
                  #Create a blank table with the table name for later population
                  self.__oracleTableDict[tableName] = DbLogTable(tableName,tableDef = {},\
                                                      dut = self.dut, markForDeleteCallback = self.markTableForDelete)
            else:
               #Fully structured table entered in
               self.__oracleTableDict[tableName] = DbLogTable(tableName, tableDef,\
                                                   self.dut, markForDeleteCallback = self.markTableForDelete)

         return self.__oracleTableDict[tableName]
