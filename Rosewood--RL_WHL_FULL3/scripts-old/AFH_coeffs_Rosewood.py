#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Test Parameters for Extreme3
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/06/23 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Amazon/AFH_coeffs_Rosewood.py $
# $Revision: #2 $
# $DateTime: 2016/06/23 23:53:52 $
# $Author: chiliang.woo $perp
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Amazon/AFH_coeffs_Rosewood.py#2 $
# Level: 1
#---------------------------------------------------------------------------------------------------------#

from Constants import *
from Test_Switches import testSwitch

PRE_AMP_HEATER_MODE = 'LO_POWER'
triseValuesDefaultTI  = [ 3 ] * 180
triseValuesDefaultLSI = [ 2 ] * 180
ovsRiseTimeValuesTI = ovsRiseTimeValuesLSI  = [ 0 ] * 180

# ================================================================================================
#   HWY coefficients
# ================================================================================================
HWY_LSI5231_25AS2M3_5400 = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00456627, -0.00009229, 0.00000025, 0.00710104, -0.00000011, -0.00001844, 0.81839960, -0.00009863, -0.00234897, 2.41991300, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00693462, 0.00826708, -0.00002407, -0.00010411, 0.00000045, 0.00000024, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00032609, 0.00000323, -0.00000001, 0, 0, 0, -0.00000175, -0.00000002, 0, 0.00000262, 0.00002187, -0.00000005, 0, -0.00000008, -0.00000066, -0.00001524, 0.00000009, 0, -0.00000002, 0.00000056, 0.00000017, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.06,0,0],
   'gammaWriter'        : [1.11,0,0],
   'gammaReaderHeater'  : [1.000,0,0],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
}

TDK_LSI5231_25AS2M3_5400 = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00289071, -0.00012090, 0.00000031, 0.00901420, -0.00000047, -0.00003433, 1.07364806, -0.00011874, -0.00504226, 0.04720153, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00332825, 0.00857982, -0.00002769, -0.00008586, 0.00000017, 0.00000019, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[-0.00034373, 0.00002510, -0.00000007, 0, 0, 0, 0.00007491, -0.00000009, 0, 0.00000824, 0.00007258, -0.00000009, 0, 0.00000014, -0.00000137, 0.00005946, -0.00000003, 0, -0.00000006, -0.00000082, -0.00000078, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.05,0,0],
   'gammaWriter'        : [1.22,0,0],
   'gammaReaderHeater'  : [1.000,0,0],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
}

HWY_TI7550_25AS2M3_5400 = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00248105, -0.00006960, 0.00000021, 0.00701449, -0.00000003, -0.00001610, 1.03305148, -0.00015667, -0.00350670, 0.15345815, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00494605, 0.00774592, -0.00001840, -0.00007570, 0.00000014, 0.00000022, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00091400, 0.00000429, -0.00000001, 0, 0, 0, -0.00000981, -0.00000004, 0, 0.00000305, -0.00000583, 0.00000001, 0, 0.00000015, -0.00000059, -0.00000900, -0.00000004, 0, 0.00000019, 0.00000290, 0.00000027, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.06,0,0],
   'gammaWriter'        : [1.11,0,0],
   'gammaReaderHeater'  : [1.000,0,0],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultTI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesTI,
}

HWY_TI7551_25AS2M3_5400 = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00031333, -0.00003023, 0.00000011, 0.00714812, -0.00000064, -0.00001629, 0.93147172, -0.00003960, -0.00415844, 1.43486143, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[-0.00307928, 0.00824126, -0.00002194, -0.00002346, -0.00000024, 0.00000009, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00029534, 0.00001417, -0.00000003, 0, 0, 0, -0.00003804, -0.00000003, 0, 0.00000357, 0.00005280, -0.00000007, 0, 0.00000003, -0.00000099, 0.00006801, -0.00000013, 0, 0.00000003, -0.00000048, -0.00000084, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.06,0,0],
   'gammaWriter'        : [1.11,0,0],
   'gammaReaderHeater'  : [1.000,0,0],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultTI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesTI,
}

HWY_TI7551_25RW3E_5400 = { # 4/2/2015 #32
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00243672, -0.00005611, 0.00000014, 0.00771494, -0.00000124, -0.00002000, 1.03371066, -0.00015594, -0.00495948, 0.97817195, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00148257, 0.00881565, -0.00002640, -0.00004970, -0.00000081, 0.00000011, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[-0.00068344, 0.00001485, -0.00000003, 0, 0, 0, -0.00001094, -0.00000003, 0, 0.00000269, 0.00003049, -0.00000004, 0, 0.00000001, -0.00000044, 0.00003911, -0.00000009, 0, 0.00000004, -0.00000044, -0.00000037, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.06, 0, 0],
   'gammaWriter'        : [1.11, 0, 0],
   'gammaReaderHeater'  : [1.00, 0, 0],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultTI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesTI,
}

HWY_TI7551_25RW3E_5A2HH_5400 = { # 8/28/2015 #63 ROSEWOOD71D_HWY_25RW3E_TI_0XC200_0X1_5A2HH_2
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00417100, -0.00003443, 0.00000007, 0.00760476, -0.00000162, -0.00001794, 1.09381208, -0.00017339, -0.00500484, -0.27024045, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00126650, 0.00869897, -0.00002407, -0.00004451, -0.00000124, 0.00000012, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00023626, 0.00003281, -0.00000009, 0, 0, 0, -0.00002427, -0.00000005, 0, 0.00000381, 0.00001672, -0.00000005, 0, 0.00000011, -0.00000009, 0.00001405, -0.00000004, 0, 0.00000001, 0.00000005, 0.00000012, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.05999994, 0.00000000, 0.00000000, ],
   'gammaWriter'        : [1.11000001, 0.00000000, 0.00000000, ],
   'gammaReaderHeater'  : [1.00000000, 0.00000000, 0.00000000, ],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultTI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesTI,
   'CoeffTrackingNo'    : 'RW1HT063',
}

HWY_TI7551_25RW3E_4C430_5400 = { # 9-Sep-2015 #65 ROSEWOOD71D_HWY_25RW3E_TI_0XC200_0X1_4C430_2
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00294189, -0.00005159, 0.00000013, 0.00747849, -0.00000120, -0.00001911, 1.03771864, -0.00016903, -0.00502404, 0.59484513, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00103341, 0.00849631, -0.00002455, -0.00004478, -0.00000083, 0.00000011, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[-0.00087947, 0.00001956, -0.00000005, 0, 0, 0, -0.00000238, -0.00000004, 0, 0.00000357, 0.00004075, -0.00000010, 0, 0.00000006, -0.00000031, 0.00003999, -0.00000007, 0, 0.00000009, 0.00000017, -0.00000057, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.05999994, 0.00000000, 0.00000000, ],
   'gammaWriter'        : [1.11000001, 0.00000000, 0.00000000, ],
   'gammaReaderHeater'  : [1.00000000, 0.00000000, 0.00000000, ],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultTI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesTI,
   'CoeffTrackingNo'    : 'RW1HT065',
}

HWY_TI7551_25RW3E_5A3J2_5400 = { # 1-Oct-2015 #73 ROSEWOOD71D_HWY_25RW3E_TI_0XC200_0X1_5A3J2_2
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00130198, -0.00003015, 0.00000009, 0.00756597, -0.00000163, -0.00001675, 1.00384432, -0.00010713, -0.00426467, 0.77042261, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00186842, 0.00855914, -0.00002230, -0.00004448, -0.00000120, 0.00000012, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00121036, -0.00000520, 0.00000002, 0, 0, 0, 0.00001006, -0.00000011, 0, 0.00000351, -0.00000734, -0.00000001, 0, 0.00000002, -0.00000008, -0.00000870, -0.00000004, 0, 0.00000014, 0.00000095, 0.00000012, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.05999994, 0.00000000, 0.00000000, ],
   'gammaWriter'        : [1.11000001, 0.00000000, 0.00000000, ],
   'gammaReaderHeater'  : [1.00000000, 0.00000000, 0.00000000, ],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultTI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesTI,
   'CoeffTrackingNo'    : 'RW1HT073',
}

HWY_TI7551_25RW3E_4A60B_5400_4H = { #43
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00042285, -0.00004869, 0.00000014, 0.00752744, -0.00000133, -0.00001647, 1.05582203, -0.00018006, -0.00442447, 0.08315845, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[-0.00035763, 0.00872869, -0.00002387, -0.00004835, -0.00000094, 0.00000012, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[-0.00051783, 0.00001489, -0.00000003, 0, 0, 0, -0.00000741, -0.00000004, 0, 0.00000299, 0.00003969, -0.00000007, 0, 0.00000008, -0.00000061, 0.00004175, -0.00000008, 0, 0.00000006, -0.00000070, -0.00000039, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.05999994, 0.00000000, 0.00000000],
   'gammaWriter'        : [1.11000001, 0.00000000, 0.00000000],
   'gammaReaderHeater'  : [1.00000000, 0.00000000, 0.00000000],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultTI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesTI,
}

HWY_TI7551_25RW3E_4C6JH_5400_4H = { #45
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[-0.00039100, -0.00004905, 0.00000013, 0.00761414, -0.00000120, -0.00001806, 1.03647623, -0.00013893, -0.00440392, 0.57278042, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[-0.00121189, 0.00877664, -0.00002495, -0.00005157, -0.00000070, 0.00000012, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[-0.00056172, 0.00001379, -0.00000003, 0, 0, 0, -0.00000130, -0.00000004, 0, 0.00000278, 0.00005837, -0.00000009, 0, 0.00000004, -0.00000069, 0.00005617, -0.00000011, 0, 0.00000003, -0.00000105, -0.00000057, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.05999994, 0.00000000, 0.00000000],
   'gammaWriter'        : [1.11000001, 0.00000000, 0.00000000],
   'gammaReaderHeater'  : [1.00000000, 0.00000000, 0.00000000],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultTI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesTI,
}

TDK_TI7550_25AS2M2_5400 = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[-0.001701880,-0.000075100,0.000000253,0.008919047,-0.000000559,-0.000024700,1.133530736,-0.000187962,-0.004869343,-0.213804842,AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.004259570,0.008473660,-0.000020900,-0.000057500,-0.000000233,0.000000172,AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.002203686,0.000026200,-0.000000096,0,0,0,-0.000053500,-0.000000025,0,0.000010400,-0.000206645,-0.000000084,0,0.000002020,0.000004970,-0.000213989,0.000000360,0,0.000001590,0.000011600,0.000002610,AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.05,0,0],
   'gammaWriter'        : [1.22,0,0],
   'gammaReaderHeater'  : [1.000,0,0],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultTI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesTI,
}

TDK_TI7551_25RW3E_5F608_5400_4H = { #95
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00042997, -0.00004171, 0.00000009, 0.00622856, -0.00000071, -0.00001240, 1.03089916, -0.00003495, -0.00345645, 0.18263697, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00202902, 0.00731690, -0.00001911, -0.00005740, -0.00000050, 0.00000012, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00114846, -0.00000732, 0.00000002, 0, 0, 0, 0.00001768, -0.00000012, 0, 0.00000458, -0.00000231, -0.00000002, 0, 0.00000009, -0.00000007, -0.00002011, -0.00000001, 0, 0.00000017, 0.00000098, 0.00000036, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.12000000, 0.00000000, 0.00000000, ],
   'gammaWriter'        : [1.14000000, 0.00000000, 0.00000000, ],
   'gammaReaderHeater'  : [0.96000000, 0.00000000, 0.00000000, ],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultTI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesTI,
   'CoeffTrackingNo'    : 'RW2TT095',
}

HWY_LSI5830_25AS2M3_5400 = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00158903, -0.00006828, 0.00000020, 0.00727914, -0.00000056, -0.00001559, 0.99821645, -0.00009402, -0.00332211, 1.04298513, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00139342, 0.00847189, -0.00002211, -0.00005813, -0.00000018, 0.00000016, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00126209, 0.00001717, -0.00000004, 0, 0, 0, -0.00003917, 0.00000000, 0, 0.00000285, 0.00002812, -0.00000011, 0, 0.00000007, 0.00000001, 0.00004592, -0.00000012, 0, 0.00000010, -0.00000052, -0.00000055, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.06,0,0],
   'gammaWriter'        : [1.11,0,0],
   'gammaReaderHeater'  : [1.000,0,0],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
}

HWY_LSI5830_25AS2M3_5400_4H = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00127943, -0.00006310, 0.00000016, 0.00738524, -0.00000046, -0.00001771, 0.95358094, -0.00011985, -0.00381322, 1.72405064, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00331174, 0.00857236, -0.00002355, -0.00007543, -0.00000015, 0.00000018, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00121589, 0.00001778, -0.00000002, 0, 0, 0, 0.00000843, -0.00000005, 0, 0.00000256, 0.00005175, -0.00000009, 0, 0.00000005, -0.00000057, 0.00004535, -0.00000007, 0, 0.00000000, -0.00000072, -0.00000056, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.06,0,0],
   'gammaWriter'        : [1.11,0,0],
   'gammaReaderHeater'  : [1.000,0,0],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
}

HWY_LSI5830_25AS2M3_4A49H_5400_4H = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00232220, -0.00008724, 0.00000024, 0.00764597, -0.00000055, -0.00001948, 1.11411654, -0.00019607, -0.00484797, -0.20004596, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00099221, 0.00882982, -0.00002589, -0.00003431, -0.00000009, 0.00000008, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00136048, 0.00003844, -0.00000011, 0, 0, 0, -0.00003020, -0.00000005, 0, 0.00000283, 0.00004996, -0.00000013, 0, 0.00000005, -0.00000052, 0.00002596, -0.00000013, 0, 0.00000020, -0.00000024, -0.00000027, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.06,0,0],
   'gammaWriter'        : [1.11,0,0],
   'gammaReaderHeater'  : [1.000,0,0],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
}

HWY_LSI5830_25AS2M3_4A4C5_5400_4H = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[-0.00140672, -0.00004675, 0.00000014, 0.00733597, -0.00000075, -0.00001958, 1.11960456, -0.00023158, -0.00420265, -0.27919398, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00119667, 0.00842798, -0.00002511, -0.00004461, -0.00000035, 0.00000010, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00124801, 0.00001270, -0.00000003, 0, 0, 0, -0.00004700, 0.00000001, 0, 0.00000270, 0.00003528, -0.00000010, 0, 0.00000011, 0.00000024, 0.00007545, -0.00000009, 0, 0.00000015, -0.00000120, -0.00000131, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.06,0,0],
   'gammaWriter'        : [1.11,0,0],
   'gammaReaderHeater'  : [1.000,0,0],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
}

HWY_LSI5830_25RW3_5400 = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[-0.00043051, -0.00005288, 0.00000015, 0.00741986, -0.00000132, -0.00001802, 1.10970906, -0.00019522, -0.00388633, -0.87366526, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00172541, 0.00858279, -0.00002392, -0.00004824, -0.00000093, 0.00000011, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00159071, 0.00001592, -0.00000004, 0, 0, 0, -0.00002582, -0.00000006, 0, 0.00000284, 0.00003737, 0.00000002, 0, -0.00000004, -0.00000107, 0.00000113, -0.00000005, 0, 0.00000026, -0.00000044, -0.00000003, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.06,0,0],
   'gammaWriter'        : [1.11,0,0],
   'gammaReaderHeater'  : [1.000,0,0],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
}

HWY_LSI5830_25RW3E_5A2HH_5400 = { # 12-Aug-2015 #52
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00370945, -0.00007020, 0.00000017, 0.00771002, -0.00000139, -0.00001971, 1.10278993, -0.00023157, -0.00434671, -0.00739726, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[-0.00013586, 0.00888329, -0.00002754, -0.00004557, -0.00000106, 0.00000012, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[-0.00152534, 0.00002436, -0.00000005, 0, 0, 0, -0.00001433, -0.00000001, 0, 0.00000291, 0.00005841, -0.00000011, 0, 0.00000021, -0.00000074, 0.00004258, -0.00000008, 0, 0.00000008, -0.00000044, -0.00000038, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.05999994, 0.00000000, 0.00000000],
   'gammaWriter'        : [1.11000001, 0.00000000, 0.00000000],
   'gammaReaderHeater'  : [1.00000000, 0.00000000, 0.00000000],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
}

HWY_LSI5830_25RW3E_5A3J2_5400 = { # 64 RW71D_HWY_LSI_25RW3E_5A3J2_2H_07-Sep-2015
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00185323, -0.00006799, 0.00000016, 0.00762950, -0.00000119, -0.00001853, 1.14261396, -0.00021384, -0.00384800, -1.18742336, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00066167, 0.00884623, -0.00002728, -0.00006312, -0.00000071, 0.00000017, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[-0.00096401, 0.00001728, -0.00000003, 0, 0, 0, -0.00002606, -0.00000002, 0, 0.00000289, 0.00002946, -0.00000009, 0, 0.00000010, -0.00000009, 0.00003629, -0.00000009, 0, 0.00000014, -0.00000008, -0.00000042, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.05999994, 0.00000000, 0.00000000],
   'gammaWriter'        : [1.11000001, 0.00000000, 0.00000000],
   'gammaReaderHeater'  : [1.00000000, 0.00000000, 0.00000000],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
   'CoeffTrackingNo'    : 'RW1HL064',
}

HWY_LSI5830_25RW3E_5ABG5_5400 = { # 77 RW71D_HWY_LSI_25RW3E_5ABG5_2H_13-Oct-2015
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00192183, -0.00004443, 0.00000012, 0.00788454, -0.00000149, -0.00001986, 1.05515574, -0.00007696, -0.00384156, 0.16322834, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00032295, 0.00914599, -0.00002831, -0.00004992, -0.00000106, 0.00000013, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00149284, -0.00000428, 0.00000001, 0, 0, 0, 0.00000689, -0.00000009, 0, 0.00000282, -0.00001524, -0.00000002, 0, 0.00000016, 0.00000051, -0.00000672, 0.00000001, 0, 0.00000002, 0.00000038, 0.00000016, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.05999994, 0.00000000, 0.00000000],
   'gammaWriter'        : [1.11000001, 0.00000000, 0.00000000],
   'gammaReaderHeater'  : [1.00000000, 0.00000000, 0.00000000],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
   'CoeffTrackingNo'    : 'RW1HL077',
}

HWY_LSI5830_25RW3E_5A5J0_5400 = { # 78 RW71D_HWY_LSI_25RW3E_5A5J0_2H_22-Oct-2015
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00255816, -0.00005937, 0.00000015, 0.00766849, -0.00000135, -0.00001872, 1.00625409, -0.00000383, -0.00347955, 0.67482214, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00115132, 0.00895287, -0.00002762, -0.00005315, -0.00000096, 0.00000014, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00093552, 0.00000440, -0.00000001, 0, 0, 0, -0.00000649, -0.00000008, 0, 0.00000295, 0.00001094, -0.00000006, 0, 0.00000016, -0.00000011, -0.00001704, -0.00000002, 0, 0.00000001, 0.00000053, 0.00000055, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.05999994, 0.00000000, 0.00000000],
   'gammaWriter'        : [1.11000001, 0.00000000, 0.00000000],
   'gammaReaderHeater'  : [1.00000000, 0.00000000, 0.00000000],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
   'CoeffTrackingNo'    : 'RW1HL078',
}

HWY_LSI5830_25RW3E_4C677_5400 = { # 91 RW71D_HWY_LSI_25RW3E_4C677_2H_20-Nov-2015
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00162835, -0.00004783, 0.00000013, 0.00764218, -0.00000158, -0.00001824, 1.07444846, -0.00012965, -0.00446587, -0.02621777, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[-0.00041449, 0.00880151, -0.00002609, -0.00003691, -0.00000119, 0.00000011, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00156086, -0.00000832, 0.00000003, 0, 0, 0, -0.00000042, -0.00000008, 0, 0.00000299, -0.00000652, -0.00000002, 0, 0.00000015, 0.00000006, -0.00000761, 0.00000001, 0, 0.00000008, 0.00000061, -0.00000018, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.05999994, 0.00000000, 0.00000000],
   'gammaWriter'        : [1.11000001, 0.00000000, 0.00000000],
   'gammaReaderHeater'  : [1.00000000, 0.00000000, 0.00000000],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
   'CoeffTrackingNo'    : 'RW1HL091',
}

HWY_LSI5830_25RW3_5400_4H = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00129111, -0.00008309, 0.00000022, 0.00781589, -0.00000106, -0.00002313, 1.00026352, -0.00020969, -0.00426668, 1.04283562, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00247917, 0.00885847, -0.00002886, -0.00003885, -0.00000085, 0.00000007, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00097419, 0.00001524, -0.00000004, 0, 0, 0, -0.00001339, -0.00000002, 0, 0.00000282, 0.00008324, -0.00000013, 0, 0.00000014, -0.00000109, 0.00005777, -0.00000007, 0, 0.00000009, -0.00000145, -0.00000060, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.05999994, 0.00000000, 0.00000000],
   'gammaWriter'        : [1.11000001, 0.00000000, 0.00000000],
   'gammaReaderHeater'  : [1.00000000, 0.00000000, 0.00000000],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
}

HWY_LSI5830_25RW3E_4A4C5_5400_4H = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00051241, -0.00003071, 0.00000010, 0.00754240, -0.00000180, -0.00001677, 1.02088226, -0.00027139, -0.00380126, 1.53121635, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00004255, 0.00861790, -0.00002208, -0.00001492, -0.00000148, 0.00000005, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[-0.00009587, 0.00002155, -0.00000005, 0, 0, 0, -0.00001872, -0.00000002, 0, 0.00000268, 0.00006116, -0.00000010, 0, 0.00000008, -0.00000100, 0.00007956, -0.00000008, 0, -0.00000003, -0.00000074, -0.00000142, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.05999994, 0.00000000, 0.00000000],
   'gammaWriter'        : [1.11000001, 0.00000000, 0.00000000],
   'gammaReaderHeater'  : [1.00000000, 0.00000000, 0.00000000],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
}

HWY_LSI5830_25RW3E_5A2HH_5400_4H = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00382439, -0.00007144, 0.00000018, 0.00772319, -0.00000138, -0.00001963, 1.10526455, -0.00020031, -0.00444896, -0.36907039, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00031143, 0.00884770, -0.00002649, -0.00005124, -0.00000114, 0.00000014, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[-0.00061580, 0.00002012, -0.00000005, 0, 0, 0, -0.00000879, -0.00000003, 0, 0.00000286, 0.00003531, -0.00000007, 0, 0.00000017, -0.00000028, 0.00002912, -0.00000006, 0, 0.00000011, -0.00000039, -0.00000014, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.05999994, 0.00000000, 0.00000000],
   'gammaWriter'        : [1.11000001, 0.00000000, 0.00000000],
   'gammaReaderHeater'  : [1.00000000, 0.00000000, 0.00000000],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
   'CoeffTrackingNo'    : 'RW2HL059',
}

HWY_LSI5830_25RW3E_5A3J2_5400_4H = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00350267, -0.00007232, 0.00000019, 0.00762331, -0.00000126, -0.00001798, 1.06851535, -0.00009524, -0.00415607, -0.08956262, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00082187, 0.00878237, -0.00002550, -0.00006246, -0.00000094, 0.00000017, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[-0.00023596, 0.00000878, -0.00000001, 0, 0, 0, -0.00001295, -0.00000004, 0, 0.00000279, 0.00003227, -0.00000010, 0, 0.00000019, -0.00000018, 0.00003723, -0.00000008, 0, 0.00000010, -0.00000031, -0.00000045, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.05999994, 0.00000000, 0.00000000],
   'gammaWriter'        : [1.11000001, 0.00000000, 0.00000000],
   'gammaReaderHeater'  : [1.00000000, 0.00000000, 0.00000000],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
   'CoeffTrackingNo'    : 'RW2HL067',
}

HWY_LSI5830_25RW3E_5A2HG_5400_4H = { #74
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00187585, -0.00004137, 0.00000011, 0.00762817, -0.00000145, -0.00001959, 1.07429474, -0.00000366, -0.00391766, -0.81556401, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00045503, 0.00873871, -0.00002567, -0.00004672, -0.00000129, 0.00000012, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00051721, 0.00001084, -0.00000003, 0, 0, 0, -0.00001371, -0.00000011, 0, 0.00000282, 0.00001006, -0.00000003, 0, 0.00000021, -0.00000043, 0.00000029, -0.00000004, 0, 0.00000012, 0.00000054, -0.00000005, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.05999994, 0.00000000, 0.00000000],
   'gammaWriter'        : [1.11000001, 0.00000000, 0.00000000],
   'gammaReaderHeater'  : [1.00000000, 0.00000000, 0.00000000],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
   'CoeffTrackingNo'    : 'RW2HL074',
}

HWY_LSI5830_25RW3E_5A5J0_5400_4H = { #80
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00024481, -0.00003037, 0.00000007, 0.00770940, -0.00000125, -0.00002086, 1.06996537, -0.00007605, -0.00439426, -0.29247953, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00066411, 0.00894039, -0.00003077, -0.00004825, -0.00000092, 0.00000012, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00035404, 0.00000711, -0.00000001, 0, 0, 0, 0.00000226, -0.00000008, 0, 0.00000283, 0.00000437, -0.00000002, 0, 0.00000010, -0.00000006, 0.00000748, -0.00000003, 0, 0.00000007, 0.00000036, -0.00000015, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.05999994, 0.00000000, 0.00000000],
   'gammaWriter'        : [1.11000001, 0.00000000, 0.00000000],
   'gammaReaderHeater'  : [1.00000000, 0.00000000, 0.00000000],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
   'CoeffTrackingNo'    : 'RW2HL080',
}

HWY_LSI5830_25RW3E_5A99G_5400_4H = {  #RW72D_HWY_LSI_25RW3E_5A99G_09-Nov-2015
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00107087, -0.00003920, 0.00000010, 0.00772857, -0.00000131, -0.00002107, 1.08473310, -0.00008603, -0.00464897, -0.44490779, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00022587, 0.00884388, -0.00002887, -0.00004573, -0.00000090, 0.00000011, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00050377, 0.00000347, -0.00000001, 0, 0, 0, -0.00001017, -0.00000007, 0, 0.00000282, -0.00000918, -0.00000001, 0, 0.00000009, 0.00000020, -0.00001080, 0.00000000, 0, 0.00000011, 0.00000057, -0.00000001, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.05999994, 0.00000000, 0.00000000],
   'gammaWriter'        : [1.11000001, 0.00000000, 0.00000000],
   'gammaReaderHeater'  : [1.00000000, 0.00000000, 0.00000000],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
   'CoeffTrackingNo'    : 'RW2HL085',
}

HWY_TI7551_25RW3E_5A2HH_5400_4H = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00058435, -0.00006201, 0.00000017, 0.00754083, -0.00000149, -0.00001667, 1.07037647, -0.00014368, -0.00460046, -0.09783779, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[-0.00000627, 0.00873086, -0.00002406, -0.00005843, -0.00000119, 0.00000015, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[-0.00085637, 0.00001952, -0.00000004, 0, 0, 0, -0.00000736, -0.00000006, 0, 0.00000364, 0.00003209, -0.00000008, 0, 0.00000006, -0.00000030, 0.00002505, -0.00000005, 0, 0.00000019, 0.00000012, -0.00000045, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.05999994, 0.00000000, 0.00000000],
   'gammaWriter'        : [1.11000001, 0.00000000, 0.00000000],
   'gammaReaderHeater'  : [1.00000000, 0.00000000, 0.00000000],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultTI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesTI,
   'CoeffTrackingNo'    : 'RW2HT066',
}

HWY_TI7551_25RW3E_5A3J2_5400_4H = { # 71 RW72D_HWY_TI_25RW3E_5A3J2_4H_22-Sep-2015
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00117855, -0.00005532, 0.00000015, 0.00750578, -0.00000151, -0.00001715, 1.04977013, -0.00018011, -0.00461713, 0.31483117, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[-0.00022376, 0.00856465, -0.00002262, -0.00004912, -0.00000121, 0.00000013, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[-0.00068138, 0.00001883, -0.00000004, 0, 0, 0, -0.00000478, -0.00000005, 0, 0.00000353, 0.00003298, -0.00000009, 0, 0.00000005, -0.00000020, 0.00003282, -0.00000007, 0, 0.00000009, 0.00000006, -0.00000031, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.05999994, 0.00000000, 0.00000000, ],
   'gammaWriter'        : [1.11000001, 0.00000000, 0.00000000, ],
   'gammaReaderHeater'  : [1.00000000, 0.00000000, 0.00000000, ],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultTI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesTI,
   'CoeffTrackingNo'    : 'RW2HT071',
}

HWY_TI7551_25RW3E_5A2HG_5400_4H = { # 79
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00051000, -0.00002304, 0.00000006, 0.00753372, -0.00000159, -0.00001823, 1.03114934, -0.00007640, -0.00454111, 0.29158429, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00159009, 0.00877195, -0.00002610, -0.00004603, -0.00000130, 0.00000011, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00122228, -0.00000499, 0.00000002, 0, 0, 0, 0.00001855, -0.00000014, 0, 0.00000349, -0.00000431, -0.00000002, 0, 0.00000005, 0.00000008, -0.00002641, -0.00000002, 0, 0.00000012, 0.00000090, 0.00000050, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.05999994, 0.00000000, 0.00000000, ],
   'gammaWriter'        : [1.11000001, 0.00000000, 0.00000000, ],
   'gammaReaderHeater'  : [1.00000000, 0.00000000, 0.00000000, ],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultTI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesTI,
   'CoeffTrackingNo'    : 'RW2HT079',
}

HWY_TI7551_25RW3E_5A5J0_5400_4H = { # 81
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00130787, -0.00003407, 0.00000009, 0.00739189, -0.00000126, -0.00001793, 1.01569661, -0.00003660, -0.00466203, 0.41072492, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00178876, 0.00864729, -0.00002687, -0.00004994, -0.00000091, 0.00000013, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00100674, -0.00000393, 0.00000002, 0, 0, 0, 0.00001079, -0.00000012, 0, 0.00000357, -0.00001777, -0.00000001, 0, 0.00000006, 0.00000040, -0.00000875, -0.00000004, 0, 0.00000013, 0.00000087, 0.00000021, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.05999994, 0.00000000, 0.00000000, ],
   'gammaWriter'        : [1.11000001, 0.00000000, 0.00000000, ],
   'gammaReaderHeater'  : [1.00000000, 0.00000000, 0.00000000, ],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultTI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesTI,
   'CoeffTrackingNo'    : 'RW2HT081',
}

HWY_TI7551_25RW3E_5A99G_5400_4H = { # 82
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[-0.00056187, -0.00003049, 0.00000008, 0.00739436, -0.00000131, -0.00001744, 1.02406015, -0.00002734, -0.00478752, 0.33901222, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00044696, 0.00856908, -0.00002490, -0.00004307, -0.00000099, 0.00000011, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00097149, -0.00000062, 0.00000001, 0, 0, 0, 0.00001501, -0.00000014, 0, 0.00000356, -0.00002200, 0.00000000, 0, 0.00000010, 0.00000041, -0.00000887, -0.00000002, 0, 0.00000021, 0.00000060, 0.00000007, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.05999994, 0.00000000, 0.00000000, ],
   'gammaWriter'        : [1.11000001, 0.00000000, 0.00000000, ],
   'gammaReaderHeater'  : [1.00000000, 0.00000000, 0.00000000, ],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultTI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesTI,
   'CoeffTrackingNo'    : 'RW2HT082',
}

TDK_TI7551_25RW3E_5F608_5400 = { # 97 RW71D_TDK_TI_25RW3E_5F608_2H_22-Dec-2015
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00138717, -0.00004909, 0.00000012, 0.00650026, -0.00000075, -0.00001355, 1.02916515, -0.00001851, -0.00415699, 0.25708328, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00092505, 0.00746206, -0.00002015, -0.00005777, -0.00000037, 0.00000011, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00016383, 0.00002016, -0.00000003, 0, 0, 0, 0.00001933, -0.00000011, 0, 0.00000483, -0.00001502, -0.00000003, 0, 0.00000008, 0.00000048, -0.00001224, -0.00000005, 0, 0.00000019, 0.00000072, 0.00000042, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.12000000, 0.00000000, 0.00000000, ],
   'gammaWriter'        : [1.14000000, 0.00000000, 0.00000000, ],
   'gammaReaderHeater'  : [0.96000000, 0.00000000, 0.00000000, ],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultTI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesTI,
   'CoeffTrackingNo'    : 'RW1TT097',
}

HWY_LSI5830_25RW3E_4C6JH_5400_4H = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[-0.00091127, -0.00003052, 0.00000008, 0.00790056, -0.00000130, -0.00001921, 1.02401856, -0.00017164, -0.00364196, 1.28117818, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00041101, 0.00914863, -0.00002745, -0.00004178, -0.00000087, 0.00000009, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[-0.00026561, 0.00000903, -0.00000001, 0, 0, 0, -0.00001197, -0.00000001, 0, 0.00000218, 0.00004910, -0.00000013, 0, 0.00000005, -0.00000020, 0.00005457, -0.00000010, 0, 0.00000002, -0.00000066, -0.00000069, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.05999994, 0.00000000, 0.00000000],
   'gammaWriter'        : [1.11000001, 0.00000000, 0.00000000],
   'gammaReaderHeater'  : [1.00000000, 0.00000000, 0.00000000],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
}

TDK_LSI5830_25AS2M3_5400_4H = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00375815, -0.00008000, 0.00000021, 0.00679542, -0.00000048, -0.00001631, 1.03536569, -0.00003486, -0.00340256, 0.17352924, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00164920, 0.00717738, -0.00001781, -0.00005733, 0.00000002, 0.00000014, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00169280, 0.00000946, -0.00000001, 0, 0, 0, -0.00001009, -0.00000006, 0, 0.00000422, 0.00000169, -0.00000001, 0, 0.00000013, -0.00000009, 0.00004457, -0.00000015, 0, -0.00000002, -0.00000060, -0.00000014, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.05,0,0],
   'gammaWriter'        : [1.22,0,0],
   'gammaReaderHeater'  : [1.000,0,0],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
}

TDK_LSI5830_25RW3E_5F068_5400 = { # 8/24/2015 #62 ROSEWOOD71D_TDK_25RW3E_LSI_0X8200_0X2_5F068_2
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00317420, -0.00007754, 0.00000020, 0.00872386, -0.00000137, -0.00002988, 1.12212501, -0.00016247, -0.00544072, -0.25628586, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00080509, 0.00805847, -0.00002301, -0.00006413, -0.00000094, 0.00000017, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[-0.00105103, 0.00002822, -0.00000007, 0, 0, 0, 0.00000388, -0.00000012, 0, 0.00000885, 0.00000811, -0.00000007, 0, 0.00000042, 0.00000010, 0.00000531, -0.00000006, 0, 0.00000034, 0.00000091, -0.00000010, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.05000000, 0.00000000, 0.00000000, ],
   'gammaWriter'        : [1.22000000, 0.00000000, 0.00000000, ],
   'gammaReaderHeater'  : [1.00000000, 0.00000000, 0.00000000, ],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
   'CoeffTrackingNo'    : 'RW1TL062',
}

TDK_LSI5830_25RW3E_5F608_5400_4H = { #94
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00163615, -0.00003822, 0.00000008, 0.00632376, -0.00000087, -0.00001261, 1.06158419, -0.00006104, -0.00320193, -0.17720154, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00168119, 0.00738033, -0.00001992, -0.00005163, -0.00000046, 0.00000011, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00165512, -0.00000058, 0.00000000, 0, 0, 0, 0.00001279, -0.00000009, 0, 0.00000349, -0.00000973, -0.00000001, 0, 0.00000019, 0.00000009, -0.00001123, -0.00000001, 0, 0.00000014, 0.00000070, 0.00000011, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.12000000, 0.00000000, 0.00000000, ],
   'gammaWriter'        : [1.14000000, 0.00000000, 0.00000000, ],
   'gammaReaderHeater'  : [0.96000000, 0.00000000, 0.00000000, ],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
   'CoeffTrackingNo'    : 'RW2TL094',
}

TDK_LSI5830_25RW3E_5F608_5400 = { # 96 RW71D_TDK_LSI_25RW3E_5F608_2H_22-Dec-2015
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[-0.00008564, -0.00004431, 0.00000012, 0.00639946, -0.00000117, -0.00001286, 1.09737310, -0.00005529, -0.00353528, -0.59946758, AFH_Uniform_Track_Lbl],
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00070414, 0.00736984, -0.00001875, -0.00005605, -0.00000077, 0.00000015, AFH_Uniform_Track_Lbl],
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00071079, 0.00000379, -0.00000001, 0, 0, 0, -0.00001483, -0.00000009, 0, 0.00000372, 0.00002077, -0.00000005, 0, 0.00000017, -0.00000045, -0.00000521, -0.00000003, 0, 0.00000009, 0.00000041, 0.00000023, AFH_Uniform_Track_Lbl],
   },
   'gammaWriterHeater'  : [1.12000000, 0.00000000, 0.00000000, ],
   'gammaWriter'        : [1.14000000, 0.00000000, 0.00000000, ],
   'gammaReaderHeater'  : [0.96000000, 0.00000000, 0.00000000, ],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
   'CoeffTrackingNo'    : 'RW1TL096',
}

# ================================================================================================
#   RHO coefficients
# ================================================================================================
RHO_LSI5231_50111_5400 = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00075585, -0.00003395, 0.00000011, 0.00647591, 0.00000089, -0.00002686, 1.02275700, 0.00005203, -0.00818827, -0.33635053, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00346123, 0.00471363, -0.00001402, -0.00004653, 0.00000054, 0.00000015, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00385270, -0.00002084, 0.00000005, 0, 0, 0, 0.00003875, 0.00000010, 0, 0.00000554, 0.00000778, -0.00000010, 0, 0.00000016, 0.00000035, -0.00000002, -0.00000002, 0, -0.00000009, -0.00000029, 0.00000054, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.154853080, 0.000029580, -0.000000060],
   'gammaWriter'        : [1.209512300, 0.000022900, -0.000000100],
   'gammaReaderHeater'  : [1.000056562, 0.000000361, -0.000000002],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
}

RHO_LSI5830_50111_5400 = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00338430, -0.00006088, 0.00000018, 0.00655478, 0.00000091, -0.00001883, 0.96452165, 0.00003967, -0.00597654, 0.27278570, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00171286, 0.00488247, -0.00001119, -0.00004909, 0.00000094, 0.00000014, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00067274, -0.00001374, 0.00000005, 0, 0, 0, -0.00002107, -0.00000001, 0, 0.00000602, 0.00006479, -0.00000011, 0, -0.00000002, -0.00000133, 0.00004552, -0.00000006, 0, -0.00000019, -0.00000025, -0.00000052, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.154853080, 0.000029580, -0.000000060],
   'gammaWriter'        : [1.209512300, 0.000022900, -0.000000100],
   'gammaReaderHeater'  : [1.000056562, 0.000000361, -0.000000002],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
}

RHO_LSI5830_50111_5400_NU7 = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00176713, -0.00003704, 0.00000011, 0.00667959, 0.00000131, -0.00002877, 0.99575657, 0.00019309, -0.00811830, -0.03678855, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00384241, 0.00468618, -0.00001265, -0.00005761, 0.00000096, 0.00000016, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00160364, -0.00001695, 0.00000006, 0, 0, 0, -0.00002125, -0.00000001, 0, 0.00000470, 0.00002063, -0.00000005, 0, 0.00000000, -0.00000023, 0.00002327, -0.00000010, 0, -0.00000009, -0.00000009, 0.00000000, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.20409794,0.0000581,-0.00000007],
   'gammaWriter'        : [1.2869314,0.0000314,-0.0000001],
   'gammaReaderHeater'  : [1.00211529,-0.000024569,0.000000055],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
}

RHO_LSI5830_50111_5400_N2Q = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00204785, -0.00005177, 0.00000016, 0.00680313, 0.00000144, -0.00002885, 0.99919414, 0.00011679, -0.00724288, 0.02057763, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00509638, 0.00479112, -0.00001291, -0.00007723, 0.00000103, 0.00000021, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00319541, -0.00002656, 0.00000008, 0, 0, 0, -0.00000234, -0.00000001, 0, 0.00000470, 0.00001056, -0.00000004, 0, -0.00000004, 0.00000019, 0.00001504, -0.00000001, 0, 0.00000006, 0.00000001, -0.00000031, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.20409794,0.0000581,-0.00000007],
   'gammaWriter'        : [1.2869314,0.0000314,-0.0000001],
   'gammaReaderHeater'  : [1.00211529,-0.000024569,0.000000055],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
}

RHO_LSI5830_50111_N2Q_5400_4H = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00012459, -0.00004660, 0.00000015, 0.00699410, 0.00000133, -0.00002929, 1.01070898, 0.00014039, -0.00693884, -0.15318705, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00414959, 0.00484000, -0.00001223, -0.00007632, 0.00000089, 0.00000022, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00189467, -0.00001462, 0.00000005, 0, 0, 0, -0.00001015, -0.00000003, 0, 0.00000487, 0.00005051, -0.00000005, 0, -0.00000008, -0.00000060, 0.00004288, -0.00000009, 0, -0.00000005, -0.00000058, -0.00000033, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.20409794,0.0000581,-0.00000007],
   'gammaWriter'        : [1.2869314,0.0000314,-0.0000001],
   'gammaReaderHeater'  : [1.00211529,-0.000024569,0.000000055],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
}

RHO_LSI5830_50111_5400_4H = { #RW7 2D
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00419490, -0.00005987, 0.00000016, 0.00649073, 0.00000121, -0.00001594, 0.99822582, 0.00018362, -0.00618856, -0.21759497, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00823695, 0.00476572, -0.00000934, -0.00008499, 0.00000117, 0.00000020, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00202440, -0.00001458, 0.00000005, 0, 0, 0, -0.00001716, -0.00000004, 0, 0.00000611, 0.00003409, -0.00000006, 0, -0.00000009, -0.00000038, 0.00004177, -0.00000007, 0, 0.00000023, -0.00000015, -0.00000104, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.154853080, 0.000029580, -0.000000060],
   'gammaWriter'        : [1.209512300, 0.000022900, -0.000000100],
   'gammaReaderHeater'  : [1.000056562, 0.000000361, -0.000000002],
   'isDriveDualHeater'  : 1,
   'triseValues'       : triseValuesDefaultLSI,
   'ovsRiseTimeValues' : ovsRiseTimeValuesLSI,
}

RHO_TI7550_50111_5400 = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[-0.00077808, -0.00004040, 0.00000012, 0.00648047, 0.00000136, -0.00001690, 1.06593065, 0.00009310, -0.00573538, -0.44226294, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00541848, 0.00502767, -0.00001240, -0.00005890, 0.00000104, 0.00000019, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00280504, -0.00002500, 0.00000008, 0, 0, 0, 0.00000717, 0.00000007, 0, 0.00000779, -0.00003880, -0.00000005, 0, 0.00000100, 0.00000004, -0.00013789, -0.00000004, 0, 0.00000158, 0.00000490, 0.00000272, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.1545134,-0.0000079,0.00000005],
   'gammaWriter'        : [1.215774,0.0000448,-0.0000002],
   'gammaReaderHeater'  : [1.000820036,0.000000702,-0.000000002],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultTI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesTI,
}

RHO_TI7551_50114_5400 = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[-0.00017248, -0.00002268, 0.00000005, 0.00761484, 0.00000069, -0.00002649, 1.05008267, 0.00009553, -0.00526004, -0.16596348, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00256973, 0.00522429, -0.00001168, -0.00005100, 0.00000050, 0.00000013, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00173981, -0.00000670, 0.00000003, 0, 0, 0, -0.00007139, -0.00000002, 0, 0.00000757, 0.00004943, -0.00000003, 0, 0.00000000, -0.00000078, 0.00004658, -0.00000011, 0, 0.00000023, -0.00000025, -0.00000071, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.18666765,0.0003643,-0.00000101],
   'gammaWriter'        : [1.2829372,0.000032,0],
   'gammaReaderHeater'  : [1.000651974,-0.000002765,0.000000007],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultTI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesTI,
}

RHO_TI7551_50125_O2Q_5400 = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00544212, -0.00007009, 0.00000020, 0.00736670, -0.00000007, -0.00002090, 1.00217111, -0.00000472, -0.00529192, 0.27388629, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00429401, 0.00528329, -0.00001084, -0.00007878, 0.00000006, 0.00000021, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00024131, 0.00000262, -0.00000000, 0, 0, 0, -0.00000291, -0.00000007, 0, 0.00000504, 0.00002432, -0.00000005, 0, -0.00000011, 0.00000000, 0.00002360, -0.00000003, 0, 0.00000000, -0.00000044, -0.00000030, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.1759932,0.00007914,-0.00000002],
   'gammaWriter'        : [1.2515585,0.0000825,-0.0000001],
   'gammaReaderHeater'  : [1.000421547,-0.000001796,0.000000003],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultTI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesTI,
}

RHO_TI7551_50130_OG8_5400 = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00508068, -0.00005686, 0.00000017, 0.00623816, 0.00000155, -0.00002407, 1.00951730, 0.00005422, -0.00748988, 0.10143202, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00465662, 0.00451963, -0.00001003, -0.00007175, 0.00000050, 0.00000021, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00057918, -0.00000713, 0.00000003, 0, 0, 0, -0.00000234, -0.00000004, 0, 0.00000430, 0.00003275, -0.00000008, 0, -0.00000002, -0.00000030, 0.00004114, -0.00000008, 0, 0.00000001, -0.00000045, -0.00000043, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.14247291,0.00035736,-0.00000033],
   'gammaWriter'        : [1.2774925,0.0000889,-0.0000001],
   'gammaReaderHeater'  : [1.001699908,-0.000003689,0.000000006],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultTI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesTI,
}

RHO_TI7551_50116_N4Z_5400 = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00770545, -0.00006563, 0.00000017, 0.00711198, 0.00000111, -0.00002484, 0.99284002, 0.00015618, -0.00707810, -0.01506688, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00408777, 0.00492192, -0.00001158, -0.00006589, 0.00000072, 0.00000017, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00138061, -0.00001943, 0.00000006, 0, 0, 0, 0.00000012, -0.00000003, 0, 0.00000622, 0.00001049, -0.00000006, 0, 0.00000013, 0.00000003, 0.00000009, -0.00000002, 0, 0.00000024, 0.00000087, 0.00000000,AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.20754731,    0.00000552,   0.00000008],
   'gammaWriter'        : [1.28171349,    0.00003220,   0.00000000],
   'gammaReaderHeater'  : [1.00123966,   -0.00000365,   0.00000001],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultTI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesTI,
}

RHO_TI7551_50116_OG8_5400_4H = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00007352, -0.00002518, 0.00000008, 0.00633238, 0.00000066, -0.00001607, 0.91709937, 0.00008206, -0.00374924, 0.40776915, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00217858, 0.00467508, -0.00000986, -0.00004197, 0.00000068, 0.00000011, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00167164, -0.00000906, 0.00000003, 0, 0, 0, -0.00002826, -0.00000002, 0, 0.00000607, 0.00002474, -0.00000004, 0, -0.00000001, -0.00000030, 0.00003936, -0.00000003, 0, -0.00000003, -0.00000009, -0.00000063, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.2075473,    0.00000552,   0.00000008],
   'gammaWriter'        : [1.2817135,    0.0000322,    0],
   'gammaReaderHeater'  : [1.001239625, -0.000003649,  0.000000008],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultTI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesTI,
}

RHO_TI7551_50116_NT4_5400_4H = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00360068, -0.00005818, 0.00000014, 0.00673595, 0.00000101, -0.00001760, 0.97652614, 0.00011527, -0.00661856, -0.08644398, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00315963, 0.00479264, -0.00000916, -0.00006202, 0.00000064, 0.00000016, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[-0.00005128, -0.00000116, 0.00000001, 0, 0, 0, -0.00000577, -0.00000003, 0, 0.00000387, 0.00005068, -0.00000007, 0, -0.00000003, -0.00000076, 0.00004922, -0.00000010, 0, 0.00000009, -0.00000057, -0.00000067, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.20540000, 0.00004000, 0.00000000],
   'gammaWriter'        : [1.01820000, -0.00004000, 0.00000000],
   'gammaReaderHeater'  : [1.00096000, 0.00000000, 0.00000000],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultTI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesTI,
   'CoeffTrackingNo'    : 'RW2RT061',
}

RHO_TI7551_50116_OT4_5400 = { # 8/21/2015 #55 ROSEWOOD71D_RHO_501.16_TI_0XC200_0X1_OT4_2
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00419327, -0.00004178, 0.00000012, 0.00664623, 0.00000090, -0.00002420, 0.97966091, 0.00011571, -0.00954325, 0.00172085, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00197494, 0.00459681, -0.00001058, -0.00005007, 0.00000059, 0.00000014, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00074025, -0.00001057, 0.00000003, 0, 0, 0, 0.00000585, -0.00000003, 0, 0.00000471, 0.00000934, -0.00000002, 0, 0.00000009, -0.00000017, -0.00000175, -0.00000002, 0, 0.00000018, 0.00000060, 0.00000023, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.20540000, 0.00004000, 0.00000000, ],
   'gammaWriter'        : [1.01820000, -0.00004000, 0.00000000, ],
   'gammaReaderHeater'  : [1.00096000, 0.00000000, 0.00000000, ],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultTI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesTI,
   'CoeffTrackingNo'    : 'RW1RT055',
}

RHO_TI7551_50116_OT4_5400_4H = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00382031, -0.00007542, 0.00000020, 0.00675380, 0.00000096, -0.00001922, 0.99763324, 0.00011688, -0.00790692, -0.18044534, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00461115, 0.00471504, -0.00000934, -0.00008351, 0.00000070, 0.00000022, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00089860, -0.00001044, 0.00000003, 0, 0, 0, 0.00000380, -0.00000004, 0, 0.00000506, -0.00000108, -0.00000002, 0, 0.00000006, 0.00000018, 0.00000500, -0.00000004, 0, 0.00000022, 0.00000070, 0.00000003, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.20540000, 0.00004000, 0.00000000],
   'gammaWriter'        : [1.01820000, -0.00004000, 0.00000000],
   'gammaReaderHeater'  : [1.00096000, 0.00000000, 0.00000000],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultTI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesTI,
   'CoeffTrackingNo'    : 'RW2RT057',
}

RHO_TI7551_50116_NL2_5400_4H = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00620066, -0.00005615, 0.00000015, 0.00658429, 0.00000115, -0.00001942, 0.99434629, 0.00001828, -0.00817877, -0.09442237, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00538783, 0.00471116, -0.00001050, -0.00006352, 0.00000072, 0.00000017, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00169795, -0.00001937, 0.00000005, 0, 0, 0, -0.00000732, 0.00000004, 0, 0.00000498, -0.00002525, -0.00000003, 0, 0.00000014, 0.00000031, -0.00001709, -0.00000002, 0, 0.00000018, 0.00000142, 0.00000005, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.20539999, 0.00004000, 0.00000000],
   'gammaWriter'        : [1.01820004, -0.00004000, 0.00000000],
   'gammaReaderHeater'  : [1.00095999, 0.00000000, 0.00000000],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultTI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesTI,
   'CoeffTrackingNo'    : 'RW2RT076',
}

RHO_TI7551_50116_PD7_5400_4H = { # 88 RW72D_RHO_TI_501.16_PD7_4H_18-Nov-2015
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00435199, -0.00003552, 0.00000011, 0.00692033, 0.00000089, -0.00002438, 1.06205259, -0.00001511, -0.00953056, -1.03307225, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00144310, 0.00486977, -0.00001203, -0.00005702, 0.00000060, 0.00000016, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[-0.00111315, -0.00002556, 0.00000006, 0, 0, 0, -0.00007381, 0.00000007, 0, 0.00000594, -0.00001724, 0.00000002, 0, 0.00000026, -0.00000039, 0.00006362, -0.00000007, 0, 0.00000026, 0.00000189, -0.00000220, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.20539999, 0.00004000, 0.00000000, ],
   'gammaWriter'        : [1.01820004, -0.00004000, 0.00000000, ],
   'gammaReaderHeater'  : [1.00095999, 0.00000000, 0.00000000, ],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultTI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesTI,
   'CoeffTrackingNo'    : 'RW2RT088',
}

RHO_TI7551_50116_NL2_5400 = {    # 1-Oct-2015 #72 ROSEWOOD71D_RHO_501.16_TI_0XC200_0X1_NL2_2
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00603423, -0.00006590, 0.00000018, 0.00689056, 0.00000085, -0.00002473, 1.00125912, 0.00002268, -0.00892204, 0.02924038, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00331968, 0.00473571, -0.00001078, -0.00007130, 0.00000054, 0.00000019, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00191852, -0.00001739, 0.00000005, 0, 0, 0, -0.00000353, 0.00000003, 0, 0.00000474, -0.00001921, -0.00000002, 0, 0.00000009, 0.00000017, -0.00001956, -0.00000004, 0, 0.00000018, 0.00000153, 0.00000031, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.20540000, 0.00004000, 0.00000000, ],
   'gammaWriter'        : [1.01820000, -0.00004000, 0.00000000, ],
   'gammaReaderHeater'  : [1.00096000, 0.00000000, 0.00000000, ],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultTI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesTI,
   'CoeffTrackingNo'    : 'RW1RT072',
}

RHO_TI7551_50116_PD7_5400 = {    # 92 RW71D_RHO_TI_501.16_PD7_2H_28-Nov-2015
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00425924, -0.00005368, 0.00000015, 0.00715837, 0.00000064, -0.00002466, 1.01468938, -0.00001280, -0.00902860, -0.03761671, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00306005, 0.00488208, -0.00001085, -0.00006633, 0.00000042, 0.00000018, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00179771, -0.00001967, 0.00000005, 0, 0, 0, -0.00000551, 0.00000002, 0, 0.00000556, -0.00001769, -0.00000004, 0, 0.00000013, 0.00000032, -0.00000798, -0.00000003, 0, 0.00000022, 0.00000136, -0.00000003, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.20539999, 0.00004000, 0.00000000, ],
   'gammaWriter'        : [1.01820004, -0.00004000, 0.00000000, ],
   'gammaReaderHeater'  : [1.00095999, 0.00000000, 0.00000000, ],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultTI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesTI,
   'CoeffTrackingNo'    : 'RW1RT092',
}

RHO_LSI5830_50114_5400 = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00259673, -0.00007592, 0.00000020, 0.00668995, 0.00000031, -0.00001890, 0.97528076, -0.00000792, -0.00541454, 0.42903827, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00410828, 0.00485924, -0.00000998, -0.00006712, 0.00000035, 0.00000018, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00224922, 0.00000486, 0.00000000, 0, 0, 0, 0.00001853, -0.00000004, 0, 0.00000589, -0.00000558, -0.00000008, 0, 0.00000018, 0.00000032, 0.00001919, -0.00000003, 0, 0.00000010, 0.00000045, -0.00000064, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.136184590, -0.000021970,  0.000000070],
   'gammaWriter'        : [1.222359600,  0.000018500,  0],
   'gammaReaderHeater'  : [1.000467146, -0.000001333,  0.000000003],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
}

RHO_LSI5830_50114_5400_NG8 = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00313251, -0.00003382, 0.00000007, 0.00688324, 0.00000100, -0.00002647, 1.02220385, 0.00015564, -0.00640693, -0.29744125, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00359029, 0.00483005, -0.00001251, -0.00007029, 0.00000074, 0.00000019, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[-0.00051973, -0.00000401, 0.00000002, 0, 0, 0, -0.00002416, -0.00000001, 0, 0.00000376, 0.00005270, -0.00000007, 0, -0.00000004, -0.00000049, 0.00006030, -0.00000010, 0, 0.00000003, -0.00000095, -0.00000061, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.18666765,   0.0003643,   -0.00000101],
   'gammaWriter'        : [1.2829372,    0.000032,     0],
   'gammaReaderHeater'  : [1.000651974, -0.000002765,  0.000000007],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
}

RHO_LSI5830_50114_5400_4H = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00379213, -0.00012232, 0.00000033, 0.00662294, 0.00000043, -0.00002396, 1.05021412, 0.00001876, -0.00698109, -0.36963650, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00455441, 0.00477154, -0.00001205, -0.00006101, 0.00000062, 0.00000015, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00286567, 0.00001662, -0.00000007, 0, 0, 0, 0.00001141, -0.00000006, 0, 0.00000575, 0.00003297, -0.00000003, 0, 0.00000005, -0.00000038, 0.00000125, -0.00000002, 0, 0.00000015, -0.00000028, 0.00000001, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.136184590, -0.000021970,  0.000000070],
   'gammaWriter'        : [1.222359600,  0.000018500,  0],
   'gammaReaderHeater'  : [1.000467146, -0.000001333,  0.000000003],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
}

RHO_LSI5830_50114_NU7_5400_4H = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00264019, -0.00002573, 0.00000006, 0.00677062, 0.00000117, -0.00002466, 0.98116447, 0.00016178, -0.00669697, 0.14148737, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00593570, 0.00460908, -0.00000988, -0.00007314, 0.00000089, 0.00000020, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00188007, -0.00000995, 0.00000004, 0, 0, 0, -0.00000909, -0.00000002, 0, 0.00000476, 0.00002101, -0.00000009, 0, 0.00000005, -0.00000006, 0.00002391, -0.00000004, 0, -0.00000005, 0.00000020, -0.00000025, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.18666765,   0.0003643,   -0.00000101],
   'gammaWriter'        : [1.2829372,    0.000032,     0],
   'gammaReaderHeater'  : [1.000651974, -0.000002765,  0.000000007],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
}

RHO_LSI5830_50116_OT4_5400 = { # 8/21/2015 #56 ROSEWOOD71D_RHO_501.16_LSI_0X8200_0X2_OT4_2
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00348451, -0.00005236, 0.00000013, 0.00703204, 0.00000098, -0.00002753, 1.04713557, 0.00010413, -0.00930988, -0.45066676, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00238493, 0.00482542, -0.00001173, -0.00005771, 0.00000068, 0.00000015, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[-0.00004703, -0.00000234, 0.00000002, 0, 0, 0, -0.00001224, 0.00000000, 0, 0.00000383, 0.00004743, -0.00000007, 0, 0.00000016, -0.00000083, 0.00003897, -0.00000008, 0, 0.00000012, -0.00000004, -0.00000058, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.20540000, 0.00004000, 0.00000000, ],
   'gammaWriter'        : [1.01820000, -0.00004000, 0.00000000, ],
   'gammaReaderHeater'  : [1.00096000, 0.00000000, 0.00000000, ],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
   'CoeffTrackingNo'    : 'RW1RL056',
}

RHO_LSI5830_50116_O2Q_5400 = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00538339, -0.00009765, 0.00000026, 0.00718405, 0.00000133, -0.00002735, 1.02264085, 0.00019444, -0.00679593, -0.27497269, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00400238, 0.00504930, -0.00001295, -0.00009967, 0.00000096, 0.00000028, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00052309, -0.00000917, 0.00000004, 0, 0, 0, -0.00000237, -0.00000002, 0, 0.00000345, 0.00003926, -0.00000011, 0, 0.00000005, -0.00000011, 0.00004486, -0.00000007, 0, 0.00000002, -0.00000080, -0.00000047, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.2075473,    0.00000552,   0.00000008],
   'gammaWriter'        : [1.2817135,    0.0000322,    0],
   'gammaReaderHeater'  : [1.001239625, -0.000003649,  0.000000008],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
}

RHO_LSI5830_50116_N5T_5400 = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00000325, -0.00006157, 0.00000019, 0.00713617, 0.00000060, -0.00002562, 1.10370840, -0.00003577, -0.00616310, -0.68659651, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00055186, 0.00515559, -0.00001283, -0.00007038, 0.00000029, 0.00000020, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00281446, -0.00001643, 0.00000004, 0, 0, 0, -0.00005011, -0.00000002, 0, 0.00000469, 0.00002950, -0.00000001, 0, 0.00000004, -0.00000042, -0.00000894, 0.00000004, 0, 0.00000015, -0.00000076, 0.00000012, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.2075473,   0.00000552, 0.00000008],
   'gammaWriter'        : [1.2817135,   0.0000322,  0],
   'gammaReaderHeater'  : [1.001239625,-0.000003649,0.000000008],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
}

RHO_LSI5830_50116_NL2_5400 = { # 68 RW71D_RHO_LSI_501.16_NL2_2H_21-Sep-2015
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00425628, -0.00006810, 0.00000017, 0.00728779, 0.00000090, -0.00002949, 1.05308304, 0.00011310, -0.00966521, -0.56397672, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00280930, 0.00500742, -0.00001307, -0.00007194, 0.00000062, 0.00000019, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[-0.00031209, 0.00000094, 0.00000001, 0, 0, 0, -0.00001186, -0.00000001, 0, 0.00000394, 0.00003731, -0.00000008, 0, 0.00000021, -0.00000048, 0.00003679, -0.00000009, 0, 0.00000012, -0.00000015, -0.00000051, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.20539999, 0.00004000, 0.00000000, ],
   'gammaWriter'        : [1.01820004, -0.00004000, 0.00000000, ],
   'gammaReaderHeater'  : [1.00095999, 0.00000000, 0.00000000, ],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
   'CoeffTrackingNo'    : 'RW1RL068',
}

RHO_LSI5830_50116_PD7_5400 = { # 83 RW71D_RHO_LSI_501.16_PD7_2H_06-Nov-2015
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00274280, -0.00004670, 0.00000012, 0.00734545, 0.00000077, -0.00002389, 1.05812748, -0.00002976, -0.00805913, -0.38697236, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00264359, 0.00510569, -0.00001256, -0.00006145, 0.00000059, 0.00000016, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00124181, -0.00000624, 0.00000001, 0, 0, 0, -0.00003497, 0.00000000, 0, 0.00000445, -0.00000571, -0.00000004, 0, 0.00000015, 0.00000016, 0.00000667, -0.00000001, 0, 0.00000006, 0.00000055, -0.00000026, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.20539999, 0.00004000, 0.00000000, ],
   'gammaWriter'        : [1.01820004, -0.00004000, 0.00000000, ],
   'gammaReaderHeater'  : [1.00095999, 0.00000000, 0.00000000, ],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
   'CoeffTrackingNo'    : 'RW1RL083',
}

RHO_LSI5830_50116_N4Z_5400_4H = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00555197, -0.00008038, 0.00000022, 0.00710369, 0.00000068, -0.00002545, 1.01866110, 0.00006208, -0.00634574, 0.02339846,  AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00213605, 0.00500685, -0.00001265, -0.00006177, 0.00000051, 0.00000018, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00000170, 0.00000969, -0.00000002, 0, 0, 0, -0.00002629, 0.00000000, 0, 0.00000342, 0.00003924, -0.00000008, 0, 0.00000013, -0.00000067, 0.00004658, -0.00000008, 0, 0.00000004, -0.00000049, -0.00000062, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.2075473,    0.00000552,   0.00000008],
   'gammaWriter'        : [1.2817135,    0.0000322,    0],
   'gammaReaderHeater'  : [1.001239625, -0.000003649,  0.000000008],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
}

RHO_LSI5830_50116_NT4_5400_4H = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00301556, -0.00004773, 0.00000012, 0.00696228, 0.00000095, -0.00002737, 1.03887423, 0.00011127, -0.00944631, -0.53697326, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00236747, 0.00481637, -0.00001261, -0.00005643, 0.00000067, 0.00000015, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00028634, -0.00000334, 0.00000002, 0, 0, 0, -0.00000203, -0.00000001, 0, 0.00000379, 0.00003887, -0.00000009, 0, 0.00000017, -0.00000035, 0.00004458, -0.00000011, 0, 0.00000010, -0.00000018, -0.00000044, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.20540000, 0.00004000, 0.00000000],
   'gammaWriter'        : [1.01820000, -0.00004000, 0.00000000],
   'gammaReaderHeater'  : [1.00096000, 0.00000000, 0.00000000],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
   'CoeffTrackingNo'    : 'RW2RL060',
}

RHO_LSI5830_50116_OT4_5400_4H = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00435255, -0.00006793, 0.00000017, 0.00711579, 0.00000106, -0.00002584, 1.03172810, 0.00014698, -0.00880272, -0.44301118, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00358451, 0.00491213, -0.00001181, -0.00007982, 0.00000072, 0.00000021, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00045304, -0.00000550, 0.00000003, 0, 0, 0, -0.00000405, -0.00000002, 0, 0.00000387, 0.00004874, -0.00000010, 0, 0.00000016, -0.00000052, 0.00003942, -0.00000007, 0, 0.00000010, -0.00000028, -0.00000047, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.20540000, 0.00004000, 0.00000000],
   'gammaWriter'        : [1.01820000, -0.00004000, 0.00000000],
   'gammaReaderHeater'  : [1.00096000, 0.00000000, 0.00000000],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
   'CoeffTrackingNo'    : 'RW2RL058',
}

RHO_LSI5830_50116_NL2_5400_4H = { #69
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00359399, -0.00006805, 0.00000018, 0.00737023, 0.00000075, -0.00002744, 1.06573268, 0.00008966, -0.00878080, -0.74061078, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00302504, 0.00504136, -0.00001229, -0.00007815, 0.00000046, 0.00000021, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00027592, -0.00000261, 0.00000002, 0, 0, 0, -0.00001545, -0.00000000, 0, 0.00000394, 0.00003339, -0.00000008, 0, 0.00000022, -0.00000030, 0.00002697, -0.00000007, 0, 0.00000015, -0.00000041, 0.00000000, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.20540000, 0.00004000, 0.00000000],
   'gammaWriter'        : [1.01820000, -0.00004000, 0.00000000],
   'gammaReaderHeater'  : [1.00096000, 0.00000000, 0.00000000],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
   'CoeffTrackingNo'    : 'RW2RL069',
}

RHO_LSI5830_50116_PD7_5400_4H = { # 87 RW72D_RHO_LSI_501.16_PD7_4H_18-Nov-2015
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00243277, -0.00005008, 0.00000013, 0.00724168, 0.00000091, -0.00002785, 1.07415162, -0.00001610, -0.00967481, -0.65083078, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00267463, 0.00492320, -0.00001226, -0.00005885, 0.00000063, 0.00000016, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00061369, -0.00000218, 0.00000001, 0, 0, 0, -0.00002750, 0.00000006, 0, 0.00000415, -0.00000125, -0.00000003, 0, 0.00000014, 0.00000011, -0.00000143, -0.00000004, 0, 0.00000010, 0.00000052, 0.00000003, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.20539999, 0.00004000, 0.00000000, ],
   'gammaWriter'        : [1.01820004, -0.00004000, 0.00000000, ],
   'gammaReaderHeater'  : [1.00095999, 0.00000000, 0.00000000, ],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
   'CoeffTrackingNo'    : 'RW2RL087',
}

RHO_LSI5830_50116_OG8_5400_4H = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00030091, -0.00005355, 0.00000017, 0.00728256, 0.00000019, -0.00002438, 1.05067365, 0.00002110, -0.00593152, -0.23224909, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00253459, 0.00513469, -0.00001165, -0.00005656, 0.00000020, 0.00000016, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00201882, -0.00001293, 0.00000004, 0, 0, 0, -0.00003442, -0.00000001, 0, 0.00000465, 0.00003860, -0.00000005, 0, 0.00000016, -0.00000062, 0.00003224, -0.00000003, 0, -0.00000011, -0.00000055, -0.00000028, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.2075473,    0.00000552,   0.00000008],
   'gammaWriter'        : [1.2817135,    0.0000322,    0],
   'gammaReaderHeater'  : [1.001239625, -0.000003649,  0.000000008],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
}

RHO_LSI5830_50130_OG8_5400 = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00398778, -0.00005428, 0.00000015, 0.00618528, 0.00000162, -0.00002271, 1.02797550, 0.00002401, -0.00580967, -0.15264986, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00432705, 0.00462487, -0.00001092, -0.00007195, 0.00000058, 0.00000020, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[-0.00031381, 0.00000188, 0.00000001, 0, 0, 0, -0.00001290, -0.00000003, 0, 0.00000319, 0.00003609, -0.00000009, 0, 0.00000008, -0.00000030, 0.00003293, -0.00000009, 0, 0.00000002, -0.00000036, -0.00000025, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.14247291,   0.00035736,  -0.00000033],
   'gammaWriter'        : [1.2774925,    0.0000889,   -0.0000001],
   'gammaReaderHeater'  : [1.001699908, -0.000003689,  0.000000006],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
}

RHO_LSI5830_50130_OG8_5400_4H = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00434718, -0.00006218, 0.00000018, 0.00626545, 0.00000167, -0.00002320, 1.02530460, 0.00006741, -0.00543263, -0.21107708,  AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00347087, 0.00466962, -0.00001193, -0.00007806, 0.00000062, 0.00000022,  AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00026804, -0.00000210, 0.00000002, 0, 0, 0, 0.00000233, -0.00000003, 0, 0.00000309, 0.00005251, -0.00000010, 0, 0.00000005, -0.00000075, 0.00004838, -0.00000006, 0, 0.00000004, -0.00000049, -0.00000087, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.14247291,0.00035736,-0.00000033],
   'gammaWriter'        : [1.2774925,0.0000889,-0.0000001],
   'gammaReaderHeater'  : [1.001699908,-0.000003689,0.000000006],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
}

RHO_LSI5830_50141_NL2_5400 = { # 84 RW71D_RHO_LSI_501.41_NL2_2H_06-Nov-2015
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00378008, -0.00004442, 0.00000011, 0.00583540, 0.00000180, -0.00002707, 1.04052120, 0.00004794, -0.01139575, -0.78064233, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00380367, 0.00397318, -0.00001062, -0.00004937, 0.00000114, 0.00000013, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00086285, -0.00000629, 0.00000002, 0, 0, 0, -0.00001955, 0.00000007, 0, 0.00000321, -0.00002141, -0.00000003, 0, 0.00000021, 0.00000061, -0.00000109, 0.00000001, 0, 0.00000019, 0.00000045, -0.00000024, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.20539999, 0.00004000, 0.00000000, ],
   'gammaWriter'        : [1.01820004, -0.00004000, 0.00000000, ],
   'gammaReaderHeater'  : [1.00095999, 0.00000000, 0.00000000, ],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
   'CoeffTrackingNo'    : 'RW1RL084',
}

RHO_LSI5830_50141_NL2_5400_4H = { # 86 RW72D_RHO_LSI_501.41_NL2_11-Nov-2015
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00335023, -0.00004659, 0.00000013, 0.00590045, 0.00000177, -0.00002662, 1.04606688, -0.00000082, -0.01116783, -0.62621013, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00228187, 0.00411321, -0.00001211, -0.00004507, 0.00000114, 0.00000013, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00117251, -0.00000498, 0.00000001, 0, 0, 0, -0.00001636, 0.00000009, 0, 0.00000315, 0.00000108, -0.00000003, 0, 0.00000014, -0.00000021, -0.00002442, 0.00000003, 0, 0.00000010, 0.00000051, 0.00000029, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.20539999, 0.00004000, 0.00000000, ],
   'gammaWriter'        : [1.01820004, -0.00004000, 0.00000000, ],
   'gammaReaderHeater'  : [1.00095999, 0.00000000, 0.00000000, ],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
   'CoeffTrackingNo'    : 'RW2RL086',
}

RHO_LSI5830_50142_NL2_5400 = { # 99 RW71D_RHO_LSI_501.42_NL2_2H_26-Feb-2016
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00231759, -0.00004208, 0.00000014, 0.00652900, 0.00000090, -0.00002775, 1.05533120, -0.00009658, -0.00902854, 0.01274160, AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00216112, 0.00406572, -0.00001075, -0.00003516, 0.00000080, 0.00000011, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00197057, -0.00001845, 0.00000004, 0, 0, 0, -0.00001556, 0.00000010, 0, 0.00000436, -0.00000301, -0.00000006, 0, 0.00000032, 0.00000020, -0.00000537, 0.00000003, 0, -0.00000005, 0.00000030, 0.00000012, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.30525584, 0.00001885, -0.00000004, ],
   'gammaWriter'        : [1.34481060, -0.00003660, 0.00000010, ],
   'gammaReaderHeater'  : [1.00084648, -0.00000190, 0.00000000, ],
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
   'CoeffTrackingNo'    : 'RW1RL099',
}


# ================================================================================================
#   HAMR Related 2-Oct-15
# ================================================================================================
RHO_LSI5235_5W_5400 = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.0063569, 0.0000624, -0.000000347, 0.0084423, 0.00000091, -0.0000232, 1, 0, 0, 0,  AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.0052525, 0.0065486, -0.0000104, 0, 0, 0,  AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0, 0.000082,-0.000000188, 0, 0, 0, 0.002371, -0.00000213, 0, 0.0001166, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0024136, 0, 0, 0, 0, 0,-0.1,0.059, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.149,0,0],
   'gammaWriter'        : [1.52, 0,0],
   'gammaReaderHeater'  : [1.0  ,0,0], 
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
   'CoeffTrackingNo'    : 'STWRL003',
}

#HAMR Related 8-Oct-15
RHO_LSI5235_Z7_5400 = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00593941100000, 0.00010884000000, -0.00000048200000, 0.00872822900000, 0.00000018500000, -0.00002340000000, 1, 0, 0, 0,  AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00406052000000, 0.00664549000000, -0.00001100000000, 0, 0, 0,  AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0, 0.00001420000000,-0.00000000273000, 0, 0, 0, 0.00186548300000,-0.00000076500000, 0, 0.00017457000000, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.00265387900000, 0, 0, 0, 0, 0, -0.1, 0.059,AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.121,0,0],
   'gammaWriter'        : [1.463, 0,0],
   'gammaReaderHeater'  : [1.0  ,0,0], 
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
   'CoeffTrackingNo'    : 'STWRL004',
}
#HAMR Related 16-Dec-15
RHO_LSI5235_Z7_5400_V6 = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00593941100000, 0.00010884000000, -0.00000048200000, 0.00872822900000, 0.00000018500000, -0.00002340000000, 1, 0, 0, 0,  AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00406052000000, 0.00664549000000, -0.00001100000000, 0, 0, 0,  AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[ 0, 0.00001420000000,-0.00000000273000, 0, 0, 0, 0.00186548300000,-0.00000076500000, 0, 0.00017457000000, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.00265387900000, 0, 0, 0, 0, 0,-0.1, 0.059, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.121,0,0],
   'gammaWriter'        : [1.463, 0,0],
   'gammaReaderHeater'  : [1.0  ,0,0], 
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
   'CoeffTrackingNo'    : 'STWRL006',
}
#HAMR Related 16-Dec-15
RHO_LSI5235_Z7_5400_V8 = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.024851578, -0.0000157283377289, 0.0000000227298427571, 0.0101716114283, 0.00000139094025961, -0.0000285754416153, 1.11892255403, -0.0000164233769567, -0.0000164233769567, -0.002685054,  AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00849055176278, 0.00642083451413, -0.0000119864197309, 0.00000279296260458, 0.0000007447467361, -0.0000000166187770977,  AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.008514074, 0.00000243269040791,0.0000000809186082813, 0, 0, 0, 0.00299615488526,0.00000189755082548, 0, 0.000387375, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.007716049, 0.00000133505546935, -0.0000301920185767, 0, 0, -0.0000307337777018,-0.1,0.059, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.121,0,0],
   'gammaWriter'        : [1.463, 0,0],
   'gammaReaderHeater'  : [1.0  ,0,0], 
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
   'CoeffTrackingNo'    : 'STWRL010',
}
#HAMR Related 15-DEC-15
RHO_LSI5235_AL1_5400 = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00256700000, 0.000129000000, -0.00000058500000, 0.00863300000, 0.00000064200000, -0.00002160000000, 1, 0, 0, 0,  AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.003823000000, 0.006668000000, -0.000010900000000, 0, 0, 0,  AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0, 0.00007130000000,-0.00000013000, 0, 0, 0, 0.00137500000,-0.0000021600000, 0, 0.00017000000, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.00265400000, 0, 0, 0, 0, 0,-0.1,0.059, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.121,0,0],
   'gammaWriter'        : [1.463, 0,0],
   'gammaReaderHeater'  : [1.0  ,0,0], 
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
   'CoeffTrackingNo'    : 'STWRL005',
}

#HAMR Related 15-DEC-15
RHO_LSI5235_AL1_5400_V9 = {
   'WRT_HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.0295698923458, -0.0000935224483848, 0.00000026265955757, 0.00989935121452, 0.00000154927197508, -0.0000213937446872, 1.02026168324, 0.0000617697096368, -0.006620514, 0.0180709215949,  AFH_Uniform_Track_Lbl]
   },
   'HTR_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.01402549, 0.00631273772165,-0.00000963964453116 , -0.000141953200001, 0.00000115896501236, 0.000000532908351986, AFH_Uniform_Track_Lbl]
   },
   'WRT_PTP_COEF':
   {
      'HI_POWER':[],
      'LO_POWER':[0.00292130592055, -0.00000937103641967,0.0000000398938435062, 0, 0, 0, 0.00171005081635,0.00000151341189944, 0, 0.000246763848396, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.00564823869133, -0.000000291685319352, 0.00000725216562326, 0, 0, -0.0000413744428318, -0.1,0.059, AFH_Uniform_Track_Lbl]
   },
   'gammaWriterHeater'  : [1.121,0,0],
   'gammaWriter'        : [0.96, 0,0],
   'gammaReaderHeater'  : [1.0  ,0,0], 
   'isDriveDualHeater'  : 1,
   'triseValues'        : triseValuesDefaultLSI,
   'ovsRiseTimeValues'  : ovsRiseTimeValuesLSI,
   'CoeffTrackingNo'    : 'STWRL011',
}

# ================================================================================================
# ================================================================================================
# ================================================================================================

clearance_Coefficients = {
   'ATTRIBUTE' : 'PREAMP_TYPE',
   'DEFAULT'   : 'LSI5830',
   # ==================== LSI/Avago preamp ====================
   'LSI5830' :{
      'ATTRIBUTE' : 'AABType',
      'DEFAULT'   : '501.16',
      '501.11'    : {
         'ATTRIBUTE' : 'numPhysHds',
         'DEFAULT'   : 2,
         2           : {
            'ATTRIBUTE' : 'HSA_WAFER_CODE',
            'DEFAULT'   : 'N2Q',
            'NI0'       : RHO_LSI5830_50111_5400,
            'NU7'       : RHO_LSI5830_50111_5400_NU7,      # 17
            'N2Q'       : RHO_LSI5830_50111_5400_N2Q,      # 19
         },
         4           : {
            'ATTRIBUTE' : 'HSA_WAFER_CODE',
            'DEFAULT'   : 'N2Q',
            'NI0'       : RHO_LSI5830_50111_5400_4H,       # 11
            'NU7'       : RHO_LSI5830_50111_5400_NU7,      # 17
            'N2Q'       : RHO_LSI5830_50111_N2Q_5400_4H,   # 21
         },
      },
      '501.14'    : {
         'ATTRIBUTE' : 'numPhysHds',
         'DEFAULT'   : 2,
         2           : {
            'ATTRIBUTE' : 'HSA_WAFER_CODE',
            'DEFAULT'   : 'NG8',
            'default'   : RHO_LSI5830_50114_5400,
            'NG8'       : RHO_LSI5830_50114_5400_NG8,
         },
         4           : {
            'ATTRIBUTE' : 'HSA_WAFER_CODE',
            'DEFAULT'   : 'NU7',
            'default'   : RHO_LSI5830_50114_5400_4H,           # 18
            'NU7'       : RHO_LSI5830_50114_NU7_5400_4H,       # 24
         },
      },
      '501.16'    : {
         'ATTRIBUTE' : 'numPhysHds',
         'DEFAULT'   : 2,
         2           : {
            'ATTRIBUTE' : 'HSA_WAFER_CODE',
            'DEFAULT'   : 'NL2',
            'O2Q'       : RHO_LSI5830_50116_O2Q_5400,          # 30
            'N5T'       : RHO_LSI5830_50116_N5T_5400,          # 33
            'OT4'       : RHO_LSI5830_50116_OT4_5400,          # 56 ROSEWOOD71D_RHO_501.16_LSI_0X8200_0X2_OT4_2
            'NL2'       : RHO_LSI5830_50116_NL2_5400,          # 68 RW71D_RHO_LSI_501.16_NL2_2H_21-Sep-2015
            'PD7'       : RHO_LSI5830_50116_PD7_5400,          # 83 RW71D_RHO_LSI_501.16_PD7_2H_06-Nov-2015
         },
         4           :  {
            'ATTRIBUTE' : 'HSA_WAFER_CODE',
            'DEFAULT'   : 'NL2',
            'O2Q'       : RHO_LSI5830_50116_OG8_5400_4H,       # 36
            'N4Z'       : RHO_LSI5830_50116_N4Z_5400_4H,       # 44
            'NT4'       : RHO_LSI5830_50116_NT4_5400_4H,       # 60
            'OT4'       : RHO_LSI5830_50116_OT4_5400_4H,       # 58
            'NL2'       : RHO_LSI5830_50116_NL2_5400_4H,       # 69
            'PD7'       : RHO_LSI5830_50116_PD7_5400_4H,       # 87 RW72D_RHO_LSI_501.16_PD7_4H_18-Nov-2015
         },
      },
      '501.41'    : {
         'ATTRIBUTE' : 'numPhysHds',
         'DEFAULT'   : 2,
         2           : {
            'ATTRIBUTE' : 'HSA_WAFER_CODE',
            'DEFAULT'   : 'NL2',
            'NL2'       : RHO_LSI5830_50141_NL2_5400,          # 84 RW71D_RHO_LSI_501.41_NL2_2H_06-Nov-2015
         },
         4           : {
            'ATTRIBUTE' : 'HSA_WAFER_CODE',
            'DEFAULT'   : 'NL2',
            'NL2'       : RHO_LSI5830_50141_NL2_5400_4H,       # 86 RW72D_RHO_LSI_501.41_NL2_4H_11-Nov-2015
         },

      },
      '501.42'    : RHO_LSI5830_50142_NL2_5400,                # 99 RW71D_RHO_LSI_501.42_NL2_2H_26-Feb-2016
      '501.30'    : {
         'ATTRIBUTE' : 'numPhysHds',
         'DEFAULT'   : 2,
         2           : {
            'ATTRIBUTE' : 'HSA_WAFER_CODE',
            'DEFAULT'   : 'OG8',
            'OG8'       : RHO_LSI5830_50130_OG8_5400,          # 40

         },
         4           : RHO_LSI5830_50130_OG8_5400_4H,          # 38
      },
      'H_25AS2M3' : {
         'ATTRIBUTE' : 'numPhysHds',
         'DEFAULT'   : 2,
         2           : HWY_LSI5830_25AS2M3_5400,
         4           : {
            'ATTRIBUTE' : 'HSA_WAFER_CODE',
            'DEFAULT'   : '4A4C5',
            '4A3C0'     : HWY_LSI5830_25AS2M3_5400_4H,
            '4A49H'     : HWY_LSI5830_25AS2M3_4A49H_5400_4H,   # 16
            '4A4C5'     : HWY_LSI5830_25AS2M3_4A4C5_5400_4H,   # 34
         },
      },
      'H_25RW3'      : {
         'ATTRIBUTE' : 'numPhysHds',
         'DEFAULT'   : 2,
         2           : HWY_LSI5830_25RW3_5400,                 # 15
         4           : HWY_LSI5830_25RW3_5400_4H,              # 23, 4AF1F
      },
      'H_25RW3E'     : {
         'ATTRIBUTE' : 'numPhysHds',
         'DEFAULT'   : 2,
         2           : {
            'ATTRIBUTE' : 'HSA_WAFER_CODE',
            'DEFAULT'   : '5A5J0',
            '5A2HH'     : HWY_LSI5830_25RW3E_5A2HH_5400,       # 52
            '5A3J2'     : HWY_LSI5830_25RW3E_5A3J2_5400,       # 64 RW71D_HWY_LSI_25RW3E_5A3J2_2H_07-Sep-2015
            '5ABG5'     : HWY_LSI5830_25RW3E_5ABG5_5400,       # 77 RW71D_HWY_LSI_25RW3E_5ABG5_2H_13-Oct-2015
            '5A5J0'     : HWY_LSI5830_25RW3E_5A5J0_5400,       # 78 RW71D_HWY_LSI_25RW3E_5A5J0_2H_22-Oct-2015
            '4C677'     : HWY_LSI5830_25RW3E_4C677_5400,       # 91 RW71D_HWY_LSI_25RW3E_4C677_2H_20-Nov-2015
         },
         4           : {
            'ATTRIBUTE' : 'HSA_WAFER_CODE',
            'DEFAULT'   : '5A99G',
            '4C6JH'     : HWY_LSI5830_25RW3E_4C6JH_5400_4H,    # 42
            '4A4C5'     : HWY_LSI5830_25RW3E_4A4C5_5400_4H,    # 35
            '5A2HH'     : HWY_LSI5830_25RW3E_5A2HH_5400_4H,    # 59
            '5A3J2'     : HWY_LSI5830_25RW3E_5A3J2_5400_4H,    # 67
            '5A2HG'     : HWY_LSI5830_25RW3E_5A2HG_5400_4H,    # 74
            '5A5J0'     : HWY_LSI5830_25RW3E_5A5J0_5400_4H,    # 80
            '5A99G'     : HWY_LSI5830_25RW3E_5A99G_5400_4H,    # 85
            '5AA99'     : HWY_LSI5830_25RW3E_5A99G_5400_4H,    # same as #85 5A99G
            '5A9BJ'     : HWY_LSI5830_25RW3E_5A99G_5400_4H,    # copy 5A99G
         },
      },
      '25RW3E'       : {
         'ATTRIBUTE' : 'numPhysHds',
         'DEFAULT'   : 2,
         2           : {
            'ATTRIBUTE' : 'HSA_WAFER_CODE',
            'DEFAULT'   : '5F057',
            '5F068'     : TDK_LSI5830_25RW3E_5F068_5400,       # 62
            '5F057'     : TDK_LSI5830_25RW3E_5F608_5400,       # 96 RW71D_TDK_LSI_25RW3E_5F608_2H_22-Dec-2015
         },
         4           : {
            'ATTRIBUTE' : 'HSA_WAFER_CODE',
            'DEFAULT'   : '5F608',
            '5F608'       : TDK_LSI5830_25RW3E_5F608_5400_4H,                # 94
         },
      },
      '25AS2M3'   : {
         'ATTRIBUTE' : 'numPhysHds',
         'DEFAULT'   : 2,
         2           : HWY_LSI5830_25AS2M3_5400,
         4           : TDK_LSI5830_25AS2M3_5400_4H,            # 14, 4F223
      },
   }, # LSI5830 =========

   # HMAR Related StarWood
   # ==================== LSI preamp ====================
   'LSI5235':{
      'ATTRIBUTE' : 'AABType',
      'DEFAULT'   : '501.11',
      '501.11'    : {
            'ATTRIBUTE' : 'HSA_WAFER_CODE',
            'DEFAULT'   : '5W',
            '5W'       : RHO_LSI5235_5W_5400,
            'BZ7'      : RHO_LSI5235_Z7_5400,

      },
   },

   # ==================== TI preamp ====================
   'TI7551':{
      'ATTRIBUTE' : 'AABType',
      'DEFAULT'   : '501.16',
      '501.11'    : RHO_TI7550_50111_5400,
      '501.14'    : RHO_TI7551_50114_5400,
      '501.16'       : {
         'ATTRIBUTE' : 'numPhysHds',
         'DEFAULT'   : 2,
         2           : {
            'ATTRIBUTE' : 'HSA_WAFER_CODE',
            'DEFAULT'   : 'NL2',
            'N4Z'       : RHO_TI7551_50116_N4Z_5400,           # 50
            'OT4'       : RHO_TI7551_50116_OT4_5400,           # 55 ROSEWOOD71D_RHO_501.16_TI_0XC200_0X1_OT4_2
            'NL2'       : RHO_TI7551_50116_NL2_5400,           # 1-Oct-2015 #72
            'PD7'       : RHO_TI7551_50116_PD7_5400,           # 92 RW71D_RHO_TI_501.16_PD7_2H_28-Nov-2015
         },
         4           : {
            'ATTRIBUTE' : 'HSA_WAFER_CODE',
            'DEFAULT'   : 'NL2',
            'OG8'       : RHO_TI7551_50116_OG8_5400_4H,        # 37
            'NT4'       : RHO_TI7551_50116_NT4_5400_4H,        # 61
            'OT4'       : RHO_TI7551_50116_OT4_5400_4H,        # 57
            'NL2'       : RHO_TI7551_50116_NL2_5400_4H,        # 76
            'PD7'       : RHO_TI7551_50116_PD7_5400_4H,        # 88 RW72D_RHO_TI_501.16_PD7_4H_18-Nov-2015
         },
      },
      '501.25'    : RHO_TI7551_50125_O2Q_5400,                 # 41
      '501.30'    : RHO_TI7551_50130_OG8_5400,                 # 39
      '501.42'    : RHO_LSI5830_50142_NL2_5400,                # 99 RW71D_RHO_LSI_501.42_NL2_2H_26-Feb-2016
      'H_25AS2M3' : HWY_TI7551_25AS2M3_5400,
      'H_25RW3'      : {
         'ATTRIBUTE' : 'numPhysHds',
         'DEFAULT'   : 2,
         2           : HWY_TI7551_25RW3E_5400,                 # 4/2/2015 #32
         4           : HWY_TI7551_25RW3E_5400,                 # 4/2/2015 #32
      },
      'H_25RW3E'     : {
         'ATTRIBUTE' : 'numPhysHds',
         'DEFAULT'   : 2,
         2           : {
            'ATTRIBUTE' : 'HSA_WAFER_CODE',
            'DEFAULT'   : '5A3J2',
            '4A4C5'     : HWY_TI7551_25RW3E_5400,              # 4/2/2015 #32
            '5A2HH'     : HWY_TI7551_25RW3E_5A2HH_5400,        # 63 ROSEWOOD71D_HWY_25RW3E_TI_0XC200_0X1_5A2HH_2
            '4C430'     : HWY_TI7551_25RW3E_4C430_5400,        # 65 ROSEWOOD71D_HWY_25RW3E_TI_0XC200_0X1_4C430_2
            '5A3J2'     : HWY_TI7551_25RW3E_5A3J2_5400,        # 1-Oct-2015 #73
         },
         4           : {
            'ATTRIBUTE' : 'HSA_WAFER_CODE',
            'DEFAULT'   : '5A99G',
            '4C6JH'     : HWY_TI7551_25RW3E_4C6JH_5400_4H,     # 45
            '4A60B'     : HWY_TI7551_25RW3E_4A60B_5400_4H,     # 43
            '5A2HH'     : HWY_TI7551_25RW3E_5A2HH_5400_4H,     # 66
            '5A3J2'     : HWY_TI7551_25RW3E_5A3J2_5400_4H,     # 71 RW72D_HWY_TI_25RW3E_5A3J2_4H_22-Sep-2015
            '5A2HG'     : HWY_TI7551_25RW3E_5A2HG_5400_4H,     # 79
            '5A5J0'     : HWY_TI7551_25RW3E_5A5J0_5400_4H,     # 81
            '5A99G'     : HWY_TI7551_25RW3E_5A99G_5400_4H,     # 82
            '5A9BJ'     : HWY_TI7551_25RW3E_5A99G_5400_4H,     # copy 5A99G
         },
      },
      '25RW3E'       : {
         'ATTRIBUTE' : 'numPhysHds',
         'DEFAULT'   : 2,
         2           : {
            'ATTRIBUTE' : 'HSA_WAFER_CODE',
            'DEFAULT'   : '5F057',
            '5F057'     : TDK_TI7551_25RW3E_5F608_5400,       # 97 RW71D_TDK_TI_25RW3E_5F608_2H_22-Dec-2015
         },
         4           : {
            'ATTRIBUTE' : 'HSA_WAFER_CODE',
            'DEFAULT'   : '5F816',
            '5F608'    : TDK_TI7551_25RW3E_5F608_5400_4H, #95
            '5F816'    : TDK_TI7551_25RW3E_5F608_5400_4H, #95
         },
      },	  
      '25AS2M3'   : TDK_TI7550_25AS2M2_5400,
   },
   # HMAR Related StarWood
   # ==================== LSI preamp ====================
   'LSI5235':{
      'ATTRIBUTE' : 'AABType',
      'DEFAULT'   : '501.11',
      '501.11'    : {
            'ATTRIBUTE' : 'HSA_WAFER_CODE',  
            'DEFAULT'   : '5W',
            '5W'       : RHO_LSI5235_5W_5400,          
            'BZ7'      : RHO_LSI5235_Z7_5400_V8,    
            'AL1'      : RHO_LSI5235_AL1_5400_V9, 

      },
   },
}
