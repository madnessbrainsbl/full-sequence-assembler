#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Test Parameters for Muskie
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/12/22 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/st135Params_AFH_v36.py $
# $Revision: #12 $
# $DateTime: 2016/12/22 19:01:21 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/st135Params_AFH_v36.py#12 $
# Level: 1
#---------------------------------------------------------------------------------------------------------#

######################################  On the fly contact dac regression limits ###################################
### These limits apply during the contact search.  Dac limit failures will cause an internal retry
### These do not apply to the final interpolation and will not (directly) cause test failures or global retries
full_SearchLimits = {
   'ACCESS_ORDER'       : ['member'],
   'ZoneOrder' : {
      # Only enter zones to be tested (no -1's needed) 11Oct21
      'ACCESS_ORDER'    : ['heaterElement', 'programName'],
      'WRITER_HEATER': {
         '*'    : {
            'ACCESS_ORDER'    : ['AABType', 'AFH_State'],
            '*'      : {
               1  : (118,13,55,31,93,45,0,149,),
               2  : (118,13,55,31,93,45,0,149,),
               3  : (118,13,55,31,93,45,0,149,),
               4  : (118,13,55,31,93,45,0,149,),
            },
            '501.12' : {
               1  : (118,13,130,31,142,45,93,55,0,149,), # (118,13,55,31,93,45,0,149,),
               2  : (118,13,130,31,142,45,93,55,0,149,), # (118,13,55,31,93,45,0,149,),
               3  : (118,13,130,31,142,45,93,55,0,149,), # (118,13,55,31,93,45,0,149,),
               4  : (118,13,130,31,142,45,93,55,0,149,), # (118,13,55,31,93,45,0,149,),
            },
            '501.16' : {
               1  : (118,13,130,31,142,45,93,55,0,149,), # (118,13,55,31,93,45,0,149,),
               2  : (118,13,130,31,142,45,93,55,0,149,), # (118,13,55,31,93,45,0,149,),
               3  : (118,13,130,31,142,45,93,55,0,149,), # (118,13,55,31,93,45,0,149,),
               4  : (118,13,130,31,142,45,93,55,0,149,), # (118,13,55,31,93,45,0,149,),
            },
            '501.41' : {
               1  : (118,13,130,31,142,45,93,55,0,149,), # (118,13,55,31,93,45,0,149,),
               2  : (118,13,130,31,142,45,93,55,0,149,), # (118,13,55,31,93,45,0,149,),
               3  : (118,13,130,31,142,45,93,55,0,149,), # (118,13,55,31,93,45,0,149,),
               4  : (118,13,130,31,142,45,93,55,0,149,), # (118,13,55,31,93,45,0,149,),
            },
         },
      },
      'READER_HEATER': {
         '*'    : {
            'ACCESS_ORDER'    : ['AABType', 'AFH_State'],
            '*'      : {
               1  : (118,13,55,31,93,45,0,149,),
               2  : (118,13,55,31,93,45,0,149,),
               3  : (118,13,55,31,93,45,0,149,),
               4  : (118,13,55,31,93,45,0,149,),
            },
            '501.12' : {
               1  : (118,13,130,31,142,45,93,55,0,149,), # (118,13,55,31,93,45,0,149,),
               2  : (118,13,130,31,142,45,93,55,0,149,), # (118,13,55,31,93,45,0,149,),
               3  : (118,13,130,31,142,45,93,55,0,149,), # (118,13,55,31,93,45,0,149,),
               4  : (118,13,130,31,142,45,93,55,0,149,), # (118,13,55,31,93,45,0,149,),
            },
            '501.16' : {
               1  : (118,13,130,31,142,45,93,55,0,149,), # (118,13,55,31,93,45,0,149,),
               2  : (118,13,130,31,142,45,93,55,0,149,), # (118,13,55,31,93,45,0,149,),
               3  : (118,13,130,31,142,45,93,55,0,149,), # (118,13,55,31,93,45,0,149,),
               4  : (118,13,130,31,142,45,93,55,0,149,), # (118,13,55,31,93,45,0,149,),
            },
            '501.41' : {
               1  : (118,13,130,31,142,45,93,55,0,149,), # (118,13,55,31,93,45,0,149,),
               2  : (118,13,130,31,142,45,93,55,0,149,), # (118,13,55,31,93,45,0,149,),
               3  : (118,13,130,31,142,45,93,55,0,149,), # (118,13,55,31,93,45,0,149,),
               4  : (118,13,130,31,142,45,93,55,0,149,), # (118,13,55,31,93,45,0,149,),
            },
         },
      },
   },
   'MaxExtrapolationTracks'   : {
      # Maximum OTF regression extrapolation.  Failures use default start/end dacs
      # if this limit is exceeded in a given zone, then OTF is turned on in that zone
      'ACCESS_ORDER'    : ['programName', 'headType'],
      '*' : {'TDK': (15000),         'HWY': (15000),         'RHO': (15000)},
      },
}

######################################  Search Options ###################################
### These limits apply during the contact search.  Dac limit failures will cause an internal retry
### These do not apply to the final interpolation and will not (directly) cause test failures or global retries
full_SearchOptions = {
   'ACCESS_ORDER'    : ['member'],
   'ShutOffHighFreqDuringGlobalRetries'   : {
      ## check , what is that?
      'ACCESS_ORDER' : ['programName', 'headType'],
      '*' : {'TDK': 0,      'HWY': 0,      'RHO': 0},
   },
   'RunReaderHeaterWPH' : {
      'ACCESS_ORDER' : ['programName', 'headType'],
      '*' : {'TDK': 0,      'HWY': 0,      'RHO': 0},
   },
   'EnableCurveFitDuringTCSCal'  : {
      'ACCESS_ORDER' : ['heaterElement', 'programName', 'headType'],
      'WRITER_HEATER'   : {
         '*' : {'TDK': 1,   'HWY': 1,   'RHO': 1},
      },
      'READER_HEATER'   : {
         '*' : {'TDK': 0,   'HWY': 0,   'RHO': 0},
      },
   },
   'IPDVersionToExecute'   : {
      # first entry is used beyond first global retries, second is first 2 attempts
      'ACCESS_ORDER' : ['programName', 'headType'],
      '*' : {'TDK': (3,2),  'HWY': (3,2),  'RHO':(3,2)},  #(3,2) will use IPD2 on the first 2 global retries and IPD3 on the third and beyond
   },
   'AFH1_WriteTriplet'  : {
      #This input determines the write power applied during aFH1 for the WRITER_HEATER
      'ACCESS_ORDER' : ['programName', 'headType'],
      '*' : {'TDK': (-1,-1,-1),   'HWY': (-1,-1,-1),   'RHO':(6,4,10)},
   },
}

full_baseIPD2Prm_135_update1 = {
   'ACCESS_ORDER' : ['member'],
   'CWORD1' : {
      'ACCESS_ORDER' : ['heaterElement'],
      'READER_HEATER': 0x3B16,
      '*'            : 0x3F16,
   },
   'CWORD2' : {
      'ACCESS_ORDER' : ['AFH_State', 'heaterElement'],
      1  : {
         'READER_HEATER': 0xC0C5,
         '*'            : 0x80C5,
      },
      2  : {
         'READER_HEATER': 0xC1C5,
         '*'            : 0x81C5,
      },
      3  : {
         'READER_HEATER': 0x41C0,
         '*'            : 0x01C0,
      },
      4  : {
         'READER_HEATER': 0xC1C0,
         '*'            : 0x81C0,
      },
      #25    : (0x0090,), #!!!???
      '*'   : {
         'READER_HEATER': 0x4180,
         '*'            : 0x0180,
      },
   },
   'CONTACT_LIMITS'  : {
      'ACCESS_ORDER' : ['AABType'],
      '?'      : '"%s" in ["26YR4","25AS2","25AS2M2","25AS2M3"]',
      'True'   : [0x640C, 4356, 258, 0x3832, -160, 160, 6164,],   # open wirp limit to (56, 50)
      'False'  : [0x640C, 4356, 258, 10788, -160, 160, 6164,],
   },
   'DAC_RANGE'    : {
      'ACCESS_ORDER' : ['programName'],
      'M10P'   : {
         'ACCESS_ORDER'    : ['P_DC_DETCR_DSA_CONTACT_DETECTION'],
         1        : (-70,0xF064,30),
         '*'      : (-20, 30, 20),
      },
      '*'      : {
         'ACCESS_ORDER' : ['AABType', 'heaterElement'],
         '?'      : '"%s" in ["H_25CA1","2112-BP07","500.00","500.06","500.26","501.00","501.02","501.11","501.12","501.14","501.16","501.25","501.30","501.32","501.41","501.03","501.04","501.05","500.03"]',
         'True'   : {
            'READER_HEATER': (-20, 0x461E, 20),
            '*'            : (-20, 30, 20),
         },
         'False'  : {
            'READER_HEATER': (-20, 0x6432, 20),
            '*'            : (-20, 50, 20),
         },
      }
   },
   'CLEARANCE_CONSISTENCY_LIMIT' : (70, 90, 50),
   'TEST_LIMITS_5'   : {
      'ACCESS_ORDER' : ['AFH_State'],
      1     : [1025, 1283, 15000, 0, 0,],    # (Low points/Low order, High points/High order, Extrapolation limit,  Not used, Not used)
      2     : [7682, 8195, 0, 0, 0,],        # (Low points/Low order, High points/High order, Extrapolation limit,  Not used, Not used)
      4     : [7682, 8195, 0, 0, 0,],        # (Low points/Low order, High points/High order, Extrapolation limit,  Not used, Not used)
      '*'   : [0xFF01, 0xFF03, -999, 0, 0,], # (Low points/Low order, High points/High order, Extrapolation limit,  Not used, Not used)
   },
   'MAX_MIN_DELTA'   : {
      'ACCESS_ORDER' : ['AABType'],
         '?'      : '"%s" in ["501.00","501.02","501.11","501.12","501.14","501.16","501.25","501.30","501.32","501.41","501.03","501.04","501.05","500.03"]',
         'True'   : {
            'ACCESS_ORDER' : ['programName'],
            'M10P'         : {
               'ACCESS_ORDER'    : ['P_DC_DETCR_DSA_CONTACT_DETECTION'],
               1        : (90, 160),
               '*'      : (70, 150),
            },
            '*'            : (70, 90),
         },
         'False'  : (70, 90),
   },
   'HEATER'          : (0x0FAA, 0x0103),
   'READ_HEAT'       : (170,),
   # may not have
   'AGC_HIT_LIMIT'   : {
      'ACCESS_ORDER' : ['IPD3SettingUsed'],
      1  : {
         'ACCESS_ORDER' : ['AGC_BASELINE_JUMP_DETECTION'],
         1  : {
            'ACCESS_ORDER' : ['programName'],
            'Rosewood7' : None,
            '*'         : (1300,5),
         },
      },
   },
   'DUAL_HEATER_CONTROL'   : {
      # SHD for dual heater 1st parameter 0=Write 1=Read heater, 2nd parameter in - active
      'ACCESS_ORDER' : ['isDriveDualHeater', 'heaterElement'],
      1     : {
         'WRITER_HEATER'   : (0, 0x0000),    # 0 = Write  (old traditional path)
         'READER_HEATER'   : (1, 0x0000),    # 1 = reader heater (new)
      },
   },
   'DC_DETCR'        : {
      'ACCESS_ORDER' : ['LFACH_AFH_CONTACT_DETECTION'],
      1     : {
         'ACCESS_ORDER' : ['heaterElement'],
         'READER_HEATER': (0x8009, 480, 10, 0x100, 0, 0xFC87, 5, 0xFFFB, 30, 0),
         '*'            : (0x8001, 480, 10, 0x100, 0, 0xFC87, 5, 0xFFFB, 30, 0),
      },
      '*'   : {
         'ACCESS_ORDER' : ['P_DC_DETCR_DSA_CONTACT_DETECTION'],
         1     : (0x8011, 90*64, 10, 256, 8, 5, 0, 44, 0, 0, 80),
      },
   },
   'DETCR_DETECTOR'  : {
      'ACCESS_ORDER' : ['LFACH_AFH_CONTACT_DETECTION'],
      1     : (0x0071, 0x0708, 0x0007, 0x00DC, 0x0003, 0x0000, 0x0003, 0x0000, 0x0000, 0x0000),
      '*'   : {
         'ACCESS_ORDER' : ['P_DC_DETCR_DSA_CONTACT_DETECTION'],
         1     : (0x71, 1800, 7, 220, 3, 0, 0, 20, 0, 0),
      },
   },
   'DETECTOR_BIT_MASK'  : {
      'ACCESS_ORDER' : ['AFH_64ZONES_T135_SQUEEZE_PARAM'],
      1  : {
         'ACCESS_ORDER' : ['P_DC_DETCR_DSA_CONTACT_DETECTION'],
         1  : (0xFFFF, 0xFFFF,   # detector 1 bit mask: TDA PES
               0xFFFF, 0xFFFF,   # detector 2 bit mask: SF3 bug makes this apply to detector 4 (LFACH_DSA)
               0x0000, 0x0000,   # detector 3 bit mask: SF3 bug makes this apply to detector 5
               0x0000, 0x0000,   # detector 4 bit mask: SF3 bug makes this apply to detector 6
               0x0000, 0x0000,   # detector 5 bit mask: LF PES
               0xFFFF, 0xFFFF,   # detector 6 bit mask: VCM (DC DETCR)
         ),
         0  : {
            'ACCESS_ORDER' : ['programName'],
            'M10P'      : (0xFFFF, 0xFFFF,   # detector 1 bit mask: TDA PES
                           0xFFFF, 0xC000,   # detector 2 bit mask: SF3 bug makes this apply to detector 4
                           0xFFFF, 0xFFFF,   # detector 3 bit mask: SF3 bug makes this apply to detector 5
                           0x0000, 0x0000,   # detector 4 bit mask: SF3 bug makes this apply to detector 6
                           0xFFFF, 0xFFFF,   # detector 5 bit mask: LF PES
                           0xFFFF, 0xFFFF,   # detector 6 bit mask: VCM
            ),
            '*'         : (0xFFFF, 0xFFFF,   # detector 1 bit mask: TDA PES
                           0xFFFF, 0xC000,   # detector 2 bit mask: SF3 bug makes this apply to detector 4
                           0xFFFF, 0xFFFF,   # detector 3 bit mask: SF3 bug makes this apply to detector 5
                           0xFFFF, 0xC000,   # detector 4 bit mask: SF3 bug makes this apply to detector 6
                           0xFFFF, 0xFFFF,   # detector 5 bit mask: LF PES
                           0xFFFF, 0xFFFF,   # detector 6 bit mask: VCM,
            ),
         },
      },
      0  : {
         'ACCESS_ORDER' : ['LFACH_AFH_CONTACT_DETECTION'],
         1  : (0xFFFF, 0xFFFF,
               0xFFFF, 0xFFFF,
               0xFFFF, 0xFFFF,
               0x000F, 0xFF80,
               0xFFFF, 0xFFFF,
               0xFFFF, 0xFFFF,
         ),
         0  : {
            'ACCESS_ORDER' : ['headType'],
            # 25-AUG-11
            'RHO' : (0xFFFF, 0xFFFF,   # detector 1 bit mask: TDA PES
                     0x000F, 0xFF80,   # detector 2 bit mask: SF3 bug makes this apply to detector 4
                     0xFFFF, 0xFFFF,   # detector 3 bit mask: SF3 bug makes this apply to detector 5
                     0x000F, 0xFF80,   # detector 4 bit mask: SF3 bug makes this apply to detector 6
                     0xFFFF, 0xFFFF,   # detector 5 bit mask: LF PES
                     0xFFFF, 0xFFFF,   # detector 6 bit mask: VCM
            ),
            'TDK' : (0xFFFF, 0xFFFF,   # detector 1 bit mask: TDA PES
                     0x000F, 0xFF80,   # detector 2 bit mask: FDA AGC
                     0xFFFF, 0xFFFF,   # detector 3 bit mask: FDA PES
                     0x000F, 0xFF80,   # detector 4 bit mask: TDA AGC
                     0xFFFF, 0xFFFF,   # detector 5 bit mask: LF PES
                     0xFFFF, 0xFFFF,   # detector 6 bit mask: VCM
            ),
            'HWY' : (0xFFFF, 0xFFFF,   # detector 1 bit mask: TDA PES
                     0x000F, 0xFF80,   # detector 2 bit mask: FDA AGC
                     0xFFFF, 0xFFFF,   # detector 3 bit mask: FDA PES
                     0x000F, 0xFF80,   # detector 4 bit mask: TDA AGC
                     0xFFFF, 0xFFFF,   # detector 5 bit mask: LF PES
                     0xFFFF, 0xFFFF,   # detector 6 bit mask: VCM
            ),
         },
      },
   },
   'AGC_RETRY_ZONES_EXT': {
      'ACCESS_ORDER' : ['AFH_64ZONES_T135_SQUEEZE_PARAM'],
      1  : (0,0),
   },
   'PES_RETRY_ZONES_EXT': {
      'ACCESS_ORDER' : ['AFH_64ZONES_T135_SQUEEZE_PARAM'],
      1  : (0,0),
   },
   'DETECTOR_BIT_MASK_EXT'    : {
      'ACCESS_ORDER' : ['AFH_64ZONES_T135_SQUEEZE_PARAM'],
      1  : {
         'ACCESS_ORDER' : ['P_DC_DETCR_DSA_CONTACT_DETECTION'],
         1  : (0xFFFF, 0xFFFF,   # detector 1 bit mask: TDA PES LFACH PES)
               0xFFFF, 0xFFFF,   # detector 2 bit mask: SF3 bug makes this apply to detector 4(LFACH_DSA)
               0x0000, 0x0000,   # detector 3 bit mask: SF3 bug makes this apply to detector 5
               0x0000, 0x0000,   # detector 4 bit mask: SF3 bug makes this apply to detector 6
               0x0000, 0x0000,   # detector 5 bit mask: LF PES
               0xFFFF, 0xFFFF,   # detector 6 bit mask: VCM DC DETCR)
         ),
         0  : {
            'ACCESS_ORDER' : ['programName'],
            'M10P'      : (0xFFFF, 0xFFFF,   # detector 1 bit mask: TDA PES
                           0x0000, 0x00FF,   # detector 2 bit mask: SF3 bug makes this apply to detector 4
                           0xFFFF, 0xFFFF,   # detector 3 bit mask: SF3 bug makes this apply to detector 5
                           0x0000, 0x0000,   # detector 4 bit mask: SF3 bug makes this apply to detector 6
                           0xFFFF, 0xFFFF,   # detector 5 bit mask: LF PES
                           0xFFFF, 0xFFFF,   # detector 6 bit mask: VCM
            ),
            '*'         : (0xFFFF, 0xFFFF,   # detector 1 bit mask: TDA PES
                           0x0000, 0x00FF,   # detector 2 bit mask: SF3 bug makes this apply to detector 4
                           0xFFFF, 0xFFFF,   # detector 3 bit mask: SF3 bug makes this apply to detector 5
                           0x0000, 0x00FF,   # detector 4 bit mask: SF3 bug makes this apply to detector 6
                           0xFFFF, 0xFFFF,   # detector 5 bit mask: LF PES
                           0xFFFF, 0xFFFF,   # detector 6 bit mask: VCM,
            ),
         },
      },
   },
   # IPD2_BIT_INDEX, DETCR_BIT_INDEX & DETECTOR_BIT_INDEX follows SHORT_ZONE_ORDER. Each bit represent the zone in SHORT_ZONE_ORDER.
   # For exmple for 180 zone, first 8 zones are 156, 24, 84, 48, 132, 72, 0, 179.
   # Bit 0 of IPD2_BIT_INDEX, DETCR_BIT_INDEX & DETECTOR_BIT_INDEX represent the bit mask for zone 156.
   # Bit 1 of IPD2_BIT_INDEX, DETCR_BIT_INDEX & DETECTOR_BIT_INDEX represent the bit mask for zone 24, and so on.
   'IPD2_BIT_INDEX'     : {
      'ACCESS_ORDER' : ['AABType'],
      '*'      : (0, 255),
      '501.12' : (0x000, 0x3FF),
      '501.16' : (0x000, 0x3FF),
      '501.41' : (0x000, 0x3FF),
   },
   'DETCR_BIT_INDEX'    : {
      'ACCESS_ORDER' : ['AABType'],
      '*'      : (0, 255),
      '501.12' : (0x000, 0x3FF),
      '501.16' : (0x000, 0x3FF),
      '501.41' : (0x000, 0x3FF),
      '501.42' : {
         'ACCESS_ORDER' : ['AFH_State'],
         '*'   : (0x000, 0x0FF),
         4     : (0x000, 0x000),
      },
   },
   'DETECTOR_BIT_INDEX' : {
      'ACCESS_ORDER' : ['ZONE_MASK_BANK_SUPPORT'],
      1  : (0, 0xFF, 0, 0x34, 0, 0xFF, 0, 0x34, 0, 0xFF, 0, 0xFF),
   },
   # For FAFH
   'CWORD3' : {
      'ACCESS_ORDER' : ['enableFAFH', 'AFH_State', 'AFH3_TO_IMPROVE_TCC'],
      1     : {
         2     : {1  : 0x0002,   '*': 0x0000},
         '*'   : {'*': 0x0000},
      },
   },
   'CERT_TEMPERATURE'   : {
      'ACCESS_ORDER' : ['enableFAFH', 'AFH_State', 'AFH3_TO_IMPROVE_TCC'],
      1     : {
         2     : {1  : 0},
         3     : {'*': 0},
         4     : {'*': 1},
      },
   },
   'TRGT_RD_CLEARANCE'  : {
      'ACCESS_ORDER' : ['T135_RAP_CONSISTENCY_CHECK', 'AFH_State'],
      1     : {
         2     : 0x000F,
         '*'   : 0x0000,
      },
   },
   'TRGT_WR_CLEARANCE'  : {
      'ACCESS_ORDER' : ['T135_RAP_CONSISTENCY_CHECK', 'AFH_State'],
      1     : {
         2     : 0x000F,
         '*'   : 0x0000,
      },
   },
}

full_baseIPD2Prm_135_update2 = {
   'ACCESS_ORDER' : ['member'],
   'DESPORT_DEGREE'     : {
      'ACCESS_ORDER' : ['programName'],
      'M10P'      : {
         'ACCESS_ORDER' : ['headType'],
         '?'      : '"%s" in ["TDK","HWY"]',
         'True'   : 3,
         'False'  : {
            'ACCESS_ORDER'    : ['P_DC_DETCR_DSA_CONTACT_DETECTION'],
            1        : 3,
            '*'      : 2,
         },
      },
      'Rosewood7' : 3,
      '*'         : {
         'ACCESS_ORDER' : ['AABType'],
         '?'      : '"%s" in ["2112-BP07","500.00","500.06","500.26"]',
         'True'   : {
            'ACCESS_ORDER' : ['AFH_State'],
            '?'      : '%s in [1,2,4]',
            'True'   : 2,
            'False'  : 3,
         },
         'False'  :  3,
      },
   },
   'FIT_DEGREE'         : {
      'ACCESS_ORDER' : ['AABType'],
      '501.12' : 3,
      '501.16' : 3,
      '501.41' : 3,
      '*'      : 2,
   },
   'DESPORT_THRESHOLD'  : {
      'ACCESS_ORDER' : ['programName'],
      'M10P'      : {
         'ACCESS_ORDER' : ['headType'],
         '?'      : '"%s" in ["TDK","HWY"]',
         'True'   : 300,
         'False'  : 200,
      },
      '*'         : 300,      # Head Media official release (24-Jul-13)
   },
   'MIN_POINT'          : 4,
   'EXTRAPOLATION_LIMIT': {
      'ACCESS_ORDER' : ['programName'],
      'Rosewood7' : {
         'ACCESS_ORDER' : ['numZones'],
         150   : 55000,
         '*'   : 52000,
      },
      '*'         : 38000,      # Head Media official release (16-Oct-12)
   },
   'STANDARD_DIVISION'  : 10000,
   'MAX_PREDICT_INTERVAL'  : 1000,
   'SPECTRAL_DETECTOR_0'   : (201, 0x3889, 0, 169, 201, 649),
   'SPECTRAL_DETECTOR_1'   : (1, 1, 0, 1, 1, 1),
   'SPECTRAL_DETECTOR_2'   : (3614, 1, 0, 3614, 3614, 3614),
   'SPECTRAL_DETECTOR_3'   : (650, 0x190, 0, 650, 650, 650),
   'SPECTRAL_DETECTOR_4'   : (1, 1, 0, 1, 1, 1),
   'SPECTRAL_DETECTOR_5'   : {
      'ACCESS_ORDER' : ['IPD3SettingUsed'],
      1  : (0x1421, 1, 0, 0x1421, 0x1421, 0x1421),
      0  : (0x0431, 1, 0, 0x0431, 0x0431, 0x0431),
   },
   'SPECTRAL_DETECTOR_6'   : {
      'ACCESS_ORDER' : ['IPD3SettingUsed'],
      1  : {
         'ACCESS_ORDER' : ['intHeadRetryCntr', 'AGC_BASELINE_JUMP_DETECTION'],
         3  : {
            1  : (0x8, 1, 0, 0x2008, 0x8, 0x8),
            '*': (0x8, 1, 0, 0x8, 0x8, 0x8)
         },
         '*': {
            1  : (1, 1, 0, 0x2008, 4, 16),
            '*': (1, 1, 0, 16, 4, 16),
         },
      },
      0  : (1, 1, 0, 16, 4, 16),
   },
   'SPECTRAL_DETECTOR_7'   : (1, 1, 0, 2, 4, 1),
   'SPECTRAL_DETECTOR_8'   : {
      'ACCESS_ORDER' : ['IPD3SettingUsed'],
      1  : {
         'ACCESS_ORDER' : ['intHeadRetryCntr'],
         2  : (0x8C5A, 0, 0, 0x735A, 0x825A, 0x825A),
         3  : (0x8C5A, 0, 0, 0x785A, 0x825A, 0x825A),
         '*': (0x8C5A, 0, 0, 0x6450, 0x825A, 0x825A),
      },
      0  : (0x8C5A, 0, 0, 0x6450, 0x825A, 0x825A),
   },
   'SPECTRAL_DETECTOR_9'   : (-1, -1, 0, -1, -1, -1),
}

full_baseIPD2Prm_135_DETCR_CD = {
   'ACCESS_ORDER' : ['member'],
   'band_pass_filter'   : {   # CTRL0 B15~B8 -- bit11..8 TI5551 LSI2935 filter,  bit13..8 TI5552 TI7551 TI7550 LSI5230 LSI5231 LSI5235 LSI5830 filter,
      'ACCESS_ORDER' : ['LFACH_AFH_CONTACT_DETECTION'],
      1  : 0x04,
      0  : {
         'ACCESS_ORDER' : ['preamp_vender', 'preamp_type'],
         'TI'  : {
            'TI5551' : {
               'ACCESS_ORDER' : ['preamp_rev'],
               '?'      : '%s >= 5',   # TI CAA Preamp
               'True'   : {
                  'ACCESS_ORDER' : ['headType', 'heaterElement'],
                  'RHO' : {
                     'WRITER_HEATER': 0x32,  # baseline filter set to 80k-2Mhz
                     '*'            : 0x22,  # CD filter set to 80k-500Khz
                  },
                  '*'   : {
                     '*'            : 0x22,
                  },
               },
               'False'  : 0x30,
            },
            'TI5552' : 0x02,  # bandpass 000010b
            'TI7550' : 0x02,
            'TI7551' : 0x02,
            '*'      : 0x30,
         },
         'LSI' : {
            'LSI5230': 0x02,
            'LSI5235': 0x02,
            'LSI5231': 0x02,
            'LSI5830': 0x02,
            '*'      : 0x32,
         },
      },
   },
   'bias_voltage'       : {   # CTRL0 B7~B0 -- bias for TI5551 LSI2935 TI5552 TI7550 LSI5230 LSI5231 LSI5235 LSI5830 filter
      'ACCESS_ORDER' : ['LFACH_AFH_CONTACT_DETECTION'],
      1  : 0xE0,
      0  : {
         'ACCESS_ORDER' : ['preamp_type'],
         '?'      : '([key for (key, value) in {"CASE1":["TI5552","LSI5230", ],"CASE2":["LSI5231","LSI5830","TI7550","TI7551"],"CASE3":["LSI2935","TI5551"],"CASE4":["LSI5235", ], }.items() if "%s" in value]+["CASE*"])[0]',
         'CASE1'  : {
            'ACCESS_ORDER' : ['headType', 'AFH_State', 'programName'],
            'RHO' : {
               '*'   : {'*'   : 0x17},
            },
            'TDK' : {
               '?'      : '%s in [1,2]',
               'True'   : {
                  'Angsana'   : 0x16,
                  'AngsanaH'  : 0x16,
                  'Angsana2D' : 0x16,
                  '*'         : 0x14,
               },
               'False'  : {
                  'Angsana'   : 0x16,
                  'AngsanaH'  : 0x16,
                  'Angsana2D' : 0x16,
                  '*'         : 0x12,
               },
            },
            'HWY' : {
               '?'      : '%s in [1,2]',
               'True'   : {'*'   : 0x14},
               'False'  : {'*'   : 0x12},
            },
         },
         'CASE2'  : {
            'ACCESS_ORDER' : ['headType', 'programName'],
            'RHO' : {
               'M10P'      : 0x30,
               '*'         : 0x28,
            },
            'TDK' : {
               'M10P'      : 0x2C,
               '*'         : 0x23,
            },
            'HWY' : {
               'M10P'      : 0x2C,
               '*'         : 0x25,
            },
         },
         'CASE3'  : {
            'ACCESS_ORDER' : ['programName'],
            'YarraR' : {
               'ACCESS_ORDER' : ['heaterElement', 'AABType'],
               'READER_HEATER': {
                  '?'      : '"%s" in ["501.00","501.02","501.11","501.12","501.14","501.16","501.25","501.30","501.32","501.41","501.03","501.04","501.05"]',
                  'True'   :  0x19,       # Target to trigger early by 2A on average
                  'False'  :  '!*',
               },
               '*'         : '!*',
            },
            '*'      : {
               'ACCESS_ORDER' : ['headType', 'AFH_State'],
               'RHO' : {
                  '*'      : 0x17,
               },
               'TDK' : {
                  '?'      : '%s in [1,2]',
                  'True'   : 0x14,
                  'False'  : 0x12,
               },
               'HWY' : {
                  '?'      : '%s in [1,2]',
                  'True'   : 0x14,
                  'False'  : 0x12,
               },
            },
         },
         'CASE4'  : {
            'ACCESS_ORDER' : ['headType', 'programName'],
            'RHO' : {
               'M10P'      : 0x30,
               '*'         : 0x1C,
            }, 
            'TDK' : {
               'M10P'      : 0x2C,
               '*'         : 0x1C,
            }, 
            'HWY' : {
               'M10P'      : 0x2C,
               '*'         : 0x1C,
            },
         },
         'CASE*'  : {
            'ACCESS_ORDER' : ['headType', 'AFH_State'],
            'RHO' : {
               '*'      : 0x17,
            },
            'TDK' : {
               '?'      : '%s in [1,2]',
               'True'   : 0x14,
               'False'  : 0x12,
            },
            'HWY' : {
               '?'      : '%s in [1,2]',
               'True'   : 0x14,
               'False'  : 0x12,
            },
         },
      },
   },
   'afh_setting_1'   : {      # CTRL1 B15~B8 bit 0x800 compare first two zones clearance against previous results, if delta > then bit10..8  then a full T135 will be performed otherwise stop and return.
      'ACCESS_ORDER' : ['LFACH_AFH_CONTACT_DETECTION'],
      1  : 0x00,
      0  : {
         'ACCESS_ORDER' : ['AFH_State'],
         3     : {
            'ACCESS_ORDER' : ['AFH3_TO_IMPROVE_TCC'],
            1     : 0x08 | 0x05,    # Re-AFH3 and 5A threshold
            '*'   : 0x00,
         },
         4     : {
            'ACCESS_ORDER' : ['AFH4_TO_USE_TWO_ZONES_TCC'],
            1     : 0x08,
            '*'   : 0x00,
         },
         '*'   : 0x00,
      },
   },
   'detcr_gain'      : {      # CTRL1 B7~B0 -- DETCR gain
      'ACCESS_ORDER' : ['LFACH_AFH_CONTACT_DETECTION'],
      1  : 0xE0,
      0  : {
         'ACCESS_ORDER' : ['preamp_vender'],
         'TI'  : {
            'ACCESS_ORDER' : ['preamp_type'],
            'TI5552' : 0x16,
            'TI7550' : {
               'ACCESS_ORDER' : ['programName', 'headType'],
               'M10P'   : {
                  'RHO'    : 0x15,
                  '*'      : 0x11,
               },
               '*'      : {
                  '*'      : 0x1F,
               },
            },
            'TI7551' : {
               'ACCESS_ORDER' : ['programName', 'headType'],
               'M10P'   : {
                  'RHO'    : 0x15,
                  '*'      : 0x11,
               },
               '*'      : {
                  '*'      : 0x1F,
               },
            },
            '*'      : 0x18,
         },
         'LSI' : {
            'ACCESS_ORDER' : ['preamp_type'],
            'LSI5230': 0x08,
            'LSI5235': 0x28,
            'LSI5231': {
               'ACCESS_ORDER' : ['programName'],
               'M10P'   : {
                  'ACCESS_ORDER' : ['headType'],
                  'RHO'    : 0x14,
                  '*'      : 0x11,
               },
               '*'      : {
                  'ACCESS_ORDER' : ['headType'],
                  'RHO'    : 0x17,
                  'TDK'    : {
                     'ACCESS_ORDER' : ['AFH_State'],
                     '?'      : '%s in [1,2]',
                     'True'   : 0x1F,
                     'False'  : 0x17,
                  },
                  'HWY'    : {
                     'ACCESS_ORDER' : ['AFH_State'],
                     '?'      : '%s in [1,2]',
                     'True'   : 0x1F,
                     'False'  : 0x17,
                  },
               },
            },
            'LSI5830': {
               'ACCESS_ORDER' : ['programName'],
               'M10P'   : {
                  'ACCESS_ORDER' : ['headType'],
                  'RHO'    : 0x14,
                  '*'      : 0x11,
               },
               '*'      : {
                  'ACCESS_ORDER' : ['headType'],
                  'RHO'    : 0x17,
                  'TDK'    : {
                     'ACCESS_ORDER' : ['AFH_State'],
                     '?'      : '%s in [1,2]',
                     'True'   : 0x1F,
                     'False'  : 0x17,
                  },
                  'HWY'    : {
                     'ACCESS_ORDER' : ['AFH_State'],
                     '?'      : '%s in [1,2]',
                     'True'   : 0x1F,
                     'False'  : 0x17,
                  },
               },
            },
            '*'      : {
               'ACCESS_ORDER' : ['headType'],
               'RHO'    : 0x14,
               'TDK'    : {
                  'ACCESS_ORDER' : ['AFH_State'],
                  '?'      : '%s in [1,2]',
                  'True'   : 0x18,
                  'False'  : 0x14,
               },
               'HWY'    : {
                  'ACCESS_ORDER' : ['AFH_State'],
                  '?'      : '%s in [1,2]',
                  'True'   : 0x18,
                  'False'  : 0x14,
               },
            },
         },
      },
   },
   'detcr_ctrl2'     : {      # CTRL2 B15~B0 -- bit[11..8] baseline fault count > revs * bit[11..8] then noise floor found. bit[7..6] map to blanking time bit[7..6] for TI5552 & TI5230, bit[5..0] start vth for baseline tuning
      'ACCESS_ORDER' : ['LFACH_AFH_CONTACT_DETECTION'],
      1  : 0x90CB,
      0  : {
         'ACCESS_ORDER' : ['preamp_type'],
         'TI5551' : {
            'ACCESS_ORDER' : ['preamp_rev'],
            '?'      : '%s >= 5',   # TI CAA Preamp
            'True'   : 0x611F,      # WPH & HO gap set to 6
            'False'  : 0x011F,
         },
         'TI5552' : {
            'ACCESS_ORDER' : ['headType'],
            'TDK' : {
               'ACCESS_ORDER' : ['programName'],
               '?'      : '"%s" in ["Angsana", "AngsanaH","Angsana2D"]',
               'True'   : 0x017F,      # set blanking time register 0x0F to 0xF
               'False'  : 0x011F,
            },
            '*'      : '!*',
         },
         'LSI5230': {
            'ACCESS_ORDER' : ['headType'],
            'TDK' : {
               'ACCESS_ORDER' : ['programName'],
               '?'      : '"%s" in ["Angsana", "AngsanaH","Angsana2D"]',
               'True'   : 0x017F,      # set blanking time register 0x0F to 0xF
               'False'  : 0x011F,
            },
            '*'      : '!*',
         },
         'LSI5235': {
            'ACCESS_ORDER' : ['headType'],
            'TDK' : {
               'ACCESS_ORDER' : ['programName'],
               '?'      : '"%s" in ["Angsana", "AngsanaH","Angsana2D"]',
               'True'   : 0x017F,      # set blanking time register 0x0F to 0xF
               'False'  : 0x011F,
            },
            '*'      : '!*',
         },
         '*'      : 0x011F,
      },
   },
   'detcr_ctrl3'     : {      # CTRL3 B15~B0 bit[15..8] if fault count > revs * bit[15..8] then declare contact, bit[7..0] baseline heater dac.
      'ACCESS_ORDER' : ['LFACH_AFH_CONTACT_DETECTION'],
      1  : 0xC106,
      0  : {
         'ACCESS_ORDER' : [ 'heaterElement'],
         'READER_HEATER': {
            'ACCESS_ORDER' : [ 'headType'],
            'RHO' : {
               'ACCESS_ORDER' : ['programName'],
               'YarraR'    : 0x0114,
               '*'         : 0x010F,
            },
            'HWY' : {
               'ACCESS_ORDER' : ['programName'],
               'YarraR'    : 0x0114,
               '*'         : 0x0F0F,
            },
            '*'   : 0x010F,
         },
         'WRITER_HEATER': {
            'ACCESS_ORDER' : [ 'headType'],
            'RHO' : {
               'ACCESS_ORDER' : ['programName'],
               'YarraR'    : 0x0114,
               '*'         : 0x040F,
            },
            'HWY' : {
               'ACCESS_ORDER' : ['programName'],
               'YarraR'    : 0x0114,
               '*'         : 0x0F0F,
            },
            '*'   : 0x040F,
         },
         '*' : 0x040F, 
      },
   },
   'write_current'   : {      # CTRL4 B15~B4 bit[15..12] wirte current, bit[11..8] write damping, bit[7..4] write damping duration, bit[3..0] w+h vth back off from baseline noise for contact detction
      'ACCESS_ORDER' : ['LFACH_AFH_CONTACT_DETECTION'],
      1  : 0x01D,
      0  : {
         'ACCESS_ORDER' : ['programName'],
         'Rosewood7' : {
            'ACCESS_ORDER' : ['preamp_type'],
            '?'      : '"%s" in ["TI7551", "LSI5830"]',
            'True'   : { # 3G+ Preamp settings
               'ACCESS_ORDER' : ['AFH_State'],
               '?'      : '%s in [1,2,3,4]',
               'True'   : 0x000,    # read only to use same triplet as wph, so just set DETCR_CD word 5 bit[15..4] to 0
               'False'  : '!*',
            },
            'False' : {
               'ACCESS_ORDER' : ['AFH_State'],
               '?'      : '%s in [1,2]',
               'True'   : 0x000,    # AFH1 & AFH2 read only to use same triplet as wph, so just set DETCR_CD word 5 bit[15..4] to 0
               'False'  : '!*',
            }
         },
         '*'         : {
            'ACCESS_ORDER' : ['preamp_type'],
            '?'      : '"%s" in ["TI5552", "LSI5230", "LSI5235"]',
            'True'   : {
               'ACCESS_ORDER' : ['headType'],
               'TDK'       : {
                  'ACCESS_ORDER' : ['programName'],
                  '?'      : '"%s" in ["Angsana", "AngsanaH","Angsana2D"]',
                  'True'   : 0xD76,       # HO vth triplet to 13-7-6
                  'False'  : 0x846,
               },
               '*'         : 0x846,
            },
            'False'  : 0x846,
         },
      },
   },
   'threshold_backoff_4': {   # CTRL4 B3~B0
      'ACCESS_ORDER' : ['LFACH_AFH_CONTACT_DETECTION'],
      1  : 0x00,
      0  : {
         'ACCESS_ORDER' : ['preamp_type'],
         '?'      : '([key for (key, value) in {"CASE1":["TI5551"],"CASE2":["TI5552"],"CASE3":["LSI5230", "LSI5235"],"CASE4":["LSI5231","LSI5830","TI7550","TI7551"]}.items() if "%s" in value]+["CASE*"])[0]',
         'CASE1'  : {
            'ACCESS_ORDER' : ['preamp_rev'],
            '?'      : '%s >= 5',   # TI CAA Preamp
            'True'   : {
               'ACCESS_ORDER' : ['headType', 'heaterElement'],
               'RHO' : {
                  'READER_HEATER': 0x02,
                  '*'            : 0x03,
               },
               '*'   : {
                  '*'            : 0x03,
               },
            },
            'False'  : {
               'ACCESS_ORDER' : ['heaterElement'],
               'READER_HEATER': 0x03,
               '*'            : 0x02,
            },
         },
         'CASE2'  : {
            'ACCESS_ORDER' : ['headType'],
            'RHO' : {
               'ACCESS_ORDER' : ['programName'],
               'Angsana'   : {
                  'ACCESS_ORDER' : ['heaterElement'],
                  'READER_HEATER': 0x02,
                  '*'            : 0x08,
               },
               'AngsanaH'  : {
                  'ACCESS_ORDER' : ['heaterElement'],
                  'READER_HEATER': 0x02,
                  '*'            : 0x08,
               },
               'Angsana2D' : 0x05,
               '*'         : 0x02,
            },
            'TDK' : {
               'ACCESS_ORDER' : ['programName'],
               'Angsana'   : 0x05,
               'AngsanaH'  : 0x05,
               'Angsana2D' : 0x05,
               '*'         : 0x03,
            },
            '*'   : {
               'ACCESS_ORDER' : ['heaterElement'],
               'READER_HEATER': 0x03,
               '*'            : 0x02,
            },
         },
         'CASE3'  : {
            'ACCESS_ORDER' : ['headType'],
            'RHO' : 0x04,
            'TDK' : 0x04,
            '*'   : 0x04,
         },
         'CASE4'  : {
            'ACCESS_ORDER' : ['headType'],
            'RHO' : {
               'ACCESS_ORDER' : ['programName'],
               'M10P'      : 0x06,
               '*'         : 0x04,
            },
            'HWY' : {
               'ACCESS_ORDER' : ['programName', 'preamp_type'],
               'M10P'      : {
                  '*'      : 0x06,
               },
               '*'         : {
                  'TI7550' : 0x05,
                  'TI7551' : 0x04,
                  '*'      : 0x04,
                  },
            },
            '*'   : 0x03,
         },
         'CASE*'  : {
            'ACCESS_ORDER' : ['preamp_vender', 'headType', 'heaterElement'],
            'TI'  : {
               '*'   : {
                  'READER_HEATER': 0x03,     # Ti5551 backoff 3 count for reader heater
                  '*'            : 0x02,
               },
            },
            'LSI' : {
               'RHO' : {
                  'READER_HEATER': 0x03,     # Ti5551 backoff 3 count for reader heater
                  '*'            : 0x02,
               },
               '*'   : 0x03,
            },
         },
      },
   },
   'afh_setting_5'   : {      # CTRL5 B15~B4
      # CTRL5_EXTREM_OD_LIMIT_POLYFIT_DAC_DELTA         (0x8000) -- extrem OD/ID use measured contact dac instead of polyfit contact dac
      #
      # CTRL5_MD_ZOMES_NOT_USE_HALF_CD_THRESHOLD        (0x2000)  -- less sensitive MD zone use 1/2 of number of fault count of OD/ID zone to declare contact
      # CTRL5_DETCR_RD_USE_WPH_THRESHOLD                (0x1000)  -- no longer in use
      # CTRL5_DETCR_DEBUG_PRINT                         (0x0800)  -- print debug information
      # CTRL5_DETCR_RO_USE_AFH1_WPH_THRESHOLD_IN_RAP    (0x0400)  -- no longer in use
      # CTRL5_DETCR_RO_TO_USE_WPH_TRIPLET               (0x0200)  -- baseline tuing readonly to use W+H triplet
      # CTRL5_DETCR_DYNAMIC_CD_THRESHOLD                (0x0100) -- if slow avalanche, DETCR fault count > average of previous 3 fault count + 15 then declare contact
      # CTRL5_DETCR_REPORT_HEATER_FROM_ZERO             (0x0080) -- debug purpose, start heater dac from 0 instead of interpolated value
      # CTRL5_DETCR_BASELINE_TA_MODE                    (0x0040) -- baseline tuing in TA mode instead of CD mode
      'ACCESS_ORDER' : ['LFACH_AFH_CONTACT_DETECTION'],
      1  : 0x138,
      0  : {
         'ACCESS_ORDER' : ['preamp_type'],
         'TI5551' : {
            'ACCESS_ORDER' : ['preamp_rev', 'AFH_State', 'programName', 'headType'],
            '?'      : '%s >= 5',   # TI CAA Preamp
            'True'   : {
               1  : {
                  '?'      : '"%s" in ["YarraR", "Angsana", "AngsanaH"]',
                  'True'   : {
                     'RHO' : {
                        'ACCESS_ORDER' : ['heaterElement'],
                        'READER_HEATER': 0x234,    # TA mode baseline
                        '*'            : 0x230,
                     },
                     'TDK' : 0x630,    # enable T135 to use 5% trk at extreme ID/OD. need SF3 support.
                     '*'   : 0x230,
                  },
                  'False'  : 0x230,
               },
               2  : {
                  '?'      : '"%s" in ["YarraR", "Angsana", "AngsanaH"]',
                  'True'   : {
                     'RHO' : {
                        'ACCESS_ORDER' : ['heaterElement'],
                        'READER_HEATER': 0x254,    # TA mode baseline
                        '*'            : 0x250,
                     },
                     'TDK' : 0x650,    # enable T135 to use 5% trk at extreme ID/OD. need SF3 support.
                     '*'   : 0x250,
                  },
                  'False'  : 0x250,
               },
               '*': {
                  '?'      : '"%s" in ["YarraR", "Angsana", "AngsanaH"]',
                  'True'   : {
                     'RHO' : {
                        'ACCESS_ORDER' : ['heaterElement'],
                        'READER_HEATER': 0x214,    # TA mode baseline
                        '*'            : 0x210,
                     },
                     'TDK' : 0x610,    # enable T135 to use 5% trk at extreme ID/OD. need SF3 support.
                     '*'   : 0x210,
                  },
                  'False'  : 0x210,
               },
            },
            'False'  : '!*',
         },
         '*'      : {
            'ACCESS_ORDER' : ['AFH_State', 'programName'],
            1  : {
               '?'      : '"%s" in ["YarraR", "Angsana", "AngsanaH"]',
               'True'   : {
                  'ACCESS_ORDER' : ['headType'],
                  'TDK'          : 0x630,    # Ti5551 backoff 3 count for reader heater
                  '*'            : 0x230,
               },
               'False'  : {
                  'ACCESS_ORDER' : ['preamp_type', 'programName'],
                  '?'      : '"%s" in ["LSI5830","TI7551"]',
                  'True'   : {
                     'M10P' : 0x230,
                     '*'    : 0x210,
                  },
                  'False'  : 0x230,
               }
            },
            2  : {
               '?'      : '"%s" in ["YarraR", "Angsana", "AngsanaH"]',
               'True'   : {
                  'ACCESS_ORDER' : ['headType'],
                  'TDK'          : 0x650,    # Ti5551 backoff 3 count for reader heater
                  '*'            : 0x250,
               },
               'False'  : 0x250,
            },
            '*': {
               '?'      : '"%s" in ["YarraR", "Angsana", "AngsanaH"]',
               'True'   : {
                  'ACCESS_ORDER' : ['headType'],
                  'TDK'          : 0x610,    # Ti5551 backoff 3 count for reader heater
                  '*'            : 0x210,
               },
               'False'  : 0x210,
            },
         },
      },
   },
   'threshold_backoff_5': {   # CTRL5 B3~B0 vth back off from baseline noise floor for read only
      'ACCESS_ORDER' : ['LFACH_AFH_CONTACT_DETECTION'],
      1  : 0x04,
      0  : {
         'ACCESS_ORDER' : ['preamp_type'],
         '?'      : '([key for (key, value) in {"CASE1":["TI5551"],"CASE2":["TI5552"],"CASE3":["LSI5230", ],"CASE4":["LSI5231","TI7550"],"CASE5":["LSI5830","TI7551"],"CASE6":["LSI5235",]}.items() if "%s" in value]+["CASE*"])[0]',
         'CASE1'  : {
            'ACCESS_ORDER' : ['preamp_rev'],
            '?'      : '%s >= 5',   # TI CAA Preamp
            'True'   : {
               'ACCESS_ORDER' : ['headType', 'heaterElement'],
               'RHO' : {
                  'READER_HEATER': 0x02,
                  '*'            : 0x03,
               },
               '*'   : {
                  '*'            : 0x03,
               },
            },
            'False'  : {
               'ACCESS_ORDER' : ['heaterElement'],
               'READER_HEATER': 0x03,
               '*'            : 0x02,
            },
         },
         'CASE2'  : {
            'ACCESS_ORDER' : ['headType'],
            'RHO' : {
               'ACCESS_ORDER' : ['programName'],
               'Angsana'   : 0x0A,
               'AngsanaH'  : 0x0A,
               'Angsana2D' : 0x06,
               '*'         : {
                  'ACCESS_ORDER' : ['heaterElement'],
                  'READER_HEATER': 0x03,
                  '*'            : 0x02,
               },
            },
            'TDK' : {
               'ACCESS_ORDER' : ['programName'],
               '?'      : '"%s" in ["Angsana", "AngsanaH","Angsana2D"]',
               'True'   : 0x06,
               'False'  : 0x03,
            },
            '*'   : {
               'ACCESS_ORDER' : ['heaterElement'],
               'READER_HEATER': 0x03,
               '*'            : 0x02,
            },
         },
         'CASE3'  : {
            'ACCESS_ORDER' : ['headType'],
            'RHO' : {
               'ACCESS_ORDER' : ['heaterElement'],
               'READER_HEATER': 0x06,
               '*'            : 0x08,
            },
            'TDK' : 0x08,
            '*'   : {
               'ACCESS_ORDER' : ['heaterElement'],
               'READER_HEATER': 0x03,
               '*'            : 0x02,
            },
         },
         'CASE4'  : {
            'ACCESS_ORDER' : ['headType'],
            'RHO' : {
               'ACCESS_ORDER' : ['programName', 'heaterElement'],
               'M10P'      : {
                  'READER_HEATER': 0x0C,
                  '*'            : 0x08,
               },
               '*'         : {
                  'READER_HEATER': 0x08,
                  '*'            : 0x0F,
               },
            },
            'HWY' : {
               'ACCESS_ORDER' : ['programName'],
               'M10P'      : {
                  'ACCESS_ORDER' : ['heaterElement'],
                  'READER_HEATER': 0x08,
                  '*'            : 0x07,
               },
               '*'         : {
                  'ACCESS_ORDER' : ['preamp_type', 'heaterElement'],
                  'TI7550' : {
                     'READER_HEATER': 0x06,
                     '*'            : 0x06,
                  },
                  '*'      : {
                     'READER_HEATER': 0x06,
                     '*'            : 0x0F,
                  },
               },
            },
            '*'   : {
               'ACCESS_ORDER' : ['programName', 'heaterElement'],
               'M10P'      : {
                  'READER_HEATER': 0x08,
                  '*'            : 0x07,
               },
               '*'         : {
                  'READER_HEATER': 0x06,
                  '*'            : 0x05,
               },
            },
         },
         'CASE5'  : {
            'ACCESS_ORDER' : ['headType'],
            'RHO' : {
               'ACCESS_ORDER' : ['programName', 'heaterElement'],
               'M10P'      : {
                  'READER_HEATER': 0x0C,
                  '*'            : 0x08,
               },
               '*'         : {
                  'READER_HEATER': 0x08,
                  '*'            : 0x08,
               },
            },
            'HWY' : {
               'ACCESS_ORDER' : ['programName'],
               'M10P'      : {
                  'ACCESS_ORDER' : ['heaterElement'],
                  'READER_HEATER': 0x08,
                  '*'            : 0x07,
               },
               '*'         : {
                  'ACCESS_ORDER' : ['preamp_type', 'heaterElement'],
                  'TI7551' : {
                     'READER_HEATER': 0x06,
                     '*'            : 0x08,
                  },
                  '*'      : {
                     'READER_HEATER': 0x06,
                     '*'            : 0x08,
                  },
               },
            },
            '*'   : {
               'ACCESS_ORDER' : ['programName', 'heaterElement'],
               'M10P'      : {
                  'READER_HEATER': 0x08,
                  '*'            : 0x07,
               },
               '*'         : {
                  'READER_HEATER': 0x06,
                  '*'            : 0x05,
               },
            },
         },
         'CASE6'  : {
            'ACCESS_ORDER' : ['headType'],
            'RHO' : {
               'ACCESS_ORDER' : ['programName', 'heaterElement'],
               'M10P'      : {
                  'READER_HEATER': 0x0C,
                  '*'            : 0x08,
               },
               '*'         : {
                  'READER_HEATER': 0x06,
                  '*'            : 0x08,
               },
            },
            'HWY' : {
               'ACCESS_ORDER' : ['programName'],
               'M10P'      : {
                  'ACCESS_ORDER' : ['heaterElement'],
                  'READER_HEATER': 0x08,
                  '*'            : 0x07,
               },
               '*'         : {
                  'ACCESS_ORDER' : ['preamp_type', 'heaterElement'],
                  'TI7551' : {
                     'READER_HEATER': 0x06,
                     '*'            : 0x06,
                  },
                  '*'      : {
                     'READER_HEATER': 0x06,
                     '*'            : 0x08,
                  },
               },
            },
            '*'   : {
               'ACCESS_ORDER' : ['programName', 'heaterElement'],
               'M10P'      : {
                  'READER_HEATER': 0x08,
                  '*'            : 0x07,
               },
               '*'         : {
                  'READER_HEATER': 0x06,
                  '*'            : 0x08,
               },
            },
         },
         'CASE*'  : {
            'ACCESS_ORDER' : ['heaterElement'],
            'READER_HEATER': 0x03,
            '*'            : 0x02,
         },
      },
   },
}


###################################################################################################################
def get_value_by_param_in_order(target, param, order = []):
   ret = {}
   members = target.keys()
   order = list(order)
   if 'ACCESS_ORDER' in members:
      members.remove('ACCESS_ORDER')
      order.extend(target['ACCESS_ORDER'])

   cur_order = order.pop(0)
   #print members
   if cur_order == 'member':
      for key in members:
         #print key
         if type(target[key]) is dict:
            ret_temp = get_value_by_param_in_order(target[key], param, order)
         else:
            ret_temp = target[key]
         if (ret_temp is not None) and (ret_temp != '!*'):
            ret[key] = ret_temp
   else:
      if param[cur_order] not in members:
         if '*' in members:
            new_target = target['*']
         elif '?' in members:
            temp = str(eval(target['?'] % str(param[cur_order])))
            if temp in members:
               new_target = target[temp]
            else:
               new_target = None
         else:
            new_target = None
      else:
         new_target = target[param[cur_order]]
      if type(new_target) is dict:
         ret_temp = get_value_by_param_in_order(new_target, param, order)
         if (ret_temp == '!*') and ('*' in members):
            if type(target['*']) is dict:
               ret_temp = get_value_by_param_in_order(target['*'], param, order)
               if ret_temp == '!*':
                  ret = None
               else:
                  ret = ret_temp
            else:
               ret = target['*']
         else:
            ret = ret_temp
      else:
         ret = new_target

   return ret


###################################################################################################################
#
#          Function:  getSelfTest135Dictionary
#
#   Original Author:  Michael T. Brady
#
#       Description:  Get the test 135 parameter dictionary
#
#           Purpose:  Provide a mechanism where test 135 dictionary can be set in 1 place with access
#                     to production process run-time attributes such as RPM and servoWedges without using
#                     Test Parameter Extractor.  This allows this same code to be run on the bench using WinFoF.
#
#             Input:  AFH_State,  1 for AFH1, 2 for AFH2 , etc.
#
#
#      Return Value:  baseIPD2Prm_135(dict)
#
###################################################################################################################
def getSelfTest135Dictionary( AFH_State,     intHeadRetryCntr,   programName,
                              heaterElement, iHead,              SpokesPerRev,
                              RPM,           headType,           AABType,
                              numZones,      isDriveDualHeater,  virtualRun,
                              benchMode,     enableFAFH,         iConsistencyCheckRetry,
                              preamp_type    = 'LSI2739',
                              preamp_rev     = 0, wafer_code = 'BZ7'):
#  AFH_State                  # AFH State number(integer).  =1 for AFH1, =2 for AFH2, etc.
#  intHeadRetryCntr           # Global head retry counter(integer).  = 0 for initial measurement, =1 for the 1st retry.
#  programName                # Program Name(string)  = "Trinidad", ="Grenada", etc.
#
#  heaterElement              # active heater element for contact detection(string) = "WRITER_HEATER" or "READER_HEATER"
#  iHead                      # logical head number being tested(integer).  For Bench testing, set this to 0.
#  SpokesPerRev               # number of servo wedges per track(integer)
#
#
#  RPM                        # RPM for the drive(integer)
#  headType                   # head vendor(string) = "RHO", "TDK", "HWY", etc.
#  AABType                    # Air bearing type(string)
#
#  numZones                   # number of logical zones(integer)
#  isDriveDualHeater          # enables dual heater contact detect(integer) = 0 for disable, =1 for enable
#  virtualRun                 # enable Process PF3 virtual exeution run.  = 0 for disable, = 1 for enable.  = 0 for real process and Bench level runs.

   import re

   # process input parameters
   param_in = {}
   programName = programName.split(".")[0]
   if virtualRun:
      SpokesPerRev   = 272
      RPM            = 7200  # you should strongly consider adding this so that the calculation is correct in VE mode
      if iHead == 0:
         headType    = 'RHO'
      else:
         headType    = 'TDK'

   # collect all the necessary switches
   from Test_Switches import testSwitch

   necessary_switch = [
                     'FE_AFH3_TO_IMPROVE_TCC',
                     'FE_AFH4_TO_USE_TWO_ZONES_TCC',
                     'FE_0166305_357263_T135_RAP_CONSISTENCY_CHECK',
                     'FE_0158916_357263_AGC_BASELINE_JUMP_DETECTION',
                     'FE_AFH4_TRACK_CLEAN_UP',
                     'FE_AFH_TO_USE_DC_DETCR_ONLY',
                     'FE_0184276_322482_AFH_64ZONES_T135_SQUEEZE_PARAM',
                     'FE_0245014_470992_ZONE_MASK_BANK_SUPPORT',
                     'extern.FE_0235757_322482_LFACH_AFH_CONTACT_DETECTION',
                     'FE_0274637_496738_P_DC_DETCR_DSA_CONTACT_DETECTION',
                     ]
   for item in necessary_switch:
      key = re.match('^(?:extern\.)?(?:FE_)?(?:\d+_)*(\w+)', item).groups()[0]
      try:
         if eval('testSwitch.%s' % (item)):
            param_in[key] = 1
         else:
            param_in[key] = 0
      except:
         param_in[key] = 0

   del testSwitch


   # collect all the parameters
   func_in = [
               'AFH_State',
               'intHeadRetryCntr',
               'programName',
               'heaterElement',
               'iHead',
               'SpokesPerRev',
               'RPM',
               'headType',
               'AABType',
               'numZones',
               'isDriveDualHeater',
               'virtualRun',
               'benchMode',
               'enableFAFH',
               'iConsistencyCheckRetry',
               'preamp_type',
               'preamp_rev',
               ]
   for item in func_in:
      param_in[item] = eval(item)

   SearchOptions  = get_value_by_param_in_order(full_SearchOptions, param_in)
   print 'SearchOptions', SearchOptions

   if (intHeadRetryCntr >= SearchOptions['IPDVersionToExecute'][1]) and (SearchOptions['IPDVersionToExecute'][0] == 3):
      param_in['IPD3SettingUsed'] = 1
   else:
      param_in['IPD3SettingUsed'] = 0

   if preamp_type.startswith('LSI'):
      param_in['preamp_vender'] = 'LSI'
   elif preamp_type.startswith('TI'):
      param_in['preamp_vender'] = 'TI'

   #print "param_in", param_in

   baseIPD2Prm_135 = {
      'test_num'                    : 135,
      'prm_name'                    : 'baseIPD2Prm_135',
      'timeout'                     : 25000,

      'HEAD_RANGE'                  : (0x0101),          # heads to test
      'ZONE_POSITION'               : (100,),            # Controls where within the zone to test ( 100 = 50% )
      'MAX_BASELINE_DAC'            : (20,),             # max baseline dac for dynamic threshold
      'AGC_RETRY_ZONES'             : (0x3FFF, 0xFFFF),  # if a bit is RESET here, AGC detectors will be shut off in that zone at the 4th retry
      'PES_RETRY_ZONES'             : (0x3FFF, 0xFFFF),  # if a bit is RESET here, PES detectors will be shut off in that zone at the 4th retry
      'BASELINE_REVS'               : (0x0508,),
      'CONTACT_VERIFY'              : (0x0201,),         # Retry verifies, initial verifies
      'DEBUG_PRINT'                 : (0x0230,),         # 19-SEP-11 Controls debug output
      'FINE_SEARCH_BACKUP'          : 8,
      'GAIN'                        : (7,),
      'MOVING_BACKOFF'              : (40,),             # Local-Reference Dac Backoff
   }

   SearchLimits   = get_value_by_param_in_order(full_SearchLimits, param_in)
   print 'SearchLimits', SearchLimits
   baseIPD2Prm_135_update2 = get_value_by_param_in_order(full_baseIPD2Prm_135_update2, param_in)
   print 'baseIPD2Prm_135_update2', baseIPD2Prm_135_update2
   detcr_cd = get_value_by_param_in_order(full_baseIPD2Prm_135_DETCR_CD, param_in)
   print 'detcr_cd', detcr_cd
   # update baseIPD2Prm_135
   baseIPD2Prm_135_update1 = get_value_by_param_in_order(full_baseIPD2Prm_135_update1, param_in)
   print 'baseIPD2Prm_135_update1', baseIPD2Prm_135_update1
   baseIPD2Prm_135.update(baseIPD2Prm_135_update1)

   # B_WR_NUM_WEDGES, E_POST_RD_NUM_WEDGES, Mx_FREQ_RANGE and SECTOR_RANGEx
   AGCTransient      =  12                                  # percentage of rev to discard from AGC to avoid heat transient effect
   WriteLength       =  90                                  # percentage of the rev to write/heat
   fastIO_B          = int(SpokesPerRev*WriteLength/100.0)  # set fastIO segment B to x percent of a rev
   AGCEndSpoke       = int(fastIO_B)                        # AGC detectors avoid spacing transient
   fastIO_E          = SpokesPerRev-fastIO_B                # set fastIO segment C to complete rev when added to B

   if param_in['P_DC_DETCR_DSA_CONTACT_DETECTION']:
      baseIPD2Prm_135["B_WR_NUM_WEDGES"]        = 384
      baseIPD2Prm_135['E_POST_RD_NUM_WEDGES']   = 0
   else:
      baseIPD2Prm_135['B_WR_NUM_WEDGES']        = (fastIO_B)
      baseIPD2Prm_135['E_POST_RD_NUM_WEDGES']   = (fastIO_E)

   #### optimize DFT length for PES
   # maximum DftN, fast DFT is most efficient for lengths that are multiples of 8
   PESDftN           = int(SpokesPerRev) & ~(0x7)
   #### optimize DFT length for AGC
   # maximum AGCDftN, fast DFT is most efficient for lengths that are multiples of 8
   AGCDftN           = (fastIO_B-int(AGCTransient/100.0*SpokesPerRev)) & ~(0x7)
   Nyquist           = RPM/120*SpokesPerRev
   PESFr             = RPM/60*SpokesPerRev/PESDftN
   AGCFr             = RPM/60*SpokesPerRev/AGCDftN
   LFPESFr           = RPM/60*SpokesPerRev/(SpokesPerRev-fastIO_B)

   if (intHeadRetryCntr and SearchOptions['ShutOffHighFreqDuringGlobalRetries']):
      EndFreq = int(10 * PESFr)
   else:
      EndFreq = int(Nyquist + PESFr)

   if param_in['IPD3SettingUsed'] and param_in['AGC_BASELINE_JUMP_DETECTION']:
      MinAGCBin = 0
      MinAGCBinWithBLJ = MinAGCBin+20                                                        # min AGC bin when a baseline jump is detected
      baseIPD2Prm_135['M5_FREQ_RANGE'] = (int(AGCFr*MinAGCBinWithBLJ),int(Nyquist + AGCFr))  # AGC when BLJ is detected       0x20

   if param_in['P_DC_DETCR_DSA_CONTACT_DETECTION']:
      baseIPD2Prm_135["M0_FREQ_RANGE"] = [90, 17370]
      baseIPD2Prm_135["M1_FREQ_RANGE"] = [11500, 11540]
      baseIPD2Prm_135["M2_FREQ_RANGE"] = [886, 18166]
      baseIPD2Prm_135["M3_FREQ_RANGE"] = [5700, 5800]
      baseIPD2Prm_135["M4_FREQ_RANGE"] = [0, 17370]
   else:
      baseIPD2Prm_135['M0_FREQ_RANGE'] = (int(PESFr),EndFreq)                                # Full spectra PES Freq Range    0x1
      baseIPD2Prm_135['M1_FREQ_RANGE'] = (int(AGCFr),int(Nyquist + AGCFr))                   # Full spectra AGC Freq Range    0x2
      baseIPD2Prm_135['M2_FREQ_RANGE'] = (int(LFPESFr),int(Nyquist + LFPESFr))               # Full spectra LF PES Freq Range 0x4
      baseIPD2Prm_135['M3_FREQ_RANGE'] = (int(AGCFr*10),int(Nyquist + AGCFr))                # AGC Freq Range sans LF         0x8
      baseIPD2Prm_135['M4_FREQ_RANGE'] = (0, EndFreq)                                        # Full spectra VCM Freq Range    0x10

   baseIPD2Prm_135['SECTOR_RANGE1'] = (SpokesPerRev - PESDftN,SpokesPerRev)                  # HF PES
   baseIPD2Prm_135['SECTOR_RANGE2'] = (AGCEndSpoke-AGCDftN,AGCEndSpoke)                      # AGC
   baseIPD2Prm_135['SECTOR_RANGE3'] = (fastIO_B , SpokesPerRev)                              # LF PES

   # CWORD1
   if AFH_State in [4] and param_in['AFH4_TRACK_CLEAN_UP']:
      baseIPD2Prm_135["CWORD1"]     |= 0x0008   # cleanup Formatted ACERASE all test tracks and +/-5tracks
   if (AFH_State in [3,4]) and SearchOptions['EnableCurveFitDuringTCSCal']:
      baseIPD2Prm_135["CWORD1"]     |= 0x2000   # turn on final curve fit
   if (programName in ['M10P']):
      baseIPD2Prm_135["CWORD1"]     |= 0x0080   # Test all heads even if one head fails
   if (isDriveDualHeater and not SearchOptions['RunReaderHeaterWPH'] and (heaterElement == "READER_HEATER")):
      baseIPD2Prm_135["CWORD1"] &= ~0x0400        # shut off bit that Run Heat-Only test after W+H

   # CWORD2
   if param_in['IPD3SettingUsed'] and param_in['AGC_BASELINE_JUMP_DETECTION']:
      baseIPD2Prm_135["CWORD2"]     |= 0x2000
   if SearchOptions['EnableCurveFitDuringTCSCal'] and (AFH_State in [3,4]):
      baseIPD2Prm_135["CWORD2"]     |= 0x0040 #turn on dual curve fit
   if AFH_State == 3:  #CWORD2_NO_NEW_TEST_TRK_FOR_OPTI_ZONE
      baseIPD2Prm_135["CWORD2"]     |= 0x8000
   
   if param_in['AFH3_TO_IMPROVE_TCC'] and AFH_State in [3,] :
      baseIPD2Prm_135["CWORD2"]     |= 0x8001
   # else: 
      # if AFH_State not in [4,]:        
         # baseIPD2Prm_135["CWORD2"]     |= 0x02 #save to flash

   # WRITE_TRIPLET
   if (isDriveDualHeater and not SearchOptions['RunReaderHeaterWPH'] and (heaterElement == "READER_HEATER")):
      baseIPD2Prm_135['WRITE_TRIPLET'] = (0, 0, 0)      # write triplet used during contact detect (WCA,OSA,OSW)
   elif (isDriveDualHeater and (heaterElement == "READER_HEATER")):
      baseIPD2Prm_135['WRITE_TRIPLET'] = (-1, -1, -1)      # set fixed high power write triplet for reader heater ,
   elif ((programName in ['M10P']) and (AFH_State==1) and (heaterElement == "WRITER_HEATER")):
      baseIPD2Prm_135['WRITE_TRIPLET'] = SearchOptions['AFH1_WriteTriplet']
   elif numZones not in [150]:
      baseIPD2Prm_135['WRITE_TRIPLET'] = (-1, -1, -1)   # write triplet used during contact detect (WCA,OSA,OSW)
   ###  V3BAR Destroking Parameters  ###
   if (AFH_State==25):
      baseIPD2Prm_135["WRITE_TRIPLET"] = ( 0, 0, 0,)           # set to 0 to force main detect to be heater only

   # TEST_LIMITS_5
   if AFH_State == 3:
      baseIPD2Prm_135['TEST_LIMITS_5'][2]=SearchLimits['MaxExtrapolationTracks']

   # SPECTRAL_DETECTOR
   pectral_detector = [baseIPD2Prm_135_update2['SPECTRAL_DETECTOR_%d' % (item)] for item in xrange(10)]
   if param_in['P_DC_DETCR_DSA_CONTACT_DETECTION']:
      baseIPD2Prm_135['SPECTRAL_DETECTOR2'] = [0x0289, 1, 0x0A3C, 170, 1, 0x0431, 0x08, 1, 0x8C5A, -1]
   if param_in['LFACH_AFH_CONTACT_DETECTION']:
      baseIPD2Prm_135['SPECTRAL_DETECTOR2'] = tuple([item[1] for item in pectral_detector])

   if not param_in['P_DC_DETCR_DSA_CONTACT_DETECTION'] and (not param_in['LFACH_AFH_CONTACT_DETECTION'] or not param_in['AFH_TO_USE_DC_DETCR_ONLY']):
      baseIPD2Prm_135["SPECTRAL_DETECTOR5"] = tuple([item[4] for item in pectral_detector])

   if param_in['P_DC_DETCR_DSA_CONTACT_DETECTION']:
      baseIPD2Prm_135["SPECTRAL_DETECTOR1"] = [0x00C9, 1, 0x0A3C, 300, 1, 0x0431, 0x08, 1, 0x8C5A, -1]
      baseIPD2Prm_135["SPECTRAL_DETECTOR6"] = [0x3889, 1, 0x0001, 400, 1, 0x0001, 0x01, 1, 0x0000, -1]
   if not param_in['LFACH_AFH_CONTACT_DETECTION'] or not param_in['AFH_TO_USE_DC_DETCR_ONLY']:
      baseIPD2Prm_135["SPECTRAL_DETECTOR1"] = tuple([item[0] for item in pectral_detector])
      baseIPD2Prm_135["SPECTRAL_DETECTOR6"] = tuple([item[5] for item in pectral_detector])
      if programName not in ['M10P']:
         baseIPD2Prm_135["SPECTRAL_DETECTOR4"] = tuple([item[3] for item in pectral_detector])

   # HEATER and READ_HEAT
   if heaterElement == "READER_HEATER":
      baseIPD2Prm_135["HEATER"] = (0x1EAA, 0x0103)
   if AABType in ["501.00","501.02","501.11","501.12","501.14","501.16","501.25","501.30","501.32","501.41","501.03","501.04","501.05","500.03"]:
       new_value = 200
       baseIPD2Prm_135["HEATER"] = ((baseIPD2Prm_135["HEATER"][0]&0xFF00|new_value), baseIPD2Prm_135["HEATER"][1])
       baseIPD2Prm_135["READ_HEAT"] = (200,)
   if param_in['IPD3SettingUsed']:
      if heaterElement == "READER_HEATER":
         baseIPD2Prm_135["HEATER"]  = ((baseIPD2Prm_135["HEATER"][0]&0x00FF|0x0F00), baseIPD2Prm_135["HEATER"][1])
   if param_in['LFACH_AFH_CONTACT_DETECTION']:
      baseIPD2Prm_135['HEATER'] = (0x0FFA, 0x0101)
      baseIPD2Prm_135['READ_HEAT'] = (250,)

   # REVS_BY_ZONE
   zone_list = list(SearchLimits['ZoneOrder'])
   from Test_Switches import testSwitch
   if preamp_type in ['LSI5235', ]:
      zone_list =  [118, 13, 133, 31, 93, 55, 0, 149,]
   if testSwitch.extern.FE_0327966_322482_ADAPTIVE_AFH_DETCR_BIAS and testSwitch.FE_0328298_305538_P_ENABLE_ADAPTIVE_AFH_DETCR_BIAS:
      zone_list =  [149,0,50,110,30,125,15,140,]
   if headType == 'HWY':
      baseIPD2Prm_135['FINE_SEARCH_BACKUP'] = 12
      zone_list =  [149, 0, 15, 134, 35, 114, 94, 55,]
   zone_list.extend([-1]*(32-len(zone_list)))
   baseIPD2Prm_135['ZONE_ORDER'] = zone_list
   baseIPD2Prm_135["REVS_BY_ZONE"] = [0x2314]*31 + [-1]*1 # change CD revs from 30 to 20
   if param_in['AFH_64ZONES_T135_SQUEEZE_PARAM']:
      #AFHParamAsPCFile = CAFHParamAsPCFile(baseIPD2Prm_135)
      #RegisterResultsCallback( AFHParamAsPCFile.Send64ZoneParamAsPCFile, [81,], 0)
      short_zone_order = 18
      baseIPD2Prm_135["SHORT_ZONE_ORDER"] = baseIPD2Prm_135["ZONE_ORDER"][:short_zone_order]
      baseIPD2Prm_135["SHORT_REVS_BY_ZONE"] = baseIPD2Prm_135["REVS_BY_ZONE"][:short_zone_order]
      del(baseIPD2Prm_135["ZONE_ORDER"])
      del(baseIPD2Prm_135["REVS_BY_ZONE"])

   # CURVE_FIT2
   baseIPD2Prm_135['CURVE_FIT2'] = [
                                    baseIPD2Prm_135_update2['DESPORT_DEGREE'],
                                    baseIPD2Prm_135_update2['FIT_DEGREE'],
                                    baseIPD2Prm_135_update2['DESPORT_THRESHOLD'],
                                    baseIPD2Prm_135_update2['MIN_POINT'],
                                    baseIPD2Prm_135_update2['EXTRAPOLATION_LIMIT'],
                                    baseIPD2Prm_135_update2['STANDARD_DIVISION'],
                                    baseIPD2Prm_135_update2['MAX_PREDICT_INTERVAL'],
                                    0]

   # DETCR_CD
   if preamp_type in ['LSI5235', ]:
      baseIPD2Prm_135['CURVE_FIT2'] = [3, 3, 300, 4, 55000, 10000, 1000, 0]
      baseIPD2Prm_135['DAC_RANGE'] = (-50, 17950, 20)  #(-20, 0x461E, 20)
      detcr_cd['afh_setting_5'] =  detcr_cd['afh_setting_5'] & 0xFFDF
      detcr_cd['write_current'] = 0      
      if wafer_code == 'BZ7':
         detcr_cd['bias_voltage'] = 0x15
         detcr_cd['afh_setting_1'] = 0x1F #####LC
         detcr_cd['threshold_backoff_4'] = 8
         detcr_cd['threshold_backoff_5'] = 12
         if heaterElement == "READER_HEATER":
            detcr_cd['threshold_backoff_5'] = 10
      if wafer_code == 'AL1':
         detcr_cd['bias_voltage'] = 0x57
         detcr_cd['afh_setting_1'] = 0x13 #####LC
         detcr_cd['threshold_backoff_4'] = 3
         detcr_cd['threshold_backoff_5'] = 10
         if heaterElement == "READER_HEATER":
            detcr_cd['threshold_backoff_5'] = 6

   if testSwitch.extern.FE_0327966_322482_ADAPTIVE_AFH_DETCR_BIAS and testSwitch.FE_0328298_305538_P_ENABLE_ADAPTIVE_AFH_DETCR_BIAS:
      baseIPD2Prm_135['CURVE_FIT2'] = [3, 3, 300, 4, 55000, 10000, 1000, 0]
      if headType == 'TDK':
         detcr_cd['bias_voltage'] = 0x28
         detcr_cd['threshold_backoff_4'] = 4
         detcr_cd['threshold_backoff_5'] = 8
         if heaterElement == "READER_HEATER":
            if AFH_State == 4:
               detcr_cd['threshold_backoff_5'] = 4
            else:
               detcr_cd['threshold_backoff_5'] = 6
            detcr_cd['bias_voltage'] = 0x30

      if headType == 'RHO':
         detcr_cd['bias_voltage'] = 0x24
         detcr_cd['threshold_backoff_4'] = 6
         detcr_cd['threshold_backoff_5'] = 0x0A
         if heaterElement == "READER_HEATER":
            if AFH_State == 4:
               detcr_cd['threshold_backoff_5'] = 6
            else:
               detcr_cd['threshold_backoff_5'] = 8
            detcr_cd['bias_voltage'] = 0x26

      if headType == 'HWY':
         detcr_cd['bias_voltage'] = 0x38
         detcr_cd['threshold_backoff_4'] = 4
         detcr_cd['threshold_backoff_5'] = 8
         if heaterElement == "READER_HEATER":
            if AFH_State == 4:
               detcr_cd['threshold_backoff_5'] = 5
            else:
                 detcr_cd['threshold_backoff_5'] = 6
            detcr_cd['bias_voltage'] = 0x35

   baseIPD2Prm_135['DETCR_CD'] = (
                              (detcr_cd['band_pass_filter'] << 8) | detcr_cd['bias_voltage'],
                              (detcr_cd['afh_setting_1'] << 8) | detcr_cd['detcr_gain'],
                              detcr_cd['detcr_ctrl2'],
                              detcr_cd['detcr_ctrl3'],
                              (detcr_cd['write_current'] << 4) | detcr_cd['threshold_backoff_4'],
                              (detcr_cd['afh_setting_5'] << 4) | detcr_cd['threshold_backoff_5'],
                              0xFFFF,
                              0xFFFF,
                              0xFFFF,
                              0xFFFF)

   #For DC DETCR Only
   if baseIPD2Prm_135.has_key("SPECTRAL_DETECTOR4"): # remove AGC detector4 based on HM feedback 8-Jul-2015
      del(baseIPD2Prm_135["SPECTRAL_DETECTOR4"])

   from Test_Switches import testSwitch
   if testSwitch.FE_0315250_322482_P_AFH_CM_OVERLOADING:    
      baseIPD2Prm_135['DEBUG_PRINT'] = 0 

   if testSwitch.extern.FE_0327966_322482_ADAPTIVE_AFH_DETCR_BIAS and testSwitch.FE_0328298_305538_P_ENABLE_ADAPTIVE_AFH_DETCR_BIAS and \
      ( (headType == 'RHO' and AABType in ("501.16",)) or (headType == 'TDK' and AABType in ("25RW3E",)) or (headType == 'HWY' and AABType in ("H_25RW3E",)) ):
      if not baseIPD2Prm_135.has_key("CWORD3"):
          baseIPD2Prm_135["CWORD3"]    = 0
      if (AFH_State in [1,2]) and (heaterElement != "READER_HEATER"): 
         baseIPD2Prm_135["CWORD3"]     |= 0x0080  # CWORD3_DETCR_ADAPTIVE_BIAS_BY_ZONE_GROUP = 0x0080
      if (AFH_State in [3,4]) and (heaterElement != "READER_HEATER"):
         baseIPD2Prm_135["CWORD3"]     |= 0x0100  # CWORD3_DETCR_GET_BIAS_FROM_RAP = 0x0100
      if headType    == 'RHO':
         baseIPD2Prm_135['DETCR_BIAS_RANGE'] = (0x0724,0x321E) # min delta, end, start bias
      if headType    == 'TDK':
         baseIPD2Prm_135['DETCR_BIAS_RANGE'] = (0x0623,0x3C23) # min delta, end, start bias
      if headType    == 'HWY':
         baseIPD2Prm_135['DETCR_BIAS_RANGE'] = (0x0623,0x3B27) # min delta, end, start bias

   if testSwitch.extern.FE_0243165_322482_REAFH3:
      if testSwitch.FE_AFH3_TO_IMPROVE_TCC and  AFH_State in [3,]:
         if not baseIPD2Prm_135.has_key("CWORD3"):
            baseIPD2Prm_135["CWORD3"]    = 0
         baseIPD2Prm_135["CWORD3"]     |= 0x0004  # CWORD3_AFH3_BY_EXCEPTION = 0x0004
         baseIPD2Prm_135["AFH_CLR_VS_RAP_THRESH"] = 5

      if testSwitch.FE_AFH4_TO_USE_TWO_ZONES_TCC and  AFH_State in [4,]:
         if not baseIPD2Prm_135.has_key("CWORD3"):
            baseIPD2Prm_135["CWORD3"]    = 0
         baseIPD2Prm_135["CWORD3"]     |= 0x0008  # CWORD3_AFH4_TCS_BY_TWO_ZONES = 0x0008

   #if testSwitch.extern.FE_0191201_322482_SCP_YARRA_AFH_BYPASS_NEW_OPTI_ZONES:
      # baseIPD2Prm_135["CWORD3"]     |= 0x0010  # CWORD3_EXTREME_OD_USE_MEASURED_DAC = 0x0010
      # baseIPD2Prm_135["CWORD3"]     |= 0x0020    # CWORD3_EXTREM_OD_LIMIT_POLYFIT_DAC_DELTA = 0x0020

   if testSwitch.HAMR and AFH_State in [2,]:
      if not baseIPD2Prm_135.has_key("CWORD3"):
         baseIPD2Prm_135["CWORD3"]    = 0
      baseIPD2Prm_135["CWORD3"]     |= 0x0400  # CWORD3_HAMR_PARTIAL_IOP

   if testSwitch.extern.FE_0312552_322482_PORT_ESG_LFACH_TO_PSG and AABType in ["501.42", ]: # LCT media concurrent DC/AC contact detection
      if not baseIPD2Prm_135.has_key("CWORD3"):
         baseIPD2Prm_135["CWORD3"]    = 0      
      if AFH_State in [4,]:
        baseIPD2Prm_135["CWORD3"]    |= 0x200
        baseIPD2Prm_135["DETCR_BIT_INDEX"]  = (0,0)
      else:
        baseIPD2Prm_135["CWORD3"]    |= 0x40
        
      baseIPD2Prm_135["DETCR_DETECTOR"] =(0x79, 1800, 7, 220, 3, 0, 4, 0, 0, 0) # , 0x79, 1800, 7, 220, 3, 0, 4, 0, 0, 0)
       
      dc_detcr = [0x31, 5760, 3, 240, 4, 65, 0, 0, 30, 0, 0x31] # calibrate DETCR current bias using target voltage 240 mV
      if preamp_type.startswith('TI'):
         dc_detcr[4] = 3
      if heaterElement == "READER_HEATER":
         dc_detcr[10] |=  0x8
      #    baseIPD2Prm_135["DC_DETCR"] = (0x31, 5760, 3, 0, 4, 65, 0, 0, 30, 0, 0x39) #  , 5760, 3, 0, 4, 65, 0, 0, 30, 0)
      #else:
      #   baseIPD2Prm_135["DC_DETCR"] = (0x31, 5760, 3, 0, 4, 65, 0, 0, 30, 0, 0x31) # , 5760, 3, 0, 4, 65, 0, 0, 30, 0)
      baseIPD2Prm_135["DC_DETCR"] = tuple(dc_detcr)
      baseIPD2Prm_135["SPECTRAL_DETECTOR1"] = [201, 1, 3614, 650, 1, 1073, 0x08, 1, 35930, -1]
      baseIPD2Prm_135["SPECTRAL_DETECTOR2"] = [14473, 32769, 2620, 170, 1, 1, 1, 1, 35930, -1]
      baseIPD2Prm_135["SPECTRAL_DETECTOR6"] = [649, 1, 3614, 650, 1, 1073, 0x08, 1, 33370, -1]
      baseIPD2Prm_135["M3_FREQ_RANGE"] = [5700, 5800]
      if baseIPD2Prm_135.has_key("SPECTRAL_DETECTOR5"): 
         del(baseIPD2Prm_135["SPECTRAL_DETECTOR5"]) 
      if baseIPD2Prm_135.has_key("PES_RETRY_ZONES_EXT"): 
         del(baseIPD2Prm_135["PES_RETRY_ZONES_EXT"]) 
      if baseIPD2Prm_135.has_key("AGC_RETRY_ZONES"): 
         del(baseIPD2Prm_135["AGC_RETRY_ZONES"]) 
      if baseIPD2Prm_135.has_key("DETECTOR_BIT_MASK"): 
         del(baseIPD2Prm_135["DETECTOR_BIT_MASK"]) 
      if baseIPD2Prm_135.has_key("DETECTOR_BIT_MASK_EXT"): 
         del(baseIPD2Prm_135["DETECTOR_BIT_MASK_EXT"]) 
      baseIPD2Prm_135["B_WR_NUM_WEDGES"]        = 323
      baseIPD2Prm_135["E_POST_RD_NUM_WEDGES"]   = 38
      baseIPD2Prm_135["DAC_RANGE"]   = (-50,50,20)

   return baseIPD2Prm_135

   #####################################################################################
   #
   #           Parameter defines/definititions
   #
   ##################################################################################
   #define CWORD1_UNUSED_BIT                          ( 0x0001 )
   #define CWORD1_MASK_SERVO_UNSAFES                  ( 0x0002 )
   #define CWORD1_TEST_ALL_TRACKS                     ( 0x0004 )
   #define CWORD1_RUN_CONCURRENT                      ( 0x0008 )
   #define CWORD1_RUN_BY_SPECIFIED_ZONE_ORDER         ( 0x0010 )
   #define CWORD1_RUN_BY_ZONE_OD_TO_ID                ( 0x0020 )
   #define CWORD1_RUN_BY_ZONE_ID_TO_OD                ( 0x0040 )
   #define CWORD1_TEST_ALL_HEADS                      ( 0x0080 )
   #define CWORD1_RUN_FIND_GOOD_TRACK                 ( 0x0100 )
   #define CWORD1_SEEK_AWAY_ON_CONTACT                ( 0x0200 )
   #define CWORD1_RUN_WPH_AND_HO                      ( 0x0400 )
   #define CWORD1_NORMALIZE_AGC                       ( 0x0800 )
   #define CWORD1_LIMIT_DAC_RANGE_BASED_ON_PREV_TRACK ( 0x1000 )
   #define CWORD1_CURVE_FIT_FINAL_CONTACT_DACS        ( 0x2000 )
   #define CWORD1_LIMIT_DAC_RANGE_BASED_ON_REGRESSION ( 0x4000 )
   #define CWORD1_INTERPOLATE_CLEARANCE               ( 0x8000 )


   #define CWORD2_SAVE_RESULTS_TO_RAM                 ( 0x0001 )
   #define CWORD2_SAVE_RESULTS_TO_FLASH               ( 0x0002 )
   #define CWORD2_UPDATE_SYSTEM_ZONE                  ( 0x0004 )
   #define CWORD2_ALLOW_MORE_THAN_2_FASTIO_REVS       ( 0x0008 )
   #define CWORD2_CONFIRM_INITIAL_ZONES               ( 0x0010 )
   #define CWORD2_EXTRME_OD_ID_RUN                    ( 0x0020 )
   #define CWORD2_DO_DUAL_CURVE_FIT                   ( 0x0040 )
   #define CWORD2_FAIL_IF_GLOBAL_MAX_DAC_REACHED      ( 0x0080 )
   #define CWORD2_RUN_INITIAL_ZONES_BASED_ON_RAP_CLR  ( 0x0100 )
   #define CWORD2_INTERPOLATE_WIRP_LIMITS             ( 0x0200 )
   #define CWORD2_RMS_MOTION_CALCULATION              ( 0x0400 )
   #define CWORD2_PRED_INTERVAL_DYNAMIC_THRESHOLD     ( 0x0800 )
   #define CWORD2_HEAD_STABILITY_CHECK                ( 0x1000 )
   #define CWORD2_ENABLE_AGC_BASELINE_JUMP_DETECTION  ( 0x2000 )


   #define GLOBAL_DISPLAY_OPTIONS_PER_ITERATION_AGC_STATS      (0x0001)
   #define GLOBAL_DISPLAY_OPTIONS_DUMP_TIME_AVERAGED_AGC       (0x0002)
   #define GLOBAL_DISPLAY_OPTIONS_DUMP_TIME_AVERAGED_PES       (0x0004)
   #define GLOBAL_DISPLAY_OPTIONS_DISABLE_TRACK_SUMMARY_OUTPUT (0x0008)
   #define GLOBAL_DISPLAY_OPTIONS_DUMP_REVS_IN_CONTACT         (0x0010)
   #define GLOBAL_DISPLAY_OPTIONS_DUMP_DATA_ON_RETRY           (0x0020)
   #define GLOBAL_DISPLAY_OPTIONS_DUMP_LOW_AVERAGED_REF_AGC    (0x0040)
   #define GLOBAL_DISPLAY_OPTIONS_DUMP_SET_SAVE_RESTORE_OCLIM  (0x0080)
   #define GLOBAL_DISPLAY_OPTIONS_POLY_FIT                     (0x0100)
   #define GLOBAL_DISPLAY_OPTIONS_AGC_OPTI                     (0x0200)
