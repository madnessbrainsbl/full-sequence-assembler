#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Test Parameters for Luxor programs - Grenada,
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/12/28 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Amazon/ServoParameters.py $
# $Revision: #33 $
# $DateTime: 2016/12/28 19:04:15 $
# $Author: yihua.jiang $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Amazon/ServoParameters.py#33 $
# Level: 1
#---------------------------------------------------------------------------------------------------------#
import Constants
from Constants import *
from Utility import CUtility
from Test_Switches import testSwitch
from TestParameters import numHeads
Utl = CUtility()

if testSwitch.FE_0243459_348085_DUAL_OCLIM_CUSTOMER_CERT:
   defaultOCLIM_customer = {
      'ATTRIBUTE'  : 'BG',
      'DEFAULT'    : 'OEM1B',
      'OEM1B'      : 10,
      'SBS'        : 9,
      }

defaultOCLIM         = 14  # Enter value in % of Track. Value will be converted prior to drive call

mdwOCLIM             = 20  # OCLIM to use during mdw calibrations
oclimSAPOffset       = 42  # Symbol offset into SAP for OCLIM value for current head
maxOCLIM             = 3.1 # Maximum over allowance for OCLIM

DisableShockSensor   = 'C716F,0,0,0,0,0,0,0'
EnableShockSensor    = 'C706F,0,0,0,0,0,0,0'
MAX_CYL              = 206000
mdwCalCompleteOffset = 101
snoNotches_152       = []
snoNotches_152_VCM   = []
snoNotches_152_DAC   = []

prm_VOST_Default_TPI = 290000    # Default servo tpi

#P025_LD_UNLD_PARAM_STATS  LOAD_MAX_CUR SPEC in absolute value
load_max_cur_USL = 155
load_max_cur_LSL = 105

if testSwitch.FE_0258915_348429_COMMON_TWO_TEMP_CERT:
   load_max_cur_USL_adjust = 20
   load_max_cur_LSL_adjust = 20
else:
   load_max_cur_USL_adjust = 0
   load_max_cur_LSL_adjust = 0


#MAX_RRO spec trigger reZAP
MAX_RRO = 7

# setChannelRegisterSettingsInSAP can be used to set channel register values by writing to the SAP.
#  In order to use this functionality, you must have servo code which supports this ability, and
#  SF3 switch FE_0115982_357915_SET_CHANNEL_REG_IN_SAP must be enabled.  Servo defines the maximum
#  number of registers which may be set in this manner.  The keys in the dictionary are the addresses
#  of the channel registers to write, and the corresponding values are the values to write to those
#  registers.  Both should be 16 bit values.
setChannelRegisterSettingsInSAP = {
   #Address (16 bit)         : value (16 bit)
   0x0073                    : 0x8137,
}
# Parameters arrangement according to tests
################################## Test 0004 ##################################
# For Motor Jitter test
MotorJitterPrm_4 = {
   'test_num'                : 4,
   'prm_name'                : 'Motor Jitter Test',
   'timeout'                 : 200,
   'spc_id'                  : 1,
   'CWORD1'                  : 0x0010,
   'MOTOR_TIMER_DELTA'       : 300,
   'ZERO_CROSSING_REVS'      : 100,
}
###############################################################################
################################## Test 0007 ##################################
# Parameters sets for Tuned Seek Test (Test #7)
#Tuned Seek OD 3 cyls
prm_007_0070 = {   
   'test_num'                : 7,
   'prm_name'                : 'prm_tunedSeek_7_0070',
   'timeout'                 : 1200 * numHeads,
   'spc_id'                  : 1,
   'CWORD1'                  : (0x0400,),
   'START_CYL'               : (0x0000,0x0000,),
   'END_CYL'                 : (0x0000,0x0003,),
   'INITIAL_DELAY'           : (0x0000,),
   'FINAL_DELAY'             : (0x0c80,),
   'DELAY_INCREMENT'         : (0x00fa,),
   'SEEK_TYPE'               : (0x0025,),
   'TEST_HEAD'               : (0x00ff,),
   'DELAY_B4_RETRY'          : (0x0001,),
   'UNSAFE_MAX_LIMIT'        : (0x07ff,),
   'SEEK_NUMS'               : (0x00fa,),
   'RETRY_LIMIT'             : (0x005a,),
}
#Tuned Seek OD 5 cyls
prm_007_0071 = {   
   'test_num'                : 7,
   'prm_name'                : 'prm_tunedSeek_7_0071',
   'timeout'                 : 1200 * numHeads,
   'spc_id'                  : 2,
   'CWORD1'                  : (0x0400,),
   'START_CYL'               : (0x0000,0x0000,),
   'END_CYL'                 : (0x0000,0x0005,),
   'INITIAL_DELAY'           : (0x0000,),
   'FINAL_DELAY'             : (0x0c80,),
   'DELAY_INCREMENT'         : (0x00fa,),
   'SEEK_TYPE'               : (0x0025,),
   'TEST_HEAD'               : (0x00ff,),
   'DELAY_B4_RETRY'          : (0x0001,),
   'UNSAFE_MAX_LIMIT'        : (0x07ff,),
   'SEEK_NUMS'               : (0x00fa,),
   'RETRY_LIMIT'             : (0x005a,),
}
#Tuned Seek MD 3 cyls
prm_007_0072 = {
   'test_num'                : 7,
   'prm_name'                : 'prm_tunedSeek_7_0072',
   'timeout'                 : 1200 * numHeads,
   'spc_id'                  : 3,
   'CWORD1'                  : (0x0400,),
   'START_CYL'               : (0x0001,0x1940,),
   'END_CYL'                 : (0x0001,0x1943,),
   'INITIAL_DELAY'           : (0x0000,),
   'FINAL_DELAY'             : (0x0c80,),
   'DELAY_INCREMENT'         : (0x00fa,),
   'SEEK_TYPE'               : (0x0025,),
   'TEST_HEAD'               : (0x00ff,),
   'DELAY_B4_RETRY'          : (0x0001,),
   'UNSAFE_MAX_LIMIT'        : (0xffff,),
   'SEEK_NUMS'               : (0x00fa,),
   'RETRY_LIMIT'             : (0x005a,),
}
#Tuned Seek MD 5 cyls
prm_007_0073 = {
   'test_num'                : 7,
   'prm_name'                : 'prm_tunedSeek_7_0073',
   'timeout'                 : 1200 * numHeads,
   'spc_id'                  : 4,
   'CWORD1'                  : (0x0400,),
   'START_CYL'               : (0x0001,0x1940,),
   'END_CYL'                 : (0x0001,0x1945,),
   'INITIAL_DELAY'           : (0x0000,),
   'FINAL_DELAY'             : (0x0c80,),
   'DELAY_INCREMENT'         : (0x00fa,),
   'SEEK_TYPE'               : (0x0025,),
   'TEST_HEAD'               : (0x00ff,),
   'DELAY_B4_RETRY'          : (0x0001,),
   'UNSAFE_MAX_LIMIT'        : (0xffff,),
   'SEEK_NUMS'               : (0x00fa,),
   'RETRY_LIMIT'             : (0x005a,),
}
#Tuned Seek ID 3 cyls
prm_007_0074 = {
   'test_num'                : 7,
   'prm_name'                : 'prm_tunedSeek_7_0074',
   'timeout'                 : 1200*numHeads,
   'spc_id'                  : 13,
   'CWORD1'                  : (0x0400,),
   'START_CYL'               : (0x0002,0x3280,),
   'END_CYL'                 : (0x0002,0x3283,),
   'INITIAL_DELAY'           : (0x1225,),
   'FINAL_DELAY'             : (0x1225,),
   'DELAY_INCREMENT'         : (0x1225,),
   'SEEK_TYPE'               : (0x0025,),
   'TEST_HEAD'               : (0x00ff,),
   'DELAY_B4_RETRY'          : (0x0001,),
   'UNSAFE_MAX_LIMIT'        : (0x07ff,),
   'SEEK_NUMS'               : (0x00fa,),
   'RETRY_LIMIT'             : (0x005a,),
}
#Tuned Seek ID 5 cyls
prm_007_0076 = {
   'test_num'                : 7,
   'prm_name'                : 'prm_tunedSeek_7_0076',
   'timeout'                 : 1200*numHeads,
   'spc_id'                  : 14,
   'CWORD1'                  : (0x0400,),
   'START_CYL'               : (0x0002,0x3280,),
   'END_CYL'                 : (0x0002,0x3285,),
   'INITIAL_DELAY'           : (0x1225,),
   'FINAL_DELAY'             : (0x1225,),
   'DELAY_INCREMENT'         : (0x1225,),
   'SEEK_TYPE'               : (0x0025,),
   'TEST_HEAD'               : (0x00ff,),
   'DELAY_B4_RETRY'          : (0x0001,),
   'UNSAFE_MAX_LIMIT'        : (0x07ff,),
   'SEEK_NUMS'               : (0x00fa,),
   'RETRY_LIMIT'             : (0x005a,),
}
#Tuned Seek OD 0-30
prm_007_0270 = {
   'test_num'                : 7,
   'prm_name'                : 'prm_tunedSeek_7_0270',
   'timeout'                 : 1200 * numHeads,
   'spc_id'                  : 5,
   'CWORD1'                  : (0x0400,),
   'START_CYL'               : (0x0000,0x0000,),
   'END_CYL'                 : (0x0000,0x001e,),
   'INITIAL_DELAY'           : (0x0032,),
   'FINAL_DELAY'             : (0x0032,),
   'DELAY_INCREMENT'         : (0x0000,),
   'SEEK_TYPE'               : (0x0025,),
   'TEST_HEAD'               : (0x00ff,),
   'DELAY_B4_RETRY'          : (0x0001,),
   'UNSAFE_MAX_LIMIT'        : (0x07ff,),
   'SEEK_NUMS'               : (0x0064,),
   'RETRY_LIMIT'             : (0x07ff,),
}
#Tuned Seek OD 0-50
prm_007_0271 = {
   'test_num'                : 7,
   'prm_name'                : 'prm_tunedSeek_7_0271',
   'timeout'                 : 1200 * numHeads,
   'spc_id'                  : 6,
   'CWORD1'                  : (0x0400,),
   'START_CYL'               : (0x0000,0x0000,),
   'END_CYL'                 : (0x0000,0x0032,),
   'INITIAL_DELAY'           : (0x0032,),
   'FINAL_DELAY'             : (0x0032,),
   'DELAY_INCREMENT'         : (0x0000,),
   'SEEK_TYPE'               : (0x0025,),
   'TEST_HEAD'               : (0x00ff,),
   'DELAY_B4_RETRY'          : (0x0001,),
   'UNSAFE_MAX_LIMIT'        : (0x07ff,),
   'SEEK_NUMS'               : (0x0064,),
   'RETRY_LIMIT'             : (0x07ff,),
}
#Tuned Seek OD 0-100
prm_007_0272 = {
   'test_num'                : 7,
   'prm_name'                : 'prm_tunedSeek_7_0272',
   'timeout'                 : 1200*numHeads,
   'spc_id'                  : 7,
   'CWORD1'                  : (0x0400,),
   'START_CYL'               : (0x0000,0x0000,),
   'END_CYL'                 : (0x0000,0x0064,),
   'INITIAL_DELAY'           : (0x0032,),
   'FINAL_DELAY'             : (0x0032,),
   'DELAY_INCREMENT'         : (0x0000,),
   'SEEK_TYPE'               : (0x0025,),
   'TEST_HEAD'               : (0x00ff,),
   'DELAY_B4_RETRY'          : (0x0001,),
   'UNSAFE_MAX_LIMIT'        : (0x07ff,),
   'SEEK_NUMS'               : (0x0064,),
   'RETRY_LIMIT'             : (0x07ff,),
}
#Tuned Seek OD 0-300
prm_007_0273 = {
   'test_num'                : 7,
   'prm_name'                : 'prm_tunedSeek_7_0273',
   'timeout'                 : 1200 * numHeads,
   'spc_id'                  : 8,
   'CWORD1'                  : (0x0400,),
   'START_CYL'               : (0x0000,0x0000,),
   'END_CYL'                 : (0x0000,0x012c,),
   'INITIAL_DELAY'           : (0x0032,),
   'FINAL_DELAY'             : (0x0032,),
   'DELAY_INCREMENT'         : (0x0000,),
   'SEEK_TYPE'               : (0x0025,),
   'TEST_HEAD'               : (0x00ff,),
   'DELAY_B4_RETRY'          : (0x0001,),
   'UNSAFE_MAX_LIMIT'        : (0x07ff,),
   'SEEK_NUMS'               : (0x0064,),
   'RETRY_LIMIT'             : (0x07ff,),
}
#Tuned Seek Od 0-500
prm_007_0274 = {
   'test_num'                : 7,
   'prm_name'                : 'prm_tunedSeek_7_0274',
   'timeout'                 : 1200*numHeads,
   'spc_id'                  : 9,
   'CWORD1'                  : (0x0400,),
   'START_CYL'               : (0x0000,0x0000,),
   'END_CYL'                 : (0x0000,0x01f4,),
   'INITIAL_DELAY'           : (0x0032,),
   'FINAL_DELAY'             : (0x0032,),
   'DELAY_INCREMENT'         : (0x0000,),
   'SEEK_TYPE'               : (0x0025,),
   'TEST_HEAD'               : (0x00ff,),
   'DELAY_B4_RETRY'          : (0x0001,),
   'UNSAFE_MAX_LIMIT'        : (0x07ff,),
   'SEEK_NUMS'               : (0x0064,),
   'RETRY_LIMIT'             : (0x07ff,),
}
#Tuned Seek OD 0-1000
prm_007_0275 = {
   'test_num'                : 7,
   'prm_name'                : 'prm_tunedSeek_7_0275',
   'timeout'                 : 1200 * numHeads,
   'spc_id'                  : 10,
   'CWORD1'                  : (0x0400,),
   'START_CYL'               : (0x0000,0x0000,),
   'END_CYL'                 : (0x0000,0x03e8,),
   'INITIAL_DELAY'           : (0x0032,),
   'FINAL_DELAY'             : (0x0032,),
   'DELAY_INCREMENT'         : (0x0000,),
   'SEEK_TYPE'               : (0x0025,),
   'TEST_HEAD'               : (0x00ff,),
   'DELAY_B4_RETRY'          : (0x0001,),
   'UNSAFE_MAX_LIMIT'        : (0x07ff,),
   'SEEK_NUMS'               : (0x0064,),
   'RETRY_LIMIT'             : (0x07ff,),
}
#Tuned Seek OD 0-2000
prm_007_0276 = {
   'test_num'                : 7,
   'prm_name'                : 'prm_tunedSeek_7_0276',
   'timeout'                 : 1200 * numHeads,
   'spc_id'                  : 11,
   'CWORD1'                  : (0x0400,),
   'START_CYL'               : (0x0000,0x0000,),
   'END_CYL'                 : (0x0000,0x07d0,),
   'INITIAL_DELAY'           : (0x0032,),
   'FINAL_DELAY'             : (0x0032,),
   'DELAY_INCREMENT'         : (0x0000,),
   'SEEK_TYPE'               : (0x0025,),
   'TEST_HEAD'               : (0x00ff,),
   'DELAY_B4_RETRY'          : (0x0001,),
   'UNSAFE_MAX_LIMIT'        : (0x07ff,),
   'SEEK_NUMS'               : (0x0064,),
   'RETRY_LIMIT'             : (0x07ff,),
}
#Tuned Seek OD 0-3000
prm_007_0277 = {
   'test_num'                : 7,
   'prm_name'                : 'prm_tunedSeek_7_0277',
   'timeout'                 : 1200 * numHeads,
   'spc_id'                  : 12,
   'CWORD1'                  : (0x0400,),
   'START_CYL'               : (0x0000,0x0000,),
   'END_CYL'                 : (0x0000,0x0bb8,),
   'INITIAL_DELAY'           : (0x0032,),
   'FINAL_DELAY'             : (0x0032,),
   'DELAY_INCREMENT'         : (0x0000,),
   'SEEK_TYPE'               : (0x0025,),
   'TEST_HEAD'               : (0x00ff,),
   'DELAY_B4_RETRY'          : (0x0001,),
   'UNSAFE_MAX_LIMIT'        : (0x07ff,),
   'SEEK_NUMS'               : (0x0064,),
   'RETRY_LIMIT'             : (0x07ff,),
}
#Tuned Seek MD 72000-72030
prm_007_0370 = {
   'test_num'                : 7,
   'prm_name'                : 'prm_tunedSeek_7_0370',
   'timeout'                 : 1200 * numHeads,
   'spc_id'                  : 5,
   'CWORD1'                  : (0x0400,),
   'START_CYL'               : (0x0001,0x1940,),
   'END_CYL'                 : (0x0001,0x195e,),
   'INITIAL_DELAY'           : (0x0032,),
   'FINAL_DELAY'             : (0x0032,),
   'DELAY_INCREMENT'         : (0x0000,),
   'SEEK_TYPE'               : (0x0025,),
   'TEST_HEAD'               : (0x00ff,),
   'DELAY_B4_RETRY'          : (0x0001,),
   'UNSAFE_MAX_LIMIT'        : (0x07ff,),
   'SEEK_NUMS'               : (0x0064,),
   'RETRY_LIMIT'             : (0x07ff,),
}
#Tuned Seek MD 72000-72050
prm_007_0371 = {
   'test_num'                : 7,
   'prm_name'                : 'prm_tunedSeek_7_0371',
   'timeout'                 : 1200 * numHeads,
   'spc_id'                  : 6,
   'CWORD1'                  : (0x0400,),
   'START_CYL'               : (0x0001,0x1940,),
   'END_CYL'                 : (0x0001,0x1972,),
   'INITIAL_DELAY'           : (0x0032,),
   'FINAL_DELAY'             : (0x0032,),
   'DELAY_INCREMENT'         : (0x0000,),
   'SEEK_TYPE'               : (0x0025,),
   'TEST_HEAD'               : (0x00ff,),
   'DELAY_B4_RETRY'          : (0x0001,),
   'UNSAFE_MAX_LIMIT'        : (0x07ff,),
   'SEEK_NUMS'               : (0x0064,),
   'RETRY_LIMIT'             : (0x07ff,),
}
#Tuned Seek MD 72000-72100
prm_007_0372 = {
   'test_num'                : 7,
   'prm_name'                : 'prm_tunedSeek_7_0372',
   'timeout'                 : 1200 * numHeads,
   'spc_id'                  : 7,
   'CWORD1'                  : (0x0400,),
   'START_CYL'               : (0x0001,0x1940,),
   'END_CYL'                 : (0x0001,0x19a4,),
   'INITIAL_DELAY'           : (0x0032,),
   'FINAL_DELAY'             : (0x0032,),
   'DELAY_INCREMENT'         : (0x0000,),
   'SEEK_TYPE'               : (0x0025,),
   'TEST_HEAD'               : (0x00ff,),
   'DELAY_B4_RETRY'          : (0x0001,),
   'UNSAFE_MAX_LIMIT'        : (0x07ff,),
   'SEEK_NUMS'               : (0x0064,),
   'RETRY_LIMIT'             : (0x07ff,),
}
#Tuned Seek MD 72000-72300
prm_007_0373 = {
   'test_num'                : 7,
   'prm_name'                : 'prm_tunedSeek_7_0373',
   'timeout'                 : 1200 * numHeads,
   'spc_id'                  : 8,
   'CWORD1'                  : (0x0400,),
   'START_CYL'               : (0x0001,0x1940,),
   'END_CYL'                 : (0x0001,0x1a6c,),
   'INITIAL_DELAY'           : (0x0032,),
   'FINAL_DELAY'             : (0x0032,),
   'DELAY_INCREMENT'         : (0x0000,),
   'SEEK_TYPE'               : (0x0025,),
   'TEST_HEAD'               : (0x00ff,),
   'DELAY_B4_RETRY'          : (0x0001,),
   'UNSAFE_MAX_LIMIT'        : (0x07ff,),
   'SEEK_NUMS'               : (0x0064,),
   'RETRY_LIMIT'             : (0x07ff,),
}
#Tuned Seek MD 72000-72500
prm_007_0374 = {
   'test_num'                : 7,
   'prm_name'                : 'prm_tunedSeek_7_0374',
   'timeout'                 : 1200 * numHeads,
   'spc_id'                  : 9,
   'CWORD1'                  : (0x0400,),
   'START_CYL'               : (0x0001,0x1940,),
   'END_CYL'                 : (0x0001,0x1b34,),
   'INITIAL_DELAY'           : (0x0032,),
   'FINAL_DELAY'             : (0x0032,),
   'DELAY_INCREMENT'         : (0x0000,),
   'SEEK_TYPE'               : (0x0025,),
   'TEST_HEAD'               : (0x00ff,),
   'DELAY_B4_RETRY'          : (0x0001,),
   'UNSAFE_MAX_LIMIT'        : (0x07ff,),
   'SEEK_NUMS'               : (0x0064,),
   'RETRY_LIMIT'             : (0x07ff,),
}
#Tuned Seek MD 72000-73000
prm_007_0375 = {
   'test_num'                : 7,
   'prm_name'                : 'prm_tunedSeek_7_0375',
   'timeout'                 : 1200*numHeads,
   'spc_id'                  : 10,
   'CWORD1'                  : (0x0400,),
   'START_CYL'               : (0x0001,0x1940,),
   'END_CYL'                 : (0x0001,0x1d28,),
   'INITIAL_DELAY'           : (0x0032,),
   'FINAL_DELAY'             : (0x0032,),
   'DELAY_INCREMENT'         : (0x0000,),
   'SEEK_TYPE'               : (0x0025,),
   'TEST_HEAD'               : (0x00ff,),
   'DELAY_B4_RETRY'          : (0x0001,),
   'UNSAFE_MAX_LIMIT'        : (0x07ff,),
   'SEEK_NUMS'               : (0x0064,),
   'RETRY_LIMIT'             : (0x07ff,),
}
#Tuned Seek MD 72000-74000
prm_007_0376 = {
   'test_num'                : 7,
   'prm_name'                : 'prm_tunedSeek_7_0376',
   'timeout'                 : 1200 * numHeads,
   'spc_id'                  : 11,
   'CWORD1'                  : (0x0400,),
   'START_CYL'               : (0x0001,0x1940,),
   'END_CYL'                 : (0x0001,0x2110,),
   'INITIAL_DELAY'           : (0x0032,),
   'FINAL_DELAY'             : (0x0032,),
   'DELAY_INCREMENT'         : (0x0000,),
   'SEEK_TYPE'               : (0x0025,),
   'TEST_HEAD'               : (0x00ff,),
   'DELAY_B4_RETRY'          : (0x0001,),
   'UNSAFE_MAX_LIMIT'        : (0x07ff,),
   'SEEK_NUMS'               : (0x0064,),
   'RETRY_LIMIT'             : (0x07ff,),
}
#Tuned Seek MD 72000-75000
prm_007_0377 = {
   'test_num'                : 7,
   'prm_name'                : 'prm_tunedSeek_7_0377',
   'timeout'                 : 1200 * numHeads,
   'spc_id'                  : 12,
   'CWORD1'                  : (0x0400,),
   'START_CYL'               : (0x0001,0x1940,),
   'END_CYL'                 : (0x0001,0x24f8,),
   'INITIAL_DELAY'           : (0x0032,),
   'FINAL_DELAY'             : (0x0032,),
   'DELAY_INCREMENT'         : (0x0000,),
   'SEEK_TYPE'               : (0x0025,),
   'TEST_HEAD'               : (0x00ff,),
   'DELAY_B4_RETRY'          : (0x0001,),
   'UNSAFE_MAX_LIMIT'        : (0x07ff,),
   'SEEK_NUMS'               : (0x0064,),
   'RETRY_LIMIT'             : (0x07ff,),
}
#Tuned Seek ID 144000-144030
prm_007_0470 = {
   'test_num'                : 7,
   'prm_name'                : 'prm_tunedSeek_7_0470',
   'timeout'                 : 1200 * numHeads,
   'spc_id'                  : 5,
   'CWORD1'                  : (0x0400,),
   'START_CYL'               : (0x0002,0x3280,),
   'END_CYL'                 : (0x0002,0x329e,),
   'INITIAL_DELAY'           : (0x0032,),
   'FINAL_DELAY'             : (0x0032,),
   'DELAY_INCREMENT'         : (0x0000,),
   'SEEK_TYPE'               : (0x0025,),
   'TEST_HEAD'               : (0x00ff,),
   'DELAY_B4_RETRY'          : (0x0001,),
   'UNSAFE_MAX_LIMIT'        : (0x07ff,),
   'SEEK_NUMS'               : (0x0064,),
   'RETRY_LIMIT'             : (0x07ff,),
}
#Tuned Seek ID 144000-144050
prm_007_0471 = {
   'test_num'                : 7,
   'prm_name'                : 'prm_tunedSeek_7_0471',
   'timeout'                 : 1200 * numHeads,
   'spc_id'                  : 6,
   'CWORD1'                  : (0x0400,),
   'START_CYL'               : (0x0002,0x3280,),
   'END_CYL'                 : (0x0002,0x32b2,),
   'INITIAL_DELAY'           : (0x0032,),
   'FINAL_DELAY'             : (0x0032,),
   'DELAY_INCREMENT'         : (0x0000,),
   'SEEK_TYPE'               : (0x0025,),
   'TEST_HEAD'               : (0x00ff,),
   'DELAY_B4_RETRY'          : (0x0001,),
   'UNSAFE_MAX_LIMIT'        : (0x07ff,),
   'SEEK_NUMS'               : (0x0064,),
   'RETRY_LIMIT'             : (0x07ff,),
}
#Tuned Seek ID 144000-144100
prm_007_0472 = {
   'test_num'                : 7,
   'prm_name'                : 'prm_tunedSeek_7_0472',
   'timeout'                 : 1200 * numHeads,
   'spc_id'                  : 7,
   'CWORD1'                  : (0x0400,),
   'START_CYL'               : (0x0002,0x3280,),
   'END_CYL'                 : (0x0002,0x32e4,),
   'INITIAL_DELAY'           : (0x0032,),
   'FINAL_DELAY'             : (0x0032,),
   'DELAY_INCREMENT'         : (0x0000,),
   'SEEK_TYPE'               : (0x0025,),
   'TEST_HEAD'               : (0x00ff,),
   'DELAY_B4_RETRY'          : (0x0001,),
   'UNSAFE_MAX_LIMIT'        : (0x07ff,),
   'SEEK_NUMS'               : (0x0064,),
   'RETRY_LIMIT'             : (0x07ff,),
}
#Tuned Seek ID 144000-144300
prm_007_0473 = {
   'test_num'                : 7,
   'prm_name'                : 'prm_tunedSeek_7_0473',
   'timeout'                 : 1200*numHeads,
   'spc_id'                  : 8,
   'CWORD1'                  : (0x0400,),
   'START_CYL'               : (0x0002,0x3280,),
   'END_CYL'                 : (0x0002,0x33ac,),
   'INITIAL_DELAY'           : (0x0032,),
   'FINAL_DELAY'             : (0x0032,),
   'DELAY_INCREMENT'         : (0x0000,),
   'SEEK_TYPE'               : (0x0025,),
   'TEST_HEAD'               : (0x00ff,),
   'DELAY_B4_RETRY'          : (0x0001,),
   'UNSAFE_MAX_LIMIT'        : (0x07ff,),
   'SEEK_NUMS'               : (0x0064,),
   'RETRY_LIMIT'             : (0x07ff,),
}
#Tuned Seek ID 144000-144500
prm_007_0474 = {
   'test_num'                : 7,
   'prm_name'                : 'prm_tunedSeek_7_0474',
   'timeout'                 : 1200 * numHeads,
   'spc_id'                  : 9,
   'CWORD1'                  : (0x0400,),
   'START_CYL'               : (0x0002,0x3280,),
   'END_CYL'                 : (0x0002,0x3474,),
   'INITIAL_DELAY'           : (0x0032,),
   'FINAL_DELAY'             : (0x0032,),
   'DELAY_INCREMENT'         : (0x0000,),
   'SEEK_TYPE'               : (0x0025,),
   'TEST_HEAD'               : (0x00ff,),
   'DELAY_B4_RETRY'          : (0x0001,),
   'UNSAFE_MAX_LIMIT'        : (0x07ff,),
   'SEEK_NUMS'               : (0x0064,),
   'RETRY_LIMIT'             : (0x07ff,),
}
#Tuned Seek ID 144000-145000
prm_007_0475 = {
   'test_num'                : 7,
   'prm_name'                : 'prm_tunedSeek_7_0475',
   'timeout'                 : 1200 * numHeads,
   'spc_id'                  : 10,
   'CWORD1'                  : (0x0400,),
   'START_CYL'               : (0x0002, 0x3280,),
   'END_CYL'                 : (0x0002, 0x3668,),
   'INITIAL_DELAY'           : (0x0032,),
   'FINAL_DELAY'             : (0x0032,),
   'DELAY_INCREMENT'         : (0x0000,),
   'SEEK_TYPE'               : (0x0025,),
   'TEST_HEAD'               : (0x00ff,),
   'DELAY_B4_RETRY'          : (0x0001,),
   'UNSAFE_MAX_LIMIT'        : (0x07ff,),
   'SEEK_NUMS'               : (0x0064,),
   'RETRY_LIMIT'             : (0x07ff,),
}
#Tuned Seek ID 144000-146000
prm_007_0476 = {
   'test_num'                : 7,
   'prm_name'                : 'prm_tunedSeek_7_0476',
   'timeout'                 : 1200 * numHeads,
   'spc_id'                  : 11,
   'CWORD1'                  : (0x0400,),
   'START_CYL'               : (0x0002, 0x3280,),
   'END_CYL'                 : (0x0002, 0x3A50,),
   'INITIAL_DELAY'           : (0x0032,),
   'FINAL_DELAY'             : (0x0032,),
   'DELAY_INCREMENT'         : (0x0000,),
   'SEEK_TYPE'               : (0x0025,),
   'TEST_HEAD'               : (0x00FF,),
   'DELAY_B4_RETRY'          : (0x0001,),
   'UNSAFE_MAX_LIMIT'        : (0x07FF,),
   'SEEK_NUMS'               : (0x0064,),
   'RETRY_LIMIT'             : (0x07FF,),
}
#Tuned Seek ID 144000-147000
prm_007_0477 = {
   'test_num'                : 7,
   'prm_name'                : 'prm_tunedSeek_7_0477',
   'timeout'                 : 1200 * numHeads,
   'spc_id'                  : 12,
   'CWORD1'                  : (0x0400,),
   'START_CYL'               : (0x0002, 0x3280,),
   'END_CYL'                 : (0x0002, 0x3E38,),
   'INITIAL_DELAY'           : (0x0032,),
   'FINAL_DELAY'             : (0x0032,),
   'DELAY_INCREMENT'         : (0x0000,),
   'SEEK_TYPE'               : (0x0025,),
   'TEST_HEAD'               : (0x00FF,),
   'DELAY_B4_RETRY'          : (0x0001,),
   'UNSAFE_MAX_LIMIT'        : (0x07FF,),
   'SEEK_NUMS'               : (0x0064,),
   'RETRY_LIMIT'             : (0x07FF,),
}
# Now form a list of all of the parameters sets just defined
prm_tunedSeek_7 = [
   prm_007_0070,
   prm_007_0071,
   prm_007_0072,
   prm_007_0073,
   prm_007_0074,
   prm_007_0076,
   prm_007_0270,
   prm_007_0271,
   prm_007_0272,
   prm_007_0273,
   prm_007_0274,
   prm_007_0275,
   prm_007_0276,
   prm_007_0277,
   prm_007_0370,
   prm_007_0371,
   prm_007_0372,
   prm_007_0373,
   prm_007_0374,
   prm_007_0375,
   prm_007_0376,
   prm_007_0377,
   prm_007_0470,
   prm_007_0471,
   prm_007_0472,
   prm_007_0473,
   prm_007_0474,
   prm_007_0475,
   prm_007_0476,
   prm_007_0477,
]
###############################################################################
################################## Test 0010 ##################################
# Force Constant Calibration
fccCalPrm_10 = {           
   'test_num'                : 10,
   'prm_name'                : 'fccCalPrm_10',
   'timeout'                 : 10000,
   'spc_id'                  : 1,
   'CWORD1'                  : 0x0400,
   'CWORD2'                  : 0x0005,
   'RETRIES'                 : 6,
   'FC_DATA'                 : (0x32, 0x0F),
   'LIMIT2'                  : 300,     #326,
   'DELTA_LIMIT'             : 0x7FFF,
   'SEEK_LENGTH'             : (1000, 3200),
   'GAIN'                    : 50,
   'SEEK_ERR_LIMIT'          : 0x31F,
   'TEST_HEAD'               : 0,
}
###############################################################################
################################## Test 0011 ##################################
# Test Parameter sets used to enable/disable the various options
#Read RVFF register
prm_0011_read_RVFF = {       
   'test_num'                : 11,
   'prm_name'                : 'prm_0011_read_RVFF',
   'timeout'                 : 300,
   'CWORD1'                  : 0x0200,  #0x0200 = Read by SYM_OFFSET
   'SYM_OFFSET'              : 207,
   'NUM_LOCS'                : 0x0000,
   'ACCESS_TYPE'             : 2,
   'DblTablesToParse'        : 'P011_SV_RAM_RD_BY_OFFSET',
}
# Only touch lsb, which allows current to flow to VCM for this correction
prm_0011_enable_RVFF_current = {  
   'test_num'                : 11,
   'prm_name'                : 'prm_0011_enable_RVFF_current',
   'timeout'                 : 300,
   'CWORD1'                  : 0x0400,
   'SYM_OFFSET'              : 207,         # Symbol Offset
   'WR_DATA'                 : 0x0001,
   'MASK_VALUE'              : 0xFFFE,  #lsb for RVFF current
   'NUM_LOCS'                : 0x0000,
   'ACCESS_TYPE'             : 2,
}

prm_0011_shock_RVFF = {
   'test_num'                : 11,
   'prm_name'                : 'prm_0011_shock_RVFF',
   'timeout'                 : 300,
   'CWORD1'                  : 0x0400,
   'SYM_OFFSET'              : 207,         # Symbol Offset
   'WR_DATA'                 : 0x0200,
   'MASK_VALUE'              : 0x0000,
   'NUM_LOCS'                : 0x0000,
   'ACCESS_TYPE'             : 2,
}

prm_0011_disableshockmode = {
   'test_num'                : 11,
   'prm_name'                : 'prm_0011_disableshockmode',
   'timeout'                 : 300,
   'CWORD1'                  : 0x0400,
   'SYM_OFFSET'              : 242,         # Symbol Offset
   'WR_DATA'                 : 0x0000,
   'MASK_VALUE'              : 0x0000,
   'NUM_LOCS'                : 0x0000,
   'ACCESS_TYPE'             : 2,
}

prm_0011_enableshockmode = {
   'test_num'                : 11,
   'prm_name'                : 'prm_0011_enableshockmode',
   'timeout'                 : 300,
   'CWORD1'                  : 0x0400,
   'SYM_OFFSET'              : 242,         # Symbol Offset
   'WR_DATA'                 : 0x0001,
   'MASK_VALUE'              : 0x0000,
   'NUM_LOCS'                : 0x0000,
   'ACCESS_TYPE'             : 2,
}

prm_0011_enableSwot = {
   'test_num'                : 11,
   'prm_name'                : 'prm_0011_enableSwot',
   'timeout'                 : 300,
   'CWORD1'                  : 0x0400,
   'SYM_OFFSET'              : 242,         # Symbol Offset
   'WR_DATA'                 : 0x0001,
   'MASK_VALUE'              : 0x0000,
   'NUM_LOCS'                : 0x0000,
   'ACCESS_TYPE'             : 2,
}                         
                          
prm_0011_OST_150KTPI = {  
   'test_num'                : 11,
   'prm_name'                : 'prm_0011_OST_150KTPI',
   'timeout'                 : 600,
   'CWORD1'                  : 0x0400,
   'SYM_OFFSET'              : 234,         # Symbol Offset
   'WR_DATA'                 : 0x49D9,
   'MASK_VALUE'              : 0x0000,
}

loadPVDFeatures2Prm_11 = {
   'test_num'                : 11,
   'prm_name'                : 'LoadPVDFeatures2',
   'timeout'                 : 1000,
   'spc_id'                  : 1,
   'PARAM_0_4'               : (0x0B01, 0x0000, 0, 0, 0),  # Load PVD FEATURES_2 data into SRAM
}

ReadPVDFeatures2Bit4Prm_11 = {
   'test_num'                : 11,
   'prm_name'                : 'ReadPVDFeatures2Bit4',
   'timeout'                 : 1000,
   'spc_id'                  : 1,
   'CWORD1'                  : 0x0001,
   'START_ADDRESS'           : (0x500, 0x002A),            # Address to read bit 4 of FEATURES_2 table in VPD
   'END_ADDRESS'             : (0x500, 0x002A),
}                           
                            
getMaxCylViaAddrPrm_11 = {                                # USE ACCESS_TYPE 3 AND EXTENDED_MASK TO GET MAX_CYL AS 32 BIT VALUE
   'test_num'                : 11,
   'prm_name'                : 'GetMaxCylViaAddr',
   'timeout'                 : 1000,
   'spc_id'                  : 1,
   'CWORD1'                  : 0x0001,
   'ACCESS_TYPE'             : 3,
   'EXTENDED_MASK_VALUE'     : 0xFFFF,
}                           
                            
getMaxCylPrm_11 = {         
   'test_num'                : 11,
   'prm_name'                : 'GetMaxCyl',
   'timeout'                 : 1000,
   'spc_id'                  : 1,
   'CWORD1'                  : 0x0200,
   'SYM_OFFSET'              : 2,
   'ACCESS_TYPE'             : 0,
}                           
                            
ReadPVDDataPrm_11 = {       
   'test_num'                : 11,
   'prm_name'                : 'ReadPVDFeatures2Bit4',
   'timeout'                 : 1000,
   'spc_id'                  : 1,
   'CWORD1'                  : 0x4000,
   'VPD_DATA'                : (0, 5),
}                           
                            
getSymbolViaAddrPrm_11 = {                       # USE ACCESS_TYPE 3 AND EXTENDED_MASK TO GET MAX_CYL AS 32 BIT VALUE
   'test_num'                : 11,
   'prm_name'                : 'GetSymbolViaAddr',
   'timeout'                 : 1000,
   'spc_id'                  : 1,
   'CWORD1'                  : 0x0001,
   'ACCESS_TYPE'             : 3,
   'EXTENDED_MASK_VALUE'     : 0xFFFF,
}                           

getServoSymbolPrm_11 = {
   'base'                    : {
      'test_num'                : 11,
      'prm_name'                : 'getServoSymbolPrm',
      'timeout'                 : 1000,
      'spc_id'                  : 1,
      'CWORD1'                  : 0x0200,
      'ACCESS_TYPE'             : 0,
   },                     
   'SYM_OFFSET'              : {          
      'maxServoTrack'           : 2,
      'rpm'                     : 144,
      'servoWedges'             : 140,
      'arcTPI'                  : 142,
      'ostRatioAddr'            : 234,
      'PGAgain'                 : 132,
      'maxLogicalTrack'         : 247,
   }
}

VCATCHROMEON_11 = {
   'test_num'                : 11,
   'prm_name'                : 'Enable AGC Unsafe faults',
   'spc_id'                  : 1,
   'timeout'                 : 300,
   'CWORD1'                  : 1024,
   'SYM_OFFSET'              : 152,
   'MASK_VALUE'              : 4368,
   'WR_DATA'                 : 5,
   'NUM_LOCS'                : 0,
   'ACCESS_TYPE'             : 2,
}                          
                           
enableAGCUnsafes_11 = {    
   'test_num'                : 11,
   'prm_name'                : 'Enable AGC Unsafe faults',
   'spc_id'                  : 1,
   'CWORD1'                  : 0x0400,
   'SYM_OFFSET'              : 180,
   'MASK_VALUE'              : 0xFFFE,
   'WR_DATA'                 :  0x01,
}                          
                           
disableAGCUnsafes_11 = {   
   'test_num'                : 11,
   'prm_name'                : 'Disable AGC Unsafe faults',
   'spc_id'                  : 1,
   'CWORD1'                  : 0x0400,
   'SYM_OFFSET'              : 180,
   'MASK_VALUE'              : 0xFFFE,
   'WR_DATA'                 : 0x00,
}

enableSWDFaults_11 = {
   'test_num'                : 11,
   'prm_name'                : 'Enable SWD Write Faults', #Updates SAP
   'spc_id'                  : 1,
   'CWORD1'                  : 0x0400,
   'SYM_OFFSET'              : 101,
   'MASK_VALUE'              : 0xFFDF,
   'WR_DATA'                 : 0x20,
   }                       
                           
disableSWDFaults_11 = {    
   'test_num'                : 11,
   'prm_name'                : 'Disable SWD Write Faults', #Updates SAP
   'spc_id'                  : 1,
   'CWORD1'                  : 0x0400,
   'SYM_OFFSET'              : 101,
   'MASK_VALUE'              : 0xFFDF,
   'WR_DATA'                 : 0x00,
}

# Calls to disable and enable the shock sensor on a drive with
# SF3 code on it. Currently going to be used in ZAP
Disable_SF3_ShockSensor = {
   'test_num'                : 11,
   'prm_name'                : 'Disable_SF3_ShockSensor',
   'timeout'                 : 1000,
   'spc_id'                  : 1,
   'PARAM_0_4'               : (29039, 0, 0, 0, 0)
}                           
                            
Enable_SF3_ShockSensor = {  
   'test_num'                : 11,
   'prm_name'                : 'Enable_SF3_ShockSensor',
   'timeout'                 : 1000,
   'spc_id'                  : 1,
   'PARAM_0_4'               : (28783, 0, 0, 0, 0)
}                           
                            
enableLiveSensor_11 = {     
   'test_num'                : 11,
   'prm_name'                : 'Enable LiveSensor', #Updates SAP
   'spc_id'                  : 1,
   'CWORD1'                  : 0x0400,
   'SYM_OFFSET'              : 384,
   'MASK_VALUE'              : 0xFFFE,
   'WR_DATA'                 : 0x1,
}
disableLiveSensor_11 = {
   'test_num'                : 11,
   'prm_name'                : 'Disable LiveSensor', #Updates SAP
   'spc_id'                  : 1,
   'CWORD1'                  : 0x0400,
   'SYM_OFFSET'              : 384,
   'MASK_VALUE'              : 0xFFFE,
   'WR_DATA'                 : 0x0,
}                           
enableTASensor_11 = {       
   'test_num'                : 11,
   'prm_name'                : 'Disable LiveSensor', #Updates SAP
   'spc_id'                  : 1,
   'CWORD1'                  : 0x0400,
   'SYM_OFFSET'              : 384,
   'MASK_VALUE'              : 0xFFFB,
   'WR_DATA'                 : 0x4,
}                           
disableTASensor_11 = {      
   'test_num'                : 11,
   'prm_name'                : 'Disable LiveSensor', #Updates SAP
   'spc_id'                  : 1,
   'CWORD1'                  : 0x0400,
   'SYM_OFFSET'              : 384,
   'MASK_VALUE'              : 0xFFFB,
   'WR_DATA'                 : 0x0,
}

mdwCalState_11 = {
   'CalCompleteMask'         : 2**14,
   'read'                    : {
      'test_num'                : 11,
      'prm_name'                : 'mdwCalRead',
      'spc_id'                  : 1,
      'CWORD1'                  : 0x0200,
      'SYM_OFFSET'              : mdwCalCompleteOffset,    #  Symbol Offset
      'NUM_LOCS'                : 0,
      'timeout'                 : 120,
   },                      
   'calComplete'             : {          
      'test_num'                : 11,
      'prm_name'                : 'mdwCalComplete',
      'spc_id'                  : 1,
      'CWORD1'                  : 0x0400,
      'SYM_OFFSET'              : mdwCalCompleteOffset,    #  Symbol Offset
      'WR_DATA'                 : 0,
      'MASK_VALUE'              : ~2**14,
      'NUM_LOCS'                : 0,
      'timeout'                 : 120,
   },
   'calRequired'             : {
      'test_num'                : 11,
      'prm_name'                : 'mdwCalRequired',
      'spc_id'                  : 1,
      'CWORD1'                  : 0x0400,
      'SYM_OFFSET'              : mdwCalCompleteOffset,    #  Symbol Offset
      'WR_DATA'                 : 2**14,
      'MASK_VALUE'              : ~2**14,
      'NUM_LOCS'                : 0,
      'timeout'                 : 120,
   },
}

###############################################################################
################################## Test 0013 ##################################
#Test 13 TMFF Calibration
tmffCalPrm_13={
   'test_num'                : 13,
   'prm_name'                : 'tmffCalPrm_13_ServoParms',
   'timeout'                 : 200*numHeads,  #200*numHeads, #1000*numHeads,
   'spc_id'                  : 1,
   'START_CYL'               : (0x000,0x1700,),
   'END_CYL'                 : {
      'ATTRIBUTE' : 'PROC_CTRL9',
      'DEFAULT'   : '0',
      '0'         : (0xFFFF,0xFFFF,),
      '1'         : {'EQUATION':'dWord(int(self.dut.maxServoTrack*0.9))'}
      },
   'HEAD_RANGE'              : (0x00FF,),
   'REVS'                    : (1,),
   'RETRY_LIMIT'             : (16,),
   'CWORD1'                  : (0x0707,),
   'GAIN_LIMIT'              : (200,),
   'SEEK_DELAY'              : (5,),
   'LIMIT'                   : (12,),
   #'TEST_CYL' : (0x0001,0x4C08,),
}
if testSwitch.CHEOPSAM_LITE_SOC and not testSwitch.SCOPY_TARGET:  # temporary code for RLSCOPY DEMO in SKDC
   tmffCalPrm_13.update( { 'NUM_SAMPLES' : 40 } )
else:
   tmffCalPrm_13.update( { 'SEEK_STEP' : 5047 } )
###############################################################################
################################## Test 0025 ##################################
# Sweep tests - LUL test in ADV_SWEEP
lul_prm_025 = {
   'test_num'                : 25,
   'prm_name'                : 'lul_prm_025',
   'timeout'                 : 1200*numHeads,
   'spc_id'                  : 1,
   'CWORD1'                  : 0x0040,        # (0x0080,), # run lul test - bit6 = get LUL params from servo symbol table.
   'NUM_SAMPLES'             : (300,),        # how many times to run load/unload
   'DELAY_TIME'              : (1000,),       # delay between load/unload in ms
   'TIMER_OPTION'            : (30,),         # Timer0 interrupt interval in us
   'GAIN'                    : (32768,),      # 1/K_dac in bit/V, K_dac = 1/(2^15)in V/bit
   'GAIN2'                   : (490,),        # K_pa in mA/V, Rf_Rin_ratio / (Gs * Rs) *1000 = 1000 / (3 * 0.68)
   'SCALED_VAL'              : (17587,),      # Velocity_BitsPerIps * 1000 in bit/1000ips, millivolt_per_ips/adc_resolution=1000*Kt*adc_amplifiergain/VCM_pivot_to_gap/adc_resolution=1000*0.01295*5/1.31/(2.4/2^10)
   'RPM'                     : (167,),
}
if testSwitch.CHEOPSAM_LITE_SOC and testSwitch.IS_2D_DRV == 1:
   lul_prm_025.update({ 'CWORD1' : (0x8040,), }) # 0x8000 ABORT_ON_HI_I_OR_V
   lul_prm_025.update({ 'LIMIT2' : (290,), }) # unload max peak current limit
   lul_prm_025.update({ 'RETRY_COUNTER_MAX' : (8,), }) # 8 consecutive over limit unload current
   lul_prm_025['DblTablesToParse'] = ['P025_LOAD_UNLOAD_PARAMS']
if testSwitch.CHEOPSAM_LITE_SOC and testSwitch.IS_2D_DRV == 0:
   lul_prm_025.update({ 'CWORD1' : (0x8040,), }) # 0x8000 ABORT_ON_HI_I_OR_V
   lul_prm_025.update({ 'LIMIT' : (300,), }) # unload max peak current limit
   lul_prm_025.update({ 'RETRY_COUNTER_MAX' : (8,), }) # 8 consecutive over limit unload current
   lul_prm_025['DblTablesToParse'] = ['P025_LOAD_UNLOAD_PARAMS']

lul_prm_CheckReverseIPS_025 = {
   'test_num'                : 25,
   'prm_name'                : 'lul_prm_CheckReverseIPS_025',
   'timeout'                 : 1200*numHeads,
   'spc_id'                  : 20,
   'CWORD1'                  : 0x0060,        # (0x0080,), # run lul test - bit6 = get LUL params from servo symbol table, bit 5 = Enable Reverse IPS check
   'NUM_SAMPLES'             : (30,),         # how many times to run load/unload
   'DELAY_TIME'              : (1000,),       # delay between load/unload in ms
   'TIMER_OPTION'            : (30,),         # Timer0 interrupt interval in us
   'GAIN'                    : (32768,),      # 1/K_dac in bit/V, K_dac = 1/(2^15)in V/bit
   'GAIN2'                   : (490,),        # K_pa in mA/V, Rf_Rin_ratio / (Gs * Rs) *1000 = 1000 / (3 * 0.68)
   'SCALED_VAL'              : (17587,),      # Velocity_BitsPerIps * 1000 in bit/1000ips, millivolt_per_ips/adc_resolution=1000*Kt*adc_amplifiergain/VCM_pivot_to_gap/adc_resolution=1000*0.01295*5/1.31/(2.4/2^10)
   'RPM'                     : (167,),
   'REVERSE_IPS_LIMIT'       : (15,),    # Reverse ips limit value. This value will be divided by 10 in T25.
}

spin_dip_prm_025 = {
   'test_num'                : 25,
   'prm_name'                : 'spin_dip_prm_025',
   'timeout'                 : 1200*numHeads,
   'spc_id'                  : 10,
   'CWORD1'                  : (0x95C0,),     # (0x0080,), # run lul test - bit6 = get LUL params from servo symbol table.
   'NUM_SAMPLES'             : (10,),         # how many times to run load/unload
   'DELAY_TIME'              : (1000,),       # delay between load/unload in ms
   'TIMER_OPTION'            : (30,),         # Timer0 interrupt interval in us
   'GAIN'                    : (32768,),      # 1/K_dac in bit/V, K_dac = 1/(2^15)in V/bit
   'GAIN2'                   : (490,),        # K_pa in mA/V, Rf_Rin_ratio / (Gs * Rs) *1000 = 1000 / (3 * 0.68)
   'SCALED_VAL'              : (17587,),      # Velocity_BitsPerIps * 1000 in bit/1000ips, millivolt_per_ips/adc_resolution=1000*Kt*adc_amplifiergain/VCM_pivot_to_gap/adc_resolution=1000*0.01295*5/1.31/(2.4/2^10)
   'RPM'                     : (167,),
   'LIMIT'                   : (400,),        # Load Peak Current Limit in mA
   'LIMIT2'                  : (400,),        # Unload Peak Current Limit in mA
   'SPINDLE_DIP_LIMIT'       : (109,),   # Spindle dip limit
   'DblTablesToParse': ['P025_LOAD_UNLOAD_PARAMS'],
}

load_unload_profile_025 = {
   'test_num'                : 25,
   'prm_name'                : 'load_unload_profile_025',
   'timeout'                 : 1200*numHeads,
   'spc_id'                  : 30,
   'CWORD1'                  : (0x9540,),     # (0x0080,), # run lul test - bit6 = get LUL params from servo symbol table.
   'NUM_SAMPLES'             : (10,),         # how many times to run load/unload
   'DELAY_TIME'              : (1000,),       # delay between load/unload in ms
   'TIMER_OPTION'            : (30,),         # Timer0 interrupt interval in us
   'GAIN'                    : (32768,),      # 1/K_dac in bit/V, K_dac = 1/(2^15)in V/bit
   'GAIN2'                   : (490,),        # K_pa in mA/V, Rf_Rin_ratio / (Gs * Rs) *1000 = 1000 / (3 * 0.68)
   'SCALED_VAL'              : (17587,),      # Velocity_BitsPerIps * 1000 in bit/1000ips, millivolt_per_ips/adc_resolution=1000*Kt*adc_amplifiergain/VCM_pivot_to_gap/adc_resolution=1000*0.01295*5/1.31/(2.4/2^10)
   'RPM'                     : (167,),
   'LIMIT'                   : (400,),        # Load Peak Current Limit in mA
   'LIMIT2'                  : (400,),        # Unload Peak Current Limit in mA
   'SPINDLE_DIP_LIMIT'       : (109,),   # Spindle dip limit
}                         
                          
LULsweep_25 = {           
   'test_num'                : 25,
   'prm_name'                : 'LULsweep_25',
   'timeout'                 : 7500,
   'spc_id'                  : 1,
   'CWORD1'                  : 0x0200,      # high speed LUL without capturing current velocity profile
   'NUM_SAMPLES'             : 815,
   'DELAY_TIME'              : 100,         # time / ms  after each load or unload
   'TIMER_OPTION'            : 20,          # timer0 interupt duration / us
   'GAIN'                    : 32768,
   'GAIN2'                   : 1333,        # K_pa in mA/V
   'SCALED_VAL'              : 33572,       # velocity scaler bits / ips
   'RPM'                     : 225,         # unit conversion between spin (60*REFCLK_FREQ)/(TACH_PULSES_PER_REV*
   }

pre185_LULsweep_25 = {
   'test_num'                : 25,
   'prm_name'                : 'pre185_LULsweep_25',
   'timeout'                 : 1800,
   'spc_id'                  : 1,
   'CWORD1'                  : 0x0000,      # high speed LUL without capturing current velocity profile
   'NUM_SAMPLES'             : 20,
   'DELAY_TIME'              : 100,         # time / ms  after each load or unload
   'TIMER_OPTION'            : 20,          # timer0 interupt duration / us
   'GAIN'                    : 32768,
   'GAIN2'                   : 1333,        # K_pa in mA/V
   'SCALED_VAL'              : 16100,       # velocity scaler bits / ips
   'RPM'                     : 225,         # unit conversion between spin (60*REFCLK_FREQ)/(TACH_PULSES_PER_REV*
   }                        
                            
prm_SrvoActRetract_25 = {   
   'test_num'                : 25,
   'prm_name'                : 'prm_SrvoActRetract_25',
   'timeout'                 : 1200 * numHeads,
   'spc_id'                  : 1,
   'CWORD1'                  : 0,
   'TEST_CYL'                : (0xFFFF, 0xFFFF),
   'LOOP_CNT'                : 20,
   'SEEK_NUMS'               : 100,
   'SEEK_DELAY'              : 300,
   'GAIN'                    : (32768,),      # 1/K_dac in bit/V, K_dac = 1/(2^15)in V/bit
   'GAIN2'                   : (490,),        # K_pa in mA/V, Rf_Rin_ratio / (Gs * Rs) *1000 = 1000 / (3 * 0.68)
   'SCALED_VAL'              : (17587,),      # Velocity_BitsPerIps * 1000 in bit/1000ips, millivolt_per_ips/adc_resolution=1000*Kt*adc_amplifiergain/VCM_pivot_to_gap/adc_resolution=1000*0.01295*5/1.31/(2.4/2^10)
}

prm_Latch_Unlatch_25 = {
   'test_num'                : 25,
   'prm_name'                : 'prm_Latch_Unlatch_25',
   'timeout'                 : 1200,
   'spc_id'                  : 1,
   'CWORD1'                  : 14,
   'LOOP_CNT'                : 20,
   'MIN_CAND'                : -32768,
   'SEEK_DELAY'              : 300,
}                           
                            
PreLoadUnloadPrm_25 = {     
   'test_num'                : 25,
   'prm_name'                : 'PreLoadUnloadPrm_25',
   'timeout'                 : 1200 * numHeads,
   'spc_id'                  : 1,
   'CWORD1'                  : 0x1400,
   'NUM_SAMPLES'             : 100,
   'DELAY_TIME'              : 100,         # time / ms  after each load or unload
   'TIMER_OPTION'            : 21,          # timer0 interupt duration / us
   'GAIN'                    : 32768,
   'GAIN2'                   : 1507,        # K_pa in mA/V
   'SCALED_VAL'              : 33572,       # velocity scaler bits / ips
   'RPM'                     : 1800,        # unit conversion between spin (60*REFCLK_FREQ)/(TACH_PULSES_PER_REV*
   'MIN_UNLD_VEL_THRESH'     : 0,
}                           

LoadUnloadPrm_25 = {
   'test_num'                : 25,
   'prm_name'                : 'LoadUnloadPrm_25',
   'timeout'                 : 1200 * numHeads,
   'spc_id'                  : 1,
   'CWORD1'                  : 0x1400,
   'NUM_SAMPLES'             : 100,
   'DELAY_TIME'              : 100,         # time / ms  after each load or unload
   'TIMER_OPTION'            : 21,          # timer0 interupt duration / us
   'GAIN'                    : 32768,
   'GAIN2'                   : 1507,        # K_pa in mA/V
   'SCALED_VAL'              : 33572,       # velocity scaler bits / ips
   'RPM'                     : 1800,         # unit conversion between spin (60*REFCLK_FREQ)/(TACH_PULSES_PER_REV*
   'MIN_UNLD_VEL_THRESH'     : 0,
}

LoadUnloadPrmStickyCS_25 = LoadUnloadPrm_25.copy()
FailProcLoadUnloadPrm_25 = {
   'test_num'                : 25,
   'prm_name'                : 'FailProcLoadUnloadPrm_25',
   'timeout'                 : 600,
   'spc_id'                  : 1,
   'CWORD1'                  : 0x1400,
   'NUM_SAMPLES'             : 100,
   'DELAY_TIME'              : 100,         # time / ms  after each load or unload
   'TIMER_OPTION'            : 21,          # timer0 interupt duration / us
   'GAIN'                    : 32768,
   'GAIN2'                   : 1507,        # K_pa in mA/V
   'SCALED_VAL'              : 16945,       # velocity scaler bits / ips
   'RPM'                     : 1800,         # unit conversion between spin (60*REFCLK_FREQ)/(TACH_PULSES_PER_REV*
   'MIN_UNLD_VEL_THRESH'     : 0,
}
###############################################################################
################################## Test 0030 ##################################
#=== SeaSweep Prms (2) - Start
NOMINAL_TOTAL_DATA_CYL = 15160
BUTTERFLY_NO_OF_TEST_TRKS = int(NOMINAL_TOTAL_DATA_CYL * 0.20)

adv_sweep_prm = {
   'FLAWSCAN_NUM_TEST_TRKS'  : 20000,
   'SEEK_GUARD_BAND'         : 4000,
}

direct_write_seek_prm_030 = {
   'test_num'                : 30,
   'prm_name'                : 'direct_write_seek_prm_030',
   'timeout'                 : 120,
   'spc_id'                  : 3,
   'CWORD1'                  : (0x0023,),
   'BIT_MASK'                : (0,0),
   'START_CYL'               : (0x0000,0x0000,),
   'END_CYL'                 : (0x0000,0x0000,),
   'PASSES'                  : (1,),
   'CWORD2'                  : (0xBABE,),
   'TIME'                    : (0,0xffff,0xffff,),
}

full_stroke_random_sweep_prm_030 = {
   'test_num'                : 30,
   'prm_name'                : 'full_stroke_random_sweep_prm_030',
   'timeout'                 : 1200*numHeads,
   'spc_id'                  : 4,
   'CWORD1'                  : (0x0324,),
   'START_CYL'               : (0x0000,0x0000,),
   'END_CYL'                 : (0xffff,0xffff,),
   'PASSES'                  : (35000,),
   'CWORD2'                  : (0xBABE,),
   'TIME'                    : (0,0xffff,0xffff,),
   'SKIP_ON_FAIL'            : (),
   'DblTablesToParse':['P030_SEEK_SETTLE_DISTY'],
}                           
                            
butterfly_sweep_prm_030 = { 
   'test_num'                : 30,
   'prm_name'                : 'butterfly_sweep_prm_030',
   'timeout'                 : 1800*numHeads,
   'spc_id'                  : 3,
   'CWORD1'                  : (0x022B,),
   'START_CYL'               : (0x0001,0x359D,),
   'END_CYL'                 : (0x0001,0xEF62,),
   'PASSES'                  : (8,),
   'CWORD2'                  : (0xBABE,),
   'TIME'                    : (0,0xffff,0xffff,),
   'SKIP_ON_FAIL'            : (),
}

full_stroke_two_point_sweep = {
   'test_num'                : 30,
   'prm_name'                : 'full_stroke_two_point_sweep',
   'timeout'                 : 1500*numHeads,
   'spc_id'                  : 2,
   'CWORD1'                  : (0x0023,),
   'BIT_MASK'                : (0,0),
   'START_CYL'               : (0x0000,0x0000,),
   'END_CYL'                 : (0xffff,0xffff,),
   'PASSES'                  : (16000,),
   'CWORD2'                  : (0xBABE,),
   'TIME'                    : (0,0xffff,0xffff,),
   'SKIP_ON_FAIL'            : (),
}
#=== SeaSweep Prms (2) - End
powerOnRetract_11 = {
   'test_num'                : 11,
   'prm_name'                : 'Power on hardware retract',
   'timeout'                 : 1000,
   'spc_id'                  : 1,
   'PARAM_0_4'               : (0x0E00, 1, 0, 0, 0),
}                           
                            
prm_030_random_write = {    
   'test_num'                : 30,
   'prm_name'                : 'prm_030_random_write',
   'timeout'                 : 1200 * numHeads,
   'spc_id'                  : 1,
   'CWORD1'                  : 0x0324,
   'START_CYL'               : (0x0000, 0x0000),
   'END_CYL'                 : (0x0000, 150000),
   'PASSES'                  : 1000,
   'CWORD2'                  : 0xBABE,
   'TIME'                    : (0, 0xFFFF, 200),
}                           
                            
prm_030_random_read = {     
   'test_num'                : 30,
   'prm_name'                : 'prm_030_random_read',
   'timeout'                 : 1200 * numHeads,
   'spc_id'                  : 1,
   'CWORD1'                  : 0x0314,
   'START_CYL'               : (0x0000, 0x0000),
   'END_CYL'                 : (0x0000, 150000),
   'PASSES'                  : 1000,
   'CWORD2'                  : 0xBABE,
   'TIME'                    : (0, 0xFFFF, 200),
}                         
                          
prm_030_full_write = {    
   'test_num'                : 30,
   'prm_name'                : 'prm_030_full_write',
   'timeout'                 : 1200 * numHeads,
   'spc_id'                  : 1,
   'CWORD1'                  : 0x0123,
   'START_CYL'               : (0x0000, 0x0000),
   'END_CYL'                 : (0x0000, 150000),
   'PASSES'                  : 1000,
   'CWORD2'                  : 0xBABE,
   'TIME'                    : (0, 0xFFFF, 200),
}

prm_030_full_read = {
   'test_num'                : 30,
   'prm_name'                : 'prm_030_full_read',
   'timeout'                 : 1200 * numHeads,
   'spc_id'                  : 1,
   'CWORD1'                  : 0x0113,
   'START_CYL'               : (0x0000, 0x0000),
   'END_CYL'                 : (0x0000, 150000),
   'PASSES'                  : 1000,
   'CWORD2'                  : 0xBABE,
   'TIME'                    : (0, 0xFFFF, 200),
}
###############################################################################
################################## Test 0031 ##################################
readThermalPrm_31 = {
   'test_num'                : 31,
   'prm_name'                : 'readThermalPrm_31',
   'spc_id'                  : 1,
   'RAW_MAX_SIN'             : 0x7FFF,
   'RAW_MAX_COS'             : 0x7FFF,
   'RAW_MAX_DC_OFFSET'       : 0x7FFF,
   'SEEK_RETRY_LIMIT'        : 0x2DB4,
   'HD_SKEW_LENGTH'          : 4,
   'TIMING_ERR_LIM'          : 0x7FFF,
   'timeout'                 : 1800,
}
###############################################################################
################################## Test 0032 ##################################
svo_Scan_32 = {        # Seek test: random write
   'base'                    : {
      'test_num'                : 32,
      'prm_name'                : 'svo_Scan_32',
      'spc_id'                  : 1,
      'SEEK_TYPE'               : 0x25,
      'START_CYL'               : (0x0000, 0x0000),
      'END_CYL'                 : (0x0000, 0x03E8),
      'PASSES'                  : 2,
      'TIME'                    : (0xFFFF, 0xFFFF, 0xA),
      'SEEK_TIME'               : (0xFFFF, 0xFFFF, 0x6),
   },
   'modes'                  : {
      'read'                   : 0x115,
      'format'                 : 0x105,
      'write'                  : 0x125,
   }
}
###############################################################################
################################## Test 0033 ##################################
pesMeasurePrm_33 = {
  'test_num'                 : 33,
  'prm_name'                 :'pesMeasurePrm_33',
  'spc_id'                   : 1,
  'TEST_CYL'                 : (0,0,),
  'END_CYL'                  : (0,110,),
  'TEST_HEAD'                : (0xFF,),
  'REVS'                     : (20,), # was 8. to get True RRO
  'DELTA_NRRO_LIMIT'         : (0x0050,),
  'CWORD1'                   : (0x0002,), #turn on retry on another cyl
  'SEEK_TYPE'                : (0x25,),
  'DELAY_TIME'               : (0,),
  'REPORT_OPTION'            : (1,),
  'MIN_NRRO_LIMIT'           : (0x7fff,),
  'MAX_NRRO_LIMIT'           : (0x7fff,),
  'MAX_RRO_LIMIT'            : (0x7fff,),
  'MAX_RO_LIMIT'             : (0x7fff,),
  'S_OFFSET'                 : (0,),
  'RETEST_DELAY'             : (0,),
  'NUM_SAMPLES'              : (100,),
  'timeout'                  : 1500,
  'RETEST_UNSAFE_LMT'        : (200,),
  'RETRY_INCR'               : (10,),
}
###############################################################################
################################## Test 0034 ##################################
NrroLinearityPrm_34 = {
   'base'                    : {
      'test_num'                : 34,
      'prm_name'                : 'NrroLinearityPrm_34_ServoParms',
      'timeout'                 : 1800,
      'spc_id'                  : 1,
   },
   'trackList'               : [100, 37200, 0x122A0]
}
###############################################################################
################################## Test 0037 ##################################
autoRPS_Prm_37 = {
   'test_num'                : 37,
   'prm_name'                : 'test 37 rotational positional sort',
   'timeout'                 : 7200, # 2 hrs for now
   'spc_id'                  : 1,
   'SEEK_NUMS'               : 16,
   'SEEK_DELAY'              : 2,
   'TIMER_OPTION'            : 0,
   'REPORT_OPTION'           : 1,
   'SEEK_ERR_LIMIT'          : 1000,
   'UPDATE_ETF'              : 1,
   'RD_CONST_COEFF'          : 300,
   'RD_STD_LIMIT'            : 400,
   'WRT_CONST_COEFF'         : 300,
   'WRT_STD_LIMIT'           : 400,
   'FAIL_SAFE'               : (),
}
###############################################################################
################################## Test 0043 ##################################
headSkewCalPrm_43 = {
   'test_num'                : 43,
   'prm_name'                : 'headSkewCalPrm_34',
   'timeout'                 : 300*numHeads,     #1000*numHeads,
   'spc_id'                  : 1,
   'SEEK_STEP'               : (10,),
   'ZETA_1'                  : (8,-16,),  #was 14,-14
   'LOOP_CNT'                : (30,),
   'NO_TMD_LMT'              : (18,),
   'RETRY_LIMIT'             : (4,),
   'SEEK_NUMS'               : (12,),
   'CWORD1'                  : (0x0003,),
   'GAIN_DELTA_LIM'          : (6127), #double clk for stingray
   'CSM_START_DELAY'         : (500),
}                         

radialCalPrm_43 = {
  'test_num'                 : 43,
  'prm_name'                 : 'radialCalPrm_43',
  'timeout'                  : 800*numHeads,   #7200,
  'MARGIN_LIMIT'             : {
      'ATTRIBUTE' : 'PROC_CTRL9',
      'DEFAULT'   : '0',
      '0'         : 0x0103,
      '1'         : 0x010A,
      },
  'CWORD1'                   : (0x3007,),
  'FREQUENCY'                : (133,),
  'TIMER_OPTION'             : (12,),
  'NUM_SAMPLES'              : (20,),
  'LIMIT'                    : (289,),
}
###############################################################################
################################## Test 0045 ##################################
srvSectorOffsetPrm_45 = {
   'test_num'                : 45,
   'prm_name'                : 'srvSectorOffsetPrm_45',
   'timeout'                 : 1000 * numHeads,
   'spc_id'                  : 1,
   'LOOP_CNT'                : 8,
   'RETRY_LIMIT'             : 8,
   'NUM_SAMPLES'             : 0,
   'INTERVAL_SIZE'           : 25,
   'CWORD1'                  : 0x000F,
   'REVS'                    : 3, # default is 20, too many here
   'SEEK_STEP'               : 500,
}
###############################################################################
################################## Test 0046 ##################################
CRRO_IRRO_Prm_46 = {
   'test_num'                : 46,
   'prm_name'                : 'CRRO_IRRO_Prm_046',
   'timeout'                 : 1200 * numHeads,
   'spc_id'                  : 1,
   'TRACK_LIMIT'             : (0x0032,),
   'REVS'                    : (0x0064,),
   'HEAD_RANGE'              : (0x00ff,),
   'CWORD1'                  : (0x0002,),
}

CRRO_IRRO_RealMode_Prm_46 = CRRO_IRRO_Prm_46.copy()
CRRO_IRRO_RealMode_Prm_46.update({
   'prm_name'                : 'CRRO_IRRO_RealMode_Prm_046',
   'CWORD1'                  : (0x0802,),
   })
###############################################################################
################################## Test 0047 ##################################
# Test 47 VCAT AC Cal audit reporting
vCatCal_Internal_47 = {
   'test_num'                : 47,
   'prm_name'                : 'vCatCal_Internal_47',
   'timeout'                 : 2000 * numHeads,
   'spc_id'                  : 1,
   'retryECList'             : [11216, 11049],
   'retryCount'              : 2,
   'retryMode'               : POWER_CYCLE_RETRY,
   'CWORD1'                  : 0x0401,
   'CWORD2'                  : 0x0010, # enable single state T47
   'SEEK_DELAY'              : 640,
   'LIMIT'                   : 66,                # Eccentricity limit: 24/10 = 2.4 (LIMIT/DIVISOR)
   'DIVISOR'                 : 100,
   'RETRY_LIMIT'             : 3,
   'NUM_SAMPLES'             : 40,
   'REVS'                    : 200,
   'PES_REVS'                : 600,
   'LIMIT32'                 : (0, 18,),
   'MARGIN_LIMIT'            : {
      'ATTRIBUTE' : 'PROC_CTRL9',
      'DEFAULT'   : '0',
      '0'         : 0x0505,
      '1'         : 0x050A,
      },
}

if testSwitch.KARNAK:
   vCatCal_Internal_47.update( {'SEEK_DELAY' : 1200, } )

vCatCal_02Prm_47 = {
   'test_num'                : 47,
   'prm_name'                : 'vCatCal_02Prm_47_ServoParms',
   'timeout'                 : 2000 * numHeads,
   'spc_id'                  : 1,
   'CWORD1'                  : 0x2018,
}

vCatGoVirtualPrm_47 = {          # vCatGoVirtual, chrome off
   'test_num'                : 47,
   'prm_name'                : 'vCatGoVirtualPrm_47',
   'timeout'                 : 2000 * numHeads,
   'spc_id'                  : 0,
   'TEST_CYL'                : (0, 30000),
   'CWORD1'                  : 0x0040,
}                          
                           
vCatOn_47 = {              
   'test_num'                : 47,
   'prm_name'                : 'vCatOn_47',
   'timeout'                 : 1000 * numHeads,
   'spc_id'                  : 0,
   'CWORD1'                  : 0x0240,
}                          
                           
vCatGoRealPrm_47 = {              # VCAT Go Real, chrome off
   'test_num'                : 47,
   'prm_name'                : 'vCatGoRealPrm_47',
   'timeout'                 : 2000 * numHeads,
   'spc_id'                  : 1,
   'TEST_CYL'                : (0, 30000),
   'CWORD1'                  : 0x0120,
}                          
                           
vCatGoRealNoSAPPrm_47 = {         # VCAT Go Real, chrome off, no SAP update
   'test_num'                : 47,
   'prm_name'                : 'vCatGoRealNoSAPPrm_47',
   'timeout'                 : 2000 * numHeads,
   'spc_id'                  : 1,
   'TEST_CYL'                : (0, 30000),
   'CWORD1'                  : 0x1120,
}
###############################################################################
################################## Test 0052 ##################################
zgsPrm_52 = {
   'test_num'                : 52,
   'prm_name'                : 'zgsPrm_52',
   'timeout'                 : 100,
   'spc_id'                  : 1,
}
###############################################################################
################################## Test 0056 ##################################
enableHiBWController_Dual_AFH = {
   'test_num'                : 56,
   'prm_name'                : 'Enable High BW Controller for AFH',
   'spc_id'                  : 1,
   'CWORD1'                  : 0x7002,
   'LOOP_CNT'                : 1,
}

if testSwitch.FE_0122163_357915_DUAL_STAGE_ACTUATOR_SUPPORT:
   if testSwitch.FE_0112192_345334_ADD_T56_FOR_PZT_CAL:
      enableHiBWController_Dual_Cal = {
         'test_num'                : 56,
         'prm_name'                : 'Enable High BW Controller',
         'spc_id'                  : 1,
      }
      enableHiBWController_Single_Cal = {
         'test_num'                : 56,
         'prm_name'                : 'Enable High BW Controller',
         'spc_id'                  : 1,
      }
      enableHiBWController_Dual = {
         'test_num'                : 56,
         'prm_name'                : 'Enable High BW Controller',
         'spc_id'                  : 1,
      }
      enableHiBWController_Single = {
         'test_num'                : 56,
         'prm_name'                : 'Enable High BW Controller',
         'spc_id'                  : 1,
      }
   else:
      enableHiBWController_Single = {
         'test_num'                : 11,
         'prm_name'                : 'Enable High BW Controller',
         'spc_id'                  : 1,
         'SYM_OFFSET'              : 6,
         'WR_DATA'                 : 7
      }
      enableHiBWController_Dual = {
         'test_num'                : 11,
         'prm_name'                : 'Enable High BW Controller',
         'spc_id'                  : 1,
         'SYM_OFFSET'              : 6,
         'WR_DATA'                 : 7
      }
else:
   enableHiBWController = {
      'test_num'                : 11,
      'prm_name'                : 'Enable High BW Controller',
      'spc_id'                  : 1,
      'CWORD1'                  : 0x0400,
      'SYM_OFFSET'              : 6,
      'WR_DATA'                 : 6,
   }

prm_56_PZT_cal_SKDC_SERVO_TEST = {
   'test_num'                : 56,
   'prm_name'                : 'SKDC_PZT_Cal_56',
   'LOOP_CNT'                : 10,
   'spc_id'                  : 1,
   'MAXIMUM'                 : 11703,
   'MINIMUM'                 : 3261,
   'timeout'                 : 600,
   'CWORD1'                  : 4370
}
###############################################################################
################################## Test 0057 ##################################
prm_57_VCM_Offset_Screen = {
   'test_num'                : 57,
   'prm_name'                : 'prm_57_VCM_Offset_Screen',
   'timeout'                 : 300,
   'spc_id'                  : 1,
   'CWORD1'                  : 0x0009,
   'NUM_READS'               : 100,
   'BIAS_AVG'                : 0x2000,
   'DELAY_TIME'              : 10,
   'LIMIT'                   : 40,
}

if (testSwitch.DISABLE_VCM_OFFSET_SCREEN):
   prm_57_VCM_Offset_Screen['test_num'] = 'NOP'
###############################################################################
################################## Test 0064 ##################################
prm_64_servo_pad = {
   'test_num'                : 64,
   'prm_name'                : 'prm_64_servo_pad',
   'timeout'                 : 36000,
   'CWORD1'                  : 0x0108,   # Disable REPORT_ADDED_FLAWS (0x8000) and DISPLAY_SFT (0x0002)
   'SET_REG01'               : {
      'ATTRIBUTE'               : 'CAPACITY_CUS',
      'DEFAULT'                 : '500G_OEM1B',
      '1000G_OEM1B'             : (10, 5),
      '1000G_STD'               : (10, 2),
      '750G_OEM1B'              : (10, 5),
      '750G_STD'                : (10, 2),
      '2000G_SBS'               : (10, 2), 
      '1500G_SBS'               : (10, 2), 
      '1000G_SBS'               : (10, 2),
      '500G_SBS'                : (10, 2),
      '500G_OEM1B'              : (10, 5),
      '500G_STD'                : (10, 2),
      '320G_STD'                : (10, 2),
   },
}

prm_64_isolated_servo_pad = {
   'test_num'                : 64,
   'prm_name'                : 'prm_64_isolated_servo_pad',
   'timeout'                 : 36000,
   'CWORD1'                  : 0x0400,
}

prm_64_pad_mc_zone_boundary = {
   'test_num'                : 64,
   'prm_name'                : 'prm_64_pad_mc_zone_boundary',
   'timeout'                 : 3600,
   'CWORD1'                  : 0x8001,
   'NUM_TRACKS_PER_ZONE'     : 5,
}
###############################################################################
################################## Test 0073 ##################################
ClearMDWOffset_73 = {
   'test_num'                : 73,
   'prm_name'                : 'ClearMDWOffset_73',
   'timeout'                 : 2400,
   'spc_id'                  : 100,
   'CWORD1'                  : (0x3,),     # Bit 0 : Run MDWCAL Offset, Bit 1 : Enable Search Mode, Bit 2 : Enable debug data report
   'MAX_TIME_LIMIT'          : 40,
   'ERR_THRSH'               : (6000,6000,200),
}                           
                            
ClearMDWOffset_73_1 = {     
   'test_num'                : 73,
   'prm_name'                : 'ClearMDWOffset_73_1',
   'timeout'                 : 2400,
   'spc_id'                  : 200,
   'CWORD1'                  : (0x1,),     # Bit 0 : Run MDWCAL Offset, Bit 1 : Enable Search Mode, Bit 2 : Enable debug data report
   'MAX_TIME_LIMIT'          : 40,
   'ERR_THRSH'               : (6000,200,200),
   'PREAMBLE_CYCLE'          : (0,0,0,0),
   'FREQ'                    : 120,
   'ERR_AC_THRSH'            : {
      'ATTRIBUTE': 'BG',
      'DEFAULT'  : 'OEM1B',
      'OEM1B'    : (80, 400),
      'SBS'      : (310, 400), # Default value is (80, 400)
      },
}
if testSwitch.CHEOPSAM_LITE_SOC:
   ClearMDWOffset_73_1.update( { "PREAMBLE_CYCLE" : (43,43,43,43), } )
   ClearMDWOffset_73_1.update( { "FREQ" : (11980,), } )
if testSwitch.SCOPY_TARGET:   # temporary code for RLSCOPY DEMO in SKDC
   ClearMDWOffset_73_1.pop("PREAMBLE_CYCLE")
   ClearMDWOffset_73_1.pop("FREQ")
if not testSwitch.CHEOPSAM_LITE_SOC:
   ClearMDWOffset_73_1.pop("PREAMBLE_CYCLE")
   ClearMDWOffset_73_1.pop("FREQ")
   ClearMDWOffset_73_1.pop("ERR_AC_THRSH")
   
ClearMDWOffset_73_2 = {
   'test_num'                : 73,
   'prm_name'                : 'ClearMDWOffset_73_2',
   'timeout'                 : 2400,
   'spc_id'                  : 300,
   'CWORD1'                  : (0x8001,),     # Bit 0 : Run MDWCAL Offset, Bit 1 : Enable Search Mode, Bit 2 : Enable debug data report
   'MAX_TIME_LIMIT'          : 40,
   'ERR_THRSH'               : (6000,200,200),
   'ERR_AC_THRSH'            : {
      'ATTRIBUTE': 'BG',
      'DEFAULT'  : 'OEM1B',
      'OEM1B'    : (100,2000),
      'SBS'      : (310,2000),
      },
   'PREAMBLE_CYCLE'          : (0,0,0,0),
   'FREQ'                    : 120,
}
if testSwitch.CHEOPSAM_LITE_SOC:
   ClearMDWOffset_73_2.update( { "PREAMBLE_CYCLE" : (43,43,43,43), } )
   ClearMDWOffset_73_2.update( { "FREQ" : (11980,), } )

ZoneBoundaryCal_vcatOn_73 = {
   'test_num'                : 73,
   'prm_name'                : 'ZoneBoundaryCal_vcatOn_73',
   'timeout'                 : 3600,
   'spc_id'                  : 200,
   'CWORD1'                  : {
      'ATTRIBUTE'               : 'MARVELL_SRC',
      'DEFAULT'                 : 1,
      0                         : (0xD6,),
      1                         : (0x256,),
   },
   'FREQ'                    : 120,
}

ZoneBoundaryCal_73 = {
   'test_num'                : 73,
   'prm_name'                : 'ZoneBoundaryCal_73',
   'timeout'                 : 3600,
   'spc_id'                  : 200,
   'CWORD1'                  : (0x56,),         # Bit 1 : Enable Search Mode, Bit 2 : Enable debug data report, Bit 4 : Run Zone Boundary Cal, Bit 6 : Update Zone Servo Tracks to servo ram
   'FREQ'                    : 120,
}

PRM_SYNC_ZONE_BOUNDARY_73 = {
   'test_num'                : 73,
   'prm_name'                : 'PRM_SYNC_ZONE_BOUNDARY_73',
   'timeout'                 : 3600,
   'spc_id'                  : 200,
   'CWORD1'                  : 0x2000,          # Bit 13: Sync zone boundary to VBAR
}
###############################################################################
################################## Test 0097 ##################################
LULRandomWrite_97 = {
   'test_num'                : 97,
   'prm_name'                : 'LULRandomWrite_97',
   'timeout'                 : 3600 + (3600 * numHeads),
   'spc_id'                  : 1,
   'CWORD1'                  : 0x0000,            # No dwell
   'LOOP_CNT'                : 500,
   'BAND_SIZE'               : 100,
   'OD_OFFSET'               : 500,               # OD band offset relative to min cyl
   'ID_OFFSET'               : 100,               # ID band offset from max cyl
   'TLEVEL'                  : 16,
   'DELAY_TIME'              : 300,               # Delay time between each LUL command / ms
   'TIMER_OPTION'            : 20,                # Coefficient spec'd by servo regarding LUL timing
   'GAIN'                    : 32768,
   'GAIN2'                   : 1333,
   'SCALED_VAL'              : 33572,
   'RPM'                     : 225,
   'TEST_LIMITS_5'           : (1, 1, 0, 0, 0),# (Write BER limit * -10, Read BER limit * -10, unused, unused, unused)
}
###############################################################################
################################## Test 0126 ##################################
svoFlawPrm_126={
    'test_num'               : 126,
    'prm_name'               : 'svoFlawPrm_126',
    'timeout'                : 60000*numHeads,
    'spc_id'                 : 1,
    'START_CYL'              : (0,0),
    'END_CYL'                : (0xFFFF,0xFFFF),
    'NBR_CYLS'               : 0,
    'OFFSET_SETTING'         : (0x0000,0x0000,0x0000,), #center track only
    'HEAD_RANGE'             : 0x00FF,
    'CWORD1'                 : 0x1010,  # From 0xD010 disable the verified report in the report file & servo flaw trace reporting
    'SEEK_TYPE'              : 0X25,
    'REVS'                   : (0x0305,), # upper byte is 1st look revs; lower byte is 2nd look revs
    'THRESHOLD'              : {  # Number of failed revs in 2nd look to qualify for failed track
       'ATTRIBUTE'              : 'CAPACITY_CUS',
       'DEFAULT'                : '500G_OEM1B',
       '1000G_OEM1B'            : (0x0001,),
       '1000G_STD'              : (0x0002,),
       '750G_OEM1B'             : (0x0001,),
       '750G_STD'               : (0x0002,),                               
       '500G_OEM1B'             : (0x0001,),
       '500G_STD'               : (0x0002,),
       '500G_NONE'              : (0x0002,),
       '320G_STD'               : (0x0002,),
       '320G_NONE'              : (0x0002,),
    },
    'SET_OCLIM'              : (0x0000,),
    'MAX_ERROR'              : 29,        # 10% of the Total Servo Sev
}

prm_126_svo_scan_probation_write = {
   'test_num'                : 126,
   'prm_name'                : 'prm_126_svo_scan_probation_write',
   'timeout'                 : 36000,
   'spc_id'                  : 252,
   'START_CYL'               : (0x0000, 0x0000),
   'END_CYL'                 : (0xFFFF, 0xFFFF),
   'HEAD_RANGE'              : 0x00FF,
   'CWORD2'                  : 0x0084, # scan probation track
   'SEEK_TYPE'               : 0x25, # write position
   'OFFSET_SETTING'          : (0xFFEE, 0x12, 0x12,), # +-7% offset
   'HEAD_CLAMP'              : 0x7D0, # 2000
   'REVS'                    : 0x0303, # 3 REVS for both level 1 and 2
   'THRESHOLD'               : 1, # 1 time to capture the flaw
   'NBR_CYLS'                : 1, # +-1 adj track
}


prm_126_read_sft_oracle = {
   'test_num'                 : 126,
   'prm_name'                 : 'prm_126_read_sft',
   'timeout'                  : 600,
   'spc_id'                   : 1,
   'CWORD1'                   : 0x0002,
   }

prm_126_read_sft = {
   'test_num'                : 126,
   'prm_name'                : 'prm_126_scan_probation_bad_sample_write',
   'timeout'                 : 36000,
   'spc_id'                  : 412,
   'START_CYL'               : (0x0000, 0x0000),
   'END_CYL'                 : (0xFFFF, 0xFFFF),
   'HEAD_RANGE'              : 0x00FF,
   'CWORD2'                  : 0x0104, # scan probation track
   'SEEK_TYPE'               : 0x25,
   'OFFSET_SETTING'          : (0, 0, 0,), # offset
   'HEAD_CLAMP'              : 0x7D0, # 2000
   'REVS'                    : 0x0A0A, # 10 REVS for both level 1 and 2
   'THRESHOLD'               : 1, # 1 time to capture the flaw
   'NBR_CYLS'                : 0, # adj track
}

adj_svo_scan_write_prm_126 = {
   'test_num'                : 126,
   'prm_name'                : 'adj_svo_scan_write_prm_126',
   'timeout'                 : 36000,
   'spc_id'                  : 1,
   'START_CYL'               : (0x0000, 0x0000),
   'END_CYL'                 : (0xFFFF, 0xFFFF),
   'HEAD_RANGE'              : 0x00FF,
   'CWORD1'                  : 0x0080,
   'SEEK_TYPE'               : 0x25,
   'OFFSET_SETTING'          : (0xFFE0, 0x20, 0x20,),
   'HEAD_CLAMP'              : 0xB9,
   'REVS'                    : 0x030A,
   'THRESHOLD'               : 3,
   'NBR_CYLS'                : 1,        # Lowered to 1 to effectively disable this for Banshee
   'THRESHOLD'               : 4,
}

adj_svo_scan_read_prm_126 = {
   'test_num'                : 126,
   'prm_name'                : 'adj_svo_scan_read_prm_126',
   'timeout'                 : 36000,
   'spc_id'                  : 1,
   'START_CYL'               : (0x0000, 0x0000),
   'END_CYL'                 : (0xFFFF, 0xFFFF),
   'HEAD_RANGE'              : 0x00FF,
   'CWORD1'                  : 0x0080,
   'SEEK_TYPE'               : 0x15,
   'OFFSET_SETTING'          : (0xFFE0,0x20,0x20,),
   'HEAD_CLAMP'              : 0xB9,
   'REVS'                    : 0x030A,
   'THRESHOLD'               : 3,
   'NBR_CYLS'                : 1,       # Lowered to 1 to effectively disable this for Banshee
   'MAX_ERROR'               : 832,
   'THRESHOLD'               : 4,
}

prm_126_cw1 = {
    'test_num':126,
    'prm_name':'prm_126_cw1',
    'timeout':36000,
    "CWORD1" : (0x0100,),
    'SET_REG01': {
              "ATTRIBUTE"   : "CAPACITY_CUS",
              "DEFAULT"     : "500G_OEM1B",
              "1000G_OEM1B" : (10, 5),
              "1000G_STD"   : (10, 2),
              "750G_OEM1B"  : (10, 5),
              "750G_STD"    : (10, 2),

              "500G_OEM1B"  : (10, 5),
              "500G_STD"    : (10, 2),
              "320G_STD"    : (10, 2),
              },
}

prm_126_pad_oar = {
  'test_num':126,
  'prm_name':'prm_126_pad_oar',
  'timeout':600,
  'spc_id':1,
  "CWORD1" : (0x0800,),
  "HEAD_RANGE" : (0x00FF),
  "PAD_TK_VALUE" : 0,
}

DetectZSCOF_track_126 = {
   'test_num'                : 126,
   'prm_name'                : 'DetectZSCOF_track_126',
   'timeout'                 : 600,
   'spc_id'                  : 1,
   'CWORD2'                  : 0x0010,
}
###############################################################################
################################## Test 0136 ##################################
flexBiasCalibration_136 = {
   'test_num'                : 136,
   'prm_name'                : 'flexBiasCalibration_136',
   'timeout'                 : 1000,
   'spc_id'                  : 1,
   'SEEK_NUMS'               : (10000,),
   'CWORD1'                  : (0xc,),
   'BDRAG_ATTENS'            : 5,
   'INCREMENT'               : 100,
   'BIAS_MOVING_WINDOW'      : 6,
   'BIAS_SUM_ZONES_LIMIT'    : 1000,
   'BIAS_SPIKE_LIMIT'        : 8000,
}

flexBiasCalibration_136_1 = {
   'test_num'                : 136,
   'prm_name'                : 'flexBiasCalibration_136',
   'timeout'                 : 1500,
   'spc_id'                  : 11,
   'SEEK_NUMS'               : (5000,),
   'CWORD1'                  : (0xc,),
   'BDRAG_ATTENS'            : 5,
   'INCREMENT'               : 20,
   'BIAS_MOVING_WINDOW'      : 6,
   'BIAS_SUM_ZONES_LIMIT'    : 1000,
   'BIAS_SPIKE_LIMIT'        : 8000,
}

flexBiasCalibration_136_2 = {
   'test_num'                : 136,
   'prm_name'                : 'flexBiasCalibration_136',
   'timeout'                 : 1500,
   'spc_id'                  : 12,
   'SEEK_NUMS'               : (5000,),
   'CWORD1'                  : (0xc,),
   'BDRAG_ATTENS'            : 5,
   'INCREMENT'               : 20,
   'BIAS_MOVING_WINDOW'      : 6,
   'BIAS_SUM_ZONES_LIMIT'    : 1000,
   'BIAS_SPIKE_LIMIT'        : 8000,
 }

# Flex bias cal setup for coarse calibration during MDW cals
flexBiasCalibration_136_MDW = {
   'test_num'                : 136,
   'prm_name'                : 'flexBiasCalibration_136_MDW',
   'timeout'                 : 7200,
   'spc_id'                  : 1,
   'SEEK_NUMS'               : (2000,),
   'CWORD1'                  : (0xc,),
   'BDRAG_ATTENS'            : 5,
   'INCREMENT'               : 300,
   'BIAS_MOVING_WINDOW'      : 6,
   'BIAS_SUM_ZONES_LIMIT'    : 1000,
   'BIAS_SPIKE_LIMIT'        : 6000,
}
###############################################################################
################################## Test 0150 ##################################
servoLinCalPrm_150 = {
   'test_num'                : 150,
   'prm_name'                : 'servoLinCalPrm_150',
   'timeout'                 : 2000 * numHeads,
   'spc_id'                  : 1,
   'CWORD1'                  : 0x780F,
   'TEST_CYL'                : (0, 0),
   'NBR_CYLS'                : 8,
   'HEAD_RANGE'              : 0x00FF,
   'NUM_SAMPLES'             : 5100,
   'FINAL_PK_PK_GAIN_LIM'    : 600,
   'GAIN_CORR_LIM'           : 600,
}                           
                            
servoLinCalCheck_150 = {    
   'test_num'                : 150,
   'prm_name'                : 'servoLinCalCheck_150',
   'timeout'                 : 8000 * numHeads,
   'spc_id'                  : 1,
   'CWORD1'                  : 0x7807,
   'TEST_CYL'                : (0x0000, 0x0000),
   'NBR_CYLS'                : 10,
   'NBR_BINS'                : 16,
   'HEAD_RANGE'              : 0x00FF,
   'FREQUENCY'               : 920,
   'CONVERGE_LIM_1'          : 50,
   'INJ_AMPL'                : 10,
   'NUM_SAMPLES'             : 6400,
   'NBR_MEAS_REPS'           : 3,
   'GAIN_DELTA_LIM'          : 50,
   'FINAL_PK_PK_GAIN_LIM'    : {
      'ATTRIBUTE'               : 'HGA_SUPPLIER',
      'DEFAULT'                 : 'RHO',
      'RHO'                     : 500,
      'HWY'                     : 300,
      'TDK'                     : 300,
   },
   'GAIN_CORR_LIM'          : 600,
}
###############################################################################
################################## Test 0152 ##################################
if (testSwitch.WO_MULTIRATESNO_TT122 == 0):
   doBodePrm_152 = {
      'test_num'                : 152,
      'prm_name'                : 'doBodePrm_152_ServoParms',
      'timeout'                 : 1000 * numHeads,
      'spc_id'                  : 1,

   }
else:
   doBodePrm_152 = {
      'test_num'                : 152,
      'prm_name'                : 'doBodePrm_152_ServoParms',
      'timeout'                 : 1000 * numHeads,
      'spc_id'                  : 1,
      'FAIL_SAFE'               : (),
      'PLOT_TYPE'               : 6,
   }                          

doBodeSNO_152 = {
   'test_num'                : 152,
   'prm_name'                : 'doBodePrm_152',
   'spc_id'                  : 1,
   'DO_SNO'                  : [],
   'SNO_METHOD'              : 1,
   'PLOT_TYPE'               : 6,
   'HEAD_RANGE'              : (0xFFFF),
   'NBR_NOTCHES'             : (1),
   'NUM_SAMPLES'             : 10, # Only needed when SNO_METHOD = 5, peak normalization w/0 SNO
   'PTS_UNDR_PK'             : 3,
   'SHARP_THRESH'            : 5,
   'PEAK_SUMMARY'            : 2,
   'NOTCH_CONFIG'            : 0, # Configure each notch independently
   'NOTCH_TABLE'             : 0, #VCM
   'FREQ_BAND_LO_1_PARMS'    : (200,175,11),
   'FREQ_BAND_MID_1_PARMS'   : (6000,100,1000),
}

Controller_3_BodePrm_152 = {
   'test_num'                : 152,
   'prm_name'                : 'Controller_3_BodePrm_152',
   'timeout'                 : 1000 * numHeads,
   'spc_id'                  : 1,
   'FAIL_SAFE'               : (),
   'CWORD1'                  : 0x0001,
   'START_CYL'               : (0, 48900),
   'END_CYL'                 : (0, 48900),
   'HEAD_RANGE'              : 0xFFFF,
   'FREQ_RANGE'              : (500, 1600),
   'FREQ_INCR'               : 0x19,
   'NBR_TFA_SAMPS'           : 0x0E,
   'NBR_MEAS_REPS'           : 0x02,
   'INJ_AMPL'                : 50,
   'GAIN_LIMIT'              : 1000,
   'PLOT_TYPE'               : 6,           # Closed Loop
}

doBodePrm_152_OD = {
   'test_num'                : 152,
   'prm_name'                : 'doBodePrm_152 at OD',
   'timeout'                 : 1000*numHeads,
   'spc_id'                  : 1,
   'FAIL_SAFE'               : (),
   'PLOT_TYPE'               : (6,),
   'MEASURE_PHASE'           : (),  # May want to comment this out once the drive is ready for production, adds data, but otherwise does not increase test time.
   'CWORD1'                  : (0x0000),  # No CWORD1 Options used
   'START_CYL'               : (0,10,),
   'END_CYL'                 : (0,10,),
   'HEAD_RANGE'              : (0xFFFF,),
   'FREQ_RANGE'              : (500,0xFFFF,),  # Tests from 500 Hz to (2 * Nyquist - 500 Hz)
   'FREQ_INCR'               : (0x19,),
   'NBR_TFA_SAMPS'           : (0x0e,),
   'NBR_MEAS_REPS'           : (0x02,),
   'INJ_AMPL'                : (50,),
   'GAIN_LIMIT'              : (1000,),
   'SHARP_THRESH'            : (0,),
}

doBodePrm_152_S_OD = {
   'test_num'                : 152,
   'prm_name'                : 'doBodePrm_152_S at OD',
   'timeout'                 : 1000*numHeads,
   'spc_id'                  : 4,
   'FAIL_SAFE'               : (),
   'PLOT_TYPE'               : (2,),
   'MEASURE_PHASE'           : (),  # May want to comment this out once the drive is ready for production, adds data, but otherwise does not increase test time.
   'CWORD1'                  : (0x0000),  # No CWORD1 Options used
   'START_CYL'               : (0,10,),
   'END_CYL'                 : (0,10,),
   'HEAD_RANGE'              : (0xFFFF,),
   'FREQ_RANGE'              : (500,0xFFFF,),  # Tests from 500 Hz to (2 * Nyquist - 500 Hz)
   'FREQ_INCR'               : (0x19,),
   'NBR_TFA_SAMPS'           : (0x0e,),
   'NBR_MEAS_REPS'           : (0x02,),
   'INJ_AMPL'                : (50,),
   'GAIN_LIMIT'              : (1000,),
   'SHARP_THRESH'            : (0,),
}

doBodePrm_152_MD = {
   'test_num'                : 152,
   'prm_name'                : 'doBodePrm_152 at MD',
   'timeout'                 : 1000*numHeads,
   'spc_id'                  : 2,
   'FAIL_SAFE'               : (),
   'PLOT_TYPE'               : (6,),
   'MEASURE_PHASE'           : (),  # May want to comment this out once the drive is ready for production, adds data, but otherwise does not increase test time.
   'CWORD1'                  : (0x0000),  # No CWORD1 Options used
   'START_CYL'               : (0x0001,0x3880,),
   'END_CYL'                 : (0x0001,0x3880,),
   'HEAD_RANGE'              : (0xFFFF,),
   'FREQ_RANGE'              : (500,0xFFFF,),  # Tests from 500 Hz to (2 * Nyquist - 500 Hz)
   'FREQ_INCR'               : (0x19,),
   'NBR_TFA_SAMPS'           : (0x0e,),
   'NBR_MEAS_REPS'           : (0x02,),
   'INJ_AMPL'                : (50,),
   'GAIN_LIMIT'              : (1000,),
   'SHARP_THRESH'            : (0,),
}                          

doBodePrm_152_S_MD = {
   'test_num'                : 152,
   'prm_name'                : 'doBodePrm_152_S at MD',
   'timeout'                 : 1000*numHeads,
   'spc_id'                  : 5,
   'FAIL_SAFE'               : (),
   'PLOT_TYPE'               : (2,),
   'MEASURE_PHASE'           : (),  # May want to comment this out once the drive is ready for production, adds data, but otherwise does not increase test time.
   'CWORD1'                  : (0x0000),  # No CWORD1 Options used
   'START_CYL'               : (0x0001,0x3880,),
   'END_CYL'                 : (0x0001,0x3880,),
   'HEAD_RANGE'              : (0xFFFF,),
   'FREQ_RANGE'              : (500,0xFFFF,),  # Tests from 500 Hz to (2 * Nyquist - 500 Hz)
   'FREQ_INCR'               : (0x19,),
   'NBR_TFA_SAMPS'           : (0x0e,),
   'NBR_MEAS_REPS'           : (0x02,),
   'INJ_AMPL'                : (50,),
   'GAIN_LIMIT'              : (1000,),
   'SHARP_THRESH'            : (0,),
}

doBodePrm_152_ID = {
   'test_num'                : 152,
   'prm_name'                : 'doBodePrm_152 at ID',
   'timeout'                 : 1000*numHeads,
   'spc_id'                  : 3,
   'FAIL_SAFE'               : (),
   'PLOT_TYPE'               : (6,),
   'MEASURE_PHASE'           : (),  # May want to comment this out once the drive is ready for production, adds data, but otherwise does not increase test time.
   'CWORD1'                  : (0x0000),  # No CWORD1 Options used
   'START_CYL'               : (0x0002,0x7100,),
   'END_CYL'                 : (0x0002,0x7100,),
   'HEAD_RANGE'              : (0xFFFF,),
   'FREQ_RANGE'              : (500,0xFFFF,),  # Tests from 500 Hz to (2 * Nyquist - 500 Hz)
   'FREQ_INCR'               : (0x19,),
   'NBR_TFA_SAMPS'           : (0x0e,),
   'NBR_MEAS_REPS'           : (0x02,),
   'INJ_AMPL'                : (50,),
   'GAIN_LIMIT'              : (1000,),
   'SHARP_THRESH'            : (0,),
}

doBodePrm_152_S_ID = {    
   'test_num'                : 152,
   'prm_name'                : 'doBodePrm_152_S at ID',
   'timeout'                 : 1000*numHeads,
   'spc_id'                  : 6,
   'FAIL_SAFE'               : (),
   'PLOT_TYPE'               : (2,),
   'MEASURE_PHASE'           : (),  # May want to comment this out once the drive is ready for production, adds data, but otherwise does not increase test time.
   'CWORD1'                  : (0x0000),  # No CWORD1 Options used
   'START_CYL'               : (0x0002,0x7100,),
   'END_CYL'                 : (0x0002,0x7100,),
   'HEAD_RANGE'              : (0xFFFF,),
   'FREQ_RANGE'              : (500,0xFFFF,),  # Tests from 500 Hz to (2 * Nyquist - 500 Hz)
   'FREQ_INCR'               : (0x19,),
   'NBR_TFA_SAMPS'           : (0x0e,),
   'NBR_MEAS_REPS'           : (0x02,),
   'INJ_AMPL'                : (50,),
   'GAIN_LIMIT'              : (1000,),
   'SHARP_THRESH'            : (0,),
}

if (testSwitch.CHENGAI):
   doBodePrm_152_OD.update( { 'PLOT_TYPE' : (1,), } )
   doBodePrm_152_MD.update( { 'PLOT_TYPE' : (1,), } )
   doBodePrm_152_ID.update( { 'PLOT_TYPE' : (1,), } )
   doBodePrm_152_OD.update( { 'CWORD2' : (0), } )
   doBodePrm_152_MD.update( { 'CWORD2' : (0), } )
   doBodePrm_152_ID.update( { 'CWORD2' : (0), } )

gainFreqFilter_152 = {
   'ATTRIBUTE'               : 'CAPACITY_CUS',
   'DEFAULT'                 : '500G_OEM1B',
   '500G_OEM1B'              : [(6000,23000,8.0), ],  #Start Freq, End Freq, Gain Limit. Set Gain Limit = 0 to set no limit
}

T282_TEST_CYL_05_PCT =  (0xFFFF, 0xFFFD)     # OD (5% of max logical cylinder)
snoNotches_282_DAC_8954 = [
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (11000,12200,),
   'FREQ_RANGE': (11000,12200,),
   'FREQ_INCR': 10,
   'FILTERS': 2**1+2**10,
   'NBR_NOTCHES': (2),
   'BANDWIDTH_BY_ZONE': (0,0,0,0,1000,1000,),
   'NOTCH_DEPTH_BY_ZONE': (0,0,0,0,1400,1400,),
   'SNO_METHOD': 8,
   'HEAD_RANGE': (0x00FF),
   'INJECTION_CURRENT': 70,
   'spc_id': 41,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (6600,7500,),
   'FREQ_RANGE': (6600,7500,),
   'FREQ_INCR': 20,
   'FILTERS': 2**11,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 160,
   'NOTCH_DEPTH': 310,
   'HEAD_RANGE': (0x00FF),
   'AUTO_SCALE_SEED': 300,
   'INJECTION_CURRENT': 70,
   'PEAK_WIDTH': 250,
   'spc_id': 42,
},
   ]
if HDASerialNumber[1:3] in ['C0', 'F4', 'F8']: # D0. For D1 / D2, need reanalysis the parameters.
   snoNotches_282_DAC_8954.extend(
       [
           {
               'START_CYL': T282_TEST_CYL_05_PCT,
               'END_CYL': T282_TEST_CYL_05_PCT,
               'NOTCH_TABLE': 2,
               'CWORD1': 0x2110,
               'FREQ_LIMIT': (9500,10500,),
               'FREQ_RANGE': (9500,10500,),
               'FREQ_INCR': 20,
               'FILTERS': 2**12,
               'NBR_NOTCHES': (1),
               'BANDWIDTH': 1140,
               'NOTCH_DEPTH': 900,
               'HEAD_RANGE': (0x0001),
               'AUTO_SCALE_SEED': 260,
               'INJECTION_CURRENT': 70,
               'PEAK_WIDTH': 250,
               'spc_id': 43,
               },
           {
               'START_CYL': T282_TEST_CYL_05_PCT,
               'END_CYL': T282_TEST_CYL_05_PCT,
               'NOTCH_TABLE': 2,
               'CWORD1': 0x2110,
               'FREQ_LIMIT': (10100,11120,),
               'FREQ_RANGE': (10100,11120,),
               'FREQ_INCR': 20,
               'FILTERS': 2**12,
               'NBR_NOTCHES': (1),
               'BANDWIDTH': 1140,
               'NOTCH_DEPTH': 900,
               'HEAD_RANGE': (0x0202),
               'AUTO_SCALE_SEED': 260,
               'INJECTION_CURRENT': 70,
               'PEAK_WIDTH': 250,
               'spc_id': 44,
               },
           ]
      )
elif HDASerialNumber[1:3] in ['BZ', 'F5', 'F9']: # D3
   snoNotches_282_DAC_8954.extend(
       [
           {
               'START_CYL': T282_TEST_CYL_05_PCT,
               'END_CYL': T282_TEST_CYL_05_PCT,
               'NOTCH_TABLE': 2,
               'CWORD1': 0x2110,
               'FREQ_LIMIT': (9500,10500,),
               'FREQ_RANGE': (9500,10500,),
               'FREQ_INCR': 20,
               'FILTERS': 2**12,
               'NBR_NOTCHES': (1),
               'BANDWIDTH': 1140,
               'NOTCH_DEPTH': 900,
               'HEAD_RANGE': (0x0002),
               'AUTO_SCALE_SEED': 260,
               'INJECTION_CURRENT': 70,
               'PEAK_WIDTH': 250,
               'spc_id': 43,
               },
           ]
      )

snoNotches_282_DAC_8940 = [
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (6600,7500,),
   'FREQ_RANGE': (6600,7500,),
   'FILTERS': 2**0,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 160,
   'NOTCH_DEPTH': 310,
   'HEAD_RANGE': (0x00FF),
   'AUTO_SCALE_SEED': 300,
   'spc_id': 40,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (8100,9200,),
   'FREQ_RANGE': (8100,9200,),
   'FILTERS': 2**1,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 600,
   'NOTCH_DEPTH': 350,
   'HEAD_RANGE': (0x0002),
   'AUTO_SCALE_SEED': 260,
   'spc_id': 41,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (8100,9200,),
   'FREQ_RANGE': (8100,9200,),
   'FILTERS': 2**1,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 700,
   'NOTCH_DEPTH': 500,
   'HEAD_RANGE': (0x0303),
   'AUTO_SCALE_SEED': 260,
   'spc_id': 42,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (9500,10500,),
   'FREQ_RANGE': (9500,10500,),
   'FILTERS': 2**2,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 1140,
   'NOTCH_DEPTH': 900,
   'HEAD_RANGE': (0x0002),
   'AUTO_SCALE_SEED': 260,
   'spc_id': 43,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (10100,11120,),
   'FREQ_RANGE': (10100,11120,),
   'FILTERS': 2**2,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 1140,
   'NOTCH_DEPTH': 900,
   'HEAD_RANGE': (0x0303),
   'AUTO_SCALE_SEED': 260,
   'spc_id': 44,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (11090,11600,),
   'FREQ_RANGE': (11090,11600,),
   'FILTERS': 2**3,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 500,
   'NOTCH_DEPTH': 1500,
   'HEAD_RANGE': (0x00FF),
   'AUTO_SCALE_SEED': 260,
   'spc_id': 45,
   'FREQ_INCR': 10,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (17200,19000,),
   'FREQ_RANGE': (17200,19000,),
   'FILTERS': 2**5,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 2000,
   'NOTCH_DEPTH': 400,
   'HEAD_RANGE': (0x00FF),
   'AUTO_SCALE_SEED': 260,
   'spc_id': 46,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (19000,22000,),
   'FREQ_RANGE': (19000,22000,),
   'FILTERS': 2**6,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 2500,
   'NOTCH_DEPTH': 1900,
   'HEAD_RANGE': (0x0000),
   'AUTO_SCALE_SEED': 180,
   'spc_id': 47,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (19000,24500,),
   'FREQ_RANGE': (19000,24500,),
   'FILTERS': 2**6+2**7,
   'NBR_NOTCHES': (2),
   'BANDWIDTH_BY_ZONE': (0,0,0,0,1900,2500,),
   'NOTCH_DEPTH_BY_ZONE': (0,0,0,0,1600,1900,),
   'HEAD_RANGE': (0x0102),
   'AUTO_SCALE_SEED': 180,
   'spc_id': 48,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (19000,22000,),
   'FREQ_RANGE': (19000,22000,),
   'FILTERS': 2**6,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 2500,
   'NOTCH_DEPTH': 1900,
   'HEAD_RANGE': (0x0303),
   'AUTO_SCALE_SEED': 180,
   'spc_id': 49,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (22000,24500,),
   'FREQ_RANGE': (22000,24500,),
   'FILTERS': 2**7,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 4500,
   'NOTCH_DEPTH': 1600,
   'HEAD_RANGE': (0x0000),
   'AUTO_SCALE_SEED': 180,
   'spc_id': 50,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (22000,25000,),
   'FREQ_RANGE': (22000,25000,),
   'FILTERS': 2**7+2**8,
   'NBR_NOTCHES': (2),
   'BANDWIDTH_BY_ZONE': (0,0,0,0,1900,4500,),
   'NOTCH_DEPTH_BY_ZONE': (0,0,0,0,1000,1700,),
   'HEAD_RANGE': (0x0303),
   'AUTO_SCALE_SEED': 180,
   'spc_id': 51,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (24500,28000,),
   'FREQ_RANGE': (24500,28000,),
   'FILTERS': 2**8+2**9,
   'NBR_NOTCHES': (2),
   'BANDWIDTH_BY_ZONE': (0,0,0,0,4200,4200,),
   'NOTCH_DEPTH_BY_ZONE': (0,0,0,0,1500,1500,),
   'HEAD_RANGE': (0x0000),
   'AUTO_SCALE_SEED': 180,
   'spc_id': 52,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (24500,28000,),
   'FREQ_RANGE': (24500,28000,),
   'FILTERS': 256,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 4200,
   'NOTCH_DEPTH': 1700,
   'HEAD_RANGE': (0x0102),
   'AUTO_SCALE_SEED': 180,
   'spc_id': 56,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (25000,31500,),
   'FREQ_RANGE': (25000,31500,),
   'FILTERS': 2**9+2**10+2**11,
   'NBR_NOTCHES': (3),
   'BANDWIDTH_BY_ZONE': (0,0,0,4000,4000,4000,),
   'NOTCH_DEPTH_BY_ZONE': (0,0,0,1900,1900,1900,),
   'HEAD_RANGE': (0x0303),
   'AUTO_SCALE_SEED': 180,
   'spc_id': 54,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (28000,31500,),
   'FREQ_RANGE': (28000,31500,),
   'FILTERS': 3584,
   'NBR_NOTCHES': (3),
   'BANDWIDTH_BY_ZONE': (0,0,0,4200,3000,3000,),
   'NOTCH_DEPTH_BY_ZONE': (0,0,0,1700,2300,2300,),
   'HEAD_RANGE': (0x0102),
   'AUTO_SCALE_SEED': 180,
   'spc_id': 57,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (28000,31500,),
   'FREQ_RANGE': (28000,31500,),
   'FILTERS': 2**10+2**11,
   'NBR_NOTCHES': (2),
   'BANDWIDTH_BY_ZONE': (0,0,0,0,3000,3000,),
   'NOTCH_DEPTH_BY_ZONE': (0,0,0,0,2300,2300,),
   'HEAD_RANGE': (0x0000),
   'AUTO_SCALE_SEED': 180,
   'spc_id': 58,
},
   ]
snoNotches_282_DAC_8947 = [
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (6600,7500,),
   'FREQ_RANGE': (6600,7500,),
   'FILTERS': 2**0,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 160,
   'NOTCH_DEPTH': 310,
   'HEAD_RANGE': (0x00FF),
   'AUTO_SCALE_SEED': 300,
   'spc_id': 40,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (8100,9200,),
   'FREQ_RANGE': (8100,9200,),
   'FILTERS': 2**1,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 600,
   'NOTCH_DEPTH': 350,
   'HEAD_RANGE': (0x0002),
   'AUTO_SCALE_SEED': 260,
   'spc_id': 41,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (8100,9200,),
   'FREQ_RANGE': (8100,9200,),
   'FILTERS': 2**1,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 700,
   'NOTCH_DEPTH': 500,
   'HEAD_RANGE': (0x0303),
   'AUTO_SCALE_SEED': 260,
   'spc_id': 42,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (9500,10500,),
   'FREQ_RANGE': (9500,10500,),
   'FILTERS': 2**2,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 1140,
   'NOTCH_DEPTH': 900,
   'HEAD_RANGE': (0x0002),
   'AUTO_SCALE_SEED': 260,
   'spc_id': 43,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (10100,10820,),
   'FREQ_RANGE': (10100,10820,),
   'FILTERS': 2**2,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 1140,
   'NOTCH_DEPTH': 900,
   'HEAD_RANGE': (0x0303),
   'AUTO_SCALE_SEED': 260,
   'spc_id': 44,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (10800,11800,),
   'FREQ_RANGE': (10800,11800,),
   'FILTERS': 2**3,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 500,
   'NOTCH_DEPTH': 1500,
   'HEAD_RANGE': (0x00FF),
   'AUTO_SCALE_SEED': 260,
   'spc_id': 45,
   'FREQ_INCR': 10,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (17200,19000,),
   'FREQ_RANGE': (17200,19000,),
   'FILTERS': 2**5,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 2000,
   'NOTCH_DEPTH': 400,
   'HEAD_RANGE': (0x00FF),
   'AUTO_SCALE_SEED': 260,
   'spc_id': 46,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (19000,22000,),
   'FREQ_RANGE': (19000,22000,),
   'FILTERS': 2**6,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 2500,
   'NOTCH_DEPTH': 1900,
   'HEAD_RANGE': (0x0000),
   'AUTO_SCALE_SEED': 180,
   'spc_id': 47,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (19000,24500,),
   'FREQ_RANGE': (19000,24500,),
   'FILTERS': 2**6+2**7,
   'NBR_NOTCHES': (2),
   'BANDWIDTH_BY_ZONE': (0,0,0,0,1900,2500,),
   'NOTCH_DEPTH_BY_ZONE': (0,0,0,0,1600,1900,),
   'HEAD_RANGE': (0x0102),
   'AUTO_SCALE_SEED': 180,
   'spc_id': 48,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (19000,22000,),
   'FREQ_RANGE': (19000,22000,),
   'FILTERS': 2**6,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 2500,
   'NOTCH_DEPTH': 1900,
   'HEAD_RANGE': (0x0303),
   'AUTO_SCALE_SEED': 180,
   'spc_id': 49,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (22000,24500,),
   'FREQ_RANGE': (22000,24500,),
   'FILTERS': 2**7,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 4500,
   'NOTCH_DEPTH': 1600,
   'HEAD_RANGE': (0x0000),
   'AUTO_SCALE_SEED': 180,
   'spc_id': 50,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (22000,25000,),
   'FREQ_RANGE': (22000,25000,),
   'FILTERS': 2**7+2**8,
   'NBR_NOTCHES': (2),
   'BANDWIDTH_BY_ZONE': (0,0,0,0,1900,4400,),
   'NOTCH_DEPTH_BY_ZONE': (0,0,0,0,1000,1700,),
   'HEAD_RANGE': (0x0303),
   'AUTO_SCALE_SEED': 180,
   'spc_id': 51,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (24500,28000,),
   'FREQ_RANGE': (24500,28000,),
   'FILTERS': 2**8+2**9,
   'NBR_NOTCHES': (2),
   'BANDWIDTH_BY_ZONE': (0,0,0,0,4100,4100,),
   'NOTCH_DEPTH_BY_ZONE': (0,0,0,0,1500,1500,),
   'HEAD_RANGE': (0x0000),
   'AUTO_SCALE_SEED': 180,
   'spc_id': 52,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (24500,28000,),
   'FREQ_RANGE': (24500,28000,),
   'FILTERS': 256,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 4100,
   'NOTCH_DEPTH': 1700,
   'HEAD_RANGE': (0x0102),
   'AUTO_SCALE_SEED': 180,
   'spc_id': 56,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (25000,31500,),
   'FREQ_RANGE': (25000,31500,),
   'FILTERS': 2**9+2**10+2**11,
   'NBR_NOTCHES': (3),
   'BANDWIDTH_BY_ZONE': (0,0,0,3900,3900,3900,),
   'NOTCH_DEPTH_BY_ZONE': (0,0,0,1900,1900,1900,),
   'HEAD_RANGE': (0x0303),
   'AUTO_SCALE_SEED': 180,
   'spc_id': 54,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (28000,31500,),
   'FREQ_RANGE': (28000,31500,),
   'FILTERS': 3584,
   'NBR_NOTCHES': (3),
   'BANDWIDTH_BY_ZONE': (0,0,0,4100,2900,2900,),
   'NOTCH_DEPTH_BY_ZONE': (0,0,0,1700,2300,2300,),
   'HEAD_RANGE': (0x0102),
   'AUTO_SCALE_SEED': 180,
   'spc_id': 57,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (28000,31500,),
   'FREQ_RANGE': (28000,31500,),
   'FILTERS': 2**10+2**11,
   'NBR_NOTCHES': (2),
   'BANDWIDTH_BY_ZONE': (0,0,0,0,2900,2900,),
   'NOTCH_DEPTH_BY_ZONE': (0,0,0,0,2300,2300,),
   'HEAD_RANGE': (0x0000),
   'AUTO_SCALE_SEED': 180,
   'spc_id': 58,
},
   ]  

snoNotches_282_DAC_8949 = [
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (6600,7500,),
   'FREQ_RANGE': (6600,7500,),
   'FILTERS': 2**0,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 160,
   'NOTCH_DEPTH': 310,
   'HEAD_RANGE': (0x00FF),
   'AUTO_SCALE_SEED': 300,
   'spc_id': 40,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (8100,9200,),
   'FREQ_RANGE': (8100,9200,),
   'FILTERS': 2**1,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 600,
   'NOTCH_DEPTH': 350,
   'HEAD_RANGE': (0x0002),
   'AUTO_SCALE_SEED': 260,
   'spc_id': 41,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (8100,9200,),
   'FREQ_RANGE': (8100,9200,),
   'FILTERS': 2**1,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 700,
   'NOTCH_DEPTH': 500,
   'HEAD_RANGE': (0x0303),
   'AUTO_SCALE_SEED': 260,
   'spc_id': 42,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (9500,10500,),
   'FREQ_RANGE': (9500,10500,),
   'FILTERS': 2**2,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 1140,
   'NOTCH_DEPTH': 900,
   'HEAD_RANGE': (0x0002),
   'AUTO_SCALE_SEED': 260,
   'spc_id': 43,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (10100,10820,),
   'FREQ_RANGE': (10100,10820,),
   'FILTERS': 2**2,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 1140,
   'NOTCH_DEPTH': 900,
   'HEAD_RANGE': (0x0303),
   'AUTO_SCALE_SEED': 260,
   'spc_id': 44,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (10800,11800,),
   'FREQ_RANGE': (10800,11800,),
   'FILTERS': 2**3,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 500,
   'NOTCH_DEPTH': 1500,
   'HEAD_RANGE': (0x00FF),
   'AUTO_SCALE_SEED': 260,
   'spc_id': 45,
   'FREQ_INCR': 10,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (17200,19000,),
   'FREQ_RANGE': (17200,19000,),
   'FILTERS': 2**5,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 2000,
   'NOTCH_DEPTH': 400,
   'HEAD_RANGE': (0x00FF),
   'AUTO_SCALE_SEED': 260,
   'spc_id': 46,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (19000,22000,),
   'FREQ_RANGE': (19000,22000,),
   'FILTERS': 2**6,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 2500,
   'NOTCH_DEPTH': 1900,
   'HEAD_RANGE': (0x0000),
   'AUTO_SCALE_SEED': 180,
   'spc_id': 47,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (19000,24500,),
   'FREQ_RANGE': (19000,24500,),
   'FILTERS': 2**6+2**7,
   'NBR_NOTCHES': (2),
   'BANDWIDTH_BY_ZONE': (0,0,0,0,1900,2500,),
   'NOTCH_DEPTH_BY_ZONE': (0,0,0,0,1600,1900,),
   'HEAD_RANGE': (0x0102),
   'AUTO_SCALE_SEED': 180,
   'spc_id': 48,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (19000,22000,),
   'FREQ_RANGE': (19000,22000,),
   'FILTERS': 2**6,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 2500,
   'NOTCH_DEPTH': 1900,
   'HEAD_RANGE': (0x0303),
   'AUTO_SCALE_SEED': 180,
   'spc_id': 49,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (22000,24500,),
   'FREQ_RANGE': (22000,24500,),
   'FILTERS': 2**7,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 4500,
   'NOTCH_DEPTH': 1600,
   'HEAD_RANGE': (0x0000),
   'AUTO_SCALE_SEED': 180,
   'spc_id': 50,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (22000,25000,),
   'FREQ_RANGE': (22000,25000,),
   'FILTERS': 2**7+2**8,
   'NBR_NOTCHES': (2),
   'BANDWIDTH_BY_ZONE': (0,0,0,0,1900,4400,),
   'NOTCH_DEPTH_BY_ZONE': (0,0,0,0,1000,1700,),
   'HEAD_RANGE': (0x0303),
   'AUTO_SCALE_SEED': 180,
   'spc_id': 51,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (24500,28000,),
   'FREQ_RANGE': (24500,28000,),
   'FILTERS': 2**8+2**9,
   'NBR_NOTCHES': (2),
   'BANDWIDTH_BY_ZONE': (0,0,0,0,4100,4100,),
   'NOTCH_DEPTH_BY_ZONE': (0,0,0,0,1500,1500,),
   'HEAD_RANGE': (0x0000),
   'AUTO_SCALE_SEED': 180,
   'spc_id': 52,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (24500,28000,),
   'FREQ_RANGE': (24500,28000,),
   'FILTERS': 256,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 4100,
   'NOTCH_DEPTH': 1700,
   'HEAD_RANGE': (0x0102),
   'AUTO_SCALE_SEED': 180,
   'spc_id': 56,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (25000,31500,),
   'FREQ_RANGE': (25000,31500,),
   'FILTERS': 2**9+2**10+2**11,
   'NBR_NOTCHES': (3),
   'BANDWIDTH_BY_ZONE': (0,0,0,3900,3900,3900,),
   'NOTCH_DEPTH_BY_ZONE': (0,0,0,1900,1900,1900,),
   'HEAD_RANGE': (0x0303),
   'AUTO_SCALE_SEED': 180,
   'spc_id': 54,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (28000,31500,),
   'FREQ_RANGE': (28000,31500,),
   'FILTERS': 3584,
   'NBR_NOTCHES': (3),
   'BANDWIDTH_BY_ZONE': (0,0,0,4100,2900,2900,),
   'NOTCH_DEPTH_BY_ZONE': (0,0,0,1700,2300,2300,),
   'HEAD_RANGE': (0x0102),
   'AUTO_SCALE_SEED': 180,
   'spc_id': 57,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (28000,31500,),
   'FREQ_RANGE': (28000,31500,),
   'FILTERS': 2**10+2**11,
   'NBR_NOTCHES': (2),
   'BANDWIDTH_BY_ZONE': (0,0,0,0,2900,2900,),
   'NOTCH_DEPTH_BY_ZONE': (0,0,0,0,2300,2300,),
   'HEAD_RANGE': (0x0000),
   'AUTO_SCALE_SEED': 180,
   'spc_id': 58,
},
   ] 
   
CktSNO_152 = {
   'test_num'                : 152,
   'prm_name'                : 'doBodePrm_152',
   'timeout'                 : 4000*numHeads,
   'spc_id'                  : 9,
   'CWORD1'                  : (0x0000),  # No CWORD1 Options used
   'CWORD2'                  : 4,       # Force SNO if PEAK was not detected.
   'DO_SNO'                  : (),
   'SNO_METHOD'              : 1,
   'PLOT_TYPE'               : 1,
   'START_CYL'               : (0, 10000),
   'END_CYL'                 : (0, 10000),
   'HEAD_RANGE'              : (0xFFFF),
   'FREQ_RANGE'              : (8184,9512,),      # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'FREQ_INCR'               : (24,),
   'NBR_NOTCHES'             : (1),
   'NBR_TFA_SAMPS'           : 14, #was 2000
   'NBR_MEAS_REPS'           : 3,
   'INJ_AMPL'                : 70,
   'GAIN_LIMIT'              : -200, # previously set to +90, -60 will ensure new notch settings get made.  #"GAIN_LIMIT": 0xFFC4,
   'NUM_SAMPLES'             : 10, # Only needed when SNO_METHOD = 5, peak normalization w/0 SNO                            
   'ZETA_1'                  : (int(0.020*1000), int(0.03*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_2'                  : (int(0.030*1000), int(0.09*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_3'                  : (int(0.050*1000), int(0.12*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_4'                  : (int(0.080*1000), int(0.16*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_5'                  : (int(0.040*1000), int(0.18*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_6'                  : (int(0.280*1000), int(0.64*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary                            
   'PEAK_WIDTH'              : 10,
   'PTS_UNDR_PK'             : 3,
   'SHARP_THRESH'            : 0, # changed from 5 to 0
   'PEAK_GAIN_MIN'           : -200,    #
   'PEAK_SUMMARY'            : 2,
   'NOTCH_CONFIG'            : 0, # Configure each notch independently
   'NOTCH_TABLE'             : 0, #VCM
}                          
                           
CktNotches_152 = [         
   {                       
   'FILTERS'                 : 2**5,
   'FREQ_RANGE'              : (10300,11400,),
   'FREQ_INCR'               : 24,
   'ZETA_6'                  : (int(0.28*1000),int(0.64*100)),
   'HEAD_RANGE'              : (0xFFFF),
   'NBR_NOTCHES'             : (1),
   'BANDWIDTH'               : (750),
   'NOTCH_DEPTH'             : (1300),
   'FREQ_OFFSET'             : (50),      # Add Freq for Notch Zeta config
   },
]

sno_phase_peak_detect_152_OD = {
   'test_num'                : 152,
   'prm_name'                : 'doSNOPhasePrm_152',
   'timeout'                 : 4000*numHeads,
   'spc_id'                  : 10,
   'CWORD1'                  : (0x0100),  # No CWORD1 Options used
   'CWORD2'                  : 32,       # Force SNO if PEAK was not detected and set SNO Phase Detection.
   'DO_SNO'                  : (),
   'MEASURE_PHASE'           : (),
   'SNO_METHOD'              : 6,
   'PLOT_TYPE'               : 6,
   'START_CYL'               : (0, 10000),
   'END_CYL'                 : (0, 10000),
   'HEAD_RANGE'              : (0),
   'FREQ_RANGE'              : (2000,3000,),      # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'FREQ_INCR'               : (24,),             # change from 24 to 10 (3rd May 2013)
   'NBR_NOTCHES'             : (1),
   'NBR_TFA_SAMPS'           : 14, #was 2000
   'NBR_MEAS_REPS'           : 3,
   'INJ_AMPL'                : 70,
   'PHASE_LIMIT'             : -1000, # for detecting the min phase value
   'NUM_SAMPLES'             : 10, # Only needed when SNO_METHOD = 5, peak normalization w/0 SNO
   'ZETA_1'                  : (int(0.020*1000), int(0.03*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_2'                  : (int(0.030*1000), int(0.09*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_3'                  : (int(0.050*1000), int(0.12*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_4'                  : (int(0.080*1000), int(0.16*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_5'                  : (int(0.040*1000), int(0.18*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_6'                  : (int(0.280*1000), int(0.64*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'PEAK_WIDTH'              : 10,
   'PTS_UNDR_PK'             : 3,
   'SHARP_THRESH'            : 0, # changed from 5 to 0
   'PEAK_SUMMARY'            : 2,
   'NOTCH_CONFIG'            : 0, # Configure each notch independently
   'NOTCH_TABLE'             : 0, #VCM
}

CktNotchesPD_152_OD = [
   {
   'FILTERS'                 : 2**5,
   'FREQ_RANGE'              : (2200,3000,),
   'FREQ_INCR'               : 10,                         # change from 24 to 10 (3rd May 2013)
   'ZETA_6'                  : (int(0.28*1000),int(0.64*100)),
   'NBR_NOTCHES'             : (1),
   'BANDWIDTH'               : (750),
   'NOTCH_DEPTH'             : (1300),
   },
]

sno_phase_peak_detect_152_ID = {
   'test_num'                : 152,
   'prm_name'                : 'doSNOPhasePrm_152',
   'timeout'                 : 4000*numHeads,
   'spc_id'                  : 12,
   'CWORD1'                  : (0x0100),  # No CWORD1 Options used
   'CWORD2'                  : 32,       # Force SNO if PEAK was not detected and set SNO Phase Detection.
   'DO_SNO'                  : (),
   'MEASURE_PHASE'           : (),
   'SNO_METHOD'              : 6,
   'PLOT_TYPE'               : 6,
   'START_CYL'               : (0x0005, 0x0910),  #ID test cylinder change from 320000 to 330000
   'END_CYL'                 : (0x0005, 0x0910),
   'HEAD_RANGE'              : (0),
   'FREQ_RANGE'              : (2000,3000,),      # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'FREQ_INCR'               : (24,),             # change from 24 to 10 (3rd May 2013)
   'NBR_NOTCHES'             : (1),
   'NBR_TFA_SAMPS'           : 14, #was 2000
   'NBR_MEAS_REPS'           : 3,
   'INJ_AMPL'                : 70,
   'PHASE_LIMIT'             : -1000, # for detecting the min phase value
   'NUM_SAMPLES'             : 10, # Only needed when SNO_METHOD = 5, peak normalization w/0 SNO
   'ZETA_1'                  : (int(0.020*1000), int(0.03*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_2'                  : (int(0.030*1000), int(0.09*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_3'                  : (int(0.050*1000), int(0.12*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_4'                  : (int(0.080*1000), int(0.16*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_5'                  : (int(0.040*1000), int(0.18*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_6'                  : (int(0.280*1000), int(0.64*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'PEAK_WIDTH'              : 10,
   'PTS_UNDR_PK'             : 3,
   'SHARP_THRESH'            : 0, # changed from 5 to 0
   'PEAK_SUMMARY'            : 2,
   'NOTCH_CONFIG'            : 0, # Configure each notch independently
   'NOTCH_TABLE'             : 0, #VCM
}

CktNotchesPD_152_ID = [
   {
   'FILTERS'                 : 2**5,
   'FREQ_RANGE'              : (2200,3000,),
   'FREQ_INCR'               : 10,                         # change from 24 to 10 (3rd May 2013)
   'ZETA_6'                  : (int(0.28*1000),int(0.64*100)),
   'NBR_NOTCHES'             : (1),
   'BANDWIDTH'               : (750),
   'NOTCH_DEPTH'             : (1300),
   },
]

# Add one more phase loss measurement at 4kHz for OD & ID respectively
sno_phase_peak_detect_152_OD_1 = {
   'test_num'                : 152,
   'prm_name'                : 'doSNOPhasePrm_152',
   'timeout'                 : 4000*numHeads,
   'spc_id'                  : 13,
   'CWORD1'                  : (0x0100),  # No CWORD1 Options used
   'CWORD2'                  : 32,       # Force SNO if PEAK was not detected and set SNO Phase Detection.
   'DO_SNO'                  : (),
   'MEASURE_PHASE'           : (),
   'SNO_METHOD'              : 6,
   'PLOT_TYPE'               : 6,
   'START_CYL'               : (0, 10000),
   'END_CYL'                 : (0, 10000),
   'HEAD_RANGE'              : (0),
   'FREQ_RANGE'              : (2000,3000,),      # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'FREQ_INCR'               : (24,),             # change from 24 to 10 (3rd May 2013)
   'NBR_NOTCHES'             : (1),
   'NBR_TFA_SAMPS'           : 14, #was 2000
   'NBR_MEAS_REPS'           : 3,
   'INJ_AMPL'                : 70,
   'PHASE_LIMIT'             : -1000, # for detecting the min phase value
   'NUM_SAMPLES'             : 10, # Only needed when SNO_METHOD = 5, peak normalization w/0 SNO
   'ZETA_1'                  : (int(0.020*1000), int(0.03*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_2'                  : (int(0.030*1000), int(0.09*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_3'                  : (int(0.050*1000), int(0.12*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_4'                  : (int(0.080*1000), int(0.16*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_5'                  : (int(0.040*1000), int(0.18*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_6'                  : (int(0.280*1000), int(0.64*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'PEAK_WIDTH'              : 10,
   'PTS_UNDR_PK'             : 3,
   'SHARP_THRESH'            : 0, # changed from 5 to 0
   'PEAK_SUMMARY'            : 2,
   'NOTCH_CONFIG'            : 0, # Configure each notch independently
   'NOTCH_TABLE'             : 0, #VCM
}

CktNotchesPD_152_OD_1 = [
   {
   'FILTERS'                 : 2**5,
   'FREQ_RANGE'              : (3000,3900,),
   'FREQ_INCR'               : 10,                         # change from 24 to 10 (3rd May 2013)
   'ZETA_6'                  : (int(0.28*1000),int(0.64*100)),
   'NBR_NOTCHES'             : (1),
   'BANDWIDTH'               : (750),
   'NOTCH_DEPTH'             : (1300),
   },
]

sno_phase_peak_detect_152_ID_1 = {
   'test_num'                : 152,
   'prm_name'                : 'doSNOPhasePrm_152',
   'timeout'                 : 4000*numHeads,
   'spc_id'                  : 15,
   'CWORD1'                  : (0x0100),  # No CWORD1 Options used
   'CWORD2'                  : 32,       # Force SNO if PEAK was not detected and set SNO Phase Detection.
   'DO_SNO'                  : (),
   'MEASURE_PHASE'           : (),
   'SNO_METHOD'              : 6,
   'PLOT_TYPE'               : 6,
   'START_CYL'               : (0x0005, 0x0910),  #ID test cylinder change from 320000 to 330000
   'END_CYL'                 : (0x0005, 0x0910),
   'HEAD_RANGE'              : (0),
   'FREQ_RANGE'              : (2000,3000,),      # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'FREQ_INCR'               : (24,),             # change from 24 to 10 (3rd May 2013)
   'NBR_NOTCHES'             : (1),
   'NBR_TFA_SAMPS'           : 14, #was 2000
   'NBR_MEAS_REPS'           : 3,
   'INJ_AMPL'                : 70,
   'PHASE_LIMIT'             : -1000, # for detecting the min phase value
   'NUM_SAMPLES'             : 10, # Only needed when SNO_METHOD = 5, peak normalization w/0 SNO
   'ZETA_1'                  : (int(0.020*1000), int(0.03*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_2'                  : (int(0.030*1000), int(0.09*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_3'                  : (int(0.050*1000), int(0.12*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_4'                  : (int(0.080*1000), int(0.16*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_5'                  : (int(0.040*1000), int(0.18*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_6'                  : (int(0.280*1000), int(0.64*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'PEAK_WIDTH'              : 10,
   'PTS_UNDR_PK'             : 3,
   'SHARP_THRESH'            : 0, # changed from 5 to 0
   'PEAK_SUMMARY'            : 2,
   'NOTCH_CONFIG'            : 0, # Configure each notch independently
   'NOTCH_TABLE'             : 0, #VCM
}

CktNotchesPD_152_ID_1 = [
   {
   'FILTERS'                 : 2**5,
   'FREQ_RANGE'              : (3000,3900,),
   'FREQ_INCR'               : 10,                         # change from 24 to 10 (3rd May 2013)
   'ZETA_6'                  : (int(0.28*1000),int(0.64*100)),
   'NBR_NOTCHES'             : (1),
   'BANDWIDTH'               : (750),
   'NOTCH_DEPTH'             : (1300),
   },
]
# Add one more phase loss measurement at 4kHz for OD & ID respectively
sno_phase_peak_detect_152_OD_2 = {
   'test_num'                : 152,
   'prm_name'                : 'doSNOPhasePrm_152',
   'timeout'                 : 4000*numHeads,
   'spc_id'                  : 17,
   'CWORD1'                  : (0x0100),  # No CWORD1 Options used
   'CWORD2'                  : 32,       # Force SNO if PEAK was not detected and set SNO Phase Detection.
   'DO_SNO'                  : (),
   'MEASURE_PHASE'           : (),
   'SNO_METHOD'              : 6,
   'PLOT_TYPE'               : 6,
   'START_CYL'               : (0, 10000),
   'END_CYL'                 : (0, 10000),
   'HEAD_RANGE'              : (0),
   'FREQ_RANGE'              : (2000,3000,),      # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'FREQ_INCR'               : (24,),             # change from 24 to 10 (3rd May 2013)
   'NBR_NOTCHES'             : (1),
   'NBR_TFA_SAMPS'           : 14, #was 2000
   'NBR_MEAS_REPS'           : 3,
   'INJ_AMPL'                : 70,
   'PHASE_LIMIT'             : -1000, # for detecting the min phase value
   'NUM_SAMPLES'             : 10, # Only needed when SNO_METHOD = 5, peak normalization w/0 SNO
   'ZETA_1'                  : (int(0.020*1000), int(0.03*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_2'                  : (int(0.030*1000), int(0.09*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_3'                  : (int(0.050*1000), int(0.12*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_4'                  : (int(0.080*1000), int(0.16*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_5'                  : (int(0.040*1000), int(0.18*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_6'                  : (int(0.280*1000), int(0.64*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'PEAK_WIDTH'              : 10,
   'PTS_UNDR_PK'             : 3,
   'SHARP_THRESH'            : 0, # changed from 5 to 0
   'PEAK_SUMMARY'            : 2,
   'NOTCH_CONFIG'            : 0, # Configure each notch independently
   'NOTCH_TABLE'             : 0, #VCM
}

CktNotchesPD_152_OD_2 = [
   {
   'FILTERS'                 : 2**5,
   'FREQ_RANGE'              : (1000,2200,),
   'FREQ_INCR'               : 10,                         # change from 24 to 10 (3rd May 2013)
   'ZETA_6'                  : (int(0.28*1000),int(0.64*100)),
   'NBR_NOTCHES'             : (1),
   'BANDWIDTH'               : (750),
   'NOTCH_DEPTH'             : (1300),
   },
]

sno_phase_peak_detect_152_ID_2 = {
   'test_num'                : 152,
   'prm_name'                : 'doSNOPhasePrm_152',
   'timeout'                 : 4000*numHeads,
   'spc_id'                  : 19,
   'CWORD1'                  : (0x0100),  # No CWORD1 Options used
   'CWORD2'                  : 32,       # Force SNO if PEAK was not detected and set SNO Phase Detection.
   'DO_SNO'                  : (),
   'MEASURE_PHASE'           : (),
   'SNO_METHOD'              : 6,
   'PLOT_TYPE'               : 6,
   'START_CYL'               : (0x0005, 0x0910),  #ID test cylinder change from 320000 to 330000
   'END_CYL'                 : (0x0005, 0x0910),
   'HEAD_RANGE'              : (0),
   'FREQ_RANGE'              : (2000,3000,),      # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'FREQ_INCR'               : (24,),             # change from 24 to 10 (3rd May 2013)
   'NBR_NOTCHES'             : (1),
   'NBR_TFA_SAMPS'           : 14, #was 2000
   'NBR_MEAS_REPS'           : 3,
   'INJ_AMPL'                : 70,
   'PHASE_LIMIT'             : -1000, # for detecting the min phase value
   'NUM_SAMPLES'             : 10, # Only needed when SNO_METHOD = 5, peak normalization w/0 SNO                           
   'ZETA_1'                  : (int(0.020*1000), int(0.03*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_2'                  : (int(0.030*1000), int(0.09*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_3'                  : (int(0.050*1000), int(0.12*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_4'                  : (int(0.080*1000), int(0.16*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_5'                  : (int(0.040*1000), int(0.18*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_6'                  : (int(0.280*1000), int(0.64*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary                           
   'PEAK_WIDTH'              : 10,
   'PTS_UNDR_PK'             : 3,
   'SHARP_THRESH'            : 0, # changed from 5 to 0
   'PEAK_SUMMARY'            : 2,
   'NOTCH_CONFIG'            : 0, # Configure each notch independently
   'NOTCH_TABLE'             : 0, #VCM
}

CktNotchesPD_152_ID_2 = [
   {
   'FILTERS'                 : 2**5,
   'FREQ_RANGE'              : (1000,2200,),
   'FREQ_INCR'               : 10,                         # change from 24 to 10 (3rd May 2013)
   'ZETA_6'                  : (int(0.28*1000),int(0.64*100)),
   'NBR_NOTCHES'             : (1),
   'BANDWIDTH'               : (750),
   'NOTCH_DEPTH'             : (1300),
   },
]

# Add one more phase loss measurement at 4kHz for OD & ID respectively
sno_phase_peak_detect_152_OD_3 = {
   'test_num'                : 152,
   'prm_name'                : 'doSNOPhasePrm_152',
   'timeout'                 : 4000*numHeads,
   'spc_id'                  : 33,
   'CWORD1'                  : (0x0100),  # No CWORD1 Options used
   'CWORD2'                  : 32,       # Force SNO if PEAK was not detected and set SNO Phase Detection.
   'DO_SNO'                  : (),
   'MEASURE_PHASE'           : (),
   'SNO_METHOD'              : 6,
   'PLOT_TYPE'               : 6,
   'START_CYL'               : (0, 10000),
   'END_CYL'                 : (0, 10000),
   'HEAD_RANGE'              : (0),
   'FREQ_RANGE'              : (2000,3000,),      # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'FREQ_INCR'               : (24,),             # change from 24 to 10 (3rd May 2013)
   'NBR_NOTCHES'             : (1),
   'NBR_TFA_SAMPS'           : 14, #was 2000
   'NBR_MEAS_REPS'           : 3,
   'INJ_AMPL'                : 70,
   'PHASE_LIMIT'             : -1000, # for detecting the min phase value
   'NUM_SAMPLES'             : 10, # Only needed when SNO_METHOD = 5, peak normalization w/0 SNO
   'ZETA_1'                  : (int(0.020*1000), int(0.03*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_2'                  : (int(0.030*1000), int(0.09*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_3'                  : (int(0.050*1000), int(0.12*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_4'                  : (int(0.080*1000), int(0.16*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_5'                  : (int(0.040*1000), int(0.18*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_6'                  : (int(0.280*1000), int(0.64*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'PEAK_WIDTH'              : 10,
   'PTS_UNDR_PK'             : 3,
   'SHARP_THRESH'            : 0, # changed from 5 to 0
   'PEAK_SUMMARY'            : 2,
   'NOTCH_CONFIG'            : 0, # Configure each notch independently
   'NOTCH_TABLE'             : 0, #VCM
}

CktNotchesPD_152_OD_3 = [
   {
   'FILTERS'                 : 2**5,
   'FREQ_RANGE'              : (3500,5000,),
   'FREQ_INCR'               : 10,                         # change from 24 to 10 (3rd May 2013)
   'ZETA_6'                  : (int(0.28*1000),int(0.64*100)),
   'NBR_NOTCHES'             : (1),
   'BANDWIDTH'               : (750),
   'NOTCH_DEPTH'             : (1300),
   },
]

sno_phase_peak_detect_152_ID_3 = {
   'test_num'                : 152,
   'prm_name'                : 'doSNOPhasePrm_152',
   'timeout'                 : 4000*numHeads,
   'spc_id'                  : 35,
   'CWORD1'                  : (0x0100),  # No CWORD1 Options used
   'CWORD2'                  : 32,       # Force SNO if PEAK was not detected and set SNO Phase Detection.
   'DO_SNO'                  : (),
   'MEASURE_PHASE'           : (),
   'SNO_METHOD'              : 6,
   'PLOT_TYPE'               : 6,
   'START_CYL'               : (0x0005, 0x0910),  #ID test cylinder change from 320000 to 330000
   'END_CYL'                 : (0x0005, 0x0910),
   'HEAD_RANGE'              : (0),
   'FREQ_RANGE'              : (2000,3000,),      # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'FREQ_INCR'               : (24,),             # change from 24 to 10 (3rd May 2013)
   'NBR_NOTCHES'             : (1),
   'NBR_TFA_SAMPS'           : 14, #was 2000
   'NBR_MEAS_REPS'           : 3,
   'INJ_AMPL'                : 70,
   'PHASE_LIMIT'             : -1000, # for detecting the min phase value
   'NUM_SAMPLES'             : 10, # Only needed when SNO_METHOD = 5, peak normalization w/0 SNO
   'ZETA_1'                  : (int(0.020*1000), int(0.03*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_2'                  : (int(0.030*1000), int(0.09*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_3'                  : (int(0.050*1000), int(0.12*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_4'                  : (int(0.080*1000), int(0.16*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_5'                  : (int(0.040*1000), int(0.18*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'ZETA_6'                  : (int(0.280*1000), int(0.64*100)),  # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'PEAK_WIDTH'              : 10,
   'PTS_UNDR_PK'             : 3,
   'SHARP_THRESH'            : 0, # changed from 5 to 0
   'PEAK_SUMMARY'            : 2,
   'NOTCH_CONFIG'            : 0, # Configure each notch independently
   'NOTCH_TABLE'             : 0, #VCM
}

CktNotchesPD_152_ID_3 = [
   {
   'FILTERS'                 : 2**5,
   'FREQ_RANGE'              : (3500,5000,),
   'FREQ_INCR'               : 10,                         # change from 24 to 10 (3rd May 2013)
   'ZETA_6'                  : (int(0.28*1000),int(0.64*100)),
   'NBR_NOTCHES'             : (1),
   'BANDWIDTH'               : (750),
   'NOTCH_DEPTH'             : (1300),
   },
]

SNO_PHASE_DELTA_LIMIT = -360        # change limit from 30 to 33 deg phase loss (3rd May 2013)
SNO_GAIN_PK2PK_LIMIT = 40     # To verify gain data in SNO
SNO_LOOP_LIMIT = 3            # No of SNO loops (1 + 2x retry) to try if bode data is bogus
###############################################################################
################################## Test 0175 ##################################
# ------------------------------ Consolidate all T175 params ------------------------------
zapByZone_175 = {
   'test_num'                : 175,
   'prm_name'                : {
      'ATTRIBUTE'               : ('RUN_3P5PCT_ZAP', 'RUN_4PCT_ZAP'),
      'DEFAULT'                 : 'default',
      'default'                 : 'zapByZone_175_5pct',
      (1,0)                     : 'zapByZone_175_3P5pct',
      (0,1)                     : 'zapByZone_175_4pct',
   },
   'spc_id'                  : 1,
   'timeout'                 : 10 * 3600 * numHeads, # 10hrs per head
   'CWORD1'                  : {
      'ATTRIBUTE'               : 'FE_0234376_229876_T109_READ_ZFS',
      'DEFAULT'                 : 0,
      0                         : 0x71AB,
      1                         : 0x61AB,
   },
   'CWORD2'                  : 0x1500,   # ZBZ
   'CWORD3'                  : {
      'ATTRIBUTE'               : ('RUN_ZAP_TO_DATA_TPI', 'FE_0245014_470992_ZONE_MASK_BANK_SUPPORT'),
      'DEFAULT'                 : (1,0),
      (0,0)                     : 0x660, # READ_ZFS_ZBZ + FIXED_REV_READ + FIXED_REVS + RW_OPTM_SPANS_SHINGLE
      (1,0)                     : 0xE60, # ZAP_TO_DATA_TPI + READ_ZFS_ZBZ + FIXED_REV_READ + FIXED_REVS + RW_OPTM_SPANS_SHINGLE
      (0,1)                     : 0x260, # FIXED_REV_READ + FIXED_REVS + RW_OPTM_SPANS_SHINGLE
      (1,1)                     : 0xA60, # ZAP_TO_DATA_TPI + FIXED_REV_READ + FIXED_REVS + RW_OPTM_SPANS_SHINGLE
   },
   'START_CYL'               : (0x0000,0x0000,),
   'END_CYL'                 : (0xFFFF,0xFFFF,),
   'SEC_CYL'                 : (0,30000,), # ZBZ
   'HEAD_RANGE'              : 0x00FF,
   'MAX_ITERATION'           : 5, # 5 should be enough
   'GAIN'                    : 60,
   'INJ_AMPL'                : 300,
   'RZ_SETTLE_DELAY'         : {'EQUATION':'self.dut.servoWedges/4'},  # add 1/4 rev delay
   'RZ_VERIFY_AUDIT_INTERVAL': 2000,
   'WZ_VERIFY_AUDIT_INTERVAL': 500,
   'RD_REVS'                 : {
      'ATTRIBUTE'               : 'programName',
      'DEFAULT'                 : 'default',
      'default'                 : 2,
      'Rosewood7'               : 1,
      'Chengai'                 : 1,
   },
   'REVS'                    : 2,
   'RZ_RRO_AUDIT_INTERVAL'   : 2000,
   'WZ_RRO_AUDIT_INTERVAL'   : 500, # a factor affects ZBZ, set a big value for not ZBZ
   'RZAP_MABS_RRO_LIMIT'     : 287,   # 7%
   'SEC_RZAP_MABS_RRO_LIMIT' : 370,   # 9%
   'WZAP_MABS_RRO_LIMIT'     : {
      'ATTRIBUTE'               : ('RUN_3P5PCT_ZAP', 'RUN_4PCT_ZAP'),
      'DEFAULT'                 : 'default',
      'default'                 : 205,   # 5%
      (1,0)                     : 143,   # 3.5%
      (0,1)                     : 164,   # 4%
   },
   'SEC_WZAP_MABS_RRO_LIMIT' : {
      'ATTRIBUTE'               : ('RUN_3P5PCT_ZAP', 'RUN_4PCT_ZAP'),
      'DEFAULT'                 : 'default',
      'default'                 : 205,   # 5%
      (1,0)                     : 143,   # 3.5%
      (0,1)                     : 164,   # 4%
   },
   'START_HARM'              : {
      'ATTRIBUTE'               : 'CHENGAI',
      'DEFAULT'                 : 0,
      0                         : 11,
      1                         : 12,
   },
   'DISABLE_HARMONICS'       : {
      'ATTRIBUTE'               : 'CHENGAI',
      'DEFAULT'                 : 0,
      0                         : (0x0000,0x1000,),
      1                         : (0x0000,0x0000,),
   },
}
# ------------------------------ Consolidate all T175 params ------------------------------
zapByZone_175_forced = zapByZone_175.copy()
zapByZone_175_forced['prm_name'] = 'zapByZone_175_forced'

zapbasic_175 = {
   'test_num'                : 175,
   'prm_name'                : 'zapPrm_175_basicZAP',
   'timeout'                 : 4500 * numHeads,
   'spc_id'                  : 1,
   'CWORD1'                  : 0x71AB,   # blm Generate rd and wr ZAP, write/verfy fields in wedges,report summary,force valid ZAP flag in SAP
   'CWORD2'                  : 0x0000,   # blm 0x0400 sets the ZBZ flag - other ie bit 11 disable ACFF harmonics? (not used by ZBZ)
   'CWORD3'                  : {
      'ATTRIBUTE'               : ('SMR', 'FAST_2D_VBAR_TESTTRACK_CONTROL'),
      'DEFAULT'                 : 'default',
      'default'                 : 0x0240,      # FIXED_REV_READ + FIXED_REVS - fixed revs for both write and read
      (1,0)                     : 0x0260,      # FIXED_REV_READ + FIXED_REVS + CWORD3_RESERVED_BIT_5 - fixed revs for both write and read
   },
   'REVS'                    : 2,
   'RD_REVS'                 : { # need to enable cword3 bit 0x0200
      'ATTRIBUTE'               : 'programName',
      'DEFAULT'                 : 'default',
      'default'                 : 2,
      'Rosewood7'               : 1,
      'Chengai'                 : 1,
   },
   'MAX_ITERATION'           : 5,     # for poor PES head
   'WZAP_MABS_RRO_LIMIT'     : 143,   # 3.5%
   'RZAP_MABS_RRO_LIMIT'     : 287,   # 7%
   'AUDIT_INTERVAL'          : 100,   # a factor affects ZBZ if using ZBZ
   'GAIN'                    : 60,    # blm ZAP gain
   'START_HARM'              : 11,    # 3 screws drive
   'DISABLE_HARMONICS'       : (0x0000,0x1000,), # for ch12
   'INJ_AMPL'                : 300,   # blm needed for x-fer function/impulse response
   'RETRY_INCR'              : 6,     # Retry cylinder increment step size used in Microjog
   'RETRIES'                 : 1,
   'RZ_SETTLE_DELAY'         : {'EQUATION':'self.dut.servoWedges/4'},
   'WZ_SETTLE_DELAY'         : {'EQUATION':'self.dut.servoWedges/8'},
}
###############################################################################
################################## Test 0180 ##################################
ShockSensor_Screen_180 = {
   'test_num'                : 180,
   'prm_name'                : 'ShockSensor_Screen_180',
   'timeout'                 : 1200 * numHeads,
   'spc_id'                  : 11,
   'CWORD1'                  : 0x0110,
   'M0_FREQ_RANGE'           : (10,20),
   'M1_FREQ_RANGE'           : (20,40),
   'M2_FREQ_RANGE'           : (40,60),
   'M3_FREQ_RANGE'           : (60,80),
   'M4_FREQ_RANGE'           : (80,100),
   'M5_FREQ_RANGE'           : (100,120),
   'M6_FREQ_RANGE'           : (120,140),
   'M7_FREQ_RANGE'           : (140,160),
   'M8_FREQ_RANGE'           : (160,180),
   'TEST_HEAD'               : 255,
   'TEST_CYL'                : (1, 34464),
   'PES_REVS'                : 20,
   'FREQ_INCR'               : 20,
}

Resonance_Screen_180 = {
   'test_num'                : 180,
   'prm_name'                : 'Resonance_Screen_180',
   'timeout'                 : 1200 * numHeads,
   'spc_id'                  : 1,
   'CWORD1'                  : 40960,
   'M0_FREQ_RANGE'           : (60, 300),
   'M1_FREQ_RANGE'           : (300, 540),
   'M2_FREQ_RANGE'           : (540, 780),
   'M3_FREQ_RANGE'           : (780, 1020),
   'M4_FREQ_RANGE'           : (7500, 9000),
   'M5_FREQ_RANGE'           : (17500, 21500),
   'TEST_HEAD'               : 255,
   'PES_REVS'                : 10,
   'NUM_SEEKS'               : 30,
   'AMPL_LIMIT'              : (65535, 65535, 65535, 65535, 65535, 65535, 65535),
}
'''
prm_Resonance_OD_180 = {
   # OD
   'test_num'                : 180,
   'prm_name'                : 'prm_Resonance_OD_180_ServoParms',
   'timeout'                 : 1200 * numHeads,
   'spc_id'                  : 1,
   'TEST_HEAD'               : (0xFF,),
   'TEST_CYL'                : (0x0000,0x0064,),
   'PES_REVS'                : (10,),
   #'M0_FREQ_RANGE'           : (60, 300),
   #'M1_FREQ_RANGE'           : (300, 540),
   #'M2_FREQ_RANGE'           : (540, 780),
   'M3_FREQ_RANGE'           : (7500, 9000),
   'M4_FREQ_RANGE'           : (18000, 19500),
   'M5_FREQ_RANGE'           : (19500, 21000),
   'M6_FREQ_RANGE'           : (21000, 22500),
}
prm_Resonance_MD_180 = {
   # MD
   'test_num'                : 180,
   'prm_name'                : 'prm_Resonance_MD_180_ServoParms',
   'timeout'                 : 1200 * numHeads,
   'spc_id'                  : 1,
   'TEST_HEAD'               : (0xFF,),
   'TEST_CYL'                : (0x0002, 0xBF20,),
   'PES_REVS'                : (10,),
   #'M0_FREQ_RANGE'           : (60, 300),
   #'M1_FREQ_RANGE'           : (300, 540),
   #'M2_FREQ_RANGE'           : (540, 780),
   'M3_FREQ_RANGE'           : (7500, 9000),
   'M4_FREQ_RANGE'           : (18000, 19500),
   'M5_FREQ_RANGE'           : (19500, 21000),
   'M6_FREQ_RANGE'           : (21000, 22500),
}
prm_Resonance_ID_180 = {
   # ID
   'test_num'                : 180,
   'prm_name'                : 'prm_Resonance_ID_180_ServoParms',
   'timeout'                 : 1200 * numHeads,
   'spc_id'                  : 1,
   'TEST_HEAD'               : (0xFF,),
   'TEST_CYL'                : (0x0004,0x45C0,),
   'PES_REVS'                : (10,),
   #'M0_FREQ_RANGE'           : (60, 300),
   #'M1_FREQ_RANGE'           : (300, 540),
   #'M2_FREQ_RANGE'           : (540, 780),
   'M3_FREQ_RANGE'           : (7500, 9000),
   'M4_FREQ_RANGE'           : (18000, 19500),
   'M5_FREQ_RANGE'           : (19500, 21000),
   'M6_FREQ_RANGE'           : (21000, 22500),
   }
'''
prm_Resonance_OD_180 = {
   # OD
   'test_num'                : 180,
   'prm_name'                : 'prm_Resonance_OD_180',
   'timeout'                 : 1200*numHeads,
   'spc_id'                  : 1,
   'TEST_HEAD'               : (0xFF,),
   'TEST_CYL'                : (0,10,),
   'PES_REVS'                : (20,),
   'CWORD1'                  : (0x0001,),
}
prm_Resonance_MD_180 = {
   # MD
   'test_num'                : 180,
   'prm_name'                : 'prm_Resonance_MD_180',
   'timeout'                 : 1200*numHeads,
   'spc_id'                  : 1,
   'TEST_HEAD'               : (0xFF,),
   'TEST_CYL'                : (0x0001,0x86A0,),	#change to 100,000 for Desaru
   'PES_REVS'                : (20,),
   'CWORD1'                  : (0x0001,),
}
prm_Resonance_ID_180 = {
   # ID
   'test_num'                : 180,
   'prm_name'                : 'prm_Resonance_ID_180',
   'timeout'                 : 1200*numHeads,
   'spc_id'                  : 1,
   'TEST_HEAD'               : (0xFF,),
   'TEST_CYL'                : (0x3,0x0D40,),		#change to 200,000 for Desaru
   'PES_REVS'                : (20,),
   'CWORD1'                  : (0x0001,),
}

# build list of parameter dictionaries
if testSwitch.BF_0127147_357552_REFERENCE_T180_PARAM_BY_STRING_NAME:
   #references a string of the dictionary name
   prm_Resonance_180 = {
      'OD'                      : 'prm_Resonance_OD_180',
      'MD'                      : 'prm_Resonance_MD_180',
      'ID'                      : 'prm_Resonance_ID_180',
   }
else:
   #references actual dictionary
   prm_Resonance_180 = {
      'OD'                      : prm_Resonance_OD_180,
      'MD'                      : prm_Resonance_MD_180,
      'ID'                      : prm_Resonance_ID_180,
   }

Resonance_RRO_Screen_180 = {
   'test_num'              : 180,
   'prm_name'              : 'Resonance_RRO_Screen_180',
   'timeout'               : 1200 * numHeads,
   'spc_id'                : 100,
   'CWORD1'                : 40960,
   'M0_FREQ_RANGE'         : (7000, 7200),
   'M1_FREQ_RANGE'         : (7200, 7400),
   'M2_FREQ_RANGE'         : (7400, 7600),
   'M3_FREQ_RANGE'         : (7800, 8000),
   'M4_FREQ_RANGE'         : (8000, 8200),
   'M5_FREQ_RANGE'         : (8200, 8400),
   'M6_FREQ_RANGE'         : (8400, 8600),
   'M7_FREQ_RANGE'         : (8600, 8800),
   'M8_FREQ_RANGE'         : (8800, 9000),
   'TEST_HEAD'             : 255,
   'PES_REVS'              : 32,
   'NUM_SEEKS'             : 1,
   'AMPL_LIMIT'            : (65535, 65535, 65535, 65535, 65535, 65535, 65535),
   'M7_M8_RRO_AMPL_LIMIT'  : (65535, 65535),
}
###############################################################################
################################## Test 0185 ##################################
if testSwitch.EnableVariableGB_by_Ramp:
   RampDetectTestPrm_185 = {
      'test_num'                : 185,
      'prm_name'                : 'RampDetectTestPrm_185',
      'timeout'                 : 4000 * numHeads,
      'spc_id'                  : 1,
      'CWORD1'                  : (0x8504,), # bit 0x0400 for ramp detect track 0 cal
      'CWORD2'                  : (0x5000,),
      'TK0_LIMIT'               : (30000,),
      'PAD_TK_VALUE'            : (10400,),
      'GAIN'                    : (36,), # unload FCO, channel setting for FCO unload
      'GAIN2'                   : (15,), # unload FCO, channel setting of flaw numbers to detect ramp
      'ID_PAD_TK_VALUE'         : {
         'ATTRIBUTE' : 'IS_2D_DRV',
         'DEFAULT'   : 0,
         0           : {
            'ATTRIBUTE' : 'WTF',
            'DEFAULT'   : 'D0R0',
            'D0R0'      : (2900,),
            'D0R1'      : (34000,), # For 500G Rezone
            'D0RS'      : (34000,), # For 500G Rezone
            'D0RA'      : (34000,), # For 500G Rezone
            },
         1           : 2900,
         },
      'FINAL_LSHIFT_VALUE'      : (0x0004,),
      'SEEK_LENGTH'             : (0x0000,0x0064,),
      'SEEK_COUNT'              : (0x012C,),
      'MIN_HEAD_SKEW_VALUE'     : (0x0001,),
      'LSHIFT_VALUE'            : (0x0003,),
      'SEEK_TYPE'               : (0x28,),
      'NORMAL_STEP'             : (32,),
      'START_CYL'               : (0x0, 0x4E20),  # 20000
      'END_CYL'                 : {
         'ATTRIBUTE'               : 'HAMR',
         'DEFAULT'                 :  0,
         0                         :  (0x6, 0x0000),  # increase from 340000 (0x5, 0x3020)
         1                         :  (0x3, 0xA000),  # HAMR Starwood mule
      },
      'VTPI_USEORIMULTIPLIERS'  : (0,),
      'GB_BY_RAMP_CYL_P1'       : {
         'ATTRIBUTE'               : 'ADAPTIVE_GUARD_BAND',
         'DEFAULT'                 : 0,
         0                         : (17550,),
         1                         : {
            'ATTRIBUTE' : 'BG',
            'DEFAULT'   : 'OEM1B',
            'SBS'       : {
               'ATTRIBUTE'    : 'rerunReason',
               'DEFAULT'      : (),
               ()             : {
                  'ATTRIBUTE' : 'IS_2D_DRV',
                  'DEFAULT'   : 0,
                  0           : {
                     'ATTRIBUTE' : 'AABType',
                     'DEFAULT'   : '501.16',
                     '501.16'    : {
                        'ATTRIBUTE' : 'WTF',
                        'DEFAULT'   : 'D0R0',
                        'D0R0'      : (8000,),
                        'D0R1'      : (18000,), # For 500G Rezone
                        'D0RS'      : (18000,), # For 500G Rezone
                        'D0RA'      : (18000,), # For 500G Rezone
                        },
                     '501.42'    : {
                        'ATTRIBUTE' : 'WTF',
                        'DEFAULT'   : 'D0R0',
                        'D0R0'      : {
                           'ATTRIBUTE' : 'PROC_CTRL19',
                           'DEFAULT'   : '0',
                           '0'         : (9000,),
                           '1'         : (9500,),
                           },
                        'D0R1'      : (18000,), # For 500G Rezone
                        'D0RS'      : (18000,), # For 500G Rezone
                        'D0RA'      : (18000,), # For 500G Rezone
                        },
                     },
                  1           : {
                     'ATTRIBUTE' : 'AABType',
                     'DEFAULT'   : '501.16',
                     '501.16'    : (9000,),
                     '501.42'    : (9500,),
                     },
                  },
               ('PRE2', 'ZEST', 42174): {
                  'ATTRIBUTE' : 'IS_2D_DRV',
                  'DEFAULT'   : 0,
                  0           : {
                     'ATTRIBUTE' : 'WTF',
                     'DEFAULT'   : 'D0R0',
                     'D0R0'      : (9500,),
                     'D0R1'      : (18000,), # For 500G Rezone
                     'D0RS'      : (18000,), # For 500G Rezone
                     'D0RA'      : (18000,), # For 500G Rezone                     
                     },
                  1           : (10000,),
                  },
               ('PRE2', 'ZEST', 42176): {
                  'ATTRIBUTE' : 'IS_2D_DRV',
                  'DEFAULT'   : 0,
                  0           : {
                     'ATTRIBUTE' : 'WTF',
                     'DEFAULT'   : 'D0R0',
                     'D0R0'      : (9500,),
                     'D0R1'      : (18000,), # For 500G Rezone
                     'D0RS'      : (18000,), # For 500G Rezone
                     'D0RA'      : (18000,), # For 500G Rezone                     
                     },
                  1           : (10000,),
                  },
               },
            'OEM1B'     : {
               'ATTRIBUTE'               : 'IS_2D_DRV',
               'DEFAULT'                 : 0,
               0           : {
                  'ATTRIBUTE' : 'AABType',
                  'DEFAULT'   : '501.16',
                  '501.16'    : {
                     'ATTRIBUTE' : 'WTF',
                     'DEFAULT'   : 'D0R0',
                     'D0R0'      : (8000,),
                     'D0R1'      : (18000,), # For 500G Rezone
                     'D0RS'      : (18000,), # For 500G Rezone
                     'D0RA'      : (18000,), # For 500G Rezone
                     },
                  '501.42'    : {
                     'ATTRIBUTE' : 'WTF',
                     'DEFAULT'   : 'D0R0',
                     'D0R0'      : {
                        'ATTRIBUTE' : 'PROC_CTRL19',
                        'DEFAULT'   : '0',
                        '0'         : (9000,),
                        '1'         : (9500,),
                        },
                     'D0R1'      : (18000,), # For 500G Rezone
                     'D0RS'      : (18000,), # For 500G Rezone
                     'D0RA'      : (18000,), # For 500G Rezone
                     },
                  },
               1               : {
                  'ATTRIBUTE' : 'AABType',
                  'DEFAULT'   : '501.16',
                  '501.16'    : (9000,),
                  '501.42'    : (9500,),                  
                  },
               },
         },
      },
      'GB_BY_RAMP_CYL_P2'       : {
         'ATTRIBUTE'               : 'ADAPTIVE_GUARD_BAND',
         'DEFAULT'                 : 0,
         0                         : (4000,),
         1                         : {
            'ATTRIBUTE' : 'BG',
            'DEFAULT'   : 'OEM1B',
            'SBS'       : {
               'ATTRIBUTE'    : 'rerunReason',
               'DEFAULT'      : (),
               ()             : {
                  'ATTRIBUTE' : 'IS_2D_DRV',
                  'DEFAULT'   : 0,
                  0           : {
                     'ATTRIBUTE' : 'AABType',
                     'DEFAULT'   : '501.16',
                     '501.16'    : {
                        'ATTRIBUTE' : 'WTF',
                        'DEFAULT'   : 'D0R0',
                        'D0R0'      : (5000,),
                        'D0R1'      : (15000,), # For 500G Rezone
                        'D0RS'      : (15000,), # For 500G Rezone
                        'D0RA'      : (15000,), # For 500G Rezone                        
                        },
                     '501.42'    : {
                        'ATTRIBUTE' : 'WTF',
                        'DEFAULT'   : 'D0R0',
                        'D0R0'      : {
                           'ATTRIBUTE' : 'PROC_CTRL19',
                           'DEFAULT'   : '0',
                           '0'         : (6000,),
                           '1'         : (6500,),
                           },
                        'D0R1'      : (15000,), # For 500G Rezone
                        'D0RS'      : (15000,), # For 500G Rezone 
                        'D0RA'      : (15000,), # For 500G Rezone 
                        },
                     },
                  1           : {
                     'ATTRIBUTE' : 'AABType',
                     'DEFAULT'   : '501.16',
                     '501.16'    : (6000,),
                     '501.42'    : (6500,),
                     },
                  },
               ('PRE2', 'ZEST', 42174): {
                  'ATTRIBUTE' : 'IS_2D_DRV',
                  'DEFAULT'   : 0,
                  0           : {
                     'ATTRIBUTE' : 'WTF',
                     'DEFAULT'   : 'D0R0',
                     'D0R0'      : (6500,),
                     'D0R1'      : (15000,), # For 500G Rezone
                     'D0RS'      : (15000,), # For 500G Rezone
                     'D0RA'      : (15000,), # For 500G Rezone
                     },
                  1           : (7000,),
                  },
               ('PRE2', 'ZEST', 42176): {
                  'ATTRIBUTE' : 'IS_2D_DRV',
                  'DEFAULT'   : 0,
                  0           : {
                     'ATTRIBUTE' : 'WTF',
                     'DEFAULT'   : 'D0R0',
                     'D0R0'      : (6500,),
                     'D0R1'      : (15000,), # For 500G Rezone
                     'D0RS'      : (15000,), # For 500G Rezone
                     'D0RA'      : (15000,), # For 500G Rezone
                     },
                  1           : (7000,),
                  },
               },
            'OEM1B'     : {
               'ATTRIBUTE'               : 'IS_2D_DRV',
               'DEFAULT'                 : 0,
               0           : {
                  'ATTRIBUTE' : 'AABType',
                  'DEFAULT'   : '501.16',
                  '501.16'    : {
                     'ATTRIBUTE' : 'WTF',
                     'DEFAULT'   : 'D0R0',
                     'D0R0'      : (5000,),
                     'D0R1'      : (15000,), # For 500G Rezone
                     'D0RS'      : (15000,), # For 500G Rezone                     
                     'D0RA'      : (15000,), # For 500G Rezone
                     },
                  '501.42'    : {
                     'ATTRIBUTE' : 'WTF',
                     'DEFAULT'   : 'D0R0',
                     'D0R0'      : {
                        'ATTRIBUTE' : 'PROC_CTRL19',
                        'DEFAULT'   : '0',
                        '0'         : (6000,),
                        '1'         : (6500,), 
                        },
                     'D0R1'      : (15000,), # For 500G Rezone
                     'D0RS'      : (15000,), # For 500G Rezone   
                     'D0RA'      : (15000,), # For 500G Rezone                     
                     },
                  },
               1              : {
                  'ATTRIBUTE' : 'AABType',
                  'DEFAULT'   : '501.16',
                  '501.16'    : (6000,),
                  '501.42'    : (6500,),
                  },
               },
         },
      },
      'MIN_RAMPCYL_REQ'         : {
         'ATTRIBUTE'               : 'IS_2D_DRV',
         'DEFAULT'                 : 0,
         0                         : (3000, ),
         1                         : (3000, ),
      },
      'SHORT_RAMP_CLIP_CYL'     : (500,),
   }
else:
   RampDetectTestPrm_185 = {
      'test_num'                : 185,
      'prm_name'                : 'RampDetectTestPrm_185',
      'timeout'                 : 4000*numHeads,	   #4000*numHeads,
      'spc_id'                  : 1,
      'CWORD1'                  : (0x8504,), # bit 0x0400 for ramp detect track 0 cal
      'TK0_LIMIT'               : (26000,), #(0x43A8,), # (0x2BB8,),
      'PAD_TK_VALUE'            : {
         'ATTRIBUTE'               : 'HGA_SUPPLIER',
         'DEFAULT'                 : 'TDK',
         'TDK'                     : (8000,),
         'HWY'                     : (8000,),
         'RHO'                     : (8000,),
      },
      'GAIN'                    : (36,), # unload FCO, channel setting for FCO unload
      'GAIN2'                   : (15,), # unload FCO, channel setting of flaw numbers to detect ramp
      'ID_PAD_TK_VALUE'         : (2000,),
      'FINAL_LSHIFT_VALUE'      : (0x0004,),
      'SEEK_LENGTH'             : (0x0000,0x0064,),
      'SEEK_COUNT'              : (0x012C,),
      'MIN_HEAD_SKEW_VALUE'     : (0x0001,),
      'LSHIFT_VALUE'            : (0x0003,),
      'SEEK_TYPE'               : (0x28,),
      'VTPI_USEORIMULTIPLIERS'  :(0,),
   }

trkZeroCalPrm_185 = {
   'test_num'                : 185,
   'prm_name'                : 'trkZeroCalPrm_185',
   'timeout'                 : 1000 + 1000 * numHeads,
   'spc_id'                  : 1,
   'SEEK_LENGTH'             : (0x0000, 0x0064),
   'TK0_LIMIT'               : 0x2710,
   'ID_PAD_TK_VALUE'         : 50,
   'PAD_TK_VALUE'            : 9625,
   'DRIVE_TPI_VALUE'         : (0x0001, 0xD4C0),
   'MIN_HEAD_SKEW_VALUE'     : 0x0001,
   'FINAL_LSHIFT_VALUE'      : 0x0004,
   'CWORD1'                  : 0x0514,
   'SEEK_TYPE'               : 0x28,
   'SLOPE_CYL_1'             : (0x0000, 0x0000),
   'SLOPE_CYL_2'             : (0x0001, 0x0000),
   'NORMAL_STEP'             : (32,),
}
###############################################################################
################################## Test 0189 ##################################
dcSkewCalPrm_189 = {
   'test_num'                : 189,
   'prm_name'                : 'dcSkewCalPrm_189',
   'timeout'                 : 3000*numHeads,   #5400*numHeads,
   'spc_id'                  : 1,
   'START_CYL'               : (0x0000,0x0064,),
   'END_CYL'                 : (0xffff,0xffff,),
   'SEEK_STEP'               : (1266,),
   'LIMIT'                   : (0x1408,),
   'CWORD1'                  : (0x113C,), # Enable T189 Timing Skew Cal
   'THRESHOLD'               : {
      'ATTRIBUTE' : 'IS_2D_DRV',
      'DEFAULT'   : 0,
      0           : (12,),
      1           : {
         'ATTRIBUTE' : 'BG',
         'DEFAULT'   : 'OEM1B',
         'OEM1B'     : (12,),
         'SBS'       : {
            'ATTRIBUTE' : 'PROC_CTRL55',
            'DEFAULT'   : 'default',
            'default'   : (12,),
            '10806'     : (25,),
            },
         },
      },
   'TMNG_ERR_RANGE_LIMIT'    : (240,),
   'TMNG_FIT_ERR_REF_LIMIT'  : (20,),
   'SEEK_DELAY'              : (20,),
   'NUM_LOCS'                : (80,),
}
#dcSkewCalPrm_189.update({'CWORD1'       : (0x123C,),})
#dcSkewCalPrm_189.update({'SEEK_DELAY'   : (4,),})

dcSkewCalPrm_189_1 = {
   'test_num'                : 189,
   'prm_name'                : 'dcSkewCalPrm_189_1',
   'timeout'                 : 3000*numHeads,   #5400*numHeads,
   'spc_id'                  : 1,
   'START_CYL'               : (0x0000,0x0064,),
   'END_CYL'                 : (0xffff,0xffff,),
   'SEEK_STEP'               : (1266,),
   'LIMIT'                   : (0xFFFF,),   # was 0x1408
   'CWORD1'                  : (0x01BC,),
   'THRESHOLD'               : (12,),
   'TMNG_ERR_RANGE_LIMIT'    : (240,),
   'TMNG_FIT_ERR_REF_LIMIT'  : (20,),
   'SEEK_DELAY'              : (20,),
   'NUM_LOCS'                : (80,),
}

enableMDWUncalBit_11 = {
      'test_num'             : 11,
      'prm_name'             : 'enableMDWUncalBit_11',
      'spc_id'               : 1,
      'CWORD1'               : 0x0400,
      'SYM_OFFSET'           : 101,      #  Symbol Offset
      'WR_DATA'              : 0x6002,
      'MASK_VALUE'           : 0x0FF0,
      'NUM_LOCS'             : 0,
      'timeout'              : 120,
}

readMDWUncalBit_11 = {
      'test_num'             : 11,
      'prm_name'             : 'readMDWUncalBit_11',
      'spc_id'               : 1,
      'CWORD1'               : 0x0200,
      'SYM_OFFSET'           : 101,      #  Symbol Offset
      'NUM_LOCS'             : 0,
      'timeout'              : 120,
}

disableMDWUncalBit_11 = {
      'test_num'             : 11,
      'prm_name'             : 'disableMDWUncalBit_11',
      'spc_id'               : 1,
      'CWORD1'               : 0x0400,
      'SYM_OFFSET'           : 101,      #  Symbol Offset
      'WR_DATA'              : 0x2000,
      'MASK_VALUE'           : 0x0FF0,
      'NUM_LOCS'             : 0,
      'timeout'              : 120,
}

dcSkewCalPrmTTR_189 = {
   'test_num'                : 189,
   'prm_name'                : 'dcSkewCalPrm_189',
   'timeout'                 : 3600 * numHeads,
   'spc_id'                  : 1,
   'START_CYL'               : (0x0000, 0x0064),
   'END_CYL'                 : (0xFFFF, 0xFFFF),
   'SEEK_STEP'               : {
      'ATTRIBUTE'               : 'rpm',
      'DEFAULT'                 : '7202',
         '7202'                 : 2063,
         '5984'                 : 2528 
   },
   'CWORD1'                  : 0x1334,
   'THRESHOLD'               : 5,
   'SEEK_DELAY'              : 4,
   'LIMIT'                   : 0xFFFF,
   'SEEK_NUMS'               : 1,        # reduces the number of lead in headswitches from 600 to 1
   'LOOP_CNT'                : 24,       # reduces the number of headswitches at each calibration track to 24
}
###############################################################################
################################## Test 0193 ##################################
chromeCalPrm_193 = {
   'test_num'                : 193,
   'prm_name'                : 'chromeCalPrm_193',
   'timeout'                 : 1800*numHeads,   #7200,
   'spc_id'                  : 1,
   'CWORD1'                  : (0x1D68,),
   'HEAD_RANGE'              : (0x00FF,),
   'MAX_ITERATION'           : (6,),
   'MABS_RRO_LIMIT'          : (410,),
   'MABS_RRO_TARGET'         : (80,),
   'GAIN'                    : (240,),
   'START_HARM'              : (4,),
   'END_HARM'                : (32,),
   'INJ_AMPL'                : (800,),
   'NBR_ZONES'               : (12,),
   'NBR_CYLS'                : (400,),
   'GAIN2'                   : (96,),
   'ZAP_START_HARM'          : (4,),
}
###############################################################################
################################## Test 0194 ##################################
prm_194_ATS = {
   'test_num'                : 194,
   'prm_name'                : 'prm_194_ATS_ServoParms',
   'timeout'                 : 3600,
   'spc_id'                  : 1,
}
#################### TUNE ATS SEEK PROFILE ####################
TuneATS_194 = {
   'test_num'                : 194,
   'prm_name'                : 'Tune ATS',
   'CWORD1'                  : (22401,),
   'MABS_RRO_LIMIT'          : (180,),
   'START_HARM'              : (2,),
   'END_HARM'                : (55,),
   'timeout'                 : 1800,
   'MAX_ITERATION'           : (6,),
   'NBR_ZONES'               : (5,),
   'NBR_CYLS'                : (399,),
   'GAIN'                    : (95,),
   'PERCENT_LIMIT'           : (97,),
}
###############################################################################
################################## Test 0237 ##################################
FULL_STROKE_HI    = 0xFFFF       # Upper word of magic number used to denote Seek Length = FullStroke - 1000
FULL_STROKE_LO    = 0xFFFF       # Lower word of magic number used to denote Seek Length = FullStroke - 1000
UNUSED_POINT_HI   = 0x7FFF       # Upper word of a magic number used to denote an unused RPS_SEEK_LENGTH (in case all 16 are not needed)
UNUSED_POINT_LO   = 0xFFFF       # Lower word of a magic number used to denote an unused RPS_SEEK_LENGTH

RPS_Seek_237 = [
   {
   'test_num'                : 237,
   'prm_name'                : 'RPS_seekPrm_237_0',
   'timeout'                 : 30,
   'spc_id'                  : 1,
   'CWORD1'                  : 0x0010,
   'SEEK_TYPE'               : 0,                # JIT0
   'RPS_SEEK_LENGTHS'        : [0,800,
                                0,1157,
                                0,1468,
                                0,1974,
                                0,2895,
                                0,5682,
                                0,7729,
                                0,10073,
                                0,12956,
                                0,13097,
                                0,21647,
                                0,36814,
                                0,56659,
                                1,17412,
                                2,43028,
                                FULL_STROKE_HI, FULL_STROKE_LO],   # Full Stroke - 1000
   },
   {
   'test_num'                : 237,
   'prm_name'                : 'RPS_seekPrm_237_1',
   'timeout'                 : 30,
   'spc_id'                  : 1,
   'CWORD1'                  : 0x0010,
   'SEEK_TYPE'               : 1,                # JIT1
   'RPS_SEEK_LENGTHS'        : [0,800,
                                0,1157,
                                0,1468,
                                0,1974,
                                0,2895,
                                0,5682,
                                0,7729,
                                0,10073,
                                0,12956,
                                0,13097,
                                0,21647,
                                0,36814,
                                0,56659,
                                1,17412,
                                2,43028,
                                FULL_STROKE_HI, FULL_STROKE_LO],   # Full Stroke - 1000
   },
   {
   'test_num'                : 237,
   'prm_name'                : 'RPS_seekPrm_237_2',
   'timeout'                 : 30,
   'spc_id'                  : 1,
   'CWORD1'                  : 0x0010,
   'SEEK_TYPE'               : 2,                # JIT2
   'RPS_SEEK_LENGTHS'        : [0,800,
                                0,1157,
                                0,1468,
                                0,1974,
                                0,2895,
                                0,5682,
                                0,7729,
                                0,10073,
                                0,12956,
                                0,13097,
                                0,21647,
                                0,36814,
                                0,56659,
                                1,17412,
                                2,43028,
                                FULL_STROKE_HI, FULL_STROKE_LO],   # Full Stroke - 1000
   },
   {
   'test_num'                : 237,
   'prm_name'                : 'RPS_seekPrm_237_3',
   'timeout'                 : 30,
   'spc_id'                  : 1,
   'CWORD1'                  : 0x0010,
   'SEEK_TYPE'               : 3,                # JIT3
   'RPS_SEEK_LENGTHS'        : [0,800,
                                0,1157,
                                0,1468,
                                0,1974,
                                0,2895,
                                0,5682,
                                0,7729,
                                0,10073,
                                0,12956,
                                0,13097,
                                0,21647,
                                0,36814,
                                0,56659,
                                1,17412,
                                2,43028,
                                FULL_STROKE_HI, FULL_STROKE_LO],   # Full Stroke - 1000
   },
   {
   'test_num'                : 237,
   'prm_name'                : 'RPS_seekPrm_237_4',
   'timeout'                 : 30,
   'spc_id'                  : 1,
   'CWORD1'                  : 0x0010,
   'SEEK_TYPE'               : 0x10,
   'RD_SCALE_FACTORS'        : [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10],
   'WR_SCALE_FACTORS'        : [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10],
   },
   {
   'test_num'                : 237,
   'prm_name'                : 'RPS_seekPrm_237_5',
   'timeout'                 : 30,
   'spc_id'                  : 1,
   'CWORD1'                  : 0x0010,
   'SEEK_TYPE'               : 0x11,
   'RD_SCALE_FACTORS'        : [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10],
   'WR_SCALE_FACTORS'        : [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10],
   },
   {
   'test_num'                : 237,
   'prm_name'                : 'RPS_seekPrm_237_6',
   'timeout'                 : 30,
   'spc_id'                  : 1,
   'CWORD1'                  : 0x0010,
   'SEEK_TYPE'               : 0x12,
   'RD_SCALE_FACTORS'        : [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10],
   'WR_SCALE_FACTORS'        : [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10],
   },
   {
   'test_num'                : 237,
   'prm_name'                : 'RPS_seekPrm_237_7',
   'timeout'                 : 30,
   'spc_id'                  : 1,
   'CWORD1'                  : 0x0010,
   'SEEK_TYPE'               : 0x13,
   'RD_SCALE_FACTORS'        : [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10],
   'WR_SCALE_FACTORS'        : [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10],
   },
   {
   'test_num'                : 237,
   'prm_name'                : 'RPS_seekPrm_237',
   'timeout'                 : 3600,
   'spc_id'                  : 1,
   'CWORD1'                  : 0x006C,        # Production mode, using Physical Seek Lengths
   'SEEK_NUMS'               : 32,
   'LOOP_CNT'                : 5000,
   'SEEK_DELAY'              : 10,
   'SEEK_ERR_LIMIT'          : 100,
   'RD_STD_LIMIT'            : 75,
   'WRT_STD_LIMIT'           : 75,
   'RD_CONST_COEFF'          : 10,
   'WRT_CONST_COEFF'         : 10,
   },
]
###############################################################################
################################## Test 0257 ##################################
prm_RepeatableTMR_257 = {
   'test_num'                : 257,
   'prm_name'                : "prm_RepeatableTMR_257",
   'timeout'                 : 36000,
   'spc_id'                  : 1,
   'CWORD1'                  : (0x0000,),
   'CWORD2'                  : (0x0000,),
   'NBR_CYLS'                : (10,),
   'DISABLE_HARMONICS'       : (0x0004,0x1800,), #make sure this matches what the drive was processed with.
   'HEAD_RANGE'              : (0x00ff,),
   'START_HARM'              : (10,)  #make sure this matches what the drive was processed with.
}

prm_257_WirroMeas_SKDC_SERVO_TEST = {
   'test_num'                : 257,
   'prm_name'                : "SKDC_WirroMeas_257",
   'timeout'                 : 8800,
   'spc_id'                  : 1,
   'CWORD1'                  : 0x800,
   'CWORD2'                  : 256,
   'NBR_BINS'                : 11,
   'NBR_CYLS'                : 1,
   'BIN_SIZE'                : 1,
   'NBR_ZONES'               : 19,
   'HEAD_RANGE'              : 0,
   'START_HARM'              : (10,),
}
#################### T257 WIRRO ####################
Incoherent_WIRRO_Meas_H10_257 = {
   'test_num'                : 257,
   'prm_name'                : 'Incoherent_WIRRO_Meas',
   'timeout'                 : 4400 * numHeads,
   'spc_id'                  : 1,
   'CWORD1'                  : 0,
   'CWORD2'                  : 0x1902,
   'NBR_CYLS'                : 50,
   'NBR_ZONES'               : 4,
   'HEAD_RANGE'              : 0x00FF,
   'START_HARM'              : (10,),
   'DISABLE_HARMONICS'       : (32,0),
   'ZONE_STEP_SIZE'          : 25,
   'ZONE_POSITION'           : 20,
}
###############################################################################
################################## Test 0263 ##################################
#################### T263 Viterbi ####################
prm_263_ViterbiFir={
   'test_num'                : 263,
   'prm_name'                : 'prm_263_ViterbiFir',
   'timeout'                 : 3600,
   'CWORD1'                  : 0x1000,
}
prm_263_ViterbiTarget={
   'test_num'                : 263,
   'prm_name'                : 'prm_263_ViterbiTarget',
   'timeout'                 : 40000,
   'CWORD1'                  : 0x1400,
   'INTERVAL_SIZE'           : 4000,
   'SAMPLE_CNT'              : 8,
   'TAP1S_RANGE'             : 0xECEC,    #0x817D,    #0xEC34,    #0xC020,   #0xD40C,   #0xD010
   'TAP2S_RANGE'             : 0xEBEB,    #0xC404,    #0x817D,    #0xAA0A,    #0xBE1E,   #0xD20A,   #0xCE0E
}

prm_263_FIR_TAP_SWEEP_ID={
   'test_num'                : 263,
   'prm_name'                : 'prm_263_FIR_TAP_SWEEP_ID',
   'timeout'                 : 400000,
   'CWORD1'                  : 0x8000,
   'INTERVAL_SIZE'           : 1000,      #60000,     #2000,     #1000   
   'REVS'                    : 10,        #3,  
   'TAP1S_RANGE'             : 0xEC0A,    #0x817D,    #0xEC34,    #0xC020,   #0xD40C,   #0xD010
   'TAP2S_RANGE'             : 0xEB0F,    #0xC404,    #0x817D,    #0xAA0A,    #0xBE1E,   #0xD20A,   #0xCE0E
   'HEAD_RANGE'              : 0x00FF,
   'MAX_ERR_RATE'            : 3,
}
enableViterbi_11 = {
   'read'                    : {
      'test_num'                : 11,
      'prm_name'                : 'enableViterbi_11',
      'spc_id'                  : 1,
      'CWORD1'                  : 0x0200,
      'SYM_OFFSET'              : 510,      #  Symbol Offset
      'NUM_LOCS'                : 0,
      'timeout'                 : 120,
   },
}    
###############################################################################
################################## Test 0275 ##################################
zfs_275 = {
   'test_num'                   : 275,
   'prm_name'                   : 'zfs_275',
   'timeout'                    : 3600 * numHeads,
   'spc_id'                     : 1,
   'START_CYL'                  : (0x0000, 0x0000),
   'END_CYL'                    : (0xFFFF, 0xFFFF),
   'SEC_CYL'                    : (0,30000,), # ZBZ
   'HEAD_RANGE'                 : 0x00FF,
   'CWORD1'                     : 0x00C3,
   'WZAP_MABS_RRO_LIMIT'        : 143, # 3.5%
   'RZAP_MABS_RRO_LIMIT'        : 287, # 7%
   'SEC_WZAP_MABS_RRO_LIMIT'    : 143,
   'SEC_RZAP_MABS_RRO_LIMIT'    : 370, # 9%
   'RZ_SETTLE_DELAY'            : {'EQUATION':'self.dut.servoWedges/4'},  # add 1/4 rev delay
   'REVS'                       : 2,   # minimum revs
   'ITERATIONS'                 : {
      'ATTRIBUTE'               : 'IS_2D_DRV',
      'DEFAULT'                 : 0,
      0                         : {
         'ATTRIBUTE'  : 'BG',
         'DEFAULT'    : 'OEM1B',
         'OEM1B'      : 1,
         'SBS'        : 1,
      },
      1                         : 1,
   },
   'MAX_ITERATION'              : 5,
   'RZ_RRO_AUDIT_INTERVAL'      : 2000,
   'WZ_RRO_AUDIT_INTERVAL'      : 1000, # a factor affects ZBZ, set a big value for not ZBZ
   'RZ_VERIFY_AUDIT_INTERVAL'   : 2000,
   'WZ_VERIFY_AUDIT_INTERVAL'   : 500,
   'RD_REVS'                    : 1,
   'START_HARM'                 : {
      'ATTRIBUTE'                  : 'numPhysHds',
      'DEFAULT'                    : 2,
      2                            : 14, # RW1D, was 11x, change to 14x.
      4                            : 18, # RW2D, was 11x, change to 18x.
   },
   'DISABLE_HARMONICS'             : {
      'ATTRIBUTE'                  : 'numPhysHds',
      'DEFAULT'                    : 2,
      2                            : (0x0451,0x0000,), # RW1D, was 12x only.  change to disable harmonics 11,12,13,16,20,22,26
      4                            : (0x0410,0x0000,), # RW2D, was 12x only.  change to disable harmonics 20x,26x
   },
   'FREQUENCY'                  : 0x023B,
   'DblTablesToParse'         : ['P275_ZAP_SUMMARY'],
}

# T275, CWORD1
# 9  0x0200  Disable test failure
# 8  0x0100  Force ZAP to be disabled in SAP
# 7  0x0080  Force ZAP to be enabled in SAP
# 6  0x0040  Write ZAP to disk
# 5  0x0020  Retrieve transfer function from file
# 4  0x0010  Save transfer function to file
# 3  0x0008  Retrieve timing values from file
# 2  0x0004  Save timing values to file
# 1  0x0002  Perform operation for read position (legacy mode)
# 0  0x0001  Perform operation for write position
###############################################################################
################################## Test 0282 ##################################
#if testSwitch.FE_SGP_REPLACE_T152_WITH_T282:
doBodePrm_282_S_OD = {
   'test_num'                : 282,
   'prm_name'                : 'doBodePrm_282_S at OD',
   'timeout'                 : 800*numHeads,
   'spc_id'                  : 4,
   'FAIL_SAFE'               : (),
   'CWORD1'                  : (0x0082),
   'START_CYL'               : (0xFFFF,0xFFFD,),
   'END_CYL'                 : (0xFFFF,0xFFFD,),
   'HEAD_RANGE'              : (0xFFFF,),
   'FREQ_RANGE'              : (50,0xFFFF,),  # Tests from 500 Hz to (2 * Nyquist - 500 Hz)
   'FREQ_INCR'               : (0x19,),
   'INJ_AMPL'                : (500,),
   'INJECTION_CURRENT'       : (300,),
   'RANGE'                   : (120,220,),
   'GAIN_LIMIT'              : (1000,),
   'SHARP_THRESH'            : (0,),
   'WRITE_CURRENT_ADJ'       : (200,), # starting injection amplitude for FREQ_RESP_OPEN_LOOP_VCM_CURRENT = 0
   'INPUT_VOLTAGE'           : (200,), # starting injection amplitude for FREQ_RESP_OPEN_LOOP_DAC_VOLTAGE = 1
}

doBodePrm_282_S_MD = {
   'test_num'                : 282,
   'prm_name'                : 'doBodePrm_282_S at MD',
   'timeout'                 : 800*numHeads,
   'spc_id'                  : 5,
   'FAIL_SAFE'               : (),
   'CWORD1'                  : (0x0082),
   'START_CYL'               : (0xFFFF,0xFFFE,),
   'END_CYL'                 : (0xFFFF,0xFFFE,),
   'HEAD_RANGE'              : (0xFFFF,),
   'FREQ_RANGE'              : (50,0xFFFF,),  # Tests from 500 Hz to (2 * Nyquist - 500 Hz)
   'FREQ_INCR'               : (0x19,),
   'INJ_AMPL'                : (500,),
   'INJECTION_CURRENT'       : (300,),
   'RANGE'                   : (120,220,),
   'GAIN_LIMIT'              : (1000,),
   'SHARP_THRESH'            : (0,),
   'WRITE_CURRENT_ADJ'       : (200,), # starting injection amplitude for FREQ_RESP_OPEN_LOOP_VCM_CURRENT = 0
   'INPUT_VOLTAGE'           : (200,), # starting injection amplitude for FREQ_RESP_OPEN_LOOP_DAC_VOLTAGE = 1
}

doBodePrm_282_S_ID = {
   'test_num'                : 282,
   'prm_name'                : 'doBodePrm_282_S at ID',
   'timeout'                 : 800*numHeads,
   'spc_id'                  : 6,
   'FAIL_SAFE'               : (),
   'CWORD1'                  : (0x0082),
   'START_CYL'               : (0xFFFF,0xFFFF,),
   'END_CYL'                 : (0xFFFF,0xFFFF,),
   'HEAD_RANGE'              : (0xFFFF,),
   'FREQ_RANGE'              : (50,0xFFFF,),  # Tests from 500 Hz to (2 * Nyquist - 500 Hz)
   'FREQ_INCR'               : (0x19,),
   'INJ_AMPL'                : (500,),
   'INJECTION_CURRENT'       : (300,),
   'RANGE'                   : (120,220,),
   'GAIN_LIMIT'              : (1000,),
   'SHARP_THRESH'            : (0,),
   'WRITE_CURRENT_ADJ'       : (200,), # starting injection amplitude for FREQ_RESP_OPEN_LOOP_VCM_CURRENT = 0
   'INPUT_VOLTAGE'           : (200,), # starting injection amplitude for FREQ_RESP_OPEN_LOOP_DAC_VOLTAGE = 1
}
if testSwitch.FE_0264856_480505_USE_OL_GAIN_INSTEAD_OF_S_GAIN_IN_282:
   # Open Loop gain instead of Sensitivity gain in doBodePrm_282
   doBodePrm_282_S_OD['prm_name'] = 'doBodePrm_282_OL at OD'
   doBodePrm_282_S_OD["CWORD1"]   = (0x0080)
   doBodePrm_282_S_MD['prm_name'] = 'doBodePrm_282_OL at MD'
   doBodePrm_282_S_MD["CWORD1"]   = (0x0080)
   doBodePrm_282_S_ID['prm_name'] = 'doBodePrm_282_OL at ID'
   doBodePrm_282_S_ID["CWORD1"]   = (0x0080)

doBodePrm_282_S_Score_OD = {
   'test_num'                : 282,
   'prm_name'                : 'doBodePrm_282_S_Score at OD',
   'timeout'                 : 800*numHeads,
   'spc_id'                  : 44,
   'FAIL_SAFE'               : (),
   'CWORD1'                  : (0x0086),
   'START_CYL'               : (0x0,0x4269,),
   'END_CYL'                 : (0x0,0x4269,),
   'HEAD_RANGE'              : (0xFFFF,),
   'FREQ_RANGE'              : (50,0xFFFF,),
   'FREQ_INCR'               : (0x19,),	#25,
   'INJ_AMPL'                : (500,),
   'INJECTION_CURRENT'       : (300,),
   'RANGE'                   : (120,220,),
   'GAIN_LIMIT'              : (1000,),
   'SHARP_THRESH'            : (0,),
   'WRITE_CURRENT_ADJ'       : (200,), # starting injection amplitude for FREQ_RESP_OPEN_LOOP_VCM_CURRENT = 0
   'INPUT_VOLTAGE'           : (200,), # starting injection amplitude for FREQ_RESP_OPEN_LOOP_DAC_VOLTAGE = 1
}

doBodePrm_282_S_Score_ID = {
   'test_num'                : 282,
   'prm_name'                : 'doBodePrm_282_S_Score at ID',
   'timeout'                 : 800*numHeads,
   'spc_id'                  : 66,
   'FAIL_SAFE'               : (),
   'CWORD1'                  : (0x0086),
   'START_CYL'               : (0x5,0xF501,),
   'END_CYL'                 : (0x5,0xF501,),
   'HEAD_RANGE'              : (0xFFFF,),
   'FREQ_RANGE'              : (50,0xFFFF,),
   'FREQ_INCR'               : (0x19,),	#25,
   'INJ_AMPL'                : (500,),
   'INJECTION_CURRENT'       : (300,),
   'RANGE'                   : (120,220,),
   'GAIN_LIMIT'              : (1000,),
   'SHARP_THRESH'            : (0,),
   'WRITE_CURRENT_ADJ'       : (200,), # starting injection amplitude for FREQ_RESP_OPEN_LOOP_VCM_CURRENT = 0
   'INPUT_VOLTAGE'           : (200,), # starting injection amplitude for FREQ_RESP_OPEN_LOOP_DAC_VOLTAGE = 1
}

doBodePrm_282_VCM_structural_OD = {
   'test_num'                : 282,
   'prm_name'                : 'doBodePrm_282_VCM_structural_OD',
   'timeout'                 : 800*numHeads,
   'spc_id'                  : 1,
   'FAIL_SAFE'               : (),
   'CWORD1'                  : (0x8),
   'START_CYL'               : (0xFFFF,0xFFFD,),
   'END_CYL'                 : (0xFFFF,0xFFFD,),
   'HEAD_RANGE'              : (0xFFFF,),
   'FREQ_RANGE'              : (50,0xFFFF,),  # Tests from 500 Hz to (2 * Nyquist - 500 Hz)
   'FREQ_INCR'               : (0x19,),
   'INJ_AMPL'                : (500,),
   'INJECTION_CURRENT'       : (300,),
   'RANGE'                   : (120,220,),
   'GAIN_LIMIT'              : (1000,),
   'SHARP_THRESH'            : (0,),
}

doBodePrm_282_VCM_structural_MD = {
   'test_num'                : 282,
   'prm_name'                : 'doBodePrm_282_VCM_structural_MD',
   'timeout'                 : 800*numHeads,
   'spc_id'                  : 2,
   'FAIL_SAFE'               : (),
   'CWORD1'                  : (0x8),
   'START_CYL'               : (0xFFFF,0xFFFE,),
   'END_CYL'                 : (0xFFFF,0xFFFE,),
   'HEAD_RANGE'              : (0xFFFF,),
   'FREQ_RANGE'              : (50,0xFFFF,),  # Tests from 500 Hz to (2 * Nyquist - 500 Hz)
   'FREQ_INCR'               : (0x19,),
   'INJ_AMPL'                : (500,),
   'INJECTION_CURRENT'       : (300,),
   'RANGE'                   : (120,220,),
   'GAIN_LIMIT'              : (1000,),
   'SHARP_THRESH'            : (0,),
}

doBodePrm_282_VCM_structural_ID = {
   'test_num'                : 282,
   'prm_name'                : 'doBodePrm_282_VCM_structural_ID',
   'timeout'                 : 800*numHeads,
   'spc_id'                  : 3,
   'FAIL_SAFE'               : (),
   'CWORD1'                  : (0x8),
   'START_CYL'               : (0xFFFF,0xFFFF,),
   'END_CYL'                 : (0xFFFF,0xFFFF,),
   'HEAD_RANGE'              : (0xFFFF,),
   'FREQ_RANGE'              : (50,0xFFFF,),  # Tests from 500 Hz to (2 * Nyquist - 500 Hz)
   'FREQ_INCR'               : (0x19,),
   'INJ_AMPL'                : (500,),
   'INJECTION_CURRENT'       : (300,),
   'RANGE'                   : (120,220,),
   'GAIN_LIMIT'              : (1000,),
   'SHARP_THRESH'            : (0,),
}

doBodePrm_282_VCM_structural_ID_1 = {
   'test_num'                : 282,
   'prm_name'                : 'doBodePrm_282_VCM_structural_ID_1',
   'timeout'                 : 800*numHeads,
   'spc_id'                  : 100,
   'FAIL_SAFE'               : (),
   'CWORD1'                  : (0x8),
   'START_CYL'               : (0xFFFF,0xFFFF,),
   'END_CYL'                 : (0xFFFF,0xFFFF,),
   'HEAD_RANGE'              : (0xFFFF,),
   'FREQ_RANGE'              : (50,0xFFFF,),  # Tests from 500 Hz to (2 * Nyquist - 500 Hz)
   'FREQ_INCR'               : (0x19,),
   'INJ_AMPL'                : (500,),
   'INJECTION_CURRENT'       : (300,),
   'RANGE'                   : (120,220,),
   'GAIN_LIMIT'              : (1000,),
   'SHARP_THRESH'            : (0,),
}

doBodePrm_282_uAct_structural_OD = {
   'test_num'                : 282,
   'prm_name'                : 'doBodePrm_282_uAct_structural_OD',
   'timeout'                 : 800*numHeads,
   'spc_id'                  : 7,
   'FAIL_SAFE'               : (),
   'CWORD1'                  : (0x10),
   'START_CYL'               : (0xFFFF,0xFFFD,),
   'END_CYL'                 : (0xFFFF,0xFFFD,),
   'HEAD_RANGE'              : (0xFFFF,),
   'FREQ_RANGE'              : (50,0xFFFF,),  # Tests from 500 Hz to (2 * Nyquist - 500 Hz)
   'FREQ_INCR'               : (0x19,),
   'INJ_AMPL'                : (200,),
   'GAIN_LIMIT'              : (1000,),
   'SHARP_THRESH'            : (0,),
}

doBodePrm_282_uAct_structural_MD = {
   'test_num'                : 282,
   'prm_name'                : 'doBodePrm_282_uAct_structural_MD',
   'timeout'                 : 800*numHeads,
   'spc_id'                  : 8,
   'FAIL_SAFE'               : (),
   'CWORD1'                  : (0x10),
   'START_CYL'               : (0xFFFF,0xFFFE,),
   'END_CYL'                 : (0xFFFF,0xFFFE,),
   'HEAD_RANGE'              : (0xFFFF,),
   'FREQ_RANGE'              : (50,0xFFFF,),  # Tests from 500 Hz to (2 * Nyquist - 500 Hz)
   'FREQ_INCR'               : (0x19,),
   'INJ_AMPL'                : (200,),
   'GAIN_LIMIT'              : (1000,),
   'SHARP_THRESH'            : (0,),
}

doBodePrm_282_uAct_structural_ID = {
   'test_num'                : 282,
   'prm_name'                : 'doBodePrm_282_uAct_structural_ID',
   'timeout'                 : 800*numHeads,
   'spc_id'                  : 9,
   'FAIL_SAFE'               : (),
   'CWORD1'                  : (0x10),
   'START_CYL'               : (0xFFFF,0xFFFF,),
   'END_CYL'                 : (0xFFFF,0xFFFF,),
   'HEAD_RANGE'              : (0xFFFF,),
   'FREQ_RANGE'              : (50,0xFFFF,),  # Tests from 500 Hz to (2 * Nyquist - 500 Hz)
   'FREQ_INCR'               : (0x19,),
   'INJ_AMPL'                : (200,),
   'GAIN_LIMIT'              : (1000,),
   'SHARP_THRESH'            : (0,),
}

doBodePrm_282_XVFF_structural_OD = {
   'test_num'                : 282,
   'prm_name'                : 'doBodePrm_282_XVFF_structural_OD',
   'timeout'                 : 800*numHeads,  
   'spc_id'                  : 21,
   'FAIL_SAFE'               : (),
   'CWORD1'                  : (0x0401),
   'START_CYL'               : (0xFFFF,0xFFFD,),
   'END_CYL'                 : (0xFFFF,0xFFFD,),
   'HEAD_RANGE'              : (0xFFFF,),
   'FREQ_RANGE'              : (500,17000,),  # Tests from 500 Hz to (2 * Nyquist - 500 Hz)
   'FREQ_INCR'               : (0x19,),
   'INJ_AMPL'                : (500,),
   'INJECTION_CURRENT'       : (300,),
   'RV_LIMIT'                : (100,),
   'RANGE'                   : (120,220,),
   'GAIN_LIMIT'              : (1000,),
   "SHARP_THRESH"            : (0,),
}

doBodePrm_282_XVFF_structural_MD = {
   'test_num'                : 282,
   'prm_name'                : 'doBodePrm_282_XVFF_structural_OD',
   'timeout'                 : 800*numHeads,  
   'spc_id'                  : 22,
   'FAIL_SAFE'               : (),
   'CWORD1'                  : (0x0401),
   'START_CYL'               : (0xFFFF,0xFFFE,),
   'END_CYL'                 : (0xFFFF,0xFFFE,),
   'HEAD_RANGE'              : (0xFFFF,),
   'FREQ_RANGE'              : (500,17000,),  # Tests from 500 Hz to (2 * Nyquist - 500 Hz)
   'FREQ_INCR'               : (0x19,),
   'INJ_AMPL'                : (500,),
   'INJECTION_CURRENT'       : (300,),
   'RV_LIMIT'                : (100,),
   'RANGE'                   : (120,220,),
   'GAIN_LIMIT'              : (1000,),
   "SHARP_THRESH"            : (0,),
}

doBodePrm_282_XVFF_structural_ID = {
   'test_num'                : 282,
   'prm_name'                : 'doBodePrm_282_XVFF_structural_OD',
   'timeout'                 : 800*numHeads,  
   'spc_id'                  : 23,
   'FAIL_SAFE'               : (),
   'CWORD1'                  : (0x0401),
   'START_CYL'               : (0xFFFF,0xFFFF,),
   'END_CYL'                 : (0xFFFF,0xFFFF,),
   'HEAD_RANGE'              : (0xFFFF,),
   'FREQ_RANGE'              : (500,17000,),  # Tests from 500 Hz to (2 * Nyquist - 500 Hz)
   'FREQ_INCR'               : (0x19,),
   'INJ_AMPL'                : (500,),
   'INJECTION_CURRENT'       : (300,),
   'RV_LIMIT'                : (100,),
   'RANGE'                   : (120,220,),
   'GAIN_LIMIT'              : (1000,),
   "SHARP_THRESH"            : (0,),
}

#==============================================================================
#  Common SNO / SNOBZ parameters:
#     This section defines all T288 parameters that are exactly the same on
#     each call to T282 when SNO or SNOBZ is executed.
#==============================================================================
doBodeSNO_282 = {
   'test_num'                : 282,
   'prm_name'                : 'doBodeSNO_282',
   'timeout'                 : 6000,
   'FREQ_INCR'               : 49,
   'HEAD_RANGE'              : (0x00FF),               # All heads
   'FREQ_RANGE'              : (500,0xFFFF,),  # Tests from 500 Hz to (2 * Nyquist - 500 Hz)
   'FREQ_INCR'               : 24,
   'INJ_AMPL'                : (500,),
   'INJECTION_CURRENT'       : (300,),
   'RANGE'                   : (120,220,),
   'GAIN_LIMIT'              : (1000,),
   'SHARP_THRESH'            : (0,),
   'START_CYL'               : (0, 10000), # OD (5% of max cyl)
   'END_CYL'                 : (0, 10000), # OD (5% of max cyl)
   'SNO_METHOD'              : 1,
   'PEAK_SUMMARY'            : 2,
   'NUM_FCS_CTRL'            : 0,
   #'PEAK_GAIN_MIN'           : -30,
   'PEAK_WIDTH'              : 250,
   'CWORD2'                  : 0x0001,
   # NOTE: 'NUM_FCS_CTRL' defaults to 0, but is shown here as a remainder that you must specify which controller response is to be used.
   # If more than one VCM and/or DAC controller is included in the file, this parameter is used to select the one to be used during SNO/SNOBZ.
   # 0 selects the first VCM and DAC controller, 1 selects the second controller (for both VCM and DAC), and so on...
}

#==============================================================================
#  VCM Notch specific parameters:
#     This section is a list of parameter sets that represent each unique T282
#     call used to place VCM notches.  Each parameter set is combined with the
#     common parameters (above) to invoke T282 to place a single notch (SNO)
#     or multiple notches (SNOBZ).  Through any combiantion of single notch or
#     multi-notch placement calls, you should provide parameter sets to ensure
#     all optimized notches are placed - ie: all notches which cannot be left
#     as defaults for all drives.
#==============================================================================
# BANDWIDTH is not scaled and NOTCH_DEPTH are scaled up by 100.
# SNO_GAIN_RATIO is scaled up by 100.
snoNotches_282_VCM = [
# VCM SNO Parameters for all heads
   {
   'NOTCH_TABLE'             : 0,
   'CWORD1'                  : 0x2108,
   'FREQ_LIMIT'              : (10600,11800,),
   'FREQ_RANGE'              : (10600,11800,),
   'FREQ_INCR'               : 24,
   'FILTERS'                 : 2**2, # 3rd Notch
   'NBR_NOTCHES'             : (1),
   'PEAK_GAIN_MIN'           : 5,
   'BANDWIDTH'               : 760,
   'NOTCH_DEPTH'             : 1900,
   'SNO_METHOD'              : 1,
   'HEAD_RANGE'              : (0x00FF),
   },
]

snoNotches_282_VCM2 = [
# VCM SNO Parameters for all heads
   {
   'NOTCH_TABLE'             : 0,
   'CWORD1'                  : 0x2108,
   'FREQ_LIMIT'              : (28000,31500,),
   'FREQ_RANGE'              : (28000,31500,),
   'FREQ_INCR'               : 24,
   'FILTERS'                 : 2**6, # 7th Notch
   'NBR_NOTCHES'             : (1),
   'PEAK_GAIN_MIN'           : 5,
   'BANDWIDTH'               : 1800,
   'NOTCH_DEPTH'             : 1400,
   'SNO_METHOD'              : 1,
   'HEAD_RANGE'              : (0x00FF),
   },
]
#==============================================================================
#  uActuator Notch specific parameters:
#     This section is a list of parameter sets that represent each unique T282
#     call used to place DAC notches.  Each parameter set is combined with the
#     common parameters (above) to invoke T282 to place a single notch (SNO)
#     or multiple notches (SNOBZ).  Through any combiantion of single notch or
#     multi-notch placement calls, you should provide parameter sets to ensure
#     all optimized notches are placed - ie: all notches which cannot be left
#     as defaults for all drives.
#==============================================================================
snoNotches_282_DAC = [
# DAC SNO Parameters for all heads
   {
   'NOTCH_TABLE'             : 2,
   'CWORD1'                  : 0x2110,
   'FREQ_LIMIT'              : (10600,11800,),
   'FREQ_RANGE'              : (10600,11800,),
   'FREQ_INCR'               : 24,
   'FILTERS'                 : 2**1, # 2nd Notch
   'NBR_NOTCHES'             : (1),
   'PEAK_GAIN_MIN'           : 5,
   'BANDWIDTH'               : 1500,
   'NOTCH_DEPTH'             : 1400,
   'SNO_METHOD'              : 1,
   'HEAD_RANGE'              : (0x00FF),
   },
]

snoNotches_282_DAC2 = [
# DAC SNO Parameters for all heads
   {
   'NOTCH_TABLE'             : 2,
   'CWORD1'                  : 0x2110,
   'FREQ_LIMIT'              : (28000,32000,),
   'FREQ_RANGE'              : (28000,32000,),
   'FREQ_INCR'               : 24,
   'FILTERS'                 : 2**7, # 8th Notch
   'NBR_NOTCHES'             : (1),
   'PEAK_GAIN_MIN'           : 5,
   'BANDWIDTH'               : 1800,
   'NOTCH_DEPTH'             : 1400,
   'SNO_METHOD'              : 1,
   'HEAD_RANGE'              : (0x00FF),
   },
]

load_unload_profile_025 = {
  "test_num"     : 25,
  "prm_name"     : "load_unload_profile_025",
  "timeout"      : 1200*numHeads,
  "spc_id"       : 30,
  "CWORD1"       : (0x9540,),     # (0x0080,), # run lul test - bit6 = get LUL params from servo symbol table.
  "NUM_SAMPLES"  : (10,),         # how many times to run load/unload
  "DELAY_TIME"   : (1000,),       # delay between load/unload in ms
  "TIMER_OPTION" : (30,),         # Timer0 interrupt interval in us
  "GAIN"         : (32768,),      # 1/K_dac in bit/V, K_dac = 1/(2^15)in V/bit
  "GAIN2"        : (490,),        # K_pa in mA/V, Rf_Rin_ratio / (Gs * Rs) *1000 = 1000 / (3 * 0.68)
  "SCALED_VAL"   : (17587,),      # Velocity_BitsPerIps * 1000 in bit/1000ips, millivolt_per_ips/adc_resolution=1000*Kt*adc_amplifiergain/VCM_pivot_to_gap/adc_resolution=1000*0.01295*5/1.31/(2.4/2^10)
  "RPM"          : (167,),
  "LIMIT"        : (400,),        # Load Peak Current Limit in mA
  "LIMIT2"       : (400,),        # Unload Peak Current Limit in mA
  "SPINDLE_DIP_LIMIT" : (109,),   # Spindle dip limit
}

sno_phase_peak_detect_RW1D_282_OD = {
   'test_num'                : 282,
   'prm_name'                : 'doSNOPhasePrm_282',
   'timeout'                 : 4000*numHeads,
   'spc_id'                  :20,
   'CWORD1'                  :(0x0208),  # No CWORD1 Options used
   'CWORD2'                  : (0x60),       # Bit5, Bit6
   'START_CYL'               : (0, 10000),
   'END_CYL'                 : (0, 10000),
   'HEAD_RANGE'              : (0),
   'FREQ_RANGE'              : (2200,3500,),      # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'FREQ_INCR'               : (10,),             # change from 24 to 10 (3rd May 2013)
   'NBR_NOTCHES'             : (1),
   'NBR_TFA_SAMPS'           : 14, #was 2000
   'NBR_MEAS_REPS'           : 3,
   'INJ_AMPL'                : 70,
   'PHASE_LIMIT'             : -500,  #-1000, # for detecting the min phase value
   'NUM_SAMPLES'             : 10, # Only needed when SNO_METHOD = 5, peak normalization w/0 SNO
   'PEAK_WIDTH'              : 10,
   'PTS_UNDR_PK'             : 3,
   'SHARP_THRESH'            : 0, # changed from 5 to 0
   'PEAK_SUMMARY'            : 2,
   'NOTCH_CONFIG'            : 0, # Configure each notch independently
   'NOTCH_TABLE'             : 0, #VCM
   #'dlfile'                  : 'hubble1d54_bin_CTLR_BIN.bin'
   'MIN_BW_THRESH'           : 70,    #ThetMaung (13/Aug/2015)
   'MAX_BW_THRESH'           : 300,  #ThetMaung (13/Aug/2015)
}

CktNotchesPD_RW1D_282_OD = [
   {
   'FILTERS'                 : 2**6, #2**1, Change from 2nd to 7th location (13/Jul/2015)
   'FREQ_RANGE'              : (2200,3500,),
   'FREQ_INCR'               : 10,                         # change from 24 to 10 (3rd May 2013)
   'NBR_NOTCHES'             : (1),
   'BANDWIDTH'               : (750),
   'NOTCH_DEPTH'             : (1300),
   },
]

sno_phase_peak_detect_RW1D_282_ID = {
   'test_num'                : 282,
   'prm_name'                : 'doSNOPhasePrm_282',
   'timeout'                 : 4000*numHeads,
   'spc_id'                  : 21,
   'CWORD1'                  : (0x0208),  # No CWORD1 Options used
   'CWORD2'                  : (0x60),       # Force SNO if PEAK was not detected and set SNO Phase Detection.
   'START_CYL'               : (0x0004, 0xE200),  #(0, 10000),
   'END_CYL'                 : (0x0004, 0xE200),  #(0, 10000),
   'HEAD_RANGE'              : (0),
   'FREQ_RANGE'              : (1300,1800,),      # default value but gets overwritten by the data in the snoNotches_152 dictionary
   'FREQ_INCR'               : (10,),             # change from 24 to 10 (3rd May 2013)
   'NBR_NOTCHES'             : (1),
   'NBR_TFA_SAMPS'           : 14, #was 2000
   'NBR_MEAS_REPS'           : 3,
   'INJ_AMPL'                : 70,
   'PHASE_LIMIT'             : -500,  #-1000, # for detecting the min phase value
   'NUM_SAMPLES'             : 10, # Only needed when SNO_METHOD = 5, peak normalization w/0 SNO
   'PEAK_WIDTH'              : 10,
   'PTS_UNDR_PK'             : 3,
   'SHARP_THRESH'            : 0, # changed from 5 to 0
   'PEAK_SUMMARY'            : 2,
   'NOTCH_CONFIG'            : 0, # Configure each notch independently
   'NOTCH_TABLE'             : 0, #VCM
   #'dlfile'                  : 'hubble1d54_bin_CTLR_BIN.bin'
   'MIN_BW_THRESH'           : 70,
   'MAX_BW_THRESH'           : 300,
}

CktNotchesPD_RW1D_282_ID = [
   {
   'FILTERS'                 : 2**7, #8th notch
   'FREQ_RANGE'              : (1300,1800,),  #For 1.6kHz
   'FREQ_INCR'               : 10,
   'NBR_NOTCHES'             : (1),
   'BANDWIDTH'               : (750),
   'NOTCH_DEPTH'             : (1300),
   },
]
###############################################################################
################################## Test 0287 ##################################
# ZEST
prism_zest_287 = {
   'test_num'                : 287,
   'prm_name'                : 'prism_zest_287',
   'timeout'                 : 4200 * numHeads,
   'spc_id'                  : 1,
   # CWORD1 controls the following functions
   # bit 0: (0x0001) save ZEST table to disk
   # bit 1: (0x0002) force disable ZEST in SAP
   # bit 2: (0x0004) force enable ZEST in SAP
   # bit 3: (0x0008) perform PRISM
   'CWORD1'                  : {
      'ATTRIBUTE'               : 'ENABLE_ZEST_BIT_IN_SAP',
      'DEFAULT'                 : '0',
      '0'                       : 0xB,
      '1'                       : 0xD, 
   },
   # CWORD2 controls the reporting functions used for verification
   'CWORD2'                  : 0x0000,                  # no display
   'CUT_OFF_FRQ'             : (45, 205, 205, 0, 0),
   'HEAD_RANGE'              : 0x00FF,                  # All heads
   'ID_PAD_TK_VALUE'         : {
       'ATTRIBUTE'              : 'RUN_ZEST',
       'DEFAULT'                : '0',
       '0'                      : 1206, # 80% of ID_PAD_TK_VALUE from T185. See ServoParameters.py. For Grenada Luxor this is 1508*0.8 = 1206. Automate?
       '1'                      : 1000, # SSDC extended zest coverage for ID
   },                 
   'PAD_TK_VALUE'            : {
       'ATTRIBUTE'              : 'RUN_ZEST',
       'DEFAULT'                : '0',
       '0'                      : 9788, # 80% of PAD_TK_VALUE from T185. See ServoParameters.py. For Grenada Luxor this is 12236*0.8 = 9788. Automate?
       '1'                      : 3000, # SSDC extended zest coverage for OD 
   },                 
   'MEAS_REP_CNT'            : (16,4,2,0,0),            # The number of RRO averages per iteration by velocity.
   'MAX_ITER'                : (32,32,32,0,0),          # Maximum PRISM iteration count by velocity.
   'VELOCITY'                : (320,80,40,0,0,),        # Velocities for constant vel PRISM seeks. A zero ends the list. These are scaled up by 10. For example: 100 = 10 tracks/sector.
   'JOG_ERR_THRSH'           : 0xFFFF,
   'NBR_BINS'                : 31,                      # extend binning for P287_PHYS_SPACING_HSTGRM
   'JOG_BIN_SIZE'            : 30,                      # extend bin size for P287_JOG_ERROR_HSTGRM
   'BIN_SIZE'                : 30,                      # extend bin size for P287_PHYS_SPACING_HSTGRM
   'RETRY_LIMIT'             : 0,                       # remove retry for single track zest spike issue  
   'THRESHOLD'               : 0x800,                   # retry threshold set to 0.5 track
   'SEEK_ERR_LIMIT'          : 0x2000,                  # limit max PES err (2 tracks) during CV seek
   'SQZ_THRSH'               : 0xFFFF,
}
if testSwitch.SCOPY_TARGET:
   prism_zest_287.update({'ID_PAD_TK_VALUE': 1000,
                          'timeout'        :  {"EQUATION": "8400 * self.dut.imaxHead"},
                          'CWORD2'         : {'ATTRIBUTE': 'ENABLE_SHORT_PRE2',
                                              'DEFAULT': 0,
                                              0: 0x0000,
                                              1: 0x0001,},
                          'CWORD1'         : {'ATTRIBUTE': 'ENABLE_SHORT_PRE2',
                                              'DEFAULT': 0,
                                              0: 0x000D,
                                              1: 0x0008,},
                          })

prism_zest_on_287 = {
   'test_num'                : 287,
   'prm_name'                : 'prism_zest_287',
   'timeout'                 : 4200 * numHeads,
   'spc_id'                  : 1,
   # CWORD1 controls the following functions
   # bit 0: (0x0001) save ZEST table to disk
   # bit 1: (0x0002) force disable ZEST in SAP
   # bit 2: (0x0004) force enable ZEST in SAP
   # bit 3: (0x0008) perform PRISM
   'CWORD1'                  : 0x0004,
   # CWORD2 controls the reporting functions used for verification
   'CWORD2'                  : 0x0000,                  # no display
   'CUT_OFF_FRQ'             : (45, 205, 205, 0, 0),
   'HEAD_RANGE'              : 0x00FF,                  # All heads
   'ID_PAD_TK_VALUE'         : {
      'ATTRIBUTE'               : 'RUN_ZEST',
      'DEFAULT'                 : '0',
      '0'                       : 1206,                    # 80% of ID_PAD_TK_VALUE from T185. See ServoParameters.py. For Grenada Luxor this is 1508*0.8 = 1206. Automate?
      '1'                       : 0, 
   },
   'PAD_TK_VALUE'            : {
      'ATTRIBUTE'               : 'RUN_ZEST',
      'DEFAULT'                 : '0',
      '0'                       : 9788,                    # 80% of PAD_TK_VALUE from T185. See ServoParameters.py. For Grenada Luxor this is 12236*0.8 = 9788. Automate?
      '1'                       : 0, 
   },
   'MEAS_REP_CNT'            : (16,4,2,0,0),            # The number of RRO averages per iteration by velocity.
   'MAX_ITER'                : (32,32,32,0,0),          # Maximum PRISM iteration count by velocity.
   'VELOCITY'                : (320,80,40,0,0,),        # Velocities for constant vel PRISM seeks. A zero ends the list. These are scaled up by 10. For example: 100 = 10 tracks/sector.
   'JOG_ERR_THRSH'           : 0xFFFF,
   'SQZ_THRSH'               : 0xFFFF,
}

prism_zest_off_287 = {
   'test_num'                : 287,
   'prm_name'                : 'prism_zest_287',
   'timeout'                 : 4200 * numHeads,
   'spc_id'                  : 1,
   # CWORD1 controls the following functions
   # bit 0: (0x0001) save ZEST table to disk
   # bit 1: (0x0002) force disable ZEST in SAP
   # bit 2: (0x0004) force enable ZEST in SAP
   # bit 3: (0x0008) perform PRISM
   'CWORD1'                  : 0x0002,
   # CWORD2 controls the reporting functions used for verification
   'CWORD2'                  : 0x0000,                  # no display
   'CUT_OFF_FRQ'             : (45, 205, 205, 0, 0),
   'HEAD_RANGE'              : 0x00FF,                  # All heads
   'ID_PAD_TK_VALUE'         : {
      'ATTRIBUTE'               : 'RUN_ZEST',
      'DEFAULT'                 : '0',
      '0'                       : 1206,                    # 80% of ID_PAD_TK_VALUE from T185. See ServoParameters.py. For Grenada Luxor this is 1508*0.8 = 1206. Automate?
      '1'                       : 0, 
   },
   'PAD_TK_VALUE'            : {
      'ATTRIBUTE'               : 'RUN_ZEST',
      'DEFAULT'                 : '0',
      '0'                       : 9788,                    # 80% of PAD_TK_VALUE from T185. See ServoParameters.py. For Grenada Luxor this is 12236*0.8 = 9788. Automate?
      '1'                       : 0, 
   },
   'MEAS_REP_CNT'            : (16,4,2,0,0),            # The number of RRO averages per iteration by velocity.
   'MAX_ITER'                : (32,32,32,0,0),          # Maximum PRISM iteration count by velocity.
   'VELOCITY'                : (320,80,40,0,0,),        # Velocities for constant vel PRISM seeks. A zero ends the list. These are scaled up by 10. For example: 100 = 10 tracks/sector.
   'JOG_ERR_THRSH'           : 0xFFFF,
   'SQZ_THRSH'               : 0xFFFF,
}

prism_zest_display_status_287 = {
   'test_num'                : 287,
   'prm_name'                : 'prism_zest_287',
   'timeout'                 : 4200 * numHeads,
   'spc_id'                  : 1,
   # CWORD1 controls the following functions
   # bit 0: (0x0001) save ZEST table to disk
   # bit 1: (0x0002) force disable ZEST in SAP
   # bit 2: (0x0004) force enable ZEST in SAP
   # bit 3: (0x0008) perform PRISM
   'CWORD1'                  : 0,
   # CWORD2 controls the reporting functions used for verification
   'CWORD2'                  : 0x0000,                  # no display
   'CUT_OFF_FRQ'             : (45, 205, 205, 0, 0),
   'HEAD_RANGE'              : 0x00FF,                  # All heads
   'ID_PAD_TK_VALUE'         : {
      'ATTRIBUTE'               : 'RUN_ZEST',
      'DEFAULT'                 : '0',
      '0'                       : 1206,                    # 80% of ID_PAD_TK_VALUE from T185. See ServoParameters.py. For Grenada Luxor this is 1508*0.8 = 1206. Automate?
      '1'                       : 0, 
   },
   'PAD_TK_VALUE'            : {
      'ATTRIBUTE'               : 'RUN_ZEST',
      'DEFAULT'                 : '0',
      '0'                       : 9788,                    # 80% of PAD_TK_VALUE from T185. See ServoParameters.py. For Grenada Luxor this is 12236*0.8 = 9788. Automate?
      '1'                       : 0, 
   },
   'MEAS_REP_CNT'            : (16,4,2,0,0),            # The number of RRO averages per iteration by velocity.
   'MAX_ITER'                : (32,32,32,0,0),          # Maximum PRISM iteration count by velocity.
   'VELOCITY'                : (320,80,40,0,0,),        # Velocities for constant vel PRISM seeks. A zero ends the list. These are scaled up by 10. For example: 100 = 10 tracks/sector.
   'JOG_ERR_THRSH'           : 0xFFFF,
   'SQZ_THRSH'               : 0xFFFF,
}
###############################################################################
################################## Test 0332 ##################################
pztCal_332 = {
   'test_num'                : 332,
   'prm_name'                : 'PZT gain cal',
   'CWORD1'                  : (0x0128,),	# phase base gain cal
   'HEAD_RANGE'              : (0x00FF,),
   'TEST_CYL'                : (0,20000,),
   'timeout'                 : 150,
   'spc_id'                  : 1,
}

pztCal_332_1 = {
   'test_num'                : 332,
   'prm_name'                : 'PZT gain check',
   'CWORD1'                  : (0x002C,),
   'HEAD_RANGE'              : (0x00FF,),
   'TEST_CYL'                : (0,20000,),
   'timeout'                 : 150,
   'spc_id'                  : 2,
}

pztCal_332_2 = {
   'test_num'                : 332,
   'prm_name'                : 'PZT stress and check',
   'GAIN'                    : (10,),
   'INPUT_VOLTAGE'           : (8,),
   'FREQUENCY'               : (2000,),
   'CWORD1'                  : (0x0002,), # chengai = 0x0006 
   'HEAD_RANGE'              : (0x00FF,),
   'TEST_CYL'                : (0,20000,),
   'timeout'                 : 150,
   'spc_id'                  : 3,
}
###############################################################################
################################## Test 0335 ##################################
MDW_SCAN_Prm_335 = {
   'test_num'                : 335,
   'prm_name'                : 'MDW_SCAN_Prm_335',
   'timeout'                 : 900 * numHeads,
   'spc_id'                  : 1,
   'CWORD1'                  : 0xA000,            # Ignore seek errors (don't fail the test if seek to any track fails), Enable limit checking
   #'TEST_HEAD'               : 1,
   'HEAD_RANGE'              : 0x00FF,
   'PRETHRESH_MIN'           : 16,
   'PRETHRESH_MAX'           : 20,
   'PRETHRESH_S2T'           : 1,
   'ACQFLAW_MIN'             : 1,
   'ACQFLAW_MAX'             : 2,
   'LIMIT_S2T'               : 0xFFFF,
}

MDW_SCAN_OD_MD_Prm_335 = {
   'test_num'                : 335,
   'prm_name'                : 'MDW_SCAN_OD_MD_Prm_335',
   'timeout'                 : 900 * numHeads,
   'spc_id'                  : 1,
   'CWORD1'                  : 0xA000,            # Ignore seek errors (don't fail the test if seek to any track fails), Enable limit checking
   #'TEST_HEAD'               : 1,
   'HEAD_RANGE'              : 0x00FF,
   'PRETHRESH_MIN'           : 16,
   'PRETHRESH_MAX'           : 20,
   'PRETHRESH_S2T'           : 1,
   'ACQFLAW_MIN'             : 1,
   'ACQFLAW_MAX'             : 2,
   'LIMIT_S2T'               : 0xFFFF,
   'MDW_CERT_TRKS'           : (15, 15, 10, 70, 0, 15),
}

MDW_SCAN_ID_Prm_335 = {
   'test_num'                : 335,
   'prm_name'                : 'MDW_SCAN_ID_Prm_335',
   'timeout'                 : 900 * numHeads,
   'spc_id'                  : 1,
   'CWORD1'                  : 0xA000,            # Ignore seek errors (don't fail the test if seek to any track fails), Enable limit checking
   #'TEST_HEAD'               : 1,
   'HEAD_RANGE'              : 0x00FF,
   'PRETHRESH_MIN'           : 16,
   'PRETHRESH_MAX'           : 20,
   'PRETHRESH_S2T'           : 1,
   'ACQFLAW_MIN'             : 1,
   'ACQFLAW_MAX'             : 2,
   'LIMIT_S2T'               : 0xFFFF,
   'MDW_CERT_TRKS'           : (0, 15, 0, 70, 15, 15),
   'PREAMBLE_LMTS'           : (18, 120),
}
###############################################################################
#################### FAFH ####################
ReadFAFH_AllowAccessBit_172 = {
   'test_num'                : 172,
   'prm_name'                : 'ReadFAFH_AllowAccessBit',
   'CWORD1'                  : 33,
   'C_ARRAY1'                : [0, 34, 0, 0, 0, 0, 0, 0, 0, 0],
   'timeout'                 : 1000,
}

AllowFAFH_AccessBit_178 = {
   'test_num'                : 178,
   'prm_name'                : 'AllowFAFH_AccessBit',
   'CWORD1'                  : 33,
   'C_ARRAY1'                : [0, 34, 0, 0, 0, 0, 0, 0, 0, 1],
   'timeout'                 : 1000,
}
DisallowFAFH_AccessBit_178 = {
   'test_num'                : 178,
   'prm_name'                : 'DisallowFAFH_AccessBit',
   'CWORD1'                  : 33,
   'C_ARRAY1'                : [0, 34, 0, 0, 0, 0, 0, 0, 0, 0],
   'timeout'                 : 1000,
}

#################### T180 Resonance RRO SCRN ####################
TCC_UPDATE_172 = {
   'test_num'            : 172,
   'prm_name'            : 'TCC_UPDATE_172',
   'timeout'             : 1000,
   'CWORD1'              : 124,
}   

