#!/usr/bin/env fofpython
# --------------------------------------------------------------------------------------- #
#                                                                                         #
#                                   Seagate Confidential                                  #
#                                                                                         #
# --------------------------------------------------------------------------------------- #

# ******************************************************************************
#
# VCS Information:
#                 $File: //depot/TCO/DEX/parseresults.py $
#                 $Revision: #11 $
#                 $Change: 805618 $
#                 $Author: alan.a.hewitt $
#                 $DateTime: 2015/01/05 07:11:47 $
#
# ******************************************************************************

# INCREMENT THIS VERSION NUMBER FOR EACH NEW RELEASE OF DEX
VERSION = "2.44"

# reference:
# -> http://yeti/html/esg_tse_firmware-tester_data_record_format_specification.html (old)
# -> http://yeti/html/tse_firmware-tester_data_record_format_specification.html (new)
# ====================================================================================
# ====================================================================================
# Old CM & Old FW
# ====================================================================================
# ====================================================================================
#                     CM            |                    FW
# ----------------------------------+----------------------------------------
#        Header (10 Bytes)          |   Header  (24 Bytes)       Data
# --------------------------------  +  --------------------  +  ------
# Size  Time  +5V  +12V  Temp  SPC  |  tNum  eCode  tParams  |   Data
#   2     4    1     1     1    1   |    2     2       20    |  <= 512
#
#
#
# ====================================================================================
# ====================================================================================
# Old CM & New FW
# ====================================================================================
# ====================================================================================
#                     CM            |                    FW
# ----------------------------------+----------------------------------------
#        Header (10 Bytes)          |   Header (5 Bytes)        Data      CRC
# --------------------------------  +  ------------------  +   ------  +  ---
# Size  Time  +5V  +12V  Temp  SPC  |  tNum  eCode  bType  |    Data   |  CRC
#   2     4    1     1     1    1   |    2     2      1    |   <= 512  |   2
#
#
#
# ====================================================================================
# ====================================================================================
# New CM & Old FW
# ====================================================================================
# ====================================================================================
#          CM      |                    FW             |  CM
# -----------------+-----------------------------------+-----
# Header (5 Bytes) |   Header  (24 Bytes)       Data   |  CRC
# ---------------  +  --------------------  +  ------  +  ---
# Size  rKey  SPC  |  tNum  eCode  tParams  |   Data   |  CRC
#   2     1    1   |    2     2       20    |  <= 512  |   2
#
#
#
# ====================================================================================
# ====================================================================================
# New CM & New FW)
# ====================================================================================
# ====================================================================================
#          CM      |                    FW                    |  CM
# -----------------+------------------------------------------+-----
# Header (5 Bytes) |   Header (5 Bytes)        Data      CRC  |  CRC
# ---------------  +  ------------------  +   ------  +  ---  +  ---
# Size  rKey  SPC  |  tNum  eCode  bType  |    Data   |  CRC  |  CRC
#   2     1    1   |    2     2      1    |   <= 512  |   2   |   2
#
#
#
#
# ------------------------------------------------------------------------
# KEY:
# ------------------------------------------------------------------------
# Size  = Total Record Size (Bytes)
# Time  = thisTest Date & Time
# +5V   = Chamber +5V
# +12V  = Chamber +12V
# Temp  = Chamber Temp
# SPC   = SPC ID
#
# tNum  = Test Number
# eCode = Error Code
# bType = Block Type


import sys,time,traceback,struct,binascii,types,os,fnmatch,zipfile

from resultshandlers import ResultsHandlers

VERBOSE = 0

# States the test can be in
# Found a partial results flag of 1
STATE_TEST_START = "Test Started"
# Found the **TestCompleted ScriptComment
STATE_TEST_COMPLETED = "Test Completed"
# Found the FINISHED ScriptComment
STATE_FINISHED = "Test Finished"
# Found a partial results flag of 0
STATE_TEST_DONE = "Test Done"


# Define TraceMessage if we're not running in the Gemini script environment.
try:     TraceMessage
except:
  def TraceMessage(msg): print msg

try:
   from ErrorCodes import errCodes
except:
   errCodes = {}

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Define the class here, and make a global instance below.
# The idea is that the scripter will import the instance.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class _ResultsParser:
  def __init__(self):

    # Keeps track of test state, so ScriptComments can be matched up to get test data for TEST_TIME_BY_TEST parametric table
    self.testState = ""

    # Our results call back should save the results to the results file.
    self.saveToResultsFile = 1

    # Dictionary of test information which is used to populate the run time parametric table
    self.testRunTime = {}

    # This is the count of tests within the results file; the counter is used when populating run time dictionary
    self.testCounter = 0

    # Total script run time of the drive; calculated for the P_EVENT_SUMMARY parametric table
    self.totalRunTime = 0

    # Dictionary to hold data on the failing test
    self.failingTestSignature = {}

    # Start time of the script parsed out of a ScriptComment
    self.scriptStart = 0

    # Default counters; counters are populated after a test has been processed or when counters are reset by a -7 test number from
    # results file, so it is possible the first test may not have counters therefore defaults need to be set
    self.counters = 1,1,{},(0,0,0,0,-1)

    # Data for the P_EVENT_SUMMARY parametric table
    self.pEventSummary = {}

    # Default sequence number
    self.seq = 0

    # Default SPC_ID
    self.spcId = "?"
    self.spcId32 = None

    # Parameter name written by the script to the results file for each test
    self.paramNameByTest = ""

    # Variable gets populated when the paramCode file is parsed
    self.paramNames = {}

    # Dictionary of information pulled from viewer support files
    self.supportFiles = {}


  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # This function was created to allow passing of args from a script.
  # Originally individual args were used (like this function)
  # then a change was made to be handle options in a dictionary
  # (like createDEXHandlers) this broke the scripts because they
  # were passing individual args - this function was created so the
  # scripts do not have to change
  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def createHandlers(self,textResultsOnly=0,paramResultsOnly=0,paramFilePath="",ignoreSpcId=0,errorCodeFile="",procErrorCodeFile="",messagesFile="",winFOFInstance=None, skipParametricTables={}):
    scriptOptions = {}

    # Checks to alert script writer if they pass in junk
    if not textResultsOnly == 0 and not textResultsOnly == 1:
      msg = "ERROR parseresults.py:  Invalid value - %s - for keyword argument textResultsOnly." % (textResultsOnly)
      TraceMessage(msg)
    else:
      scriptOptions["textResultsOnly"] = textResultsOnly

    if not paramResultsOnly == 0 and not paramResultsOnly == 1:
      msg = "ERROR parseresults.py:  Invalid value - %s - for keyword argument paramResultsOnly." % (paramResultsOnly)
      TraceMessage(msg)
    else:
      scriptOptions["paramResultsOnly"] = paramResultsOnly

    if not ignoreSpcId == 0 and not ignoreSpcId == 1:
      msg = "ERROR parseresults.py:  Invalid value - %s - for keyword argument ignoreSpcId." % (ignoreSpcId)
      TraceMessage(msg)
    else:
      scriptOptions["ignoreSpcId"] = ignoreSpcId

    # if not winFOFInstance is None:
    if winFOFInstance == None:
      # If text results are produced but users do not pass in an errorCode or paramFile or messagesFile, warn them
      # In order for DEX to find these support files, the users have to pass in the path to them
      if not paramResultsOnly and (not errorCodeFile or not paramFilePath or not procErrorCodeFile or not messagesFile):
        msg = "WARNING parseresults.py:  For complete text results pass in an errorCodeFile path, procErrorCodeFile path, paramFile path and messagesFile path."
        TraceMessage(msg)

    scriptOptions["errorCodeFile"] = errorCodeFile

    scriptOptions["procErrorCodeFile"] = procErrorCodeFile

    scriptOptions["paramFile"] = paramFilePath

    scriptOptions["messagesFile"] = messagesFile

    scriptOptions["winFOFInstance"] = winFOFInstance

    scriptOptions["skipParametricTables"] = skipParametricTables

    self.createDEXHandlers(scriptOptions)


  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # Constructor cannot accept arguments when DEX is run at command line because when this script is imported an instance of
  # the ResultsParser class is created.  This function was created to allow passing of args when run from the command line.
  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def createDEXHandlers(self,userOptions,startTime=0):

    self.userOptions = userOptions

    if startTime == 0:
      startTime = time.time()

    # Flag to indicate whether DEXRPT is being run
    self.userOptions["dexrpt"] = 0

    self.textResultsOnly = self.userOptions.get("textResultsOnly",0)
    self.paramResultsOnly = self.userOptions.get("paramResultsOnly",0)

    self.resultsHandlers = ResultsHandlers(self.userOptions,VERSION,startTime)

    if self.paramResultsOnly == 0:
      self.readParamCodeFile(userOptions["paramFile"])

    # if winFOFInstance then update supportFiles to handle fault-codes from the firmware
    if self.userOptions.get('winFOFInstance',0):
      self.supportFiles['errorCodes']   = self.loadErrorCodeDesc()
      self.supportFiles['firmwareMsgs'] = self.loadFirmwareMessages()
      self.errorMsg = ''


  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # Constructor cannot accept arguments when DEXRPT is run at command line because when this script is imported an instance of
  # the ResultsParser class is created.  This function was created to allow passing of args when run from the command line.
  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def rptCreateHandlers(self,userOptions,startTime):
    from resultshandlers import RptResultsHandlers

    self.userOptions = userOptions

    if startTime == 0:
      startTime = time.time()

    # Set to zero; gets set when running DEX, otherwise it should be 0
    self.textResultsOnly = 0
    self.paramResultsOnly = 0

    # Flag to indicate whether DEXRPT is being run
    self.userOptions["dexrpt"] = 1

    self.resultsHandlers = RptResultsHandlers(userOptions,VERSION,startTime)


  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # Courtesy method to get one of the results handler objects.
  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def get(self,handlerNumber):
    return self.resultsHandlers.get(handlerNumber)


  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def writeEventSummaryParametricTable(self):
    # Data for P_EVENT_SUMMARY is written to results file by the scripts; it is saved off by parametricextractors & written to parametric file by this function
    # It has to be written after parsing results file because the table needs total run time of the script

    from tabledictionary import tableRevision

    match = 0

    # New results files will only contain 11000 block codes
    # Keys method may not present the keys in numerical order;
    # therefore sort is required as the data must be written in order or the XML will get rejected by FIS
    blockCodes = self.pEventSummary.keys()
    blockCodes.sort()

    for thisBlockCode in blockCodes:
      if thisBlockCode == 11000: # skip "special" DEX block codes
        scriptOccurrence,seqOccurrence,testSeqEventDict,failureHeader = self.counters

        # Grab the failing information from the failure header DEX populates for each failing test
        # The drive can pass and have failed tests in the failureHeader
        failKeys = failureHeader.keys()
        # Key is script occurrence, want keys in order because if there are multiple failures that match signature, the first matching failure should be used
        failKeys.sort()
        for j in failKeys:
          testNum,errorCode,failSeqOccurrence,failTestSeqEvent,failTestScriptEvent,failPortID = failureHeader[j]
          failScriptOccurrence = j
          # If the drive failed
          if self.failingTestSignature:
            # Does the signature match any of the failing tests in the header?  If so, populate the parametric table with that data
            if self.failingTestSignature["testNumber"] == testNum and self.failingTestSignature["errorCode"] == errorCode:
              match = 1
              break

        # If it is a passing drive or for some reason there is not a matching signature for the failing drive
        if not match:
          # Set up the defaults FIS wants to see in the parametric table
          failSeqOccurrence,failTestSeqEvent,failTestScriptEvent,failPortID,failScriptOccurrence = 0,0,0,-1,0

          # If it is a failed drive and no matching signature, raise a warning messsage
          if self.failingTestSignature:
            msg = "ERROR parseresults.py:  No signature match found for any failing test. Signature: %s; FailureHeader: %s  " % (self.failingTestSignature,failureHeader)
            TraceMessage(msg)

        # These columns are only for P_EVENT_SUMMARY table which is written by the user script
        # User script populates some columns with place holders (?num) and this script fills in the actual data
        # FAILING_PORTID ?1; FAILING_EVENT ?2; FAILING_SQ_EVT ?3; FAILING_TST_EVT ?4; FAILING_TS_EVT ?5;  DEX_VER ?6; RUN_TIME ?7; PARAM_DICTIONARY_VER ?8
        if self.pEventSummary[thisBlockCode]:
          self.pEventSummary[thisBlockCode] = self.pEventSummary[thisBlockCode].replace("?1",str(failPortID),1)
          self.pEventSummary[thisBlockCode] = self.pEventSummary[thisBlockCode].replace("?2",str(failScriptOccurrence),1)
          self.pEventSummary[thisBlockCode] = self.pEventSummary[thisBlockCode].replace("?3",str(failSeqOccurrence),1)
          self.pEventSummary[thisBlockCode] = self.pEventSummary[thisBlockCode].replace("?4",str(failTestScriptEvent),1)
          self.pEventSummary[thisBlockCode] = self.pEventSummary[thisBlockCode].replace("?5",str(failTestSeqEvent),1)
          self.pEventSummary[thisBlockCode] = self.pEventSummary[thisBlockCode].replace("?6",str(VERSION),1)
          self.pEventSummary[thisBlockCode] = self.pEventSummary[thisBlockCode].replace("?7",str(self.totalRunTime),1)
          self.pEventSummary[thisBlockCode] = self.pEventSummary[thisBlockCode].replace("?8",str(tableRevision),1)
      if self.pEventSummary[thisBlockCode]:
        # If there are any null characters in the data, get rid of them; the Gemini host will reject data with a nul as invalid XML data
        if self.pEventSummary[thisBlockCode].find("\00"):
          self.pEventSummary[thisBlockCode] = self.pEventSummary[thisBlockCode].replace("\00","")
        self.resultsHandlers.writeToParametricFile(self.pEventSummary[thisBlockCode])


  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def writeTestTimeParametricTable(self):
    # TEST_TIME_BY_TEST data is gathered by DEX and written to parametric file or text file by this function
    testTimeFileFlag = 0
    try:
      if self.testRunTime:
        tableName = "TABLE=TEST_TIME_BY_TEST TYPE=S"
        columnTypes = "N,N,N,N,N,N,V,N"
        columnNames = "SPC_ID,OCCURRENCE,SEQ,TEST_SEQ_EVENT,TEST_NUMBER,ELAPSED_TIME,PARAMETER_NAME,TEST_STATUS"

        # DEXRPT handling
        if self.userOptions.get("dexrpt",0):
          # Add two additional columns
          dexrptColumnNames = "SERIALNUM,RESULTS_FILENAME,%s" % columnNames
          inputDir, inputFileName = os.path.split(self.userOptions.get("inputFile",""))
          serialNum = self.userOptions.get("serialNum","")
          # User has chosen to print the TEST_TIME_BY_TEST table to the main output file
          if self.userOptions.get("printTestTimeByTest",0):
            self.resultsHandlers.writeToParametricFile(tableName)
            self.resultsHandlers.writeToParametricFile(dexrptColumnNames)
          # User has also chosen to write data to individual table files
          if self.userOptions.get("printTestTimeByTest",0) and self.userOptions.get("outputFilesByTable",0):
            fileExists = 0
            outputFile = os.path.join(self.userOptions.get("outputFileDir",""),"test_time_by_test.sum")
            if os.path.exists(outputFile):
               fileExists = 1
            # File will never get overwritten to, always appended to.  This is the behavior requested by process engineers.
            testTimeFile = open(outputFile,'a')
            testTimeFileFlag = 1
            # If the file already exists, do not write column names because they are already in the file
            if not fileExists:
              testTimeFile.write("%s\n" % dexrptColumnNames)
        # DEX handling
        else:
          # Can not write data to XML file if user chooses to only create a text file
          if not self.textResultsOnly:
            self.resultsHandlers.writeToParametricFile(tableName)
            self.resultsHandlers.writeToParametricFile(columnNames)
            self.resultsHandlers.writeToParametricFile(columnTypes)
          # Only write data to text file is user chooses the option to write this table to the text file
          if self.userOptions.get("testTimeTable",0):
            tableName = "\n%s" % (tableName)
            self.resultsHandlers.writeToTextFile(tableName,1)
            self.resultsHandlers.writeToTextFile(columnNames,1)


        for myKey in self.testRunTime.keys():
          data = ""
          for i in range(len(self.testRunTime[myKey])):
            # Do not put a comma on the last item in the row
            # Assuming data is in correct order - the function to populate the dictionary should have put it in dictionary in the correct order
            if i == len(self.testRunTime[myKey]) - 1:
              data = data + "%s" % self.testRunTime[myKey][i]
            else:
              data = data + "%s," % self.testRunTime[myKey][i]

          # DEXRPT handling
          if self.userOptions.get("dexrpt",0):
            if self.userOptions.get("printTestTimeByTest",0):
              self.resultsHandlers.writeToParametricFile("%s,%s,%s" % (serialNum,inputFileName,data))
            if self.userOptions.get("printTestTimeByTest",0) and self.userOptions.get("outputFilesByTable",0):
              testTimeFile.write("%s,%s,%s\n" % (serialNum,inputFileName,data))
          # DEX handling
          else:
            if self.userOptions.get("testTimeTable",0):
              self.resultsHandlers.writeToTextFile("%s" % data,1)

            if not self.textResultsOnly:
              self.resultsHandlers.writeToParametricFile("%s" % data)
      else:
        if self.userOptions.get("testTimeTable",0):
          msg = "\nNo data available for the TEST_TIME_BY_TEST parametric table"
          self.resultsHandlers.writeToTextFile(msg,1)

    except:
      msg = "ERROR parseresults.py:  Error writing TEST_TIME_BY_TEST parametric table"
      TraceMessage(msg)
      if VERBOSE:
        traceback.print_exc()

    else:
      if testTimeFileFlag:
        testTimeFile.close()


  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def parseScriptComment(self,testNumber,errorCode,resultsData,*args,**kwargs):
    # This function parses ScriptComments (-44 test number) found in the results file & does the following:
    # 1)  Populates a dictionary of information for each instance of a test which includes test number, run time, test status and header data
    #     needed for parametrics.  The run time info is needed for the parametric table TEST_TIME_BY_TEST
    # 2)  Grabs the 32 bit spcId if one exists
    # 3)  Calculates total script run time which is used in the P_EVENT_SUMMARY parametric table

    # Format CM code uses to write date/time stamp into results file with time.strftime
    timeFormat = "%b %d %Y-%H:%M:%S"

    try:
      # Look for keyword written in by the CM code specifically for this parser which contains test time for a single test
      if resultsData.find("**TestCompleted=") != -1:

        # Split to get the time stamp & keyword in one list entry and the test number/test time in another
        cmtString = resultsData.split("=",1)
        testNum,testTime = cmtString[1].split(",",1)

        # Convert test time to a float so math functions can be utilized on it
        if not isinstance(testTime,types.FloatType):
          testTime = float(testTime)
        # Convert test num because any test number coming from results file will be an int
        if not isinstance(testNum,types.IntType):
          testNum = int(testNum)

        # Populate test header dictionary with information; Counters are incremented after last block of a test; the ScriptComment with test time
        # will only occur after the counters have been incremented so they need to be decremented for use in this dictionary
        # Order of data in dictionary is important - needs to be in the same order as columns in the TEST_TIME_BY_TEST table
        # Last value, TEST_STATUS, is a default; fill in a -1 just in case DEX is unable to get the actual status from the FINISHED comment
        # Just going to assume this is the correct spcID - no checking the counters or the test number
        scriptOccurrence,seqOccurrence, testSeqEventDict,failureHeader=self.counters
        self.testRunTime[scriptOccurrence-1] = [self.spcId,seqOccurrence-1, self.seq,testSeqEventDict[testNum]-1,testNum,testTime,self.paramNameByTest,-1]
        self.testState = STATE_TEST_COMPLETED
        self.paramNameByTest = ""

      # Look for keywords written in by CM code which will contain, among other things, the test number, time & status
      elif resultsData.find("F I N I S H E D   Testing") != -1 and resultsData.find("Test Stat:") != -1:
        cmtList = resultsData.split("Test Stat: ",1)
        cmtList = cmtList[1]
        testStat = cmtList.split(",",1)[0]

        # If a **TestCompleted comment was previously found for this test, then grab the test status from this comment
        if self.testState == STATE_TEST_COMPLETED:
          scriptOccurrence,seqOccurrence, testSeqEventDict,failureHeader=self.counters
          # Remove last item in list which is a default of -1 put in place by the **TestCompleted comment and append the real value
          self.testRunTime[scriptOccurrence-1].pop(7)
          self.testRunTime[scriptOccurrence-1].append(testStat)

        self.testState = STATE_FINISHED

      # Look for keyword written in by the CM code specifically for this parser which contains 32 bit spcId information
      elif resultsData.find("**SPC_ID32=") != -1:

        # Split to get the time stamp & keyword in one list entry and the spcId value and spcId comment in another
        spcIdString = resultsData.split("=",1)
        # Split the scpId value out from the spcId comment
        self.spcId32 = spcIdString[1].split(" ",1)[0]

      # Look for keyword written to results file by CM cellpy at start of the script to help calculate total script run time
      elif resultsData.find("##### FOF generated Results File") != -1:
        # Power loss recovery appends to the results file so there could be two instances of this comment in the file
        # Manufacturing wants the total script runtime, so after the first instance of this comment, ignore any others in the file
        if not self.scriptStart:
          # Split ScriptComment to isolate the date/time stamp
          scriptStartDate = resultsData.split("  ")[0]
          scriptStartDate = scriptStartDate.split("\n")[1]
          # Parse date/time string and convert to seconds since the epoch
          self.scriptStart = time.mktime(time.strptime(scriptStartDate,timeFormat))

      # Look for keyword written in by scripts; they write the parameter name which goes in the TEST_TIME_BY_TEST table
      # Limit the string to 128 characters; need some limit to ensure process does not go crazy and overload the CM
      elif resultsData.find("**PRM_NAME=") != -1:
        self.paramNameByTest = resultsData.split("=",1)[1][0:128]

      else:
        # Look for last ScriptComment in results file to get the end time of the script which is used to calculate total script run time
        # As looping through results file, these variables will get overwritten by every ScriptComment; eventually they will contain data for the last comment

        # Split ScriptComment to isolate the date/time stamp
        scriptEndDate = resultsData.split("  ")[0]
        scriptEndDate = scriptEndDate.split("\n")[1]

        # Not every ScriptComment has a time stamp; if it does not have a time stamp, an error is raised & ScriptComment can be ignored
        try:
          # Parse date/time string and convert to seconds since the epoch
          end = time.mktime(time.strptime(scriptEndDate,timeFormat))
        except TypeError:
          # This is a typical error when name/value pair attributes are in a ScriptComment ex. ('VALID_OPER','MTSIO')
          pass
        except ValueError:
          # This is a typical error for ScriptComment containing info on CSF (CellStatus Bits)
          pass
        else:
          # Find total script run time in hours
          self.totalRunTime = round((end - self.scriptStart) / 3600.0,2)

    except:
      # One reason for falling into this except, is the ScriptComment does not have a timestamp; This can happen when a ScriptComment is really long which really is not an error..
      # This msg is confusing users, so only print when in verbose mode
      if VERBOSE:
        msg = "ERROR parseresults.py:  Error parsing ScriptComment;  test number %s; resultsData: %s ignoring error " % (testNumber,resultsData)
        TraceMessage(msg)
        traceback.print_exc()


  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def readParamCodeFile(self,paramFilePath):
    try:
      paramCodeFile = open(paramFilePath)
    except:
      self.paramNames = None
      msg = "\nERROR:  Cannot open paramCodeFile: %s\n" % (paramFilePath)
      TraceMessage(msg)
      self.resultsHandlers.writeToTextFile(msg)
      if VERBOSE:
        traceback.print_exc()
      return

    try:
      paramCodeLines = paramCodeFile.readlines()

      self.paramNames = {}   # nameCode: parameterName

      for line in paramCodeLines:
        split = line.split()
        if len(split) >= 3:  # The line from the C header file should contain at least: #define ITEM value
          define,name,value = split[:3]
          if define == "#define":  # the first item in the line shall be "#define"
            if name.find("_PARM_") > 0:  # second parm must contain "_PARM_"
              parameterName,item = name.split("_PARM_")  # key is the name the user will put into their parm files
              if item in ["C"]:        # item must be in ["C"] (code)
                nameCode = int(value)  # convert the value to integer
                self.paramNames[nameCode] = parameterName
    except:
      self.paramNames = None
      msg = "ERROR: Cannot parse paramCodeFile: %s" % paramCodeFile
      TraceMessage(msg)
      if VERBOSE:
        traceback.print_exc()


  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # Parse a file filled with #defines; fileNames is a list
  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def parseDefineFile(self,lines,fileNames):
    messages = {}
    try:
      for line in lines:
        # Remove beginning and ending white space from the line
        line = line.strip()
        if fnmatch.fnmatch(line,"#define*"):
          try:
            origLine = line
            myLine = line.split(" ", 2)

            # Before lstrip() looks like:   "                 0  /* Drive Passed  */\n"
            codeInfo = myLine[2].lstrip()

            # line will contain a list: first item in list is the code, second item is string message plus other junk
            line = codeInfo.split(" ",1)

            # Before lstrip() looks like:   "  /* Drive Passed  */\n"
            msg = line[1].lstrip(" /*")
            # There could be two sets of comments on a line, just use the first one & consider the rest junk data
            msg,junk = msg.split("*/",1)
            msg = msg.rstrip("\n ")
            if messages.has_key(int(line[0])) and int(line[0]) !=0:
              # If duplicates exist, the existing message for the code will be overwritten by the next message
              msg = "WARNING:  Duplicate code - %s - in file(s): %s" % (int(line[0]),fileNames)
              TraceMessage(msg)
            messages[int(line[0])] = msg
          except:
            if VERBOSE:
              TraceMessage("ERROR: Problem parsing file(s): %s. Line: %s %s " % (fileNames,origLine,traceback.print_exc()))
            # If a line cannot be parsed, just skip it
            continue
        else:
          # If the line does not start with a #define, just skip it and move on
          continue
    except:
      msg = "ERROR: Cannot parse file(s): " % (fileNames)
      TraceMessage(msg)
      self.resultsHandlers.writeToTextFile(msg)
      if VERBOSE:
        traceback.print_exc()
    return messages


  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # Load all the error codes and their descriptions into a dictionary
  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def loadErrorCodeDesc(self):
     descriptions = {}
     lines = []
     errorCodeFiles = []


     if errCodes:
        return errCodes

     # Read in the TSE error code file
     try:
       f = open(self.userOptions["errorCodeFile"])
       lines.extend(f.readlines())
       f.close()
       errorCodeFiles.append(self.userOptions["errorCodeFile"])
     except:
       msg = "ERROR:  Cannot open or read error code file: %s\n" % (self.userOptions["errorCodeFile"])
       TraceMessage(msg)
       self.resultsHandlers.writeToTextFile(msg)
       if VERBOSE:
         traceback.print_exc()

     # Report Exception only if user has passed in procErrorCodeFile. If not then do not even try and read the file
     if not self.userOptions.get('winFOFInstance',0) or self.userOptions["procErrorCodeFile"]:
       # Read in the process engineering error code file
       try:
         f = open(self.userOptions["procErrorCodeFile"])
         lines.extend(f.readlines())
         f.close()
         errorCodeFiles.append(self.userOptions["procErrorCodeFile"])
       except:
         msg = "ERROR:  Cannot open or read process error code file: %s\n" % (self.userOptions["procErrorCodeFile"])
         TraceMessage(msg)
         self.resultsHandlers.writeToTextFile(msg)
         if VERBOSE:
           traceback.print_exc()

     if lines:
       descriptions = self.parseDefineFile(lines,errorCodeFiles)

     return descriptions


  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def loadFirmwareMessages(self):

     msgDict = {}
     lines = []

     # Read in the TSE messages file
     try:
       f = open(self.userOptions["messagesFile"])
       lines.extend(f.readlines())
       f.close()
     except:
       msg = "ERROR:  Cannot open or read messages file: %s\n" % (self.userOptions["messagesFile"])
       TraceMessage(msg)
       self.resultsHandlers.writeToTextFile(msg)
       if VERBOSE:
         traceback.print_exc()

     if lines:
       msgDict = self.parseDefineFile(lines, [self.userOptions["messagesFile"]])

     return msgDict


  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # Calculate a CRC the same way the CM/script code & self-test/IO code does
  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def calcCRC(self,data,sizein,crc):
    for i in map(ord, data[:sizein]):
      crc += (crc & 0xAA) ^ i
    return crc


  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def processOldFirmwareHeader(self,resultsSector):
    # A 24-byte "dataHeader"
    #   * testNum           (2 bytes)
    #   * errorCode         (2 bytes)
    #   * 10 testParams     (2 bytes each / 20 bytes total)
    # Define the dataHeader.

    # Every resultsSector should have a dataHeader with above format
    dataHeaderSize = struct.calcsize('>hH' + '10H')

    # Validate
    if len(resultsSector) < dataHeaderSize:
      msg = self.errorMsg + "Invalid data header.  received: %s bytes, expected: >= %s bytes." % (len(resultsSector),dataHeaderSize)
      TraceMessage(msg)
      return(1,msg)

    # Split the dataHeader from the resultsData.
    dataHeader = resultsSector[:dataHeaderSize]
    resultsData = resultsSector[dataHeaderSize:]

    # Pull out the big-endian testNumber, errorCode
    testNumber, errorCode = struct.unpack('>hH',dataHeader[:4])
    return(0,(testNumber,errorCode,resultsData))


  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # WinFOF calls this function via a tester callback therefore the first 5 args & their order can not change
  # temp & the volts are no longer even used, they are remnants of the old firmware & tester header
  def resultsCallBack(self,data,currentTemp=None,drive5=None,drive12=None,collectParametric=None,currentTime=None):

    # WinFOF does a callback of this function and relies on this piece of code to write data to the results file
    if self.saveToResultsFile:
      from writeresultsfunctions import ESGSaveResults
      ESGSaveResults(data,collectParametric)

    # If our caller is reading from a results file, they will have a currentTime to pass in here.
    # If our caller is the tester, then we will not get currentTime.
    if None == currentTime: currentTime = time.time()

    # Cut off the one byte results key
    resultsSector = data[1:]

    # Assume this is a new 5 byte firmware header
    # Every firmware header has 2 bytes test number, 2 bytes error code and 1 byte block type
    firmareHeaderFormat = ">hHb"
    firmareHeaderSize = struct.calcsize(firmareHeaderFormat)

    # Validate the size
    if len(resultsSector) < firmareHeaderSize:
      msg = self.errorMsg + "Invalid firmware header.  received: %s bytes, expected: >= %s bytes." % (len(resultsSector),dataHeaderSize)
      TraceMessage(msg)
      return(1,msg)

    testNumber, errorCode, blockType = struct.unpack(firmareHeaderFormat,resultsSector[:firmareHeaderSize])

    # Is this a new style firmware header?
    if blockType in (1,):
      # On a new style record, the firmware CRC is the last 2 bytes of the firmware record
      crcFormat = ">H"
      crcSize = struct.calcsize(crcFormat)
      firmwareCRCCheck = struct.unpack(crcFormat,resultsSector[len(resultsSector)-crcSize:])[0]

      # Calculate the firmware CRC
      # First two bytes (test num) and last two bytes (firmware CRC) are not included in the CRC calculation
      rec = resultsSector[2:-crcSize]
      # Pass the same arbitrary seed value (604 == throwing missiles) as firmware & tester do to ensure a CRC of 0's does not equal 0
      crc = self.calcCRC(rec,len(rec),604)
      # Our function returns a 32 bit value, but firmware function returns a 16 bit value so mask it to get a 16 bit value
      crc = crc & 0xFFFF

      # There is a slim chance an old header would be in this loop by mistake.  Compare our calculated CRC with the firmware calculated CRC
      # If the CRC check fails, try to process the old style header
      if firmwareCRCCheck != crc:
        #TraceMessage("CRC Check does not match.  DEX CRC Check: %s Firmware CRC Check %s" % (crc,firmwareCRCCheck))
        err,data = self.processOldFirmwareHeader(resultsSector)
        # If there was an error do not keep trying to process this record
        if err:
          return(2,data)
        else:
          testNumber,errorCode,resultsData = data

      # New style 5 byte firmware record
      else:
        # From the data set, remove the firmware header from the beginning and the firmware CRC check at the end
        resultsData = resultsSector[firmareHeaderSize:-crcSize]

    else:
      # Old style 24 byte firmware header
      err,data = self.processOldFirmwareHeader(resultsSector)
      # If there was an error do not keep trying to process this record
      if err:
        return(3,data)
      else:
        testNumber,errorCode,resultsData = data

    # This msg is used below where we raise Exceptions.
    errMsg = "==> testNumber: %s (x%04X) errorCode: %s" % (testNumber,testNumber,errorCode)

    # If the high bit is set in the test number, this indicates either a negative test number or partial results.

    # Two forms of spcId - old 4 bit style which comes in the 10 bytes header, new 32 bit which is in a ScriptComment
    # CM code fills in both legacy and new but if spcId is greater than 4 bits, the legacy spcId is set to zero
    # If a 32 bit spcId exists, always use that
    if self.spcId32 and self.spcId32 != "None":
      collectParametric = self.spcId32

    # Look for a valid negative test number.  Do this before masking off the high bit in the test number.
    if testNumber < 0 and testNumber >= -44:

      # Look-up the resultsHandler and run it.
      resultsHandler = self.resultsHandlers.get(testNumber)
      # At the start of a seq, reset the seq specific parametric counters & get default counter values
      # Do not deal with parametric counters when only a text file is created unless user has chosen option to have TEST_TIME_BY_TEST table written to text file
      if testNumber == -7:
        if (not self.textResultsOnly or self.userOptions.get("testTimeTable",0)):
          self.seq = struct.unpack('>H',resultsData[:(struct.calcsize(">H"))])[0]
          self.counters = self.resultsHandlers.resetParamCounters(self.seq)
        else:
          # Ignore; Will fall in here if a -7 and just outputting text results
          return

      # -44 indicates a ScriptComment which is a CM script service; parse ScriptComment to get run times & 32 bit spcIds
      # Do not parse comment when only a text file is created unless user has chosen option to have TEST_TIME_BY_TEST table written to text file
      if testNumber == -44 and (not self.textResultsOnly or self.userOptions.get("testTimeTable",0)):
          self.parseScriptComment(testNumber,errorCode,resultsData)
          # If a 32 bit spcId exists, always use that
          if self.spcId32 and self.spcId32 != "None":
            collectParametric = self.spcId32
      if not resultsHandler:
        # Now we have a negative test number that we don't understand.
        msg = "parseresults.py:  There is no handler for this negative test number.\n%s" % (errMsg)
        if VERBOSE:
          TraceMessage(msg)
        return

      # Call the resultsHandler to process these results.
      for item in range(len(resultsHandler)):
        resultsHandler[item](resultsData,testNumber,collectParametric,self.counters,self.resultsHandlers,self.userOptions,self.supportFiles)
      return

    # Check for the partial results flag and mask it off.
    partialResults = (testNumber & 0x8000)>0
    testNumber &= 0x7FFF

    # Partial results flag of 0 indicates the last block of data for a particular test
    if partialResults == 0:
      self.testState = STATE_TEST_DONE
    else:
      self.testState = STATE_TEST_START

    # This msg is used below in exceptions.
    errMsg = "==>  partialResults: %s  testNumber: %s (x%04X)  errorCode: %s " % (partialResults,testNumber,testNumber,errorCode)
    if VERBOSE: TraceMessage(errMsg)

    # Some results are processed by testNumber.
    # Other results are processed using interpreted results, by block number.

    # Try to look-up the resultsHandler by testNumber and run it.
    resultsHandler = self.resultsHandlers.get(testNumber)
    if resultsHandler:
      for item in range(len(resultsHandler)):
        resultsHandler[item](resultsData,testNumber,collectParametric,self.counters,self.resultsHandlers,self.userOptions,self.supportFiles)
      return

    # Now try to parse the interpreted results blocks.
    try:
      # Loop on the blocks - there can be several.
      while len(resultsData) >= 4:

        # All interpreted results blocks have 'size' and 'code' fields, followed by the results data.
        blockSize,blockCode = struct.unpack("HH",resultsData[:4])
        if blockSize < 4 or blockSize > 512:
          if 'FOF' ==  resultsData[:3]:
            msg = "parseresults.py: %s\n%s" % (resultsData,errMsg)
            if VERBOSE: TraceMessage(msg)

            # Last block in results file contains the 'FOF Final Error Code'
            # A results file could have multiple failures...
            # ...the last block is what the drive actually failed for
            if errorCode != 0:
              self.failingTestSignature = {"testNumber":testNumber,"errorCode":errorCode}

          else:
            msg = "parseresults.py:  Bad block size in interpreted results: %s\n%s"  % (blockSize,errMsg)
            if VERBOSE: TraceMessage(msg)
            # Not all tests have a block size & code (i.e interpreted results) so they show up as a bad block size; skip
            # these tests but increment the counters first.  This code can be deleted after all tests are converted to dblog
            nonInterpTestList = [117,8,505,508,514,535,542,550,555,557,591,595,599,602]
            if (testNumber < 100 or testNumber in nonInterpTestList):
              # Increment parametric counters before skipping this block
              # Do not deal with parametric counters when only a text file is created unless user has chosen option to have TEST_TIME_BY_TEST table written to text file
              if partialResults == 0 and (not self.textResultsOnly or self.userOptions.get("testTimeTable",0)):
                self.counters = self.resultsHandlers.incrementParamCounters(testNumber,errorCode)
                self.spcId = collectParametric
          return # We're done trying to interpret this block since it is invalid.

        blockData = resultsData[4:blockSize]
        # Look up the results handler for this block and run it.
        resultsHandler = self.resultsHandlers.get(blockCode)
        if resultsHandler:
          for item in range(len(resultsHandler)):
            self.formattedData=resultsHandler[item](blockData,testNumber,collectParametric,self.counters,self.resultsHandlers,self.userOptions,self.paramNames,self.supportFiles)
            # Both viewer and parametric blocks loop through here; we only want the parametric data which happens to loop through second
            # Is there a way to ensure this will always contains parametric data??
            if testNumber == 9999:
              self.pEventSummary[blockCode] = self.formattedData
        else:
          if VERBOSE:  TraceMessage("parseresults.py: NO HANDLER:   blockSize: %s  blockCode: %s  blockData: %s\n%s" % (blockSize,blockCode,binascii.hexlify(blockData),errMsg))

        # Cut the current block off the front of the full results block and loop around.
        resultsData = resultsData[blockSize:]

    except:
      msg = "ERROR parseresults.py:  Exception parsing interpreted results; ignoring error \n%s"  % (errMsg)
      TraceMessage(msg)
      if VERBOSE:  traceback.print_exc()

    # Increment parametric counters after the test is processed (partial results of 0 indicates the last block of data for a test)
    # Do not deal with parametric counters when only a text file is created unless user has chosen option to have TEST_TIME_BY_TEST table written to text file
    if partialResults == 0 and (not self.textResultsOnly or self.userOptions.get("testTimeTable",0)):
      self.counters = self.resultsHandlers.incrementParamCounters(testNumber,errorCode)
      # Set spcId for use in the run time dictionary
      self.spcId = collectParametric
      # At end of test, clear the 32 bit spcId just as a safeguard
      self.spcId32 = ""


  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def processOldTesterHeader(self,testerHeader):
    # A 10-byte tester header
    #   * "record size"     (2 bytes)
    #   * Time              (4 bytes)
    #   * v5                (1 byte)
    #   * v12               (1 byte)
    #   * collectParametric (1 byte)
    #   * Temp              (1 byte)

    minRecordSize = self.oldTesterHeaderSize

    # Validate:  Did we actually read a full header?
    if len(testerHeader) != self.oldTesterHeaderSize:
      msg = "WARNING: Invalid tester header.  received : %s bytes, expected: %s bytes" % (len(testerHeader),self.oldTesterHeaderSize)
      TraceMessage(self.errorMsg+msg)
      return(1,msg)

    # Unpack the header.
    thisRecordSize, self.currentTime, v5, v12, self.collectParametric, rptTemp = struct.unpack(self.oldTesterHeaderFormat,testerHeader)

    return(0,"OK")


  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def processResultsFile(self,resultsFileName):

    self.currentTime =  None

    # Do not save the results to the results file
    ResultsParser.saveToResultsFile = 0

    if os.path.exists(resultsFileName):
      zipFileName = ""
      resultFileDirectory = os.path.split( resultsFileName )[0]
      resultsFileBaseDotExtension = os.path.split( resultsFileName )[1]
      resultsFileBaseName = os.path.splitext( os.path.split( resultsFileName )[1] )[0]
      resultsFileExtension = os.path.splitext( os.path.split( resultsFileName )[1] )[1]
      if( resultsFileExtension.upper() == ".ZIP" ):
        zipFileName = resultsFileName
        if zipfile.is_zipfile( zipFileName ):
          zipFile = zipfile.ZipFile( zipFileName, 'r' )
          resultsFileName = zipFile.namelist()[0] # grab 1st filename in ZIP
          TraceMessage("*** unzipping %s ***" % (resultsFileName))
          file( resultsFileName, 'wb' ).write( zipFile.read( resultsFileName ) )
          zipFile.close()
        else:
          TraceMessage("'%s' aint no stinkin zip file!" % zipFileName)

      # Open the binary results file.
      resultsFile = open(resultsFileName,'rb')
    else:
      msg = "ERROR parseresults.py:  Input results file does not exist --> %s" % resultsFileName
      return(1,msg)

    # Do not load error codes/descriptions or messages file when DEXRPT is running or if only parametric results are produced
    if self.paramResultsOnly == 0 and self.userOptions.get("dexrpt",0) == 0:
      self.supportFiles['errorCodes'] = self.loadErrorCodeDesc()
      self.supportFiles['firmwareMsgs'] = self.loadFirmwareMessages()

    resultsFile.seek(0, 2) # last byte
    resultsFileTotalBytes = resultsFile.tell()
    resultsFile.seek(0, 0) # byte0
    thisRecordNumber = 0

    # While not EOF & not "FOF Final Error Code"
    while resultsFile.tell() < resultsFileTotalBytes:

      thisRecordByte0 = resultsFile.tell()
      thisRecordNumber += 1

      # Error msg to be used throughout this method
      self.errorMsg = "\nERROR in %s's %s()\n" % (os.path.basename(__file__), __name__)
      self.errorMsg = "%s           %s testRecord #%i @ byte %i [%s] of %i\n" % (self.errorMsg, resultsFileName, thisRecordNumber, thisRecordByte0, hex(thisRecordByte0), resultsFileTotalBytes)
      self.errorMsg = "%s           data garbled, testRecord %i ignored.\n" % (self.errorMsg, thisRecordNumber)

      # Defines for the old 10 byte tester header
      # 2 bytes size, 4 bytes time, 1 byte 5 volt, 1 byte 12 volt, 1 byte temp, 1 byte collect parametric
      self.oldTesterHeaderFormat = '<HLbbbb'
      self.oldTesterHeaderSize = struct.calcsize(self.oldTesterHeaderFormat)

      # Defines for the new 4 byte tester header
      # 2 byte size, 1 byte results key, 1 byte collect parametric
      testerHeaderFormat = '<Hbb'
      testerHeaderSize = struct.calcsize(testerHeaderFormat)

      # Start off with the assumption this is a new style tester header
      testerHeader = resultsFile.read(testerHeaderSize)

      # Validate:  Did we actually read a full testerHeader?
      if len(testerHeader) != testerHeaderSize:
        msg = "ABORT: Invalid tester header.  received: %s bytes, expected: %s bytes" % (len(testerHeader),testerHeaderSize)
        return(2,self.errorMsg+msg)

      # Unpack the testerHeader.
      thisRecordSize,resultsKey,self.collectParametric = struct.unpack(testerHeaderFormat,testerHeader)

      # Verify the size field is accurate
      # max record size 549:  10 byte old tester header, 24 byte old firmware header,512 bytes data, 2 bytes firmware junk, 1 byte tester alignment byte
      # min record size 13: 4 bytes new tester header,5 bytes new firmware header, 2 bytes firmware CRC, 2 bytes tester CRC
      if thisRecordSize > 549 or thisRecordSize < 13:
        msg = "ABORT: Incorrect record size:  Size of record pulled from tester header: %s Expected size range: 13 - 549" % (thisRecordSize)
        return(3,self.errorMsg+msg)

      # Is this a new style tester header?

      # A results key of 7 is used by the scripts when writing a data block to set the sequence number; this data block uses a testNumber of -7
      if resultsKey in (2,3,7,16,17):
        # Read the remainder of the record
        restOfRecord = resultsFile.read(thisRecordSize-testerHeaderSize)

        # Get the tester CRC which is the last 2 bytes in the record
        crcFormat = ">H"
        crcSize = struct.calcsize(crcFormat)
        testerCRCCheck =  struct.unpack(crcFormat,restOfRecord[len(restOfRecord)-crcSize:])[0]

        # Calculate the tester CRC; CRC entire rec except for the tester CRC on the end
        rec = testerHeader + restOfRecord[:-crcSize]
        # Pass the same arbitrary seed value (604 == throwing missiles) as firmware & tester do to ensure a CRC of 0's does not equal 0
        crc = self.calcCRC(rec,len(rec),604)
        # CRC function returns a 32 bit value, but tester packs it into a 16 bit value so mask it to get a 16 bit value
        crc = crc & 0xFFFF

        # Compare our calculated CRC with the tester calculated CRC - if they match, this has to be a new style tester header
        if testerCRCCheck != crc:
          #TraceMessage("CRC Check does not match.  DEX CRC Check: %s Tester CRC Check %s" % (crc,testerCRCCheck))

          # There is a slim chance an old 10 byte header would be in this loop by mistake. If the CRC check fails, try to process the old style 34 byte header
          resultsFile.seek(thisRecordByte0)
          testerHeader = resultsFile.read(self.oldTesterHeaderSize)

          err,msg = self.processOldTesterHeader(testerHeader)
          if err:
            continue
          # Read the remainder of the record
          restOfRecord = resultsFile.read(thisRecordSize-self.oldTesterHeaderSize)
          # Chop off the alignment byte (also called runt block) the old CM code adds to the record
          restOfRecord = restOfRecord[:-1]
        else:
          # Pass the rest of the record but exclude the tester CRC Check
          # The callback does not know whether this record had old or new style tester header so
          # no way of knowing if the tester CRC check is on the end or not; remove CRC to simplify things
          restOfRecord = restOfRecord[:-crcSize]

      # resultsKey was not valid so this must be an old style 10 byte tester header
      else:
        resultsFile.seek(thisRecordByte0)
        testerHeader = resultsFile.read(self.oldTesterHeaderSize)
        err,msg = self.processOldTesterHeader(testerHeader)
        if err:
          continue
        # Read the remainder of the record
        restOfRecord = resultsFile.read(thisRecordSize-self.oldTesterHeaderSize)
        # Chop off the alignment byte (also called runt block) the old CM code adds to the record
        restOfRecord = restOfRecord[:-1]

      # Regardless of old or new style tester header, the collect parametric flag needs to go through this code
      # cm code defaults spc_id to a 0 and user scripts can write a 0.  Only way to tell who wrote the 0 is this flag
      # If cm wrote the 0, default spc_id to None which is also the default the cm code uses for the 32 bit spc_id
      if not (self.collectParametric & 0x40):
        self.collectParametric = None

      if self.collectParametric:
        self.collectParametric = self.collectParametric & 0x0F

      # Validate:  Size of record must be greater than new firmware header (5 bytes) plus the 2 bytes firmware CRC
      if len(restOfRecord) < 7:
        msg = "WARNING: Record size mismatch.  Record must at least be length of firmware header.  Len of firmware header: %s Expected size: > 7" % (len(restOfRecord))
        TraceMessage(self.errorMsg+msg)
        continue

      # Results data coming back from the drive has a one-byte prefix (results key).  WinFOF calls resultsCallBack() passing firmware data
      # so the 1 byte prefix will exist.  Simulate that here by prefixing 1 space character so resultsCallBack() does not need to determine orgin
      ResultsParser.resultsCallBack(" " + restOfRecord,collectParametric=self.collectParametric,currentTime=self.currentTime)

    TraceMessage("DONE!  %i Test Record(s) Processed:" % thisRecordNumber)
    if self.failingTestSignature != {}: # found "FOF Final Error Code"
      TraceMessage("       %i total %s bytes (100%s)" % (resultsFileTotalBytes, resultsFileName, "%"))
    else: # print file pos. (byte) of last record looked at
      TraceMessage("       @ byte %i [%s] of %i %s bytes" % (thisRecordByte0, hex(thisRecordByte0), resultsFileTotalBytes, resultsFileName))

    resultsFile.close()
    # if resultsFile in .ZIP, del .r##
    if( zipFileName != "" ):
      os.remove( resultsFileName )

    # Do not create P_EVENT_SUMMARY parametric table when DEXRPT is running or if only text results are produced
    if self.textResultsOnly == 0 and self.userOptions.get("dexrpt",0) == 0:
      self.writeEventSummaryParametricTable()

    # For DEXRPT, only create TEST_TIME_BY_TEST table when overridden with the user option
    # For DEX, TEST_TIME_BY_TEST table will always be created in the XML file.  Only create in the text file when overridden by user option
    if self.userOptions.get("dexrpt",0) and self.userOptions.get("printTestTimeByTest",0) or self.textResultsOnly == 0 and self.userOptions.get("dexrpt",0) == 0 or self.userOptions.get("testTimeTable",0):
      self.writeTestTimeParametricTable()

    # Do not write error code & description when DEXRPT is running or if only parametric results are produced
    if self.paramResultsOnly == 0 and self.userOptions.get("dexrpt",0) == 0:
      if self.failingTestSignature:
        self.resultsHandlers.writeToTextFile("\nCompletion Code: %s\n" % self.failingTestSignature["errorCode"])
        try:
          self.resultsHandlers.writeToTextFile("%s\n" % self.supportFiles['errorCodes'][self.failingTestSignature["errorCode"]])
        except:
          if VERBOSE:
            traceback.print_exc()
      else:
        self.resultsHandlers.writeToTextFile("\nCompletion Code: 0\n")

    # Script ignores most errors (would rather have some of the XML/text results than none)
    # This is just a check that the script ran OK based on file size of output files
    stat = 0
    try:
      # Do not check file size on a Windows system;  Windows does not do file writes immediately unless the fsync command is
      # used with every write/flush combo - fsync slows down DEX by a factor of ~10 due to virus scanner
      if os.name == "posix":
        xmlSize,textSize = self.resultsHandlers.getResultsFileSizes()
        if not self.textResultsOnly:
          # 18 is the size of the xml file with only the FIS required beginning tag, <parametric_dblog>, in it
          if xmlSize <= 18:
            msg = "ERROR parseresults.py:  Parametric results file does not contain any DBLog data; XML file size (%s)" % xmlSize
            stat = 1
        # 20 is the approximate size of the text results file with only the DBLog version at the top
        if not stat and not self.paramResultsOnly and textSize <= 20:
          msg = "ERROR parseresults.py:  Text results file does not contain any DBLog data; Text file size (%s)" % textSize
          stat = 2
    except:
      if VERBOSE:
        TraceMessage("parseresults.py:  Problem finding results file sizes")
        traceback.print_exc()

    if stat:
      TraceMessage("%s,%s" % (stat,msg))
      return(stat,msg)

    return(0,"OK")


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# _main_()?
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Run from a Gemini script environment
# Create a global singleton ResultsParser object.
ResultsParser = _ResultsParser()
