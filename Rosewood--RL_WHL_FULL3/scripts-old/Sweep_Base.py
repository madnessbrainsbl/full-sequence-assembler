#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Base Particle Sweep Module
#
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/12/27 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Sweep_Base.py $
# $Revision: #12 $
# $DateTime: 2016/12/27 23:52:43 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Sweep_Base.py#12 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
from State import CState
import MessageHandler as objMsg
from PowerControl import objPwrCtrl
import time
import ScrCmds


#----------------------------------------------------------------------------------------------------------
class CAdvanceSweep(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      self.dut = dut
      depList = []
      CState.__init__(self, dut, depList)
      
      from Servo import CServoScreen
      self.oSrvScreen = CServoScreen()
      
      self.scan1_err = {}
      self.scan2_err = {}
      self.disappear_err = {}
      self.new_err = {}
      self.scan1_err_cnt_by_head = {}
      self.scan2_err_cnt_by_head = {}
      self.disappear_err_cnt_by_head = {}
      self.new_err_cnt_by_head = {}

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if testSwitch.SEA_SWEEPER_ENABLED:
         #=== Initialize variables
         self.maxTrack = self.dut.maxTrack
         self.flawScanNumTestTrks = TP.adv_sweep_prm.get('FLAWSCAN_NUM_TEST_TRKS',20000)
         self.seekGuardBand = TP.adv_sweep_prm.get('SEEK_GUARD_BAND',4000)

         # Set to allow access to FAFH Zones at beginning of STATE
         if testSwitch.IS_FAFH: 
            self.oSrvScreen.St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value
            self.oSrvScreen.St(TP.AllowFAFH_AccessBit_178) # Allow FAFH access for servo test
            self.oSrvScreen.St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value

         #=== Full stroke random seek ===
         self.oSrvScreen.St(TP.full_stroke_random_sweep_prm_030)                     
         if testSwitch.IS_2D_DRV :
            if testSwitch.virtualRun:
               entries = [{'4MS-5MS':733, '5MS-6MS':133, '6MS-7MS':0}]
            else:
               entries = self.dut.objSeq.SuprsDblObject['P030_SEEK_SETTLE_DISTY']
            for entry in entries:
               if int(entry['4MS-5MS']) > 1400 and int(entry['5MS-6MS']) > 1000 and int(entry['6MS-7MS']) > 700:
                  objMsg.printMsg('4MS-5MS > 1400 and 5MS-6MS > 1000 and 6MS-7MS > 700')
                  if testSwitch.ENABLE_ON_THE_FLY_DOWNGRADE and self.downGradeOnFly(1, 10087):
                     objMsg.printMsg('10087, downgrade to %s as %s' % (self.dut.BG, self.dut.partNum))
                     break
                  else:
                     ScrCmds.raiseException(10087, '4MS-5MS > 1400 and 5MS-6MS > 1000 and 6MS-7MS > 700')

         pbic_test_enabled = 1
         if testSwitch.PBIC_SUPPORT and \
            ((self.dut.BG in ['SBS'] and len(ConfigVars[CN].get('PBICSwitches', '00000')) >= 3 and int(ConfigVars[CN].get('PBICSwitches', '00000')[2]) > 0) or\
             (self.dut.BG not in ['SBS'] and len(ConfigVars[CN].get('PBICSwitchesOEM', '00000')) >= 3 and int(ConfigVars[CN].get('PBICSwitchesOEM', '00000')[2]) > 0)):
            from PBIC import ClassPBIC
            objPBIC = ClassPBIC()
            pbic_test_enabled = objPBIC.PBIC_Control_bd()
         
         if pbic_test_enabled == 1:

            #=== Butterfly sweep at OD, MD and ID ===
            self.doButterflySweep()
            #=== Spin at max RPM for 5 mins, restore to 7200 RPM ===
            if testSwitch.SEA_SWEEPER_RPM:
               oBasicSweep = CBasicSweep(self.dut,self.params)
               oBasicSweep.changeRPM()
            #=== Quick media defect scan from OD to ID, at x track interval ===
            # Record defect count, D1
            if testSwitch.HDI_ENABLED:
               from MediaScan import CUserFlaw               
               self.oUserFlaw = CUserFlaw()
               
               # if the above switch is on, it will perform write/read operation, need to dis-allow access
               # Set to dis-allow access to FAFH Zones at end of STATE
               if testSwitch.IS_FAFH: 
                  self.oSrvScreen.St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value
                  self.oSrvScreen.St(TP.DisallowFAFH_AccessBit_178) # Dis-allow FAFH access after completing servo test
                  self.oSrvScreen.St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value

               if 'AFS' in TP.DataFlawFeatures[self.dut.partNum[0:3]]:
                  self.oUserFlaw.initdbi() # initialize the dblog buffer for flawscan within f/w
                  self.mediaScan1()
                  self.oUserFlaw.repdbi() # dump db log to host (result file)

               # turn back on after finish 
               # Set to allow access to FAFH Zones at beginning of STATE
               if testSwitch.IS_FAFH: 
                  self.oSrvScreen.St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value
                  self.oSrvScreen.St(TP.AllowFAFH_AccessBit_178) # Allow FAFH access for servo test
                  self.oSrvScreen.St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value

            #=== Full stroke two-point seek ===
            startCyl = self.seekGuardBand
            endCyl = self.maxTrack[0] - self.seekGuardBand
            self.oSrvScreen.St(self.oSrvScreen.oUtility.overRidePrm(TP.full_stroke_two_point_sweep,
                                      {'START_CYL':self.oSrvScreen.oUtility.ReturnTestCylWord(startCyl),
                                       'END_CYL' :self.oSrvScreen.oUtility.ReturnTestCylWord(endCyl),
                                      }))
         #=== LUL for ~5 mins ===
         try:
            self.oSrvScreen.servoRetract(TP.lul_prm_025)
         except ScriptTestFailure, failureData:
            if failureData[0][2] == 11092 and testSwitch.IS_2D_DRV:
               if not self.checkUnloadCurrent():
                  raise failureData
               elif self.dut.BG not in ['SBS']:
                  if testSwitch.ENABLE_ON_THE_FLY_DOWNGRADE and self.downGradeOnFly(1, 11092):
                     objMsg.printMsg('EC11092, downgrade to %s as %s' % (self.dut.BG, self.dut.partNum))
                  else:
                     raise failureData
            else:
               raise failureData

         if testSwitch.FE_0303511_305538_P_ENABLE_UNLOAD_CURR_OVER_TIME_SCREEN or not testSwitch.IS_2D_DRV:
            self.checkUnloadOverTime(TP.T025_Unload_Curr_Screen, spcid=TP.lul_prm_025['spc_id'])
        
         if (self.dut.partNum == '2G3172-900' or self.dut.partNum == '2G2174-900') and self.dut.nextOper == 'FNC2':
            from dbLogUtilities import DBLogCheck
            dblchk = DBLogCheck(self.dut)
            if (dblchk.checkComboScreen(TP.T25_LCUR_Check) == FAIL) or (dblchk.checkComboScreen(TP.T25_ULCUR_Check) == FAIL):
                  if testSwitch.ENABLE_ON_THE_FLY_DOWNGRADE and self.downGradeOnFly(1, 11092):
                     objMsg.printMsg('EC11092, downgrade to %s as %s' % (self.dut.BG, self.dut.partNum))
                  else:
                     ScrCmds.raiseException(11092, "Max Unload/Load Current exceeded")
         
        
         if testSwitch.RUN_LUL_MAX_CURRENT_SCREEN:
            self.checkLULStatus()
            
         if pbic_test_enabled == 1:

            #=== Spin at max RPM for 5 mins, restore to 7200 RPM ===
            if testSwitch.SEA_SWEEPER_RPM:
               oBasicSweep.changeRPM()

         # Set to dis-allow access to FAFH Zones at end of STATE
         if testSwitch.IS_FAFH: 
            self.oSrvScreen.St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value
            self.oSrvScreen.St(TP.DisallowFAFH_AccessBit_178) # Dis-allow FAFH access after completing servo test
            self.oSrvScreen.St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value

         #=== Quick media defect scan from OD to ID, at x track interval ===
         # Record defect count, D1
         if testSwitch.HDI_ENABLED:
            if 'AFS' in TP.DataFlawFeatures[self.dut.partNum[0:3]]:
               objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
               self.oUserFlaw.initdbi() # initialize the dblog buffer for flawscan within f/w
               self.mediaScan2()
               self.checkNewDefect()
               self.updateDBLogTable()
               self.oUserFlaw.repdbi() # dump db log to host (result file)
               # Check delta defect count, D2-D1
               self.checkDeltaDefectCount()
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

   #-------------------------------------------------------------------------------------------------------
   def checkUnloadCurrent(self):
      result = True
      if self.dut.objSeq.SuprsDblObject.has_key('P025_LOAD_UNLOAD_PARAMS'):
      
         objMsg.printMsg('Check mean unload peak current(280) and Continous 8x unload peak current(290)')
         unloadCur = {}
         for entry in self.dut.objSeq.SuprsDblObject['P025_LOAD_UNLOAD_PARAMS']:
            unloadCur[int(entry['CYCLE_NUM'])] = float(entry['ULD_MAX_CUR'])
         cycleNum = unloadCur.keys()
         cycleNum.sort()
         
         meanUnloadCurrent = sum(unloadCur.values()) / len(cycleNum)
         if meanUnloadCurrent > 280:
            objMsg.printMsg('Fail because mean unload peak current > 280 and Continous 8x unload peak current > 290')
            #ScrCmds.raiseException(11092, 'Mean unload peak current > 280 and Continous 8x unload peak current > 290')
            result = False
      return result
            
   #-------------------------------------------------------------------------------------------------------
   def checkUnloadOverTime(self, parm, spcid=None):
      """
      Check Unload Over Time to screen drives
      """
      objMsg.printMsg('Screening unload current over time...')
      try:
         if spcid == None: # if spc_id is defined, then get only tables matching the spc_id
            tbl = self.dut.dblData.Tables(parm['table']).tableDataObj()
         else:
            tbl = self.dut.dblData.Tables(parm['table']).chopDbLog('SPC_ID', 'match', str(spcid))
      except:
         objMsg.printMsg('Warning, table %s not found. Skipping...' % parm['table'])
         return 0

      fail_cnt = 0
      for entry in tbl:
         hdr = entry[parm['header']] #   MAX, STDEV
         col = entry[parm['column']] # 122.2,   3.1
         if hdr in parm:
            res = float(col)
            objMsg.printMsg('%s = %3.2f (spec = %s)' % (hdr, res, parm[hdr]))
            if (res >= parm[hdr]):
               fail_cnt += 1

      if fail_cnt >= len(parm) - 3: # ignore table, header, column
         if testSwitch.ENABLE_ON_THE_FLY_DOWNGRADE and self.downGradeOnFly(1, 48539):
            objMsg.printMsg('EC48539, downgrade to %s as %s' % (self.dut.BG, self.dut.partNum))
         else:
            ScrCmds.raiseException(48539, "Unload Current Max/StDev Limits exceeded")

   #-------------------------------------------------------------------------------------------------------
   def checkLULStatus(self):
      """
      CHECK LUL STATUS
      """
      objMsg.printMsg('START CHECK LOAD_MAX_CUR STATUS')
      try:
         entries = self.dut.dblData.Tables('P025_LD_UNLD_PARAM_STATS').tableDataObj()
      except:
         objMsg.printMsg('WARNING...TABLE P025_LD_UNLD_PARAM_STATS NOT FOUND')
         return 0
      HSA_SN =DriveAttributes.get('HSA_SERIAL_NUM','NONE')
      objMsg.printMsg('HSA_SN: %s' % HSA_SN)
      
      if HSA_SN[0] == "K": # Compart
         load_max_cur_LSL = TP.load_max_cur_LSL
         load_max_cur_USL = TP.load_max_cur_USL
      else:
         load_max_cur_LSL = TP.load_max_cur_LSL + TP.load_max_cur_LSL_adjust
         load_max_cur_USL = TP.load_max_cur_USL + TP.load_max_cur_USL_adjust

      for entry in entries:
         if entry['STATISTIC_NAME'] == 'MAX':
            result = abs(round(float(entry['LOAD_MAX_CUR']),2))
            if result > load_max_cur_USL or result < load_max_cur_LSL:
               objMsg.printMsg('LOAD_MAX_CUR = %s' % result)
               objMsg.printMsg('load_max_cur_USL = %s' % load_max_cur_USL)
               objMsg.printMsg('load_max_cur_LSL = %s' % load_max_cur_LSL)
               ScrCmds.raiseException(14664, "LOAD_MAX_CUR Limit exceeded")
      objMsg.printMsg('CHECK LOAD_MAX_CUR pass')
   
   #-------------------------------------------------------------------------------------------------------
   def doButterflySweep(self):
      minIDTrack = min(self.dut.maxTrack)
      numOfTstTrks = TP.BUTTERFLY_NO_OF_TEST_TRKS
      testcyllist = [(0, numOfTstTrks), (int(minIDTrack/2),int(minIDTrack/2)+numOfTstTrks),
                     (minIDTrack-numOfTstTrks, minIDTrack-1 )]
      for scyl,ecyl in testcyllist:
         self.oSrvScreen.St(self.oSrvScreen.oUtility.overRidePrm(TP.butterfly_sweep_prm_030,
                                    {'START_CYL':self.oSrvScreen.oUtility.ReturnTestCylWord(scyl),
                                     'END_CYL' :self.oSrvScreen.oUtility.ReturnTestCylWord(ecyl),
                                    }))

   #-------------------------------------------------------------------------------------------------------
   def mediaScan1(self):
      #=== Delete table P109_LOG_VER_DATA_ERR_FSB
      if not testSwitch.virtualRun:
         try:
            self.dut.dblData.delTable('P109_LOG_VER_DATA_ERR_FSB', forceDeleteDblTable = 1)
         except:
            objMsg.printMsg("Delete P109_LOG_VER_DATA_ERR_FSB table failed")
            pass

      try:
         #=== Write pass
         prmcopy = TP.prm_Interval_AFS_2T_Write_109.copy()
         objMsg.printMsg("Media_Scan_1: Write Pass at OD, all heads")
         prmcopy.update({ 'START_CYL' : self.oSrvScreen.oUtility.ReturnTestCylWord(0), \
                          'END_CYL'   : self.oSrvScreen.oUtility.ReturnTestCylWord(self.flawScanNumTestTrks), \
                          })
         self.oSrvScreen.St(prmcopy)

         for head in range(self.dut.imaxHead):
            objMsg.printMsg("Media_Scan_1: Write Pass at ID, head %d" %head)
            startCyl = self.maxTrack[head]-self.flawScanNumTestTrks
            endCyl = self.maxTrack[head]
            prmcopy.update({'HEAD_RANGE': (head<<8|head,),
                          'START_CYL' : self.oSrvScreen.oUtility.ReturnTestCylWord(startCyl), \
                          'END_CYL'   : self.oSrvScreen.oUtility.ReturnTestCylWord(endCyl), \
                          })
            self.oSrvScreen.St(prmcopy)

         #=== Read pass
         self.mediaScan2()
         self.scan1_err = self.makeErrDict(spc_id=1)

      finally:
         import traceback
         objMsg.printMsg(traceback.format_exc(),objMsg.CMessLvl.IMPORTANT)

   #-------------------------------------------------------------------------------------------------------
   def mediaScan2(self):
      #=== Delete table P109_LOG_VER_DATA_ERR_FSB
      if not testSwitch.virtualRun:
         try:
            self.dut.dblData.delTable('P109_LOG_VER_DATA_ERR_FSB', forceDeleteDblTable = 1)
         except:
            objMsg.printMsg("Delete P109_LOG_VER_DATA_ERR_FSB table failed")
            pass
      prmcopy = TP.prm_Interval_AFS_CM_Read_109.copy()
      #=== Read pass at OD, all heads
      objMsg.printMsg("Media_Scan_2: Read Pass at OD, all heads")
      prmcopy.update({'START_CYL' : self.oSrvScreen.oUtility.ReturnTestCylWord(0), \
                      'END_CYL'   : self.oSrvScreen.oUtility.ReturnTestCylWord(self.flawScanNumTestTrks), \
                    })
      self.oSrvScreen.St(prmcopy)

      #=== Read pass at ID, by head
      for head in range(self.dut.imaxHead):
         objMsg.printMsg("Media_Scan_2: Read Pass at ID, head %d" %head)
         startCyl = self.maxTrack[head]-self.flawScanNumTestTrks
         endCyl = self.maxTrack[head]
         prmcopy.update({'HEAD_RANGE': (head<<8|head,), \
                          'START_CYL' : self.oSrvScreen.oUtility.ReturnTestCylWord(startCyl), \
                          'END_CYL'   : self.oSrvScreen.oUtility.ReturnTestCylWord(endCyl), \
                          })
         self.oSrvScreen.St(prmcopy)
      self.scan2_err = self.makeErrDict(spc_id=2)

   #-------------------------------------------------------------------------------------------------------
   def checkDeltaDefectCount(self):
      if testSwitch.virtualRun:
         (maxDiff, minDiff, diffData, entrySigVal) = self.dut.dblData.Tables('P107_VERIFIED_FLAWS').diffDbLog(diffItem='VRFD_FLAWS',entrySig='TEST_SEQ_EVENT',sortOrder=['HD_LGC_PSN','HD_LGC_PSN'])
      else:
         (maxDiff, minDiff, diffData, entrySigVal) = self.dut.dblData.Tables('P107_VERIFIED_FLAWS').diffDbLog(diffItem='VRFD_FLAWS',entrySig='TEST_SEQ_EVENT',sortOrder=['HD_LGC_PSN'])

      for item in diffData:
         self.dut.dblData.Tables('P107_DELTA_DEFECT_COUNT').addRecord(
            {
            'HD_PHYS_PSN'       : item.get('HD_PHYS_PSN'),
            'SPC_ID'            : self.dut.objSeq.curRegSPCID,
            'OCCURRENCE'        : self.dut.objSeq.getOccurrence(),
            'SEQ'               : self.dut.objSeq.curSeq,
            'TEST_SEQ_EVENT'    : self.dut.objSeq.getTestSeqEvent(0),
            'HD_LGC_PSN'        : item.get('HD_LGC_PSN'),
            'DELTA_DEFECT_COUNT': item.get('difference')
            })

      objMsg.printDblogBin(self.dut.dblData.Tables('P107_DELTA_DEFECT_COUNT'))

      # Check for failures
      failedList = []
      for item in diffData:
         if item.get('difference') > TP.prm_AdvSweep_Criteria['delta_defect_limit']:
            failedList.append ([item.get('HD_LGC_PSN'),item.get('difference')])

      if failedList:
         ScrCmds.raiseException(14714, "Exceeded delta defect count limit, failed List %s" %str(failedList))

   #-------------------------------------------------------------------------------------------------------
   def makeErrDict(self,spc_id=1):
      """
      Sample table:
      P109_LOG_VER_DATA_ERR_FSB:
       HD_PHYS_PSN HD_LGC_PSN TRK_NUM SECTOR OFFSET SYM_POS SYM_LEN RPT_CNT
                 0          0    2436    104   2705  436801       1       3
                 0          0   11688     44   3551  185447       1       3
                 0          0   14208    115   3206  478616       3       3
                 0          0   14520     53    741  215285       1       3
      """
      #self.scan1_err
      if testSwitch.virtualRun:
         spc_id = str(spc_id)
         logdata = self.dut.dblData.Tables('P109_LOG_VER_DATA_ERR_FSB').chopDbLog('SPC_ID', 'match',spc_id)
      else:
         try:
            logdata = self.dut.dblData.Tables('P109_LOG_VER_DATA_ERR_FSB').tableDataObj()

         except:
            logdata = {}
      err_dict = {}
      for record in logdata:
         err_dict[ int(record['HD_PHYS_PSN']), int(record['TRK_NUM']), int(record['SECTOR']) ] = 1

      if DEBUG:
         objMsg.printMsg("defect table by head, track, sector:--> %s" %str( err_dict ))

      return err_dict

   #-------------------------------------------------------------------------------------------------------
   def checkNewDefect(self):
      if DEBUG:
         objMsg.printMsg("scan1 defect table==>%s" %str(self.scan1_err))
         objMsg.printMsg("scan2 defect table==>%s" %str(self.scan2_err))
      #=== Disappeared defects
      for err in self.scan1_err.keys():
         if err not in self.scan2_err.keys():
            self.disappear_err[err] = 1
      #=== New found defects
      for err in self.scan2_err.keys():
         if err not in self.scan1_err.keys():
            self.new_err[err] = 1
      #=== Summarize sector defect counts by head
      self.scan1_err_cnt_by_head = self.getErrCountByHead(self.scan1_err)
      self.scan2_err_cnt_by_head = self.getErrCountByHead(self.scan2_err)
      self.disappear_err_cnt_by_head = self.getErrCountByHead(self.disappear_err)
      self.new_err_cnt_by_head = self.getErrCountByHead(self.new_err)

   #-------------------------------------------------------------------------------------------------------
   def getErrCountByHead (self, entries):
      data = {}
      for key in entries:
         if key[0] not in data:
            data[key[0]] = 1   # head,track,sector = key
         else:
            data[key[0]] += 1

      return data

   #-------------------------------------------------------------------------------------------------------
   def updateDBLogTable(self):
      #=== P109_WEDGE_FLAW_01: Defect entries for MediaScan1
      datalist = self.scan1_err.keys()
      datalist.sort()
      for data in datalist:
         self.dut.dblData.Tables('P109_WEDGE_FLAW_01').addRecord(
            {
            'HD_PHYS_PSN'    : data[0],
            'SPC_ID'         : self.dut.objSeq.curRegSPCID,
            'OCCURRENCE'     : self.dut.objSeq.getOccurrence(),
            'SEQ'            : self.dut.objSeq.curSeq,
            'TEST_SEQ_EVENT' : self.dut.objSeq.getTestSeqEvent(0),
            'HD_LGC_PSN'     : data[0],
            'TRK_NUM'        : data[1],
            'WEDGE'          : data[2],
            })
      #=== P109_WEDGE_FLAW_02: Defect entries for MediaScan2
      datalist = self.scan2_err.keys()
      datalist.sort()
      for data in datalist:
         self.dut.dblData.Tables('P109_WEDGE_FLAW_02').addRecord(
            {
            'HD_PHYS_PSN'    : data[0],
            'SPC_ID'         : self.dut.objSeq.curRegSPCID,
            'OCCURRENCE'     : self.dut.objSeq.getOccurrence(),
            'SEQ'            : self.dut.objSeq.curSeq,
            'TEST_SEQ_EVENT' : self.dut.objSeq.getTestSeqEvent(0),
            'HD_LGC_PSN'     : data[0],
            'TRK_NUM'        : data[1],
            'WEDGE'          : data[2],
            })
      #=== P109_NEW_WEDGE_FLAW: New defect entries in MediaScan2
      datalist = self.new_err.keys()
      datalist.sort()
      for data in datalist:
         self.dut.dblData.Tables('P109_NEW_WEDGE_FLAW').addRecord(
            {
            'HD_PHYS_PSN'    : data[0],
            'SPC_ID'         : self.dut.objSeq.curRegSPCID,
            'OCCURRENCE'     : self.dut.objSeq.getOccurrence(),
            'SEQ'            : self.dut.objSeq.curSeq,
            'TEST_SEQ_EVENT' : self.dut.objSeq.getTestSeqEvent(0),
            'HD_LGC_PSN'     : data[0],
            'TRK_NUM'        : data[1],
            'WEDGE'          : data[2],
            })
      #=== P109_VANISH_WEDGE_FLAW: Disappeared defect entries in MediaScan2
      datalist = self.disappear_err.keys()
      datalist.sort()
      for data in datalist:
         self.dut.dblData.Tables('P109_VANISH_WEDGE_FLAW').addRecord(
            {
            'HD_PHYS_PSN'    : data[0],
            'SPC_ID'         : self.dut.objSeq.curRegSPCID,
            'OCCURRENCE'     : self.dut.objSeq.getOccurrence(),
            'SEQ'            : self.dut.objSeq.curSeq,
            'TEST_SEQ_EVENT' : self.dut.objSeq.getTestSeqEvent(0),
            'HD_LGC_PSN'     : data[0],
            'TRK_NUM'        : data[1],
            'WEDGE'          : data[2],
            })
      #=== P109_WEDGE_FLAW_COUNT
      for head in range(self.dut.imaxHead):
         self.dut.dblData.Tables('P109_WEDGE_FLAW_COUNT').addRecord(
            {
            'HD_PHYS_PSN'        : self.dut.LgcToPhysHdMap[head],
            'SPC_ID'             : self.dut.objSeq.curRegSPCID,
            'OCCURRENCE'         : self.dut.objSeq.getOccurrence(),
            'SEQ'                : self.dut.objSeq.curSeq,
            'TEST_SEQ_EVENT'     : self.dut.objSeq.getTestSeqEvent(0),
            'HD_LGC_PSN'         : head,
            'FLAW_CNT_01'        : self.scan1_err_cnt_by_head.get(head,0),
            'FLAW_CNT_02'        : self.scan2_err_cnt_by_head.get(head,0),
            'NEW_FLAW_CNT'       : self.new_err_cnt_by_head.get(head,0),
            'VANISH_FLAW_CNT'    : self.disappear_err_cnt_by_head.get(head,0),
            })

      #=== Print DBLog tables
      objMsg.printDblogBin(self.dut.dblData.Tables('P109_WEDGE_FLAW_01'))
      objMsg.printDblogBin(self.dut.dblData.Tables('P109_WEDGE_FLAW_02'))
      if len(self.new_err):
         objMsg.printDblogBin(self.dut.dblData.Tables('P109_NEW_WEDGE_FLAW'))
      if len(self.disappear_err):
         objMsg.printDblogBin(self.dut.dblData.Tables('P109_VANISH_WEDGE_FLAW'))
      objMsg.printDblogBin(self.dut.dblData.Tables('P109_WEDGE_FLAW_COUNT'))


#----------------------------------------------------------------------------------------------------------
class CBasicSweep(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      self.dut = dut
      depList = []
      CState.__init__(self, dut, depList)
      
      from Servo import CServoFunc
      self.oServoFunc = CServoFunc()

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if self.dut.BG in ['SBS'] and len(ConfigVars[CN].get('PBICSwitches', '00000')) >= 3 and int(ConfigVars[CN].get('PBICSwitches', '00000')[2]) == 2:
         return
      if self.dut.BG not in ['SBS'] and len(ConfigVars[CN].get('PBICSwitchesOEM', '00000')) >= 3 and int(ConfigVars[CN].get('PBICSwitchesOEM', '00000')[2]) == 2:
         return
      if testSwitch.SEA_SWEEPER_ENABLED:
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=1, onTime=5, useESlip=1)
         #=== Spin at max RPM for 4 mins, restore to 7200 RPM ===
         if testSwitch.SEA_SWEEPER_RPM:
            self.changeRPM()
         #=== Power cycle with unload from ID, MD, OD for (30,30,10) each ===
         self.seekAndPowerCycle()
         if testSwitch.FE_SGP_81592_ADD_FULL_STROKE_RND_SK_IN_BASIC_SWEEP_2_IMPROVE_T136:
            #=== Full stroke random seek ===
            self.oServoFunc.St(TP.full_stroke_random_sweep_prm_030)
            objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=1, onTime=5, useESlip=1)

         #=== Spin at max RPM for 4 mins, restore to 7200 RPM ===
         if testSwitch.SEA_SWEEPER_RPM:
            self.changeRPM()
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=1, onTime=5, useESlip=1)

   #-------------------------------------------------------------------------------------------------------
   def changeRPM(self):
      # Test revised to leave drive in better state for continued testing.
      # Time to spin at higher RPM is set in the parameters passed in the test call.
      changeRPMloops = getattr(TP, 'changeRPMloops', 1)
      changeRPMnominalDwell = getattr(TP, 'changeRPMnominalDwell', 0)
      for loop in range(changeRPMloops):
         time.sleep(changeRPMnominalDwell)
         self.oServoFunc.setSpinSpeed(TP.maxRPM_spinup_spindownPrm_4)

   #-------------------------------------------------------------------------------------------------------
   def seekAndPowerCycle(self):
      '''
         1. Testzone at ID, MD, OD = numzn-1, numzn/2 - 1 , 0
         2. Seek to middle of the zone. If fails, shift 10 trks away from the failed trk.
         3. Loop for ID, MD, OD: 30, 30, 10
      '''
      # Prepare testing zones: [(testzone, loop),]
      testzonelist = [(self.dut.numZones - 1,30), (self.dut.numZones/2 - 1,30), (0,10)]
      objMsg.printMsg("Testing zones, loop: %s" %(str(testzonelist)))

      # Loop test zones
      from FSO import CFSO, dataTableHelper            
      self.oFSO = CFSO()
      self.dth = dataTableHelper()
      self.oFSO.getZoneTable()
      zt = self.dut.dblData.Tables(TP.zone_table['table_name']).tableDataObj()     
      for testzone, loop in testzonelist:
         Index = self.dth.getFirstRowIndexFromTable_byZone(zt, 0, testzone)
         testcyl = int(zt[Index]['ZN_START_CYL']) + (int(zt[Index]['NUM_CYL']))/2
         while Index+1< len(zt) and int(zt[Index]['ZN']) == int(zt[Index+1]['ZN']):
            testcyl += (int(zt[Index]['NUM_CYL']))/2
            Index += 1
         for i in range (loop):
            try:
               TP.direct_write_seek_prm_030['START_CYL'] = self.oServoFunc.oUtility.ReturnTestCylWord(testcyl)
               TP.direct_write_seek_prm_030['END_CYL'] = self.oServoFunc.oUtility.ReturnTestCylWord(testcyl)
               self.oServoFunc.St(TP.direct_write_seek_prm_030)
               time.sleep(0.5) # Sleep for 500ms
               self.oServoFunc.St(TP.powerOnRetract_11)
            except:
               if testzone > self.dut.numZones/2:
                  testcyl -= 10
               else:
                  testcyl += 10


#----------------------------------------------------------------------------------------------------------
class CParticleStir(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from Process import CProcess
      self.oProcess = CProcess()

      self.oProcess.St(TP.spinupPrm_1)
      self.oProcess.St(TP.fullStroke_10K_Wr_Sk_Prm_30)       # 10K full pack seeks
      if testSwitch. DoODParticleSweepActions:
         self.oProcess.St(TP.seq_MD_OD_Wr_Sk_Prm_30)         # MD to OD sweep with 2 ms dwell
      self.oProcess.St(TP.seq_MD_ID_Wr_Sk_Prm_30)            # MD to ID sweep with 2 ms dwell


#----------------------------------------------------------------------------------------------------------
class CParticleSweep(CState):
   """
   Perform a particle sweep.  This class can either operation using F3 diags, or using SF3 test
   212.  The default mode is F3, but if the user specifies input parameter 'MODE' as 'SF3', it will
   use T212.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      mode = self.params.get('MODE', 'SF3')
      if mode == 'DIAG':
         from serialScreen import sptDiagCmds
         import sptCmds
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
         oSerial = sptDiagCmds()
         sptCmds.enableDiags()
         oSerial.particleSweep(TP.prm_particleSweep)
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      elif mode == 'SF3':
         changerpm = self.params.get('CHANGERPM', 0)
         if changerpm:
            oBasicSweep = CBasicSweep(self.dut,self.params)
            try:
               objPwrCtrl.powerCycle(set5V=5500, set12V=12000, offTime=10, onTime=10, useESlip=1)
            except:
               objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
            oBasicSweep.changeRPM()
            objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)


         rework = self.params.get('REWORK','NA')

         if rework=='Y' and DriveAttributes.get('PRIME','NA')=='N': # Rework drive
            loopAgi = 5
         else:
            loopAgi = 1 # Prime drive

         #=== Sweep test loop
         from Rim import objRimType
         from Process import CProcess
        
         self.oProc = CProcess()
         for n in xrange(loopAgi):
            objMsg.printMsg("====================== Particle Sweep Test loop %d ========================="%(n+1))
            try:
               self.oProc.St(TP.prm_particleSweep_212)
            except:
               
               if objRimType.IsLowCostSerialRiser():
                  try:
                     objMsg.printMsg('Retry by PowerCycle() with ESlip for fixing EC11049 SP HDSTR')
                     time.sleep(60)
                     objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
                     self.oProc.St(TP.prm_particleSweep_212)
                  except:
                     objMsg.printMsg('Retry again by PowerCycle()with ESlip for fixing EC11049 SP HDSTR')
                     time.sleep(60)
                     objPwrCtrl.powerCycle()
                     self.oProc.St(TP.prm_particleSweep_212)
               else:
                  raise

      else:
         objMsg.printMsg("Improper state parameter 'MODE': %s" % mode)


#----------------------------------------------------------------------------------------------------------
class CSF3ParticleSweep(CState):
   """
   Perform a particle sweep.
   This is the Serial (SF3) implementation of this Class.
   This Class uses T30 and T212 to perform the Particle Sweep
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

      from Process import CProcess
      self.oProc = CProcess()

   #-------------------------------------------------------------------------------------------------------
   def performSweep(self):

      if testSwitch.FE_0111498_399481_NO_T212_IN_PARTICLE_SWEEP:
         objMsg.printMsg("*** Performing Spindown, wait 90s, spinup and T30 Particle Sweep ***")
         self.oProc.St(TP.spindownPrm_2)
         time.sleep(90) # Spin down and wait for 90 seconds to allow Al and SS particles larger than 1um to settle gravitationally.
         self.oProc.St(TP.spinupPrm_1)
         self.oProc.St(TP.seq_MD_ID_Wr_Sk_Prm_30)
      else:
         objMsg.printMsg("*** Performing T212 Particle Sweep ***")
         self.oProc.St(TP.prm_particleSweep_212)

   #-------------------------------------------------------------------------------------------------------
   def fullStrokeSeeks(self):
      objMsg.printMsg("*** Performing T30 Seeks ***")
      self.oProc.St(TP.prm_030_sweep)

   #-------------------------------------------------------------------------------------------------------
   def butterflySeeks(self):
      objMsg.printMsg("*** Performing T30 Butterfly Seeks ***")
      self.oProc.St(TP.prm_030_butterfly_sweep)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      mode        = self.params.get('MODE', None)
      offTime     = self.params.get('OFFTIME', 90)
      onTime      = self.params.get('ONTIME', 30)
      loops       = self.params.get('LOOPS', 0) # default to zero to retain backwards compatibilty

      for mainLoop in range(loops):
         objMsg.printMsg("*** Performing Power Cycle ***")
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
         self.performSweep()
         self.fullStrokeSeeks()
         self.butterflySeeks()

      self.performSweep()
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)


#----------------------------------------------------------------------------------------------------------
class CSweep(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      oSrvSweep = CServoScreen()
      oSrvSweep.servoRetract(TP.prm_025_0125)
      # power cycle 10x
      for i in range(10):
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      # 1/3 stroke sweep in MD
      oSrvSweep.St(TP.prm_030_one_third_sweep)
      # max stroke sweep in MD
      oSrvSweep.St(TP.prm_030_max_sweep)
      # butterfly sweep in ID
      oSrvSweep.St(TP.prm_030_butterfly_sweep)
      # random sweep in ID
      oSrvSweep.St(TP.prm_030_random_sweep)

