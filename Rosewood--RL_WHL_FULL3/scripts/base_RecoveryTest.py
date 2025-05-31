#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Customer Screens
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_RecoveryTest.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_RecoveryTest.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from StateTable import StateTable, StateParams
import types, os, time, re
from TestParamExtractor import TP
from CTMX import CTMX

from State import CState

import MessageHandler as objMsg
import Utility, traceback
from sptCmds import comMode
from PowerControl import objPwrCtrl

import ScrCmds

import PIF
from base_GOTF import CGOTFGrading

from Process import CProcess
from Rim import objRimType, theRim,SATA_RiserBase, SAS_RiserBase
from sptCmds import objComMode
import sptCmds
from ICmdFactory import ICmd
from Utility import CUtility

import Process
oProc = Process.CProcess()
from serialScreen import sptDiagCmds
oSerial = sptDiagCmds()
IR_XprefixWhenStartOriginalFailOper    = True
IR_Report_IR_EC_WhenFailDuringRecovery = 1
IR_ReportFirstEC  = 1
IR_HybridReportEC = (1 & IR_ReportFirstEC)  #if fail same Oper report Re-run EC, if fail difference Oper report first-run EC.
IR_ErrorCode      = 14999
IR_ExcludeECList  = [14555,11044,12169]
IR_DefaultName    = 'XXXX-XXXXX'
IR_DefaultVersion = 'N'
IR_OPER_LIST      = ['PRE2','CAL2','FNC2','CRT2','FIN2','CUT2','IOSC2','SPSC2']
if ConfigVars[CN].get('BenchTop', 0) == 1:
   ADG_PROCESS_TIME = 1 #second
else:
   ADG_PROCESS_TIME = 600 #second
MAX_STATE_RETRY = {
    'DEFAULT' : 2,
    'FNC2':{
       'READ_SCRN':2 
    },

}
MAX_DRIVE_REPLUG = {
    'DEFAULT' : 5,
    'PRE2': 5,
    'CAL2': 5,
    'FNC2': 5,
    'CRT2': 5,
    'FIN2': 5,
    'CUT2': 5,
    'IOSC2': 5,
    'SPSC2': 5,
}
MAX_RERUN_OPER = {
    'DEFAULT' : 1,
    'PRE2': 1,
    'CAL2': 1,
    'FNC2': 1,
    'CRT2': 1,
    'FIN2': 1,
    'CUT2': 1,
    'IOSC2': 1,
    'SPSC2': 1,
}
#=========================================================================================================
class dynamicDict(dict):
    """Dynamic creation of data structures. The iDea from perl's autovivification feature."""
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value

#=========================================================================================================

def evalPhaseOut(dictOrString):
   """dict was previously a dict encased in a string - if/else for backwards compatability
   Calls should eventually be removed and this function deleted
   """
   if type(dictOrString)==type({}):    # check that dictOrString is a dictionary
      return dictOrString              # new method
   else:                               # must be old string method
      return eval(dictOrString)        # old g

###########################################################################################################
#class CTableUtility:
##------------------------------------------------------------------------------------------------------#
#   """ Class to handle Image File Downloads """
#   def __init__( self, dut ):
#      self.dut = dut
##------------------------------------------------------------------------------------------------------#
#   def queryFromTable(self,table,failcolumn,failcode,failcriteria_op,failcriteria_val,failed_meas_values,failcriteria_vio,failcriteria_filterDict):
#      """ using gotf tools to fail drive for a test.
#      for  Business_Group = ALL case. all parms defined in GOTF_table.xml """
#            ScrCmds.raiseException(failcode,"the %s column in the %s table failed, because the measured value(s): %s , are not %s the limit of %s.\n the num_violations allowed = %s. the filter dictionary is: %s " %
#                     (failcolumn,failtable,failed_meas_values,failcriteria_op,failcriteria_val,failcriteria_vio,failcriteria_filterDict))
#
#   #------------------------------------------------------------------------------------------------------#

class CRecoveryUtility(CState):
   """
   This is a state to inherit fail_proc states from,
   it will handle the failure saving / not allowing a drive to pass.
   The inherited state needs only define the tests desired in the fail sequence.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, depList=[]):
      CState.__init__(self, dut, depList)
   #------------------------------------------------------------------------------------------------------#
   def appendState(self, oper, state):
      if oper in self.dut.stateSequence:
         if not state in self.dut.stateSequence[oper]:
            self.dut.stateSequence[oper].append(state)
      else:
         self.dut.stateSequence[oper]=[]
         self.dut.stateSequence[oper].append(state)

   #------------------------------------------------------------------------------------------------------#
   def runState(self, oper, state,irParams):
      try:
         TraceMessage( '--- iRecovery : Running Oper - %s --- State - %s ---' % (oper, state) )
         ReportStatus('%s --- %s' % (oper, state))
         ScriptComment('State Sequence Number: %d' % self.dut.seqNum)
         ScriptComment('- '*20 + 'IR_' + state + ' : BEGIN   ' + ' -'*20)
         ScriptComment('From iRecovery Rerun At State %s @%s' %(state,oper))
         objMsg.printMsg('<<< Test failure Handling >>>')
         self.dut.ctmxState = CTMX('STATE') # Create CTMX entry for this state
         self.dut.curTestInfo = {'state': state,'param': 'None', 'occur': '', 'tstSeqEvt': 0, 'test': 0, 'seq':self.dut.seqNum, 'stackInfo':'', 'testPriorFail': ''}

         if not self.depList==[] and not state in self.dut.stateDependencies:       #Track state dependencies
            self.dut.stateDependencies[state] = self.depList

         # try to disply failure data
         try: objMsg.printMsg('Fail Data: %s'%self.dut.failureData)
         except: pass

         #try to save failure data
         try: tmpFailData = CUtility().copy(self.dut.failureData)
         except: pass

         try:
            #self.run() # run the fail_proc tests
            if StateTable[oper][state][MODULE]:
               cmd = 'import %s' % StateTable[oper][state][MODULE]; exec(cmd)
         
            TraceMessage( '--- StateMachine Running Oper - %s --- Switching to State - %s ---' % (oper, state) )
            # instantiate/execute the Class Object
            self.dut.currentState = state
            
            # Determine state sequence per operation
            self.appendState(oper, state)
            #StateMachineInst.appendState(oper, state)
         
            self.dut.stateDBLogInfo.setdefault(self.dut.currentState,[])
            scriptModule      = StateTable[oper][state][MODULE]
            classMethod       = StateTable[oper][state][METHOD]
            stateTransitions  = evalPhaseOut(StateTable[oper][state][TRANS])
         
            stateTransitions['rerunState'] = state
            
            if StateParams[oper].has_key(state):
               inputParameters = evalPhaseOut(StateParams[oper][state])
            else:
               inputParameters = {} # default to empty dict
            if len(irParams) > 0:
               objMsg.printMsg("Original State Params %s: " % inputParameters)
               inputParameters = evalPhaseOut(irParams)
               objMsg.printMsg("iRecovery State Params %s: " %inputParameters)
            cmd = '%s.%s(self.dut, %s).run()' % (scriptModule, classMethod, inputParameters)
            try:
               exec(cmd)
               return True
               objMsg.printMsg('Perform recovery @%s is complete' %state)
            except:
               objMsg.printMsg("Traceback... \n%s" % traceback.format_exc())
               return False
         finally:
            self.dut.failureData = tmpFailData # recover the failure data
         ScriptComment('- '*20 + 'IR_' +  state + ' : COMPLETE' + ' -'*20)
      except:
         objMsg.printMsg("Traceback... \n%s" % traceback.format_exc())
         
         return False
         
         
def isIRDict(obj):
   if type(obj) in [types.DictType,type(dynamicDict({}))]:
      return True
   elif isinstance(obj,dict):
      return True
   else:
      return False
def getFullOperateName(keywordName='XXXX-XXXXX'):
   OperateNamePrefix  = 'INDEX_'
   return OperateNamePrefix + str(keywordName).replace('-','_')[0:10]
   
def reOper(self,*args,**kwargs):
   try:
      if isIRDict(args[0]):
         restartAtOper = str(args[0]['OPER'])
      else:
         restartAtOper = str(args[0])
      failedEC,failedOper,failedState,failedTest = args[1]
      recoveryCmd = kwargs.get('recoveryCmd',{})
      indexCmd = kwargs.get('indexCmd',{})

      
      counterName = "IR_RUN_" + restartAtOper + "_CNT"
      #counter = DriveAttributes.get(counterName,0)
      if not testSwitch.virtualRun:
         if ConfigVars[CN].get('BenchTop', 0) == 0: #if in real production use RequestService to get more update Attributes
            name, returnedData = RequestService('GetAttributes', (str(counterName)))
            objMsg.printMsg("iRecovery : GetAttributes %s result = name : %s, data : %s" %(counterName,`name`,`returnedData`))               
         else:
            name,returnedData    = ('GetAttributes',{counterName: DriveAttributes.get(counterName,'UNKNOWN')})
      else:
         name,returnedData = ('GetAttributes',{counterName: 'UNKNOWN'})
         
      counter = returnedData.get(counterName,'UNKNOWN')
      try:
         counter = int(counter)
      except:
         counter = 0
      reOperRetryLimit = MAX_RERUN_OPER.get(restartAtOper,MAX_RERUN_OPER.get('DEFAULT',1))
      objMsg.printMsg("Found command Re-%s from %s, This drive use to Re-%s %s time/times , Retry Limit is %s" %(restartAtOper,counterName,restartAtOper,counter,reOperRetryLimit))
      if int(counter) < int(reOperRetryLimit):
         objMsg.printMsg("Re-Oper at %s %s time/times, Go to  %s" %( restartAtOper, counter,restartAtOper) )
         
         self.dut.nextOperOverride = restartAtOper
         counter = int(counter) + 1
         objMsg.printMsg("increase %s to %s" %(counterName,counter))
         
         DriveAttributes[counterName] = counter
         DriveAttributes['IR_BF_EC'] = failedEC
         DriveAttributes['IR_BF_OPER'] = failedOper
         DriveAttributes['IR_BF_STATE'] = failedState
         DriveAttributes['IR_BF_TEST'] = failedTest
         DriveAttributes['IR_RE_OPER'] = 'RUNNING'
         #==============================================================================================
         objMsg.printMsg("#"*50)
         objMsg.printMsg("Set R operation to wait ADG accessing !")
         DriveAttributes['IR_ADG_HOLDING'] = "WAIT"
         RequestService('SetOperation',('R' + self.dut.nextOper[0:4],))
         ReportErrorCode(int(self.dut.failureData[0][2]))
         #Send attributes and parametrics
         RequestService('SendRun', 1)
         RequestService('SetOperation',(self.dut.nextOper,))
         objMsg.printMsg("Wait the drive for ADG process !")
         objMsg.printMsg("iRecovery awaiting ADG process time is %s sec" %ADG_PROCESS_TIME)
         time.sleep(ADG_PROCESS_TIME) #Wait ADG process time to access this drive
         
         attrName = 'IR_ADG_HOLDING'
         
         if not testSwitch.virtualRun:
            if ConfigVars[CN].get('BenchTop', 0) == 0: #if in real production use RequestService to get more update Attributes
               name, returnedData = RequestService('GetAttributes', (attrName))
               objMsg.printMsg("iRecovery : GetAttributes %s result = name : %s, data : %s" %(attrName,`name`,`returnedData`))               
            else:
               name,returnedData    = ('GetAttributes',{attrName: DriveAttributes.get(attrName,'UNKNOWN')})
         else:
            name,returnedData = ('GetAttributes',{attrName: 'UNKNOWN'})

         if returnedData.get('IR_ADG_HOLDING','UNKNOWN') == "HOLD":
            self.dut.nextState = 'FAIL_PROC'
            self.dut.stateTransitionEvent = 'fail'
            return False
         else:
            DriveAttributes['IR_ADG_HOLDING'] = "DONE"
         #==============================================================================================
         self.dut.irReOper = True
         self.dut.breakCmd = True
         return True
      else:
         if indexCmd < len(recoveryCmd):
            objMsg.printMsg("Try to optimized by remaining command")
            return True
         else:
            objMsg.printMsg("Can't re-run @%s since retry limit exceed !!!!!" %restartAtOper)
            return False
   except:
      DriveAttributes['IR_STATUS'] = 'EXCURSION'
      objMsg.printMsg('iRecovery: Re-Oper command fail')
      objMsg.printMsg("Traceback... \n%s" % traceback.format_exc())
      self.dut.report_IR_EC = True
      return False
   
def reState(self,*args,**kwargs):
   try:
      objMsg.printMsg("#"*50)
      objMsg.printMsg('iRecovery: execute state %s @%s' %(args[0]['STATE'],args[0]['OPER']))
      failedEC,failedOper,failedState,failedTest = args[1]
      
      execState = args[0]['STATE']
      execOper  = args[0]['OPER']
      failsafe = args[0].get('SET_FAIL_SAFE',0)
      stateParams = args[0].get('PARAMS',{})
      
      temp_state = self.dut.nextState
      temp_oper = self.dut.nextOper
      self.dut.nextState = execState
      self.dut.nextOper = execOper
      objMsg.printMsg('Set nextState to %s and nextOper to %s' %(execState,execOper))
      runStateStat =  CRecoveryUtility(self.dut).runState(execOper,execState,stateParams)
      objMsg.printMsg('Get back nextState (%s) and nextOper (%s) ' %(temp_state,temp_oper))
      self.dut.nextState = temp_state
      self.dut.nextOper = temp_oper 
      return (runStateStat or failsafe)
      
   except:
      failsafe = args[0].get('SET_FAIL_SAFE',0)
      DriveAttributes['IR_STATUS'] = 'EXCURSION'
      objMsg.printMsg('iRecovery: Re-State command fail')
      self.dut.nextState = temp_state
      self.dut.nextOper = temp_oper
      objMsg.printMsg('Get back nextState (%s) and nextOper (%s) ' %(temp_state,temp_oper))
      objMsg.printMsg("Traceback... \n%s" % traceback.format_exc())
      self.dut.report_IR_EC = True
      return False or failsafe

def execCmd(self,*args,**kwargs):
   try:
      if isIRDict(args[0]):
         LimitSameOperSameEC = int(args[0].get('EXEC_TIMES_LIMIT',1))
         cmdToExec = args[0].get('CMD','')
         failsafe = args[0].get('SET_FAIL_SAFE',0)
      else:
         cmdToExec = args[0]
         failsafe = 0
      objMsg.printMsg("#"*50)
      objMsg.printMsg('execute command : %s' %cmdToExec)
      #failedEC,failedOper,failedState,failedTest = args[1]
      exec(cmdToExec)
      return True
   except:
      if isIRDict(args[0]):
         failsafe = args[0].get('SET_FAIL_SAFE',0)
      else:
         failsafe = 0
      DriveAttributes['IR_STATUS'] = 'EXCURSION'
      objMsg.printMsg('iRecovery: execute command fail')
      objMsg.printMsg("Traceback... \n%s" % traceback.format_exc())
      self.dut.report_IR_EC = True
      return False or failsafe

def rePlug(self,*args,**kwargs):
   objMsg.printMsg("#"*50)
   objMsg.printMsg("Re-Plug command detected with arguments : %s" %repr(args))
   try:
      
      if isIRDict(args[0]):
         LimitSameOperSameEC = int(args[0].get('EXEC_TIMES_LIMIT',1))
         if args[0].get('NEXT_STATE','INIT') not in ['?', 'INIT','NONE'] :
            DriveAttributes['NEXT_STATE'] = args[0].get('NEXT_STATE','INIT')
      else:
         LimitSameOperSameEC = args[0]
      failedEC,failedOper,failedState,failedTest = args[1]
      recoveryCmd = kwargs.get('recoveryCmd',{})
      indexCmd = kwargs.get('indexCmd',{})
      
      
      
      counterName = failedOper + "_" + failedEC + "_CNT"
      if int(DriveAttributes.get(counterName, 0)) == 0:
         #initail rule counter
         DriveAttributes[counterName] = 1
         objMsg.printMsg('DriveAttributes["%s"] = 1' %counterName)
         counter = 1
      else:
         counter = int(DriveAttributes[counterName]) + 1
         DriveAttributes[counterName] = counter
         objMsg.printMsg('Increase counter,  DriveAttributes["%s"] = %s' %(counterName,counter))
      objMsg.printMsg('>>>>> counter = %s, Allow Repeat Fail (same OPER and same EC) = %s <<<<<' %(counter,LimitSameOperSameEC))
      if int(counter) > MAX_DRIVE_REPLUG.get(failedOper,MAX_DRIVE_REPLUG.get('DEFAULT',1)):
         objMsg.printMsg("Re-Plug at %s %s times, Retry limit exceed" %(failedOper, MAX_DRIVE_REPLUG.get(failedOper,MAX_DRIVE_REPLUG.get('DEFAULT',1))) )
         return False
      elif int(counter) <= LimitSameOperSameEC:
         self.dut.irReplug = True
         self.dut.replugECMatrix.update({int(failedEC) : []})
         objMsg.printMsg('self.dut.replugECMatrix : %s' % repr(self.dut.replugECMatrix))
         objMsg.printMsg('Add %s to replugECMatrix' %failedEC)
         objMsg.printMsg('iRecovery: Re-Plug completed')
         self.dut.breakCmd = True
         return True
      else:
         if indexCmd < len(recoveryCmd):
            objMsg.printMsg("Try to optimized by remaining command")
            return True
         else:
            objMsg.printMsg("Can't re-run state since retry limit exceed !!!!!")
            return False
   except:
      DriveAttributes['IR_STATUS'] = 'EXCURSION'
      objMsg.printMsg("Traceback... \n%s" % traceback.format_exc())
      objMsg.printMsg('iRecovery: Re-Plug command fail')
      self.dut.report_IR_EC = True
      return False
   
def reRunState(self,*args,**kwargs):
   try:
      if isIRDict(args[0]):
         LimitSameRuleBase = int(args[0].get('EXEC_TIMES_LIMIT',1))
         failsafe = args[0].get('SET_FAIL_SAFE',0)
      else:
         LimitSameRuleBase = args[0]
         failsafe = 0
      recoveryCmd = kwargs.get('recoveryCmd',{})
      indexCmd = kwargs.get('indexCmd',{})
      objMsg.printMsg("#"*50)
      objMsg.printMsg("Re-Try same state command detected with arguments : %s" %repr(args))
      counterName = 'EC' + "".join([str(e) + "_" for e in args[1]]) + 'CNT'
      objMsg.printMsg('Increase counter of %s Rule' %counterName)
      counter = eval('getattr(self.dut,counterName,0)')
      objMsg.printMsg('counter = %s' %counter)
      if counter == 0:
         #initail rule counter
         exec('self.dut.%s = 0' %counterName)
      if counter < LimitSameRuleBase:
         self.dut.breakCmd = True
        
         exec('self.dut.%s = self.dut.%s + 1' %(counterName,counterName))
         objMsg.printMsg('self.dut.%s = %s' %(counterName,eval('getattr(self.dut,counterName,0)')))
         return True
      else:
         if indexCmd < len(recoveryCmd):
            objMsg.printMsg("Try to optimized by remaining command")
            return True
         else:
            objMsg.printMsg("Can't re-run state since retry limit exceed !!!!!")
            return False
   except:
      if isIRDict(args[0]):
         failsafe = args[0].get('SET_FAIL_SAFE',0)
      else:
         failsafe = 0

      DriveAttributes['IR_STATUS'] = 'EXCURSION'
      objMsg.printMsg('iRecovery: Re-Tune command fail')
      objMsg.printMsg("Traceback... \n%s" % traceback.format_exc())
      self.dut.report_IR_EC = True
      return False or failsafe
 
def setRuleLimit(self,*args,**kwargs):
   try:
      recoveryCmd = kwargs.get('recoveryCmd',{})
      indexCmd = kwargs.get('indexCmd',{})
      counterName = 'SET_EC' + "".join([str(e) + "_" for e in args[1]]) + 'CNT'
      objMsg.printMsg('Increase counter of %s Rule' %counterName)
      counter = eval('getattr(self.dut,counterName,0)')
      objMsg.printMsg('counter = %s' %counter)
      if counter == 0:
         #initail rule counter
         exec('self.dut.%s = 0' %counterName)
      if counter < args[0]:   
         exec('self.dut.%s = self.dut.%s + 1' %(counterName,counterName))
         objMsg.printMsg('self.dut.%s = %s' %(counterName,eval('getattr(self.dut,counterName,0)')))
         return True
      else:
         objMsg.printMsg("rule-base limit exceed, Can't perform remaining command!!!!!")
         return False
   except:
      DriveAttributes['IR_STATUS'] = 'EXCURSION'
      objMsg.printMsg('iRecovery: Set Rule Base Limit command fail')
      objMsg.printMsg("Traceback... \n%s" % traceback.format_exc())
      self.dut.report_IR_EC = True
      return False
def increaseCounterOfOperateQueue(self,*args,**kwargs):
   try:
      attrCounterName = args[0]
      if not testSwitch.virtualRun:
         if ConfigVars[CN].get('BenchTop', 0) == 0: #if in real production use RequestService to get more update Attributes
            name, returnedData = RequestService('GetAttributes', (attrCounterName))
            objMsg.printMsg("iRecovery : GetAttributes %s, result = name : %s, data : %s" %(attrCounterName,`name`,`returnedData`))           
         else:
            name,returnedData    = ('GetAttributes',{attrCounterName: DriveAttributes.get(attrCounterName,'UNKNOWN')})
      else:
         name,returnedData = ('GetAttributes',{attrCounterName: 'UNKNOWN'})
      
      ATTR_COUNTER_VALUE = returnedData.get(attrCounterName,'UNKNOWN')
      try:
         ATTR_COUNTER_VALUE = int(ATTR_COUNTER_VALUE)
      except:
         ATTR_COUNTER_VALUE = 0
      
      loopCounter = max([ATTR_COUNTER_VALUE,getattr(self.dut,attrCounterName,0)])
      loopCounter = loopCounter + 1
      cmd = "DriveAttributes['%s'] = %s" %(attrCounterName,loopCounter)
      objMsg.printMsg("cmd : %s" %(cmd))
      exec(cmd)
      cmd = "self.dut.%s = %s" %(attrCounterName,loopCounter)
      objMsg.printMsg("cmd : %s" %(cmd))
      exec(cmd)
      objMsg.printMsg('iRecovery: Increase Operation counter completed')
      return True
   except:
      DriveAttributes['IR_STATUS'] = 'EXCURSION'
      objMsg.printMsg('iRecovery: Set Rule Base Limit command fail')
      objMsg.printMsg("Traceback... \n%s" % traceback.format_exc())
      self.dut.report_IR_EC = True
      return False
def updateNameList(self,*args,**kwargs):
   try:
      updateName = args[0]
      objMsg.printMsg("'%s' Sent to 'IR_NAME_LIST' Attribute" %(updateName))
      try:
         sentName = updateName[0:10] #Fix name as 10 char
      except:
         sentName = IR_DefaultName
      self.dut.currentIRName = sentName 
      return True
   except:
      DriveAttributes['IR_STATUS'] = 'EXCURSION'
      objMsg.printMsg('iRecovery: Set Rule Base Limit command fail')
      objMsg.printMsg("Traceback... \n%s" % traceback.format_exc())
      self.dut.report_IR_EC = True
      return False
def goToState(self,*args,**kwargs):
   try:
      objMsg.printMsg("#"*50)
      objMsg.printMsg("Go-to-State command detected with arguments : %s" %repr(args))
      recoveryCmd = kwargs.get('recoveryCmd',{})
      indexCmd = kwargs.get('indexCmd',{})
      if isIRDict(args[0]):
         jumpToState = args[0]['STATE']
         LimitSameRuleBase = int(args[0].get('EXEC_TIMES_LIMIT',1))
      elif type(args[0]) == types.ListType:
         jumpToState = args[0][0]
         LimitSameRuleBase = args[0][1]
      elif type(args[0]) == types.StringType:
         jumpToState = args[0]
         LimitSameRuleBase = 1
      counterName = 'EC' + "".join([str(e) + "_" for e in args[1]]) + 'CNT'
      objMsg.printMsg('Increase counter of %s Rule' %counterName)
      counter = eval('getattr(self.dut,counterName,0)')
      objMsg.printMsg('counter = %s' %counter)
      if counter == 0:
         #initail rule counter
         exec('self.dut.%s = 0' %counterName)
      if counter < LimitSameRuleBase:
         self.dut.goToState = jumpToState
         self.dut.breakCmd = True
         exec('self.dut.%s = self.dut.%s + 1' %(counterName,counterName))
         objMsg.printMsg('self.dut.%s = %s' %(counterName,eval('getattr(self.dut,counterName,0)')))
         return True
      else:
         if indexCmd < len(recoveryCmd):
            objMsg.printMsg("Try to optimized by remaining command")
            return True
         else:
            objMsg.printMsg("Can't re-run state since retry limit exceed !!!!!")
            return False
   except:
      DriveAttributes['IR_STATUS'] = 'EXCURSION'
      objMsg.printMsg('iRecovery: Re-Tune command fail')
      objMsg.printMsg("Traceback... \n%s" % traceback.format_exc())
      self.dut.report_IR_EC = True
      return False 
   
def CustomFunction(self,*args,**kwargs):
   try:
      objMsg.printMsg("#"*50)
      objMsg.printMsg("Re-Custom Function command detected with arguments : %s" %repr(args))
      if isIRDict(args[0]):
         customModule = args[0]['PATH'][0]
         customMethod = args[0]['PATH'][1]
         failsafe = args[0].get('SET_FAIL_SAFE',0)
         LimitSameRuleBase = int(args[0].get('EXEC_TIMES_LIMIT',1))
      else:
         customModule = args[0][0]
         customMethod = args[0][1]
         failsafe = 0
      exec('import %s' % customModule)
      cmd = '%s.%s(self.dut, %s).run()' %(customModule,customMethod,self.params)
      objMsg.printMsg('cmd: %s' %cmd)
      exec(cmd)
      return True
   except:
      if isIRDict(args[0]):
         failsafe = args[0].get('SET_FAIL_SAFE',0)
      else:
         failsafe = 0
      DriveAttributes['IR_STATUS'] = 'EXCURSION'
      objMsg.printMsg('iRecovery: Re-Tune command fail')
      objMsg.printMsg("Traceback... \n%s" % traceback.format_exc())
      self.dut.report_IR_EC = True
      return False or failsafe

def invalidCmd(self,*args,**kwargs):
   objMsg.printMsg("#"*50)
   objMsg.printMsg("In invalidCmd")
   
   
def validateKeyword(oDict,keyword):
   if keyword in oDict.get('EXCEPTION',[]):
      objMsg.printMsg('%s in EXCEPTION list' %keyword)
      return False
   else:
      return True


def getRecoveryCmd(self,failedEC='',failedOper='',failedState='',failedTest='',DEBUG = 0):
   def getMapRules(oDict,keyword):
      if not validateKeyword(oDict,keyword): return # Ensure the keyword not in 'EXCEPTION' list
      output = oDict.get(keyword,{})
      if not len(output):
         output = oDict.get('ALL',{})
         if not len(output):
            output = oDict.get('DEFAULT',{})
            getFromKey = 'DEFAULT'
         else:
            getFromKey = 'ALL'
      else:
         getFromKey = keyword
      return output,getFromKey
      
   def selectByOption(ListOfcmdList,DEBUG = 0):
      selectedRule = []
      for cmdList in ListOfcmdList:
         if not isIRDict(cmdList):
            objMsg.printMsg("command list type is not iRecovery Dict, cmdList type is %s and content is %s " %(type(cmdList),`cmdList`))
            continue
         if not cmdList.has_key('RECOVERY_COMMAND'):
            objMsg.printMsg("Not found key 'RECOVERY_COMMAND'")
            continue
         for cmd in cmdList['RECOVERY_COMMAND']:
               if isIRDict(cmd.values()[0]):
                  if DEBUG:
                     objMsg.printMsg('%s argument is dict need to validate (args = %s and type = %s)' %(cmd.keys(),cmd.values()[0],type(cmd.values()[0])))
                  if 'OPERATE_QUEUE' in cmd.keys():
                     try:
                        attrCounterName = getFullOperateName(str(cmdList['RECOVERY_COMMAND'][0]['NAME'])[0:10])
                     except:
                        objMsg.printMsg("Traceback... \n%s" % traceback.format_exc())
                        objMsg.printMsg("iRecovery : not found keyword 'NAME' in RECOVERY_COMMAND[0] or something wrong with 'NAME' set Recovery command to empty list >> []")
                        return []                       
                     if not testSwitch.virtualRun:
                        if ConfigVars[CN].get('BenchTop', 0) == 0: #if in real production use RequestService to get more update Attributes
                           name, returnedData = RequestService('GetAttributes', (attrCounterName))
                           objMsg.printMsg("iRecovery : GetAttributes %s, result = name : %s, data : %s" %(attrCounterName,`name`,`returnedData`))           
                        else:
                           name,returnedData    = ('GetAttributes',{attrCounterName: DriveAttributes.get(attrCounterName,'UNKNOWN')})
                     else:
                        name,returnedData = ('GetAttributes',{attrCounterName: 'UNKNOWN'})
                     
                     ATTR_COUNTER_VALUE = returnedData.get(attrCounterName,'UNKNOWN')
                     try:
                        ATTR_COUNTER_VALUE = int(ATTR_COUNTER_VALUE)
                     except:
                        ATTR_COUNTER_VALUE = 0
                     
                     loopCounter = max([ATTR_COUNTER_VALUE,getattr(self.dut,attrCounterName,0)])
                     selectedOperate = 'OPERATION_' + str(loopCounter)
                     objMsg.printMsg("iRecovery : OPERATE_QUEUE detected gonna run %s" %(selectedOperate))
                     
                     if dict(cmd.values()[0]).has_key(selectedOperate):
                        selectedRule = []
                        selectedRule.append({'INCR_QUEUE_CNT':attrCounterName})
                        selectedRule.extend(dict(cmd.values()[0])[selectedOperate])
                        objMsg.printMsg("iRecovery : selectedRule >> %s" %selectedRule)
                        return selectedRule
                     else:
                        objMsg.printMsg("iRecovery : OPERATE_QUEUE is not define %s set iRecovery command to empty list >> []" %selectedOperate)
                        return []
                  if dict(cmd.values()[0]).has_key('ATTR_PRE_VALIDATE'):
                     notMatch = False
                     for checkItem in cmd.values()[0]['ATTR_PRE_VALIDATE']:
                        flag, value = checkItem.iteritems().next()
                        attrName = str(flag)
                        if not testSwitch.virtualRun:
                           if ConfigVars[CN].get('BenchTop', 0) == 0: #if in real production use RequestService to get more update Attributes
                              name, returnedData = RequestService('GetAttributes', (attrName))
                              objMsg.printMsg("iRecovery : GetAttributes %s result = name : %s, data : %s" %(attrName,`name`,`returnedData`))               
                           else:
                              name,returnedData    = ('GetAttributes',{attrName: DriveAttributes.get(attrName,'UNKNOWN')})
                        else:
                           name,returnedData = ('GetAttributes',{attrName: 'UNKNOWN'})
                           
                        attrValue = returnedData.get(attrName,'UNKNOWN')
                        objMsg.printMsg('Validate Attribute "%s": Actual: %s Rule: %s' %(flag,attrValue,value))
                        if type(value) == types.ListType:
                           if attrValue not in value:
                              if DEBUG:
                                 objMsg.printMsg('%s with argument %s not pass validate skip adding to recovery command list' %(cmd.keys()[0],cmd.values()[0]))
                              notMatch = True
                        elif type(value) == types.StringType:      
                           if attrValue != value:
                              if DEBUG:
                                 objMsg.printMsg('%s with argument %s not pass validate skip adding to recovery command list' %(cmd.keys()[0],cmd.values()[0]))
                              notMatch = True
                              break
                     if notMatch:
                        continue
                         
                  if dict(cmd.values()[0]).has_key('IF'):
                     notMatch = False
                     if type(cmd.values()[0]['IF']) == types.ListType:
                        for checkItem in cmd.values()[0]['IF']:
                           objMsg.printMsg('Checking condition %s, value = %s' %(checkItem, eval(checkItem)))
                           if not eval(checkItem):
                              notMatch = True
                              break
                     elif type(cmd.values()[0]['IF']) == types.StringType:
                        if not eval(cmd.values()[0]['IF']):
                            objMsg.printMsg('Checking condition %s, value = %s' %(cmd.values()[0]['IF'], eval(cmd.values()[0]['IF'])))
                            notMatch = True
                            break
                     if notMatch:
                        continue
                  if dict(cmd.values()[0]).has_key('TEST_SWITCH_PRE_VALIDATE'):
                     notMatch = False
                     for checkItem in cmd.values()[0]['TEST_SWITCH_PRE_VALIDATE']:
             
                        flag, value = checkItem.iteritems().next()
                        objMsg.printMsg('Validate Test Switch "%s": Actual: %s Rule: %s' %(flag,getattr(testSwitch, flag),value))
                        if getattr(testSwitch, flag) != value:
                           notMatch = True
                           break
                     if notMatch:
                        continue
                      
                  if dict(cmd.values()[0]).has_key('DUT_PRE_VALIDATE'):
                     notMatch = False
                     for checkItem in cmd.values()[0]['DUT_PRE_VALIDATE']:
                  
                        flag, value = checkItem.iteritems().next()
                        objMsg.printMsg('Validate self.dut.%s: Actual: %s Rule: %s' %(flag,getattr(self.dut, flag, None),value))
                        attrValue = getattr(self.dut, flag, None)
                        if type(value) == types.ListType:
                           if attrValue not in value:
                              if DEBUG:
                                 objMsg.printMsg('%s with argument %s not pass validate skip adding to recovery command list' %(cmd.keys()[0],cmd.values()[0]))
                              notMatch = True
                        elif type(value) == types.StringType:      
                           if attrValue != value:
                              if DEBUG:
                                 objMsg.printMsg('%s with argument %s not pass validate skip adding to recovery command list' %(cmd.keys()[0],cmd.values()[0]))
                              notMatch = True
                              break
                     if notMatch:
                        continue
                  
               if DEBUG:
                  objMsg.printMsg('Add %s to recovery command list' %(cmd))
               selectedRule.append(cmd)
               
         
      return selectedRule
   
   def lookUpRules(failedEC='',failedOper='',failedState='',failedTest='',DEBUG = 0):
      recoveryCmd = []
      commandList = []
      commonCommand = {'RECOVERY_COMMAND':[]}
      GlobalCmd = []
      ruleBaseName = ""
      RecoveryRules = RecoveryRulesBased
      RuleMaping_by_EC,ruleFromEC         = getMapRules(RecoveryRules,failedEC)
      RuleMaping_by_Oper,getFromOPER      = getMapRules(RuleMaping_by_EC,failedOper)
      RuleMaping_by_State,getFromState    = getMapRules(RuleMaping_by_Oper,failedState)
      RuleMaping_by_Test,getFromTest      = getMapRules(RuleMaping_by_State,failedTest)

      if RecoveryRules.has_key(failedEC):
         if RecoveryRules[failedEC].has_key('RECOVERY_COMMAND'):
            commonCommand['RECOVERY_COMMAND'].extend(RecoveryRules[failedEC]['RECOVERY_COMMAND'])
         if RecoveryRules[failedEC].has_key(failedOper):
            if RecoveryRules[failedEC][failedOper].has_key('RECOVERY_COMMAND'):
               commonCommand['RECOVERY_COMMAND'].extend(RecoveryRules[failedEC][failedOper]['RECOVERY_COMMAND'])
            if RecoveryRules[failedEC][failedOper].has_key(failedState):
               if RecoveryRules[failedEC][failedOper][failedState].has_key('RECOVERY_COMMAND'):
                  commonCommand['RECOVERY_COMMAND'].extend(RecoveryRules[failedEC][failedOper][failedState]['RECOVERY_COMMAND'])
         
      try:
         ruleBaseName = RuleMaping_by_Test['RECOVERY_COMMAND']['NAME']
      except:
         ruleBaseName = ruleFromEC + "-" + getFromOPER + "-" + getFromState + "-" + getFromTest
      

      if DEBUG:
         objMsg.printMsg('commonCommand : %s' %commonCommand)
         
      recoveryCmd.append(RuleMaping_by_Test)
      
      if DEBUG:
         objMsg.printMsg('RuleMaping_by_Test : %s' %RuleMaping_by_Test)
      commandList.append(commonCommand)
      if DEBUG:
         objMsg.printMsg('commandList added commonCommand : %s' %commandList)
      commandList.extend([e for e in recoveryCmd if len(e)]) #filter empty dict
      if DEBUG:
         objMsg.printMsg('commandList added recoveryCmd : %s' %commandList)

      
      
      if len(commandList) >= 1:
               selectedRule = selectByOption(commandList,DEBUG = 0)
               return selectedRule
      else:
         return []
         
   if DEBUG:
      objMsg.printMsg('Getting Failure Information >>> fail from EC: %s, Oper: %s, State:%s and Test:%s'%(failedEC,failedOper,failedState,failedTest)) 
   ####### Add BEGIN COMMON command .........
   recoveryCmdExec =[]
   #recoveryCmdExec = getInitailCommonCmd()
   recoveryCmdExec = lookUpRules(failedEC,failedOper,failedState,failedTest,DEBUG)
   #reset log file by IR operation
   #recoveryCmdExec.insert(0,{'EXEC':"updateAndResetResults(self, errorCode = failedEC, errMsg = 'iRecovery restart' ,forceToFailOper = 'IR')"})
   if DEBUG:
      objMsg.printMsg('Recovery command list: %s' %recoveryCmdExec)
   if len(recoveryCmdExec):
      #firstRule = recoveryCmdExec[0];
      return recoveryCmdExec
      #return firstRule
   else:
      return {}


def execRecovery(self,failedInfo, params={}):
   try:
      failedEC,failedOper,failedState,failedTest = failedInfo
      recoveryKeyWord = ['ATTR_PRE_VALIDATE','TEST_SWITCH_PRE_VALIDATE','DUT_PRE_VALIDATE','IF']

      objMsg.printMsg("Do recovery for: failedEC: %s,failedOper: %s,failedState: %s,failedTest: %s" %(failedEC,failedOper,failedState,failedTest))
      objMsg.printMsg("The state list which use to recovery >>> %s" % getattr(self.dut, "RecoveryStateList", 'NONE'))

      cmdDict           = getRecoveryCmd(self,str(failedEC),str(failedOper),str(failedState),str(failedTest),DEBUG=0)
      retryByOper       = MAX_STATE_RETRY.get(self.dut.nextOper,{})
      retry_state_limit = retryByOper.get(failedState,retryByOper.get('DEFAULT',2))
      
      if getattr(self.dut, "RecoveryStateList", []).count(failedState) >= retry_state_limit:
         objMsg.printMsg("retry at %s %s times, Retry limit exceed" %(failedState,getattr(self.dut, "RecoveryStateList", []).count(failedState)) )
         return False
      
      self.dut.RecoveryStateList.append(failedState)
      if not len(cmdDict):
         objMsg.printMsg('***** No specific rule to recover  *****')
         self.dut.stateTransitionEvent = 'fail'
         return False
      ############## Recover command detected ##############

      objMsg.printMsg("Recovery with command : %s" %cmdDict)
      self.dut.IR_Active               = True
      DriveAttributes['IR_ACTIVE']     = 'Y'
      DriveAttributes['IR_CMS_CONFIG'] = self.dut.driveattr['CMS_CONFIG']
      DriveAttributes['IR_FAIL_EC']    = failedEC
      DriveAttributes['IR_FAIL_OPER']  = failedOper
      DriveAttributes['IR_FAIL_STATE'] = failedState
      DriveAttributes['IR_FAIL_TEST']  = failedTest
      
      FNC2OperIndex = self.dut.operList.index("FNC2")
      currentOperIndex = self.dut.operList.index(self.dut.nextOper)
      
      if (self.dut.nextOper == 'FNC2' and riserType == 'HDSTR') or ((currentOperIndex > FNC2OperIndex) and self.dut.HDSTR_SP2_PROC == 'Y'):
         DriveAttributes['IR_HSP_ACTIVE'] = 'Y'
      if self.dut.IR_RUN_CNT <= 0:
         objMsg.printMsg('***** This drive do iRecovery 1 time  *****')
         self.dut.IR_RUN_CNT = 1
      else:
         self.dut.IR_RUN_CNT = self.dut.IR_RUN_CNT + 1
         objMsg.printMsg('***** This drive do iRecovery %s times  *****' %self.dut.IR_RUN_CNT)
         
      self.dut.PendingMerge2_IR_RUN_LIST   = self.dut.PendingMerge2_IR_RUN_LIST  + failedEC + '/'
      
      objMsg.printMsg('#'*20 + '  Start perform each command which specific in rule-based  ' + '#'*20 + '\n')
      indexCommand = 0
      for dictCmd in cmdDict:
         for  key, value in dictCmd.items():
            indexCommand = indexCommand + 1
            values = { 
                       'REOPER'        :    reOper,
                       'RESTATE'       :   reState, 
                       'CUSTOM'        :    CustomFunction,
                       'REPLUG'        :    rePlug,
                       'EXEC'          :      execCmd,
                       'RERUN_STATE'   :     reRunState,
                       'GO_TO_STATE'   :     goToState,
                       'RETRY_LIMIT'   : setRuleLimit,
                       'INCR_QUEUE_CNT': increaseCounterOfOperateQueue,
                       'NAME'          : updateNameList,
                       #'ADG_DISPOSITION': #Awaiting development,
                     }
            if key in recoveryKeyWord:
               continue
            if not values.get(key, invalidCmd)(self,value,failedInfo,indexCmd = indexCommand,recoveryCmd = cmdDict):
               objMsg.printMsg("Traceback... \n%s" % traceback.format_exc())
               objMsg.printMsg('***** RECOVERY FAILED *****')
               self.dut.stateTransitionEvent = 'fail'
               self.dut.IR_Active = False
               return False
            if getattr(self.dut,"breakCmd",False) == True:
               self.dut.breakCmd = False
               objMsg.printMsg('break command detected, Ignore remaining command')
               self.dut.IR_Active = False
               return True
      self.dut.IR_Active = False
   except:
      DriveAttributes['IR_STATUS'] = 'EXCURSION'
      objMsg.printMsg("Traceback... \n%s" % traceback.format_exc())
      objMsg.printMsg('***** EXECUTE RECOVERY FAILED *****')
      self.dut.IR_Active = False
      return False

   else:
      objMsg.printMsg('Restart at failed state to make sure that we can pass with iRecovery')
      objMsg.printMsg('Restarting @%s state: %s'  %(self.dut.nextOper,self.dut.failureState))
      self.dut.IR_Active = False
      return True

###########################################################################################################
class CRecovery(CState):
   """
   Perform intelligent recovery (iRecovery) before decided to fail the drive.
   """
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      objMsg.printMsg('Recovery Test')
      try: from Utility import CUtility;tmpFailData = CUtility().copy(self.dut.failureData)
      except: pass
      try:
         if testSwitch.UPS_PARAMETERS:
            from UPS import upsObj
            upsObj.setupUPS()
         if not self.__selectIRecovery():
            objMsg.printMsg("iRecovery is rejected by iRecovery selection")
            return
         if self.dut.nextOper not in IR_OPER_LIST:
            objMsg.printMsg("self.dut.nextOper not in %s" %IR_OPER_LIST)
            return
         before_faillureData = self.dut.failureData
         objMsg.printMsg('self.dut.failureData:%s' % str(self.dut.failureData[0]))
         objMsg.printMsg('before_faillureData:%s' % str(before_faillureData))
         
         ec = str(self.dut.failureData[0][2])
         failTest = str(self.dut.failureData[0][1])
         failedInfo = (ec,self.dut.nextOper,self.dut.failureState,failTest)
         objMsg.printMsg('failedInfo:%s' % `failedInfo`)
         objMsg.printMsg('*'*50 + ' Start recovery process ' + '*'*50 )
         

         if execRecovery(self,failedInfo, params={}):
            self.dut.IR_Active = False
            ec,self.dut.nextOper,self.dut.failureState,failTest = failedInfo
            self.dut.nextState = self.dut.failureState
            self.dut.stateTransitionEvent = 'restartAtState'
            objMsg.printMsg('#'*50 + ' Finished recovery process...' + '#'*50 + "\n" )
            DriveAttributes['IR_STATUS'] = 'PASS'
            self.dut.ir_status = 'PASS'
            if not testSwitch.virtualRun:
               self.handleRulesBasedEffectiveness()
         else:
            self.dut.IR_Active = False
            ec,self.dut.nextOper,self.dut.failureState,failTest = failedInfo
            self.dut.failureData = tmpFailData # recover the failure data
            self.dut.stateTransitionEvent = 'fail'
            objMsg.printMsg('#'*50 + ' Finished recovery process...' + '#'*50 + "\n" )
            DriveAttributes['IR_STATUS'] = 'FAIL'
            self.dut.ir_status = 'FAIL'
            if not testSwitch.virtualRun:
               self.handleRulesBasedEffectiveness()
            if IR_Report_IR_EC_WhenFailDuringRecovery and getattr(self.dut,'report_IR_EC',False):
               raise

         if getattr(self.dut,'goToState','NONE') != 'NONE':
            objMsg.printMsg('*'*50 + ' Force restart at State ' + self.dut.goToState + ' detected ' + '*'*50 )
            self.dut.nextState = self.dut.goToState
            self.dut.stateTransitionEvent = 'restartAtState'
            self.dut.goToState = 'NONE'
         if getattr(self.dut,'irReplug',0) == True:
            objMsg.printMsg('*'*50 + ' Force re-plug detected ' + '*'*50 )
            self.dut.nextState = 'FAIL_PROC'
            self.dut.stateTransitionEvent = 'fail'
         if getattr(self.dut,'irReOper',False) == True:
            objMsg.printMsg('*'*50 + ' Force Re-Oper detected ' + '*'*50 )
            self.dut.nextState = 'FAIL_PROC'
            self.dut.stateTransitionEvent = 'fail'
            
      except:
         objMsg.printMsg("Get failure info (iRecovery : Last fail infomation in iRecovery)")
         objMsg.printMsg("Traceback... \n%s" % traceback.format_exc())
         
         self.dut.stateTransitionEvent = 'fail'
         if not IR_Report_IR_EC_WhenFailDuringRecovery:
            self.dut.failureData = tmpFailData # recover the failure data
         if IR_Report_IR_EC_WhenFailDuringRecovery:
            ScrCmds.raiseException(IR_ErrorCode,'Report iRecovery when fail During Recovery')
   
   
   def __selectIRecovery(self,DebugMsg=1):
         from iRecovery_selection import iRecovery_Config
         iRecoveryAttrList = {'SN':HDASerialNumber, 'PN':DriveAttributes['PART_NUM'], 'SBG':DriveAttributes['SUB_BUILD_GROUP']}
         if DebugMsg:
            ScrCmds.statMsg('------ iRecovery Selection ------')
            ScrCmds.statMsg('Serial Num = %s'%str(iRecoveryAttrList['SN']))
            ScrCmds.statMsg('Part Number = %s'%str(iRecoveryAttrList['PN']))
            ScrCmds.statMsg('Sub Build Group = %s'%str(iRecoveryAttrList['SBG']))
   
         keyList = iRecovery_Config.keys()
         keyList.sort()
         run_iRecovery = False
         for key in keyList:
            for attribute in iRecovery_Config[key]:
               if not iRecoveryAttrList.has_key(attribute):
                     ScrCmds.raiseException(11044, 'iRecoveryConfig attribute "%s" is undefined in iRecovery_selection.py Valid attributes = %s'%(attribute,iRecoveryAttrList.keys()))
               if iRecovery_Config[key][attribute] == '*':
                  run_iRecovery = True
               elif attribute == 'SN':
                  if iRecoveryAttrList['SN'][1:3] == iRecovery_Config[key]['SN']:
                     run_iRecovery = True
                  else:
                     run_iRecovery = False
                     break
               elif iRecovery_Config[key][attribute][0:1] == '-':
                  if iRecoveryAttrList[attribute][6:10] == iRecovery_Config[key][attribute]:
                     run_iRecovery = True
                  else:
                     run_iRecovery = False
                     break
               elif attribute == 'SBG':
                  if iRecoveryAttrList['SBG'] == iRecovery_Config[key]['SBG']:
                     run_iRecovery = True
                  else:
                     run_iRecovery = False
                     break
               elif iRecoveryAttrList[attribute] == iRecovery_Config[key][attribute]:
                  run_iRecovery = True
               else:
                  run_iRecovery = False
                  break
            if run_iRecovery:
               return True
         else:
            return False
   def handleRulesBasedEffectiveness(self):
      objMsg.printMsg("iRecovery : self.dut.currentIRName : %s, IR_DefaultName : %s" %(self.dut.PendingMerge2_IR_NAME_LIST, getattr(self.dut,'currentIRName',IR_DefaultName)))
      DriveAttributes['IR_LAST_ACTION']   = getattr(self.dut,'currentIRName',IR_DefaultName)
      self.dut.PendingMerge2_IR_NAME_LIST = self.dut.PendingMerge2_IR_NAME_LIST + getattr(self.dut,'currentIRName',IR_DefaultName)
      self.dut.currentIRName = IR_DefaultName # Reset IR NAME to default IR_DefaultName
      strBuf = ""
      objMsg.printMsg("iRecovery : self.dut.PendingMerge2_IR_NAME_LIST : %s" %(self.dut.PendingMerge2_IR_NAME_LIST))
      IR_NAME_PendingMergeList = [e for e in self.dut.PendingMerge2_IR_NAME_LIST.split('/') if (len(e)>0 and e != 'NEVER')]
      for i in range(1,len(IR_NAME_PendingMergeList)+1):
         strBuf = strBuf + IR_NAME_PendingMergeList[i-1] +'/'
         if i%iRecovery_NAME_LIST_perAttr == 0 and i > 0:
            cmd    = 'DriveAttributes["IR_NAME_LIST_%s"] = "%s"' %(self.dut.IR_NAME_LIST_startIndex,strBuf[0:-1])
            objMsg.printMsg("iRecovery : Sending RulesBased 'NAME' that IR used to perform")
            objMsg.printMsg(cmd)
            exec(cmd)
            strBuf = ""
            self.dut.IR_NAME_LIST_startIndex = self.dut.IR_NAME_LIST_startIndex + 1
      if strBuf != "":
         cmd    = 'DriveAttributes["IR_NAME_LIST_%s"] = "%s"' %(self.dut.IR_NAME_LIST_startIndex,strBuf[0:-1])
         objMsg.printMsg("iRecovery : Sending EC that IR use to perform")
         objMsg.printMsg(cmd)
         exec(cmd)
         strBuf = ""
      else:
         if self.dut.IR_NAME_LIST_startIndex == 0:
            cmd = 'DriveAttributes["IR_NAME_LIST_0"] = "NEVER"'
            objMsg.printMsg("iRecovery : Sending EC that IR use to perform")
            objMsg.printMsg(cmd)
            exec(cmd)
from iRecovery_Rules import RecoveryRulesBased