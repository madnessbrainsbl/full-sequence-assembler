#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description:
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/12/14 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/StateMachine.py $
# $Revision: #6 $
# $DateTime: 2016/12/14 23:54:29 $
# $Author: yihua.jiang $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/StateMachine.py#6 $
# Level: 4
#---------------------------------------------------------------------------------------------------------#
import Constants
from Constants import *
from PIF import states_GOTF

if testSwitch.FE_0189561_418088_IRECOVERY_SUPPORT:
   IR_EXCLUDED_OPERS = ['SDAT2','CMT2','AUD2','CCV2',]
   from Exceptions import CRaiseException

import ScrCmds, struct, time, re

import MessageHandler as objMsg
import PBIC
from base_GOTF import CGOTFGrading
import re, traceback, PIF
from StateUtility import appendState, stateRerunComplete, rerunState, UpdateStateRerunFlag
from TestParamExtractor import TP

# import module listing all states/operations
from StateTable import StateTable, StateParams
from TestParamExtractor import TP
from Drive import objDut

GOTF_EXCLUDED_OPERS = ['SDAT2','IDT2','CCV2',]
if testSwitch.FE_0190477_357260_P_SKIP_GOTF_FOR_SELECT_STATES:
   GOTF_EXCLUDED_STATES = getattr(TP,'GOTF_EXCLUDED_STATES',['FAIL_PROC','COMPLETE','FAIL_PROC_MANT'])
else:
   GOTF_EXCLUDED_STATES = []

if testSwitch.FE_0185033_231166_P_MODULARIZE_DCM_COMMIT:
   import CommitServices

if testSwitch.FE_0113445_347508_RUN_MULTIPLE_MANUAL_GOTF_TABLES == 1:
   try:
      Manual_GOTF = {}
      objMsg.printMsg("PRODUCTNAME=%s" % (TP.ProductName_Manual_GOTF))
      Manual_GOTF = getattr(PIF,'Manual_GOTF_%s' % TP.ProductName_Manual_GOTF,{})
   except:
      try:
         objMsg.printMsg("NO PRODUCTNAME DEFINED" )
         from PIF import Manual_GOTF
      except:
         TraceMessage("Manual GOTF settings not found in TestParameters.py. Feature disabled. Refer to TPE-0002135")
         Manual_GOTF = {}
else:
   try:
      from PIF import Manual_GOTF
   except:
      TraceMessage("Manual GOTF settings not found in TestParameters.py. Feature disabled. Refer to TPE-0002135")
      Manual_GOTF = {}

import CommitServices, CommitCls

#states which are only run by PN
states_PN = getattr(PIF ,'states_PN',{})

try:
   # One more chance if reflow to CMT2 - can be lowest tier OEM
   from PIF import LowestOEM
except:
   LowestOEM = "STD"

#states which are only run by PN
states_PN = getattr(PIF ,'states_PN',{})
initState = 'INIT'

def evalPhaseOut(dictOrString):
   """dict was previously a dict encased in a string - if/else for backwards compatability
   Calls should eventually be removed and this function deleted
   """
   if type(dictOrString)==type({}):    # check that dictOrString is a dictionary
      return dictOrString              # new method
   else:                               # must be old string method
      return eval(dictOrString)        # old method

###########################################################################################################
###########################################################################################################
class CStateMachine:
#------------------------------------------------------------------------------------------------------#
   """ Class to handle Image File Downloads """
   def __init__( self, dut ):

      TraceMessage( ("STATE MACHINE INSTANTIATED") )

      from FSO import dataTableHelper
      self.dth = dataTableHelper()
      self.dut = dut
      self.oGOTF = CGOTFGrading()
      objBGPN = CBGPN(self.oGOTF)
      objBGPN.GetBGPN()

      # if grading rev not allowed, quit
      if testSwitch.GOTFGradingRevCheck == 1 and self.dut.nextOper != 'PRE2' and self.oGOTF.GradingRev != "NONE":
         objMsg.printMsg("Non PRE2 - checking grading rev %s vs %s" % (self.dut.driveattr['GRADING_REV'], self.oGOTF.GradingRev))
         if self.dut.driveattr['GRADING_REV'][:-1] != self.oGOTF.GradingRev[:-1]:
            objMsg.printMsg("Grading rev check fail. Checking LowestOEM=%s self.dut.longattr_bg=%s" % (LowestOEM, self.dut.longattr_bg))
            if self.dut.nextOper == 'CMT2' and LowestOEM in self.dut.longattr_bg:
               self.dut.longattr_bg = LowestOEM
               objMsg.printMsg("self.dut.longattr_bg forced to %s" % (self.dut.longattr_bg))
            else:
               msg = "Drive cannot further downgrade because of grading rev mismatch %s vs %s" % (self.dut.driveattr['GRADING_REV'], self.oGOTF.GradingRev)
               ScrCmds.raiseException(13425, msg)

      self.dut.driveattr['GRADING_REV'] = self.oGOTF.GradingRev   # force update to latest rev
      # Request from Process for better OEM / SBS Yield Tracking
      if not self.dut.powerLossEvent and self.dut.BG == 'SBS' and self.dut.nextOper == 'PRE2':
         self.dut.driveattr['DNGRADE_ON_FLY'] = 'SBS'

      #Extend the parsing list with the grading list
      self.dut.dblParser.dblTableMaster.extend(self.oGOTF.gotfCriteria.keys())
      if not testSwitch.winFOF or testSwitch.virtualRun:
         self.chkDepend = ConfigVars[CN].get('ChkStateDepend', 1)
      else:
         self.chkDepend = 0

      #
      #  Create a mechanism here to determine which
      #  operation to start with and which operations
      #  to run.
      #

      oper, initialState = self.dut.nextOper, self.dut.nextState
      TraceMessage(oper + ' ' + initialState)

      if initialState == 'COMPLETE' and self.dut.SpecialPwrLoss == 1 and testSwitch.FE_0129265_405392_SPECIAL_STATES_PLR:
         objMsg.printMsg("Execute only INIT state for power loss at COMPLETE state")
         self.execState(oper, initState) # do not check dependencies for initState state
         self.chkDepend = 0 # do not check dependencies for state recovery procedure
      elif initialState != initState: # execute INIT state as this is mandatory for any test process
         if not initialState == 'COMPLETE':
            scriptModule      = StateTable[oper][initialState][MODULE] # check if the state is safe
            classMethod       = StateTable[oper][initialState][METHOD] # WRT power loss recovery
            exec('import %s' % scriptModule)
            if (not eval('%s.%s(self.dut, {}).safeToStartAfterPwrLoss'%(scriptModule, classMethod))
                     and self.dut.stateTransitionEvent=='procStatePowerLoss'):
               initialState = initState # if pwrloss and state doesn't allow powerloss, start over
            else:
               self.execState(oper, initState) # do not check dependencies for initState state
               self.chkDepend = 0 # do not check dependencies for state recovery procedure
            exec('del %s' % scriptModule)
         else:
            self.execState(oper, initState) # do not check dependencies for initState state
            self.chkDepend = 0 # do not check dependencies for state recovery procedure
      if testSwitch.FE_0331809_433430_P_STOP_TEST_IF_INIT_FAILED and self.dut.stateTransitionEvent == 'fail':
         try:
            errorCode, errorInfo = self.dut.failureData[0][2],self.dut.failureData[0][0]
         except:
            errorCode, errorInfo = 49052,'INIT failed during power lose recovery' #default error information if retrieve faildata failed
         ScrCmds.raiseException(errorCode,errorInfo)
      #if oper == 'CMT2':
      #   self.CMT2GOTFcheck()
      keepRunning = 1
      while keepRunning:
         self.stateMachine(oper, initialState, self.chkDepend)
         #
         #  If we are checking dependencies then
         #  run completely through the tests twice,
         #  once to check dependencies and once to
         #  execute the tests.
         #
         if self.chkDepend == 1:
            if testSwitch.FE_0133890_231166_VALIDATE_SHIPMENT_DEPENDANCIES:
               self.validateShipmentStateCriteria()
            if testSwitch.FE_0134030_347506_SAVE_AND_RESTORE:
               self.dut.stateLoopCounter = {} #this was populated during the dependencies check.  Reset for state table execution
               self.dut.statesExec[self.dut.nextOper] = [] #this was populated during the dependencies check.  Reset for state table execution
            self.chkDepend = 0
         else:
            keepRunning = 0

      self.CTUbinning()

      # Synchronize from Manual Business Segment to Auto Business Segment.
      self.oGOTF.syncManualToAutoBS(self.dut, oper)

   #------------------------------------------------------------------------------------------------------#
   def validateShipmentStateCriteria(self):
      """
      Function validates that the state flow conforms to the minimum requirements for a shipable drive.
      """

      #Only need to validate CUT2 for shipment
      if not self.dut.nextOper == "CUT2":
         return

      # Below is the required list... also allowed are states with this names in them for repeats
      #  Such as: DISPLAY_G_1

      #Typically these should be performed in this order
      if testSwitch.FE_0151675_231166_P_SUPPORT_SINGLE_DIAG_INIT_SHIP:
         depList = [
            'VERIFY_SMART',
            'CRITICAL_LOG',
            'READY_SHIP'
            ]
      else:
         depList = [
           'VERIFY_SMART',
           'CRITICAL_LOG',
           'CLEAR_UDS',
           'RESET_SMART',
           'RESET_DOS',
           'RESET_AMPS',
           'AMPS_CHECK',
           'DISPLAY_G',
           'CLEAR_MINI_CERT'
                    ]

      #Allow programs to add to this list
      depList.extend(getattr(TP,  'SHIP_DEP_LIST',  []))

      for dep in depList:
         if self.dut.stateData.get(dep,0) == 0:
            #it is possible there are multiple of these states to iterate through the list looking for partial matches to state name
            for state in self.dut.stateData:
               if dep in state and self.dut.stateData[state] == 1:
                  # we found a match
                  break
            else:
               #we didn't find a partial match
               ScrCmds.raiseException(13403, "State dependency failure. %s is a required state to ship drives." % dep)

   #------------------------------------------------------------------------------------------------------#
   def CTUbinning(self):
      if self.dut.stateTransitionEvent != 'pass':
         return

      try:
         from PIF import Binning
      except:
         return

      from PIFHandler import CPIFHandler
      PIFHandler = CPIFHandler()

      dPNum = PIFHandler.getPnumInfo(sPnum=self.dut.partNum, dPNumInfo=Binning, GetAll=True, dcm=False)

      objMsg.printMsg('%s Start CTUbinning Partnum dPNum=%s' % (self.dut.partNum, dPNum))
      pnlst = dPNum.get('AllLst', [])
      if len(pnlst) == 0:
         return

      dSBR = PIFHandler.getPnumInfo(sPnum=self.dut.sbr, dPNumInfo=pnlst[len(pnlst) - 1], GetAll=True, dcm=False)
      objMsg.printMsg('dSBR=%s' % dSBR)
      sbrlst = dSBR.get('AllLst', [])
      if len(sbrlst) == 0:
         return

      bins = sbrlst[len(sbrlst) - 1].get("BINS", [])
      IsChanged = False
      for bin in bins:
         bin_bg = self.dut.BG + bin
         gotfres = self.oGOTF.gotfTestGroup(bin_bg)
         objMsg.printMsg('gotfTestGroup bin_bg=%s gotfres=%s' % (bin_bg, gotfres))

         if gotfres == True:
            IsChanged = True
            attr = self.dut.driveattr.get('GOTF_BIN_BEST', "")

            if not bin_bg in str(self.oGOTF.gotfGradingResults):
               objMsg.printMsg('bin %s not found in gotfGradingResults' % bin_bg)
            elif attr != "#BINZ":
               try:
                  oldidx = bins.index(attr)
                  newidx = bins.index(bin)
                  objMsg.printMsg('GOTF_BIN_BEST oldidx=%s newidx=%s' % (oldidx, newidx))

                  if newidx > oldidx:     # only update if CTU bin worse than previous one
                     self.dut.driveattr['GOTF_BIN_BEST'] = bin
               except:
                  # fresh update
                  objMsg.printMsg('Old BIN not found in GOTF_BIN_BEST. Updating to %s' % bin)
                  self.dut.driveattr['GOTF_BIN_BEST'] = bin

               break
         else:
            attr = self.dut.driveattr.get('GOTF_BIN_CTQ', "")
            if attr == "NONE":
               attr = ""

            sCTQ = "%02d/" % self.GetCTQ(tmpbg=bin_bg)
            if not sCTQ in attr:
               attr = attr + sCTQ
               self.dut.driveattr['GOTF_BIN_CTQ'] = attr
               objMsg.printMsg('Updated GOTF_BIN_CTQ=%s' % attr)

      if IsChanged == False:
         objMsg.printMsg('Fail all binning')
         self.dut.driveattr['GOTF_BIN_BEST'] = "#BINZ"
      objMsg.printMsg("End CTUbinning GOTF_BIN_CTQ=%s GOTF_BIN_BEST=%s" % (self.dut.driveattr.get('GOTF_BIN_CTQ', ""), self.dut.driveattr.get('GOTF_BIN_BEST', "")))

   #------------------------------------------------------------------------------------------------------#
   def GetCTQ(self, tmpbg=""):
      if tmpbg == "":
         tmpbg = self.dut.BG

      # CTQ will be the first found failure, unsorted
      # Verbose message on failure only
      tabledata = self.dut.dblData.Tables('P_GOTF_TABLE_SUMMARY').tableDataObj()

      if DEBUG > 0:
         objMsg.printDblogBin(self.dut.dblData.Tables('P_GOTF_TABLE_SUMMARY'))
      iCTQ = 0

      try:
         for tab in tabledata:
            if tab['BUSINESS_GROUP'] == tmpbg and tab['PF_RESULT'] == 'F' and tab['DBLOG_POSITION'] < 32:
               iCTQ = tab['DBLOG_POSITION']
               break
      except:
         iCTQ = 0

      return iCTQ


   def CMT2GOTFcheck(self):

      if self.dut.driveattr['CUST_SCORE'] != self.dut.driveattr['DRIVE_SCORE']:
         changeBGto = 'NONE'
         for demand in self.dut.demand_table:
            if changeBGto != 'NONE':
               break
            elif (demand != self.dut.BG):
               if self.oGOTF.gotfCustScore(demand) ==  self.oGOTF.gotfDriveScore(demand):
                  if states_GOTF.has_key(demand):
                     if self.dut.statesSkipped[self.dut.nextOper] != [] and states_GOTF[demand][self.dut.nextOper] == 'ALL':
                        changeBGto = 'NONE'
                  else:
                     for skipped in self.dut.statesSkipped[self.dut.nextOper]:
                        if skipped in states_GOTF[demand][self.dut.nextOper]:
                           changeBGto = 'NONE'
                           break

         if changeBGto == 'NONE':
            self.dut.BG = 'STD'
         else:
            self.dut.BG = changeBGto

         if len(self.dut.manual_gotf) > 0:      # knl
            # search back BG -> PN
            if self.dut.BG in self.dut.manual_gotf:
               pn = self.dut.manual_gotf[self.dut.BG][self.dut.bgIndex]
               if len(pn) != 10:    # safety net
                  ScrCmds.raiseException(11044, 'Part Number in manual_gotf is invalid')
            else:
               ScrCmds.raiseException(11044, 'Business group not found in manual_gotf')

            self.dut.partNum = pn
            self.dut.driveattr['BSNS_SEGMENT'] = self.dut.BG
            self.dut.driveattr['PART_NUM'] = self.dut.partNum
            ScrCmds.HostSetPartnum(self.dut.partNum)
            objMsg.printMsg("Part number changed to %s" % str(self.dut.partNum))

   #------------------------------------------------------------------------------------------------------#
   def GetBGPNPrecedence(self):     # knl
      '''
      Get business group and part number precedence

      Precedence (in descending order) as per TT:
      1. When both BG and full PN match (eg 'OEM1,9EV132-999')
      4. When BG is * and full PN matches (eg ''*,9EV132-999')
      2. When both BG and PSF match (eg 'OEM1,9EV2')
      5. When BG is * and PSF matches (eg ''*,9EW2')
      3. When BG matches. PSF is either blank or * (eg 'OEM1' or 'OEM1,*')
      6. When * are used for both BG and PSF (eg '*,*')
      '''

      if self.dut.BG == None:    # Fix bug when ConfigVars does NOT have Business Group defined - knl
         return self.dut.BG

      BGList = []
      BGList.append(self.dut.BG + ',' + self.dut.partNum)
      BGList.append('*' + ',' + self.dut.partNum)
      BGList.append(self.dut.BG + ',' + self.dut.partNum[:4])
      BGList.append('*' + ',' + self.dut.partNum[:4])
      BGList.append(self.dut.BG)
      BGList.append(self.dut.BG + ',*')
      BGList.append('*,*')

      bg = self.dut.BG    # use default business group
      for i in BGList:
         if states_GOTF.has_key(i):
            bg = i
            break

      return bg

   def setDepopRestartPointer(self):
      if self.dut.nextOper == 'PRE2':
         if not 'DEPOP_RESTART_PTR' in self.dut.objData:
            self.dut.objData['DEPOP_RESTART_PTR'] = ResultsFile.size()

         if 'recur' in self.dut.objData:
            self.dut.objData['recur'] = self.dut.objData['recur'] + 1
         else:
            self.dut.objData['recur'] = 1


         if self.dut.objData['recur'] > 12:
            raise Exception, "Looped %s times through PRE2" % self.dut.objData['recur']

   #------------------------------------------------------------------------------------------------------#
   def stateMachine(self, oper, initialState, chkDepend):
      from Rim import objRimType

      self.dut.nextState = initialState

      try:
         self.idxCMT2 = self.dut.operList.index('CMT2')
      except:
         self.idxCMT2 = 10000

      while self.dut.nextState != 'COMPLETE' and self.dut.nextState != 'FAIL':
         if self.dut.nextState == initialState and not chkDepend:
            self.setDepopRestartPointer()

         bg = self.GetBGPNPrecedence()    # knl
         if DEBUG > 0:
            objMsg.printMsg("stateMachine: using states_GOTF dict key %s" % bg)

         if testSwitch.BF_0174138_395340_P_FIX_RUN_WRONG_STATE_TEST_AFTER_PWL and not chkDepend:
            #Update all necessary variables to disc for power loss recovery.
            self.dut.objData.update({'NEXT_STATE': self.dut.nextState}) # pickle drive and state information
         if 'G' in StateTable[oper][self.dut.nextState][OPT]:
            if states_GOTF.has_key(bg):
               if states_GOTF[bg].has_key(oper):
                  if states_GOTF[bg][oper] != 'ALL' and self.dut.nextState not in states_GOTF[bg][oper]:
                     objMsg.printMsg("Skipping state %s" % str(self.dut.nextState))
                     self.dut.statesSkipped[self.dut.nextOper].append(self.dut.nextState)
                     self.dut.nextState = evalPhaseOut(StateTable[oper][self.dut.nextState][TRANS])['pass']
                     continue
               else:
                  objMsg.printMsg("WARNING: Oper %s is not found in states_GOTF. Skipping state %s" % (str(bg), str(self.dut.nextState)))
                  self.dut.nextState = evalPhaseOut(StateTable[oper][self.dut.nextState][TRANS])['pass']
                  continue
            else:
               objMsg.printMsg("WARNING: Business Group %s is not found in states_GOTF. Skipping state %s" % (str(bg), str(self.dut.nextState)))
               self.dut.nextState = evalPhaseOut(StateTable[oper][self.dut.nextState][TRANS])['pass']
               continue

         if 'S' in StateTable[oper][self.dut.nextState][OPT]:
            if self.dut.driveattr.get('ST240_PROC','N') == 'P':
               objMsg.printMsg("ST240 states %s" % self.dut.nextState)
            else:
               objMsg.printMsg("Skipping ST240 states %s since ST240_PROC is not set to \'P\'" % self.dut.nextState)
               self.dut.nextState = evalPhaseOut(StateTable[oper][self.dut.nextState][TRANS])['pass']
               continue


         if 'H' in StateTable[oper][self.dut.nextState][OPT]:

            if testSwitch.FE_0160791_7955_P_ADD_STATE_TABLE_SWITCH_CONTROL_IN_H_OPT and testSwitch.FE_0123282_231166_ADD_SWITCH_CONTROL_TO_STATE_TABLE:
               if not self.checkStateEnabledBySwitch(StateTable[oper][self.dut.nextState][OPT]):
                  self.dut.nextState = evalPhaseOut(StateTable[oper][self.dut.nextState][TRANS])['pass']
                  continue

            objMsg.printMsg("HDSTR_PROC = %s" % self.dut.HDSTR_PROC)
            run_test_state = 0
            if testSwitch.FE_0124465_391186_HDSTR_SHARE_FNC_FNC2_STATES:
               if oper in ['FNC'] and (self.dut.HDSTR_PROC == 'Y' or self.dut.driveattr.get('ST240_PROC','NONE')== 'C'):
                  run_test_state = 1
            else:
               if oper in ['FNC2','FNC'] and self.dut.HDSTR_PROC == 'Y':
                  run_test_state = 1

            if run_test_state:
               objMsg.printMsg("Skipped HDSTR state %s" % str(self.dut.nextState))
               self.dut.nextState = evalPhaseOut(StateTable[oper][self.dut.nextState][TRANS])['pass']
               continue
            elif oper == 'PRE2' and self.dut.nextState == "HDSTR_RECORD" and self.dut.HDSTR_PROC == 'Y':
               StateParams[oper][self.dut.nextState] = "[]"
               objMsg.printMsg("HDSR_RECORD state")
               for state, state_info in StateTable['FNC2'].iteritems():
                  if state != 'COMPLETE':
                     if 'G' in state_info[OPT]:
                        if states_GOTF.has_key(bg):
                           if states_GOTF[bg].has_key(oper):
                              if states_GOTF[bg] != 'ALL' and self.dut.nextState not in states_GOTF[bg]:
                                 objMsg.printMsg("State may not be added to HDSTR due to GOTF %s" % str(self.dut.nextState))
                                 continue
                           else:
                              objMsg.printMsg("WARNING: Oper %s is not found in states_GOTF. Skipping state %s" % (str(bg), str(self.dut.nextState)))
                              self.dut.nextState = evalPhaseOut(StateTable[oper][self.dut.nextState][TRANS])['pass']
                              continue
                        else:
                           objMsg.printMsg("WARNING: Business Group %s is not found in states_GOTF. Skipping state %s" % (str(bg), str(self.dut.nextState)))
                           continue

                     if 'H' in state_info[OPT]:
                        evalPhaseOut(StateParams[oper][self.dut.nextState]).append(state)
                  objMsg.printMsg("HDSTR states %s" % str(StateParams[oper][self.dut.nextState]))
           # else:
           #    objMsg.printMsg("Skipping HDSTR_RECORD since HDSTR_PROC is not set to \'Y\'")
           #    self.dut.nextState = evalPhaseOut(StateTable[oper][self.dut.nextState][TRANS])['pass']

#         else:
#            objMsg.printMsg("HDSTR option in oper %s and state %s is not handled" % (str(oper), str(self.dut.nextState)))

         if 'AS' in StateTable[oper][self.dut.nextState][OPT]:
            if testSwitch.BF_0140398_231166_FIX_STATE_INTF_TRANSITION_IOINT:
               if not ( self.dut.drvIntf in TP.WWN_INF_TYPE.get('WW_SATA_ID', []) or self.dut.drvIntf == 'SATA' ):
                  objMsg.printMsg("Skipping state %s since drive isn't SATA" % self.dut.nextState)
                  self.dut.nextState = StateTable[oper][self.dut.nextState][TRANS]['pass']
                  continue
            else:
               if not objRimType.CPCRiser():
                  self.dut.nextState = StateTable[oper][self.dut.nextState][TRANS]['pass']
                  continue
         if 'SS' in StateTable[oper][self.dut.nextState][OPT]:
            if testSwitch.BF_0140398_231166_FIX_STATE_INTF_TRANSITION_IOINT:
               if not ( self.dut.drvIntf in TP.WWN_INF_TYPE.get('WW_SAS_ID', []) or self.dut.drvIntf == 'SAS' ):
                  objMsg.printMsg("Skipping state %s since drive isn't SAS" % self.dut.nextState)
                  self.dut.nextState = StateTable[oper][self.dut.nextState][TRANS]['pass']
                  continue
            else:
               if not objRimType.IOInitRiser():
                  self.dut.nextState = StateTable[oper][self.dut.nextState][TRANS]['pass']
                  continue
         if testSwitch.FE_0162093_426568_P_HEAD_VENDOR_STATE_SELECTION and ('RHO' in StateTable[oper][self.dut.nextState][OPT] or 'TDK' in StateTable[oper][self.dut.nextState][OPT]):
            if self.dut.HGA_SUPPLIER not in StateTable[oper][self.dut.nextState][OPT]:
               objMsg.printMsg("Skipping state %s since drive correct head vendor." % self.dut.nextState)
               self.dut.nextState = StateTable[oper][self.dut.nextState][TRANS]['pass']
               continue
         if testSwitch.FE_0147105_426568_P_COMBO_STATE_SELECTION_P_TESTSWITCH and ('P' in StateTable[oper][self.dut.nextState][OPT]) and (testSwitch.FE_0123282_231166_ADD_SWITCH_CONTROL_TO_STATE_TABLE and ( not self.checkStateEnabledBySwitch(StateTable[oper][self.dut.nextState][OPT]) )) :
            #Check if we have a filter definition for this state
            if not self.handlePartnumFilteredState():
               objMsg.printMsg("Skipping state %s since PN isn't a match." % self.dut.nextState)
               self.dut.nextState = StateTable[oper][self.dut.nextState][TRANS]['pass']
               continue
            else:
               self.dut.nextState = evalPhaseOut(StateTable[oper][self.dut.nextState][TRANS])['pass']
               continue
         if 'P' in StateTable[oper][self.dut.nextState][OPT]:
            #Check if we have a filter definition for this state
            if not self.handlePartnumFilteredState():
               objMsg.printMsg("Skipping state %s since drive isn't in the Part Num Filter" % self.dut.nextState)
               self.dut.nextState = StateTable[oper][self.dut.nextState][TRANS]['pass']
               continue
         if 'E' in StateTable[oper][self.dut.nextState][OPT]:
            if not self.checkStateEnabledBySwitch(StateTable[oper][self.dut.nextState][OPT]):
               self.dut.nextState = evalPhaseOut(StateTable[oper][self.dut.nextState][TRANS])['pass']
               continue
            if testSwitch.proqualCheck and self.dut.prevOperStatus["%s_TEST_DONE" %oper] == "PASS":
               objMsg.printMsg( '*** Warning!!! Skipping Oper - %s --- State - %s ---' % (oper, `self.dut.nextState`))
               self.dut.statesSkipped[self.dut.nextOper].append(self.dut.nextState)
               self.dut.nextState = evalPhaseOut(StateTable[oper][self.dut.nextState][TRANS])['pass']
               continue

         if testSwitch.FE_0123282_231166_ADD_SWITCH_CONTROL_TO_STATE_TABLE and ( not self.checkStateEnabledBySwitch(StateTable[oper][self.dut.nextState][OPT]) ):
            #State has testSwitch matching and flag(s) is/are disabled
            # example usage below
            # 'VBAR_TUNE_I'   : ['base_SerialTest',   'CVbarTuning',               {'pass':'WATERFALL','fail':'FAIL_PROC'},           [{'FE_xxxxxxx_xxxxxx_VBAR_FLAG1': 1, 'extern.FE_xxxxxxx_231166_VBAR_FLAG2', 1},]],
            # so state would run if FE_xxxxxxx_xxxxxx_VBAR_FLAG1 = 1 and extern.FE_xxxxxxx_231166_VBAR_FLAG2 = 1
            # otherwise the pass transiton would occur
            self.dut.nextState = evalPhaseOut(StateTable[oper][self.dut.nextState][TRANS])['pass']
            continue
         if 'non-TODT' in StateTable[oper][self.dut.nextState][OPT] and (DriveAttributes.get('PART_NUM', self.dut.partNum) in TP.TODT_PN or 'ALL' in TP.TODT_PN):
            objMsg.printMsg("Skipping state %s since STD drive" % self.dut.nextState)
            self.dut.nextState = evalPhaseOut(StateTable[oper][self.dut.nextState][TRANS])['pass']
            continue
         if 'RWK' in StateTable[oper][self.dut.nextState][OPT]:
            if DriveAttributes.get('PRIME','N') == 'N':
               objMsg.printMsg("Rework drive require additional screen.")
            else:
               objMsg.printMsg("Skipping state %s since PRIME drive." % self.dut.nextState)
               self.dut.nextState = evalPhaseOut(StateTable[oper][self.dut.nextState][TRANS])['pass']
               continue
         if self.dut.nextState[:4] == 'EQAT':
            if DriveAttributes.get('PART_NUM', self.dut.partNum) in TP.EQAT_PN or 'ALL' in TP.EQAT_PN:
               objMsg.printMsg("EQAT test require,, perform EQAT2 test")
            else:
               objMsg.printMsg("Skipping EQAT test since not require")
               self.dut.nextState = evalPhaseOut(StateTable[oper][self.dut.nextState][TRANS])['pass']
               continue

         if 'R' not in StateTable[oper][self.dut.nextState][OPT] and self.dut.reconfigOper:
            objMsg.printMsg("Skipping %s test since not part of reconfiguration process." % self.dut.nextState)
            self.dut.nextState = evalPhaseOut(StateTable[oper][self.dut.nextState][TRANS])['pass']
            continue

         if TIER1 in StateTable[oper][self.dut.nextState][OPT] or TIER2 in StateTable[oper][self.dut.nextState][OPT] or TIER3 in StateTable[oper][self.dut.nextState][OPT] or TIERX in StateTable[oper][self.dut.nextState][OPT]:

            #if drive isn't tiered but tier required then skip
            if (not self.dut.reconfigOper) and ( not CommitServices.isTierPN( self.dut.partNum ) and ( TIERX in StateTable[oper][self.dut.nextState][OPT] ) ):
               objMsg.printMsg("Skipping %s since TIER only state" % self.dut.nextState)
               self.dut.nextState = evalPhaseOut(StateTable[oper][self.dut.nextState][TRANS])['pass']
               continue

            #if drive isn't Tier1 but Tier1 required then skip
            elif ( CommitServices.getTab( self.dut.partNum ) != TIER1 ) and (TIER1 in StateTable[oper][self.dut.nextState][OPT]):
               objMsg.printMsg("Skipping %s since is a TIER1 only state" % self.dut.nextState)
               self.dut.nextState = evalPhaseOut(StateTable[oper][self.dut.nextState][TRANS])['pass']
               continue

            #if drive is Tier1 but not Tier1 required then skip
            elif ( CommitServices.getTab( self.dut.partNum ) != TIER2 ) and (TIER2 in StateTable[oper][self.dut.nextState][OPT]):
               objMsg.printMsg("Skipping %s since is a TIER2 only state" % self.dut.nextState)
               self.dut.nextState = evalPhaseOut(StateTable[oper][self.dut.nextState][TRANS])['pass']
               continue

            #if drive isn't T03 but T03 required then skip
            elif ( CommitServices.getTab( self.dut.partNum ) != TIER3 ) and (TIER3 in StateTable[oper][self.dut.nextState][OPT]):
               objMsg.printMsg("Skipping %s since is a TIER3 only state" % self.dut.nextState)
               self.dut.nextState = evalPhaseOut(StateTable[oper][self.dut.nextState][TRANS])['pass']
               continue

         elif testSwitch.FE_0189561_418088_IRECOVERY_SUPPORT and 'IR' in StateTable[oper][self.dut.nextState][OPT]:
            import base_RecoveryTest
            try:
               objMsg.printMsg("self.dut.failureData[0][2] : %s" %`self.dut.failureData[0][2]`)
               ec = int(self.dut.failureData[0][2])
            except:
               objMsg.printMsg("Traceback... \n%s" % traceback.format_exc())
               ec = -1
            if ec in base_RecoveryTest.IR_ExcludeECList:
               objMsg.printMsg("Skipping IRECOVERY state since %s is in iRecovery exclude EC list" %ec)
               self.dut.nextState = evalPhaseOut(StateTable[oper][self.dut.nextState][TRANS])['fail']
               continue
            elif ec != -1 and (str(ec) not in  base_RecoveryTest.RecoveryRulesBased.keys()):
               objMsg.printMsg("Skipping IRECOVERY state since %s not found in iRecovery Rule-base" %ec)
               self.dut.nextState = evalPhaseOut(StateTable[oper][self.dut.nextState][TRANS])['fail']
               continue
            elif ec == -1:
               objMsg.printMsg("Skipping IRECOVERY state since self.dut.failureData[0][2] not found")
               DriveAttributes['IR_STATUS'] = 'EXCURSION'
               self.dut.nextState = evalPhaseOut(StateTable[oper][self.dut.nextState][TRANS])['fail']
               continue

         if testSwitch.shortProcess and oper in testSwitch.shortProcess.keys():
            # If running a short process, figure out which states to run
            listNum = testSwitch.shortProcess[oper]

            # Figure out if the plugin is setup correctly. This will catch if the wrong oper or list number was specified.
            try: temp = TP.shortProcessOptions[oper][listNum]
            except KeyError: ScrCmds.raiseException(11044, 'Short Process plugin setup incorrectly')

            if self.dut.nextState not in TP.shortProcessOptions[oper][listNum]:
               if chkDepend:
                  msg = 'Bypassing dependancy check for %s state for short process' % self.dut.nextState
               else:
                  msg = 'Bypassing %s state for short process' % self.dut.nextState
               objMsg.printMsg(msg)
               self.dut.nextState = evalPhaseOut(StateTable[oper][self.dut.nextState][TRANS])['pass']
               continue

         if testSwitch.FE_0156504_357260_P_RAISE_GOTF_FAILURE_THROUGH_FAIL_PROC:
            self.dut.gotfState = self.dut.nextState

         #For CPC tracking
         if testSwitch.CPCWriteReadRemoval and self.dut.nextOper in ['FIN2','CUT2','FNG2']:
            objMsg.printMsg('Tracking List before new test state = %s' % self.dut.TrackingList)

         #For temperature monitoring
         if hasattr(TP,'temperatureLoggingList'):   curState = self.dut.nextState

         #We passed all criteria: run state
         if testSwitch.FE_0189561_418088_IRECOVERY_SUPPORT:
            IR_current_state = self.dut.objData.get('NEXT_STATE','UNKNOWN')
         self.execState( oper, self.dut.nextState, chkDepend ) # execute the state (test block)

         #GOTF scoring
         if self.dut.stateTransitionEvent == 'depopRestart':        #reset gotf score to all X's
            objMsg.printMsg(self.dut.stateTransitionEvent + " Transition...resetting GOTF drive score to X's")
            self.oGOTF.gotfResetDriveScore()

         if not chkDepend:
            if (oper == 'CUT2' and not (self.dut.partNum in getattr(TP,'TODT_PN',['NONE'])or 'ALL' in getattr(TP,'TODT_PN',['NONE']))) or (oper == 'TODT'):
               if self.dut.nextState == 'COMPLETE' and testSwitch.DISABLE_SCORECOMPARE == 0 :
                  passedScoreCompare = self.oGOTF.gotfCompareScores(self.dut.driveattr['DRIVE_SCORE'], self.dut.driveattr['CUST_SCORE'])
                  if not passedScoreCompare:
                     msg = "Post-CMT2 grading check - CUST_SCORE %s and DRIVE_SCORE %s do not match" % (str(self.dut.driveattr['CUST_SCORE']), str(self.dut.driveattr['DRIVE_SCORE']))
                     if (testSwitch.virtualRun == 1) or (testSwitch.auditTest==1) or (testSwitch.DISABLE_POSTCMT2_GOTF_CHK==1):
                        objMsg.printMsg(msg)
                     else:
                        ScrCmds.raiseException(14733, msg)
            if testSwitch.FE_0143655_345172_P_SPECIAL_SBR_ENABLE:
               if self.dut.stateTransitionEvent == 'pass' and (self.dut.spSBG.spSBGGOTF) and self.dut.nextOper not in GOTF_EXCLUDED_OPERS:
                  ScrCmds.statMsg("Special SBR Condition 7 -Enable GOTFs.")
                  self.oGOTF.gotfGradeState(self.dut.currentState)
                  #objMsg.printMsg("Grading results %s" % str(self.oGOTF.gotfGradingResults))
                  self.oGOTF.gotfUpdateDblTbl()

                  if self.oGOTF.gotfTestGroup('ALL') == False: #using gotf tools to fail drive for a test
                     self.dut.Status_GOTF = 0
                     self.dut.failureState = self.dut.currentState
                     self.failDrive(self.oGOTF.failtable,self.oGOTF.failcolumn,self.oGOTF.failcode,self.oGOTF.failcriteria_op,self.oGOTF.failcriteria_val,self.oGOTF.failed_meas_values,self.oGOTF.failcriteria_vio,self.oGOTF.failcriteria_filterDict)
                     if testSwitch.FE_0156504_357260_P_RAISE_GOTF_FAILURE_THROUGH_FAIL_PROC:
                        self.dut.nextState = evalPhaseOut(StateTable[oper][self.dut.gotfState][TRANS])[self.dut.stateTransitionEvent]

                  if DEBUG > 0:
                     objMsg.printMsg("gotfBsnsList before=%s" % `self.dut.gotfBsnsList`)
                  IsChanged = 0
                  for i in self.dut.gotfBsnsList[:]:
                     if DEBUG > 0:
                        objMsg.printMsg("gotfBsnsList i=%s" % i)
                     res = self.oGOTF.gotfTestGroup(i)
                     if DEBUG > 0:
                        objMsg.printMsg("gotfBsnsList res=%s" % res)
                     if res == 0:
                        self.dut.gotfBsnsList.remove(i)
                        IsChanged = 1

                  if DEBUG > 0:
                     objMsg.printMsg("gotfBsnsList after=%s" % `self.dut.gotfBsnsList`)
                  if len(self.dut.gotfBsnsList) == 0 and len(self.dut.manual_gotf) == 0:
                     msg = "Drive cannot further downgrade as no more valid Business Groups available"
                     ScrCmds.raiseException(13425, msg)

                  if IsChanged:
                     self.dut.longattr_bg = str.join("/", self.dut.gotfBsnsList)    # must convert list to string
                     objMsg.printMsg("gotfBsnsList changed. Updated self.dut.longattr_bg=%s" % self.dut.longattr_bg)

               elif not (self.dut.spSBG.spSBGGOTF):
                  ScrCmds.statMsg("Special SBR Condition 7 -Disable GOTFs.")
               #ScrCmds.statMsg("BUG gotfTestGroup : %s" % self.oGOTF.gotfTestGroup(self.dut.BG))
               if self.dut.stateTransitionEvent == 'pass' and (self.dut.spSBG.spSBGGOTF) and self.oGOTF.gotfTestGroup(self.dut.BG) == False:
                  if not testSwitch.FE_0221005_504374_P_3TIER_MULTI_OPER:
                     self.ChkCMT2TestDone(oper)
                  #ScrCmds.statMsg("BUG manual_gotf : %s" % self.dut.manual_gotf)
                  if len(self.dut.manual_gotf) > 0 and ( testSwitch.AutoCommit == 0 or testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT):      # manual commit only (skip for autocommit)

                     if not testSwitch.FE_0189561_418088_IRECOVERY_SUPPORT:
                        if testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT:
                           self.dut.driveattr['WTF_CTRL'] = ('%s_%s_%d'%(oper, self.dut.partNum[-3:],self.oGOTF.gotfDowngradePos(self.dut.BG)))
                           self.changeBG()
                           self.changePN()
                        else:
                           # Original YarraR algo
                           self.changeBG()
                           objMsg.printMsg("Business group changed to %s" % str(self.dut.BG))
                           self.dut.driveattr['WTF_CTRL'] = ('%s_%s_%d'%(oper, self.dut.partNum[-3:],self.oGOTF.gotfDowngradePos(self.dut.BG)))

                           if testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT:
                              self.changePN()
                           else:
                              # search back BG -> PN
                              pn = self.dut.manual_gotf[self.dut.BG][self.dut.bgIndex]
                              if len(pn) != 10:    # safety net
                                 ScrCmds.raiseException(11044, 'Part Number in manual_gotf is invalid')
                              self.dut.partNum = pn
                              self.dut.driveattr['BSNS_SEGMENT'] = self.dut.BG
                              self.dut.driveattr['PART_NUM'] = self.dut.partNum
                              if not testSwitch.FE_0190240_007955_USE_FILE_LIST_FUNCTIONS_FROM_DUT_OBJ:
                                 from Setup import CSetup
                                 CSetup().buildFileList()
                              else:
                                 self.dut.buildFileList()                                 
                              objMsg.printMsg("Part number changed to %s" % str(self.dut.partNum))
                     else:
                        try:
                           self.dut.driveattr['WTF_CTRL'] = ('%s_%s_%d'%(oper, self.dut.partNum[-3:],self.oGOTF.gotfDowngradePos(self.dut.BG)))
                           self.changeBG()
                        except CRaiseException,exceptionData:
                           self.dut.stateTransitionEvent = 'fail'
                           if testSwitch.BF_0193059_357260_P_ALWAYS_TREAT_FAILUREDATA_AS_TUPLE:
                              self.dut.failureData = exceptionData.args
                           else:
                              self.dut.failureData = exceptionData
                           self.dut.nextState = evalPhaseOut(StateTable[oper][self.dut.gotfState][TRANS])[self.dut.stateTransitionEvent]
                        if self.dut.stateTransitionEvent == 'pass':
                           self.changePN()

               elif self.dut.spSBG.spSBGGOTF:
                  if self.dut.spSBG.spSBGGOTFPN:
                     ScrCmds.statMsg("Special SBR Condition 5 -Enable downgrade to other tab.")
                  else:
                     ScrCmds.statMsg("Special SBR Condition 5 -Disable downgrade to other tab.")

            else:
               if self.dut.stateTransitionEvent == 'pass' and self.dut.nextOper not in GOTF_EXCLUDED_OPERS:
                  self.oGOTF.gotfGradeState(self.dut.currentState)
                  #objMsg.printMsg("Grading results %s" % str(self.oGOTF.gotfGradingResults))
                  self.oGOTF.gotfUpdateDblTbl()

                  if self.oGOTF.gotfTestGroup('ALL') == False: #using gotf tools to fail drive for a test
                     from OTF_Waterfall import CDepop_OTF_Check
                     oDPOTF = CDepop_OTF_Check(self.dut)

                     if oDPOTF.dpotfCheck(self.oGOTF.failcode, 0):
                        self.failDrive(self.oGOTF.failtable,self.oGOTF.failcolumn,self.oGOTF.failcode,self.oGOTF.failcriteria_op,self.oGOTF.failcriteria_val,self.oGOTF.failed_meas_values,self.oGOTF.failcriteria_vio,self.oGOTF.failcriteria_filterDict)
                     else:
                        self.dut.Status_GOTF = 0
                        self.dut.failureState = self.dut.currentState
                        self.failDrive(self.oGOTF.failtable,self.oGOTF.failcolumn,self.oGOTF.failcode,self.oGOTF.failcriteria_op,self.oGOTF.failcriteria_val,self.oGOTF.failed_meas_values,self.oGOTF.failcriteria_vio,self.oGOTF.failcriteria_filterDict)
                        if testSwitch.FE_0156504_357260_P_RAISE_GOTF_FAILURE_THROUGH_FAIL_PROC:
                           self.dut.nextState = evalPhaseOut(StateTable[oper][self.dut.gotfState][TRANS])[self.dut.stateTransitionEvent]

                  if DEBUG > 0:
                     objMsg.printMsg("gotfBsnsList before=%s" % `self.dut.gotfBsnsList`)
                  IsChanged = 0
                  for i in self.dut.gotfBsnsList[:]:
                     if DEBUG > 0:
                        objMsg.printMsg("gotfBsnsList i=%s" % i)
                     res = self.oGOTF.gotfTestGroup(i)
                     if DEBUG > 0:
                        objMsg.printMsg("gotfBsnsList res=%s" % res)
                     if res == 0:
                        self.dut.gotfBsnsList.remove(i)
                        IsChanged = 1

                  if DEBUG > 0:
                     objMsg.printMsg("gotfBsnsList after=%s" % `self.dut.gotfBsnsList`)
                  if len(self.dut.gotfBsnsList) == 0 and len(self.dut.manual_gotf) == 0:
                     msg = "Drive cannot further downgrade as no more valid Business Groups available"
                     ScrCmds.raiseException(13425, msg)

                  if IsChanged:
                     self.dut.longattr_bg = str.join("/", self.dut.gotfBsnsList)    # must convert list to string
                     objMsg.printMsg("gotfBsnsList changed. Updated self.dut.longattr_bg=%s" % self.dut.longattr_bg)

               if self.dut.stateTransitionEvent == 'pass' and self.oGOTF.gotfTestGroup(self.dut.BG) == False:
                  self.ChkCMT2TestDone(oper)

                  if len(self.dut.manual_gotf) > 0 and (testSwitch.AutoCommit == 0 or testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT):      # manual commit only (skip for autocommit)
                     if not testSwitch.FE_0189561_418088_IRECOVERY_SUPPORT:

                        if testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT:
                           self.dut.driveattr['WTF_CTRL'] = ('%s_%s_%d'%(oper, self.dut.partNum[-3:],self.oGOTF.gotfDowngradePos(self.dut.BG)))
                           self.changePN()
                           self.changeBG()
                        else:
                           # original YarraR GOTF
                           self.dut.driveattr['WTF_CTRL'] = ('%s_%s_%d'%(oper, self.dut.partNum[-3:],self.oGOTF.gotfDowngradePos(self.dut.BG)))
                           OldBG = self.dut.BG
                           self.changeBG()
                           objMsg.printMsg("Business group changed to %s" % str(self.dut.BG))

                           # search back BG -> PN
                           pn = self.dut.manual_gotf[self.dut.BG][self.dut.bgIndex]
                           if len(pn) != 10:    # safety net
                              ScrCmds.raiseException(11044, 'Part Number in manual_gotf is invalid')

                           OldPN = self.dut.partNum
                           self.dut.partNum = pn
                           self.dut.driveattr['BSNS_SEGMENT'] = self.dut.BG
                           self.dut.driveattr['PART_NUM'] = self.dut.partNum
                           ScrCmds.HostSetPartnum(self.dut.partNum)
                           objMsg.printMsg("Part number changed to %s" % str(self.dut.partNum))
                           self.ChkGOTFRetest(oldpn=OldPN, newpn=pn, oldbg=OldBG, newbg=self.dut.BG)
                           if not testSwitch.FE_0190240_007955_USE_FILE_LIST_FUNCTIONS_FROM_DUT_OBJ:
                              from Setup import CSetup
                              CSetup().buildFileList()
                           else:
                              self.dut.buildFileList()                              

                     else: #testSwitch.FE_0189561_418088_IRECOVERY_SUPPORT = 1
                        try:
                           self.dut.driveattr['PROC_CTRL12'] = ('%s_%s_%d'%(oper, self.dut.partNum[-3:],self.oGOTF.gotfDowngradePos(self.dut.BG)))
                           self.changeBG()

                        except CRaiseException,exceptionData:
                           self.dut.stateTransitionEvent = 'fail'
                           if testSwitch.BF_0193059_357260_P_ALWAYS_TREAT_FAILUREDATA_AS_TUPLE:
                              self.dut.failureData = exceptionData.args
                           else:
                              self.dut.failureData = exceptionData
                           self.dut.nextState = evalPhaseOut(StateTable[oper][self.dut.gotfState][TRANS])[self.dut.stateTransitionEvent]

                        if self.dut.stateTransitionEvent == 'pass':
                           self.changePN()


            self.dut.seqNum += 1 # do not increment sequence number if only checking dependencies
            self.writeSeqNum(self.dut.seqNum) # write the seq num to the binary file for dex

            if testSwitch.virtualRun == 1:
               self.dut.objSeq.setSeq(self.dut.seqNum)

            #For CPC tracking
            if testSwitch.CPCWriteReadRemoval and self.dut.nextOper in ['FIN2','CUT2','FNG2'] and \
               not testSwitch.virtualRun:
               objMsg.printMsg('Report new tracking records')
               result = ICmd.CommandLocation(3)
               objMsg.printMsg('result = %s' % result)
               self.dut.TrackingList = self.dut.TrackingList + result['RES']
               objMsg.printMsg('Updated Tracking List = %s' % self.dut.TrackingList)
               self.dut.objData.update({'TrackingList': self.dut.TrackingList})

               #enable, reset and setup tracking
               objMsg.printMsg('Reset and start tracking, numLBA = %d numTrackingZone = %d'% (self.dut.numLba,self.dut.numTrackingZone))
               result = ICmd.CommandLocation(1,self.dut.numTrackingZone,self.dut.numLba)

            if hasattr(TP,'CheckFirstSysTrackList') and oper in TP.CheckFirstSysTrackList:
               if TP.CheckFirstSysTrackList[oper] == 'ALL' or curState in TP.CheckFirstSysTrackList[oper]:
                  try:
                     if (oper == 'PRE2' and self.dut.systemAreaPrepared) or (oper in ['CAL2','FNC2','CRT2','FIN2']):    # can only read system track after it's initialised
                        if curState in ["INIT", "END_TEST", "FAIL_PROC", "SDOD"]:
                           objMsg.printMsg('Skipping CheckSystemFirstTrack() for %s...' % curState)
                        else:
                           objMsg.printMsg('Running CheckSystemFirstTrack() for %s...' % curState)
                           self.CheckSystemFirstTrack()     # read first system track and report if error encountered
                  except:
                     objMsg.printMsg('Unable to read system area...')



            #For temperature monitoring
            if hasattr(TP,'temperatureLoggingList'):
               if not testSwitch.FE_0314243_356688_P_CM_REDUCTION_REDUCE_PROCESS_MSG:
                  objMsg.printMsg('Oper = %s, State = %s'% (oper,curState))
               drive_temp = 0 
               maximumDriveTemp = TP.temp_profile.get('maximumDriveTemp',65)
               objMsg.printMsg('Oper = %s, State = %s, maximumDriveTemp = %s'% (oper,curState,maximumDriveTemp))

               try:
                  if not testSwitch.FE_0314243_356688_P_CM_REDUCTION_REDUCE_PROCESS_MSG:
                     objMsg.printMsg('TP.temperatureLoggingList[oper] %s'% (TP.temperatureLoggingList.get(oper)))

                  if TP.temperatureLoggingList.get(oper) == 'ALL' or curState in TP.temperatureLoggingList.get(oper, []):
                     if not testSwitch.FE_0314243_356688_P_CM_REDUCTION_REDUCE_PROCESS_MSG:
                        objMsg.printMsg("Running temperature monitoring for state %s" % str(curState))

                     try:
                        cell_temp = ReportTemperature()/10.0
                        if curState == "INIT" or curState == "END_TEST" or curState == "FAIL_PROC" or curState == "SDOD":   drive_temp = 0.0
                        else: drive_temp = self.ReadTemp()/1.0
                        objMsg.printMsg('State Name:%s Cell Temp:%s Drive Temp:%s' % (curState, cell_temp,drive_temp))
                        tcData = GetTempCtrlData()
                        driveRPM,elecRPM = struct.unpack(">2H",tcData[34:38])
                        objMsg.printMsg('Drive RPM: %s  Elec RPM: %s' % (driveRPM,elecRPM))
                         
                        self.dut.dblData.Tables('P_TEMPERATURES').addRecord(
                                       {
                                       'SPC_ID'       : 0,
                                       'OCCURRENCE'   : 0,
                                       'SEQ'          : self.dut.seqNum,
                                       'TEST_SEQ_EVENT': 0,
                                       'STATE_NAME'   : curState,
                                       'DRIVE_TEMP'   : drive_temp,
                                       'CELL_TEMP'    : cell_temp,
                                       'DRIVE_FAN_RPM': driveRPM,
                                       'ELEC_FAN_RPM' : elecRPM,
                                       })
                        if objRimType.IsPSTRRiser():
                           RequestService('SetScriptInfo', ("Drive temp:%s" %drive_temp,))
                     except:
                        objMsg.printMsg('Unable to read temp... %s' % `traceback.format_exc()`)
               except:
                  objMsg.printMsg('Oper (%s) / State (%s) is not in TP.temperatureLoggingList' %(oper,curState))

               if drive_temp > maximumDriveTemp:
                  objMsg.printMsg('Abort! Drive Temperature(%s) above maximumDriveTemp (%s)!' %(drive_temp,maximumDriveTemp))
                  ScrCmds.raiseException(42227, "Drive Temperature above maximumDriveTemp") 
               if self.dut.BG in ['SBS'] and drive_temp < 0:
                  objMsg.printMsg('Abort! Drive Temperature(%s) < 0!' %drive_temp)
                  ScrCmds.raiseException(42227, "Drive Temperature < 0") 
                  
                  
            #For PBIC KPIV data collection
            if testSwitch.PBIC_SUPPORT:
               from PBIC import ClassPBIC
               objPBIC = ClassPBIC()
               if hasattr(TP,'kpivdatastateList'):
                  if not testSwitch.FE_0314243_356688_P_CM_REDUCTION_REDUCE_PROCESS_MSG:
                     objMsg.printMsg('Oper = %s, State = %s'% (oper,curState))
                  drive_temp = 0 
                  maximumDriveTemp = TP.temp_profile.get('maximumDriveTemp',65)
                  objMsg.printMsg('Oper = %s, State = %s, maximumDriveTemp = %s'% (oper,curState,maximumDriveTemp))

                  try:
                     #objMsg.printMsg('TP.kpivdatastateList[oper] %s'% (TP.kpivdatastateList.get(oper)))

                     if TP.kpivdatastateList.get(oper) == 'ALL' or curState in TP.kpivdatastateList.get(oper, []):
                        objMsg.printMsg("Running PBIC kpiv data collection for state %s" % str(curState))
                        objPBIC.KPIV_collection() 
                  except:
                     objMsg.printMsg('Oper (%s) / State (%s) is not in TP.kpivdatastateList' %(oper,curState))

            # update CUST_SCORE & DRIVE_SCORE attributes as requested by Process - knl 16Apr08
            try:
               self.dut.driveattr['CUST_SCORE'] = self.oGOTF.gotfCustScore(self.dut.BG)
            except:
               #objMsg.printMsg("Unable to get CUST_SCORE. Traceback=%s" % traceback.format_exc())
               self.dut.driveattr['CUST_SCORE'] = "NONE"

            try:
               self.dut.driveattr['DRIVE_SCORE'] = self.oGOTF.gotfDriveScore(self.dut.BG)
            except:
               #objMsg.printMsg("Unable to get DRIVE_SCORE. Traceback=%s" % traceback.format_exc())
               self.dut.driveattr['DRIVE_SCORE'] = "NONE"

            objMsg.printMsg("CUST_SCORE=%s DRIVE_SCORE=%s" % (str(self.dut.driveattr['CUST_SCORE']), str(self.dut.driveattr['DRIVE_SCORE'])))

            #Update all necessary variables to disc for power loss recovery.
            if testSwitch.FE_0180513_007955_COMBINE_CRT2_FIN2_CUT2:
               self.dut.objData.update({'certOper': self.dut.certOper})
            self.dut.objData.update({'NEXT_OPER': oper, 'NEXT_STATE': self.dut.nextState, 'SEQ_NUM': self.dut.seqNum,}) # pickle drive and state information
            self.dut.dblParser.objDbLogIndex.streamIndexFile()

            self.dut.objData.update({'STATE_DBLOG_INFO':self.dut.stateDBLogInfo})
            self.dut.objData.update({'DriveAttributes':self.dut.driveattr})
            self.dut.objData.update({'depopMask':self.dut.depopMask})
            self.dut.objData.update({'HDSTR_PROC':self.dut.HDSTR_PROC})
            self.dut.objData.update({'HDSTR_UNLOAD_ACTIVE':self.dut.HDSTR_UNLOAD_ACTIVE})
            self.dut.objData.update({'HDSTR_RETEST':self.dut.HDSTR_RETEST})
            self.dut.objData.update({'CCVSampling':self.dut.CCVSampling})
            if testSwitch.FE_0163083_410674_RETRIEVE_P_VBAR_NIBLET_TABLE_AFTER_POWER_RECOVERY:
               self.dut.objData.update({'OCC_VBAR_NIBLET':self.dut.OCC_VBAR_NIBLET})
               self.dut.objData.update({'vbar_niblet':self.dut.vbar_niblet})
            if testSwitch.FE_0164322_410674_RETRIEVE_P_VBAR_TABLE_AFTER_POWER_RECOVERY:
               self.dut.objData.update({'OCC_PWR_PICKER':self.dut.OCC_PWR_PICKER})
               self.dut.objData.update({'OCC_PWR_TRIPLETS':self.dut.OCC_PWR_TRIPLETS})
               self.dut.objData.update({'vbar_format_sum':self.dut.vbar_format_sum})
               self.dut.objData.update({'vbar_hms_adjust':self.dut.vbar_hms_adjust})
               self.dut.objData.update({'wrt_pwr_picker':self.dut.wrt_pwr_picker})
               self.dut.objData.update({'wrt_pwr_triplets':self.dut.wrt_pwr_triplets})
               if getattr(self.dut, 'spcIdHelper', None) is not None:
                  self.dut.objData.update({'spcIdHelper':self.dut.spcIdHelper})
            if testSwitch.FE_0134030_347506_SAVE_AND_RESTORE:
               #save process specific variables like vbar, afh settings
               self.dut.storeProcessData()

            if testSwitch.CACHE_TABLEDATA_OBJ:
               self.dut.dblData.clearCachedData()

            try:
               objMsg.printMsg("GarbageCollect ret=%s" %  repr(GarbageCollect()))
            except:
               objMsg.printMsg("GarbageCollect failed: %s" % (traceback.format_exc(),))

         if testSwitch.FE_0189561_418088_IRECOVERY_SUPPORT and (self.dut.nextState == 'FAIL_PROC' and IR_current_state != iRecoveryStateName and self.dut.nextOper not in IR_EXCLUDED_OPERS):
            objMsg.printMsg("iRecovery enabled, Perform %s state before go to FAIL_PROC state" %(iRecoveryStateName))
            self.dut.nextState = iRecoveryStateName

         if testSwitch.FE_0220066_395340_P_AUTO_RE_DL_GTGA_FOR_ALL_DOWNGRADE:
            if getattr(self.dut ,'INIT_IO','NONE') == 'DONE' and getattr(self.dut ,'PNChanged','NONE') == 'DONE':
               if testSwitch.FE_0221005_504374_P_3TIER_MULTI_OPER:
                  self.dut.nextState = self.dut.objData.get('INIT_STATE','INIT')
               else:
                  self.dut.nextState = self.dut.objData.get('INIT_STATE','INIT_I_R')
            self.dut.PNChanged = 'NONE'
         else:
            if ( not CommitServices.isTierPN( self.dut.partNum ) ) and testSwitch.FE_0208720_470167_P_AUTO_DOWNGRADE_BLUENUN_FAIL_FOR_APPLE and getattr(self.dut, 'failBluenun',False) == True:
               self.dut.failBluenun = False
               if testSwitch.FE_0221005_504374_P_3TIER_MULTI_OPER:
                  self.dut.nextState = 'DNLD_U_CODE2'
               else:
                  self.dut.nextState = 'DNLD_U_CODE'

      if self.dut.nextState == 'FAIL':
         raise ScriptTestFailure, self.dut.failureData

      try:
         BestScore = str.join('', self.oGOTF.BestScore)
         self.dut.driveattr['GOTF_BEST_SCORE'] = self.AddScore(self.dut.driveattr['GOTF_BEST_SCORE'], BestScore)
         objMsg.printMsg("BestScore=%s Accumulative=%s" % (BestScore, self.dut.driveattr['GOTF_BEST_SCORE']))
      except:
         objMsg.printMsg("Unable to get GOTF_BEST_SCORE. Traceback=%s" % traceback.format_exc())
         self.dut.driveattr['GOTF_BEST_SCORE'] = "NONE"


   #-------------------------------------------------------------------------------------------------------
   def ReadTemp(self):     # Loke

      from Temperature import CTemperature
      thermistor = 0

      try:
         if not self.dut.f3Active:
            thermistor = CTemperature().retHDATemp()
            if not testSwitch.FE_0314243_356688_P_CM_REDUCTION_REDUCE_PROCESS_MSG:
               objMsg.printMsg("SF3 thermistor data=%s" % thermistor)
         else:
            thermistor = CTemperature().getF3Temp()
            objMsg.printMsg("F3 thermistor data=%s" % thermistor)
      except:
         ReportErrorCode(0)

      return thermistor

   #------------------------------------------------------------------------------------------------------#
   def CheckSystemFirstTrack(self):
      try:
         if self.dut.f3Active:
            import sptCmds
            iLevel, iCyl, iHd, iSect, iLen = TP.CheckFirstSysTrackCmd
            sptCmds.enableDiags()
            objMsg.printMsg('Go to level %s...' % iLevel)
            sptCmds.gotoLevel(iLevel)
            sptCmds.sendDiagCmd('A0', printResult = False)
            sptCmds.sendDiagCmd('S%d,%d,,,,1' % (iCyl, iHd), printResult = False)  # seek to reserve lba
            try:
               sptCmds.sendDiagCmd('r,%d,%d' % (iSect, iLen), printResult = True)
            except:
               objMsg.printMsg('Check SysAreaStartTrack Error: ERROR')
            else:
               objMsg.printMsg('Check SysAreaStartTrack Error: 0')
         else:
            from Process import CCudacom
            from Servo import CServo
            oCudacom = CCudacom()
            oServo = CServo()
            iCyl, iHd = TP.CheckFirstSysTrackCmd

            try:
               sysZt = self.dut.dblData.Tables(TP.zone_table['resvd_table_name']).tableDataObj()
               TableIndex = self.dth.getFirstRowIndexFromTable_byHead(sysZt, iHd)
               SysAreaStartTrack = int(sysZt[TableIndex]['ZN_START_CYL']) + iCyl
            except:
               from FSO import CFSO
               CFSO().getZnTblInfo(spc_id = 0, supressOutput = 0)   
               sysZt = self.dut.dblData.Tables(TP.zone_table['resvd_table_name']).tableDataObj()
               TableIndex = self.dth.getFirstRowIndexFromTable_byHead(sysZt, iHd)
               SysAreaStartTrack = int(sysZt[TableIndex]['ZN_START_CYL']) + iCyl

            objMsg.printMsg('Reading track %d head %d...' % (SysAreaStartTrack, iHd))
            ret = oServo.rsk(SysAreaStartTrack, iHd) # cyl, head
            buf, errorCode = oCudacom.Fn(1356, 1)   # read 1 track
            objMsg.printMsg('Check SysAreaStartTrack Error: %s' % (str(errorCode)))
      except:
         pass

   #------------------------------------------------------------------------------------------------------#
   def ChkGOTFRetest(self, oldpn='', newpn='', oldbg='', newbg=''):
      '''
         Check if GOTF downgrade is allowed; if not, do a reCRT2
      '''

      try:
         from PIF import retestGOTF
      except:
         return

      from PIFHandler import CPIFHandler
      PIFHandler = CPIFHandler()

      dRetest = PIFHandler.getPnumInfo(sPnum=self.dut.nextOper, dPNumInfo=retestGOTF, GetAll=True)
      lstRetest = dRetest.get('AllLst', [])
      objMsg.printMsg('lstRetest oper=%s' % (lstRetest))
      if len(lstRetest) == 0:
         return

      sCTQ = "%02d" % self.GetCTQ(tmpbg=oldbg)
      objMsg.printMsg('iCTQ=%s' % (sCTQ))
      dRetest = PIFHandler.getPnumInfo(sPnum=sCTQ, dPNumInfo=lstRetest[0], GetAll=True)
      lstRetest = dRetest.get('AllLst', [])
      objMsg.printMsg('lstRetest CTQ=%s' % lstRetest)
      if len(lstRetest) == 0:
         return
      tmpGOTFRetest = lstRetest[0]
      if len(tmpGOTFRetest) == 0:
         return

      # Chk if new downgraded Drive P/NO is in Codes.py, if not fail and exit Gemini
      from Codes import fwConfig
      if not fwConfig.has_key(newpn):
         ScrCmds.raiseException(14731, 'New PN %s not found in Codes.py fwConfig' % newpn)   # Process to decide new failcode

        # Check SFWP equal previous P/NO SFWP
      #OldServoCode = fwConfig[oldpn].get('SFWP', '')
      #NewServoCode = fwConfig[newpn].get('SFWP', '')
      #objMsg.printMsg('OldServoCode=%s NewServoCode=%s' % (OldServoCode, NewServoCode))

      #if bool(retestGOTF.get('SKIP_SFWP_CHECK', False)) == True:
      #   objMsg.printMsg('Skipping servo code check')
      #else:
      #   if NewServoCode == '' or NewServoCode != OldServoCode:
      #      ScrCmds.raiseException(14731, 'New servo code [%s] not match with old servo code' % NewServoCode)   # Process to decide new failcode

       # check TGTP
      #OldTargetCode = fwConfig[oldpn].get('TGTP', '')
      #NewTargetCode = fwConfig[newpn].get('TGTP', '')
      #objMsg.printMsg('OldTargetCode=%s NewTargetCode=%s' % (OldTargetCode, NewTargetCode))

      #if NewTargetCode != '' and NewTargetCode == OldTargetCode and NewServoCode != '' and NewServoCode == OldServoCode:
      #   try:
      #      tmpGOTFRetest = retestGOTF[self.dut.nextOper]["RE_OPER"]
      #      objMsg.printMsg('RE_OPER=%s' % tmpGOTFRetest)
      #   except:
      #      objMsg.printMsg('RE_OPER not found. Proceed with GOTF downgrade')
      #      return

      if int(DriveAttributes.get("LOOPER_COUNT", "0")) >= 1:
         ScrCmds.raiseException(14732, 'GOTF Rerun count LOOPER_COUNT exceeded')

      # now, we can proceed with GOTF retest
      self.dut.GOTFRetest = tmpGOTFRetest
      objMsg.printMsg("GOTF retest PN %s" % newpn)
      ScrCmds.HostSetPartnum(newpn)

      if self.dut.RetestLastErr == None:
         ScrCmds.raiseException(14730, 'GOTF restart...')
      else:
         objMsg.printMsg("GOTF retest oldpn %s" % oldpn)
         self.dut.RetestPN = oldpn
         objMsg.printMsg("GOTF retest self.dut.RetestPN %s" % self.dut.RetestPN)
         errCode = self.dut.RetestLastErr[0][2]
         errMsg = self.dut.RetestLastErr[0][0]
         ScrCmds.raiseException(errCode, errMsg)

   #------------------------------------------------------------------------------------------------------#
   def AddScore(self, old, new):
      '''
         Accumulate cust score values
      '''

      if self.dut.nextOper == 'PRE2':
         return new

      iMaxLen = 32
      if old == "NONE":
         old = 'X' * iMaxLen
      if new == "NONE":
         new = 'X' * iMaxLen

      if len(old) > iMaxLen or len(new) > iMaxLen:
         ScrCmds.raiseException(13425, "Score length cannot be greater than %s" % iMaxLen)

      AccStr = ""
      OldStr = old.upper() + 'X' * (iMaxLen - len(old))
      NewStr = new.upper() + 'X' * (iMaxLen - len(new))

      for i in xrange(iMaxLen):
         if OldStr[i] == 'X' and NewStr[i] == 'X':
            AccStr += 'X'
         elif OldStr[i] == 'X':
            AccStr += NewStr[i]
         elif NewStr[i] == 'X':
            AccStr += OldStr[i]
         else:
            if OldStr[i] < NewStr[i]:
               AccStr += OldStr[i]
            else:
               AccStr += NewStr[i]

      return AccStr

   def checkStateEnabledBySwitch(self, stateOption):
      """
      Function checks to see if the switch set by the state options is enabled or disabled
      """
      #if enabled by testSwitch or extern
      for item in stateOption:
         if type(item) == dict:
            break
      else:
         return True

      for flag, value in item.items():
         if getattr(testSwitch, flag) != value:
            objMsg.printMsg("Skipping state %s since required flag isn't set." % self.dut.nextState)
            return False

      return True

   #------------------------------------------------------------------------------------------------------#
   def handlePartnumFilteredState(self):
      """
      Function checks to see if this state matches partnumber requirements in states_PN in PIF
         Returns True or False identifying if state should be executed or not.
      """
      if self.dut.nextState in states_PN:
         for pnPattern in states_PN[self.dut.nextState]:
            if re.search(pnPattern, self.dut.partNum):
               return True #we matched

         else:
            #no match don't run the state
            objMsg.printMsg("Skipping state %s: PN %s matching failed" % (self.dut.nextState, self.dut.partNum))
            return False
      else:
         #if the state doesn't have PN criteria defined then we run it to be safe
         return True

      return False


   #------------------------------------------------------------------------------------------------------#

   def writeSeqNum(self,seqNum, testNumber = -7):

      if testNumber == -7:
         # Start of sequence
         blockCode="\007"

      # Create the 25 byte header
      header1=blockCode + struct.pack('>h', testNumber) + 22*"0"  # 1 byte block code, 2 bytes test number (-7), 2 bytes error code, 20 bytes parms (2 bytes for each of 10 params)
      header2=struct.pack('>h', seqNum) + "\x00\x00"           # sequence number and revision
      if testSwitch.virtualRun:
         objMsg.printMsg("Seq Num: %s,Stat Test Num: %s" % (seqNum, testNumber))
      else:
         self.dut.dblParser.ESGSaveResults(header1 + header2)

   #------------------------------------------------------------------------------------------------------#
   def execState(self, oper, state, chkDepend=0):

      #  Import module
      if StateTable[oper][state][MODULE]:
         cmd = 'import %s' % StateTable[oper][state][MODULE]; exec(cmd)

      TraceMessage( '--- StateMachine Running Oper - %s --- Switching to State - %s ---' % (oper, state) )
      # instantiate/execute the Class Object
      self.dut.currentState = state

      # Determine state sequence per operation
      # Only update actual running state, not dependant check.
      if not chkDepend:
         appendState(oper, state)

      self.dut.stateDBLogInfo.setdefault(self.dut.currentState,[])
      scriptModule      = StateTable[oper][state][MODULE]
      classMethod       = StateTable[oper][state][METHOD]
      stateTransitions  = evalPhaseOut(StateTable[oper][state][TRANS])

      stateTransitions['rerunState'] = state

      if StateParams[oper].has_key(state):
         inputParameters = evalPhaseOut(StateParams[oper][state])
      else:
         inputParameters = {} # default to empty dict

      if chkDepend:
         cmd = '%s.%s(self.dut, %s).dependencies(oper, state)' % (scriptModule, classMethod, inputParameters)
      else:
         cmd = '%s.%s(self.dut, %s).runState(oper, state)' % (scriptModule, classMethod, inputParameters)

      TraceMessage( cmd )
      #Disable cell if we need gantry insertion protection
      StateNames = getattr(TP,'Gantry_Ins_Prot_StateNames',[])
      CellDisabled = 0
      if testSwitch.GANTRY_INSERTION_PROTECTION and state in StateNames and self.dut.stateRerun.get('FAIL_STATE') == state:
         objMsg.printMsg("Disabling adjacent cell for %s." %state)
         RequestService('DisableCell')
         CellDisabled = 1
      try:
         exec( cmd )
      finally:
         # Reenable cell unless disable immed is on
         if ConfigVars[CN].get('DISABLE_IMMEDIATE',0) == 0 and CellDisabled:
            objMsg.printMsg("Enabling adjacent cell after %s." %state)
            RequestService('EnableCell')

      if testSwitch.FE_0143655_345172_P_SPECIAL_SBR_ENABLE and self.dut.stateTransitionEvent != 'pass':
         if not self.dut.spSBG.spSBGAutoRerun:
            objMsg.printMsg("Special SBR Condition 3 -Disable Auto-Rerun")
            if self.dut.stateTransitionEvent == 'depopRestart' and self.dut.spSBG.spSBGWaVBAR:
               objMsg.printMsg("Special SBR Condition 4 -Enable Waterfall from VBAR")
            else:
               objMsg.printMsg("Special SBR Condition 4 -Disable Waterfall from VBAR")
               objMsg.printMsg("Auto rerun state is disabled by SBR name(%s)" % str(self.dut.driveattr['SUB_BUILD_GROUP']))
               objMsg.printMsg("self.dut.stateTransitionEvent: '%s' changed to 'fail'" % str(self.dut.stateTransitionEvent))
               self.dut.stateTransitionEvent = 'fail'
         else:
            objMsg.printMsg("Special SBR Condition 3 -Enable Auto-Rerun and waterfall from VBAR")
            #if self.dut.stateTransitionEvent == 'depopRestart' and self.dut.spSBGWaVBAR:
            if self.dut.stateTransitionEvent in ['depopRestart','reRunVBAR'] and self.dut.spSBG.spSBGWaVBAR:
               objMsg.printMsg("Special SBR Condition 4 -Enable Waterfall from VBAR")
            else:
               objMsg.printMsg("Special SBR Condition 4 -Disable Waterfall from VBAR")
               objMsg.printMsg("Auto rerun state is disabled by SBR name(%s)" % str(self.dut.driveattr['SUB_BUILD_GROUP']))
               objMsg.printMsg("self.dut.stateTransitionEvent: '%s' changed to 'fail'" % str(self.dut.stateTransitionEvent))
               self.dut.stateTransitionEvent = 'fail'

      if self.dut.endState == state and self.dut.stateTransitionEvent == 'pass':
         self.dut.nextState = 'COMPLETE'

      # Handle state rerun
      elif (oper in self.dut.stateRerun) and (state in self.dut.stateRerun[oper]) and not self.dut.downgradeOTF:
         if not stateRerunComplete(oper, state):
            if testSwitch.FE_SGP_402984_ALLOW_MULTIPLE_FAIL_STATE_RETRIES:
               self.dut.stateTransitionEvent = 'fail'
            self.dut.nextState = rerunState(oper, self.dut.stateSequence, self.dut.stateRerun)
         elif not self.dut.stateTransitionEvent == 'restartAtState':
            self.dut.nextState = stateTransitions[self.dut.stateTransitionEvent]

      else:
         if not self.dut.stateTransitionEvent == 'restartAtState':
            #if 'restartAtState' then state set an out-of-sequence restart state
            if self.dut.stateTransitionEvent == 'fail' and state == 'FAIL_PROC' and testSwitch.FE_0129336_405392_NO_EXCEPTIONAL_PASS_FROM_FAIL_PROC:
               self.dut.nextState = 'FAIL'
            else:
               self.dut.nextState = stateTransitions[self.dut.stateTransitionEvent]


      self.dut.statesExec[self.dut.nextOper].append(self.dut.currentState)

      if testSwitch.FE_0134030_347506_SAVE_AND_RESTORE:
         self.dut.lastState = state

      UpdateStateRerunFlag(oper, state)
      self.dut.downgradeOTF = 0
      self.dut.lastState = state

   #------------------------------------------------------------------------------------------------------#
   def changeBG(self):
      if testSwitch.WA_0124296_340210_DOWNGRADE_TO_STD_ONLY:
         if 'STD' in self.dut.demand_table:
            self.dut.BG = 'STD'
            objMsg.printMsg("Business group changed to %s" % str(self.dut.BG))
            return

      if testSwitch.WA_0171451_407749_P_DOWNGRADE_TO_SBS_ONLY:
         if 'SBS' in self.dut.demand_table:
            self.dut.BG = 'SBS'
            objMsg.printMsg("Business group changed to %s" % str(self.dut.BG))
            return

      changeBGto = 'NONE'

      for demand in self.dut.demand_table:
         if changeBGto != 'NONE':
            break
         elif (demand != self.dut.BG) and (self.oGOTF.gotfTestGroup(demand)== True):
            if testSwitch.BF_0185687_007955_P_PREVENT_DOWNGRADE_TO_HIGHER_BG:
               if self.dut.demand_table.index(self.dut.BG) > self.dut.demand_table.index(demand):
                  continue
            changeBGto = demand
            if states_GOTF.has_key(demand):
               if self.dut.statesSkipped[self.dut.nextOper] != [] and states_GOTF[demand][self.dut.nextOper] == 'ALL':
                  changeBGto = 'NONE'
               else:
                  for skipped in self.dut.statesSkipped[self.dut.nextOper]:
                     if skipped in states_GOTF[demand][self.dut.nextOper]:
                        changeBGto = 'NONE'
                        break

      if testSwitch.FE_0143655_345172_P_SPECIAL_SBR_ENABLE:
         if self.dut.spSBG.spSBGGOTFPN:
            ScrCmds.statMsg("Special SBR Condition 5 -Enable downgrade to other tab.")
         else:
            ScrCmds.statMsg("Special SBR Condition 5 -Disable downgrade to other tab.")
         if changeBGto == 'NONE' or not self.dut.spSBG.spSBGGOTFPN:
            iCTQ = self.GetCTQ(tmpbg=self.dut.BG)
            ScrCmds.raiseException(14765 + iCTQ, 'Failed Grading at CTQ%s' % iCTQ)
      else:
         if changeBGto == 'NONE':
            iCTQ = self.GetCTQ(tmpbg=self.dut.BG)
            ScrCmds.raiseException(14765 + iCTQ, 'Failed Grading at CTQ%s' % iCTQ)

      self.dut.BG = changeBGto
      objMsg.printMsg("Business group changed to %s" % str(self.dut.BG))

   #------------------------------------------------------------------------------------------------------#
   def changePN(self):

      force_tierPN = 0
      if testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT and not CommitServices.isTierPN(self.dut.partNum) \
         and self.dut.driveattr['ORG_TIER'] != 'NONE' and ( self.dut.driveattr.get('COMMIT_DONE', "FAIL") == "PASS" or DriveAttributes.get('COMMIT_DONE', "FAIL") == 'PASS'):
         objMsg.printMsg("Tier Drive downgrading after commit...Decommitting PN: %s" %self.dut.partNum)
         try:
            CommitCls.CAutoCommit(self.dut, {'TYPE': 'DECOMMIT'}).run()
         except:
            objMsg.printMsg("Commit error!!\n%s" % (traceback.format_exc(),))
         force_tierPN = 1

      if CommitServices.isTierPN( self.dut.partNum ) and ( CommitServices.getTab( self.dut.partNum ) == TIER3 ):
         # Allow PN/BG to change from higher level to lower then ask FIS for 9D PN in new
         CommitCls.CAutoCommit(self.dut, {'TYPE': 'COMMIT', 'SEND_OPER': 0}).run()
         finalPN = CommitServices.setFN_PN(self.dut.partNum, self.dut.driveattr['ORG_TIER'])
         self.dut.driveattr['FN_PN'] = finalPN
         return

      # Search back BG -> PN
      if self.dut.BG in self.dut.manual_gotf:
         if testSwitch.FE_0245993_504374_P_MANUAL_COMMIT_DOWNGRADE_TO_TIER and testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT and self.dut.driveattr['ORG_TIER'] == 'NONE' or force_tierPN:
            tierDefaultPN = getattr(PIF, 'tierDefaultPN', {})
            newPartNum = self.dut.manual_gotf[self.dut.BG][self.dut.bgIndex]
            if len(newPartNum) == 4: #Safety Net if Manual_GOTF has both 9-digit and 3-digit PNs
               newPartNum = CommitServices.getSixDigTLA(self.dut.partNum, includeDash = False) + newPartNum
            if tierDefaultPN.has_key(newPartNum[0:3]): #Default to program's first 3-digit PN if applicable
               newPartNum = tierDefaultPN[newPartNum[0:3]] + newPartNum[-7:]               
         else:
            newPartNum = self.dut.manual_gotf[self.dut.BG][self.dut.bgIndex]
      else:
         ScrCmds.raiseException(11044, 'Business group %s not found in manual_gotf' %self.dut.BG)

      if len(newPartNum) != 10:    # safety net
         ScrCmds.raiseException(11044, 'Part Number in manual_gotf is invalid')

      objMsg.printMsg("Changing Part Number to %s" %newPartNum)

      self.dut.partNum = newPartNum
      self.dut.driveattr['BSNS_SEGMENT'] = self.dut.BG
      self.dut.driveattr['PART_NUM'] = self.dut.partNum
      #ScrCmds.HostSetPartnum(self.dut.partNum)

      if CommitServices.isTierPN( self.dut.partNum ) and not (self.dut.driveattr['ORG_TIER'] == 'NONE'):
         CommitCls.CAutoCommit(self.dut, {'TYPE': 'COMMIT', 'SEND_OPER': 0}).run()
      else:
         if testSwitch.FE_0190240_007955_USE_FILE_LIST_FUNCTIONS_FROM_DUT_OBJ:
            self.dut.buildFileList()                                 # Rebuild filelist after PN change to insure proper FW is downloaded

         from CustomCfg import CCustomCfg
         CCustomCfg().getDriveConfigAttributes(force = True)
      self.dut.PNChanged = 'DONE'

      #Reporting of FN_PN for Tier tab before commit and BG after commiting
      if testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT and not (self.dut.driveattr['ORG_TIER'] == 'NONE'):
         finalPN = CommitServices.setFN_PN(self.dut.partNum, self.dut.driveattr['ORG_TIER'])
         self.dut.driveattr['FN_PN'] = finalPN

      #Establish ORG_TIER at the very end of downgrade for manual commit to tier downgrade
      if testSwitch.FE_0245993_504374_P_MANUAL_COMMIT_DOWNGRADE_TO_TIER and self.dut.driveattr['ORG_TIER'] == 'NONE':
         self.dut.driveattr['ORG_TIER'] = CommitServices.getTab( self.dut.partNum )
         ScrCmds.statMsg("ORG_TIER = %s" % self.dut.driveattr['ORG_TIER'])

   #------------------------------------------------------------------------------------------------------#
   def failDrive(self,failtable,failcolumn,failcode,failcriteria_op,failcriteria_val,failed_meas_values,failcriteria_vio,failcriteria_filterDict):
      """ using gotf tools to fail drive for a test.
      for  Business_Group = ALL case. all parms defined in GOTF_table.xml """
      if testSwitch.auditTest and testSwitch.FE_0123777_399481_DO_NOT_FAIL_AUDIT_DRIVES_FOR_GOTF:
         objMsg.printMsg("the %s column in the %s table failed, because the measured value(s): %s , are not %s the limit of %s.\n the num_violations allowed = %s. the filter dictionary is: %s " %
                     (failcolumn,failtable,failed_meas_values,failcriteria_op,failcriteria_val,failcriteria_vio,failcriteria_filterDict))
      else:
         if testSwitch.FE_0141166_409401_P_REPORT_HEAD_WHEN_FAIL_P152_GOTF and failtable == 'P152_PEAK_SUMMARY':
             tbl = self.dut.dblData.Tables(failtable).tableDataObj()
             objMsg.printMsg("Report data when failed PEAK_FREQUENCY column in the P152_PEAK_SUMMARY table by GOTF Grading.")
             objMsg.printMsg("HD_PHYS_PSN\tPEAK_RANK\tHD_LGC_PSN\tPEAK_MAGNITUDE\tPEAK_FREQUENCY\tOCCURRENCE")
             for record in tbl:
                 objMsg.printMsg("\t%s\t\t%s\t\t%s\t\t%s\t\t%s\t\t%s"%(record['HD_PHYS_PSN'],record['PEAK_RANK'],record['HD_LGC_PSN'],record['PEAK_MAGNITUDE'],record['PEAK_FREQUENCY'],record['OCCURRENCE']))
         if testSwitch.FE_0156504_357260_P_RAISE_GOTF_FAILURE_THROUGH_FAIL_PROC:
            self.dut.stateTransitionEvent = 'fail'
            self.dut.failureData = ScrCmds.makeFailureData(failcode,"the %s column in the %s table failed, because the measured value(s): %s , are not %s the limit of %s.\n the num_violations allowed = %s. the filter dictionary is: %s " %(failcolumn,failtable,failed_meas_values,failcriteria_op,failcriteria_val,failcriteria_vio,failcriteria_filterDict))
         else:
            ScrCmds.raiseException(failcode,"the %s column in the %s table failed, because the measured value(s): %s , are not %s the limit of %s.\n the num_violations allowed = %s. the filter dictionary is: %s " %
                     (failcolumn,failtable,failed_meas_values,failcriteria_op,failcriteria_val,failcriteria_vio,failcriteria_filterDict))

   #------------------------------------------------------------------------------------------------------#
   def ChkCMT2TestDone(self, oper):

      if (self.dut.operList.index(oper) <= self.idxCMT2) or (testSwitch.virtualRun) or testSwitch.FE_0148305_231166_P_ALLOW_POST_CMT2_DOWNGRADE:
         objMsg.printMsg("CMT2_TEST_DONE = NONE. Drive can proceed with downgrade")
         return

      # FIN2 9D CC downgrade FIN2 -> re-CRT2
      if oper is 'FIN2' and testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT:
         self.changeBG()
         self.changePN()
         self.dut.nextOperOverride = 'CRT2'
         # append CRT2 in configvars RUN_OPER_ON_FAIL for FIN2-> re-CRT2 downgrade
         if not 'CRT2' in ConfigVars[CN].get('RUN_OPER_ON_FAIL',[]):
            ConfigVars[CN]['RUN_OPER_ON_FAIL'].append('CRT2')
      else:
         self.dut.nextOperOverride = 'CMT2'

      self.dut.driveattr['DRIVE_SCORE'] = self.oGOTF.gotfDriveScore(self.dut.BG)
      ScrCmds.raiseException(10468, "Post-CMT2 grading failure.")


###########################################################################################################
###########################################################################################################
class CBGPN:
   #------------------------------------------------------------------------------------------------------#
   def __init__(self, oGOTF):
      self.dut = objDut
      self.oGOTF = oGOTF

   #------------------------------------------------------------------------------------------------------#
   def InitACMT(self):
      '''
      Init auto commit
      '''

      # start AutoCommit
      # skip Web services if FNC2, CRT2 or CMT2 non-Fresh load
      if self.dut.nextOper == 'FNC2' or self.dut.nextOper == 'CRT2':
         self.dut.gotfBsnsList = self.dut.longattr_bg.split("/")
         objMsg.printMsg('Web services not required for FNC2 or CRT2')
         objMsg.printMsg('self.dut.gotfBsnsList=%s' % self.dut.gotfBsnsList)
         return

      if self.dut.nextOper == 'CMT2' and self.dut.scanTime == 0:
         self.dut.gotfBsnsList = self.dut.longattr_bg.split("/")
         objMsg.printMsg('Web services not required for CMT2 non-fresh load')
         objMsg.printMsg('self.dut.gotfBsnsList=%s' % self.dut.gotfBsnsList)
         return


      params = self.dut.partNum

      objMsg.printMsg('RequestService GetDriveConfigAttributes params: %s' % `params`)
      retries, retry_intv = ConfigVars[CN].get("CMT Retry Count", [4, 1])
      objMsg.printMsg('CMT Retry Count - Num=%s Delay=%s min' % (retries, retry_intv))

      if testSwitch.FE_0185033_231166_P_MODULARIZE_DCM_COMMIT:
         for i in xrange(retries):
            try:
               driveConfigAttrs = CommitServices.getDriveConfigAttributes(params)
               break
            except CRaiseException:
               objMsg.printMsg("Commit call failed: \n%s" % (traceback.format_exc(),))
               driveConfigAttrs = {}

            if driveConfigAttrs != {}:
               ScrCmds.raiseException(14761, "Custom Drive Attributes - DCM not supported in Host/FIS.")



         else:
            #raise the lower exception
            raise

         if testSwitch.virtualRun:
            if self.dut.longattr_bg == 'NONE':
               self.dut.longattr_bg = 'STD'
         bs = driveConfigAttrs.get('BSNS_SEGMENT', ('=',''))[1]

      else:
         for i in xrange(retries):
            if i > 0:
               objMsg.printMsg('Web Service failed. Retrying in %s mins' % retry_intv)
               time.sleep(retry_intv * 60)
            if ConfigVars[CN].get('DCC_PRE_RELEASE', 0):
               Reply = RequestService("DCMServerRequest",("GetLatest_DriveConfigAttributes",(params, )))[1]['DATA']
            else:
               Reply = RequestService("DCMServerRequest", ("GetDriveConfigAttributes", (params,)))[1]['DATA']
           
            if ConfigVars[CN]['BenchTop'] or testSwitch.virtualRun:   # for benchtop testing only!!!
               objMsg.printMsg('BenchTop Reply=%s' % `Reply`)
               #Reply = ('GetDriveConfigAttributes', ['THRUPUT_GROUP:=:DISTY', 'THRUPUT_GROUP:=:OEM1', 'THRUPUT_GROUP:=:OEM2', 'BSNS_SEGMENT:=:OEM2', 'SERVER_ERROR=NO ERROR'])
               Reply = ['THRUPUT_GROUP:=:DISTY', 'THRUPUT_GROUP:=:STD', 'BSNS_SEGMENT:=:STD', 'SERVER_ERROR=NO ERROR']
               if self.dut.longattr_bg == 'NONE':
                  self.dut.longattr_bg = 'STD'

            objMsg.printMsg('RequestService GetDriveConfigAttributes reply: %s' % `Reply`)
            if str(Reply).find("NO ERROR") > -1:
               break

         #Reply = Reply[1]     # get the list item, eg: ['THRUPUT_GROUP:=:DISTY', 'THRUPUT_GROUP:=:OEM1', 'THRUPUT_GROUP:=:OEM2', 'BSNS_SEGMENT:=:OEM2', 'SERVER_ERROR=NO ERROR']

         bs = ''
         for i in Reply:
            Values = i.split(':=:')
            if Values[0] == 'BSNS_SEGMENT':
               bs = Values[1]
               break

      if bs == '':
         msg = "GetBGPN: raise exception. Cannot find BSNS_SEGMENT"
         ScrCmds.raiseException(13425, msg)

      if self.dut.nextOper == 'PRE2':  # pre2 only skip check; all other operations must check
         self.dut.gotfBsnsList = self.oGOTF.gotfGroupList
         self.dut.longattr_bg = str.join("/", self.oGOTF.gotfGroupList)    # must convert list to string
         objMsg.printMsg('PRE2 - reset longattr_bg=%s gotfGroupList=%s ' % (self.dut.longattr_bg, self.oGOTF.gotfGroupList))
      else:
         objMsg.printMsg('Non PRE2 - Use longattr_bg=%s ' % (self.dut.longattr_bg))
         self.dut.gotfBsnsList = self.dut.longattr_bg.split("/")  # convert back from string to list

         if not bs in self.dut.gotfBsnsList:
            msg = "GetBGPN: raise exception. Web services BG not found in valid list"
            ScrCmds.raiseException(13425, msg)

      self.dut.BG = bs
      self.dut.driveattr['BSNS_SEGMENT'] = bs
      objMsg.printMsg('Found BSNS_SEGMENT: %s BusinessGroupList=%s' % (bs, `self.dut.gotfBsnsList`))
      self.dut.demand_table = []     # reset so that no downgrade will be performed

      return   # end AutoCommit

   #------------------------------------------------------------------------------------------------------#
   def GetBGPN(self, reset_Manual_GOTF = 0):
      '''
      Get business group/part number
      '''
      if reset_Manual_GOTF:
         objMsg.printMsg("**** Reset Manual_GOTF ****")
         from PIF import DemandTable
         import Utility
         oUtil = Utility.CUtility()
         self.dut.demand_table = oUtil.copy(DemandTable)
      self.dut.bgIndex = -1
      self.dut.manual_gotf = {}

      self.dut.gotfBsnsList = []
      objLongAttr = CLongAttr()

      self.dut.longattr_bg = objLongAttr.DecodeAttr(DriveAttributes)
      objMsg.printMsg('Decoded longattr_bg=%s' % self.dut.longattr_bg)

      if self.dut.longattr_bg == "":
         self.dut.longattr_bg = "NONE"


      if testSwitch.AutoCommit and not testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT:
         self.InitACMT()  # Init auto commit
      elif len(Manual_GOTF) == 0:
         # GOTF based on DemandTable in PIF.py only. Create manual_gotf with all the same PN

         for dem in self.dut.demand_table:
            self.dut.manual_gotf[dem] = self.dut.partNum

         objMsg.printMsg("Created manual_gotf=%s" % self.dut.manual_gotf)
      else:
         # GOTF based on both Manual_GOTF and DemandTable in PIF.py

         # convert 2 dim dictionary to 1 dim
         for dem in self.dut.demand_table:
            mg_list = []
            for base in Manual_GOTF.keys():
               for cust in Manual_GOTF[base].keys():
                  if cust == dem:
                     mg_list = mg_list + Manual_GOTF[base][cust]

            if len(mg_list) > 0:
               self.dut.manual_gotf[dem] = mg_list


         foundPN = 0
         for dem,pnList in self.dut.manual_gotf.items():
            if self.dut.partNum in pnList:
               foundPN = 1

         if foundPN == 0:
            for dem,pnList in self.dut.manual_gotf.items():
               for idx, pn in enumerate(pnList):
                  import re
                  if len(pn) == 4 and re.compile("\-\w{3}").match(pn):
                     pnc = self.dut.partNum[0:6]+pn
                     pnList[idx] = pnc


         objMsg.printMsg("GetBGPN: Combined manual_gotf table: %s" % str(self.dut.manual_gotf))
         #for dem in self.dut.manual_gotf.keys():
         #   objMsg.printMsg("%s %s" % (dem, self.dut.manual_gotf[dem]))

         # check manual DCC, if found, assign new BG
         for dem in self.dut.demand_table:
            try:
               self.dut.bgIndex = self.dut.manual_gotf[dem].index(self.dut.partNum)
               self.dut.BG = dem
               self.dut.driveattr['BSNS_SEGMENT'] = dem
               break
            except:
               self.dut.bgIndex = -1
               #objMsg.printMsg("GetBGPN: Cannot find bg=%s" % (dem))
               pass

         if self.dut.bgIndex == -1:
            msg = "GetBGPN: raise exception. Part number %s not found in Manual_GOTF" % self.dut.partNum
            ScrCmds.raiseException(11044, msg)

         # get rid of bg without valid pn to downgrade to
         for demand in self.dut.demand_table[:]:
            try:
               pn = self.dut.manual_gotf[demand][self.dut.bgIndex]
               if len(pn) != 10:
                  #objMsg.printMsg("GetBGPN: Invalid PN detected: %s" % pn)
                  ScrCmds.raiseException(11044, 'Part Number in manual_gotf is invalid')
            except:
               objMsg.printMsg("GetBGPN: Invalid BG removed: %s" % demand)
               self.dut.demand_table.remove(demand)

         objMsg.printMsg("GetBGPN: Found PN=%s BG=%s. Final DemandTable: %s" % (self.dut.partNum, self.dut.BG, str(self.dut.demand_table)))
         for demand in self.dut.demand_table:
            pn = self.dut.manual_gotf[demand][self.dut.bgIndex]
            objMsg.printMsg("   BG=%s PN=%s" % (demand, pn))

         if self.dut.OldBG != "NONE" and self.ChkReconfig() == False:
            ScrCmds.raiseException(11044, 'Reconfig is not allowed')

         if testSwitch.FE_0197001_409401_P_CHK_BG_FOR_PROTECTION_RE_CONFIG:
            self.dut.checkBGforReFIN2()

         self.dut.setDriveCapacity()
         ScrCmds.statMsg('self.CAPACITY=%s' % self.dut.CAPACITY_PN)
         ScrCmds.statMsg('self.CAPACITY_CUS=%s' % self.dut.CAPACITY_CUS)

   #------------------------------------------------------------------------------------------------------#
   def ChkReconfig(self):
      '''
      returns True is reconfig is allowed; False otherwise
      ReConfigTable = ['CTUB','OEM1B','CTUB','OEM1A','OEM1D','OEM1E','OEM1D','CTUD','OEM1C','STD']
      a) general rule - allow left to right reconfig. That means CTUB can be reconfig to any OEM. STD can be reconfig to only STD
      b) but duplicate values are allowed, eg OEM1D. So, OEM1D can reconfig to OEM1E as well as OEM1E can reconfig to OEM1D
      '''
      objMsg.printMsg("Checking if reconfig is allowed. Old BG=%s New BG=%s" % (self.dut.OldBG, self.dut.BG))
      
      if testSwitch.RECONFIG_CHECK_BASED_ON_BSNS_SEGMENT:
         # Allow reconfig if newBG is inside BSNS_SEGMENT (BSNS_SEGMENT2, BSNS_SEGMENT3) or newBG is equal to BSNS_SEGMENT.
         longattr_bg = CLongAttr().DecodeAttr(DriveAttributes)
         gotfBsnsList = longattr_bg.split("/")
         if (self.dut.BG in gotfBsnsList) or (self.dut.BG == DriveAttributes.get('BSNS_SEGMENT', "NONE")): 
            return True
         
         return False

      else:
         try:
            from PIF import ReConfigTable
         except ImportError:
            objMsg.printMsg("Warning: Checking for reconfigure Business Group is DISABLED!")
            return True       # table not found - ignore checks
         try:
            OldBGIdx = ReConfigTable.index(self.dut.OldBG)                             # find first occurrence
            NewBGIdx = len(ReConfigTable) - 1 - ReConfigTable[::-1].index(self.dut.BG) # find last occurrence
            return NewBGIdx >= OldBGIdx
         except:
            return False      # OEM not found, disallow reconfig


###########################################################################################################
###########################################################################################################
class CLongAttr:
   '''
   Go get around 32 char limitation of fis attributes by using multiple attributes
   '''
   def __init__(self):
      self.dict = {}
      self.iLenLimit = 30
      self.attr_list = ['BSNS_SEGMENT2', 'BSNS_SEGMENT3', ]
      for i in self.attr_list:
         self.dict[i] = "NONE"

   def EncodeAttr(self, longattr):
      '''
      encode a single long attr to multiple attr
      '''
      iIndex = 0
      for i in xrange(0, len(longattr), self.iLenLimit):
         tmpstr = longattr[i : self.iLenLimit + i]
         try:
            self.dict[self.attr_list[iIndex]] = tmpstr
            iIndex = iIndex + 1
         except:
            msg = "Fail to encode attr %s" % tmpstr
            ScrCmds.raiseException(11044, msg)

      return self.dict

   def DecodeAttr(self, dict):
      '''
      decode multiple attr a single long attr
      '''
      longattr = ""

      for i in self.attr_list:
         if i in dict:
            if dict[i] != "NONE":
               longattr = longattr + dict[i]

      return longattr

#---------------------------------------------- E N D ----------------------------------------------------#
