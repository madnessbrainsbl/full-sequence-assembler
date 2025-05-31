#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: This file holds all operational switches for the process. Flags defined here are overridden by
#                 the program.
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/12/18 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_TestParameters.py $
# $Revision: #12 $
# $DateTime: 2016/12/18 23:21:55 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_TestParameters.py#12 $
# Level: 2
#---------------------------------------------------------------------------------------------------------#

from Test_Switches import testSwitch

Native_Capacity = ['500G']
RetailTabList = ['995']

formatIteration = '103'

T50T51RetryParams = {
   'NUM_RETRIES' : 2,
}

CalcClrByPos_Prm_49 = {
   'test_num': 49,
   'prm_name': 'calc_Clr_by_pos',
   'timeout': 100,  # this is 1000 times longer than the test should take.
   'spc_id': 1,
   'CWORD1': 5,
}

CalcClrByZone_Prm_49 = {
   'test_num': 49,
   'prm_name': 'calculateClearanceByZone',
   'timeout': 600,
   'spc_id': 1,
   'CWORD1': 2,
}

TA_LIST_Prm_130 = {
   'test_num': 130,
   'prm_name': 'TAListPrm_130',
   'timeout': 5000,
   'CWORD1': (0x100),
   'spc_id': 1
}

dumpPreampRegs_172 = {
   'test_num': 172,
   'prm_name': 'dumpPreampRegs_172',
   'timeout': 60,
   'CWORD1': 41,
   'spc_id': 1,
}

AFH_Clearance_Prm_172 = {
   'test_num': 172,
   'prm_name': 'P172_AFH_CLEARANCE',
   'timeout': 1800,
   'CWORD1': (5,),
   'spc_id': 1
}

AFH_Drive_Adapts_Dump_Prm_172 = {
   'test_num': 172,
   'prm_name': 'AFH Drive Adapts Dump',
   'timeout': 1800,
   'CWORD1': (16,),
   'spc_id': 1
}

AFH_GAMMA_Prm_172 = {
   'test_num': 172,
   'prm_name': 'P172_AFH_GAMMA:',
   'timeout': 1800,
   'CWORD1': (21,),
   'spc_id': 1
}

AFH_PTP_Coef_Dump_Prm_172 = {
   'test_num': 172,
   'prm_name': 'AFH PTP Coef Dump',
   'timeout': 1800,
   'CWORD1': (15,),
   'spc_id': 1
}

AFH_WorkingAdapts_Prm_172 = {
   'test_num': 172,
   'prm_name': 'P172_AFH_WORKING_ADAPTS',
   'timeout': 1800,
   'CWORD1': (4,),
   'spc_id': 1
}

AFH_Display_Working_Preamp_Adaptives_Table_Prm_172 = {

   # WARNING!!! - This test call tweaks flyheight heater values!!!

   'test_num': 172,
   'prm_name': 'P172_AFH_WORKING_ADAPTS',
   'timeout': 1800,
   'CWORD1': 42,
   'spc_id': 1
}

hdstrTestFlags = {
   'Hdstr_In_Gemini'          : 'N',               #  Run HDSTR tests in Gemini rather than moving to HDSTR  Y/N
}

Retrieve_TC_Coeff_Prm_172 = {
   'test_num':172,
   'prm_name': 'Retrieve TC Coefficient',
   "CWORD1" : (10),
   'spc_id': 1,
   'timeout': 100,
}

RetrieveWPs_Prm_172 = {
   'test_num': 172,
   'prm_name': "Retrieve WP's",
   'CWORD1': 12,
   'timeout': 100,
   'spc_id': 1
}

setZgsFlagInCapPrm_178 = {
   'test_num' : 178,
   'prm_name' : 'setZgsFlagInCapPrm_178',
   'timeout'  : 1200,
   'spc_id'   : 1,
   "CWORD1"   : 0x0120,
   "CAP_WORD" : (0x0071,0x0100,0xFF00),
}
setRVFlagInCapPrm_178 = {
   'test_num' : 178,
   'prm_name' : 'setRVFlagInCapPrm_178',
   'timeout'  : 1200,
   'spc_id'   : 1,
   "CWORD1"   : 0x0120,
   "CAP_WORD" : (0x0071,0x0200,0xFF00),
}
resetByte227InCapPrm_178 = {
   'test_num' : 178,
   'prm_name' : 'resetByte227InCapPrm_178',
   'timeout'  : 1200,
   'spc_id'   : 1,
   "CWORD1"   : 0x0120,
   "CAP_WORD" : (0x0071,0x0000,0xFF00),
}

baseCoefs_Prm_178 = {
   'test_num': 178,
   'prm_name' : 'baseCoefs_178',
   "CWORD1" : (0x2200,),
   "CWORD2" : (0x0007,),
   "WRT_PTP_COEF" : (0x0005, 0x0004, 0xA29E,),  #21 COEFFS
   "HTR_PTP_COEF" : (0x0003, 0x0000, 0xEA22,),  #6 COEFFS
   "WRT_HTR_PTP_COEF" : (0x0000, 0x000C, 0x636D,), #10 COEFFS
   "BIT_MASK" : (0x0000, 0x0002,), # Bit = Index of coeff to update with input value.
}

CAPUpdate_Prm_178 = {
   'test_num': 178,
   'CWORD1': 0x20,
   'timeout': 300,
}

RAPUpdate_Prm_178 = {
   'test_num': 178,
   'CWORD1':  (0x0220),
   'timeout': 300,
}

ZN_REMAP_DEST_CAP_OFS = 0xAD

prm_setCAPRemapZone_178 = {
   'test_num'    : 178,
   'prm_name'    : "prm_setCAPRemapZone_178",
   'timeout'     :900,
   'CAP_WORD'    :(0x00AD,0xFF16,0xFF), # Set Zone Remap Destination to after Last Usr Zone-1
   "CWORD1"      : 288,
}

prm_enableAGB_178 = {
   'test_num'    : 178,
   'prm_name'    : "prm_enableAGB",
   'timeout'     :900,
   'CAP_WORD'    :(0x00AA,0xFFFE,0xFFFF), # CAP Word to enable AGB
   "CWORD1"      : 288,
}

TC_Coeff_Prm_178 = {
   'test_num': 178,
   'prm_name': 'Set TC Coefficient',
   "CWORD1" : (0x2204,),
   "CWORD2" : (0x0040,),
   "TEMPERATURE_COEF" : (0x0000, 0x0000,), #High word= integer portion, Low word = decimal portion * 10^3 converted to HEX
   "HEAD_RANGE" : 0xFF, # Head mask of heads to update with input parms
   "BIT_MASK" : (0x0000, 0x0002,), # Bit = Index of coeff to update with input value - Indexes start at 1
}


TC_Coeff_Prm_178_DH = {
   'test_num': 178,
   'prm_name': 'Set TCS values for DH',
   "CWORD1" : (0x2200,),
   "CWORD2" : (0x0000,),
}

clearanceSettling_Prm_178 = {
   'test_num': 178,
   'prm_name': 'clearance settling parameters for test 178',
   "CWORD1" : (0x2200,),
   "CWORD2" : (0x0000,),
}

AFH_CLEARANCE_SETTLING_CLEARANCE_SETTLING_CORRECTION_BY_HEAD                                              = 100

displayClearanceSettling_Prm_172 = {
   'test_num'              : 172,
   'prm_name'              : 'displayClearanceSettling from RAP using test 172',
   'CWORD1'                : 33,
   'C_ARRAY1'              : [0,AFH_CLEARANCE_SETTLING_CLEARANCE_SETTLING_CORRECTION_BY_HEAD,0,0,0,0,0,0,0,0],
   'timeout'               : 1000,
   }

test172_displayClearanceSettlingData = {
   'test_num'              : 172,
   'prm_name'              : 'test172_displayClearanceSettlingData',
   'CWORD1'                : 33,
   'C_ARRAY1'              : [0,AFH_CLEARANCE_SETTLING_CLEARANCE_SETTLING_CORRECTION_BY_HEAD,0,0,0,0,0,0,0,0],
   'timeout'               : 1000,
   }



# Parameters for MR Resistance Check while on ramp
get_MR_Values_on_ramp_186 = {
   'test_num'              : 186,
   'prm_name'              : 'get_MR_Values_on_ramp_186',
   'spc_id'                : 1,
   'CWORD1'                : 0x1006,  # Only gather and report MR resistance values, while on ramp
   }


set0Pattern_Prm_508 = {
   'spc_id': 1,
   'test_num': 508,
   'prm_name': "base_prm_set0Pattern_508",
   'CTRL_WORD1': 0,
   'PATTERN_TYPE':0,
   'DATA_PATTERN0':(0,0),
    'DATA_PATTERN1':(0,0),
}

CPCRiser_FinalAssemDate_Prm_557 = {
   'test_num'                : 557,
   'prm_name'                : "FinalAssemDate_Prm_557",
   "CTRL_WORD1"              : (0x0001),
   "TEST_FUNCTION"           : (1),         # 0=Write, 1=Read, 2=Compare to current date, Final Assembly Date Code
   "BYTE_OFFSET"             : (0, 0x0046),
#      "MAX_DIFFERENCE_IN_DAYS"  : (14),        # Fail if more than 14 days
   "FINAL_ASSEMBLY_DATE"     : (0,0,0,0),
   "timeout"                 : 600,
}

IF3_FinalAssemDate_Prm_557 = {
   'test_num'                : 557,
   'prm_name'                : "prm_557_FinalAssemDate",
   "DATE_FORMAT" : (0x0001,),
   "ETF_DATE_OFFSET" : (0x0046,),
   "CURRENT_MONTH_YEAR" : (0),
   "TEST_OPERATING_MODE" : (0x0000,),
   "TEST_FUNCTION" : (0x0000,),
   "CURRENT_DAY_WEEK" : (0,),
   "MAX_ETF_DAYS_DELTA" : (0x0000,),
   "timeout"                 : 600,
}

randWrite_Prm_597 = {
   'spc_id': 1,
   'test_num': 597,
   'prm_name': "base_prm_randWrite_597",
   'CTRL_WORD1': 0x0011,
   'LOOP_COUNT': 25000,
   'MIN_SECTOR_COUNT': 8,
   'MAX_SECTOR_COUNT': 8,
   'timeout': 600,
}

randRead_Prm_597 = {
   'spc_id': 1,
   'test_num': 597,
   'prm_name': "base_prm_randRead_597",
   'CTRL_WORD1': 0x0021,
   'LOOP_COUNT': 25000,
   'MIN_SECTOR_COUNT': 8,
   'MAX_SECTOR_COUNT': 8,
   'timeout': 600,
}

formatMIF_Prm_638 = {
   'test_num':638,
   'prm_name': "format MIF",
   'DFB_WORD_0' : 0x4501,
   'DFB_WORD_1' : 0x0100,
   'DFB_WORD_2' : 0x0500,
   'DFB_WORD_3' : 0x0000,
   'DFB_WORD_4' : 0x0000,
   'DFB_WORD_5' : 0x0000,
   'DFB_WORD_6' : 0x0100,
   'DFB_WORD_7' : 0x0000,
   'timeout' : 25200
}

displayMIF_Prm_638 = {}
displayMIF_Prm_638.update( formatMIF_Prm_638 )
displayMIF_Prm_638['prm_name'] = "Display MIF"
displayMIF_Prm_638['DFB_WORD_0'] = 0x4401
displayMIF_Prm_638['DFB_WORD_6'] = 0x0000

prm_638_WrtAltTones = {
   'test_num' : 638,
   'prm_name' : 'prm_638_WrtAltTones',
   'timeout' : 1200,
   "ATTRIBUTE_MODE" : (0x0000,),
   "BYPASS_WAIT_UNIT_RDY" : (0x0001,),
   "CMD_BYTE_GROUP_0" : (0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,),
   "CMD_BYTE_GROUP_1" : (0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,),
   "CMD_BYTE_GROUP_2" : (0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,),
   "CMD_DFB_LENGTH" : (0x0000,),
   "LONG_COMMAND" : (0x0000,),
   "PARAMETER_0" : (0x5201,),
   "PARAMETER_1" : (0x0100,),
   "PARAMETER_2" : (0x0902,),
   "PARAMETER_3" : (0x0000,),
   "PARAMETER_4" : (0x0000,),
   "PARAMETER_5" : (0x0200,),
   "PARAMETER_6" : (0x0000,),
   "PARAMETER_7" : (0x0000,),
   "PARAMETER_8" : (0x0000,),
   "REPORT_OPTION" : (0x0000,),
   "SCSI_COMMAND" : (0x0000,),
   "SECTOR_SIZE" : (0x0000,),
   "TEST_FUNCTION" : (0x0000,),
   "TRANSFER_LENGTH" : (0x0000,),
   "TRANSFER_MODE" : (0x0000,),
   "WRITE_SECTOR_CMD_ALL_HDS" : (0x0000,),
}

prm_638_HeadAmpMeasurements = {
   'test_num':638,
   'prm_name':'prm_638_HeadAmpMeasurements',
   'timeout':1200,
   'CTRL_WORD1' : 0x0000,
   'DFB_WORD_0' : 0x5201,
   'DFB_WORD_1' : 0x0100,
   'DFB_WORD_2' : 0x0A00,
   'DFB_WORD_3' : 0x0000,
   'DFB_WORD_4' : 0x0000,
   'DFB_WORD_5' : 0x0000,
}

if testSwitch.WA_0256539_480505_SKDC_M10P_BRING_UP_DEBUG_OPTION:
   setDetcrOnPrm_011 = {
    'test_num'               : 11,
    'prm_name'               : 'setDetcrOnPrm_011',
    'spc_id'                 : 1,
    'NUM_LOCS'               : 0,
    'SYM_OFFSET'             : 384,
    'MASK_VALUE'             : 0,
    'timeout'                : 120,
    'WR_DATA'                : 1,
    'CWORD1'                 : 1024,
   }
   setDetcrOffPrm_011 = setDetcrOnPrm_011.copy()
   setDetcrOffPrm_011.update({'prm_name': 'setDetcrOffPrm_011',})
   setDetcrOffPrm_011.update({'WR_DATA' : 0,})

setZapOnPrm_011 = {
   'ATTRIBUTE'                   : 'BF_0119055_231166_USE_SVO_CMD_ZAP_CTRL',
   'DEFAULT'                     : 0,
   1                             : {         # BF_0119055_231166_USE_SVO_CMD_ZAP_CTRL = 1
      'test_num'                 : 11,
      'prm_name'                 : 'setZapOnPrm_011',
      'timeout'                  : 300,
      "PARAM_0_4"                : [0x00ff,0x0500,0,0,0]
   },
   0                             : {         # BF_0119055_231166_USE_SVO_CMD_ZAP_CTRL = 0
      'test_num'                 : 11,
      'prm_name'                 : 'setZapOnPrm_011',
      'timeout'                  : 300,
      "CWORD1"                   : (0x0400,),
      "SYM_OFFSET"               : (152,),         #  Symbol Offset
      "WR_DATA"                  : (0x0005,),
      "MASK_VALUE"               : (0x1110,),
      "NUM_LOCS"                 : (0x0000),
      "ACCESS_TYPE"              : (2,),
   },
}
setZapOffPrm_011 = {
   'ATTRIBUTE'                   : 'BF_0119055_231166_USE_SVO_CMD_ZAP_CTRL',
   'DEFAULT'                     : 0,
   1                             : {         # BF_0119055_231166_USE_SVO_CMD_ZAP_CTRL = 1
      'test_num'                 : 11,
      'prm_name'                 : 'setZapOffPrm_011',
      'timeout'                  : 300,
      "PARAM_0_4"                : [0x00ff,0x0000,0,0,0]
   },
   0                             : {         # BF_0119055_231166_USE_SVO_CMD_ZAP_CTRL = 0
      'test_num'                 : 11,
      'prm_name'                 : 'setZapOffPrm_011',
      'timeout'                  : 300,
      "CWORD1"                   : (0x0400,),
      "SYM_OFFSET"               : (152,),         #  Symbol Offset
      "WR_DATA"                  : (0x0000,),
      "MASK_VALUE"               : (0x1110,),
      "NUM_LOCS"                 : (0x0000),
      "ACCESS_TYPE"              : (2,),
   },
}

zapPrm_175_zapOff = {                   # Turn off ZAP
   'ATTRIBUTE'              : 'ZFS',
   'DEFAULT'                : 0,
   1                        : {
      'test_num'            : 275,
      'prm_name'            : 'zapPrm_275_zapOff',
      'timeout'             : 1800,
      'CWORD1'              : 0x0103,                # Generate 'Read' and 'Write' ZAP, force invalid ZAP flag in SAP
   },
   0                        : {
      'test_num'            : 175,
      'prm_name'            : 'zapPrm_175_zapOff',
      'timeout'             : 1800,
      'CWORD1'              : 0x1024,                # Generate 'Read' and 'Write' ZAP, force invalid ZAP flag in SAP
   },
}

zapPrm_175_zapOn = {                   # Turn on ZAP
   'ATTRIBUTE'              : 'ZFS',
   'DEFAULT'                : 0,
   1                        : {
      'test_num'            : 275,
      'prm_name'            : 'zapPrm_275_zapOn',
      'timeout'             : 500,
      'ZAP_SPAN'            : 0,                # need to set zap_span to 0 to turn on zap
      'CWORD1'              : 0x0083,                # enable both read and write ZAP
   },
   0                        : {
      'test_num'            : 175,
      'prm_name'            : 'zapPrm_175_zapOn',
      'timeout'             : 3*60,
      'CWORD1'              : 0x1028,                # enable both read and write ZAP
   },
}

prm_ZAP_OTF = {
   'GEN_PC_FILES'             : 0,
   'ITERATIONS'               : 20,
   'WZAP_MABS_RRO_LIMIT'      : 246,
   'RZAP_MABS_RRO_LIMIT'      : 287,
   'INJ_AMPL'                 : 300,
   'START_HARM'               : 10,
}

##################### AFH #####################################



# T109 to be used in AFH Clean-up
prm_109_AFH_CleanUpWriteZeroesToTracks = {
   'test_num'                 : 109,
   'prm_name'                 : '109_track_cleanup_for_test135',
   'timeout'                  : 3000,

              "RW_MODE" : (
   0x0040 |  # BLOCK_WRITE
                        0,),

               "CWORD1" : (
##  0x0002 |   # UNCERT_TO_SKIPTRACK - Log Skip Tracks.  Uncertified tracks (up to head clamp limit) will be logged
               # as skip-tracks in the servo flaw table instead of being logged as uncertified tracks.
   0x0001 |  # REP_SERVO_ERRORS
                        0,),

               "CWORD2" : (
   0x0800 |  # REPORT_SUMMARY_TABLES - Summary Tables - Servo errors, RW errors, Not certified count, Head clamp,
   0x0400 |  # REPORT_DEBUG_MSGS
                        0,),

               "CWORD4" : (
                        0,),

               "START_CYL" : (0x0000,0x0000,),  ##############  START LBA  #############

               "END_CYL" : (0x0000,0x3F00,),  ##############   END LBA   #############

               "RETRY_LIMIT" : (100),         # Read retries
}




setPreampHeaterMode_178 = {
   'test_num'                 : 178,
   'prm_name'                 : 'setPreampHeaterMode_178',
   'spc_id'                   : 1,
   "CWORD1"                   : (0x6224,),
   "CWORD2"                   : (0x0080,),
}

reportDPesPrm_35 = {
# Test 35 Delta PES
  # OD
   'test_num'                 : 35,
   'prm_name'                 : 'reportDPesPrm_35',
   'timeout'                  : 2000,
   'spc_id'                   : 1,
   "CWORD1"                   : (0x0001,),         # Report Delta PES only
   "REPORT_OPTION"            : (4,),
}

deStroke_drive_185_params = {
   'test_num'              : 185,
   'prm_name'              : 'deStroke_drive_185_params',
   'spc_id'                : 1,
   'CWORD1'                : 0x2800, # Set Stroke - Recalculate the TPI Warp and Logical to Physical Track polynomials
   }

lubeSmoothPrm_33 = {
   'test_num'              : 30,
   'prm_name'              : 'Lube Smoothing Parameter',
   'spc_id'                : 1,
   'iTrack'                : 100,  #Process only definition parameter... overridden in level 3
   # Process only param. Used to spec the seek range for smoothing
   # Actual smoothing range is range/2-dPES_Track->range/2+dPES_Track
   'range'                 : 100,
   'CWORD1'                : 0x0306,
   'TIME'                  : (1, 1000, 1000),
   'PASSES'                : 100,
   'SEEK_DELAY'            : 10,
   'BIT_MASK'              : (0, 0),
   'START_CYL'             : (0, 0x0100),
   'END_CYL'               : (0, 0x0200),
   }

activeClearControl_178 = {
   'test_num'              : 178,
   'prm_name'              : 'activeClearControl_178',
   'spc_id'                : 1,
   'CWORD1'                : 0x2224,
   'CWORD2'                : 0x0018,
   'TGT_IDLE_CLR'          : 254,
   'MIN_PREHEAT_USECS'     : 1000,
   }

afhTargetClearance_by_zone = {
   'test_num'              : 178,
   'prm_name'              : 'afhTargetClearance_by_zone',
   'spc_id'                : 1,
   'CWORD1'                : 0x2204,
   'CWORD2'                : 0x0780,
   'HEAD_RANGE'            : 0xFFFF,            # Head mask of heads to update with input parms
   'BIT_MASK'              : (0xFFFF, 0xFFFF),  # Zone Mask of zones to update with input parms. Bits 16 = system zone 0, etc.
}

afhTargetWGC_by_zone= {
    'test_num'              : 178,
    'prm_name'              : 'afhTargetWGC_by_zone',
    'spc_id'                : 1,
    'timeout'               : 600,   # Extra pad - should take 5 min/zone per pass
    'HEAD_RANGE'            : 0xFFFF,            # Head mask of heads to update with input parms
    'BIT_MASK'              : (0xFFFF, 0xFFFF),  # Zone Mask of zones to update with input parms. Bits 16 = system zone 0, etc.
    'C_ARRAY1'              : [0, 31, 0, 0, 0, 0, 0,0, 0, 15], #[0, 31, 0, 0, 0, 0, 0,0,0,targetWGCClr]
}
afhDeclineStepWGC_by_zone= {
    'test_num'              : 178,
    'prm_name'              : 'afhDeclineStepWGC_by_zone',
    'spc_id'                : 1,
    'timeout'               : 600,   # Extra pad - should take 5 min/zone per pass
    'HEAD_RANGE'            : 0xFFFF,            # Head mask of heads to update with input parms
    'BIT_MASK'              : (0xFFFF, 0xFFFF),  # Zone Mask of zones to update with input parms. Bits 16 = system zone 0, etc.
    'C_ARRAY1'              : [0, 32, 0, 0, 0, 0, 0,0, 0, 0], #[0, 31, 0, 0, 0, 0, 0,0,0,targetWGCClr]
}

DeclineStepWGC_by_zone = {
   "ATTRIBUTE" : "CAPACITY_PN",
   "DEFAULT"   : "500G",
   "500G"      :{
      'ATTRIBUTE':'numZones',
      31:  31*[1],  ## only user zones
      60:  60*[0],  ## only user zones ,0 is base on Chengai product
        },
   "320G"      :{
      'ATTRIBUTE':'numZones',
      31:  31*[1],  ## only user zones
      60:  60*[0],  ## only user zones ,0 is base on Chengai product
        },
}
afhDeclineCntWGC_by_zone= {
    'test_num'              : 178,
    'prm_name'              : 'afhDeclineCntWGC_by_zone',
    'spc_id'                : 1,
    'timeout'               : 600,   # Extra pad - should take 5 min/zone per pass
    'HEAD_RANGE'            : 0xFFFF,            # Head mask of heads to update with input parms
    'BIT_MASK'              : (0xFFFF, 0xFFFF),  # Zone Mask of zones to update with input parms. Bits 16 = system zone 0, etc.
    'C_ARRAY1'              : [0, 33, 0, 0, 0, 0, 0,0, 0, 0], #[0, 31, 0, 0, 0, 0, 0,0,0,targetWGCClr]
}
DeclineCntWGC_by_zone = {
   "ATTRIBUTE" : "CAPACITY_PN",
   "DEFAULT"   : "500G",
   "500G"      : {
      'ATTRIBUTE':'numZones',
      31:  [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5],
      60:  [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5],
        },
   "320G"      : {
      'ATTRIBUTE':'numZones',
      31:  [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 7],
      60:  [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6],
        },
}

minTCCTempDifferential = 19                     # temp delta required between AFH3 and AFH4;  ideally > 20C.
TccAccMargin = 0                                # temp margin
TccAccMarginCold = 2                            # temp margin
requiredDeltaTempBetweenAFH2_and_AFH3 = 0       # temp delta required between AFH2 and AFH3;  ideally should be 0.

# How many degrees Celsius between valid temperature ranges
# Historic ST-10 minimum of 14 has been used as a starting point.
TccCal_temp_range = 14

# How many temperature ranges to run for multi-temp CERT
nTempCERT = 2

prm_011_TimingMarkEnable = {

    'test_num'              :   11,
    'MASK_VALUE'            :   (0xEFFF),
    'CWORD1'                :   (0x0002),
    'WR_DATA'               :   (0x1000),
    'ACCESS_TYPE'           :   (0x0002),
    }
if testSwitch.FE_0184102_326816_ZONED_SERVO_SUPPORT: # zoned servo support
   prm_011_TimingMarkEnable.update({
    'test_num'              :   11,
    'SYM_OFFSET'            :   (0x012E), #302
    'MASK_VALUE'            :   (0x0000),
    'EXTENDED_MASK_VALUE'   :   (0x0020),
    'CWORD1'                :   (0x0800),
    'WR_DATA'               :   (0x1000),
    'ACCESS_TYPE'           :   (0x0002),
    })

masterHeatPrm_11 = {
   #Master heat control parameter
   #AFH will modify DriveAttribute['masterHeatState']
   'enable' : {
      'test_num'           : 11,
      'prm_name'           : 'masterHeatEnable',
      'spc_id'             : 1,
      'CWORD1'             : 0x0400,
      'SYM_OFFSET'         : 222,      #  Symbol Offset
      'WR_DATA'            : 0x0001,
      'MASK_VALUE'         : 0x0000,
      'NUM_LOCS'           : 0,
      'timeout'            : 120,
   },
   'disable': {
      'test_num'           : 11,
      'prm_name'           : 'masterHeatDisable',
      'spc_id'             : 1,
      'CWORD1'             : 0x0400,
      'SYM_OFFSET'         : 222,      #  Symbol Offset
      'WR_DATA'            : 0x0000,
      'MASK_VALUE'         : 0x0000,
      'NUM_LOCS'           : 0,
      'timeout'            : 120,
   },
   'read': {
      'test_num'           : 11,
      'prm_name'           : 'masterHeatRead',
      'spc_id'             : 1,
      'CWORD1'             : 0x0200,
      'SYM_OFFSET'         : 222,      #  Symbol Offset
      'NUM_LOCS'           : 0,
      'timeout'            : 120,
   },
   'saveSAP': {
      'test_num'           : 178,
      'prm_name'           : 'save SAP to FLASH',
      'spc_id'             : 1,
      'CWORD1'             : 0x420,
   },
}

tornWritePrm_11 = {
   #TornWrite protection control parameter
   'enable' : {
      'test_num'           : 11,
      'prm_name'           : 'tornWriteEnable',
      'spc_id'             : 100,
      'CWORD1'             : 0x0400,
      'SYM_OFFSET'         : 468,      #  Symbol Offset
      'WR_DATA'            : 0x0001,
      'MASK_VALUE'         : 0xFFFE,
      'NUM_LOCS'           : 0,
      'timeout'            : 120,
   },
   'disable': {
      'test_num'           : 11,
      'prm_name'           : 'tornWriteDisable',
      'spc_id'             : 100,
      'CWORD1'             : 0x0400,
      'SYM_OFFSET'         : 468,      #  Symbol Offset
      'WR_DATA'            : 0x0000,
      'MASK_VALUE'         : 0xFFFE,
      'NUM_LOCS'           : 0,
      'timeout'            : 120,
   },
   'read': {
      'test_num'           : 11,
      'prm_name'           : 'tornWriteRead',
      'spc_id'             : 100,
      'CWORD1'             : 0x0200,
      'SYM_OFFSET'         : 468,      #  Symbol Offset
      'NUM_LOCS'           : 0,
      'timeout'            : 120,
   },
   'saveSAP': {
      'test_num'           : 178,
      'prm_name'           : 'save SAP to FLASH',
      'spc_id'             : 100,
      'CWORD1'             : 0x420,
   },
}

quietSeekPrm_11 = {        # Quiet seek control parameters
   'enable' : {
      'test_num'           : 11,
      'prm_name'           : 'quietSeekEnable',
      'spc_id'             : 1,
      'CWORD1'             : 0x0400,
      'SYM_OFFSET'         : 239,      #  Symbol Offset
      'WR_DATA'            : 0x0008,
      'MASK_VALUE'         : 0xFFF7,
      'NUM_LOCS'           : 0x0000,
      'timeout'            : 120,
      },
   'disable': {
      'test_num'           : 11,
      'prm_name'           : 'quietSeekDisable',
      'spc_id'             : 1,
      'CWORD1'             : 0x0400,
      'SYM_OFFSET'         : 239,      #  Symbol Offset
      'WR_DATA'            : 0x0000,
      'MASK_VALUE'         : 0xFFF7,
      'NUM_LOCS'           : 0x0000,
      'timeout'            : 120,
      },
   'read': {
      'test_num'           : 11,
      'prm_name'           : 'quietSeekRead',
      'spc_id'             : 1,
      'CWORD1'             : 0x0200,
      'SYM_OFFSET'         : 239,      #  Symbol Offset
      'NUM_LOCS'           : 0x0000,
      'timeout'            : 120,
      },
   "saveSAP": {
      "test_num"              : 178,
      "prm_name"              : "save SAP to FLASH",
      'spc_id'                : 1,
      "CWORD1"                : 0x420,
   },
}

CTPH_172 = {
   }

# Workaround fix for anomalous temperature diode readings, specifically T172, CWORD1 = 17 reporting bad values
tempDiodeMultRtry = {
   'numRetries'                  : 2,        # 2 retries
   'driveTempDiodeRangeLimit'    : 5,        # Set limit in range of values to 5C between successive calls before failing the drive
   }

## PTP coefficient variance limit
allowed_PTP_variance = 10**-7


# pre AFH version 34
# Note to HDM leads, the values below when they refer to clearance/actuation are in Angstroms(not u")
# initial limits are wide-open.
consistencyCheck3rdGenDict = {
   "percentToTrim"               :   12.5,
   "trimmedMean_LSL"             : -100.0,  # Angstroms
   "trimmedMean_USL"             :   30.0,  # Angstroms
   "winStdDev_LSL"               : -100.0,  # Angstroms
   "winStdDev_USL"               :  100.0,  # Angstroms
   "maxClrDelta"                 :   30.0,  # Angstroms; between WRITER_HEATER and READER_HEATER for the HO consistency chk
   "numPointsViolateMaxClrDelta" :      6,
   }

# AFH version 34
# dictionary is by AFH State (1,2, etc.)
consistencyCheck3rdGenDict_2 = {
   1 : {
      "percentToTrim"               :   12.5,
      "trimmedMean_LSL"             : -100.0,  # Angstroms
      "trimmedMean_USL"             :   40.0,  # Angstroms
      "winStdDev_LSL"               : -100.0,  # Angstroms
      "winStdDev_USL"               :  100.0,  # Angstroms
      "maxClrDelta"                 :   40.0,  # Angstroms; between WRITER_HEATER and READER_HEATER for the HO consistency chk
      "numPointsViolateMaxClrDelta" :      6,
      },
   2 : {
      "percentToTrim"               :   12.5,
      "trimmedMean_LSL"             : -100.0,  # Angstroms
      "trimmedMean_USL"             :   30.0,  # Angstroms
      "winStdDev_LSL"               : -100.0,  # Angstroms
      "winStdDev_USL"               :  100.0,  # Angstroms
      "maxClrDelta"                 :   30.0,  # Angstroms; between WRITER_HEATER and READER_HEATER for the HO consistency chk
      "numPointsViolateMaxClrDelta" :      6,
      },
   3 : {
      "percentToTrim"               :   12.5,
      "trimmedMean_LSL"             : -100.0,  # Angstroms
      "trimmedMean_USL"             :   30.0,  # Angstroms
      "winStdDev_LSL"               : -100.0,  # Angstroms
      "winStdDev_USL"               :  100.0,  # Angstroms
      "maxClrDelta"                 :   30.0,  # Angstroms; between WRITER_HEATER and READER_HEATER for the HO consistency chk
      "numPointsViolateMaxClrDelta" :      6,
      },
   4 : {
      "percentToTrim"               :   12.5,
      "trimmedMean_LSL"             : -100.0,  # Angstroms
      "trimmedMean_USL"             :   30.0,  # Angstroms
      "winStdDev_LSL"               : -100.0,  # Angstroms
      "winStdDev_USL"               :  100.0,  # Angstroms
      "maxClrDelta"                 :   30.0,  # Angstroms; between WRITER_HEATER and READER_HEATER for the HO consistency chk
      "numPointsViolateMaxClrDelta" :      6,
      },

   }

min_temp_diff_between_hot_cold = 14

##################### AFH AR settings ##########################


#  New WHIRP/HIRP test 191 parameters
#  Intended for AFH Major version >= 19.
#  Updated to default WIRP on.  MTB  09-APP-2010
prm_191_0002 = {
   'test_num'                 : 191,
   'prm_name'                 : 'AR T191 parameter list',
   'spc_id'                   : 8,
   'timeout':10000,
                                                #
   "CWORD1"                   : (0x0251,),      # Bit defs are in T191_prv.h, but 0x1191 is good for Heater Only and 0x1111 for Write + Heat
   "CWORD2"                   : (0x0003,),      # Set to 0x7000 if "x/o's" or 0x3000 for "0/1's" in production
   "DISCARD_LIMITS"           : (10, 12),
   "HEATER"                   : (60, -12),      # Bit 8 of CWORD1 set says use this heater range, otherwise compute from drive's clearance data
   "MAX_ITERATION"            : 20,             # Number of revs to avg
   'RETRY_LIMIT'              : 3,              # limit internal st(191) retries
   "WIRP_POINT_COUNT"         : (2),
   "THRESHOLD"                : (970),
   "SET_OCLIM"                : (200,)
}

prm_192_base = {
   'test_num'                 : 192,
   'prm_name'                 : 'base T192 parameter list',
   'spc_id'                   : 1920,
   'timeout'                  : 10000,
                                                #
   "CWORD1"                   : (0x0251,),      #
   "CWORD2"                   : (0,),           # Control word- which coeff to be generated
   "HEAD_RANGE"               : (0x0001,),      # both head
   "ZONE"                     : (0x0302,),      # zone spec
   "HEATER"                   : (0, 5),         # used by HO & WPH coeff generation only
   "MAX_ITERATION"            : 10,             # Number of revs to avg
   'RETRY_LIMIT'              : 1,              #
   "WIRP_POINT_COUNT"         : (2),
   "SET_OCLIM"                : (200,),
   "BACKOFF_HTR_DAC"          : 10,
   "DUAL_HEATER_CONTROL":  {                    #
      'ATTRIBUTE': 'HGA_SUPPLIER',
      'DEFAULT'  : 'TDK',
      'RHO'      : (0,0xFF),
      'TDK'      : (0,0),
   },
   "FREQ_STEP"                : (0,1),           # Not include Freq item - default
   "WRITE_CURRENT":  {                          #better to make sure it's same as default value in INIT_RAP
      'ATTRIBUTE': 'HGA_SUPPLIER',
      'DEFAULT'  : 'TDK',
      'RHO'      : (7,),
      'TDK'      : (9,),
   },
   "DAMPING":  {
      'ATTRIBUTE': 'HGA_SUPPLIER',
      'DEFAULT'  : 'TDK',
      'RHO'      : (4,),
      'TDK'      : (7,),
   },
   "DURATION":  {
      'ATTRIBUTE': 'HGA_SUPPLIER',
      'DEFAULT'  : 'TDK',
      'RHO'      : (6,),
      'TDK'      : (6,),
   },
   "WRITE_CUR_LIST"           : (5,8,11,15),    # Used by WPTP only
   "WRITE_DUMP_LIST"          : (1,5,10,15),    # Used by WPTP only
   "WRITE_DUMPDUR_LIST"       : (1,5,10,15)     # Used by WPTP only
}

test178_gammaH = {
   'test_num'              : 178,
   'prm_name'              : 'test178_gammaH',
   'CWORD1'                : 0x2200,
   'CWORD3'                : 0x0070,
   'timeout'               : 1000,
   }

test178_gammaW = {
   'test_num'                 : 178,
   'prm_name'                 : 'test178_gammaW',
   'CWORD1'                   : (0x2200,),
   'CWORD3'                   : (0x0380,),
   'timeout'                  : 1000,
}


test178_scale_offset = {
   'test_num'              : 178,
   'prm_name'              : 'test178_scale_offset',
   'CWORD1'                : 0x2200,
   'CWORD3'                : 0x0003,
   'timeout'               : 1000,
   }

test178_enableReaderHeater = {
   'test_num'              : 178,
   'prm_name'              : 'test178_enableReaderHeater',
   'CWORD1'                : 0x2200,
   'CWORD3'                : 0x0000,
   'C_ARRAY1'              : [0,4,0,0,0,0,0,0,0,1],         # 4 means set the active reader element
                                                            # 1 means set the reader heater to be active element, to clear 0=writer heater
   'timeout'               : 1000,
   'HEAD_RANGE'            : 1,
   }

test178_disableReaderHeater = {
   'test_num'              : 178,
   'prm_name'              : 'test178_disableReaderHeater',
   'CWORD1'                : 0x2200,
   'CWORD3'                : 0x0000,
   'C_ARRAY1'              : [0,4,0,0,0,0,0,0,0,0],         # 4 means set the active reader element
                                                            # 1 means set the reader heater to be active element, to clear 0=writer heater
   'timeout'               : 1000,
   'HEAD_RANGE'            : 1,
   }

test172_displayActiveHeater = {
   'test_num'              : 172,
   'prm_name'              : 'test172_displayActiveHeater',
   'CWORD1'                : 31,
   'C_ARRAY1'              : [0,4,0,0,0,0,0,0,0,0],
   'timeout'               : 1000,
   }

if testSwitch.FE_0147357_341036_AFH_T172_FIX_TRUNK_MERGE_CWORD1_31 == 1:
   test172_displayActiveHeater['CWORD1'] = 33

# Dual Heater

baseT191_WRITER_HEATER={
    'test_num'          : 191,
    'prm_name'          : 'baseT191_WRITER_HEATER',
    'timeout'           : 6000,
#   'spc_id'            : (spcidnum),
    'HEATER'            : (0x003C, -15),
    'ZONE'              : {
      'ATTRIBUTE'    : 'numZones',
      'DEFAULT'      : 24,
      24             : (0x0302),
      31             : (0x0302),
      60             : (0x0304),
      120            : (0x0308),
      150            : (0x030A),
      180            : (0x030C),
      },
    #'ZONE'              : (0x0302),
    'WIRP_POINT_COUNT'  : (2,),
    'CWORD2'            : (0x0003),  #0x2 to close loop
    'HEAD_RANGE'        : (0),
    'THRESHOLD'         : (970,),
    'MAX_ITERATION'     : (30,),
    'RETRY_LIMIT'       : (3,),
    'CWORD1'            : (0x12D1,),
    'DISCARD_LIMITS'    : (20,20),
    'FREQUENCY'         : (100,),
    'DUAL_HEATER_CONTROL' : (0,-1,),
    'HIRP_CURVE_FIT'    : {
      'ATTRIBUTE'    : 'numZones',
      'DEFAULT'      : 24,
      24             : (40,160,-5000,5000,3,1,4,0,0,0),
      31             : (40,160,-5000,5000,3,1,4,0,0,0),
      60             : (40,160,-5000,5000,4,1,4,0,0,0),
      120            : (40,160,-5000,5000,8,1,4,0,0,0),
      150            : (40,160,-5000,5000,10,1,4,0,0,0),
      180            : (40,160,-5000,5000,12,1,4,0,0,0),
      },
}

baseT191_READER_HEATER={
   'test_num'          : 191,
   'prm_name'          : 'baseT191_READER_HEATER',
    'timeout'               : 6000,
#   'spc_id'                : (spcidnum),
    'HEATER'                : (0x003C, -15),
    'ZONE'              : {
      'ATTRIBUTE'    : 'numZones',
      'DEFAULT'      : 24,
      24             : (0x0302),
      31             : (0x0302),
      60             : (0x0304),
      120            : (0x0308),
      150            : (0x030A),
      180            : (0x030C),
      },
    #'ZONE'              : (0x0302),
    'WIRP_POINT_COUNT'      : (2,),
    'CWORD2'                : (0x0003),
    'HEAD_RANGE'            : (0),
    'MAX_ITERATION'         : (30,),
    'THRESHOLD'             : (970,),
    'RETRY_LIMIT'           : (3,),
    'CWORD1'                : (0x12D1,),
    'DISCARD_LIMITS'        : (10,12),
    'FREQUENCY'             : (100,),
    'DUAL_HEATER_CONTROL'   : (1,-1,),
    'HIRP_CURVE_FIT'    : {
      'ATTRIBUTE'    : 'numZones',
      'DEFAULT'      : 24,
      24             : (40,160,-5000,5000,3,1,4,0,0,0),
      31             : (40,160,-5000,5000,3,1,4,0,0,0),
      60             : (40,160,-5000,5000,4,1,4,0,0,0),
      120            : (40,160,-5000,5000,8,1,4,0,0,0),
      150            : (40,160,-5000,5000,10,1,4,0,0,0),
      180            : (40,160,-5000,5000,12,1,4,0,0,0),
      },
}



##################### end of AFH AR settings ##########################


##################### FAFH settings ##########################


fafhFrequencyCalibrationParams_074_01 = {
   'ATTRIBUTE'       : 'FE_0170290_357257_FAFH_PROCESS_SUPPORT_REFACTOR',
   'DEFAULT'         : '0',
   '0'               : {
      'test_num'        : 74,
      'prm_name'        : 'FAFH_074_frequency_calibration',
      'HEAD_RANGE'      : 0x00FF,
      'CWORD3'          : 0x3020,     # Low nibble selects op (0 = Cal Freq) | 0x0020 = Write RAP to Flash (& reset)
      'ZONE'            : 0x0007,     # Bits 0, 1, 2 = Calibrate Freq in Test Serpent at OD, ID, MD, respectively
      'timeout'         : 30000,
      'SET_OCLIM'       : 200,
   },
   '1'               : {
      'test_num'        : 74,
      'prm_name'        : 'FAFH_074_frequency_calibration',
      'HEAD_RANGE'      : 0x00FF,
      'CWORD1'          : 0x3020,     # This must be CWORD1 instead of CWORD3 if the SF3 refactoring flag is set
      'ZONE'            : 0x0007,     # Bits 0, 1, 2 = Calibrate Freq in Test Serpent at OD, ID, MD, respectively
      'timeout'         : 30000,
      'SET_OCLIM'       : 200,
   }
}

fafhTrackPrepParams_074_02 = {
   'ATTRIBUTE'       : 'FE_0170290_357257_FAFH_PROCESS_SUPPORT_REFACTOR',
   'DEFAULT'         : '0',
   '0'               : {
      'test_num'        : 74,
      'prm_name'        : 'FAFH_074_TrackPrep',
      'HEAD_RANGE'      : 0x00FF,
      'CWORD3'          : 0x3001,     # Low nibble selects op (1 = Prep Test Tracks)
      'ZONE'            : 0x0007,     # Bits 0, 1, 2 = Calibrate Freq in Test Serpent at OD, ID, MD, respectively
      'timeout'         : 30000,
      'SET_OCLIM'       : 50,
   },
   '1'               : {
      'test_num'        : 74,
      'prm_name'        : 'FAFH_074_TrackPrep',
      'HEAD_RANGE'      : 0x00FF,
      'CWORD1'          : 0x3011,     # This must be CWORD1 instead of CWORD3 if the SF3 refactoring flag is set
      'ZONE'            : 0x0007,     # Bits 0, 1, 2 = Calibrate Freq in Test Serpent at OD, ID, MD, respectively
      'timeout'         : 30000,
      'SET_OCLIM'       : 50,
   }
}

fafhAR_measurementParams_074_03 = {
   'ATTRIBUTE'       : 'FE_0170290_357257_FAFH_PROCESS_SUPPORT_REFACTOR',
   'DEFAULT'         : '0',
   '0'               : {
      'test_num'        : 74,
      'prm_name'        : 'FAFH_074_AR_measurement',
      'HEAD_RANGE'      : 0x00FF,
      'CWORD3'          : 0x3012,     # Low nibble selects op (2 = Make AR Measurement)
      'ZONE'            : 0x0007,     # Bits 0, 1, 2 = Calibrate Freq in Test Serpent at OD, ID, MD, respectively
      'timeout'         : 30000,
   },
   '1'               : {
      'test_num'        : 74,
      'prm_name'        : 'FAFH_074_AR_measurement',
      'HEAD_RANGE'      : 0x00FF,
      'CWORD1'          : 0x3012,     # This must be CWORD1 instead of CWORD3 if the SF3 refactoring flag is set
      'ZONE'            : 0x0007,     # Bits 0, 1, 2 = Calibrate Freq in Test Serpent at OD, ID, MD, respectively
      'timeout'         : 30000,
   }
}


fafhAR_displayCoefficientsParams_074_04 = {
   'ATTRIBUTE'       : 'FE_0170290_357257_FAFH_PROCESS_SUPPORT_REFACTOR',
   'DEFAULT'         : '0',
   '0'               : {
      'test_num'        : 74,
      'prm_name'        : 'FAFH_074_AR_displayCoefficients',
      'HEAD_RANGE'      : 0x00FF,
      'CWORD3'          : 0x3014,     # Low nibble selects op (4 = Calc AR/T Coeffs)
      'ZONE'            : 0x0007, # Bits 0, 1, 2 = Calibrate Freq in Test Serpent at OD, ID, MD, respectively
      'timeout'         : 30000,
   },
   '1'               : {
      'test_num'        : 74,
      'prm_name'        : 'FAFH_074_AR_displayCoefficients',
      'HEAD_RANGE'      : 0x00FF,
      'CWORD1'          : 0x3014,     # This must be CWORD1 instead of CWORD3 if the SF3 refactoring flag is set
      'ZONE'            : 0x0007, # Bits 0, 1, 2 = Calibrate Freq in Test Serpent at OD, ID, MD, respectively
      'timeout'         : 30000,
   },
}

fafhInitializeReferenceTrackCorrespondingHIRP_values_074_05 = {
   'ATTRIBUTE'       : 'FE_0170290_357257_FAFH_PROCESS_SUPPORT_REFACTOR',
   'DEFAULT'         : '0',
   '0'               : {
      'test_num'        : 74,
      'prm_name'        : 'fafhInitializeReferenceTrackCorrespondingHIRP_values_074_05',
      'CWORD3'          : 12,
      'timeout'         : 100,
   },
   '1'               : {
      'test_num'        : 74,
      'prm_name'        : 'fafhInitializeReferenceTrackCorrespondingHIRP_values_074_05',
      'CWORD1'          : 12, # This must be CWORD1 instead of CWORD3 if the SF3 refactoring flag is set
      'timeout'         : 100,
   },
}

prm_display_fafh_parm_file_074_06 = {
   'ATTRIBUTE'       : 'FE_0170290_357257_FAFH_PROCESS_SUPPORT_REFACTOR',
   'DEFAULT'         : '0',
   '0'               : {
      'test_num'        : 74,
      'prm_name'        : 'prm_display_fafh_parm_file_074_06',
      'HEAD_RANGE'      : 0x00FF,
      'CWORD3'          : 0x8,     # Low nibble selects op (4 = Calc AR/T Coeffs)
      'ZONE'            : 0x0007, # Bits 0, 1, 2 = Calibrate Freq in Test Serpent at OD, ID, MD, respectively
      'timeout'         : 30000,
   },
   '1'               : {
      'test_num'        : 74,
      'prm_name'        : 'prm_display_fafh_parm_file_074_06',
      'HEAD_RANGE'      : 0x00FF,
      'CWORD1'          : 0x8,     # This must be CWORD1 instead of CWORD3 if the SF3 refactoring flag is set
      'ZONE'            : 0x0007, # Bits 0, 1, 2 = Calibrate Freq in Test Serpent at OD, ID, MD, respectively
      'timeout'         : 30000,
   },
}

prm_init_fafh_param_file_074_07 = {
   'ATTRIBUTE'       : 'FE_0170290_357257_FAFH_PROCESS_SUPPORT_REFACTOR',
   'DEFAULT'         : '0',
   '0'               : {
      'test_num'        : 74,
      'prm_name'        : 'prm_init_fafh_param_file',
      'HEAD_RANGE'      : 0x00FF,
      'CWORD3'          : 0x5,     # Low nibble selects op (4 = Calc AR/T Coeffs)
      'ZONE'            : 0x0007, # Bits 0, 1, 2 = Calibrate Freq in Test Serpent at OD, ID, MD, respectively
      'timeout'         : 30000,
   },
   '1'               : {
      'test_num'        : 74,
      'prm_name'        : 'prm_init_fafh_param_file',
      'HEAD_RANGE'      : 0x00FF,
      'CWORD1'          : 0x5,     # This must be CWORD1 instead of CWORD3 if the SF3 refactoring flag is set
      'ZONE'            : 0x0007, # Bits 0, 1, 2 = Calibrate Freq in Test Serpent at OD, ID, MD, respectively
      'timeout'         : 30000,
   },
}

prm_write_fafh_param_file_074_08 = {
   'ATTRIBUTE'       : 'FE_0170290_357257_FAFH_PROCESS_SUPPORT_REFACTOR',
   'DEFAULT'         : '0',
   '0'               : {
      'test_num'        : 74,
      'prm_name'        : 'prm_write_fafh_param_file',
      'HEAD_RANGE'      : 0x00FF,
      'CWORD3'          : 0x6,     # Low nibble selects op (4 = Calc AR/T Coeffs)
      'ZONE'            : 0x0007, # Bits 0, 1, 2 = Calibrate Freq in Test Serpent at OD, ID, MD, respectively
      'timeout'         : 30000,
   },
   '1'               : {
      'test_num'        : 74,
      'prm_name'        : 'prm_write_fafh_param_file',
      'HEAD_RANGE'      : 0x00FF,
      'CWORD1'          : 0x6,     # This must be CWORD1 instead of CWORD3 if the SF3 refactoring flag is set
      'ZONE'            : 0x0007, # Bits 0, 1, 2 = Calibrate Freq in Test Serpent at OD, ID, MD, respectively
      'timeout'         : 30000,
   },
}


##################### end of FAFH settings ##########################

##################### VBAR SECTION ####################################

# BPI Nominal Settings
WPForVBPINominalMeasurements = 2
VBPINominalCapabilities = (0.75, 0.96, 1.04, 1.30)
VBPINominalFormats      = (0.80, 1.00, 1.00, 1.20)
TG_Coef = 2
# TPI Margin Target for VBAR-HMS Constant Margin Testing.
# Available knobs based on desired usage of Constant Margin Testing.
# Constant TPI Margin Testing is enabled by setting the ADJUST_TPI_FOR_CONSTANT_MARGIN in Test_Switches.py
VTPIConstantMarginTarget = 0   # Example: -0.02 implies -2.0 percent margin.
# Constant HMS Margin Testing is enabled by setting the ADJUST_HMS_FOR_CONSTANT_MARGIN in Test_Switches.py
VHMSConstantMarginTarget = 0   # Example: 3.0 implies 3.0 nanometers.

TPI_MAX = 1.4
BPI_MAX = 1.3
TPI_MIN = 0.6
BPI_MIN = 0.6
VBAR_ZONE_POS = 198
WCSAT_BPIMARGIN = 0.057
WC_CAP_MIN = 0
MR_BIAS_BACKOFF_ZONE = 1

TpiMarginVerify_211 = {
   'test_num'           : 211,
   'prm_name'           : 'TpiMarginVerify_211',
   'timeout'            : 6*600,
   'NUM_TRACKS_PER_ZONE': 6,
   'NUM_SQZ_WRITES'     : 6,
   'ZONE_POSITION'      : 1,
   'ADJ_BPI_FOR_TPI'    : 0, # According to the algorithm, we need to use BPI capability minus the BPI margin to test TPI capability
   'CWORD1'             : 0x0026,
   'SET_OCLIM'          : 1228,
   'TARGET_SER'         : 5,
   'TLEVEL'             : 7,
   'START_OT_FOR_TPI'  : 34,
}

# Alternate MeasureHMS_211 dictionary that will override MeasureHMS_211 for the CVbarHMS2 class, if implemented.
AltMeasureHMS_211 = {
}

MeasureBPITPI_WP_211 = {
   'prm_name'        : 'MeasureBPITPI_WP_211',
   'CWORD1'          : 0x0037,
}

MeasureBPITPI_ZN_211 = {
   'prm_name'        : 'MeasureBPITPI_ZN_211',
   'CWORD1'          : 0x0027,
}

# VBAR Settling Settings
VbarSettlingParms = {
   'calClearances'        : [0,2,4,6,8,10,12,14,16,18],  # Clearance settings used for the calibration routine.
   'dwellClearances'      : [8,0],          # Make sure entries in this list are included in self.deltaClrSettings.
   'numOfCalTestLoops'    : 4,              # Iterations through the calibration measurement routine.
   'numOfSettleTestLoops' : 1,              # Iterations through the settling measurement routine.
   'numOfSettleCycles'    : 1,              # Number of cycles to measure settling at each clearance setting in dwellClearances.
   'dwellTimes'           : [30],           # Amount of time to set with heads on the ramp.
   'hmsPasses'            : 1,              # Number of passes for HMS measurements
   'hmsSqueeze'           : [ 0,],          # Amount of squeeze used in the hms cap measurement routine, for each pass
   'hmsHtrSetting'        : [ 3,],          # Heater settings used in the hms cap measurement routine, for each pass
   'hmsNumSqueeze'        : [ 0,],          # Num Squeeze passed to Test 211 in the hms cap measurement routine, for each pass
   'hmsTlevel'            : [12,],          # T-Level passed to Test 211 in the hms cap measurement routine, for each pass
   'hmsStore'             : [ 1,],          # A list of flags indicating which pass to store
   'hmsMeasurementZones'  : {'ATTRIBUTE' : 'numZones',  # List of zones to run the hmscap measurements in.  Want at least 5
                              17         : [1,3,7,10,15],
                              24         : [1,3,11,16,22],
                              30         : [1,4,15,20,28],
                              60         : [1,8,30,40,58], #(1, 0.13%, 0.5%, 0.67%, numZones-2)
                              120        : [1,16,60,80,118], #(1, 0.13%, 0.5%, 0.67%, numZones-2)
                              150        : [1,20,75,101,148], #(1, 0.13%, 0.5%, 0.67%, numZones-2)
                              180        : [1,23,90,121,178], #(1, 0.13%, 0.5%, 0.67%, numZones-2)
                            },
   'hmsSettlingZones'     : {'ATTRIBUTE' : 'numZones',  # List of zones to run the settling measurements in. sample time issues if you specify more than 2 zones.
                              17         : [1,15],
                              24         : [1,22],
                              30         : [1,28],
                              60         : [1,58],
                              120        : [1,118],
                              150        : [1,148],
                              180        : [1,178],
                            },

}

prm_BPI_211_Nominal = {  # For BPI Nominal
   'test_num'           : 211,
   'prm_name'           : 'MeasureBPINominal_211',
   'HEAD_MASK'          : 0xFF,
   'NUM_TRACKS_PER_ZONE': 6,
   'ZONE_POSITION'      : VBAR_ZONE_POS,
   'BPI_MAX_PUSH_RELAX' : 20,#{'EQUATION' :'TP.VbarBpiMaxPushRelax'},
   'CWORD1'             : 0x0001, #Enable multi-track mode
   'CWORD2'             : 0x0010, #Enable BIE for BPIC
   'SET_OCLIM'          : 1228,
   'RESULTS_RETURNED'   : 0x000F,
   'TLEVEL'             : 0,
   'THRESHOLD'          : 16,
   'TARGET_SER'         : {'EQUATION': 'TP.VbarTargetSER'}, #reference to TestParamter.py
   'timeout'            : 3600,
   'spc_id'             : 0,
}

if testSwitch.M11P_BRING_UP:
   prm_BPI_211_Nominal.update({
         'ZONE_POSITION'      : VBAR_ZONE_POS,
         'CWORD1'             : 0x0015, #Enable multi-track mode
         'CWORD2'             : 0x0010, #Enable BIE for BPIC
         'SET_OCLIM'          : 655,
         'RESULTS_RETURNED'   : 0x000E,
         'BPI_MAX_PUSH_RELAX' : {'EQUATION' : 'TP.VbarBpiMaxPushRelax'},
   })

if testSwitch.HAMR: 
   prm_BPI_211_Nominal.update({'BPI_MAX_PUSH_RELAX' : 50,})

prm_TPI_SIM_211 = {
   'test_num'           : 211,
   'prm_name'           : 'MeasureTPI_211',
   'HEAD_RANGE'         : 0x00FF,
   'NUM_TRACKS_PER_ZONE': 6,
   'NUM_SQZ_WRITES'     : {'EQUATION': 'TP.num_sqz_writes'}, #reference to TestParamter.py
   'ZONE_POSITION'      : VBAR_ZONE_POS,
   'ADJ_BPI_FOR_TPI'    : 0,
   'CWORD1'             : 0x0002,   # TPI Measurement
   'CWORD6'             : 0x0002,   # BPI Adjust from SIM
   'SET_OCLIM'          : 655,
   'TARGET_SER'         : 5,
   'TPI_TARGET_SER'     : 5,
   'RESULTS_RETURNED'   : {
      'ATTRIBUTE': 'T211_TURNOFF_REPORT_OPTIONS_DURING_2DVBAR_TPIC_MEAS',
      'DEFAULT'  : 0,
      0 : 0x0006,
      1 : 0x000F,
    },
   'timeout'            : 3600,
   'spc_id'             : 0,
}

##################### end of VBAR section ##########################

mdw_152 = {
   'test_num'                 : 'NOP',
}
mdw_notches_152 = []

CktSNO_152 = {
   'test_num':152,
   'prm_name':'doBodePrm_152',
   'timeout': 4000,  # per head
   'spc_id':9,
   'CWORD1':(0x0000),  # No CWORD1 Options used
   'CWORD2'          : 4,       # Force SNO if PEAK was not detected.
   'DO_SNO'          : (),
   'SNO_METHOD'      : 1,
   'PLOT_TYPE'       : 1,
   'START_CYL'       : (0, 10000),
   'END_CYL'         : (0, 10000),
   'HEAD_RANGE'      : (0xFFFF),
   'FREQ_RANGE'      : (8184,9512,),      # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'FREQ_INCR'       : (24,),
   'NBR_NOTCHES'     : (1),
   'NBR_TFA_SAMPS'   : 14, #was 2000
   'NBR_MEAS_REPS'   : 3,
   'INJ_AMPL'        : 70,
   'GAIN_LIMIT'      : -200, # previously set to +90, -60 will ensure new notch settings get made.  #"GAIN_LIMIT": 0xFFC4,
   'NUM_SAMPLES'     : 10, # Only needed when SNO_METHOD = 5, peak normalization w/0 SNO

   'ZETA_1'          : (int(0.020*1000), int(0.03*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_2'          : (int(0.030*1000), int(0.09*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_3'          : (int(0.050*1000), int(0.12*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_4'          : (int(0.080*1000), int(0.16*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_5'          : (int(0.040*1000), int(0.18*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_6'          : (int(0.280*1000), int(0.64*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary

   'PEAK_WIDTH'      : 10,
   'PTS_UNDR_PK'     : 3,
   'SHARP_THRESH'    : 0, # changed from 5 to 0
   'PEAK_GAIN_MIN'   : -200,    #
   'PEAK_SUMMARY'    : 2,
   'NOTCH_CONFIG'    : 0, # Configure each notch independently
   'NOTCH_TABLE'     : 0, #VCM
}

CktNotches_152 = [
         {
	'FILTERS': 2**5,
	'FREQ_RANGE': (10300,11400,),
	'FREQ_INCR': 24,
	 #ZETA  : (W1),(D1)
	"ZETA_6": (int(0.28*1000),int(0.64*100)),
    'HEAD_RANGE'      : (0xFFFF),
    'NBR_NOTCHES'     : (1),
    'BANDWIDTH'       : (750),
    'NOTCH_DEPTH'     : (1300),
    'FREQ_OFFSET'     : (50),      # Add Freq for Notch Zeta config
         },
]

sno_phase_peak_detect_152 = {
   'test_num':152,
   'prm_name':'doSNOPhasePrm_152',
   'timeout': 4000,  # per head
   'spc_id':10,
   'CWORD1':(0x0000),  # No CWORD1 Options used
   'CWORD2'          : 20,       # Force SNO if PEAK was not detected and set SNO Phase Detection.
   'DO_SNO'          : (),
   'MEASURE_PHASE'   : (),
   'SNO_METHOD'      : 6,
   'PLOT_TYPE'       : 6,
   'START_CYL'       : (0, 10000),
   'END_CYL'         : (0, 10000),
   'HEAD_RANGE'      : (0),
   'FREQ_RANGE'      : (2000,3000,),      # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'FREQ_INCR'       : (24,),             # change from 24 to 10 (3rd May 2013)
   'NBR_NOTCHES'     : (1),
   'NBR_TFA_SAMPS'   : 14, #was 2000
   'NBR_MEAS_REPS'   : 3,
   'INJ_AMPL'        : 70,
   'PHASE_LIMIT'     : -1000, # for detecting the min phase value
   'NUM_SAMPLES'     : 10, # Only needed when SNO_METHOD = 5, peak normalization w/0 SNO

   'ZETA_1'          : (int(0.020*1000), int(0.03*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_2'          : (int(0.030*1000), int(0.09*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_3'          : (int(0.050*1000), int(0.12*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_4'          : (int(0.080*1000), int(0.16*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_5'          : (int(0.040*1000), int(0.18*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_6'          : (int(0.280*1000), int(0.64*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary

   'PEAK_WIDTH'      : 10,
   'PTS_UNDR_PK'     : 3,
   'SHARP_THRESH'    : 0, # changed from 5 to 0
   'PEAK_SUMMARY'    : 2,
   'NOTCH_CONFIG'    : 0, # Configure each notch independently
   'NOTCH_TABLE'     : 0, #VCM
}

CktNotchesPD_152 = [
         {
	'FILTERS': 2**5,
	'FREQ_RANGE': (2000,3000,),
	'FREQ_INCR': 24,                         # change from 24 to 10 (3rd May 2013)
	 #ZETA  : (W1),(D1)
	"ZETA_6": (int(0.28*1000),int(0.64*100)),
    'HEAD_RANGE'      : (0),
    'NBR_NOTCHES'     : (1),
    'BANDWIDTH'       : (750),
    'NOTCH_DEPTH'     : (1300),
    'FREQ_OFFSET'     : (50),      # Add Freq for Notch Zeta config
         },
]

SNO_PHASE_DELTA_LIMIT = -35        # change limit from 30 to 33 deg phase loss (3rd May 2013)

STE_Prm_213 = {
   #AAB: Modified per Schaff's params
   'prm_name'                : 'STE_Prm_213',
   'test_num'                : 213,
   'timeout'                 : 195000,  # 16 hours->which maps to test time of abut 8 hours.
   'spc_id'                  : 200,
   "HEAD_RANGE"              : (0x00FF,),
   "ZONE_POSITION"           : (1,),            # zone position set to 90%
   "TEST_CYL"                : (0xFFFF,0xFFFF,),  # set this to all FFFF if using zone masks
   "CWORD1"                  : (0xC121),
   "CWORD2"                  : (0x3407),
   "NBR_MEAS_REPS"           : (1,),       # number of times to do STE writes / measure per-track BER
   "THRESHOLD"               : (194,),     # maximum allowed BASELINE_BER obtained prior to erasure, 390 corresponds to max BER of -3.9 decades.
   "NUM_TRACKS_PER_ZONE"     : (20,),      # number of tracks on either side of the center track to write
   "TARGET_TRK_WRITES"       : (40,),      # 47=50K, number of center track STE writes, xx translates to 10^(x.x), 50 is 100K
   "NUM_SQZ_WRITES"          : (1,),       # number of writes when writing per-track data
   "NUM_ADJ_ERASE"           : (5,),
   "OFFSET_SETTING"          : (0,0,1,),
   "READ_OFFSET"             : (0x0000,),
   "S_OFFSET"                : (1,),
   "PATTERNS"                : (0x80,0x01,0x00,),
   "AC_ERASE"                : (),
   "BITS_TO_READ"            : (0x0107,),  # in all cases pass at least 10e7 bits, more will be required if BER is better than -6.5 but then ERRORS_TO_READ min kicks in so more bits are passed
   "ERRORS_TO_READ"          : (50,),      # keep passing bits til this minimum number of errors is read, 0 = disable
   "TLEVEL"                  : (0,),       # ECC error code correction level
   "STE_MAX_ERASURE_SPEC"    : (500,),     # maximum allowed BER loss due to STE, 150 = 1.50 decades of BER loss
   "BER_LIMIT"               : (400,),     # BER_AFTER_STE_SPEC, maximum allowed BER after STE, 400 = -4.00
   "DAMPING_OFFSET"          : (1,1),      # value of 3 is the minimum allowed osa, if default is 3 or less then no osa backoff occurs.
   "DATA_SET1"               : (0,15,30,0),  #DOS_STE ranges that trigger different thresholds
   "DATA_SET2"               : (1,2,3,0),     #DOS_ATI values that get written to RAP (currently not enabled)
   "DATA_SET3"               : (4,8,12,0),  #DOS_STE ranges that trigger different thresholds
   "DATA_SET4"               : (0,1,2,3),     #DOS_STE values that get written to RAP.
   'MAX_RADIUS'              : 1195,
   'MAX_ATI_ERR_RATE_SPEC'   : (194,),
   'MIN_ERR_RATE'            : 200,
   'ZONE_MASK'               : (0, 1),
   'NUM_GROUPS_LIMIT'        : (5,),
   'LOG10_BER_SPEC'          : (170,),
   'PAD_SIZE'                : 61184,      # Not used.  I'd delete, but don't want to cause a PF3 binary change
   'GAP_SIZE'                : 188,        # Not used.  I'd delete, but don't want to cause a PF3 binary change
   'FREQUENCY'               : 210,        # Not used.  I'd delete, but don't want to cause a PF3 binary change
   'ZONE_MASK_EXT'           : (0, 2),     # Not used.  I'd delete, but don't want to cause a PF3 binary change
   "MIN_MAX_WRT_CUR"         : (0x05,0xFF,),  # VERY IMPORTANT! Test will use unitialized values to set channel registers
                                         #    if Iw_max is not set to 0xff.  5 is the minimum allowed Iw DAC setting.
}

prm_mergeG_to_P = {
    'RADIAL_PAD_CYLS'             : 4,
    'S_WEDGE_DEFECT_PAD'          : 2,
    'M_WEDGE_DEFECT_PAD'          : 4,
    }

prm_056_uAct_Dual_Stage = {
   'test_num'     : 56,
   'prm_name'     : 'prm_056_uAct_Dual_Stage',
   'timeout'      : 600,
   'MINIMUM'      : 4096,
   'spc_id'       : 1,
   'LOOP_CNT'     : 10,
   'MAXIMUM'      : 12288,
   'CWORD1'       : 0x5022
}

prm_DS_SensitivityScoring_288 = {
   'test_num'     : 288,
   'prm_name'     : 'prm_DS_SensitivityScoring_288',
   'timeout'      : 3000,
   'spc_id'       : 1,
   'CWORD1'       : 0xD000,
   'CWORD3'       : 0x2006,         # DS OL bode, with sensitivity transform, and magnitude limit checking (via binary limit file)
   'START_CYL'    : (0, 0x0666),    # 5% of max cyl, as a Q15 value
   'END_CYL'      : (0, 0x0666),    # 5% of max cyl, as a Q15 value
   'dlfile'       : ('UndefinedPath','UndefinedFile'),      # This MUST be replaced with the actual file location and name before calling the test
}

prm_VCM_SensitivityScoring_288 = {
   'test_num'     : 288,
   'prm_name'     : 'prm_VCM_SensitivityScoring_288',
   'timeout'      : 2000,
   'spc_id'       : 1,
   'CWORD1'       : 0xD000,
   'CWORD3'       : 0x0806,         # VCM OL bode, with sensitivity transform, and magnitude limit checking (via binary limit file)
   'START_CYL'    : (0, 0x0666),    # 5% of max cyl, as a Q15 value
   'END_CYL'      : (0, 0x0666),    # 5% of max cyl, as a Q15 value
   'dlfile'       : ('UndefinedPath','UndefinedFile'),      # This MUST be replaced with the actual file location and name before calling the test
}

prm_DS_SensitivityScoring_282 = {
   'test_num'     : 282,
   'prm_name'     : 'prm_DS_SensitivityScoring_282',
   'timeout'      : 5000,
   'spc_id'       : 1,
   'CWORD1'       : 0x0086,         # DS OL bode, translate to sensitivity, and compare against binary limit file
   'dlfile'       : ('UndefinedPath','UndefinedFile'),      # This MUST be replaced with the actual file location and name before calling the test
}

prm_VCM_SensitivityScoring_282 = {
   'test_num'     : 282,
   'prm_name'     : 'prm_VCM_SensitivityScoring_282',
   'timeout'      : 3000,
   'spc_id'       : 1,
   'CWORD1'       : 0x0026,         # VCM OL bode, translate to sensitivity, and compare against binary limit file
   'dlfile'       : ('UndefinedPath','UndefinedFile'),      # This MUST be replaced with the actual file location and name before calling the test
}

# The following parameter sets (doBodeSNO_282, snoNotches_282_VCM, snoNotches_282_DAC, and snoNotches_282)
# are "place holders" that must be overridden by ServoTestParameters.py.  These parameter sets are intended
# to cause T282 failures if executed without overriding anything (to ensure that SNO is run with valid
# Servo supplied parameters).
doBodeSNO_282 = {
      'test_num'              : 282,
      'prm_name'              : 'doBodeSNO_282',
      'timeout'               : 100,
      'CWORD1'                : 0x00F8,
      'HEAD_RANGE'            : 0x0000,
      'dlfile'                : ('UndefinedPath', 'UndefinedFile'),
   }

snoNotches_282_VCM = [
      {
         'NOTCH_TABLE'        : 0,
      },
	]

snoNotches_282_DAC = [
      {
         'NOTCH_TABLE'        : 2,
      },
	]

snoNotches_282 = [
      {
         'NOTCH_TABLE'        : 0,
      },
	]

prm_198_servoFIR = {
   'test_num':198,
   'prm_name':'prm_198_servoFIR',
   'timeout':14400,
   'spc_id':2,
   "CWORD1" : (0x4000,),   # tune
   "RETRY_LIMIT" : (8,),
   "REVS" : (10,),
   "MARGIN_LIMIT" : (0x0A14,),
   }

prm_054_PressureSensorCal = {
   'test_num'     : 54,
   'prm_name'     : 'prm_054_PressureSensorCal',
   'timeout'      : 60,
   'spc_id'       : 1,
   #'LIMIT32'      : (600, 10),
   'NUM_SAMPLES'  : 10,
   'REF_ADC'      : 303,            #248 at 5k ft, 303 at sealevel
   'CWORD1'       : 0x0001
   }

prm_084_RandomSeeks= {
   'test_num'     : 84,
   'prm_name'     : 'prm_084_RandomSeeks',
   'timeout'      : 300,   # Should be at least 5 seconds more than LOOP_CNT * SEEK_TIME_LIMIT
   'spc_id'       : 1,
   'TEST_HEAD'    : 0,
   'LOOP_CNT'     : 10,    # Loop 10 times ...
   'SEEK_TIME_LIMIT' : 5,  #  ... 5 Seconds each random seek sequence
   'CWORD1'       : 0x0000
}

tempSaturation_maxWaitTime = 6000 #in min

tempSaturation_DifferentialReq = {
   #How close a drive temp must be to the cell temp
   'SCOPY'                 : -1,
   'STS'                   : -1,
   'PRE2'                  : -1,
   'CAL2'                  : 8,
   'FNC2'                  : 8,
   'SPSC2'                 : 8,
   'SDAT2'                 : -1,
   'CRT2'                  : -1,
   'CMT2'                  : 10,
   'FIN2'                  : 10,
   'IOSC2'                 : 10,
   'AUD2'                  : 10,
   'CUT2'                  : 10,
   'CCV2'                  : 10,
   }

heatHDA_Seeks_prm = {
   'test_num'              : 30,
   'prm_name'              : 'SF3 random seeks to heat HDA',
   'spc_id'                : 1,
   'CWORD1'                : 0x0314, #random target random heads read seek
   'TIME'                  : (0, 0xffff, 0xffff),
   'PASSES'                : 0x9C0, #~30 seconds if seek time is 12ms
   'SEEK_DELAY'            : 1,
   'BIT_MASK'              : (0, 0),
   'START_CYL'             : (0, 0),
   'END_CYL'               : (0x1, 0),
   'timeout'               : 500,
   }

ChannelDieTempPrm_172 = {
   'test_num'              : 172,
   'prm_name'              : 'SoC Die Temperature reported by Channel',
   'spc_id'                : 1,
   'CWORD1'                : 35,
   'timeout'               : 200,
   }

prm_MeasureHumidity_235 = {
   'test_num'            : 235,
   'prm_name'            : 'prm_MeasureHumidity_235',
   'timeout'             : 300,
   'spc_id'              : 1,
   "TEMPERATURE_COEF"    : ( 90, 0 ),
   "RELHUMIDITY_COEF"    : ( 70, 0 ),
   "DELAY_TIME"          : 10,
   "RETRY_LIMIT"         : 1
}

prm_MeasureAndSaveHumidity_235 = prm_MeasureHumidity_235.copy()
prm_MeasureAndSaveHumidity_235["CWORD1"] = 0x0100
prm_MeasureAndSaveHumidity_235["prm_name"] = "prm_MeasureAndSaveHumidity_235"

# Ordered list of keys which correspond to modifications of the humidity coefficients specified in AFH_coeffs_<program>.py
#  These modificiations will be applied on the table before sending to T178
hcsParamModificationOptions = ['abs(%s)',       # take the absolute value of the coeff
                               '%s * 1000',     # multiply it by 1000
                               'int(%s)',       # cast to int
                               ]

prm_afhSetHCSCoefficient_178 = {
     'test_num'            : 178,
     'prm_name'            : 'prm_afhSetHCSCoefficient_178',
     'timeout'             : 1000,
     "CWORD1"              : 0x200,
     "CWORD4"              : 0x10,
}

prm_afhSetHCSCoefficientAndSaveToRAP_178 = {
     'test_num'            : 178,
     'prm_name'            : 'prm_afhSetHCSCoefficientAndSaveToRAP_178',
     'timeout'             : 1000,
     "CWORD1"              : 0x220,
     "CWORD4"              : 0x10,
}

prm_outputHCSCoefficientsAndTCSAdders_172 = {
     'test_num'            : 172,
     'prm_name'            : 'prm_outputHCSCoefficientsAndTCSAdders_172',
     'timeout'             : 1000,
     "CWORD1"              : 38,
}

prm_outputHCSAndTCSAdderEnabledBits_172 = {
     'test_num'            : 172,
     'prm_name'            : 'prm_outputHCSAndTCSAdderEnabledBits_172',
     'timeout'             : 1000,
     "CWORD1"              : 37,
}

prm_afhSetTCSAdder_178 = {
     'test_num'            : 178,
     'prm_name'            : 'prm_afhSetTCSAdder_178',
     'timeout'             : 1000,
     "CWORD1"              : 0x200,
     "CWORD4"              : 0x20,
}

prm_afhSetTCSAdderAndSaveToRAP_178 = {
     'test_num'            : 178,
     'prm_name'            : 'prm_afhSetTCSAdderAndSaveToRAP_178',
     'timeout'             : 1000,
     "CWORD1"              : 0x220,
     "CWORD4"              : 0x20,
}

prm_enableTCSAdderBit_178 = {
     'test_num'            : 178,
     'prm_name'            : 'prm_enableTCSAdderBit_178',
     'timeout'             : 1000,
     "CWORD1"              : 0x220,
     "MR_OP_MODE"          : 0x8004,
}

prm_disableTCSAdderBit_178 = {
     'test_num'            : 178,
     'prm_name'            : 'prm_disableTCSAdderBit_178',
     'timeout'             : 1000,
     "CWORD1"              : 0x220,
     "MR_OP_MODE"          : 0x4,
}

prm_enableHumiditySensorBit_178 = {
     'test_num'            : 178,
     'prm_name'            : 'prm_enableHumiditySensorBit_178',
     'timeout'             : 1000,
     "CWORD1"              : 0x220,
     "MR_OP_MODE"          : 0x8001,
}

prm_disableHumiditySensorBit_178 = {
     'test_num'            : 178,
     'prm_name'            : 'prm_disableHumiditySensorBit_178',
     'timeout'             : 1000,
     "CWORD1"              : 0x220,
     "MR_OP_MODE"          : 0x1,
}

tcs_adder_scaler = 1000000    # corresponds with TCS_ADDER_SCALER in t178_prv.h
tcs_adder_sign_multiplier = 1 # controls whether or not the tcs_adders are multiplied by 1 or -1
prm_setTRise_178 = {
     'test_num'            : 178,
     'prm_name'            : 'prm_RAPTRiseValue_178',
     'timeout'             : 1000,
     "CWORD1"              : 0x200,
     "CWORD4"              : 0x40,
}

prm_setTRiseAndSaveToRAP_178 = {
     'test_num'            : 178,
     'prm_name'            : 'prm_setTRiseAndSaveToRAP_178',
     'timeout'             : 1000,
     "CWORD1"              : 0x220,
     "CWORD4"              : 0x40,
}
TRiseValueModificationOptions = []

prm_outputTRiseValuesByHeadByZone_172 = {
     'test_num'            : 172,
     'prm_name'            : 'prm_outputTRiseValuesByHeadByZone_172',
     'timeout'             : 1000,
     "CWORD1"              : 43,
}

### Short Process Configuration ###
# Populate each operation below with a list of desired states to run, all others will be bypassed
# The config var will choose one of the lists described below for that operation
# i.e. PIM.modConfigVars("shortProcess", "{'FNC2': '1'}")
# "baseline" process is for quickly setting up drives in the automated system.
shortProcessOptions = {
   'PRE2': {
      'baseline':
         ['INIT', 'END_TEST', 'FAIL_PROC', 'COMPLETE'],
      '1':
         ['INIT', 'DNLD_CODE', 'SETUP_PROC', 'HEAD_CAL', 'MDW_CAL',
                  'SVO_TUNE', 'PARTICLE_SWP', 'PES_SCRN', 'INIT_RAP', 'SERVO_OPTI',
                  'AFH1', 'CAL_MR_RES', 'AGC_JOG', 'RW_GAP_CAL', 'HIRP1A',
                  'INIT_SYS', 'END_TEST', 'FAIL_PROC', 'COMPLETE']},
   'CAL2': {
      'baseline':
         ['INIT', 'END_TEST', 'FAIL_PROC', 'COMPLETE'],
      '1':
         ['INIT','VER_SYS', 'VBAR_ZAP', 'VBAR_WP1', 'TARG_COPY', 'AFH2',
                  'RESTART_VBAR', 'PV_RW_GAP_CAL1', 'VBAR_WP2_ZAP', 'VBAR_WP2',
                  'PREP_RERUN_AFH2', 'AFH2B', 'LIN_SCREEN2', 'GMR_RES_4', 'HEATER_RES2',
                  'GMR_RES_5', 'OPTI_ZAP', 'READ_OPTI', 'FINE_OPTI1', 'VBAR_HMS_ZAP',
                  'RSSDAT0', 'VBAR_HMS', 'VBAR_HMS1', 'VBAR_CLR', 'VBAR_HMS2', 'RSSDAT1',
                  'RSSDAT2_ZAP', 'RSSDAT2', 'DISABLE_ZAP', 'PV_RW_GAP_CAL2', 'STATIC_OPTI',
                  'FINE_OPTI', 'SWD_CAL', 'SWD_VER', 'WRT_SIM_FILES2', 'VER_SYS2', 'DISP_CHAN',
                  'GMR_RES_6', 'STE_ATI', 'END_TEST', 'FAIL_PROC', 'COMPLETE']},
   'FNC2': {
      'baseline':
         ['INIT', 'END_TEST', 'FAIL_PROC', 'COMPLETE'],
      '1':
         ['INIT', 'INIT_DRV_INFO', 'READ_SCRN', 'INIT_FS',
                  'LUL_TEST25', 'LUL_TEST97', 'WRITE_SCRN', 'PES_INSTAB', 'END_TEST',
                  'FAIL_PROC', 'COMPLETE'],
      '2':
         ['INIT', 'INIT_DRV_INFO', 'A_FLAWSCAN', 'DGTL_FLWSCN',
                  'END_TEST', 'FAIL_PROC', 'COMPLETE']},
}

Bode_Scrn_Audit =  {
      'PN'        : ['9YN166'],
      'SN_sampler': '0123456789ABCDEFGH'
   }

prm_638 = {
   "test_num"   : 538,
   "prm_name"   : "prm_538",
   "PARAMETER_0": 0x2000,
   "FEATURES"   : 0xD0,
   "COMMAND"    : 0xB0,
   "LBA_MID"    : 0x4F,
   "LBA_LOW"    : 0x00,
   "LBA_HIGH"   : 0xC2,
   "SECTOR_COUNT": 0,
   "timeout"    : 2600,
   }

prm_508_Buff= {
   'test_num'               : 508,
   'prm_name'               : "prm_508_Buff",
   'CTRL_WORD1'             : (0x0000),
   'BYTE_OFFSET'            : (0,0),
   'BUFFER_LENGTH'          : (0,1280),
   'PATTERN_TYPE'           : (0),                # 0 = fixed pattern
   'DATA_PATTERN0'          : (0x0000, 0x0000),
   'DATA_PATTERN1'          : (0x0000, 0x0000),
#   'BYTE_PATTERN_LENGTH'    : (32),
}

prm_538={
  "test_num"   : 538,
  "prm_name"   : "prm_538",
  "PARAMETER_0": 0x2000,
  "FEATURES"   : 0xD0,
  "COMMAND"    : 0xB0,
  "LBA_MID"    : 0x4F,
  "LBA_LOW"    : 0x00,
  "LBA_HIGH"   : 0xC2,
  "SECTOR_COUNT": 0,
  "timeout"    : 2600
}

enableWriteCache_538 = {
   'test_num'                 : 538,
   'prm_name'                 : "enableWriteCache_538",
   'FEATURES'                 : 0x02,
   'COMMAND'                  : 0xEF,
   'LBA_MID'                  : 0x0,
   'LBA_LOW'                  : 0x0,
   'LBA_HIGH'                 : 0x0,
   'SECTOR_COUNT'             : 0,
   'timeout'                  : 2600,
}

prm_microsoft = {
   'LOOP'      : 15,
   'TEST_LBAS' : 0x5000,   # 10MB
   # Read operation parameters. None means no limit is set.
   'READ_OD_LOW_LIMIT'  : 30,
   'READ_OD_UP_LIMIT'   : None,
   'READ_ID_LOW_LIMIT'  : 17,
   'READ_ID_UP_LIMIT'   : None,
   # Write operation parameters. None means no limit is set.
   'WRITE_OD_LOW_LIMIT' : 30,
   'WRITE_OD_UP_LIMIT'  : None,
   'WRITE_ID_LOW_LIMIT' : 17,
   'WRITE_ID_UP_LIMIT'  : None,
}

###################################### MANTARAY NETAPP ###########################################################################
netapp_seekTest = {
   'loop_Test'             : 1,
   'loop_Seek'             : 5000,
   'seek_type'             : 0x2,               # 0x2 = WRITE_SEEK
   }

netapp_staticDataCompare = {
   'loop_Count'            : 10,
   'delay_time'            : 5,                 # Delay for each loop 5 secs
   }

netapp_dataCompareSIOPTest = {
   'loop_Count'            : 2,
   'sector_count'          : 64,                # 512 * 64 = 32K
   'delay_time'            : 5,
   }

netapp_butterflyWriteTest = {
   'loop_Count'            : 15,
   'run_time'              : 30*60,                            # Run time in seconds
   'TOTAL_LBA_TO_XFER'     : (0x0000, 0x0000, 0x0060, 0x0000), # Approx. 10 min - MantaRay SAS
   'TOTAL_BLKS_TO_XFR'     : (0x006A, 0x0000),                 # Approx. 10 min - MantaRay - CPC
   }

netapp_bandSeqRWCmpTest = {
   'loop_Count'            : 2,
   'increasing_step'       : 10,                # Default use 2 = 2%
   'pattern_count'         : 4,                 # Random , Incremental, Shifting bit, Counting
   'stepLBA'               : 64,                # 32K xfer
   }

netapp_stressedPinchTest = {
   'loop_Count'            : 10,
   'loop_Write'            : 4,
   }

netapp_simulateWorkLoadSIOPTest = {
   'run_time'              : 15*60,             # Run time in second
   'lba_size'              : 512,
   }

netapp_dataErasureTest = {
   'loop_Count'            : 1,                 # About 941 secs per loop
   'lba_size'              : 512,
   'data_size'             : (.5 * 1024 * 1024 * 1024) / 512,  # Write 1/2GB
   'pattern_count'         : 2,                 # Random , Incremental, Shifting bit, Counting
   }

netapp_dataErasureTest2 = {
   'loop_Write'            : 3500,
   }

netapp_adjacentPinch = {
   'loop_Count'            : 1,
   'loop_Write'            : 1000,
   }

prm_510_BUTTERFLY = {
   'test_num'          : 510,
   'prm_name'          : 'prm_510_BUTTERFLY',
   'spc_id'            :  1,
   'timeout'           : 3000,                                 # 15 Mins Test Time
   'CTRL_WORD1'        : 0x0422,                               # Butterfly Sequencetial Write; Display Location of errors
   'CTRL_WORD2'        : 0x0000,
   'STARTING_LBA'      : (0, 0, 0, 0),
   'BLKS_PER_XFR'      : 256,
   'TOTAL_BLKS_TO_XFR' : (0x0000, 0xFFFF),
   'OPTIONS'           : 0,                                    # Butterfly Converging
   }

prm_510_CMDTIME_WR = {        # Write Same screen for NetApp customer
   'test_num'              : 510,
   'prm_name'              : 'prm_510_CMDTIME_WR',
   'timeout'               : 2694.7,             # = Mean + 7%
   'spc_id'                : 5,
   'CTRL_WORD1'            : 0x0022,
   'CTRL_WORD2'            : 0xA080,
   'STARTING_LBA'          : (0, 0, 0, 0),
   'BLKS_PER_XFR'          : 5000,              # 5000 = 10MB per NetApp
   'MAX_NBR_ERRORS'        : 0,
   'MAX_COMMAND_TIME'      : 7000,              # 7 Second for SATA
   }

prm_510_CMDTIME_RD = {        # Write Same screen for NetApp customer
   'test_num'              : 510,
   'prm_name'              : 'prm_510_CMDTIME_RD',
   'timeout'               : 2617.7,             # = Mean + 7%
   'spc_id'                : 5,
   'CTRL_WORD1'            : 0x0012,
   'CTRL_WORD2'            : 0xA080,
   'STARTING_LBA'          : (0, 0, 0, 0),
   'BLKS_PER_XFR'          : 5000,              # 5000 = 10MB per NetApp
   'MAX_NBR_ERRORS'        : 0,
   'MAX_COMMAND_TIME'      : 7000,              # 7 Second for SATA
   }

## Full pack read.
prm_510_FPR_AVSCAN = {
   'test_num'          : 510,
   'prm_name'          : "prm_510_FPR_AVSCAN",
   'display_info'      : True,
   'timeout'           :  2*25200,
   'spc_id'            :  4,
   "CTRL_WORD1"        : (0x0012),             ## Hidden reties disabled, Read
   "CTRL_WORD2"        : (0xE080),             ## 09/14/07: Changed 0x2080->ox6080 to report CCT
                                               ## 11/13/07: Turn on bit 15 (0x6080 -> E080)to save read error
   "STARTING_LBA"      : (0,0,0,0),
   "TOTAL_BLKS_TO_XFR" : (0x0000,0x0000),      # Full pack
   "BLKS_PER_XFR"      : (0x100),
   "DATA_PATTERN0"     : (0x0000, 0x0000),
   "MAX_NBR_ERRORS"    : (10),
   "RESET_AFTER_ERROR" : (1),
   "CCT_BIN_SETTINGS"  : (0x1E0A),              #6/11/08 set up 30 bins at 10 ms each
   "MAX_COMMAND_TIME"  : (0xFFFF),              ## Failure threashold in ms.  0xFFFF is for data collection, no failing
   #"DISABLE_ECC_ON_THE_FLY" : (1),              ### 11/07/07 1=Disable 0=Enable
   #"ECC_CONTROL"       : (1),                   ### 11/07/07 1=Enable  0=Disable
   #"ECC_T_LEVEL"       : (12),                  #6/11/08 set per nieves recommendation
   "CCT_LBAS_TO_SAVE"  : (0x30),                #6/11/08 added for AVSCAN spec
}

## MT50/10 Measurement Test

prm_MT50_10_Measurement_269= {
   'test_num'               : 269,
   'prm_name'               : 'prm_MT50_10_Measurement_269',
   'spc_id'                 : 1,
   'timeout'                : 10000,
   'CWORD1'                 : 0x3801,  #If Bit 9 in ON, test only at Zero Skew Area, Zone_mask is no effect.
   'LOOP_CNT'               : 2,
   'STEP_INC'               : 4,
   'HEAD_MASK'              : 0xFF,
   'ZONE_MASK'              : {
                               'ATTRIBUTE':'numZones',
                               24: (0x0000, 0x0001),
                               31: (0x0000, 0x0001),   
                               60: (0x0000, 0x0001),
                               },
   'ZONE_MASK_EXT'          : {
                               'ATTRIBUTE':'numZones',
                               24: (0x0000, 0x0000),
                               31: (0x0000, 0x0000),   
                               60: (0x0000, 0x0000),
                              },
   'TRIM_PERCENTAGE_VALUE'  : 10,
   'SET_OCLIM'              : 200,
   'OFFSET_SETTING'         : (-380, 380, 255),
   'ZONE_POSITION'          : 198,
}

erase_band_testing_zones = [0]
prm_erase_band = {
   'test_num'              : 270,
   'prm_name'              : 'prm_erase_band',
   'timeout'               : 10000,
   'spc_id'                : 1,
   'LOOP_CNT'              : 2,
   'HEAD_MASK'             : 255,
   'OFFSET_SETTING'        : (-380, 380, 212),
   'STEP_INC'              : 8,
   'CWORD1'                : 0x0001,
   'ZONE_POSITION'         : 198,
   'SET_OCLIM'             : 200,
}

#HSC st190 setting of HSC_TCC_LT & HSC_TCC_HT
prm_190_HSC_TCC = {
   'test_num'               : 190,
   'prm_name'               : 'HSC_TCCtestprm',
   'timeout'                : 36000,
   'spc_id'                 : 1,
   'CWORD1'                 : {
      'ATTRIBUTE'          : 'nextState',
      'DEFAULT'            : 'default',
      'default'            : 0x1122,
      'HSC_TCC_LT'         : 0x1122,
      'HSC_TCC_HT'         : 0x1102,
   },
   'HEAD_RANGE'             : 0xFFFF,
   'BIT_MASK'               : (0x4444, 0x8889), # (0,1,),
   'LOOP_CNT'               : 20,
   'FREQUENCY'              : 120,
   'THRESHOLD'              : 0,
}

Prm_190_Settling = {
   'test_num'               : 190,
   'prm_name'               : 'settlingtestprm',
   'timeout'                : 36000,
   'spc_id'                 : 1,
   'CWORD1'                 : 0x0002,
   'HEAD_RANGE'             : 0xFFFF,
   'BIT_MASK'               : (0,1,),
   'LOOP_CNT'               : 90,     # only place to control loop cnt ,90
   'FREQUENCY'              : 120,     #Prm_190["FREQUENCY"]
}

getRpmPrm_11_HSC = {
               'test_num'        :11,
               'prm_name'        :'GetRPM',
               'timeout'         :1000,
               'spc_id'          :1,
               'CWORD1'          :(0x0200),
               'SYM_OFFSET'      :(144),
               'ACCESS_TYPE'     :(0),
               'ZONE_POSITION'   :198,
}

############################ Track Cleanup default parameters ####################################
trackCleanupRetryCnt = 3    #  defined the # of retry when errors r reported during wr/rd in Clean-up state.

if testSwitch.FE_0184418_357260_P_USE_TRACK_WRITES_FOR_CLEANUP or testSwitch.FE_0187241_357260_P_USE_BAND_WRITES_FOR_CLEANUP:
   trackCleanupSerpentPad  = 5
   trackPadMultiplier      = 1.2
   trackCleanupAFHPad      = 100
   trackCleanupT211Pad     = 10
   trackCleanupT238Pad     = 10
   trackCleanupT250Pad     = 10
   trackCleanupT61Pad      = 10
   trackCleanupT190Pad     = 10
   trackCleanupT195Pad     = 10
   if testSwitch.FE_0258915_348429_COMMON_TWO_TEMP_CERT:
      trackCleanupT199Pad     = 10
   trackCleanupNCTCPad     = 50
else:
   trackCleanupSerpentPad  = 200
   trackPadMultiplier      = 1.2
   trackCleanupAFHPad      = 100
   trackCleanupT211Pad     = 10
   trackCleanupT238Pad     = 10
   trackCleanupT250Pad     = 5
   trackCleanupT61Pad      = 10
   trackCleanupT190Pad     = 5
   trackCleanupT195Pad     = 5
   if testSwitch.FE_0258915_348429_COMMON_TWO_TEMP_CERT:
      trackCleanupT199Pad     = 5
   trackCleanupNCTCPad     = 35

####################### FOF Screen use #################################
##### LUL_Profile_Const #####
SPINDLE_RPM = 5408
K_RPM_CNT = 167000000
VEL_BITS_PER_IPS = 19630
K_DAC = 32768
K_PA = 666

####################### For debugging #######################
# After every state, read system sector to make sure no error
# 'OPER': [list of states] or 'ALL'
CheckFirstSysTrackList = { # Read first system track and report good/bad
   'PRE2' : '',
   'CAL2' : '',
   'FNC2' : '',
   'CRT2' : '',
}
CheckFirstSysTrackCmd = {  # True = F3 mode, False = SF3 mode
   True  : ('2', 0, 0, 0, 1), # ( DiagLevel, Cyl, Head, Sector, Length )
   False : (0, 0), # ( Cyl, Head )
}

if testSwitch.DEPOP_TESTING:  # depop testing
   DepopTestSN = {
      # 'Serial Num' : [ head_to_depop ],
      # 'Q9400VIR'  : [0],
   }


############################ CTcc_BY_BER #########################################
prm_errRateByZone = {
   'test_num'              : 250,
   'prm_name'              : "prm_errRateByZone",
   'spc_id'                : 1,
   'timeout'               : 900,   # extra pad- shud take 5 min/zone for ea pass
   'ZONE'                  : 0,
   'ZONE_MASK'             : (0L, 1),
   'ZONE_MASK_EXT'         : (0L, 0),
   'TEST_HEAD'             : 0,
   'CWORD1'                : (0x01c3,),   # (0x0187,),
   'CWORD2'                : 5,
   'TLEVEL'                : 0,        # ECC off default
   'PERCENT_LIMIT'         : 0xFF,     # turn on the consideration for non_converging code word
   'WR_DATA'               : (0x00),   # 1 byte for data pattern if writing first
   'RETRIES'               : 50,
   'ZONE_POSITION'         : 198,
   'MAX_ERR_RATE'          : -90,
   'NUM_TRACKS_PER_ZONE'   : 10,
   'SKIP_TRACK'            : 200,
   'MINIMUM'               : -10,
   'MAX_ITERATION'         : 0x0705,
}

######### APO #########
prm_F3_APO_delta_BER = {
    'Zones'      : [1, 15, 30],
    'SectorStep' : 5,
    'FailSafe'   : 1,
}

####################### ATI/WRITE_SCRN PARAM ##########################

RRAW_CRITERIA_ATI_51 = {
   'baseline_limit'        : (0, 0.7, 0, 0.7),      # Limit = 0.7, flag = 1 means enabled this limit check
   'erasure_limit'         : (1, 5.0, 1, 5.0),
   'delta_limit'           : (0, 1.1, 0, 3.0),
   'deltapercentage_limit' : (0, 101, 0, 30)
}

BIE_BER_CRITERIA_ATI_51 = {
   'baseline_limit'        : (0, 0, 0, 0),      #  flag = 1 means enabled this limit check
   'erasure_limit'         : (0, 0, 0, 0),
   'delta_limit'           : (0, 0, 0, 100),
   'deltapercentage_limit' : (0, 0, 0, 0)
}
OTF_CRITERIA_ATI  = {   # no limit check
   'baseline_limit'        : (0, 0.0, 0, 0.7),
   'erasure_limit'         : (0, 4.0, 0, 4.0),
   'delta_limit'           : (0, 1.1, 0, 1.1),
   'deltapercentage_limit' : (0, 101, 0, 101)
}
##############################################################################


#########################Part Num Info Capacity###############################
capacity = {
   '2' : '500G',
   'C' : '320G',
   '1' : '250G',
   '4' : '1000G',
   '3' : '750G',
   'G' : '750G',
   'E' : '640G',
}
##############################################################################

# HeaterPower = (power_to_apply, repeat_no_of_times, no_of_times_to_check_to_pass)
prm_Head_Recovery_Heater_Power = {
   'EC_Trigger'      : [11126, 10560],
   'HeaterPower'     : [(40,1,0), (50,1,0), (60,1,0), (65,3,0), (65,15,1), ],
}

Post_TSR_ET_Instability_VGA_195_Limit = 12   # limit to use for T195 after TSR

RdScrn2_Retry_with_TSR = {
   'EC_Trigger'      : [10632],  # error codes in READ_SCRN2 to trigger TSR
   'Extra_T250'      : 2,        # no of additionaly T250 to run
}

RDScrn_SPC_ID   = 1 #define default read_scrn spc_id
RdScrn2_SPC_ID  = 2
SqzWrite_SPC_ID = 3 #define default SQZ_WRITE spc_id

OdMinCap = 0

VbarCapacityGBPerHead = 250 #default value of capper_hd
UMP_ZONE = {
   31:   [1, 30],
   60:   [1, 2, 3, 59],
   120:  [5, 6, 7, 119],
   150:  [4, 5, 6, 7, 149],
   180:  [5, 6, 7, 8, 9, 10, 179],
}

if testSwitch.FE_0385234_356688_P_MULTI_ID_UMP:
   UMP_ZONE.update({
      150:  range(121, 150, 1),
   })

UMP_ZONE_BY_HEAD = {
   1: {

         60  : [2, 3, 59],
         120 : [4, 5, 6, 119],
         150 : [3, 4, 5, 6, 149],
         180 : [4, 5, 6, 7, 8, 9, 179],
      },
   2: {

         60  : [2, 3, 59],
         120 : [4, 5, 6, 119],
         150 : [3, 4, 5, 6, 149],
         180 : [4, 5, 6, 7, 8, 9, 179],
      },
   3: {

         60  : [2, 3, 59],
         120 : [4, 5, 6, 119],
         150 : [3, 4, 5, 6, 149],
         180 : [4, 5, 6, 7, 8, 9, 179],
      },
   4: {

         60  : [2, 3, 59],
         120 : [4, 5, 6, 119],
         150 : [3, 4, 5, 6, 149],
         180 : [4, 5, 6, 7, 8, 9, 179],
      },
}

if testSwitch.FE_0385234_356688_P_MULTI_ID_UMP:
   UMP_ZONE_BY_HEAD.update({
      1: {
            60  : [3, 4, 59],
            120 : [5, 6, 7, 119],
            150 : range(121, 150, 1), #[4, 5, 6, 7, 149],
            180 : [5, 6, 7, 8, 9, 10, 179],
         },
      2: {
            60  : [3, 4, 59],
            120 : [5, 6, 7, 119],
            150 : range(121, 150, 1), #[4, 5, 6, 7, 149],
            180 : [5, 6, 7, 8, 9, 10, 179],
         },
      3: {
            60  : [3, 4, 59],
            120 : [5, 6, 7, 119],
            150 : range(122, 150, 1), #[4, 5, 6, 149],
            180 : [5, 6, 7, 8, 9, 10, 179],
         },
      4: {
            60  : [3, 4, 59],
            120 : [5, 6, 7, 119],
            150 : range(123, 150, 1), #[4, 5, 149],
            180 : [5, 6, 7, 8, 9, 10, 179],
         },
   })

if testSwitch.ADAPTIVE_GUARD_BAND:   
   MC_ZONE = {
      'ATTRIBUTE':'numZones',
      'DEFAULT': 150,   
      150 : range(1, min(UMP_ZONE[150]), 1),
      180 : range(1, min(UMP_ZONE[180]), 1),
   }
else:   
   MC_ZONE = {
      'ATTRIBUTE':'numZones',
      'DEFAULT': 150,   
      150 : range(0, min(UMP_ZONE[150]), 1),
      180 : range(0, min(UMP_ZONE[180]), 1),
   }
   
if testSwitch.FE_0385234_356688_P_MULTI_ID_UMP:
   if testSwitch.ADAPTIVE_GUARD_BAND:
      MC_ZONE.update({
         'ATTRIBUTE':'numZones',
         'DEFAULT': 150,
         150 : range(1,4,1),      # [1, 2, 3]
         180 : range(1, min(UMP_ZONE[180]), 1),
      })
   else:
      MC_ZONE.update({
         'ATTRIBUTE':'numZones',
         'DEFAULT': 150,
         150 : range(0,3,1),      # [0, 1, 2]
         180 : range(0, min(UMP_ZONE[180]), 1),
      })
   
numMC = len(MC_ZONE)
numUMP = len(UMP_ZONE)
      
BaseTestZone = {               # eg. for BPINOMINAL, PRE_OPTI, 2D_VBAR
   'ATTRIBUTE':'numZones',
   'DEFAULT': 150,
   150 :[0,35,75,115,149],
}

baseVbarTestZones  = {
   'ATTRIBUTE': 'FE_0385234_356688_P_MULTI_ID_UMP',
   'DEFAULT'  : 0,
   0 : {150: [8, 13, 18, 23, 28, 33, 38, 43, 48, 53, 58, 63, 68, 73, 78, 83, 88, 93, 98, 103, 108, 113, 118, 123, 128, 133, 138, 143, 148, 149],},
   1 : {150: [8, 13, 18, 23, 28, 33, 38, 43, 48, 53, 58, 63, 68, 73, 78, 83, 88, 93, 98, 103, 108, 113, 118],},
}

baseSMRZoneBeforeUMP = {
   'ATTRIBUTE':'numZones',
   'DEFAULT': 150,
   150 : {'EQUATION': "sorted(list(set(range(TP.MC_ZONE[-1]+1,(TP.baseVbarTestZones[150][0]),1) + TP.baseVbarTestZones[150] + range(TP.baseVbarTestZones[150][-1]+1,(TP.UMP_ZONE[150][0]),1) )))",},
}

BERInVBAR_ZN = {           # eg. for T250 in VBAR_ZN
   'ATTRIBUTE':'numZones',
   'DEFAULT': 150,
   150 :[0,38,78,118,149],
}

_2D_VBAR_ZN_INDEX = {   #Index for the 2D test zone from the list baseVbarTestZones
   'ATTRIBUTE': 'FE_0385234_356688_P_MULTI_ID_UMP',
   'DEFAULT'  : 0,
   0 : {150: [2, 6, 14, 22, 28],},
   1 : {150: [2, 6, 14, 22],},
}

_2DVBAR_ZN = {           # eg. for T250 in VBAR_ZN
   'ATTRIBUTE':'numZones',
   'DEFAULT': 150,
   150 : {
      'ATTRIBUTE': 'FE_0385234_356688_P_MULTI_ID_UMP',
      'DEFAULT'  : 0,
      0 : [0, 18, 38, 78, 118, 148],
      1 : {'EQUATION': "[0] + [TP.baseVbarTestZones[150][index] for index in TP._2D_VBAR_ZN_INDEX [150]] + [TP.UMP_ZONE[150][0]-1]",},
   },
}

BPIMeasureZone = {        # eg. for BPI measure zone, 0+MC+UMP+[(8 to 148)/5]+SPARE, ZONE MUST in ASCENDING order
   'ATTRIBUTE':'numZones',
   'DEFAULT': 150,      
   150: {
      'ATTRIBUTE': 'FE_0385234_356688_P_MULTI_ID_UMP',
      'DEFAULT'  : 0,
      0 : [0] + MC_ZONE[150] + range(UMP_ZONE[150][0],UMP_ZONE[150][len(UMP_ZONE[150])-2]+1,1) + range(UMP_ZONE[150][len(UMP_ZONE[150])-2]+1,149,5) + [149],    # spare zn define in UMP_ZONE
      1 : {'EQUATION': "sorted(list(set([0] + TP.MC_ZONE + list(set(TP.UMP_ZONE[150] + range(TP.MC_ZONE[-1]+1,(TP.baseVbarTestZones[150][0]),1) + TP.baseVbarTestZones[150] + range(TP.baseVbarTestZones[150][-1]+1,(TP.UMP_ZONE[150][0]),1))))) )",},   
   },
}

BPIMeasureZoneNoUMP = {        # eg. for BPI measure zone, 0+MC+UMP+[(8 to 148)/5]+SPARE, ZONE MUST in ASCENDING order
   'ATTRIBUTE':'numZones',
   'DEFAULT': 150,      
   150: {
      'ATTRIBUTE': 'FE_0385234_356688_P_MULTI_ID_UMP',
      'DEFAULT'  : 0,
      0 : [0] + MC_ZONE[150] + range(UMP_ZONE[150][len(UMP_ZONE[150])-2]+1,149,5),    # spare zn define in UMP_ZONE
      1 : {'EQUATION': "sorted(list(set([0] + TP.MC_ZONE + list(set(range(TP.MC_ZONE[-1]+1,(TP.baseVbarTestZones[150][0]),1) + TP.baseVbarTestZones[150] + range(TP.baseVbarTestZones[150][-1]+1,(TP.UMP_ZONE[150][0]),1))))) )",},   
   },
}
   
Unvisited_Zones = {
   'ATTRIBUTE':'numZones',
   'DEFAULT': 60,
   31: range(1,31,2),
   60: range(1,60,2),
   120: range(1,120,2),
   150: {
      'ATTRIBUTE': 'FE_0274346_356688_ZONE_ALIGNMENT',
      'DEFAULT'  : 0,
      0 : range(1,150,2),
      1 : list(set(range(150))-set(BPIMeasureZone[150])),
   },
   180: range(1,180,2),
}

Triplet_Zones = {
   'ATTRIBUTE':'numZones',
   'DEFAULT': 31,
   24: [0,23,12,6,18,3,9,15,21],
   31: [0,30,15,7,22,4,11,19,26], 
   60:{ 
      'ATTRIBUTE':'FAST_2D_VBAR_UNVISITED_ZONE', #test time reduction for Vbar
      'DEFAULT': 0,
      0: [x*(60-1)/(31 -1) for x in [0,30,15,7,22,4,11,19,26]], #[0, 59, 29, 13, 43, 7, 21, 37, 51]
      1: [0, 59] + [int(x*59/30/2)*2 for x in [15,7,22,4,11,19,26]], #[0, 59, 28, 12, 42, 6, 20, 36, 50]
   },
   120:{ 
      'ATTRIBUTE':'FAST_2D_VBAR_UNVISITED_ZONE', #test time reduction for Vbar
      'DEFAULT': 0,
      0: [x*(120-1)/(31 -1) for x in [0,30,15,7,22,4,11,19,26]], 
      1: [0, 119] + [int(x*119/30/2)*2 for x in [15,7,22,4,11,19,26]], 
   },
   150:{ 
      'ATTRIBUTE': 'FE_0274346_356688_ZONE_ALIGNMENT',
      'DEFAULT'  : 0,
      0: {
         'ATTRIBUTE':'FAST_2D_VBAR_UNVISITED_ZONE', #test time reduction for Vbar
         'DEFAULT': 0,
         0: [x*(150-1)/(31 -1) for x in [0,30,15,7,22,4,11,19,26]], 
         1: [0, 149] + [int(x*149/30/2)*2 for x in [15,7,22,4,11,19,26]], 
      },
      1: [0,149,75,35,115,15,55,95,135],
   },
   180:{ 
      'ATTRIBUTE':'FAST_2D_VBAR_UNVISITED_ZONE', #test time reduction for Vbar
      'DEFAULT': 0,
      0: [x*(180-1)/(31 -1) for x in [0,30,15,7,22,4,11,19,26]], #[0, 179, 89, 41, 131, 23, 65, 113, 155]
      1: [0, 179] + [int(x*179/30/2)*2 for x in [15,7,22,4,11,19,26]], #[0, 179, 88, 40, 130, 22, 64, 112, 154]
   },
}

Channel_PreOpti_Zones = {
   'ATTRIBUTE':'numZones',
   'DEFAULT': 60,
   31: list(set([ zn for zn in range(31) if zn not in Unvisited_Zones[31]] + Triplet_Zones[31])),
   60: {
      'ATTRIBUTE':'FAST_2D_VBAR_UNVISITED_ZONE', #test time reduction for Vbar
      'DEFAULT': 0,
      0 : list(set([ zn for zn in range(60) if zn not in Unvisited_Zones[60]] + Triplet_Zones[60][0])),
      1 : list(set([ zn for zn in range(60) if zn not in Unvisited_Zones[60]] + Triplet_Zones[60][1])),
   },
   120: {
      'ATTRIBUTE':'FAST_2D_VBAR_UNVISITED_ZONE', #test time reduction for Vbar
      'DEFAULT': 0,
      0 : list(set([ zn for zn in range(120) if zn not in Unvisited_Zones[120]] + Triplet_Zones[120][0])),
      1 : list(set([ zn for zn in range(120) if zn not in Unvisited_Zones[120]] + Triplet_Zones[120][1])),
   },
   150: {
      'ATTRIBUTE': 'FE_0274346_356688_ZONE_ALIGNMENT',
      'DEFAULT'  : 0,
      0: {
         'ATTRIBUTE':'FAST_2D_VBAR_UNVISITED_ZONE', #test time reduction for Vbar
         'DEFAULT': 0,
         0 : list(set([ zn for zn in range(150) if zn not in Unvisited_Zones[150][0]] + Triplet_Zones[150][0][0])),
         1 : list(set([ zn for zn in range(150) if zn not in Unvisited_Zones[150][0]] + Triplet_Zones[150][0][1])),
      },
      1: Triplet_Zones[150][1],
   },
   180: {
      'ATTRIBUTE':'FAST_2D_VBAR_UNVISITED_ZONE', #test time reduction for Vbar
      'DEFAULT': 0,
      0 : list(set([ zn for zn in range(180) if zn not in Unvisited_Zones[180]] + Triplet_Zones[180][0])),
      1 : list(set([ zn for zn in range(180) if zn not in Unvisited_Zones[180]] + Triplet_Zones[180][1])),
   },
}

prm_FINModules = [
    ('IDT_SHORT_DST_IDE'          , 'ON'),
    ('IDT_VERIFY_SMART_IDE'       , 'ON'),
    ('IDT_VERIFY_SMART_ONLY'      , 'ON'),
    ('IDT_RESET_SMART'            , 'ON'),
    ('IDT_GET_SMART_LOGS'         , 'ON'),
    ('IDT_SERIAL_SDOD_TEST'       , 'OFF')
]

AGC_Destroke_Ratio = 1.0

RD_OFST_SEL_FMT_PICKER = 0 #dummy value 
SPC_ID_BANDED_TPI_FMT_PICKER = 1 #dummy value
SQZBPI_SER = 77 #-2.11 db ser setting

VBAR_measured_Zones =  { #default all zones
   'ATTRIBUTE':'numZones',
   'DEFAULT': 31,
   31 : range(31),
   60 : range(60),
   120: range(120),
   150: range(150),
   180: range(180),
}
Destroke_Trk_To_Load_A_New_RAP = 10000

MIN_SOVA_SQZ_WRT = -10 
NUM_UDE          = 0

tracksPerBand = 50 ## Default value of tracks per band for SMR zones ##

minizap_zone_OAR_ELT_SMR = [] ## OAR measurement zone

T250_OAR_Screen_Spec = {
   ('P250_SEGMENT_BER_SUM2', 'match')      : {
      'spc_id'       : 22, # default is all table available
      # 'row_sort'     : 'HD_LGC_PSN', # default is HD_LGC_PSN if omitted
      'col_sort'     : 'DATA_ZONE', # default is DATA_ZONE if omitted
      'col_range'    : (1,4,149), # default is any, no filtering
      'column'       : ('DELTA_ALIGNED_BER'),
      'compare'      : (         '>'),
      'criteria'     : (          1.0 ),
      #'fail_count'   : 1, # this is must have for count type
   },
   ('P250_SEGMENT_BER_SUM2', 'count')      : {
      'spc_id'       : 23, # default is all table available
      # 'row_sort'     : 'HD_LGC_PSN', # default is HD_LGC_PSN if omitted
      'col_sort'     : 'DATA_ZONE', # default is DATA_ZONE if omitted
      'col_range'    : (1,4,149), # default is any, no filtering
      'column'       : ('DELTA_ALIGNED_BER'),
      'compare'      : (         '>'),
      'criteria'     : (          1.0 ),
      'fail_count'   : 1, # this is must have for count type
   },
   ('Fail_Cnt','')                        : 1, # default is fail all criteria to constitute screening failed
}

# Define the State that turn on/off zap in simple_opti class 
zapOnstatelist = ['READ_OPTI', 'PRE_OPTI', 'PRE_OPTI2', 'READ_OPTI1', 'PREVBAR_OPTI', 'LASER_FINAL']
zapOffstatelist = ['PRE_OPTI', 'PRE_OPTI2','LASER_FINAL', 'READ_OPTI'] 

zapOffOper_SegmentedBER = {
   'ATTRIBUTE'    : 'nextOper',
   'DEFAULT'      : 'PRE2',
   'PRE2'         : 1,
   'CAL2'         : 1,
   'FNC2'         : 0,
   'CRT2'         : 0,
}

### OTC test parameter   
prm_TPI_211_OTC = {
   'test_num'           : {
      'ATTRIBUTE'    : 'SFT_TEST_0271',
      'DEFAULT'      : 0,
      0              : 211, # for linggi code
      1              : 271, # for trunk code
   },
   'prm_name'           : {
      'ATTRIBUTE'    : 'SFT_TEST_0271',
      'DEFAULT'      : 0,
      0              : 'MeasureTPIOTC_211', # for linggi code
      1              : 'MeasureTPIOTC_271', # for trunk code
   },
   'HEAD_RANGE'         : 0x3ff, #all hds 
   'NUM_TRACKS_PER_ZONE': {
      'ATTRIBUTE'    : 'nextState',
      'DEFAULT'      : 'default', #for vbar_otc, vbar_otc2
      'default'      : 3, #3 tracks 
      'VBAR_ZN'      : 1, #1 track for vbar_margin by otc
      'VBAR_MARGIN'  : 1, #1 track for vbar_margin by otc
      'VBAR_MARGIN_OTC'  : 1, #1 track for vbar_margin by otc
      'OTC_BANDSCRN' : 3,
   },
   'NUM_SQZ_WRITES'     : {
      'ATTRIBUTE':'FE_0258915_348429_COMMON_TWO_TEMP_CERT',
      'DEFAULT'  : 0,
       0          : {'EQUATION': 'TP.num_sqz_writes'}, #reference to TestParamter.py
       1          : 1,
   }, 
   'ZONE_POSITION'      : {'EQUATION': 'TP.ZONE_POS'}, #reference to TestParamter.py
   'CWORD1'             : 0x0036,   #Enable multi-track mode
   'CWORD2'             : 0x0008,
   'CWORD3'             : {
      'ATTRIBUTE'    : 'nextState',
      'DEFAULT'      : 'default', #for vbar_otc, vbar_otc2
      'default'      : 0x0003 | testSwitch.OTC_REV_CONTROL << 2 | testSwitch.FAST_2D_VBAR_TESTTRACK_CONTROL << 3, 
      'VBAR_ZN'      : 0x003D,
      'VBAR_MARGIN'  : 0x003D,
      'VBAR_MARGIN_OTC'  : 0x003D,
      'OTC_BANDSCRN' : 0x098F,
   },
   'SET_OCLIM'          : {
      'ATTRIBUTE'    : 'nextState',
      'DEFAULT'      : 'default', #for vbar_otc, vbar_otc2
      'default'      : 800,
      'VBAR_ZN'      : 1228,
      'VBAR_MARGIN'  : 1228,
      'VBAR_MARGIN_OTC'  : 1228,
      'OTC_BANDSCRN' : 1228,
   },
   'TPI_TARGET_SER'     : {
      'ATTRIBUTE'    : 'nextState',
      'DEFAULT'      : 'default', #for vbar_otc, vbar_otc2
      'default'      : 30,
      'OTC_BANDSCRN' : 1, # set to low to avoid huge baseline error flag
   },
   'TPI_STEP'           : 2,
   'RESULTS_RETURNED'   : {
      'ATTRIBUTE'    : 'nextState',
      'DEFAULT'      : 'default',
      'default'      : 0x0106, #skip OTC Bucket printing
      'OTC_BANDSCRN' : 0x0006, #detail print
   },
   'TPI_TLEVEL'         : {'EQUATION' :'TP.MaxIteration'},
   'LIMIT'              : 180,
   'MAX_ERR_RATE'       : -80,
   'timeout'            : {'EQUATION' : '70*self.dut.imaxHead*self.dut.numZones'},
   'spc_id'             : {
      'ATTRIBUTE'    : 'nextState',
      'DEFAULT'      : 'default', #for vbar_otc, vbar_otc2
      'default'      : 2, 
      'OTC_BANDSCRN' : 40,
   },
   'ADJ_BPI_FOR_TPI'    : 0, #no internal drive adjustment of bpic
   'CWORD4'             : 0x1, #get shingle direction from the drive
   ## zone_mask, zone_mask_ext, zone_mask_bank to be updated
}

if testSwitch.HAMR: 
   prm_TPI_211_OTC['RESULTS_RETURNED'].update({ 'VBAR_OTC': 0x0006, 'VBAR_OTC2': 0x0006,})  # detail printing

Measured_BPINOMINAL_Zones = {
   'ATTRIBUTE':'numZones',
   'DEFAULT': 60,
   17 : [0, 4, 8, 12, 16],
   24 : [0, 6, 12, 18, 22],
   31 : [0, 3, 8, 16, 24, 30],
   60 : [0, 6, 16, 32, 48, 59],
   120: [0, 12, 32, 64, 96, 119],
   150: [0, 15, 40, 80, 120, 149],
   180: [0,18,48,96,144,179],
}

num_sqz_writes = {
   'ATTRIBUTE':'FE_0258915_348429_COMMON_TWO_TEMP_CERT',
   'DEFAULT'  : 0,
   0          : 6,
   1          : 10,
}

SetByZnCword = 0x2000 #cword1 of t210 to set format by zone instead of by head
prm_PrePostOptiAuditSQZWRT_250_2 = {
   'test_num'              : 250,
   'prm_name'              : 'PrePostPhastOptiSQZWRT',
   'spc_id'                : 24,
   'timeout'               : {
      'EQUATION':'self.dut.imaxHead*1000*self.dut.numZones/60'
   },         
   'CWORD1'                : 0x4981, #turn on adjacent wrt
   'CWORD2'                : 0,
   'TEST_HEAD'             : 0x00FF,
   'NUM_SQZ_WRITES'        : 1, #num of adjacent wrt is 1
   'ZONE_MASK'             : {
      'ATTRIBUTE'    : 'numZones',
      'DEFAULT'      : 24,
      24             : (0x00FF, 0xFFFF),
      31             : (0x7FFF, 0xFFFF),
      60             : (0xFFFF, 0xFFFF),
   },
   'ZONE_MASK_EXT'             : {
      'ATTRIBUTE'    : 'numZones',
      'DEFAULT'      : 24,
      24             : (0, 0),
      31             : (0, 0),
      60             : (0x0FFF, 0xFFFF),
   },
   'MAX_ERR_RATE'          : -90,
   'MINIMUM'               : -19,
   'ZONE_POSITION'         : {'EQUATION': 'TP.ZONE_POS'},
   'WR_DATA'               : 0x00,
   'NUM_TRACKS_PER_ZONE'   : 10,
   'MAX_ITERATION'         : {'EQUATION' :'TP.MaxIteration'},  ## org is 24
   'RETRIES'               : 50,
   'SKIP_TRACK'            : {
      'ATTRIBUTE'    : 'FE_0245014_470992_ZONE_MASK_BANK_SUPPORT',
      'DEFAULT'      : 0,
      0              : 200,
      1              : 20, #Zone 94, 110, 179 may have less than 200 tracks, so skip_track cannot remain at 200.
   },
   'TLEVEL'                : 0,
}

RunT250Pre_Channel = 1 # must run t250 pre_channel tuning
RunT250Post_Channel = 1 # must run t250 post_channel tuning

bpi_bin_size = {
   'EQUATION':'self.dut.imaxHead*488928* self.dut.numZones/60'
}

zone_table = {
   'table_name': {
      "ATTRIBUTE"    : ('FE_0269440_496741_LOG_RED_P172_ZONE_TBL_SPLIT','FE_0184102_326816_ZONED_SERVO_SUPPORT'),
      'DEFAULT'      : (0,0),
      (0,0)        : 'P172_ZONE_TBL',
      (0,1)        : 'P172_ZONED_SERVO',
      (1,0)        : 'P172_ZONE_DATA',
      (1,1)        : 'P172_ZONED_SERVO_RED',      
   },
   'resvd_table_name': {
      "ATTRIBUTE"    : ('FE_0269440_496741_LOG_RED_P172_ZONE_TBL_SPLIT','FE_0184102_326816_ZONED_SERVO_SUPPORT'),
      'DEFAULT'      : (0,0),
      (0,0)        : 'P172_RESVD_ZONE_TBL',
      (0,1)        : 'P172_RSVD_ZONED_SERVO',
      (1,0)        : 'P172_RESVD_ZONE_DATA',
      (1,1)        : 'P172_RSVD_ZONED_SERVO_RED',            
   },
   'trk_name': {
      "ATTRIBUTE"    : ('FE_0269440_496741_LOG_RED_P172_ZONE_TBL_SPLIT','FE_0184102_326816_ZONED_SERVO_SUPPORT'),
      'DEFAULT'      : (0,0),
      (0,0)        : 'PBA_TRACK',
      (0,1)        : 'PBA_TRACK',
      (1,0)        : 'PBA_TRK',
      (1,1)        : 'PBA_TRACK',           
   },   
   'cword1': {
      "ATTRIBUTE"    : 'FE_0184102_326816_ZONED_SERVO_SUPPORT',
      'DEFAULT'      : 0,
      0              : 0x0002,
      1              : 48,
   },      
}

zoned_servo_zn_tbl = {
   'table_name': {
      "ATTRIBUTE"    : 'FE_0269440_496741_LOG_RED_P172_ZONE_TBL_SPLIT',
      'DEFAULT'      : 0,
      0              : 'P172_ZONED_SERVO',
      1              : 'P172_ZONED_SERVO_RED',
   },
   'resvd_table_name': {
      "ATTRIBUTE"    : 'FE_0269440_496741_LOG_RED_P172_ZONE_TBL_SPLIT',
      'DEFAULT'      : 0,
      0              : 'P172_RSVD_ZONED_SERVO',
      1              : 'P172_RSVD_ZONED_SERVO_RED',
   },
}

#####################EWAC/WPE####################################
prm_WPE = {
   'test_num':69, 
   'FREQUENCY':100, 
   'BAND_SIZE': 7, 
   'ZONE_POSITION':198, 
   'spc_id': 1, 
   'CWORD1': {'EQUATION': 'TP.wpeCword1'}, #refer to cword1 inside TestParameter.py
   'BIT_MASK'    : (0, 1), 
   'BIT_MASK_EXT': {
      'ATTRIBUTE' : 'programName',
      'DEFAULT'   : 'default',
      'default'   : (0, 0),
      'M10P'      : (0x0800, 0x0001),
   },
   'timeout': 1000,
}

prm_OW_EWAC_69 = {
   'test_num'        : 69,
   'FREQUENCY'       : 100,
   'BAND_SIZE'       : 7,
   'ZONE_POSITION'   : 198,
   'CWORD1'          : {'EQUATION' : 'TP.ewacCword1'}, #refer to cword1 inside TestParameter.py
   'spc_id'          : 1,
   'HEAD_RANGE'      : 0,
   'BIT_MASK_EXT': {
      'ATTRIBUTE' : 'programName',
      'DEFAULT'   : 'default',
      'default'   : (0, 0),
      'M10P'      : (0x0800, 0x0001),
   },
   'timeout'         : 360,
}

prm_HdPinReversalTest_265 = {
   'test_num'               : 265,
   'prm_name'               : 'prm_HdPinReversalTest_265',
   'spc_id'                 : 1,
   'timeout'                : 10000,
   'CWORD1'                 : 0x7,
   'LOOP_CNT'               : 10,
   'TARGET_TRK_WRITES'      : 3000,
   'HEAD_MASK'              : 0xFF,
   'ZONE_POSITION'          : 100,
   'WRITE_TRIPLET'          : (110,20,20), #Will be used if cword1 bit3 is ON.
}

################################################################


###################FE_0269922_348085_P_SIGMUND_IN_FACTORY#######
filesToSave = {
   "ATTRIBUTE": 'FE_0269922_348085_P_SIGMUND_IN_FACTORY',
   0          : ['HEADER', 'AFH', 'RW_GAP', 'MR_RES'],
   1          : ['HEADER', 'AFH', 'RW_GAP', 'MR_RES', 'SIF'],
}
################################################################

############################# PROC_CTRL30 Bit Definitions ###################################
Proc_Ctrl30_Def = {}
