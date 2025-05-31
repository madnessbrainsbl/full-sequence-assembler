#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Implements a basic ICmd interface
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_SAS_ICmd_Params.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_SAS_ICmd_Params.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from base_Initiator_Cmd_Params import *

IdentifyDevice = {
   'test_num'              : 514,
   'prm_name'              : "prm_514_IdentifyInformation",
   'PAGE_CODE'             : 0,
   }

HardReset = {
   'test_num'              : 599,
   'prm_name'              : "base_prm_599_SasHardReset",
   'spc_id'                : 1,
   'timeout'               : 600,
   'PARAMETER_10'          : 0x0000,
   'PARAMETER_9'           : 0x0000,
   'PARAMETER_8'           : 0x0000,
   'PARAMETER_3'           : 0x0000,
   'PARAMETER_2'           : 0x0002,
   'PARAMETER_1'           : 0x0000,
   'PARAMETER_7'           : 0x0000,
   'PARAMETER_6'           : 0x0000,
   'PARAMETER_5'           : 0x0000,
   'PARAMETER_4'           : 0x0000,
   }

base_510_prm = {
   'test_num'              : 510,
   'prm_name'              : 'base_510_prm',
   'spc_id'                : 1,
   'timeout'               : 3000,
   'START_LBA34'           : (0,0,0,0),
   'END_LBA34'             : (0,0,0,0),         # = Max lba
   'TOTAL_LBA_TO_XFER'     : 0,
   'NUMBER_LBA_PER_XFER'   : (0, 256),
   'PATTERN_LSW'           : 0,
   'PATTERN_MSW'           : 0,
   'PATTERN_MODE'          : 0x80,
   'CACHE_MODE'            : 1,
   'ACCESS_MODE'           : 0,
   'SAVE_READ_ERR_TO_MEDIA': 0,
   'PATTERN_LENGTH_IN_BITS': 32,
   'ERROR_REPORTING_MODE'  : 0x1,
   }

SequentialWriteDMAExt = dict(base_510_prm)
SequentialWriteDMAExt.update({
   'test_num'              : 510,
   'prm_name'              : 'SequentialWriteDMAExt',
   'spc_id'                : 1,
   'timeout'               : 252000,
   'WRITE_READ_MODE'       : 2,                 # Write Mode
   })

ZeroCheck = dict(base_510_prm)
ZeroCheck.update({
   'test_num'              : 551,
   'prm_name'              : "ZeroCheck",
   'spc_id'                : 1,
   'timeout'               : 252000,
   'WRITE_READ_MODE'       : 0x01,              # Read Mode
   'TRANSFER_MODE'         : 1,                 # Async
   'CACHE_MODE'            : 1,                 # Default caching
   'ACCESS_MODE'           : 0,                 # Seq
   'TEST_OPERATING_MODE'   : 0,                 # Normal... 1 is fast- not sure what does
   })
ZeroCheck.pop('ERROR_REPORTING_MODE', 0)
ZeroCheck.pop('TOTAL_LBA_TO_XFER', 0)

SequentialReadDMAExt = dict(base_510_prm)
SequentialReadDMAExt.update({
            'test_num'   : 510,
            'prm_name'   : "SequentialReadDMAExt",
            'spc_id'     : 1,
            'timeout'    : 252000,
            'WRITE_READ_MODE' : (0x01), #Write Mode
            })

SequentialWRDMAExt = dict(base_510_prm)
SequentialWRDMAExt.update({
            'test_num'   : 510,
            'prm_name'   : "SequentialWRDMAExt",
            'spc_id'     : 1,
            'timeout'    : 252000,
            'WRITE_READ_MODE' : (0x00), #Write Mode
            })

RandomWriteDMAExt = dict(base_510_prm)
RandomWriteDMAExt.update({
            'test_num'   : 510,
            'prm_name'   : "RandomWriteDMAExt",
            'spc_id'     : 1,
            'timeout'    : 252000,
            'WRITE_READ_MODE' : 0x02, #Write Mode
            'NUMBER_LBA_PER_XFER': (0,0), #random block length per xfer
            'ACCESS_MODE' : (0x01),      #Random
            })

RandomReadDMAExt = dict(base_510_prm)
RandomReadDMAExt.update({
            'test_num'   : 510,
            'prm_name'   : "RandomReadDMAExt",
            'spc_id'     : 1,
            'timeout'    : 252000,
            'WRITE_READ_MODE' : 0x01, #Write Mode
            'NUMBER_LBA_PER_XFER': (0,0), #random block length per xfer
            'ACCESS_MODE' : (0x01),      #Random
            })

RandomWRDMAExt = dict(base_510_prm)
RandomWRDMAExt.update({
            'test_num'   : 510,
            'prm_name'   : "RandomWRDMAExt",
            'spc_id'     : 1,
            'timeout'    : 252000,
            'WRITE_READ_MODE' : 0x00, #Write Mode
            'NUMBER_LBA_PER_XFER': (0,0), #random block length per xfer
            'ACCESS_MODE' : (0x01),      #Random
            })

prm_510_CMDTIME_WR = {     # Write screen for NetApp customer
   'test_num'              : 510,
   'prm_name'              : 'prm_510_CMDTIME_WR',
   'timeout'               : 26193,
   'spc_id'                : 5,
   'CACHE_MODE'            : 0x0001,
   'WRITE_READ_MODE'       : 0x0002,
   'ENABLE_WT_SAME'        : 1,
   'MEASURE_TIME'          : 1,
   'MSECS_PER_CMD_SPEC'    : 5000,
   'TOT_MSECS_PER_TOT_CMDS_SPEC' : 5000,        # = 5 sec for SAS
   'TOT_CMDS_MINS_SPEC'    : 431,               # = Mean + 7%
   'ACCESS_MODE'           : 0,
   'PATTERN_MODE'          : 0x0080,
   'NUMBER_LBA_PER_XFER'   : (0, 5000),
   'PATTERN_LSW'           : 0,
   'PATTERN_MSW'           : 0,
   'STEP_SIZE'             : (0, 0, 0, 5000),
   }

prm_510_CMDTIME_RD = {     # Write screen for NetApp customer
   'test_num'              : 510,
   'prm_name'              : 'prm_510_CMDTIME_RD',
   'timeout'               : 26139,
   'spc_id'                : 5,
   'CACHE_MODE'            : 0x0001,
   'WRITE_READ_MODE'       : 0x0001,
   'MEASURE_TIME'          : 1,
   'MSECS_PER_CMD_SPEC'    : 5000,
   'TOT_MSECS_PER_TOT_CMDS_SPEC' : 5000,        # = 5 sec for SAS
   'TOT_CMDS_MINS_SPEC'    : 431,               # = Mean + 7%
   'ACCESS_MODE'           : 0,
   'NUMBER_LBA_PER_XFER'   : (0, 5000),
   'STEP_SIZE'             : (0, 0, 0, 5000),
   }

prm_510_BUTTERFLY = {
   'test_num'              : 510,
   'prm_name'              : 'prm_510_BUTTERFLY',
   'spc_id'                : 1,
   'timeout'               : 3000,
   'START_LBA34'           : (0, 0, 0, 0),
   'END_LBA34'             : (0, 0, 0, 0),      # Causes max lba
   'TOTAL_LBA_TO_XFER'     : (0, 0, 0, 0x200),  # Override this to increase test length
   'NUMBER_LBA_PER_XFER'   : (0, 256),
   'PATTERN_LSW'           : 0,
   'PATTERN_MSW'           : 0,
   'PATTERN_MODE'          : 0x80,
   'CACHE_MODE'            : 1,
   'ACCESS_MODE'           : 1,
   'SAVE_READ_ERR_TO_MEDIA': 0,
   'PATTERN_LENGTH_IN_BITS': 32,
   'ERROR_REPORTING_MODE'  : 1,
   'BUTTERFLY_ACCESS'      : 0,
   'BTRFLY_CMP_DATA'       : 0,
   }

WritePatternToBuffer = {
   'test_num'              : 508,
   'prm_name'              : 'WritePatternToBuffer',
   'timeout'               : 600,
   'PARAMETER_10'          : 0x0000,
   'PARAMETER_9'           : 0x0000,
   'PARAMETER_8'           : 0x0000,
   'PARAMETER_3'           : 0x0000,
   'PARAMETER_2'           : 0x0000,
   'PARAMETER_1'           : 0xFF00,
   'PARAMETER_7'           : 0x0000,
   'PARAMETER_6'           : 0x0000,
   'PARAMETER_5'           : 0x0000,
   'PARAMETER_4'           : 0xFF80,
   'stSuppressResults'     : ST_SUPPRESS__ALL,
   }

WriteInternalPatternToBuffer = {
   'test_num'              : 508,
   'prm_name'              : 'WriteInternalPatternToBuffer',
   'timeout'               : 600,
   'stSuppressResults'     : ST_SUPPRESS__ALL,
   }

BufferCopy = {
   'test_num'              : 508,
   'prm_name'              : 'BufferCopy',
   'timeout'               : 600,
   'stSuppressResults'     : ST_SUPPRESS__ALL,
   }

SeekTest = {
   'test_num'              : 549,
   'prm_name'              : 'RandomSeek',
   'timeout'               : 36000,
   }

SimulateWorkLoadSIOP = {
   'test_num'              : 597,
   'prm_name'              : 'SimulateWorkLoadSIOP',
   'timeout'               : 3600,
   'TEST_FUNCTION'         : (0x1000,),
   'TEST_OPERATING_MODE'   : 0x0000,
   'TEST_PASS_COUNT'       : 0x0003,
   'TEST_PASS_MULTIPLIER'  : 0x0000,
   'RW_CMD_WEIGHT'         : 0x4100,
   'RANDOM_SEED'           : 0x0C0C,
   'PATTERN_MODE'          : 0x0001,
   'ALLOW_WIDE_MODE'       : (0x0001,),
   'FORCE_ASYNC'           : (0x0000,),
   'GRADING_OUTPUT'        : (0x0000,),
   'HIGH_PARTITION_SIZE'   : (0x0000,),
   'IOPS_LOWER_LIM'        : (0x0000,),
   'MAX_BLOCK_PER_CMD'     : (0x0004,),
   'MAX_UNRECOVERABLE_ERR' : (0x0000,),
   'MISC_CMD_WEIGHT'       : (0x0000,),
   'MULT_CMD_PACKET'       : (0x0000,),
   #'OPERATIONAL_FLAGS'     : (0x0007,),
   'PARTITION_NUM'         : (0x0002,),
   'PARTITION_SIZE'        : (0x0000,),
   'QUEUE_DEPT'            : (0x0000,),
   'QUEUE_TAG_WEIGHT'      : (0x0001,),
   'RECOVERED_ERR_LIMS'    : (0x0100,),
   'REQ_ACK_OFFSET'        : (0x0000,),
   }
   
prm_549_ButterflyReadSeek = {
   'test_num'                 : 549,
   'prm_name'                 : 'prm_549_ButterflyReadSeek',
   'timeout'                  : 3600,
   'spc_id'                   : 1,
   'CYLINDER_INC_DEC'         : (30,),  # Seek step size
   'TEST_FUNCTION'            : (0x0000,),
   'MAX_SEEK_TIME'            : (0xFFFF,),
   'HEAD_SELECTION'           : (0x0000,),  # Manually select head to use
   'SEEK_TIME_DELTA'          : (0x0000,),
   'MIN_SEEK_TIME_DELTA_SPEC' : (0x0000,),
   'AVG_SEEK_TIME_DELTA_SPEC' : (0x0000,),
   'END_CYL'                  : (0x0000,0x0000,),  # Use max cylinder
   'SCAN_MODE'                : (0x0000,),
   'START_CYL'                : (0x0000,0x0000,),
   'MAXIMUM_ERROR_COUNT'      : (0x4000,),  # bit 14 = rd seek, bits 12:8 = head 0
   'SEEK_DELAY'               : (0x0000,),
   'SEEK_COUNT'               : (0x1388,),
   'MAX_SEEK_TIME_DELTA_SPEC' : (0x0000,),
   'SAVE_SEEK_TIME'           : (0x0000,),
   'MAX_AVG_SEEK_TIME'        : (0xFFFF,),
   'TUNED_END_CYL'            : (0x00FF,0xFFFF,),
   'SERVO_RAM_ADDRESS'        : (0x0000,),
   'REPORT_SEEK_TIME'         : (0x0000,),
   'CHK_OFF_TRACK_FAULTS'     : (0x0000,),
   'TEST_OPERATING_MODE'      : (0x0007,),  # Butterfly seek sequential/manual head
   'TIMER_OPTION'             : (0x0001,),
   'SEEK_DIRECTION'           : (1,),  # 0=Diverge, 1=Converge
   'REPORT_SEEK_TIME'         : (1,),
   }

prm_507_549 = {               # T549 needs this to look for dealloc trks
   'test_num'                 : 507,
   'prm_name'                 : 'prm_507_549',
   'timeout'                  : 1200,
   'RETRY_COUNT_RANGE_END'    : 0,
   'SET_SDBP_MODE_ON'         : 0,
   'DELAYED_START'            : 0,
   'TEST_FUNCTION'            : 0,
   'MAX_HEAD_IDENTIFICATION'  : 0,
   'SET_SERVO_GAP_BYTE_COUNT' : 0,
   'REMOTE_START'             : 0,
   'WRT_READ_DISCONNECT_MODE' : 1,
   'RESET_DRIVE_AFTER_TEST'   : 0,
   'SAVE_LAST_50_COMMANDS'    : 0,
   'RETRY_COUNT_RANGE_START'  : 0,
   'ACTIVE_LED_ON'            : 0,
   'SET_SERVO_WEDGES_PER_TRK' : 1,
   'ONE_SEC_PER_ILQ_MODE'     : 0,
   'UNKNOWN_MODEL_NUMBER'     : 0,
   'SERVO_GAP_BYTE_COUNT'     : 0,
   'ONE_CRC_WRD_PER_PKT_MODE' : 0,
   'DRIVE_CONFIG_TBL_REFRESH' : 0,
   'SERVO_WEDGES_PER_TRACK'   : 0x01A0,
   'stSuppressResults'        : ST_SUPPRESS__ALL,
   }

prm_549_RdmWrtSeek = {     # Random Write Seek
   'test_num'              : 549,
   'prm_name'              : 'prm_549_RdmWrtSeek',
   'timeout'               : 10800,
   'spc_id'                : 1,
   'HEAD_SELECTION'        : 1,
   'END_CYL'               : (0x0000, 64244),
   'START_CYL'             : (0x0000, 0x0000),
   'MAXIMUM_ERROR_COUNT'   : 16384,
   'TEST_OPERATING_MODE'   : 1,
   }

DisplayBufferData = {
            'test_num'     : 508,
            'prm_name'     : 'DisplayReadBuffer',
            'timeout'      : 600,
            'PARAMETER_10' : (0x0000,),
            'PARAMETER_9' : (0x0000,),
            'PARAMETER_8' : (0x0000,),
            'PARAMETER_3' : (0x000F,),
            'PARAMETER_2' : (0x0000,),
            'PARAMETER_1' : (0x0005,),
            'PARAMETER_7' : (0x0000,),
            'PARAMETER_6' : (0x0000,),
            'PARAMETER_5' : (0x0000,),
            'PARAMETER_4' : (0x0000,),
            'DblTablesToParse': ['P000_BUFFER_DATA','P508_BUFFER']
   }

UnlockFactoryCmds = {
   'test_num'              : 638,
   'prm_name'              : 'UnlockFactoryCmds',
   'timeout'               : 3600,
   'ATTRIBUTE_MODE'        : (0x0000,),
   'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
   'REPORT_OPTION'         : (0x0000,),
   'SCSI_COMMAND'          : (0x0000,),
   'TEST_FUNCTION'         : (0x0000,),
   'BYPASS_WAIT_UNIT_RDY'  : (0x0001,),
   'LONG_COMMAND'          : (0x0000,),
   'PARAMETER_0'           : (0xFFFF,),
   'PARAMETER_1'           : (0x0100,),
   'PARAMETER_2'           : (0x9A32,),
   'PARAMETER_3'           : (0x4F03,),
   'PARAMETER_4'           : (0x0000,),
   'PARAMETER_5'           : (0x0000,),
   'PARAMETER_6'           : (0x0000,),
   'PARAMETER_7'           : (0x0000,),
   'PARAMETER_8'           : (0x0000,),
   'stSuppressResults'     : ST_SUPPRESS__ALL,
   }
if testSwitch.BF_0126696_231166_FIX_CMD_FAIL_IN_SAS_DITS_UNLK:
   UnlockFactoryCmds['BYPASS_WAIT_UNIT_RDY'] = 0

ClearFormatCorrupt = {
   'test_num':638,
   'prm_name':'ClearFormatCorrupt',
   'timeout':3600,
   'ATTRIBUTE_MODE' : (0x0000,),
   'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
   'REPORT_OPTION' : (0x0000,),
   'PARAMETER_8' : (0x0000,),
   'SCSI_COMMAND' : (0x0000,),
   'PARAMETER_7' : (0x0000,),
   'TEST_FUNCTION' : (0x0000,),
   'BYPASS_WAIT_UNIT_RDY' : (0x0000,),
   'PARAMETER_1' : (0x0100,),
   'PARAMETER_2' : (0x0100,),
   'PARAMETER_3' : (0x0000,),
   'PARAMETER_0' : (0x1301,),
   'LONG_COMMAND' : (0x0000,),
   'PARAMETER_6' : (0x0000,),
   'PARAMETER_5' : (0x0000,),
   'PARAMETER_4' : (0x0000,),
   }

ClearFormatCorrupt_1 = {
# oProc.St({'test_num':538},0x0000,0xC800,0x0000,0x0000,0x0000,0x0000,0x0200,0x0001,0x0000,0x0000,timeout=3600) # Clr format corrupt, no chk ready
   'test_num':538,
   'prm_name':'ClearFormatCorrupt_1',
   'timeout':3600,
   'COMMAND_WORD_5' : (0x0000,),
   'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
   'READ_CAPACITY' : (0x0000,),
   'COMMAND_WORD_6' : (0x0000,),
   'COMMAND_WORD_1' : (0xC800,),
   'SECTOR_SIZE' : (0x0200,),
   'COMMAND_WORD_3' : (0x0000,),
   'SELECT_COPY' : (0x0000,),
   'SUPRESS_RESULTS' : (0x0000,),
   'TEST_FUNCTION' : (0x0000,),
   'COMMAND_WORD_2' : (0x0000,),
   'COMMAND_WORD_4' : (0x0000,),
   'TRANSFER_LENGTH' : (0x0000,),
   'CHK_OPEN_LATCH_RETRY_CNT' : (0x0000,),
   'USE_CMD_ATTR_TST_PARMS' : (0x0000,),
   'TRANSFER_OPTION' : (0x0001,),
   }

FormatDevice = {
   'test_num':511,
   'prm_name':'FormatDevice',
   'timeout':3600,
   'CONDITIONAL_FORMAT': 0,
   'FORMAT_MODE': 1,
   'DISABLE_PRIMARY_LIST': 0,
   'DISABLE_CERTIFICATION': 1,
   'IMMEDIATE_BIT': 1,
   }

CertBadBlocks = {
   'test_num':515,
   'prm_name':'CertBadBlocks',
   'timeout':3600,
   'TEST_OPERATING_MODE': 0,
   }

DisplayBadBlocks = {
   'test_num':529,
   'prm_name':'Display Bad Blocks',
   'timeout':3600,
   'GLIST_OPTION': 2,
   #'SERVO_DEFECT_FUNCTION': 2,
   'MAX_GLIST_ENTRIES': (0xFFFF, 0xFFFF),
   #'MAX_SERVO_DEFECTS': 0xFFFF,
   'GRADING_OUTPUT': 1,
   'DblTablesToParse': ['P000_FLAW_COUNT',]
   }

MergeDefectLists = {
   'test_num':529,
   'prm_name':'MergeDefectLists',
   'timeout':3600,
   'GLIST_OPTION': 1,
   'MAX_GLIST_ENTRIES': (0xFFFF, 0xFFFF),
   'GRADING_OUTPUT': 0,
   'SERVO_DEFECT_FUNCTION': 1,
   'MAX_SERVO_DEFECTS': 0xFFFF,
}
if testSwitch.WA_0139839_231166_P_RETRY_11102_IN_MERGE_G:
   MergeDefectLists.update({
      'retryECList'              : [11102,],
      'retryCount'               : 3,
      'retryMode'                : HARD_RESET_RETRY,
   })

FormatDrive_CertifyDisabled = {
# oProc.St({'test_num':511},0x0000,0x01A0,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=72000) # Certify Disabled
   'test_num':511,
   'prm_name':'FormatDrive_CertifyDisabled',
   'timeout':72000,
   'HEAD_TO_FORMAT_LSW' : (0x0000,),
   'END_TRACK' : (0x0000,0x0000,),
   'TEST_FUNCTION' : (0x0000,),
   'HEAD_TO_FORMAT_MSW' : (0x0000,),
   'INIT_PATTERN_MODIFIER' : (0x0000,),
   'INIT_PATTERN' : (0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,),
   'IMMEDIATE_BIT' : (0x0000,),
   'INIT_PATTERN_BIT' : (0x0000,),
   'DEFECT_LIST_FORMAT' : (0x0000,),
   'COMP_LIST_OF_GRWTH_DEFS' : (0x0001,),
   'LBA_INTERVAL' : (0x0000,),
   'FORMAT_OPTIONS_VARIABLE' : (0x0001,),
   'FORMAT_MODE' : (0x0000,),
   'DISABLE_PRIMARY_LIST' : (0x0000,),
   'DISABLE_CERTIFICATION' : (0x0001,),
   'STOP_FMT_ON_DEFT_LST_ERR' : (0x0000,),
   'START_TRACK' : (0x0000,0x0000,),
   'CONDITIONAL_FORMAT' : (0x0000,),
   'INIT_PATTERN_LENGTH' : (0x0000,),
   'DISABLE_SAVING_PARAMS' : (0x0000,),
   'HEAD_TO_FORMAT' : (0x0000,),
   'COMPARE_OPTION' : (0x0000,),
   }

FormatDrive_CertifyEnabled = {
# oProc.St({'test_num':511},0x0000,0x01A0,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=72000) # Certify Disabled
   'test_num':511,
   'prm_name':'FormatDrive_CertifyEnabled',
   'timeout':144000,
   'HEAD_TO_FORMAT_LSW' : (0x0000,),
   'END_TRACK' : (0x0000,0x0000,),
   'TEST_FUNCTION' : (0x0000,),
   'HEAD_TO_FORMAT_MSW' : (0x0000,),
   'INIT_PATTERN_MODIFIER' : (0x0000,),
   'INIT_PATTERN' : (0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,),
   'IMMEDIATE_BIT' : (0x0000,),
   'INIT_PATTERN_BIT' : (0x0000,),
   'DEFECT_LIST_FORMAT' : (0x0000,),
   'COMP_LIST_OF_GRWTH_DEFS' : (0x0001,),
   'LBA_INTERVAL' : (0x0000,),
   'FORMAT_OPTIONS_VARIABLE' : (0x0001,),
   'FORMAT_MODE' : (0x0000,),
   'DISABLE_PRIMARY_LIST' : (0x0000,),
   'DISABLE_CERTIFICATION' : (0x0000,),
   'STOP_FMT_ON_DEFT_LST_ERR' : (0x0000,),
   'START_TRACK' : (0x0000,0x0000,),
   'CONDITIONAL_FORMAT' : (0x0000,),
   'INIT_PATTERN_LENGTH' : (0x0000,),
   'DISABLE_SAVING_PARAMS' : (0x0000,),
   'HEAD_TO_FORMAT' : (0x0000,),
   'COMPARE_OPTION' : (0x0000,),
   }

FormatDriveTimeout = {
# oProc.St({'test_num':506},0x0000,0x0000,0x0000,0xE100,0x0000,0x0000,0x0000,0x3840,0x0000,0x0000,timeout=1200)  # Setting command timeout to 16 hours for format
   'test_num':506,
   'prm_name':'FormatDriveTimeout',
   'timeout':1200,
   'FORMAT_CMD_TIME_MSB' : (0x0000,),
   'FACTORY_CMD_TIMEOUT_SECS' : (0x3840,),
   'COMMAND_TIMEOUT_MS' : (0x0000,),
   'TEST_FUNCTION' : (0x0000,),
   'TEST_EXE_TIME_SECONDS' : (0x0000,),
   'RESPONSE_TIME_MS' : (0x0000,),
   'WAIT_READY_TIME' : (0x0000,),
   'FORMAT_CMD_TIME_LSB' : (0xE100,),
   'COMMAND_TIMEOUT_SECONDS' : (0x0000,),
   }

FormatDriveTimeout_Certify = {
# oProc.St({'test_num':506},0x0000,0x0000,0x0000,0xE100,0x0000,0x0000,0x0000,0x3840,0x0000,0x0000,timeout=1200)  # Setting command timeout to 32 hours for format
   'test_num':506,
   'prm_name':'FormatDriveTimeout_Certify',
   'timeout':1200,

   'FACTORY_CMD_TIMEOUT_SECS' : (0x3840,),
   'COMMAND_TIMEOUT_MS' : (0x0000,),
   'TEST_FUNCTION' : (0x0000,),
   'TEST_EXE_TIME_SECONDS' : (0x0000,),
   'RESPONSE_TIME_MS' : (0x0000,),
   'WAIT_READY_TIME' : (0x0000,),
   'FORMAT_CMD_TIME_MSB' : (0x0001,),
   'FORMAT_CMD_TIME_LSB' : (0xc200,),
   'COMMAND_TIMEOUT_SECONDS' : (0x0000,),
   }

if testSwitch.FE_0136005_357552_USE_ALL_FIS_ATTRS_FOR_DTD_CREATION:
   WriteMIFDataToDisc = {
      'test_num' : 595,
      'prm_name' : 'WriteMIFDataToDisc',
      'timeout' : 3600,
      "AP_LSI_OFFSET" : (0x0034,),
      "ATTRIBUTE_MODE" : (0x0004,),
      "CTRL_WORD1" : (0x003F,),
      "INIT_MFG_INFO_FILE" : (0x0001,),
      "MFG_INFO_FILE_FMT" : (0x0001,),
      "OPTIONS_WORD1" : (0x1FFE,),
      "OPTIONS_WORD2" : (0x001F,),
      "PAGE_LENGTH" : (0x0000,),
      "TEST_FUNCTION" : (0x0000,),
      "VPD_PAGE_DATA1" : (0x0000,),
      "VPD_PAGE_DATA2" : (0x0000,),
      "VPD_PAGE_DATA3" : (0x0000,),
      "VPD_PAGE_DATA4" : (0x0000,),
   }
else:
   WriteMIFDataToDisc = {
      'test_num':595,
      'prm_name':'WriteMIFDataToDisc',
      'timeout':3600,
      'INIT_MFG_INFO_FILE': 1,
      'MFG_INFO_FILE_FMT': 0,
      'ATTRIBUTE_MODE': 4,
      'OPTIONS_WORD1': 0xFF,
      'OPTIONS_WORD2': 0xFF,
   }

GetPreampTemp = {
   # Get converted temp.
   'test_num':638,
   'prm_name':'GetPreampTemp',
   'timeout':1200,
   'ATTRIBUTE_MODE' : (0x0000,),
   'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
   'REPORT_OPTION' : (0x0000,),
   'PARAMETER_8' : (0x0000,),
   'SCSI_COMMAND' : (0x0000,),
   'PARAMETER_7' : (0x0000,),
   'TEST_FUNCTION' : (0x0000,),
   'BYPASS_WAIT_UNIT_RDY' : (0x0000,),
   'PARAMETER_3' : (0x0000,),
   'PARAMETER_2' : (0x0000,),
   'PARAMETER_1' : (0x0100,),
   'PARAMETER_0' : (0x5001,),
   'LONG_COMMAND' : (0x0000,),
   'PARAMETER_6' : (0x0001,),
   'PARAMETER_5' : (0x0200,),
   'PARAMETER_4' : (0x0000,),
   }

FlushCache = {
   'test_num':538,
   'prm_name':'FlushCache',
   'timeout':3600,
   'COMMAND_WORD_5' : (0x0000,),
   'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
   'READ_CAPACITY' : (0x0000,),
   'COMMAND_WORD_6' : (0x0000,),
   'COMMAND_WORD_1' : (0x3500,),
   'SECTOR_SIZE' : (0x0000,),
   'COMMAND_WORD_3' : (0x0000,),
   'SELECT_COPY' : (0x0000,),
   'SUPRESS_RESULTS' : (0x0000,),
   'TEST_FUNCTION' : (0x0000,),
   'COMMAND_WORD_2' : (0x0000,),
   'COMMAND_WORD_4' : (0x0000,),
   'TRANSFER_LENGTH' : (0x0000,),
   'CHK_OPEN_LATCH_RETRY_CNT' : (0x0000,),
   'USE_CMD_ATTR_TST_PARMS' : (0x0000,),
   'TRANSFER_OPTION' : (0x0000,),
   }

Seek = {
   'test_num':638,
   'prm_name':'Seek',
   'timeout':1200,
   'ATTRIBUTE_MODE' : (0x0000,),
   'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
   'REPORT_OPTION' : (0x0000,),
   'PARAMETER_8' : (0x0000,),
   'SCSI_COMMAND' : (0x0000,),
   'PARAMETER_7' : (0x0000,),
   'TEST_FUNCTION' : (0x0000,),
   'BYPASS_WAIT_UNIT_RDY' : (0x0000,),
   'PARAMETER_3' : (0x0000,),
   'PARAMETER_2' : (0x0000,),
   'PARAMETER_1' : (0x0100,),
   'PARAMETER_0' : (0x3401,),
   'LONG_COMMAND' : (0x0000,),
   'PARAMETER_6' : (0x0000,),
   'PARAMETER_5' : (0x0000,),
   'PARAMETER_4' : (0x0000,),
   }

GetMaxLBA_non16 = {
   'test_num':538,
   'prm_name':'GetMaxLBA',
   'timeout':3600,
   'COMMAND_WORD_5' : (0x0000,),
   'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
   'READ_CAPACITY' : (0x0000,),
   'COMMAND_WORD_6' : (0x0000,),
   'COMMAND_WORD_1' : (0x2500,),
   'SECTOR_SIZE' : (0x0000,),
   'COMMAND_WORD_3' : (0x0000,),
   'SELECT_COPY' : (0x0000,),
   'SUPRESS_RESULTS' : (0x0000,),
   'TEST_FUNCTION' : (0x0000,),
   'COMMAND_WORD_2' : (0x0000,),
   'COMMAND_WORD_4' : (0x0000,),
   'TRANSFER_LENGTH' : (0x0000,),
   'CHK_OPEN_LATCH_RETRY_CNT' : (0x0000,),
   'USE_CMD_ATTR_TST_PARMS' : (0x0000,),
   'TRANSFER_OPTION' : (0x0000,),
   'DblTablesToParse': ['P000_BUFFER_DATA',]
   }

GetMaxLBA = {
   'test_num':538,
   'prm_name':'GetMaxLBA',
   'timeout':30,
   'COMMAND_WORD_5' : (0x0000,),
   'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
   'READ_CAPACITY' : (0x0000,),
   'COMMAND_WORD_6' : (0x0000,),
   'COMMAND_WORD_7' : (0x0020,),
   'COMMAND_WORD_1' : (0x9E10,),
   'SECTOR_SIZE' : (0x0000,),
   'COMMAND_WORD_3' : (0x0000,),
   'SELECT_COPY' : (0x0000,),
   'SUPRESS_RESULTS' : (0x0000,),
   'TEST_FUNCTION' : (0x0000,),
   'COMMAND_WORD_2' : (0x0000,),
   'COMMAND_WORD_4' : (0x0000,),
   'TRANSFER_LENGTH' : (0x0000,),
   'CHK_OPEN_LATCH_RETRY_CNT' : (0x0000,),
   'USE_CMD_ATTR_TST_PARMS' : (0x0000,),
   'TRANSFER_OPTION' : (0x0000,),
   'DblTablesToParse': ['P000_BUFFER_DATA',]
   }

LongDST = {
   'test_num':600,
   'prm_name':'LongDST',
   'timeout':54000,
   'TEST_OPERATING_MODE' : (0x0002,),
   'TEST_FUNCTION' : (0x0000,),
   'DELAY_TIME' : (0x007D,),
   }
   
ShortDST = {
   'test_num':600,
   'prm_name':'ShortDST',
   'timeout':1200,
   'TEST_OPERATING_MODE' : (0x0001,),
   'TEST_FUNCTION' : (0x0000,),
   'DELAY_TIME' : (0x007D,),
   }

SmartEnableOper = {
   'test_num':538,
   'prm_name':'SmartEnableOper',
   'timeout':3600,
   'COMMAND_WORD_5' : (0x0000,),
   'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
   'READ_CAPACITY' : (0x0000,),
   'COMMAND_WORD_6' : (0x0000,),
   'COMMAND_WORD_1' : (0x1C00,),
   'SECTOR_SIZE' : (0x0000,),
   'COMMAND_WORD_3' : (0x0000,),
   'SELECT_COPY' : (0x0000,),
   'SUPRESS_RESULTS' : (0x0000,),
   'TEST_FUNCTION' : (0x0000,),
   'COMMAND_WORD_2' : (0x0000,),
   'COMMAND_WORD_4' : (0x0000,),
   'TRANSFER_LENGTH' : (0x0000,),
   'CHK_OPEN_LATCH_RETRY_CNT' : (0x0000,),
   'USE_CMD_ATTR_TST_PARMS' : (0x0000,),
   'TRANSFER_OPTION' : (0x0000,),
   }

SmartReturnStatus = {
   'test_num':518,
   'prm_name':'SmartReturnStatus',
   'timeout':3600,
   'MODE_COMMAND': 0,
   'MODE_SENSE_OPTION': 0,
   'PAGE_CODE': 0x1C,
   'DblTablesToParse': ['P518_MODE_SENSE_HEADER',]
   }
if testSwitch.BF_0173040_470833_P_FIX_SAS_SIC_T518_HEADER_ISSUES:
	SmartReturnStatus.update({'DblTablesToParse': ['P518_MODE_SENSE_HEADER','P000_MODE_SENSE_HEADER',]}) #Allow P000 tables to be returned

SmartReturnFrameData = {
   'test_num':564,
   'prm_name':'SmartReturnFrameData',
   'timeout':1200,
   'spc_id':1,
   'BAD_SAMPLE_CNT' : (0xFFFF,),
   'BAD_ADDRESS_COUNT' : (0xFFFF,),
   'TEST_FUNCTION' : (0x0000,),
   'MAX_REALLOCATED_SECTORS' : (0x00FF,),
   'CHECK_ALL_SELECTED_HDS' : (0x0000,),
   'BUZZ_COUNT' : (0xFFFF,),
   'MAX_THERMAL_ASP' : (0x00FF,),
   'MAXIMUM_ERROR_COUNT' : (0x0000,),
   'SUPPRESS_REPORT_DATA' : (0x0000,),
   'SOME_HEADS' : (0x0000,),
   'SMART_ATTRIBUTE' : (0x0000,),
   'ONE_TRACK' : (0x00FF,),
   'MAX_READ_ERRORS' : (0x00FF,),
   'TEMPERATURE' : (0xFF1E,),
   'FLY_HEIGHT_MEAS' : (0x00FF,),
   'TA_WUS_SPEC' : (0x00FF,),
   'SEEK_ERR_LIMIT' : (0x00FF,),
   'SELECTED_HEAD' : (0x0000,),
   'NO_TIMING_MARK_DET' : (0xFFFF,),
   'ONE_THIRD_SEEK' : (0x00FF,),
   'SRVO_UNSF_SPEC' : (0x00FF,),
   'EXTREME_HEADS' : (0x0000,),
   'BUFFER_IOECC': 0xFFFF,
   }
if testSwitch.FE_0140112_357552_FAIL_FOR_IO_TCM_ECC_ERRORS:
   SmartReturnFrameData.update({'BUFFER_IOECC': 0}) #Fail if any IOECC errors

SmartReturnStatusDITS = {
   'test_num':638,
   'prm_name':'SmartReturnStatusDITS',
   'timeout':1200,
   'ATTRIBUTE_MODE' : (0x0000,),
   'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
   'REPORT_OPTION' : (0x0000,),
   'PARAMETER_8' : (0x0000,),
   'SCSI_COMMAND' : (0x0000,),
   'PARAMETER_7' : (0x0000,),
   'TEST_FUNCTION' : (0x0000,),
   'BYPASS_WAIT_UNIT_RDY' : (0x0000,),
   'PARAMETER_3' : (0x0000,),
   'PARAMETER_2' : (0x0400,),
   'PARAMETER_1' : (0x0100,),
   'PARAMETER_0' : (0x5201,),
   'LONG_COMMAND' : (0x0000,),
   'PARAMETER_6' : (0x0000,),
   'PARAMETER_5' : (0x0000,),
   'PARAMETER_4' : (0x0000,),
   'DblTablesToParse': ['P000_BUFFER_DATA',]
   }

SmartReadLogSecSize = {
   'test_num':638,
   'prm_name':'SmartReadLogSecSize',
   'timeout':1200,
   'ATTRIBUTE_MODE' : (0x0000,),
   'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
   'REPORT_OPTION' : (0x0000,),
   'PARAMETER_8' : (0x0000,),
   'SCSI_COMMAND' : (0x0000,),
   'PARAMETER_7' : (0x0000,),
   'TEST_FUNCTION' : (0x0000,),
   'BYPASS_WAIT_UNIT_RDY' : (0x0000,),
   'PARAMETER_3' : (0x0000,),
   'PARAMETER_2' : (0x0F00,),
   'PARAMETER_1' : (0x0100,),
   'PARAMETER_0' : (0x5201,),
   'LONG_COMMAND' : (0x0000,),
   'PARAMETER_6' : (0x0000,),
   'PARAMETER_5' : (0x0000,),
   'PARAMETER_4' : (0x0000,),
   'DblTablesToParse': ['P000_BUFFER_DATA',]
   }

if testSwitch.FE_0134083_231166_UPDATE_SMART_AND_UDS_INIT:
   ClearSmartPredictiveCounters = {
      'test_num':638,
      'prm_name':'ClearSmartPredictiveCounters',
      'timeout':1200,
      'ATTRIBUTE_MODE' : (0x0000,),
      'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
      'REPORT_OPTION' : (0x0000,),
      'PARAMETER_8' : (0x0000,),
      'SCSI_COMMAND' : (0x0000,),
      'PARAMETER_7' : (0x0000,),
      'TEST_FUNCTION' : (0x0000,),
      'BYPASS_WAIT_UNIT_RDY' : (0x0001,),
      'PARAMETER_3' : (0x0000,),
      'PARAMETER_2' : (0x0000,),
      'PARAMETER_1' : (0x0100,),
      'PARAMETER_0' : (0x5201,),
      'LONG_COMMAND' : (0x0000,),
      'PARAMETER_6' : (0x0000,),
      'PARAMETER_5' : (0x0000,),
      'PARAMETER_4' : (0x0000,),
   }

   InitSmartHeadAmp = {
      'test_num':638,
      'prm_name':'InitSmartHeadAmp',
      'timeout':1200,
      'ATTRIBUTE_MODE' : (0x0000,),
      'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
      'REPORT_OPTION' : (0x0000,),
      'PARAMETER_8' : (0x0000,),
      'SCSI_COMMAND' : (0x0000,),
      'PARAMETER_7' : (0x0000,),
      'TEST_FUNCTION' : (0x0000,),
      'BYPASS_WAIT_UNIT_RDY' : (0x0001,),
      'PARAMETER_3' : (0x0000,),
      'PARAMETER_2' : (0x0A00,),
      'PARAMETER_1' : (0x0100,),
      'PARAMETER_0' : (0x5201,),
      'LONG_COMMAND' : (0x0000,),
      'PARAMETER_6' : (0x0000,),
      'PARAMETER_5' : (0x0000,),
      'PARAMETER_4' : (0x0000,),
   }

InitAltTone = {
   'test_num' : 638,
   'prm_name' : 'prm_638_WrtSMART_AltTone',
   'timeout' : 65,
   'ATTRIBUTE_MODE' : (0x0000,),
   'BYPASS_WAIT_UNIT_RDY' : (0x0001,),
   'CMD_BYTE_GROUP_0' : (0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,),
   'CMD_BYTE_GROUP_1' : (0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,),
   'CMD_BYTE_GROUP_2' : (0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,),
   'CMD_DFB_LENGTH' : (0x0000,),
   'LONG_COMMAND' : (0x0000,),
   'PARAMETER_0' : (0x5201,),
   'PARAMETER_1' : (0x0100,),
   'PARAMETER_2' : (0x0902,),
   'PARAMETER_3' : (0x3D00,),
   'PARAMETER_4' : (0x0000,),
   'PARAMETER_5' : (0x0200,),
   'PARAMETER_6' : (0x0000,),
   'PARAMETER_7' : (0x0000,),
   'PARAMETER_8' : (0x0000,),
   'REPORT_OPTION' : (0x0000,),
   'SCSI_COMMAND' : (0x0000,),
   'SECTOR_SIZE' : (0x0000,),
   'TEST_FUNCTION' : (0x0000,),
   'TRANSFER_LENGTH' : (0x0000,),
   'TRANSFER_MODE' : (0x0000,),
   'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
   }

ClearSmart = {
   'test_num':638,
   'prm_name':'ClearSmart',
   'timeout':1200,
   'ATTRIBUTE_MODE' : (0x0000,),
   'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
   'REPORT_OPTION' : (0x0000,),
   'PARAMETER_8' : (0x0000,),
   'SCSI_COMMAND' : (0x0000,),
   'PARAMETER_7' : (0x0000,),
   'TEST_FUNCTION' : (0x0000,),
   'BYPASS_WAIT_UNIT_RDY' : (0x0000,),
   'PARAMETER_3' : (0x0000,),
   'PARAMETER_2' : (0x0800,),
   'PARAMETER_1' : (0x0100,),
   'PARAMETER_0' : (0x5201,),
   'LONG_COMMAND' : (0x0000,),
   'PARAMETER_6' : (0x0000,),
   'PARAMETER_5' : (0x0000,),
   'PARAMETER_4' : (0x0000,),
   }

SmartReadLogSec_smarcmd = {
   'test_num':638,
   'prm_name':'SmartReadLogSec',
   'timeout':1200,
   'ATTRIBUTE_MODE' : (0x0000,),
   'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
   'REPORT_OPTION' : (0x0000,),
   'PARAMETER_8' : (0x0000,),
   'SCSI_COMMAND' : (0x0000,),
   'TEST_FUNCTION' : (0x0000,),
   'BYPASS_WAIT_UNIT_RDY' : (0x0000,),
   'PARAMETER_3' : (0x0000,), # smart command argument 2
   'PARAMETER_2' : (0x0C00,), #command C- read smart log/smart command argument 1
   'PARAMETER_1' : (0x0100,), #rev1
   'PARAMETER_0' : (0x5201,), #command 0x152
   'LONG_COMMAND' : (0x0000,),
   'PARAMETER_7' : (0x0000,), #allocation length (read size) 2
   'PARAMETER_6' : (0x0000,), #allocation length (read size) 1
   'PARAMETER_5' : (0x0000,), #mem offset 2
   'PARAMETER_4' : (0x0000,), #mem offset 1
}

SmartReadLogSec = {
   'test_num':638,
   'prm_name':'SmartReadLogSec',
   'timeout':1200,
   'ATTRIBUTE_MODE' : (0x0000,),
   'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
   'REPORT_OPTION' : (0x0000,),
   'PARAMETER_8' : (0x0000,),
   'SCSI_COMMAND' : (0x0000,),
   'TRANSFER_MODE': 1,
   'TRANSFER_LENGTH': 0,
   'SECTOR_SIZE': 0,
   'TEST_FUNCTION' : (0x0000,),
   'BYPASS_WAIT_UNIT_RDY' : (0x0000,),
   'PARAMETER_3' : (0x0000,), # starting lock index
   'PARAMETER_2' : (0x3500,), #smart log 0x35/ transfer length
   'PARAMETER_1' : (0x0100,), #rev1
   'PARAMETER_0' : (0x4401,), #command 0x144
   'LONG_COMMAND' : (0x0000,),
   'PARAMETER_7' : (0x0000,), #
   'PARAMETER_6' : (0x0000,), #
   'PARAMETER_5' : (0x0000,), #mem offset 2
   'PARAMETER_4' : (0x0000,), #mem offset 1
   'DblTablesToParse': ['P000_BUFFER_DATA',]
   }

WriteFinalAssemblyDate = {
   'test_num'           : 557,
   'prm_name'           : "WriteFinalAssemblyDate",
   "DATE_FORMAT"        : (0x0001,),
   "ETF_DATE_OFFSET"    : (0x0046,),
   "CURRENT_MONTH_YEAR" : (0),
   "TEST_OPERATING_MODE" : (0x0000,),
   "TEST_FUNCTION"      : (0x0000,),
   "CURRENT_DAY_WEEK"   : (0,),
   "MAX_ETF_DAYS_DELTA" : (0x0000,),
   "timeout"            : 600,
   }

Standby = {
   'test_num':538,
   'prm_name':'Standby',
   'timeout':3600,
   'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
   'READ_CAPACITY' : (0x0000,),
   'COMMAND_WORD_6' : (0x0000,),
   'COMMAND_WORD_5' : (0x0000,),
   'COMMAND_WORD_4' : (0x0000,),
   'COMMAND_WORD_3' : (0x3000,), #puts the drive in standby... host has power control now
   'COMMAND_WORD_2' : (0x0000,),
   'COMMAND_WORD_1' : (0x1B00,),
   'SECTOR_SIZE' : (0x0000,),
   'SELECT_COPY' : (0x0000,),
   'SUPRESS_RESULTS' : (0x0000,),
   'TEST_FUNCTION' : (0x0000,),
   'TRANSFER_LENGTH' : (0x0000,),
   'CHK_OPEN_LATCH_RETRY_CNT' : (0x0000,),
   'USE_CMD_ATTR_TST_PARMS' : (0x0000,),
   'TRANSFER_OPTION' : (0x0000,),
   }

StandbyImmed = Standby.copy()
StandbyImmed.update({
   'COMMAND_WORD_3' : (0xB000,),
   'prm_name':'StandbyImmed',
   })

TransferRate = {
   'test_num' : 535,
   'prm_name' : 'TransferRate',
   'timeout' : 300,
   "FC_SAS_TRANSFER_RATE" : (0x0000,),
   "TEST_FUNCTION" : (0x8000,),
   "TEST_OPERATING_MODE" : (0x0009,),
   }

ClearSense = {
   'test_num' : 517,
   'prm_name' : 'ClearSense',
                   "SENSE_DATA_8" : (0x0000,0x0000,0x0000,0x0000,),
                   "MAX_REQS_CMD_CNT" : (0x000F,),
                   "SENSE_DATA_4" : (0x0000,0x0000,0x0000,0x0000,),
                   "SENSE_DATA_1" : (0x0000,0x0000,0x0000,0x0000,),
                   "TEST_FUNCTION" : (0x0000,),
                   "SENSE_DATA_3" : (0x0000,0x0000,0x0000,0x0000,),
                   "CHK_FRU_CODE" : (0x0000,),
                   "SENSE_DATA_5" : (0x0000,0x0000,0x0000,0x0000,),
                   "SENSE_DATA_6" : (0x0000,0x0000,0x0000,0x0000,),
                   "SENSE_DATA_7" : (0x0000,0x0000,0x0000,0x0000,),
                   "ACCEPTABLE_SNS_DATA" : (0x0000,),
                   "RPT_SEL_SNS_DATA" : (0x0000,),
                   "SRVO_LOOP_CODE" : (0x0000,),
                   "CHK_SRVO_LOOP_CODE" : (0x0000,),
                   "SEND_TUR_CMDS_ONLY" : (0x0001,),
                   "RPT_REQS_CMD_CNT" : (0x0000,),
                   "SENSE_DATA_2" : (0x0000,0x0000,0x0000,0x0000,),
                   "OMIT_DUP_ENTRY" : (0x0000,),
                   "ACCEPTABLE_IF_MATCH" : (0x0000,),
               }

CurrentFwOptionsSettings = {
   'test_num' : 518,
   'prm_name' : 'CurrentFwOptionsSettings',
   'timeout' : 1800,
   "DATA_TO_CHANGE" : (0x0000,),
   "MODE_COMMAND" : (0x0000,),
   "MODE_SELECT_ALL_INITS" : (0x0000,),
   "MODE_SENSE_INITIATOR" : (0x0000,),
   "MODE_SENSE_OPTION" : (0x0000,),
   "MODIFICATION_MODE" : (0x0000,),
   "PAGE_BYTE_AND_DATA34" : (0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,),
   "PAGE_CODE" : (0x0000,),
   "PAGE_FORMAT" : (0x0001,),
   "SAVE_MODE_PARAMETERS" : (0x0000,),
   "SUB_PAGE_CODE" : (0x0001,),
   "TEST_FUNCTION" : (0x0000,),
   "UNIT_READY" : (0x0000,),
   "VERIFY_MODE" : (0x0000,),
   }

WrtDefaultFwOptions = {
   'test_num' : 537,
   'prm_name' : 'WrtDefaultFwOptions',
   'timeout'  : 300,
   "MODE_COMMAND" : (0x0000,),
   "MODE_PAGES_BYPASSED_1" : (0x0000,),
   "MODE_PAGES_BYPASSED_2" : (0x0000,),
   "MODE_PAGES_BYPASSED_3" : (0x0000,),
   "TEST_FUNCTION" : (0x0000,),
}
if testSwitch.FE_0181878_007523_CCA_CCV_PROCESS_LCO:
   WrtDefaultFwOptions.update({
      "MODE_COMMAND" : (0x0002,),  # trigger bypass option
      "MODE_PAGES_BYPASSED_1" : (0x0003,),  # With Page 3 bypassed
      })

setModePage8_DISC = {
   'test_num'              : 518,
   'prm_name'              : 'setModePage8_DISC',
   'timeout'               : 1800,
   'DATA_TO_CHANGE'        : 0x0001,
   'MODE_COMMAND'          : 0x0001,
   'MODE_SELECT_ALL_INITS' : 0x0000,
   'MODE_SENSE_INITIATOR'  : 0x0000,
   'MODE_SENSE_OPTION'     : 0x0003,
   'MODIFICATION_MODE'     : 0x0000,
   'PAGE_BYTE_AND_DATA34'  : (0x0241,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,),
   'PAGE_CODE'             : 0x0008,
   'PAGE_FORMAT'           : 0x0000,
   'SAVE_MODE_PARAMETERS'  : 0x0001,
   'SUB_PAGE_CODE'         : 0x0000,
   'TEST_FUNCTION'         : 0x0000,
   'UNIT_READY'            : 0x0000,
   'VERIFY_MODE'           : 0x0000,
   }

setModePage8_WCE_0 = {
   'test_num'              : 518,
   'prm_name'              : 'setModePage8_WCE_0',
   'timeout'               : 1800,
   'DATA_TO_CHANGE'        : 0x0001,
   'MODE_COMMAND'          : 0x0001,
   'MODE_SELECT_ALL_INITS' : 0x0000,
   'MODE_SENSE_INITIATOR'  : 0x0000,
   'MODE_SENSE_OPTION'     : 0x0003,
   'MODIFICATION_MODE'     : 0x0000,
   'PAGE_BYTE_AND_DATA34'  : (0x0220,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,),
   'PAGE_CODE'             : 0x0008,
   'PAGE_FORMAT'           : 0x0000,
   'SAVE_MODE_PARAMETERS'  : 0x0001,
   'SUB_PAGE_CODE'         : 0x0000,
   'TEST_FUNCTION'         : 0x0000,
   'UNIT_READY'            : 0x0000,
   'VERIFY_MODE'           : 0x0000,
   }

WriteCache_Prm = {
   'test_num'              : 518,
   'prm_name'              : 'Set Write Cache Mode',
   'timeout'               : 1800,
   'DATA_TO_CHANGE'        : 0x0001,
   'MODE_COMMAND'          : 0x0001,
   'MODE_SELECT_ALL_INITS' : 0x0000,
   'MODE_SENSE_INITIATOR'  : 0x0000,
   'MODE_SENSE_OPTION'     : 0x0000,
   'MODIFICATION_MODE'     : 0x0000,
   'PAGE_BYTE_AND_DATA34'  : (0x0221,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000, 0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,),
   'PAGE_CODE'             : 0x0008,
   'PAGE_FORMAT'           : 0x0000,
   'SAVE_MODE_PARAMETERS'  : 0x0000,
   'SUB_PAGE_CODE'         : 0x0000,
   'TEST_FUNCTION'         : 0x0000,
   'UNIT_READY'            : 0x0000,
   'VERIFY_MODE'           : 0x0000,
   'stSuppressResults'     : ST_SUPPRESS__ALL,
   }

Check_RemainingPlist = {
   'test_num':530,
   'prm_name':'Check_RemainingPlist',
   'timeout':7200,
   'SET_TO_FAIL' : (0x0000,),
   'MAX_DEFECTIVE_SECTORS' : (0x0000,),
   'MAX_DEFECTIVE_SECS_CYL' : (0x0000,),
   'TEST_OPERATING_MODE' : (0x0007,),
   'TEST_FUNCTION' : (0x0000,),
   'MAX_DEFECTIVE_SECS_HEAD' : (0x0000,),
   'DEFECT_LIST_FORMAT' : (0x0000,),
   'MIN_PERCENT_ENTRIES' : (0x0000,),
   'MAX_CYL_DISPLAYED' : (0x0000,),
   'MULTIPLY_BY_10' : (0x0000,),
   'MAX_DEFECTIVE_SECS_ZONE' : (0x0000,),
   'MAX_PERCENT_DEFECTIVE' : (0x0000,),
   'MIN_PERCENT_ENTRIES' : (5,),
   }

Check_RemainingSpares = {
   'test_num':530,
   'prm_name':'Check_RemainingSpares',
   'timeout':7200,
   'SET_TO_FAIL' : (0x0000,),
   'MAX_DEFECTIVE_SECTORS' : (0x0000,),
   'MAX_DEFECTIVE_SECS_CYL' : (0x0000,),
   'TEST_OPERATING_MODE' : (0x0009,),
   'TEST_FUNCTION' : (0x0000,),
   'MAX_DEFECTIVE_SECS_HEAD' : (0x0000,),
   'DEFECT_LIST_FORMAT' : (0x0000,),
   'MIN_PERCENT_ENTRIES' : (0x0000,),
   'MAX_CYL_DISPLAYED' : (0x0000,),
   'MULTIPLY_BY_10' : (0x0000,),
   'MAX_DEFECTIVE_SECS_ZONE' : (0x0000,),
   'MAX_PERCENT_DEFECTIVE' : (0x0000,),
   'MIN_PERCENT_ENTRIES' : (5,),
   'SCALED_VAL' : (0,),
}
if testSwitch.FE_0181878_007523_CCA_CCV_PROCESS_LCO:
   Check_RemainingSpares['MIN_PERCENT_ENTRIES'] = 0
   Check_RemainingPlist['MIN_PERCENT_ENTRIES'] = 0

getModePages = {
   'test_num' : 518,
   'prm_name' : 'getModePages',
   'timeout' : 3600,
   "DATA_TO_CHANGE" : (0x0000,),
   "MODE_COMMAND" : (0x0000,),
   "MODE_SELECT_ALL_INITS" : (0x0000,),
   "MODE_SENSE_INITIATOR" : (0x0000,),
   "MODE_SENSE_OPTION" : (0x0003,),
   "MODIFICATION_MODE" : (0x0000,),
   "PAGE_CODE" : (0x0000,),
   "PAGE_FORMAT" : (0x0000,),
   "SAVE_MODE_PARAMETERS" : (0x0000,),
   "SUB_PAGE_CODE" : (0x0000,),
   "TEST_FUNCTION" : (0x0000,),
   "UNIT_READY" : (0x0000,),
   "VERIFY_MODE" : (0x0000,),
   'DblTablesToParse': ['P518_MODE_PAGE_DATA',]
   }
if testSwitch.BF_0173040_470833_P_FIX_SAS_SIC_T518_HEADER_ISSUES:
   getModePages.update({'DblTablesToParse': ['P518_MODE_PAGE_DATA','P000_MODE_PAGE_DATA',]}) #Allow P000 tables to be returned

setShippingSectorSize = {
   'test_num' : 518,
   'prm_name' : 'setShippingSectorSize',
   'timeout' : 3600,
   "DATA_TO_CHANGE" : (0x0000,),
   "MODE_COMMAND" : (0x0001,),
   "MODE_SELECT_ALL_INITS" : (0x0000,),
   "MODE_SENSE_INITIATOR" : (0x0000,),
   "MODE_SENSE_OPTION" : (0x0000,),
   "MODIFICATION_MODE" : (0x0001,),
   "PAGE_CODE" : (0x0000,),
   "PAGE_FORMAT" : (0x0000,),
   "SAVE_MODE_PARAMETERS" : (0x0000,),
   "SUB_PAGE_CODE" : (0x0000,),
   "TEST_FUNCTION" : (0x0000,),
   "UNIT_READY" : (0x0000,),
   "VERIFY_MODE" : (0x0000,),
   "PAGE_BYTE_AND_DATA34" : (0x00FF,0x01FF,0x02FF,0x03FF,0x04FF,0x05FF,0x06FF,0x07FF,0x08FF,0x09FF,0x0A00,0x0B00,0x0C00,0x0D00,0x0E02,0x0F00,),
   }

prm_506_FormatTimeout = {
   'test_num' : 506,
   'prm_name' : 'prm_506_FormatTimeout',
   'timeout' : 300,
   "COMMAND_TIMEOUT_MS" : (0x0000,),
   "COMMAND_TIMEOUT_SECONDS" : (0x0000,),
   "FACTORY_CMD_TIMEOUT_SECS" : (50000),
   "FORMAT_CMD_TIME_LSB" : (50000),    #10-Hd should be ~25k sec
   "FORMAT_CMD_TIME_MSB" : (0x0000,),
   "RESPONSE_TIME_MS" : (0x0000,),
   "TEST_EXE_TIME_SECONDS" : (0x0000,),
   "TEST_FUNCTION" : (0x0000,),
   "WAIT_READY_TIME" : (0x0000,),
   }

prm_511_SAS_Format = {
   'test_num' : 511,
   'prm_name' : 'prm_511_SAS_Format',
   'timeout' : 72000,
   "COMP_LIST_OF_GRWTH_DEFS" : (0x0001,),
   "DISABLE_CERTIFICATION" : (0x0001,),
   "FORMAT_OPTIONS_VARIABLE" : (0x0001,),
   }

IOECC_DTCM_Check = {
   'test_num' : 556,
   'prm_name' : 'IOECC_DTCM_Check',
   'timeout' : 1800,
   "TEST_FUNCTION" : (0x0000),
   "REPORT_OPTION" :(0x0000),
   "FAIL_SMART_ERR" :(0x0000),
   "SAVE_AND_COMPARE" :(0x0000),
   "TEST_OPERATING_MODE" : (0x000A),
   "MIN_HEAD_AMP" :(0x0000),
   "MAX_HEAD_AMP" :(0x0000),
   "MAX_NORM_COEF" :(0x0000),
   "TEST_HEAD" :(0x0000),
   "RETRY_LIMIT" :(0x0000),
   "NUM_MEASUREMENTS" :(0x0000),
   "MSB_BYTES_TRANSFER" :(0x0000),
   "LSB_BYTES_TRANSFER" :(0x0000),
   "FLY_HEIGHT_DELTA_OD" :(0x0000),
   "FLY_HEIGHT_DELTA_ID" :(0x0000),
   }

SCSI_SelfTest = {
   'test_num' : 552,
   'prm_name' : 'SCSI_SelfTest',
   'timeout' : 1200,
   "PARAMETER_1" : (0x0000,),
   "PARAMETER_10" : (0x0000,),
   "PARAMETER_2" : (0x0000,),
   "PARAMETER_3" : (0x0000,),
   "PARAMETER_4" : (0x0000,),
   "PARAMETER_5" : (0x0000,),
   "PARAMETER_6" : (0x0000,),
   "PARAMETER_7" : (0x0000,),
   "PARAMETER_8" : (0x0000,),
   "PARAMETER_9" : (0x0000,),
   "TEST_FUNCTION" : (0x0000,),
}
if testSwitch.FE_0141467_231166_P_SAS_FDE_SUPPORT:
   spinup_517 = {
          'test_num': 517,
          'prm_name': 'spinup_517',
          "SENSE_DATA_8" : (0x0000,0x0000,0x0000,0x0000,),
          "MAX_REQS_CMD_CNT" : (0x00FF,),
          "SENSE_DATA_4" : (0x0000,0x0000,0x0000,0x0000,),
          "SENSE_DATA_1" : (0x0000,0x0000,0x0000,0x0000,),
          "TEST_FUNCTION" : (0x0000,),
          "SENSE_DATA_3" : (0x0000,0x0000,0x0000,0x0000,),
          "CHK_FRU_CODE" : (0x0000,),
          "SENSE_DATA_5" : (0x0000,0x0000,0x0000,0x0000,),
          "SENSE_DATA_6" : (0x0000,0x0000,0x0000,0x0000,),
          "SENSE_DATA_7" : (0x0000,0x0000,0x0000,0x0000,),
          "ACCEPTABLE_SNS_DATA" : (0x0000,),
          "RPT_SEL_SNS_DATA" : (0x0001,),
          "SRVO_LOOP_CODE" : (0x0000,),
          "CHK_SRVO_LOOP_CODE" : (0x0000,),
          "SEND_TUR_CMDS_ONLY" : (0x0001,),
          "RPT_REQS_CMD_CNT" : (0x0001,),
          "SENSE_DATA_2" : (0x0000,0x0000,0x0000,0x0000,),
          "OMIT_DUP_ENTRY" : (0x0000,),
          "ACCEPTABLE_IF_MATCH" : (0x0000,),
          "SEND_TUR_CMDS_ONLY": 1,
               }
   prm_517_RequestSense5 = {
          'test_num': 517,
          'prm_name': 'prm_517_RequestSense5',
          "ACCEPTABLE_IF_MATCH" : (0x0000,),
          "ACCEPTABLE_SNS_DATA" : (0x0000,),
          "CHK_FRU_CODE" : (0x0000,),
          "CHK_SRVO_LOOP_CODE" : (0x0000,),
          "MAX_REQS_CMD_CNT" : (0x0005,),
          "OMIT_DUP_ENTRY" : (0x0000,),
          "RPT_REQS_CMD_CNT" : (0x0000,),
          "RPT_SEL_SNS_DATA" : (0x0000,),
          "SEND_TUR_CMDS_ONLY" : (0x0000,),
          "SENSE_DATA_1" : (0x0002,0x0000,0x00FF,0x0004,),
          "SENSE_DATA_2" : (0x0004,0x0000,0x00FF,0x001C,),
          "SENSE_DATA_3" : (0x0004,0x0000,0x00FF,0x0042,),
          "SENSE_DATA_4" : (0x0001,0x0000,0x00FF,0x005D,),
          "SENSE_DATA_5" : (0x0000,0x0000,0x0000,0x0000,),
          "SENSE_DATA_6" : (0x0000,0x0000,0x0000,0x0000,),
          "SENSE_DATA_7" : (0x0000,0x0000,0x0000,0x0000,),
          "SENSE_DATA_8" : (0x0000,0x0000,0x0000,0x0000,),
          "SRVO_LOOP_CODE" : (0x0000,),
          "TEST_FUNCTION" : (0x0000,),
      }

prm_503_LogPage_2 = {
   'test_num' : 503,
   'prm_name' : 'prm_503_LogPage_2',
   'timeout' : 1200,
   'spc_id' : 1,
   "BGMS_FAILURES" : (0x0000,),
   "PAGE_CODE" : (0x0002,),
   "PARAMETER_CODE_1" : (0xFFFF,),
   "PARAMETER_CODE_1_LSW" : (0xFFFF,),
   "PARAMETER_CODE_1_MSW" : (0xFFFF,),
   "PARAMETER_CODE_2" : (0xFFFF,),
   "PARAMETER_CODE_2_LSW" : (0xFFFF,),
   "PARAMETER_CODE_2_MSW" : (0xFFFF,),
   "ROBUST_LOGGING" : (0xFFFF,),
   "SAVE_PARAMETERS" : (0x0000,),
   "TEST_FUNCTION" : (0x0000,),
   "TEST_OPERATING_MODE" : (0x0001,),
   }

prm_503_LogPage_3 = {
   'test_num' : 503,
   'prm_name' : 'prm_503_LogPage_3',
   'timeout' : 1200,
   'spc_id' : 2,
   "BGMS_FAILURES" : (0x0000,),
   "PAGE_CODE" : (0x0003,),
   "PARAMETER_CODE_1" : (0xFFFF,),
   "PARAMETER_CODE_1_LSW" : (0xFFFF,),
   "PARAMETER_CODE_1_MSW" : (0xFFFF,),
   "PARAMETER_CODE_2" : (0xFFFF,),
   "PARAMETER_CODE_2_LSW" : (0xFFFF,),
   "PARAMETER_CODE_2_MSW" : (0xFFFF,),
   "ROBUST_LOGGING" : (0xFFFF,),
   "SAVE_PARAMETERS" : (0x0000,),
   "TEST_FUNCTION" : (0x0000,),
   "TEST_OPERATING_MODE" : (0x0001,),
   }

prm_503_LogPage_6 = {
   'test_num' : 503,
   'prm_name' : 'prm_503_LogPage_6',
   'timeout' : 1200,
   'spc_id' : 3,
   "BGMS_FAILURES" : (0x0000,),
   "PAGE_CODE" : (0x0006,),
   "PARAMETER_CODE_1" : (0xFFFF,),
   "PARAMETER_CODE_1_LSW" : (0xFFFF,),
   "PARAMETER_CODE_1_MSW" : (0xFFFF,),
   "PARAMETER_CODE_2" : (0xFFFF,),
   "PARAMETER_CODE_2_LSW" : (0xFFFF,),
   "PARAMETER_CODE_2_MSW" : (0xFFFF,),
   "ROBUST_LOGGING" : (0xFFFF,),
   "SAVE_PARAMETERS" : (0x0000,),
   "TEST_FUNCTION" : (0x0000,),
   "TEST_OPERATING_MODE" : (0x0001,),
   }

prm_503_ClrLogPg3A = {
   'test_num' : 503,
   'prm_name' : 'prm_503_ClrLogPg3A',
   'timeout' : 1200,
   "BGMS_FAILURES" : (0x0000,),
   "PAGE_CODE" : (0x003A,),
   "PARAMETER_CODE_1" : (0xFFFF,),
   "PARAMETER_CODE_1_LSW" : (0xFFFF,),
   "PARAMETER_CODE_1_MSW" : (0xFFFF,),
   "PARAMETER_CODE_2" : (0xFFFF,),
   "PARAMETER_CODE_2_LSW" : (0xFFFF,),
   "PARAMETER_CODE_2_MSW" : (0xFFFF,),
   "ROBUST_LOGGING" : (0xFFFF,),
   "SAVE_PARAMETERS" : (0x0001,),
   "TEST_FUNCTION" : (0x0000,),
   "TEST_OPERATING_MODE" : (0x0001,),
   }

prm_503_ClrLogPg6 = {
   'test_num' : 503,
   'prm_name' : 'prm_503_ClrLogPg6',
   'timeout' : 1200,
   "BGMS_FAILURES" : (0x0000,),
   "PAGE_CODE" : (0x0006,),
   "PARAMETER_CODE_1" : (0xFFFF,),
   "PARAMETER_CODE_1_LSW" : (0xFFFF,),
   "PARAMETER_CODE_1_MSW" : (0xFFFF,),
   "PARAMETER_CODE_2" : (0xFFFF,),
   "PARAMETER_CODE_2_LSW" : (0xFFFF,),
   "PARAMETER_CODE_2_MSW" : (0xFFFF,),
   "ROBUST_LOGGING" : (0xFFFF,),
   "SAVE_PARAMETERS" : (0x0001,),
   "TEST_FUNCTION" : (0x0000,),
   "TEST_OPERATING_MODE" : (0x0001,),
   }

prm_503_ClrLogPgs = {
   'test_num' : 503,
   'prm_name' : 'prm_503_ClrLogPgs',
   'timeout' : 1200,
   "BGMS_FAILURES" : (0x0000,),
   "PAGE_CODE" : (0x0000,),
   "PARAMETER_CODE_1" : (0xFFFF,),
   "PARAMETER_CODE_1_LSW" : (0xFFFF,),
   "PARAMETER_CODE_1_MSW" : (0xFFFF,),
   "PARAMETER_CODE_2" : (0xFFFF,),
   "PARAMETER_CODE_2_LSW" : (0xFFFF,),
   "PARAMETER_CODE_2_MSW" : (0xFFFF,),
   "ROBUST_LOGGING" : (0x0000,),
   "SAVE_PARAMETERS" : (0x0000,),
   "TEST_FUNCTION" : (0x0000,),
   "TEST_OPERATING_MODE" : (0x0002,),
   }

prm_503_LogPage_3E = {
   'test_num' : 503,
   'prm_name' : 'prm_503_LogPage_3E',
   'timeout' : 1200,
   'spc_id' : 4,
   "BGMS_FAILURES" : (0x0000,),
   "PAGE_CODE" : (0x003E,),
   "PARAMETER_CODE_1" : (0xFFFF,),
   "PARAMETER_CODE_1_LSW" : (0xFFFF,),
   "PARAMETER_CODE_1_MSW" : (0xFFFF,),
   "PARAMETER_CODE_2" : (0xFFFF,),
   "PARAMETER_CODE_2_LSW" : (0xFFFF,),
   "PARAMETER_CODE_2_MSW" : (0xFFFF,),
   "ROBUST_LOGGING" : (0xFFFF,),
   "SAVE_PARAMETERS" : (0x0000,),
   "TEST_FUNCTION" : (0x0000,),
   "TEST_OPERATING_MODE" : (0x0001,),
   }

prm_503_LogPage_3E_Spec1 = {
   'test_num' : 503,
   'prm_name' : 'prm_503_LogPage_3E_Spec1',
   'timeout' : 1200,
   'spc_id' : 6,
   "BGMS_FAILURES" : (0x0000,),
   "PAGE_CODE" : (0x003E,),
   "PARAMETER_CODE_1" : (0x8001,),
   "PARAMETER_CODE_1_LSW" : (0x0000,),
   "PARAMETER_CODE_1_MSW" : (0x0000,),
   "PARAMETER_CODE_2" : (0x8011,),
   "PARAMETER_CODE_2_LSW" : (0x0000,),
   "PARAMETER_CODE_2_MSW" : (0x0000,),
   "ROBUST_LOGGING" : (0xFFFF,),
   "SAVE_PARAMETERS" : (0x0000,),
   "TEST_FUNCTION" : (0x0000,),
   "TEST_OPERATING_MODE" : (0x0000,),
   }

prm_503_LogPage_2_Spec2 = {
   'test_num' : 503,
   'prm_name' : 'prm_503_LogPage_2_Spec2',
   'timeout' : 1200,
   'spc_id' : 7,
   "BGMS_FAILURES" : (0x0000,),
   "PAGE_CODE" : (0x003E,),
   "PARAMETER_CODE_1" : (0x8101,),
   "PARAMETER_CODE_1_LSW" : (0x0000,),
   "PARAMETER_CODE_1_MSW" : (0x0000,),
   "PARAMETER_CODE_2" : (0x8111,),
   "PARAMETER_CODE_2_LSW" : (0x0000,),
   "PARAMETER_CODE_2_MSW" : (0x0000,),
   "ROBUST_LOGGING" : (0xFFFF,),
   "SAVE_PARAMETERS" : (0x0000,),
   "TEST_FUNCTION" : (0x0000,),
   "TEST_OPERATING_MODE" : (0x0000,),
   }

DriveModelNumberInquiry = {
   'test_num': 638,
   'prm_name': 'DriveModelNumberInquiry',
   'ATTRIBUTE_MODE': (0,),
   'SCSI_COMMAND': (1,),
   'TEST_FUNCTION': (0,),
   'PARAMETER_8': (0,),
   'PARAMETER_3': (255,),
   'PARAMETER_2': (65280,),
   'PARAMETER_1': (49920,),
   'PARAMETER_0': (4609,),
   'PARAMETER_7': (0,),
   'PARAMETER_6': (0,),
   'PARAMETER_5': (0,),
   'PARAMETER_4': (65280,),
   'WRITE_SECTOR_CMD_ALL_HDS': (0,),
   'REPORT_OPTION': (1,),
   'BYPASS_WAIT_UNIT_RDY': (0,),
   'timeout': 600,
   'LONG_COMMAND': (0,)
   }

prm_538_ChangeDefCMD = {
   'test_num' : 538,
   'prm_name' : 'Change Definition 0x40 CMD',
   'timeout' : 300,
   "CHK_OPEN_LATCH_RETRY_CNT" : (0x0000,),
   "COMMAND_WORD_1" : (0x4000,),
   "COMMAND_WORD_2" : (0x0000,),
   "COMMAND_WORD_3" : (0x0000,),
   "COMMAND_WORD_4" : (0x0000,),
   "COMMAND_WORD_5" : (0x0000,),
   "COMMAND_WORD_6" : (0x0000,),
   "READ_CAPACITY" : (0x0000,),
   "SECTOR_SIZE" : (0x0000,),
   "SELECT_COPY" : (0x0000,),
   "SUPRESS_RESULTS" : (0x0000,),
   "TEST_FUNCTION" : (0x0000,),
   "TRANSFER_LENGTH" : (0x0000,),
   "TRANSFER_OPTION" : (0x0000,),
   "USE_CMD_ATTR_TST_PARMS" : (0x0000,),
   "WRITE_SECTOR_CMD_ALL_HDS" : (0x0000,),
   }

prm_518_Disable_PrescanBGMS = {
   'test_num' : 518,
   'prm_name' : 'prm_518_Disable_PrescanBGMS',
   'timeout' : 1800,
   "DATA_TO_CHANGE" : (0x0000,),
   "MODE_COMMAND" : (0x0001,),
   "MODE_SELECT_ALL_INITS" : (0x0000,),
   "MODE_SENSE_INITIATOR" : (0x0000,),
   "MODE_SENSE_OPTION" : (0x0000,),
   "MODIFICATION_MODE" : (0x0000,),
   "PAGE_BYTE_AND_DATA34" : (0x0004,0x0000,0x0005,0x0000,0x0006,0x00FF,0x0007,0x00FF,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,),
   "PAGE_CODE" : (0x001C,),
   "PAGE_FORMAT" : (0x0001,),
   "SAVE_MODE_PARAMETERS" : (0x0000,),
   "SUB_PAGE_CODE" : (0x0001,),
   "TEST_FUNCTION" : (0x0000,),
   "UNIT_READY" : (0x0000,),
   "VERIFY_MODE" : (0x0000,),
   }

prm_538_StandardInquiry = {
   'test_num' : 538,
   'prm_name' : 'prm_538_StandardInquiry',
   'timeout' : 1800,
   "COMMAND_WORD_1" : (0x1200,),
   "COMMAND_WORD_2" : (0x0000,),
   "COMMAND_WORD_3" : (0xFF00,),
   "COMMAND_WORD_4" : (0x0000,),
   }


try:
   from pgm_SAS_ICmd_Params import *
except ImportError:
   pass #possibly not defined
