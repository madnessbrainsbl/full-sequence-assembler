#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: GOTF (Grading On The Fly)  Main Module
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_GOTF.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_GOTF.py#1 $
# Level: 4
#---------------------------------------------------------------------------------------------------------#

#---------------------------------------------------------------------------------------------------------#
import re, traceback
import os
import ScrCmds
from Constants import *
import MessageHandler as objMsg
from Drive import objDut
from SIM_FSO import objSimArea

from DbLogAlias import processTableOverrides
from TestParamExtractor import TP

GOTF_DEBUG = 0
#---------------------------------------------------------------------------------------------------------#

#---------------------------------------------------------------------------------------------------------#
class CGOTFDBlogTools:

   #------------------------------------------------------------------------------------------------------#
   def gotfGetColVal(self,table):        # Returns dictionary of columns along with values for the reqeusted table

      columndict = {}
      filterColDict = {}
      if GOTF_DEBUG != 0:
         objMsg.printMsg("GOTF: Extracting Columns and Values for Table: %s" % str(table))
      for criteria_table in self.gotfCriteria:
         if criteria_table == table:
            logdata = self.dut.dblData.Tables(criteria_table).tableDataObj()
            for column in self.gotfCriteria[criteria_table]['ColumnPosDict']:
               columndict[column] = []

               for record in logdata:
                  if record.has_key(column):
                     if record[column].__class__ == list:         # Check to see if values already in form of list
                        columndict[column].extend(record[column]) #  - use .extend to avoid nesting lists
                     else:
                        columndict[column].append(record[column]) # Else use append - assume single value (str,dec etc.)


            for column in self.gotfCriteria[criteria_table]['FilterColList']:
               filterColDict[column] = []
               for record in logdata:
                  tmprec = record.get(column, self.dut.driveattr.get(column, DriveAttributes.get(column, getattr(self.dut,column,None))))
                  if tmprec != None:
                     if tmprec.__class__ == list:         # Check to see if values already in form of list
                        filterColDict[column].extend(tmprec) #  - use .extend to avoid nesting lists
                     else:
                        filterColDict[column].append(tmprec) # Else use append - assume single value (str,dec etc.)
                  else:
                     filterColDict[column].append("_NOT_FOUND_")

            #Remove the local logdata variable for this loop
            del logdata

      if columndict == {} and GOTF_DEBUG != 0:
         objMsg.printMsg("GOTF WARNING: Failed to find any matching Columns and Values for Table: %s" % str(table))
      return columndict, filterColDict


#---------------------------------------------------------------------------------------------------------#
class CGOTFxmlTools:

   #------------------------------------------------------------------------------------------------------#
   def extractElement(self,element,data):
      p1 = r' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
      data = re.sub(p1, "", str(data))
      pattern = r'<%s>((.|\n)*?)</%s>' %(element,element)
      return re.search(pattern,str(data),re.IGNORECASE).group(1).strip()


   #------------------------------------------------------------------------------------------------------#
   def GOTFgetRPM(self):                        # Get RPM info from Codes fwConfig SFWP
      getRPM = ''
      try:
         from Codes import fwConfig
         ServoCode = fwConfig[self.dut.driveattr['PART_NUM']]['SFWP']
         int(ServoCode.split('_')[0][-2:])
         getRPM = ServoCode.split('_')[0][-2:]
         objMsg.printMsg("GOTFgetRPM: getRPM=%s" % getRPM)
      except:
         objMsg.printMsg("GOTFgetRPM: Unable to get RPM from fwConfig SFWP. Traceback=%s" % traceback.format_exc())

      return getRPM

   #------------------------------------------------------------------------------------------------------#
   def buildGOTFTables(self, filePath = ''):                        # Parse GOTF criteria from xml document:
      if GOTF_DEBUG !=0:
         objMsg.printMsg("GOTF: Building GOTF tables from XML file")

      if testSwitch.GOTF_GRADING_TABLE_BY_RPM:
         TP.ProductName = self.GOTFgetRPM()

      if testSwitch.RECONFIG_RPM_CHK and self.dut.scanTime != 0 and self.dut.nextOper != 'PRE2':
         # fresh load from conveyor for all operations except PRE2
         getRPM = self.GOTFgetRPM()
         objMsg.printMsg("RECONFIG_RPM_CHK rpm=%s attr=%s" % (getRPM, self.dut.driveattr['SPINDLE_RPM']))
         if getRPM != self.dut.driveattr['SPINDLE_RPM'][:2]:
            ScrCmds.raiseException(14801, "Fail Drive Reconfig RPM check")

      criteria = {}                             # - Dictionary of grading criteria
      results = {}                              # - Dictionary of grading results
      grouplist = []
      self.BusGroupAll = {}
      fileName = 'GOTF_table.xml'
      cmfFileName = 'GOTF_table_%s.xml' % DriveAttributes.get('CMS_FAMILY', '')
      prodFileName = 'GOTF_table_%s.xml' % getattr(TP,'ProductName','')

      if filePath == '':
         #Try cms family version 1st
         filePath = os.path.join(ScrCmds.getSystemScriptsPath(), cmfFileName)

         if not os.path.exists(filePath):
            if DEBUG > 0:
               objMsg.printMsg("Failed to find CMS_FAMILY specific GOTF file %s" % cmfFileName)
                        
            #Try testparameter product version 2nd
            filePath = os.path.join(ScrCmds.getSystemScriptsPath(), prodFileName)   
            if not os.path.exists(filePath):
                if DEBUG > 0:
                    objMsg.printMsg("Failed to find Product specific GOTF file %s" % cmfFileName)
            
                #Try standard version last   
                filePath = os.path.join(ScrCmds.getSystemScriptsPath(), fileName)
         
         if not os.path.exists(filePath) and testSwitch.virtualRun == 1:
            filePath = os.path.join(os.getcwd() + os.sep + str(fileName))
            if not os.path.exists(filePath):
               filePath = os.path.join(os.getcwd(), '..', 'scripts',str(fileName))
               if not os.path.exists(filePath):
                  import cmEmul
                  filePath = os.path.join(os.getcwd(), '..', 'scripts',cmEmul.program, str(fileName))

      #objMsg.printMsg("GOTF_table filePath=%s" % filePath)
      objFile = open(filePath, 'r')             # - List of business group represented in xml criteria document
      data = self.extractElement('GradingCriteria',objFile.read())

      try:
         GradingRev = self.extractElement('GradingRev', data)
         if GradingRev.strip() == '':
            GradingRev = "NONE"  # default
      except:
         GradingRev = "NONE"  # default

      pat = r'<row>((.|\n)*?)</row>'
      rowlist = re.findall(pat,data,re.IGNORECASE)

      for row in rowlist:
         table = self.extractElement('criteria_table',row)
         bus_group = self.extractElement('business_Group',row)
         if bus_group == 'ALL':
            position = 99
            level =99
            if not self.BusGroupAll.has_key(table): # using gotf tools to pass/fail drive for a test
               self.BusGroupAll[table] = []

         else:
            position = int(self.extractElement('Grade_Position',row))
            level = self.extractElement('Grade_Level',row)
         if table not in criteria: criteria[table] = {'ColumnPosDict':{}, 'FilterColList':[]}
         if bus_group <> 'ALL': # dont add ALL to grouplist (gotf tools to p/f drive for a test)
            if bus_group not in grouplist: grouplist.append(bus_group)
         if position not in results: results[position] = {}
         if bus_group not in results[position]: results[position][bus_group] = [level,None]
         if bus_group not in criteria[table]:
            criteria[table][bus_group] = {}
            criteria[table][bus_group][position] = {level:
                                          {'Columns':{}
                                             }}
         else:
               if position not in criteria[table][bus_group]:
                  criteria[table][bus_group][position] ={level:
                                          {'Columns':{}
                                             }}

               else:
                  if level not in criteria[table][bus_group][position]:
                     criteria[table][bus_group][position][level] = {'Columns':{}
                                             }

         column = self.extractElement('criteria_column',row)
         if bus_group == 'ALL':
            self.BusGroupAll[table].append(column)
         
         
         fDict = {}

         for i in xrange(1, 5):
            item_key = "Filter" + str(i) + "_Item"
            op_key = "Filter" + str(i) + "_Op"
            value_key = "Filter" + str(i) + "_Value"
            try:
               fCol = self.extractElement(item_key, row)
               if not fDict.has_key(fCol):
                  fDict[fCol] = []
            except:
               fCol = ""
            if fCol != "":
               if fDict.has_key(fCol):
                  fDict[fCol].append([self.extractElement(op_key, row), self.extractElement(value_key, row)])
               if fCol not in criteria[table]['FilterColList']:
                  criteria[table]['FilterColList'].append(fCol)

         try:
            failCode = self.extractElement('Fail_Code',row)
         except:
            failCode = 'none'
                  
         if column not in criteria[table]['ColumnPosDict']:
            criteria[table]['ColumnPosDict'][column] = {bus_group:[(position, self.extractElement('criteria_op',row), fDict)]}
         else:
            bDuplicate = 0
            for item in criteria[table]['ColumnPosDict'][column]:
               if bus_group == item:
                  for subItem in criteria[table]['ColumnPosDict'][column][bus_group]:
                     if self.extractElement('criteria_op',row) in subItem and \
                        fDict in subItem:
                        bDuplicate = 1
                        break
                  if bDuplicate == 1: break
            if bDuplicate == 1:
               objMsg.printMsg('Table: %s, Column: %s, position: %s, bus_group: %s'%(table, column, position, bus_group))
               objMsg.printMsg("WARNING Duplicate criteria ignored")
               continue
            if bus_group not in criteria[table]['ColumnPosDict'][column]:
               criteria[table]['ColumnPosDict'][column][bus_group] = [(position, self.extractElement('criteria_op',row), fDict)]
            else:
               criteria[table]['ColumnPosDict'][column][bus_group].append((position, self.extractElement('criteria_op',row), fDict))
         
         if column not in criteria[table][bus_group][position][level]['Columns']:
            criteria[table][bus_group][position][level]['Columns'][column] = []
         else:
            objMsg.printMsg('Warning! Skipped GOTF_table.xml row %s' % `row`)

         criteria[table][bus_group][position][level]['Columns'][column].append((self.extractElement('criteria_op',row),
                                                               self.extractElement('criteria_value',row),
                                                               int(self.extractElement('Num_Violations',row)),
                                                               failCode,fDict)) 

      return criteria, grouplist, results, GradingRev


#---------------------------------------------------------------------------------------------------------#
class CGOTFtesttools:

   #------------------------------------------------------------------------------------------------------#
   def testString(self,operation):                       # Build string consisting of operator (<,>,= etc.) and test value
      testOpTable = [('LESS','<'),                       # List of comparison operator strings
                     ('GREATER','>'),
                     ('EQUAL','=')]
      teststring = ''
      for key in testOpTable:                            # Loop though list to assemble string of comparison operators
         if key[0] in operation[0]:
            teststring += key[1]
      if teststring == '=': teststring = '=='            # '=' not valid syntax - replace with '=='
      if not teststring: objMsg.printMsg("FAILED - no valid operations identified")
      teststring += str(operation[1])                    # Tack on value (as string) to compare against
      return teststring

   #------------------------------------------------------------------------------------------------------#
   def gotfTestOperation(self,values,operation,failed_meas_values =[]):         # Evaluate list of measured values against specified operation
      """ return violations and list of failed values for bus_group = ALL (gotf tools to p/f drive for a test) """
      violations = 0
      for value in values:
         violations += not eval(str(value)+operation)    # Evaluate measured value against specified criteria value
         if not eval(str(value)+operation):
            failed_meas_values.append(value)
      return violations                                  # Return count of 'violations'

   #------------------------------------------------------------------------------------------------------#
   def gotfTestColumn(self,table,bus_group,column,values,criteria, failed_meas_values=[]): # For the given table, group, column and values - evaluate against the criteria
      if GOTF_DEBUG != 0:
         objMsg.printMsg("GOTF: Testing Column: %s, Group: %s against logged values." % (column, bus_group))
      result = 1

      result *= self.gotfTestOperation(values,self.testString(criteria),failed_meas_values) <= criteria[2]
      return result

   #------------------------------------------------------------------------------------------------------#
   def syncManualToAutoBS(self, dut, curOper):
      """
      Synchronize from Manual Business Segment to Auto Business Segment.

      @type dut: object
      @param dut: Disk Under Test
      @type curOper: string
      @param curOper: current running operation

      1. Synchronization Manual to Auto BS only for Manual GOTF.
      2. Get Business Segment from Demand Table at PRE2; and BSNS_SEGMENTx
         at any state after PRE2.
      3. Remove failed Business Segment.
      4. Update all passed Business Segment back to BSNS_SEGMENTx.
      """
      # 1. Synchronization Manual to Auto BS only for Manual GOTF.
      if testSwitch.AutoCommit and not testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT: return
      
      from StateMachine import CLongAttr
      objMsg.printMsg("GOTF: Synchronize from Manual Business Segment to Auto Business Segment.")
      update_bs_flg = False
      # 2. Get Business Segment from Demand Table at PRE2; and BSNS_SEGMENTx
      #    at any state after PRE2
      if curOper == "PRE2":
         dut.gotfBsnsList = dut.DEMAND_TABLE[:]
         objMsg.printMsg("GOTF: Auto Business Segment from Demand Table is %s" % dut.gotfBsnsList)
         update_bs_flg = True
      else:
         dut.longattr_bg = CLongAttr().DecodeAttr(DriveAttributes)
         dut.gotfBsnsList = dut.longattr_bg.split("/")
         objMsg.printMsg("GOTF: Auto Business Segment from BSNS_SEGMENT2, BSNS_SEGMENT3, and ... is %s" % dut.gotfBsnsList)
      
      # 3. Remove failed Business Segment.
      for bs in dut.gotfBsnsList[:]:
         res = self.gotfTestGroup(bs)
         objMsg.printMsg("GOTF: Grading %6s result %s (1 = Pass, 0 = Fail)" % (bs, res))
         if res == 0:
            dut.gotfBsnsList.remove(bs)
            update_bs_flg = True
      
      # 4. Update all passed Business Segment back to BSNS_SEGMENTx.
      objMsg.printMsg("GOTF: Auto Business Segment after grading is %s" % dut.gotfBsnsList)
      if update_bs_flg:
         objMsg.printMsg("GOTF: Updating Business Segment into BSNS_SEGMENTx.")
         dut.longattr_bg = str.join('/', dut.gotfBsnsList)
         encdAutoBS = CLongAttr().EncodeAttr(dut.longattr_bg)
         objMsg.printMsg("GOTF: Encoded Auto Business Segment result is %s." % encdAutoBS)
         dut.driveattr.update(encdAutoBS)

#---------------------------------------------------------------------------------------------------------#
class CGOTFGrading(CGOTFxmlTools,CGOTFtesttools,CGOTFDBlogTools):
   """
   Data structures defined:
   self.gotfCriteria = { table: { busines group : {'Level':...},
                       {'Position': ...}
                       {'Columns' : { column : (operation,value,violations)}}}}
   self.gotfGroupList = ['group','group',...]
   self.gotfGradingResults = {position:{'group':[level,'grade'],'group':[],...}  (Note: grade = 'P', 'F' or None)
   """

   #------------------------------------------------------------------------------------------------------#
   def __init__(self, filePath = ''):
      """
      self.gotfCriteria = { table:
                              { business group :
                                  {position:
                                     {level:
                                          {'Columns' : { column : [(operation,value,violations) .....]}}}}
      """
      self.dut = objDut
      self.gotfCriteria, self.gotfGroupList, self.gotfGradingResults, self.GradingRev = self.buildGOTFTables(filePath = filePath) # Parse criteria
      if GOTF_DEBUG != 0:
         objMsg.printMsg("gotfCriteria %s" % str(self.gotfCriteria))
         objMsg.printMsg("gotfGroupList %s" % str(self.gotfGroupList))
         objMsg.printMsg("gotfGradingResults %s" % str(self.gotfGradingResults))
         objMsg.printMsg("BusGroupAll %s" % str(self.BusGroupAll))
         objMsg.printMsg("GradingRev %s" % self.GradingRev)

      self.gotfTableSummary = {}
      self.BestScore = ['X'] * 32

   def GetBestScore(self, pos, lev):
      try:
         OldScore = int(self.BestScore[pos], 16)
         NewScore = int(lev, 16)
         if NewScore > OldScore:
            self.BestScore[pos] = lev
      except:
         self.BestScore[pos] = lev

   def PrnLog(self, res, item, table, column, bg, pos, lev):
      try:
         if res != None:
            msg = "%s, %s, %s, %s, %s, [" % (table, column, bg, pos, lev)
            for i in item:
               for j in item[i]:
                  msg = msg + str(i) + self.testString(j) + ","

            objMsg.printMsg("%s], %s" % (msg, res))
      except:
         objMsg.printMsg("Unable to print P_GOTF_TABLE_SUMMARY update. Traceback=%s" % traceback.format_exc())

   #------------------------------------------------------------------------------------------------------#
   def GradeTable(self,table):                  # Evaluate all data for given 'table' and update grading table
      if GOTF_DEBUG !=0:
         objMsg.printMsg("GOTF: Grading table: %s" % str(table))
      tabledata, filterdata = self.gotfGetColVal(table)
      failed_meas_values = [] # gotf tools to p/f drive for a test
      if tabledata <> {}:
        for column in tabledata:
            
            if table in self.BusGroupAll.keys(): #using gotf tools to pass/fail drive for a test
               if column in self.BusGroupAll[table]:
                  if not self.gotfGradingResults[99]['ALL'][1] == 'F': #dont test column if already failing grade for this BG and posn
                     if column in self.gotfCriteria[table]['ALL'][99][99]['Columns']:
                        for criteria in self.gotfCriteria[table]['ALL'][99][99]['Columns'][column]:
                           if self.gotfGradingResults[99]['ALL'][1] == 'F': break
                           f_tabledata = self.getFilteredValues(table, 'ALL', 99, 99, column, tabledata[column], filterdata, criteria[4])
                           if f_tabledata == []:  #IF NO DATA IS FOUND AFTER FILTERING DO NOT ASSIGN PASS/FAIL CRITERIA
                               break

                           if self.gotfTestColumn(table,'ALL',column,f_tabledata, criteria, failed_meas_values) and self.gotfGradingResults[99]['ALL'][1] != 'F':
                              self.gotfGradingResults[99]['ALL'][1] = 'P'
                           else: # grab failing info for raiseException call
                              self.gotfGradingResults[99]['ALL'][1] = 'F'
                              self.failtable = table
                              self.failcolumn = column
                              self.failcriteria_op = criteria[0]
                              self.failcriteria_val = criteria[1]
                              self.failcriteria_vio = criteria[2]
                              self.failcode = criteria[3]
                              self.failcriteria_filterDict = criteria[4]
                              self.failed_meas_values = failed_meas_values # blm
            #else: # normal GOTF block
            for bg in self.gotfGroupList:
               if bg in self.gotfCriteria[table]:
                  for pos in self.gotfCriteria[table][bg]:
                     for lev in self.gotfCriteria[table][bg][pos]:
                        if column in self.gotfCriteria[table][bg][pos][lev]['Columns']:
                           if not self.gotfGradingResults[pos][bg][1] == 'F': #dont test column if already failing grade for this BG and posn
                              for criteria in self.gotfCriteria[table][bg][pos][lev]['Columns'][column]:
                                 f_tabledata = self.getFilteredValues(table,bg, pos, lev, column, tabledata[column], filterdata, criteria[4])
                                 if f_tabledata == []:  #IF NO DATA IS FOUND AFTER FILTERING DO NOT ASSIGN PASS/FAIL CRITERIA
                                    break

                                 if self.gotfTestColumn(table,bg,column,f_tabledata, criteria) and self.gotfGradingResults[pos][bg][1] != 'F':
                                    self.gotfGradingResults[pos][bg][1] = 'P'
                                    self.GetBestScore(pos, lev)
                                 else:
                                    self.gotfGradingResults[pos][bg][1] = 'F'

                                 self.PrnLog(self.gotfGradingResults[pos][bg][1], criteria[4], table, column + self.testString(criteria), bg, pos, lev)

                        else:
                           #column not in BG
                           if column in self.gotfCriteria[table]['ColumnPosDict']:
                              if bg in self.gotfCriteria[table]['ColumnPosDict'][column]:
                                 for item in self.gotfCriteria[table]['ColumnPosDict'][column][bg]:
                                    tmpPos = item[0]
                                    if tmpPos == 99: bg = 'ALL'
                                    #if self.gotfGradingResults[tmpPos][bg][1] == None:
                                    #   self.gotfGradingResults[tmpPos][bg] = [0, 'P']

               else:
                  #Dont Care criteria for this BG
                  if column in self.gotfCriteria[table]['ColumnPosDict']:
                     if bg in self.gotfCriteria[table]['ColumnPosDict'][column]:
                        for item in self.gotfCriteria[table]['ColumnPosDict'][column][bg]:
                           pos = item[0]
                           if pos == 99:  bg = 'ALL'
                           #if self.gotfGradingResults[pos][bg][1] == None:
                              #self.gotfGradingResults[pos][bg] = [0, 'P']

   #------------------------------------------------------------------------------------------------------#
   def getFilteredValues(self, table, BG, pos, lev, column, coldata, filterdata, filter_criteria):

      fdata = []
      fdata.extend(coldata)
      if GOTF_DEBUG != 0:
         objMsg.printMsg("table %s BG %s pos %s lev %s" % (table, BG, pos, lev))
         objMsg.printMsg("gotfcriteria %s" % str(self.gotfCriteria[table][BG][pos][lev]))
      if filter_criteria == {}:
         if GOTF_DEBUG != 0:
            objMsg.printMsg("fdata 1 %s" % str(fdata))
         return fdata

      pop_idx_lst = []
      for filter_col in filter_criteria.keys():

         if len(coldata) != len(filterdata[filter_col]):
            if GOTF_DEBUG != 0:
               objMsg.printMsg("coldata %s" % str(coldata))
               objMsg.printMsg("filter_col %s" % str(filter_col))
               objMsg.printMsg("fdata 2 %s" % str(fdata))
            return fdata
         fd_key = 0
         pop_key = 0
         if GOTF_DEBUG != 0:
            objMsg.printMsg("filter_col %s" % str(filter_col))
            objMsg.printMsg("filterdata[filter_col] %s" % str(filterdata[filter_col]))
         max_val = None   
         for operation in filter_criteria[filter_col]:
            if operation[0] == 'MAX':
               max_val = max(filterdata[filter_col])

         for val in filterdata[filter_col]:
            if GOTF_DEBUG != 0:
               objMsg.printMsg("fd_key %s pop_idx_lst %s" % (str(fd_key), str(pop_idx_lst)))
            if not (fd_key in pop_idx_lst):
               if GOTF_DEBUG != 0:
                  objMsg.printMsg("GOTF: Testing Column: %s, Group: %s against logged values." % (filter_col, BG))
               result = 1

               for operation in filter_criteria[filter_col]:
                  if operation[0] == 'MAX':
                     continue
                  try:
                     #handles all numeric data even in string format
                     operation_str = self.testString(operation)
                     result *= eval(str(val) + operation_str)
                     if GOTF_DEBUG != 0:
                        objMsg.printMsg("val %s operation_str %s calc %s result %s" % (str(val), str(operation_str), str(eval(str(val) + operation_str)), str(result)))
                  except:
                     if val.__class__ == str and operation[0] == 'EQUAL TO':
                     #exclusively handles string comparisons
                        result *= not(cmp(val, str(operation[1])))
                        if GOTF_DEBUG != 0:
                           objMsg.printMsg("val str %s operation %s result %s" % (str(val), str(operation), str(result)))
                     else:
                        objMsg.printMsg('Unable to resolve filter criteria %s in table %s val type %s' % (str(filter_col), str(table), str(val.__class__)))

               if not result:
                  fdata.pop(fd_key-pop_key)
                  pop_idx_lst.append(fd_key)
                  pop_key += 1
                  if GOTF_DEBUG != 0:
                     objMsg.printMsg("pop_idx_lst %s" % str(pop_idx_lst))
               elif str(val) == "_NOT_FOUND_":
                  fdata.pop(fd_key-pop_key)
                  pop_idx_lst.append(fd_key)
                  pop_key += 1
                  if GOTF_DEBUG != 0:
                     objMsg.printMsg("Filter item not found %s" % str(filter_criteria))
               elif max_val != None and val < max_val:
                  fdata.pop(fd_key-pop_key)
                  pop_idx_lst.append(fd_key)
                  pop_key += 1
                  if GOTF_DEBUG != 0:
                     objMsg.printMsg("pop_idx_lst %s" % str(pop_idx_lst))
            else:
               pop_key +=1
            fd_key += 1
            if GOTF_DEBUG != 0:
               objMsg.printMsg("fdata %s" % str(fdata))
                
      return fdata


   #------------------------------------------------------------------------------------------------------#
   def gotfGradeAll(self):                               # Build grading Table and populate with all available scoring data
      if GOTF_DEBUG != 0:
         objMsg.printMsg("GOTF: Grading all available results.")
      if testSwitch.FE_0156504_357260_P_RAISE_GOTF_FAILURE_THROUGH_FAIL_PROC:
         self.gotfGradingResults[99]['ALL'][1] = 'P'           # Clear out existing 'ALL' failure - allow for retry attempt.
      for table in self.gotfCriteria:
         self.GradeTable(table)

      #objMsg.printDblogBin(self.dut.dblData.Tables('P_GOTF_TABLE_SUMMARY'))

   #------------------------------------------------------------------------------------------------------#
   def gotfGradeState(self,state):                       # Re-score all tables referenced by 'state'
      if GOTF_DEBUG != 0:
         objMsg.printMsg("GOTF: Grading all tables for state: %s" % str(state))
      
      #since deltable will modify the stateDBLogInfo list then we need to create a copy of the list
      tblList = list(set(self.dut.stateDBLogInfo.get(state,[]))) #create a unique list just in-case there are duplicates (causes exception)
      
      if testSwitch.FE_0156504_357260_P_RAISE_GOTF_FAILURE_THROUGH_FAIL_PROC:
         self.gotfGradingResults[99]['ALL'][1] = 'P'           # Clear out existing 'ALL' failure - allow for retry attempt.
      for table in tblList:
         self.GradeTable(table)
         
         #Remove ram data since we are done with it
         try:
            if not table in processTableOverrides: #Don't delete RAM tables defined for process
               self.dut.dblData.delTable(table)
         except:
            pass
         
   #------------------------------------------------------------------------------------------------------#
   def gotfCustScore(self,group):
      score = 'X'*32                                     # Start with 'empty' customer score
      for position in self.gotfGradingResults:
         if position <> 99: # no score for Business_Group = ALL case
            if group in self.gotfGradingResults[position]:
               score = self.concat(score[:position],self.gotfGradingResults[position][group][0], score[position+1:])
            else:
               #objMsg.printMsg("WARNING: No score for position %s for group %s. Defaults to score 0s" % (position, group))
               score = self.concat(score[:position],'N',score[position+1:])
      score = score.rstrip('X')
      score = score.replace('N', 'X')
               
      return score

   #------------------------------------------------------------------------------------------------------#
   def concat(self,*args):
      """
      Return the concatenated str of all objects in args. If list entered args = args[0]
      """
      if len(args) == 1:
         args = args[0]
      return ''.join(map(str,args))
   
   def gotfDriveScore(self,group):
      score = self.dut.driveattr.get('DRIVE_SCORE','X'*32)
      #objMsg.printMsg("self.dut.driveattr[drive_score] %s" % str(self.dut.driveattr['DRIVE_SCORE']))
      if score == 'NONE':
         score = 'X'*32
      
      for position in self.gotfGradingResults:
         if position <> 99: # no score for Business_Group = ALL case
            if self.gotfGradingResults[position].get(group,[False,False])[1]:
               if self.gotfGradingResults[position][group][1] == 'P':
                  if self.dut.driveattr['DRIVE_SCORE'] != "NONE":
                     if self.dut.driveattr['DRIVE_SCORE'][position] == '0':
                        score = self.concat(score[:position], '0', score[position+1:])
                     else:
                        score = self.concat(score[:position],self.gotfGradingResults[position][group][0], score[position+1:])
                        
                     objMsg.printMsg("score %s" % score)   
                  else:
                     score = self.concat(score[:position],self.gotfGradingResults[position][group][0], score[position+1:])
               elif self.gotfGradingResults[position][group][1] == 'F':
                  objMsg.printMsg("WARNING: Drive failed for position %s for group %s." % (position, group))
                  score = self.concat(score[:position], '0', score[position+1:])
            else:
               if score[position] == 'X':
                  score = self.concat(score[:position], 'N', score[position+1:])
                  #objMsg.printMsg("WARNING: No score for position %s for group %s." % (position, group))

      score = score.rstrip('X')
      score = score.replace('N', 'X')
      return score

   #------------------------------------------------------------------------------------------------------#
   def gotfResetDriveScore(self,):
       """
       Reset GOTF drive score to all X's (used for state table transitions to beginning of process like depopRestart)
       """
       self.dut.driveattr['DRIVE_SCORE'] = 'NONE'
       for position in self.gotfGradingResults:
         for BG in self.gotfGradingResults[position]:
            self.gotfGradingResults[position][BG][1] = None

       self.dut.driveattr['DRIVE_SCORE'] = self.gotfDriveScore(self.dut.BG)
           
           
   def gotfTestGroup(self,group):                        # For given group, fail (return 0) if failed for any test
      result = 1
      for position in self.gotfGradingResults:
         if self.gotfGradingResults[position].has_key(group):
            result *= not(self.gotfGradingResults[position][group][1] == 'F')
      if GOTF_DEBUG !=0:
         objMsg.printMsg("GOTF: Grading group: %s, Result: %s (1 = Pass, 0 = Fail)" % (group, result))
      return result
   
   #------------------------------------------------------------------------------------------------------#
   def gotfCompareScores(self, driveScore, custScore):
      """
      Cross check a drive's score against a customer score allowing X in customer score to be an ignore in drive score.
      *Used in post cmt score verification
      """
      
      for pos,score in enumerate(custScore):
         if score != 'X': #Bypass checking customer ignore bits
            if not (driveScore[pos] == score): #If driveScore != custScore we failed scoring
               return False

      return True

   def gotfDowngradePos(self,group):                        # For given group, fail (return 0) if failed for any test
      for position in self.gotfGradingResults:
         if self.gotfGradingResults[position].has_key(group) and self.gotfGradingResults[position][group][1] == 'F':
            break
      return position
   
   def gotfUpdateDblTbl(self):
      
      
      for table in self.gotfCriteria:
         for bg in self.gotfCriteria[table]:
            if bg != 'ColumnPosDict' and bg != 'FilterColList':
               for pos in self.gotfCriteria[table][bg]:
         
                  for level in self.gotfCriteria[table][bg][pos]:
                     for col in self.gotfCriteria[table][bg][pos][level]['Columns'].keys():
                        try:
                           fcols = str(self.gotfCriteria[table][bg][pos][level]['Columns'][col][4].keys())
                        except:
                           fcols = 'NONE'
                        if self.gotfGradingResults[pos][bg][1] != None and bg != 'ALL':
                           curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(800)
                           self.dut.dblData.Tables('P_GOTF_TABLE_SUMMARY').addRecord(
                              {
                              'SPC_ID'           :  '1',
                              'OCCURRENCE'       :  occurrence,
                              'SEQ'              :  curSeq,
                              'TEST_SEQ_EVENT'   :  testSeqEvent,
                              'DBLOG_TABLE'      :  table,
                              'DBLOG_COLUMN'     :  col,
                              'DBLOG_FILTER_COL' :  fcols,
                              'DBLOG_POSITION'   :  pos,
                              'BUSINESS_GROUP'   :  bg,
                              'PF_RESULT'        :  self.gotfGradingResults[pos][bg][1],
                              })
   
class CDblFile:
   def __init__(self):
      self.gotf_file = 'gotfDbl'
      from FSO import CFSO
      self.oFSO = CFSO()
      self.FIRST = 0
      self.dblFilePath = os.path.join(ScrCmds.getSystemResultsPath(), self.oFSO.getFofFileName(0), self.gotf_file)
      #objMsg.printMsg("self.dblFilePath %s" % str(self.dblFilePath))

   def writeDblToFile(self, tableName):
      self.dblFile = GenericResultsFile(self.gotf_file)

      if self.FIRST == 0:
         self.dblFile.open('a')
         self.dblFile.write("<parametric_dblog>"+str(objDut.dblData.Tables(tableName)))
         self.FIRST = 1
      self.dblFile.open('a')
      self.dblFile.write(str(objDut.dblData.Tables(tableName)))
      self.dblFile.close()
      self.dblFile.open('rb')
      data = self.dblFile.read()
      #objMsg.printMsg("data %s" % str(data))

   def saveDbltoDisc(self):
      record = objSimArea['GOTF_DBLOG']
      #Write data to drive SIM
      self.dblFile.close()
      self.dblFile.open('a')
      self.dblFile.write("</parametric_dblog>")
      self.dblFile.close()
      objMsg.printMsg("Saving GOTF File to drive SIM.  File Path: %s" % self.dblFilePath, objMsg.CMessLvl.DEBUG)
      self.oFSO.saveResultsFileToDrive(1, self.dblFilePath, 0, record, 1)

      #Verify data on drive SIM
      if not testSwitch.virtualRun:
         path = self.oFSO.retrieveHDResultsFile(record)
         file = open(path,'rb')
         try:
            file.seek(0,2)  # Seek to the end
            fileLength = file.tell()
         finally:
            file.close()
         objMsg.printMsg("Re-Read of GOTF SIM File %s had size %d" % (record.name,fileLength), objMsg.CMessLvl.DEBUG)
         if fileLength == 0:
            ScrCmds.raiseException(11044, "GOTF SIM readback of 0 size.")

   def readGOTFdblFile(self, dbl):
      if self.dut.currentState == 'INIT' or (self.dut.nextOper == 'PRE2' and self.dut.systemAreaPrepared == 0):
         return
      record = objSimArea['GOTF_DBLOG']
      path = None
      if not testSwitch.virtualRun:
         path = self.oFSO.retrieveHDResultsFile(record)
      else:
         path = self.dblFilePath

      #objMsg.printMsg("readGOTFdblFile path %s" % str(path))
      import loadXML
      loadXML.loadGemXML(path, dbl)

#---------------------------------------------------------------------------------------------------------#
