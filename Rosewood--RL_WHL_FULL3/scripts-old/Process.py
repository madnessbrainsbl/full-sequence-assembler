#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description:
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/11/07 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Process.py $
# $Revision: #4 $
# $DateTime: 2016/11/07 20:03:43 $
# $Author: gang.c.wang $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Process.py#4 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *

import os
import types
import traceback
import sys
import binascii
import struct
import time
import MessageHandler as objMsg
from Drive import objDut
import Utility
import ScrCmds
from PowerControl import objPwrCtrl
from TestParamExtractor import TP, paramExtractor
from string import lower
from Cell import theCell
from Rim import objRimType, theRim
import sptCmds
from DbLogAlias import reverseTableHeaders
from Exceptions import CRaiseException
from base_stHandler import st_Handler


#**********************************************************************************************************
#**********************************************************************************************************
class CProcess(object):
   """
      Base class for all classes used in common platform test processes.
   """
   #------------------------------------------------------------------------------------------------------#
   def __init__(self):
      self.st_Handler = st_Handler
      self.createTime = time.time()
      self.elapsedTime = 0
      self.dut = objDut

      self.oUtility = Utility.CUtility()

      self.curSeq = 0
      self.testSeqEvent = 0
      self.occurrence = 0
   #------------------------------------------------------------------------------------------------------#
   def dispClass(self):
      self.elapsedTime = time.time() - self.createTime
      return self.elapsedTime

   def dictDataObj(self, rows, cols):
      from DbLog import dbLogListObj
      # This is very similar to the tableDataObj in DBLog, but is used here to re-format data
      #  without updating the DBLog indices
      outList = []
      for rec in rows:

         if '*' in cols:
            starIdx = cols.index('*')
            buff = ''.join(rec[starIdx:])
            rec = rec[:starIdx] + [buff,]

         outList.append(dbLogListObj(dict(zip(cols,rec))))
      return outList

   #----------------------------------------------------------------------------
   def pTableSuppression(self,suppressList):
      tableList = []
      tableErrList = []
      for tableName in suppressList:
         tableCode = reverseTableHeaders.get(tableName,'ERR')
         if tableCode == 'ERR':
            tableErrList.append(tableName)

         else:
            tableList.append(tableCode)

      if len(tableList) > 10:
         tableList = tableList[:10]
      else:
         tableList = tableList + [-1]*(10-len(tableList))
      if tableErrList:
         objMsg.printMsg("Suppress Error, following tables not defined in tabledictionary:")
         objMsg.printMsg(tableErrList)

      return tableList
   #----------------------------------------------------------------------------
   def DisableParmCtrl(self, testList = None):
      '''
      Add ParmCtrl = 0x0002 at St() if test number is included in test list or in
      product over-ride dictionary

      productOvr {
         <product name> : [list of test numbers]
         Example:
         proc.LIGHTNINGBUG : [135]
      }
      test 0 and 8 cannot have ParmCtrl assigned are are excluded in St() call.
      '''
      if testList is None:
         testList = []

      # make sure they didnt send in strings
      testList = [int(test) for test in testList]

      self.dut.UPSParmCtrlTestList.extend(testList)

   #----------------------------------------------------------------------------
   def parseStArgs(self,*inPrm,**kwargs):
      parmList = []
      parmDict = {}

      for parm in inPrm:
         if type(parm) == types.IntType:
            parmList.append(parm)
         if type(parm) == types.DictType:
            name = parm.get('prm_name','missing_name')
            if parm.has_key('ATTRIBUTE') or parm.has_key('EQUATION'):
               parm = paramExtractor.run(parm,name,self.dut)
            for prm in parm:
               if type(parm[prm]) == types.DictType and (parm[prm].has_key('ATTRIBUTE') or parm[prm].has_key('EQUATION')):
                  parm[prm] = paramExtractor.run(parm[prm],name,self.dut,prm)
               if type(parm[prm]) == types.TupleType:
                  if len(parm[prm]) and type(parm[prm][0]) == types.StringType:
                     if lower(parm[prm][0]) in ['data','servo']:
                        parm[prm] = self.calcCyl(parm[prm])
            parmDict.update(self.oUtility.copy(parm))
      parmDict.update(kwargs)

      parmName = parmDict.pop('prm_name','Missing name')

      testNum = parmDict.pop('test_num',"MISSING")



      if type(testNum) == types.StringType:
         if testNum.upper()  == 'NOP':
            if testSwitch.virtualRun:
               msg = '%s__%s__%s' % (self.dut.nextOper,testNum,parmName)
               stInfo.addEntry(msg)
            return (-1, '', kwargs, [], 0, 0, parmDict.pop('prm_name','Missing name'), 0, 0)
         else:
            ScrCmds.raiseException(14824,"Unrecognized test_num value %s" % testNum)

      if testSwitch.UPS_PARAMETERS:

         try:
            testNum = int(testNum)
         except ValueError:
            ScrCmds.raiseException(14824, "test_num type not int: (%s,%s)" % (testNum, type(testNum)))

         if testNum in self.dut.UPSTests:
            parmDict = ParmFormatConverter(parmDict)

         parmDict.pop('test_num', "MISSING") # now we can get rid of 'test_num'

         if self.dut.UPSTests:
            if testNum in self.dut.UPSTests:
               parmDict['ParmCtrl'] = 0 # do not report all parameters
            elif testNum not in self.dut.UPSParmCtrlTestList and testNum in self.dut.UPSTests:
               parmDict['ParmCtrl'] = 0x0002 # Report all parameters
      if testNum < 500:
         #Only scale the timeouts if we are running mct tests that will block on script servicing time
         # Only scale up the timeouts if the baud rate drops
         timeoutfactor = max(float(Baud390000)/theCell.getBaud(), 1)
      else:
         timeoutfactor = 1

         if self.dut.IsSDI:      # for now, all SDI tests are >- 500
            objMsg.printMsg("SDI param before=%s" % parmDict)
            from SDI_Test import SDIParam
            parmDict = SDIParam(parmDict)
            parmDict.pop('stSuppressResults',0)    # remove suppression to ease SDI debugging
            objMsg.printMsg("SDI param after=%s" % parmDict)

      #PSTR EIC
      if objRimType.IsPSTR_EIC():
         timeoutfactor = timeoutfactor * 1.5

      if 'timeout' in parmDict:
         if type(parmDict['timeout']) == types.ListType:
            parmDict['timeout'] = self.oUtility.reverseTestCylWord(parmDict['timeout'])
         parmDict['timeout'] = timeoutfactor*parmDict['timeout']


      self.dut.objSeq.suppressresults = parmDict.pop('stSuppressResults',0)

      self.dut.objSeq.tablesToParse = parmDict.pop('DblTablesToParse',None)
      if self.dut.objSeq.tablesToParse:
         if not type(self.dut.objSeq.tablesToParse) in [types.ListType, types.TupleType]:
            self.dut.objSeq.tablesToParse = [self.dut.objSeq.tablesToParse,]
         self.dut.objSeq.SuprsDblObject = {}



      retry = parmDict.pop('retryCount',2)
      stpwrCycleRetryList = parmDict.pop('retryECList',[])
      retryMode = parmDict.pop('retryMode',POWER_CYCLE_RETRY)
      retryParms = parmDict.pop('retryParms', {})
      failSafe = parmDict.pop('failSafe',0)

      pwrCycleRetryList = self.oUtility.copy(TP.pwrCycleRetryList)

      if stpwrCycleRetryList != []:
         for errCode in stpwrCycleRetryList:
            pwrCycleRetryList.append(errCode)

      kwargs = {}
      kwargs['timeout'] = max(parmDict.pop('timeout',600), 30) #Never set a timeout < 30 sec
      kwargs['spc_id'] = parmDict.pop('spc_id',parmDict.pop('SPC_ID',None))
      kwargs['dlfile'] = parmDict.pop('dlfile',None)

      if kwargs['dlfile'] == None:
         kwargs.pop('dlfile')

      if kwargs['spc_id'] == None:
         kwargs.pop('spc_id')


      if parmDict.has_key('DATE'):
         from time import localtime
         year,month,day = localtime()[:3]
         MonDayString = "%02d%02d"%(month,day)
         YearString = "%04d"%(year)
         MMDD = int(MonDayString,16)
         YYYY = int(YearString,16)
         parmDict['DATE'] = (MMDD,YYYY,)

      if parmDict.has_key('ETF_LOG_DATE'):
         from time import localtime
         year,month,day = localtime()[:3]
         MonDayString = "%02d%02d"%(month,day)
         YearString = "%04d"%(year)
         MMDD = int(MonDayString,16)
         YYYY = int(YearString,16)
         parmDict['ETF_LOG_DATE'] = (MMDD,YYYY,)

      if (ConfigVars[CN].get('SUPPRESS_FW_PTABLES',0) == 1) and parmDict.has_key('SUPPRESS_TABLE_DISPLAY'):
         parmDict['SUPPRESS_TABLE_DISPLAY']  = self.pTableSuppression(parmDict['SUPPRESS_TABLE_DISPLAY'])
      elif parmDict.has_key('SUPPRESS_TABLE_DISPLAY'):
         parmDict.pop('SUPPRESS_TABLE_DISPLAY')

      if len(parmList) > 0:
         args = testNum,parmList
      else:
         args = testNum,parmDict


      # TMO dump for FA and Debug aid
      if self.dut.sptActive.getMode() == self.dut.sptActive.availModes.mctBase:
         for i in (0,len(args)-1):
            if isinstance(args[i],types.DictType):

               if args[i].has_key('TIMEOUT_TIMER_SEC') and kwargs.has_key('timeout'):
                  if testSwitch.TIMEOUT_TIMER_SEC_SUPPORT:
                     args[i]['TIMEOUT_TIMER_SEC'] = int(kwargs['timeout'] * 0.9)  # Set TIMEOUT_TIMER_SEC at 90% of CM timeout
                  else:
                     del args[i]['TIMEOUT_TIMER_SEC']
               elif kwargs.has_key('timeout') and testSwitch.TIMEOUT_TIMER_SEC_SUPPORT:
                  kwargs['TIMEOUT_TIMER_SEC'] = int(kwargs['timeout'] * 0.9)

      if testSwitch.virtualRun:
         msg = '%s__%s__%s' % (self.dut.nextOper,args,kwargs)
         stInfo.addEntry(msg)
      return testNum, args, kwargs, pwrCycleRetryList, retryMode, retry, parmName, failSafe, retryParms
   #------------------------------------------------------------------------------------------------------#
   def St(self,*inPrm,**kwargs):
      """
      St(): Wrapper for CM level run_st call that implements an ESG style command protocol "call" to run a self test on the drive firmware.
      @type *args: dict
      @param *args: generic list/dictionary of arguments
      @type **kwargs: dict
      @param **kwargs: keyword for argument list
      """

      # define a few constants
      NOT_FOUND = 0

      TupleOfTuplesDetected = NOT_FOUND  # not found

      stats = [0,0,0,0,0] #Initialize stats in case we have an exception or other issue we don't abort at the return

      testNum, args, kwargs, pwrCycleRetryList, retryMode, retry, parmName, failSafe, retryParms = self.parseStArgs(*inPrm,**kwargs)
      totalNumRetries = retry

      if testNum == -1:
         objMsg.printMsg("Skipping test call, test_num = 'NOP'.")
         return [testNum,0,-1,kwargs.get('timeout',300)]


      stackLen = len(traceback.extract_stack())
      stackIndex = 0
      for stackInfo in traceback.extract_stack():
         if stackInfo[2] =='runState':
            break
         stackIndex+=1
         stackMaxLen= stackLen-stackIndex
      else:
         stackMaxLen = 3
      executionInfoList = []
      if not testSwitch.FE_0167407_357260_P_SUPPRESS_EXECUTION_INFO:
         self.dut.curTestInfo['stackInfo'] = ''
         for stackInfoIndex in range(2,stackMaxLen):
            scriptFile,scriptLineNo,scriptMacro = StackFrameInfo(stackInfoIndex)
            executionInfo = "Execution Info: %s,%s,%s" % (scriptFile,scriptLineNo,scriptMacro)
            self.dut.curTestInfo['stackInfo'] = '%s%s,%s,%s ' % (self.dut.curTestInfo['stackInfo'],scriptFile,scriptLineNo,scriptMacro)
            executionInfoList.append(executionInfo)

      executionParameter = "Execution Parameter: %s: %s" % (testNum,parmName)

      if sptCmds.objComMode.getMode() != sptCmds.objComMode.availModes.mctBase and testNum < 500 and testNum != 8:
         #MCT test so we need to talk to the drive
         theRim.DisableInitiatorCommunication(sptCmds.objComMode)
         objPwrCtrl.changeBaud(PROCESS_HDA_BAUD)
      elif testNum > 500 and sptCmds.objComMode.getMode() != sptCmds.objComMode.availModes.intBase:
         # IO test so need to be in interface mode.
         # Loke
         objMsg.printMsg("Attr FDE_DRIVE=%s" % self.dut.driveattr['FDE_DRIVE'])
         if self.dut.driveattr['FDE_DRIVE'] == 'FDE':
            theCell.enableESlip(sendESLIPCmd = True)
            theCell.disableESlip()
            self.dut.sptActive.setMode(self.dut.sptActive.availModes.intBase)
         else:
             if not (testSwitch.M11P or testSwitch.M11P_BRING_UP):
               objPwrCtrl.powerCycle()

      if self.dut.objSeq.suppressresults:
         msg = "Suppressed output for test: %s: %s" % (testNum,parmName)
         if not (self.dut.objSeq.suppressresults & ST_SUPPRESS_SUPR_CMT) and \
            not testSwitch.FE_SGP_402984_P_SUPPRESS_SUPPRESSED_OUTPUT_INFO:
            objMsg.printMsg(msg,objMsg.CMessLvl.IMPORTANT)

         if (self.dut.objSeq.suppressresults & ST_SUPPRESS__ALL) or \
            (self.dut.objSeq.suppressresults & ST_SUPPRESS_RECOVER_LOG_ON_FAILURE) or \
            not testSwitch.BF_0124988_231166_FIX_SUPPR_CONST_IMPL:
            self.dut.dblParser.ScriptComment(msg)
            for executionInfo in executionInfoList:
               self.dut.dblParser.ScriptComment(executionInfo)
            self.dut.dblParser.ScriptComment(executionParameter)

            #add args that are dict to kwargs
            mkwargs = kwargs.copy()
            margs = []

            for arg in args:
               if type(arg) == type({}):
                  mkwargs.update(arg)
               else:
                  margs.append(arg)

            self.dut.dblParser.ScriptComment("Parameters==>  (%s, [], %s)" % (margs, mkwargs))
            self.dut.dblParser.ScriptComment("**SPC_ID32=%s  CMT=None" % (mkwargs.get('spc_id',mkwargs.get('SPC_ID',None)),))

      while retry >= 0:
         if totalNumRetries != retry: # If we're performing a retry, update the parameters
            if type(args[1]) == types.DictType:
               args[1].update(retryParms)
         try:
            #### Perform the mdw deferred spin to get the head off the ramp
            self.mdwDeferredSpin(testNum)
            ######################## DBLOG Implementation- Setup
            self.registerTest(testNum, kwargs.get('spc_id',kwargs.get('SPC_ID',None)))

            self.dut.curTestInfo['param'] = parmName
            self.dut.curTestInfo['occur'] = self.occurrence
            self.dut.curTestInfo['tstSeqEvt']= self.testSeqEvent
            self.dut.curTestInfo['test'] = testNum

            ########################
            #Test Execution
            if not self.dut.objSeq.suppressresults or testSwitch.virtualRun:
               for executionInfo in executionInfoList:
                  objMsg.printMsg(executionInfo,objMsg.CMessLvl.IMPORTANT)
               objMsg.printMsg(executionParameter,objMsg.CMessLvl.IMPORTANT)
            else:  #suppress CM printing of test params, voltage, status, etc.
               try: #Older CM code does not support DisableScriptComment
                  if testSwitch.BF_0124988_231166_FIX_SUPPR_CONST_IMPL:
                     if (self.dut.objSeq.suppressresults & ST_SUPPRESS__CM_OUTPUT) or (self.dut.objSeq.suppressresults & ST_SUPPRESS__ALL):
                        DisableScriptComment(0x0FF0)
                  else:
                     if self.dut.objSeq.suppressresults & (ST_SUPPRESS__CM_OUTPUT | ST_SUPPRESS__ALL):
                        DisableScriptComment(0x0FF0)
               except:
                  pass

            #Disable cell if we need gantry insertion protection
            if testSwitch.GANTRY_INSERTION_PROTECTION and testNum in TP.Gantry_Ins_Prot_Tests:
               RequestService('DisableCell')

            if testSwitch.virtualRun == 1:
               # find errors such as accidentally creating tuple of tuples.
               for arg in args:
                  if type(arg) == types.DictType:
                     for key in arg.keys():
                        if type(arg[key]) == types.TupleType:
                           for subParm in arg[key]:
                              if type(subParm) == types.TupleType:
                                 TupleOfTuplesDetected += 1
                                 objMsg.printMsg('Tuple of Tuples detected in args to ST() command. Args: %s' % str(args))  # !!! something went really wrong with the algorithm fail immediately
            try:
               stats = st(*args,**kwargs)
            finally:
               # Reenable cell unless disable immed is on

               if ConfigVars[CN].get('DISABLE_IMMEDIATE',0) == 0 and testSwitch.GANTRY_INSERTION_PROTECTION and testNum in TP.Gantry_Ins_Prot_Tests:
                  RequestService('EnableCell')

               if stats == None or stats == []:
                  if testSwitch.BF_0126057_231166_FAIL_INVALID_TST_RETURN:
                     stats = ['st', testNum,0,-1,parmDict.get('timeout',300)]
                  else:
                     stats = [testNum,0,-1,parmDict.get('timeout',300)]
               if self.dut.objSeq.suppressresults & (ST_SUPPRESS__CM_OUTPUT | ST_SUPPRESS__ALL) and stats[1] != 0:
                  self.dut.dblParser.ScriptComment("**TestCompleted=%s,%.2f" % (stats[1],stats[3]))
                  self.dut.dblParser.ScriptComment(" F I N I S H E D   Testing %s(%s), Test Stat: %s, Test Time: %.2f" % (stats[0], stats[1], stats[2], stats[3]))
               ######################## DBLOG Implementation- Closure
               
               self.dut.objSeq.curRegTest = 0
               
               if self.dut.objSeq.suppressresults: # Turn CM output back on
                  try: #Older CM code does not support DisableScriptComment
                     DisableScriptComment(0)
                  except:
                     pass
               # If requested data returned, reformat into list of dictionaries, using tableDataObj()
               if self.dut.objSeq.tablesToParse and not (self.dut.objSeq.SuprsDblObject == {}) : #Want data returned, and actually have data
                  for thisTable in self.dut.objSeq.SuprsDblObject.keys():
                     dataRows = self.dut.objSeq.SuprsDblObject[thisTable]['tableData']
                     tableCols = self.dut.objSeq.SuprsDblObject[thisTable]['tableCols']
                     self.dut.objSeq.SuprsDblObject[thisTable] = self.dictDataObj(dataRows,tableCols)

            retry = -1 #Exit the while loop
            #     if not then SetFailSafe() was on and we don't want an infinite loop


            if testSwitch.FE_0273221_348085_P_SUPPORT_MULTIPLE_SF3_OVL_DOWNLOAD and testNum != 8 and self.dut.registerOvl:
               if not testSwitch.FE_0314243_356688_P_CM_REDUCTION_REDUCE_FILE_MSG:
                  objMsg.printMsg('checkForOverlayKey %s' % (self.dut.registerOvl))
               self.dut.overlayHandler.checkForOverlayKey(self.dut.registerOvl, overrideMap = True)

            if testSwitch.BF_0127710_231166_FIX_COM_MODE_POST_MCT_TEST:
               if sptCmds.objComMode.getMode() != sptCmds.objComMode.availModes.mctBase and testNum < 500 and testNum != 8:
                  #Re-implement that this is MCT mode- disable initiator on previous power cycle may corrupt this.
                  sptCmds.objComMode.setMode(sptCmds.objComMode.availModes.mctBase)

               if testSwitch.FE_0151360_231166_P_ADD_SUPPORT_SAS_SED_CRT2_UNLK:
                  if testNum > 500:
                     self.dut.overlayHandler.checkForOverlayKey('IO_OVL', overrideMap = True)
                  elif testNum != 8:
                     self.dut.overlayHandler.checkForOverlayKey()

            stats = list(stats)
            self.dut.curTestInfo['param'] = 'None'
            self.dut.curTestInfo['test'] = 0
            self.dut.curTestInfo['testPriorFail'] = testNum
            self.dut.curTestInfo['tstSeqEvt']= 0
            self.st_Handler.checkCRCRetries()

            if testSwitch.BF_0126057_231166_FAIL_INVALID_TST_RETURN:
               if stats[1] != testNum and not testSwitch.virtualRun:
                  ScrCmds.raiseException(10132, "Wrong test returned from DUT %s. Indicates protocol violation and probably non test execution" % (stats,), ScriptTestFailure)


         # handle CRaiseExceptions differently
         except CRaiseException, e:
            self.updateTestTimeTable(testNum,stats,parmName)
            raise
         # handle ScriptTestFailure exception types
         except ScriptTestFailure, (failureData):
            stats[2] =failureData[0][2]
            self.updateTestTimeTable(testNum,stats,parmName)
            if testSwitch.FE_0147574_426568_P_FAIL_SAFE_BASED_ON_ERROR_CODE:
               if (type(failSafe) == types.ListType and stats[2] not in failSafe) or (type(failSafe) ==  types.IntType and failSafe != 1):
                  retry = self.st_Handler.handleScriptTestFailure(self, failureData, pwrCycleRetryList, retry, testNum, retryMode)
               else:
                  objMsg.printMsg("Fail safe enabled, ScriptTestFailure EC: %s" %failureData[0][2])
                  retry = -1
            else:
               if not failSafe:
                  retry = self.st_Handler.handleScriptTestFailure(self, failureData, pwrCycleRetryList, retry, testNum, retryMode)
               else:
                  objMsg.printMsg("Fail safe enabled, ScriptTestFailure EC: %s" %failureData[0][2])
                  retry = -1
         # handle other exception types
         except Exception, e:
            stats[2],errMsg=ScrCmds.translateErrCode(11044)
            self.updateTestTimeTable(testNum,stats,parmName)
            if testSwitch.FE_0147574_426568_P_FAIL_SAFE_BASED_ON_ERROR_CODE:
               if (type(failSafe) == types.ListType and stats[2] not in failSafe) or (type(failSafe) ==  types.IntType and failSafe != 1):
                  retry = self.st_Handler.handleGenericFailure(self, e, pwrCycleRetryList, retry, testNum, retryMode)
               else:
                  objMsg.printMsg("Fail safe enabled, Exception EC: %s" %stats[2])
                  retry = -1
            else:
               if not failSafe:
                  retry = self.st_Handler.handleGenericFailure(self, e, pwrCycleRetryList, retry, testNum, retryMode)
               else:
                  objMsg.printMsg("Fail safe enabled, Exception EC: %s" %stats[2])
                  retry = -1
         except Exception, newE:
            stats[2],errMsg=ScrCmds.translateErrCode(11044)
            self.updateTestTimeTable(testNum,stats,parmName)
            if testSwitch.FE_0147574_426568_P_FAIL_SAFE_BASED_ON_ERROR_CODE:
               if (type(failSafe) == types.ListType and stats[2] not in failSafe) or (type(failSafe) ==  types.IntType and failSafe != 1):
                  retry = self.st_Handler.handleLastDitchException(self, newE, pwrCycleRetryList, retry, testNum, retryMode)
               else:
                  objMsg.printMsg("Fail safe enabled, Exception EC: %s" %stats[2])
                  retry = -1
            else:
               if not failSafe:
                  retry = self.st_Handler.handleLastDitchException(self, newE, pwrCycleRetryList, retry, testNum, retryMode)
               else:
                  objMsg.printMsg("Fail safe enabled, Exception EC: %s" %stats[2])
                  retry = -1
         else:
            self.updateTestTimeTable(testNum,stats,parmName)
      
      if TupleOfTuplesDetected != NOT_FOUND:
         ScrCmds.raiseException(11044, 'Tuple of Tuples detected in args to ST() command.')  # !!! something went really wrong with the algorithm fail immediately


      #Save the DBLOG data to save on memory space.
      ########################
      if testSwitch.captureDriveVars == 1:
         self.dut.DriveVarsMaster.update(DriveVars)
      return stats

   #------------------------------------------------------------------------------------------------------#
   def calcCyl(self,inCyl):
      """
      calcCyl(): calculates a % of the max data or servo cylinder and adds an offset
      i.e. 'END_CYL' : ('Data',.8,200) - 'Data' use data tracks, .8 80% of track, 200 - offset
      Use 'Servo' for servo tracks
      """

      if lower(inCyl[0]) == 'data':
         mxCyl = min(self.dut.maxTrack)
      else:
         mxCyl = self.dut.maxServoTrack
      cylMult = min(inCyl[1],1)
      returnCyl = int(mxCyl*cylMult)

      if len(inCyl) == 3:              # check if offset (3rd) parameter present
         returnCyl += int(inCyl[2])    # only allow integer

      returnCyl = min(returnCyl,mxCyl)

      if DEBUG > 0:
         objMsg.printMsg("Cylinder Parameters: ", objMsg.CMessLvl.DEBUG)
         objMsg.printMsg(inCyl, objMsg.CMessLvl.DEBUG)
         objMsg.printMsg("Max Cylinder: %u" % mxCyl, objMsg.CMessLvl.DEBUG)
         objMsg.printMsg("Calculated Cylinder: %u" %returnCyl, objMsg.CMessLvl.DEBUG)

      return self.oUtility.ReturnTestCylWord(returnCyl)


   #------------------------------------------------------------------------------------------------------#
   def retryFunctionHandler(self,retryMode,testNum):
      if self.dut.sptActive.getMode() == self.dut.sptActive.availModes.mctBase:
         if retryMode == HARD_RESET_RETRY:
            pass
         elif retryMode == POWER_CYCLE_RETRY:
            self.lowLevelFIFODump()
            objPwrCtrl.powerCycle(useESlip=1)
            self.mdwDeferredSpin(testNum)    # Re-spin the drive to re-try
      elif self.dut.sptActive.getMode() in [self.dut.sptActive.availModes.intBase, self.dut.sptActive.availModes.sptDiag]:
         if retryMode == HARD_RESET_RETRY:
            if objRimType.CPCRiser():
               ICmd.HardReset()
         elif retryMode == POWER_CYCLE_RETRY:
            objPwrCtrl.powerCycle(useESlip=1)

   #------------------------------------------------------------------------------------------------------#
   def dumpLastIOCmd(self):
      self.safeTestWrapper(504,1,{},"Last IO Cmd_504")

   #------------------------------------------------------------------------------------------------------#
   def safeTestWrapper(self,testNum,spc_id,params,paramName, raiseException = 0):
      ######################## DBLOG Implementation- Setup
      self.registerTest(testNum,spc_id)
      stats = []

      try:
         try:
            SetFailSafe()
            stats = st(testNum, **params) # dump servo fifo

         except:
            if stats == None or stats == []:
               stats = (testNum,0,0,0)
            if raiseException:
               raise
      finally:
         ClearFailSafe()
         self.updateTestTimeTable(testNum,stats,paramName)
         ######################## DBLOG Implementation- Closure
         self.dut.objSeq.curRegTest = 0

   #------------------------------------------------------------------------------------------------------#
   def lowLevelFIFODump(self):
      if self.dut.sptActive.getMode() == self.dut.sptActive.availModes.mctBase:
         self.safeTestWrapper(159,1,{'CWORD1':1, 'timeout':60},'SERVO_FIFO_DUMP_159')

   #------------------------------------------------------------------------------------------------------#
   def mdwDeferredSpin(self, testNum):
      if self.dut.IsSDI:
         objMsg.printMsg("SDI skipping mdwDeferredSpin")
         return

      if self.dut.sptActive.getMode() == self.dut.sptActive.availModes.mctBase:
         if self.dut.mdwCalComplete == 0 and \
                  not testSwitch.extern.FE_0122976_325269_MINIMIZE_NO_SPIN_TEST_LIST and \
                  not testNum in testSwitch.disable_tests_deferred_spin:

            try:
               self.safeTestWrapper(1,1,TP.MDWUncalSpinup,'MDWUncalSpinup', 1)
            except:
               self.safeTestWrapper(1,1,{'CWORD1': 0x0001},'Last_Ditch_Spin')

   #----------------------------------------------------------------------------
   def registerTest(self,testNum,spcID):
      self.curSeq,self.occurrence,self.testSeqEvent = self.dut.objSeq.registerCurrentTest(testNum)
      self.dut.objSeq.curRegSPCID = spcID


   #----------------------------------------------------------------------------
   def updateTestTimeTable(self,testNum,stats,parmName):
      ######################## DBLOG Implementation- Closure
      #objDut.dblData.getDBL()
      memVals = objMsg.getMemVals()
      cpuElapsedTime = objMsg.getCpuEt()
      if self.dut.objSeq.curRegSPCID == None:
         spcId = 0
      else:
         spcId = self.dut.objSeq.curRegSPCID

      self.dut.dblData.Tables('TEST_TIME_BY_TEST').addRecord(
         {
         'SPC_ID': spcId,
         'OCCURRENCE': self.occurrence,
         'SEQ':self.curSeq,
         'TEST_SEQ_EVENT': self.testSeqEvent,
         'TEST_NUMBER': testNum,
         'ELAPSED_TIME': '%.2f' % stats[3],
         'PARAMETER_NAME':parmName,
         'TEST_STATUS':stats[2],
         'CELL_TEMP':"%0.1f" % (ReportTemperature()/10.0),
         'SZ': memVals.get('VSZ',''),
         'RSS': memVals.get('RSS',''),
         'CPU_ET': '%.2f' % cpuElapsedTime,
         })

   #------------------------------------------------------------------------------------------------------#
   def upLoadAttribute(self, codetype, filename):
      self.dut.driveattr['DL_'+codetype] = filename

   #------------------------------------------------------------------------------------------------------#
   def setMDWCalState(self, mdwCalState = 0):
      self.dut.mdwCalComplete = self.dut.driveattr['MDW_CAL_STATE'] = mdwCalState
      objMsg.printMsg("MDW_CAL_STATE = %s" % mdwCalState)


   #------------------------------------------------------------------------------------------------------#
   def dnldCode(self, codeType, fileName='', timeout = 200, interfaceDownload = False):
      pd = None
      if len(fileName) == 0:
         from  PackageResolution import PackageDispatcher
         pd = PackageDispatcher(self.dut, codeType)
         fileName = pd.getFileName()

         if fileName in  ['',None, []]:
            if testSwitch.FailcodeTypeNotFound and not testSwitch.virtualRun:
               ScrCmds.raiseException(10326,'Code not found in codeType resolution.')
            else:
               objMsg.printMsg("*"*20 + "Warning: Skipping %s Download" % codeType, objMsg.CMessLvl.IMPORTANT)
               return None

         if type(fileName) in [types.ListType, types.TupleType] and codeType.find('CFW') != -1:
            self.dut.overlayHandler.downloadOverlay(fileName[0])
            fileName = fileName[1]

      self.dut.reset_DUT_dnld_segment(codeType)

      dnldDict = {'test_num':8,
                  'prm_name':'Download_Code_8',
                  'dlfile':(CN,fileName),
                  'timeout':timeout }
      dnldDict['retryMode'] = POWER_CYCLE_RETRY

      ret = self.st_Handler.dnldCode(self, codeType, fileName, dnldDict, interfaceDownload = interfaceDownload)
      if pd and pd.flagFileName:
         testSwitch.importExternalFlags(pd.flagFileName)

      return ret


   #----------------------------------------------------------------------------
   def dnldInitiator(self, reqCodeType ='INC'):
      import string
      from  PackageResolution import PackageDispatcher
      try:
         prm_535_InitiatorRev = {
            "test_num" : 535,
            "REG_ADDR" : (0x0000,),
            "REG_VALUE" : (0x0000,),
            "TEST_OPERATING_MODE" : (0x0002,),
            "TEST_FUNCTION" : (0x8800,),
            "BAUD_RATE" : (0x0000,),
            "EXPECTED_FW_REV_1" : (0x0000,),
            "DRIVE_TYPE" : (0x0000,),
         }
         self.St(prm_535_InitiatorRev)
      except:
         try:
            self.St({'test_num':535,'timeout':300},0x8002)
         except:
            ScrCmds.raiseException(14551,'535 Initiator inquiry failed')

      curFileName = DriveVars.get('Initiator Code','')

      from  PackageResolution import PackageDispatcher
      fileName = PackageDispatcher(self.dut, reqCodeType).getFileName()

      if fileName in  ['',None, []]:
         if testSwitch.FailcodeTypeNotFound and not testSwitch.virtualRun:
            ScrCmds.raiseException(10326,'Code not found in codeType resolution.')
         else:
            objMsg.printMsg("*"*20 + "Warning: Skipping %s Download" % reqCodeType, objMsg.CMessLvl.IMPORTANT)
            return None

      if type(fileName) in [types.ListType, types.TupleType] and reqCodeType.find('INC') != -1:
         self.dut.overlayHandler.downloadOverlay(fileName[0])
         fileName = fileName[1]

      for initType in ['FFK20','H30FC']:
         if curFileName.find(initType) != -1 and fileName.find(initType) != -1:
            fileNameList = fileName.split('.')
            fileNameList[1] = string.zfill(fileNameList[1],8)
            relFileName = '-'.join(fileNameList[:3])

            relCurFileName = curFileName[:curFileName.rfind('-')]
            if relFileName != relCurFileName:
               st(8,0,0,0,dlfile=(CN,fileName))
            else:
               objMsg.printMsg('Initiator card has %s, skip download' % fileName)
            break
      else:
         if not testSwitch.virtualRun:
            ScrCmds.raiseException(14551,'Code not compatible')

#---------------------------------------------------------------------------------------------------------#
class CCudacom:
   """
      Base class for Cudacom functions used in common platform test processes.
   """
   ERROR_PACKET = '\x46\x00\x01'
   OVL_REQ_PACKET = '\x46\x00\x00\x02'
   CUDACOM_COMPLETE_PACKET = '\xbe\xef\xca\xfe'
   #------------------------------------------------------------------------------------------------------#
   def __init__(self):
      self.dut = objDut
      self.oUtility = Utility.CUtility()


   #------------------------------------------------------------------------------------------------------#
   def isCompletionPacket(self,buf):
      """
      Check to see if the packet passed is the completion packet.
      Completion packet is 0xbeefcafe followed by the 2 byte error code.
      Return 1 if packet is a completion packet, 0 otherwise.
      """
      if len(buf) == 6 and buf[0:4] == self.CUDACOM_COMPLETE_PACKET:
         return 1
      return 0

   def isOverlayRequest(self,buf):
      if buf[0:4] == self.OVL_REQ_PACKET:
         return True
      else:
         return False

   #------------------------------------------------------------------------------------------------------#
   def ReceiveResults(self,timeout=60,displayError=1):
      """
      Get the result (of a preceeding fn call) from the serial port.
      Optionally pass a timeout value (default = 5 seconds)
      Optionally pass displayError=0 to supress displaying a nonzero error code.
      Returns <result data>
      Raises exception on error
      """
      bfrList = []
      finalPacket = 0
      
      startTime = time.time()
      
      while finalPacket == 0:
         try:
            buf = ReceiveBuffer(60,checkSRQ=1)
            if DEBUG > 0:
               objMsg.printMsg("Cudacom - ReceiveResults Debug: Return Buf: %s" % binascii.hexlify(buf))

            if self.isOverlayRequest(buf):
               #Need to handle overlay request
               return buf,0
            if self.isCompletionPacket(buf) == 1:
               finalPacket = 1
               errorCode = struct.unpack(">H",buf[4:6])[0]
               if DEBUG > 0:
                  objMsg.printMsg("Cudacom - ReceiveResults errorCode unpacked: %s" % errorCode)
               if errorCode != 0 and displayError == 1:
                  objMsg.printMsg("Error code %d reported" % errorCode)
               break
            else:
               elapsedTime = time.time() - startTime
               if elapsedTime > timeout:
                  raise
               bfrList.append(buf)
         except:
            bfrList = []
            objMsg.printMsg("CCudacom - ReceiveResults: Receive Buffer error - Failure: Exception: %s, Message: %s" % (sys.exc_info()[0], sys.exc_info()[1]))
            ScrCmds.raiseException(11077,"CudaCom ReceiveResults failed")
      return ''.join(bfrList), errorCode


   #------------------------------------------------------------------------------------------------------#
   def Fn(self,*args,**kwargs):

      if DEBUG > 0:
         objMsg.printMsg("CCudacom - Fn Debug: Arguments passed: %s" % str(args))
      retries = kwargs.get('retries',0)
      pwrCycRet = kwargs.get('pwrCycRet',0)
      timeout = kwargs.get('timeout',60 * 10)
      while retries >= 0:
         try:
            if testSwitch.FE_0247538_402984_MASK_CUDACOM_ARGS_16BIT & PY_27:
               fn_args = map(self.oUtility.mask_16bit, args)                     # convert signed to unsgined integer arguments
               fn(*fn_args)
            else:
               fn(*args)

            buf, errorCode = self.ReceiveResults(timeout)
            if self.isOverlayRequest(buf):
               while self.isOverlayRequest(buf):
                  self.dut.overlayHandler.processOverlayRequest(buf,currentTemp=0,drive5=0,drive12=0,collectParametric=0)
                  buf, ec = self.ReceiveResults(timeout)
            retries = -1
         except:
            objMsg.printMsg("CCudacom - Fn: fn call failed: Exception: %s, Message: %s" % (sys.exc_info()[0], sys.exc_info()[1]))
            retries -= 1
            if retries < 0:
               ScrCmds.raiseException(11077,"CudaCom fn call failed")
            if pwrCycRet:
               objPwrCtrl.powerCycle(useESlip=1)
      if DEBUG > 0:
         objMsg.printMsg("CCudacom - Fn Debug: Buffer returned: %s" % binascii.hexlify(buf) )
      return buf, errorCode

   #-------------------------------------------------------------------------------------------------------
   def displayMemory(self, buf, baseAddr=0,addressableUnit=1,unitsPerLine=16,groupSize=4,startingByte=0,forceLen=0):
      """
      Print a binary string buffer to the string in a "memory dump" format::
          address     hex data for 0..(N-1)
          address+N   hex data for N..(2N-1)
          address+2N  hex data for 2n..(3N-1)
          etc.
      @param buf:               Buffer to display
      @param baseAddr:          Base address to display
      @param addressableUnit:   Number of bytes per Address value
      @param unitsPerLine:      Number of address values displayed per line
      @param groupSize:         Number of addressable units to display per grouping
      @param startingByte:      Starting byte of data to display
      @param forceLen:          Total Number of bytes to display (overwrites natural length of the input data)
      """
      data = binascii.hexlify(buf)

      forceLen *= 2             # convert to ASCII (2 memory bytes per ascii character)
      startingByte *= 2
      bytesToDisplay = len(data) - startingByte

      # Overwirte the natural data length, if requested
      if forceLen > 0 and forceLen < bytesToDisplay:
        bytesToDisplay = forceLen

      cnt=0
      objMsg.printMsg("Address     Data")
      # Convert addressableUnit from bytes to nibbles
      addressableUnit*=2
      baseAddrStr = '%08x ' % baseAddr
      dataStr = ''
      for i2 in range(startingByte,startingByte+bytesToDisplay,addressableUnit):
        dataStr = '%s %s'%(dataStr,data[i2:i2+addressableUnit])
        cnt+=1
        if cnt % groupSize == 0:
          dataStr = '%s%s'%(dataStr, " ")

        if cnt == unitsPerLine and i2 < (startingByte + bytesToDisplay) - addressableUnit:
          cnt=0
          dataStr = '%s  %s'%(baseAddrStr,dataStr)
          objMsg.printMsg(dataStr)
          objMsg.printMsg('')
          dataStr = ''
          baseAddr += unitsPerLine
          #objMsg.printMsg('%08x ' % baseAddr)
          baseAddrStr = '%08x ' % baseAddr

   #-------------------------------------------------------------------------------------------------------
   def DumpMemory(self, buf, baseAddr=0,addressableUnit=1,unitsPerLine=16,groupSize=4,startingByte=0,forceLen=0):
      """
      Print a binary string buffer to the string in a "memory dump" format::
          address     hex data for 0..(N-1)
          address+N   hex data for N..(2N-1)
          address+2N  hex data for 2n..(3N-1)
          etc.
      @param buf:               Buffer to display
      @param baseAddr:          Base address to display
      @param addressableUnit:   Number of bytes per Address value
      @param unitsPerLine:      Number of address values displayed per line
      @param groupSize:         Number of addressable units to display per grouping
      @param startingByte:      Starting byte of data to display
      @param forceLen:          Total Number of bytes to display (overwrites natural length of the input data)
      """
      data = binascii.hexlify(buf)

      forceLen *= 2             # convert to ASCII (2 memory bytes per ascii character)
      startingByte *= 2
      bytesToDisplay = len(data) - startingByte

      # Overwirte the natural data length, if requested
      if forceLen > 0 and forceLen < bytesToDisplay:
        bytesToDisplay = forceLen

      cnt=0
      objMsg.printMsg("Address      0    1    2    3     4    5    6    7     8    9    A    B     C    D    E    F")
      # Convert addressableUnit from bytes to nibbles
      addressableUnit*=2            
      baseAddrStr = '%08x ' % baseAddr
      dataStr = ''
      for i2 in range(startingByte,startingByte+bytesToDisplay,addressableUnit):
        dataStr = '%s %s'%(dataStr,data[i2:i2+addressableUnit])
        cnt+=1
        if cnt % groupSize == 0:
          dataStr = '%s%s'%(dataStr, " ")

        if cnt == unitsPerLine and i2 < (startingByte + bytesToDisplay):
          cnt=0
          dataStr = '%s  %s'%(baseAddrStr,dataStr)
          objMsg.printMsg(dataStr)          
          dataStr = ''
          baseAddr += unitsPerLine
          #objMsg.printMsg('%08x ' % baseAddr)
          baseAddrStr = '%08x ' % baseAddr

   #-------------------------------------------------------------------------------------------------------

   def servocmd(self,cmd=1,parm0=0, parm1=0, parm2=0, parm3=0):
      """
      Issue servo command in WinFOF
      @param cmd: servo command
      @param parm0: command parameter 0 (default:0)
      @param parm1: command parameter 1 (default:0)
      @param parm2: command parameter 2 (default:0)
      @param parm3: command parameter 3 (default:0)
      """
      st([11], [], {'timeout': 120, 'PARAM_0_4': (cmd,parm0,parm1,parm2,parm3)})

