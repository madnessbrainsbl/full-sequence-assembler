#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Vbar RAP Tools Module
#  - Contains various RAP related functions
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
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/VBAR_Constants.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/VBAR_Constants.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#

from Constants import *
from TestParamExtractor import TP
from Drive import objDut
from Utility import getVBARPrintDbgMsgFunction

###########################################################################################################
######################### I N T E R N A L   D E B U G   F L A G S #########################################
###########################################################################################################
# NOTE: All these flags here should be zero for production
# Validate with external tools if necessary
verbose = 0       # Set to a value greater than 0 for various levels of debug output in the log.
verifyPicker = 0  # Set to 1 to enable auto-VE to run in the CPicker class, (Note: Tons of added data to the log)
debug_VE = 0
debug_LBR = 0 and testSwitch.FE_0261758_356688_LBR
debug_RF = 0

Q0toQ15Factor = 32768
Q0toQ14Factor = 16384

# Define a constant that will be used to prevent infinite loops due to rounding error associated with DBLog
# floating data that has been truncated to 4 digits for a string, and converted back to a float for comparison.
RndErrCorrFactor = 1e-7

# Defines from T210_prv.h that can be used for BPI and TPI format adjustment
# CWORD1
SET_BPI =                     0x0001
SET_TPI =                     0x0002

# CWORD2
CW2_SET_TRACK_PITCH =         0x0010
CW2_SET_TRACK_GUARD =         0x0020
CW2_SET_WRT_FAULT_THRESHOLD = 0x0040
CW2_SET_SQUEEZE_MICROJOG =    0x0080
CW2_SET_SHINGLED_DIRECTION =  0x0100
CW2_SET_TRACKS_PER_BAND =     0x0200
if testSwitch.FE_0325260_348085_P_VARIABLE_GUARD_TRACKS_FOR_ISO_BAND_ISOLATION:
   CW2_SET_NUM_GUARD_TRACKS   =  0x4000

SHINGLE_DIRECTION_OD_TO_ID =  0
SHINGLE_DIRECTION_ID_TO_OD =  1

T210_PARM_NUM_HEADS        =  16

TPI_MAX = TP.TPI_MAX
BPI_MAX = TP.BPI_MAX
TPI_MIN = TP.TPI_MIN
BPI_MIN = TP.BPI_MIN

###########################################################################################################
################################# V B A R   S E T T I N G S ###############################################
###########################################################################################################

# ATPI Picker error codes
ATPI_PASS                  = 0
ATPI_FAIL_CAPABILITY       = 1
ATPI_FAIL_PERFORMANCE      = 2
ATPI_FAIL_CAPACITY         = 3
ATPI_FAIL_HEAD_COUNT       = 4
ATPI_FAIL_SATURATION       = 5
ATPI_DEPOP_RESTART         = 6
ATPI_FAIL_NO_NIBLET        = 7
ATPI_FAIL_HMS_CAPABILITY   = 8
ATPI_FAIL_MINIMUM_THRUPUT  = 9
ATPI_FAIL_IMBALANCED_HEAD  = 10
ATPI_INVALID_DATA          = 100.00
ATPI_FAIL_OTC              = 11

maxBPI = {}
if testSwitch.FE_0163083_410674_RETRIEVE_P_VBAR_NIBLET_TABLE_AFTER_POWER_RECOVERY and \
   testSwitch.FE_0164322_410674_RETRIEVE_P_VBAR_TABLE_AFTER_POWER_RECOVERY:
   dblogOccCnt = \
   {
      'P211_VBAR_CAPS_WPPS'      : 1,
      'P_VBAR_NIBLET'            : objDut.OCC_VBAR_NIBLET,
      'P_VBAR_SUMMARY2'          : 1,
      'P_VBAR_MEASUREMENTS'      : 1,
      'VBAR_PICKER_DATA'         : 1,
      'P_WRT_PWR_PICKER'         : objDut.OCC_PWR_PICKER,
      'P_WRT_PWR_TRIPLETS'       : objDut.OCC_PWR_TRIPLETS,
      'P_SETTLING_SUMMARY'       : 1,
      'P_VBAR_PICKER_FMT_ADJUST' : 1,
      'P_VBAR_PICKER_RESULTS'    : 1,
      'P_VBAR_CLRNC_ADJUST'      : 1,
      'P_SMR_FORMAT_SUMMARY'     : 1,
   }
else:
   dblogOccCnt = \
   {
      'P211_VBAR_CAPS_WPPS'      : 1,
      'P_VBAR_NIBLET'            : 1,
      'P_VBAR_SUMMARY2'          : 1,
      'P_VBAR_MEASUREMENTS'      : 1,
      'VBAR_PICKER_DATA'         : 1,
      'P_WRT_PWR_PICKER'         : 1,
      'P_WRT_PWR_TRIPLETS'       : 1,
      'P_SETTLING_SUMMARY'       : 1,
      'P_VBAR_PICKER_FMT_ADJUST' : 1,
      'P_VBAR_PICKER_RESULTS'    : 1,
      'P_VBAR_CLRNC_ADJUST'      : 1,
      'P_SMR_FORMAT_SUMMARY'     : 1,
   }

printDbgMsg = getVBARPrintDbgMsgFunction()
