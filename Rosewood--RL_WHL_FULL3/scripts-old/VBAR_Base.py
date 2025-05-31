#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: VBAR Base CLass module
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
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/VBAR_Base.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/VBAR_Base.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#

from Constants import *
from TestParamExtractor import TP
from State import CState
import MessageHandler as objMsg


#----------------------------------------------------------------------------------------------------------
class CVbarBase(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.dut = dut
      self.params = dict(params)
      depList = []
      CState.__init__(self, dut, depList)

      # Default SPC_ID behavior
      self.bump_spcid_before = 0
      self.bump_spcid_after  = 0
      self.skip_state        = 0

      # Load actions - virtual call to avoid loading from TP at import time
      self.loadActions()

      # Update with State Table parms
      self.actions.update(self.params)

      if testSwitch.FE_0165107_163023_P_FIX_TPII_WITH_PRESET_IN_VBAR:
         #!!!! for Charlie's TPI fix SNR experiment only!!!!  YWL
         if HDASerialNumber in TP.TPIsettingPerDriveSN:
            self.actions.update({
                               'MAX_TPI_PICKER_ADJ' : 0.00,
                                })

      # Ensure spc_id is initialized
      from Utility import CSpcIdHelper
      self.spcHelper = CSpcIdHelper(self.dut)
      self.spcHelper.getSetIncrSpcId('P_VBAR_FORMAT_SUMMARY', startSpcId = 0, increment = 0, useOpOffset = 1)
      self.spcHelper.getSetIncrSpcId('P_VBAR_ADC_SUMMARY', startSpcId = 0, increment = 0, useOpOffset = 1)

   #-------------------------------------------------------------------------------------------------------
   def bump_spcid(self):
      self.spcHelper.incrementRevision('P_VBAR_FORMAT_SUMMARY')

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if self.bump_spcid_before:
         self.bump_spcid()

      if testSwitch.FE_0258044_348085_WATERFALL_WITH_ONE_TRK_PER_BAND and self.skip_state:
         return

      from WTF_Base import CWaterfallTest
      CWaterfallTest(self.dut, self.actions).run()

      # Increment the minor revision
      self.spcHelper.getSetIncrSpcId('P_VBAR_FORMAT_SUMMARY', startSpcId = 0, increment = 1, useOpOffset = 1)

      if self.bump_spcid_after:
         self.bump_spcid()


#----------------------------------------------------------------------------------------------------------
class CVbarFormatPicker(CVbarBase):
   #-------------------------------------------------------------------------------------------------------
   def loadActions(self):
      self.bump_spcid_after  = 1
      self.actions = {
                  'LBR'              : testSwitch.FE_0261758_356688_LBR and not testSwitch.virtualRun, # Adjust Zone Boundery during Picker routine
                  'FMT_PICKER'       : 1,
                  'HANDLE_NIBLET'    : True, # Set Max LBA
                  'REFRESH_ZONE_TBL' : True, # Refresh zone table
                  'HANDLE_WTF_EXT'   : 1,    # Update PCBA, fam, SAP, CAP, PFM_ID
      }


#----------------------------------------------------------------------------------------------------------
class CVbarTripletOpti(CVbarBase):
   #-------------------------------------------------------------------------------------------------------
   def loadActions(self):
      self.actions = {
                  'AUTO_TRIPLET_MEAS': 1,                  
                  'NO_MARGIN_SPEC'   : 0,# testSwitch.SMR_TRIPLET_OPTI_SET_BPI_TPI, #1, # off the save BPI/TPI
                  'FMT_PICKER'       : testSwitch.SMR_TRIPLET_OPTI_SET_BPI_TPI,       #1, # off the save BPI/TPI
                  'ITERATIONS'       : 0,
                  'SAVE_PERSISTENT'  : 0,
                  'LOAD_PERSISTENT'  : 0,
      }
      

#----------------------------------------------------------------------------------------------------------
class CTPINom(CVbarBase):
   #-------------------------------------------------------------------------------------------------------
   def loadActions(self):
      self.bump_spcid_before = 1
      self.bump_spcid_after  = 1

      self.actions = {
                  'TPINOMINAL'         : 1,
                  'SAVE_PERSISTENT'    : 0,
                  'LOAD_PERSISTENT'    : 0,
                  'GET_BPI_FILE'       : 0, # Do not load BPI Config Table
      }


#----------------------------------------------------------------------------------------------------------
class CBPINom(CVbarBase):
   #-------------------------------------------------------------------------------------------------------
   def loadActions(self):
      self.actions = {
                  'BPI_NOM'            : 1,
                  'REFRESH_ZONE_TBL'   : False, #dont refresh zone table 
                  'SAVE_PERSISTENT'    : 0,
                  'LOAD_PERSISTENT'    : 0,
      }
#----------------------------------------------------------------------------------------------------------
class CVbarPESZn(CVbarBase):
   #-------------------------------------------------------------------------------------------------------
   def loadActions(self):
      self.actions = {
                  'VBAR_PES'           : 1,
                  'REFRESH_ZONE_TBL'   : False, #dont refresh zone table 
                  'SAVE_PERSISTENT'    : 0,
                  'LOAD_PERSISTENT'    : 0,
      }

#----------------------------------------------------------------------------------------------------------
class CBPIXfer(CVbarBase):
   #-------------------------------------------------------------------------------------------------------
   def loadActions(self):
      self.bump_spcid_before = 1
      self.bump_spcid_after  = 1

      self.actions = {
                  'BPI_TRANSFER_MEAS'  : 1,
                  'REFRESH_ZONE_TBL'   : False, #dont refresh zone table 
      }

#----------------------------------------------------------------------------------------------------------
class C2DVbarZn(CVbarBase):
   def loadActions(self):
      self.bump_spcid_before = 1
      self.bump_spcid_after  = 1

      self.actions = {
                  '2D_VBAR_MEAS'       : 1,
                  'REFRESH_ZONE_TBL'   : False, #dont refresh zone table 
      }

#----------------------------------------------------------------------------------------------------------
class C1DVbarZn(CVbarBase):
   def loadActions(self):
      self.bump_spcid_before = 1
      self.bump_spcid_after  = 1

      self.actions = {
                  '1D_VBAR_MEAS'       : 1,
                  'TPI_DSS_MEAS'       : testSwitch.FE_0257372_504159_TPI_DSS_UMP_MEASURMENT,
                  'REFRESH_ZONE_TBL'   : False, #dont refresh zone table 
      }

#----------------------------------------------------------------------------------------------------------
class CVbarMargin(CVbarBase):
   def loadActions(self):
      self.bump_spcid_before = 1
      self.bump_spcid_after  = 1

      self.actions = {
                  'ADC_SUMMARY'        : testSwitch.FE_0253362_356688_ADC_SUMMARY,
                  'ZIPPER_ZONE_UPDATE' : testSwitch.FE_0257373_348085_ZONED_SERVO_CAPACITY_CALCULATION,
                  'ATI_MEAS'           : testSwitch.RUN_ATI_IN_VBAR,
                  'OTC_MARGIN_MEAS'    : testSwitch.VBAR_MARGIN_BY_OTC,
                  'OTC_MARGIN_V2'      : testSwitch.FE_0293889_348429_VBAR_MARGIN_BY_OTCTP,
                  'SQZ_BPIC_MEAS'      : testSwitch.FE_0254388_504159_SQZ_BPIC,
                  'SET_ADC_FMT'        : testSwitch.FE_xxxxxxx_348429_P_SET_ADC_FMT,
                  'SMR_FORMAT'         : testSwitch.VBAR_MARGIN_BY_OTC | testSwitch.FE_0254388_504159_SQZ_BPIC,
                  'MARGIN_OPTI'        : testSwitch.VBAR_MARGIN_BY_OTC | testSwitch.FE_0254388_504159_SQZ_BPIC | \
                                         testSwitch.RUN_ATI_IN_VBAR,
                  'SET_MARGIN_RELOAD'  : testSwitch.FE_0303725_348429_P_VBAR_MARGIN_RELOAD,
      }
#----------------------------------------------------------------------------------------------------------
class CVbarSet_ADC(CVbarBase):
   def loadActions(self):
      self.actions = {
                  'ENABLE_ZAP'         : 0,
                  'ZIPPER_ZONE_UPDATE' : testSwitch.FE_0257373_348085_ZONED_SERVO_CAPACITY_CALCULATION,
                  'SET_ADC_FMT'        : testSwitch.FE_xxxxxxx_348429_P_SET_ADC_FMT,
                  'SMR_FORMAT'         : testSwitch.VBAR_MARGIN_BY_OTC | testSwitch.FE_0254388_504159_SQZ_BPIC,
      }

#----------------------------------------------------------------------------------------------------------
class CVbarReport_ADC(CVbarBase):
   def loadActions(self):
      self.actions = {
                  'ENABLE_ZAP'         : 0,
                  'ADC_SUMMARY'        : testSwitch.FE_0253362_356688_ADC_SUMMARY,
                  'ZIPPER_ZONE_UPDATE' : testSwitch.FE_0257373_348085_ZONED_SERVO_CAPACITY_CALCULATION,
                  'SET_ADC_FMT'        : testSwitch.FE_xxxxxxx_348429_P_SET_ADC_FMT,
                  'SMR_FORMAT'         : testSwitch.VBAR_MARGIN_BY_OTC | testSwitch.FE_0254388_504159_SQZ_BPIC,
                  'SAVE_PERSISTENT'    : 0, # This is so that not to update the VBAR Dictionary
      }

#----------------------------------------------------------------------------------------------------------
class CVbarMargin_Opti(CVbarBase):
   def loadActions(self):
      self.actions = {
                  'MARGIN_OPTI'        : testSwitch.VBAR_MARGIN_BY_OTC | testSwitch.FE_0254388_504159_SQZ_BPIC | \
                                         testSwitch.RUN_ATI_IN_VBAR,
                  'LOAD_FREQ_TABLE'    : 1,
                  'REFRESH_ZONE_TBL'   : False, #dont refresh zone table 
      }

#----------------------------------------------------------------------------------------------------------
class CVbarMargin_SqzBPI(CVbarBase):
   def loadActions(self):
      self.actions = {
                  'SQZ_BPIC_MEAS'      : testSwitch.FE_0254388_504159_SQZ_BPIC,
                  'LOAD_FREQ_TABLE'    : 0,
                  'REFRESH_ZONE_TBL'   : False, #dont refresh zone table 
      }

#----------------------------------------------------------------------------------------------------------
class CVbarMargin_MgnRLoad(CVbarBase):
   def loadActions(self):
      self.actions = {
                  'SET_MARGIN_RELOAD'  : testSwitch.FE_0303725_348429_P_VBAR_MARGIN_RELOAD,
      }

#----------------------------------------------------------------------------------------------------------
class CVbarMargin_Segment(CVbarBase):
   def loadActions(self):
      self.actions = {
                  'SEG_BER_MEAS'  : testSwitch.FE_SEGMENTED_BPIC,
                  'REFRESH_ZONE_TBL'   : False, #dont refresh zone table 
      }

#----------------------------------------------------------------------------------------------------------
class CVbarMargin_SHMS(CVbarBase):
   def loadActions(self):
      self.actions = {
                  'SMR_HMS'  : testSwitch.FE_0325284_348429_P_VBAR_SMR_HMS,
                  'REFRESH_ZONE_TBL'   : False, #dont refresh zone table 
      }
#----------------------------------------------------------------------------------------------------------
class CVbarMargin_TPISOVA(CVbarBase):
   def loadActions(self):
      self.actions = {
                  'TPI_MARGIN_BY_SOVA' : testSwitch.FE_0345891_348429_TPIM_SOVA_USING_FIX_TRANSFER,
                  'REFRESH_ZONE_TBL'   : False, #dont refresh zone table 
      }
#----------------------------------------------------------------------------------------------------------
class CVbarMargin_OTC(CVbarBase):
   def loadActions(self):
      self.actions = {
                  'OTC_MARGIN_MEAS'    : testSwitch.VBAR_MARGIN_BY_OTC,
                  'OTC_MARGIN_V2'      : testSwitch.FE_0293889_348429_VBAR_MARGIN_BY_OTCTP,
                  'REFRESH_ZONE_TBL'   : False, #dont refresh zone table 
      }

#----------------------------------------------------------------------------------------------------------
class CVbarMargin_ATI(CVbarBase):
   def loadActions(self):
      self.actions = {
                  'ATI_MEAS'           : testSwitch.RUN_ATI_IN_VBAR,
                  'GET_BPI_FILE'       : 0, # Do not load BPI Config Table
                  'REFRESH_ZONE_TBL'   : False, #dont refresh zone table 
      }

#----------------------------------------------------------------------------------------------------------
class CVbarOC2(CVbarBase):
   def loadActions(self):
      self.bump_spcid_before = 1
      self.bump_spcid_after  = 1

      self.actions = {
                  'ENABLE_ZAP'         : 0,
                  'REVERT'             : 0,
                  'VBAR_OC2'           : testSwitch.FE_0302539_348429_P_ENABLE_VBAR_OC2,
      }

#----------------------------------------------------------------------------------------------------------
class CVbarZn(CVbarBase):
   def loadActions(self):
      self.bump_spcid_before = 1
      self.bump_spcid_after  = 1

      self.actions = {
                  'ZN_OPTI'        : not testSwitch.VBAR_2D_DEBUG_MODE,
                  'ATI_MEAS'       : testSwitch.RUN_ATI_IN_VBAR,
                  'ZN_MEAS'        : 1,
                  'HMS_OPTI'       : 0,
                  'SMR_MEAS'       : testSwitch.SMR,
                  'FMT_PICKER'     : 1,
                  'ITERATIONS'     : 0,
                  'OTC_MARGIN_MEAS': testSwitch.VBAR_MARGIN_BY_OTC,
                  'SQZ_BPIC_MEAS'  : testSwitch.FE_0254388_504159_SQZ_BPIC,
                  'OTC_MARGIN_V2'  : testSwitch.FE_0293889_348429_VBAR_MARGIN_BY_OTCTP,
                  'ADC_SUMMARY'    : testSwitch.FE_0253362_356688_ADC_SUMMARY,
                  'LBR'            : testSwitch.FE_0261758_356688_LBR and not testSwitch.virtualRun,
                  'TPI_DSS_MEAS'   : testSwitch.FE_0257372_504159_TPI_DSS_UMP_MEASURMENT,
                  'ZIPPER_ZONE_UPDATE' : testSwitch.FE_0257373_348085_ZONED_SERVO_CAPACITY_CALCULATION,
                  'PARAMS_FILTER'  : testSwitch.APPLY_FILTER_ON_SMR_TPI,
                  'SET_ADC_FMT'    : testSwitch.FE_xxxxxxx_348429_P_SET_ADC_FMT,
                  'SMR_FORMAT'     : testSwitch.VBAR_MARGIN_BY_OTC | testSwitch.FE_0254388_504159_SQZ_BPIC,
                  'MARGIN_OPTI'    : testSwitch.VBAR_MARGIN_BY_OTC | testSwitch.FE_0254388_504159_SQZ_BPIC | \
                                    testSwitch.RUN_ATI_IN_VBAR,
                  'SET_MARGIN_RELOAD'  : testSwitch.FE_0303725_348429_P_VBAR_MARGIN_RELOAD,
                  'HANDLE_NIBLET'  : True,   # Set Max LBA
                  'REFRESH_ZONE_TBL' : True, # Refresh zone table
                  'HANDLE_WTF_EXT' : 1,      # Update PCBA, fam, SAP, CAP, PFM_ID
      }

      if testSwitch.FE_0158815_208705_VBAR_ZN_MEAS_ONLY:
         self.actions.update({
                  'NO_MARGIN_SPEC': 1,
                  'MAX_BPI_PICKER_ADJ' : 0.00,
                  'MAX_TPI_PICKER_ADJ' : 0.00,
         })

#----------------------------------------------------------------------------------------------------------
class CVbarOTC(CVbarBase):
   def loadActions(self):
      self.bump_spcid_before = 1
      self.bump_spcid_after  = 1
      self.skip_state        = 0

      if (testSwitch.TRUNK_BRINGUP or testSwitch.ROSEWOOD7) and not testSwitch.extern.SFT_TEST_0271:
         objMsg.printMsg('WARNING: VBAR OTC requires SFT_TEST_0271')
         self.actions = {}
         return

      self.actions = {
         'RD_OFT_MEAS'        : testSwitch.OTC_BASED_RD_OFFSET, 
         'FMT_PICKER'         : not testSwitch.FE_0309812_348429_P_LOAD_BY_ACTIVE_HEAD_ZONES,
         'REFRESH_ZONE_TBL'   : False, #dont refresh zone table 
      }

      if testSwitch.FE_0258044_348085_WATERFALL_WITH_ONE_TRK_PER_BAND:
         objMsg.printMsg("VBAR_OTC: Partnumber=%s" % self.dut.driveattr['PART_NUM'])
         part1, part2 = self.dut.driveattr['PART_NUM'].split('-')
         if part1[-1] in ['C','c']:
            objMsg.printMsg("Skip state = %s" % (self.dut.currentState))
            self.skip_state = 1

#----------------------------------------------------------------------------------------------------------
class CVbarInterbandScrn(CVbarBase):
   def loadActions(self):
      self.actions = {
         'OTC_INTERBANDMEAS'  : 1,
         'LOAD_FORMAT_SCALE'  : 0, # Don load the format scaler
         'LOAD_PERSISTENT'    : 0, # Do not load persistent data from SIM
         'SAVE_PERSISTENT'    : 0, # Do not update persistent data to SIM
         'GET_BPI_FILE'       : 0, # Do not load BPI Config Table
         'ENABLE_ZAP'         : 0, # Do not enable ZAP
         'NO_DISABLE_ZAP'     : 1, # Do not disable ZAP
      }

#----------------------------------------------------------------------------------------------------------
class CVbarHMS_ZapOffEnd(CVbarBase):
   def loadActions(self):

      if testSwitch.VBAR_HMS_MEAS_ONLY:
         self.actions = {
                     'HMS_MEAS'           : 1,
                     'HMS_OPTI'           : [0,1],
                     'ADJ_MARGIN_SPEC'    : 0,
                     'FMT_PICKER'         : 0,
                     'ITERATIONS'         : 1,
                     'BPI_PER_HMS'        : TP.BPIperHMS1,
                     'MAX_BPI_STEP'       : [0.07, 0.06],
                     'MAX_TPI_PICKER_ADJ' : 0.00,
                     'NO_DISABLE_ZAP'     : 0,
                     'LOAD_FORMAT_SCALE'  : 0, # Do not load the format scaler
                     'LOAD_PERSISTENT'    : 0, # Do not load persistent data from SIM
                     'SAVE_PERSISTENT'    : 0, # Do not update persistent data to SIM
                     'GET_BPI_FILE'       : 0, # Do not load BPI Config Table
                     'REFRESH_ZONE_TBL'   : False, #dont refresh zone table 
         }
      else:
         self.actions = {
                     'HMS_OPTI'           : [0,1],
                     'HMS_MEAS'           : 1,
                     'HMS_ADJ'            : 1,
                     'HMS_FAIL'           : 0,
                     'ADJ_MARGIN_SPEC'    : 1,
                     'FMT_PICKER'         : 1,
                     'ITERATIONS'         : 2,
                     'BPI_PER_HMS'        : TP.BPIperHMS1,
                     'MAX_BPI_STEP'       : [0.07, 0.06],
                     'MAX_TPI_PICKER_ADJ' : 0.00,
                     'NO_DISABLE_ZAP'     : 0,
                     'HANDLE_NIBLET'      : True, # Set Max LBA
                     'REFRESH_ZONE_TBL'   : True, # Refresh zone table
                     'HANDLE_WTF_EXT'     : 1,    # Update PCBA, fam, SAP, CAP, PFM_ID
         }
      

      if testSwitch.shortProcess:
         self.actions.update({
            'ITERATIONS'         : 1,
         })

      if testSwitch.FE_0158815_208705_VBAR_ZN_MEAS_ONLY:
         self.actions.update({
                  'NO_MARGIN_SPEC': 1,
         })

      if testSwitch.FE_0162444_208705_ASYMMETRIC_VBAR_HMS:
         self.actions.update({
                  'MIN_TARGET_HMSCAP'  : TP.VbarHMSMinTargetHMSCap,
                  'MAX_TARGET_HMSCAP'  : TP.VbarHMSMaxTargetHMSCap,
         })

      elif testSwitch.ADJUST_HMS_FOR_CONSTANT_MARGIN:
         self.actions.update({
                  'MIN_TARGET_HMSCAP'  : TP.VHMSConstantMarginTarget,  # VBAR HMS Constant Margin testing mode,
                  'MAX_TARGET_HMSCAP'  : TP.VHMSConstantMarginTarget,  # VHMSConstantMarginTarget is set in base_TestParameters.py.
         })

    