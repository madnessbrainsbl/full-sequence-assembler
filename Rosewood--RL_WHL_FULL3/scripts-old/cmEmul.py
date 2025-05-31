
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/11/08 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/cmEmul.py $
# $Revision: #5 $
# $DateTime: 2016/11/08 00:12:47 $
# $Author: gang.c.wang $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/cmEmul.py#5 $
#CM emulation for full script processsing and bench level virtual debugging
from Test_Switches import testSwitch


import sys as SYS
import os as OS
import traceback as TRACEBACK
import struct as STRUCT
import time, re


##################################################
# Global Settings
##################################################
global failSafeMode, fnReturnData, curTemp, DriveVars, ErrorCode
if testSwitch.FE_0118213_399481_SET_VE_SERIAL_NUMBER_BY_PART_NUMBER:
   global HDASerialNumber

failSafeMode = False
fnReturnData  = '\x80'
ErrorCode = 0

SYS.path.append(OS.path.join('..','Profile')) #for profile scripts

##################################################
# User Settings
##################################################
try:
   TraceMessage('')
except:
   def TraceMessage(msg):
      print str(msg)

HOST_ID = 'winFOFBench'
VCS_REVISION = "$Revision: #5 $"
print 'HOST_ID:', HOST_ID
try:
   HostVersion = re.search(r"#(\d+)", VCS_REVISION) + ".0.CMEMUL"
except:
   HostVersion = '0.0.WINFOF'
#HostVersion = "14.03-17 / 14NOV2008"  # uncomment for CPC OTF
CMIP = '127.0.0.1'
CHAMBER_TYPE = 'GEMINI'  #Types GEMINI B2D SP240 STC
cellTypeString = 'GXD3'
try:
   repr(ConfigId)
except:
   ConfigId = ("merlin","","bench","") #CE,CP,CN,CV

CE,CP,CN,CV = ConfigId
iPort = 0
if not testSwitch.FE_0118213_399481_SET_VE_SERIAL_NUMBER_BY_PART_NUMBER:
   try:
      print HDASerialNumber
   except:
      try:
         from pgm_Constants import virtualDrvSN
         HDASerialNumber = virtualDrvSN
      except:
         HDASerialNumber = '1PTBENCH'

CarrierSN = 'nothing'
curTemp = 480
Baud38400 = 38400

PortIndex = 0
CellNumber = 0

CMCodeVersion = 'cmEmul_winFOF'
EditRev = 0

import shutil as SHUTIL
#createDir = lambda dirName : OS.mkdir(dirName) if not OS.path.isdir(dirName) else None
def createDir(dirName):
   if not OS.path.isdir(dirName):
      OS.mkdir(dirName)
def copyMultipleFiles(fileList, sourceDir, destDir):
   for fileName in fileList:
      targetFile = OS.path.join(sourceDir, fileName)
      if not OS.path.isfile(OS.path.join(destDir, fileName)):
         SHUTIL.copy(targetFile, destDir)



try:
   repr(UserScriptPath)
except:
   if OS.name == 'nt':
      reqDirs = ("..\\dlfiles\\", "..\\dlfiles\\bench\\",
                    "..\\params\\", "..\\params\\bench\\",
                    "..\\scripts\\")
      map(createDir, reqDirs)
      copyMultipleFiles(("codes.h", "param_cd.h", "proc_codes.h",), "C:\\var\\merlin\\params\\bench\\", "..\\params\\bench\\")
      UserDownloadsPath = "..\\dlfiles\\"
      ParamFilePath = "..\\params\\"
      ScriptPath  = "..\\scripts\\"
      UserScriptPath = ScriptPath
   else:
      UserDownloadsPath = OS.sep + "var" + OS.sep + 'merlin' + OS.sep + 'cfgs' +OS.sep+ CN + OS.sep + 'dlfiles' + OS.sep
      ParamFilePath = OS.sep + "var" + OS.sep + 'merlin' + OS.sep + 'cfgs' +OS.sep+ CN + OS.sep + 'params' + OS.sep
      ScriptPath  = OS.sep + "var" + OS.sep + 'merlin' + OS.sep + 'cfgs' +OS.sep+ CN + OS.sep + 'scripts' + OS.sep
      UserScriptPath = ScriptPath

try:
   print DriveAttributes
except:
   DriveAttributes = {}

   ##################################################
   # Default Settings
   ##################################################
   # Drive Attributes
   DriveAttributes.update({'SUB_BUILD_GROUP':str(CN)})

   DriveAttributes.update({'MODEL_NUM': 'NONE'})
   DriveAttributes.update({'CARRIER_ID': 'NONE'})
   DriveAttributes.update({'FOF_RESTART': 0})
   DriveAttributes.update({'WW_SATA_ID': '5000C50011EBF574'})

   DriveAttributes.update({
      'BSNS_SEGMENT'    : "INVALID",
      'TIME_TO_READY'   : "0.0",
      'SECURITY_TYPE'   : "INVALID",
      'WWN'             : "INVALID",
      'ZERO_PTRN_RQMT'  : "INVALID",
      'FDE_TYPE'        : "INVALID",
      'USER_LBA_COUNT'  : "0",
      'DRV_MODEL_NUM'   : "INVALID",
      'CUST_MODEL_NUM'  : "INVALID",
      'CUST_MODEL_NUM2' : "INVALID",
      'CONFIG_CODE'     : "INVALID",
      })
   if testSwitch.FE_0127531_231166_USE_EXPLICIT_INTF_TYPE:
      DriveAttributes['INTERFACE'] = 'AS'

##################################################
# Config override
##################################################
ConfigName = CN
ConfigVars =  {}
ConfigVars[CN] = {}

try:
   configVarspath = False
   if OS.path.exists(OS.path.join('.',CN,'Config.py')):
      configVarspath = OS.path.join('.',CN,'Config.py')
   elif OS.path.exists(OS.path.join(UserScriptPath,CN,'Config.py')) and getattr(testSwitch, 'useConfigPY', False):
      configVarspath = OS.path.join(UserScriptPath,CN,'Config.py')

   if configVarspath:
      exec(open(configVarspath,'r').read())
      ConfigVars[CN] = topcfg["ConfigVars"]
except:
   print("Failed to get configvars from %s\n%s" % (configVarspath, TRACEBACK.format_exc()))

if testSwitch.virtualRun and ConfigVars[CN] == {}:

   from ConfigVars import CfgVars
   for key,value in CfgVars.items():
      ConfigVars[CN][key] = eval(value['value'])

   configVarspath = OS.path.join(OS.getcwd(),'ConfigVars.py')

print('*'*80)
print("Obtaining ConfigVars[%s] from %s" % (CN, configVarspath))
print('*'*80)

# ConfigVars
ConfigVars[CN].update({'MessageOutputLevel':13})
ConfigVars[CN].update({'StartSubSequence':0})
ConfigVars[CN].update({'EVAL_MODE':'OFF'})
ConfigVars[CN].update({'resultsLog': 1,'reportstatus':1,'traceLog': 1,'anotherLog':1})
ConfigVars[CN].update({'Business Group': 'STD'})

# Disable power loss recovery for bench execution... people whom need to winfof test this can override manually
ConfigVars[CN]['StatePwrLossRecovery'] = 0


##################################################
# Force BenchTop for elimination of ramping requirements
ConfigVars[CN].update({'BenchTop': 1})
##################################################
#  Program specific auto-detected variables
##################################################
try:
   from pgm_Constants import virtualPartNum, virtualPgm
   partNum = virtualPartNum
   program = virtualPgm
except:
   program = 'Muskie' #Used for virtual execution not winFOF

DriveAttributes.update({'PART_NUM': partNum})
ConfigVars[CN].update({'PartNum':partNum})

suppress_user_powerCycles = ConfigVars[CN].get('benchSuppressPowerCycles',0) #Assigning to 1 will cause no power-cycle requests to be raised
#  if external power module is not attached

from StateTable import Operations
if ConfigVars[CN].get('DefInitOper',False):
   Operation = ConfigVars[CN]['DefInitOper']
   Operations = ConfigVars[CN].get('OperList',Operations)
   operIndex = Operations.index(Operation)
else:
   try:
      operList = ConfigVars[CN].get('OperList',Operations)
      Operation = operList[0]
      operIndex = operList.index(Operation)
   except:
      TraceMessage(TRACEBACK.format_exc())
      raise
DriveAttributes['SET_OPER'] = Operation
DriveAttributes['OPER_INDEX'] = operIndex

try:
   print partNum    #may have been imported from pgm_Constants
except:
   try:
      from Codes import fwConfig
      partNum = fwConfig.keys()[0]
   except:
      TraceMessage(TRACEBACK.format_exc())
      partNum = '9EH132-999'

if testSwitch.FE_0118213_399481_SET_VE_SERIAL_NUMBER_BY_PART_NUMBER:
   try:
      print HDASerialNumber
   except:
      try:
         from pgm_Constants import VE_PN_PatternToSerialNumberDict
         for PN_Pattern,SerialNumber in VE_PN_PatternToSerialNumberDict.items():
            if re.match(PN_Pattern, partNum):
               HDASerialNumber = SerialNumber
               break
      except:
         HDASerialNumber = '1PTBENCH'


def getRiserType(partNum,curOper):
   interfaceMatrix = {
         '004': {
            'SCOPY':'DDFC',
            'PRE2' :'DDFC',
            'CAL2' :'DDFC',
            'FNC2' :'DDFC',
            'FIN2' :'FC4',
            'FDE2' :'FC4',
            'CRT2' :'FC4',
            'CUT2' :'FC4',
            'B2D2' :'FC4',
            'CCV2' :'FC4',
            'SHST' :'FC4',
            'AUD2' :'FC4',
            'CMT2' :'FC4',
            'IOSC2':'FC4',
            'SPSC2':'FC4',
            'SDAT2':'FC4',
         },
         '007': {
            'SCOPY':'DDFC',
            'PRE2' :'DDFC',
            'CAL2' :'DDFC',
            'FNC2' :'DDFC',
            'FIN2' :'FC4',
            'FDE2' :'FC4',
            'CRT2' :'FC4',
            'CUT2' :'FC4',
            'B2D2' :'FC4',
            'CCV2' :'FC4',
            'SHST' :'FC4',
            'AUD2' :'FC4',
            'CMT2' :'FC4',
            'IOSC2':'FC4',
            'SPSC2':'FC4',
            'SDAT2':'FC4',
         },
         '066': {
            'SCOPY':'DDSAS',
            'PRE2' :'DDSAS',
            'CAL2' :'DDSAS',
            'FNC2' :'DDSAS',
            'FIN2' :'SAS',
            'FDE2' :'SAS',
            'CRT2' :'SAS',
            'CUT2' :'SAS',
            'B2D2' :'SAS',
            'CCV2' :'SAS',
            'SHST' :'SAS',
            'AUD2' :'SAS',
            'CMT2' :'SAS',
            'IOSC2':'SAS',
            'SPSC2':'SAS',
            'SDAT2':'SAS',
         },
         '1XX': {
            'SCOPY':'DDSATA',
            'PRE2' :'DDSATA',
            'CAL2' :'DDSATA',
            'FNC2' :'DDSATA',
            'FIN2' :'DDIPSATA',
            'CUT2' :'DDIPSATA',
            #'FIN2' :'P1INI0',       # Simulate SIC in IO VE
            #'CUT2' :'P1INI0',       # Simulate SIC in IO VE
            'CMT2' :'DDIPSATA',
            'FDE2' :'DDIPSATA',
            'CRT2' :'DDIPSATA',
            'AUD2' :'DDIPSATA',
            'B2D2' :'DDIPSATA',
            'CCV2' :'DDIPSATA',
            'IOSC2':'DDIPSATA',
            'SPSC2':'DDIPSATA',
            'SDAT2':'DDIPSATA',
            '6GA'  :'P1INI0',
         },
         '2XX':{
            'SCOPY':'DDSAS',
            'PRE2' :'DDSAS',
            'CAL2' :'DDSAS',
            'FNC2' :'DDSAS',
            'FIN2' :'SAS',
            'FDE2' :'SAS',
            'CRT2' :'SAS',
            'CUT2' :'SAS',
            'B2D2' :'SAS',
            'CCV2' :'SAS',
            'AUD2' :'SAS',
            'CMT2' :'SAS',
            'IOSC2':'SAS',
            'SPSC2':'DDSAS',
            'SDAT2':'SAS',
         },
         'GXX': {
            'SCOPY':'DDSATA',
            'PRE2' :'DDSATA',
            'CAL2' :'DDSATA',
            'FNC2' :'DDSATA',
            'FIN2' :'DDIPSATA',
            'FDE2' :'DDIPSATA',
            'CRT2' :'DDIPSATA',
            'CUT2' :'DDIPSATA',
            'B2D2' :'DDIPSATA',
            'CCV2' :'DDIPSATA',
            'CMT2' :'DDIPSATA',
            'AUD2' :'DDIPSATA',
            'IOSC2':'DDIPSATA',
            'SPSC2':'DDIPSATA',
            'SDAT2':'DDIPSATA',
         },
         'ker': {                # Broker Process
            'SCOPY':'DDSATA',
            'PRE2' :'DDSATA',
            'FIN2' :'DDIPSATA',
            'BRO'  :'DDIPSATA',
         },
         'stc': {                # Seagate Thermal Chamber
            'SCOPY':'DDIPSATA',
            'PRE2' :'DDIPSATA',
            'STC'  :'DDIPSATA',
         },
      }

   riserTypeMatrix = interfaceMatrix.get(partNum[3:6],interfaceMatrix.get(partNum[3]+'XX','DDPSATA'))

   if type(riserTypeMatrix) is dict:
      riserType = riserTypeMatrix.get(Operation,'DDIPSATA')
   else:
      riserType = riserTypeMatrix
   print riserType,Operation
   return riserType

riserType = getRiserType(partNum,Operation)
if 'SAS' in riserType:
   riserExtension = 'D3SS6TDT31'
else:
   riserExtension = 'D3ST6TDT31'

##################################################
##################################################

class cmFile(file):
   """
   Generic Results file *like* class to implement the same interface
      as allowed writable files in the CM.
   """
   def __init__(self,fName):
      self.fName = fName

   def open(self,mode):
      file.__init__(self,self.fName,mode)
      return self

   def delete(self):
      try:
         OS.remove(self.fName)
         return True
      except:
         print("Failed to remove %s" % self.fName)
         return False

   def size(self):
      return OS.stat(self.fName)[6]

   def __del__(self):
      self.close()
##################################################
##################################################

try:
   driveVStr = open(ScriptPath + "DriveVars.txt",'r').read()
except:
   try:
      driveVStr = open(ScriptPath + OS.sep + "DriveVars.txt",'r').read()
   except:
      try:
         driveVStr = open("." + OS.sep + "DriveVars.txt",'r').read()
      except:
         print("Failed to import Drive Vars...")
         driveVStr = {}

#### WinFOF Section
try:
   from pppa import *
except ImportError: # if power control is not available
   if suppress_user_powerCycles == 1:
      def DriveOff(*args,**kwargs):
         pass
      def DriveOn(*args, **kwargs):
         pass

      def RimOn(*args, **kwargs):
         pass

      def RimOff(*args, **kwargs):
         pass
   else:
      pass
else: # if power control is available
   def DriveOff(*args,**kwargs):
      pwroff()
      sleep(kwargs.get('pauseTime',10) )

   def DriveOn(*args,**kwargs):
      pwron()
      sleep(kwargs.get('pauseTime',10) )

def CheckDownloadRequest(*args,**kwargs):
   return 'DefaultCPCFile','9.999BENCH'

def DownloadRim(*args,**kwargs):
   return (0,{'BOOTVER':(0,0), 'CPCVER':(0.000,0)})

try:
   #Not all CM's support the following functions
   SPortToInitiator
except NameError:
   def SPortToInitiator( flag):
      pass
   def DisableStaggeredStart( flag):
      pass

try:
   if GChar() == None:
      redefineRawVars = True
   else:
      redefineRawVars = False
except:
   redefineRawVars = True

if redefineRawVars:
   """Then we are in WINFOF and not sterm"""
   def GChar(ignoreOFlow = 1, readSize = None):
      return Receive()

   def PBlock(theBlock):
      return Send(theBlock)

   def PChar(theChar):
      return PBlock(theChar)

#### Virtual section- stand-a-lone execution
if testSwitch.virtualRun:
   DriveAttributes['TD_SID'] = '0'*32
   def dummyTime(val):
      if ( val % (60*60) == 0 ): # when remainder is 0
         print "Virtual Run: Sleeping %f mins" % (val/(60*60))

   time.sleep = dummyTime

   # Disable power loss recovery for VE
   ConfigVars[CN]['StatePwrLossRecovery'] = 0

   def setPartNum(virtualPartNum):

      try:
         from Codes import fwConfig
         partNumList = [PN.upper() for PN in fwConfig.keys()]
         if virtualPartNum.upper() in partNumList:
            partNum = virtualPartNum
         else:
            partNum = fwConfig.keys()[0]
      except:
         try:
            TraceMessage(TRACEBACK.format_exc())
            partNum = fwConfig.keys()[0]
         except:
            partNum = '9EH132-999'

      riserType = getRiserType(partNum,Operation)

      DriveAttributes.update({'PART_NUM': partNum})
      ConfigVars[CN].update({'PartNum':partNum})

      if testSwitch.FE_0118213_399481_SET_VE_SERIAL_NUMBER_BY_PART_NUMBER:
         global HDASerialNumber
         try:
            from pgm_Constants import VE_PN_PatternToSerialNumberDict
            for PN_Pattern,SerialNumber in VE_PN_PatternToSerialNumberDict.items():
               if re.match(PN_Pattern, partNum):
                  HDASerialNumber = SerialNumber
                  break
         except:
            HDASerialNumber = '1PTBENCH'

      return riserType,partNum

   def createUserScriptPath(pgm):
      return ".\\%s" % pgm

   if OS.name == 'nt':
      reqDirs = ("..\\dlfiles\\", "..\\dlfiles\\bench\\",
                    "..\\params\\", "..\\params\\bench\\",
                    "..\\results\\", "..\\results\\bench\\", "..\\results\\" + CN,
                    )
      map(createDir, reqDirs)
      copyMultipleFiles(("codes.h", "param_cd.h", "proc_codes.h",), "C:\\var\\merlin\\params\\bench\\", "..\\params\\bench\\")
      UserDownloadsPath = "..\\dlfiles\\"
      ParamFilePath = "..\\params\\"
      ResultsFilePath = "..\\results\\" + CN
      ScriptPath  = createUserScriptPath(program)
      UserScriptPath = ScriptPath
   else:
      UserDownloadsPath = OS.sep + "var" + OS.sep + 'merlin' + OS.sep + 'cfgs' +OS.sep+ CN + OS.sep + 'dlfiles' + OS.sep
      ParamFilePath = OS.sep + "var" + OS.sep + 'merlin' + OS.sep + 'cfgs' +OS.sep+ CN + OS.sep + 'params' + OS.sep
      ResultsFilePath = OS.path.join('var','merlin','results',CN)
      ScriptPath  = '.'

   CellIndex = 0
   PortIndex = 0
   TrayIndex = 0
   DriveVars = {}

   GenericErrorCode = 11044
   Baud38400, Baud115200 , Baud390000, Baud460800, Baud625000, Baud921600, Baud1228000 = (38400, 115200, 390000, 460800, 625000, 921600, 1228000)


   exec("DriveVars.update(%s)" % driveVStr)
   print(str(DriveVars))

   if not OS.path.exists(OS.path.join(ResultsFilePath,'bench.rp1')):
      print "Bench results file not found... creating directory structure and file."
      try:OS.makedirs(ResultsFilePath)
      except:pass
      open(OS.path.join(ResultsFilePath, 'bench.rp1'),'w').write('')

   #Delete the serialize log
   if OS.path.exists(OS.path.join(ResultsFilePath,'%s_serialize.log' % HDASerialNumber)):
      print "Removing %s" % OS.path.join(ResultsFilePath,'%s_serialize.log' % HDASerialNumber)
      OS.remove(OS.path.join(ResultsFilePath,'%s_serialize.log' % HDASerialNumber))

   def loadAvailableParamsFromSelfTest_ParamCDdotH():
      enableCheckingSelfTestParams = True
      allowedSelfTestParams = {}
      paramFileName = 'param_cd.h'
      INDEX_OF_POUND_DEFINE = 0
      INDEX_OF_PARAMETER_NAME = 1
      CHARS_TO_STRIP_OFF_PARAMETER_NAME = '_P'

      if OS.path.isfile('.' + OS.sep + paramFileName) == True:
         fPtr = open('.' + OS.sep + paramFileName, 'r')
      else:
         if OS.path.isfile(ParamFilePath + paramFileName) == True:
            fPtr = open(ParamFilePath + paramFileName, 'r')
         else:
            enableCheckingSelfTestParams = False
            return allowedSelfTestParams, enableCheckingSelfTestParams

      for line in fPtr:
         splitLine = line.split(' ')
         if splitLine[INDEX_OF_POUND_DEFINE] == '#define' and splitLine[INDEX_OF_PARAMETER_NAME][-2:] == '_P':
            paramName = splitLine[INDEX_OF_PARAMETER_NAME]
            allowedSelfTestParams[paramName[:-7]] = splitLine[-1][0]
      fPtr.close()
      return allowedSelfTestParams, enableCheckingSelfTestParams

   allowedSelfTestParams, enableCheckingSelfTestParams = loadAvailableParamsFromSelfTest_ParamCDdotH()


   class DataBlockSetup: #Used by test 595
      def formatBlock(self,*args,**kwargs):
         pass
      def loadDictionaryToBlock(self,*args,**kwargs):
         pass
      def sendToFile(self,*args,**kwargs):
         pass

   class InterfaceCommand:
      basicResponse = {'LLRET':0,'STS':'80', 'IDSerialNumber': HDASerialNumber}
      extraAck = 0

      def __getattr__(self,name):
         import __builtin__
         if name in dir(__builtin__):
            return getattr(__builtin__,name)
         else:
            return self.PassThrough

      def EslipRetry(self,*args, **kwargs):
         self.extraAck = int(not self.extraAck)
         return {'ERTRYCNT':0, 'EXTRAACK':str(self.extraAck)}

      def HardReset(self,*args,**kwargs):
         pass
      def SetRFECmdTimeout(self,*args,**kwargs):
         pass
      def TestUnitReady(self,*args,**kwargs):
         return self.basicResponse
      def IdentifyDevice(self,*args,**kwargs):
         # Product:Wyatt - SN:5VC01VCY
         #self.cpcReadBuff = '\x5a\x0c\xff\x3f\x37\xc8\x10\x00\x00\x00\x00\x00\x3f\x00\x00\x00\x00\x00\x00\x00\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x56\x35\x30\x43\x56\x31\x59\x43\x00\x00\x00\x40\x04\x00\x30\x30\x31\x30\x44\x53\x31\x4d\x54\x53\x31\x39\x30\x36\x31\x33\x41\x34\x20\x53\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x10\x80\x00\x00\x00\x2f\x00\x40\x00\x02\x00\x02\x07\x00\xff\x3f\x10\x00\x3f\x00\x10\xfc\xfb\x00\x10\x01\xff\xff\xff\x0f\x00\x00\x07\x04\x03\x00\x78\x00\x78\x00\x78\x00\x78\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1f\x00\x06\x05\x00\x00\x48\x00\x40\x00\xf0\x01\x29\x00\x6b\x34\x09\x7d\x23\x61\x69\x34\x09\xbc\x23\x61\x7f\x00\x17\x00\x17\x00\x80\x80\xfe\xff\x00\x00\x00\xfe\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xb0\x9e\xa1\x12\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x50\x00\xc5\xeb\x11\x74\xf5\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1e\x40\x1c\x40\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x21\x00\xb0\x9e\xa1\x12\xb0\x9e\xa1\x12\x20\x20\x02\x00\x40\x01\x00\x01\x00\x50\x06\x3c\x0a\x3c\x00\x00\x3c\x00\x00\x00\x08\x00\x00\x00\x00\x00\x1f\x00\x80\x02\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x3c\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x3b\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x18\x15\x00\x00\x00\x00\x00\x00\x00\x00\x10\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xa5\xca'
         
         # Product: YarraBP         
         self.cpcReadBuff = 'Z\x0c\xff?7\xc8\x10\x00\x00\x00\x00\x00?\x00\x00\x00\x00\x00\x00\x00            0Q0T209B\x00\x00\x00\x80\x04\x000010DS1MTS52L00T219-SW41 1                      \x10\x80\x00@\x00/\x00@\x00\x02\x00\x02\x07\x00\xff?\x10\x00?\x00\x10\xfc\xfb\x00\x10\x01\xff\xff\xff\x0f\x00\x00\x07\x04\x03\x00x\x00x\x00x\x00x\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1f\x00\x06\x0f\x04\x00H\x00@\x00\xf0\x01)\x00kti}caitI\xbcca\x7f\x00\x1a\x00\x1a\x00\x80\x80\xfe\xff\x00\x00\x00\xd0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00pY\x1c\x1d\x00\x00\x00\x00\x00\x00\x00\x00\x03`\x00\x00\x00P\x00\xc5\xa1\x0b\xeb\xca\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1e@\x1e@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\x00pY\x1c\x1dpY\x1c\x1d  \x02\x00@\x01\x08\x01\x00P\x06<\n<\x00\x00<\x00\x00\x00\x08\x00\x00\x00\x00\x00\xff\x00\x80\x02\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00(\x10\x00\x00\x00@\x00\x00\x00_\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x005\x10\x00\x00\x00\x00\x00@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x18\x15\x00\x00\x00\x00\x02\x00\x00\x00\x10\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xa5'
         self.cpcWriteBuff = self.cpcReadBuff
          
         return self.basicResponse
      def ClearBinBuff(self,*args,**kwargs):
         return self.basicResponse
      def GetBuffer(self,*args,**kwargs):
         """ CPC Document Version: 2.220 """
         
         # verifying parameter
         paramLen = len(args)
         byteCount = 512            # TODO: has to be a whole buffer
         if len > 2:
            byteCount = args[2]
         startOffset = 0
         if len > 1:
            startOffset = args[1]
         bufferType = None
         if len > 0:
            bufferType  = args[0]
         endOffset = startOffset + byteCount
         # getting data
         ret = self.basicResponse.copy()
         data = '\x00\x01\xff'
         if bufferType == 1:     # WBF: CPC Write Buffer
            data = self.cpcWriteBuff[startOffset:endOffset]
         elif bufferType == 2:   # RBF: CPC Read Buffer
            data = self.cpcReadBuff[startOffset:endOffset]
         elif bufferType == 3:   # BWR: CPC Both Write and Read Buffer
            data = self.cpcWRBuff[startOffset:endOffset]
         elif bufferType == 4:   # SBF: CPC Serial Buffer
            data = self.cpcSerialBuff[startOffset:endOffset]
         ret.update({'DATA':data})
         return ret
      def CRCErrorRetry(self,*args, **kwargs):
         rest = self.basicResponse.copy()
         rest['RETRY'] = 1
         rest['CRCCNT'] = 0
         return rest
      def PassThrough(self,*args,**kwargs):
         return self.basicResponse
      def SetFeatures(self,*args,**kwargs):
         return self.basicResponse
      def SingleSeekTime(self,*args,**kwargs):
         return {'LLRET':0,'STS':'80', 'SnSkMinTm':4,'STS':'80','SnSkMaxTm':8,'STS':'80', 'SnSkAvgTm': 6}
      def RandomSeekTime(self,*args,**kwargs):
         return {'LLRET':0,'STS':'80', 'RnSkMinTm':4,'STS':'80','RnSkMaxTm':8,'STS':'80', 'RnSkAvgTm': 6}
      def FullSeekTime(self,*args,**kwargs):
         return {'LLRET':0,'STS':'80', 'FuSkMinTmOI':4,'STS':'80','FuSkMaxTmOI':8,'STS':'80', 'FuSkAvgTmOI': 6, 'FuSkMinTmIO':4,'STS':'80','FuSkMaxTmIO':8,'STS':'80', 'FuSkAvgTmIO': 6}
      def Idle(self,*args,**kwargs):
         return self.basicResponse
      def CheckPowerMode(self,*args,**kwargs):
         return {'LLRET':0,'STS':'80','SCNT': 0xff}
      def SmartEnableOper(self, *args, **kwargs):
         return {'LLRET':0,'STS':'80','SCNT': 0xff}
      def SmartReturnStatus(self,*args,**kwargs):
         return {'LLRET':0,'STS':'80','LBA': 0xc24f00}
      def SmartReadLogSec(self,*args,**kwargs):
         return {'LLRET':0,'STS':'80'}
      def SmartWriteLogSec(self,*args,**kwargs):
         return {'LLRET':0,'STS':'80'}
      def StatusCheck(self,*args,**kwargs):
         self.basicResponse['SpinUpTm'] = 0
         return self.basicResponse
      def SmartReadData(self,*args,**kwargs):
         return self.basicResponse
      def DeleteAllFiles(self, *args, **kwargs):
         return self.basicResponse
      def GetMaxLBA(self):
         return {'LLRET': 0, 'MAX48': '0x000000000950F8B0', 'RES': '', 'RESULT': 'IEK_OK:No error', 'MAX28': '268435455', 'CT': '0'}
      def GetIntfTimeout(self):
         return {'LLRET': 0, 'TMO': '30000', 'RES': '', 'RESULT': 'IEK_OK:No error', 'CT': '0'}
      def BluenunSlide(self,*args,**kwargs):
         return {'LLRET': 0, 'TMO': '0', 'RES': '', 'RESULT': 'IEK_OK:No error', 'CT': '0', 'REC': 2, 'TLIM': 150, 'SLOWRD': 30, 'TOE':0}
      def SerialDone(self, *args, **kwargs):
         return self.basicResponse
      def RandomCCT(self, *args, **kwargs):
         return {'LLRET':0,'STS':'80','THR0':0,'THR1':0,'THR2':0}
      def SequentialCCT(self, *args, **kwargs):
         return {'LLRET':0,'STS':'80','THR0':0,'THR1':0,'THR2':0}

   ICmd = InterfaceCommand()

   ResultsFile = cmFile(OS.path.join(ResultsFilePath,'bench.rp1'))

   def SetRFECmdTimeout(*args,**kwargs):
      pass

   def SetFailSafe():
      global failSafeMode
      failSafeMode = True
#      print("Fail Safe Enabled")

   def ClearFailSafe():
      global failSafeMode
      failSafeMode = False
#      print("Fail Safe Disabled")

   def TraceMessage(sMsg):
      print(sMsg)

   def WriteToResultsFile(data):
      print(str(data))
      try:
         ResultsFile.open('ab')
         ResultsFile.write(data)
         ResultsFile.close()
      except:
         pass

   def SerialCmd(DOT='none',name='HVC#',i=3):
      pass

   def CellLed(i):
      pass

   def DriveOff(*args,**kwargs):
      pass

   def DriveOn(*args, **kwargs):
      pass

   def RimOn(*args, **kwargs):
      pass

   def RimOff(*args, **kwargs):
      pass


   def ReportRestartFlags(*args, **kwargs):
      pass

   def SetBaudRate(baud=1000):
      pass

   def ReportStatus(sMsg):
      pass

   def ScriptComment(sMsg, writeTimestamp=1):
      WriteToResultsFile(sMsg)

   def SetTPMFile(data):
      pass

   def UseESlip(var = 1):
      pass

   def UseHardSRQ(boolFlag = 1):
      pass

   def RequestService(*args):
      if testSwitch.WA_0256539_480505_SKDC_M10P_BRING_UP_DEBUG_OPTION:
         MAX_RESULT_FILE_SIZE = '256000000'
      else:
         MAX_RESULT_FILE_SIZE = '64000000'
      DefaultMaxEventSize = '2000000'

      if len(args) >= 2: 
         if  args[1] == 'ChamberType':
            return '',{'ChamberType':CHAMBER_TYPE}
         elif args[1] == 'MAX_RESULT_FILE_SIZE':
            return '',{'MAX_RESULT_FILE_SIZE':MAX_RESULT_FILE_SIZE}
         elif args[1]== 'DefaultMaxEventSize':
            return '',{'DefaultMaxEventSize':DefaultMaxEventSize}

      if args[0] == 'GetDellPPID':
         return '', {'Status':'PASS'}
      elif args[0] == 'SetResultDir' and testSwitch.FE_0134030_347506_SAVE_AND_RESTORE:
         return '', {'Status':'PASS'}
      elif args[0] == 'SendGenericFile' and testSwitch.FE_0134030_347506_SAVE_AND_RESTORE:
         return '', 0
      elif args[0] == 'ReceiveGenericFile' and testSwitch.FE_0134030_347506_SAVE_AND_RESTORE:
         return '', 0
      elif args[0] == 'GetSiteconfigSetting':
         if args[1] == 'CMSHostSite':
            return ('GetSiteconfigSetting', {'CMSHostSite': 'NA'})
         else:
            return ('',None)
      else:
         return '',{'DATA':'Error or not supported'} #"",{}

   def PChar(*args):
      pass

   def PBlock(*args):
      pass

   def GChar(*args):
      return ''

   def fn(*args, **kwargs):

      cudaNum = args[0]
      if hasattr(fn_Handlers,"fn_%s_handler" % str(cudaNum)):
         ret = eval("fn_Handlers().fn_%s_handler(args,kwargs)" % str(cudaNum))
      else:
         #TRACEBACK.print_exc()
         ret = '\x80'

   class fn_Handlers:

      def fn_1336_handler(self, *args,**kwargs):
         global fnReturnData
         retData = STRUCT.pack("HH", 0xFF, 0)
         fnReturnData = retData
         return retData

      def fn_1339_handler(self, *args,**kwargs):
         global fnReturnData
         retData = STRUCT.pack("H", 1)
         fnReturnData = retData
         return retData

      def fn_1355_handler(self, *args,**kwargs):
         global fnReturnData
         retData = STRUCT.pack(">L",128)
         fnReturnData = retData
         return retData

      def fn_1342_handler(self, *args,**kwargs):
         global fnReturnData
         retData = STRUCT.pack("fLLLHHLLL",4.5,0,00,00,264,00,80,00,00)
         fnReturnData = retData
         return retData

      def fn_1243_handler(self, *args,**kwargs):
         """ Handle seek cudacom request """
         global fnReturnData
         SEEK_PASS_STAT = 0
         SEEK_FAIL_STAT = 0xFF
         SEEK_SENSE     = 0
         retData = STRUCT.pack("HHL",SEEK_PASS_STAT,0,SEEK_SENSE)

         fnReturnData = retData
         return retData
      def fn_1308_handler(self, *args,**kwargs):
         global fnReturnData
         retData = STRUCT.pack(">H",233)
         fnReturnData = retData
         return retData


   def ReceiveBuffer(*args, **kwargs):
      global fnReturnData
      mdata = fnReturnData
      fnReturnData = '\xbe\xef\xca\xfe\x00\x00'
      return mdata


   stIgnoredParams = ['spc_id', 'timeout']
   stValidParams = stIgnoredParams.extend(allowedSelfTestParams.keys())
   
   def st(*args, **kwargs):
      global failSafeMode
      try:
         nowTime = time.ctime()
         nowTime = nowTime[0:10] + nowTime[19:24]     # remove HH:MM:SS from the ASCII time stamp to avoid driving meaningless time changes into VE comparisons.

         testNum = args[0]
         for arg in args:
            if type(arg) is dict:
               for key in arg.keys():
                  if enableCheckingSelfTestParams and key not in stValidParams:
                     print("\n\n\n*** Virtual Execution Failed ***")
                     msg = "Parameter %s is not defined in param_cd.h" % (key)
                     print(msg)
                     msg = "Virtual Execution Failed!!! " + msg
                     errorCode = 10254
                     test = 0
                     testTime = 0
                     temp = 48
                     fullStatus = ((msg,test,errorCode,testTime),temp,(12,5))
                     raise ScriptTestFailure, fullStatus
                  kwargs[key] = arg[key]
                  
         dispMsg =   "%s   ----->  S T A R T I N G   st(%d)\n" % (nowTime, testNum)
         dispMsg +=  "%s  Parameters==>  ([%d], [], %s)\n" % (nowTime, testNum, str(kwargs))
         dispMsg +=  "%s  **TestCompleted=%s,xx.xx\n" % (nowTime, testNum)
         dispMsg +=  "%s   F I N I S H E D   Testing st(%d), Test Stat: 0, Test Time: xx.xx  <-----\n" % (nowTime, testNum)
         print(dispMsg)

         if hasattr(test_Handlers,"tst_%s_handler" % str(testNum)):
            ret = eval("test_Handlers().tst_%s_handler(args,kwargs)" % str(testNum))
         else:
            ret = (0,0,0,0)
      except ScriptTestFailure, failureData:
         if not failSafeMode:
            raise
         else:
            ret = failureData[0]
      return ret

   class test_Handlers:

      def tst_149_handler(self,*args, **kwargs):
         return (149,time.ctime(),time.ctime(),149)

      def tst_510_handler(self,*args, **kwargs):
         return (510,0,0,601)

      def tst_251_handler(self,*args, **kwargs):
         #global ErrorCode
         #ErrorCode += 1
         #if ErrorCode %10 == 0:
         #   print "FAILING 251"
         #
         #   self.failureDataWrapper(251,10007, 0, 0)
         #
         #else:
         #   print "PASSING 251"
         return ('',251,0,0.2)


      def tst_47_handler(self,*args, **kwargs):
         return (47,time.ctime(),time.ctime(),47)

      def failureDataWrapper(self, test,errorCode,testTime,temp,volts = (12,5), msg = ''):
         fullStatus = ((msg,test,errorCode,testTime),temp,(volts[0],volts[1]))
         raise ScriptTestFailure, fullStatus

   def ReportVoltages():
      return "5V, 12V"

   def ScriptPause(*args):
      pass

   def DisableScriptComment(*args, **kwargs):
      pass

   def SendBuffer(*args, **kwargs):
      return ""

   def StackFrameInfo(index = -1):
      scriptFile, scriptLineNo, _, scriptMacro = TRACEBACK.extract_stack()[-index-1]
      return (scriptFile,scriptLineNo,scriptMacro)

   def GenericResultsFile(fName):
      fRef = cmFile(OS.path.join(ResultsFilePath,fName))
      return fRef

   def setVars(temp):
      global DriveVars
      temp = temp / 10.0
      DriveVars['Drive_Temperature_Deg_C'] = temp
      DriveVars['Buffer Data'] = ''

   def SetTemperatureLimits(*args, **kwargs):
      pass

   def SetTemperatureWithWait(targetTemp, *args, **kwargs):
      global curTemp

      curTemp = targetTemp
      setVars(curTemp)
      return curTemp

   def RampToTempNoWait(targetTemp, *args, **kwargs):
      # targetTemp is in tenths of degrees
      global curTemp
      setVars(curTemp)
      curTemp = targetTemp

   def RampToTempWithWait(targetTemp, *args, **kwargs):
      global curTemp
      setVars(curTemp)
      curTemp = targetTemp


   def ReleaseTheHeater():
      pass

   def YieldScript(timeout):
      pass
   def ReportDriveSN(*args):
      print("HDA SN = %s" % args[0])

   def ProcessResults(*args, **kwargs):
      pass

   def FOFexecfile(inFile):
      #import sys
      filePath = ScriptPath + inFile[0] + '\\' +  inFile[1]
      if filePath not in SYS.path:
         SYS.path.append(filePath)
      try:
         exec("import %s" % inFile[1].split('.')[0])
      except:
         execFile = open(ScriptPath + inFile[0] + '\\' +  inFile[1]).readlines()
         for line in execFile:
            exec(line)
      #__import__(ScriptPath + inFile[0] + '\\' + inFile[1])

   def RegisterResultsCallback(*args, **kwargs):
      pass

   def RegisterParamsDictionary(*args, **kwargs):
      pass

   def UnRegisterParamsDictionary(*args, **kwargs):
      pass


   XmlResultsFile = cmFile(HDASerialNumber + ".xml")
   XmlResultsFile.open('w')
   XmlResultsFile.close()

   class ScriptTestFailure(Exception):
      SlotStatus = 0
      ErrorCode = 0

def ReportErrorCode(errorCode):
   global ErrorCode
   if not errorCode == 0:
      print("Setting error code to: %s" % (errorCode,))
      ErrorCode = errorCode

def GetDriveVoltsAndAmps():
   return ((.03,.03),(1,1),(5,12))

def writeSeqNum(*args, **kwargs):
   print("Setting Sequence number to: %s" % str(args[0]))

def ReportTemperature():
   global curTemp
   return curTemp

def memoryCheck(sMsg = ""):
   return sMsg + "\n(5, 1) memoryCheck\n" + "SZ  RSS SZ DRS   VSZ   PID COMMAND\n" + "5967 4704 18616 23458 23868 14560 fof-CellPy #3      DD' -OO cellpy/cpy  5 1"

def GetLoadAverage():
   """Returns a tuple that contains the [one, five, fifteen]-minute load averages from /proc/loadavg"""
   return (0.1899, 0.2899, 0.3998)

class FOFSerialCommError(Exception):
   def __init__(self):
      pass
class FOFFileIsMissing(Exception):
   def __init__(self):
      pass
class FOFTemperatureRampFailure(Exception):
   def __init__(self):
      Exception.__init__(self)

class FOFBadPlugBits(Exception):
   def __init__(self):
      Exception.__init__(self)
class LogStInfo:

   def __init__(self):
      self.logFlag = 0
##   #def createLogFile(self,program):
##      self.fileObj = open('stLog.txt','w')
##      self.fileObj.close()

   def createLogFile(self,program,logFlag=0):
      self.logFlag = logFlag
      if self.logFlag == 1:
         self.program = program
         self.fileObj = open('%s.txt' % program,'w')
         #self.fileObj.close()

   def closeLogFile(self):
      self.fileObj.close()

   def addState(self,state):
      self.state = state

   def addEntry(self,msg):
      if self.logFlag == 1:
      #self.fileObj = open('stLog.txt','a')
      #try:
         #self.fileObj = open('%s.txt' % self.program,'a')
         self.fileObj.write('%s__%s\n' % (self.state,msg))
         #finally:
         #   self.fileObj.close()

stInfo = LogStInfo()

ConfigVars[CN]['ReplugEnabled'] = 1
ConfigVars[CN]['BenchTop'] = 0

def IsDrivePlugged():
   return True

HostItems = {'ScanTime':1,'InsertTime':1,'AutomationTime':1}
