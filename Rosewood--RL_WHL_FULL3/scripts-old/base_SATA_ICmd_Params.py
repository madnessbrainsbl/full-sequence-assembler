#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Implements a basic ICmd interface
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/09/20 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_SATA_ICmd_Params.py $
# $Revision: #2 $
# $DateTime: 2016/09/20 03:10:55 $
# $Author: phonenaing.myint $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_SATA_ICmd_Params.py#2 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from base_Initiator_Cmd_Params import *

HardReset = {
   'test_num'              : 535,
   'prm_name'              : 'base_prm_535_SataHardReset',
   'spc_id'                : 1,
   'TEST_OPERATING_MODE'   : 0x000B,
   }

SequentialWriteDMAExt = {
   'test_num'              : 510,
   'prm_name'              : 'SequentialWriteDMAExt',
   'spc_id'                : 1,
   'timeout'               : 252000,
   'CTRL_WORD1'            : 0X0000,
   'CTRL_WORD2'            : 0X0000,
   'WRITE_READ_MODE'       : 0x02,                 # Write Mode
   'STARTING_LBA'          : (0, 0, 0, 0),
   'BLKS_PER_XFR'          : 256,
   'DATA_PATTERN0'         : (0, 0),
   'PATTERN_MODE'          : 0x80,
   }

ZeroCheck = {
   'test_num'              : 510,
   'prm_name'              : 'ZeroCheck',
   'spc_id'                : 1,
   'timeout'               : 252000,
   'CTRL_WORD1'            : 0X0000,
   'CTRL_WORD2'            : 0X0000,
   'WRITE_READ_MODE'       : 0x01,                 # Read Mode
   'STARTING_LBA'          : (0, 0, 0, 0),
   'BLKS_PER_XFR'          : 256,
   'DATA_PATTERN0'         : (0, 0),
   'PATTERN_MODE'          : 0x80,
   'ENABLE_HW_PATTERN_GEN' : 1,
   }

SequentialReadDMAExt = {
   'test_num'              : 510,
   'prm_name'              : 'SequentialReadDMAExt',
   'spc_id'                : 1,
   'timeout'               : 252000,
   'CTRL_WORD1'            : 0X0000,
   'CTRL_WORD2'            : 0X0000,
   'WRITE_READ_MODE'       : 0x01,                 # Read Mode
   'STARTING_LBA'          : (0, 0, 0, 0),
   'BLKS_PER_XFR'          : 256,
   'DATA_PATTERN0'         : (0, 0),
   'PATTERN_MODE'          : 0x80,
   }

SequentialWRDMAExt = {
   'test_num'              : 510,
   'prm_name'              : 'SequentialWRDMAExt',
   'spc_id'                : 1,
   'timeout'               : 252000,
   'CTRL_WORD1'            : 0X0000,
   'CTRL_WORD2'            : 0X0000,
   'WRITE_READ_MODE'       : 0x00,                 # Write/Read Mode
   'STARTING_LBA'          : (0, 0, 0, 0),
   'BLKS_PER_XFR'          : 256,
   'DATA_PATTERN0'         : (0, 0),
   'PATTERN_MODE'          : 0x80,
   }

SequentialWriteVerify = {
   'test_num'              : 510,
   'prm_name'              : 'SequentialWriteVerify',
   'spc_id'                : 1,
   'timeout'               : 252000,
   'CTRL_WORD1'            : 0X0000,               # Write/Read Mode
   'CTRL_WORD2'            : 0X0000,
   'STARTING_LBA'          : (0,0,0,0),
   'BLKS_PER_XFR'          : 256,
   'DATA_PATTERN0'         : (0,0),
   'CTRL_WORD2'            : 0x80,
   }

Bit_to_Bit_cmp = {
   'test_num'              : 551,
   'prm_name'              : 'Bit_to_Bit_cmp',
   'spc_id'                : 1,
   'timeout'               : 252000,
   'CTRL_WORD1'            : 0,                    # 0x10 = read only, >> 4
                                                   # 0x20 = write only
                                                   # 0x00 = write/read
                                                   # 1 = fast mode >> 0
                                                   # 0 is normal mode
                                                   # access mode = 0 is seq >> 1
   }

RandomWriteDMAExt = {
   'test_num'              : 510,
   'prm_name'              : 'RandomWriteDMAExt',
   'spc_id'                : 1,
   'timeout'               : 252000,
   'CTRL_WORD1'            : 0X0000,
   'CTRL_WORD2'            : 0X0000,
   'WRITE_READ_MODE'       : 0x02,                 # Write Mode
   'ACCESS_MODE'           : 0x01,                 # Random
   'STARTING_LBA'          : (0, 0, 0, 0),
   'BLKS_PER_XFR'          : 256,
   'DATA_PATTERN0'         : (0, 0),
   'PATTERN_MODE'          : 0x80,
   }

RandomReadDMAExt = {
   'test_num'              : 510,
   'prm_name'              : 'RandomReadDMAExt',
   'spc_id'                : 1,
   'timeout'               : 252000,
   'CTRL_WORD1'            : 0X0000,
   'CTRL_WORD2'            : 0X0000,
   'WRITE_READ_MODE'       : 0x01,                 # Read Mode
   'ACCESS_MODE'           : 0x01,                 # Random
   'STARTING_LBA'          : (0, 0, 0, 0),
   'BLKS_PER_XFR'          : 256,
   'DATA_PATTERN0'         : (0, 0),
   'PATTERN_MODE'          : 0x80,
   }

RandomWRDMAExt = {
   'test_num'              : 510,
   'prm_name'              : 'RandomWRDMAExt',
   'spc_id'                : 1,
   'timeout'               : 252000,
   'CTRL_WORD1'            : 0X0000,
   'CTRL_WORD2'            : 0X0000,
   'WRITE_READ_MODE'       : 0x00,                 # Write/Read Mode
   'ACCESS_MODE'           : 0x01,                 # Random
   'STARTING_LBA'          : (0, 0, 0, 0),
   'BLKS_PER_XFR'          : 256,
   'DATA_PATTERN0'         : (0, 0),
   'PATTERN_MODE'          : 0x80,
   }

BufferCompareTest = {
   'test_num'              : 643,
   'prm_name'              : 'BufferCompareTest',
   'TEST_FUNCTION'         : 0x10,
   'STARTING_LBA'          : (0, 0, 0, 0),
   'TOTAL_BLKS_TO_XFR64'   : (0, 0, 0, 1000 ),
   'BUFFER_LENGTH'         : (0, 512),
   'LOOP_COUNT'            : 1,
   }

WritePatternToBuffer = {
   'test_num'              : 508,
   'prm_name'              : 'WritePatternToBuffer',
   'timeout'               : 600,
   'CTRL_WORD1'            : 0x0000,
   'BUFFER_LENGTH'         : (0, 512),
   'BYTE_OFFSET'           : (0, 0),
   'DATA_PATTERN0'         : (0, 0),
   'DATA_PATTERN1'         : (0, 0),
   'stSuppressResults'     : ST_SUPPRESS__ALL,
   }

DisplayBufferData = {
   'test_num'              : 508,
   'prm_name'              : 'DisplayWriteBuffer',
   'timeout'               : 600,
   'CTRL_WORD1'            : 0x0004,
   'BUFFER_LENGTH'         : (0, 512),
   'stSuppressResults'     : ST_SUPPRESS__ALL,    
   }

CompareBuffers = {
   'test_num'              : 508,
   'prm_name'              : 'CompareBuffers',
   'timeout'               : 600,
   'CTRL_WORD1'            : 0x0008,
   'BUFFER_LENGTH'         : (0, 512),
   'BYTE_OFFSET'           : (0, 0),
   'stSuppressResults'     : ST_SUPPRESS__ALL,
   }

BufferCopy = {
   'test_num'              : 508,
   'prm_name'              : 'BufferCopy',
   'timeout'               : 600,
   'CTRL_WORD1'            : 0x0007,
   'BUFFER_LENGTH'         : (0, 512),
   'BYTE_OFFSET'           : (0, 0),
   'stSuppressResults'     : ST_SUPPRESS__ALL,
   }

SetFeaturesParameter = {
   'test_num'              : 538,
   'prm_name'              : 'SetFeatures',
   'timeout'               : 600,
   'FEATURES'              : 0,
   'SECTOR_COUNT'          : 0,
   'SECTOR'                : 0,
   'CYLINDER'              : 0,
   'COMMAND'               : 0xEF,
   'HEAD'                  : 0,
   'DEVICE'                : 0,
   'PARAMETER_0'           : 0,
   }

SmartParameter = {
   'test_num'              : 538,
   'prm_name'              : 'Smart',
   'timeout'               : 600,
   'FEATURES'              : 0,
   'SECTOR_COUNT'          : 1,
   'COMMAND'               : 0xB0,
   'LBA_LOW'               : 0,
   'LBA_MID'               : 0x4F,
   'LBA_HIGH'              : 0xC2,
   'PARAMETER_0'           : 0x2000                      # Enables LBA mode cmd reg defs
   }

Seek_LBA = {
   'test_num': 538,
   'prm_name': 'Seek_LBA',
   'timeout':  600,
   'FEATURES': 0,
   'SECTOR_COUNT': 1,
   'COMMAND':  0x42, #Read Verify Ext - Non Data
   'DEVICE': 0x40,
   'PARAMETER_0': 0x2000 #enables LBA mode cmd reg defs
}

Seek_CHS = {
   'test_num': 538,
   'prm_name': 'Seek_CHS',
   'timeout':  600,
   'FEATURES': 0,
   'SECTOR_COUNT': 0,
   'SECTOR':0,
   'CYLINDER':(0),
   'COMMAND': 0x70, #Physical Seek
   'HEAD': 0,
   'DEVICE':0,
   'PARAMETER_0':0, #0x2000 enables LBA mode cmd reg defs
}

WriteTestMobile = {
   'test_num'              : 510,
   'prm_name'              : 'WriteTestMobile',
   'spc_id'                : 1,
   'timeout'               : 252000,
   'CTRL_WORD1'            : 0x0021,
   'CTRL_WORD2'            : 0X0000,
   'STARTING_LBA'          : (0, 0, 0, 0),
   'BLKS_PER_XFR'          : 256,
   'DATA_PATTERN0'         : (0, 0),
   'PATTERN_MODE'          : 0x01,
   }

Standby = {
   'test_num'              : 538,
   'prm_name'              : 'Standby',
   'timeout'               : 600,
   'FEATURES'              : 0,
   'SECTOR_COUNT'          : 0,
   'SECTOR'                : 0,
   'CYLINDER'              : 0,
   'COMMAND'               : 0xE2,
   'HEAD'                  : 0,
   'DEVICE'                : 0,
   'PARAMETER_0'           : 0,
   }

StandbyImmed = Standby.copy()
StandbyImmed.update({
   'COMMAND'               : 0xE0,
   'prm_name'              : 'StandbyImmed',
   })

Idle = {
   'test_num':538,
   'prm_name':'Idle',
   'timeout': 600,
   'FEATURES': 0,
   'SECTOR_COUNT': 0,
   'SECTOR':0,
   'CYLINDER':(0),
   'COMMAND': 0xE3,
   'HEAD': 0,
   'DEVICE':0,
   'PARAMETER_0':0, #0x2000 enables LBA mode cmd reg defs
	}

IdleImmediate = Idle.copy()
IdleImmediate.update({
   'COMMAND': 0xE1,
   'prm_name':'IdleImmediate',
   })

Sleep = {
   'test_num':538,
   'prm_name':'Sleep',
   'timeout': 600,
   'FEATURES': 0,
   'SECTOR_COUNT': 0,
   'SECTOR':0,
   'CYLINDER':(0),
   'COMMAND': 0xE6,
   'HEAD': 0,
   'DEVICE':0,
   'PARAMETER_0':0, #0x2000 enables LBA mode cmd reg defs
	}

CheckPowerMode = {
   'test_num':538,
   'prm_name':'CheckPowerMode',
   'timeout': 600,
   'FEATURES': 0,
   'SECTOR_COUNT': 0,
   'SECTOR':0,
   'CYLINDER':(0),
   'COMMAND': 0xE5,
   'HEAD': 0,
   'DEVICE':0,
   'PARAMETER_0':0, #0x2000 enables LBA mode cmd reg defs
	}
	
FlushCache = {
   'test_num'              : 538,
   'prm_name'              : 'FlushCache',
   'timeout'               : 600,
   'FEATURES'              : 0,
   'SECTOR_COUNT'          : 0,
   'SECTOR'                : 0,
   'CYLINDER'              : 0,
   'COMMAND'               : 0xE7,
   'HEAD'                  : 0,
   'DEVICE'                : 0,
   'PARAMETER_0'           : 0,
   }

FlushCacheExt = {
   'test_num':538,
   'prm_name':'FlushCacheExt',
   'timeout': 600,
   'FEATURES': 0,
   'SECTOR_COUNT': 0,
   'SECTOR':0,
   'CYLINDER':(0),
   'COMMAND': 0xEA,
   'HEAD': 0,
   'DEVICE':0,
   'PARAMETER_0':0, #0x2000 enables LBA mode cmd reg defs
}

FlushMediaCache = {
   'test_num':538,
   'prm_name':'FlushMediaCache',
   'timeout': 600,
   'FEATURES': 0,
   'SECTOR_COUNT': 0,
   'SECTOR':0,
   'CYLINDER':(0),
   'COMMAND': 0xF7,
   'HEAD': 0,
   'DEVICE':0,
   'PARAMETER_0':0, #0x2000 enables LBA mode cmd reg defs
}

WriteMIFDataToDisc = {
   'test_num'              : 795,
   'prm_name'              : 'Send CCC data to drive',
   'timeout'               : 3600
   }

IdentifyDevice = {
   'test_num'              : 514,
   'prm_name'              : 'prm_514_IdentifyDevice',
   'timeout'               : 120,
   'CTRL_WORD1'            : 0x8003,
   'DblTablesToParse'      : ['P514_IDENTIFY_DEVICE_DATA',],
   'retryECList'           : [10100, ],
   'retryCount'            : 5,
   'retryMode'             : POWER_CYCLE_RETRY,
   }

Recalibrate = {
   'test_num'              : 538,
   'prm_name'              : 'Recalibrate',
   'timeout'               : 600,
   'FEATURES'              : 0,
   'SECTOR_COUNT'          : 0,
   'SECTOR'                : 0,
   'CYLINDER'              : 0,
   'COMMAND'               : 0x10,
   'HEAD'                  : 0,
   'DEVICE'                : 0,
   'PARAMETER_0'           : 0,
   }

UnlockFactoryCmds = {
   'test_num'              : 638,
   'prm_name'              : 'prm_638_Unlock_Seagate',
   'timeout'               : 3600,
   'spc_id'                : 1,
   'DFB_WORD_0'            : 0xFFFF,                     # DITS cmd ID (Unlock Diagnostics)
   'DFB_WORD_1'            : 0x0100,                     # Rev ID
   'DFB_WORD_2'            : 0x9A32,                     # Unlock Seagate Access Key LSW
   'DFB_WORD_3'            : 0x4F03,                     # Unlock Seagate Access Key MSW
   'retryECList'           : [14061, 14029, 14006, 14016,],
   'retryCount'            : 10,
   'retryMode'             : HARD_RESET_RETRY,
   'stSuppressResults'     : ST_SUPPRESS__ALL,
   }

ClearFormatCorrupt = {
   'test_num'              : 638,
   'prm_name'              : 'ClearFormatCorrupt',
   'timeout'               : 3600,
   'spc_id'                : 1,
   'DFB_WORD_0'            : 0x1301,                     # DITS cmd ID (Set Clear Format Corrupt Condition)
   'DFB_WORD_1'            : 0x0100,                     # Rev ID (Usually x0001)
   'DFB_WORD_2'            : 0x0100,                     # LSB_bit_0: 0=Normal operation 1=Clear fmt corrupt
   'DFB_WORD_3'            : 0x0000,
   }

# Sent servo command 2F (Temperature sensor measurement)
GetPreampTemp = {
   'test_num'              : 638,
   'prm_name'              : 'GetPreampTemp',
   'timeout'               : 3600,
   'spc_id'                : 1,
   'DFB_WORD_0'            : 0x4F01,                     # DITS cmd ID
   'DFB_WORD_1'            : 0x0100,                     # Rev ID (Usually x0001)
   'DFB_WORD_2'            : 0x0000,                     # LSB_bit_0=CO, bit_1=O, bit_2=F, bit_3=T,bit_4=D.  MSB = rsvd.
   'DFB_WORD_3'            : 0x2F00,                     # Servo cmd (16 bits, little endian)
   }

LongDST = {
   'test_num'              : 600,
   'prm_name'              : 'LongDST',
   'timeout'               : 54000,
   'spc_id'                : 1,
   'TEST_OPERATING_MODE'   : 2,                          # 1 = short DST, 2 = long DST
   'DELAY_TIME'            : 60,
   }

ShortDST = {
   'test_num'              : 600,
   'prm_name'              : 'ShortDST',
   'timeout'               : 3600,
   'spc_id'                : 1,
   'TEST_OPERATING_MODE'   : 1,                          # 1 = short DST, 2 = long DST
   'DELAY_TIME'            : 10,
   }

WriteFinalAssemblyDate = {
   'test_num'              : 557,
   'prm_name'              : 'WriteFinalAssemblyDate',
   'CTRL_WORD1'            : 0x0001,
   'TEST_FUNCTION'         : 1,                          # 0=Write, 1=Read, 2=Compare to current date, Final Assembly Date Code
   'BYTE_OFFSET'           : (0, 0x0046),
   'FINAL_ASSEMBLY_DATE'   : (0, 0, 0, 0),
   'timeout'               : 600,
   }

if testSwitch.FE_0133768_372897_DMAEXTTRANSRATE_TEST_WITH_T641:
   DMAExtTransRate = {
      'test_num'           : 641,
      'prm_name'           : 'DMAExtTransRate',
      'WRITE_READ_MODE'    : 0,
      'BLKS_PER_XFR'       : 256,
      'DATA_PATTERN0'      : (0, 0),
      'STARTING_LBA'       : (0, 0, 0, 0),
      'TOTAL_BLKS_TO_XFR64': (0, 0, 0 ,0),
      }
else:
   DMAExtTransRate = {
      'test_num'           : 550,
      'prm_name'           : 'DMAExtTransRate',
      'WRITE_READ_MODE'    : 0,
      'FILL_WRITE_BUFFER'  : 1,
      'PATTERN_TYPE'       : 0x80,
      'DATA_PATTERN'       : (0, 0),
      'TOTAL_BLKS_TO_XFR64': (0, 0, 0, 0),
      'MAX_NBR_ERRORS'     : 0,
      }

ExecDeviceDiag = {
   'test_num':538,
   'prm_name':'ExecDeviceDiag',
   'timeout': 600,
   'FEATURES': 0,
   'SECTOR_COUNT': 0,
   'SECTOR':0,
   'CYLINDER':(0),
   'COMMAND': 0x90,
   'HEAD': 0,
   'DEVICE':0,
   'PARAMETER_0':0, #0x2000 enables LBA mode cmd reg defs
   }

WriteBuffer = {
   'test_num'              : 538,
   'prm_name'              : 'WriteBuffer',
   'timeout'               : 600,
   'FEATURES'              : 0,
   'SECTOR_COUNT'          : 0,
   'SECTOR'                : 0,
   'CYLINDER'              : 0,
   'COMMAND'               : 0xE8,
   'HEAD'                  : 0,
   'DEVICE'                : 0,
   'PARAMETER_0'           : 0,
   }

ReadBuffer = {
   'test_num'              : 538,
   'prm_name'              : 'ReadBuffer',
   'timeout'               : 600,
   'FEATURES'              : 0,
   'SECTOR_COUNT'          : 0,
   'SECTOR'                : 0,
   'CYLINDER'              : 0,
   'COMMAND'               : 0xE4,
   'HEAD'                  : 0,
   'DEVICE'                : 0,
   'PARAMETER_0'           : 0,
   }


WriteSectorsExt = {
   'test_num':538,
   'prm_name':'WriteSectorsExt',
   'timeout': 600,
   'FEATURES': 0,
   'SECTOR_COUNT': 0,
   'COMMAND': 0x34,
   'LBA':0,
   'PARAMETER_0': 0x2000 #enables LBA mode cmd reg defs
   }

ReadSectorsExt = {
   'test_num':538,
   'prm_name':'ReadSectorsExt',
   'timeout': 600,
   'FEATURES': 0,
   'SECTOR_COUNT': 0,
   'COMMAND': 0x24,
   'LBA':0,
   'PARAMETER_0': 0x2000 #enables LBA mode cmd reg defs
   }

ReadVerifySects = {
   'test_num'              : 538,
   'prm_name'              : 'ReadVerifySects',
   'timeout'               : 600,
   'FEATURES'              : 0,
   'SECTOR_COUNT'          : 0,                          # No of Sectors
   'COMMAND'               : 0x40,
   'LBA_LOW'               : 0,                          # Starting LBA
   'LBA_MID'               : 0,
   'LBA_HIGH'              : 0,
   'PARAMETER_0'           : 0x2000                      # Enables LBA mode cmd reg defs
   }

SetMultipleMode = {
   'test_num':538,
   'prm_name':'SetMultipleMode',
   'timeout'               : 600,
   'FEATURES'              : 0,
   'SECTOR_COUNT'          : 0,                          # No of Sectors
   'COMMAND'               : 0xC6,
   'LBA_LOW'               : 0,                          # Starting LBA
   'LBA_MID'               : 0,
   'LBA_HIGH'              : 0,
   'PARAMETER_0'           : 0x2000                      # Enables LBA mode cmd reg defs
   }

WriteMultiple = {
   'test_num'              : 538,
   'prm_name'              : 'WriteMultiple',
   'timeout'               : 600,
   'FEATURES'              : 0,
   'SECTOR_COUNT'          : 0,                          # No of Sectors
   'COMMAND'               : 0xC5,
   'LBA_LOW'               : 0,                          # Starting LBA
   'LBA_MID'               : 0,
   'LBA_HIGH'              : 0,
   'PARAMETER_0'           : 0x2000                      # Enables LBA mode cmd reg defs
   }

ReadMultiple = {
   'test_num'              : 538,
   'prm_name'              : 'ReadMultiple',
   'timeout'               : 600,
   'FEATURES'              : 0,
   'SECTOR_COUNT'          : 0,                          # No of Sectors
   'COMMAND'               : 0xC4,
   'LBA_LOW'               : 0,                          # Starting LBA
   'LBA_MID'               : 0,
   'LBA_HIGH'              : 0,
   'PARAMETER_0'           : 0x2000                      # Enables LBA mode cmd reg defs
   }

TransferRate = {
   'test_num'              : 641,
   'prm_name'              : 'TransferRate',
   'timeout'               : 600,
   'WRITE_READ_MODE'       : 0,
   'STARTING_LBA'          : (0, 0, 0, 0),
   'TOTAL_BLKS_TO_XFR64'   : (0, 0, 3, 0),
   'BLKS_PER_XFR'          : 256,
   'DblTablesToParse': ['P641_DMAEXT_TRANSFER_RATE',] #RT13072010 to enable retrieval from returned data
}

WriteTestSim2 = {
   'test_num'              : 643,
   'prm_name'              : 'WriteTestSim2',
   'timeout'               : 120000,
   'TEST_FUNCTION'         : 0x0000,
   'COMPARE_OPTION'        : 0x01,
   'LOOP_COUNT'            : 5000,
   'FIXED_SECTOR_COUNT'    : 63,
   'SINGLE_LBA'            : (0x0000, 0x0000),
   'MAX_LBA'               : (0x003F, 0xFFFF),
   'MID_LBA'               : (0x000F, 0x423F),
   'MIN_LBA'               : (0x0000, 0x0000),
   }

BluenunSlide = {           # Test 639 - BLUENUN SLIDE parameters
   'test_num'              : 639,
   'prm_name'              : 'BluenunSlide',
   'timeout'               : 120000,
   'spc_id'                : 1,
   'CTRL_WORD1'            : 0x0002,                     # 0x0002 - BlueNunSlide
   'CTRL_WORD2'            : 0x0000,
   'STARTING_LBA'          : (0, 0, 0, 0),
   'MAXIMUM_LBA'           : (0, 0, 0, 0),
   'BLKS_PER_XFR'          : 0x0,
   'MULTIPLIER'            : 0x0,
   }

BluenunMulti = {           # Test 639 - BLUENUN MULTI parameters
   'test_num'              :639,
   'prm_name'              :'BluenunMulti',
   'timeout'               : 120000,
   'spc_id'                : 1,
   'CTRL_WORD1'            : 0x0003,                     # 0x0003 - BlueNunMulti
   'MAXIMUM_LBA'           : (0, 0, 0, 0),
   'BLKS_PER_XFR'          : (0),
   'BLUENUN_SPAN3'         : (0, 0, 0, 0),
   'BLUENUN_SKIP3'         : (0, 0),
   }

BluenunAuto = {
   'test_num'              :639,
   'prm_name'              :'BluenunAuto',
   'timeout'               : 120000,   
   'spc_id'                : 1,   
   'CTRL_WORD1'            : (0x1), #0x1 - BlueNunAuto   
   'STARTING_LBA'          : (0,0,0,0),
   'MAXIMUM_LBA'           : (0,0,0,0),
}

RandomCCT = {              # Test 510 - CCT TEST parameters
   'test_num'              : 510,
   'prm_name'              : 'prm_510_CCT',
   'timeout'               : 25200,
   'spc_id'                : 1,
   'CTRL_WORD1'            : 0x11,                       # Default Random Read CCT
   'CTRL_WORD2'            : 0x6080,
   'STARTING_LBA'          : (0, 0, 0, 0),
   'MAXIMUM_LBA'           : (0, 0, 1, 0),
   'TOTAL_BLKS_TO_XFR64'   : (0x0000, 0x5000),           #  20480 blks
   'BLKS_PER_XFR'          : 0x0001,
   'DATA_PATTERN0'         : (0x0000, 0x0000),
   'MAX_NBR_ERRORS'        : 0xFFFF,
   'RESET_AFTER_ERROR'     : 1,
   'CCT_BIN_SETTINGS'      : 0x1E23,                     # Total 30 bins, every bin step 35ms
   'MAX_COMMAND_TIME'      : 0x2710,                     # Fail cmd time > 10s
   'CCT_LBAS_TO_SAVE'      : 0x32,                       # save max 50 entries
   }

SequentialCCT = {
   'test_num'              : 510,
   'prm_name'              : 'prm_510_CCT',
   'timeout'               : 25200,
   'spc_id'                : 1,
   'CTRL_WORD1'            : 0x10,                       # Default Sequential Read CCT
   'CTRL_WORD2'            : 0x6080,
   'STARTING_LBA'          : (0, 0, 0, 0),
   'TOTAL_BLKS_TO_XFR64'   : (0x0000, 0x5000),           # 20480 blks
   'BLKS_PER_XFR'          : 0x0001,
   'DATA_PATTERN0'         : (0x0000, 0x0000),
   'MAX_NBR_ERRORS'        : 0xffff,
   'RESET_AFTER_ERROR'     : 1,
   'CCT_BIN_SETTINGS'      : 0x1e23,                     # Total 30(1e) bins, every bin step 35(23)ms
   'MAX_COMMAND_TIME'      : 0x2710,                     # Fail cmd time > 2000 ms
   'CCT_LBAS_TO_SAVE'      : 0x32,                       # save max 50 entries
   }

ClearUDS = {
   'test_num'              : 556,
   'prm_name'              : 'Clear UDS counters and SMART',
   'timeout'               : 300,
   'CTRL_WORD1'            : 0x010F
   }

TwoPointSeekTime = {
   'test_num'              : 549,
   'prm_name'              : 'TwoPointSeekTime',
   'spc_id'                : 1,
   'CTRL_WORD1'            : 0x0043,                     # Logical Seek Mode | reportSeekTimes | timerServo
   'SEEK_OPTIONS_BYTE'     : 0x44,                       # so_st | so_mr
   'TEST_FUNCTION'         : 2,                          # Sequential Seeks
   'MINIMUM_LOCATION'      : (0, 0, 0x0000, 0x0000),
   'MAXIMUM_LOCATION'      : (0, 0, 0x0001, 0x3880),     # Nominal mid cylinder (160000/2)
   'TEST_HEAD'             : 0,
   'timeout'               : 36000,
   'DblTablesToParse'      : ['P549_IO_SK_TIME',]
   }

ButterflySeekTime = {
   'test_num':549,
   'prm_name':'ButterflySeekTime',
   'timeout': 252000,
   'TEST_FUNCTION': 0x7, #ButterFly seek with sequential head 
   'CTRL_WORD1' : 0x43, #Report Seek Times & Servo Timer    
   'STEP_SIZE': (0,0,0,0),
}

RandomSeekTime = {
   'test_num'              : 549,
   'prm_name'              : 'RandomSeekTime',
   'spc_id'                : 1,
   'CTRL_WORD1'            : 0x0043,                     # Logical Seek Mode | reportSeekTimes | timerServo
   'SEEK_OPTIONS_BYTE'     : 0x44,                       # so_st | so_mr
   'TEST_FUNCTION'         : 1,                          # Random Seeks
   'MINIMUM_LOCATION'      : (0, 0, 0, 0),
   'MAXIMUM_LOCATION'      : (0, 0, 0, 0),               # Use drive maximum
   'TEST_HEAD'             : 0,
   'NUM_SEEKS'             : 10,
   'timeout'               : 36000,
   'DblTablesToParse'      : ['P549_IO_SK_TIME',]
   }

SequentialSeek = {
   'test_num'              : 549,
   'prm_name'              : 'SequentialSeek',
   'timeout'               : 252000,
   'TEST_FUNCTION'         : 0x2,   #Sequential Seek
   'CTRL_WORD1'            : 0x43, #Report Seek Times & Servo Timer 
   'MINIMUM_LOCATION'      : (0,0,0,0),   
   'MAXIMUM_LOCATION'      : (0,0,0,0),               
   'STEP_SIZE'             : (0,0,0,0),    
   }

RandomSeek = {
   'test_num'              : 549,
   'prm_name'              : 'RandomSeek',
   'timeout'               : 252000,
   'TEST_FUNCTION'         : 0x1, #Random seeks 
   'CTRL_WORD1'            : 0x43, #Report Seek Times & Servo Timer 
   'MINIMUM_LOCATION'      : (0,0,0,0),   
   'MAXIMUM_LOCATION'      : (0,0,0,0),               
   'NUM_SEEKS'             : (0),    
   }

FunnelSeek = {
   'test_num'              : 549,
   'prm_name'              : 'FunnelSeek',
   'timeout'               : 252000,
   'TEST_FUNCTION'         : 10,   #Funnel Seek
   'CTRL_WORD1'            : 0x43, #Report Seek Times & Servo Timer 
   'SEEK_OPTIONS_BYTE'     : 0x64, #Return Seek Time
   'MINIMUM_LOCATION'      : (0,0,0,0),   
   'MAXIMUM_LOCATION'      : (0,0,0,0),               
   'STEP_SIZE'             : (0,0,0,0),
   'SECTOR_COUNT'          : 0,        
   'DblTablesToParse'      : ['P549_IO_SK_TIME',]
   }

WrtAltTones = {
   'test_num' : 638,
   'prm_name' : 'WrtAltTones',
   'timeout' : 1200,
   "CTRL_WORD1" : (0x0006), #Use existing Buffer space. (do not create a local only buffer), Report read data in Oracle supported P508_BUFFER table 
   "DFB_WORD_0" : (0x5201,),
   "DFB_WORD_1" : (0x0100,),
   "DFB_WORD_2" : (0x0902,),
   "DFB_WORD_3" : (0x0000,),
   "DFB_WORD_4" : (0x0000,),
   "DFB_WORD_5" : (0x0200,),
   "DFB_WORD_6" : (0x0000,),
   "DFB_WORD_7" : (0x0000,),
   "DFB_WORD_8" : (0x0000,),
   }

SystemTrackWriteSim = {
   'test_num'           : 654,
   'timeout'            : 252000,
   'prm_name'           : 'SystemTrackWriteSim',   
   'spc_id'             : 1,   
   'LBA'                : (0,0,0,0), #Report Seek Times
   'DATA_PATTERN0'      : (0,0),   
   'SECTOR_COUNT'       : (0),               
   'MULTI_SECTORS_BLOCK': (0),    
   }

#################################################################                                    
