#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Implements a basic ICmd interface
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001-2011 Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_CPC_ICmd_TN_Params.py $
# $Revision: #2 $
# $DateTime: 2016/09/20 03:10:55 $
# $Author: phonenaing.myint $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_CPC_ICmd_TN_Params.py#2 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from base_Initiator_Cmd_Params import *

HardReset = {
            'test_num' : 533,
            'prm_name' : 'PRM_533_HARDRESET',
            'CTRL_WORD1' : 1,
            'timeout' : 600
         }

SequentialWriteDMAExt = {
            'test_num'   : 510,
            'prm_name'   : "SequentialWriteDMAExt",
            'spc_id'     : 1,
            'timeout' : 252000,
            'WRITE_READ_MODE' : (0x02), #Write Mode
            'STARTING_LBA' : (0,0,0,0),
            #'TOTAL_BLKS_TO_XFR': (0,0),
            'BLKS_PER_XFR' : 256,
            'DATA_PATTERN0' : (0,0),
            'PATTERN_MODE'  : (0x80),
}

ZeroCheck = {
            'test_num'   : 510,
            'prm_name'   : "ZeroCheck",
            'spc_id'     : 1,
            'timeout' : 252000,
            'WRITE_READ_MODE' : (0x01), #Read Mode
            'STARTING_LBA' : (0,0,0,0),
            #'TOTAL_BLKS_TO_XFR': (0,0),
            'BLKS_PER_XFR' : 256,
            'DATA_PATTERN0' : (0,0),
            'PATTERN_MODE'  : (0x80),
}

SequentialReadDMAExt = {
            'test_num'   : 510,
            'prm_name'   : "SequentialReadDMAExt",
            'spc_id'     : 1,
            'timeout' : 252000,
            'WRITE_READ_MODE' : (0x01), #Read Mode
            'STARTING_LBA' : (0,0,0,0),
            #'TOTAL_BLKS_TO_XFR': (0,0),
            'BLKS_PER_XFR' : 256,
            'DATA_PATTERN0' : (0,0),
            'PATTERN_MODE'  : (0x80),
}

SequentialWRDMAExt = {
            'test_num'   : 510,
            'prm_name'   : "SequentialWRDMAExt",
            'spc_id'     : 1,
            'timeout' : 252000,
            'WRITE_READ_MODE' : (0x00), #Write/Read Mode
            'STARTING_LBA' : (0,0,0,0),
            #'TOTAL_BLKS_TO_XFR': (0,0),
            'BLKS_PER_XFR' : 256,
            'DATA_PATTERN0' : (0,0),
            'PATTERN_MODE'  : (0x80),
}

SequentialReadVerifyExt = {
            'test_num'   : 510,
            'prm_name'   : "SequentialReadVerifyExt",
            'spc_id'     : 1,
            'timeout' : 252000,
            'WRITE_READ_MODE' : (0x04), #read verify
            'STARTING_LBA' : (0,0,0,0),
            #'TOTAL_BLKS_TO_XFR': (0,0),
            'BLKS_PER_XFR' : 256,
            'DATA_PATTERN0' : (0,0),
            'PATTERN_MODE'  : (0x80),
}

SequentialWriteVerify = {
            'test_num'   : 510,
            'prm_name'   : "SequentialWriteVerify",
            'spc_id'     : 1,
            'timeout' : 252000,
            'CTRL_WORD1' : 0, #Write/Read Mode
            'STARTING_LBA' : (0,0,0,0),
            #'TOTAL_BLKS_TO_XFR': (0,0),
            'BLKS_PER_XFR' : 256,
            'DATA_PATTERN0' : (0,0),
            'CTRL_WORD2'  : 0x80,
}

Bit_to_Bit_cmp = {
            'test_num'   : 551,
            'prm_name'   : "Bit_to_Bit_cmp",
            'spc_id'     : 1,
            'timeout'    : 252000,
            'CTRL_WORD1' : 0, # 0x10 = read only, >> 4
                              # 0x20 = write only
                              # 0x00 = write/read
                              # 1 = fast mode >> 0
                              # 0 is normal mode
                              # access mode = 0 is seq >> 1
}

RandomWriteDMAExt = {
            'test_num'   : 510,
            'prm_name'   : "RandomWriteDMAExt",
            'spc_id'     : 1,
            'timeout' : 252000,
            'WRITE_READ_MODE' : (0x02),  #Write Mode
            'ACCESS_MODE' : (0x01),      #Random
            'STARTING_LBA' : (0,0,0,0),
            #'TOTAL_BLKS_TO_XFR': (0,0),
            'BLKS_PER_XFR' : 256,
            'DATA_PATTERN0' : (0,0),
            'PATTERN_MODE'  : (0x80),
}

RandomReadDMAExt = {
            'test_num'   : 510,
            'prm_name'   : "RandomReadDMAExt",
            'spc_id'     : 1,
            'timeout' : 252000,
            'WRITE_READ_MODE' : (0x01),  #Read Mode
            'ACCESS_MODE' : (0x01),      #Random
            'STARTING_LBA' : (0,0,0,0),
            #'TOTAL_BLKS_TO_XFR': (0,0),
            'BLKS_PER_XFR' : 256,
            'DATA_PATTERN0' : (0,0),
            'PATTERN_MODE'  : (0x80),
}

RandomWRDMAExt = {
            'test_num'   : 510,
            'prm_name'   : "RandomWRDMAExt",
            'spc_id'     : 1,
            'timeout' : 252000,
            'WRITE_READ_MODE' : (0x00), #Write/Read Mode
            'ACCESS_MODE' : (0x01),     #Random
            'STARTING_LBA' : (0,0,0,0),
            #'TOTAL_BLKS_TO_XFR': (0,0),
            'BLKS_PER_XFR' : 256,
            'DATA_PATTERN0' : (0,0),
            'PATTERN_MODE'  : (0x80),
}

ReverseWriteDMAExt = {
            'test_num'   : 510,
            'prm_name'   : "ReverseWriteDMAExt",
            'spc_id'     : 1,
            'timeout' : 252000,            
            'CTRL_WORD1' : (0x220), #Reverse Write
            'CTRL_WORD2' : (0x2080),
            'STARTING_LBA' : (0,0,0,0),            
            'BLKS_PER_XFR' : 256,
            'DATA_PATTERN0' : (0,0),
}

ReverseReadDMAExt = {
            'test_num'   : 510,
            'prm_name'   : "ReverseReadDMAExt",
            'spc_id'     : 1,
            'timeout' : 252000,            
            'CTRL_WORD1' : (0x210), #Reverse Read
            'CTRL_WORD2' : (0x2080),
            'STARTING_LBA' : (0,0,0,0),            
            'BLKS_PER_XFR' : 256,
            'DATA_PATTERN0' : (0,0),
}
BufferCompareTest = {
      'test_num' : 643,
      'prm_name' : "BufferCompareTest",
      'timeout' : 252000,  
      'TEST_FUNCTION'         : 0x10,
      'STARTING_LBA'          : (0,0,0,0),
      'TOTAL_BLKS_TO_XFR64'   : (0,0,0,1000 ),
      'BUFFER_LENGTH'         : (0, 512 ),
      'LOOP_COUNT'            : 1,
}

WritePatternToBuffer = {
        'test_num':     508,
        'prm_name':     'WritePatternToBuffer',
        'timeout':      600,
        'CTRL_WORD1':   0x0,
        #'PATTERN_TYPE': 0,
        'BUFFER_LENGTH': (0,512),
        'BYTE_OFFSET':  (0,0),
        'DATA_PATTERN0':(0,0),
        'DATA_PATTERN1':(0,0),
        }

DisplayBufferData = {
         'test_num':    508,
         'prm_name':    'DisplayWriteBuffer',
         'timeout':     600,
         'CTRL_WORD1':  0x5,
         'BUFFER_LENGTH': (0,512),
         'stSuppressResults' : ST_SUPPRESS__ALL,     
         }

CompareBuffers = {
         'test_num':    508,
         'prm_name':    'CompareBuffers',
         'timeout':     600,
         'CTRL_WORD1':  0x8,
         'BUFFER_LENGTH': (0,512),
         'BYTE_OFFSET':  (0,0),
         }    
                       
BufferCopy = {
         'test_num':    508,
         'prm_name':    'BufferCopy',
         'timeout':     600,
         'CTRL_WORD1':  0x7,
         'BUFFER_LENGTH': (0,512),
         'BYTE_OFFSET':  (0,0),
         }             

SetFeaturesParameter = {
   'test_num':538,
   'prm_name':'SetFeatures',
   'timeout': 600,
   'FEATURES': 0,
   'SECTOR_COUNT': 0,
   'SECTOR':0,
   'CYLINDER':(0),
   'COMMAND': 0xEF,
   'HEAD': 0,
   'DEVICE':0,
   'PARAMETER_0':0x2000, #0x2000 enables LBA mode cmd reg defs

}

SmartParameter = {
   'test_num':538,
   'prm_name':'Smart',
   'timeout': 600,
   'FEATURES': 0,
   'SECTOR_COUNT': 1,
   'COMMAND': 0xB0,
   'LBA_LOW': 0,
   'LBA_MID':0x4F,
   'LBA_HIGH':0xC2,
   'PARAMETER_0': 0x2000 #enables LBA mode cmd reg defs
}

WriteLong = {
   'test_num':538,
   'prm_name':'WriteLong',
   'timeout': 600,
   'FEATURES': 0,
   'SECTOR_COUNT': 1,
   'COMMAND': 0x33,
   'LBA':0,
   'PARAMETER_0':0x2000, #0x2000 enables LBA mode cmd reg defs
}  

ReadLong = {
   'test_num':538,
   'prm_name':'ReadLong',
   'timeout': 600,
   'FEATURES': 0,
   'SECTOR_COUNT': 1,
   'COMMAND': 0x23,
   'LBA':0,
   'PARAMETER_0':0x2000, #0x2000 enables LBA mode cmd reg defs
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
            'test_num'   : 510,
            'prm_name'   : "WriteTestMobile",
            'spc_id'     : 1,
            'timeout' : 252000,
            #'WRITE_READ_MODE' : (0x02),
            "CTRL_WORD1"      : 0x20 | 0x1,
            'STARTING_LBA' : (0,0,0,0),
            #'TOTAL_BLKS_TO_XFR': (0,0),
            'BLKS_PER_XFR' : 256,
            'DATA_PATTERN0' : (0,0),
            'PATTERN_MODE'  : (0x01),
}

Standby = {
   'test_num':538,
   'prm_name':'Standby',
   'timeout': 600,
   'FEATURES': 0,
   'SECTOR_COUNT': 0,
   'SECTOR':0,
   'CYLINDER':(0),
   'COMMAND': 0xE2,
   'HEAD': 0,
   'DEVICE':0,
   'PARAMETER_0':0, #0x2000 enables LBA mode cmd reg defs
}

StandbyImmed = Standby.copy()
StandbyImmed.update({
   'COMMAND': 0xE0,
   'prm_name':'StandbyImmed',
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
   'DblTablesToParse': ['P5XX_TFREG_CHS',],
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
   'test_num':538,
   'prm_name':'FlushCache',
   'timeout': 600,
   'FEATURES': 0,
   'SECTOR_COUNT': 0,
   'SECTOR':0,
   'CYLINDER':(0),
   'COMMAND': 0xE7,
   'HEAD': 0,
   'DEVICE':0,
   'PARAMETER_0':0, #0x2000 enables LBA mode cmd reg defs
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
   'test_num': 795,
   'prm_name':"Send CCC data to drive",
   'timeout': 3600
}

IdentifyDevice = {
   'test_num' : 514,
   'prm_name' : 'prm_514_IdentifyDevice',
   'timeout' : 30,
   'CTRL_WORD1': 0x8003,
   'DblTablesToParse': ['P514_IDENTIFY_DEVICE_DATA',]
}

UnlockFactoryCmds = {
   'test_num'                 : 638,
   'prm_name'                 : "prm_638_Unlock_Seagate",
   'timeout'                  : 3600,
   'spc_id'                   : 1,
   "DFB_WORD_0"               : 0xFFFF,         # DITS cmd ID (Unlock Diagnostics)
   "DFB_WORD_1"               : 0x0100,         # Rev ID
   "DFB_WORD_2"               : 0x9A32,         # Unlock Seagate Access Key LSW
   "DFB_WORD_3"               : 0x4F03,         # Unlock Seagate Access Key MSW
   'retryECList'              : [14061, 14029],
   'retryCount'               : 10,
   'retryMode'                : HARD_RESET_RETRY,
   #'CTRL_WORD1'               : 0x10,
}

ClearFormatCorrupt = {
   'test_num'        : 638,
   'prm_name'        : 'ClearFormatCorrupt',
   'timeout'         : 3600,
   'spc_id'          : 1,
   'DFB_WORD_0'      : 0x1301,   # DITS cmd ID (Set Clear Format Corrupt Condition)
   'DFB_WORD_1'      : 0x0100,   # Rev ID (Usually x0001)
   'DFB_WORD_2'      : 0x0100,   # LSB_bit_0: 0=Normal operation 1=Clear fmt corrupt
   'DFB_WORD_3'      : 0x0000,   #
   }   
   
prm_638_SetDatScub_0 = {
   'test_num'        : 638,
   'prm_name'        : 'prm_638_SetDatScub_0',
   'timeout'         : 3600,
   'spc_id'          : 1,   
   'DFB_WORD_0'      : 0x0101,   # DITS cmd ID (Disable data scrubing)
   'DFB_WORD_1'      : 0x0100,   # Rev ID (Usually x0001)
   'DFB_WORD_2'      : 0x0000,   
   'DFB_WORD_3'      : 0x0000,   
   }   

prm_638_SetIA_0 = {
   'test_num'        : 638,
   'prm_name'        : 'prm_638_SetIA_0',
   'timeout'         : 3600,
   'spc_id'          : 1,   
   'DFB_WORD_0'      : 0x0901,   # DITS cmd ID (Disable Inter-Command-Activity)
   'DFB_WORD_1'      : 0x0100,   # Rev ID (Usually x0001)
   'DFB_WORD_2'      : 0x0000,   
   'DFB_WORD_3'      : 0x0000,   
   }  
      
# Sent servo command 2F (Temperature sensor measurement)
GetPreampTemp = {
   'test_num'    : 638,
   'prm_name'    : "GetPreampTemp",
   'timeout'     :  3600,
   'spc_id'      : 1,
   "DFB_WORD_0"  : 0x4F01,  # DITS cmd ID
   "DFB_WORD_1"  : 0x0100,  # Rev ID (Usually x0001)
   "DFB_WORD_2"  : 0x0000,  # LSB_bit_0=CO, bit_1=O, bit_2=F, bit_3=T,bit_4=D.  MSB = rsvd.
   "DFB_WORD_3"  : 0x2F00,  # Servo cmd (16 bits, little endian)
   #'CTRL_WORD1'               : 0x10,
}

LongDST = {
   'test_num'    : 600,
   'prm_name'    : "LongDST",
   'timeout'     : 28800,
   'spc_id'      : 1,
   # 'TEST_FUNCTION' : (2), # 1=short DST 2=long DST
   'TEST_OPERATING_MODE' : 2,
   'DELAY_TIME' : (60),
}

ShortDST = {
   'test_num'    : 600,
   'prm_name'    : "ShortDST",
   'timeout'     : 3600,
   'spc_id'      : 1,
   # 'TEST_FUNCTION' : (1), # 1=short DST 2=long DST
   'TEST_OPERATING_MODE' : 1,
   'DELAY_TIME' : (10),
}

WriteFinalAssemblyDate = {
   'test_num'                : 557,
   'prm_name'                : "WriteFinalAssemblyDate",
   "CTRL_WORD1"              : (0x0001),
   "TEST_FUNCTION"           : (1),         # 0=Write, 1=Read, 2=Compare to current date, Final Assembly Date Code
   "BYTE_OFFSET"             : (0, 0x0046),
#  "MAX_DIFFERENCE_IN_DAYS"  : (14),        # Fail if more than 14 days
   "FINAL_ASSEMBLY_DATE"     : (0,0,0,0),
   "timeout"                 : 600,
}

DMAExtTransRate = {
   'test_num'                : 641,
   'prm_name'                : "DMAExtTransRate",
   'WRITE_READ_MODE': 0,
   'BLKS_PER_XFR': 0,       
   'STARTING_LBA': (0, 0, 0, 0),   
   'TOTAL_BLKS_TO_XFR64': (0,0,0,0),
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
   'test_num':538,
   'prm_name':'WriteBuffer',
   'timeout': 600,
   'FEATURES': 0,
   'SECTOR_COUNT': 0,
   'SECTOR':0,
   'CYLINDER':(0),
   'COMMAND': 0xE8,
   'HEAD': 0,
   'DEVICE':0,
   'PARAMETER_0':0, #0x2000 enables LBA mode cmd reg defs
}

ReadBuffer = {
   'test_num':538,
   'prm_name':'ReadBuffer',
   'timeout': 600,
   'FEATURES': 0,
   'SECTOR_COUNT': 0,
   'SECTOR':0,
   'CYLINDER':(0),
   'COMMAND': 0xE4,
   'HEAD': 0,
   'DEVICE':0,
   'PARAMETER_0':0, #0x2000 enables LBA mode cmd reg defs
}

WriteSectors = {
   'test_num':538,
   'prm_name':'WriteSectors',
   'timeout': 600,
   'FEATURES': 0,
   'SECTOR_COUNT': 0, #No of Sectors
   'COMMAND': 0x30,
   'LBA':0,
   'PARAMETER_0': 0x2000 #enables LBA mode cmd reg defs
}

ReadSectors = {
   'test_num':538,
   'prm_name':'ReadSectors',
   'timeout': 600,
   'FEATURES': 0,
   'SECTOR_COUNT': 0,
   'COMMAND': 0x20,
   'LBA':0,
   'PARAMETER_0': 0x2000 #enables LBA mode cmd reg defs
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
   'test_num':538,
   'prm_name':'ReadVerifySects',
   'timeout': 600,
   'FEATURES': 0,
   'SECTOR_COUNT': 0,#No of Sectors
   'COMMAND': 0x40,
   'LBA':0,
   'PARAMETER_0': 0x2000 #enables LBA mode cmd reg defs
}

ReadVerifySectsExt = {
   'test_num':538,
   'prm_name':'ReadVerifySectsExt',
   'timeout': 600,
   'FEATURES': 0,
   'SECTOR_COUNT': 0,
   'COMMAND': 0x42,
   'LBA':0,
   'PARAMETER_0': 0x2000 #enables LBA mode cmd reg defs
}

SetMultipleMode = {
   'test_num':538,
   'prm_name':'SetMultipleMode',
   'timeout': 600,
   'FEATURES': 0,
   'SECTOR_COUNT': 0,
   'COMMAND': 0xC6,
   'LBA_LOW': 0,
   'LBA_MID': 0,
   'LBA_HIGH':0,
   'PARAMETER_0': 0x2000 #enables LBA mode cmd reg defs
}

WriteMultiple = {
   'test_num':538,
   'prm_name':'WriteMultiple',
   'timeout': 600,
   'FEATURES': 0,
   'SECTOR_COUNT': 0,#No of Sectors
   'COMMAND': 0xC5,
   'LBA':0,
   'PARAMETER_0': 0x2000 #enables LBA mode cmd reg defs
}

ReadMultiple = {
   'test_num':538,
   'prm_name':'ReadMultiple',
   'timeout': 600,
   'FEATURES': 0,
   'SECTOR_COUNT': 0,#No of Sectors
   'COMMAND': 0xC4,
   'LBA':0,
   'PARAMETER_0': 0x2000 #enables LBA mode cmd reg defs
}

#################################KWAI Params################
WriteDMALBA = {
   'test_num':538,
   'prm_name':'WriteDMALBA',
   'timeout': 600,
   'FEATURES': 0,
   'SECTOR_COUNT': 0,
   'COMMAND': 0xCA,
   'LBA':0,
   'PARAMETER_0': 0x2000 #enables LBA mode cmd reg defs
}

ReadDMALBA = {
   'test_num':538,
   'prm_name':'ReadDMALBA',
   'timeout': 600,
   'FEATURES': 0,
   'SECTOR_COUNT': 0,
   'COMMAND': 0xC8,
   'LBA':0,
   'PARAMETER_0': 0x2000 #enables LBA mode cmd reg defs
}

InitDeviceParms = {
   'test_num':538,
   'prm_name':'InitDeviceParms',
   'timeout': 600,
   'FEATURES': 0,
   'SECTOR_COUNT': 0,
   'SECTOR':0,
   'CYLINDER':(0),
   'COMMAND': 0x91,
   'HEAD': 0,
   'DEVICE':0,
   'PARAMETER_0':0, #0x2000 enables LBA mode cmd reg defs
}

SecuritySetPassword = {
   'test_num':538,
   'prm_name':'SecuritySetPassword',
   'timeout': 600,
   'FEATURES': 0,
   'SECTOR_COUNT': 0,
   'COMMAND': 0xF1,
   'LBA_LOW': 0,
   'LBA_MID': 0,
   'LBA_HIGH': 0,
   'PARAMETER_0': 0x2000 #enables LBA mode cmd reg defs
}

SecurityFreezeLock = {
   'test_num':538,
   'prm_name':'SecurityFreezeLock',
   'timeout': 600,
   'FEATURES': 0,
   'SECTOR_COUNT': 0,
   'COMMAND': 0xF5,
   'LBA_LOW': 0,
   'LBA_MID': 0,
   'LBA_HIGH': 0,
   'PARAMETER_0': 0x2000 #enables LBA mode cmd reg defs
}


SecurityErasePrepare = {
   'test_num':538,
   'prm_name':'SecurityErasePrepare',
   'timeout': 600,
   'FEATURES': 0,
   'SECTOR_COUNT': 0,
   'COMMAND': 0xF3,
   'LBA_LOW': 0,
   'LBA_MID': 0,
   'LBA_HIGH': 0,
   'PARAMETER_0': 0x2000 #enables LBA mode cmd reg defs
}

SecurityEraseUnit = {
   'test_num':538,
   'prm_name':'SecurityEraseUnit',
   'timeout': 600,
   'FEATURES': 0,
   'SECTOR_COUNT': 0,
   'COMMAND': 0xF4,
   'LBA_LOW': 0,
   'LBA_MID': 0,
   'LBA_HIGH': 0,
   'PARAMETER_0': 0x2000 #enables LBA mode cmd reg defs
}

ButterflySeekTime = {
   'test_num':549,
   'prm_name':'ButterflySeekTime',
   'timeout': 252000,
   'TEST_FUNCTION': 0x7, #ButterFly seek with sequential head 
   'CTRL_WORD1' : 0x43, #Report Seek Times & Servo Timer    
   'STEP_SIZE': (0,0,0,0),
}

SequentialSeek = {
   'test_num':549,
   'prm_name':'SequentialSeek',
   'timeout': 252000,
   'TEST_FUNCTION': 0x2,   #Sequential Seek
   'CTRL_WORD1' : 0x43, #Report Seek Times & Servo Timer 
   'MINIMUM_LOCATION': (0,0,0,0),   
   'MAXIMUM_LOCATION': (0,0,0,0),               
   'STEP_SIZE'  : (0,0,0,0),    
}

FunnelSeek = {
   'test_num':549,
   'prm_name':'FunnelSeek',
   'timeout': 252000,
   'TEST_FUNCTION': 0x4,   #Incremental/Decremental
   'CTRL_WORD1' : 0x43, #Report Seek Times & Servo Timer 
   'MINIMUM_LOCATION': (0,0,0,0),   
   'MAXIMUM_LOCATION': (0,0,0,0),               
   'STEP_SIZE'  : (0,0,0,0),    
}

RandomSeek = {
   'test_num':549,
   'prm_name':'RandomSeek',
   'timeout': 252000,
   'TEST_FUNCTION': 0x1, #Random seeks 
   'CTRL_WORD1' : 0x43, #Report Seek Times & Servo Timer 
   'MINIMUM_LOCATION': (0,0,0,0),   
   'MAXIMUM_LOCATION': (0,0,0,0),               
   'NUM_SEEKS'  : (0),    
}
#################################################################
TransferRate = {
   'test_num':641,
   'prm_name':'TransferRate',
   'timeout': 600,
   'WRITE_READ_MODE':0,
   'STARTING_LBA': (0, 0, 0, 0),
   'TOTAL_BLKS_TO_XFR64':(0, 0, 3, 0),
   'BLKS_PER_XFR':256,
}

WriteTestSim2 = {
   'test_num':643,
   'prm_name':'WriteTestSim2',
   'timeout': 120000,
             "TEST_FUNCTION" : (0x0000,),
            "COMPARE_OPTION" : (0x01,),
       #"MULTI_SECTORS_BLOCK" : (0x07,),
             #"DATA_PATTERN0" : (0x5678,0x1234,),
             #"DATA_PATTERN1" : (0xabdf,0xeeee,),
                "LOOP_COUNT" : (5000,),
        "FIXED_SECTOR_COUNT" : (63,),
                "SINGLE_LBA" : (0x0000,0x0000,),
                   "MAX_LBA" : (0x003F,0xFFFF,),
                   "MID_LBA" : (0x000F,0x423F),
                   "MIN_LBA" : (0x0000,0x0000,),
}
#################################################################
#T639 - BLUENUN SLIDE parameters
BluenunSlide = {
   'test_num':639,
   'prm_name':'BluenunSlide',
   'timeout': 120000,
   'spc_id'     : 1,
          "CTRL_WORD1" : 0x2, #0x2 - BlueNunSlide
          "CTRL_WORD2" : 0x0,
        "STARTING_LBA" : (0,0,0,0),
         "MAXIMUM_LBA" : (0,0,0,0),
        "BLKS_PER_XFR" : 0x0,        
          "MULTIPLIER" : 0x0,
}

#T639 - BLUENUN MULTI parameters
BluenunMulti = {
   'test_num':639,
   'prm_name':'BluenunMulti',
   'timeout': 120000,
   'spc_id'     : 1,
   'CTRL_WORD1'        : (0x3), #0x3 - BlueNunMulti
   'MAXIMUM_LBA'       : (0,0,0,0),
   'BLKS_PER_XFR'      : (0),
   'BLUENUN_SPAN3'     : (0,0,0,0),
   'BLUENUN_SKIP3'     : (0,0),
}

BluenunAuto = {
   'test_num':639,
   'prm_name':'BluenunAuto',
   'timeout': 120000,   
   'spc_id'     : 1,   
   'CTRL_WORD1'        : (0x1), #0x1 - BlueNunAuto   
   'STARTING_LBA'      : (0,0,0,0),
   'MAXIMUM_LBA'       : (0,0,0,0),
}

#T639 - BLUENUN SCAN parameters
BluenunScan = {
   'test_num':639,
   'prm_name':'BluenunScan',
   'timeout': 120000,   
   'spc_id'     : 1,   
   'CTRL_WORD1'        : (0x0), #0x0 - BlueNunScan   
   'STARTING_LBA'      : (0,0,0,0),
   'MAXIMUM_LBA'       : (0,0,0,0),
}

#################################################################
#################################################################
#T510 - CCT TEST parameters
RandomCCT = {
   'test_num'          :  510,
   'prm_name'          :  "prm_510_CCT",
   'timeout'           :  25200,
   'spc_id'            :  1,
   "CTRL_WORD1"        : (0x11),              #Default Random Read CCT
   "CTRL_WORD2"        : (0x6080),
   "STARTING_LBA"      : (0,0,0,0),
   "MAXIMUM_LBA"       : (0,0,1,0),
   "TOTAL_BLKS_TO_XFR64" : (0x0000,0x5000),      #  20480 blks
   "BLKS_PER_XFR"      : (0x0001),
   "DATA_PATTERN0"     : (0x0000, 0x0000),
   "MAX_NBR_ERRORS"    : (0xffff),
   "RESET_AFTER_ERROR" : (1),
   "CCT_BIN_SETTINGS"  : (0x1e23),             # Total 30 bins, every bin step 35ms
   "MAX_COMMAND_TIME"  : 0x2710,               # Ffail cmd time > 10s
   "CCT_LBAS_TO_SAVE"  : 0x32,                 # save max 50 entries
}

SequentialCCT = {
   'test_num'          :  510,
   'prm_name'          :  "prm_510_CCT",
   'timeout'           :  25200,
   'spc_id'            :  1,
   "CTRL_WORD1"        : (0x10),              #Default Sequential Read CCT
   "CTRL_WORD2"        : (0x6080),
   "STARTING_LBA"      : (0,0,0,0),
   "MAXIMUM_LBA"       : (0,0,1,0),
   "TOTAL_BLKS_TO_XFR64" : (0x0000,0x5000),      #  20480 blks
   "BLKS_PER_XFR"      : (0x0001),
   "DATA_PATTERN0"     : (0x0000, 0x0000),
   "MAX_NBR_ERRORS"    : (0xffff),
   "RESET_AFTER_ERROR" : (1),
   "CCT_BIN_SETTINGS"  : (0x1e23),             # Total 30(1e) bins, every bin step 35(23)ms
   "MAX_COMMAND_TIME"  : 0x2710,               # Ffail cmd time > 10s
   "CCT_LBAS_TO_SAVE"  : 0x32,                 # save max 50 entries
}

ClearUDS = {
   "test_num"           : 556,
   "prm_name"           : 'Clear UDS counters and SMART',
   "timeout"            : 300,
   "CTRL_WORD1"         : 0x10F
}
      
SeqDelayWR = {
      'test_num' : 643,
      'prm_name' : "SeqDelayWR",      
      'timeout' : 252000,  
      'TEST_FUNCTION'         : 0x30,  #SeqDelayWR function            
      'WRITE_READ_MODE'       : (1),   # Default WRITE
      'STARTING_LBA'          : (0,0,0,0),
      'TOTAL_BLKS_TO_XFR64'   : (0,0,0,0),            
      'FIXED_SECTOR_COUNT'    : (0),
      'MIN_DELAY_TIME'        : (0),
      'MAX_DELAY_TIME'        : (0),
      'STEP_DELAY_TIME'       : (0),
      'GROUP_SIZE'            : (0),      
}

SequentialWRCopy = {
      'test_num' : 643,
      'prm_name' : "SequentialWRCopy",      
      'timeout' : 252000,  
      'TEST_FUNCTION'         : 0x40, #SequentialWRCopy function
      'START_READ_LBA'        : (0,0,0,0),
      'START_WRITE_LBA'       : (0,0,0,0),
      'FIXED_SECTOR_COUNT'    : (0),
      'TOTAL_BLKS_TO_XFR64'   : (0,0,0,0),
}

TwoPointSeekTime = {
   'test_num'           : 549,
   'prm_name'           : 'TwoPointSeekTime',
   'spc_id'             : 1,
   'CTRL_WORD1'         : 0x0043,               # Logical Seek Mode | reportSeekTimes | timerServo
   'SEEK_OPTIONS_BYTE'  : 0x44,                 # so_st | so_mr
   'TEST_FUNCTION'      : 2,                    # Sequential Seek
   'MINIMUM_LOCATION'   : (0, 0, 0x0000,0x0000,),
   'MAXIMUM_LOCATION'   : (0, 0, 0x0001,0x3880,),     # Nominal mid cylinder (160000/2),maybe should change for Marina
   'TEST_HEAD'          : 0,
   #'CYLINDER_INCREMENT' : (200,),               # Change here to control times
   'timeout'            : 36000,
   'DblTablesToParse': ['P549_IO_SK_TIME',]
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

NCQSequentialReadDMA = {
   'test_num'           : 597,
   'timeout'            : 252000,
   'prm_name'           : 'NCQSequentialReadDMA',
   'spc_id'             : 1,
   'CTRL_WORD1'         : (0x0020),     # read sequential
   'CTRL_WORD2'         : (0x0000),     # no ratio
   'MINIMUM_LBA'        : (0, 0, 0, 0), # minimum LBA
   'MAXIMUM_LBA'        : (0, 0, 0, 0), # maximum LBA
   'MIN_SECTOR_COUNT'   : (0x0100),     # sector count
}

NCQSequentialWriteDMA = {
   'test_num'           : 597,
   'timeout'            : 252000,
   'prm_name'           : 'NCQSequentialWriteDMA',
   'spc_id'             : 1,
   'CTRL_WORD1'         : (0x0010),     # write sequential
   'CTRL_WORD2'         : (0x0000),     # no ratio
   'MINIMUM_LBA'        : (0, 0, 0, 0), # minimum LBA
   'MAXIMUM_LBA'        : (0, 0, 0, 0), # maximum LBA
   'MIN_SECTOR_COUNT'   : (0x0100),     # sector count
}

NCQRandomReadDMA = {
   'test_num'           : 597,
   'timeout'            : 252000,
   'prm_name'           : 'NCQRandomReadDMA',
   'spc_id'             : 1,
   'CTRL_WORD1'         : (0x0021),     # read random
   'CTRL_WORD2'         : (0x0000),     # no ratio
   'MINIMUM_LBA'        : (0, 0, 0, 0), # minimum LBA
   'MAXIMUM_LBA'        : (0, 0, 0, 0), # maximum LBA
   'MIN_SECTOR_COUNT'   : (0x0100),     # minimum sector count
   'MAX_SECTOR_COUNT'   : (0x0100),     # maximum sector count
   'LOOP_COUNT'         : (0x0001),     # number of commands to send
}

NCQRandomWriteDMA = {
   'test_num'           : 597,
   'timeout'            : 252000,
   'prm_name'           : 'NCQRandomWriteDMA',
   'spc_id'             : 1,
   'CTRL_WORD1'         : (0x0011),     # write random
   'CTRL_WORD2'         : (0x0000),     # no ratio
   'MINIMUM_LBA'        : (0, 0, 0, 0), # minimum LBA
   'MAXIMUM_LBA'        : (0, 0, 0, 0), # maximum LBA
   'MIN_SECTOR_COUNT'   : (0x0100),     # minimum sector count
   'MAX_SECTOR_COUNT'   : (0x0100),     # maximum sector count
   'LOOP_COUNT'         : (0x0001),     # number of commands to send
}

SetProductID = {
   'test_num'              : 506,
   'prm_name'              : 'prm_506_set_PROD_ID',
   'timeout'               : 30,
   'stSuppressResults'     : ST_SUPPRESS__ALL,
   'PROD_ID'               : 0,
   }

#################################################################                                    
