# --------------------------------------------------------------------------------------- #
#                                                                                         #
#                                   Seagate Confidential                                  #
#                                                                                         #
# --------------------------------------------------------------------------------------- #

# ******************************************************************************
#
# VCS Information:
#                 $File: //depot/TCO/DEX/viewerextractors.py $
#                 $Revision: #4 $
#                 $Change: 430710 $
#                 $Author: alan.a.hewitt $
#                 $DateTime: 2012/02/28 13:08:43 $
#
# ******************************************************************************
import struct, string

from tabledictionary import *

# Table code pulled from results file
tableCode = 0
colNameList = []
colWidthTuple = ( )
dummyDataList = []


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# grab tableCode from resultsData coming back from initiator
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def getTableCode( resultsData ):
  # NOTE!!!  this function does not set global variables
  #          that resposnibility is left to the callling function

  errorFlag = False
  message = ""
  tableCode = "" # empty default

  try:
    tableCode = struct.unpack( "H", resultsData[:2] )[0] # value is a tuple so just grab the first part

  except:
    errorFlag = True
    message = "ERROR viewerextractors.py:  Problem extracting tableCode"

  return errorFlag, message, tableCode


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# grab tableDictionary info
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def getTableDictionaryInfo( thisCode="" ):
  # NOTE!!!  this function does not set global variables
  #          that resposnibility is left to the callling function

  global tableCode
  errorFlag = False
  message = ""
  tableNameString = "" # empty default
  colNameList = []     # empty default
  colWidthTuple = ()   # empty default

  if thisCode == "": # if no tableCode is passed in (i.e. local tableCode == "")...
    thisCode = tableCode # thisCode = global tableCode

  try: # grab table name, colNames & colWidths from tabledictionary.py's tableHeader[]
    tableNameString = tableHeaders[thisCode][0]
    colNameList = tableHeaders[thisCode][1].split( ',' ) # .split() string ", , , " -> list: ["","","", ]
    colWidthTuple = tableHeaders[thisCode][4] # ( , , , )
    if len( colNameList ) != len( colWidthTuple ):
      # message = "\nWARNING viewerextractors.py:  TableCode %s:  Num colNames [%i] <> Num colWidths [%i]" % ( thisCode, len( colNameList ), len( colWidthTuple ) )
      if len( colNameList ) < len( colWidthTuple ):
        # message += "\n        append %i dummy colNames" % ( len( colWidthTuple ) - len( colNameList ) )
        while len( colNameList ) < len( colWidthTuple ):
          colNameList += ["?"*3] # dummy colName
      else:
        # message += "\n        append %i default colWidths" % ( len( colNameList ) - len( colWidthTuple ) )
        while len( colNameList ) > len( colWidthTuple ):
          colWidthTuple += ( 10, ) # default colWidth  *** NEED COMMA to += tuple ***
      # resultsHandlers.writeToTextFile( message, 1 )

  except:
    errorFlag = True
    message = "ERROR viewerextractors.py:  Problem grabbing tabledictionary.py info for tableCode %s" % thisCode

  return errorFlag, message, tableNameString, colNameList, colWidthTuple


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# parse resultsData into list
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def getDataList( resultsData, startIndex=0, stopIndex=-1 ):
  global tableCode
  errorFlag = False
  message = ""
  dataList = []

  if stopIndex == -1:
    stopIndex = len(resultsData.split(','))

  try: # grab resultsData
    dataList = resultsData.split( ',' )

  except:
    errorFlag = True
    message = "ERROR viewerextractors.py:  Problem parsing resultsData for tableCode %s" % tableCode

  return errorFlag, message, dataList[ startIndex:stopIndex ]


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# match col counts ... num (global)colNames = num dataList
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def matchColCounts( dataList, nameList=[] ):
  # NOTE!!!  this function does not set global variables
  #          that resposnibility is left to the callling function
  global colNameList
  global colWidthTuple
  errorFlag = False
  message = ""

  if nameList == [""]:
    nameList = colNameList # if no colNameList passed in, default to global colNameList

  dummyDataList = [] # clear dummy data

  # match # of colNames to # colData
  if len( nameList ) != len( dataList ):
    # message = "\nWARNING viewerextractors.py:  TableCode %s:  Num colNames [%i] <> Num colWidths [%i]" % ( tableCode, len( nameList ), len( colWidthTuple ) )
    if len( nameList ) < len( dataList ):
      # message += "\n        append %i dummy colNames" % ( len( dataList ) - len( nameList ) )
      while len( nameList ) < len( dataList ):
        nameList += ["?"*3] # add dummy col Names
        colWidthTuple += ( 10, ) # default col width ***NEED COMMA***
    else:
      # message += "\n        append %i dummy Data" % ( len( nameList ) - len( dataList ) )
      while len( nameList ) > len( dataList ) + len( dummyDataList ): # add dummy data
        dummyDataList += ["?"*3]
    # resultsHandlers.writeToTextFile( message, 1 )

  return errorFlag, message, dummyDataList


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Format dataList according to the colWidths
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def formatData( colNameList, colWidthTuple, dataList ):

  errorFlag = False
  message = ""
  formattedData = ""

  # Loop through each data item & format with the correct width which comes from the imported dictionary
  for i in range( len( dataList ) ):
    try:
      # Constant width; signified by an asterik in the column names field
      if colNameList == ["*"]:
        thisWidth = colWidthTuple[0]
      else:
        # Check if length of test data is equal to the number of widths in the dictionary; if not equal, flag an error
        if i > len( colWidthTuple ):
          # message = "\nERROR viewerextractors.py:  Number of data elements ( %s ) n results file is not equal to number of columns ( %s ) in tableditionary.py/table_cd.h" % ( len( dataList ), len( colWidths ) )
          # Upon error, assume a width so the test data can still get written to the text file
          thisWidth = 10
        else:
          # Variable width
          thisWidth = colWidthTuple[i]

      # Format the data according to the width
      formattedData += ' %*s' % ( thisWidth, dataList[i] )

    except:
      errorFlag = True
      message = "ERROR viewerextractors.py:  Error formatting the data.  dataList[] = ", dataList

  return( errorFlag, message, formattedData )


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 11000 block code; contains table code & firmware data
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ViewerFirstBlock:

  def __call__( self, resultsData, testNumber, collectParametric, counters, resultsHandlers, *args, **kwargs ):
    global tableCode
    global colNameList
    global colWidthTuple
    global dummyDataList

    formattedData = resultsData # default return value, in case exceptions occur

    # Special case:  process scripts write block 11000 with testNumber of 9999 for parametric table P_EVENT_SUMMARY
    if testNumber != 9999:

      errorFlag, message, tableCode = getTableCode( resultsData ) # grab tableCode from resultsData
      if errorFlag:
        resultsHandlers.writeToTextFile( "\n" + message, 1 )
      else:
        errorFlag, message, tableNameString, colNameList, colWidthTuple = getTableDictionaryInfo( tableCode )
        if errorFlag:
          resultsHandlers.writeToTextFile( "\n" + message, 1 )
        else:
          errorFlag, message, dataList = getDataList( resultsData[2:] )
          if errorFlag:
            resultsHandlers.writeToTextFile( "\n" + message, 1 )

      if not errorFlag:
        txtData = "%s:" % tableNameString
        try: # write table name
          resultsHandlers.writeToTextFile( "", 1 ) # Write an empty line (return character) between tables
          resultsHandlers.writeToTextFile( txtData, 1 )
          formattedData = "%s:" % ( txtData )
        except:
          message = "\nERROR viewerextractors.py:  Block 11000:  Problem writing table name for tableCode %s" % tableCode
          resultsHandlers.writeToTextFile( message, 1 )


        if colNameList != ["*"]: # no column names if asterik
          # Match number of colNames & number of colData
          errorFlag, message, dummyDataList = matchColCounts( dataList, colNameList )

          try: # write column names but only if the column name is not an asterik
            errorFlag, message, txtData = formatData( colNameList, colWidthTuple, colNameList )
            if not errorFlag:
              resultsHandlers.writeToTextFile( txtData, 1 )
              formattedData += "\n%s" % ( txtData )
            if message:
              resultsHandlers.writeToTextFile( "%s for tableCode %s" % ( message, tableCode ), 1 )
          except:
            message = "\nERROR viewerextractors.py:  Block 11000:  Problem writing column names for tableCode %s" % tableCode
            resultsHandlers.writeToTextFile( message, 1 )
            resultsHandlers.writeToTextFile( str(colNameList), 1 )
            resultsHandlers.writeToTextFile( str(colWidthTuple), 1 )
            resultsHandlers.writeToTextFile( txtData, 1 )
        # Column name is an asterik
        else:
          # Clear the dummy data list so it does not contain left over data from matchColCounts()
          dummyDataList = []


      if not errorFlag:
        try: # write resultsData ( from initiator/firmware )
          errorFlag, message, txtData = formatData( colNameList, colWidthTuple, ( dataList + dummyDataList ) )
          if not errorFlag:
            resultsHandlers.writeToTextFile( txtData, 1 )
            formattedData += "\n%s" % ( txtData )
          if message:
            resultsHandlers.writeToTextFile( "%s for tableCode %s" % ( message, tableCode ), 1 )
        except:
          message = "\nERROR viewerextractors.py:  Block 11000:  Problem formatting & writing data for tableCode %s" % tableCode
          resultsHandlers.writeToTextFile( message, 1 )

    return formattedData


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 11002 block code; contains firmware data
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ViewerSubBlock:

  def __call__( self, resultsData, testNumber, collectParametric, counters, resultsHandlers, *args, **kwargs ):
    global tableCode
    global colNameList
    global colWidthTuple
    global dummyDataList
    formattedData = resultsData # default return value, in case exceptions occur

    errorFlag, message, dataList = getDataList( resultsData )
    if errorFlag:
      resultsHandlers.writeToTextFile( message, 1 )

    if not errorFlag:
      try: # write resultsData ( from initiator/firmware )
        errorFlag, message, txtData = formatData( colNameList, colWidthTuple, ( dataList + dummyDataList ) )
        if not errorFlag:
          resultsHandlers.writeToTextFile( txtData, 1 )
          formattedData += "\n%s" % ( txtData )
        if message:
          resultsHandlers.writeToTextFile( "%s for tableCode %s" % ( message, tableCode ), 1 )
      except:
        message = "\nERROR viewerextractors.py:  Block 11002:  Problem formatting & writing data for tableCode %s" % tableCode
        resultsHandlers.writeToTextFile( message, 1 )
        resultsHandlers.writeToTextFile( str( colNameList ), 1 )
        resultsHandlers.writeToTextFile( str( colWidthTuple ), 1 )
        resultsHandlers.writeToTextFile( str( dataList + dummyDataList ), 1 )


    return formattedData


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 11003 block code; contains table code & comma delimited data consisting of a string & an error code
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class FaultCode:
  def __call__( self, resultsData, testNumber, collectParametric, counters, resultsHandlers, iserOptions, paramNames, supportFiles, *args, **kwargs ):
    global tableCode
    global colNameList
    global colWidthTuple
    global dummyDataList
    formattedData = resultsData # default return value, in case exceptions occur


    errorFlag, message, tableCode = getTableCode( resultsData ) # grab tableCode from resultsData
    if errorFlag:
      resultsHandlers.writeToTextFile( message, 1 )
    else:
      errorFlag, message, tableNameString, colNameList, colWidthTuple = getTableDictionaryInfo( tableCode )
      if errorFlag:
        resultsHandlers.writeToTextFile( message, 1 )
      else: # write table name
        txtData = "%s:" % tableNameString
        try:
          resultsHandlers.writeToTextFile( "", 1 ) # Write an empty line (return character) between tables
          resultsHandlers.writeToTextFile( txtData, 1 )
          formattedData = "%s:" % ( txtData )
        except:
          message = "\nERROR viewerextractors.py:  Block 11003:  Problem writing table name for tableCode %s" % tableCode
          resultsHandlers.writeToTextFile( message, 1 )
          errorFlag = True

        if not errorFlag: # write column names but only if the column names
          errorFlag, message, dataList = getDataList( resultsData[2:] )
          if errorFlag:
            resultsHandlers.writeToTextFile( message, 1 )
          else:
            errSource = dataList[0] # 1st element = errSource
            errCode = dataList[1] # 2nd element = errCode
            eCodesExceptionFlag = False
            try:
              errDescription = supportFiles['errorCodes'][int( errCode )]
            except:
              errDescription = "???"
              eCodesExceptionFlag = True
            colWidthTuple = colWidthTuple[:2] + (max(len(colNameList[2]), len(errDescription)),) + colWidthTuple[3:]    # Set column width of error description to match length of column name or length of description string, whichever is longer.
            if len(dataList) > 2:  # Optional error message supplied.
               optionalErrorMessage = ': ' + dataList[2];  # Add a : delimiter to improve readability.
               dataList = list( (errSource, errCode, errDescription, optionalErrorMessage) )
               colWidthTuple = colWidthTuple[:3] + (max(len(colNameList[3]), len(optionalErrorMessage)),) + colWidthTuple[4:]    # Set column width of optional error message to match length of column name or length of message string, whichever is longer.
            else:
               dataList = list( (errSource, errCode, errDescription) )
               colNameList = colNameList[:3]

          try:
            errorFlag, message, txtData = formatData( colNameList, colWidthTuple, colNameList )
            if not errorFlag:
              resultsHandlers.writeToTextFile( txtData, 1 )
              formattedData += "\n%s" % ( txtData )
            if message:
              resultsHandlers.writeToTextFile( "%s for tableCode %s" % ( message, tableCode ), 1 )
          except:
            message = "\nERROR viewerextractors.py:  Block 11003:  Problem writing column names for tableCode %s" % tableCode
            resultsHandlers.writeToTextFile( message, 1 )
            errorFlag = True

    if not errorFlag:
       # write errSource, errCode & errDescription
       errorFlag, message, txtData = formatData( colNameList, colWidthTuple, dataList )
       if not errorFlag:
         resultsHandlers.writeToTextFile( txtData, 1 )
         formattedData += "\n%s" % txtData

       if eCodesExceptionFlag:
         message = "\nERROR viewerextractors.py:  Block 11003:  No description available for error code: %s" % ( errCode )
         resultsHandlers.writeToTextFile( message, 1 )

    return formattedData

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 11004 block code; contains message code which needs to be looked up in messages support file
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class FirmwareMessage:

  def __call__( self, resultsData, testNumber, collectParametric, counters, resultsHandlers, iserOptions, paramNames, supportFiles, *args, **kwargs ):

    formattedData = resultsData # default return value, in case exceptions occur

    try:
      # Grab the message code from the data; value is a tuple so just grab the first part
      messageCode = resultsData

      try:
        message = supportFiles['firmwareMsgs'][int( messageCode )]
      except:
        message = "\nERROR viewerextractors.py:  Block 11004:  No description available for message code: %s" % ( messageCode )
        resultsHandlers.writeToTextFile( message, 1 )
        message = ""

      if message:
        formattedData = "\nFW: %s" % message
        resultsHandlers.writeToTextFile( formattedData, 1 )
    except:
      message = "\nERROR viewerextractors.py:  Block 11004:  Problem decoding message code & writing message"
      resultsHandlers.writeToTextFile( message, 1 )

    return formattedData


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 3065 block code; contains firmware test parameter data.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class TestParameters:

   def __call__( self, resultsData, testNumber, collectParametric, counters, resultsHandlers, userOptions, paramNames, *args, **kwargs ):
      parameterLine = ""

      try:
         # Grab the table code; value is a tuple so just grab the first part
         parameterValueIndex = struct.unpack( "H", resultsData[0:2] )[0]
         parameterValueCount = struct.unpack( "H", resultsData[2:4] )[0]
         parameterNameCode = struct.unpack( "H", resultsData[4:6] )[0]
         parameterValueType = resultsData[6]

      except:
         message = "\nERROR viewerextractors.py:  Block 3065:  Problem unpacking header data"
         # print message
         resultsHandlers.writeToTextFile( message, 1 )

      try:
        # If param code file could not be read in, paramNames will be None
        if parameterValueIndex == 0 and paramNames != None:  # First value for this named parameter
           parameterLine = "\n%26s " % paramNames[parameterNameCode]  # Initialize to parameter name string from definition file.
           resultsHandlers.writeToTextFile( parameterLine, 0 )  # Write to results text file without a trailing CR/LF
        if parameterValueCount > 0:  # Add parameter value(s) if not a boolean.
           if parameterValueType == 'l':
              parameterValue = struct.unpack( "L", resultsData[7:11] )[0]  # Get 4 byte integer value
              parameterValueString = "%10u (0x%08lx)" % ( parameterValue, parameterValue )
           elif parameterValueType in "cd":
              parameterValue = struct.unpack( "H", resultsData[7:9] )[0]  # Get 2 byte unsigned integer value
              parameterValueString = "%10u (0x%04x)" % ( parameterValue, parameterValue )
           elif parameterValueType in "fi":
              parameterValue = struct.unpack( "h", resultsData[7:9] )[0]  # Get 2 byte integer value
              parameterValueString = "%10d (0x%04x)" % ( parameterValue, parameterValue )
           elif parameterValueType == 'q':
              parameterValue = struct.unpack( "Q", resultsData[7:15] )[0]  # Get 8 byte integer value
              parameterValueString = "%10u (0x%016lx)" % ( parameterValue, parameterValue )
           else:
              message = "\nERROR viewerextractors.py:  Unrecognized parameter value type %c" % parameterValueType
              resultsHandlers.writeToTextFile( message, 1 )

           parameterLine = parameterValueString  # Add parameter values to the output string
           resultsHandlers.writeToTextFile( parameterLine, 0 )  # Write to results text file without a trailng CR/LF
      except:
        message = "\nERROR viewerextractors.py:  Block 3065:  Problem decoding test parameters for parameter name code: %s" % ( parameterNameCode )
        # print message
        resultsHandlers.writeToTextFile( message, 1 )

      return parameterLine


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# -44 block code; contains script comment written by user scripts or CM code
# 4002 ( write terminated string ) & 4003 ( write non-terminated string ) block codes from firmware
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ScriptComment:

  def __call__( self, resultsData, testNumber, collectParametric, counters, resultsHandlers, *args, **kwargs ):
    # Replace the nul character otherwise text file looks funny
    resultsData = resultsData.replace( "\00", "" )
    resultsHandlers.writeToTextFile( resultsData )
    return resultsData


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 4000 block code from firmware; write newline(s) to text file
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class WriteNewLine:

  def __call__( self, resultsData, testNumber, collectParametric, counters, resultsHandlers, *args, **kwargs ):
    count = struct.unpack( "i", resultsData[0:4] )
    resultsHandlers.writeToTextFile( "\n"*count )
    return resultsData


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 4001 block code from firmware; write space(s) to text file
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class WriteSpace:

  def __call__( self, resultsData, testNumber, collectParametric, counters, resultsHandlers, *args, **kwargs ):
    count = struct.unpack( "i", resultsData[0:4] )
    resultsHandlers.writeToTextFile( " "*count )
    return resultsData
