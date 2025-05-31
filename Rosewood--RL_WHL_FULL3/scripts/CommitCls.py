#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Auto Commit services, parts borrowed from ST10 code
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/CommitCls.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/CommitCls.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#

from Constants import *
import MessageHandler as objMsg
from State import CState
import ScrCmds
import time
import CommitServices
from Drive import objDut
from TestParamExtractor import TP
import os,types

COMMIT   = 0
DECOMMIT = 1
INVALID  = 2
FIS_REQ_PASS = 'PASS'
FIS_REQ_FAIL = 'FAIL'
FIS_REQ_NO_DEMAND = 23619

if testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT:
   MustHaveLst = [   'CC_FISC_YEAR',
                     'CC_FISC_WEEK',
                     'CC_PART_NUM',
                     'CC_DCC_DA',
                     'CC_DCC_REV',
                     'CC_BUILD_TYPE',
                     'CC_SBUILD_TYPE',
                  ]
else:
   MustHaveLst  = ['CUST_SCORE']        # Attribute that must be returned by Commit call

if testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT:
   Value        = {COMMIT:'AutoConfig',DECOMMIT:'DeCommit',INVALID:'Invalid or Unknown'}
else:
   Value        = {COMMIT:'AutoCommit',DECOMMIT:'DeCommit',INVALID:'Invalid or Unknown'}



class CReconfigAllow(CState):
   '''
   Identify and change flow for reconfig
   '''
   def __init__(self, dut, params = None):
      self.params = {}
      depList = []
      if params != None:
         self.params = params

      CState.__init__(self, dut, depList)

   def run(self):
      if self.dut.reconfigOper:
         self.dut.stateTransitionEvent = 'reconfig'


class CAutoCommitTier_Fail(CState):
   '''
   Fail during a high tier evaluation
   '''
   def __init__(self, dut, params={}):
      self.dut = dut
      self.params = params
      depList = []
      self.AttrLst = []
      CState.__init__(self, dut, depList)

   def run(self):
      from PIF import Manual_GOTF
      from CustomCfg import CCustomCfg
      CustConfig = CCustomCfg()

      if ( CommitServices.getTab( self.dut.partNum ) == TIER1 ):    #Change PN and BG of T01 Drive to T02 at the end of CRT2 if failed screens

         if self.dut.CustomCfgTestFailure != False:
            self.dut.driveattr['WTF_CTRL'] = ('%s_%s_%s'%(self.dut.nextOper, self.dut.partNum[-3:], CustConfig.screenCode(self.dut.CustomCfgTestFailure)))

         #self.dut.BG = CommitServices.getBusinessGroup(TIER2, Manual_GOTF['Base'])    # using LCO PIF Manual_GOTF structure
         self.dut.BG = CommitServices.getBusinessGroup(TIER2, objDut.manual_gotf)      # using ScPk PIF Manual_GOTF structure

         if self.dut.BG in self.dut.manual_gotf:
            newPartNum = self.dut.manual_gotf[self.dut.BG][self.dut.bgIndex]
         else:
            objMsg.printMsg("Business group %s not found in manual_gotf" %self.dut.BG)
            return

         if len(newPartNum) != 10:    # safety net
            objMsg.printMsg("RECONF_BG_IS_NOT_ALLOWED")
            return

         objMsg.printMsg("Changing Part Number to %s" %newPartNum)

         self.dut.partNum = newPartNum
         self.dut.driveattr['BSNS_SEGMENT'] = self.dut.BG
         self.dut.driveattr['PART_NUM'] = self.dut.partNum

         if testSwitch.BF_0196490_231166_P_FIX_TIER_SU_CUST_TEST_CUST_SCREEN:
            ScrCmds.raiseException(13425, "Unable to commit to any Tier")


class CAutoCommit(CState):
   '''
   Auto Commit services, parts borrowed from ST10 code
   '''
   def __init__(self, dut, params={}):
      self.dut = dut
      self.params = params
      depList = []
      self.AttrLst = []
      self.oldOper = self.dut.nextOper
      CState.__init__(self, dut, depList)


   #-------------------------------------------------------------------------------------------------------
   def stateEntryEventHandler(self, event):
      """
      Handles if the input state transition was a previous fail event
      """
      objMsg.printMsg("entryeventHandler... %s" % event)
      ec = 0
      try:
         ec = self.dut.failureData[0][2]
      except:
         # quite a few exceptions that can happen as failureData doesn't always present a consistent API outside of Setup:failure handling
         pass

      if testSwitch.BF_0196490_231166_P_FIX_TIER_SU_CUST_TEST_CUST_SCREEN:
         objMsg.printMsg("Error Code detected: %s" % (ec, ))
         if event == 'fail':
            self.AllowTierTransitionDueToFail = True
         else:
            self.AllowTierTransitionDueToFail = False
      else:
         if event == 'fail' and ec not in [11044,]:
            self.AllowTierTransitionDueToFail = True
         else:
            self.AllowTierTransitionDueToFail = False


   #-------------------------------------------------------------------------------------------------------
   def run(self):
      """
      Runs the state default transition method.
      Default: COMMITs drive to new PN and udpates FW in process
      Params:
         name ::     valid values   :: default
         TYPE :: [COMMIT, DECOMMIT] :: COMMIT
         UPDATE_FW :: True,False    :: True
         SEND_OPER ::     0,1       ::   1
      """
      try:
         TYPE = eval('%s' % self.params.get('TYPE', 'COMMIT'))
      except:
         TYPE = INVALID

      if TYPE == COMMIT:
         self.commit()
      elif TYPE == DECOMMIT:
         self.decommit()
      else:
         objMsg.printMsg('Error The Commit Type call is %s' % Value[TYPE])
         ScrCmds.raiseException(11900, 'Error The Commit Type call is %s' % Value[TYPE])

      if self.params.get('UPDATE_FW', True):
         objMsg.printMsg("Updating FW process uses for DUT.")
         self.dut.buildFileList()

      if testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT and self.dut.currentState == 'COMMIT':
         finalPN = CommitServices.setFN_PN(self.dut.partNum, self.dut.driveattr['ORG_TIER'])
         self.dut.driveattr['FN_PN'] = finalPN

   def sendCMT2StartEvent(self):
      self.oldOper = self.dut.nextOper

      newOper = "CMT2"
      ReportErrorCode(0)
      ScrCmds.statMsg('='*64)

      ReportStatus('%s --- %s --- %s' % (newOper, 'COMMIT', 0)) # display fail state on GUI cell status window

      #oper fixup
      RequestService('SetOperation',(newOper,))
      self.dut.nextOper = newOper
      self.dut.statesExec[self.dut.nextOper] = []
      self.dut.statesSkipped[self.dut.nextOper] = []



      RequestService("SendStartEvent", 0)

   #-------------------------------------------------------------------------------------------------------
   def sendCMT2PassEvent(self):
      #Prep the error info for fis upload
      #from Setup import CSetup

      #mySetup = CSetup()

      #not needed for cmt2
      #Prep the parametric data for FIS upload
      #mySetup.writeParametricData()

      #need to update attributes to FIS
      self.dut.updateFISAttr()

      #Send the data under the *Oper run
      RequestService("SendParametrics", (1,))  # Send parametric data for all failures

      #Send attributes and parametrics
      RequestService('SendRun', 1)

      #Reset to the primary operation
      RequestService('SetOperation',(self.oldOper,))
      self.dut.nextOper = self.oldOper

   #-------------------------------------------------------------------------------------------------------
   def commit(self):

      if testSwitch.AutoCommit == 0:
         objMsg.printMsg('Manual commit: assign COMMIT_DONE=PASS')
         self.dut.driveattr['COMMIT_DONE'] = "PASS"
         return

      if testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT:

         tierList = [TIER1, TIER2, TIER3]
         #tierPN, originalTier = CommitServices.convertPNtoTier(self.dut.partNum)

         if not testSwitch.FE_0220066_395340_P_AUTO_RE_DL_GTGA_FOR_ALL_DOWNGRADE and ( CommitServices.isTierPN(self.dut.partNum)
         and (self.dut.nextOper == 'CRT2')
         and (self.dut.sptActive.getMode() != self.dut.sptActive.availModes.mctBase) ):    #if tiered drive, and in CRT2, and has F3 code
            ScrCmds.raiseException(14733, "Pre-CMT2 grading failure, Post-Attribute Setting - Cannot change Business group") #Fail drive for GOTF spec fail after setting drive attributes for Tier Tab

         else:
            #modify oper and fis event to CMT2
            if self.params.get('SEND_OPER', 1) and testSwitch.FE_0198600_231166_P_SEND_CMT2_INLINE_EVENT:
               self.sendCMT2StartEvent()

            sixDigPN = CommitServices.getSixDigTLA(self.dut.partNum)
            tierPN = self.dut.partNum
            tier = CommitServices.getTab(self.dut.partNum)
            try:
               from PIF import Manual_GOTF
            except:
               Manual_GOTF = { 'Base' : {} }

            if getattr(self, 'AllowTierTransitionDueToFail', False):
               objMsg.printMsg("Found failing transition: WTF to next TIER")
               tierPN = self.dut.partNum
               tier = CommitServices.getNextTier(tierPN)

            #Start at the current tier point
            while tier != None:
               tierPN = sixDigPN + tier

               #modify business segment always to align them in the loop.
               #bg = CommitServices.getBusinessGroup(tier, Manual_GOTF['Base'])     # LCO method
               bg = CommitServices.getBusinessGroup(tier, objDut.manual_gotf)     # ScPk method
               if bg != None and not ( CommitServices.getTab( self.dut.partNum ) == TIER3 ):
                  self.dut.driveattr['BSNS_SEGMENT'] = bg

               self.collectCommitAttr(tierPN)
               res, lst = self.CommitCall(COMMIT)
               objMsg.printMsg('COMMIT: %s-%s' % (res, `lst`))
               failCode = int(lst.get('FAILCODE', 0))
               if res == OK and lst['RESULT'] == FIS_REQ_PASS:
                  break # Found good 9 digit CC
               elif lst['RESULT'] == FIS_REQ_FAIL and failCode == FIS_REQ_NO_DEMAND:
                  if tier in ConfigVars[CN].get('TIER_OK_WTF', []):
                     objMsg.printMsg("No demand for %s but TIER_OK_WTF allows WTF for %s" % (tier, tier))
                  else:
                     self.dut.driveattr['COMMIT_DONE'] = "FAIL"
                     ScrCmds.raiseException(failCode, "Unable to commit to any Tier")

               elif lst['RESULT'] != FIS_REQ_PASS:
                  if failCode == 23558 and self.dut.nextOper != 'CMT2':    # Report original Gradebit EC if there is no demand for downgrading Tier/PN from ACMS
                     iCTQ = self.GetCTQ(tmpbg=self.dut.demand_table[self.dut.demand_table.index(self.dut.BG)-1])
                     ScrCmds.raiseException(14765 + iCTQ, 'Failed Grading at CTQ%s' % iCTQ)
                  else:
                     ScrCmds.raiseException(failCode, "Unhandled ACMS error returned %s" % ( failCode, ) )

               tier = CommitServices.getNextTier(tierPN)

            else:
               self.dut.driveattr['COMMIT_DONE'] = "FAIL"
               ScrCmds.raiseException(11900, "Unable to commit to any Tier")

      else:
         self.collectCommitAttr()
         res, lst = self.CommitCall(COMMIT)
         objMsg.printMsg('COMMIT: %s-%s' % (res, `lst`))

      self.updateCommitDriveAttr(res, lst)

      if self.params.get('SEND_OPER', 1) and testSwitch.FE_0198600_231166_P_SEND_CMT2_INLINE_EVENT:
         self.sendCMT2PassEvent()

   #-----------------------------------------#
   def collectCommitAttr(self, tierPN = None):
      # 23617:No Demand for Part Number 9EV132-998. Check with Production Control
      if tierPN != None:
         self.addAttrToList('PART_NUM', tierPN)
      else:
         self.addAttrToList('PART_NUM', self.dut.driveattr['PART_NUM'])
      self.addAttrToList('SERIAL_NUM', self.dut.serialnum)

      try:
         self.addAttrToList('PCBA_PART_NUM', DriveAttributes['PCBA_PART_NUM'])
      except:
         if ConfigVars[CN]['BenchTop'] or testSwitch.virtualRun:
            self.addAttrToList('PCBA_PART_NUM', '100494143')
         else:
            raise

      try:
         self.addAttrToList('HDA_CODE', DriveAttributes['HDA_CODE'])
      except:
         if ConfigVars[CN]['BenchTop'] or testSwitch.virtualRun:
            self.addAttrToList('HDA_CODE', '100463892')
         else:
            raise

      if ConfigVars[CN].get('ACMT_TEST_SERVER', 0) == 1:
         objMsg.printMsg('ACMT_TEST_SERVER detected. Setting PROC_CTRL1=DEVP')
         self.addAttrToList('PROC_CTRL1', 'DEVP')  # this is for SK Yee FIS bench testing only

      
      try:
         from PIF import FORCE_ACMT_BS
      except:
         objMsg.printMsg('FORCE_ACMT_BS not found in PIF')
         FORCE_ACMT_BS = {}

      # check syntax - Python syntax error or wrong entry - fail drive
      for i in FORCE_ACMT_BS:
         if type(FORCE_ACMT_BS[i][0]) != types.IntType:
            ScrCmds.raiseException(11900, "FORCE_ACMT_BS IntType syntax error")

         if FORCE_ACMT_BS[i][1] != 'OFF' and FORCE_ACMT_BS[i][1] != 'ON':
            ScrCmds.raiseException(11900, "FORCE_ACMT_BS OFF/ON syntax error")

      bg = self.dut.driveattr.get('BSNS_SEGMENT', DriveAttributes['BSNS_SEGMENT'])
      if FORCE_ACMT_BS.has_key(bg):
         if FORCE_ACMT_BS[bg][1] == 'ON':
            objMsg.printMsg('FORCE_ACMT_BS BG=%s forced ON' % bg)
            self.addAttrToList('BSNS_SEGMENT', bg) # entry found but forced 'ON'
         else:
            newlst = []
            bgrank = FORCE_ACMT_BS[bg][0]
            objMsg.printMsg('FORCE_ACMT_BS current BG=%s rank=%s' % (bg, bgrank))

            for i in self.dut.gotfBsnsList:
               if not FORCE_ACMT_BS.has_key(i):
                  objMsg.printMsg('FORCE_ACMT_BS BGitem=%s not found' % (i))
                  continue

               objMsg.printMsg('FORCE_ACMT_BS checking BGitem=%s BGRank=%s Result=%s' % (i, FORCE_ACMT_BS[i][0], bool(FORCE_ACMT_BS[i][0] <= bgrank)))
               if FORCE_ACMT_BS[i][0] <= bgrank:
                  newlst.append(i)
            
            objMsg.printMsg('FORCE_ACMT_BS BG=%s Final BG List=%s' % (bg, newlst))
            if len(newlst) == 0:
               ScrCmds.raiseException(11900, "FORCE_ACMT_BS BG List Empty")

            self.addAttrToList('BSNS_SEGMENT', str.join(',', newlst))
      else:
         objMsg.printMsg('FORCE_ACMT_BS BG=%s key not found' % bg)
         if testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT:
            if ( CommitServices.getTab(self.dut.partNum) in [TIER3,] ):
                  #If T03 drive has not downgraded in any other operation, it is capable of committing to standard or SBS.
                  #Allow ACMS to commit dut to either. Else drive is downgrading, therefore, commit to SBS
               if bg in ['STD'] and (self.dut.currentState == 'COMMIT' or self.dut.driveattr['ORG_TIER'] in [TIER1, TIER2]):
                  bg = 'STD,SBS'

         self.addAttrToList('BSNS_SEGMENT', bg) # no key entry found
    
   #-----------------------------------------#
   def updateCommitDriveAttr(self, res, lst):

      if testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT:
         criticalKey = 'PART_NUM'
         if lst.has_key(criticalKey):
            if CommitServices.isTierPN(self.dut.partNum) and self.dut.nextState == 'COMMIT':
               #we are now reconfiguring to new PN
               self.dut.reconfigOper = 1

            self.dut.partNum = lst["PART_NUM"]
            RequestService("SetPartnum", self.dut.partNum)
            #Update the gemini settings for conformity in calling the dcm
            self.dut.driveattr['PART_NUM'] = lst["PART_NUM"]
            DriveAttributes['PART_NUM'] = self.dut.partNum

            self.dut.driveConfigAttrs = CommitServices.getDriveConfigAttributes(self.dut.partNum)


            if 'MODEL_NUM' in lst:
               self.dut.modelnum = lst["MODEL_NUM"]
            self.dut.BG = self.dut.driveConfigAttrs["BSNS_SEGMENT"][1]

            objMsg.printMsg('Found PART_NUM: %s, MODEL_NUM: %s, BSNS_SEGMENT: %s' % (self.dut.partNum, self.dut.modelnum, self.dut.BG))


            if len(self.dut.partNum) != 10:
               ScrCmds.raiseException(11900, "Length of PART_NUM from FIS AutoCommit reply is not 10 (%s)" % (self.dut.partNum,))

            #Required attributes by autoconfig
            for attr in MustHaveLst:
               self.dut.driveattr[attr] = lst[attr]

            self.dut.driveattr['MODEL_NUM'] = self.dut.modelnum
            self.dut.driveattr['BSNS_SEGMENT'] = self.dut.BG

            self.dut.driveattr['COMMIT_DONE'] = "PASS"
         else:
            self.dut.driveattr['COMMIT_DONE'] = "FAIL"
            ScrCmds.raiseException(11900, "FIS AutoCommit reply error missing critical attribute: %s" % criticalKey)

      else:
         if lst.has_key("BSNS_SEGMENT"):
            self.dut.BG = lst["BSNS_SEGMENT"]
            self.dut.driveattr['BSNS_SEGMENT'] = lst["BSNS_SEGMENT"]
            objMsg.printMsg('Found BSNS_SEGMENT: %s' % lst["BSNS_SEGMENT"])

            if lst.has_key("PART_NUM"):
               if len(lst["PART_NUM"]) != 10:
                  ScrCmds.raiseException(11900, "Length of PART_NUM from FIS AutoCommit reply is not 10")

               self.dut.partNum = lst["PART_NUM"]
               self.dut.driveattr['PART_NUM'] = lst["PART_NUM"]
               self.dut.modelnum = lst["MODEL_NUM"]
               self.dut.driveattr['MODEL_NUM'] = lst["MODEL_NUM"]
               DriveAttributes['PART_NUM'] = self.dut.partNum
               objMsg.printMsg('Found PART_NUM: %s MODEL_NUM: %s' % (lst["PART_NUM"], lst["MODEL_NUM"]))

               self.dut.driveattr['CC_PART_NUM']  = lst["CC_PART_NUM"]
               self.dut.driveattr['CC_DCC_REV']   = lst["CC_DCC_REV"]
               self.dut.driveattr['CC_DCC_DA']    = lst["CC_DCC_DA"]
               self.dut.driveattr['CC_FISC_YEAR'] = lst["CC_FISC_YEAR"]
               self.dut.driveattr['CC_FISC_WEEK'] = lst["CC_FISC_WEEK"]

            self.dut.driveattr['COMMIT_DONE'] = "PASS"
         else:
            self.dut.driveattr['COMMIT_DONE'] = "FAIL"
            ScrCmds.raiseException(11900, "FIS AutoCommit reply error")

   #-----------------------------------------#
   def CommitCall(self,TYPE=INVALID):
      paramsAttrLst = self.params.get('ATTR_LST', [])
      if len(paramsAttrLst) == 0:
         paramsAttrLst = self.AttrLst
      lst,result = [],1

      retries, retry_intv = ConfigVars[CN].get("CMT Retry Count", [4, 1])
      objMsg.printMsg('CMT Retry Count - Num=%s Delay=%s min' % (retries, retry_intv))

      for retry in xrange(retries):
         objMsg.printMsg('Calling RequestService Value: %s TYPE=%s params=%s' % (`Value`, TYPE, `paramsAttrLst`))
         if not testSwitch.virtualRun:
            try:
               data = RequestService(Value[TYPE],paramsAttrLst)
            except:  # allow ACMS server error retry
               data = (Value[TYPE], "ACMS server error.")
         else:
            if TYPE == COMMIT:
               if testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT:
                  #[ 'SERIAL_NUM=3SK10001', 'MODEL_NUM=ST92503010', 'INTERFACE=AS', 'CC_PART_NUM=%s' % self.dut.partNum,
                  #            'CC_DCC_DA=*', 'CC_DCC_REV=A', 'CC_BUILD_TYPE=*', 'CC_SBUILD_TYPE=*', 'CC_FISC_YEAR=2010',
                  #            'CC_FISC_WEEK=26', 'SERVER_ERROR=NO ERROR']
                  resplst = [
                             'RESULT=PASS',
                             'SERIAL_NUM=Z1D09XWZ',
                             'PART_NUM=9YN162-304',
                             'CC_PART_NUM=9YN162-304',
                             'CC_DCC_DA=*',
                             'CC_DCC_REV=B',
                             'CC_BUILD_TYPE=*',
                             'CC_SBUILD_TYPE=*',
                             'CC_FISC_YEAR=2012',
                             'CC_FISC_WEEK=50',
                             ]
                  resplst.append('PART_NUM=%s' % ( CommitServices.getSixDigTLA(self.dut.partNum) + '999' ))

                  if False:#True:#fail case
                     resplst.extend(['RESULT=%s' % FIS_REQ_FAIL,
                                   'FAILCODE=%s' % FIS_REQ_NO_DEMAND])
                  else:
                     resplst.extend(['RESULT=%s' % FIS_REQ_PASS,
                                 'FAILCODE=%s' % 0])


                  data = ('AutoConfig', resplst)
               else:
                  data = ('AutoCommit', ['RESULT=PASS', 'SERIAL_NUM=5YH00CGV', 'PART_NUM=9UB132-900', 'MODEL_NUM=ST92503010', 'INTERFACE=AS', 'CC_PART_NUM=9UB132-900', 'CC_DCC_DA=*', 'CC_DCC_REV=A', 'CC_BUILD_TYPE=*', 'CC_SBUILD_TYPE=*', 'CC_FISC_YEAR=2010', 'CC_FISC_WEEK=26', 'BSNS_SEGMENT=STD', 'SERVER_ERROR=NO ERROR'])
            elif TYPE == DECOMMIT:
               data = ('DeCommit', ['RESULT=PASS', 'SERIAL_NUM=5YH00CGV', 'CC_DECOMMIT_MSG=Decrement', 'CC_PART_NUM=9UB132-DCT', 'SERVER_ERROR=NO ERROR'])
            else:
               pass
         objMsg.printMsg('RequestService COMMIT reply: %s' % (data,))
         lst = data[1]

         if isinstance(lst,types.ListType) and 'RESULT=PASS' in lst:
            break

         objMsg.printMsg("Error %s return data = %s - is not list type or server 'RESULT=FAIL' error!" %(Value[TYPE],lst))
         # Try re-commit to the next lower tier
         ec = int(self.itranslateList(lst, TYPE, getErrCode=1).get('FAILCODE',0))
         if CommitServices.isTierPN(self.dut.partNum) and testSwitch.FE_DOWNGRADE_TO_LOWER_TIER_BASED_ON_ACMS_EC and (ec in getattr(TP, 'ACMSDowngradeErrorCodes', [23558, 23559,])):
            newTierPN, newBG = self.ACMSTierDowngrade(lst,TYPE,ec=ec)
                           
            if newTierPN != '' and newBG != '':
            # Refresh paramsAttrLst part num and business group for new ACMS commit
               new_params = {'PART_NUM':newTierPN, 'BSNS_SEGMENT':newBG}
               for idx, attr in enumerate(paramsAttrLst):
                  param = attr.split('=')[0]
                  if param in new_params:
                     paramsAttrLst[idx] =  param + '=' + new_params[param] 

         # Delay for another ACMS commit
         delay = retry_intv*60   #seconds
         if retry != retries-1:
            objMsg.printMsg('Wait for %s seconds, then retry.' % delay)
            time.sleep(delay)

      # for ACMS retry
      if testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT:
         self.returnLst = self.itranslateList(lst, TYPE)
      else:
         self.returnLst = self.itranslateList(lst)
      objMsg.printMsg('self.returnLst: %s' % (self.returnLst))
      result = OK

      return result,self.returnLst

   #-----------------------------------------#
   def ACMSTierDowngrade(self, lst,TYPE=INVALID, ec=0):
      """
      Tier part number downgrade based on ACMS error code
      """
      nextTierPN = ''
      newBG = ''
      nextTier = CommitServices.getNextTier(self.dut.partNum)
      if nextTier:
         #Establish ORG_TIER at the very end of downgrade for manual commit to tier downgrade
         if testSwitch.FE_0245993_504374_P_MANUAL_COMMIT_DOWNGRADE_TO_TIER and self.dut.driveattr['ORG_TIER'] == 'NONE':
            self.dut.driveattr['ORG_TIER'] = CommitServices.getTab( self.dut.partNum )
            ScrCmds.statMsg("ORG_TIER = %s" % self.dut.driveattr['ORG_TIER'])
         nextTierPN = self.dut.partNum[:7] + nextTier
         newBG = CommitServices.getBusinessGroup(nextTierPN, objDut.manual_gotf)

         objMsg.printMsg( "ACMS error code %s found in tier downgrade error code list. Changing tier part number from %s to %s." %(ec,self.dut.partNum,nextTierPN))
         self.dut.partNum = nextTierPN
         self.dut.driveattr['PART_NUM'] = nextTierPN

         #Reporting of FN_PN for Tier tab before commit and BG after commiting
         if testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT and not (self.dut.driveattr['ORG_TIER'] == 'NONE'):
            finalPN = CommitServices.setFN_PN(self.dut.partNum, self.dut.driveattr['ORG_TIER'])
            self.dut.driveattr['FN_PN'] = finalPN
   
      return nextTierPN, newBG
   #-----------------------------------------#
   def itranslateList(self,lst,TYPE=INVALID, getErrCode=0):
      dictLst = {}
      if len(lst):
         for item in lst:
           try:
              dictLst[item.split('=')[0]] = item.split('=')[1].split(':')[0]
           except:
              pass
      if getErrCode:                # Option to query for ACMS error code only
         return dictLst
      if TYPE == COMMIT:
         for must_have in MustHaveLst:
            if not dictLst.has_key(must_have):
               objMsg.printMsg('Error %s not found in return list' % must_have)
               dictLst['RESULT'] = FIS_REQ_FAIL
               break
      return dictLst
   #-----------------------------------------#
   def addAttrToList(self,attr,value):
      self.AttrLst.append('%s=%s'%(attr, value))
      objMsg.printMsg('Add %s=%s to Commit params List' % (attr, value))

      iLimit = 255
      if len(value) > iLimit:
         ScrCmds.raiseException(11900, "Value length cannot be greater than %s" % iLimit)
      return
   #-----------------------------------------#
   def decommit(self):
      if (DriveAttributes.get('CC_PART_NUM', 'NONE')  == 'NONE'): return

      self.collectDecommitAttr()
      res, lst = self.CommitCall(DECOMMIT)
      objMsg.printMsg('DECOMMIT: %s-%s' % (res, `lst`))
      if testSwitch.virtualRun:
         lst = {'RESULT':'PASS', 'SERIAL_NUM':'3WV0064J',
                'CC_ERR_MSG':'No Decrement : Drive already decommitted',
                'CC_PART_NUM':'9RN132-DCT', 'SERVER_ERROR':'NO ERROR'}
      self.updateDecommitDriveAttr(res, lst)
   #-----------------------------------------#
   def collectDecommitAttr(self):
      self.addAttrToList('SERIAL_NUM',    self.dut.serialnum)
      try:
         self.addAttrToList('PART_NUM',      self.dut.driveattr['PART_NUM'])
      except:
         self.addAttrToList('PART_NUM',      DriveAttributes.get('PART_NUM', 'NONE'))

      if testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT:
         for attr in MustHaveLst:
            self.addAttrToList( attr, self.dut.driveattr.get(attr, DriveAttributes.get( attr, 'NONE' ) ) )
      else:
         self.addAttrToList('CC_PART_NUM',   DriveAttributes.get('CC_PART_NUM', 'NONE'))
         self.addAttrToList('CC_DCC_REV',    DriveAttributes.get('CC_DCC_REV', 'NONE'))
         self.addAttrToList('CC_DCC_DA',     DriveAttributes.get('CC_DCC_DA', 'NONE'))
         self.addAttrToList('CC_FISC_YEAR',  DriveAttributes.get('CC_FISC_YEAR', 'NONE'))
         self.addAttrToList('CC_FISC_WEEK',  DriveAttributes.get('CC_FISC_WEEK', 'NONE'))
      self.addAttrToList('BSNS_SEGMENT',  self.dut.longattr_bg.replace("/", ","))

   #-----------------------------------------#
   def updateDecommitDriveAttr(self, res, lst):
      if lst.has_key("CC_PART_NUM"):
         if len(lst["CC_PART_NUM"]) != 10:
            ScrCmds.raiseException(11900, "Length of CC_PART_NUM from FIS AutoCommit reply is not 10")
         DriveAttributes['CC_PART_NUM'] = lst["CC_PART_NUM"]
         objMsg.printMsg('Found CC_PART_NUM: %s' % lst["CC_PART_NUM"])
      else:
         ScrCmds.raiseException(11900, "FIS AutoCommit reply error")

   #-----------------------------------------#
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
