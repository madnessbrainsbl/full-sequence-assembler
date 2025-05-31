# --------------------------------------------------------------------------------------- #
#                                                                                         #
#                                   Seagate Confidential                                  #
#                                                                                         #
# --------------------------------------------------------------------------------------- #

# ******************************************************************************
#
# VCS Information:
#                 $File: //depot/TCO/DEX/rptextractors.py $
#                 $Revision: #2 $
#                 $Change: 319143 $
#                 $Author: rebecca.r.hepper $
#                 $DateTime: 2010/12/16 07:36:23 $
#
# ******************************************************************************

from parametricextractors import *

currentFileObject = ""
# Lookup dictionary of file objects and table names
fileObjects = {}

class RptParametricFirstBlock(ParametricFirstBlock):   # 11000 block code; 1st block of data; contains table code & data

  def __call__(self,resultsData,testNumber,collectParametric,counters,resultsHandlers,userOptions,*args,**kwargs):
    
    global currentFileObject
    global fileObjects
    
    testNumList = userOptions.get("testNumList",[])
    spcIdList = userOptions.get("spcIdList",[])
    outputFilesByTable = userOptions.get("outputFilesByTable",0)

    # If list is empty collect parametric data on all tests; otherwise only collect data on the tests in the list
    if not testNumList or testNumber in testNumList:  
      # If the list of spc ids is empty collect data on all spc ids; otherwise only collect data if the spc id is in the list
      if not spcIdList or str(collectParametric) in spcIdList:  
        resultsData = self.handleTableData(resultsData,testNumber,collectParametric,counters,resultsHandlers,userOptions)
        
        # If the user wants a separate output file for each parametric table
        if outputFilesByTable:
          # Clear file object in case errors occur before it gets reset - this would cause data to be written to the wrong file
          currentFileObject = ""
          err = 0
          try:
            # Data formatted by parametricextractors will contain table name & type, column names and one row of table data
            tableName,columnNames,tableData = resultsData.split("\n")
            # Data looks like:  TABLE=P001_TIME_TO_READY TYPE=S  need to split out the actual table name
            tableName = tableName.split(" ")[0]
            tableName = tableName.split("=")[1].lower()
          except:
            # Do not throw error.  If the col types in the dictionary is empty and the parseViewerTables user option is not set,
            # the data returned from handleTableData() will not be as expected so the split will fail.  In this case, we do not 
            # want to write that data to sum files so just set the err.
            err = 1
           
          if not err:
            fileExistance = resultsHandlers.checkFileExistance(tableName) 
              
            # Multiple file states to handle:
            #  1) File does not exist - new instance of a table so open the file
            #  2) File exists, is in the file object lookup dictionary and is open - file already opened during parsing of current results file, get file object from dictionary
            #  3) File exists, is in the file object lookup dictionary and is closed - do not think this state should occur, but check anyways, open the file 
            #  4) File exists, is not in the file object lookup dictionary - previous results file created the output file; open the file           
            
            #  All files are closed when finished parsing a results file
            
            openFile = 0
            if not fileExistance:   
              openFile = 1
            # File does exist
            else:  
              try:
                # Lookup works if file was opened for current results file; we now have the file object
                currentFileObject = fileObjects[tableName]   
              except:
                # File exists but we don't have it in the lookup dictionary so it was created by a different results file
                openFile = 1
              else:
                # If file is currently closed, open it
                if fileObjects[tableName].closed:  
                  openFile = 1  
            
            if openFile:  
              try:
                # Open file to get a file object and add it to the lookup dictionary
                currentFileObject = resultsHandlers.openFile(tableName)
                fileObjects[tableName] = currentFileObject
              except:
                TraceMessage("ERROR rptextractors.py block 11000; Unable to open output file for table %s " % tableName) 
                traceback.print_exc()
                err = 1

            # If the file already exists, do not write column names because they are already in the file
            if not fileExistance and not err:
              try:
                # Add serial number to the column name string
                resultsHandlers.writeFile(currentFileObject,"%s" % (columnNames))
              except:
                TraceMessage("ERROR rptextractors.py block 11000; Unable to write column names to output file for table %s " % tableName) 
                traceback.print_exc()
            
            # Write table data
            if not err:
              try:
                resultsHandlers.writeFile(currentFileObject,"%s" % (tableData))
              except:
                TraceMessage("ERROR rptextractors.py block 11000; Unable to write data to output file for table %s " % tableName) 
                traceback.print_exc()
        
    return resultsData  


class RptParametricSubBlock(ParametricSubBlock):   # 11002 block code; contains firmware test data

  def __call__(self,resultsData,testNumber,collectParametric,counters,resultsHandlers,userOptions,*args,**kwargs):
    
    global currentFileObject
    
    testNumList = userOptions.get("testNumList",[])
    spcIdList = userOptions.get("spcIdList",[])
    outputFilesByTable = userOptions.get("outputFilesByTable",0)
    
    # If list is empty collect parametric data on all tests; otherwise only collect data on the tests in the list 
    if not testNumList or testNumber in testNumList: 
      # If the list of spc ids is empty collect data on all spc ids; otherwise only collect data if the spc id is in the list
      if not spcIdList or str(collectParametric) in spcIdList:
        resultsData = self.handleData(resultsData,testNumber,collectParametric,counters,resultsHandlers,userOptions)
        
        # If user wants an output file for each table
        if outputFilesByTable and currentFileObject:
          try:
            # Write to the file that block 11000 set
            resultsHandlers.writeFile(currentFileObject,"%s" % (resultsData))
          except:
            TraceMessage("ERROR  rptextractors.py block 11002; Unable to write data to output file for test %s" % testNumber)  
            traceback.print_exc() 
        
    return resultsData  
