# --------------------------------------------------------------------------------------- #
#                                                                                         #
#                                   Seagate Confidential                                  #
#                                                                                         #
# --------------------------------------------------------------------------------------- #

# ******************************************************************************
#
# VCS Information:
#                 $File: //depot/TCO/DEX/parametricextractors.py $
#                 $Revision: #6 $
#                 $Change: 367517 $
#                 $Author: rebecca.r.hepper $
#                 $DateTime: 2011/06/22 09:00:45 $
#
# ******************************************************************************
import types,struct,traceback,string,os
from tabledictionary import *

# If this file exists, only send tables & spc_ids listed in this file to Oracle; the spc_id from the script is meaningless
try:
  from tablematrix import *
except:
  tableMatrix = {}

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# GLOBALS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
seqNum = 0            # Sequence number
currentTableCode = 0  # Table code extracted from binary results file
skipParsing = 0       # Flag set if tablematrix file is present and the current table code & spc_id is not in the file
colCount = 0


# Define TraceMessage if we're not running in the Gemini script environment.
try:
  TraceMessage
except:
  def TraceMessage(msg):
    print msg


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def alignData(tableType,resultsData,headerData):

  # Scalar parametric table also known as a simple table
  if tableType == "S":
    resultsData = "%s,%s" % (headerData,resultsData)

  # Vector parametric table also known as a 1 dimensional table
  elif tableType == "V":
    dim1,data = resultsData.split(",",1)  # Split once
    resultsData = "%s,%s,%s" % (dim1,headerData,data)

  # Matrix parametric table also known as a 2 dimensional table
  elif tableType == "M":
    dim1,dim2,data = resultsData.split(",",2)  # Split twice
    resultsData = "%s,%s,%s,%s" % (dim1,dim2,headerData,data)

  else:
    TraceMessage("ERROR parametricextractors.py:  Invalid table type %s" % tableType)
    # TODO - what should I do?  Write the data anyway assuming simple?

  return resultsData


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def maskData(resultsData,colMasks,userOptions):
  err = 0
  msg = "OK"
  try:
    # Already know some data is parametric data since there were col types in the dictionary
    # In masks,  parametric data is a 1 & viewer data is a 0; if there are 0's data must be masked
    if 0 in colMasks:

      # Turn the comma seperated data into a list
      resultsDataList = resultsData .split(",")

      # Check if there are less masks than data (i.e test data or col names)
      # There can be more masks than data if using a new tabledictionary.py with new columns on a table and old 
      # firmware which does not yet have those new columns.
      if len(colMasks) < len(resultsDataList):
        msg = "Not enough masks: %s available to mask the data: %s" % (len(colMasks),len(resultsDataList))
        err = 1

      if not err:

        finalList = []

        # If the mask flag from dictionary is set, add the data to the final list or if the DEXRPT option to collect data
        # on the tables meant for the text file (viewer)is set add it to the list
        for i in range(len(resultsDataList)):
          if colMasks[i] == 1 or userOptions.get("parseViewerTables",0):
            finalList.append(resultsDataList[i])

        # Turn the list back into a comma separated string
        resultsData  = string.join(finalList,",")
  except:
    err = 1
    msg = "Error masking data"
  return(err,msg,resultsData)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def formatColumnNames(resultsData,testNumber,tableType,colMasks,userOptions):
  # Column names are a comma separated list.  The list can contain a mixture of column names that are meant for Oracle and
  # column names meant only for the text file.  Col names must be masked according to the mask flag in the dictionary then
  # the header column names are added.
  global colCount
  err = 0
  msg = "OK"
  colCount = 0

  try:
    err, msg, resultsData = maskData(resultsData,colMasks,userOptions)

    # Even if an error occurred while masking the data, try adding the header columns
    # Special case:  parametric table P_EVENT_SUMMARY which does not have an SPC_ID column
    if testNumber == 9999:
      headerCols = "OCCURRENCE,SEQ,TEST_SEQ_EVENT"
    else:
      # Standard ESG header columns that follow the table dimensions (if any); these column names are not in the imported dictionary
      headerCols = "SPC_ID,OCCURRENCE,SEQ,TEST_SEQ_EVENT"

    # Put data in correct order based on table type
    resultsData = alignData(tableType,resultsData,headerCols)
    colCount = list(colMasks).count(1) + len(headerCols.split(","))

  except:
    err = 1
    msg = "Error masking column names"

  return(err,msg,resultsData)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def formatTableData(resultsData,counters,testNumber,tableType,colMasks,collectParametric,seqNum,userOptions):
  # Data comes in as a comma separated list of only firmware data.  The firmware data can be only parametric data or both parametric & viewer data.
  # If the data is a mixture of parametric & viewer data, it is turned into a list so it can be compared against the masks in the dictionary
  # Based on table type, it is aligned with dimensional header data followed by firmware data.

  err = 0
  msg = "OK"

  try:
    err, msg, resultsData = maskData(resultsData,colMasks,userOptions)
    # Even if an error occurred while masking the data, try adding the header columns

    # Unpack test header and seq counters
    scriptOccurrence,seqOccurrence,testSeqEventDict,failureHeader = counters

    # First test in a seq will have an empty dictionary because counters are incremented after test is processed
    try:
      testSeqEvent = testSeqEventDict[testNumber]
    except:
      testSeqEvent = 1

    # Find the seq number
    if type(seqNum) is types.TupleType:
      seqNum = seqNum[0]

    # Special case:  parametric table P_EVENT_SUMMARY which does not have an SPC_ID column
    if testNumber == 9999:
      headerData = "%s,%s,%s" % (seqOccurrence,seqNum,testSeqEvent)
    else:
      # Data for header columns does not come from firmware; this tool has to fill in the information
      headerData = "%s,%s,%s,%s" % (collectParametric,seqOccurrence,seqNum,testSeqEvent)

    # Put data in correct order based on table type
    resultsData = alignData(tableType,resultsData,headerData)

  except:
    err = 1
    msg = "Error masking firmware data"

  return(err,msg,resultsData)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class StartSeq:

  def __call__(self,resultsData,*args,**kwargs):
    global seqNum
    format = ">h"
    size = struct.calcsize(format)
    seqNum = struct.unpack(format,resultsData[0:size])
    return seqNum


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ParametricFirstBlock:     # 11000 block code; 1st block of data; contains table code & data

  def __call__(self,resultsData,testNumber,collectParametric,counters,resultsHandlers,userOptions,*args,**kwargs):
    # Only collect parametric data if the spc_id is set in the user script or if user passes option to ignore spc_id
    # Or collect data if the tablematrix file is present and DEX is being run
    if (str(collectParametric) != "None" and str(collectParametric) != "-1") or userOptions.get("ignoreSpcId",0) or (tableMatrix and not userOptions.get("dexrpt",0)):
      return(self.handleTableData(resultsData,testNumber,collectParametric,counters,resultsHandlers,userOptions))


  def handleTableData(self,resultsData,testNumber,collectParametric,counters,resultsHandlers,userOptions,):
    global seqNum
    global tableType
    global currentTableCode
    global skipParsing
    global colCount

    runDexRpt = userOptions.get("dexrpt",0)

    # Set up return value in case exceptions occur
    formattedData = resultsData

    # Special case:  parametric table P_EVENT_SUMMARY which does not have an SPC_ID column
    if testNumber == 9999:
      headerCols = "OCCURRENCE,SEQ,TEST_SEQ_EVENT"
    else:
      # Standard ESG header columns that follow the table dimensions (if any); these column names are not in the imported dictionary
      headerCols = "SPC_ID,OCCURRENCE,SEQ,TEST_SEQ_EVENT"

    try:
      # Grab the table code; value is a tuple so just grab the first part
      currentTableCode = struct.unpack("H",resultsData[:2])[0]

      skipParsing = 0
      if tableMatrix and not runDexRpt and not testNumber == 9999:
        # If the tableCode and the spc_id is not in the tablematrix, skip processing this data
        if currentTableCode in tableMatrix.keys():
          if not (str(collectParametric) in str(tableMatrix[currentTableCode][1])):
            skipParsing = 1
        else:
          skipParsing = 1

      # DEX users can pass in a dictionary of table codes & spc_ids that they want to skip writing to the XML file
      if userOptions.get('skipParametricTables',{}):
        if currentTableCode in userOptions['skipParametricTables']:
          if str(collectParametric) in str(userOptions['skipParametricTables'][currentTableCode]):
            skipParsing = 1
      
      if not skipParsing:
        # If dictionary has col types, the table is meant for Oracle; if col types is an empty string, the table is for the text file only
        try:
          colTypes = tableHeaders[currentTableCode][3]
        except:
          TraceMessage("ERROR parametricextractors.py block 11000;  Can not find col types for table code %s" % currentTableCode)
          colTypes = ""

        if (not colTypes) and userOptions.get("parseAllTables",0):
          try:
            colMasks = tableHeaders[currentTableCode][2]
            colTypes = ['X' for x in colMasks]
            colTypes = ','.join(colTypes)
          except:
            pass

        # DEXRPT has an option to parse the tables meant for the text file (viewer), if set, parse even though the col types field is empty
        if colTypes or userOptions.get("parseViewerTables",0):

          # Per FIS spec, table name line must look like:  TABLE=T175_ZAP_SUMRY TYPE=V
          # Words 'TABLE=' and 'TYPE=' do not come across from firmware; this script adds them
          try:
            tableName = tableHeaders[currentTableCode][0]
            tableType = tableHeaders[currentTableCode][5]
            formattedData = "TABLE=%s TYPE=%s" % (tableName,tableType)
          except:
            TraceMessage("ERROR parametricextractors.py block 11000;  Can not find table name or type for table code %s" % currentTableCode)
          else:
            # Special case:  process scripts write testNumber of 9999 for parametric table P_EVENT_SUMMARY
            # Data for this table written at a later point as one of the last things DEX does
            if testNumber != 9999:
              resultsHandlers.writeToParametricFile(formattedData)

            # Based on table code; grab list of column names & masks from imported dictionary
            try:
              columns = tableHeaders[currentTableCode][1]
              colMasks = tableHeaders[currentTableCode][2]
              if userOptions.get("parseAllTables",0):
                colMasks = [1 for x in colMasks]
                colMasks = tuple(colMasks)
            except:
              TraceMessage("ERROR parametricextractors.py block 11000;  Can not find col names or masks for table code %s" % currentTableCode)
            else:
              # Mask off the column names according to the mask found in the import dictionary
              err,msg,columnData = formatColumnNames(columns,testNumber,tableType,colMasks,userOptions)
              if err:
                TraceMessage("ERROR parametricextractors.py block 11000;  %s for table code %s" % (msg,currentTableCode))

              # If running DEXRPT add column names to the beginning of the data
              if runDexRpt:
                columnData = "SERIALNUM,RESULTS_FILENAME," + columnData

              if testNumber != 9999:
                resultsHandlers.writeToParametricFile(columnData)
              formattedData += "\n%s" % columnData

            try:
              # If DEXRPT is being run, do not write col types to the output file
              if not runDexRpt:
                # Based on table code; grab column types from imported dictionary
                #colTypes = tableHeaders[currentTableCode][3]

                # Special case:  parametric table P_EVENT_SUMMARY which does not have an SPC_ID column
                if testNumber == 9999:
                  headerTypes = "N,N,N"
                else:
                  # Column types for standard ESG header columns that follow the table dimensions (if any)
                  headerTypes = "V,N,N,N"

                # Put column types in correct order:  table dimensions types (if any); ESG header column types; types for test data
                colTypes = alignData(tableType,colTypes,headerTypes)
                if testNumber != 9999:
                  resultsHandlers.writeToParametricFile(colTypes)
                formattedData += "\n%s" % colTypes
            except:
              TraceMessage("ERROR parametricextractors.py block 11000;  Can not find col types for table code %s" % currentTableCode)


        if colTypes or userOptions.get("parseViewerTables",0) :
          try:
            err,msg,resultsData = formatTableData(resultsData[2:],counters,testNumber,tableType,colMasks,collectParametric,seqNum,userOptions)
            if err:
              TraceMessage("ERROR parametricextractors.py block 11000;  %s for table code %s" % (msg,currentTableCode))

            # If running DEXRPT, add a couple pieces of additional data
            if runDexRpt:
              inputDir, inputFileName = os.path.split(userOptions.get("inputFile",""))
              resultsData = "%s,%s,%s" % (userOptions.get("serialNum"),inputFileName,resultsData)

            # Special case:  process scripts write block 11002 with testNumber of 9999 for parametric table P_EVENT_SUMMARY
            # Data for this table written at a later point as one of the last things DEX does
            if testNumber != 9999 and not err:
              xmlData = resultsData
              missingDataCount = colCount - len(xmlData.split(","))
              if missingDataCount > 0:
                TraceMessage('WARNING!  "%s":  xmlCOLs=%i, DATA=%i' % (tableName, colCount, len(xmlData.split(","))))
                TraceMessage('          %i empty data element(s) "," appended to DataString' % missingDataCount)
                xmlData += "," * missingDataCount # add ,'s for missing data
              resultsHandlers.writeToParametricFile(xmlData)
            formattedData += "\n%s" % resultsData
          except:
            TraceMessage("ERROR parametricextractors.py block 11000;  Problem writing data for table code %s" % currentTableCode)

    except:
      TraceMessage("ERROR parametricextractors.py block 11000; Problem writing table header info and data")
      traceback.print_exc()

    return formattedData


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ParametricSubBlock:     # 11002 block code; contains data

  def __call__(self,resultsData,testNumber,collectParametric,counters,resultsHandlers,userOptions,*args,**kwargs):
    global skipParsing

    # Only collect parametric data if the spc_id is set in the user script or if user passes option to ignore spc_id or
    # if the tablematrix file is present and contains the current tablecode & spc_id
    if ((str(collectParametric) != "None" and str(collectParametric) != "-1") or userOptions.get("ignoreSpcId",0)) and not skipParsing:
      return(self.handleData(resultsData,testNumber,collectParametric,counters,resultsHandlers,userOptions))


  def handleData(self,resultsData,testNumber,collectParametric,counters,resultsHandlers,userOptions):

    global seqNum
    global tableType
    global currentTableCode
    global colCount

    # Based on table code; grab list of column types from dictionary
    # If dictionary has col types, the table is meant for Oracle; if col types is an empty string, the table is for the text file only
    try:
      colTypes = tableHeaders[currentTableCode][3]
    except:
      TraceMessage("ERROR parametricextractors.py block 11002;  Can not find column types for table code %s" % currentTableCode)
      colTypes = ""

    if (not colTypes) and userOptions.get("parseAllTables",0):
      try:
        colMasks = tableHeaders[currentTableCode][2]
        colTypes = ['X' for x in colMasks]
        colTypes = ','.join(colTypes)
      except:
        pass

    # DEXRPT has an option to parse the tables meant for the text file (viewer), if set, parse even though the col types field is empty
    if colTypes or userOptions.get("parseViewerTables",0):
      try:
        # Based on table code; grab list of column masks from imported dictionary
        colMasks = tableHeaders[currentTableCode][2]

        if userOptions.get("parseAllTables",0):
          colMasks = [1 for x in colMasks] # change any 0's -> 1's
          colMasks = tuple(colMasks)

        err,msg,resultsData = formatTableData(resultsData,counters,testNumber,tableType,colMasks,collectParametric,seqNum,userOptions)
        if err:
          TraceMessage("ERROR parametricextractors.py block 11002;  %s for table code %s" % (msg,currentTableCode))

        # If running DEXRPT, add a couple pieces of data
        if userOptions.get("dexrpt",0):
          inputDir, inputFileName = os.path.split(userOptions.get("inputFile",""))
          resultsData = "%s,%s,%s" % (userOptions.get("serialNum"),inputFileName,resultsData)

        # Special case:  process scripts write block 11002 with testNumber of 9999 for parametric table P_EVENT_SUMMARY
        # Data for this table written at a later point as one of the last things DEX does
        if testNumber != 9999 and not err:
          xmlData = resultsData
          missingDataCount = colCount - len(xmlData.split(","))
          if missingDataCount > 0:
            xmlData += "," * missingDataCount # add ,,'s for missing data
          resultsHandlers.writeToParametricFile(xmlData)
      except:
        TraceMessage("ERROR parametricextractors.py block 11002;  Problem writing data for table code %s" % currentTableCode)
        traceback.print_exc()

    return resultsData

