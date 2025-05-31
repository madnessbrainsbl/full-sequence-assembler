#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: base Serial FNC states
#
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/12/15 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_FNCTest.py $
# $Revision: #9 $
# $DateTime: 2016/12/15 23:34:49 $
# $Author: weichen.lau $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_FNCTest.py#9 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
from State import CState
import MessageHandler as objMsg
import Utility
from PowerControl import objPwrCtrl
import ScrCmds


#----------------------------------------------------------------------------------------------------------
class CDeltaRSSScreenBase(CState):
   """
      Description: Class that will perform spt based read screens and rss delta parametric failure screening
      Base: N/A
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, depList=[]):
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def CollectDeltaBERdata(self, SERprm, testhd=[], redoErrRateMeasure=2, spcid=2, skipfirst=1):
      from MathLib import stDev_standard, mean

      redoErrRateMeasure += 1
      if len(testhd) > 0:
         loops = len(testhd)
      else:
         loops = 1

      for hd in range(loops):
         if len(testhd) > 0:
            SERprm['TEST_HEAD'] = 0x0101 * (testhd[hd])
         for id in range((100*skipfirst)+spcid, (redoErrRateMeasure*100)+spcid, 100):
            try:
               self.oRdWr.quickSymbolErrorRate(SERprm, flawListMask=0x140, spc_id=id, numRetries=1)
            except:
               pass
         loops -= 1

      # Populate all T250 runs Sova BER into RawSovaErrRate
      RawSovaErrRate = [[[1.0] * self.dut.numZones for i in range(self.dut.imaxHead)] for j in range(redoErrRateMeasure)]
      for k in range(redoErrRateMeasure):
         p250ErrRateTbl = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').chopDbLog('SPC_ID', 'match', str(spcid + k*100))
         for entry in p250ErrRateTbl:
            iZone = int(entry.get('DATA_ZONE'))
            iHead = int(entry.get('HD_LGC_PSN'))
            RawSovaErrRate[k][iHead][iZone] = float(entry.get('RAW_ERROR_RATE'))

      self.meanStdevList = [0.0] * self.dut.imaxHead    # mean of stdev of all valid zones by head
      self.meanDeltaList = [0.0] * self.dut.imaxHead    # mean of max delta of all valid zones by head
      self.countList     = [0]   * self.dut.imaxHead    # no of zones that failed spec by head
      for hd in range(self.dut.imaxHead):
         StdevList = [100.0] * self.dut.numZones   # stdev of each zone of current head
         DeltaList = [100.0] * self.dut.numZones   # max delta of each zone of current head
         for zn in xrange(self.dut.numZones):
            berList = [1.0] * (redoErrRateMeasure)
            ignoredZn = 0
            for k in range(redoErrRateMeasure):
               berList[k] = RawSovaErrRate[k][hd][zn]
               if berList[k] == 1.0:
                  ignoredZn = 1
            if ignoredZn == 1:   # any one data cannot measure, then add to countList, unless all cannot measure
               if max(berList) - min(berList) > TP.HeadInstabilityBySovaErrCountScrnSpec['MIN_DELTA_BER_ZONE']:
                  self.countList[hd] += 1
            else: # add to countList if max delta > MIN_DELTA_BER_ZONE (0.2)
               StdevList[zn] = stDev_standard(berList)
               DeltaList[zn] = max(berList) - min(berList)
               if DeltaList[zn] > TP.HeadInstabilityBySovaErrCountScrnSpec['MIN_DELTA_BER_ZONE']:
                  self.countList[hd] += 1
         StdevListCln = [stdv for stdv in StdevList if stdv != 100.0]
         DeltaListCln = [delta for delta in DeltaList if delta != 100.0]
         self.meanStdevList[hd] = mean(StdevListCln)
         self.meanDeltaList[hd] = mean(DeltaListCln)
         #objMsg.printMsg('DEBUG: meanStdevList[%d] = %f' % (hd,self.meanStdevList[hd]))
         objMsg.printMsg('DEBUG: meanDeltaList[%d] = %f' % (hd,self.meanDeltaList[hd]))
      self.dut.dblData.Tables('DBS_MTRIX_BY_ZONE').deleteIndexRecords(1)
      self.dut.dblData.delTable('DBS_MTRIX_BY_ZONE')

      spcID = 1 + self.dut.stateRerun.get('FAIL',0)
      for hd in xrange(self.dut.imaxHead):
         for zn in xrange(self.dut.numZones):
            berList = [1.0] * redoErrRateMeasure
            for k in xrange(redoErrRateMeasure):
               berList[k] = RawSovaErrRate[k][hd][zn]
            self.dut.dblData.Tables('DBS_MTRIX_BY_ZONE').addRecord({
               'SPC_ID'                      : spcID,
               'OCCURRENCE'                  : self.dut.objSeq.getOccurrence(),
               'SEQ'                         : self.dut.objSeq.curSeq,
               'TEST_SEQ_EVENT'              : self.dut.objSeq.getTestSeqEvent(0),
               'HD_PHYS_PSN'                 : hd,
               'DATA_ZONE'                   : zn,
               'RAW_BER'                     : str(berList),
               'STDEV'                       : stDev_standard(berList),
               'DELTA'                       : max(berList) - min(berList),
               'AVG_STDEV_HD'                : self.meanStdevList[hd],
               'AVG_DELTA_HD'                : self.meanDeltaList[hd],
               'COUNT'                       : self.countList[hd],
               })
      objMsg.printMsg('**SPC_ID32=%d, Table=DBS_MTRIX_BY_ZONE' % (spcID))
      objMsg.printDblogBin(self.dut.dblData.Tables('DBS_MTRIX_BY_ZONE'))

   #-------------------------------------------------------------------------------------------------------
   def RunT163(self):
      if TP.servoErrInstability_163.get('TestZones',[]):
         SetFailSafe()
         self.oRdWr.servoErrorHeadInstabilityByZone(TP.servoErrInstability_163)
         ClearFailSafe()

   #-------------------------------------------------------------------------------------------------------
   def RunT250(self):
      #=== Test250: BER by zone
      self.SERprm = self.oRdWr.oUtility.copy(TP.prm_quickSER_250)
      if testSwitch.FE_0124358_391186_T250_ZONE_SWEEP_RETRIES:
         self.SERprm['ZONE_POSITION'] = 198    #Start at the end of the zone before sweeping zone if necessary
      self.spc_id_used_in_readscrn2 = self.params.get('spc_id', 2) #default is 2

      #if flawListMask=0 for second call then go with 2 retries
      self.oRdWr.quickSymbolErrorRate(self.SERprm, flawListMask=0x140, spc_id=self.spc_id_used_in_readscrn2, numRetries=1)

   #-------------------------------------------------------------------------------------------------------
   def Chk_AVG_BER(self):
      #=== Only update average_err_rate in read screen 2
      try: self.dut.dblData.delTable('P_AVERAGE_ERR_RATE', forceDeleteDblTable = 1)
      except: pass
      param_pass = {
         'AverageQBERLimit' : TP.prm_averageQBER['AverageQBERLimit'],
         'TEST_ZONES'       : range(len(self.SERprm['TEST_ZONES'])),
         'TABLE_OFFS'       : self.t250_index,
      }
      failed_AverageQBERLimit_heads = self.oRdWr.Average_QBER_byZone(param_pass)
      if self.params.get('FAIL_SAFE', 0) == 0 and failed_AverageQBERLimit_heads <> []:
         ScrCmds.raiseException(14612,"Average QBER check failed. failed_list = %s" % str(failed_AverageQBERLimit_heads))

   #-------------------------------------------------------------------------------------------------------
   def Chk_Delta_BER(self):
      try:  # if p_quick_err_rate table for rdscrn1 not found, just ignore delta ber check
         self.oRdWr.checkDeltaBER(self.SERprm)#table = 'P_QUICK_ERR_RATE', metric = 'RRAW' )
      except ScrCmds.CRaiseException, failureData:
         if self.params.get('FAIL_SAFE', 0) == 0 and failureData[0][2] in [14574]:
            raise
         else:
            pass

   #-------------------------------------------------------------------------------------------------------
   def Hd_Instable_Scrn_Sova(self):
      objMsg.printMsg("ENABLE_SCRN_HEAD_INSTABILITY_BY_SOVA_DATA_ERR is enabled.")
      objMsg.printMsg("MIN_ERR_COUNT_REQUIRED = %d" % TP.HeadInstabilityBySovaErrCountScrnSpec['MIN_ERR_COUNT_REQUIRED'])
      objMsg.printMsg("FAIL_ZONES_REQUIRED = %d" % TP.HeadInstabilityBySovaErrCountScrnSpec['FAIL_ZONES_REQUIRED'])
      objMsg.printMsg("MEAN_ERR_COUNT_REQUIRED = %d" % TP.HeadInstabilityBySovaErrCountScrnSpec['MEAN_ERR_COUNT_REQUIRED'])
      try:
         pErrRateTbl = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').chopDbLog('SPC_ID', 'match',str(self.spc_id_used_in_readscrn2))
      except:
         objMsg.printMsg("Failed to read table:P250_ERROR_RATE_BY_ZONE .")
         pass

      from MathLib import mean
      listSovaErrCount = [[0]*self.dut.numZones for hd in xrange(self.dut.imaxHead)]
      for entry in pErrRateTbl:
         iZone = int(entry.get('DATA_ZONE'))
         iHead = int(entry.get('HD_LGC_PSN'))
         listSovaErrCount[iHead][iZone] = int(entry.get('DATA_ERR_CNT'))

      for hd in xrange(self.dut.imaxHead):
         MeanSovaErrCount = mean(listSovaErrCount[hd])
         sortedListSovaErrCount = sorted(listSovaErrCount[hd])
         refErrCount = sortedListSovaErrCount[0 - TP.HeadInstabilityBySovaErrCountScrnSpec['FAIL_ZONES_REQUIRED']]
         objMsg.printMsg("head: %d, MeanSovaErrCount = %d" % (hd, MeanSovaErrCount))
         if self.params.get('FAIL_SAFE', 0) == 0 and MeanSovaErrCount > TP.HeadInstabilityBySovaErrCountScrnSpec['MEAN_ERR_COUNT_REQUIRED'] and \
            refErrCount > TP.HeadInstabilityBySovaErrCountScrnSpec['MIN_ERR_COUNT_REQUIRED']:
            ScrCmds.raiseException(10560, "Head instability check failed, head unstable @ Head : [%s]" % str(hd))

   #-------------------------------------------------------------------------------------------------------
   def Save_T250(self):
      from RdWr import CRdScrn2File
      #=== Save BER data to SIM file
      oRdScrn2File = CRdScrn2File()
      oRdScrn2File.Save_RD_SCRN2_RAW(spcid=self.spc_id_used_in_readscrn2)
      # if testSwitch.virtualRun:
         # objMsg.printMsg("Virtual Execution on... skipping sim reload from disc")
      # else:
         # oRdScrn2File.Retrieve_RD_SCRN2_RAW(dumpData = 1)

   #-------------------------------------------------------------------------------------------------------
   def Delta_VGA(self):
      self.oRdWr.CollectVGA(TP.prm_DeltaVGA,  spc_id=2)
      self.oRdWr.checkDeltaVGA(TP.prm_DeltaVGA)

   #-------------------------------------------------------------------------------------------------------
   def Chk_MR_RST_Delta(self):
      from RdWr import CMrResFile
      if testSwitch.FE_0173493_347506_USE_TEST321 and testSwitch.extern.SFT_TEST_0321:
         oMrRes = CMrResFile(TP.get_MR_Resistance_321, TP.mrDeltaLim)
      else:
         oMrRes = CMrResFile(TP.get_MR_Values_186, TP.mrDeltaLim)

      try:
         oMrRes.diffMRValues()
      except ScrCmds.CRaiseException, (exceptionData):
         if self.params.get('FAIL_SAFE', 0):
            objMsg.printMsg("FailSafe: %s" % (exceptionData))
         else:
            raise

   #-------------------------------------------------------------------------------------------------------
   def Hd_Instable_Scrn_V2(self):
      objMsg.printMsg("ENABLE_DATA_COLLECTION_IN_READSCRN2_FOR_HEAD_INSTABILITY_SCRN is enabled.")
      try:    redoErrRateMeasure = TP.RdScrn2_Retry_with_TSR['Extra_T250']
      except: redoErrRateMeasure = 2
      # CollectDeltaBERdata will populate self.meanStdevList, self.meanDeltaList, self.countList
      self.CollectDeltaBERdata(self.SERprm, redoErrRateMeasure=redoErrRateMeasure, spcid=self.spc_id_used_in_readscrn2)

      fail_stddev = 0
      for hd in range(self.dut.imaxHead):
         if testSwitch.YARRAR and self.meanStdevList[hd] > 0.1:
            fail_stddev = 1

      if fail_stddev:
         self.downGradeOnFly(1, 10560)
         if self.params.get('FAIL_SAFE', 0) == 0 and self.dut.partNum[-3:] not in TP.RetailTabList:
            ScrCmds.raiseException(10560, "Head instability check failed, AVG_STDEV_HD > 0.1" )

      if testSwitch.ENABLE_HEAD_INSTABILITY_SCRN_IN_READSCRN2:
         for hd in range(self.dut.imaxHead):
            if self.params.get('FAIL_SAFE', 0) == 0 and self.meanDeltaList[hd] >= TP.HeadInstabilityBySovaErrCountScrnSpec['MIN_AVG_DELTA_BER_HD'] and \
               self.countList[hd] > TP.HeadInstabilityBySovaErrCountScrnSpec['MIN_FAIL_ZONE_COUNT_HD']:
               ScrCmds.raiseException(10560, "Head instability check failed, head unstable @ Head : [%s]" % str(hd))
   
   #-------------------------------------------------------------------------------------------------------
   def RunScreenOTF(self):
      failOTF = False
      dataFail = [] #empty list
      try:
         t250_table = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').chopDbLog('SPC_ID', 'match', \
            str(self.spc_id_used_in_readscrn2))
         for row in t250_table: #loop throught the 250 table 
            if int(row.get('DATA_ERR_CNT'))> TP.NUM_UDE: 
               failOTF = True
               dataFail.append({'HD': int(row.get('HD_PHYS_PSN')), 'ZN': int(row.get('DATA_ZONE')), 'UDE': int(row.get('DATA_ERR_CNT'))})
      except:
         objMsg.printMsg("Failed to processing table:P250_ERROR_RATE_BY_ZONE for spc id %d" % self.spc_id_used_in_readscrn2)
         pass
      ### print out the hd/zn fail ###
      for data in dataFail:
         objMsg.printMsg("Hd %d, Zn %d, Data Error Count %d" % (data['HD'], data['ZN'], data['UDE']) )
      if self.params.get('FAIL_SAFE', 0) == 0 and failOTF:
         ScrCmds.raiseException(10632, "Too Many Data Error Counts")
      
   #-------------------------------------------------------------------------------------------------------
   def loadActions(self):
      self.actions = {
         'RUN_T163'          : not testSwitch.FE_0121254_357260_SKIP_T163_IN_READ_SCRN,
         'RUN_T250'          : 1,
         'CHK_AVG_BER'       : testSwitch.CheckAverageQBER_Enabled,
         'CHK_DELTA_BER'     : not testSwitch.DeltaBER_Disabled,
         'HD_INSTB_SCRN_SOVA': testSwitch.ENABLE_SCRN_HEAD_INSTABILITY_BY_SOVA_DATA_ERR,
         'HD_INSTB_SCRN_V2'  : testSwitch.ENABLE_DATA_COLLECTION_IN_READSCRN2_FOR_HEAD_INSTABILITY_SCRN or \
                                 testSwitch.ENABLE_THERMAL_SHOCK_RECOVERY_V2,
         'SAVE_T250'         : testSwitch.EnableT250DataSavingToSIM,
         'DELTA_VGA'         : testSwitch.DeltaVGA_Enabled,
         'CHK_MR_RST_DELTA'  : 1,
         'RUN_SKIPWRITE_SCRN': testSwitch.RUN_SKIPWRITE_SCRN,
      }

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from RdWr import CRdWrScreen
      self.oRdWr = CRdWrScreen()

      self.loadActions() #load modules to be run
      self.actions.update(self.params)#update the modules to be run by the params

      try: self.t250_index = len(self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').tableDataObj())
      except: self.t250_index = 0
      if testSwitch.virtualRun: self.t250_index = 0

      if testSwitch.FE_0149136_409401_P_DELTA_BER_IMPROVEMENT:
         #=== Retrieve Data
         objMsg.printMsg('Read BER from Disc')
         from BER_SIM import CBERFile
         oBER = CBERFile()
         oBER.readFromDrive()

      if self.actions.get('RUN_T163', False):
         self.RunT163()

      if self.actions.get('RUN_T250', False):
         self.RunT250()

      if self.actions.get('SCREEN_OTF', False):
         self.RunScreenOTF()
      
      if self.actions.get('CHK_AVG_BER', False):
         self.Chk_AVG_BER()

      if self.actions.get('CHK_DELTA_BER', False):
         self.Chk_Delta_BER()

      if not testSwitch.FE_0149136_409401_P_DELTA_BER_IMPROVEMENT:
         if self.dut.driveattr.get('ST240_PROC', 'N') == 'C' and self.dut.nextOper == 'FNC':
            return

      if self.actions.get('HD_INSTB_SCRN_SOVA', False):
         self.Hd_Instable_Scrn_Sova()

      if self.actions.get('HD_INSTB_SCRN_V2', False):
         self.Hd_Instable_Scrn_V2()

      if self.actions.get('SAVE_T250', False):
         self.Save_T250()

      if self.actions.get('DELTA_VGA', False):
         self.Delta_VGA()

      #=== Perform MR resistance delta check
      if self.actions.get('CHK_MR_RST_DELTA', False):
         self.Chk_MR_RST_Delta()


#----------------------------------------------------------------------------------------------------------
#CDeltaRSSScreen defined as template, can be overrided by in the serialTest
class CDeltaRSSScreen(CDeltaRSSScreenBase):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CDeltaRSSScreenBase.__init__(self, dut, depList)

#----------------------------------------------------------------------------------------------------------
class CGTWrite(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from FSO import CFSO
      from Servo import CServoFunc
      
      self.oFSO = CFSO()
      self.oSrvFunc = CServoFunc()
      
      objMsg.printMsg("numZones %s imaxHead %s" % (self.dut.numZones, self.dut.imaxHead))
      self.oFSO.getZnTblInfo(spc_id = 1, supressOutput = 0)
      self.oFSO.St(TP.PRM_DISPLAY_HEAD_TPI_CONFIG_172)
      objMsg.printMsg("sysZn %s" % (self.oFSO.findSysAreaClosestDataZone()))
      ShiftZone = self.getShiftZn()
      self.rdOClim()
      
      SetFailSafe()
      if TP.Display_BER:
         for hd in range(self.dut.imaxHead):
            self.runT250(hd, range(ShiftZone[hd]), IDtoOD = 0, spcid = 0)   # od to id
            if ShiftZone[hd] != self.dut.numZones - 1:
               self.runT250(hd, range(ShiftZone[hd], self.dut.numZones-1, 1), IDtoOD = 1, spcid = 0)   # id to od
            self.runT250(hd, [self.dut.numZones-1], IDtoOD = 0, spcid = 0)   # od to id
            
      self.oFSO.St(TP.prm_GTWrite)
      self.rdOClim()
      
      if TP.Display_BER:
         for hd in range(self.dut.imaxHead):
            self.runT250(hd, range(ShiftZone[hd]), IDtoOD = 0, spcid = 1)   # od to id
            if ShiftZone[hd] != self.dut.numZones - 1:
               self.runT250(hd, range(ShiftZone[hd], self.dut.numZones-1, 1), IDtoOD = 1, spcid = 1)   # id to od
            self.runT250(hd, [self.dut.numZones-1], IDtoOD = 0, spcid = 1)   # od to id
      ClearFailSafe()
      
   def runT250(self, hd, testZoneList=[], IDtoOD = 0, spcid = 0):
      oUtility = Utility.CUtility()
      prm_ber250 = TP.prm_onTrkber250.copy()  # READ_SCRN2
      prm_ber250.update({'spc_id': spcid})
      prm_ber250.update({'TEST_HEAD': hd<<8 | hd})      
      if IDtoOD == 1:
         prm_ber250.update({'ZONE_POSITION': 200})
         
      MaskList = oUtility.convertListToZoneBankMasks(testZoneList)
      objMsg.printMsg("MaskList = %s" % MaskList)
      for bank,list in MaskList.iteritems():
         if list:
            objMsg.printMsg("list = %s" % list)
            prm_ber250['ZONE_MASK_EXT'], prm_ber250['ZONE_MASK'] = oUtility.convertListTo64BitMask(list)
            if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
               prm_ber250['ZONE_MASK_BANK'] = bank
            objMsg.printMsg("prm_ber250 = %s" % prm_ber250)
            try: self.oFSO.St(prm_ber250)
            except: pass
            
   def getShiftZn(self):
      ShiftZone = [self.dut.numZones - 1 for hd in xrange(self.dut.imaxHead)]
      CFtable = self.dut.dblData.Tables('P172_HEAD_TPI_CONFIG_TBL').tableDataObj()
      for hd in range(self.dut.imaxHead):
         for rec in CFtable:
            head = int(rec['HD_LGC_PSN'])
            zone = int(rec['DATA_ZONE'])
            direction = int(rec['DIRECTION'])
            if (direction != 0):
               if head == hd:
                  ShiftZone[hd] = zone
                  break               
      objMsg.printMsg("ShiftZone %s" % (ShiftZone))
      return ShiftZone
   
   def rdOClim(self):
      self.currOClim = []
      for head in range(self.dut.imaxHead):
         self.currOClim.append(self.oSrvFunc.getwriteOCLIM_byHead(head))
      objMsg.printMsg("After test: OCLIM = %s " %(self.currOClim))
      
#----------------------------------------------------------------------------------------------------------
class CVarSpares(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from FSO import CFSO
      from MediaScan import CUserFlaw

      self.oFSO = CFSO()
      self.objFs = CUserFlaw()

      if not testSwitch.FE_0269922_348085_P_SIGMUND_IN_FACTORY:
         from bpiFile import CBpiFile
         self.obpiFile = CBpiFile()
         
      self.numUserZones   = self.dut.numZones
      objMsg.printMsg("numZones %s imaxHead %s" % (self.dut.numZones, self.dut.imaxHead))
      
      # power loss recovery handling
      objMsg.printMsg("powerLossEvent %s powerLossState %s" % (self.dut.powerLossEvent, self.dut.powerLossState))
      if self.dut.powerLossEvent and (self.dut.powerLossState == 'VAR_SPARES'):
         objMsg.printMsg("Power loss recovery at %s" % self.dut.nextState)
         self.DeleteDblTable()
         self.runWRGapCal()
         self.runRdOpti()
         self.regenerate_PList()
      else:
         objMsg.printMsg("No power loss detected at %s" % self.dut.nextState)
   
      self.DeleteDblTable()
      self.oFSO.getZnTblInfo(spc_id = 1, supressOutput = 0)
      zstable = self.dut.dblData.Tables(TP.zone_table['table_name']).tableDataObj()
      #self.dumpDefectSummaryInfo()
      self.oFSO.St(TP.prm_rap_tuned_param_172,  spc_id = 1)
      
      # get total slips
      self.oFSO.St(TP.prm_107_DEFECT_LIST_SUMMARY)
      if not testSwitch.virtualRun:
         TotalSlips  = int(self.dut.objSeq.SuprsDblObject['P2109_DEFECT_LIST_SUMMARY'][-1]['TOTAL_SLIPS'])
         objMsg.printMsg("TotalSlips: %s" % TotalSlips)
      
      # calc min spare
      self.ChkSpareAval(spcid = 1000)
      try:
         sparetable = self.dut.dblData.Tables('P130_SLIP_SCTR_CNT2').tableDataObj()
      except:
         objMsg.printMsg('Cannot Access P130_SLIP_SCTR_CNT2 table')
         return 0
         
      maxLBA      = int(self.oFSO.dth.getRowFromTable_byTable(sparetable)['MAX_LBA_IN_LIST'])
      availSpares = int(self.oFSO.dth.getRowFromTable_byTable(sparetable)['AVAIL_SPARES'])
      extraPBA    = int(self.oFSO.dth.getRowFromTable_byTable(sparetable)['MAX_SCTR_SPARES'])
      
      import WaterfallNiblets
      sectorSize = int(self.dut.Drv_Sector_Size)
      objMsg.printMsg("Drv_Sector_Size %d" % sectorSize)
      objMsg.printMsg("MC_SIZE %s" % WaterfallNiblets.MC_SIZE)
         
      if testSwitch.SPLIT_VBAR_FOR_CM_LA_REDUCTION:
         from WTF_Tools import CWTF_Tools
         oWaterfall = CWTF_Tools()
      else:
         from base_SerialTest import CWaterfallTest
         oWaterfall = CWaterfallTest(self.dut)
      oWaterfall.buildClusterList()
      objMsg.printMsg("TP.VbarPartNumCluster %s" % TP.VbarPartNumCluster)
      objMsg.printMsg("TP.VbarNibletCluster %s" % TP.VbarNibletCluster)
      objMsg.printMsg("VbarNibletCluster %s" % oWaterfall.VbarNibletCluster)
      objMsg.printMsg("MEDIA_CACHE_CAPACITY %s" % TP.VbarNibletCluster[0]['MEDIA_CACHE_CAPACITY'])
      
      if TP.T230_NativeOnly:         
         objMsg.printMsg("NATIVE_DRV %s" % (TP.VbarNibletCluster[0]['NATIVE_DRV']))
         if TP.VbarNibletCluster[0]['NATIVE_DRV'] == 0:
            objMsg.printMsg('Non native drive: skip spare adjust')
            return
         
      # retrieve MC zone
      if testSwitch.FE_0385234_356688_P_MULTI_ID_UMP:
         mediaCacheZone = TP.MC_ZONE
      else:
         if testSwitch.ADAPTIVE_GUARD_BAND :
            mediaCacheZone = range(1,min(TP.UMP_ZONE[self.numUserZones]),1) # start from 1 as the zone 0 is AGB zone
         else:
            mediaCacheZone = range(0,min(TP.UMP_ZONE[self.numUserZones]),1)
      objMsg.printMsg('mediaCacheZone: %s' % (str(mediaCacheZone)))
         
      TotalDrvSector      = 0
      TotalMCSP2SecPerTrk = 0
      Total_2SectorPerTrk = 0
      ZnSector            = [0,] * (self.dut.imaxHead * self.numUserZones)
      for rec in zstable:
         hd = int(rec['HD_LGC_PSN'])
         zn = int(rec['DATA_ZONE'])
         ZnSector[(hd * self.numUserZones) + zn] += int(rec[TP.zone_table['trk_name']]) * int(rec['TRK_NUM'])
            
         TotalDrvSector += int(rec[TP.zone_table['trk_name']]) * int(rec['TRK_NUM'])
         Total_2SectorPerTrk += 2 * int(rec['TRK_NUM'])
         if zn in mediaCacheZone:
            TotalMCSP2SecPerTrk += 2 * int(rec['TRK_NUM'])
            
      objMsg.printMsg("ZnSector: %s" % ZnSector)
      objMsg.printMsg("TotalMCSP2SecPerTrk: %s" % TotalMCSP2SecPerTrk)
      objMsg.printMsg("Total_2_sector_per_trk: %s" % Total_2SectorPerTrk)
      objMsg.printMsg("Total_drv_sector: %s" % TotalDrvSector)
      
      # calc AGB sector
      AGBSector = 0
      if testSwitch.ADAPTIVE_GUARD_BAND:
         for hd in range(self.dut.imaxHead):
            for zn in [0]:
               AGBSector += ZnSector[(hd * self.numUserZones) + zn]
               
      # calc MC total sector
      TotalMCznSector = 0
      TotalMCSectorsPerHead = []
      for hd in range(self.dut.imaxHead):
         TotalMCSectorsPerHead.append(sum([ZnSector[(hd * self.numUserZones) + zn] for zn in mediaCacheZone]))
      TotalMCznSector = min(TotalMCSectorsPerHead) * self.dut.imaxHead
      objMsg.printMsg("Total_MC_zone_sector %d" % TotalMCznSector)
      
      TargetMC          = TP.VbarNibletCluster[0]['MEDIA_CACHE_CAPACITY']
      TargetMCSector    = int(TargetMC * float(1e9)/sectorSize)
      objMsg.printMsg("TargetMC %f TargetMCSector %d" % (TargetMC, TargetMCSector))
      objMsg.printMsg("PBA_TO_LBA_SCALER %f" % TP.VbarNibletCluster[0]['PBA_TO_LBA_SCALER'])
      
      # re-assignment and slip margin definition
      SEDSector       = 86789
      TotalLBAs       = maxLBA + SEDSector
      ReassignReserve = int(TotalLBAs*0.001)
      TotalSlipsDelta = 0 #int(TotalLBAs*0.0006)    # WA for total slips delta observed btw FNC2 and quick format
      SlipMargin      = int(TotalSlips*0.008)
      if SlipMargin < 1000:
         SlipMargin = 1000
      objMsg.printMsg("TotalLBAs %s SEDSector %s maxLBA %s" % (TotalLBAs, SEDSector, maxLBA))
      objMsg.printMsg("0.1PercentofTotalLBAs %s TotalSlipsDelta %s SlipMargin %s" % (ReassignReserve, TotalSlipsDelta, SlipMargin))
      
      # assign lower and upper spec
      if TotalMCznSector < TargetMCSector:
         FinalMCSector = TotalMCznSector
      else:
         FinalMCSector = TargetMCSector
         
      MCSPSector = 2 * int(FinalMCSector/210)
      deltaMCSPsector = 0
      if MCSPSector > TotalMCSP2SecPerTrk:
         deltaMCSPsector = MCSPSector - TotalMCSP2SecPerTrk
      objMsg.printMsg("FinalMCSector %s MCSPSector %s deltaMCSPsector %s" % (FinalMCSector, MCSPSector, deltaMCSPsector))
      
      # (0.1% reserve for re-assignment + slip margin + SEDSector + MC + delta MC SP + TotalSlipsDelta) ->in sector
      minSpareNeed = ReassignReserve + SlipMargin + SEDSector + FinalMCSector + deltaMCSPsector + TotalSlipsDelta
      BPIsparesLimit = minSpareNeed + int(TotalLBAs*0.019)                 # + (1.9% reserve for serialFormat) ->in sector
      objMsg.printMsg("minSpareNeed %s BPIsparesLimit %s" % (minSpareNeed, BPIsparesLimit))
      
      prm_VarSpares = TP.prm_230_VarSpares.copy()
      
      # update spec if needed
      if TP.T230_Tighten:
         lowByteMinSpareNeed  = minSpareNeed & 0xffff
         highByteMinSpareNeed = (minSpareNeed >> 16)& 0xffff
         prm_VarSpares.update({'AVAILABLE_SPARES':(highByteMinSpareNeed, lowByteMinSpareNeed)})
      if TP.T230_Relax:
         lowBPIsparesLimit  = BPIsparesLimit & 0xffff
         highBPIsparesLimit = (BPIsparesLimit >> 16)& 0xffff
         prm_VarSpares.update({'DELTA_LIMIT_32':(highBPIsparesLimit, lowBPIsparesLimit)})
      prm_VarSpares.update({'timeout':90 * self.dut.imaxHead * self.numUserZones})
         
      # run variable spare
      if testSwitch.FE_0269922_348085_P_SIGMUND_IN_FACTORY:
         self.oFSO.St(prm_VarSpares,  spc_id = 1)
      else:
         self.oFSO.St(prm_VarSpares,  spc_id = 1, dlfile = (CN, self.obpiFile.bpiFileName))
         
      #=== Save RAP and SAP to flash
      self.oFSO.St({'test_num': 178, 'prm_name': 'prm_178_Save_RAP_and_SAP_to_flash', 'timeout': 1200, 'spc_id': 0, 'CWORD1':0x0620})      
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      self.oFSO.St(TP.spinupPrm_1)
      self.oFSO.St(TP.prm_rap_tuned_param_172,  spc_id = 2)
      self.oFSO.getZnTblInfo(spc_id = 1, supressOutput = 0)
      
      totalBPIChg = 1
      avgBPIChg   = -1
      BpiRevert   = 1
      try:
         finaltable  = self.dut.dblData.Tables('P230_VAR_SPARE_ALLOC').tableDataObj()
         totalBPIChg = int(self.oFSO.dth.getRowFromTable_byTable(finaltable)['TOTAL_NUM_BPI_CHG'])
         avgBPIChg   = float(self.oFSO.dth.getRowFromTable_byTable(finaltable)['AVG_BPI_DELTA_ADJ'])
         Reverttable = self.dut.dblData.Tables('P230_BPI_REVERT_SUMMARY').tableDataObj()
         BpiRevert   = int(self.oFSO.dth.getRowFromTable_byTable(Reverttable)['NUM_ZONE_BPI_REVERT'])         
      except:
         pass
      objMsg.printMsg("Total BPI change %s avgBPIChg %s numZonesBpiRevert %s" % (totalBPIChg, avgBPIChg, BpiRevert))
      
      if totalBPIChg != 0 or (testSwitch.FE_0349420_356688_P_ENABLE_OPTI and avgBPIChg != -1) or BpiRevert != 0:  # BPI changed/avgBPIChg/BPI revert, need re-cal and regenerate PList
         self.runWRGapCal()
         self.runRdOpti()
         self.regenerate_PList()
         self.oFSO.St(TP.prm_107_DEFECT_LIST_SUMMARY)
         # remove slip margin
         if TP.T230_Tighten:
            lowByteMinSpareNeed  = (minSpareNeed - SlipMargin) & 0xffff
            highByteMinSpareNeed = ((minSpareNeed - SlipMargin) >> 16)& 0xffff
            prm_VarSpares.update({'AVAILABLE_SPARES':(highByteMinSpareNeed, lowByteMinSpareNeed)})
         if TP.T230_Relax:
            lowBPIsparesLimit  = (BPIsparesLimit - SlipMargin) & 0xffff
            highBPIsparesLimit = ((BPIsparesLimit - SlipMargin) >> 16)& 0xffff
            prm_VarSpares.update({'DELTA_LIMIT_32':(highBPIsparesLimit, lowBPIsparesLimit)})
         self.ChkSpareAval(prm_VarSpares['AVAILABLE_SPARES'], prm_VarSpares['DELTA_LIMIT_32'], spcid = 2000)
            
      if testSwitch.FE_0269922_348085_P_SIGMUND_IN_FACTORY:
         self.oFSO.St({'test_num':210, 'prm_name':'prm_vbar_formats_210', 'CWORD1': 0x0100, 'CWORD2': 0x0001, 'timeout': 60, 'spc_id': 0})
      else:
         self.oFSO.St({'test_num':210, 'prm_name':'prm_vbar_formats_210', 'CWORD1': 0x0100, 'CWORD2': 0x0001, 'dlfile' : (CN, self.obpiFile.bpiFileName), 'timeout': 60, 'spc_id': 0})
         
      if (TP.prm_230_VarSpares['CWORD1'] & 0x0100):    # FailBER
         failcode = 0
         failEC = [10632]
         try:
            failcode = int(self.oFSO.dth.getRowFromTable_byTable(finaltable)['FAIL_CODE'])
            objMsg.printMsg("failcode: %s" % failcode)
         except:
            pass
            
         if failcode in failEC:
            ScrCmds.raiseException(10632, "Minimum Error rate not met")

      self.oFSO.St(TP.prm_rap_tuned_param_172,  spc_id = 3)
            
   #----------------------------------------------------------------------------------------------------
   def ChkSpareAval(self, minSpare = 0, maxSpare = 0, spcid = 0):
      prm_ChkSpareAval = TP.prm_230_ChkSpareAval.copy()
      prm_ChkSpareAval.update({'SUPERPARITY_PER_TRK': TP.prm_230_VarSpares['SUPERPARITY_PER_TRK']})
      
      if spcid == 2000:
         prm_ChkSpareAval.update({'DEBUG_PRINT': prm_ChkSpareAval['DEBUG_PRINT'] | 0x08})
         prm_ChkSpareAval.update({'AVAILABLE_SPARES': minSpare})
         prm_ChkSpareAval.update({'DELTA_LIMIT_32': maxSpare})
         
      if testSwitch.FE_0269922_348085_P_SIGMUND_IN_FACTORY:
         self.oFSO.St(prm_ChkSpareAval,  spc_id = spcid)
      else:
         self.oFSO.St(prm_ChkSpareAval,  spc_id = spcid, dlfile = (CN, self.obpiFile.bpiFileName))
         
   #----------------------------------------------------------------------------------------------------
   def DeleteDblTable(self):
      if not testSwitch.virtualRun:
         for table in ['P230_VAR_SPARE_ALLOC', 'P130_SLIP_SCTR_CNT2', TP.zone_table['table_name'], 'P210_VBAR_FORMATS', TP.zoned_servo_zn_tbl['table_name'], 'P2109_DEFECT_LIST_SUMMARY', 'P230_BPI_REVERT_SUMMARY']:
            try:
               self.dut.dblData.Tables(table).deleteIndexRecords(1)
               self.dut.dblData.delTable(table, forceDeleteDblTable = 1)
            except: pass
            
   #----------------------------------------------------------------------------------------------------
   def runWRGapCal(self):
      if not testSwitch.FE_0269922_348085_P_SIGMUND_IN_FACTORY and (TP.prm_230_VarSpares['CWORD1'] & 0x0008 == 0):  # didn't run at T230, so need to cal T176
         from RdWr import CRdWrOpti
         oRdWr = CRdWrOpti()
         oUtility = Utility.CUtility()
         rwgapParams = oUtility.copy(TP.Writer_Reader_Gap_Calib_176)
         rwgapParams['CWORD1'] = rwgapParams['CWORD1']|0x0002 # skipsyszone
         rwgapParams['spc_id'] = 0
         T176updateParams = oUtility.copy(TP.prm_176_update)
         
         BPIChanged = 0
         try:
            BPIChanged = self.dut.dblData.Tables('P210_VBAR_FORMATS').tableDataObj()
         except:
            objMsg.printMsg('Cannot Access P210_VBAR_FORMATS table')
            pass
            
         if (BPIChanged):
            for hd in range(self.dut.imaxHead):
               for rec in BPIChanged:
                  head = int(rec['HD_LGC_PSN'])
                  if head == hd:
                     rwgapParams.update({'HEAD_RANGE': (oUtility.converttoHeadRangeMask(hd, hd),)})
                     objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
                     self.oFSO.St(TP.spinupPrm_1)
                     T176updateParams.update({'HEAD_RANGE': (oUtility.converttoHeadRangeMask(hd, hd),)})
                     self.oFSO.St(T176updateParams, dlfile = (CN, self.obpiFile.bpiFileName))   # RAP_REVERT | NO_UPDATE_RZ
                     oRdWr.Writer_Reader_Gap_Calib(rwgapParams, zapFromDut = 0)
                     break
         else:
            self.oFSO.St(TP.prm_176_update, dlfile = (CN, self.obpiFile.bpiFileName))   # RAP_REVERT | NO_UPDATE_RZ
            oRdWr.Writer_Reader_Gap_Calib(rwgapParams, zapFromDut = 0)
            
   #----------------------------------------------------------------------------------------------------
   def runRdOpti(self):
      from Opti_Read import CRdOpti
      CRdOpti(self.dut, {'ZONES':range(self.numUserZones)}).run()  # re-cal T251 and run T250
      
   #----------------------------------------------------------------------------------------------------
   def regenerate_PList(self):
      self.oFSO.St(TP.prm_init_plist_149)
      self.objFs.repPList()
      self.objFs.repdbi()
      self.oFSO.St(TP.prm_DBI_Fail_Limits_140)
      self.oFSO.St(TP.prm_write_plist_149)
      self.oFSO.St(TP.prm_write_SFT_plist_149)
      self.objFs.repPList()
      self.runScratchFill()
      self.dumpDefectSummaryInfo()
         
   #----------------------------------------------------------------------------------------------------
   def runScratchFill(self):
      self.oFSO.St(TP.prm_scratch_fill_117_1) # this runs the media damage screens
      self.oFSO.St(TP.prm_118_rev2_long002)
      self.oFSO.St(TP.prm_118_rev2_radial002)
      self.oFSO.St(TP.prm_118_rev2_short002)
      self.oFSO.St(TP.prm_118_rev2_unvisited002)
      self.oFSO.St(TP.prm_118_sort_fill_def_list)
      if testSwitch.FE_0137096_342029_P_T64_SUPPORT:
         self.oFSO.St(TP.prm_64_isolated_servo_pad) # Isolated Servo Padding (Data Padding)
      self.filterExcessiveScratchesInMovingWindow()

   #----------------------------------------------------------------------------------------------------
   def filterExcessiveScratchesInMovingWindow(self):
      try:
         data = self.dut.dblData.Tables('P117_MEDIA_SCREEN').tableDataObj()
         self.dut.dblData.Tables('P117_MEDIA_SCREEN').deleteIndexRecords(confirmDelete=1)
         self.dut.dblData.delTable('P117_MEDIA_SCREEN')
      except:         
         objMsg.printMsg('Cannot Access P117_MEDIA_SCREEN table')
         return

      try:
         ScratchLength = TP.prm_filterExcessiveScratches['SCRATCH_LENGTH']
         NumScratches = TP.prm_filterExcessiveScratches['NUM_SCRATCHES']
         TrkWindow = TP.prm_filterExcessiveScratches['TRK_WINDOW']
      except:         
         objMsg.printMsg('prm_filterExcessiveScratches input not defined')
         return

      try:
         Scratches = {}
         for entry in data:
            if int(entry['SCRATCH_LENGTH']) > ScratchLength:
               head = int(entry['HD_PHYS_PSN'])
               beginning_trk = int( entry['BEGINNING_TRK'])
               scratch_length = int( entry['SCRATCH_LENGTH'])

               if Scratches.has_key( head ):
                  Scratches[head].append([beginning_trk, scratch_length])
               else:
                  Scratches[head] = [[beginning_trk, scratch_length]]

         for key in Scratches.keys():
            Scratches[key].sort()
      except:         
         objMsg.printMsg('Not filtering for excessive scratches in P117_MEDIA_SCREEN')
         return

      objMsg.printMsg("Filtering drives with more than %d" % NumScratches + " scratches longer than %d" % ScratchLength + " within a %d" % TrkWindow + " track window in P117_MEDIA_SCREEN")
      for key in Scratches:
         ScratchesList = Scratches[key]
         for item in ScratchesList:
            # Perform the check once we can look at "NumScratches" scratches at once
            # Then, if the track numbers for scratches that are longer than "ScratchLength" length are within
            #   the "TrkWindow" window, then there are too many scratches within the window.
            if ScratchesList.index(item) >= (NumScratches - 1):
               EndingTrk = ScratchesList[ScratchesList.index(item)][0]
               BeginningTrk = ScratchesList[ScratchesList.index(item) - NumScratches - 1][0]
               if (EndingTrk - BeginningTrk ) < TrkWindow:
                  ScrCmds.raiseException(10304,"Too many scratches within a given window in P117_MEDIA_SCREEN") #10304 = MEDIA_DAMAGE_FAILURE in codes.h
         
   #----------------------------------------------------------------------------------------------------
   def dumpDefectSummaryInfo(self):
      try:
         #don't clog hdstr results since we can dump after fs
         if testSwitch.FE_0131622_357552_USE_T126_REPSLFAW_INSTEAD_OF_T130:
            #Use unique spc_id for last Servo Flaw dump
            self.oFSO.St(TP.prm_126_read_sft_oracle, spc_id=1000) #report servo flaw table
         else:
            self.objFs.repServoFlaws()
         self.objFs.repdbi()   # dump db log to host (result file)
         self.objFs.repPList() # dump p-list to host (result file)
         try:
            if DriveAttributes.get('DISC_1_LOT','NONE')[0]=='P':
               self.oFSO.St(TP.prm_107_aperio)
            if testSwitch.checkMediaFlip:
               DISC_FLIP_VALUE = 'PW00000000000'
               if DriveAttributes.get('DISC_1_LOT','NONE')[0:13] == DISC_FLIP_VALUE or DriveAttributes.get('DISC_2_LOT','NONE')[0:13] == DISC_FLIP_VALUE or DriveAttributes.get('DISC_3_LOT','NONE')[0:13] == DISC_FLIP_VALUE:
                  objMsg.printMsg('========= Media Flip Screen (T107)=========')
                  P107VerifyFlaws = self.dut.dblData.Tables('P107_VERIFIED_FLAWS').tableDataObj()
                  for i in xrange(len(P107VerifyFlaws)):
                     objMsg.printMsg('Head %s : VRFD_FLAWS = %d'%(P107VerifyFlaws[i]['HD_LGC_PSN'],int(P107VerifyFlaws[i]['VRFD_FLAWS'])))
                     if int(P107VerifyFlaws[i]['VRFD_FLAWS']) > TP.specVerFlaws:
                        ScrCmds.raiseException(49999, "This Drive is Media Flip and Drive failed with TA_CNT and VRFD_FLAWS more than spec")
                  objMsg.printMsg('=====================================')
         except:
            pass
      except FOFSerialTestTimeout:
         #Ignore FOFSerialTestTimeout's
         pass
      
#-------------------------------------------------------------------------------------------------------
class CSAMTOL(CState):
   """
   Enable SAMTOL
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from FSO import CFSO
      from Servo import CServoFunc

      self.oFSO = CFSO()
      self.oSrvFunc = CServoFunc()

      SAMTOL_index = 42   #symbol table entry 302, offset 21, set bit 12 -- offset = 21*2

      samtolAddress = self.oSrvFunc.readServoSymbolTable(['SAMTOL_SYMBOL_OFFSET',],self.oSrvFunc.ReadPVDDataPrm_11, self.oSrvFunc.getServoSymbolPrm_11, self.oSrvFunc.getSymbolViaAddrPrm_11)
      if samtolAddress != 0xFFFF:
         prm1 = TP.prm_011_TimingMarkEnable
         START_ADDRESS = self.oFSO.oUtility.ReturnTestCylWord(samtolAddress + TP.SAMTOL_index)
         prm1['START_ADDRESS'] = START_ADDRESS
         self.oFSO.St(prm1)
         self.oFSO.saveSAPtoFLASH()
      else:
         objMsg.printMsg('SAMTOL NOT SUPPORTED BY SERVO - NOT ENABLING')


#----------------------------------------------------------------------------------------------------------
class CSequentialStCmds(CState):
   """
      Takes a list of st parameter dictionaries [{},{},...]
      and executes them in order.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from Process import CProcess
      oProcess = CProcess()

      def cleanRetrieve(paramName):
         val = self.params.get(paramName,None)
         if not val == None:
            val = eval(val)
         return val

      StCmdList = cleanRetrieve('StCmdList')
      for StCmd in StCmdList:
         oProcess.St(StCmd)


#----------------------------------------------------------------------------------------------------------
class CSetCustomerOCLIM(CState):
   """
   Set oclim on all heads
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if testSwitch.FE_0243459_348085_DUAL_OCLIM_CUSTOMER_CERT == 1:
         if self.dut.nextOper in ['CRT2'] and self.dut.nextState in ['SET_CUST_OCLIM'] and self.dut.BG not in ['SBS']:
            return
         from Servo import CServoFunc
         oSrvFunc = CServoFunc()
         oSrvFunc.setOClim({},TP.defaultOCLIM_customer,updateFlash = 1)

#----------------------------------------------------------------------------------------------------------
class CDisplayOCLIM(CState):
   """
   Display OCLim
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if self.dut.BG not in ['SBS']: 
         return
      import traceback
      from Process import CProcess
      sapOffset = TP.oclimSAPOffset
      try:
         # Read 16bit locations from the SAP--OCLIMs for all heads
         CProcess().St({'test_num':11, 'CWORD1':0x200, 'SYM_OFFSET':sapOffset, 'NUM_LOCS':self.dut.imaxHead-1,})
      except:
         objPwrCtrl.powerCycle(useESlip=1)

#----------------------------------------------------------------------------------------------------------
class CMfgDateToETF(CState):
   """
      Write post-Flawscan manufacturing date to Drive Information File in ETF. Also transfers
      DriveSN and WWN from CAP to ETF. The specfic format T149 writes is required by SAS customers.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):

      if not testSwitch.FE_0133958_357552_T149_MFGDATE_TO_ETF:
         objMsg.printMsg("FE_0133958_357552_T149_MFGDATE_TO_ETF flag disabled - skip this state")
         return

      def getDateStr():
         """Get time, swap format"""
         if testSwitch.virtualRun == 1:
            return "07252010"  #Const string for VE bin compare
         else:
            import time
            year, month, day = time.localtime()[:3]
            return  "%02d%02d%04d" %(month, day, year)

      def getDifInfo():
         """Read up a binary file from CM, and return chars at specific locations"""
         from FSO import CBinAsciiFileIO
         oBAIO = CBinAsciiFileIO('filedata') #instantiate with name of folder under pcfiles

         etf_driveSN = oBAIO.readBin2Chars(8,8).upper()
         etf_mfgDate = oBAIO.readBin2Chars(16,8)
         etf_WWN = oBAIO.readBin2Hex(62,8).upper() #read 16 nibbles of hex numbers

         objMsg.printMsg("Read from binary file: DriveSN: %s" %etf_driveSN)
         objMsg.printMsg("Read from binary file: Mfg Date: %s" %etf_mfgDate)
         objMsg.printMsg("Read from binary file: WWN: %s" %etf_WWN)

         return (etf_driveSN, etf_mfgDate, etf_WWN)


      from Proces import CProcess
      oProc = CProcess()

      #Get the before date string, just in case it is 1 sec. before midnight
      dateStrList = [getDateStr()]

      #All this try/except stuff can be removed when SPT fix implemented for T149 EC10399 readback failure
      try:
         oProc.St(TP.prm_149_Wwn2Etf) #writes driveSN, WWN, mfg date to ETF

      except ScriptTestFailure, (failureData):
         print("In exception ScriptTestFailure")
         if failureData[0][2] in [10399]:  #Drv CPF-Read after Write Failure
            #If it was a EC10399 failure, go verify data written correctly.
            oProc.St(TP.prm_130_readDIF)

            dateStrList.append(getDateStr())

            etf_driveSN, etf_mfgDate, etf_WWN = getDifInfo()

            #Funkiness here because drives may be reprocessed SATA->SAS, without removing old attribute.
            #  Need to rely on interface testing to ensure WWN in CAP is correct.
            wwn_inFIS = etf_WWN in [self.dut.driveattr.get('WW_SATA_ID',''),self.dut.driveattr.get('WW_SAS_ID','')]

            if etf_mfgDate not in dateStrList or etf_driveSN != self.dut.serialnum or not wwn_inFIS:
               objMsg.printMsg("\nFailed attribute check. Current attributes are:")
               objMsg.printMsg("DriveSN attribute: %s" %self.dut.serialnum)
               objMsg.printMsg("Before and After Dates: %s" %dateStrList)
               objMsg.printMsg("WWN attribute: %s" %wwn_inFIS)
               ScrCmds.raiseException(11044, "DIF file does not match actual drive attributes")

         else:
            raise

#----------------------------------------------------------------------------------------------------------
class CGetPartialLog(CState):
   """
      Send partial log and parametric data to FIS server.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      evalOper = "*%s" % self.dut.nextOper
      objMsg.printMsg("evalOper=%s" % (evalOper))
      try:
         from Setup import CSetup
         CSetup().writeParametricData()                  
         DriveAttributes.update({'CMS_CONFIG':'NONE'}) 
         DriveAttributes.update({'CMS_CONFIG':self.dut.driveattr["CMS_CONFIG"],'LOOPER_COUNT':1}) # LOOPER_COUNT to "disable" ADG
         ReportErrorCode(14824) #Use a dummy error code for unyielded data. UNRECOGNIZED_TEST_NUM 14824
         RequestService('SetOperation',(evalOper,))
         RequestService('SendRun',(1,))
      finally:
         DriveAttributes['LOOPER_COUNT'] = '0'                 # "enable" ADG
         ReportErrorCode(0)
         RequestService('SetOperation',(self.dut.nextOper,))   #Reset to the primary operation

#----------------------------------------------------------------------------------------------------------
class CPadMcZoneBoundary(CState):
   """
      Pad MC Zone Boundary
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from MediaScan import CUserFlaw
      self.oUserFlaw = CUserFlaw()
      self.oUserFlaw.writePListToSlipList(spcId = 1071)
      self.oUserFlaw.St(TP.prm_64_pad_mc_zone_boundary)
      self.oUserFlaw.writePListToSlipList(spcId = 1072)
