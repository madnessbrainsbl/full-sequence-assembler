#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Test Parameters for Extreme3
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Amazon/AFH_params.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $perp
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Amazon/AFH_params.py#1 $
# Level: 1
#---------------------------------------------------------------------------------------------------------#

from Constants import *
from AFH_constants import angstromsScaler
from Utility import CUtility
Utl = CUtility()
from Test_Switches import testSwitch
from TestParameters import numHeads
from TestParameters import program
from base_TestParameters import prm_191_0002

##################### AFH #####################################
# still need these for V3BAR
optimized_dPES_maskParams_version_2_0 = {
   'tracks'                   : [67, 50521, 188524, 202018],
   AFH_Uniform_Track_Lbl      : [67, 50521, 188524, 202018],            # Nominal logical tracks specified here
   'scaling'                  : [0.000431, 0.25, 0.765611, 0.99999],    # When AFH_V3BAR_phase5 switch is enabled the hard coded track locations below are ignored
   }

baseDpesPrm_35 = {}
maskParams = optimized_dPES_maskParams_version_2_0
heatSearchParams = {}
T35_Retry_Loop_Params = {}


# legacy/base V3BAR parameters for Luxor.  I believe these are un-used.  Clean these up after Carib moves to AFH 35.X
V3BAR_phase5_params = {
   'amount_of_stroke_to_skip' : 0.005,          # This previously was num of tracks to skip between looking for a valid ID cylinder  (historical values 0.05% of stroke or 500 cyls on 100kTP technology)
   'num_skips'                : 8,
   'min_clr'                  : 0.05,
   'primary_delta_Z'          : 0.15,
   'delta_Z'                  : 0.30,
   'ID_search_coarse_retry_limit': 10,
   'UnitTest_clrList'         : [],
   'actuation_mode'           : 'Write+Heat',
   'num_invalid_DAC_retries'  : 5,
   'path2_scaler1'            : 0.333,
   'path2_scaler2'            : 2,
   'path2_scaler3'            : 0.667,
   'path2_scaler4'            : 0.333,
   'path3_num_iterations'     : 8,
   'path3_scaler1'            : 0.229659,
   'path3_scaler2'            : 0.114829,
   'pos3_minus_pos2_clr_limit': 0.25,
}


deStroke_drive_185_params = {
   'test_num'                 : 185,
   'prm_name'                 : "deStroke_drive_178_params",
   'spc_id'                   : 1,
   'CWORD1'                   : 0x0800,         # Set Stroke - Recalculate the TPI Warp and Logical to Physical Track polynomials
   }


#
# #
#          from ProgramName import getProgramNameGivenTestSwitch
#          programName = getProgramNameGivenTestSwitch( testSwitch )

#

#  afhZoneTargets = defaultProfile

#Firmware equation governing TCS1 and TCS2
#TCS1 * Delta temp + TCS2 * Delta temp^2
tccDict_178 = {
   'default'                  : 0,
   'TCS1'                     : 0,
   'TCS2'                     : 0,
   'TCS1_USL'                 : 0.0025,         # 2.5 n"/C
   'TCS1_LSL'                 : -0.0025,        # 2.5 n"/C
   'TCS2_USL'                 : 1.0,            # 1 u"/C (essentially disable)
   'TCS2_LSL'                 : -1.0,           # -1 u"/C (essentially disable)
   }

tempSpecDict_178 = {
   #Temp cap is of form (temperature, min/maxClearance)
   'loTemp'                : (0, 127),
   'hiTemp'                : (85, 0),
   }


settling_correction_values = {

         'Min_Settling_Assumption'  :  7.0,                # if measured settling is less than this, assume it will get this bad eventually.
         'Min_Settling_Margin'      :  5.0,                # target for Min HMSCap margin after Min_Settling_Assumption subtracted
         'Max_Settling_Correction'  :  10.0,               # maximum settling correction allowed (at time zero)
         'Min_Settling_Correction'  :  2.0,                # minimum settling correction allowed (at time zero)
         }
#######################################################################################################################
#
# AFH V35 burnish check params
#
# The V35 burnish params are by heater element type (READER_HEATER or WRITER_HEATER) where as V34 burnish params
# are implicitly for WRITER_HEATER only as has historically been done.
#
#######################################################################################################################

# old ST-10 T02 to T09 delta
burnish_params_1 = {
      "WRITER_HEATER" : {
         'mode'                     : 'burnish',
         'twoSidedLimit_USL'        :  15/angstromsScaler,
         'twoSidedLimit_LSL'        : -15/angstromsScaler,
         'twoSidedHardLimit_USL'    :  24/angstromsScaler,
         'twoSidedHardLimit_LSL'    : -24/angstromsScaler,
         'groupA_nth_AFH_state'     : 1,              # Not an AFH state index, rather the nth AFH. 1 for AFH1(INIT_AFH), 2 for AFH2(AFH_VER).  Does NOT depend on StateTable.py
         'groupB_nth_AFH_state'     : 2,              # Not an AFH state index, rather the nth AFH. 1 for AFH1(INIT_AFH), 2 for AFH2(AFH_VER).  Does NOT depend on StateTable.py
         },

      "READER_HEATER" : {
         'mode'                     : 'burnish',
         'twoSidedLimit_USL'        :  15/angstromsScaler,
         'twoSidedLimit_LSL'        : -15/angstromsScaler,
         'twoSidedHardLimit_USL'    :  24/angstromsScaler,
         'twoSidedHardLimit_LSL'    : -24/angstromsScaler,
         'groupA_nth_AFH_state'     : 1,              # Not an AFH state index, rather the nth AFH. 1 for AFH1(INIT_AFH), 2 for AFH2(AFH_VER).  Does NOT depend on StateTable.py
         'groupB_nth_AFH_state'     : 2,              # Not an AFH state index, rather the nth AFH. 1 for AFH1(INIT_AFH), 2 for AFH2(AFH_VER).  Does NOT depend on StateTable.py
         },

   }
if testSwitch.AFH2_FAIL_BURNISH_RERUN_AFH1 ==1:
   burnish_params_1.update({
      "WRITER_HEATER" : {
         'mode'                     : 'burnish',
         'twoSidedLimit_USL'        :  6/angstromsScaler,
         'twoSidedLimit_LSL'        : -6/angstromsScaler,
         'twoSidedHardLimit_USL'    :  24/angstromsScaler,
         'twoSidedHardLimit_LSL'    : -24/angstromsScaler,
         'groupA_nth_AFH_state'     : 1,              # Not an AFH state index, rather the nth AFH. 1 for AFH1(INIT_AFH), 2 for AFH2(AFH_VER).  Does NOT depend on StateTable.py
         'groupB_nth_AFH_state'     : 2,              # Not an AFH state index, rather the nth AFH. 1 for AFH1(INIT_AFH), 2 for AFH2(AFH_VER).  Does NOT depend on StateTable.py
         },
      "READER_HEATER" : {
         'mode'                     : 'burnish',
         'twoSidedLimit_USL'        :  6/angstromsScaler,
         'twoSidedLimit_LSL'        : -6/angstromsScaler,
         'twoSidedHardLimit_USL'    :  24/angstromsScaler,
         'twoSidedHardLimit_LSL'    : -24/angstromsScaler,
         'groupA_nth_AFH_state'     : 1,              # Not an AFH state index, rather the nth AFH. 1 for AFH1(INIT_AFH), 2 for AFH2(AFH_VER).  Does NOT depend on StateTable.py
         'groupB_nth_AFH_state'     : 2,              # Not an AFH state index, rather the nth AFH. 1 for AFH1(INIT_AFH), 2 for AFH2(AFH_VER).  Does NOT depend on StateTable.py
         },
   })
burnish_params_1R = {
      "WRITER_HEATER" : {
         'mode'                     : 'burnish',
         'twoSidedLimit_USL'        :  15/angstromsScaler,
         'twoSidedLimit_LSL'        : -15/angstromsScaler,
         'twoSidedHardLimit_USL'    :  24/angstromsScaler,
         'twoSidedHardLimit_LSL'    : -24/angstromsScaler,
         'groupA_nth_AFH_state'     : 1,              # Not an AFH state index, rather the nth AFH. 1 for AFH1(INIT_AFH), 2 for AFH2(AFH_VER).  Does NOT depend on StateTable.py
         'groupB_nth_AFH_state'     : 2,              # Not an AFH state index, rather the nth AFH. 1 for AFH1(INIT_AFH), 2 for AFH2(AFH_VER).  Does NOT depend on StateTable.py
         },

      "READER_HEATER" : {
         'mode'                     : 'burnish',
         'twoSidedLimit_USL'        :  15/angstromsScaler,
         'twoSidedLimit_LSL'        : -15/angstromsScaler,
         'twoSidedHardLimit_USL'    :  24/angstromsScaler,
         'twoSidedHardLimit_LSL'    : -24/angstromsScaler,
         'groupA_nth_AFH_state'     : 1,              # Not an AFH state index, rather the nth AFH. 1 for AFH1(INIT_AFH), 2 for AFH2(AFH_VER).  Does NOT depend on StateTable.py
         'groupB_nth_AFH_state'     : 2,              # Not an AFH state index, rather the nth AFH. 1 for AFH1(INIT_AFH), 2 for AFH2(AFH_VER).  Does NOT depend on StateTable.py
         },

   }

burnish_params_RDDAC1 = {
      "WRITER_HEATER" : {
         'mode'                     : 'burnish',
         'twoSidedLimit_USL'        :  10,
         'twoSidedLimit_LSL'        : -10,
         'groupA_nth_AFH_state'     : 1,              # Not an AFH state index, rather the nth AFH. 1 for AFH1(INIT_AFH), 2 for AFH2(AFH_VER).  Does NOT depend on StateTable.py
         'groupB_nth_AFH_state'     : 2,              # Not an AFH state index, rather the nth AFH. 1 for AFH1(INIT_AFH), 2 for AFH2(AFH_VER).  Does NOT depend on StateTable.py
         'comparison_type'          : 'abs_rddac',
         },

      "READER_HEATER" : {
         'mode'                     : 'burnish',
         'twoSidedLimit_USL'        :  10,
         'twoSidedLimit_LSL'        : -10,
         'groupA_nth_AFH_state'     : 1,              # Not an AFH state index, rather the nth AFH. 1 for AFH1(INIT_AFH), 2 for AFH2(AFH_VER).  Does NOT depend on StateTable.py
         'groupB_nth_AFH_state'     : 2,              # Not an AFH state index, rather the nth AFH. 1 for AFH1(INIT_AFH), 2 for AFH2(AFH_VER).  Does NOT depend on StateTable.py
         'comparison_type'          : 'abs_rddac',
         },

   }
burnish_params_RDDAC1R = {
      "WRITER_HEATER" : {
         'mode'                     : 'burnish',
         'twoSidedLimit_USL'        :  10,
         'twoSidedLimit_LSL'        : -10,
         'groupA_nth_AFH_state'     : 1,              # Not an AFH state index, rather the nth AFH. 1 for AFH1(INIT_AFH), 2 for AFH2(AFH_VER).  Does NOT depend on StateTable.py
         'groupB_nth_AFH_state'     : 2,              # Not an AFH state index, rather the nth AFH. 1 for AFH1(INIT_AFH), 2 for AFH2(AFH_VER).  Does NOT depend on StateTable.py
         'comparison_type'          : 'abs_rddac',
         },

      "READER_HEATER" : {
         'mode'                     : 'burnish',
         'twoSidedLimit_USL'        :  10,
         'twoSidedLimit_LSL'        : -10,
         'groupA_nth_AFH_state'     : 1,              # Not an AFH state index, rather the nth AFH. 1 for AFH1(INIT_AFH), 2 for AFH2(AFH_VER).  Does NOT depend on StateTable.py
         'groupB_nth_AFH_state'     : 2,              # Not an AFH state index, rather the nth AFH. 1 for AFH1(INIT_AFH), 2 for AFH2(AFH_VER).  Does NOT depend on StateTable.py
         'comparison_type'          : 'abs_rddac',
         },

   }

burnish_params_MaxWt_Clr = {
      'ATTRIBUTE'  : 'HGA_SUPPLIER',
      'DEFAULT'    : 'RHO',
      'RHO'        : 0xFFFF,
      'HWY'        : 80.0, # 80
      'TDK'        : 80.0  # 80 
   }

burnish_params_delta_ODID = {
      'ATTRIBUTE'  : 'HGA_SUPPLIER',
      'DEFAULT'    : 'RHO',
      'RHO'        : 30.0,
      'HWY'        : 25.0, # 80
      'TDK'        : 25.0  # 80 
   }

burnish_params_ID = 7.0 #{
   #   'ATTRIBUTE'  : 'HGA_SUPPLIER',
   #   'DEFAULT'    : 'RHO',
   #   'RHO'        : {
   #           'ATTRIBUTE' : 'MediaType',
   #           'RMO-L9.0'  : 1000.0,
   #           'RMO-L8.0'  : 1000.0,
   #           'RMO-L8.5'  : 1000.0,
   #           'SDK-C224'  : 7.0,
   #           'NONE'      : 1000.0,
   #         },
   #   'HWY'        : {
   #           'ATTRIBUTE' : 'MediaType',
   #           'RMO-L9.0'  : 1000.0,
   #           'RMO-L8.0'  : 1000.0,
   #           'RMO-L8.5'  : 1000.0,
   #           'SDK-C224'  : 7.0,
   #           'NONE'      : 1000.0,
   #         },
   #   'TDK'        : {
   #           'ATTRIBUTE' : 'MediaType',
   #           'RMO-L9.0'  : 1000.0,
   #           'RMO-L8.0'  : 1000.0,
   #           'RMO-L8.5'  : 1000.0,
   #           'SDK-C224'  : 7.0,
   #           'NONE'      : 1000.0,
   #         }, 
   #}


# old ST-10 T09 to T87 delta
burnish_params_2 = {
      "WRITER_HEATER" : {
         'mode'                     : 'burnish',
         'twoSidedLimit_USL'        :  15/angstromsScaler,
         'twoSidedLimit_LSL'        : -15/angstromsScaler,
         'twoSidedHardLimit_USL'    :  24/angstromsScaler,
         'twoSidedHardLimit_LSL'    : -24/angstromsScaler,
         'groupA_nth_AFH_state'     : 2,              # Not an AFH state index, rather the nth AFH. 1 for AFH1(INIT_AFH), 2 for AFH2(AFH_VER).  Does NOT depend on StateTable.py
         'groupB_nth_AFH_state'     : 3,              # Not an AFH state index, rather the nth AFH. 1 for AFH1(INIT_AFH), 2 for AFH2(AFH_VER).  Does NOT depend on StateTable.py
         },
      "READER_HEATER" : {
         'mode'                     : 'burnish',
         'twoSidedLimit_USL'        :  15/angstromsScaler,
         'twoSidedLimit_LSL'        : -15/angstromsScaler,
         'twoSidedHardLimit_USL'    :  24/angstromsScaler,
         'twoSidedHardLimit_LSL'    : -24/angstromsScaler,
         'groupA_nth_AFH_state'     : 2,              # Not an AFH state index, rather the nth AFH. 1 for AFH1(INIT_AFH), 2 for AFH2(AFH_VER).  Does NOT depend on StateTable.py
         'groupB_nth_AFH_state'     : 3,              # Not an AFH state index, rather the nth AFH. 1 for AFH1(INIT_AFH), 2 for AFH2(AFH_VER).  Does NOT depend on StateTable.py
         },

   }

burnish_params_2R = {
      "WRITER_HEATER" : {
         'mode'                     : 'burnish',
         'twoSidedLimit_USL'        :  15/angstromsScaler,
         'twoSidedLimit_LSL'        : -15/angstromsScaler,
         'twoSidedHardLimit_USL'    :  24/angstromsScaler,
         'twoSidedHardLimit_LSL'    : -24/angstromsScaler,
         'groupA_nth_AFH_state'     : 2,              # Not an AFH state index, rather the nth AFH. 1 for AFH1(INIT_AFH), 2 for AFH2(AFH_VER).  Does NOT depend on StateTable.py
         'groupB_nth_AFH_state'     : 3,              # Not an AFH state index, rather the nth AFH. 1 for AFH1(INIT_AFH), 2 for AFH2(AFH_VER).  Does NOT depend on StateTable.py
         },
      "READER_HEATER" : {
         'mode'                     : 'burnish',
         'twoSidedLimit_USL'        :  15/angstromsScaler,
         'twoSidedLimit_LSL'        : -15/angstromsScaler,
         'twoSidedHardLimit_USL'    :  24/angstromsScaler,
         'twoSidedHardLimit_LSL'    : -24/angstromsScaler,
         'groupA_nth_AFH_state'     : 2,              # Not an AFH state index, rather the nth AFH. 1 for AFH1(INIT_AFH), 2 for AFH2(AFH_VER).  Does NOT depend on StateTable.py
         'groupB_nth_AFH_state'     : 3,              # Not an AFH state index, rather the nth AFH. 1 for AFH1(INIT_AFH), 2 for AFH2(AFH_VER).  Does NOT depend on StateTable.py
         },

   }

burnish_params_3 = {
      "WRITER_HEATER" : {
         'mode'                     : 'burnish',
         'twoSidedLimit_USL'        :  10/angstromsScaler,
         'twoSidedLimit_LSL'        : -8/angstromsScaler,
         'twoSidedHardLimit_USL'    :  24/angstromsScaler,
         'twoSidedHardLimit_LSL'    : -24/angstromsScaler,
         'groupA_nth_AFH_state'     : 2,              # Not an AFH state index, rather the nth AFH. 1 for AFH1(INIT_AFH), 2 for AFH2(AFH_VER).  Does NOT depend on StateTable.py
         'groupB_nth_AFH_state'     : 3,              # Not an AFH state index, rather the nth AFH. 1 for AFH1(INIT_AFH), 2 for AFH2(AFH_VER).  Does NOT depend on StateTable.py
         },
      "READER_HEATER" : {
         'mode'                     : 'burnish',
         'twoSidedLimit_USL'        :  10/angstromsScaler,
         'twoSidedLimit_LSL'        : -10/angstromsScaler,
         'twoSidedHardLimit_USL'    :  24/angstromsScaler,
         'twoSidedHardLimit_LSL'    : -24/angstromsScaler,
         'groupA_nth_AFH_state'     : 2,              # Not an AFH state index, rather the nth AFH. 1 for AFH1(INIT_AFH), 2 for AFH2(AFH_VER).  Does NOT depend on StateTable.py
         'groupB_nth_AFH_state'     : 3,              # Not an AFH state index, rather the nth AFH. 1 for AFH1(INIT_AFH), 2 for AFH2(AFH_VER).  Does NOT depend on StateTable.py
         },

   }

# pre/post VBAR clr check if fail then rerun VBAR
deltaClrVBAR_burnish_params = {
      "WRITER_HEATER" : {
         'mode'                     : 'delta_VBAR',
         'twoSidedLimit_USL'        :  12.7 / angstromsScaler,
         'twoSidedLimit_LSL'        : -12.7  / angstromsScaler,
         'groupA_nth_AFH_state'     : 1,              # Not an AFH state index, rather the nth AFH. 1 for AFH1(INIT_AFH), 2 for AFH2(AFH_VER).  Does NOT depend on StateTable.py
         'groupB_nth_AFH_state'     : 2,              # Not an AFH state index, rather the nth AFH. 1 for AFH1(INIT_AFH), 2 for AFH2(AFH_VER).  Does NOT depend on StateTable.py
         },
      "READER_HEATER" : {
         'mode'                     : 'delta_VBAR',
         'twoSidedLimit_USL'        :  12.7 / angstromsScaler,
         'twoSidedLimit_LSL'        : -12.7  / angstromsScaler,
         'groupA_nth_AFH_state'     : 1,              # Not an AFH state index, rather the nth AFH. 1 for AFH1(INIT_AFH), 2 for AFH2(AFH_VER).  Does NOT depend on StateTable.py
         'groupB_nth_AFH_state'     : 2,              # Not an AFH state index, rather the nth AFH. 1 for AFH1(INIT_AFH), 2 for AFH2(AFH_VER).  Does NOT depend on StateTable.py
         },

      }

deltaClrVBAR_burnish_paramsR = {
      "WRITER_HEATER" : {
         'mode'                     : 'delta_VBAR',
         'twoSidedLimit_USL'        :  12.7 / angstromsScaler,
         'twoSidedLimit_LSL'        : -12.7  / angstromsScaler,
         'groupA_nth_AFH_state'     : 1,              # Not an AFH state index, rather the nth AFH. 1 for AFH1(INIT_AFH), 2 for AFH2(AFH_VER).  Does NOT depend on StateTable.py
         'groupB_nth_AFH_state'     : 2,              # Not an AFH state index, rather the nth AFH. 1 for AFH1(INIT_AFH), 2 for AFH2(AFH_VER).  Does NOT depend on StateTable.py
         },
      "READER_HEATER" : {
         'mode'                     : 'delta_VBAR',
         'twoSidedLimit_USL'        :  12.7 / angstromsScaler,
         'twoSidedLimit_LSL'        : -12.7  / angstromsScaler,
         'groupA_nth_AFH_state'     : 1,              # Not an AFH state index, rather the nth AFH. 1 for AFH1(INIT_AFH), 2 for AFH2(AFH_VER).  Does NOT depend on StateTable.py
         'groupB_nth_AFH_state'     : 2,              # Not an AFH state index, rather the nth AFH. 1 for AFH1(INIT_AFH), 2 for AFH2(AFH_VER).  Does NOT depend on StateTable.py
         },

      }

#######################################################################################################################
#
# END of AFH burnish check params
#
#######################################################################################################################

minClr_params_1 = {}                   ## NOT USED ANYMORE IN DH CODE.
minClr_params_2 = {}                   ## NOT USED ANYMORE IN DH CODE.
minClr_params_3 = {}                   ## NOT USED ANYMORE IN DH CODE.
minClr_params_1R = {}                   ## NOT USED ANYMORE IN DH CODE.
minClr_params_2R = {}                   ## NOT USED ANYMORE IN DH CODE.
minClr_params_3R = {}                   ## NOT USED ANYMORE IN DH CODE.
crossStrokeClrLimit = {}               ## NOT USED ANYMORE IN DH CODE.
clrRangeChkLimit = {}                  ## NOT USED ANYMORE IN DH CODE.
extreme_OD_ID_clearanceRangeCheck = {} ## NOT USED ANYMORE IN DH CODE.

if  testSwitch.AFH2_FAIL_BURNISH_RERUN_AFH1 or testSwitch.FE_AFH3_TO_DO_BURNISH_CHECK:
  AFH2_RETRYFROM_AFH1_ERROR_CODE = [48394, 11186, 14559]  

# The number of bits of DAC resolution in the preamp used to calculate the maximum possible preamp DAC value
dpreamp_number_bits_DAC = {
   'TI3945'       : 8,
   'TI3946'       : 8,
   'TI3948'       : 8,
   'TI5551'       : 8,
   'TI5552'       : 8,
   'TI7550'       : 8,
   'TI7551'       : 8,
   'LSI8831'      : 8,
   'LSI8832'      : 8,
   'LSI2731'      : 8,
   'LSI2935'      : 8,
   'LSI2958'      : 8,
   'LSI5230'      : 8,
   'LSI5231'      : 8,
   'LSI5830'      : 8,
   'TI3448'       : 8,
   'TI3453'       : 8,
   }

dpreamp_DACs_backoff_from_Max_DAC_T35 = {
   'TI3945'       : 0,
   'TI3946'       : 0,
   'TI3948'       : 0,
   'TI5551'       : 0,
   'TI5552'       : 0,
   'TI7550'       : 0,
   'TI7551'       : 0,
   'LSI8831'      : 0,
   'LSI8832'      : 0,
   'LSI2731'      : 0,
   'LSI2935'      : 0,
   'LSI2958'      : 0,
   'LSI5230'      : 0,
   'LSI5231'      : 0,   
   'LSI5830'      : 0,   
   'TI3448'       : 0,
   'TI3453'       : 0,
   }

# Please read the following before changing the clr_USL_Hard.
# Upper Spec Limit (USL) hard for calculated clearance values.  Values above this limit do not make sense and will be fail the drive for calculating
# a FH number that is too high.  This is most likely indicative of bad coefficients.
# This parameter should be changed very rarely.  It is NOT an upper spec limit for clearance to fail the drive on.  Rather this limit is an
# internal calculation limit that says "if any value was calculted to be this large then something has to be wrong with the coefficients."
clr_USL_Hard = 5.0
test135UseMeasuredData = "I"     # "I" for interpolated data, "M" for measured data

AFH_consChk_numRetries = 3

#trackCleanupAFHPad = 800



##################### AFH AR settings ##########################
# currently only measuring user data zones and NOT system zones
AR_params = {
   'HEAD_RETEST_LIMIT'        : 1,
}

prm_191_0001 = {
   'test_num'                 : 191,
   'prm_name'                 : 'AR T191 parameter list',
   'spc_id'                   : 8,
   'timeout'                  : 20000,
   "HEAD_RANGE"               : (0,),           # Not really a range.  Specify just one head.
   "MAX_ITERATION"            : 20,             # Number of revs to avg
   "CWORD1"                   : 0x1251,      # Bit defs are in T191_prv.h, but 0x1191 is good for Heater Only and 0x1111 for Write + Heat
#                      0x2000             # Bit 13 - turn on very low level debug to see the HSC channel register values
#                      0x1000             # Bit 12 - Processed Debug Data.   Causes the table of Actuation and raw HSC resister readings,
                                          # as a function of Heater DAC value, (P191_HSC_DATA) to be printed to the ascii log.
                                          # Only the adjustment values (P191_CLR_COEF_CAL) are printed normally.
                                          # P191_HSC_DATA is considered debug data.
#                      0x0100             # Bit 8 - set says use this heater range, otherwise compute from drive's clearance data
#                      0x0080             # Bit 7 - HEATER ONLY, If this bit is set HIRP is measured.
                                          # If reset, HIWP (the equivalent of Write+Heat) is measured.
#                      0x0010             # Bit 4 - display debug data
#                      0x0001             # Bit 0 - display AGC data
   "CWORD2"                   : 0x0003,
   "LENGTH_LIMIT"             : 128,
   "ZONE"                     : 0x0101,
   "DISCARD_LIMITS"           : (10,12,),
   "WIRP_POINT_COUNT"         : 2,
   "SET_OCLIM"                : 200,
   "THRESHOLD  "              : 970,
   "HEATER"                   : (60, -12),      # Bit 8 of CWORD1 set says use this heater range, otherwise compute from drive's clearance data
   'RETRY_LIMIT'              : 3,              # limit internal st(191) retries
}


AR_params = {
   'STDEV_LIMIT'              : 0.10,    # 100 is disabled essentially
   'TRACK_RETEST_LIMIT'       : 1,
   'HEAD_RETEST_LIMIT'        : 1,
   'stateList'                : [1],      # Note, these are not the AFH state Indexes in StateTable.py, rather the nth HIRP state to be tested
                                          # This should not be changed, unless you'd like to run this in a different HIRP state
                                          # 1 in 1st HIRP state, 2 is 2nd HIRP state, etc.
   'numTrksToSeekAwayOnRetry' : 100,
   'scale_USL'                : 1.4,
   'scale_LSL'                : 0.6,
   'offset_USL'               : 35,
   'offset_LSL'               : -20,
   'additionalRevsForSt191DuringHeadRetest': 10,
   'MAX_NUM_FAILED_ADJACENT_ZONES' : 2,
}


baseT191_WRITER_HEATER = {
   'test_num'          : 191,
   'prm_name'          : 'baseT191_WRITER_HEATER',
   'timeout'           : 6000,
#  'spc_id'            : (spcidnum),
   'HEATER'            : (0x003C, -15),
   'ZONE'              : {
      'ATTRIBUTE'    : 'numZones',
      'DEFAULT'      : 31,
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
   'THRESHOLD'         : (980,),
   'MAX_ITERATION'     : (20,),
   'RETRY_LIMIT'       : (4,),
   'CWORD1'            : (0x12D1,),
   'DISCARD_LIMITS'    : (20,20),
   'FREQUENCY'         : (100,),
   'DUAL_HEATER_CONTROL' : (0,-1,),
   "SET_OCLIM"         : (200,),
   'LENGTH_LIMIT'      : 901,
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

baseT191_READER_HEATER = {
   'test_num'          : 191,
   'prm_name'          : 'baseT191_READER_HEATER',
   'timeout'               : 6000,
#  'spc_id'                : (spcidnum),
   'HEATER'                : (0xFF3C, -15),
   'ZONE'              : {
      'ATTRIBUTE'    : 'numZones',
      'DEFAULT'      : 31,
      24             : (0x0302),  
      31             : (0x0302),  
      60             : (0x0304),
      120            : (0x0308), 
      150            : (0x030A),  
      180            : (0x030C), 
      },
   #'ZONE'                  : (0x0302),
   'WIRP_POINT_COUNT'      : (2,),
   'CWORD2'                : (0x0003),
   'HEAD_RANGE'            : (0),
   'MAX_ITERATION'         : (20,),
   'THRESHOLD'             : (980,),
   'RETRY_LIMIT'           : (4,),
   'CWORD1'                : (0x12D1,),
   'DISCARD_LIMITS'        : (10,12),
   'FREQUENCY'             : (100,),
   'DUAL_HEATER_CONTROL'   : (1,-1,),
   "SET_OCLIM"             : (200,),
   'LENGTH_LIMIT'          : 901,
   'HIRP_CURVE_FIT'        : {
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

if testSwitch.M10P:
   baseT191_WRITER_HEATER['HEATER'] = (0xFF28, -20)
   baseT191_WRITER_HEATER['CWORD1'] = (0x1051,)
   baseT191_WRITER_HEATER['THRESHOLD'] = (940,)
   baseT191_READER_HEATER['CWORD1'] = (0x92D1,)
   baseT191_READER_HEATER['THRESHOLD'] = (940,)

if testSwitch.FE_0148582_341036_AFH_WHIRP_V35_CHANGE_VALUES == 1:
   baseT191_WRITER_HEATER['HEATER'] = (0xFF3C, -15)
   baseT191_WRITER_HEATER['CWORD1'] = (0x9241,)
   baseT191_READER_HEATER['CWORD1'] = (0x92D1,)

if testSwitch.FE_0149438_395340_P_LUL_BEFORE_RUN_AFH:
   AFH_LUL = {
      'AFH_State'                : (1,2),
      'loop'                     : 10,
   }
   if testSwitch.FE_0162917_407749_P_AFH_LUL_FOR_RETRY_BY_ERROR_CODE:
      AFH_LUL['AFH_EC_LIST']     = [14841, 14703]

#######################################################################################################################
#
# START of AFH Clearance Settling parameters
#
#######################################################################################################################


AFH_clearanceSettling_ParametersDict = {
   'CLR_SETTLING_CORRECTION_IN_ANGSTROMS': 0,  # in angstroms
   'MIN_CLR_SETTLING_CORRECTION': 2,
   'CLR_SETTLING_DECAY': 40,
   }
   
#######################################################################################################################
#
# END of AFH Clearance Settling parameters
#
#######################################################################################################################
if testSwitch.M10P:
   from AFH_params_M10P import *
elif testSwitch.CHENGAI:
   from AFH_params_Chengai import *
else:
   from AFH_params_Rosewood import *

