#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: SDAT Test Parameters
# Owner: Jim French
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Amazon/SdatParameters.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Amazon/SdatParameters.py#1 $
# Level: 1
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
numHeads = TP.numHeads
from base_SdatParameters import *

ENABLE_MIXED_RATE_NOTCH_SUPPORT  = 1   # Requires servo and SF3 support, be sure to set if running w/mixedrate in pre2
OUTPUT_CONTROLLER_COEFFICIENTS   = 1   # Use T172(CWORD1=29) to dump the servo controller coeffs and controller map

# Create the default project name at runtime to alleviate maintaining the pn2Prj dictionary
nativeHdCount = TP.Servo_Sn_Prefix_Matrix[HDASerialNumber[1:3]]['PhysHds']
numDiscs = int(round(float(nativeHdCount)/2))
project = '%s%sD' % (TP.ProductName, numDiscs)  # Build up project name to use as the default
pn2Prj = {
   'DEF'        : project,
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
   'NBR_TFA_SAMPS'          : 22,
   'NBR_MEAS_REPS'          : 4,
   'INJ_AMPL'               : 140,
   'GAIN_LIMIT'             : 1000,
   'MEASURE_PHASE'          : (),
   'CWORD1'                 : 0x0020,
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
   'FREQ_BAND_LO_1_PARMS'   : (200,   80,  11),
   'FREQ_BAND_LO_2_PARMS'   : (500,   60,  22),
   'FREQ_BAND_MID_1_PARMS'  : (6000,  40,  1000),
   'FREQ_BAND_MID_2_PARMS'  : (22000, 80,  1800),
   'FREQ_BAND_HI_1_PARMS'   : (28000, 200, 2500),
   'FREQ_BAND_HI_2_PARMS'   : (64000, 400, 5000),
   'GAIN_LIMIT'             : 5000,
   'MEASURE_PHASE'          : (),
   'CWORD1'                 : 0x0020,
   }

uActStructuralSDATBode = {
   'test_num'               : 152,
   'prm_name'               : 'uActStructuralSDATBode',
   'timeout'                : 2000*numHeads,
   'spc_id'                 : 1,
   'FAIL_SAFE'              : (),
   'PLOT_TYPE'              : 7,     #  Plot type 7 is uActuator structural upsample
   'HEAD_RANGE'             : 0xFFFF,
   'FREQ_RANGE'             : (25, 65535),
   'FREQ_INCR'              : 25,
   'FREQ_BAND_LO_1_PARMS'   : (200,   80,  11),
   'FREQ_BAND_LO_2_PARMS'   : (500,   60,  22),
   'FREQ_BAND_MID_1_PARMS'  : (6000,  40,  1000),
   'FREQ_BAND_MID_2_PARMS'  : (22000, 80,  1800),
   'FREQ_BAND_HI_1_PARMS'   : (28000, 200, 2500),
   'FREQ_BAND_HI_2_PARMS'   : (64000, 400, 5000),
   'INJ_AMPL2'              : 120,
   'GAIN_LIMIT'             : 5000,
   'MEASURE_PHASE'          : (),
   'CWORD1'                 : 0x0020,
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

vCatOff_47 = {                         # Turn off VCAT
   'test_num'               : 47,
   'prm_name'               : 'vCatOff_47',
   'timeout'                : 500*numHeads,
   'spc_id'                 : 1,
   'CWORD1'                 : 0x0020,      # Switch to real track mode, turns off VCAT
   }

setDualStage_56 = {
   'test_num'               : 56,
   'prm_name'               : 'Set Dual Stage',
   'spc_id'                 : 1,
   'CWORD1'                 : 0x0002,
   'TEST_CYL'               :(0,0),
   }


setSingleStage_56 = {
   'test_num'               : 56,
   'prm_name'               : 'Set Single Stage',
   'spc_id'                 : 1,
   'CWORD1'                 : 0x0001,
   'TEST_CYL'               :(0,0),
   }


runPztGainCal_56 = {
   'test_num'               : 56,
   'prm_name'               : 'Run PZT Gain Cal',
   'spc_id'                 : 1,
   'CWORD1'                 : 0x7022,
   'LOOP_CNT'               : 10,
   'TEST_CYL'               :(0,0),
   }

doDualStageBodeTestsPrm_288 = {
      'test_num'               : 288,
      'prm_name'               : 'doDualStageBodeTests288',
      'timeout'                : 600 + (1800*numHeads),
      'spc_id'                 : 1,
      'FREQ_STEP'              : (0,25),
      'FREQ_START'             : (0,25),
      'FREQ_STOP'              : (0x0000,0x9C40),
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
      'FREQ_STOP'              : (0x0000,0x9C40),
      'CWORD1'                 : 0x8000,               # Execute all measuremnts enabled by other CWORDx control bits
      'CWORD3'                 : 0x0A00,               # Run OL VCM Current, and VCM Plant Bode measurements
      }

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
   'timeout'                : {"EQUATION": "600 + (4000* self.dut.imaxHead)"},
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
   'timeout'                : {"EQUATION": "600 + (1600* self.dut.imaxHead)"},
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
   'timeout'                : {"EQUATION": "600 + (1000* self.dut.imaxHead)"},
   'spc_id'                 : 0,   # No data goes to the result file.
   'CWORD1'                 : 0x8100,
   }


# These parameters are used to get the three MDW
# data items (eccentricity, error rates, track zero) through Test 288.
getMdwDataPrm_288 = {
   'test_num'               : 288,
   'prm_name'               : 'GetMdwData',
   'timeout'                : {"EQUATION": "600 + (1000* self.dut.imaxHead)"},
   'spc_id'                 : 0,   # No data goes to the result file.
   'CWORD1'                 : 0x81C0,
   }

# These parameters are used to get TMR verify data through Test 288.
getTmrVerPrm_288 = {
   'test_num'               : 288,
   'prm_name'               : 'GetTmrVerifyData',
   'timeout'                : {"EQUATION": "600 + (1000* self.dut.imaxHead)"},
   'spc_id'                 : 0,   # No data goes to the result file.
   'CWORD1'                 : 0x8000,
   'CWORD4'                 : 0x003F,
   }



# These parameters are used to get Track follow data through Test 288.
getTrkFollowPrm_288 = {
   'test_num'               : 288,
   'prm_name'               : 'GetTrackFollowRroData',
   'timeout'                : {"EQUATION": "900 + (1500* self.dut.imaxHead)"},
   'spc_id'                 : 0,   # No data goes to the result file.
   'CWORD1'                 : 0x8000,
   'CWORD4'                 : 0x0040
   }

# These parameters are used to get servo linearization data through Test 288.
getLinearizationPrm_288 = {
   'test_num'               : 288,
   'prm_name'               : 'GetServoLinearizationData',
   'timeout'                : {"EQUATION": "900 + (500* self.dut.imaxHead)"},
   'spc_id'                 : 0,   # No data goes to the result file.
   'CWORD1'                 : 0x8000,
   'CWORD4'                 : 0x0400
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
   'CWORD2'                 : 0xC000, #JY++
   }

getZestTableZip_288 = {
   'test_num'        : 288,
   'prm_name'        : 'getZestTableZip',
   'timeout'         : {"EQUATION": "500* self.dut.imaxHead"},
   'spc_id'          : 0, # No data goes to the result file
   'CWORD1'          : 0x8001,
   }

getDriveInfo_288 = {
   'test_num'        : 288,
   'prm_name'        : 'getDriveInfo',
   'timeout'         : {"EQUATION": "500* self.dut.imaxHead"},
   'spc_id'          : 0, # No data goes to the result file
   'CWORD1'          : 0x8000,
   'CWORD4'          : 0x8000,
   }

InitializeAndDriveInfoPrm_288 = {
   'test_num'               : 288,
   'prm_name'               : 'InitializeAndDriveInfo288',
   'timeout'                : {"EQUATION": "500* self.dut.imaxHead"},
   'spc_id'                 : 0,
   'CWORD1'                 : 0xD000,               # Set all params to default, create a new (empty) binary data file, and run test
   'CWORD4'                 : 0x8000,               # Test to run Drive Info
   }


VibeDataSequentialSeeks_288 = {
   'test_num'        : 288,
   'prm_name'        : 'VibeDataSequentialSeeks',
   'timeout'         : 3600,
   'spc_id'         : 0,
   'CWORD1'          : 0x8000,
   'CWORD2'          : 0x0400,
   }

VibeDataButterflySeeks_288 = {
   'test_num'        : 288,
   'prm_name'        : 'VibeDataButterflySeeks',
   'timeout'         : 3600,
   'spc_id'          : 0,
   'CWORD1'          : 0x8000,
   'CWORD2'          : 0x0800,
   }

VibeDataCollection_288 = {
   'test_num'        : 288,
   'prm_name'        : 'VibeDataCollection',
   'timeout'         : 3600,
   'spc_id'          : 0,
   'CWORD1'          : 0x8000,
   'CWORD2'          : 0x0200,
   }


getuActGainCalPrm_288 = {
   'test_num'        : 288,
   'prm_name'        : 'getuActGainCal',
   'timeout'         : 3600,
   'spc_id'          : 0,
   'CWORD1'          : 0x8000,
   'CWORD2'          : 0x0080,
   }

xvTransferFuncPrmOD_288 = {
    'test_num':288,
    'prm_name':'xvTransferFuncPrmOD',
    'timeout': 4000,
    'CWORD1':0x8000,
    'CWORD3': 0x0081,
    'TRACK_OPTIONS': 0,
    'HEAD_MASK':1,
    'START_CYL':(0,1000),
    'END_CYL':(0,1000),
    'STEP_CYL':(0,10),
    'FREQ_OPTIONS':0,
    'FREQ_STEP':(0,25),
    'FREQ_START':(0,1000),
    'FREQ_STOP':(0,26000),
}

xvTransferFuncPrmID_288 = {
    'test_num':288,
    'prm_name':'xvTransferFuncPrmID',
    'timeout': 4000,
    'CWORD1':0x8000,
    'CWORD3': 0x0081,
    'TRACK_OPTIONS': 1,
    'HEAD_MASK':1,
    'START_CYL':(0x0000,0x7d70),
    'END_CYL':(0x0000,0x7d71),
    'STEP_CYL':(0,0xA3),
    'FREQ_OPTIONS':0,
    'FREQ_STEP':(0,25),
    'FREQ_START':(0,1000),
    'FREQ_STOP':(0,26000),
}


