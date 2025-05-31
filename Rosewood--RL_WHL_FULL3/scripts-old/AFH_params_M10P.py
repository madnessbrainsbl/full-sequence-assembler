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
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Amazon/AFH_params_M10P.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $perp
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Amazon/AFH_params_M10P.py#1 $
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

DefaultPreampVendor = 'LSI5231'

AAB_TYPE = { # Defaul AAB TYPE to override Config VAR
   'ATTRIBUTE': 'HGA_SUPPLIER',
   'DEFAULT'  : 'TDK',
   'RHO'      : '501.11' ,
   'TDK'      : '26YR42' ,
   'HWY'      : 'H_25AS2B',
}
#Each Prea-amp + AAB + Power Mode combination will have 2 sets of coefficients.
#   1. WP + Heater
#   2. Heater only
#Coefficient abstraction..
#
AAB_RHO = ['501.02','501.11']
AAB_TDK = ['26YR4','26YR42']
AAB_HWY = ['H_25AS2B']

DefaultRHOAABType = '501.11'
DefaultTDKAABType = '26YR42'
DefaultHWYAABType = 'H_25AS2B'
DefaultAABType = DefaultTDKAABType
#DefaultAABType = DefaultHWYAABType
#DefaultAABType = DefaultRHOAABType

#Attributes used to detect the head manufacturer.
HGA_SUPPLIER_LOOKUP = {
    'RHO'  : { 'HGA_SUPPLIER' : ['RHO',] },
    'URHO' : { 'HGA_SUPPLIER' : ['URHO',] },
    'USAE' : { 'HGA_SUPPLIER' : ['USAE',] },
    'URHOA': { 'HGA_SUPPLIER' : ['URHOA',] },
    'TDK'  : { 'HGA_SUPPLIER' : ['TDK',] },
    'HWY'  : { 'HGA_SUPPLIER' : ['HWY',] },
      }
#Attributes used to detect the wafer code.
WAFER_CODE_MATRIX = {}

ATTR_AAB_MATRIX = {}


#if testSwitch.FE_0150604_208705_P_VBAR_HMS_PHASE_2_INCREASE_TGT_CLR:
#      writeClearance = 18.0
#      readClearance = 18.0
#else:
#      writeClearance = 15.0
#      readClearance = 15.0

writeClearance = 12.0
readClearance = 12.0

defaultProfile = {
      'ATTRIBUTE':'numZones',
      'DEFAULT': 60,
      31 : {
         'TGT_WRT_CLR' : {
            'ATTRIBUTE' : 'HGA_SUPPLIER',
            'DEFAULT' : 'RHO',
            'RHO'                : [round(writeClearance/angstromsScaler,8) for i in xrange(32)],
            'TDK'                : [round(writeClearance/angstromsScaler,8) for i in xrange(32)],
            },
         'TGT_MAINTENANCE_CLR' : {
            'ATTRIBUTE' : 'HGA_SUPPLIER',
            'DEFAULT' : 'RHO',
            'RHO'                : [round(writeClearance/angstromsScaler,8) for i in xrange(32)],
            'TDK'                : [round(writeClearance/angstromsScaler,8) for i in xrange(32)],
            },

         'TGT_PREWRT_CLR' : {
            'ATTRIBUTE' : 'HGA_SUPPLIER',
            'DEFAULT' : 'RHO',
            'RHO'                : [round(writeClearance/angstromsScaler,8) for i in xrange(32)],
            'TDK'                : [round(writeClearance/angstromsScaler,8) for i in xrange(32)],
            },
         'TGT_RD_CLR' : {
            'ATTRIBUTE' : 'HGA_SUPPLIER',
            'DEFAULT' : 'RHO',
            'RHO'                : [round(readClearance/angstromsScaler,8) for i in xrange(32)],
            'TDK'                : [round(readClearance/angstromsScaler,8) for i in xrange(32)],
            },

         }, # end of 31 : {
      60 : {
         'TGT_WRT_CLR' : {
            'ATTRIBUTE' : 'HGA_SUPPLIER',
            'DEFAULT' : 'RHO',
            'RHO'                : [round(writeClearance/angstromsScaler,8) for i in xrange(61)],
            'TDK'                : [round(writeClearance/angstromsScaler,8) for i in xrange(61)],
            },
         'TGT_MAINTENANCE_CLR' : {
            'ATTRIBUTE' : 'HGA_SUPPLIER',
            'DEFAULT' : 'RHO',
            'RHO'                : [round(writeClearance/angstromsScaler,8) for i in xrange(61)],
            'TDK'                : [round(writeClearance/angstromsScaler,8) for i in xrange(61)],
            },

         'TGT_PREWRT_CLR' : {
            'ATTRIBUTE' : 'HGA_SUPPLIER',
            'DEFAULT' : 'RHO',
            'RHO'                : [round(writeClearance/angstromsScaler,8) for i in xrange(61)],
            'TDK'                : [round(writeClearance/angstromsScaler,8) for i in xrange(61)],
            },
         'TGT_RD_CLR' : {
            'ATTRIBUTE' : 'HGA_SUPPLIER',
            'DEFAULT' : 'RHO',
            'RHO'                : [round(readClearance/angstromsScaler,8) for i in xrange(61)],
            'TDK'                : [round(readClearance/angstromsScaler,8) for i in xrange(61)],
            },
         }, # end of 60 : {
      } # end of defaultProfile = {
####### Tgt Clr related params START here ##########

afhZoneTargets = {
   'ATTRIBUTE':'numZones',
   'DEFAULT': 31,
   31:{
      'ATTRIBUTE':'AABType',
      '26YR4':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(28)] + [16, 17, 18, 15] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(28)] + [16, 17, 18, 15] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(28)] + [16, 17, 18, 15] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(28)] + [16, 17, 18, 15] ),
         },
      '26YR42':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(32)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(32)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(32)] ),
            "TGT_RD_CLR"          : tuple( [12 for i in range(32)] ),
#            "TGT_RD_CLR"          : tuple( [15 for i in range(29)] + [16, 17, 15] ),
         },
      'H_25AS2B':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(32)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(32)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(32)] ),
            "TGT_RD_CLR"          : tuple( [12 for i in range(32)] ),
         },
      '501.02':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(32)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(32)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(32)] ),
            "TGT_RD_CLR"          : tuple( [12 for i in range(32)] ),
         },
      '501.11':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(32)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(32)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(32)] ),
            "TGT_RD_CLR"          : tuple( [12 for i in range(32)] ),
         },
      },
   60:{
      'ATTRIBUTE':'AABType',
      'DEFAULT'  : '26YR42',
      '26YR4':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(61)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(61)] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(61)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(61)] ),
         },
      '26YR42':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(61)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(61)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(61)] ),
            "TGT_RD_CLR"          : tuple( [12 for i in range(61)] ),
         },
      'H_25AS2B':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(61)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(61)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(61)] ),
            "TGT_RD_CLR"          : tuple( [12 for i in range(61)] ),
         },
      '501.02':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(61)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(61)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(61)] ),
            "TGT_RD_CLR"          : tuple( [12 for i in range(61)] ),
         },
      '501.11':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(61)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(61)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(61)] ),
            "TGT_RD_CLR"          : tuple( [12 for i in range(61)] ),
         },
      },
}

####### Tgt Clr related params END here ##########





prm_191_0002["CWORD1"] = (0x02D1,)
Test135_numHeadRetries = 3  # Retry limit in T135. Set to 5. Default is 3



##################COPY FROM YARRABP START ##############################
#Firmware equation governing TCS1 and TCS2
#TCS1 * Delta temp + TCS2 * Delta temp^2
tccDict_178 = {}
if 0:
   tccDict_178 = {
      'ATTRIBUTE':'HGA_SUPPLIER',
      'DEFAULT': 'TDK',
      'RHO':  {
         #  'default'                  : 0,
         'TCS1'                     : -0.001, #-0.0005, # this seems too high.
         'TCS2'                     : 0,
         # suggested values
         'TCS1_LSL'                 : -0.0040,        # was -0.0020 -> -2.0 n"/C
         'MODIFIED_SLOPE_LSL'       : -0.0040,        # -1.5 n"/C
         'MODIFIED_SLOPE_USL'       : -0.0005,        # -0.5 n"/C
         'TCS1_USL'                 : -0.0005,        # was 0.0005 ->  +0.5 n"/C
         'TCS2_USL'                 : 1.0,            # 1 u"/C (essentially disable)
         'TCS2_LSL'                 : -1.0,           # -1 u"/C (essentially disable)
         'dTc'                      : 0.0005, #Updated on 17 Oct 2011 # very std dTc, dTh settings.  Should be the same as legacy RAP.
         'dTh'                      : -0.002, #updated on 17 Oct 2011.
         'COLD_TEMP_DTC'            : 10, #updated on 17 Oct 2011.
         'HOT_TEMP_DTH'             : 55, #updated on 17 Oct 2011.
         'enableModifyTCS_values'   : 1,
         'dThR'                     : (-0.298103195 / 254.0, -0.404627717 / 254.0, -0.344044506 / 254.0, -0.236665516 / 254.0, -0.185345043 / 254.0,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
         'dTcR'                     : (0.112182395 / 254.0, 0.149864432 / 254.0, 0.1259926 / 254.0, 0.137140324 / 254.0, 0.11726935 / 254.0,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
      }, #end of 'RHO'
      'TDK': {
         'ATTRIBUTE':'AABType',
         'DEFAULT': '26YR42',
         '26YR42': {
            #  'default'                  : 0,
            'TCS1'                     : -0.001, #-0.0005, # this seems too high.
            'TCS2'                     : 0,
            # suggested values
            'TCS1_LSL'                 : -0.0040,        # was -0.0020 -> -2.0 n"/C
            'MODIFIED_SLOPE_LSL'       : -0.0040,        # -1.5 n"/C
            'MODIFIED_SLOPE_USL'       : -0.0005,        # -0.5 n"/C
            'TCS1_USL'                 : -0.0005,        # was 0.0005 ->  +0.5 n"/C
            'TCS2_USL'                 : 1.0,            # 1 u"/C (essentially disable)
            'TCS2_LSL'                 : -1.0,           # -1 u"/C (essentially disable)
            'dTc'                      : 0.0005, #Updated on 17 Oct 2011 # very std dTc, dTh settings.  Should be the same as legacy RAP.
            'dTh'                      : -0.002, #updated on 17 Oct 2011.
            'COLD_TEMP_DTC'            : 10, #updated on 17 Oct 2011.
            'HOT_TEMP_DTH'             : 55, #updated on 17 Oct 2011.
            'enableModifyTCS_values'   : 1,
            'dThR'                     : (-0.298103195 / 254.0, -0.404627717 / 254.0, -0.344044506 / 254.0, -0.236665516 / 254.0, -0.185345043 / 254.0,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
            'dTcR'                     : (0.112182395 / 254.0, 0.149864432 / 254.0, 0.1259926 / 254.0, 0.137140324 / 254.0, 0.11726935 / 254.0,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
         },#end of '26YR42'
      }, #end of 'TDK'
      'HWY': {
         'ATTRIBUTE':'AABType',
         'DEFAULT': 'H_25AS2B',
         'H_25AS2B': {
            #  'default'                  : 0,
            'TCS1'                     : -0.001, #-0.0005, # this seems too high.
            'TCS2'                     : 0,
            # suggested values
            'TCS1_LSL'                 : -0.0040,        # was -0.0020 -> -2.0 n"/C
            'MODIFIED_SLOPE_LSL'       : -0.0040,        # -1.5 n"/C
            'MODIFIED_SLOPE_USL'       : -0.0005,        # -0.5 n"/C
            'TCS1_USL'                 : -0.0005,        # was 0.0005 ->  +0.5 n"/C
            'TCS2_USL'                 : 1.0,            # 1 u"/C (essentially disable)
            'TCS2_LSL'                 : -1.0,           # -1 u"/C (essentially disable)
            'dTc'                      : 0.0005, #Updated on 17 Oct 2011 # very std dTc, dTh settings.  Should be the same as legacy RAP.
            'dTh'                      : -0.002, #updated on 17 Oct 2011.
            'COLD_TEMP_DTC'            : 10, #updated on 17 Oct 2011.
            'HOT_TEMP_DTH'             : 55, #updated on 17 Oct 2011.
            'enableModifyTCS_values'   : 1,
            'dThR'                     : (-0.298103195 / 254.0, -0.404627717 / 254.0, -0.344044506 / 254.0, -0.236665516 / 254.0, -0.185345043 / 254.0,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
            'dTcR'                     : (0.112182395 / 254.0, 0.149864432 / 254.0, 0.1259926 / 254.0, 0.137140324 / 254.0, 0.11726935 / 254.0,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
         },#end of 'H_25AS2B'
      }, #end of 'HWY'
   }


##########
# NOTE:  FOR Dual HEATER(DH) the above limits from single heater don't apply anymore.
##########

#### NOTE:  TCC related params are in Angstroms now

tcc_DH_dict_178 = {
   'ATTRIBUTE': 'HGA_SUPPLIER',
   'DEFAULT'  : 'TDK',
   'TDK'      : {
      'ATTRIBUTE':'AABType',
      'DEFAULT': '26YR42',
      '26YR42': {
         "WRITER_HEATER"   : {
            'TCS1'                     :  -0.254,
            'TCS2'                     :  0.0,
            
            'TCS1_USL'                 : -0.127,              #  Angstroms/C
            'TCS1_LSL'                 : -1.016,              #  Angstroms/C
            
            'MODIFIED_SLOPE_USL'       : -0.127,              # fold limits in Ang/C
            'MODIFIED_SLOPE_LSL'       : -1.016,              # fold limits in Ang/C
            'enableModifyTCS_values'   : 1,
            
            'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
            'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
            
            'dTc'                      :  0.0005*254,            #  Angstroms/C
            'dTh'                      :  -0.002*254,            #  Angstroms/C
            'COLD_TEMP_DTC'            : 10,
            'HOT_TEMP_DTH'             : 55,
            'clearanceDataType'        : 'Write Clearance',
            'dThR'                     : (-0.298103195, -0.404627717, -0.344044506, -0.236665516, -0.185345043,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
            'dTcR'                     : (0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
         },
         "READER_HEATER"   : {          #dummy ONLY, TDK doesn't have READER_HEATER
            'TCS1'                     :  -0.254,
            'TCS2'                     :  0.0,
            
            'TCS1_USL'                 : -0.127,              #  Angstroms/C
            'TCS1_LSL'                 : -1.016,              #  Angstroms/C
            
            'MODIFIED_SLOPE_USL'       : -0.127,              # fold limits in Ang/C
            'MODIFIED_SLOPE_LSL'       : -1.016,              # fold limits in Ang/C
            'enableModifyTCS_values'   : 1,
            
            'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
            'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
            
            'dTc'                      : 0.0005*254,          #  Angstroms/C
            'dTh'                      : -0.002*254,          #  Angstroms/C
            'COLD_TEMP_DTC'            : 10,
            'HOT_TEMP_DTH'             : 55,
            'clearanceDataType'        : 'Read Clearance',
            'dThR'                     : (-0.298103195, -0.404627717, -0.344044506, -0.236665516, -0.185345043,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
            'dTcR'                     : (0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
         },
      },
   },# end of TDK
   'HWY'      : {
      'ATTRIBUTE':'AABType',
      'DEFAULT': 'H_25AS2B',
      'H_25AS2B': {
         "WRITER_HEATER"   : {
            'TCS1'                     :  -0.254,
            'TCS2'                     :  0.0,
            
            'TCS1_USL'                 : -0.127,              #  Angstroms/C
            'TCS1_LSL'                 : -1.016,              #  Angstroms/C
            
            'MODIFIED_SLOPE_USL'       : -0.127,              # fold limits in Ang/C
            'MODIFIED_SLOPE_LSL'       : -1.016,              # fold limits in Ang/C
            'enableModifyTCS_values'   : 1,
            
            'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
            'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
            
            'dTc'                      :  0.0005*254,            #  Angstroms/C
            'dTh'                      :  -0.002*254,            #  Angstroms/C
            'COLD_TEMP_DTC'            : 10,
            'HOT_TEMP_DTH'             : 55,
            'clearanceDataType'        : 'Write Clearance',
            'dThR'                     : (-0.298103195, -0.404627717, -0.344044506, -0.236665516, -0.185345043,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
            'dTcR'                     : (0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
         },
         "READER_HEATER"   : {          #dummy ONLY, TDK doesn't have READER_HEATER
            'TCS1'                     :  -0.254,
            'TCS2'                     :  0.0,
            
            'TCS1_USL'                 : -0.127,              #  Angstroms/C
            'TCS1_LSL'                 : -1.016,              #  Angstroms/C
            
            'MODIFIED_SLOPE_USL'       : -0.127,              # fold limits in Ang/C
            'MODIFIED_SLOPE_LSL'       : -1.016,              # fold limits in Ang/C
            'enableModifyTCS_values'   : 1,
            
            'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
            'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
            
            'dTc'                      : 0.0005*254,          #  Angstroms/C
            'dTh'                      : -0.002*254,          #  Angstroms/C
            'COLD_TEMP_DTC'            : 10,
            'HOT_TEMP_DTH'             : 55,
            'clearanceDataType'        : 'Read Clearance',
            'dThR'                     : (-0.298103195, -0.404627717, -0.344044506, -0.236665516, -0.185345043,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
            'dTcR'                     : (0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
         },
      },
   },# end of HWY
   'RHO'      : {
      'ATTRIBUTE':'AABType',
      'DEFAULT': '501.11',
      '501.02': {
         "WRITER_HEATER"   : {
            'TCS1'                     :  -0.254,
            'TCS2'                     :  0.0,
            
            'TCS1_USL'                 : -0.127,              #  Angstroms/C
            'TCS1_LSL'                 : -1.016,              #  Angstroms/C
            
            'MODIFIED_SLOPE_USL'       : -0.127,              # fold limits in Ang/C
            'MODIFIED_SLOPE_LSL'       : -1.016,              # fold limits in Ang/C
            'enableModifyTCS_values'   : 1,
            
            'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
            'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
            
            'dTc'                      :  0.0005*254,            #  Angstroms/C
            'dTh'                      :  -0.002*254,            #  Angstroms/C
            'COLD_TEMP_DTC'            : 10,
            'HOT_TEMP_DTH'             : 55,
            'clearanceDataType'        : 'Write Clearance',
            'dThR'                     : (-0.298103195, -0.404627717, -0.344044506, -0.236665516, -0.185345043,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
            'dTcR'                     : (0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
         },
         "READER_HEATER"   : {          #dummy ONLY, TDK doesn't have READER_HEATER
            'TCS1'                     :  -0.254,
            'TCS2'                     :  0.0,
            
            'TCS1_USL'                 : -0.127,              #  Angstroms/C
            'TCS1_LSL'                 : -1.016,              #  Angstroms/C
            
            'MODIFIED_SLOPE_USL'       : -0.127,              # fold limits in Ang/C
            'MODIFIED_SLOPE_LSL'       : -1.016,              # fold limits in Ang/C
            'enableModifyTCS_values'   : 1,
            
            'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
            'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
            
            'dTc'                      : 0.0005*254,          #  Angstroms/C
            'dTh'                      : -0.002*254,          #  Angstroms/C
            'COLD_TEMP_DTC'            : 10,
            'HOT_TEMP_DTH'             : 55,
            'clearanceDataType'        : 'Read Clearance',
            'dThR'                     : (-0.298103195, -0.404627717, -0.344044506, -0.236665516, -0.185345043,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
            'dTcR'                     : (0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
         },
      },# end of 501.02
      '501.11': {
         "WRITER_HEATER"   : {
            'TCS1'                     :  -0.254,
            'TCS2'                     :  0.0,
            
            'TCS1_USL'                 : -0.127,              #  Angstroms/C
            'TCS1_LSL'                 : -1.016,              #  Angstroms/C
            
            'MODIFIED_SLOPE_USL'       : -0.127,              # fold limits in Ang/C
            'MODIFIED_SLOPE_LSL'       : -1.016,              # fold limits in Ang/C
            'enableModifyTCS_values'   : 1,
            
            'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
            'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
            
            'dTc'                      :  0.0005*254,            #  Angstroms/C
            'dTh'                      :  -0.002*254,            #  Angstroms/C
            'COLD_TEMP_DTC'            : 10,
            'HOT_TEMP_DTH'             : 55,
            'clearanceDataType'        : 'Write Clearance',
            'dThR'                     : (-0.298103195, -0.404627717, -0.344044506, -0.236665516, -0.185345043,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
            'dTcR'                     : (0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
         },
         "READER_HEATER"   : {          #dummy ONLY, TDK doesn't have READER_HEATER
            'TCS1'                     :  -0.254,
            'TCS2'                     :  0.0,
            
            'TCS1_USL'                 : -0.127,              #  Angstroms/C
            'TCS1_LSL'                 : -1.016,              #  Angstroms/C
            
            'MODIFIED_SLOPE_USL'       : -0.127,              # fold limits in Ang/C
            'MODIFIED_SLOPE_LSL'       : -1.016,              # fold limits in Ang/C
            'enableModifyTCS_values'   : 1,
            
            'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
            'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
            
            'dTc'                      : 0.0005*254,          #  Angstroms/C
            'dTh'                      : -0.002*254,          #  Angstroms/C
            'COLD_TEMP_DTC'            : 10,
            'HOT_TEMP_DTH'             : 55,
            'clearanceDataType'        : 'Read Clearance',
            'dThR'                     : (-0.298103195, -0.404627717, -0.344044506, -0.236665516, -0.185345043,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
            'dTcR'                     : (0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
         },
      },# end of 501.11
   },# end of RHO
}
##################COPY FROM YARRABP END##############################

#
if not testSwitch.FE_0169232_341036_ENABLE_AFH_TGT_CLR_CANON_PARAMS :
   tcc_DH_values = tcc_DH_dict_178



tcc_OFF = {
   "WRITER_HEATER"   : {
      'TCS1'                     :  0,
      'TCS2'                     :  0.0,
      'dTc'                      :  0,            #  Angstroms/C
      'dTh'                      :  0,            #  Angstroms/C
      'COLD_TEMP_DTC'            : 10,
      'HOT_TEMP_DTH'             : 55,
   },
   "READER_HEATER"   : {
      'TCS1'                     :  0,
      'TCS2'                     :  0.0,
      'dTc'                      :  0,            #  Angstroms/C
      'dTh'                      :  0,            #  Angstroms/C
      'COLD_TEMP_DTC'            : 10,
      'HOT_TEMP_DTH'             : 55,
   },
}

