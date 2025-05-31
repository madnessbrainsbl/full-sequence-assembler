#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Head Instability Test Module
#  - Contains support for HD_STABILITY and similar states
#
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Head_Instab.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Head_Instab.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
from State import CState
import MessageHandler as objMsg
from PowerControl import objPwrCtrl
from Process import CProcess
from MathLib import stDev_standard, mean


#----------------------------------------------------------------------------------------------------------
class CHeadInstability(CState):
   """
   Run head instability test
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   
      self.oProc = CProcess()

   #-------------------------------------------------------------------------------------------------------
   def run(self):

      if testSwitch.MARVELL_T195_VERSION:
         # Test will run in fail-safe state mode until it can be evaulated on drives with working ZAP
         # - Anthony Schubert
         if TP.prm_195_VGA.get ('ZONES',[]):
            inPrm = TP.prm_195_VGA['base']
            if testSwitch.auditTest ==1:
               inPrm['RETRY_LIMIT'] = 0x03
            for zn in TP.prm_195_VGA['ZONES']:
               inPrm['ZONE'] = zn
               try:
                  self.oProc.St(inPrm)
               except:
                  objMsg.printMsg("Expected to fail until ZAP re-enabled")
         else:
            try:
               self.oProc.St(TP.prm_195_VGA)  # Head Stability
            except:
               objMsg.printMsg("Expected to fail until ZAP re-enabled")
            try:
               self.oProc.St(TP.prm_195_BIAS)            # Head Stability
            except:
               objMsg.printMsg("Expected to fail until ZAP re-enabled")
            try:
               self.oProc.St(TP.prm_195_VMM)  # Head Stability
            except:
               objMsg.printMsg("Expected to fail until ZAP re-enabled")

      # Use non-Marvell T195 version
      else:
         if testSwitch.FE_0131531_357915_SPC_ID_IN_STATE_PARAM_FOR_CHEADINSTABILITY:
            spcId = self.params.get('SPC_ID', TP.prm_Instability_195.get('spc_id', 1))

         if testSwitch.FE_0111302_231166_RUN_195_IN_SEPERATE_STATE:
            if TP.prm_Instability_195.get ('ZONES',[]):
               inPrm = TP.prm_Instability_195['base']
               if testSwitch.FE_0131531_357915_SPC_ID_IN_STATE_PARAM_FOR_CHEADINSTABILITY:
                  inPrm['spc_id'] = spcId
               if testSwitch.auditTest ==1:
                  inPrm['RETRY_LIMIT'] = 0x03
               for zn in TP.prm_Instability_195['ZONES']:
                  inPrm['ZONE'] = zn
                  self.oProc.St(inPrm)
            else:
               if testSwitch.FE_0131531_357915_SPC_ID_IN_STATE_PARAM_FOR_CHEADINSTABILITY:
                  inPrm = TP.prm_Instability_195
                  inPrm['spc_id'] = spcId
                  self.oProc.St(inPrm)
               else:
                  self.oProc.St(TP.prm_Instability_195)

            if testSwitch.WA_0110971_009438_POWER_CYCLE_AT_ZAP_START == 0:
               # TRM - Apparently the ZAP issue is not caused by T195 - Sparrow disabled INSTAB_195_SUPPORT,
               # and the issue re-appeared.   So, this flag moves the power cycle out of Test195 and
               # into the start of ZAP.
               #
               # Prior (apperently incorrect) comment:
               # T195 doesn't fully restore drive state, so that seeks in subsequent tests (ZAP) fail
               # Until T195 is fixed, power cycle to restore drive state.
               objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
         else:
            if testSwitch.FE_0131531_357915_SPC_ID_IN_STATE_PARAM_FOR_CHEADINSTABILITY:
               inPrm = TP.prm_Instability_195
               inPrm['spc_id'] = spcId
               self.oProc.St(inPrm)
            else:
               self.oProc.St(TP.prm_Instability_195)


#----------------------------------------------------------------------------------------------------------
class CHeadInstabilityScreenAndRecovery(CState):
   """
      Description: Class that will perform head instablity screen and recovery
      Base: N/A
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

      self.oProc = CProcess()

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      self.unstable_head_ec = TP.prm_Head_Recovery_Heater_Power['EC_Trigger']

      for table in ['P072_SUMMARY','P195_SUMMARY', 'P103_WIJITA']:
         try: self.dut.dblData.delTable(table, forceDeleteDblTable = 1)
         except: pass

      if testSwitch.ANGSANAH:
         try:
            self.oProc.St(TP.Instability_TA_199) #T199
         except: pass
         try:
            self.oProc.St(TP.Instability_TA_199_2) #T199
         except: pass
         try:
            self.oProc.St(TP.Instability_TA_199_3) #T199
         except: pass
         ## Power cycle to disable the  VGAR adaptation
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

      if self.dut.nextOper == "FNC2" and testSwitch.RUN_T195_IN_FNC2_CRT2:
         try:
            self.oProc.St(TP.prm_Servo_AGC_Mode_103)
         except: pass


      if not testSwitch.KARNAK:
         self.oProc.St(TP.prm_Head_Scrn_395)

      if testSwitch.FE_0189781_357595_HEAD_RECOVERY:
         try:
            self.oProc.St(TP.prm_ET_Instability_VGA_195)
         except ScriptTestFailure, (failureData):
            ec = failureData[0][2]
            if ec in self.unstable_head_ec:
               if self.dut.nextOper == "CAL2" and testSwitch.RUN_T195_IN_CAL2:   # run T195 after Vbar in CAL2 for data collection, no failing
                  pass
               self.HeadCheckingAndBaking()
            else:
               raise

      else:
         if not testSwitch.KARNAK:
            try: self.oProc.St(TP.prm_ET_Instability_VGA_195)
            except: pass

   #-------------------------------------------------------------------------------------------------------
   def getFailedPhyHd(self, spcid=1):
      fail_hd=[]
      tablename = "P195_SUMMARY"
      testsummary = self.dut.dblData.Tables(tablename).chopDbLog('SPC_ID', 'match', str(spcid))
      for data in testsummary:
         if (int(data['HD_STATUS']) in self.unstable_head_ec):
            if not (int(data['HD_PHYS_PSN']) in fail_hd):
               fail_hd.append(int(data['HD_PHYS_PSN']))
      return fail_hd

   #-------------------------------------------------------------------------------------------------------
   def IsRetailTab(self):
      if self.dut.partNum[-3:] in TP.RetailTabList:
         objMsg.printMsg('Already Retail Partnumber %s.' % self.dut.partNum)
         return 1
      return 0

   #-------------------------------------------------------------------------------------------------------
   def checkT103(self, phyHd):
      tableData = self.dut.dblData.Tables('P103_WIJITA').chopDbLog('HD_PHYS_PSN', 'match',str(phyHd))
      AVG_WIJITA_column = []
      for row in tableData:
         AVG_WIJITA_column.append(int(row['AVG_WIJITA']))
      if len(AVG_WIJITA_column)>0:
         #objMsg.printMsg('HeadScreen_P103_WIJITA std dev AVG_WIJITA %f.' % stDev_standard(AVG_WIJITA_column))
         if mean(AVG_WIJITA_column) > 74:
            objMsg.printMsg('HeadScreen_P103_WIJITA mean AVG_WIJITA %f.' % mean(AVG_WIJITA_column))
            return 0
      return 1

   #-------------------------------------------------------------------------------------------------------
   def checkBER(self, phy_hd, P250_spc_id):
      max_data_err_cnt = 0
      ber_list = []
      try:
         ber_table = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').chopDbLog('SPC_ID', 'match', str(P250_spc_id))
         for row in ber_table:
            if phy_hd == int(row['HD_PHYS_PSN']):
               ber_list.append(float(row['RAW_ERROR_RATE']))
               if int(row['DATA_ERR_CNT']) > max_data_err_cnt:
                  max_data_err_cnt = int(row['DATA_ERR_CNT'])
      except:
         if P250_spc_id == 2:
            from RdWr import CRdScrn2File
            oRdScrn2File = CRdScrn2File()
            ber_list = oRdScrn2File.Retrieve_RD_SCRN2_RAW_byPhyHd(phy_hd,0)
         else:
            objMsg.printMsg('checkBER Cannot Get BER data')
            return 0
      if len(ber_list):
         objMsg.printMsg( 'HeadScreen_P250 hd %d : mean ber %f.' % (phy_hd, mean(ber_list)) )
         #objMsg.printMsg('HeadScreen_P250 std dev %f.' % stDev_standard(ber_list))

         if mean(ber_list) > -2.4 or max_data_err_cnt > 30:
            objMsg.printMsg('checkBER failed BER or Data Err Cnt avg_ber: %f  max_data_err_cnt %d' % (mean(ber_list), max_data_err_cnt))
            return 0

      return 1

   #-------------------------------------------------------------------------------------------------------
   def HeadCheckingAndBaking(self, run_instability_checking=1, fail_hd=[], reTSR=1, heaterparms=TP.prm_Head_Recovery_Heater_Power['HeaterPower']):

      raise_ec = 0

      if testSwitch.FE_0189781_357595_HEAD_RECOVERY:
         # FE_0189781_357595_HEAD_RECOVERY uses prm_ET_Instability_VGA_195 in checking for failure heads:
         if not len(fail_hd):
            fail_hd = self.getFailedPhyHd()
      
      objMsg.printMsg('fail_hd to bake: %s' % str(fail_hd), objMsg.CMessLvl.VERBOSEDEBUG)

      for failedHd in fail_hd:
         objMsg.printMsg('failedHd: %s' % str(failedHd), objMsg.CMessLvl.VERBOSEDEBUG)
         if not reTSR and ((1 << failedHd) & (self.dut.driveattr['THERM_SHK_RCVRY'] & 0xFF)):
            objMsg.printMsg('Head %d already been baked, skipped..' % (failedHd), objMsg.CMessLvl.VERBOSEDEBUG)
            continue

         #Run only failed Head
         if testSwitch.FE_0189781_357595_HEAD_RECOVERY:
            head_instab_param = TP.prm_ET_Instability_VGA_195
            head_instab_param.update({ 'HEAD_RANGE'  : 0x0101 * failedHd })
         else: 
            head_instab_param = TP.prm_Head_Recovery_baking_MrrChk_072
            head_instab_param.update({ 'TEST_HEAD'  : failedHd })

         attempt = 0
         while ( attempt < len(heaterparms) ):
            reader_heaterpow = heaterparms[attempt][0]   # reader heater to apply (mW)
            heaterpowloop = heaterparms[attempt][1]   # repeat no of times
            checkingloop  = heaterparms[attempt][2]   # loops to check to ensure pass after TSR
            if testSwitch.FE_0322846_403980_P_DUAL_HEATER_N_BIAS_TSHR:
               writer_heaterpow = heaterparms[attempt][3] # writer heater to apply (mW)
               readerBias = heaterparms[attempt][4] # reader voltage bias to apply (mV)
            attempt      += 1
            if run_instability_checking == 0 and checkingloop: # to trigger end of TSR
               break # continue

            objMsg.printMsg('===== Hd %d TSR attempt %d =====' % (failedHd, attempt))
            for cnt in range(heaterpowloop):
               objMsg.printMsg('T072 TSR at Hd %d with reader heater %dmW, loop #%d, pass loop=%d' % (failedHd, reader_heaterpow, cnt+1, checkingloop))
               #bake only failed Head and Updated the heater power value to desired value
               if testSwitch.FE_0322846_403980_P_DUAL_HEATER_N_BIAS_TSHR:
                  objMsg.printMsg('writer heater %dmW, readerBias %dmV' % (writer_heaterpow, readerBias))
                  self.oProc.St(head_instab_param, { 'HEATER':(writer_heaterpow, reader_heaterpow), 'MRBIAS_SAMPLES': readerBias,})
               else:
                  self.oProc.St(head_instab_param, { 'HEATER':(reader_heaterpow,0) })
               self.dut.driveattr['THERM_SHK_RCVRY'] |= (1 << failedHd)    # TSR attr to indicate which head is baked/shocked

               if testSwitch.FE_0189781_357595_HEAD_RECOVERY and run_instability_checking == 1 and checkingloop:  # check for instability
                  try:
                     for chk in range(checkingloop):
                        self.oProc.St(head_instab_param)
                     attempt = len(heaterparms)    # to end while loop
                     break #screen pass

                  except ScriptTestFailure, (failureData):
                     from VBAR import CUtilityWrapper 
                     ec = failureData[0][2]
                     if ( attempt < len(heaterparms) ):  # continue to shock
                        pass  # continue for loop to shock and check again
                     elif self.dut.nextOper == 'FNC2':   # fail if cannot recover thru head bake in FNC2
                        objMsg.printMsg("T195 Head Screen Failed for EC %d  with Partnumber %s" % (ec, self.dut.partNum))
                        raise
                     elif self.dut.nextOper == 'PRE2' and self.checkBER(failedHd, P250_spc_id = 195):    # only for PRE2
                        objMsg.printMsg("T195 Head Screen Failed for EC %d  with Partnumber %s" % (ec, self.dut.partNum))
                        raise_ec = ec
                     elif testSwitch.ENABLE_HEAD_INSTABILITY_WATERFALL and (CUtilityWrapper(self.dut,{}).SearchLowerCapacityPn()!=0) \
                     and self.dut.nextOper == 'PRE2':    # downgrade only in PRE2, not FNC2
                        objMsg.printMsg("T195 Head Screen Failed for EC %d (%s) - Force Waterfall" % (ec, self.dut.partNum))
                        self.dut.Waterfall_Req = "REZONE"
                        self.dut.driveattr['DNGRADE_ON_FLY'] = '%s_%s_%d' % (self.dut.nextOper, self.dut.partNum[-3:], ec)
                        return
                     else: raise


      if testSwitch.FE_0189781_357595_HEAD_RECOVERY: 
         if raise_ec and self.dut.partNum[-3:] not in TP.RetailTabList :
            if testSwitch.FE_HEATER_RELIEF_RECONFIG:
               from Head_Screen import CHead_Screen 
               CHead_Screen().HeaterReliefReconfig()
            else:
               import ScrCmds
               ScrCmds.raiseException(raise_ec, 'T195 Head Screen Failed - Raise to downgrade to SBS')


#----------------------------------------------------------------------------------------------------------
class CColdStability(CState):
   """
   CRT2 - Cold instability screen state
      Run Test 195, 199
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

      self.oProc = CProcess()

   #-------------------------------------------------------------------------------------------------------
   def run(self):

      self.oProc.St(TP.prm_Instability_195_test)
      self.oProc.St(TP.prm_Instability_195_2_test)

      self.oProc.St(TP.Instability_TA_199_test)
      self.oProc.St(TP.Instability_TA_199_2_test)

      objPwrCtrl.powerCycle(useESlip=1)  # Powercycle at the end of the test

