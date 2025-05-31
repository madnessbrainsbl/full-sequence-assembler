#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Head Instability Test Module
#  - Contains support for HD_STABILITY and similar states
#
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/10/20 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Head_Screen.py $
# $Revision: #10 $
# $DateTime: 2016/10/20 23:37:15 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Head_Screen.py#10 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
from State import CState
import MessageHandler as objMsg
from PowerControl import objPwrCtrl
import ScrCmds


#----------------------------------------------------------------------------------------------------------
class CHeadScreenBase(CState):
   """
      Description: Class that will perform Head Screen
      Base: CState
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, depList=[], params={}):
      self.params = params
      CState.__init__(self, dut, depList)
      from Process import CProcess      
      self.oProc = CProcess()

   #-------------------------------------------------------------------------------------------------------
   def loadActions(self):
      self.actions = {
         'ZAP_ON_AT_BEGIN'   : 0,
         'PRE_BER_CHECK'     : 0,
         'RUN_T199'          : 0,
         'RUN_T250_DBS'      : 0,
         'RUN_T315_SUM'      : 0,
         'RUN_T103'          : 0,
         'DO_ASYMMETRY_CHECK': 0,
         'DO_HRR'            : 0,
         'POST_BER_CHECK'    : 0,
         'ZAP_OFF_AT_END'    : 0,
      }
   
   #-------------------------------------------------------------------------------------------------------
   def ZapOn(self):
      if testSwitch.ENABLE_T175_ZAP_CONTROL:
         self.oProc.St(TP.zapPrm_175_zapOn)
      else:
         self.oProc.St(TP.setZapOnPrm_011)
         if not testSwitch.BF_0119055_231166_USE_SVO_CMD_ZAP_CTRL:
            self.oProc.St(TP.saveSvoRam2Flash_178)
   
   #-------------------------------------------------------------------------------------------------------
   def ZapOff(self):
      if testSwitch.ENABLE_T175_ZAP_CONTROL:
         self.oProc.St(TP.zapPrm_175_zapOff)
      else:
         self.oProc.St(TP.setZapOffPrm_011)
         if not testSwitch.BF_0119055_231166_USE_SVO_CMD_ZAP_CTRL:
            self.oProc.St(TP.saveSvoRam2Flash_178)
   
   #-------------------------------------------------------------------------------------------------------
   def CollectBERdata(self, testhd=[], numToRun = 3, spcid=102):
      from MathLib import stDev_standard, mean
      from RdWr import CRdWrScreen
      self.oRdWr = CRdWrScreen()

      numHds = len(testhd)
      
      if numHds <= 0 or numHds >self.dut.imaxHead:
         return
      
      SERprm = self.oProc.oUtility.copy(TP.prm_quickSER_250)
      SERprm.update({'MAX_ERR_RATE' : self.params.get('MAX_ERR_RATE', -80)})
      if self.params.get('RST_RD_OFFSET', 0): #Reset read offset to on track read in FNC2
         SERprm.update({'CWORD2' : (SERprm['CWORD2'][0] | 0x0800, )})
         flawListMask = 0x40
      else: 
         flawListMask = 0x140
      if self.actions.get('TCC', 0): #Enable temperature compensation in CRT2
         SERprm.update({'CWORD2' : (SERprm['CWORD2'][0] | 0x0001, )})
	  
      if (self.dut.numZones == 150):
         altZone = 3
      else:
         altZone = 1
      SERprm.update({'TEST_ZONES' : range(0,self.dut.numZones,altZone)}) 
      testzn = len(SERprm['TEST_ZONES']) 
	  
      if testSwitch.FE_0124358_391186_T250_ZONE_SWEEP_RETRIES:
         SERprm['ZONE_POSITION'] = 198    #Start at the end of the zone before sweeping zone if necessary

      RawSovaErrRate = [[[1.0] * testzn for i in range(numHds)] for j in xrange(numToRun)]
      tZone = [[1.0] * testzn for i in range(numHds)]
      for loop in xrange(numToRun):
         spcId_local = spcid + loop*100

         RS2H_p250ErrRateTbl = 0
         try:
            RS2H_p250ErrRateTbl = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').chopDbLog('SPC_ID', 'match', str(16))
         except:
            objMsg.printMsg('Cannot Access READ_SCRN2H P250_ERROR_RATE_BY_ZONE table')
            pass

         if RS2H_p250ErrRateTbl and loop == 0:
            p250ErrRateTbl = RS2H_p250ErrRateTbl
         else:

            if numHds == self.dut.imaxHead:  # all head
               try: self.oRdWr.quickSymbolErrorRate(SERprm, flawListMask, spc_id=spcId_local, numRetries=1)
               except: pass
            else:
               for hd in testhd:
                  SERprm['TEST_HEAD'] = hd<<8 + hd
                  try: self.oRdWr.quickSymbolErrorRate(SERprm, flawListMask, spc_id=spcId_local, numRetries=1)
                  except: pass
            p250ErrRateTbl = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').chopDbLog('SPC_ID', 'match', str(spcId_local))

         for entry in p250ErrRateTbl:
            iHead = int(entry.get('HD_LGC_PSN'))
            iZone = int(entry.get('DATA_ZONE'))
            if iZone in range(0,self.dut.numZones,altZone):
               tZone[iHead][iZone/altZone] = iZone
               RawSovaErrRate[loop][iHead][iZone/altZone] = float(entry.get('RAW_ERROR_RATE'))

      self.meanStdevList = [0.0] * numHds    # mean of stdev of all valid zones by head
      self.meanDeltaList = [0.0] * numHds    # mean of max delta of all valid zones by head
      self.countList     = [0]   * numHds    # no of zones that failed spec by head
      for hd in testhd:
         StdevList = [100.0] * testzn   # stdev of each zone of current head
         DeltaList = [100.0] * testzn   # max delta of each zone of current head
         for zn in xrange(testzn):
            berList = [1.0] * (numToRun)
            ignoredZn = 0
            for k in range(numToRun):
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
         objMsg.printMsg('DEBUG: meanDeltaList[%d] = %f' % (hd,self.meanDeltaList[hd]))
         objMsg.printMsg('DEBUG: countList[%d] = %d' % (hd,self.countList[hd]))
      self.dut.dblData.Tables('DBS_MTRIX_BY_ZONE').deleteIndexRecords(1)
      self.dut.dblData.delTable('DBS_MTRIX_BY_ZONE')

      for hd in testhd:
         for zn in xrange(testzn):
            berList = [1.0] * numToRun
            for k in xrange(numToRun):
               berList[k] = RawSovaErrRate[k][hd][zn]
            self.dut.dblData.Tables('DBS_MTRIX_BY_ZONE').addRecord({
               'SPC_ID'                      : spcid,
               'OCCURRENCE'                  : self.dut.objSeq.getOccurrence(),
               'SEQ'                         : self.dut.objSeq.curSeq,
               'TEST_SEQ_EVENT'              : self.dut.objSeq.getTestSeqEvent(0),
               'HD_PHYS_PSN'                 : hd,
               'DATA_ZONE'                   : tZone[hd][zn],
               'RAW_BER'                     : str(berList),
               'STDEV'                       : stDev_standard(berList),
               'DELTA'                       : max(berList) - min(berList),
               'AVG_STDEV_HD'                : self.meanStdevList[hd],
               'AVG_DELTA_HD'                : self.meanDeltaList[hd],
               'COUNT'                       : self.countList[hd],
               })
      objMsg.printMsg('**SPC_ID32=%d, Table=DBS_MTRIX_BY_ZONE' % (spcid))
      objMsg.printDblogBin(self.dut.dblData.Tables('DBS_MTRIX_BY_ZONE'))

   #---------------------------------------------------------------------------------------------------------
   def HeadAsymmetryChecking(self):
      try:
         asym_ratio_spec = TP.prm_Asymmetry_251_spec
      except:
         asym_ratio_spec = 0.5
      num_failed_zone = 0
      if not testSwitch.virtualRun:
         try:
            self.dut.dblData.Tables('P251_MARVELL_DIBIT').deleteIndexRecords(1)        # del previous table pointers
            self.dut.dblData.delTable('P251_MARVELL_DIBIT')
         except:
             objMsg.printMsg("*** No P251_MARVELL_DIBIT table !! ***")
             pass

      self.oProc.St(TP.prm_Asymmetry_251)
      marvelldibittbl = self.dut.dblData.Tables('P251_MARVELL_DIBIT').chopDbLog('SPC_ID', 'match',str(TP.prm_Asymmetry_251['spc_id']))
      for i in xrange(len(marvelldibittbl)):
         iHead = int(marvelldibittbl[i]['HD_PHYS_PSN'])
         iDataZone = int(marvelldibittbl[i]['DATA_ZONE'])
         asym_ratio = abs(float(marvelldibittbl[i]['NLTS3']))
         if asym_ratio > asym_ratio_spec:
            objMsg.printMsg( "HeadAsymmetry failed spec %02f @ Hd%d Zn%02d asymmetry ratio %02f ..." %(asym_ratio_spec,iHead, iDataZone,asym_ratio) )
            num_failed_zone += 1

      if num_failed_zone > 2:
         objMsg.printMsg("HeadAsymmetryChecking failed. Downgrade Required")
         self.downGradeOnFly(1, "HASYM")
         #self.dut.Waterfall_Req = "RC"
         #self.dut.driveattr['DNGRADE_ON_FLY'] = '%s_%s_%d' % (self.dut.nextOper, self.dut.partNum[-3:], 48464)
         #objMsg.printMsg('DNGRADE_ON_FLY: %s' % (self.dut.driveattr['DNGRADE_ON_FLY']))
         #ScrCmds.raiseException(48464, 'HEAD_SCRN Asymmetry failed Hd%d Zn%02d !!!' % (iHead, iDataZone))
   
   #-------------------------------------------------------------------------------------------------------
   def HeaterReliefReconfig(self):
     from AFH import CdPES
     odPES  = CdPES(TP.masterHeatPrm_11, TP.defaultOCLIM)
     spcId = 50000
     if self.dut.HGA_SUPPLIER == 'RHO':  #reconfig to single heater
        self.oProc.St({'test_num':172, 'prm_name':'AFH PTP Coef Dump', 'timeout': 1800, 'CWORD1': (15,), 'spc_id':spcId})
        odPES.setIRPCoefs(self.dut.PREAMP_TYPE, self.dut.AABType, TP.PRE_AMP_HEATER_MODE, TP.clearance_Coefficients_DH2SG, forceRAPWrite = 1)
        odPES.setGammaHValues(self.dut.PREAMP_TYPE, self.dut.AABType, TP.clearance_Coefficients_DH2SG, TP.test178_gammaH)
        from FSO import CFSO
        CFSO().saveRAPtoFLASH()
        objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
        self.oProc.St({'test_num':172, 'prm_name':'AFH PTP Coef Dump', 'timeout': 1800, 'CWORD1': (15,), 'spc_id':(spcId+1)})
     elif self.dut.HGA_SUPPLIER in ['TDK', 'HWY']: # back off rdclr
        self.oProc.St({'test_num':172, 'prm_name':"%s" % (  'P172_AFH_CLEARANCE_tableName' ), 'timeout': 1800, 'CWORD1': (5,), 'spc_id':spcId})
        self.oProc.St({'test_num':172, 'prm_name':"%s" % ( 'P172_AFH_WORKING_ADAPTS_tableName' ), 'timeout': 1800, 'CWORD1': (4,), 'spc_id':spcId})
        tgtRdClr = []
        adj_tgtClr = 15
        afhZoneTargets_SW = TP.afhZoneTargets.copy()
        objMsg.printMsg('TGT_RD_CLR backoff by:   %f' % (adj_tgtClr))

        for zn in range(self.dut.numZones+1):
          adjtgtRdClr = TP.afhZoneTargets['TGT_RD_CLR'][zn] + adj_tgtClr
          tgtWrClr.append(adjtgtRdClr)
        afhZoneTargets_SW['TGT_RD_CLR'] = tgtWrClr

        odPES.setClearanceTargets(TP.afhTargetClearance_by_zone, afhZoneTargets_SW, range(0, int(self.dut.numZones + 1)))
        self.oProc.St(TP.activeClearControl_178)

        objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
        self.oProc.St({'test_num':172, 'prm_name':"%s" % ( 'P172_AFH_CLEARANCE_tableName' ), 'timeout': 1800, 'CWORD1': (5,), 'spc_id':(spcId + 1)})
        self.oProc.St({'test_num':172, 'prm_name':"%s" % ( 'P172_AFH_WORKING_ADAPTS_tableName' ), 'timeout': 1800, 'CWORD1': (4,), 'spc_id':(spcId+1)})

     self.dut.stateTransitionEvent = 'restartAtState'
     self.dut.nextState = 'AFH1'
   
   #-------------------------------------------------------------------------------------------------------
   def bakingFailHeads(self, failHeads = []):
      if len(failHeads) == 0:
         objMsg.printMsg('no failHeads to bake')
         return
      else:
         failHds = list(set(failHeads))
         objMsg.printMsg('failHeads to bake: %s' % str(failHds), objMsg.CMessLvl.VERBOSEDEBUG)   
       
      heaterpower = TP.prm_Head_Recovery_Heater_Power['heaterpower']
      forcebaking = TP.prm_Head_Recovery_Heater_Power['forcebaking']
      headRecoveryParams = TP.prm_Head_Recovery_baking_MrrChk_072.copy()
      #servo_info = str(self.dut.driveattr['SERVO_INFO'][0:4])
      #objMsg.printMsg('SERVO_INFO: %s' % servo_info)

      for failedHd in failHds:
         for attempt in range(len(heaterpower)):
            if forcebaking[attempt] != 0:
               headRecoveryParams.update({'TEST_HEAD'  : failedHd,'HEATER':(heaterpower[attempt],0)})
               self.oProc.St(headRecoveryParams)

      self.dut.driveattr['THERM_SHK_RCVRY'] = sum(1<<i for i in failHds)
      if 'TRIGGER_TSR' in TP.Proc_Ctrl30_Def:
         self.dut.driveattr['PROC_CTRL30'] = '0X%X' % (int(self.dut.driveattr.get('PROC_CTRL30', '0'),16) | TP.Proc_Ctrl30_Def['TRIGGER_TSR'])

   #-------------------------------------------------------------------------------------------------------
   def RunT199(self):
      self.oProc.St(TP.Instability_TA_199) #T199
      self.oProc.St(TP.Instability_TA_199_2) #T199
      # pending for scrn spc and baking process
   
   #-------------------------------------------------------------------------------------------------------
   def RunT250Dbs(self):
     
      testhd = xrange(self.dut.imaxHead)
      spcid = 102
      failmarginal = 0
      
      try:
         numToRun = TP.HeadInstabilityBySovaErrCountScrnSpec['NUMBER_T250_TO_RUN']
         self.CollectBERdata(testhd, numToRun, spcid=102)
      except:
         numToRun = 3
         pass

      # check if it passes the criteria
      pAvgDelta = TP.HeadInstabilityBySovaErrCountScrnSpec['MIN_AVG_DELTA_BER_HD']
      pZnCnt    = TP.HeadInstabilityBySovaErrCountScrnSpec['MIN_FAIL_ZONE_COUNT_HD']
      objMsg.printMsg("DEBUG: check AVG_DELTA_HD >= %.5f and COUNT >= %i" % (pAvgDelta, pZnCnt))
      self.dut.fail_head_TSR = []
      for hd in testhd:
         if (self.meanDeltaList[hd] >= pAvgDelta and self.countList[hd] >= pZnCnt):
            objMsg.printMsg("Head instability check failed, T250 head %d unstable" % (hd) )
            errStr = "Head instability check fail. AVG_DELTA_HD >= %.5f and COUNT >= %d" % (pAvgDelta, pZnCnt)
            objMsg.printMsg("%s" % (errStr))
            self.dut.fail_head_TSR.append(hd)
      
      if self.dut.fail_head_TSR:
         if testSwitch.ENABLE_THERMAL_SHOCK_RECOVERY_V3 and self.actions.get('TSHR', 0) and not testSwitch.virtualRun:
            from RdWr import CMrResFile
            if testSwitch.FE_0173493_347506_USE_TEST321 and testSwitch.extern.SFT_TEST_0321:
                oMrRes = CMrResFile(TP.get_MR_Resistance_321, TP.mrDeltaLim)
            else:
                oMrRes = CMrResFile(TP.get_MR_Values_186, TP.mrDeltaLim)
            oMrRes.diffMRValues()
            from Head_Instab import CHeadInstabilityScreenAndRecovery
            CHeadInstabilityScreenAndRecovery(self.dut,{}).HeadCheckingAndBaking(run_instability_checking = 0, fail_hd=self.dut.fail_head_TSR)
            self.CollectBERdata(testhd, numToRun, spcid=202)
            for hd in range(self.dut.imaxHead):
                if self.meanDeltaList[hd] >= TP.HeadInstabilityBySovaErrCountScrnSpec['MIN_AVG_DELTA_BER_HD_BAK'] and \
                self.countList[hd] > pZnCnt:
                    objMsg.printMsg("meanDeltaList >= %f and countList > %d" % (TP.HeadInstabilityBySovaErrCountScrnSpec['MIN_AVG_DELTA_BER_HD_BAK'],pZnCnt) )        
                    if self.actions.get('FAIL_SAFE', 0):
                       objMsg.printMsg("Head instability check failed, head unstable. Fail safe enabled.")
                    else:
                       ScrCmds.raiseException(10560, "Head instability check failed, head unstable @ Head : [%s]" %str(hd) )   

         else:
            if not self.actions.get('FAIL_SAFE', 0):
               errStr = errStr + ' @ Head : ' + str(self.dut.fail_head_TSR)
               ScrCmds.raiseException(10560, errStr)
      if (self.dut.nextState == 'HEAD_SCRN4') and testSwitch.FE_0368834_505898_P_MARGINAL_SOVA_HEAD_INSTABILITY_SCRN and TP.MarginalSovaHDIntabilityCombo:
         try:
            wpeUin = eval('[%s]' % self.dut.driveattr['WPE_UIN'])
         except:
            wpeUin = [0] * self.dut.imaxHead
         for hd in xrange(self.dut.imaxHead):
            if self.dut.modeloss_avg_info[hd] >= TP.MarginalSovaHDIntabilityCombo['Mean_MODE_LOSS'] and self.dut.sigmaloss_avg_info[hd] >= TP.MarginalSovaHDIntabilityCombo['Mean_SIGMA_LOSS'] and self.meanDeltaList[hd] >= TP.MarginalSovaHDIntabilityCombo['P250_MeanDELTA_BER'] and wpeUin[hd] <= TP.MarginalSovaHDIntabilityCombo['DRV_WPE_UINC']:
               objMsg.printMsg('head %d' % hd) 
               objMsg.printMsg('modeloss_avg_info = %f >= %f' %  (self.dut.modeloss_avg_info[hd],TP.MarginalSovaHDIntabilityCombo['Mean_MODE_LOSS']))
               objMsg.printMsg('sigmaloss_avg_info = %f >= %f' %  (self.dut.modeloss_avg_info[hd],TP.MarginalSovaHDIntabilityCombo['Mean_SIGMA_LOSS']))
               objMsg.printMsg('meanDeltaList = %f >= %f' %  (self.dut.modeloss_avg_info[hd],TP.MarginalSovaHDIntabilityCombo['P250_MeanDELTA_BER']))
               objMsg.printMsg('wpeUin = %f >= %f' %  (wpeUin[hd],TP.MarginalSovaHDIntabilityCombo['DRV_WPE_UINC']))
               failmarginal = 1
         if failmarginal:
             if testSwitch.ENABLE_ON_THE_FLY_DOWNGRADE and self.downGradeOnFly(1, 10560):
                 objMsg.printMsg('Failed for Marginal Sova Instability screening, downgrade to %s as %s' % (self.dut.BG, self.dut.partNum))
             else:
                 ScrCmds.raiseException(10560, 'Failed for Marginal Sova Instability screening ')
 
         

   #-------------------------------------------------------------------------------------------------------
   def RunT315Sum(self):
      if 1:
         t315_hd_instab_det = 0
         try:
            self.oProc.St({'test_num':231,
                          'prm_name':'Verify SIM written',
                          'CWORD1':0x04,
                          'timeout':2000})
            self.oProc.St(TP.prm_T315_Data)
            if testSwitch.ENABLE_T315_SCRN:
               objMsg.printMsg('========= T315 screening =========')
               tableData = []
               
               try:
                  tableData = self.dut.dblData.Tables('P315_INSTABILITY_METRIC').tableDataObj()
               except: 
                   objMsg.printMsg("P315_INSTABILITY_METRIC not found!!!!!")
                   pass
               if len(tableData) > 0:
                  for row in tableData:
                      iHead = int(row['HD_LGC_PSN'])
                      hd_metric = int(row['HD_INSTABILITY_METRIC'])
                      if(hd_metric >= TP.t315_hd_instability_spec):
                        t315_hd_instab_det = 1
                        objMsg.printMsg("T315 screening failed!: HD_INSTABILITY_METRIC >= %d" % (TP.t315_hd_instability_spec))
                        
            #self.oProc.St(TP.prm_T315_SUM)
            self.oProc.St({'test_num':231,
                          'prm_name':'Verify SIM written',
                          'CWORD1':0x04,
                          'timeout':2000})
         except:
            objMsg.printMsg("T315 failed at state: %s" % TP.prm_T315_Data['FILE_ID'])
            objPwrCtrl.powerCycle()
            pass
         if testSwitch.ENABLE_T315_SCRN:
             if t315_hd_instab_det == 1:
                ScrCmds.raiseException(11126, "Head instability check failed for T315, cannot downgrade: HD_INSTABILITY_METRIC >= %d" % (TP.t315_hd_instability_spec))

      else:
         objMsg.printMsg("Skipping T315 state: %s" % TP.prm_T315_Data['FILE_ID'])
   
   #-------------------------------------------------------------------------------------------------------
   def run_BER_CHK(self, prm_name, spc_id):
      prm_PrePostOptiAudit_250_local = self.oProc.oUtility.copy(TP.prm_PrePostOptiAudit_250)  
      prm_PrePostOptiAudit_250_local.update({'MAX_ERR_RATE' : self.actions.get('MAX_ERR_RATE', -80)})
      if self.actions.get('RST_RD_OFFSET', 0): #Reset read offset to on track read in FNC2
         prm_PrePostOptiAudit_250_local['CWORD2'] = prm_PrePostOptiAudit_250_local['CWORD2'] | 0x0800
         prm_PrePostOptiAudit_250_local['CWORD1'] = prm_PrePostOptiAudit_250_local['CWORD1'] | 0x0040
      if self.actions.get('TCC', 0): #Enable temperature compensation in CRT2
         prm_PrePostOptiAudit_250_local['CWORD2'] = prm_PrePostOptiAudit_250_local['CWORD2'] | 0x0001
      #default zones is Measured_BPINOMINAL_Zones, can be overridden using state table parameter
      MaskList = self.oProc.oUtility.convertListToZoneBankMasks(self.params.get('BER_ZONES', TP.Measured_BPINOMINAL_Zones))
      for bank, list in MaskList.iteritems():
         if list:
            if self.actions.get('TCC', 0) and 0 in list: #RSS propose to use Zone 4 in CRT2
               list.remove(0)
               list.append(4)
            prm_PrePostOptiAudit_250_local ['ZONE_MASK_EXT'], prm_PrePostOptiAudit_250_local ['ZONE_MASK'] = \
               self.oProc.oUtility.convertListTo64BitMask(list)
            if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
               prm_PrePostOptiAudit_250_local ['ZONE_MASK_BANK'] = bank
            try: self.oProc.St(prm_PrePostOptiAudit_250_local, {'spc_id': spc_id, 'prm_name': prm_name})
            except: pass

   #-------------------------------------------------------------------------------------------------------
   def RunT297(self):
      failHead = set()
      t297loop = TP.HeadInstabilityT297Spec['t297loop'] #3 # Per RSS request 29 July 2015
      modeloss_info = [[0]*t297loop for hd in xrange(self.dut.imaxHead)]  #3 runs of T297
      modeloss_avg_info = [[0.0] for hd in xrange(self.dut.imaxHead)]  #3 runs of T297
      sigmaloss_info = [[0]*t297loop for hd in xrange(self.dut.imaxHead)]  #3 runs of T297
      sigmaloss_avg_info = [[0.0] for hd in xrange(self.dut.imaxHead)]  #3 runs of T297
      raise_flag = 0
      self.dut.fail_head_TSR = []
      Prm_297 = TP.prm_Instability_297.copy()
      if self.actions.get('TCC', 0): #Enable temperature compensation in CRT2
         Prm_297['CWORD1'] = Prm_297['CWORD1'] | 0x0100
         Prm_297['ZONE'] = 4 #RSS propose to use Zone 4 in CRT2
      if self.actions.get('NO_ADJUST', 0): # Set bit 1 of CWORD1, PERCENT_LIMIT = 0, to use default BPI.
         Prm_297['CWORD1'] = Prm_297['CWORD1'] | 0x0002
      for loop in range(t297loop):
         Prm_297['spc_id'] = Prm_297['spc_id']+loop
         self.oProc.St(Prm_297)
         try:
            P297_tbl = self.dut.dblData.Tables('P297_HD_INSTBY_BIE_SUM').chopDbLog('SPC_ID', 'match',str(Prm_297['spc_id']))
         except:
            P297_tbl = []
         for entry in P297_tbl:
            failHd = int(entry.get('HD_LGC_PSN'))
            modeloss = float(entry.get('MODE_LOSS')) 
            sigmaloss = float(entry.get('SIGMA_LOSS'))
            modeloss_info[failHd][loop] = modeloss 
            sigmaloss_info[failHd][loop] = sigmaloss 
      objMsg.printMsg("modeloss_info %s" %(modeloss_info))
      objMsg.printMsg("sigmaloss_info %s" %(sigmaloss_info))

      #Retry on different zone position in CRT2 only:
      if self.actions.get('TCC', 0): #Enable temperature compensation in CRT2
          hd_retry = []
          for hd in xrange(self.dut.imaxHead):
             temp_sum = 0.0
             for loop in range(t297loop):
                temp_sum += sigmaloss_info[hd][loop]
             if temp_sum == 0:
                hd_retry.append(hd)
          for hd in hd_retry:
             objMsg.printMsg("Re-try hd %d in different zone position..." %(hd))
             for loop in range(t297loop):
                 Prm_297['spc_id'] = Prm_297['spc_id']+loop+t297loop
                 Prm_297['HEAD_RANGE'] = ( (hd << 8) + hd )
                 Prm_297['ZONE_POSITION'] = 100
                 self.oProc.St(Prm_297)
                 try:
                    P297_tbl = self.dut.dblData.Tables('P297_HD_INSTBY_BIE_SUM').chopDbLog('SPC_ID', 'match',str(Prm_297['spc_id']))
                 except:
                    P297_tbl = []
                 for entry in P297_tbl:
                    failHd = int(entry.get('HD_LGC_PSN'))
                    modeloss = float(entry.get('MODE_LOSS')) 
                    sigmaloss = float(entry.get('SIGMA_LOSS'))
                    modeloss_info[failHd][loop] = modeloss 
                    sigmaloss_info[failHd][loop] = sigmaloss      
          objMsg.printMsg("modeloss_info %s" %(modeloss_info))
          objMsg.printMsg("sigmaloss_info %s" %(sigmaloss_info))

      #Retry on different zone:
      hd_retry = []
      for hd in xrange(self.dut.imaxHead):
         temp_sum = 0.0
         for loop in range(t297loop):
            temp_sum += sigmaloss_info[hd][loop]
         if temp_sum == 0:
            hd_retry.append(hd)
      for hd in hd_retry:
         objMsg.printMsg("Re-try hd %d in different zone..." %(hd))
         for loop in range(t297loop):
             Prm_297['spc_id'] = Prm_297['spc_id']+loop+t297loop
             Prm_297['HEAD_RANGE'] = ( (hd << 8) + hd )
             if self.actions.get('TCC', 0): #Enable temperature compensation in CRT2
                Prm_297['ZONE'] = 5
             else:
                Prm_297['ZONE'] = 35 # zone neutral
             self.oProc.St(Prm_297)
             try:
                P297_tbl = self.dut.dblData.Tables('P297_HD_INSTBY_BIE_SUM').chopDbLog('SPC_ID', 'match',str(Prm_297['spc_id']))
             except:
                P297_tbl = []
             for entry in P297_tbl:
                failHd = int(entry.get('HD_LGC_PSN'))
                modeloss = float(entry.get('MODE_LOSS')) 
                sigmaloss = float(entry.get('SIGMA_LOSS'))
                modeloss_info[failHd][loop] = modeloss 
                sigmaloss_info[failHd][loop] = sigmaloss      
      objMsg.printMsg("modeloss_info %s" %(modeloss_info))
      objMsg.printMsg("sigmaloss_info %s" %(sigmaloss_info))

      for hd in xrange(self.dut.imaxHead):
         temp_sum = 0.0
         temp_sum2 = 0.0
         for loop in range(t297loop):
            temp_sum = temp_sum + modeloss_info[hd][loop]
            temp_sum2 = temp_sum2 + sigmaloss_info[hd][loop]
            modeloss_avg_info[hd][0] = temp_sum / t297loop
            sigmaloss_avg_info[hd][0] = temp_sum2 / t297loop
         if (modeloss_avg_info[hd][0] >= TP.HeadInstabilityT297Spec['MODELOSS_AVG_INFO']) or (modeloss_avg_info[hd][0] >= TP.HeadInstabilityT297Spec['MODELOSS_AVG_INFO_COMBO'] and sigmaloss_avg_info[hd][0] >= TP.HeadInstabilityT297Spec['SIGMALOSS_AVG_INFO_COMBO']):
            if not testSwitch.ENABLE_THERMAL_SHOCK_RECOVERY_V3:
               raise_flag = 1
               failHead.add(hd)
            if hd not in self.dut.fail_head_TSR: 
               self.dut.fail_head_TSR.append(hd)
            objMsg.printMsg("Head %s failed HEAD_SCRN T297 MODE_LOSS >= %f or (MODE_LOSS >= %f & SIGMA_LOSS >= %f ) " %(hd,TP.HeadInstabilityT297Spec['MODELOSS_AVG_INFO'],TP.HeadInstabilityT297Spec['MODELOSS_AVG_INFO_COMBO'],TP.HeadInstabilityT297Spec['SIGMALOSS_AVG_INFO_COMBO']))
            
      objMsg.printMsg('self.dut.fail_head_TSR = %s' % (self.dut.fail_head_TSR))
      objMsg.printMsg("modeloss_info %s" %(modeloss_info))
      objMsg.printMsg("sigmaloss_info %s" %(sigmaloss_info))
      objMsg.printMsg('modeloss_avg_info = %s' % (modeloss_avg_info))
      objMsg.printMsg('sigmaloss_avg_info = %s' % (sigmaloss_avg_info))

      if testSwitch.ENABLE_THERMAL_SHOCK_RECOVERY_V3 and self.actions.get('TSHR', 0):
         objMsg.printMsg('self.dut.fail_head_TSR = %s' % (self.dut.fail_head_TSR))
         if self.dut.fail_head_TSR or self.dut.fail_head_TSR2:
            from Head_Instab import CHeadInstabilityScreenAndRecovery  
         if self.dut.fail_head_TSR:
            from RdWr import CMrResFile
            if testSwitch.FE_0173493_347506_USE_TEST321 and testSwitch.extern.SFT_TEST_0321:
               oMrRes = CMrResFile(TP.get_MR_Resistance_321, TP.mrDeltaLim)
            else:
               oMrRes = CMrResFile(TP.get_MR_Values_186, TP.mrDeltaLim)
            oMrRes.diffMRValues()

            CHeadInstabilityScreenAndRecovery(self.dut,{}).HeadCheckingAndBaking(run_instability_checking = 0, fail_hd=self.dut.fail_head_TSR)
            #objMsg.printMsg('self.dut.driveattr[THERM_SHK_RCVRY_V3] = %s' % (self.dut.driveattr['THERM_SHK_RCVRY_V3']))    
                 
            Prm_297['spc_id'] = Prm_297['spc_id']+t297loop+1
            self.oProc.St(Prm_297)
            try:
               P297_tbl = self.dut.dblData.Tables('P297_HD_INSTBY_BIE_SUM').chopDbLog('SPC_ID', 'match',str(Prm_297['spc_id']))
            except:
               P297_tbl = []
            for entry in P297_tbl:
               failHd = int(entry.get('HD_LGC_PSN'))
               modeloss_avg_info[failHd][0] = float(entry.get('MODE_LOSS')) 
               sigmaloss_avg_info[failHd][0] = float(entry.get('SIGMA_LOSS'))
               objMsg.printMsg("HD_LGC_PSN %s modeloss %s sigmaloss %s" %(failHd, modeloss, sigmaloss))
                       
            objMsg.printMsg('modeloss_avg_info = %s' % (modeloss_avg_info))
            objMsg.printMsg('sigmaloss_avg_info = %s' % (sigmaloss_avg_info))
            

            for hd in xrange(self.dut.imaxHead):
               if (modeloss_avg_info[hd][0] >= TP.HeadInstabilityT297Spec['MODELOSS_AVG_INFO']) or (modeloss_avg_info[hd][0] >= TP.HeadInstabilityT297Spec['MODELOSS_AVG_INFO_COMBO'] and sigmaloss_avg_info[hd][0] >= TP.HeadInstabilityT297Spec['SIGMALOSS_AVG_INFO_COMBO']):
                  if hd not in self.dut.fail_head_TSR: #head has not been baked in first round.
                     self.dut.fail_head_TSR2.append(hd) 
                  else:
                     raise_flag = 1
                     failHead.add(hd)                     
                     objMsg.printMsg("Head %s failed HEAD_SCRN T297 MODE_LOSS >= %f or (MODE_LOSS >= %f & SIGMA_LOSS >= %f ) after TSR." %(hd,TP.HeadInstabilityT297Spec['MODELOSS_AVG_INFO'],TP.HeadInstabilityT297Spec['MODELOSS_AVG_INFO_COMBO'],TP.HeadInstabilityT297Spec['SIGMALOSS_AVG_INFO_COMBO']))
         if self.dut.fail_head_TSR2:
            CHeadInstabilityScreenAndRecovery(self.dut,{}).HeadCheckingAndBaking(run_instability_checking = 0, fail_hd=self.dut.fail_head_TSR2)

            #objMsg.printMsg('self.dut.driveattr[THERM_SHK_RCVRY_V3] = %s' % (self.dut.driveattr['THERM_SHK_RCVRY_V3']))    
            Prm_297['spc_id'] = Prm_297['spc_id']+t297loop+2
            self.oProc.St(Prm_297)
            try:
               P297_tbl = self.dut.dblData.Tables('P297_HD_INSTBY_BIE_SUM').chopDbLog('SPC_ID', 'match',str(Prm_297['spc_id']))
            except:
               P297_tbl = []
            for entry in P297_tbl:
               failHd = int(entry.get('HD_LGC_PSN'))
               modeloss_avg_info[failHd][0] = float(entry.get('MODE_LOSS')) 
               sigmaloss_avg_info[failHd][0] = float(entry.get('SIGMA_LOSS'))
               objMsg.printMsg("HD_LGC_PSN %s modeloss %s sigmaloss %s" %(failHd, modeloss, sigmaloss))

            objMsg.printMsg('modeloss_avg_info = %s' % (modeloss_avg_info))
            objMsg.printMsg('sigmaloss_avg_info = %s' % (sigmaloss_avg_info))

            for hd in xrange(self.dut.imaxHead):
               if (modeloss_avg_info[hd][0] >= TP.HeadInstabilityT297Spec['MODELOSS_AVG_INFO']) or (modeloss_avg_info[hd][0] >= TP.HeadInstabilityT297Spec['MODELOSS_AVG_INFO_COMBO'] and sigmaloss_avg_info[hd][0] >= TP.HeadInstabilityT297Spec['SIGMALOSS_AVG_INFO_COMBO']):
                  raise_flag = 1
                  failHead.add(hd)
                  objMsg.printMsg("Head %s failed HEAD_SCRN T297 MODE_LOSS >= %f or (MODE_LOSS >= %f & SIGMA_LOSS >= %f ) after TSR." %(hd,TP.HeadInstabilityT297Spec['MODELOSS_AVG_INFO'],TP.HeadInstabilityT297Spec['MODELOSS_AVG_INFO_COMBO'],TP.HeadInstabilityT297Spec['SIGMALOSS_AVG_INFO_COMBO']))

      if testSwitch.FE_305538_P_T297_WPE_SCREEN and self.dut.HGA_SUPPLIER == 'RHO':
         try:
            wpeUin = eval('[%s]' % self.dut.driveattr['WPE_UIN'])
         except:
            wpeUin = [0] * self.dut.imaxHead
         objMsg.printMsg("Retrieving WPE_UIN = %s" % str(wpeUin))

         if len(modeloss_avg_info) == len(wpeUin):
            for hd in xrange(self.dut.imaxHead):
               wpeSpec,modeSpec,sigmaSpec = TP.CRT2_T297_WPE_Screen['T069_WPE_uin'], TP.CRT2_T297_WPE_Screen['T297_Avg_ModeLoss'], TP.CRT2_T297_WPE_Screen['T297_Avg_SigmaLoss']
               objMsg.printMsg("Hd%d: WPE_UIN=%f (%f), MODE_LOSS=%f (%f), SIGMA_LOSS=%f (%f)" % (hd, wpeUin[hd], wpeSpec, modeloss_avg_info[hd][0], modeSpec, sigmaloss_avg_info[hd][0], sigmaSpec))
               if wpeUin[hd] >= wpeSpec and modeloss_avg_info[hd][0] >= modeSpec and sigmaloss_avg_info[hd][0] >= sigmaSpec:
                  if testSwitch.ENABLE_ON_THE_FLY_DOWNGRADE and not self.actions.get('FAIL_SAFE', 0) and self.downGradeOnFly(1, 10560):
                     objMsg.printMsg('Failed for WPE/T297 combo spec, downgrade to %s as %s' % (self.dut.BG, self.dut.partNum))
                  else:
                     raise_flag = 1
                     failHead.add(hd)

      for hd in xrange(self.dut.imaxHead):  # store modeloss and sigmaloss for combo specs 
         self.dut.modeloss_avg_info.append(modeloss_avg_info[hd][0])
         self.dut.sigmaloss_avg_info.append(sigmaloss_avg_info[hd][0])
      if TP.PoorSovaHDInstCombo_Spec3 :
         objMsg.printMsg("PoorSovaHDInstCombo_Spec3")
         delta_mre = [''] * self.dut.imaxHead
         tbl = self.dut.dblData.Tables('P_DELTA_MRE').tableDataObj() 
         for rec in tbl:
             delta_mre[int(rec['HD_LGC_PSN'])] = abs(float(rec['DELTA_MRE']))
         for hd in xrange(self.dut.imaxHead):
             if self.dut.modeloss_avg_info[hd] >= TP.PoorSovaHDInstCombo_Spec3['mean_mode_loss'] and self.dut.sigmaloss_avg_info[hd] >= TP.PoorSovaHDInstCombo_Spec3['mean_sigma_loss'] and delta_mre[hd] >  TP.PoorSovaHDInstCombo_Spec3['Delta_MRE'] :
                 if testSwitch.ENABLE_ON_THE_FLY_DOWNGRADE and not self.actions.get('FAIL_SAFE', 0) and self.downGradeOnFly(1, 10560):
                    objMsg.printMsg('Failed for PoorSovaHDInstCombo_Spec3, downgrade to %s as %s' % (self.dut.BG, self.dut.partNum))
                    break
                 else:
                    ScrCmds.raiseException(10560, "Failed PoorSovaHDInstCombo_Spec1 @ Head : [%s]" % str(hd))
      
      if raise_flag == 1 and not self.actions.get('FAIL_SAFE', 0):
         ScrCmds.raiseException(10560, "Head instability check failed, head unstable @ Head : %s" %str(list(failHead)) )
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      self.loadActions() #load modules to be run
      self.actions.update(self.params)#update the modules to be run by the params
      
      if self.dut.BG in ['SBS'] and self.dut.BTC and self.actions.get('TSHR', 0):
         self.actions['TSHR'] = 0 # Disable TSR for BTC drive in PRE2 HEAD_SCRN_SMR
         self.actions['FAIL_SAFE'] = 1

      if self.actions.get('ZAP_ON_AT_BEGIN', 0):
         self.ZapOn()

      if self.actions.get('PRE_BER_CHECK', 0):
         self.run_BER_CHK('Pre BER for Head Scrn', 2014)

      if self.actions.get('RUN_T199', 0):
         try: self.RunT199()
         except: pass
      if self.actions.get('RUN_T103', 0):
         try: self.oProc.St(TP.prm_Servo_AGC_Mode_103)
         except: pass

      if self.actions.get('RUN_T250_DBS', 0):
         try: self.RunT250Dbs()
         except ScrCmds.CRaiseException, (failureData): 
            if failureData[0][2] in [10560]:
               raise
            else: #not 10560
               pass

      if self.actions.get('RUN_T315_SUM', 0):
         try: self.RunT315Sum()
         except: pass

      if self.actions.get('DO_HRR', 0):
         try: self.HeaterReliefReconfig()
         except: pass

      if self.actions.get('DO_ASYMMETRY_CHECK', 0):
         self.RunT297()
         

      if self.actions.get('POST_BER_CHECK', 0):
         self.run_BER_CHK('Post BER for Head Scrn', 2015)

      if self.actions.get('ZAP_OFF_AT_END', 0):
         self.ZapOff()


#----------------------------------------------------------------------------------------------------------
class CHeadScreen1(CHeadScreenBase):
   """
      Description: Class that will perform Head Screen in PRE2
      Base: CHeadScreenBase
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CHeadScreenBase.__init__(self, dut, depList, params)

   #-------------------------------------------------------------------------------------------------------
   def loadActions(self):
      self.actions = {
         'ZAP_ON_AT_BEGIN'   : 1,
         'PRE_BER_CHECK'     : 1,
         'RUN_T199'          : 0,
         'RUN_T250_DBS'      : 0,
         'RUN_T315_SUM'      : 0,
         'RUN_T103'          : 0,
         'DO_ASYMMETRY_CHECK': 1,
         'DO_HRR'            : 0,
         'POST_BER_CHECK'    : 0,
         'ZAP_OFF_AT_END'    : 1,
      }


#----------------------------------------------------------------------------------------------------------
class CHeadScreen2(CHeadScreenBase):
   """
      Description: Class that will perform Head Screen in FNC2
      Base: CHeadScreenBase
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CHeadScreenBase.__init__(self, dut, depList, params)

   #-------------------------------------------------------------------------------------------------------
   def loadActions(self):
      self.actions = {
         'ZAP_ON_AT_BEGIN'   : 0,
         'PRE_BER_CHECK'     : 0,
         'RUN_T199'          : 0,
         'RUN_T250_DBS'      : 1,
         'RUN_T315_SUM'      : testSwitch.RUN_TEST_315,
         'RUN_T103'          : testSwitch.extern.PROD_SFT_TEST_0103,#depend on st103 turn on in sf3
         'DO_ASYMMETRY_CHECK': 0,
         'DO_HRR'            : 0,
         'POST_BER_CHECK'    : 0,
         'ZAP_OFF_AT_END'    : 0,
      }


#----------------------------------------------------------------------------------------------------------
class CHead_Screen(CState):
   """
      Description: NA
      Base: NA
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      if testSwitch.FE_0189781_357595_HEAD_RECOVERY:
         depList = ['HEAD_CAL']
      else:
         depList = []
      if testSwitch.FE_HEATER_RELIEF_RECONFIG:
         self.dut = dut
      CState.__init__(self, dut, depList)

      from Process import CProcess      
      self.oProc = CProcess()

   #-------------------------------------------------------------------------------------------------------
   def HeaterReliefReconfig(self):
      from AFH import CdPES
      odPES = CdPES(TP.masterHeatPrm_11, TP.defaultOCLIM)
      spcId = 50000
      if self.dut.HGA_SUPPLIER == 'RHO':  #reconfig to single heater
         self.oProc.St({'test_num':172, 'prm_name':'AFH PTP Coef Dump', 'timeout': 1800, 'CWORD1': (15,), 'spc_id':spcId})
         odPES.setIRPCoefs(self.dut.PREAMP_TYPE, self.dut.AABType, TP.PRE_AMP_HEATER_MODE, TP.clearance_Coefficients_DH2SG, forceRAPWrite = 1)
         odPES.setGammaHValues(self.dut.PREAMP_TYPE, self.dut.AABType, TP.clearance_Coefficients_DH2SG, TP.test178_gammaH)
         from FSO import CFSO
         CFSO().saveRAPtoFLASH()
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
         self.oProc.St({'test_num':172, 'prm_name':'AFH PTP Coef Dump', 'timeout': 1800, 'CWORD1': (15,), 'spc_id':(spcId+1)})
      elif self.dut.HGA_SUPPLIER in ['TDK', 'HWY']: # back off rdclr
         self.oProc.St({'test_num':172, 'prm_name':"%s" % (  'P172_AFH_CLEARANCE_tableName' ), 'timeout': 1800, 'CWORD1': (5,), 'spc_id':spcId})
         self.oProc.St({'test_num':172, 'prm_name':"%s" % ( 'P172_AFH_WORKING_ADAPTS_tableName' ), 'timeout': 1800, 'CWORD1': (4,), 'spc_id':spcId})
         tgtRdClr = []
         adj_tgtClr = 15
         afhZoneTargets_SW = TP.afhZoneTargets.copy()
         objMsg.printMsg('TGT_RD_CLR backoff by:   %f' % (adj_tgtClr))
         
         for zn in range(self.dut.numZones+1):
            adjtgtRdClr = TP.afhZoneTargets['TGT_RD_CLR'][zn] + adj_tgtClr
            tgtWrClr.append(adjtgtRdClr)
         afhZoneTargets_SW['TGT_RD_CLR'] = tgtWrClr
         
         odPES.setClearanceTargets(TP.afhTargetClearance_by_zone, afhZoneTargets_SW, range(0, int(self.dut.numZones + 1)))
         self.oProc.St(TP.activeClearControl_178)
         
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
         self.oProc.St({'test_num':172, 'prm_name':"%s" % ( 'P172_AFH_CLEARANCE_tableName' ), 'timeout': 1800, 'CWORD1': (5,), 'spc_id':(spcId + 1)})
         self.oProc.St({'test_num':172, 'prm_name':"%s" % ( 'P172_AFH_WORKING_ADAPTS_tableName' ), 'timeout': 1800, 'CWORD1': (4,), 'spc_id':(spcId+1)})

      self.dut.stateTransitionEvent = 'restartAtState'
      self.dut.nextState = 'AFH1'

   #---------------------------------------------------------------------------------------------------------
   def HeadAsymmetryChecking(self):
      try:
         asym_ratio_spec = TP.prm_Asymmetry_251_spec
      except:
         asym_ratio_spec = 0.5
      num_failed_zone = 0

      if not testSwitch.virtualRun:
         try:
            self.dut.dblData.Tables('P251_MARVELL_DIBIT').deleteIndexRecords(1)        # del previous table pointers
            self.dut.dblData.delTable('P251_MARVELL_DIBIT')
         except:
             objMsg.printMsg("*** No P251_MARVELL_DIBIT table !! ***")
             pass

      self.oProc.St(TP.prm_Asymmetry_251)
      marvelldibittbl = self.dut.dblData.Tables('P251_MARVELL_DIBIT').chopDbLog('SPC_ID', 'match',str(TP.prm_Asymmetry_251['spc_id']))
      for i in xrange(len(marvelldibittbl)):
         iHead = int(marvelldibittbl[i]['HD_PHYS_PSN'])
         iDataZone = int(marvelldibittbl[i]['DATA_ZONE'])
         asym_ratio = abs(float(marvelldibittbl[i]['NLTS3']))
         if asym_ratio > asym_ratio_spec:
            objMsg.printMsg( "HeadAsymmetry failed spec %02f @ Hd%d Zn%02d asymmetry ratio %02f ..." %(asym_ratio_spec,iHead, iDataZone,asym_ratio) )
            num_failed_zone += 1

      if num_failed_zone > 2:
         objMsg.printMsg("HeadAsymmetryChecking failed. Downgrade Required")
         self.downGradeOnFly(1, "HASYM")
         #self.dut.Waterfall_Req = "RC"
         #self.dut.driveattr['DNGRADE_ON_FLY'] = '%s_%s_%d' % (self.dut.nextOper, self.dut.partNum[-3:], 48464)
         #objMsg.printMsg('DNGRADE_ON_FLY: %s' % (self.dut.driveattr['DNGRADE_ON_FLY']))
         #ScrCmds.raiseException(48464, 'HEAD_SCRN Asymmetry failed Hd%d Zn%02d !!!' % (iHead, iDataZone))
   #---------------------------------------------------------------------------------------------------------
   def run(self):
      if not testSwitch.RUN_HEAD_SCREEN:
         return

      if testSwitch.ENABLE_T175_ZAP_CONTROL:
         self.oProc.St(TP.zapPrm_175_zapOn)
      else:
         self.oProc.St(TP.setZapOnPrm_011)
         if not testSwitch.BF_0119055_231166_USE_SVO_CMD_ZAP_CTRL:
            self.oProc.St(TP.saveSvoRam2Flash_178)

      try:
         self.oProc.St(TP.prm_PrePostOptiAudit_250, {'spc_id':195, 'prm_name':'BER for Head Scrn'})
      except: pass

      from Head_Instab import CHeadInstabilityScreenAndRecovery
      CHeadInstabilityScreenAndRecovery(self.dut,{}).run()

      try:
         if testSwitch.KARNAK:
            self.oProc.St(TP.prm_Instability_297)
         else:
            self.HeadAsymmetryChecking()
      except: pass

      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

      #try: # disabled since it's at too early stage of PRE2 causing unnecessary write faults which could potentially corrupt system zone
      #   CWeakWriteOWTest(self.dut,{}).run()
      #except: pass
      #objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

      #self.oProc.St(TP.prm_Head_Asymmetry_CSM_196)
      if testSwitch.ENABLE_T175_ZAP_CONTROL:
         self.oProc.St(TP.zapPrm_175_zapOff)
      else:
         self.oProc.St(TP.setZapOffPrm_011)
         if not testSwitch.BF_0119055_231166_USE_SVO_CMD_ZAP_CTRL:
            self.oProc.St(TP.saveSvoRam2Flash_178)


#----------------------------------------------------------------------------------------------------------
class CStrong_write_screen(CState):

   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)

      from Process import CProcess      
      self.oProc = CProcess()

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      SetFailSafe()
      try:
         self.oProc.St(TP.prm_Strong_Write_Screen_1)
         self.oProc.St(TP.prm_Strong_Write_Screen_2)
         self.oProc.St(TP.prm_Strong_Write_Screen_3)
         self.oProc.St(TP.prm_Strong_Write_Screen_4)
         self.oProc.St(TP.prm_Strong_Write_Screen_5)
         self.oProc.St(TP.prm_Strong_Write_Screen_6)
         self.oProc.St(TP.prm_Strong_Write_Screen_7)
         self.oProc.St(TP.prm_Strong_Write_Screen_8)
         self.oProc.St(TP.prm_Strong_Write_Screen_9)
         self.strongwrtscr()
      except:  pass
      ClearFailSafe()
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

   #-------------------------------------------------------------------------------------------------------
   def strongwrtscr(self,):

       tableName = 'P251_FITNESS_R_SQUARED'
       strong_wrt_table = self.dut.dblData.Tables(tableName).chopDbLog('SPC_ID', 'match',str(1111)) ## spc_id ?

       for i in xrange(len(strong_wrt_table)):
          iHead   = int(strong_wrt_table[i]['HD_PHYS_PSN'])
          iDataZone  = int(strong_wrt_table[i]['DATA_ZONE'])
          iRgstr_ID = int(strong_wrt_table[i]['RGSTR_ID'])
          R_Squared = float(strong_wrt_table[i]['R_SQUARED'])
          Slope = float(strong_wrt_table[i]['FIT_SLOPE'])

          if abs(Slope) > TP.strong_wrt_slope:
             objMsg.printMsg("Strong Write test failed FIT_SLOPE on Hd %d Zone %d" % (iHead, iDataZone))

#----------------------------------------------------------------------------------------------------------
class CHdPinReversalScreen(CState):
   """
   Head Pin Reversal Screen
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from Process import CProcess 
      self.oProc = CProcess()
      try:  self.oProc.St(TP.prm_HdPinReversalTest_265)
      except: pass

#----------------------------------------------------------------------------------------------------------
