#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: All global constants live within this file
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Constants.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Constants.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#

import Test_Switches
from Test_Switches import testSwitch

if testSwitch.winFOF == 1:
   from cmEmul import *
import sys
CE, CP, CN, CV = ConfigId  #Equip, Product, Name, Version from Config
#except:
#   CE, CP, CN, CV = ConfigId = ("", "", "", "") #Exception case when not running in CM: Magill

CHAMBER_TYPES = ['B2D', 'B2D2','SP240', 'GEMINI', 'STC', 'MANUAL']
HOST_ID_MSG = '''Gemini systems must have the following hostID format in /var/merlin/host/siteconfig.py
The Host_ID is an 8-digit alpha-numeric, and the format is PPFLLXXX where:
PP  = 2-digit Plant Location ID (AK [AMK], LC [LCO], OK [OKlahoma], SH [SHR], SS [Suzhou], TC [TCO], TK [ Thailand], WX [Wuxi])
 F  = 1-digit Plant Floor location
LL  = 2-digit Plant Line location
 S  = 1-digit Gemini chamber Type  (C [STC], G [GEMINI], L [SP240], R [SP240], U [B2D])
XX  = 2-digit system serial number
Note that this ID should be unique for each Gemini system!'''


DEF_BAUD = Baud38400
PROCESS_HDA_BAUD = Baud460800

baudSet = {     Baud38400  : "\x00\x00\x01\x00",
                Baud115200 : "\x00\x00\x02\x00",
                Baud390000 : "\x00\x00\x03\x00",
                Baud460800 : "\x00\x00\x04\x00",
                Baud625000 : "\x00\x00\x05\x00",
                Baud921600 : "\x00\x00\x06\x00",
                Baud1228000: "\x00\x00\x07\x00",
}
if testSwitch.BF_0152393_231166_P_RE_ADD_LEGACY_ESLIP_PORT_INCR_TMO:
   baudSet_timeout = 30
else:
   baudSet_timeout = 2

OK          = 0
NOT_OK      = -1
ON          = 1
OFF         = 0
DEBUG       = 0
TIMED       = 0
STX         = '\x02'
ETX         = '\x03'
EOT         = '\x04'
ENQ         = '\x05'
SACK        = '\x06'
SNAK        = '\x15'
ACK         = '\x01'
NAK         = '\x02'
ESC         = '\x1B'
END         = '\xC0'
CTRL_B      = '\x02'
CTRL_E      = '\x05'
CTRL_D      = '\x04'
CTRL_I      = '\x09'
CTRL_L      = '\x0c'
CTRL_R      = '\x12'
CTRL_T      = '\x14'
CTRL_X      = "\030"
CTRL_Z      = '\x1A'
CTRL_BKT    = '\x1D'
CTRL_U      = '\x15'
CTRL_W      = '\x17'
CTRL_A      = '\x01'
CTRL_C      = '\x03'
CTRL_N      = '\x0e'
CTRL_O      = '\x0f'
CTRL_U      = '\x15'
CTRL_W      = '\x17'
CTRL_Y      = '\x19'
CTRL_       = '\x1f'
CR          = '\x0D'
DOT         = '.'
MAX_PORTS   = 4
MAX_5V      = 5550
MIN_5V      = 3000
MODULE  = 0
METHOD  = 1
TRANS   = 2
OPT     = 3
DBLOG_EOL_CHAR = "\n"
SHIFT_4='\x24'

# CPC Write, Read and Serial buffer definitions
WBF = 1  # Write  Buffer select on FillBuff*** commands
RBF = 2  # Read   Buffer select on FillBuff*** commands
BWR = 3  # Both Write and Read Buffer select on FillBuff*** commands
SBF = 4  # Serial Buffer select on FillBuff*** commands

# TestParameter retry mode definitions
POWER_CYCLE_RETRY = 0
HARD_RESET_RETRY = 1

ENABLE = 1
DISABLE = 0

AFH_Uniform_Track_Lbl = "UniformTrack"
INVALID_HD = 0xFF
#These will prevent parametric upload with dex and will affect ADG parsing
ST_SUPPRESS__NONE                  = 0
ST_SUPPRESS__ALL                   = 1
ST_SUPPRESS__CM_OUTPUT             = 2
ST_SUPPRESS_SUPR_CMT               = 4
ST_SUPPRESS_RECOVER_LOG_ON_FAILURE = 8


TEST_PASSED = 0
PASS = 1
FAIL = 0
SKIP = -1
OFF = 0
ON = 1

PF3_Changlist = "1174429"
PF3_Branch    = "//depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B"
PFE_RELEASE_NOTES = "1174429"
PF3_BUILD_TARGET = "Amazon.RL42"

# Constants to override system settings under "PRODUCTION_MODE"
productionMaxEventSize        = None

# Serial Port constants
CPC_WRITE_BUFFER              = 0x01
CPC_SERIAL_BUFFER             = 0x04

PASS_RETURN = {'LLRET':OK}
FAIL_RETURN = {'LLRET':-1}

IO_CRC_RETRY_VAL              = 20              # Maximum per-command retries for CRC errors
MAX_INITIATOR_BUFFER_BLK_SIZE = 19711
SN50CList                     =  ['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F']
SN_FIELD_WIDTH                = 8

# Conversion constants
ANGS_PER_NM                   = 10.0   # Angstroms per nanometer used on clearance algorithms.

#Diag Unlock Command
UNLOCK_CMD = 'C34F329A'

#Tier Tab constants
TIER1 = 'T01'
TIER2 = 'T02'
TIER3 = 'T03'
TIERX = 'T0.' #used for all match

_pyver = sys.version_info
PYTHON_VERSION = _pyver[0] + (_pyver[1])/10.0 + (_pyver[2])/100.0 #construct 2.72 or 2.41 etc
PY_27 = PYTHON_VERSION > 2.69
PY_24 = PYTHON_VERSION < 2.50

#FDE/TCG/OPAL/SED/ISE/FIPS/SD&D constants
SECURED_DIAG_AND_DOWNLOAD  = 'SECURED BASE (SD AND D)'
DRM_SCSA  = 'DRM_SCSA'
SECURED_DIAG_AND_DOWNLOAD_TYPES = [SECURED_DIAG_AND_DOWNLOAD,
                                   DRM_SCSA]

TCG_ENTERPRISE_SSC_1_0_FDE = 'TCG ENTERPRISE SSC 1.0 FDE'
TCG_OPAL_1_SED             = 'TCG OPAL SSC 1.0 FDE'
TCG_OPAL_2_SED             = 'TCG OPAL 2 SED'
ISE                        = 'INSTANT_SECURE_ERASE_DRIVE'
FIPS_SED                   = 'FDE BASE FIPS 140-2'