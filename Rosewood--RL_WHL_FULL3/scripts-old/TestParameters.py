#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Test Parameters for Luxor programs - Grenada,
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/12/29 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Amazon/TestParameters.py $
# $Revision: #125 $
# $DateTime: 2016/12/29 22:40:52 $
# $Author: yihua.jiang $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Amazon/TestParameters.py#125 $
# Level: 1
#---------------------------------------------------------------------------------------------------------#

from Constants import *
from Utility import CUtility
from Test_Switches import testSwitch
Utl = CUtility()

####### PSTR Batch TimeOut #######
#PSTRTimeOut = 39.5      # PSTR Batch Timeout in hours

if testSwitch.DEPOP_TESTING:  # depop testing
   DepopTestSN = {
      # 'Serial Num' : [ head_to_depop ],
      # 'Q9400VIR'  : [0],
   }

#=== Flaw scan related: Update the dict to T94, T134 and T109 parameters.
if testSwitch.FE_0276349_228371_CHEOPSAM_SRC:
   ZPS_ACQ_SM_values = {
      "SET_XREG20" : ( 0x0029, 0x0002, 0xCEC ),  # D_TL_ZPS_LEN
      "SET_XREG21" : ( 0x002C, 0x0019, 0xC70 ),  # D_SEQ_ZPS_DLY
      "SET_XREG22" : ( 0x002C, 0x000C, 0xCF8 ),  # D_SEQ_ACQ1_LEN
      "SET_XREG23" : ( 0x002D, 0x0000, 0xC70 ),  # D_SEQ_ACQ2_LEN
      "SET_XREG24" : ( 0x002E, 0x0001, 0xC70 ),  # D_SEQ_LFSM1_LEN
      "SET_XREG25" : ( 0x0037, 0x0000, 0xC33 ),  # D_AGC_TGS_EN
   }

if testSwitch.CHEOPSAM_LITE_SOC:
   Disable_TA_CheopsaM_Lite ={
   "SET_XREG19" : ( 0xa0, 0, 0x1340 ),   # Disable TA, TASetupList
   }

   Enable_TA_CheopsaM_Lite ={
   "SET_XREG19" : ( 0xa0, 1, 0x1340 ),   # Enable TA,TASetupList 
   }

if testSwitch.WA_0000000_348432_FLAWSCAN_AMPLITUDE_DROP:
   AGC_TGS_Correction = {
      "SET_XREG25" : ( 0x0037, 0x0001, 0xC33 ),  # D_AGC_TGS_EN
      "SET_XREG26" : ( 0x0037, 0x0000, 0xC11 ),  # D_AGC_TGS_HALF - 0: 100% correction, 1: 50% correction
   }

PSTROperList = ['SCOPY','STS', 'PRE2', 'CAL2', 'FNC2']

########################### Customer Unique Options ###########################
# Table of Customer Unique options for the drive's Part Number.
# Part Number can be a Regular Expression.
# Note that if the drive's Part Number can be matched by more than one
# Regular Expression in this table, the results will be unpredicatable!
# Valid settings for each option are 'enable', 'disable' or 'default'.
optionsByPN_re = {
#   '1*' : {
#      'RVFF'               : 'default',
#      'shock sensor'       : 'default',
#      'SWOT'               : 'default',
#      'OST'                : 'default',
#      'ZGS'                : 'default',
#      'RV'                 : 'default',
#      },
   '...G..-...' : {
      'ZGS'          : 'enabled',
   },
   '.F....-...' : {
      'RV'           : 'enabled',
   },
}

# Table of Customer Unique options for the drive's Business Group.
# This table is only used if the drive's part number can't be found in the
# above part number list.
optionsByBG_re = {
   'OEM2' : {
      'RVFF'               : 'default',
      'shock sensor'       : 'default',
      'SWOT'               : 'default',
      'OST'                : 'default',
      'ZGS'                : 'default',
      },
   }

# ZGS   set CAP Byte 227 = 1
# RV    set CAP Bype 227 = 2
# "CAP_WORD" : (0x0071,0x0100,0xFF00).  offset, write_data, write_mask
setZgsFlagInCapPrm_178 = {
   'test_num' : 178,
   'prm_name' : 'setZgsFlagInCapPrm_178',
   'timeout'  : 1200,
   'spc_id'   : 1,
   "CWORD1"   : 0x0120,
   "CAP_WORD" : (0x0071,0x0100,0xFF00),
}
setRVFlagInCapPrm_178 = {
   'test_num' : 178,
   'prm_name' : 'setRVFlagInCapPrm_178',
   'timeout'  : 1200,
   'spc_id'   : 1,
   "CWORD1"   : 0x0120,
   "CAP_WORD" : (0x0071,0x0200,0xFF00),
}
resetByte227InCapPrm_178 = {
   'test_num' : 178,
   'prm_name' : 'resetByte227InCapPrm_178',
   'timeout'  : 1200,
   'spc_id'   : 1,
   "CWORD1"   : 0x0120,
   "CAP_WORD" : (0x0071,0x0000,0xFF00),
}

saveSvoRam2Flash_178 = {
   'test_num'              : 178,
   'prm_name'              : 'saveSAP2Flash_178',
   'spc_id'                : 1,
   'CWORD1'                : 0x0420,
   }

TA_LPF_prm_178 = {         # Update TA_LPF values in RAP
   'test_num'              : 178,
   'prm_name'              : 'TA_LPF_prm_178',
   'timeout'               : 1800,
   'CWORD1'                : 0x0220,
   'TA_LPF'                : 250,
   }

##################### Temperature #####################################
if cellTypeString == 'Neptune2':
   if testSwitch.FE_0258915_348429_COMMON_TWO_TEMP_CERT:
      temp_profile = {
      #Inputs to SetTemp
      #def SetTemp(reqTemp,minTemp,maxTemp,rampMode='wait'):
      'DEF'     : (25,22,28),
      'SCOPY'   : (25,22,28),
      'STS'    : (25,22,28),
      'PRE2'    : (25,22,28),
      'CAL2'    : (25,22,28),
      'FNC2'    : (25,22,28),
      'SDAT2'   : (25,22,28),

      'MQM2'    : (52,49,55),
      'CRT2'    : (52,49,55),
      'CMT2'    : (52,49,55),
      'FIN2'    : (52,49,55),
      'FNG2'    : (52,49,55),
      'AUD2'    : (52,49,55),
      'CUT2'    : (52,49,55),
      #input to tempMonitoring
      'minDriveTemp'         : 22,   #Min drive temp, to ensure wedge is push in properly to pass delta check at CRT2
      'maxDriveTemp'         : 56,   #max drive temp, to protect open/burnt sled
      'maxOverHeatCount'     : 2,    #Number of count for maximum drive temp  
      'maxCertTemp'          : 60,   #Max cert temp in PRE2, to achive the delta for VER_RAMP
      'additionalTempDelta'  : 1,    #Additional delta to heat up the drive in VER_RAMP, set to zero if want to disable
   }
      minTCCTempDifferential = 17
      TccAccMarginCold = 0                            # temp margin, default=2
      #TccAccMarginCold = 2                            # temp margin, default=2
      #requiredDeltaTempBetweenAFH2_and_AFH3 = 0       # temp delta required between AFH2 and AFH3;  ideally should be 0.
   else:
      temp_profile = {
         #Inputs to SetTemp
         #def SetTemp(reqTemp,minTemp,maxTemp,rampMode='wait'):
         'DEF'     : (46,43,55),
         'STS'     : (46,43,55),
         'PRE2'    : (46,43,55),
         'CAL2'    : (46,43,55),
         'FNC2'    : (46,43,55),
         'SDAT2'   : (46,43,55),

         'MQM2'    : (24,23,28),
         'CRT2'    : (24,23,28),
         'CMT2'    : (24,23,28),
         'FIN2'    : (24,23,28),
         'FNG2'    : (24,23,28),
         'AUD2'    : (24,23,28),
         'CUT2'    : (24,23,28),
         #input to tempMonitoring
         'minDriveTemp'          : 46,   #Min drive temp, to ensure wedge is push in properly to pass delta check at CRT2
         'maxDriveTemp'          : 56,   #Max drive temp, to protect open/burnt sled
         'maxOverHeatCount'      : 2,    #Number of count for maximum drive temp  
      }
      minTCCTempDifferential = 17                      # temp delta required between AFH3 and AFH4;  ideally > 20C. Default=19
      #TccAccMargin = 0                                # temp margin, default=0
      #TccAccMarginCold = 2                            # temp margin, default=2
      #requiredDeltaTempBetweenAFH2_and_AFH3 = 0       # temp delta required between AFH2 and AFH3;  ideally should be 0.

else:
   if testSwitch.FE_0258915_348429_COMMON_TWO_TEMP_CERT:
      temp_profile = {
      #Inputs to SetTemp
      #def SetTemp(reqTemp,minTemp,maxTemp,rampMode='wait'):
      'DEF'     : (25,22,28),
      'SCOPY'   : (25,22,28),
      'STS'     : (25,22,28),
      'PRE2'    : (25,22,28),
      'CAL2'    : (25,22,28),
      'FNC2'    : (25,22,28),
      'SDAT2'   : (25,22,28),

      'MQM2'    : (52,49,55),
      'CRT2'    : (52,49,55),
      'CMT2'    : (52,49,55),
      'FIN2'    : (52,49,55),
      'FNG2'    : (52,49,55),
      'AUD2'    : (52,49,55),
      'CUT2'    : (52,49,55),
      #input to tempMonitoring
      'minDriveTemp'         : 22,   #Min drive temp, to ensure wedge is push in properly to pass delta check at CRT2
      'maxDriveTemp'          : 56,   #Max drive temp, to protect open/burnt sled - Not N2, not critical
      'maxOverHeatCount'      : 2,    #Number of count for maximum drive temp - Not N2, not critical 
      'maxCertTemp'          : 60,   #Max cert temp in PRE2, to achive the delta for VER_RAMP
      'additionalTempDelta'  : 1,    #Additional delta to heat up the drive in VER_RAMP, set to zero if want to disable
    }
      minTCCTempDifferential = 17
      TccAccMarginCold = 0                            # temp margin, default=2

   else:
      temp_profile = {
         #Inputs to SetTemp
         #def SetTemp(reqTemp,minTemp,maxTemp,rampMode='wait'):
         'DEF'     : (46,43,55),
         'SCOPY'   : (46,43,55),
         'STS'     : (46,43,55),
         'PRE2'    : (46,43,55),
         'CAL2'    : (46,43,55),
         'FNC2'    : (46,43,55),
         'SDAT2'   : (46,43,55),

         'MQM2'    : (22,20,28),
         'CRT2'    : (22,20,28),
         'CMT2'    : (22,20,28),
         'FIN2'    : (22,20,28),
         'FNG2'    : (22,20,28),
         'AUD2'    : (22,20,28),
         'CUT2'    : (22,20,28),
         #input to tempMonitoring
         'minDriveTemp'          : 45,   #Min drive temp, to ensure wedge is push in properly to pass delta check at CRT2
         'maxDriveTemp'         : 56,   #max drive temp, to protect open/burnt sled
         'maxOverHeatCount'     : 2,
      }
if testSwitch.FE_0251909_480505_NEW_TEMP_PROFILE_FOR_ROOM_TEMP_PRE2:
   temp_profile = {
      #Inputs to SetTemp
      #def SetTemp(reqTemp,minTemp,maxTemp,rampMode='wait'):
      'DEF'     : (25,20,30),
      'SCOPY'   : (25,20,30),
      'STS'     : (25,20,30),
      'PRE2'    : (25,20,30),
      'CAL2'    : (25,20,30),
      'FNC2'    : (25,20,30),
      'SDAT2'   : (25,20,30),

      'MQM2'    : (52,50,60),
      'CRT2'    : (52,50,60),
      'CMT2'    : (52,50,60),
      'FIN2'    : (52,50,60),
      'FNG2'    : (52,50,60),
      'AUD2'    : (52,50,60),
      'CUT2'    : (52,50,60),
   }
   minTCCTempDifferential = 17                      # temp delta required between AFH3 and AFH4;  ideally > 20C. Default=19

# Add the state where cell and drive temp will be recorded right after the state completion.
temperatureLoggingList = {
   #"PRE2": ['AFH1','PARTICLE_SWP','AFH2','WRT_SIM_FILES2'],
   "SCOPY": 'ALL',
   "STS"  : 'ALL',
   "PRE2": 'ALL',
   "CAL2": 'ALL',
   #"CRT2": ['VER_RAMP','AFH4'],
   "FNC2": 'ALL',
   "CRT2": 'ALL',
   "MQM2": 'ALL',
   "FIN2": 'ALL',
}

# Define the thermal coefficient for N2 - 'MobileTC', 'SFF5mmTC', 'EnterpriseTC' or 'CutoutTC'
ThermalCoefficients = {
   #'MobileTC'     : ['ROSEWOOD7', 'ROSEWOOD71D', 'ROSEWOOD72D'],
   #'SFF5mmTC'     : ['CHENGAI'],
   #'EnterpriseTC' : [],
   #'CutoutTC'     : [],
   'CoverSealTC'    : ['COTTONWOOD','ROSEWOOD7', 'ROSEWOOD71D', 'ROSEWOOD72D', 'ROSEWOODLC1D', 'ROSEWOODLC2D', 'ROSEWOODLC'],  #For drive that has cover seal such as Rosewood
}

if testSwitch.FE_0258915_348429_COMMON_TWO_TEMP_CERT :
    fanSpeed_profile = {
          'ATTRIBUTE'             : 'nextOper',
          'DEFAULT'               : 'default',
          'default'               : (1570,2610),
          #Add unique fan speed settings for each operation( dFan,eFan))
          'SCOPY'                 : (2270, 1819),
          'STS'                   : (2270, 1819),
          'PRE2'                  : (2270, 1819),
          'CAL2'                  : (2270, 1819),
          'FNC2'                  : (2270, 1819),
          # Default fan speed is used for all IO slot operations
       }
else:
    fanSpeed_profile = {
          'ATTRIBUTE'             : 'nextOper',
          'DEFAULT'               : 'default',
          'default'               : (2360,2610),
          #Add unique fan speed settings for each operation( dFan,eFan))
          'SCOPY'                 : (1613, 1819),
          'STS'                  : (1613, 1819),
          'PRE2'                  : (1613, 1819),
          'CAL2'                  : (1613, 1819),
          'FNC2'                  : (1613, 1819),
          # Default fan speed is used for all IO slot operations
       }

temp_profile_by_head ={
   # Special control temperature by Oven by head for HDSTR_SP Tester
   #OPER                   : {'SN[1:3]:(reqTemp,minTemp,maxTemp)},
   'SCOPY'                 : {'1D':(46, 41, 53),'1E':(46, 41, 53),'1F':(46, 41, 53)},
   'STS'                  : {'1D':(46, 41, 53),'1E':(46, 41, 53),'1F':(46, 41, 53)},
   'PRE2'                  : {'1D':(46, 41, 53),'1E':(46, 41, 53),'1F':(46, 41, 53)},
   'CAL2'                  : {'1D':(46, 41, 53),'1E':(46, 41, 53),'1F':(46, 41, 53)},
   'FNC2'                  : {'1D':(46, 41, 53),'1E':(46, 41, 53),'1F':(46, 41, 53)},
   }


replugECMatrix = {
   #Move drive to new cell on error code.
   #To filter by test number or test state or both, add them to list, e.g. 14013 : [598,"READ_XFER"],
   #For operation not defined here, 'default' setup will be used
   'ATTRIBUTE': 'nextOper',
   'DEFAULT'  : 'default',

   'SCOPY'    : {
                 #"SEND_NEW_OPER" : "*",
                 42226 : [ ], #Tester Pwr/Temp Ctrl-Drive Temp too cold
                 11087 : [ ], #Tester Misc Serial Protocol Error (CM/Cell)
                 10340 : ["INIT","DNLD_CODE"], #Loss Communication
                 11104 : [ ], # VCLimitTrip
                 42180 : [ ], # FailedCheckTemperature
                },
   'STS'      : {
                 #"SEND_NEW_OPER" : "*",
                 42226 : [ ], #Tester Pwr/Temp Ctrl-Drive Temp too cold
                 11087 : [ ], #Tester Misc Serial Protocol Error (CM/Cell)
                 10340 : ["INIT","DNLD_CODE"], #Loss Communication
                 11104 : [ ], # VCLimitTrip
                 42180 : [ ], # FailedCheckTemperature
                },
   'PRE2'     : {
                 #"SEND_NEW_OPER" : "*",
                 42226 : [ ], #Tester Pwr/Temp Ctrl-Drive Temp too cold
                 11087 : [ ], #Tester Misc Serial Protocol Error (CM/Cell)
                 10340 : ["INIT","DNLD_CODE"], #Loss Communication
                 11104 : [ ], # VCLimitTrip
                 42180 : [ ], # FailedCheckTemperature
                },

   'CAL2'     : {
                 #"SEND_NEW_OPER" : "*",
                 42226 : [ ], #Tester Pwr/Temp Ctrl-Drive Temp too cold
                 #11087 : [ ], #Tester Misc Serial Protocol Error (CM/Cell)
                 10340 : ["INIT"], #Loss Communication
                },

   'FNC2'     : {
                 #"SEND_NEW_OPER" : "*",
                 10340 : ["INIT"], #Loss Communication
                 42180 : [ ], # FailedCheckTemperature
                },

   'CRT2'     : {
                 #"SEND_NEW_OPER" : "*",
                 10340 : ["INIT"], #Loss Communication
                 12517 : [ ], #Two Temp Cert Failure (too hot), failed temperature delta
                 42180 : [ ], # FailedCheckTemperature
                },

   'FIN2'     : {
                 #"SEND_NEW_OPER" : "*",
                 10340 : ["INIT"], #Loss Communication
                 11187 : [ ],
                 12361 : ["VOLTAGE_HL"], #Voltage Nom/Nom
                 12364 : ["VOLTAGE_HL"], #Voltage High/Nom
                 12367 : ["VOLTAGE_HL"], #Voltage Low/Nom
                 12657 : [ ], #Seq DMA Write Error
                 13401 : [ ], #Download CPC APP/USB1/USB2 failed
                 13420 : ["INIT"],
                 13424 : [ ], #Drive not ATA ready
                 13452 : [ ], #Command Set Failure
                 14001 : [ ], #Iface SATA - Undefined Error
                 14005 : [ ], #SATA wait for drive ready
                 14012 : [ ], #Iface SATA - bad block
                 14016 : [ ], #Iface SATA - media change requested
                 14017 : [ ], #Aborted command
                 14026 : [ ], #UDMA crc error
                 14029 : [ ], #Drive encountered problem
                 14031 : [ ], #Drive Not Ready to Check Status
                 14034 : [ ], #Buffer Too Small
                 14037 : [ ],
                 14723 : [ ], #Zero Verify failure in CUT2 operation
                 14746 : [ ], # C410 screen failure
                 },

   'CUT2'     : {
                 #"SEND_NEW_OPER" : "*",
                 12657 : [ ], #Seq DMA Write Error
                 14005 : [ ], #SATA wait for drive ready
                 14026 : [ ], #UDMA crc error
                },

   'default'  : {
                 #"SEND_NEW_OPER" : "*",
                 # 11197 : [], #cell fan speed trip
                 # 11105 : [], #interlock trip (fan/hotplug)
                 # 11045 : [], #bad plug bits
                 # 11061 : [], #bad riser data
                 # 11060 : [], #cell temperature ramp fail
                },
}


##################### General #####################################

# Set up family lists:
if testSwitch.ROSEWOOD7:
    program = 'Rosewood7'
elif testSwitch.CHENGAI:
    program = 'Chengai'

## Set product name, this will be used to determine which GOTF file to use
ProductName = program
HDTSP_Recycle_PCBA = [13458,13459,14013,14719,13455,10398,14029]
HDSTR_SP_HD = ['1'] # Disallow 1 head drives from running in HDSTR
HDSTRNEXTRUN = 'CRT2'
PRE_CHECK_TEMP_STATES = ['A_FLAWSCAN']
POST_CHECK_TEMP_STATES = ['VBAR_ZAP','ZAP','AFH1','AFH2','AFH3','DGTL_FLWSCN']

#CHOOI-18May17 OffSpec
# CRITICAL_TEMP_MIN = 40
# CRITICAL_TEMP_MAX = 65
CRITICAL_TEMP_MIN = 30
CRITICAL_TEMP_MAX = 70

HDSTR_CHECK_TEMP_STATE = ['INIT', 'DNLD_CODE', 'SETUP_PROC', 'PCBA_SCRN','VCM_OFFSET_SCRN', 'HEAD_CAL','GMR_RES_0', 'END_TEST', 'DNLD_SF3CODE', 'DNLD_F3CODE', 'DISPLAY_G', 'ENC_WR_SCRN', 'SERIAL_FMT', 'RE_FORMAT', 'FAIL_PROC']
Min_Freq_Range_Hookup = 13075
Max_Freq_Range_Hookup = 14425
myDefaultPN = DriveAttributes.get('PART_NUM', ConfigVars[CN].get('PartNum', '9WN144'))
specTA_CNT = 50
specVerFlaws = 8000
prm_DownloadCodeTimeout = 300


staticDepopSerialNum = {   # For 2D drive with 1 dummy head
   'C0'  : 0,
   'C7'  : 1,
   'C8'  : 2,
   'BZ'  : 3,
   'F4'  : 0,
   'F8'  : 0,
   'F5'  : 3,
   'F9'  : 3,
}

RWLC1D_PN = { # Rosewood7 2-hdr HDA
       #RW7 1D non-SED
      '1RK172':{'FAM_ID':(0xA5,),'PFM_ID':(0x03,),'HD_COUNT':(2,),'DATE':(0xFFFF,0xFFFF,),}, # 1000G (N)
      '2E7172':{'FAM_ID':(0xA5,),'PFM_ID':(0x03,),'HD_COUNT':(2,),'DATE':(0xFFFF,0xFFFF,),}, # 1000G (N)
      '1RK17C':{'FAM_ID':(0xA5,),'PFM_ID':(0x04,),'HD_COUNT':(2,),'DATE':(0xFFFF,0xFFFF,),}, #  750G (R)
      '1RK17D':{'FAM_ID':(0xA5,),'PFM_ID':(0x0F,),'HD_COUNT':(2,),'DATE':(0xFFFF,0xFFFF,),}, #  500G (R)
      '2E717D':{'FAM_ID':(0xA5,),'PFM_ID':(0x0F,),'HD_COUNT':(2,),'DATE':(0xFFFF,0xFFFF,),}, #  500G (R)
      #RW7 1D non-SED ZGS
      '1RKG72':{'FAM_ID':(0xA5,),'PFM_ID':(0x03,),'HD_COUNT':(2,),'DATE':(0xFFFF,0xFFFF,),}, # 1000G (N)
      #RW7 1D SED
      '1RC172':{'FAM_ID':(0xA5,),'PFM_ID':(0x03,),'HD_COUNT':(2,),'DATE':(0xFFFF,0xFFFF,),}, # 1000G (N)
      '1RC17D':{'FAM_ID':(0xA5,),'PFM_ID':(0x0F,),'HD_COUNT':(2,),'DATE':(0xFFFF,0xFFFF,),}, #  500G (R)
      #RW7 1D SED FIPS
      '1RD172':{'FAM_ID':(0xA5,),'PFM_ID':(0x03,),'HD_COUNT':(2,),'DATE':(0xFFFF,0xFFFF,),}, # 1000G (N)
      #RW7 1D DVR
      '1RE172':{'FAM_ID':(0xA5,),'PFM_ID':(0x03,),'HD_COUNT':(2,),'DATE':(0xFFFF,0xFFFF,),}, # 1000G (N)
      '1RE17D':{'FAM_ID':(0xA5,),'PFM_ID':(0x0F,),'HD_COUNT':(2,),'DATE':(0xFFFF,0xFFFF,),}, #  500G (R)
      #RW7 1D Mobile Surveillance HDD
      '2G3172':{'FAM_ID':(0xA5,),'PFM_ID':(0x03,),'HD_COUNT':(2,),'DATE':(0xFFFF,0xFFFF,),}, # 1000G (N)
      #RW7 1D 1-head Capacity *** EVAL ONLY ***
      '1RK171':{'FAM_ID':(0xA5,),'PFM_ID':(0x0F,),'HD_COUNT':(1,),'DATE':(0xFFFF,0xFFFF,),}, #  500G (N)
      '1RK17A':{'FAM_ID':(0xA5,),'PFM_ID':(0x06,),'HD_COUNT':(1,),'DATE':(0xFFFF,0xFFFF,),}, #  375G (R)      
      #RW7 1D interim Capacity *** EVAL ONLY ***
      #'1RK172-999':{'FAM_ID':(0xA5,),'PFM_ID':(0x0A,),'HD_COUNT':(2,),'DATE':(0xFFFF,0xFFFF,),}, # 930G (N)
      '1RK172-999':{'FAM_ID':(0xA5,),'PFM_ID':(0x10,),'HD_COUNT':(2,),'DATE':(0xFFFF,0xFFFF,),}, # 970G (N)
      '1RE172-2J0':{'FAM_ID':(0xA5,),'PFM_ID':(0x10,),'HD_COUNT':(2,),'DATE':(0xFFFF,0xFFFF,),}, # 970G (N)
      '1RK172-996':{'FAM_ID':(0xA5,),'PFM_ID':(0x0A,),'HD_COUNT':(2,),'DATE':(0xFFFF,0xFFFF,),}, # 930G (N)
      #'1RK172-997':{'FAM_ID':(0xA5,),'PFM_ID':(0x0B,),'HD_COUNT':(2,),'DATE':(0xFFFF,0xFFFF,),}, # 870G (N)
      #'1RK172-996':{'FAM_ID':(0xA5,),'PFM_ID':(0x0C,),'HD_COUNT':(2,),'DATE':(0xFFFF,0xFFFF,),}, # 810G (N)
      '1RC172-995':{'FAM_ID':(0xA5,),'PFM_ID':(0x0A,),'HD_COUNT':(2,),'DATE':(0xFFFF,0xFFFF,),}, # 930G (N) temp use -995 as interim cap 930GB
      '1RD172-995':{'FAM_ID':(0xA5,),'PFM_ID':(0x0A,),'HD_COUNT':(2,),'DATE':(0xFFFF,0xFFFF,),}, # 930G (N) temp use -995 as interim cap 930GB

      #RW7H 1D non-SED
      '1U7172':{'FAM_ID':(0xA5,),'PFM_ID':(0x03,),'HD_COUNT':(2,),'DATE':(0xFFFF,0xFFFF,),}, # 1000G (N)
      '1U717D':{'FAM_ID':(0xA5,),'PFM_ID':(0x0F,),'HD_COUNT':(2,),'DATE':(0xFFFF,0xFFFF,),}, #  500G (R)
      #RW7H 1D SED
      '1U8172':{'FAM_ID':(0xA5,),'PFM_ID':(0x03,),'HD_COUNT':(2,),'DATE':(0xFFFF,0xFFFF,),}, # 1000G (N)
      '1U817D':{'FAM_ID':(0xA5,),'PFM_ID':(0x0F,),'HD_COUNT':(2,),'DATE':(0xFFFF,0xFFFF,),}, #  500G (R)
      #RW7H 1D SED FIPS
      '1U9172':{'FAM_ID':(0xA5,),'PFM_ID':(0x03,),'HD_COUNT':(2,),'DATE':(0xFFFF,0xFFFF,),}, # 1000G (N)
      '1U917D':{'FAM_ID':(0xA5,),'PFM_ID':(0x0F,),'HD_COUNT':(2,),'DATE':(0xFFFF,0xFFFF,),}, #  500G (R)
      #RW7H 1D non-SED 4GB
      '1UA172':{'FAM_ID':(0xA5,),'PFM_ID':(0x03,),'HD_COUNT':(2,),'DATE':(0xFFFF,0xFFFF,),}, # 1000G (N)
      '1UA17D':{'FAM_ID':(0xA5,),'PFM_ID':(0x0F,),'HD_COUNT':(2,),'DATE':(0xFFFF,0xFFFF,),}, #  500G (R)
      #RW7H 1D SED 4GB
      '1UB172':{'FAM_ID':(0xA5,),'PFM_ID':(0x03,),'HD_COUNT':(2,),'DATE':(0xFFFF,0xFFFF,),}, # 1000G (N)
      '1UB17D':{'FAM_ID':(0xA5,),'PFM_ID':(0x0F,),'HD_COUNT':(2,),'DATE':(0xFFFF,0xFFFF,),}, #  500G (R)
      #RW7H 1D SED FIPS 4GB
      '1UC172':{'FAM_ID':(0xA5,),'PFM_ID':(0x03,),'HD_COUNT':(2,),'DATE':(0xFFFF,0xFFFF,),}, # 1000G (N)
      '1UC17D':{'FAM_ID':(0xA5,),'PFM_ID':(0x0F,),'HD_COUNT':(2,),'DATE':(0xFFFF,0xFFFF,),}, #  500G (R)
      #RW7H 1D interim Capacity *** EVAL ONLY ***
      '1U7172-999':{'FAM_ID':(0xA5,),'PFM_ID':(0x0A,),'HD_COUNT':(2,),'DATE':(0xFFFF,0xFFFF,),}, #  930G (N)
      '1U7172-997':{'FAM_ID':(0xA5,),'PFM_ID':(0x03,),'HD_COUNT':(2,),'DATE':(0xFFFF,0xFFFF,),}, # 1000G (N) non-SDnD
      '1U7172-996':{'FAM_ID':(0xA5,),'PFM_ID':(0x0A,),'HD_COUNT':(2,),'DATE':(0xFFFF,0xFFFF,),}, #  930G (N) non-SDnD
      '1UA172-999':{'FAM_ID':(0xA5,),'PFM_ID':(0x0A,),'HD_COUNT':(2,),'DATE':(0xFFFF,0xFFFF,),}, #  930G (N)
      '1UA172-997':{'FAM_ID':(0xA5,),'PFM_ID':(0x0B,),'HD_COUNT':(2,),'DATE':(0xFFFF,0xFFFF,),}, #  870G (N)
      '1UA172-996':{'FAM_ID':(0xA5,),'PFM_ID':(0x0C,),'HD_COUNT':(2,),'DATE':(0xFFFF,0xFFFF,),}, #  810G (N)
}
RWLC2D_PN ={ # Rosewood7 4-hdr HDA
      #RW7 2DLC non-SED
      '1R8174':{'FAM_ID':(0xA5,),'PFM_ID':(0x01,),'HD_COUNT':(4,),'DATE':(0xFFFF,0xFFFF,),}, # 2000G (N)
      '2E8174':{'FAM_ID':(0xA5,),'PFM_ID':(0x01,),'HD_COUNT':(4,),'DATE':(0xFFFF,0xFFFF,),}, # 2000G (N)
      '1R817G':{'FAM_ID':(0xA5,),'PFM_ID':(0x02,),'HD_COUNT':(4,),'DATE':(0xFFFF,0xFFFF,),}, # 1500G (R)
      #RW7 2DLC non-SED ZGS
      '1R8G74':{'FAM_ID':(0xA5,),'PFM_ID':(0x01,),'HD_COUNT':(4,),'DATE':(0xFFFF,0xFFFF,),}, # 2000G (N)
      #RW7 2DLC SED
      '1R9174':{'FAM_ID':(0xA5,),'PFM_ID':(0x01,),'HD_COUNT':(4,),'DATE':(0xFFFF,0xFFFF,),}, # 2000G (N)
      #RW7 2DLC SED FIPS
      '1RA174':{'FAM_ID':(0xA5,),'PFM_ID':(0x01,),'HD_COUNT':(4,),'DATE':(0xFFFF,0xFFFF,),}, # 2000G (N)
      #RW7 1D/2DLC 1-head Capacity *** EVAL ONLY ***
      '1R8171':{'FAM_ID':(0xA5,),'PFM_ID':(0x0F,),'HD_COUNT':(1,),'DATE':(0xFFFF,0xFFFF,),}, #  500G (N)
      '1R817A':{'FAM_ID':(0xA5,),'PFM_ID':(0x06,),'HD_COUNT':(1,),'DATE':(0xFFFF,0xFFFF,),}, #  375G (R)
      #BIG BANG Project 2D rezoned to 1T with 1D pn SBS
      '1RK172':{'FAM_ID':(0xA5,),'PFM_ID':(0x03,),'HD_COUNT':(4,),'DATE':(0xFFFF,0xFFFF,),}, # 1000G (N) 1TB      for SBS
      #RW7 2DLC DVR
      '1RE174':{'FAM_ID':(0xA5,),'PFM_ID':(0x01,),'HD_COUNT':(4,),'DATE':(0xFFFF,0xFFFF,),}, # 2000G (N)
      #RW7 2DLC Mobile Surveillance HDD
      '2G2174':{'FAM_ID':(0xA5,),'PFM_ID':(0x01,),'HD_COUNT':(4,),'DATE':(0xFFFF,0xFFFF,),}, # 2000G (N)
      #Microsoft xbox 2D 
      '1RE174-2J0':{'FAM_ID':(0xA5,),'PFM_ID':(0x11,),'HD_COUNT':(4,),'DATE':(0xFFFF,0xFFFF,),}, # 1950G (N) xbox  
      '1R8174-999':{'FAM_ID':(0xA5,),'PFM_ID':(0x11,),'HD_COUNT':(4,),'DATE':(0xFFFF,0xFFFF,),}, # 1950G (N) xbox  
      #RW7 1D using 2D *** EVAL ONLY ***
      '1R8172':{'FAM_ID':(0xA5,),'PFM_ID':(0x03,),'HD_COUNT':(2,),'DATE':(0xFFFF,0xFFFF,),}, # 1000G (N)
      '1R817C':{'FAM_ID':(0xA5,),'PFM_ID':(0x04,),'HD_COUNT':(2,),'DATE':(0xFFFF,0xFFFF,),}, #  750G (R)
      '1R817D':{'FAM_ID':(0xA5,),'PFM_ID':(0x0F,),'HD_COUNT':(2,),'DATE':(0xFFFF,0xFFFF,),}, #  500G (R)
      '1R8172-999':{'FAM_ID':(0xA5,),'PFM_ID':(0x0A,),'HD_COUNT':(2,),'DATE':(0xFFFF,0xFFFF,),}, # 930G (N)
      #RW7 2D interim Capacity *** EVAL ONLY ***
      #'1R8174-999':{'FAM_ID':(0xA5,),'PFM_ID':(0x07,),'HD_COUNT':(4,),'DATE':(0xFFFF,0xFFFF,),}, # 1860G (N)
      '1R8174-997':{'FAM_ID':(0xA5,),'PFM_ID':(0x08,),'HD_COUNT':(4,),'DATE':(0xFFFF,0xFFFF,),}, # 1740G (N)
      '1R8174-996':{'FAM_ID':(0xA5,),'PFM_ID':(0x09,),'HD_COUNT':(4,),'DATE':(0xFFFF,0xFFFF,),}, # 1620G (N)

      #RW7H 2D non-SED
      '1RG174':{'FAM_ID':(0xA5,),'PFM_ID':(0x01,),'HD_COUNT':(4,),'DATE':(0xFFFF,0xFFFF,),}, # 2000G (N)
      #RW7H 2D SED
      '1RH174':{'FAM_ID':(0xA5,),'PFM_ID':(0x01,),'HD_COUNT':(4,),'DATE':(0xFFFF,0xFFFF,),}, # 2000G (N)
      #RW7H 2D SED FIPS
      '1RJ174':{'FAM_ID':(0xA5,),'PFM_ID':(0x01,),'HD_COUNT':(4,),'DATE':(0xFFFF,0xFFFF,),}, # 2000G (N)
      #RW7H 2D non-SED 4GB
      '1U4174':{'FAM_ID':(0xA5,),'PFM_ID':(0x01,),'HD_COUNT':(4,),'DATE':(0xFFFF,0xFFFF,),}, # 2000G (N)
      '1U4172':{'FAM_ID':(0xA5,),'PFM_ID':(0x03,),'HD_COUNT':(2,),'DATE':(0xFFFF,0xFFFF,),}, # 1000G (N)
      '1U417C':{'FAM_ID':(0xA5,),'PFM_ID':(0x04,),'HD_COUNT':(2,),'DATE':(0xFFFF,0xFFFF,),}, #  750G (R)
      #RW7H 2D SED 4GB
      '1U5174':{'FAM_ID':(0xA5,),'PFM_ID':(0x01,),'HD_COUNT':(4,),'DATE':(0xFFFF,0xFFFF,),}, # 2000G (N)
      #RW7H 2D SED FIPS 4GB
      '1U6174':{'FAM_ID':(0xA5,),'PFM_ID':(0x01,),'HD_COUNT':(4,),'DATE':(0xFFFF,0xFFFF,),}, # 2000G (N)
      #RW7H 2D interim Capacity *** EVAL ONLY ***
      '1RG174-999':{'FAM_ID':(0xA5,),'PFM_ID':(0x07,),'HD_COUNT':(4,),'DATE':(0xFFFF,0xFFFF,),}, # 1860G (N)
      '1RG174-997':{'FAM_ID':(0xA5,),'PFM_ID':(0x08,),'HD_COUNT':(4,),'DATE':(0xFFFF,0xFFFF,),}, # 1740G (N)
      '1RG174-996':{'FAM_ID':(0xA5,),'PFM_ID':(0x09,),'HD_COUNT':(4,),'DATE':(0xFFFF,0xFFFF,),}, # 1620G (N)
      '1U4174-999':{'FAM_ID':(0xA5,),'PFM_ID':(0x07,),'HD_COUNT':(4,),'DATE':(0xFFFF,0xFFFF,),}, # 1860G (N)
      '1U4174-997':{'FAM_ID':(0xA5,),'PFM_ID':(0x08,),'HD_COUNT':(4,),'DATE':(0xFFFF,0xFFFF,),}, # 1740G (N)
      '1U4174-996':{'FAM_ID':(0xA5,),'PFM_ID':(0x09,),'HD_COUNT':(4,),'DATE':(0xFFFF,0xFFFF,),}, # 1620G (N)      
}
RWLC2D_3H_PN = { # Rosewood7 3-hdr HDA
      #RW7 2D, Dummy H3
      '1RK172':{'FAM_ID':(0xA5,),'PFM_ID':(0x03,),'HD_COUNT':(4,),'DATE':(0xFFFF,0xFFFF,),}, # 1000G (D)
}
###################### PART NUMBER START ###########################################
familyInfoBySerialNum = {
   'DE': RWLC1D_PN,
   'ES': RWLC1D_PN,
   'F6': RWLC1D_PN,
   '93': RWLC1D_PN,
   'CB': RWLC1D_PN,
   'C0': RWLC2D_3H_PN,
   'C7': RWLC2D_3H_PN,
   'C8': RWLC2D_3H_PN,
   'BZ': RWLC2D_3H_PN,
   'F4': RWLC2D_3H_PN,
   'F5': RWLC2D_3H_PN,
   'F8': RWLC2D_3H_PN,
   'F9': RWLC2D_3H_PN,
   'DZ': RWLC2D_PN,
   'F7': RWLC2D_PN,
   '94': RWLC2D_PN,
   'CC': RWLC2D_PN,
}
familyInfo = familyInfoBySerialNum[HDASerialNumber[1:3]]

#CHOOI-19May17 OffSpec
#RetailTabList = ['567','566','995','J87','8J7','87J','6E8','6U8']
RetailTabList = ['567','566','995','J87','8J7','87J','6E8','6U8','E99','ELB','9E9','LEB','P99','PLB']

RetailTabMasspro = {
   'ATTRIBUTE'       : 'IS_2D_DRV',
   'DEFAULT'         : 0,
   0                 : {
       'ATTRIBUTE'       : 'CAPACITY_PN',
       'DEFAULT'         : '1000G',
       '500G'            : '1RK17D-' + getattr(testSwitch, 'DEFAULT_STD_TAB', '6E8'), # temp change from 995 to 566
       '1000G'           : '1RK172-' + getattr(testSwitch, 'DEFAULT_STD_TAB', '6E8'), # temp change from 995 to 566
   },
   1                 : {
       'ATTRIBUTE'       : 'CAPACITY_PN',
       'DEFAULT'         : '2000G',
       '1500G'           : '1R817G-' + getattr(testSwitch, 'DEFAULT_STD_TAB', '6E8'), # temp change from 995 to 566
       '2000G'           : '1R8174-' + getattr(testSwitch, 'DEFAULT_STD_TAB', '6E8'), # temp change from 995 to 566
   },
}
# For 10137 improvement, a new SBS tab on LC2D(2T/1.5T) is created.
# And this new tab need a new servo code with LBW
# All other tabs are with a servo code with HBW
RetailTabWithLBWServoCode = {
   10137: {
      'ATTRIBUTE' : 'IS_2D_DRV',
      'DEFAULT'   : 0,
      0           : '',
      1           : {
         'ATTRIBUTE' : 'CAPACITY_PN',
         'DEFAULT'   : '2000G',
         '1500G'     : '1R817G-6U8', 
         '2000G'     : '1R8174-6U8', 
         },
      },
   }
#--------- Special PN list, although it's STD, but these PN should use OEM setting ---------#
SPE_PN_LIST = ['998','J88','8J8','88J','0E0']

if testSwitch.WA_0247335_348085_WATERFALL_WITH_10_DIGITS_PARTNUMBER:
    SPE_PN_LIST = SPE_PN_LIST + ['992','991','993',]

#--------- PN that can downgrade from STD/OEM to STD/SBS ---------#
#SPEWAF_PN_LIST = ['1R8174-998', '1R8174-900', '1RK172-998', '1KK162-998', '1RK171-998', '1R8171-998', '1R8172-998']
PN_RECFG_SBS_LIST = []
##########################   (DEV|STD|ACR|ASS|LVC|SAM|PNS|???),   #######(DEV|STD)
EC_RECFG_SBS_LIST = []

VbarPartNumCluster = [''] * 9
###################### PART NUMBER END ###########################################

####################### FOF Screen use #################################
##### LUL_Profile_Const #####
SPINDLE_RPM = 5408
K_RPM_CNT = 167000000
VEL_BITS_PER_IPS = 17587
K_DAC = 32768
K_PA = 490

# Build family lists, based on physical number of heads
# Dynamically build up the part number lists (oneHdPN, twoHdPN, etc.) so we don't have to maintain them by hand
num2Name = {
   '1' : 'one',
   '2' : 'two',
   '3' : 'three',
   '4' : 'four',
   '5' : 'five',
   '6' : 'six',
   '7' : 'seven',
   '8' : 'eight',
   '10': 'ten',
}
for v in num2Name.values():
   exec('%sHdPN = []' % v)
for pNum,info in familyInfo.items():
   exec("%sHdPN.append('%s')" % (num2Name[str(info['HD_COUNT'][0])], pNum))

fourKSectorPN = ()  # Part numbers that use 4k sectors

if not ConfigVars[CN].get('numHeads',0) == 0:
   for key in familyInfo.keys():
      familyInfo[key]['HD_COUNT'] = (ConfigVars[CN].get('numHeads',0),)

if testSwitch.virtualRun:
   # Fix head count for VE so that VBAR passes.
   # Not all Luxor programs have a 2-hd part number,
   # so this is a quick way to run properly
   for key in familyInfo.keys():
      familyInfo[key]['HD_COUNT'] = (2,)

if myDefaultPN not in familyInfo: # cannot find 10-digit part number
   myDefaultPN = myDefaultPN[0:6] # then default to 6-digit part number
   if myDefaultPN not in familyInfo: # cannot find 6-digit part number
      myDefaultPN = myDefaultPN[0:3] # then default to 3-digit part number, if still cannot find, raise script error

depopMask = []

## 500G 2H(K0)
if HDASerialNumber[1:6] == 'ESK02':
   depopMask = [0]
   familyInfo['1RK172']['HD_COUNT'] = (1,)
   familyInfo['1RK17C']['HD_COUNT'] = (1,)
   familyInfo['1RK17D']['HD_COUNT'] = (1,)

## 500G 2H(K1)
if HDASerialNumber[1:6] == 'ESK01':
   depopMask = [1]
   familyInfo['1RK172']['HD_COUNT'] = (1,)
   familyInfo['1RK17C']['HD_COUNT'] = (1,)
   familyInfo['1RK17D']['HD_COUNT'] = (1,)

## 1500G 3H(K0)
if HDASerialNumber[1:6] == 'DZK0E':
   depopMask = [0]
   familyInfo['1R8174']['HD_COUNT'] = (3,)
   familyInfo['1R817G']['HD_COUNT'] = (3,)

## 1500G 3H(K1)
if HDASerialNumber[1:6] == 'DZK0D':
   depopMask = [1]
   familyInfo['1R8174']['HD_COUNT'] = (3,)
   familyInfo['1R817G']['HD_COUNT'] = (3,)

## 1500G 3H(K2)
if HDASerialNumber[1:6] == 'DZK0B':
   depopMask = [2]
   familyInfo['1R8174']['HD_COUNT'] = (3,)
   familyInfo['1R817G']['HD_COUNT'] = (3,)

## 1500G 3H(K3)
if HDASerialNumber[1:6] == 'DZK07':
   depopMask = [3]
   familyInfo['1R8174']['HD_COUNT'] = (3,)
   familyInfo['1R817G']['HD_COUNT'] = (3,)

## 1000G 2H(K01)
if HDASerialNumber[1:6] == 'DZK0C':
   depopMask = [0,1]
   familyInfo['1R8174']['HD_COUNT'] = (2,)
   familyInfo['1R817G']['HD_COUNT'] = (2,)
   familyInfo['1R8172']['HD_COUNT'] = (2,)
   familyInfo['1R817C']['HD_COUNT'] = (2,)
   familyInfo['1R817D']['HD_COUNT'] = (2,)

## 1000G 2H(K02)
if HDASerialNumber[1:6] == 'DZK0A':
   depopMask = [0,2]
   familyInfo['1R8174']['HD_COUNT'] = (2,)
   familyInfo['1R817G']['HD_COUNT'] = (2,)
   familyInfo['1R8172']['HD_COUNT'] = (2,)
   familyInfo['1R817C']['HD_COUNT'] = (2,)
   familyInfo['1R817D']['HD_COUNT'] = (2,)

## 1000G 2H(K03)
if HDASerialNumber[1:6] == 'DZK06':
   depopMask = [0,3]
   familyInfo['1R8174']['HD_COUNT'] = (2,)
   familyInfo['1R817G']['HD_COUNT'] = (2,)
   familyInfo['1R8172']['HD_COUNT'] = (2,)
   familyInfo['1R817C']['HD_COUNT'] = (2,)
   familyInfo['1R817D']['HD_COUNT'] = (2,)

## 1000G 2H(K12)
if HDASerialNumber[1:6] == 'DZK09':
   depopMask = [1,2]
   familyInfo['1R8174']['HD_COUNT'] = (2,)
   familyInfo['1R817G']['HD_COUNT'] = (2,)
   familyInfo['1R8172']['HD_COUNT'] = (2,)
   familyInfo['1R817C']['HD_COUNT'] = (2,)
   familyInfo['1R817D']['HD_COUNT'] = (2,)

## 1000G 2H(K13)
if HDASerialNumber[1:6] == 'DZK05':
   depopMask = [1,3]
   familyInfo['1R8174']['HD_COUNT'] = (2,)
   familyInfo['1R817G']['HD_COUNT'] = (2,)
   familyInfo['1R8172']['HD_COUNT'] = (2,)
   familyInfo['1R817C']['HD_COUNT'] = (2,)
   familyInfo['1R817D']['HD_COUNT'] = (2,)

## 1000G 2H(K23)
if HDASerialNumber[1:6] == 'DZK03':
   depopMask = [2,3]
   familyInfo['1R8174']['HD_COUNT'] = (2,)
   familyInfo['1R817G']['HD_COUNT'] = (2,)
   familyInfo['1R8172']['HD_COUNT'] = (2,)
   familyInfo['1R817C']['HD_COUNT'] = (2,)
   familyInfo['1R817D']['HD_COUNT'] = (2,)

# 500G 1H(K123)
if HDASerialNumber[1:6] == 'DZK01':
   depopMask = [1,2,3]
   familyInfo['1R8174']['HD_COUNT'] = (1,)
   familyInfo['1R817G']['HD_COUNT'] = (1,)
   familyInfo['1R8172']['HD_COUNT'] = (1,)
   familyInfo['1R817C']['HD_COUNT'] = (1,)
   familyInfo['1R817D']['HD_COUNT'] = (1,)
   familyInfo['1R8171']['HD_COUNT'] = (1,)
   familyInfo['1R817A']['HD_COUNT'] = (1,)

# 500G 1H(K023)
if HDASerialNumber[1:6] == 'DZK02':
   depopMask = [0,2,3]
   familyInfo['1R8174']['HD_COUNT'] = (1,)
   familyInfo['1R817G']['HD_COUNT'] = (1,)
   familyInfo['1R8172']['HD_COUNT'] = (1,)
   familyInfo['1R817C']['HD_COUNT'] = (1,)
   familyInfo['1R817D']['HD_COUNT'] = (1,)
   familyInfo['1R8171']['HD_COUNT'] = (1,)
   familyInfo['1R817A']['HD_COUNT'] = (1,)

# 500G 1H(K013)
if HDASerialNumber[1:6] == 'DZK04':
   depopMask = [0,1,3]
   familyInfo['1R8174']['HD_COUNT'] = (1,)
   familyInfo['1R817G']['HD_COUNT'] = (1,)
   familyInfo['1R8172']['HD_COUNT'] = (1,)
   familyInfo['1R817C']['HD_COUNT'] = (1,)
   familyInfo['1R817D']['HD_COUNT'] = (1,)
   familyInfo['1R8171']['HD_COUNT'] = (1,)
   familyInfo['1R817A']['HD_COUNT'] = (1,)

# 500G 1H(K012)
if HDASerialNumber[1:6] == 'DZK08':
   depopMask = [0,1,2]
   familyInfo['1R8174']['HD_COUNT'] = (1,)
   familyInfo['1R817G']['HD_COUNT'] = (1,)
   familyInfo['1R8172']['HD_COUNT'] = (1,)
   familyInfo['1R817C']['HD_COUNT'] = (1,)
   familyInfo['1R817D']['HD_COUNT'] = (1,)
   familyInfo['1R8171']['HD_COUNT'] = (1,)
   familyInfo['1R817A']['HD_COUNT'] = (1,)


numHeads = familyInfo[myDefaultPN]['HD_COUNT'][0]
defPFMID = familyInfo[myDefaultPN]['PFM_ID'][0]

if myDefaultPN[0:3] in ['1U7', '1U8', '1U9', '1UA', '1UB', '1UC', '1U4', '1U5', '1U6', '1RG', '1RH', '1RJ']:
   testSwitch.FE_0000000_305538_HYBRID_DRIVE = 1

# Simple hack for using common PCO for 1D and 2D products, i.e. Rosewood7
if numHeads > 2:
   testSwitch.IS_2D_DRV = 1

if numHeads == 1 and testSwitch.ROSEWOOD7: # 1-H hack for RW7
   testSwitch.FE_0114584_007955_DISABLE_WRITE_WWN_IN_SETFAMILYINFO = 1

# --- This is the default capacity per head ---
VbarCapacityGBPerHead = 500
WTFCapacityGBPerHead  = 375
# RW7 Common Part Number for 1TB Support
if testSwitch.TRUNK_BRINGUP:
    VbarCapacityGBPerHead = 341  # trunk code bringup using ch08(gen1C) configure
elif testSwitch.CHENGAI:
   VbarCapacityGBPerHead = 375
elif HDASerialNumber[1:3] in ['67']: # hack for ChengaiMule
   VbarCapacityGBPerHead = 375
   WTFCapacityGBPerHead  = 250

Native_Capacity = ['%dG' % (VbarCapacityGBPerHead*numHeads)]

Analog_FS_Freq_3xT = 667
Analog_FS_Freq_2T = 1000
Analog_FS_Freq = Analog_FS_Freq_3xT

TA_FS_Freq = Analog_FS_Freq_2T

famUpdatePrm_178 = {
   'NO_ETF'                : (),
   'test_num'              : 178,
   'prm_name'              : 'famUpdatePrm_178',
   'timeout'               : 1200,
   'spc_id'                : 1,
   }

partNumInterfaceMatrix = {
   '1XX'                      :'AS',
   '2XX'                      :'SAS',
   }

WWN_INF_TYPE = {                    # Interface value from DriveAttribute INTERFACE
   #'WW_FC_ID'  :('FC', 'FCV'),
   'WW_SAS_ID'                : ('SS', 'SAS'),
   'WW_SATA_ID'               : ('AS', 'SATA', 'NS', 'CS'), # Sata, new name for SATA, Sata Nearline, Sata consumer electronics
   }

#These two prms need to be called in FNC2 AFTER flawscan
prm_149_Wwn2Etf = {
   'test_num'                 : 149,
   'prm_name'                 : 'prm_149_Wwn2Etf',
   'timeout'                  : 300,
   'CWORD2'                   : (0x0003,),
   'ETF_LOG_DATE'             : (0xFFFF,0xFFFF),  #Set by Process.py
}
prm_130_readDIF = {
   'test_num'                 : 130,
   'prm_name'                 : 'prm_130_readDIF',
   'timeout'                  : 300,
   'CWORD2'                   : (0x8002,),  #Read DIF in Binary to CM
}


Servo_Sn_Prefix_Matrix = {
    '94' : {'PhysHds':4, 'PFM_ID':(0x1,)},   # Rosewood7 2D
    'DZ' : {'PhysHds':4, 'PFM_ID':(0x1,)},   # Rosewood7LC 2D
    'F7' : {'PhysHds':4, 'PFM_ID':(0x1,)},   # Rosewood7LC 2D IDCS
    'CC' : {'PhysHds':4, 'PFM_ID':(0x1,)},   # Rosewood7 2D larger OD Flange MBA
    '93' : {'PhysHds':2, 'PFM_ID':(0x3,)},   # Rosewood7 1D
    'DE' : {'PhysHds':2, 'PFM_ID':(0x3,)},   # Rosewood7LC 1D
    'ES' : {'PhysHds':2, 'PFM_ID':(0x3,)},   # Rosewood7LC 1D R11
    'F6' : {'PhysHds':2, 'PFM_ID':(0x3,)},   # Rosewood7LC 1D IDCS
    'CB' : {'PhysHds':2, 'PFM_ID':(0x3,)},   # Rosewood7 1D larger OD Flange MBA
    'C0' : {'PhysHds':4, 'PFM_ID':(0x1,)},   # Rosewood7 2D 3H (dummy H0)
    'C7' : {'PhysHds':4, 'PFM_ID':(0x1,)},   # Rosewood7 2D 3H (dummy H1)
    'C8' : {'PhysHds':4, 'PFM_ID':(0x1,)},   # Rosewood7 2D 3H (dummy H2)
    'BZ' : {'PhysHds':4, 'PFM_ID':(0x1,)},   # Rosewood7 2D 3H (dummy H3)
    'F4' : {'PhysHds':4, 'PFM_ID':(0x1,)},   # Rosewood7 2D 3H (dummy H3)
    'F5' : {'PhysHds':4, 'PFM_ID':(0x1,)},   # Rosewood7 2D 3H (dummy H3)
    'F8' : {'PhysHds':4, 'PFM_ID':(0x1,)},   # Rosewood7 2D 3H (dummy H3) IDCS
    'F9' : {'PhysHds':4, 'PFM_ID':(0x1,)},   # Rosewood7 2D 3H (dummy H3) IDCS
    '67' : {'PhysHds':2, 'PFM_ID':(0x1,)},   # Chengai
    'A7' : {'PhysHds':1, 'PFM_ID':(0x1,)},   # HMAR related
}

if testSwitch.virtualRun:
    Servo_Sn_Prefix_Matrix['A7']['PhysHds'] = 2


# DCM attribute overrides
# Define these as PN based matches- all 9 digits must match PN
# EG. DRV_MODEL_NUM_Override = {'9FZ162-999':'ST3500410AS'}
DRV_MODEL_NUM_Override = {}

CUST_MODEL_NUM_Override = {}

driveModelJustification = {}

if testSwitch.FE_0127527_426568_STEPLBA_SET_BY_TEST_PARAMETER_IN_DOS_VERIFY:
   stepLBAinCVerifyDOS = 600000

USER_LBA_COUNT_Override = { }

#Enable the disabling of a cell to reduce the probability of insertion disturbance during
#  the tests in the list below.
# **Warning- use sparingly and only for shorter TT tests as this feature can cause a decrease in gemini utilization
Gantry_Ins_Prot_Tests = [35, 191]

#Disable and Enable cell during start and end of test states defined
#Feature is enabled using testSwitch.GANTRY_INSERTION_PROTECTION
Gantry_Ins_Prot_StateNames = ['SP_WR_TRUPUT', 'SP_RD_TRUPUT']

##################### Oracle #####################################

dbl_RUNTIME = {150 : ['P150_GAIN_SUMMARY']}

# Caution: UMP_ZONE value will be on the fly update with according to the number of logical head.
if testSwitch.ADAPTIVE_GUARD_BAND:
   UMP_ZONE_BY_HEAD = {
      1: {
            60  : [3, 4, 59],
            120 : [5, 6, 7, 119],
            150 : [4, 5, 6, 7, 149],
            180 : [5, 6, 7, 8, 9, 10, 179],
         },
      2: {
            60  : [3, 4, 59],
            120 : [5, 6, 7, 119],
            150 : [4, 5, 6, 7, 149],
            180 : [5, 6, 7, 8, 9, 10, 179],
         },
      3: {
            60  : [3, 4, 59],
            120 : [5, 6, 7, 119],
            150 : [4, 5, 6, 149],
            180 : [5, 6, 7, 8, 9, 10, 179],
         },
      4: {
            60  : [3, 4, 59],
            120 : [5, 6, 7, 119],
            150 : [4, 5, 149],
            180 : [5, 6, 7, 8, 9, 10, 179],
         },
   }

else:
   UMP_ZONE_BY_HEAD = {
      1: {
            60  : [2, 3, 59],
            120 : [4, 5, 6, 119],
            150 : [3, 4, 5, 6, 149],
            180 : [4, 5, 6, 7, 8, 9, 179],
         },
      2: {
            60  : [2, 3, 59],
            120 : [4, 5, 6, 119],
            150 : [3, 4, 5, 6, 149],
            180 : [4, 5, 6, 7, 8, 9, 179],
         },
      3: {
            60  : [2, 3, 59],
            120 : [4, 5, 6, 119],
            150 : [3, 4, 5, 6, 149],
            180 : [4, 5, 6, 7, 8, 9, 179],
         },
      4: {
            60  : [2, 3, 59],
            120 : [4, 5, 6, 119],
            150 : [3, 4, 5, 6, 149],
            180 : [4, 5, 6, 7, 8, 9, 179],
         },
   }

if testSwitch.FE_0385234_356688_P_MULTI_ID_UMP:
   UMP_ZONE_BY_HEAD.update({
      1: {
            60  : [3, 4, 59],
            120 : [5, 6, 7, 119],
            150 : range(121, 150, 1), #[4, 5, 6, 7, 149],
            180 : [5, 6, 7, 8, 9, 10, 179],
         },
      2: {
            60  : [3, 4, 59],
            120 : [5, 6, 7, 119],
            150 : range(121, 150, 1), #[4, 5, 6, 7, 149],
            180 : [5, 6, 7, 8, 9, 10, 179],
         },
      3: {
            60  : [3, 4, 59],
            120 : [5, 6, 7, 119],
            150 : range(122, 150, 1), #[4, 5, 6, 149],
            180 : [5, 6, 7, 8, 9, 10, 179],
         },
      4: {
            60  : [3, 4, 59],
            120 : [5, 6, 7, 119],
            150 : range(123, 150, 1), #[4, 5, 149],
            180 : [5, 6, 7, 8, 9, 10, 179],
         },
   })
   
if testSwitch.FE_348085_P_NEW_UMP_MC_ZONE_LAYOUT:
   UMP_ZONE_BY_HEAD.update({
      1: {
               60  : [1, 2, 59],
               120 : [1, 2, 3, 119],
               150 : [1, 2, 3, 4, 149],
               180 : [1, 2, 3, 4, 5, 6, 179],
         },
      2: {
               60  : [1, 2, 59],
               120 : [1, 2, 3, 119],
               150 : [1, 2, 3, 4, 149],
               180 : [1, 2, 3, 4, 5, 6, 179],
         },
      3: {
               60  : [1, 2, 59],
               120 : [1, 2, 3, 119],
               150 : [1, 2, 3, 149],
               180 : [1, 2, 3, 4, 5, 6, 179],
         },
      4: {
               60  : [1, 2, 59],
               120 : [1, 2, 3, 119],
               150 : [1, 2, 149],
               180 : [1, 2, 3, 4, 5, 6, 179],
         },
   })


UMP_ZONE = UMP_ZONE_BY_HEAD[numHeads].copy()

# Need to sync up with RAP
if testSwitch.FE_0257373_348085_ZONED_SERVO_CAPACITY_CALCULATION:
   #DEFAULT_ZONES_WITH_ZIPPER = [16, 30, 45]   # rap 1A01
   #DEFAULT_ZONES_WITH_ZIPPER = [16, 30, 44]   # rap 1A02
   DEFAULT_ZONES_WITH_ZIPPER = [16, 30, 44, 45]   # rap 1A01 + 1A02

if testSwitch.ADAPTIVE_GUARD_BAND:
   MC_ZONE = {
      'ATTRIBUTE':'numZones',
      'DEFAULT': 150,
      150 : range(1, min(UMP_ZONE[150]), 1),
      180 : range(1, min(UMP_ZONE[180]), 1),
   }
else:
   MC_ZONE = {
      'ATTRIBUTE':'numZones',
      'DEFAULT': 150,
      150 : range(0, min(UMP_ZONE[150]), 1),
      180 : range(0, min(UMP_ZONE[180]), 1),
   }

if testSwitch.FE_0385234_356688_P_MULTI_ID_UMP:
   if testSwitch.ADAPTIVE_GUARD_BAND:
      MC_ZONE.update({
         'ATTRIBUTE':'numZones',
         'DEFAULT': 150,
         150 : range(1,4,1),      # [1, 2, 3]
         180 : range(1, min(UMP_ZONE[180]), 1),
      })
   else:
      MC_ZONE.update({
         'ATTRIBUTE':'numZones',
         'DEFAULT': 150,
         150 : range(0,3,1),      # [0, 1, 2]
         180 : range(0, min(UMP_ZONE[180]), 1),
      })
   
if testSwitch.FE_348085_P_NEW_UMP_MC_ZONE_LAYOUT:
   MC_ZONE.update({
      'ATTRIBUTE':'numZones',
      'DEFAULT': 150,
      150 : [], 
      180 : [], 
   })
   
numMC = len(MC_ZONE)
numUMP = len(UMP_ZONE)

BaseTestZone = {               # eg. for BPINOMINAL, PRE_OPTI, 2D_VBAR
   'ATTRIBUTE':'numZones',
   'DEFAULT': 150,
   150 :[0,35,75,115,149],
}

baseVbarTestZones  = {
   'ATTRIBUTE': 'FE_0385234_356688_P_MULTI_ID_UMP',
   'DEFAULT'  : 0,
   0 : {150: [8, 13, 18, 23, 28, 33, 38, 43, 48, 53, 58, 63, 68, 73, 78, 83, 88, 93, 98, 103, 108, 113, 118, 123, 128, 133, 138, 143, 148, 149],},
   1 : {150: [8, 13, 18, 23, 28, 33, 38, 43, 48, 53, 58, 63, 68, 73, 78, 83, 88, 93, 98, 103, 108, 113, 118],},
}

baseSMRZoneBeforeUMP = {
   'ATTRIBUTE':'numZones',
   'DEFAULT': 150,
   150 : {'EQUATION': "sorted(list(set(range(TP.MC_ZONE[-1]+1,(TP.baseVbarTestZones[150][0]),1) + TP.baseVbarTestZones[150] + range(TP.baseVbarTestZones[150][-1]+1,(TP.UMP_ZONE[150][0]),1) )))",},
}

baseVbarTestZones_10StepOD5StepID  = {
   'ATTRIBUTE': 'FE_0385234_356688_P_MULTI_ID_UMP',
   'DEFAULT'  : 0,
   0 : {150: [8, 18, 28, 38, 48, 58, 68, 78, 88, 98, 108, 118, 128, 138, 143, 148, 149],},
   1 : {150: [8, 18, 28, 38, 48, 58, 68, 78, 88, 98, 108, 118],},
}

baseVbarTestZones_10StepNoUMP  = {
   'ATTRIBUTE': 'FE_0385234_356688_P_MULTI_ID_UMP',
   'DEFAULT'  : 0,
   0 : {150: [8, 18, 28, 38, 48, 58, 68, 78, 88, 98, 108, 118, 128, 138, 148],},
   1 : {150: [8, 18, 28, 38, 48, 58, 68, 78, 88, 98, 108, 118],},
}

baseVbarTestZones_10Step  = {
   'ATTRIBUTE': 'FE_0385234_356688_P_MULTI_ID_UMP',
   'DEFAULT'  : 0,
   0 : {150: [8, 18, 28, 38, 48, 58, 68, 78, 88, 98, 108, 118, 128, 138, 148, 149],},
   1 : {150: [8, 18, 28, 38, 48, 58, 68, 78, 88, 98, 108, 118],},
}

baseVbarTestZones_20Step  = {
   'ATTRIBUTE': 'FE_0385234_356688_P_MULTI_ID_UMP',
   'DEFAULT'  : 0,
   0 : {150: [8, 28, 48, 68, 88, 108, 128, 148, 149],},
   1 : {150: [8, 28, 48, 68, 88, 108, 118],},
}

_2D_VBAR_ZN_INDEX = {   #Index for the 2D test zone from the list baseVbarTestZones
   'ATTRIBUTE': 'FE_0385234_356688_P_MULTI_ID_UMP',
   'DEFAULT'  : 0,
   0 : {150: [2, 6, 14, 22, 28],},
   1 : {150: [2, 6, 14, 22],},
}

_2DVBAR_ZN = {           # eg. for T250 in VBAR_ZN [0, 18, 38, 78, 118, 148]
   'ATTRIBUTE': 'FE_0385234_356688_P_MULTI_ID_UMP',
   'DEFAULT'  : 0,
   0 : {'EQUATION': "[0] + [TP.baseVbarTestZones[self.dut.numZones][index] for index in TP._2D_VBAR_ZN_INDEX [self.dut.numZones]]",},
   1 : {'EQUATION': "[0] + [TP.baseVbarTestZones[self.dut.numZones][index] for index in TP._2D_VBAR_ZN_INDEX [self.dut.numZones]] + [TP.UMP_ZONE[self.dut.numZones][0]-1]",},
}

BERInVBAR_ZN = {           # eg. for T250 in VBAR_ZN [0, 38, 78, 118, 149]
   'ATTRIBUTE': 'FE_0385234_356688_P_MULTI_ID_UMP',
   'DEFAULT'  : 0,
   0 : {'EQUATION': "[0] + [ TP.SMRZoneAfterUMP[index] for index in [len(TP.SMRZoneAfterUMP)/4-1, len(TP.SMRZoneAfterUMP)/2, -int(len(TP.SMRZoneAfterUMP)/4.0)] ] + [TP.UMP_ZONE[self.dut.numZones][-1]]",},
   1 : [0,38,78,118,149],
}

BPIMeasureZone = {        # eg. for BPI measure zone, 0+MC+UMP+[(8 to 148)/5]+SPARE, ZONE MUST in ASCENDING order
   'ATTRIBUTE': 'FE_0385234_356688_P_MULTI_ID_UMP',
   'DEFAULT'  : 0,
   0 : {'EQUATION': "sorted(list(set([0] + TP.MC_ZONE + list(set(TP.UMP_ZONE[self.dut.numZones] + range(TP.UMP_ZONE[self.dut.numZones][-2]+1,(TP.baseVbarTestZones[self.dut.numZones][0]),1) + TP.baseVbarTestZones[self.dut.numZones])))) )",},
   1 : {'EQUATION': "sorted(list(set([0] + TP.MC_ZONE + list(set(TP.UMP_ZONE[self.dut.numZones] + range(TP.MC_ZONE[-1]+1,(TP.baseVbarTestZones[self.dut.numZones][0]),1) + TP.baseVbarTestZones[self.dut.numZones] + range(TP.baseVbarTestZones[self.dut.numZones][-1]+1,(TP.UMP_ZONE[self.dut.numZones][0]),1))))) )",},   
}

SMRZoneAfterUMP = {
   "EQUATION" : "sorted(list(set(TP.BPIMeasureZone)-set([0]+ TP.MC_ZONE + TP.UMP_ZONE[self.dut.numZones])))"
}

BPIMeasureZone_TTR = {        # eg. for BPI measure zone, 0+MC+UMP+[(8 to 148)/10]+SPARE, ZONE MUST in ASCENDING order
   'ATTRIBUTE': 'FE_0385234_356688_P_MULTI_ID_UMP',
   'DEFAULT'  : 0,
   0 : {'EQUATION': "sorted(list(set([0] + TP.MC_ZONE + list(set(TP.UMP_ZONE[self.dut.numZones] + range(TP.UMP_ZONE[self.dut.numZones][-2]+1,(TP.baseVbarTestZones_10Step[self.dut.numZones][0]),1) + TP.baseVbarTestZones_10Step[self.dut.numZones])))) )",},
   1 : {'EQUATION': "sorted(list(set([0] + TP.MC_ZONE + list(set(range(TP.MC_ZONE[-1]+1,(TP.baseVbarTestZones_10Step[150][0]),1) + TP.baseVbarTestZones_10Step[150] + range(TP.baseVbarTestZones_10Step[150][-1]+1,(TP.UMP_ZONE[150][0]),1) + TP.UMP_ZONE[150])))) )",},
}

BPIMeasureZone_TTR2 = {        # eg. for BPI measure zone, 0+MC+UMP+[(8 to 148)/10]+SPARE, ZONE MUST in ASCENDING order
   'ATTRIBUTE': 'FE_0385234_356688_P_MULTI_ID_UMP',
   'DEFAULT'  : 0,
   0 : {'EQUATION': "sorted(list(set([0] + TP.MC_ZONE + list(set(TP.UMP_ZONE[self.dut.numZones] + range(TP.UMP_ZONE[self.dut.numZones][-2]+1,(TP.baseVbarTestZones_20Step[self.dut.numZones][0]),1) + TP.baseVbarTestZones_20Step[self.dut.numZones])))) )",},
   1 : {'EQUATION': "sorted(list(set([0] + TP.MC_ZONE + list(set(range(TP.MC_ZONE[-1]+1,(TP.baseVbarTestZones_20Step[150][0]),1) + TP.baseVbarTestZones_20Step[150] + range(TP.baseVbarTestZones_20Step[150][-1]+1,(TP.UMP_ZONE[150][0]),1) + TP.UMP_ZONE[150])))) )",},
}

BPIMeasureZone_NoUMP = {        # eg. for BPI measure zone, 0+MC+UMP+[(8 to 148)/10]+SPARE, ZONE MUST in ASCENDING order
   'ATTRIBUTE': 'FE_0385234_356688_P_MULTI_ID_UMP',
   'DEFAULT'  : 0,
   0 : {'EQUATION': "sorted(list(set([0] + TP.MC_ZONE + list(set(range(TP.UMP_ZONE[self.dut.numZones][-2]+1,(TP.baseVbarTestZones_10StepNoUMP[self.dut.numZones][0]),1) + TP.baseVbarTestZones_10StepNoUMP[self.dut.numZones])))) )",},
   1 : {'EQUATION': "sorted(list(set([0] + TP.MC_ZONE + list(set(range(TP.MC_ZONE[-1]+1,(TP.baseVbarTestZones_10StepNoUMP[150][0]),1) + TP.baseVbarTestZones_10StepNoUMP[150] + range(TP.baseVbarTestZones_10StepNoUMP[150][-1]+1,(TP.UMP_ZONE[150][0]),1))))) )",},
}

OTCMeasureZone = {        # eg. for BPI measure zone, 0+MC+UMP+[(8 to 148)/10]+SPARE, ZONE MUST in ASCENDING order
   'ATTRIBUTE': 'FE_0385234_356688_P_MULTI_ID_UMP',
   'DEFAULT'  : 0,
   0 : {'EQUATION': "sorted(list(set([0] + TP.MC_ZONE + list(set(TP.UMP_ZONE[self.dut.numZones] + range(TP.UMP_ZONE[self.dut.numZones][-2]+1,(TP.baseVbarTestZones_10StepOD5StepID[self.dut.numZones][0]),1) + TP.baseVbarTestZones_10StepOD5StepID[self.dut.numZones])))) )",},
   1 : {'EQUATION': "sorted(list(set([0] + TP.MC_ZONE + list(set(range(TP.MC_ZONE[-1]+1,(TP.baseVbarTestZones_10StepOD5StepID[150][0]),1) + TP.baseVbarTestZones_10StepOD5StepID[150] + range(TP.baseVbarTestZones_10StepOD5StepID[150][-1]+1,(TP.UMP_ZONE[150][0]),1) + TP.UMP_ZONE[150])))) )",},
}

# Override the tracks per band # Default is 50
tracksPerBand = 50
if testSwitch.THIRTY_TRACKS_PER_BAND:
   tracksPerBand = 30

###### Parametric Load #####################################
# Details on the test switch and parameters related to parametric load can be found on the wiki:
#  http://wiki.firmware.seagate.com/wiki/index.php/DBLog#DBLog_Documentation

#No Load usage: List of tuples where index 0 is the table name and index 1 is the load status into the inLineDbLog allocation
# if index 1 is set to 0 then this table will not be loaded for script data usage or upload to oracle
#                     [('TABLE_NAME,                  ParametricUploadStatus')]
parametric_no_load = [
   ('P000_BASELINE_PES', 0),
   ('P000_DEBUG_DATA', 0),
   ('P000_DELTA_PES', 0),
   ('P000_DRIVE_VAR_TABLE', 0),
   ('P000_PES', 0),
   ('P000_REPORTED_ERROR_CODE', 0),
   ('P000_SENSE_DATA', 0),
   ('P000_SERVO_UNSAFE_FLAG', 0),
   ('P000_XFR_FUNCTION', 0),
   ('P001_TIME_TO_READY', 0),
   ('P030_ESP_SEEK', 0),
   ('P035_CFH_DYNAMIC_THRSHLD', 0),
   ('P035_DETAIL', 0),
   ('P047_COSINE_POINTS', 0),
   ('P047_SINE_POINTS', 0),
   ('P047_VCAT_3_COEF_AC_COS', 0),
   ('P047_VCAT_3_COEF_AC_SIN', 0),
   ('P047_VCAT_5_COEF_AC_COS', 0),
   ('P047_VCAT_5_COEF_AC_SIN', 0),
   ('P050_BASELINE_MSRMNT2', 0),
   ('P050_ENCROACH_MSRMNT2', 0),
   ('P051_BASELINE_MSRMNT2', 0),
   ('P051_ERASURE_MSRMNT2', 0),
   ('P136_BIAS_VALUE', 0),
   ('P140_FLAW_COUNT', 0),
   ('P151_ATTENUATION_VGA', 0),
   ('P151_CHANNEL_OPT', 0),
   ('P151_FW_ACTION_FLAGS', 0),
   ('P151_SERVO_OFFSETS', 0),
   ('P152_BODE_GAIN_ONLY', 0),
   ('P172_CAP_TABLE', 0),
   ('P172_RAP_TABLE', 0),
   ('P172_SAP_TABLE', 0),
   ('P172_ZONE_TBL',0),
   ('P172_RESVD_ZONE_TBL',0),
   ('P172_ZONE_DATA',0),
   ('P172_RESVD_ZONE_DATA',0),
   ('P172_WRITE_POWERS', 0),
   ('P175_SERVO_WRITE_DELAY', 0),
   ('P176_SERVO_WRITE_DELAY', 0),
   ('P185_V3BAR_ID_THRESHOLDS', 0),
   ('P185_V3BAR_OD_THRESHOLDS', 0),
   ('P186_BIAS_CAL', 0),
   ('P189_HEAD_SKEW_DETAILS', 0),
   ('P210_CAPACITY_HD2', 0),
   ('P211_BPI_CAP_AVG', 0),
   ('P211_BPI_CAP_SINGLE', 0),
   ('P211_BPI_CAP_SINGLE', 0),
   ('P211_BPI_INIT', 0),
   ('P211_BPI_MEASUREMENT', 0),
   ('P211_BPI_MEASUREMENT', 0),
   ('P211_HEADER_INFO', 0),
   ('P211_HEADER_INFO', 0),
   ('P211_OTC_MEASUREMENT', 0),
   ('P211_TPI_CAP_AVG', 0),
   ('P211_TPI_CAP_SINGLE', 0),
   ('P211_TPI_CAP_SINGLE', 0),
   ('P211_TPI_INIT', 0),
   ('P211_TPI_MEASUREMENT', 0),
   ('P211_VBAR_DEFAULT_CHAN', 0),
   ('P231_HEADER_INFO', 0),
   ('P234_EAW_VGAS', 0),
   ('P234_VGAS_RESULTS', 0),
   ('P251_BEST_FITNESS_POINT', 0),
   ('P251_BEST_FITNESS_POINT2', 0),
   ('P251_ERR_RATE_BUCKET_EXTD', 0),
   ('P251_FITNESS_POINT_EXTD', 0),
   ('P251_STATUS', 0),
   ('P_MINOR_FAIL_CODE', 0),
   ('P_NPT_OPTI_AGERE', 0),
   ('P_TRACK', 0),
   ('P172_ZONED_SERVO', 0),
   ('P172_RSVD_ZONED_SERVO', 0),
   ('P172_ZONED_SERVO_RED', 0),
   ('P172_RSVD_ZONED_SERVO_RED', 0),
   ('P172_HEAD_TPI_CONFIG_TBL', 0),
   ('P210_VBAR_FORMATS', 0),
   ('P_VBAR_PICKER_FMT_ADJUST', 0),
   ('P130_SYS_RZDT', 0),
   ('P061_OVERWRITE_PER_SECTOR', 0),
   ('P061_OW_MEASUREMENT', 0)
   ]

priority_parametric_load_list = []
priority_parametric_reload_list = []
productionLoadOnly = []

if testSwitch.VBAR_HMS_V2:
   priority_parametric_load_list.append('P_VBAR_HMS_ADJUST')

if testSwitch.VBAR_HMS_V4:
   priority_parametric_load_list.append('P_SETTLING SUMMARY')

# Add Tables to priority load list based on RSS requirements for analysis
priority_parametric_load_list.extend (['TEST_TIME_BY_STATE',
                                         'P_WRT_PWR_TRIPLETS',
                                         'P_WRT_PWR_PICKER',
                                         'P_VBAR_FORMAT_SUMMARY',
                                         'P_VBAR_ADC_SUMMARY',
                                         'P_VBAR_MAX_FORMAT_SUMMARY',
                                         'P_FORMAT_ZONE_ERROR_RATE',
                                         'P255_PRECOMP_VGA_LSI_DATA',
                                         'P255_PREAMP_CHNL_HD_PARAM',
                                         'P255_NPTARG_MISC_LSI_DATA',
                                         'P255_NPML_TAP2_3_LSI_DATA',
                                         'P255_NPML_TAP0_1_LSI_DATA',
                                         'P255_NPML_BIAS_LSI_TAPS',
                                         'P255_FIR_LSI_DATA',
                                         'P251_SUBPROC_SUM_AGERE',
                                         'P251_DIBIT_OPTI_VALUES',
                                         'P251_ATTENUATION_VGA2',
                                         'P250_ERROR_RATE_BY_ZONE',
                                         'P238_MICROJOG_CAL',
                                         'P211_VBAR_CAPS_WPPS',
                                         'P177_PREAMP_CAL_EXTD',
                                         'P176_HD_GAP_DELTA',
                                         'P172_AFH_WORKING_ADAPTS',
                                         'P134_TA_SUM_HD2',
                                         'P126_SRVO_FLAW_HD',
                                         'P117_SCRATCH_FILL_BY_HEAD',
                                         'P109_UNSAFE_SUMMARY',
                                         'P109_SUM_HD_ZONE',
                                         'P109_LUL_ERROR_COUNT',
                                         'P107_VERIFIED_FLAW_LENGTH',
                                         'P107_VERIFIED_FLAWS',
                                         'P107_TOTAL_VERIFIED_FLAWS',
                                         'P234_EAW_ERROR_RATE2',
                                         'P_DELTA_MRE',
                                         'P_AGB_STARTTRACK',
                                         'P_TEMP_WEAK_WRITE_BER',
                                         'P_TEMP_APO_BER',
                                         'P_AVERAGE_ERR_RATE'])

if testSwitch.SMR:
   if 'P_VBAR_FORMAT_SUMMARY' not in priority_parametric_load_list:
      priority_parametric_load_list.append('P_VBAR_FORMAT_SUMMARY')
   if 'P_VBAR_SMR_MEASUREMENT' not in priority_parametric_load_list:
      priority_parametric_load_list.append('P_VBAR_SMR_MEASUREMENT')


#Use to automatically calculate spcId's by Operation
spcId_operBase = {
   'OPER' : {
      'PRE2'   : 1000,
      'CAL2'   : 2000,
      'FNC2'   : 3000,
      },
   'StateName' : {
      'GMR_RES_0'  : 10,
      'GMR_RES_1'  : 20,
      'GMR_RES_2'  : 30,
      'GMR_RES_3'  : 40,
      'GMR_RES_4'  : 50,
      'GMR_RES_5'  : 60,
      'GMR_RES_6'  : 70,
      'GMR_RES_7'  : 80,
      'GMR_RES_8'  : 90,
      'GMR_RES_9'  : 100,
      'GMR_RES_10' : 110,
      }
   }

if testSwitch.FE_SGP_PREAMP_GAIN_TUNING:
   VGAR_LowerLimit = 40
   VGAR_UpperLimit = 220
   getPreampGain  = {
      'test_num'        : 11,
      'prm_name'        : "Get PreampGain",
      'CWORD1'          : 1,
      'timeout'         : 100,
      'START_ADDRESS'   : (0x01,0x8CFE),
      'END_ADDRESS'     : (0x01,0x8CFE),
      'ACCESS_TYPE'     : 2,
      'WR_DATA'         : 0,
      }

   setPreampGain = {
      'test_num'        : 11,
      'prm_name'        : "Set PreampGain",
      'CWORD1'          : 2,
      'timeout'         : 100,
      'START_ADDRESS'   : (0x1,0x8cfe),
      'END_ADDRESS'     : (0x1,0x8cfe),
      'ACCESS_TYPE'     : 2,
      'WR_DATA'         : 0,
      }

##################### System Area #################################

prepETFPrm_149 = {
   'test_num'              : 149,
   'prm_name'              : 'prepETFPrm_149',
   'timeout'               : 1000,
   'spc_id'                : 1,
   'CWORD1'                : 0x8000,
   'TLEVEL'                : 0x45,
   }

readETFPrm_130 = {
   'test_num'              : 130,
   'prm_name'              : 'readETFPrm_130',
   'timeout'               : 60,
   'spc_id'                : 1,
   'CWORD2'                : 0x00FF,
   }

##################### Channel #####################################
channelType = {
   '9ZU' : 'AGERE',
   '9YH' : 'AGERE',
   '9TS' : 'AGERE',
   '9TT' : 'AGERE',
   '9SM' : 'AGERE',
   '9XK' : 'AGERE',
   }

##################### RAP #####################################

RAP_Offsets = {
   # RAP Rev is 1st key
   '16.0':{
      'RD_DLY':{
         'OFFSET' : 0x16B,
         'MASK'   : 0x7
         },
      'ENRDDLY':{
         'OFFSET' : 0x16B,
         'MASK'   : 0x100
         },
      },
   '16.1':{
      },
   '16.2':{
      'RD_DLY':{
         'OFFSET' : 0x16A,
         'MASK'   : 0x7
         },
      'ENRDDLY':{
         'OFFSET' : 0x16A,
         'MASK'   : 0x100
         },
      },
   }

Default_TPI_Format = {
   'ATTRIBUTE'    : 'RAP_REV',
   'DEFAULT'      : '580K',
   'MAP'          : { '480K': ('8.2.3D.3','8.2.3D.4','8.2.3D.5','8.2.3D.6','8.2.3D.7','8.2.3D.8','8.2.3D.9','8.2.3D.A','8.2.3D.B','8.2.3D.C','8.2.3D.D','8.2.3D.E','8.2.3D.F','8.2.3D.10','8.2.3F.B0','8.2.3F.B1'), },
   '580K'         : 0.85,
   '480K'         : 1.0,
}

##################### Pre-Amp #####################################
PreAmpTypes = {
   ##   Dictionary items consist of preampID: (PREAMP_TYPE, preampRev List)
   'LSI' : {
      'CODE_TYPE' : 'RAPT',
      0xBE        : ('LSI5235',[]), # HAMR related. Starwood eval
      0x6D        : ('AGERE7538',[]),
      0x6A        : ('LSI7830',[]),
      0x6B        : ('LSI7830',[]),
      0x73        : ('LSI7831',[]),
      0x71        : ('LSI7831',[]),
      0x72        : ('LSI7831',[]),
      0xA5        : ('LSI8831',[]),
      0xA6        : ('LSI8831',[]),
      0xA7        : ('LSI8832',[]),
      0xB2        : ('LSI8834',[]), # 2 channel
      0xB3        : ('LSI8834',[]), # 4 channel
      0xB4        : ('LSI8834',[]), # 6 channel
      0xB5        : ('LSI8834',[]), # 10 channel
      0xA9        : ('LSI8832',[]), # 2 channel low-Z preamp
      0xAC        : ('LSI8832',[]), # 4 channel low-Z preamp
      0xA8        : ('LSI8832',[]), # 6 channel low-Z preamp
      0xA1        : ('LSI2731',[]),
      0xA3        : ('LSI2731',[]),
      0xB6        : ('LSI2935',[]),
      0xB0        : ('LSI2935',[]), # 2 channel
      0xB9        : ('LSI5230',[]),
      0xBA        : ('LSI5230',[]),
      0x8101      : ('LSI5231',[]), # 2Ch
      0x8111      : ('LSI5231',[]), # 4Ch
      0x8100      : ('LSI5231',[]), # 2Ch
      0x8110      : ('LSI5231',[]), # 4Ch
      0xA1        : ('LSI2731',[]),
      0xAE        : ('LSI2739',[]),
      0xAF        : ('LSI2739',[]),
      0xD         : ('LSI2958',[]), # 4 channel 16reg used for M9
      0x8200      : ('LSI5830',[]), # 2Ch 3G+ Preamp
      0x8210      : ('LSI5830',[]), # 4Ch 3G+ Preamp
      0x8231      : ('LSI5830',[]), # 8Ch 3G+ Preamp
      0x8251      : ('LSI5830',[]), # 12Ch 3G+ Preamp
      0x8230      : ('LSI5830',[]), # 8Ch 3G+ Preamp
      0x8250      : ('LSI5830',[]), # 12Ch 3G+ Preamp
      },
   'AGERE' : {
      'CODE_TYPE' : 'RAPT',
      0x6D        : ('AGERE7538',[]),
      0x6A        : ('LSI7830',[]),
      0x6B        : ('LSI7830',[]),
      0x73        : ('LSI7831',[]),
      0x71        : ('LSI7831',[]),
      0x72        : ('LSI7831',[]),
      0xA5        : ('LSI8831',[]),
      0xA6        : ('LSI8831',[]),
      0xA7        : ('LSI8832',[]),
      0xB2        : ('LSI8834',[]), # 2 channel
      0xB3        : ('LSI8834',[]), # 4 channel
      0xB4        : ('LSI8834',[]), # 6 channel
      0xB5        : ('LSI8834',[]), # 10 channel
      0xA9        : ('LSI8832',[]), # 2 channel low-Z preamp
      0xAC        : ('LSI8832',[]), # 4 channel low-Z preamp
      0xA8        : ('LSI8832',[]), # 6 channel low-Z preamp
      0xA1        : ('LSI2731',[]),
      0xA3        : ('LSI2731',[]),
      0xB6        : ('LSI2935',[]),
      0xA1        : ('LSI2731',[]),
      0xAE        : ('LSI2739',[]),
      0xAF        : ('LSI2739',[]),
      0xD         : ('LSI2958',[]), # 4 channel 16reg used for M9
      },
   'TI' : {
      'CODE_TYPE' : 'RAPT',
      0x45        : ('TI1842',[]),
      0x4C        : ('TI1843',[]),
      0x4E        : ('TI3940',[]),
      0x52        : ('TI3940',[]),
      0x59        : ('TI3941',[]),
      0x58        : ('TI3941',[]),
      0x57        : ('TI3941',[]),
      0x5D        : ('TI3941',[]),
      0x55        : ('TI3945',[]),
      0x56        : ('TI3945',[]),
      0x60        : ('TI3945',[]),
      0x64        : ('TI3945',[]),
      0x66        : ('TI3448',[]),
      0x67        : ('TI3946',[]), # 2 channel low-Z preamp
      0x6C        : ('TI3946',[]), # 4 channel low-Z preamp
      0x68        : ('TI3946',[]), # 6 channel low-Z preamp
      0x69        : ('TI3946',[]),
      0xC5        : ('TI3946',[]), # 6 channel 1.8V preamp
      0xCA        : ('TI3948',[]), # 2 channel
      0xCB        : ('TI3948',[]), # 4 channel
      0xCC        : ('TI3948',[]), # 6 channel
      0xCD        : ('TI3948',[]), # 10 channel
      0xC8        : ('TI3453',[]),
      0xD1        : ('TI5551',[]),
      0xD0        : ('TI5551',[]),
      0x341       : ('TI5551',[]),
      0x340       : ('TI5551',[]),
      0xDA        : ('TI5552',[]),
      0xDB        : ('TI5552',[]),
      0xC101      : ('TI7550',[]),
      0xC111      : ('TI7550',[]),
      0xC100      : ('TI7550',[]),
      0xC110      : ('TI7550',[]),
      0xC200      : ('TI7551',[]), # 2Ch 3G+ Preamp
      0xC210      : ('TI7551',[]), # 4Ch 3G+ Preamp
      0x61        : ('TI3449',[]),
      0xC7        : ('TI3453',[]),
      0xC9        : ('TI3453',[])
      }
   }

DefaultHsaWaferCode = { # for switch off and VE
   "ATTRIBUTE" : 'HGA_SUPPLIER',
   "DEFAULT"   : 'RHO',
   "RHO"       : 'PD7',
   "HWY"       : {
      'ATTRIBUTE'       : 'IS_2D_DRV',
      'DEFAULT'         : 0,
      0                 : '5A5J0',
      1                 : '5A99G', #as POR1
   },
   "TDK"       : {
      'ATTRIBUTE'       : 'IS_2D_DRV',
      'DEFAULT'         : 0,
      0                 : '5F057',
      1                 : '5F816',
   },
}

DefaultMediaPartNum = { # for switch off and VE
   'ATTRIBUTE'       : 'IS_2D_DRV',
   'DEFAULT'         : 0,
   0                 : '100789054',
   1                 : '100789054',
}

MediaType_List = {
   'R5.1' : (100770622,),
   'R6.4' : (100773694,),
   'R7.0' : (100784538, 100786095, 100786096,),
   'R8.0' : (100789054, 100790595, 100790597, 100793390,),
   'R10'  : (100794093, 100795936, 100798272, 100798273, 100798091, 100798094, 100801964,100821440),   # R10 and R10.1
   'R11'  : (100799667, 100803558, 100808986, 100808987, 100808990, 100740712, 100809147,100812115, 100812116, 100804643, 100812467, 100812468, 100812469, 100816070),   #R11, Fuji R11
   'R12'  : (100804148, 100805340, 100813473, 100813379, 100815268, 100815265, 100815266, 100815267, 100816072, 100818155, 100818158, 100818283, 100815537),
   'C677' : (100776122,),
   'C655' : (100787070,),
   'C572' : (100791451,),
}

IBE3_HsaPartNum = (100792887, 100792888, 100792889, 100793148, 100793149, )
UV_MediaPartNum = (100793390, 100794093, 100795936, 100798272, 100798273, 100798091, 100798094, 100799667, 100803558, 100801964, 100805340, 100804148, 100808986, 100808987, 100808990, 100740712, 100809147,100812115, 100812116, 100804643)

MDSW_DiscLotNum = ('U9', 'A')

#### - dictionary for Ang Head Cal workaround
spinup_D00_Prm = {
   'test_num'              : 1,
   'prm_name'              : 'spinup_D00_Prm',
   'timeout'               : 100,
   'spc_id'                : 1,
   'CWORD1'                : 0x0001,
   'MAX_START_TIME'        : 200,
   'DELAY_TIME'            : 50,
   'SYNC_REQUIRED'         : (),
   }

prm_030_continuous_seek = {
   'test_num'           : 30,
   'prm_name'           : 'prm_030_continuous_seek',
   'timeout'            : 3600,
   'spc_id'             : 1,
   'CWORD1'             : 0x0013,
   'CWORD2'             : 0xBABE,
   'START_CYL'          : (0x02, 0xE630,),   # trk 230000 =(0x03, 0x8270,); 190000 = (0x02, 0xE630,)
   'END_CYL'            : (0x02, 0xE630,),
   'PASSES'             : 1,
   'TIME'               : (0, 0xFFFF, 0xFFFF),
   'BIT_MASK'           : (0, 0),
   #'SEEK_DELAY'         : 10,
   }
#### - end of dictionary for Ang Head Cal workaround

spinupPrm_1 = {
   'test_num'              : 1,
   'prm_name'              : 'spinupPrm_1',
   'timeout'               : 100,
   'spc_id'                : 1,
   'CWORD1'                : 0x0001,
   'MAX_START_TIME'        : 200,
   'DELAY_TIME'            : 50,
   }

spinupPrm_2 = {
  'test_num':1,
  'prm_name':'spinupPrm_2',
  'timeout':100,
  'spc_id' : 1,
  #"CWORD1" : (0x1,),
  "MAX_START_TIME" : (200,),
  "DELAY_TIME" : (5,),
}

spinupPrm_3 = {
   'test_num' : 1,
   'prm_name' : 'spinupPrm_3',
   'timeout'  : 100,
   'spc_id'   : 1,
}

MDWUncalSpinup = {
   'spc_id'                : 1,
   'timeout'               : 100,
   'CWORD1'                : 0x0001,
   'MAX_START_TIME'        : 500,
   'DELAY_TIME'            : 50,
   }

spindownPrm_2 = {
   'test_num'              : 2,
   'prm_name'              : 'spindownPrm_2',
   'timeout'               : 100,
   'spc_id'                : 1,
   }

spinupPrm_Lombard_1 = {
   'test_num'              : 1,
   'prm_name'              : 'spinupPrm_Lombard_1',
   'timeout'               : 100,
   'spc_id'                : 1,
   'CWORD1'                : 0x0000,
   'MAX_START_TIME'        : 200,
   'DELAY_TIME'            : 50,
   }

SAMTOL_index = 42   #MEGALODON SATA - symbol table entry 302, offset 21, set bit 12 -- offset = 21*2

heaterResistancePrm_80 = {
   'test_num'              : 80,
   'prm_name'              : 'Heater Resistance Measurement',
   'spc_id'                : 1,
   'CWORD1'                : 0x0005,   # Measure heater resistance on the ramp
   'HEATER'                : (0xFD0E, 0x0001),
   'TEST_CYL'              : ('DATA', 0.5, 0),
   'SEC_CYL'               : (0x0001, 0xDE21),
   'HEAD_RANGE'            : 0xFFFF,
   'MINIMUM'               : {
         'ATTRIBUTE'          : 'HGA_SUPPLIER',
         'DEFAULT'            : 'RHO',
         'HWY'                : 0X2D00,
         #'TDK'                : 0X2D00,
         'RHO'                : 0X2D00,
      },
   'MAXIMUM'               : {
         'ATTRIBUTE'          : 'HGA_SUPPLIER',
         'DEFAULT'            : 'RHO',
         'HWY'                : 0X9600,
         #'TDK'                : 0X9600,
         'RHO'                : 0x7800,
      },
   }


prm_ClearDBILog_101 = {
   'test_num'              : 101,
   'prm_name'              : 'clearDBILog_101',
   'timeout'               : 600000,
   'spc_id'                : 1,
}


prm_HdLoadDamageWrite_109 = {
   'test_num'              : 109,
   'prm_name'              : 'prm_HdLoadDamageWrite_109',
   'timeout'               : 14400*numHeads,
   'spc_id'                : 1,
   'CWORD1'                : 0x0002,
   'CWORD2'                : 0x0800,
   'RW_MODE'               : 0x0100,
   'START_CYL'             : (0x0000, 0x0000),
   'END_CYL'               : (0x0000, 0x1770),   # 6000
   'HEAD_RANGE'            : 0x00FF,
   'HEAD_CLAMP'            : 2000,
   'TRACK_LIMIT'           : 5,
   'ZONE_LIMIT'            : 50000,
   'ERRS_B4_SFLAW_SCAN'    : 1,
   'SWD_RETRY'             : 0x0305,
   'SET_OCLIM'             : 4,
   'FREQUENCY'             : 667,
   }

prm_HdLoadDamageRead_109 = {
   'test_num'           : 109,
   'prm_name'           : 'prm_HdLoadDamageRead_109',
   'timeout'            : 72000,
   'spc_id'             : 1,
   'CWORD1'             : 0x0442,
   'CWORD2'             : 0x0880,
   'CWORD4'             : 0x0020,
   'RW_MODE'            : 0x4000,
   'START_CYL'          : (0x0000, 0x0000),
   'END_CYL'            : (0x0000, 0x1770),   # 6000
   'HEAD_RANGE'         : 0x00FF,
   'PASS_INDEX'         : 0,
   'HEAD_CLAMP'         : 600,
   'TRACK_LIMIT'        : 80,
   'ZONE_LIMIT'         : 65000,
   'IGNORE_UNVER_LIMIT' : (),
   'DIVISOR'            : 75,
   'TA_THRESHOLD'       : 20,
   'ERRS_B4_SFLAW_SCAN' : 1,
   'VERIFY_GAMUT'       : (2, 3, 10),
   'FREQUENCY'          : 667,
   'SET_XREG00'         : (0x00D2, 0x0001, 0x1BCC),   # TAEP_EN
   'SET_XREG01'         : (0x00D2, 0x0003, 0x1B74),   # TA_HOLD - 1
   'SET_XREG02'         : (0x00D2, 0x0003, 0x1B30),   # TA_DLY - 0
   'SET_XREG03'         : (0x0099, 0x0006, 0x1BFC),   # ZGRDiff
   'SET_XREG04'         : (0x00A5, 0x0000, 0x1BCC),   # ZGSR
   'SET_XREG05'         : (0x0095, 0x0000, 0x1B76),   # GUG_flaw
   'SET_XREG06'         : (0x00E5, 0x0000, 0x1B77),   # DEFSCAN
   'SET_XREG07'         : (0x0095, 0x0005, 0x1B53),   # GUGACQR
   'SET_XREG09'         : (0x00E6, 0x0003, 0x1BB8), # QM_LEN2&QM_LVL2
   'SET_XREG08'         : (0x0095, 0x0000, 0x1B20),   # GUGR
   'SET_XREG15'         : (0x00E1, 0x0002, 0x1B40),   # QMTOL
   'SET_XREG16'         : (0x00E1, 0x0005, 0x1BC8),   # QM_LEN
   'SET_XREG17'         : (0x00EA, 0x000C, 0x1B70),   # QM_LVL
   'SET_XREG18'         : (0x00B0, 0x005A, 0x1BF8),   # SHADOWR
   'SET_XREG19'         : (0x00B2, 0x005A, 0x1B70),   # GWIN_SEL_2T  vgarsh
   'SET_XREG20'         : (0x00A6, 0x0002, 0x1B32),   # ZPSLENR
   'SET_XREG21'         : (0x00E6, 0x0090, 0x1B70), # QM_LEN2&QM_LVL2
   'SET_XREG22'         : (0x00E4, 0x0001, 0x1BD8),   # DEF_SEP
   'SET_XREG23'         : (0x00E7, 0x0014, 0x1B50),   # MAXCNT
   'SET_XREG24'         : (0x0366, 0x0000, 0x1BA9),   # Sets GWIN_SEL_2T (VGAR), ChReg 18C[10:9]
   'SET_XREG25'         : (0x0366, 0x0000, 0x1BFB),   # Sets GWIN_CNT_2T (8T), ChReg 18C[15:11]
   'SET_XREG26'         : (0x0364, 0x0100, 0x1B80),   # Sets GWIN_THRSH_2T (1.41dB), ChReg 18E[8:0]
   'SET_XREG28'         : (0x00A6, 0x0000, 0x1B74),   # ACQLENR
   'FSB_SEL'            : (0x0089, 0x0000),
   }

t315_hd_instability_spec = 56 # HD_INSTABILITY_METRIC >= 56

prm_T315_Data = {
   'test_num'                 : 315,
   'prm_name'                 : "T315_Data",
   'spc_id'                   : 1,
   "OFFSET"                   : 0,  #-10(0xfff6)  default 0
   "timeout"                  : 2000,
   "CWORD1"                   : {
      'ATTRIBUTE'             : 'nextState',
      'DEFAULT'               : 'T315_COMMON',
      'T315_COMMON'            : { #RUN_T315_3, RUN_T315_4, RUN_T315_5
         'ATTRIBUTE'          : 'SMR',
         'DEFAULT'            : 0,
         0                    : 0x000F,
         1                    : 0x0007 | (testSwitch.FE_0255243_505898_T315_ODD_EVEN_ZONE<< 5),
      },
      'RUN_T315_1'            : {
         'ATTRIBUTE'          : 'SINGLEPASSFLAWSCAN',
         'DEFAULT'            : 0,
         0                    : 0x0007 | (testSwitch.FE_0255243_505898_T315_ODD_EVEN_ZONE<< 5),
         1                    : 0x0017 | (testSwitch.FE_0255243_505898_T315_ODD_EVEN_ZONE<< 5),#disable defect free band chk
      },
      'RUN_T315_2'            : {
         'ATTRIBUTE'          : 'SINGLEPASSFLAWSCAN',
         'DEFAULT'            : 0,
         0                    : 0x0007 | (testSwitch.FE_0255243_505898_T315_ODD_EVEN_ZONE<< 5),
         1                    : 0x0017 | (testSwitch.FE_0255243_505898_T315_ODD_EVEN_ZONE<< 5),#disable defect free band chk
      },
      'RUN_T315_SUM_SPF'      : 0x8000, #only sum the measurement
      'RUN_T315_SUM'          : 0x8001 | (testSwitch.FE_0255243_505898_T315_ODD_EVEN_ZONE<< 5),
      'HEAD_SCRN2'            : 0x8001 | (testSwitch.FE_0255243_505898_T315_ODD_EVEN_ZONE<< 5),
   },
   "HEAD_RANGE"               : 0x00ff,
   "ZONE"                     : 0x00ff,
   "PERCENT_LIMIT"            : 0,
   "ITERATIONS"               : 100,
   "NUM_TRKS_AVERAGED"        : {
      'ATTRIBUTE' : 'programName',
      'DEFAULT'   : 'default',
      'default'   : 1, # 1 bands
   },
   'FILE_ID'                  : {
         'ATTRIBUTE'             : 'nextState',
         'DEFAULT'               : 'RUN_T315_1',
         'RUN_T315_1'            : 1,
         'RUN_T315_2'            : 2,
         'RUN_T315_3'            : 3,
         'RUN_T315_4'            : 4,
         'RUN_T315_5'            : 5,
         'RUN_T315_SUM'          : 5,
         'RUN_T315_SUM_SPF'      : 2, #need at >=2 measurement value
         'HEAD_SCRN2'            : 5,
   },
}

prm_T315_SUM = {
   'test_num'                 : 315,
   'prm_name'                 : "T315_SUM",
   'spc_id'                   : 1,
   "OFFSET"                   : 0,  #-10(0xfff6)  default 0
   "timeout"                  : 2000,
   "CWORD1"                   : 0x8001,
   "HEAD_RANGE"               : 0x00ff,
   "ZONE"                     : 0x00ff,
   "PERCENT_LIMIT"            : 0,
   "ITERATIONS"               : 100,
   "NUM_TRKS_AVERAGED"        : 10,      # DEFAULT IS 5
   'FILE_ID'                  : 5,
}

prm_T315_RESET = {
   'test_num'                 : 315,
   'prm_name'                 : "T315_RESET",
   'spc_id'                   : 1,
   "OFFSET"                   : 0,  #-10(0xfff6)  default 0
   "timeout"                  : 2000,
   "CWORD1"                   : 0x4000,
   "HEAD_RANGE"               : 0x00ff,
   "ZONE"                     : 0x00ff,
   "PERCENT_LIMIT"            : 0,
   "ITERATIONS"               : 100,
   "NUM_TRKS_AVERAGED"        : 10,      # DEFAULT IS 5
   'FILE_ID'                  : 5,
}

prm_HdLoadDamageLimit_140 = {
   'test_num'              : 140,
   'prm_name'              : 'prm_HdLoadDamageLimit_140',
   'timeout'               : 1800,
   'spc_id'                : 1,
   'CWORD1'                : 0x2000,
   'UNVER_LIMIT'           : 0xFFFF,
   'VERIFIED_DRIVE_LIMIT'  : 0xFFFF,            # Verified flaw limit for drive.
   'VERIFIED_HEAD_LIMIT'   : 0xFFFF,            # Verified flaw limit per head
   'VERIFIED_TRACK_LIMIT'  : 0xFFFF,            # Verified flaw limit per track
   'VERIFIED_CYL_LIMIT'    : 0xFFFF,            # Verified flaw limit per cylinder
   'UNVER_HD_ZONE_LIMIT'   : (0xFFFF, 0xFFFF),  # Unverified flaw limit per head-zone (in hundreds)
   'HEAD_UNVER_LIMIT'      : (0xFFFF, 0xFFFF),  # Unverified flaw limit per head (in hundreds).
   'PATTERN_IDX'           : 0xFFFF,            # Index pattern mask (Pattern is only 2-byte long)
   }

prm_163_MDW_QLTY_OD = {                         # Rd pattern check OD
   'test_num'              : 163,
   'prm_name'              : 'prm_163_MDW_QLTY_OD',
   'timeout'               : 18000,
   'spc_id'                : 1,
   'CWORD1'                : 0xC000,            # Use logical tracks, at the OD.
   'INTERVAL_SIZE'         : 1000,              # Run 1000 tracks at the OD starting at track 0.
   'READ_MODE'             : (),                # Read mode, no writes.  Super sector reads are performed.
   'LOOP_CNT'              : 2,                 # Causes each track to be read 2 times (2 revs).
   'OB_SECT_LMT'           : 0,                 # If set to a non zero value, enables error code 'OBSERVER_SECTOR_LIMIT' 11069.
   'BAD_ID_LMT'            : 0,                 # If set to a non zero value, enables error code 'BAD_ID_LIMIT' 10111.
   'NO_TMD_LMT'            : 0,                 # If set to a non zero value, enables error code 'NO_TMD_LIMIT' 10350.
   'HEAD_RANGE'            : 0x00FF,
   'INTERVAL_NUM'          : 1,
   'UNSAFE_LMT'            : 0,                 # A limit of 0 disables the limit check.  This is the default value, and doesn't need to be passed in.
   'S_OFFSET'              : 0,                 # No offset
   'RW_MODE'               : 0x0020,            # RW Mode. Run the test using the "read track" function
   }

prm_163_MDW_QLTY_ID = {                         # Rd pattern check ID
   'test_num'              : 163,
   'prm_name'              : 'prm_163_MDW_QLTY_ID',
   'timeout'               : 18000,
   'spc_id'                : 2,
   'CWORD1'                : 0xA000,            # Use logical tracks, at the ID.
   'INTERVAL_SIZE'         : 1000,              # Run 1000 tracks at the ID starting at MaxLogicalCyl(head) - INTERVAL_SIZE, and extending to MaxLogicalCyl(head).
   'READ_MODE'             : (),                # Read mode, no writes.  Super sector reads are performed.
   'LOOP_CNT'              : 2,                 # Causes each track to be read 2 times (2 revs).
   'OB_SECT_LMT'           : 0,                 # If set to a non zero value, enables error code 'OBSERVER_SECTOR_LIMIT' 11069.
   'BAD_ID_LMT'            : 0,                 # If set to a non zero value, enables error code 'BAD_ID_LIMIT' 10111.
   'NO_TMD_LMT'            : 0,                 # If set to a non zero value, enables error code 'NO_TMD_LIMIT' 10350.
   'HEAD_RANGE'            : 0x00FF,
   'UNSAFE_LMT'            : 0,                 # A limit of 0 disables the limit check.  This is the default value, and doesn't need to be passed in.
   'S_OFFSET'              : 0,                 # No offset
   'RW_MODE'               : 0x0020,            # RW Mode. Run the test using the "read track" function
   }

#if not testSwitch.extern.FE_0202123_228373_KARNAK_YARRAR_LSI and not testSwitch.M10P:
pgaGainCalPrm_177_1 = {
   'test_num'   : 177,
   'prm_name'   : 'pgaGainCalPrm_177',
   'timeout'    : 1800,
   'spc_id'     : 1,
   "TEST_CYL"   : (2,58928,),
   'HEAD_RANGE' : (0x00ff,),
   'CWORD1'     : (0x0003,),
   'CWORD2'     : (0x0001,),
   'SET_ANY_REG': (0, 0),
}

if testSwitch.MARVELL_SRC:
   pgaGainCalPrm_177_1['THRESHOLD']  = 60      # per recommendation from Radin GEN3B 25APR2012
   pgaGainCalPrm_177_1['THRESHOLD2'] = 100     # per recommendation from Radin GEN3B 25APR2012

if testSwitch.MARVELL_SRC and testSwitch.WA_0276349_228371_CHEOPSAM_SRC_BRING_UP:
   pgaGainCalPrm_177_1['THRESHOLD']  = 90  # per recommendation from servo
   pgaGainCalPrm_177_1['THRESHOLD2'] = 120 # per recommendation from servo

pgaGainCalPrm_177 = {
   'test_num'           : 177,
   'prm_name'           : 'pgaGainCalPrm_177',
   'timeout'            : 1800,
   'spc_id'             : 1,
   "TEST_CYL"           : (2,58928,),
   "HEAD_RANGE"         : (0x00ff,),
   "THRESHOLD"          : (240,), #For Chengai
   "THRESHOLD2"         : (320,), #For Chengai
   "CWORD1"             : (0x0001,),
}

pgaPostAFHGainCalPrm_177 = {
   'test_num'              : 177,
   'prm_name'              : 'pgaPostAFHGainCalPrm_177',
   'timeout'               : 1800,
   'spc_id'                : 1,
   'HEAD_RANGE'            : 0x00FF,
   'CWORD1'                : 0x0000,
   'CWORD2'                : 5,
   'SET_ANY_REG'           : (1, 1),
   }

PresetAGCPrm_186 = {
   'test_num'              : 186,
   'prm_name'              : 'PresetAGCPrm_186',
   'timeout'               : 1800,
   'spc_id'                : 1,
   'CWORD1'                : 0x0003,
   }

if testSwitch.RUN_VBIAS_T186_A2D:
   CURRENT_MODE = 128
   VOLTAGE_MODE = 1



SkipWriteDetect_198 = {
   'test_num'              : 198,
   'prm_name'              : 'SkipWriteDetect_198',
   'timeout'               : 36000,
   'spc_id'                : 1,
   'CWORD1'                : 0x10EE,
   'OFFSET_SETTING'        : (0, 2, 0),
   'SEEK_NUMS'             : 800,
   'SEEK_DELAY'            : 0,
   'SWD_DELTA'             : 4,
   'SWD_4_SAMP_THRESH'     : 3,
   'SWD_FILTER'            : 2,
   'ZONE_MASK'             : (0xFFFF, 0xFFFF),
   'FLY_HEIGHT'            : 0x0014,
   'DVGA_MAX'              : 128,
   'FVGA_MAX'              : 128,
   'RVGA_MAX'              : 128,
   }


SkipWriteDetectorAdjustment_227 = {
   'test_num'              : 227,
   'prm_name'              : 'SkipWriteDetectorAdjustment_227',
   'timeout'               : 3000 * numHeads,
   'spc_id'                : 1,
   'CWORD1'                : 0x0191,
   'TEST_HEAD'             : 0xFF,
   'ZONE_MASK'             : (0xFFFF, 0xFFFF),
   'DELTA_LIMIT'           : 12,
   }


SkipWriteDetectorVerification_227 = {
   'test_num'              : 227,
   'prm_name'              : 'SkipWriteDetectorVerification_227',
   'spc_id'                : 1,
   'timeout'               : 3000 * numHeads,
   'CWORD1'                : 0x0182,
   'TEST_HEAD'             : 0xFF,
   'ZONE_MASK'             : (0xFFFF, 0xFFFF),
   'DELTA_LIMIT'           : 15,
   }


WIJITAAdj_227 = {
   'test_num'              : 227,
   'prm_name'              : 'WIJITAAdj_227',
   'spc_id'                : 1,
   'timeout'               : 600 * numHeads,
   'CWORD1'                : 0x8004,
   'SWD_DELTA'             : 10,
   'ZONE_MASK'             : [1, 0x8361],
   'TEST_HEAD'             : 255,
   'DELTA_LIMIT'           : 12,
   }

RV_ADC_OFFSET_36 = {
   'test_num'              : 36,
   'prm_name'              : 'RV_ADC_OFFSET_36',
   'spc_id'                : 1,
   'timeout'               : 120,
   'CWORD1'                : 0x0020,
   }

PresetAGC_InitPrm_186 = {
   'test_num'              : 186,
   'prm_name'              : 'PresetAGC_InitPrm_186',
   'timeout'               : 600,
   'spc_id'                : 1,
   'CWORD1'                : {
      'ATTRIBUTE'          : 'nextState',
      'DEFAULT'            : 'INIT',
      'INIT'               : 0x1001,
      'FOF_SCRN'           : 0x1005,
      'HEAD_CAL'           : 0x1005,
      'FAIL_PROC'          : 0x1006,
      },
   'MRBIAS_RANGE'          : {      # MR Bias Limits - MRE Resistance Limits (Max, Min) Ohms
      'ATTRIBUTE'          : 'HGA_SUPPLIER',
      'DEFAULT'            : 'RHO',
#CHOOI-18May17 OffSpec
#       'RHO'                : (1300, 80),
#       'HWY'                : (1100, 180),
#       'TDK'                : (1300, 80),},
      'RHO'                : (10000, 10),
      'HWY'                : (10000, 10),
      'TDK'                : (10000, 10),},
   'MAXIMUM'               : {      # Maximum Bias Voltage Limit, mV
      'ATTRIBUTE'          : 'HGA_SUPPLIER',
      'DEFAULT'            : 'RHO',
      'RHO'                : {
         'ATTRIBUTE' : 'HSA_WAFER_CODE',
         'DEFAULT'   : 'OT4',
         'NT4'       : 150,
         'OT4'       : 150,
         'N5B'       : 150,
         'N1W'       : 150,
         'QD7'       : 150,
         'NL2'       : 150,
         'NI0'       : 140,
         'NU7'       : 140,
         'N2Q'       : 140,
         'OG8'       : 140,
         'N4Z'       : 140,
         'O2Q'       : 140,
         'NG8'       : 140,
         'N5T'       : 140,
         'BZ7'       : 140,
         'AL1'       : 140,
      },
      'HWY'                : 140,
      'TDK'                : 140,
   },
   'LIMIT'                 : {      # Maximum Bias Power Limit, uW
      'ATTRIBUTE'          : 'HGA_SUPPLIER',
      'DEFAULT'            : 'RHO',
      'RHO'                : 100,
      'HWY'                : 100,
      'TDK'                : 100,},
}

if testSwitch.FE_0189781_357595_HEAD_RECOVERY:
   PresetAGC_InitPrm_186["CWORD1"]["HEAD_CAL"] |= 0x0040 #Save MRR value to PC file

setZapOffPrm_011_Direct = {
   'test_num'              : 11,
   'prm_name'              : 'setZapOffPrm_011_Direct',
   'timeout'               : 300,
   'PARAM_0_4'             : [0x00FF, 0x0000, 0, 0, 0]
   }

PresetAGC_InitPrm_186_PostPRE2 = {
   'test_num'              : 186,
   'prm_name'              : 'PresetAGC_InitPrm_186_PostPRE2',
   'spc_id'                : 1,
   'timeout'               : 600,
   'CWORD1'                : 0x1003,
   'MRBIAS_RANGE'          : (850, 100),
   'MAXIMUM'               : 140,
   'LIMIT'                 : 100,
   }

if testSwitch.FE_0194098_322482_SCREEN_DETCR_OPEN_CONNECTION:
   DETCR_OpenScr_186 = {
      'test_num'              : 186,
      'prm_name'              : 'DETCR_Open_186',
      'timeout'               : 200,
      'spc_id'                : 1,
      'CWORD1'                : 0x0003,
      'HEAD_RANGE'            : 0x0001,
      'SCREEN_DETCR_OPEN'     : (1,0,10000,0,10000,0,10000,0,0,0,0,0,),
      }

if ConfigVars[CN].get('HDTYPE',0) == 1: # if TDK  head
#CHOOI-19May17 OffSpec
#   PresetAGC_InitPrm_186_PostPRE2['MRBIAS_RANGE']        = (1000, 200)
   PresetAGC_InitPrm_186_PostPRE2['MRBIAS_RANGE']        = (10000, 10)
   PresetAGC_InitPrm_186_PostPRE2['MAX_MR_BIAS_SCALAR']  = 2



# Parameters for MR Resistance Check while on ramp
get_MR_Values_on_ramp_186 = {
   'test_num'              : 186,
   'prm_name'              : 'get_MR_Values_on_ramp_186',
   'spc_id'                : 1,
   'CWORD1'                : 0x1004,  # Only gather and report MR resistance values, while on ramp
   'MRBIAS_RANGE'          : {      # MR Bias Limits - MRE Resistance Limits (Max, Min) Ohms
      'ATTRIBUTE'          : 'HGA_SUPPLIER',
      'DEFAULT'            : 'RHO',
#CHOOI-19May17 OffSpec
#       'RHO'                : (750, 100),
#       'HWY'                : (1100, 180),
#       'TDK'                : (1000, 200),},
      'RHO'                : (10000, 10),
      'HWY'                : (10000, 10),
      'TDK'                : (10000, 10),},
   'MAXIMUM'               : {      # Maximum Bias Voltage Limit, mV
      'ATTRIBUTE'          : 'HGA_SUPPLIER',
      'DEFAULT'            : 'RHO',
      'RHO'                : 140,
      'HWY'                : 140,
      'TDK'                : 140,},
   'LIMIT'                 : {      # Maximum Bias Power Limit, uW
      'ATTRIBUTE'          : 'HGA_SUPPLIER',
      'DEFAULT'            : 'RHO',
      'RHO'                : 140,
      'HWY'                : 100,
      'TDK'                : 100,},
   }

headPolarityTest_26 = {
   'test_num'              : 26,
   'prm_name'              : 'headPolarityTest_26',
   'spc_id'                : 1,
   'timeout'               : 120,
   'FAIL_SAFE'              : (),
   }


# Parameters for Delta MR Resistance Check
##Test 321
resRangeLim = 50  # Range (max-min) MR resistance change, in percent of baseline

get_MR_Resistance_321 = {
   'test_num'              : 321,
   'prm_name'              : 'get_MR_Resistance_321',
   'spc_id'                : 11000,
   'timeout'               : 600,
   'CWORD1'                : {
     'ATTRIBUTE'          : 'nextState',
     'DEFAULT'            : 'GMR_RES',
     'GMR_RES'            : 0x000D,  #report resistance, measure on disc and skip demod sync
     'FAIL_PROC'          : 0x0000,  #report resistance, measure on ramp
     },
   'RESISTANCE_RANGE'      : {       # MR Bias Limits - MRE Resistance Limits (Max, Min) Ohms,
      'ATTRIBUTE'          : 'HGA_SUPPLIER',
      'DEFAULT'            : 'RHO',
#CHOOI-19May17 OffSpec
#       'RHO'                : (750, 100),
#       'HWY'                : (1100, 180),
#       'TDK'                : (1000, 200),},
      'RHO'                : (10000, 10),
      'HWY'                : (10000, 10),
      'TDK'                : (10000, 10),},
   }


setScopyControlFeatures = {
      'test_num'        : 11,
      'prm_name'        : "Set ScopyControlFeatures",
      'CWORD1'          : 256,
      'timeout'         : 100,
      'START_ADDRESS'   : (0x0011,0x69CC),
      'END_ADDRESS'     : (0x0011,0x69CC),
      'ACCESS_TYPE'     : 1,
      'MASK_VALUE'      : 254,
      'WR_DATA'         : 1,
      }   

readScopyControlFeatures = {
      'test_num'        : 11,
      'prm_name'        : "Read ScopyControlFeatures",
      'CWORD1'          : 1,
      'timeout'         : 100,
      'START_ADDRESS'   : (0x0011,0x69CC),
      'END_ADDRESS'     : (0x0011,0x69CC),
      'ACCESS_TYPE'     : 1,
      }   

SaveSAPtoFLASH = {
      'test_num'        : 178,
      'prm_name'        : "SaveSAPtoFLASH",
      'CWORD1'          : 0x420,
      'timeout'         : 100,
      }   


mrBiasCal_321 = {
   'test_num'              : 321,
   'prm_name'              : 'mrBias_Calibration_321',
   'timeout'               : 600,
   'spc_id'                : 1,
   'CWORD1'                : {
      'ATTRIBUTE'       : 'nextState',
      'DEFAULT'         : 'HEAD_CAL',
      'HEAD_CAL'        : 0x1000,  #do cal, measure on ramp
      'CAL_MR_RES'      : 0x100D,  #do cal, measure on disc and skip demod sync
   },
   'RESISTANCE_RANGE'      : {      # MR Bias Limits - MRE Resistance Limits (Max, Min) Ohms
      'ATTRIBUTE'       : 'HGA_SUPPLIER',
      'DEFAULT'         : 'RHO',
#CHOOI-19May17 OffSpec
#       'RHO'             : (750, 100),
#       'HWY'             : (1100, 180),
#       'TDK'             : (1000, 200),
      'RHO'             : (10000, 10),
      'HWY'             : (10000, 10),
      'TDK'             : (10000, 10),
   },
   'MAX_VOLTAGE'           : { # Maximum Bias Voltage Limit, mV
      'ATTRIBUTE'       : 'HGA_SUPPLIER',
      'DEFAULT'         : 'RHO',
      'RHO'             : {
         'ATTRIBUTE' : 'HSA_WAFER_CODE',
         'DEFAULT'   : 'OT4',
         'NT4'       : 150,
         'OT4'       : 150,
         'N5B'       : 150,
         'N1W'       : 150,
         'QD7'       : 150,
         'NL2'       : 150,
         'NI0'       : 140,
         'NU7'       : 140,
         'N2Q'       : 140,
         'OG8'       : 140,
         'N4Z'       : 140,
         'O2Q'       : 140,
         'NG8'       : 140,
         'N5T'       : 140,
         'BZ7'       : 140,
         'AL1'       : 140,
      },
      'HWY'             : 140,
      'TDK'             : 140,
   },
   'MAX_POWER'             : {      # Maximum Bias Power Limit, uW
      'ATTRIBUTE'          : 'HGA_SUPPLIER',
      'DEFAULT'            : 'RHO',
      'RHO'                : 140,
      'HWY'                : 100,
      'TDK'                : 100,}
   }

mrDeltaLim = 20   # Absolute value of maximum allowed MR resistance change from PRE2 to FNC2


##################### Digital Flawscan #####################################



DFS = {
   'test_num'                 : 2109,
   'prm_name'                 : 'logical_fs_2109',
   'spc_id'                   : 1,
   'timeout'                  : 36000 * numHeads,
   'CWORD1'                   : (0x0022,),
   'CWORD2'                   : {
      'ATTRIBUTE'          : 'RUN_TEST_315',
      'DEFAULT'            : 0,
      0                    : (0x0D80,),
      1                    : (0x0DC0,),
   },
   'START_TLBA'               : (0, 0, 0, 0,),                       ##############  START LBA   #############
   "END_TLBA"                 : (0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF,),   ##############   END LBA    #############
   "CYL_SHIFT"                : (0x000F,0x4240,),                    ##############   LBA INCR   ############# 1,000,000
   "RETRY_LIMIT"              : (3),                                 ############## Write retries #############
   "VERIFY_GAMUT"             : (5, 5, 0),                           ## read retry fail threshold, total read retries, not used
   "DFS_DATA_DEFECT_PAD"      : (2,1,),                             ## Data pad cyls, sectors
   "SID_QM_THRESH"            : (0x80, 0x80, 0x80, 0x80),
   "SID_QM_CONTROL"           : (0x444, 0x1E0, 0x0d00, 0x0d00),
   #'WREVENTRK'                : (),   # perform even/odd
   #'WRODDTRK'                 : (),   # perform even/odd
}


if testSwitch.VBAR_HMS_V4 :
   DFS.update({"SID_QM_THRESH" : (0xA0, 0xA0, 0xA0, 0xA0)})





##################### Particle Sweep ################################

prm_particleSweep = {
   'timeout'               : 20,    # Maximum timeout for one sweep operation
   'spc_id'                : 1,
   'sweepCnt'              : 20,
   'duration'              : 5500,  # Sweep time in mSec
   'dwell'                 : 1,     # Number of dwell revs between each step
   }


prm_particleSweep_212 = {
   'test_num'              : 212,
   'prm_name'              : 'prm_particleSweep_212',
   'spc_id'                : 1,
   'timeout'               : 1000,
   'CWORD2'                : 0x0001,
   'TIMER_MAX'             : 30,
   'PASSES'                : 3,
   'SIDE_RAIL_LEN'         : {
      'ATTRIBUTE':'HGA_SUPPLIER',
      'DEFAULT'   :'RHO',
      'RHO'       : 5,
      'TDK'       : 4,
      },
   }


if testSwitch.shortProcess:
   prm_particleSweep.update({
      'sweepCnt': 1,
   })
   prm_particleSweep_212.update({
      'PASSES': 1,
   })


prm_030_full_sweep = {
   'test_num'           : 30,
   'prm_name'           : 'prm_030_full_sweep',
   'timeout'            : 1200 * numHeads,
   'spc_id'             : 1,
   'CWORD1'             : 0x0123,
   'START_CYL'          : (0x0000, 0x0000),
   'END_CYL'            : (0xFFFF, 0xFFFF),
   'PASSES'             : 575,
   'TIME'               : (0, 0xFFFF, 0xFFFF),
   }

prm_030_continuous_sweep = {
   'test_num'           : 30,
   'prm_name'           : 'prm_030_continuous_sweep',
   'timeout'            : 3600,
   'spc_id'             : 1,
   'CWORD1'             : 0x0013,
   'START_CYL'          : (0x0000, 0x0000),
   'END_CYL'            : (0xFFFF, 0xFFFF),
   'PASSES'             : 25000,
   'TIME'               : (0, 0xFFFF, 0xFFFF),
   'SEEK_DELAY'         : 10,
   }

random_write_seeks_30 = {
   'test_num'           : 30,
   'prm_name'           : 'random_write_seeks_30',
   'timeout'            : 3600,
   'spc_id'             : 1,
   'start_zone'         : 0,
   'end_zone'           : 5,
   'START_CYL'          : (0x0000, 0x0000),
   'END_CYL'            : (0xFFFF, 0xFFFF),
   'CWORD1'             : (0x0324),       # Random Writes seeks
   'CWORD2'             : (0xbabe),
   'PASSES'             : (60000),
   'TIME'               : (0, 0xFFFF, 0xFFFF),
}

#####============== BASIC SWEEP HIGH RPM PARMS ==================================
maxRPM_spinupPrm_4 = {
   'test_num'              : 4,
   'prm_name'              : 'maxRPM_spinupPrm_4',
   'timeout'               : 200,
   'spc_id'                : 1,
   'CWORD1'                : 0x0001,            # 0:7200, 1:9000
   }

defaultRPM_spinupPrm_4 = {
   'test_num'              : 4,
   'prm_name'              : 'defaultRPM_spinupPrm_4',
   'timeout'               : 200,
   'spc_id'                : 1,
   'CWORD1'                : 0x0000,            # 0:7200, 1:9000
   }

maxRPM_spinup_spindownPrm_4 = {
   'test_num'              : 4,
   'prm_name'              : 'maxRPM_spinup_spindownPrm_4',
   'timeout'               : 600,
   'spc_id'                : 1,
   'TIMER_OPTION'          : 300,              # 300 sec (5min)
   'CWORD1'                : 0x0001,
   }

maxRPM_spinup_spindownPrm_4_2 = {
   'test_num'              : 4,
   'prm_name'              : 'HighRPM_spinup_spindownPrm_4',
   'timeout'               : 1000,
   'spc_id'                : 1,
   'TIMER_OPTION'          : 600,              # duration to spin @ high rpm, in seconds
   'CWORD1'                : 0x0001,
   }

changeRPMloops = 1
changeRPMnominalDwell = 30

#####============== BASIC SWEEP HIGH RPM PARMS ( E N D ) =====================

prm_549_ButterflySeek = {
   'test_num'           : 549,
   'prm_name'           : 'prm_549_ButterflySeek',
   'spc_id'             : 1,
   'CTRL_WORD1'         : 0x0007,               # normalHeadScan | autoHeadSelection | reportSeekTimes | timerServo
   'SEEK_OPTIONS_BYTE'  : 0x44,                 # so_st | so_mr
   'TEST_FUNCTION'      : 7,                    # Butterfly Seq Hd
   'START_CYL'          : (0x0000, 0x4E20),     # 20,000
   'END_CYL'            : (0x0001, 0xFBD0),     # 130,000
   'CYLINDER_INCREMENT' : 50,
   'timeout'            : 36000,
   }

prm_549_ReverseSeek = {
   'test_num'           : 549,
   'prm_name'           : 'prm_549_ReverseSeek',
   'spc_id'             : 1,
   'CTRL_WORD1'         : 0x0003,               # normalHeadScan | autoHeadSelection | reportSeekTimes | timerServo
   'SEEK_OPTIONS_BYTE'  : 0x44,                 # so_st | so_mr
   'START_CYL'          : (0x0000, 0x4E20),     # 20,000
   'END_CYL'            : (0x0001, 0xFBD0),     # 130,000
   'TEST_HEAD'          : 0,
   'TEST_FUNCTION'      : 9,
   'CYLINDER_INCREMENT' : 1,
   'timeout'            : 36000,
   }

prm_510_RndWrite = {
   'test_num'           : 510,
   'prm_name'           : 'prm_510_RndWrite',
   'timeout'            : 252000,
   'spc_id'             : 1,
   'CTRL_WORD1'         : 0x0021,               # Random Write mode
   'CTRL_WORD2'         : 0x2080,               # Fixed Pattern
   'STARTING_LBA'       : (0, 0, 0, 0),
   'TOTAL_BLKS_TO_XFR'  : (0x0078, 0x0000),     # 3GiB
   'BLKS_PER_XFR'       : 0x100,
   'DATA_PATTERN0'      : (0x0000, 0x0000),
   'MAX_NBR_ERRORS'     : 0,
   }

prm_510_FPR_MQM = {
   'test_num'           : 510,
   'prm_name'           : 'prm_510_FPR_MQM',
   'timeout'            : 25200,
   'spc_id'             : 1,
   'CTRL_WORD1'         : 0x0012,
   'CTRL_WORD2'         : 0x2080,               # Fixed Pattern
   'STARTING_LBA'       : (0, 0, 0, 0),
   'TOTAL_BLKS_TO_XFR'  : (0x0000, 0x0000),     # Full pack
   'BLKS_PER_XFR'       : 0x100,
   'MAX_NBR_ERRORS'     : 0,
   }

prm_549_ButterflySeekID = {
   'test_num'           : 549,
   'prm_name'           : 'prm_549_ButterflySeekID',
   'spc_id'             : 1,
   'CTRL_WORD1'         : 0x0007,               # autoHeadSelection | normalHeadScan | reportSeekTimes | timerServo
   'SEEK_OPTIONS_BYTE'  : 0x44,                 # so_st | so_mr
   'TEST_FUNCTION'      : 7,                    # Butterfly Seq Hd
   'START_CYL'          : (0x0001, 0x7000),
   'CYLINDER_INCREMENT' : 100,
   'timeout'            : 36000,
   }

prm_549_RandomSeek = {
   'test_num'           : 549,
   'prm_name'           : 'prm_549_RandomSeek',
   'spc_id'             : 1,
   'CTRL_WORD1'         : 0x0007,               # autoHeadSelection | normalHeadScan | reportSeekTimes | timerServo
   'SEEK_OPTIONS_BYTE'  : 0x44,                 # so_st | so_mr
   'TEST_FUNCTION'      : 1,                    # Butterfly Seq Hd
   'NUM_SEEKS'          : (40000),              # target 5 mins
   'timeout'            : 36000,
   }

prm_549_MDODSweep = {
   'test_num'           : 549,
   'prm_name'           : 'prm_549_MDODSweep',
   'spc_id'             : 1,
   'CTRL_WORD1'         : 0x0003,               # reportSeekTimes | timerServo
   'SEEK_OPTIONS_BYTE'  : 0x44,                 # so_st | so_mr
   'TEST_FUNCTION'      : 9,                    # Sequential Reverse Seek
   'START_CYL'          : (0x0000,0x0000,),
   'END_CYL'            : (0x0001,0x3880,),     # Nominal mid cylinder (160000/2),maybe should change for Marina
   'TEST_HEAD'          : 0,
   'CYLINDER_INCREMENT' : (200,),               # Change here to control times
   'timeout'            : 36000,
   }

prm_549_MDIDSweep = {
   'test_num'           : 549,
   'prm_name'           : 'prm_549_MDIDSweep',
   'spc_id'             : 1,
   'CTRL_WORD1'         : 0x0003,               # reportSeekTimes | timerServo
   'SEEK_OPTIONS_BYTE'  : 0x44,                 # so_st | so_mr
   'TEST_FUNCTION'      : 2,                    # Sequential Forward Seek
   'START_CYL'          : (0x0001,0x3880,),     # Nominal mid cylinder (160000/2),maybe should change for Marina
   'END_CYL'            : (0xFFFF,0xFFFF,),
   'TEST_HEAD'          : 0,
   'CYLINDER_INCREMENT' : (200,),               # Change here to control times
   'timeout'            : 36000,
   }

prm_518_SetShippingSectorSize = {
   'test_num' : 518,
   'prm_name' : 'prm_518_SetShippingSectorSize',
   'timeout' : 3600,
  	"DATA_TO_CHANGE" : (0x0000,),
	"MODE_COMMAND" : (0x0001,),
	"MODE_SELECT_ALL_INITS" : (0x0000,),
	"MODE_SENSE_INITIATOR" : (0x0000,),
	"MODE_SENSE_OPTION" : (0x0003,),
	"MODIFICATION_MODE" : (0x0001,),
	"PAGE_BYTE_AND_DATA34" : (0x0E02,0x0F00,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,),
	"PAGE_CODE" : (0x0000,),
	"PAGE_FORMAT" : (0x0000,),
	"SAVE_MODE_PARAMETERS" : (0x0000,),
	"SUB_PAGE_CODE" : (0x0000,),
	"TEST_FUNCTION" : (0x0000,),
	"UNIT_READY" : (0x0000,),
	"VERIFY_MODE" : (0x0000,),
}

prm_511_SAS_Format = {
   'test_num' : 511,
   'prm_name' : 'prm_511_SAS_Format',
   'timeout' : 72000,
	"COMPARE_OPTION" : (0x0000,),
	"COMP_LIST_OF_GRWTH_DEFS" : (0x0001,),
	"CONDITIONAL_FORMAT" : (0x0000,),
	"DEFECT_LIST_FORMAT" : (0x0000,),
	"DISABLE_CERTIFICATION" : (0x0001,),
	"DISABLE_PRIMARY_LIST" : (0x0000,),
	"DISABLE_SAVING_PARAMS" : (0x0000,),
	"END_TRACK" : (0x0000,0x0000,),
	"FORMAT_MODE" : (0x0000,),
	"FORMAT_OPTIONS_VARIABLE" : (0x0001,),
	"HEAD_TO_FORMAT" : (0x0000,),
	"HEAD_TO_FORMAT_LSW" : (0x0000,),
	"HEAD_TO_FORMAT_MSW" : (0x0000,),
	"IMMEDIATE_BIT" : (0x0000,),
	"INIT_PATTERN" : (0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,),
	"INIT_PATTERN_BIT" : (0x0000,),
	"INIT_PATTERN_LENGTH" : (0x0000,),
	"INIT_PATTERN_MODIFIER" : (0x0000,),
	"LBA_INTERVAL" : (0x0000,),
	"START_TRACK" : (0x0000,0x0000,),
	"STOP_FMT_ON_DEFT_LST_ERR" : (0x0000,),
	"TEST_FUNCTION" : (0x0000,),
}

prm_504_DisplaySense = {
   'test_num' : 504,
   'prm_name' : 'prm_504_DisplaySense',
   'timeout' : 1200,
   'spc_id' : 1,
	"CONTROLLER_CHIP_REG" : (0x0000,),
	"NUMBER_REGISTER_BANKS" : (0x0000,),
	"TEST_FUNCTION" : (0x8000,),
	"TRANSLATE_LOGICAL_BLOCK" : (0x0000,),
}

prm_556_SmartFunction = {
   'test_num'              : 556,
   'prm_name'              : 'prm_556_SmartFunction',
   'spc_id'                : 1,
   'timeout'               : 25200,
   'CTRL_WORD1'            : 10,
   }


MQM2_SCRIPT_REV = 'MQM_MN01'

if testSwitch.VBAR_HMS_V4:
   MQM_WeakWrite = (
      ("diagInit", dict(Version = 'Sentosa Weak Write 2010-05-03', OK_Errors = ['3160080', '3160083', '3160084', '3160100', '401009B'], Ignore_Errors = ['4030086', '4030087', '4030088', '4090081'], perRWERR_TypeLimit = 99)),
      ("diagWeakWriteScreen", dict(DataPattern = 0xCAFEBABE, ber_spc_id = 8, spinDownDwell = 60, weakWriteModes = ({'mode':'ID','numTracksToOffset':-10}, {'mode':'MD','numTracksToOffset':0}, {'mode':'OD','numTracksToOffset':10},), failSafe = 1)),
      ("diagRandomWrite", dict(numMinutes = 30, DataPattern = 0x22222222, ber_spc_id = 3)),
      ("diagWeakWriteScreen", dict(DataPattern = 0xBEEFCAFE, ber_spc_id = 7, spinDownDwell = 0, weakWriteModes = ({'mode':'ID','numTracksToOffset':-10}, {'mode':'MD','numTracksToOffset':0}, {'mode':'OD','numTracksToOffset':10},), failSafe = 1)),
      ("diagWeakWriteBERDelta", dict(base_spc_id = 7, weak_spc_id = 8)),
   )

   MQM_OTFDataCollection = (
      ("diagInit", dict(Version = 'OTF Data Collection 2011-09-23', OK_Errors = ['3160080', '3160083', '3160084', '3160100', '401009B'], Ignore_Errors = ['4030086', '4030087', '4030088', '4090081'], perRWERR_TypeLimit = 99)),
      ("collectOTFData", dict(DataPattern = 0xCAFEBABE, ber_spc_id = 9, failSafe = 1,)),
   )
else:
   MQM_WeakWrite = (
      ("diagInit", dict(Version = 'Sentosa Weak Write 2010-05-03', OK_Errors = ['3160080', '3160083', '3160084', '3160100', '401009B'], Ignore_Errors = ['4030086', '4030087', '4030088', '4090081'], perRWERR_TypeLimit = 99)),
      ("diagWeakWriteScreen", dict(DataPattern = 0xCAFEBABE, ber_spc_id = 8, spinDownDwell = 60, weakWriteModes = ({'mode':'ID','numTracksToOffset':-10}, {'mode':'OD','numTracksToOffset':10},), failSafe = 1)),
      ("diagRandomWrite", dict(numMinutes = 30, DataPattern = 0x22222222, ber_spc_id = 3)),
      ("diagWeakWriteScreen", dict(DataPattern = 0xBEEFCAFE, ber_spc_id = 7, spinDownDwell = 0, weakWriteModes = ({'mode':'ID','numTracksToOffset':-10}, {'mode':'OD','numTracksToOffset':10},), failSafe = 1)),
      ("diagWeakWriteBERDelta", dict(base_spc_id = 7, weak_spc_id = 8)),
   )

   MQM_OTFDataCollection = (
      ("diagInit", dict(Version = 'OTF Data Collection 2011-09-23', OK_Errors = ['3160080', '3160083', '3160084', '3160100', '401009B'], Ignore_Errors = ['4030086', '4030087', '4030088', '4090081'], perRWERR_TypeLimit = 99)),
      ("collectOTFData", dict(DataPattern = 0xCAFEBABE, ber_spc_id = 9, failSafe = 1,)),
   )

MQM_RandomWrites = (
   ("diagInit", dict(Version = '15 Minute Random Write Zeros, 20k Block Size', OK_Errors = [], Ignore_Errors = ['4030086', '4030087', '4030088', '4090081'], perRWERR_TypeLimit = 0, printResult = False)),
   ("diagRandomWrite", dict(numMinutes = 15, DataPattern = 0, ber_spc_id = 14, berByHead = True, sectorCount = 20000, altBadSectors = 0)),
)
MQM_WriteByZoneRangeSEQ = (

   ("diagRWZoneRangeSEQ", dict( mode = 'W', CylRange = {'mode':'zonetozone'}, zoneRange = [8,15])),

)


MQM_WriteByZoneRangeRND = (

   ("diagRWZoneRangeRND", dict( mode = 'W', CylRange = {'mode':'zonetozone'}, zoneRange = [8,15])),

)
MQM_FullPackWrite = (
   ("diagInit", dict(Version = 'Full pack wrt', OK_Errors = [], Ignore_Errors = ['4030086', '4030087', '4030088', '4090081'], perRWERR_TypeLimit = 0, printResult = False)),
   ("diagFullPackWrite", dict( SMThresh = None)),

)


##################### ReadWrite #####################################

## Encroached Write
EncroachedCmdTimeout = 14400 * numHeads # 240 min/head for a read or write pack
encroachedWriteScreen_Params = {
   'spc_id'                      : 20,
   'WRITE_RETRIES'               : '6,5,64',
   'READ_RETRIES'                : '6,5,A',
   'WRITE_LOOPS'                 : 1,
   'MAX_FLAWS'                   : 9998,
   'WINDOW_RANGE'                : None,
   'MAX_DEFECTS_WINDOW'          : None,
   'BIE_THRESH'                  : 0xA0,
   'ITER_CNT'                    : 0x20,
   'ITER_LOAD'                   : 0x00,
   'RWERRS_TO_FILTER'            : [ '4090080',
                                     '4090081',
                                     '4090082',
                                     '4090083',
                                     '4090084',
                                     '4090085',
                                     '4090086',
                                     '4090087'],
   }

setupBIEThresh_Params = {
   "memCmds"                     : [(0x8001, 0x40EA, 0x0D00,)], # Halt formatter on a difficult to read sector
   "regCmds" : [
      (0x0490, 0x04C4,),                   # MET_SEL1-#bits in Error, MET_SEL0-#bits in Error, OR operation
      (0x0491, 0x01E0,),                   # ignore all status except code convergence
   ],
   "bieThreshRegisters"          : (0x0492, 0x0493,), # Bits in Error Threshold
   "iterLoadRegisters"           : (0x0420,),         # BIE_ITER_LOAD, 0 does not effect RAW BER
}

disableBIEDetector_Params = {
   "memCmds"                     : [(0x8001, 0x40EA, 0x0F00,)],
   "regCmds" : [
   ],
   "regsToDisp"                  : (0x0490, 0x0491, 0x0492, 0x0493, 0x0420,),
}
## End Encroached Write

formatIteration = '4F'

formatOptions = {
   'spc_id'                   : 1,
   'OverallTimeout'           : 8 * 3600 * numHeads * 1.2,
   'formatTimeout'            : 8 * 3600 * numHeads,
   'formatType'               : 'Initial Format Pass',
   'forceFormat'              : 1,
   'noPowerCycle'             : 0,
   'msdScreens'               : [],
   'dumpDefectLists'          : 0,
   'otfScreen'                : 0,
   'nonResidentFlawLimit'     : None,     # Limit applied to 'non-resident' G-List following format
   'collectBERdata'           : 1,
   'skipGListCheck'           : 1,

   'NumDefectsBeforeSkippingTrack' : 0x32,

   # Paramter 1 bits:
   'DisableTrackRewrite'      : 1,        # Bit 7 : Disable Track Rewrite
   'DisableDataSyncRewrites'  : 0,        # Bit 6: Disable Track Re-write for Data Sync Time-out Errors.
   'SeaCOSFormat'             : 0,        # Bit 5: Enable SeaCOS XF Space Format.
   'SkipReFormat'             : 0,        # Bit 4: Enable Zone Re-format Skipping.
   'EnableLogging'            : 1,        # Bit 3: Enable Event-based Format Logging. (Verbose Mode)
   'DisableCertify'           : 0,        # Bit 2: Disable User Partition Certify. (No read pass)
   'DisableWritePass'         : 0,        # Bit 1: Disable User Partition Format. (Quick Format)
   'CorruptPrimaryDefects'    : 1,        # Bit 0: Corrupt User Partition Primary Defects.

   'DefectListOptions'        : 3,        # Bit 2: Process Active Log,.Bit 1: Process Primary Lists,.Bit 0: Process Grown Defect Lists.
   'MaxWriteRetryCount'       : 0x15,       # Maximum write retries to be applied to an LBA during format
   'MaxReadRetryCnt'          : 10,        # Maximum LBA certification count/ read retries
   'MaxIterationCount'        : testSwitch.DO_BIE_IN_FMT and 0x3A or 5 and 0x45,       # Max iteration count applied during format
   'CertReWriteThresh'        : None, # Track Rewrite During Certify Retry Threshold.

   'BIE_THRESH'               : testSwitch.DO_BIE_IN_FMT and 0xA0 or False,
   'ITER_CNT'                 : 0x3A,
   'ITER_LOAD'                : 0x00,
   'RETRIES'                  : '6,5,64',

   'ifFailDoDisplayG'         : 1,
   'MaxWriteRetryCount2'      : 0x15,       # Maximum secondary  Write Retry Count
   'MaxReadRetryCount2'       : 0xa,        # Maximum secondary  Read Retry Count
   'TLevel2'                  : 0x45,       # Maximum secondary  ECC T-Level
   'BoxPaddingHeight'         : 0x0505,     # Specifies box padding height. Bits[15:8] defines upper height value and Bits[7:0] defines lower height value
   'BoxPaddingWidth'          : 0x0202,     # Specifies box padding width. Bits[15:8] defines left width value and Bits[7:0] defines right width value
   }

if testSwitch.TRUNK_BRINGUP:
   formatOptions['OverallTimeout'] =  4 * 3600 * numHeads * 1.2
   formatOptions['formatTimeout']  = 4 * 3600 * numHeads

formatOptions2 = {
   'spc_id'                   : 1,
   'OverallTimeout'           : 108000,
   'formatTimeout'            : 600 + 300*numHeads,
   'formatType'               : 'Re-Format - If GList Entries',
   'forceFormat'              : 0,
   'noPowerCycle'             : 0,
   'msdScreens'               : [],
   'dumpDefectLists'          : 0,
   'otfScreen'                : 0,
   'nonResidentFlawLimit'     : None,     # Limit applied to 'non-resident' G-List following format
   'collectBERdata'           : 1,

   'NumDefectsBeforeSkippingTrack' : 0x0004,

   'DisableDataSyncRewrites'  : 1,        # Bit 6: Disable Track Re-write for Data Sync Time-out Errors.
   'SeaCOSFormat'             : 0,        # Bit 5: Enable SeaCOS XF Space Format.
   'SkipReFormat'             : 0,        # Bit 4: Enable Zone Re-format Skipping.
   'EnableLogging'            : 0,        # Bit 3: Enable Event-based Format Logging. (Verbose Mode)
   'DisableCertify'           : 0,        # Bit 2: Disable User Partition Certify. (No read pass)
   'DisableWritePass'         : 0,        # Bit 1: Disable User Partition Format. (Quick Format)
   'CorruptPrimaryDefects'    : 1,        # Bit 0: Corrupt User Partition Primary Defects.

   'DefectListOptions'        : 2,        # Bit 2: Process Active Log,.Bit 1: Process Primary Lists,.Bit 0: Process Grown Defect Lists.
   'MaxWriteRetryCount'       : 100,      # Maximum write retries to be applied to an LBA during format
   'MaxReadRetryCnt'          : 5,        # Maximum LBA certification count/ read retries
   'MaxIterationCount'        : testSwitch.DO_BIE_IN_FMT and 0x3A or 12,       # Max iteration count applied during format
   'CertReWriteThresh'        : 100 * numHeads, # Track Rewrite During Certify Retry Threshold.

   'BIE_THRESH'               : testSwitch.DO_BIE_IN_FMT and 0xA0 or False,
   'ITER_CNT'                 : 0x3A,
   'ITER_LOAD'                : 0x00,
   'RETRIES'                  : '6,5,64',

   'ifFailDoDisplayG'         : 1,
   }

if testSwitch.encroachedWriteScreen:
   formatOptions2['forceFormat']         = 1
   formatOptions2['MaxWriteRetryCount']  = 0xA

if testSwitch.TRUNK_BRINGUP:
   formatOptions2['OverallTimeout'] =  54000

if testSwitch.SINGLEPASSFLAWSCAN:
   packWriteFormat = {            # Unconditional Write Only Format
      'spc_id'                   : 1,
      'OverallTimeout'           : 8 * 3600 * numHeads * 1.2, #108000,
      'formatTimeout'            : 8 * 3600 * numHeads, #600 + 300*numHeads,
      'formatType'               : 'Forced Write Only Format pass (aka Pack Write)',
      'forceFormat'              : 1,
      'noPowerCycle'             : 0,
      'msdScreens'               : [],
      'dumpDefectLists'          : 0,
      'skipGListCheck'           : 1,
      'otfScreen'                : 0,
      'nonResidentFlawLimit'     : None,     # Limit applied to 'non-resident' G-List following format
      'collectBERdata'           : 1,

      'DisableDataSyncRewrites'  : 0,        # Bit 6: Disable Track Re-write for Data Sync Time-out Errors.
      'SeaCOSFormat'             : 0,        # Bit 5: Enable SeaCOS XF Space Format.
      'SkipReFormat'             : 0,        # Bit 4: Enable Zone Re-format Skipping.
      'EnableLogging'            : 0,        # Bit 3: Enable Event-based Format Logging. (Verbose Mode)
      'DisableCertify'           : 0,        # Bit 2: Disable User Partition Certify. (No read pass)
      'DisableWritePass'         : 0,        # Bit 1: Disable User Partition Format. (Quick Format)
      'CorruptPrimaryDefects'    : 0,        # Bit 0: Corrupt User Partition Primary Defects.

      'DefectListOptions'        : None,     # Bit 2: Process Active Log,.Bit 1: Process Primary Lists,.Bit 0: Process Grown Defect Lists.
      'MaxWriteRetryCount'       : 0x20,     # Maximum write retries to be applied to an LBA during format
      'MaxReadRetryCnt'          : None,     # Maximum LBA certification count/ read retries
      'MaxIterationCount'        : None,     # Max iteration count applied during format
      'CertReWriteThresh'        : None,     # Track Rewrite During Certify Retry Threshold.

      'BIE_THRESH'               : testSwitch.DO_BIE_IN_FMT and 0xA0 or False,
      'ITER_CNT'                 : 0x3A,
      'ITER_LOAD'                : 0x00,
      'RETRIES'                  : '6,5,64',

      'ifFailDoDisplayG'         : 0,
      }

formatOptionsChkMrgG = {
   'DisableDataSyncRewrites'  : 0,        # Bit 6: Disable Track Re-write for Data Sync Time-out Errors.
   'SeaCOSFormat'             : 0,        # Bit 5: Enable SeaCOS XF Space Format.
   'SkipReFormat'             : 0,        # Bit 4: Enable Zone Re-format Skipping.
   'EnableLogging'            : 0,        # Bit 3: Enable Event-based Format Logging. (Verbose Mode)
   'DisableCertify'           : 1,        # Bit 2: Disable User Partition Certify. (No read pass)
   'DisableWritePass'         : 0,        # Bit 1: Disable User Partition Format. (Quick Format)
   'CorruptPrimaryDefects'    : 0,        # Bit 0: Corrupt User Partition Primary Defects.
   'MaxWriteRetryCount'       : 64,       # Maximum write retries to be applied to an LBA during format
   'MaxIterationCount'        : testSwitch.DO_BIE_IN_FMT and 0x3A or 5,       # Max iteration count applied during format

   'BIE_THRESH'               : testSwitch.DO_BIE_IN_FMT and 0xA0 or False,
   'ITER_CNT'                 : 0x3A,
   'ITER_LOAD'                : 0x00,
   'RETRIES'                  : '6,5,64',
   }
##################### Opti #####################################

ZONE_POS = 198             # Equal to 99 % of zone
MaxIteration  = {
      'ATTRIBUTE'       : 'FE_0118663_357416_CALCULATE_MAX_LDPC_ITERATIONS',
      'DEFAULT'         : 0,
      1                 : 0xFFFF,
      0                 : 255,
}

IC=0                      # set new variable
TrainOpts=2               # set new variable
TrainOpts_2=0x82
OPTIZAP_TRACK_LIMIT = 0x061E  # ZAP Range [test cyl + lower byte, test cyl - Upper Byte]

OAR_TEST_ZONE = {
   "EQUATION"     : '[TP.UMP_ZONE[self.dut.numZones][0]]',
}

minizap_zone_OAR_ELT_SMR = {
   'ATTRIBUTE'  : 'SMR',
   'DEFAULT'    : 0,
   0            : [],
   1            : {
      'ATTRIBUTE'          : 'nextState',
      'DEFAULT'            : 'NORMAL',
      'NORMAL'             : [],
      'OPTIZAP_2'          : OAR_TEST_ZONE,
   },
}

T250_OAR_Screen_Spec = {
   ('P250_SEGMENT_BER_SUM2', 'match')      : {
      'spc_id'       : 22, # default is all table available
      # 'row_sort'     : 'HD_LGC_PSN', # default is HD_LGC_PSN if omitted
      'col_sort'     : 'DATA_ZONE', # default is DATA_ZONE if omitted
      'col_range'    : (1,4), # default is any, no filtering
      'column'       : ('DELTA_ALIGNED_BER'),
      'compare'      : (         '>'),
      'criteria'     : (          1.0 ),
      #'fail_count'   : 1, # this is must have for count type
   },
   ('P250_SEGMENT_BER_SUM2', 'count')      : {
      'spc_id'       : 23, # default is all table available
      # 'row_sort'     : 'HD_LGC_PSN', # default is HD_LGC_PSN if omitted
      'col_sort'     : 'DATA_ZONE', # default is DATA_ZONE if omitted
      'col_range'    : (1,4), # default is any, no filtering
      'column'       : ('DELTA_ALIGNED_BER'),
      'compare'      : (         '>'),
      'criteria'     : (          1.0 ),
      'fail_count'   : 1, # this is must have for count type
   },
   ('Fail_Cnt','')      : 1, # default is fail all criteria to constitute screening failed
   ('Title','')         : 'T250_OAR_Screen_Spec',
}

T250_OAR_Screen_Spec_ID = { # Screen reli failure with ID warping issue in 2D
   'ATTRIBUTE'    : 'IS_2D_DRV',
   'DEFAULT'      : 0,
   0 : {}, # Disable for 1D Only at the moment
   1 : { 
      ('P250_SEGMENT_BER_SUM2', 'count')      : {
           'spc_id'       : 22, # No Squeeze OAR
           'col_sort'     : 'DATA_ZONE', 
           'col_range'    : (149,), 
           'column'       : ('DELTA_ALIGNED_BER', 'WORST_ALIGNED_BER'),
           'compare'      : (                '>',                 '>'),
           'criteria'     : (                0.5,                -2.3),
           'fail_count'   : 1, 
      },
      ('Fail_Cnt','')         : 1, # default is fail all criteria to constitute screening failed
      ('Title','')            : 'T250_OAR_Screen_Spec_ID',
   },
}
# if (testSwitch.TRUNK_BRINGUP or testSwitch.ROSEWOOD7): #trunk code some register is different
if testSwitch.MARVELL_SRC:
   if testSwitch.ENABLE_TARGET_TUNING_T251:
     if not testSwitch.UPS_PARAMETERS:
        simple_OptiPrm_251={
           'test_num'              : 251,
           'prm_name'              : 'simple_OptiPrm_251',
           'timeout'               : 3600 * numHeads,
           'spc_id'                : 1,
           'BIT_MASK'              : (0, 512),
           'BIT_MASK_EXT'          : (0, 0),   # All bits are set by default in SF3, thus need to specify zero if the rest of the zones are not required.
           'CWORD2'                : 0x200,
           'CWORD1'                : 0x4e,  # Opti every zone requested, Disable ZLR, Update RAP/SAP to RAM only (Do not save to flash) Enable ber in between
           'ZONE_POSITION'         : ZONE_POS,
           'REG_TO_OPT1': (0, 0, 0, 1),        # BER Data Point
           'REG_TO_OPT1_EXT': (0, 0x0, 0x1040),

           'REG_TO_OPT2'     : (0x11, 0xFFF0, 0xF, 1),    # Asymmetry
           'REG_TO_OPT2_EXT' : (0, 3, 0x1440),  # DHD 3 training reads, Regression, Force Full Rng, FIR init to center, BER Opti, VGAR, NLD, FIR, filtering option.

           'REG_TO_OPT3'     : (0x24, 0, 15, 1),    # CTF / Bandwidth
           'REG_TO_OPT3_EXT' : (0, 3, 0x9440),  #

           'REG_TO_OPT4'     : (0x25, 5, 50, 5),    # BST
           'REG_TO_OPT4_EXT' : (0, 3, 0x9440),  #

           'REG_TO_OPT5'     : (0x33, 50, -10, 3),   # FIR Tap 3  was (0x33, 100, -100, 5)
           'REG_TO_OPT5_EXT' : (0, 3, 0x1440),  # 3 training reads, disabled Regression, Force Full Rng, FIR init to center, BER Opti, VGAR, NLD, FIR, filtering option.

           'REG_TO_OPT7'    : (0x450, 0, 22, 2), # 001-101 (Adaptive reference)
           'REG_TO_OPT7_EXT': (0, 3, 0x9442), # DHD 3 training reads, Regression, Force Full Rng, set 0x1000 bit to disable FIR and NPML init, BER Opti, VGAR, NLD, FIR, filtering option, Re-write data.

           'REG_TO_OPT8'     : (0x113, 0, 22, 2),  # 101
           'REG_TO_OPT8_EXT' : (0, 3, 0x9442),  # DHD 3 training reads, Regression, Force Full Rng, set 0x1000 bit to disable FIR and NPML init, BER Opti, VGAR, NLD, FIR, filtering option, Re-write data.

           'REG_TO_OPT9'     : (0x112, 0, 22, 2),  # 011
           'REG_TO_OPT9_EXT' : (0, 3, 0x9442),  # DHD 3 training reads, Regression, Force Full Rng, set 0x1000 bit to disable FIR and NPML init, BER Opti, VGAR, NLD, FIR, filtering option, Re-write data.

           'REG_TO_OPT10'    : (0x114, 0, 22, 2), # 111
           'REG_TO_OPT10_EXT': (0, 3, 0x9442), # DHD 3 training reads, Regression, Force Full Rng, set 0x1000 bit to disable FIR and NPML init, BER Opti, VGAR, NLD, FIR, filtering option, Re-write data.

           'REG_TO_OPT11'     : (245, 0, 0, 4),    # NPT subprocess
           'REG_TO_OPT11_EXT' : (0, 0, 0x6000),  #

           #'REG_TO_OPT12'     : (0x11, 0xFFF0, 0xF, 2),    # Asymmetry
           #'REG_TO_OPT12_EXT' : (0, 3, 0x9440),  # DHD 3 training reads, Regression, Force Full Rng, FIR init to center, BER Opti, VGAR, NLD, FIR, filtering option.

           'REG_TO_OPT13'     : (0x24, 0, 15, 1),    # CTF / Bandwidth
           'REG_TO_OPT13_EXT' : (0, 3, 0x9440),  #
                                                 #
           'REG_TO_OPT14'     : (0x25, 5, 50, 5),    # BST
           'REG_TO_OPT14_EXT' : (0, 3, 0x9440),  #
                                                 #
           'REG_TO_OPT15'     : (0x33, 50, -10, 3),   # FIR Tap 3  was (0x33, 100, -100, 5)
           'REG_TO_OPT15_EXT' : (0, 3, 0x3440),  # 3 training reads, disabled Regression, Forse Full Rng, set 0x1000 bit to disable FIR and NPML init, BER Opti, VGAR, NLD, FIR, filtering option.

           'REG_TO_OPT16': (0, 0, 0, 1),        # BER Data Point,save FIR
           'REG_TO_OPT16_EXT': (0, 3, 0x1044),

           'REG_TO_OPT17': (0, 0, 0, 1),        # BER Data Point
           'REG_TO_OPT17_EXT': (0, 0x10, 0x1074),

           'RESULTS_RETURNED'      : 0x0007,
           'SET_OCLIM'             : 819,
           'NUM_READS'             : 2,
           'LOG10_BER_SPEC'        : 350, # Margin range: -4.5 to -3.25
           'DELTA_LIMIT'           : 100,
           #'NUM_ITER_READS'        : 5, # was 50; Marvell take out temporily
           'TLEVEL'                : MaxIteration,
           'VGA_MIN'               : 128,
           'GAIN'                  :  0,       # non linear update gain
           #'NOMRF_REF_VALUE'       :  50,      # NOMRF reference value (only take effect when sweeping LATE1/LATE0/LATE2)
           'NUM_SQZ_WRITES'        :  0,       # number of ati write
           'SQZ_OFFSET'            :  0,       # squeeze offset in tics
           'THRESHOLD2'            :  1,
           'ADAPTIVES'             :  6,
           'REVS'                  :  50,     # maximum revs if converge not meet
           'MIN_DELTA'             :  3,      # delta sova 0.003, consider converge, if also meet MIN_REVS, exit out
           'MIN_REVS'              :  5,      # since ber measurement will use 2 revs each, the minimum revs will double

       }
        if testSwitch.FE_0298712_403980_PRECODER_IN_T251 and not testSwitch.FE_0311911_403980_P_PRECODER_IN_READ_OPTI_ONLY:
           simple_OptiPrm_251['REG_TO_OPT18']=(0x613C, 0, 4, 1)
           simple_OptiPrm_251['REG_TO_OPT18_EXT']=(0, 3, 0x1C42)
           #extern test switch cannot be used here. Thus, the following parameters are set in SerialTest.py & Opti_Read.py.
           #simple_OptiPrm_251['PRECODER0']=(0x0713, 0x4652)
           #simple_OptiPrm_251['PRECODER1']=(0x0713, 0x4625)
           #simple_OptiPrm_251['PRECODER2']=(0x0145, 0x7362)
           #simple_OptiPrm_251['PRECODER3']=(0x0142, 0x7365)
           #simple_OptiPrm_251['PRECODER4']=(0x7654, 0x3210)
     else: #UPS
         # need to review SF3 code margin system input, LOG10_BER_SPEC not supported.DELTA_LIMIT not support
         # NRB read auto adjust scheme not in adapt code also. "MIN_DELTA", "MIN_REVS" not in
         simple_OptiPrm_251={
            'test_num'              : 251,
            'prm_name'              : 'simple_OptiPrm_251',
            'timeout'               : 3600 * numHeads,
            'spc_id'                : 1,
            'ZnMsk'                 : (0,0,0,512),# need to change back SF3, there is no zone bank
            'Cwrd2'                 : 0x200,
            'Cwrd1'                 :  0x4e, # Opti every zone requested, Disable ZLR, Update RAP/SAP to RAM only (Do not save to flash) Enable ber in between
            'ZnPsn'                 : ZONE_POS,
            'Reg'                   : (0,        0,        0,        1,        0,        0,   0x1040,        0, #BER points
                                    0x11,   0xFFF0,      0xF,        1,        0,        3,   0x1440,        0, #Asymmetry,DHD 3 training reads, Regression, Force Full Rng, FIR init to center, BER Opti, VGAR, NLD, FIR, filtering option.
                                    0x24,        0,      0xF,        1,        0,        3,   0x9440,        0, #CTF / Bandwidth       
                                    0x25,        5,       50,        5,        0,        3,   0x9440,        0, #BST    
                                    0x33,       50,      -10,        3,        0,        3,   0x1440,        0, #FIR tap3 ,# 3 training reads, disabled Regression, Force Full Rng, FIR init to center, BER Opti, VGAR, NLD, FIR, filtering option.   
                                   0x450,        0,       22,        2,        0,        3,   0x9442,        0, #001-101 (Adaptive reference),DHD 3 training reads, Regression, Force Full Rng, set 0x1000 bit to disable FIR and NPML init, BER Opti, VGAR, NLD, FIR, filtering option, Re-write data.
                                   0x113,        0,       22,        2,        0,        3,   0x9442,        0, #101, DHD 3 training reads, Regression, Force Full Rng, set 0x1000 bit to disable FIR and NPML init, BER Opti, VGAR, NLD, FIR, filtering option, Re-write data.
                                   0x112,        0,       22,        2,        0,        3,   0x9442,        0, #011, # DHD 3 training reads, Regression, Force Full Rng, set 0x1000 bit to disable FIR and NPML init, BER Opti, VGAR, NLD, FIR, filtering option, Re-write data.                                                                                      
                                   0x114,        0,       22,        2,        0,        3,   0x9442,        0, #111, # DHD 3 training reads, Regression, Force Full Rng, set 0x1000 bit to disable FIR and NPML init, BER Opti, VGAR, NLD, FIR, filtering option, Re-write data.
                                   0x245,        0,        0,        4,        0,        0,   0x6000,        0, #NPT subprocess                                                                    
                                    0x24,        0,      0xF,        1,        0,        3,   0x9440,        0, #CTF/Bandwidth  
                                    0x25,        5,       50,        5,        0,        3,   0x9440,        0, #BST
                                    0x33,       50,      -10,        3,        0,        3,   0x3440,        0, #FIR tap 3, 3 training reads, disabled Regression, Forse Full Rng, set 0x1000 bit to disable FIR and NPML init, BER Opti, VGAR, NLD, FIR, filtering option.                                                                               
                                       0,        0,        0,        1,        0,        3,   0x1044,        0, # BER Data Point,not save FIR       
                                       0,        0,        0,        1,        0,     0x10,   0x1074,        0),# BER Data Point,saving FIR    


            'RprtOptn'              :   7,
            'Oclim'                 : 819, 
            'RdCnt'                 : 2,
            'Tlvl'                  : MaxIteration,
            'VgaMn  '               : 128,
            'Gain'                  :  0,       # non linear update gain
            'SqzWrCnt'              :  0,       # number of ati write
            'SqzOfst'               :  0,       # squeeze offset in tics
            'WrRef'                 :  6,       # reference write precmp value 
            'Rvs'                   :  50,      # maximum revs if converge not meet
            'ThrshCqm'              :  1 ,      # pTestTrkPrepOpts->fitness_thld
           # 'MIN_DELTA'             :  3,      # not in adapt code. delta sova 0.003, consider converge, if also meet MIN_REVS, exit out
           # 'MIN_REVS'              :  5,      # not in adapt code. since ber measurement will use 2 revs each, the minimum revs will double

        }
         # below not yet be supported for UPS
         if testSwitch.FE_0298712_403980_PRECODER_IN_T251 and not testSwitch.FE_0311911_403980_P_PRECODER_IN_READ_OPTI_ONLY:
            simple_OptiPrm_251['REG_TO_OPT18']=(0x613C, 0, 4, 1)
            simple_OptiPrm_251['REG_TO_OPT18_EXT']=(0, 3, 0x1C42)

   else:# no target
     if not testSwitch.UPS_PARAMETERS:
        simple_OptiPrm_251={
             'test_num'              : 251,
             'prm_name'              : 'simple_OptiPrm_251',
             'timeout'               : 12000 * numHeads,
             'spc_id'                : 1,
             'BIT_MASK'              : (0, 512),
             'BIT_MASK_EXT'          : (0, 0),   # All bits are set by default in SF3, thus need to specify zero if the rest of the zones are not required.
             'CWORD2'                : 0x200,
             'CWORD1'                : 0x4e,  # Opti every zone requested, Disable ZLR, Update RAP/SAP to RAM only (Do not save to flash) Enable ber in between
             'ZONE_POSITION'         : ZONE_POS,
             'REG_TO_OPT1': (0, 0, 0, 1),        # BER Data Point
             'REG_TO_OPT1_EXT': (0, 0x0, 0x1040),

             'REG_TO_OPT2'     : (0x11, 0xFFF0, 0xF, 2),    # Asymmetry
             'REG_TO_OPT2_EXT' : (0, 3, 0x9440),  # DHD 3 training reads, Regression, Force Full Rng, FIR init to center, BER Opti, VGAR, NLD, FIR, filtering option.

             'REG_TO_OPT3'     : (0x24, 0, 15, 1),    # CTF / Bandwidth
             'REG_TO_OPT3_EXT' : (0, 3, 0x9440),  #

             'REG_TO_OPT4'     : (0x25, 5, 50, 5),    # BST
             'REG_TO_OPT4_EXT' : (0, 3, 0x9440),  #

             'REG_TO_OPT5'     : (0x33, 50, -10, 3),   # FIR Tap 3  was (0x33, 100, -100, 5)
             'REG_TO_OPT5_EXT' : (0, 3, 0x1440),  # 3 training reads, disabled Regression, Force Full Rng, FIR init to center, BER Opti, VGAR, NLD, FIR, filtering option.

             'REG_TO_OPT6'     : (0x34, 70, 120, 4),   # FIR Tap 4 was (0x34, 100, -100, 5)
             'REG_TO_OPT6_EXT' : (0, 3, 0x1440),  # 3 training reads, disabled Regression, Force Full Rng, FIR init to center, BER Opti, VGAR, NLD, FIR, filtering option.

             'REG_TO_OPT7'    : (0x450, 0, 22, 2), # 001-101 (Adaptive reference)
             'REG_TO_OPT7_EXT': (0, 3, 0x9442), # DHD 3 training reads, Regression, Force Full Rng, set 0x1000 bit to disable FIR and NPML init, BER Opti, VGAR, NLD, FIR, filtering option, Re-write data.

             'REG_TO_OPT8'     : (0x113, 0, 22, 2),  # 101
             'REG_TO_OPT8_EXT' : (0, 3, 0x9442),  # DHD 3 training reads, Regression, Force Full Rng, set 0x1000 bit to disable FIR and NPML init, BER Opti, VGAR, NLD, FIR, filtering option, Re-write data.

             'REG_TO_OPT9'     : (0x112, 0, 22, 2),  # 011
             'REG_TO_OPT9_EXT' : (0, 3, 0x9442),  # DHD 3 training reads, Regression, Force Full Rng, set 0x1000 bit to disable FIR and NPML init, BER Opti, VGAR, NLD, FIR, filtering option, Re-write data.

             'REG_TO_OPT10'    : (0x114, 0, 22, 2), # 111
             'REG_TO_OPT10_EXT': (0, 3, 0x9442), # DHD 3 training reads, Regression, Force Full Rng, set 0x1000 bit to disable FIR and NPML init, BER Opti, VGAR, NLD, FIR, filtering option, Re-write data.

             'REG_TO_OPT12'     : (0x24, 0, 15, 1),    # CTF / Bandwidth
             'REG_TO_OPT12_EXT' : (0, 3, 0x9440),  #

             'REG_TO_OPT13'     : (0x25, 5, 50, 5),    # BST
             'REG_TO_OPT13_EXT' : (0, 3, 0x9440),  #

             'REG_TO_OPT14'     : (0x33, 50, -10, 3),   # FIR Tap 3  was (0x33, 100, -100, 5)
             'REG_TO_OPT14_EXT' : (0, 3, 0x1440),  # 3 training reads, disabled Regression, Forse Full Rng, set 0x1000 bit to disable FIR and NPML init, BER Opti, VGAR, NLD, FIR, filtering option.

             'REG_TO_OPT15'     : (0x34, 70, 120, 4), # FIR Tap 4 was (0x34, 100, -100, 5) was 60, 120, 5 25APR2012
             'REG_TO_OPT15_EXT' : (0, 3, 0x1444),  # 3 training reads, disabled Regression, Force Full Rng, set 0x1000 bit to disable FIR and NPML init, BER Opti, VGAR, NLD, FIR, filtering option,save FIR

             'REG_TO_OPT16'     : (0, 0, 0, 1),        # BER Data Point
             'REG_TO_OPT16_EXT' : (0, 10, 0x1074),   # save all adaptive parameter: FIR,NLD,NRB..

             'RESULTS_RETURNED'      : 0x0007,
             'SET_OCLIM'             : 819,
             'NUM_READS'             : 2,
             'LOG10_BER_SPEC'        : 350, # Margin range: -4.5 to -3.25
             'DELTA_LIMIT'           : 100,
             #'NUM_ITER_READS'        : 5, # was 50; Marvell take out temporily
             'TLEVEL'                : MaxIteration,
             'VGA_MIN'               : 128,
             'GAIN'                  :  0,       # non linear update gain
             #'NOMRF_REF_VALUE'       :  50,      # NOMRF reference value (only take effect when sweeping LATE1/LATE0/LATE2)
             'NUM_SQZ_WRITES'        :  0,       # number of ati write
             'SQZ_OFFSET'            :  0,       # squeeze offset in tics
             'THRESHOLD2'            :  1,
             'ADAPTIVES'             :  6,
             'REVS'                  :  50,     # maximum revs if converge not meet
             'MIN_DELTA'             :  3,      # delta sova 0.003, consider converge, if also meet MIN_REVS, exit out
             'MIN_REVS'              :  5,      # since ber measurement will use 2 revs each, the minimum revs will double
        }
        if testSwitch.FE_0298712_403980_PRECODER_IN_T251 and not testSwitch.FE_0311911_403980_P_PRECODER_IN_READ_OPTI_ONLY:
             simple_OptiPrm_251['REG_TO_OPT17']=(0x613C, 0, 4, 1)
             simple_OptiPrm_251['REG_TO_OPT17_EXT']=(0, 3, 0x1C42)
             #extern test switch cannot be used here. Thus, the following parameters are set in SerialTest.py & Opti_Read.py.
             #simple_OptiPrm_251['PRECODER0']=(0x0713, 0x4652)
             #simple_OptiPrm_251['PRECODER1']=(0x0713, 0x4625)
             #simple_OptiPrm_251['PRECODER2']=(0x0145, 0x7362)
             #simple_OptiPrm_251['PRECODER3']=(0x0142, 0x7365)
             #simple_OptiPrm_251['PRECODER4']=(0x7654, 0x3210)

     else:# USP support
         # need to review SF3 code margin system input, LOG10_BER_SPEC not supported.DELTA_LIMIT not support
         # NRB read auto adjust scheme not in adapt code also. "MIN_DELTA", "MIN_REVS" not in
        simple_OptiPrm_251={
           'test_num'              : 251,
           'prm_name'              : 'simple_OptiPrm_251',
           'timeout'               : 12000 * numHeads,
           'spc_id'                : 1,
           'ZnMsk'                 : (0,0,0,512),# need to change back SF3, there is no zone bank
           'Cwrd2'                 : 0x200,
           'Cwrd1'                 :  0x4e, # Opti every zone requested, Disable ZLR, Update RAP/SAP to RAM only (Do not save to flash) Enable ber in between
           'ZnPsn'                 : ZONE_POS,
           'Reg'                   : (0,        0,        0,        1,        0,        0,   0x1040,        0, #BER points
                                   0x11,   0xFFF0,      0xF,        2,        0,        3,   0x9440,        0, #Asymmetry,DHD 3 training reads, Regression, Force Full Rng, FIR init to center, BER Opti, VGAR, NLD, FIR, filtering option.
                                   0x24,        0,      0xF,        1,        0,        3,   0x9440,        0, #CTF / Bandwidth       
                                   0x25,        5,       50,        5,        0,        3,   0x9440,        0, #BST    
                                   0x33,       50,      -10,        3,        0,        3,   0x1440,        0, #FIR tap3 ,# 3 training reads, disabled Regression, Force Full Rng, FIR init to center, BER Opti, VGAR, NLD, FIR, filtering option.   
                                   0x34,       70,      120,        4,        0,        3,   0x1440,        0, #FIR tap4 ,# 3 training reads, disabled Regression, Force Full Rng, FIR init to center, BER Opti, VGAR, NLD, FIR, filtering option.   
                                  0x450,        0,       22,        2,        0,        3,   0x9442,        0, #001-101 (Adaptive reference),DHD 3 training reads, Regression, Force Full Rng, set 0x1000 bit to disable FIR and NPML init, BER Opti, VGAR, NLD, FIR, filtering option, Re-write data.
                                  0x113,        0,       22,        2,        0,        3,   0x9442,        0, #101, DHD 3 training reads, Regression, Force Full Rng, set 0x1000 bit to disable FIR and NPML init, BER Opti, VGAR, NLD, FIR, filtering option, Re-write data.
                                  0x112,        0,       22,        2,        0,        3,   0x9442,        0, #011, # DHD 3 training reads, Regression, Force Full Rng, set 0x1000 bit to disable FIR and NPML init, BER Opti, VGAR, NLD, FIR, filtering option, Re-write data.                                                                                      
                                  0x114,        0,       22,        2,        0,        3,   0x9442,        0, #111, # DHD 3 training reads, Regression, Force Full Rng, set 0x1000 bit to disable FIR and NPML init, BER Opti, VGAR, NLD, FIR, filtering option, Re-write data.
                                   0x24,        0,      0xF,        1,        0,        3,   0x9440,        0, #CTF/Bandwidth  
                                   0x25,        5,       50,        5,        0,        3,   0x9440,        0, #BST
                                   0x33,       50,      -10,        3,        0,        3,   0x1440,        0, #FIR tap 3, 3 training reads, disabled Regression, Forse Full Rng, set 0x1000 bit to disable FIR and NPML init, BER Opti, VGAR, NLD, FIR, filtering option.                                                                               
                                   0x34,       70,      120,        4,        0,        3,   0x1440,        0, #FIR tap 4, 3 training reads, disabled Regression, Forse Full Rng, set 0x1000 bit to disable FIR and NPML init, BER Opti, VGAR, NLD, FIR, filtering option.                                                                               
                                      0,        0,        0,        1,        0,     0x10,   0x1074,        0),# BER Data Point,saving FIR    
            'RprtOptn'              :   7,
            'Oclim'                 : 819, 
            'RdCnt'                 : 2,
            'Tlvl'                  : MaxIteration,
            'VgaMn  '               : 128,
            'Gain'                  :  0,       # non linear update gain
            'SqzWrCnt'              :  0,       # number of ati write
            'SqzOfst'               :  0,       # squeeze offset in tics
            'WrRef'                 :  6,       # reference write precmp value 
            'Rvs'                   :  50,      # maximum revs if converge not meet
            'ThrshCqm'              :  1 ,      # pTestTrkPrepOpts->fitness_thld
           # 'MIN_DELTA'             :  3,      # not in adapt code. delta sova 0.003, consider converge, if also meet MIN_REVS, exit out
           # 'MIN_REVS'              :  5,      # not in adapt code. since ber measurement will use 2 revs each, the minimum revs will double

        }
        # following not yet supported
        if testSwitch.FE_0298712_403980_PRECODER_IN_T251 and not testSwitch.FE_0311911_403980_P_PRECODER_IN_READ_OPTI_ONLY:
           simple_OptiPrm_251['REG_TO_OPT17']=(0x613C, 0, 4, 1)
           simple_OptiPrm_251['REG_TO_OPT17_EXT']=(0, 3, 0x1C42)
           #extern test switch cannot be used here. Thus, the following parameters are set in SerialTest.py & Opti_Read.py.
           #simple_OptiPrm_251['PRECODER0']=(0x0713, 0x4652)
           #simple_OptiPrm_251['PRECODER1']=(0x0713, 0x4625)
           #simple_OptiPrm_251['PRECODER2']=(0x0145, 0x7362)
           #simple_OptiPrm_251['PRECODER3']=(0x0142, 0x7365)
           #simple_OptiPrm_251['PRECODER4']=(0x7654, 0x3210)

   simple_OptiPrm_251_short_tune = simple_OptiPrm_251.copy() # default short sequence here, will revise
   simple_OptiPrm_251_short_tune_znAlign = simple_OptiPrm_251.copy() # default short sequence here, will revise

else:  #LSI
   simple_OptiPrm_251 = {
      'test_num'                 : 251,
      'prm_name'                 : 'simple_OptiPrm_251',
      'timeout'                  : 12000 * numHeads,
      'spc_id'                   : 1,
      'BIT_MASK'                 : (0, 512),
      'BIT_MASK_EXT'             : (0, 0), # All bits are set by default in SF3, thus need to specify zero if the rest of the zones are not required.
      'CWORD1'                   : 0x000A, # shingle write = default enable, disable is controlled by StateTable.py
      'ZONE_POSITION'            : ZONE_POS,
      'REG_TO_OPT1'              : (132, 0, 0, 1),      # VGA
      'REG_TO_OPT1_EXT'          : (0, 0x81, 0),
      'REG_TO_OPT2'              : (37, 5, 125, 5),     # ZFR
      'REG_TO_OPT2_EXT'          : (0x30, TrainOpts_2, 0x8C74),

      'REG_TO_OPT3'              : (146, 20, 60, 2),    # CTFFR,
      'REG_TO_OPT3_EXT'          : (0x30, TrainOpts_2, 0x8C75),

      'REG_TO_OPT4'              : (147, -120, 120, 10),    #NLTAP
      'REG_TO_OPT4_EXT'          : (0x38, TrainOpts_2, 0x8C74),  # 8 means it need to freeze non linear update gain to Gain value

      'REG_TO_OPT6'              : (0x38B, 0, 15, 1),    #MAINNPCAL2
      'REG_TO_OPT6_EXT'          : (0x30, TrainOpts_2, 0x8C74),

      'REG_TO_OPT8'              : (0x408, 0, 63, 2),    #LATE1
      'REG_TO_OPT8_EXT'          : (0x30, TrainOpts_2, 0x8C74),

      'REG_TO_OPT9'              : (155, 0, 63, 2),    #LATE02
      'REG_TO_OPT9_EXT'          : (0x30, TrainOpts_2, 0x8C74),

      'REG_TO_OPT10'             : (0x407, 0, 63, 2),    #LATE0
      'REG_TO_OPT10_EXT'         : (0x30, TrainOpts_2, 0x8C74),

      'REG_TO_OPT11'             : (0x409, 0, 63, 2),    #LATE2
      'REG_TO_OPT11_EXT'         : (0x30, TrainOpts_2, 0x8C74),

      'REG_TO_OPT12'             : (145, -96, 96, 16),  # TDTARG
      'REG_TO_OPT12_EXT'         : (0x30, TrainOpts_2, 0xC74),

      'REG_TO_OPT13'             : (37, 5, 125, 5),     # ZFR
      'REG_TO_OPT13_EXT'         : (0x30, TrainOpts_2, 0x8C74),

      'REG_TO_OPT14'             : (906, 80, 200, 8),     # BDF_TAPW8R
      'REG_TO_OPT14_EXT'         : (0x30, TrainOpts_2, 0x8C74),

      'REG_TO_OPT15'             : (867, 90, 127, 2),     # BDF_TARG_T1
      'REG_TO_OPT15_EXT'         : (0x30, TrainOpts_2, 0x8c74),

      'REG_TO_OPT16'             : (0x38C, 0, 15, 1),     # BENTHRESH
      'REG_TO_OPT16_EXT'         : (0x30, TrainOpts_2, 0x8c74),

      #'REG_TO_OPT17'             : (234, 1, 15, 1),     # VSCALE with ILC = 2 (3 iter), enable margin and screeze write
      #'REG_TO_OPT17_EXT'         : (0x0, 0x1081, 0x9C40), # was (0x0, 0x1381, 0x107C)

      #'REG_TO_OPT18'             : (257, 1, 15, 1),     # VSCALE_LLR with ILC = 2 (3 iter),update later
      #'REG_TO_OPT18_EXT'         : (0x0, 0x1081, 0x9C40), # was (0x0, 0x1381, 0x107C)

      'REG_TO_OPT19'             : (267, 1, 15, 1),     # VSCALE_BM2
      'REG_TO_OPT19_EXT'         : (0x0, 0x1081, 0x9C40),

      'REG_TO_OPT20'             : (258, 1, 15, 1),     #VSCALE_LLR2
      'REG_TO_OPT20_EXT'         : (0x0, 0x1081, 0x9C40),

      #'REG_TO_OPT21'             : (901, 1, 15, 1),     #VSCALE2
      #'REG_TO_OPT21_EXT'         : (0x0, 0x1081, 0x9C40),

      'REG_TO_OPT22'             : (0, 0, 0, 1),
      'REG_TO_OPT22_EXT'         : (0x0000, TrainOpts_2, 0x74),  #enable two stage adatption

      'RESULTS_RETURNED'         : { # 0x0007,
         'ATTRIBUTE'          : 'FE_0245014_470992_ZONE_MASK_BANK_SUPPORT',
         'DEFAULT'            : 0,
         0                    : 0x0007,
         1                    : 0x0000,
      },
      'SET_OCLIM'                : 819,
      'NUM_READS'                : 2,
      'LOG10_BER_SPEC'           : 350, # Margin range: -4.5 to -3.25
      'DELTA_LIMIT'              : 100,
      'NUM_ITER_READS'           : 5, # was 50
      'TLEVEL'                   : MaxIteration,
      'VGA_MIN'                  : {
         'ATTRIBUTE'          : 'nextState',
         'DEFAULT'            : 'ELSE',
         'INIT_SYS'           : 128,      # VGA MIN
         'ELSE'               : 128,},    # VGA MIN
      'GAIN'                     : 0,     # non linear update gain
      #'NOMRF_REF_VALUE'          :  50,  # NOMRF reference value (only take effect when sweeping LATE1/LATE0/LATE2)
      'NUM_SQZ_WRITES'           : 0,     # number of ati write
      'SQZ_OFFSET'               : 0,     # squeeze offset in tics
      'THRESHOLD2'               : 1,
   }


   simple_OptiPrm_251_short_tune =  {
      'test_num'                 : 251,
      'prm_name'                 : 'simple_OptiPrm_251_short_tune',
      'timeout'                  : 12000 * numHeads,
      'spc_id'                   : 1,
      'BIT_MASK'                 : (0, 512),
      'BIT_MASK_EXT'             : (0, 0), # All bits are set by default in SF3, thus need to specify zero if the rest of the zones are not required.
      'CWORD1'                   : 0x400A, #disable shingle write
      'ZONE_POSITION'            : ZONE_POS,
      'REG_TO_OPT1'              : (132, 0, 0, 1),      # VGA
      'REG_TO_OPT1_EXT'          : (0, 0x81, 0),

      'REG_TO_OPT2'              : (37, 5, 125, 5),     # ZFR
      'REG_TO_OPT2_EXT'          : (0x30, TrainOpts_2, 0x8C74),

      'REG_TO_OPT3'              : (146, 20, 60, 2),    # CTFFR,
      'REG_TO_OPT3_EXT'          : (0x30, TrainOpts_2, 0x8C75),

   #  'REG_TO_OPT5'               : (0x1B9, 0, 4, 1),    #DFIRSCALE
   #  'REG_TO_OPT5_EXT'           : (0x30, TrainOpts_2, 0x1C74),  # not in trunk yet

      'REG_TO_OPT9'              : (155, 0, 63, 2),    #LATE02
      'REG_TO_OPT9_EXT'          : (0x30, TrainOpts_2, 0x8C74),

      'REG_TO_OPT10'             : (0x407, 0, 63, 2),    #LATE0
      'REG_TO_OPT10_EXT'         : (0x30, TrainOpts_2, 0x8C74),

      'REG_TO_OPT11'             : (0x409, 0, 63, 2),    #LATE2
      'REG_TO_OPT11_EXT'         : (0x30, TrainOpts_2, 0x8C74),

      'REG_TO_OPT12'             : (146, 20, 60, 2),    # CTFFR,
      'REG_TO_OPT12_EXT'         : (0x30, TrainOpts_2, 0x8C75),

      'REG_TO_OPT13'             : (37, 5, 125, 5),     # ZFR
      'REG_TO_OPT13_EXT'         : (0x30, TrainOpts_2, 0x8C74),

      'REG_TO_OPT14'             : (145, -96, 96, 16),  # TDTARG
      'REG_TO_OPT14_EXT'         : (0x30, TrainOpts_2, 0xC74),

      'REG_TO_OPT15'             : (147, -120, 120, 10),    #NLTAP
      'REG_TO_OPT15_EXT'         : (0x38, TrainOpts_2, 0x8C74),  # 8 means it need to freeze non linear update gain to Gain value

      'REG_TO_OPT16'             : (906, 80, 200, 8),     # BDF_TAPW8R
      'REG_TO_OPT16_EXT'         : (0x30, TrainOpts_2, 0x8C74),

      'REG_TO_OPT17'             : (867, 90, 127, 2),     # BDF_TARG_T1
      'REG_TO_OPT17_EXT'         : (0x30, TrainOpts_2, 0x8c74),

      'REG_TO_OPT18'             : (0x38C, 0, 15, 1),     # BENTHRESH
      'REG_TO_OPT18_EXT'         : (0x30, TrainOpts_2, 0x8c74),

      #'REG_TO_OPT17'             : (234, 1, 15, 1),     # VSCALE with ILC = 2 (3 iter), enable margin and screeze write
      #'REG_TO_OPT17_EXT'         : (0x0, 0x1081, 0x9C40), # was (0x0, 0x1381, 0x107C)

      #'REG_TO_OPT18'             : (257, 1, 15, 1),     # VSCALE_LLR with ILC = 2 (3 iter),update later
      #'REG_TO_OPT18_EXT'         : (0x0, 0x1081, 0x9C40), # was (0x0, 0x1381, 0x107C)

      #'REG_TO_OPT21'             : (901, 1, 15, 1),     #VSCALE2
      #'REG_TO_OPT21_EXT'         : (0x0, 0x1081, 0x9C40),

      'REG_TO_OPT22'             : (0, 0, 0, 1),
      'REG_TO_OPT22_EXT'         : (0x0000, TrainOpts_2, 0x74), #enable two stage adapion

      'RESULTS_RETURNED'         : { # 0x0007,
         'ATTRIBUTE'          : 'FE_0245014_470992_ZONE_MASK_BANK_SUPPORT',
         'DEFAULT'            : 0,
         0                    : 0x0007,
         1                    : 0x0000,
      },
      'SET_OCLIM'                : 819,
      'NUM_READS'                : 2,
      'LOG10_BER_SPEC'           : 350, # Margin range: -4.5 to -3.25
      'DELTA_LIMIT'              : 100,
      'NUM_ITER_READS'           : 5, # was 50
      'TLEVEL'                   : MaxIteration,
      'VGA_MIN'                  : {
         'ATTRIBUTE'          : 'nextState',
         'DEFAULT'            : 'ELSE',
         'INIT_SYS'           : 128,      # VGA MIN
         'ELSE'               : 128,},    # VGA MIN
      'GAIN'                     : 0,     # non linear update gain
      #'NOMRF_REF_VALUE'          :  50,  # NOMRF reference value (only take effect when sweeping LATE1/LATE0/LATE2)
      'NUM_SQZ_WRITES'           : 0,     # number of ati write
      'SQZ_OFFSET'               : 0,     # squeeze offset in tics
      'THRESHOLD2'               : 1,
   }
   simple_OptiPrm_251_short_tune_znAlign = Utl.copy(simple_OptiPrm_251_short_tune)
   simple_OptiPrm_251_short_tune_znAlign['REG_TO_OPT8']     = simple_OptiPrm_251_short_tune_znAlign['REG_TO_OPT9']
   simple_OptiPrm_251_short_tune_znAlign['REG_TO_OPT8_EXT'] = simple_OptiPrm_251_short_tune_znAlign['REG_TO_OPT9_EXT']
   # insert VBAR's REG_TO_OPT8 n rename to REG_TO_OPT9
   simple_OptiPrm_251_short_tune_znAlign['REG_TO_OPT9']     = simple_OptiPrm_251['REG_TO_OPT8']
   simple_OptiPrm_251_short_tune_znAlign['REG_TO_OPT9_EXT'] = simple_OptiPrm_251['REG_TO_OPT8_EXT']



if testSwitch.WORKAROUND_TARGET_SIM_FILE_THRESHED and (not testSwitch.MARVELL_SRC) :
    simple_OptiPrm_251.update({
      'CWORD1'      : 0x80A,  # get the target from pc file
    })

if testSwitch.RSS_TARGETLIST_GEN:
   simple_OptiPrm_251.update({
     'RESULTS_RETURNED': 0x0004,   #supress the bucket data output
     'timeout'         : 60000 * numHeads,
   })

if testSwitch.FE_0314243_356688_P_CM_REDUCTION_REDUCE_CHANNEL_MSG:
     if not testSwitch.UPS_PARAMETERS:
        simple_OptiPrm_251.update({'RESULTS_RETURNED'   :  {
                                       'ATTRIBUTE'          : 'nextState',
                                       'DEFAULT'            : 'PREVBAR_OPTI',
                                       'PREVBAR_OPTI'       : 0x4,
                                       'READ_OPTI'          : 0x7,
                                       },})
        simple_OptiPrm_251_short_tune.update({'RESULTS_RETURNED'   :  {
                                       'ATTRIBUTE'          : 'nextState',
                                       'DEFAULT'            : 'PREVBAR_OPTI',
                                       'PREVBAR_OPTI'       : 0x4,
                                       'READ_OPTI'          : 0x7,
                                       },})
        simple_OptiPrm_251_short_tune_znAlign.update({'RESULTS_RETURNED'   :  {
                                       'ATTRIBUTE'          : 'nextState',
                                       'DEFAULT'            : 'PREVBAR_OPTI',
                                       'PREVBAR_OPTI'       : 0x4,
                                       'READ_OPTI'          : 0x7,
                                       },})
     else:
        simple_OptiPrm_251.update({'RprtOptn'   :  0x4,})
        simple_OptiPrm_251_short_tune.update({'RprtOptn'   :  0x4,})
        simple_OptiPrm_251_short_tune_znAlign.update({'RprtOptn'   :  0x4,})
     
if (testSwitch.MARVELL_SRC):
     base_phastOptiPrm_SysZn_251 ={
       'test_num'              : 251,
       'prm_name'              : 'base_phastOptiPrm_SysZn_251',
       'timeout'               : 2000 * numHeads,
       'spc_id'                : 1,
       'BIT_MASK'              : (0, 512),
       'BIT_MASK_EXT'          : (0, 0), # All bits are set by default in SF3, thus need to specify zero if the rest of the zones are not required.
       'TEST_HEAD'             : 0xFF,
       'CWORD1'                : 0x004A,  #enable BER in between,Disable ZLR,  Try again laer for test time!!
       'ZONE_POSITION'         : ZONE_POS,

       'REG_TO_OPT1'           : (0, 0, 0, 1),        # BER Data Point
       'REG_TO_OPT1_EXT'       : (0, 0x0, 0x1040),

       'REG_TO_OPT2'           : (0x11, 0xFFF0, 0xF, 2),    # Asymmetry
       'REG_TO_OPT2_EXT'       : (0, 3, 0x0474),  # DHD 3 training reads, Regression, Force Full Rng, FIR init to center, BER Opti, VGAR, NLD, FIR, filtering option.

       'REG_TO_OPT3'           : (0x33, 50, -30, 5),   # FIR Tap 3  was (0x33, 100, -100, 5)
       'REG_TO_OPT3_EXT'       : (0, 3, 0x0474),  # 3 training reads, disabled Regression, Force Full Rng, FIR init to center, BER Opti, VGAR, NLD, FIR, filtering option.

       'REG_TO_OPT4'           : (0x34, 60, 120, 5),   # FIR Tap 4 was (0x34, 100, -100, 5)
       'REG_TO_OPT4_EXT'       : (0, 3, 0x0474),  # 3 training reads, disabled Regression, Force Full Rng, FIR init to center, BER Opti, VGAR, NLD, FIR, filtering option.

       'REG_TO_OPT5'           : (0x11, 0xFFF0, 0xF, 2),    # Asymmetry
       'REG_TO_OPT5_EXT'       : (0, 3, 0x9474),  # DHD 3 training reads, Regression, Force Full Rng, FIR init to center, BER Opti, VGAR, NLD, FIR, filtering option.

       'REG_TO_OPT6'           : (0x24, 0, 15, 1),    # CTF / Bandwidth
       'REG_TO_OPT6_EXT'       : (0, 3, 0x9474),  #

       'REG_TO_OPT7'           : (0x25, 5, 60, 5),    # BST
       'REG_TO_OPT7_EXT'       : (0, 3, 0x9074),  #

       'REG_TO_OPT8'           : (0x0156, 0, 12, 1),  # Loop 1 - prc 2,3,6,7
       'REG_TO_OPT8_EXT'       : (0, 3, 0x9476),  # DHD 3 training reads, Regression, Force Full Rng, set 0x1000 bit to disable FIR and NPML init, BER Opti, VGAR, NLD, FIR, filtering option, Re-write data.

       'REG_TO_OPT9'           : (0x0157, 0, 12, 1),  # Loop 2 - prc 4,5
       'REG_TO_OPT9_EXT'       : (0, 3, 0x9476),  # DHD 3 training reads, Regression, Force Full Rng, set 0x1000 bit to disable FIR and NPML init, BER Opti, VGAR, NLD, FIR, filtering option, Re-write data.

       'REG_TO_OPT10'          : (0x0158, 0, 23, 2), # Loop 3 - prc 3,6,7
       'REG_TO_OPT10_EXT'      : (0, 3, 0x9476), # DHD 3 training reads, Regression, Force Full Rng, set 0x1000 bit to disable FIR and NPML init, BER Opti, VGAR, NLD, FIR, filtering option, Re-write data.

       'REG_TO_OPT11'          : (0x0159, 0, 23, 2), # Loop 4 - prc 0,1
       'REG_TO_OPT11_EXT'      : (0, 3, 0x9476), # DHD 3 training reads, Regression, Force Full Rng, set 0x1000 bit to disable FIR and NPML init, BER Opti, VGAR, NLD, FIR, filtering option, Re-write data.

       'REG_TO_OPT12'          : (0x015A, 0, 12, 1), # Loop 5 - prc 0,1,4,5
       'REG_TO_OPT12_EXT'      : (0, 3, 0x9476), # DHD 3 training reads, Regression, Force Full Rng, set 0x1000 bit to disable FIR and NPML init, BER Opti, VGAR, NLD, FIR, filtering option, Re-write data.

       'REG_TO_OPT13'          : (0x33, 50, -30, 5),   # FIR Tap 3  was (0x33, 100, -100, 5)
       'REG_TO_OPT13_EXT'      : (0, 3, 0x1474),  # 3 training reads, disabled Regression, Forse Full Rng, set 0x1000 bit to disable FIR and NPML init, BER Opti, VGAR, NLD, FIR, filtering option.

       'REG_TO_OPT14'          : (0x34, 60, 120, 5), # FIR Tap 4 was (0x34, 100, -100, 5) was 60, 120, 5 25APR2012
       'REG_TO_OPT14_EXT'      : (0, 3, 0x1474),  # 3 training reads, disabled Regression, Force Full Rng, set 0x1000 bit to disable FIR and NPML init, BER Opti, VGAR, NLD, FIR, filtering option.

       'REG_TO_OPT15'          :  (0, 0, 0, 1),        # BER Data Point
       'REG_TO_OPT15_EXT'      :  (0, 0x0, 0x1040),
       'NUM_READS'             : 2,
       'RESULTS_RETURNED'      : 0x0007,
       'SET_OCLIM'             : 819,
       'TLEVEL'                : MaxIteration,
       'GAIN'                  :  0,       # non linear update
       }
else:
     base_phastOptiPrm_SysZn_251 ={
       'test_num'              : 251,
       'prm_name'              : 'base_phastOptiPrm_SysZn_251',
       'timeout'               : 2000 * numHeads,
       'spc_id'                : 1,
       'BIT_MASK'              : (0, 512),
       'BIT_MASK_EXT'          : (0, 0), # All bits are set by default in SF3, thus need to specify zero if the rest of the zones are not required.
       'TEST_HEAD'             : 0xFF,
       'CWORD1'                : 0x000A,  #enable BER in between
       'ZONE_POSITION'         : ZONE_POS,
       'REG_TO_OPT1'           : (132, 0, 0, 1),      # VGA
       'REG_TO_OPT1_EXT'       : (0, 0x81, 0),

       'REG_TO_OPT2'           : (146, 30, 50, 10),   # Dummy CTFFR,force full range
       'REG_TO_OPT2_EXT'       : (0x0, TrainOpts, 0xC3D),

       'REG_TO_OPT3'           : (132, 0, 0, 1),      # VGA
       'REG_TO_OPT3_EXT'       : (0, 0x81, 0),

       'REG_TO_OPT4'           : (146, 20, 60, 2),    # CTFFR,
       'REG_TO_OPT4_EXT'       : (0x0, TrainOpts, 0x8C3D),

       'REG_TO_OPT5'           : (37, 5, 125, 5),     # ZFR
       'REG_TO_OPT5_EXT'       : (0x0, TrainOpts, 0x8C3C), # was 8000

       'REG_TO_OPT7'           : (145, -80, 80, 16),  # TDTARG
       'REG_TO_OPT7_EXT'       : (0x0, TrainOpts, 0xC3C),

       #'REG_TO_OPT8'           : (147, -127, 127, 8),    #NLTAP
       #'REG_TO_OPT8_EXT'       : (0x38, TrainOpts, 0x8C3C),  # 8 means it need to freeze non linear update gain to Gain value

       'REG_TO_OPT9'           : (155, 0, 63, 2),     # Precomp-LATE02RF  (DBE)
       'REG_TO_OPT9_EXT'       : (0x0, TrainOpts, 0x8C00),

       'REG_TO_OPT10'          : (146, 20, 60, 2),    # CTFFR - change from relative sweep
       'REG_TO_OPT10_EXT'      : (0x0, TrainOpts, 0x8C3D),

       'REG_TO_OPT11'          : (37, 5, 125, 5),     # ZFR - change from relative sweep
       'REG_TO_OPT11_EXT'      : (0x0, TrainOpts, 0x8C3C),

       'REG_TO_OPT12'          : (245, 0, 0, 1),      # NPT
       'REG_TO_OPT12_EXT'      : (0, 0, 0x6000),

       'REG_TO_OPT13'          : (145, -80, 80, 16),  # TDTARG
       'REG_TO_OPT13_EXT'      : (0x0, TrainOpts, 0x2C3C),

       #'REG_TO_OPT14'          : (234, 1, 15, 1),     # VSCALE with ILC = 2 , enable margin and screeze write
       #'REG_TO_OPT14_EXT'      : (0x0, 0x1001, 0x9C40), # was (0x0, 0x1381, 0x107C)

       #'REG_TO_OPT15'          : (257, 1, 15, 1),     # VSCALE_LLR with ILC = 2 ,update later
       #'REG_TO_OPT15_EXT'      : (0x0, 0x1001, 0x9C40), # was (0x0, 0x1381, 0x107C)

       #'REG_TO_OPT16'          : (267, 1, 15, 1),     # VSCALE_BM2
       #'REG_TO_OPT16_EXT'      : (0x0, 0x1001, 0x9C40),

       #'REG_TO_OPT17'          : (258, 1, 15, 1),     #VSCALE_LLR2
       #'REG_TO_OPT17_EXT'      : (0x0, 0x1001, 0x9C40),

       'REG_TO_OPT18'          : (0, 0, 0, 1),
       'REG_TO_OPT18_EXT'      : (0x0000, 0x0, 0x3C),

       'NUM_READS'             : 2,
       'RESULTS_RETURNED'      : 0x0007,
       'SET_OCLIM'             : 819,
       'TLEVEL'                : MaxIteration,
       'GAIN'                  :  0,       # non linear update
   }

if testSwitch.FE_0262766_480561_RUN_MRBIAS_OPTI_T251:
    mrbias_OptiPrm_251 ={
       'test_num'              : 251,
       'prm_name'              : 'mrbias_OptiPrm_251',
       'timeout'               : 1000 * numHeads,
       'spc_id'                : 1,
       'BIT_MASK'              : (0, 1),
       'BIT_MASK_EXT'          : (0, 0), # All bits are set by default in SF3, thus need to specify zero if the rest of the zones are not required.
       'TEST_HEAD'             : 0xFF,
       'CWORD1'                : 0x080A,  #enable BER in between
       'ZONE_POSITION'         : ZONE_POS,

       'DELTA_LIMIT'           : 100,  #
       'SET_OCLIM'             : 819,
       'RESULTS_RETURNED'      : 7,
       'SQZ_OFFSET'            : 0,
       'NUM_ITER_READS'        : 100,
       'LOG10_BER_SPEC'        : 350, # Margin range: -4.5 to -3.5Rh
       'NUM_READS'             : 100,
       'THRESHOLD2'            : 1,  #
       'TLEVEL'                : MaxIteration,
       'VGA_MIN'               : 128,  #
       'NUM_SQZ_WRITES'        : 0,

       'REG_TO_OPT1'           : (1, 60, 100, 1),      # MRBIAS test range 60% ~ 100%, increase 1
       'REG_TO_OPT1_EXT'       : (0x0, 0x82, 0x0041),
    }


if testSwitch.KARNAK and (not testSwitch.MARVELL_SRC):
   base_phastOptiPrm_SysZn_251.pop('REG_TO_OPT12')
   base_phastOptiPrm_SysZn_251.pop('REG_TO_OPT12_EXT')
   base_phastOptiPrm_SysZn_251.pop('REG_TO_OPT13')
   base_phastOptiPrm_SysZn_251.pop('REG_TO_OPT13_EXT')
   base_phastOptiPrm_SysZn_251.update({'THRESHOLD2': 1,})

if testSwitch.FE_0314243_356688_P_CM_REDUCTION_REDUCE_CHANNEL_MSG:
   base_phastOptiPrm_SysZn_251.update({'RESULTS_RETURNED'   :  0x4,})

# Parameter used for post vbar opti
simple_OptiPrm_251_2 = simple_OptiPrm_251.copy()

base_phastOptiPrm_251 = simple_OptiPrm_251.copy()
base_phastOptiPrm_251.update({'prm_name': 'base_phastOptiPrm_251',})

base_readOpti_Prm_251 = simple_OptiPrm_251.copy()
if not testSwitch.FE_0258915_348429_COMMON_TWO_TEMP_CERT:
   base_readOpti_Prm_251.update({'prm_name': 'base_readOpti_Prm_251',})
else:
   base_readOpti_Prm_251.update({'prm_name': 'base_readOpti_Prm_251','RESULTS_RETURNED'   :  0x0007,})

if testSwitch.FE_0311911_403980_P_PRECODER_IN_READ_OPTI_ONLY:
   #Run Precoder in read_opti only:
   base_readOpti_Prm_251['REG_TO_OPT18']=(0x613C, 0, 4, 1)
   base_readOpti_Prm_251['REG_TO_OPT18_EXT']=(0, 3, 0x1C42)
   base_phastOptiPrm_251['REG_TO_OPT18']=(0x613C, 0, 4, 1)
   base_phastOptiPrm_251['REG_TO_OPT18_EXT']=(0, 3, 0x1C42)
   #extern test switch cannot be used here. Thus, the following parameters are set in SerialTest.py & Opti_Read.py.
   #simple_OptiPrm_251['PRECODER0']=(0x0713, 0x4652)
   #simple_OptiPrm_251['PRECODER1']=(0x0713, 0x4625)
   #simple_OptiPrm_251['PRECODER2']=(0x0145, 0x7362)
   #simple_OptiPrm_251['PRECODER3']=(0x0142, 0x7365)
   #simple_OptiPrm_251['PRECODER4']=(0x7654, 0x3210)

if testSwitch.FE_0253168_403980_RD_OPTI_ODD_ZONE_COPY_TO_EVEN:
   if testSwitch.WORKAROUND_TARGET_SIM_FILE_THRESHED:
      base_readOpti_Prm_251.update({'CWORD1': 0x180A,})
   else:
      base_readOpti_Prm_251.update({'CWORD1': 0x100A,})

WPC_TripletPrm_178 = {
      'test_num'           : 178,
      'prm_name'           : 'WPC_TripletPrm_178',
      'timeout'            : 2000*numHeads,
      'spc_id'             : 1,
      'CWORD1'             : 0x0200,
      'BIT_MASK'           : (0, 512),
      'DURATION'           : 6,
      'WRITE_CURRENT'      : 7,
      'DAMPING'            : 7,
      'CWORD2'             : 0x1107,
      'HEAD_RANGE'         : 0x00FF,
   }

VSCALE_OptiPrm_251 = {
   'test_num'              : 251,
   'prm_name'              : 'VSCALE_OptiPrm_251',
   'timeout'               : 6000 * numHeads,
   'spc_id'                : 1,
   'BIT_MASK'              : (0, 0x0100),
   'TEST_HEAD'             : 0xFF,
   'CWORD1'                : 0x0008,
   'ZONE_POSITION'         : ZONE_POS,

   'REG_TO_OPT1'          : (234,3, 13, 5),   # VSCALE in SFR mode
   'REG_TO_OPT1_EXT'      : (0, 0x381, 0x1CC0),
   'REG_TO_OPT2'          : (234, 0, 4, 2),   # VSCALE relative sweep
   'REG_TO_OPT2_EXT'      : (0, 0x381, 0x15FC),


   'RESULTS_RETURNED'      : 0x0007,             #
   'CWORD2'                : 0x0004,             # populate FIR TAPs with real values in the debug data
   'SET_OCLIM'             : 819,
   #'SYNC_BYTE_CONTROL'     : 0x000A,
   'NUM_READS'             : 50,
   'TLEVEL'                : 1,
   }

if testSwitch.VBAR_HMS_V2:
   # Using 2 iterations provides a better cal
   VSCALE_OptiPrm_251.update({
      'TLEVEL'             : 2,
   })

if testSwitch.VBAR_HMS_V2 and not testSwitch.RSSDAT:
   # Shut off detailed reporting to save log space
   VSCALE_OptiPrm_251.update({
      'RESULTS_RETURNED'   : 0x0000,
   })





tdtarg_OptiPrm_251={       # Test 251 - read channel optimization.
   #TDTARGR optimization
   'test_num'              : 251,
   'prm_name'              : 'tdtarg_OptiPrm_251',
   'timeout'               : 10600*numHeads,
   'spc_id'                : -1,
   'CWORD1'                : 0x0038,
   #                          regID min max step
   'REG_TO_OPT1'           : (145,  2,  15, 1),    # REGID_TDTARG (sweep from 2 to 15)  With bitmask
   'REG_TO_OPT1_EXT'       : (0,    0,  0xC3C),    # Save FIR and NPML at optimized tdtarg, test all values, force best fitness pick
   'RESULTS_RETURNED'      : 0x0007,
   'ZONE_POSITION'         : ZONE_POS,
   'SET_OCLIM'             : 819,
   'BIT_MASK'              : (0x0001, 0xFFFF),
   'MARGIN_LIMIT'          : 600,
   #'SYNC_BYTE_CONTROL'     : 0x000A,
   }
#if testSwitch.extern.FE_0280068_322482_CBD_MEASUREMENT:

CBDMeasurement_Prm_251={       # 3, 75, 145
   'test_num'              : 251,
   'prm_name'              : 'CBD_Measurement_251',
   'timeout'               : 100000,
   'spc_id'                : 1,
   'CWORD1'                : 90,
   'CWORD2'                : 0xB000,
   'REG_TO_OPT2'           : (158,  0,  0, 1),
   'REG_TO_OPT2_EXT'       : (0,    5,  0x5555),
   'RESULTS_RETURNED'      : 12803,
   'ZONE_POSITION'         : 198,
   'SET_OCLIM'             : 819,
   'BIT_MASK'              : (0x000, 0x008),
   'BIT_MASK_EXT'          : (0x000, 0x000),
   'TEST_HEAD'             : 0xFF,
   'NUM_READS'             : 20,
   'THRESHOLD2'            : 1000,
   'TLEVEL'                : 1797,
   'GAIN2'                 : 102,
   'ADAPTIVES'             : 6,
   'ZONE_MASK_BANK'        : 0,
   }
if testSwitch.MARVELL_SRC:
  CBDMeasurement_Prm_251.update({'REG_TO_OPT2': (351,  0,  0, 1),})

eSNR_Prm_488={       # 3, 75, 145
   'test_num'              : 488,
   'prm_name'              : 'eSNR_488',
   'timeout'               : 200000,
   'spc_id'                : 1,
   'HEAD_RANGE': 255, 
   'ZONE_POSITION': 0, 
   'ZONE_MASK': (0, 0x0100), 
   'ZONE_MASK_EXT': (0, 0), 
   'ZONE_MASK_BANK': 0, 
   'READ_OFFSET': 0, 
   'NLD_WRITE_LOOP': 1, 
   'NLD_READ_LOOP': 3, 
   'TRIM_PERCENTAGE_VALUE': 80, 
   'GAIN': 0, 
   'PERCENT_LIMIT': 8, 
   'ADAPT_FIR': 0, 
   'RETRY_LIMIT': 7,
   'CWORD1': 2,  
   'CWORD2': 1, 
   'DEBUG_PRINT': 35

   }


#following is for zone insertion scheme
if testSwitch.FE_0376137_356688_VBAR_MARGIN_ZONE_COPY_TTR:
   nonUMP_zoneGroup_size = 10
   ump_zoneGroup_size = 1
   opti_Zn_index= [0,0,0,0,0,2,0,0,0,0,4] #opti zone index array for group size
   KFCI_insert_limit = 0.01             #insert criteria, eg, KFCI +-1%
else:
   nonUMP_zoneGroup_size = 5
   ump_zoneGroup_size = 1
   opti_Zn_index= [0,0,0,0,0,2,0,0,0,0] #opti zone index array for group size
   KFCI_insert_limit = 0.01             #insert criteria, eg, KFCI +-1%


base_PHAST_AGC_JOG_238 = {
   'test_num'           : 238,
   'prm_name'           : 'base_PHAST_AGC_JOG_238',
   'timeout'            : 5000*numHeads,
   'spc_id'             : 1,
   'THRESHOLD'          : 38,
   'THRESHOLD2'         : 435,               # 905% of the maximum VGA value
   'NUM_SAMPLES'        : 2,                 # Max is 5 and 2 has a hidden retry if variance is to high
   'NUM_ADJ_ERASE'      : { 
       'ATTRIBUTE'      : 'WA_0347481_0228371_T238_COARSE_TUNE_4TRKS',
       'DEFAULT'        : 0,
       1                : 4,                 # cater 4 trks  
       0                : 3,                 # cater 3 trks
    },
   'MJOG_FOM_THRESHOLD' : 800,
   'TEST_HEAD'          : 0xFFFF,
   'CWORD1'             : 0x6007,            # to print out VGA value
   'CWORD2'             : 0,       # Temporary change to disable MRA, FIR, NPFIR for Banshee
   'S_OFFSET'           : 0,
   'SET_OCLIM'          : 0x4CC,
   'SYNC_BYTE_CONTROL'  : 0x10,
   'MAX_ERROR'          : 100,
   'INCREMENT'          : 6,
   'TARGET_TRK_WRITES'  : 3,
   'SYNC_BYTE_CONTROL'  : 0x280,     # syn mark threshold, take effective when sync mark threshold
                                     # detection turn on (RAP C902)
}


base_PHAST_CQM_JOG_238 = {
   'test_num'              : 238,
   'prm_name'              : 'base_PHAST_CQM_JOG_238',
   'timeout'               : 1000 * numHeads,
   'spc_id'                : 1,
   'MJOG_FOM_THRESHOLD'    : 0x800,
   'THRESHOLD'             : 38,
   'THRESHOLD2'            : 512,
   'NUM_SAMPLES'           : 2,
   'NUM_ADJ_ERASE'         : 2,
   'TEST_HEAD'             : 0xFFFF,
   'CWORD1'                : 0x2081,
   'S_OFFSET'              : 0,
   'MAX_ERROR'             : 100,
   'SYNC_BYTE_CONTROL'     : 0x001F,
   }


vgaOptiPrm_151={
   #Test 151 - read channel optimization.
   #VGA Parameter Blk 7313
   'test_num'              : 151,
   'prm_name'              : 'vgaOptiPrm_151',
   'timeout'               : 5000 * numHeads,
   'spc_id'                : 1,
   'TRGT_PRE_READS'        : 0x50,              # Training Reads (parameter value  in sectors now)
   'RETRY_LIMIT'           : 5,                 # Retries to perform on read errors.
   'TARGET_TRK_WRITES'     : 0x01,
   'NUM_SQZ_WRITES'        : 0x00,
   'SQZ_OFFSET'            : 0x00,
   'NUM_SAMPLES'           : 0x02,
   'SET_OCLIM'             : 0x4E1,
   'CWORD1'                : 0x4000,
   # Optimize up to 4 register at a time.  Each register to opt
   # has a registerID, start value, end value, and step size.
   # The extention parameter has re-write flag, relative steps
   # below, and relative steps above (if relative mode).
   # All unused variables should be set to zero.
   #---------Example for setting up write current.----------
   #                      regID start end   step
   'REG_TO_OPT1'           : (0x82, 0x00, 0x00, 0x01),   # REGID_VGAS
   'REG_TO_OPT2'           : (0x84, 0x00, 0x00, 0x01),   # REGID_VGAR
   'RESULTS_RETURNED'      : 0x10,
   'MD_CYL'                : (0x0001, 0x0000),
   'VGA_MAX'               : 0x1C0,
   'VGA_MIN'               : 0x80,
   'ZONE_POSITION'         : ZONE_POS
   }

if testSwitch.VgaPcFileFlashUpdate == 1:
   vgaOptiPrm_151.update({'CWORD1'  : 0x4200})


preComp_OptiPrm_151={
   #Test 151 - read channel optimization.
   #Precomp LATE2R/LATE2F Blk 7314
   'test_num'              : 151,
   'prm_name'              : 'preComp_OptiPrm_151',
   'timeout'               : 10000 * numHeads,
   'spc_id'                : 1,
   'CWORD1'                : 0x4000,
   'TARGET_TRK_WRITES'     : 0x01,
   'NUM_SAMPLES'           : 0x02,
   'REG_TO_OPT1'           : (0x88, -12, 5, 0x01),       # REGID_PRECOMP_LATE-> Uses offset from NOMR value not explicit values listed here
   'REG_TO_OPT1_EXT'       : (0x01, 0x00, 0x00),         # ReWrite each time value changes
   'RESULTS_RETURNED'      : 0x0F,
   'NON_DIS_WEDGES'        : 50,
   'RW_MODE'               : 0x0,                        # Force Sync - currently required for Agere
   'TRGT_PRE_READS'        : 0x50,                       # Training Reads (parameter value  in sectors now)
   'RETRY_LIMIT'           : 5,                          # Retries to perform on read errors.
   'PATTERNS'              : (0xAA, 0xAA, 0xAA),
   'LIMIT32'               : (0, 0),                     # Debug output - Taps and CQM data
   'ZONE_POSITION'         : ZONE_POS
   }

tdtarg_OptiPrm_151={
   #Test 151 - read channel optimization.
   #TDTARGR optimization
   'test_num'              : 151,
   'prm_name'              : 'tdtarg_OptiPrm_151',
   'timeout'               : 10000*numHeads,
   'spc_id'                : 1,
   'CWORD1'                : 0x4000,
   'TARGET_TRK_WRITES'     : 0x01,
   'NUM_SAMPLES'           : 0x02,                       # 1 might be sufficient
   #                          regID start end step
   'REG_TO_OPT1'           : (0x91, 0x08, 0x0F, 0x01),   # REGID_TDTARG
   'RESULTS_RETURNED'      : 0x0F,
   'NON_DIS_WEDGES'        : 50,
   # Force reset of channel back to defaults between each bucket point.
   # This is done by forcing a zero seek.  Prevents failure do to railed taps.
   'SEEK_COUNT'            : 1,                          # Just needs to be non-zero, only one seek is performed.
   'TRGT_PRE_READS'        : 0x50,                       # Training Reads (parameter value  in sectors now)
   'RETRY_LIMIT'           : 5,                          # Retries to perform on read errors.
   'PATTERNS'              : (0xAA, 0xFF, 0xFF),
   'LIMIT32'               : (0, 0),                     # Display TAP and CQM debug data (1,0,),
   'ZONE_POSITION'         : ZONE_POS
   }

zfr_OptiPrm_151={
   #Test 151 - read channel optimization.
   #Precomp LATE2R/LATE2F Blk 7314
   'test_num'              : 151,
   'prm_name'              : 'zfr_OptiPrm_151',
   'timeout'               : 10000 * numHeads,
   'spc_id'                : 1,
   'CWORD1'                : 0x4000,
   'TARGET_TRK_WRITES'     : 0x01,
   'NUM_SAMPLES'           : 0x02,
   'REG_TO_OPT1'           : (0x25, 0x05, 0x1A, 0x01),   # REGID_PRECOMP_LATE
   'RESULTS_RETURNED'      : 0x0F,
   'NON_DIS_WEDGES'        : 50,
   'TRGT_PRE_READS'        : 0x50,                       # Training Reads (parameter value  in sectors now)
   'RETRY_LIMIT'           : 5,                          # Retries to perform on read errors.
   'PATTERNS'              : (0xAA, 0xAA, 0xAA),
   'LIMIT32'               : (0,0),                      # Debug output - Taps and CQM data
   'ZONE_POSITION'         : ZONE_POS
   }

ctffr_OptiPrm_151={
   #Test 151 - read channel optimization.
   #Precomp LATE2R/LATE2F Blk 7314
   'test_num'              : 151,
   'prm_name'              : 'ctffr_OptiPrm_151',
   'timeout'               : 10000 * numHeads,
   'spc_id'                : 1,
   'TARGET_TRK_WRITES'     : 0x01,
   'NUM_SAMPLES'           : 0x02,
   'REG_TO_OPT1'           : (0x92, 35, 56, 0x03),       # REGID_CTFFR
   'RESULTS_RETURNED'      : 0x0F,
   'NON_DIS_WEDGES'        : 50,
   'SEEK_COUNT'            : 1,                          # Just needs to be non-zero, only one seek is performed.
   'TRGT_PRE_READS'        : 0x50,                       # Training Reads (parameter value  in sectors now)
   'RETRY_LIMIT'           : 5,                          # Retries to perform on read errors.
   'PATTERNS'              : (0xAA, 0xAA, 0xAA),
   'CWORD1'                : 0x4000,                     # Don't update RAP
   'ZONE_POSITION'         : ZONE_POS
   }

nld_151={
  #Test 151 - read channel optimization.
  #Precomp LATE2R/LATE2F Blk 7314
  'test_num':151,
  'prm_name':'nld_151',
  'timeout':10000*numHeads,
  'spc_id':1,
  "TARGET_TRK_WRITES" : (0x01,),
  "NUM_SQZ_WRITES": (1,),
  "SQZ_OFFSET": (0,),
  "NLD_WRITE_LOOP": (2,),
  "NLD_READ_LOOP": (3),
  "CWORD2":(0x1400),
  "CWORD1" : (0x4008,),
  "ZONE_POSITION": ZONE_POS,
  "SET_OCLIM" : (819,),
}

FIR_NY_DC_OptiPrm_141 = {
   #Test 141 - read channel optimization.
   #Tap Adaptation
   'test_num'              : 141,
   'prm_name'              : 'FIR_NY_DC_OptiPrm_141',
   'spc_id'                : 1,
   'REG_TO_OPT1'           : (0x00, 0x00, 0x00, 0x00),   # 0 = FIR_TAPS
   'REG_TO_OPT2'           : (0x01, 0x00, 0x00, 0x00),   # 1 = NYQUIST_AND_DC_TAPS
   'PATTERNS'              : (0xAA, 0xAA, 0xAA),
   'CWORD1'                : 0x4100,                     # 'OR' in 0x0002 to force update for passed heads, 0x0008 to avoid saving to RAP
   'TRGT_PRE_READS'        : 0x50,                       # Training Reads (parameter value  in sectors now)
   'RETRY_LIMIT'           : 5,                          # Retries to perform on read errors.
   'TARGET_TRK_WRITES'     : 1,                          # No matter the count, a max of 1 pattern write will be done
   'NON_DIS_WEDGES'        : 50,
   'RESULTS_RETURNED'      : 0xF,
   'timeout'               : 10000*numHeads,
   'ZONE_POSITION'         : ZONE_POS
   }

NPML_OptiPrm_141={
   #Test 141 - read channel optimization.
   #Tap Adaptation
   'test_num'              : 141,
   'prm_name'              : 'NPML_OptiPrm_141',
   'spc_id'                : 1,
   'REG_TO_OPT2'           : (0x02, 0x00, 0x00, 0x00),   # 2 = NPML_TAPS
   'PATTERNS'              : (0xAA, 0xAA, 0xAA),
   'CWORD1'                : 0x4100,                     # 'OR' in 0x0002 to force update for passed heads, 0x0008 to avoid saving to RAP
   'TRGT_PRE_READS'        : 0x50,                       # Training Reads (parameter value  in sectors now)
   'RETRY_LIMIT'           : 5,                          # Retries to perform on read errors.
   'TARGET_TRK_WRITES'     : 1,                          # No matter the count, a max of 1 pattern write will be done
   'NON_DIS_WEDGES'        : 50,
   'RESULTS_RETURNED'      : 0xF,
   'timeout'               : 10000*numHeads,
   'ZONE_POSITION'         : ZONE_POS
   }

FIR_NPML_OptiPrm_141={
  #Test 141 - read channel optimization.
  #Tap Adaptation
  'test_num'               : 141,
  'prm_name'               : 'FIR_NPML_OptiPrm_141',
  'spc_id'                 : 1,
  'REG_TO_OPT1'            : (0x00, 0x00, 0x00, 0x00),   # 1 = FIR taps
  'REG_TO_OPT2'            : (0x02, 0x00, 0x00, 0x00),   # 2 = NPML_TAPS
  'PATTERNS'               : (0xAA, 0xAA, 0xAA),
  'CWORD1'                 : 0x4100,                     # 'OR' in 0x0002 to force update for passed heads, 0x0008 to avoid saving to RAP
  'TRGT_PRE_READS'         : 8,                          # Training Reads (parameter value  in sectors now)
  'RETRY_LIMIT'            : 5,                          # Retries to perform on read errors.
  'TARGET_TRK_WRITES'      : 1,                          # No matter the count, a max of 1 pattern write will be done
  'NON_DIS_WEDGES'         : 1,
  'RESULTS_RETURNED'       : 0xF,
   'timeout'               : 10000 * numHeads,
   'ZONE_POSITION'         : ZONE_POS
}

MRNL_OptiPrm_141={
   #Test 141 - read channel optimization.
   #Tap Adaptation
   'test_num'              : 141,
   'prm_name'              : 'MRNL_OptiPrm_141',
   'spc_id'                : 1,
   'REG_TO_OPT1'           : (0x03, 0x00, 0x00, 0x00),   # 3 = MRNL_TAPS
   'PATTERNS'              : (0xAA, 0xAA, 0xAA),
   'CWORD1'                : 0x4100,                     # 'OR' in 0x0002 to force update for passed heads, 0x0008 to avoid saving to RAP
   'TRGT_PRE_READS'        : 0x50,                       # Training Reads (parameter value  in sectors now)
   'RETRY_LIMIT'           : 5,                          # Retries to perform on read errors.
   'TARGET_TRK_WRITES'     : 1,                          # No matter the count, a max of 1 pattern write will be done
   'NON_DIS_WEDGES'        : 50,
   'RESULTS_RETURNED'      : 0xF,
   'timeout'               : 10000 * numHeads,
   'ZONE_POSITION'         : ZONE_POS
   }

cqmMicruJog_138 = {
   'test_num'              : 138,
   'prm_name'              : 'cqmMicruJog_138',
   'timeout'               : 20000 * numHeads,
   'spc_id'                : 1,
   'PATTERNS'              : (0xAA, 0xFF, 0x00),
   'SQZ_PATTERNS'          : (0xAA, 0xAA),
   'TARGET_TRK_WRITES'     : 0x05,
   'NUM_SQZ_WRITES'        : 0x06,
   'SQZ_OFFSET'            : 0x00,
   'NUM_SAMPLES'           : 0x02,
   'CWORD1'                : 0x8002,
   'NON_DIS_WEDGES'        : 50,
   'TEST_HEAD'             : 0xFFFF,
   'OFFSET_SETTING'        : (-0x100, 0x100, 0x10),
   'MJOG_FOM_THRESHOLD'    : 0x300,
   'NUM_ADJ_ERASE'         : 0x0002,
   'MAX_ERROR'             : 0xFFFF,
   'LIMIT'                 : 6,
   'AC_ERASE'              : (),
   }

reportChanOptiParms_255 = {
   'test_num'              : 255,
   'prm_name'              : 'reportChanOptiParms_255',
   'timeout'               : 600,
   'spc_id'                : 1,
   'RESULTS_RETURNED'      : 0x803F,
   }


otc_Screen_167 = {
      'test_num'           : 167,
      'prm_name'           : 'Off Track Capability Screen for Test 167',
      'timeout'            : 1000*numHeads,
      'spc_id'             : 1,
      'TEST_CYL'           : (0, 0x100),
      'HEAD_RANGE'         : 0xFF,
      'CWORD1'             : 0x493,
      'NUM_SAMPLES'        : 5,
      'TARGET_TRK_WRITES'  : 1,
      'NUM_SQZ_WRITES'     : 1,
      'SQZ_OFFSET'         : 0,
      'INCREMENT'          : 2,
      'THRESHOLD'          : 55,    # Diveded by 10 (37 => 3.8)
      'MINIMUM'            : 100,
      'MAXIMUM'            : 8000,
      'LIMIT'              : 300,
      'PATTERNS'           : (0xAA, 0xFF, 0x00),
      'OFFSET_SETTING'     : (0, 20, 10),
      'READ_OFFSET'        : 20,
      'ZONE_POSITION'      : 198,
      'ZONE_MASK'          : (0x7FFF, 0xFFFF),
      'TLEVEL'             : 0x105,
}


Writer_Reader_Gap_Calib_176 = {
   'test_num'              : 176,
   'prm_name'              : 'Writer_Reader_Gap_Calib_176',
   'timeout'               : 500 * numHeads,
   'spc_id'                : 1,
   'CWORD1'                : 0x4004, #use script parameter for fre, gap & radius, trunk code bit 2 is to use default for RAP
   'HEAD_RANGE'            : 0x00FF,
   'FREQUENCY'             : 105, #For Chengai
   'SEEK_STEP'             : 50,
   'OFFSET'                : {
      'ATTRIBUTE'       : 'FE_0253057_350037_EXTEND_GAP_CAL_SUPPORT',
      'DEFAULT'         : 0,
      1                 : -1,
      0                 : 0x8000,
   },
   'PAD_SIZE'              : {
      'ATTRIBUTE'       : 'FE_0184102_326816_ZONED_SERVO_SUPPORT',
      'DEFAULT'         : 1,
      1                 : -200,
      0                 : {
         'ATTRIBUTE' : ('POLY_ZAP', '_128_REG_PREAMPS'),
         'DEFAULT'   : (0,0),
         (0,0)       : -11400,
         (1,0)       : 2700,
         (1,1)       : 3000,
      },
   },
   'GAP_SIZE'              : 205,
   'MAX_RADIUS'         : 1211,
}
if testSwitch.HAMR:
   Writer_Reader_Gap_Calib_176['OFFSET'] = 12
   

if testSwitch.FE_0245944_504159_USE_DFT_VAL_RADIUS_GAP_FRE_FRM_RAP_SAP:
   del Writer_Reader_Gap_Calib_176['GAP_SIZE']
   del Writer_Reader_Gap_Calib_176['MAX_RADIUS']
   del Writer_Reader_Gap_Calib_176['FREQUENCY']

prm_176_update= {
   'test_num'    :  176,
   'prm_name'    :  'prm_176_update',
   'CWORD1'      :  (0x8002),         # RAP_REVERT | NO_UPDATE_RZ = 1
}

# Parameters for Delta MR Resistance Check
get_MR_Values_186 = {
   'test_num'              : 186,
   'prm_name'              : 'get_MR_Values_186',
   'spc_id'                : 1,
   'CWORD1'                : 0x1002,  # Only gather and report MR resistance values
   }

mrDeltaLim = 100   # Absolute value of maximum allowed MR resistance change from PRE2 to FNC2
mrDeltaLimPercent = 20 # delta MRE in percentage

mrComboScreenDeltaCRT2 = {
   'ATTRIBUTE'    : ('nextOper', 'IS_2D_DRV'),
   'DEFAULT'      : 'default',
   'default'      : 100.0, # fail-safe
   ('CRT2', 1)       : { # for 2D in CRT2 only
      'ATTRIBUTE'    : 'HGA_SUPPLIER',
      'DEFAULT'      : 'RHO',
      'RHO'          : 100.0, # fail-safe
      'HWY'          : 15.0,
   },
}

mrComboScreenPRE2 = {
   'ATTRIBUTE'    : ('nextOper', 'IS_2D_DRV'),
   'DEFAULT'      : 'default',
   'default'      : 0.0, # fail-safe
   ('CRT2', 1)       : { # for 2D in CRT2 only
      'ATTRIBUTE'    : 'HGA_SUPPLIER',
      'DEFAULT'      : 'RHO',
      'RHO'          : 0.0, # fail-safe
      'HWY'          : 350.0,
   },
}
mrComboScreenDeltaFNC2Percent = {
   'ATTRIBUTE'    : ('nextOper', 'IS_2D_DRV'),
   'DEFAULT'      : 'default',
   'default'      : 0, # fail-safe
   ('FNC2', 1)       : { # for 2D in FNC2 only
      'ATTRIBUTE'    : 'HGA_SUPPLIER',
      'DEFAULT'      : 'RHO',
      'RHO'          : 3, # fail-safe
      'TDK'          : 0,
   },
}
mrComboScreenDFCT_TRK_CNT = {
   'ATTRIBUTE'    : ('nextOper', 'IS_2D_DRV'),
   'DEFAULT'      : 'default',
   'default'      : 0, # fail-safe
   ('FNC2', 1)       : { # for 2D in FNC2 only
      'ATTRIBUTE'    : 'HGA_SUPPLIER',
      'DEFAULT'      : 'RHO',
      'RHO'          : 1400, # fail-safe
      'TDK'          : 0,
   },
}

T186_ResRangeLim = 50  # Range (max-min) MR resistance change, in percent of baseline

prm_186_MRRes_noSync = {
   'test_num'              : 186,
   'timeout'               : 600,
   'prm_name'              : 'prm_186_MRRes_noSync',
   'spc_id'                : 1,
   'CWORD1'                : 0x1082,  # Just measure MR resistance, no demodSync
   }


setNPT_156 = {
   'test_num'              : 156,
   'prm_name'              : 'setNPT_156',
   'timeout'               : 200,
   'spc_id'                : 1,
   'CWORD1'                : 1,
   }

prm_ProgRdChanTarget = {
   'testMethod'            : 'HdZn',   # Either 'HdZn' to test by head/zone or 'Hd' to test by head only
   'berECCLevel'           : 0,
   'berRetryLim'           : 10,       # Number of BER measurement retries allowed
   'berRetryStep'          : 50,       # Number of cylinders to move for each BER retry
   }

prm_ProgRdChanTarget_250 = {
   'test_num'              : 250,
   'prm_name'              : 'prm_ProgRdChanTarget_250',
   'spc_id'                : 1,
   'timeout'               : 1000 * numHeads,   # Extra pad- should take 5 min/zone for each pass
   'WR_DATA'               : 0x00,              # 1 byte for data pattern if writing first
   'ZONE_POSITION'         : ZONE_POS,
   'MAX_ERR_RATE'          : -83,
   'CWORD1'                : 0x0187,            # 1 = write first, 0x80 dummy read, 0x2 sample mode, 0x100 limit number of tracks to test, 0x4 sector error rate mode
   'MINIMUM'               : -38,               # Minimum BER spec
   }

prm_PrePostOptiAudit_250 = {
   'test_num'              : 250,
   'prm_name'              : 'prm_PrePostSimpleOptiAudit_250',
   'spc_id'                : 4,
   'timeout'               : 1000*numHeads,             # per Rich Dziallo, 2011MAR18
   'CWORD1'                : 0x0981,
   'CWORD2'                : 0x0000,
   'TEST_HEAD'             : 0x00FF,
   'ZONE_MASK'             : {
      'ATTRIBUTE'    : 'numZones',
      'DEFAULT'      : 24,
      24             : (0x0084, 0x1045),  # zone [0,2,6,12,18,23]
      31             : (0x4101, 0x0109),  # zone [0,3,8,16,24,30]
      60             : (0x1, 0x41),  # zone [0,6,16,32,48,59]
      120            : (0L, 4097L),   # zone 0,12,32 for zone bank 0. total zones: [0,12,32,64,96,119] defined in TP.Measured_BPINOMINAL_Zones or VABR.py def BPINominalBHBZV2.
      150            : (0L, 32769L),   # zone 0,15,40 for zone bank 0. total zones: [0,15,40,80,120,149] defined in TP.Measured_BPINOMINAL_Zones or VABR.py def BPINominalBHBZV2.
      180            : (4L, 1),   # zone 0,18,48 for zone bank 0. total zones: [0,18,48,96,144,179] defined in TP.Measured_BPINOMINAL_Zones or VABR.py def BPINominalBHBZV2.
      },
   'ZONE_MASK_EXT'         : {
      'ATTRIBUTE'    : 'numZones',
      'DEFAULT'      : 24,
      24             : (0, 0),  # zone [0,2,6,12,18,23]
      31             : (0, 0),  # zone [0,3,8,16,24,30]
      60             : (0x801, 0x1),  # zone [0,6,16,32,48,59]
      120            : (0L, 1L),   # zone 0,12,32 for zone bank 0. total zones: [0,12,32,64,96,119] defined in TP.Measured_BPINOMINAL_Zones or VABR.py def BPINominalBHBZV2.
      150            : (0L, 256L),   # zone 0,15,40 for zone bank 0. total zones: [0,15,40,80,120,149] defined in TP.Measured_BPINOMINAL_Zones or VABR.py def BPINominalBHBZV2.
      180            : (1L, 0), # zone 0,18,48 for zone bank 0. total zones: [0,18,48,96,144,179] defined in TP.Measured_BPINOMINAL_Zones or VABR.py def BPINominalBHBZV2.
      },
   'MAX_ERR_RATE'          : -80,
   'MINIMUM'               : -17,
   'ZONE_POSITION'         : ZONE_POS,
   'WR_DATA'               : 0x00,
   'NUM_TRACKS_PER_ZONE'   : 10,
   'MAX_ITERATION'         : MaxIteration,  ## org is 24
   'RETRIES'               : 50,
   'SKIP_TRACK'            : {
      'ATTRIBUTE'    : 'FE_0245014_470992_ZONE_MASK_BANK_SUPPORT',
      'DEFAULT'      : 0,
      0              : 200,
      1              : 20, #Zone 94, 110, 179 may have less than 200 tracks, so skip_track cannot remain at 200.
   },
   'TLEVEL'                : 0,
   }

prm_PrePostOptiAudit_250_2 = {
   'test_num'              : 250,
   'prm_name'              : 'PrePostPhastOptiAudit_250 all zones',
   'spc_id'                : 4,
   #'timeout'               : 1000*numHeads,             # per Rich Dziallo, 2011MAR18
   'timeout'               : {
       'ATTRIBUTE'    : 'numZones',
       'DEFAULT'      : 60,
       60             : 1000*numHeads,             # per Rich Dziallo, 2011MAR18
       120            : 1000*numHeads*10,
       150            : 1000*numHeads*10,
       180            : 1000*numHeads*10,
      },
   'CWORD1'                : 0x0981,
   'CWORD2'                : 0x0000,
   'TEST_HEAD'             : 0x00FF,
   'ZONE_MASK'             : {
      'ATTRIBUTE'    : 'numZones',
      'DEFAULT'      : 24,
      24             : (0x00FF, 0xFFFF),
      31             : (0x7FFF, 0xFFFF),
      60             : (0xFFFF, 0xFFFF),
      },
   'ZONE_MASK_EXT'             : {
      'ATTRIBUTE'    : 'numZones',
      'DEFAULT'      : 24,
      24             : (0, 0),
      31             : (0, 0),
      60             : (0x0FFF, 0xFFFF),
      },
   'MAX_ERR_RATE'          : -80,
   'MINIMUM'               : -22,
   'ZONE_POSITION'         : ZONE_POS,
   'WR_DATA'               : 0x00,
   'NUM_TRACKS_PER_ZONE'   : 10,
   'MAX_ITERATION'         : MaxIteration,  ## org is 24
   'RETRIES'               : 50,
   'SKIP_TRACK'            : {
      'ATTRIBUTE'    : 'FE_0245014_470992_ZONE_MASK_BANK_SUPPORT',
      'DEFAULT'      : 0,
      0              : 200,
      1              : 20, #Zone 94, 110, 179 may have less than 200 tracks, so skip_track cannot remain at 200.
   },
   'TLEVEL'                : 0,
}

prm_SQZWRITE_250 = {
   'test_num'              : 250,
   'prm_name'              : 'SQZBPIC',
   'spc_id'                : 400,
   'timeout'               : 1000*numHeads,             # per Rich Dziallo, 2011MAR18
   'CWORD1'                : 0x4981, #0x4183, #having squeeze write
   'CWORD2'                : 0x1000, #turn on test track control
   'TEST_HEAD'             : 0x00FF,
   'ZONE_MASK'             : {
      'ATTRIBUTE'    : 'numZones',
      'DEFAULT'      : 24,
      24             : (0x00FF, 0xFFFF),
      31             : (0x7FFF, 0xFFFF),
      60             : (0xFFFF, 0xFFFF),
   },
   'ZONE_MASK_EXT'             : {
      'ATTRIBUTE'    : 'numZones',
      'DEFAULT'      : 24,
      24             : (0, 0),
      31             : (0, 0),
      60             : (0x0FFF, 0xFFFF),
   },
   'MAX_ERR_RATE'          : -90,
   'MINIMUM'               : -10, #no min spec
   'ZONE_POSITION'         : ZONE_POS,
   'WR_DATA'               : 0x00,
   'NUM_TRACKS_PER_ZONE'   : 10,
   'MAX_ITERATION'         : MaxIteration,  ## org is 24
   'RETRIES'               : 50,
   'SKIP_TRACK'            : {
      'ATTRIBUTE'    : 'FE_0245014_470992_ZONE_MASK_BANK_SUPPORT',
      'DEFAULT'      : 0,
      0              : 200,
      1              : 20, #Zone 94, 110, 179 may have less than 200 tracks, so skip_track cannot remain at 200.
   },
   'TLEVEL'                : 0,
   'NUM_SQZ_WRITES'        : 1, #num of adjacent writes
}

RunT250Pre_Channel = {
   'ATTRIBUTE'  : 'nextState',
   'DEFAULT'    : 1, # must run t250 pre_channel tuning
   'VAR_SPARES' : 0,
}
RunT250Post_Channel = {
   'ATTRIBUTE'  : 'nextState',
   'DEFAULT'    : 1, # must run t250 pre_channel tuning
   'VAR_SPARES' : 0,
}

if not testSwitch.RSS_TARGETLIST_GEN:
   if testSwitch.FE_0276349_228371_CHEOPSAM_SRC:  # list for marvell
       if testSwitch.USE_NEW_PROGRAMMABLE_TARGET_LIST_0727_2015:
           NPT_Targets_156 = [(4,7,0,0,0),(3,7,0,0,0),(3,8,0,0,0)]
       else:
           NPT_Targets_156 = [(4,7,0,0,0),(2,8,2,0,0),(3,7,1,0,0),(3,9,1,0,0),(5,10,0,0,0),(0,10,5,0,0)]


   else:
       NPT_Targets_156 = [(10,10,-1,0,3197),(10,12,4,0,254 ), (11,11,0,0,3198),
                      (11,13,0,0,3198), (12,12,0,0,3198), (13,13,0,0,3198),
                      (7,13,4,0,252),   (8,14,5,0,254),   (9,10,0,0,3198),
                      (9,12,1,0,252),   (9,12,2,0,252),   (9,12,3,0,254),
                      (9,13,3,0,252),   (9,9,0,0,3198),   (9,9,2,0,254),
                      (11,11,2,0,252),  (11,12,3,0,254),  (9,11,0,0,3198),
                      (11,11,3,0,254),  (10,12,0,0,3198), (8,12,0,0,3197),
                      (9,13,2,0,252),   (10,11,3,0,254),  (11,12,2,0,252),
                      (9,11,1,0,252)]
else:
   NPT_Targets_156 = [(13,14, 0, 0, 3198),    (8, 14, 5, 0, 3196),    (7, 13, 7, 0, 3196),
                      (10,12, 4, 0, 3196),    (8, 12, 6, 0, 3196),    (6, 14, 6, 0, 3196), (13,13, 0, 0, 3196),
                      (9, 13, 3, 0, 3196),    (6, 13, 6, 0, 3196),    (13,13,-1, 0, 3197), (11,13, 0, 0, 3198),
                      (9, 12, 3, 0, 3196),    (7, 13, 4, 0, 3196),    (6, 12, 6, 0, 3196), (12,12, 0, 0, 3198),
                      (9, 12, 2, 0, 3196),    (6, 12, 5, 0, 3196),    (12,12,-1, 0, 3197), (9, 12, 1, 0, 3196),
                      (5, 12, 5, 0, 3196),    (11,11, 0, 0, 3198),    (6, 11, 4, 0, 3196), (9, 9,  2, 0, 3196),
                      (7, 11, 2, 0, 3196),    (9, 10, 0, 0, 3198),    (10,10,-1, 0, 3197), (9, 9,  0, 0, 3198),
                      (5, 11,-2, 0, 3196),    (5, 11,-1, 0	,3197),    (5, 11,	0,0	,3197), (5,	11,	1, 0, 252 )	,
                      (5, 11, 2, 0	,252 ),    (5, 11, 3, 0	, 252)	,
                      (5, 11 ,4	,0	,252 )	,(	5 ,	11	,5	,0	,254 )	,(	5 ,	12	,-2	,0	,3196)	,
                      (5, 12 ,-1	,0	,3197)	,(	5 ,	12	,0	,0	,3197)	,(	5 ,	12	,1	,0	,252 )	,
                      (5, 12 ,2	,0	,252 )	,(	5 ,	12	,3	,0	,252 )	,(	5 ,	12	,4	,0	,252 )	,
                      (5, 12 ,5	,0	,254 )	,(	5 ,	13	,-2	,0	,3196)	,(	5 ,	13	,-1	,0	,3197)	,
                      (5, 13 ,0	,0	,3197)	,(	5 ,	13	,1	,0	,3197)	,(	5 ,	13	,2	,0	,252 )	,
                      (5	,13	,3	,0	,252 )	,(	5 ,	13	,4	,0	,252 )	,(	5 ,	13	,5	,0	,252 )	,
                      (5	,14	,-2	,0	,3196)	,(	5 ,	14	,-1	,0	,3197)	,(	5 ,	14	,0	,0	,3197)	,
                      (5	,14	,1	,0	,3197)	,(	5 ,	14	,2	,0	,252 )	,(	5 ,	14	,3	,0	,252 )	,
                      (5	,14	,4	,0	,252 )	,(	5 ,	14	,5	,0	,252 )	,(	6 ,	11	,-2	,0	,3196)	,
                      (6	,11	,-1	,0	,3197)	,(	6 ,	11	,0	,0	,3197)	,(	6 ,	11	,1	,0	,252 )	,
                      (6	,11	,2	,0	,252 )	,(	6 ,	11	,3	,0	,252 )	,(	6 ,	11	,4	,0	,254 )	,
                      (6	,11	,5	,0	,255 )	,(	6 ,	11	,6	,0	,255 )	,(	6 ,	12	,-2	,0	,3196)	,
                      (6	,12	,-1	,0	,3197)	,(	6 ,	12	,0	,0	,3197)	,(	6 ,	12	,1	,0	,252 )	,
                      (6	,12	,2	,0	,252 )	,(	6 ,	12	,3	,0	,252 )	,(	6 ,	12	,4	,0	,252 )	,
                      (6	,12	,5	,0	,254 )	,(	6 ,	12	,6	,0	,255 )	,(	6 ,	13	,-2	,0	,3196)	,
                      (6	,13	,-1	,0	,3197)	,(	6 ,	13	,0	,0	,3197)	,(	6 ,	13	,1	,0	,252 )	,
                      (6	,13	,2	,0	,252 )	,(	6 ,	13	,3	,0	,252 )	,(	6 ,	13	,4	,0	,252 )	,
                         (6	,13	,5	,0	,254 )	,(	6 ,	13	,6	,0	,254 )	,(	6 ,	14	,-2	,0	,3196)	,
                         (6	,14	,-1	,0	,3197)	,(	6 ,	14	,0	,0	,3197)	,(	6 ,	14	,1	,0	,252 )	,
                         (6	,14	,2	,0	,252 )	,(	6 ,	14	,3	,0	,252 )	,(	6 ,	14	,4	,0	,252 )	,
                         (6	,14	,5	,0	,252 )	,(	6 ,	14	,6	,0	,254 )	,(	7 ,	11	,-2	,0	,3197)	,
                         (7	,11	,-1	,0	,3197)	,(	7 ,	11	,0	,0	,3197)	,(	7 ,	11	,1	,0	,252 )	,
                         (7	,11	,2	,0	,252 )	,(	7 ,	11	,3	,0	,252 )	,(	7 ,	11	,4	,0	,254 )	,
                         (7	,11	,5	,0	,255 )	,(	7 ,	11	,6	,0	,255 )	,(	7 ,	12	,-2	,0	,3197)	,
                         (7	,12	,-1	,0	,3197)	,(	7 ,	12	,0	,0	,3197)	,(	7 ,	12	,1	,0	,252 )	,
                         (7	,12	,2	,0	,252 )	,(	7 ,	12	,3	,0	,252 )	,(	7 ,	12	,4	,0	,254 )	,
                         (7	,12	,5	,0	,254 )	,(	7 ,	12	,6	,0	,255 )	,(	7 ,	13	,-2	,0	,3196)	,
                         (7	,13	,-1	,0	,3197)	,(	7 ,	13	,0	,0	,3197)	,(	7 ,	13	,1	,0	,252 )	,
                         (7	,13	,2	,0	,252 )	,(	7 ,	13	,3	,0	,252 )	,(	7 ,	13	,4	,0	,252 )	,
                         (7	,13	,5	,0	,254 )	,(	7 ,	13	,6	,0	,255 )	,(	7 ,	14	,-2	,0	,3196)	,
                         (7	,14	,-1	,0	,3197)	,(	7 ,	14	,0	,0	,3197)	,(	7 ,	14	,1	,0	,252 )	,
                         (7	,14	,2	,0	,252 )	,(	7 ,	14	,3	,0	,252 )	,(	7 ,	14	,4	,0	,252 )	,
                         (7	,14	,5	,0	,254 )	,(	7 ,	14	,6	,0	,254 )	,(	8 ,	11	,-2	,0	,3197)	,
                         (8	,11	,-1	,0	,3197)	,(	8 ,	11	,0	,0	,3197)	,(	8 ,	11	,1	,0	,252 )	,
                         (8	,11	,2	,0	,252	)	,
                         (8	,11	,3	,0	,254 )	,(	8 ,	11	,4	,0	,254 )	,(	8 ,	11	,5	,0	,255 )	,
                         (8	,11	,6	,0	,255 )	,(	8 ,	12	,-2	,0	,3197)	,(	8 ,	12	,-1	,0	,3197)	,
                         (8	,12	,0	,0	,3197)	,(	8 ,	12	,1	,0	,252 )	,(	8 ,	12	,2	,0	,252 )	,
                         (8	,12	,3	,0	,252 )	,(	8 ,	12	,4	,0	,254 )	,(	8 ,	12	,5	,0	,255 )	,
                         (8	,12	,6	,0	,255 )	,(	8 ,	13	,-2	,0	,3197)	,(	8 ,	13	,-1	,0	,3197)	,
                         (8	,13	,0	,0	,3197)	,(	8 ,	13	,1	,0	,252 )	,(	8 ,	13	,2	,0	,252 )	,
                         (8	,13	,3	,0	,252 )	,(	8 ,	13	,4	,0	,252 )	,(	8 ,	13	,5	,0	,254 )	,
                         (8	,13	,6	,0	,255 )	,(	8 ,	14	,-2	,0	,3197)	,(	8 ,	14	,-1	,0	,3197)	,
                         (8	,14	,0	,0	,3197)	,(	8 ,	14	,1	,0	,252 )	,(	8 ,	14	,2	,0	,252 )	,
                         (8	,14	,3	,0	,252 )	,(	8 ,	14	,4	,0	,252 )	,(	8 ,	14	,5	,0	,254 )	,
                         (8	,14	,6	,0	,254 )	,(	9 ,	11	,-2	,0	,3197)	,(	9 ,	11	,-1	,0	,3197)	,
                         (9	,11	,0	,0	,3198)	,(	9 ,	11	,1	,0	,252 )	,(	9 ,	11	,2	,0	,252 )	,
                         (9	,11	,3	,0	,254 )	,(	9 ,	11	,4	,0	,254 )	,(	9 ,	11	,5	,0	,255 )	,
                         (9	,11	,6	,0	,255 )	,(	9 ,	12	,-2	,0	,3197)	,(	9 ,	12	,-1	,0	,3197)	,
                         (9	,12	,0	,0	,3197)	,(	9 ,	12	,1	,0	,252 )	,(	9 ,	12	,2	,0	,252 )	,
                         (9	,12	,3	,0	,254 )	,(	9 ,	12	,4	,0	,254 )	,(	9 ,	12	,5	,0	,255 )	,
                         (9	,12	,6	,0	,255 )	,(	9 ,	13	,-2	,0	,3197)	,(	9 ,	13	,-1	,0	,3197)	,
                         (9	,13	,0	,0	,3197)	,(	9 ,	13	,1	,0	,252 )	,(	9 ,	13	,2	,0	,252 )	,
                         (9	,13	,3	,0	,252 )	,(	9 ,	13	,4	,0	,254 )	,(	9 ,	13	,5	,0	,254 )	,
                         (9	,13	,6	,0	,255 )	,(	9 ,	14	,-2	,0	,3197)	,(	9 ,	14	,-1	,0	,3197)	,
                         (9	,14	,0	,0	,3197)	,(	9 ,	14	,1	,0	,252 )	,(	9 ,	14	,2	,0	,252 )	,
                         (9	,14	,3	,0	,252 )	,(	9 ,	14	,4	,0	,254 )	,(	9 ,	14	,5	,0	,254 )	,
                         (10	,11	,-2	,0	,3197)	,(	10,	11	,-1	,0	,3197)	,(	10,	11	,0	,0	,3198)	,
                         (10	,11	,1	,0	,252 )	,(	10,	11	,2	,0	,252 )	,(	10,	11	,3	,0	,254 )	,
                         (10	,11	,4	,0	,254 )	,(	10,	11	,5	,0	,255 )	,(	10,	11	,6	,0	,255 )	,
                         (10	,12	,-2	,0	,3197)	,(	10,	12	,-1	,0	,3197)	,(	10,	12	,0	,0	,3198)	,
                         (10	,12	,1	,0	,252 )	,(	10,	12	,2	,0	,252 )	,(	10,	12	,3	,0	,254 )	,
                         (10	,12	,4	,0	,254 )	,(	10,	12	,5	,0	,255 )	,(	10,	12	,6	,0	,255 )	,
                         (10	,13	,-2	,0	,3197)	,(	10,	13	,-1	,0	,3197)	,(	10,	13	,0	,0	,3197)	,
                         (10	,13	,1	,0	,252 )	,(	10,	13	,2	,0	,252 )	,(	10,	13	,3	,0	,252 )	,
                         (10	,13	,4	,0	,254 )	,(	10,	13	,5	,0	,254 )	,(	10,	14	,-2	,0	,3197)	,
                         (10	,14	,-1	,0	,3197)	,(	10,	14	,0	,0	,3197)	,(	10,	14	,1	,0	,252 )	,
                         (10	,14	,2	,0	,252 )	,(	10,	14	,3	,0	,252 )	,(	10,	14	,4	,0	,254 )	,
                         (11	,11	,-2	,0	,3197)	,(	11,	11	,-1	,0	,3197)	,(	11,	11	,0	,0	,3198)	,
                         (11	,11	,1	,0	,3198)	,(	11,	11	,2	,0	,252 )	,(	11,	11	,3	,0	,254 )	,
                         (11	,11	,4	,0	,254 )	,(	11,	11	,5	,0	,254 )	,(	11,	11	,6	,0	,255 )	,
                         (11	,12	,-2	,0	,3197)	,(	11,	12	,-1	,0	,3197)	,(	11,	12	,0	,0	,3198)	,
                         (11	,12	,1	,0	,252 )	,(	11,	12	,2	,0	,252 )	,(	11,	12	,3	,0	,254 )	,
                         (11	,12	,4	,0	,254 )	,(	11,	12	,5	,0	,254 )	,(	11,	13	,-2	,0	,3197)	,
                         (11	,13	,-1	,0	,3197)	,(	11,	13	,0	,0	,3198)	,(	11,	13	,1	,0	,252 )	,
                         (11	,13	,2	,0	,252 )	,(	11,	13	,3	,0	,254 )	,(	11,	13	,4	,0	,254 )	,
                         (11	,14	,-2	,0	,3197)	,(	11,	14	,-1	,0	,3197)	,(	11,	14	,0	,0	,3197)	,
                         (11	,14	,1	,0	,252 )	,(	11,	14	,2	,0	,252 )	,(	11,	14	,3	,0	,252 )]

##################### SEGMENTED BPIC #####################################
NUM_TRACKS_TO_MEASURE = 5

TARGET_MINIMUM_SOVA_BER = {
   'ATTRIBUTE' : 'WA_0309963_504266_504_LDPC_PARAM',
   'DEFAULT'   : 0,
   0           :  -2.50, # Need to align with lowest 2D VBAR Target SOVA
   1           :  -2.40, # Need to align with lowest 2D VBAR Target SOVA
}
TARGET_MINIMUM_SOVA_SQZ = {
   'ATTRIBUTE' : 'WA_0309963_504266_504_LDPC_PARAM',
   'DEFAULT'   : 0,
   0           :  -2.10,# Need to align with Squeeze BPI Target SOVA
   1           :  -1.90,# Need to align with Squeeze BPI Target SOVA
}
SEGMENTED_ZN_ADJUST = range(150)#range(31)
FSOW_ZN_ADJUST = [0,1,2] # Zones that will be backoff with FSOW Margin
OD_POSITION_TEST_ZONES = [0,1] # test zones for Position 0 
#MIN_SEGMENTED_BPIM_ADJUST = 0.015
MIN_SEGMENTED_BPIM_ADJUST = 1.0#(data collection) 0.02 # Backoff has to be bigger than this before being backoff, this is to cater for measurement variations

##################### VBAR #####################################

VbarNumMeasPerZone  = 1    # Leave this to 1 if multi-track measurement mode is enabled in T211 i.e. CWORD1=0x0004
                           # WARNING: Increasing this number to greater than 1 will increase test time dramatically

if testSwitch.FE_0334525_348429_INTERPOLATED_DEFAULT_TRIPLET:
   TZM_Def = {
      'ATTRIBUTE':'HGA_SUPPLIER',
      'DEFAULT': 'RHO',
      'RHO': {'ALL' : 0},
      'HWY': {'ALL' : 0},
      'TDK': {'OD' : 0},
      }
else:
   TZM_Def = {'ALL' : 0}

if testSwitch.FE_0114310_340210_ZONE_GRPS_4_TRIPLETS:
   TripletZoneMap = {
      'DEF'          : TZM_Def,
      'TI3448'       : TZM_Def,
      'TI3453'       : TZM_Def,
      'TI3945'       : TZM_Def,
      'TI3946'       : TZM_Def,
      'TI3948'       : TZM_Def,
      'TI5551'       : TZM_Def,
      'TI5552'       : TZM_Def,
      'TI7550'       : TZM_Def,
      'TI7551'       : TZM_Def,
      'LSI8831'      : TZM_Def,
      'LSI8832'      : TZM_Def,
      'LSI8834'      : TZM_Def,
      'LSI2731'      : TZM_Def,
      'LSI2935'      : TZM_Def,
      'LSI2958'      : TZM_Def,
      'LSI5230'      : TZM_Def,
      'LSI5231'      : TZM_Def,
      'LSI5830'      : TZM_Def,
      'LSI5235'      : TZM_Def,
      }
else:
   TripletZoneMap = {
      'N_USER_ZONES' : {
         'ATTRIBUTE'    : 'numZones',
         'DEFAULT'      : 17,
         17             : 17,
         24             : 24,
         31             : 31,
         60             : 60,
         },
      'DEF'          : TZM_Def,
      'TI3448'       : TZM_Def,
      'TI3453'       : TZM_Def,
      'TI3945'       : TZM_Def,
      'TI3946'       : TZM_Def,
      'TI3948'       : TZM_Def,
      'TI5551'       : TZM_Def,
      'TI5552'       : TZM_Def,
      'TI7550'       : TZM_Def,
      'TI7551'       : TZM_Def,
      'LSI8831'      : TZM_Def,
      'LSI8832'      : TZM_Def,
      'LSI8834'      : TZM_Def,
      'LSI2731'      : TZM_Def,
      'LSI2935'      : TZM_Def,
      'LSI2958'      : TZM_Def,
      'LSI5230'      : TZM_Def,
      'LSI5231'      : TZM_Def,
      'LSI5830'      : TZM_Def,
      'LSI5235'      : TZM_Def,
      }

BP5_PNs = [
           '100662060',
           '100662061',
           '100662064',
           '100662065',
           '100658203',
           '100658204',
           '100658205',
           '100658206',
           '100662062',
           '100662063',
           '100662066',
           '100662067',
           '100662074',
           '100662075',
           '100662076',
           '100662077',
]

##################### FAST 2D VBAR #####################################
Target_SFRs = {     # must in descending order
   'ATTRIBUTE' : 'WA_0309963_504266_504_LDPC_PARAM',
   'DEFAULT'   : 0,
   0           : [-2.55, -2.72, -2.92, -3.22, -3.50], #remove -2.2, -2.4 to save test time
   1           : [-2.40, -2.55, -2.72, -2.92, -3.22],
}
DefaultTargetSFRIndex = {
   'ATTRIBUTE' : 'WA_0309963_504266_504_LDPC_PARAM',
   'DEFAULT'   : 0,
   0           : 0,  # use -2.55
   1           : 1,  # use -2.55
}

BPI_Setting = [   63,    39,    28,    19,    12,     6,     3]
ADC_Saturation = { # 0.0
      'ATTRIBUTE':'FE_0258915_348429_COMMON_TWO_TEMP_CERT',
      'DEFAULT'  : 0,
      0 : 0.0,
      1 : 0.0025,
}
Minimum_Target_SFR_Idx = 0  # Minimum Pickable Index -2.55
TargetSFR_T211_BPIC = -2.92  # BPIC measurement Target SFR at VBAR_ZN, use to DC shift final BPIC as per linear fit and best SFR
Target_OTC_Bucket = 0.25
if testSwitch.FE_0276349_228371_CHEOPSAM_SRC:
   TPI_TLEVEL = 13  #for TPI Measurement iteration for Cheop channel
else:
   TPI_TLEVEL = 10  #for TPI Measurement iteration for karnak channel
   
if testSwitch.CHEOPSAM_LITE_SOC:
   TPI_TLEVEL = 10  #for TPI Measurement iteration for Cheoplite channel

SQZBPI_SER = { # F(x)=pow(10, 4-1.85)
   'ATTRIBUTE' : 'WA_0309963_504266_504_LDPC_PARAM',
   'DEFAULT'   : 0,
   0           :  74, # -2.13db # 79, # -2.10db # 89, # -2.05db, 100, #-2.0db
   1           : 104, # -1.98db #112, # -1.95db #125, # -1.90db, 141, #-1.85db
}

MAX_SQZBPI_MARGIN = 0.10 # Maximum Squeeze BPI Margin backoff
if testSwitch.FE_0254909_348085_VBAR_REDUCDED_TG:
   Default_TG_Coef = 1.8# used by Chengai
else:
   Default_TG_Coef = 2.0 # TG Multiplier from LCO
if testSwitch.FE_0293889_348429_VBAR_MARGIN_BY_OTCTP_INTERBAND_MARGIN:
   TG_Coef = {
   'ATTRIBUTE'      :'nextState',
   'DEFAULT'        : 'default',
   'default'        : 1.0, # No need for multiplier
   'VBAR_SET_ADC'   : Default_TG_Coef, # For ADC reporting
   'VBAR_ADC_REPORT': Default_TG_Coef, # For ADC reporting
   'VBAR_ADC_REPORT2': Default_TG_Coef, # For ADC reporting
   'VBAR_OC2'       : Default_TG_Coef, # For ADC Reporting
   }
else:
   TG_Coef = Default_TG_Coef

Markov_Gain = 0 # Aproximate Gain for Markov

#0 - select rd offset frm track guard/4
#1 - select rd offset frm otc measurement
#2 - select rd offset frm t211
RD_OFST_SEL_FMT_PICKER = {
   'ATTRIBUTE':'nextState',
   'DEFAULT': 'VBAR_ZN',
   'VBAR_ZN': {
      'ATTRIBUTE':'FAST_2D_VBAR_UNVISITED_ZONE',
      'DEFAULT': 0,
      0: testSwitch.VBAR_MARGIN_BY_OTC and 1 or 2,
      1: 2,#testSwitch.VBAR_MARGIN_BY_OTC and 1 or 2,
   },
   'VBAR_OTC3' : 1, #selectt rd offset frm otc bucket
   'VBAR_OTC2' : 1, #selectt rd offset frm otc bucket
   'VBAR_OTC' : 1, #select rd offset frm otc bucket
}
RD_OFST_SEL_OTC_PICKER = 2 #select rd offset frm t211

SPC_ID_BANDED_TPI_FMT_PICKER = {
   'ATTRIBUTE':'nextState',
   'DEFAULT': 'default',
   'default'   : 1,
   'VBAR_ZN'   : 100,
   'VBAR_FMT_PICKER': 100,
   'VBAR_OTC'  : 50,
   'VBAR_OTC2' : 200,
   'VBAR_OTC3' : 250,
   'VBAR_MARGIN' : 300,
   'VBAR_ADC_REPORT' : 300,
   'VBAR_ADC_REPORT2' : 400, # after OC2 Push
}
SPC_ID_BANDED_TPI_OTC_PICKER = 50

Measured_2D_Zones = {
   'ATTRIBUTE':'numZones',
   'DEFAULT': 150,
   120: [0, 12, 32, 64, 96, 118],
   150: {
      'ATTRIBUTE': 'FE_0274346_356688_ZONE_ALIGNMENT',
      'DEFAULT'  : 0,
      0 : [0, 16, 40, 80, 120, 148],
      1 : _2DVBAR_ZN,
   },
   180: [0, 18, 48, 96, 144, 178],
}
Measured_BPINOMINAL_Zones = {
   'ATTRIBUTE':'numZones',
   'DEFAULT': 150,
   60 : [0, 6, 16, 32, 48, 59],
   120: [0, 12, 32, 64, 96, 119],
   150: {
      'ATTRIBUTE': 'FE_0274346_356688_ZONE_ALIGNMENT',
      'DEFAULT'  : 0,
      0 : [0, 16, 40, 80, 120, 149],
      1 : BaseTestZone[150],
   },
   180: [0, 18, 48, 96, 144, 179],
}
Lump_2D_Zones = {
   'ATTRIBUTE':'numZones',
   'DEFAULT': 60,
   31: {0: [0, 1, 2, 3],
        6: [4, 5, 6, 7, 8],
       12: [9, 10, 11, 12, 13, 14, 15],
       18: [16, 17, 18, 19, 20],
       23: [21, 22, 23]},
   60: {0: range(4),
        6: range(4,12),
       16: range(12,24),
       32: range(24,40),
       48: range(40,54),
       58: range(54,60)},
}
Unvisited_Zones = {
   'ATTRIBUTE':'numZones',
   'DEFAULT': 150,
   60: range(1,60,2),
   120: range(1,120,2),
   150: {
      'ATTRIBUTE': 'FE_0274346_356688_ZONE_ALIGNMENT',
      'DEFAULT'  : 0,
      0 : range(1,150,2),
      1 : {'EQUATION' : "list(set(range(150))-set(TP.BPIMeasureZone))"},
   },
   180: range(1,180,2),
}

num_sqz_writes = 6

VBAR_measured_Zones = { #depend of unvisited zone switch
   'ATTRIBUTE':'numZones',
   'DEFAULT': 150,
   60 : list(set(range(60)) - set(Unvisited_Zones[60]) ),
   120 : list(set(range(120)) - set(Unvisited_Zones[120]) ),
   150 : {
      'ATTRIBUTE': 'FE_0274346_356688_ZONE_ALIGNMENT',
      'DEFAULT'  : 0,
         0 : list(set(range(150)) - set(Unvisited_Zones[150][0]) ),
         1 : BPIMeasureZone,
   },
   180 : list(set(range(180)) - set(Unvisited_Zones[180]) ),
}

# Active zones use to minimize CM Load
active_zones = {
   'ATTRIBUTE'          : 'nextState',
   'DEFAULT'            : 'ALL',
   'ALL'                : [],
   'BPINOMINAL'         : Measured_BPINOMINAL_Zones,
   'BPINOMINAL2'        : Measured_BPINOMINAL_Zones,
   'VBAR_BPI_XFER'      : VBAR_measured_Zones,
   'VBAR_ZN_2D'         : VBAR_measured_Zones,
   'VBAR_SET_ADC'       : VBAR_measured_Zones,
   'VBAR_MARGIN_SQZBPI' : VBAR_measured_Zones,
}


VCM_ST_PARM = {
   'ST_PARM_ON_VCM'  : {
      'CWORD3'    : 0x0200, #cword3 on linggi
      'INJ_AMPL2' : 200,
      'SET_OCLIM' : 1500, #noise injection causing write fault
   },
   'ST_PARM_OFF_VCM' : {
      'CWORD3'    : 0x0000,
      'INJ_AMPL2' : 0,
      'SET_OCLIM' : 1228,
   },
}

Overide_OTC_Margin = 0.07 # for use when OTC Margin can not measure
if testSwitch.FE_0293889_348429_VBAR_MARGIN_BY_OTCTP_INTERBAND_MARGIN or testSwitch.FE_0308542_348085_P_DESPERADO_3:
   Target_Intra_Track_Pitch = { # target narrower when interband is On
      'ATTRIBUTE' : 'WA_0309963_504266_504_LDPC_PARAM',
      'DEFAULT'   : 0,
      0           : 0.55,
      1           : 0.54,
   }
   Target_Inter_Track_Pitch = { # target narrower when interband is On
      'ATTRIBUTE' : 'WA_0309963_504266_504_LDPC_PARAM',
      'DEFAULT'   : 0,
      0           : 0.55,
      1           : 0.54,
   }
   TPIM_Intra_PushLimit = {
      'ATTRIBUTE' : 'WA_0309963_504266_504_LDPC_PARAM',
      'DEFAULT'   : 0,
      0           : -0.05,
      1           : -0.05,
   }
   TPIM_Inter_PushLimit = -0.05
else:
   Target_Intra_Track_Pitch = 0.585 # for use on intraband track spacing
   Target_Inter_Track_Pitch = 0.585 # for use on interband track spacing
   TPIM_Intra_PushLimit = -0.02

TPIM_Intra_PushLimit_Res = {
   'ATTRIBUTE' : 'numPhysHds',
   'DEFAULT'   : 2,
   2      : 0.02,
   3      : TPIM_Intra_PushLimit,
   4      : TPIM_Intra_PushLimit,
}
TPIM_Intra_PushLimit_MC = {
   'ATTRIBUTE' : 'numPhysHds',
   'DEFAULT'   : 2,
   2      : 0.00000001,
   3      : TPIM_Intra_PushLimit,
   4      : TPIM_Intra_PushLimit,
}
BPI_Squeeze_PushLimit = -0.05
BPI_Squeeze_PushLimit_Res = { # Push limit for Squeeze BPI for Resonance Margin
   'ATTRIBUTE' : 'numPhysHds',
   'DEFAULT'   : 2,
   2      : -0.03,
   3      : BPI_Squeeze_PushLimit,
   4      : BPI_Squeeze_PushLimit,
}
BPI_Squeeze_PushLimit_MC = { # Push limit for Squeeze BPI for MC Zones
   'ATTRIBUTE' : 'numPhysHds',
   'DEFAULT'   : 2,
   2      : 0.015,
   3      : BPI_Squeeze_PushLimit,
   4      : BPI_Squeeze_PushLimit,
}
MS_WFT = 0.03 # WFT Threshold to be used in MS Zones 
MC_WFT = { # WFT Threshold to be used in MC Zones
   'ATTRIBUTE'             : 'nextState',
   'DEFAULT'               : 'VBAR_FMT_PICKER',
   'VBAR_FMT_PICKER'       : 0.04,
   'VBAR_SET_ADC'          : MS_WFT, # use same as mainstore zones when evaluating margin
   'VBAR_MARGIN_RLOAD'     : MS_WFT, # use same as mainstore zones when evaluating margin
}
Target_UMP_Track_Pitch = 0.80 # for use on interband track spacing
ParitySec_perTrack = 2 # number of parity sectors per track for parity allocation

# For TPIM SOVA Transfer
TPIM_TARGET_SOVA = -1.8  # Target SQZ SOVA BER for the TPIM
TPIM_FIXED_SLOPE = 3.0 # user provided slope to be used for SQZ SOVA BER vs TPIM calculation

###### VBAR_OTC ######
InsertZn_Gap = 0.0544 # gap limit to trigger additional zone measurement 0.544u" * 10%

#######################################
#
#  Multimatrix triplet control rules
#
#######################################
mmt_testzonelist = [0,35,75,115,149]
mmt_subzonelist = [0, 149]
mmt_use_default_OSD = 0 # Flag to use default OSD or not.
mmt_osd_tuninglist = range(28,3,-4) # OSD tuning list in reverse order. [28, 24, 20, 16, 12, 8, 4]
mmt_fixed_osa = 20
mmt_osa_tuninglist = range(4,30,6)
mmt_iwlist = range(105,6,-7) # begin at 2/3 of 128, which is 84, as requested by RSS #in reverse loop
mmt_iwstep = abs(mmt_iwlist[0] - mmt_iwlist[1])
mmt_ow_iwstep = 2
mmt_ow_start_iw = 7 # Loop Iw from 7 onwards, all to way to Iw=105 until OW=20dB is achieved. 
mmt_ow_spec = 20 # To achieve a min of 20dB for Over Write (T61). 
mmt_ow_search_size = 3 # No. of consecutive deltaAvg to detect OW kp is found.
mmt_ow_deltaStop = 1 # If there are 3 (mmt_ow_search_size) consecutive deltaAvg < 1, stop ow search.
mmt_deltaBERStop = { # T250 knee point rate of change
   'ATTRIBUTE' : 'HGA_SUPPLIER',
   'DEFAULT'   : 'HWY',
   'TDK'       : 0.10,
   'HWY'       : 0.10,
   'RHO'       : 0.15,
}
mmt_osdIwKPBERCheck = 0.08 # OSD T250 IwKP BER check. Pick the OSD with the highest IwKP BER if delta > 0.8.
mmt_t250_max_err_rate = -70 # T250 MAX_ERR_RATE, for test time reduction.
mmt_dc_start_value = 0  # T51 dc start value
mmt_n_writes = 1000     # T51 default number of writes (CENTER_TRACK_WRITES).
mmt_dc_plus_value = { # T51 Iw to be used for the second 2 point stress.
   'ATTRIBUTE' : 'HGA_SUPPLIER',
   'DEFAULT'   : 'HWY',
   'TDK'       : 35,
   'HWY'       : 35,
   'RHO'       : 14,
}
mmt_dc_plus_delta_check = 0.09 # DC plus - DC @ 0 delta check. 
mmt_oamincap = 4 # Osa & Osd min cap for curve fitting safe guard.
mmt_oamaxcap = 31 # Osa & Osd max cap for curve fitting safe guard.
mmt_iwmaxcap = 127 #iw max cap for curve fitting safe guard.


#######################################
#
#  CERT_BASED_ATB triplet control rules
#
#######################################
testzonelist = [0,149]
iwlist = range(0,127,10)
osa_tuninglist = range(0,31,4) 
osd_tuninglist = [3,16,29]
n_writes = 3000     # T51 default number of writes (CENTER_TRACK_WRITES).
band_size = 5       # T51 BAND_SIZE reduce from 11 to 5 for test time reduction purpose.
tlevel = 200        # T51 TLEVEL increase from 40 to 200 for better accuracy.
cword2 = 0x6        # To enable triplet update within T51.

# Table Format: PreAmp Type: [list of write triplets -- can be any number of triplets]
# WP Triplet Format: (Iw, Ovs, Ovd) -> (Write Current, Overshoot, Overshoot Duration)
VbarWpTable = {
   # Global Setting, For Factory Maintenance
   # 'ATTRIBUTE' : ('USE_HSA_WAFER_CODE_ATTR', 'FE_0317559_305538_P_USE_MEDIA_PART_NUM'),
   # 'DEFAULT'   : (0,0),
   # (0,0)       : {
   #    'ATTRIBUTE':'HGA_SUPPLIER',
   #    'DEFAULT': 'RHO',
   #    'RHO':  {
   #       'ATTRIBUTE'       : 'IS_2D_DRV',
   #       'DEFAULT'         : 0,
   #       0 : { #1Disc Drives
   #          'LSI5830'   : {'ALL': [(41, 20, 28)] * 8,},
   #          'TI7551'    : {'ALL': [(36, 14, 28)] * 8,},
   #          },
   #       1 : { #2Disc Drives
   #          'LSI5830'   : {'ALL': [(38, 20, 22)] * 8,},
   #          'TI7551'    : {'ALL': [(36, 14, 28)] * 8,},
   #          },
   #       },
   #    'HWY':  {
   #       'ATTRIBUTE'       : 'IS_2D_DRV',
   #       'DEFAULT'         : 0,
   #       0 : {
   #          'LSI5830'   : {'ALL': [(48, 20, 26)] * 8,},
   #          'TI7551'    : {'ALL': [(55, 12, 26)] * 8,},
   #          },
   #       1 : {
   #          'LSI5830'   : {'ALL': [(55, 18, 26)] * 8,},
   #          'TI7551'    : {'ALL': [(62, 10, 26)] * 8,},
   #          },
   #       },
   #    'TDK':  {
   #       'LSI5830'   : {'ALL': [(95, 12, 22)] * 8,}, 
   #       'TI7551'    : {'ALL': [(95, 12, 8)] * 8,}, 
   #       },
   #    },
   # # For Local Setting, Defined further by Media Type
   # (0,1)       : {
   #    'ATTRIBUTE':'HGA_SUPPLIER',
   #    'DEFAULT': 'RHO',
   #    'RHO':  {
   #       'ATTRIBUTE'       : 'IS_2D_DRV',
   #       'DEFAULT'         : 0,
   #       0 : { #1Disc Drives
   #          'LSI5830'   : {
   #             'ATTRIBUTE'       : 'MediaType',
   #             'DEFAULT'         : 'R7.0',
   #             'R7.0'            : {'ALL': [(41, 20, 28)] * 8,},
   #             'C677'            : {'ALL': [(41, 20, 28)] * 8,},
   #             },
   #          'TI7551'    : {
   #             'ATTRIBUTE'       : 'MediaType',
   #             'DEFAULT'         : 'R7.0',
   #             'R7.0'            : {'ALL': [(36, 14, 28)] * 8,},
   #             'C677'            : {'ALL': [(36, 14, 28)] * 8,},
   #             },
   #          },
   #       1 : { #2Disc Drives
   #          'LSI5830'   : {
   #             'ATTRIBUTE'       : 'MediaType',
   #             'DEFAULT'         : 'R7.0',
   #             'R7.0'            : {'ALL': [(38, 20, 22)] * 8,},
   #             'C677'            : {'ALL': [(38, 20, 22)] * 8,},
   #             },
   #          'TI7551'    : {
   #             'ATTRIBUTE'       : 'MediaType',
   #             'DEFAULT'         : 'R7.0',
   #             'R7.0'            : {'ALL': [(36, 14, 28)] * 8,},
   #             'C677'            : {'ALL': [(36, 14, 28)] * 8,},
   #             },
   #          },
   #       },
   #    'HWY':  {
   #       'ATTRIBUTE'       : 'IS_2D_DRV',
   #       'DEFAULT'         : 0,
   #       0 : { #1Disc Drives
   #          'LSI5830'   : {
   #             'ATTRIBUTE'       : 'MediaType',
   #             'DEFAULT'         : 'R7.0',
   #             'R7.0'            : {'ALL': [(48, 20, 26)] * 8,},
   #             'C677'            : {'ALL': [(48, 20, 26)] * 8,},
   #             },
   #          'TI7551'    : {
   #             'ATTRIBUTE'       : 'MediaType',
   #             'DEFAULT'         : 'R7.0',
   #             'R7.0'            : {'ALL': [(55, 12, 26)] * 8,},
   #             'C677'            : {'ALL': [(55, 12, 26)] * 8,},
   #             },
   #          },
   #       1 : { #2Disc Drives
   #          'LSI5830'   : {
   #             'ATTRIBUTE'       : 'MediaType',
   #             'DEFAULT'         : 'R7.0',
   #             'R7.0'            : {'ALL': [(55, 18, 26)] * 8,},
   #             'C677'            : {'ALL': [(55, 18, 26)] * 8,},
   #             },
   #          'TI7551'    : {
   #             'ATTRIBUTE'       : 'MediaType',
   #             'DEFAULT'         : 'R7.0',
   #             'R7.0'            : {'ALL': [(62, 10, 26)] * 8,},
   #             'C677'            : {'ALL': [(62, 10, 26)] * 8,},
   #             },
   #          },
   #       },
   #    'TDK':  {
   #       'LSI5830'   : {
   #          'ATTRIBUTE'       : 'MediaType',
   #          'DEFAULT'         : 'R7.0',
   #          'R7.0'            : {'ALL': [(48, 20, 26)] * 8,}, # 19-Nov-2015
   #          'R8.0'            : {'ALL': [(48, 20, 26)] * 8,}, # 19-Nov-2015
   #          'C572'            : {'ALL': [(48, 20, 26)] * 8,}, # 19-Nov-2015
   #          },
   #       'TI7551'    : {'ALL': [(55, 12,  8)] * 8,},
   #       },
   #    },
   # # For Local Setting, Defined further by Media Type and HSA Wafer Code
   # (1,1)       : { # 24-Nov-15 Updated Iw/OSA
      'ATTRIBUTE':'HGA_SUPPLIER',
      'DEFAULT': 'RHO',
      'RHO':  {
         # 'DEF'       :  {'ALL': [(7, 4, 6), (7, 4, 6), (7, 4, 6), (7, 4, 6), (7, 4, 6), (7, 4, 6), (7, 4, 6), (7, 4, 6),],},
         'LSI5235'   : {'ALL': [(12, 8, 8)] * 8,}, # HMR
         'LSI5830'   : {
            'ATTRIBUTE'       : ('MediaType', 'HSA_WAFER_CODE'),
            'DEFAULT'         : ('R7.0', 'NL2'), 
            ('R5.1', 'OG8')   : {'ALL': [(41, 20, 16)] * 8,}, # 23-Apr-15
            ('R6.4', 'OG8')   : {'ALL': [(41, 20, 16)] * 8,}, # 23-Apr-15
            ('R5.1', 'NG8')   : {'ALL': [(41, 20, 16)] * 8,}, # 23-Apr-15
            ('R5.1', 'O2Q')   : {'ALL': [(41, 20, 16)] * 8,}, # 23-Apr-15 copied from RHO + LSI + R5.1 + OG8 # 24-Nov-15
            ('R5.1', 'N5T')   : {'ALL': [(41, 20, 18)] * 8,}, # 4-May-15
            ('R5.1', 'OT4')   : {'ALL': [(41, 20, 18)] * 8,}, # copied from R7+OT4
            ('R5.1', 'NT4')   : {'ALL': [(41, 20, 26)] * 8,}, # 5-Jun-15
            ('R5.1', 'N4Z')   : {
               'ATTRIBUTE' : 'IS_2D_DRV',
               'DEFAULT'   : 0,
               0           : {'ALL': [(41, 20, 18)] * 8,}, # 25-Jun-15
               1           : {'ALL': [(41, 20, 22)] * 8,}, # 16-Jun-15
               },
            ('R6.4', 'NT4')   : {'ALL': [(41, 20, 26)] * 8,}, # 24-Jul-15
            ('R6.4', 'OT4')   : {'ALL': [(41, 20, 22)] * 8,}, # 26-Jul-15
            ('R7.0', 'OT4')   : {'ALL': [(41, 20, 18)] * 8,}, # 01-Sep-15
            ('R7.0', 'NT4')   : {'ALL': [(41, 20, 20)] * 8,}, # 19-Sep-15,RW2D 
            ('R7.0', 'NL2')   : {
               'ATTRIBUTE' : 'IS_2D_DRV',
               'DEFAULT'   : 0,
               0           : {'ALL': [(41, 20, 28)] * 8,}, # 23-Sep-15
               1           : {'ALL': [(38, 20, 22)] * 8,}, # 09-Dec-15 2D, Jose c.o Andy
               },
            ('R7.0', 'PD7')   : { # copied from NL2
               'ATTRIBUTE' : 'IS_2D_DRV',
               'DEFAULT'   : 0,
               0           : {'ALL': [(41, 20, 28)] * 8,}, # 23-Sep-15
               1           : {'ALL': [(38, 20, 22)] * 8,}, # 09-Dec-15 2D, Jose c.o Andy
               },
            ('R8.0', 'NL2')   : {
               'ATTRIBUTE' : 'IS_2D_DRV',
               'DEFAULT'   : 0,
               0           : {'ALL': [(41, 20, 28)] * 8,},
               1           : {'ALL': [(38, 20, 22)] * 8,}, # 09-Dec-15 2D, Jose c.o Andy
               },		 
            ('R8.0', 'PD7')   : {
               'ATTRIBUTE' : 'IS_2D_DRV',
               'DEFAULT'   : 0,
               0           : {'ALL': [(41, 20, 28)] * 8,}, # 20-Nov-2015, 1D 
               1           : {'ALL': [(38, 20, 28)] * 8,}, # 09-Dec-15 2D, Jose c.o Andy
               },
            ('R10',  'PD7')   : { # copied from R8
               'ATTRIBUTE' : 'IS_2D_DRV',
               'DEFAULT'   : 0,
               0           : {'ALL': [(38, 20, 28)] * 8,}, # 04-Mar-2016
               1           : {'ALL': [(38, 20, 28)] * 8,}, # 12-Feb-2016
               },
            ('C677', 'OT4')   : {'ALL': [(41, 20, 18)] * 8,}, # 26-Aug-15
            ('C677', 'NT4')   : {'ALL': [(41, 20, 24)] * 8,}, # 19-Sep-15,RW2D
            ('C677', 'NL2')   : {
               'ATTRIBUTE' : 'IS_2D_DRV',
               'DEFAULT'   : 0,
               0           : {'ALL': [(41, 20, 28)] * 8,}, # 24-Sep-15
               1           : {'ALL': [(38, 20, 22)] * 8,}, # 09-Dec-15 2D, Jose c.o Andy
               },
            ('C677', 'PD7')   : { # copied from NL2
               'ATTRIBUTE' : 'IS_2D_DRV',
               'DEFAULT'   : 0,
               0           : {'ALL': [(41, 20, 28)] * 8,}, # 24-Sep-15
               1           : {'ALL': [(38, 20, 22)] * 8,}, # 09-Dec-15 2D, Jose c.o Andy
               },
            ('C572', 'PD7')   : { # copied from C677+NL2
               'ATTRIBUTE' : 'IS_2D_DRV',
               'DEFAULT'   : 0,
               0           : {'ALL': [(41, 20, 28)] * 8,}, # 24-Sep-15
               1           : {'ALL': [(38, 20, 22)] * 8,}, # 09-Dec-15 2D, Jose c.o Andy
               },
            ('C655', 'NL2'): {'ALL': [(41, 20, 28)] * 8,}, # 29-Oct-15
            ('C572', 'NL2'): {'ALL': [(38, 22, 28)] * 8,}, # 11-Jan_16 2D.
         },
         'TI7551'    : {
            'ATTRIBUTE'       : ('MediaType', 'HSA_WAFER_CODE'),
            'DEFAULT'         : ('R7.0', 'NL2'),
            ('R5.1', 'O2Q')   : {'ALL': [(36, 14, 28)] * 8,}, # 20-Apr-15
            ('R5.1', 'NG8')   : {'ALL': [(36, 14, 28)] * 8,}, # 20-Apr-15
            ('R5.1', 'N5T')   : {'ALL': [(36, 14, 28)] * 8,}, # 20-Apr-15
            ('R5.1', 'OG8')   : {'ALL': [(36, 14, 28)] * 8,}, # 15-May-15
            ('R5.1', 'OT4')   : {'ALL': [(36, 14, 28)] * 8,}, # copied from R7+OT4
            ('R5.1', 'NT4')   : {'ALL': [(36, 14, 28)] * 8,}, # 23-Jun-15
            ('R5.1', 'N4Z')   : {'ALL': [(36, 14, 28)] * 8,}, # 20-Jul-15
            ('R6.4', 'OT4')   : {
               'ATTRIBUTE' : 'IS_2D_DRV',
               'DEFAULT'   : 0,
               0           : {'ALL': [(36, 14, 26)] * 8,}, # 14-Aug-15
               1           : {'ALL': [(36, 14, 28)] * 8,}, # 28-Aug-15
               },
            ('R6.4', 'NT4')   : {'ALL': [(36, 14, 28)] * 8,}, # 08-Sep-15,RW2D
            ('R7.0', 'OT4')   : {'ALL': [(36, 14, 28)] * 8,}, # 18-Sep-15
            ('R7.0', 'NT4')   : {'ALL': [(36, 14, 26)] * 8,}, # 19-Sep-15,RW2D
            ('R7.0', 'NL2')   : {'ALL': [(36, 14, 28)] * 8,}, # 10-Oct-15 1D, 19-Oct-15 2D same as 1D
            ('R7.0', 'PD7')   : {'ALL': [(36, 14, 28)] * 8,}, # copied from NL2
            ('R8.0', 'NL2')   : {'ALL': [(36, 14, 28)] * 8,}, # 18-Nov-15 2D
            ('R8.0', 'PD7')   : {'ALL': [(36, 14, 28)] * 8,}, # 23-Nov-2015
            ('R10',  'PD7')   : {'ALL': [(36, 14, 28)] * 8,}, # 04-Mar-2016
            ('C677', 'OT4')   : {'ALL': [(36, 14, 28)] * 8,}, # 18-Sep-15
            ('C677', 'NT4')   : {'ALL': [(36, 14, 26)] * 8,}, # 19-Sep-15
            ('C677', 'NL2')   : {'ALL': [(36, 14, 28)] * 8,}, # 27-Oct-15
            ('C677', 'PD7')   : {'ALL': [(36, 14, 28)] * 8,}, # 09-Dec-15 2D, Jose c.o Andy
            ('C655', 'NL2')   : {'ALL': [(36, 14, 28)] * 8,}, # 29-Oct-15
            ('C572', 'PD7')   : {'ALL': [(36, 14, 28)] * 8,}, # 15-Jan-16
         },
      },

      'HWY':  {
         # 'DEF'       :  {'ALL':[(13, 4 ,3), (13, 4, 3), (13, 9, 11), (6, 4, 3), (6, 3, 3), (5, 3, 3), (4, 3, 3), (3, 3, 3),],},
         'LSI5830'   : {
            'ATTRIBUTE'       : ('MediaType', 'HSA_WAFER_CODE'),
            'DEFAULT'         : ('R7.0', '5A5J0'),
            ('R5.1', '4A4C5') : {'ALL': [(48, 20, 16)] * 8,}, # 6-Apr-15
            ('R5.1', '4AHDD') : {'ALL': [(48, 20, 16)] * 8,}, # copied from 4A4C5
            ('R5.1', '4A60B') : {'ALL': [(48, 20, 16)] * 8,}, # copied from 4A4C5
            ('R5.1', '4A3C0') : {'ALL': [(48, 20, 16)] * 8,}, # copied from HWY + LSI + R5.1 + 4A4C5
            ('R5.1', '4AF1F') : {'ALL': [(48, 20, 16)] * 8,}, # 17-Mar-15
            ('R5.1', '4AH63') : {'ALL': [(48, 20, 16)] * 8,}, # copy 4AF1F
            ('R5.1', '4C6JH') : {'ALL': [(48, 20, 20)] * 8,}, # 13-Jul-15
            ('R5.1', '4C430') : {'ALL': [(48, 20, 20)] * 8,}, # 8-Jun-15
            ('R6.4', '4C430') : {'ALL': [(48, 20, 20)] * 8,}, # 24-Jul-15
            ('R6.4', '5A2HH') : {
               'ATTRIBUTE' : 'IS_2D_DRV',
               'DEFAULT'   : 0,
               0           : {'ALL': [(48, 20, 28)] * 8,}, # 11-Aug-15
               1           : {'ALL': [(48, 20, 22)] * 8,}, # 02-Sep-15 -> 18-Sep-15
               },
            ('R7.0', '5A2HH') : {
               'ATTRIBUTE' : 'IS_2D_DRV',
               'DEFAULT'   : 0,
               0           : {'ALL': [(48, 20, 26)] * 8,}, # 18-Sep-15
               1           : {'ALL': [(55, 18, 22)] * 8,}, # 09-Dec-15 2D, Jose c.o Andy
               },
            ('R7.0', '5A3J2') : {'ALL': [(48, 20, 20)] * 8,}, # 22-Sep-15
            ('R8.0', '5A3J2') : {'ALL': [(48, 20, 20)] * 8,}, # copied from R7 + 5A3J2
            ('R7.0', '5A2HG') : {
               'ATTRIBUTE' : 'IS_2D_DRV',
               'DEFAULT'   : 0,
               0           : {'ALL': [(48, 20, 20)] * 8,}, # 23-Sep-15 1D, 12-Oct-15 2D same as 1D
               1           : {'ALL': [(55, 18, 20)] * 8,}, # 09-Dec-15 2D, Jose c.o Andy
               },
            ('R7.0', '5ABG5') : {'ALL': [(48, 20, 26)] * 8,}, # 27-Oct-15
            ('R8.0', '5ABG5') : {'ALL': [(48, 20, 26)] * 8,}, # copied from R7 + 5ABG5
            ('R7.0', '5A5J0') : {          
               'ATTRIBUTE' : 'IS_2D_DRV',
               'DEFAULT'   : 0,
               0           : {'ALL': [(48, 20, 26)] * 8,}, # 04-Nov-15 1D, 12-Nov-15 2D same as 1D
               1           : {'ALL': [(55, 18, 26)] * 8,}, # 09-Dec-15 2D, Jose c.o Andy
               },
            ('R8.0', '5A5J0') : {          
               'ATTRIBUTE' : 'IS_2D_DRV',
               'DEFAULT'   : 0,
               0           : {'ALL': [(48, 20, 26)] * 8,}, # copy
               1           : {'ALL': [(55, 18, 26)] * 8,}, # 09-Dec-15 2D, Jose c.o Andy
               },
            ('R7.0', '5A99G') : {'ALL': [(55, 18, 26)] * 8,}, # 09-Dec-15 2D, Jose c.o Andy
            ('R8.0', '5A99G') : {'ALL': [(55, 18, 26)] * 8,}, # 09-Dec-15 2D, Jose c.o Andy
            ('R8.0', '5A9BJ') : {'ALL': [(48, 20, 26)] * 8,}, # copy
            ('R8.0', '5F057') : {'ALL': [(48, 20, 26)] * 8,}, # 19-Nov-2015
            ('R8.0', '4C677') : {'ALL': [(48, 20, 26)] * 8,}, # 23-Nov-2015
            ('R10',  '5A99G') : { # copied from R8
               'ATTRIBUTE' : 'IS_2D_DRV',
               'DEFAULT'   : 0,
               0           : {'ALL': [(48, 20, 26)] * 8,}, # copy
               1           : {'ALL': [(55, 18, 26)] * 8,}, # 09-Dec-15 2D, Jose c.o Andy
               },
            ('R10',  '5A5J0') : { # copied from R8
               'ATTRIBUTE' : 'IS_2D_DRV',
               'DEFAULT'   : 0,
               0           : {'ALL': [(48, 20, 26)] * 8,}, # copy
               1           : {'ALL': [(55, 18, 26)] * 8,}, # 09-Dec-15 2D, Jose c.o Andy
               },
            ('C655', '4C677') : {'ALL': [(48, 20, 26)] * 8,}, # 23-Nov-2015
            ('C677', '5A2HH') : {
               'ATTRIBUTE' : 'IS_2D_DRV',
               'DEFAULT'   : 0,
               0           : {'ALL': [(48, 20, 26)] * 8,}, # 19-Sep-15
               1           : {'ALL': [(55, 18, 26)] * 8,}, # 09-Dec-15 2D, Jose c.o Andy
               },
            ('C677', '5A3J2') : {
               'ATTRIBUTE' : 'IS_2D_DRV',
               'DEFAULT'   : 0,
               0           : {'ALL': [(48, 20, 20)] * 8,}, # 19-Sep-15
               1           : {'ALL': [(48, 20, 26)] * 8,}, # 24-Sep-15
               },
            ('C677', '5A2HG') : {
               'ATTRIBUTE' : 'IS_2D_DRV',
               'DEFAULT'   : 0,
               0           : {'ALL': [(48, 20, 20)] * 8,}, # 7-oct-15, 12-Oct-15 2D same as 1D
               1           : {'ALL': [(55, 18, 20)] * 8,}, # 09-Dec-15 2D, Jose c.o Andy
               },
            ('C677', '5ABG5') : {'ALL': [(48, 20, 26)] * 8,}, # 27-oct-15
            ('C677', '5A5J0') : {
               'ATTRIBUTE' : 'IS_2D_DRV',
               'DEFAULT'   : 0,
               0           : {'ALL': [(48, 20, 26)] * 8,}, # 04-Nov-15
               1           : {'ALL': [(55, 18, 26)] * 8,}, # 09-Dec-15 2D, Jose c.o Andy
               },
            ('C677', '5A99G') : {
               'ATTRIBUTE' : 'IS_2D_DRV',
               'DEFAULT'   : 0,
               0           : {'ALL': [(48, 20, 26)] * 8,}, # 24-Nov-2015
               1           : {'ALL': [(55, 18, 26)] * 8,}, # 09-Dec-15 2D, Jose c.o Andy
               },
            ('C448', '5A3J2') : {'ALL': [(48, 20, 24)] * 8,}, # 25-Sep-15
            ('C572', '5AA99') : {'ALL': [(55, 18, 26)] * 8,}, # 11-Jan_16 2D.	
            ('C572', '5A99G') : {'ALL': [(55, 18, 26)] * 8,}, # 11-Jan_16 2D POR1.				
         },
         'TI7551'    : {
            'ATTRIBUTE'       : ('MediaType', 'HSA_WAFER_CODE'),
            'DEFAULT'         : ('R7.0', '5A5J0'),
            ('R5.1', '4A4C5') : {'ALL': [(55, 12, 18)] * 8,}, # 30-Apr-15
            ('R5.1', '4AHDD') : {'ALL': [(55, 12, 18)] * 8,}, # copied from 4A4C5
            ('R5.1', '4A60B') : {'ALL': [(55, 12, 28)] * 8,}, # 10-Jun-15
            ('R5.1', '4C6JH') : {'ALL': [(55, 12, 28)] * 8,}, # 18-Jun-15
            ('R5.1', '4C430') : {'ALL': [(55, 12, 26)] * 8,}, # 19-Jun-15
            ('R6.4', '4C430') : {'ALL': [(55, 12, 28)] * 8,}, # 14-Aug-15
            ('R7.0', '5A2HH') : {
               'ATTRIBUTE' : 'IS_2D_DRV',
               'DEFAULT'   : 0,
               0           : {'ALL': [(55, 12, 26)] * 8,}, # 19-Sep-15
               1           : {'ALL': [(62, 10, 28)] * 8,}, # 09-Dec-15 2D, Jose c.o Andy
               },   
            ('R7.0', '5A3J2') : {'ALL': [(55, 12, 26)] * 8,}, # 25-Sep-15
            ('R8.0', '5ABG5') : {'ALL': [(55, 12, 26)] * 8,}, # copied from R7 + 5A3J2
            ('R7.0', '5A2HG') : {
               'ATTRIBUTE' : 'IS_2D_DRV',
               'DEFAULT'   : 0,
               0           : {'ALL': [(55, 12, 28)] * 8,}, # 02-Nov-15, 2D
               1           : {'ALL': [(62, 10, 28)] * 8,}, # 09-Dec-15 2D, Jose c.o Andy
               },   
            ('R7.0', '5A5J0') : {
               'ATTRIBUTE' : 'IS_2D_DRV',
               'DEFAULT'   : 0,
               0           : {'ALL': [(55, 12, 26)] * 8,}, # 24-Nov-15
               1           : {'ALL': [(62, 10, 28)] * 8,}, # 09-Dec-15 2D, Jose c.o Andy
               },
            ('R8.0', '5A5J0') : {
               'ATTRIBUTE' : 'IS_2D_DRV',
               'DEFAULT'   : 0,
               0           : {'ALL': [(55, 12, 26)] * 8,}, # copy
               1           : {'ALL': [(62, 10, 28)] * 8,}, # 09-Dec-15 2D, Jose c.o Andy
               },
            ('R7.0', '5A99G') : {'ALL': [(62, 10, 26)] * 8,}, # 09-Dec-15 2D, Jose c.o Andy
            ('R8.0', '5A99G') : {
               'ATTRIBUTE' : 'IS_2D_DRV',
               'DEFAULT'   : 0,
               0           : {'ALL': [(55, 12, 26)] * 8,}, # 23-Nov-15 2D
               1           : {'ALL': [(62, 10, 26)] * 8,}, # 09-Dec-15 2D, Jose c.o Andy
               },
            ('R8.0', '5A9BJ') : {'ALL': [(55, 12, 26)] * 8,}, # copy
            ('R10',  '5A99G') : { # copied from R8
               'ATTRIBUTE' : 'IS_2D_DRV',
               'DEFAULT'   : 0,
               0           : {'ALL': [(55, 12, 26)] * 8,}, # copy
               1           : {'ALL': [(62, 10, 28)] * 8,}, # 09-Dec-15 2D, Jose c.o Andy
               },
            ('R10',  '5A5J0') : { # copied from R8
               'ATTRIBUTE' : 'IS_2D_DRV',
               'DEFAULT'   : 0,
               0           : {'ALL': [(55, 12, 26)] * 8,}, # copy
               1           : {'ALL': [(62, 10, 28)] * 8,}, # 09-Dec-15 2D, Jose c.o Andy
               },
            ('C677', '5A2HG') : {
               'ATTRIBUTE' : 'IS_2D_DRV',
               'DEFAULT'   : 0,
               0           : {'ALL': [(55, 12, 28)] * 8,}, # 02-Nov-15, 2D
               1           : {'ALL': [(62, 10, 28)] * 8,}, # 09-Dec-15 2D, Jose c.o Andy
               },
            ('C677', '4C430') : {'ALL': [(55, 12, 26)] * 8,}, # 19-Jun-15 copied from HWY + TI + R5.1 + 4C430
            ('C677', '5A2HH') : {
               'ATTRIBUTE' : 'IS_2D_DRV',
               'DEFAULT'   : 0,
               0           : {'ALL': [(55, 12, 28)] * 8,}, # 04-Sep-15
               1           : {'ALL': [(62, 10, 26)] * 8,}, # 09-Dec-15 2D, Jose c.o Andy
               },
            ('C677', '5A5J0') : {
               'ATTRIBUTE' : 'IS_2D_DRV',
               'DEFAULT'   : 0,
               0           : {'ALL': [(55, 12, 26)] * 8,}, # 24-Nov-15
               1           : {'ALL': [(62, 10, 28)] * 8,}, # 09-Dec-15 2D, Jose c.o Andy
               },   
            ('C677', '5A3J2') : {
               'ATTRIBUTE' : 'IS_2D_DRV',
               'DEFAULT'   : 0,
               0           : {'ALL': [(55, 12, 28)] * 8,}, # 20-Oct-15
               1           : {'ALL': [(55, 12, 26)] * 8,}, # 29-Sep-15
               },
            ('C677', '5A99G') : {
               'ATTRIBUTE' : 'IS_2D_DRV',
               'DEFAULT'   : 0,
               0           : {'ALL': [(55, 12, 26)] * 8,}, # 24-Nov-2015
               1           : {'ALL': [(62, 10, 26)] * 8,}, # 29-Sep-15
               },
         },
      },

      'TDK': {
         'ATTRIBUTE' : 'FE_0334525_348429_INTERPOLATED_DEFAULT_TRIPLET',
         'DEFAULT'   : 0,
         0: {
            'LSI5830'   : {
               'ATTRIBUTE'       : ('MediaType', 'HSA_WAFER_CODE'),
               'DEFAULT'         : ('R8.0', '5F057'),
               ('R7.0', '5F057') : {'ALL': [(48, 20, 26)] * 8,}, # 24-Dec-2015
               ('R8.0', '5F057') : {'ALL': [(48, 20, 26)] * 8,}, # 24-Dec-2015
               ('R8.0', '5F608') : {'ALL': [(48, 20, 26)] * 8,}, # 24-Dec-2015 (1D) 30-Dec-2015 (2D)
               ('R10',  '5F057') : {'ALL': [(48, 20, 26)] * 8,}, # 24-Dec-2015 copied from R8
               ('C572', '5F057') : {'ALL': [(48, 20, 26)] * 8,}, # copied from R8
               ('C572', '5F608') : {'ALL': [(48, 20, 26)] * 8,}, # 2D, 22-Jan-2016 copy from R8.0               
            },
            'TI7551'    : {
               'ATTRIBUTE'       : ('MediaType', 'HSA_WAFER_CODE'),
               'DEFAULT'         : ('R8.0', '5F057'),
               ('R7.0', '5F057') : {'ALL': [(55, 12, 26)] * 8,}, # 24-Dec-2015
               ('R8.0', '5F057') : {'ALL': [(55, 12, 26)] * 8,}, # 24-Dec-2015
               ('R8.0', '5F608') : {'ALL': [(55, 12, 26)] * 8,}, # 24-Dec-2015
               ('R10',  '5F057') : {'ALL': [(55, 12, 26)] * 8,}, # 24-Dec-2015 copied from R8
               ('C572', '5F057') : {'ALL': [(55, 12, 26)] * 8,},
               ('C572', '5F608') : {'ALL': [(55, 12, 26)] * 8,}, # 2D, 30-Dec-2015		
            },
         },
         1: {
            'LSI5830'   : {
               'ATTRIBUTE'       : ('MediaType', 'HSA_WAFER_CODE'),
               'DEFAULT'         : ('R8.0', '5F057'),
               ('R7.0', '5F057') : {'ALL': [(48, 20, 26)] * 8,}, # 24-Dec-2015
               ('R8.0', '5F057') : {'OD': [(70, 12, 26)] * 8, 'ID': [(50, 10, 26)] * 8,}, # 12-Jan-2016 jose,
               ('R8.0', '5F608') : {'OD': [(70, 12, 26)] * 8, 'ID': [(50, 10, 26)] * 8,}, # 12-Jan-2016 jose,
               ('R10',  '5F816') : {'OD': [(60, 20, 26)] * 8, 'ID': [(50, 10, 26)] * 8,}, # 04-Mar-2016 
               ('R10',  '5F057') : {'OD': [(60, 20, 26)] * 8, 'ID': [(50, 10, 26)] * 8,}, # 04-Mar-2016 
               ('C572', '5F057') : {'OD': [(70, 12, 26)] * 8, 'ID': [(50, 10, 26)] * 8,}, # 12-Jan-2016 jose,
               ('C572', '5F608') : {'OD': [(70, 12, 26)] * 8, 'ID': [(50, 10, 26)] * 8,}, # 2D, 22-Jan-2016 copy from R8.0                 
            },
            'TI7551'    : { # {'ALL': [(55, 12,  8)] * 8,},
               'ATTRIBUTE'       : ('MediaType', 'HSA_WAFER_CODE'),
               'DEFAULT'         : ('R8.0', '5F057'),
               ('R7.0', '5F057') : {'ALL': [(55, 12, 26)] * 8,}, # 24-Dec-2015
               ('R8.0', '5F057') : {'OD': [(70, 9, 26)] * 8, 'ID': [(50, 7, 26)] * 8,}, # 12-Jan-2016 jose,
               ('R8.0', '5F608') : {'OD': [(70, 9, 26)] * 8, 'ID': [(50, 7, 26)] * 8,}, # 12-Jan-2016 jose,
               ('R10',  '5F816') : {'OD': [(70, 9, 26)] * 8, 'ID': [(50, 7, 26)] * 8,}, # 04-Mar-2016 
               ('R10',  '5F057') : {'OD': [(70, 9, 26)] * 8, 'ID': [(50, 7, 26)] * 8,}, # 04-Mar-2016 
               ('C572', '5F057') : {'OD': [(70, 9, 26)] * 8, 'ID': [(50, 7, 26)] * 8,}, # 12-Jan-2016 jose,
               ('C572', '5F608') : {'OD': [(70, 9, 26)] * 8, 'ID': [(50, 7, 26)] * 8,}, # 12-Jan-2016 jose,
            },
         },
      },
   # },
}

MinimumHeatRecoverySpec = {
  'MIN_DAC_REQUIRED'      : {
     'ATTRIBUTE'          : 'HGA_SUPPLIER',
     'DEFAULT'            : 'RHO',
     'RHO'                : 30,
     'HWY'                : 30,
     'TDK'                : 30,},
  'MIN_IW_REQUIRED'      : {
     'ATTRIBUTE'          : 'HGA_SUPPLIER',
     'DEFAULT'            : 'RHO',
     'RHO'                : 10,
     'HWY'                : 10,
     'TDK'                : 10,},
  'MIN_IW_REQUIRED_SUB'   : {
     'ATTRIBUTE'          : 'HGA_SUPPLIER',
     'DEFAULT'            : 'RHO',
     'RHO'                : 5,
     'HWY'                : 12,
     'TDK'                : 12,},
  'MAX_IW_REQUIRED'      : {
     'ATTRIBUTE'          : 'HGA_SUPPLIER',
     'DEFAULT'            : 'RHO',
     'RHO'                : 15,
     'HWY'                : 15,
     'TDK'                : 15,},
  'IW_DAC_SLOPE'      : {
     'ATTRIBUTE'          : 'HGA_SUPPLIER',
     'DEFAULT'            : 'RHO',
     'RHO'                : 2.2,
     'HWY'                : 2.2,
     'TDK'                : 2.2,},
}

TccResetSpec = {
  'DELTA_CLR_MEAN'      : {
     'ATTRIBUTE'          : 'HGA_SUPPLIER',
     'DEFAULT'            : 'RHO',
     'RHO'                : 10,
     'HWY'                : 10,
     'TDK'                : 10,},
  'DELTA_CLR_STDEV'      : {
     'ATTRIBUTE'          : 'HGA_SUPPLIER',
     'DEFAULT'            : 'RHO',
     'RHO'                : 10,
     'HWY'                : 10,
     'TDK'                : 10,},
}

HMSCapScrnSpec = {
  'MIN_HMSCap_REQUIRED'      : {
     'ATTRIBUTE'          : 'HGA_SUPPLIER',
     'DEFAULT'            : 'RHO',
     'RHO'                : 0.50,
     'HWY'                : 0.50,
     'TDK'                : 0.50,},
  'MEAN_HMSCap_REQUIRED'      : {
     'ATTRIBUTE'          : 'HGA_SUPPLIER',
     'DEFAULT'            : 'RHO',
     'RHO'                : 0.95,
     'HWY'                : 0.95,
     'TDK'                : 0.95,},
  'StdDev_HMSCap_REQUIRED': {      ## intend to use for AngsanaH only.
     'ATTRIBUTE'          : 'HGA_SUPPLIER',
     'DEFAULT'            : 'RHO',
     'RHO'                : 0.71,
     'HWY'                : 0.71,
     'TDK'                : 0.71,},
}
CSCScrnSpec = {
  'MAX_CSC_REQUIRED'      : {
     'ATTRIBUTE'          : 'HGA_SUPPLIER',
     'DEFAULT'            : 'RHO',
     'RHO'                : 5.75,
     'HWY'                : 5.75,
     'TDK'                : 5.75,},
  'BER_COLD_REQUIRED'      : {
     'ATTRIBUTE'          : 'HGA_SUPPLIER',
     'DEFAULT'            : 'RHO',
     'RHO'                : -2.9,
     'HWY'                : -2.9,
     'TDK'                : -2.9,},
  'BER_DELTA_REQUIRED'      : {
     'ATTRIBUTE'          : 'HGA_SUPPLIER',
     'DEFAULT'            : 'RHO',
     'RHO'                : 0.2,
     'HWY'                : 0.2,
     'TDK'                : 0.2,},
}

HeadInstabilityBySovaErrCountScrnSpec = {
  'MEAN_ERR_COUNT_REQUIRED'      : {
     'ATTRIBUTE'          : 'HGA_SUPPLIER',
     'DEFAULT'            : 'RHO',
     'RHO'                : 100,
     'HWY'                : 100,
     'TDK'                : 100,},
  'MIN_ERR_COUNT_REQUIRED'   : {
     'ATTRIBUTE'          : 'HGA_SUPPLIER',
     'DEFAULT'            : 'RHO',
     'RHO'                : 50,
     'HWY'                : 50,
     'TDK'                : 50,},
  'FAIL_ZONES_REQUIRED'      : {
     'ATTRIBUTE'          : 'HGA_SUPPLIER',
     'DEFAULT'            : 'RHO',
     'RHO'                : 15,
     'HWY'                : 15,
     'TDK'                : 15,},
  #'MIN_AVG_DELTA_BER_HD'     : {
  #   'ATTRIBUTE'          : 'HGA_SUPPLIER',
  #   'DEFAULT'            : 'RHO',
  #   'RHO'                : 0.1,
  #   'HWY'                : 0.1,
  #   'TDK'                : 0.1,},
  'NUMBER_T250_TO_RUN'    : 3,
  'MIN_AVG_DELTA_BER_HD'  : {
            "ATTRIBUTE"   : "IS_2D_DRV",
            "DEFAULT"     : 0,
            0       : 0.3,
            1       : {
               'ATTRIBUTE': 'BG',
               'DEFAULT'  : 'OEM1B',
               'OEM1B'    : 0.108,
               'SBS'      : 0.3,
               },
            },
  'MIN_AVG_DELTA_BER_HD_BAK' : {
            "ATTRIBUTE"   : "CAPACITY_PN",
            "DEFAULT"     : "750G",
            "750G"        : 0.13,
            "500G"        : 0.13,},
  #'MIN_DELTA_BER_ZONE'       : {
  #   'ATTRIBUTE'          : 'HGA_SUPPLIER',
  #   'DEFAULT'            : 'RHO',
  #   'RHO'                : 0.1,
  #   'HWY'                : 0.1,
  #   'TDK'                : 0.1,},
  'MIN_DELTA_BER_ZONE'  : {
            "ATTRIBUTE"   : "CAPACITY_PN",
            "DEFAULT"     : "500G",
            "500G"        : 0.2, ## 0.2 is base on AngsanaH data only.
            "320G"        : 1.2,},
  'MIN_FAIL_ZONE_COUNT_HD'   : {
     'ATTRIBUTE'          : 'IS_2D_DRV',
     'DEFAULT'            : 0,
     0                    : 25,
     1                    : {
        'ATTRIBUTE': 'BG',
        'DEFAULT'  : 'OEM1B',
        'OEM1B'    : 6,
        'SBS'      : 25,
        },
     },
}
DestrokeByT193ChromeSpec = {
  'MABS_CRRO_LIMIT_LO'       : {
     'ATTRIBUTE'          : 'HGA_SUPPLIER',
     'DEFAULT'            : 'RHO',
     'RHO'                : 12.0,
     'HWY'                : 12.0,
     'TDK'                : 12.0,},
  'DESTROKE_TRKS_FIXED_LO'   : {
     'ATTRIBUTE'          : 'HGA_SUPPLIER',
     'DEFAULT'            : 'RHO',
     'RHO'                : 5000,
     'HWY'                : 5000,
     'TDK'                : 5000,},
  'MABS_CRRO_LIMIT_UP'       : {
     'ATTRIBUTE'          : 'HGA_SUPPLIER',
     'DEFAULT'            : 'RHO',
     'RHO'                : 20.0,
     'HWY'                : 20.0,
     'TDK'                : 20.0,},
  'DESTROKE_TRKS_FIXED_UP'   : {
     'ATTRIBUTE'          : 'HGA_SUPPLIER',
     'DEFAULT'            : 'RHO',
     'RHO'                : 11000,
     'HWY'                : 11000,
     'TDK'                : 11000,},
}
GuaranteedOperTempSpec = {
  'OPER_TEMP_SPEC_LO'       : {
     'ATTRIBUTE'          : 'HGA_SUPPLIER',
     'DEFAULT'            : 'RHO',
     'RHO'                : 0,
     'HWY'                : 0,
     'TDK'                : 0,},
  'OPER_TEMP_SPEC_HI'   : {
     'ATTRIBUTE'          : 'HGA_SUPPLIER',
     'DEFAULT'            : 'RHO',
     'RHO'                : 70,
     'HWY'                : 70,
     'TDK'                : 70,},
}
VbarSwPwf = [0.9650, 0.9700, 0.9750, 0.9800, 0.9850, 0.9900, 0.9950, 1.000]             # Saturation write power weighting function
VbarFwPwf = [0.9610, 0.9710, 0.9790, 0.9850, 0.9900, 0.9950, 0.9975, 1.000]   # Fitness write power weighting function
VbarClrWfDeltaf = [0.002, 0.005, 0.015, 0.050]  # deltas for clearance weighting function

MD_Data_Zn_Before_Sys_Zn = 17
VbarMeasNumTrksPerZone  = 6
VbarMeasNumSqzWrites    = 6
VbarMeasTrkTimeout      = 600
VbarBpiMaxPushRelax     = 20
VbarAdjBpiForTpi        = 0
VbarNomSerpentWidth     = 200
VbarTargetSER           = 28 # 2.55db


#super parity had update the PVT size to 0x11000 byte to avoid flashLED 465A.
#0x11000 = 69632 byte
#Every bit represent 1 track, thus 69632 byte = 557056 tracks for the whole drive.
#there still be chance that the drive will exceed this number of tracks and flashLED 465A reported after serial format.
#To prevent this, we need to apply a check in VBAR.  If the total physical tracks > 558000, then stop TPI push or direct waterfall the drive.
#With this check, it will be some over kill because the Super Parity only look at the maximum track for the last LBA, while VBAR is looking at the physical tracks which include the spares
SuperparityTrkLimit = 558000

VbarMaxHeads = {
   'ATTRIBUTE' : 'FE_0112737_357263_T210_MAX16_HEAD_SUPPORT',
   'DEFAULT'   : 1,
      1        : 16,
      0        : 8,
}

BPI_MIN                 = 0.6
TPI_MIN                 = 0.4


# BPI Margin by Clearance Backoff
BPIClrMarginThreshold = 0.01#100
BPIMarginClrBackoff = 3 # Clearance Backoff for BPIC Margin Measurement

# BPI Nominal Controls
VBPINominalCapabilities = (0.75, 0.96, 1.04, 1.30)
VBPINominalFormats      = (0.80, 1.00, 1.00, 1.20)

# VBAR HMS
def frange(start, end, steps):
   return [start + i * (end-start)/(steps-1) for i in range(steps)]

BPIperHMS = {
   'ATTRIBUTE':'numZones',
   'DEFAULT': 150,
   60: [
        frange(0.05, 0.035, 60),
        frange(0.05, 0.035, 60),
        frange(0.04, 0.03,  60),
        frange(0.04, 0.03,  60),
        frange(0.04, 0.03,  60),
        frange(0.03, 0.02,  60),
        frange(0.03, 0.02,  60),
       ],
   150: [
        frange(0.05, 0.035, 150),
        frange(0.05, 0.035, 150),
        frange(0.04, 0.03,  150),
        frange(0.04, 0.03,  150),
        frange(0.04, 0.03,  150),
        frange(0.03, 0.02,  150),
        frange(0.03, 0.02,  150),
       ],
}

BPIperHMS1 = {
   'ATTRIBUTE':'numZones',
   'DEFAULT': 150,
   60: [
        frange(0.05, 0.035, 60),
        frange(0.05, 0.035, 60),
       ],
   150: [
        frange(0.05, 0.035, 150),
        frange(0.05, 0.035, 150),
       ],
}

BPIperHMS2 = {
   'ATTRIBUTE':'numZones',
   'DEFAULT': 150,
   60: [
        frange(0.04, 0.03,  60),
        frange(0.04, 0.03,  60),
        frange(0.04, 0.03,  60),
        frange(0.03, 0.02,  60),
        frange(0.03, 0.02,  60),
       ],
   150: [
        frange(0.04, 0.03,  150),
        frange(0.04, 0.03,  150),
        frange(0.04, 0.03,  150),
        frange(0.03, 0.02,  150),
        frange(0.03, 0.02,  150),
       ],
}

BPIperHMS_CLR = {
   'ATTRIBUTE':'numZones',
   'DEFAULT': 150,
   60: [
        frange(0.04, 0.03,  60),
       ],
   150: [
        frange(0.04, 0.03,  150),
       ],
}


if testSwitch.VBAR_HMS_V4:
   if testSwitch.ODMZ:
      HMSMarginTaper = {
         'ATTRIBUTE':'numZones',
         'DEFAULT': 150,
         60 : [0.9] + frange(-0.9/59, -0.9/59, 59),
         150: [0.9] + frange(-0.9/149, -0.9/149, 149),
      }
   else:
      HMSMarginTaper = {
         'ATTRIBUTE':'numZones',
         'DEFAULT': 150,
         60 : frange(0.0, 0.0, 60),
         150: frange(0.0, 0.0, 150),
      }

else:
   HMSMarginTaper = {
      'ATTRIBUTE':'numZones',
      'DEFAULT': 150,
      60 : frange(0.0, 0.0, 60),
      150: frange(0.0, 0.0, 150),
   }


if testSwitch.FE_0162444_208705_ASYMMETRIC_VBAR_HMS:
   VbarMaxBpiAdjperHMS = {
      'ATTRIBUTE':'numZones',
      'DEFAULT': 150,
      60 : frange(0.05, 0.05, 60),
      150: frange(0.05, 0.05, 150),
   }

elif testSwitch.VBAR_HMS_V4:
   if testSwitch.ODMZ:
      VbarMaxBpiAdjperHMS = {
         'ATTRIBUTE':'numZones',
         'DEFAULT': 150,
         60 : [0.0] + frange(0.12, 0.12, 59),   #30: frange(0.12, 0.12, 30),
         150: [0.0] + frange(0.12, 0.12, 149),
      }
   else:
      VbarMaxBpiAdjperHMS = {
         'ATTRIBUTE':'numZones',
         'DEFAULT': 150,
         60 : frange(0.12, 0.12, 60),
         150: frange(0.12, 0.12, 150),
      }

else:
   VbarMaxBpiAdjperHMS = {
         'ATTRIBUTE':'numZones',
         'DEFAULT': 150,
         60 : frange(0.12, 0.12, 60),
         150: frange(0.12, 0.12, 150),
      }


if testSwitch.VBAR_HMS_V4:
   if testSwitch.ODMZ:
      VbarMinBpiAdjperHMS = {
         'ATTRIBUTE':'numZones',
         'DEFAULT': 150,
         60 : [-0.25] + frange(-0.15, -0.15, 59),  #30: frange(-0.15, -0.15, 30),
         150: [-0.25] + frange(-0.15, -0.15, 149),  #30: frange(-0.15, -0.15, 30),
      }
   else:
      VbarMinBpiAdjperHMS = {
      'ATTRIBUTE':'numZones',
      'DEFAULT': 150,
      60 : frange(-0.15, -0.15, 60),
      150: frange(-0.15, -0.15, 150),
   }

else:
   VbarMinBpiAdjperHMS = {
      'ATTRIBUTE':'numZones',
      'DEFAULT': 150,
      60 : frange(-0.15, -0.15, 60),
      150: frange(-0.15, -0.15, 150),
   }


if testSwitch.VBAR_HMS_V4:
   if testSwitch.FE_0162444_208705_ASYMMETRIC_VBAR_HMS:
      VbarHMSThreshold = 0.00
   else:
      VbarHMSThreshold = 0.13

   VbarHMSMaxPassLimit = 7.000

   VbarHMSMaxPickerStep = [0.08, 0.07, 0.06, 0.05, 0.04, 0.03, 0.02]

   if not testSwitch.FE_0162448_007867_MOVE_VBAR_HMS_SPEC_AND_MT_ADJUSTS_TO_NIBLET:
      VbarHMSBPIMTAdjust = -0.30
else:
   VbarHMSThreshold = 0.15
   VbarHMSMaxPassLimit = 5.000

   VbarHMSMaxPickerStep = [0.07, 0.06, 0.05, 0.04, 0.03, 0.02, 0.02]

   if not testSwitch.FE_0162448_007867_MOVE_VBAR_HMS_SPEC_AND_MT_ADJUSTS_TO_NIBLET:
      VbarHMSBPIMTAdjust = -0.06

if not testSwitch.FE_0162448_007867_MOVE_VBAR_HMS_SPEC_AND_MT_ADJUSTS_TO_NIBLET:
   if testSwitch.VBAR_HMS_V4:
      VbarHMSTPIMTAdjust = -0.02
   elif testSwitch.FE_0150604_208705_P_VBAR_HMS_PHASE_2_INCREASE_TGT_CLR:
      if testSwitch.MEGALODON:
         VbarHMSTPIMTAdjust = 0.00
      else:
         VbarHMSTPIMTAdjust = -0.01
   else:
      VbarHMSTPIMTAdjust = -0.03

   if testSwitch.VBAR_HMS_V4:
      VbarHMSMinZoneSpec = 0.8
      VbarHMSMinHeadSpec = 1.8
   elif testSwitch.FE_0145538_208705_VBAR_HMS_INCREASE_TGT_CLR:
      VbarHMSMinZoneSpec = 0.0
      VbarHMSMinHeadSpec = 0.0
   else:
      VbarHMSMinZoneSpec = 1.0
      VbarHMSMinHeadSpec = 1.0

VbarHMSSafeToIncreaseClearanceSpec = 2.6
VbarHMSIncreaseClearanceZonePct = 0.90
VbarHMSClrIncreaseWH  =  0.3
VbarHMSClrIncreaseRH  =  0.3
VbarHMSClrIncreaseCap = -0.3
VbarHMSRequireDecreaseClearanceSpec = 2.0

if testSwitch.VBAR_HMS_V4 :
   VbarHMSDecreaseClearanceZonePct = 0.06
else:
   VbarHMSDecreaseClearanceZonePct = 0.30

VbarHMSClrDecreaseWH  = -0.3
VbarHMSClrDecreaseRH  = -0.3
VbarHMSClrDecreaseCap =  0.3

if testSwitch.VBAR_HMS_V4:
   if testSwitch.FE_0162444_208705_ASYMMETRIC_VBAR_HMS:
      VbarHMSMinTargetHMSCap = 2.5   # Minimum allowed HMS average that HMS2 will converge towards
      VbarHMSMaxTargetHMSCap = 2.5   # Maximum allowed HMS average that HMS2 will converge towards
   else:
      VbarHMSMinTargetHMSCap = 2.0   # Minimum allowed HMS average that HMS2 will converge towards
      VbarHMSMaxTargetHMSCap = 4.0   # Maximum allowed HMS average that HMS2 will converge towards

if testSwitch.CONDITIONAL_RUN_HMS:
   VbarHMSTriggerSpec = {
      'HMSCapSpec': 0.9,
      'EWACSpec':2.46,
      'HMSCapSpecMin': 0.77,
   }
   VbarHMSMaxPassLimit = 2.5
   VbarHMSMinHeadSpec  = 1.2
   VbarHMSSafeToIncreaseClearanceSpec = 7.0
   VbarHMSRequireDecreaseClearanceSpec = 0


##################### SCP HMS #####################################
MAX_HMS_ITERATIONS = 16
HMS_BPI_STEP = 0.0075
SCP_HMS_SKIP_OPTI_MODULA = 1 #2
SCP_MAX_HMSC_BPIADJ = 0.10 # Max Backoff
SCP_MIN_ADJ = 1.02 #0.02 # The backoff has to be greater than this before kickin

##################### On the Fly Triplet #####################################
NPow = 30 # Power used for the Center of Gravity Calculations
OvershootDuration = 7 # Default Overshoot Duration
SteepSatThreshold = 0.057
if testSwitch.FE_ENHANCED_TRIPLET_OPTI:
   FlatSatThreshold = {
       "ATTRIBUTE" : 'HGA_SUPPLIER',
       "DEFAULT" : 'RHO',
       "TDK" : 0.0010,
       "RHO" : 0.0025,
       "HWY" : 0.0010,
       }
else:
   FlatSatThreshold = {
      'ATTRIBUTE' : 'FE_0308035_403980_P_MULTIMATRIX_TRIPLET',
      'DEFAULT'   : 0,
         1        : 0.001,
         0        : 0.0025,
   }
BPIAvalancheThreshold = 0.03

#FF is used in Auto Triplet Generation of 8 Sets
TripletTemplate = {'Q1': [(0,0), (-1,1), (-1,0), (-2,1), (-3,2), (-3,1), (-4,2), (-5,2)],
                   'Q2': [(5,2), (4,2),  (3,2),  (3,1),  (2,1),  (1,1),  (1,0),  (0,0)],
                   'Q3': [(0,0), (-1,0), (-1,-1),(-2,-1),(-3,-1),(-3,-2),(-4,-2),(-5,-2)],
                   'Q4': [(5,-2),(4,-2), (3,-1), (3,-2), (2,-1), (1,0),  (1,-1), (0,0)],
                  }

VBAR_TCC = {
    #"WC_NOMINAL_TEMP" : 40,
    "WC_HOT_OFFSET" : 0,
    #"WC_HOT_TEMP" : 60,
    "WC_COLD_OFFSET" : 0,
    #"WC_COLD_TEMP" : 0,
}
Stage1Matrix ={
    "ATTRIBUTE" : 'HGA_SUPPLIER',
    "DEFAULT" : 'RHO',
    "TDK" : {
            "ATTRIBUTE" : 'PREAMP_TYPE',
            "DEFAULT" : 'default',
            "default" : {
      #matrix List  Iw:Oa 1  2  3  4  5  6  7  8  9  10 11 12 13 14 15
                     1 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     2 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     3 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     4 : [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                     5 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     6 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     7 : [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0],
                     8 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     9 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     10: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     11: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     12: [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0],
                     13: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     14: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     15: [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                     },
            "LSI2935": {
      #matrix List  Iw:Oa 1  2  3  4  5  6  7  8  9  10 11 12 13 14 15
                     1 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     2 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     3 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     4 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
                     5 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     6 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     7 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0],
                     8 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     9 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     10: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     11: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     12: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0],
                     13: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     14: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     15: [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
                     },
            "LSI5231": {
      #matrix List  Iw:Oa 1  2  3  4  5  6  7  8  9  10 11 12 13 14 15
                     0 : [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                     1 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     2 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     3 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     4 : [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                     5 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     6 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     7 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     8 : [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                     9 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     10: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     11: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     12: [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                     13: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     14: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     15: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     },
            "TI7550": {
      #matrix List  Iw:Oa 1  2  3  4  5  6  7  8  9  10 11 12 13 14 15
                     0 : [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                     1 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     2 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     3 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     4 : [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                     5 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     6 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     7 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     8 : [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                     9 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     10: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     11: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     12: [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                     13: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     14: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     15: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     },
            "TI7551": {
      #matrix List  Iw:Oa 1  2  3  4  5  6  7  8  9  10 11 12 13 14 15
                     0 : [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                     1 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     2 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     3 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     4 : [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                     5 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     6 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     7 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     8 : [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                     9 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     10: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     11: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     12: [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                     13: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     14: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     15: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     },
            "LSI5830": {
      #matrix List  Iw:Oa 1  2  3  4  5  6  7  8  9  10 11 12 13 14 15
                     0 : [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                     1 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     2 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     3 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     4 : [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                     5 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     6 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     7 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     8 : [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                     9 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     10: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     11: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     12: [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                     13: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     14: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     15: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     },
            },
    "RHO" : {
            "ATTRIBUTE" : 'PREAMP_TYPE',
            "DEFAULT" : 'default',
            "default" : {
      #matrix List  Iw:Oa 1  2  3  4  5  6  7  8  9  10 11 12 13 14 15
                     1 : [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     2 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     3 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     4 : [0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     5 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     6 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     7 : [0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     8 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     9 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     10: [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     11: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     12: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     13: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     14: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     15: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     },
            "LSI2935": {
      #matrix List  Iw:Oa 1  2  3  4  5  6  7  8  9  10 11 12 13 14 15
                     1 : [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     2 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     3 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     4 : [0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     5 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     6 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     7 : [0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     8 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     9 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     10: [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     11: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     12: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     13: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     14: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     15: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     },
            "LSI5231": {
      #matrix List  Iw:Oa 1  2  3  4  5  6  7  8  9  10 11 12 13 14 15
                     0 : [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                     1 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     2 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     3 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     4 : [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                     5 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     6 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     7 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     8 : [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                     9 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     10: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     11: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     12: [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                     13: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     14: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     15: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     },
            "LSI5830": {
      #matrix List  Iw:Oa 1  2  3  4  5  6  7  8  9  10 11 12 13 14 15
                     0 : [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                     1 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     2 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     3 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     4 : [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                     5 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     6 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     7 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     8 : [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                     9 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     10: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     11: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     12: [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                     13: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     14: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     15: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     },
            "TI7550": {
      #matrix List  Iw:Oa 1  2  3  4  5  6  7  8  9  10 11 12 13 14 15
                     0 : [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                     1 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     2 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     3 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     4 : [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                     5 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     6 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     7 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     8 : [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                     9 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     10: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     11: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     12: [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                     13: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     14: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     15: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     },
            "TI7551": {
      #matrix List  Iw:Oa 1  2  3  4  5  6  7  8  9  10 11 12 13 14 15
                     0 : [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                     1 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     2 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     3 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     4 : [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                     5 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     6 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     7 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     8 : [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                     9 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     10: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     11: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     12: [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                     13: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     14: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     15: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     },
            },
    "HWY" : {
            "ATTRIBUTE" : 'PREAMP_TYPE',
            "DEFAULT" : 'default',
            "default" : {
      #matrix List  Iw:Oa 1  2  3  4  5  6  7  8  9  10 11 12 13 14 15
                     1 : [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     2 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     3 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     4 : [0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     5 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     6 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     7 : [0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     8 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     9 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     10: [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     11: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     12: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     13: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     14: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     15: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     },
            "LSI2935": {
      #matrix List  Iw:Oa 1  2  3  4  5  6  7  8  9  10 11 12 13 14 15
                     1 : [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     2 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     3 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     4 : [0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     5 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     6 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     7 : [0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     8 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     9 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     10: [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     11: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     12: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     13: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     14: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     15: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     },
            "LSI5231": {
      #matrix List  Iw:Oa 1  2  3  4  5  6  7  8  9  10 11 12 13 14 15
                     0 : [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                     1 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     2 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     3 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     4 : [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                     5 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     6 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     7 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     8 : [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                     9 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     10: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     11: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     12: [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                     13: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     14: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     15: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     },
            "LSI5830": {
      #matrix List  Iw:Oa 1  2  3  4  5  6  7  8  9  10 11 12 13 14 15
                     0 : [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                     1 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     2 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     3 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     4 : [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                     5 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     6 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     7 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     8 : [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                     9 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     10: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     11: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     12: [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                     13: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     14: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     15: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     },
            "TI7550": {
      #matrix List  Iw:Oa 1  2  3  4  5  6  7  8  9  10 11 12 13 14 15
                     0 : [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                     1 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     2 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     3 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     4 : [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                     5 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     6 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     7 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     8 : [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                     9 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     10: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     11: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     12: [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                     13: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     14: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     15: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     },
            "TI7551": {
      #matrix List  Iw:Oa 1  2  3  4  5  6  7  8  9  10 11 12 13 14 15
                     0 : [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                     1 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     2 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     3 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     4 : [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                     5 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     6 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     7 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     8 : [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                     9 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     10: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     11: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     12: [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                     13: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     14: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     15: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     },
            },
}
TripletAreas = {
    "ATTRIBUTE" : 'HGA_SUPPLIER',
    "DEFAULT" : 'RHO',
    "TDK" : {
            "ATTRIBUTE" : 'PREAMP_TYPE',
            "DEFAULT" : 'default',
            "default" : {
               'S01': [(4,3),(7,7),(7,11)],
               'S02': [(4,3),(7,7),(12,7)],
               'S03': [(4,3),(7,11),(4,15)],
               'S04': [(4,3),(12,7),(15,3)],
               'S05': [(7,11),(7,7),(12,7)],
               'S06': [(12,11),(7,11),(7,7)],
               'S07': [(7,7),(12,7),(12,11)],
               'S08': [(12,7),(12,11),(7,11)],
               'S09': [(4,15),(7,11),(7,7)],
               'S10': [(4,15),(12,11),(7,11)],
               'S11': [(15,3),(12,7),(7,7)],
               'S12': [(15,3),(12,11),(12,7)],
               'S13': [(15,3),(15,15),(12,11)],
               'S14': [(15,15),(12,11),(7,11)],
               'S15': [(15,15),(12,7),(12,11)],
               'S16': [(15,15),(7,11),(4,15)],
              },
            "LSI2935" :{
               'S01': [(4,10),(7,11),(7,14)],
               'S02': [(4,10),(7,11),(12,11)],
               'S03': [(4,10),(7,14),(4,15)],
               'S04': [(4,10),(12,11),(15,10)],
               'S05': [(7,14),(7,11),(12,11)],
               'S06': [(12,14),(7,14),(7,11)],
               'S07': [(7,11),(12,11),(12,14)],
               'S08': [(12,11),(12,14),(7,14)],
               'S09': [(4,15),(7,14),(7,11)],
               'S10': [(4,15),(12,14),(7,14)],
               'S11': [(15,10),(12,11),(7,11)],
               'S12': [(15,10),(12,14),(12,11)],
               'S13': [(15,10),(15,15),(12,14)],
               'S14': [(15,15),(12,14),(7,14)],
               'S15': [(15,15),(12,11),(12,14)],
               'S16': [(15,15),(7,14),(4,15)],
              },
            "LSI5231" :{
               'S01': [(00,01),(04,04),(04, 9)],
               'S02': [(00,01),(04,04),( 8,04)],
               'S03': [(00,01),(04, 9),(00,12)],
               'S04': [(00,01),( 8,04),(12,01)],
               'S05': [(04, 9),(04,04),( 8,04)],
               'S06': [( 8, 9),(04, 9),(04,04)],
               'S07': [(04,04),( 8,04),( 8, 9)],
               'S08': [( 8,04),( 8, 9),(04, 9)],
               'S09': [(00,12),(04, 9),(04,04)],
               'S10': [(00,12),( 8, 9),(04, 9)],
               'S11': [(12,01),( 8,04),(04,04)],
               'S12': [(12,01),( 8, 9),( 8,04)],
               'S13': [(12,01),(12,12),( 8, 9)],
               'S14': [(12,12),( 8, 9),(04, 9)],
               'S15': [(12,12),( 8,04),( 8, 9)],
               'S16': [(12,12),(04, 9),(00,12)],
              },
            "LSI5830" :{
               'S01': [(00,01),(04,04),(04, 9)],
               'S02': [(00,01),(04,04),( 8,04)],
               'S03': [(00,01),(04, 9),(00,12)],
               'S04': [(00,01),( 8,04),(12,01)],
               'S05': [(04, 9),(04,04),( 8,04)],
               'S06': [( 8, 9),(04, 9),(04,04)],
               'S07': [(04,04),( 8,04),( 8, 9)],
               'S08': [( 8,04),( 8, 9),(04, 9)],
               'S09': [(00,12),(04, 9),(04,04)],
               'S10': [(00,12),( 8, 9),(04, 9)],
               'S11': [(12,01),( 8,04),(04,04)],
               'S12': [(12,01),( 8, 9),( 8,04)],
               'S13': [(12,01),(12,12),( 8, 9)],
               'S14': [(12,12),( 8, 9),(04, 9)],
               'S15': [(12,12),( 8,04),( 8, 9)],
               'S16': [(12,12),(04, 9),(00,12)],
              },
            "TI7550" :{
               'S01': [(00,01),(04,04),(04, 9)],
               'S02': [(00,01),(04,04),( 8,04)],
               'S03': [(00,01),(04, 9),(00,12)],
               'S04': [(00,01),( 8,04),(12,01)],
               'S05': [(04, 9),(04,04),( 8,04)],
               'S06': [( 8, 9),(04, 9),(04,04)],
               'S07': [(04,04),( 8,04),( 8, 9)],
               'S08': [( 8,04),( 8, 9),(04, 9)],
               'S09': [(00,12),(04, 9),(04,04)],
               'S10': [(00,12),( 8, 9),(04, 9)],
               'S11': [(12,01),( 8,04),(04,04)],
               'S12': [(12,01),( 8, 9),( 8,04)],
               'S13': [(12,01),(12,12),( 8, 9)],
               'S14': [(12,12),( 8, 9),(04, 9)],
               'S15': [(12,12),( 8,04),( 8, 9)],
               'S16': [(12,12),(04, 9),(00,12)],
              },
            "TI7551" :{
               'S01': [(00,01),(04,04),(04, 9)],
               'S02': [(00,01),(04,04),( 8,04)],
               'S03': [(00,01),(04, 9),(00,12)],
               'S04': [(00,01),( 8,04),(12,01)],
               'S05': [(04, 9),(04,04),( 8,04)],
               'S06': [( 8, 9),(04, 9),(04,04)],
               'S07': [(04,04),( 8,04),( 8, 9)],
               'S08': [( 8,04),( 8, 9),(04, 9)],
               'S09': [(00,12),(04, 9),(04,04)],
               'S10': [(00,12),( 8, 9),(04, 9)],
               'S11': [(12,01),( 8,04),(04,04)],
               'S12': [(12,01),( 8, 9),( 8,04)],
               'S13': [(12,01),(12,12),( 8, 9)],
               'S14': [(12,12),( 8, 9),(04, 9)],
               'S15': [(12,12),( 8,04),( 8, 9)],
               'S16': [(12,12),(04, 9),(00,12)],
              },
          },
    "RHO" : {
            "ATTRIBUTE" : 'PREAMP_TYPE',
            "DEFAULT" : 'default',
            "default" : {
               'S01': [(01,01),(04,02),(04,05)],
               'S02': [(01,01),(04,02),(07,02)],
               'S03': [(01,01),(04,05),(01,06)],
               'S04': [(01,01),(07,02),(10,01)],
               'S05': [(04,05),(04,02),(07,02)],
               'S06': [(07,05),(04,05),(04,02)],
               'S07': [(04,02),(07,02),(07,05)],
               'S08': [(07,02),(07,05),(04,05)],
               'S09': [(01,06),(04,05),(04,02)],
               'S10': [(01,06),(07,05),(04,05)],
               'S11': [(10,01),(07,02),(04,02)],
               'S12': [(10,01),(07,05),(07,02)],
               'S13': [(10,01),(10,06),(07,05)],
               'S14': [(10,06),(07,05),(04,05)],
               'S15': [(10,06),(07,02),(07,05)],
               'S16': [(10,06),(04,05),(01,06)],
              },
            "LSI2935" :{
               'S01': [(01,01),(04,02),(04,05)],
               'S02': [(01,01),(04,02),(07,02)],
               'S03': [(01,01),(04,05),(01,06)],
               'S04': [(01,01),(07,02),(10,01)],
               'S05': [(04,05),(04,02),(07,02)],
               'S06': [(07,05),(04,05),(04,02)],
               'S07': [(04,02),(07,02),(07,05)],
               'S08': [(07,02),(07,05),(04,05)],
               'S09': [(01,06),(04,05),(04,02)],
               'S10': [(01,06),(07,05),(04,05)],
               'S11': [(10,01),(07,02),(04,02)],
               'S12': [(10,01),(07,05),(07,02)],
               'S13': [(10,01),(10,06),(07,05)],
               'S14': [(10,06),(07,05),(04,05)],
               'S15': [(10,06),(07,02),(07,05)],
               'S16': [(10,06),(04,05),(01,06)],
              },
            "LSI5231" :{
               'S01': [(00,01),(04,04),(04, 9)],
               'S02': [(00,01),(04,04),( 8,04)],
               'S03': [(00,01),(04, 9),(00,12)],
               'S04': [(00,01),( 8,04),(12,01)],
               'S05': [(04, 9),(04,04),( 8,04)],
               'S06': [( 8, 9),(04, 9),(04,04)],
               'S07': [(04,04),( 8,04),( 8, 9)],
               'S08': [( 8,04),( 8, 9),(04, 9)],
               'S09': [(00,12),(04, 9),(04,04)],
               'S10': [(00,12),( 8, 9),(04, 9)],
               'S11': [(12,01),( 8,04),(04,04)],
               'S12': [(12,01),( 8, 9),( 8,04)],
               'S13': [(12,01),(12,12),( 8, 9)],
               'S14': [(12,12),( 8, 9),(04, 9)],
               'S15': [(12,12),( 8,04),( 8, 9)],
               'S16': [(12,12),(04, 9),(00,12)],
              },
            "LSI5830" :{
               'S01': [(00,01),(04,04),(04, 9)],
               'S02': [(00,01),(04,04),( 8,04)],
               'S03': [(00,01),(04, 9),(00,12)],
               'S04': [(00,01),( 8,04),(12,01)],
               'S05': [(04, 9),(04,04),( 8,04)],
               'S06': [( 8, 9),(04, 9),(04,04)],
               'S07': [(04,04),( 8,04),( 8, 9)],
               'S08': [( 8,04),( 8, 9),(04, 9)],
               'S09': [(00,12),(04, 9),(04,04)],
               'S10': [(00,12),( 8, 9),(04, 9)],
               'S11': [(12,01),( 8,04),(04,04)],
               'S12': [(12,01),( 8, 9),( 8,04)],
               'S13': [(12,01),(12,12),( 8, 9)],
               'S14': [(12,12),( 8, 9),(04, 9)],
               'S15': [(12,12),( 8,04),( 8, 9)],
               'S16': [(12,12),(04, 9),(00,12)],
              },
            "TI7550" :{
               'S01': [(00,01),(04,04),(04, 9)],
               'S02': [(00,01),(04,04),( 8,04)],
               'S03': [(00,01),(04, 9),(00,12)],
               'S04': [(00,01),( 8,04),(12,01)],
               'S05': [(04, 9),(04,04),( 8,04)],
               'S06': [( 8, 9),(04, 9),(04,04)],
               'S07': [(04,04),( 8,04),( 8, 9)],
               'S08': [( 8,04),( 8, 9),(04, 9)],
               'S09': [(00,12),(04, 9),(04,04)],
               'S10': [(00,12),( 8, 9),(04, 9)],
               'S11': [(12,01),( 8,04),(04,04)],
               'S12': [(12,01),( 8, 9),( 8,04)],
               'S13': [(12,01),(12,12),( 8, 9)],
               'S14': [(12,12),( 8, 9),(04, 9)],
               'S15': [(12,12),( 8,04),( 8, 9)],
               'S16': [(12,12),(04, 9),(00,12)],
              },
            "TI7551" :{
               'S01': [(00,01),(04,04),(04, 9)],
               'S02': [(00,01),(04,04),( 8,04)],
               'S03': [(00,01),(04, 9),(00,12)],
               'S04': [(00,01),( 8,04),(12,01)],
               'S05': [(04, 9),(04,04),( 8,04)],
               'S06': [( 8, 9),(04, 9),(04,04)],
               'S07': [(04,04),( 8,04),( 8, 9)],
               'S08': [( 8,04),( 8, 9),(04, 9)],
               'S09': [(00,12),(04, 9),(04,04)],
               'S10': [(00,12),( 8, 9),(04, 9)],
               'S11': [(12,01),( 8,04),(04,04)],
               'S12': [(12,01),( 8, 9),( 8,04)],
               'S13': [(12,01),(12,12),( 8, 9)],
               'S14': [(12,12),( 8, 9),(04, 9)],
               'S15': [(12,12),( 8,04),( 8, 9)],
               'S16': [(12,12),(04, 9),(00,12)],
              },
          },
    "HWY" : {
            "ATTRIBUTE" : 'PREAMP_TYPE',
            "DEFAULT" : 'default',
            "default" : {
               'S01': [(01,01),(04,02),(04,05)],
               'S02': [(01,01),(04,02),(07,02)],
               'S03': [(01,01),(04,05),(01,06)],
               'S04': [(01,01),(07,02),(10,01)],
               'S05': [(04,05),(04,02),(07,02)],
               'S06': [(07,05),(04,05),(04,02)],
               'S07': [(04,02),(07,02),(07,05)],
               'S08': [(07,02),(07,05),(04,05)],
               'S09': [(01,06),(04,05),(04,02)],
               'S10': [(01,06),(07,05),(04,05)],
               'S11': [(10,01),(07,02),(04,02)],
               'S12': [(10,01),(07,05),(07,02)],
               'S13': [(10,01),(10,06),(07,05)],
               'S14': [(10,06),(07,05),(04,05)],
               'S15': [(10,06),(07,02),(07,05)],
               'S16': [(10,06),(04,05),(01,06)],
              },
            "LSI2935" :{
               'S01': [(01,01),(04,02),(04,05)],
               'S02': [(01,01),(04,02),(07,02)],
               'S03': [(01,01),(04,05),(01,06)],
               'S04': [(01,01),(07,02),(10,01)],
               'S05': [(04,05),(04,02),(07,02)],
               'S06': [(07,05),(04,05),(04,02)],
               'S07': [(04,02),(07,02),(07,05)],
               'S08': [(07,02),(07,05),(04,05)],
               'S09': [(01,06),(04,05),(04,02)],
               'S10': [(01,06),(07,05),(04,05)],
               'S11': [(10,01),(07,02),(04,02)],
               'S12': [(10,01),(07,05),(07,02)],
               'S13': [(10,01),(10,06),(07,05)],
               'S14': [(10,06),(07,05),(04,05)],
               'S15': [(10,06),(07,02),(07,05)],
               'S16': [(10,06),(04,05),(01,06)],
              },
            "LSI5231" :{
               'S01': [(00,01),(04,04),(04, 9)],
               'S02': [(00,01),(04,04),( 8,04)],
               'S03': [(00,01),(04, 9),(00,12)],
               'S04': [(00,01),( 8,04),(12,01)],
               'S05': [(04, 9),(04,04),( 8,04)],
               'S06': [( 8, 9),(04, 9),(04,04)],
               'S07': [(04,04),( 8,04),( 8, 9)],
               'S08': [( 8,04),( 8, 9),(04, 9)],
               'S09': [(00,12),(04, 9),(04,04)],
               'S10': [(00,12),( 8, 9),(04, 9)],
               'S11': [(12,01),( 8,04),(04,04)],
               'S12': [(12,01),( 8, 9),( 8,04)],
               'S13': [(12,01),(12,12),( 8, 9)],
               'S14': [(12,12),( 8, 9),(04, 9)],
               'S15': [(12,12),( 8,04),( 8, 9)],
               'S16': [(12,12),(04, 9),(00,12)],
              },
            "LSI5830" :{
               'S01': [(00,01),(04,04),(04, 9)],
               'S02': [(00,01),(04,04),( 8,04)],
               'S03': [(00,01),(04, 9),(00,12)],
               'S04': [(00,01),( 8,04),(12,01)],
               'S05': [(04, 9),(04,04),( 8,04)],
               'S06': [( 8, 9),(04, 9),(04,04)],
               'S07': [(04,04),( 8,04),( 8, 9)],
               'S08': [( 8,04),( 8, 9),(04, 9)],
               'S09': [(00,12),(04, 9),(04,04)],
               'S10': [(00,12),( 8, 9),(04, 9)],
               'S11': [(12,01),( 8,04),(04,04)],
               'S12': [(12,01),( 8, 9),( 8,04)],
               'S13': [(12,01),(12,12),( 8, 9)],
               'S14': [(12,12),( 8, 9),(04, 9)],
               'S15': [(12,12),( 8,04),( 8, 9)],
               'S16': [(12,12),(04, 9),(00,12)],
              },
            "TI7550" :{
               'S01': [(00,01),(04,04),(04, 9)],
               'S02': [(00,01),(04,04),( 8,04)],
               'S03': [(00,01),(04, 9),(00,12)],
               'S04': [(00,01),( 8,04),(12,01)],
               'S05': [(04, 9),(04,04),( 8,04)],
               'S06': [( 8, 9),(04, 9),(04,04)],
               'S07': [(04,04),( 8,04),( 8, 9)],
               'S08': [( 8,04),( 8, 9),(04, 9)],
               'S09': [(00,12),(04, 9),(04,04)],
               'S10': [(00,12),( 8, 9),(04, 9)],
               'S11': [(12,01),( 8,04),(04,04)],
               'S12': [(12,01),( 8, 9),( 8,04)],
               'S13': [(12,01),(12,12),( 8, 9)],
               'S14': [(12,12),( 8, 9),(04, 9)],
               'S15': [(12,12),( 8,04),( 8, 9)],
               'S16': [(12,12),(04, 9),(00,12)],
              },
            "TI7551" :{
               'S01': [(00,01),(04,04),(04, 9)],
               'S02': [(00,01),(04,04),( 8,04)],
               'S03': [(00,01),(04, 9),(00,12)],
               'S04': [(00,01),( 8,04),(12,01)],
               'S05': [(04, 9),(04,04),( 8,04)],
               'S06': [( 8, 9),(04, 9),(04,04)],
               'S07': [(04,04),( 8,04),( 8, 9)],
               'S08': [( 8,04),( 8, 9),(04, 9)],
               'S09': [(00,12),(04, 9),(04,04)],
               'S10': [(00,12),( 8, 9),(04, 9)],
               'S11': [(12,01),( 8,04),(04,04)],
               'S12': [(12,01),( 8, 9),( 8,04)],
               'S13': [(12,01),(12,12),( 8, 9)],
               'S14': [(12,12),( 8, 9),(04, 9)],
               'S15': [(12,12),( 8,04),( 8, 9)],
               'S16': [(12,12),(04, 9),(00,12)],
              },
          },
}

if testSwitch.FE_348429_0247869_TRIPLET_INTEGRATED_ATISTE:
   IwMaxCap = {
      "ATTRIBUTE" : ('HGA_SUPPLIER', 'PREAMP_TYPE'),
      "DEFAULT"   : ('RHO', 'LSI5830'),
      ('RHO', 'LSI5830')      : {
         'ATTRIBUTE'       : ('MediaType', 'HSA_WAFER_CODE'),
         ('R5.1', 'OG8')   : [ 8*7+20, 6*7+20, 5*7+20, 5*7+20],   # 23-Apr-15
         ('R6.4', 'OG8')   : [ 8*7+20, 6*7+20, 5*7+20, 5*7+20],   # 23-Apr-15
         ('R5.1', 'NG8')   : [ 8*7+20, 6*7+20, 5*7+20, 5*7+20],   # 23-Apr-15
         ('R5.1', 'O2Q')   : [ 8*7+20, 6*7+20, 5*7+20, 5*7+20],   # 23-Apr-15 copied from RHO + LSI + R5.1 + OG8
         ('R5.1', 'N5T')   : [10*7+20, 9*7+20, 8*7+20, 7*7+20, 6*7+20, 5*7+20, 4*7+20],   # 04-May-15
         ('R5.1', 'NT4')   : [10*7+20, 9*7+20, 8*7+20, 7*7+20, 6*7+20, 5*7+20, 4*7+20],   # 05-Jun-15
         ('R5.1', 'N4Z')   : {
            'ATTRIBUTE' : 'numPhysHds',
            'DEFAULT'   : 2,
            2           : [ 9*7+20, 8*7+20, 7*7+20, 6*7+20, 5*7+20, 4*7+20, 4*7+20, 3*7+20], # 25-Jun-15
            4           : [10*7+20, 9*7+20, 8*7+20, 7*7+20, 6*7+20, 5*7+20, 4*7+20],         # 16-Jun-15
         },
         ('R5.1', 'OT4')   : [76,69,62,55,48,41,41,34], # copied from R7.0
         ('R6.4', 'NT4')   : [ 9*7+20, 8*7+20, 7*7+20, 6*7+20, 5*7+20, 4*7+20, 3*7+20, 3*7+20], # 24-Jul-15
         ('R6.4', 'OT4')   : [ 9*7+20, 8*7+20, 7*7+20, 6*7+20, 5*7+20, 4*7+20, 4*7+20, 3*7+20], # 26-Jul-15
         ('R7.0', 'OT4')   : [76,69,62,55,48,41,41,34], # Reviewed by Andy chou 18-sep-15
         ('R7.0', 'NT4')   : [83,76,69,62,55,48,41,41], # Reviewed by Andy chou 19-sep-15, same as old 08-Sep-15,RW2D
         ('R7.0', 'NL2')   : {
            'ATTRIBUTE' : 'numPhysHds',
            'DEFAULT'   : 2,
            2           : [76,69,62,55,48,41,34], # 23-Sep-15
            4           : [69,62,55,48,41,34],    # 29-Sep-15
         },
         ('R7.0', 'PD7')   : { # copied from R7+NL2
            'ATTRIBUTE' : 'numPhysHds',
            'DEFAULT'   : 2,
            2           : [76,69,62,55,48,41,34], # 23-Sep-15
            4           : [69,62,55,48,41,34],    # 29-Sep-15
         },
         ('R8.0', 'NL2')   : {
            'ATTRIBUTE' : 'numPhysHds',
            'DEFAULT'   : 2,
            2           : [76,69,62,55,48,41,34],
            4           : [69,62,55,48,41,34],    # 23-Oct-15, same as R7.0
         },		 
         ('R8.0', 'PD7')   : [76,69,62,55,48,41,34], # 20-Nov-2015, 1D & 2D
         ('R10',  'PD7')   : [76,69,62,55,48,41],    # 04-Mar-2016
         ('C677', 'OT4')   : [76,69,62,55,48,41,34], # Reviewed by Andy chou 18-sep-15
         ('C677', 'NT4')   : [83,76,69,62,55,48,48,41], # Reviewed by Andy chou 19-sep-15       
         ('C677', 'NL2')   : {
            'ATTRIBUTE' : 'numPhysHds',
            'DEFAULT'   : 2,
            2           : [69,62,55,48,41,34,27],  # 24-Sep-15
            4           : [69,62,55,48,41,34],  # 29-Sep-15
         },
         ('C677', 'PD7')   : { # copied from C677 + NL2
            'ATTRIBUTE' : 'numPhysHds',
            'DEFAULT'   : 2,
            2           : [69,62,55,48,41,34,27],  # 24-Sep-15
            4           : [69,62,55,48,41,34],  # 29-Sep-15
         },
         ('C572', 'PD7')   : { # copied from C677 + NL2
            'ATTRIBUTE' : 'numPhysHds',
            'DEFAULT'   : 2,
            2           : [69,62,55,48,41,34,27],  # 24-Sep-15
            4           : [69,62,55,48,41,34],  # 29-Sep-15
         },
         ('C655', 'NL2')   : [69,62,55,48,41,34], # 29-Oct-15  
         ('C572', 'NL2')   : [76,69,62,55,48,41,34], # 11-Jan-16 2D.	 
      },
      ('RHO', 'TI7551')       : {
         'ATTRIBUTE'       : ('MediaType', 'HSA_WAFER_CODE'),
         ('R5.1', 'O2Q')   : [ 5*7+20, 5*7+20, 4*7+20, 4*7+20, 4*7+20],          # 20-Apr-15
         ('R5.1', 'NG8')   : [ 5*7+20, 5*7+20, 4*7+20, 4*7+20, 4*7+20],          # 20-Apr-15
         ('R5.1', 'N5T')   : [ 5*7+20, 5*7+20, 4*7+20, 4*7+20, 4*7+20],          # 20-Apr-15
         ('R5.1', 'OG8')   : [ 5*7+20, 4*7+20, 4*7+20, 3*7+20, 3*7+20],          # 15-May-15
         ('R5.1', 'NT4')   : [ 5*7+20, 4*7+20, 3*7+20, 3*7+20, 3*7+20, 3*7+20],  # 23-Jun-15
         ('R5.1', 'N4Z')   : [ 5*7+20, 4*7+20, 3*7+20, 3*7+20, 3*7+20, 3*7+20],  # 20-Jul-15
         ('R5.1', 'OT4')   : [62,55,48,41,34], # copied from R7.0
         ('R6.4', 'OT4')   : [ 6*7+20, 5*7+20, 4*7+20, 3*7+20, 3*7+20, 3*7+20, 3*7+20],   # 28-Aug-15
         ('R6.4', 'NT4')   : [ 8*7+20, 7*7+20, 6*7+20, 5*7+20, 4*7+20, 4*7+20, 4*7+20, 3*7+20], # 08-Sep-15,RW2D        
         ('R7.0', 'OT4')   : [62,55,48,41,34], # Reviewed by Andy chou 18-sep-15
         ('R7.0', 'NT4')   : [83,76,69,62,55,48,41],  # Reviewed by Andy chou 19-sep-15, same as old 17-Sep-15,RW2D           
         ('R7.0', 'NL2')   : [62,55,48,41,34], # 10-Oct-15 1D, 19-Oct-15 2D same as 1D
         ('R7.0', 'PD7')   : [62,55,48,41,34], # copied from NL2
         ('R8.0', 'NL2')   : [62,55,48,41,34], # 18-Nov-15 2D     
         ('R8.0', 'PD7')   : [62,55,48,41,34], # 15-Dec-15
         ('R10',  'PD7')   : [62,55,48,41,34], # 04-Mar-2016
         ('C677', 'OT4')   : [62,55,48,41,34], # Reviewed by Andy chou 18-sep-15
         ('C677', 'NT4')   : [83,76,69,62,55,48,41,34], # Newly added, reviewed by Andy chou 19-sep-15       
         ('C677', 'NL2')   : {
            'ATTRIBUTE' : 'numPhysHds',
            'DEFAULT'   : 2,
            2           : [62,55,48,41,34], # 20-Oct-15
            4           : [62,55,48,41,34], # 27-Oct-15
         },
         ('C677', 'PD7')   : { # copied from NL2
            'ATTRIBUTE' : 'numPhysHds',
            'DEFAULT'   : 2,
            2           : [62,55,48,41,34], # 20-Oct-15
            4           : [62,55,48,41,34], # 27-Oct-15
         },
         ('C655', 'NL2')   : [62,55,48,41,34], # 29-Oct-15
         ('C572', 'PD7')   : [62,55,48,41,34], # 15-Jan-16
      },
      # HAMR related. Starwood.
      ('RHO', 'LSI5235')      : {
         'ATTRIBUTE'       : ('MediaType', 'HSA_WAFER_CODE'),
         'DEFAULT'         : ('R5.1', '5W'),
         ('R5.1', '5W')    : [ 5*7+20, 5*7+20, 4*7+20, 4*7+20, 4*7+20],          # Need to review if want to run. HAMR!!
         ('R5.1', 'BZ7')   : [ 5*7+20, 5*7+20, 4*7+20, 4*7+20, 4*7+20],          # Need to review if want to run. HAMR!!
      },
      ('HWY', 'LSI5830')      : {
         'ATTRIBUTE'       : ('MediaType', 'HSA_WAFER_CODE'),
         ('R5.1', '4A4C5') : [11*7+20,10*7+20, 8*7+20, 7*7+20, 6*7+20, 5*7+20],  # 06-Apr-15
         ('R5.1', '4AHDD') : [11*7+20,10*7+20, 8*7+20, 7*7+20, 6*7+20, 5*7+20],  # copied from 4A4C5
         ('R5.1', '4A60B') : [11*7+20,10*7+20, 8*7+20, 7*7+20, 6*7+20, 5*7+20],  # copied from 4A4C5
         ('R5.1', '4A3C0') : [11*7+20,10*7+20, 8*7+20, 7*7+20, 6*7+20, 5*7+20],  # copied from HWY + LSI + R5.1 + 4A4C5
         ('R5.1', '4AF1F') : [10*7+20, 8*7+20, 6*7+20, 5*7+20, 4*7+20],          # 17-Mar-15
         ('R5.1', '4AH63') : [10*7+20, 8*7+20, 6*7+20, 5*7+20, 4*7+20],          # copy 4AF1F
         ('R5.1', '4C6JH') : [11*7+20,10*7+20, 9*7+20, 8*7+20, 7*7+20, 6*7+20, 5*7+20],   # 07-Jun-15
         ('R5.1', '4C430') : [13*7+20,12*7+20,11*7+20,10*7+20, 9*7+20, 8*7+20, 6*7+20],   # 08-Jun-15
         ('R6.4', '4C430') : [13*7+20,12*7+20,11*7+20,10*7+20, 9*7+20, 8*7+20, 6*7+20],   # 24-Jul-15
         ('R6.4', '5A2HH') : {
            'ATTRIBUTE' : 'numPhysHds',
            'DEFAULT'   : 2,
            2           : [ 9*7+20, 8*7+20, 7*7+20, 6*7+20, 5*7+20, 4*7+20, 3*7+20, 3*7+20, 3*7+20],  # 11-Aug-15
            4           : [ 9*7+20, 8*7+20, 7*7+20, 6*7+20, 5*7+20, 4*7+20, 4*7+20, 3*7+20, 2*7+20],  # 02-Sep-15 -> 18-Sep-15
         },
         ('R7.0', '5A2HH') : {
            'ATTRIBUTE' : 'numPhysHds',
            'DEFAULT'   : 2,
            2           : [83,76,69,62,55,48,48,41,34],   # Reviewed by Andy chou 18-sep-15.
            4           : [83,76,69,62,55,48,48,41,34],   # Reviewed by Andy chou 19-sep-15, same as old
         },
         ('R7.0', '5A3J2') : [83,76,69,62,55,48,48,41,34],     # 22-Sep-15
         ('R8.0', '5A3J2') : [83,76,69,62,55,48,48,41,34],     # copied from R7 + 5A3J2
         ('R7.0', '5A2HG') : [83,76,69,62,55,48,48,41,34,27],  # 23-Sep-15 1D, 12-Oct-15 2D same as 1D
         ('R7.0', '5ABG5') : [83,76,69,62,55,48,41,41,34,27],  # 27-Oct-15
         ('R8.0', '5ABG5') : [83,76,69,62,55,48,41,41,34,27],  # copied from R7 + 5ABG5
         ('R7.0', '5A5J0') : [83,76,69,62,55,48,41,41,34,27],  # 04-Nov-15 1D, 12-Nov-15 2D same as 1D
         ('R8.0', '5A5J0') : [83,76,69,62,55,48,41,41,34,27],  # copy
         ('R8.0', '5A99G') : [83,76,69,62,55,48,41,41,34],     # 18-Nov-15 2D
         ('R8.0', '5A9BJ') : [83,76,69,62,55,48,41,41,34],     # copy     
         ('R8.0', '5F057') : [83,76,69,62,55,48,41,41,34],     # 19-Nov-2015
         ('R8.0', '4C677') : [83,76,69,62,55,48,41,41,34],     # 23-Nov-2015
         ('R10',  '5A99G') : [83,76,69,62,55,48,41,41,34,27],  # copied from R8
         ('R10',  '5A5J0') : [83,76,69,62,55,48,41,41,34,27],  # copied from R8
         ('C655', '4C677') : [83,76,69,62,55,48,48,41,34],     # 23-Nov-2015
         ('C677', '5A2HH') : {
            'ATTRIBUTE' : 'numPhysHds',
            'DEFAULT'   : 2,
            2           : [83,76,69,62,55,48,48,41,34],   # Reviewed by Andy chou 18-sep-15
            4           : [83,76,69,62,55,48,48,41,34],   # Reviewed by Andy chou 19-sep-15
         },
         ('C677', '5A3J2') : {
            'ATTRIBUTE' : 'numPhysHds',
            'DEFAULT'   : 2,
            2           : [83,76,69,62,55,48,48,41,34],      # 19-Sep-15
            4           : [90,83,76,69,62,55,48,41,34,34],   # 24-sep-15
         },
         ('C677', '5A2HG') : [83,76,69,62,55,48,48,41,34],     # 7-oct-15, 12-Oct-15 2D same as 1D
         ('C677', '5ABG5') : [83,76,69,62,55,48,48,41,34],     # 27-oct-15
         ('C677', '5A5J0') : [83,76,69,62,55,48,48,41,34],     # 04-Nov-15
         ('C572', '5AA99') : [83,76,69,62,55,48,41,34],        # 11-Jan-16 2D.	
         ('C572', '5A99G') : [83,76,69,62,55,48,41,34],        # 11-Jan-16 2D POR.	 		  
         ('C448', '5A3J2') : [90,83,76,69,62,55,48,41,41,34],  # 25-Sep-15
      },
      ('HWY', 'TI7551')       : {
         'ATTRIBUTE'       : ('MediaType', 'HSA_WAFER_CODE'),
         ('R5.1', '4A4C5') : [11*7+20,10*7+20, 9*7+20, 8*7+20, 7*7+20, 6*7+20, 5*7+20],   # 30-Apr-15
         ('R5.1', '4AHDD') : [11*7+20,10*7+20, 9*7+20, 8*7+20, 7*7+20, 6*7+20, 5*7+20],   # copied from 4A4C5
         ('R5.1', '4A60B') : [13*7+20,12*7+20,11*7+20, 9*7+20, 8*7+20, 7*7+20, 6*7+20],   # 10-Jun-15
         ('R5.1', '4C6JH') : [11*7+20,10*7+20, 9*7+20, 8*7+20, 7*7+20, 6*7+20, 5*7+20, 4*7+20], # 18-Jun-15
         ('R5.1', '4C430') : [11*7+20,10*7+20, 9*7+20, 8*7+20, 7*7+20, 6*7+20, 5*7+20],   # 19-Jun-15
         ('R6.4', '4C430') : [11*7+20,10*7+20, 9*7+20, 8*7+20, 7*7+20, 6*7+20, 5*7+20, 5*7+20, 5*7+20, 4*7+20],   # 14-Aug-15
         ('R7.0', '5A2HH') : {
            'ATTRIBUTE' : 'numPhysHds',
            'DEFAULT'   : 2,
            2           : [97,90,83,76,69,69,69,62,62,55],   # Reviewed by Andy chou 18-sep-15, same as old 04-Sep-15
            4           : [97,90,83,76,69,62],               # Reviewed by Andy chou 18-sep-15, same as old 17-Sep-15, RW2D
         },
         ('R7.0', '5A3J2') : [97,90,83,76,69,69,69,62,62,55],  # 25-Sep-15
         ('R8.0', '5ABG5') : [97,90,83,76,69,69,69,62,62,55],  # copied from R7 + 5A3J2
         ('R7.0', '5A2HG') : [97,90,83,76,69,62,55,48],     # 02-Nov-15, 2D
         ('R7.0', '5A5J0') : [97,90,83,76,69,62,55,48],     # 12-Nov-15 2D
         ('R8.0', '5A5J0') : [97,90,83,76,69,62,55,48],     # copy
         ('R8.0', '5A99G') : [97,90,83,76,69,62,55],        # 23-Nov-15 2D
         ('R8.0', '5A9BJ') : [97,90,83,76,69,62,55],        # copy      
         ('R10',  '5A99G') : [97,90,83,76,69,62,55,48],     # copied from R8
         ('R10',  '5A5J0') : [97,90,83,76,69,62,55,48],     # copied from R8
         ('C677', '5A2HG') : [97,90,83,76,69,69,62,55],     # 02-Nov-15, 2D
         ('C677', '4C430') : [11*7+20,10*7+20, 9*7+20, 8*7+20, 7*7+20, 6*7+20, 5*7+20],   # 19-Jun-15 copied from HWY + TI + R5.1 + 4C430
         ('C677', '5A2HH') : [97,90,83,76,76,69,62,55],     # Reviewed by Andy chou 18-sep-15
         ('C677', '5A3J2') : {
            'ATTRIBUTE' : 'numPhysHds',
            'DEFAULT'   : 2,
            2           : [97,90,83,76,76,69,62,55],     # 20-Oct-15
            4           : [97,90,83,76,69,62],  # 29-Sep-15
         },
         ('C677', '5A5J0') : [97,90,83,76,76,69,62,55],     # copied from C677+5A3J2
      },

      ('TDK', 'LSI5830')      : {
         'ATTRIBUTE'       : ('MediaType', 'HSA_WAFER_CODE'),
         ('R7.0', '5F057') : [104,97,83,76,69,62,55],          # 24-Dec-2015
         ('R8.0', '5F057') : [104,97,83,76,69,62,55],          # 24-Dec-2015
         ('R8.0', '5F608') : {
            'ATTRIBUTE' : 'numPhysHds',
            'DEFAULT'   : 2,
            2           : [104,97,83,76,69,62,55],          # 24-Dec-2015
            4           : [104,97,83,76,69,62,55,48],  # 30-Dec-15
         },
         ('R10',  '5F816') : [90,83,76,69,62,55,48,41],        # 03-Mar-2016 
         ('R10',  '5F057') : [90,83,76,69,62,55,48,41],        # 03-Mar-2016
         ('C572', '5F057') : [104,97,83,76,69,62,55],          # copied from R8
         ('C572', '5F608') : [104,97,83,76,69,62,55,48],       # 2D, 22-Jan-2016 copy from R8.0  
      },

      ('TDK', 'TI7551')       : {
         'ATTRIBUTE'       : ('MediaType', 'HSA_WAFER_CODE'),
         ('R7.0', '5F057') : [104,97,83,76,69,62,55,48,41], # 24-Dec-2015
         ('R8.0', '5F057') : [104,97,83,76,69,62,55,48,41], # 24-Dec-2015
         ('R8.0', '5F608') : [104,97,83,76,69,62,55,48,41], # 24-Dec-2015
         ('R10',  '5F816') : [97,83,76,69,62,55,48,41],     # 03-Mar-2016 
         ('R10',  '5F057') : [97,83,76,69,62,55,48,41],     # 03-Mar-2016
         ('C572', '5F057') : [104,97,83,76,69,62,55,48,41], # 25-Dec-2015
         ('C572', '5F608') : [104,97,83,76,69,62,55,48,41], # 2D, 30-Dec-2015		 
      },
   }

   OaMaxCap = {
      "ATTRIBUTE" : ('HGA_SUPPLIER', 'PREAMP_TYPE'),
      "DEFAULT"   : ('RHO', 'LSI5830'),
      ('RHO', 'LSI5830')      : {
         'ATTRIBUTE'       : ('MediaType', 'HSA_WAFER_CODE'),
         ('R5.1', 'OG8')   : [10*2,12*2,14*2,11*2],   # 23-Apr-15
         ('R6.4', 'OG8')   : [10*2,12*2,14*2,11*2],   # 23-Apr-15
         ('R5.1', 'NG8')   : [10*2,12*2,14*2,11*2],   # 23-Apr-15
         ('R5.1', 'O2Q')   : [10*2,12*2,14*2,11*2],   # 23-Apr-15 copied from RHO + LSI + R5.1 + OG8
         ('R5.1', 'N5T')   : [13*2,13*2,13*2,13*2,14*2,14*2,14*2],   # 04-May-15
         ('R5.1', 'NT4')   : [14*2,14*2,14*2,15*2,15*2,15*2,15*2],   # 05-Jun-15
         ('R5.1', 'N4Z')   : {
            'ATTRIBUTE' : 'numPhysHds',
            'DEFAULT'   : 2,
            2           : [14*2,14*2,15*2,15*2,15*2,15*2,14*2,14*2], # 25-Jun-15
            4           : [14*2,14*2,14*2,15*2,15*2,15*2,15*2],      # 16-Jun-15
         },
         ('R5.1', 'OT4')   : [28,28,28,28,28,28,26,28],  # copied from R7.0
         ('R6.4', 'NT4')   : [14*2,14*2,14*2,14*2,14*2,14*2,14*2,13*2],   # 24-Jul-15
         ('C677', 'NT4')   : [28,28,28,30,30,30,28,28],   # Reviewed by Andy chou 19-sep-15           
         ('R6.4', 'OT4')   : [14*2,14*2,14*2,14*2,14*2,14*2,13*2,13*2],   # 26-Jul-15
         ('R7.0', 'OT4')   : [28,28,28,28,28,28,26,28],   # Reviewed by Andy chou 18-sep-15
         ('R7.0', 'NT4')   : [28,28,28,28,28,28,30,28],   # Reviewed by Andy chou 19-sep-15
         ('R7.0', 'NL2')   : {
            'ATTRIBUTE' : 'numPhysHds',
            'DEFAULT'   : 2,
            2           : [28,28,28,28,28,28,28],   # 23-Sep-15
            4           : [28,28,28,28,28,28],      # 29-Sep-15
         },
         ('R7.0', 'PD7')   : { # copied from R7 + NL2
            'ATTRIBUTE' : 'numPhysHds',
            'DEFAULT'   : 2,
            2           : [28,28,28,28,28,28,28],   # 23-Sep-15
            4           : [28,28,28,28,28,28],      # 29-Sep-15
         },
         ('R8.0', 'NL2')   : {
            'ATTRIBUTE' : 'numPhysHds',
            'DEFAULT'   : 2,
            2           : [28,28,28,28,28,28,28],   
            4           : [28,28,28,28,28,28],      # 23-Oct-15, same as R7.0
         },		 
         ('R8.0', 'PD7')   : [28,28,28,28,28,28,28],   # 20-Nov-2015, 1D & 2D
         ('R10',  'PD7')   : [28,28,28,28,28,28],      # 03-Mar-2016
         ('C677', 'OT4')   : [28,28,28,28,28,28,28],   # Reviewed by Andy chou 18-sep-15
         ('C677', 'NL2')   : {
            'ATTRIBUTE' : 'numPhysHds',
            'DEFAULT'   : 2,
            2           : [28,28,28,28,28,28,28],   # 24-Sep-15
            4           : [28,28,28,28,28,28],      # 29-Sep-15
         },
         ('C677', 'PD7')   : { # copied from C677 + NL2
            'ATTRIBUTE' : 'numPhysHds',
            'DEFAULT'   : 2,
            2           : [28,28,28,28,28,28,28],   # 24-Sep-15
            4           : [28,28,28,28,28,28],      # 29-Sep-15
         },
         ('C572', 'PD7')   : { # copied from C677 + NL2
            'ATTRIBUTE' : 'numPhysHds',
            'DEFAULT'   : 2,
            2           : [28,28,28,28,28,28,28],   # 24-Sep-15
            4           : [28,28,28,28,28,28],      # 29-Sep-15
         },
         ('C655', 'NL2')   : [28,28,28,28,28,30],   # 29-Oct-15
         ('C572', 'NL2')   : [26,26,26,26,26,26,26],   # 11-Jan-16 2D.	
      },
      ('RHO', 'TI7551')       : {
         'ATTRIBUTE'       : ('MediaType', 'HSA_WAFER_CODE'),
         ('R5.1', 'O2Q')   : [10*2, 9*2,10*2, 9*2, 8*2],             # 20-Apr-15
         ('R5.1', 'NG8')   : [10*2, 9*2,10*2, 9*2, 8*2],             # 20-Apr-15
         ('R5.1', 'N5T')   : [10*2, 9*2,10*2, 9*2, 8*2],             # 20-Apr-15
         ('R5.1', 'OG8')   : [ 8*2, 9*2, 8*2,10*2, 8*2],             # 15-May-15
         ('R5.1', 'NT4')   : [10*2,10*2,11*2,10*2, 9*2, 8*2],        # 23-Jun-15
         ('R5.1', 'OT4')   : [16,16,18,18,18], # copied from R7.0
         ('R7.0', 'NT4')   : [20,20,20,20,20,20,20], # Reviewed by Andy chou 18-sep-15, same as old 17-Sep-15,RW2D          
         ('R5.1', 'N4Z')   : [10*2,10*2,11*2,10*2, 9*2, 8*2],        # 20-Jul-15
         ('R6.4', 'OT4')   : [10*2,10*2,10*2,11*2,10*2, 9*2, 8*2],   # 28-Aug-15
         ('R6.4', 'NT4')   : [10*2,10*2,10*2,10*2,10*2, 9*2, 8*2,10*2], # 08-Sep-15,RW2D        
         ('R7.0', 'OT4')   : [16,16,18,18,18], # Reviewed by Andy chou 18-sep-15
         ('R7.0', 'NL2')   : [20,20,20,20,20], # 10-Oct-15 1D, 19-Oct-15 2D same as 1D
         ('R7.0', 'PD7')   : [20,20,20,20,20], # copied from NL2
         ('R8.0', 'NL2')   : [20,20,20,20,20], # 18-Nov-15 2D   
         ('R8.0', 'PD7')   : [18,18,18,18,18], # 15-Dec-15
         ('R10',  'PD7')   : [20,20,20,20,20], # 03-Mar-2016
         ('C677', 'OT4')   : [16,16,18,18,18], # Reviewed by Andy chou 18-sep-15
         ('C677', 'NT4')   : [20,20,20,22,22,24,24,26],   # Newly added, reviewed by Andy chou 19-sep-15
         ('C677', 'NL2')   : {
            'ATTRIBUTE' : 'numPhysHds',
            'DEFAULT'   : 2,
            2           : [18,18,18,18,18], # 20-Oct-15
            4           : [20,20,20,20,20], # 27-Oct-15
         },
         ('C677', 'PD7')   : { # copied from NL2
            'ATTRIBUTE' : 'numPhysHds',
            'DEFAULT'   : 2,
            2           : [18,18,18,18,18], # 20-Oct-15
            4           : [20,20,20,20,20], # 27-Oct-15
         },
         ('C655', 'NL2')   : [18,18,18,18,18], # 29-Oct-15
         ('C572', 'PD7')   : [18,18,18,18,18], # 15-Jan-16
      },
      ('RHO', 'LSI5235')      : {
         'ATTRIBUTE'       : ('MediaType', 'HSA_WAFER_CODE'),
         'DEFAULT'         : ('R5.1', '5W'),
         ('R5.1', '5W')    : [28,28,28,28,28],           # Need to review if want to run. HAMR!!
         ('R5.1', 'BZ7')   : [28,28,28,28,28],           # Need to review if want to run. HAMR!!
      },
      ('HWY', 'LSI5830')      : {
         'ATTRIBUTE'       : ('MediaType', 'HSA_WAFER_CODE'),
         ('R5.1', '4A4C5') : [ 8*2, 9*2,10*2,12*2,14*2,15*2],        # 06-Apr-15
         ('R5.1', '4AHDD') : [ 8*2, 9*2,10*2,12*2,14*2,15*2],        # copied from 4A4C5
         ('R5.1', '4A60B') : [ 8*2, 9*2,10*2,12*2,14*2,15*2],        # copied from 4A4C5
         ('R5.1', '4A3C0') : [ 8*2, 9*2,10*2,12*2,14*2,15*2],        # copied from HWY + LSI + R5.1 + 4A4C5
         ('R5.1', '4AF1F') : [10*2,11*2,14*2,14*2,14*2],             # 17-Mar-15
         ('R5.1', '4AH63') : [10*2,11*2,14*2,14*2,14*2],             # copy 4AF1F
         ('R5.1', '4C6JH') : [12*2,13*2,13*2,14*2,14*2,15*2,15*2],   # 07-Jun-15
         ('R5.1', '4C430') : [13*2,13*2,13*2,14*2,14*2,15*2,15*2],   # 08-Jun-15
         ('R6.4', '4C430') : [13*2,13*2,13*2,14*2,14*2,15*2,15*2],   # 24-Jul-15
         ('R6.4', '5A2HH') : {
            'ATTRIBUTE' : 'numPhysHds',
            'DEFAULT'   : 2,
            2           : [14*2,14*2,14*2,14*2,14*2,15*2,15*2,13*2,11*2],   # 11-Aug-15
            4           : [14*2,14*2,14*2,14*2,14*2,15*2,14*2,14*2,14*2],   # 02-Sep-15 -> 18-Sep-15
         },
         ('R7.0', '5A2HH') : {
            'ATTRIBUTE' : 'numPhysHds',
            'DEFAULT'   : 2,
            2           : [28,28,28,28,28,30,28,28,28],   # Reviewed by Andy chou 18-sep-15
            4           : [24,24,28,28,28,30,28,28,30],   # Reviewed by Andy chou 19-sep-15, same as old
         },
         ('R7.0', '5A3J2') : [28,28,28,28,28,30,28,28,28],     # 22-Sep-15
         ('R8.0', '5A3J2') : [28,28,28,28,28,30,28,28,28],     # copied from R7 + 5A3J2
         ('R7.0', '5A2HG') : [28,28,28,28,28,30,28,28,28,28],  # 23-Sep-15 1D, 12-Oct-15 2D same as 1D
         ('R7.0', '5ABG5') : [28,28,28,28,28,28,30,28,28,28],  # 27-Oct-15
         ('R8.0', '5ABG5') : [28,28,28,28,28,28,30,28,28,28],  # copied from R7 + 5ABG5
         ('R7.0', '5A5J0') : [28,28,28,28,28,28,30,28,28,28],  # 04-Nov-15 1D, 12-Nov-15 2D same as 1D
         ('R8.0', '5A5J0') : [28,28,28,28,28,28,30,28,28,28],  # copy
         ('R8.0', '5A99G') : [28,28,28,28,28,28,30,28,28],     # 18-Nov-15 2D
         ('R8.0', '5A9BJ') : [28,28,28,28,28,28,30,28,28],     # copy      
         ('R8.0', '5F057') : [28,28,28,28,28,28,30,28,28],     # 19-Nov-2015
         ('R8.0', '4C677') : [28,28,28,28,28,28,30,28,28],     # 23-Nov-2015
         ('R10',  '5A99G') : [28,28,28,28,28,28,30,28,28,28],  # copied from R8
         ('R10',  '5A5J0') : [28,28,28,28,28,28,30,28,28,28],  # copied from R8
         ('C655', '4C677') : [28,28,28,28,28,30,28,28,28],     # 23-Nov-2015
         ('C677', '5A2HH') : {
            'ATTRIBUTE' : 'numPhysHds',
            'DEFAULT'   : 2,
            2           : [28,28,28,28,28,28,28,28,28],   # Reviewed by Andy chou 18-sep-15
            4           : [26,26,26,28,30,30,28,28,30],   # Reviewed by Andy chou 19-sep-15
         },
         ('C677', '5A3J2') : {
            'ATTRIBUTE' : 'numPhysHds',
            'DEFAULT'   : 2,
            2           : [28,28,28,28,28,30,28,28,28],      # 19-Sep-15
            4           : [28,28,28,28,28,28,28,28,30,28],   # 24-sep-15
         },
         ('C677', '5A2HG') : [28,28,28,28,28,30,28,28,28],      # 9-oct-15, 12-Oct-15 2D same as 1D
         ('C677', '5ABG5') : [28,28,28,28,28,30,28,28,28],      # 27-Oct-15
         ('C677', '5A5J0') : [28,28,28,28,28,30,28,28,28],      # 04-Nov-15
         ('C572', '5AA99') : [26,26,26,26,26,26,26,26],         # 11-Jan-16 2D.		 
         ('C572', '5A99G') : [26,26,26,26,26,26,26,26],         # 11-Jan-16 2D POR1.			 
         ('C448', '5A3J2') : [28,28,28,28,28,28,28,30,28,28],   # 25-Sep-15
      },
      ('HWY', 'TI7551')       : {
         'ATTRIBUTE'       : ('MediaType', 'HSA_WAFER_CODE'),
         ('R5.1', '4A4C5') : [ 8*2, 8*2, 9*2, 9*2,10*2,10*2,10*2],   # 30-Apr-15
         ('R5.1', '4AHDD') : [ 8*2, 8*2, 9*2, 9*2,10*2,10*2,10*2],   # copied from 4A4C5
         ('R5.1', '4A60B') : [14*2,14*2,14*2,15*2,15*2,15*2,15*2],   # 10-Jun-15
         ('R5.1', '4C6JH') : [ 8*2, 8*2, 8*2, 8*2, 9*2, 9*2,10*2,10*2],   # 18-Jun-15
         ('R5.1', '4C430') : [ 8*2, 8*2, 8*2, 9*2, 9*2, 9*2,10*2],   # 19-Jun-15
         ('R6.4', '4C430') : [10*2,10*2,10*2,11*2,11*2,12*2,12*2,11*2,10*2,10*2],   # 14-Aug-15
         ('R7.0', '5A2HH') : {
            'ATTRIBUTE' : 'numPhysHds',
            'DEFAULT'   : 2,
            2           : [18,18,18,18,18,16,14,16,14,16],    # Reviewed by Andy chou 18-sep-15, same as old 04-Sep-15
            4           : [14,14,14,16,16,18],                # Reviewed by Andy chou 19-sep-15
         },
         ('R7.0', '5A3J2') : [18,18,18,18,18,16,14,16,14,16], # 25-Sep-15
         ('R8.0', '5ABG5') : [18,18,18,18,18,16,14,16,14,16], # copied from R7 + 5A3J2
         ('R7.0', '5A2HG') : [20,20,20,20,20,20,20,20],      # 02-Nov-15, 2D
         ('R7.0', '5A5J0') : [20,20,20,20,20,20,20,20],      # 12-Nov-15 2D	 
         ('R8.0', '5A5J0') : [20,20,20,20,20,20,20,20],      # copy
         ('R8.0', '5A99G') : [20,20,20,20,20,20,20],         # 23-Nov-15 2D	 
         ('R8.0', '5A9BJ') : [20,20,20,20,20,20,20],         # copy
         ('R10',  '5A99G') : [20,20,20,20,20,20,20,20],      # copied from R8
         ('R10',  '5A5J0') : [20,20,20,20,20,20,20,20],      # copied from R8
         ('C677', '5A2HG') : [20,20,20,20,22,20,20,20],      # 02-Nov-15, 2D
         ('C677', '4C430') : [ 8*2, 8*2, 8*2, 9*2, 9*2, 9*2,10*2],   # 19-Jun-15 copied from HWY + TI + R5.1 + 4C430
         ('C677', '5A2HH') : [20,20,20,20,18,18,18,22],       # Reviewed by Andy chou 18-sep-15
         ('C677', '5A3J2') : {
            'ATTRIBUTE' : 'numPhysHds',
            'DEFAULT'   : 2,
            2           : [20,20,20,20,20,20,20,20],        # 20-Oct-15
            4           : [14,14,14,16,18,18],  # 29-Sep-15
         },
         ('C677', '5A5J0') : [20,20,20,20,20,20,20,20],        # copied from C677+5A3J2
      },

      ('TDK', 'LSI5830')      : {
         'ATTRIBUTE'       : ('MediaType', 'HSA_WAFER_CODE'),
         ('R7.0', '5F057') : [20,20,20,22,22,22,24],           # 24-Dec-2015
         ('R8.0', '5F057') : [20,20,20,22,22,22,24],           # 24-Dec-2015
         ('R8.0', '5F608') : {
            'ATTRIBUTE' : 'numPhysHds',
            'DEFAULT'   : 2,
            2           : [20,20,20,22,22,22,24],           # 24-Dec-2015
            4           : [20,20,22,24,24,24,24,26]  # 30-Dec-15
         },
         ('R10',  '5F816') : [26,26,26,26,26,26,26,26],        # 03-Mar-2016 
         ('R10',  '5F057') : [26,26,26,26,26,26,26,26],        # 03-Mar-2016 
         ('C572', '5F057') : [20,20,20,22,22,22,24],           # copied from R8
         ('C572', '5F608') : [20,20,22,24,24,24,24,26],        # 2D, 22-Jan-2016 copy from R8.0  
      },
      ('TDK', 'TI7551')       : {
         'ATTRIBUTE'       : ('MediaType', 'HSA_WAFER_CODE'),
         ('R7.0', '5F057') : [16,16,16,16,16,16,16,16,16],     # 24-Dec-2015
         ('R8.0', '5F057') : [16,16,16,16,16,16,16,16,16],     # 24-Dec-2015
         ('R8.0', '5F608') : [16,16,16,16,16,16,16,16,16],     # 24-Dec-2015
         ('R10',  '5F816') : [16,16,16,16,16,16,16,16],        # 03-Mar-2016 
         ('R10',  '5F057') : [16,16,16,16,16,16,16,16],        # 03-Mar-2016
         ('C572', '5F057') : [16,16,16,16,16,16,16,16,16],     # 25-Dec-2015
         ('C572', '5F608') : [14,14,14,14,14,14,14,14,14],     #2D, 30-Dec-2015		 
      },
   }

   IwMinCap = {
      "ATTRIBUTE" : 'FE_0332552_348429_TRIPLET_INTEGRATED_OW_HMS',
      "DEFAULT"   : 0,
      0           : {
         "ATTRIBUTE" : ('HGA_SUPPLIER', 'PREAMP_TYPE'),
         "DEFAULT"   : ('RHO', 'LSI5830'),
         ('RHO', 'LSI5830')      : {
            'ATTRIBUTE'       : ('MediaType', 'HSA_WAFER_CODE'),
            ('R5.1', 'OG8')   : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 
            ('R6.4', 'OG8')   : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 
            ('R5.1', 'NG8')   : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 
            ('R5.1', 'O2Q')   : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 
            ('R5.1', 'N5T')   : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 
            ('R5.1', 'NT4')   : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 
            ('R5.1', 'N4Z')   : {
               'ATTRIBUTE' : 'numPhysHds',
               'DEFAULT'   : 2,
               2           : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 
               4           : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 
            },
            ('R5.1', 'OT4')   : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # copied from R7.0
            ('R6.4', 'NT4')   : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 
            ('C677', 'NT4')   : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # Reviewed by Andy chou 19-sep-15         
            ('R6.4', 'OT4')   : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 
            ('R7.0', 'OT4')   : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # Reviewed by Andy chou 18-sep-15
            ('R7.0', 'NT4')   : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # Reviewed by Andy chou 19-sep-15
            ('R7.0', 'NL2')   : {
               'ATTRIBUTE' : 'numPhysHds',
               'DEFAULT'   : 2,
               2           : [20,20,20,20,20,20,20], # 23-Sep-15
               4           : [20,20,20,20,20,20],    # 29-Sep-15
            },
            ('R7.0', 'PD7')   : { # copied from R7 + NL2
               'ATTRIBUTE' : 'numPhysHds',
               'DEFAULT'   : 2,
               2           : [20,20,20,20,20,20,20], # 23-Sep-15
               4           : [20,20,20,20,20,20],    # 29-Sep-15
            },
            ('R8.0', 'NL2')   : {
               'ATTRIBUTE' : 'numPhysHds',
               'DEFAULT'   : 2,
               2           : [20,20,20,20,20,20,20],
               4           : [20,20,20,20,20,20],    # 23-Oct-15, same as R7.0
            },
            ('R8.0', 'PD7')   : [27,27,27,27,27,27,27], # 20-Nov-2015, 1D & 2D
            ('R10',  'PD7')   : [27,27,27,27,27,27,27], # 20-Nov-2015, 1D & 2D copied from R8
            ('C677', 'OT4')   : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # Reviewed by Andy chou 18-sep-15
            ('C677', 'NL2')   : {
               'ATTRIBUTE' : 'numPhysHds',
               'DEFAULT'   : 2,
               2           : [20,20,20,20,20,20,20], # 24-Sep-15
               4           : [20,20,20,20,20,20],    # 29-Sep-15
            },
            ('C677', 'PD7')   : { # copied from C677 + NL2
               'ATTRIBUTE' : 'numPhysHds',
               'DEFAULT'   : 2,
               2           : [20,20,20,20,20,20,20], # 24-Sep-15
               4           : [20,20,20,20,20,20],    # 29-Sep-15
            },
            ('C572', 'PD7')   : { # copied from C677 + NL2
               'ATTRIBUTE' : 'numPhysHds',
               'DEFAULT'   : 2,
               2           : [20,20,20,20,20,20,20], # 24-Sep-15
               4           : [20,20,20,20,20,20],    # 29-Sep-15
            },
            ('C655', 'NL2')   : [20,20,20,20,20,20], # 29-Oct-15
            ('C572', 'NL2')   : [27,27,27,27,27,27,27], # 11-Jan-16 2D.		 			
         },
         ('RHO', 'TI7551')       : {
            'ATTRIBUTE'       : ('MediaType', 'HSA_WAFER_CODE'),
            ('R5.1', 'O2Q')   : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 
            ('R5.1', 'NG8')   : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 
            ('R5.1', 'N5T')   : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 
            ('R5.1', 'OG8')   : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 
            ('R5.1', 'NT4')   : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 
            ('R7.0', 'NT4')   : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # Reviewed by Andy chou 19-sep-15     
            ('R5.1', 'N4Z')   : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 
            ('R5.1', 'OT4')   : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # copied from R7.0
            ('R6.4', 'OT4')   : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 
            ('R6.4', 'NT4')   : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], #  
            ('R7.0', 'OT4')   : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # Reviewed by Andy chou 18-sep-15
            ('R7.0', 'NL2')   : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 10-Oct-15 1D, 19-Oct-15 2D same as 1D
            ('R7.0', 'PD7')   : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # copied from NL2
            ('R8.0', 'NL2')   : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 18-Nov-15 2D 
            ('R8.0', 'PD7')   : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 23-Nov-2015
            ('R10',  'PD7')   : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 23-Nov-2015 copied from R8
            ('C677', 'OT4')   : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # Reviewed by Andy chou 18-sep-15
            ('C677', 'NT4')   : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # Newly added, reviewed by Andy chou 19-sep-15
            ('C677', 'NL2')   : {
               'ATTRIBUTE' : 'numPhysHds',
               'DEFAULT'   : 2,
               2           : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 20-Oct-15
               4           : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 27-Oct-15
            },
            ('C677', 'PD7')   : { # copied from NL2
               'ATTRIBUTE' : 'numPhysHds',
               'DEFAULT'   : 2,
               2           : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 20-Oct-15
               4           : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 27-Oct-15
            },
            ('C655', 'NL2')   : [20,20,20,20,20], # 29-Oct-15
            ('C572', 'PD7')   : [27,27,27,27,27], # 15-Jan-16
         },
         ('RHO', 'LSI5235')      : {
            'ATTRIBUTE'       : ('MediaType', 'HSA_WAFER_CODE'),
            'DEFAULT'         : ('R5.1', '5W'),
            ('R5.1', '5W')    : [10,10,10,10,10,10],           # Need to review if want to run. HAMR!!
            ('R5.1', 'BZ7')   : [10,10,10,10,10,10],           # Need to review if want to run. HAMR!!
         },
         ('HWY', 'LSI5830')      : {
            'ATTRIBUTE'       : ('MediaType', 'HSA_WAFER_CODE'),
            ('R5.1', '4A4C5') : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 
            ('R5.1', '4AHDD') : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 
            ('R5.1', '4A60B') : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 
            ('R5.1', '4A3C0') : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 
            ('R5.1', '4AF1F') : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 
            ('R5.1', '4AH63') : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # copy 4AF1F
            ('R5.1', '4C6JH') : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 
            ('R5.1', '4C430') : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 
            ('R6.4', '4C430') : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 
            ('R6.4', '5A2HH') : {
               'ATTRIBUTE' : 'numPhysHds',
               'DEFAULT'   : 2,
               2           : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 
               4           : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 18-Sep-15
            },
            ('R7.0', '5A2HH') : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # Reviewed by Andy chou 18-sep-15 (1D), 19-sep-15 (2D)
            ('R7.0', '5A3J2') : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 22-Sep-15
            ('R8.0', '5A3J2') : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # copied from R7 + 5A3J2
            ('R7.0', '5A2HG') : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 22-Sep-15 1D, 12-Oct-15 2D same as 1D
            ('R7.0', '5ABG5') : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 27-Oct-15
            ('R8.0', '5ABG5') : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # copied from R7 + 5ABG5
            ('R7.0', '5A5J0') : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 04-Nov-15 1D, 12-Nov-15 2D same as 1D
            ('R8.0', '5A5J0') : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # copy
            ('R8.0', '5A99G') : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 18-Nov-15 2D    
            ('R8.0', '5A9BJ') : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # copy   
            ('R8.0', '5F057') : [20, 20, 20, 20, 20, 20, 20, 20, 20], # 19-Nov-2015
            ('R8.0', '4C677') : [20,20,20,20,20,20,20,20,20], # 23-Nov-2015
            ('R10',  '5A99G') : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # copied from R8
            ('R10',  '5A5J0') : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # copied from R8
            ('C655', '4C677') : [20,20,20,20,20,20,20,20,20], # 23-Nov-2015
            ('C677', '5A2HH') : {
               'ATTRIBUTE' : 'numPhysHds',
               'DEFAULT'   : 2,
               2           : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20],   # Reviewed by Andy chou 18-sep-15
               4           : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20],   # Reviewed by Andy chou 19-sep-15
            },
            ('C677', '5A3J2') : {
               'ATTRIBUTE' : 'numPhysHds',
               'DEFAULT'   : 2,
               2           : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20],   # 19-Sep-15
               4           : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20],   # 24-sep-15
            },
            ('C677', '5A2HG') : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 7-oct-15, 12-Oct-15 2D same as 1D
            ('C677', '5ABG5') : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 27-oct-15
            ('C677', '5A5J0') : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 04-Nov-15
            ('C572', '5AA99') : [27,27,27,27,27,27,27,27], # 11-Jan-16 2D.	 
            ('C572', '5A99G') : [27,27,27,27,27,27,27,27], # 11-Jan-16 2D POR1.	
            ('C448', '5A3J2') : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 25-Sep-15
         },
         ('HWY', 'TI7551')       : {
            'ATTRIBUTE'       : ('MediaType', 'HSA_WAFER_CODE'),
            ('R5.1', '4A4C5') : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 
            ('R5.1', '4AHDD') : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 
            ('R5.1', '4A60B') : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 
            ('R5.1', '4C6JH') : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 
            ('R5.1', '4C430') : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 
            ('R6.4', '4C430') : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 
            ('R7.0', '5A2HH') : {
               'ATTRIBUTE' : 'numPhysHds',
               'DEFAULT'   : 2,
               2           : [34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34],   # Reviewed by Andy chou 18-sep-15
               4           : [34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34],   # Reviewed by Andy chou 19-sep-15
            },
            ('R7.0', '5A3J2') : [34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34], # 25-Sep-15
            ('R8.0', '5ABG5') : [34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34], # copied from R7 + 5A3J2
            ('R7.0', '5A2HG') : [27,27,27,27,27,27,27,27], # 02-Nov-15, 2D
            ('R7.0', '5A5J0') : [27,27,27,27,27,27,27,27], # 12-Nov-15 2D		 
            ('R8.0', '5A5J0') : [27,27,27,27,27,27,27,27], # copy
            ('R8.0', '5A99G') : [34,34,34,34,34,34,34],    # 23-Nov-2015
            ('R8.0', '5A9BJ') : [34,34,34,34,34,34,34],    # copy
            ('R10',  '5A99G') : [27,27,27,27,27,27,27,27], # copied from R8
            ('R10',  '5A5J0') : [27,27,27,27,27,27,27,27], # copied from R8
            ('C677', '5A2HG') : [27,27,27,27,27,27,27,27], # 02-Nov-15, 2D
            ('C677', '4C430') : [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], # 
            ('C677', '5A2HH') : [34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34], # Reviewed by Andy chou 18-sep-15
            ('C677', '5A3J2') : {
               'ATTRIBUTE' : 'numPhysHds',
               'DEFAULT'   : 2,
               2           : [34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34], # 20-Oct-15
               4           : [27,27,27,27,27,27], # 29-Sep-15
            },
            ('C677', '5A5J0') : [34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34], # copied from C677+5A3J2
         },

         ('TDK', 'LSI5830')      : {
            'ATTRIBUTE'       : ('MediaType', 'HSA_WAFER_CODE'),
            ('R7.0', '5F057') : [27,27,27,27,27,27,27],               # 24-Dec-2015
            ('R8.0', '5F057') : [27,27,27,27,27,27,27],               # 24-Dec-2015
            ('R8.0', '5F608') : {
               'ATTRIBUTE' : 'numPhysHds',
               'DEFAULT'   : 2,
               2           : [27,27,27,27,27,27,27],               # 24-Dec-2015
               4           : [27,27,27,27,27,27,27,27], # 30-Dec-15
            },
            ('R10',  '5F816') : [27,27,27,27,27,27,27,27,27],         # 03-Mar-2016 
            ('R10',  '5F057') : [27,27,27,27,27,27,27,27,27],         # 03-Mar-2016
            ('C572', '5F057') : [27,27,27,27,27,27,27],               # copied from R8
            ('C572', '5F608') : [27,27,27,27,27,27,27,27],            # 2D, 22-Jan-2016 copy from R8.0  
         },
         ('TDK', 'TI7551')       : { #
            'ATTRIBUTE'       : ('MediaType', 'HSA_WAFER_CODE'),
            ('R7.0', '5F057') : [27,27,27,27,27,27,27,27,27],  # 24-Dec-2015
            ('R8.0', '5F057') : [27,27,27,27,27,27,27,27,27],  # 24-Dec-2015
            ('R8.0', '5F608') : [27,27,27,27,27,27,27,27,27],  # 24-Dec-2015
            ('R10',  '5F816') : [27,27,27,27,27,27,27,27],     # 03-Mar-2016 
            ('R10',  '5F057') : [27,27,27,27,27,27,27,27],     # 03-Mar-2016
            ('C572', '5F057') : [27,27,27,27,27,27,27,27,27],  # 25-Dec-2015
            ('C572', '5F608') : [27,27,27,27,27,27,27,27,27],  # 30-Dec-2015		 
         },
      },
      1           : {
         "ATTRIBUTE" : ('HGA_SUPPLIER', 'PREAMP_TYPE'),
         "DEFAULT"   : ('RHO', 'LSI5830'),
         ('RHO', 'LSI5830')      : [27,30,33,36,39],     # 03-Mar-2016
         ('RHO', 'TI7551')       : [20,24,27,30,32],     # 03-Mar-2016
         ('RHO', 'LSI5235')      : [10, 10, 10, 10, 10], # HAMR Starwood mule. Need to review if want to run
         ('HWY', 'LSI5830')      : [20, 24, 28, 32, 36],
         ('HWY', 'TI7551')       : {
            'ATTRIBUTE'       : ('MediaType', 'HSA_WAFER_CODE'),
            'DEFAULT'         : ('R7.0', '5A5J0'),
            ('R5.1', '4A4C5') : [20, 24, 28, 32, 36],
            ('R5.1', '4AHDD') : [20, 24, 28, 32, 36],
            ('R5.1', '4A60B') : [20, 24, 28, 32, 36],
            ('R5.1', '4C6JH') : [20, 24, 28, 32, 36],
            ('R5.1', '4C430') : [20, 24, 28, 32, 36],
            ('R6.4', '4C430') : [20, 24, 28, 32, 36],
            ('R7.0', '5A2HH') : [34, 36, 38, 40, 42],
            ('R7.0', '5A3J2') : [34, 36, 38, 40, 42],
            ('R8.0', '5ABG5') : [34, 36, 38, 40, 42],
            ('R7.0', '5A2HG') : [27, 30, 33, 36, 39],
            ('R7.0', '5A5J0') : [27, 30, 33, 36, 39],	 
            ('R8.0', '5A5J0') : [27, 30, 33, 36, 39],
            ('R8.0', '5A99G') : [34, 36, 38, 40, 42],
            ('R8.0', '5A9BJ') : [34, 36, 38, 40, 42],
            ('R10',  '5A99G') : [27, 30, 33, 36, 39], # copied from R8
            ('R10',  '5A5J0') : [27, 30, 33, 36, 39], # copied from R8
            ('C677', '5A2HG') : [27, 30, 33, 36, 39],
            ('C677', '4C430') : [20, 24, 28, 32, 36],
            ('C677', '5A2HH') : [34, 36, 38, 40, 42],
            ('C677', '5A3J2') : {
               'ATTRIBUTE' : 'numPhysHds',
               'DEFAULT'   : 2,
               2           : [34, 36, 38, 40, 42],
               4           : [27, 30, 33, 36, 39],
            },
            ('C677', '5A5J0') : [34, 36, 38, 40, 42],
         },
         ('TDK', 'LSI5830'): [27,30,33,36],     # 03-Mar-2016
         ('TDK', 'TI7551') : [27,30,33,36,39],  # 03-Mar-2016
      },
   }

   OaMinCap = {
      "ATTRIBUTE" : ('HGA_SUPPLIER', 'PREAMP_TYPE'),
      "DEFAULT"   : ('RHO', 'LSI5830'),
      ('RHO', 'LSI5830')   : [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],   # 03-Mar-2016
      ('RHO', 'TI7551')    : [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],   # 03-Mar-2016
      ('HWY', 'LSI5830')   : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      ('HWY', 'TI7551')    : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      ('TDK', 'LSI5830')   : [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],   # 03-Mar-2016
      ('TDK', 'TI7551')    : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],   # 03-Mar-2016
   }
else:
   IwMaxCap = {
      "ATTRIBUTE" : 'HGA_SUPPLIER',
      "DEFAULT" : 'RHO',
      "RHO" : [126],
      "HWY" : [126],
      "TDK" : [126],
   }
   OaMaxCap = {
      "ATTRIBUTE" : 'HGA_SUPPLIER',
      "DEFAULT" : 'RHO',
      "RHO" : [30],
      "HWY" : [30],
      "TDK" : [30],
   }
   IwMinCap = {
      "ATTRIBUTE" : 'HGA_SUPPLIER',
      "DEFAULT" : 'RHO',
      "TDK" : [20],
      "RHO" : [20],
   }
   OaMinCap = {
      "ATTRIBUTE" : 'HGA_SUPPLIER',
      "DEFAULT" : 'RHO',
      "TDK" : [0],
      "RHO" : [0],
   }
Iw_Add_Mgn = 7 # backoff from IwMaxCap to provide additional margin, this is per legacy 0~15DAC setting
Iw_Add_Mgn_Limit = { # Iw_Add_Mgn will not be applied if Max Iw Limit is equal to or below this
   "ATTRIBUTE" : 'HGA_SUPPLIER',
   "DEFAULT" : 'RHO',
   "RHO" : 0,
   "HWY" : 41,
   "TDK" : 41,
} 

Osa_Add_Mgn = 0 # backoff from OaMaxCap to provide additional margin, this is per legacy 0~15DAC setting
OdMaxCap = {
   "ATTRIBUTE" : 'HGA_SUPPLIER',
   "DEFAULT" : 'RHO',
   "TDK" : 30,
   "RHO" : 30,
}
OdMinCap = {
   "ATTRIBUTE" : 'HGA_SUPPLIER',
   "DEFAULT" : 'RHO',
   "TDK" : 0,
   "RHO" : 0,
}
IwSweepStep = 7
OsaSweepStep = 2
OsdSweepStep = 2
OsdStepRange = {
   "ATTRIBUTE" : 'PREAMP_TYPE',
   "DEFAULT" : 'LSI5830',
   "LSI5830": 2,
   "TI7551" : 1, 
}

EwacIWFactor = {  # Factor for IW Max Computation based on EWAC
   "ATTRIBUTE" : 'HGA_SUPPLIER',
   "DEFAULT" : 'RHO',
   "TDK" : 41,
   "RHO" : 20,
}
EwacIWSlope = {  # Slope for IW Max Computation based on EWAC
   "ATTRIBUTE" : 'HGA_SUPPLIER',
   "DEFAULT" : 'RHO',
   "TDK" : -8,
   "RHO" : -4,
}
# For Rosewood7 Strong Write
OSA_MAX_SWEEP = 30
OSD_MAX_SWEEP = 30
OSA_ADD_MARGIN = 0 # Additional Margin for OSA
SWEEP_STEP_OSA_OSD = 4 #Step Size for OSA/OSD
SWEEP_STEP_IW = 7 #Step Size for IW
SWEEP_RANGE_IW = 7 # Number of steps to sweep for Iw from Start Triplet
WPC_SLOPE_LIMIT = 0.02 #0.005 #0.5
WPC_INTERCEPT_LIMIT = 2.2#1.0 #`1
START_TRIPLET = [32,4,4] # OSD is overriden by default triplet
WPC_ZONES = [0,75,149]

TPI_Write_Fault_Threshold = 0.12
Triplet_ATI_STE_Test_Zone = {
      'ATTRIBUTE':'numZones',
      'DEFAULT': 60,
      17: [0, 16],
      24: [0, 22],
      31: [0, 30],
      60: [0, 59],
      150:[0, 149],
}

TPI_EWAC_Coeff = {
       "ATTRIBUTE" : 'HGA_SUPPLIER',
       "DEFAULT" : 'RHO',
       "TDK" : {
               "SLOPE"     : -4.4499029,
               "INTERCEPT" : 6.2756329,
               "NOMINAL"   : 2.5,
               },
       "RHO" : {
               "SLOPE"     : -3.9027112,
               "INTERCEPT" : 5.5239075,
               "NOMINAL"   : 2.5,
               },
}
TRIPLET_CRITERIA_ATI_STE_51  = {
      'ATTRIBUTE':'FE_0258915_348429_COMMON_TWO_TEMP_CERT',
      'DEFAULT'  : 0,
      0          : {
         'poorer_ber_delta_limit'      : (0, 0.15, 0, 1.10), # (ATI flag, ATI Limit, STE flag, STE Limit), flag = 1 means enabled this limit check
         'delta_limit'                 : (0, 2.0, 0, 1.0),
         'worse_ber_limit'             : (0, 5.0, 1, 6.0),
         },
      1          : {
         'poorer_ber_delta_limit'      : (0, 0.15, 1, 1.5), # (ATI flag, ATI Limit, STE flag, STE Limit), flag = 1 means enabled this limit check
         'delta_limit'                 : (0, 2.0, 0, 1.0),
         'worse_ber_limit'             : (0, 5.0, 1, 7.0),
         },
}
TRIPLET_CRITERIA_OW_61 = 20.0
TRIPLET_CRITERIA_HMSC_211 = -1.0
##################### End- On the Fly Triplet #####################################


MeasureHMS_211 = {
   'HMS_MAX_PUSH_RELAX' : 490,
   'HMS_STEP'           : 1,
   'TLEVEL'             : 5,
   'TARGET_SER'         : 5,
   'NUM_SQZ_WRITES'     : 0,
   'START_OT_FOR_TPI'   : 0,
   'CWORD2'             : 0x0003,
}

if testSwitch.VBAR_HMS_V2:
   MeasureHMS_211.update({
      'TLEVEL'             : 5,
      'CWORD2'             : 0x0003,
      'HMS_STEP'           : 1,
      'HMS_MAX_PUSH_RELAX' : 75,
   })

if testSwitch.VBAR_HMS_V4:
   MeasureHMS_211.update({
      'TLEVEL'             : 0x0005,
      'TARGET_SER'         : 0x0005,
      'HMS_START'          : 20,
      #'BER_PENALTY'        : (0, 24, 17, 60),   # TLEVEL, THRESHOLD, TARGET_SER, SLOPE   2.4 = (0, 24, 17, 60) 2.3 = (0, 30, 16, 60) 2.2 = (0, 37, 17, 60) 2.1 = (0, 46, 17, 60)  2.0 = (0, 57, 17, 60)
   })

if testSwitch.SMR:
   MeasureHMS_211['CWORD6'] = 0x001 #Reset Read offset

AltMeasureHMS_211 = MeasureHMS_211.copy()

Triplet_prm_HMS_211 = {'test_num'           : 211,
   'prm_name'           : 'MeasureHMS_211',
   'HEAD_MASK'          : 0xFFFF, #hd_mask,
   'ZONE_POSITION'      : 198,#TP.VBAR_ZONE_POS,
   'NUM_TRACKS_PER_ZONE': 6,
   'HMS_MAX_PUSH_RELAX' : 300,
   'HMS_STEP'           : 1,
   'ADJ_BPI_FOR_TPI'    : VbarAdjBpiForTpi,
   'THRESHOLD'          : 90,
   'CWORD1'             : 0x600C,
   'CWORD2'             : 0x0003,
   'CWORD6'             : 0x0001,
   'SET_OCLIM'          : 655,
   'TARGET_SER'         : 5,
   'TLEVEL'             : 15,
   'NUM_SQZ_WRITES'     : 0,
   'RESULTS_RETURNED'   : 0x000F,
   'timeout'            : 3600, #*hdCnt*znCnt,
   'spc_id'             : 0,
   'HMS_START'          : 20,
}


# Uncomment and Add AltMeasureHMS_211 updates here for modified CVbarHMS2 class operation
#if testSwitch.VBAR_HMS_V4:
   #AltMeasureHMS_211.update({ })


MeasureBPI_211 = {
   'CWORD1'             : 0x0001,
   'CWORD2'             : 0x0010,
   'THRESHOLD'          : 16,
   'TLEVEL'             : 0,
   'TARGET_SER'         : VbarTargetSER,
   'SET_OCLIM'          : 0x04CC,
   }

if testSwitch.VBAR_HMS_V2:
   MeasureBPI_211.update({
      'CWORD1'             : 0x0045,
   })

MeasureTPI_211 = {
   'TLEVEL'             : 3,
   'TARGET_SER'         : VbarTargetSER,
   'SET_OCLIM'          : 0x04CC,
   'THRESHOLD'          : 16,
   'TPI_TLEVEL'         : TPI_TLEVEL,
}

#TPI_Feedback_Margin = 10

MeasureBPITPI_211 = {
   'SET_OCLIM'          : 0x04CC,
   'MAX_RANGE'          : 110,
   'TARGET_SER'         : VbarTargetSER,
   'THRESHOLD'          : 16,
}

if testSwitch.BF_0148756_208705_TPI_TLEVEL_CONTROL:
   MeasureBPITPI_211.update({
      'TPI_TLEVEL'      : 5,
   })

#used for  measuring all zn HMS, TPI, BPI together.
MeasureBPITPI_ZN_211 = {}   #nothing to update for now. actual parm defined in Vbar.py

if testSwitch.VBAR_HMS_V4:
   MeasureTPI_211.update({
      'TLEVEL'          : 50,
   })

   MeasureBPITPI_211.update({
      'TPI_TLEVEL'      : 50,
   })

if testSwitch.FE_0150604_208705_P_VBAR_HMS_PHASE_2_INCREASE_TGT_CLR:
   MeasureBPITPI_WP_211 = MeasureBPITPI_211.copy()
   MeasureBPITPI_WP_211.update({
      'prm_name'        : 'MeasureBPITPI_WP_211',
      'CWORD1'          : 0x0067,
   })

   MeasureBPITPI_ZN_211 = MeasureBPITPI_211.copy()
   MeasureBPITPI_ZN_211.update({
      'prm_name'        : 'MeasureBPITPI_ZN_211',
      'CWORD2'          : 0x0014,
      'ADJ_BPI_FOR_TPI' : 0,
      'CWORD1'          : 0x0027,
   })

MeasureTPIOnly_211 = MeasureTPI_211.copy()
MeasureTPIOnly_211.update({
   'ADJ_BPI_FOR_TPI'       : 0,
})

VBAR_TCC = {
   'WC_HOT_OFFSET'         : 0,
   'WC_COLD_OFFSET'        : 0,
   }

# Threshold for failing heads with high clearance sensitivity
# One threshold for each of the 5 write power zones (zn : threshold)
# Metric is BPICwp - BPICzn
VBARDeltaBPICThresholds = {
                           0  : -0.099,
                           2  : -0.082,
                           8  : -0.066,
                           14 : -0.05,
                           16 : -0.038,
                          }

# Fail the delta BPIC spec if the number of failing zones
# Equals or exceeds this number
VBARDeltaBPICZoneFailureLimit = 3

STE_Prm_213 = {
   'prm_name'                 : 'STE_Prm_213',
   'test_num'                 : 213,
   'timeout'                  : 195000,  # 16 hours->which maps to test time of abut 8 hours.
   'spc_id'                   : 200,
   "HEAD_RANGE"               : (0x00FF,),
   "ZONE_POSITION"            : (5,),            # zone position set to 90%
   "TEST_CYL"                 : (0xFFFF,0xFFFF,),  # set this to all FFFF if using zone masks
   "CWORD1"                   : (0xC121),
   "CWORD2"                   : (0x3407),
   "NBR_MEAS_REPS"            : (1,),       # number of times to do STE writes / measure per-track BER
   "THRESHOLD"                : (194,),     # maximum allowed BASELINE_BER obtained prior to erasure, 390 corresponds to max BER of -3.9 decades.
   "NUM_TRACKS_PER_ZONE"      : (20,),      # number of tracks on either side of the center track to write
   "TARGET_TRK_WRITES"        : (40,),      # 47=50K, number of center track STE writes, xx translates to 10^(x.x), 50 is 100K
   "NUM_SQZ_WRITES"           : (1,),       # number of writes when writing per-track data
   "NUM_ADJ_ERASE"            : (20,),
   "OFFSET_SETTING"           : (0,0,1,),
   "READ_OFFSET"              : (0x0000,),
   "S_OFFSET"                 : (1,),
   "PATTERNS"                 : (0x80,0x01,0x00,),
   "AC_ERASE"                 : (),
   "BITS_TO_READ"             : (0x0107,),  # in all cases pass at least 10e7 bits, more will be required if BER is better than -6.5 but then ERRORS_TO_READ min kicks in so more bits are passed
   "ERRORS_TO_READ"           : (50,),      # keep passing bits til this minimum number of errors is read, 0 = disable
   "TLEVEL"                   : (4,),       # ECC error code correction level
   "STE_MAX_ERASURE_SPEC"     : (500,),     # maximum allowed BER loss due to STE, 150 = 1.50 decades of BER loss
   "BER_LIMIT"                : (400,),     # BER_AFTER_STE_SPEC, maximum allowed BER after STE, 400 = -4.00
   "DAMPING_OFFSET"           : (1,1),      # value of 3 is the minimum allowed osa, if default is 3 or less then no osa backoff occurs.
   "DATA_SET1"                : (0,15,30,0),  #DOS_STE ranges that trigger different thresholds
   "DATA_SET2"                : (1,2,3,0),     #DOS_ATI values that get written to RAP (currently not enabled)
   "DATA_SET3"                : (4,8,12,0),  #DOS_STE ranges that trigger different thresholds
   "DATA_SET4"                : (0,1,2,3),     #DOS_STE values that get written to RAP.
   'MAX_RADIUS'               : 1195,
   'MAX_ATI_ERR_RATE_SPEC'    : (194,),
   'MIN_ERR_RATE'             : 200,
   'ZONE_MASK'                : (0, 2),
   'NUM_GROUPS_LIMIT'         : (5,),
   'LOG10_BER_SPEC'           : (170,),
   'PAD_SIZE'                 : 61184,
   'GAP_SIZE'                 : 188,
   'FREQUENCY'                : 210,
   'ZONE_MASK_EXT'            : (0, 2),
   # Below are based on gap cal values - need to be tuned per program, if anything other than MR SAS ever uses this test
   "MIN_MAX_WRT_CUR"          : (0x05,0xFF,),  # VERY IMPORTANT! Test will use unitialized values to set channel registers
   #    if Iw_max is not set to 0xff.  5 is the minimum allowed Iw DAC setting.
   'FAIL_SAFE'                : (),
   'failSafe'                 : 1         # Allows fail-safe for all failure modes
}


##################### USER AREA FLAWSCAN #####################################
FLAWSCAN_DEFREQUENCY = 700 ## Flaw scan freq changed from 850 per Core team request
FLAWSCAN_DEFREQUENCY_320G = 1000

prm_Fine_Tune_Threshold_109 = {
   'test_num'             : 109,
   'prm_name'             : 'prm_Fine_Tune_Threshold_109',
   'timeout'              : 10000*numHeads,
   'spc_id'               : 1,
   "CWORD1"               : 0x0040,   # REPORT_VERS
   "CWORD2"               : 0x2880,   # FSB mode
   "CWORD3"               : 0x003F,   # Enable FINE_TUNE_THRESHOLD
   "CWORD4"               : 0x2000,   # Disable DETCR_PREAMP_SUPPORT
   "ZONE_MASK"            : (0xFFFF, 0xFFFF),
   "ZONE_MASK_EXT"        : (0xFFFF, 0xFFFF),
   "HEAD_RANGE"           : 0x00FF,
   "RW_MODE"              : 0x4000,
   "VERIFY_GAMUT"         : (2, 3, 20),
   "FSB_SEL"              : (1,1),
   "SET_OCLIM"            : {
      'ATTRIBUTE'  : 'BG',
      'DEFAULT'    : 'OEM1B',
      'OEM1B'      : 5,
      'SBS'        : 2,
      },
   "FREQUENCY"            : FLAWSCAN_DEFREQUENCY,
   "IGNORE_UNVER_LIMIT"   : (),
   "ERRS_B4_SFLAW_SCAN"   : 1,
   "NUM_TRACKS_PER_ZONE"  : 200,
   "POS_THRES_OPTI_CRITERIA" : (1, 5, 8),     # (PosBadTrack, PosQualCnt, PosDeltaThres)
   "NEG_THRES_OPTI_CRITERIA" : (150, 120, 5), # (NegBadTrack, NegQualCnt, NegDeltaThres)
}

prm_AFS_2T_Write_109 = {
   'test_num'           : 109,
   'prm_name'           : 'prm_AFS_2T_Write_109',
   'timeout'            : 8000*numHeads,
   'spc_id'             : 1,
   "CWORD1"             : 0x0006,                 # REWRITES (0x0004), UNCERT_TO_SKIPTRACK (0x0002)
   "CWORD2"             : 0xC800,                 # XPLUSV_SCAN (0x8000), PARA_JOG_SCRN (0x4000), REPORT_SUMMARY_TABLES (0x0800)
   "HEAD_RANGE"         : 0x00FF,
   "START_CYL"          : (0x0000,0x0000,),
   "END_CYL"            : (0xFFFF,0xFFFF,),
   "RW_MODE"            : 0x0100,
   "HEAD_CLAMP"         : 900,
   "TRACK_LIMIT"        : 80,
   "ZONE_LIMIT"         : 50000,
   "SET_OCLIM"          : {
      'ATTRIBUTE'  : 'BG',
      'DEFAULT'    : 'OEM1B',
      'OEM1B'      : 5,
      'SBS'        : 2,
      },  #10 equv 10% OCLim, 5 equv 12% OCLim
   "SFLAW_OTF"          : (),
   "ERRS_B4_SFLAW_SCAN" : 1,
   "FREQUENCY"          : FLAWSCAN_DEFREQUENCY,
   }


if testSwitch.RUN_ZEST:
   prm_AFS_2T_Write_109.update({"CWORD2": 0x8800,})


if testSwitch.UMP_SHL_FLAWSCAN:
   #=== UMP - write parm
   PRM_WRITE_UMP_ZONES_109 = prm_AFS_2T_Write_109.copy()
   PRM_WRITE_UMP_ZONES_109.update({
      'prm_name': 'PRM_WRITE_UMP_ZONES_109',
      'spc_id'  : 1091,
      "CWORD3"  : 0x0200,
   })
   #=== SHL - write parm
   PRM_WRITE_SHL_ZONES_109 = prm_AFS_2T_Write_109.copy()
   PRM_WRITE_SHL_ZONES_109.update({
      'prm_name': 'PRM_WRITE_SHL_ZONES_109',
      'spc_id'  : 1091,
      "CWORD3"  : 0x0100,
   })

if testSwitch.WA_0128885_357915_SEPARATE_OD_ODD_EVEN_FLAWSCAN:
   endODScanCyl = 0x11200  # End of agressive OD scan range
   numWritePasses = 3 # Number of write passes for aggressive scan

   prm_AFS_2T_Write_OD_109 = prm_AFS_2T_Write_109.copy()
   prm_AFS_2T_Write_109['START_CYL'] = CUtility.ReturnTestCylWord(endODScanCyl + 1)  # Set starting cylinder for normal flawscan
   prm_AFS_2T_Write_OD_109({
      'END_CYL'            : CUtility.ReturnTestCylWord(endODScanCyl),  # Set OD scan ending cylinder
      'prm_name'           : 'prm_AFS_2T_Write_OD_109',
   })

if testSwitch.shortProcess:
   prm_AFS_2T_Write_109.update({
      'END_CYL'            : (0, 0x4E20), # 20,000
   })

prm_basic_AFS_2T_Write_109 = {
   'test_num'              : 109,
   'prm_name'              : 'prm_basic_AFS_2T_Write_109',
   'timeout'               : 1800,
   'spc_id'                : 1,
   'CWORD1'                : 0x0016,      # Bit 2='rewrites' but it does nothing
   'CWORD2'                : 0x0800,
   'RW_MODE'               : 0x0100,
   'SFLAW_OTF'             : (),          # Integrated Servo FS in A Data FS
   }

prm_AFS_CM_Read_109_LM94 = {
   'test_num'           : 109,
   'prm_name'           : 'prm_AFS_CM_Read_109',
   'timeout'            : 10000*numHeads,
   'spc_id'             : 1,
   "CWORD1"             : 0x0072,
   "CWORD2"             : 0x2880,
   "HEAD_RANGE"         : 0x00FF,
   "START_CYL"          : (0x0000,0x0000),
   "END_CYL"            : (0xFFFF,0xFFFF),
   "RW_MODE"            : 0x4000,
   "HEAD_CLAMP"         : 150,
   "TRACK_LIMIT"        : 80,
   "ZONE_LIMIT"         : 65000,
   "VERIFY_GAMUT"       : (2, 3, 20),
   "DEFECT_LENGTH"      : 3,
   "THRESHOLD"          : 20,                 # drop-out 1
   "THRESHOLD2"         : 0x007F,             # drop-in 1
   "FSB_SEL"            : (1,1),              # mask: NOT USED, sel: FS_BUS_SEL for formatter
   "SET_OCLIM"          : {
      'ATTRIBUTE'  : 'BG',
      'DEFAULT'    : 'OEM1B',
      'OEM1B'      : 5,
      'SBS'        : 2,
      },                  # 10 equv 10% OCLim, 5 equv 12% OCLim
   "SFLAW_OTF"          : (),
   "IGNORE_UNVER_LIMIT" : (),
   "ERRS_B4_SFLAW_SCAN" : 1,
   "VERIFY_COUNT"       : 25,                 # Skip the track if too many verified counts.
   "GAIN"               : 0,                  # Flag detcr TA if threshold need extra adjust from T094,+ deduct, - increase thresold
   #"ZONE_POSITION"      : 180,
   "E_FACTOR"           :  {
            "ATTRIBUTE"   : "CAPACITY_PN",
            "DEFAULT"     : "500G",
            "1000G"     : 300,
            "750G"      : 400,
            "500G"      : 300,
            "320G"      : 400,
       },
   "FREQUENCY"          : FLAWSCAN_DEFREQUENCY,
}

DETCR_SUPPORT_BIT = 13

if testSwitch.MARVELL_SRC:
   prm_AFS_CM_Read_109 = {
      'test_num'           : 109,
      'prm_name'           : 'prm_AFS_CM_Read_109',
      'timeout'            : 11500*numHeads,
      'spc_id'             : 1,
      'HEAD_CLAMP'         : 600,          # per Kyoumarss, 2011APR12
      'CWORD1'             : {
         'EQUATION' : "0x0072 | (testSwitch.FE_228371_DETCR_TA_SERVO_CODE_SUPPORTED)<< 10"
      },
      'CWORD2'             : 0x2880,       # report frequency scale table
      'CWORD4'             : {
         'EQUATION' : "0x0020 | (not testSwitch.FE_228371_DETCR_TA_SERVO_CODE_SUPPORTED)<<TP.DETCR_SUPPORT_BIT | testSwitch.FE_PREAMP_DUAL_POLARITY_SUPPORT_DETCR_TA << 15"
      },  #Enable Read Training
      'HEAD_RANGE'         : 0x00FF,
      'START_CYL'          : (0x0000,0x0000),
      'END_CYL'            : (0xFFFF,0xFFFF),
      'RW_MODE'            : 0x4000,
      'FSB_SEL'            : (0x0000, 0x0001),           # actually overwrite by 'SET_XREG08'
      'SET_OCLIM'          : {
         'ATTRIBUTE'  : 'BG',
         'DEFAULT'    : 'OEM1B',
         'OEM1B'      : 5,
         'SBS'        : 2,
         },                          # 10 equv 10% OCLim, 5 equv 12% OCLim
      'TRACK_LIMIT'        : 80,
      'ZONE_LIMIT'         : 65000,
      'IGNORE_UNVER_LIMIT' : (),
      'SFLAW_OTF'          : (),                         # Integrated Servo FS in A Data FS
      'FREQUENCY'          : FLAWSCAN_DEFREQUENCY,
      'ERRS_B4_SFLAW_SCAN' : 1,
      'VERIFY_GAMUT'       : (2, 3, 10),
      'VERIFY_COUNT'       : 25,                         # Skip the track if too many verified counts.
      'DEFECT_LENGTH'      : 3,
      'SET_XREG00'         : ( 0x00AF, 127,    0xC60 ),  # DFS_TE_THR
      'SET_XREG01'         : ( 0x00AD, 127,    0xC60 ),  # MAD DROP IN 1 THRESHOLD(SUPER BIT)
      'SET_XREG02'         : ( 0x00AE, 127,    0xC60 ),  # MAD DROP IN 2 THRESHOLD (SUPER BIT)
      'SET_XREG03'         : ( 0x00AA, 0,      0xCCC ),  # DOUBLING CLOCL FREQUENCY FOR 4T FLAW SCAN
      'SET_XREG04'         : ( 0x00AD, 51,     0xCE8 ),  # MAD DROP OUT 1 THRESHOLD(VOID DETECTION)
      'SET_XREG05'         : ( 0x00AE, 51,     0xCE8 ),  # MAD DROP OUT 2 THRSSHOLD (VOID DETECTION)
      'SET_XREG06'         : ( 0x00AC, 2,      0xC54 ),  # WINDOW SIZE SELECT 1
      'SET_XREG07'         : ( 0x00AF, 2,      0xCBA ),  # WINDOW SIZE SELECT 2
      'SET_XREG08'         : ( 0x00AB, 0x1FBF, 0xCC0 ),  # Enable Drop-out1 detector.
      'HD_TYPE'            : {
         'ATTRIBUTE'       : 'HGA_SUPPLIER',
         'DEFAULT'         : 'RHO',
         'RHO'             : 0,
         'TDK'             : 1,
         'HWY'             : 2,
         },
      }

else:
   prm_AFS_CM_Read_109 = {
      'test_num'           : 109,
      'prm_name'           : 'prm_AFS_CM_Read_109',
      'timeout'            : 11500*numHeads,
      'spc_id'             : 1,
      'CWORD1'             : 0x0443,
      'CWORD2'             : 0x0882,
      'CWORD4'             : {
         'EQUATION' :  "0x0020 | (not testSwitch.FE_228371_DETCR_TA_SERVO_CODE_SUPPORTED)<<TP.DETCR_SUPPORT_BIT | testSwitch.FE_PREAMP_DUAL_POLARITY_SUPPORT_DETCR_TA << 15"
      },    #Enable Read Training
      'HEAD_RANGE'         : 0x00FF,
      'START_CYL'          : (0x0000,0x0000),
      'END_CYL'            : (0xFFFF,0xFFFF),
      'RW_MODE'            : 0x4000,
      'PASS_INDEX'         : 0,
      'HEAD_CLAMP'         : 600,
      'TRACK_LIMIT'        : 80,
      'ZONE_LIMIT'         : 65000,
      'DIVISOR'            : 75,
      'TA_THRESHOLD'       : 20,
      'VERIFY_GAMUT'       : (2, 3, 10),
      'FSB_SEL'            : { # mask: NOT USED, sel: FS_BUS_SEL for formatter
         'ATTRIBUTE'    : 'FE_0245014_470992_ZONE_MASK_BANK_SUPPORT',
         'DEFAULT'      : 0,
         0              : (0x0089, 0x0000),
         1              : (0x0081, 0x0000),
      },
      'SET_OCLIM'          : {
         'ATTRIBUTE'  : 'BG',
         'DEFAULT'    : 'OEM1B',
         'OEM1B'      : 5,
         'SBS'        : 2,
         },                  # 10 equv 10% OCLim, 5 equv 12% OCLim
      'SFLAW_OTF'          : (),
      'IGNORE_UNVER_LIMIT' : (),
      'ERRS_B4_SFLAW_SCAN' : 1,
      'VERIFY_COUNT'       : 25,                 # Skip the track if too many verified counts.
      #'ZONE_POSITION'      : 180,
      'FREQUENCY'          : FLAWSCAN_DEFREQUENCY,
      'SET_XREG00'         : ( 0x0A12, 0x0000, 0x1bcc ),   # TAEP_OFF
      'SET_XREG01'         : ( 0x0A12, 0x0003, 0x1b74 ),   # TA_HOLD
      'SET_XREG02'         : ( 0x0A12, 0x0003, 0x1b30 ),   # TA_DLY
      'SET_XREG03'         : ( 0x1215, 0x0004, 0x1bfc ),   # ZGR_DIFF
      'SET_XREG04'         : ( 0x129c, 0x0000, 0x1b30 ),   # ZGSENR
      'SET_XREG05'         : ( 0x1211, 0x0000, 0x1b76 ),   # GUGFLAW
      'SET_XREG06'         : ( 0x123c, 0x0003, 0x1bb8 ),   # QMLEN2
      'SET_XREG07'         : ( 0x1210, 0x0005, 0x1bec ),   # GUGACQR
      'SET_XREG08'         : ( 0x1210, 0x0000, 0x1ba8 ),   # GUGR
      'SET_XREG14'         : ( 0x121e, 0x0001, 0x1b32 ),   # ZPS_LENR
      'SET_XREG15'         : ( 0x1237, 0x0003, 0x1b40 ),   # QMTOL
      'SET_XREG16'         : ( 0x1237, 0x0005, 0x1bc8 ),   # QMLEN
      'SET_XREG17'         : ( 0x1240, 0x000B, 0x1b70 ),   # QMLVL
      'SET_XREG21'         : ( 0x123c, 0x0090, 0x1b70 ),   # QMLVL2
      'SET_XREG23'         : ( 0x123d, 0x0014, 0x1b50 ),   # MAX_CNT
      'SET_XREG22'         : ( 0x123a, 0x0001, 0x1bd8 ),   # DEFSEP
      'SET_XREG24'         : ( 0x12b8, 0x0000, 0x1ba9 ),   # GWINSEL2T
      'SET_XREG25'         : ( 0x12b8, 0x0000, 0x1bfb ),   # GWINCNT2T
      'SET_XREG26'         : ( 0x12b6, 0x0100, 0x1b80 ),   # GWINTHRSH2T
      'SET_XREG27'         : ( 0x0806, 0x0002, 0x1bfd ),   # DFIRSCALE
}

if testSwitch.FE_0276349_228371_CHEOPSAM_SRC:
   prm_AFS_CM_Read_109.update(ZPS_ACQ_SM_values)
   if not testSwitch.CHEOPSAM_LITE_SOC:
       prm_AFS_CM_Read_109.update({
           'SET_XREG09'         : ( 0x010D, 0xFFDF, 0xCF0 ),# Enable TA detector (Bit7, 0: Enable, 1: Disable
             })                                             # not in cheopsamLite 
   else:
       prm_AFS_CM_Read_109.update( Enable_TA_CheopsaM_Lite)   # enable TA 

if testSwitch.WA_0000000_348432_FLAWSCAN_AMPLITUDE_DROP:
   prm_AFS_CM_Read_109.update(AGC_TGS_Correction)

if testSwitch.Enable_ATAFS or testSwitch.FE_0168920_322482_ADAPTIVE_THRESHOLD_FLAWSCAN_LSI:   #0x0001 to enable adaptive flaw scan
   prm_AFS_CM_Read_109.update({'RW_MODE'   : 0x4001,})

if testSwitch.FE_0168920_322482_ADAPTIVE_THRESHOLD_FLAWSCAN_LSI:
   #=== Tune Slim and UMP tracks.
   PRM_TUNE_SLIM_UMP_AFS_THRESHOLD_109 = prm_AFS_CM_Read_109.copy()
   PRM_TUNE_SLIM_UMP_AFS_THRESHOLD_109.pop('SFLAW_OTF')      # Disable Servo Scan OTF

   if testSwitch.MARVELL_SRC:
      if testSwitch.HAMR:
         MinThreshold = 40
         MaxThreshold = 43
      else:
         MinThreshold = 45
         MaxThreshold = 51

      PRM_TUNE_SLIM_UMP_AFS_THRESHOLD_109.update({
         "SET_XREG08" : ( 0x00AB, 0x1FBF, 0xCC0 ),   # Enable Drop-out1 detector.
      })

      if not testSwitch.CHEOPSAM_LITE_SOC:
          PRM_TUNE_SLIM_UMP_AFS_THRESHOLD_109.update({
             "SET_XREG09" : ( 0x010D, 0xFFFF, 0xCF0 ),   # Disable TA (Bit7).
             })
      else:
          PRM_TUNE_SLIM_UMP_AFS_THRESHOLD_109.update( Disable_TA_CheopsaM_Lite)   # Disable TA 
   else:
      MinThreshold = 9
      MaxThreshold = 13
      PRM_TUNE_SLIM_UMP_AFS_THRESHOLD_109.update({
         "FSB_SEL" : (0x0080, 0x0000),               # Enable QM detector only
      })

   PRM_TUNE_SLIM_UMP_AFS_THRESHOLD_109.update({
      'prm_name'                : 'PRM_TUNE_SLIM_UMP_AFS_THRESHOLD_109',
      "RW_MODE"                 : 0x4001,
      "CWORD1"                  : 0x00F0,
      "CWORD2"                  : 0x2880,
      "CWORD3"                  : 0x002D,
      "CWORD4"                  : 0x2020,
      "MIN_NRRO_LIMIT"          : MinThreshold,               # Minimum threshold limit
      "MAX_NRRO_LIMIT"          : MaxThreshold,               # Maximum threshold limit
      "NUM_TRACKS_PER_ZONE"     : { 'ATTRIBUTE': 'numZones',
                                    'DEFAULT'  : 60,
                                    60         : 200,
                                    120        : 50,
                                    150        : 50,
                                    180        : 50,
                                  },
      "POS_THRES_OPTI_CRITERIA" : { 'ATTRIBUTE': 'numZones',
                                    'DEFAULT'  : 60,
                                    60         : (1, 5, 5),     # (PosBadTrack, PosQualCnt, PosDeltaThres)
                                    120        : (1, 3, 5),
                                    150        : (1, 3, 5),
                                    180        : (1, 3, 5),
                                  },
      "NEG_THRES_OPTI_CRITERIA" : { 'ATTRIBUTE': 'numZones',
                                    'DEFAULT'  : 60,
                                    60         : (150, 120, 5), # (NegBadTrack, NegQualCnt, NegDeltaThres)
                                    120        : ( 45,  40, 5),
                                    150        : ( 45,  40, 5),
                                    180        : ( 45,  40, 5),
                                  },
   })
   #=== Tune Fat tracks.
   PRM_TUNE_FAT_AFS_THRESHOLD_109 = PRM_TUNE_SLIM_UMP_AFS_THRESHOLD_109.copy()
   PRM_TUNE_FAT_AFS_THRESHOLD_109['prm_name'] = 'PRM_TUNE_FAT_AFS_THRESHOLD_109',
   PRM_TUNE_FAT_AFS_THRESHOLD_109["CWORD3"] |= 0x0080        # TUNE_FAT_TRACK_AFS_THRES


if testSwitch.FE_0238194_348432_T109_REWRITE_BEFORE_VERIFY_READ and not testSwitch.SMR:
   T109_CWORD1_REWRITES = 0x0004 # Rewrite before each verify read
   T109_CWORD2_REWRT_ONCE = 0x0008 # Rewrite once before first verify read
   #prm_AFS_CM_Read_109['CWORD1'] |= T109_CWORD1_REWRITES
   prm_AFS_CM_Read_109['CWORD2'] |= T109_CWORD2_REWRT_ONCE

if testSwitch.WA_0128885_357915_SEPARATE_OD_ODD_EVEN_FLAWSCAN:
   prm_AFS_CM_Read_OD_109 = prm_AFS_CM_Read_109.copy()
   prm_AFS_CM_Read_109.update({
      'START_CYL'    : CUtility.ReturnTestCylWord(endODScanCyl + 1), # Set starting cylinder for normal flawscan
   })
   prm_AFS_CM_Read_OD_109.update({
      'END_CYL'         : CUtility.ReturnTestCylWord(endODScanCyl),  # Set OD scan ending cylinder
      'SET_XREG16'      : (0x00E2, 0x050E, 0x1BC0), # (Sets QM_LVL=0xE)
      'prm_name'        : 'prm_AFS_CM_Read_OD_109',
   })

if testSwitch.UMP_SHL_FLAWSCAN:
   #=== UMP - read parm
   PRM_READ_UMP_ZONES_109 = prm_AFS_CM_Read_109.copy()
   PRM_READ_UMP_ZONES_109.update({
      'prm_name': 'PRM_READ_UMP_ZONES_109',
      'spc_id'  : 1092,
      "CWORD3"  : 0x0200,
   })
   #=== SHL - read parm
   PRM_READ_SHL_ZONES_109 = prm_AFS_CM_Read_109.copy()
   PRM_READ_SHL_ZONES_109.update({
      'prm_name': 'PRM_READ_SHL_ZONES_109',
      'spc_id'  : 1092,
      "CWORD3"  : 0x0100,
   })

if testSwitch.FE_0234376_229876_T109_READ_ZFS:
   RZFS_ZBZ_T109_SETTINGS = {
      'prm_name'              : 'PRM_RZFS_ZBZ_109',
      'timeout'               : 28800 * numHeads, # 8 hrs per head
      "CWORD5"                : 0x100B,
      "RZAP_MABS_RRO_LIMIT"   : 287,
      "START_HARM"            : 12,
      "MAX_ITERATION"         : 5,
      "RZ_RRO_AUDIT_INTERVAL" : 2000,
   }
   PRM_READ_UMP_ZONES_109.update(RZFS_ZBZ_T109_SETTINGS)
   PRM_READ_SHL_ZONES_109.update(RZFS_ZBZ_T109_SETTINGS)

#=== Flaw scan beatup params
if testSwitch.ENABLE_FLAWSCAN_BEATUP:
   BeatupExtendedTracks = 2.0   # unit: %
   BeatupScratchLen = 100
   NumberOfWriteLoops = 10
   prm_AFS_2T_Read_Beatup_109 = prm_AFS_CM_Read_109.copy()
   prm_AFS_2T_Read_Beatup_109['prm_name'] = 'prm_AFS_2T_Read_Beatup_109'
   prm_AFS_2T_Write_Beatup_109 = prm_AFS_2T_Write_109.copy()
   prm_AFS_2T_Write_Beatup_109['prm_name'] = 'prm_AFS_2T_Write_Beatup_109'
   prm_AFS_2T_Write_Beatup_109['CWORD2'] &= 0xBFFF  # Disable PARA_JOG_SCRN (0x4000)
   prm_AFS_2T_Write_Beatup_109['LOOP_CNT'] = NumberOfWriteLoops
   # For SMR drive, test can only be performed on UMP zones.
   if testSwitch.SMR:
      BeatupExtendedTracks = 10 # unit: track
      prm_AFS_2T_Read_Beatup_109['CWORD3'] = 0x0200
      prm_AFS_2T_Write_Beatup_109['CWORD3'] = 0x0200

if testSwitch.shortProcess:
   prm_AFS_CM_Read_109.update({
      'END_CYL'            : (0, 0x4E20), # 20,000
   })

prm_basic_AFS_CM_Read_109 = {
   'test_num'              : 109,
   'prm_name'              : 'prm_basic_AFS_CM_Read_109',
   'timeout'               : 1800,
   'spc_id'                : 1,
   'CWORD1'                : 0x0402,
   'CWORD2'                : 0x0900,
   'RW_MODE'               : 0x4000,
   'DIVISOR'               : 75,
   'EARLY_FLAW'            : (7, 3, 6),
   'DEFECT_LENGTH'         : 0x040A,            # QM_TOL, QM_LEN
   'THRESHOLD'             : 20,                # QM_LVL
   'TA_THRESHOLD'          : 20,                # TA LVL
   }

prm_AFS_1T_OffTrk_Write_109 = {
   'test_num'              : 109,
   'prm_name'              : 'prm_AFS_1T_OffTrk_Write_109',
   'timeout'               : 21600 * numHeads,  # 6 hours per head (cut down after we get a handle on actual test time)
   'spc_id'                : 1,
   'CWORD1'                : 0x0016,            # 0x10:Report all read errors; 0x4:Enable rewrites during verify; 0x2:Log skip tracks
   'CWORD2'                : 0x0900,            # 0x800:Summary tables; 0x100:Enable early flaw detection
   'CERT_OFFSET'           : -112,              # -44% offtrack  #AAB: should we go 50% instead?  What are the units on this?
   'SET_OCLIM'             : -50,               # 60% OCLIM; CERT_OFFSET offset plus nominal OCLIM
   'RW_MODE'               : 0x10,              # Write using super-sector 1T pattern
   'START_CYL'             : (0x0000, 0x0000),
   'END_CYL'               : (0xFFFF, 0xFFFF),
   'HEAD_RANGE'            : 0xFF,              # Default to all heads. This may be modified to selectively clean heads if not all heads need cleaning
   'HEAD_CLAMP'            : 600,               # Since CWORD1 0x2 is set: this is the skip track limit
   'TRACK_LIMIT'           : 80,                # Since super-sector write, this specifies the number of errors allowed before calling a track an uncertified track
   'ZONE_LIMIT'            : 50000,             # Defect zone limit, over this limit means head is clamped
   'SWD_RETRY'             : 0x0305,            # Log skip track if 3 of 5 SWD repeats.  Note SWD should NOT be on during this test
   }

if testSwitch.FE_0118875_006800_RUN_T109_MSE_SCAN:
   prm_MSE_Scan_109 = {
      'test_num'              : 109,
      'prm_name'              : 'prm_MSE_Scam_109',
      'timeout'               : 35000,
      'spc_id'                : 1,
      'CWORD1'                : 0x0082,            # 0x0400 debug dump failed tracks, 0x0010 report tracks
      'CWORD2'                : 0x0C10,
      'RW_MODE'               : 0x0000,
      'START_CYL'             : (0x0000, 0x0000),
      'END_CYL'               : (0xFFFF, 0xFFFF),
      'HEAD_RANGE'            : 0x00FF,
      #MSE limits
      'CWORD4'                : 0x1000,            # MSE scan enable
      'NUM_SAMPLES'           : 100,               # Number of test points to use during zone calibration
      'R_STDEV_LIMIT'         : [0x0101],          # 1 retry 1 percent trim
      'PERCENT_LIMIT'         : 500,               # Sigma multiplier for limit (limit = slope*(track offset into zone) + intercept) + (std dev * percent_limit\100)
      #Error Thresholds
      'HEAD_CLAMP'            : 1000,
      'FREQUENCY'             : Analog_FS_Freq,
      }


prm_Interval_AFS_2T_Write_109_old = {
  'test_num'           : 109,
  'prm_name'           : 'prm_Interval_AFS_2T_Write_109',
  'timeout'            : 70000,
  'spc_id'             : 1,
  "CWORD1"             : (0x0076,),
  "CWORD2"             : (0x0800,),
  "RW_MODE"            : (0x0100,),
  "START_CYL"          : (0x0000,0x0000,),
  "END_CYL"            : (0xFFFF,0xFFFF,),
  "HEAD_RANGE"         : (0x00FF,),
  #Error Thresholds
  "HEAD_CLAMP"         : (3000,),
  "TRACK_LIMIT"        : (80,),
  "ZONE_LIMIT"         : (50000,),
  #"SFLAW_OTF"          : (),         # Integrated Servo FS in A Data FS
  "DEFECT_LENGTH"      : (0x0003,),  # MADS window size
  "THRESHOLD"          : (0x0017,),  # QM_LVL
  "EARLY_FLAW"         : (7,3,6),
  "ERRS_B4_SFLAW_SCAN" : (1,),
  "SET_OCLIM"          : {
      'ATTRIBUTE'  : 'BG',
      'DEFAULT'    : 'OEM1B',
      'OEM1B'      : 5,
      'SBS'        : 2,
      },  #10 equv 10% OCLim, 5 equv 12% OCLim
  "SEEK_STEP"          : (2,),
}
prm_Interval_AFS_2T_Write_109  = {
   'test_num'           : 109,
   'prm_name'           : 'prm_Interval_AFS_2T_Write_109 ',
   'timeout'            : 70000,
   'spc_id'             : 1,
   "CWORD1"             : 0x0006,                 # REWRITES (0x0004), UNCERT_TO_SKIPTRACK (0x0002)
   "CWORD2"             : 0x0800,                 # XPLUSV_SCAN (0x8000), PARA_JOG_SCRN (0x4000), REPORT_SUMMARY_TABLES (0x0800)
   "HEAD_RANGE"         : 0x00FF,
   "START_CYL"          : (0x0000,0x0000,),
   "END_CYL"            : (0xFFFF,0xFFFF,),
   "RW_MODE"            : 0x0100,
   "HEAD_CLAMP"         : 900,
   "TRACK_LIMIT"        : 80,
   "ZONE_LIMIT"         : 50000,
   "SET_OCLIM"          : {
      'ATTRIBUTE'  : 'BG',
      'DEFAULT'    : 'OEM1B',
      'OEM1B'      : 5,
      'SBS'        : 2,
      },  #10 equv 10% OCLim, 5 equv 12% OCLim
   "SFLAW_OTF"          : (),
   "ERRS_B4_SFLAW_SCAN" : 1,
   "FREQUENCY"          : FLAWSCAN_DEFREQUENCY,
   "SEEK_STEP"          : (2,),
   }
prm_Interval_AFS_CM_Read_109_old = {
  'test_num'           : 109,
  'prm_name'           : 'prm_Interval_AFS_CM_Read_109',
  'timeout'            : 70000,
  'spc_id'             : 1,
  "CWORD1"             : (0x0472,), # 0x0002 to disable TA_OTF
  "CWORD2"             : (0x0800,),
  "RW_MODE"            : (0x4000,),
  "START_CYL"          : (0x0000,0x0000,),
  "END_CYL"            : (0xFFFF,0xFFFF,),
  "HEAD_RANGE"         : (0x00FF,),
  #Error Thresholds
  "HEAD_CLAMP"         : (3000,),
  "TRACK_LIMIT"        : (80,),
  "ZONE_LIMIT"         : (65000,),
  "VERIFY_GAMUT"       : (3, 3, 20),
  "IGNORE_UNVER_LIMIT" : (),
  #"SFLAW_OTF"          : (),         # Integrated Servo FS in A Data FS
  "DEFECT_LENGTH"      : (0x0003,),  # MADS window size
  "THRESHOLD"          : (0x0017,),  # QM_LVL
  "EARLY_FLAW"         : (7,3,6),
  "ERRS_B4_SFLAW_SCAN" : (1,),
  "SET_OCLIM"          : {
      'ATTRIBUTE'  : 'BG',
      'DEFAULT'    : 'OEM1B',
      'OEM1B'      : 5,
      'SBS'        : 2,
      },  #10 equv 10% OCLim, 5 equv 12% OCLim
  "SEEK_STEP"          : (2,),
  "TA_THRESHOLD"       : (0x000C,),       # TA Level
  "DIVISOR"            : (0x000B,),
}
prm_Interval_AFS_CM_Read_109 = {
   'test_num'           : 109,
   'prm_name'           : 'prm_Interval_AFS_CM_Read_109',
   'timeout'            : 70000,
   'spc_id'             : 1,
   "CWORD1"             : 0x0072,
   "CWORD2"             : 0x2880,
   "HEAD_RANGE"         : 0x00FF,
   "START_CYL"          : (0x0000,0x0000),
   "END_CYL"            : (0xFFFF,0xFFFF),
   "RW_MODE"            : 0x4000,
   "HEAD_CLAMP"         : 150,
   "TRACK_LIMIT"        : 80,
   "ZONE_LIMIT"         : 65000,
   "VERIFY_GAMUT"       : (2, 3, 20),
   "DEFECT_LENGTH"      : 3,
   "THRESHOLD"          : 20,                 # drop-out 1
   "THRESHOLD2"         : 0x007F,             # drop-in 1
   "FSB_SEL"            : (1,1),              # mask: NOT USED, sel: FS_BUS_SEL for formatter
   "SET_OCLIM"          : {
      'ATTRIBUTE'  : 'BG',
      'DEFAULT'    : 'OEM1B',
      'OEM1B'      : 5,
      'SBS'        : 2,
      },  #10 equv 10% OCLim, 5 equv 12% OCLim
   "SFLAW_OTF"          : (),
   "IGNORE_UNVER_LIMIT" : (),
   "ERRS_B4_SFLAW_SCAN" : 1,
   "GAIN"               : 0,                  # Flag detcr TA if threshold need extra adjust from T094,+ deduct, - increase thresold
   #"ZONE_POSITION"      : 180,
   "E_FACTOR"           : {
            "ATTRIBUTE"   : "CAPACITY_PN",
            "DEFAULT"     : "500G",
            "1000G"     : 300,
            "750G"      : 400,
            "500G"      : 300,
            "320G"      : 400,
      },
   "FREQUENCY"          : FLAWSCAN_DEFREQUENCY,
   "SEEK_STEP"          : (2,),
   }

prm_AdvSweep_Criteria = {
    'delta_defect_limit' : 888,
}

prm_107_aperio = {                              # Aperio Gray Code defect report
   'test_num'              : 107,
   'prm_name'              : 'prm_107_aperio',
   'timeout'               : 14400,
   'CWORD1'                : 0x0010,
   }

prm_write_plist_149 = {                      # Write flaws in db-log to primary defect list
   'test_num'              : 149,
   'prm_name'              : 'prm_write_plist_149',
   'spc_id'                : 1,
   'CWORD1'                : 0x0010,
   'CWORD2'                : 0x0040,
   }

prm_write_SFT_plist_149 = {                  # Write flaws in db-log to primary defect list
   'test_num'              : 149,
   'prm_name'              : 'prm_write_SFT_plist_149',
   'CWORD1'                : 0x0020,
   'CWORD2'                : 0x0040,
   }

prm_init_plist_149 = {
   'test_num'              : 149,
   'prm_name'              : 'prm_init_plist_149',
   'CWORD1'                : 0x0004,
   }

if testSwitch.Enable_ATAFS == 1:
   prm_ATAFS_395 = {
   'test_num'      : 395,
   'prm_name'      : 'prm_ATAFS_395',
   'spc_id'        : 1,
   'timeout'       : 3600,
   'CWORD1'        : 0x0015,  #Gen2B: 0x0035, Gen2C: 0x0055
   'HEAD_RANGE'    : 0x00FF,
   'ZONE_POSITION' : 180,
   'THRESHOLD'     : 5,       # ADC treshold low limit
   'THRESHOLD2'    : 30,      # ADC treshold up limit
   'OFFSET'        : 0,       # 1150
   'SLOPE_LIMIT'   : 180,     # 90
   'MINIMUM'       : 5,       # flaw scan threshold low limit
   'MAXIMUM'       : 50,      # flaw scan threshold up limit
   'DELTA_LIMIT'   : 0,       # 2
   'SCALED_VAL'    : 1000,    # To scale vgar. Default is 1000.
   'RETRY_LIMIT'   : 4,
   'FREQUENCY'     : {
            "ATTRIBUTE"   : "CAPACITY_PN",
            "DEFAULT"     : "500G",
            "1000G"     : FLAWSCAN_DEFREQUENCY,
            "750G"      : FLAWSCAN_DEFREQUENCY,
            "500G"      : FLAWSCAN_DEFREQUENCY,
            "320G"      : FLAWSCAN_DEFREQUENCY_320G,
            },
   'TARGET_COEF'   : {
            "ATTRIBUTE"   : "CAPACITY_PN",
            "DEFAULT"     : "500G",
            "1000G"     : -80,
            "750G"      : -80,
            "500G"      : -80,
            "320G"      : -200,
            },
   }

MAX_TA_IN_AFH_TEST_ZONES = 13
#_________________________________________________________________________________________________________
# FE_0168920_322482_ADAPTIVE_THRESHOLD_FLAWSCAN_LSI
if testSwitch.MARVELL_SRC:
   if testSwitch.HAMR:
      Default_Threshold = 42
   else:
      Default_Threshold = 48
else:
   Default_Threshold = 11

PRM_INIT_AFS_THRESHOLD_355 = {
   'test_num'   : 355,
   'prm_name'   : 'PRM_INIT_AFS_THRESHOLD_355',
   'spc_id'     : 1,
   'timeout'    : 3600,
   "CWORD1"     : 0x0001,
   "THRESHOLD"  : Default_Threshold,      # UMP track default threshold
   "THRESHOLD2" : Default_Threshold,      # Slim track default threshold
   "THRESHOLD3" : Default_Threshold,      # fat track default threshold
}

PRM_DISPLAY_AFS_THRESHOLD_355 = {
   'test_num'   : 355,
   'prm_name'   : 'PRM_DISPLAY_AFS_THRESHOLD_355',
   'spc_id'     : 1,
   'timeout'    : 3600,
   "CWORD1"     : 0x0004,
}

PRM_SYNCUP_AFS_THRESHOLD_355 = {
   'test_num'   : 355,
   'prm_name'   : 'PRM_SYNCUP_AFS_THRESHOLD_355',
   'spc_id'     : 1,
   'timeout'    : 3600,
   "CWORD1"     : 0x0010,
}

PRM_DISPLAY_AFS_THRESHOLD_355_2 = PRM_DISPLAY_AFS_THRESHOLD_355.copy()
PRM_DISPLAY_AFS_THRESHOLD_355_2['spc_id'] = 2

#_________________________________________________________________________________________________________
prm_094_0002 = {
   'test_num'              : 94,
   'prm_name'              : 'prm_094_0002',
   'spc_id'                : 1,
   'timeout'               : 3600,
   #"CWORD1" : (0x0000,),  Currently no switches are defined for Cword1.
   "DYNAMIC_THRESH"        : {
      "ATTRIBUTE"       : 'PREAMP_TYPE',
      "DEFAULT"         : 'default',
      "default"         : (23,5,0,1,0,),  #Bias, Gain, Filter, Polarity, and vthRange 0 = full 18-204, 1 = reduced 9-102
      "LSI5231"         : (0x2a,4,0x2e,1 + (testSwitch.FE_PREAMP_DUAL_POLARITY_SUPPORT_DETCR_TA<<4) ,0,),
      "LSI5830"         : (0x2a,6,0x2e,1 + (testSwitch.FE_PREAMP_DUAL_POLARITY_SUPPORT_DETCR_TA<<4) ,0,),
      "TI7550"          : (0x2a,4,0x2e,1 + (testSwitch.FE_PREAMP_DUAL_POLARITY_SUPPORT_DETCR_TA<<4) ,0,),
      "TI7551"          : (0x2a,6,0x2e,1 + (testSwitch.FE_PREAMP_DUAL_POLARITY_SUPPORT_DETCR_TA<<4) ,0,),
   },
   "LIMIT"                 : (5,),         # This is the number of errors found which will allow the threshold search to conclude for a hd/zn.
   "CWORD2"                : {
      "ATTRIBUTE"       : 'FE_0214217_006800_T94_VTH_THRESH_BASED_ON_LINE_FIT',
      "DEFAULT"         : 0,
      0                 : (0x0003,),   #use input bias/gain in T94 configure table
      1                 : (0x2003,),   #use input bias/gain in T94 configure table, 0x2000=T94_VTH_THRESH_BASED_ON_LINE_FIT
   },
   "THRESHOLD"             : (0x2),       #user specified vth, set when cword2 0x10
   "VERIFY_GAMUT"          : (1,2,10, ),
   #"HEAD_RANGE"            : (0x0001,),
   "NUM_TRACKS_PER_ZONE"   : (10,),  #don't go over 500, if it is desired to exceed this number I can change some code to accommodate that.
   # DAC_RANGE - sets the Vth range to try, first argument is start, 2nd is end and 31 is the max, 3rd arg is step size.
   # most likely should be 1.  The defaults for this are 0 to 31 counting by 1.
   "DAC_RANGE"             : {
      "ATTRIBUTE"       : 'PREAMP_TYPE',
      "DEFAULT"         : 'default',
      "default"         : (0,31,1,),
      "LSI5231"         : (0,63,1,),
      "LSI5830"         : (0,63,1,),
      "TI7550"          : (0,63,1,),
      "TI7551"          : (0,63,1,),
   },
   "HD_TYPE"              : {
      'ATTRIBUTE'       : 'HGA_SUPPLIER',
      'DEFAULT'         : 'RHO',
      'RHO'             : 0,
      'TDK'             : 1,
      'HWY'             : 2,
   },
}

if testSwitch.FE_0276349_228371_CHEOPSAM_SRC:
   prm_094_0002.update(ZPS_ACQ_SM_values)
   if not testSwitch.CHEOPSAM_LITE_SOC :
      prm_094_0002.update({
         "SET_XREG01"            : (0x00ab, 0x1fff,  0xcc0 ),
         "SET_XREG02"            : (0x010d, 0xffdf,  0xcf0 ),  #not in cheopsam Lite
      })
   else:
      prm_094_0002.update({
         "SET_XREG01"            : (0x00ab, 0x1fff,  0xcc0 ),
      })



if testSwitch.IS_DETCR:
    prm_094_0002.update({
      'timeout'                : 10000 * numHeads,
    #   "OFFSET"                : 3,
    #   "HEAD_RANGE"            : (0x000F,),   # MLW added 11/29/10
    })

if testSwitch.shortProcess:
   prm_094_0002.update({
      "ZONE_MASK"             : (0, 0x0003),
   })



prm_094_0003 = prm_094_0002.copy()
prm_094_0003.update({
   "LIMIT"                 : (1,),           # Average limit.
   "HEAD_RANGE"            : (0x00FF,),  # do all heads, Change not required, value was 0x0001
})

if testSwitch.FE_0159597_357426_DSP_SCREEN == 1:
   DSP_prm_094_NEG = {
      'test_num'              : 94,
      'prm_name'              : 'DSP_prm_094_NEG',
      'spc_id'                : 32100,
      'timeout'               : 3600,
      #"CWORD1" : (0x0000,),  Currently no switches are defined for Cword1.
      "DYNAMIC_THRESH"        : (31,7,1,1,1,),  #Bias, Gain, Filter, Polarity, and vthRange 0 = reduced 9 - 102, 1 = full 18-204
      "LIMIT"                 : (5,),         # This is the number of errors found which will allow the threshold search to conclude for a hd/zn.
      "CWORD2"                : (0x0002,),
      "THRESHOLD"             : (0x2),
      "VERIFY_GAMUT"          : (1,2,10, ),
      "HEAD_RANGE"            : (0x0001,),
      'ZONE_MASK':(0x1,0xFF00),#Run from Zones - 8-16
      'CWORD2'   :(0x82), #Allow manual offset
      'OFFSET'   :(5), #Reducing offset compared to what T109 uses
      "DYNAMIC_THRESH"        : (31,7,1,0x10,1,),  #Bias, Gain, Filter, Polarity, and vthRange 0 = reduced 9 - 102, 1 = full 18-204
      "NUM_TRACKS_PER_ZONE"   : (200,),  #don't go over 500, if it is desired to exceed this number I can change some code to accommodate that.
      # DAC_RANGE - sets the Vth range to try, first argument is start, 2nd is end and 31 is the max, 3rd arg is step size.
      # most likely should be 1.  The defaults for this are 0 to 31 counting by 1.
      "DAC_RANGE"             : (0,31,1,),
   }


prm_186_0001 = {
   'test_num'              : 186,
   'prm_name'              : 'prm_186_0001',
   'spc_id'                : 1,
   'timeout'               : 3600,
   "CWORD1"                : (0x0200,),
   "HEAD_RANGE"            : (0x00FF),
   "GAIN_CONTROL"          : (7),        # user specified dac setting
   "INPUT_VOLTAGE"         : (200),
   "HD_TYPE"               : {
       'ATTRIBUTE'         : 'HGA_SUPPLIER',
       'DEFAULT'           : 'RHO',
       'RHO'               : 0,
       'TDK'               : 1,
       'HWY'               : 2,
       },
}

LiveSensor_prm_094 = {
   'test_num'              : 94,
   'prm_name'              : 'LiveSensor_prm_094',
   'spc_id'                : 1,
   'timeout'               : 3600,
  # 'LIVE_SENSOR_THRESHOLD' : (0xFFFF, 0xFFFF),
   "CWORD3" : (0x8000,),
   "DYNAMIC_THRESH"        : {
      "ATTRIBUTE" : 'PREAMP_TYPE',
      "DEFAULT" : 'default',
      "default" : (0x28, 7, 2, 0, 3,),  #Bias, Gain, Filter, Polarity, and vthRange 0 = full 18-204, 1 = reduced 9-102
      "LSI5231" : (0x28, 7, 2, 0, 3,),
      "LSI5830" : (0x28, 7, 2, 0, 3,),
      "TI7550"  : (0x28, 7, 2, 2, 3,),
      "TI7551"  : (0x28, 7, 2, 2, 3,),
            },
   "LIMIT"                 : (5,),         # This is the number of errors found which will allow the threshold search to conclude for a hd/zn.
   "CWORD2"                : (0x0023,),   #use user input bias/gain (0x20), servo code nor ready, ust have
   "THRESHOLD"             : (0xFF),       #user specified vth, set when cword2 0x10
   "VERIFY_GAMUT"          : (1,2,10, ),
   "HEAD_RANGE"            : (0x0001,),
   "NUM_TRACKS_PER_ZONE"   : (10,),  #don't go over 500, if it is desired to exceed this number I can change some code to accommodate that.
   # DAC_RANGE - sets the Vth range to try, first argument is start, 2nd is end and 31 is the max, 3rd arg is step size.
   # most likely should be 1.  The defaults for this are 0 to 31 counting by 1.
   "DAC_RANGE"   :    (0,63,1,),
}

#This is used by T109 to update Detrc related values insides HAP table
LiveSensor_prm_094_2 = {
   'test_num'              : 94,
   'prm_name'              : 'LiveSensor_prm_094 update settings for TA Detection',
   'spc_id'                : 1,
   'timeout'               : 3600,
   "CWORD3" : (0x0800,),
   "DYNAMIC_THRESH"        : {
      "ATTRIBUTE" : 'HGA_SUPPLIER',
      "DEFAULT" :  'RHO',
      "RHO"     : (46, 6, 0x56, 0x2, 0x1,),  #Bias, Gain, Filter, Polarity, and vthRange 0 = full 18-204, 1 = reduced 9-102
      "TDK"     : (58, 6, 0x56, 0x2, 0x1,),
      "HWY"     : {
         'ATTRIBUTE': 'BG',
         'DEFAULT'  : 'OEM1B',
         'OEM1B'    : (58, 6, 0x56, 0x2, 0x1,),
         'SBS'      : (46, 6, 0x56, 0x2, 0x1,),
         },
      },
}
################################################################################
# Scratch Fill - Start
################################################################################
if testSwitch.FE_0205578_348432_T118_PADDING_BY_VBAR:
   CW1_PADDING_BY_VBAR = 0x0020
else:
   CW1_PADDING_BY_VBAR = 0x0000

if testSwitch.IS_DETCR: # Turn off tripad
   CW2_TRIPAD = 0x0000
else:
   CW2_TRIPAD = 0x0001

#=== Old settings have over-mapped issue. Suspect due to searching window too large.
LongPadPrm_118 = {
   'prm_name'                 : 'prm_118_rev2_long002',
   'test_num'                 : 118,
   'timeout'                  : 7000 * numHeads,
   'CWORD1'                   : 0x8004 | CW1_PADDING_BY_VBAR,
   'CWORD2'                   : 0x8004,
   'PERCENT_LIMIT'            : 0,
   'SPIRAL_TAIL_LEN_PERC'     : 30,
   'RADIAL_FILL_PAD_PERC'     : 100,
   'TANGENTIAL_TAIL_LEN_PERC' : 100,
   'SPIRAL_FILL_PAD'          : 10,
   'RGN_NUM_ELEMENTS'         : 20,
   'NUM_SCRATCH_LIMIT'        : 20000,  #CHOOI-18May17 OffSpec change from 5000 to 20000
   'WIN_NUM_INTERVALS'        : 36,
   'LONG_SPIRAL_SIGMA_THRESH' : 200,
   'RADIAL_TAIL_LEN'          : (4, 8, 16, 0),
   'RGN_CYL_SPACING_THRESH'   : 200,
   'WIN_DENSITY_THRESH'       : 1,
   'LINEAR_DENSITY_THRESH'    : 10,
   'TANGENTIAL_TAIL_LEN_MAX'  : 4,
   'NUM_REGIONS_LIMIT'        : 400,
   'TANGENTIAL_FILL_PAD'      : (2, 5, 15),
   'RADIAL_FILL_PAD_CONST'    : 100,
   'SPIRAL_TAIL_LEN_MAX'      : 150,
   'RGN_DENSITY_THRESH'       : 10,
   'DESPORT_THRESH'           : 500,
   'WIN_CYL_SPACING_THRESH'   : 125,
   'PARAMETER_DIVISOR'        : 100,
   'WIN_NUM_ELEMENTS'         : 20,
   'SPIRAL_TAIL_PAD'          : 15,
   'BANDSIZE'                 : 20,
   'WIN_BYTE_SPACING_THRESH'  : 500,
   'HEAD_RANGE'               : 65535,
   }

ShortPadPrm_118 = {
   'prm_name'                 : 'prm_118_rev2_short002',
   'test_num'                 : 118,
   'timeout'                  : 7000 * numHeads,
   'CWORD1'                   : 0x000c | CW1_PADDING_BY_VBAR,
   'CWORD2'                   : 0x8004,
   'PERCENT_LIMIT'            : 0,
   'SPIRAL_TAIL_LEN_PERC'     : 30,
   'RADIAL_FILL_PAD_PERC'     : 100,
   'TANGENTIAL_TAIL_LEN_PERC' : 100,
   'SPIRAL_FILL_PAD'          : 2,
   'RADIAL_SPAN_2'            : (15, 50, 150, 150),
   'RADIAL_TAIL_LEN'          : (4, 8, 16, 20),
   'RGN_CYL_SPACING_THRESH'   : 130,
   'NUM_SCRATCH_LIMIT'        : 20000,  #CHOOI-18May17 OffSpec change from 5000 to 20000
   'NUM_REGIONS_LIMIT'        : 400,
   'RADIAL_FILL_PAD_CONST'    : 100,
   'LONG_SPIRAL_SIGMA_THRESH' : 200,
   'WIN_NUM_ELEMENTS'         : 20,
   'PARAMETER_DIVISOR'        : 100,
   'SPIRAL_TAIL_PAD'          : 9,
   'TANGENTIAL_TAIL_LEN_MAX'  : 8,
   'BANDSIZE'                 : 2,
   'RADIAL_SPN_TA'            : 3,
   'RGN_NUM_ELEMENTS'         : 100,
   'RADIAL_SPAN_TA_PAD'       : 5296,
   'RADIAL_SPAN_1'            : (1, 2, 4, 8),
   'WIN_DENSITY_THRESH'       : 1,
   'LINEAR_DENSITY_THRESH'    : 10,
   'TANGENTIAL_FILL_PAD'      : (4, 10, 30),
   'RADIAL_TAIL_LEN_2'        : (2, 20, 30, 30),
   'RGN_DENSITY_THRESH'       : 1,
   'DESPORT_THRESH'           : 500,
   'SPIRAL_TAIL_LEN_MAX'      : 40,
   'WIN_CYL_SPACING_THRESH'   : 130,
   'WIN_BYTE_SPACING_THRESH'  : 2000,
   'HEAD_RANGE'               : 65535,
   'RADIAL_SPAN_TA_LEN'       : 300,
}

RadialPadPrm_118 = {
   'prm_name'                 : 'prm_118_rev2_radial002',
   'test_num'                 : 118,
   'timeout'                  : 7000 * numHeads,
   'CWORD1'                   : 0x400c | CW1_PADDING_BY_VBAR,
   'CWORD2'                   : 0x8004 | CW2_TRIPAD,
   'PERCENT_LIMIT'            : 0,
   'SPIRAL_TAIL_LEN_PERC'     : 30,
   'RADIAL_FILL_PAD_PERC'     : 100,
   'TANGENTIAL_TAIL_LEN_PERC' : 100,
   'SPIRAL_FILL_PAD'          : 2,
   'RADIAL_SPAN_2'            : (15, 50, 150, 150),
   'RADIAL_TAIL_LEN'          : (4, 8, 16, 20),
   'RGN_CYL_SPACING_THRESH'   : 130,
   'NUM_SCRATCH_LIMIT'        : 20000,  #CHOOI-18May17 OffSpec change from 5000 to 20000
   'NUM_REGIONS_LIMIT'        : 400,
   'RADIAL_FILL_PAD_CONST'    : 100,
   'LONG_SPIRAL_SIGMA_THRESH' : 200,
   'WIN_NUM_ELEMENTS'         : 20,
   'PARAMETER_DIVISOR'        : 100,
   'SPIRAL_TAIL_PAD'          : 9,
   'TANGENTIAL_TAIL_LEN_MAX'  : 4,
   'BANDSIZE'                 : 2,
   'RADIAL_SPN_TA'            : 3,
   'RGN_NUM_ELEMENTS'         : 100,
   'RADIAL_SPAN_TA_PAD'       : 5296,
   'RADIAL_SPAN_1'            : (1, 2, 4, 8),
   'WIN_DENSITY_THRESH'       : 1,
   'LINEAR_DENSITY_THRESH'    : 10,
   'TANGENTIAL_FILL_PAD'      : (2, 5, 15),
   'RADIAL_TAIL_LEN_2'        : (2, 20, 30, 30),
   'RGN_DENSITY_THRESH'       : 1,
   'DESPORT_THRESH'           : 500,
   'SPIRAL_TAIL_LEN_MAX'      : 40,
   'WIN_CYL_SPACING_THRESH'   : 30,
   'WIN_BYTE_SPACING_THRESH'  : 500,
   'HEAD_RANGE'               : 65535,
   'RADIAL_SPAN_TA_LEN'       : 300,
}

# Parameter used for if FE_0125537_399481_TA_ONLY_T118_CALL = 1
RadialTaPadPrm_118 = {
   'prm_name'                 : 'prm_118_rev2_radial002_TA_Only',
   'test_num'                 : 118,
   'timeout'                  : 7000 * numHeads,
   'CWORD1'                   : 0x4008 | CW1_PADDING_BY_VBAR,
   'CWORD2'                   : 0x8015,
   'PERCENT_LIMIT'            : 0,
   'SPIRAL_TAIL_LEN_PERC'     : 30,
   'RADIAL_FILL_PAD_PERC'     : 100,
   'TANGENTIAL_TAIL_LEN_PERC' : 100,
   'SPIRAL_FILL_PAD'          : 2,
   'RADIAL_SPAN_2'            : (15, 50, 150, 150),
   'RADIAL_TAIL_LEN'          : (4, 8, 16, 20),
   'RGN_CYL_SPACING_THRESH'   : 130,
   'NUM_SCRATCH_LIMIT'        : 20000,  #CHOOI-18May17 OffSpec change from 5000 to 20000
   'NUM_REGIONS_LIMIT'        : 400,
   'RADIAL_FILL_PAD_CONST'    : 100,
   'LONG_SPIRAL_SIGMA_THRESH' : 200,
   'WIN_NUM_ELEMENTS'         : 20,
   'PARAMETER_DIVISOR'        : 100,
   'SPIRAL_TAIL_PAD'          : 9,
   'TANGENTIAL_TAIL_LEN_MAX'  : 4,
   'BANDSIZE'                 : 2,
   'RADIAL_SPN_TA'            : 3,
   'RGN_NUM_ELEMENTS'         : 100,
   'RADIAL_SPAN_TA_PAD'       : 5296,
   'RADIAL_SPAN_1'            : (1, 2, 4, 8),
   'WIN_DENSITY_THRESH'       : 1,
   'LINEAR_DENSITY_THRESH'    : 10,
   'TANGENTIAL_FILL_PAD'      : (2, 5, 15),
   'RADIAL_TAIL_LEN_2'        : (2, 20, 30, 30),
   'RGN_DENSITY_THRESH'       : 1,
   'DESPORT_THRESH'           : 500,
   'SPIRAL_TAIL_LEN_MAX'      : 40,
   'WIN_CYL_SPACING_THRESH'   : 30,
   'WIN_BYTE_SPACING_THRESH'  : 500,
   'HEAD_RANGE'               : 65535,
   'RADIAL_SPAN_TA_LEN'       : 1405,
}

TripadUnvisitedPadPrm_118 = {
   'prm_name'                 : 'prm_118_Tripad_Unvisited',
   'test_num'                 : 118,
   'timeout'                  : 7000 * numHeads,
   'CWORD1'                   : 0x200c | CW1_PADDING_BY_VBAR,
   'CWORD2'                   : 0x8015,
   'PERCENT_LIMIT'            : 0,
   'SPIRAL_TAIL_LEN_PERC'     : 30,
   'RADIAL_FILL_PAD_PERC'     : 100,
   'TANGENTIAL_TAIL_LEN_PERC' : 100,
   'SPIRAL_FILL_PAD'          : 2,
   'RADIAL_SPAN_2'            : (15, 50, 150, 150),
   'RADIAL_TAIL_LEN'          : (4, 8, 16, 20),
   'RGN_CYL_SPACING_THRESH'   : 130,
   'NUM_SCRATCH_LIMIT'        : 20000,  #CHOOI-18May17 OffSpec change from 5000 to 20000
   'NUM_REGIONS_LIMIT'        : 400,
   'RADIAL_FILL_PAD_CONST'    : 100,
   'LONG_SPIRAL_SIGMA_THRESH' : 200,
   'WIN_NUM_ELEMENTS'         : 20,
   'PARAMETER_DIVISOR'        : 100,
   'SPIRAL_TAIL_PAD'          : 9,
   'TANGENTIAL_TAIL_LEN_MAX'  : 4,
   'BANDSIZE'                 : 2,
   'RADIAL_SPN_TA'            : 3,
   'RGN_NUM_ELEMENTS'         : 100,
   'RADIAL_SPAN_TA_PAD'       : 5296,
   'RADIAL_SPAN_1'            : (1, 2, 4, 8),
   'WIN_DENSITY_THRESH'       : 1,
   'LINEAR_DENSITY_THRESH'    : 10,
   'TANGENTIAL_FILL_PAD'      : (2, 5, 15),
   'RADIAL_TAIL_LEN_2'        : (2, 20, 30, 30),
   'RGN_DENSITY_THRESH'       : 1,
   'DESPORT_THRESH'           : 500,
   'SPIRAL_TAIL_LEN_MAX'      : 40,
   'WIN_CYL_SPACING_THRESH'   : 30,
   'WIN_BYTE_SPACING_THRESH'  : 500,
   'HEAD_RANGE'               : 65535,
   'RADIAL_SPAN_TA_LEN'       : 1405,
}

UnvisitedPadPrm_118 = {
   'prm_name'                 : 'prm_118_rev2_unvisited002',
   'test_num'                 : 118,
   'timeout'                  : 7000 * numHeads,
   'CWORD1'                   : 0x200c | CW1_PADDING_BY_VBAR,
   'CWORD2'                   : 0x8006,
   'PERCENT_LIMIT'            : 0,
   'SPIRAL_TAIL_LEN_PERC'     : 30,
   'RADIAL_FILL_PAD_PERC'     : 100,
   'TANGENTIAL_TAIL_LEN_PERC' : 100,
   'SPIRAL_FILL_PAD'          : 2,
   'RGN_NUM_ELEMENTS'         : 100,
   'NUM_SCRATCH_LIMIT'        : 20000,  #CHOOI-18May17 OffSpec change from 5000 to 20000
   'RADIAL_TAIL_LEN_2'        : (2, 20, 30, 30),
   'WIN_BYTE_SPACING_THRESH'  : 500,
   'RADIAL_TAIL_LEN'          : (4, 8, 16, 20),
   'RGN_CYL_SPACING_THRESH'   : 130,
   'WIN_DENSITY_THRESH'       : 1,
   'RGN_DENSITY_THRESH'       : 1,
   'RADIAL_SPAN_2'            : (15, 50, 150, 150),
   'LINEAR_DENSITY_THRESH'    : 10,
   'NUM_REGIONS_LIMIT'        : 400,
   'TANGENTIAL_FILL_PAD'      : (4, 10, 30),
   'HEAD_RANGE'               : 65535,
   'WIN_CYL_SPACING_THRESH'   : 30,
   'RADIAL_FILL_PAD_CONST'    : 450,
   'SPIRAL_TAIL_LEN_MAX'      : 40,
   'LONG_SPIRAL_SIGMA_THRESH' : 200,
   'DESPORT_THRESH'           : 500,
   'WIN_NUM_ELEMENTS'         : 20,
   'PARAMETER_DIVISOR'        : 100,
   'SPIRAL_TAIL_PAD'          : 9,
   'TANGENTIAL_TAIL_LEN_MAX'  : 8,
   'BANDSIZE'                 : 2,
   'RADIAL_SPAN_1'            : (1, 2, 4, 8),
}

#=== OPtimized padding parameters
optiLongPadPrm_118 = {
   'prm_name'                 : 'prm_118_rev2_long002_opti',
   'test_num'                 : 118,
   'timeout'                  : 7000 * numHeads,
   "BANDSIZE"                 : 20,
   "CWORD1"                   : 0x8004 | CW1_PADDING_BY_VBAR,
   "CWORD2"                   : 0x8004,
   "CWORD3"                   : 0x0000, # 0x0001 - Display scratch details
   "DESPORT_THRESH"           : 500,
   "LINEAR_DENSITY_THRESH"    : 10,
   "LONG_SPIRAL_SIGMA_THRESH" : 200,
   "NUM_GROUPS_LIMIT"         : 400,
   "NUM_REGIONS_LIMIT"        : 400,
   'NUM_SCRATCH_LIMIT'        : 20000,  #CHOOI-18May17 OffSpec change from 2000 to 20000
   "PARAMETER_DIVISOR"        : 100,
   "PERCENT_LIMIT"            : 100,
   "RADIAL_FILL_PAD_CONST"    : 100,
   "RADIAL_FILL_PAD_PERC"     : 30,
   "RADIAL_TAIL_LEN"          : (1,2,2,3),
   "RGN_CYL_SPACING_THRESH"   : 100,
   "RGN_DENSITY_THRESH"       : 10,
   "RGN_NUM_ELEMENTS"         : 20,
   "SPIRAL_FILL_PAD"          : 4,
   "SPIRAL_TAIL_LEN_MAX"      : 150,
   "SPIRAL_TAIL_LEN_PERC"     : 40,
   "SPIRAL_TAIL_PAD"          : 10,
   "TANGENTIAL_FILL_PAD"      : (2,2,3),
   "TANGENTIAL_TAIL_LEN_MAX"  : 40,
   "TANGENTIAL_TAIL_LEN_PERC" : 80,
   "WIN_BYTE_SPACING_THRESH"  : 1000,
   "WIN_CYL_SPACING_THRESH"   : 20,
   "WIN_DENSITY_THRESH"       : 1,
   "WIN_NUM_ELEMENTS"         : 20,
   "WIN_NUM_INTERVALS"        : 36,
}

optiRadialPadPrm_118 = {
   'prm_name'                 : 'prm_118_rev2_radial002_opti',
   'test_num'                 : 118,
   'timeout'                  : 7000 * numHeads,
   "BANDSIZE"                 : 2,
   "CWORD1"                   : 0x400C | CW1_PADDING_BY_VBAR,
   "CWORD2"                   : 0x8004 | CW2_TRIPAD,
   "CWORD3"                   : 0x0000, # Display scratch details
   "DESPORT_THRESH"           : 500,
   "LINEAR_DENSITY_THRESH"    : 10,
   "LONG_SPIRAL_SIGMA_THRESH" : 200,
   "NUM_GROUPS_LIMIT"         : 400,
   "NUM_REGIONS_LIMIT"        : 400,
   'NUM_SCRATCH_LIMIT'        : 20000,  #CHOOI-18May17 OffSpec change from 2000 to 20000
   "PARAMETER_DIVISOR"        : 100,
   "PERCENT_LIMIT"            : 50,
   "RADIAL_FILL_PAD_CONST"    : 1020,
   "RADIAL_FILL_PAD_PERC"     : 20,
   "RADIAL_SPAN_1"            : (1,2,4,8),
   "RADIAL_SPAN_2"            : (15,50,150,300),
   "RADIAL_SPAN_TA_LEN"       : 30, #350 tracks!
   "RADIAL_SPAN_TA_PAD"       : 1024,
   "RADIAL_SPN_TA"            : 50,
   "RADIAL_TAIL_LEN"          : (4,8,16,20),
   "RADIAL_TAIL_LEN_2"        : (1,60,150,150),
   "RGN_CYL_SPACING_THRESH"   : 50,
   "RGN_DENSITY_THRESH"       : 1,
   "RGN_NUM_ELEMENTS"         : 100,
   "SPIRAL_FILL_PAD"          : 2,
   "SPIRAL_TAIL_LEN_MAX"      : 40,
   "SPIRAL_TAIL_LEN_PERC"     : 20,
   "SPIRAL_TAIL_PAD"          : 6,
   "TANGENTIAL_FILL_PAD"      : (1,1,2),
   "TANGENTIAL_TAIL_LEN_MAX"  : 4,
   "TANGENTIAL_TAIL_LEN_PERC" : 50,
   "WIN_BYTE_SPACING_THRESH"  : 1000,
   "WIN_CYL_SPACING_THRESH"   : 50,
   "WIN_DENSITY_THRESH"       : 1,
   "WIN_NUM_ELEMENTS"         : 20,
}

optiShortPadPrm_118 = {
   'prm_name'                 : 'prm_118_rev2_short002_opti',
   'test_num'                 : 118,
   'timeout'                  : 7000 * numHeads,
   "BANDSIZE"                 : 2,
   "CWORD1"                   : 0x000C | CW1_PADDING_BY_VBAR,
   "CWORD2"                   : 0x8004,
   "CWORD3"                   : 0x0000, # Display scratch details
   "DESPORT_THRESH"           : 500,
   "LINEAR_DENSITY_THRESH"    : 10,
   "LONG_SPIRAL_SIGMA_THRESH" : 200,
   "NUM_GROUPS_LIMIT"         : 400,
   "NUM_REGIONS_LIMIT"        : 400,
   'NUM_SCRATCH_LIMIT'        : 20000,  #CHOOI-18May17 OffSpec change from 2000 to 20000
   "PARAMETER_DIVISOR"        : 100,
   "PERCENT_LIMIT"            : 150,
   "RADIAL_FILL_PAD_CONST"    : 3900,
   "RADIAL_FILL_PAD_PERC"     : 20,
   "RADIAL_SPAN_1"            : (1,2,3,4),
   "RADIAL_SPAN_2"            : (8,20,50,50),
   "RADIAL_SPAN_TA_LEN"       : 100,
   "RADIAL_SPAN_TA_PAD"       : 1024,
   "RADIAL_SPN_TA"            : 10,
   "RADIAL_TAIL_LEN"          : (4,8,17,0),
   "RADIAL_TAIL_LEN_2"        : (3,24,32,32),
   "RGN_CYL_SPACING_THRESH"   : 50,
   "RGN_DENSITY_THRESH"       : 1,
   "RGN_NUM_ELEMENTS"         : 100,
   "SPIRAL_FILL_PAD"          : 2,
   "SPIRAL_TAIL_LEN_MAX"      : 40,
   "SPIRAL_TAIL_LEN_PERC"     : 20,
   "SPIRAL_TAIL_PAD"          : 6,
   "TANGENTIAL_FILL_PAD"      : (5,5,30),
   "TANGENTIAL_TAIL_LEN_MAX"  : 8,
   "TANGENTIAL_TAIL_LEN_PERC" : 330,
   "WIN_BYTE_SPACING_THRESH"  : 2000,
   "WIN_CYL_SPACING_THRESH"   : 30,
   "WIN_DENSITY_THRESH"       : 1,
   "WIN_NUM_ELEMENTS"         : 20,
}

optiUnvisitedPadPrm_118 = {
   'prm_name'                 : 'prm_118_rev2_unvisited002_opti',
   'test_num'                 : 118,
   'timeout'                  : 7000 * numHeads,
   "BANDSIZE"                 : 2,
   "CWORD1"                   : 0x200C | CW1_PADDING_BY_VBAR,
   "CWORD2"                   : 0x8006,
   "CWORD3"                   : 0x0000, # Disable displaying scratch details
   "DESPORT_THRESH"           : 500,
   "LINEAR_DENSITY_THRESH"    : 10,
   "LONG_SPIRAL_SIGMA_THRESH" : 200,
   "NUM_GROUPS_LIMIT"         : 400,
   "NUM_REGIONS_LIMIT"        : 400,
   'NUM_SCRATCH_LIMIT'        : 20000,  #CHOOI-18May17 OffSpec change from 2000 to 20000
   "PARAMETER_DIVISOR"        : 100,
   "PERCENT_LIMIT"            : 100,
   "RADIAL_FILL_PAD_CONST"    : { 'ATTRIBUTE' : 'ENABLE_T118_EXTEND_ISOLATED_DEFECT_PADDING',
                                    'DEFAULT' : 0,
                                            0 : 100,
                                            1 : 4400,
                                },    
   "RADIAL_FILL_PAD_PERC"     : 30,
   "RADIAL_SPAN_1"            : (1,2,4,8),
   "RADIAL_SPAN_2"            : (15,50,150,300),
   "RADIAL_TAIL_LEN"          : { 'ATTRIBUTE' : 'ENABLE_T118_EXTEND_ISOLATED_DEFECT_PADDING',
                                    'DEFAULT' : 0,
                                            0 : (1,2,2,3),
                                            1 : (3,3,3,3),
                                },
   "RADIAL_TAIL_LEN_2"        : { 'ATTRIBUTE' : 'ENABLE_T118_EXTEND_ISOLATED_DEFECT_PADDING',
                                    'DEFAULT' : 0,
                                            0 : (1,60,150,150),
                                            1 : (3,60,150,150),
                                },
   "RGN_CYL_SPACING_THRESH"   : 50,
   "RGN_DENSITY_THRESH"       : 1,
   "RGN_NUM_ELEMENTS"         : 100,
   "SPIRAL_FILL_PAD"          : 2,
   "SPIRAL_TAIL_LEN_MAX"      : 40,
   "SPIRAL_TAIL_LEN_PERC"     : 20,
   "SPIRAL_TAIL_PAD"          : 6,
   "TANGENTIAL_FILL_PAD"      : (1,1,2),
   "TANGENTIAL_TAIL_LEN_MAX"  : 4,
   "TANGENTIAL_TAIL_LEN_PERC" : 50,
   "WIN_BYTE_SPACING_THRESH"  : 1000,
   "WIN_CYL_SPACING_THRESH"   : 50,
   "WIN_DENSITY_THRESH"       : 1,
   "WIN_NUM_ELEMENTS"         : 20,
}

# Parameter used for if FE_0125537_399481_TA_ONLY_T118_CALL = 1
optiRadialTaPadPrm_118 = optiRadialPadPrm_118.copy()
optiRadialTaPadPrm_118['prm_name'] = 'prm_118_rev2_radial002_TA_Only_opti'
optiRadialTaPadPrm_118["CWORD1"] = 0x4008 | CW1_PADDING_BY_VBAR
optiRadialTaPadPrm_118["CWORD2"] = 0x8015

optiTripadUnvisitedPadPrm_118 = optiUnvisitedPadPrm_118.copy()
optiRadialTaPadPrm_118['prm_name'] = 'prm_118_Tripad_Unvisited_opti'
optiTripadUnvisitedPadPrm_118["CWORD1"] = 0x200C | CW1_PADDING_BY_VBAR
optiTripadUnvisitedPadPrm_118["CWORD2"] = 0x8015

prm_118_sort_fill_def_list = {
   'prm_name'                 : 'prm_118_sort_fill_def_list',
   'test_num'                 : 118,
   'timeout'                  : 7000 * numHeads,
   'CWORD1'                   : 0x1000,
}

if testSwitch.T118_OPTIMIZED_PADDING_PARAMETERS:
   prm_118_rev2_long002 = optiLongPadPrm_118.copy()
   prm_118_rev2_radial002 = optiRadialPadPrm_118.copy()
   prm_118_rev2_short002 = optiShortPadPrm_118.copy()
   prm_118_rev2_unvisited002 = optiUnvisitedPadPrm_118.copy()
   prm_118_rev2_radial002_TA_Only = optiRadialTaPadPrm_118.copy()
   prm_118_Tripad_Unvisited = optiTripadUnvisitedPadPrm_118.copy()
else:
   prm_118_rev2_long002 = LongPadPrm_118.copy()
   prm_118_rev2_radial002 = RadialPadPrm_118.copy()
   prm_118_rev2_short002 = ShortPadPrm_118.copy()
   prm_118_rev2_unvisited002 = UnvisitedPadPrm_118.copy()
   prm_118_rev2_radial002_TA_Only = RadialTaPadPrm_118.copy()
   prm_118_Tripad_Unvisited = TripadUnvisitedPadPrm_118.copy()

prm_130_report_plist = {
   'test_num' : 130,
   'prm_name' : 'prm_130_report_plist',
   'timeout'  : 900 * numHeads,
   'spc_id'   : 2,
   "CWORD1"   : 0x0080,
}

################################################################################
# Scratch Fill - End
################################################################################

if testSwitch.MARVELL_SRC:
    prm_134_TA_Scan = {
       'test_num'                 : 134, # Scan Defects for TA's
       'prm_name'                 : 'prm_134_TA_Scan',
       'timeout'                  : 5000 * numHeads,
       'spc_id'                   : 310,
       'CWORD1'                   : 0x1000,
       'CWORD2'                   : 0x1500,
       'CWORD3'                   : 0x1020,            # scan defect for TA
       'CWORD4'                   : 0x1500,            # turn on debug msg and turn off positive threshold tune                                                   #
       'TA_THRESHOLD'             : 0xFFFF,            # Threshold 14.0 = 5 + 1.8 * 5 (0x0005)
       'AMP_CHARACTOR_STEP'       : 0x0003,            # Step 10.4 = 5 + 1.8 * 3 (0x0003)
       'TA_VERIFY_RETRY'          : (1, 3),
       'TRK_WINDOW_SIZE'          : 75,                # should follow T134,Number of tracks that may be between possibly joinable TA's
       'SYMBOL_PSN_WINDOW_SIZE'   : 180,               # should follow T134, Number of symbols +/- the present TA's starting position that a possibly adjacent TA may occur in.
       'DIVISOR'                  : 75,
       'FREQUENCY'                : TA_FS_Freq,
       'FLY_HEIGHT'               : 0,
       'HD_TYPE'                  : {
           'ATTRIBUTE'            : 'HGA_SUPPLIER',
           'DEFAULT'              : 'RHO',
           'RHO'                  : 0,
           'TDK'                  : 1,
           'HWY'                  : 2,
           },
       }
else:
    prm_134_TA_Scan = {
       'test_num'                 : 134, # Scan Defects for TA's
       'prm_name'                 : 'prm_134_TA_Scan',
       'timeout'                  : 5000 * numHeads,
       'spc_id'                   : 310,
       'CWORD1'                   : 0x1000,
       'CWORD2'                   : 0x1500,
       'CWORD3'                   : 0x1020,            # scan defect for TA
       'CWORD4'                   : 0x1500,            # turn on debug msg and turn off positive threshold tune                                                   #
       'TA_THRESHOLD'             : 0xFFFF,            # Threshold 14.0 = 5 + 1.8 * 5 (0x0005)
       'AMP_CHARACTOR_STEP'       : 0x0003,            # Step 10.4 = 5 + 1.8 * 3 (0x0003)
       'TA_VERIFY_RETRY'          : (1, 3),
       'TRK_WINDOW_SIZE'          : 50,                # Number of tracks that may be between possibly joinable TA's
       'SYMBOL_PSN_WINDOW_SIZE'   : 150,               # Number of symbols +/- the present TA's starting position that a possibly adjacent TA may occur in.
       'DIVISOR'                  : 75,
       'FREQUENCY'                : TA_FS_Freq,
       'FLY_HEIGHT'               : 0,
       'SET_XREG00'               : (0x0A12, 0x0000, 0x1BCC),    #TAEPOFF
       'SET_XREG01'               : (0x0A12, 0x0003, 0x1B74),    #TA_HOLD
       'SET_XREG02'               : (0x0A12, 0x0003, 0x1B30),    #TA_DLY
       'SET_XREG04'               : (0x129c, 0x0000, 0x1B30),    #ZGSENR
       'SET_XREG05'               : (0x1211, 0x0000, 0x1B76),    #GUGFLAW
       }

if testSwitch.FE_0276349_228371_CHEOPSAM_SRC:
   prm_134_TA_Scan.update(ZPS_ACQ_SM_values)

if testSwitch.CHEOPSAM_LITE_SOC:
   prm_134_TA_Scan.update(Enable_TA_CheopsaM_Lite)

if testSwitch.T134_TA_FAILURE_SPEC:
   TA_PER_DRV_1D = 100                  # per drive 1D
   TA_PER_DRV_2D = 150                  # per drive 2D
   TA_PER_SUF_1D = 0                    # per surface 1D , 0 is to turn off
   TA_PER_SUF_2D = 0                    # per surface 2D , 0 is to turn off
   MARVELL_THRESH_LIMIT = 0x2D7         # bit3-0 number of passive TA; bit 15-4 combine format for TA track width


T134_TA_Screen_Spec = {
   'ATTRIBUTE'    : 'BG',
   'DEFAULT'      : 'OEM',
   'SBS'          : {}, # fail-safe
   'OEM'          : {
      ('P134_TA_DETCR_DETAIL', 'match')      : {
         'ATTRIBUTE' : 'CAPACITY_PN',
         'DEFAULT'   : '1000G',
         '1000G'     : {
            # 'spc_id'       : 310, # default is all table available
            # 'row_sort'     : 'HD_LGC_PSN', # default is HD_LGC_PSN if omitted
            # 'col_sort'     : 'DATA_ZONE', # default is DATA_ZONE if omitted
            # 'col_range'    : (4,5,6,7), # default is any, no filtering
            'column'       : ('TA_SEVERITY', 'TA_WIDTH_TRKS', 'TRK_NUM'),
            'compare'      : (         '>=',             '>',       '<'),
            'criteria'     : (            6,             100,     35000),
            # 'fail_count'   : 1, # this is must have for count type
         },
         '500G'      : {
            'column'       : ('TA_SEVERITY', 'TA_WIDTH_TRKS', 'TRK_NUM'),
            'compare'      : (         '==',             '>',       '<'),
            'criteria'     : (            7,             100,     13000),
            # 'fail_count'   : 1, # this is must have for count type
         },
      },
      ('Title','')            : 'T134_TA_Screen_Spec',
   },
}



T134_TA_Screen_Spec_TRK300 = {
   'ATTRIBUTE'    : 'BG',
   'DEFAULT'      : 'OEM',
   'SBS'          : {}, # fail-safe
   'OEM'          : {
      ('P134_TA_DETCR_DETAIL', 'match')      : {
         'ATTRIBUTE' : 'CAPACITY_PN',
         'DEFAULT'   : '1000G',
         '1000G'     : {
            # 'spc_id'       : 310, # default is all table available
            # 'row_sort'     : 'HD_LGC_PSN', # default is HD_LGC_PSN if omitted
            # 'col_sort'     : 'DATA_ZONE', # default is DATA_ZONE if omitted
            # 'col_range'    : (4,5,6,7), # default is any, no filtering
            'column'       : ('TA_SEVERITY', 'TA_WIDTH_TRKS'),
            'compare'      : (         '==',             '>'),
            'criteria'     : (            7,             300),
            # 'fail_count'   : 1, # this is must have for count type
         },
      },
      ('Title','')            : 'T134_TA_Screen_Spec_TRK300',
   },
}

prm_134_TA_Burnish = {
   'test_num'                 : 134,
   'prm_name'                 : 'prm_134_TA_Burnish',
   'spc_id'                   : 320,
   'timeout'                  : 500 * numHeads,
   'CWORD1'                   : 0x0008,
   'CWORD2'                   : 0x0808,
   'CWORD3'                   : 0x3100,
   'MAX_RANGE'                : 0x0001,
   'BURNISH'                  : (0, 5),
   'MAX_ASPS'                 : (255, 255),
   'LIMIT2'                   : 0xFFFF,
   'MVL_THRESH_LEVEL'         : (3, 4, 4096, 4096),
   'SQRT_AMP_WIDTH_LIMIT'     : 0x0fff,
   'SYMBOL_PSN_WINDOW_SIZE'   : 456,
   'ASP_LENGTH1'              : 0xFFFF,
   'ASP_WIDTH1'               : 0x00FF,
   'SET_XREG00'               : (0x00E5, 0x0001, 0x0777),
   'FREQUENCY'                : TA_FS_Freq,
   }


prm_134_TA_Rescan = {
   'test_num'                 : 134,
   'prm_name'                 : 'prm_134_TA_Rescan',
   'timeout'                  : 5000 * numHeads,
   'spc_id'                   : 330,
   'CWORD1'                   : 0x1000,
   'CWORD2'                   : 0xD500,
   'CWORD3'                   : 0x3020,
   'TA_VERIFY_RETRY'          : (1, 5),
   'TA_THRESHOLD'             : 0xFFFF,         # does not apply to DETCR; applies to channel analog-like detectors
   'SYMBOL_PSN_WINDOW_SIZE'   : 456,            # Number of symbols +/- the present TA's starting position that a possibly adjacent TA may occur in.
   'AMP_CHARACTOR_STEP'       : 3,
   'FLY_HEIGHT'               : 0,
   'LIMIT2'                   : 0xFFFF,
   'TRK_WINDOW_SIZE'          : 50,             # Number of tracks that may be between possibly joinable TA's
   'DIVISOR'                  : 75,
   'FREQUENCY'                : TA_FS_Freq,
   'SET_XREG00'               : (0x0A12, 0x0000, 0x1BCC),    #TAEPOFF
   'SET_XREG01'               : (0x0A12, 0x0003, 0x1B74),    #TA_HOLD
   'SET_XREG02'               : (0x0A12, 0x0003, 0x1B30),    #TA_DLY
   'SET_XREG04'               : (0x129c, 0x0000, 0x1B30),    #ZGSENR
   'SET_XREG05'               : (0x1211, 0x0000, 0x1B76),    #GUGFLAW
   'SET_XREG06'               : (0x00E5, 0x0000, 0x1B77),
   }

prm_134_TA_Scan_S34 = {
   'test_num'                 : 134,            # Scan Defects for TA's
   'prm_name'                 : 'prm_134_TA_Scan_S34',
   'spc_id'                   : 340,
   'timeout'                  : 500 * numHeads,
   'CWORD1'                   : 0x8100,
   'CWORD2'                   : 0x1084,
   'CWORD3'                   : 0x3080,
   'MVL_THRESH_LEVEL'         : (3, 4, 500, 100),
   'ASP_LENGTH1'              : 5000,
   'ASP_WIDTH1'               : 100,
   'SQRT_AMP_WIDTH_LIMIT'     : 4000,
   'LIMIT2'                   : 20000,
   'MAX_ASPS'                 : (4095, 100),
   'TRK_WINDOW_SIZE'          : 50,             # Number of tracks that may be between possibly joinable TA's
   'SYMBOL_PSN_WINDOW_SIZE'   : 456,            # Number of symbols +/- the present TA's starting position that a possibly adjacent TA may occur in.
   }


prm_134_TA_Scan_S56 = {
   'test_num'                 : 134,            # Scan Defects for TA's
   'prm_name'                 : 'prm_134_TA_Scan_S56',
   'spc_id'                   : 350,
   'timeout'                  : 500 * numHeads,
   'CWORD1'                   : 0x8100,
   'CWORD2'                   : 0x1084,
   'CWORD3'                   : 0x3080,
   'MVL_THRESH_LEVEL'         : (5, 6, 40, 20),
   'ASP_LENGTH1'              : 5000,
   'ASP_WIDTH1'               : 100,
   'SQRT_AMP_WIDTH_LIMIT'     : 4000,
   'LIMIT2'                   : 20000,
   'MAX_ASPS'                 : (4095, 40),
   'TRK_WINDOW_SIZE'          : 50,             # Number of tracks that may be between possibly joinable TA's
   'SYMBOL_PSN_WINDOW_SIZE'   : 456,            # Number of symbols +/- the present TA's starting position that a possibly adjacent TA may occur in.
}

prm_134_TA_Scan_S67 = {
   'test_num'                 : 134, # Scan Defects for TA's
   'prm_name'                 : 'prm_134_TA_Scan_S67',
   'spc_id'                   : 360,
   'timeout'                  : 500 * numHeads,
   'CWORD1'                   : (0x8100,),
   'CWORD2'                   : (0x1084,),
   'CWORD3'                   : (0x3080,),
   'MVL_THRESH_LEVEL'         : (6, 7, 20, 10),
   'ASP_LENGTH1'              : (5000,),
   'ASP_WIDTH1'               : (100,),
   'SQRT_AMP_WIDTH_LIMIT'     : (4000,),
   'LIMIT2'                   : (20000,),
   'MAX_ASPS'                 : (4095, 20),
   'TRK_WINDOW_SIZE'          : (50,),  # number of tracks that may be between possibly joinable TA's
   'SYMBOL_PSN_WINDOW_SIZE'   : (456,), # number of symbols +/- the present TA's starting position that a possibly adjacent TA may occur in.
}

if testSwitch.IS_DETCR:
   prm_134_TA_Rescan.update({
      'timeout'               : 500 * numHeads,
      'CWORD2'                : 0x9500,
      'CWORD3'                : 0x1020,
      'CWORD4'                : 0x1000,
      'OFFSET'                : 3,
   })

Prm_334_Dwell_Test  = {
   'test_num'                 : 334,
   'prm_name'                 : 'Prm_334_Dwell_Test',
   'timeout'                  : 2592000,              # 2592000=30 days; 1728000=20 days; 864000=10 days
   'spc_id'                   : 100,
   'dlfile'                   : (CN, 'DWELL_STEPS'),   # Text file 'DWELL_STEPS' calls out all the details of each dwell step
   "DWELL_STEPS"              : (14,),                # Number of dwell steps to execute listed in the file 'DWELL_STEPS'
   "DWELL_STEP_SEQUENCE"      : (0,),                 # order to run the dwell steps, 0 = sequential, 1 = random
   #Read Resistance Setup & Spec Limit [recommended values]
   "QTY_RES_MEAS"             : (10,),                # [10] number of times to repeat the reader resistance measurement for averaging
   "LIMIT_RES"                : (40,),                # [25] Read resistance spec, fail if resistance changes +/- more than 2.5% (default = 20 or 2.0%)
   #BER Measurement Setup & Spec Limits [recommended values, takes ~30 minutes for a 6 headed drive for all BER measurements per dwell step]
   "ZONE"                     : (0x0105,),            # zone mask to specify which 2 zones to test BER in, 0x0022 picks zones 1 & 5
   "MAX_ITERATION"            : (4,),                 # [4] number of times to repeat all zones,tracks,write/reads
   "NUM_TRACKS_PER_ZONE"      : (5,),                 # [5] number of tracks measured in each zone
   "TRACK_STEP_SIZE"          : (50,),                # [50] number of tracks to jump for each of the NUM_TRACKS_PER_ZONE
   "NUM_WRITES_READS"         : (2,),                 # [2] number of write/reads for each track (1 write/read = 1 BER measurement)
   "NUM_BITS_READ"            : (8, 2,),              # [8,2] with each BER measurement pass 1e8 bits or stop reading when 1e3 errors are found
   "DESPORT_SIGMA"            : (18,),                # [18 or 20] when calculating avg BER for each zone, sport outliers more than 2.0 sigma from the avg
   "LIMIT_BER_RW"             : (50,),                # [35] read/write BER spec, fail if read/write BER gets worse by more than 0.35 decades
   "LIMIT_BER_RO"             : (70,),                # [55] read only BER spec, fail if read only BER gets worse by more than 0.55 decades
   "LIMIT_BER_RWRO"           : (20,),                # [25] (read/write)-(read only) BER spec, fail if write read BER gets worse then read only BER by >0.25
   #Debug Setup, applicable for debugging only
   "CWORD2"                   : (0x0000,),            # 0x0000 normal dwell operation, all steps and testing is done
                                                      # 0x0001 report dwell tracks only for each step only, no BER or read resistance
                                                      # 0x0002 measure baseline BER only (baseline = BER prior to dwelling)
                                                      # 0x0004 measure baseline read resistance only
                                                      # 0x0008 do entire test except the dwelling, all dwell tracks are reported, all BER/resistance is done
                                                      # 0x0100 dwell only, no BER or read resistance
}
DwellTestCmdList = [Prm_334_Dwell_Test,]


TA_deallocation_prm_215 = {
   'test_num'                 : 215,
   'prm_name'                 : 'TA_deallocation_prm_215',
   'timeout'                  : 1800,
   #Deallocate +/- 4 tracks for all TAs > 17 mV
   'CWORD1'                   :  0x2019,      # Deallocate tracks and not cylinders, enable minimum padding at OD and ID
   'CWORD2'                   :  0x0C00,      # protect reader/writer in read/write opteration, protect writer in read operation
   'TA_AMPLITUDE'             : (4,5,6,7,),
   # 1 (TA track) + 8 (4 trks either side) + ~8 (+/-4 tracks for microjog) = ~17 tracks/TA
   'NUM_ADJ_CYLS'           : {
       'ATTRIBUTE': 'BG',
       'DEFAULT'  : 'OEM1B',
       'OEM1B'    : {
          'ATTRIBUTE'          : 'HGA_SUPPLIER',
          'DEFAULT'            : 'RHO',
          'RHO'                : (25,25,70,70,),
          'TDK'                : (25,25,52,52,),
          'HWY'                : (25,25,52,52,),
          },
       'SBS'      : (0,0,15,15,),
       
      },
   'TRK_WINDOW_SIZE'          : 75,
   'SYMBOL_PSN_WINDOW_SIZE'   : 180,
   'HD_TYPE'                  : {
         'ATTRIBUTE'          : 'HGA_SUPPLIER',
         'DEFAULT'            : 'RHO',
         'RHO'                : 0,
         'TDK'                : 1,
         'HWY'                : 2,
         },
   'PAD_TK_VALUE'             : {
      'ATTRIBUTE': 'BG',
      'DEFAULT'  : 'OEM1B',
      'OEM1B'    : 0, # Checked with Xiaowei, default value is 0
      'SBS'      : {
         'ATTRIBUTE': 'IS_2D_DRV',
         'DEFAULT'  : 0,
         1          : 5,
         0          : 0,
         },
      },   
   }
if testSwitch.FE_0341719_228371_MORE_PAD_LOW_SEVERITY_TA:
   TA_deallocation_prm_215.update({'NUM_ADJ_CYLS':
       {
        'ATTRIBUTE': 'BG',
        'DEFAULT'  : 'OEM1B',
        'OEM1B'    : {
           'ATTRIBUTE'          : 'HGA_SUPPLIER',
           'DEFAULT'            : 'RHO',
           'RHO'                : (70,70,70,70,),
           'TDK'                : (52,52,52,52,),
           'HWY'                : (52,52,52,52,),
           },
        'SBS'      : (0,0,15,15,),
        },
       })

if testSwitch.FE_0342075_228371_TA_PADDING_SBS_2D:
   TA_deallocation_prm_215.update({'PAD_TK_VALUE': 5,})  #cross operation padding extra +-5

   TA_deallocation_prm_215.update({'NUM_ADJ_CYLS':       #padding for detcr to reader  
       {
        'ATTRIBUTE'          : 'HGA_SUPPLIER',
        'DEFAULT'            : 'RHO',
        'RHO'                : (15,15,15,15,),
        'TDK'                : (15,15,15,15,),
        'HWY'                : (15,15,15,15,),
       },})

prm_scratch_fill_117_1 = {
   'test_num'                 : 117,
   'prm_name'                 : 'prm_scratch_fill_117_1',
   'timeout'                  : 9600,
   'spc_id'                   : 1,
   'BYTE_WINDOW'              : 10000,
   'TRK_SPACING'              : 45,
   'MDS_MAX_BYTES_SCR_MULT'   : (0, 60000, 1,),
   'MDS_MAX_TRK_LEN_B4_PRINT' : 0,
   'MDS_VIRTUAL_MAX_BYTES'    : 0,
   'MDS_MAX_SCRATCH_TRK_LEN'  : 1500,
   'MDS_SCRATCH_INCLUDES_CYL' : (0, 0),
   'MEDIA_DAMAGE_SCREEN_TEST' : (),
   'MDS_MAX_TOTAL_BYTES_WCYL' : 50000,
}
if testSwitch.SINGLEPASSFLAWSCAN:
   prm_scratch_fill_117_1.update({'MDS_MAX_BYTES_SCR_MULT'   : (0x5, 0x5730, 1),}) #Change to 350K for SPFS
if testSwitch.FE_0258915_348429_COMMON_TWO_TEMP_CERT:
   prm_scratch_fill_117_1.update({'MDS_MAX_SCRATCH_TRK_LEN'   : 2000,}) #Change to 2k, 1.5k was based on Chengai

if testSwitch.FE_ENABLE_T117_SCREEN_NUM_SCRATCH_PHPZ:
   T117_NUM_SCRATCH_LIMIT_PHPZ = 35 # Based on TVM failed drive FA.
   T117_SCREEN_ZONE_LIST = ['All',]

prm_scratch_fill_117_2 = {
   'test_num'              : 117,
   'prm_name'              : 'prm_scratch_fill_117_2',
   'timeout'               : 9600,
   'spc_id'                : 1,
   'CWORD1'                : 0x0001,
   'HEAD_RANGE'            : 0xFF,
   'MAX_FLAWS_PER_SURFACE' : 0, # Resolve EC10482. Not applicable for PList size is > 65535. Max value for this param is 65535.
   'TAIL_SIZES'            : (5, 10, 20, 30,),
   'FILL_BACKSIZE'         : 21,
   'PROXIMITY_WINDOW'      : 1,
   'PROCEED_TILL_END'      : (),
   'TRK_SPACING'           : 50,
   'BYTE_WINDOW'           : 1000,
   'LARGE_FLAW_LEN'        : 1,
   'MAX_TOTAL_FLAWS'       : 0xFFFF,
   'SECTORS_TO_CHK'        : 3,
   'LONG_DEFECT_PAD'       : (1,10000,),
   'TAIL_LEN'              : (0,10000,),
   'SERVO_TAIL_SIZE'       : 1,
   'PAD_SIZE'              : 3,
   'GAP_FILL'              : 2,
}

if int(DriveAttributes.get('DRAM_PHYS_SIZE',0)) == 8388608:
   prm_scratch_fill_117_1['test_num'] = 'NOP'
   prm_scratch_fill_117_2['test_num'] = 'NOP'

prm_delPlist_140 = {
   'test_num'              : 140,
   'prm_name'              : 'prm_delPlist_140',
   'timeout'               : 1800,
   'spc_id'                : 1,
   'CWORD1'                : 0x0004,
   }

prm_DBI_Fail_Limits_140 = {
   'test_num'              : 140,
   'prm_name'              : 'prm_DBI_Fail_Limits_140',
   'timeout'               : 1800,
   'spc_id'                : 1,
   'CWORD1'                : 0x2000,
   'UNVER_LIMIT'           : 0xFFFF,
   'VERIFIED_DRIVE_LIMIT'  : 0xFFFF,            # Verified flaw limit for drive.
   'VERIFIED_HEAD_LIMIT'   : 0xFFFF,            # Verified flaw limit per head
   'VERIFIED_TRACK_LIMIT'  : 0xFFFF,            # Verified flaw limit per track
   'VERIFIED_CYL_LIMIT'    : 0xFFFF,            # Verified flaw limit per cylinder
   'UNVER_HD_ZONE_LIMIT'   : (0xFFFF, 0xFFFF),  # Unverified flaw limit per head-zone (in hundreds)
   'HEAD_UNVER_LIMIT'      : (0xFFFF, 0xFFFF),  # Unverified flaw limit per head (in hundreds).
   'PATTERN_IDX'           : 0xFFFF,            # Index pattern mask (Pattern is only 2-byte long)
   }

if testSwitch.FE_0258915_348429_COMMON_TWO_TEMP_CERT_SCRN_A00004:
   ID_REGION_VRFD_FLAW_LIMIT =  {
        'ATTRIBUTE'          : 'HGA_SUPPLIER',
        'DEFAULT'            : 'RHO',
        'RHO'                : 0xFFFF,
        'HWY'                : 500,
        'TDK'                : 500,}
   ID_REGION_UNVRFD_FLAW_LIMIT =  {
        'ATTRIBUTE'          : 'HGA_SUPPLIER',
        'DEFAULT'            : 'RHO',
        'RHO'                : 0xFFFF,
        'HWY'                : 15000,
        'TDK'                : 15000,}
DataFlawFeatures = {
   '9SM'                      : ['AFS'],
   '9TS'                      : ['AFS'],
   '9TT'                      : ['AFS'],
   '1DG'                      : ['AFS'],
   '1E9'                      : ['AFS'],
   '1G7'                      : ['AFS'],
   '1G8'                      : ['AFS'],
   }

# Use for T83 AGC
pesMeasurePrm_83_agc01 = {
  'test_num'        : 83,
  'prm_name'        : 'pesMeasurePrm_83_agc01',
  'spc_id'          : 1,
  "TEST_CYL"        : (1L,0,),
  'END_CYL'         : (4L,0x1540,),
  "NUM_SAMPLES"     : (1,),
  "AGC_TRACK_SPAN"  : (100,),
  "REVS"            : (8,),
  "TEST_HEAD"       : (0x00FF,),
  "CWORD1"          : (0x00C0,),
  "S_OFFSET" 		: (0,),
  #"AGC_MINMAX_DELTA" : 120,
  'AGC_MINMAX_DELTA'          : {      # AGC min to max delta to trigger destroke
     'ATTRIBUTE'       : 'IS_2D_DRV',
     'DEFAULT'         : 0,
     0                 : 100, # 30 is added by C2T Switch to become 100
     1                 : {
        'ATTRIBUTE' : 'BG',
        'DEFAULT'   : 'OEM1B',
        'OEM1B'     : 90, # 30 is added by C2T Switch to become 90
        'SBS'       : 80,        
        },
     },
  'timeout'         : 10000,
}

if testSwitch.REDUCE_LOG_SIZE:
   pesMeasurePrm_83_agc01.update({'CWORD1': 0x40,})

pesMeasurePrm_83_agc01_ds = {
  'AGC_MINMAX_DELTA_MARGIN'     : {      # AGC min to max delta margin to pass AGC_SCRN once destroke done to avoid marginal pass
     'ATTRIBUTE'          : 'HGA_SUPPLIER',
     'DEFAULT'            : 'RHO',
     'RHO'                : 20,
     'HWY'                : 20,
     'TDK'                : 20,},
  'DS_MAX_CYL'          : {
      'ATTRIBUTE' : 'BG',
      'DEFAULT'   : 'OEM1B',
      'OEM1B'     : 22000,
      'SBS'       : 12000,
      },
  'DS_STEP'             : 2000,
  'DS_DEEP_TRY'         : 10000,
}

if testSwitch.CHENGAI:
   Destroke_Trk_To_Load_A_New_RAP = 15000
else:
   Destroke_Trk_To_Load_A_New_RAP = {
       'ATTRIBUTE' : 'BG',
       'DEFAULT'   : 'OEM1B',
       'OEM1B'     : 10000, # Max allowed destroked tracks
       'SBS'       : 12000, # Max allowed destroked tracks
      }

OsRangePrm_11 = {
   'enable' : {
      'test_num'           : 11,
      'prm_name'           : 'ModifyOsRange',
      'spc_id'             : 100,
      'CWORD1'             : 0x0400,
      'SYM_OFFSET'         : 431,      #  Symbol Offset
      'WR_DATA'            : {
         'ATTRIBUTE'          : 'HGA_SUPPLIER',
         'DEFAULT'            : 'RHO',
         'RHO'                : 0x0133,
         'HWY'                : 0x0100,
         'TDK'                : 0x0100,
         },
      'MASK_VALUE'         : 0,
      'NUM_LOCS'           : 0,
      'timeout'            : 120,
   },
   'read': {
      'test_num'           : 11,
      'prm_name'           : 'ReadOsRangeAdd',
      'spc_id'             : 100,
      'CWORD1'             : 0x0200,
      'SYM_OFFSET'         : 431,      #  Symbol Offset
      'NUM_LOCS'           : 0,
      'timeout'            : 120,
   },
   'saveSAP': {
      'test_num'           : 178,
      'prm_name'           : 'save SAP to FLASH',
      'spc_id'             : 100,
      'CWORD1'             : 0x420,
   },
}
IwRiseTimePrm_11 = {
   'IwRiseTime_lsi' : {
      'test_num'           : 11,
      'prm_name'           : 'IwRiseTime',
      'spc_id'             : 100,
      'CWORD1'             : 0x0400,
      'SYM_OFFSET'         : 431,      #  Symbol Offset
      'WR_DATA'            : 0x0050,   #  218 ps
      'MASK_VALUE'         : 0xFF0F,
      'NUM_LOCS'           : 0,
      'timeout'            : 120,
   },
   'IwRiseTime_ti' : {
      'test_num'           : 11,
      'prm_name'           : 'IwRiseTime',
      'spc_id'             : 100,
      'CWORD1'             : 0x0400,
      'SYM_OFFSET'         : 431,      #  Symbol Offset
      'WR_DATA'            : 0x0060,   #  225 ps
      'MASK_VALUE'         : 0xFF0F,
      'NUM_LOCS'           : 0,
      'timeout'            : 120,
   },
   'read': {
      'test_num'           : 11,
      'prm_name'           : 'IwRiseTime',
      'spc_id'             : 100,
      'CWORD1'             : 0x0200,
      'SYM_OFFSET'         : 431,      #  Symbol Offset
      'NUM_LOCS'           : 0,
      'timeout'            : 120,
   },
   'saveSAP': {
      'test_num'           : 178,
      'prm_name'           : 'save SAP to FLASH',
      'spc_id'             : 100,
      'CWORD1'             : 0x420,
   },
}
WrtZoutPrm_11 = {  #40ohm
   'wrt_lsi' : {
      'test_num'           : 11,
      'prm_name'           : 'Zout',
      'spc_id'             : 100,
      'CWORD1'             : 0x0400,
      'SYM_OFFSET'         : 431,      #  Symbol Offset
      'WR_DATA'            : 0x0003,
      'MASK_VALUE'         : 0xFFF0,
      'NUM_LOCS'           : 0,
      'timeout'            : 120,
   },
   'wrt_ti' : {
      'test_num'           : 11,
      'prm_name'           : 'Zout',
      'spc_id'             : 100,
      'CWORD1'             : 0x0400,
      'SYM_OFFSET'         : 431,      #  Symbol Offset
      'WR_DATA'            : 0x0002,
      'MASK_VALUE'         : 0xFFF0,
      'NUM_LOCS'           : 0,
      'timeout'            : 120,
   },
   'read': {
      'test_num'           : 11,
      'prm_name'           : 'Zout',
      'spc_id'             : 100,
      'CWORD1'             : 0x0200,
      'SYM_OFFSET'         : 431,      #  Symbol Offset
      'NUM_LOCS'           : 0,
      'timeout'            : 120,
   },
   'saveSAP': {
      'test_num'           : 178,
      'prm_name'           : 'save SAP to FLASH',
      'spc_id'             : 100,
      'CWORD1'             : 0x420,
   },
}

MAX_NOMINAL_VTPI_CYL_WITH_DESTROKE_Prm_11 = {
   'enable' : {
      'test_num'           : 11,
      'prm_name'           : 'ModifyMaxNominalVtpiCyl',
      'spc_id'             : 100,
      'CWORD1'             : 0x0400,
      'ACCESS_TYPE'        : 3,
      'SYM_OFFSET'         : 247,      #  Symbol Offset
      'WR_DATA'            : {
         'ATTRIBUTE'          : 'HGA_SUPPLIER',
         'DEFAULT'            : 'RHO',
         'RHO'                : 0x84A4,
         'HWY'                : 0x84A4,
         'TDK'                : 0x84A4,
         },
      'EXTENDED_WR_DATA'      : {
         'ATTRIBUTE'          : 'HGA_SUPPLIER',
         'DEFAULT'            : 'RHO',
         'RHO'                : 0x3,
         'HWY'                : 0x3,
         'TDK'                : 0x3,
         },
      'MASK_VALUE'         : 0,
      'EXTENDED_MASK_VALUE': 0,
      'NUM_LOCS'           : 0,
      'timeout'            : 120,
   },
   'read': {
      'test_num'           : 11,
      'prm_name'           : 'ReadMaxNominalVtpiCyl',
      'spc_id'             : 100,
      'CWORD1'             : 0x0200,
      'ACCESS_TYPE'        : 3,
      'SYM_OFFSET'         : 247,      #  Symbol Offset
      'NUM_LOCS'           : 0,
      'timeout'            : 120,
   },
   'saveSAP': {
      'test_num'           : 178,
      'prm_name'           : 'save SAP to FLASH',
      'spc_id'             : 100,
      'CWORD1'             : 0x420,
   },
}

preampRisingPrm_11 = {
   'enable' : {
      'test_num'           : 11,
      'prm_name'           : 'ModifyPreampRising',
      'spc_id'             : 100,
      'CWORD1'             : 0x0400,
      'SYM_OFFSET'         : 431,      #  Symbol Offset
      'WR_DATA'            : {
         'ATTRIBUTE'          : 'HGA_SUPPLIER',
         'DEFAULT'            : 'TDK',
         #'RHO'                : 0x0133,
         'HWY'                : 0x8000,
         'TDK'                : 0x8000,
         },
      'MASK_VALUE'         : 0,
      'NUM_LOCS'           : 0,
      'timeout'            : 120,
   },
   'read': {
      'test_num'           : 11,
      'prm_name'           : 'ReadPreampRising',
      'spc_id'             : 100,
      'CWORD1'             : 0x0200,
      'SYM_OFFSET'         : 431,      #  Symbol Offset
      'NUM_LOCS'           : 0,
      'timeout'            : 120,
   },
   'saveSAP': {
      'test_num'           : 178,
      'prm_name'           : 'save SAP to FLASH',
      'spc_id'             : 100,
      'CWORD1'             : 0x420,
   },
}
##################### SERVO SCREENS #####################################
# Servo Screens


LULDefectScanPrm_109 = {
   'test_num'           : 109,
   'prm_name'           : 'LULDefectScanPrm_109',
   'timeout'            : 14400*numHeads,
   'spc_id'             : 1,
   'CWORD1'             : 0x0441,
   'CWORD2'             : 0x0888,
   'START_CYL'          : (0x0000, 0x0000),
   'END_CYL'            : (0xFFFF, 0xFFFF),
   'HEAD_CLAMP'         : 600,
   'RW_MODE'            : 0x4180,
   'TRACK_LIMIT'        : 80,
   'ZONE_LIMIT'         : 0xFDE8,
   'HEAD_RANGE'         : 0x00FF,
   'PASS_INDEX'         : 0,
   'IGNORE_UNVER_LIMIT' : (),
   'SFLAW_OTF'          : (),
   'ERRS_B4_SFLAW_SCAN' : 1,
   'VERIFY_GAMUT'       : (2, 3, 10),
   'SKIP_TRACK'         : 1,
   'LUL_SCAN_SCRATCH'   : (0xFFFF, 50000, 200, 2000, 5000, 20),
   'FSB_SEL'            : (0x0088, 0x0000),
   'SET_XREG00'         : (0x0A12, 0x0000, 0x1BCC),    # TAEP_OFF
   'SET_XREG01'         : (0x0A12, 0x0003, 0x1B74),    # TA_HOLD
   'SET_XREG02'         : (0x0A12, 0x0003, 0x1B30),    # TA_DLY
   'SET_XREG03'         : (0x1215, 0x0006, 0x1BFC),    # ZGR_DIFF
   'SET_XREG04'         : (0x129c, 0x0000, 0x1B30),    # ZGS_ENR
   'SET_XREG05'         : (0x1211, 0x0000, 0x1B76),    # GUG_FLAW
   'SET_XREG06'         : (0x123C, 0x00FA, 0x1B70),    # QMLVL2
   'SET_XREG07'         : (0x1210, 0x0005, 0x1Bec),    # GUG_ACQR
   'SET_XREG08'         : (0x1210, 0x0000, 0x1Ba8),    # GUGR
   'SET_XREG15'         : (0x1237, 0x0004, 0x1B40),    # QMTOL
   'SET_XREG16'         : (0x1237, 0x0005, 0x1BC8),    # QMLEN
   'SET_XREG17'         : (0x1240, 0x000e, 0x1B70),    # QMLVL
   'SET_XREG20'         : (0x121E, 0x0001, 0x1B32),    # ZPSLENR
   'SET_XREG21'         : (0x123C, 0x0003, 0x1BB8),    # QMLEN2
   'SET_XREG22'         : (0x123A, 0x0001, 0x1BD8),    # DEFSEP
   'SET_XREG23'         : (0x123D, 0x0014, 0x1B50),    # MAX_CNT
   'SET_XREG24'         : (0x12b8, 0x0000, 0x1BA9),    # GWINSEL2T
   'SET_XREG25'         : (0x12b8, 0x0000, 0x1BFB),    # GWINCNT2
   'SET_XREG26'         : (0x12b6, 0x0064, 0x1B80),    # GWINTHRSH2T
   'SET_XREG28'         : (0x121E, 0x0000, 0x1B74),    # ACQLENR
}


DSP_ScanWritePrm_109 = {
   'test_num'              : 109,
   'prm_name'              : 'DSP_ScanWritePrm_109',
   'timeout'               : 14400*numHeads,
   'spc_id'                : 1,
   'START_CYL'             : (0, 0x0CD7),          #     3287
   'END_CYL'               : (1, 0x3845),          #     79941
   'RW_MODE'               : 0x0100,
   'HEAD_RANGE'            : 0x00FF,
   'HEAD_CLAMP'            : 5000,
   'TRACK_LIMIT'           : 5,
   'ZONE_LIMIT'            : 50000,
   'ERRS_B4_SFLAW_SCAN'    : 1,
   'SWD_RETRY'             : 0x0305,
   'FREQUENCY'             : Analog_FS_Freq,
   'SET_OCLIM'             : -36,                  # Tolerate servo offtrack
   }


DSP_ScanReadPrm_109 = {
   'test_num'           : 109,
   'prm_name'           : 'DSP_ScanReadPrm_109',
   'timeout'            : 18000*numHeads,
   'spc_id'             : 1,
   'CWORD1'             : 0x0043,
   'CWORD2'             : 0x0888,            # Early Flawscan OFF
   'CWORD4'             : 0x0020,            # Training Read
   'RW_MODE'            : 0x4000,
   'START_CYL'         : (0, 0x0CD7),        #     3287
   'END_CYL'           : (1, 0x3845),        #     79941
   'HEAD_RANGE'         : 0x00FF,
   'HEAD_CLAMP'         : 300,
   'TRACK_LIMIT'        : 16,
   'ZONE_LIMIT'         : 100000,
   'VERIFY_GAMUT'       : (2, 3, 10),
   'IGNORE_UNVER_LIMIT' : (),
   'PASS_INDEX'         : 0,
   'ERRS_B4_SFLAW_SCAN' : 20,
   'PER_TRK_SFLW_LIM'   : 32,
   'SET_OCLIM'          : -36,               # Tolerate servo offtrack
   'TA_THRESHOLD'       : 0x0008,            # TA LVL
   'DIVISOR'            : 0x003F,
   'FSB_SEL'            : (0x0589, 0),       # 0,3,7,8,10    0X589
   'SFLAW_OTF'          : (),
   'SET_XREG00'         : (210, 1,   7116),  # TAEP_EN
   'SET_XREG01'         : (210, 3,   7028),  # TA_hold
   'SET_XREG02'         : (210, 3,   6960),  # TADLY
   'SET_XREG03'         : (153, 6,   7164),  # ZGRDIFF   12
   'SET_XREG04'         : (165, 0,   7116),  # ZGS_ENR
   'SET_XREG05'         : (149, 0,   7030),  # GUG_FLAW
   'SET_XREG06'         : (229, 0,   7031),  # Def_Scan
   'SET_XREG07'         : (149, 5,   6995),  # GUGACQR was 6
   'SET_XREG09'         : (225, 2,   6976),  # QM_TOL     3
   'SET_XREG10'         : (226, 1037,7104),  # QM_LVL 9,LEN 5
   'SET_XREG11'         : (230, 0,   7096),  # QM_LEN2
   'SET_XREG12'         : (231, 10,  6992),  # MAXCNT
   'SET_XREG13'         : (233, 32,  6992),  # Def_SEP
   'SET_XREG14'         : (230, 226, 7024),  # QM_LVL2
   'SET_XREG15'         : (152, 1,   7065),  # GUGLIMR
   'SET_XREG16'         : (166, 0,   7028),  # ACQLENR
   'SET_XREG17'         : (149, 2,   6944),  # GUGR
   'SET_XREG18'         : (152, 1,   7082),  # SHADOWR
   'SET_XREG19'         : (396, 1,   7081),  # GWIN_SEL_2T  vgarsh
   'SET_XREG20'         : (398, 30,  7040),  # GWIN_THRSH_2T (1.41DB)
   'SET_XREG21'         : (396, 2,   7163),  # GWIN_CNT_2T   (8T)
   'SET_XREG22'         : (146, 4,   7056),  # AMCNT
   'SET_XREG24'         : ( 0x00B0, 0x4A, 0x1BF8 ),
   'SET_XREG25'         : ( 0x00B2, 0x4A, 0x1B70 ),
   'SET_XREG26'         : ( 0x00B3, 0xB0, 0x1B70 ),
   'SET_XREG27'         : ( 0x00B4, 0x6F, 0x1B70 ),
   'SET_XREG28'         : ( 0x00B7, 0x02, 0x1BBA ),
   'SET_XREG29'         : ( 0x007D, 0x01, 0x1BFF ),
   'FREQUENCY'          : Analog_FS_Freq,
   }

#Prasanna Added This
DSP_LULDefectScanPrm_109 = {
   'test_num'           : 109,
   'prm_name'           : 'DSP_LULDefectScanPrm_109',
   'timeout'            : 36000,
   'spc_id'             : 1,
   'CWORD1'             : 0x0441,
   'CWORD2'             : 0x08C0, #Changed from 0x8c0 to disable writes
   'CWORD4'             : 0x8000, # Use Or'ed Comparator
   'START_CYL'          : (2,0x22e0),#140K
   'END_CYL'            : (3,0x3450),#210K
   'HEAD_CLAMP'         : 600,
   'RW_MODE'            : 0x4080, #Change from 0x4180 to disable write
   'TRACK_LIMIT'        : 80,
   'ZONE_LIMIT'         : 0xFDE8,
   'HEAD_RANGE'         : 0x00F,
   'PASS_INDEX'         : 0,
   'IGNORE_UNVER_LIMIT' : (),
   'SFLAW_OTF'          : (),
   'ERRS_B4_SFLAW_SCAN' : 1,
   'VERIFY_GAMUT'       : (2, 3, 10),
   'SKIP_TRACK'         : 1,
   'LUL_SCAN_SCRATCH'   : (1000, 25000, 2000, 2000, 5000, 20),# used to be -> (0xFFFF, 50000, 200, 2000, 5000, 20),
   #   [Allowed_Errors], [Max_Symbols_Per_Region], [Num_Trks_Per_Region], [Delta_Symbols], [Max_Scratch_Span], [Radial_Fill_Cnt]
   'FSB_SEL'            : (0x0008, 0x0000),
   'SET_XREG00': ( 0x0A12, 0x0000, 0x1BCC ),
   'SET_XREG01': ( 0x0A12, 0x0003, 0x1B74 ),
   'SET_XREG02': ( 0x0A12, 0x0003, 0x1B30 ),
   'SET_XREG07': ( 0x1210, 0x0005, 0x1Bdc ),
   'SET_XREG08': ( 0x1210, 0x0000, 0x1Ba8 ),
   'SET_XREG28': ( 0x121E, 0x0000, 0x1B74 ),
}

#DSP_Screen_Zones = [0,1,2,3,4,5,6,7,8,9,10,11]
DSP_Screen_Zones = [8,9,10,11,12,13,14,15,16] #Prasanna
#DSP_Screen_Zones = [3,4]

DspScreen_140 = {
   'test_num'                 : 140,
   'prm_name'                 : 'DspScreen_140',
   'spc_id'                   : 1,
   'CWORD1'                   : 0x0001,
   'timeout'                  : 12000,
   'HEAD_RANGE'               : 0xFFFF,
   'PERCENT_LIMIT'            : 50,
   'START_CYL'                : (0, 0x0CD7),          #     3287
   'END_CYL'                  : (1, 0x3845),          #     79941
   'MINIMUM'                  : 100,
   }

#########################Interface#################################################################

ATA_READY_CHCK = 1

prm_PowerOffTime = {
   'seconds'            : 5,
   }
prm_PowerOnTime = {
   'seconds'            : 5,
   }

USB_IDENTIFIER = ['BS']

prm_IntfTest={
   'ATTRIBUTE' :'ATA_ReadyTimeout',
      'DEFAULT':'USB',

      'USB'    :{
         "Default CPC Cmd Timeout": 15,      #USB
         "Default ICmd Timeout"   : 180000,  #50 hours

         "Read_maxLBAPercent": 2,
         "Read_numZones"     : 1,
         "Read_zoneLocation" : 'OD',
         "Read_xfer_key"     : 0x45,

         "Write_maxLBAPercent": 2,
         "Write_numZones"     : 1,
         "Write_zoneLocation" : 'OD',
         "Write_xfer_key"     : 0x45,

         "RW_maxLBAPercent": 1,
         "RW_numZones"     : 1,
         "RW_zoneLocation" : 'OD',

         "5V_margin"          : 0.05,
         "12V_margin"         : 0.1,
         "tests"              : ['H-N', 'L-N', 'N-N'],  # can also include 'N-H', 'N-L', H-N', 'L-N'
	   },

      'NON_USB':{
         "Default CPC Cmd Timeout": 10,      #Non-USB
         "Default ICmd Timeout"   : 180000,  #50 hours

         "Read_maxLBAPercent": 2,
         "Read_numZones"     : 1,
         "Read_zoneLocation" : 'OD',
         "Read_xfer_key"     : 0x45,

         "Write_maxLBAPercent": 2,
         "Write_numZones"     : 1,
         "Write_zoneLocation" : 'OD',
         "Write_xfer_key"     : 0x45,

         "RW_maxLBAPercent": 1,
         "RW_numZones"     : 1,
         "RW_zoneLocation" : 'OD',

         "5V_margin"          : 0.05,
         "12V_margin"         : 0.1,
         "tests"              : ['H-N', 'L-N', 'N-N'],  # can also include 'N-H', 'N-L', H-N', 'L-N'
	   },
}
#FDE type matrix reference by process group
FDEMatrix = {
            "FDE Base" :
                         {
                            'IssueFDECard'  : 'FALSE',
                            'ATA_Mode'      : 'FALSE',
                            'PreBoot'       : 'FALSE',
                            'USB_FDE'       : 'FALSE',
                            'PreBootImage'  : 'None',
                            'SBS'           : 'FALSE',
                            'REMOTE_ISSUANCE':'TRUE'
                            },
            "ATA Only"  :
                         {
                            'IssueFDECard'  : 'FALSE',
                            'ATA_Mode'      : 'TRUE',   #ATA Only
                            'PreBoot'       : 'FALSE',
                            'USB_FDE'       : 'FALSE',
                            'PreBootImage'  : 'None',
                            'SBS'           : 'FALSE',
                            'REMOTE_ISSUANCE':'TRUE'
                            },
            "Internal USB Enabled"  :
                         {
                            'IssueFDECard'  :'TRUE',
                            'ATA_Mode'      :'FALSE',
                            'PreBoot'       :'TRUE',
                            'USB_FDE'       :'TRUE',
                            'PreBootImage'  :'TRUE',    #Internal USB
                            'SBS'           :'TRUE',
                            'REMOTE_ISSUANCE':'FALSE'
                            },
            "OEM USB Enabled"       :
                         {
                            'IssueFDECard'  :'TRUE',
                            'ATA_Mode'      :'FALSE',
                            'PreBoot'       :'TRUE',
                            'USB_FDE'       :'TRUE',
                            'PreBootImage'  :'None',
                            'SBS'           :'TRUE',
                            'REMOTE_ISSUANCE':'FALSE'
                            },
            }

CUSTOMER_TYPE = {
   'APPLE'  : ['APPLE_SCREENS','APPLE_ATI','APPLETHREAD','BLUENUN','BLUENUN_SLIDE','AP1','AP2','AP3','AP4','AP5'],
   'TCG'    : ['TCG'],
   'HP'     : ['HP_SCREEN'],        # Need to update actual HP screen(s) when available on PIF
   'LENOVO' : ['LENOVO_SCREEN'],    # Need to update actual LENOVO screen(s) when available on PIF
}

##############################  DR IO specs v1.0 ###############################
prm_598_limit = 0.8

if testSwitch.FE_0385234_356688_P_MULTI_ID_UMP:
   prm_598_limit = 0.0  # temp skip check, pending process code update

if testSwitch.ROSEWOOD7:
   prm_598_spec = {
      '5400' : {
             '2000':{'4':[140 * prm_598_limit, 65 * prm_598_limit]},    # Rosewood7 2-disk.
             '1950':{'4':[125 * prm_598_limit, 56 * prm_598_limit]},    # Rosewood7 2-disk.             
             '1860':{'4':[125 * prm_598_limit, 56 * prm_598_limit]},    # Rosewood7 2-disk.
             '1740':{'4':[125 * prm_598_limit, 56 * prm_598_limit]},    # Rosewood7 2-disk.
             '1620':{'4':[125 * prm_598_limit, 56 * prm_598_limit]},    # Rosewood7 2-disk.
             '1500':{'4':[125 * prm_598_limit, 56 * prm_598_limit],     # Rosewood7 2-disk.
                     '3':[125 * prm_598_limit, 56 * prm_598_limit]},    # Rosewood7 2-disk, 3 head depop
             '1000':{'4':[125 * prm_598_limit, 56 * prm_598_limit],     # Rosewood7 2-disk @1T, 
                     '3':[125 * prm_598_limit, 56 * prm_598_limit],     # Rosewood7 2-disk, 3 head depop
                     '2':[140 * prm_598_limit, 65 * prm_598_limit]},    # Rosewood7 1-disk as per DR spec 1.0
             '970' :{'2':[125 * prm_598_limit, 56 * prm_598_limit]},    # Rosewood7 1-disk as per DR spec 1.0
             '930' :{'2':[125 * prm_598_limit, 56 * prm_598_limit]},    # Rosewood7 1-disk as per DR spec 1.0
             '870' :{'2':[125 * prm_598_limit, 56 * prm_598_limit]},    # Rosewood7 1-disk as per DR spec 1.0
             '810' :{'2':[125 * prm_598_limit, 56 * prm_598_limit]},    # Rosewood7 1-disk as per DR spec 1.0
             '750' :{'2':[125 * prm_598_limit, 56 * prm_598_limit]},    # Rosewood7 1-disk as per DR spec 1.0
             '500' :{'2':[125 * prm_598_limit, 56 * prm_598_limit]},    # Rosewood7 1-disk as per DR spec 1.0
             },
   }
   if DriveAttributes.get('BSNS_SEGMENT','NONE') == 'SBS': # Request from RW1D CT to salvage ~0.8% SBS 1TB yield lost by loosening ID spec
      prm_598_spec['5400']['1000']['2'] = [140 * prm_598_limit, 60 * prm_598_limit]
      prm_598_spec['5400']['500']['2']  = [100 * prm_598_limit, 50 * prm_598_limit]
      prm_598_spec['5400']['2000']['4'] = [140 * prm_598_limit, 60 * prm_598_limit]

elif testSwitch.SMR:
   prm_598_spec = {
      '5400' : {
             '4000':{'10':[50 * prm_598_limit, 20 * prm_598_limit]},
             '2000':{'4':[100 * prm_598_limit, 50 * prm_598_limit]},
             '1500':{'4':[100 * prm_598_limit, 50 * prm_598_limit]},
             '1000':{'2':[100 * prm_598_limit, 50 * prm_598_limit]},
             '750' :{'2':[100 * prm_598_limit, 50 * prm_598_limit]},
             '720' :{'2':[100 * prm_598_limit, 50 * prm_598_limit]},  # Chengai interim capacity
             '680' :{'2':[100 * prm_598_limit, 50 * prm_598_limit]},  # Chengai interim capacity
             '640' :{'2':[100 * prm_598_limit, 50 * prm_598_limit]},
             '500' :{'2':[100 * prm_598_limit, 50 * prm_598_limit]},
             '320' :{'2':[80  * prm_598_limit, 40 * prm_598_limit]},
             '250' :{'1':[100 * prm_598_limit, 50 * prm_598_limit]},
             },
   }
else:
   prm_598_spec = {
      '5400' : {
             '1000':{'4':[100 * prm_598_limit, 50 * prm_598_limit]},
             '750' :{'4':[100 * prm_598_limit, 50 * prm_598_limit]},
             '500' :{'2':[100 * prm_598_limit, 50 * prm_598_limit]},
             '320' :{'2':[80  * prm_598_limit, 40 * prm_598_limit]},
             '250' :{'1':[100 * prm_598_limit, 50 * prm_598_limit]},
             },
   }
OFWXferRatioLimit = 0.65
# Key customers: HP/Lenovo/DVR
# As per YarraR DR specs 3.1
prm_PowerControl={
   '5400' : {
               'ATTRIBUTE' : 'ATA_ReadyTimeout',
               'DEFAULT'   : 'USB',
               'USB'       : {
                              'STD_OEM'   : {1:10000, 2:10000, 3:10000, 4:10000},
                              'FDE'       : {1:6000, 2:6000, 3:6000, 4:6000},
                             },
               'NON_USB'   : {
                              'STD_OEM'   : {1:4000, 2:4000, 3:4000, 4:4000},
                              'APPLE'     : {1:3000, 2:3000, 3:3000, 4:3000},
                              'FDE'       : {1:6000, 2:6000, 3:6000, 4:6000},
                             },
            },
   }
# Unique TTR limit by part number tab {'tab': ttr limit}
# For multiple product family, change prm_TTR_ByPn = {'1DG...-(567|99.)' : 5500, '1E9...-995' : 4500}
prm_TTR_ByPn = {
                  '1R(K|C|D)...-...'       : 3500, # Rosewood7 1D - temp relax TTR
                  '1U(7|8|9|A|B|C)...-...' : 3500, # Rosewood7H 1D - temp relax TTR
                  '1R(8|9|A)...-...'       : 5000, # Rosewood7 2D - temp relax TTR
                  '1R(G|H|J)...-...'       : 5000, # Rosewood7H 2D - temp relax TTR
                  '1U(4|5|6)...-...'       : 5000, # Rosewood7H 2D - temp relax TTR
               }

# RW7-2D Common Part Number for 1TB Support
#if testSwitch.IS_2D_DRV == 1:
if HDASerialNumber[1:3] in ['C0', 'C7', 'C8', 'BZ', '94', 'CC','F5','F4']: # RW7-2D S/N prefix for 3H and 4H
   prm_TTR_ByPn['1R(K|C|D)...-...'] = 5000 # Rosewood7 2D. Follow '1R(8|9|A)...-...'

# RW71D and 2D SBS drives with low current spin up TTR spec. is 8sec
SBS_TTR_Spec = 8000


# T528 offset in SIC cells (ms)
T528_OFFSET = 100          # For other new products Karnak, SMR, Angsana2D.
                           # Offset still needs to be studied/ verified.

if testSwitch.NEW_TTR_SPEC_CHECK: #For RW2D
   SPTTR_OFFSET = -30.0  # SP TTR temperature offset (ms) requested by RW72D core team
   MAX_SPTTR_COUNT_ALLOWED = 3 #Failed drive if 3F/20 TTR measurement > Max TTR spec.
else:
   SPTTR_OFFSET = 0.0         # SP TTR offset (ms)

#st(508, CTRL_WORD1 = 0x0005, BYTE_OFFSET = (0,0), BUFFER_LENGTH = (0,1536), timeout = 3600)
# Read and display the read buffer
prm_508_3 = {
   'test_num'                 : 508,
   'prm_name'                 : 'prm_508_3',
   'timeout'                  : 3600,
   'spc_id'                   : 1,
   'CTRL_WORD1'               : (0x0005),
   'BYTE_OFFSET'              : (0,0),
   'BUFFER_LENGTH'            : (0,1536),
}

# Read and display the write buffer
prm_508_2_WB32B = {
   'test_num'                 : 508,
   'prm_name'                 : 'prm_508_2_WB32B',
   'CTRL_WORD1'               : (0x0004),
   'BYTE_OFFSET'              : (0,0),
   'BUFFER_LENGTH'            : (0,32),
   'spc_id'                   : (1),
   'timeout'                  : 3600,
#'BUFFER_LENGTH' : (0,0x8000),
}

prm_509_Rd_r1 = {
   'test_num'                 : 509,
   'prm_name'                 : 'prm_509_Rd_r1',
   'CTRL_WORD1'               : 0x0010, # 0x0030= Rd w/ DiTS cmd, 0x00=Wt/Rd, 0x10=Read, 0x20=Wrt
   'ZONE'                     : 0,
   'MULTIPLIER'               : 1,
   'BLKS_PER_XFR'             : 200,    # Changed value from 512 -> 50 to prevent hang
   'MAX_NBR_ERRORS'           : 0xFFFF, # Error limit only have effect on DITS mode only
   'MAX_ERROR_RATE'           : 371,
   'RESET_AFTER_ERROR'        : 0,
   'FREE_RETRY_CONTROL'       : 1,      # 1 = Disable Free Retries
   'HIDDEN_RETRY_CONTROL'     : 1,      # 1 = Disable Hidden Retries
   'DISABLE_ECC_ON_THE_FLY'   : 1,      # 1 = Disable ECC on the fly correction
   'ECC_CONTROL'              : 1,      # 1 = Use T-level correction specified in ECC_T_LEVEL
   'ECC_T_LEVEL'              : 8,      # T-Level if ECC_CONTROL is set. The Default is 0 (All ECC will be disabled)
   'DEBUG_FLAG'               : 0,      # 1 = Enable debug reporting
   'DITS_MODE'                : 1,      # 1 = Enable DITS Read LBA command
   'spc_id'                   : 1,
   'timeout'                  : 3600,
}

prm_510_W10K = {
   'test_num'                 : 510,
   'prm_name'                 : 'prm_510_W10K',
   'spc_id'                   : 1,
   'CTRL_WORD1'               : (0x20),
   'CTRL_WORD2'               : (0x2080),
   'STARTING_LBA'             : (0,0,0,0),
   'TOTAL_BLKS_TO_XFR'        : (0x0001,0x0000),
   'BLKS_PER_XFR'             : (0x100),
   #'DATA_PATTERN0'            : (0x1234, 0x5678),
   'DATA_PATTERN0'            : (0x4433, 0x2211),
   'MAX_NBR_ERRORS'           : (50),
   'timeout'                  : 252000,
   'RESET_AFTER_ERROR'        : (1),
}

prm_510_W1K = {
   'test_num'                 : 510,
   'prm_name'                 : 'prm_510_W1K',
   'spc_id'                   : 1,
   'CTRL_WORD1'               : (0x20),
   'CTRL_WORD2'               : (0x2080),
   'STARTING_LBA'             : (0,0,0,0),
   'TOTAL_BLKS_TO_XFR'        : (0x0000,0x1000),
   'BLKS_PER_XFR'             : (0x100),
   #'DATA_PATTERN0'           : (0x1234, 0x5678),
   'DATA_PATTERN0'            : (0x4433, 0x2211),
   'MAX_NBR_ERRORS'           : (3),
   'timeout'                  : 252000,
   'RESET_AFTER_ERROR'        : (1),
}

prm_510_W400K = {
   'test_num'                 : 510,
   'prm_name'                 : 'prm_510_W400K',
   'spc_id'                   : 1,
   'CTRL_WORD1'               : (0x20),
   'CTRL_WORD2'               : (0x2080),
   'STARTING_LBA'             : (0,0,0,0),
   'TOTAL_BLKS_TO_XFR'        : (0x0006,0x1A80),
   'BLKS_PER_XFR'             : (0x100),
   #'DATA_PATTERN0'           : (0x1234, 0x5678),
   'DATA_PATTERN0'            : (0x0000, 0x0000),
   'MAX_NBR_ERRORS'           : (0),
   'FREE_RETRY_CONTROL'       : 0,
   'HIDDEN_RETRY_CONTROL'     : 0,
   'RPT_HIDDEN_RETRY_CNTRL'   : 0,
   'DISABLE_ECC_ON_THE_FLY'   : 0,
   'ECC_CONTROL'              : 0,
   'CCT_BIN_SETTINGS'         : (0x0A02),
   'timeout'                  : 600000,
   'RESET_AFTER_ERROR'        : (1),
}

prm_510_W1K = {
   'test_num'                 : 510,
   'prm_name'                 : 'prm_510_W1K',
   'spc_id'                   : 1,
   'CTRL_WORD1'               : (0x20),
   'CTRL_WORD2'               : (0x2080),
   'STARTING_LBA'             : (0,0,0,0),
   'TOTAL_BLKS_TO_XFR'        : (0x0000,0x1000),
   'BLKS_PER_XFR'             : (0x100),
   #'DATA_PATTERN0'           : (0x1234, 0x5678),
   'DATA_PATTERN0'            : (0x4433, 0x2211),
   'MAX_NBR_ERRORS'           : (3),
   'timeout'                  : 252000,
   'RESET_AFTER_ERROR'        : (1),
}

prm_510_FPW= {
   'test_num'                 : 510,
   'prm_name'                 : "prm_510_FPW",
   'timeout'                  : 252000,
   'spc_id'                   : 1,
   "CTRL_WORD1"               : (0x20),
   "CTRL_WORD2"               : (0x2080),             # (0x2082)
   "STARTING_LBA"             : (0,0,0,0),
   "TOTAL_BLKS_TO_XFR"        : (0x0000,0x0000),      # Full pack
   "BLKS_PER_XFR"             : (0x100),
   "DATA_PATTERN0"            : (0x0000, 0x0000),     # (0x1234, 0x5678),
   "MAX_NBR_ERRORS"           : (0),
   #"RESET_AFTER_ERROR" : (1)                         # Don K. put the reset inside his code as default
   }
prm_510_FPR= {
   'test_num'                 : 510,
   'prm_name'                 : "prm_510_FPR",
   'timeout'                  : 252000,
   'spc_id'                   : 1,
   "CTRL_WORD1"               : (0x10),
   "CTRL_WORD2"               : (0x2080),
   "STARTING_LBA"             : (0,0,0,0),
   "TOTAL_BLKS_TO_XFR"        : (0x0000,0x0000),      # Full pack
   "BLKS_PER_XFR"             : (0x100),
   "DATA_PATTERN0"            : (0x0000, 0x0000),
   "MAX_NBR_ERRORS"           : (0),
   #"RESET_AFTER_ERROR" : (1)                         # Don K. put the reset inside his code as default
   }

################### AVSCAN ##############
## Full pack write.
prm_510_FPW_AVSCAN = {
   'test_num'          :  510,
   'prm_name'          : "prm_510_FPW_AVSCAN",
   'display_info'      : True,
   'timeout'           :  2*25200,
   'spc_id'            :  5,
   "CTRL_WORD1"        : 0x0022,                # Hidden reties disabled, write
   "CTRL_WORD2"        : 0xE080,
   "STARTING_LBA"      : (0,0,0,0),
   "TOTAL_BLKS_TO_XFR" : (0x0000,0x0000),      # Full pack
   "BLKS_PER_XFR"      : 0x100,
   "DATA_PATTERN0"     : (0x0000, 0x0000),     ### 02/06/07 Pattern changed 12345678 -> 00000000
   "MAX_NBR_ERRORS"    : 10,
   "RESET_AFTER_ERROR" : 1,
   "CCT_BIN_SETTINGS"  : 0x1E14,                # 9/10/12 set up 30 bins at 20 ms each
   "MAX_COMMAND_TIME"  : 0xFFFF,                # Failure threashold in ms.  0xFFFF is for data collection, no failing
   "CCT_LBAS_TO_SAVE"  : 0x30,                  # 6/11/08 added for AVSCAN spec
}
## Full pack read.
prm_510_FPR_AVSCAN = {
   'test_num'          : 510,
   'prm_name'          : "prm_510_FPR_AVSCAN",
   'display_info'      : True,
   'timeout'           :  2*25200,
   'spc_id'            :  4,
   "CTRL_WORD1"        : 0x0012,                # Hidden reties disabled, Read
   "CTRL_WORD2"        : 0xE080,                # 09/14/07: Changed 0x2080->ox6080 to report CCT
   "STARTING_LBA"      : (0,0,0,0),
   "TOTAL_BLKS_TO_XFR" : (0x0000,0x0000),      # Full pack
   "BLKS_PER_XFR"      : 0x100,
   "DATA_PATTERN0"     : (0x0000, 0x0000),
   "MAX_NBR_ERRORS"    : 10,
   "RESET_AFTER_ERROR" : 1,
   "CCT_BIN_SETTINGS"  : 0x1E14,                # 9/10/12 set up 30 bins at 10 ms each
   "MAX_COMMAND_TIME"  : 0xFFFF,                # Failure threashold in ms.  0xFFFF is for data collection, no failing
   "CCT_LBAS_TO_SAVE"  : 0x30,                  # 6/11/08 added for AVSCAN spec
}


prm_510_R1K = {
   'test_num'                 : 510,
   'prm_name'                 : 'prm_510_R1K',
   'spc_id'                   : 1,
   'CTRL_WORD1'               : (0x10),
   'CTRL_WORD2'               : (0x2080),
   'STARTING_LBA'             : (0,0,0,0),
   'TOTAL_BLKS_TO_XFR'        : (0x0000,0x1000),
   'BLKS_PER_XFR'             : (0x100),
   'MAX_NBR_ERRORS'           : (3),
   'timeout'                  : 252000,
   'RESET_AFTER_ERROR'        : (1),
}

prm_510_R10K = {
   'test_num'                 : 510,
   'prm_name'                 : 'prm_510_R10K',
   'spc_id'                   : 1,
   'CTRL_WORD1'               : (0x10),
   'CTRL_WORD2'               : (0x2080),
   'STARTING_LBA'             : (0,0,0,0),
   'TOTAL_BLKS_TO_XFR'        : (0x0001,0x0000),
   'BLKS_PER_XFR'             : (0x100),
   'MAX_NBR_ERRORS'           : (50),
   'timeout'                  : 252000,
   'RESET_AFTER_ERROR'        : (1),
}

prm_510_R400K = {
   'test_num'                 : 510,
   'prm_name'                 : 'prm_510_R400K',
   'spc_id'                   : 1,
   'CTRL_WORD1'               : (0x10),
   'CTRL_WORD2'               : (0x2080),
   'STARTING_LBA'             : (0,0,0,0),
   'TOTAL_BLKS_TO_XFR'        : (0x0006,0x1A80),
   'BLKS_PER_XFR'             : (0x100),
   'MAX_NBR_ERRORS'           : (0),
   'timeout'                  : 600000,
}

prm_510_R400KF = {
   'test_num'                 : 510,
   'prm_name'                 : 'prm_510_R400K',
   'spc_id'                   : 1,
   'CTRL_WORD1'               : (0x12),
   'CTRL_WORD2'               : (0x2080),
   'STARTING_LBA'             : (0,0,0,0),
   'TOTAL_BLKS_TO_XFR'        : (0x0006,0x1A80),
   'BLKS_PER_XFR'             : (0x100),
   'MAX_NBR_ERRORS'           : (0),
   'FREE_RETRY_CONTROL'       : 0,
   'HIDDEN_RETRY_CONTROL'     : 0,
   'RPT_HIDDEN_RETRY_CNTRL'   : 0,
   'DISABLE_ECC_ON_THE_FLY'   : 0,
   'ECC_CONTROL'              : 0,
   'CCT_BIN_SETTINGS'         : (0x0A02),
   'timeout'                  : 600000,
   'RESET_AFTER_ERROR'        : (1),
}

prm_510_W400KF = {

   'test_num'                 : 510,
   'prm_name'                 : 'prm_510_W400K',
   'spc_id'                   : 1,
   'CTRL_WORD1'               : (0x22),
   'CTRL_WORD2'               : (0x2080),
   'STARTING_LBA'             : (0,0,0,0),
   'TOTAL_BLKS_TO_XFR'        : (0x0006,0x1A80),
   'BLKS_PER_XFR'             : (0x100),
   'DATA_PATTERN0'            : (0x0000, 0x0000),
   'MAX_NBR_ERRORS'           : (0),
   'FREE_RETRY_CONTROL'       : 0,
   'HIDDEN_RETRY_CONTROL'     : 0,
   'RPT_HIDDEN_RETRY_CNTRL'   : 0,
   'DISABLE_ECC_ON_THE_FLY'   : 0,
   'ECC_CONTROL'              : 0,
   'CCT_BIN_SETTINGS'         : (0x0A02),
   'timeout'                  : 600000,

}

prm_510_R400K_TET3_SCRN = {
    'test_num'                : 510,
    'prm_name'                : 'prm_510_R400K_TET3_SCRN',
    'spc_id'                  : 1,
    'CTRL_WORD1'              : (0x10),
    'CTRL_WORD2'              : (0x2080),
    'STARTING_LBA'            : (0,0,0,0),
    'TOTAL_BLKS_TO_XFR'       : (0x0006,0x1A80),
    'BLKS_PER_XFR'            : (0x100),
    'MAX_NBR_ERRORS'          : (50),
    'timeout'                 : 600000,
    'RESET_AFTER_ERROR'       : (1),
}

prm_510_W400K_TET3_SCRN = {
   'test_num'                 : 510,
   'prm_name'                 : 'prm_510_W400K_TET3_SCRN',
   'spc_id'                   : 1,
   'CTRL_WORD1'               : (0x20),
   'CTRL_WORD2'               : (0x2080),
   'STARTING_LBA'             : (0,0,0,0),
   'TOTAL_BLKS_TO_XFR'        : (0x0006,0x1A80),
   'BLKS_PER_XFR'             : (0x100),
  #'DATA_PATTERN0'            : (0x1234, 0x5678),
   'DATA_PATTERN0'            : (0x0000, 0x0000),
   'MAX_NBR_ERRORS'           : (50),
   'timeout'                  : 600000,
   'RESET_AFTER_ERROR'        : (1),
}

## Full pack read pattern 00.
prm_510_FPR_500 = {
   'test_num'                 : 510,
   'prm_name'                 : 't510_FPR',
   'timeout'                  :  50000,
   'spc_id'                   : 1,
   'CTRL_WORD1'               : (0x10),
   'CTRL_WORD2'               : (0x2080),
   'STARTING_LBA'             : (0,0,0,0),
   'TOTAL_BLKS_TO_XFR'        : (0x0000,0x0000),# Full pack
   'BLKS_PER_XFR'             : (0x100),
   'DATA_PATTERN0'            : (0x0000, 0x0000),     ### 02/06/07 Pattern changed 12345678 -> 00000000
   'MAX_NBR_ERRORS'           : (500),                  ### 02/06/07 Error limit change 10 -> 0
   'RESET_AFTER_ERROR'        : (1)
}

prm_510_RndW = {
   'test_num'                 : 510,
   'prm_name'                 : 'prm_510_RndW',
   'spc_id'                   : 1,
   'CTRL_WORD1'               : (0x23),
   'CTRL_WORD2'               : (0x2080),
   'STARTING_LBA'             : (0,0,0,0),
   'TOTAL_BLKS_TO_XFR'        : (0x01FF,0xC350),# 50,000
   'BLKS_PER_XFR'             : (0x100),
   'DATA_PATTERN0'            : (0x0000, 0x0000),
   'MAX_NBR_ERRORS'           : (0),
   'timeout'                  : 600,
   'RESET_AFTER_ERROR'        : (1)
}
## -------------------------------------------------  T514  -------------------------------

prm_514_ALL = {
    'test_num'                : 514,
    'prm_name'                : 'prm_514_ALL',
    'spc_id'                  : 1,
    'CTRL_WORD1'              : (0x01),
    'CTRL_WORD2'              : (0x0000),
    'timeout'                 : 30000,
}

prm_514_FwRev = {
    'test_num'                : 514,
    'prm_name'                : 'prm_514_FwRev',
    'spc_id'                  : 1,
    'CTRL_WORD1'              : (0x08),         # Display FW rev
    'CTRL_WORD2'              : (0x0000),
    'timeout'                 : 3000,
}

prm_529_G2P_Opt0 = {
   'test_num'                 : 529,
   'prm_name'                 : 'prm_529_G2P_Opt0',
   'spc_id'                   : 1,
   'CTRL_WORD1'               : (1),
   'TEST_FUNCTION'            : (0),            # Option 0 => Display the G-List
   'timeout'                  : 3600
}
prm_529_G2P_Opt1 = {
   'test_num'                 : 529,
   'prm_name'                 : 'prm_529_G2P_Opt1',
   'spc_id'                   : 1,
   'CTRL_WORD1'               : (0),
   'TEST_FUNCTION'            : (1),            # Option 1 => Display and Transfer the G list
   'timeout'                  : 3600
}
prm_529_G2P_Opt2 = {
   'test_num'                 : 529,
   'prm_name'                 : 'prm_529_G2P_Opt2',
   'spc_id'                   : 1,
   'CTRL_WORD1'               : (0),
   'TEST_FUNCTION'            : (2),            # Option 2 => Transfer the G list, No Display
   'timeout'                  : 3600
}

prm_529_DisplayTransferGList = {  #Display G-list and transfer G-list to P-list, and require format after this run
   'test_num' : 529,
   'prm_name' : 'prm_529_DisplayTransferGList',
   'timeout' : 7200,
   'CONDITIONAL_REWRITE' : (0x0000,),
   'DISP_1_WEDGE_SERVO_FLAWS' : (0x0000,),
   'FAIL_ON_SLIPPED_TRK' : (0x0000,),
   'GLIST_OPTION' : (0x0001,),
   'GRADING_OUTPUT' : (0x0000,),
   'MAX_GLIST_ENTRIES' : (0x0000,0xFFFF,),
   'MAX_SERVO_DEFECTS' : (0x0002,),
   'PAD_500_BYTES_UNITS' : (0x0003,),
   'PAD_CYLS' : (0x0005,),
   'PAD_D_GLIST' : (0x0001,),
   'SERVO_DEFECT_FUNCTION' : (0x0001,),
   'SERVO_GAP_BYTE_COUNT' : (0x0000,),
   'SLIPPED_TRACKS_HEAD_NUM' : (0x0000,),
   'SLIPPED_TRACKS_SPEC' : (0x0000,),
   'TEST_FUNCTION' : (0x0000,),
   'TEST_HEAD' : (0x0000,),
   'WEDGES_PER_TRK' : (0x0000,), #Correct value should be read from drive.
   'WEDGE_NUM' : (0x0000,),
}

prm_518_WCE_0_RCD_0 = {  # Clear Write Cache Enable bit to 0, and clear Read Cache Disable bit to 0.
   'test_num' : 518,
   'prm_name' : 'prm_518_WCE_0_RCD_0',
   'timeout' : 1800,
	"DATA_TO_CHANGE" : (0x0001,),
	"MODE_COMMAND" : (0x0001,),
	"MODE_SELECT_ALL_INITS" : (0x0000,),
	"MODE_SENSE_INITIATOR" : (0x0000,),
	"MODE_SENSE_OPTION" : (0x0003,),
	"MODIFICATION_MODE" : (0x0000,),
#	"PAGE_BYTE_AND_DATA" : (0x0220,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,),
	"PAGE_BYTE_AND_DATA34" : (0x0220,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,),
	"PAGE_CODE" : (0x0008,),
	"PAGE_FORMAT" : (0x0000,),
	"SAVE_MODE_PARAMETERS" : (0x0001,),
	"SUB_PAGE_CODE" : (0x0000,),
	"TEST_FUNCTION" : (0x0000,),
	"UNIT_READY" : (0x0000,),
	"VERIFY_MODE" : (0x0000,),
}

prm_518_WCE_1_RCD_0 = {  # Set Write Cache Enable bit to 1, and clear Read Cache Disable bit to 0.
   'test_num' : 518,
   'prm_name' : 'prm_518_WCE_1_RCD_0',
   'timeout' : 1800,
	"DATA_TO_CHANGE" : (0x0001,),
	"MODE_COMMAND" : (0x0001,),
	"MODE_SELECT_ALL_INITS" : (0x0000,),
	"MODE_SENSE_INITIATOR" : (0x0000,),
	"MODE_SENSE_OPTION" : (0x0003,),
	"MODIFICATION_MODE" : (0x0000,),
#	"PAGE_BYTE_AND_DATA" : (0x0221,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,),
	"PAGE_BYTE_AND_DATA34" : (0x0221,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,),
	"PAGE_CODE" : (0x0008,),
	"PAGE_FORMAT" : (0x0000,),
	"SAVE_MODE_PARAMETERS" : (0x0001,),
	"SUB_PAGE_CODE" : (0x0000,),
	"TEST_FUNCTION" : (0x0000,),
	"UNIT_READY" : (0x0000,),
	"VERIFY_MODE" : (0x0000,),
}

## -------------------------------------------------  T598  -------------------------------
# Zone based transfer test - Write
prm_598_w={
   'test_num'      : 598,
   'prm_name'      : "prm_598_w",
   'spc_id'        :  1,
   "timeout"       : 30000,
   "CTRL_WORD1"    : (0x0004), # Write
   "STARTING_ZONE" : (0),
   "ENDING_ZONE"     : {
      'ATTRIBUTE'    : 'numZones',
      'DEFAULT'      : 180,
      24             : (23),
      31             : (30),
      60             : (59),
      120            : (119),
      150            : (149),
      180            : (179),
      },
   "NUM_SERP"        : (8),
   "DATA_PATTERN0"   : (0,0),
   "PATTERN_TYPE"    : (0),
   'BIT_PATTERN_LENGTH': 0x20,
   "REV_TIME"        : 0x2B66,     # Default RPM at 5400
   "BLKS_PER_XFR"    : (0xFF),     # 255 LBAs per xfer
   "HEAD_TO_TEST"    : (0),        # default = 0, SMR drive
   "BAND_OFFSET"     : (0),        # default = 0, SMR drive
   'USING_SCRIPT_SKEW_TIME'      : (0),
}

# Zone based transfer test - Read
prm_598_r={
   'test_num'        : 598,
   'prm_name'        : "prm_598_r",
   'spc_id'          :  2,
   "timeout"         : 30000,
   "CTRL_WORD1"      : (0x0000), # Read w/ cache
   "STARTING_ZONE"   : (0),
   "ENDING_ZONE"     : {
      'ATTRIBUTE'    : 'numZones',
      'DEFAULT'      : 180,
      24             : (23),
      31             : (30),
      60             : (59),
      120            : (119),
      150            : (149),
      180            : (179),
      },
   "NUM_SERP"        : (8),
   "REV_TIME"        : 0x2B66,   # Default RPM at 5400
   "BLKS_PER_XFR"    : (0xFF),   # 255 LBAs per xfer
   "HEAD_TO_TEST"    : (0), # default = 0, SMR drive
   "BAND_OFFSET"     : (0), # default = 0, SMR drive
   'USING_SCRIPT_SKEW_TIME'      : (0),
}

## -------------------------------------------------  T621  -------------------------------
## ATI test
prm_621 = {
   'test_num'              : 621,
   'prm_name'              : 'prm_621',
   'CTRL_WORD1'            : 0x0018,
   'CTRL_WORD2'            : 0x0002,
   'MAX_REC_ERRORS'        : 0x03FF,
   'MAX_NON_REC_ERRORS'    : 0x003F,
   'DISABLE_ECC_ON_THE_FLY': 1,
   'FREE_RETRY_CONTROL'    : 1,
   'HIDDEN_RETRY_CONTROL'  : 1,
   'RPT_HIDDEN_RETRY_CNTRL': 0,
   'TEST_HEAD'             : 0xFF,
   'SIDE_TRACK_RANGE'      : 1,
   'USR_MAX_CENTER_WRITES' : 1,
   'TEST_CYLINDER'         : (0x0, 0x61A8),
   'spc_id'                :  1,
   'timeout'               :  25200
}

## -------------------------------------------------  T638  -------------------------------
# Unlock Seagate Access
prm_638_Unlock_Seagate={
   'test_num'        : 638,
   'prm_name'        : 'prm_638_Unlock_Seagate',
   'timeout'         : 3600,
   'spc_id'          : 1,
   'DFB_WORD_0'      : 0xFFFF,   # DITS cmd ID (Unlock Diagnostics)
   'DFB_WORD_1'      : 0x0100,   # Rev ID
   'DFB_WORD_2'      : 0x9A32,   # Unlock Seagate Access Key LSW
   'DFB_WORD_3'      : 0x4F03,   # Unlock Seagate Access Key MSW
   'retryECList'     : [14061, 14029],
   'retryCount'      : 10,
   'retryMode'       : HARD_RESET_RETRY,
   }

# Set Clear format corupt condition
prm_638_ClrFmtCorupt={
   'test_num'        : 638,
   'prm_name'        : 'prm_638_ClrFmtCorupt',
   'timeout'         : 3600,
   'spc_id'          : 1,
   'DFB_WORD_0'      : 0x1301,   # DITS cmd ID (Set Clear Format Corrupt Condition)
   'DFB_WORD_1'      : 0x0100,   # Rev ID (Usually x0001)
   'DFB_WORD_2'      : 0x0100,   # LSB_bit_0: 0=Normal operation 1=Clear fmt corrupt
   'DFB_WORD_3'      : 0x0000,   #
   }

# Set Data scrubbing
prm_638_SetIA_0={
   'test_num'        : 638,
   'prm_name'        : 'prm_638_SetIA_0',
   'timeout'         : 3600,
   'spc_id'          : 1,
   'DFB_WORD_0'      : 0x0901,   # DITS cmd ID
   'DFB_WORD_1'      : 0x0100,   # Rev ID (Usually x0001)
   'DFB_WORD_2'      : 0x0000,   # LSB 0=disable 1=enable
   'DFB_WORD_3'      : 0x0000,
   }

# Sent servo command 2F (Temperature sensor measurement)
prm_638_ServoCmd_2F={
   'test_num'        : 638,
   'prm_name'        : 'prm_638_ServoCmd_2F',
   'timeout'         : 3600,
   'spc_id'          : 1,
   'DFB_WORD_0'      : 0x4F01,  # DITS cmd ID
   'DFB_WORD_1'      : 0x0100,  # Rev ID (Usually x0001)
   'DFB_WORD_2'      : 0x0000,  # LSB_bit_0=CO, bit_1=O, bit_2=F, bit_3=T,bit_4=D.  MSB = rsvd.
   'DFB_WORD_3'      : 0x2F00,  # Servo cmd (16 bits, little endian)
   }

# Get temperature
prm_638_GetTemp = {
   'test_num'                 : 638,
   'prm_name'                 : 'prm_638_GetTemp',
   'timeout'                  :  3600,
   'spc_id'                   : 1,
   'DFB_WORD_0'               : 0x5001,         # DITS cmd ID
   'DFB_WORD_1'               : 0x0100,         # Rev ID (Usually x0001)
   'DFB_WORD_2'               : 0x0000,         # LSB: 0=Converted, Temp 1=Temp, ref V 2=Temp V.  MSB: Reserve
   'DFB_WORD_3'               : 0x0000,
}

# Set Data scrubbing
prm_638_SetDatScub_0={
   'test_num'        : 638,
   'prm_name'        : 'prm_638_SetDatScub_0',
   'timeout'         : 3600,
   'spc_id'          : 1,
   'DFB_WORD_0'      : 0x0101,  # DITS cmd ID
   'DFB_WORD_1'      : 0x0100,  # Rev ID (Usually x0001)
   'DFB_WORD_2'      : 0x0000,  # LSB 0=disable 1=enable
   'DFB_WORD_3'      : 0x0000,
   }

# Set ECC control (0x0103)
prm_638_Set_ECC_8 = {
   'test_num'                 : 638,
   'prm_name'                 : 'prm_638_Set_ECC_8',
   'timeout'                  : 3600,
   'spc_id'                   : 1,
   'DFB_WORD_0'               : 0x0301,         # DITS cmd ID
   'DFB_WORD_1'               : 0x0100,         # Rev ID (Usually x0001)
   'DFB_WORD_2'               : 0x0800,         # LSB T-Level
   'DFB_WORD_3'               : 0x0100,         # Enable ECC override (x0001=enable, x0000=disable)
}

# Set ECC control (0x0103)
prm_638_Set_ECC_10 = {
   'test_num'                 : 638,
   'prm_name'                 : 'prm_638_Set_ECC_10',
   'timeout'                  :  3600,
   'spc_id'                   : 1,
   'DFB_WORD_0'               : 0x0301,         # DITS cmd ID
   'DFB_WORD_1'               : 0x0100,         # Rev ID (Usually x0001)
   'DFB_WORD_2'               : 0x0A00,         # LSB T-Level
   'DFB_WORD_3'               : 0x0100,         # Enable ECC override (x0001=enable, x0000=disable)
}

# Set full retries
prm_638_SetFullRetry = {
   'test_num'                 : 638,
   'prm_name'                 : 'prm_638_SetFullRetry',
   'timeout'                  :  3600,
   'spc_id'                   : 1,
   'DFB_WORD_0'               : 0x6501,         # DITS cmd ID
   'DFB_WORD_1'               : 0x0100,         # Rev ID (Usually x0001)
   'DFB_WORD_2'               : 0x0000,         # LSB bit 0: FullRetryFlag, 1 - enable, 0 - disable.
   'DFB_WORD_3'               : 0x0000,         # Rsvd
}

prm_blueNunScanAuto = {
   'ERROR_COUNT_LIMIT'     : 25,
   'cmd_per_sample'        : 4,
   'Samples Per Reg'       : 125,
   'BlueNun Log TMO'       : 1,
   'BlueNun Group Retries' : 1,
   'BlueNun Max Retries'   : 50000,
   'BlueNun Auto Multi'    : 12,
   'sect_cnt'              : 256,
}

prm_AccessTime = {
   'spc_id'                : 1,
   'Overhead_Limit'        : 5,
   'Single_Limit'          : 10,
   'Random_Limit'          : 15,
   'FullStroke_Limit'      : 30,
   'Seek_Type'             : 28,
   'Loop_Count'            : 1000,
   'Overhead_LBA'          : 1000,
   'Toss_Limit'            : 10000,
   }

prm_DRamSettings = {
   'spc_id'                : 1,
   'StartLBA'              : 0,
   'MidLBA'                : 100000,
   'EndLBA'                : 2000000,
   'StepCount'             : 256,
   'SectorCount'           : 256,
   'StampFlag'             : 1,
   'CompareFlag'           : 1,
   }

prm_DRamFiles = [
   'WALKZERO.PAT',
   'WALKONE.PAT',
   ]

# Sync Critical Event Type with GIO
prm_CriticalEvents = {
   'CE_0x2' : 0,  # BAD_SMART_EVENT
   'CE_0x3' : 0,  # MARKED_PENDING
   'CE_0x7' : 0,  # REALLOCATION_FAILED
   'CE_0xB' : 0,  # WRITE_BBM_REALLOCATION_FAILED
}

prm_FIN2_CriticalEvents = {
   'CE_0x21'               : 20,
   'CE_0x22'               : 20,
   'CE_0x23'               : 20,
   'CE_0x43'               : 20,
   }

prm_AUD2_CriticalEvents = {
   'CE_0x21'                  : 10,
   'CE_0x22'                  : 10,
   'CE_0x23'                  : 10,
   'CE_0x43'                  : 10,
}

prm_MQM2_CriticalEvents = {
   'CE_0x21'                  : 5,
   'CE_0x22'                  : 5,
   'CE_0x23'                  : 5,
   'CE_0x43'                  : 5,
}

prm_DefectListLimits = {
   'ALT_LIST'                 : 0,
   'GLIST'                    : 0,
   'RLIST'                    : 0
}

prm_SmartDefectList = {
   'PLIST_LIMIT' : 20,
   #'PLIST_LIMIT' : 0,
   'GLIST_LIMIT' : 0,
   'ALT_LIST'    : 0,
}

smartResetParams = {
   'options'                  : [1],
   'initFastFlushMediaCache'  : 1,
   'timeout'                  : 120,
   'retries'                  : 2,
   }

smartUDSResetParams = {
   'options'                  : [0x25],
   'initFastFlushMediaCache'  : 1,
   'timeout'                  : 120,
   'retries'                  : 2,
   }

clearDOSParams = {
   'displayBefore'         : 1,
   'clearDOS'              : 1,
   'clearLength'           : 12416,
   'verifyAfter'           : 1,
   'maxRetries'            : 2,
   }

if testSwitch.FE_0385813_385431_Enable_MSFT_CactusScreen: 
   prm_microsoft = {
      'LOOP'      : 15,
      'TEST_LBAS' : 0x32000,  # 100MB
      # Read operation parameters. None means no limit is set.
      'READ_OD_LOW_LIMIT'  : None,       # should be 60
      'READ_OD_UP_LIMIT'   : None,
      'READ_ID_LOW_LIMIT'  : None,       # should be 40
      'READ_ID_UP_LIMIT'   : None,
      # Write operation parameters. None means no limit is set.
      'WRITE_OD_LOW_LIMIT' : None,       # should be 60
      'WRITE_OD_UP_LIMIT'  : None,
      'WRITE_ID_LOW_LIMIT' : None,       # should be 40
      'WRITE_ID_UP_LIMIT'  : None,
   }

   prm_microsoft_Cactus = {
      'OD_LOOP'      : 40,
      'OD_StartLBA'  : 780,   #in GB
      'ID_LOOP'      : 40,
      'ID_StartLBA'  : 820,   #in GB
      
      'TEST_LBAS' : 0x2FAF1,  # 100MB
      # Read operation parameters. None means no limit is set.
      'READ_OD_LOW_LIMIT'  : None,       # should be 75
      'READ_OD_UP_LIMIT'   : None,
      'READ_ID_LOW_LIMIT'  : None,       # should be 75
      'READ_ID_UP_LIMIT'   : None,
      # Write operation parameters. None means no limit is set.
      'WRITE_OD_LOW_LIMIT' : None,       # should be 75
      'WRITE_OD_UP_LIMIT'  : None,
      'WRITE_ID_LOW_LIMIT' : None,       # should be 75
      'WRITE_ID_UP_LIMIT'  : None,
   }

else:
   prm_microsoft = {
      'LOOP'      : 15,
      'TEST_LBAS' : 0x32000,  # 100MB
      # Read operation parameters. None means no limit is set.
      'READ_OD_LOW_LIMIT'  : 90,
      'READ_OD_UP_LIMIT'   : None,
      'READ_ID_LOW_LIMIT'  : 40,
      'READ_ID_UP_LIMIT'   : None,
      # Write operation parameters. None means no limit is set.
      'WRITE_OD_LOW_LIMIT' : 90,
      'WRITE_OD_UP_LIMIT'  : None,
      'WRITE_ID_LOW_LIMIT' : 40,
      'WRITE_ID_UP_LIMIT'  : None,
   }

##------------------------------Apple ATI-----------------------------------
prm_508_Buff= {
   'test_num'               : 508,
   'prm_name'               : "prm_508_Buff",
   'CTRL_WORD1'             : (0x0000),
   'BYTE_OFFSET'            : (0,0),
   'BUFFER_LENGTH'          : (0,1280),
   'PATTERN_TYPE'           : (0),                # 0 = fixed pattern
   'DATA_PATTERN0'          : (0x0000, 0x0000),
   'DATA_PATTERN1'          : (0x0000, 0x0000),
#   'BYTE_PATTERN_LENGTH'    : (32),
}
prm_510_ATIRD= {
    "test_num"   : 510,
    "prm_name"   : "prm_510_ATIRD",
    'spc_id'     : 1,
    "CTRL_WORD1" : (0x10),
    "CTRL_WORD2" : (0x2080),
    "STARTING_LBA" : (0,0,0,0),
    "TOTAL_BLKS_TO_XFR" : (0x0000,0x1000),
    "BLKS_PER_XFR" : (0x100),
    "timeout" : 252000,
}
prm_510_ATIWT= {
    "test_num"   : 510,
    "prm_name"   : "prm_510_ATIWT",
    'spc_id'     : 1,
    "CTRL_WORD1" : (0x20),
    "CTRL_WORD2" : (0x2080),
    "STARTING_LBA" : (0,0,0,0),
    "TOTAL_BLKS_TO_XFR" : (0x061A,0x8000),
    "BLKS_PER_XFR" : (0x800),
    "DATA_PATTERN0" : (0x0000, 0x0000),
    "timeout" : 252000,
}
##---------------------- HP Integration Simulation Test ------------------------
prm_HP_INTG_SIM = {
   # Test module to run. All available modules are OS_CREATION, RP_CREATION,
   # RP_RESTORATION, BURN_IN_TEST, and READ_SCAN.
   'TEST_TO_RUN'  : ['OS_CREATION',
                     'RP_CREATION',
                     'RP_RESTORATION',
                     'BURN_IN_TEST',
                     'READ_SCAN',],
}
##------------------------- Write/Read SMART (WrRdSmt) -------------------------
prm_WrRdSmt = {
   'W_PTRN'          : "65e2",         # Defined write pattern
   'SECTOR_COUNT'    : 256,            # Sector count for Write/Read command
   'START_LBA'       : None,           # Start LBA for Write/Read command
                                       # None means start from LBA 0
   'END_LBA'         : None,           # End LBA for Write/Read command
                                       # None means start from Maximum LBA
   'V_LIST_SP_RETRY' : 3,              # VList serial port retry
   # Seagate SMART Attributes checking dictionary
   'lCAIDS' :  {
                  'ID'  : 'WRRDSMT',
                  # ATTR_RAW contains array of attributes to be checked against
                  # SMART Raw Data. Attribute to be checked contains:
                  #  - Attribute number
                  #  - Operator (represent expected criteria)
                  #  - Expected value
                  #    This could be number or string. For string, THRESHOLD
                  #    word is used as replacement for SMART Threshold only,
                  #    please don't use it for other means.
                  #  - Byte length (in Bytes)
                  'ATTR_RAW':
                     [
                        (  5, '<=',    0, 2),   # G-List checking
                        (197, '<=',    0, 4),   # G-List checking
                        (198, '<=',    0, 4),   # G-List checking
                        (187, '<=',    0, 2),
                     ],
                  # ATTR_N contains array of attributes to be checked against
                  # SMART Nominal value. Attribute to be checked contains:
                  #  - Attribute number
                  #  - Operator (represent expected criteria)
                  #  - Expected value
                  #    This could be number or string. For string, THRESHOLD
                  #    word is used as replacement for SMART Threshold only,
                  #    please don't use it for other means.
                  'ATTR_N':
                     [
                        (  1, '>', "math.ceil(1.5 * THRESHOLD)"),
                        (  3, '>', "math.ceil(1.5 * THRESHOLD)"),
                        (  7, '>', "math.ceil(1.5 * THRESHOLD)"),
                        ( 10, '>', "THRESHOLD"),
                        (184, '>', "THRESHOLD"),
                        (188, '>', "math.ceil(1.5 * THRESHOLD)"),
                        (189, '>', "math.ceil(1.5 * THRESHOLD)"),
                        (191, '>', "math.ceil(1.5 * THRESHOLD)"),
                        (192, '>', "math.ceil(1.5 * THRESHOLD)"),
                        (193, '>', "math.ceil(1.5 * THRESHOLD)"),
                        (195, '>', "math.ceil(1.5 * THRESHOLD)"),
                        (199, '>', "math.ceil(1.5 * THRESHOLD)"),
                     ],
                  # WORDOFFSET contains array of offset to be checked against
                  # Vendor Information. Attribute to be checked contains:
                  #  - Start offset
                  #  - End offset (increased by one)
                  #    For example the offset is 410:411, please put 412
                  #    instead
                  #  - Operator (represent expected criteria)
                  #  - Expected value (only number)
                  'WORDOFFSET':
                     [
                        (410, 412,  '==',   0),    # G-List checking
                        (412, 414,  '==',   0),    # G-List checking
                     ],
               },
}

##------------------------------- Apple LTOS -----------------------------------
prm_AppleLTOS = {
   'IFACE_CMD_TO'    : 5,              # Interface command timeout in second
   'W_PTRN'          : None,           # Defined write pattern. None means
                                       # zero pattern.
   'LBA_RANGE'       : 0x61A80,        # Range LBA to be tested
   'RNDM_BLK_SZ'     : [1, 256],       # Start and end of random block size.
                                       # Maximum is 256 blocks.
   'TTL_LOOP'        : 150,            # Total loop for both write and read
}

##------------------------- Delay Random Read Test -----------------------------
prm_DLY_RNDM_RD = {
   'TTL_LOOP'        : 50,             # Total loop for entire test
   'IFACE_CMD_TO'    : 5,              # Interface command timeout in second
   'DLY'             : 600,            # Delay between power on and random read
                                       # in second
}

##------------------------------- HP WRC Test ----------------------------------
prm_HP_WRC = {
   'TTL_LOOP'     : 2,                 # Total loop for entire test
   'IFACE_CMD_TO' : 5,                 # Interface command timeout in second
   'ZONE_1'       : [0x5A00, 0x6300],  # Start and end LBA at Zone 1 in LBA
   'ZONE_2'       : [0x8A00, 0xA300],  # Start and end LBA at Zone 2 in LBA
   'TX_LEN'       : [0x1, 0x80],       # Random transfer length in block
   'BLK_SKIP'     : [0x180, 0x280],    # Random block skip in block
   'DLY'          : [1, 8],            # Delay between different data patterns
                                       # in second
   'DATA_PTRN'    : '0106',            # Fixed data pattern in hexadecimal
                                       # string
}

##--------------------------- NEC Performance Test -----------------------------
prm_NEC_PFM = {
   'TX_BLK'       : 1,                 # Read transfer block
   'TTL_READ'     : 9000,              # Total read in times
   'TIME_OUT'     : 220000,            # Time out to perform all test in
                                       # milliseconds
}

##------------ HP Store Test Suite - DST Suite - Self Test Interrupt -----------
prm_HP_Store_STINT = {
   'IFACE_CTO'       : 5,              # Interface command timeout in second
   'IDLE_IMM_CTO'    : 10,             # Idle immediate command timeout in
                                       # second
   'DLY'             : 0.5,            # Delay between commands in second
   'Mode4LBALen'     : 0x02545AB8      # LBA length for self-test Mode4
}

##------------------------------- Acer S3 Test ---------------------------------
prm_Acer_S3 = {
   'TTL_TEST_TIME': 30,                # Total test time in minutes
   'LBA_RANGE_80' : [ 19531250,        # Randomly, 80% of Reads/Writes will
                     156250000],       # fall into this LBA range
                                       # [start LBA, end LBA]. The rest (20%)
                                       # will fall into LBA 0 to maximum LBA.
                                       #  19531250 sectors * 512 B/sector = ~10GB
                                       # 156250000 sectors * 512 B/sector = ~80GB
}

##------------------------------- Acer S4 Test ---------------------------------
prm_Acer_S4 = {
   'TTL_TEST_TIME': 30,                # Total test time in minutes
   'LBA_RANGE_80' : [ 19531250,        # Randomly, 80% of Reads/Writes will
                     156250000],       # fall into this LBA range
                                       # [start LBA, end LBA]. The rest (20%)
                                       # will fall into LBA 0 to maximum LBA.
                                       #  19531250 sectors * 512 B/sector = ~10GB
                                       # 156250000 sectors * 512 B/sector = ~80GB
}

##------------------------------- Acer S5 Test ---------------------------------
prm_Acer_S5 = {
   'TTL_TEST_TIME': 30,                # Total test time in minutes
   'LBA_RANGE_80' : [ 19531250,        # Randomly, 80% of Reads/Writes will
                     156250000],       # fall into this LBA range
                                       # [start LBA, end LBA]. The rest (20%)
                                       # will fall into LBA 0 to maximum LBA.
                                       #  19531250 sectors * 512 B/sector = ~10GB
                                       # 156250000 sectors * 512 B/sector = ~80GB
}

##------------------------- HP DST Performance Test ----------------------------
prm_HP_DST_PFM = {
   'IFACE_CMD_TO' : 5,                 # Interface command timeout in second
}

##------------------------------- Go Flex TV -----------------------------------
prm_GO_FLEX_TV = {
   'TTL_MAIN_LOOP'      : 5000,        # Total main loop (times)
   'TTL_PLAY_LOOP'      : 5000,        # Total play loop (times)
   'TTL_FORWARD_LOOP'   : 1000,        # Total forward loop (times)
   'FORWARD_LENGTH'     : 5000,        # Forward length (LBAs)
   'TTL_REVERSE_LOOP'   : 1000,        # Total reverse loop (times)
   'TTL_SCAN_LOOP'      : 6000,        # Total scan loop (times)
   'SCAN_HALF_LENGTH'   : 2000,        # Scan half length (LBAs)
}

prm_538={
  "test_num"   : 538,
  "prm_name"   : "prm_538",
  "PARAMETER_0": 0x2000,
  "FEATURES"   : 0xD0,
  "COMMAND"    : 0xB0,
  "LBA_MID"    : 0x4F,
  "LBA_LOW"    : 0x00,
  "LBA_HIGH"   : 0xC2,
  "SECTOR_COUNT": 0,
  "timeout"    : 2600
}

RWDictGlobal = []

# check P000_DEFECTIVE_PBAS dumped by CDisplay_G_list
CHK_DEFECTIVE_PBAS = {
   'NUMBER_OF_PBAS'  : 0,
}

##------------------------- Verify SMART IOEDC -------------------------
prm_SmtIOEDC = {
   # Seagate SMART Attributes checking dictionary
   'lCAIDS' :  {
                  'ID'      :'WRRDSMT',
                  'ATTR_RAW':
                   [
                      (184, '<=',    0, 6),       # SMART Attribute 184 Raw Data = IOEDC reported
                   ],
               },
}

prm_600_long = {
   'test_num'              : 600,
   'prm_name'              : 'prm_600_long',
   'timeout'               : 60*90*numHeads,
   'spc_id'                : 1,
   'TEST_FUNCTION'         : 2,     # 1=short DST 2=long DST
   'STATUS_CHECK_DELAY'    : 60,
}

prm_600_short = {
   'test_num'              : 600,
   'prm_name'              : 'prm_600_short',
   'timeout'               : 3600,
   'spc_id'                : 1,
   'TEST_FUNCTION'         : 1,     # 1=short DST 2=long DST
   'STATUS_CHECK_DELAY'    : 10,
}

#SDOD Timeout value in Seconds
SDOD = {'SerialTimeout':10}

min_ber_spec_oem = {
   'ATTRIBUTE' : 'WA_0309963_504266_504_LDPC_PARAM',
   'DEFAULT'   : 0,
   0           : -2.0,
   1           : -1.8,
}
min_ber_spec_sbs = {
   'ATTRIBUTE' : 'WA_0309963_504266_504_LDPC_PARAM',
   'DEFAULT'   : 0,
   0           : -2.0,
   1           : -1.8,
}

cold_min_ber_spec_oem = {
   'ATTRIBUTE' : 'WA_0309963_504266_504_LDPC_PARAM',
   'DEFAULT'   : 0,
   0           : -2.0,
   1           : -1.8,
}
cold_min_ber_spec_sbs = {
   'ATTRIBUTE' : 'WA_0309963_504266_504_LDPC_PARAM',
   'DEFAULT'   : 0,
   0           : -2.0,
   1           : -1.8,
}

max_delta_ber_spec_oem = 0.29
max_delta_ber_spec_sbs = 0.29

MIN_SOVA_SQZ_WRT   = {
   'ATTRIBUTE'    : 'FE_0261598_504159_SCREEN_OTF',
   'DEFAULT'      : 0,
   0  : {
         'ATTRIBUTE' : ('FE_0302539_348429_P_ENABLE_VBAR_OC2','WA_0309963_504266_504_LDPC_PARAM'),
         'DEFAULT'   : (0,0),
         (0,0)       : -18, #define Spec for screening SQZ write in fnc2
         (0,1)       : -17, #0.1 lower than spec when turn on Markov
         (1,0)       : -17, #0.1 lower than spec when turn on OC2 push
         (1,1)       : -16, #0.2 lower than spec when turn on OC2 push + Markov
   },
   1  : -10,
}
NUM_UDE            = 40   #define min number of UDE of the zone/hd

prm_averageQBER = {
    'AverageQBERLimit': {'EQUATION' : "abs(TP.min_ber_spec_sbs)"},
}

prm_quickSER_250_RHO = {
   'test_num'           : 250,
   'prm_name'           : 'prm_quickSMER_250',
   'spc_id'             : 1,
   'timeout'            : {
     'ATTRIBUTE'      : 'numZones',
     'DEFAULT'        : 60,
     60               : 1800*numHeads, # extra pad- shud take 5 min/zone for ea pass
     120              : 1800*numHeads,
     150              : 1800*numHeads,
     180              : 1800*numHeads,
     },

   'TEST_ZONES'         : {
     'ATTRIBUTE'      : 'numZones',
     'DEFAULT'        : 17,
     17               : range(17),
     24               : range(24),
     31               : range(31),
     60               : range(60),
     120              : range(120),
     150              : range(150),
     180              : range(180)
     },
   'TEST_HEAD'          : 0xFF,
   'WR_DATA'            : (0x00),# 1 byte for data pattern if writing first
   'ZONE_POSITION'      : ZONE_POS,
   'MAX_ERR_RATE'       : -90,
   'MODES'              : ['BITERR'], #,'SYMBOL'],
   'CWORD1'             : 0x09C1,    # Use sector error rate at sampling mode
   'CWORD2'             : (0x0000,), # Use BIE with non converging for equation
   'NUM_TRACKS_PER_ZONE' : 10,
   'RETRIES'            : 50,       # supported from SF3 CL86949
   'SKIP_TRACK'            : {
      'ATTRIBUTE'    : 'FE_0245014_470992_ZONE_MASK_BANK_SUPPORT',
      'DEFAULT'      : 0,
      0              : 200,
      1              : 20, #Zone 94, 110, 179 may have less than 200 tracks, so skip_track cannot remain at 200.
   },
   'TLEVEL'             : 0,
   'PERCENT_LIMIT'      : 0xFF, # turn on the consideration for non_converging code word
   'MAX_ITERATION'      : MaxIteration, # org is 24
   'SER_num_failing_zones_rtry': 2, #max allowed failing zones for T250 retries
   'checkDeltaBER_num_failing_zones': 0, #num allowed failing zones to pass checkDeltaBER

   'max_diff'           : {         # (2nd BER - 1st BER). the difference is +ve value  when BER degraded
     "ATTRIBUTE"       : "CAPACITY_CUS",
     "DEFAULT"         : "1000G_OEM1B",
     "1000G_OEM1B"     : max_delta_ber_spec_oem,
     "1000G_STD"       : max_delta_ber_spec_sbs,
     "750G_OEM1B"      : max_delta_ber_spec_oem,
     "750G_STD"        : max_delta_ber_spec_sbs,
     },

   'MINIMUM'            : {
     "ATTRIBUTE"       : "CAPACITY_CUS",
     "DEFAULT"         : "1000G_OEM1B",
     "1000G_OEM1B"     : {'EQUATION' : "int(TP.min_ber_spec_oem * 10)"},
     "1000G_STD"       : {'EQUATION' : "int(TP.min_ber_spec_sbs * 10)"},
     "750G_OEM1B"      : {'EQUATION' : "int(TP.min_ber_spec_oem * 10)"},
     "750G_STD"        : {'EQUATION' : "int(TP.min_ber_spec_sbs * 10)"},
     },

   'SER_raw_BER_limit'  :{
     "ATTRIBUTE"  : "nextOper",
     "DEFAULT"    : "FNC2",
     "FNC2"       : {
         "ATTRIBUTE"       : "CAPACITY_CUS",
         "DEFAULT"         : "1000G_OEM1B",
         "1000G_OEM1B"     : min_ber_spec_oem,
         "1000G_STD"       : min_ber_spec_sbs,
         "750G_OEM1B"      : min_ber_spec_oem,
         "750G_STD"        : min_ber_spec_sbs,
         },
     "CRT2"       : {
         "ATTRIBUTE"       : "CAPACITY_CUS",
         "DEFAULT"         : "1000G_OEM1B",
         "1000G_OEM1B"     : cold_min_ber_spec_oem,
         "1000G_STD"       : cold_min_ber_spec_sbs,
         "750G_OEM1B"      : cold_min_ber_spec_oem,
         "750G_STD"        : cold_min_ber_spec_sbs,
         },
    },
}


prm_quickSER_250_TDK =  prm_quickSER_250_RHO.copy()

prm_quickSER_250_2A_RHO = prm_quickSER_250_RHO.copy()
prm_quickSER_250_2A_TDK = prm_quickSER_250_TDK.copy()

prm_quickSER_250_TCC_RHO = prm_quickSER_250_RHO.copy()
prm_quickSER_250_TCC_TDK = prm_quickSER_250_TDK.copy()

prm_quickSER_250_TCC_2_RHO = prm_quickSER_250_RHO.copy()
prm_quickSER_250_TCC_2_TDK = prm_quickSER_250_TDK.copy()


prm_quickSER_250_2A_RHO.update({'spc_id'   : 14,})
prm_quickSER_250_2A_TDK.update({'spc_id'   : 14,})

prm_quickSER_250_TCC_RHO.update({'spc_id'  : {
         'ATTRIBUTE'          : 'nextState',
         'DEFAULT'            : 'READ_SCRN2C',
         'READ_SCRN2C'        : 15,
         'READ_SCRN2C_SMR'    : 17,
         'READ_SCRN2D'        : 18,
},})
prm_quickSER_250_TCC_RHO.update({'CWORD2'  : (0x0005,)}) # 0x4 for BIE with equation 0x1 for temperature compensation
prm_quickSER_250_TCC_TDK.update({'spc_id'  : {
         'ATTRIBUTE'          : 'nextState',
         'DEFAULT'            : 'READ_SCRN2C',
         'READ_SCRN2C'        : 15,
         'READ_SCRN2C_SMR'    : 17,
         'READ_SCRN2D'        : 18,
},})
prm_quickSER_250_TCC_TDK.update({'CWORD2'  : (0x0005,)}) # 0x4 for BIE with equation 0x1 for temperature compensation

prm_quickSER_250_TCC_2_RHO.update({'spc_id'  : 16,})
prm_quickSER_250_TCC_2_RHO.update({'CWORD2'  : (0x0005,)}) # 0x4 for BIE with equation 0x1 for temperature compensation
prm_quickSER_250_TCC_2_TDK.update({'spc_id'  : 16,})
prm_quickSER_250_TCC_2_TDK.update({'CWORD2'  : (0x0005,)}) # 0x4 for BIE with equation 0x1 for temperature compensation


prm_quickSER_250 = {
      'ATTRIBUTE':'HGA_SUPPLIER',
      'DEFAULT': 'RHO',
      'TDK': prm_quickSER_250_TDK ,
      'RHO': prm_quickSER_250_RHO ,
   }
prm_quickSER_250_2A = {
      'ATTRIBUTE':'HGA_SUPPLIER',
      'DEFAULT': 'RHO',
      'TDK': prm_quickSER_250_2A_TDK ,
      'RHO': prm_quickSER_250_2A_RHO ,
   }

prm_quickSER_250_TCC = {
      'ATTRIBUTE':'HGA_SUPPLIER',
      'DEFAULT': 'RHO',
      'TDK': prm_quickSER_250_TCC_TDK ,
      'RHO': prm_quickSER_250_TCC_RHO ,
   }
prm_quickSER_250_TCC_2  = {
      'ATTRIBUTE':'HGA_SUPPLIER',
      'DEFAULT': 'RHO',
      'TDK': prm_quickSER_250_TCC_2_TDK ,
      'RHO': prm_quickSER_250_TCC_2_RHO ,
   }

SkipWriteScrn_spec = {
   'TEST_ZONE'             : [1,2],
   'Clr_Backoff_BER_limit' : {
      "ATTRIBUTE"       : "CAPACITY_CUS",
      "DEFAULT"         : "1000G_OEM1B",
      "1000G_OEM1B"     : 2.0,
      "1000G_STD"       : 1.9,
      "750G_OEM1B"      : 2.0,
      "750G_STD"        : 1.9,
   },
   'max_diff'           : {  #Clr Backoff BER minus Clr on target BER
      "ATTRIBUTE"       : "CAPACITY_CUS",
      "DEFAULT"         : "1000G_OEM1B",
      "1000G_OEM1B"     : 0,
      "1000G_STD"       : -0.2,
      "750G_OEM1B"      : 0,
      "750G_STD"        : -0.2,
   },
}

prm_Cold_Write_252 = {
   'test_num'           : 252,
   'prm_name'           : 'prm_Cold_Write_252',
   'spc_id'             : 1,
   'timeout'            : 3600,
   'CWORD1'             : 0x0000,
   'TLEVEL'             : 24,
   'ZONE_POSITION'      : 100,
   'TEST_HEAD'          : 0x00FF,
   'ZONE_MASK' : {
               'ATTRIBUTE'    : 'numZones',
               'DEFAULT'      : 31,
               24             : (0, 0),
               31             : (4096, 33025), #zone 0,8,15,28
               60             : (0x4000, 0x8001), #zone 0,15,30,57
               },
   'ZONE_MASK_EXT' : {
               'ATTRIBUTE'    : 'numZones',
               'DEFAULT'      : 31,
               24             : (0, 0),
               31             : (0, 0),
               60             : (0x0200, 0x0000), #zone 0,15,30,57
               },
   'HEAD_RANGE'         : 0x00FF,
}

prm_auditTest_T252 = {
   'timeout'            : 7200,
   'ZONE_POSITION'      : 198,
   'TLEVEL'             : 32,
   }

ClrSettling_SpinDownDelay = 30*60*1 # in unit of secs
ClrSettling_ColdBER_prm_250 = {
    'test_num'              : 250,
    'prm_name'              : 'ColdBER_prm_250',
    'RETRIES'               : 50,
    'MAX_ITERATION'         : MaxIteration,  ## org is 24
    'ZONE_POSITION'         : 198,
    'spc_id'                : 1998,
    'MAX_ERR_RATE'          : -90,
    'TEST_HEAD'             : 255,
    'NUM_TRACKS_PER_ZONE'   : 10,
    'SKIP_TRACK'            : {
      'ATTRIBUTE'    : 'FE_0245014_470992_ZONE_MASK_BANK_SUPPORT',
      'DEFAULT'      : 0,
      0              : 200,
      1              : 20, #Zone 94, 110, 179 may have less than 200 tracks, so skip_track cannot remain at 200.
    },
    'TLEVEL'                : 0,
    'MINIMUM'               : -17,
    'timeout'               : 120.0,
    'ZONE_MASK'             : (0L, 1),
    'WR_DATA'               : 0,
    'CWORD1'                : 0x1C3,
    'CWORD2'                : {
      'ATTRIBUTE'             : 'nextOper',
      'DEFAULT'               : 'default',
      'default'               : 0x1, #tcc on
      'FNC2'                  : 0, #tcc off
      'CRT2'                  : 1, #tcc off
    },
}


ClrSettling_HotBER_prm_250 = ClrSettling_ColdBER_prm_250.copy()
ClrSettling_HotBER_prm_250.update({'prm_name' : 'HotBER_prm_250',})
ClrSettling_HotBER_prm_250.update({'spc_id' : 1999,})

prm_Head_Recovery_baking_MrrChk_072 = {
   'test_num'           : 72,
   'prm_name'           : 'prm_Head_Recovery_baking_MrrChk_072',
   'spc_id'             : 1,
   'timeout'            : 7200,
   'CWORD1'             : { 
      'ATTRIBUTE'    : 'FE_0322846_403980_P_DUAL_HEATER_N_BIAS_TSHR',
      'DEFAULT'      : 0,
      0              : 0x0004,
      1              : 0x0002, # BAKING_PLUS_CHECKING_MRR mode 0x0002, BAKING_ONLY 0x0001
   },
   'CWORD2'          : { 
      'ATTRIBUTE'    : 'FE_0322846_403980_P_DUAL_HEATER_N_BIAS_TSHR',
      'DEFAULT'      : 0,
      0              : 0x0003, # BAKING_PLUS_CHECKING_MRR mode #0x0002,# BAKING_ONLY #
      1              : 0, # 
   },
   'HEATER'             : {
      'ATTRIBUTE'    : 'FE_0322846_403980_P_DUAL_HEATER_N_BIAS_TSHR',
      'DEFAULT'      : 0,
      0              : (40, 0), # Reader heater only
      1              : (0, 40), # (Writer heater, Reader heater)
   },
   'TEST_HEAD'          : 0x00,   #default as head 0 , will update in the script
   'DELAY_TIME'         : 10000, #milliseconds
   'MRBIAS_SAMPLES'     : {
      'ATTRIBUTE'    : 'FE_0322846_403980_P_DUAL_HEATER_N_BIAS_TSHR',
      'DEFAULT'      : 0,
      0              : 0,
      1              : 136, # Reader voltage bias
   },
}

# HeaterPower = (reader power_to_apply, repeat_no_of_times, no_of_times_to_check_to_pass, writer power to apply, voltage bias to apply)
if testSwitch.ENABLE_THERMAL_SHOCK_RECOVERY_V3: 
   prm_Head_Recovery_Heater_Power = {
         'EC_Trigger'      : [11126, 10560],
         'HeaterPower'     : {
            'ATTRIBUTE'    : 'FE_0322846_403980_P_DUAL_HEATER_N_BIAS_TSHR',
            'DEFAULT'      : 0,
            0              : [(40,1,0), (50,3,0), (50,1,1), ],
            1              : [(40,1,0,0,136), (50,3,0,0,136), (50,1,1,0,136), ],
         },
   }

RdScrn2_Retry_with_TSR = {
   'EC_Trigger'      : [10632],  # error codes in READ_SCRN2 to trigger TSR
   'Extra_T250'      : 2,        # no of additionaly T250 to run
}

##### ## OAR_ELT parameter ########################################################################################
prm_OAR_ErrRate_250 = {
   'base': {
      'test_num'           : 250,
      'prm_name'           : 'prm_OAR_ErrRate_250',
      'spc_id'             : 21,
      'timeout'            : 500*numHeads, # extra pad- shud take 5 min/zone for ea pass
      'ZONE_MASK'          : { 'EQUATION'        : " (0, sum([1 << zn for zn in TP.OAR_TEST_ZONE]))"},
      'TEST_HEAD'          : 0xFF,
      'WR_DATA'            : (0x00),# 1 byte for data pattern if writing first
      'ZONE_POSITION'      : 0,
      'MAX_ERR_RATE'       : -80,
      "CWORD1"             : 0x0181, # CWORD1 setting applied in level 3 code
      "CWORD2"             : 0x0002, # CWORD1 setting applied in level 3 code
      'NUM_TRACKS_PER_ZONE' : 40,
      'RETRIES'            : 50,       # supported from SF3 CL86949
      'SKIP_TRACK'         : 200,      # supported from SF3 CL101463
      'MINIMUM'            : 8, #Minimum BER spec delta BER is 0.8
      'TLEVEL'             : 0,
      'MAX_ITERATION'      : MaxIteration,  # org is 0x705iteration used to measure the sector error rate
   },
   'differential' : 2.0,
   'minimum'      : -0.5,
}
## Criteria For Delta OAR ELT
num_region_pertrack_oar  = 20
## Update OAR Spec for SMR program
if testSwitch.SMR:
   max_delta_oar_WTF        = 300 #150
   max_delta_oar            = 300 #80
else:
   max_delta_oar_WTF        = 150
   max_delta_oar            = 80

oar_fault_count_limit    = 8000 #2 #5
delta_FSOW_limit         = 8000 #60
FirstSec_FSOW_limit      = 8000 #170

## Criteria For MAX OAR ELT
num_region_pertrack_oar_iter    = 60
max_delta_oar_iter              = 8000 #200#90
true_oar_fault_count_limit_iter = 8000 #5  # Decide if True OAR or not by requiring more tracks with high ELT
oar_fault_count_limit_iter      = 8000 #1  # Decide if OAR level is failing, requires only one track to fail
#max_bie_iter                   = 235
iteration_limit = 100
max_bie_iter_WTF = 8000 #150
max_bie_iter = 190
SEG_BER_NUM_TRACKS_PER_ZONE = 30
SegSQZBER_MeasureZone = {        # eg. for Segmented Squeeze BER measure zone, 0+MC+[(8 to 148)/5], ZONE MUST in ASCENDING order
   'ATTRIBUTE': 'FE_0385234_356688_P_MULTI_ID_UMP',
   'DEFAULT'  : 0,
   0 : {'EQUATION': "sorted([0] + TP.MC_ZONE + TP.baseVbarTestZones[self.dut.numZones][:-1])",},
   1 : {'EQUATION': "sorted([0] + TP.MC_ZONE + TP.baseSMRZoneBeforeUMP)",},
}

SegBER_MeasureZone = {        # eg. for Segmented BER measure zone, UMP+SPARE, ZONE MUST in ASCENDING order
   'EQUATION': "sorted(list(set(TP.UMP_ZONE[self.dut.numZones])))",
}
prm_EraseAfterWrite_vgas_234 = {
   'test_num'                 : 234,
   'prm_name'                 : 'prm_EraseAfterWrite_vgas_234',
   'spc_id'                   : 1,
   'timeout'                  : 3600,
   'CWORD1'                   : 0x01,
   'CWORD2'                   : 0x01,
   'NBR_ZONES'                : 0x01,
   'REVS'                     : 10,
   'NBR_CYLS'                 : 20,
   'TARGET_TRK_WRITES'        : 10000,
   'WEDGE_NUM'                : 0,
}

prm_EraseAfterWrite_ber_234 = {
   'test_num'              : 234,
   'prm_name'              : 'prm_EraseAfterWrite_ber_234',
   'spc_id'                : 1,
   'timeout'               : 3600,
   'CWORD1'                : 0x0002,
   'CWORD2'                : 0x0004,
   'HEAD_RANGE'            : 0x00FF,
   'TARGET_TRK_WRITES'     : 1000,
   'DEGAUSS_OFF_ERR_LIM'   : 50,
   'DEGAUSS_ON_ERR_LIM'    : 50,
   'TLEVEL'                : 1,
   'BITS_TO_READ'          : 80,
   'ZONE'                  : 0,
   'ZONE_POSITION'         : 100,
   }

prm_EraseAfterWrite_bie_234 = {
   'test_num'              : 234,
   'prm_name'              : 'prm_EraseAfterWrite_bie_234',
   'spc_id'                : 1,
   'timeout'               : 600 * 60 * numHeads,
   'CWORD1'                : 0x0002,
   'CWORD2'                : 0x0004,
   'HEAD_RANGE'            : 0x00FF,
   'TARGET_TRK_WRITES'     : 50000,
   'LIMIT32'               : (0x000F, 0x4240),  # 1000000d
   'DEGAUSS_OFF_ERR_LIM'   : 50,
   'DEGAUSS_ON_ERR_LIM'    : 50,
   'TLEVEL'                : 1,
   'BITS_TO_READ'          : 70,
   'ZONE'                  : 0,
   'ZONE_POSITION'         : 100,
   'LIMIT'                 : 16,
   }

prm_Erase_afterWrite_234_YBP = {
   'test_num'           : 234,
   'prm_name'           : 'prm_Erase_afterWrite_234',
   'spc_id'             : 1,
   'timeout'            : 3600,
   #'retryECList'        : [10476],
   #'retryCount'         : 3,
   #'retryMode'          : POWER_CYCLE_RETRY,
   'TEST_MODE'          : 0x0002,  # EAW BER2 mode
   'CWORD2'             : 0x000C,  # Test w Degauss ON followed by OFF , 0x000C Degauss on only
   'HEAD_RANGE'         : 0x00FF,
   'REVS'               : 100,
   'SECTOR_SIZE'           : {
         "ATTRIBUTE"   : "CAPACITY_PN",
         "DEFAULT"     : "500G",
         "1000G"     : 17,
         "750G"      : 14,
         "500G"      : 17,
         "320G"      : 14,
         "640G"      : 20,
          },
   'TARGET_TRK_WRITES'  : 10000,
   'DELAY_TIME'         : 200,
   'DEGAUSS_OFF_ERR_LIM': 60,
   'DEGAUSS_ON_ERR_LIM' : 5,
   'TLEVEL'             : 0x0205,
   'BITS_TO_READ'       : 80,
   'ZONE'               : 0,
   'ZONE_POSITION'      : 100,
   #'testZones'          : [1,15,29],   # Test OD, MD & ID
   'testZones'          : { # Test OD, MD & ID
                          'ATTRIBUTE':'numZones',
                          31: [1,15,29],
                          60: [1,30,59],
                          },
   'testRegs'           : [0],      #[0] means no changing of preamp regs, org=[0,0x39]
}

prm_Erase_afterWrite_234 = prm_Erase_afterWrite_234_YBP

prm_Erase_afterWrite_234_2 = prm_Erase_afterWrite_234
prm_Erase_afterWrite_234_2['DEGAUSS_ON_ERR_LIM'] = 30

prm_EraseAfterWrite_240 = {
      'test_num'                : 240,
      'prm_name'                : 'prm_EraseAfterWrite_240',
      'spc_id'                  : 1,
      'timeout'                 : 1800 * numHeads,
      'PRE_WRITES'              : 1,
      'ZONE_POSITION'           : ZONE_POS,
      'CWORD2'                  : {
                                    'ATTRIBUTE' : 'FE_0315237_504266_T240_DISABLE_SKIP_TRACK',
                                    'DEFAULT'   : 0,
                                    0 : 0x8013, # 0x8017,   # bit 5 = T240_DEGAUSS_ON_DISABLE
                                    1 : 0x8012, # It can disable skipping as we don't enable ON/OFF Degauss feature
                                 },
      'ZONE'                    : 1,
      'DEGAUSS_OFF_ERR_LIM'     : 60,
      'BITS_TO_READ'            : 90,
      'TLEVEL'                  : MaxIteration,
      'INTERVAL_SIZE'           : 60,
      'DEGAUSS_ON_ERR_LIM'      : 60,
      'NUM_SAMPLES'             : 5,
      'HEAD_RANGE'              : 0xFFFF,
      'DELTA_LIMIT'             : 100,
      'DELTA_LIMIT_SER'         : 400,
      'DEGAUSS_OFF_ERR_LIM_SER' : 60,
      'DEGAUSS_ON_ERR_LIM_SER'  : 60,
      'LIMIT32'                 : (0x000F,0x4240)
      }
############## STRONG WRITE SCREEN START ##############################
##'STRONG_WRT_SCREEN'  : ['SerialTest',        'CStrong_write_screen', {'pass':'EWAC_TEST',     'fail':'FAIL_PROC'}, []],
strong_wrt_r_squared = 0.5
strong_wrt_slope = 0.4
prm_Strong_Write_Screen_1 = {
    'test_num':251,
    'SQZ_OFFSET': (0,),
    'BIT_MASK': (0, 0x7ff),
    'RESULTS_RETURNED': (23,),
    'REG_TO_OPT2': (3, 3, 15, 1),
    'REG_TO_OPT1': (2, 6, 6, 1),
    'BIT_MASK_EXT': (0, 7),
    'TRACK_STEP_SIZE': (20,),
    'ZONE_POSITION': (198,),
    'TARGET_TRK_WRITES': (1,),
    'timeout': 60000,
    'SET_OCLIM': 1249,
    'REG_TO_OPT1_EXT': (0x8000, 0, 0x14C2),
    'REG_TO_OPT2_EXT': (0x8000, 0, 0x14C2),
    'NUM_READS': (10,),
    'NUM_SQZ_WRITES': (200,),
    'CWORD2': (0x104,),
    'CWORD1': (74,),
    'timeout': 600,
    'spc_id': 111
    }

prm_Strong_Write_Screen_2 = prm_Strong_Write_Screen_1.copy()
prm_Strong_Write_Screen_3 = prm_Strong_Write_Screen_1.copy()
prm_Strong_Write_Screen_4 = prm_Strong_Write_Screen_1.copy()
prm_Strong_Write_Screen_5 = prm_Strong_Write_Screen_1.copy()
prm_Strong_Write_Screen_6 = prm_Strong_Write_Screen_1.copy()
prm_Strong_Write_Screen_7 = prm_Strong_Write_Screen_1.copy()
prm_Strong_Write_Screen_8 = prm_Strong_Write_Screen_1.copy()
prm_Strong_Write_Screen_9 = prm_Strong_Write_Screen_1.copy()

prm_Strong_Write_Screen_2.update( {
'REG_TO_OPT1': (2, 7, 7, 1),
})
prm_Strong_Write_Screen_3.update( {
'REG_TO_OPT1': (2, 8, 8, 1),
})
prm_Strong_Write_Screen_4.update( {
'REG_TO_OPT1': (2, 10, 10, 1),
})
prm_Strong_Write_Screen_5.update( {
'REG_TO_OPT1': (2, 11, 11, 1),
})
prm_Strong_Write_Screen_6.update( {
'REG_TO_OPT1': (2, 12, 12, 1),
})
prm_Strong_Write_Screen_7.update( {
'REG_TO_OPT1': (2, 13, 13, 1),
})
prm_Strong_Write_Screen_8.update( {
'REG_TO_OPT1': (2, 14, 14, 1),
})
prm_Strong_Write_Screen_9.update( {
'REG_TO_OPT1': (2, 15, 15, 1),
})
############### STRONG WRITE SCREEN END ###############################
##############HEAD SCRN TEST START#######################################
##############HEAD SCRN TEST START########################################
prm_Head_Asymmetry_CSM_196 = {
   'test_num'              : 196,
   'prm_name'              : 'prm_Head_Asymmetry_CSM_196',
   'spc_id'                : 1,
   'timeout'               : 1800 * numHeads,
   'CWORD1'             : 0x1D,
   'RETRY_LIMIT' : 3,
   'ZONE_POSITION': 198,
}
prm_Servo_AGC_Mode_103 = {
   'test_num'              : 103,
   'prm_name'              : 'prm_Servo_AGC_Mode_103',
   'spc_id'                : 1,
   'timeout'               : 1800 * numHeads,
   'CWORD1'             : 0x31c0,
   'RETRY_LIMIT'        : (2,),
   'WEDGE_NUM'          : 10408,
   'LOOP_CNT'           : 200,
   'STD_DEV_LIMIT'      : 900,
   'DELTA_LIMIT'        : 50,
   'SLOPE_LIMIT'        : 1000,
   'TIMEOUT_TIMER_SEC_32_BITS': (0, 3240),
   'RW_MODE'            : (32),
   'ZONE_POSITION': 198,
}

Head_Scrn_Zone_Mask = {
   'ZONE_MASK'     : {
      'ATTRIBUTE'  : 'numZones',
      'DEFAULT'    : 31,
      24           : (0xff, 0xffff),
      31           : (0x7fff,0x0),
      60           : (0, 0),
      },
   'ZONE_MASK_EXT' : {
      'ATTRIBUTE'  : 'numZones',
      'DEFAULT'    : 31,
      24           : (0, 0),
      31           : (0, 0),
      60           : (0x0FFF,0xE000), #zone 45-59 only (test time reduction)
      },
}
prm_Head_Scrn_395 = {
   'test_num'      : 395,
   'prm_name'      : 'prm_Head_Scrn_395',
   'spc_id'        : 1,
   'timeout'       : 3600,
   'CWORD1'        : {
      'ATTRIBUTE'  : 'numZones',
      'DEFAULT'    : 31,
      24           : 0x0015,
      31           : 0x0015,
      60           : 0x0055, #Enable Bit 6 of CWORD1 to copy test values from even to odd zones, when alternate zones are run.
      },
   'HEAD_RANGE'    : 0x00FF,
   'ZONE_POSITION' : 198,
   'THRESHOLD'     : 5,       # ADC treshold low limit
   'THRESHOLD2'    : 30,      # ADC treshold up limit
   'OFFSET'        : 0,       # 1150
   'SLOPE_LIMIT'   : 180,     # 90
   'MINIMUM'       : 5,       # flaw scan threshold low limit
   'MAXIMUM'       : 50,      # flaw scan threshold up limit
   'DELTA_LIMIT'   : 0,       # 2
   'SCALED_VAL'    : 1000,    # To scale vgar. Default is 1000.
   'RETRY_LIMIT'   : 4,
   'FREQUENCY'     : 1000,
   'TARGET_COEF'   : -80,
}
#prm_Head_Scrn_395.update(Head_Scrn_Zone_Mask)

prm_ET_Instability_VGA_195_base = {
   'test_num'              : 195,
   'prm_name'              : 'prm_ET_Instability_VGA_195',
   'spc_id'                : 1,
   'timeout'               : 1800 * numHeads,
   'CWORD1'                : 0x8002,
   #'CSM_THRESHOLD'           : (0,40000,),
   'NUM_READS'              : 1,
   'MAX_BLOCK_COUNT'        : (0, 10), # Number of wedges to read at each read offset in the track offset loop.
   'DELTA_LIMIT'            : (32000,),
   'RANGE2'                : (0, 57, 3, 0),
   'AC_ERASE'               : (),
   'THRESHOLD'              : (25,),

   'RETRY_LIMIT'             : 5,
   'ZONE_POSITION': 198,
   'THRESHOLD2'   : 0,
   'NORM_STDEV_BY_AVG'     :  20,
   ##'MAX_CSM_AVG'           : 20,
   'NUM_FAIL_ZONE_LIMIT'   : 3,
   'AVG_NORM_STDEV_BY_HEAD': {
      "ATTRIBUTE"  : "nextOper",
      "DEFAULT"    : "PRE2",
      "PRE2"       : {
            "ATTRIBUTE"   : "CAPACITY_PN",
            "DEFAULT"     : "500G",
            "1000G" : 10,
            "750G"  : 15,
            "500G"  : 10,
            "320G"  : 15,
            },
      "FNC2"       : {
            "ATTRIBUTE"   : "CAPACITY_PN",
            "DEFAULT"     : "500G",
            "1000G" : 12,
            "750G"  : 15,
            "500G"  : 12,
            "320G"  : 15,
            },
      },
}
prm_ET_Instability_VGA_195_base.update(Head_Scrn_Zone_Mask)

prm_ET_Instability_VGA_195_openspec = prm_ET_Instability_VGA_195_base.copy()
prm_ET_Instability_VGA_195_openspec.update( {
'AVG_NORM_STDEV_BY_HEAD': 200,
'DELTA_LIMIT'            : (0xffff),
'NORM_STDEV_BY_AVG'     : 200,
'NUM_FAIL_ZONE_LIMIT'   : 32,
})

prm_ET_Instability_VGA_195_DAM = prm_ET_Instability_VGA_195_base.copy()
prm_ET_Instability_VGA_195_DAM.update({   # to capture digital AMing Instability
   'NORM_STDEV_BY_AVG'     : 9,
   'NUM_FAIL_ZONE_LIMIT'   : 1,
   'NUM_READS'             : 10,
})

prm_ET_Instability_VGA_195 = {
"ATTRIBUTE"  : "nextOper",
"DEFAULT"    : "PRE2",
"PRE2"       : {
   "ATTRIBUTE"   : "CAPACITY_CUS",
   "DEFAULT"     : "1000G_OEM1B",
   "1000G_OEM1B" : prm_ET_Instability_VGA_195_base,
   "750G_STD"    : prm_ET_Instability_VGA_195_openspec,
   },
"FNC2"       : prm_ET_Instability_VGA_195_base,
}

prm_ET_Instability_VMM_195 = {
   'test_num'              : 195,
   'prm_name'              : 'prm_ET_Instability_VMM_195',
   'spc_id'                : 1,
   'timeout'               : 1800 * numHeads,
   'CWORD1'                : 0x8001,
   'CSM_THRESHOLD'          : (20,0),
   'DELTA_LIMIT'            : (65000,),
   'ZONE_POSITION': 198,
   }

prm_Asymmetry_251 = {
      'test_num'           : 251,
      'prm_name'           : 'prm_Asymmetry_251',
      'timeout'            : 50000*numHeads,
      'spc_id'             : 1,
      'BIT_MASK'           : {
                          'ATTRIBUTE':'numZones',
                          24: (0xff, 0xffff),
                          31: (0x4811,0x0012), #zone 1,4,16,20,27,30
                          60: (0x8000,0x0082), #zone 1,7,31,39,53,39
                          },
      'BIT_MASK_EXT'       : {
                          'ATTRIBUTE':'numZones',
                          24: (0, 0),
                          31: (0,0),
                          60: (0x0820,0x0080), #zone 1,7,31,39,53,39
                          },
      'CWORD1'             : 0x5A,
      'ZONE_POSITION'      : 198,
      'RESULTS_RETURNED'   :  0x3,
      'SET_OCLIM'          :  819,
      'TLEVEL'             :  0x0705,
      'NUM_READS'          :  0x2,
      'GAIN'               :  0,                  #freeze FIR if  REG_TO_OPT5_EXT first word=1
      'GAIN2'              : 102,
      'ADAPTIVES'          :  6,               #default value for writeprecom 001 101
      'THRESHOLD2'         :  1000,               #1000*1000 for the criteria when selecting track,default 100*1000

      'REG_TO_OPT1'        : (0x15f, 0, 0, 1),      # Dibit
      'REG_TO_OPT1_EXT'    : (0, 0, 1 ),     # Dibit
}


prm_Asymmetry_251_spec_OEM = 0.4 # 40% head asymmetry
prm_Asymmetry_251_spec_SBS = 0.5
prm_Asymmetry_251_spec = {
     "ATTRIBUTE"     : "CAPACITY_CUS",
     "DEFAULT"       : "1000G_OEM1B",
     "1000G_OEM1B"   : prm_Asymmetry_251_spec_OEM,
     "1000G_STD"     : prm_Asymmetry_251_spec_SBS,
     "750G_OEM1B"    : prm_Asymmetry_251_spec_OEM,
     "750G_STD"      : prm_Asymmetry_251_spec_SBS,
}
##############HEAD SCRN TEST END#########################################
##############HEAD SCRN TEST END#########################################

prm_Instability_195 = {
   'test_num'              : 195,
   'prm_name'              : 'prm_Instability_195',
   'spc_id'                : 1,
   'timeout'               : 1800 * numHeads,
   'CWORD1'                : 0x0000,
   'ZONE'                  : 15,
   'ZONE_POSITION'         : 100,
   'READ_OFFSET'           : 192,
   'PRE_WRITES'            : 1,
   'PATTERN_MASK'          : 0x003C,
   'THRESHOLD'             : 0x3348,
   'THRESHOLD2'            : 0x5978,
   'FREQUENCY'             : 64,
   'LIMIT'                 : 0xFFFF,
   'RETRY_INCR'            : 32,
   'SET_OCLIM'             : 0x04E1,
   'RETRY_LIMIT'           : 3,
   'FAIL_SAFE'             : (),
   'failSafe'              : 1         # Allows fail-safe for all failure modes
   }

prm_Instability_195_2 = {
   'test_num'              : 195,
   'prm_name'              : 'prm_Instability_195_2',
   'spc_id'                : 2,
   'timeout'               : 1800 * numHeads,
   'CWORD1'                : 0x0000,
   'ZONE'                  : 0x000F,
   'ZONE_POSITION'         : 100,
   'READ_OFFSET'           : 48,
   'PRE_WRITES'            : 1,
   'PATTERN_MASK'          : 0x003C,
   'THRESHOLD'             : 0x0A0D,
   'THRESHOLD2'            : 0x1013,
   'FREQUENCY'             : 7,
   'LIMIT'                 : 0xFFFF,
   'RETRY_INCR'            : 16,
   'SET_OCLIM'             : 0x04E1,
   'RETRY_LIMIT'           : 3,
   'FAIL_SAFE'             : (),
   'failSafe'              : 1         # Allows fail-safe for all failure modes
   }

prm_Instability_195_3 = {
   'test_num'              : 195,
   'prm_name'              : 'prm_Instability_195_3',
   'spc_id'                : 3,
   'timeout'               : 1800 * numHeads,
   'CWORD1'                : 0x0000,
   'ZONE'                  : 0x0000,
   'ZONE_POSITION'         : 100,
   'READ_OFFSET'           : 48,
   'PRE_WRITES'            : 1,
   'PATTERN_MASK'          : 0x00C0,
   'THRESHOLD'             : 0x0508,
   'THRESHOLD2'            : 0x0B0E,
   'FREQUENCY'             : 46,
   'LIMIT'                 : 0xFFFF,
   'RETRY_INCR'            : 16,
   'SET_OCLIM'             : 0x04E1,
   'RETRY_LIMIT'           : 3,
   'FAIL_SAFE'             : (),
   'failSafe'              : 1         # Allows fail-safe for all failure modes
   }

prm_Instability_195_3_1 = {
   'test_num'              : 195,
   'prm_name'              : 'prm_Instability_195_3_1',
   'spc_id'                : 3,
   'timeout'               : 1800 * numHeads,
   'CWORD1'                : 0x0000,
   'ZONE'                  : 8,
   'ZONE_POSITION'         : 100,
   'READ_OFFSET'           : 48,
   'PRE_WRITES'            : 1,
   'PATTERN_MASK'          : 0x00C0,
   'THRESHOLD'             : 0x0508,
   'THRESHOLD2'            : 0x0B0E,
   'FREQUENCY'             : 34,
   'LIMIT'                 : 0xFFFF,
   'RETRY_INCR'            : 16,
   'SET_OCLIM'             : 0x04E1,
   'RETRY_LIMIT'           : 3,
   'FAIL_SAFE'             : (),
   'failSafe'              : 1         # Allows fail-safe for all failure modes
   }

prm_Instability_195_3_2 = {
   'test_num'              : 195,
   'prm_name'              : 'prm_Instability_195_3_2',
   'spc_id'                : 3,
   'timeout'               : 1800 * numHeads,
   'CWORD1'                : 0x0000,
   'ZONE'                  : 16,
   'ZONE_POSITION'         : 100,
   'READ_OFFSET'           : 48,
   'PRE_WRITES'            : 1,
   'PATTERN_MASK'          : 0x00C0,
   'THRESHOLD'             : 0x0508,
   'THRESHOLD2'            : 0x0B0E,
   'FREQUENCY'             : 23,
   'LIMIT'                 : 0xFFFF,
   'RETRY_INCR'            : 16,
   'SET_OCLIM'             : 0x04E1,
   'RETRY_LIMIT'           : 3,
   'FAIL_SAFE'             : (),
   'failSafe'              : 1         # Allows fail-safe for all failure modes
   }

Instability_TA_199 ={
   'test_num'          : 199,
   'prm_name'          : 'Instability_TA_199',
   'spc_id'            : 1,
   'timeout'           : 1800 * numHeads,
   'READ_OFFSET'       : (0x0000),
   'PRE_WRITES'        : (0x0001),
   'ZONE_POSITION'     : (0x00C6),
   'ZONE'              : {
      'ATTRIBUTE':'FAST_2D_VBAR_UNVISITED_ZONE', #test time reduction for Vbar
      'DEFAULT': 0,
      0 : (0x0003),
      1 : {
         'ATTRIBUTE': 'FE_0274346_356688_ZONE_ALIGNMENT',
         'DEFAULT'  : 0,
         0 : (0x2), #shift to zone 2
         1 : (0x0),
      },
   },
   'HEAD_RANGE'        : (0x00FF),
   'THRESHOLD2'        : (0x2224), #34, 36
   'FREQUENCY'         : (52),
   'RETRY_INCR'        : (0x0010),
   'THRESHOLD'         : (0x1D20), #29, 32
   'SET_OCLIM'         : (819),
   'RETRY_LIMIT'       : (0x0010),
   'CWORD1'            : {
      'ATTRIBUTE'             : 'nextOper',
      'DEFAULT'               : 'default',
      'default'               : (0x0020),#set to 0x0020 if want to turn on NormalizeVGAR
      'FNC2'                  : (0x0020),#set to 0x0020 if want to turn on NormalizeVGAR
      'CRT2'                  : (0x8020),#set to 0x8020, tcc on
   },
   'PATTERN_MASK'      : (0x0001),
   'MVL_THRESH_LEVEL'  : (0x4e20, 0x2710, 0x0bb8, 0x07d0),
   'ZETA_4'            : (0x0000, 0x0019),
   'ZETA_1'            : (0x0000, 0x0050),
   'ZETA_3'            : (0x0000, 0x0023),
   'ZETA_2'            : (0x0000, 0x0050),
   'FAIL_SAFE'         : (),
   'failSafe'          : 1,
}

Instability_TA_199_2 ={
   'test_num'          : 199,
   'prm_name'          : 'Instability_TA_199_2',
   'spc_id'            : 2,
   'timeout'           : 1800 * numHeads,
   'READ_OFFSET'       : (0x0000),
   'PRE_WRITES'        : (0x0001),
   'ZONE_POSITION'     : (0x00C6),
   'ZONE'              : {
      'ATTRIBUTE':'FAST_2D_VBAR_UNVISITED_ZONE', #test time reduction for Vbar
      'DEFAULT': 0,
      0 : (0x0003),
      1 : {
         'ATTRIBUTE': 'FE_0274346_356688_ZONE_ALIGNMENT',
         'DEFAULT'  : 0,
         0 : (0x2), #shift to zone 2
         1 : (0x0),
      },
   },
   'HEAD_RANGE'        : (0x00FF),
   'THRESHOLD2'        : (0x2224), #34, 36
   'FREQUENCY'         : (13),
   'RETRY_INCR'        : (0x0010),
   'THRESHOLD'         : (0x1D20), #29, 32
   'SET_OCLIM'         : (819),
   'RETRY_LIMIT'       : (0x0010),
   'CWORD1'            : {
      'ATTRIBUTE'             : 'nextOper',
      'DEFAULT'               : 'default',
      'default'               : (0x0020),#set to 0x0020 if want to turn on NormalizeVGAR
      'FNC2'                  : (0x0020),#set to 0x0020 if want to turn on NormalizeVGAR
      'CRT2'                  : (0x8020),#set to 0x8020, tcc on
   },
   'PATTERN_MASK'      : (0x0001),
   'MVL_THRESH_LEVEL'  : (0x4e20, 0x2710, 0x0bb8, 0x07d0),
   'ZETA_4'            : (0x0000, 0x0019),
   'ZETA_1'            : (0x0000, 0x0050),
   'ZETA_3'            : (0x0000, 0x0023),
   'ZETA_2'            : (0x0000, 0x0050),
   'FAIL_SAFE'         : (),
   'failSafe'          : 1,
}

Instability_TA_199_3 ={
   'test_num'          : 199,
   'prm_name'          : 'Instability_TA_199_3',
   'spc_id'            : 3,
   'timeout'           : 1800 * numHeads,
   'READ_OFFSET'       : (0x0000),
   'PRE_WRITES'        : (0x0001),
   'ZONE_POSITION'     : (0x00C6),
   'ZONE'              : (0x0003),
   'HEAD_RANGE'        : (0x00FF),
   'THRESHOLD2'        : (0x2224), #34, 36
   'FREQUENCY'         : (75),
   'RETRY_INCR'        : (0x0010),
   'THRESHOLD'         : (0x1D20), #29, 32
   'SET_OCLIM'         : (819),
   'RETRY_LIMIT'       : (0x0010),
   'CWORD1'            : {
      'ATTRIBUTE'             : 'nextOper',
      'DEFAULT'               : 'default',
      'default'               : (0x0020),#set to 0x0020 if want to turn on NormalizeVGAR
      'FNC2'                  : (0x0020),#set to 0x0020 if want to turn on NormalizeVGAR
      'CRT2'                  : (0x8020),#set to 0x8020, tcc on
   },
   'PATTERN_MASK'      : (0x0001),
   'MVL_THRESH_LEVEL'  : (0x4e20, 0x2710, 0x0bb8, 0x07d0),
   'ZETA_4'            : (0x0000, 0x0019),
   'ZETA_1'            : (0x0000, 0x0050),
   'ZETA_3'            : (0x0000, 0x0023),
   'ZETA_2'            : (0x0000, 0x0050),
   'FAIL_SAFE'         : (),
   'failSafe'          : 1,
}

prm_Instability_297 = {
    'test_num'      : 297,
    'prm_name'      : 'Head Instability Test T297',
    'PATTERN_IDX'   : 0,
    'FAIL_SAFE'     : (),
    'ZONE'          : {
      'ATTRIBUTE': 'FE_0274346_356688_ZONE_ALIGNMENT',
      'DEFAULT'  : 0,
      0 : 4,
      1 : 0,
    },
    'NUM_READS'     : 10,
    'MAX_ERR_RATE'  : 2500,
    'spc_id'        : 20100,
    'TRGT_READS'    : 10000,
    'SET_OCLIM'     : 0,
    'HEAD_RANGE'    : 255,
    'timeout'       : 9000,
    'CWORD1'        : 0,  #0x2 # Set bit 1 of CWORD1 - This bit forces the test to use the adjustment value in the PERCENT_LIMIT input parameter.
    'PERCENT_LIMIT' : 0, # BPI adjustment to be made. The value is divided by 100 such that a value of 400 gives you a 4 percent BPI increase. 
                         # A value of 0 means the default BPI is used.
    'ZONE_POSITION' : (0x00C6),
}

Instability_PES_41 ={
  'test_num'              : 41,
  'prm_name'              : 'Instability_PES_41',
  'spc_id'                : 1,
  'timeout'               : 1800 * numHeads,
  'CWORD1'                : 0x0001,
  'REVS'                  : 10,
  'SEEK_TYPE'             : 21,
  'PERCENT_LIMIT'         : 200,
  'NUM_TRACKS_PER_ZONE'   : 3,
  'HEAD_RANGE'            : 0x00FF,
  }

T50T51RetryParams = {
'NUM_RETRIES' : 5,
}

prm_Encroachment_50 = {
   'base': {
      'test_num'                       : 50,
      'prm_name'                       : 'prm_Encroachment_50',
      'spc_id'                         : 1,
      'CWORD1'                         : 0xA0 | testSwitch.USE_ZERO_LATENCY_WRITE_IN_T50_T51,
      'timeout'                        : 3600,
      'ZONE_POSITION'                  : 100,
      'RETRY_COUNTER_MAX'              : 100,
      'RETRY_INCR'                     : 100,
      #'RDM_SEEK_BEFORE_WRT'            : 1,
      #'RDM_SEEK_RETRIES'               : 100,
      'BASELINE_CLEANUP_WRT_RETRY'     : 10,
      'CHANGE_SEEK_LENGTH_AND_RETRY'   : 2,
      'TLEVEL'                         : 30,
   },
   'ZONES'                             : {'EQUATION' : "[ min(TP.UMP_ZONE[self.dut.numZones]) ]"},
   'BAND_WRITES'                       : [500], #as dos kick in after 1000x wrt
}
############## HAMR Related Parameter ##########
## HAMR Related 
prm_051_ATI = {
    'test_num'                      : 51,
    'prm_name'                      : 'prm_051_ATI',
    'timeout'                       : 900, 
    'spc_id'                        : 500,
    'CHANGE_SEEK_LENGTH_AND_RETRY'  : 25, 
    'CENTER_TRACK_WRITES'           : 3, 
    'MAX_ERR_RATE'                  : 600, 
    'BASELINE_CLEANUP_WRT_RETRY'    : 25, 
    'TLEVEL'                        : 65535, 
    'BAND_SIZE'                     : 3, 
    'RETRY_INCR'                    : 5, 
    'ZONE'                          : 0, 
    'TEST_HEAD'                     : 0, 
    'RETRY_COUNTER_MAX'             : 100, 
    'CWORD1'                        : 208, 
    'ZONE_POSITION'                 : 198
}




prm_250_NoSqueeze = {
   'test_num'                 : 250,
   'prm_name'                 : 'prm_250_NoSqueeze',
   'timeout'                  : 900, 
   'RETRIES'                  : 50,                
   'MAX_ERR_RATE'             : -60,               
   #'SQZ_OFFSET'               : 3,             # sqt %       
   #'NUM_SQZ_WRITES'           : 1,             # Number of write          
   'SKIP_TRACK'               : 20,                
   'TEST_HEAD'                : (0,),                
   'WR_DATA'                  : 0, 
   'PERCENT_LIMIT'            : 255, 
   'ZONE_POSITION'            : 198, 
   'ZONE_MASK'                : (0L,1), 
   'NUM_TRACKS_PER_ZONE'      : 10, 
   'spc_id'                   : 1, 
   'TLEVEL'                   : 0, 
   'MINIMUM'                  : -10, 
   'ZONE_MASK_BANK'           : 0, 
   'ZONE_MASK_EXT'            : (0L, 0L), 
   'MAX_ITERATION'            : 65535, 
   'CWORD2'                   : 0x1801, 
   'CWORD1'                   : 0x0183,         # 0x4000 is squeeze

}

prm_250_Squeeze = prm_250_NoSqueeze.copy()

prm_250_Squeeze.update({'prm_name'      : 'prm_250_Squeeze',
                        'CWORD1'        : 0x4183,             # 0x4000 is squeeze
                        'SQZ_OFFSET'    : 3,                  # squeeze percentage  
                        'NUM_SQZ_WRITES': 1,                  # number of write
                      })

prm_172_RdClr = {
   'test_num'                 : 172,
   'prm_name'                 : 'prm_172_RdClr',
   'timeout'                  : 1200,
   'CWORD1'                   : (0x0005,),   # Read AFH Clearance
}
prm_172_PreampAdpt = {
   'test_num'                 : 172,
   'prm_name'                 : 'prm_172_PreampAdpt',
   'timeout'                  : 1200,
   'CWORD1'                   : (4),   # Read RAP


}
prm_172_HamrPreampTable = {
   'test_num'                 : 172,
   'prm_name'                 : 'prm_172_HamrPreampTable',
   'timeout'                  : 1200,
   'CWORD1'                   : (62,),


}
prm_172_HamrWorkingTable = {
   'test_num'                 : 172,
   'prm_name'                 : 'prm_172_HamrWorkingTable',
   'timeout'                  : 1200,
   'CWORD1'                    : (63,),
}

prm_172_display_AFH_target_clearance = {
   'test_num'          : 172,
   'prm_name'          : 'display_AFH_target_clearance_172',
   'timeout'           : 1800,
   'CWORD1'            : 5,       #outputs P172_AFH_DH_CLEARANCE
   'spc_id'            : 111,
}

prm_172_display_AFH_adapts_summary = {
   'test_num'          : 172,
   'prm_name'          : 'display_AFH_target_clearance_172',
   'timeout'           : 1800,
   'CWORD1'            : 52,       #outputs P172_AFH_ADAPTS_SUMMARY
   'spc_id'            : 111,
}


prm_178_WrtLsrCrnt = {
   'test_num'                 : 178,
   'prm_name'                 : 'prm_178_WrtLsrCrnt',
   'CWORD1'                   : (0x0200,),   # 0x2000 set will update working table only, clear will update both working table and RAP.
   'CWORD2'                   : (0,),  
   'CWORD3'                   : (0x0007,),   # 0x04=I_THRESH, 0x02=I_OP_RANGE, 0x01=I_OP
   'LASER'                    : (0,0,0),       # (Iop, IopRange, Ith)
}

prm_178_hamr_mode = {
   'test_num'                 : 178,
   'prm_name'                 : 'prm_178_hamr_mode',
   'CWORD1'                   : (0x0200,),   # 0x2000 set will update working table only, clear will update both working table and RAP.
   'CWORD2'                   : (0,),  
   'CWORD3'                   : (0x0010,),   # 
   'ZONE'                     : 0xff,
   'HEAD_RANGE'               : 0xff,
   'HAMR_MODE'                : 0,           # bit 1 enable or disable HAMR
}


prm_178_hamr_control = {
   'test_num'                 : 178,
   'prm_name'                 : 'prm_178_hamr_mode',
   'CWORD1'                   : (0x0200,),   # 0x2000 set will update working table only, clear will update both working table and RAP.
   'CWORD2'                   : (0,),  
   'CWORD3'                   : (0x0100,),   # 
   'ZONE'                     : 0xff,
   'HEAD_RANGE'               : 0xff,
   'HAMR_CONTROL'             : 0,           # bit 1 enable or disable HAMR
}

prm_178_hamr_pd_tgt_output = {
   'test_num'                 : 178,
   'prm_name'                 : 'prm_178_hamr_pd_tgt_output',
   'CWORD1'                   : (0x0200,),   # 0x2000 set will update working table only, clear will update both working table and RAP.
   'CWORD2'                   : (0,),  
   'CWORD3'                   : (0x0080,),   # 
   'ZONE'                     : 0xff,
   'HEAD_RANGE'               : 0xff,
   'TARGET_PD_OUTPUT'         : 0,           # bit 1 enable or disable HAMR
}

prm_178_display_hamr_setting = {
   'test_num'                 : 172,
   'prm_name'                 : 'prm_178_display_hamr_setting',
   'CWORD1'                   : 65,   
}

prm_178_set_MLCFCA_DBIATKAI = {
    'test_num'              : 178,
    'prm_name'              : 'prm_178_set_MLCFCA_DBIATKAI',
    'spc_id'                : 1,
    'timeout'               : 600,
    'CWORD1'                : 0x2200,
    'CWORD2'                : 0,
    'C_ARRAY1'              : [0, 37, 0, 0, 0, 0, 0, 0, 0, 0],
}

prm_172_RdZoneTable = {
   'test_num'               : 172,
   'prm_name'               : 'prm_172_RdZoneTable',
   'spc_id'                 : 1,
   'timeout'                : 1200,
   'CWORD1'                 : 2,

}

defaultLaserImax = {
    "ATTRIBUTE" : 'HGA_SUPPLIER',
    "DEFAULT" : 'RHO',
    "RHO" : 96
}

prm_172_RdRap = {
   'test_num'                 : 172,
   'prm_name'                 : 'prm_172_RdRap',
   'timeout'                  : 1200,
   'CWORD1'                   : (0x0009,),   # Read RAP

}
prm_172_RdSap = {
   'test_num'                 : 172,
   'prm_name'                 : 'prm_172_RdSap',
   'timeout'                  : 1200,
   'CWORD1'                   : (0x0000,),
}
prm_223_PhotoDetector = {
   'test_num'                 : 223,
   'prm_name'                 : 'prm_223_PhotoDetector',
   'CWORD1'                    : (0x00),
   'DEBUG_PRINT'                   : (0),
   'TEST_HEAD'                     :(0,0xFF),
   'TARGET_ITHRESH_CURRENT'              :  (0),
   #'ZONE_MASK'                    : (0x40000000,0,0,0),         # Zones 30
   'ZONE_POSITION'                    : (100),             # Percent into zone where testing occurs (0-200, 100 = 50%)
}
prm_223_LaserIthCal = {
   'test_num'                 : 223,
   'prm_name'                 : 'prm_223_LaserIthCal',
   'CWORD1'                    : (0x00),
   'DEBUG_PRINT'                   : (0),
   'TEST_HEAD'                     : (0,0xFF),
   'RANGE'               : (0,250),
   'PD_FILTER'                    : (0,100,3),
   'TARGET_ITHRESH_CURRENT'              : (0),
#   'HtrOvrd'                  :  (0),
}

#------------- Laser Calibration Parameters ------------------------------------
LaserCalParams    = {
   'ATTRIBUTE'    :  'HGA_SUPPLIER',
   'MAP'          : {'RHO'      : ['RHO','RHO_5400','RHO_5400_BOB8']},
   'BASE'         :  {
      'AplyCrvFit'           : True,         # Interpolate laser picks across the stroke
      'ErrCode'              : 10632,        # Default Error Code if laser cal fails
      'FailZnSpec'           : 3,            # Maximum number of user zones that can fail
      'MaxDacDlta'           : 25,           # Maximum IOP change in DACs
      'SqzPrcnt'             : 3,            # Percentage of track pitch to move both adjacent tracks in the direction of the test track
      'SqzWrtCnt'            : 1,            # Number of times to write adjacent tracks during squeezed BER measurment
      'AtiWrtCnt'            : 100,            # Number of times to write adjacent tracks during squeezed BER measurment
      'AtiSqzPrcnt'          : 0,            # Percentage of track pitch to move both adjacent tracks in the direction of the test track
      'ZnOrdr'               : [0, 10, 20, 40, 80, 100, 128,135, 149], #[84], #[16, 12, 20, 8, 24, 4, 28, 0, 33],  # Test zones
      'ZnPsn'                : 180,
   },
   'HWY'          :  {
      'FineIncr'             : 1,            # Number of DACs to increment during fine cal mode
      'CoarseIncr'           : 4,            # Number of DACs to increment until fine mode search range is found
      'ThreshIncr'           : 8,            # Number of DACs to increment until minimum threshold BER is met

      'BcktThrsh'            : 25,           # Percentage applied to baseline VGA signal to determine minimum bucket depth
      'DltaLmt'              : 7,            # Bucket Depth Delta value used to determine saturation
      'RtryCylIncr'          : 50,           # Number of cylinders to move on retry in T218
      'RtryLmt'              : 2,            # Number of retries for T218
      'VgaOfstRg'            : 1600,         # +/- servo offset from default jog table to search for VGA bucket
      'DeltaBerThrsh'        : 0.2,          # Maximum delta between non-squeezed and squeezed BER
      'LsrCurRg'             : (25,37),      # Starting laser current (mA), Maximum laser current (mA)
      'MaxBerSpec'           : -1.6,         # Zone fails if this BER spec is not met
      'MaxBerThrsh'          : -1.0,         # Maximum BER to be considered a valid measurement
   },
   'RHO'          :  {
      'FineIncr'             : 1,            # Number of DACs to increment during fine cal mode
      'CoarseIncr'           : 2,            # Number of DACs to increment until fine mode search range is found
      'ThreshIncr'           : 8,            # Number of DACs to increment until minimum threshold BER is met

      'BcktThrsh'            : 17,           # Percentage applied to baseline VGA signal to determine minimum bucket depth
      'DltaLmt'              : 10,           # Bucket Depth Delta value used to determine saturation
      'RtryCylIncr'          : 50,           # Number of cylinders to move on retry in T218
      'RtryLmt'              : 2,            # Number of retries for T218
      'VgaOfstRg'            : 1200,         # +/- servo offset from default jog table to search for VGA bucket

      'DeltaBerThrsh'        : 0.2,          # Maximum delta between non-squeezed and squeezed BER
      'DfltLsrThrsh'         : 17.6,         # Default laser threshold current (mA) to use if PDV cal fails.
      'LsrCurRg'             : (25,37),      # Starting laser current (mA), Maximum laser current (mA)
      'MaxBerSpec'           : -1.6,         # Zone fails if this BER spec is not met
      'MaxBerThrsh'          : -1.0,         # Maximum BER to be considered a valid measurement
   },
   'TDK'          :  {
      'FineIncr'             : 1,            # Number of DACs to increment during fine cal mode
      'CoarseIncr'           : 2,            # Number of DACs to increment until fine mode search range is found
      'ThreshIncr'           : 8,            # Number of DACs to increment until minimum threshold BER is met

      'BcktThrsh'            : 25,           # Percentage applied to baseline VGA signal to determine minimum bucket depth
      'DltaLmt'              : 7,            # Bucket Depth Delta value used to determine saturation
      'RtryCylIncr'          : 50,           # Number of cylinders to move on retry in T218
      'RtryLmt'              : 2,            # Number of retries for T218
      'VgaOfstRg'            : 900,          # +/- servo offset from default jog table to search for VGA bucket

      'DeltaBerThrsh'        : 0.2,          # Maximum delta between non-squeezed and squeezed BER
      'DfltLsrThrsh'         : 17.6,         # Default laser threshold current (mA) to use if PDV cal fails.
      'LsrCurRg'             : (25,37),      # Starting laser current (mA), Maximum laser current (mA)
      'MaxBerSpec'           : -1.6,         # Zone fails if this BER spec is not met
      'MaxBerThrsh'          : -1.0,         # Maximum BER to be considered a valid measurement
   },
}


prm_218_TA_LaserInit = {
       'ATTRIBUTE' : 'HGA_SUPPLIER',
       'DEFAULT'   : 'RHO',
       'RHO'      : {
          'test_num'                 : 218,
          'prm_name'                 : 'prm_218_TA_LaserInit',
          'timeout'                  : 7200,
          'CWORD1'                   : (0x0011,),       # bit 0 - update RAP - default(0), bit 1 - HAMR health check, bit 2 - Collect VGA data only, bit 3 - Calibrate iThresh value
          'DEBUG_PRINT'              : (0x00,),         # bit 0 - output debug minima info, bit 1 - output smoothed data to vga table, bit 2 - output debug data, bit 3 - Output ALL VGA sweeps
          'TARGET_CYLINDER'          : (0,25000),         # Cylinder to test
          'STD_DEV_LIMIT'            : (18,),           # Standard deviation in VGA signal used to determine when a track has been erased.
          'PERCENT_LIMIT'            : (40),            # Percentage applied to baseline VGA signal to determine minimum bucket depth 'ThrshLmt'
          'DELTA_LIMIT'                  : (7),             # Bucket Depth Delta value used to determine saturation - default(0)
          'SET_OCLIM'                    : (819),           # Oclim offset - default(0)
          'SERVO_OFFSET_RANGE'                       : (850,1800),     # +/- Servo Offset Range (Read, Erase)
          'LASER_CURRENT_STEP_SIZE'           : (0x0401,),       # [MSB]Coarse iAdd Step size, [LSB]Fine iAdd Step size
          'MIN_DAC'                : (1,),            # Minimum working write heat DAC allowed during T218.
          'RANGE'               : (0,150,),   # Starting iAdd value, Maximum iAdd value
       },
   }
#-------------------------------------------------------------------------------
MinWrtHtClr = 0                            # 25C Min Write Heat Clearance Spec

LaserBiasParams   = {
   'ATTRIBUTE' : 'HGA_SUPPLIER',
   'RHO'          :  {
      'Fltr'                  : 3,                 # Default PD filter setting used for PD calibration
      'Gain'                  : 5,                 # Default PD gain setting used for PD calibration
      'Incr'                  : 15,                # Number of IOP DACs to sweep per T223 call
      'MaxCov'                : 0.05,              # Coefficient of Variation used to reject bad data points
      'MaxOutliers'           : 3,                 # Maximum number of outliers that can be removed from the data set
      'PdGainRg'              : (0, 7),            # Range of valid PD gain settings
      'PdTgtRg'               : (50.0, 150.0),     # Range of PDV values to target for PD gain calibration
      'ZnOrdr'                : [0, 40, 80, 110, 149], #[0, 16, 33, 50, 67], # Test zones
      'ZnPsn'                 : 100,               # Zone position to test
      'DfltLsrBias'           : 12.375,              # Default laser bias (turn on) current (in mA) to use if PD cal fails. This is the default inflection point in the PD curve.
      'StdDevDlta'            : 0.2,               # Change in largest std deviation used to detect inflection point.
      'TgtLdiRg'              : (9.5, 15.00),    # Laser current range (in mA) for valid bias current detection.
      'ThreshDacOfst'         : -10,
   },
}

if testSwitch.HAMR_LBC_ENABLED:
   LaserBiasParams['RHO'].update({'ThreshDacOfst'  : 6})
   

prm_011_LbcFilter = {
   'test_num'                 : 11,
   'prm_name'                 : 'prm_011_LbcFilter',
   'timeout'                  : 1200,
   'CWORD1'                   : 0x0400,
   'spc_id'                   : 1,
   #'TstMode'                  : (10,),
   'ACCESS_TYPE'              : (3,),
   'MASK_VALUE'               : (0xFFFF,),
   'EXTENDED_MASK_VALUE'      : (0x00FF,),
   'SYM_OFFSET'               : (568,),
   'WR_DATA'                  : (0,),
   'EXTENDED_WR_DATA'         : (0,),
}

prm_011_LbcEnable = {
   'test_num'                 : 11,
   'prm_name'                 : 'prm_011_LbcEnable',
   'timeout'                  : 1200,
   'CWORD1'                   : 0x0400,
   'spc_id'                   : 1,
   #'TstMode'                  : (10,),
   'ACCESS_TYPE'              : (2,),
   'MASK_VALUE'               : (0xFF00,),
   'SYM_OFFSET'               : (568,),
   'WR_DATA'                  : (1,),
}

prm_011_RdLbcInfo = {
   'test_num'                 : 11,
   'prm_name'                 : 'prm_011_RdLbcInfo',
   'timeout'                  : 1200,
   'CWORD1'                   : 0x0200,
   'spc_id'                   : 1,
   #'TstMode'                  : (9,),
   'SYM_OFFSET'               : (568,),
   'ACCESS_TYPE'              : (1,),     # 1 byte at a time
   'NUM_LOCS'                 : (11,),    # 12 bytes total
}

prm_011_SetLbcKi = {
   'test_num'                 : 11,
   'prm_name'                 : 'prm_011_SetLbcKi',
   'timeout'                  : 1200,
   'CWORD1'                   : 0x0400,
   'TstMode'                  : (16,),
   'ACCESS_TYPE'             : (3,),        # 32-bit access mode
   'MASK_VALUE'               : (0x0000,),   # Modify all bits
   #########   Temporary   write SBM to fix #############
   'EXTENDED_MASK_VALUE'      : (0x0001,),   #  Per Oui Bit Mask is not required, Try setting bit 0 to prevent failure when all values = 0
   'Ofst'                     : (8,),        # Offset 8 bytes into servo symbol
   'SYM_OFFSET'               : (568,),
   'WR_DATA'                  : (0x0000,),   # Lower word of Ki bytes
   'EXTENDED_WR_DATA'         : (0x0000,),   # Upper word of Ki bytes
}

prm_011_RdHamrSvoDiag = {
   'test_num'                 : 11,
   'prm_name'                 : 'prm_011_RdHamrSvoDiag',
   'timeout'                  : 1200,
   'spc_id'                   : 1,
   'CWORD1'                   : 0x0200,
   #'TstMode'                  : (9,),
   'SYM_OFFSET'               : (567,),
   'ACCESS_TYPE'              : (1,),     # 1 byte at a time
   'NUM_LOCS'                 : (34,),    # 34 bytes total
}

prm_011_LbcGain = {
   'test_num'                 : 11,
   'prm_name'                 : 'prm_011_LbcGain',
   'timeout'                  : 1200,
   'CWORD1'                   : 0x0400,
   'spc_id'                   : 1,
   #'TstMode'                  : (10,),
   'ACCESS_TYPE'              : (3,),
   'MASK_VALUE'               : (0xFFFF,),
   'EXTENDED_MASK_VALUE'      : (0xFF00,),
   'SYM_OFFSET'               : (568,),
   'WR_DATA'                  : (0,),
   'EXTENDED_WR_DATA'         : (0,),
}
"""
         TypeCast = { # dict of functions
            '*': lambda x: self.CastDataType(x), # use default CastDataType, for SPC_ID primarily
            'F': float,
            'H': lambda x: int(x, 16), # Hexadecimal
            'I': int,
            'V': str,
         }
"""
pTableDataTypes = {
         # definitions should match the columns in tabledictionary
         # if tabledictionary defines column *, final column type is used for all subsequent columns
         'P011_SV_RAM_RD_BY_OFFSET' : { 
                                        'SYM_OFFSET' : '*',
                                        'RAM_ADDRESS': '*',
                                        'READ_DATA'  : 'H',
                                      },

      }

#------------- LDI DAC Conversion Factors --------------------------------------
IthreshDac        = {
   'ATTRIBUTE'    : 'PREAMP_TYPE',
    "DEFAULT"     : 'LSI5235',
   'TI'           : 0.28,
   'LSI5235'      : 0.275,
}
IaddDac           = {
   'ATTRIBUTE'    : 'PREAMP_TYPE',
   "DEFAULT"     :  'LSI5235',
   'TI'          : 0.28,
   'LSI5235'     : 0.205,
}
TPI_OC2COMPENSATION = {
   'ATTRIBUTE': 'HGA_SUPPLIER',
   'DEFAULT'  : 'HWY',
   'RHO'      : {
    'ATTRIBUTE'          : 'IS_2D_DRV',
    'DEFAULT'            : 0,
    0                    : 0.01,
    1                    : 0.015,
    },
   'HWY'      :{
    'ATTRIBUTE'          : 'IS_2D_DRV',
    'DEFAULT'            : 0,
    0                    : 0.01,
    1                    : 0.015,
    },
   'TDK'      : {
    'ATTRIBUTE'          : 'IS_2D_DRV',
    'DEFAULT'            : 0,
    0                    : 0.01,
    1                    : 0.015,
    },
}

ADD_TPI_OC2COMPENSATION = { # WFT Threshold to be used in MC Zones
   'ATTRIBUTE'             : 'nextState',
   'DEFAULT'               : 'VBAR_SET_ADC',
   'VBAR_SET_ADC'          : 0,
   'VBAR_FMT_PICKER'       : { # Additional Compensation for Retail usage
       'ATTRIBUTE'          : 'IS_2D_DRV',
       'DEFAULT'            : 0,
       0                    : 0.01,
       1                    : 0.005,
   },
}

ADD_BPI_OC2COMPENSATION = 0.03 # Additional Compensation for Retail usage

####################### ATI/WRITE_SCRN PARAM ##########################
if not testSwitch.FE_0302539_348429_P_ENABLE_VBAR_OC2:
    ATI_RRAW_ERASURE_LIMIT_OEM = 5.0
    ATI_RRAW_ERASURE_LIMIT_SBS = 4.7
    STE_RRAW_ERASURE_LIMIT_OEM = 5.0
    BASELINE_RRAW_ERASURE_LIMIT_OEM = 5.0
else:
    ATI_RRAW_ERASURE_LIMIT_OEM      = 5.0
    ATI_RRAW_ERASURE_LIMIT_SBS      = 4.7
    STE_RRAW_ERASURE_LIMIT_OEM      = 5.0
    BASELINE_RRAW_ERASURE_LIMIT_OEM = 5.0

ATI_RRAW_ERASURE_LIMIT_OEM_10K = 0
ATI_RRAW_ERASURE_LIMIT_SBS_10K = 0
STE_RRAW_ERASURE_LIMIT_OEM_10K = 0
BASELINE_RRAW_ERASURE_LIMIT_OEM_10K = 0

ATI_RRAW_ERASURE_LIMIT_OEM2 = 0
ATI_RRAW_ERASURE_LIMIT_SBS2 = 0
STE_RRAW_ERASURE_LIMIT_OEM2 = 0
BASELINE_RRAW_ERASURE_LIMIT_OEM2 = 0

RRAW_CRITERIA_ATI_51_UMP = {
   'baseline_limit'        : (1, BASELINE_RRAW_ERASURE_LIMIT_OEM, 1, BASELINE_RRAW_ERASURE_LIMIT_OEM),      # Limit = 0.7, flag = 1 means enabled this limit check
   'erasure_limit'         : {
       'ATTRIBUTE' : 'BG',
       'DEFAULT'   : 'OEM1B',
       'OEM1B'     : (1, ATI_RRAW_ERASURE_LIMIT_OEM, 1, STE_RRAW_ERASURE_LIMIT_OEM),
       'SBS'       : (0, ATI_RRAW_ERASURE_LIMIT_SBS, 0, STE_RRAW_ERASURE_LIMIT_OEM),
       },
   'delta_limit'           : (0, 1.1, 0, 3.0),
   'deltapercentage_limit' : (0, 101, 0, 30)
}

RRAW_CRITERIA_ATI_51_UMP_10K = {
   'baseline_limit'        : (1, BASELINE_RRAW_ERASURE_LIMIT_OEM_10K, 1, BASELINE_RRAW_ERASURE_LIMIT_OEM_10K),      # Limit = 0.7, flag = 1 means enabled this limit check
   'erasure_limit'         : (0, ATI_RRAW_ERASURE_LIMIT_OEM_10K, 1, STE_RRAW_ERASURE_LIMIT_OEM_10K), #dont check ATI spec
   'delta_limit'           : (0, 1.1, 0, 3.0),
   'deltapercentage_limit' : (0, 101, 0, 30),
}

#dummy value since unknown spec
RRAW_CRITERIA_ATI_51_SLIM = {
   'baseline_limit'        : (1, BASELINE_RRAW_ERASURE_LIMIT_OEM, 1, BASELINE_RRAW_ERASURE_LIMIT_OEM),      # Limit = 0.7, flag = 1 means enabled this limit check
   'erasure_limit'         : {
       'ATTRIBUTE' : 'BG',
       'DEFAULT'   : 'OEM1B',
       'OEM1B'     : (1, ATI_RRAW_ERASURE_LIMIT_OEM, 1, STE_RRAW_ERASURE_LIMIT_OEM),
       'SBS'       : (0, ATI_RRAW_ERASURE_LIMIT_SBS, 0, STE_RRAW_ERASURE_LIMIT_OEM),
       },
   'delta_limit'           : (0, 1.1, 0, 3.0),
   'deltapercentage_limit' : (0, 101, 0, 30),
}

RRAW_CRITERIA_ATI_51_FAT  = {
   'baseline_limit'        : (1, BASELINE_RRAW_ERASURE_LIMIT_OEM, 1, BASELINE_RRAW_ERASURE_LIMIT_OEM),      # Limit = 0.7, flag = 1 means enabled this limit check
   'erasure_limit'         : {
       'ATTRIBUTE' : 'BG',
       'DEFAULT'   : 'OEM1B',
       'OEM1B'     : (1, ATI_RRAW_ERASURE_LIMIT_OEM, 1, STE_RRAW_ERASURE_LIMIT_OEM),
       'SBS'       : (0, ATI_RRAW_ERASURE_LIMIT_SBS, 0, STE_RRAW_ERASURE_LIMIT_OEM),
       },
   'delta_limit'           : (0, 1.1, 0, 3.0),
   'deltapercentage_limit' : (0, 101, 0, 30),
   'SKIP_CHK'              : [-1],
}

RRAW_CRITERIA_ATI_51_FAT_OPEN  = {
   'baseline_limit'        : (1, 0, 1, 0),      # Limit = 0.7, flag = 1 means enabled this limit check
   'erasure_limit'         : (1, 0, 1, 0),
   'delta_limit'           : (0, 1.1, 0, 3.0),
   'deltapercentage_limit' : (0, 101, 0, 30),
   'SKIP_CHK'              : [-1],
}
RRAW_CRITERIA_ATI_51_UMP2 = {
   'baseline_limit'        : (1, BASELINE_RRAW_ERASURE_LIMIT_OEM2, 1, BASELINE_RRAW_ERASURE_LIMIT_OEM2),      # Limit = 0.7, flag = 1 means enabled this limit check
   'erasure_limit'         : (1, ATI_RRAW_ERASURE_LIMIT_OEM2, 1, STE_RRAW_ERASURE_LIMIT_OEM2),
   'delta_limit'           : (0, 1.1, 0, 3.0),
   'deltapercentage_limit' : (0, 101, 0, 30)
}
RRAW_CRITERIA_ATI_51_SLIM2 = {
   'baseline_limit'        : (1, BASELINE_RRAW_ERASURE_LIMIT_OEM2, 1, BASELINE_RRAW_ERASURE_LIMIT_OEM2),      # Limit = 0.7, flag = 1 means enabled this limit check
   'erasure_limit'         : (1, ATI_RRAW_ERASURE_LIMIT_OEM2, 1, STE_RRAW_ERASURE_LIMIT_OEM2),
   'delta_limit'           : (0, 1.1, 0, 3.0),
   'deltapercentage_limit' : (0, 101, 0, 30),
}

RRAW_CRITERIA_ATI_51_FAT2  = {
   'baseline_limit'        : (1, BASELINE_RRAW_ERASURE_LIMIT_OEM2, 1, BASELINE_RRAW_ERASURE_LIMIT_OEM2),      # Limit = 0.7, flag = 1 means enabled this limit check
   'erasure_limit'         : (1, ATI_RRAW_ERASURE_LIMIT_OEM2, 1, STE_RRAW_ERASURE_LIMIT_OEM2),
   'delta_limit'           : (0, 1.1, 0, 3.0),
   'deltapercentage_limit' : (0, 101, 0, 30),
   'SKIP_CHK'              : [-1],
}
RRAW_CRITERIA_ATI_51 = {
   "ATTRIBUTE"   : "SMR",
   'DEFAULT'     : 0,
   0             : RRAW_CRITERIA_ATI_51_UMP, #CMR Spec
   1             :  { #SMR Spec
      'ATTRIBUTE'          : 'nextState',
      'DEFAULT'            : 'default',
      'default'            : RRAW_CRITERIA_ATI_51_UMP,
      'WRITE_SCRN'         : RRAW_CRITERIA_ATI_51_UMP,
      'WRITE_SCRN_10K'     : RRAW_CRITERIA_ATI_51_UMP_10K,
      'INTER_BAND_SCRN'    : RRAW_CRITERIA_ATI_51_FAT_OPEN,
      'INTER_BAND_SCRN_500': RRAW_CRITERIA_ATI_51_FAT,
      'INTRA_BAND_SCRN'    : RRAW_CRITERIA_ATI_51_SLIM,
      'SMR_WRITE_SCRN'     : RRAW_CRITERIA_ATI_51_FAT,
      'WRITE_SCRN2'        : RRAW_CRITERIA_ATI_51_UMP2,
      'INTER_BAND_SCRN2'   : RRAW_CRITERIA_ATI_51_FAT2,
      'INTRA_BAND_SCRN2'   : { # RRAW_CRITERIA_ATI_51_SLIM2,
            'ATTRIBUTE'       : 'IS_2D_DRV',
            'DEFAULT'         : 0,
            0                 : {
                 'ATTRIBUTE'       : 'BG',
                 'DEFAULT'         : 'OEM1B',
                 'OEM1B'           : RRAW_CRITERIA_ATI_51_SLIM,
                 'SBS'             : RRAW_CRITERIA_ATI_51_SLIM2,
                 },
            1                 : RRAW_CRITERIA_ATI_51_SLIM2,
            },
      'SMR_WRITE_SCRN2'     : RRAW_CRITERIA_ATI_51_FAT2,
      'PRE_WRITE_SCRN'      : RRAW_CRITERIA_ATI_51_UMP2,
      'PRE_INTER_BAND_SCRN' : RRAW_CRITERIA_ATI_51_FAT2,
      'PRE_INTRA_BAND_SCRN' : RRAW_CRITERIA_ATI_51_SLIM2,
   },
}

if testSwitch.FE_0308542_348085_P_DESPERADO_3:
   RRAW_CRITERIA_ATI_51_SLIM.update({'SKIP_CHK' : [1]})
   RRAW_CRITERIA_ATI_51_SLIM2.update({'SKIP_CHK' : [1]})
   RRAW_CRITERIA_ATI_51_FAT.update({'SKIP_CHK' : [-1, 1]})
   RRAW_CRITERIA_ATI_51_FAT2.update({'SKIP_CHK' : [-1, 1]})
   RRAW_CRITERIA_ATI_51_FAT_OPEN.update({'SKIP_CHK' : [-1, 1]})

STE_BIE_BER_ERASURE_DELTA_LIMIT_OEM = 100
STE_BIE_BER_ERASURE_DELTA_LIMIT_SBS = 100
STE_BIE_BER_ERASURE_LIMIT_OEM = 0
STE_BIE_BER_ERASURE_LIMIT_SBS = 0
BIE_BER_CRITERIA_ATI_51 = {
   'baseline_limit'        : (0, 0, 0, 0),      #  flag = 1 means enabled this limit check
   'erasure_limit'         : (0, 0, 0, STE_BIE_BER_ERASURE_LIMIT_SBS),
   'delta_limit'           : (0, 0, 0, STE_BIE_BER_ERASURE_DELTA_LIMIT_SBS),
   'deltapercentage_limit' : (0, 0, 0, 0),
}

OTF_CRITERIA_ATI  = {   # no limit check
   'baseline_limit'        : (0, 0.0, 0, 0.7),
   'erasure_limit'         : (0, 4.0, 0, 4.0),
   'delta_limit'           : (0, 1.1, 0, 1.1),
   'deltapercentage_limit' : (0, 101, 0, 101)
}

ATI_SCRN_spc_id = 3000
WRITE_SCRN_spc_id = 10000

prm_SMR_zone_UMP = {
   'ZONES'  : {
      'EQUATION' : "list(set([TP.UMP_ZONE[self.dut.numZones][0]]+[TP.UMP_ZONE[self.dut.numZones][-1]]))",
   },
   'SPC_ID' : 10000,
   'CWORD1' : 0x0080 | testSwitch.USE_ZERO_LATENCY_WRITE_IN_T50_T51,
   'CENTER_TRACK_WRITES' : [3000],
   'BAND_SIZE' : 11,
}

prm_SMR_zone_UMP_10K = {
   'ZONES' : {
      'EQUATION' : "[TP.UMP_ZONE[self.dut.numZones][0]]",
   },
   'SPC_ID' : 80000,
   'CWORD1' : 0x0080 | testSwitch.USE_ZERO_LATENCY_WRITE_IN_T50_T51,
   'CENTER_TRACK_WRITES' : [10000],
   'BAND_SIZE' : 201,
}

prm_SMR_zone_Slim = {
   'ZONES' : {
      'ATTRIBUTE': 'FE_0385234_356688_P_MULTI_ID_UMP',
      'DEFAULT'  : 0,
      0 : {'EQUATION' : "[TP.UMP_ZONE[self.dut.numZones][-2]+1] + [self.dut.numZones/2, self.dut.numZones-2]",},
      1 : {'EQUATION' : "[TP.baseVbarTestZones[self.dut.numZones][0]] + [self.dut.numZones/2, TP.UMP_ZONE[self.dut.numZones][0]-1]",},
   },
   'SPC_ID' : 5000,
   'CWORD1' : 0x1200 | testSwitch.USE_ZERO_LATENCY_WRITE_IN_T50_T51,
   'CENTER_TRACK_WRITES' : [50],
}
prm_SMR_zone_Fat = {
   'ZONES' : {
      'ATTRIBUTE': 'FE_0385234_356688_P_MULTI_ID_UMP',
      'DEFAULT'  : 0,
      0 : {'EQUATION' : "[TP.UMP_ZONE[self.dut.numZones][-2]+1] + [self.dut.numZones/2, self.dut.numZones-2]",},
      1 : {'EQUATION' : "[TP.baseVbarTestZones[self.dut.numZones][0]] + [self.dut.numZones/2, TP.UMP_ZONE[self.dut.numZones][0]-1]",},
   },
   'SPC_ID' : 4000,
   'CWORD1' : 0x1200 | testSwitch.USE_ZERO_LATENCY_WRITE_IN_T50_T51,
   'CENTER_TRACK_WRITES' : [1000],
}
prm_SMR_zone_Fat_500 = {
   'ZONES' : {
      'ATTRIBUTE': 'FE_0385234_356688_P_MULTI_ID_UMP',
      'DEFAULT'  : 0,
      0 : {'EQUATION' : "[TP.UMP_ZONE[self.dut.numZones][-2]+1] + [self.dut.numZones/2, self.dut.numZones-2]",},
      1 : {'EQUATION' : "[TP.baseVbarTestZones[self.dut.numZones][0]] + [self.dut.numZones/2, TP.UMP_ZONE[self.dut.numZones][0]-1]",},
   },
   'SPC_ID' : 4500,
   'CWORD1' : 0x1200 | testSwitch.USE_ZERO_LATENCY_WRITE_IN_T50_T51,
   'CENTER_TRACK_WRITES' : [500],
}
prm_SMR_zone_Merge = {
   'ZONES'  : prm_SMR_zone_Fat['ZONES'],
   'CWORD1' : prm_SMR_zone_Fat['CWORD1'],
   'SPC_ID' : 6000,
   'CENTER_TRACK_WRITES' : prm_SMR_zone_Fat['CENTER_TRACK_WRITES'],
}

prm_WTF_ALL_UMP_zone = {
   'ZONES' : {
      'EQUATION' : "[1, self.dut.numZones/2, self.dut.numZones-2]",
   },
}

prm_ATI_51 = {
   'ZONES'                 : {
      'ATTRIBUTE'          : 'nextState',
      'DEFAULT'            : 'WRITE_SCRN',
      'INTRA_BAND_SCRN'    : {
            'ATTRIBUTE'    : ('Waterfall_Done', 'FE_0258044_348085_WATERFALL_WITH_ONE_TRK_PER_BAND'),
            'DEFAULT'      : 'default',
            'default'      : prm_SMR_zone_Slim['ZONES'],
            ('DONE', 1)    : [], #skip it
      },
      'WRITE_SCRN'         : {
            'ATTRIBUTE'    : ('Waterfall_Done', 'FE_0258044_348085_WATERFALL_WITH_ONE_TRK_PER_BAND'),
            'DEFAULT'      : 'default',
            'default'      : prm_SMR_zone_UMP['ZONES'],
            ('DONE', 1)    : prm_WTF_ALL_UMP_zone['ZONES'],
      },
      'WRITE_SCRN_10K'     : {
            'ATTRIBUTE'    : ('Waterfall_Done', 'FE_0258044_348085_WATERFALL_WITH_ONE_TRK_PER_BAND'),
            'DEFAULT'      : 'default',
            'default'      : prm_SMR_zone_UMP_10K['ZONES'],
            ('DONE', 1)    : prm_WTF_ALL_UMP_zone['ZONES'],
      },
      'INTER_BAND_SCRN'    : {
            'ATTRIBUTE'    : ('Waterfall_Done', 'FE_0258044_348085_WATERFALL_WITH_ONE_TRK_PER_BAND'),
            'DEFAULT'      : 'default',
            'default'      : prm_SMR_zone_Fat['ZONES'],
            ('DONE', 1)    : [], #skip it
      },
      'INTER_BAND_SCRN_500'    : {
            'ATTRIBUTE'    : ('Waterfall_Done', 'FE_0258044_348085_WATERFALL_WITH_ONE_TRK_PER_BAND'),
            'DEFAULT'      : 'default',
            'default'      : prm_SMR_zone_Fat_500['ZONES'],
            ('DONE', 1)    : [], #skip it
      },
      'SMR_WRITE_SCRN'     : {
            'ATTRIBUTE'    : ('Waterfall_Done', 'FE_0258044_348085_WATERFALL_WITH_ONE_TRK_PER_BAND'),
            'DEFAULT'      : 'default',
            'default'      : prm_SMR_zone_Merge['ZONES'],
            ('DONE', 1)    : [], #skip it
      },
      'INTRA_BAND_SCRN2'   : {
            'ATTRIBUTE'    : ('Waterfall_Done', 'FE_0258044_348085_WATERFALL_WITH_ONE_TRK_PER_BAND'),
            'DEFAULT'      : 'default',
            'default'      : prm_SMR_zone_Slim['ZONES'],
            ('DONE', 1)    : [], #skip it
      },
      'WRITE_SCRN2'        : {
            'ATTRIBUTE'    : ('Waterfall_Done', 'FE_0258044_348085_WATERFALL_WITH_ONE_TRK_PER_BAND'),
            'DEFAULT'      : 'default',
            'default'      : prm_SMR_zone_UMP['ZONES'],
            ('DONE', 1)    : prm_WTF_ALL_UMP_zone['ZONES'],
      },
      'INTER_BAND_SCRN2'   : {
            'ATTRIBUTE'    : ('Waterfall_Done', 'FE_0258044_348085_WATERFALL_WITH_ONE_TRK_PER_BAND'),
            'DEFAULT'      : 'default',
            'default'      : prm_SMR_zone_Fat['ZONES'],
            ('DONE', 1)    : [], #skip it
      },
      'SMR_WRITE_SCRN2'    : {
            'ATTRIBUTE'    : ('Waterfall_Done', 'FE_0258044_348085_WATERFALL_WITH_ONE_TRK_PER_BAND'),
            'DEFAULT'      : 'default',
            'default'      : prm_SMR_zone_Merge['ZONES'],
            ('DONE', 1)    : [], #skip it
      },
      'PRE_INTRA_BAND_SCRN': {
            'ATTRIBUTE'    : ('Waterfall_Done', 'FE_0258044_348085_WATERFALL_WITH_ONE_TRK_PER_BAND'),
            'DEFAULT'      : 'default',
            'default'      : prm_SMR_zone_Slim['ZONES'],
            ('DONE', 1)    : [], #skip it
      },
      'PRE_INTER_BAND_SCRN': {
            'ATTRIBUTE'    : ('Waterfall_Done', 'FE_0258044_348085_WATERFALL_WITH_ONE_TRK_PER_BAND'),
            'DEFAULT'      : 'default',
            'default'      : prm_SMR_zone_Fat['ZONES'],
            ('DONE', 1)    : [], #skip it
      },
   },
   'base'                     : {
      'spc_id'                : {
         'ATTRIBUTE'          : 'nextState',
         'DEFAULT'            : 'default',
         'default'            : 1,
         'WRITE_SCRN'         : prm_SMR_zone_UMP['SPC_ID'],
         'WRITE_SCRN_10K'     : prm_SMR_zone_UMP_10K['SPC_ID'],
         'ATI_SCRN'           : ATI_SCRN_spc_id,
         'INTER_BAND_SCRN'    : prm_SMR_zone_Fat['SPC_ID'],
         'INTER_BAND_SCRN_500': prm_SMR_zone_Fat_500['SPC_ID'],
         'INTRA_BAND_SCRN'    : prm_SMR_zone_Slim['SPC_ID'],
         'SMR_WRITE_SCRN'     : prm_SMR_zone_Merge['SPC_ID'],
         'WRITE_SCRN2'        : prm_SMR_zone_UMP['SPC_ID'],
         'INTER_BAND_SCRN2'    : prm_SMR_zone_Fat['SPC_ID'],
         'INTRA_BAND_SCRN2'    : prm_SMR_zone_Slim['SPC_ID'],
         'SMR_WRITE_SCRN2'     : prm_SMR_zone_Merge['SPC_ID'],
      },
      'test_num'              : 51,
      'prm_name'              : 'prm_ATI_51',
      'timeout'               : 18000,
      'BAND_SIZE'             : {
         'ATTRIBUTE'          : 'nextState',
         'DEFAULT'            : 'default',
         'default'            : 3 * tracksPerBand,
         'SMR_WRITE_SCRN'     : 3 * tracksPerBand, # 2 band
         'WRITE_SCRN'         : prm_SMR_zone_UMP['BAND_SIZE'],
         'SMR_WRITE_SCRN2'     : 3 * tracksPerBand, # 2 band
         'WRITE_SCRN2'         : prm_SMR_zone_UMP['BAND_SIZE'],
         'WRITE_SCRN_10K'     : prm_SMR_zone_UMP_10K['BAND_SIZE'],
      },
      'TEST_HEAD'             : 0,
      'CWORD1'                : {
         'ATTRIBUTE'          : 'nextState',
         'DEFAULT'            : 'default',
         'default'            : 0x0080 | testSwitch.USE_ZERO_LATENCY_WRITE_IN_T50_T51,
         'WRITE_SCRN'         : prm_SMR_zone_UMP['CWORD1'],
         'WRITE_SCRN_10K'     : prm_SMR_zone_UMP_10K['CWORD1'],
         'ATI_SCRN'           : 0x0040 | testSwitch.USE_ZERO_LATENCY_WRITE_IN_T50_T51,
         'INTER_BAND_SCRN'    : prm_SMR_zone_Fat['CWORD1'],
         'INTER_BAND_SCRN_500': prm_SMR_zone_Fat_500['CWORD1'],
         'INTRA_BAND_SCRN'    : prm_SMR_zone_Slim['CWORD1'],
         'SMR_WRITE_SCRN'     : prm_SMR_zone_Merge['CWORD1'],
         'WRITE_SCRN2'         : prm_SMR_zone_UMP['CWORD1'] | 0x8000,
         'INTER_BAND_SCRN2'    : prm_SMR_zone_Fat['CWORD1'] | 0x8000,
         'INTRA_BAND_SCRN2'    : prm_SMR_zone_Slim['CWORD1'] | 0x8000,
         'SMR_WRITE_SCRN2'     : prm_SMR_zone_Merge['CWORD1'] | 0x8000,
         'PRE_WRITE_SCRN'      : prm_SMR_zone_UMP['CWORD1'] | 0x0040, # Disable Defect Free Band
         'PRE_INTER_BAND_SCRN' : prm_SMR_zone_Fat['CWORD1'] | 0x0040, # Disable Defect Free Band
         'PRE_INTRA_BAND_SCRN' : prm_SMR_zone_Slim['CWORD1'] | 0x0040, # Disable Defect Free Band
      },
      'CWORD2'                : {
         'EQUATION' : "testSwitch.extern.FE_0274344_504159_P_DEFECT_FREE_BAND_WITH_DEFECT_TABLE",
      },
      'ZONE_POSITION'   : {
         'ATTRIBUTE'    : 'nextState',
         'DEFAULT'      : 'default',
         'default'      : 100,
         'ATI_SCRN'     : 190,
      },
      'TLEVEL'          : {
         'ATTRIBUTE'                : 'FE_0276349_228371_CHEOPSAM_SRC',
         'DEFAULT'                  : 1,
         0                          : 30,
         1                          : 40,
      },
      'RETRY_COUNTER_MAX'              : 100,
      'MAX_ERR_RATE'                   : 873,
      'BASELINE_CLEANUP_WRT_RETRY'     : 25,
      'CHANGE_SEEK_LENGTH_AND_RETRY'   : 25,
      'RETRY_INCR'                     : 100,
   },
   'CENTER_TRACK_WRITES' : {
         'ATTRIBUTE'          : 'nextState',
         'DEFAULT'            : 'default',
         'default'            : prm_SMR_zone_UMP['CENTER_TRACK_WRITES'],
         'WRITE_SCRN'         : prm_SMR_zone_UMP['CENTER_TRACK_WRITES'],
         'WRITE_SCRN_10K'     : prm_SMR_zone_UMP_10K['CENTER_TRACK_WRITES'],
         'INTER_BAND_SCRN'    : prm_SMR_zone_Fat['CENTER_TRACK_WRITES'],
         'INTER_BAND_SCRN_500': prm_SMR_zone_Fat_500['CENTER_TRACK_WRITES'],
         'INTRA_BAND_SCRN'    : prm_SMR_zone_Slim['CENTER_TRACK_WRITES'],
         'SMR_WRITE_SCRN'     : prm_SMR_zone_Merge['CENTER_TRACK_WRITES'],
         'INTER_BAND_SCRN2'    : prm_SMR_zone_Fat['CENTER_TRACK_WRITES'],
         'INTRA_BAND_SCRN2'    : prm_SMR_zone_Slim['CENTER_TRACK_WRITES'],
         'SMR_WRITE_SCRN2'     : prm_SMR_zone_Merge['CENTER_TRACK_WRITES'],
         'PRE_INTER_BAND_SCRN' : prm_SMR_zone_Fat['CENTER_TRACK_WRITES'],
         'PRE_INTRA_BAND_SCRN' : prm_SMR_zone_Slim['CENTER_TRACK_WRITES'],
      },
   'LIMITS'              : {      # BER Prediction test Setup and Limits
      'RP_LIMIT'              : 3.9,            # RRAW BER Prediction Limit
      'OD_LIMIT'              : 9.0,            # OTF BER Delta Limit
      'PRED_NUM_WRITES'       : 1000000,        # Predict the BER for this number of Writes
      'CALCULATE_BER_PRED'    : 0               # Turn the BER prediction on/off - 1=on, 0=off
   },
}

#Change to and 1 to turn on an ALL ZONE test 51 operation, rather than just OD, MD, ID.
if testSwitch.T51_ALL_ZONES:
   prm_ATI_51.update({
      'ZONES' : { 'ATTRIBUTE'  : 'numZones',
                  'DEFAULT'    : 31,
                  17           : range(17),
                  24           : range(24),
                  31           : range(31),
                  60           : range(60),
                },
   })

if testSwitch.shortProcess:
   prm_ATI_51.update({
      'ZONES'              : [1],
   })


prm_ATI_51_WRT_SCRN = CUtility.copy(prm_ATI_51)
prm_ATI_51_ATI_SCRN = CUtility.copy(prm_ATI_51)
prm_ATI_51_WRT_MERGE_SCRN = CUtility.copy(prm_ATI_51)
#prm_ATI_51_WRT_MERGE_SCRN['NUM_SUB_WRITES'] = (prm_SMR_zone_Slim['CENTER_TRACK_WRITES'][0], 0, 0)
prm_ATI_51_WRT_MERGE_SCRN.update({
    'NUM_SUB_WRITES' : { 
        'ATTRIBUTE'     : 'nextState',
        'DEFAULT'       : 'SMR_WRITE_SCRN',
        'SMR_WRITE_SCRN': (prm_SMR_zone_Slim['CENTER_TRACK_WRITES'][0], prm_SMR_zone_Fat_500['CENTER_TRACK_WRITES'][0], 0),
        'SMR_WRITE_SCRN2': (prm_SMR_zone_Slim['CENTER_TRACK_WRITES'][0], 0, 0),
            },
    'RD_TRKS_SUB_WRITES' : { 
        'ATTRIBUTE'     : 'nextState',
        'DEFAULT'       : 'SMR_WRITE_SCRN',
        'SMR_WRITE_SCRN': (5, 0, 0),
        'SMR_WRITE_SCRN2': (5, 0, 0),
            },
})


## Triplet ATI
prm_Triplet_ATI_STE = {
      'test_num'                    : 51,
      'prm_name'                    : 'prm_Triplet_ATI_STE',
      'spc_id'                      : 500,
      'CHANGE_SEEK_LENGTH_AND_RETRY': 25,
      'ZONE_POSITION'               : 198,
      'ZONE'                        : 0,
      'MAX_ERR_RATE'                : 873,
      'BASELINE_CLEANUP_WRT_RETRY'  : 25,
      'TLEVEL'                      : {
         'ATTRIBUTE'                : 'FE_0276349_228371_CHEOPSAM_SRC',
         'DEFAULT'                  : 1,
         0                          : 30,
         1                          : 40,
      },
      'BAND_SIZE'                   : 11,
      'RETRY_INCR'                  : 5,
      'timeout'                     : 400, # 7 mins
      'TEST_HEAD'                   : 0,
      'RETRY_COUNTER_MAX'           : 100,
      'CWORD1'                      : 0x40D0,
      'CENTER_TRACK_WRITES'         : 3000,
}


##--------------------------- Combo Spec Screen ---------------------------
flawLIMIT = {
    "ATTRIBUTE" : 'HGA_SUPPLIER',
    "DEFAULT" : 'RHO',
    "TDK" : 563,
    "RHO" : 439,
}
OTFLimit   = 5.4
deltaLimit = 0.023

prm_auditTest_178 = {
   'test_num'              : 178,
   'prm_name'              : 'prm_auditTest_178',
   'spc_id'                : 1,
   'CWORD1'                : 0x0220,
   'NUM_SERP'              : 2,
   'timeout'               : 200,
   }

T508_0000FFFF = {
   'test_num'                 : 508,
   'prm_name'                 : 'T508_0000FFFF',
   "CTRL_WORD1"               : (0x0000),
   "BYTE_OFFSET"              : (0,0),
   "BUFFER_LENGTH"            : (0x2,0x0000),
   "PATTERN_TYPE"             : (0),            # 0 = fixed pattern
   "DATA_PATTERN0"            : (0x0000, 0xFFFF),
   "DATA_PATTERN1"            : (0x0000, 0x0000),
   "BYTE_PATTERN_LENGTH"      : (4),
}

#st(508, CTRL_WORD1 = 0x0004, BYTE_OFFSET = (0,0), BUFFER_LENGTH = (0,1536), timeout = 3600)
# Read and display the write buffer
T508_2 = {
   'test_num'                 : 508,
   'prm_name'                 : 'T508_2',
   "CTRL_WORD1"               : (0x0004),
   "BYTE_OFFSET"              : (0,0),
   "BUFFER_LENGTH"            : (0,1536),
   #"BUFFER_LENGTH"            : (0,0x8000),
}

prm_508_Display_ReadBuffer = {
   'test_num' : 508,
   'prm_name' : 'prm_508_Display_ReadBuffer',
   'timeout' : 420,

   'PARAMETER_1' : (0x0005,),
   'PARAMETER_10' : (0x0000,),
   'PARAMETER_2' : (0x0000,),
   'PARAMETER_3' : (0x0200,),
   'PARAMETER_4' : (0x0000,),
   'PARAMETER_5' : (0x0000,),
   'PARAMETER_6' : (0x0000,),
   'PARAMETER_7' : (0x0000,),
   'PARAMETER_8' : (0x0000,),
   'PARAMETER_9' : (0x0000,),
}

prm_508_Display_WriteBuffer = {
   'test_num' : 508,
   'prm_name' : 'prm_508_Display_WriteBuffer',
   'timeout' : 420,

   'PARAMETER_1' : (0x0004,),
   'PARAMETER_10' : (0x0000,),
   'PARAMETER_2' : (0x0000,),
   'PARAMETER_3' : (0x0200,),
   'PARAMETER_4' : (0x0000,),
   'PARAMETER_5' : (0x0000,),
   'PARAMETER_6' : (0x0000,),
   'PARAMETER_7' : (0x0000,),
   'PARAMETER_8' : (0x0000,),
   'PARAMETER_9' : (0x0000,),
}

if testSwitch.BF_0130425_357466_FIX_T597_DOS_VER:
   prm_597_RdmWrt = {
      'test_num' : 597,
      'prm_name' : 'prm_597_RdmWrt',
      'timeout' : 1200,
      'ALLOW_WIDE_MODE' : (0x0001,),
      'FORCE_ASYNC' : (0x0000,),
      'GRADING_OUTPUT' : (0x0000,),
      'HIGH_PARTITION_SIZE' : (0x0000,),
      'IOPS_LOWER_LIM' : (0x0000,),
      'MAX_BLOCK_PER_CMD' : (0x0004,),
      'MAX_UNRECOVERABLE_ERR' : (0x0000,),
      'MISC_CMD_WEIGHT' : (0x0000,),
      'MULT_CMD_PACKET' : (0x0000,),
      'OPERATIONAL_FLAGS' : (0x0007,),
      'PARTITION_NUM' : (0x0002,),
      'PARTITION_SIZE' : (0x0000,),
      'QUEUE_DEPT' : (0x0000,),
      'QUEUE_TAG_WEIGHT' : (0x0001,),
      'RANDOM_SEED' : (0x006C,),
      'RECOVERED_ERR_LIMS' : (0x0100,),
      'REQ_ACK_OFFSET' : (0x0000,),
      'RW_CMD_WEIGHT' : (0x0100,),
      'TEST_FUNCTION' : (0x1000,),
      'TEST_OPERATING_MODE' : (0x0008,),
      'TEST_PASS_COUNT' : (0x0003,),
      'TEST_PASS_MULTIPLIER' : (0x0000,),
   }
   prm_597_RdmRd = {
      'test_num' : 597,
      'prm_name' : 'prm_597_RdmRd',
      'timeout' : 1200,
      'ALLOW_WIDE_MODE' : (0x0001,),
      'FORCE_ASYNC' : (0x0000,),
      'GRADING_OUTPUT' : (0x0000,),
      'HIGH_PARTITION_SIZE' : (0x0000,),
      'IOPS_LOWER_LIM' : (0x0000,),
      'MAX_BLOCK_PER_CMD' : (0x0004,),
      'MAX_UNRECOVERABLE_ERR' : (0x0000,),
      'MISC_CMD_WEIGHT' : (0x0000,),
      'MULT_CMD_PACKET' : (0x0000,),
      'OPERATIONAL_FLAGS' : (0x0007,),
      'PARTITION_NUM' : (0x0002,),
      'PARTITION_SIZE' : (0x0000,),
      'QUEUE_DEPT' : (0x0000,),
      'QUEUE_TAG_WEIGHT' : (0x0001,),
      'RANDOM_SEED' : (0x006C,),
      'RECOVERED_ERR_LIMS' : (0x0100,),
      'REQ_ACK_OFFSET' : (0x0000,),
      'RW_CMD_WEIGHT' : (0x1000,),
      'TEST_FUNCTION' : (0x1000,),
      'TEST_OPERATING_MODE' : (0x0008,),
      'TEST_PASS_COUNT' : (0x0003,),
      'TEST_PASS_MULTIPLIER' : (0x0000,),
   }
else:
   prm_597_RdmWrt = {
      'test_num'                 : 597,
      'prm_name'                 : 'prm_597_RdmWrt',
      'timeout'                  : 1200,
      "IOPS_LOWER_LIM"           : (0x0000,),  ###  this needs to get set once we have data and we want to set it to
      "MAX_BLOCK_PER_CMD"        : (0x0008,),  ## Changed from 4 to 8 this will be 4 K command Block size Suitable for Near line application.
      "OPERATIONAL_FLAGS"        : (0x0004,),  ##  Changed from 7 to 4 the first two bit are undefined Measuers IOPS and apply limit
      "RANDOM_SEED"              : (0x006C,),  ## Random seed the same for all the test This is good to always genrate the same LBA
      "TEST_PASS_COUNT"          : (0x1388,),
      "TEST_PASS_MULTIPLIER"     : (0x0001,),
      "MAXIMUM_LBA"              : (0, 0, 0, 0),
      "MINIMUM_LBA"              : (0, 0, 0, 0),
   }
   prm_597_RdmRd = {
      'test_num'                 : 597,
      'prm_name'                 : 'prm_597_RdmRd',
      'timeout'                  : 1200,
      "IOPS_LOWER_LIM"           : (0x0000,),
      "MAX_BLOCK_PER_CMD"        : (0x0008,),  ## Changed from 4 to 8 this will be 4 K command Block size Suitable for Near line application.
      "OPERATIONAL_FLAGS"        : (0x0004,),  ##  Changed from 7 to 4 the first two bit are undefined Measuers IOPS and apply limit
      "RANDOM_SEED"              : (0x006C,),  ## Random seed the same for all the test This is good to always genrate the same LBA
      "TEST_PASS_COUNT"          : (0x1388,),  ###5000 Command
      "TEST_PASS_MULTIPLIER"     : (0x0001,),
      "MAXIMUM_LBA"              : (0, 0, 0, 0),
      "MINIMUM_LBA"              : (0, 0, 0, 0),
   }

prm_598_Wrt = {
   'test_num'                 : 598,
   'prm_name'                 : 'prm_598_Wrt',
   'timeout'                  : 12000,
   'spc_id'                   : 2,
   "BLKS_PER_XFR"             : (0x2000,),
   "CYLINDER_SKEW_TIME"       : (0x05DC,),      # MLW WAS 0x018C
   "DERATED_SKEW_TIME"        : (0x0834,),      # MLW WAS 0x073E
   "DEVIATION_LIMIT"          : (0x0063,),      # MLW 10/20/09 chgd from 0x0012 to not fail
   "DISABLE_CACHING"          : (0x0000,),
   "DISABLE_ECC_ON_FLY"       : (0x0000,),
   "DISABLE_FREE_RETRY"       : (0x0000,),
   "DISPLAY_WEAKEST_HEAD"     : (0x0000,),
   "ENABLE_PFAST"             : (0x0000,),
   "EXECUTE_HIDDEN_RETRY"     : (0x0000,),
   "RANDOM_SEED"              : (0x0011,),
   "REPORT_HIDDEN_RETRY"      : (0x0000,),
   "REV_TIME"                 : (0x208D,),
   "RW_MODE"                  : (0x0001,),
   "SERPENT_BLOCK_OPT"        : (0x0001,),
   "TEST_FUNCTION"            : (0x0000,),
   "TOTAL_BLKS_TO_XFR"        : (0x0000,0x0003,),
   "TRACK_SKEW_TIME"          : (0x0898,),      # MLW WAS 0x04F7
   "ZONE_TEST"                : (0x0000,),
   "ZONE_TO_TEST"             : (0x0000,),
}

prm_598_Rd = {
   'test_num'                 : 598,
   'prm_name'                 : 'prm_598_Rd',
   'timeout'                  : 12000,
   'spc_id'                   : 1,
   "BLKS_PER_XFR"             : (0x2000,),
   "CYLINDER_SKEW_TIME"       : (0x05DC,),      # MLW WAS 0x018C
   "DERATED_SKEW_TIME"        : (0x0834,),      # MLW WAS 0x073E
   "DEVIATION_LIMIT"          : (0x0063,),      # MLW 10/20/09 chgd from 0x0009 to not fail
   "DISABLE_CACHING"          : (0x0000,),
   "DISABLE_ECC_ON_FLY"       : (0x0000,),
   "DISABLE_FREE_RETRY"       : (0x0000,),
   "DISPLAY_WEAKEST_HEAD"     : (0x0000,),
   "ENABLE_PFAST"             : (0x0000,),
   "EXECUTE_HIDDEN_RETRY"     : (0x0000,),
   "RANDOM_SEED"              : (0x0011,),
   "REPORT_HIDDEN_RETRY"      : (0x0000,),
   "REV_TIME"                 : (0x208D,),
   "RW_MODE"                  : (0x0000,),
   "SERPENT_BLOCK_OPT"        : (0x0001,),
   "TEST_FUNCTION"            : (0x0000,),
   "TOTAL_BLKS_TO_XFR"        : (0x0000,0x0003,),
   "TRACK_SKEW_TIME"          : (0x0898,),      # MLW WAS 0x04F7
   "ZONE_TEST"                : (0x0000,),
   "ZONE_TO_TEST"             : (0x0000,),
}

#####################  PCBA    #####################################

pcbaDram_102 = {
   'base' : {
      'test_num'           : 102,
      'prm_name'           : 'PCBA SCREEN_102',
      'spc_id'             : 1,
      'timeout'            : 500,
      'NUM_SAMPLES'        : 1,
      'PRINT'              : 10,
      },
   'modes' : {
      'LOW_V_FIXED_PATT'   : {'CWORD1' : 0x0012, 'PATTERNS' : (0x5050, 0x0F0F, 0x0000)},
      'LOW_V_ADDR_PATT'    : {'CWORD1' : 0x0011},
      'LOW_V_RAND_PATT'    : {'CWORD1' : 0x0014},
      'NOM_V_RAND_PATT'    : {'CWORD1' : 0x0024},
      'NOM_V_FIXED_PATT'   : {'CWORD1' : 0x0022, 'PATTERNS' : (0x5050, 0x0F0F, 0x0000)},
      'NOM_V_ADDR_PATT'    : {'CWORD1' : 0x0021},
      'HIGH_V_RAND_PATT'   : {'CWORD1' : 0x0044},
      'HIGH_V_FIXED_PATT'  : {'CWORD1' : 0x0042, 'PATTERNS' : (0x5050, 0x0F0F, 0x0000)},
      'HIGH_V_ADDR_PATT'   : {'CWORD1' : 0x0041},
      }
   }

#####################  State Rerun  #####################################
# Pls arrange in alphabetical order
stateRerunParams = {
#  'states'       : {'AFH1' : [12345]},
#  'dependencies' : {'AFH1' : ['MDW_CAL', 'INIT_RAP'], 'MDW_CAL' : ['HEAD_CAL']},
   'states'        : {
      'ATTRIBUTE'  : 'BG',
      'DEFAULT'    : 'OEM1B',
      'OEM1B'      : {
            'FOF_SCRN'           : [11164],
            'ADV_SWEEP'          : [10427],
            'ATTR_VAL'           : [10609],
            'ATI_SCRN'           : [14861, 14635, 10522,10468],
            'B2B_COMPARE'        : [14746],
            'BPINOMINAL'         : [10007],
            'CLEAR_EWLM'         : [10251],
            'COMMAND_SET'        : [13452],
            'CUST_CFG'           : [13426, (14035, 3)],
            'DNLD_CODE'          : [(11044, 2)],
            'DNLD_BRG_IV'        : [10340],
            'DNLD_F3CODE'        : [10340],
            'ENABLE_MC'          : [10569],
            'FULL_WRITE'         : [10569],
            'INIT'               : [10609, 13420],
            'INIT_SYS'           : [10130],
            'INTRA_BAND_SCRN2'   : [10522],
            'INTER_BAND_SCRN2'   : [10522],
            'INTER_BAND_SCRN_500': [10522],
            'PES_SCRN2'          : [10622],
            'PES_SCRN3'          : [10622],
            'POWER_MODE'         : [13454],
            'PREVBAR_OPTI'       : [10522],
            'PRE_OPTI'           : [10007, 10522],
            'PRE_OPTI2'          : [10007],
            'PV_SCRN'            : [48463],
            'READ_OPTI'          : [10632],
            'READ_SCRN2'         : [10632, 14574],
            'SQZ_WRITE'          : [10632],
            'SQZ_WRITE2'         : [10632],
            'READ_SCRN2A'        : [14554],
            'READ_SCRN2C'        : [14554],
            'READ_XFER'          : [14005, (10578, 2), 14029, 10340, 14026],
            'SEEK_TIME'          : [10566],
            'SERVO_OPTI2'        : [11049, 11087],
            'SET_DCM_ATTR'       : [10609],
            'SPMQM'              : [10569],  # OPShock
            'SP_RD_TRUPUT'       : [14554, 14005, (10578, 2), 14029, 10340, 14026, 10566, 11044, 10569, 10443],
            'SP_WR_TRUPUT'       : [14554, 14005, (10578, 2), 14026, 14017, 10566, 11044, 10569, 10443],
            'VBAR_CLR'           : [19999],
            'VBAR_HMS1'          : [19999],
            'VBAR_HMS2'          : [19999],
            'VOLTAGE_HL'         : [(12361,2), (12364,2), (12367,2), (10161,2)],
            'WRITE_SCRN'         : [10427, 14861, 14635,10522,10468, 11087],
            'WRITE_SCRN2'        : [10427, 14861, 14635,10522,10468, 11087],
            'WRITE_XFER'         : [14005, (10578, 2), 14026, 14017],
            'WR_VERIFY'          : [14737],
            'ZAP'                : [11049, 11087],
            'ZEST'               : [(14995,2), 48562],
            'SPF'                : [11231, 11049, 10463, 10548],
            '*'                  : [(13420,2), (14026,2)],    # requested by ScPk 09/11/2011
         },
      'SBS'        : {
            'AFH1'               : [14841,11049],
            'AFH2'               : [14841],
            'ADV_SWEEP'          : [10427],
            'ATTR_VAL'           : [10609],
            'ATI_SCRN'           : [14861, 14635, 10522,10468],
            'B2B_COMPARE'        : [14746],
            'BPINOMINAL'         : [10007],
            'CLEAR_EWLM'         : [10251],
            'COMMAND_SET'        : [13452],
            'CUST_CFG'           : [13426, (14035, 3)],
            'DNLD_CODE'          : [(11044, 2)],
            'DNLD_BRG_IV'        : [10340],
            'DNLD_F3CODE'        : [10340],
            'ENABLE_MC'          : [10569],
            'FULL_WRITE'         : [10569],
            'INIT'               : [10609, 13420],
            'INIT_SYS'           : [10130, 14501, 10451],
            'INTRA_BAND_SCRN2'   : [10522],
            'INTER_BAND_SCRN2'   : [10522],
            'INTER_BAND_SCRN_500': [10522],
            'PES_SCRN'           : [10414], # 10414=maxRRO fail, will trigger rezap 1st
            'PES_SCRN2'          : [10622],
            'PES_SCRN3'          : [10622],
            'POWER_MODE'         : [13454],
            'PREVBAR_OPTI'       : [10522],
            'PRE_OPTI'           : [10007, 10522],
            'PRE_OPTI2'          : [10007],
            'PV_SCRN'            : [48463],
            'READ_OPTI'          : [10632],
            'READ_SCRN2'         : [10632, 14574],
            'RW_GAP_CAL'         : [14841, 10352, 48598],
            'SIF_CAL'            : [11049],
            'SQZ_WRITE'          : [10632],
            'SQZ_WRITE2'         : [10632],
            'SERVO_OPTI'         : [10137],
            'READ_SCRN2A'        : [14554],
            'READ_SCRN2C'        : [14554],
            'READ_XFER'          : [14005, (10578, 2), 14029, 10340, 14026],
            'SEEK_TIME'          : [10566],
            'SERVO_OPTI2'        : [11049, 11087],
            'SET_DCM_ATTR'       : [10609],
            'SPMQM'              : [10569],  # OPShock
            'SP_RD_TRUPUT'       : [14554, 14005, (10578, 2), 14029, 10340, 14026, 10566, 11044, 10569, 10443],
            'SP_WR_TRUPUT'       : [14554, 14005, (10578, 2), 14026, 14017, 10566, 11044, 10569, 10443],
            'SP_RD_TRUPUT2'      : [14554, 14005, (10578, 2), 14029, 10340, 14026, 10566, 11044, 10569, 10443],
            'SP_WR_TRUPUT2'      : [14554, 14005, (10578, 2), 14026, 14017, 10566, 11044, 10569, 10443],
            'VBAR_CLR'           : [19999],
            'VBAR_HMS1'          : [19999],
            'VBAR_HMS2'          : [19999],
            'VOLTAGE_HL'         : [(12361,2), (12364,2), (12367,2), (10161,2)],
            'WRITE_SCRN'         : [10427, 14861, 14635,10522,10468, 11087],
            'WRITE_SCRN2'        : [10427, 14861, 14635,10522,10468, 11087],
            'INTRA_BAND_SCRN'    : [14635],            
            'WRITE_XFER'         : [14005, (10578, 2), 14026, 14017],
            'WR_VERIFY'          : [14737],
            'ZAP'                : [11049, 11087, 10463, 10657],
            'ZEST'               : [(14995,2), 11049, 48562, 42174, 42176],
            'SPF'                : [11231, 11049, 10463, 10548],
            'AGC_JOG'            : [10267, 10266],
            'SERIAL_FMT'         : [10219, 10566],
            'SP_TTR'             : [10197],
            'INIT_SMART'         : [10566],
            '*'                  : [(13420,2), (14026,2)],    # requested by ScPk 09/11/2011
         },
            
   },
   'dependencies'  : {
      'ATTRIBUTE'  : 'BG',
      'DEFAULT'    : 'OEM1B',
      'OEM1B'      : {
            'ATI_SCRN'           : ['VBAR_ZN'],       # due to re-zone to lower capacity
            'BPINOMINAL'         : ['OPTIZAP_1'],
            'DNLD_BRG_IV'        : ['REDNLD_BRG_IV'],
            'DNLD_F3CODE'        : ['REDNLD_BRG_IV'],
            'PREVBAR_OPTI'       : ['PREVBAR_ZAP'],
            'PRE_OPTI'           : ['OPTIZAP_1'],
            'PV_SCRN'            : ['VBAR_ZN'],       # due to re-zone to lower capacity
            'READ_OPTI'          : ['VBAR_ZN'],       # due to re-zone to lower capacity
            'READ_XFER'          : ['WRITE_XFER'],
            'SP_RD_TRUPUT'       : ['SP_WR_TRUPUT'],
            'SPF'                : ['RZAP'],
            },
      'SBS'        : {
            'ATI_SCRN'           : ['VBAR_ZN'],       # due to re-zone to lower capacity
            'BPINOMINAL'         : ['OPTIZAP_1'],
            'DNLD_BRG_IV'        : ['REDNLD_BRG_IV'],
            'DNLD_F3CODE'        : ['REDNLD_BRG_IV'],
            'PES_SCRN'           : ['ZAP'],
            'PREVBAR_OPTI'       : ['PREVBAR_ZAP'],
            'PRE_OPTI'           : ['OPTIZAP_1'],
            'PV_SCRN'            : ['VBAR_ZN'],       # due to re-zone to lower capacity
            'READ_OPTI'          : ['VBAR_ZN'],       # due to re-zone to lower capacity
            'READ_XFER'          : ['WRITE_XFER'],
            'SP_RD_TRUPUT'       : ['SP_WR_TRUPUT'],
            'SP_RD_TRUPUT2'      : ['SP_WR_TRUPUT2'],
            ('ZEST',42174)       : ['MDW_CAL'],
            ('ZEST',42176)       : ['MDW_CAL'],
            'SPF'                : ['RZAP'],
            'SERVO_OPTI'         : ['INIT'],
            ('AFH1',14841)       : ['INIT'],
            'AFH2'               : ['INIT'],
            'RW_GAP_CAL'         : ['INIT'],
            'AGC_JOG'            : ['INIT'],
            ('INIT_SYS', 14501)  : ['INIT'],
            ('INIT_SYS', 10451)  : ['INIT'],
            },
   },
}
if testSwitch.FE_0365343_518226_SPF_REZAP_BY_HEAD:
   stateRerunParams['dependencies']['OEM1B'].update({'SPF' : ['SPF_REZAP']})
   stateRerunParams['dependencies']['SBS'].update({'SPF' : ['SPF_REZAP']})
if testSwitch.RD_SCRN2_FAIL_RERUN_ZAP:
   stateRerunParams['dependencies']['OEM1B'].update({'READ_SCRN2' : ['REZAP2']})

#if testSwitch.DEBUG_EC10129:
#   stateRerunParams['dependencies']['D_FLAWSCAN'] = ['VER_SIM1']

# Add error code to the list below to power cycle during state re-rerun.
pwrCycleRetryList = [10251,10666,11051,11226,11036,10502,11049,13420,13452,14026,14746,10569, 13426]

# Add error code into the list below, drive will auto downgrade by Manual_GOTF table.
downGradeECList = [10632,14635,14861]
# Add error code into the list below, drive will auto downgrade to STD directly.
downGradeSTDECList = [10632,14635,14861,14574]

downGradeSBSECList = []

# Add error code into the list below, drive will auto downgrade then rerun current state or rerun whole oper.
downGradeRerunParams = {
  'state' : {
     'HEAD_SCRN'          : [11126,10560],
     'HEAD_CAL'           : [48723],
     'MDW_CAL'            : [48723],
     'EAW_SCRN'           : [10468,],
     'OAR_SCREEN_ELT'     : [14612, 14613, 14614],
     'D_FLAWSCAN'         : [10291, 10277, 10463, 10479, 10482, 10504, 10546, 10547, 10548, 10591, 10623, 11049,11087],
     'READ_SCRN2H'        : [10632, 14574, 48448],
     'SETTLING'           : [10522,],
     'WEAK_WR_OW1'        : [48450,],
     'WEAK_WR_OW2'        : [48450,],
     'ZAP'                : [10463,10627],
     'RZAP'               : [10463,10627],
     },
  'oper' : {
     'HEAD_CAL'           : [11049, 11087],
     'SERVO_OPTI'         : [10137,11049, 11087],
     'MDW_CAL'            : [10427,11049, 11087],
     },
  'reCRT2' : {
     'WRITE_XFER'         : [10578,],
     'READ_XFER'          : [10578,],
     'INTFTTR'            : [13424,], #ATA Ready Failed
     'DEFECT_LIST'        : [13456,], #Failed Critical Event Log
     'SMART_DFT_LIST'     : [13456,],
     'CRITICAL_LOG'       : [13456,],
     },
  'statedepend' : {
     'ZEST'               : [42174, 42176],
     'WEAK_WR_DELTABER'   : [10340, 11049, 11087, 10566, 14805, 14806],
     'SERIAL_FMT'         : [10219, 10566, 48463, 42170, 14651, 13426],
     'SPF'                : [10463],     
     },
  'dependencies' : {
     'WEAK_WR_DELTABER'   : 'DNLD_CODE5',
     'SERIAL_FMT'         : 'DNLD_CODE5',
     'ZEST'               : 'MDW_CAL',
     'SPF'                : 'ZAP',
     },
}

#Skip checking of PCBA_SN if drive previously failed for below error code
SKIP_PCBA_SN_FAILCODE = [11075, 'DNLD_BRG_IV', "DNLD_CODE", "DNLD_CODE3", "SETUP_PROC"]

# ATI screen re-zone and re-vbar error codes
#if 'ATI_SCRN' in stateRerunParams['states']:
#   ATIScrnRezoneEC = stateRerunParams['states']['ATI_SCRN']


prm_TCG={
   'CORE_SPEC'          : (0x0002),      # 0x01 = Core Spec 1, 0x02 = Core Spec 2
   'SSC_VERSION'        : (0x0001),      # 0x00 = ENT_SSC,  0x01 = OPAL_SSC
   'MASTER_AUTHORITY'   : (0x0001),      # Authentication type: 1 = PSID and 0 = MSID
   'CHECK_ENCRYPTION'   : (0),           # Default should be 1 for encryption check , Org is 1 Ann 02 Oct
   'UNIFIED_F3'         : (0),           # Default should be 1 for NSG
   'TCGBandTest'        : (0),           # Default should be 1 for Band Test
   'CHECK_RNG'          : (1),           # Default should be 1 for Randam Number Generator check
   'numChallenge'       : (152),         # Default 152 - No. chanllenge(sample) collected for RNG check
   'lenRandomNum'       : (32),          # 32 (NOT ALLOWED TO CHANGE W/O CONSULTING TCG F3 team)
   'FDE_TYPE'           : 'FDE BASE',
   'SECURITY_TYPE'      : 'TCG OPAL 2 SED',
   #'IEEE1667_INTF'      : 'ACTIVATED',  # Do not set, this will be set by DCM
                                         # Not Applicable = IEEEE1667 Feature not Supported
                                         # Activated Allows Windows 8 to gain control of the SED functionality
                                         # Deactivated- Enforces that only 3rd party software can take control of the device
}

if testSwitch.WA_0134988_395340_RESET_TIMEOUT_THAT_REMAIN_ON_CPC:
   prm_506_RESET_RUNTIME = {
      'test_num'          : 506,
      'prm_name'          : "prm_506_SET_RUNTIME",
      'spc_id'            :  1,
      "TEST_RUN_TIME"     :  0,
   }

if testSwitch.LAUNCHPAD_RELEASE:
   if testSwitch.FE_0334158_379676_P_RFWD_FFV_1_POINT_5:
      TCG_DNLD_SEQ = ['TGT3','OVL3','IV3','TGT','OVL','TGT','OVL']
   else:
      TCG_DNLD_SEQ = ['TGT3','OVL3','IV3','TGT','OVL']
else:
   if testSwitch.FE_0334158_379676_P_RFWD_FFV_1_POINT_5:
      TCG_DNLD_SEQ = ['TGTB','OVLB','IV','TGT','OVL','CXM','TGT','OVL']
   else:
      TCG_DNLD_SEQ = ['TGTB','OVLB','IV','TGT','OVL','CXM']

#these are the pcba numbers that will use a lower bandwidth filter for servo. They are enabled using WA_0126043_426568_TOGGLE_SAPBIT_FOR_HIGH_BW_FILTER
pcba_nums = ['100609308','100609310','100611019','100611021','100621718','100621720', \
             # Trinidad PCBAs without RVFF sensors:
             '100603206','100603208','100603212','100603214','100603478','100603484','100617479','100617481', \
             '100620807','100620810','100622000','100622006','100622008','100622010','100622012','100622014', \
             '100622016','100624707','100626795','100630114','100591260','100591264','100591271','100591276']
overlayMap = {
   'ATTRIBUTE'                : 'nextOper',
   'DEFAULT'                  : 'PRE2',
   'PRE2'                     : 'S_OVL',
   'FIN2'                     : 'IO_OVL',
   'CMT2'                     : 'IO_OVL',
   'IOSC2'                    : 'IO_OVL',
   'CUT2'                     : 'IO_OVL',
}

MR_Bias_Backoff_62 = {
   'test_num'                 : 62,
   'prm_name'                 : "MR_Bias_Backoff_62",
   'spc_id'                   : 1,
   'CWORD1'                   : 0x0001,
   'HEAD_RANGE'               : 0xFFFF,
   'ZONE'                     : 0,
   'ZONE_POSITION'            : 198,
   'NUM_READS'                : 500,
   'TLEVEL'                   : 15,
   'LOOP_CNT'                 : 16,
   'DELTA_LIMIT'              : 25,
}

hdstr_tempCheck = {
   'test_num'                 : 172,
   'prm_name'                 : 'Check HDA Temp',
   'spc_id'                   : 1,
   'CWORD1'                   : 17,
   'timeout'                  : 100
}
##################### Seek Test #####################################

SeekTestCmdList = [
   {
      'test_num'                 : 30,
      'prm_name'                 : 'FwdSeqRdHd0Sk_30',
      'spc_id'                   : 10,
      'CWORD1'                   : (0x0011,),
      'START_CYL'                : (0x0001, 0x84AC),
      'END_CYL'                  : (0x0001, 0x8894),
      'BIT_MASK'                 : (0, 0),
      'PASSES'                   : (1),
      'TIME'                     : (0, 220, 20),
      'SEEK_DELAY'               : (10),
   },
   {
      'test_num'                 : 30,
      'prm_name'                 : 'RevSeqRdHd0Sk_30',
      'spc_id'                   : 11,
      'CWORD1'                   : (0x0012,),
      'START_CYL'                : (0x0001, 0x84AC),
      'END_CYL'                  : (0x0001, 0x8894),
      'BIT_MASK'                 : (0, 0),
      'PASSES'                   : (1),
      'TIME'                     : (0, 220, 20),
      'SEEK_DELAY'               : (10),
   },
   {
      'test_num'                 : 30,
      'prm_name'                 : 'FwdSeqWrtHd0Sk_30',
      'spc_id'                   : 15,
      'CWORD1'                   : (0x0021,),
      'START_CYL'                : (0x0001, 0x84AC),
      'END_CYL'                  : (0x0001, 0x8894),
      'BIT_MASK'                 : (0, 0),
      'PASSES'                   : (1),
      'TIME'                     : (0, 220, 20),
      'SEEK_DELAY'               : (10),
   },
   {
      'test_num'                 : 30,
      'prm_name'                 : 'RevSeqWrtHd0Sk_30',
      'spc_id'                   : 16,
      'CWORD1'                   : (0x0022,),
      'START_CYL'                : (0x0001, 0x84AC),
      'END_CYL'                  : (0x0001, 0x8894),
      'BIT_MASK'                 : (0, 0),
      'PASSES'                   : (1),
      'TIME'                     : (0, 220, 20),
      'SEEK_DELAY'               : (10),
   },
]


# HDSTR/ST240 Parameters

Pre_Hdstr_Oper = 'CAL2'                            # Operation before hdstr
hdstrTestFlags = {
   'Hdstr_In_Gemini'          : 'N',               #  Run HDSTR tests in Gemini rather than moving to HDSTR  Y/N
   'Hdstr_Delay_In_Mins'      : 400 * numHeads,    # Minutes to run
}

hdstrClrBuff = {
   'test_num'                 : 233,
   'prm_name'                 : "HDSTR Status Check",
   'CWORD1'                   : 0x5
} #begin record

hdstrRecord = {
   'test_num'                 : 233,
   'prm_name'                 : "HDSTR Status Check",
   'CWORD1'                   : 0x4
} #begin record

hdstrSave = {
   'test_num'                 : 233,
   'prm_name'                 : "HDSTR Status Check",
   'CWORD1'                   : 0x06
}

hdstrStopRecord = {
   'test_num'                 : 233,
   'prm_name'                 : "HDSTR Status Check",
   'CWORD1'                   : 0x02
}

hdstrStartImmediate = {
   'test_num'                 : 233,
   'prm_name'                 : "HDSTR Status Check",
   'CWORD1'                   : 0x0008
}

hdstrDisplayOutput = {
   'test_num'                 : 233,
   'CWORD1'                   : 0x3,
   'prm_name'                 : "Unload ST240 data",
   'timeout'                  : 4000
}

hdstrReadCmdFromDisc = {
   'test_num'                 : 233,
   'prm_name'                 : "HDSTR Status Check",
   'CWORD1'                   : 0x7
}

hdstrDisableAutoRun = {
   'test_num'                 : 233,
   'prm_name'                 : "HDSTR Status Check",
   'CWORD1'                   : 0xB
}

hdstrDefault = {
   'test_num'                 : 233,
   'prm_name'                 : "HDSTR Status Check",
   'CWORD1'                   : 0
}

hdstr_Enable_autoRun_1secDelay = {
   'test_num'                 : 233,
   'prm_name'                 : "HDSTR Status Check",
   'CWORD1'                   : 9,
   'INITIAL_DELAY'            : 10
}

hdstr_autoSeek_30 = {
   'test_num'                 : 30,
   'prm_name'                 : 'Long seeks to warm hda for testing',
   'spc_id'                   : 1,
   'CWORD1'                   : (0x0000,), #Seq forward and reverse = 0
   'TIME'                     : (0,1000,1000), #Warachai Suggest.
#   'TIME'                     : (1,1000,1000),
   'SEEK_DELAY'               : (0),
   'BIT_MASK'                 : (0,0),
   'START_CYL'                : (0,0x100),
   'END_CYL'                  : (0,0x5000),
   'PASSES'                   : (10),
   'timeout'                  : (200000),
}
hdstr_tempCheck = {
   'test_num'                 : 172,
   'prm_name'                 : 'Check HDA Temp',
   'spc_id'                   : 1,
   'CWORD1'                   : 17,
   'timeout'                  : 100
}

hdstr_recover_CAP = {
   'test_num'                 : 130,
   'prm_name'                 : 'Recover CAP to PC File',
   'spc_id'                   : 1,
   'CWORD2'	                  : 0x8080,
   'timeout'                  : 100000
}

hdstr_recover_SAP = {
   'test_num'                 : 130,
   'prm_name'                 : 'Recover SAP to PC File',
   'spc_id'                   : 1,
   'CWORD2'	                  : 0x8010,
   'timeout'                  : 100000
}

hdstr_recover_RAP = {
   'test_num'                 : 130,
   'prm_name'                 : 'Recover RAP to PC File',
   'spc_id'                   : 1,
   'CWORD2'	                  : 0x8040,
   'timeout'                  : 100000
}

hdstr_CAP_PCFile_to_Flash = {
   'test_num'                 : 178,
   'prm_name'                 : 'Copy CAP PCFile to Flash',
   'spc_id'                   : 1,
   'CWORD1'	                  : 0x0121,
   'timeout'                  : 100000
}

hdstr_SAP_PCFile_to_Flash = {
   'test_num'                 : 178,
   'prm_name'                 : 'Copy SAP PCFile to Flash',
   'spc_id'                   : 1,
   'CWORD1'	                  : 0x0421,
   'timeout'                  : 100000
}

hdstr_RAP_PCFile_to_Flash = {
   'test_num'                 : 178,
   'prm_name'                 : 'Copy RAP PCFile to Flash',
   'spc_id'                   : 1,
   'CWORD1'	                  : 0x0221,
   'timeout'                  : 100000
}
hdstr_Read_SAP_TABLE ={
   'test_num'                 : 172,
   'prm_name'                 : 'Read SAP Table',
   'spc_id'                   : 1,
   'CWORD1'	              : 0x0000,
   'timeout'                  : 500
}
hdstr_030_random_read = {
   'test_num'                 : 30,
   'prm_name'                 : 'hdstr_030_random_read',
   'timeout'                  : 2400 * numHeads,
   'spc_id'                   : 1,
   'CWORD1'                   : 0x0314,
   'START_CYL'                : (0x0000, 0x0000),
   'END_CYL'                  : (  0x2L, 0x49F0),
   'PASSES'                   : 0xFFFF,
   'TIME'                     : (0, 0xFFFF, 0xFFFF),
   'BIT_MASK'                 : (0, 0),
   'SEEK_DELAY'               : 0x0012,
   }
heatHDA_Seeks_prm = {
   'test_num'              : 30,
   'prm_name'              : 'SF3 random seeks to heat HDA',
   'spc_id'                : 1,
   'CWORD1'                : 0x0314, #random target random heads read seek
   'TIME'                  : (0, 0xffff, 0xffff),
   'PASSES'                : 0x9C0, #~30 seconds if seek time is 12ms
   'SEEK_DELAY'            : 1,
   'BIT_MASK'              : (0, 0),
   'START_CYL'             : (0, 0),
   'END_CYL'               : (0x1, 0),
   'timeout'               : 500,
   }
RapWordSyncMarcWindow = {
   'test_num':178,
   'prm_name':'RapWordSyncMarcWindow',
   'timeout':1000,
   'spc_id':1,
   'CWORD1'               : (0x0220,),
   'RAP_WORD': (0x1FD4, 0x22, 0xff), # Change Register 5C to 0x22 (Offset 0x1FD4 is base on current RAP 18-Oct-2012)
}

Bode_Scrn_Audit =  {
      'PN'        : ['9YN166', '9ZL162'],
      'SN_sampler': '0123456789ABCDEFGH'
   }

############################
##############   This is a example of how the preset TPI setting looks like. Note this might change when RAP
##############      changes its format about TPI table.
############################
if testSwitch.FE_0165107_163023_P_FIX_TPII_WITH_PRESET_IN_VBAR:
   TPIsettingPerDriveSN = {
       'Z1D00C4P' : [ [215,214,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 0
                      [208,210,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 1
                      [210,208,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 2
                      [207,209,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 3
                      [208,206,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 4
                      [207,205,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 5
                      [207,206,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 6
                      [207,204,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 7
                      [205,203,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 8
                      [208,203,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 9
                      [208,201,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 10
                      [207,200,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 11
                      [207,197,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 12
                      [206,201,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 13
                      [207,199,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 14
                      [208,199,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 15
                      [205,199,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 16
                      [207,199,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 17
                      [205,196,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 18
                      [204,198,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 19
                      [205,200,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 20
                      [204,200,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 21
                      [203,200,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 22
                      [198,200,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 23
                      [197,200,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 24
                      [198,198,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 25
                      [194,196,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 26
                      [194,197,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 27
                      [195,196,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 28
                      [196,196,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 29
                    ],

       'Z1D00C63' : [ [214,212,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 0
                      [210,208,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 1
                      [207,205,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 2
                      [206,203,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 3
                      [202,204,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 4
                      [200,202,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 5
                      [200,200,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 6
                      [205,197,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 7
                      [206,199,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 8
                      [204,193,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 9
                      [205,199,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 10
                      [205,199,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 11
                      [204,199,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 12
                      [204,199,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 13
                      [204,198,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 14
                      [198,197,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 15
                      [197,197,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 16
                      [197,197,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 17
                      [196,197,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 18
                      [198,193,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 19
                      [198,197,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 20
                      [196,196,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 21
                      [197,197,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 22
                      [197,197,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 23
                      [196,195,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 24
                      [198,197,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 25
                      [196,195,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 26
                      [197,195,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 27
                      [195,194,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 28
                      [196,195,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 29
                    ],

       'Z1D00C93' : [ [211,203,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 0
                      [207,199,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 1
                      [206,197,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 2
                      [207,196,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 3
                      [205,195,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 4
                      [204,194,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 5
                      [203,193,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 6
                      [204,192,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 7
                      [204,190,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 8
                      [203,191,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 9
                      [203,191,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 10
                      [203,192,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 11
                      [203,191,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 12
                      [203,191,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 13
                      [202,189,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 14
                      [202,190,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 15
                      [203,190,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 16
                      [201,189,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 17
                      [201,189,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 18
                      [201,190,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 19
                      [202,189,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 20
                      [202,188,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 21
                      [202,188,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 22
                      [201,188,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 23
                      [203,188,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 24
                      [201,187,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 25
                      [197,186,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 26
                      [196,187,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 27
                      [199,186,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 28
                      [199,188,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 29
                    ],

       'Z1D00C89' : [ [214,227,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 0
                      [209,222,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 1
                      [207,220,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 2
                      [208,219,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 3
                      [209,219,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 4
                      [207,217,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 5
                      [207,218,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 6
                      [207,217,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 7
                      [207,216,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 8
                      [203,217,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 9
                      [205,217,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 10
                      [204,215,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 11
                      [204,216,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 12
                      [205,215,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 13
                      [205,215,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 14
                      [204,215,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 15
                      [205,215,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 16
                      [203,215,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 17
                      [204,214,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 18
                      [203,214,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 19
                      [205,213,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 20
                      [205,212,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 21
                      [205,213,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 22
                      [205,212,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 23
                      [205,213,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 24
                      [204,212,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 25
                      [203,211,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 26
                      [203,211,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 27
                      [204,211,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 28
                      [203,212,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 29
                    ],

       'Z1D00CAS' : [ [206,207,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 0
                      [202,202,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 1
                      [200,199,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 2
                      [199,199,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 3
                      [197,197,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 4
                      [198,197,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 5
                      [198,195,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 6
                      [197,194,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 7
                      [196,194,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 8
                      [197,194,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 9
                      [200,193,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 10
                      [199,192,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 11
                      [199,194,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 12
                      [199,190,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 13
                      [198,192,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 14
                      [198,191,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 15
                      [198,192,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 16
                      [198,188,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 17
                      [198,189,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 18
                      [197,192,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 19
                      [197,194,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 20
                      [196,193,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 21
                      [196,194,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 22
                      [197,194,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 23
                      [196,195,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 24
                      [194,195,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 25
                      [196,192,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 26
                      [195,192,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 27
                      [195,192,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 28
                      [196,192,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 29
                    ],

       'Z1D00C57' : [ [221,225,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 0
                      [218,220,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 1
                      [215,218,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 2
                      [214,216,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 3
                      [215,218,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 4
                      [215,216,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 5
                      [215,216,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 6
                      [213,216,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 7
                      [212,215,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 8
                      [211,214,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 9
                      [211,212,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 10
                      [211,212,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 11
                      [209,212,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 12
                      [208,212,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 13
                      [208,212,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 14
                      [208,210,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 15
                      [209,210,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 16
                      [207,210,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 17
                      [208,209,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 18
                      [207,209,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 19
                      [207,211,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 20
                      [207,212,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 21
                      [208,212,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 22
                      [208,211,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 23
                      [206,211,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 24
                      [208,211,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 25
                      [206,207,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 26
                      [205,211,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 27
                      [205,211,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 28
                      [205,209,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   # zone 29
                    ],

   }
############################ Open Up DTH ########################################
OPEN_UP_HOT_TEMP_DTH = 65

############################ CTcc_BY_BER #########################################
from AFH_constants import AFH_ANGSTROMS_PER_MICROINCH
Maximum_TCC1_Step_allowed = {
    "ATTRIBUTE" : 'HGA_SUPPLIER',
    "DEFAULT" : 'RHO',
    "TDK" : 6,
    "RHO" : 6
}

Maximum_TCC1_Step_allowed_for_dec = {
   "ATTRIBUTE" : 'HGA_SUPPLIER',
   "DEFAULT"   : 'RHO',
   "TDK"       : 6,
   "RHO"       : 6
}
tcc1_step_size = {
    "ATTRIBUTE" : 'FE_0258915_348429_COMMON_TWO_TEMP_CERT',
    "DEFAULT" : 0,
    0 : 0.0001*AFH_ANGSTROMS_PER_MICROINCH,
    1 : 0.00007874*AFH_ANGSTROMS_PER_MICROINCH #2015/07/30,  recommended setting, ~0.02/step * 5 = 0.1 #0.0002*AFH_ANGSTROMS_PER_MICROINCH
}

tcc1_step_size_dec = {
    "ATTRIBUTE" : 'HGA_SUPPLIER',
    "DEFAULT" : 'RHO',
    "TDK" : {   (-100,0.1  ):0.0001*AFH_ANGSTROMS_PER_MICROINCH,
                (0.1 ,0.2  ):0.0002*AFH_ANGSTROMS_PER_MICROINCH,
                (0.2 ,0.3  ):0.0003*AFH_ANGSTROMS_PER_MICROINCH,
                (0.3 ,0.4  ):0.0004*AFH_ANGSTROMS_PER_MICROINCH,
                (0.4 ,0.5  ):0.0005*AFH_ANGSTROMS_PER_MICROINCH,
                (0.5 ,100.0):0.0006*AFH_ANGSTROMS_PER_MICROINCH,
            },
    "RHO" : {   (-100,0.1  ):0.0001*AFH_ANGSTROMS_PER_MICROINCH,
                (0.1 ,0.2  ):0.0002*AFH_ANGSTROMS_PER_MICROINCH,
                (0.2 ,0.3  ):0.0003*AFH_ANGSTROMS_PER_MICROINCH,
                (0.3 ,0.4  ):0.0004*AFH_ANGSTROMS_PER_MICROINCH,
                (0.4 ,0.5  ):0.0005*AFH_ANGSTROMS_PER_MICROINCH,
                (0.5 ,100.0):0.0006*AFH_ANGSTROMS_PER_MICROINCH,
            }
}

step_to_check_delta_ber = {
    "ATTRIBUTE" : 'HGA_SUPPLIER',
    "DEFAULT" : 'RHO',
    "TDK" : 4,
    "RHO" : 4
}

expected_minimun_ber_increase = {
    "ATTRIBUTE" : 'HGA_SUPPLIER',
    "DEFAULT" : 'RHO',
    "TDK" : 0.05,
    "RHO" : 0.05
}

if testSwitch.FE_0258915_348429_COMMON_TWO_TEMP_CERT:
   ber_spec = {
       "ATTRIBUTE" : 'HGA_SUPPLIER',
       "DEFAULT" : 'RHO',
       "TDK" : -2.6,
       "RHO" : -2.6
   }
else:
   ber_spec = {
       "ATTRIBUTE" : 'HGA_SUPPLIER',
       "DEFAULT" : 'RHO',
       "TDK" : -2.4,
       "RHO" : -2.4
   }

maximum_delta_writer_heat = {
    "ATTRIBUTE" : 'HGA_SUPPLIER',
    "DEFAULT" : 'RHO',
    "TDK" : 2, #2015/07/30,  recommended setting  #5,
    "RHO" : 2  #2015/07/30,  recommended setting  #5
}

delta_R2_R2A_ber = {
    "ATTRIBUTE" : 'HGA_SUPPLIER',
    "DEFAULT" : 'RHO',
    "TDK" : 1000,
    "RHO" : 1000
}
deltaC = 0.2
#if testSwitch.CHENGAI: # enable TCC reset
#   deltaC = 2.0  # open up for data collection  #0.2

if testSwitch.FE_0258915_348429_COMMON_TWO_TEMP_CERT:
   delta_R2H_R2_by_partnum = 0.4
   delta_R2C_R2_by_partnum = 0.2

else :
   #delta_R2C_R2_by_partnum = deltaC
   #delta_R2H_R2_by_partnum = 0.4
   delta_R2C_R2_by_partnum = 4.5
   delta_R2H_R2_by_partnum = 1.0
# dth adjust only for TWO_TEMP_CERT
dThAdjSpec = {
  'R2H_max_ber'      : {
     'ATTRIBUTE'          : "CAPACITY_PN",
     'DEFAULT'            : "750G",
     '1000G'               : 2.4,
     '750G'               : 2.7,},
  'R2H_R2C_delta_ber'     : {
     'ATTRIBUTE'          : "CAPACITY_PN",
     'DEFAULT'            : "750G",
     '1000G'               : 0.6,
     '750G'               : 0.9,},
  'Add_dth_high'     : {
     'ATTRIBUTE'          : "CAPACITY_PN",
     'DEFAULT'            : "750G",
     '1000G'               : 2.0,
     '750G'               : 2.0,},
  'Add_dth_low'     : {
     'ATTRIBUTE'          : "CAPACITY_PN",
     'DEFAULT'            : "750G",
     '1000G'               : 1.0,
     '750G'               : 1.0,},
  'Temp_refer'     : {
     'ATTRIBUTE'          : "CAPACITY_PN",
     'DEFAULT'            : "750G",
     '1000G'               : 65,
     '750G'               : 65,},
}


delta_R2C_bigger_than_R2 = {
    "ATTRIBUTE" : 'HGA_SUPPLIER',
    "DEFAULT" : 'RHO',
    "TDK" : delta_R2C_R2_by_partnum,
    "RHO" : delta_R2C_R2_by_partnum
}

delta_R2H_bigger_than_R2 = {
    "ATTRIBUTE" : 'HGA_SUPPLIER',
    "DEFAULT" : 'RHO',
    "TDK" : delta_R2H_R2_by_partnum,
    "RHO" : delta_R2H_R2_by_partnum
}
# Update TCC to Flash
save_to_flash = testSwitch.FE_0258915_348429_COMMON_TWO_TEMP_CERT

min_tcc_ber_limit_WTF = 10.0
if testSwitch.FE_0258915_348429_COMMON_TWO_TEMP_CERT:
   TCC_MIN_BER_NOT_COMPENSATED = 2.6

else:
    TCC_MIN_BER_NOT_COMPENSATED = 2.5



prm_errRateByZone={
   'test_num'              : 250,
   'prm_name'              : "prm_errRateByZone",
   'spc_id'                : 1,
   'timeout'               : 900, # extra pad- shud take 5 min/zone for ea pass
   'ZONE'                  : 0,
   'ZONE_MASK'             : (0L, 1),
   'ZONE_MASK_EXT'         : (0L, 0),
   'TEST_HEAD'             : 0,
   'TLEVEL'                : 0, # ECC off default
   'PERCENT_LIMIT'         : 0xFF, # turn on the consideration for non_converging code word
   'WR_DATA'               :(0x00),# 1 byte for data pattern if writing first
   "CWORD1"                : 0x09C1, # (0x0187,),
   'RETRIES'               : 50,
   'ZONE_POSITION'         : 198,
   'MAX_ERR_RATE'          : -80,
   'NUM_TRACKS_PER_ZONE'   : 10,
   'SKIP_TRACK'            : {
      'ATTRIBUTE'    : 'FE_0245014_470992_ZONE_MASK_BANK_SUPPORT',
      'DEFAULT'      : 0,
      0              : 200,
      1              : 20, #Zone 94, 110, 179 may have less than 200 tracks, so skip_track cannot remain at 200.
   },
   'MINIMUM'               : -10,
   'MAX_ITERATION'         : MaxIteration,
   'CWORD2'                : 0x801, # 5
}


##### end of CTcc_BY_BER ################

############## Pre heat screen parameter #############################################################################
prm_PREHEAT_ErrRate_250 = {
   'base': {
         'test_num'           : 250,
         'prm_name'           : 'prm_PREHEAT_ErrRate_250',
         'spc_id'             : 3000, ##33
         'timeout'            : 500*numHeads, # extra pad- shud take 5 min/zone for ea pass
         'ZONE_MASK'          : (0L, 1), #(255L, 65535),
         'ELT_REF_SECTOR'     : (5,25), #(start ref sector, end ref sector)
         'TEST_HEAD'          : 0xFF,
         'WR_DATA'            : (0x00),#(0x00) 1 byte for data pattern if writing first
         'ZONE_POSITION'      : 0,
         'MAX_ERR_RATE'       : -60,
         "CWORD1"             : (0x0183,), # CWORD1 setting applied in level 3 code
         "CWORD2"             : (0x0009,), #  0x21 or 0x41 /CWORD1 setting applied in level 3 code added T250_CWORD2_BY_START_CYL
         'NUM_TRACKS_PER_ZONE' : 1,
         'RETRIES'            : 50,       # supported from SF3 CL86949
         'SKIP_TRACK'            : {
            'ATTRIBUTE'    : 'FE_0245014_470992_ZONE_MASK_BANK_SUPPORT',
            'DEFAULT'      : 0,
            0              : 200,
            1              : 20, #Zone 94, 110, 179 may have less than 200 tracks, so skip_track cannot remain at 200.
         },
         'MINIMUM'            : 1, #Minimum BER spec 4.0
         'TLEVEL'             : 0,
         'MAX_ITERATION'      : MaxIteration, #  org is 0x705 iteration used to measure the sector error rate
         },
    'lowest_clr_limit'     : 10,
    'pct_limit'            : 0.9, # 90% of reference sectors
    'num_testtrack_perzone': 5, #number of test tracks per zone
}

###############################################################################################################
############## WGC (Write Gate Count parameter ################################################################
prm_Preheat = {
   'test_num'           : 253,
   'prm_name'           : 'prm_Preheat',
   'spc_id'             : 1,
   'timeout'            : 1800*numHeads,
   'ZONE_MASK'          : (65535L, 65535), #(16448L, 32913),
   'ZONE_MASK_EXT'      : (65535L, 65535), # Suport 60 zones
   'ELT_REF_SECTOR'     : (20,40), # ref codeword
   'PREHEAT_LIMIT'      : (90,90), # preheat linmit
   'TEST_HEAD'          : 0xFF,
   'WR_DATA'            : (0x00),#(0x00) 1 byte for data pattern if writing first
   'ZONE_POSITION'      : 0,
   'RD_ITERATION'       : 200, # number of read for data processing
   'LOW_CLR_LIMIT'      : 3,
   "CWORD1"             : (0x03,), # tune = 1, Preheat = 2, WGC = 4
}
prm_WGC = {
   'test_num'           : 253,
   'prm_name'           : 'prm_WGC',
   'spc_id'             : 1,
   'timeout'            : 1800*numHeads,
   'ZONE_MASK'          : (65535L, 65535), #(16448L, 32913),
   'ZONE_MASK_EXT'      : (65535L, 65535), # Suport 60 zones
   'ELT_REF_SECTOR'     : (0,20), # ref codeword
   'WGC_LIMIT'          : (85,85), # WGC linmit
   'TEST_HEAD'          : 0xFF,
   'WR_DATA'            : (0x00),#(0x00) 1 byte for data pattern if writing first
   'ZONE_POSITION'      : 0,
   'RD_ITERATION'       : 200, # number of read for data processing
   'LOW_CLR_LIMIT'      : 3,
   "CWORD1"             : (0x05,), # tune = 1, Preheat = 2, WGC = 4
}
###################################################################
#  Weak Write Scrn based on OverWrite
###################################################################
WeakWrOWPrm_61 = {
  'test_num':61,
  'prm_name':'WeakWrOWPrm_61',
  'timeout': 6000,
  'spc_id' : 1,
  "BAND_SIZE" : (7,),
  "HEAD_RANGE" : (0xFFFF,),
  "ZONE_POSITION" : (198,),
  'BIT_MASK'  : {
      'ATTRIBUTE':'numZones',
      'DEFAULT'   : 60,
      24: (0xff, 0xffff),
      31: (0x6003,0x0006),
      60: (0x0000,0x0001), #zone 1,2,31,32,58,59
        },
  "CWORD1" : ( 0x0001),
}
WeakWrOWPrm_61_FastIO_ORG = {
  'test_num':61,
  'prm_name':'WeakWrOWPrm_61_FastIO',
  'timeout': 60,
  'spc_id' : 1,
  "BAND_SIZE" : (7,),
  "HEAD_RANGE" : (0xFFFF,),
  "ZONE_POSITION" : (198,),
  "BIT_MASK" : (0x0000, 0x1001),
  "CWORD1" : ( 9 ),
  "READ_OFFSET" : (0,),
}

WeakWrOWPrm_61_FastIO = {
  'test_num':61,
  'prm_name':'WeakWrOWPrm_61_FastIO',
  'timeout': 1000,
  'spc_id' : 1,
  "BAND_SIZE" : (7,),
  "HEAD_RANGE" : (0xFFFF,),
  "ZONE_POSITION" : (198,),
  "BIT_MASK" : {
              'ATTRIBUTE'    : 'numZones',
              'DEFAULT'      : 31,
              24             : (0x00FF, 0xFFFF),
              31             : (0x7FFF, 0xFFFF),
              60             : (0xFFFF, 0xFFFF),
              },
  "BIT_MASK_EXT" : {
              'ATTRIBUTE'    : 'numZones',
              'DEFAULT'      : 31,
              24             : (0, 0),
              31             : (0, 0),
              60             : (0x0FFF, 0xFFFF),
              },
  "CWORD1" : ( 9 ),
  "READ_OFFSET" : (0,),
}




#HSC st190 setting of HSC_TCC_LT & HSC_TCC_HT
prm_190_HSC_TCC = {
   'test_num'               : 190,
   'prm_name'               : 'HSC_TCCtestprm',
   'timeout'                : 36000,
   'spc_id'                 : 1,
   'CWORD1'                 : {
      'ATTRIBUTE'          : 'nextState',
      'DEFAULT'            : 'default',
      'default'            : 0x1122,
      'HSC_TCC_LT'         : 0x1122,
      'HSC_TCC_HT'         : 0x1102,
   },
   'HEAD_RANGE'             : 0xFFFF,
   'BIT_MASK'               : (0x4040, 0x8081), #for FE_0245014_470992_ZONE_MASK_BANK_SUPPORT, bitmask not used
   'BIT_MASK_EXT'           : (0x4040, 0x8080), #for FE_0245014_470992_ZONE_MASK_BANK_SUPPORT, bitmask_ext not used
   'LOOP_CNT'               : 20,
   'FREQUENCY'              : 120,
   'THRESHOLD'              : 0,
   'ZONE'                   : {
      'ATTRIBUTE'          : 'FE_0245014_470992_ZONE_MASK_BANK_SUPPORT',
      'DEFAULT'            : 0,
      0                    : [],
      1                    : {
         'ATTRIBUTE'          : 'numZones',
         'DEFAULT'            : 180,
         120                  : [0,14,30,44,60,78,94,108,124],
         150                  : [0,18,38,55,75,98,118,135,155],
         180                  : [0,21,45,66,90,117,141,162,186],
      },
   },
}

Prm_190_Settling = {
   'test_num'               : 190,
   'prm_name'               : 'settlingtestprm',
   'timeout'                : 36000,
   'spc_id'                 : 1,
   'CWORD1'                 : 0x0002,
   'HEAD_RANGE'             : 0xFFFF,
   'BIT_MASK'               : (0x0000, 0x0001),
   'LOOP_CNT'               : 90,     # only place to control loop cnt ,90
   'FREQUENCY'              : 120,     #Prm_190["FREQUENCY"]
   'ZONE'                   : {
      'ATTRIBUTE'          : 'FE_0245014_470992_ZONE_MASK_BANK_SUPPORT',
      'DEFAULT'            : 0,
      0                    : [],
      1                    : {
         'ATTRIBUTE'          : 'numZones',
         'DEFAULT'            : 180,
         180                  : [0],
      },
   },
}

##### for VBAR ATI ##########
prm_VBAR_ATI_51 = {
      'base': {
         'test_num'                     : 51,
         'prm_name'                     : 'prm_VBAR_ATI_51',
         'spc_id'                       : 1,
         'timeout'                      : 18000,          # was 7200sec
         'CWORD1'                       : 0x0040 | testSwitch.USE_ZERO_LATENCY_WRITE_IN_T50_T51,       # SKIP_FLW_TBL_CHKS = 0x0040
         'ZONE_POSITION'                : 198,
         'ZONE'                         : [0],
         'TEST_HEAD'                    : 0,
         'TLEVEL'                       : {     # Default is 10 in SF3
            'ATTRIBUTE'                 : 'FE_0276349_228371_CHEOPSAM_SRC',
            'DEFAULT'                   : 1,
            0                           : 30,
            1                           : 40,
         },
         'RETRIES'                      : 0,           # Read retry cnt, default is 16 in SF3
         'RETRY_LIMIT'                  : 0xFF,        # Soft err threshold, default is 6 in SF3
         'BAND_SIZE'                    : 5,
         #'SET_OCLIM'                    : (493,),
         'CENTER_TRACK_WRITES'          : 3000,
         'MAX_TRK_OTF_ERRORS'           : 200,      # default = 0xFFFF, set to 400 to reduce testtime for poor tracks
         'BASELINE_CLEANUP_WRT_RETRY'   : 25,
         'CHANGE_SEEK_LENGTH_AND_RETRY' : 25,
         'MAX_ERR_RATE'                 : 873,
         },
      'ZONES' : {
         "EQUATION" : "TP.UMP_ZONE[self.dut.numZones]",
       },
      'ZONES_WITH_OD_POSITION' : {
         'ATTRIBUTE'                 : 'FE_0385234_356688_P_MULTI_ID_UMP',
         'DEFAULT'                   : 0,
         0                           : [4,5],
         1                           : [],
      },
      'ZONEPOS' : {
         "EQUATION" : "dict(zip(TP.UMP_ZONE[self.dut.numZones], [ (198, )for zn in TP.UMP_ZONE[self.dut.numZones]]))",
       },
      'ZONE_MAP': {
         "EQUATION" : "dict(zip(TP.UMP_ZONE[self.dut.numZones], [ (zn, )for zn in TP.UMP_ZONE[self.dut.numZones]]))",
      },
      'ZONE_FOR_COLLECTION': {
         'ATTRIBUTE'    :'FE_0267804_504159_P_VBAR_ATI_FOR_DATA_COLLECTION',
         'DEFAULT'      : 0,
         0              : [],
         1              : {
            "EQUATION"  : "TP.UMP_ZONE[self.dut.numZones]",
         },
      },
}

STE_THRESHOLD = 7.0 # Threshold to use when detecting STE head during VBAR ATI
TPIM_TO_BPIM_THRESHOLD = 0.16 # Threshold in TPIM to shift to BPIM instead for suspected STE issue
BPIM_FIX_BACKOFF = { # Fix BPI Backoff for UMP Zones
      'ATTRIBUTE'          : 'FE_0285640_348429_VBAR_STE_BACKOFF_BPI',
      'DEFAULT'            : 0,
      0                    : 0.08,
      1                    : 0.00000001, # Use Tuned Value
   }
BPIM_BACKOFF = 0.16 # Backoff in BPIM when an STE issue is detected for UMP Zones
BPIM_BACKOFF_SMR = 0.08 # Backoff in BPIM when an STE issue is detected for SMR Zones
STE_BACKOFF_ZONES = []#[0,1,2,3] # Zones to Backoff for SMR Zones
STEEP_ATI_THRESHOLD = 0.5 # OTF BER per 1% Margin, if degradation in OTF is more than this, additional backoff will be imposed

# For VBAR STE
prm_VBAR_STE_51 = {
   'CENTER_TRACK_WRITES'          : 10000,
   }

#########  VBAR TPI Margin Threshold (TMT) Scaler ##########
Otf_TmtScaler = [
   {"OtfBerLowerLimit": 0.0, "OtfBerUpperLimit": 5.5,  "TmtScaler": 0.00,},
   {"OtfBerLowerLimit": 5.5, "OtfBerUpperLimit": 6.0,  "TmtScaler": 0.14,},
   {"OtfBerLowerLimit": 6.0, "OtfBerUpperLimit": 6.5,  "TmtScaler": 0.43,},
   {"OtfBerLowerLimit": 6.5, "OtfBerUpperLimit": 7.0,  "TmtScaler": 0.72,},
   {"OtfBerLowerLimit": 7.0, "OtfBerUpperLimit": 10.0, "TmtScaler": 1.00,},
]

Default_TmtScale = 0.0

TPIAdjustDuringVBART51 = { # for Adjusting the Start Offset when measuring VBAR T51
      'ATTRIBUTE': 'HGA_SUPPLIER',
      'DEFAULT'  : 'RHO',
      'TDK'      : 0,
      'RHO'      : 0,
}
OffsetAdjustDuringVBART51 = { # for Adjusting the the next Offset when OTF BER is very good on the Start Offset
      'ATTRIBUTE': 'HGA_SUPPLIER',
      'DEFAULT'  : 'RHO',
      'TDK'      : 0.0,
      'RHO'      : 0.0,
}
#########  END VBAR TPI Margin Threshold (TMT) Scaler ##########

# calcThruput param
cylSkew = {
   'ATTRIBUTE' : 'programName',
   'DEFAULT'   : 'default',
   'default'   : 0x22,
   'Rosewood7' : 0x1E,   
}

prm_display_cylSkew = {
   'test_num'               : 172,
   'prm_name'               : 'prm_display_cylSkew',
   'spc_id'                 : 1,
   'timeout'                : 100,
   'CWORD1'                 : 64,
}

# Prevent FIN2 WR_VERIFY from running Serial Port throughput
RWSerialTruputOper = None

# Files to allow reading of PCBA SN in Boot Mode (default in ReadPCBASN_Boot.zip)
PCBA_SN_BOOT_FILES = ['STPM_CheopsAM_ReadSN_827435.txt','STPM_CheopsLite_LiteM_ReadSN.txt','STPM_KarnakPlus_ReadSN_674292.txt', 'STPM_KarnakA_ReadSN.txt', 'STPM_Karnak_ReadSN.txt', 'STPM_LM94V2_ReadSN.txt', 'STPM_LM94_ReadSN.txt', 'sertpm_CL388538_Bsm_PcbaHda.txt', 'sertpm_CL388538_LxM93_PcbaHda.txt', 'sertpm_CL391611_BsSt2_PcbaHda.txt']
if testSwitch.CHEOPSAM_LITE_SOC:
   PCBA_SN_BOOT_FILES[0], PCBA_SN_BOOT_FILES[1] =  PCBA_SN_BOOT_FILES[1], PCBA_SN_BOOT_FILES[0]

prm_speedLookup_override = [(3,3), (1,1.5),]


#--------- ATI DOS threshold settings ---------#
prm_setDOSATISTEThreshold_by_BG = {
   'test_num'           : 178,
   'prm_name'           : 'prm_setDOSATISTEThreshold',
   'spc_id'             : 1,
   'timeout'            : 600,         # Extra pad - should take 5 min/zone per pass
   'HEAD_RANGE'         : 0x3ff,  # Head mask, 3 means set both 2 heads
   'C_ARRAY1'           : {
      "ATTRIBUTE"    : "CAPACITY_CUS",
      "DEFAULT"      : "1000G_OEM1B",
      "1000G_OEM1B"  : [0, 30, 0, 0, 0, 0, 0, 40, 2, 0x04], #[0, 30, 0, 0, 0, 0, 0,STERange,STEThresholdScalar,ATIThresholdScalar], 0xff is default value
      "1000G_STD"    : [0, 30, 0, 0, 0, 0, 0, 40, 2, 0x04],
      "750G_OEM1B"   : [0, 30, 0, 0, 0, 0, 0, 40, 2, 0x04],
      "750G_STD"     : [0, 30, 0, 0, 0, 0, 0, 40, 2, 0x04],
   },
}

if testSwitch.SMRPRODUCT :

   prm_setDOSATISTEThreshold_by_BG_FAT = {
      'test_num'                 : 178,
      'prm_name'                 : 'prm_setDOSATISTEThreshold_FAT',
      'spc_id'                   : 1,
      'timeout'                  : 600,         # Extra pad - should take 5 min/zone per pass
      'HEAD_RANGE'               : 0x3ff,  # Head mask, 3 means set both 2 heads
      'C_ARRAY1'                 : {
         "ATTRIBUTE"          : "FE_0276349_228371_CHEOPSAM_SRC",
         "DEFAULT"            : 1,
         0                    : {
            "ATTRIBUTE"    : "CAPACITY_CUS",
            "DEFAULT"      : "1000G_OEM1B",
            "1000G_OEM1B"  : [0, 35, 0, 0, 0, 0, 0, 40, 0, 0x04], #[0, 30, 0, 0, 0, 0, 0,STERange,STEThresholdScalar,ATIThresholdScalar], 0xff is default value
            "1000G_STD"    : [0, 35, 0, 0, 0, 0, 0, 40, 0, 0x04], #[0, 30, 0, 0, 0, 0, 0,STERange,STEThresholdScalar,ATIThresholdScalar], 0xff is default value
            "750G_OEM1B"   : [0, 35, 0, 0, 0, 0, 0, 40, 0, 0x04], #[0, 30, 0, 0, 0, 0, 0,STERange,STEThresholdScalar,ATIThresholdScalar], 0xff is default value
            "750G_STD"     : [0, 35, 0, 0, 0, 0, 0, 40, 0, 0x04], #[0, 30, 0, 0, 0, 0, 0,STERange,STEThresholdScalar,ATIThresholdScalar], 0xff is default value
         },
         1                    : {
            "ATTRIBUTE"    : "CAPACITY_CUS",
            "DEFAULT"      : "1000G_OEM1B",
            "1000G_OEM1B"  : [0, 35, 0, 0, 0, 0, 0, 40, 2, 0x05], #[0, 30, 0, 0, 0, 0, 0,STERange,STEThresholdScalar,ATIThresholdScalar], 0xff is default value
            "1000G_STD"    : [0, 35, 0, 0, 0, 0, 0, 40, 2, 0x05], #[0, 30, 0, 0, 0, 0, 0,STERange,STEThresholdScalar,ATIThresholdScalar], 0xff is default value
            "750G_OEM1B"   : [0, 35, 0, 0, 0, 0, 0, 40, 2, 0x05], #[0, 30, 0, 0, 0, 0, 0,STERange,STEThresholdScalar,ATIThresholdScalar], 0xff is default value
            "750G_STD"     : [0, 35, 0, 0, 0, 0, 0, 40, 2, 0x05], #[0, 30, 0, 0, 0, 0, 0,STERange,STEThresholdScalar,ATIThresholdScalar], 0xff is default value
         },
      },
   }

   prm_setDOSATISTEThreshold_by_BG_SLIM = {
      'test_num'              : 178,
      'prm_name'              : 'prm_setDOSATISTEThreshold_SLIM',
      'spc_id'                : 1,
      'timeout'               : 600,         # Extra pad - should take 5 min/zone per pass
      'HEAD_RANGE'            : 0x3ff,  # Head mask, 3 means set both 2 heads
      'C_ARRAY1'              : {
         "ATTRIBUTE"    : "CAPACITY_CUS",
         "DEFAULT"      : "1000G_OEM1B",
         "1000G_OEM1B"  : [0, 36, 0, 0, 0, 0, 0, 40, 2, 0x09], #[0, 30, 0, 0, 0, 0, 0,STERange,STEThresholdScalar,ATIThresholdScalar], 0xff is default value
         "1000G_STD"    : [0, 36, 0, 0, 0, 0, 0, 40, 2, 0x09], #[0, 30, 0, 0, 0, 0, 0,STERange,STEThresholdScalar,ATIThresholdScalar], 0xff is default value
         "750G_OEM1B"   : [0, 36, 0, 0, 0, 0, 0, 40, 2, 0x09], #[0, 30, 0, 0, 0, 0, 0,STERange,STEThresholdScalar,ATIThresholdScalar], 0xff is default value
         "750G_STD"     : [0, 36, 0, 0, 0, 0, 0, 40, 2, 0x09], #[0, 30, 0, 0, 0, 0, 0,STERange,STEThresholdScalar,ATIThresholdScalar], 0xff is default value
      },
   }

prm_AdaptiveDOS_Table = {
 'NeedToScanThreshold' : 8192,
 'TRK_INDEX' : [-1, 1],  #define trk index on which to collect OTF performance
 'ATI_Threshold_Table' : {
 1024 : {  # DOS ATI Scan Threshold
    # number of writes in ATI test :  (min_OTF, max_OTF) is the OTF performance band.
    10000 : (0, 7.501),
    5000  : (0, 8.001),
   },
 2048 : {
    10000 : (7.502, 8.001),
    5000  : (8.002, 8.501),
   },
 4096 : {
    10000 : (8.002, 100),
    5000  : (8.502, 100),
   },
 },
}
prm_setDOSATISTEThreshold_by_ATI = {
    'test_num'              : 178,
    'prm_name'              : 'prm_setDOSATISTEThreshold',
    'spc_id'                : 1,
    'timeout'               : 600,         # Extra pad - should take 5 min/zone per pass
    'HEAD_RANGE'            : 0x3ff,  # Head mask, 3 means set both 2 heads
    'C_ARRAY1'              : { #[0, 30, 0, 0, 0, 0, 0,STERange,STEThresholdScalar,ATIThresholdScalar], 0xff is default value
        "ATTRIBUTE"   : "CAPACITY_CUS",
        "DEFAULT"     : "1000G_OEM1B",
        "1000G_OEM1B" : [0, 30, 0, 0, 0, 0, 0, 40, 0, 0xff],
        "1000G_STD"   : [0, 30, 0, 0, 0, 0, 0, 40, 1, 0xff],
        "750G_OEM1B"  : [0, 30, 0, 0, 0, 0, 0, 40, 1, 0xff],
        "750G_STD"    : [0, 30, 0, 0, 0, 0, 0, 40, 1, 0xff],
    },
}

prm_getDOSATISTEThreshold = {
    'test_num'              : 172,
    'prm_name'              : 'prm_getDOSATISTEThreshold',
    'spc_id'                : 1,
    'timeout'               : 600,
    'CWORD1'                : 33,
    'C_ARRAY1'              : [0, 30, 0, 0, 0, 0, 0, 0, 0, 0],
    }
prm_getDOSATISTEThreshold_fat = {
    'test_num'              : 172,
    'prm_name'              : 'prm_getDOSATISTEThreshold_fat',
    'spc_id'                : 1,
    'timeout'               : 600,
    'CWORD1'                : 33,
    'C_ARRAY1'              : [0, 35, 0, 0, 0, 0, 0, 0, 0, 0],
    }
prm_getDOSATISTEThreshold_slim = {
    'test_num'              : 172,
    'prm_name'              : 'prm_getDOSATISTEThreshold_slim',
    'spc_id'                : 1,
    'timeout'               : 600,
    'CWORD1'                : 33,
    'C_ARRAY1'              : [0, 36, 0, 0, 0, 0, 0, 0, 0, 0],
    }
prm_setCAPRemapZone = {
   'test_num'    : 178,
   'prm_name'    : "prm_setCAPRemapZone",
   'timeout'     :900,
   'CAP_WORD'    :(0x0076,0xFF16,0xFF), # Set Zone Remap Destination to after Zone 16h
   "CWORD1"      : 288,
}

prm_dispCAP ={
   'test_num'    : 172,
   'prm_name'    : "prm_dispCAP",
   'timeout':100,
   'dlfile': None,
   "CWORD1"    : 1,
}



if testSwitch.VBAR_CHECK_IMBALANCED_HEAD:
   ImbalancedHeadLimit = 0.20

### Skip Zone ###
SkipZn_Ver = 100 #0.03
SkipZn_Un  = 100 #0.7

#####################EWAC/WPE/OTC####################################
####################### EWAC #################################
ewacCword1 = 0x01
T61OW_byZone_Limit_OEM = 21
T61OW_byZone_Limit_SBS = 20
T61OW_byZone_Limit = {
     "ATTRIBUTE"     : "CAPACITY_CUS",
     "DEFAULT"       : "1000G_OEM1B",
     "1000G_OEM1B"   : T61OW_byZone_Limit_OEM,
     "1000G_STD"     : T61OW_byZone_Limit_SBS,
     "750G_OEM1B"    : T61OW_byZone_Limit_OEM,
     "750G_STD"      : T61OW_byZone_Limit_SBS,
}
T61SMROW_Limit = 15
# cword1 to be used by prm_wpe defined inside base_TestParameter
wpeCword1 = 0x2
if testSwitch.FE_0247196_334287_FIXED_WP_FQ_ET:
   wpeCword1 |= 0x10

MrvlSymbTable ={
    # Key                           : [REG_ADDR, MASK, St, Len], St: starting bit of the regsiter, Len: length of the key
    "CSM_START"                     : [ 0x00A, 0x00FF,   8,  8],
    "CSM_ON"                        : [ 0x00E, 0x3FFF,  14,  2],
    "CSM_ACC_RBACK_SRC"             : [ 0x00E, 0xDFFF,  13,  1],
    "CSM_RST_NXT_RG"                : [ 0x00E, 0xFFBF,   6,  1],
    "CSM_RST_MODE"                  : [ 0x00E, 0xFFEF,   4,  1],
    "CSM_STOP_MODE"                 : [ 0x00E, 0xFFF7,   3,  1],
    "CSM_TRIG_SRC"                  : [ 0x00E, 0xFFFD,   1,  1],
    "CSM_STOP"                      : [ 0x012, 0xF000,   0,  12],
    "CSM_ACC_LSB"                   : [ 0x014, 0x0000,   0,  16],
    "CSM_ACC_MSB"                   : [ 0x016, 0x0000,   0,  16],
    "D_CTF_AUTOGM_DIS"              : [ 0x01A, 0xFEFF,   8,  1],
    "D_CTF_FCO"                     : [ 0x01A, 0xFF0F,   4,  4],
    "D_CTF_BST"                     : [ 0x01C, 0xFFC0,   0,  6],
    "D_CTF_DACSEL"                  : [ 0x01E, 0xC0FF,   8,  6],
    "D_CTF_FIXGM"                   : [ 0x01E, 0xFFDF,   5,  1],
    "D_CTF_GMSEL"                   : [ 0x01E, 0xFFE0,   0,  5],
    "D_FIR_C1"                      : [ 0x020, 0x00FF,   8,  8],
    "D_FIR_C0"                      : [ 0x020, 0xFF00,   0,  8],
    "D_FIR_C3"                      : [ 0x022, 0x00FF,   8,  8],
    "D_FIR_C2"                      : [ 0x022, 0xFF00,   0,  8],
    "D_FIR_C5"                      : [ 0x024, 0x00FF,   8,  8],
    "D_FIR_C4"                      : [ 0x024, 0xFF00,   0,  8],
    "D_FIR_C7"                      : [ 0x026, 0x00FF,   8,  8],
    "D_FIR_C6"                      : [ 0x026, 0xFF00,   0,  8],
    "D_FIR_C9"                      : [ 0x028, 0x00FF,   8,  8],
    "D_FIR_C8"                      : [ 0x028, 0xFF00,   0,  8],
    "D_FIR_COEFF_INIT"              : [ 0x02A, 0x7FFF,  15,  1],
    "D_FIR_COEFF_INIT_ACLR"         : [ 0x02A, 0xBFFF,  14,  1],
    "D_FIR_COEFF_RBACK"             : [ 0x02A, 0xDFFF,  13,  1],
    "D_FIR_ADAPT_EN"                : [ 0x02A, 0xEFFF,  12,  1],
    "D_FIR_COEFF_MASK[9:8]"         : [ 0x02A, 0xFCFF,  8,   2],
    "D_FIR_COEFF_MASK[7:0]"         : [ 0x02A, 0xFF00,  0,   8],
    "D_FIR_F3B_FIX"                 : [ 0x02C, 0x7FFF,  15,  1],
    "D_FIR_F3A_FIX"                 : [ 0x02C, 0xFF7F,   7,  1],
    "D_TBG_N"                       : [ 0x048, 0xFF00,   0,  8],
    "D_TL_PH2"                      : [ 0x050, 0xF0FF,   8,  4],
    "D_TL_TE_BYPASS_TBL"            : [ 0x050, 0xFF7F,   7,  1],
    "D_TL_ACQ_ONLY"                 : [ 0x050, 0xFFBF,   6,  1],
    "D_TL_PH1"                      : [ 0x050, 0xFFF0,   0,  4],
    "D_TL_FRQ2"                     : [ 0x050, 0x0FFF,  12,  4],
    "D_TL_ZPS_LEN"                  : [ 0x052, 0xCFFF,  12,  2],
    "D_TL_FT"                       : [ 0x052, 0xFF0F,   4,  4],
    "D_TL_PT"                       : [ 0x052, 0xFFF0,   0,  4],
    "D_SEQ_LFSM1_DLY"               : [ 0x05A, 0x80FF,   8,  7],
    "D_SEQ_FSM1_DLY"                : [ 0x05E, 0xE0FF,   8,  5],
    "D_IZ_NORMZ"                    : [ 0x060, 0x0FFF,  12,  4],
    "D_IZ_AZZ"                      : [ 0x062, 0xFFF0,   0,  4],
    "D_AGC_GINIT"                   : [ 0x068, 0x7FFF,  15,  1],
    "D_AGC_ACQ_BW"                  : [ 0x068, 0xF3FF,  10,  2],
    "D_AGC_TRK_BW"                  : [ 0x068, 0xFCFF,   8,  2],
    "D_AGC_MODE"                    : [ 0x06C, 0xF8FF,   8,  3],
    "D_AGC_GAIN_FREEZE_EN"          : [ 0x070, 0x7FFF,  15,  1],
    "D_AGC_GAIN_FREEZE_THR"         : [ 0x070, 0x9FFF,  13,  2],
    "D_AGC_GAIN_OFFSET_DN"          : [ 0x070, 0xFF0F,   4,  4],
    "D_AGC_GAIN_OFFSET_UP"          : [ 0x070, 0xFFF0,   0,  4],
    "BSL_MU2_SEL"                   : [ 0x074, 0xFFCF,   4,  2],
    "S_SEQ_SG_EXT_EN"               : [ 0x0F6, 0x7FFF,  15,  1],
    "D_NLD_EST_ADAPT_EN"            : [ 0x10C, 0xFF7F,   7,  1],
    "D_WREF_FSEL"                   : [ 0x12A, 0xFFC0,   0,  6],
    "D_FORCE_SM1_FND"               : [ 0x12C, 0xFF7F,   7,  1],
    "D_RW_MODE"                     : [ 0x136, 0xFFF8,   0,  3],
    "HSC_FSEL2"                     : [ 0x162, 0xFF0F,   4,  4],
    "HSC_FSEL1"                     : [ 0x162, 0xFFF0,   0,  4],
    "HSC_SRC"                       : [ 0x164, 0x7FFF,  15,  1],
    "HSC_SIN_COS"                   : [ 0x164, 0xBFFF,  14,  1],
    "HSC_OUT_SEL"                   : [ 0x164, 0xEFFF,  12,  1],
    "D_CTF_FIXDAC"                  : [ 0x206, 0xFF7F,   7,  1],
    "D_ASC_ATTEN"                   : [ 0x260, 0x80FF,   8,  7],
    "D_ASC_ASCV"                    : [ 0x260, 0xFFE0,   0,  5],
    "D_ASC_ADAPT_EN"                : [ 0x262, 0x7FFF,  15,  1],
    "D_ASC_INIT"                    : [ 0x262, 0xFF7F,   7,  1],

    "R032"                          : [ 0x32,  0xFFF8,   0,  3],
    "R045044"                       : [ 0x44,  0xFFFF,   0,  16],
    "R047046"                       : [ 0x46,  0x0000,   0,  16],
    "R048"                          : [ 0x48,  0xFF00,   0,  8],
    "R053"                          : [ 0x52,  0x00FF,   8,  8],
    "R06C"                          : [ 0x6C,  0xFF00,   0,  8],
    "R06A"                          : [ 0x6A,  0xFF00,   0,  8],
    "R045"                          : [ 0x44,  0x00FF,   8,  8],

}


bpi_config = {
              0:	19,
              1:	23,
              2:	27,
              3:	31,
              4:	37,
              5:	43,
              6:	49,
              7:	59,
              8:	68,
              9:	73,
              10:	82,
              11:	94,
              12:	101,
              13:	113,
              14:	126,
              15:	138,
              16:	148,
              17:	164,
              18:	176,
              19:	191,
              20:	206,
              21:	223,
              22:	120,
              23:	120,
             }

ewac_test_track = 100
ewac_test_head  = 0
wpe_test_track  = 100
wpe_test_head   = 0



#OW table: 	1600KFCI 	1700KFCI 	1800KFCI 	1900KFCI


ROW_bpi_config1 = {
              0:	149,
              1:	143,
              2:	139,
              3:	136,
              4:	133,
              5:	130,
              6:	128,
              7:	128,
              8:	124,
              9:	120,
              10:	120,
              11:	122,
              12:	119,
              13:	120,
              14:	120,
              15:	120,
              16:	119,
              17:	124,
              18:	120,
              19:	120,
              20:	120,
              21:	123,
              22:	123,
              23:	126,
             }


ROW_bpi_config2 = {
              0:	174,
              1:	169,
              2:	166,
              3:	162,
              4:	158,
              5:	156,
              6:	152,
              7:	154,
              8:	149,
              9:	145,
              10:	146,
              11:	146,
              12:	143,
              13:	146,
              14:	146,
              15:	144,
              16:	143,
              17:	148,
              18:	146,
              19:	145,
              20:	147,
              21:	149,
              22:	149,
              23:	151,
             }


ROW_bpi_config3 = {
              0:	201,
              1:	196,
              2:	191,
              3:	188,
              4:	185,
              5:	181,
              6:	178,
              7:	179,
              8:	175,
              9:	171,
              10:	171,
              11:	172,
              12:	168,
              13:	171,
              14:	171,
              15:	169,
              16:	168,
              17:	173,
              18:	169,
              19:	171,
              20:	172,
              21:	172,
              22:	173,
              23:	176,
             }

ROW_bpi_config4 = {
              0:	228,
              1:	223,
              2:	217,
              3:	213,
              4:	211,
              5:	206,
              6:	204,
              7:	204,
              8:	199,
              9:	194,
              10:	196,
              11:	198,
              12:	193,
              13:	196,
              14:	195,
              15:	194,
              16:	192,
              17:	198,
              18:	194,
              19:	197,
              20:	196,
              21:	198,
              22:	198,
              23:	201,
             }


#######################################################################################
###################################################################
# SPT GIO parameter settings based on GIO Package : GIO_CST_18CVM
###################################################################
prm_GIOSettings={
    'IDT IntfTimeout'    :  10000,      # DT set to NSG spec
    'IDT SerialTimeout'  :  10000,
    'IDT Loops'          :  1,
    'IDT Oper'           :  'CST2',     # DT change to CST2 from IDT2
    'IDT Type'           :  'Normal',
    'IDT Temp'           :  50,
    'IDT Hot Temp'       :  50,
    'IDT Ambient Temp'   :  22,
    'IDT N2 Ambient Temp'   :  25,
    'IDT 48 Bit LBAs'    :  'ON',
    'IDT Ready Limit'    :  10000,      # TTR DT set to NSG spec
    'IDT Wrt Xfer'       :  100,
    'IDT Wrt Xfer Limit' :  0.8,
    'IDT Rd Xfer'        :  100,
    'IDT Rd Xfer Limit'  :  0.8,
    'IDT Hold Drive'     :  'Y',        # DT 180510 Hold drive flag for restart
    'IDT Hold Time'      :  72,
    'IDT 5vMargin'       :  0.05,
    'IDT 12vMargin'      :  0.10,
}

if 0:
   # serial port IDT_MS_SUS_TXFER_RATE offset
   MSSTR_WROD_OFFSET = -9.156
   MSSTR_RDOD_OFFSET = -12.620
   MSSTR_WRID_OFFSET = 0.0
   MSSTR_RDID_OFFSET = -3.527

if testSwitch.ROSEWOOD7 and testSwitch.IS_2D_DRV == 1: #For RW2D
   # serial port customer MSTR offset (based on RD07 MBC1 (Microsoft Code) AA6979 / A5F4)
   CSTR_WROD_OFFSET = -7.83
   CSTR_RDOD_OFFSET = -4.62
   CSTR_WRID_OFFSET = 0.89
   CSTR_RDID_OFFSET = -3.04

# SPMQM_Module, ON_OFF, Options:
#     SPMQM_EC - force error code if there is any failure in module
#     DISABLE_CELL - disable cell (automation) prior to running test module, eg "0"
#     NUM_RETRY - number of retries if module fails
#Flow based on MQM_UNF22B2

prm_GIOVersion = {"GIOVer" : 'RW7LC_3.20'} #Unified MQM modules for RWLC1D and RWLC2D
prm_GIOModules = [  ('IDT_WRITE_DRIVE_ZERO'       , 'OFF', {"SPMQM_EC": "13091", "OPS_CAUSE": "SPMQM_WDZ"}),
                    ('IDT_FULL_DST_IDE'           , 'OFF', {"SPMQM_EC": "13069", "OPS_CAUSE": "SPMQM_FDI"}),
                    ('IDT_RANDOM_WRITE_TEST'      , 'ON', {"SPMQM_EC": "13086", "OPS_CAUSE": "SPMQM_RWT"}),
                    ('IDT_FULL_DST_IDE'           , 'ON', {"SPMQM_EC": "13069", "OPS_CAUSE": "SPMQM_FDI"}),
                    ('IDT_BEATUP_WR_RD'           , 'OFF', {"SPMQM_EC": "13351", "OPS_CAUSE": "SPMQM_BWR"}),
                    ('IDT_FULL_DST_IDE'           , 'OFF', {"SPMQM_EC": "13069", "OPS_CAUSE": "SPMQM_FDI"}),
                    ('IDT_WRITE_DRIVE_ZERO'       , 'ON', {"SPMQM_EC": "13091", "OPS_CAUSE": "SPMQM_WDZ"}),
                    ('IDT_FULL_DST_IDE'           , 'ON', {"SPMQM_EC": "13069", "OPS_CAUSE": "SPMQM_FDI"})]



#WTFRerunParams = {
#     'states'        : {
#                     'READ_OPTI' : [14635, 10632],
#                     'ATI_SCRN'  : [14635, 10632],
#                     },
#    }


prm_sp_wr_truput = {
   'spc_id'       :  1,
   'rwMode'       :  1,       # 0=Read 1=write
   'zoneNumber'   :  None,    # None=All Zones
   'headNumber'   :  None,    # None=All Heads
   'cylSkew'      :  '',      # Default cyl skew
   'headSkew'     :  '',      # Default head skew
   'zoneSkew'     :  '',      # Default zone skew
   'skewStepSize' :  '',      # Default skew step size
   #'transfLen'    :  '8',     # Transfer Length In Tracks
   #'transfLen'    :  '1E0',    # Transfer Length In Tracks (blank is default 8 tracks)
   'transfLen'    :  'FF',    # Transfer Length In Tracks (blank is default 8 tracks)
   'transfOffset' :  '',      # Transfer Offset In Tracks
   'maxRetries'   :  '',      # Max Number of Retries
   'rwTracing'    :  False,   # Enable read write tracing
   'SkipWrBefRd'  :  1,       # bit 14: set=skip write for read throughput test, cleared=write before read
   'LimitTxLen'   :  True,    # If transfLen exceeds drive, use MaxTransfLen automatically
   'timeout'      :  3000,    # Max timeout 50 mins
   'TruputOffset' : [0.0, 0.0], # offset for first and last zone
   }

if testSwitch.SMRPRODUCT:
   prm_sp_wr_truput.update({
      'transfLen'    :  '8',    # Transfer Length In bands (blank is default 8 bands)
   })

prm_sp_rd_truput = {
   'spc_id'       :  2,
   'rwMode'       :  0,       # 0=Read 1=write
   'zoneNumber'   :  None,    # None=All Zones
   'headNumber'   :  None,    # None=All Heads
   'cylSkew'      :  '',      # Default cyl skew
   'headSkew'     :  '',      # Default head skew
   'zoneSkew'     :  '',      # Default zone skew
   'skewStepSize' :  '',      # Default skew step size
   'transfLen'    :  '8',     # Transfer Length In Tracks
   #'transfLen'    :  '1E0',    # Transfer Length In Tracks (blank is default 8 tracks)
   #'transfLen'    :  'FF',    # Transfer Length In Tracks (blank is default 8 tracks)
   'transfOffset' :  '',      # Transfer Offset In Tracks
   'maxRetries'   :  '',      # Max Number of Retries
   'rwTracing'    :  False,   # Enable read write tracing
   'SkipWrBefRd'  :  1,       # bit 14: set=skip write for read throughput test, cleared=write before read
   'LimitTxLen'   :  True,    # If transfLen exceeds drive, use MaxTransfLen automatically
   'timeout'      :  3000,    # Max timeout 50 mins
   'TruputOffset' : [0.0, 0.0], # offset for first and last zone
   }
prm_sp_wr_truput2 = prm_sp_wr_truput.copy()
prm_sp_wr_truput2['spc_id'] = 3
prm_sp_rd_truput2 = prm_sp_rd_truput.copy()
prm_sp_rd_truput2['spc_id'] = 4

if testSwitch.ROSEWOOD7:
   prm_FINModules = {
      'ATTRIBUTE': 'BG',
      'DEFAULT'  : 'OEM1B',
      'OEM1B'    : {
         'ATTRIBUTE': 'FPW_PRIOR_TO_FIN2_LONGDST',
         'DEFAULT'  : 1,
         1          : [
            ('IDT_WRITE_DRIVE_ZERO'       , 'ON', {"SPMQM_EC": "13091", "OPS_CAUSE": "SPMQM_WDZ"}),
            ('IDT_FULL_DST_IDE'           , 'ON'),
            ('IDT_VERIFY_SMART_IDE'       , 'OFF'),
            ('IDT_GET_SMART_LOGS'         , 'ON'),
            ('IDT_VERIFY_SMART_ONLY'      , 'ON'),
            ('IDT_RESET_SMART'            , 'ON'),
            ('IDT_CHECK_SMART_ATTR'       , 'ON'),
            ('IDT_SERIAL_SDOD_TEST'       , 'OFF')
            ],
         0          : [
            ('IDT_FULL_DST_IDE'           , 'ON'),
            ('IDT_VERIFY_SMART_IDE'       , 'OFF'),
            ('IDT_GET_SMART_LOGS'         , 'ON'),
            ('IDT_VERIFY_SMART_ONLY'      , 'ON'),
            ('IDT_RESET_SMART'            , 'ON'),
            ('IDT_CHECK_SMART_ATTR'       , 'ON'),
            ('IDT_SERIAL_SDOD_TEST'       , 'OFF')
            ],
         },
      'SBS'      : [
         ('IDT_FULL_DST_IDE'           , 'ON', {'NUM_RETRY':1}),
         ('IDT_VERIFY_SMART_IDE'       , 'OFF'),
         ('IDT_GET_SMART_LOGS'         , 'ON'),
         ('IDT_VERIFY_SMART_ONLY'      , 'ON'),
         ('IDT_RESET_SMART'            , 'ON'),
         ('IDT_CHECK_SMART_ATTR'       , 'ON'),
         ('IDT_SERIAL_SDOD_TEST'       , 'OFF')
         ], 
      }
   
else:
   prm_FINModules = [
     ('IDT_SHORT_DST_IDE'          , 'ON'),
     ('IDT_GET_SMART_LOGS'         , 'ON'),
     ('IDT_VERIFY_SMART_IDE'       , 'OFF'),
     ('IDT_VERIFY_SMART_ONLY'      , 'ON'),
     ('IDT_RESET_SMART'            , 'ON'),
     ('IDT_CHECK_SMART_ATTR'       , 'ON'),
     ('IDT_SERIAL_SDOD_TEST'       , 'OFF')
    ]

prm_IOMQM_Modules =  []

# Powerloss Recovery Init State Setting
# if Powerloss Recovery Saved State == 'CurrentState' then jump to 'NextState'
# instead of actual state saved in Drive Marshall during Power Trip

PwrLossInitState = {
   'FNC2':   {
              'SPMQM'   : {'NextState': 'SERIAL_FMT', 'SPMQM_Module': 'IDT_PM_ZONETHRUPUT'}
             },

   'FIN2':   {
              'SDOD'    : {'NextState': 'CCVMAIN'},
              'END_TEST': {'NextState': 'CCVMAIN'},
              'COMPLETE': {'NextState': 'CCVMAIN'},
             },
   }

####################### Joint Lab tests #################################

prm_T296_Data = {
   'test_num'     : 296,
   'prm_name'     : "prm_T296_Data",
   'timeout'      : 9000,
   'PATTERN_IDX'  : 0,
   'ZONE_POSITION': 40,
   'ZONE'         : 4,
   'MAX_ERR_RATE' : 2500,
   'NUM_READS'    : 10,
   'TRGT_READS'   : 10000,
   'SET_OCLIM'    : 0,
   'HEAD_RANGE'   : 255,
   'CWORD1'       : 0, # 0x8000 to turn on debug print.
   'FAIL_SAFE'    : (),
}

prm_320_OTC_Measure = {
    'test_num'      : 320,
    'prm_name'      : "prm_320_OTC_Measure",
    'timeout'       : 72000,
    'SQZ_OFFSET'    : 0,
    'ZONE_POSITION' : 10,
    'ZONE'          : 0,
    'HEAD_RANGE'    : 255,
    'ITERATIONS'    : 10,
    'NUM_SQZ_WRITES': 6,
    'CWORD1'        : 0, #0xc000 to turn on debug print.
    'THRESHOLD'     : 39, #Not use
    'RETRY_LIMIT'   : 1,
    'PERCENT_LIMIT' : 1,
    'PERCENT_LIMIT2': 1,
}

prm_337 = {
    'test_num'   : 337,
    'prm_name'   : "prm_337_Reverse_Overwrite",
    'timeout'    : 10000,
    'HEAD_MASK'  : 3,
    'ZONE_MASK'  : (0x4000, 0x4001),
    'LOOP_CNT'   : 16,
    'CWORD1'     : 4,
}

#==============================================================================#
# Single Pass Flaw Scan Params
#==============================================================================#
# NOTES:
# 1. Need to review settings again for SMR drive!
#==============================================================================#
T2108_BIE_FACTOR = 1
T2108_BIE = 592

prm_SPFS_WRITE_2108 = {
   'test_num'           : 2108,
   'prm_name'           : 'prm_SPFS_WRITE_2108',
   'timeout'            : {
      'ATTRIBUTE'  : 'FE_0241396_505235_FLAWSCAN_POWER_LOSS_RECOVERY',
      'DEFAULT'    : 0,
      0            : 3600 * 3 * numHeads,   # 3hrs per head
      1            : 3600 * 6,
      },
   'spc_id'             : 1,
   "CWORD1"             : 0x0006,
   "CWORD2"             : 0x0800,
   "CWORD4"             : 0x2000,
   "HEAD_RANGE"         : 0x00FF,
   "START_CYL"          : (0x0000,0x0000),
   "END_CYL"            : (0xFFFF,0xFFFF),
   "RW_MODE"            : 0x0040,
   "HEAD_CLAMP"         : 2000,
   "ZONE_LIMIT"         : 50000,
   "TRACK_LIMIT"        : 5,
   "SFLAW_OTF"          : (),
   "ERRS_B4_SFLAW_SCAN" : 1,
   "SET_OCLIM"          : {
      'ATTRIBUTE'  : 'BG',
      'DEFAULT'    : 'OEM1B',
      'OEM1B'      : 5,
      'SBS'        : 2,
      },
}

prm_SPFS_READ_2108 = {
   'test_num'           : 2108,
   'prm_name'           : 'prm_SPFS_READ_2108',
   'timeout'            : {
      'ATTRIBUTE'  : 'FE_0241396_505235_FLAWSCAN_POWER_LOSS_RECOVERY',
      'DEFAULT'    : 0,
      0            : 3600 * 3 * numHeads,   # 3hrs per head
      1            : 3600 * 6,
      },
   'spc_id'             : 1,
   "CWORD1"             : 0x0052,
   "CWORD2"             : 0x0A80,
   "CWORD4"             : 0x202A,
   "HEAD_RANGE"         : 0x00FF,
   "START_CYL"          : (0x0000, 0x0000),
   "END_CYL"            : (0xFFFF, 0xFFFF),
   "RW_MODE"            : 0x2000,
   "HEAD_CLAMP"         : 600,
   "BAD_WEDGE_LIMIT"    : {
      'ATTRIBUTE'  : 'BG',
      'DEFAULT'    : 'OEM1B',
      'OEM1B'      : 6,       # Defective sectors per track limit (CA for RW2D Relia). Skip the track & save TA ver to DBI if limit exceeded. 
      'SBS'        : 16,      # Default value from SF3
      },
   "TRACK_LIMIT"        : {
      'ATTRIBUTE'  : 'BG',
      'DEFAULT'    : 'OEM1B',
      'OEM1B'      : 30,      # Verified defects per track limit (CA for RW2D Relia). Skip the track & save TA ver to DBI if limit exceeded.
      'SBS'        : 80,
      },
   "ZONE_LIMIT"         : 65000,
   "PASS_INDEX"         : 0x0000,
   "FSB_SEL"            : (0x0428,0x0000),
   "VERIFY_GAMUT"       : (2,3,10),
   "SFLAW_OTF"          : (),
   "IGNORE_UNVER_LIMIT" : (),
   "WINDOW"             : 0x0099,
   "WINDOW_2"           : 0x1F2F,
   "SID_QM_THRESH"      : (T2108_BIE * T2108_BIE_FACTOR,) * 4,
   "SID_QM_CONTROL"     : (0x0444,0x01A0,0x0D00,0x0D00),
   "SET_XREG00"         : (0x1215, 0x0008, 0x21FC), # ZGRDIFF=10; mmspflaw_sel_2
   "SET_XREG01"         : (0x12B7, 0x0020, 0x2180), # GWIN_THRSH_TRK=0x15 mmspflaw_sel_1
   "SET_XREG02"         : (0x129A, 0x0010, 0x2184), # ZGS_THRSHR=12 (Check with Jim why he is changing this to 5)
   "OFFSET"             : 0x00C8, #offset to biethreshold
   "RETRY_COUNTER_MAX"  : 0x0A,
   "SET_OCLIM"          : {
      'ATTRIBUTE'  : 'BG',
      'DEFAULT'    : 'OEM1B',
      'OEM1B'      : 5,
      'SBS'        : 2,
      },
}

if testSwitch.MARVELL_SRC:
   T2108_BIE_FACTOR = 2
   prm_SPFS_READ_2108.update({
      #=== FSB selection
      "FSB_SEL"     : {         # (0xD8B0, 0x0001)
         'ATTRIBUTE' : ('FE_0280868_348432_MEDIA_DEFECT_DETECTOR', 'FE_228371_DETCR_TA_SERVO_CODE_SUPPORTED'),
         'DEFAULT'   : (0,0),
         (0,0)       : (0x0000,0x0000),
         (0,1)       : (0x0020,0x0002),
         (1,0)       : (0x0004,0x0002),
         (1,1)       : (0x0024,0x0002),  # EC Drop Out, (0x0200,0x0000), Preamble (0x0000,0x0002)
      },                                 # DLD ERR flag (0x1000,0x0000)
      #=== MDD
      # Only MDD0 is enabled.
      "MDD_CONTROL" : (0x01, 0x01),             # (MDDEN, MDDLLREN)
      "MDD_TDO"     : (0x0A, 0x0F, 0x0A),       # (MDD0TDO,MDD1TDO,MDD2TDO)
      "MDD_TDI"     : (0x3F, 0x3F, 0x3F),       # (MDD0TDI,MDD1TDI,MDD2TDI)
      "MDD_WSEL"    : (0x00, 0x02, 0x00),       # (MDD0WSEL,MDD1WSEL,MDD2WSEL)
      "MDD_QLFWIN"  : (0x03, 0x03, 0x02),       # Qualifier Window size for MDD0,MDD1,MDD2
      "MDD_QLFTHR"  : (0x08, 0x08, 0x0A),       # Qualifier Window Threshold for MDD0,MDD1,MDD2
      #=== DLD
      # DLD is enabled.  DLD ERR detector: BIT12
      "SET_XREG00"  : (0x0230, 0x0001, 0x2100), # R230[0] or D_DLD_VMM_EN
      "SET_XREG01"  : (0x0230, 0x0001, 0x2133), # R230[3] or D_DLD_ERR_EN
      "SET_XREG02"  : (0x0232, 0x0001, 0x2176), # R232[7:6] or D_DLD_ERR_MODE
      "SET_XREG03"  : (0x0232, 0x0001, 0x2198), # R232[9:8] or D_DLD_ERR_WIN_LEN
      "SET_XREG04"  : (0x0232, 0x000F, 0x2150), # R232[5:0] or D_DLD_MSE_THR
      #=== TA
      # TA detection is disabled.
      "SET_XREG05"  : { # R206[1] or TA_DET_EN
         'ATTRIBUTE' : 'FE_228371_DETCR_TA_SERVO_CODE_SUPPORTED',
         'DEFAULT'   : 0,
         0       : (0x0206, 0x0000, 0x2133),
         1       : (0x0206, 0x0001, 0x2133),
      },
      #Control Sync Mark Threshold
      "SET_XREG06"  : (0x0117, 0x0001, 0x21DC), # R117[13:12] or D_HNT_SM1_NORM_THR
      "SET_XREG07"  : (0x0117, 0x0002, 0x2196), # R117[9:6] or D_SM1_BB_HQ_THR
      #Control Iteration Cnt threshold
      "SET_XREG08"  : (0x4088, 0x0001, 0x20BB), # SID Register 0x4088 BCI_EMASK1_LO[11:11] iters_cnt_mask
      "SET_XREG09"  : (0x408A, 50, 0x20B0),     # SID Register 0x408A BCI_EMASK2_LO[11:0] icnt_thres
      #Control Logging of Non converged sector into SLE
      "SET_XREG10"  : (0x408A, 0x0001, 0x20FF), # SID Register 0x408A BCI_EMASK2_LO[15:15] cf_mask
      #Control Logging of sector with LLI Status greater than 0xD into SLE
      "SET_XREG11"  : (0x4088, 0x0001, 0x2066), # SID Register 0x4088 BCI_EMASK1_LO[11:11] lli_wr_mask
      "SET_XREG12"  : (0x4088, 0x000D, 0x2030), # SID Register 0x4088 BCI_EMASK1_LO[3:0] lli_thres
      #Settings for EC Drop Out Threshold: EC DROP-OUT: BIT9
      "SET_XREG13"  : (0x0214, 0x0001, 0x2133), # R214h D_EC_WIN_SIZE_SEL 0: 14 Bits, 1: 30 Bits
      "SET_XREG14"  : (0x0214, 0x000C, 0x21FC), # R214h D_EC_THR EC Threshold, a lower value results in higher sensitivity
      #"SET_XREG15"  : (0x0215, 0x0039, 0x21E8), # R215h D_EC_UPPER_THR (for Drop-In)
      "SET_XREG15"  : (0x0215, 0x000F, 0x2160), # R215h D_EC_LOWER_TH (for Drop-Out)
      #Settings for STT_D_DEFECT_IN_PREAMBLE: BIT17
      "SET_XREG16"  : (0x0345, 0x0002, 0x21FE), # R215h D_PRE_TSD_AD1_WIN (Preamble)
      "SET_XREG17"  : (0x0345, 0x0038, 0x21D7), # R215h D_PRE_TSD_DO1_THR (Preamble)
      #"SET_XREG18"  : (0x0346, 0x0001, 0x21FE), # R215h D_PRE_TSD_AD2_WIN (Preamble)
      #"SET_XREG19"  : (0x0345, 0x0030, 0x21D7), # R215h D_PRE_TSD_DO2_THR (Preamble)
      "SET_XREG20"  : (0x00AC, 0x007F, 0x21E8), # R0AFh DFS_TA_THR (TA)
      #=== BIE
      "SID_QM_THRESH" : (0x0DAC,) * 4,
      "MAX_ITERATION" : 0x4F, #79
   })

# Disable FSB. (CWORD4[5])
if testSwitch.SPFS_DISABLE_FSB:
   prm_SPFS_READ_2108["CWORD4"] &= (~(1 << 5) & 0xFFFF)
   prm_SPFS_READ_2108["FSB_SEL"] = (0x0000, 0x0000)

# Disable EVM/ Miscomp. (CWORD2[6])
if testSwitch.SPFS_DISABLE_EVM:
   prm_SPFS_READ_2108["CWORD2"] |= (1 << 6)

# Enable Adaptive BIE
if testSwitch.FE_0272568_358501_P_ADAPTIVE_BIE_IN_SPF:
   prm_SPFS_READ_2108["CWORD4"] |= (1 << 7)

# Enable Setup List when NPCal is disabled.
if testSwitch.ENABLE_NPCAL_OFF_SETUP_IN_SPF:
   prm_SPFS_READ_2108["CWORD4"] |= (1 << 4)

########## CGTWrite ##########
Display_BER   = 1
T042_WRITE_GT = 0x0002
prm_GTWrite = {
   'test_num'                 : 42,
   'prm_name'                 : 'prm_GTWrite',
   'CWORD1'                   : T042_WRITE_GT,
   'timeout'                  : 600,   
   'RETRIES'                  : 10,
   'OFFSET'                   : 256,
   'SEEK_DELAY'               : 20,   # delay
   'PATTERN_BYTE'             : 0xCCCC,
   'SET_OCLIM'                : 1228,
   'DEBUG_PRINT'              : 1,   
}
prm_onTrkber250 = {
   'test_num'      : 250,
   'prm_name'      : 'prm_onTrkber250',
   'RETRIES'       : 50,
   'MAX_ERR_RATE'  : -80,
   'SKIP_TRACK'    : 20,
   'WR_DATA'       : 0,
   'PERCENT_LIMIT' : 255,
   'ZONE_POSITION' : 0,
   'spc_id'        : 1,
   'TEST_HEAD'     : 255,
   'NUM_TRACKS_PER_ZONE': 1,
   'TLEVEL'        : 0,
   'MINIMUM'       : {
     "ATTRIBUTE"       : "CAPACITY_CUS",
     "DEFAULT"         : "1000G_OEM1B",
     "1000G_OEM1B"     : {'EQUATION' : "int(TP.min_ber_spec_oem * 10)"},
     "1000G_STD"       : {'EQUATION' : "int(TP.min_ber_spec_sbs * 10)"},
     "750G_OEM1B"      : {'EQUATION' : "int(TP.min_ber_spec_oem * 10)"},
     "750G_STD"        : {'EQUATION' : "int(TP.min_ber_spec_sbs * 10)"},
   },
   'timeout'       : 1800 * numHeads,
   'MAX_ITERATION' : 255,
   'CWORD2'        : (0x0800,),
   'CWORD1'        : 0x0981,
}

########## Variable Spares ##########
# control for tighten and relax spec update, otherwise use open spec
T230_Tighten       = 1 # allow to tighten
T230_Relax         = 0 # allow to relax
T230_NativeOnly    = 0 # adjust spare on native drive only
# param from T250
T250_prm        = prm_quickSER_250_RHO.copy()
T250_cword1     = {"EQUATION"     : "TP.prm_quickSER_250['CWORD1'] | 0x4000",}
T250_cword2     = {"EQUATION"     : "TP.prm_quickSER_250['CWORD2'][0]",}
CMR_MinErrRate  = {"EQUATION"     : "int(TP.prm_quickSER_250['MINIMUM'] * (-10))",}
SMR_MinErrRate  = {"EQUATION"     : "int(TP.MIN_SOVA_SQZ_WRT * (-10))",}
prm_230_VarSpares = {
   'test_num'           : 230,
   'prm_name'           : 'prm_230_VarSpares',
   'timeout'            : 10800,
   'CWORD1'             : 0x8033, # turn off BPI margin check # | (testSwitch.FE_0319957_356688_P_STORE_BPIP_MAX_IN_SIM << 9),  # use T250, don't run internal RWGap cal, check bpi margin when switch turn on
   #'CWORD1'             : 0x801B,  # use T088
   #   uint16 UpdateRapInFlash             : 1;  //    :0: Update RAP in FLASH \,
   #   uint16 ScaleDbiLog                  : 1;  //    :1: Scale the DBI Log for the new BPI \,
   #   uint16 SimScaleDbiLog               : 1;  //    :2: **Debug Only!!** Simulate (do not save) the Scaling of the DBI Log for the new BPI \,
   #   uint16 RunGapCal                    : 1;  //    :3: Run Gap Cal \,
   #   uint16 WriteGb                      : 1;  //    :4: Write Guardbands \,
   #   uint16 runT250                      : 1;  //    :5:  \,
   #   uint16 CheckSList                   : 1;  //    :6: Use Servo Flaw List \,
   #   uint16 CalcSpare                    : 1;  //    :7: Calculate spare \,
   #   uint16 FailBER                      : 1;  //    :8: return fail if BER not meet\,
   #   uint16 CheckBpiMargin               : 1;  //    :9: check bpi margin\,
   #   uint16 Reserved_10_14               : 5;  //    :10-14: \,
   #   uint16 QMonBER                      : 1;  //    :15: QMON BER Mode for Error Rate Measurement if supported \,
   'ZONE_POSITION'      : 198,
   'DEBUG_PRINT'        : 0x48,     # 0x6E
   #   uint16 RptSortedErrRate             : 1;   //    :0: Report Sorted Error Rate for each new BER \,
   #   uint16 RptEachStep                  : 1;   //    :1: Report info for each step \,
   #   uint16 RptFreqAndWdgSz              : 1;   //    :2: Report wedge size and frequency for each step \,
   #   uint16 RptScalingCapacity           : 1;   //    :3: Report Scaling Capacity \,
   #   uint16 RptAllZnErr                  : 1;   //    :4: End Report Error Rate for all zones \,
   #   uint16 RptDbiScaling                : 1;   //    :5: Report DBI Scaling info \,
   #   uint16 RptGapDeltaTable             : 1;   //    :6: Report GapDeltaTable\,
   #   uint16 RptEachMeasBER               : 1;   //    :7: Report measure BER in detail\,
   #   uint16 RptBpipMax                   : 1;   //    :8: Report BPIP_MAX from SIM for all zones\,
   #   uint16 RptEndMargin                 : 1;   //    :9: Report end Bpi margin\,
   #   uint16 Reserved_10_15               : 6;   //    :10-15:  \,
   'MAX_ERROR'          : 3,
   'RETRY_INCR'         : T250_prm['RETRIES'],    # 50,
   'SECTOR_SIZE'        : 4096,
   'NUM_SAMPLES'        : T250_prm['NUM_TRACKS_PER_ZONE'], # 10,
   'BIT_MASK'           : (65535, 65535),         # Used to exclude zones, like zone 0
   'BIT_MASK_EXT'       : (4095, 65535),
   'BPI_MAX_PUSH_RELAX' : 2,                      # Used to limit the number of BPI Profile changes per head/zone. Default 2
   'AVAILABLE_SPARES'   : (0, 0),
   'DELTA_LIMIT_32'     : (0xffff, 0xffff),
   'GAP_TRANS_OFFSET'   : 3000,
   'TLEVEL'             : MaxIteration,
   'SUPERPARITY_PER_TRK': 2,
   'MAX_BPI_ADJ'        : 0,                      # 0 - no limit
   'PI_BYTE'            : 0,
   'SKIP_TRACK'         : T250_prm['SKIP_TRACK'], # T250_SKIP_TRACK
   'MINIMUM'            : 10,                     # BER variation, add to tighten BER limit, /-100.0
   ### on trk or sqz write control of t250 ###
   'MIN_ERR_RATE'       : CMR_MinErrRate,         # 200/-100.0
   'CMR_MIN_ERR_RATE'   : CMR_MinErrRate,         # 200/-100.0
   'NUM_SQZ_WRITES'     : 0,                      # 0: on trk write, 1: SQZ_WRITE
   'MAX_ERR_RATE'       : -80,                    # -80: on trk write, -90: SQZ_WRITE, -80: for TTR
   'CWORD3'             : T250_prm['CWORD1'],
   'CWORD4'             : T250_cword2,
}
if testSwitch.SMR:
   prm_230_VarSpares.update({
      'MIN_ERR_RATE'       : SMR_MinErrRate,    # 190/-100.0
      'NUM_SQZ_WRITES'     : 1,                 # 0: on trk write, 1: SQZ_WRITE
      'CWORD3'             : T250_cword1,       # 0x49C1,
      })
if (prm_230_VarSpares['CWORD1'] & 0x0020 == 0):  # use T088, not T250
   prm_230_VarSpares.update({
      'prm_name'           : 'prm_230_VarSpares_T088',
      'OD_OFFSET'          : 0,
      'TARGET_TRK_WRITES'  : 1,
      'NUM_SQZ_WRITES'     : 0,
      'NUM_TRKS_AVERAGED'  : 3,
      'SQZ_OFFSET'         : 0,
      'REVS'               : 1,
      })
   
if testSwitch.FE_0319957_356688_P_STORE_BPIP_MAX_IN_SIM:
   prm_230_VarSpares.update({
      'DELTA_LIMIT'        : 9,      # if(Bpip+DELTA_LIMIT)>= bpipMax_hd_zn[head][zone], then don't allow tighten BPI, /10000.0
      'DEBUG_PRINT'        : 0x348,  # 0x3EF,
      })
   
prm_230_ChkSpareAval = {
   'test_num'           : 230,
   'prm_name'           : 'prm_230_ChkSpareAval',
   'timeout'            : 200 * numHeads,
   'CWORD1'             : 0x00a0,
   'SECTOR_SIZE'        : 4096,
   'AVAILABLE_SPARES'   : (0, 0),
   'DELTA_LIMIT_32'     : (0, 0),
   'DEBUG_PRINT'        : 0,
   'PI_BYTE'            : 0,
}

prm_107_DEFECT_LIST_SUMMARY = {
   'test_num'              : 107,
   'prm_name'              : 'prm_107_DEFECT_LIST_SUMMARY',
   'timeout'               : 6000,
   'CWORD1'                : 256,
   'DblTablesToParse'      : ['P2109_DEFECT_LIST_SUMMARY'],
   }

prm_rap_tuned_param_172 = {
   'test_num'           : 172,
   'prm_name'           : 'prm_rap_tuned_param_172',
   'timeout'            : 1000,
   'CWORD1'             : 19,
   'REG_ADDR'           : 13,
}
########## end: Variable Spares ##########

######### APO #########
prm_F3_APO_delta_BER = {
   'Zones'      : {
      'ATTRIBUTE'    : 'numZones',
      'DEFAULT'      : 31,
      31             : [1, 15, 30],
      60             : [min(UMP_ZONE[60])],# VC advice
      120            : [min(UMP_ZONE[120])],# follow 60 zone
      150            : [min(UMP_ZONE[150])],# follow 60 zone
      180            : [min(UMP_ZONE[180])],# follow 60 zone
   },
   'SectorStep' : 5,
   'FailSafe'   : 1,
}

################### NAND Screen ###################
#Current Spec as recommended by MunKai
prm_NAND_SCREEN = {
   'ATTRIBUTE' : 'NandVendor',
   'DEFAULT'   : 'dafault',
   'dafault'   : {
                  'BAD_CLP_CNT' : 40,
                  'RETIRED_CLP_CNT' : 1,
                  'MAX_MLC_EC' : 1000,
                  'MAX_SLC_EC' : 3000,
                  },
   'Samsung'   : {
                  'BAD_CLP_CNT' : 40,
                  'RETIRED_CLP_CNT' : 1,
                  'MAX_MLC_EC' : 1000,
                  'MAX_SLC_EC' : 3000,
                  },
   'MicronONFI3'   : {
                  'BAD_CLP_CNT' : 30,
                  'RETIRED_CLP_CNT' : 1,
                  'MAX_MLC_EC' : 1000,
                  'MAX_SLC_EC' : 3000,
                  },
   'ToshibaA19'   : {
                  'BAD_CLP_CNT' : 70,
                  'RETIRED_CLP_CNT' : 1,
                  'MAX_MLC_EC' : 1000,
                  'MAX_SLC_EC' : 3000,
                  },
   'Toshiba15nm'  : {
                  'BAD_CLP_CNT' : 70,
                  'RETIRED_CLP_CNT' : 1,
                  'MAX_MLC_EC' : 1000,
                  'MAX_SLC_EC' : 3000,
                  },
}

################### Clear NAND flash on Recycle PCBA ###################
HDALessTxtName = 'RY_Hybrid_SpecialTPM.txt'
HDALessBinName = 'RY_Hybrid_Headerless.BIN'

#########################Part Num Info Capacity###############################
capacity = {
   'ATTRIBUTE' :  'programName',
   'DEFAULT'    : 'default',
   'default'    :  { #other programs
      '1' : '%dG' % (VbarCapacityGBPerHead    ),
      'A' : '%dG' % (WTFCapacityGBPerHead     ),
      '2' : '%dG' % (VbarCapacityGBPerHead * 2),
      'C' : '%dG' % (WTFCapacityGBPerHead  * 2),
      '3' : '%dG' % (VbarCapacityGBPerHead * 3),
      '4' : '%dG' % (VbarCapacityGBPerHead * 4),
      'G' : '%dG' % (WTFCapacityGBPerHead  * 4),
      'E' : '640G',
   },
   'Rosewood7'  :  {
      '1' : '%dG' % (VbarCapacityGBPerHead    ),
      'A' : '%dG' % (WTFCapacityGBPerHead     ),
      '2' : '1000G', #'%dG' % (VbarCapacityGBPerHead * numHeads),
      'C' : '%dG' % (WTFCapacityGBPerHead  * 2),
      '3' : '%dG' % (VbarCapacityGBPerHead * 3),
      '4' : '%dG' % (VbarCapacityGBPerHead * 4),
      'G' : '%dG' % (WTFCapacityGBPerHead  * 4),
      'D' : '500G',
   },
   'Chengai'    :  {
      '2' : '750G',
      'C' : '500G',
   },
}
##############################################################################


#######################################################################################
###################################################################
# Precoder Param
###################################################################
vPCodeMap0 = [ 0x3210,
  0x4652,
  0x4625,
  0x7362,
  0x7365
]

vPCodeMap1 = [ 0x7654,
  0x0713,
  0x0713,
  0x0145,
  0x0142
]

vIDX0_3 = []
vIDX4_7 = []

post_coder_lut = [0] * 8

for k in range(len(vPCodeMap0)):
    reg_value = (vPCodeMap1[k]<<16) | vPCodeMap0[k]
    reg_value = "%08x" % reg_value
    reg_value = reg_value[::-1]
    for j in range(8):
        post_coder_lut[int(reg_value[j],16)] = j
    reg_value = str(post_coder_lut[3]) + str(post_coder_lut[2]) + str(post_coder_lut[1]) + str(post_coder_lut[0])
    vIDX0_3.append(int(reg_value,16))
    reg_value = str(post_coder_lut[7]) + str(post_coder_lut[6]) + str(post_coder_lut[5]) + str(post_coder_lut[4])
    vIDX4_7.append(int(reg_value,16))


mask = [0] * len(vPCodeMap0)


prm_Pcode_all_msk = {
    'Zn16_allMsk'              : {
                               'ATTRIBUTE':'numZones',
                               24: 0xFFFF,
                               31: 0xFFFF,   # default check at zone 16 only
                               60: 0xFFFF,
                               },
    'Zn32_allMsk'              : {
                               'ATTRIBUTE':'numZones',
                               24: 0xFF,
                               31: 0x3FFF,  # default check at zone 16 only
                               60: 0xFFFF
                               },
    'Zn48_allMsk'              : {
                               'ATTRIBUTE':'numZones',
                               24: 0,
                               31: 0,
                               60: 0xFFFF,
                               },
    'Zn64_allMsk'              : {
                               'ATTRIBUTE':'numZones',
                               24: 0,
                               31: 0,   # default check at zone 16 only
                               60: 0xFFF,
                               },
}

regIDX0_3 = 0x0421
regIDX4_7 = 0x0422
regMAP0 = 0x202E
regMAP1 = 0x202F
pCodeCudocomCMD = 1399


prm_Pcode_DET_LUT_IDX0_3 = { 'REG_ID' : regIDX0_3 ,
                             'Param' : vIDX0_3,
                             'Zn16Msk' : list(mask),
                             'Zn32Msk' : list(mask),
                             'Zn48Msk' : list(mask),
                             'Zn60Msk' : list(mask)

                           }

prm_Pcode_DET_LUT_IDX4_7 = { 'REG_ID' : regIDX4_7 ,
                             'Param' : vIDX4_7,
                             'Zn16Msk' : list(mask),
                             'Zn32Msk' : list(mask),
                             'Zn48Msk' : list(mask),
                             'Zn60Msk' : list(mask)

                           }

prm_Pcode_PCODE_MAP0 = {'REG_ID' : regMAP0 ,
                        'Param' : vPCodeMap0,
                        'Zn16Msk' : list(mask),
                        'Zn32Msk' : list(mask),
                        'Zn48Msk' : list(mask),
                        'Zn60Msk' : list(mask)

                       }

prm_Pcode_PCODE_MAP1 = {'REG_ID' : regMAP1 ,
                        'Param' : vPCodeMap1,
                        'Zn16Msk' : list(mask),
                        'Zn32Msk' : list(mask),
                        'Zn48Msk' : list(mask),
                        'Zn60Msk' : list(mask)

                       }

Precoder_BER_prm_250 = {
    'test_num'              : 250,
    'prm_name'              : 'Pcoder_BER',
    'RETRIES'               : 50,
    'MAX_ITERATION'         : MaxIteration,  ## org is 24
    'ZONE_POSITION'         : 198,
    'spc_id'                : 9423,
    'MAX_ERR_RATE'          : -80,
    'TEST_HEAD'             : 255,
    'NUM_TRACKS_PER_ZONE'   : 10,
    'SKIP_TRACK'            : 200,
    'TLEVEL'                : 0,
    'MINIMUM'               : 10, ## remove ber screening
    'timeout'               : 2000,
    "ZONE_MASK"             : (0xFFFF, 0xFFFF),
    "ZONE_MASK_EXT"         : (0xFFF, 0xFFFF),
    'WR_DATA'               : 0,
    'CWORD1'                : 0x1C3,
    'CWORD2'                : 0

}

MaxTable = {
 'HD_PHYS_PSN' : [],
 'DATA_ZONE'   : [],
 'RAW_ERROR_RATE' : [],
 'COMBI' : []
}

prm_MT50_10_Measurement_269= {
   'test_num'               : 269,
   'prm_name'               : 'prm_MT50_10_Measurement_269',
   'spc_id'                 : 1,
   'timeout'                : 6000 * numHeads,
   'CWORD1'                 : 0x3801,  #If Bit 9 in ON, test only at Zero Skew Area, Zone_mask is no effect.
   'LOOP_CNT'               : 2,
   'STEP_INC'               : 4,
   'HEAD_MASK'              : 0x3FF,
   'ZONE_MASK'              : (0x0000, 0x0001),
   'ZONE_MASK_EXT'          : (0x0000, 0x0000),
   'TRIM_PERCENTAGE_VALUE'  : 10,
   'SET_OCLIM'              : 200,
   'OFFSET_SETTING'         : (-380, 380, 255),
   'ZONE_POSITION'          : 198,
   'LENGTH_LIMIT'           : 1032,
}

erase_band_testing_zones = [75]

prm_erase_band = {
   'test_num'              : 270,
   'prm_name'              : 'prm_erase_band',
   'timeout'               : 6000 * numHeads,
   'spc_id'                : 1,
   'LOOP_CNT'              : 2,
   'HEAD_MASK'             : 0x3FF,
   #'ZONE_MASK'             : (0x0000, 0x0001),
   #'ZONE_MASK_EXT'         : (0x0000, 0x0000),
   'OFFSET_SETTING'        : (-380, 380, 212),
   'STEP_INC'              : 8,
   'CWORD1'                : 0x0001, #If Bit 9 in ON, test only at Zero Skew Area, Zone_mask is no effect.
   'ZONE_POSITION'         : 198,
   'SET_OCLIM'             : 200,
   'LENGTH_LIMIT'          : 1032,
}

############# Sigmund In Factor ##############################
sif_prm_322 = {
    'test_num'                          : 322,
    'dlfile'                            : (CN, 'CHG_778G_1A03_base1A02_adjsrvbound_RWGap_205_single.SIG'),
    'timeout'                           : 1.5 * 1800 * numHeads,
    'SIF_CREATE_FORMAT'                 : 2,
    'SIF_W2R_TOLERANCE'                 : {
                                           'ATTRIBUTE'        : 'MARVELL_SRC',
                                           'DEFAULT'          : 1,
                                           0                  : 0,
                                           1                  : 300,
    },
    'SIF_W2R_BY_HEAD_EXT'               : [20500,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    'CWORD1'                            : 3,
    }
bpi_bin_size = {
   'EQUATION':'self.dut.imaxHead*635780* self.dut.numZones/60'
}

#######################################################################################
# Zoned Servo related info
PRM_DISPLAY_ZONED_SERVO_CONFIG_TABLE_172 = {
   'test_num'               : 172,
   'prm_name'               : 'PRM_DISPLAY_ZONED_SERVO_CONFIG_TABLE_172',
   'spc_id'                 : 1,
   'timeout'                : 1200,
   'CWORD1'                 : 47,
}

PRM_DISPLAY_ZONED_SERVO_ZONE_TABLE_172 = {
   'test_num'               : 172,
   'prm_name'               : 'PRM_DISPLAY_ZONED_SERVO_ZONE_TABLE_172',
   'spc_id'                 : 1,
   'timeout'                : 1200,
   'CWORD1'                 : 48,
}

PRM_DISPLAY_HEAD_TPI_CONFIG_172 = {
   'test_num'               : 172,
   'prm_name'               : 'PRM_DISPLAY_HEAD_TPI_CONFIG_172',
   'spc_id'                 : 1,
   'timeout'                : 1200,
   'CWORD1'                 : 49,
}

PRM_DISPLAY_ZONED_SERVO_RADIUS_KFCI_172 = {
   'test_num'               : 172,
   'prm_name'               : 'PRM_DISPLAY_ZONED_SERVO_RADIUS_KFCI_172',
   'spc_id'                 : 1,
   'timeout'                : 1200,
   'CWORD1'                 : 59,
}

############################### LBR ########################################################
ZB_remain = {    # must add previous zone to ZB_IDremain. from: FAFH zone
   'ATTRIBUTE':'numZones',
   'DEFAULT': 60,
   60:  [0,  60/2-1,  60-2],
   150: [0, 150/2-1, 150-2],
   180: [0, 180/2-1, 180-2],
}

ZB_IDremain = {            # from: FAFH zone
   'ATTRIBUTE':'numZones',
   'DEFAULT': 60,
   60:  [ 60/2-2,  60-3],
   150: [150/2-2, 150-3],
   180: [180/2-2, 180-3],
}

updateZB_178 = {
   'test_num' : 178,
   'prm_name' : 'updateZB_178',
   'timeout'  : 120,
   'spc_id'   : 1,
}

DisplaySysZB = {
   'test_num' : 172,
   'prm_name' : 'Display System ZB',
   'CWORD1'   : 60,
   'timeout'  : 10,
   'spc_id'   : 1,
}

DisplayUserZB = {
   'test_num' : 172,
   'prm_name' : 'Display User ZB',
   'CWORD1'   : 61,
   'timeout'  : 10,
   'spc_id'   : 1,
}

LBRDeltaDensityLimit = {
   'ATTRIBUTE' : 'programName',
   'DEFAULT'   : 'default',
   'default'   : 1,
   'Rosewood7' : {
      'ATTRIBUTE'       : 'FE_0370517_348429_ADDITIONAL_OC2_BPI_PUSH',
      'DEFAULT'         : 0,
      0                 : 0.007,
      1                 : 0.008,
   },
}

Add_OC2BPIPush_DensityLimit = {
   'ATTRIBUTE'          : 'FE_0370517_348429_ADDITIONAL_OC2_BPI_PUSH',
   'DEFAULT'            : 0,
   0                    : 0,
   1                    : 0.025, # ~25Gb for RW1D
}
   

#######################################################################################

SPRatio = 0.2    # fail if drive Super Parity Ratio > 0.2

ACMSDowngradeErrorCodes = {
   23558 : 'No matching configuration',
   23559 : 'Configuration not Released/Found',
   # 23616 : 'No Demand for this Part Number',
   # 23617 : 'Demand Full or QTY Req NULL/Empty',
   # 49405 : 'No Matching Demand Found',
   # 49406 : 'No 9 digit CC assigns to Tier CC'
}

############################# Begin - AEGIS Screening #################################
svoRules = (  # https://docs.google.com/a/seagate.com/spreadsheets/d/1wte3EqNX1c1x3mui5SIYsVsJgPyLVKnfXwuJQtrsmEU/edit?usp=sharing
#  ('Critical Features',         'Symbol_Offset_Name',            LocCnt,  BitMsk,  Criterion),
   ('LVFF Enable',               'SP_LVFF_ENABLE_SYMBOL_OFFSET',  0,       0x0001,  0x0001),  # Linear Vibration Feed Forward on
   ('ACFF Enable',               'ZONED_ACFF_SYMBOL_OFFSET',      0,       0x0809,  0x0809),  # Zoned ACFF, seek acoustic feature, cert done
)

# afhRapInit = 16608
# afhHdOfst = 144
afhClrRules = (
#  ('Features Description',      'Column_Name',                   Rap_Offset,       Criterion),
   ('PRE_HEAT_TRGT_CLRNC',       'PRE_HEAT_TRGT_CLRNC',           4,                12),
   ('WRT_HEAT_TRGT_CLRNC',       'WRT_HEAT_TRGT_CLRNC',           3,                12),
   ('READ_HEAT_TRGT_CLRNC',      'READ_HEAT_TRGT_CLRNC',          5,                15),
)
############################# End - AEGIS Screening ###################################


############################# PROC_CTRL30 Bit Definitions ###################################
Proc_Ctrl30_Def = {
   'DESTROKED'    : 0x0001,
   'QSFM_1'       : 0x0002,
   'QSFM_2'       : 0x0004,
   'QAFH'         : 0x0008,
   'TRIGGER_TSR'  : 0x0010,
   'FORCE_PUSH'   : 0x0040,
   'T189_10806'   : 0x0100,
   'T73_RETRY'    : 0x0200,
   'ShortScreen'  : 0x0400,
   'FULL_AFH3'    : 0x2000,
   'RE_AFH2'      : 0x4000,
   'TCC_BY_BER'   : 0x8000,
}

SetByZnCword = 0x2000 #cword1 of t210 to set format by zone instead of by head

########## RW7 unload current screening - controlled by FE_0303511_305538_P_ENABLE_UNLOAD_CURR_OVER_TIME_SCREEN #########
T025_Unload_Curr_Screen = {
   'ATTRIBUTE' : 'IS_2D_DRV',
   'DEFAULT'   : 0,
   0           : {
      'table'        : 'P025_LD_UNLD_PARAM_STATS',
      'header'       : 'STATISTIC_NAME',
      'column'       : 'ULD_MAX_CUR',
      'MAX'          : 170.0, # fail if >= spec
      },
   1           : {
      'table'        : 'P025_LD_UNLD_PARAM_STATS',
      'header'       : 'STATISTIC_NAME',
      'column'       : 'ULD_MAX_CUR',
      'MAX'          : 100.0, # fail if >= spec
      'STDEV'        : 3.0,   # fail if >= spec
      },
}

#######################################################################################
################################PBIC Controller Settings ######################## BEGIN
#######################################################################################

# Add the state where KPIV data are collected right after the state completion.

kpivdatastateList = {
   "PRE2": 'ALL',
   "CAL2": 'ALL',
   "FNC2": 'ALL',
   "CRT2": 'ALL',
   #"CRT2": ['VER_RAMP','AFH4'],

}

#######################################
#
#  ATI screening BPIC control rules
#
#######################################


#------------------

ATI_BPIM_BH_lim = {
   'ATTRIBUTE' : 'nextOper',
   'DEFAULT'   : 'FNC2',
   'FNC2'      : 0.02,
   'CRT2'      : 0.008,
   }
ATI_TPIM_BH_lim = {
   'ATTRIBUTE' : 'nextOper',
   'DEFAULT'   : 'FNC2',
   'FNC2'      : 0.02,
   'CRT2'      : 0.015,
   }
ATI_RRO_BH_lim  = 0   
ATI_NRRO_BH_lim = 0   
ATI_ER_AVG_BH_lim   = {
   'ATTRIBUTE' : 'nextOper',
   'DEFAULT'   : 'FNC2',
   'FNC2'      : -1.8,
   'CRT2'      : -1.95,
   }
ATI_ER_MAX_BH_lim   = {
   'ATTRIBUTE' : 'nextOper',
   'DEFAULT'   : 'FNC2',
   'FNC2'      : -1.75,
   'CRT2'      : -1.85,
   }





#######################################
#
#  SWEEPING BPIC control rules
#
#######################################


#------------------

SWP_BPIM_BH_lim = 0.0363
SWP_TPIM_BH_lim = 0.052
SWP_RRO_BH_lim  = 3.92
SWP_NRRO_BH_lim = 2.97
SWP_ER_BH_lim   = -2.84



#######################################
#
#  Weakwrite BPIC control rules
#
#######################################


#------------------

WeakWrt_BPIM_BH_lim = 0.0363
WeakWrt_TPIM_BH_lim = 0.052
WeakWrt_SQZER_BH_lim = -2.84
WeakWrt_ER2_BH_lim   = -2.84


#######################################################################################
################################PBIC Controller Settings ########################   END
#######################################################################################

IDDISTables = ['P_SIDE_ENCROACH_BER','TEST_TIME_BY_STATE','P250_BER_MTRIX_BY_ZONE','P_VBAR_SUMMARY2','P_VBAR_HMS_ADJUST']
EC_BYPASS_DDIS = []

### Serial Port Apple spec based on LCO - need to collect data for NSG ###
### MIN_MAX_READ / MIN_MAX_WRITE -/+10% criteria population mean spec. for read and write transfer for all zones
Head2WriteSpec = ( (119.75, 146.36), (118.25, 144.53), (119.71, 146.31), (119.15, 145.63), (117.84, 144.02), (117.42, 143.51), (117.03, 143.04), (116.58, 142.48), (116.45, 142.32), (115.88, 141.63), (115.35, 140.99), (114.81, 140.33), (114.32, 139.73), (113.87, 139.17), (113.36, 138.55), (112.83, 137.9), (112.31, 137.27), (111.84, 136.7), (111.45, 136.21), (110.94, 135.59), (110.45, 135.0), (110.07, 134.53), (109.63, 133.99), (109.22, 133.49), (108.84, 133.02), (108.41, 132.5), (107.73, 131.67), (107.04, 130.82), (106.66, 130.37), (106.29, 129.91), (105.88, 129.4), (105.45, 128.88), (105.01, 128.34), (104.5, 127.72), (104.05, 127.18), (103.62, 126.65), (103.16, 126.08), (102.26, 124.98), (100.4, 122.71), (100.52, 122.86), (100.87, 123.29), (100.44, 122.76), (99.97, 122.19), (99.53, 121.65), (99.1, 121.13), (98.61, 120.52), (98.15, 119.96), (97.69, 119.4), (97.21, 118.82), (96.76, 118.26), (96.28, 117.68), (95.81, 117.1), (95.34, 116.52), (94.86, 115.94), (94.36, 115.33), (93.86, 114.72), (93.44, 114.21), (92.96, 113.61), (92.53, 113.09), (92.11, 112.58), (91.64, 112.0), (91.15, 111.4), (90.69, 110.85), (90.24, 110.29), (89.74, 109.68), (89.27, 109.11), (88.81, 108.54), (88.35, 107.98), (87.87, 107.39), (87.37, 106.78), (86.87, 106.17), (86.4, 105.59), (85.9, 104.99), (85.26, 104.21), (83.99, 102.66), (82.82, 101.23), (82.93, 101.36), (83.07, 101.53), (82.65, 101.02), (82.2, 100.46), (81.72, 99.88), (81.23, 99.28), (80.75, 98.7), (80.28, 98.11), (79.85, 97.6), (79.37, 97.0), (78.9, 96.43), (78.44, 95.87), (77.98, 95.31), (77.53, 94.76), (77.05, 94.17), (76.59, 93.61), (76.12, 93.03), (75.66, 92.47), (75.19, 91.9), (74.74, 91.34), (74.27, 90.78), (73.83, 90.24), (73.39, 89.7), (72.96, 89.17), (72.53, 88.64), (72.09, 88.11), (71.66, 87.58), (71.22, 87.05), (70.78, 86.51), (70.35, 85.99), (69.91, 85.44), (69.46, 84.9), (69.01, 84.34), (68.54, 83.77), (67.69, 82.73), (66.3, 81.03), (65.7, 80.3), (65.83, 80.46), (65.86, 80.5), (65.54, 80.1), (65.15, 79.62), (64.74, 79.13), (64.33, 78.62), (63.93, 78.14), (63.54, 77.65), (63.14, 77.17), (62.74, 76.68), (62.34, 76.19), (61.93, 75.7), (61.54, 75.21), (61.14, 74.73), (60.74, 74.24), (60.34, 73.74), (59.95, 73.28), (59.57, 72.8), (59.19, 72.34), (58.81, 71.87), (58.41, 71.39), (58.04, 70.94), (57.67, 70.49), (57.31, 70.04), (56.95, 69.61), (56.58, 69.16), (56.21, 68.7), (55.85, 68.26), (55.5, 67.83), (55.16, 67.41), (54.8, 66.98), (54.45, 66.55), (54.1, 66.12), (53.74, 65.68), (53.39, 65.26), (53.02, 64.8), )
Head2ReadSpec =  ( (123.03, 150.360), (121.48, 148.48), (122.97, 150.30), (122.44, 149.65), (117.84, 144.03), (117.43, 143.53), (117.04, 143.05), (116.59, 142.5), (119.6, 146.18), (119.01, 145.46), (118.48, 144.81), (117.93, 144.13), (117.42, 143.52), (116.95, 142.94), (116.43, 142.3), (115.89, 141.64), (115.35, 140.99), (114.88, 140.41), (114.46, 139.9), (113.95, 139.27), (113.45, 138.66), (113.05, 138.17), (112.6, 137.62), (112.18, 137.1), (111.78, 136.62), (111.35, 136.09), (110.65, 135.24), (109.94, 134.37), (109.55, 133.9), (109.17, 133.44), (108.75, 132.91), (108.31, 132.38), (107.85, 131.82), (107.34, 131.19), (106.88, 130.63), (106.43, 130.09), (105.96, 129.5), (105.03, 128.37), (103.13, 126.05), (103.25, 126.2), (103.61, 126.63), (103.16, 126.08), (102.69, 125.5), (102.23, 124.94), (101.79, 124.41), (101.28, 123.79), (100.81, 123.21), (100.34, 122.64), (99.85, 122.04), (99.38, 121.47), (98.89, 120.86), (98.41, 120.28), (97.92, 119.68), (97.43, 119.08), (96.93, 118.47), (96.4, 117.83), (95.98, 117.31), (95.48, 116.69), (95.04, 116.16), (94.61, 115.63), (94.12, 115.04), (93.62, 114.42), (93.16, 113.86), (92.69, 113.29), (92.18, 112.67), (91.7, 112.07), (91.22, 111.49), (90.75, 110.91), (90.26, 110.32), (89.74, 109.69), (89.23, 109.06), (88.75, 108.47), (88.24, 107.85), (87.59, 107.05), (86.3, 105.47), (85.08, 103.99), (85.19, 104.12), (85.33, 104.29), (84.9, 103.76), (84.43, 103.19), (83.94, 102.59), (83.43, 101.97), (82.95, 101.38), (82.46, 100.78), (82.02, 100.25), (81.52, 99.64), (81.05, 99.06), (80.57, 98.47), (80.1, 97.91), (79.63, 97.33), (79.14, 96.73), (78.67, 96.15), (78.18, 95.56), (77.71, 94.98), (77.24, 94.4), (76.77, 93.83), (76.29, 93.25), (75.84, 92.69), (75.38, 92.13), (74.94, 91.6), (74.5, 91.05), (74.05, 90.51), (73.61, 89.97), (73.16, 89.42), (72.7, 88.86), (72.27, 88.33), (71.81, 87.77), (71.35, 87.21), (70.88, 86.64), (70.41, 86.05), (69.53, 84.98), (68.11, 83.24), (67.49, 82.49), (67.62, 82.65), (67.66, 82.69), (67.32, 82.28), (66.92, 81.79), (66.5, 81.28), (66.08, 80.76), (65.67, 80.26), (65.26, 79.77), (64.85, 79.27), (64.45, 78.77), (64.03, 78.26), (63.62, 77.76), (63.21, 77.26), (62.81, 76.76), (62.39, 76.26), (61.98, 75.75), (61.59, 75.27), (61.19, 74.79), (60.8, 74.31), (60.41, 73.83), (60.01, 73.34), (59.62, 72.87), (59.25, 72.42), (58.87, 71.96), (58.5, 71.51), (58.13, 71.05), (57.75, 70.58), (57.38, 70.14), (57.02, 69.69), (56.67, 69.26), (56.3, 68.81), (55.94, 68.37), (55.58, 67.93), (55.21, 67.48), (54.86, 67.05), (54.47, 66.58), )
Head4ReadSpec = ( (195.88,239.41), (197.1,240.9), (195.57,239.03), (193.98,237.09), (192.67,235.49), (191.21,233.7), (190.15,232.4), (188.93,230.91), (186.76,228.26), (184.78,225.84), (183.1,223.79), (181.1,221.34), (179.89,219.86), (178.24,217.85), (176.65,215.91), (175.25,214.2), (173.87,212.51), (170.44,208.31), (168.47,205.91), (166.83,203.9), (165.24,201.96), (163.73,200.11), (162.07,198.08), (160.25,195.86), (158.64,193.89), (157.45,192.44), (155.93,190.58), (154.57,188.92), (152.62,186.53), (151.07,184.64), (149.74,183.01), (148,180.89), (145.91,178.34), (143.68,175.61), (142.08,173.65), (140.43,171.64), (138.26,168.99), (135.88,166.07), (134.26,164.1), (132.25,161.64), (128.51,157.07), (127.18,155.44), (125.16,152.97), (123.04,150.38), (121.61,148.63), (120.03,146.7), (118.46,144.78), (117.09,143.11), (111.16,135.86), (109.1,133.35), (107.23,131.06), (105.02,128.36), (102.48,125.25), (100.31,122.6), (99.14,121.17), (97.79,119.52), (95.91,117.22), (94.03,114.93), (92.18,112.66), (89.39,109.25),    )
Head4WriteSpec = ( (194.51,237.74), (195.37,238.79), (194.14,237.29), (192.57,235.36), (191.11,233.58), (190.09,232.34), (188.93,230.91), (187.65,229.35), (185.4,226.6), (183.38,224.13), (181.88,222.3), (179.99,219.99), (178.77,218.5), (177.32,216.73), (175.47,214.46), (174.28,213.01), (172.83,211.24), (169.39,207.04), (167.54,204.78), (166.01,202.9), (164.55,201.11), (162.93,199.14), (160.99,196.76), (159.4,194.82), (157.9,192.99), (156.67,191.49), (155.17,189.65), (153.62,187.76), (151.75,185.47), (150.24,183.62), (149.06,182.19), (147.23,179.95), (145.33,177.62), (142.95,174.71), (141.28,172.67), (139.8,170.86), (137.74,168.35), (135.19,165.24), (133.68,163.39), (131.79,161.07), (127.9,156.32), (126.74,154.9), (124.57,152.25), (122.42,149.63), (121.1,148.01), (119.6,146.17), (118.04,144.27), (116.57,142.48), (110.75,135.36), (108.84,133.03), (106.86,130.61), (104.69,127.95), (102.17,124.88), (100.02,122.25), (98.95,120.94), (97.51,119.17), (95.67,116.92), (93.84,114.69), (91.85,112.26), (89.21,109.04),    )

prm_Apple_PerformanceScreens = {
   'MIN_ZONE_SPEC' : ( (4,120.0), (5,120.0) ), #format is data zone and min data rate
   'MIN_R_TO_W'    : { 4      : 3.0,
                       5      : 3.0,
                     'default': 5.0,
                     }, # ZONE Specifics
   #format is zone specific limit for that indexed zone... 10% population
   'MIN_MAX_READ'       : {'ATTRIBUTE': 'imaxHead',
                           'default'  : 2,
                           2: Head2ReadSpec,
                           4: Head4ReadSpec,
                           },
   'MIN_MAX_WRITE'      : {'ATTRIBUTE': 'imaxHead',
                           'default'  : 2,
                           2: Head2WriteSpec,
                           4: Head4WriteSpec,
                           },
}

##Write Current Rise Time, Overshoot Rise Time Overshoot Fall Time Values
prm_wooT178 = {
      'test_num'           : 178,
      'prm_name'           : 'OverShoot_param',
      'timeout'            : 1200,
      "T_RISE"             : {
          "ATTRIBUTE" : 'PREAMP_TYPE',
          "DEFAULT" : 'LSI5830',
          "LSI5830":  {
                'ATTRIBUTE'          : 'HGA_SUPPLIER',
                'DEFAULT'            : 'RHO',
                'HWY'                : 7,
                'RHO'                : 7,
                },
          "TI7551" : {
                'ATTRIBUTE'          : 'HGA_SUPPLIER',
                'DEFAULT'            : 'RHO',
                'HWY'                : 1,
                'RHO'                : 1,
                },
        },
      "OVS_RISE_TIME"             : {
          "ATTRIBUTE" : 'PREAMP_TYPE',
          "DEFAULT" : 'LSI5830',
          "LSI5830": {
                'ATTRIBUTE'          : 'HGA_SUPPLIER',
                'DEFAULT'            : 'RHO',
                'HWY'                : 7,
                'RHO'                : 7,
                },
          "TI7551" : {
                'ATTRIBUTE'          : 'HGA_SUPPLIER',
                'DEFAULT'            : 'RHO',
                'HWY'                : 7,
                'RHO'                : 7,
                },
        },
      "OVS_FALL_TIME"             : {
          "ATTRIBUTE" : 'PREAMP_TYPE',
          "DEFAULT" : 'LSI5830',
          "LSI5830":  {
                'ATTRIBUTE'          : 'HGA_SUPPLIER',
                'DEFAULT'            : 'RHO',
                'HWY'                : 3,
                'RHO'                : 3,
                },
          "TI7551" : {
                'ATTRIBUTE'          : 'HGA_SUPPLIER',
                'DEFAULT'            : 'RHO',
                'HWY'                : 3,
                'RHO'                : 3,
                },
        },
      'ZONE'               : 150,
      'CWORD1'             : 512,
      'CWORD3'             : 8192,
      'CWORD4'             : 8256,
      'HEAD_RANGE'         : 1023,
}
HeadInstabilityT297Spec = {
   't297loop'                 : 3, #Per RSS request 21 July 2015
   'MODELOSS_AVG_INFO'        : { # 0.60, #Per RSS request 2 Sept 2015
      'ATTRIBUTE'    : 'nextOper',
      'DEFAULT'      : 'default',
      'default'      : 0.27,
      'CRT2'         : 0.60,
   },
   'MODELOSS_AVG_INFO_COMBO'  : {
      'ATTRIBUTE'    : 'nextOper',
      'DEFAULT'      : 'default',
      'default'      : 0.18,
      'CRT2'         : 0.155,
   },
   'SIGMALOSS_AVG_INFO_COMBO' : {
      'ATTRIBUTE'    : 'nextOper',
      'DEFAULT'      : 'default',
      'default'      : 0.09,
      'CRT2'         : 0.085,
   },
}

TargetLoop =[[2,9,1],[3,8,0],[3,9,1],[4,10,1],[4,7,0],[2,8,2]]

T185_T25_RDG_Screen_Spec = {
   'ATTRIBUTE'    : 'BG',
   'DEFAULT'      : 'OEM',
   'SBS'          : {}, # fail-safe
   'OEM'          : {
      'UFCO_OffsetFail'    : 6000,
      # 'Max_RampCyl'        : 6000,
   },
}
#######################################
#
#  Min Erasure BER Screen Spec
#
#######################################
Min_Erasure_Ber_Screen_Spec = {
   'ATTRIBUTE'       : 'IS_2D_DRV',
   'DEFAULT'         : 0,
   0                 : {
      ('P051_ERASURE_BER', 'count')      : {
         'spc_id'       : {                 # default is all table available
            'ATTRIBUTE'               : 'FE_0253166_504159_MERGE_FAT_SLIM',
            'DEFAULT'                 : 0,
            0                         : 4000,
            1                         : 6000,
         },
         'row_sort'     : ('HD_LGC_PSN','DATA_ZONE'), # default is HD_LGC_PSN if omitted
         'col_sort'     : 'TRK_INDEX',                # default is DATA_ZONE if omitted
         'col_range'    : (-2,-3),                    # default is any, no filtering
         'column'       : ('TEST_TYPE',   'RRAW_BER'),
         'compare'      : (       '==',         '<='),
         'criteria'     : (  'erasure',          7.0),
         'fail_count'   : 2,                          # this is must have for count type
      },
      ('Title','')         : 'Min_Erasure_Ber_Screen_Spec',
   },
   1                 : {}, # disabled for RW7-2D
}

CRT2_1K_COMBO_Screen_Spec = {
   'ATTRIBUTE'       : 'IS_2D_DRV',
   'DEFAULT'         : 0,
   0                 : {}, # disabled for RW7-1D
   1                 : {
      ('P051_ERASURE_BER', 'count')      : {
         'spc_id'       : {                 # default is all table available
            'ATTRIBUTE'               : 'FE_0253166_504159_MERGE_FAT_SLIM',
            'DEFAULT'                 : 0,
            0                         : 4000,
            1                         : 6000,
         },
         'row_sort'     : ('HD_LGC_PSN','DATA_ZONE'), # default is HD_LGC_PSN if omitted
         'col_sort'     : 'TRK_INDEX',                # default is DATA_ZONE if omitted
         'col_range'    :  list(range(-59,-1) + range(2,31)), # default is any, no filtering
         'column'       : ('TEST_TYPE',   'RRAW_BER', 'BITS_IN_ERROR_BER'),
         'compare'      : (       '==',         '<=',      '<='),
         'criteria'     : (  'erasure',          5.0,       1.7),
         'fail_count'   : 1,                          # this is must have for count type
      },
      ('Title','')         : 'CRT2_1K_COMBO_Screen_Spec',
   },
}

FNC2_10K_STE_Screen_Spec = {
   'ATTRIBUTE'       : 'IS_2D_DRV',
   'DEFAULT'         : 0,
   0                 : {}, # disabled for RW7-1D
   1                 : {
      ('P051_ERASURE_BER', 'count')      : {
         'spc_id'       : 80000,                       # default is all table available
         'row_sort'     : ('HD_LGC_PSN','DATA_ZONE'), # default is HD_LGC_PSN if omitted
         'col_sort'     : 'TRK_INDEX',                # default is DATA_ZONE if omitted
         'col_range'    :  (-2), # default is any, no filtering
         'column'       : ('TEST_TYPE',   'RRAW_BER', 'BITS_IN_ERROR_BER'),
         'compare'      : (       '==',         '<=',      '<='),
         'criteria'     : (  'erasure',          4.52,       1.58),
         'fail_count'   : 1,                          # this is must have for count type
      },
   },
}

Zest_Screen_Spec = {
   'ATTRIBUTE'    : 'BG',
   'DEFAULT'      : 'OEM',
   'SBS'          : {}, # fail-safe
   'OEM'          : {
      ('P287_PHYS_TRK_STATS', 'match')      : {
         'ATTRIBUTE'       : 'IS_2D_DRV',
         'DEFAULT'         : 0,
         0                 : {
            'column'       : ('MABS_JOG_ERR', 'MABS_DC_ERR'),
            'compare'      : (           '>',           '>'),
            'criteria'     : (          30.0,          35.0),
         },
         1                 : {
            'column'       : ('MABS_JOG_ERR', 'MABS_DC_ERR'),
            'compare'      : (           '>',           '>'),
            'criteria'     : (          30.0,          30.0),
         },
      },
      # --- common criteria for both 1D and 2D
      ('P287_PHYS_TRK_STATS', 'count')      : {
         'column'       : ('MABS_DC_ERR'),
         'compare'      : (          '>'),
         'criteria'     : (         80.0),
         'fail_count'   : 1,              # this is must have for count type
      },
      ('Fail_Cnt','')      : 1, # fail if any of the above set of criteria failed
      ('Title','')         : 'Zest_Screen_Spec',
   },
}

T337_OverWrite_Screen_Spec = {
   'ATTRIBUTE'    : 'BG',
   'DEFAULT'      : 'OEM',
   'SBS'          : {}, # fail-safe
   'OEM'          : {
      'ATTRIBUTE'    : 'nextOper',
      'DEFAULT'      : 'default',
      'default'      : {}, # fail-safe
      'CAL2'         : { # in CAL2 only
         ('P337_OVERWRITE', 'match')      : {
            'column'       : ('OVERWRITE'),
            'compare'      : (       '<='),
            'criteria'     : (       10.0),
         },
         ('Title','')         : 'T337_OverWrite_Screen_Spec',
      },
   },
}

SqzWrite_SPC_ID = { # define default SQZ_WRITE spc_id
   'ATTRIBUTE'    : 'nextState',
   'DEFAULT'      : 'SQZ_WRITE',
   'SQZ_WRITE'    : 3,
   'SQZ_WRITE2'   : 30,
}

T250_SqzWrite_Screen_Spec1 = {
   'ATTRIBUTE'    : 'IS_2D_DRV',
   'DEFAULT'      : 0,
   0              : {
      'ATTRIBUTE'    : 'nextState',
      'DEFAULT'      : 'default',
      'default'      : {}, # fail-safe
      'SQZ_WRITE'    : {
         'ATTRIBUTE' : 'WA_0309963_504266_504_LDPC_PARAM',
         'DEFAULT'   : 0,
         0           : {
            ('P250_ERROR_RATE_BY_ZONE', 'max')   : {
               'spc_id'       : 3,         # sqz write spcid only
               'fail_code'    : 0,         # good BER only
               'column'       : ('RAW_ERROR_RATE'),
               'compare'      : (            '>='),
               'criteria'     : (           -1.87),
            },
            ('P250_ERROR_RATE_BY_ZONE', 'mean')   : {
               'spc_id'       : 3,         # sqz write spcid only
               'fail_code'    : 0,         # good BER only
               'column'       : ('RAW_ERROR_RATE'),
               'compare'      : (            '>='),
               'criteria'     : (           -2.00),
            },
            ('Title','')      : 'T250_SqzWrite_Screen_Spec1',
         },
         1           : {
            ('P250_ERROR_RATE_BY_ZONE', 'max')   : {
               'spc_id'       : 3,         # sqz write spcid only
               'fail_code'    : 0,         # good BER only
               'column'       : ('RAW_ERROR_RATE'),
               'compare'      : (            '>='),
               'criteria'     : (           -1.70),
               'fail_code'    : 0,
            },
            ('P250_ERROR_RATE_BY_ZONE', 'mean')   : {
               'spc_id'       : 3,         # sqz write spcid only
               'fail_code'    : 0,         # good BER only
               'column'       : ('RAW_ERROR_RATE'),
               'compare'      : (            '>='),
               'criteria'     : (           -1.80),
               'fail_code'    : 0,
            },
            ('Title','')      : 'T250_SqzWrite_Screen_Spec1',
         },
      },
   },
   1              : {},
}

T250_SqzWrite_Screen_Spec3 = {
   'ATTRIBUTE'    : 'IS_2D_DRV',
   'DEFAULT'      : 0,
   0              : {
       'ATTRIBUTE'    : 'BG',
       'DEFAULT'      : 'OEM',
       'SBS'          : {}, # fail-safe
       'OEM'          : {
          'ATTRIBUTE'    : 'HGA_SUPPLIER',
          'DEFAULT'      : 'FailSafe',
          'FailSafe'     : {}, # fail-safe
          'TDK'          : {
             'ATTRIBUTE'    : 'nextState',
             'DEFAULT'      : 'default',
             'default'      : {}, # fail-safe
             'SQZ_WRITE'    : {
                   ('P250_ERROR_RATE_BY_ZONE', 'mean')   : {
                      'spc_id'       : 3,         # sqz write spcid only
                      'col_sort'     : ('DATA_ZONE'),
                      'col_range'    : {'EQUATION' : "[zn for zn in xrange(self.dut.numZones) if zn not in TP.UMP_ZONE[self.dut.numZones]]"},
                      'column'       : ('RAW_ERROR_RATE'),
                      'compare'      : (            '>='),
                      'criteria'     : (          -1.84),
                   },
                   ('P250_ERROR_RATE_BY_ZONE', 'max')   : {
                      'spc_id'       : 3,         # sqz write spcid only
                      'col_sort'     : ('DATA_ZONE'),
                      'col_range'    : {'EQUATION' : "[zn for zn in xrange(self.dut.numZones) if zn not in TP.UMP_ZONE[self.dut.numZones]]"},
                      'column'       : ('RAW_ERROR_RATE'),
                      'compare'      : (            '>='),
                      'criteria'     : (          -1.75),
                   },
                   ('Title','')      : 'T250_SqzWrite_Screen_Spec3',
             },
          },
       },
    },
    1              : {},
}

T250_SqzWrite_Screen_Spec4 = {
   'ATTRIBUTE'    : 'IS_2D_DRV',
   'DEFAULT'      : 0,
   0              : {
       'ATTRIBUTE'    : 'BG',
       'DEFAULT'      : 'OEM',
       'SBS'          : {}, # fail-safe
       'OEM'          : {
          'ATTRIBUTE'    : 'nextState',
          'DEFAULT'      : 'default',
          'default'      : {}, # fail-safe
          'SQZ_WRITE'    : {
             'ATTRIBUTE'    : 'HGA_SUPPLIER',
             'DEFAULT'      : 'FailSafe',
             'FailSafe'     : {}, # fail-safe
             'TDK'          : {
                   ('P250_ERROR_RATE_BY_ZONE', 'mean')  : {
                      'spc_id'       : 3,                       # sqz write spcid only
                      'col_sort'     : ('DATA_ZONE'),
                      'col_range'    : {'EQUATION' : "[zn for zn in xrange(self.dut.numZones) if zn not in TP.UMP_ZONE[self.dut.numZones]]"},
                      'column'       : ('RAW_ERROR_RATE'),
                      'compare'      : (            '>='),
                      'criteria'     : (          -1.835),
                   },
                   ('P250_ERROR_RATE_BY_ZONE', 'max - mean')  : {
                      'spc_id'       : 3,                       # sqz write spcid only
                      'col_sort'     : ('DATA_ZONE'),
                      'col_range'    : {'EQUATION' : "[zn for zn in xrange(self.dut.numZones) if zn not in TP.UMP_ZONE[self.dut.numZones]]"},
                      'column'       : ('RAW_ERROR_RATE'),
                      'compare'      : (            '>='),
                      'criteria'     : (           0.15),
                   },
                   ('Title','')      : 'T250_SqzWrite_Screen_Spec4',
             },
             'RHO'          : {
                   ('P250_ERROR_RATE_BY_ZONE', 'mean')  : {
                      'spc_id'       : 3,                       # sqz write spcid only
                      'col_sort'     : ('DATA_ZONE'),
                      'col_range'    : {'EQUATION' : "[zn for zn in xrange(self.dut.numZones) if zn not in TP.UMP_ZONE[self.dut.numZones]]"},
                      'column'       : ('RAW_ERROR_RATE',),
                      'compare'      : (            '>=',),
                      'criteria'     : (           -1.80,),
                   },
                   ('Title','')      : 'T250_SqzWrite_Screen_Spec4',
             },
          },
       },
    },
    1              : {
       'ATTRIBUTE'    : 'BG',
       'DEFAULT'      : 'OEM',
       'SBS'          : {}, # fail-safe
       'OEM'          : {
          'ATTRIBUTE'    : 'nextState',
          'DEFAULT'      : 'default',
          'default'      : {}, # fail-safe
          'SQZ_WRITE'    : {
                       ('P250_ERROR_RATE_BY_ZONE', 'match')  : {
                          'spc_id'       : 3,                       # sqz write spcid only
                          'col_sort'     : ('DATA_ZONE'),
                          'col_range'    : {'EQUATION' : "[zn for zn in xrange(self.dut.numZones) if zn not in TP.UMP_ZONE[self.dut.numZones]]"},
                          'column'       : ('RAW_ERROR_RATE',),
                          'compare'      : (            '>=',),
                          'criteria'     : (           -1.75,),
                       },
                       ('Title','')      : 'T250_SqzWrite_Screen_Spec4',
            },
        },
    },        
}
T250_SqzWrite_Screen_Spec5 = {
   'ATTRIBUTE'    : 'IS_2D_DRV',
   'DEFAULT'      : 0,
   0              : {
      'ATTRIBUTE'  : 'PART_NUM',
      'DEFAULT'    : 'default',
      'default'    : {},
      '2G3172-900' : {
      ('P250_ERROR_RATE_BY_ZONE', 'max')   : {
              'spc_id'       : 3,         # sqz write spcid only
              'col_sort'     : ('DATA_ZONE'),
              'col_range'    : {'EQUATION' : "[zn for zn in xrange(self.dut.numZones) if zn not in TP.UMP_ZONE[self.dut.numZones]]"},
              'column'       : ('RAW_ERROR_RATE'),
              'compare'      : (            '>='),
              'criteria'     : (          -1.8),
        },
      },
   },
   1              :{      
   'ATTRIBUTE'  : 'PART_NUM',
   'DEFAULT'    : 'default',
   'default'    : {},
   '2G2174-900' : {
    ('P250_ERROR_RATE_BY_ZONE', 'max')   : {
              'spc_id'       : 3,         # sqz write spcid only
              'col_sort'     : ('DATA_ZONE'),
              'col_range'    : {'EQUATION' : "[zn for zn in xrange(self.dut.numZones) if zn not in TP.UMP_ZONE[self.dut.numZones]]"},
              'column'       : ('RAW_ERROR_RATE'),
              'compare'      : (            '>='),
              'criteria'     : (          -1.8),
        },
      },
   },
}
T269_MT50_10_Screen_Spec = {
   'ATTRIBUTE'    : 'BG',
   'DEFAULT'      : 'OEM',
   'SBS'          : {}, # fail-safe
   'OEM'          : {
      'ATTRIBUTE'    : 'HGA_SUPPLIER',
      'DEFAULT'      : 'FailSafe',
      'FailSafe'     : {}, # fail-safe
      'RHO'          : {
         # 'ATTRIBUTE'    : 'nextState',
         # 'DEFAULT'      : 'default',
         # 'default'      : {}, # fail-safe
         # 'MT50_10_MEASURE'    : {
               ('P269_MT50_RESULT_DATA', 'match')  : {
                  'column'       : ('MT10_WIDTH',),
                  'compare'      : (        '>=',),
                  'criteria'     : (        1.67,),
               },
               ('P269_MT50_RESULT_DATA', 'delta')  : { # column - column2
                  'column'       : ('MT10_WIDTH',),
                  'column2'      : ('MT50_WIDTH',),
                  'compare'      : (        '<=',),
                  'criteria'     : (        0.63,),
               },
               ('Title','')      : 'T269_MT50_10_Screen_Spec',
         # },
      },
   }
}

T250_RdScrn2H_SqzWrite_Spec = { # combo with T250_RdScrn2H_Combo_Spec
   'ATTRIBUTE'    : 'BG',
   'DEFAULT'      : 'OEM',
   'SBS'          : {}, # fail-safe
   'OEM'          : {
      'ATTRIBUTE'    : 'HGA_SUPPLIER',
      'DEFAULT'      : 'FailSafe',
      'FailSafe'     : {}, # fail-safe
      'RHO'          : {
            ('P250_ERROR_RATE_BY_ZONE', 'mean')  : {
               'spc_id'       : 30,
               'col_sort'     : ('DATA_ZONE'),
               'col_range'    : {'EQUATION' : "[zn for zn in xrange(self.dut.numZones) if zn not in TP.UMP_ZONE[self.dut.numZones]]"},
               'column'       : ('RAW_ERROR_RATE',),
               'compare'      : (            '>',), #ori >=
               'criteria'     : (           -1.72,), #ori -1.83
            },
            ('Title','')      : 'T250_RdScrn2H_SqzWrite_Spec',
      },
   },
}

T250_RdScrn2C_SovaDgrade_Spec = { # combo with T250_RdScrn2C_SovaDgrade_Spec
   'ATTRIBUTE'    : 'IS_2D_DRV',
   'DEFAULT'      : 'default',
   'default'      : {}, # fail-safe
   1              : {
       'ATTRIBUTE'    : 'BG',
       'DEFAULT'      : 'OEM',
       'SBS'          : {}, # fail-safe
       'OEM'          : {
          'ATTRIBUTE'    : 'HGA_SUPPLIER',
          'DEFAULT'      : 'FailSafe',
          'FailSafe'     : {}, # fail-safe
          'RHO'          : {
                ('P250_ERROR_RATE_BY_ZONE', 'mean')  : {
                   'spc_id'       : 15,
                   'col_sort'     : ('DATA_ZONE'),
                   'column'       : ('RAW_ERROR_RATE',),
                   'compare'      : (            '>',),
                   'criteria'     : (           -2.32,),
                },
                ('P250_ERROR_RATE_BY_ZONE', 'min')  : {
                   'spc_id'       : 15,
                   'col_sort'     : ('DATA_ZONE'),
                   'column'       : ('RAW_ERROR_RATE',),
                   'compare'      : (            '>',),
                   'criteria'     : (           -2.77,),
                },
                ('Title','')      : 'T250_RdScrn2C_SovaDgrade_Spec',
          },
       },
    },
}


T250_RdScrn2H_Combo_Spec = { # combo with T250_RdScrn2H_SqzWrite_Spec
   'RdScrn2H_FNC2_Delta'   : { # 0.06,
      'ATTRIBUTE'    : 'BG',
      'DEFAULT'      : 'OEM',
      'SBS'          : 99.0, # fail-safe
      'OEM'          : {
         'ATTRIBUTE'    : 'HGA_SUPPLIER',
         'DEFAULT'      : 'FailSafe',
         'FailSafe'     : 99.0,
         'RHO'          : 0.15, #ori 0.06
      },
   },
   'RdScrn2H_Avg'          : { # -2.5,
      'ATTRIBUTE'    : 'BG',
      'DEFAULT'      : 'OEM',
      'SBS'          : 99.0, # fail-safe
      'OEM'          : {
         'ATTRIBUTE'    : 'HGA_SUPPLIER',
         'DEFAULT'      : 'FailSafe',
         'FailSafe'     : 99.0,
         'RHO'          : -2.4, #ori -2.5
      },
   },
}

T135_AFH_Clr_Screen_Spec = {
   'ATTRIBUTE'    : 'nextState',
   'DEFAULT'      : 'default',
   'default'      : {}, # fail-safe
   'AFH1'         : {
      'ATTRIBUTE'    : 'BG',
      'DEFAULT'      : 'OEM',
      'SBS'          : {}, # fail-safe
      'OEM'          : {
         'ATTRIBUTE' : 'HGA_SUPPLIER',
         'DEFAULT'   : 'HWY',
         'RHO'       : {
             'ATTRIBUTE' : 'AABType',
             'DEFAULT'   : '501.16',
             '501.16'        : {
            ('P135_FINAL_CONTACT', 'match')      : {
               'col_range'    : [148], 
               'column'       : ('MSRD_INTRPLTD','WRT_CNTCT_DAC','RD_CLR',),
               'compare'      : (           '==',           '==',     '<',),
               'criteria'     : (            'I',             -1,    68.0,), # RH HO Clr
            },
            ('Title','')      : 'T135_AFH_Clr_Screen_Spec',
            },
             '501.42'        : {
            ('P135_FINAL_CONTACT', 'match')      : {
               'col_range'    : [148], 
               'column'       : ('MSRD_INTRPLTD','WRT_CNTCT_DAC','RD_CLR',),
               'compare'      : (           '==',           '==',     '<',),
               'criteria'     : (            'I',             -1,    40.0,), # RH HO Clr
            },
            ('Title','')      : 'T135_AFH_Clr_Screen_Spec',
            },
         },
         'HWY'       : {
            ('P135_FINAL_CONTACT', 'match')      : {
               'col_range'    : [148], 
               'column'       : ('MSRD_INTRPLTD','WRT_CNTCT_DAC','RD_CLR',),
               'compare'      : (           '==',           '==',     '<',),
               'criteria'     : (            'I',             -1,    72.0,), # RH HO Clr
            },
            ('Title','')      : 'T135_AFH_Clr_Screen_Spec',
         },
      },
   },
}

T250_ReadScreen_Spec = {
   'ATTRIBUTE'    : 'BG',
   'DEFAULT'      : 'ON',
   # 'SBS'          : {}, # fail-safe
   'ON'           : {
      'ATTRIBUTE'    : 'nextState',
      'DEFAULT'      : 'default',
      'default'      : {}, # fail-safe
      'READ_SCRN2H'  : {
         ('P250_ERROR_RATE_BY_ZONE', 'max')   : {
            'spc_id'       : 16,
            'column'       : ('RAW_ERROR_RATE',),
            'compare'      : (             '>',),
            'criteria'     : (           -2.25,),
         },
         ('P250_ERROR_RATE_BY_ZONE', 'mean')   : {
            'spc_id'       : 16,
            'column'       : ('RAW_ERROR_RATE',),
            'compare'      : (             '>',),
            'criteria'     : (           -2.35,),
         },
         ('Title','')      : 'T250_ReadScreen_Spec',
      },
   },
}
MarginalSovaMeanHMS_CAP = {
   'ATTRIBUTE'    : 'BG',
   'DEFAULT'      : 'ON',
   'SBS'          : {}, # fail-safe
   'ON'           : {
      'ATTRIBUTE'    : 'nextState',
      'DEFAULT'      : 'default',
      'default'      : {}, # fail-safe
      'READ_SCRN2H'  : 2.5,
    },
}
MarginalSovaHDIntabilityCombo = {
   'ATTRIBUTE'    : 'BG',
   'DEFAULT'      : 'OEM',
   'SBS'          : {}, # fail-safe
   'OEM'          : {
        'Mean_MODE_LOSS'     : 0.043,
        'Mean_SIGMA_LOSS'    : 0.036,
        'P250_MeanDELTA_BER' : 0.0345,
        'DRV_WPE_UINC'       : 2.8,
    },
}

PoorSovaHDInstCombo_Spec1 = {
   'ATTRIBUTE'    : 'IS_2D_DRV',
   'DEFAULT'      : 0,
   0              : {}, #fail-safe
   1              : {
       'ATTRIBUTE'    : 'BG',
       'DEFAULT'      : 'OEM',
       'SBS'          : {}, # fail-safe
       'OEM'          : {
            'ATTRIBUTE'    : 'HGA_SUPPLIER',
            'DEFAULT'      : 'FailSafe',
            'FailSafe'     : {}, # fail-safe
            'RHO'          : {
                'Mean_MODE_LOSS'     : 0.098,
                'Mean_SIGMA_LOSS'    : 0.026,
                'Drive_WPE_uinch'    : 2.55,
            },
        },
   },
}

PoorSovaHDInstCombo_Spec2 = {
   'ATTRIBUTE'    : 'IS_2D_DRV',
   'DEFAULT'      : 0,
    0             : {},
    1             : {
       'ATTRIBUTE'    : 'BG',
       'DEFAULT'      : 'OEM',
       'SBS'          : {}, # fail-safe
       'OEM'          : {
          'ATTRIBUTE'    : 'HGA_SUPPLIER',
          'DEFAULT'      : 'FailSafe',
          'FailSafe'     : {}, # fail-safe
          'RHO'          : {
                'ATTRIBUTE'    : 'nextState',
                'DEFAULT'      : 'FailSafe',
                'FailSafe'     : {}, # fail-safe
                'SQZ_WRITE2'   : {
                            'MAX_BER' : { ('P250_ERROR_RATE_BY_ZONE', 'max')   : {
                                          'spc_id'       : 30,         # sqz write 2 spcid only
                                          'col_sort'     : ('DATA_ZONE'),
                                          'col_range'    : {'EQUATION' : "[zn for zn in xrange(self.dut.numZones) if zn not in TP.UMP_ZONE[self.dut.numZones]]"},
                                          'column'       : ('RAW_ERROR_RATE'),
                                          'compare'      : (            '>='),
                                          'criteria'     : (          -1.66),
                                        },
                            },
                            'Drive_WPE_uinch' : 2.55,
                },
            },
        },
    },
}

PoorSovaHDInstCombo_Spec3 = {
   'ATTRIBUTE'    : 'IS_2D_DRV',
   'DEFAULT'      : 0,
    0             : {},
    1             : {
       'ATTRIBUTE'    : 'BG',
       'DEFAULT'      : 'OEM',
       'SBS'          : {}, # fail-safe
       'OEM'          : {
          'ATTRIBUTE'    : 'HGA_SUPPLIER',
          'DEFAULT'      : 'FailSafe',
          'FailSafe'     : {}, # fail-safe
          'RHO'          : {
                'ATTRIBUTE'    : 'nextState',
                'DEFAULT'      : 'FailSafe',
                'FailSafe'     : {}, # fail-safe
                'HEAD_SCRN3'   : {
                            'mean_mode_loss'  : 0.135,
                            'mean_sigma_loss' : 0.03,
                            'Delta_MRE'       : 4,
                },
            },
        },
    },
}


T185_RDG_Screen_Spec = { #2D
   'ATTRIBUTE'    : 'BG',
   'DEFAULT'      : 'OEM',
   'SBS'          : {}, # fail-safe
   'OEM'          : {
      'ATTRIBUTE'  : 'PART_NUM',
      'DEFAULT'    : 'default',
      'default'    : 2500,
      '1R8174-0E0' : 2500,
    },
}
T185_RDG_Screen_Spec2 = { 
   'ATTRIBUTE'    : 'BG',
   'DEFAULT'      : 'OEM',
   'SBS'          : {}, # fail-safe
   'OEM'          : {
       'ATTRIBUTE'    : 'IS_2D_DRV',
       'DEFAULT'      : 0,
        0 : 5000,
        1 : 6000, 
   },
}

T135_AFH2_RD_Clr_Screen_Spec = {
   'ATTRIBUTE'    : 'BG',
   'DEFAULT'      : 'OEM',
   'SBS'          : {}, # fail-safe
   'OEM'          : {
       'ATTRIBUTE'    : 'nextState',
       'DEFAULT'      : 'default',
       'default'      : {}, # fail-safe
       'AFH2'         : {
          'ATTRIBUTE' : 'HGA_SUPPLIER',
          'DEFAULT'   : 'RHO',
          'RHO'       : {
             'ATTRIBUTE' : 'AABType',
             'DEFAULT'   : '501.16',
             '501.16'        : {
                 'ATTRIBUTE' : 'PART_NUM',
                 'DEFAULT'   : 'default',
                 'default'       : {
                    ('P135_FINAL_CONTACT', 'mean')      : {
                       'spc_id'       : 20000,
                       'msrd_intrpltd': 'M',
                       'active_heater': 'R',            
                       'col_sort'     : ('DATA_ZONE'),
                       'col_range'    : [0,13,31], 
                       'column'       : ('RD_CLR'),
                       'compare'      : (     '<'),
                       'criteria'     : (      85.0),
                    },
                 },
                 '1R8174-0E0'       : {
                    ('P135_FINAL_CONTACT', 'mean')      : {
                       'spc_id'       : 20000,
                       'msrd_intrpltd': 'M',
                       'active_heater': 'R',            
                       'col_sort'     : ('DATA_ZONE'),
                       'col_range'    : [0,13,31], 
                       'column'       : ('RD_CLR'),
                       'compare'      : (     '<'),
                       'criteria'     : (      85.0),
                    },
                 },
             },
             '501.42'        : {
                 ('P135_FINAL_CONTACT', 'mean')         : {
                    'spc_id'       : 20000,
                    'msrd_intrpltd': 'M',
                    'active_heater': 'R',            
                    'col_sort'     : ('DATA_ZONE'),
                    'col_range'    : [0,13,31], 
                    'column'       : ('RD_CLR'),
                    'compare'      : (     '<'),
                    'criteria'     : (      70.0),
                    },
             },
          },
          'TDK'       : {
             ('P135_FINAL_CONTACT', 'mean')      : {
                'spc_id'       : 20000,
                'msrd_intrpltd': 'M',
                'active_heater': 'R',            
                'col_range'    : [0,13,31], 
                'column'       : ('RD_CLR'),
                'compare'      : (     '<'),
                'criteria'     : (      103.0),
             },
          },
       },
   },
}

T33_ReZap_Trigger_Limit = {
   ('P033_PES_HD2', 'max')   : {
      'column'       : ('RRO',),
      'compare'      : (  '>',),
      'criteria'     : (  6.5,),
   },
}

T33_RRO_Check = { #Mobile survillience
   'ATTRIBUTE'    : 'PART_NUM',
   'DEFAULT'      : 'Default',
   'Default'      : {},
   '2G3172-900'   : {
   ('P033_PES_HD2', 'max')   : {
      'column'       : ('RRO',),
      'compare'      : (  '>',),
      'criteria'     : (  4,),
                },
   },
   '2G2174-900'   : {
   ('P033_PES_HD2', 'max')   : {
      'column'       : ('RRO',),
      'compare'      : (  '>',),
      'criteria'     : (  5,),
                },
   },
}

T33_NRRO_Check = { #Mobile survillience
   'ATTRIBUTE'    : 'PART_NUM',
   'DEFAULT'      : 'Default',
   'Default'      : {},
   '2G3172-900'   : {
   ('P033_PES_HD2', 'max')   : {
      'column'       : ('NRRO',),
      'compare'      : (  '>',),
      'criteria'     : (  4,),
                },
   },
   '2G2174-900'   : {
   ('P033_PES_HD2', 'max')   : {
      'column'       : ('NRRO',),
      'compare'      : (  '>',),
      'criteria'     : (  7,),
                },
   },
}

T25_LCUR_Check = { #Mobile survillience
   'ATTRIBUTE'    : 'PART_NUM',
   'DEFAULT'      : 'Default',
   'Default'      : {},
   '2G3172-900'   : {
   ('P025_LD_UNLD_PARAM_STATS', 'max')   : {
      'column'       : ('STATISTIC_NAME',   'LOAD_MAX_CUR'),
      'compare'      : ('=='            ,    '<'          ),
      'criteria'     : ('MAX'           ,     -240        ),
     },
   },
   '2G2174-900'   : {
   ('P025_LD_UNLD_PARAM_STATS', 'max')   : {
      'column'       : ('STATISTIC_NAME',   'LOAD_MAX_CUR'),
      'compare'      : ('=='            ,    '<'          ),
      'criteria'     : ('MAX'           ,     -310        ),
     },
   },
}
T25_ULCUR_Check = { #Mobile survillience
   'ATTRIBUTE'    : 'PART_NUM',
   'DEFAULT'      : 'Default',
   'Default'      : {},
   '2G3172-900'   : {
   ('P025_LD_UNLD_PARAM_STATS', 'max')   : {
      'column'       : ('STATISTIC_NAME',   'ULD_MAX_CUR'),
      'compare'      : ('=='            ,   '>'          ),
      'criteria'     : ('MAX'           ,   160          ),
     },
   },
   '2G2174-900'   : {
   ('P025_LD_UNLD_PARAM_STATS', 'max')   : {
      'column'       : ('STATISTIC_NAME',   'ULD_MAX_CUR'),
      'compare'      : ('=='            ,   '>'          ),
      'criteria'     : ('MAX'           ,   270          ),
     },
   },
}


SerFmt_OCLIM = 369 # 171H or 9%
SerFmt_OTF_Spec = 6.8 # screening spec for serial format OTF error rate
SerFmt_OTF_Combo_Spec = {  # combo screening spec for serial format OTF error rate
   'ATTRIBUTE'       : 'IS_2D_DRV',
   'DEFAULT'         : 0,
   0                 : 7.4,  
   1                 : 0,    #no spec for 2D yet
}
SerFmt_RAW_Combo_Spec = {  # combo screening spec for serial format RAW error rate
   'ATTRIBUTE'       : 'IS_2D_DRV',
   'DEFAULT'         : 0,
   0                 : 1.77, 
   1                 : 0,    #no spec for 2D yet
}
SerFmt_Screen_Ignore_Zone = [149,] # zones to ignore during serial format screening

if testSwitch.virtualRun:
   truput_ve_data_pass = """
      T3C000,,,,,8,,
              Cyl   Head  Band  Throughput  CalThruput
      Hd  Zn  Skew  Skew  Skew  (MB/s)      (MB/s)      Ratio   StartLBA       EndLBA
      0   00  1E    78    1E      0.000       0.000     0.000   FFFFFFFFFFFFFFFF   FFFFFFFFFFFFFFFF invalid address
      0   01  1E    78    1E      0.000       0.000     0.000   FFFFFFFFFFFFFFFF   FFFFFFFFFFFFFFFF invalid address
      0   02  1E    78    1E      0.000       0.000     0.000   FFFFFFFFFFFFFFFF   FFFFFFFFFFFFFFFF invalid address
      0   03  1E    78    1E    130.935     134.569     0.972   0000005496BC   00000056045C
      0   04  1E    78    1E     71.573     137.674     0.519   000000000000   000000017610
      0   05  1E    78    1E     71.393     137.329     0.519   000000253FF8   00000026B518
      0   06  1E    78    1E     71.213     136.984     0.519   0000006E1E48   0000006F9278
      0   07  1E    78    1E     71.034     136.639     0.519   000000A150EC   000000A2C42C
      0   08  1E    78    1E    128.585     132.153     0.973   000000AA9448   000000ABFB58
      0   09  1E    78    1E    128.250     131.808     0.973   000000E7B28F   000000E918AF
      0   0A  1E    78    1E    127.914     131.463     0.973   000001005A83   00000101BFB3
      1   00  1E    78    1E      0.000      71.420     0.000   FFFFFFFFFFFFFFFF   FFFFFFFFFFFFFFFF invalid address
      1   01  1E    78    1E      0.000      71.420     0.000   FFFFFFFFFFFFFFFF   FFFFFFFFFFFFFFFF invalid address
      1   02  1E    78    1E      0.000      71.420     0.000   FFFFFFFFFFFFFFFF   FFFFFFFFFFFFFFFF invalid address
      1   03  1E    78    1E    135.299     139.054     0.972   000000315A76   00000032D446
      1   04  1E    78    1E     76.416     146.991     0.519   0000000C20B8   0000000DB018
      1   05  1E    78    1E     76.236     146.646     0.519   00000018B1E8   0000001A4058
      1   06  1E    78    1E     75.877     145.955     0.519   000000828D11   0000008419A1
      1   07  1E    78    1E     75.698     145.610     0.519   00000097B71A   0000009942BA
      1   08  1E    78    1E    133.285     136.984     0.972   000000BA2EDA   000000BBA30A
      1   09  1E    78    1E    131.943     135.604     0.973   000000CBFE23   000000CD6E93
      1   0A  1E    78    1E    131.943     135.604     0.973   0000010C8FE7   0000010E0057
   """
CRT2_T297_WPE_Screen = {
   'T297_Avg_ModeLoss'  : { # 0.055,
      'ATTRIBUTE'    : 'BG',
      'DEFAULT'      : 'OEM',
      'SBS'          : 999.0, # fail-safe
      'OEM'          : 0.055,
   },
   'T297_Avg_SigmaLoss' : { # 0.02,
      'ATTRIBUTE'    : 'BG',
      'DEFAULT'      : 'OEM',
      'SBS'          : 999.0, # fail-safe
      'OEM'          : 0.02,
   },
   'T069_WPE_uin'       : { # 3.15,
      'ATTRIBUTE'    : 'BG',
      'DEFAULT'      : 'OEM',
      'SBS'          : 999.0, # fail-safe
      'OEM'          : 3.15,
   },
}
   
#hot SOC temp screening criteria
if testSwitch.CHEOPSAM_LITE_SOC:
   hotSOC_temp_crt = { #CheopsLite SOC
      'ATTRIBUTE'       : 'IS_2D_DRV',
      'DEFAULT'         : 0,
      0                 : 32.99, 
      1                 : 32.99, 
   }
else:
   hotSOC_temp_crt = { #CheopsAM SOC
      'ATTRIBUTE'       : 'IS_2D_DRV',
      'DEFAULT'         : 0,
      0                 : 35.0, #1D spec. Based on correlation study, spec = 33.39C. 1D core team suggested to use 35C
      1                 : 35.0, #2D spec. Based on correlation study, spec = 32.86C. 2D core team suggested to use 35C
   }

Precautionary_Opti_Prm = {
      'test_num':256, 
      'prm_name':'Precautionary CH Opti_LUT',
      'ZONE_POSITION': 198,    
      'SET_OCLIM': 819,
      'BIT_MASK': (0L, 1L), #(4228L, 8463L), #zone neutral
      'BIT_MASK_EXT': (0L, 0L), #(33825L, 34882L), #zone neutral
      'timeout' : 18000,
      'NUM_READS': 100
   }

Precautionary_Opti_Prm_ATE = Precautionary_Opti_Prm.copy()
Precautionary_Opti_Prm_ATE.update({
      'prm_name':'Preacutionary CH Opti_ATE',
      'CWORD1' : 0x9642, 
      'SQZ_OFFSET' : 52,
      'spc_id': 1,
      'MOVING_BACKOFF' : 5,
})
Precautionary_Opti_Prm_ATW = Precautionary_Opti_Prm.copy()
Precautionary_Opti_Prm_ATW.update({
      'prm_name':'Preacutionary CH Opti_ATW',
      'CWORD1' : 0x9644, 
      'NUM_SQZ_WRITES' : 400,
      'spc_id': 2,
      'MOVING_BACKOFF' : 100,
})
Precautionary_Opti_Prm_WW = Precautionary_Opti_Prm.copy()
Precautionary_Opti_Prm_WW.update({
      'prm_name':'Preacutionary CH Opti_WW',
      'CWORD1' : 0x9641, 
      'CLEARANCE_OFFSET' : 400,
      'spc_id': 3,
      'MOVING_BACKOFF' : 50,
})

