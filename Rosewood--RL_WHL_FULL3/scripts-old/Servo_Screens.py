#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Servo Screen Module
#  - Contains FNC2 servo screen state support
#
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/12/20 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Servo_Screens.py $
# $Revision: #3 $
# $DateTime: 2016/12/20 00:58:41 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Servo_Screens.py#3 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#

from Constants import *
from TestParamExtractor import TP
from State import CState
import MessageHandler as objMsg
from PowerControl import objPwrCtrl
from Process import CProcess


#----------------------------------------------------------------------------------------------------------
class CServoScreens(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from Servo import CServoScreen
      self.oSrvScreen = CServoScreen()
      self.oProc = CProcess()

      # Set to allow access to FAFH Zones at beginning of STATE
      if testSwitch.IS_FAFH: 
         self.oProc.St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value
         self.oProc.St(TP.AllowFAFH_AccessBit_178) # Allow FAFH access for servo test
         self.oProc.St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value

      self.oProc.St(TP.readThermalPrm_31)
      if not ( testSwitch.ROSEWOOD7 ):
         self.oSrvScreen.NrroLinearityScreen(TP.NrroLinearityPrm_34) # servo recommend to remove
         self.oSrvScreen.servoScan(TP.svo_Scan_32) # servo recommend to remove
         self.oSrvScreen.servoRetract(TP.prm_SrvoActRetract_25) # servo recommend to remove

      if not testSwitch.SINGLEPASSFLAWSCAN:
         if testSwitch.RUN_ATS_SEEK_TUNING:
            SetFailSafe()
            self.oProc.St(TP.TuneATS_194)
            ClearFailSafe()
         # T194 save to SAP, there is a power cycle. Need to re-enable access
         # Set to allow access to FAFH Zones at beginning of STATE
         if testSwitch.IS_FAFH: 
            self.oProc.St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value
            self.oProc.St(TP.AllowFAFH_AccessBit_178) # Allow FAFH access for servo test
            self.oProc.St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value

      self.oProc.St(TP.prm_030_random_write)
      self.oProc.St(TP.prm_030_random_read)
      self.oProc.St(TP.prm_030_full_write)
      self.oProc.St(TP.prm_030_full_read)

      self.oSrvScreen.resonanceTest(TP.prm_Resonance_180)
      if not ( testSwitch.ROSEWOOD7 or testSwitch.TRUNK_BRINGUP ):
         self.oSrvScreen.tunedSeek(TP.prm_tunedSeek_7) # servo recommend to remove
      if testSwitch.FE_0258915_348429_COMMON_TWO_TEMP_CERT_SCRN_A00006:
         objMsg.printMsg("===============FE_0258915_348429_COMMON_TWO_TEMP_CERT_SCRN_A00006===============")
         entries = None
         try:
            entries = self.dut.dblData.Tables('P025_LD_UNLD_PARAM_STATS').tableDataObj()
         except:
            objMsg.printMsg('Attention:Table P025_LD_UNLD_PARAM_STATS not exist!!!')
         if entries:
            ULD_TIME_MAX = 0
            LOAD_TIME_MIN = 1000
            for record in entries:
               STATISTIC_NAME = record['STATISTIC_NAME']
               if STATISTIC_NAME == 'MAX':
                  ULD_TIME_MAX = float(record['ULD_TIME'])
               elif STATISTIC_NAME == 'MIN':
                  LOAD_TIME_MIN = float(record['LOAD_TIME'])
            if ULD_TIME_MAX > 138.0 and LOAD_TIME_MIN < 177.0:
               objMsg.printMsg("Same_Two_Temp_CERT_Downgrade Trigger ULD_TIME_MAX %4f LOAD_TIME_MIN %4f" % (ULD_TIME_MAX,LOAD_TIME_MIN))
               if self.dut.CAPACITY_CUS.find('STD') < 0 and not self.downGradeOnFly(1, 14664):
                  import ScrCmds
                  ScrCmds.raiseException(14664, 'Load and Unload Time out of limit.')
            else:
               objMsg.printMsg("ULD_TIME_MAX %4f LOAD_TIME_MIN %4f Passed specs limit" % (ULD_TIME_MAX,LOAD_TIME_MIN))

      # Set to dis-allow access to FAFH Zones at end of STATE
      if testSwitch.IS_FAFH: 
         self.oProc.St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value
         self.oProc.St(TP.DisallowFAFH_AccessBit_178) # Dis-allow FAFH access after completing servo test
         self.oProc.St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value


#----------------------------------------------------------------------------------------------------------
class CPESInstability(CState):
   """
   Run Test 41 - PES Instability test
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      objMsg.printMsg("Performing PES based head instability screen.")
      CProcess().St(TP.Instability_PES_41)


#----------------------------------------------------------------------------------------------------------
class CLinearityScreen(CState):
   """
   Check linearity settings using T150.  If state parameter 'CAL' is set to 'ON', this state will re-calibrate
   the linearizer.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      self.oProc = CProcess()
      if (testSwitch.FE_0113902_345334_SAVE_SAP_WHEN_CHANGING_DUAL_STAGE) :
         from FSO import CFSO
         self.oFSO = CFSO()

      # Set to allow access to FAFH Zones at beginning of STATE
      if testSwitch.IS_FAFH: 
         self.oProc.St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value
         self.oProc.St(TP.AllowFAFH_AccessBit_178) # Allow FAFH access for servo test
         self.oProc.St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value

      if testSwitch.FE_0122163_357915_DUAL_STAGE_ACTUATOR_SUPPORT and testSwitch.FE_0122180_357915_T150_DISABLE_UACT:
         self.oProc.St(TP.enableHiBWController_Single)
      self.oProc.St(TP.vCatGoRealNoSAPPrm_47)
      if testSwitch.ENABLE_T175_ZAP_CONTROL:
         self.oProc.St(TP.zapPrm_175_zapOff)
      else:
         self.oProc.St(TP.setZapOffPrm_011) # Turn off ZAP for Track Spacing

      if self.params.get('CAL','') == 'ON':
         linParms = TP.servoLinCalPrm_150.copy()
         try:
            linParms['CWORD1'] &= 0xBFFF  # Clear bit 14 to ensure SAP is not flashed.  We must not write the system area with ZAP and VCAT real mode off
         except:
            linParms['CWORD1'] = linParms['CWORD1'][0] & 0xBFFF
         head_range = self.params.get('HEAD_RANGE', None)
         if head_range != None:
            linParms['HEAD_RANGE'] = head_range

         self.oProc.St(linParms)
         if self.params.get('ENABLE_CHROME_ZAP_POST_SCREEN',False): #Warning: Can't be run pre- FULL PACK ZAP state
            self.oProc.St(TP.VCATCHROMEON_11)

         self.oProc.St(TP.vCatOn_47)  # Save SAP to flash is implicit in this call

         if testSwitch.FE_0122163_357915_DUAL_STAGE_ACTUATOR_SUPPORT and testSwitch.FE_0122180_357915_T150_DISABLE_UACT:
            self.oProc.St(TP.enableHiBWController_Dual)
            if (testSwitch.FE_0113902_345334_SAVE_SAP_WHEN_CHANGING_DUAL_STAGE) :
               self.oFSO.saveSAPtoFLASH()
      else:
         self.oProc.St(TP.servoLinCalCheck_150)
         if testSwitch.FE_0122163_357915_DUAL_STAGE_ACTUATOR_SUPPORT and testSwitch.FE_0122180_357915_T150_DISABLE_UACT:
            self.oProc.St(TP.enableHiBWController_Dual)
            if (testSwitch.FE_0113902_345334_SAVE_SAP_WHEN_CHANGING_DUAL_STAGE) :
               self.oFSO.saveSAPtoFLASH()

      # Set to dis-allow access to FAFH Zones at end of STATE
      if testSwitch.IS_FAFH: 
         self.oProc.St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value
         self.oProc.St(TP.DisallowFAFH_AccessBit_178) # Dis-allow FAFH access after completing servo test
         self.oProc.St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value

      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)


#----------------------------------------------------------------------------------------------------------
class CServoTests(CState):
   """
   A class to hold post download 2 servo test operations.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      CProcess().T37RPSDefaultDownload()

#----------------------------------------------------------------------------------------------------------
class CAGCScreen(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      
      self.oProc = CProcess()

   #-------------------------------------------------------------------------------------------------------
   def run(self):

      from Utility import CUtility
      self.oUtility = CUtility()

      # objMsg.printMsg("AGC_Screen Begin DESTROKE_REQ = %s" % self.dut.driveattr['DESTROKE_REQ'])
      # objMsg.printMsg("AGC_Screen Begin self.dut.IDExtraPaddingSize = %d" % self.dut.IDExtraPaddingSize)
      #self.get_DestrokeForIDRolloff()
      origPaddingSize = TP.RampDetectTestPrm_185['ID_PAD_TK_VALUE']
      import types
      if type(origPaddingSize) == types.TupleType:
         origPaddingSize = origPaddingSize[0]

      FinalExtraPaddingSize = 0                          # final extra padding size (largest of all heads)
      FinalErrCode = 0                                   # final error code
      self.data_AGCScrn = [[0]]*self.dut.imaxHead          # record all AGC data
      #FailEvenDestrokeWithNewRap   = 0
      agc_prm = TP.pesMeasurePrm_83_agc01.copy()
      origAGC_MINMAX_DELTA = agc_prm['AGC_MINMAX_DELTA']
      agc_prm_ds = TP.pesMeasurePrm_83_agc01_ds.copy()
      dsMinMaxDeltaMargin = agc_prm_ds['AGC_MINMAX_DELTA_MARGIN']
      dsMaxCyl = agc_prm_ds['DS_MAX_CYL']
      dsStep = agc_prm_ds['DS_STEP']
      for head in range(self.dut.imaxHead):
         self.data_AGCScrn[head]=[]
         ExtraPaddingSize = 0                            # local extra padding size needed
         Errcode = 0                                     # local error code

         iTrack = self.dut.maxTrack[head]- 1
         agc_prm['TEST_HEAD'] = head
         agc_prm['END_CYL'] = self.oUtility.ReturnTestCylWord(iTrack)
         agc_prm['TEST_CYL'] = self.oUtility.ReturnTestCylWord(iTrack-101)
         agc_prm['AGC_MINMAX_DELTA'] = origAGC_MINMAX_DELTA

         try: self.oProc.St(agc_prm)
         except ScriptTestFailure, (failureData):
            self.get_AGCdata()
            Errcode = failureData[0][2]
            # TODO: if destrok with new rap, still fail here, should fail immediately or go through normal destrok process?
            #if not Errcode in [10622,] or testSwitch.AGC_SCRN_DESTROKE == 0 or self.dut.driveattr['DESTROKE_REQ'] == 'DSD' or self.dut.driveattr['DESTROKE_REQ'] == 'DSD_ID':
            # Bypass / Report failure if Not 10622 / 10427
            # Bypass / Report failure if OEM and destroke is turned off
            # Bypass / Report failure if SBS and destroke is turned off
            # Bypass / Report failure if Already detroked
            if not Errcode in [10622,10427] or \
              (testSwitch.AGC_SCRN_DESTROKE == 0 and self.dut.BG not in ['SBS']) or \
              (testSwitch.AGC_SCRN_DESTROKE_FOR_SBS == 0 and self.dut.BG in ['SBS']) or \
              self.dut.driveattr['DESTROKE_REQ'] == 'DSD' or self.dut.driveattr['DESTROKE_REQ'] == 'DSD_NEW_RAP':
               if testSwitch.AGC_SCRN_DESTROKE_FOR_SBS == 1 and self.dut.BG in ['SBS']: # For SBS and destrked is turned on, bypass and continue
                  pass
               elif not testSwitch.AGC_DATA_COLLECTION: raise
            else:
               try:
                  Errcode = 0
                  self.oProc.St(agc_prm)    # retry 1 more time
               except ScriptTestFailure, (failureData):
                  self.get_AGCdata()
                  Errcode = failureData[0][2]
                  # TODO: if destrok with new rap, still fail here, should fail immediately or go through normal destrok process?
                  if not Errcode in [10622,]:
                     raise
                  else:
                     orig_fail_cyl = int(self.dut.dblData.Tables('P083_AGC').tableDataObj()[-1]['TRK_NUM'])
                     agc_prm['AGC_MINMAX_DELTA'] = origAGC_MINMAX_DELTA - dsMinMaxDeltaMargin  # tight the delta to avoid marginal pass
                     # Track_step from 0 to force to recheck orig_fail_cyl
                     for track_step in range(0, dsMaxCyl, dsStep):
                        Errcode = 0
                        objMsg.printMsg("Moving Test Track towards OD: %d" % (iTrack - track_step))
                        agc_prm.update({'END_CYL':  self.oUtility.ReturnTestCylWord(iTrack - track_step)})
                        agc_prm.update({'TEST_CYL': self.oUtility.ReturnTestCylWord(iTrack-101 - track_step)})
                        try:
                           self.oProc.St(agc_prm)
                           break
                        except ScriptTestFailure, (failureData):
                           self.get_AGCdata()
                           Errcode = failureData[0][2]
                           if not Errcode in [10622,]:
                              raise
                     test_cyl = int(self.dut.dblData.Tables('P083_AGC').tableDataObj()[-1]['TRK_NUM'])
                     ExtraPaddingSize = int((orig_fail_cyl - test_cyl) * TP.AGC_Destroke_Ratio)
                     objMsg.printMsg("OrigFailCyl: %d   PassCyl: %d   Padding: %d" % (orig_fail_cyl, test_cyl, ExtraPaddingSize))

         if Errcode == 0:
            self.get_AGCdata()                          # record last AGC data
            if ExtraPaddingSize > FinalExtraPaddingSize:
               FinalExtraPaddingSize = ExtraPaddingSize
         else:
            FinalErrCode = Errcode
            if testSwitch.AGC_SCRN_DESTROKE_FOR_SBS == 1 and self.dut.BG in ['SBS']:
               if ExtraPaddingSize > FinalExtraPaddingSize:
                  FinalExtraPaddingSize = ExtraPaddingSize
   
      ##############################
      self.oProc.St(TP.spinupPrm_1)
      objMsg.printMsg("HEAD  TRACK DELTA_AGC")
      for head in range(self.dut.imaxHead):
         for index in range(len(self.data_AGCScrn[head])):
            #objMsg.printMsg("%s\t%s\t%s" % (head, self.data_AGCScrn[head][index]['Track'], self.data_AGCScrn[head][index]['Delta_AGC']))
            objMsg.printMsg("%4s %6s %9s" % (head, self.data_AGCScrn[head][index]['Track'], self.data_AGCScrn[head][index]['Delta_AGC']))
      objMsg.printMsg("ORIGINAL_ID_PAD: %d   NEW_ID_PAD: %d   FINAL_ERRCODE: %d" % (origPaddingSize, FinalExtraPaddingSize + origPaddingSize, FinalErrCode))
      ##############################
      if FinalErrCode != 0 and not (testSwitch.AGC_SCRN_DESTROKE_FOR_SBS == 1 and self.dut.BG in ['SBS']):
         if not testSwitch.AGC_DATA_COLLECTION: raise
         #if not FinalErrCode in [10622,] or testSwitch.AGC_SCRN_DESTROKE_WITH_NEW_RAP == 0 or FailEvenDestrokeWithNewRap !=0:
         #   raise
         #else: # Destroke with new RAP
         #   self.dut.driveattr['DESTROKE_REQ'] = 'DSD_ID'
         #   oDestrokeWaterfall = CDestrokeWaterfall(self.dut,self.params)
         #   oDestrokeWaterfall.run()

      elif self.dut.driveattr['DESTROKE_REQ'] == 'NONE':
         #TP.RampDetectTestPrm_185.update({'ID_PAD_TK_VALUE': (FinalExtraPaddingSize + origPaddingSize)})
         #objMsg.printMsg(TP.RampDetectTestPrm_185)
         self.dut.IDExtraPaddingSize = max(FinalExtraPaddingSize,self.dut.IDExtraPaddingSize )
         try:
            self.dut.objData.update({'IDExtraPaddingSize':self.dut.IDExtraPaddingSize})
         except:
            objMsg.printMsg("Fail to save IDExtraPaddingSize to objdata")
         if self.dut.IDExtraPaddingSize > 0:
            objMsg.printMsg("EXTRA_ID_PAD_SIZE: %d" %self.dut.IDExtraPaddingSize)
            if self.dut.IDExtraPaddingSize > TP.Destroke_Trk_To_Load_A_New_RAP:
               if testSwitch.AGC_SCRN_DESTROKE_FOR_SBS == 1 and self.dut.BG in ['SBS']:
                   self.dut.IDExtraPaddingSize = TP.Destroke_Trk_To_Load_A_New_RAP
                   self.dut.driveattr['DESTROKE_REQ'] = 'DSD'
               else:
                  self.dut.driveattr['DESTROKE_REQ'] = 'DSD_NEW_RAP'
            else:
               self.dut.driveattr['DESTROKE_REQ'] = 'DSD'

            if 'DESTROKED' in TP.Proc_Ctrl30_Def:
               self.dut.driveattr['PROC_CTRL30'] = '0X%X' % (int(self.dut.driveattr.get('PROC_CTRL30', '0'),16) | TP.Proc_Ctrl30_Def['DESTROKED'])
            self.dut.stateTransitionEvent = 'restartAtState'
            if not testSwitch.FE_0190240_007955_USE_FILE_LIST_FUNCTIONS_FROM_DUT_OBJ:
               from Setup import CSetup
               objSetup = CSetup()
               objSetup.buildFileList()  #update file list after update new partno
            else:
               self.dut.buildFileList()
            self.dut.nextState = 'DNLD_CODE'
            from DbLog import DbLog
            DbLog(self.dut).delAllOracleTables()


   #-------------------------------------------------------------------------------------------------------
   def get_AGCdata(self):
      head = int(self.dut.dblData.Tables('P083_AGC').tableDataObj()[-1]['HD_LGC_PSN'])
      test_cyl = int(self.dut.dblData.Tables('P083_AGC').tableDataObj()[-1]['TRK_NUM'])
      agc_val = int(self.dut.dblData.Tables('P083_AGC').tableDataObj()[-1]['DELTA_MA_AGC'])
      self.data_AGCScrn[head].append({'Head'            : head,
                                 'Track'           : test_cyl,
                                 'Delta_AGC'       : agc_val,
                                 })

   #-------------------------------------------------------------------------------------------------------
   def get_DestrokeForIDRolloff(self):
      if 0 and self.dut.HGA_SUPPLIER in ['HWY', 'TDK'] and testSwitch.YARRAR :
         padsize = 0
         wrt_heat_clr = {}
         self.oProc.St({'test_num':172,'spc_id': 2, 'prm_name':'DestrokeForIDRolloff Retrieve Table', 'CWORD1':5})
         WRT_HEAT_CLRNC_Table = self.dut.dblData.Tables('P172_AFH_DH_CLEARANCE').chopDbLogLoop([0,30], 'SPC_ID', 'min')
         for row in WRT_HEAT_CLRNC_Table:
            wrt_heat_clr.setdefault(int(row['HD_LGC_PSN']), {}).update({int(row['DATA_ZONE']):int(row['WRT_HEAT_CLRNC'])})
         for hd in  wrt_heat_clr:
            if (wrt_heat_clr[hd][min(wrt_heat_clr[hd].keys())] - wrt_heat_clr[hd][max(wrt_heat_clr[hd].keys())]) > 24:
               padsize  = 3501
         self.dut.IDExtraPaddingSize = max(padsize, self.dut.IDExtraPaddingSize)
         objMsg.printMsg("DestrokeForIDRolloff self.dut.IDExtraPaddingSize = %d" % self.dut.IDExtraPaddingSize)
         try:
            self.dut.objData.update({'IDExtraPaddingSize':self.dut.IDExtraPaddingSize})
         except:
            objMsg.printMsg("Fail to save IDExtraPaddingSize to objdata")

