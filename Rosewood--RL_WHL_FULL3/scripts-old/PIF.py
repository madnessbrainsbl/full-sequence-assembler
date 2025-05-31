#-----------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                     #
#-----------------------------------------------------------------------------------------#
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/12/27 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Amazon/PIF.py $
# $Revision: #51 $
# $DateTime: 2016/12/27 23:52:43 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Amazon/PIF.py#51 $
# Level: 1
#-----------------------------------------------------------------------------------------#
import WaterfallNiblets
from Constants import *
from Test_Switches import testSwitch
from TestParamExtractor import TP

std_Attr_Fmt = {
   'defaultByte': 0xFF,
   #Fmt is [start,end,pattern]
   #The last item needs to be the maximum length of the file
   'baseFmt': [
               [0,   2047,0x20], # Initialize full file
               [338, 511, 0xFF],
               [512, 519, 0xFF], # HDA SN must be 0xFF's
               [520, 520, 0x80], # Page D1 Length
               [521, 521, 0xFF],
               [762, 1023,0xFF],
               [1280,1280,0x00], # Page D3 Length
               [1281,1281,0xFF],
               [1522,1535,0xFF],
               [1536,1536,0x40], # Page D4 Length
               [1778,2045,0xFF],
               [2047,2047,0x20], # Must re-init last byte for DTDFileCreator
              ],

   # Attributes to be applied to the drive
   # Spec is (startByte, endByte, shiftRight) default shift is LEFT
   'AttrLocs':{
      'SERVO_CODE':              (2,   17),
      'FIRMWARE_VER':            (18,  33),
      'PCBA_PART_NUM':           (34,  49),
      'PCBA_REV':                (50,  65),
      'PCBA_SERIAL_NUM':         (66,  81),
      'PCBA_DATECODE':           (82,  97),
      'PRE_AMP_LOT_1':           (274, 305),
      'DISC_CUST_SN':            (306, 337), # Dell PPID
      'PART_NUM':                (522, 537),
      'HDA_CODE':                (538, 547),
      'HSA_SERIAL_NUM':          (554, 569),
      'MOTOR_LOT':               (570, 585),
      'MEDIA_1_DC':              (586, 601),
      'MEDIA_2_DC':              (602, 617),
      'MEDIA_3_DC':              (618, 633),
      'BIRTH_DATE':              (634, 649),
      'MEDIA_4_DC':              (650, 665),
      'MEDIA_5_DC':              (666, 681),
      'HSA_PART_NUM':            (682, 697),
      'MOTOR_SERIAL_NUM':        (698, 713),
      }
   }

dPNumInfo = {
      '1':
         {
            #            ID = name of CAID   Size = bytes for this attribute  Offset = Offset with log (if needed)  Info = passed in data
            #'Content': ['DISPLAY_GLIST', ],  # check rlist
            'lCAIDS' :  [
                  {'ID':   'SMARTREADDATA',              # Check SMART attribute data - 512 bytes from CPC ICmd.SmartReadData()
                           'ATTR_RAW':
                           [
                              (5,   '<=',    0, 6),      # SMART Attribute 5 Raw Data = Retired Sector Count
                              #(9,   '<=',    0, 4),     # SMART Attribute 9 Raw Data = Power On Hours (POH)
                              (184, '<=',    0, 6),      # SMART Attribute 184 Raw Data = IOEDC reported
                              (197, '<=',    0, 6),      # SMART Attribute 197 Raw Data = Pending Spares Count
                              (198, '<=',    0, 6),      # SMART Attribute 198 Raw Data = Uncorrectable Sect Count
                           ],
                           'WORDOFFSET':                 # unsigned short little-endian format
                           [
                              (410, 412,  '<=',  0),     # Offset 410:411 Spare Count when Last reset Smart
                              (412, 414,  '<=',  0),     # Offset 412:413 Pending Spare Count when last reset Smart
                           ],
                  },
            ],
         }
}

if testSwitch.FE_0135028_426568_CLEAR_MODE_PAGES_FOR_SATA:
   dPNumInfo.update({'.*': {'lCAIDS': [{'ID':'RESET_MODE_PGS'},]}})

# This is the same function as PIF dPNumInfo SMARTREADDATA
dSmartInfo = {
             '[91]':
                  {
                  'lCAIDS' :  [
                                 {'ID':'SMARTREADDATA',          # Check SMART attribute data - 512 bytes from CPC ICmd.SmartReadData()
                                  'ATTR_RAW':
                                     [
                                        (9,   '<=',    0, 4),       # SMART Attribute 9 Raw Data = Power On Hours (POH)
                                     ],
                                 },
                              ],
                  }

            }

states_GOTF = {
   '*,*' : {                        # RW7 1D/2D SD&D, SED, FIPS
         "PRE2": 'ALL',
         "CAL2": 'ALL',
         "FNC2": ['DNLD_BRG_IV'],   # use this if using SDnD/SED F3
         "CRT2": ['DNLD_BRG_IV'],   # use this if using SDnD/SED F3
         "MQM2": 'ALL',
         "FIN2": 'ALL',
         "CUT2": [''],
         "FNG2": [''],
   },

   '*,1UA1': {                      # RW7 1DH 4GB-NAND
         "PRE2": 'ALL',
         "CAL2": 'ALL',
         "FNC2": [''],
         "CRT2": [''],
         "MQM2": 'ALL',
         "FIN2": 'ALL',
         "CUT2": [''],
         "FNG2": [''],
   },
}

########################### GOTF Manual Commit ###################################
#  Business Group(BG): [PartNum1, PartNum2, PartNum3]
#  In example below, PN_A will downgrade to PN_B then downgrade to PN_STD
#
#  At start of test, partnumber and or 3 digit tab number attribute used to find BG eg.

   #'CTUA'   : ['9GE14D-700','9GE14G-700'], or ['-700','"']
   #'CTUB'   : ['9GE14D-020','9GE14G-020'], or ['-020','"']
   #'STD'    : ['9GE14D-566','"'], or ['-566','"']

   # All entries must contain same number of row names, if no name '"', must be added
   # Note : Manual_GOTF is the master list of available tabs, defines start point from
   #        precommited 3 digit tab number ie. starting BG and then flows vertically downward
   #        if it doesn't meet criteria of starting BG based on order of demand table sequence.


Manual_GOTF = {
   'Base' : {
      'CTUA'             : [    '',    '',    '', '-020', '-055', '-070', '-140', '-170', '-171', '-150', '-230', '-800', '-950',     '', ''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,],
      'CTUB'             : [    '',    '',    '',     '',     '',     '',     '',     '',     '',     '',     '',     '',     '',     '', ''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,],
      'OEM1A'            : [    '',    '',    '',     '',     '',     '',     '',     '',     '',     '',     '',     '',     '',     '', ''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,],
      'OEM1B'            : [    '',    '','-030',     '',     '',     '',     '',     '',     '',     '',     '',     '',     '', '-285', ''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,],
      'STD'              : [    '',    '',    '',     '',     '',     '',     '',     '',     '',     '',     '',     '',     '',     '', '-990','-991','-992','-993','-994',''    ,'-996','-997','-998','-999','-500',''    ,''    ,''    ,''    ,''    ,],
      'SBS'              : ['-899','-GLB',    '',     '',     '',     '',     '',     '',     '',     '',     '',     '',     '',     '', ''    ,''    ,''    ,''    ,''    ,'-995',''    ,''    ,''    ,''    ,''    ,'-566','-567','-568','-985','-986',],
      },
   'Master_Child' : { # Master-Child tab for Rosewood7
      'CTUA'             : [''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,'-2J0',''    ,''    ,''    ,''    ,''    ,''    ,''    ,'','' ,'-7B0','-7B1','-7B2',''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,'-960','-2B5',''    ,'-900',''    ,''    ,'-740','-741',''    ,''    ,''    ,''    ,''    ,],
      'CTUB'             : [''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,],
      'OEM1A'            : [''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,],
      'OEM1B'            : [''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,'-8B8',''    ,'-8B9','-8C5','-8C6','-3A0','-2A0',''    ,''    ,''    ,'-7A0',''    ,'-3C0',''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,'-2B0',''    ,''    ,''    ,'-3A6',''    ,''    ,''    ,],
      'STD'              : [''    ,''    ,''    ,''    ,'-J88','-8J8','-88J','-88W','-W88',''    ,'-0E0',''    ,'-8E8',''    ,''    ,''    ,''    ,''    ,'-5A5',''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,''    ,],
      'SBS'              : ['-9E9','-P99','-LEB','-PLB','-995','-995','-995','-995','-995',''    ,'-995','-995','-995','-995','-995','-995','-995','-995','-995','-995','-995','-995','-995','-995','-J87','-8J7','-87J','-87W','-W87','-E68','-68E','-995','-995','-995','-995','-995',''    ,'-6E0','-995','-995','-995','-8E0','-P68','-6U8',],
      },
   'Master_Child_FTAB' : { # Master-Child full tab for Rosewood7
      'CTUA'             : [''          ,'1RC17D-2A0',''          ,''          ,''          ,''          ,''          ,''          ,''          ,'2G2174-900','2G3172-900','1RK17D-2A0',],
      'CTUB'             : [''          ,''          ,''          ,''          ,''          ,''          ,''          ,''          ,''          ,''          ,''          ,''          ,],
      'OEM1A'            : [''          ,''          ,''          ,''          ,''          ,''          ,''          ,''          ,''          ,''          ,''          ,''          ,],
      'OEM1B'            : [''          ,''          ,''          ,''          ,''          ,'1RG174-2A0',''          ,''          ,''          ,''          ,''          ,''          ,],
      'STD'              : ['1RC172-8J8',''          ,'1RE172-8J8','1RE174-8J8','1RE17D-8J8',''          ,'2E7172-0E0','2E717D-0E0','2E8174-0E0',''          ,''          ,''          ,],
      'SBS'              : ['1RK172-995','1RK17D-995','1RK172-995','1RK172-995','1RK17D-995','1R8174-995','1RK172-995','1RK17D-995','1R8174-995','1R8174-995','1RK172-995','1RK172-995',],
      },
   }

DemandTable = ['CTUA','CTUB','OEM1A','OEM1B','STD','SBS']
LowestOEM = "STD"
WTFTable = {
   # HAMR related. Starwood eval
   'A7_N1' : 'D0R0', # 300       # Relax 1H
   # Rosewood7 1D
   '93_N2' : 'D0R0', # 1000      # Native 2H
   '93_R2' : 'D0R0', # 1000      # Native 2H SBS
   '93_RC' : 'D0R1', # 750       # 1st level wtf
   '93_RD' : 'D0R1', # 500       # 1st level wtf
   '93_NC' : 'D0RS', # 750       # force rezone at PWA
   '93_ND' : 'D0RS', # 500       # force rezone at PWA   
   # Rosewood7 1DLC
   'DE_N2' : 'D0R0', # 1000      # Native 2H
   'DE_R2' : 'D0R0', # 1000      # Native 2H SBS
   'DE_RC' : 'D0R1', # 750       # 1st level wtf
   'DE_RD' : 'D0R1', # 500       # 1st level wtf
   'DE_NC' : 'D0RS', # 750       # force rezone at PWA
   'DE_ND' : 'D0RS', # 500       # force rezone at PWA
   # Rosewood7 1DLC R11
   'ES_N2' : 'D0R0', # 1000      # Native 2H
   'ES_R2' : 'D0R0', # 1000      # Native 2H SBS
   'ES_RC' : 'D0R1', # 750       # 1st level wtf
   'ES_RD' : 'D0R1', # 500       # 1st level wtf
   'ES_N1' : 'D1R0', # 500       # Native 1H
   'ES_D1' : 'D1R0', # 500       # 1st level wtf
   'ES_RA' : 'D1R1', # 375       # 1st level wtf
   'ES_NC' : 'D0RS', # 750       # force rezone at PWA
   'ES_ND' : 'D0RS', # 500       # force rezone at PWA
   # Rosewood7 1DLC IDCS
   'F6_N2' : 'D0R0', # 1000      # Native 2H
   'F6_R2' : 'D0R0', # 1000      # Native 2H SBS
   'F6_RC' : 'D0R1', # 750       # 1st level wtf
   'F6_RD' : 'D0R1', # 500       # 1st level wtf
   'F6_NC' : 'D0RS', # 750       # force rezone at PWA
   'F6_ND' : 'D0RS', # 500       # force rezone at PWA
   # Rosewood7 1D larger OD Flange MBA
   'CB_N2' : 'D0R0', # 1000      # Native 2H
   'CB_R2' : 'D0R0', # 1000      # Native 2H SBS
   'CB_RC' : 'D0R1', # 750       # 1st level wtf
   'CB_RD' : 'D0R1', # 500       # 1st level wtf
   'CB_NC' : 'D0RS', # 750       # force rezone at PWA
   'CB_ND' : 'D0RS', # 500       # force rezone at PWA
   # Rosewood7 1D Thicker LVCM (0.85mm)
   'ES_N2' : 'D0R0', # 1000      # Native 2H
   'ES_R2' : 'D0R0', # 1000      # Native 2H SBS
   'ES_RC' : 'D0R1', # 750       # 1st level wtf
   'ES_RD' : 'D0R1', # 500       # 1st level wtf
   'ES_NC' : 'D0RS', # 750       # force rezone at PWA
   'ES_ND' : 'D0RS', # 500       # force rezone at PWA
   # Rosewood7 2D 3H (RW7 Common Part Number for 1TB Support)
   # Rosewood7 2D
   '94_N4' : 'D0R0', # 2000      # Native 4H
   '94_R4' : 'D0R0', # 2000      # Native 4H SBS
   '94_RG' : 'D0R1', # 1500      # 1st level wtf
   '94_NG' : 'D0RS', # 1500      # force rezone at PWA
   '94_D3' : 'D1R0', # 1500      # Depop to 3H
   # Rosewood7 2D @ 1TB
   '94_N2' : 'D0R0', # 1000      # Force rezone 1TB SBS
   '94_R2' : 'D0R2', # 1000      # Waterfall 1TB SBS
   '94_RC' : 'D0R1', # 750       # 1st level wtf
   '94_NC' : 'D0RS', # 750       # force rezone at PWA
   # Rosewood7 2DLC
   'DZ_N4' : 'D0R0', # 2000      # Native 4H
   'DZ_R4' : 'D0R0', # 2000      # Native 4H SBS
   'DZ_RG' : 'D0R1', # 1500      # 1st level wtf
   'DZ_NG' : 'D0RS', # 1500      # force rezone at PWA
   'DZ_D3' : 'D1R0', # 1500      # Depop to 3H
   'DZ_D2' : 'D2R0', # 1000      # Depop to 2H
   
   # Rosewood7 2DLC @ 1TB
   'DZ_N2' : 'D0R0', # 1000      # Force rezone 1TB SBS
   'DZ_R2' : 'D0R2', # 1000      # Waterfall 1TB SBS
   'DZ_RC' : 'D0R1', # 750       # 1st level wtf
   'DZ_RD' : 'D0R2', # 500       # 2st level wtf
   'DZ_NC' : 'D0RS', # 750       # force rezone at PWA
   # Rosewood7 2DLC @ 500GB
   'DZ_N1' : 'D3R0', # 500      # Force rezone 500GB SBS
   'DZ_D1' : 'D3R0', # 500      # Force rezone 500GB SBS
   'DZ_NA' : 'D3R1', # 375      # Force rezone 320GB SBS
   'DZ_RA' : 'D3R1', # 375      # Force rezone 320GB SBS

   # Rosewood7 2DLC #IDCS
   'F7_N4' : 'D0R0', # 2000      # Native 4H
   'F7_R4' : 'D0R0', # 2000      # Native 4H SBS
   'F7_RG' : 'D0R1', # 1500      # 1st level wtf
   'F7_NG' : 'D0RS', # 1500      # force rezone at PWA
   'F7_D3' : 'D1R0', # 1500      # Depop to 3H
   # Rosewood7 2DLC @ 1TB
   'F7_N2' : 'D0R0', # 1000      # Force rezone 1TB SBS
   'F7_R2' : 'D0R2', # 1000      # Waterfall 1TB SBS
   'F7_RC' : 'D0R1', # 750       # 1st level wtf
   'F7_NC' : 'D0RS', # 750       # force rezone at PWA
   # Rosewood7 2D larger OD Flange MBA
   'CC_N4' : 'D0R0', # 2000      # Native 4H
   'CC_R4' : 'D0R0', # 2000      # Native 4H SBS
   'CC_RG' : 'D0R1', # 1500      # 1st level wtf
   'CC_NG' : 'D0RS', # 1500      # force rezone at PWA
   'CC_D3' : 'D1R0', # 1500      # Depop to 3H
   'CC_N2' : 'D0R0', # 1000      # Force rezone 1TB SBS
   'CC_R2' : 'D0R2', # 1000      # Waterfall 1TB SBS
   'CC_RC' : 'D0R1', # 750       # 1st level wtf
   'CC_NC' : 'D0RS', # 750       # force rezone at PWA
   # Rosewood7 2D larger OD Flange MBA
   'DZ_N4' : 'D0R0', # 2000      # Native 4H
   'DZ_R4' : 'D0R0', # 2000      # Native 4H SBS
   'DZ_RG' : 'D0R1', # 1500      # 1st level wtf
   'DZ_NG' : 'D0RS', # 1500      # force rezone at PWA
   'DZ_D3' : 'D1R0', # 1500      # Depop to 3H
   'DZ_N2' : 'D0R0', # 1000      # Force rezone 1TB SBS
   'DZ_R2' : 'D0R2', # 1000      # Waterfall 1TB SBS
   'DZ_RC' : 'D0R1', # 750       # 1st level wtf
   'DZ_NC' : 'D0RS', # 750       # force rezone at PWA
   # Rosewood7 1D/2D 1-head Capacity
   '93_N1' : 'D0R0', # 500       # Native 1H
   '93_R1' : 'D0R0', # 500       # Native 1H SBS
   '93_NA' : 'D0R1', # 375       # 1st level wtf
   '93_RA' : 'D0R1', # 375       # 1st level wtf
   '94_N1' : 'D0R0', # 500       # Native 1H
   '94_R1' : 'D0R0', # 500       # Native 1H SBS
   '94_RA' : 'D0R1', # 375       # 1st level wtf

   # Chengai 1D 4K
   '67_N2' : 'D0R0', # 750        # Native 2H
   '67_R2' : 'D0R0', # 750        # Native 2H SBS
   '67_RC' : 'D0R1', # 500        # 1st level wtf
   '67_NC' : 'D0RS', # 500        # force rezone at PWA
}

# Rosewood7 2D 3H (RW7 Common Part Number for 1TB Support)
for i in TP.staticDepopSerialNum.keys():
   WTFTable[i+'_D3'] = 'D1R0'    # 1000      # Static depop to 3H

# Example: This WS prefix is from 7200 rpm, hence if the current drive attribute 'SPINDLE_RPM' is 5400,
# then append 'S1' to drive atrribute 'WTF'
#   'WS': {
#         '5400': 'S1',
#         },

#RPM_WTF_Prefix_Table ={
WTF_rpmTable = {
   '0X': {
         '5400': 'S1',
         },
   '0W': {
         '5400': 'S1',
         },
   '0S': {
         '5400': 'S1',
         },
   '0R': {
         '5400': 'S1',
        },
}

nibletLibrary = {
# HAMR related. Starwood eval
'A7_N1L3_300G_4096_5400'   : WaterfallNiblets.Native_300G_1H_5400,         # Relax 300GB
# Rosewood7 1D
'93_N2L3_1000G_4096_5400'  : WaterfallNiblets.Native_1000G_2H_5400,        # Native 1000GB
'93_N2L3_1000G_4096_MS'    : WaterfallNiblets.Native_1000G_2H_5400_MS,     # Native 1000GB Mobile Survillence
'93_N2L3_1000G_4096_MC15'  : WaterfallNiblets.Native_1000G_2H_5400_15G,    # Native 1000GB 15G MC
'93_N2L2_1000G_4096_5400'  : WaterfallNiblets.Native_1000G_2H_5400,        # Native 1000GB SBS
'93_N2L2_1000G_4096_MC15'  : WaterfallNiblets.Native_1000G_2H_5400_15G,    # Native 1000GB SBS 15G MC
'93_R2L3_1000G_4096_5400'  : WaterfallNiblets.Native_1000G_2H_5400,        # Auto WTF 1000GB
'93_R2L2_1000G_4096_5400'  : WaterfallNiblets.Native_1000G_2H_5400,        # Auto WTF 1000GB SBS
'93_R2L2_1000G_4096_MC15'  : WaterfallNiblets.Native_1000G_2H_5400_15G,    # Auto WTF 1000GB SBS 15G MC
'93_N2L3_970G_4096_5400'   : WaterfallNiblets.Native_970G_2H_5400,         # Native 970GB
'93_NCL3_750G_4096_5400'   : WaterfallNiblets.Rezone_750G_2H_5400,         # Force Rezone 750GB
'93_RCL3_750G_4096_5400'   : WaterfallNiblets.Rezone_750G_2H_5400,         # Auto Rezone 750GB
'93_RCL2_750G_4096_5400'   : WaterfallNiblets.Rezone_750G_2H_5400,         # Auto Rezone 750GB SBS
'93_NDL3_500G_4096_5400'   : WaterfallNiblets.Native_500G_2H_5400,         # Native 500GB for BTC Hds
'93_RDL3_500G_4096_5400'   : WaterfallNiblets.Rezone_500G_2H_5400,         # Auto Rezone 500GB
'93_NDL2_500G_4096_5400_SBS' : WaterfallNiblets.Rezone_500G_2H_5400_SBS,   # Force Rezone 500GB SBS
'93_RDL2_500G_4096_5400_SBS' : WaterfallNiblets.Rezone_500G_2H_5400_SBS,   # Auto Rezone 500GB SBS
# Rosewood7 1DLC
'DE_N2L3_1000G_4096_5400'  : WaterfallNiblets.Native_1000G_2H_5400,        # Native 1000GB
'DE_N2L3_1000G_4096_MS'    : WaterfallNiblets.Native_1000G_2H_5400_MS,     # Native 1000GB Mobile Survillence
'DE_N2L3_1000G_4096_MC15'  : WaterfallNiblets.Native_1000G_2H_5400_15G,    # Native 1000GB 15G MC
'DE_N2L2_1000G_4096_5400'  : WaterfallNiblets.Native_1000G_2H_5400,        # Native 1000GB SBS
'DE_N2L2_1000G_4096_MC15'  : WaterfallNiblets.Native_1000G_2H_5400_15G,    # Native 1000GB SBS 15G MC
'DE_R2L3_1000G_4096_5400'  : WaterfallNiblets.Native_1000G_2H_5400,        # Auto WTF 1000GB
'DE_R2L2_1000G_4096_5400'  : WaterfallNiblets.Native_1000G_2H_5400,        # Auto WTF 1000GB SBS
'DE_R2L2_1000G_4096_MC15'  : WaterfallNiblets.Native_1000G_2H_5400_15G,    # Auto WTF 1000GB SBS 15G MC
'DE_N2L3_970G_4096_5400'   : WaterfallNiblets.Native_970G_2H_5400,         # Native 970GB
'DE_NCL3_750G_4096_5400'   : WaterfallNiblets.Rezone_750G_2H_5400,         # Force Rezone 750GB
'DE_RCL3_750G_4096_5400'   : WaterfallNiblets.Rezone_750G_2H_5400,         # Auto Rezone 750GB
'DE_RCL2_750G_4096_5400'   : WaterfallNiblets.Rezone_750G_2H_5400,         # Auto Rezone 750GB SBS
'DE_NDL3_500G_4096_5400'   : WaterfallNiblets.Native_500G_2H_5400,         # Native 500GB for BTC Hds
'DE_RDL3_500G_4096_5400'   : WaterfallNiblets.Rezone_500G_2H_5400,         # Auto Rezone 500GB
'DE_RDL2_500G_4096_5400_SBS' : WaterfallNiblets.Rezone_500G_2H_5400_SBS,   # Auto Rezone 500GB SBS
'DE_NDL2_500G_4096_5400_SBS' : WaterfallNiblets.Rezone_500G_2H_5400_SBS,   # Force Rezone 500GB SBS
# Rosewood7 1DLC R11

# Rosewood7 1DLC IDCS
'F6_N2L3_1000G_4096_5400'  : WaterfallNiblets.Native_1000G_2H_5400,        # Native 1000GB
'F6_N2L3_1000G_4096_MS'    : WaterfallNiblets.Native_1000G_2H_5400_MS,     # Native 1000GB Mobile Survillence
'F6_N2L3_1000G_4096_MC15'  : WaterfallNiblets.Native_1000G_2H_5400_15G,    # Native 1000GB 15G MC
'F6_N2L2_1000G_4096_5400'  : WaterfallNiblets.Native_1000G_2H_5400,        # Native 1000GB SBS
'F6_N2L2_1000G_4096_MC15'  : WaterfallNiblets.Native_1000G_2H_5400_15G,    # Native 1000GB SBS 15G MC
'F6_R2L3_1000G_4096_5400'  : WaterfallNiblets.Native_1000G_2H_5400,        # Auto WTF 1000GB
'F6_R2L2_1000G_4096_5400'  : WaterfallNiblets.Native_1000G_2H_5400,        # Auto WTF 1000GB SBS
'F6_R2L2_1000G_4096_MC15'  : WaterfallNiblets.Native_1000G_2H_5400_15G,    # Auto WTF 1000GB SBS 15G MC
'F6_N2L3_970G_4096_5400'   : WaterfallNiblets.Native_970G_2H_5400,         # Native 970GB
'F6_NCL3_750G_4096_5400'   : WaterfallNiblets.Rezone_750G_2H_5400,         # Force Rezone 750GB
'F6_RCL3_750G_4096_5400'   : WaterfallNiblets.Rezone_750G_2H_5400,         # Auto Rezone 750GB
'F6_RCL2_750G_4096_5400'   : WaterfallNiblets.Rezone_750G_2H_5400,         # Auto Rezone 750GB SBS
'F6_NDL3_500G_4096_5400'   : WaterfallNiblets.Native_500G_2H_5400,         # Native 500GB for BTC Hds
'F6_RDL3_500G_4096_5400'   : WaterfallNiblets.Rezone_500G_2H_5400,         # Auto Rezone 500GB
'F6_RDL2_500G_4096_5400_SBS' : WaterfallNiblets.Rezone_500G_2H_5400_SBS,   # Auto Rezone 500GB SB
'F6_NDL2_500G_4096_5400_SBS' : WaterfallNiblets.Rezone_500G_2H_5400_SBS,   # Force Rezone 500GB SB
# Rosewood7 1D interim capacity
'93_R2L3_930G_4096_5400'   : WaterfallNiblets.Native_930G_2H_5400,         # Native 930GB
'93_R2L3_870G_4096_5400'   : WaterfallNiblets.Native_870G_2H_5400,         # Native 870GB
'93_R2L3_810G_4096_5400'   : WaterfallNiblets.Native_810G_2H_5400,         # Native 810GB
'93_R2L2_930G_4096_5400'   : WaterfallNiblets.Native_930G_2H_5400,         # Native 930GB
'93_R2L2_870G_4096_5400'   : WaterfallNiblets.Native_870G_2H_5400,         # Native 870GB
'93_R2L2_810G_4096_5400'   : WaterfallNiblets.Native_810G_2H_5400,         # Native 810GB
# Rosewood7 1D larger OD Flange MBA
'CB_N2L3_1000G_4096_5400'  : WaterfallNiblets.Native_1000G_2H_5400,        # Native 1000GB
'CB_N2L3_1000G_4096_MS'    : WaterfallNiblets.Native_1000G_2H_5400_MS,     # Native 1000GB Mobile Survillence
'CB_N2L3_1000G_4096_MC15'  : WaterfallNiblets.Native_1000G_2H_5400_15G,    # Native 1000GB 15G MC
'CB_N2L2_1000G_4096_5400'  : WaterfallNiblets.Native_1000G_2H_5400,        # Native 1000GB SBS
'CB_N2L2_1000G_4096_MC15'  : WaterfallNiblets.Native_1000G_2H_5400_15G,    # Native 1000GB SBS 15G MC
'CB_R2L3_1000G_4096_5400'  : WaterfallNiblets.Native_1000G_2H_5400,        # Auto WTF 1000GB SBS
'CB_R2L2_1000G_4096_5400'  : WaterfallNiblets.Native_1000G_2H_5400,        # Native 1000GB SBS
'CB_R2L2_1000G_4096_MC15'  : WaterfallNiblets.Native_1000G_2H_5400_15G,    # Native 1000GB SBS 15G MC
'CB_N2L3_970G_4096_5400'   : WaterfallNiblets.Native_970G_2H_5400,         # Native 970GB
'CB_NCL3_750G_4096_5400'   : WaterfallNiblets.Rezone_750G_2H_5400,         # Force Rezone 750GB
'CB_RCL3_750G_4096_5400'   : WaterfallNiblets.Rezone_750G_2H_5400,         # Auto Rezone 750GB
'CB_RCL2_750G_4096_5400'   : WaterfallNiblets.Rezone_750G_2H_5400,         # Auto Rezone 750GB SBS
'CB_NDL3_500G_4096_5400'   : WaterfallNiblets.Native_500G_2H_5400,         # Native 500GB for BTC Hds
'CB_RDL3_500G_4096_5400'   : WaterfallNiblets.Rezone_500G_2H_5400,         # Auto Rezone 500GB
'CB_NDL2_500G_4096_5400_SBS' : WaterfallNiblets.Rezone_500G_2H_5400_SBS,   # Force Rezone 500GB SBS
'CB_RDL2_500G_4096_5400_SBS' : WaterfallNiblets.Rezone_500G_2H_5400_SBS,   # Auto Rezone 500GB SBS
# Rosewood7 1D interim capacity larger OD Flange MBA
'CB_R2L3_930G_4096_5400'   : WaterfallNiblets.Native_930G_2H_5400,         # Native 930GB
'CB_R2L3_870G_4096_5400'   : WaterfallNiblets.Native_870G_2H_5400,         # Native 870GB
'CB_R2L3_810G_4096_5400'   : WaterfallNiblets.Native_810G_2H_5400,         # Native 810GB
'CB_R2L2_930G_4096_5400'   : WaterfallNiblets.Native_930G_2H_5400,         # Native 930GB
'CB_R2L2_870G_4096_5400'   : WaterfallNiblets.Native_870G_2H_5400,         # Native 870GB
'CB_R2L2_810G_4096_5400'   : WaterfallNiblets.Native_810G_2H_5400,         # Native 810GB
# Rosewood7 1D Thicker LVCM (0.85mm)
'ES_N2L3_1000G_4096_5400'  : WaterfallNiblets.Native_1000G_2H_5400,        # Native 1000GB
'ES_N2L3_1000G_4096_MS'    : WaterfallNiblets.Native_1000G_2H_5400_MS,     # Native 1000GB Mobile Survillence
'ES_N2L3_1000G_4096_MC15'  : WaterfallNiblets.Native_1000G_2H_5400_15G,    # Native 1000GB 15G MC
'ES_N2L2_1000G_4096_5400'  : WaterfallNiblets.Native_1000G_2H_5400,        # Native 1000GB SBS
'ES_N2L2_1000G_4096_MC15'  : WaterfallNiblets.Native_1000G_2H_5400_15G,    # Native 1000GB SBS 15G MC
'ES_R2L3_1000G_4096_5400'  : WaterfallNiblets.Native_1000G_2H_5400,        # Auto WTF 1000GB SBS
'ES_R2L2_1000G_4096_5400'  : WaterfallNiblets.Native_1000G_2H_5400,        # Native 1000GB SBS
'ES_R2L2_1000G_4096_MC15'  : WaterfallNiblets.Native_1000G_2H_5400_15G,    # Native 1000GB SBS 15G MC
'ES_N2L3_970G_4096_5400'   : WaterfallNiblets.Native_970G_2H_5400,         # Native 970GB
'ES_NCL3_750G_4096_5400'   : WaterfallNiblets.Rezone_750G_2H_5400,         # Force Rezone 750GB
'ES_RCL3_750G_4096_5400'   : WaterfallNiblets.Rezone_750G_2H_5400,         # Auto Rezone 750GB
'ES_NCL2_750G_4096_5400'   : WaterfallNiblets.Rezone_750G_2H_5400,         # Force Rezone 750GB
'ES_RCL2_750G_4096_5400'   : WaterfallNiblets.Rezone_750G_2H_5400,         # Auto Rezone 750GB SBS
'ES_NDL3_500G_4096_5400'   : WaterfallNiblets.Native_500G_2H_5400,         # Native 500GB for BTC Hds
'ES_RDL3_500G_4096_5400'   : WaterfallNiblets.Rezone_500G_2H_5400,         # Auto Rezone 500GB
'ES_NDL2_500G_4096_5400'   : WaterfallNiblets.Rezone_500G_2H_5400,         # Force Rezone 500GB SBS
'ES_RDL2_500G_4096_5400'   : WaterfallNiblets.Rezone_500G_2H_5400,         # Auto Rezone 500GB
'ES_D1L2_500G_4096_5400'   : WaterfallNiblets.Native_500G_1H_5400_SBS,     # Native 500GB SBS
'ES_N1L2_500G_4096_5400'   : WaterfallNiblets.Native_500G_1H_5400_SBS,     # Native 500GB SBS
'ES_D1L2_375G_4096_5400'   : WaterfallNiblets.Rezone_375G_1H_5400,         # Native 375GB SBS
'ES_RAL2_375G_4096_5400'   : WaterfallNiblets.Rezone_375G_1H_5400,         # Auto Rezone 375GB
# Rosewood7 1D interim capacity Thicker LVCM (0.85mm)
'ES_R2L3_930G_4096_5400'   : WaterfallNiblets.Native_930G_2H_5400,         # Native 930GB
'ES_R2L3_870G_4096_5400'   : WaterfallNiblets.Native_870G_2H_5400,         # Native 870GB
'ES_R2L3_810G_4096_5400'   : WaterfallNiblets.Native_810G_2H_5400,         # Native 810GB
'ES_R2L2_930G_4096_5400'   : WaterfallNiblets.Native_930G_2H_5400,         # Native 930GB
'ES_R2L2_870G_4096_5400'   : WaterfallNiblets.Native_870G_2H_5400,         # Native 870GB
'ES_R2L2_810G_4096_5400'   : WaterfallNiblets.Native_810G_2H_5400,         # Native 810GB

# Rosewood7 2D
'94_N4L3_2000G_4096_5400'  : WaterfallNiblets.Native_2000G_4H_5400,        # Native 2000GB
'94_N4L3_2000G_4096_MS  '  : WaterfallNiblets.Native_2000G_4H_5400_MS,     # Native 2000GB  Mobile Survillence
'94_N4L2_2000G_4096_5400'  : WaterfallNiblets.Native_2000G_4H_5400_SBS,    # Native 2000GB SBS
'94_R4L2_2000G_4096_5400'  : WaterfallNiblets.Native_2000G_4H_5400_SBS,    # Auto WTF 2000GB SBS
'94_N4L3_2000G_4096_MC15'  : WaterfallNiblets.Native_2000G_4H_5400_15G,    # Native 2000GB 15G MC
'94_N4L2_2000G_4096_MC15'  : WaterfallNiblets.Native_2000G_4H_5400_15G,    # Native 2000GB SBS 15G MC
'94_R4L2_2000G_4096_MC15'  : WaterfallNiblets.Native_2000G_4H_5400_15G,    # Auto WTF 2000GB SBS 15G MC
'94_NGL2_1500G_4096_5400'  : WaterfallNiblets.Rezone_1500G_4H_5400,        # Force Rezone 1500GB
'94_NGL3_1500G_4096_5400'  : WaterfallNiblets.Rezone_1500G_4H_5400,        # Force Rezone 1500GB
'94_RGL3_1500G_4096_5400'  : WaterfallNiblets.Rezone_1500G_4H_5400,        # Auto Rezone 1500GB
'94_RGL2_1500G_4096_5400'  : WaterfallNiblets.Rezone_1500G_4H_5400,        # Auto Rezone 1500GB SBS
'94_D3L3_1500G_4096_5400'  : WaterfallNiblets.Depop_1500G_3H_5400,         # Depop 1500GB
'94_D3L2_1500G_4096_5400'  : WaterfallNiblets.Depop_1500G_3H_5400_SBS,     # Depop 1500GB SBS
# Rosewood7 2DLC
'DZ_N4L3_2000G_4096_5400'  : WaterfallNiblets.Native_2000G_4H_5400,        # Native 2000GB
'DZ_N4L3_2000G_4096_MS  '  : WaterfallNiblets.Native_2000G_4H_5400_MS,     # Native 2000GB  Mobile Survillence
'DZ_N4L2_2000G_4096_5400'  : WaterfallNiblets.Native_2000G_4H_5400_SBS,    # Native 2000GB SBS
'DZ_R4L2_2000G_4096_5400'  : WaterfallNiblets.Native_2000G_4H_5400_SBS,    # Auto WTF 2000GB SBS
'DZ_N4L3_2000G_4096_MC15'  : WaterfallNiblets.Native_2000G_4H_5400_15G,    # Native 2000GB 15G MC
'DZ_N4L2_2000G_4096_MC15'  : WaterfallNiblets.Native_2000G_4H_5400_15G,    # Native 2000GB SBS 15G MC
'DZ_R4L2_2000G_4096_MC15'  : WaterfallNiblets.Native_2000G_4H_5400_15G,    # Auto WTF 2000GB SBS 15G MC
'DZ_N4L3_1950G_4096_5400'  : WaterfallNiblets.Native_1950G_4H_5400,        # Native 1950GB
'DZ_NGL2_1500G_4096_5400'  : WaterfallNiblets.Rezone_1500G_4H_5400,        # Force Rezone 1500GB
'DZ_NGL3_1500G_4096_5400'  : WaterfallNiblets.Rezone_1500G_4H_5400,        # Force Rezone 1500GB
'DZ_RGL3_1500G_4096_5400'  : WaterfallNiblets.Rezone_1500G_4H_5400,        # Auto Rezone 1500GB
'DZ_RGL2_1500G_4096_5400'  : WaterfallNiblets.Rezone_1500G_4H_5400,        # Auto Rezone 1500GB SBS
'DZ_RGL2_1000G_4096_5400'  : WaterfallNiblets.Static_Depop_1000G_3H_5400_15G,# Auto Rezone 1500GB SBS
'DZ_D3L3_1500G_4096_5400'  : WaterfallNiblets.Depop_1500G_3H_5400,         # Depop 1500GB
'DZ_D3L2_1500G_4096_5400'  : WaterfallNiblets.Depop_1500G_3H_5400_SBS,     # Depop 1500GB SBS
'DZ_D3L2_1000G_4096_5400'  : WaterfallNiblets.Static_Depop_1000G_3H_5400,  # Depop 1000GB SBS

'DZ_N2L2_1000G_4096_5400'  : WaterfallNiblets.Native_1000G_2H_5400_15G,    # Native 1000GB SBS 15G MC
'DZ_D2L2_1000G_4096_5400'  : WaterfallNiblets.Native_1000G_2H_5400_15G,    # Native 1000GB SBS 15G MC
'ES_NCL2_750G_4096_5400'   : WaterfallNiblets.Native_750G_2H_5400_SBS,         # Force Rezone 750GB
'DZ_RCL2_750G_4096_5400'   : WaterfallNiblets.Native_750G_2H_5400_SBS,     # Native 750GB SBS
'DZ_D2L2_750G_4096_5400'   : WaterfallNiblets.Native_750G_2H_5400_SBS,     # Native 750GB SBS
'DZ_D2L2_500G_4096_5400'   : WaterfallNiblets.Rezone_500G_2H_5400_SBS,   # Auto Rezone 500GB SBS

'DZ_N1L2_500G_4096_5400'   : WaterfallNiblets.Native_500G_1H_5400_SBS,     # Native 500GB SBS
'DZ_D1L2_500G_4096_5400'   : WaterfallNiblets.Native_500G_1H_5400_SBS,     # Auto WTF 500GB SBS
'DZ_D1L2_375G_4096_5400'   : WaterfallNiblets.Rezone_375G_1H_5400,         # DEPOP 1H 500GB Rezone 375GB
'DZ_NAL2_375G_4096_5400'   : WaterfallNiblets.Rezone_375G_1H_5400,         # Auto Rezone 375GB
'DZ_RAL2_375G_4096_5400'   : WaterfallNiblets.Rezone_375G_1H_5400,         # Auto Rezone 375GB

# Rosewood7 2DLC
'F7_N4L3_2000G_4096_5400'  : WaterfallNiblets.Native_2000G_4H_5400,        # Native 2000GB
'F7_N4L3_2000G_4096_MS  '  : WaterfallNiblets.Native_2000G_4H_5400_MS,     # Native 2000GB  Mobile Survillence
'F7_N4L2_2000G_4096_5400'  : WaterfallNiblets.Native_2000G_4H_5400_SBS,    # Native 2000GB SBS
'F7_R4L2_2000G_4096_5400'  : WaterfallNiblets.Native_2000G_4H_5400_SBS,    # Auto WTF 2000GB SBS
'F7_N4L3_2000G_4096_MC15'  : WaterfallNiblets.Native_2000G_4H_5400_15G,    # Native 2000GB 15G MC
'F7_N4L2_2000G_4096_MC15'  : WaterfallNiblets.Native_2000G_4H_5400_15G,    # Native 2000GB SBS 15G MC
'F7_R4L2_2000G_4096_MC15'  : WaterfallNiblets.Native_2000G_4H_5400_15G,    # Auto WTF 2000GB SBS 15G MC
'F7_N4L3_1950G_4096_5400'  : WaterfallNiblets.Native_1950G_4H_5400,        # Native 1950GB
'F7_NGL2_1500G_4096_5400'  : WaterfallNiblets.Rezone_1500G_4H_5400,        # Force Rezone 1500GB
'F7_NGL3_1500G_4096_5400'  : WaterfallNiblets.Rezone_1500G_4H_5400,        # Force Rezone 1500GB
'F7_RGL3_1500G_4096_5400'  : WaterfallNiblets.Rezone_1500G_4H_5400,        # Auto Rezone 1500GB
'F7_RGL2_1500G_4096_5400'  : WaterfallNiblets.Rezone_1500G_4H_5400,        # Auto Rezone 1500GB SBS
'F7_D3L3_1500G_4096_5400'  : WaterfallNiblets.Depop_1500G_3H_5400,         # Depop 1500GB
'F7_D3L2_1500G_4096_5400'  : WaterfallNiblets.Depop_1500G_3H_5400_SBS,     # Depop 1500GB SBS
# Rosewood7 2D interim capacity
'94_R4L3_1860G_4096_5400'  : WaterfallNiblets.Native_1860G_4H_5400,        # Native 1860GB
'94_R4L3_1740G_4096_5400'  : WaterfallNiblets.Native_1740G_4H_5400,        # Native 1740GB
'94_R4L3_1620G_4096_5400'  : WaterfallNiblets.Native_1620G_4H_5400,        # Native 1620GB
# Rosewood7 2D larger OD Flange MBA
'CC_N4L3_2000G_4096_5400'  : WaterfallNiblets.Native_2000G_4H_5400,        # Native 2000GB
'CC_N4L3_2000G_4096_MS  '  : WaterfallNiblets.Native_2000G_4H_5400_MS,     # Native 2000GB  Mobile Survillence
'CC_N4L2_2000G_4096_5400'  : WaterfallNiblets.Native_2000G_4H_5400_SBS,    # Native 2000GB SBS
'CC_R4L2_2000G_4096_5400'  : WaterfallNiblets.Native_2000G_4H_5400_SBS,    # Auto WTF 2000GB SBS
'CC_N4L3_2000G_4096_MC15'  : WaterfallNiblets.Native_2000G_4H_5400_15G,        # Native 2000GB 15G MC
'CC_N4L2_2000G_4096_MC15'  : WaterfallNiblets.Native_2000G_4H_5400_15G,    # Native 2000GB SBS 15G MC
'CC_R4L2_2000G_4096_MC15'  : WaterfallNiblets.Native_2000G_4H_5400_15G,    # Auto WTF 2000GB SBS 15G MC
'CC_NGL2_1500G_4096_5400'  : WaterfallNiblets.Rezone_1500G_4H_5400,        # Force Rezone 1500GB
'CC_NGL3_1500G_4096_5400'  : WaterfallNiblets.Rezone_1500G_4H_5400,        # Force Rezone 1500GB
'CC_RGL3_1500G_4096_5400'  : WaterfallNiblets.Rezone_1500G_4H_5400,        # Auto Rezone 1500GB
'CC_RGL2_1500G_4096_5400'  : WaterfallNiblets.Rezone_1500G_4H_5400,        # Auto Rezone 1500GB SBS
'CC_D3L3_1500G_4096_5400'  : WaterfallNiblets.Depop_1500G_3H_5400,         # Depop 1500GB
'CC_D3L2_1500G_4096_5400'  : WaterfallNiblets.Depop_1500G_3H_5400_SBS,     # Depop 1500GB SBS
# Rosewood7 2D interim capacity larger OD Flange MBA
'CC_R4L3_1860G_4096_5400'  : WaterfallNiblets.Native_1860G_4H_5400,        # Native 1860GB
'CC_R4L3_1740G_4096_5400'  : WaterfallNiblets.Native_1740G_4H_5400,        # Native 1740GB
'CC_R4L3_1620G_4096_5400'  : WaterfallNiblets.Native_1620G_4H_5400,        # Native 1620GB
# Rosewood7 2D interim capacity larger OD Flange MBA
'DZ_R4L3_1860G_4096_5400'  : WaterfallNiblets.Native_1860G_4H_5400,        # Native 1860GB
'DZ_R4L3_1740G_4096_5400'  : WaterfallNiblets.Native_1740G_4H_5400,        # Native 1740GB
'DZ_R4L3_1620G_4096_5400'  : WaterfallNiblets.Native_1620G_4H_5400,        # Native 1620GB

# Rosewood7 2D using 1D PN
'94_N2L3_1000G_4096_5400'  : WaterfallNiblets.Native_1000G_2H_5400,        # Native 1000GB
'94_N2L2_1000G_4096_5400'  : WaterfallNiblets.Native_1000G_4H_5400_SBS,    # Native 1000GB SBS
'94_R2L2_1000G_4096_5400'  : WaterfallNiblets.Rezone_1000G_4H_5400_SBS,    # Auto WTF 1000GB SBS with 1D pn
'94_NCL3_750G_4096_5400'   : WaterfallNiblets.Rezone_750G_2H_5400,         # Force Rezone 750GB
'94_RCL3_750G_4096_5400'   : WaterfallNiblets.Rezone_750G_2H_5400,         # Auto Rezone 750GB
'94_RCL2_750G_4096_5400'   : WaterfallNiblets.Rezone_750G_2H_5400,         # Auto Rezone 750GB SBS
# Rosewood7 2DLC using 1DLC PN
'DZ_N2L3_1000G_4096_5400'  : WaterfallNiblets.Native_1000G_2H_5400,        # Native 1000GB
'DZ_R2L2_1000G_4096_5400'  : WaterfallNiblets.Rezone_1000G_4H_5400_SBS,    # Auto WTF 1000GB SBS with 1D pn
'DZ_NCL3_750G_4096_5400'   : WaterfallNiblets.Rezone_750G_2H_5400,         # Force Rezone 750GB
'DZ_RCL3_750G_4096_5400'   : WaterfallNiblets.Rezone_750G_2H_5400,         # Auto Rezone 750GB
'DZ_RCL2_750G_4096_5400'   : WaterfallNiblets.Rezone_750G_2H_5400,         # Auto Rezone 750GB SBS
# Rosewood7 2DLC using 1DLC PN IDCS
'F7_N2L3_1000G_4096_5400'  : WaterfallNiblets.Native_1000G_2H_5400,        # Native 1000GB
'F7_N2L2_1000G_4096_5400'  : WaterfallNiblets.Native_1000G_4H_5400_SBS,    # Native 1000GB SBS
'F7_R2L2_1000G_4096_5400'  : WaterfallNiblets.Rezone_1000G_4H_5400_SBS,    # Auto WTF 1000GB SBS with 1D pn
'F7_NCL3_750G_4096_5400'   : WaterfallNiblets.Rezone_750G_2H_5400,         # Force Rezone 750GB
'F7_RCL3_750G_4096_5400'   : WaterfallNiblets.Rezone_750G_2H_5400,         # Auto Rezone 750GB
'F7_RCL2_750G_4096_5400'   : WaterfallNiblets.Rezone_750G_2H_5400,         # Auto Rezone 750GB SBS
# Rosewood7 1D using 2D larger OD Flange MBA
'CC_N2L3_1000G_4096_5400'  : WaterfallNiblets.Native_1000G_2H_5400,        # Native 1000GB
'CC_N2L2_1000G_4096_5400'  : WaterfallNiblets.Native_1000G_4H_5400_SBS,    # Native 1000GB SBS
'CC_R2L2_1000G_4096_5400'  : WaterfallNiblets.Rezone_1000G_4H_5400_SBS,    # Auto WTF 1000GB SBS with 1D pn
'CC_NCL3_750G_4096_5400'   : WaterfallNiblets.Rezone_750G_2H_5400,         # Force Rezone 750GB
'CC_RCL3_750G_4096_5400'   : WaterfallNiblets.Rezone_750G_2H_5400,         # Auto Rezone 750GB
'CC_RCL2_750G_4096_5400'   : WaterfallNiblets.Rezone_750G_2H_5400,         # Auto Rezone 750GB SBS
# Rosewood7 1D using 2D larger OD Flange MBA
'DZ_N2L3_1000G_4096_5400'  : WaterfallNiblets.Native_1000G_2H_5400,        # Native 1000GB
'DZ_R2L2_1000G_4096_5400'  : WaterfallNiblets.Rezone_1000G_4H_5400_SBS,    # Auto WTF 1000GB SBS with 1D pn
'DZ_NCL3_750G_4096_5400'   : WaterfallNiblets.Rezone_750G_2H_5400,         # Force Rezone 750GB
'DZ_RCL3_750G_4096_5400'   : WaterfallNiblets.Rezone_750G_2H_5400,         # Auto Rezone 750GB
'DZ_RCL2_750G_4096_5400'   : WaterfallNiblets.Rezone_750G_2H_5400,         # Auto Rezone 750GB SBS
# Rosewood7 1D/2D 1-head Capacity
'93_N1L3_500G_4096_5400'    : WaterfallNiblets.Native_500G_1H_5400,         # Native 500GB
'93_N1L2_500G_4096_5400_SBS': WaterfallNiblets.Native_500G_1H_5400_SBS,     # Native 500GB SBS
'93_R1L2_500G_4096_5400_SBS': WaterfallNiblets.Native_500G_1H_5400_SBS,     # Auto WTF 500GB SBS
'93_RAL3_375G_4096_5400'   : WaterfallNiblets.Rezone_375G_1H_5400,         # Auto Rezone 375GB
'93_NAL2_375G_4096_5400'   : WaterfallNiblets.Rezone_375G_1H_5400,         # Auto Rezone 375GB
'93_RAL2_375G_4096_5400'   : WaterfallNiblets.Rezone_375G_1H_5400,         # Auto Rezone 375GB

'94_N1L3_500G_4096_5400'   : WaterfallNiblets.Native_500G_1H_5400,         # Native 500GB
'94_N1L2_500G_4096_5400'   : WaterfallNiblets.Native_500G_1H_5400_SBS,     # Native 500GB SBS
'94_R1L2_500G_4096_5400'   : WaterfallNiblets.Native_500G_1H_5400_SBS,     # Auto WTF 500GB SBS
'94_RAL3_375G_4096_5400'   : WaterfallNiblets.Rezone_375G_1H_5400,         # Auto Rezone 375GB


#Chengai 1D
'67_N2L3_750G_4096_5400':	WaterfallNiblets.Native_750G_2H_5400,           # Native 750GB
'67_N2L2_750G_4096_5400':	WaterfallNiblets.Native_750G_2H_5400_SBS,       # Native 750GB SBS
'67_R2L2_750G_4096_5400':	WaterfallNiblets.Native_750G_2H_5400_SBS,       # Auto WTF 750GB SBS
'67_NCL3_500G_4096_5400':	WaterfallNiblets.Rezone_500G_2H_5400,           # Force Rezone 500GB
'67_RCL3_500G_4096_5400':	WaterfallNiblets.Rezone_500G_2H_5400,           # Auto Rezone 500GB
#Chengai Temporary
'67_N2L3_720G_4096_5400':	WaterfallNiblets.Native_720G_2H_5400,        #Auto Rezone 720GB
'67_R2L3_720G_4096_5400':	WaterfallNiblets.Native_720G_2H_5400,        #Native 720GB
'67_N2L3_680G_4096_5400':	WaterfallNiblets.Native_680G_2H_5400,        #Auto Rezone 680GB
'67_R2L3_680G_4096_5400':	WaterfallNiblets.Native_680G_2H_5400,        #Native 680GB
'67_N2L3_640G_4096_5400':	WaterfallNiblets.Native_640G_2H_5400,        #Auto Rezone 640GB
'67_R2L3_640G_4096_5400':	WaterfallNiblets.Native_640G_2H_5400,        #Native 640GB
}

# Rosewood7 2D 3H (RW7 Common Part Number for 1TB Support)
for i in TP.staticDepopSerialNum.keys():
   nibletLibrary[i+'_D3L3_1000G_4096_5400'] = WaterfallNiblets.Static_Depop_1000G_3H_5400    # Static depop to 1000GB
   nibletLibrary[i+'_D3L2_1000G_4096_MC15'] = WaterfallNiblets.Static_Depop_1000G_3H_5400_15G    # Static depop to 1000GB with 15G MC

nibletTable = {
   #====== HAMR related. Starwood7 1D 
   '1TV202-' : # Relax 300G with 1H
   {
      'Capacity': ['300G_4096_5400' ],
      'Native'  : ['N1L3'           ],
      'Rezone'  : [''               ],
      'Depop'   : [''               ],
      'Part_num': [''               ],
   },


   #====== Rosewood7 1D LC Dev ===========#
   '1RK172-999' : # Native 970G for MS
   {
      'Capacity': ['970G_4096_5400'],
      'Native'  : ['N2L3'          ],
      'Rezone'  : ['R2L3'          ],
      'Depop'   : ['D3L3'          ],
      'Part_num': [''              ],
   },
   '1RK172-998' :
   {
      'Capacity': ['1000G_4096_5400','1000G_4096_MC15','500G_4096_5400'],
      'Native'  : ['N2L3'           ,'N2L2'           ,              ''],
      'Rezone'  : ['R2L3'           ,'R2L2'           ,          'RDL2'],
      'Depop'   : ['D3L3'           ,''               ,              ''],
      'Part_num': [''               ,'1RK172-995'     ,    '1RK17D-995'],
   },

   '1RK172-995' : # Native 1000G SBS
   {
      'Capacity': ['1000G_4096_MC15','750G_4096_5400','500G_4096_5400','500G_4096_5400','375G_4096_5400'],
      'Native'  : [           'N2L2',              '',              '',              '',              ''],
      'Rezone'  : [               '',          'RCL2',          'RDL2',              '',              ''],
      'Depop'   : [               '',              '',              '',          'D1L2',          'D1L2'],
      'Part_num': [               '',    '1RK17C-995',    '1RK17D-995',    '1RK172-995',    '1RK172-995'],
   },
   '1RK17C-995' : # Rezone 700G SBS
   {
      'Capacity': ['750G_4096_5400','500G_4096_5400'],
      'Native'  : [          'NCL2',              ''],
      'Rezone'  : [          'RCL2',          'RDL2'],
      'Depop'   : [              '',              ''],
      'Part_num': [              '',    '1RK17D-995'],
   },
   '1RK17D-995' : # Rezone 500G SBS
   {
      'Capacity': ['500G_4096_5400'],
      'Native'  : [          'NDL2'],
      'Rezone'  : [          'RDL2'],
      'Depop'   : [              ''],
      'Part_num': [              ''],
   },
   '1RK171-995' : # Native 500G SBS
   {
      'Capacity': ['500G_4096_5400','375G_4096_5400'],
      'Native'  : [          'N1L2',              ''],
      'Rezone'  : [              '',          'RAL2'],
      'Depop'   : [          'D1L2',          'D1L2'],
      'Part_num': [              '',    '1RK17A-995'],
   },
   '1RK17A-995' : # Native 320G SBS
   {
      'Capacity': ['375G_4096_5400'],
      'Native'  : [              ''],
      'Rezone'  : [          'RAL2'],
      'Depop'   : [          'D1L2'],
      'Part_num': [              ''],
   },

   
#CHOOI-19May17 OffSpec
   '1RK172-LEB' : # Native 1000G SBS
   {
      'Capacity': ['1000G_4096_MC15'],
      'Native'  : ['N2L2'           ],
      'Rezone'  : ['R2L2'           ],
      'Depop'   : ['D3L3'           ],
      'Part_num': [''               ],
   },
#CHOOI-19May17 OffSpec
   '1RK17D-LEB' : # Rezone 500G SBS
   {
      'Capacity': ['500G_4096_5400_SBS'],
      'Native'  : ['NDL2'              ],
      'Rezone'  : ['RDL2'              ],
      'Depop'   : [''                  ],
      'Part_num': [''                  ],
   },
   # '1RE172-2J0' : # Native 970G for MS
   # {
      # 'Capacity': ['970G_4096_5400'],
      # 'Native'  : ['N2L3'          ],
      # 'Rezone'  : ['R2L3'          ],
      # 'Depop'   : ['D3L3'          ],
      # 'Part_num': [''              ],
   # },
   '1RE172-8J8' : # RWLCDVR ST1000VT001 DVR 
   {
      'Capacity': ['1000G_4096_5400','500G_4096_5400'],
      'Native'  : ['N2L3'           ,''              ],
      'Rezone'  : ['R2L3'           ,'RDL3'          ],
      'Depop'   : ['D3L3'           ,''              ],
      'Part_num': [''               ,'1RE17D-'       ],
   },
   '1RE172-2J0' : # RWLCDVR ST1000VT001 MS
   {
      'Capacity': ['1000G_4096_5400'],
      'Native'  : ['N2L3'           ],
      'Rezone'  : ['R2L3'           ],
      'Depop'   : ['D3L3'           ],
      'Part_num': [''               ],
   },
   '1RK172-960' : # JAPAN EEB TV
   {
      'Capacity': ['1000G_4096_5400','500G_4096_5400','500G_4096_5400_SBS'],
      'Native'  : ['N2L3'           ,''              ,''                  ],
      'Rezone'  : ['R2L3'           ,'RDL3'          ,'RDL2'              ],
      'Depop'   : ['D3L3'           ,''              ,''                  ],
      'Part_num': [''               ,'1RK17D-'       ,'1RK17D-995'        ],
   },
   '1RK172-6E0' : # Native 1000G SBS
   {
      'Capacity': ['1000G_4096_MC15','500G_4096_5400_SBS'],
      'Native'  : ['N2L2'           ,''                  ],
      'Rezone'  : ['R2L2'           ,'RDL2'              ],
      'Depop'   : ['D3L3'           ,''                  ],
      'Part_num': [''               ,'1RK17D-'           ],
   },
   '1RK17D-6E0' : # Rezone 500G SBS
   {
      'Capacity': ['500G_4096_5400_SBS'],
      'Native'  : ['NDL2'              ],
      'Rezone'  : ['RDL2'              ],
      'Depop'   : [''                  ],
      'Part_num': [''                  ],
   },
   '2G3172-900' : # Mobile Surveillance HDD
   {
      'Capacity': ['1000G_4096_MS'     ,'1000G_4096_5400','1000G_4096_MC15','500G_4096_5400','500G_4096_5400_SBS'],
      'Native'  : ['N2L3'              ,'N2L3'           ,'N2L2'           ,''              ,''                  ],
      'Rezone'  : ['R2L3'              ,'R2L3'           ,'R2L2'           ,'RDL3'          ,'RDL2'              ],
      'Depop'   : ['D3L3'              ,'D3L3'           ,''               ,''              ,''                  ],
      'Part_num': [''                  ,'1RK172-8J8'     ,'1RK172-8J7'     ,'1RK17D-8J8'    ,'1RK17D-8J7'        ],
   },
   #====== Rosewood7 1D SED 
   '1RC172-' :    # Native 1000G SED
   {
      'Capacity': ['1000G_4096_5400'],
      'Native'  : ['N2L3'           ],
      'Rezone'  : [''               ],
      'Depop'   : [''               ],
      'Part_num': [''               ],
   },
   '1RC17D-' :    # Rezone 500G SED
   {
      'Capacity': ['500G_4096_5400','500G_4096_5400_SBS'],
      'Native'  : ['NDL3'          ,''                  ],
      'Rezone'  : ['RDL3'          ,'RDL2'              ],
      'Depop'   : [''              ,''                  ],
      'Part_num': [''              ,'1RK17D-995'        ],
   },
   '1RD172-' :    # Native 1000G SED FIPS
   {
      'Capacity': ['1000G_4096_5400','930G_4096_5400'],
      'Native'  : ['N2L3'           ,''              ],
      'Rezone'  : [''               ,'R2L3'          ],
      'Depop'   : [''               ,''              ],
      'Part_num': [''               ,'1RD172-999'    ],
   },

   #====== Rosewood7 2D LC Dev ===========#
   '1R8174-8J8' :    #Native 2T 25GMC -> 15GMC -> 1.5T
   {
      'Capacity': ['2000G_4096_5400','2000G_4096_MC15','1500G_4096_5400'],
      'Native'  : ['N4L3'           ,''               ,''               ],
      'Rezone'  : [''               ,'R4L2'           ,'RGL3'           ],
      'Depop'   : [''               ,''               ,'D3L3'           ],
      'Part_num': [''               ,'1R8174-8J7'     ,'1R817G-'        ],
   },
   '1R817G-8J8' :    # Rezone 1500G
   {
      'Capacity': ['1500G_4096_5400','1500G_4096_5400'],
      'Native'  : ['NGL3'          ,''                ],
      'Rezone'  : ['RGL3'          ,'RGL3'            ],
      'Depop'   : ['D3L3'          ,'D3L3'            ],
      'Part_num': [''              ,'1R817G-8J7'      ],
   },
   '1R8174-8J7' : # Native 2000G SBS
   {
      'Capacity': ['2000G_4096_MC15','1500G_4096_5400'],
      'Native'  : ['N4L2'           ,''               ],
      'Rezone'  : ['R4L2'           ,'RGL2'           ],
      'Depop'   : [''               ,'D3L2'           ],
      'Part_num': [''               ,'1R817G-'        ],
   },
   '1R8174-999' :    # Microsoft
   {
      'Capacity': ['1950G_4096_5400'],      #1950G for Xbox
      'Native'  : ['N4L3'           ],
      'Rezone'  : [''               ],
      'Depop'   : [''               ],
      'Part_num': [''               ],
   },  
   #====== Rosewood7 2D LC Customer ===========#
#CHOOI-19May17 OffSpec
   '1R8174-9E9' : # Native 2000G SBS
   {
      'Capacity': ['2000G_4096_MC15'],
      'Native'  : ['N4L2'           ],
      'Rezone'  : ['R4L2'           ],
      'Depop'   : [''               ],
      'Part_num': [''               ],
   },
#CHOOI-19May17 OffSpec
   '1R8174-LEB' : # Native 2000G SBS
   {
      'Capacity': ['2000G_4096_MC15'],
      'Native'  : ['N4L2'           ],
      'Rezone'  : ['R4L2'           ],
      'Depop'   : [''               ],
      'Part_num': [''               ],
   },
   '1R8174-995' : # Native 2000G SBS
   {
      'Capacity': ['2000G_4096_5400','1500G_4096_5400','1500G_4096_5400','1000G_4096_5400','1000G_4096_5400', '750G_4096_5400', '500G_4096_5400', '500G_4096_5400', '375G_4096_5400'],
      'Native'  : [           'N4L2',               '',               '',               '',               '',               '',               '',               '',               ''],
      'Rezone'  : [               '',           'RGL2',               '',               '',               '',               '',               '',               '',               ''],
      'Depop'   : [               '',               '',           'D3L2',           'D3L2',           'D2L2',           'D2L2',           'D2L2',           'D1L2',           'D1L2'],
      'Part_num': [               '',     '1R817G-995',     '1R8174-995',     '1R8174-995',     '1R8174-995',     '1R8174-995',     '1R8174-995',     '1R8174-995',     '1R8174-995'],
   },
   '1R817G-995' :    # Rezone 1500G
   {
      'Capacity': ['1500G_4096_5400'],
      'Native'  : [           'NGL2'],
      'Rezone'  : [           'RGL2'],
      'Depop'   : [           'D3L2'],
      'Part_num': [               ''],
   },
   '1R8172-995' : # Native 1000G SBS
   {
      'Capacity': ['1000G_4096_5400','1000G_4096_5400'],
      'Native'  : [           'N2L2',               ''],
      'Rezone'  : [               '',               ''],
      'Depop'   : [           'D3L2',           'D2L2'],
      'Part_num': [               '',               ''],
   },
   '1R817C-995' : # Rezone 750G SBS
   {
      'Capacity': ['750G_4096_5400'],
      'Native'  : [          'NCL2'],
      'Rezone'  : [              ''],
      'Depop'   : [          'D2L2'],
      'Part_num': [              ''],
   },
   '1R817D-995' : # Rezone 500G SBS
   {
      'Capacity': ['500G_4096_5400'],
      'Native'  : [          'NDL2'],
      'Rezone'  : [              ''],
      'Depop'   : [          'D2L2'],
      'Part_num': [              ''],
   },
   '1R8171-995' : # Native 500G SBS
   {
      'Capacity': ['500G_4096_5400','375G_4096_5400'],
      'Native'  : [          'N1L2',              ''],
      'Rezone'  : [              '',          'RAL2'],
      'Depop'   : [          'D1L2',              ''],
      'Part_num': [              '',    '1R817A-995'],
   },
   '1R817A-995' : # Native 320G SBS
   {
      'Capacity': ['375G_4096_5400'],
      'Native'  : [          'NAL2'],
      'Rezone'  : [          'RAL2'],
      'Depop'   : [          'D1L2'],
      'Part_num': [              ''],
   },

    '1R8174-6U8' : # Native 2000G SBS LBW
   {
      'Capacity': ['2000G_4096_MC15'],
      'Native'  : ['N4L2'           ],
      'Rezone'  : ['R4L2'           ],
      'Depop'   : [''               ],
      'Part_num': [''               ],
   },
#CHOOI-19May17 OffSpec
   '1R817G-9E9' :    # Rezone 1500G
   {
      'Capacity': ['1500G_4096_5400'],
      'Native'  : ['NGL2'           ],
      'Rezone'  : ['RGL2'           ],
      'Depop'   : ['D3L2'           ],
      'Part_num': [''               ],
   },
#CHOOI-19May17 OffSpec
   '1R817G-LEB' :    # Rezone 1500G
   {
      'Capacity': ['1500G_4096_5400'],
      'Native'  : ['NGL2'           ],
      'Rezone'  : ['RGL2'           ],
      'Depop'   : ['D3L2'           ],
      'Part_num': [''               ],
   },
   '1R817G-6U8' :    # Rezone 1500G LBW
   {
      'Capacity': ['1500G_4096_5400'],
      'Native'  : ['NGL2'           ],
      'Rezone'  : ['RGL2'           ],
      'Depop'   : ['D3L2'           ],
      'Part_num': [''               ],
   },
   '1R8174-' : # OEM
   {
      'Capacity': ['2000G_4096_5400'],
      'Native'  : ['N4L3'           ],
      'Rezone'  : [''               ],
      'Depop'   : [''               ],
      'Part_num': [''               ],
   },
   '1R817G-' :    # Rezone 1500G OEM
   {
      'Capacity': ['1500G_4096_5400'],
      'Native'  : ['NGL3'           ],
      'Rezone'  : ['RGL3'           ],
      'Depop'   : ['D3L3'           ],
      'Part_num': [''               ],
   },
   '2E8174-' : # Rebrand OEM
   {
      'Capacity': ['2000G_4096_5400'],
      'Native'  : ['N4L3'           ],
      'Rezone'  : [''               ],
      'Depop'   : [''               ],
      'Part_num': [''               ],
   },
   # '1RE174-2J0' : # Microsoft
   # {
      # 'Capacity': ['1950G_4096_5400'],      #1950G for Xbox
      # 'Native'  : ['N4L3'           ],
      # 'Rezone'  : [''               ],
      # 'Depop'   : [''               ],
      # 'Part_num': [''               ],
   # },   
   '1RG174-0E0' : # STD 8GB NVC OEM/HP
   {
      'Capacity': ['2000G_4096_5400'],
      'Native'  : ['N4L3'           ],
      'Rezone'  : [''               ],
      'Depop'   : [''               ],
      'Part_num': [''               ],
   },
   '1RK172-W88' : # RWLC Master&Child OEM dev BTC
   {
      'Capacity': ['1000G_4096_5400'],
      'Native'  : ['N2L3'           ],
      'Rezone'  : ['R2L3'           ],
      'Depop'   : ['D3L3'           ],
      'Part_num': [''               ],
   },
   '1RK172-W87' : # Master&Child SBS dev BTC
   {
      'Capacity': ['1000G_4096_5400'],
      'Native'  : ['N2L2'           ],
      'Rezone'  : ['R2L2'           ],
      'Depop'   : ['D3L2'           ],
      'Part_num': [''               ],
   },   
   '1RK172-P68' :
   {
      'Capacity': ['1000G_4096_MC15'],
      'Native'  : ['N2L2'           ],
      'Rezone'  : ['R2L2'           ],
      'Depop'   : ['D3L2'           ],
      'Part_num': [''               ],
   },   
#CHOOI-19May17 OffSpec
   '1RK172-P99' :
   {
      'Capacity': ['1000G_4096_MC15'],
      'Native'  : ['N2L2'           ],
      'Rezone'  : ['R2L2'           ],
      'Depop'   : ['D3L2'           ],
      'Part_num': [''               ],
   },
#CHOOI-19May17 OffSpec
   '1RK172-PLB' :
   {
      'Capacity': ['1000G_4096_MC15'],
      'Native'  : ['N2L2'           ],
      'Rezone'  : ['R2L2'           ],
      'Depop'   : ['D3L2'           ],
      'Part_num': [''               ],
   },   
   '1RE174-8J8' : # DVR DVR ST2000VT000
   {
      'Capacity': ['2000G_4096_5400'],
      'Native'  : ['N4L3'           ],
      'Rezone'  : [''               ],
      'Depop'   : [''               ],
      'Part_num': [''               ],
   },
   '1RE174-2J0' : # DVR MS ST2000VT000
   {
      'Capacity': ['2000G_4096_5400'],
      'Native'  : ['N4L3'           ],
      'Rezone'  : [''               ],
      'Depop'   : [''               ],
      'Part_num': [''               ],
   },
   '1R8174-960' : # Japan EBB TV
   {
      'Capacity': ['2000G_4096_5400'],
      'Native'  : ['N4L3'           ],
      'Rezone'  : [''               ],
      'Depop'   : [''               ],
      'Part_num': [''               ],
   },
   '1R8174-6E0' : # Native 2000G SBS
   {
      'Capacity': ['2000G_4096_MC15'],
      'Native'  : ['N4L2'           ],
      'Rezone'  : ['R4L2'           ],
      'Depop'   : [''               ],
      'Part_num': [''               ],
   },
   '2G2174-900' : # Mobile Surveillance HDD
   {
      'Capacity': ['2000G_4096_5400_MS','2000G_4096_5400','2000G_4096_MC15','1500G_4096_5400'],
      'Native'  : ['N4L3'              ,'N4L3'           ,''               ,''               ],
      'Rezone'  : [''                  ,''               ,'R4L2'           ,'RGL3'           ],
      'Depop'   : [''                  ,''               ,''               ,'D3L3'           ],
      'Part_num': [''                  ,'1R8174-8J8'     ,'1R8174-8J7'     ,'1R817G-8J8'     ],
   },   
}



'''
            Depop On The Fly

   Rules for construction of 'depop_OTF_Config' dictionary:

depop_OTF_Config = {
   <failcode>: {                                      # <failcode description>
      <failing state> : {
         '<table name>' : {
            <test name>' : {
               'Column'          : <column name>,
               'NextState'       : <next state>,
               'Head'            : <failing head>,                            # This will typically be 'HD_PHYS_PSN'
               'Comparator'      : <comparator>,                              # Valid comparators: '==', '<', '>', 'All', 'Count', 'Last', 'LastRow'
               'validFailTests'  : [],                                        # Valid failing states
               'Priority'        : <priority>,                                # Priority used if multiple tests match failing case. Highest priority is chosen, default is 0
               'Filters'         : {
                  <filter column (string)>   : (<filter comparator>, <filter value>),
      }}},
      <failing state> : {
         <table name> : {
            <test name> : {
               'Column'          : <column name>,
               'NextState'       : <next state>,
               'Head'            : <failing head>,
               'Comparator'      : <comparator>,
               'Priority'        : <priority>,
   }}}},
        ...
   }

Details:
   <failcode >       = (Integer) - Failcode to trigger this DPOTF event.
                                 - Failcode keys must be unique; multiple state / table combinations mat exist under single failcode entry.

   <failing state>   = (String)  - This is the state during which the failure occurred. For the given failcode, the failing state must match this entry.
                                 - (GOTF failure get raise between states, but the failing state is the state which just completed)
                                 - Wildcards: 'AnyState' will match any failing state.

   <validFailTests>  = (List)    - List of tests for which this failure occurred.  This applies only to failing selfTest tests; GOTF or script generated
                                    ECs will not have a test associated with them.
                                 - If this entry is populated, the failing test must be included in this list.
                                 - If this entry is omitted or empty [], no match will be attempted.

   <table name>      = (String)  - This is the DBLog table containing the information required for determing the failing head.
                                 - DPOTF is only capable of evaluating one table per test.  Compound screens are not supported at this time.

   <test name>       = (String)  - Each criteria (failcode / state) under a given Failcode must have a unique test name.
                                 - The test name is only used to keep the eligible tests separate
                                 - Multiple 'tests' may match a given failcode / state (e.g. GOTF may have multiple criteria for one table)
                                 - In the event that there are multiple tests, each will be evaluated If more than one test identifies failing heads

   <column name>     = (String)  - The column name will indicate the column name for final evaluation (based on 'Comparator')

   <next state>      = (String)  - Following a successful depop, the process will proceed to this state
                                 - Wildcards: 'LastState' and 'SameState' will return to the failing state following a successful Depop
                                 - 'NextState' will procedd to the next state in the StateTable following depop
                                 - Wildcards may be used for any Depop, but are required if 'AnyState' is used for the failing state match.

   <failing head>    = (String)  - The failing head(s) will extracted from this column of the DBLog table
                                 - HD_PHYS_PSN is typically used for the failing head.
                                 - The column used for failing head must reflect the physical head to depop

   <comparator>      = (String)  - The comparator defines how the table data will be process to determine the failing head(s)
                                 - '<', '>'           These simple rules will force the single head with the lowest or highest value for the given 'Column'
                                 - '==', 'All'        These 'greedy' comparator will select all heads (following filtering) for depop
                                                      - Cases where the test report a failing status (e.g. ERR_CODE) will use these
                                 - 'Count'            The Count option will add all (filtered) rows for each head, the head with the highest count will be selected
                                                      - For example, P_TRACK might be posted repeatedly for the failing head, the head with the most is chosen
                                 - 'Last', 'LastRow'  This feature should be used carefully.  This will seltect the head of the last row in the given table
                                                      - This presumes that the test failed and reported data for that head before ending.

    <priority>        = (Integer) - Each test under a given failcode should have a unique priority.  Priority is used to select the test if multiple tests are valid.
                                 - If multiple Depop tests are selected and find heads to depop, the priority will be applied.

   Filters:                      Each column / comparator / value filter combination will be applied to the DBLog table under review.
                                 - The order of filtering is indeterminate (at this time)
                                 - In most cases, these filters should be applied to reduce the table down to failing data only

GOTF DPOTF:
  GOTF failures occur between states but raise the failure for the previous state.
  - For GTOF ECs, the GOTF / DPOTF filters / criteria must track each other.
  - The GOTF criteria should be applied as a DPOTF filter, leaving the failing data for final evaluation, the the 'All' option will depop those heads.

Do Not Depop List:
   Failcodes found in the do not depop list 'disallowed_DPOTF_ErrCodes' has been deemed inelligible for depop.
   If added to 'depop_OTF_Config' PF3 code will fail to execute.  ECs should not be removed from this list.
'''

# Depop OTF parameters and dictionaries:
disallowed_Depop_Hds    = []
default_Depop_Hds       = [7, 6, 5, 4, 3, 2, 1, 0]
disallowed_Depop_States = ['DEPOP_OTF', 'END_TEST', 'FAIL_PROC']
allowed_Depop_Opers     = ['PRE2', ]   # ['PRE2', 'CAL2', 'FNC2',]

depop_next_head_method = {
   'PRE2'   : ['useDefaultHeadList'],
   # 'CAL2'   : ['use_P210_HeadCaps', 'useDefaultHeadList'],
   # 'FNC2'   : ['use_P172_HeadCaps', 'useDefaultHeadList'],
}

depop_OTF_Config = {
   10468: {                                           # This is the 'dummy' failcode raised by DEPOP_DEMO to trigger a DEPOP_OTF event
      'DEPOP_DEMO' : {
         'P000_DEPOP_HEADS' : {
            '1' : {
               'Column'          : 'HD_PHYS_PSN',
               'NextState'       : 'NextState',
               'Head'            : 'HD_PHYS_PSN',
               'Comparator'      : '==',
            }
         },
      },
   },
}

destroke_OTF_Config = {    # for ChkDESTROKEOTF function in State.py.
   10007: {
      'ValidState'   : ['BPINOMINAL','TRIPLET_OPTI_V2','RW_GAP_CAL','PRE_OPTI'],
      'Table'        : 'P000_SERVO_UNSAFE_FLAG2',
      'Fail_Track'   : 'TRACK_NUM',
      'Fail_Limit'   : '20000',
      'Min_Padding'  : '18000',
      'NextState'    : 'DNLD_CODE',
   },
   10352: {
      'ValidState'   : ['BPINOMINAL','TRIPLET_OPTI_V2','RW_GAP_CAL','PRE_OPTI'],
      'Table'        : 'P_TRACK',
      'Fail_Track'   : 'CYLINDER',
      'Fail_Limit'   : '20000',
      'Min_Padding'  : '18000',
      'NextState'    : 'DNLD_CODE',
   },
}

Reconfig_Niblet_Check = {
#### Only CC Tab using level "2" niblet need to specify here. Default not defined here is treated as level "3" niblet.
#### Level "3" has higher order than "2" and hence allow waterfall to lower order CC.

   '1RK...-(995|986|985|990|991|566|567|568|899|GLB)' : 2, #SBS niblet level
   '1RK...-(J87|8J7|87J|87W|E68|68E|88J|88W|W87|6E8|P68|6E0|E99|ELB|9E9|LEB|P99|PLB)' : 2, #master/child
   '1R8...-(995|950|566|567|J87|8J7|6E8|9E9|LEB|6E0|6U8|E99|ELB|9E9|LEB|P99|PLB)' : 2, #SBS niblet level
   '1KK...-(995|950)' : 2, #SBS niblet level
   '1KL...-(995|950)' : 2, #SBS niblet level
   #'1EE...-(995|950)' : 2, #SBS niblet level
   '1E9...-(995|950|500|566|567)' : 2, #SBS niblet level
}

Binning = \
{
   # template dictionary for CTUBinning support
   "9":
   {
      "ZZZ":  {"BINS" : ["#BINA", "#BINZ", "#BINC", "#BIND", "#BINE"]},
   }
}

#Regex for tiered lists
tieredPnMatrix = {
   TIER1 : ['700',], #Tier 1 tab list
   TIER2 : ['020','070',], #Tier 2 tab list
   TIER3 : ['500','566',], #Tier 3 tab list
}

defaultBottomTier = TIER3
tierRegex = '.{6}-T\d\d'
nonTierRegex = '.{6}-(?!(T\d\d))'
genericTierPN = '1DG1XX-TXX'

TCG_PN_REG = '^\d(RC|R9|RD|RA).*'
NOT_TCG_PN_REG = '^\d(?!(RC|R9|RD|RA)).*'

APPLE = '^.{6}-(700|040|701|041|042|703|704|705|706|707|044)'

# Define the states you want to run only on certain PN's- requires 'P' in Opt column in state-table
# Format is 'state': [re1, re2, re3,],
states_PN = {
   'DNLD_CODE_TCG'      : [TCG_PN_REG],
   'RESET_SMART_TCG'    : [TCG_PN_REG],
   'DNLD_CODE_TCG2'     : [TCG_PN_REG],
   'DNLD_BRG_IV'        : [TCG_PN_REG],
   'RESET_SMART_TCG2'   : [TCG_PN_REG],
   'DNLD_U_CODE'        : [NOT_TCG_PN_REG],
   'DNLD_U_CODE2'       : [NOT_TCG_PN_REG],
   'SERIAL_FMT2'        : [TCG_PN_REG],
   'RESET_AMPS'         : [APPLE,],
   'END_TEST'           : [TCG_PN_REG],
   'CUST_CFG2'          : [nonTierRegex],
   'ATTR_VAL2'          : [nonTierRegex],
   'COMMIT'             : [tierRegex], #non committed  tiers
}

# AutoCommit BG control
# 3,2,1 - Ranking. Eg 3=highest priority
# ON - Only commit to same BG. Eg STD only commit to STD, STDLG only commit to STDLG
# OFF- Can commit to other BG. OEM1A can commit to OEM1A,OEM1B,OEM1C,STD,etc
# by default, cannot cross BG
#FORCE_ACMT_BS = {'CTUA':[3,'OFF'], 'CTUB':[3,'OFF'], 'CTUC':[3,'OFF'], 'CTUD':[3,'OFF'], 'OEM1A':[3,'OFF'], 'OEM1B':[3,'OFF'], 'OEM1C':[3,'OFF'], 'OEM1D':[3,'OFF'], 'OEM1E':[3,'OFF'], 'OEM1F':[3,'OFF'], 'STD':[3,'OFF']}

if 1:
   NO_IO_CFG = {
      'NO_IO_OPER'      : ['CRT2', 'MQM2','FIN2', 'FNG2'],    # operations that can go to cold serial cells
      'NO_IO_TAB'       : ['*'],                 # part number tabs that do not need IO cells. '*' wildcard is allowed
      'NO_IO_RIMTYPE'   : ['75'],          # rimtype of cold serial cells. Script will query Host if available, if not use default
   }

   try:
      if ConfigVars[ConfigId[2]].get('PRODUCTION_MODE',0) == 0 and ConfigVars[ConfigId[2]].get('IOLESSTAB',0):
         NO_IO_CFG['NO_IO_TAB'].append("998")
         NO_IO_CFG['NO_IO_TAB'].append("997")
         NO_IO_CFG['NO_IO_TAB'].append("996")
         NO_IO_CFG['NO_IO_TAB'].append("995")
         TraceMessage("New NO_IO_CFG=%s" % NO_IO_CFG)
   except:
      pass

   try:
      import re
      from Codes import fwConfig
      TraceMessage("Current NO_IO_TAB=%s fwConfig=%s" % (NO_IO_CFG['NO_IO_TAB'], fwConfig.keys()))

      for iotab in NO_IO_CFG['NO_IO_TAB'][:]:
         for pn in fwConfig:
            if re.search(iotab, pn[-3:]) and not pn[-3:] in iotab and not pn[-3:] in NO_IO_CFG['NO_IO_TAB']:
               TraceMessage("Appending NO_IO_TAB PN=%s" % pn[-3:])
               NO_IO_CFG['NO_IO_TAB'].append(pn[-3:])

      TraceMessage("New NO_IO_TAB=%s" % NO_IO_CFG['NO_IO_TAB'])
   except:
      pass

IO_RIM_CUSTOMER = {
                   'CUSTOMER_SCREEN' : ['SY1','DV1'],  # SONY_SCREEN, Panasonic AVSCAN
                   'IO_RIMTYPE'      : ['57']
                  }
# following are from GIO ReliFunction.py to detect Apple
AppleFWSignature = 'AP'
ApplePartNum = ['700', '701', '702', '703', '704', '705', '706', '707', '708', '709', '040', '041', '042', '043', '044', '045', '046', '047', '048', '049']

retestGOTF = \
{
   "SKIP_SFWP_CHECK": 0,    # if 1, skip servo code check. Default = 0 (enable servo code check)

   "FIN2":     # operation
   {
      #"Failcode2dblog" : [10570, 10571, ],
      # 2 char CTQ bit : dictionary of attributes to send to update

      "\S": {'SET_OPER': 'CRT2', 'VALID_OPER': 'CRT2', 'RIM_TYPE': '57', 'LOOPER_COUNT': '1','NO_YIELD_REPORT':'*'},
      #"09": {'SET_OPER': 'CRT2', 'VALID_OPER': 'CRT2', 'RIM_TYPE': '75', 'LOOPER_COUNT': '1','NO_YIELD_REPORT':'*','PROC_CTRL40':'APPLE_SBS'},
      #"\S": {'SET_OPER': 'CRT2', 'VALID_OPER': 'CRT2', 'RIM_TYPE': '75', 'LOOPER_COUNT': '1','NO_YIELD_REPORT':'*','PROC_CTRL40':'APPLE_SBS'},
   },
}

############################CCV Testing for each customer############################
CCV_BS_TYPE = 'NBSATA'

SHIPHOLD_SBR_PREFIX = []
