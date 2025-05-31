#-----------------------------------------------------------------------------------------#
# Property of Seagate TechnFology, Copyright 2006, All rights reserved                     #
#-----------------------------------------------------------------------------------------#
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/12/28 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Amazon/StateTable.py $
# $Revision: #36 $
# $DateTime: 2016/12/28 20:22:59 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Amazon/StateTable.py#36 $
# Level: 3
#-----------------------------------------------------------------------------------------#
from Test_Switches import testSwitch
TIER1 = 'T01'
TIER2 = 'T02'
TIER3 = 'T03'
TIERX = 'T0.'

StateTable = {}
StateParams = {}

###################################################################################################################
# State Transition Table
StateTable['PRE2'] = {
   #-----------------------------------------------------------------------------------------------------------------------------------------
   #  State                Module               Method                     Transitions                                           Optional by
   #                                                                                                                             GOTF 'G'
   #-----------------------------------------------------------------------------------------------------------------------------------------
   'INIT'               : ['Serial_Init',       'CInitTesting',            {'pass':'DNLD_CODE',             'fail':'FAIL_PROC'}, []],
   'DNLD_CODE'          : ['Serial_Download',   'CDnldCode',               {'pass':'SETUP_PROC',            'fail':'FAIL_PROC'}, [{'FE_0247885_081592_BODE_PLOT_AT_7200RPM': 0}]],
   'SETUP_PROC'         : ['Serial_Init',       'CSetupProc',              {'pass':'DUMP_PREAMP2',          'fail':'FAIL_PROC'}, []],
   'DUMP_PREAMP2'       : ['base_Preamp',       'CDumpPreamp',             {'pass':'PCBA_SCRN',             'fail':'FAIL_PROC'}, []],
   'PCBA_SCRN'          : ['PCBA_Screen',       'CPcbaScreen',             {'pass':'FOF_SCRN',              'fail':'FAIL_PROC'}, []],
   'FOF_SCRN'           : ['FOF_Screens',       'CFOFScreen',              {'pass':'HRPM_SPIN',             'fail':'FAIL_PROC'}, [{'RUN_FOF_SCREEN': 1}]],
   'HRPM_SPIN'          : ['base_Motor',        'CHighRPMSpin',            {'pass':'SPIN_DIP_SCRN',         'fail':'FAIL_PROC'}, [{'SEA_SWEEPER_RPM' : 1}]],
   'SPIN_DIP_SCRN'      : ['base_Motor',        'CSpinDipScreen',          {'pass':'HEAD_CAL',              'fail':'FAIL_PROC'}, []],
   'HEAD_CAL'           : ['Head_Tuning',       'CInitializeHead_Elec',    {'pass':'MDW_CAL',               'fail':'FAIL_PROC'}, []],
   'MDW_CAL'            : ['Servo_Tuning',      'CMdwCal',                 {'pass':'SVO_TUNE',              'fail':'FAIL_PROC'}, []],
   'SVO_TUNE'           : ['Servo_Tuning',      'CServoTune',              {'pass':'SNO_PHASE',             'fail':'FAIL_PROC'}, [{'FE_SGP_81592_MOVE_MDW_TUNING_TO_SVO_TUNE_STATE': 1}]],
   'SNO_PHASE'          : ['Servo_Tuning',      'CSNOPkDetect',            {'pass':'SNO',                   'fail':'FAIL_PROC'}, [{'RUN_SNO_PD': 1}]],
   'SNO'                : ['Servo_Tuning',      'CSNO',                    {'pass':'BASIC_SWEEP',           'fail':'FAIL_PROC'}, [{'RUN_SNO': 1, 'IS_2D_DRV': 1}]],

   'BASIC_SWEEP'        : ['Sweep_Base',        'CBasicSweep',             {'pass':'SERVO_OPTI',            'fail':'FAIL_PROC'}, []],
   'SERVO_OPTI'         : ['Servo_Tuning',      'CServoOptiCal',           {'pass':'PES_SCRN',              'fail':'FAIL_PROC'}, []],
   'PES_SCRN'           : ['Servo_Tuning',      'CPESScreens',             {'pass':'INIT_RAP',              'fail':'FAIL_PROC'}, []],
   'INIT_RAP'           : ['base_RAP',          'CInitRAP',                {'pass':'THER_SF3',              'fail':'FAIL_PROC'}, []],
   'THER_SF3'           : ['base_Temperature',  'CThermistor_SF3',         {'pass':'AFH1',                  'fail':'FAIL_PROC'}, []],
   'AFH1'               : ['base_AFH',          'CInitAFH',                {'pass':'PES_SCRN2',             'fail':'FAIL_PROC'}, []],
   'PES_SCRN2'          : ['Servo_Tuning',      'CPESScreens',             {'pass':'PARTICLE_SWP',          'fail':'FAIL_PROC'}, []],
   'PARTICLE_SWP'       : ['Sweep_Base',        'CParticleSweep',          {'pass':'AGC_SCRN',              'fail':'FAIL_PROC'}, []],
   'AGC_SCRN'           : ['Servo_Screens',     'CAGCScreen',              {'pass':'AGC_JOG',               'fail':'FAIL_PROC'}, []],
   'AGC_JOG'            : ['Servo_Tuning',      'CuJog',                   {'pass':'RW_GAP_CAL',            'fail':'FAIL_PROC'}, []],
   'RW_GAP_CAL'         : ['SerialTest',        'CReadWriteGapCal',        {'pass':'LIN_SCREEN1',           'fail':'FAIL_PROC'}, []],
   'LIN_SCREEN1'        : ['Servo_Screens',     'CLinearityScreen',        {'pass':'DNLD_CODE_SIF',         'fail':'FAIL_PROC'}, []],
   'DNLD_CODE_SIF'      : ['Serial_Download',   'CDnldCode',               {'pass':'SIF_CAL',               'fail':'FAIL_PROC'}, [{'FE_0269922_348085_P_SIGMUND_IN_FACTORY': 1}]],
   'SIF_CAL'            : ['base_PRETest',      'CSigmundInFactoryCal',    {'pass':'DNLD_CODE_NO_SIF',      'fail':'FAIL_PROC'}, [{'FE_0269922_348085_P_SIGMUND_IN_FACTORY': 1}]],
   'DNLD_CODE_NO_SIF'   : ['Serial_Download',   'CDnldCode',               {'pass':'SIF_SET_FORMAT',        'fail':'FAIL_PROC'}, [{'FE_0269922_348085_P_SIGMUND_IN_FACTORY': 1}]],
   'SIF_SET_FORMAT'     : ['base_PRETest',      'CSigmundInFactorySetFormat', {'pass':'DISPLAY_RADIUS_KFCI','fail':'FAIL_PROC'}, [{'FE_0269922_348085_P_SIGMUND_IN_FACTORY': 1}]],
   'DISPLAY_RADIUS_KFCI': ['base_SerialTest',   'CReportZonedServoRadiusKFCI',{'pass':'INIT_SYS',           'fail':'FAIL_PROC'}, [{'FE_0269922_348085_P_SIGMUND_IN_FACTORY': 1}]],
   'INIT_SYS'           : ['SerialTest',        'CWriteETF',               {'pass':'WRT_SIM_FILES1',        'fail':'FAIL_PROC'}, []],
   'WRT_SIM_FILES1'     : ['SerialTest',        'CSaveSIMFilesToDUT',      {'pass':'VER_SYS1',              'fail':'FAIL_PROC'}, []],
   'VER_SYS1'           : ['SerialTest',        'CReadETF',                {'pass':'RELOAD_FORMAT0',        'fail':'FAIL_PROC'}, []],
   'RELOAD_FORMAT0'     : ['base_PRETest',      'CReloadFormat',           {'pass':'ZEST',                  'fail':'FAIL_PROC'}, [{'FE_0309959_348085_P_DEFAULT_580KTPI_FOR_DATA_TRACK_SUPPORT': 1}]],
   'ZEST'               : ['Servo_Tuning',      'CZest',                   {'pass':'OPTIZAP_1',             'fail':'FAIL_PROC'}, [{'RUN_ZEST': 1}]],
   'OPTIZAP_1'          : ['base_ZapStates',    'COptiZap',                {'pass':'RELOAD_NOMINAL_BPI',    'fail':'FAIL_PROC'}, []],
   'RELOAD_NOMINAL_BPI' : ['VBAR',              'CReloadBPINominal',       {'pass':'BPINOMINAL',            'fail':'FAIL_PROC'}, [{'FE_0269922_348085_P_SIGMUND_IN_FACTORY': 1}]],
   'BPINOMINAL'         : ['VBAR_Base',         'CBPINom',                 {'pass':'RW_GAP_CAL_02',         'fail':'FAIL_PROC'}, []],
   'RW_GAP_CAL_02'      : ['SerialTest',        'CReadWriteGapCal',        {'pass':'PRE_OPTI',              'fail':'FAIL_PROC'}, [{'FE_0269922_348085_P_SIGMUND_IN_FACTORY': 0}]],
   'PRE_OPTI'           : ['Opti_Read',         'CRdOpti',                 {'pass':'HEAD_SCRN_SMR',         'fail':'FAIL_PROC'}, []],
   'HEAD_SCRN_SMR'      : ['Head_Screen',       'CHeadScreen1',            {'pass':'FAFH_INIT_WRT_PARAM',   'fail':'FAIL_PROC'}, [{'ENABLE_HEAD_SCRN_IN_PRE2': 1, 'SMR': 1}]],
   'FAFH_INIT_WRT_PARAM': ['base_AFH',          'FAFHparamInit_Write',     {'pass':'TPINOMINAL',            'fail':'FAIL_PROC'}, [{'IS_FAFH':1,'FE_AFH3_TO_IMPROVE_TCC':1}]],
   'TPINOMINAL'         : ['VBAR_Base',         'CTPINom',                 {'pass':'PRETRIPLET_ZAP',        'fail':'FAIL_PROC'}, [{'RUN_TPINOMINAL1' : 1}]],
   'PRETRIPLET_ZAP'     : ['base_ZapStates',    'COptiZap',                {'pass':'TRIPLET_OPTI_V2',       'fail':'FAIL_PROC'}, [{'RUN_TPINOMINAL1' : 1}]],
   'TRIPLET_OPTI_V2'    : ['VBAR_Base',         'CVbarTripletOpti',        {'pass':'MultiMatrixTriplet',    'fail':'FAIL_PROC'}, [{'SINGLEPASSFLAWSCAN': 0}]],
   'MultiMatrixTriplet' : ['triplet',           'CMultiMatrixTriplet',     {'pass':'RELOAD_FORMAT1',        'fail':'FAIL_PROC'}, [{'FE_0308035_403980_P_MULTIMATRIX_TRIPLET' : 1, 'SINGLEPASSFLAWSCAN': 1}]],
   'RELOAD_FORMAT1'     : ['base_PRETest',      'CReloadFormat',           {'pass':'POSTTRIPLET_ZAP',       'fail':'FAIL_PROC'}, [{'FE_0273368_348429_TEMP_ENABLE_TPINOMINAL_FOR_ATI_STE' : 1}]],
   'POSTTRIPLET_ZAP'    : ['base_ZapStates',    'COptiZap',                {'pass':'FAFH_FREQ_SELECT',      'fail':'FAIL_PROC'}, [{'FE_0273368_348429_TEMP_ENABLE_TPINOMINAL_FOR_ATI_STE' : 1}]],
   'FAFH_FREQ_SELECT'   : ['base_AFH',          'CFAFH_frequencySelect',   {'pass':'THER_SF3_2',            'fail':'FAIL_PROC'}, [{'IS_FAFH': 1}]],
   'THER_SF3_2'         : ['base_Temperature',  'CThermistor_SF3',         {'pass':'AFH2',                  'fail':'FAIL_PROC'}, []],
   'AFH2'               : ['base_AFH',          'CInitAFH',                {'pass':'WRT_SIM_FILES2',        'fail':'FAIL_PROC'}, []],
   'WRT_SIM_FILES2'     : ['SerialTest',        'CSaveSIMFilesToDUT',      {'pass':'HIRP1A',                'fail':'FAIL_PROC'}, []],
   'HIRP1A'             : ['base_AFH',          'CMeasureAR',              {'pass':'VER_SYS2',              'fail':'FAIL_PROC'}, [{'SKIP_HIRP1A': 0}]],
   'VER_SYS2'           : ['SerialTest',        'CReadETF',                {'pass':'PBIC_DATA_SV_PRE2',     'fail':'FAIL_PROC'}, []],
   'PBIC_DATA_SV_PRE2'  : ['SerialTest',        'CPBI_Data',               {'pass':'SAVE_NOM_FREQ',         'fail':'FAIL_PROC'}, [{'PBIC_SUPPORT' : 1}]],
   'SAVE_NOM_FREQ'      : ['VBAR',              'CSaveNominalFreqFile',    {'pass':'DUMP_BPI_BIN',          'fail':'FAIL_PROC'}, [{'FE_0319957_356688_P_STORE_BPIP_MAX_IN_SIM': 1}]],
   'DUMP_BPI_BIN'       : ['VBAR',              'CDisplayBpiBinFile',      {'pass':'PBIC_DATA_LD',          'fail':'FAIL_PROC'}, [{'REDUCE_LOG_SIZE' : 0}]],
   
   #From CAL2
   'PBIC_DATA_LD'       : ['base_SerialTest',   'CPBI_Data',               {'pass':'LIN_SCREEN2',           'fail':'FAIL_PROC'}, [{'PBIC_SUPPORT' : 1}]],
   'LIN_SCREEN2'        : ['Servo_Screens',     'CLinearityScreen',        {'pass':'RESTORE_SIF_BPI_TO_PC', 'fail':'FAIL_PROC'}, []],
   'RESTORE_SIF_BPI_TO_PC': ['base_PRETest',    'CRestoreSifBpiBinToPCFile',{'pass':'BPINOMINAL2',          'fail':'FAIL_PROC'}, [{'FE_0269922_348085_P_SIGMUND_IN_FACTORY': 1}]],
   'BPINOMINAL2'        : ['VBAR_Base',         'CBPINom',                 {'pass':'ADAPTIVE_UMP',          'fail':'FAIL_PROC'}, []],
   'ADAPTIVE_UMP'       : ['base_CALTest',      'CAdaptiveUmpZone',        {'pass':'PREVBAR_ZAP',           'fail':'FAIL_PROC'}, [{'FE_0284435_504159_P_VAR_MC_UMP_ZONES' : 1}]],
   'PREVBAR_ZAP'        : ['base_ZapStates',    'COptiZap',                {'pass':'PREVBAR_OPTI',          'fail':'FAIL_PROC'}, [{'RUN_PREVBAR_ZAP': 1}]],
   'PREVBAR_OPTI'       : ['Opti_Read',         'CRdOpti',                 {'pass':'ZNDSRV_INFO_1',         'fail':'FAIL_PROC'}, [{'FE_0279318_348429_SPLIT_2DVBAR_MODULES' : 1}]],
   'ZNDSRV_INFO_1'      : ['SerialTest',        'CReportZonedServoInfo',   {'pass':'VBAR_BPI_XFER',         'fail':'FAIL_PROC'}, []],
   'VBAR_BPI_XFER'      : ['VBAR_Base',         'CBPIXfer',                {'pass':'VBAR_ZN_2D',            'fail':'FAIL_PROC'}, [{'FE_0279318_348429_SPLIT_2DVBAR_MODULES' : 1}]],
   'VBAR_ZN_2D'         : ['VBAR_Base',         'C2DVbarZn',               {'pass':'VBAR_ZN_1D',            'fail':'FAIL_PROC'}, [{'FE_0279318_348429_SPLIT_2DVBAR_MODULES' : 1}]],
   'VBAR_ZN_1D'         : ['VBAR_Base',         'C1DVbarZn',               {'pass':'VBAR_SET_ADC',          'fail':'FAIL_PROC'}, [{'FE_0279318_348429_SPLIT_2DVBAR_MODULES' : 1}]],
   'VBAR_SET_ADC'       : ['VBAR_Base',         'CVbarSet_ADC',            {'pass':'VBAR_MARGIN_OPTI',      'fail':'FAIL_PROC'}, [{'FE_0309814_348429_SPLIT_VBAR_MARGIN_MODULES' : 1}]],
   'VBAR_MARGIN_OPTI'   : ['VBAR_Base',         'CVbarMargin_Opti',        {'pass':'VBAR_OTC3',             'fail':'FAIL_PROC'}, [{'FE_0309814_348429_SPLIT_VBAR_MARGIN_MODULES' : 1}]],
   'VBAR_OTC3'          : ['VBAR_Base',         'CVbarOTC',                {'pass':'VBAR_MARGIN_SQZBPI',    'fail':'FAIL_PROC'}, [{'FE_0309814_348429_SPLIT_VBAR_MARGIN_MODULES' : 1, 'FE_0345101_348429_P_AVM_RD_OFFSET_AND_CHANNEL_TUNE' : 1}]],
   'VBAR_MARGIN_SQZBPI' : ['VBAR_Base',         'CVbarMargin_SqzBPI',      {'pass':'VBAR_MARGIN_RLOAD',     'fail':'FAIL_PROC'}, [{'FE_0309814_348429_SPLIT_VBAR_MARGIN_MODULES' : 1}]],
   'VBAR_MARGIN_RLOAD'  : ['VBAR_Base',         'CVbarMargin_MgnRLoad',    {'pass':'VBAR_MARGIN_TPISOVA',   'fail':'FAIL_PROC'}, [{'FE_0309814_348429_SPLIT_VBAR_MARGIN_MODULES' : 1, 'FE_0303725_348429_P_VBAR_MARGIN_RELOAD' : 1}]],
   'VBAR_MARGIN_TPISOVA': ['VBAR_Base',         'CVbarMargin_TPISOVA',     {'pass':'VBAR_MARGIN_OTC',       'fail':'FAIL_PROC'}, [{'FE_0345891_348429_TPIM_SOVA_USING_FIX_TRANSFER' : 1}]],
   'VBAR_MARGIN_OTC'    : ['VBAR_Base',         'CVbarMargin_OTC',         {'pass':'VBAR_MARGIN_ATI',       'fail':'FAIL_PROC'}, [{'FE_0309814_348429_SPLIT_VBAR_MARGIN_MODULES' : 1}]],
   'VBAR_MARGIN_ATI'    : ['VBAR_Base',         'CVbarMargin_ATI',         {'pass':'VBAR_MARGIN_SHMS',      'fail':'FAIL_PROC'}, [{'FE_0309814_348429_SPLIT_VBAR_MARGIN_MODULES' : 1}]],
   'VBAR_MARGIN_SHMS'   : ['VBAR_Base',         'CVbarMargin_SHMS',        {'pass':'VBAR_ADC_REPORT',       'fail':'FAIL_PROC'}, [{'FE_0309814_348429_SPLIT_VBAR_MARGIN_MODULES' : 1, 'FE_0325284_348429_P_VBAR_SMR_HMS' : 1}]],
   'VBAR_ADC_REPORT'    : ['VBAR_Base',         'CVbarReport_ADC',         {'pass':'VBAR_OC2',              'fail':'FAIL_PROC'}, [{'FE_0309814_348429_SPLIT_VBAR_MARGIN_MODULES' : 1}]],
   'VBAR_OC2'           : ['VBAR_Base',         'CVbarOC2',                {'pass':'VBAR_ADC_REPORT2',      'fail':'FAIL_PROC'}, [{'FE_0302539_348429_P_ENABLE_VBAR_OC2' : 1}]],
   'VBAR_ADC_REPORT2'   : ['VBAR_Base',         'CVbarReport_ADC',         {'pass':'VBAR_FMT_PICKER',       'fail':'FAIL_PROC'}, [{'FE_0307316_356688_P_ADC_SUMMARY_OC2' : 1}]],
   'VBAR_FMT_PICKER'    : ['VBAR_Base',         'CVbarFormatPicker',       {'pass':'ZNDSRV_INFO_2',         'fail':'FAIL_PROC'}, [{'FE_0279318_348429_SPLIT_2DVBAR_MODULES' : 1}]],
   'ZNDSRV_INFO_2'      : ['SerialTest',        'CReportZonedServoInfo',   {'pass':'PV_SCRN',               'fail':'FAIL_PROC'}, []],
   'PV_SCRN'            : ['base_CALTest',      'CPVScreen',               {'pass':'WRT_SIM_FILES3',        'fail':'FAIL_PROC'}, []],
   'WRT_SIM_FILES3'     : ['SerialTest',        'CSaveSIMFilesToDUT',      {'pass':'VER_SYS3',              'fail':'FAIL_PROC'}, []],
   'VER_SYS3'           : ['SerialTest',        'CReadETF',                {'pass':'WRITE_OD_ID',           'fail':'FAIL_PROC'}, []],
   'WRITE_OD_ID'        : ['base_CALTest',      'CWriteODIDGuardBand',     {'pass':'ZONEINSERTION',         'fail':'FAIL_PROC'}, []],
   'ZONEINSERTION'      : ['Opti_Read',         'CRdOptiZoneInsertion',    {'pass':'OPTIZAP_2',             'fail':'FAIL_PROC'}, [{'FE_0271421_403980_P_ZONE_COPY_OPTIONS': 1} ]],
   'OPTIZAP_2'          : ['base_ZapStates',    'COptiZap',                {'pass':'VBAR_OTC2',             'fail':'FAIL_PROC'}, []],
   'VBAR_OTC2'          : ['VBAR_Base',         'CVbarOTC',                {'pass':'READ_OPTI',             'fail':'FAIL_PROC'}, [{'FE_348429_0255607_ENABLE_BAND_WRITE_T251': 1, 'VBAR_ADP_EQUAL_ADC': 0}]],
   'READ_OPTI'          : ['SerialTest',        'CRdOpti_2DVBAR',          {'pass':'HMSC_DATA',             'fail':'FAIL_PROC'}, []],
   'HMSC_DATA'          : ['VBAR_Base',         'CVbarHMS_ZapOffEnd',      {'pass':'HMSC_DATA_SQZ',         'fail':'FAIL_PROC'}, []],
   'HMSC_DATA_SQZ'      : ['VBAR_Base',         'CVbarHMS_ZapOffEnd',      {'pass':'VBAR_OTC',              'fail':'FAIL_PROC'}, [{'FE_0338929_348429_P_ENABLE_SQZ_HMS': 1}]],
   'VBAR_OTC'           : ['VBAR_Base',         'CVbarOTC',                {'pass':'SEGMENTED_BER',         'fail':'FAIL_PROC'}, [{'VBAR_2D': 1}]],
   'SEGMENTED_BER'      : ['base_CALTest',      'CSegmentedErrRate',       {'pass':'SEG_BER_SQZ',           'fail':'FAIL_PROC'}, [{'FE_0304753_348085_P_SEGMENTED_BER': 1}]],
   'SEG_BER_SQZ'        : ['base_CALTest',      'CSegmentedErrRate',       {'pass':'WEAK_WR_OW1',           'fail':'FAIL_PROC'}, [{'FE_0304753_348085_P_SEGMENTED_BER': 1, 'SMR' : 1}]],
   'WEAK_WR_OW1'        : ['Head_Measure',      'CWeakWriteOWTest',        {'pass':'VER_SYS4',              'fail':'FAIL_PROC'}, []],
   'VER_SYS4'           : ['SerialTest',        'CReadETF',                {'pass':'DUMP_PREAMP',           'fail':'FAIL_PROC'}, []],
   'DUMP_PREAMP'        : ['base_Preamp',       'CDumpPreamp',             {'pass':'PBIC_DATA_SV_CAL2',     'fail':'FAIL_PROC'}, []],
   'PBIC_DATA_SV_CAL2'  : ['SerialTest',        'CPBI_Data',               {'pass':'PBIC_DATA_LD2',         'fail':'FAIL_PROC'}, [{'PBIC_SUPPORT' : 1}]],

   #From FNC2
   'PBIC_DATA_LD2'         : ['base_SerialTest',   'CPBI_Data',                  {'pass':'CHK_PCBA_SN',           'fail':'FAIL_PROC'}, [{'PBIC_SUPPORT' : 1}]],
   'CHK_PCBA_SN'           : ['PCBA_Base',         'CCheckPCBA_SN',              {'pass':'RESTORE_SIF_BPI_TO_PC2','fail':'FAIL_PROC'}, [{'WA_REMOVE_PCBA_SN_CHK_FRM_STATE_TABLE_DURING_EM_PHASE': 0}]],
   'RESTORE_SIF_BPI_TO_PC2': ['base_PRETest',      'CRestoreSifBpiBinToPCFile',  {'pass':'CBD_MEASUREMENT',       'fail':'FAIL_PROC'}, [{'FE_0269922_348085_P_SIGMUND_IN_FACTORY': 1}]],
   'CBD_MEASUREMENT'       : ['Opti_Read',         'CMeasureCBD',                {'pass':'DISP_OCLIM',            'fail':'FAIL_PROC'}, []],
   'DISP_OCLIM'            : ['base_FNCTest',      'CDisplayOCLIM',              {'pass':'ZAP',                   'fail':'FAIL_PROC'}, []],
   'ZAP'                   : ['base_ZapStates',    'CZap',                       {'pass':'DETCR_PREAMP_SETUP_0',  'fail':'FAIL_PROC'}, []],
   'DETCR_PREAMP_SETUP_0'  : ['base_Preamp',       'CDETCRPreampSetup',          {'pass':'FAFH_TRACK_PREP_1',     'fail':'FAIL_PROC'}, [{'IS_FAFH': 1,'FE_228371_DETCR_TA_SERVO_CODE_SUPPORTED': 1}]],
   'FAFH_TRACK_PREP_1'     : ['base_AFH',          'CFAFH_trackPrep',            {'pass':'FAFH_DISPLAY',          'fail':'FAIL_PROC'}, [{'IS_FAFH': 1}]],
   'FAFH_DISPLAY'          : ['base_AFH',          'T74PrintOut',                {'pass':'SET_CUST_OCLIM',        'fail':'FAIL_PROC'}, [{'DISPLAY_FAFH_PARAM_FILE_FOR_DEBUG': 1}]],
   'SET_CUST_OCLIM'        : ['base_FNCTest',      'CSetCustomerOCLIM',          {'pass':'PES_SCRN3',             'fail':'FAIL_PROC'}, [{'FE_0243459_348085_DUAL_OCLIM_CUSTOMER_CERT': 1}]],
   'PES_SCRN3'             : ['Servo_Tuning',      'CPESScreens',                {'pass':'ADV_SWEEP',             'fail':'FAIL_PROC'}, []],
   'ADV_SWEEP'             : ['Sweep_Base',        'CAdvanceSweep',              {'pass':'DISP_OCLIM_2',          'fail':'FAIL_PROC'}, []],
   'DISP_OCLIM_2'          : ['base_FNCTest',      'CDisplayOCLIM',              {'pass':'ZNDSRV_INFO_3',         'fail':'FAIL_PROC'}, []],
   'ZNDSRV_INFO_3'         : ['SerialTest',        'CReportZonedServoInfo',      {'pass':'GT_WRITE',              'fail':'FAIL_PROC'}, []],
   'GT_WRITE'              : ['base_FNCTest',      'CGTWrite',                   {'pass':'TUNE_ATS',              'fail':'FAIL_PROC'}, [{'FE_0363840_356688_P_ENABLE_GT_WRITE': 1}]],
   'TUNE_ATS'              : ['Servo_Tuning',      'CATSTuning',                 {'pass':'D_FLAWSCAN',            'fail':'FAIL_PROC'}, [{'SINGLEPASSFLAWSCAN': 1, 'RUN_ATS_SEEK_TUNING': 1}]],
   'D_FLAWSCAN'            : ['Flawscan_AFS',      'CDataFlawScan',              {'pass':'PAD_MC_ZONE_BOUNDARY',  'fail':'FAIL_PROC'}, [{'SINGLEPASSFLAWSCAN': 0}]],
   'PAD_MC_ZONE_BOUNDARY'  : ['base_FNCTest',      'CPadMcZoneBoundary',         {'pass':'SPF',                   'fail':'FAIL_PROC'}, [{'SINGLEPASSFLAWSCAN': 0}]],
   'SPF'                   : ['Flawscan_SPFS',     'CSinglePassFlawScan',        {'pass':'PAD_MC_ZONE_BOUNDARY2', 'fail':'FAIL_PROC'}, [{'SINGLEPASSFLAWSCAN': 1}]],
   'PAD_MC_ZONE_BOUNDARY2' : ['base_FNCTest',      'CPadMcZoneBoundary',         {'pass':'SVO_SCRN',              'fail':'FAIL_PROC'}, [{'SINGLEPASSFLAWSCAN': 1}]],
   'SVO_SCRN'              : ['Servo_Screens',     'CServoScreens',              {'pass':'VAR_SPARES',            'fail':'FAIL_PROC'}, []],
   'VAR_SPARES'            : ['base_FNCTest',      'CVarSpares',                 {'pass':'THER_SF3_3',            'fail':'FAIL_PROC'}, [{'VARIABLE_SPARES': 1}]],
   'THER_SF3_3'            : ['base_Temperature',  'CThermistor_SF3',            {'pass':'READ_SCRN2',            'fail':'FAIL_PROC'}, []],
   'READ_SCRN2'            : ['SerialTest',        'CDeltaRSSScreen',            {'pass':'SQZ_WRITE',             'fail':'FAIL_PROC'}, []],
   'SQZ_WRITE'             : ['SerialTest',        'CSQZWrite',                  {'pass':'ENCROACH_SCRN',         'fail':'FAIL_PROC'}, [{'FE_0252331_504159_SHINGLE_WRITE': 1, 'SMR': 1}]],
   'ENCROACH_SCRN'         : ['base_RssScreens',   'CEncroachment_Screens',      {'pass':'INTRA_BAND_SCRN',       'fail':'FAIL_PROC'}, [{'FE_0111793_347508_PHARAOH_TTR': 0}]],
   'INTRA_BAND_SCRN'       : ['base_RssScreens',   'CWrite_Screens',             {'pass':'INTER_BAND_SCRN_500',   'fail':'FAIL_PROC'}, [{'SMR': 1, 'FE_0253166_504159_MERGE_FAT_SLIM': 0}]],
   'INTER_BAND_SCRN_500'   : ['base_RssScreens',   'CWrite_Screens',             {'pass':'INTER_BAND_SCRN',       'fail':'FAIL_PROC'}, [{'SMR': 1, 'FE_0253166_504159_MERGE_FAT_SLIM': 0}]],
   'INTER_BAND_SCRN'       : ['base_RssScreens',   'CWrite_Screens',             {'pass':'WRITE_SCRN',            'fail':'FAIL_PROC'}, [{'SMR': 1, 'FE_0253166_504159_MERGE_FAT_SLIM': 0}]],
   'WRITE_SCRN'            : ['base_RssScreens',   'CWrite_Screens',             {'pass':'WRITE_SCRN_10K',        'fail':'FAIL_PROC'}, []],
   'WRITE_SCRN_10K'        : ['base_RssScreens',   'CWrite_Screens',             {'pass':'OTC_BANDSCRN',          'fail':'FAIL_PROC'}, []],
   'OTC_BANDSCRN'          : ['VBAR_Base',         'CVbarInterbandScrn',         {'pass':'WEAK_WR_OW3',           'fail':'FAIL_PROC'}, [{'FE_0293889_348429_VBAR_MARGIN_BY_OTCTP_INTERBAND_MEAS' :1}]],
   'WEAK_WR_OW3'           : ['Head_Measure',      'CWeakWriteOWTest',           {'pass':'HEAD_SCRN2',            'fail':'FAIL_PROC'}, []],
   'HEAD_SCRN2'            : ['Head_Screen',       'CHeadScreen2',               {'pass':'RAMP_DOWN',             'fail':'FAIL_PROC'}, [{'ENABLE_HEAD_SCRN_IN_FNC2': 1, 'SMR': 1}]],
   'RAMP_DOWN'             : ['base_Temperature',  'CRampDown',                  {'pass':'AFH3',                  'fail':'FAIL_PROC'}, []],
   'AFH3'                  : ['base_AFH',          'CInitAFH',                   {'pass':'WRT_SIM_FILES4',        'fail':'FAIL_PROC'}, [{'FE_AFH3_TO_IMPROVE_TCC': 1}]],
   'WRT_SIM_FILES4'        : ['SerialTest',        'CSaveSIMFilesToDUT',         {'pass':'FAFH_CAL_TEMP_1',       'fail':'FAIL_PROC'}, [{'FE_AFH3_TO_IMPROVE_TCC': 1}]],
   'FAFH_CAL_TEMP_1'       : ['base_AFH',          'CFAFH_calibration',          {'pass':'FAFH_DISPLAY1',         'fail':'FAIL_PROC'}, [{'IS_FAFH': 1}]],
   'FAFH_DISPLAY1'         : ['base_AFH',          'T74PrintOut',                {'pass':'READ_SCRN3',            'fail':'FAIL_PROC'}, [{'DISPLAY_FAFH_PARAM_FILE_FOR_DEBUG': 1}]],
   'READ_SCRN3'            : ['SerialTest',        'CDeltaRSSScreen',            {'pass':'DNLD_BRG_IV',           'fail':'FAIL_PROC'}, []],
   'DNLD_BRG_IV'           : ['Serial_Download',   'CDnldCode',                  {'pass':'CAP_Modify',            'fail':'FAIL_PROC'}, []],
   'CAP_Modify'            : ['base_IntfTest',     'CCapacityScreen',            {'pass':'QUICK_FORMAT',          'fail':'FAIL_PROC'}, []],
   'QUICK_FORMAT'          : ['SerialTest',        'CQuickFmt',                  {'pass':'SERIAL_FMT',            'fail':'FAIL_PROC'}, []],
   'SERIAL_FMT'            : ['Serial_SerFmt',     'CSerialFormat',              {'pass':'DNLD_U_CODE',           'fail':'FAIL_PROC'},[]],
   #'FULL_WRITE'           : ['base_IntfTest',     'CPackWrite',                 {'pass':'DNLD_U_CODE',           'fail':'FAIL_PROC'}, []],
   'DNLD_U_CODE'           : ['Serial_Download',   'CDnldCode',                  {'pass':'RESET_SMART',           'fail':'FAIL_PROC'}, []],
   'RESET_SMART'           : ['base_IntfTest',     'CClearSMART',                {'pass':'RESET_DOS',             'fail':'FAIL_PROC'}, []],
   'RESET_DOS'             : ['base_IntfTest',     'CClearDOS',                  {'pass':'END_TEST',              'fail':'FAIL_PROC'}, []],
   'END_TEST'              : ['Serial_Exit',       'CEndTesting',                {'pass':'COMPLETE',              'fail':'FAIL_PROC'}, []],
   'FAIL_PROC'             : ['Serial_Exit',       'CFailProc',                  {'pass':'COMPLETE',              'fail':'COMPLETE'},  []],
   'COMPLETE'              : [0],
}


# State Input Arguments Table
StateParams['PRE2'] = {
   'DNLD_CODE'          : {'CODES': ['IMG', 'RAPT', 'CMB'],},
   'DNLD_CODE_SIF'      : "{'CODES': ['CFW3','S_OVL3'],'SKIP_CODE': 0,'registerOvl':'S_OVL3'}",
   'DNLD_CODE_NO_SIF'   : "{'CODES': ['CFW','S_OVL'],'SKIP_CODE': 0,'registerOvl':'S_OVL'}",
   'SIF_SET_FORMAT'     : "{'FORMAT_TO_SET' : 'BPI_NOMINAL_FORMAT',}",
   'RELOAD_FORMAT0'     : "{'MODE' : 'TPI', 'TPI' : TP.Default_TPI_Format }",
   'RELOAD_NOMINAL_BPI' : "{'FORMAT_TO_SET' : 'BPI_NOMINAL_FORMAT',}",
   'THER_SF3'           : {'PERFORM_COOLING_STEPS':0,},
   'AFH1'               : {'exec231': 0, 'clearCM_SIM': 1, 'brnsh_chk': 0, 'brnsh_chk2': 0, 'deltaVBAR_chk': 0, 'AFH_V3BAR_phase5': 0,},
   'AFH2'               : {'exec231': 0, 'clearCM_SIM': 0, 'brnsh_chk': 1, 'brnsh_chk2': 0, 'deltaVBAR_chk': 0, 'AFH_V3BAR_phase5': 0,},
   'HIRP1A'             : {'exec231':1},
   'LIN_SCREEN1'        : {'CAL' : 'ON'},
   'LIN_SCREEN2'        : {'CAL' : 'ON'},
   'OPTIZAP_2'          : {'OPTIZAP_TRACK_LIMIT': 0x0220,}, # overwrite the default zap track limit
   'PARTICLE_SWP'       : {'MODE':'SF3',},
   'PES_SCRN'           : {'disableUnsafeRetry':1},
   'PES_SCRN2'          : {'SPC_ID' : 2, 'disableUnsafeRetry':1},
   'READ_OPTI'          : {'RUN_TGT_OPTI' : 0, 'BAND_WRITE_250': 1, 'RST_OFFSET' : 1, 'OFF_LOG' : False, 'BAND_WRITE_251' : 1, 'SANITY_CHECK_CHANNEL_PARAMS': 0, 'MAX_ERR_RATE' : -80, 'ON_TRK_BER_ZONES': "TP.BPIMeasureZone", 'SQZ_WRT_BER_ZONES': "TP.BPIMeasureZone"},
   'RELOAD_FORMAT'      : {'BPI' : 140,},
   'RELOAD_FORMAT1'     : "{'MODE' : 'TPI', 'TPI' : TP.Default_TPI_Format }",
   'POSTTRIPLET_ZAP'    : {'ZONES': "TP.Triplet_Zones", 'MINIZAP_OAR': 0, 'OPTIZAP_TRACK_LIMIT': 0x0A1E},
   'TPINOMINAL'         : {'DSS_MEASUREMENT_ONLY': 1, 'TPI_NOMINAL_SET_FMT_ZONES': "TP.Triplet_Zones"},
   'RW_GAP_CAL_02'      : {'SKIP_SYS_ZONE' : 1},
   'TRIPLET_OPTI_V2'    : {'UPDATE_SQUEEZE_MICROJOG': 1 },
   'SERVO_OPTI'         : {'GainThreshold' : 3.8, 'StartFrequency' : 7800, 'EndFrequency': 8200},
   'WRITE_OD_ID'        : {'OD_Pad': 20, 'ID_Pad': 20},
   'WRT_SIM_FILES1'     : {'saveFiles' : "TP.filesToSave",},
   'WRT_SIM_FILES2'     : {'saveFiles' : ['AFH',],},
   'WRT_SIM_FILES3'     : {'saveFiles' : ['RW_GAP',],},
   'BPINOMINAL'         : {'RUN_MRBIAS_OPTI' : 0 },
   'PRETRIPLET_ZAP'     : {'ZONES': "TP.Triplet_Zones", 'MINIZAP_OAR': 0, 'OPTIZAP_TRACK_LIMIT': 0x0A1E},
   'PREVBAR_OPTI'       : {'ZONES': "TP.VBAR_measured_Zones", 'ON_TRK_BER_ZONES': "TP.Measured_2D_Zones", 'param': 'simple_OptiPrm_251_short_tune_znAlign'},
   'VBAR_MARGIN_RLOAD'  : {'MINIZAP_ZONES': "TP.BPIMeasureZone", 'ON_TRK_BER_ZONES': "TP.BPIMeasureZone", 'SQZ_BPIC_ZONES': "TP.BPIMeasureZone", 'OTC_MARGIN_ZONES': "TP.BPIMeasureZone", 'BAND_WRITE_251' : 1},
   'VBAR_SET_ADC'       : {'UPDATE_SQUEEZE_MICROJOG' : 1 ,'ACTIVE_ZONES': "TP.BPIMeasureZone"},
   'VBAR_MARGIN_SQZBPI' : {'SQZ_BPIC_ZONES': "TP.BPIMeasureZone"},
   'VBAR_MARGIN_OTC'    : {'MINIZAP_ZONES': "TP.BPIMeasureZone", 'ON_TRK_BER_ZONES': "TP.BPIMeasureZone", 'OTC_MARGIN_ZONES': "TP.BPIMeasureZone"},
   'SEGMENTED_BER'      : {'ZONES': "TP.SegBER_MeasureZone"},
   'SEG_BER_SQZ'        : {'ZONES': "TP.SegSQZBER_MeasureZone"},
   'VBAR_MARGIN_SHMS'   : {'ZONES': "TP.BPIMeasureZone_TTR"},
   'VBAR_OTC'           : {'OTC_MEASURE_ZONES': "TP.BPIMeasureZone",},
   'VBAR_OTC2'          : {'OTC_MEASURE_ZONES': "TP.BPIMeasureZone",},
   'VBAR_OTC3'          : {'OTC_MEASURE_ZONES': "TP.BPIMeasureZone",},
   'VBAR_ADC_REPORT'    : {'UPDATE_SQUEEZE_MICROJOG' : 1 },
   'VBAR_ADC_REPORT2'   : {'UPDATE_SQUEEZE_MICROJOG' : 1 },
   'VBAR_MARGIN_OPTI'   : {'ZAP_LIMIT' : 0x0520, 'BAND_WRITE_251' : 1, 'MINIZAP_ZONES': "TP.BPIMeasureZone", 'ON_TRK_BER_ZONES': "TP.BPIMeasureZone", 'SQZ_BPIC_ZONES': "TP.BPIMeasureZone", 'OTC_MARGIN_ZONES': "TP.BPIMeasureZone"},
   'VBAR_FMT_PICKER'    : {'UPDATE_SQUEEZE_MICROJOG' : 1 ,'UPDATE_SHINGLE_DIRECTION': 1},
   'PREVBAR_ZAP'        : {'ZONES': "TP.VBAR_measured_Zones", 'OPTIZAP_TRACK_LIMIT': 0x0220},
   'PRE_OPTI'           : {'param': 'simple_OptiPrm_251_short_tune', 'ZONES': "TP.Channel_PreOpti_Zones", 'ON_TRK_BER_ZONES': "TP.Measured_BPINOMINAL_Zones"},
   'OPTIZAP_1'          : {'ZONES': "TP.Channel_PreOpti_Zones", 'OPTIZAP_TRACK_LIMIT': 0x0220, 'MINIZAP_OAR': False},
   'HEAD_SCRN_SMR'      : {'TSHR': 1, 'FAIL_SAFE': 0, 'NO_ADJUST': 1},
   'WEAK_WR_OW1'        : {'OW_ZONE': [4], 'POSITION': [198], 'SMROW_ZONE': [1,8], 'SMR_POSITION': [198]},
   'VBAR_MARGIN_TPISOVA': {'TPISOVA_MARGIN_ZONES': "TP.BPIMeasureZone"},
   
   #From FNC2
   'DNLD_BRG_IV'        : "{'CODES': ['TGT3','OVL3','IV3'],}",
   'DNLD_U_CODE'        : "{'CODES': ['TGT','OVL'],}",
   'AFH3'               : "{'exec231': 1, 'clearCM_SIM': 0, 'brnsh_chk': 0, 'brnsh_chk2': 0, 'brnsh_chk3': 1, 'deltaVBAR_chk': 0, 'updateClr': 0, 'AFH_V3BAR_phase5': 0,}",
   'FAFH_CAL_TEMP_1'    : "{'tempIndexStr' : 'FAFH_HOT_MEASUREMENT'}",
   'PES_SCRN3'          : "{'CYL_IS_LOGICAL' : 1, 'SPC_ID' : 3}",
   'READ_SCRN2'         : "{'ODD_ZONES' : 0, 'RST_RD_OFFSET' : 1, 'MAX_ERR_RATE' : -80}",
   'READ_SCRN3'         : "{'ODD_ZONES' : 0, 'RST_RD_OFFSET' : 1, 'MAX_ERR_RATE' : -80}",
   'HEAD_SCRN2'         : "{'RST_RD_OFFSET' : 1, 'MAX_ERR_RATE' : -80, 'TSHR': 1, 'FAIL_SAFE': 0}",
   'WRT_SIM_FILES4'     : "{'saveFiles' : ['AFH']}",
   'WRITE_SCRN'         : "{'RUN_EAW_SCRN_TLEVEL10' : 1, 'input_dict': 'TP.prm_ATI_51_WRT_SCRN'}",
   'WRITE_SCRN_10K'     : "{'RUN_EAW_SCRN_TLEVEL10' : 1, 'input_dict': 'TP.prm_ATI_51_WRT_SCRN'}",
   'INTER_BAND_SCRN'    : "{'RUN_EAW_SCRN_TLEVEL10' : 1, 'input_dict': 'TP.prm_ATI_51_WRT_SCRN'}",
   'INTER_BAND_SCRN_500': "{'RUN_EAW_SCRN_TLEVEL10' : 1, 'input_dict': 'TP.prm_ATI_51_WRT_SCRN'}",
   'INTRA_BAND_SCRN'    : "{'RUN_EAW_SCRN_TLEVEL10' : 1, 'input_dict': 'TP.prm_ATI_51_WRT_SCRN'}",
   'OTC_BANDSCRN'       : {'ZONES': "[0, 4, 8, 75, 148]"},
   'WEAK_WR_OW3'        : {'OW_ZONE': [4], 'POSITION': [100], 'SMROW_ZONE': [1,8], 'SMR_POSITION': [100,50]},
   'SERIAL_FMT'         : "{'FORMAT_OPTIONS': 'TP.formatOptions'}",
}

###################################################################################################################
# State Transition Table
StateTable['FNC2'] = {
   #-----------------------------------------------------------------------------------------------------------------------------------------------
   #  State                   Module               Method                        Transitions                                           Optional by
   #                                                                                                                                   GOTF  'G'
   #-----------------------------------------------------------------------------------------------------------------------------------------------
   'INIT'                  : ['Serial_Init',       'CInitTesting',               {'pass':'PBIC_DATA_LD',          'fail':'FAIL_PROC'}, []],
   'PBIC_DATA_LD'          : ['base_SerialTest',   'CPBI_Data',                  {'pass':'CHK_PCBA_SN',           'fail':'FAIL_PROC'}, [{'PBIC_SUPPORT' : 1}]],
   'CHK_PCBA_SN'           : ['PCBA_Base',         'CCheckPCBA_SN',              {'pass':'RESTORE_SIF_BPI_TO_PC', 'fail':'FAIL_PROC'}, [{'WA_REMOVE_PCBA_SN_CHK_FRM_STATE_TABLE_DURING_EM_PHASE': 0}]],
   'RESTORE_SIF_BPI_TO_PC' : ['base_PRETest',      'CRestoreSifBpiBinToPCFile',  {'pass':'CBD_MEASUREMENT',       'fail':'FAIL_PROC'}, [{'FE_0269922_348085_P_SIGMUND_IN_FACTORY': 1}]],
   'CBD_MEASUREMENT'       : ['Opti_Read',         'CMeasureCBD',                {'pass':'DISP_OCLIM',            'fail':'FAIL_PROC'}, []],
   'DISP_OCLIM'            : ['base_FNCTest',      'CDisplayOCLIM',              {'pass':'ZAP',                   'fail':'FAIL_PROC'}, []],
   'ZAP'                   : ['base_ZapStates',    'CZap',                       {'pass':'DETCR_PREAMP_SETUP_0',  'fail':'FAIL_PROC'}, []],
   'DETCR_PREAMP_SETUP_0'  : ['base_Preamp',       'CDETCRPreampSetup',          {'pass':'FAFH_TRACK_PREP_1',     'fail':'FAIL_PROC'}, [{'IS_FAFH': 1,'FE_228371_DETCR_TA_SERVO_CODE_SUPPORTED': 1}]],
   'FAFH_TRACK_PREP_1'     : ['base_AFH',          'CFAFH_trackPrep',            {'pass':'FAFH_DISPLAY',          'fail':'FAIL_PROC'}, [{'IS_FAFH': 1}]],
   'FAFH_DISPLAY'          : ['base_AFH',          'T74PrintOut',                {'pass':'SET_CUST_OCLIM',        'fail':'FAIL_PROC'}, [{'DISPLAY_FAFH_PARAM_FILE_FOR_DEBUG': 1}]],
   'SET_CUST_OCLIM'        : ['base_FNCTest',      'CSetCustomerOCLIM',          {'pass':'PES_SCRN',              'fail':'FAIL_PROC'}, [{'FE_0243459_348085_DUAL_OCLIM_CUSTOMER_CERT': 1}]],
   'PES_SCRN'              : ['Servo_Tuning',      'CPESScreens',                {'pass':'ADV_SWEEP',             'fail':'FAIL_PROC'}, []],
   'ADV_SWEEP'             : ['Sweep_Base',        'CAdvanceSweep',              {'pass':'DISP_OCLIM_2',          'fail':'FAIL_PROC'}, []],
   'DISP_OCLIM_2'          : ['base_FNCTest',      'CDisplayOCLIM',              {'pass':'ZNDSRV_INFO_3',         'fail':'FAIL_PROC'}, []],
   'ZNDSRV_INFO_3'         : ['SerialTest',        'CReportZonedServoInfo',      {'pass':'GT_WRITE',              'fail':'FAIL_PROC'}, []],
   'GT_WRITE'              : ['base_FNCTest',      'CGTWrite',                   {'pass':'TUNE_ATS',              'fail':'FAIL_PROC'}, [{'FE_0363840_356688_P_ENABLE_GT_WRITE': 1}]],
   'TUNE_ATS'              : ['Servo_Tuning',      'CATSTuning',                 {'pass':'SPF',                   'fail':'FAIL_PROC'}, [{'SINGLEPASSFLAWSCAN': 1, 'RUN_ATS_SEEK_TUNING': 1}]],
   'SPF'                   : ['Flawscan_SPFS',     'CSinglePassFlawScan',        {'pass':'PAD_MC_ZONE_BOUNDARY2', 'fail':'FAIL_PROC'}, [{'SINGLEPASSFLAWSCAN': 1}]],
   'PAD_MC_ZONE_BOUNDARY2' : ['base_FNCTest',      'CPadMcZoneBoundary',         {'pass':'SVO_SCRN',              'fail':'FAIL_PROC'}, [{'SINGLEPASSFLAWSCAN': 1}]],
   'SVO_SCRN'              : ['Servo_Screens',     'CServoScreens',              {'pass':'VAR_SPARES',            'fail':'FAIL_PROC'}, []],
   'VAR_SPARES'            : ['base_FNCTest',      'CVarSpares',                 {'pass':'THER_SF3_3',            'fail':'FAIL_PROC'}, [{'VARIABLE_SPARES': 1}]],
   'THER_SF3_3'            : ['base_Temperature',  'CThermistor_SF3',            {'pass':'READ_SCRN2',            'fail':'FAIL_PROC'}, []],
   'READ_SCRN2'            : ['SerialTest',        'CDeltaRSSScreen',            {'pass':'SQZ_WRITE',             'fail':'FAIL_PROC'}, []],
   'SQZ_WRITE'             : ['SerialTest',        'CSQZWrite',                  {'pass':'ENCROACH_SCRN',         'fail':'FAIL_PROC'}, [{'FE_0252331_504159_SHINGLE_WRITE': 1, 'SMR': 1}]],
   'ENCROACH_SCRN'         : ['base_RssScreens',   'CEncroachment_Screens',      {'pass':'INTRA_BAND_SCRN',       'fail':'FAIL_PROC'}, [{'FE_0111793_347508_PHARAOH_TTR': 0}]],
   'INTRA_BAND_SCRN'       : ['base_RssScreens',   'CWrite_Screens',             {'pass':'INTER_BAND_SCRN_500',   'fail':'FAIL_PROC'}, [{'SMR': 1, 'FE_0253166_504159_MERGE_FAT_SLIM': 0}]],
   'INTER_BAND_SCRN_500'   : ['base_RssScreens',   'CWrite_Screens',             {'pass':'INTER_BAND_SCRN',       'fail':'FAIL_PROC'}, [{'SMR': 1, 'FE_0253166_504159_MERGE_FAT_SLIM': 0}]],
   'INTER_BAND_SCRN'       : ['base_RssScreens',   'CWrite_Screens',             {'pass':'WRITE_SCRN',            'fail':'FAIL_PROC'}, [{'SMR': 1, 'FE_0253166_504159_MERGE_FAT_SLIM': 0}]],
   'WRITE_SCRN'            : ['base_RssScreens',   'CWrite_Screens',             {'pass':'WRITE_SCRN_10K',        'fail':'FAIL_PROC'}, []],
   'WRITE_SCRN_10K'        : ['base_RssScreens',   'CWrite_Screens',             {'pass':'OTC_BANDSCRN',          'fail':'FAIL_PROC'}, []],
   'OTC_BANDSCRN'          : ['VBAR_Base',         'CVbarInterbandScrn',         {'pass':'WEAK_WR_OW3',           'fail':'FAIL_PROC'}, [{'FE_0293889_348429_VBAR_MARGIN_BY_OTCTP_INTERBAND_MEAS' :1}]],
   'WEAK_WR_OW3'           : ['Head_Measure',      'CWeakWriteOWTest',           {'pass':'HEAD_SCRN2',            'fail':'FAIL_PROC'}, []],
   'HEAD_SCRN2'            : ['Head_Screen',       'CHeadScreen2',               {'pass':'RAMP_DOWN',             'fail':'FAIL_PROC'}, [{'ENABLE_HEAD_SCRN_IN_FNC2': 1, 'SMR': 1}]],
   'RAMP_DOWN'             : ['base_Temperature',  'CRampDown',                  {'pass':'AFH3',                  'fail':'FAIL_PROC'}, []],
   'AFH3'                  : ['base_AFH',          'CInitAFH',                   {'pass':'WRT_SIM_FILES1',        'fail':'FAIL_PROC'}, [{'FE_AFH3_TO_IMPROVE_TCC': 1}]],
   'WRT_SIM_FILES1'        : ['SerialTest',        'CSaveSIMFilesToDUT',         {'pass':'FAFH_CAL_TEMP_1',       'fail':'FAIL_PROC'}, [{'FE_AFH3_TO_IMPROVE_TCC': 1}]],
   'FAFH_CAL_TEMP_1'       : ['base_AFH',          'CFAFH_calibration',          {'pass':'FAFH_DISPLAY1',         'fail':'FAIL_PROC'}, [{'IS_FAFH': 1}]],
   'FAFH_DISPLAY1'         : ['base_AFH',          'T74PrintOut',                {'pass':'READ_SCRN3',            'fail':'FAIL_PROC'}, [{'DISPLAY_FAFH_PARAM_FILE_FOR_DEBUG': 1}]],
   'READ_SCRN3'            : ['SerialTest',        'CDeltaRSSScreen',            {'pass':'DNLD_BRG_IV',           'fail':'FAIL_PROC'}, []],
   'DNLD_BRG_IV'           : ['Serial_Download',   'CDnldCode',                  {'pass':'CAP_Modify',            'fail':'FAIL_PROC'}, []],
   'CAP_Modify'            : ['base_IntfTest',     'CCapacityScreen',            {'pass':'QUICK_FORMAT',          'fail':'FAIL_PROC'}, []],
   'QUICK_FORMAT'          : ['SerialTest',        'CQuickFmt',                  {'pass':'SERIAL_FMT',            'fail':'FAIL_PROC'}, []],
   'SERIAL_FMT'            : ['Serial_SerFmt',     'CSerialFormat',              {'pass':'DNLD_U_CODE',           'fail':'FAIL_PROC'},[]],
   #'FULL_WRITE'           : ['base_IntfTest',     'CPackWrite',                 {'pass':'DNLD_U_CODE',           'fail':'FAIL_PROC'}, []],
   'DNLD_U_CODE'           : ['Serial_Download',   'CDnldCode',                  {'pass':'RESET_SMART',           'fail':'FAIL_PROC'}, []],
   'RESET_SMART'           : ['base_IntfTest',     'CClearSMART',                {'pass':'RESET_DOS',             'fail':'FAIL_PROC'}, []],
   'RESET_DOS'             : ['base_IntfTest',     'CClearDOS',                  {'pass':'END_TEST',              'fail':'FAIL_PROC'}, []],
   'END_TEST'              : ['Serial_Exit',       'CEndTesting',                {'pass':'COMPLETE',              'fail':'FAIL_PROC'}, []],
   'FAIL_PROC'             : ['Serial_Exit',       'CFailProc',                  {'pass':'COMPLETE',              'fail':'COMPLETE'},  []],
   'COMPLETE'              : [0,],
}


StateParams['FNC2'] = {
   'INIT'               : "{'GET_WEDGE_INFO': True}",
   'DNLD_BRG_IV'        : "{'CODES': ['TGT3','OVL3','IV3'],}",
   'DNLD_U_CODE'        : "{'CODES': ['TGT','OVL'],}",
   'AFH3'               : "{'exec231': 1, 'clearCM_SIM': 0, 'brnsh_chk': 0, 'brnsh_chk2': 0, 'brnsh_chk3': 1, 'deltaVBAR_chk': 0, 'updateClr': 0, 'AFH_V3BAR_phase5': 0,}",
   'FAFH_CAL_TEMP_1'    : "{'tempIndexStr' : 'FAFH_HOT_MEASUREMENT'}",
   'PES_SCRN'           : "{'CYL_IS_LOGICAL' : 1, 'SPC_ID' : 3}",
   'READ_SCRN2'         : "{'ODD_ZONES' : 0, 'RST_RD_OFFSET' : 1, 'MAX_ERR_RATE' : -80}",
   'READ_SCRN3'         : "{'ODD_ZONES' : 0, 'RST_RD_OFFSET' : 1, 'MAX_ERR_RATE' : -80}",
   'HEAD_SCRN2'         : "{'RST_RD_OFFSET' : 1, 'MAX_ERR_RATE' : -80, 'TSHR': 1, 'FAIL_SAFE': 0}",
   'WRT_SIM_FILES1'     : "{'saveFiles' : ['AFH']}",
   'WRITE_SCRN'         : "{'RUN_EAW_SCRN_TLEVEL10' : 1, 'input_dict': 'TP.prm_ATI_51_WRT_SCRN'}",
   'WRITE_SCRN_10K'     : "{'RUN_EAW_SCRN_TLEVEL10' : 1, 'input_dict': 'TP.prm_ATI_51_WRT_SCRN'}",
   'INTER_BAND_SCRN'    : "{'RUN_EAW_SCRN_TLEVEL10' : 1, 'input_dict': 'TP.prm_ATI_51_WRT_SCRN'}",
   'INTER_BAND_SCRN_500': "{'RUN_EAW_SCRN_TLEVEL10' : 1, 'input_dict': 'TP.prm_ATI_51_WRT_SCRN'}",
   'INTRA_BAND_SCRN'    : "{'RUN_EAW_SCRN_TLEVEL10' : 1, 'input_dict': 'TP.prm_ATI_51_WRT_SCRN'}",
   'OTC_BANDSCRN'       : {'ZONES': "[0, 4, 8, 75, 148]"},
   'WEAK_WR_OW3'        : {'OW_ZONE': [4], 'POSITION': [100], 'SMROW_ZONE': [1,8], 'SMR_POSITION': [100,50]},
   'SERIAL_FMT'         : "{'FORMAT_OPTIONS': 'TP.formatOptions'}",
}


###################################################################################################################
# State Transition Table
StateTable['SDAT2'] = {
   #--------------------------------------------------------------------------------------------------------------
   #  State        Module           Method                        Transitions                            Optional by
   #                                                                                                     HDSTR 'H'
   #                                                                                                     GOTF  'G'
   #---------------------------------------------------------------------------------------------------------------
   'INIT'               : [    'Serial_Init', 'CInitTesting',               {'pass':'DNLD_CODE',         'fail':'FAIL_PROC'}, []],
   'DNLD_CODE'          : ['Serial_Download', 'CDnldCode',                  {'pass':'INIT_DRVINFO',      'fail':'FAIL_PROC'}, []],
   'INIT_DRVINFO'       : [    'Serial_Init', 'CInit_DriveInfo',            {'pass':'BASE_2',            'fail':'FAIL_PROC'}, []],
   'BASE_2'             : [           'SDAT', 'CSdatBase2',                 {'pass':'UACT_2',            'fail':'FAIL_PROC'}, []],
   'UACT_2'             : [           'SDAT', 'CSdatUACT2',                 {'pass':'MDW_2',             'fail':'FAIL_PROC'}, []],
   'MDW_2'              : [           'SDAT', 'CSdatMDW2',                  {'pass':'CTRL_NOTCH_2',      'fail':'FAIL_PROC'}, []],
   'CTRL_NOTCH_2'       : [           'SDAT', 'CSdatControllerNotch2',      {'pass':'TMR_VERF_2',        'fail':'FAIL_PROC'}, []],
   'TMR_VERF_2'         : [           'SDAT', 'CSdatTmrVerf2',              {'pass':'BODES_2',           'fail':'FAIL_PROC'}, []],
   'BODES_2'            : [           'SDAT', 'CSdatBodes2',                {'pass':'TRK_FOLLOW_2',      'fail':'FAIL_PROC'}, []],
   'TRK_FOLLOW_2'       : [           'SDAT', 'CSdatTrkFlw2',               {'pass':'SERVO_LIN_2',       'fail':'FAIL_PROC'}, []],
   'SERVO_LIN_2'        : [           'SDAT', 'CSdatServoLin2',             {'pass':'ZEST_2',            'fail':'FAIL_PROC'}, []],
   'ZEST_2'             : [           'SDAT', 'CSdatZest2',                 {'pass':'DBLOG_2',           'fail':'FAIL_PROC'}, []],
   'DBLOG_2'            : [           'SDAT', 'CSdatDblog2',                {'pass':'END_TEST',          'fail':'FAIL_PROC'}, []],

   'END_TEST'           : [    'Serial_Exit', 'CEndTesting',                {'pass':'COMPLETE',          'fail':'FAIL_PROC'}, []],
   'FAIL_PROC'          : [    'Serial_Exit', 'CFailProc',                  {'pass':'COMPLETE',          'fail':'COMPLETE' }, []],
   'COMPLETE'           : [0,],
}

if testSwitch.FE_0159477_350037_SAMPLE_MONITOR == 1:
   StateTable['SDAT2'].update({
      'ZEST_2'             : [           'SDAT', 'CSdatZest2',                 {'pass':'WIRRO_SQ_2',        'fail':'FAIL_PROC'}, []],
      'WIRRO_SQ_2'         : [           'SDAT', 'CSdatWirroSq2',              {'pass':'XV_TRANSFER',       'fail':'FAIL_PROC'}, []],
      'XV_TRANSFER'        : [           'SDAT', 'XVTransferFunction',         {'pass':'VIBE_2',            'fail':'FAIL_PROC'}, []],
      'VIBE_2'             : [           'SDAT', 'CSdatVibe2',                 {'pass':'DBLOG_2',           'fail':'FAIL_PROC'}, []],
      'DBLOG_2'            : [           'SDAT', 'CSdatDblog2',                {'pass':'END_TEST',          'fail':'FAIL_PROC'}, []],

   })

# State Input Arguments Table
StateParams['SDAT2'] = {
   'DNLD_CODE'          : {'CODES': ['CFW', 'S_OVL'],},
   }

###################################################################################################################
# State Transition Table
StateTable['CRT2'] = {
   #-----------------------------------------------------------------------------------------------------------------------------------------------
   #  State                   Module               Method                        Transitions                                           Optional by
   #                                                                                                                                   GOTF  'G'
   #-----------------------------------------------------------------------------------------------------------------------------------------------
   'INIT'                  : ['Serial_Init',       'CInitTesting',               {'pass':'PBIC_DATA_LD',          'fail':'FAIL_PROC'}, []],
   'MASTER_HEAT_ON'        : ['Serial_Init',       'CTurnOnMasterHeat',          {'pass':'PBIC_DATA_LD',          'fail':'FAIL_PROC'}, []],      #for master heat recovery due to certain exception
   'PBIC_DATA_LD'          : ['base_SerialTest',   'CPBI_Data',                  {'pass':'CHK_PCBA_SN',           'fail':'FAIL_PROC'}, ['E', {'PBIC_SUPPORT' : 1}]],
   'CHK_PCBA_SN'           : ['PCBA_Base',         'CCheckPCBA_SN',              {'pass':'DNLD_CODE3',            'fail':'FAIL_PROC'}, [{'WA_REMOVE_PCBA_SN_CHK_FRM_STATE_TABLE_DURING_EM_PHASE': 0}]],
   'DNLD_CODE3'            : ['Serial_Download',   'CDnldCode',                  {'pass':'DTH_OFF',               'fail':'FAIL_PROC'}, []],
   'DTH_OFF'               : ['base_TccCal',       'CInitDTH',                   {'pass':'INIT_DRVINFO',          'fail':'FAIL_PROC'}, ['E', {'FE_OPEN_UP_DTH_VALUE': 1}]],
   'INIT_DRVINFO'          : ['Serial_Init',       'CInit_DriveInfo',            {'pass':'FAFH_DISPLAY3',         'fail':'FAIL_PROC'}, []],
   'FAFH_DISPLAY3'         : ['base_AFH',          'T74PrintOut',                {'pass':'VER_RAMP2',             'fail':'FAIL_PROC'}, ['E', {'DISPLAY_FAFH_PARAM_FILE_FOR_DEBUG':1}]],
   'VER_RAMP2'             : ['base_TccCal',       'CRampTempDiff',              {'pass':'HSC_TCC_LT',            'fail':'FAIL_PROC'}, ['E', {'HSC_BASED_TCS_CAL': 1}]],
   'HSC_TCC_LT'            : ['base_TccCal',       'CHSC_TCC',                   {'pass':'GETSKZN',               'fail':'FAIL_PROC'}, ['E', {'HSC_BASED_TCS_CAL': 1}]],
   'GETSKZN'               : ['OTF_Waterfall',     'CRetrieveSKIPZN',            {'pass':'READ_SCRN2A',           'fail':'FAIL_PROC'}, [{'SKIPZONE': 1}]],
   'READ_SCRN2A'           : ['base_CRTTest',      'CReadScreenSOVA',            {'pass':'VER_RAMP',              'fail':'FAIL_PROC'}, ['E', {'FE_0258915_348429_COMMON_TWO_TEMP_CERT': 0}]],
   'VER_RAMP'              : ['base_TccCal',       'CRampTempDiff',              {'pass':'TCC_RESET',             'fail':'FAIL_PROC'}, []],
   'TCC_RESET'             : ['base_TccCal',       'CTccReset',                  {'pass':'AFH4',                  'fail':'FAIL_PROC'}, ['E', {'ENABLE_TCC_RESET_BY_HEAD_BEFORE_AFH4': 1}]],
   'TCC_UPDATE'            : ['base_TccCal',       'CTccupdate',                 {'pass':'FAFH_CAL_TEMP_2',       'fail':'FAIL_PROC'}, ['E']],
   'AFH4'                  : ['base_TccCal',       'CTccCalibration',            {'pass':'FAFH_CAL_TEMP_2',       'fail':'FAIL_PROC'}, ['E']],
   'FAFH_CAL_TEMP_2'       : ['base_AFH',          'CFAFH_calibration',          {'pass':'DTH_OFF2',              'fail':'FAIL_PROC'}, ['E', {'IS_FAFH': 1}]],
   'DTH_OFF2'              : ['base_TccCal',       'CInitDTH',                   {'pass':'READ_SCRN2C',           'fail':'FAIL_PROC'}, ['E', {'FE_OPEN_UP_DTH_VALUE': 1}]],
   'READ_SCRN2C'           : ['base_CRTTest',      'CReadScreenSOVA',            {'pass':'TCC_BY_BER',            'fail':'FAIL_PROC'}, ['E']],
   'TCC_BY_BER'            : ['base_TccCal',       'CTcc_BY_BER',                {'pass':'DTH_ON2',           'fail':'FAIL_PROC'}, ['E']],
   'DTH_ON2'                : ['base_TccCal',       'CInitDTH',                   {'pass':'READ_SCRN2D',           'fail':'FAIL_PROC'}, ['E', {'FE_OPEN_UP_DTH_VALUE': 1, 'FE_AFH_RSQUARE_TCC' : 1}]],
   'READ_SCRN2D'           : ['base_CRTTest',      'CReadScreenSOVA',            {'pass':'TCC_VERIFY1',           'fail':'FAIL_PROC'}, ['E', {'RESET_TCC1_SLOPE_IF_BOTH_TCC1_AND_BER_OVER_SPEC': 1}]],
   'TCC_VERIFY1'           : ['base_TccCal',       'CTcc_Verify',                {'pass':'TCC_VERIFY2',           'fail':'FAIL_PROC'}, ['E', {'RESET_TCC1_SLOPE_IF_BOTH_TCC1_AND_BER_OVER_SPEC': 1}]],
   'TCC_VERIFY2'           : ['base_TccCal',       'CTcc_Verify',                {'pass':'SEGMENTED_BER2',        'fail':'FAIL_PROC'}, ['E', {'ENABLE_SMART_TCS_LIMITS_DATA_COLLECTION': 1}]],
   'SEGMENTED_BER2'        : ['base_CALTest',      'CSegmentedErrRate',          {'pass':'SQZ_WRITE2',            'fail':'FAIL_PROC'}, ['E', {'FE_SEGMENTED_BPIC': 1}]],
   # 'ENCROACH_SCRN2'        : ['base_RssScreens',   'CEncroachment_Screens',      {'pass':'SQZ_WRITE2',      'fail':'FAIL_PROC'}, ['E', {'FE_0111793_347508_PHARAOH_TTR': 0, 'FE_0258915_348429_COMMON_TWO_TEMP_CERT': 1}]],
   'SQZ_WRITE2'            : ['SerialTest',        'CSQZWrite',                  {'pass':'INTRA_BAND_SCRN2',      'fail':'FAIL_PROC'}, ['E', {'FE_0336349_305538_P_RUN_SQZWRITE2_IN_CRT2': 1, 'SMR': 1}]],
   'INTRA_BAND_SCRN2'      : ['base_RssScreens',   'CWrite_Screens',             {'pass':'INTER_BAND_SCRN2',      'fail':'FAIL_PROC'}, ['E', {'SMR': 1, 'FE_0253166_504159_MERGE_FAT_SLIM': 0, 'FE_0258915_348429_COMMON_TWO_TEMP_CERT': 1}]],
   'INTER_BAND_SCRN2'      : ['base_RssScreens',   'CWrite_Screens',             {'pass':'SMR_WRITE_SCRN2',       'fail':'FAIL_PROC'}, ['E', {'SMR': 1, 'FE_0253166_504159_MERGE_FAT_SLIM': 0, 'FE_0258915_348429_COMMON_TWO_TEMP_CERT': 1}]],
   'SMR_WRITE_SCRN2'       : ['base_RssScreens',   'CWrite_Screens',             {'pass':'WRITE_SCRN2',           'fail':'FAIL_PROC'}, ['E', {'SMR': 1, 'FE_0253166_504159_MERGE_FAT_SLIM': 1, 'FE_0258915_348429_COMMON_TWO_TEMP_CERT': 1}]],
   'WRITE_SCRN2'           : ['base_RssScreens',   'CWrite_Screens',             {'pass':'READ_SCRN2H',           'fail':'FAIL_PROC'}, ['E', {'FE_0258915_348429_COMMON_TWO_TEMP_CERT': 1}]],
   'READ_SCRN2H'           : ['base_CRTTest',      'CReadScreenSOVA',            {'pass':'HEAD_SCRN3',            'fail':'FAIL_PROC'}, ['E']],
   'HEAD_SCRN3'            : ['Head_Screen',       'CHeadScreen1',               {'pass':'HEAD_SCRN4',            'fail':'FAIL_PROC'}, ['E', {'ENABLE_HEAD_SCRN_IN_CRT2': 1, 'SMR': 1}]],
   'HEAD_SCRN4'            : ['Head_Screen',       'CHeadScreen2',               {'pass':'SETTLING',              'fail':'FAIL_PROC'}, ['E', {'ENABLE_HEAD_SCRN_IN_CRT2': 1, 'SMR': 1}]],
   'SETTLING'              : ['Head_Measure',      'CSettlingTestAllHd',         {'pass':'AGB_ZONE_REMAP',        'fail':'FAIL_PROC'}, ['E', {'ENABLE_CLR_SETTLING_STATE': 1, 'FE_0258915_348429_COMMON_TWO_TEMP_CERT': 0}]],
   # 'PRE_HEAT_OPTI'         : ['Head_Measure',      'CPreHeaterOpti',             {'pass':'HSC_OD_ID',             'fail':'FAIL_PROC'}, ['E']],
   # 'WEAK_WR_OW3'           : ['Head_Measure',      'CWeakWriteOWTest',           {'pass':'DNLD_CODE5',            'fail':'FAIL_PROC'}, ['E']],
   # 'OW_DATA7'              : ['Head_Measure',      'COWTest_FastIO',             {'pass':'DNLD_CODE5',            'fail':'FAIL_PROC'}, ['E']],
   'AGB_ZONE_REMAP'        : ['base_CRTTest',      'CAGB_zoneRemap',             {'pass':'TWO_T189',              'fail':'FAIL_PROC'}, ['E', {'ADAPTIVE_GUARD_BAND': 1}]],
   'TWO_T189'              : ['Servo_Tuning',      'CTwoT189Cal',                {'pass':'COMPARE_T189Multi',     'fail':'FAIL_PROC'}, ['E', {'FE_0309927_228373_TWO_TEMP_T189_IMPLEMENTATION': 1}]],
   'COMPARE_T189Multi'     : ['Servo_Tuning',      'CCompareT189Multi',          {'pass':'RESRRO_SCRN',           'fail':'FAIL_PROC'}, ['E', {'FE_0349167_228373_T189_MULTI_PRE2_CRT2_COMPARISON': 1}]],
   'RESRRO_SCRN'           : ['Servo_Tuning',      'CResonanceRROScrn',          {'pass':'BODE_SCRN',             'fail':'FAIL_PROC'}, ['E', {'FE_0362477_228373_T180_RESONANCE_RRO_SCRN_CRT2': 1}]],
   'BODE_SCRN'             : ['Servo_Tuning',      'CBodeScreen',                {'pass':'SHCKSNSR_SCRN',         'fail':'FAIL_PROC'}, ['E', {'FE_0341704_340866_BODE_SCREEN_IN_CRT2': 1}]],
   'SHCKSNSR_SCRN'         : ['Servo_Tuning',      'CShockSensorScrn',           {'pass':'POST_BSP_SCAN',         'fail':'FAIL_PROC'}, ['E', {'FE_0325684_340866_SHOCK_SENSOR_SCREEN': 1}]],
   'POST_BSP_SCAN'         : ['base_SerialTest',   'CPostBSPScan',               {'pass':'FAFH_DISPLAY2',         'fail':'FAIL_PROC'}, ['E', {'POST_SERVO_FLAW_SCAN_IN_CRT2': 1}]],
   'FAFH_DISPLAY2'         : ['base_AFH',          'T74PrintOut',                {'pass':'DNLD_CODE5',            'fail':'FAIL_PROC'}, ['E', {'DISPLAY_FAFH_PARAM_FILE_FOR_DEBUG': 1}]],
   'DNLD_CODE5'            : ['Serial_Download',   'CDnldCode',                  {'pass':'MC_VERIFY',             'fail':'FAIL_PROC'}, []],
   'MC_VERIFY'             : ['base_CRTTest',      'CMediaCacheVerify',          {'pass':'DTH_ON',                'fail':'FAIL_PROC'}, []],
   'DTH_ON'                : ['base_TccCal',       'CInitDTH',                   {'pass':'SET_CUST_OCLIM',        'fail':'FAIL_PROC'}, ['E', {'FE_OPEN_UP_DTH_VALUE': 1}]],
   'SET_CUST_OCLIM'        : ['base_FNCTest',      'CSetCustomerOCLIM',          {'pass':'MCT_VERIFY',            'fail':'FAIL_PROC'}, [{'FE_0243459_348085_DUAL_OCLIM_CUSTOMER_CERT': 1}]],
   'MCT_VERIFY'            : ['base_GPLists',      'CVerifyDrive',               {'pass':'DNLD_F3CODE2',          'fail':'FAIL_PROC'}, []],
   'DNLD_F3CODE2'          : ['Serial_Download',   'CDnldCode',                  {'pass':'INIT_ASD',              'fail':'FAIL_PROC'}, [{'FE_0000000_305538_HYBRID_DRIVE': 1}]], # only download SDP for hybrid
   'INIT_ASD'              : ['base_CRTTest',      'CInitASDforHybrid',          {'pass':'DNLD_BRG_IV',           'fail':'FAIL_PROC'}, [{'FE_0000000_305538_HYBRID_DRIVE': 1}]], # for hybrid only
   'DNLD_BRG_IV'           : ['Serial_Download',   'CDnldCode',                  {'pass':'DNLD_F3CODE',           'fail':'FAIL_PROC'}, ['G']],
   'DNLD_F3CODE'           : ['Serial_Download',   'CDnldCode',                  {'pass':'DNLD_F3CODE_QNR',       'fail':'FAIL_PROC'}, []],
   'DNLD_F3CODE_QNR'       : ['Serial_Download',   'CDnldCode',                  {'pass':'HDA_FW_VERIFY',         'fail':'FAIL_PROC'}, [{'FE_0334158_379676_P_RFWD_FFV_1_POINT_5': 1}]],
   'REDNLD_BRG_IV'         : ['Serial_Download',   'CDnldCode',                  {'pass':'REDNLD_F3CODE',         'fail':'FAIL_PROC'}, ['G']],
   'REDNLD_F3CODE'         : ['Serial_Download',   'CDnldCode',                  {'pass':'HDA_FW_VERIFY',         'fail':'FAIL_PROC'}, []],

   'HDA_FW_VERIFY'         : ['base_CRTTest',      'CCheckHDA_FW',               {'pass':'WEAK_WR_DELTABER',      'fail':'FAIL_PROC'}, [{'FE_0318342_402984_CHECK_HDA_FW': 1}]],
   'WEAK_WR_DELTABER'      : ['Head_Measure_F3',   'CSymBer_WeakWrite',          {'pass':'SERIAL_FMT',            'fail':'FAIL_PROC'}, ['E', {'RUN_WEAK_WR_DELTABER': 1}]],

   # ------------------------------- This is for older process where Serial Format is in FNC2 -------------------------------
   'TRACK_CLEANUP'         : ['base_TccCal',       'CTrackCleanup',              {'pass':'INIT_CONGEN',           'fail':'SERIAL_FMT'},[]],
   # ------------------------------- This is for older process where Serial Format is in FNC2 -------------------------------

   'SERIAL_FMT'            : ['Serial_SerFmt',     'CSerialFormat',              {'pass':'MQM_TEST',              'fail':'FAIL_PROC'}, []],
   'MQM_TEST'              : ['base_qualityMQM',   'CSFMT_MQMBEATUP',            {'pass':'F3_BER',                'fail':'FAIL_PROC'}, [{'FE_ENABLE_SFT_BEATUP': 1}]],
   'F3_BER'                : ['base_CRTTest',      'CSerialBER',                 {'pass':'INIT_CONGEN',           'fail':'FAIL_PROC'}, [{'RUN_F3_BER': 1}]],

   'INIT_CONGEN'           : ['base_CRTTest',      'CInitCONGEN',                {'pass':'INIT_SMART',            'fail':'FAIL_PROC'}, [{'INIT_CONGEN_SKIP': 0}]],
   # 'SP_WR_TRUPUT'          : ['base_RssScreens',   'CSerial_Truput',             {'pass':'SP_RD_TRUPUT',          'fail':'FAIL_PROC'}, []],
   # 'SP_RD_TRUPUT'          : ['base_RssScreens',   'CSerial_Truput',             {'pass':'INIT_SMART',            'fail':'FAIL_PROC'}, []],
   # 'ENCRO_TEST2'           : ['SerialTest',        'COfstEncroTst',              {'pass':'INIT_SMART',            'fail':'FAIL_PROC'}, []],
   'INIT_SMART'            : ['base_SerSMART',       'CClearSMART',                {'pass':'END_TEST',            'fail':'FAIL_PROC'}, []],
   # 'PBIC_DATA_SV'          : ['base_SerialTest',   'CPBI_Data',                  {'pass':'END_TEST',              'fail':'FAIL_PROC'}, [{'PBIC_SUPPORT' : 1}]],
   'END_TEST'              : ['Serial_Exit',       'CEndTesting',                {'pass':'COMPLETE',              'fail':'FAIL_PROC'}, []],
   'FAIL_PROC'             : ['Serial_Exit',       'CFailProc',                  {'pass':'COMPLETE',              'fail':'COMPLETE'},  []],
   'COMPLETE'              : [0,],
}

if testSwitch.NCTC_CLOSED_LOOP:
   StateTable['CRT2']['VER_RAMP'][2]['pass'] = 'TCC_UPDATE'

if testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT and testSwitch.FE_0221005_504374_P_3TIER_MULTI_OPER:
   ###########################################################################################################
   #                                                                                                         #
   #                     !!!!!!!!!!!! CRT2 with TIER support!!!!!!!!!!!!!!                                   #
   #                                                                                                         #
   ###########################################################################################################
   StateTable['CRT2'].update({

      # Begin IO section
      'MCT_VERIFY'         : ['base_GPLists',    'CVerifyDrive',             {'pass':'DNLD_CODE_TCG',    'fail':'FAIL_PROC'},  []],
      'DNLD_CODE_TCG'      : ['Serial_Download', 'CDnldCode',                {'pass':'DNLD_U_CODE',      'fail':'FAIL_PROC'},  ['P']],        #  Bridge code + F3 code for TCG drives PN
      'DNLD_U_CODE'        : ['Serial_Download', 'CDnldCode',                {'pass':'WEAK_WR_DELTABER', 'fail':'FAIL_PROC'},  ['P']],        #  Normal F3 code for non-TCG drives
      'WEAK_WR_DELTABER'   : ['Head_Measure_F3', 'CSymBer_WeakWrite',        {'pass':'TRACK_CLEANUP',    'fail':'FAIL_PROC'},  []],
      'TRACK_CLEANUP'      : ['base_TccCal',     'CTrackCleanup',            {'pass':'INIT_CONGEN',      'fail':'SERIAL_FMT'}, []],
      'SERIAL_FMT'         : ['Serial_SerFmt',   'CSerialFormat',            {'pass':'INIT_CONGEN',      'fail':'FAIL_PROC'},  []],
      'INIT_CONGEN'        : ['base_CRTTest',    'CInitCONGEN',              {'pass':'RESET_SMART',      'fail':'FAIL_PROC'},  []],
      'RESET_SMART'        : ['base_IntfTest',   'CClearSMART',              {'pass':'CUST_CFG',         'fail':'FAIL_PROC'},  []],

      # Do tier CUST_CFG for potential tier downgrade
      'CUST_CFG'         : [  'base_IntfTest', 'CCustomConfig',              {'pass':'COMPLETE',         'fail':'TIER1_FAIL'}, [TIERX]],
      'TIER1_FAIL'       : [      'CommitCls', 'CAutoCommitTier_Fail',       {'pass':'FAIL_PROC',        'fail':'END_TEST'},   [TIER1]],

      'END_TEST'         : ['Serial_Exit',     'CEndTesting',                {'pass':'COMPLETE',         'fail':'FAIL_PROC'}, []],
      'FAIL_PROC'        : ['Serial_Exit',     'CFailProc',                  {'pass':'COMPLETE',         'fail':'COMPLETE' }, []],
      'COMPLETE'         : [0,],   })

# State Input Arguments Table
StateParams['CRT2'] = {
   'VER_RAMP'           : "{'OPTEMP': 'CRT2',}",
   'VER_RAMP2'          : "{'OPTEMP': 'CRT2',}",
   'DNLD_CODE3'         : "{'CODES': ['CFW'], 'SKIP_CODE': 1, 'CLR_CERTDONE_BIT': 1}",
   'DNLD_CODE5'         : "{'CODES': ['CFW','SFW2'],'SKIP_CODE': 1,'CMP_CODE': 1}", #download after downgrade
   'DNLD_F3CODE2'       : "{'CODES': ['TGT2','OVL2'],}",
   'DNLD_F3CODE3'       : "{'CODES': ['TGT3','OVL3'],}",
   'DNLD_BRG_IV'        : "{'CODES': ['TGTB','OVLB','IV'],}",
   'DNLD_F3CODE'        : "{'CODES': ['TGT','OVL','CXM'],}",
   'DNLD_F3CODE_QNR'    : "{'CODES': ['TGT','OVL'],}",
   'REDNLD_BRG_IV'      : "{'CODES': ['TGTB','OVLB','IV'],}",
   'REDNLD_F3CODE'      : "{'CODES': ['TGT','OVL','CXM'],}",

   # For 3-tier code download state handling
   'DNLD_CODE_TCG'      : "{'CODES': ['TGTB','OVLB','IV','TGT','OVL'],}",
   'DNLD_U_CODE'        : "{'CODES': ['TGT','OVL'],}",

   'INIT_DRVINFO'       : "{'FORCE' : 1}",
   'AFH4'               : "{'exec231': 1,}",
   'FAFH_CAL_TEMP_2'    : "{'tempIndexStr' : 'FAFH_COLD_MEASUREMENT'}",
   'CCT_TEST'           : "{'WRITE': 'TP.prm_510_W1K', 'READ': 'TP.prm_510_R1K',}",    # knl 30Nov07
   'SP_WR_TRUPUT'       : "{'XFER_TYPE': 'TP.prm_sp_wr_truput',}",
   'SP_RD_TRUPUT'       : "{'XFER_TYPE': 'TP.prm_sp_rd_truput',}",
   'WEAK_WR_DELTABER'   : "{'param': {'ColdDownDelay': 50*60*1, 'DeltaBER_Limit': 0.15, 'Minimum_SymBer': 2.40, 'Minimum_ColdSymBer': 2.15, 'AvgPoints': 25, 'LoopCount': 600, 'FailSafe':1},}",
   'ENCRO_TEST2'        : "{'param': {'noOfWrite':2, 'verifyCnt':1, 'OffstPercent':8, 'RdRty':0x05, 'WrRty':0x8, 'ECCRty':0, 'numOfZones':20},}",
   'SERIAL_FMT'         : "{'FORMAT_OPTIONS': 'TP.formatOptions'}",
   'TRACK_CLEANUP'      : "{'RETRY_COUNT' : 3, 'WR_RETRIES' : 200}",
   'F3_BER'             : "{'READ_ONLY': 0, 'WHOLE_SURFACE': 0}",
   'HEAD_SCRN3'         : "{'RST_RD_OFFSET' : 1, 'MAX_ERR_RATE' : -80, 'TCC' : 1, 'ZAP_OFF_AT_END' : 0, 'TSHR': 0, 'FAIL_SAFE': 0, 'NO_ADJUST': 1}",
   'HEAD_SCRN4'         : "{'RST_RD_OFFSET' : 1, 'MAX_ERR_RATE' : -80, 'TCC' : 1, 'ZAP_OFF_AT_END' : 0, 'TSHR': 0, 'FAIL_SAFE': 0}",
   'READ_SCRN2H'        : "{'ODD_ZONES' : 0, 'RST_RD_OFFSET' : 1, 'MAX_ERR_RATE' : -80}",
   'READ_SCRN2D'        : "{'ODD_ZONES' : 0, 'RST_RD_OFFSET' : 1, 'MAX_ERR_RATE' : -80}",
   'READ_SCRN2C'        : "{'ODD_ZONES' : 0, 'RST_RD_OFFSET' : 1, 'MAX_ERR_RATE' : -80}",
   'READ_SCRN2A'        : "{'ODD_ZONES' : 0, 'RST_RD_OFFSET' : 1, 'MAX_ERR_RATE' : -80}",
   'SQZ_WRITE2'         : "{'TCC': 1, 'FAIL_SAFE': 1}",
   'WRITE_SCRN2'        : "{'RUN_EAW_SCRN_TLEVEL10' : 1, 'input_dict': 'TP.prm_ATI_51_WRT_SCRN'}",
   'INTER_BAND_SCRN2'   : "{'RUN_EAW_SCRN_TLEVEL10' : 1, 'input_dict': 'TP.prm_ATI_51_WRT_SCRN'}",
   'INTRA_BAND_SCRN2'   : "{'RUN_EAW_SCRN_TLEVEL10' : 1, 'input_dict': 'TP.prm_ATI_51_WRT_SCRN'}",
   'SMR_WRITE_SCRN2'    : "{'RUN_EAW_SCRN_TLEVEL10' : 1, 'input_dict': 'TP.prm_ATI_51_WRT_MERGE_SCRN'}",
   'DTH_OFF'            : "{'MODE': 'off'}",
   'DTH_OFF2'           : "{'MODE': 'off'}",
   'DTH_ON'             : "{'MODE': 'on'}",
   'DTH_ON2'             : "{'MODE': 'on'}",
   'SEGMENTED_BER2'     : "{'ZONES': 'TP.UMP_ZONE'}",
   'SEG_BER_SQZ2'       : "{'ZONES': 'TP.BPIMeasureZone'}",
}

if testSwitch.FE_0251909_480505_NEW_TEMP_PROFILE_FOR_ROOM_TEMP_PRE2:
  StateParams['CRT2'].update({
   'DNLD_F3_5IN1'       : "{'CODES': ['ALL3'],}",
  })

if testSwitch.SINGLEPASSFLAWSCAN:
  StateParams['CRT2'].update({
     'SERIAL_FMT'   : "{'FORMAT_OPTIONS': 'TP.packWriteFormat'}",
  })

if testSwitch.TRUNK_BRINGUP:
  StateParams['CRT2'].update({
   'DNLD_F3_5IN1'       : "{'CODES': ['TGT3','OVL3'],}",
  })

if testSwitch.LAUNCHPAD_RELEASE:
  StateParams['CRT2'].update({
   'DNLD_BRG_IV'        : "{'CODES': ['TGT3','OVL3','IV3'],}",
   'DNLD_F3CODE'        : "{'CODES': ['TGT','OVL'],}",
   'REDNLD_BRG_IV'      : "{'CODES': ['TGT3','OVL3','IV3'],}",
   'REDNLD_F3CODE'      : "{'CODES': ['TGT','OVL'],}",
   # For 3-tier code download state handling
   'DNLD_CODE_TCG'      : "{'CODES': ['TGT3','OVL3','IV3','TGT','OVL'],}",
  })
###################################################################################################################
StateTable['MQM2'] = {
      #--------------------------------------------------------------------------------------------------------------------------------
      #  State                   Module             Method                          Transitions                            Optional by
      #
      #                                                                                                                     GOTF 'G'
      #--------------------------------------------------------------------------------------------------------------------------------
      'INIT'                 : ['Serial_Init',     'CInitTesting',              {'pass':'SPMQM',             'fail':'FAIL_PROC'}, []],

      'SPMQM'                : ['GIO',             'CGIO',                      {'pass':'END_TEST',            'fail':'FAIL_PROC'}, []],

      'END_TEST'             : ['Serial_Exit',     'CEndTesting',               {'pass':'COMPLETE',            'fail':'FAIL_PROC'}, []],
      'FAIL_PROC'            : ['Serial_Exit',     'CFailProc',                 {'pass':'COMPLETE',            'fail':'COMPLETE'},  []],
      'COMPLETE'             : [0,],
   }
StateParams['MQM2'] = {
#For now, no param input
}

#####################################################################################################################
# State Transition Table
# StateTable['CUT2'] = {
#    #--------------------------------------------------------------------------------------------------------------
#    #  State        Module           Method                        Transitions                            Optional by
#    #                                                                                                     HDSTR 'H'
#    #                                                                                                     GOTF  'G'
#    #---------------------------------------------------------------------------------------------------------------
#    'INIT'         : ['base_IntfTest',   'CInitTesting',        {'pass':'DISABLE_UDR2',    'fail':'FAIL_PROC'},      []],
# 
#    'DISABLE_UDR2' : ['base_IntfTest',   'CDisableUDR2',        {'pass':'INTFTTR',         'fail':'FAIL_PROC'},      []],
#    'INTFTTR'      : ['CustomerScreens', 'CIntfTTR',            {'pass':'WRITE_XFER',      'fail':'FAIL_PROC'},      []],
#    'WRITE_XFER'   : ['base_IntfTest',   'CZoneXferTest',       {'pass':'READ_XFER',       'fail':'FAIL_PROC'},      []],
#    'READ_XFER'    : ['base_IntfTest',   'CZoneXferTest',       {'pass':'IOMQM',           'fail':'FAIL_PROC'},      []],
#    'IOMQM'        : ['base_IntfTest',   'CGIO',                {'pass':'DO_COMMIT',       'fail':'FAIL_PROC'},      []],
#    'DO_COMMIT'    : ['CommitCls',       'CAutoCommit',         {'pass':'VOLTAGE_HL',      'fail':'FAIL_PROC'},      []],
#    'VOLTAGE_HL'   : ['base_IntfTest',   'CVoltageHLTest',      {'pass':'COMMAND_SET',     'fail':'FAIL_PROC'},      []],
#    'COMMAND_SET'  : ['base_IntfTest',   'CCommandSet',         {'pass':'POWER_MODE',      'fail':'FAIL_PROC'},      []],
#    'POWER_MODE'   : ['base_IntfTest',   'CPowerMode',          {'pass':'SMART_DST',       'fail':'FAIL_PROC'},      []],
#    'SMART_DST'    : ['base_IntfTest',   'CSmartDSTShort',      {'pass':'CUST_CFG',        'fail':'FAIL_PROC'},      []],
#    'CUST_CFG'     : ['base_IntfTest',   'CCustomConfig',       {'pass':'ATTR_VAL',        'fail':'FAIL_PROC'},      []],
#    'ATTR_VAL'     : ['base_IntfTest',   'CSetDriveConfigAttributes', {'pass':'ENABLE_FAFH', 'fail':'FAIL_PROC'},    []],
#    'ENABLE_FAFH'  : ['base_IntfTest',   'CEnaFAFH',            {'pass':'S_PARITY_CHK',    'fail':'FAIL_PROC'},      [{'ENABLE_FAFH_FIN2':1}]],
#    'S_PARITY_CHK' : ['base_IntfTest',   'CSParityCheck',       {'pass':'WR_VERIFY',       'fail':'FAIL_PROC'},      []],
#    'WR_VERIFY'    : ['base_IntfTest',   'CWRVerify',           {'pass':'ENABLE_MC',         'fail':'FAIL_PROC'},    [{'ROSEWOOD7 : 0'}]],
#    'ENABLE_MC'    : ['base_IntfTest',   'CEnableMC',           {'pass':'SMART_DFT_LIST',  'fail':'FAIL_PROC'},      [{'ENABLE_MEDIA_CACHE':1}]],
#    'SMART_DFT_LIST': ['base_IntfTest',  'CSmartDefectList',    {'pass':'CRITICAL_LOG',    'fail':'FAIL_PROC'},      []],
#    'CRITICAL_LOG' : ['base_IntfTest',   'CCriticalEvents',     {'pass':'VERIFY_SMART',    'fail':'FAIL_PROC'},      []],
#    'VERIFY_SMART' : ['base_IntfTest',   'CVerifySMART',        {'pass':'RESET_SMART',     'fail':'FAIL_PROC'},      []],
#    'RESET_SMART'  : ['base_IntfTest',   'CClearSMART',         {'pass':'CHK_SMART_ATTR',  'fail':'FAIL_PROC'},      []],
#    'CHK_SMART_ATTR': ['base_IntfTest',  'CChkSmartAttr',       {'pass':'RESET_DOS',       'fail':'FAIL_PROC'},      []],
#    'RESET_DOS'    : ['base_IntfTest',   'CClearDOS',           {'pass':'NVCACHE_INIT',    'fail':'FAIL_PROC'},      []],
#    'NVCACHE_INIT' : ['NVCache',         'InitNVCacheWithDiags',{'pass':'FINAL_PREP',      'fail':'FAIL_PROC'},      [{'FE_0000000_305538_HYBRID_DRIVE':1}]],
#    'FINAL_PREP'   : ['CustomerContent', 'CFinalPrep',          {'pass':'RESET_UDS',       'fail':'FAIL_PROC'},      [{'FE_0385431_MOVE_FINAL_LIFE_STATE_TO_END':1}]],
#    'RESET_UDS'    : ['base_IntfTest',   'CClearUds',           {'pass':'ENABLE_UDR2',     'fail':'FAIL_PROC'},      [{'FE_0252611_433430_CLEAR_UDS' : 1}]],
#    'ENABLE_UDR2'  : ['base_IntfTest',   'CEnableUDR2',         {'pass':'CLEAR_EWLM',      'fail':'FAIL_PROC'},      []],
#    'CLEAR_EWLM'   : ['base_IntfTest',   'CClearEWLM',          {'pass':'CCVMAIN',            'fail':'FAIL_PROC'},      []],
#    'CCVMAIN'      : ['base_CCV',        'CCCV_main',           {'pass':'SDOD',            'fail':'FAIL_PROC'},      []],
#    'SDOD'         : ['base_IntfTest',    'CSDOD',              {'pass':'END_TEST',        'fail':'FAIL_PROC'},      []],
# 
#    'END_TEST'     : ['base_IntfTest',   'CEndTesting',         {'pass':'COMPLETE',        'fail':'FAIL_PROC'},      []],
#    'FAIL_PROC'    : ['base_IntfTest',   'CFailProc',           {'pass':'COMPLETE',        'fail':'COMPLETE'},       []],
#    'COMPLETE'     : [0,],
# }
# 
# # State Input Arguments Table
# StateParams['CUT2'] = {
#    'CRITICAL_LOG' : "{'PARAM_NAME': 'TP.prm_CriticalEvents',}",
#    'WRITE_XFER'   : "{'XFER_TYPE': 'TP.prm_598_w', 'XFER_MODE': 'WRITE'}",
#    'READ_XFER'    : "{'XFER_TYPE': 'TP.prm_598_r',}",
#    'CCT_TEST'     : "{'CCT_TEST': 'TP.prm_510_CCT'}",
#    'SP_WR_TRUPUT'     : "{'XFER_TYPE': 'TP.prm_sp_wr_truput',}",
#    'SP_RD_TRUPUT'     : "{'XFER_TYPE': 'TP.prm_sp_rd_truput',}",
# }

#####################################################################################################################
# State Transition Table
if testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT and testSwitch.FE_0221005_504374_P_3TIER_MULTI_OPER:
   ###########################################################################################################
   #                                                                                                         #
   #                            !!!!!!!!!!!! CMT2 for TIER support!!!!!!!!!!!!!!                             #
   #                                                                                                         #
   ###########################################################################################################
   # State Transition Table
   StateTable['CMT2'] = {
      #------------------------------------------------------------------------------------------------------------------
      #  State            Module             Method                    Transitions                               Optional by
      #                                                                                                          HDSTR 'H'
      #                                                                                                          GOTF 'G'
      #------------------------------------------------------------------------------------------------------------------
      'INIT'             : [  'base_IntfTest', 'CInitTesting',               {'pass':'COMMIT',          'fail':'FAIL_PROC'}, []],

      # If we are a tier at this point we commit and re-download codes; states_PN- testing after this point is all 9digit CC and no tier
      'COMMIT'           : [      'CommitCls', 'CAutoCommit',                {'pass':'COMPLETE',        'fail':'FAIL_PROC'}, ['P']],

      'END_TEST'         : [  'base_IntfTest', 'CEndTesting',                {'pass':'COMPLETE',        'fail':'FAIL_PROC'}, []],
      'FAIL_PROC'        : [  'base_IntfTest', 'CFailProc',                  {'pass':'COMPLETE',        'fail':'COMPLETE' }, []],
      'COMPLETE'         : [0,],
      }

   # State Input Arguments Table
   StateParams['CMT2'] = {
      #'INIT'             : {'SHORT_INIT': 1},
      'COMMIT'           : {'SEND_OPER': 0,},
      }

#######################################################################################################################
# State Transition Table

try:
   TraceMessage("StateTable.py NoIO detection start")
   if testSwitch.virtualRun:
      raise ValueError('In virtual run mode')
   from PIF import NO_IO_CFG
except:
   import traceback
   TraceMessage("StateTable.py NoIO detection exception=%s" % traceback.format_exc())
   NO_IO_CFG = {}

if (
     (DriveAttributes.get('PART_NUM','NONE')[-3:] in NO_IO_CFG.get('NO_IO_TAB',[]) or \
      "*" in NO_IO_CFG.get('NO_IO_TAB',[])) and \
      (DriveAttributes.get('IOFIN2_PENDING', 'NONE') != "1" and DriveAttributes.get('IOFIN2_PENDING', 'NONE') != "2") or \
      testSwitch.virtualRun
    ):
   TraceMessage("Attr RIM_TYPE=%s PIF NO_IO_RIMTYPE=%s" % (DriveAttributes.get('RIM_TYPE', 'NONE'), NO_IO_CFG.get('NO_IO_RIMTYPE', [])))

   if DriveAttributes.get('RIM_TYPE', 'NONE') in NO_IO_CFG.get('NO_IO_RIMTYPE', []) or testSwitch.FORCE_SERIAL_ICMD:
      testSwitch.NoIO = 1
      testSwitch.SDBP_TN_GET_UDR2 = 0
      testSwitch.CPCWriteReadRemoval = 0
      testSwitch.IOWriteReadRemoval = not testSwitch.CPCWriteReadRemoval
      testSwitch.SI_SERIAL_ONLY = 1    # force SI to use serial class only


#CHOOI-27May17 OffSpec
TraceMessage("==============================================================================================")
TraceMessage("==============================================================================================")
TraceMessage("testSwitch.NoIO=%s" % (testSwitch.NoIO))
TraceMessage("testSwitch.SDBP_TN_GET_UDR2=%s" % (testSwitch.SDBP_TN_GET_UDR2))
TraceMessage("testSwitch.CPCWriteReadRemoval=%s" % (testSwitch.CPCWriteReadRemoval))
TraceMessage("testSwitch.IOWriteReadRemoval=%s" % (testSwitch.IOWriteReadRemoval))
TraceMessage("testSwitch.SI_SERIAL_ONLY=%s" % (testSwitch.SI_SERIAL_ONLY))
TraceMessage("testSwitch.FORCE_SERIAL_ICMD=%s" %testSwitch.FORCE_SERIAL_ICMD)
TraceMessage("testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT=%s" % (testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT))
TraceMessage("testSwitch.FE_0221005_504374_P_3TIER_MULTI_OPER=%s" % (testSwitch.FE_0221005_504374_P_3TIER_MULTI_OPER))

TraceMessage("Statetable testSwitch.NoIO = %s" %testSwitch.NoIO)
TraceMessage("==============================================================================================")
TraceMessage("==============================================================================================")

#CHOOI-03Jun17 OffSpec
#if DriveAttributes.get('RIM_TYPE', 'NONE') == '57' and DriveAttributes.get('VALID_OPER', 'NONE') == 'CUT2':
if DriveAttributes.get('RIM_TYPE', 'NONE') == '57':
   testSwitch.NoIO = 0
   testSwitch.SDBP_TN_GET_UDR2 = 1
   testSwitch.CPCWriteReadRemoval = 1
   testSwitch.IOWriteReadRemoval = not testSwitch.CPCWriteReadRemoval
   testSwitch.SI_SERIAL_ONLY = 0    # force SI to use serial class only
   testSwitch.FORCE_SERIAL_ICMD = 0      # if 1, then force serial commands, even in IO cells

#CHOOI-27May17 OffSpec
TraceMessage("==============================================================================================")
TraceMessage("==============================================================================================")
TraceMessage("testSwitch.NoIO=%s" % (testSwitch.NoIO))
TraceMessage("testSwitch.SDBP_TN_GET_UDR2=%s" % (testSwitch.SDBP_TN_GET_UDR2))
TraceMessage("testSwitch.CPCWriteReadRemoval=%s" % (testSwitch.CPCWriteReadRemoval))
TraceMessage("testSwitch.IOWriteReadRemoval=%s" % (testSwitch.IOWriteReadRemoval))
TraceMessage("testSwitch.SI_SERIAL_ONLY=%s" % (testSwitch.SI_SERIAL_ONLY))
TraceMessage("testSwitch.FORCE_SERIAL_ICMD=%s" %testSwitch.FORCE_SERIAL_ICMD)
TraceMessage("testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT=%s" % (testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT))
TraceMessage("testSwitch.FE_0221005_504374_P_3TIER_MULTI_OPER=%s" % (testSwitch.FE_0221005_504374_P_3TIER_MULTI_OPER))

TraceMessage("Statetable testSwitch.NoIO = %s" %testSwitch.NoIO)
TraceMessage("==============================================================================================")
TraceMessage("==============================================================================================")

if testSwitch.NoIO == 0:
   testSwitch.FORCE_SERIAL_ICMD = 0      # if 1, then force serial commands, even in IO cells

#CHOOI-01June17 OffSpec
   TraceMessage("testSwitch.FORCE_SERIAL_ICMD=%s" %testSwitch.FORCE_SERIAL_ICMD)
   TraceMessage("==============================================================================================")
   TraceMessage("==============================================================================================")

   if testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT and testSwitch.FE_0221005_504374_P_3TIER_MULTI_OPER:
      StateTable['FIN2'] = {
         #-------------------------------------------------------------------------------------------------------------------
         #  State            Module         Method                          Transitions                      Optional by
         #
         #                                                                                                     GOTF 'G'
         #-------------------------------------------------------------------------------------------------------------------
         'INIT'         : ['base_IntfTest',   'CInitTesting',        {'pass':'DNLD_CODE_TCG2',   'fail':'FAIL_PROC'},    []],
         #'PBIC_DATA_LD' : ['base_SerialTest', 'CPBI_Data',           {'pass':'DISABLE_UDR2',    'fail':'FAIL_PROC'},      [{'PBIC_SUPPORT' : 1}]],

         # Download the specific 9 digit code
         'DNLD_CODE_TCG2' : ['base_IntfTest',   'CDnlduCode',        {'pass':'DNLD_U_CODE2',    'fail':'FAIL_PROC'},    ['R','P']],
         'DNLD_U_CODE2'    : ['base_IntfTest',   'CDnlduCode',        {'pass':'RESET_SMART2',      'fail':'FAIL_PROC'},  ['R','P']],
         'RESET_SMART2'    : ['base_IntfTest',   'CClearSMART',       {'pass':'DISABLE_UDR2_2',    'fail':'FAIL_PROC'},  ['R']],
         'DISABLE_UDR2_2' : ['base_IntfTest',   'CDisableUDR2',      {'pass':'INTFTTR',         'fail':'FAIL_PROC'},      []],

         # Common I/O performance tests
         'INTFTTR'      : ['CustomerScreens', 'CIntfTTR',            {'pass':'WRITE_XFER',      'fail':'FAIL_PROC'},      []],
         'WRITE_XFER'   : ['base_IntfTest',   'CZoneXferTest',       {'pass':'READ_XFER',       'fail':'FAIL_PROC'},      []],
         'READ_XFER'    : ['base_IntfTest',   'CZoneXferTest',       {'pass':'IOMQM',           'fail':'FAIL_PROC'},      []],
         #'400K_ZERO'    : ['base_IntfTest',   'C400KZeros',          {'pass':'400K_ZERO_CHK',   'fail':'FAIL_PROC'},      []],
         #'400K_ZERO_CHK': ['base_IntfTest',   'C400KZeroCheck',      {'pass':'IOMQM',           'fail':'FAIL_PROC'},      []],
         'IOMQM'        : ['base_IntfTest',   'CGIO',                {'pass':'VOLTAGE_HL',      'fail':'FAIL_PROC'},      []],
         'VOLTAGE_HL'   : ['base_IntfTest',   'CVoltageHLTest',      {'pass':'COMMAND_SET',     'fail':'FAIL_PROC'},      []],
         'COMMAND_SET'  : ['base_IntfTest',   'CCommandSet',         {'pass':'POWER_MODE',      'fail':'FAIL_PROC'},      []],
         'POWER_MODE'   : ['base_IntfTest',   'CPowerMode',          {'pass':'SMART_DST',       'fail':'FAIL_PROC'},      []],
         'SMART_DST'    : ['base_IntfTest',   'CSmartDSTShort',      {'pass':'CUST_CFG2',      'fail':'FAIL_PROC'},      []],

         # All non-tiers run this state
         'CUST_CFG2'    : ['base_IntfTest',   'CCustomConfig',       {'pass':'ATTR_VAL2',        'fail':'FAIL_PROC'},     []],
         'ATTR_VAL2'    : ['base_IntfTest',   'CSetDriveConfigAttributes', {'pass':'DISPLAY_ACFF', 'fail':'FAIL_PROC'},   []],
         'ENABLE_FAFH'  : ['base_IntfTest',   'CEnaFAFH',            {'pass':'DISPLAY_ACFF',    'fail':'FAIL_PROC'},      [{'ENABLE_FAFH_FIN2':1}]],
         'DISPLAY_ACFF' : ['base_IntfTest',   'CACFFDisplay',        {'pass':'SUPIV_CHK',       'fail':'FAIL_PROC'},      []],
         'SUPIV_CHK'    : ['base_IntfTest',   'CSPInvRatioChk',      {'pass':'AMPS_CHECK',      'fail':'FAIL_PROC'},      []],
         'AMPS_CHECK'   : ['base_IntfTest',   'CAMPSCheck',          {'pass':'DEFECT_LIST',     'fail':'FAIL_PROC'},      []],
         'DEFECT_LIST'  : ['base_IntfTest',   'CCheck_DefList',      {'pass':'SMART_DFT_LIST',  'fail':'FAIL_PROC'},      []],
         'SMART_DFT_LIST': ['base_IntfTest',  'CSmartDefectList',    {'pass':'CRITICAL_LOG',         'fail':'FAIL_PROC'}, []],
         'CRITICAL_LOG' : ['base_IntfTest',   'CCriticalEvents',     {'pass':'VERIFY_SMART',    'fail':'FAIL_PROC'},      []],
         'VERIFY_SMART' : ['base_IntfTest',   'CVerifySMART',        {'pass':'RESET_SMART',     'fail':'FAIL_PROC'},      []],
         'RESET_SMART'  : ['base_IntfTest',   'CClearSMART',         {'pass':'CHK_SMART_ATTR',  'fail':'FAIL_PROC'},      []],
         'CHK_SMART_ATTR': ['base_IntfTest',  'CChkSmartAttr',       {'pass':'RESET_DOS',       'fail':'FAIL_PROC'},      []],
         'RESET_DOS'    : ['base_IntfTest',   'CClearDOS',           {'pass':'ENABLE_UDR2',         'fail':'FAIL_PROC'},  []],
         'ENABLE_UDR2'  : ['base_IntfTest',   'CEnableUDR2',         {'pass':'SDOD',            'fail':'FAIL_PROC'},      []],
         'SDOD'         : ['base_IntfTest',    'CSDOD',               {'pass':'END_TEST',        'fail':'FAIL_PROC'},     []],
         'CCV_Y_N'      : ['base_SATACCVTest', 'CCheckForCCVTest',   {'pass':'CCVTest',         'fail':'FAIL_PROC',  'noCCV':'CLEANUP'},      []],
         'CCVTest'      : ['base_SATACCVTest', 'CCCVTest',           {'pass':'CLEANUP',            'fail':'FAIL_PROC'},   []],
         'CLEANUP'      : [ 'base_SATACCVTest','CCleanupPostCCV',    {'pass':'END_TEST',          'fail':'FAIL_PROC'},    [{'FE_0174396_231166_P_MOVE_CLEANUP_TO_OWN_STATE':1}]],
         'END_TEST'     : ['base_IntfTest',   'CEndTesting',         {'pass':'COMPLETE',        'fail':'FAIL_PROC'},      []],
         'FAIL_PROC'    : ['base_IntfTest',   'CFailProc',           {'pass':'COMPLETE',        'fail':'COMPLETE'},       []],
         'COMPLETE'     : [0,],
      }

   else:
      StateTable['FIN2'] = {
         #-------------------------------------------------------------------------------------------------------------------
         #  State            Module         Method                          Transitions                      Optional by
         #
         #                                                                                                     GOTF 'G'
         #-------------------------------------------------------------------------------------------------------------------
         'INIT'         : ['base_IntfTest',   'CInitTesting',        {'pass':'DISABLE_UDR2',    'fail':'FAIL_PROC'},      []],
         #'PBIC_DATA_LD' : ['base_SerialTest', 'CPBI_Data',           {'pass':'DISABLE_UDR2',    'fail':'FAIL_PROC'},      [{'PBIC_SUPPORT' : 1}]],

         'DISABLE_UDR2' : ['base_IntfTest',   'CDisableUDR2',        {'pass':'LC_SPINUP',       'fail':'FAIL_PROC'},      []],
         'LC_SPINUP'    : ['base_IntfTest',   'CConfigLowCurrentSpinup',   {'pass':'INTFTTR',   'fail':'FAIL_PROC'},      []],
         'INTFTTR'      : ['CustomerScreens', 'CIntfTTR',            {'pass':'AGB_BEATUP',      'fail':'FAIL_PROC'},      []],
         'AGB_BEATUP'   : ['base_SerialTest', 'CAGB_Beatup',         {'pass':'WRITE_XFER',      'fail':'FAIL_PROC'},      []], #Phone: LowContact Air Bearing eval
         'WRITE_XFER'   : ['base_IntfTest',   'CZoneXferTest',       {'pass':'READ_XFER',       'fail':'FAIL_PROC'},      []],
         'READ_XFER'    : ['base_IntfTest',   'CZoneXferTest',       {'pass':'IOMQM',           'fail':'FAIL_PROC'},      []],
         'IOMQM'        : ['base_IntfTest',   'CGIO',                {'pass':'DO_COMMIT',       'fail':'FAIL_PROC'},      []],
         'DO_COMMIT'    : ['CommitCls',       'CAutoCommit',         {'pass':'VOLTAGE_HL',      'fail':'FAIL_PROC'},      []],
         'VOLTAGE_HL'   : ['base_IntfTest',   'CVoltageHLTest',      {'pass':'COMMAND_SET',     'fail':'FAIL_PROC'},      []],
         'COMMAND_SET'  : ['base_IntfTest',   'CCommandSet',         {'pass':'POWER_MODE',      'fail':'FAIL_PROC'},      []],
         'POWER_MODE'   : ['base_IntfTest',   'CPowerMode',          {'pass':'SMART_DST',       'fail':'FAIL_PROC'},      []],
         'SMART_DST'    : ['base_IntfTest',   'CSmartDSTShort',      {'pass':'CUST_CFG',        'fail':'FAIL_PROC'},      []],
         'CUST_CFG'     : ['base_IntfTest',   'CCustomConfig',       {'pass':'ATTR_VAL',        'fail':'FAIL_PROC'},      []],
         'ATTR_VAL'     : ['base_IntfTest',   'CSetDriveConfigAttributes', {'pass':'ENABLE_FAFH', 'fail':'FAIL_PROC'},    []],
         'ENABLE_FAFH'  : ['base_IntfTest',   'CEnaFAFH',            {'pass':'S_PARITY_CHK',    'fail':'FAIL_PROC'},      [{'ENABLE_FAFH_FIN2':1}]],
         'S_PARITY_CHK' : ['base_IntfTest',   'CSParityCheck',       {'pass':'WR_VERIFY',       'fail':'FAIL_PROC'},      []],
         'WR_VERIFY'    : ['base_IntfTest',   'CWRVerify',           {'pass':'ENABLE_MC',       'fail':'FAIL_PROC'},      [{'ROSEWOOD7 : 0'}]],
         'ENABLE_MC'    : ['base_IntfTest',   'CEnableMC',           {'pass':'SMART_DFT_LIST',  'fail':'FAIL_PROC'},      [{'ENABLE_MEDIA_CACHE':1}]],
         'SMART_DFT_LIST': ['base_IntfTest',  'CSmartDefectList',    {'pass':'CRITICAL_LOG',    'fail':'FAIL_PROC'},      []],
         'CRITICAL_LOG' : ['base_IntfTest',   'CCriticalEvents',     {'pass':'VERIFY_SMART',    'fail':'FAIL_PROC'},      []],
         'VERIFY_SMART' : ['base_IntfTest',   'CVerifySMART',        {'pass':'RESET_SMART',     'fail':'FAIL_PROC'},      []],
         'RESET_SMART'  : ['base_IntfTest',   'CClearSMART',         {'pass':'CHK_SMART_ATTR',  'fail':'FAIL_PROC'},      []],
         'CHK_SMART_ATTR': ['base_IntfTest',  'CChkSmartAttr',       {'pass':'RESET_DOS',       'fail':'FAIL_PROC'},      []],
         'RESET_DOS'    : ['base_IntfTest',   'CClearDOS',           {'pass':'NVCACHE_INIT',    'fail':'FAIL_PROC'},      []],
         'NVCACHE_INIT' : ['NVCache',         'InitNVCacheWithDiags',{'pass':'FINAL_PREP',      'fail':'FAIL_PROC'},      [{'FE_0000000_305538_HYBRID_DRIVE' : 1}]],
         'FINAL_PREP'   : ['CustomerContent', 'CFinalPrep',          {'pass':'RESET_UDS',       'fail':'FAIL_PROC'},      [{'FE_0385431_MOVE_FINAL_LIFE_STATE_TO_END':1}]],
         'RESET_UDS'    : ['base_IntfTest',   'CClearUds',           {'pass':'ENABLE_UDR2',     'fail':'FAIL_PROC'},      [{'FE_0252611_433430_CLEAR_UDS' : 1}]],
         'ENABLE_UDR2'  : ['base_IntfTest',   'CEnableUDR2',         {'pass':'CLEAR_EWLM',      'fail':'FAIL_PROC'},      []],
         'CLEAR_EWLM'   : ['base_IntfTest',   'CClearEWLM',          {'pass':'CCVMAIN',         'fail':'FAIL_PROC'},      []],
         'CCVMAIN'      : ['base_CCV',        'CCCV_main',           {'pass':'SDOD',            'fail':'FAIL_PROC'},      []],
         'SDOD'         : ['base_IntfTest',   'CSDOD',               {'pass':'END_TEST',        'fail':'FAIL_PROC'},      []],
         'END_TEST'     : ['base_IntfTest',   'CEndTesting',         {'pass':'COMPLETE',        'fail':'FAIL_PROC'},      []],
         'FAIL_PROC'    : ['base_IntfTest',   'CFailProc',           {'pass':'COMPLETE',        'fail':'COMPLETE'},       []],
         'COMPLETE'     : [0,],

      }

      if DriveAttributes.get('IOFIN2_PENDING', 'NONE') == "2": #For customers that require CCT test
         StateTable['FIN2'].update({
            'LC_SPINUP'    : ['base_IntfTest',   'CConfigLowCurrentSpinup',   {'pass':'SP_TTR',    'fail':'FAIL_PROC'}, []],
            'SP_TTR'       : ['CustomerScreens', 'CSP_TTR',             {'pass':'AGB_BEATUP',      'fail':'FAIL_PROC'}, []], #serial TTR test
            'AGB_BEATUP'   : ['base_SerialTest', 'CAGB_Beatup',         {'pass':'SP_WR_TRUPUT',    'fail':'FAIL_PROC'},      []], #Phone: LowContact Air Bearing eval
            'SP_WR_TRUPUT' : ['base_RssScreens', 'CSerial_Truput',      {'pass':'SP_RD_TRUPUT',    'fail':'FAIL_PROC'}, []], #serial Throughput test
            'SP_RD_TRUPUT' : ['base_RssScreens', 'CSerial_Truput',      {'pass':'DO_COMMIT',       'fail':'FAIL_PROC'}, []], #skip IOMQM
            'POWER_MODE'   : ['base_IntfTest',   'CPowerMode',          {'pass':'CUST_CFG',        'fail':'FAIL_PROC'}, []], #skip ShortDST

            'S_PARITY_CHK' : ['base_IntfTest',   'CSParityCheck',       {'pass':'ENABLE_MC',       'fail':'FAIL_PROC'}, []], #skip WRVERIFY
            'ENABLE_MC'    : ['base_IntfTest',   'CEnableMC',           {'pass':'SMART_DST',       'fail':'FAIL_PROC'}, [{'ENABLE_MEDIA_CACHE':1}]], #Long DST
            'SMART_DST'    : ['base_IntfTest',   'CSmartDSTLong',       {'pass':'SMART_DFT_LIST',  'fail':'FAIL_PROC'}, []],
         })
         if testSwitch.ENABLE_SONY_FT2:
            StateTable['FIN2'].update({
               'DO_COMMIT'    : ['CommitCls',       'CAutoCommit',         {'pass':'SONY_FT2',        'fail':'FAIL_PROC'}, []],
               'SONY_FT2'     : ['CustomerScreens', 'CSony_FT2Test',       {'pass':'VOLTAGE_HL',      'fail':'FAIL_PROC'}, []],
            })
            
else: # No IO process
   StateTable['FIN2'] = {
      #-------------------------------------------------------------------------------------------------------------------
      #  State            Module             Method                          Transitions                            Optional by
      #
      #                                                                                                             GOTF 'G'
      #-------------------------------------------------------------------------------------------------------------------
      'INIT'         : ['Serial_Init',     'CInitTesting',              {'pass':'LONG_DST',        'fail':'FAIL_PROC'}, []],
      'LONG_DST'     : ['GIO',             'CSPFIN2',                   {'pass':'LC_SPINUP',       'fail':'FAIL_PROC'}, [{'FE_0296361_402984_DEFECT_LIST_TRACKING_FROM_CRT2' : 1}]],
      'LC_SPINUP'    : ['base_IntfTest',   'CConfigLowCurrentSpinup',   {'pass':'SP_TTR',          'fail':'FAIL_PROC'}, []],
      'PBIC_DATA_LD' : ['base_SerialTest', 'CPBI_Data',                 {'pass':'DISABLE_UDR2',    'fail':'FAIL_PROC'}, [{'PBIC_SUPPORT' : 1}]],
      'SP_TTR'       : ['CustomerScreens', 'CSP_TTR',                   {'pass':'AGB_BEATUP',      'fail':'FAIL_PROC'}, []],
      'AGB_BEATUP'   : ['base_SerialTest', 'CAGB_Beatup',               {'pass':'DISABLE_UDR2',    'fail':'FAIL_PROC'}, []], #Phone: LowContact Air Bearing eval
      'DISABLE_UDR2' : ['base_IntfTest',   'CDisableUDR2',              {'pass':'SP_WR_TRUPUT',    'fail':'FAIL_PROC'}, []],
      'SP_WR_TRUPUT' : ['base_RssScreens', 'CSerial_Truput',            {'pass':'SP_RD_TRUPUT',    'fail':'FAIL_PROC'}, []],
      'SP_RD_TRUPUT' : ['base_RssScreens', 'CSerial_Truput',            {'pass':'DO_COMMIT',       'fail':'FAIL_PROC'}, []],
      #'SP_APPLE'    : ['base_RssScreens', 'CSP_Apple',                 {'pass':'DO_COMMIT',       'fail':'FAIL_PROC'}, []],
      'DO_COMMIT'    : ['CommitCls',       'CAutoCommit',               {'pass':'CUST_CFG',        'fail':'FAIL_PROC'}, []],
      #'POWER_MODE'   : ['base_IntfTest',   'CPowerMode',                {'pass':'CUST_CFG',        'fail':'FAIL_PROC'}, []],
      'CUST_CFG'     : ['base_IntfTest',   'CCustomConfig',             {'pass':'ATTR_VAL',        'fail':'FAIL_PROC'}, []],
      'ATTR_VAL'     : ['base_IntfTest',   'CSetDriveConfigAttributes', {'pass':'ENABLE_FAFH',     'fail':'FAIL_PROC'}, []],
      'ENABLE_FAFH'  : ['base_IntfTest',   'CEnaFAFH',                  {'pass':'S_PARITY_CHK',    'fail':'FAIL_PROC'}, [{'ENABLE_FAFH_FIN2':1}]],
      'S_PARITY_CHK' : ['base_IntfTest',   'CSParityCheck',             {'pass':'WR_VERIFY',       'fail':'FAIL_PROC'}, [{'CHECK_SUPERPARITY_INVALID_RATIO': 1}]],
      'WR_VERIFY'    : ['base_IntfTest',   'CWRVerify',                 {'pass':'VERIFY_MC',       'fail':'FAIL_PROC'}, [{'ROSEWOOD7 : 0'}]],
      'VERIFY_MC'    : ['base_IntfTest',   'CEnableMC',                 {'pass':'SP_WR_TRUPUT2',   'fail':'FAIL_PROC'}, []],
      'SP_WR_TRUPUT2': ['base_RssScreens', 'CSerial_Truput',            {'pass':'SP_RD_TRUPUT2',   'fail':'FAIL_PROC'}, []],
      'SP_RD_TRUPUT2': ['base_RssScreens', 'CSerial_Truput',            {'pass':'SPFIN2',          'fail':'FAIL_PROC'}, []],
      'SPFIN2'       : ['GIO',             'CSPFIN2',                   {'pass':'NVCACHE_INIT',       'fail':'FAIL_PROC'}, []],
      #'RESET_DOS'    : ['base_IntfTest',   'CClearDOS',                 {'pass':'NVCACHE_INIT',    'fail':'FAIL_PROC'}, []], #checked in CCVMAIN
      'NVCACHE_INIT' : ['NVCache',         'InitNVCacheWithDiags',      {'pass':'FINAL_PREP',      'fail':'FAIL_PROC'}, [{'FE_0000000_305538_HYBRID_DRIVE' : 1}]],
      'FINAL_PREP'   : ['CustomerContent', 'CFinalPrep',                {'pass':'ENABLE_UDR2',     'fail':'FAIL_PROC'}, [{'FE_0385431_MOVE_FINAL_LIFE_STATE_TO_END' : 1}]],
      #'RESET_UDS'    : ['base_IntfTest',   'CClearUds',                 {'pass':'ENABLE_UDR2',     'fail':'FAIL_PROC'}, [{'FE_0252611_433430_CLEAR_UDS' : 1}]], #checked in CCVMAIN
      'ENABLE_UDR2'  : ['base_IntfTest',   'CEnableUDR2',               {'pass':'CCVMAIN',      'fail':'FAIL_PROC'}, []],
      #'CLEAR_EWLM'   : ['base_IntfTest',   'CClearEWLM',                {'pass':'CCVMAIN',         'fail':'FAIL_PROC'}, []], #checked in CCVMAIN
      'CCVMAIN'      : ['base_CCV',        'CCCV_main',                 {'pass':'SDOD',            'fail':'FAIL_PROC'},      []],
      'SDOD'         : ['base_IntfTest',   'CSDOD',                     {'pass':'END_TEST',        'fail':'FAIL_PROC'},      []],
      'END_TEST'     : ['Serial_Exit',     'CEndTesting',               {'pass':'COMPLETE',        'fail':'FAIL_PROC'}, []],
      'FAIL_PROC'    : ['Serial_Exit',     'CFailProc',                 {'pass':'COMPLETE',        'fail':'COMPLETE'},  []],
      'COMPLETE'     : [0,],

   }


# State Input Arguments Table
StateParams['FIN2'] = {
   'CRITICAL_LOG'    : "{'PARAM_NAME': 'TP.prm_CriticalEvents',}",
   'WRITE_XFER'      : "{'XFER_TYPE': 'TP.prm_598_w', 'XFER_MODE': 'WRITE'}",
   'READ_XFER'       : "{'XFER_TYPE': 'TP.prm_598_r',}",
   'CCT_TEST'        : "{'CCT_TEST': 'TP.prm_510_CCT'}",
   'SP_WR_TRUPUT'    : "{'XFER_TYPE': 'TP.prm_sp_wr_truput',}",
   'SP_RD_TRUPUT'    : "{'XFER_TYPE': 'TP.prm_sp_rd_truput',}",
   'SP_WR_TRUPUT2'   : "{'XFER_TYPE': 'TP.prm_sp_wr_truput2', 'OFWXferRatio': 'TP.OFWXferRatioLimit'}",
   'SP_RD_TRUPUT2'   : "{'XFER_TYPE': 'TP.prm_sp_rd_truput2'}",

   # For 3-tier code download state handling
   'DNLD_CODE_TCG2'  : "{'CODES': ['TGTB','OVLB','IV','TGT','OVL', 'SFW'],}",
   'DNLD_U_CODE2'    : "{'CODES': ['TGT','OVL','SFW'], 'CMP_CODE': 1}",     # Compare and include servo code
   'SERIAL_FMT2'     : "{'FORMAT_OPTIONS': 'TP.formatOptions'}",
}

###################################################################################################################
#CHOOI-03Jun17 OffSpec
StateTable['CUT2'] = {
   #-------------------------------------------------------------------------------------------------------------------
   #  State            Module         Method                          Transitions                      Optional by
   #
   #                                                                                                     GOTF 'G'
   #-------------------------------------------------------------------------------------------------------------------
   'INIT'               : ['base_IntfTest',   'CInitTesting',                {'pass':'DNLD_OOS_CODE',    'fail':'FAIL_PROC'},  []],
   'DNLD_OOS_CODE'      : ['base_IntfTest',   'CDnlduCode',                  {'pass':'OOS_CHECK_ID_1',   'fail':'FAIL_PROC'},  []],
   'OOS_CHECK_ID_1'     : ['base_IntfTest',   'CSetDriveConfigAttributes',   {'pass':'COMPLETE',         'fail':'FAIL_PROC'},  []],

#    'OOS_CHECK_ID_1'     : ['base_IntfTest',   'CSetDriveConfigAttributes',   {'pass':'WRITE_ATTR_VAL_1', 'fail':'WRITE_ATTR_VAL_1'},  []],
#    'WRITE_ATTR_VAL_1'   : ['base_IntfTest',   'CSetDriveConfigAttributes',   {'pass':'DNLD_NORMAL_CODE', 'fail':'DNLD_NORMAL_CODE'},  []],
#    'DNLD_NORMAL_CODE'   : ['base_IntfTest',   'CDnlduCode',                  {'pass':'WRITE_ATTR_VAL_2', 'fail':'WRITE_ATTR_VAL_2'},  []],
#    'WRITE_ATTR_VAL_2'   : ['base_IntfTest',   'CSetDriveConfigAttributes',   {'pass':'OOS_CHECK_ID_2',   'fail':'OOS_CHECK_ID_2'},    []],
#    'OOS_CHECK_ID_2'     : ['base_IntfTest',   'CSetDriveConfigAttributes',   {'pass':'COMPLETE',         'fail':'FAIL_PROC'},         []],

   'END_TEST'           : ['base_IntfTest',    'CEndTesting',                {'pass':'COMPLETE',        'fail':'FAIL_PROC'},  []],
   'FAIL_PROC'          : ['base_IntfTest',    'CFailProc',                  {'pass':'COMPLETE',        'fail':'COMPLETE' },  []],
   'COMPLETE'           : [0,],
}


#CHOOI-03JUN17 OFFSPEC
StateParams['CUT2'] = {
   'DNLD_OOS_CODE'      : {'CODES': ['TGT5',], 'CMP_CODE': 0},
   'DNLD_OOS_CODE_1'    : {'CODES': ['TGT5',], 'CMP_CODE': 0},
   'DNLD_NORMAL_CODE'   : {'CODES': ['TGT','OVL'], 'CMP_CODE': 0},
}


###################################################################################################################
StateTable['CCV2'] = {
      #--------------------------------------------------------------------------------------------------------------------------------
      #  State                   Module             Method                          Transitions                            Optional by
      #
      #                                                                                                                     GOTF 'G'
      #--------------------------------------------------------------------------------------------------------------------------------
      'INIT'                 : ['Serial_Init',     'CInitTesting',              {'pass':'CCVMAIN',             'fail':'FAIL_PROC'}, []],

      'CCVMAIN'              : ['base_CCV',        'CCCV_main',                 {'pass':'END_TEST',            'fail':'FAIL_PROC'}, []],

      'END_TEST'             : ['Serial_Exit',     'CEndTesting',               {'pass':'COMPLETE',            'fail':'FAIL_PROC'}, []],
      'FAIL_PROC'            : ['Serial_Exit',     'CFailProc',                 {'pass':'COMPLETE',            'fail':'COMPLETE'},  []],
      'COMPLETE'             : [0,],
   }
StateParams['CCV2'] = {
#For now, no param input
}

###################################################################################################################
# State Transition Table
StateTable['AUD2'] = {
   #---------------------------------------------------------------------------------------------------------------
   #  State            Module         Method                          Transitions                      Optional by
   #
   #                                                                                                     GOTF 'G'
   #---------------------------------------------------------------------------------------------------------------
   'INIT'         : ['IntfTest',    'CInitTesting',   {'pass':'ACCESS_TIME',    'fail':'FAIL_PROC'},      []],
   'ACCESS_TIME'  : ['IntfTest',    'CAccessTime',    {'pass':'COMMAND_SET',    'fail':'FAIL_PROC'},      []],
   'COMMAND_SET'  : ['IntfTest',    'CCommandSet',    {'pass':'POWER_MODE',     'fail':'FAIL_PROC'},      []],
   'POWER_MODE'   : ['IntfTest',    'CPowerMode',     {'pass':'DRAM_SCREEN',    'fail':'FAIL_PROC'},      []],
   'DRAM_SCREEN'  : ['IntfTest',    'CDRamScreen',    {'pass':'READ_WRITE',     'fail':'FAIL_PROC'},      []],
   'READ_WRITE'   : ['IntfTest',    'CReadWrite',     {'pass':'RESET_SMART',    'fail':'FAIL_PROC'},      []],
   'RESET_SMART'  : ['base_SerSMART',  'CClearSMART',    {'pass':'END_TEST',       'fail':'FAIL_PROC'},      []],
   'END_TEST'     : ['IntfTest',    'CEndTesting',    {'pass':'COMPLETE',       'fail':'FAIL_PROC'},      []],
   'FAIL_PROC'    : ['IntfTest',    'CFailProc',      {'pass':'COMPLETE',       'fail':'COMPLETE'},       []],
   'COMPLETE'     : [0,],
}

# State Input Arguments Table
StateParams['AUD2'] = {
    'READ_WRITE' : "{'WRITE': 'prm_510_FPW', 'READ': 'prm_510_FPR',}",
}

#####################################################################################################################
# State Transition Table
if testSwitch.NoIO == 0:
   StateTable['FNG2'] = {
      #----------------------------------------------------------------------------------------------------
      #  State            Module         Method                          Transitions                      Optional by
      #
      #                                                                                                     GOTF 'G'
      #---------------------------------------------------------------------------------------------------------------
      'INIT'         : ['base_IntfTest',   'CInitTesting',     {'pass':'DISABLE_UDR2',    'fail':'FAIL_PROC'},      []],
      'DISABLE_UDR2' : ['base_IntfTest',   'CDisableUDR2',     {'pass':'VOLTAGE_HL',      'fail':'FAIL_PROC'},      []],
      'VOLTAGE_HL'   : ['base_IntfTest',   'CVoltageHLTest',   {'pass':'COMMAND_SET',     'fail':'FAIL_PROC'},      []],
      'COMMAND_SET'  : ['base_IntfTest',   'CCommandSet',      {'pass':'POWER_MODE',      'fail':'FAIL_PROC'},      []],
      'POWER_MODE'   : ['base_IntfTest',   'CPowerMode',       {'pass':'SMART_DST',       'fail':'FAIL_PROC'},      []],
      'SMART_DST'    : ['base_IntfTest',   'CSmartDSTShort',   {'pass':'FULL_WRITE',      'fail':'FAIL_PROC'},      []],
      'FULL_WRITE'   : ['base_IntfTest',   'CPackWrite',       {'pass':'FULL_READ',       'fail':'FAIL_PROC'},      []],
      'FULL_READ'    : ['base_IntfTest',   'CFullZeroCheck',   {'pass':'SMART_DFT_LIST',  'fail':'FAIL_PROC'},      []],
      'SMART_DFT_LIST': ['base_IntfTest',  'CSmartDefectList', {'pass':'CRITICAL_LOG',    'fail':'FAIL_PROC'},      []],
      'CRITICAL_LOG' : ['base_IntfTest',   'CCriticalEvents',  {'pass':'VERIFY_SMART',    'fail':'FAIL_PROC'},      []],
      'VERIFY_SMART' : ['base_IntfTest',   'CVerifySMART',     {'pass':'RESET_SMART',     'fail':'FAIL_PROC'},      []],
      'RESET_SMART'  : ['base_IntfTest',   'CClearSMART',      {'pass':'CUST_CFG',        'fail':'FAIL_PROC'},      []],
      'CUST_CFG'     : ['base_IntfTest',   'CCustomConfig',    {'pass':'ATTR_VAL',        'fail':'FAIL_PROC'},      []],
      'ATTR_VAL'     : ['base_IntfTest',   'CSetDriveConfigAttributes', {'pass':'S_PARITY_CHK', 'fail':'FAIL_PROC'},  []],
      'S_PARITY_CHK' : ['base_IntfTest',   'CSParityCheck',    {'pass':'DEFECT_LIST',     'fail':'FAIL_PROC'},      []],
      'DEFECT_LIST'  : ['base_IntfTest',   'CCheck_DefList',   {'pass':'READ_WWN',        'fail':'FAIL_PROC'},      []],
      'READ_WWN'     : ['IntfTest',        'CReadWWN',         {'pass':'SMART_DFT_LIST2', 'fail':'FAIL_PROC'},      []],
      'SMART_DFT_LIST2': ['base_IntfTest', 'CSmartDefectList', {'pass':'CRITICAL_LOG2',   'fail':'FAIL_PROC'},      []],
      'CRITICAL_LOG2': ['base_IntfTest',   'CCriticalEvents',  {'pass':'VERIFY_SMART2',   'fail':'FAIL_PROC'},      []],
      'VERIFY_SMART2': ['base_IntfTest',   'CVerifySMART',     {'pass':'RESET_SMART2',    'fail':'FAIL_PROC'},      []],
      'RESET_SMART2' : ['base_IntfTest',   'CClearSMART',      {'pass':'SEACORDER',       'fail':'FAIL_PROC'},      []],
      'SEACORDER'    : ['base_IntfTest',   'CSeaCorder',       {'pass':'RESET_DOS',       'fail':'FAIL_PROC'},      [{'FE_0242596_356922_CLEAR_SEACORDER' : 1}]],
      'RESET_DOS'    : ['base_IntfTest',   'CClearDOS',        {'pass':'ENABLE_UDR2',     'fail':'FAIL_PROC'},      []],
      'ENABLE_UDR2'  : ['base_IntfTest',   'CEnableUDR2',      {'pass':'AMPS_CHECK',      'fail':'FAIL_PROC'},      []],
      'AMPS_CHECK'   : ['base_IntfTest',   'CAMPSCheck',       {'pass':'CLEAR_EWLM',      'fail':'FAIL_PROC'},      []],
      'CLEAR_EWLM'   : ['base_IntfTest',   'CClearEWLM',       {'pass':'SDOD',            'fail':'FAIL_PROC'},      []],
      'SDOD'         : ['base_IntfTest',   'CSDOD',            {'pass':'END_TEST',        'fail':'FAIL_PROC'},      []],
      'END_TEST'     : ['base_IntfTest',   'CEndTesting',      {'pass':'COMPLETE',        'fail':'FAIL_PROC'},      []],
      'FAIL_PROC'    : ['base_IntfTest',   'CFailProc',        {'pass':'COMPLETE',        'fail':'COMPLETE'},       []],
      'COMPLETE'     : [0,],
   }
   if testSwitch.ENABLE_MEDIA_CACHE:
      StateTable['FNG2'].update({
         'DISABLE_UDR2' : ['base_IntfTest',   'CDisableUDR2',        {'pass':'DISABLE_MC',      'fail':'FAIL_PROC'},      []],
         'DISABLE_MC'   : ['base_IntfTest',   'CDisableMC',          {'pass':'VOLTAGE_HL',         'fail':'FAIL_PROC'},      []],
         'RESET_DOS'    : ['base_IntfTest',   'CClearDOS',           {'pass':'ENABLE_MC',       'fail':'FAIL_PROC'},      []],
         'ENABLE_MC'    : ['base_IntfTest',   'CEnableMC',           {'pass':'ENABLE_UDR2',     'fail':'FAIL_PROC'},      []],
      })
else:
   StateTable['FNG2'] = {
      #-------------------------------------------------------------------------------------------------------------------
      #  State            Module         Method                          Transitions                      Optional by
      #
      #                                                                                                     GOTF 'G'
      #-------------------------------------------------------------------------------------------------------------------
      'INIT'         : ['Serial_Init',     'CInitTesting',              {'pass':'LC_SPINUP',       'fail':'FAIL_PROC'}, []],
      'LC_SPINUP'    : ['base_IntfTest',   'CConfigLowCurrentSpinup',   {'pass':'SP_TTR',          'fail':'FAIL_PROC'}, []],
      'PBIC_DATA_LD' : ['base_SerialTest', 'CPBI_Data',                 {'pass':'DISABLE_UDR2',    'fail':'FAIL_PROC'}, [{'PBIC_SUPPORT' : 1}]],
      'SP_TTR'       : ['CustomerScreens', 'CSP_TTR',                   {'pass':'DISABLE_UDR2',    'fail':'FAIL_PROC'}, []],
      'DISABLE_UDR2' : ['base_IntfTest',   'CDisableUDR2',              {'pass':'FULL_WRITE',      'fail':'FAIL_PROC'}, []],
      'FULL_WRITE'   : ['base_IntfTest',   'CPackWrite',                {'pass':'DO_COMMIT',       'fail':'FAIL_PROC'},      []],
      'FULL_READ'    : ['base_IntfTest',   'CFullZeroCheck',            {'pass':'DO_COMMIT',        'fail':'FAIL_PROC'},      []],
      #'SP_APPLE'    : ['base_RssScreens', 'CSP_Apple',                 {'pass':'DO_COMMIT',       'fail':'FAIL_PROC'}, []],
      'DO_COMMIT'    : ['CommitCls',       'CAutoCommit',               {'pass':'CUST_CFG',        'fail':'FAIL_PROC'}, []],
      #'POWER_MODE'   : ['base_IntfTest',   'CPowerMode',                {'pass':'CUST_CFG',        'fail':'FAIL_PROC'}, []],
      'CUST_CFG'     : ['base_IntfTest',   'CCustomConfig',             {'pass':'ATTR_VAL',        'fail':'FAIL_PROC'}, []],
      'ATTR_VAL'     : ['base_IntfTest',   'CSetDriveConfigAttributes', {'pass':'ENABLE_FAFH',     'fail':'FAIL_PROC'}, []],
      'ENABLE_FAFH'  : ['base_IntfTest',   'CEnaFAFH',                  {'pass':'S_PARITY_CHK',    'fail':'FAIL_PROC'}, [{'ENABLE_FAFH_FIN2':1}]],
      'S_PARITY_CHK' : ['base_IntfTest',   'CSParityCheck',             {'pass':'WR_VERIFY',       'fail':'FAIL_PROC'}, [{'CHECK_SUPERPARITY_INVALID_RATIO': 1}]],
      'WR_VERIFY'    : ['base_IntfTest',   'CWRVerify',                 {'pass':'VERIFY_MC',       'fail':'FAIL_PROC'}, [{'ROSEWOOD7 : 0'}]],
      'VERIFY_MC'    : ['base_IntfTest',   'CEnableMC',                 {'pass':'SPFIN2',          'fail':'FAIL_PROC'}, []],
      'SPFIN2'       : ['GIO',             'CSPFIN2',                   {'pass':'NVCACHE_INIT',       'fail':'FAIL_PROC'}, []],
      #'RESET_DOS'    : ['base_IntfTest',   'CClearDOS',                 {'pass':'NVCACHE_INIT',    'fail':'FAIL_PROC'}, []], #checked in CCVMAIN
      'NVCACHE_INIT' : ['NVCache',         'InitNVCacheWithDiags',      {'pass':'FINAL_PREP',      'fail':'FAIL_PROC'}, [{'FE_0000000_305538_HYBRID_DRIVE' : 1}]],
      'FINAL_PREP'   : ['CustomerContent', 'CFinalPrep',                {'pass':'ENABLE_UDR2',       'fail':'FAIL_PROC'}, [{'FE_0385431_MOVE_FINAL_LIFE_STATE_TO_END' : 1}]],
      #'RESET_UDS'    : ['base_IntfTest',   'CClearUds',                 {'pass':'ENABLE_UDR2',     'fail':'FAIL_PROC'}, [{'FE_0252611_433430_CLEAR_UDS' : 1}]], #checked in CCVMAIN
      'ENABLE_UDR2'  : ['base_IntfTest',   'CEnableUDR2',               {'pass':'CCVMAIN',      'fail':'FAIL_PROC'}, []],
      #'CLEAR_EWLM'   : ['base_IntfTest',   'CClearEWLM',                {'pass':'CCVMAIN',         'fail':'FAIL_PROC'}, []], #checked in CCVMAIN
      'CCVMAIN'      : ['base_CCV',        'CCCV_main',                 {'pass':'SDOD',            'fail':'FAIL_PROC'}, []],
      'SDOD'         : ['base_IntfTest',   'CSDOD',                     {'pass':'END_TEST',        'fail':'FAIL_PROC'}, []],
      'END_TEST'     : ['Serial_Exit',     'CEndTesting',               {'pass':'COMPLETE',        'fail':'FAIL_PROC'}, []],
      'FAIL_PROC'    : ['Serial_Exit',     'CFailProc',                 {'pass':'COMPLETE',        'fail':'COMPLETE'},  []],
      'COMPLETE'     : [0,],
   }

# State Input Arguments Table
StateParams['FNG2'] = {
    'CRITICAL_LOG'   : "{'PARAM_NAME': 'TP.prm_CriticalEvents',}",
}

#####################################################################################################################
# Test Process Operation Sequence

Operations = ['PRE2','FNC2','CRT2','FIN2']



CCV2Operations = ['CCV2']
#####################################################################################################################
#####################################################################################################################
