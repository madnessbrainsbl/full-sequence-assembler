#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description:
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/11/08 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/TestParamExtractor.py $
# $Revision: #4 $
# $DateTime: 2016/11/08 00:12:47 $
# $Author: gang.c.wang $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/TestParamExtractor.py#4 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#

from Constants import *

import types
import base_TestParameters
import TestParameters
import ScrCmds
import MessageHandler as objMsg
import Utility
from Test_Switches import testSwitch

import AFH_params
import AFH_coeffs

if testSwitch.FE_0142673_399481_MOVE_SERVO_PARAMETERS_TO_SEPARATE_FILE:
   import ServoParameters
if testSwitch.WRITE_SERVO_PATTERN_USING_SCOPY:
   import Scopy_Parameters

class CParamExtractor:
   instance = None
   def __new__(self, *args, **kargs):
      if self.instance is None:
         self.instance = object.__new__(self, *args, **kargs)
      return self.instance

   def __init__(self,):
      self.dut = None
      self.driveattr = None
      self.oUtility = Utility.CUtility()
      if testSwitch.FE_0116894_357268_SERVO_SUPPLIED_TEST_PARMS:
         self.servoSuppliedParameters = {}

   def run(self,initialParam,name, dut = None, parm = ''):
      self.dut = dut
      self.driveattr = getattr(dut,'driveattr','None')

      if testSwitch.FE_0116894_357268_SERVO_SUPPLIED_TEST_PARMS:
         initialParam = self.chk_for_srvo_override(initialParam, name)

      resolvedParam = self.resolve(self.oUtility.copy(initialParam),name,parm)
      resolvedParam = self.resolveSubParams(resolvedParam,name)
      resolvedParam = self.resolveSubParams(resolvedParam,name)

      if resolvedParam == initialParam:
         return initialParam


      return resolvedParam

   def resolveSubParams(self,resolvedParam,name):
      if type(resolvedParam) == types.DictType:
         if 'EQUATION' in resolvedParam:
            resolvedParam = self.resolveEquation(resolvedParam)
         else:
            for parm in resolvedParam:
               parmValueOrg = resolvedParam[parm]
               parmValueFinal = self.resolve(parmValueOrg,name,parm)
               if type(parmValueFinal) == types.DictType or parmValueFinal != parmValueOrg:
                  resolvedParam[parm] = self.resolveSubParams(parmValueFinal,name)
      return resolvedParam

   def resolve(self,param,name, parm = ''):
      if type(param) != types.DictType:
         return param

      if not testSwitch.FE_0122823_231166_ALLOW_SWITCH_REFS_IN_TP:
         SearchList = [self.dut,self.driveattr]

      if 'EQUATION' in param:
         if not testSwitch.FE_0150973_357260_P_REDUCE_PARAMETER_EXTRACTOR_VERBOSITY:
            objMsg.printMsg('TestParamExtractor = > Dictionary name:  %s %s ,Equation: %s' % (name,parm,param['EQUATION']) )
         return self.resolveEquation(param)

      baseparam={}
      while (type(param) == types.DictType) and param.has_key('ATTRIBUTE'):             #handles nested dictionaries
         driveValue = self.findDriveValue(param)
         paramSelectedKey = ''

         #Now that you have found the drive values that the drive is, pull out the correct key in the param dictionary
         if param.has_key(driveValue):
            paramSelectedKey = driveValue
         elif param.has_key(str(driveValue)):
            paramSelectedKey = str(driveValue)
         elif param.has_key('MAP'):
            #check to see if the value is mapped to another key
            #Example driveValue = (1,4) and 'MAP': {(3,5):[(1,5),(2,5), (1,4),(2,4)],},
            for MAPitem in param['MAP'].items():
               if driveValue in MAPitem[1]:
                  paramSelectedKey = MAPitem[0]
                  if not testSwitch.FE_0150973_357260_P_REDUCE_PARAMETER_EXTRACTOR_VERBOSITY:
                     objMsg.printMsg('TestParamExtractor = > %s mapped to %s' % (driveValue,paramSelectedKey) )
                  break

         #if we still haven't found a match, check for a default
         if paramSelectedKey == '':
            if param.has_key('DEFAULT'):
               if param.has_key(param['DEFAULT']):
                  paramSelectedKey = param['DEFAULT']
               else:
                  ScrCmds.raiseException(11044,'TestParam dictionary %s is missing default key %s ' %(name,param['DEFAULT']))
               #objMsg.printMsg('TestParamExtractor = > Using Default Dictionary Key' )
            else:
               #if we have got this far, there is no key that matches the drive value and no default
               ScrCmds.raiseException(11044,'TestParam dictionary %s is missing key %s ' %(name,driveValue))

         baseparam.update(param.get('BASE',{}))
         try: # if there is a prm_name add the selections to the end, separated by commas
            baseparam['prm_name'] += '-'+paramSelectedKey
         except KeyError: pass # if there isn't a prm_name it is important not to add one.
         param = param[paramSelectedKey]

         if not testSwitch.FE_0150973_357260_P_REDUCE_PARAMETER_EXTRACTOR_VERBOSITY:
            objMsg.printMsg('TestParamExtractor = > Dictionary name:  %s %s ,Selected Dictionary Key: %s' % (name,parm,paramSelectedKey) )

      if type(param)==types.DictType and baseparam: # if this is a dictionary and we have baseparams
         baseparam.update(param) # use the leaf to update the base
         param = baseparam
      return param

   def findDriveValue(self,param):
      if testSwitch.FE_0122823_231166_ALLOW_SWITCH_REFS_IN_TP:
         SearchList = [self.dut, self.driveattr, testSwitch, testSwitch.extern]
      else:
         SearchList = [self.dut,self.dut.driveattr]

      initAttr = param['ATTRIBUTE']
      initAttrType = type(initAttr)
      if initAttrType != types.TupleType:           #handles single strings or tuples
         initAttr = (initAttr,)

      driveValue = []

      #find all matches to the ATTRIBUTE value.  The ATTRIBUTE value could be a string or a tuple of values.
      for attr in initAttr:
         #search through the list of drive values and use appropriate method to match to ATTRIBUTE value
         for variable in SearchList:
            driveValueTemp = 'NotFound'

            if type(variable) == types.DictType:
               driveValueTemp = variable.get(attr,'NotFound')
            else:
               driveValueTemp = getattr(variable,attr,'NotFound')


            if driveValueTemp != 'NotFound':        #if you have a value stop searching through the searchlist
               break
         #populate driveValue variable if a match was found
         if driveValueTemp == 'NotFound':
            ScrCmds.raiseException(11044,'TestParameter ATTRIBUTE %s does not exist as process variable.' % (initAttr[0]))
         else:
            driveValue.append(driveValueTemp)

      #set the driveValue to they same type as what is in the param keys.  Either a string or tuple
      if initAttrType == types.TupleType:
         driveValue = tuple(driveValue)
      else:
         driveValue = driveValue[0]

      return driveValue


   def resolveEquation(self,param):
      dWord = self.oUtility.ReturnTestCylWord  #provide shorter reference to use in testparameters
      return eval(param['EQUATION'])

   if testSwitch.FE_0116894_357268_SERVO_SUPPLIED_TEST_PARMS:
      def setServoParm (self, svParmParm):
         '''
         Method which takes the contents of a servo-supplied Python file of test
         parameters and incorporates it into the test parameter extraction
         process.  The servo parameters must name a parameter which has already
         been defined in TestParameters.py.
         '''
         self.servo_parms = svParmParm
         s2 = {} #local servo objects
         g = {} #globals dict
         try:
            exec(self.servo_parms, g, s2)
         except SyntaxError:
            objMsg.printMsg('Python syntax error encountered in servo parameter file.')
            raise
         self.servoSuppliedParameters.update(s2)
         return

      def chk_for_srvo_override (self, initialParam, name):
         '''
         See if the given parameter has any override settings provided in a test
         parameter file delivered with the servo release package.
         If servo did provide overrides, update the parameter here and return
         it to the caller.
         If the servo supplied parameters are a dictionary, the values associated
         with the supplied keys will be updated; values associated with other keys
         will be left alone.
         If the servo supplied parameters are a list, the entire list will be
         replaced with the servo provided version.
         '''
         if name in self.servoSuppliedParameters:
            ssp = self.servoSuppliedParameters[name]
            if type(initialParam) == types.DictType:
               initialParam.update(ssp)
            else:
               initialParam = ssp
         return initialParam

############################################################################




paramExtractor = CParamExtractor()
class CTestParam(object):
   instance = None

   def __new__(self, *args, **kargs):
      if self.instance is None:
         self.instance = object.__new__(self, *args, **kargs)
      return self.instance

   def __init__(self):
      self.dut = None

   def __getattribute__(self, name):
      try:
         return object.__getattribute__(self, name)
      except:
         try:
            return paramExtractor.run(object.__getattribute__(AFH_params, name),name, self.dut)
         except:
            pass
         try:
            return paramExtractor.run(object.__getattribute__(AFH_coeffs, name),name, self.dut)
         except:
            pass
         if testSwitch.FE_0142673_399481_MOVE_SERVO_PARAMETERS_TO_SEPARATE_FILE:
            try:
               return paramExtractor.run(object.__getattribute__(ServoParameters, name),name, self.dut)
            except:
               pass
         if testSwitch.WRITE_SERVO_PATTERN_USING_SCOPY:
            try:
               return paramExtractor.run(object.__getattribute__(Scopy_Parameters, name),name, self.dut)
            except:
               pass
         try:
            return paramExtractor.run(object.__getattribute__(TestParameters, name),name, self.dut)
         except:
            return paramExtractor.run(object.__getattribute__(base_TestParameters, name),name, self.dut)

   def setDut(self,dut):
      self.dut = dut


TP = CTestParam()

if testSwitch.FE_0116894_357268_SERVO_SUPPLIED_TEST_PARMS:
   def setSrvoOverrides(servo_parms):
      '''
      Provides external interface to internal method for accepting servo supplied
      test parameter overrides.
      '''
      paramExtractor.setServoParm(servo_parms)

if testSwitch.virtualRun:
   """
   create a flags.h style summary of the parameters in the PF3 package.
   """
   import os, copy
   class CParamSummaryCreation:
      def __init__(self):
         try:
            import WaterfallNiblets # afh unit tests don't have this file
         except:
            pass
         import Constants
         self.constants = set(dir(Constants)) # we'll ignore these

      def openFile(self):
         """
         use same method as is found in base_testSwitches.py in order to land
         VE_paramFile in the same dir.
         """
         CN = 'bench'
         paramFileName = "VE_bench_paramFile.txt"
         paramFileNameList = [os.getcwd(), 'results', CN]

         #give dir search 5 tries
         for x in xrange(5):

            paramFilePath = os.path.join(*paramFileNameList)
            if os.path.exists(paramFilePath):
               break
            else:
               paramFileNameList.insert(1, '..')

         self.paramFile = open(os.path.join(paramFilePath, paramFileName), 'w')

      def processParameter(self, theDict, keyName = None):
         """
         Recursive Reformat of parameters with TestParam-Extractor subDicts, or
         with subdicts of any flavor.
         Turns this:
         PresetAGC_InitPrm_186={
            "CWORD1"                   : (4097,),
            "MRBIAS_RANGE"             : {
                        'ATTRIBUTE':'HGA_SUPPLIER',
                        'DEFAULT':'RHO',
                        'RHO': (700, 100,),
                        'TDK': (730, 180,)
            },
         into This:
         PresetAGC_InitPrm_186={
            'CWORD1': (4097,),
            'MAX_MR_BIAS_SCALAR(HGA_SUPPLIER=RHO)': 0,
            'MAX_MR_BIAS_SCALAR(HGA_SUPPLIER=TDK)': 2,
         }
         """
         keySet = set(theDict.keys())
         if "ATTRIBUTE" in keySet and "DEFAULT" in keySet:
            attr_dflt = True
            if keyName:
               newkeyName = keyName + "(" + str(theDict["ATTRIBUTE"]) + " = %s)"
            else:
               newkeyName ="(" + str(theDict["ATTRIBUTE"]) + " = %s)"
            for key, val in theDict.items():
               if type(val) == type({}):
                  for subKey, subVal in self.processParameter(val, keyName = None).items():
                     theDict[str(newkeyName % key) + "[" + str(subKey) + "]"] = subVal
                  theDict.pop(key)
               elif key not in ('ATTRIBUTE', 'DEFAULT',):
                  theDict[newkeyName % key] = val
                  theDict.pop(key)

         else:
            for key, val in theDict.items():
               if type(val) == type({}):
                  for subKey, subVal in self.processParameter(val, keyName = None).items():
                     theDict[str(key) + "[" + str(subKey) + "]"] = subVal
                  theDict.pop(key)
         return theDict


      def getData(self, module, paramNameMatch = None):
         """
         barf
         """
         outData = {}
         objSet = set(dir(module))
         for item in objSet:
            if not paramNameMatch or paramNameMatch.search(item):
               if not item.startswith("__") and item not in self.constants: # skip __builtins__
                  attr = getattr(module, item)
                  if type(attr) == type({}):
                     outData[item] = self.processParameter(copy.deepcopy(getattr(module, item)))

         return outData, objSet

      def analyzeParameterFiles(self,):
         self.result = {
            "keySet"       : set(),
         }
         if testSwitch.WRITE_SERVO_PATTERN_USING_SCOPY:
            testParameters = ("AFH_params", "AFH_coeffs", "ServoParameters", "Scopy_Parameters", "TestParameters", "WaterfallNiblets")
         else:
            testParameters = ("AFH_params", "AFH_coeffs", "ServoParameters", "TestParameters", "WaterfallNiblets")
         for module in testParameters:
            try:
               eval(module) # afh unit tests don't have WaterfallNiblets
            except:
               continue
            parameters, keySet = self.getData(eval(module))
            self.result[module] = {
               "parameters"   : parameters,
               "keySet"       : keySet,
               }

      @staticmethod
      def formatListOfDictsAsDelimited(outputList, primaryData = [], nonPrintingData = [], delimiter = "\t"):
         """
         Format a list of dictionaries as tab, or comma delimited,
         primaryData is made to be 1st columns  nonPrintingData is ignored.
         """
         keySet = set()
         [[keySet.add(akey) for akey in aDict.keys()] for aDict in outputList]
         allKeys = primaryData + sorted(list(keySet - set(primaryData) - set(nonPrintingData)))
         dataBuffer = []
         dataBuffer.extend([key + delimiter for key in allKeys])
         dataBuffer.append('\n')
         for entry in outputList:
            for key in allKeys:
               l = []
               if key in entry:
                  l.append(str(entry[key]) + delimiter)
               else:
                  l.append(delimiter)
               dataBuffer.extend(l)

            #dataBuffer.extend([str(entry[key]) + delimiter if key in entry else delimiter for key in allKeys]) # does not work in Python <= 2.4
            dataBuffer.append('\n')
         return "".join(dataBuffer)

      def writeSummaryToFile(self,):
         l = []
         for moduleName, paramAndKeysD in sorted(self.result.items()):
            if type(paramAndKeysD) == type({}): # skip the keySet entry
               for paramName, param in sorted(paramAndKeysD["parameters"].items()):
                  if not paramName.startswith("__"): # skip __builtins__
                     for paramkKey, value in sorted(param.items()):
                        l.append({
                           "File"      : moduleName,
                           "Param"     : paramName,
                           "ParamKey"  : paramkKey,
                           "value"     : value,
                        })
         self.paramFile.write(self.formatListOfDictsAsDelimited(l))

      def run(self):
         print "hello CParamSummaryCreation"
         self.openFile()
         self.analyzeParameterFiles()
         self.writeSummaryToFile()



##############################################################################################################################

##Examples
##totalDict = {
##    1:  #self.dut type
##        {'ATTRIBUTE' : "AABType",
##         'DEFAULT': '104.28_bottle',
##         '104.28_razor':
##           {'PAD_SIZE': -1344},
##         '104.28_bottle':
##           {'PAD_SIZE': int(-7.25*256)}
##         },
##
##    9:  #MULTI NESTED,
##        {'ATTRIBUTE' : "AABType",
##         'DEFAULT': '104.28_bottle',
##         '104.28_razor':
##            {'ATTRIBUTE' : "PART_NUM",
##             '9FZ162-999':
##                {'PAD_SIZE': '-D162'},
##             '9FZXXX-999':
##                {'PAD_SIZE': '-181'},
##            },
##         '104.28_bottle':
##           {'PAD_SIZE': int(-7.25*256)}
##         },
##    10:  #LIST TYPES
##        {'ATTRIBUTE' : ("AABType","PART_NUM"),
##         'DEFAULT': ('104.28_bottle','9FZ162-999'),
##         ('104.28_razor','9FZ162-999'):
##           {'PAD_SIZE': -1344},
##         ('104.28_razor','9FZ181-999'):
##           {'PAD_SIZE': int(-7.25*256)}
##         },
##}
##brianparam = { # BASE parameters are shared by all branches
##   'ATTRIBUTE' :'HGA_SUPPLIER',
##   'BASE' : {   # the BASE parameter must be a dictionary,
##                # it is only used if the final 'leaf' is a dictionary as well.
##                # do not place any branching structure within 'BASE', this is
##                # intended as an 'end leaf' and will be enforced as such in the future.
##      'test_num' : 55,
##      'prm_name' : 'prm_055_DICE_Base_WH',
##      'timeout' : 16200,
##     },
##
##   'TDK': {
##      'prm_name' : 'prm_055_DICE_Base_WH_TDK', # Branches update BASE
##      'DICE' : (0X3D58,11, 0, 88, 64, 10, 0, 88, 64,),
##      'DURATION' : (0x0007,),
##   },
##   'RHO': { # BASE parameters can be nested as well.
##      'ATTRIBUTE' :'preampVendor',
##      'BASE': {
##         'timeout' : 20200, # Branched BASE parameters over-write less branched ones.
##         'DICE' : (0X3D58, 6, 0, 96, 64, 6, 0, 32, 64,),
##      },
##      'TI': { # prm_name is automatically updated with branch list
##         # without overwriting prm_name it is automatically set to:
##         # 'prm_055_DICE_Base_WH, RHO, TI'
##         # if you got here.
##         'DURATION' : (0x0007,),
##      },
##      'LSI': {
##         'DURATION' : (0x0005,),
##      },
##   },
##}
##heatherparm = {
##    'ATTRIBUTE':'AABType',
##    'DEFAULT':'104.28',
##    '104.28_razor': {
##        'parmname':'blah',
##        'timeout':100,
##        'CWORD1': {
##            'ATTRIBUTE':'AABType',
##            'DEFAULT': '104.28',
##            '104.28': 100,
##            '104.28_razor':200},
##        'ggg':5
##        },
##    '104.28': {
##        'parmname':'blag',
##        'timeout':'sdffffffsf',
##        'CWORD1': {
##            'ATTRIBUTE':'AABType',
##            'DEFAULT': '104.28',
##            '104.28': 100,
##            '104.28_razor':200},
##        'ggg':5
##        }
##    }
##      testparam_00 = {
##        'CWORD1': (0x0001,),
##        'LIMIT':{'EQUATION':'100*self.dut.rpm'}
##            }
## MAP WITH SINGLE ATTRIBUTES
##        a = {'ATTRIBUTE': 'seqNum',
##             'DEFAULT': 3,
##             'MAP': {1:[5,6], 2:[7,8]},
##              3:'HI',
##              1:'HELLO',
##              2: 'WHATUP'}
## MAP WITH MULTIPLE ATTRIBUTES
##        b = {'ATTRIBUTE': ('seqNum','forceMove'),
##             'DEFAULT': (3,'haha'),
##             'MAP': {(4,'hoho'):[(5,'hehe'),(6,'hehe')],
##                     (1,'hehe'):[(7,'hehe'),(8,'hoho')]},
##             (4,'hoho'):'HI',
##             (1,'hehe'):'HELLO',
##             #(3,'haha'): 'WHATUP'
##             }
