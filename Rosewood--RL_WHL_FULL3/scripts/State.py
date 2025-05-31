#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/12/08 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/State.py $
# $Revision: #10 $
# $DateTime: 2016/12/08 18:43:32 $
# $Author: yihua.jiang $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/State.py#10 $
# Level: 4
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from Exceptions import CStateException,CRaiseException,CFlashCorruptException,CReplugForTempMove,ExcessiveDieTempException
import ScrCmds, traceback
import MessageHandler as objMsg
from CTMX import CTMX
from TestParamExtractor import TP
from StateUtility import stateFail, UpdateStateRerunFlag
from Utility import CUtility
import time
from Process import CProcess
from Rim import objRimType
from StateTable import StateTable

###########################################################################################################
###########################################################################################################
class CState:
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, depList=[]):
      TraceMessage( '=' * 80 )
      self.dut     = dut
      self.depList = depList
      # always handle any event for state jump/recovery (due to power loss/process control)
      self.stateEntryEventHandler(self.dut.stateTransitionEvent)
      self.safeToStartAfterPwrLoss = True # By default states are safe to come out of PwrLoss into
      self.rerunGOTF = False

   #-------------------------------------------------------------------------------------------------------
   def dependencies(self, oper, state):
      TraceMessage( '--- Dependency Check Oper - %s --- State - %s ---' % (oper, state) )
      #
      #  Checking Dependency variables of classes that must run prior to this class running
      #

      self.dut.stateData[state] = 1 # set dep flag indicating that this class has been run
      for dep in self.depList:
         if self.dut.stateData.get(dep,0) == 0:
            ScrCmds.raiseException(13403, "State dependency failure.")
      self.dut.stateTransitionEvent = 'pass'

   #-------------------------------------------------------------------------------------------------------
   def stateEntryEventHandler(self, event):
      #
      # Override this function if you want to handle state recovery procedure
      # Otherwise, just set up some logic in run() based on self.stateEntry
      #
      self.stateEntry = 'pass' # make a state variable that tells how the state was entered
      if event == 'procStart':
         TraceMessage( '--- Handling State Entry Event - %s ---' % (event) )
         #
         # Handler Code for this event
         #
         self.stateEntry = 'procStart'
      elif event == 'procJumpToState':
         TraceMessage( '--- Handling State Entry Event - %s ---' % (event) )
         #
         # Handler Code for this event
         #
         self.stateEntry = 'procJumpToState'
      elif event == 'procStatePowerLoss':
         TraceMessage( '--- Handling State Entry Event - %s ---' % (event) )
         #
         # Handler Code for this event
         #
         self.stateEntry = 'procStatePowerLoss'


   #-------------------------------------------------------------------------------------------------------
   def statePassEventHandler(self, state):
      """
      Code runs if the target state passes
      """
      if testSwitch.FE_0154423_231166_P_ADD_POST_STATE_TEMP_MEASUREMENT:
         if testSwitch.FE_0174828_231166_P_TTR_REMOVE_INTF_TEMP_MSMT_NON_INIT:
            if self.dut.certOper or ((not self.dut.certOper) and state == "INIT"):
               objMsg.printMsg("Measuring Drive Temperature at state %s" % state)
               self.updateStateTemperature(state)
         else:
            self.updateStateTemperature(state)

      if testSwitch.WRITE_SERVO_PATTERN_USING_SCOPY:
         if self.dut.driveattr['SCOPY_TYPE'] != 'MDW' and self.dut.nextOper == 'SCOPY':
            try:
               _, p, h = state.split('_')
               if p.upper() == 'WRITE':
                  p = 'W'
               elif p.upper() == 'REWORK':
                  p = 'R'
               else:
                  p = None
               if p:
                  scopy_type = self.dut.driveattr['SCOPY_TYPE']
                  if '_' in scopy_type:
                     c = ''
                  else:
                     c = '_'
                  scopy_type += c+p+h
                  self.dut.driveattr['SCOPY_TYPE'] = scopy_type
                  DriveAttributes['SCOPY_TYPE'] = scopy_type
            except:
               pass

   #-------------------------------------------------------------------------------------------------------
   def statePreExecuteEventHandler(self, state):
      """
      Code that runs prior to the target state's run code is executed
      """
      pass

   #-------------------------------------------------------------------------------------------------------
   def updateStateTemperature(self, state):
      import Temperature
      stateTemp = Temperature.CTemperature()
      temp = ''

      try:
         if testSwitch.GA_0160140_350027_REPORT_CHANNEL_DIE_TEMP_THROUGHOUT_PROCESS:
            stateTemp.getChannelDieTemp()

         temp = stateTemp.getHDATemp()
      except ExcessiveDieTempException:
         raise
      except:
         objMsg.printMsg("Failed to get state exit temp: \n%s" % (traceback.format_exc(),))

      #update DUT copy
      self.dut.stateTemperatureData[state] = temp
      #save for PLR
      self.dut.objData.update({'stateTemperatureData': self.dut.stateTemperatureData})

   #-------------------------------------------------------------------------------------------------------
   def getCurrentTemperature(self, state):
      import Temperature
      stateTemp = Temperature.CTemperature()
      temp = ''

      try:
         if testSwitch.GA_0160140_350027_REPORT_CHANNEL_DIE_TEMP_THROUGHOUT_PROCESS:
            stateTemp.getChannelDieTemp()

         temp = stateTemp.getHDATemp()
         return temp
      except:
         objMsg.printMsg("Failed to get state exit temp: \n%s" % (traceback.format_exc(),))
   #-------------------------------------------------------------------------------------------------------
   def GOTFrunState(self, oper, state):
      TraceMessage( '--- Running Oper - %s --- State - %s ---' % (oper, state) )
      oProc = CProcess()
      if testSwitch.virtualRun:
         msg = '%s__%s' % (self.dut.nextOper,state)
         stInfo.addState(msg)
      #
      # (Override this function in your derived class if you have transition events other than 'pass' or 'fail')
      # Override is not needed, just make run() allow for self.dut.stateTransitionEvent to be changed to
      #  to whatever is needed (eg. to 'rerun')
      #
      try:
         self.dut.stateTransitionEvent = 'pass' # Setting this here allows normal exit to assume 'pass'
         ReportStatus('%s --- %s' % (oper, state))
         ScriptComment('State Sequence Number: %d' % self.dut.seqNum)
         ScriptComment('- '*20 + state + ' : BEGIN   ' + ' -'*20)
         self.dut.ctmxState = CTMX('STATE') # Create CTMX entry for this state
         self.dut.curTestInfo = {'state': state,'param': 'None', 'occur': '', 'tstSeqEvt': 0, 'test': 0, 'seq':self.dut.seqNum, 'stackInfo':'', 'testPriorFail': ''}

         if not self.depList==[] and not state in self.dut.stateDependencies:       #Track state dependencies
            self.dut.stateDependencies[state] = self.depList
         if testSwitch.FE_0160792_210191_P_TEMP_CHECKING_IN_GEMINI_CRITICAL_STATES and not (ConfigVars[CN].get('BenchTop',0) == 1):
            if oper in ['PRE2','CAL2','CAL','FNC2','FNC']:
               if state in TP.PRE_CHECK_TEMP_STATES:
                  try:
                     certTemp= DriveVars['Cert_Temperature_Deg_C']
                     curTemp = self.getCurrentTemperature(state)
                  except:
                     try:
                        oProc.St({'test_num':172, 'prm_name':'CERT TEMP', 'timeout': 200, 'CWORD1': (18,)})
                        certTemp = DriveVars['Cert_Temperature_Deg_C']
                        curTemp = self.getCurrentTemperature(state)
                     except:
                        ScrCmds.raiseException(10606, "Cannot Measure Critical Drive temperatures")
                  if not(TP.CRITICAL_TEMP_MIN<curTemp<TP.CRITICAL_TEMP_MAX):
                     ScrCmds.raiseException(10606, "Drive Temperature for state %s is %s and outside limits" %(state,curTemp))
                  if (abs(certTemp - curTemp) > 8):
                     ScrCmds.raiseException(10606, "ABS Drive Temperature for state %s is %s and outside limits Cert Temp %s" %(state,curTemp,certTemp))
         try:
            try:

               self.statePreExecuteEventHandler(state)

               if 'E' in StateTable[oper][state][OPT]:
                  if not self.dut.certOper:
                     objMsg.printMsg("Skip state not supported in F3 code.")
                  else:
                     self.run()
               else:
                  self.run()

               self.statePassEventHandler(state)

            except:
               try:
                  self.dut.supprResultsFile.flushDebugData()
               except:
                  TraceMessage("Unable to report suppressed failure logs:\n%s" % traceback.format_exc())
               raise
         finally:
            #Clear out suppressed data from state if we passed.
            self.dut.supprResultsFile.clearDebugFile()
            self.dut.ctmxState.endStamp() # Close and write CTMX entry for this state
            self.dut.ctmxState.writeDbLog()


         if testSwitch.FE_0160792_210191_P_TEMP_CHECKING_IN_GEMINI_CRITICAL_STATES  and not (ConfigVars[CN].get('BenchTop',0) == 1):
            if oper in ['PRE2','CAL2','CAL','FNC2','FNC']:
               if state in TP.POST_CHECK_TEMP_STATES:
                  try:
                     certTemp= DriveVars['Cert_Temperature_Deg_C']
                     curTemp = self.getCurrentTemperature(state)
                  except:
                     try:
                        oProc.St({'test_num':172, 'prm_name':'CERT TEMP', 'timeout': 200, 'CWORD1': (18,)})
                        certTemp = DriveVars['Cert_Temperature_Deg_C']
                        curTemp = self.getCurrentTemperature(state)
                     except:
                        ScrCmds.raiseException(10606, "Cannot Measure Critical Drive temperatures")
                  if not(TP.CRITICAL_TEMP_MIN<curTemp<TP.CRITICAL_TEMP_MAX):
                     ScrCmds.raiseException(10606, "Drive Temperature for state %s is %s and outside limits" %(state,curTemp))
                  if (abs(certTemp - curTemp) > 8):
                     ScrCmds.raiseException(10606, "ABS Drive Temperature for state %s is %s and outside limits Cert Temp %s" %(state,curTemp,certTemp))

         #Check Temp for HDSTR_SP (each state)
         if testSwitch.FE_0158685_345172_ENABLE_HDSTR_TEMP_CHECK  and not (ConfigVars[CN].get('BenchTop',0) == 1):
            try:
               if testSwitch.FE_0158388_345172_HDSTR_SP_CHECK_TEMP_EVAL_PURPOSE:
                  if oper in ['PRE2','CAL2','CAL', 'FNC2', 'FNC']:
                     if state not in TP.HDSTR_CHECK_TEMP_STATE: # HDSTR_CHECK_TEMP_STATE skip all state before MDW_CAL and after download F3 code.
                        oProc.St(TP.hdstr_tempCheck)
                        drive_temp_C = DriveVars['Drive_Temperature_Deg_C']
                        ScrCmds.statMsg('Drive temp on Gemini: %d' % drive_temp_C)
               elif objRimType.IsHDSTRRiser():
                  if oper in ['PRE2', 'CAL2', 'FNC2', 'FNC']:
                     if state not in ['INIT', 'DNLD_CODE', 'SETUP_PROC', 'PCBA_SCRN', 'HEAD_CAL', 'END_TEST', 'DNLD_SF3CODE', 'DNLD_F3CODE', 'DISPLAY_G', 'ENC_WR_SCRN', 'SERIAL_FMT', 'RE_FORMAT', 'FAIL_PROC']:
                        oProc.St(TP.hdstr_tempCheck)
                        drive_temp_C = DriveVars['Drive_Temperature_Deg_C']
                        ScrCmds.statMsg('Drive temp on HDSTR_SP: %d' % drive_temp_C)
               else:
                  if oper in ['CAL2', 'FNC2', 'FNC']:
                     if state not in ['INIT', 'DNLD_CODE','END_TEST','DNLD_SF3CODE', 'DNLD_F3CODE', 'DISPLAY_G', 'ENC_WR_SCRN', 'SERIAL_FMT', 'RE_FORMAT', 'FAIL_PROC']:
                        oProc.St(TP.hdstr_tempCheck)
                        drive_temp_C = DriveVars['Drive_Temperature_Deg_C']
                        ScrCmds.statMsg('Drive temp on Gemini: %d' % drive_temp_C)
                        oProc.St({'test_num':172, 'prm_name':'CERT TEMP', 'timeout': 200, 'CWORD1': (18,)})
                        drive_temp_C = DriveVars['Cert_Temperature_Deg_C']
                        ScrCmds.statMsg('Cert temp on Gemini: %d' % drive_temp_C)
            except:
               pass

         if testSwitch.FE_0155953_345172_CHK_DRIVE_TEMP_TO_RERUN_FNC2  and not (ConfigVars[CN].get('BenchTop',0) == 1):
            if objRimType.IsHDSTRRiser() and (oper == 'FNC2') and (state in ['ZAP','D_FLAWSCAN']):
               ec, msg = self.checkTemp(drive_temp_C, state)
               if ec != 0:
                  ScrCmds.raiseException(ec, msg)

         if objRimType.IsHDSTRRiser() and ConfigVars[CN].get('HG_CM_OverLoad',0) == 1:
            import time
            objMsg.printMsg("Set time sleep to help CM load average(%d)"%getattr(TP,'TimeWaitState',60))
            time.sleep(getattr(TP,'TimeWaitState',60))

         UpdateStateRerunFlag(oper, state)
         self.dut.curTestInfo['testPriorFail'] = ''
         ScriptComment('- '*20 + state + ' : COMPLETE' + ' -'*20)
         ScriptComment('- '*60)
         self.ChkCPCOTF()

         if self.dut.SpecialPwrLoss == 1 and testSwitch.FE_0129265_405392_SPECIAL_STATES_PLR:
            self.dut.SpecialPwrLoss = 0
         else:
            if testSwitch.FE_0189561_418088_IRECOVERY_SUPPORT:
               if str(state) != iRecoveryStateName:
                  self.dut.failureState = state
               else:
                  ScrCmds.statMsg('IRECOVERY state, Skipping updating self.dut.failureState')
            else:
               self.dut.failureState = state
            if testSwitch.FE_0129265_405392_SPECIAL_STATES_PLR:
               self.dut.objData.update({'failureState': state})

      except ScriptTestFailure, (failureData):
         if self.GOTFstateFail(oper, state, failureData):
            ScrCmds.statMsg('***** FAULT DETECTED *****')  #Requested by AMK for AutoDebug

            #Bypass current state to next state even current state is failed. M10P Coreteam Request
            if testSwitch.M10P and 'BYPASS_STATE_FAIL' in StateTable[self.dut.nextOper][self.dut.nextState][OPT]:
               self.dut.nextState = StateTable[self.dut.nextOper][self.dut.nextState][TRANS]['pass']
               self.dut.stateTransitionEvent = 'restartAtState'
               return
            self.dut.failureData       = failureData
            self.dut.depopfailureState = state
            objMsg.printMsg("Depop_On_The_Fly:%d" %testSwitch.Depop_On_The_Fly)
            objMsg.printMsg("DEPOP_OTF:%s" %DriveAttributes.get('DEPOP_OTF','NA'))
            if testSwitch.AGC_SCRN_DESTROKE:
               if self.ChkDESTROKEOTF(self.dut.failureData[0][2]):
                  return
            
            if testSwitch.ENABLE_ON_THE_FLY_DOWNGRADE and self.ChkDownGradeOTF(oper, state, self.dut.failureData[0][2]):
               return
               
            if testSwitch.FE_0148166_381158_DEPOP_ON_THE_FLY and DriveAttributes.get('DEPOP_OTF','NA') != 'DONE':
               #if self.ChkDepopOTF(self.dut.failureData[0][2], 0):
               #   return
               from OTF_Waterfall import CDepop_OTF_Check
               oDPOTF = CDepop_OTF_Check(self.dut)
               if oDPOTF.dpotfCheck(self.dut.failureData[0][2], 0):
                  return

            if self.ChkRerunWTF(self.dut.failureData[0][2]):
               return

            if self.dut.replugECMatrix.has_key(failureData[0][2]) and \
                  (self.dut.nextState in self.dut.replugECMatrix[failureData[0][2]] or self.dut.curTestInfo['test'] in self.dut.replugECMatrix[failureData[0][2]] or len(self.dut.replugECMatrix[failureData[0][2]]) == 0) and \
                  ConfigVars[CN].get('ReplugEnabled',0) and not ConfigVars[CN].get('BenchTop',0) == 1:
               ScriptComment('Replug enabled, SKIP Fail Process')
               ScrCmds.statMsg('self.dut.errCode: %s' % self.dut.errCode)
               ScrCmds.statMsg('self.dut.replugECMatrix.has_key(self.dut.errCode): %s' % self.dut.replugECMatrix.has_key(self.dut.errCode))
               ScrCmds.statMsg('self.dut.curTestInfo[test]: %s' % self.dut.curTestInfo['test'])
               ScrCmds.statMsg('self.dut.failureData: %s' % self.dut.failureData)
               if not testSwitch.BF_0170041_409401_P_FIX_11049_DRIVE_SKIP_REPLUG_AFTER_DONE_AFH4:
                  if self.dut.AFHCleanUp and testSwitch.FE_0160713_409401_P_ADD_AFH_CLEAN_UP_AT_AUTO_REPLUG_FOR_DRIVE_FAIL_AFTER_AFH4:
                     if testSwitch.SPLIT_BASE_SERIAL_TEST_FOR_CM_LA_REDUCTION:
                        from base_AFH import CCleanUpBadPattern
                     else:
                        from base_SerialTest import CCleanUpBadPattern                  
                     oCleanUpBadPattern = CCleanUpBadPattern(self.dut,{})
                     oCleanUpBadPattern.run()
               raise ScriptTestFailure, failureData

            self.dut.failTestInfo = self.dut.curTestInfo
            if testSwitch.FE_0189561_418088_IRECOVERY_SUPPORT:
               if str(state) != iRecoveryStateName:
                  self.dut.failureState = state
               else:
                  ScrCmds.statMsg('IRECOVERY state, Skipping updating self.dut.failureState')
            else:
               self.dut.failureState = state
            self.dut.genExcept = traceback.format_exc()
            self.dut.stateTransitionEvent = 'fail'
            self.dut.objData.update({'failureData': self.dut.failureData.args}) #save before fail_proc
            self.dut.objData.update({'failTestInfo': self.dut.failTestInfo})
            if testSwitch.FE_0129265_405392_SPECIAL_STATES_PLR:
               self.dut.objData.update({'genExcept': self.dut.genExcept})
         else:
            pass

      except CStateException:
         raise ScriptTestFailure, self.dut.failureData

      except CReplugForTempMove,exceptionData:
         if testSwitch.FE_0189561_418088_IRECOVERY_SUPPORT:
            if str(state) != iRecoveryStateName:
               self.dut.failureState = state
            else:
               ScrCmds.statMsg('IRECOVERY state, Skipping updating self.dut.failureState')
         else:
            self.dut.failureState = state
         self.dut.failureData          = exceptionData.args
         self.dut.genExcept = traceback.format_exc()
         raise
      except CRaiseException,exceptionData:
         if self.GOTFstateFail(oper, state, exceptionData):
            ScrCmds.statMsg('***** FAULT DETECTED *****')  #Requested by AMK for AutoDebug
            #Bypass current state to next state even current state is failed. M10P Coreteam Request
            if testSwitch.M10P and 'BYPASS_STATE_FAIL' in StateTable[self.dut.nextOper][self.dut.nextState][OPT]:
               self.dut.nextState = StateTable[self.dut.nextOper][self.dut.nextState][TRANS]['pass']
               self.dut.stateTransitionEvent = 'restartAtState'
               return

            self.dut.failureData = exceptionData.failureData      # Python 2.7 bug fix

            failCode = self.dut.failureData[0][2]
            self.dut.depopfailureState = state
            if testSwitch.AGC_SCRN_DESTROKE:
               if self.ChkDESTROKEOTF(failCode):
                  return
            if testSwitch.ENABLE_ON_THE_FLY_DOWNGRADE and self.ChkDownGradeOTF(oper, state, failCode):
               return
            if testSwitch.FE_0148166_381158_DEPOP_ON_THE_FLY and self.dut.driveattr.get('DEPOP_OTF','NA') != 'DONE':
               #if self.ChkDepopOTF(self.dut.failureData[0][2], 1):
               #   return
               from OTF_Waterfall import CDepop_OTF_Check
               oDPOTF = CDepop_OTF_Check(self.dut)
               if oDPOTF.dpotfCheck(self.dut.failureData[0][2], 1):
                  return

            if self.ChkRerunWTF(failCode):
               return
            if exceptionData.args[0][2] in [13409] and self.dut.driveattr.get('WTF_CTRL', '') != 'VBAR_13409' and testSwitch.FE_0121130_231166_ALLOW_AUTO_RERUN_VBAR:
               ScrCmds.statMsg('Drive Fail EC13409 - Auto Rerun VBAR')
               self.dut.driveattr['WTF_CTRL'] = 'VBAR_13409'
               self.dut.stateTransitionEvent = 'reRunVBAR'
               return
            self.dut.failTestInfo = self.dut.curTestInfo
            if testSwitch.FE_0189561_418088_IRECOVERY_SUPPORT:
               if str(state) != iRecoveryStateName:
                  self.dut.failureState = state
               else:
                  ScrCmds.statMsg('IRECOVERY state, Skipping updating self.dut.failureState')
            else:
               self.dut.failureState = state
            self.dut.genExcept = traceback.format_exc()
            self.dut.stateTransitionEvent = 'fail'
            self.dut.objData.update({'failureData': self.dut.failureData}) #save before fail_proc
            self.dut.objData.update({'failTestInfo': self.dut.failTestInfo})
            if testSwitch.FE_0129265_405392_SPECIAL_STATES_PLR:
               self.dut.objData.update({'genExcept': self.dut.genExcept})

         else:
            pass

      except Exception, e:
         if self.GOTFstateFail(oper, state, e):
            ScrCmds.statMsg('***** FAULT DETECTED *****')  #Requested by AMK for AutoDebug
            self.dut.failTestInfo = self.dut.curTestInfo
            if testSwitch.FE_0189561_418088_IRECOVERY_SUPPORT:
               if str(state) != iRecoveryStateName:
                  self.dut.failureState = state
               else:
                  ScrCmds.statMsg('IRECOVERY state, Skipping updating self.dut.failureState')
            else:
               self.dut.failureState = state
            self.dut.genExcept = traceback.format_exc()
            errCode,errMsg = ScrCmds.translateErrCode(GenericErrorCode)
   
            #HDSTR_SP power recovery
            if errCode in [11074] and objRimType.IsHDSTRRiser():
               for i in range(60):
                  ScrCmds.statMsg('--- HDSTR_SP ec : %s, Count : %d ---' % (errCode, i))
                  time.sleep(60)
   
            self.dut.failureData          = ScrCmds.makeFailureData(errCode,errMsg)
   
            self.dut.objData.update({'failureData': self.dut.failureData}) #save before fail_proc
            self.dut.objData.update({'failTestInfo': self.dut.failTestInfo})
            self.dut.stateTransitionEvent = 'fail'
            if testSwitch.FE_0129265_405392_SPECIAL_STATES_PLR:
               self.dut.objData.update({'genExcept': self.dut.genExcept})
         else:
            pass

      TraceMessage( '--- State Exit Event - %s ---' % self.dut.stateTransitionEvent )

   def ChkDESTROKEOTF(self, failCode):
      ''' Check DESTROKE State'''
      objMsg.printMsg("Checking DESTROKE: EC%s State %s" % (failCode, self.dut.nextState))

      if self.dut.IDExtraPaddingSize != 0:   # already destroked
         objMsg.printMsg("Already Destroked, raise primary error code!")
         return False

      if not self.dut.nextOper == 'PRE2':
         objMsg.printMsg("Cannot destroke after PRE2, skipped!")
         return False

      import PIF
      if not hasattr(PIF, 'destroke_OTF_Config'):
         objMsg.printMsg("destroke_OTF_Config not defined in PIF, skipped!")
         return False

      if failCode not in PIF.destroke_OTF_Config.keys():
         objMsg.printMsg("EC%s not in destroke_OTF_Config, skipped!" % (failCode))
         return False

      destrokeCfg = PIF.destroke_OTF_Config[failCode]
      if self.dut.nextState not in destrokeCfg['ValidState']:
         objMsg.printMsg("State %s not in destroke_OTF_Config, skipped!" % (self.dut.nextState))
         return False

      import types
      origPadding = TP.RampDetectTestPrm_185['ID_PAD_TK_VALUE']
      if type(origPadding) == types.TupleType:
         origPadding = origPadding[0]
      objMsg.printMsg("Checking ID_PAD_TK_VALUE: %d" % origPadding)
      # Get Max Track
      MaxTrack = int(self.dut.dblData.Tables('P172_MAX_CYL_VBAR').tableDataObj()[-1]['MAX_CYL_DEC'])
      objMsg.printMsg("MaxTrack : %d" % MaxTrack)

      # Get Fail Track
      try: 
         FailTrack = int(self.dut.dblData.Tables(destrokeCfg['Table']).tableDataObj()[-1][destrokeCfg['Fail_Track']])
         objMsg.printMsg("FailTrack : %d" % FailTrack)
         if MaxTrack - FailTrack > int(destrokeCfg['Fail_Limit']):
            objMsg.printMsg("Fail Tracks exceeded ID limit %s, raise primary error code!" % destrokeCfg['Fail_Limit'])
            return False
      except:
         objMsg.printMsg("Unable to find table info %s, raise primary error code!" % destrokeCfg['Table'])
         return False

      objMsg.printMsg("***** DESTROKE_RETRY_TRIGGERED ***** ")

      #Update Padd Track and Restart
      self.dut.IDExtraPaddingSize = max(MaxTrack - FailTrack, int(destrokeCfg['Min_Padding']))
      if self.dut.IDExtraPaddingSize > TP.Destroke_Trk_To_Load_A_New_RAP:
         self.dut.driveattr['DESTROKE_REQ'] = 'DSD_NEW_RAP'
      else:
         self.dut.driveattr['DESTROKE_REQ'] = 'DSD'

      try:
         self.dut.objData.update({'IDExtraPaddingSize':self.dut.IDExtraPaddingSize})  
      except:
         objMsg.printMsg("Fail to save IDExtraPaddingSize to objdata")
      #reststart
      self.dut.stateTransitionEvent = 'restartAtState'
      self.dut.nextState = destrokeCfg['NextState']

      objMsg.printMsg("self.dut.IDExtraPaddingSize = %d" % self.dut.IDExtraPaddingSize)
      if not testSwitch.FE_0190240_007955_USE_FILE_LIST_FUNCTIONS_FROM_DUT_OBJ:
         from Setup import CSetup
         objSetup = CSetup()
         objSetup.buildFileList()   # update with new rap if supported
      else:
         self.dut.buildFileList()
      return True

   def ChkRerunWTF(self, failCode):
      ''' Check RerunWTF State'''

      if not hasattr(TP,'WTFRerunParams'):
         objMsg.printMsg('No WTFRerunParams define in TP, return')  
         return False

      objMsg.printMsg("failCode  : %s " % str(failCode))
      objMsg.printMsg("nextState : %s " % self.dut.nextState)
      objMsg.printMsg("PN        : %s " % self.dut.partNum)

      try:
         if self.dut.nextOper == 'PRE2' and failCode in TP.WTFRerunParams['states'][self.dut.nextState]:
            if self.dut.partNum[3:6] == '142':
               objMsg.printMsg("Triggering waterfall rerun with 320GB capacity, reset all WTF attributes to NONE.")

               if self.dut.partNum[7:10] in ['998','995','999']:
                  newPN = self.dut.partNum[0:3] + '14C' + '-998'
               else:
                  newPN = self.dut.partNum[0:3] + '14C' + self.dut.partNum[6:10]

               self.dut.partNum           = newPN
               self.dut.WTF               = 'NONE' 
               self.dut.Waterfall_Req     = 'NONE' 
               self.dut.Waterfall_Done    = 'NONE' 
               self.dut.Niblet_Level      = 'NONE' 
               self.dut.Drv_Sector_Size   = 'NONE' 
               self.dut.Depop_Req         = 'NONE' 

               self.dut.driveattr['PART_NUM']         = self.dut.partNum
               self.dut.driveattr['WTF']              = self.dut.WTF
               self.dut.driveattr['WATERFALL_DONE']   = self.dut.Waterfall_Done
               self.dut.driveattr['WATERFALL_REQ']    = self.dut.Waterfall_Req
               self.dut.driveattr['NIBLET_LEVEL']     = self.dut.Niblet_Level
               self.dut.driveattr['DRV_SECTOR_SIZE']  = self.dut.Drv_Sector_Size
               self.dut.driveattr['DEPOP_REQ']        = self.dut.Depop_Req

               self.dut.nextState = 'WATERFALL'
               self.dut.stateTransitionEvent = 'restartAtState'
               self.dut.VbarRestarted        = 1
               
               objMsg.printMsg("New nextState : %s " % self.dut.nextState)
               objMsg.printMsg("New PN        : %s " %(self.dut.partNum) )
               ScrCmds.HostSetPartnum(self.dut.partNum)
               return True

      except:
         objMsg.printMsg("EC not found in TP.WTFRerunParams")
         return False

   def checkTemp(self, driveTemp_C, state):
      msg = ""
      objMsg.printMsg("Drive temperature at %s state is %sC"%(state, str(driveTemp_C)))
      if driveTemp_C < 40:
         msg = "Drive temperature is less than 40, require auto retest FNC2 on Gemini."
         return 10606, msg
      if testSwitch.FE_0159970_409401_P_HDSTR_SP_HIGH_TEMP_SCRN and driveTemp_C > 65:
         msg = "Drive temperature is more than 65, require auto retest FNC2 on Gemini."
         return 10605, msg

      return 0, msg

   #-------------------------------------------------------------------------------------------------------
   def checkValidEC(self, failcode, ecList):
      if failcode in ecList:
         return True
      if (failcode, self.dut.nextOper) in ecList:
         return True
      return False

   #-------------------------------------------------------------------------------------------------------
   def ChkDownGradeOTF(self, oper, state, failCode):
      try:
         ec = failCode
         ScrCmds.statMsg('Raise exception EC=%s' % ec)
         for rerunitem in getattr(TP, 'downGradeRerunParams', {'state' : {}, 'oper' : {},}):
            if rerunitem == 'dependencies':
               continue
            for rerunstate in TP.downGradeRerunParams[rerunitem]:
               if state == rerunstate and ec in TP.downGradeRerunParams[rerunitem][rerunstate]:
                  objMsg.printMsg('rerun state=%s, ec=%s, in rerun list.' % (rerunstate, ec))
                  if self.downGradeOnFly(1, ec, rerunitem, rerunstate) == 1:
                     self.dut.rerunReason = (oper, state, ec)
                     self.dut.objData.update({'rerunReason': self.dut.rerunReason})
                     if len(self.dut.driveattr.get('PROC_CTRL6','0')) > 1:
                        self.dut.driveattr['PROC_CTRL6'] = '%s_%s'%(self.dut.driveattr['PROC_CTRL6'], str(ec))
                     else:
                        self.dut.driveattr['PROC_CTRL6'] = str(ec)
                     if rerunitem == 'oper':
                        ScrCmds.statMsg('Fault detected in %s,rerun whole OPER!' % state)
                        self.dut.nextState = 'INIT'
                        self.dut.stateTransitionEvent = 'restartAtState'
                        self.dut.downgradeOTF = 1
                        ScrCmds.statMsg('NEXT STATE %s!' % self.dut.nextState)
                        #delete oracle tables
                        objMsg.printMsg(self.dut.dblData.Tables())
                        from DbLog import DbLog
                        oDbLog = DbLog(self.dut)
                        oDbLog.delAllOracleTables(confirmDelete = 1)
                        return 1
                     elif rerunitem == 'statedepend':
                        ScrCmds.statMsg('Fault detected in %s,rerun from pointed state!' % state)
                        self.delDbLog(self.dut.nextState)
                        self.dut.nextState = TP.downGradeRerunParams['dependencies'][state]
                        self.dut.stateTransitionEvent = 'restartAtState'
                        self.dut.downgradeOTF = 1
                        ScrCmds.statMsg('NEXT STATE %s!' % self.dut.nextState)
                        return 1
                     elif rerunitem == 'state':
                        ScrCmds.statMsg('Fault detected in %s,rerun current STATE!' % state)
                        if not self.dut.nextState in ['READ_SCRN2C']:
                           self.delDbLog(self.dut.nextState)
                        self.dut.nextState = state
                        self.dut.stateTransitionEvent = 'restartAtState'
                        self.dut.downgradeOTF = 1
                        ScrCmds.statMsg('NEXT STATE %s!' % self.dut.nextState)
                        return 1
                     elif rerunitem == 'reCRT2':
                        ScrCmds.statMsg('Fault detected in %s,rerun from CRT2!' % state)
                        self.dut.GOTFRetest={'SET_OPER': 'CRT2', 'VALID_OPER': 'CRT2', 'LOOPER_COUNT': '1','NO_YIELD_REPORT':'*',}
                        return 0
                     else:
                        return 0
                  else:
                     return 0
         else:
            return 0
      except:
         objMsg.printMsg("Error occur in down grade, raise primary error code!")
         return 0

   def downGradeOnFly(self, skipchk = 0, failcode = 0, rerunitem = 'NONE', rerunstate = 'NONE'):
      if not int(ConfigVars[CN].get('DowngradeOTF', 1)):
         objMsg.printMsg('Auto-downgrade disable by ConfigVar DowngradeOTF')
         return 0
      if self.dut.BG == 'STD' and not (self.dut.partNum[-3:] in getattr(TP, 'SPE_PN_LIST', ['998']) or self.dut.partNum in getattr(TP, 'SPE_PN_LIST', [])): 
         if (self.dut.nextState not in self.dut.downgradeRerun) and (failcode in getattr(TP,'downGradererunECList', [])):
            self.dut.downgradeRerun.append(self.dut.nextState)
            return 1
         else:
            return 0
      if self.dut.BG == 'SBS':
         # Calling for screen
         if rerunitem == 'NONE' and rerunstate == 'NONE':
            objMsg.printMsg('Already SBS(Lowest BS). Return')
            return 1
         # Calling for downgrade and rerun
         else:
            objMsg.printMsg('Already SBS. Cannot further downagrade and rerun')
            return 0
         
      if rerunitem != 'NONE':
         rerunContrlDict = getattr(TP,'rerunContrlDict', {})
         if self.dut.nextState in TP.downGradeRerunParams['dependencies'].keys():
            predictNextState = TP.downGradeRerunParams['dependencies'][self.dut.nextState]
         else:
            predictNextState = self.dut.nextState
         if predictNextState in rerunContrlDict.keys() and self.dut.stateSequence[self.dut.nextOper].count(predictNextState) > rerunContrlDict[predictNextState]:
            objMsg.printMsg("*** Unable to downgrade and rerun failing state %s. It out of rerun limit'." %(predictNextState))
            return 0
      failcodeList = []
      failcodeList.extend(getattr(TP,'downGradeECList', []))
      failcodeList.extend(getattr(TP,'downGradeSTDECList', []))
      failcodeList.extend(getattr(TP,'downGradeSBSECList', []))
      originalBG = self.dut.BG
      if failcode in failcodeList or skipchk:
         objMsg.printMsg("Drive fail EC %s, need to down grade!!!" % str(failcode))
         if rerunitem == 'reCRT2' and failcode in TP.downGradeRerunParams['reCRT2'][rerunstate]:
            if ConfigVars[CN].get('SBS_DEMAND', 'N') == 'N':
               objMsg.printMsg("NO SBS DEMAND!")
               return 0
            if int(DriveAttributes.get("LOOPER_COUNT", "0")) >= 1:
               objMsg.printMsg("CAN NOT RERUN AGAIN!")
               return 0
            pn = TP.RetailTabMasspro
            self.dut.BG = 'STD'

         elif 0:#self.dut.partNum[-3:] in getattr(TP, 'SPE_PN_LIST', ['998']) or self.dut.partNum in getattr(TP, 'SPE_PN_LIST', []):
            try:
               if testSwitch.SPLIT_VBAR_FOR_CM_LA_REDUCTION:
                  from WTF_Tools import CWTF_Tools
                  oWaterfall = CWTF_Tools()
               else:
                  from base_SerialTest import CWaterfallTest
                  oWaterfall = CWaterfallTest(self.dut)
               oWaterfall.buildClusterList(updateWTF = 1)
               objMsg.printMsg("TP.VbarPartNumCluster=%s" % TP.VbarPartNumCluster)
               try:
                  nibletIndex = TP.VbarPartNumCluster.index(self.dut.partNum)
               except:
                  if testSwitch.SPLIT_VBAR_FOR_CM_LA_REDUCTION:
                     from WTF_Tools import CWTF_Tools
                     oWaterfall = CWTF_Tools()
                  else:
                     from SerialTest import CWaterfallTest
                     oWaterfall = CWaterfallTest(self.dut,)
                  oWaterfall.buildClusterList(updateWTF = 0)
                  objMsg.printMsg("TP.VbarPartNumCluster=%s" % TP.VbarPartNumCluster)
                  nibletIndex = TP.VbarPartNumCluster.index(self.dut.partNum)
               pn = TP.VbarPartNumCluster[nibletIndex+1]
               objMsg.printMsg("oldPartNum=%s, newPartNum=%s" % (self.dut.partNum, pn))
               if (pn[5] != self.dut.partNum[5]) or (pn == self.dut.partNum) or (pn[-3:] not in getattr(TP,'RetailTabList', ['995'])):
                  objMsg.printMsg("CAPACITY OF DOWNGRADE PN NOT SAME AS ORIGINAL, DOWNGRADE PATH NOT CORRECT!")
                  return 0
               self.dut.BG = 'STD'
            except:
               objMsg.printMsg('Get buisness group and part number exception. Traceback=%s' % (traceback.format_exc()))
               self.dut.BG = originalBG
               return 0

         else:
            try:
               nIndex = self.dut.demand_table.index(self.dut.BG)
               for demand in self.dut.demand_table[nIndex:]:
                  pn = self.dut.manual_gotf[demand][self.dut.bgIndex]
                  objMsg.printMsg("   BG=%s PN=%s" % (demand, pn))
                  if demand != self.dut.BG:
                     self.dut.BG = demand
                     break
               else: # non break
                  if CUtility.regexInIterable(self.dut.partNum, getattr(TP, 'PN_RECFG_SBS_LIST', [])) and self.checkValidEC(failcode, getattr(TP, 'EC_RECFG_SBS_LIST', [])):
                     objMsg.printMsg("Failcode %d, partNum %s, downgrade to SBS..." % (failcode, self.dut.partNum))
                     originalPN = self.dut.partNum
                     try:
                        self.dut.partNum = TP.RetailTabMasspro
                        objMsg.printMsg("New partNum = %s" % self.dut.partNum)
                        self.dut.demand_table = list(self.dut.DEMAND_TABLE)

                        from base_GOTF import CGOTFGrading
                        from StateMachine import CBGPN
                        from CommitServices import isTierPN
                        objGOTF = CGOTFGrading()
                        objBGPN = CBGPN(objGOTF)
                        if testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT:
                           if (self.dut.driveattr['ORG_TIER'] in [TIER1, TIER2, TIER3]) or isTierPN( self.dut.partNum ):
                              objBGPN.GetBGPN(reset_Manual_GOTF = 1)
                        else:
                           objBGPN.GetBGPN()
                        demand = 'SBS'
                        if demand in self.dut.demand_table:
                           for pn in self.dut.manual_gotf[demand]:
                              if pn == self.dut.partNum: # found match
                                 self.dut.BG = demand
                                 self.dut.bgIndex = self.dut.manual_gotf[demand].index(pn)
                                 break
                           else: # cannot find any matching pn
                              raise
                     except:
                        objMsg.printMsg('Error, unable to downgrade to %s' % self.dut.partNum)
                        self.dut.partNum = originalPN
                        self.dut.BG = originalBG
                        return 0
                     else:
                        self.dut.partNum = originalPN
                  else: # non break
                     objMsg.printMsg('No downgrade path found!')
                     self.dut.BG = originalBG
                     return 0
               pn = self.dut.manual_gotf[self.dut.BG][self.dut.bgIndex]
               lbwECnPN = getattr(TP, 'RetailTabWithLBWServoCode', {})
               newPN = lbwECnPN.get(failcode, '')
               if len(newPN) > 0 and newPN in self.dut.manual_gotf[self.dut.BG]:
                  objMsg.printMsg('Need change PN(%s) to %s'%(pn, newPN))
                  pn = newPN
                  self.dut.bgIndex = self.dut.manual_gotf[demand].index(newPN)               
            except:
               objMsg.printMsg('Get buisness group and part number exception. Traceback=%s' % (traceback.format_exc()))
               self.dut.BG = originalBG
               return 0
            if len(pn) != 10:    # safety net
               objMsg.printMsg("Part Number in manual_gotf is invalid, raise error code!")
               self.dut.BG = originalBG
               return 0
            if pn[-3:] not in getattr(TP,'RetailTabList', ['995']) and failcode in getattr(TP,'downGradeSBSECList', []):
               objMsg.printMsg("Part Number is NOT SBS, can NOT downgrade!")
               self.dut.BG = originalBG
               return 0
         
         self.dut.driveattr["DNGRADE_ON_FLY"] = '%s_%s_%s'%(self.dut.nextOper, self.dut.partNum[-3:], str(failcode))
         self.dut.partNum = pn
         self.dut.driveattr['BSNS_SEGMENT'] = self.dut.BG
         self.dut.driveattr['PART_NUM'] = self.dut.partNum
         self.dut.CAPACITY_CUS = self.dut.CAPACITY_PN + '_' + self.dut.BG
         self.dut.driveattr['PROC_CTRL10'] = 'GOTF'
         objMsg.printMsg("Part number changed to %s" % str(self.dut.partNum))
         ScrCmds.HostSetPartnum(self.dut.partNum)
         self.dut.downgradeRerun.append(self.dut.nextState)
         try:
            from PIF import nibletTable
            if nibletTable[self.dut.partNum]['Native'][0].find('L') > -1:
               self.dut.Niblet_Level = nibletTable[self.dut.partNum]['Native'][0][-1]
               self.dut.driveattr['NIBLET_LEVEL'] = self.dut.Niblet_Level
         except:
            objMsg.printMsg('Reset niblet_Level exception !!!')
         try:
            if not testSwitch.FE_0190240_007955_USE_FILE_LIST_FUNCTIONS_FROM_DUT_OBJ:
               from Setup import CSetup
               objSetup = CSetup()
               objSetup.buildFileList()
            else:
               self.dut.buildFileList()
            import TestParameters
            reload(TestParameters)
            import ServoParameters
            reload(ServoParameters)
            import AFH_params
            reload(AFH_params)
         except:
            objMsg.printMsg('Rebuild code list exception !!!')
         return 1
      else:
         return 0

   def delDbLog(self, state):
      '''
      Handle DBLog tables if state fails.
      '''
      for table in self.dut.stateDBLogInfo.get(state,[])[:]:
         try:
            self.dut.dblData.Tables(table).deleteIndexRecords(confirmDelete=1)
            self.dut.dblData.delTable(table)
         except:
            objMsg.printMsg('ScriptTestFailure fail delTable table=%s. Traceback=%s' % (table, traceback.format_exc()))

      if DEBUG:
         objMsg.printMsg('ScriptTestFailure done delTable table=%s' % self.dut.stateDBLogInfo.get(state,[]))

   #-------------------------------------------------------------------------------------------------------
   def exitStateMachine(self):
      #
      # Method will throw special exception for upper level code to handle
      #
      raise CStateException

   #-------------------------------------------------------------------------------------------------------
   def ChkCPCOTF(self):
      from Rim import theRim
      if theRim.Unlock:
         res = theRim.Unlock()
         if res == 2:
            from PowerControl import objPwrCtrl
            objPwrCtrl.powerCycle(5000, 12000, 10, 30)

   #-------------------------------------------------------------------------------------------------------
   def GOTFstateFail(self, oper, state, e):
      res = stateFail(oper, state, e)
      if res == True and int(DriveAttributes.get("LOOPER_COUNT", "0")) < 1:
         import PIF
         retestGOTF = getattr(PIF, 'retestGOTF', {})
         retestOper = retestGOTF.get(oper, {})
         Failcode2dblog = retestOper.get('Failcode2dblog', [])

         if len(Failcode2dblog) > 0:
            import types, sys
            lastException, lastValue = sys.exc_info()[:2]
            self.dut.RetestLastErr = lastValue
            errCode = lastValue[0][2]

            if type(errCode) == types.IntType and errCode in Failcode2dblog:
               self.dut.dblData.Tables('P_CUSTOMER_TEST').addRecord({
                  'CUST_TEST_NAME': state,
                  'CUST_TEST_PASS': int(False),
                  })
               objMsg.printDblogBin(self.dut.dblData.Tables('P_CUSTOMER_TEST'))
               self.rerunGOTF = True
               res = False

      return res

   #-------------------------------------------------------------------------------------------------------
   def runState(self, oper, state):
      try:
         self.rerunGOTF = False
         self.GOTFrunState(oper, state)
      except:
         if self.rerunGOTF == False:
            raise

#---------------------------------------------------------------------------------------------------------#

class CFailProcState(CState):
   """
   This is a state to inherit fail_proc states from,
   it will handle the failure saving / not allowing a drive to pass.
   The inherited state needs only define the tests desired in the fail sequence.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, depList=[]):
      CState.__init__(self, dut, depList)

   def runState(self, oper, state):
      try:
         TraceMessage( '--- Running Oper - %s --- State - %s ---' % (oper, state) )
         self.dut.stateTransitionEvent = 'pass' # Setting this here allows normal exit to assume 'pass'
         ReportStatus('%s --- %s' % (oper, state))
         ScriptComment('State Sequence Number: %d' % self.dut.seqNum)
         ScriptComment('- '*20 + state + ' : BEGIN   ' + ' -'*20)
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
            self.run() # run the fail_proc tests
         finally:
            self.dut.failureData = tmpFailData # recover the failure data

      finally:
         try:
            ScriptComment('- '*20 + state + ' : COMPLETE' + ' -'*20)
            ScriptComment('- '*60)
         finally:
            if self.dut.stateTransitionEvent in ['pass','fail']: # if we make a special exception, the drive wont fail
               raise ScriptTestFailure, self.dut.failureData # this fails the drive.


   def run(self):
      """
      This function needs to be overridden in specific fail_proc state.
      It actually runs the desired tests in a failsafed way.
      """
      objMsg.printMsg('Fail_proc state tests not defined')
