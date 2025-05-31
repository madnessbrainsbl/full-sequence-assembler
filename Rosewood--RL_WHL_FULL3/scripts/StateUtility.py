#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Module that stores utilities for dealing with state rerun
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/12/14 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/StateUtility.py $
# $Revision: #6 $
# $DateTime: 2016/12/14 23:54:29 $
# $Author: yihua.jiang $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/StateUtility.py#6 $
# Level:4
#---------------------------------------------------------------------------------------------------------#

from Constants import *
from Drive import objDut as dut
from TestParamExtractor import TP
import MessageHandler as objMsg
from Rim import objRimType
from PowerControl import objPwrCtrl
import ScrCmds
import traceback
from ICmdFactory import ICmd

#------------------------------------------------------------------------------------------------------#
def stateRerunComplete(oper, state=None):
   """
   Returns True if state rerun is done otherwise returns False.
   """
   if dut.stateRerun.get(oper, {}).get(state) == 1:
      return True
   elif dut.stateRerun.get(oper, {}).get(state, 0) == 0:
      return False
   return True

#------------------------------------------------------------------------------------------------------#
def rerunState(oper, stateSequence, depStates):
   """
   Determine next state to run in state retry in sequence.
   """
   from StateTable import StateTable
   stateIndex = []
   for state in depStates[oper]:
      passState = state
      extra_state_append = []
      while not passState in stateSequence[oper]:
         extra_state_append.append(passState)
         passState = StateTable[oper][passState][TRANS]['pass']
      while extra_state_append:
         popState = extra_state_append.pop(0)
         stateSequence[oper].insert(stateSequence[oper].index(passState), popState)

   for state in depStates[oper]:
      if depStates[oper][state]==0:
         stateIndex.append(stateSequence[oper].index(state))

   nextState = stateSequence[oper][min(stateIndex)]
   return nextState

#------------------------------------------------------------------------------------------------------#
def appendState(oper, state):
   """
   Create a list of state sequence.
   """
   if oper in dut.stateSequence:
      dut.stateSequence[oper].append(state)
   else:
      dut.stateSequence[oper]=[]
      dut.stateSequence[oper].append(state)
   dut.objData.update({'stateSequence': dut.stateSequence})

#------------------------------------------------------------------------------------------------------#
def stateFail(oper, state, exceptionData):
   """
   Verifies state pass/fail status after re-run.
   Returns:
         True  - when the state still fails during re-run.
         False - state passes after re-run.
   """
   if hasattr(TP,'stateRerunParams'):
      try:
         ec = exceptionData[0][2]
         if not isinstance(ec, int):
            ec, dut.errMsg = ScrCmds.translateErrCode(dut.errCode)
         elif len(str(ec)) != 5:
            objMsg.printMsg("*** Invalid error code %s. Unable to rerun failing state %s." %(str(ec),state))
            return True
      except:
         objMsg.printMsg("Unable to recognize error code.")
         ec = 0
      objMsg.printMsg("stateFail info: Error code = %s, exceptionData = %s" %(ec, exceptionData))
      dut.failState = state

      #predictNextState = predictRerunState(oper, state, ec)
      #rerunContrlDict = getattr(TP,'rerunContrlDict', {})
      if dut.stateRerun.get('FAIL_STATE') == state:
         dut.stateRerun.update(
                        FAIL  = dut.stateRerun.get('FAIL',0) + 1, # increment fail counter
                        RETRY = dut.stateRerun.get('RETRY',0) + 1,
                        )
         # Replace by rerunCntControl, as experiment found that RERUN item is not accurate, sometimes will be update to 0.
         # if dut.stateRerun.get('FAIL',0) > dut.stateRerun.get('RERUN',1):                     # fail drive if it fails again during re-run
            # objMsg.printMsg("*** Unable to rerun failing state %s. Drive fails again during re-run" %(state))
            # objMsg.printMsg('dut.stateRerun=%s' % dut.stateRerun)
            # dut.stateRerun[oper]={}
            # return True

      if rerunCntControl(oper,state,ec):
         objMsg.printMsg('dut.stateRerun=%s' % dut.stateRerun)
         dut.stateRerun[oper]={}
         return True
      if needRerun(oper,state,ec):
         objMsg.printMsg("State:'%s', Error code:%s found in 'stateRerunParams'. Re-running failing state." %(state, ec))
         dut.depopMask = dut.globaldepopMask
         if objRimType.CPCRiser() or objRimType.IOInitRiser():
            from ICmdFactory import ICmd
            objMsg.printMsg('Reset CRC Error Count: %s' %ICmd.CRCErrorRetry(1))
         dut.stateRerun.update(FAIL_STATE = state, FAIL = 1 )     # mark failing state, update fail counter

         if not dut.stateRerun.has_key('RETRY'):
            dut.stateRerun.update({'RETRY':0})        # create retry counter

         createRerunList(oper, state, ec)
         delDbLog(state)
         powerCycleCheck(ec)
         dut.rerunReason = (oper, state, ec)
         dut.objData.update({'rerunReason': dut.rerunReason})
         if len(dut.driveattr.get('PROC_CTRL6','0')) > 1:
            dut.driveattr['PROC_CTRL6'] = '%s_%s'%(dut.driveattr['PROC_CTRL6'], str(ec))
         else:
            dut.driveattr['PROC_CTRL6'] = str(ec)
      else:
         objMsg.printMsg('dut.stateRerun=%s' % dut.stateRerun)
         dut.stateRerun[oper]={}
         return True
      if (not oper in dut.stateRerun) or (not state in dut.stateRerun[oper]) \
         or (dut.stateRerun[oper][state]==1):         # check pass/fail status based on state rerun flags
         return True
      else:
         dut.errCode = 0
         return False
   else:
      objMsg.printMsg("*** Unable to rerun failing state %s (%s). 'stateRerunParams' not defined in 'TestParameters.py'." %(state, exceptionData[0][2]))
      return True

#------------------------------------------------------------------------------------------------------#
def powerCycleCheck(ec, maxRetries=3):
   """
   Error code based power cycle option.
   """
   if dut.BG in ['SBS']:
      if testSwitch.NoIO or ((objRimType.CPCRiser() or objRimType.IOInitRiser()) and not dut.certOper):
         objPwrCtrl.powerCycle()
      elif objRimType.SerialOnlyRiser() or dut.certOper:
         objPwrCtrl.powerCycle(useESlip=1)
      return
   if ec in getattr(TP,"pwrCycleRetryList",{}):
      retry = 0
      if (objRimType.CPCRiser() or objRimType.IOInitRiser()) and not dut.certOper:
         while retry < maxRetries:  # verify good ID after power cycle. ScPk: 14May09
            try:
               objPwrCtrl.powerCycle()
               ret = ICmd.IdentifyDevice()
               if ret['LLRET'] != OK:
                  raise
               else:
                  objMsg.printMsg("Identify Device passed after power cycle.")
                  break
            except:
               retry += 1
         else:
            ScrCmds.raiseException(13420, "IdentifyDevice failed after %s power cycle attempts." %retry)

      elif objRimType.SerialOnlyRiser() or dut.certOper:
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
   
#------------------------------------------------------------------------------------------------------#
def predictRerunState(oper, state, ec):
   """
   Predict next rerun state brfore create real rerun list.
   """
   states = TP.stateRerunParams['states'].keys()
   dependencies = TP.stateRerunParams['dependencies']
   predictNextState = state
   starErrList = []
   for errCode in TP.stateRerunParams['states']['*']:
      if isinstance(errCode, tuple):
         starErrList.append(errCode[0])
      else:
         starErrList.append(errCode)

   if (state in states) or (ec in starErrList):
      # Append state dependencies to stateRerun list
      if state in dependencies.keys():
         predictNextState = dependencies[state][0]
      elif (state, ec) in dependencies.keys():
         predictNextState = dependencies[(state, ec)][0]
      else:
         predictNextState = state
   return predictNextState
#------------------------------------------------------------------------------------------------------#
def analysisStatesList(oper, state, ec):
   """
   If predict next rerun state more than request limit, skip rerun.
   """
   errorCodes = []
   errTPList = []
   rerunTimes = 0
   states = TP.stateRerunParams['states'].copy()
   errTPList.extend(states.get(state,[]))
   errTPList.extend(states.get('*',[]))
   for errCode in errTPList:
      if isinstance(errCode, tuple):
         errorCodes.append(errCode[0])
         # Track the number of re-runs on the declared error code.
         if errCode[0] == ec:
            rerunTimes = errCode[1]
      else:
         errorCodes.append(errCode)
         if errCode == ec:
            rerunTimes = 1
   return errorCodes, rerunTimes
#------------------------------------------------------------------------------------------------------#
def rerunCntControl(oper, state, ec):
   """
   If predict next rerun state more than request limit, skip rerun.
   """
   predictNextState = predictRerunState(oper, state, ec)
   rerunContrlDict = getattr(TP,'rerunContrlDict', {})
   reruncount = dut.stateSequence[oper].count(state)
   reruncountNextState = dut.stateSequence[oper].count(predictNextState)
   errorCodes, rerunTimes = analysisStatesList(oper, state, ec)
   objMsg.printMsg("errorCodes:%s, rerunTimes:%s, reruncount:%s'." %(errorCodes, rerunTimes, reruncount))
   if predictNextState in rerunContrlDict.keys() and reruncountNextState > rerunContrlDict[predictNextState]:
      objMsg.printMsg("*** Unable to rerun failing state %s. It out of maximum rerun limit." %(predictNextState))
      return True
   elif ec in errorCodes and reruncount > rerunTimes:
      objMsg.printMsg("*** Unable to rerun failing state %s. It out of states rerun limit." %(state))
      return True
   else:
      return False
#------------------------------------------------------------------------------------------------------#
def createRerunList(oper, state, ec):
   """
   Create state rerun list.
   """
   states = TP.stateRerunParams['states'].keys()
   dependencies = TP.stateRerunParams['dependencies']
   dut.stateRerun[oper]={}
   starErrList = []
   for errCode in TP.stateRerunParams['states']['*']:
      if isinstance(errCode, tuple):
         starErrList.append(errCode[0])
      else:
         starErrList.append(errCode)

   if ((state in states) and (state in dut.stateSequence[oper])) or \
      (ec in starErrList):
      dut.stateRerun[oper] = {state: dut.stateRerun[oper].get(state,0)}

      # Append state dependencies to stateRerun list
      if state in dependencies:
         for depState in dependencies[state]:
            dut.stateRerun[oper][depState] = dut.stateRerun.get(depState,0)
            if depState in dependencies:
               for depState2 in dependencies[depState]:
                  dut.stateRerun[oper][depState2] = dut.stateRerun.get(depState2,0)
      elif (state, ec) in dependencies:
         for depState in dependencies[(state, ec)]:
            dut.stateRerun[oper][depState] = dut.stateRerun.get(depState,0)
            if depState in dependencies:
               for depState2 in dependencies[depState]:
                  dut.stateRerun[oper][depState2] = dut.stateRerun.get(depState2,0)

#------------------------------------------------------------------------------------------------------#
def needRerun(oper, state, ec):
   """
   Determines if failing state needs rerun.
   """
   states = TP.stateRerunParams.get('states',{})
   objMsg.printMsg("NEED RERUN OPER %s, STATE %s, ERRCODE %s." % (oper, state, ec))
   errorCodes, rerunTimes = analysisStatesList(oper, state, ec)
   dut.stateRerun.update({'RERUN':rerunTimes})
   if ec in errorCodes:
      if (state in ['VBAR_HMS','VBAR_HMS1','VBAR_HMS2']):
         return True
      if not stateRerunComplete(oper, state):
         return True
   return False

#------------------------------------------------------------------------------------------------------#
def delDbLog(state):
   """
   Handle DBLog tables if state fails.
   """
   if (state in ['VBAR_HMS','VBAR_HMS1','VBAR_HMS2']):
      pass
   else:
      for table in dut.stateDBLogInfo.get(state,[])[:]:
         if table in ['TEST_TIME_BY_STATE']:
            continue
         try:
            dut.dblData.Tables(table).deleteIndexRecords(confirmDelete=1)
            dut.dblData.delTable(table)
         except:
            objMsg.printMsg('ScriptTestFailure fail delTable table=%s. Traceback=%s' % (table, traceback.format_exc()))

      if DEBUG:
         objMsg.printMsg('ScriptTestFailure done delTable table=%s' % dut.stateDBLogInfo.get(state,[]))

#------------------------------------------------------------------------------------------------------#
def UpdateStateRerunFlag(oper=None, state=None):
   """
   Track re-run counter and update state re-run flags.
   """
   RETRY = dut.stateRerun.get('RETRY',0)              # number of state retries
   RERUN = dut.stateRerun.get('RERUN',0)              # number of user input re-runs

   if testSwitch.FE_SGP_402984_ALLOW_MULTIPLE_FAIL_STATE_RETRIES:
      if (oper in dut.stateRerun) and (state in dut.stateRerun[oper]):
         if dut.stateTransitionEvent=='pass':
            updateFlags(oper, state)
            return
         elif RETRY >= RERUN:
            updateFlags(oper, state)
            return

   # During non-production mode, allow maximum number of 'must-pass' number of retries in RERUN value
   if not int(ConfigVars[CN].get('PRODUCTION_MODE',0)):
      if (oper in dut.stateRerun) and (state in dut.stateRerun[oper]) and (RETRY >= RERUN):
         delDbLog(state)
         updateFlags(oper, state)
   elif (oper in dut.stateRerun) and (state in dut.stateRerun[oper]):
         dut.stateRerun[oper][state]=1

def updateFlags(oper=None, state=None):
   for flagState in dut.stateRerun[oper].keys():
      if flagState == state:
         dut.stateRerun[oper].update({flagState:1})      # Only update current running state as done, or else it will affect muli dependent rerun.
   try:
      dut.stateRerun.update({'RERUN':0})
      dut.stateRerun.pop('RETRY')
      if dut.stateTransitionEvent=='pass':            # reset FAIL_STATE=None if re-run passed
         dut.stateRerun.update({'FAIL_STATE': None})
   except:
      pass

