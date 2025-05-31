#!/usr/bin/env python
# --------------------------------------------------------------------------------------- #
#                                                                                         #
#                                   Seagate Confidential                                  #
#                                                                                         #
# --------------------------------------------------------------------------------------- #

# ******************************************************************************
#
# VCS Information:
#                 $File: //depot/TCO/DEX/dexrpt.py $
#                 $Revision: #3 $
#                 $Change: 449292 $
#                 $Author: alan.a.hewitt $
#                 $DateTime: 2012/04/30 11:29:44 $
#
# ******************************************************************************

import traceback,getopt,string,sys,time,os,types,fnmatch,copy,datetime
from stat import ST_MTIME
from parseresults import ResultsParser,VERSION


usageMsg = """
    ***********************************************************************************************************************
    DEX VERSION: %s

    USAGE:  dexrpt.py -i results -t testNum -s startDate -e endDate -p spcId -n serialNumList -d outputDir -f outputFileName -o -l -v -b
    WHERE:

    OPTION  ARGUMENT        DESCRIPTION

      -i    results         mandatory; path to and name of binary/ASCII results file or path to
                                       directory where results files are located
                                       NOTE: if running on a Windows Box, and path/file contains spaces use ""
                                       (e.g. dexrpt -i "c:\\bin logs\\1az888x0.r01" -d "c:\\my data")
      -t    testNum         optional;  comma separated list of test numbers to collect data on
      -s    startDate       optional;  date from which to start searching for results file
                                       only applies when a directory is passed in with the -i option
                                       date must be in the form:  MM/DD/YY
      -e    endDate         optional;  date from which to stop searching for results file
                                       only applies when a directory is passed in with the -i option
                                       date must be in the form:  MM/DD/YY
      -p    spcId           optional;  comma separated list of spc ids to collect data on
      -n    serialNumList   optional;  path to and name of text file which contains a list of serial numbers
                                       -i option will be used for the path to the results files
                                       do not list the file extension; all results files with the given
                                       serial number as the file name will be parsed regardless of file extension
      -d    outputDir       optional;  directory to save output files in
      -f    outputFileName  optional;  name of file to store dexrpt results in
                                       if dexrpt is run against multiple results files, data from
                                       all results files will be written to this one output file
                                       with this option, the output file will always be appended to
      -o                    optional;  a separate output file will be created for each table; file name
                                       will be the table name; the table output file will always be appended to;
                                       output files by serial number will be created as well with the output file
                                       name being the input file name or the name passed in with -f option
      -l                    optional;  run against the most current result file per serial
                                       number (i.e 'Last Run Only' option in GUI)
      -v                    optional;  in addition to Oracle tables, also parse tables designated for the
                                       text file (viewer tables) only (i.e 'Parse All Tables' option in GUI)
      -b                    optional;  print the TEST_TIME_BY_TEST table to the main output file (either the
                                       default file or the file specified by the -f option)
                                       this table will get printed to its own table output file with the -o option
      -h                    optional;  prints help menu


    Python 2.3 or newer is required to run DEXRPT!

    DEFAULT BEHAVIOR:
      - only tables designated by firmware as Oracle (parametric) tables are parsed; -v (Parse All tables) overrides this
      - output files are saved with same name as input file; -f overrides this
      - output files are saved in the directory script is run from; -d overrides this

    EXAMPLES:
      dexrpt.py -i /var/merlin/results/03-1-0.rp1
      dexrpt.py -i 03-1-0.rp1 -t 107,175,1
      dexrpt.py -i /var/merlin/results -s 07/01/05 -e 08/01/05
    ***********************************************************************************************************************
    """ % (VERSION)

def parseArgsIntoList(args):
  # Convert the arguments passed in by the user to a list of ints
  argList = []
  myList = args.split(",")
  for item in myList:
    if not isinstance(item,types.IntType):
      item = int(item)
    argList.append(item)
  return argList

def parseArgsIntoStringList(args):
  # Convert the arguments passed in by the user to a list of strings
  argList = []
  myList = args.split(",")
  for item in myList:
    if not isinstance(item,types.IntType):
      item = str(item)
    argList.append(item)
  return argList


if __name__ == "__main__":

  # Define a usage summary function
  def usage(errMsg=""):
    print usageMsg
    print errMsg
    print "\n"
    sys.exit()

  def convertDate(date):
    try:
      mth,day,yr = date.split("/",2)
    except:
      usage("ERROR:  Invalid date, %s, Dates must be in the form MM/DD/YY\n" % date)
    # Started using datetime module in Jan 2010 and need a 4 digit year; only requiring users to enter the first two digits though
    if len(yr) == 2:
       yr = "20%s" % yr
    date = datetime.date(int(yr),int(mth),int(day))
    return(date)


  if sys.version[0:3] < '2.3':
    errMsg = "ERROR:  Python 2.3 or newer required to run!"
    usage(errMsg)

  try:
    optList,argList = getopt.getopt(sys.argv[1:], 'i:d:t:s:e:p:hf:n:olvab')
  except:
    # Unrecognized option in list or not using required arg with option
    traceback.print_exc()
    usage()

  # Set up defaults
  userOptions = {}
  myOptionList = []
  fileList = []
  startDate = ""
  endDate = ""
  outputFileName = ""
  serialNumFile = ""
  lastRunOnly = 0
  printTestTimeByTest = 0

  for option,args in optList:
    # The user must pass the path to and possibly the name of the binary results files.
    if option == "-i":
      resultsArg = args
    # Directory the results files should be put in
    elif option == "-d":
      userOptions["outputFileDir"] = args
    # List of test numbers to collect parametric data for
    elif option == "-t":
      userOptions["testNumList"] = parseArgsIntoList(args)
    elif option == "-s":
      startDate = args
    elif option == "-e":
      endDate = args
    elif option == "-p":
      userOptions["spcIdList"] = parseArgsIntoStringList(args)
    # Name to give the file produced by dexrpt
    elif option == "-f":
      outputFileName = args
      userOptions["singleOutputFile"] = 1
    # File containing a list of serial numbers
    elif option == "-n":
      serialNumFile = args
    # Display help
    elif option == "-h":
      usage()
    # Produce an output file for each parametric table
    elif option == "-o":
      userOptions["outputFilesByTable"] = 1
    # Collect data only on the last run
    elif option == "-l":
      lastRunOnly = 1
    # Parse viewer tables
    elif option == "-v":
      userOptions["parseViewerTables"] = 1
    # Print All Tables and Columns
    elif option == "-a":
      userOptions["parseAllTables"] = 1
      userOptions["ignoreSpcId"] = 1
    # Print TEST_TIME_BY_TEST table
    elif option == "-b":
      userOptions["printTestTimeByTest"] = 1

    myOptionList.append(option)

  # Check options against a list of mandatory options
  for opt in ["-i"]:
    if opt not in myOptionList:
      errMsg = "ERROR:  %s is a mandatory argument" % (opt)
      usage(errMsg)

  # Verify that the start & end dates are not greater than tomorrow (to account for time zone differences)
  tomorrowsDate = time.strftime("%m/%d/%y",time.gmtime(time.time()+24*60*60))
  tomorrowsDate = convertDate(tomorrowsDate)
  if startDate:
    startDate = convertDate(startDate)
    if startDate > tomorrowsDate:
      usage("Start date: %s can not be greater than tomorrows date: %s" % (startDate, tomorrowsDate))
  if endDate:
    endDate = convertDate(endDate)
    if endDate > tomorrowsDate:
      usage("End date: %s can not be greater than tomorrows date: %s" % (endDate, tomorrowsDate))
  if startDate and endDate:
    if startDate > endDate:
      usage("Start date: %s can not be greater than end date: %s" % (startDate, endDate))

  # If dir user passed in does not exist, create it
  outputFileDir = userOptions.get("outputFileDir","")
  if outputFileDir and not os.path.exists(outputFileDir):
    os.mkdir(outputFileDir)

  # If user passed in a file containing a list of serial numbers, turn the SNs into a list
  if serialNumFile:
    if os.path.isfile(serialNumFile):
      f=open(serialNumFile)
      serialNums = f.read()
      f.close()
      serialNumList = serialNums.split("\n")
    else:
      errMsg = "ERROR: Can not find file: %s containing list of serial numbers\n" % (serialNumFile)
      usage(errMsg)

  if os.path.isdir(resultsArg):

    # os.walk requires python 2.3 or newer!!
    for root,dirs,files in os.walk(resultsArg,True):

      for file in files:

        # If the file does not have a standard extension (ex: .r01 or .rp1) for a results file, skip it
        if not fnmatch.fnmatch(file,"*.r??") and not fnmatch.fnmatch(file,"*.zip"):
          continue

        filePath = os.path.join(root,file)

        # If user has passed in a date option
        if startDate or endDate:

          # If only a start date was passed in, assume end date is the current date
          if not endDate:
            endDate = time.strftime("%m/%d/%y",time.gmtime())
            endDate = convertDate(endDate)

          # Get the time of last modification for the file and format it
          fileAccessDate = time.strftime("%m/%d/%y",time.gmtime(os.stat(filePath)[ST_MTIME]))
          fileAccessDate = convertDate(fileAccessDate)

          # Skip file if file date does not fall within the given date range
          if (fileAccessDate < startDate) or (fileAccessDate > endDate):
            continue

        # If user passed in a file containing a list of serial numbers
        if serialNumFile:
          match = 0
          for name in serialNumList:
            # If serial number from the list matches one of the file names in the directory, append the file to the file list
            if name.find(".") != -1:
               # If serial number in file has an extension, it has to match the entire file name
               if name.upper() == file.upper():
                 match = 1
                 break
               zipName = name + '.zip'
               if zipName.upper() == file.upper():
                 match = 1
                 break
            else:
               # If the serial number in the file does not have an extension, it matches any file with that name regardless of extension
               if name.upper() == (file.split(".")[0]).upper():
                 match = 1
                 break

          # If there was not a match, move to the next file in the directory without appending the file to the file list
          if not match:  continue

        fileList.append(filePath)

  elif os.path.isfile(resultsArg):
    # Do not add the file to the list if it does not have a standard results file extension (ex: .r01 or .rp1)
    if fnmatch.fnmatch(resultsArg,"*.r??"):
      fileList.append(resultsArg)

  else:
    resultsArgZip = resultsArg +'.zip'
    if os.path.isfile(resultsArgZip):
      fileList.append(resultsArgZip)
    else:
      errMsg = "ERROR:  %s is not a valid directory or a results file" % (resultsArg)
      usage(errMsg)

  # Make a new list which contains only the last run for each serial number
  if lastRunOnly:
    fileDict = {}
    newList = []
    # Create list with time of last modification and full file name
    l = [(os.path.getmtime(x),x) for x in fileList]
    # Oldest files are at the beginning of the list after the sort
    l.sort()
    for modTime,file in l:
      try:
         name,extension = file.split(".")
      except:
         name,extension,zipExt = file.split(".")
      # Everytime it hits a file with the same name as a previous file, this will be overwritten
      # because the list is sorted, it should end up being the newest file (i.e last run) in the dictionary
      fileDict[name] = file
    # Create a list of files (file name including extension) from the dictionary
    for key in fileDict.keys():
      newList.append(fileDict[key])
    # Reset the original list variable
    fileList = []
    fileList = copy.deepcopy(newList)

  # Run DEX on all the files in the list
  for inputFile in fileList:
    userOptions["inputFile"] = inputFile
    startTime = time.time()

    try:
      # File name is typically a serial number
      head,tail = os.path.split(inputFile)
      userOptions["serialNum"],userOptions["fileExtension"] = tail.split(".",1)
    except:
      errMsg = "ERROR:  Not a valid input file name %s" % (inputFile)
      usage(errMsg)

    # If output file name was passed in as an arg, use it
    if outputFileName:
      userOptions["fileName"] = outputFileName
      # All results will be written to one file, so use append mode
      userOptions["fileMode"] = "a"
    # Otherwise output file name will be same as input file name
    else:
      # Use write file mode so existing files will be truncated
      userOptions["fileMode"] = "w"
      userOptions["fileName"] = userOptions["serialNum"]

    ResultsParser.rptCreateHandlers(userOptions,startTime)

    # We must tell the embedded/shared callback function to NOT save the results to the results file.
    ResultsParser.saveToResultsFile = 0

    ResultsParser.processResultsFile(userOptions["inputFile"])

    print "\nFinished parsing %s" % userOptions["inputFile"]
    del ResultsParser.resultsHandlers

  if not fileList:
    print "\nNo results files to process\n"
