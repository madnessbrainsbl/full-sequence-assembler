#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Test Parameters for Extreme3
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/11/30 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Amazon/AFH_params_Rosewood.py $
# $Revision: #10 $
# $DateTime: 2016/11/30 23:34:39 $
# $Author: yihua.jiang $perp
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Amazon/AFH_params_Rosewood.py#10 $
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

AAB_TYPE = { # Defaul AAB TYPE to override Config VAR
   'ATTRIBUTE': 'HGA_SUPPLIER',
   'DEFAULT'  : 'RHO',
   'RHO'      : '501.16',
   'TDK'      : '25RW3E',
   'HWY'      : 'H_25RW3E',
}
#Each Prea-amp + AAB + Power Mode combination will have 2 sets of coefficients.
#   1. WP + Heater
#   2. Heater only
#Coefficient abstraction..
#
AAB_RHO = ('501.11', '501.14', '501.16', '501.25', '501.30', '501.41','501.42',)
AAB_TDK = ('25AS2M3', '25RW3E',)
AAB_HWY = ('H_25AS2M3', 'H_25RW3', 'H_25RW3E',)

DefaultRHOAABType = '501.16'
DefaultTDKAABType = '25RW3E'
DefaultHWYAABType = 'H_25RW3E'
DefaultAABType = DefaultRHOAABType

#Attributes used to detect the head manufacturer.
HGA_SUPPLIER_LOOKUP = {
      'RHO': { 'HGA_SUPPLIER' : ('RHO') },
      'TDK': { 'HGA_SUPPLIER' : ('TDK') },
      'HWY': { 'HGA_SUPPLIER' : ('HWY') },
      }
#Attributes used to detect the wafer code.
WAFER_CODE_MATRIX = {
      'SDK' : { 'MEDIA_CODE' : ('PH','DK','DT','DH', 'WT','WK','PK','WT','PT','WH') },
      'RMO' : { 'MEDIA_CODE' : ('PA','PF','SG','SF','SM','SW','SE','SA','WF','PF','WW','PW','WA') },
      }

ATTR_AAB_MATRIX = {}


# ####### Tgt Clr related params START here ##########
uvMediaBackoff = {
   'ATTRIBUTE' : 'UVProcess',
   'DEFAULT'   : False,
   False       : 0,
   True        : 2,
}

afhZoneTargets = {
   'ATTRIBUTE' : 'HGA_SUPPLIER',
   'DEFAULT'   : 'RHO',
   'RHO'       :
   {
      'ATTRIBUTE' : 'AABType',
      'DEFAULT'   : '501.16',
      '501.16'    : {
         'ATTRIBUTE': 'BG',
         'DEFAULT'  : 'OEM1B',
         'OEM1B'    : {
         'TGT_WRT_CLR'           : { "EQUATION" : "tuple( [ 9 for i in range(self.dut.numZones + 1 - 16)] + [ 11 for i in range(15)] + [9] )" },
         'TGT_MAINTENANCE_CLR'   : { "EQUATION" : "tuple( [ 9 for i in range(self.dut.numZones + 1 - 16)] + [ 11 for i in range(15)] + [9] )" },
         'TGT_PREWRT_CLR'        : { "EQUATION" : "tuple( [ 9 for i in range(self.dut.numZones + 1 - 16)] + [ 11 for i in range(15)] + [9] )" },
         'TGT_RD_CLR'            : { "EQUATION" : "tuple( [(12+TP.uvMediaBackoff) for i in range(self.dut.numZones + 1)] )" },
            },
         'SBS'      : {
            'TGT_WRT_CLR'           : { "EQUATION" : "[9]*144 + [11]*6 + [9]" },
            'TGT_MAINTENANCE_CLR'   : { "EQUATION" : "tuple( [ 9 for i in range(self.dut.numZones + 1)] )" },
            'TGT_PREWRT_CLR'        : { "EQUATION" : "[9]*144 + [11]*6 + [9]" },
            'TGT_RD_CLR'            : { "EQUATION" : "tuple( [(12+TP.uvMediaBackoff) for i in range(self.dut.numZones + 1)] )" },
            },
      },
      '501.42'    : {
         'TGT_WRT_CLR'           : { "EQUATION" : "tuple( [ 7 for i in range(self.dut.numZones + 1 - 16)] + [ 9 for i in range(15)] + [7] )" },
         'TGT_MAINTENANCE_CLR'   : { "EQUATION" : "tuple( [ 7 for i in range(self.dut.numZones + 1 - 16)] + [ 9 for i in range(15)] + [7] )" },
         'TGT_PREWRT_CLR'        : { "EQUATION" : "tuple( [ 7 for i in range(self.dut.numZones + 1 - 16)] + [ 9 for i in range(15)] + [7] )" },
         'TGT_RD_CLR'            : { "EQUATION" : "tuple( [12 for i in range(self.dut.numZones + 1)] )" },
      },
   },
   'HWY'       :
   {
      'ATTRIBUTE' : 'AABType',
      'DEFAULT'   : 'H_25RW3E',
      'H_25RW3E'  : {
            'TGT_WRT_CLR'           : { "EQUATION" : "tuple( [ 9 for i in range(self.dut.numZones + 1)] )" },
            'TGT_MAINTENANCE_CLR'   : { "EQUATION" : "tuple( [ 9 for i in range(self.dut.numZones + 1)] )" },
            'TGT_PREWRT_CLR'        : { "EQUATION" : "tuple( [ 9 for i in range(self.dut.numZones + 1)] )" },
            'TGT_RD_CLR'            : { "EQUATION" : "tuple( [(14+TP.uvMediaBackoff) for i in range(self.dut.numZones + 1)] )" },
      },
   },
   'TDK'       :
   {
      'ATTRIBUTE' : 'AABType',
      'DEFAULT'   : '25RW3E',
      '25RW3E'    : {
         'TGT_WRT_CLR'           : { "EQUATION" : "tuple( [ 11 for i in range(self.dut.numZones + 1)] )" },
         'TGT_MAINTENANCE_CLR'   : { "EQUATION" : "tuple( [ 11 for i in range(self.dut.numZones + 1)] )" },
         'TGT_PREWRT_CLR'        : { "EQUATION" : "tuple( [ 11 for i in range(self.dut.numZones + 1)] )" },
         'TGT_RD_CLR'            : { "EQUATION" : "tuple( [(16+TP.uvMediaBackoff) for i in range(self.dut.numZones + 1)] )" },
      },
   },
}

if testSwitch.HAMR:
    afhZoneTargets = {
       'TGT_WRT_CLR'           : { "EQUATION" : "tuple( [ 30 for i in range(self.dut.numZones + 1)] )" },
       'TGT_MAINTENANCE_CLR'   : { "EQUATION" : "tuple( [ 45 for i in range(self.dut.numZones + 1)] )" },
       'TGT_PREWRT_CLR'        : { "EQUATION" : "tuple( [ 30 for i in range(self.dut.numZones + 1)] )" },
       'TGT_RD_CLR'            : { "EQUATION" : "tuple( [ 30 for i in range(self.dut.numZones + 1)] )" },
    }
# ####### Tgt Clr related params END here ##########



prm_191_0002['CWORD1'] = (0x02D1,)
Test135_numHeadRetries = 3  # Retry limit in T135. Set to 5. Default is 3


#### NOTE:  TCC related params are in Angstroms now

tcc_DH_dict_178 = {
   'ATTRIBUTE' : 'HGA_SUPPLIER',
   'DEFAULT'   : 'RHO',
   'TDK'       :
   {
      'ATTRIBUTE' : 'AABType',
      'DEFAULT'   : '25RW3E',
      '25RW3E'    : {
         'WRITER_HEATER'   : {
            'TCS1'                     :  -0.1940,
            'TCS2'                     :  0.0,

            'TCS1_USL'                 : 0.0522,               #  Angstroms/C
            'TCS1_LSL'                 : -0.8419,              #  Angstroms/C

            'MODIFIED_SLOPE_USL'       : 0.0522,               # fold limits in Ang/C
            'MODIFIED_SLOPE_LSL'       : -0.3916,              # fold limits in Ang/C
            'enableModifyTCS_values'   : 1,
#            'enableCalculateTCS_RSquare'   : 1,

            'TCS2_USL'                 :  1.0,                 #  1 A/C (essentially disable)
            'TCS2_LSL'                 : -1.0,                 # -1 A/C (essentially disable)

            'dTc'                      :  -0.2540,             #  Angstroms/C
            'dTh'                      :  -0.2540,             #  Angstroms/C
            'COLD_TEMP_DTC'            : 10,
            'HOT_TEMP_DTH'             : 55,
            'clearanceDataType'        : 'Write Clearance',
            'dThR'                     : (-0.8615, -0.8505, -0.21987, -0.236665516, -0.185345043,), # (-0.3097, -0.3051, -0.2456, -0.236665516, -0.185345043,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
            'dTcR'                     : (0.06801, 0.02065, 0.02417, 0.137140324, 0.11726935,), # (-0.1677, -0.1366, -0.1722, 0.137140324, 0.11726935,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
         },
         'READER_HEATER'   : {
            'TCS1'                     :  -0.3189,
            'TCS2'                     :  0.0,

            'TCS1_USL'                 : 0.0522,               #  Angstroms/C
            'TCS1_LSL'                 : -0.8419,              #  Angstroms/C

            'MODIFIED_SLOPE_USL'       : 0.0522,               # fold limits in Ang/C
            'MODIFIED_SLOPE_LSL'       : -0.5499,              # fold limits in Ang/C
            'enableModifyTCS_values'   : 1,
#            'enableCalculateTCS_RSquare'   : 1,

            'TCS2_USL'                 :  1.0,                 #  1 A/C (essentially disable)
            'TCS2_LSL'                 : -1.0,                 # -1 A/C (essentially disable)

            'dTc'                      : 0,                    #  Angstroms/C
            'dTh'                      : -0.3810,              #  Angstroms/C
            'COLD_TEMP_DTC'            : 10,
            'HOT_TEMP_DTH'             : 55,
            'clearanceDataType'        : 'Read Clearance',
            'dThR'                     : (-0.4589, -0.4220, -0.2849, -0.236665516, -0.185345043,),  # (-0.4392, -0.4302, -0.4266, -0.236665516, -0.185345043,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
            'dTcR'                     : (0.09556, 0.04283, 0.09028, 0.137140324, 0.11726935,), # (0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
         },
      }, # 25AS2M3
   },# end of TDK
   'HWY'       :
   {
      'ATTRIBUTE' : 'AABType',
      'DEFAULT'   : 'H_25RW3E',
      'H_25RW3E'  : {
         'WRITER_HEATER'   : {
            'TCS1'                     :  -0.056,
            'TCS2'                     :  0.0,

            'TCS1_USL'                 : 0.0522,               #  Angstroms/C
            'TCS1_LSL'                 : -0.8419,              #  Angstroms/C

            'MODIFIED_SLOPE_USL'       : 0.0522,               # fold limits in Ang/C
            'MODIFIED_SLOPE_LSL'       : -0.258, #-0.8419,              # fold limits in Ang/C
            'enableModifyTCS_values'   : 1,
#            'enableCalculateTCS_RSquare'   : 1,

            'TCS2_USL'                 :  1.0,                 #  1 A/C (essentially disable)
            'TCS2_LSL'                 : -1.0,                 # -1 A/C (essentially disable)

            'dTc'                      :  -0.2540,             #  Angstroms/C
            'dTh'                      :  -0.2540,             #  Angstroms/C
            'COLD_TEMP_DTC'            : 10,
            'HOT_TEMP_DTH'             : 55,
            'clearanceDataType'        : 'Write Clearance',
            'dThR'                     : (-0.2371, -0.2906, -0.2226, -0.236665516, -0.185345043,), #(-0.3097, -0.3051, -0.2456, -0.236665516, -0.185345043,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
            'dTcR'                     : (-0.1011, -0.1433, -0.2633, 0.137140324, 0.11726935,), #(-0.1677, -0.1366, -0.1722, 0.137140324, 0.11726935,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
         },
         'READER_HEATER'   : {
            'TCS1'                     :  -0.164,
            'TCS2'                     :  0.0,

            'TCS1_USL'                 : 0.0522,               #  Angstroms/C
            'TCS1_LSL'                 : -0.8419,              #  Angstroms/C

            'MODIFIED_SLOPE_USL'       : 0.0522,               # fold limits in Ang/C
            'MODIFIED_SLOPE_LSL'       : -0.445, #-0.8419,              # fold limits in Ang/C
            'enableModifyTCS_values'   : 1,
#            'enableCalculateTCS_RSquare'   : 1,

            'TCS2_USL'                 :  1.0,                 #  1 A/C (essentially disable)
            'TCS2_LSL'                 : -1.0,                 # -1 A/C (essentially disable)

            'dTc'                      : 0,                    #  Angstroms/C
            'dTh'                      : -0.3810,              #  Angstroms/C
            'COLD_TEMP_DTC'            : 10,
            'HOT_TEMP_DTH'             : 55,
            'clearanceDataType'        : 'Read Clearance',
            'dThR'                     : (-0.4692, -0.4850, -0.4880, -0.236665516, -0.185345043,),  #(-0.4392, -0.4302, -0.4266, -0.236665516, -0.185345043,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
            'dTcR'                     : (0.0, -0.000, 0.0, 0.137140324, 0.11726935,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
         },
      }, # H_25AS2M3
   },# end of HWY
   'RHO'       :
   {
      'ATTRIBUTE' : 'AABType',
      'DEFAULT'   : '501.16',
      '501.16'    : {
         'WRITER_HEATER'   : {
            'TCS1'                     :  -0.174, #-0.00017275u, #previous: 0.02667A/0.000105u, updated on 19 Oct 2011.
            'TCS2'                     :  0.0,

            'TCS1_USL'                 : 0,                    #  Angstroms/C
            'TCS1_LSL'                 : -0.8308,              #  Angstroms/C

            'MODIFIED_SLOPE_USL'       : 0,                    # fold limits in Ang/C
            'MODIFIED_SLOPE_LSL'       : -0.358, #-0.8308,              # fold limits in Ang/C
            'enableModifyTCS_values'   : 1,
#            'enableCalculateTCS_RSquare'   : 1,

            'TCS2_USL'                 :  1.0,                 #  1 A/C (essentially disable)
            'TCS2_LSL'                 : -1.0,                 # -1 A/C (essentially disable)

            'dTc'                      :  -0.125, #0.20930108, #0.00082402u #previous: 0.1171194A/0.00046110u  #  Angstroms/C
            'dTh'                      :  -0.2286,             #  Angstroms/C
            'COLD_TEMP_DTC'            : 10,
            'HOT_TEMP_DTH'             : 55,
            'clearanceDataType'        : 'Write Clearance',
            'dThR'                     : (-0.3109, -0.3325, -0.3967, -0.236665516, -0.185345043,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
            'dTcR'                     : (-0.00, -0.159, -0.194, 0.137140324, 0.11726935,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
         },
         'READER_HEATER'   : {
            'TCS1'                     :  -0.391, #-0.0019492u #previous: -0.3807714A/-0.0014991u
            'TCS2'                     :  0.0,

            'TCS1_USL'                 : 0,                    #  Angstroms/C
            'TCS1_LSL'                 : -1.0157,              #  Angstroms/C

            'MODIFIED_SLOPE_USL'       : 0,                    # fold limits in Ang/C
            'MODIFIED_SLOPE_LSL'       : -0.545, #-1.0157,              # fold limits in Ang/C
            'enableModifyTCS_values'   : 1,
#            'enableCalculateTCS_RSquare'   : 1,

            'TCS2_USL'                 :  1.0,                 #  1 A/C (essentially disable)
            'TCS2_LSL'                 : -1.0,                 # -1 A/C (essentially disable)

            'dTc'                      :  0,                   #  Angstroms/C
            'dTh'                      :  -0.4318,             #  Angstroms/C
            'COLD_TEMP_DTC'            : 10,
            'HOT_TEMP_DTH'             : 55,
            'clearanceDataType'        : 'Read Clearance',
            'dThR'                     : (-1.0540, -1.0540, -1.0540, -0.236665516, -0.185345043,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
            'dTcR'                     : (0.0, -0.000, 0.0, 0.137140324, 0.11726935,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
         },
      }, # 501.16
      '501.42'    : {
         'WRITER_HEATER'   : {
            'TCS1'                     :  -0.174, #-0.00017275u, #previous: 0.02667A/0.000105u, updated on 19 Oct 2011.
            'TCS2'                     :  0.0,

            'TCS1_USL'                 : 0,                    #  Angstroms/C
            'TCS1_LSL'                 : -0.8308,              #  Angstroms/C

            'MODIFIED_SLOPE_USL'       : 0,                    # fold limits in Ang/C
            'MODIFIED_SLOPE_LSL'       : -0.358, #-0.8308,              # fold limits in Ang/C
            'enableModifyTCS_values'   : 1,
#            'enableCalculateTCS_RSquare'   : 1,

            'TCS2_USL'                 :  1.0,                 #  1 A/C (essentially disable)
            'TCS2_LSL'                 : -1.0,                 # -1 A/C (essentially disable)

            'dTc'                      :  -0.125, #0.20930108, #0.00082402u #previous: 0.1171194A/0.00046110u  #  Angstroms/C
            'dTh'                      :  -0.2286,             #  Angstroms/C
            'COLD_TEMP_DTC'            : 10,
            'HOT_TEMP_DTH'             : 55,
            'clearanceDataType'        : 'Write Clearance',
            'dThR'                     : (-0.3367, -0.2222, -0.2317, -0.236665516, -0.185345043,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
            'dTcR'                     : (-0.0265, -0.0431, -0.0469, 0.137140324, 0.11726935,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
         },
         'READER_HEATER'   : {
            'TCS1'                     :  -0.391, #-0.0019492u #previous: -0.3807714A/-0.0014991u
            'TCS2'                     :  0.0,

            'TCS1_USL'                 : 0,                    #  Angstroms/C
            'TCS1_LSL'                 : -1.0157,              #  Angstroms/C

            'MODIFIED_SLOPE_USL'       : 0,                    # fold limits in Ang/C
            'MODIFIED_SLOPE_LSL'       : -0.545, #-1.0157,              # fold limits in Ang/C
            'enableModifyTCS_values'   : 1,
#            'enableCalculateTCS_RSquare'   : 1,

            'TCS2_USL'                 :  1.0,                 #  1 A/C (essentially disable)
            'TCS2_LSL'                 : -1.0,                 # -1 A/C (essentially disable)

            'dTc'                      :  0,                   #  Angstroms/C
            'dTh'                      :  -0.4318,             #  Angstroms/C
            'COLD_TEMP_DTC'            : 10,
            'HOT_TEMP_DTH'             : 55,
            'clearanceDataType'        : 'Read Clearance',
            'dThR'                     : (-0.3328, -0.4839, -0.2263, -0.236665516, -0.185345043,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
            'dTcR'                     : (-0.0659, -0.0422, -0.0397, 0.137140324, 0.11726935,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
         },
      }, # 501.42
   },# end of RHO
}

#TCS_WARP_ZONES = {1:(0,5), 10:(6,10),16:(11,16),19:(17,19),22:(20,23),}  # (TCC@tested zone, applied to zone start, applied to zone end)
TCS_WARP_ZONES  = {
   'ATTRIBUTE':'numZones',
   'DEFAULT': 150,
   60:  {0:(0,20), 1:(21,40),2:(41,59),},
   120: {0:(0,40), 1:(41,80),2:(81,119),},
   150: {0:(0,50), 1:(51,100),2:(101,149),},
   180: {0:(0,60), 1:(61,120),2:(121,179),},
}
##################COPY FROM YARRABP END##############################

if not testSwitch.FE_0169232_341036_ENABLE_AFH_TGT_CLR_CANON_PARAMS :
   tcc_DH_values = tcc_DH_dict_178



tcc_OFF = {
          'WRITER_HEATER'   : {
                   'TCS1'                     :  0,
                   'TCS2'                     :  0.0,
                   'dTc'                      :  0,            #  Angstroms/C
                   'dTh'                      :  0,            #  Angstroms/C
                   'COLD_TEMP_DTC'            : 10,
                   'HOT_TEMP_DTH'             : 55,
                   },
          'READER_HEATER'   : {
                   'TCS1'                     :  0,
                   'TCS2'                     :  0.0,
                   'dTc'                      :  0,            #  Angstroms/C
                   'dTh'                      :  0,            #  Angstroms/C
                   'COLD_TEMP_DTC'            : 10,
                   'HOT_TEMP_DTH'             : 55,
                   },
}

