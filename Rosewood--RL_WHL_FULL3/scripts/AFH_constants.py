#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2009, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: All global constants live within this file
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/06 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/AFH_constants.py $
# $Revision: #2 $
# $DateTime: 2016/05/06 00:36:23 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/AFH_constants.py#2 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#


from Test_Switches import testSwitch

if testSwitch.winFOF == 1:
   from cmEmul import *

# AFH constants
AFH_TRACK = 0
AFH_DET   = 1
AFH_TEMP  = 2
AFH_RdClr = 0
AFH_WrtLoss = 1
AFH_WHClr = 2
AFH_CLRDICT_ZONE_INDEX = 3
AFH_RdDac = 1
AFH_WHDac = 0

AFH_final_table = 255      # When the consistency check index reaches this value then declare this value as the "final table"
AFH_WHDAC = 0
AFH_HODAC = 1


AFH_MODE = 0
AR_MODE = 1
AFH_MODE_TEST_135_INTERPOLATED_DATA = 2
AFH_MODE_TEST_135_EXTREME_ID_OD_DATA = 3     # not to be used in standard screens, so it can't be standard AFH_MODE data.
AFH_INVALID_FH_STATE = 0xF0
AFH_WHMODE = 'Write+Heat'
AFH_HOMODE = 'Heat_Only'
if testSwitch.HAMR:
   AFH_MAX_NUM_COEFS_IN_RAP_PER_EQN_TYPE = 29
else:
   AFH_MAX_NUM_COEFS_IN_RAP_PER_EQN_TYPE = 21
AFH_EXCD_MAX_DELTA_LMT = 10298
AFH_CONTACT_BY_SERVO = 14682
AFH_FASTIO_ERROR = 14657
AFH_UNINITIALIZED_AFH_STATE = 0
AFH_UNKNOWN_AFH_STATE = 99
if testSwitch.FE_0175461_231166_P_SET_0X80_0_ALL_TRUNK_AFH_STATES:
   AFH_ERROR_CODE_DAC_MAXED_OUT = 14925
else:
   AFH_ERROR_CODE_DAC_MAXED_OUT = 14567
AFH_ANGSTROMS_PER_MICROINCH = 254.0
AFH_MICRO_INCHES_TO_ANGSTROMS = 254.0
AFH_TEST135_INTERPOLATED_SYMBOL = "I"
AFH_TEST135_MEASURED_SYMBOL = "M"
AFH_TEST135_CWORD2_EXTRME_OD_ID_RUN = 0x0020
AFH_V3BAR_STATUS_GIVE_UP = 2
AFH_DEFAULT_DAC_VALUE = -1
AFH_TCS_MINIMUM_NUM_COMMON_VALID_TEST_135_MEASUREMENTS = 3
AFH_RETURN_CODE_MEASURE_TCC_LESS_THAN_MINIMUM_NUM_COMMON_VALID_MEASUREMENTS = -2
AFH_TEST191_MINIMUM_NUM_ZONES_BEFORE_SKIPPING_ZONES_IN_CONCURRENT_HIRP = 20
AFH_IF_CLR_IN_MICROINCHES_SCALE_BY_254_ELSE_SCALE_BY_1 = AFH_ANGSTROMS_PER_MICROINCH

TEST135_DISPLAY_DICTIONARY = 1
TEST135_DISPLAY_DICTIONARY_AND_VERTICAL_SORTED_KEYS = 2

HIRP_DEFAULT_SPC_ID = 9000 # the number 9000 has no meaning, it is arbitrary.
   # It should never be used if it is, hopefully an unusual number will get someone's attention

if testSwitch.RUN_T191_HIRP_OPEN_LOOP == 1:
   LIST_VALID_CLOSED_LOOP_HIRP_STATES = [0xFF]
else:
   LIST_VALID_CLOSED_LOOP_HIRP_STATES = [40]

AFH_TEST178_GAMMA_H_CWORD3 = 0x0070
AFH_TEST178_GAMMA_W_CWORD3 = 0x0380
AFH_TEST178_GAMMA_R_CWORD3 = 0xE000


if testSwitch.FE_AFH3_TO_SAVE_CLEARANCE_TO_RAP == 1:

   AFH_LIST_STATES_TO_UPDATE_CLEARANCE = [1, 2, 3,40]
else:
   AFH_LIST_STATES_TO_UPDATE_CLEARANCE = [1, 2, 40]

AFH_LIST_STATES_TO_UPDATE_CERT_TEMP = [1,2]

WRITER_HEATER_INDEX = 0
READER_HEATER_INDEX = 1

heaterElementNameToFramesDict = {
   "WRITER_HEATER" : WRITER_HEATER_INDEX,
   "READER_HEATER" : READER_HEATER_INDEX,
   }
framesIndexToHeaterElementName = {
   WRITER_HEATER_INDEX  : "WRITER_HEATER",
   READER_HEATER_INDEX  : "READER_HEATER",
   }

heaterElementTableLongNameToShortNameDict = {
   "WRITER_HEATER": "W",
   "READER_HEATER": "R",
}

FAFH_SELF_TEST_HIGH_TEMPERATURE     = 0
FAFH_SELF_TEST_LOW_TEMPERATURE      = 1


stateTableToAFH_internalStateNumberTranslation = {
   "AFH1": 1,
   "AFH1_SCREENS": 1,
   "AFH1_DSP": 1,
   "ADDLLIWP": 1,
   "ADDLLIWP2": 1,
   "AFH2": 2,

   "AFH2A": 5,    # re-VBAR only
   "AFH2B": 2,    # re-VBAR only

   "AFH3": 3,
   "AFH4": 4,
   "TCC_BY_BER":5,
   "SETTLING":6,
   "HSC_TCC_HT":7,
   "HSC_TCC_LT":8,
   "TCC_UPDATE":9,
   "HSC_SLP_W":10,
   "HSC_SLP_R1":11,   
   "HSC_SLP_R2":12,
   "HEAD_SCRN":13,
   "TCC_VARIFY":14,
   "READ_SCRN2H":16,      

   # Misc AFH States in 20's
   "INIT_RAP": 20,    # this could be state 0, but that is already taken with AFH_UNINITIALIZED_AFH_STATE
   "INIT_SYS": 21,
   "VER_SYS": 22,
   "VER_RAMP": 23,
   "RESTART_VBAR": 24,
   "V3BAR": 25,
   "PREP_RERUN_AFH2": 26,
   "INIT_RAP_DSP": 27,
   "HIRP1A_DSP": 28,
   "VER_RAMP2": 29,

   # SWD states in 30's
   "SWD_VER" :  30,
   "SWD_VERIFY" :  30,
   "SWD_VER1":  30,
   "SWD_VER2":  31,
   "SWD_VER3":  32,

   "SWD_CAL" :  33,
   "SWD_CAL1":  33,
   "SWD_ADJUST":  34,



   # HIRP states in 40's
   "HIRP1": 40,
   "HIRP1A": 40,
   "HIRP1_DSP": 40,
   "HIRP1B": 41,
   "HIRP2": 42,
   "WIRP1A": 43,

   # FAFH states in 50's
   "FAFH_FREQ_SELECT"   : 50,
   "FAFH_TRACK_PREP"    : 51,
   "FAFH_TRACK_PREP_1"  : 51,
   "FAFH_TRACK_PREP_2"  : 52,
   "FAFH_TRACK_PREP_3"  : 53,
   "FAFH_CAL_TEMP_1" : 55,
   "FAFH_CAL_TEMP_2" : 56,

   #states with AFH utilities
   "READ_SCRN2" : 60,
   "PV_SCRN"    : 61,
   
   "AFH_COEFF_GEN"      : 81,
   "AFH_COEFF_ADJ"      : 82,

   "INIT"  : 90,
   "FH2B"  : 91,
   "FAIL_PROC": 92,        # necessary for depop code to work correctly.
   "FAIL_PROC_MANT": 92,
   
   #two plug process
   "OFF_TCC": 100,
   "ON_TCC" : 101,
   
   "DTH_OFF": 102,
   "DTH_ON" : 103,
   "DTH_OFF2" : 104,
   "DTH_ON2" : 105,

}

stateTableToHIRP_SPC_ID_encoding = {
   "HIRP1": 11000,
   "HIRP1A": 11000,
   "HIRP1B": 12000,
   "HIRP1C": 13000,

   "HIRP2": 21000,
   "HIRP2A": 21000,
   "HIRP2B": 22000,
   "HIRP2C": 23000,

   "HIRP3": 31000,

}

if testSwitch.AFH_ENABLE_ANGSTROMS_SCALER_USE_254 == 1:
   angstromsScaler = 1
else:
   angstromsScaler = 254.0

AFH_STATE_FOR_SAVING_HUMIDITY_TO_RAP = "AFH2"
