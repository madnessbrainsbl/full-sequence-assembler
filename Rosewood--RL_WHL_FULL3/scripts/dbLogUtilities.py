#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Module that stores utilities for dealing with dblog data
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/10/02 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/dbLogUtilities.py $
# $Revision: #4 $
# $DateTime: 2016/10/02 23:40:57 $
# $Author: yihua.jiang $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/dbLogUtilities.py#4 $
# Level:3
#---------------------------------------------------------------------------------------------------------#

from Constants import *
import MessageHandler as objMsg
import ScrCmds, types
from Exceptions import CDblogDataMissing


def has_alias_key(keyList, mdict, default = None):
   """
   Function returns the key from the alias dictionary
   @param keyList: List of keys to check for in the mdict
   @param mdict: input dictionary to check the keylist against
   """

   for key in keyList:
      if mdict.has_key(key):
         if DEBUG > 0:
            objMsg.printMsg('Found alias %s' % str(key))
         return key
   return default

def chopDbLog(parseColumn, matchStyle, matchName = None, tbl = None):
   """
   Return the input DBLog table (tbl), parsed using the given inputs
   @type parseColumn: string
   @param parseColumn: DBLog column name to parse the table by
   @type matchStyle: string
   @param matchStyle: 'max', 'min', or 'match'.  If 'max' or 'min', pick values out
   of the table that match the maximum or minimum value (strings will be converted
   to float values to determine the max or min) in the given parseColumn.  If
   'match', pick values matching the string given in the matchName parameter
   @type matchName: string
   @param matchName: If matchStyle is 'match' pick values out of the table that match this input
   @return: List of dictionaries: Return dictionaries in the requested DBLog table
   that match the given inputs
   """

   # Get the table if necc
   if tbl == None:
      ScrCmds.raiseException(11044,"Invalid parameters entered for chopDbLog")

   # Check that parseColumn exists in the requested Log.  If so, get the first data point
   try:
      matchVal = tbl[0][parseColumn]
   except KeyError:
      ScrCmds.raiseException(11044, "chopDbLog requested parseColumn, %s, does not exist for tableRow: %s" % (parseColumn, tbl))
   except IndexError:
      ScrCmds.raiseException(11044, "Input table empty: %s" % (tbl,))

   strMatchVal = str(matchVal)
   # If matchVal is a string that can be converted to a float, convert all values
   #  when looking for max or min
   try:
      matchVal = float(matchVal)
      convMatchVal = 1  # Convert matchVal to float
   except:
      convMatchVal = 0

   # if matchStyle is 'max' or 'min', create a comparison function
   if matchStyle == 'max':
      compare = lambda x: x > matchVal
   elif matchStyle == 'min':
      compare = lambda x: x < matchVal

   # Find the item to parse by, if matchStyle is not 'match'
   if matchStyle in ('max', 'min'):
      for entry, row in enumerate(tbl):
         compVal = row.get(parseColumn)
         if convMatchVal:
            compVal = float(compVal)
         if compare(compVal):
            strMatchVal = str(row.get(parseColumn))
            if convMatchVal:
               matchVal = float(strMatchVal)
            else:
               matchVal = strMatchVal
   elif matchStyle == 'match':
      strMatchVal = str(matchName)
   else:
      ScrCmds.raiseException(11044, "chopDbLog invalid matchStyle.  matchStyle must be 'max', 'min', or 'match', but function input is %s" % matchStyle)

   parseTbl = []
   parseTbl = [row for row in tbl if str(row.get(parseColumn)) == strMatchVal]

   return parseTbl

def chopDbLogLoop(testZoneList, colParse, ColMatchStyle, tableName, imaxHead):
   """
   Loop through a table by head/zone.
   For each zone, parse ou tthe min,max or matched value for a given column.
   no duplicate rows allowed after the last chop. return the finalTable.
   """
   finalTable= []
   for head in xrange(imaxHead):
      headData = chopDbLog('HD_LGC_PSN','match',str(head),tableName)
      for zone in xrange(len(testZoneList)):
         zoneData = chopDbLog('DATA_ZONE','match',str(testZoneList[zone]),headData)
         hdZoneParse = chopDbLog(parseColumn=colParse, matchStyle=ColMatchStyle, tbl=zoneData)
         if len(hdZoneParse) > 0:
            hdZoneParse = [hdZoneParse[len(hdZoneParse)-1]] # blm take the last entry if duplicate data
         finalTable.extend(hdZoneParse)
   return finalTable

def __createArgs(initialVal, args):
   """
   Helper function for __applyXform to extend arg list
   """
   tArgs = [initialVal,]
   if len(args) > 1:
      tArgs.extend(list(args))
   else:
      tArgs.append(args[0])
   return tArgs

def __applyXform(data,func,args,undefVal):
   """
   Helper function for diffDbLog to transform data types via mapping or list comprehension
   """
   #Create a copy
   tArgs = __createArgs(data,args)
   try:   #Calc transform of data
      x = func(*tArgs)
   except (OverflowError, ValueError) :  #Transform is undefined, so use alternate value
      tArgs = __createArgs(undefVal,args)
      x = func(*tArgs)
   return x

def __formName(name, signifier, value):
   """
   Create a standard return name-form
   """
   return "%s__%s_%s" %(name, signifier, value)


def __enterAndDiff(TDItem, DDItem, diffItem, entrySig, currEntrySigVal, entrySigVals, xform, xformArgs, xformUndef):
   """
   Helper frunction to xform data based on input type
   """
   newEntryName = __formName(diffItem, entrySig, currEntrySigVal)

   DDItem[newEntryName] = float(TDItem.get(diffItem))
   if xform:
      if not type(xform) in [types.ListType, types.TupleType]:
         xform = [xform,]
      if not type(xformArgs) in [types.ListType, types.TupleType]:
         xformArgs = [xformArgs,]

      for funcIndex in xrange(len(xform)):
         DDItem[newEntryName] = __applyXform(DDItem.get(newEntryName),xform[funcIndex],xformArgs[funcIndex],xformUndef)

   # Calculate the differnce as the change between the first entry and the last entry=
   DDItem['difference'] = float(DDItem.get(__formName(diffItem, entrySig, entrySigVals[-1]))) - \
                        float(DDItem.get(__formName(diffItem, entrySig, entrySigVals[0])))
   return DDItem


def diffDbLog(diffItem, entrySig, sortOrder=None, sigValArg=False, xform=None, xformArgs = [], xformUndef=None, tableObj = None):
   """
   Calculate a difference for the items in column diffItem.  The difference
   will be calculated based on the smallest and largest values in the column
   noted by entrySig.  Columns listed in sortOrder will be used to further
   narrow the items to be differenced.

   @type diffItem: String
   @param diffItem: Column name of the item to difference
   @type entrySig: String
   @param entrySig: Column used to differentiate one log entry from another.
         If there are more than two values in this column, the difference will
         be calculated using the smallest and largest values.
   @type sortOrder: A string or list of strings
   @param sortOrder: Items to sort by. For a type S table, this will be None.
         For a type V table (one dimension) this will have one entry, and there
         will be two entries for a type M (2D) table.
   @type sigValArg: List of strings
   @param sigValArg: Force delta comparison of two specific entrySig identifiers
         (e.g. spc_id 2 and 4)
   @type xform: Single or tuple of math functions (e.g. math.log)
   @param xform: For each data value that meets requirements, data will be transformed
         by each function supplied.
   @type xformArgs: List (e.g. [(10,)])
   @param xformArgs: Arguments used to pass to supplied math transform. If multiple
         math transforms used, arguments for each should be in separate lists
         (e.g. [(10,),(10,)])
   @type xformUndef: Float
   @param xformUndef: For some data, suplpied math transform may be undefined
         (e.g. log10(0)). In the case where a transform is undefined, replace
         input data value with value supplied in this argument, and then tranform.

   @return maxDiff: The maximum difference found
   @return minDiff: the minimum difference found
   @return diffData: The collected difference information
   @return entrySigValues: The values in the entrySig column used to calculate the difference
   """

   # If the user input sortOrder as a string, convert it to a list
   if type(sortOrder) == types.StringType:
      temp = []
      temp.append(sortOrder)
      sortOrder = temp

   # Get dbLog info - needed prior to checking table attributes
   if tableObj == None:
      ScrCmds.raiseException(11044, "Invalid parameters for diffDbLog")

   tableData = tableObj.tableDataObj()

   # Make sure the number of inputs match the table type
   objMsg.printMsg("diffDbLog: Table name is: %s" % tableObj.tableName, objMsg.CMessLvl.VERBOSEDEBUG)
   objMsg.printMsg("diffDbLog: Table type is: %s" % tableObj.tableType, objMsg.CMessLvl.VERBOSEDEBUG)
   if DEBUG > 0:
      objMsg.printMsg("tableData is: %s" % tableData, objMsg.CMessLvl.VERBOSEDEBUG)
   if tableObj.tableType == 'V' and len(sortOrder) < 1:
      ScrCmds.raiseException(11044, "Not enough sortOrder entries for type 'V' table")
   elif tableObj.tableType == 'M' and len(sortOrder) < 2:
      ScrCmds.raiseException(11044, "Not enough sortOrder entries for type 'M' table")

   # Calculate the table entry signifiers
   entrySigVals = []
   for item in tableData:
      if item.get(entrySig) not in entrySigVals:
         entrySigVals.append(item.get(entrySig))
   objMsg.printMsg("entrySig %s table values are: %s" % (entrySig,str(entrySigVals)), objMsg.CMessLvl.VERBOSEDEBUG)
   # Raise error if there are not at least two values associated with entrySig
   if len(entrySigVals) < 2:
      ScrCmds.raiseException(11044, "entrySig (%s) data needs at least two values to calculate a difference" % entrySig)

      # Pick the smallest and largest values.
      # Try to convert strings to numbers to see if they are numbers represented as strings.
      # If so, sort numerically instead of alphabetically
   try:
      numVals = []
      numVals = [float(entry) for entry in entrySigVals]
      entrySigValsToDiff = [entrySigVals[numVals.index(min(numVals))],entrySigVals[numVals.index(max(numVals))]]
   except ValueError: #The case where we get a string within a string (example: '"-5.6"'), or it's just a normal string
      try: #If string within a string, this will pass
         numVals = [float(eval(entry)) for entry in entrySigVals]
         entrySigValsToDiff = [entrySigVals[numVals.index(min(numVals))],entrySigVals[numVals.index(max(numVals))]]
      except: #Otherwise, assume we are not a string and sort as normal
         entrySigVals.sort()
         entrySigValsToDiff = [entrySigVals[0],entrySigVals[-1]]

   if sigValArg: #Identifiers passed in on command line
      if (len(sigValArg) < 2) or (sigValArg[0] == sigValArg[1]):
         ScrCmds.raiseException(11044, "entrySig (%s) data needs at least two values to calculate a difference" % entrySig)
      try:  #Identifier types match those from DbLog
         entrySigValsToDiff = [entrySigVals[entrySigVals.index(sigValArg[0])],entrySigVals[entrySigVals.index(sigValArg[1])]]
      except:
         #Identifier types didn't match, use numVals from above
         # ASSUMES 1) numVals shall always be numbers, 2) Identifiers passed in are numbers
         try:
            entrySigValsToDiff = [entrySigVals[numVals.index(sigValArg[0])],entrySigVals[numVals.index(sigValArg[1])]]
         except:
            ScrCmds.raiseException(11044, "entrySig (%s) data needs at least two values to calculate a difference" % entrySig)

   objMsg.printMsg("entrySigVal1: %s; 2: %s" % (entrySigValsToDiff[0],entrySigValsToDiff[1]), objMsg.CMessLvl.VERBOSEDEBUG)

   # Collect the necessary information in a new dictionary and calculate the differences
   diffData = []
   for TDItem in tableData:
      # See if this TDItem matches what we are trying to collect
      currEntrySigVal = TDItem.get(entrySig)
      if currEntrySigVal == entrySigValsToDiff[0]:
         findEntrySigVal = entrySigValsToDiff[1]
      elif currEntrySigVal == entrySigValsToDiff[1]:
         findEntrySigVal = entrySigValsToDiff[0]
      else:
         continue  # No match for this line, continue with the next line in tableData
      # Try to find a matching line in the already-collected data
      if len(diffData) > 0:
         findKeyName = __formName(diffItem,entrySig,findEntrySigVal)
         foundDDItemMatch = 0
         for DDItem in diffData:
            if DDItem.has_key(findKeyName):  #if we've found a matching line
               # If we have sortOrder items, make sure they match as well
               if sortOrder != None:
                  for SOItem in sortOrder:
                     if TDItem.get(SOItem) != DDItem.get(SOItem):  # we don't have a match
                        break
                     elif SOItem == sortOrder[-1]:  # we have matched all sortOrder items
                        # Here, we have matched sortOrder items and findEntrySigVal.  So
                        #  we need to append the diffItem value associated with currEntrySigVal
                        #  to the dictionary, and calculate the difference
                        foundDDItemMatch = 1
                        DDItem = __enterAndDiff(TDItem, DDItem, diffItem, entrySig, currEntrySigVal, entrySigValsToDiff, xform, xformArgs, xformUndef)
               else:  # if sortOrder==None, we have a match, just add the new entry
                  foundDDItemMatch = 1
                  DDItem = __enterAndDiff(TDItem, DDItem, diffItem, entrySig, currEntrySigVal, entrySigValsToDiff, xform, xformArgs, xformUndef)
      if len(diffData) < 1 or (DDItem == diffData[-1] and foundDDItemMatch == 0):
         # If we get here, we have not found a match, and need to create a new entry in diffData
         #newEntry = {__formName(diffItem, entrySig, TDItem.get(entrySig)):float(TDItem.get(diffItem))}
         newDataValue = float(TDItem.get(diffItem))
         if xform:
            if not type(xform) in [types.ListType, types.TupleType]:
               xform = [xform,]
            if not type(xformArgs) in [types.ListType, types.TupleType]:
               xformArgs = [xformArgs,]

            for funcIndex in xrange(len(xform)):
               newDataValue = __applyXform(newDataValue,xform[funcIndex],xformArgs[funcIndex],xformUndef)

         newEntry = {__formName(diffItem, entrySig, TDItem.get(entrySig)):newDataValue}
         if sortOrder != None:
            for SOItem in sortOrder:
               newEntry[SOItem] = TDItem.get(SOItem)
         diffData.append(newEntry)
   objMsg.printMsg("Final diffData is: %s" % diffData, objMsg.CMessLvl.VERBOSEDEBUG)

   # Calculate the maximum and minimum differences
   maxDiff = diffData[0]['difference']
   minDiff = diffData[0]['difference']
   for item in diffData:
      if item.get('difference', maxDiff) > maxDiff:
         maxDiff = item['difference']
      elif item.get('difference', minDiff) < minDiff:
         minDiff = item['difference']

   return (maxDiff, minDiff, diffData, entrySigValsToDiff)


###########################################################################################
# Convience class for accessing DBLog data
# Abstracts the handling for VE, table suppression, stale data
# Provides convenience functions for looking up specific rows
###########################################################################################
class DBLogReader:
   def __init__(self, dut, table_name, suppressed=False):
      self.dut = dut
      self.table_name = table_name
      self.start_rows = 0

      if testSwitch.virtualRun:
         suppressed = False

      self.suppressed = suppressed

   def getTableObj(self):
      if self.suppressed:
         try:
            dataList = self.dut.objSeq.SuprsDblObject[self.table_name]
         except KeyError:
            dataList = []
      else:
         try:
            dataList = self.dut.dblData.Tables(self.table_name).tableDataObj()
         except CDblogDataMissing:
            dataList = []

      return dataList

   def getRowCount(self):
      rows = len(self.getTableObj())
      return rows

   def ignoreExistingData(self):
      if testSwitch.virtualRun:
         self.start_rows = 0
      else:
         self.start_rows = self.getRowCount()

   def iterRows(self):
      final_rows = self.getRowCount()
      table_data = self.getTableObj()
      return iter(table_data[self.start_rows:final_rows])

   def getRows(self, criteria):

      columns = criteria.keys()

      # Filter out the non-matching rows
      rows = list(self.iterRows())
      for column in columns:
         cast = type(criteria[column]) # Cast the row data into the same type as the criteria data
         column_match = lambda row: cast(row[column]) == criteria[column]
         rows = filter(column_match, rows)

      return rows

   def findRow(self, criteria):
      '''Find the latest matching row, or an empty row if no match is found.
         criteria is a dictionary containing {column_name:value} to match against.'''

      rows = self.getRows(criteria)

      # Return the latest matching row, else an empty row
      if len(rows) > 0:
         return rows[-1]
      else:
         return {}


###########################################################################################
# Class to check set of criteria with dblog table, esp for screening
###########################################################################################
class DBLogCheck:
   def __init__(self, dut, title=None, verboseLevel=1):
      self.dut = dut
      self.debug = verboseLevel + testSwitch.virtualRun - testSwitch.FE_0299849_356688_P_CM_REDUCTION_REDUCE_PRINT # so that VE will print more info for debugging
      self.screenResult = {}
      self.headOffset = -1
      self.failHead = []
      self.title = title

   #-------------------------------------------------------------------------------------------------------------------------------
   # Return list of PASS/True and FAIL/False for each corresponding heads
   # Format of criteria to pass in as below:
   # (table_name, checking_type)      : { # table_name = name of db table, checking_type = match/count/max/min/mean/first/last
   #    'spc_id'       : to filter by SPC_ID. Default is all tables available if omitted
   #    'row_sort'     : category to separate. Default is HD_LGC_PSN if omitted
   #    'col_sort'     : sub-category to get. For col_range use. Default is DATA_ZONE if omitted
   #    'col_range'    : List/Tuple of sub-categories to get. Use with col_sort. Default is any, no filtering
   #    'column'       : column header to get the data from               }
   #    'compare'      : compare operation to evaluate with               }=> these 3 must be either single value or matching tuple
   #    'criteria'     : criteria to evaluate with (meet criteria = FAIL) }
   #    'fail_count'   : if num of pt fail criteria > fail_count for each head, fail the head. Default is total criteria
   #                   : must have for checking_type=count, this is the count number to fail if equal or exceeded (>=)
   # },
   #-------------------------------------------------------------------------------------------------------------------------------
   def checkCriteria(self, tblHdr, chkType, criteria):
      from MathLib import mean, stDev #, stDev_standard

      critlen   = len(criteria['criteria'])
      sortRow   = criteria.get('row_sort', ('HD_LGC_PSN',))
      sortCol   = criteria.get('col_sort', 'DATA_ZONE')
      resultRow = {}
      failcount = criteria.get('fail_count', critlen) # num of criteria to fail to trigger FAIL
      failcount = max(failcount, 1)                   # cannot less than 1
      
      if self.debug:
         tmpstr = "FailCriteria=%d/%d, Row=%s, Col=%s" % (failcount, critlen, sortRow, sortCol)
         if 'col_range' in criteria:
            try:
               tmpstr = tmpstr + ", Range=%s" % self.HumanizeList(criteria['col_range'])
            except:
               tmpstr = tmpstr + ", Range=%s" % str(criteria['col_range'])
         if 'spc_id' in criteria:
            tmpstr = tmpstr + ", spc_id=%s" % str(criteria['spc_id'])
         objMsg.printMsg(tmpstr)
      if 'HD_LGC_PSN' in sortRow:
         try:
            self.headOffset = sortRow.index('HD_LGC_PSN')
         except AttributeError: # for py2.4 compatibility
            self.headOffset = list(sortRow).index('HD_LGC_PSN')

      try:
         if 'spc_id' in criteria: # if spc_id is defined, then get only tables matching the spc_id
            tbl = self.dut.dblData.Tables(tblHdr).chopDbLog('SPC_ID', 'match', str(criteria['spc_id']))
            if 'fail_code' in criteria: # if fail_code is defined, then get only tables matching the fail_code
                tbl = self.dut.dblData.Tables(tblHdr).chopDbLog('FAIL_CODE', 'match', str(criteria['fail_code']),tbl = tbl )            
            if 'msrd_intrpltd' in criteria: 
                tbl = self.dut.dblData.Tables(tblHdr).chopDbLog('MSRD_INTRPLTD', 'match', str(criteria['msrd_intrpltd']),tbl = tbl )
            if 'active_heater' in criteria: 
                tbl = self.dut.dblData.Tables(tblHdr).chopDbLog('ACTIVE_HEATER', 'match', str(criteria['active_heater']),tbl = tbl )                
         else:
            tbl = self.dut.dblData.Tables(tblHdr).tableDataObj()
         if 'fail_code' in criteria: # if fail_code is defined, then get only tables matching the fail_code
             tbl = self.dut.dblData.Tables(tblHdr).chopDbLog('FAIL_CODE', 'match', str(criteria['fail_code']), tbl=tbl)
      except:
         objMsg.printMsg("Unable to find table %s !!" % tblHdr)
         return resultRow

      zipcrit = zip(criteria['column'], criteria['compare'], criteria['criteria'])

      #------------------------------------------------------------------------------
      if chkType == 'match':   # if eval val to spec = True --> FAIL
         for entry,row in enumerate(tbl):
            if ('col_range' not in criteria) or (type(criteria['col_range'][0])(row[sortCol]) in criteria['col_range']):
               rowVal = tuple([row[i] for i in sortRow])
               cnt = 0
               tmpstr = '%s=%s: ' % (sortRow, rowVal)
               for col,oper,spec in zipcrit:
                  val = type(spec)(row[col])
                  flg = eval('%s %s %s' % (`val`, oper, `spec`))  # True if meet criteria == FAIL criteria
                  cnt += flg                                      # count of no of times didn't meet criteria
                  tmpstr += '%s=%s (%s %s) %d ' % (col, `val`, oper, `spec`, flg)
               tmpstr += '(%d), ' % (cnt)
               if (cnt < failcount): tmpstr += 'PASS'
               else: tmpstr += 'FAIL'
               if self.debug > 1 or (cnt >= failcount): objMsg.printMsg(tmpstr)
               resultRow[rowVal] = resultRow.get(rowVal, False) or (cnt >= failcount)

      #------------------------------------------------------------------------------
      if chkType == 'delta' and 'column2' in criteria and len(criteria['column2']) == len(zipcrit):   # if eval delta val to spec = True --> FAIL
         zipcrit = zip(criteria['column'], criteria['column2'], criteria['compare'], criteria['criteria'])
         for entry,row in enumerate(tbl):
            if ('col_range' not in criteria) or (type(criteria['col_range'][0])(row[sortCol]) in criteria['col_range']):
               rowVal = tuple([row[i] for i in sortRow])
               cnt = 0
               tmpstr = '%s=%s: ' % (sortRow, rowVal)
               for col,col2,oper,spec in zipcrit:
                  if self.debug > 1: objMsg.printMsg('%s%s=%s, %s=%s' % (tmpstr, col, type(spec)(row[col]), col2, type(spec)(row[col2])))
                  val = type(spec)(row[col]) - type(spec)(row[col2])
                  flg = eval('%s %s %s' % (`val`, oper, `spec`))  # True if meet criteria == FAIL criteria
                  cnt += flg                                   # count of no of times didn't meet criteria
                  tmpstr += '(%s-%s)=%s (%s %s) %d ' % (col, col2, `val`, oper, `spec`, flg)
               tmpstr += '(%d), ' % (cnt)
               if (cnt < failcount): tmpstr += 'PASS'
               else: tmpstr += 'FAIL'
               if self.debug > 1 or (cnt >= failcount): objMsg.printMsg(tmpstr)
               resultRow[rowVal] = resultRow.get(rowVal, False) or (cnt >= failcount)

      #------------------------------------------------------------------------------
      elif chkType == 'count' and 'fail_count' in criteria:  # if count of (eval val to spec == False) > fail_count == Fail
         fail_cnt = {}
         for entry,row in enumerate(tbl):
            if ('col_range' not in criteria) or (type(criteria['col_range'][0])(row[sortCol]) in criteria['col_range']):
               rowVal = tuple([row[i] for i in sortRow])
               if rowVal not in fail_cnt: fail_cnt[rowVal] = 0
               tmpstr = '%s=%s: ' % (sortRow, rowVal)
               FailCrit = True # default to True, so any criteria that pass will set this to False
               for col,oper,spec in zipcrit:
                  val = type(spec)(row[col])    # value of the item for current row in the dblog table
                  flg = eval('%s %s %s' % (`val`, oper, `spec`))  # True if meet criteria == FAIL criteria
                  FailCrit = FailCrit and flg
                  tmpstr += '%s=%s (%s %s) %d, ' % (col, `val`, oper, `spec`, flg)
               fail_cnt[rowVal] += FailCrit
               if self.debug > 1 or FailCrit:
                  tmpstr += 'TOTAL=%d' % (fail_cnt[rowVal])
                  objMsg.printMsg(tmpstr)
         for res in fail_cnt:
            if self.debug > 1:
               if (fail_cnt[res] < failcount): tmpstr = 'PASS'
               else: tmpstr = 'FAIL'
               objMsg.printMsg('%s: Fail Count=%d (Limit: %d) %s' % (res, fail_cnt[res], failcount, tmpstr))
            resultRow[res] = resultRow.get(res, False) or (fail_cnt[res] >= failcount)

      #------------------------------------------------------------------------------
      elif chkType in ('mean', 'max', 'min', 'first', 'last', 'stDev', 'max - mean', 'max - min', 'mean - min'):   # if eval func(val) to spec = True --> Pass
         val_sum = {}
         for entry,row in enumerate(tbl):
            if ('col_range' not in criteria) or (type(criteria['col_range'][0])(row[sortCol]) in criteria['col_range']):
               rowVal = tuple([row[i] for i in sortRow])
               if rowVal not in val_sum: val_sum[rowVal] = {}
               cnt = 0
               for col,oper,spec in zipcrit:
                  if col not in val_sum[rowVal]: val_sum[rowVal][col] = []
                  val = type(spec)(row[col])    # value of the item for current row in the dblog table
                  if chkType == 'last' or (chkType == 'first' and val_sum[rowVal][col] == []):   # only take the first or last value
                     val_sum[rowVal][col] = val
                  elif chkType in ('mean', 'max', 'min', 'stDev', 'max - mean', 'max - min', 'mean - min'):
                     val_sum[rowVal][col].append(val) # add all the values as a list, will average/max/min them later

         # if self.debug > 1:
            # objMsg.printMsg("val_sum=%s" % (val_sum))
         for rowVal in val_sum:
            tmpstr = '%s=%s: ' % (sortRow, rowVal)
            for col,oper,spec in zipcrit:
               if col in val_sum[rowVal]:
                  if chkType in ('mean', 'max', 'min', 'stDev'):
                     val_sum[rowVal][col] = eval('%s(val_sum[rowVal][col])' % (chkType))
                  elif chkType in ('max - mean', 'max - min', 'mean - min',):
                     subOper = chkType.split()
                     if len(subOper) >= 3:
                        val = eval('%s(val_sum[rowVal][col])' % (subOper[0]))
                        for i in xrange(1,len(subOper),2):
                           val = eval('val %s %s(val_sum[rowVal][col])' % (subOper[i], subOper[i+1]))
                        val_sum[rowVal][col] = val
                  flg = eval('%s %s %s' % (`val_sum[rowVal][col]`, oper, `spec`))   # True if meet criteria == FAIL criteria
                  resultRow[rowVal] = resultRow.get(rowVal, False) or (flg)
                  if self.debug:
                     tmpstr += "%s=%s, (%s %s) " % (col, `val_sum[rowVal][col]`, oper, `spec`)
                     if (flg): tmpstr += 'FAIL'
                     else: tmpstr += 'PASS'
                     objMsg.printMsg(tmpstr)

      if self.debug > 1:
         tmpstr = ''
         for res in sorted(resultRow):
            tmpstr += '%s: %s, ' % (`res`, resultRow[res])
         objMsg.printMsg("resultRow={%s}" % (tmpstr))
      return resultRow

   #-------------------------------------------------------------------------------------------------------
   def HumanizeList(self, pylist):
      if len(pylist) == 0: return '<empty>'
      tmpstr = ''
      start = end = None
      for val in sorted(pylist):
         if start == None:
            start = val
         elif end == None:
            if val == (start + 1):
               end = val
            else:
               tmpstr += '%d, ' % start
               start = val
         else:
            if val == (end + 1):
               end = val
            else:
               tmpstr += '%d-%d, ' % (start, end)
               start = val
               end = None
      if end == None:
         tmpstr += '%d' % start
      else:
         tmpstr += '%d-%d' % (start, end)
      return tmpstr

   #-------------------------------------------------------------------------------------------------------
   def ConvertToTuple(self, prm, validate=True, keys=None):
      if keys == None:
         keys = ('row_sort','column','column2','compare','criteria')
      for key in keys:
         if key not in prm:
            continue
         if type(prm[key]) not in (types.ListType, types.TupleType):
            prm[key] = prm[key],
         if validate:
            if type(prm[key]) not in (types.ListType, types.TupleType):
               ScrCmds.raiseException(11044, "Invalid parameters entered for DBLogCheck")
      return 0

   #-------------------------------------------------------------------------------------------------------
   def checkComboScreen(self, prmMain, newparams=None):
      self.screenResult = {}
      if not prmMain:
         return PASS
      if ('Title','') in prmMain:
         objMsg.printMsg("="*15 + " %s " % prmMain[('Title','')] + "="*15)
      elif self.title:
         objMsg.printMsg("="*15 + " %s " % self.title + "="*15)
      else:
         objMsg.printMsg("="*15 + " DBLog Screening " + "="*15)

      Fail_Cnt = max(1, prmMain.get(('Fail_Cnt',''), len(prmMain)-(('Title','') in prmMain))) # Fail_Cnt must be minimum 1, else all drives will fail
      FailedRow = {}

      for tblHdr,chkType in prmMain.iterkeys():
         if tblHdr in ('Fail_Cnt','Title'): continue
         prm = prmMain[(tblHdr,chkType)]
         if not prm: continue
         if newparams:
            try:     prm.update(newparams)
            except:
               objMsg.printMsg('Invalid newparams %s !' % str(newparams))
               pass
         try:
            self.ConvertToTuple(prm)
         except:
            objMsg.printMsg('Invalid screen criteria in (%s, %s)! Assume PASS!' % (tblHdr, chkType))
            if testSwitch.virtualRun: raise
            continue
         if self.debug:
            objMsg.printMsg("-"*5 + " tbl=%s, type=%s " % (tblHdr, chkType) + "-"*5)
            tmpstr = 'Criteria = '
            try:
               zipcrit = zip(prm['column'], prm['compare'], prm['criteria'])
            except:
               objMsg.printMsg('Invalid screen criteria in (%s, %s)! Assume PASS!' % (tblHdr, chkType))
               if testSwitch.virtualRun: raise
               continue
            for col,oper,spec in zipcrit:
               tmpstr += '%s %s %s, ' % (col, oper, `spec`)
            objMsg.printMsg(tmpstr[:-2])

         try: # in case table error, then assume pass
            resultRow  = self.checkCriteria(tblHdr, chkType, prm)
         except:
            objMsg.printMsg('Error in screening check for (%s, %s)! Assume PASS!' % (tblHdr, chkType))
            if testSwitch.virtualRun: raise
            continue
         for res in resultRow:
            FailedRow[res] = FailedRow.get(res, 0) + (resultRow[res])
         if self.debug > 1:
            tmpstr = ''
            for res in sorted(FailedRow):
               tmpstr += '%s: %s, ' % (`res`, FailedRow[res])
            objMsg.printMsg("FailedRow={%s}" % (tmpstr[:-2]))

      objMsg.printMsg("=" * 50)
      if self.debug > 1:
         objMsg.printMsg("Fail_Cnt = %d" % Fail_Cnt)
      if self.debug:
         tmpstr = ''
         for res in sorted(FailedRow):
            tmpstr += '%s: %s, ' % (`res`, FailedRow[res])
         objMsg.printMsg("Failed Screen = {%s}" % (tmpstr[:-2]))

      failScreen = PASS
      for res in sorted(FailedRow):
         if self.debug > 1:
            objMsg.printMsg("%s : %s" % (res, FailedRow[res]))
         self.screenResult[res] = (FailedRow[res] < Fail_Cnt)
         failScreen = failScreen and (FailedRow[res] < Fail_Cnt)
         if FailedRow[res] >= Fail_Cnt and self.headOffset > -1 and int(res[self.headOffset]) not in self.failHead:
            self.failHead.append(int(res[self.headOffset]))
      return failScreen # 1=PASS, 0=FAIL

