#!/usr/bin/env fofpython
# --------------------------------------------------------------------------------------- #
#                                                                                         #
#                                   Seagate Confidential                                  #
#                                                                                         #
# --------------------------------------------------------------------------------------- #

# ******************************************************************************
#
# VCS Information:
#                 $File: //depot/TCO/DEX/dex.py $
#                 $Revision: #4 $
#                 $Change: 449292 $
#                 $Author: alan.a.hewitt $
#                 $DateTime: 2012/04/30 11:29:44 $
#
# ******************************************************************************

import getopt,string,traceback,sys,time,os
from parseresults import ResultsParser,VERSION


if __name__ == "__main__":

  startTime = time.time()


  # Define a usage summary function
  def usage(errMsg=""):
    msg = """
    ***********************************************************************************
    DEX VERSION: %s

    USAGE:  dex.py -i resultsFile -d dir -n outputFileName -c paramFile -e errorCodeFile -f pErrorCodeFile -m messages -t -p -s -b
    WHERE:

    OPTION  ARGUMENT        DESCRIPTION

      -i    resultsFile     mandatory; path to and name of binary/ASCII results file
 				       NOTE: if running on a Windows Box, and path/file contains spaces use ""
				       (e.g. dexrpt -i "c:\\bin logs\\1az888x0.r01" -d "c:\\my data")
      -d    dir             optional;  directory to save parametric & text output files in
      -n    outputFileName  optional;  file name for text file
      -c    paramFile       optional;  path to and/or name of parameter file
      -t                    optional;  only output text file
      -p                    optional;  only output parametric file
      -s                    optional;  collect parametric data on tests regardless of whether spc id is set
      -e    errorCodeFile   optional;  path to and/or name of error code file
      -f    pErrorCodeFile  optional;  path to and/or name of process error code file
      -m    messagesFile    optional;  path to and/or name of messages file
      -b                    optional;  print the TEST_TIME_BY_TEST parametric table to the text results file
                                       this option can not be used with the -p option
      -a                    optional;  print all tables & colums
                                       (added to support CO tables written directly to results file as XML)
      -g                    optional;  open the text file as 'wb' instead of 'w'.  On a Windows system, when the file is
                                       opened in the default mode, any CR in the binary/ASCII file will be replaced by a
                                       CRLF in the text file and line endings will typically be CRLF.  Using'wb' mode, a
                                       CR will be a CR and line endings will be CR.  This option only works when running
                                       DEX stand alone.
      -h                    optional;  print help menu
      -v                    optional;  report DEX Version Number

    Python 2.2.3 or newer is required to run DEX!

    DEFAULT BEHAVIOR:
      - both a parametric and a text result file are created; -t & -p override this
      - output files are saved with same name as input file; -n overrides this
      - output files are saved in dir script is run from; -d overrides this
      - parameter file path is dir script is run from; -c can override this
      - parameter file name is 'param_cd.h'; -c can override this
      - parametric data is only collected on tests with spc id set; -s will override this;
        the presence of tablematrix.py will also override this.  If present, only the
        table codes & spc_ids listed in the file will be written to the XML file.
      - error code file name is 'codes.h'; -e can override this
      - error code file path is dir script is run from; -e can override this
      - process error code file name is 'proc_codes.h'; -f can override this
      - process error code file path is dir script is run from; -f can override this
      - messages file is called 'messages.h'; -m can override this
      - messages file path is dir script is run from; -m can override this

    EXAMPLES:
      dex.py -i /var/merlin/results/03-1.rp1
      dex.py -i 03-1.rp1 -n myFile.txt -t
      dex.py -i 03-1.rp1 -c /var/merlin/cfgs/anytest/params
    ***********************************************************************************
    """ % (VERSION)
    print msg
    if errMsg:
      print errMsg
      print ""
    sys.exit()


  def validateFile(userOptionsKey,defaultFileName):
    # Determine if file info passed in is valid
    if userOptions.has_key(userOptionsKey):
      if not os.path.isfile(userOptions[userOptionsKey]):
        if not os.path.isdir(userOptions[userOptionsKey]):
          errMsg = "ERROR:  %s is not a valid file or directory" % (userOptions[userOptionsKey])
          # Do not exit for this error as it is not critical for viewing text results
          print errMsg
        # If file path was passed in but not file name, assume a default file name
        else:
          userOptions[userOptionsKey] = os.path.join(userOptions[userOptionsKey],defaultFileName)
    # If file path/name was not passed in, assume current directory and default file name
    else:
      userOptions[userOptionsKey] = defaultFileName

  try:
    optList,argList = getopt.getopt(sys.argv[1:], 'i:d:n:c:e:f:m:thvpsbag')
  except:
    # Unrecognized option in list or not using required arg with option
    errMsg = "ERROR:  Invalid options"
    usage(errMsg)

  # Set up defaults
  myOptionList = []
  paramFileName = "param_cd.h"
  errorCodeFileName = "codes.h"
  procErrorCodeFileName = "proc_codes.h"
  messagesFileName = "messages.h"
  userOptions = {}

  for option,args in optList:
    # The user must pass the name of the binary results file.
    if option == "-i":
      resultsFileName = args
    # Directory the results files should be put in
    elif option == "-d":
      userOptions["outputFileDir"] = args
    # Only output a text results file; not a parametric xml file
    elif option == "-t":
      userOptions["textResultsOnly"] = 1
    # File name for the text output file; FIS requires this option
    elif option == "-n":
      userOptions["textFileName"] = args
    # Only output a parametric xml file; not a text results file
    elif option == "-p":
      userOptions["paramResultsOnly"] = 1
    # Path to and/or name of parameter file
    elif option == "-c":
      userOptions["paramFile"] = args
    # Display help
    elif option == "-h":
      usage()
    # report DEX version
    elif option == "-v":
      print "DEX Version: %s" % VERSION
      sys.exit()
    # Collect parametric data irregardless of spc id
    elif option == "-s":
      userOptions["ignoreSpcId"] = 1
    # Path to and/or name of error code file
    elif option == "-e":
      userOptions["errorCodeFile"] = args
    # Path to and/or name of process error code file
    elif option == "-f":
      userOptions["procErrorCodeFile"] = args
    # Path to and/or name of messages file
    elif option == "-m":
      userOptions["messagesFile"] = args
    # Print the TEST_TIME_BY_TEST parametric table to the text results file
    elif option == "-b":
      userOptions["testTimeTable"] = 1
    # Print All Tables and Columns
    elif option == "-a":
      userOptions["parseAllTables"] = 1
    # Open the text results file in 'wb' mode
    elif option == "-g":
      userOptions["openWBMode"] = 1

    myOptionList.append(option)

  # Check options against a list of mandatory options
  for opt in ["-i"]:
    if opt not in myOptionList:
      errMsg = "ERROR:  %s is a mandatory argument" % (opt)
      usage(errMsg)

  # -b option can not be used when only an XML file is created
  if userOptions.get("testTimeTable",0) and userOptions.get("paramResultsOnly",0):
    errMsg = "ERROR: Options for parametric results only (-p) and writing TEST_TIME_BY_TEST table to text file (-b) conflict"
    usage(errMsg)

  if not os.path.exists(resultsFileName):
    resultsFileName = resultsFileName + '.zip'
    if not os.path.exists(resultsFileName):
      errMsg = "ERROR:  File %s does not exist" % (resultsFileName)
      usage(errMsg)

  if userOptions.has_key("outputFileDir") and not os.path.exists(userOptions["outputFileDir"]):
    os.mkdir(userOptions["outputFileDir"])

  # Determine if file info passed in is valid or if defaults should be used
  validateFile("paramFile", paramFileName)
  validateFile("errorCodeFile", errorCodeFileName)
  validateFile("procErrorCodeFile", procErrorCodeFileName)
  validateFile("messagesFile", messagesFileName)

  # Find the file name to pass so the output files can use the same name as the input file
  try:
    head,tail = os.path.split(resultsFileName)
    userOptions["outputFileName"],fileExtension = tail.split(".",1)
  except:
    errMsg = "ERROR:  Not a valid results file name %s" % (resultsFileName)
    usage(errMsg)

  if userOptions.get("textResultsOnly",0) and userOptions.get("paramResultsOnly",0):
    errMsg = "ERROR:  Options indicate neither a parametric or text results file should be produced"
    usage(errMsg)

  ResultsParser.createDEXHandlers(userOptions,startTime)

  # We must tell the embedded/shared callback function to NOT save the results to the results file.
  ResultsParser.saveToResultsFile = 0

  errNum, errMsg = ResultsParser.processResultsFile(resultsFileName)
  print "DEX Run-Time errorCode: ", errNum, errMsg
