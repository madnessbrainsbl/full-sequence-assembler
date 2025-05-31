#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Test Parameters for Extreme3
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/12/22 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Amazon/AFH_coeffs_RosewoodLC.py $
# $Revision: #9 $
# $DateTime: 2016/12/22 19:01:21 $
# $Author: chiliang.woo $perp
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Amazon/AFH_coeffs_RosewoodLC.py#9 $
# Level: 1
#---------------------------------------------------------------------------------------------------------#

from Constants import *
from Test_Switches import testSwitch
from AFH_coeffs_Rosewood import *

PRE_AMP_HEATER_MODE = 'LO_POWER'
triseValuesDefaultTI  = [ 3 ] * 180
triseValuesDefaultLSI = [ 2 ] * 180
ovsRiseTimeValuesTI = ovsRiseTimeValuesLSI  = [ 0 ] * 180

# ================================================================================================
#   TDK coefficients
# ================================================================================================
TDK_LSI5830_25RW3E_5F627_2H = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00048496, -0.00002796, 0.00000006, 0.00652842, -0.00000093, -0.00001473, 1.06445989, -0.00007097, -0.00439092, 0.09048378, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00028265, 0.00743663, -0.00002092, -0.00004162, -0.00000061, 0.00000009, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00129098, -0.00000513, 0.00000002, 0, 0, 0, 0.00002706, -0.00000008, 0, 0.00000360, -0.00000511, -0.00000006, 0, 0.00000018, 0.00000052, -0.00000144, -0.00000002, 0, 0.00000010, 0.00000050, 0.00000001, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.12,0,0],
   'gammaWriter'        : [1.14,0,0],
   'gammaReaderHeater'  : [0.96,0,0],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
   'CoeffTrackingNo'    : 'RLCTL001',
}

TDK_TI7551_25RW3E_5F608_2H = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00138994, -0.00003788, 0.00000008, 0.00659382, -0.00000081, -0.00001487, 1.03442651, -0.00005296, -0.00409621, 0.40340116, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00238158, 0.00744193, -0.00002048, -0.00006018, -0.00000038, 0.00000012, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00099011, -0.00000842, 0.00000003, 0, 0, 0, 0.00001301, -0.00000011, 0, 0.00000486, -0.00000495, -0.00000003, 0, 0.00000014, 0.00000006, -0.00001732, -0.00000005, 0, 0.00000029, 0.00000102, 0.00000042, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.12,0,0],
   'gammaWriter'        : [1.14,0,0],
   'gammaReaderHeater'  : [0.96,0,0],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
   'CoeffTrackingNo'    : 'RLCTT002',
}

TDK_LSI5830_25RW3E_5F816_4H = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00071035, -0.00002990, 0.00000007, 0.00646089, -0.00000095, -0.00001333, 1.06889528, -0.00006739, -0.00370331, -0.21918368, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00075240, 0.00750239, -0.00002042, -0.00004654, -0.00000061, 0.00000010, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00048066, -0.00000157, 0.00000001, 0, 0, 0, -0.00000072, -0.00000008, 0, 0.00000364, -0.00000601, -0.00000003, 0, 0.00000012, 0.00000019, -0.00000710, -0.00000001, 0, 0.00000012, 0.00000067, 0.00000005, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.12,0,0],
   'gammaWriter'        : [1.14,0,0],
   'gammaReaderHeater'  : [0.96,0,0],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
   'CoeffTrackingNo'    : 'RC2TL009',
}

TDK_TI7551_25RW3E_5F815_4H = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[-0.00006173, -0.00002940, 0.00000007, 0.00638630, -0.00000092, -0.00001394, 1.06092736, -0.00008681, -0.00426948, -0.04284349, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00101766, 0.00745205, -0.00002136, -0.00004821, -0.00000054, 0.00000010, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00076595, -0.00000527, 0.00000002, 0, 0, 0, 0.00001160, -0.00000011, 0, 0.00000450, -0.00002247, -0.00000001, 0, 0.00000008, 0.00000054, -0.00000304, -0.00000002, 0, 0.00000016, 0.00000079, -0.00000000, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.12,0,0],
   'gammaWriter'        : [1.14,0,0],
   'gammaReaderHeater'  : [0.96,0,0],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
   'CoeffTrackingNo'    : 'RC2TT010',
}
# ================================================================================================
#   RHO coefficients
# ================================================================================================
RHO_TI7551_50116_PD7_2H = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00654755, -0.00005970, 0.00000013, 0.00687477, 0.00000100, -0.00002658, 1.00716254, 0.00000183, -0.00968687, -0.01815421, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00509625, 0.00468000, -0.00001115, -0.00006900, 0.00000060, 0.00000016, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00191717, -0.00002001, 0.00000005, 0, 0, 0, -0.00000921, 0.00000005, 0, 0.00000530, -0.00001789, -0.00000002, 0, 0.00000017, 0.00000043, -0.00001751, -0.00000003, 0, 0.00000023, 0.00000101, 0.00000040, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.20539999, 0.00004000, 0.00000000,],
   'gammaWriter'        : [1.01820004, -0.00004000, 0.00000000,],
   'gammaReaderHeater'  : [1.00095999, 0.00000000, 0.00000000,],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
   'CoeffTrackingNo'    : 'RLCRT003',
}

RHO_LSI5830_50116_PD7_2H = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00319500, -0.00006697, 0.00000016, 0.00739589, 0.00000076, -0.00002878, 1.08266533, -0.00003303, -0.00925798, -0.64082546, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00411065, 0.00493284, -0.00001202, -0.00008000, 0.00000051, 0.00000018, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00155923, -0.00001562, 0.00000004, 0, 0, 0, -0.00001786, 0.00000004, 0, 0.00000432, -0.00000477, -0.00000004, 0, 0.00000019, 0.00000025, -0.00001066, -0.00000002, 0, 0.00000013, 0.00000049, 0.00000020, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.20539999, 0.00004000, 0.00000000,],
   'gammaWriter'        : [1.01820004, -0.00004000, 0.00000000,],
   'gammaReaderHeater'  : [1.00095999, 0.00000000, 0.00000000,],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
   'CoeffTrackingNo'    : 'RLCRL004',
}
RHO_LSI5830_50142_SD7_2H = { 
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00708960, -0.00005040, 0.00000011, 0.00616283, 0.00000132, -0.00002100, 0.98655249, -0.00002152, -0.00636361, -0.03864783, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00183566, 0.00422861, -0.00001081, -0.00004058, 0.00000078, 0.00000010, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00137654, -0.00000115, 0.00000000, 0, 0, 0, -0.00001674, 0.00000010, 0, 0.00000458, -0.00000094, -0.00000004, 0, 0.00000011, 0.00000026, -0.00001206, -0.00000001, 0, 0.00000009, 0.00000056, 0.00000021, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.30525584, 0.00001885, -0.00000004, ],
   'gammaWriter'        : [1.34481060, -0.00003660, 0.00000010, ],
   'gammaReaderHeater'  : [1.00084648, -0.00000190, 0.00000000, ],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
   'CoeffTrackingNo'    : 'RLCRL012',
}
RHO_TI7551_50142_OJD_2H = { 
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00344460, -0.00002638, 0.00000008, 0.00640148, 0.00000080, -0.00002621, 1.01897294, -0.00004714, -0.00850115, -0.06605537, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00180584, 0.00410400, -0.00001061, -0.00002294, 0.00000057, 0.00000006, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00233037, -0.00002095, 0.00000005, 0, 0, 0, -0.00002278, 0.00000011, 0, 0.00000590, -0.00002992, 0.00000000, 0, 0.00000013, 0.00000046, -0.00001637, -0.00000002, 0, 0.00000028, 0.00000138, 0.00000008, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.30525589, 0.00001885, -0.00000004, ],
   'gammaWriter'        : [1.34481061, -0.00003660, 0.00000010, ],
   'gammaReaderHeater'  : [1.00084651, -0.00000190, 0.00000000, ],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
   'CoeffTrackingNo'    : 'RLCRT017',
}
RHO_TI7551_50116_PD7_4H = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00220396, -0.00005949, 0.00000014, 0.00694379, 0.00000081, -0.00002455, 1.02288440, 0.00000275, -0.00906084, -0.13737788, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00301297, 0.00477361, -0.00001091, -0.00006725, 0.00000056, 0.00000015, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00168800, -0.00001453, 0.00000003, 0, 0, 0, -0.00001149, 0.00000003, 0, 0.00000499, -0.00002186, -0.00000002, 0, 0.00000009, 0.00000037, -0.00001675, -0.00000002, 0, 0.00000020, 0.00000125, 0.00000024, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.20539999, 0.00004000, 0.00000000,],
   'gammaWriter'        : [1.01820004, -0.00004000, 0.00000000,],
   'gammaReaderHeater'  : [1.00095999, 0.00000000, 0.00000000,],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
   'CoeffTrackingNo'    : 'RC2RT007',
}

RHO_LSI5830_50116_PD7_4H = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00480228, -0.00005896, 0.00000013, 0.00683490, 0.00000103, -0.00002346, 1.03395029, 0.00000483, -0.00859496, -0.41518581, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00495250, 0.00471088, -0.00001115, -0.00006928, 0.00000064, 0.00000015, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00205218, -0.00001301, 0.00000003, 0, 0, 0, -0.00000997, 0.00000003, 0, 0.00000372, -0.00000342, -0.00000002, 0, 0.00000015, 0.00000007, -0.00000179, -0.00000002, 0, 0.00000008, 0.00000054, 0.00000005, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.20539999, 0.00004000, 0.00000000,],
   'gammaWriter'        : [1.01820004, -0.00004000, 0.00000000,],
   'gammaReaderHeater'  : [1.00095999, 0.00000000, 0.00000000,],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
   'CoeffTrackingNo'    : 'RC2RL008',
}
RHO_LSI5830_50142_SD7_4H = { 
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00281604, -0.00003036, 0.00000008, 0.00629427, 0.00000097, -0.00002520, 1.02071255, -0.00004873, -0.00794077, -0.06262444, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00113769, 0.00408009, -0.00001076, -0.00002621, 0.00000065, 0.00000007, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00157708, -0.00000922, 0.00000002, 0, 0, 0, -0.00004014, 0.00000011, 0, 0.00000452, -0.00000473, -0.00000002, 0, 0.00000016, 0.00000012, -0.00001605, 0.00000000, 0, 0.00000012, 0.00000073, 0.00000017, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.30525584, 0.00001885, -0.00000004, ],
   'gammaWriter'        : [1.34481060, -0.00003660, 0.00000010, ],
   'gammaReaderHeater'  : [1.00084648, -0.00000190, 0.00000000, ],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
   'CoeffTrackingNo'    : 'RC2RL013',
}

RHO_TI7551_50142_SD7_4H = { 
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[-0.00239418, -0.00001556, 0.00000006, 0.00639625, 0.00000066, -0.00002485, 1.02213325, -0.00005299, -0.00824499, 0.03071830, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[-0.00170239, 0.00412877, -0.00001042, -0.00002158, 0.00000059, 0.00000006, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00222774, -0.00001767, 0.00000004, 0, 0, 0, -0.00002059, 0.00000011, 0, 0.00000579, -0.00000778, -0.00000003, 0, 0.00000013, 0.00000003, -0.00000025, -0.00000003, 0, 0.00000018, 0.00000152, -0.00000016, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.30525589, 0.00001885, -0.00000004, ],
   'gammaWriter'        : [1.34481061, -0.00003660, 0.00000010, ],
   'gammaReaderHeater'  : [1.00084651, -0.00000190, 0.00000000, ],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
   'CoeffTrackingNo'    : 'RC2RT014',
}

# ================================================================================================
#   HWY coefficients
# ================================================================================================
HWY_LSI5830_25RW3E_6A33D_2H = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00025276, -0.00002808, 0.00000007, 0.00781391, -0.00000124, -0.00002241, 1.06614474, -0.00005978, -0.00474338, -0.11871235, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00068913, 0.00934043, -0.00003126, -0.00004836, -0.00000094, 0.00000011, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00089629, -0.00000144, 0.00000001, 0, 0, 0, 0.00000806, -0.00000009, 0, 0.00000307, -0.00000556, -0.00000004, 0, 0.00000017, 0.00000027, -0.00002381, -0.00000000, 0, 0.00000011, 0.00000067, 0.00000037, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.05999994, 0.00000000, 0.00000000, ],
   'gammaWriter'        : [1.11000001, 0.00000000, 0.00000000, ],
   'gammaReaderHeater'  : [1.00000000, 0.00000000, 0.00000000, ],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
   'CoeffTrackingNo'    : 'RLCHL019',
}
HWY_LSI5830_25RW3E_6A33D_4H = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00072715, -0.00002602, 0.00000006, 0.00779139, -0.00000100, -0.00002190, 1.06650939, -0.00007396, -0.00471337, -0.13211268, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00093271, 0.00937284, -0.00003063, -0.00004334, -0.00000068, 0.00000009, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00028197, 0.00000150, 0.00000000, 0, 0, 0, -0.00001598, -0.00000006, 0, 0.00000325, -0.00000980, -0.00000003, 0, 0.00000010, 0.00000037, -0.00000324, -0.00000002, 0, 0.00000010, 0.00000054, -0.00000003, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.05000000, 0.00000000, 0.00000000, ],
   'gammaWriter'        : [1.11000000, 0.00000000, 0.00000000, ],
   'gammaReaderHeater'  : [1.00000000, 0.00000000, 0.00000000, ],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
   'CoeffTrackingNo'    : 'RC2HL015',
}

HWY_TI7551_25RW3E_5C7C6_2H = {
    'WRT_HTR_PTP_COEF':
    {
    'HI_POWER':[],
    'LO_POWER':[0.00264774, -0.00001673, 0.00000004, 0.00769945, -0.00000098, -0.00002295, 1.02963516, -0.00005676, -0.00522985, 0.36043925, AFH_Uniform_Track_Lbl],
    },
    'HTR_PTP_COEF':
    {
    'HI_POWER':[],
    'LO_POWER':[0.00443044, 0.00906813, -0.00003064, -0.00003767, -0.00000063, 0.00000008, AFH_Uniform_Track_Lbl],
    },
    'WRT_PTP_COEF':
    {
    'HI_POWER':[],
    'LO_POWER':[0.00064366, -0.00000234, 0.00000001, 0, 0, 0, 0.00000683, -0.00000009, 0, 0.00000412, -0.00002634, -0.00000001, 0, 0.00000007, 0.00000076, -0.00001710, -0.00000003, 0, 0.00000017, 0.00000060, 0.00000041, AFH_Uniform_Track_Lbl],
    },
    'gammaWriterHeater' : [1.06000000, 0.00000000, 0.00000000, ],
    'gammaWriter' : [1.11000000, 0.00000000, 0.00000000, ],
    'gammaReaderHeater' : [1.00000000, 0.00000000, 0.00000000, ],
    'isDriveDualHeater' : 1,
    'triseValues' : triseValuesDefaultTI,
    'ovsRiseTimeValues' : ovsRiseTimeValuesTI,
    'CoeffTrackingNo' : 'RLCHT023',
}
# ================================================================================================
# ================================================================================================
# ================================================================================================

clearance_Coefficients = {
   'ATTRIBUTE' : 'PREAMP_TYPE',
   'DEFAULT'   : 'LSI5830',
#  ==================== LSI/Avago preamp ====================
   'LSI5830' :{
      'ATTRIBUTE' : 'AABType',
      'DEFAULT'   : '501.16',
      '501.16'    : {
         'ATTRIBUTE' : 'numPhysHds',
         'DEFAULT'   : 2,
         2           :  RHO_LSI5830_50116_PD7_2H,            # LC4 ROSEWOODLC1D_RHO_LSI_501.16_PD7_18-Apr-2016      
         4           :  RHO_LSI5830_50116_PD7_4H,            # LC8 ROSEWOODLC2D_RHO_LSI_501.16_PD7_25-Apr-2016  
      },
      '501.42'    : {
         'ATTRIBUTE' : 'numPhysHds',
         'DEFAULT'   : 2,
         2           : RHO_LSI5830_50142_SD7_2H,                # 12 ROSEWOODLC1D_RHO_LSI_501.42_SD7_06-Jun-2016
         4           : RHO_LSI5830_50142_SD7_4H,                # 13 ROSEWOODLC2D_RHO_LSI_501.42_SD7_08-Jun-2016
         },
      '25RW3E'       : {
         'ATTRIBUTE' : 'numPhysHds',
         'DEFAULT'   : 2,
         2           : TDK_LSI5830_25RW3E_5F627_2H,          # LC1 ROSEWOODLC1D_TDK_LSI_25RW3E_5F627_12-Apr-2016
         4           : TDK_LSI5830_25RW3E_5F816_4H,          # LC9 ROSEWOODLC2D_TDK_LSI_25RW3E_5F816_26-Apr-2016
         },
      'H_25RW3E'       : {
         'ATTRIBUTE' : 'numPhysHds',
         'DEFAULT'   : 2,
         2           : HWY_LSI5830_25RW3E_6A33D_2H,          # LC19 ROSEWOOD7LC1D_HWY_LSI_25RW3E_6A33D_27-Sep-2016
         4           : HWY_LSI5830_25RW3E_6A33D_4H,          # LC15 ROSEWOOD7LC1D_HWY_LSI_25RW3E_6A33D_16-Aug-2016
         },
   }, # LSI5830 =========
 # ==================== TI preamp ====================
   'TI7551':{
      'ATTRIBUTE' : 'AABType',
      'DEFAULT'   : '501.16',
      '501.16'       : {
         'ATTRIBUTE' : 'numPhysHds',
         'DEFAULT'   : 2,
         2           : RHO_TI7551_50116_PD7_2H,               # LC3 ROSEWOODLC1D_RHO_TI_501.16_PD7_12-Apr-2016
         4           : RHO_TI7551_50116_PD7_4H,               # LC7 ROSEWOODLC2D_RHO_TI_501.16_PD7_25-Apr-2016
      },
      '501.42'    : {
         'ATTRIBUTE' : 'numPhysHds',
         'DEFAULT'   : 2,
         2           : RHO_TI7551_50142_OJD_2H,                # 17 ROSEWOODLC1D_RHO_TI_501.42_OJD_01-Sep-2016
         4           : RHO_TI7551_50142_SD7_4H,                # 14 ROSEWOODLC2D_RHO_TI_501.42_SD7_19-Jul-2016
         },
      '25RW3E'       : {
         'ATTRIBUTE' : 'numPhysHds',
         'DEFAULT'   : 2,
         2           : TDK_TI7551_25RW3E_5F608_2H,            # LC2  ROSEWOODLC1D_TDK_TI_25RW3E_5F608_12-Apr-2016
         4           : TDK_TI7551_25RW3E_5F815_4H,            # LC10 ROSEWOODLC2D_TDK_TI_25RW3E_5F815_04-May-2016
      },
      'H_25RW3E'       : {
         'ATTRIBUTE' : 'numPhysHds',
         'DEFAULT'   : 2,
         2           : HWY_TI7551_25RW3E_5C7C6_2H,          # 22-Dec-2016 #023 ROSEWOOD7LC1D_HWY_25RW3E_TI_0XC200_0X2_5C7C6_2_1
         4           : HWY_TI7551_25RW3E_5C7C6_2H,          # 22-Dec-2016 #023 ROSEWOOD7LC1D_HWY_25RW3E_TI_0XC200_0X2_5C7C6_2_1
         },
   }, # TI7551 =========
}

# clearance_Coefficients = {
   # 'ATTRIBUTE' : 'PREAMP_TYPE',
   # 'DEFAULT'   : 'LSI5830',
   # # ==================== LSI/Avago preamp ====================
   # 'LSI5830' :{
      # 'ATTRIBUTE' : 'AABType',
      # 'DEFAULT'   : '501.16',
      # '501.11'    : {
         # 'ATTRIBUTE' : 'numPhysHds',
         # 'DEFAULT'   : 2,
         # 2           : {
            # 'ATTRIBUTE' : 'HSA_WAFER_CODE',
            # 'DEFAULT'   : 'N2Q',
            # 'NI0'       : RHO_LSI5830_50111_5400,
            # 'NU7'       : RHO_LSI5830_50111_5400_NU7,      # 17
            # 'N2Q'       : RHO_LSI5830_50111_5400_N2Q,      # 19
         # },
         # 4           : {
            # 'ATTRIBUTE' : 'HSA_WAFER_CODE',
            # 'DEFAULT'   : 'N2Q',
            # 'NI0'       : RHO_LSI5830_50111_5400_4H,       # 11
            # 'NU7'       : RHO_LSI5830_50111_5400_NU7,      # 17
            # 'N2Q'       : RHO_LSI5830_50111_N2Q_5400_4H,   # 21
         # },
      # },
      # '501.14'    : {
         # 'ATTRIBUTE' : 'numPhysHds',
         # 'DEFAULT'   : 2,
         # 2           : {
            # 'ATTRIBUTE' : 'HSA_WAFER_CODE',
            # 'DEFAULT'   : 'NG8',
            # 'default'   : RHO_LSI5830_50114_5400,
            # 'NG8'       : RHO_LSI5830_50114_5400_NG8,
         # },
         # 4           : {
            # 'ATTRIBUTE' : 'HSA_WAFER_CODE',
            # 'DEFAULT'   : 'NU7',
            # 'default'   : RHO_LSI5830_50114_5400_4H,           # 18
            # 'NU7'       : RHO_LSI5830_50114_NU7_5400_4H,       # 24
         # },
      # },
      # '501.16'    : {
         # 'ATTRIBUTE' : 'numPhysHds',
         # 'DEFAULT'   : 2,
         # 2           : {
            # 'ATTRIBUTE' : 'HSA_WAFER_CODE',
            # 'DEFAULT'   : 'NL2',
            # 'O2Q'       : RHO_LSI5830_50116_O2Q_5400,          # 30
            # 'N5T'       : RHO_LSI5830_50116_N5T_5400,          # 33
            # 'OT4'       : RHO_LSI5830_50116_OT4_5400,          # 56 ROSEWOOD71D_RHO_501.16_LSI_0X8200_0X2_OT4_2
            # 'NL2'       : RHO_LSI5830_50116_NL2_5400,          # 68 RW71D_RHO_LSI_501.16_NL2_2H_21-Sep-2015
            # 'PD7'       : RHO_LSI5830_50116_PD7_5400,          # 83 RW71D_RHO_LSI_501.16_PD7_2H_06-Nov-2015
         # },
         # 4           :  {
            # 'ATTRIBUTE' : 'HSA_WAFER_CODE',
            # 'DEFAULT'   : 'NL2',
            # 'O2Q'       : RHO_LSI5830_50116_OG8_5400_4H,       # 36
            # 'N4Z'       : RHO_LSI5830_50116_N4Z_5400_4H,       # 44
            # 'NT4'       : RHO_LSI5830_50116_NT4_5400_4H,       # 60
            # 'OT4'       : RHO_LSI5830_50116_OT4_5400_4H,       # 58
            # 'NL2'       : RHO_LSI5830_50116_NL2_5400_4H,       # 69
            # 'PD7'       : RHO_LSI5830_50116_PD7_5400_4H,       # 87 RW72D_RHO_LSI_501.16_PD7_4H_18-Nov-2015
         # },
      # },
      # '501.41'    : {
         # 'ATTRIBUTE' : 'numPhysHds',
         # 'DEFAULT'   : 2,
         # 2           : {
            # 'ATTRIBUTE' : 'HSA_WAFER_CODE',
            # 'DEFAULT'   : 'NL2',
            # 'NL2'       : RHO_LSI5830_50141_NL2_5400,          # 84 RW71D_RHO_LSI_501.41_NL2_2H_06-Nov-2015
         # },
         # 4           : {
            # 'ATTRIBUTE' : 'HSA_WAFER_CODE',
            # 'DEFAULT'   : 'NL2',
            # 'NL2'       : RHO_LSI5830_50141_NL2_5400_4H,       # 86 RW72D_RHO_LSI_501.41_NL2_4H_11-Nov-2015
         # },

      # },
      # '501.42'    : {
         # 'ATTRIBUTE' : 'numPhysHds',
         # 'DEFAULT'   : 2,
         # 2           : RHO_LSI5830_50142_SD7_2H,                # 12 ROSEWOODLC1D_RHO_LSI_501.42_SD7_06-Jun-2016
         # 4           : RHO_LSI5830_50142_SD7_4H,                 # 13 ROSEWOODLC2D_RHO_LSI_501.42_SD7_08-Jun-2016
         # },
      # '501.30'    : {
         # 'ATTRIBUTE' : 'numPhysHds',
         # 'DEFAULT'   : 2,
         # 2           : {
            # 'ATTRIBUTE' : 'HSA_WAFER_CODE',
            # 'DEFAULT'   : 'OG8',
            # 'OG8'       : RHO_LSI5830_50130_OG8_5400,          # 40

         # },
         # 4           : RHO_LSI5830_50130_OG8_5400_4H,          # 38
      # },
      # 'H_25AS2M3' : {
         # 'ATTRIBUTE' : 'numPhysHds',
         # 'DEFAULT'   : 2,
         # 2           : HWY_LSI5830_25AS2M3_5400,
         # 4           : {
            # 'ATTRIBUTE' : 'HSA_WAFER_CODE',
            # 'DEFAULT'   : '4A4C5',
            # '4A3C0'     : HWY_LSI5830_25AS2M3_5400_4H,
            # '4A49H'     : HWY_LSI5830_25AS2M3_4A49H_5400_4H,   # 16
            # '4A4C5'     : HWY_LSI5830_25AS2M3_4A4C5_5400_4H,   # 34
         # },
      # },
      # 'H_25RW3'      : {
         # 'ATTRIBUTE' : 'numPhysHds',
         # 'DEFAULT'   : 2,
         # 2           : HWY_LSI5830_25RW3_5400,                 # 15
         # 4           : HWY_LSI5830_25RW3_5400_4H,              # 23, 4AF1F
      # },
      # 'H_25RW3E'     : {
         # 'ATTRIBUTE' : 'numPhysHds',
         # 'DEFAULT'   : 2,
         # 2           : {
            # 'ATTRIBUTE' : 'HSA_WAFER_CODE',
            # 'DEFAULT'   : '5A5J0',
            # '5A2HH'     : HWY_LSI5830_25RW3E_5A2HH_5400,       # 52
            # '5A3J2'     : HWY_LSI5830_25RW3E_5A3J2_5400,       # 64 RW71D_HWY_LSI_25RW3E_5A3J2_2H_07-Sep-2015
            # '5ABG5'     : HWY_LSI5830_25RW3E_5ABG5_5400,       # 77 RW71D_HWY_LSI_25RW3E_5ABG5_2H_13-Oct-2015
            # '5A5J0'     : HWY_LSI5830_25RW3E_5A5J0_5400,       # 78 RW71D_HWY_LSI_25RW3E_5A5J0_2H_22-Oct-2015
            # '4C677'     : HWY_LSI5830_25RW3E_4C677_5400,       # 91 RW71D_HWY_LSI_25RW3E_4C677_2H_20-Nov-2015
         # },
         # 4           : {
            # 'ATTRIBUTE' : 'HSA_WAFER_CODE',
            # 'DEFAULT'   : '5A99G',
            # '4C6JH'     : HWY_LSI5830_25RW3E_4C6JH_5400_4H,    # 42
            # '4A4C5'     : HWY_LSI5830_25RW3E_4A4C5_5400_4H,    # 35
            # '5A2HH'     : HWY_LSI5830_25RW3E_5A2HH_5400_4H,    # 59
            # '5A3J2'     : HWY_LSI5830_25RW3E_5A3J2_5400_4H,    # 67
            # '5A2HG'     : HWY_LSI5830_25RW3E_5A2HG_5400_4H,    # 74
            # '5A5J0'     : HWY_LSI5830_25RW3E_5A5J0_5400_4H,    # 80
            # '5A99G'     : HWY_LSI5830_25RW3E_5A99G_5400_4H,    # 85
            # '5AA99'     : HWY_LSI5830_25RW3E_5A99G_5400_4H,    # same as #85 5A99G
            # '5A9BJ'     : HWY_LSI5830_25RW3E_5A99G_5400_4H,    # copy 5A99G
         # },
      # },
      # '25RW3E'       : {
         # 'ATTRIBUTE' : 'numPhysHds',
         # 'DEFAULT'   : 2,
         # 2           : {
            # 'ATTRIBUTE' : 'HSA_WAFER_CODE',
            # 'DEFAULT'   : '5F057',
            # '5F068'     : TDK_LSI5830_25RW3E_5F068_5400,       # 62
            # '5F057'     : TDK_LSI5830_25RW3E_5F608_5400,       # 96 RW71D_TDK_LSI_25RW3E_5F608_2H_22-Dec-2015
         # },
         # 4           : {
            # 'ATTRIBUTE' : 'HSA_WAFER_CODE',
            # 'DEFAULT'   : '5F608',
            # '5F608'       : TDK_LSI5830_25RW3E_5F608_5400_4H,                # 94
         # },
      # },
      # '25AS2M3'   : {
         # 'ATTRIBUTE' : 'numPhysHds',
         # 'DEFAULT'   : 2,
         # 2           : HWY_LSI5830_25AS2M3_5400,
         # 4           : TDK_LSI5830_25AS2M3_5400_4H,            # 14, 4F223
      # },
   # }, # LSI5830 =========

   # # HMAR Related StarWood
   # # ==================== LSI preamp ====================
   # 'LSI5235':{
      # 'ATTRIBUTE' : 'AABType',
      # 'DEFAULT'   : '501.11',
      # '501.11'    : {
            # 'ATTRIBUTE' : 'HSA_WAFER_CODE',
            # 'DEFAULT'   : '5W',
            # '5W'       : RHO_LSI5235_5W_5400,
            # 'BZ7'      : RHO_LSI5235_Z7_5400,

      # },
   # },

   # # ==================== TI preamp ====================
   # 'TI7551':{
      # 'ATTRIBUTE' : 'AABType',
      # 'DEFAULT'   : '501.16',
      # '501.11'    : RHO_TI7550_50111_5400,
      # '501.14'    : RHO_TI7551_50114_5400,
      # '501.16'       : {
         # 'ATTRIBUTE' : 'numPhysHds',
         # 'DEFAULT'   : 2,
         # 2           : {
            # 'ATTRIBUTE' : 'HSA_WAFER_CODE',
            # 'DEFAULT'   : 'NL2',
            # 'N4Z'       : RHO_TI7551_50116_N4Z_5400,           # 50
            # 'OT4'       : RHO_TI7551_50116_OT4_5400,           # 55 ROSEWOOD71D_RHO_501.16_TI_0XC200_0X1_OT4_2
            # 'NL2'       : RHO_TI7551_50116_NL2_5400,           # 1-Oct-2015 #72
            # 'PD7'       : RHO_TI7551_50116_PD7_5400,           # 92 RW71D_RHO_TI_501.16_PD7_2H_28-Nov-2015
         # },
         # 4           : {
            # 'ATTRIBUTE' : 'HSA_WAFER_CODE',
            # 'DEFAULT'   : 'NL2',
            # 'OG8'       : RHO_TI7551_50116_OG8_5400_4H,        # 37
            # 'NT4'       : RHO_TI7551_50116_NT4_5400_4H,        # 61
            # 'OT4'       : RHO_TI7551_50116_OT4_5400_4H,        # 57
            # 'NL2'       : RHO_TI7551_50116_NL2_5400_4H,        # 76
            # 'PD7'       : RHO_TI7551_50116_PD7_5400_4H,        # 88 RW72D_RHO_TI_501.16_PD7_4H_18-Nov-2015
         # },
      # },
      # '501.25'    : RHO_TI7551_50125_O2Q_5400,                 # 41
      # '501.30'    : RHO_TI7551_50130_OG8_5400,                 # 39
      # '501.42'    : {
         # 'ATTRIBUTE' : 'numPhysHds',
         # 'DEFAULT'   : 2,
         # 2           : RHO_LSI5830_50142_SD7_2H,                # 12 ROSEWOODLC1D_RHO_LSI_501.42_SD7_06-Jun-2016
         # 4           : RHO_TI7551_50142_SD7_4H,                 # 14 ROSEWOODLC2D_RHO_TI_501.42_SD7_19-Jul-2016
         # },
      # 'H_25AS2M3' : HWY_TI7551_25AS2M3_5400,
      # 'H_25RW3'      : {
         # 'ATTRIBUTE' : 'numPhysHds',
         # 'DEFAULT'   : 2,
         # 2           : HWY_TI7551_25RW3E_5400,                 # 4/2/2015 #32
         # 4           : HWY_TI7551_25RW3E_5400,                 # 4/2/2015 #32
      # },
      # 'H_25RW3E'     : {
         # 'ATTRIBUTE' : 'numPhysHds',
         # 'DEFAULT'   : 2,
         # 2           : {
            # 'ATTRIBUTE' : 'HSA_WAFER_CODE',
            # 'DEFAULT'   : '5A3J2',
            # '4A4C5'     : HWY_TI7551_25RW3E_5400,              # 4/2/2015 #32
            # '5A2HH'     : HWY_TI7551_25RW3E_5A2HH_5400,        # 63 ROSEWOOD71D_HWY_25RW3E_TI_0XC200_0X1_5A2HH_2
            # '4C430'     : HWY_TI7551_25RW3E_4C430_5400,        # 65 ROSEWOOD71D_HWY_25RW3E_TI_0XC200_0X1_4C430_2
            # '5A3J2'     : HWY_TI7551_25RW3E_5A3J2_5400,        # 1-Oct-2015 #73
         # },
         # 4           : {
            # 'ATTRIBUTE' : 'HSA_WAFER_CODE',
            # 'DEFAULT'   : '5A99G',
            # '4C6JH'     : HWY_TI7551_25RW3E_4C6JH_5400_4H,     # 45
            # '4A60B'     : HWY_TI7551_25RW3E_4A60B_5400_4H,     # 43
            # '5A2HH'     : HWY_TI7551_25RW3E_5A2HH_5400_4H,     # 66
            # '5A3J2'     : HWY_TI7551_25RW3E_5A3J2_5400_4H,     # 71 RW72D_HWY_TI_25RW3E_5A3J2_4H_22-Sep-2015
            # '5A2HG'     : HWY_TI7551_25RW3E_5A2HG_5400_4H,     # 79
            # '5A5J0'     : HWY_TI7551_25RW3E_5A5J0_5400_4H,     # 81
            # '5A99G'     : HWY_TI7551_25RW3E_5A99G_5400_4H,     # 82
            # '5A9BJ'     : HWY_TI7551_25RW3E_5A99G_5400_4H,     # copy 5A99G
         # },
      # },
      # '25RW3E'       : {
         # 'ATTRIBUTE' : 'numPhysHds',
         # 'DEFAULT'   : 2,
         # 2           : {
            # 'ATTRIBUTE' : 'HSA_WAFER_CODE',
            # 'DEFAULT'   : '5F057',
            # '5F057'     : TDK_TI7551_25RW3E_5F608_5400,       # 97 RW71D_TDK_TI_25RW3E_5F608_2H_22-Dec-2015
         # },
         # 4           : {
            # 'ATTRIBUTE' : 'HSA_WAFER_CODE',
            # 'DEFAULT'   : '5F816',
            # '5F608'    : TDK_TI7551_25RW3E_5F608_5400_4H, #95
            # '5F816'    : TDK_TI7551_25RW3E_5F608_5400_4H, #95
         # },
      # },	  
      # '25AS2M3'   : TDK_TI7550_25AS2M2_5400,
   # },
   # # HMAR Related StarWood
   # # ==================== LSI preamp ====================
   # 'LSI5235':{
      # 'ATTRIBUTE' : 'AABType',
      # 'DEFAULT'   : '501.11',
      # '501.11'    : {
            # 'ATTRIBUTE' : 'HSA_WAFER_CODE',  
            # 'DEFAULT'   : '5W',
            # '5W'       : RHO_LSI5235_5W_5400,          
            # 'BZ7'      : RHO_LSI5235_Z7_5400_V8,    
            # 'AL1'      : RHO_LSI5235_AL1_5400_V9, 

      # },
   # },
# }
