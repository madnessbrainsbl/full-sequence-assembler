# --------------------------------------------------------------------------------------- #
#                                                                                         #
#                                   Seagate Confidential                                  #
#                                                                                         #
# --------------------------------------------------------------------------------------- #

# ******************************************************************************
#
# VCS Information:
#                 $File: //depot/TCO/DEX/resultshandlers.py $
#                 $Revision: #3 $
#                 $Change: 449292 $
#                 $Author: alan.a.hewitt $
#                 $DateTime: 2012/04/30 11:29:44 $
#
# ******************************************************************************
import os
from tabledictionary import tableRevision
import fnmatch

# Define TraceMessage if we are not running in the Gemini script environment.
try:     TraceMessage
except:  
  def TraceMessage(msg): print msg

ENCODING = 'cp1252'     # the default encoding to use when printing unicode....
class Stream:
    """An object that caches a stream as a class variable.
    If given a wax TextBox it will write the value to it."""
    displayMsgFunc = None
    PortId = None
    def __init__(self, err=False):
        self.is_err = err
####################################################################        
    def write(self, line):
        #line = "%s "%time.time() + line
        if isinstance(line, unicode):
           line = line.encode(ENCODING)
        if Stream.displayMsgFunc and Stream.PortId:
           #Stream.displayMsgFunc(line)
           #Stream.displayMsgFunc.put((line,0))
           Stream.displayMsgFunc.send((line,0,Stream.PortId))
        else: print line,            
####################################################################      
    def flush(self):
        pass
####################################################################    
    def writelines(self, inline):
        for line in inlines:
            self.write(line)
####################################################################
    def close(self):
        pass
####################################################################
    #def __getattr__(self, attribute):
    #    if not self.__dict__.has_key(attribute) or attribute == '__doc__':
    #        return getattr(self.stream, attribute)
    #    return self.__dict__[attribute]
####################################################################

class ResultsHandlers:  
  
  def __init__(self,userOptions,dexVersion="",startTime=0):
    self.startTime = startTime
    
    self.textResultsOnly = userOptions.get("textResultsOnly",0)    # Variable to indicate whether only the text results should be produced
    self.paramResultsOnly = userOptions.get("paramResultsOnly",0)  # Variable to indicate whether only the parametric results should be produced 
    self.openWBMode = userOptions.get("openWBMode",0)              # Variable to indicate if the text file should be opened in 'wb' mode 
    outputFileDir = userOptions.get("outputFileDir", "")
    textFileName = userOptions.get("textFileName","")
    outputFileName = userOptions.get("outputFileName")
    winFOFInstance = userOptions.get("winFOFInstance")
    
    # Do not deal with parametric counters when only a text file is created unless user has chosen option to have TEST_TIME_BY_TEST table written to text file
    if not self.textResultsOnly or userOptions.get("testTimeTable",0):
      self.setDefaults()        
      # Seq num the script registered last
      self.lastSeqNum = ""
    
    # Only import parametric tools if necessary
    if not self.textResultsOnly:
      import parametricextractors
      parametricHandlers = {
           # Parametric block handlers
           -7   : [parametricextractors.StartSeq()],
          11000 : [parametricextractors.ParametricFirstBlock(),],
          11002 : [parametricextractors.ParametricSubBlock(),],
      }
    
    # Only import text tools if necessary
    if not self.paramResultsOnly:
      import viewerextractors               
      viewerHandlers = {
           # Viewer block handlers
            3065 : [viewerextractors.TestParameters()],
             -44 : [viewerextractors.ScriptComment(),],
            4000 : [viewerextractors.WriteNewLine(),],
            4001 : [viewerextractors.WriteSpace(),],
            4002 : [viewerextractors.ScriptComment(),],
            4003 : [viewerextractors.ScriptComment(),],
           11000 : [viewerextractors.ViewerFirstBlock(),],
           11002 : [viewerextractors.ViewerSubBlock(),],
           11003 : [viewerextractors.FaultCode(),],
           11004 : [viewerextractors.FirmwareMessage(),],
      }
    
    if self.paramResultsOnly:
      self.resultsHandlers = parametricHandlers
    else:    
      self.resultsHandlers = viewerHandlers
    
    # If both XML parametric and text output files are going to be produced, combine both individual handlers into one main handler
    if not self.textResultsOnly and not self.paramResultsOnly:
      for key,value in parametricHandlers.items():
        # If main handler already has key, add the values together to create one dictionary entry
        if self.resultsHandlers.has_key(key):
          self.resultsHandlers[key] = self.resultsHandlers[key] + parametricHandlers[key]
        else:
          self.resultsHandlers[key] = value
 
    # Set up the parametric output file if necessary
    if self.textResultsOnly == 1:
      self.xmlResultsFile = None
    else:
      try:
        # Use a Script Service if running in the Gemini script environment
        # File must be opened in append mode; while firmware is transitioning to dblog style data, users must 
        # run STPGPD first and dblog second so this script must append to the XML file that STPGPD creates
        XmlResultsFile.open('a')
        self.xmlResultsFile = XmlResultsFile
      except:
        # Used when running stand alone from the command line
        # Filename will be the same as the input results file name
        # Output dir may be passed in by user, otherwise defaults to directory script is run from
        fileName = "%s.xml" % outputFileName.lower()
        self.parametricFile = os.path.join(outputFileDir,fileName) 
        # Use write mode so any existing file is truncated
        self.xmlResultsFile = open(self.parametricFile,'w')  
      
      # Host code expects this tag at the beginning of the dblog data and a corresponding ending tag
      self.xmlResultsFile.write("<parametric_dblog>")
      self.xmlResultsFile.flush()
            
    # Set up the text output file if necessary
    if self.paramResultsOnly == 1:
      self.txtResultsFile = None
    else: 
      try:
        # WINFOF - Stream output to screen
        if winFOFInstance: 
          self.txtResultsFile = Stream()
        else:
          # Use a Script Service if running in the Gemini script environment
          TextResultsFile.open()
          self.txtResultsFile = TextResultsFile
      except:
        # Used when running stand alone from the command line
        # Filename will be the same as the input results file name unless user passed in a file name 
        # Output dir may be passed in by user, otherwise defaults to directory script is run from
        if textFileName:
          fileName = textFileName
        else:
          fileName = "%s.txt" % outputFileName.lower()
        self.viewerFile = os.path.join(outputFileDir,fileName)
        # Use write mode so any existing file is truncated
        if self.openWBMode:
           self.txtResultsFile = open(self.viewerFile,'wb')
        else:
           self.txtResultsFile = open(self.viewerFile,'w')

      # Write DEX version & dictionary revisions at the top of the results file
      self.txtResultsFile.write("DEX Version: %s \n" % dexVersion)
      self.txtResultsFile.write("Dictionary Rev: %s\n" % tableRevision)
      self.txtResultsFile.write("~"*76 + "\n")
      self.txtResultsFile.flush()
  
  
  def setDefaults(self):
    self.seqOccurrence = 1             # Incremental counter of every test within a seq
    self.testSeqEventDict = {}         # Dict to hold count of each specific test within a seq; i.e. count of test 126's run
    self.scriptOccurrence = 1          # Incremental counter of every test within a script
    self.testScriptEventDict = {}      # Dict to hold count of each specific test within a script
    self.failureHeader = {}            # Header that contains data for each failing test   
    
  
  def getResultsFileSizes(self):
    try:
      # Use Script Services to get the results file sizes
      if self.textResultsOnly == 1:
        return(0,self.txtResultsFile.size())
      elif self.paramResultsOnly == 1:
        return(self.xmlResultsFile.size(),0)
      else:
        return(self.xmlResultsFile.size(),self.txtResultsFile.size())
    except AttributeError:
      from stat import ST_SIZE
      # Get file sizes when running stand alone from command line
      if self.textResultsOnly == 1:
        return(0,os.stat(self.viewerFile)[ST_SIZE])
      elif self.paramResultsOnly == 1:
        return(os.stat(self.parametricFile)[ST_SIZE],0)
      else:
        return(os.stat(self.parametricFile)[ST_SIZE],os.stat(self.viewerFile)[ST_SIZE])
  
        
  # Write data to the parametric output file
  def writeToParametricFile(self,data):
    if data:
      self.xmlResultsFile.write(data)
      # Add carriage return & line feed required by FIS
      self.xmlResultsFile.write("\n")
      # Flush data from buffer to the disk
      self.xmlResultsFile.flush()
    
    
  # Write data to text output file 
  def writeToTextFile(self,data,returnChar=0):
    self.txtResultsFile.write(data)
    # Add carriage return & line feed 
    if returnChar == 1:
      self.txtResultsFile.write("\n")  
    # Flush data from buffer to the disk
    self.txtResultsFile.flush()
       
    
  def __del__(self):
    import time
    
    if self.paramResultsOnly == 0:
      scriptTime = time.time() - self.startTime
      msg = "DEX run time: %.3f " % scriptTime
      self.txtResultsFile.write(msg)
            
      try:      
        TraceMessage(msg)
      except:
        # With python-2.3 the garbage collection must be different
        # TraceMessage is not available at this point so it must be redefined
        try:  
          TraceMessage
        except:  
          def TraceMessage(msg): print msg
        TraceMessage(msg)

      self.txtResultsFile.close()
    
    if self.textResultsOnly == 0:
      self.xmlResultsFile.write("</parametric_dblog>")
      self.xmlResultsFile.flush()
      self.xmlResultsFile.close()
    
 
  def get(self,key):
    return self.resultsHandlers.get(key)
        
        
  def resetParamCounters(self,seq):
    # If the script is trying to register the same seq number twice in a row, ignore the second register
    # This could happen in a power loss recovery scenario because the results file is appended to
    if not self.lastSeqNum == seq:
      self.lastSeqNum = seq
     
      # Reset sequence counters
      self.testSeqEventDict = {}
      self.seqOccurrence = 1
     
      # Because counters are incremented after the test results are processed, default values for the first test in the seq must be returned
      return(self.scriptOccurrence,self.seqOccurrence, self.testSeqEventDict,self.failureHeader)
  
  
  def incrementParamCounters(self,testNum,errorCode):  
    # Increment the various counters that are needed for parametric data and populate a failure header if the test failed.  The failure
    # information is used for populating the P_EVENT_SUMMARY parametric table in case of a failing drive.
    
    if testNum >= 0:      
      try:
        # Increment counter that counts each event in the sequence
        self.seqOccurrence += 1
    
        # Increment counter that counts each event in the script
        self.scriptOccurrence += 1

        # Increment counter that counts the instances of a specific test within a seq
        # If dictionary does not have testNum key, will fall into the except clause
        try:
          self.testSeqEventDict[testNum] += 1
        except:
          self.testSeqEventDict[testNum] = 2
     
        # Increment counter that counts the instances of a specific test within a script
        try:
          self.testScriptEventDict[testNum] += 1
        except:
          self.testScriptEventDict[testNum] = 2
            
        # If test failed, set up the failure header which is used in the P_EVENT_SUMMARY table
        if errorCode != 0:            
          # Hardcode failing port ID to -1  
          # Subtract one from each since this function is called after the test has been processed & the counters were incremented above
          self.failureHeader[self.scriptOccurrence - 1] = (testNum, errorCode, self.seqOccurrence - 1, self.testSeqEventDict[testNum] - 1,self.testScriptEventDict[testNum] - 1,-1)
      except:
        TraceMessage("ERROR resultshandlers.py:  Can not increment the occurrence & test_seq_event parametric counters")
    return(self.scriptOccurrence,self.seqOccurrence, self.testSeqEventDict, self.failureHeader)
    
    
class RptResultsHandlers(ResultsHandlers):

  def __init__(self,userOptions,dexVersion="",startTime=0):
    self.fileExtension = "sum"
    
    outputFileName = userOptions.get("fileName")
    outputFileExtension = userOptions.get("fileExtension")
    self.outputFileDir = userOptions.get("outputFileDir","")
    self.startTime = startTime
    fileMode = userOptions.get("fileMode","w")
    inputFile = userOptions.get("inputFile","")
    
    # List of files objects used when user chooses to create a separate output file for each parametric table
    self.fileObjectList = []
    
    self.setDefaults() 
    
    # Seq num the script registered last
    self.lastSeqNum = ""  
    
    import rptextractors
    rptParametricHandlers = {
       # Parametric block handlers
      11000 : [rptextractors.RptParametricFirstBlock(),],
      11002 : [rptextractors.RptParametricSubBlock(),],
       -7   : [rptextractors.StartSeq()],
        }  
                    
    self.resultsHandlers = rptParametricHandlers
    
    if fnmatch.fnmatch(outputFileExtension,"*.zip"):
      outputFileExtension = outputFileExtension.split('.')[0]
    if not userOptions.get("singleOutputFile",0):
      # Filename will be identical to results file name; file extension will include the last 2 chars of the results file extension
      # to differentiate multiple files for 1 drive.  Dir could contain multiple results files for same serial number; 
      # each results file has SN as file name with an incremented extension (i.e r01,r02 etc)
      fileName = "%s.%s%s" % (outputFileName,self.fileExtension,outputFileExtension[1:])
    else:
      # If user chooses to have a single output file, do not use the results name file extension - this will result in multiple files
      fileName = "%s.%s" % (outputFileName,self.fileExtension)  
    # Output dir may be passed in by user, otherwise defaults to directory script is run from
    self.rptParametricFile = os.path.join(self.outputFileDir,fileName) 
    
    # Default mode is write so any existing file is truncated except when user chooses to put all
    # results in one file, then the file must be appended to
    self.rptResultsFile = open(self.rptParametricFile,fileMode) 
    
    # Write the input file location & file name 
    msg = "\n\nINPUT FILE: %s \n\n" % inputFile
    self.rptResultsFile.write(msg)
    self.rptResultsFile.flush()
      
    
  def __del__(self):
    import time
    
    scriptTime = time.time() - self.startTime
    msg = "\nDEXRPT run time: %.3f" % scriptTime
    TraceMessage(msg)
    
    self.rptResultsFile.write(msg)    
    self.rptResultsFile.flush()
    self.rptResultsFile.close()
    
    if self.fileObjectList:
      self.closeFile(self.fileObjectList)
         
    
  def getResultsFileSizes(self):
    from stat import ST_SIZE
    # Get file sizes when running stand alone from command line
    return(os.stat(self.rptResultsFile)[ST_SIZE],0)
    
        
  # Write data to the parametric report output file; this overrides method in ResultsHandlers class
  def writeToParametricFile(self,data):      
    self.rptResultsFile.write(data)
    # Add carriage return & line feed required by FIS
    self.rptResultsFile.write("\n")
    # Flush data from buffer to the disk
    self.rptResultsFile.flush()
    
    
  # Following functions are utilized when user chooses to create separate output files for each parametric table
  
  def checkFileExistance(self,fileName):
    existance = 0
    outputFile = os.path.join(self.outputFileDir,"%s.%s" % (fileName,self.fileExtension))
    if os.path.exists(outputFile):
      existance = 1
    return(existance)
  
  
  def openFile(self,fileName,fileMode="a"):    
    outputFile = os.path.join(self.outputFileDir,"%s.%s" % (fileName,self.fileExtension))
    fileObject = open(outputFile,fileMode)

    # Create a list so all files can be closed before the script exits
    self.fileObjectList.append(fileObject)

    return(fileObject)


  def writeFile(self,fileObject,data):
    fileObject.write(data)
    fileObject.write("\n")
    fileObject.flush()


  def closeFile(self,fileObjectList):
    for object in fileObjectList:
      object.flush()
      object.close()   
