#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Module that stores aliases for column definitions coming from firmware
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/12/12 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/DbLogAlias.py $
# $Revision: #8 $
# $DateTime: 2016/12/12 22:04:57 $
# $Author: chengyi.guo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/DbLogAlias.py#8 $
# Level:3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from Test_Switches import testSwitch
from tabledictionary import tableHeaders
from DBLogDefs import DbLogTableDefinitions

"""
Rules for aliases
*Keys in dictionary must be the keys used in the process references
*List assigned to the keys must contain the key as well as the aliases
"""

dbLogColAliases = {
   'HD_LGC_PSN'         : 'HD',
   'MAX_HEAD'           : 'MAX_HD',
   'NUM_CYL'            : 'TRK_NUM',
   'RAW_ERROR_RATE'     : 'BIT_ERROR_RATE',
   'TRK_NUM'            : 'NUM_CYL',
   'TEST_TRACK'         : 'START_TRK_NUM',
   'WRT_HT_CLR'         : 'WRT_HEAT_CLR',
   'WRT_LOSS'           : 'WRITE_LOSS',
   'ZN'                 : 'DATA_ZONE',
   'DIAG_HEX'           : 'DIAG_HEX',
   'ZN_START_CYL'       : 'ZONE_START_CYL',
   }

dbLogTableAliases = {
   'ADZ_SUMARRY'                 : ['ADZ_SUMARRY'],
   'OPTI_ZN_SUMMARY'             : ['OPTI_ZN_SUMMARY'],
   'MMT_SUMMARY'                 : ['MMT_SUMMARY'],
   'P000_DEPOP_HEADS'            : ['P000_DEPOP_HEADS',],
   'P000_PG_HW_DETECTED_ERR'     : ['P000_PG_HW_DETECTED_ERR'],
   'P000_PWA_MOD_NO'             : ['P000_PWA_MOD_NO'],
   'P000_SERVO_UNSAFE_FLAG2'     : ['P000_SERVO_UNSAFE_FLAG2'],
   'P010_FORCE_CONSTANT'         : ['P010_FORCE_CONSTANT'],
   'P011_DO_SERVO_CMD'           : ['P011_DO_SERVO_CMD', 'P011_DO_SERVO_CMD10'],
   'P011_RD_SRVO_VPD_VIA_WRD'    : ['P011_RD_SRVO_VPD_VIA_WRD'],
   'P011_RW_SRVO_RAM_VIA_ADDR'   : ['P011_RW_SRVO_RAM_VIA_ADDR'],
   'P011_SRVO_DIAG_RESP'         : ['P011_SRVO_DIAG_RESP'],   
   'P011_SV_RAM_RD_BY_OFFSET'    : ['P011_SV_RAM_RD_BY_OFFSET'],
   'P025_LD_UNLD_PARAM_STATS'    : ['P025_LD_UNLD_PARAM_STATS'],
   'P030_ESP_SEEK'               : ['P030_ESP_SEEK'],
   'P033_PES_HD2'                : ['P033_PES_HD2'],
   'P035_CFH_DYNAMIC_THRSHLD'    : ['P035_CFH_DYNAMIC_THRSHLD'],
   'P041_PES_SCREEN'             : ['P041_PES_SCREEN'],
   'P047_ECCENTRICITY'           : ['P047_ECCENTRICITY'],
   'P049_HEAT_CLEARANCE'         : ['P049_HEAT_CLEARANCE'],
   'P049_TRACK_CONVERT'          : ['P049_TRACK_CONVERT'],
   'P050_ENCROACH_BER'           : ['P050_ENCROACH_BER'],
   'P051_ERASURE_BER'            : ['P051_ERASURE_BER'],
   'P052_ZGS_CAL_DATA'           : ['P052_ZGS_CAL_DATA'],
   'P055_CONTACT_SUMMARY2'       : ['P055_CONTACT_SUMMARY2'],
   'P055_DICE_FINAL_CONTACT'     : ['P055_DICE_FINAL_CONTACT'],
   'P055_DICE_SUMMARY'           : ['P055_DICE_SUMMARY'],
   'P061_OW_MEASUREMENT'         : ['P061_OW_MEASUREMENT'],
   'P382_OW_MEASUREMENT'         : ['P382_OW_MEASUREMENT'],
   'P061_BAND_OW_MEASUREMENT'    : ['P061_BAND_OW_MEASUREMENT'],
   'P062_BIAS_BACKOFF'           : ['P062_BIAS_BACKOFF'],
   'P069_EWAC_DATA'              : ['P069_EWAC_DATA'],
   'P069_EWAC_HSC'               : ['P069_EWAC_HSC'],
   'P069_EWAC_SUMMARY'           : ['P069_EWAC_SUMMARY'],
   'P069_WPE_DATA'               : ['P069_WPE_DATA'],
   'P069_WPE_HSC'                : ['P069_WPE_HSC'],
   'P069_WPE_SUMMARY'            : ['P069_WPE_SUMMARY'],
   'P072_SUMMARY'                : ['P072_SUMMARY'],
   'P083_AGC'                    : ['P083_AGC'],
   'P103_WIJITA'                 : ['P103_WIJITA'],
   'P107_DBI_LOG_ZONE_SUMMARY'   : ['P107_DBI_LOG_ZONE_SUMMARY'],
   'P107_VERIFIED_FLAWS'         : ['P107_VERIFIED_FLAWS'],
   'P109_LOG_VER_DATA_ERR'       : ['P109_LOG_VER_DATA_ERR'],
   'P109_LUL_ERROR_COUNT'        : ['P109_LUL_ERROR_COUNT'],
   'P109_THRESHOLD_SUM'          : ['P109_THRESHOLD_SUM'],
   'P117_MEDIA_SCREEN'           : ['P117_MEDIA_SCREEN','P117_MEDIA_SCREEN_02'],
   'P126_SRVO_FLAW_HD'           : ['P126_SRVO_FLAW_HD'],
   'P126_SRVO_FLAW_TRACE'        : ['P126_SRVO_FLAW_TRACE'],
   'P130_SLIP_SCTR_CNT2'         : ['P130_SLIP_SCTR_CNT2'],
   'P130_SYS_SLIST_DETAILED'     : ['P130_SYS_SLIST_DETAILED'],
   'P134_TA_DETCR_DETAIL'        : ['P134_TA_DETCR_DETAIL'],
   'P134_TA_SUM_HD2'             : ['P134_TA_SUM_HD2'],
   'P135_FINAL_CONTACT'          : ['P135_FINAL_CONTACT'],
   'P135_SEARCH_RESULTS'         : ['P135_SEARCH_RESULTS'],
   'P135_SEARCH_RESULTS_DAC'     : ['P135_SEARCH_RESULTS_DAC'],
   'P135_USED_TRACK_INFO'        : ['P135_USED_TRACK_INFO'],
   'P135_FINAL_CURVE_FIT_STAT'   : ['P135_FINAL_CURVE_FIT_STAT'],
   'P136_BDRAG_FCONS'            : ['P136_BDRAG_FCONS'],
   'P140_FLAW_COUNT'             : ['P140_FLAW_COUNT'],
   'P141_CQM'                    : ['P141_CQM'],
   'P150_GAIN_SUM'               : ['P150_GAIN_SUM'],
   'P150_GAIN_SUM'               : ['P150_GAIN_SUM'],
   'P150_GAIN_SUM2'              : ['P150_GAIN_SUM2'],
   'P151_CQM'                    : ['P151_CQM'],
   'P152_BODE_GAIN_ONLY'         : ['P152_BODE_GAIN_ONLY'],
   'P152_BODE_GAIN_PHASE'        : ['P152_BODE_GAIN_PHASE'],
   'P152_BODE_SCRN_SUM'          : ['P152_BODE_SCRN_SUM'],
   'P166_CHANNEL_INFO'           : ['P166_CHANNEL_INFO'],
   'P166_CONTROLLER_REV'         : ['P166_CONTROLLER_REV'],
   'P166_DRAM_INFO'              : ['P166_DRAM_INFO'],
   'P166_HDA_PCBA_INFO'          : ['P166_HDA_PCBA_INFO'],
   'P166_PREAMP_INFO'            : ['P166_PREAMP_INFO'],
   'P166_RAP_REVISIONS'          : ['P166_RAP_REVISIONS', 'P166_RAP_REV'],
   'P166_SELFTEST_PACKAGENAME'   : ['P166_SELFTEST_PACKAGENAME'],
   'P166_SELFTEST_REV'           : ['P166_SELFTEST_REV', 'P166_SELFTEST_REVISION'],
   'P166_SERVO_REVISIONS'        : ['P166_SERVO_REVISIONS', 'P166_SERVO_REV'],
   'P166_SOC_INFO'               : ['P166_SOC_INFO'],
   'P167_ERR_SQUEEZE'            : ['P167_ERR_SQUEEZE'],                # Consider moving to iso parse
   'P172_AFH_ADAPTS_SUMMARY'     : ['P172_AFH_ADAPTS_SUMMARY' ],
   'P172_AFH_CLEARANCE'          : ['P172_AFH_CLEARANCE'],
   'P172_AFH_DH_CLEARANCE'       : ['P172_AFH_DH_CLEARANCE'],
   'P172_AFH_DH_TC_COEF'         : ['P172_AFH_DH_TC_COEF'],
   'P172_AFH_DH_TC_COEF_2'       : ['P172_AFH_DH_TC_COEF_2'],
   'P172_AFH_DH_WORKING_ADAPT'   : ['P172_AFH_DH_WORKING_ADAPT' ],
   'P172_AFH_PTP_COEF'           : ['P172_AFH_PTP_COEF'],
   'P172_AFH_TARGET_CLEARANCE'   : ['P172_AFH_TARGET_CLEARANCE'],
   'P172_CLR_COEF_ADJ'           : ['P172_CLR_COEF_ADJ'],
   'P172_DRIVE_INFORMATION'      : ['P172_DRIVE_INFORMATION', 'P172_DRIVE_INFO'],
   'P172_HDA_TEMP'               : ['P172_HDA_TEMP'],
   'P172_MAX_CYL'                : ['P172_MAX_CYL'],
   'P172_MAX_CYL_VBAR'           : ['P172_MAX_CYL_VBAR'],
   'P172_MISC_INFO'              : ['P172_MISC_INFO'],
   'P172_RAP_TABLE'              : ['P172_RAP_TABLE'],                  # Consider moving to iso parse
   'P172_RESVD_ZONE_DATA'        : ['P172_RESVD_ZONE_DATA'],
   'P172_RESVD_ZONE_TBL'         : ['P172_RESVD_ZONE_TBL'],
   'P172_RSVD_ZONED_SERVO'       : ['P172_RSVD_ZONED_SERVO'],
   'P172_RSVD_ZONED_SERVO_RED'   : ['P172_RSVD_ZONED_SERVO_RED'],
   'P172_VBAR'                   : ['P172_VBAR'],
   'P172_WRITE_POWERS'           : ['P172_WRITE_POWERS'],               # Consider moving to iso parse
   'P172_ZONED_SERVO'            : ['P172_ZONED_SERVO'],
   'P172_ZONED_SERVO_RED'        : ['P172_ZONED_SERVO_RED'],
   'P172_ZONE_DATA'              : ['P172_ZONE_DATA'],                  # Consider moving to iso parse
   'P172_ZONE_TBL'               : ['P172_ZONE_TBL'],                   # Consider moving to iso parse
   'P172_ZB_INFO'                : ['P172_ZB_INFO'],
   'P176_HD_GAP_DELTA'           : ['P176_HD_GAP_DELTA'],
   'P177_GAIN_DATA'              : ['P177_GAIN_DATA'],
   'P180_NRRO_RRO_RSNC'          : ['P180_NRRO_RRO_RSNC'],
   'P185_DEFAULTS'               : ['P185_DEFAULTS'],
   'P185_START_HUNT_CYL'         : ['P185_START_HUNT_CYL'],
   'P185_TRK_0_V3BAR_CALHD'      : ['P185_TRK_0_V3BAR_CALHD'],
   'P186_BIAS_CAL'               : ['P186_BIAS_CAL', 'P186_BIAS_CAL2'],
   'P186_BIAS_CAL2'              : ['P186_BIAS_CAL2', 'P186_BIAS_CAL', 'P321_BIAS_CAL2'],
   'P186_BIAS_CAL2_MRE_DIFF'     : ['P186_BIAS_CAL2_MRE_DIFF', 'P321_BIAS_CAL2_MRE_DIFF'],
   'P190_DIHA_DATA3'             : ['P190_DIHA_DATA3'],
   'P190_HSC_DATA'               : ['P190_HSC_DATA'],
   'P190_TEST_TRACKS'            : ['P190_TEST_TRACKS'],
   'P191_CLR_COEF_CAL'           : ['P191_CLR_COEF_CAL'],
   'P191_CLR_COEF_CAL3'          : ['P191_CLR_COEF_CAL3'],
   'P195_INSTABILITY_SUM'        : ['P195_INSTABILITY_SUM'],
   'P195_STE_SUMMARY'            : ['P195_STE_SUMMARY'],                # Consider moving to iso parse
   'P195_SUMMARY'                : ['P195_SUMMARY'],
   'P195_VGA_CSM'                : ['P195_VGA_CSM'],
   'P195_VGA_CSM_STDEV'          : ['P195_VGA_CSM_STDEV'],
   'P199_INSTABILITY_TA'         : ['P199_INSTABILITY_TA'],
   'P210_CAPACITY_DRIVE'         : ['P210_CAPACITY_DRIVE'],             # Consider moving to iso parse
   'P210_CAPACITY_HD2'           : ['P210_CAPACITY_HD2'],               # Consider moving to iso parse
   'P210_CAPACITY_ZWZ_DRIVE'     : ['P210_CAPACITY_ZWZ_DRIVE'],
   'P210_CAPACITY_ZWZ_HD'        : ['P210_CAPACITY_ZWZ_HD'],
   'P210_SCTR_ERR_RATE2'         : ['P210_SCTR_ERR_RATE2'],             # Consider moving to iso parse
   'P210_VBAR_FORMATS'           : ['P210_VBAR_FORMATS'],
   'P210_VBAR_THRSHLD'           : ['P210_VBAR_THRSHLD'],               # Consider moving to iso parse
   'P210_VBAR_THRSHLD2'          : ['P210_VBAR_THRSHLD2'],              # Consider moving to iso parse
   'P211_BCI_ERROR'              : ['P211_BCI_ERROR'],
   'P211_BPI_CAP_AVG'            : ['P211_BPI_CAP_AVG'],                # Consider moving to iso parse
   'P211_BPI_MEASUREMENT'        : ['P211_BPI_MEASUREMENT'],
   'P211_BPI_MEASUREMENT'        : ['P211_BPI_MEASUREMENT'],   
   'P211_ELT_ERROR'              : ['P211_ELT_ERROR'],
   'P211_ELT_REF_SECTORS'        : ['P211_ELT_REF_SECTORS'],
   'P211_HMS_CAP_AVG'            : ['P211_HMS_CAP_AVG'],
   'P211_HMS_CAP_AVG2'           : ['P211_HMS_CAP_AVG2'],
   'P211_HMS_MEASUREMENT'        : ['P211_HMS_MEASUREMENT'],
   'P211_M11K_BPI_MEASUREMENT'   : ['P211_M11K_BPI_MEASUREMENT'],
   'P211_M_BPI_MEASUREMENT'      : ['P211_M_BPI_MEASUREMENT'],
   'P211_RD_OFST_AVG'            : ['P211_RD_OFST_AVG'],
   'P211_TPI_CAP_AVG'            : ['P211_TPI_CAP_AVG'],                # Consider moving to iso parse
   'P211_TPI_CAP_AVG2'           : ['P211_TPI_CAP_AVG2'],               # Consider moving to iso parse
   'P211_TPI_MEASUREMENT2'       : ['P211_TPI_MEASUREMENT2'],           #for S2D Scheme
   'P211_TPI_MEASUREMENT3'       : ['P211_TPI_MEASUREMENT3'],           #for OTC Bucket Scheme
   'P211_WPC_SUMMARY'            : ['P211_WPC_SUMMARY'], 
   'P215_TA_DFCT_TRK_CNT'        : ['P215_TA_DFCT_TRK_CNT'],
   'P227_FLY_HEIGHT_ADJ'         : ['P227_FLY_HEIGHT_ADJ'],             # Consider moving to iso parse
   'P230_VAR_SPARE_ALLOC'        : ['P230_VAR_SPARE_ALLOC'],
   'P231_HEADER'                 : ['P231_HEADER'],                     # Consider moving to iso parse
   'P231_HEADER_INFO'            : ['P231_HEADER_INFO'],                # Consider moving to iso parse
   'P233_AUTORUN_SUMMARY'        : ['P233_AUTORUN_SUMMARY'],            # Consider moving to iso parse
   'P234_EAW_ERROR_RATE2'        : ['P234_EAW_ERROR_RATE2'],
   'P238_MICROJOG_CAL'           : ['P238_MICROJOG_CAL'],
   'P238_MICROJOG_HD_STATUS'     : ['P238_MICROJOG_HD_STATUS'],
   'P238_MICROJOG_ZERO_SKEW'     : ['P238_MICROJOG_ZERO_SKEW'],
   'P250_ERROR_RATE'             : ['P250_ERROR_RATE'],
   'P250_ERROR_RATE_BY_ZONE'     : ['P250_ERROR_RATE_BY_ZONE'],
   'P382_ERROR_RATE_BY_ZONE'     : ['P382_ERROR_RATE_BY_ZONE'],
   'P250_FSOW_BIE'               : ['P250_FSOW_BIE'],
   'P250_SEGMENT_BER_SUM'        : ['P250_SEGMENT_BER_SUM'],
   'P250_SEGMENT_BIE'            : ['P250_SEGMENT_BIE'],
   'P251_FITNESS_R_SQUARED'      : ['P251_FITNESS_R_SQUARED'],
   'P251_STATUS'                 : ['P251_STATUS'],
   'P252_FIRST_SCTR_COLD_WRT'    : ['P252_FIRST_SCTR_COLD_WRT'],
   'P269_MT50_RESULT_DATA'       : ['P269_MT50_RESULT_DATA'],
   'P270_EB_RESULT_DATA'         : ['P270_EB_RESULT_DATA'],
   'P297_HD_INSTBY_BIE_SUM'      : ['P297_HD_INSTBY_BIE_SUM'],
   'P315_INSTABILITY_METRIC'     : ['P315_INSTABILITY_METRIC'],
   'P321_BIAS_CAL2'              : ['P321_BIAS_CAL2'],
   'P321_BIAS_CAL2_MRE_DIFF'     : ['P321_BIAS_CAL2_MRE_DIFF'],
   'P337_OVERWRITE'              : ['P337_OVERWRITE'],
   'P514_IDENTIFY_DEVICE_DATA'   : ['P514_IDENTIFY_DEVICE_DATA'],
   'P528_TIMED_PWRUP'            : ['P528_TIMED_PWRUP',],
   'P549_IO_SK_TIME'             : ['P549_IO_SK_TIME',], 
   'P552_DISPLAY_DRIVE_INFO'     : ['P552_DISPLAY_DRIVE_INFO'],
   'P597_ADV_TAG_Q'              : ['P597_ADV_TAG_Q'],                  # Consider moving to iso parse
   'P598_ZONE_XFER_RATE'         : ['P598_ZONE_XFER_RATE'],             # Consider moving to iso parse
   'P600_SELF_TEST_STATUS'       : ['P600_SELF_TEST_STATUS'],
   'P639_BLUENUNSCAN'            : ['P639_BLUENUNSCAN',],         
   'P639_BLUENUNSLIDE'           : ['P639_BLUENUNSLIDE',],
   'P641_DMAEXT_TRANSFER_RATE'   : ['P641_DMAEXT_TRANSFER_RATE'],
   'P648_EYE_MEASUREMENT'        : ['P648_EYE_MEASUREMENT'],
   'P707_ADAPGAIN_COMP'          : ['P707_ADAPGAIN_COMP'],
   'P_CCT_DISTRIBUTION'          : ['P_CCT_DISTRIBUTION'],
   'P_CCT_MAX_CMD_TIMES'         : ['P_CCT_MAX_CMD_TIMES'],
   'P_DFLAWSCAN_STATUS'          : ['P_DFLAWSCAN_STATUS'],
   'P_ERROR_RATE_STATUS'         : ['P_ERROR_RATE_STATUS'],
   'P_OAR_SCREEN_SUMMARY'        : ['P_OAR_SCREEN_SUMMARY'],
   'P_OAR_SUMMARY'               : ['P_OAR_SUMMARY'],
   'P_PRECODER_SUMMARY_TABLE'    : ['P_PRECODER_SUMMARY_TABLE'],
   'P_SUSTAINED_TRANSFER_RATE'   : ['P_SUSTAINED_TRANSFER_RATE'],
   'P_TRACK'                     : ['P_TRACK'],
   'P_VBAR_FORMAT_SUMMARY_ZN0'   : ['P_VBAR_FORMAT_SUMMARY_ZN0'],
   'P172_ZONED_SERVO2'           : ['P172_ZONED_SERVO2'],
   'P135_DETCR_OPTI_SETTINGS2'   : ['P135_DETCR_OPTI_SETTINGS2'],
   'P250_SEGMENT_BER_SUM2'       : ['P250_SEGMENT_BER_SUM2'],
   'P287_PHYS_TRK_STATS'         : ['P287_PHYS_TRK_STATS'],
   'P287_ZEST_STATE_INFO'        : ['P287_ZEST_STATE_INFO'],
   'P_FAILING_HEAD'              : ['P_FAILING_HEAD'],
   'P025_UNLOAD_PROFILE'         : ['P025_UNLOAD_PROFILE'],
   'P223_PHOTO_DIODE_DATA'       : ['P223_PHOTO_DIODE_DATA'], 
   'P172_PREAMP_HAMR_LASER'      : ['P172_PREAMP_HAMR_LASER'],
   'P230_BPI_REVERT_SUMMARY'     : ['P230_BPI_REVERT_SUMMARY'],
   'P172_HEAD_TPI_CONFIG_TBL'    : ['P172_HEAD_TPI_CONFIG_TBL'],
   'P189_HD_SKEW_DETAILS2'       : ['P189_HD_SKEW_DETAILS2'],   
   }

if testSwitch.AutoFA_IDDIS_Enabled:
  dbLogTableAliases.update({
     'P136_BIAS_VALUE'             : ['P136_BIAS_VALUE'],
     'P238_ERROR_INFO'             : ['P238_ERROR_INFO'],
     'P109_SERVO_ERROR_INFO'       : ['P109_SERVO_ERROR_INFO'],
     'P109_AC_PARAJOG_SUMMARY'     : ['P109_AC_PARAJOG_SUMMARY'],
     'P_TRACK'                     : ['P_TRACK'],
     'P109_UNSAFE_SUMMARY'         : ['P109_UNSAFE_SUMMARY'],
     'P134_TA_DETCT_TRIPAD'        : ['P134_TA_DETCT_TRIPAD'],
     'P140_UNVER_HD_TOTAL'         : ['P140_UNVER_HD_TOTAL'],
     'P177_GAIN_DATA'              : ['P177_GAIN_DATA'],
     'P177_GAIN_DATA_DETAILS2'     : ['P177_GAIN_DATA_DETAILS2'],
     'P250_BER_MTRIX_BY_ZONE'      : ['P250_BER_MTRIX_BY_ZONE'],
  })

if testSwitch.WA_0112781_007955_CREATE_P051_MILLIONW_PREDICTIN_EXT:
   dbLogTableAliases.update({
      'P051_MILLIONW_PREDICTIN'     : ['P051_MILLIONW_PREDICTIN'],
      'P051_MILLIONW_PREDICTIN_EXT' : ['P051_MILLIONW_PREDICTIN_EXT'],
   })
if 1:
   dbLogTableAliases.update({
      'DBS_MTRIX_BY_ZONE'     : ['DBS_MTRIX_BY_ZONE'],
   })
if testSwitch.ENABLE_DESTROKE_BASE_ON_T193_CHROME:
   dbLogTableAliases.update({
      'P193_CRRO_MEASUREMENT2'     : ['P193_CRRO_MEASUREMENT2'],
   })

if testSwitch.FE_0134030_347506_SAVE_AND_RESTORE:
   dbLogTableAliases.update({
      'P172_CAP_TABLE'       : ['P172_CAP_TABLE'],
   })
if testSwitch.checkMediaFlip:
   dbLogTableAliases.update({
      'P134_TA_SUM_HD2'       : ['P134_TA_SUM_HD2'],
   })

if testSwitch.IN_DRIVE_AFH_COEFF_PER_HEAD_GENERATION_SUPPORT:
   dbLogTableAliases.update({
      'P192_DELTA_WL'               : ['P192_DELTA_WL'],
   })   
if testSwitch.FE_0207956_463655_AFH_ENABLE_WGC_CLR_TUNING:
   dbLogTableAliases.update({
	  'P253_WGC_ELT_CODEWORD'         : ['P253_WGC_ELT_CODEWORD'],
   })
if testSwitch.RUN_SNO_PD:
   dbLogTableAliases.update({
      'P152_BODE_GAIN_PHASE'        : ['P152_BODE_GAIN_PHASE'],
      'P152_PHASE_PEAK_SUMMARY'     : ['P152_PHASE_PEAK_SUMMARY'],
      'P000_DRIVE_VAR_TABLE'        : ['P000_DRIVE_VAR_TABLE'],        
   })

#override/update the current dictionary with program specific changes
try:
   import pgm_DbLogAlias
   dbLogTableAliases.update(pgm_DbLogAlias.dbLogTableAliases)
   dbLogColAliases.update(pgm_DbLogAlias.dbLogColAliases)
except:
   pass

if testSwitch.FE_0148166_381158_DEPOP_ON_THE_FLY: 
   import PIF
   for errCode in PIF.depop_OTF_Config.keys():
       for depop_state in PIF.depop_OTF_Config[errCode].keys():
          if PIF.depop_OTF_Config[errCode][depop_state].has_key('Table'):
             dbLogTableAliases.update({PIF.depop_OTF_Config[errCode][depop_state]['Table']:[PIF.depop_OTF_Config[errCode][depop_state]['Table']]})


#-------------------------------------------------------------------------------
# Use this script to sort dbLogTableAliases in alphabetic order.
# Paste dbLogTableAliases and the following lines into a file and execute with python.
# Replace table with sorted table.
#
#print 'dbLogTableAliases = {'
#for k,v in sorted(dbLogTableAliases.items()):
#   print ("   %-28s  :  %s," % (`k`,v))
#print '}'
#-------------------------------------------------------------------------------
########### Module level constants #############

def createReverseTableLookup():
    outputDict = {}
    for tableCode,defTuple in tableHeaders.items():
        outputDict[defTuple[0]] = tableCode
    return outputDict

reverseTableHeaders = createReverseTableLookup()
################################################

#Process tables that override firmware definitions
OracleTableOverrides = ['P_EVENT_SUMMARY','TEST_TIME_BY_TEST', 'TESTER_TIMESTAMP', 'TEST_TIME_BY_STATE']

processTableOverrides = OracleTableOverrides
processTableOverrides.extend(DbLogTableDefinitions.OracleTables.keys())

dbLogTableAliasesMaster = []
for key in dbLogTableAliases.keys():
   dbLogTableAliasesMaster.append(key)
   dbLogTableAliasesMaster.extend(dbLogTableAliases[key])

#---------------------------------------------------------------------------------------------------------#
