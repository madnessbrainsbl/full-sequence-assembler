#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Contains script control functions
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/ScrCmds.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/ScrCmds.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
import os, stat, Utility
from types import DictType
import MessageHandler as objMsg
from Exceptions import CRaiseException
import traceback

#-----------------------------------------------------------------------------------------#
def statMsg(msg):
   if ConfigVars[CN].get('BenchTop', 0):  # for benchtop debugging only
      TraceMessage(msg)               #Print message to Trace Log
   ScriptComment(msg)                #Print message to Result File

def insertHeader(header, length = 80, headChar = "*", pad = 2):
   outHead = [headChar,] * length
   if header == "":
      pad = 0

   header = pad * " " + header + pad * " "
   insPt = (length/2) - (len(header)/2)
   outHead[insPt:insPt+len(header)] = list(header)

   strHead = "".join(outHead)
   statMsg(strHead)
   return strHead

#------------------------------------------------------------------------------------------------------#
def makeFailureData(errCode, errMsg):
   # On test failure: ScriptTestFailure throws data: ((test_name ,test_number, test_status, test_time), current_temp, (voltages))
   (mV3,mA3),(mV5,mA5),(mV12,mA12)  = GetDriveVoltsAndAmps()
   chamberTemp = ReportTemperature()/10.0
   voltages = (mV12/1000.0, mV5/1000.0)
   errInfo = (errMsg, 0, errCode, 0)
   failureData = (errInfo, chamberTemp, voltages)
   return failureData

#-----------------------------------------------------------------------------
def getFailureMessage(code, msg):
   import Failcode
   errCode, errMsg = Failcode.getFailCodeAndDesc(code)
   if msg:
      errMsg = msg  # override message with that supplied at runtime
   if type(errMsg) == DictType:
      errMsg = Utility.xmlHelper().dictToXML(errMsg)

   return errCode, errMsg

#-----------------------------------------------------------------------------
def raiseException(code, msg='', exceptionType = CRaiseException):
   """
      @param code: definition of error code as found in global Failcode list
      @param msg: if this argument is populated then it will override default error msg in global Failcode list
   """

   errCode, errMsg = getFailureMessage(code, msg)
   failureData = makeFailureData(errCode, errMsg)

   objMsg.printMsg('%s --- %s' % (errCode, errMsg),objMsg.CMessLvl.REPORTSTATUS & objMsg.CMessLvl.VERBOSEDEBUG)
   raise exceptionType(failureData)

#-----------------------------------------------------------------------------
def underLineTrace(strng):
   slen = len(strng)
   TraceMessage(strng)
   TraceMessage("-" * slen)
   return

#-----------------------------------------------------------------------------
def trcBanner(inputString = '',bannerLen=100):
   if bannerLen % 2:
      bannerLen += 1

   if len(inputString):
      #
      #  Add the input string to the banner
      #
      inputString = " " + inputString + " "

      newString = ""
      for i in inputString:
         newString = newString + " " + i

      slen = len(newString)

      if slen < bannerLen:
         TraceMessage("*" * bannerLen)
         prtString = "*" *  ((bannerLen - slen) / 2) + newString
         prtString = prtString + "*" * ((bannerLen - slen) / 2)
         TraceMessage(prtString)
         TraceMessage("*" * bannerLen)
      else:
         TraceMessage("*" * slen)
         TraceMessage(newString)
         TraceMessage("*" * slen)
   else:
      TraceMessage("*" * bannerLen)

#---------------------------------------------------------------------------------------------------------#
def getSystemScriptsPath():
   #if testSwitch.winFOF:
   #   path = UserScriptPath
   #   #path = os.path.join('C:\\','var','merlin','scripts',CN)
   #else:
   if testSwitch.virtualRun:
      #To allow override of nested product folders
      path = os.path.join(UserScriptPath)
   else:
      path = os.path.join(UserScriptPath, CN)
   #print("Using: %s" % str(path))
   return path

#---------------------------------------------------------------------------------------------------------#
def getSystemDnldPath():
   #if testSwitch.winFOF:
   #   path = UserDownloadsPath
   #   #path = os.path.join('C:\\','var','merlin','dlfiles',CN)
   #else:
   path = os.path.join(UserDownloadsPath, CN)
   #print("Using: %s" % str(path))
   return path

#---------------------------------------------------------------------------------------------------------#
def getSystemParamsPath():
   #if testSwitch.winFOF:
   #   path = ParamFilePath
   #   #path = os.path.join('C:\\','var','merlin','params',CN)
   #else:
   path = os.path.join(ParamFilePath, CN)
   #print("Using: %s" % str(path))
   return path


#---------------------------------------------------------------------------------------------------------#
def getSystemResultsPath():
   if testSwitch.winFOF:
      path = os.path.join("C:"+os.sep,"var","merlin","results")
   else:
      path = os.path.join(os.sep + "var","merlin","results")

   if testSwitch.virtualRun:
      path = "..\\results\\" #ResultsFilePath # ResultsFilePath already has /bench appended

   return path

#---------------------------------------------------------------------------------------------------------#
def getSystemPCPath():
   if testSwitch.winFOF:
      path = os.path.join("C:"+os.sep, "var", "merlin","pcfiles")
      #path = os.path.join('C:\\','var','merlin','params',CN)
   elif testSwitch.virtualRun:
      path = "."
   else:
      path = os.path.join(os.sep + "var", "merlin","pcfiles")
   #print("Using: %s" % str(path))
   return path

#---------------------------------------------------------------------------------------------------------#

#---------------------------------------------------------------------------------------------------------#
def getFileSize(fObj):
   """
   Get File size by either fObj.size() or using os commands to analyze the fobj based on object attributes
   """
   try:
      inSize = fObj.size()
   except AttributeError:
      inSize = os.stat(os.path.join(getSystemResultsPath(),getFofFileName(1),fObj.name))[stat.ST_SIZE]

   return inSize


def getFofFileName(file = 1):
   """
   Return the FOF file/folder name for the cell/tray/port index
   @param file: Default set to 1= return file name. 0 means return folder name
   """
   if testSwitch.winFOF == 1:
      if file == 1:
         ret = '%2.2d-%s' % (int(CellIndex),TrayIndex)
      else:
         if testSwitch.virtualRun == 1:
            ret = "bench"
         else:
            ret = '%d-%s' % (int(CellIndex),TrayIndex)
   else:
      if file == 1:
         ret = '%2.2d-%s-%s' % (int(CellIndex),TrayIndex,PortIndex)
      else:
         ret = '%d-%s-%s' % (int(CellIndex),TrayIndex,PortIndex)
   return ret
#---------------------------------------------------------------------------------------------------------#
def getSystemMaximumFileSizes():
   #Get maximum parametric results size and generic results size
   parametricFileMargin = 4000
   try:
      maxResultsFileSize = int(RequestService('GetSiteconfigSetting','MAX_RESULT_FILE_SIZE')[1]['MAX_RESULT_FILE_SIZE']) * 1000000
      if ConfigVars[CN].get('PRODUCTION_MODE',0) and productionMaxEventSize != None:
         DefaultMaxEventSize = min(productionMaxEventSize, int(RequestService('GetSiteconfigSetting','DefaultMaxEventSize')[1]['DefaultMaxEventSize']))
      else:
         DefaultMaxEventSize = int(RequestService('GetSiteconfigSetting','DefaultMaxEventSize')[1]['DefaultMaxEventSize'])
   except:
      statMsg(traceback.format_exc())
      # RPM possibly doesn't support GetSiteconfigSetting
      maxResultsFileSize = 2000000
      DefaultMaxEventSize = 2000000
   if testSwitch.BF_0179082_231166_P_INCREASE_PARAMETRIC_FILE_MARGINS:
      DefaultMaxEventSize = (DefaultMaxEventSize * 0.98) - parametricFileMargin
   statMsg("\nMaxResultsFileSize = %s\nDefaultMaxEventSize = %s" % (maxResultsFileSize,DefaultMaxEventSize) )
   return (maxResultsFileSize, DefaultMaxEventSize, parametricFileMargin)

#-------------------------------------------------------------------------------
def translateErrCode(errorCode):
   import sys
   lastException, lastValue = sys.exc_info()[:2]
   errMsg = '%s: %s' % (str(sys.exc_info()[0]),str(sys.exc_info()[1]))
   objMsg.printMsg(traceback.format_exc())

   if str(sys.exc_info()[0]).find('NameError') != -1 or \
      str(sys.exc_info()[0]).find('UnboundLocalError') != -1:
      errCode = 14555
   elif str(sys.exc_info()[0]).find('FOFSerialCommError') != -1:
      errCode = 11087
   elif str(sys.exc_info()[0]).find('FOFSerialTestTimeout') != -1:
      errCode = 11049
   elif str(sys.exc_info()[0]).find('FOFParameterError') != -1:
      errCode = 10264
   elif str(sys.exc_info()[1]).find('SER_SRQ_TIMEOUT') != -1:
      errCode = 11049
   elif str(sys.exc_info()[1]).find('ESLIP ERROR') != -1:
      errCode = 11087
   elif str(sys.exc_info()[0]).find('KeyError') != -1:
      errCode = 14526
   elif str(sys.exc_info()[0]).find('AttributeError') != -1:
      errCode = 14527
   elif str(sys.exc_info()[0]).find('IndexError') != -1:
      errCode = 14554
   elif str(sys.exc_info()[0]).find('FOFKillCell') != -1:
      errCode = 11075
   elif str(sys.exc_info()[0]).find('FOFBadPlugBits') != -1:
      errCode = 11045
   elif str(sys.exc_info()[0]).find('FOFTemperatureRampFailure') != -1:
      errCode = 11060
   elif  str(sys.exc_info()[0]).find('FOFInterlockTrip') != -1 or \
         str(sys.exc_info()[0]).find('FOFVCLimitTrip') != -1:
      errCode = 11105
   elif str(sys.exc_info()[0]).find('FOFCellFanSpeedTrip') != -1:
      errCode = 11197
   elif  str(sys.exc_info()[0]).find('RimProxyException') != -1:
      errCode = 11169
   elif  str(sys.exc_info()[0]).find('FOFCellRIMError') != -1:
      errCode = 11074
   elif str(sys.exc_info()[1]).find('SER_ACK_TIMEOUT') != -1:
      errCode = 11088  #CM_CPY_SERIAL_TIMEOUT
   elif str(sys.exc_info()[0]).find('FOFResultsProcessingFailure') != -1:
      errCode = 14823 #Unsupported Request from Drive
   elif str(sys.exc_info()[1]).find('ScriptTestFailure') != -1:
      errCode = errorCode
   elif testSwitch.FE_0112376_231166_RAISE_11049_EC_WITH_CFLASHCORRUPTEXCEPTION and \
      str(sys.exc_info()[1]).find('CFlashCorruptException') != -1:
      errCode = 11049 # CFlashCorruptException should be a timeout
   elif testSwitch.BF_0115535_405392_FIX_RAISE_11049_EC_WITH_CFLASHCORRUPTEXCEPTION and \
      str(sys.exc_info()[0]).find('CFlashCorruptException') != -1:
      errCode = 11049 # CFlashCorruptException should be a timeout
   else:
      errCode = GenericErrorCode #11044
      #statMsg('General Exception Dump: %s' % genExcept)

   return (errCode, errMsg)

#---------------------------------------------------------------------------------------------------------#
def HostSetPartnum(pn):
   '''
      SetPartnum() host service supported in Host RPM newer than 14.03-17
      Reference: http://fof-test.seagate.com:8280/HostServices/SetPartnum 
   '''
   try:
      RequestService("SetPartnum", pn)
   except:
      pass
