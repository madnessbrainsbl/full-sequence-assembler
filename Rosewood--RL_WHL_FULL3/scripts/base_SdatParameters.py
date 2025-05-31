#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Common SDAT Test Parameters (for all products)
# Owner: Gary Erickson
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_SdatParameters.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_SdatParameters.py#1 $
# Level: ?
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParameters import numHeads


servoSym = {
   'u16_Track0ValueTable_INDEX'     : 171,
   }

zipSdatResults = False

TmrVerifyTestParms = {
   'trx_to_test'            : 400,
   'revs_per_trk'           : 100,
   'revs_worst_nrro'        : 100,
   }

getSymbolTableSize_11 = {
   'test_num'               : 11,
   'prm_name'               : 'getSymbolTableSize',
   'timeout'                : 1000,
   'spc_id'                 : 1,
   'CWORD1'                 : 0x0200,
   'SYM_OFFSET'             : 0,
   'ACCESS_TYPE'            : 0,
   }

getMixedRateNotchAddrPrm_11 = {
   'test_num'               : 11,
   'prm_name'               : 'getMixedRateNotchAddr',
   'timeout'                : 1000,
   'spc_id'                 : 1,
   'CWORD1'                 : 0x0200,
   'SYM_OFFSET'             : 325,
   'ACCESS_TYPE'            : 0,
   }

getMixedRateNotchNumViaAddrPrm_11 = {
   'test_num'               : 11,
   'prm_name'               : 'getMixedRateNotchNumViaAddr',
   'timeout'                : 1000,
   'spc_id'                 : 1,
   'CWORD1'                 : 0x0001,
   'ACCESS_TYPE'            : 1,
   }

olSDATBode = {
   'test_num'               : 152,
   'prm_name'               : 'olSDATBode',
   'timeout'                : 2000*numHeads,
   'spc_id'                 : 1,
   'FAIL_SAFE'              : (),
   'HEAD_RANGE'             : 0xFFFF,
   'FREQ_RANGE'             : (25, 65535),
   'FREQ_INCR'              : 25,
   'NBR_TFA_SAMPS'          : 14,
   'NBR_MEAS_REPS'          : 2,
   'INJ_AMPL'               : 70,
   'GAIN_LIMIT'             : 1000,
   'MEASURE_PHASE'          : (),
   }

StructuralSDATBode = {
   'test_num'               : 152,
   'prm_name'               : 'StructuralSDATBode',
   'timeout'                : 2000*numHeads,
   'spc_id'                 : 1,
   'FAIL_SAFE'              : (),
   'PLOT_TYPE'              : 6,
   'HEAD_RANGE'             : 0xFFFF,
   'FREQ_RANGE'             : (25, 65535),
   'FREQ_INCR'              : 25,
   'NBR_TFA_SAMPS'          : 14,
   'NBR_MEAS_REPS'          : 2,
   'INJ_AMPL'               : 70,
   'GAIN_LIMIT'             : 1000,
   'MEASURE_PHASE'          : (),
   }

GetNotchSDATBode_152 = {
   'test_num'               : 152,
   'prm_name'               : 'GetNotchSDATBode_152',
   'timeout'                : 2000*numHeads,
   'spc_id'                 : 1,
   'CWORD1'                 : 0x0040,
   }

GetUactNotchSDATBode_152 = {
   'test_num'               : 152,
   'prm_name'               : 'GetUactNotchSDATBode_152',
   'timeout'                : 2000*numHeads,
   'spc_id'                 : 1,
   'NOTCH_TABLE'            : 2,
   'CWORD1'                 : 0x0040,
   }

setDualStage_56 = {
   'test_num'               : 56,
   'prm_name'               : 'Set Dual Stage',
   'spc_id'                 : 1,
   'CWORD1'                 : 0x0002,
   }

setSingleStage_56 = {
   'test_num'               : 56,
   'prm_name'               : 'Set Single Stage',
   'spc_id'                 : 1,
   'CWORD1'                 : 0x0001,
   }

runPztGainCal_56 = {
   'test_num'               : 56,
   'prm_name'               : 'Run PZT Gain Cal',
   'spc_id'                 : 1,
   'CWORD1'                 : 0x7022,
   'LOOP_CNT'               : 10,
   }

GetPES = {
   'test_num'               : 33,
   'prm_name'               : 'GetPES',
   'timeout'                : 5000*numHeads,
   'spc_id'                 : 1,
   'REVS'                   : 100,
   'TEST_HEAD'              : 0x00FF,
   'DELTA_NRRO_LIMIT'       : 0x0320,
   'CWORD1'                 : 0x8837,
   'SEEK_TYPE'              : 0x0025,
   'DELAY_TIME'             : 0,
   'REPORT_OPTION'          : 1,
   'MIN_NRRO_LIMIT'         : 0x002F,
   'MAX_NRRO_LIMIT'         : 0x03E8,
   'MAX_RRO_LIMIT'          : 0x03E8,
   'S_OFFSET'               : 0,
   'RETEST_DELAY'           : 0,
   'RETEST_UNSAFE_LMT'      : 200,
   'RETRY_INCR'             : 1,
   }

zapPrm_RdzapOff = {                    # Turn off Read ZAP
'test_num' : 175,
'prm_name' : 'zapPrm_RdzapOff',
'timeout'  : 1500 * numHeads,
'spc_id'   : 1,
'CWORD1'   : 0x1004,
}

zapPrm_RdzapOn = {                     # Turn on Read ZAP
   'test_num' : 175,
   'prm_name' : 'zapPrm_RdzapOn',
   'timeout'  : 3 * 60,
   'spc_id'   : 1,
   'CWORD1'   : 0x1008,
   }

vCatCalPrm_47_virtual = {              # Turn on VCAT and CHROME
   'test_num'               : 47,
   'prm_name'               : 'vCatCal_01Prm_47',
   'timeout'                : 1500*numHeads,
   'spc_id'                 : 1,
   'TEST_CYL'               : (0, 30000),
   'CWORD1'                 : 0x1240,      # Switch to virtual track mode, turn on Chrome in virtual mode
   'SEEK_DELAY'             : 50,
   'LIMIT'                  : 12,
   'REVS'                   : 128,
   'MAX_ITERATION'          : 6,
   'GAIN_CONTROL'           : 9,
   'NUM_SAMPLES'            : 20,
   'LIMIT32'                : (300, 20),
   'INJ_AMPL2'              : 800,
   'INJ_AMPL'               : 64000,
   }

vCatCalPrm_47_real = {                 # Turn off VCAT and CHROME
   'test_num'               : 47,
   'prm_name'               : 'vCatCal_01Prm_47',
   'timeout'                : 2000*numHeads,
   'spc_id'                 : 1,
   'TEST_CYL'               : (0, 30000),
   'CWORD1'                 : 0x1120,      # Switch to real track mode, turn off Chrome in real mode
   'SEEK_DELAY'             : 50,
   'LIMIT'                  : 12,
   'REVS'                   : 128,
   'MAX_ITERATION'          : 6,
   'GAIN_CONTROL'           : 9,
   'NUM_SAMPLES'            : 20,
   'LIMIT32'                : (300, 20),
   'INJ_AMPL2'              : 800,
   'INJ_AMPL'               : 64000,
   }

vCatOn_47 = {                          # Turn on VCAT
   'test_num'               : 47,
   'prm_name'               : 'vCatOn_47',
   'timeout'                : 100*numHeads,
   'spc_id'                 : 1,
   'CWORD1'                 : 0x1040,      # Switch to virtual track mode, turns on VCAT
   }

vCatOff_47 = {                         # Turn off VCAT
   'test_num'               : 47,
   'prm_name'               : 'vCatOff_47',
   'timeout'                : 100*numHeads,
   'spc_id'                 : 1,
   'CWORD1'                 : 0x1020,      # Switch to real track mode, turns off VCAT
   }

servoLinCalPrm_150_sdat = {
   'test_num'               : 150,
   'prm_name'               : 'servoLinCalPrm_150_sdat',
   'timeout'                : 2000*numHeads,
   'spc_id'                 : 1,
   'CWORD1'                 : (0x8804,),
   'NBR_CYLS'               : 1,
   'HEAD_RANGE'             : 0x00FF,
   'CONVERGE_LIM_1'         : 50,
   'INJ_AMPL'               : 10,
   'NUM_SAMPLES'            : 1024,
   'NBR_MEAS_REPS'          : 3,
   'FINAL_PK_PK_GAIN_LIM'   : 600,
   }

getRpmPrm_11 = {
   'test_num'               : 11,
   'prm_name'               : 'GetRPM',
   'timeout'                : 1000,
   'spc_id'                 : 1,
   'CWORD1'                 : 0x0200,
   'SYM_OFFSET'             : 144,
   'ACCESS_TYPE'            : 0,
   }

getSptPrm_11 = {
   'test_num'               : 11,
   'prm_name'               : 'GetSPT',
   'timeout'                : 1000,
   'spc_id'                 : 1,
   'CWORD1'                 : 0x0200,
   'SYM_OFFSET'             : 140,
   'ACCESS_TYPE'            : 0,
   }

getServoConst_11 = {
   'test_num'               : 11,
   'prm_name'               : 'GetServoConst',
   'timeout'                : 1000,
   'spc_id'                 : 1,
   'CWORD1'                 : 0x0200,
   'SYM_OFFSET'             : 140,        # Overwrite as needed to access a specific servo constant
   'ACCESS_TYPE'            : 0,
   }

getServoVar_11 = {
   'test_num'               : 11,
   'prm_name'               : 'GetServoVar',
   'timeout'                : 1000,
   'spc_id'                 : 1,
   'CWORD1'                 : 0x0200,
   'SYM_OFFSET'             : 140,        # Overwrite as needed to acces a specific servo variable
   'ACCESS_TYPE'            : 2,          # Overwrite as needed if the size of the variable is not 16 bits
   }

getServoArray_11 = {
   'test_num'               : 11,
   'prm_name'               : 'GetServoArray',
   'timeout'                : 1000,
   'spc_id'                 : 1,
   'CWORD1'                 : 0x0200,
   'SYM_OFFSET'             : 140,        # Overwrite as needed to access specific servo arrays
   'NUM_LOCS'               : 1,          # Overwrite as needed to define the size of the array to be read
   'ACCESS_TYPE'            : 2,          # Overwrite as needed if the size of each array element is not 16 bits
   }

readServoRamAddr_11 = {
      'test_num'            : 11,
      'prm_name'            : 'ReadServoRamAddr',
      'timeout'             : 1000,
      'spc_id'              : 1,
      'CWORD1'              : 0x0001,
      'START_ADDRESS'       : (0x0400, 0x14F8,),   # Overwrite as needed to access a specific servo memory address
   }

chromeOnPrm_11 = {
   'test_num'               : 11,
   'prm_name'               : 'chromeOnPrm',
   'timeout'                : 1000,
   'spc_id'                 : 1,
   'CWORD1'                 : 0x0400,      # Read/modify/write by SYM_OFFSET
   'MASK_VALUE'             : 0xFEFF,
   'WR_DATA'                : 0x0100,
   'SYM_OFFSET'             : 47,          # u16_ChromeParameters
   'ACCESS_TYPE'            : 2,
   }

chromeOffPrm_11 = {
   'test_num'               : 11,
   'prm_name'               : 'chromeOffPrm',
   'timeout'                : 1000,
   'spc_id'                 : 1,
   'CWORD1'                 : 0x0400,      # Read/modify/write by SYM_OFFSET
   'MASK_VALUE'             : 0xFEFF,
   'WR_DATA'                : 0x0000,
   'SYM_OFFSET'             : 47,          # u16_ChromeParameters
   'ACCESS_TYPE'            : 2,
   }


# These parameters are used to get MDW data
getTmndvPrm_11 = {
   'test_num'               : 11,
   'prm_name'               : 'GetTMNDV',
   'timeout'                : 1000,
   'spc_id'                 : 1,
   'CWORD1'                 : 0x0200,
   'SYM_OFFSET'             : 166,
   }

getOsevPrm_11 = {
   'test_num'               : 11,
   'prm_name'               : 'GetOSEV',
   'timeout'                : 1000,
   'spc_id'                 : 1,
   'CWORD1'                 : 0x0200,
   'SYM_OFFSET'             : 167,
   }

fullStrokeSeeksPrm_30 = {
   'test_num'               : 30,
   'prm_name'               : 'Do10KFullStrokeSeek',
   'timeout'                : 10000,
   'spc_id'                 : 1,
   'CWORD1'                 : 0x0023,
   'START_CYL'              : (0,0),
   'PASSES'                 : 10000,
   'TIME'                   : (1,1000,1000),
   }

fullStrokeSeek1Prm_30 = {
   'test_num'               : 30,
   'prm_name'               : 'Do1FullStrokeSeek',
   'timeout'                : 100,
   'spc_id'                 : 1,
   'CWORD1'                 : 0x0023,
   'START_CYL'              : (0,0),
   'PASSES'                 : 1,
   'TIME'                   : (1,1000,1000),
   }

trackSpacingPrm_187 = {                # Test 187 Track Spacing Test
   'test_num'               : 187,
   'prm_name'               : 'Track_spacing_test',
   'timeout'                : 15000*numHeads,
   'spc_id'                 : 1,
   'CWORD1'                 : 0x3000,
   'START_CYL'              : (0x0000, 0x0000),
   'END_CYL'                : (0xFFFF, 0xFFFF),
   'HEAD_RANGE'             : 0x00FF,
   'REVS'                   : 1,
   'NBR_BINS'               : 23,
   'BIN_SIZE'               : 8,
   'NBR_JOG_BINS'           : 21,
   'JOG_BIN_SIZE'           : 10,
   'JOG_ERROR_EXCEPT_LIM'   : 90,
   'JOG_ERROR_EXCEPT_LIM_2' : -90,
   'OOS_JOG_TRACKS_EXCEPT'  : 10000,
   'LOG_SPACING_EXCEPT_LIM' : 40,
   'OOS_LOG_SPACING_EXCEPT' : 10000,
   }

# Test 288 control parameters.  T288 will ultimately combine all necessary test function
# for every form of SDAT data collection.  The SDAT data is passed to the host through a
# binary PC File (sdatfile). The first call to T288 should always use initializTestPrm_288,
# which initializes all test function parameters to their default value, and clears the
# binary file.  All subsequent calls to T288 will perform specific measurements, or
# collections of measurements, and append their data to the binary file.
# When the binary file is created by the initializeTestPrm_288 call, the drive
# temperature is saved to the file immediately.  The temperature is the first
# record in the binary file.
initializeTestPrm_288 = {
   'test_num'               : 288,
   'prm_name'               : 'initializeTest288',
   'timeout'                : 60,
   'spc_id'                 : 1,
   'CWORD1'                 : 0x5000,               # Set all params to default, and create a new (empty) binary data file
   }

doDualStageBodeTestsPrm_288 = {
   'test_num'               : 288,
   'prm_name'               : 'doDualStageBodeTests288',
   'timeout'                : 600 + (1800*numHeads),
   'spc_id'                 : 1,
   'FREQ_STEP'              : (0,25),
   'FREQ_START'             : (0,25),
   'FREQ_STOP'              : (0xFFFF,0xFFFE),
   'MAX_MIN_DELTA'          : (200, 50),            # Set the target PES range to 1.2 - 4.9% of track pitch
   'CWORD1'                 : 0x8000,               # Execute all measuremnts enabled by other CWORDx control bits
   'CWORD3'                 : 0x2600,               # Run Dual Stage OL, uAct Plant, and VCM Plant Bode measurements
   }

doVCMBodeTestsPrm_288 = {
   'test_num'               : 288,
   'prm_name'               : 'doVCMBodeTests288',
   'timeout'                : 600 + (1000*numHeads),
   'spc_id'                 : 1,
   'FREQ_STEP'              : (0,25),
   'FREQ_START'             : (0,25),
   'FREQ_STOP'              : (0xFFFF,0xFFFE),
   'CWORD1'                 : 0x8000,               # Execute all measuremnts enabled by other CWORDx control bits
   'CWORD3'                 : 0x0A00,               # Run OL VCM Current, and VCM Plant Bode measurements
   }



# These parameters are used to get Eccentricity data through Test 288.
getEccentricityPrm_288 = {
   'test_num'               : 288,
   'prm_name'               : 'GetEccentricity',
   'timeout'                : 100,
   'spc_id'                 : 0,   # No data goes to the result file.
   'CWORD1'                 : 0x8040,
   }


# These parameters are used to get Tack Zero data through Test 288.
getTrkZeroPrm_288 = {
   'test_num'               : 288,
   'prm_name'               : 'GetTk0',
   'timeout'                : 100,
   'spc_id'                 : 0,   # No data goes to the result file.
   'CWORD1'                 : 0x8080,
   }


# These parameters are used to get Missed Address and Bad sector error rate
# data through Test 288.
getMdwErrRatePrm_288 = {
   'test_num'               : 288,
   'prm_name'               : 'GetMdwErrRates',
   'timeout'                : 10000,
   'spc_id'                 : 0,   # No data goes to the result file.
   'CWORD1'                 : 0x8100,
   }


# These parameters are used to get TMR verify data through Test 288.
getTmrVerPrm_288 = {
   'test_num'               : 288,
   'prm_name'               : 'GetTmrVerifyData',
   'timeout'                : 400 + (600*numHeads),
   'spc_id'                 : 0,   # No data goes to the result file.
   'CWORD1'                 : 0x8000,
   'CWORD4'                 : 0x003F,
   }



# These parameters are used to get Track follow data through Test 288.
getTrkFollowPrm_288 = {
   'test_num'               : 288,
   'prm_name'               : 'GetTrackFollowRroData',
   'timeout'                : 800 + (2000*numHeads),
   'spc_id'                 : 0,   # No data goes to the result file.
   'CWORD1'                 : 0x8000,
   'CWORD4'                 : 0x0040
   }


# These parameters are used to collect controller and notch coefficients using T288.
# SF3 flag FE_0166104_010200_ENABLE_T288_CONTROLLER_DATA_SUPPORT must be enabled in
# order for these parameters to have any effect.  All necessary PF3 changes are enabled 
# by the SF3 flag.
getCtrlAndNotchCoeffs_288 = {
   'test_num'               : 288,
   'prm_name'               : 'CtrlAndNotchCoeffs_288',
   'timeout'                : 240,
   'spc_id'                 : 0,   # No data goes to the result file.
   'CWORD1'                 : 0x8000,
   'CWORD2'                 : 0xC000,
   }