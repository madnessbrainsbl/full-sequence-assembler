#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2010, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Depop On The Fly Module
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/OTF_Waterfall.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/OTF_Waterfall.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#

from Constants import *
from TestParamExtractor import TP
import MessageHandler as objMsg
from State import CState
from Process import CProcess
import ScrCmds
import PIF
import traceback


DEPOP_DEBUG = 1
failTest = 0

#----------------------------------------------------------------------------------------------------------
class CDepop_OTF_Base(CState):
   """
      Depop on the fly supporting functioms
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut):
      self.dut = dut
      CState.__init__(self, dut)

   #-------------------------------------------------------------------------------------------------------
   def dpotfFilterTable(self, data, params, validHeadsOnly = True):
      ''' Apply any applicable filters to DBLog table data'''

      validHeads = self.validPhysHeads()
      params['Filters'] = params.get('Filters',{})       # Always go through data to allow removal of invalid head data

      filtered_table = []
      for row in data:
         validRow = 1
         for column, tuple in params['Filters'].items():
            if tuple[1].__class__ == str:
               validRow *= eval('row[column]'+ tuple[0] + 'tuple[1]')         # Test row against filter criteria - strings
            else:
               validRow *= eval(str(row[column])+ tuple[0] + str(tuple[1]))   # Test row against filter criteria - integers / floats
         if validRow and (not validHeadsOnly or int(row[params['Head']]) in validHeads):
            filtered_table.append(row)                                        # Row meets filter criteria, add to new table
      data = filtered_table

      if DEPOP_DEBUG:
         objMsg.printMsg(' Filtered_table: %s' % data)

      return data

   #-------------------------------------------------------------------------------------------------------
   def validPhysHeads(self):
      '''
         Return a list of valid (not depopped etc.) physical heads
      '''
      return list(head for head in filter(lambda h: h != INVALID_HD, self.dut.LgcToPhysHdMap))

   #-------------------------------------------------------------------------------------------------------
   def create_depop_table(self, depop_heads, spc_id = 1):
      '''
         Populate P000_DEPOP_HEADS table to inform WTFDisposition() of heads to depop
      '''
      self.dut.dblData.delTable('P000_DEPOP_HEADS', forceDeleteDblTable = 1)

      curSeq, occurrence, testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
      for head in depop_heads:
         self.dut.dblData.Tables('P000_DEPOP_HEADS').addRecord({
            'SPC_ID'          : spc_id,
            'OCCURRENCE'      : occurrence,
            'SEQ'             : curSeq,
            'TEST_SEQ_EVENT'  : testSeqEvent,
            'HD_PHYS_PSN'     : head,
            })

      if DEPOP_DEBUG:
         objMsg.printMsg('\nP000_DEPOP_HEADS table created for hd(s) %s' % depop_heads)
      objMsg.printMsg('')
      objMsg.printDblogBin(self.dut.dblData.Tables('P000_DEPOP_HEADS'))             # Dump depop table to log
      objMsg.printMsg('')

   #-------------------------------------------------------------------------------------------------------
   def depop_Options(self):
      ''' Return a list of head counts available for depop '''
      from PIF import nibletTable
      if testSwitch.SPLIT_VBAR_FOR_CM_LA_REDUCTION:
         from WTF_Tools import CWTF_Tools
         oWaterfall = CWTF_Tools()
      else:      
         from base_SerialTest import CWaterfallTest
         oWaterfall = CWaterfallTest(self.dut,{})
      partnum = oWaterfall.searchPN(self.dut.partNum)
      self.currentHeadcount = len(self.validPhysHeads())          # Get current head count from head map

      depopOptions = []
      for nibletKey in nibletTable[partnum]['Depop']:             # Find valid depop options for this PN
         if nibletKey:
            if nibletKey[2] == 'S':
               objMsg.printMsg("Depop On The Fly: Niblet Key %s Intended for Static Depop Only" %(nibletKey,))
            else:
               if int(nibletKey[1],16) < self.currentHeadcount:   # Only look for lower head counts
                  depopOptions.append(int(nibletKey[1],16))

      depopOptions = list(set(depopOptions))
      depopOptions.sort(reverse = True)
      objMsg.printMsg("Depop On The Fly: Current head count: %s, Possible Depop head counts: %s" %(self.currentHeadcount, depopOptions))

      return depopOptions

   #-------------------------------------------------------------------------------------------------------
   def postDepopFailcode(self, errData):
      ''' Post depop failcode to host
         - This will be the failcode which triggered the depop event
         - The failcode will be posted under *Oper
      '''
      from Setup import CSetup
      mySetup = CSetup()

      # Send failcode under *Oper
      evalOper = "*%s" % self.dut.nextOper
      if DEPOP_DEBUG:
         objMsg.printMsg("Depop OTF - Posting original failcode: %s to %s" %(errData[0][2], evalOper))

      # This will update attributes and failure information
      try:
         mySetup.errHandler(errType='raise', failureData=errData)
      except:
         objMsg.printMsg(traceback.format_exc(),objMsg.CMessLvl.IMPORTANT)

      RequestService('SetOperation',(evalOper,))

      # Send attributes and parametrics
      RequestService('SendRun', 1)

      # Reset to the primary operation
      RequestService('SetOperation',(self.dut.nextOper,))

      # Reset error code to prevent state machine issues.
      objMsg.printMsg("Resetting failure information")
      self.dut.errCode  = 0
      self.dut.errMsg   = ''
      self.dut.failTest = ''
      self.dut.failTemp = ''
      self.dut.failV12  = ''
      self.dut.failV5   = ''
      self.dut.testTime = 0.0

      self.dut.failureData = ScrCmds.makeFailureData(0,"")
      self.dut.objData.update({'failureData': self.dut.failureData})

      self.dut.failTestInfo = {'state': '','param': '', 'occur': 1, 'tstSeqEvt': 1, 'test': '', 'seq':'', 'stackInfo':''}
      self.dut.objData.update({'failTestInfo': self.dut.failTestInfo})

      self.dut.genExcept = ""

      ReportErrorCode(0)
      if testSwitch.virtualRun:
         import cmEmul
         cmEmul.ErrorCode = 0


   #-------------------------------------------------------------------------------------------------------
   def use_P172_HeadCaps(self):
      ''' Return a dictionary of capacities (in PBAs) for each physical head'''

      try:
         if testSwitch.extern.FE_0269440_496741_LOG_RED_P172_ZONE_TBL_SPLIT:
            zoneTable = self.dut.dblData.Tables('P172_ZONE_DATA').tableDataObj()
         else:
            zoneTable = self.dut.dblData.Tables('P172_ZONE_TBL').tableDataObj()
      except:
         if testSwitch.extern.FE_0269440_496741_LOG_RED_P172_ZONE_TBL_SPLIT:
            objMsg.printMsg("Depop OTF - Unable to locate P172_ZONE_DATA")
         else:
            objMsg.printMsg("Depop OTF - Unable to locate P172_ZONE_TBL")
         return []

      capacityDict = dict([(int(head),0) for head in self.validPhysHeads() ])
      for row in zoneTable:
         if int(row['HD_PHYS_PSN']) in capacityDict:
            if testSwitch.extern.FE_0269440_496741_LOG_RED_P172_ZONE_TBL_SPLIT:
               capacityDict[int(row['HD_PHYS_PSN'])] = capacityDict[int(row['HD_PHYS_PSN'])] + int(row['TRK_NUM'])*int(row['PBA_TRK'])
            else:
               capacityDict[int(row['HD_PHYS_PSN'])] = capacityDict[int(row['HD_PHYS_PSN'])] + int(row['TRK_NUM'])*int(row['PBA_TRACK'])

      if DEPOP_DEBUG:
         objMsg.printMsg('DEPOP_OTF Debug: use_P172_HeadCaps capacityDict = %s' %sorted(capacityDict, key = lambda x:capacityDict[x], reverse = False))

      return sorted(capacityDict, key = lambda x:capacityDict[x], reverse = False)


   #-------------------------------------------------------------------------------------------------------
   def use_P210_HeadCaps(self):
      ''' Return a dictionary of capacities for each physical head'''

      try:
         capacityTable = self.dut.dblData.Tables('P210_CAPACITY_HD2').tableDataObj()
      except:
         objMsg.printMsg("Depop OTF - Unable to locate P210_CAPACITY_HD2")
         return []

      capacityDict = dict([(int(head),0) for head in self.validPhysHeads() ])
      for row in capacityTable:
         if int(row['HD_PHYS_PSN']) in capacityDict:
            capacityDict[int(row['HD_PHYS_PSN'])] = float(row['HD_CAPACITY'])

      if DEPOP_DEBUG:
         objMsg.printMsg('DEPOP_OTF Debug: use_P210_HeadCaps capacityDict = %s' %sorted(capacityDict, key = lambda x:capacityDict[x], reverse = False))

      return sorted(capacityDict, key = lambda x:capacityDict[x], reverse = False)


   #-------------------------------------------------------------------------------------------------------
   def useDefaultHeadList(self):
      ''' Return a default list head in order of depop sequence'''

      if DEPOP_DEBUG:
         objMsg.printMsg('DEPOP_OTF Debug: useDefaultHeadList list = %s' %getattr(PIF, 'default_Depop_Hds', []))

      return getattr(PIF, 'default_Depop_Hds', [])


   #-------------------------------------------------------------------------------------------------------
   def nextDepopHeads(self):
      ''' Return a list of heads ordered by capacity
         - These heads are intended for use as sacrificial heads to depop to next available head count
         - Heads ranked lowest to highest capacity
      '''

      if self.dut.nextOper not in PIF.depop_next_head_method:                            # Fail if Oper not in table - must not be fully implemented
         ScrCmds.raiseException(11044, 'Current Operation: %s not in depop_next_head_method')

      depopHeadList = []
      for method in PIF.depop_next_head_method[self.dut.nextOper]:
         depopHeadList = eval('self.'+method+'()')
         if depopHeadList != []:
            break

      return depopHeadList

          
#----------------------------------------------------------------------------------------------------------
class CDepop_OTF_Check(CState, CDepop_OTF_Base):
   """
      Depop on the fly supporting class
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut):
      self.dut = dut
      CState.__init__(self, dut)
      CDepop_OTF_Base.__init__(self, dut)

   #-------------------------------------------------------------------------------------------------------
   def dpotfCheck(self, failCode, failType):
      ''' Check failure / state / operation for depop on the fly eligibility '''
      import PIF
      failCode = int(failCode)

      while True:
         if self.dut.currentState in ['DEPOP_OTF']:   # Already in DEPOP_OTF state
            break                                     # Return / Re-raise the primary failCode
         
         objMsg.printMsg("Depop On The Fly: Checking failcode: %s, state: %s, oper: %s" % (failCode, self.dut.currentState, self.dut.nextOper))
         
         if self.dut.nextOper not in getattr(PIF, 'allowed_Depop_Opers', []):
            objMsg.printMsg("Depop On The Fly not allowed for operation %s" %self.dut.nextOper)
            break                                     # No depop allowed for this Operation
         if self.dut.currentState in getattr(PIF, 'disallowed_Depop_States', []):
            objMsg.printMsg("Depop On The Fly not allowed for state %s" %self.dut.currentState)
            break                                     # No depop allowed for this state
         
         depopOptions = self.depop_Options()          # Get the depop options - so we know if / where we can depop
         if len(depopOptions) == 0:
            objMsg.printMsg("No depop path for this PN, raise primary error code!")
            break
         
         if PIF.depop_OTF_Config.has_key(failCode) and (PIF.depop_OTF_Config[failCode].has_key(self.dut.currentState) or PIF.depop_OTF_Config[failCode].has_key('AnyState')):
            global failTest
            failTest = self.dut.curTestInfo['test']
            
            DOTF_FailCodeDict = PIF.depop_OTF_Config[failCode]
            for state,stateDict in DOTF_FailCodeDict.items():
               if state in [self.dut.currentState,'AnyState']:
                  for table,tableDict in stateDict.items():
                     for tableOption,tableContent in tableDict.items():
                        validFailTests = tableContent.get('validFailTests',[])
                        if validFailTests and failTest not in validFailTests:
                           objMsg.printMsg("Test %s - is not a valid failtest for Depop On The Fly for EC: %s, Table: %s, raise primary error code!" % (failTest,failCode,table))
                           return False
            
            objMsg.printMsg("Valid DPOTF Failcode (%s) and State (%s) matched - setting nextState to DEPOP_OTF" % (failCode, self.dut.currentState))
            ScrCmds.statMsg('EC %s will execute Depop process, jump to bridge state DEPOP_OTF!' % failCode)
            self.dut.failType = failType
            self.dut.nextState = 'DEPOP_OTF'
            self.dut.stateTransitionEvent = 'restartAtState'
            return True
         else:
            break
         
      objMsg.printMsg("Failcode / State not covered by Depop On The Fly, raise primary error code!")
      return False


#----------------------------------------------------------------------------------------------------------
class CdpOTFHeadSelector(CDepop_OTF_Base):
   """
      Class that handle all head selection related depop on the fly support
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, failCode, failingState):
      self.dut = dut
      self.failCode = failCode
      self.failingState = failingState
      CDepop_OTF_Base.__init__(self, dut)

      self.currentHeadcount = len(self.validPhysHeads())          # Get current head count from head map
      self.selectionDict = {}
      self.depopHeadDict = dict([(head,(None,{})) for head in self.validPhysHeads()])
      self.depopHeadList = []

      self.dpOTF_build_tables()
      if self.selectionDict != {}:
         self.dpOTF_filter_tables()
         self.dpOTF_evaluate_heads()

   #-------------------------------------------------------------------------------------------------------
   def dpOTF_get_table_data(self, tableName):
      '''
         Return DBLog data for requested table
         - Return 'None' if no data available
      '''

      try:
         tableData = self.dut.dblData.Tables(tableName).tableDataObj()
      except Exception,e:
         if DEPOP_DEBUG:
            objMsg.printMsg(traceback.format_exc())
            objMsg.printMsg('Attention, Table %s is not found!!! Error msg is %s' %(tableName, e))
         tableData = None

      return tableData

   #-------------------------------------------------------------------------------------------------------
   def dpOTF_build_tables(self):
      '''
         Build master depop head selection dictionary holding all applicable (Failcode / State) depop OTF config criteria and corresponding data
         - Entries created for existing tables only
      '''
      import PIF

      dpOTF_config_params = {}
      if PIF.depop_OTF_Config[int(self.failCode)].has_key(self.failingState):
         dpOTF_config_params.update(PIF.depop_OTF_Config[int(self.failCode)][self.failingState])
      elif PIF.depop_OTF_Config[int(self.failCode)].has_key('AnyState'):
         dpOTF_config_params.update(PIF.depop_OTF_Config[int(self.failCode)]['AnyState'])
      if not dpOTF_config_params:
         ScrCmds.raiseException( 11044, 'Script Error - trying to decode invalid Depop Failcode / State' )
         
      for tableName,tableDict in dpOTF_config_params.items():
         tableData = self.dpOTF_get_table_data(tableName)
         if tableData:
            objMsg.printMsg('Preparing table data for %s' % tableName)
            for tableOption,tableContent in tableDict.items():
               if tableContent['NextState'] in ['SameState','LastState']:
                  tableContent['NextState'] = self.dut.lastState
               elif tableContent['NextState'] == 'NextState':
                  from StateTable import StateTable
                  tableContent['NextState'] = StateTable[self.dut.nextOper][self.dut.lastState][TRANS]['pass']
               if testSwitch.virtualRun:
                  from StateTable import StateTable
                  tableContent['NextState'] = StateTable[self.dut.nextOper][self.dut.lastState][TRANS]['pass']

               validFailTests = tableContent.get('validFailTests',[])
               if validFailTests and failTest not in validFailTests:
                  objMsg.printMsg("Test %s - is not a valid failtest for Depop On The Fly for EC: %s, Table: %s, TableOption: %s, removing this table option!" % (failTest,self.failCode,tableName,tableOption))
                  continue

               self.selectionDict[tableOption] = {
                  'Criteria'  : tableContent,
                  'TableName' : tableName,
                  'TableData' : tableData,
                  }
               self.selectionDict[tableOption]['Criteria']['Priority'] = self.selectionDict[tableOption]['Criteria'].get('Priority',0)

      if DEPOP_DEBUG > 1:
         objMsg.printMsg('Initial selectionDict %s' % self.selectionDict)

   #-------------------------------------------------------------------------------------------------------
   def dpOTF_filter_tables(self):
      '''
         Filter data in depop OTF selection dictionary based on filter criteria for each entry
      '''

      for tableOption,tableContent in self.selectionDict.items():
         tableContent['TableData'] = self.dpotfFilterTable(tableContent['TableData'], tableContent['Criteria'])

      if DEPOP_DEBUG > 1:
         objMsg.printMsg('Filtered selectionDict %s' % self.selectionDict)

   #-------------------------------------------------------------------------------------------------------
   def dpOTF_evaluate_heads(self):
      '''
         Apply depop head selection criteria for each entry in head selection dictionary
      '''

      for tableOption,tableContent in self.selectionDict.items():
         objMsg.printMsg('\nEvaluating Data for TableOption: %s, Table: %s, Priority: %s' % (tableOption, tableContent['TableName'], tableContent['Criteria']['Priority']))
         qualified_heads = dict([(head,None) for head in range(TP.Servo_Sn_Prefix_Matrix[HDASerialNumber[1:3]]['PhysHds'])])
         data = tableContent['TableData']
         dpotfParms = tableContent['Criteria']

         if dpotfParms['Comparator'] in ['Last', 'LastRow']:
            row = data[-1]
            qualified_heads[int(row[dpotfParms['Head']])] = float(row[dpotfParms['Column']])
         else:
            for row in data:
               if dpotfParms['Comparator'] in ['==', 'All', 'Count']:               # '==', 'All' and 'Count' rate by occurances, 'Count' will take highest count
                  if qualified_heads[int(row[dpotfParms['Head']])] == None:
                     qualified_heads[int(row[dpotfParms['Head']])] = 1
                  else:
                     qualified_heads[int(row[dpotfParms['Head']])] += 1
               else:                                                                # if <, > chosen, find extreme value for each head
                  if qualified_heads[int(row[dpotfParms['Head']])] == None or eval( str(row[dpotfParms['Column']]) + dpotfParms['Comparator'] + str(qualified_heads[int(row[dpotfParms['Head']])])):
                     qualified_heads[int(row[dpotfParms['Head']])] = float(row[dpotfParms['Column']])

         for head in qualified_heads.keys():                                        # Verify we have data for each head
            if qualified_heads[head] == None:
               qualified_heads.__delitem__(head)

         if DEPOP_DEBUG:
            objMsg.printMsg('  DEPOP_OTF Debug - qualified_heads dict: %s' % qualified_heads)

         if dpotfParms['Comparator'] in ['>', '==', 'All', 'Count']:                # Sort heads in order based on 'Comparator'
            reverse = True
         else:
            reverse = False
         depopHeadList = sorted(qualified_heads, key = lambda x: qualified_heads[x], reverse = reverse)

         objMsg.printMsg("  Qualifying depop heads: %s (Complete list, may contain already depopped heads)" % depopHeadList)
         if dpotfParms['Comparator'] in ['>', '<', 'Count', 'Last', 'LastRow']:     # Only take 'extreme' head in these cases, '==' & 'All' will attempt to depop all qualifying heads
            depopHeadList = [depopHeadList[0]]
            objMsg.printMsg('  Selecting only one head for depop: %s' %depopHeadList)

         tableContent['DepopHeads'] = []
         for head in depopHeadList:                                                 # Pare list down to only current heads (remove previously depopped heads)
            if self.depopHeadDict.has_key(head):
               tableContent['DepopHeads'].append(head)
            else:
               objMsg.printMsg('  WARNING: Depop Head %s is not a valid head - skipping this head' %head)
         objMsg.printMsg("  Screened / Qualifying depop head list: %s (Valid heads only, may still contain ineligible heads)" % tableContent['DepopHeads'])

      for tableOption,tableContent in self.selectionDict.items():                                    # Remove those results which yielded no depop heads
         if len(tableContent['DepopHeads']) == 0:
            objMsg.printMsg("\nRemoving Test %s, Table %s - No Qualified Depop Heads found" % (tableOption, tableContent['TableName']))
            self.selectionDict.pop(tableOption)

      selectionPriority = sorted(self.selectionDict, key = lambda x: self.selectionDict[x]['Criteria']['Priority'], reverse = True)

      if len(selectionPriority) != 0:
         objMsg.printMsg('\nSelecting Test %s, Table %s based on Priority' %(selectionPriority[0], self.selectionDict[selectionPriority[0]]['TableName']))
         self.selectionDict = self.selectionDict[selectionPriority[0]]                 # We can only depop based on one criteria set, chose the highest priority

         dpotfParms = self.selectionDict['Criteria']
         for head in self.selectionDict['DepopHeads']:
            score = 10*dpotfParms.get('Priority', 0) + self.selectionDict['DepopHeads'].index(head)
            if score > self.depopHeadDict[head][0]:
               self.depopHeadDict[head] = (score, dpotfParms)

         for head in self.depopHeadDict.keys():
            if self.depopHeadDict[head][0] == None:
               self.depopHeadDict.__delitem__(head)
         self.depopHeadList = sorted(self.depopHeadDict, key = lambda x: self.depopHeadDict[x][0], reverse = True)

      objMsg.printMsg('Sorted - descending, qualifying depopHeadList: %s' % self.depopHeadList)

#----------------------------------------------------------------------------------------------------------
class COTF_Waterfall(CState, CDepop_OTF_Base):
   """
      Class that will run Depop on the fly
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      self.dut = dut
      CState.__init__(self, dut)
      CDepop_OTF_Base.__init__(self, dut)
      self.zestEnabled = 0
      
      from AFH_SIM import CAFH_Frames
      self.frm = CAFH_Frames()
      objMsg.printMsg("Bef:VBAR.vbarGlobalClass %s" %(str(VBAR.vbarGlobalClass)))
      objMsg.printMsg("Bef:VBAR.getVbarGlobalVar()['formatReload'] %s" %(str(VBAR.getVbarGlobalVar()['formatReload'])))
      VBAR.clearVbarGlobalClass()
      objMsg.printMsg("VBAR.vbarGlobalClass %s" %(str(VBAR.vbarGlobalClass)))
      objMsg.printMsg("VBAR.getVbarGlobalVar()['formatReload'] %s" %(str(VBAR.getVbarGlobalVar()['formatReload'])))
      
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from Process import CProcess
      from WTF_Base import CDepopWaterfall
      self.oProc = CProcess()
      self.dut.pn_backup = self.dut.driveattr['PART_NUM']  

      #flag = self.safePowerLoss()
      #if flag == 0:
      #   return 0
      errData = self.dut.failureData
      objMsg.printMsg("\nENTERING DEPOP ON THE FLY\n")

      try:
         self.oProc.St(TP.prism_zest_display_status_287)
         p287ZestStateInfoTble = self.dut.dblData.Tables('P287_ZEST_STATE_INFO').tableDataObj()
      except:
         objMsg.printMsg("Unable to get P287_ZEST_STATE_INFO")

      zest_enabled_col  = (p287ZestStateInfoTble[0]['ZEST_ENABLED'])
      if zest_enabled_col == 'Y':
         self.zestEnabled = 1

      if self.zestEnabled == 1:
         objMsg.printMsg("Turn off ZEST")
         self.oProc.St(TP.prism_zest_off_287)
      else:
         objMsg.printMsg("ZEST state not running yet")
      
      objMsg.printMsg("DEPOP_OTF attribute: %s" %str(self.dut.driveattr['DEPOP_OTF']))
      objMsg.printMsg("Physical Head Map = %s" % self.dut.LgcToPhysHdMap)
      self.depopOptions = self.depop_Options()                 # Get list available depop options, if any
      
      if DEPOP_DEBUG > 1:
         objMsg.printMsg("COTF_Waterfall failureData: %s" %str(self.dut.failureData))
         objMsg.printMsg("COTF_Waterfall lastState: %s" %str(self.dut.lastState))
         objMsg.printMsg("COTF_Waterfall currentState: %s" %str(self.dut.currentState))
         objMsg.printMsg("COTF_Waterfall nextState: %s" %str(self.dut.nextState))
         objMsg.printMsg("COTF_Waterfall nextOper: %s" %str(self.dut.nextOper))

      self.oProc.St({'test_num':172,'prm_name':"Display SAP",'timeout': 100, 'CWORD1': 0, 'spc_id': 1}) #Dump SAP
      self.oProc.St({'test_num':172, 'prm_name':[], 'CWORD1': 9,'timeout': 12000.0}) # Dump RAP
      self.oProc.St({'test_num':172, 'prm_name':[], 'CWORD1': 1,'timeout': 12000.0}) # Dump CAP
      self.oProc.St({'test_num':172, 'prm_name':[], 'CWORD1': 4,'timeout': 12000.0}) # Dump Display Working Preamp Adaptives Table 

      if self.dut.nextOper in ['PRE2', 'CAL2']: 
         try:
            SetFailSafe()
            self.oProc.St({'test_num':101, 'prm_name':'prm_INIT_DBI_101', 'timeout':600000, 'spc_id':1,})
            ClearFailSafe()
         except:
            pass

      self.execute_depopHead(errData)
      self.postDepopFailcode(errData)                          # Post failcode to *Oper before going on
      self.oProc.St({'test_num':172,'prm_name':"Display SAP",'timeout': 100, 'CWORD1': 0, 'spc_id': 1}) #Dump SAP
      self.oProc.St({'test_num':172, 'prm_name':[], 'CWORD1': 9,'timeout': 12000.0}) # Dump RAP
      self.oProc.St({'test_num':172, 'prm_name':[], 'CWORD1': 1,'timeout': 12000.0}) # Dump CAP
      self.oProc.St({'test_num':172, 'prm_name':[], 'CWORD1': 4,'timeout': 12000.0}) # Dump Display Working Preamp Adaptives Table 

      #if (self.dut.nextOper == 'PRE2' and self.dut.systemAreaPrepared) or (self.dut.nextOper in ['CAL2', 'FNC2']):
      #if self.dut.VbarDone or self.dut.nextOper in ['FNC2']:   # completed vbar
      #   oDepopWaterfall = CDepopWaterfall(self.dut,self.params)
      #   if oDepopWaterfall.run() == 1:
      #      objMsg.printMsg('Drive Fail as capacity not enough after depod!')
      #      self.raiseError(errData)

      try:
         #slist
         self.oProc.St({'test_num':130, 'prm_name':[], 'CWORD1': 64,'timeout': 1800.0})
         #plist
         self.oProc.St({'test_num':130, 'prm_name':[], 'CWORD1': 128,'timeout': 1800.0})
         #dbi log
         self.oProc.St({'test_num':107, 'prm_name':[],'timeout': 1800.0})
      except:
         pass
         
      if testSwitch.FE_SGP_EN_REPORT_WTF_FAILURE and (self.dut.pn_backup != self.dut.driveattr['PART_NUM']):
         self.dut.OTFDepop = 1
          
      objMsg.printMsg("DEPOP_OTF attribute: %s" %str(self.dut.driveattr['DEPOP_OTF']))
      objMsg.printMsg("Physical Head Map: %s" % self.dut.LgcToPhysHdMap)
      objMsg.printMsg("Current Part Number: %s" % self.dut.partNum)
      if self.zestEnabled == 1:
         objMsg.printMsg("Turn on ZEST")
         self.oProc.St(TP.prism_zest_on_287)

      try:
         SetFailSafe()
         # Load the sorted copy of the bpi.bin
         self.oProc.St({'test_num': 210, 'prm_name': 'Restore SIF/BPI to PC files','timeout': 7200, 'CWORD3':0x04, })
         ClearFailSafe()
         objPwrCtrl.powerCycle(5000,12000,10,30)
      except:
         pass

      objMsg.printMsg("/nDEPOP ON THE FLY COMPLETE/n")

   #-------------------------------------------------------------------------------------------------------
   def execute_depopHead(self, errData):
      if DEPOP_DEBUG:
         objMsg.printMsg('DEPOP_OTF Debug - Error Data : %s' %str(errData))

      errCode = errData[0][2]
      try:
         errDescription = errData[0][0]
      except:
         errDescription = ''
         
      if self.dut.nextOper == "FNC2": # If the system zone is prepared. Need to reread back the frm during FNC2.
         self.frm.readFramesFromDRIVE_SIM()
         
      if DEPOP_DEBUG > 1:
         objMsg.printMsg('DEPOP_OTF Debug - errCode: %s' %errCode)
         objMsg.printMsg('DEPOP_OTF Debug - errDescription: %s' %errDescription)
         
      objDPHeads = CdpOTFHeadSelector(self.dut, errCode, self.dut.lastState)  # Get the list of failed heads to dpeop (only valid, depoppable heads included)
      depopHds = objDPHeads.depopHeadList 
      if not depopHds:                                                        # No failed heads identified, raise failure rather than depopping default heads
         objMsg.printMsg('Depop OTF Failed to find any valid DEPOP heads, raise primary fail code!')
         self.raiseError(errData)
         
      for head in depopHds:
         if head in getattr(PIF, 'disallowed_Depop_Hds', []):                 # Raise initial failcode - we cannot depop this head
            objMsg.printMsg('Depop OTF Failed - Depop of head %s not allowed, raise primary fail code!' % head)
            self.raiseError(errData)
         
      if self.currentHeadcount-len(depopHds) not in self.depopOptions:        # Numbers of heads to depop is not exact match for depop options
         for targetCount in self.depopOptions:
            if self.currentHeadcount-len(depopHds) > targetCount:             # Find first option and get number of extra heads to depop
               extraDepopCount = self.currentHeadcount-len(depopHds)-targetCount
               break
         else:                                                                # Too many heads identified, cannot depop
            objMsg.printMsg('Depop OTF Failed: Too many failed heads to depop, raise primary fail code!')
            self.raiseError(errData)

         nextDepopList = self.nextDepopHeads()                                # Get list of candidate depop heads based on capacity data, also return per head capacities
         for head in list(nextDepopList):
            if (head in depopHds) or (head not in self.validPhysHeads()) or (head in getattr(PIF, 'disallowed_Depop_Hds', [])):
               nextDepopList.remove(head)                                     # Toss duplicate and invalid heads from list

         if len(nextDepopList) < extraDepopCount:                             # Do we have enough heads to depop?
            objMsg.printMsg('Depop OTF Failed: not enough failed heads + default heads to depop, raise primary fail code!')
            self.raiseError(errData)

         objMsg.printMsg('Depop OTF Adding additional heads to depop list: %s' % nextDepopList[:extraDepopCount])
         depopHds.extend(nextDepopList[:extraDepopCount])                     # Tack required default heads to end of list
         
      self.create_depop_table(depopHds)
      self.dut.nextState = objDPHeads.depopHeadDict[depopHds[0]][1]['NextState']
      self.dut.objData.update({'DEPOP_OTF_RERUN_STATE': self.dut.nextState})

      if DEPOP_DEBUG:
         objMsg.printMsg('DEPOP_OTF Debug - nextState : %s' %self.dut.nextState)
         objMsg.printMsg('DEPOP_OTF Debug - stateTransitionEvent : %s' %self.dut.stateTransitionEvent)
         
      try:
         if DEPOP_DEBUG:
            objMsg.printMsg('DEPOP_OTF Debug - calling WTFDisposition')

         WTFDisposition(self.dut).run(WTFDisposition.dispoEnum.DEPOP)
       
         self.dut.objData['DEPOP_OTF_PWR_LOSS_OK'] = 'DEPOP_DONE'
         self.frm.removeDepopFrameDataFromCM_SIM()
         if (self.dut.nextOper == 'PRE2' and self.dut.systemAreaPrepared) or (self.dut.nextOper in ['CAL2', 'FNC2']):
             # If the system zone is prepared. Write back to
             self.frm.readFromCM_SIMWriteToDRIVE_SIM(exec231 = 1)
             # Here we need to add code to check that the results are valid.
             self.frm.clearFrames()
             self.frm.readFramesFromDRIVE_SIM()
             self.frm.display_frames()
      except Exception,e:
         objMsg.printMsg('Exception in DEPOP')
         objMsg.printMsg(traceback.format_exc())
         objMsg.printMsg('raise primary fail code!')
         self.raiseError(errData)

   #-------------------------------------------------------------------------------------------------------
   def raiseError(self,errData):
       if errData != ():
          errCode = errData[0][2]
          errMsg = errData[0][0]
          failTest = errData[0][1]
          ScrCmds.raiseException(errCode, 'Fail Test: ' + str(failTest)  + ' ErrMsg: ' + errMsg)
       else:
          ScrCmds.raiseException(11044, 'Wrong errData')

   #-------------------------------------------------------------------------------------------------------
   def safePowerLoss(self):
       if self.dut.powerLossEvent:
          powerloss_Level = self.dut.objData.get('DEPOP_OTF_PWR_LOSS_OK', 'NONE')
          self.dut.failureData = self.dut.objData.get('failureData','NA')
          self.dut.failType    = self.dut.objData.get('DEPOP_FAILTYPE', 0)
          if powerloss_Level == 'DEPOP_DONE':
             objMsg.printMsg('FLAG DEPOP_DONE has been detected, DEPOP_OTF was finished before powerloss, will rerun fail STATE!')
             self.dut.nextState= self.dut.objData.get('DEPOP_OTF_RERUN_STATE', 'INIT')
             self.dut.stateTransitionEvent = 'restartAtState'
             return 0
          elif powerloss_Level == 'HEAD_MASKED':
             objMsg.printMsg('FLAG HEAD_MASKED has been detected, drive was Depopped head before powerloss, will continue!')
             if testSwitch.SPLIT_BASE_SERIAL_TEST_FOR_CM_LA_REDUCTION:
                from Serial_Init import CInit_DriveInfo
             else:
                from base_SerialTest import CInit_DriveInfo
             CInit_DriveInfo(self.dut).run(force = 1)
             self.dut.nextState= self.dut.objData.get('DEPOP_OTF_RERUN_STATE', 'INIT')
             self.dut.stateTransitionEvent = 'restartAtState'
             return 0
          else:
             return 1
       else:
          objMsg.printMsg('self.dut.failureData %s' % str(self.dut.failureData))
          self.dut.objData.update({'failureData': self.dut.failureData})
          self.dut.objData.update({'DEPOP_FAILTYPE': self.dut.failType})
          return 1
          

#----------------------------------------------------------------------------------------------------------
class OTF_Depop_Demo(CState, CDepop_OTF_Base):
   """
      Class that will initiate a Depop on the fly event for demonstration of debug purposes.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      self.dut = dut
      CState.__init__(self, dut)
      CDepop_OTF_Base.__init__(self, dut)

   #------------------------------------------------------------------------------------------------------
   def run(self):
      if testSwitch.DEPOP_TESTING:
         heads = TP.DepopTestSN[self.dut.serialnum]
      else:
         heads = self.params.get('DEPOP_HEADS', None)
         
      if heads == None:
         ScrCmds.raiseException(11044, 'OTF_Depop_Demo failing - No DEPOP_HEADS defined')

      objMsg.printMsg('Forcing Depop On The Fly - Heads: %s' % heads)

      # Create dblog table with head information and raise exception for depop OTF to see
      self.create_depop_table(heads)

      ScrCmds.raiseException(10468, 'Forcing On-the-Fly depop of heads %s' % heads)  # Raise exception for OTF_DEPOP to catch


#----------------------------------------------------------------------------------------------------------
class CPreSkipZn(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if testSwitch.SKIPZONE and not testSwitch.virtualRun:
         from serialScreen import sptDiagCmds
         oSerial = sptDiagCmds()
         oSerial.PreSkipZone(self.params)
      else:
         objMsg.printMsg("=== Auto Dezone Disable. ===")


#----------------------------------------------------------------------------------------------------------
class CRetrieveSKIPZN(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if testSwitch.SKIPZONE and not testSwitch.virtualRun:
         from RdWr import CSkipZnFile
         self.dut.skipzn = CSkipZnFile().Retrieve_SKIPZN(dumpData = 1)
         objMsg.printMsg("Retrieved Skip Zone: %s" % self.dut.skipzn)
      else:
         objMsg.printMsg("=== Auto Dezone Disable. ===")

#----------------------------------------------------------------------------------------------------------
class WTFDisposition(CState):
      #-------------------------------------------------------------------------------------------------------

      class dispoEnum:
         DEPOP = 1
         DEPOP_RESTART = 2
         REZONE = 3
         DESTROKE = 4
         RPM_RESTART = 5
         PASS = 0xFF

      #-------------------------------------------------------------------------------------------------------
      def __init__(self, dut, params={}):
         self.params = params
         depList = []
         CState.__init__(self, dut, depList)
   
      #-------------------------------------------------------------------------------------------------------
      def run(self, WtfRequest = dispoEnum.DEPOP):
         """
            Handle disposition of failed drives for waterfall and depop
         """
   
         #TODO: Assess waterfall demand
         WtfRequest = self.params.get('WTF_REQUEST', WtfRequest)
   
         #Don't do elif so we can depop then rezone if necessary
         #Functions below should set the transition event
   
         headsToDepop = self.parseDepopFailureData()
   
         if WtfRequest == self.dispoEnum.DEPOP:
   
            self.depopHeads(headsToDepop)
            WtfRequest = self.dispoEnum.PASS
   
         if WtfRequest == self.dispoEnum.DEPOP_RESTART or WtfRequest == self.dispoEnum.RPM_RESTART:
            self.depopRestart()
            WtfRequest = self.dispoEnum.PASS
   
         if WtfRequest == self.dispoEnum.DESTROKE:
            self.destrokeRestart()
            WtfRequest = self.dispoEnum.PASS
   
      #-------------------------------------------------------------------------------------------------------
      def parseDepopFailureData(self):
         #get all depop requests and set up self.dut.depopMask
   
         from Exceptions import CDblogDataMissing, CRaiseException
   
         try:
            if testSwitch.FE_1111111_KillHead == 1:
               testSwitch.FE_1111111_KillHead = 0
            else:
               self.dut.depopMask = []
            badHeads = self.dut.dblData.Tables('P000_DEPOP_HEADS').tableDataObj()
   
            for hdRow in badHeads:
               if testSwitch.FE_0148166_381158_DEPOP_ON_THE_FLY:
                  head = int(hdRow['HD_PHYS_PSN'])
                  if head in self.dut.LgcToPhysHdMap:
                     self.dut.depopMask.append(head)
               else:
                  self.dut.depopMask.append(int(hdRow['HD_PHYS_PSN']))
   
            self.dut.depopMask = list(set(self.dut.depopMask))
         except (CDblogDataMissing, CRaiseException):
            pass
   
         self.dut.updateDepop_Req()
   
         return self.dut.depopMask
   
      #-------------------------------------------------------------------------------------------------------
      def depopHeads(self, headsToDepop):
         if headsToDepop:
            if testSwitch.FE_0148166_381158_DEPOP_ON_THE_FLY:
               from FSO import CFSO
               CFSO().depopHeads(headsToDepop, staticDepop = False)
               self.dut.objData.update({'DEPOP_OTF_PWR_LOSS_OK': 'HEAD_MASKED'})
               #Reset information for drive
               if testSwitch.SPLIT_BASE_SERIAL_TEST_FOR_CM_LA_REDUCTION:
                  from Serial_Init import CInit_DriveInfo
               else:
                  from base_SerialTest import CInit_DriveInfo
               CInit_DriveInfo(self.dut).run(force = 1)
   
               #self.dut.nextState= self.dut.failState
               self.dut.stateTransitionEvent = 'restartAtState'
               DriveAttributes['DEPOP_OTF'] = 'DONE'
            else:
               self.depopRestart()
   
      #-------------------------------------------------------------------------------------------------------
      def depopRestart(self):
         #Static depop is done during setup proc
         #  The state CSetupProc and sub-function "CFSO.setFamilyInfo" handle depoping by using self.dut.depopMask
         msg = "DEPOP/RPM RESTART REQUESTED.  RE-ROUTING DRIVE BACK TO BEGINNING"
         objMsg.printMsg('*'*100)
         objMsg.printMsg(msg)
         objMsg.printMsg('*'*100)
         if testSwitch.FE_0189561_418088_IRECOVERY_SUPPORT:
            objMsg.printMsg('DEPOP RESTART DETECTED, Ignore iRecovery command')
            self.dut.irIgnore = True
         self.updateAndResetResults(errorCode = 12169, errMsg = msg)
         # DriveAttributes['WATERFALL_REQ'] = 'NONE'
         # self.dut.Waterfall_Req = "NONE"
         self.dut.stateTransitionEvent = 'restartAtState'
         self.dut.nextState = 'INIT'
   
         if testSwitch.virtualRun:
            ScrCmds.raiseException(11044, "Depop restart requested during VE: Not allowed due to infinite recursion.")
   
      #-------------------------------------------------------------------------------------------------------
      def destrokeRestart(self):
         msg = "DESTROKE RESTART REQUESTED.  RE-ROUTING DRIVE BACK TO BEGINNING"
         objMsg.printMsg('*'*100)
         objMsg.printMsg(msg)
         objMsg.printMsg('*'*100)
         self.updateAndResetResults(errorCode = 12168, errMsg = msg)
   
         self.dut.stateTransitionEvent = 'restartAtState'
         self.dut.nextState = 'INIT'
   
         if testSwitch.virtualRun:
            ScrCmds.raiseException(11044, "Destroke restart requested during VE: Not allowed due to infinite recursion.")
   
      #-------------------------------------------------------------------------------------------------------
      def updateAndResetResults(self, errorCode, errMsg):
         """
         Sends event to update FIS of status so far under *Oper
         Removes memory copy of results
         Removes results file back to restart pointer.
         """
   
         #Prep the error info for fis upload
         from Setup import CSetup
   
         mySetup = CSetup()
         errCode, errMsg = ScrCmds.getFailureMessage(errorCode, errMsg)
         failureData = ScrCmds.makeFailureData(errCode, errMsg)
   
         #This will update attributes and failure information
         try:
            mySetup.errHandler(errType='raise',failureData=failureData)
         except:
            objMsg.printMsg(traceback.format_exc(),objMsg.CMessLvl.IMPORTANT)
   
         #Prep the parametric data for FIS upload
         mySetup.writeParametricData()
   
         if testSwitch.FE_SGP_EN_REPORT_RESTART_FAILURE:
            #Send the data under the Oper run
            evalOper = "%s" % self.dut.nextOper
         else:
            #Send the data under the *Oper run
            evalOper = "*%s" % self.dut.nextOper
   
         try:
            objMsg.printMsg("Backing up DriveAttributes PART_NUM %s" % DriveAttributes['PART_NUM'])
            tmp_pn = DriveAttributes['PART_NUM']
            DriveAttributes.update({'LOOPER_COUNT':1, 'PART_NUM': self.dut.pn_backup})      # LOOPER_COUNT to "disable" ADG
            RequestService('SetOperation',(evalOper,))
            #Send attributes and parametrics
            RequestService('SendRun', 1)
         finally:
            DriveAttributes['PART_NUM'] = tmp_pn
            DriveAttributes['LOOPER_COUNT'] = '0'                 # "enable" ADG
            objMsg.printMsg("Restoring DriveAttributes PART_NUM %s" % DriveAttributes['PART_NUM'])
   
         #Reset to the primary operation
         RequestService('SetOperation',(self.dut.nextOper,))
   
         #Delete results file back to restart pointer
         try:
            restartPtr = self.dut.objData['DEPOP_RESTART_PTR']
            if restartPtr > 0:
               ResultsFile.open('rb')
               try:
                  from cStringIO import StringIO
                  tempFile = StringIO(ResultsFile.read(restartPtr))
               finally:
                  ResultsFile.close()
   
               ResultsFile.open('wb')
               try:
                  ResultsFile.write(tempFile.read())
               finally:
                  tempFile.close()
                  ResultsFile.close()
   
         except KeyError:
            objMsg.printMsg("No restart pointer: Unable to remove duplicate results data")
         else:
            objMsg.printMsg("Results File Pointer Reset- Look in FIS event %s for Results File" % evalOper)
   
         #delete oracle tables
         objMsg.printMsg(self.dut.dblData.Tables())
         from DbLog import DbLog
         oDbLog = DbLog(self.dut)
         oDbLog.delAllOracleTables(confirmDelete = 1)
   
         #Clear XML data
         XmlResultsFile.open('wb')
         XmlResultsFile.write('')
         XmlResultsFile.close()
   
         #Clear the debug file so the file pointers aren't assumed accurate.
         self.dut.supprResultsFile.clearDebugFile()
   
         # Delete the dblog index file so the indicies aren't offset from old data
         self.dut.dblParser.objDbLogIndex.indexFile.delete()
   
         # Re-create the memory version of this file so it is ready to accept new data after reset
         from Parsers import DbLogIndexFile
         self.dut.dblParser.objDbLogIndex = DbLogIndexFile()
   
         #Reset the drive score
         objMsg.printMsg(self.dut.stateTransitionEvent + " Transition...resetting GOTF drive score to X's")
         from base_GOTF import CGOTFGrading
         CGOTFGrading().gotfResetDriveScore()
   
         # Reset error code to prevent state machine issues.
         objMsg.printMsg("Resetting failure information")
         self.dut.errCode  = 0
         self.dut.errMsg   = ''
         self.dut.failTest = 0
         self.dut.failTemp = 0
         self.dut.failV12  = 0
         self.dut.failV5   = 0
         self.dut.testTime = 0.0
   
         self.dut.failureData = ScrCmds.makeFailureData(0,"")
         self.dut.objData.update({'failureData': self.dut.failureData}) #save before fail_proc
   
         self.dut.failTestInfo = {'state': '','param': '', 'occur': 1, 'tstSeqEvt': 1, 'test': '', 'seq':'', 'stackInfo':''}
         self.dut.objData.update({'failTestInfo': self.dut.failTestInfo})
   
         self.dut.genExcept = ""
   
         ReportErrorCode(0)
         if testSwitch.virtualRun:
            import cmEmul
            cmEmul.ErrorCode = 0
   
         if testSwitch.BF_0128273_341036_AFH_DEPOP_HEAD_SUPPORT_AFH_SIM == 1:
            from AFH import CdPES
            odPES = CdPES(TP.masterHeatPrm_11, TP.defaultOCLIM)
            odPES.frm.reinitialize_CAFH_SIM()

