# ******************************************************************************
#
# VCS Information:
#                 $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/parmX.py $
#                 $Revision: #1 $
#                 $Change: 1047653 $
#                 $Author: chiliang.woo $
#                 $DateTime: 2016/05/05 23:40:47 $
#
# ******************************************************************************
#
# Note: parmX Revision 1 is for Version 2.7 of WinFof ONLY.
#       For WinFof Version 2.8 and later, use parmX Revision 2 or later.

import os, traceback, struct, types

####################################################################

global ParmXRef
if 'ParmXRef' not in globals(): ParmXRef = {}   # "key":{"C":code,"P":parmCount,}

def parseParamCD():
   global ParmXRef
   try:
     paramFileLoc = None
     if (isinstance(ParamCodeFile,types.TupleType) and 2 == len(ParamCodeFile)):
          configName,fileName = ParamCodeFile
          paramFileLoc =  os.path.join(ParamFilePath, configName, fileName)

     else:
         raise FOFParameterError,"ParamCodeFile should be a 2-tuple of strings containing ('configName','fileName')."

     ParmXRef = {}   # "key":(parmCode,parmCount)

     paramCodeLines = open(paramFileLoc).readlines()

     for line in paramCodeLines:

       try: _define,_name,_value = line.split()[:3]
       except ValueError: continue

       if not _define=='#define': continue

       try: key,item = _name.split("_PARM_")
       except ValueError: continue

       parmCode,dataType,statDyn,parmCount = ParmXRef.get(key,(0,2,False,0))

       _value = int(_value)
       if 'C'==item: parmCode = _value
       if 'P'==item: parmCount = _value

       #ParmXRef[key] = parmCode,parmCount
       ParmXRef[key] = parmCode,dataType,statDyn,parmCount
   except:
     ParmXRef = None
     traceback.print_exc()
     str = "Cannot parse file: %s"%paramFileLoc
     raise FOFParameterError,str

####################################################################
####################################################################
global ParmCode
def processRequest4(requestData, *args, **kargs):

   global ParmCode

   #displayBuffer(requestData)

   requestKey = ord(requestData[0])
   if requestKey == 4:
      # DON'T NEED SIZE
      # Get the two byte BigEndian write count.
      #size = requestData[1:3]
      #if not 2==len(size): raise ScriptTestFailure,"Test 0: Bad or Missing size: %s." % (`size`,)
      #size = struct.unpack('>H',size)[0]
      #if size>512: raise ScriptTestFailure,"Test 0: size %s is greater than 512." % (size,)

      requestData = requestData[3:-2]
      # if the format of data is as shown below then use the logic:
      # =====================================================================
      # |   8 bits     |    8 bits     |   Up to 18 bytes     | delimiter   |
      # |-------------------------------------------------------------------|
      # | [data-type]  |   [count]     |   [name string]      |   ,         |
      # =====================================================================
      # "data-type":   b0-b3 - data type
      #                b4    - Static or dynamic
      #                b5-b7 - Reserved for future use

      requestData = requestData.split(",")
      for item in requestData:
        key = item[2:]
        if key:             
           ParmXRef[key] = ParmCode,ord(item[0])&0x07,ord(item[0])&0x10==0x10,ord(item[1])    # code, data-type, stat-dyn, count
           ParmCode += 1
           #print "%24s:  %s"%(key,ParmXRef[key],)

      SendBuffer("\007\000\000")
   else:
     str = "Unsupported requestKey in processRequest7==>",requestKey
     raise FOFParameterError,str
####################################################################
####################################################################


#*******************************************************************************
#
#     function: parmX
#
#     designer: Sumit Gupta, J. S. Finch
#
#  description: Sets up the UPS (Uploading Parameter System)
#               Defined ParmCtrl bits:
#                    No value supplied - !!! Must be used to initialize the parameter system for the first time following each POR or FW download.
#                                            Registers callback; Executes test 0 for the first time since POR, download; Registers resulting parameter dictionary.
#                    0x8000 (bit 15) - Uploads the parameter dictionary again.
#                    0x0002 (bit  1) - Sets FW parameter report control to report all test parameters (including defaults).
#                    0x0001 (bit  0) - Sets FW aprameter report control to report ONLY host supplied parameters.
#                    0x0000          - If neither bit zero or one is set, no parameters are reported.
#
#                    Parameter errors are reported regardless of the report control setting.
#
# return value: None
#
# side effects: None
#
#    resources:
#
#*******************************************************************************
def parmX(ParmCtrl = None):
   global ParmCode
   global ParmXRef

   if ParmCtrl == None:
      # Register callback.
      RegisterResultsCallback(processRequest4, 4, 0)
      ParmCode = 0   # 32768
      # Execute test 0 with no parameters (parameters have not been uploaded yet), register resulting dictionary.
      ParmXRef = {}   # "key":{"C":code,"P":parmCount,}
      #parseParamCD() # Parses param_cd.h for the interim; Can be removed when the UPS conversion is completed.
      st(0, timeout = 300)
      RegisterParamsDictionary(ParmXRef)
      
   else:
      # Execute test 0 with caller specified parameter (parameters have been uploaded via previous call); This sets the parameter report verbosity.
      st(0, ParmCtrl = ParmCtrl, timeout = 300)
####################################################################
####################################################################

def EnableUPS(flag=1):
   if flag not in [0,1]:
     raise Exception, "Error: EnableUPS() accepts only 0 or 1 as argument"
     
   if flag: 
      parmX()       
   else:    
      global ParmXRef
      ParmXRef = {}
      RegisterParamsDictionary(None)
      
   # Update UPSEnabled flag (in the namespace)
   import __builtin__ 
   __builtin__.UPSEnabled = flag          
####################################################################

CHAR_PARM    = 0
UINT8_PARM   = 1
UINT16_PARM  = 2
UINT32_PARM  = 3
UINT64_PARM  = 4
FLOAT_PARM   = 5
DOUBLE_PARM  = 6

ParamTypeAndSpec = \
{
   CHAR_PARM:    (basestring,        'ascii',    'c',   0),
   UINT8_PARM:   ((int,long,),       'UINT_8',   'B',   0xFF),
   UINT16_PARM:  ((int,long,),       'UINT_16',  'H',   0xFFFF),
   UINT32_PARM:  ((int,long,),       'UINT_32',  'L',   0xFFFFFFFF),
   UINT64_PARM:  ((int,long,),       'UINT_64',  'Q',   0xFFFFFFFFFFFFFFFF),
   FLOAT_PARM:   ((float,int,long,), 'FLOAT',    'f',   0),
   DOUBLE_PARM:  ((float,int,long,), 'DOUBLE',   'd',   0),
}

def displayParmXRef(sortCriteria = 'code'):
   global ParmXRef

   if sortCriteria not in ['code', 'name']:
      raise Exception, "Error: displayParmXRef invalid sortCriteria!! - valid criteria ['code', 'name']; default is 'code'"

   # ParmXRef.items() return a list of (parmName, (parmCode,dataType,dynamicParm,attributeCount)). Sort based on 'sortMode'
   if sortCriteria == 'name':  dataList = sorted(ParmXRef.items(), key=lambda val:val[0])     # Sort ParmXRef with parmName.
   else:                    dataList = sorted(ParmXRef.items(), key=lambda val:val[1][0])  # Sort ParmXRef with parmCode

   print "%-18.18s %4s  %-7.7s %5s  %s %s"%('PARAMETER NAME', 'CODE', 'TYPE', 'COUNT', 'STAT/DYN', 'NAME_LEN')
   for parmName,val in dataList:

      try:    parmCode,dataType,dynamicParm,attributeCount = val 
      except: Exception, "Error: ParmXRef invalid format!!"

      try:  dataTypeReqd, dataTypeDesc, formatSpec, mask = ParamTypeAndSpec[dataType]
      except: raise  Exception,"Error: Invalid Data Type for parameter '%s'(%r). Supported DataTypes: %r"%(parmName,dataType,ParamTypeAndSpec.keys(),)

      print "%-18.18s %4d  %-7.7s %5d  %-7.7s  %8d"%(parmName, parmCode, dataTypeDesc.replace('_','').lower(), attributeCount, ['static', 'dynamic'][int(dynamicParm)], len(parmName))
