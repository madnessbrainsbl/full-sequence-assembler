#
#-----------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                     #
#-----------------------------------------------------------------------------------------#
# $RCSfile:$
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $Revision: #1 $
# $Date: 2016/05/05 $ 10/13/2008
# $Author: chiliang.woo $ Randy Taylor
# $Source:$
# Level:


prm_504_SenseAndDriveData = {
# oProc.St({'test_num':504,'prm_name':'Sense and drive data'},0x8000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=1200,spc_id=1) # Display Sense, Last Cmd, Cyl, Hd, Sec, LBA
	'test_num':504,
	'prm_name':'Sense and drive data',
	'timeout':1200,
	'spc_id':1,
	'TEST_FUNCTION' : (0x8000,),
	'NUMBER_REGISTER_BANKS' : (0x0000,),
	'CONTROLLER_CHIP_REG' : (0x0000,),
	'TRANSLATE_LOGICAL_BLOCK' : (0x0000,),
}

prm_506_CmdTimeout = {
# oProc.St({'test_num':506,'prm_name':'Timeout 180s'},0x0000,0x00b4,0x0000,0x0000,0x0100,0x0000,0x0000,0x00b4,0x0000,0x0000,timeout=600) # Extra timeout for larger Cache size drives for Send/Receive Diagnostics
	'test_num':506,
	'prm_name':'Command Timeout 180s',
	'timeout':600,
	'FORMAT_CMD_TIME_MSB' : (0x0000,),
	'FACTORY_CMD_TIMEOUT_SECS' : (0x00B4,),
	'COMMAND_TIMEOUT_MS' : (0x0000,),
	'TEST_FUNCTION' : (0x0000,),
	'TEST_EXE_TIME_SECONDS' : (0x0000,),
	'RESPONSE_TIME_MS' : (0x0000,),
	'WAIT_READY_TIME' : (0x0100,),
	'FORMAT_CMD_TIME_LSB' : (0x0000,),
	'COMMAND_TIMEOUT_SECONDS' : (0x00B4,),
}

prm_507_D_Sense = {
	'test_num':507,
	'prm_name':'prm_507_D_Sense',
   'timeout':600,
   'DESCRPTIVE_SENSE_OPTION' : (0x0001,),
   'BYPASS_FAILURE' : 0x3,
}

prm_508_WRT_pattern_to_WBuff = {
	'test_num':508,
	'prm_name':'Write 00 pattern to Write Buffer 200h',
	'timeout':600,
	'PARAMETER_1' :  (0x0000,),  # Write pattern to write buffer
	'PARAMETER_2' :  (0x0000,),
	'PARAMETER_3' :  (0x0200,),  # number of bytes
	'PARAMETER_4' :  (0xFF80,),  # fixed pattern
	'PARAMETER_5' :  (0x0000,),  # upper word pattern
	'PARAMETER_6' :  (0x0000,),  # lower word pattern
	'PARAMETER_7' :  (0x0000,),
	'PARAMETER_8' :  (0x0000,),
	'PARAMETER_9' :  (0x0000,),
	'PARAMETER_10' : (0x0000,),
}

prm_508_WRT_pattern_to_RBuff = {
	'test_num':508,
	'prm_name':'Write 00 pattern to Read Buffer 200h',
	'timeout':600,
	'PARAMETER_1' :  (0x0001,),  # Write pattern to read buffer
	'PARAMETER_2' :  (0x0000,),
	'PARAMETER_3' :  (0x0200,),  # number of bytes
	'PARAMETER_4' :  (0xFF80,),  # fixed pattern
	'PARAMETER_5' :  (0x0000,),  # upper word pattern
	'PARAMETER_6' :  (0x0000,),  # lower word pattern
	'PARAMETER_7' :  (0x0000,),
	'PARAMETER_8' :  (0x0000,),
	'PARAMETER_9' :  (0x0000,),
	'PARAMETER_10' : (0x0000,),
}

prm_508_WRT_bytes_to_WBuff = {
	'test_num':508,
	'prm_name':'Write 8 bytes of 00 to Write buffer, offset 0',
	'timeout':600,
       	'PARAMETER_1' :  (0x0002,),  # Write parameters to write buffer
       	'PARAMETER_2' :  (0x0000,),  # offset
       	'PARAMETER_3' :  (0x0008,),  # number of bytes
       	'PARAMETER_4' :  (0x0000,),
       	'PARAMETER_5' :  (0x0000,),
       	'PARAMETER_6' :  (0x0000,),
       	'PARAMETER_7' :  (0x0000,),  # (byte0,byte1)
       	'PARAMETER_8' :  (0x0000,),  # (byte2,byte3)
       	'PARAMETER_9' :  (0x0000,),  # (byte4,byte5)
      	'PARAMETER_10' : (0x0000,),  # (byte6,byte7)
}

prm_508_WRT_bytes_to_RBuff = {
	'test_num':508,
	'prm_name':'Write 8 bytes of 00 to Read buffer, offset 0',
	'timeout':600,
       	'PARAMETER_1' :  (0x0003,),  # Write parameters to read buffer
       	'PARAMETER_2' :  (0x0000,),  # offset
       	'PARAMETER_3' :  (0x0008,),  # number of bytes
       	'PARAMETER_4' :  (0x0000,),
       	'PARAMETER_5' :  (0x0000,),
       	'PARAMETER_6' :  (0x0000,),
       	'PARAMETER_7' :  (0x0000,),  # (byte0,byte1)
       	'PARAMETER_8' :  (0x0000,),  # (byte2,byte3)
       	'PARAMETER_9' :  (0x0000,),  # (byte4,byte5)
      	'PARAMETER_10' : (0x0000,),  # (byte6,byte7)
}

prm_508_Disp_WBuff = {
	'test_num':508,
	'prm_name':'Display Write Buffer 200h, offset 0',
	'timeout':600,
      	'PARAMETER_1' :  (0x0004,),  # Display Write Buffer
      	'PARAMETER_2' :  (0x0000,),  # offset
      	'PARAMETER_3' :  (0x0200,),  # number of bytes
      	'PARAMETER_4' :  (0x0000,),
      	'PARAMETER_5' :  (0x0000,),
      	'PARAMETER_6' :  (0x0000,),
      	'PARAMETER_7' :  (0x0000,),
      	'PARAMETER_8' :  (0x0000,),
      	'PARAMETER_9' :  (0x0000,),
      	'PARAMETER_10' : (0x0000,),
}

prm_508_Disp_RBuff = {
	'test_num':508,
	'prm_name':'Display Read Buffer 200h, offset 0',
	'timeout':600,
      	'PARAMETER_1' :  (0x8005,),  # Display Read Buffer with DriveVar ability
      	'PARAMETER_2' :  (0x0000,),  # offset
      	'PARAMETER_3' :  (0x0200,),  # number of bytes
      	'PARAMETER_4' :  (0x0000,),
      	'PARAMETER_5' :  (0x0000,),
      	'PARAMETER_6' :  (0x0000,),
      	'PARAMETER_7' :  (0x0000,),
      	'PARAMETER_8' :  (0x0000,),
      	'PARAMETER_9' :  (0x0000,),
      	'PARAMETER_10' : (0x0000,),
}

prm_508_Copy_RBuff_to_WBuff = {
	'test_num':508,
	'prm_name':'Copy Read to Write Buffer 200h',
	'timeout':600,
      	'PARAMETER_1' :  (0x0006,),  # Copy Read to Write Buffer
      	'PARAMETER_2' :  (0x0000,),  # offset
      	'PARAMETER_3' :  (0x0200,),  # number of bytes
      	'PARAMETER_4' :  (0x0000,),
      	'PARAMETER_5' :  (0x0000,),
      	'PARAMETER_6' :  (0x0000,),
      	'PARAMETER_7' :  (0x0000,),
      	'PARAMETER_8' :  (0x0000,),
      	'PARAMETER_9' :  (0x0000,),
      	'PARAMETER_10' : (0x0000,),
}

prm_508_Copy_WBuff_to_RBuff = {
	'test_num':508,
	'prm_name':'Copy Write to Read Buffer 200h',
	'timeout':600,
      	'PARAMETER_1' :  (0x0007,),  # Copy Write to Read Buffer
      	'PARAMETER_2' :  (0x0000,),  # offset
      	'PARAMETER_3' :  (0x0200,),  # number of bytes
      	'PARAMETER_4' :  (0x0000,),
      	'PARAMETER_5' :  (0x0000,),
      	'PARAMETER_6' :  (0x0000,),
      	'PARAMETER_7' :  (0x0000,),
      	'PARAMETER_8' :  (0x0000,),
      	'PARAMETER_9' :  (0x0000,),
      	'PARAMETER_10' : (0x0000,),
}

prm_508_CompareW2RBuffer = {
	'test_num':508,
	'prm_name':'Compare Write to Read Buffer 200h',
	'timeout':600,
	'PARAMETER_1' :  (0x0008,),  # Compare write and read buffers
	'PARAMETER_2' :  (0x0000,),
	'PARAMETER_3' :  (0x0200,),  # number of bytes
	'PARAMETER_4' :  (0x0000,),
	'PARAMETER_5' :  (0x0000,),
	'PARAMETER_6' :  (0x0000,),
	'PARAMETER_7' :  (0x0000,),
	'PARAMETER_8' :  (0x0000,),
	'PARAMETER_9' :  (0x0000,),
	'PARAMETER_10' : (0x0000,),
}

prm_508_Byte_RangeCheck = {
# oProc.St({'test_num':508,'prm_name':'Verify UDS PowerCycle Count'},0x0009,0x0008,0x0002,0x0000,0x0000,0x0000,0x0000,0x0002,0x0000,0x0000,timeout=600) # Verify value of 2 or less for bytes 8,9 (USD Power Cycle Count)
	'test_num':508,
	'prm_name':'Byte Value In-Range Check',
	'timeout':600,
	'PARAMETER_1' :  (0x0009,),  # Check range of 16 bit read buffer value
	'PARAMETER_2' :  (0x0000,),  # offset
	'PARAMETER_3' :  (0x0000,),
	'PARAMETER_4' :  (0x0000,),  # Bits 0-7 = Upper 8 bits of offset from start of buffer
	'PARAMETER_5' :  (0x0000,),
	'PARAMETER_6' :  (0x0000,),
	'PARAMETER_7' :  (0x0000,),  # Lower limit of range
	'PARAMETER_8' :  (0x0000,),  # Upper limit of range
	'PARAMETER_9' :  (0x0000,),  # Lower limit of 2nd range to check, if not set to zero
	'PARAMETER_10' : (0x0000,),  # Upper limit of 2nd range to check, if not set to zero
}

prm_510_Write1KLbas = {
# oProc.St({'test_num':510,'prm_name':'Write 1K LBAs'},0x0020,0xA080,0x0000,0x0000,0x03e8,0x0000,0x03e8,0x0000,0x0000,0x0000) # Write first 1000 LBAs with 00 per T&A spec
	'test_num':510,
	'prm_name':'Write 1K LBAs',
	'ERROR_REPORTING_MODE' : (0x0000,),
	'CACHE_MODE' : (0x0000,),
	'PATTERN_MODE' : (0x0080,),
	'END_LBA' : (0x0000,0x0000,),
	'CHK_NONREC_ERR_PER_HD' : (0x0000,),
	'RECOVERED_ERR_LIMS' : (0x0000,),
	'TEST_FUNCTION' : (0x0000,),
	'START_LBA' : (0x0000,0x0000,),
	'START_LBA34' : (0x0000,0x0000,0x0000,0x0000,),
	'TOTAL_LBA_TO_XFER' : (0x0000,0x0000,0x0000,0x03E8,),
	'END_LBA34' : (0x0000,0x0000,0x0000,0x0000,),
	'FAIL_ERROR_CODES_SCSIERR' : (0x0000,),
	'TOTAL_BLKS_TO_TRANS_LSW' : (0x03E8,),
	'OPTIONS' : (0x0000,),
	'OPTIONS_WORD2' : (0x0000,),
	'OPTIONS_WORD1' : (0x0000,),
	'EXTENDED_LIMITS' : (0x0000,),
	'DISCONNECT_MODE' : (0x0000,),
	'EXECUTE_HIDDEN_RETRY' : (0x0000,),
	'DISABLE_FREE_RETRY' : (0x0000,),
	'ENBL_LOG10_BER_SPEC' : (0x0000,),
	'LOG10_BER_SPEC' : (0x0000,),
	'WRITE_READ_MODE' : (0x0002,),
	'ECC_CONTROL' : (0x0000,),
	'BUTTERFLY_ACCESS' : (0x0000,),
	'LBA_LSW' : (0x0000,),
	'TOTAL_BLKS_TO_TRANS_MSW' : (0x0000,),
	'BLOCKS_TO_TRANS' : (0x0000,0x03E8,),
	'FILL_WRITE_BUFFER' : (0x0000,),
	'SAVE_READ_ERR_TO_MEDIA' : (0x0001,),
	'MAX_REC_ERRORS' : (0x0000,),
	'REPORT_HIDDEN_RETRY' : (0x0000,),
	'PATTERN_LSW' : (0x0000,),
	'DISABLE_ECC_ON_FLY' : (0x0000,),
	'MAX_UNRECOVERABLE_ERR' : (0x0000,),
	'CRESCENDO_ACCESS' : (0x0000,),
	'TRANSFER_MODE' : (0x0000,),
	'PATTERN_MSW' : (0x0000,),
	'WRITE_AND_VERIFY' : (0x0000,),
	'LBA_MSW' : (0x0000,),
	'ACCESS_MODE' : (0x0000,),
	'PATTERN_LENGTH_IN_BITS' : (0x0020,),
}

prm_510_WriteFirst2048LbasWith00 = {
# oProc.St({'test_num':510,'prm_name':'Write first 2048 LBAs with 00'},0x0020,0xA080,0x0000,0x0000,0x0800,0x0000,0x0800,0x0000,0x0000,0x0000) #Write first 2048 LBAs with 00, to some UNIX label area.  Allows for test rerun.
	'test_num':510,
	'prm_name':'Write first 2048 LBAs with 00',
	'ERROR_REPORTING_MODE' : (0x0000,),
	'CACHE_MODE' : (0x0000,),
	'PATTERN_MODE' : (0x0080,),
	'END_LBA' : (0x0000,0x0000,),
	'CHK_NONREC_ERR_PER_HD' : (0x0000,),
	'RECOVERED_ERR_LIMS' : (0x0000,),
	'TEST_FUNCTION' : (0x0000,),
	'START_LBA' : (0x0000,0x0000,),
	'START_LBA34' : (0x0000,0x0000,0x0000,0x0000,),
	'TOTAL_LBA_TO_XFER' : (0x0000,0x0000,0x0000,0x0800,),
	'END_LBA34' : (0x0000,0x0000,0x0000,0x0000,),
	'FAIL_ERROR_CODES_SCSIERR' : (0x0000,),
	'TOTAL_BLKS_TO_TRANS_LSW' : (0x0800,),
	'OPTIONS' : (0x0000,),
	'OPTIONS_WORD2' : (0x0000,),
	'OPTIONS_WORD1' : (0x0000,),
	'EXTENDED_LIMITS' : (0x0000,),
	'DISCONNECT_MODE' : (0x0000,),
	'EXECUTE_HIDDEN_RETRY' : (0x0000,),
	'DISABLE_FREE_RETRY' : (0x0000,),
	'ENBL_LOG10_BER_SPEC' : (0x0000,),
	'LOG10_BER_SPEC' : (0x0000,),
	'WRITE_READ_MODE' : (0x0002,),
	'ECC_CONTROL' : (0x0000,),
	'BUTTERFLY_ACCESS' : (0x0000,),
	'LBA_LSW' : (0x0000,),
	'TOTAL_BLKS_TO_TRANS_MSW' : (0x0000,),
	'BLOCKS_TO_TRANS' : (0x0000,0x0800,),
	'FILL_WRITE_BUFFER' : (0x0000,),
	'SAVE_READ_ERR_TO_MEDIA' : (0x0001,),
	'MAX_REC_ERRORS' : (0x0000,),
	'REPORT_HIDDEN_RETRY' : (0x0000,),
	'PATTERN_LSW' : (0x0000,),
	'DISABLE_ECC_ON_FLY' : (0x0000,),
	'MAX_UNRECOVERABLE_ERR' : (0x0000,),
	'CRESCENDO_ACCESS' : (0x0000,),
	'TRANSFER_MODE' : (0x0000,),
	'PATTERN_MSW' : (0x0000,),
	'WRITE_AND_VERIFY' : (0x0000,),
	'LBA_MSW' : (0x0000,),
	'ACCESS_MODE' : (0x0000,),
	'PATTERN_LENGTH_IN_BITS' : (0x0020,),
}

prm_510_RandomRead = {
	'test_num':510,
	'prm_name':'Random Read - 16 BLK XFer',
	'timeout':36000,
	"ERROR_REPORTING_MODE" : (0x0000,),
	"CACHE_MODE" : (0x0001,),
	"PATTERN_MODE" : (0x0001,),
	"END_LBA" : (0x0000,0x0000,),
	"CHK_NONREC_ERR_PER_HD" : (0x0000,),
	"RECOVERED_ERR_LIMS" : (0x0003,),
	"TEST_FUNCTION" : (0x0000,),
	"START_LBA" : (0x0000,0x0000,),
	"START_LBA34" : (0x0000,0x0000,0x0000,0x0000,),
	"TOTAL_LBA_TO_XFER" : (0x0000,0x0000,0x0000,0x0000,),
	"END_LBA34" : (0x0000,0x0000,0x0000,0x0000,),
	"FAIL_ERROR_CODES_SCSIERR" : (0x0000,),
	"TOTAL_BLKS_TO_TRANS_LSW" : (0x0000,),
	"OPTIONS" : (0x0000,),
	"OPTIONS_WORD2" : (0x0000,),
	"OPTIONS_WORD1" : (0x0002,),  # enable IOPs
	"EXTENDED_LIMITS" : (0x0000,),
	"DISCONNECT_MODE" : (0x0000,),
	"EXECUTE_HIDDEN_RETRY" : (0x0000,),
	"DISABLE_FREE_RETRY" : (0x0000,),
	"ENBL_LOG10_BER_SPEC" : (0x0000,),
	"LOG10_BER_SPEC" : (0x0000,),
	"WRITE_READ_MODE" : (0x0001,),  # Read
	"ECC_CONTROL" : (0x0000,),
	"BUTTERFLY_ACCESS" : (0x0000,),
	"LBA_LSW" : (0x0000,),
	"TOTAL_BLKS_TO_TRANS_MSW" : (0x0000,),
	"NUMBER_LBA_PER_XFER" : (0x0000,0x0010,),  # 16 block per command
	"FILL_WRITE_BUFFER" : (0x0001,),
	"SAVE_READ_ERR_TO_MEDIA" : (0x0001,),
	"MAX_REC_ERRORS" : (0x0003,),
	"MAX_RCV_ERRS" : (0x0000,0x0003,),
	"REPORT_HIDDEN_RETRY" : (0x0000,),
	"PATTERN_LSW" : (0x3039,),
	"DISABLE_ECC_ON_FLY" : (0x0000,),
	"MAX_UNRECOVERABLE_ERR" : (0x0000,),
	"CRESCENDO_ACCESS" : (0x0000,),
	"TRANSFER_MODE" : (0x0000,),
	"PATTERN_MSW" : (0x00C8,),
	"WRITE_AND_VERIFY" : (0x0000,),
	"LBA_MSW" : (0x0000,),
	"ACCESS_MODE" : (0x0001,),
	"PATTERN_LENGTH_IN_BITS" : (0x0000,),
}

prm_514_FwServoInfo = {
# oProc.St({'test_num':514,'prm_name':'FW Servo info'},0x8000,0x0001,0x00C0,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=600) # FW, Servo Ram, Servo Rom Revs
	'test_num':514,
	'prm_name':'FW Servo info',
	'timeout':600,
	'CHECK_MODE_NUMBER' : (0x0000,),
	'ENABLE_VPD' : (0x0001,),
	'TEST_FUNCTION' : (0x0000,),
	'GET_FW_REV_FROM_NETWORK' : (0x0000,),
	'EXPECTED_FW_REV_4' : (0x0000,),
	'EXPECTED_FW_REV_1' : (0x0000,),
	'EXPECTED_FW_REV_2' : (0x0000,),
	'EXPECTED_FW_REV_3' : (0x0000,),
	'PAGE_CODE' : (0x00C0,),
}

prm_514_StdInquiryData = {
	'test_num':514,
	'prm_name':'Std Inquiry Data',
	'timeout':600,
	'CHECK_MODE_NUMBER' : (0x0000,),
	'ENABLE_VPD' : (0x0000,),
	'TEST_FUNCTION' : (0x0000,),
	'GET_FW_REV_FROM_NETWORK' : (0x0000,),
	'EXPECTED_FW_REV_4' : (0x0000,),
	'EXPECTED_FW_REV_1' : (0x0000,),
	'EXPECTED_FW_REV_2' : (0x0000,),
	'EXPECTED_FW_REV_3' : (0x0000,),
	'PAGE_CODE' : (0x0000,),
}

prm_517_RequestSense = {
	'test_num':517,
	'prm_name':'Standard Request Sense - No SpinUp',
	'timeout':600,
	'TEST_FUNCTION' : (0x0000,),
	'ACCEPTABLE_IF_MATCH' : (0x0000,),
	'OMIT_DUP_ENTRY' : (0x0000,),
	'ACCEPTABLE_SNS_DATA' : (0x0000,),
	'CHK_SRVO_LOOP_CODE' : (0x0000,),
	'CHK_FRU_CODE' : (0x0000,),
	'RPT_REQS_CMD_CNT' : (0x0000,),
	'SRVO_LOOP_CODE' : (0x0000,),
	'SEND_TUR_CMDS_ONLY' : (0x0000,),
	'MAX_REQS_CMD_CNT' : (0x000A,),
	'RPT_SEL_SNS_DATA' : (0x0000,),
	'SENSE_DATA_1' : (0x0000,0x0000,0x0000,0x0000,),
	'SENSE_DATA_2' : (0x0000,0x0000,0x0000,0x0000,),
	'SENSE_DATA_3' : (0x0000,0x0000,0x0000,0x0000,),
	'SENSE_DATA_4' : (0x0000,0x0000,0x0000,0x0000,),
	'SENSE_DATA_5' : (0x0000,0x0000,0x0000,0x0000,),
	'SENSE_DATA_6' : (0x0000,0x0000,0x0000,0x0000,),
	'SENSE_DATA_7' : (0x0000,0x0000,0x0000,0x0000,),
	'SENSE_DATA_8' : (0x0000,0x0000,0x0000,0x0000,),
}
prm_517_RequestSense_Init_Check = {
# oProc.St({'test_num':517,'prm_name':'Request Sense 0'},0x0000,0x001A,0x0000,0x0000,0x0004,0x1CFF,0x0004,0x42FF,0x0001,0x5DFF,timeout=300)
	'test_num':517,
	'prm_name':'Request Sense with Error Check and SpinUp',
	'timeout':600,
	'TEST_FUNCTION' : (0x0000,),
	'ACCEPTABLE_IF_MATCH' : (0x0000,),
	'OMIT_DUP_ENTRY' : (0x0000,),
	'ACCEPTABLE_SNS_DATA' : (0x0000,),
	'CHK_SRVO_LOOP_CODE' : (0x0000,),
	'CHK_FRU_CODE' : (0x0000,),
	'RPT_REQS_CMD_CNT' : (0x0000,),
	'SRVO_LOOP_CODE' : (0x0000,),
	'SEND_TUR_CMDS_ONLY' : (0x0001,),
	'MAX_REQS_CMD_CNT' : (0x000A,),
	'RPT_SEL_SNS_DATA' : (0x0000,),
	'SENSE_DATA_1' : (0x0004,0x00FF,0x00FF,0x0083,),  # 04/83/FF/FF
	'SENSE_DATA_2' : (0x0004,0x00FF,0x00FF,0x001C,),  # 04/1C/FF/FF
	'SENSE_DATA_3' : (0x0004,0x00FF,0x00FF,0x0042,),  # 04/42/FF/FF
	'SENSE_DATA_4' : (0x0001,0x00FF,0x00FF,0x005D,),  # 01/5D/FF/FF
	'SENSE_DATA_5' : (0x0000,0x0000,0x0000,0x0000,),
	'SENSE_DATA_6' : (0x0000,0x0000,0x0000,0x0000,),
	'SENSE_DATA_7' : (0x0000,0x0000,0x0000,0x0000,),
	'SENSE_DATA_8' : (0x0000,0x0000,0x0000,0x0000,),
}

prm_517_RequestSense_Ready_Check = {
	'test_num':517,
	'prm_name':'Request Sense Ready Check',
	'timeout':600,
	'TEST_FUNCTION' : (0x0000,),
	'ACCEPTABLE_IF_MATCH' : (0x0000,),
	'OMIT_DUP_ENTRY' : (0x0000,),
	'ACCEPTABLE_SNS_DATA' : (0x0000,),
	'CHK_SRVO_LOOP_CODE' : (0x0000,),
	'CHK_FRU_CODE' : (0x0000,),
	'RPT_REQS_CMD_CNT' : (0x0000,),
	'SRVO_LOOP_CODE' : (0x0000,),
	'SEND_TUR_CMDS_ONLY' : (0x0000,),
	'MAX_REQS_CMD_CNT' : (0x000A,),
	'RPT_SEL_SNS_DATA' : (0x0000,),
	'SENSE_DATA_1' : (0x0002,0x00FF,0x00FF,0x0004,),  # 02/04/FF/FF
	'SENSE_DATA_2' : (0x0004,0x00FF,0x00FF,0x001C,),  # 04/1C/FF/FF
	'SENSE_DATA_3' : (0x0004,0x00FF,0x00FF,0x0042,),  # 04/42/FF/FF
	'SENSE_DATA_4' : (0x0001,0x00FF,0x00FF,0x005D,),  # 01/5D/FF/FF
	'SENSE_DATA_5' : (0x0000,0x0000,0x0000,0x0000,),
	'SENSE_DATA_6' : (0x0000,0x0000,0x0000,0x0000,),
	'SENSE_DATA_7' : (0x0000,0x0000,0x0000,0x0000,),
	'SENSE_DATA_8' : (0x0000,0x0000,0x0000,0x0000,),
}

prm_518_DisplayChangeableMps = {
	'test_num':518,
	'prm_name':'Display Changeable Mode Sense',
	'timeout':600,
	'UNIT_READY' : (0x0000,),
	'SAVE_MODE_PARAMETERS' : (0x0000,),
	'MODE_SENSE_INITIATOR' : (0x0000,),
	'TEST_FUNCTION' : (0x0000,),
	'MODIFICATION_MODE' : (0x0000,),
	'MODE_SELECT_ALL_INITS' : (0x0000,),
	'PAGE_FORMAT' : (0x0001,),
	'MODE_SENSE_OPTION' : (0x0001,),
	'PAGE_BYTE_AND_DATA34' : (0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,),
	'MODE_COMMAND' : (0x0000,),
	'VERIFY_MODE' : (0x0000,),
	'DATA_TO_CHANGE' : (0x0000,),
	'PAGE_CODE' : (0x0000,),
	'SUB_PAGE_CODE' : (0x0000,),
}

prm_518_DisplayCurrentMps = {
	'test_num':518,
	'prm_name':'Display Current Mode Sense',
	'timeout':600,
	'UNIT_READY' : (0x0000,),
	'SAVE_MODE_PARAMETERS' : (0x0000,),
	'MODE_SENSE_INITIATOR' : (0x0000,),
	'TEST_FUNCTION' : (0x0000,),
	'MODIFICATION_MODE' : (0x0000,),
	'MODE_SELECT_ALL_INITS' : (0x0000,),
	'PAGE_FORMAT' : (0x0001,),
	'MODE_SENSE_OPTION' : (0x0000,),
	'PAGE_BYTE_AND_DATA34' : (0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,),
	'MODE_COMMAND' : (0x0000,),
	'VERIFY_MODE' : (0x0000,),
	'DATA_TO_CHANGE' : (0x0000,),
	'PAGE_CODE' : (0x0000,),
	'SUB_PAGE_CODE' : (0x0000,),
}

prm_518_DisplayDefaultMps = {
	'test_num':518,
	'prm_name':'Display Default Mode Sense',
	'timeout':600,
	'UNIT_READY' : (0x0000,),
	'SAVE_MODE_PARAMETERS' : (0x0000,),
	'MODE_SENSE_INITIATOR' : (0x0000,),
	'TEST_FUNCTION' : (0x0000,),
	'MODIFICATION_MODE' : (0x0000,),
	'MODE_SELECT_ALL_INITS' : (0x0000,),
	'PAGE_FORMAT' : (0x0001,),
	'MODE_SENSE_OPTION' : (0x0002,),
	'PAGE_BYTE_AND_DATA34' : (0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,),
	'MODE_COMMAND' : (0x0000,),
	'VERIFY_MODE' : (0x0000,),
	'DATA_TO_CHANGE' : (0x0000,),
	'PAGE_CODE' : (0x0000,),
	'SUB_PAGE_CODE' : (0x0000,),
}

prm_518_DisplaySavedMps = {
	'test_num':518,
	'prm_name':'Display Saved Mode Sense',
	'timeout':300,
	'UNIT_READY' : (0x0000,),
	'SAVE_MODE_PARAMETERS' : (0x0000,),
	'MODE_SENSE_INITIATOR' : (0x0000,),
	'TEST_FUNCTION' : (0x0000,),
	'MODIFICATION_MODE' : (0x0000,),
	'MODE_SELECT_ALL_INITS' : (0x0000,),
	'PAGE_FORMAT' : (0x0001,),
	'MODE_SENSE_OPTION' : (0x0003,),
	'PAGE_BYTE_AND_DATA34' : (0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,),
	'MODE_COMMAND' : (0x0000,),
	'VERIFY_MODE' : (0x0000,),
	'DATA_TO_CHANGE' : (0x0000,),
	'PAGE_CODE' : (0x0000,),
	'SUB_PAGE_CODE' : (0x0000,),
}

prm_518_TEMPDisableSMART = {
   'test_num' : 518,
   'prm_name' : 'Temporary Disable SMART DEXCPT',
   'timeout' : 300,
	"DATA_TO_CHANGE" : (0x0001,),
	"MODE_COMMAND" : (0x0001,),
	"MODE_SELECT_ALL_INITS" : (0x0000,),
	"MODE_SENSE_INITIATOR" : (0x0000,),
	"MODE_SENSE_OPTION" : (0x0000,),
	"MODIFICATION_MODE" : (0x0000,),
	"PAGE_BYTE_AND_DATA" : (0x0231,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,),
	"PAGE_CODE" : (0x001C,),
	"PAGE_FORMAT" : (0x0000,),
	"SAVE_MODE_PARAMETERS" : (0x0000,),
	"SUB_PAGE_CODE" : (0x0000,),
	"TEST_FUNCTION" : (0x0000,),
	"UNIT_READY" : (0x0000,),
	"VERIFY_MODE" : (0x0000,),
}

prm_518_ModeSelect_Save = { # This is non-functional:  Parameters are expected to be passed to it to specify the page and bytes
	'test_num':518,
	'prm_name':'Saved Mode Select',
	'timeout':600,
	"UNIT_READY" : (0x0000,),
	"SAVE_MODE_PARAMETERS" : (0x0001,),
	"MODE_SENSE_INITIATOR" : (0x0000,),
	"TEST_FUNCTION" : (0x0000,),
	"MODIFICATION_MODE" : (0x0000,),
	"MODE_SELECT_ALL_INITS" : (0x0000,),
	"PAGE_FORMAT" : (0x0000,),
	"MODE_SENSE_OPTION" : (0x0003,),  # Saved Mode sense readback
	"PAGE_BYTE_AND_DATA34" : (0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,),
	"MODE_COMMAND" : (0x0001,),
	"VERIFY_MODE" : (0x0000,),
	"DATA_TO_CHANGE" : (0x0000,),
	"PAGE_CODE" : (0x0000,),
	"SUB_PAGE_CODE" : (0x0000,),
}

prm_524_WriteUnixLabel = {
# oProc.St({'test_num':524,'prm_name':'Write Unix Label'},0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,dlfile=(CN,self.ccvparm1),timeout = 300)  # Write Unix label
	'test_num':524,
	'prm_name':'Write Unix Label',
	'timeout':300,
	'TEST_FUNCTION' : (0x0000,),
	'WRT_RD_CUST_FILE' : (0x0000,),
	'FILE_ID' : (0x0000,),
}

prm_528_PwrCycle = {
   'test_num' : 528,
   'prm_name' : 'prm_528_PwrCycle',
   'timeout' : 600,
   'ALLOW_SPEC_STATUS_COND' : (0x0000,),
   'MAX_POWER_SPIN_DOWN_TIME' : (0x0000,),
   'MAX_POWER_SPIN_UP_TIME' : (0x001E,),
   'MIN_POWER_SPIN_DOWN_TIME' : (0x0000,),
   'MIN_POWER_SPIN_UP_TIME' : (0x0002,),
   'SENSE_DATA_1' : (0x0000,0x0000,0x0000,0x0000,),
   'SENSE_DATA_2' : (0x0000,0x0000,0x0000,0x0000,),
   'SENSE_DATA_3' : (0x0000,0x0000,0x0000,0x0000,),
   'SKP_SPINUP_AFTER_SPINDWN' : (0x0000,),
   'SPIN_DOWN_WAIT_TIME' : (0x001E,),
   'TEST_FUNCTION' : (0x0000,),
   'TEST_OPERATING_MODE' : (0x0000,),
   'UNIT_READY' : (0x0001,),
}

prm_529_CheckGrowthDefects = {
# oProc.St({'test_num':529,'prm_name':'Check growth defects'},0x0002,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=300)  # Verify 0 growth defects before starting testing
	'test_num':529,
	'prm_name':'Check for zero Growth Defects',
	'timeout':600,
	'SLIPPED_TRACKS_SPEC' : (0x0000,),
	'WEDGES_PER_TRK' : (0x0000,),
	'PAD_D_GLIST' : (0x0000,),
	'TEST_HEAD' : (0x0000,),
	'TEST_FUNCTION' : (0x0000,),
	'FAIL_ON_SLIPPED_TRK' : (0x0000,),
	'MAX_GLIST_ENTRIES' : (0x0000,0x0000,),
	'CONDITIONAL_REWRITE' : (0x0000,),
	'DISP_1_WEDGE_SERVO_FLAWS' : (0x0000,),
	'SERVO_DEFECT_FUNCTION' : (0x0000,),
	'WEDGE_NUM' : (0x0000,),
	'PAD_CYLS' : (0x0000,),
	'GLIST_OPTION' : (0x0002,),
	'GRADING_OUTPUT' : (0x0000,),
	'SLIPPED_TRACKS_HEAD_NUM' : (0x0000,),
	'PAD_500_BYTES_UNITS' : (0x0000,),
	'MAX_SERVO_DEFECTS' : (0x0000,),
	'SERVO_GAP_BYTE_COUNT' : (0x0000,),
}

prm_529_CheckServoDefects = {
# oProc.St({'test_num':529,'prm_name':'Check servo defects'},0x0004,0x0000,0x0002,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=300)  # Verify 0 servo defects before starting testing
	'test_num':529,
	'prm_name':'Check for zero Servo Defects',
	'timeout':600,
	'SLIPPED_TRACKS_SPEC' : (0x0000,),
	'WEDGES_PER_TRK' : (0x0000,),
	'PAD_D_GLIST' : (0x0000,),
	'TEST_HEAD' : (0x0000,),
	'TEST_FUNCTION' : (0x0000,),
	'FAIL_ON_SLIPPED_TRK' : (0x0000,),
	'MAX_GLIST_ENTRIES' : (0x0000,0x0000,),
	'CONDITIONAL_REWRITE' : (0x0000,),
	'DISP_1_WEDGE_SERVO_FLAWS' : (0x0000,),
	'SERVO_DEFECT_FUNCTION' : (0x0002,),
	'WEDGE_NUM' : (0x0000,),
	'PAD_CYLS' : (0x0000,),
	'GLIST_OPTION' : (0x0004,),
	'GRADING_OUTPUT' : (0x0000,),
	'SLIPPED_TRACKS_HEAD_NUM' : (0x0000,),
	'PAD_500_BYTES_UNITS' : (0x0000,),
	'MAX_SERVO_DEFECTS' : (0x0000,),
	'SERVO_GAP_BYTE_COUNT' : (0x0000,),
}

prm_530_Check_PList_size = {
	'test_num':530,
	'prm_name':'Check p-list size (sector mode) - Max 500,000',
	'timeout':3600,
	"SET_TO_FAIL" : (0x0001,),
	"MAX_DEFECTIVE_SECTORS" : (0xC350,),
	"MAX_DEFECTIVE_SECS_CYL" : (0xFFFF,),
	"TEST_OPERATING_MODE" : (0x0003,),
	"TEST_FUNCTION" : (0x0000,),
	"MIN_ENTRIES_IN_DST" : (0x0000,),
	"MAX_DEFECTIVE_SECS_HEAD" : (0xFFFF,),
	"DEFECT_LIST_FORMAT" : (0x0005,),
	"MIN_PERCENT_ENTRIES" : (0x0000,),
	"MAX_CYL_DISPLAYED" : (0x0000,),
	"MULTIPLY_BY_10" : (0x0001,),
	"MAX_DEFECTIVE_SECS_ZONE" : (0xFFFF,),
	"MAX_PERCENT_DEFECTIVE" : (0x0000,),
}

prm_535_DrivevarInitiatorRev = {
# oProc.St({'test_num':535,'prm_name':'DriveVar Initiator Rev'},0x8002,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=1200) # Get Initiator Code Rev with store as DriveVars['Initiator Code']
	'test_num':535,
	'prm_name':'DriveVar Initiator Rev',
	'timeout':600,
	'REG_ADDR' : (0x0000,),
	'REG_VALUE' : (0x0000,),
	'TEST_OPERATING_MODE' : (0x0002,),
	'TEST_FUNCTION' : (0x0800,),
	'BAUD_RATE' : (0x0000,),
	'EXPECTED_FW_REV_1' : (0x0000,),
	'DRIVE_TYPE' : (0x0000,),
}

prm_537_Set_SAV_To_DEF = {
	'test_num':537,
	'prm_name':'Set Saved Modes Sense to Default',
	'timeout':600,
	"MODE_PAGES_BYPASSED_1" : (0x0000,),
	"TEST_FUNCTION" : (0x0000,),
	"MODE_COMMAND" : (0x0000,),
	"MODE_PAGES_BYPASSED_2" : (0x0000,),
	"MODE_PAGES_BYPASSED_3" : (0x0000,),
}

prm_538_VPD_pageDC = {
#       oProc.St({'test_num':538},0x8002,0x1201,0xDC01,0x2200,0x0000,0x0000,0x0000,0x0160,0x0122,0x0000) #Read Inquiry VPD page DC
	'test_num':538,
	'prm_name':'Read Inquiry VPD page DC',
	'timeout':600,
      	'TEST_FUNCTION' : (0x8000,),
      	'SELECT_COPY' : (0x0000,),
      	'READ_CAPACITY' : (0x0000,),
      	'CHK_OPEN_LATCH_RETRY_CNT' : (0x0000,),
      	'SUPRESS_RESULTS' : (0x0000,),
      	'USE_CMD_ATTR_TST_PARMS' : (0x0001,),
      	'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
      	'COMMAND_WORD_1' : (0x1201,),
      	'COMMAND_WORD_2' : (0xDC01,),
      	'COMMAND_WORD_3' : (0x2200,),
      	'COMMAND_WORD_4' : (0x0000,),
      	'COMMAND_WORD_5' : (0x0000,),
      	'COMMAND_WORD_6' : (0x0000,),
      	'SECTOR_SIZE' : (0x0000,),
      	'TRANSFER_OPTION' : (0x0160,),
      	'TRANSFER_LENGTH' : (0x0122,),
}

prm_538_BgmsReadDef1CSubp1ModeSense = {
# oProc.St({'test_num':538,'prm_name':'BGMS Read Def 1C subP1 Mode Sense'},0x0002,0x5A00,0x9C01,0x0000,0x00FF,0xFF00,0x0000,0x01A0,0x0030,0x0000,timeout=600) #Read Default Page 1C, subpage 1 Mode Sense
	'test_num':538,
	'prm_name':'BGMS Read Def 1C subP1 Mode Sense',
	'timeout':600,
	'TEST_FUNCTION' : (0x0000,),
	'SELECT_COPY' : (0x0000,),
	'READ_CAPACITY' : (0x0000,),
	'CHK_OPEN_LATCH_RETRY_CNT' : (0x0000,),
	'SUPRESS_RESULTS' : (0x0000,),
	'USE_CMD_ATTR_TST_PARMS' : (0x0001,),
	'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
	'COMMAND_WORD_1' : (0x5A00,),
	'COMMAND_WORD_2' : (0x9C01,),
	'COMMAND_WORD_3' : (0x0000,),
	'COMMAND_WORD_4' : (0x00FF,),
	'COMMAND_WORD_5' : (0xFF00,),
	'COMMAND_WORD_6' : (0x0000,),
	'SECTOR_SIZE' : (0x0000,),
	'TRANSFER_OPTION' : (0x01A0,),
	'TRANSFER_LENGTH' : (0x0030,),
}

prm_538_BgmsReadSaved1CSubp1ModeSense = {
# oProc.St({'test_num':538,'prm_name':'BGMS Read Saved 1C subP1 Mode Sense'},0x0002,0x5A00,0xDC01,0x0000,0x00FF,0xFF00,0x0000,0x01A0,0x0030,0x0000,timeout=600) #Read Saved Page 1C, subpage 1 Mode Sense
	'test_num':538,
	'prm_name':'BGMS Read Saved 1C subP1 Mode Sense',
	'timeout':600,
	'TEST_FUNCTION' : (0x0000,),
	'SELECT_COPY' : (0x0000,),
	'READ_CAPACITY' : (0x0000,),
	'CHK_OPEN_LATCH_RETRY_CNT' : (0x0000,),
	'SUPRESS_RESULTS' : (0x0000,),
	'USE_CMD_ATTR_TST_PARMS' : (0x0001,),
	'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
	'COMMAND_WORD_1' : (0x5A00,),
	'COMMAND_WORD_2' : (0xDC01,),
	'COMMAND_WORD_3' : (0x0000,),
	'COMMAND_WORD_4' : (0x00FF,),
	'COMMAND_WORD_5' : (0xFF00,),
	'COMMAND_WORD_6' : (0x0000,),
	'SECTOR_SIZE' : (0x0000,),
	'TRANSFER_OPTION' : (0x01A0,),
	'TRANSFER_LENGTH' : (0x0030,),
}

prm_538_ClearLogging = {
# oProc.St({'test_num':538,'prm_name':'Clear logging'},0x0000,0x4C03,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=300)  # Clear logging
	'test_num':538,
	'prm_name':'Clear logging',
	'timeout':600,
	'TEST_FUNCTION' : (0x0000,),
	'SELECT_COPY' : (0x0000,),
	'READ_CAPACITY' : (0x0000,),
	'CHK_OPEN_LATCH_RETRY_CNT' : (0x0000,),
	'SUPRESS_RESULTS' : (0x0000,),
	'USE_CMD_ATTR_TST_PARMS' : (0x0000,),
	'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
	'COMMAND_WORD_1' : (0x4C03,),
	'COMMAND_WORD_2' : (0x0000,),
	'COMMAND_WORD_3' : (0x0000,),
	'COMMAND_WORD_4' : (0x0000,),
	'COMMAND_WORD_5' : (0x0000,),
	'COMMAND_WORD_6' : (0x0000,),
	'SECTOR_SIZE' : (0x0000,),
	'TRANSFER_OPTION' : (0x0000,),
	'TRANSFER_LENGTH' : (0x0000,),
}

prm_538_GetLogPage = {
# oProc.St({'test_num':538,'prm_name':'Page 0 of Logging'},0x0004,0x4D01,0x0000,0x0000,0x00FF,0xFF00,0x0000,0x0000,0x0000,0x0000,timeout=300)  # Get page 0 Logging Data
	'test_num':538,
	'prm_name':'Get Log Page 0x00',
	'timeout':600,
	'TEST_FUNCTION' : (0x0000,),
	'SELECT_COPY' : (0x0000,),
	'READ_CAPACITY' : (0x0000,),
	'CHK_OPEN_LATCH_RETRY_CNT' : (0x0000,),
	'SUPRESS_RESULTS' : (0x0001,),
	'USE_CMD_ATTR_TST_PARMS' : (0x0000,),
	'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
	'COMMAND_WORD_1' : (0x4D01,),
	'COMMAND_WORD_2' : (0x0000,),
	'COMMAND_WORD_3' : (0x0000,),
	'COMMAND_WORD_4' : (0x00FF,),
	'COMMAND_WORD_5' : (0xFF00,),
	'COMMAND_WORD_6' : (0x0000,),
	'SECTOR_SIZE' : (0x0000,),
	'TRANSFER_OPTION' : (0x0000,),
	'TRANSFER_LENGTH' : (0x0000,),
}

prm_538_ChangeDef = {
# oProc.St({'test_num':538,'prm_name':'Issue Change Def command'},0x0000,param1,param2,param3,param4,param5,0x0000,0x0000,0x0000,0x0000,timeout=600) # Issue Change Def. command
	'test_num':538,
	'prm_name':'Change Definition',
	'timeout':600,
	'TEST_FUNCTION' : (0x0000,),
	'SELECT_COPY' : (0x0000,),
	'READ_CAPACITY' : (0x0000,),
	'CHK_OPEN_LATCH_RETRY_CNT' : (0x0000,),
	'SUPRESS_RESULTS' : (0x0000,),
	'USE_CMD_ATTR_TST_PARMS' : (0x0000,),
	'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
	'COMMAND_WORD_1' : (0x4000,),
	'COMMAND_WORD_2' : (0x0000,),
	'COMMAND_WORD_3' : (0x0000,),
	'COMMAND_WORD_4' : (0x1296,),
	'COMMAND_WORD_5' : (0x0000,),
	'COMMAND_WORD_6' : (0x0000,),
	'SECTOR_SIZE' : (0x0000,),
	'TRANSFER_OPTION' : (0x0000,),
	'TRANSFER_LENGTH' : (0x0000,),
}

prm_538_ReadSerialNumPage = {
# oProc.St({'test_num':538,'prm_name':'Read SerialNum Page'},0x8002,0x1201,0x8000,0x3000,0x0000,0x0000,0x0000,0x0160,0x0030,0x0000) # Read Drive S/N page
	'test_num':538,
	'prm_name':'Read Inquiry Vital Product Page 80',
	'TEST_FUNCTION' : (0x8000,),
	'SELECT_COPY' : (0x0000,),
	'READ_CAPACITY' : (0x0000,),
	'CHK_OPEN_LATCH_RETRY_CNT' : (0x0000,),
	'SUPRESS_RESULTS' : (0x0000,),
	'USE_CMD_ATTR_TST_PARMS' : (0x0001,),
	'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
	'COMMAND_WORD_1' : (0x1201,),
	'COMMAND_WORD_2' : (0x8000,),
	'COMMAND_WORD_3' : (0x3000,),
	'COMMAND_WORD_4' : (0x0000,),
	'COMMAND_WORD_5' : (0x0000,),
	'COMMAND_WORD_6' : (0x0000,),
	'SECTOR_SIZE' : (0x0000,),
	'TRANSFER_OPTION' : (0x0160,),
	'TRANSFER_LENGTH' : (0x0030,),
}

prm_538_SpinDown = {
# oProc.St({'test_num':538,'prm_name':'Spin Down'},0x0000,0x1B00,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=600) # Spin Down
	'test_num':538,
	'prm_name':'Spin Down',
	'timeout':600,
	'TEST_FUNCTION' : (0x0000,),
	'SELECT_COPY' : (0x0000,),
	'READ_CAPACITY' : (0x0000,),
	'CHK_OPEN_LATCH_RETRY_CNT' : (0x0000,),
	'SUPRESS_RESULTS' : (0x0000,),
	'USE_CMD_ATTR_TST_PARMS' : (0x0000,),
	'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
	'COMMAND_WORD_1' : (0x1B00,),
	'COMMAND_WORD_2' : (0x0000,),
	'COMMAND_WORD_3' : (0x0000,),
	'COMMAND_WORD_4' : (0x0000,),
	'COMMAND_WORD_5' : (0x0000,),
	'COMMAND_WORD_6' : (0x0000,),
	'SECTOR_SIZE' : (0x0000,),
	'TRANSFER_OPTION' : (0x0000,),
	'TRANSFER_LENGTH' : (0x0000,),
}

prm_538_SpinUp = {
# oProc.St({'test_num':538,'prm_name':'Spin Up'},0x0000,0x1B00,0x0000,0x0100,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=600) # Spin Up
	'test_num':538,
	'prm_name':'Spin Up',
	'timeout':600,
	'TEST_FUNCTION' : (0x0000,),
	'SELECT_COPY' : (0x0000,),
	'READ_CAPACITY' : (0x0000,),
	'CHK_OPEN_LATCH_RETRY_CNT' : (0x0000,),
	'SUPRESS_RESULTS' : (0x0000,),
	'USE_CMD_ATTR_TST_PARMS' : (0x0000,),
	'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
	'COMMAND_WORD_1' : (0x1B00,),
	'COMMAND_WORD_2' : (0x0000,),
	'COMMAND_WORD_3' : (0x0100,),
	'COMMAND_WORD_4' : (0x0000,),
	'COMMAND_WORD_5' : (0x0000,),
	'COMMAND_WORD_6' : (0x0000,),
	'SECTOR_SIZE' : (0x0000,),
	'TRANSFER_OPTION' : (0x0000,),
	'TRANSFER_LENGTH' : (0x0000,),
}

prm_538_SendDiagnostic = {
	'test_num':538,
	'prm_name':'Send Diagnostic',
	'timeout':600,
	'TEST_FUNCTION' : (0x8000,),
	'SELECT_COPY' : (0x0000,),
	'READ_CAPACITY' : (0x0000,),
	'CHK_OPEN_LATCH_RETRY_CNT' : (0x0000,),
	'SUPRESS_RESULTS' : (0x0000,),
	'USE_CMD_ATTR_TST_PARMS' : (0x0000,),
	'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
	'COMMAND_WORD_1'  : (0x1D04,),
	'COMMAND_WORD_2'  : (0x0000,),
	'COMMAND_WORD_3'  : (0x0000,),
	'COMMAND_WORD_4'  : (0x0000,),
	'COMMAND_WORD_5'  : (0x0000,),
	'COMMAND_WORD_6'  : (0x0000,),
	'SECTOR_SIZE'     : (0x0000,),
	'TRANSFER_OPTION' : (0x0000,),
	'TRANSFER_LENGTH' : (0x0000,),
}

prm_538_ReceiveDiagnostic = {
	'test_num':538,
	'prm_name':'Receive Diagnostic',
	'timeout':600,
	'TEST_FUNCTION' : (0x8000,),
	'SELECT_COPY' : (0x0000,),
	'READ_CAPACITY' : (0x0000,),
	'CHK_OPEN_LATCH_RETRY_CNT' : (0x0000,),
	'SUPRESS_RESULTS' : (0x0001,),
	'USE_CMD_ATTR_TST_PARMS' : (0x0000,),
	'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
	'COMMAND_WORD_1'  : (0x1C00,),
	'COMMAND_WORD_2'  : (0x00ff,),
	'COMMAND_WORD_3'  : (0xff00,),
	'COMMAND_WORD_4'  : (0x0000,),
	'COMMAND_WORD_5'  : (0x0000,),
	'COMMAND_WORD_6'  : (0x0000,),
	'SECTOR_SIZE'     : (0x0000,),
	'TRANSFER_OPTION' : (0x0000,),
	'TRANSFER_LENGTH' : (0x0000,),
}

prm_538_ReadCapacity = {
	'test_num':538,
	'prm_name':'Read Capacity',
	'timeout':600,
	'TEST_FUNCTION' : (0x8000,),
	'SELECT_COPY' : (0x0000,),
	'READ_CAPACITY' : (0x0000,),
	'CHK_OPEN_LATCH_RETRY_CNT' : (0x0000,),
	'SUPRESS_RESULTS' : (0x0000,),
	'USE_CMD_ATTR_TST_PARMS' : (0x0000,),
	'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
	'COMMAND_WORD_1'  : (0x2500,),
	'COMMAND_WORD_2'  : (0x0000,),
	'COMMAND_WORD_3'  : (0x0000,),
	'COMMAND_WORD_4'  : (0x0000,),
	'COMMAND_WORD_5'  : (0x0000,),
	'COMMAND_WORD_6'  : (0x0000,),
	'SECTOR_SIZE'     : (0x0000,),
	'TRANSFER_OPTION' : (0x0000,),
	'TRANSFER_LENGTH' : (0x0000,),
}

prm_538_RequestSense = {
	'test_num':538,
	'prm_name':'RequestSense',
	'timeout':600,
	'TEST_FUNCTION' : (0x8000,),
	'SELECT_COPY' : (0x0000,),
	'READ_CAPACITY' : (0x0000,),
	'CHK_OPEN_LATCH_RETRY_CNT' : (0x0000,),
	'SUPRESS_RESULTS' : (0x0001,),
	'USE_CMD_ATTR_TST_PARMS' : (0x0000,),
	'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
	'COMMAND_WORD_1'  : (0x0300,),
	'COMMAND_WORD_2'  : (0x0000,),
	'COMMAND_WORD_3'  : (0xff00,),
	'COMMAND_WORD_4'  : (0x0000,),
	'COMMAND_WORD_5'  : (0x0000,),
	'COMMAND_WORD_6'  : (0x0000,),
	'SECTOR_SIZE'     : (0x0000,),
	'TRANSFER_OPTION' : (0x0001,),
	'TRANSFER_LENGTH' : (0x0000,),
}

prm_538_Rezero = {
	'test_num':538,
	'prm_name':'Rezero',
	'timeout':600,
	'TEST_FUNCTION' : (0x8000,),
	'SELECT_COPY' : (0x0000,),
	'READ_CAPACITY' : (0x0000,),
	'CHK_OPEN_LATCH_RETRY_CNT' : (0x0000,),
	'SUPRESS_RESULTS' : (0x0001,),
	'USE_CMD_ATTR_TST_PARMS' : (0x0000,),
	'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
	'COMMAND_WORD_1'  : (0x0100,),
	'COMMAND_WORD_2'  : (0x0000,),
	'COMMAND_WORD_3'  : (0x0000,),
	'COMMAND_WORD_4'  : (0x0000,),
	'COMMAND_WORD_5'  : (0x0000,),
	'COMMAND_WORD_6'  : (0x0000,),
	'SECTOR_SIZE'     : (0x0000,),
	'TRANSFER_OPTION' : (0x0000,),
	'TRANSFER_LENGTH' : (0x0000,),
}

prm_538_ReadLBA = {
	'test_num':538,
	'prm_name':'Read LBA',
	'timeout':600,
	'TEST_FUNCTION' : (0x8000,),
	'SELECT_COPY' : (0x0000,),
	'READ_CAPACITY' : (0x0000,),
	'CHK_OPEN_LATCH_RETRY_CNT' : (0x0000,),
	'SUPRESS_RESULTS' : (0x0000,),
	'USE_CMD_ATTR_TST_PARMS' : (0x0000,),
	'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
	'COMMAND_WORD_1'  : (0x8800,),
	'COMMAND_WORD_2'  : (0x0000,),
	'COMMAND_WORD_3'  : (0x0000,),
	'COMMAND_WORD_4'  : (0x0000,),
	'COMMAND_WORD_5'  : (0x0000,),
	'COMMAND_WORD_6'  : (0x0000,),
	'COMMAND_WORD_7'  : (0x0000,),
	'COMMAND_WORD_8'  : (0x0000,),
	'SECTOR_SIZE'     : (0x0000,),
	'TRANSFER_OPTION' : (0x0000,),
	'TRANSFER_LENGTH' : (0x0000,),
}

prm_544_ResetForEqsFile = {
# oProc.St({'test_num':544,'prm_name':'Reset for EQS file'},0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,dlfile=(CN,self.eqspecfile),timeout = 300)  # Reset always required to use primary EQS file first
	'test_num':544,
	'prm_name':'Reset for primary EQS file',
	'timeout':300,
	'TEST_FUNCTION' : (0x0000,),
	'FORMAT_OPTIONS_VARIABLE' : (0x0000,),
	'TEST_OPERATING_MODE' : (0x0000,),
	'OPTIONS' : (0x0000,),
	'SUBTEST_SPECIFIC_1' : (0x0000,),  # Reset to use primary equip_spec file option
	'SUBTEST_SPECIFIC_2' : (0x0000,),
	'SUBTEST_SPECIFIC_3' : (0x0000,),
	'SN_BYTES_0_1' : (0x0000,),
	'SN_BYTES_2_3' : (0x0000,),
	'SN_BYTES_4_5' : (0x0000,),
	'SN_BYTES_6_7' : (0x0000,),
}

prm_544_RndmRead512Lbas = {
# oProc.St({'test_num':544,'prm_name':'Rndm Read 512 LBAs'},0x0000,0x0001,0x0000,0x0200,0x0001,0x0000,0x0000,0x0000,0x0000,0x0000,dlfile=(CN,self.eqspecfile),timeout = 300)  # 512 single LBA Random Read only
	'test_num':544,
	'prm_name':'512 Single block Random Read',
	'timeout':300,
	'TEST_FUNCTION' : (0x0000,),
	'FORMAT_OPTIONS_VARIABLE' : (0x0000,),
	'TEST_OPERATING_MODE' : (0x0001,),  # Random Write/Read option
	'OPTIONS' : (0x0000,),
	'SUBTEST_SPECIFIC_1' : (0x0200,),  # Number of Write/Reads
	'SUBTEST_SPECIFIC_2' : (0x0001,),  # Bit 0 = 1: Disable Write (Read only)
	'SUBTEST_SPECIFIC_3' : (0x0000,),
	'SN_BYTES_0_1' : (0x0000,),
	'SN_BYTES_2_3' : (0x0000,),
	'SN_BYTES_4_5' : (0x0000,),
	'SN_BYTES_6_7' : (0x0000,),
}

prm_544_ResetRecovery = {
# oProc.St({'test_num':544,'prm_name':'Reset Recovery'},0x0000,0x0002,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,dlfile=(CN,self.eqspecfile),timeout = 600)  # Check for 06/29 after Reset Test
	'test_num':544,
	'prm_name':'Reset Recovery',
	'timeout':600,
	'TEST_FUNCTION' : (0x0000,),
	'FORMAT_OPTIONS_VARIABLE' : (0x0000,),
	'TEST_OPERATING_MODE' : (0x0002,),  # Reset Recovery option
	'OPTIONS' : (0x0000,),
	'SUBTEST_SPECIFIC_1' : (0x0000,),
	'SUBTEST_SPECIFIC_2' : (0x0000,),
	'SUBTEST_SPECIFIC_3' : (0x0000,),
	'SN_BYTES_0_1' : (0x0000,),
	'SN_BYTES_2_3' : (0x0000,),
	'SN_BYTES_4_5' : (0x0000,),
	'SN_BYTES_6_7' : (0x0000,),
}

prm_544_StdInquiryCheck = {
# oProc.St({'test_num':544,'prm_name':'Std Inquiry Check'},0x0000,0x0003,0x0000,0x0410,0x0000,0x2000,0x0000,0x0000,0x0000,0x0000,dlfile=(CN,self.eqspecfile),timeout = 300)  # Std. Inquiry check with rev field masked
	'test_num':544,
	'prm_name':'Std Inquiry Check mask bytes 20-23h',
	'timeout':300,
	'TEST_FUNCTION' : (0x0000,),
	'FORMAT_OPTIONS_VARIABLE' : (0x0000,),
	'TEST_OPERATING_MODE' : (0x0003,),  # Inquiry Compare option
	'OPTIONS' : (0x0000,),
	'SUBTEST_SPECIFIC_1' : (0x0410,),  # Byte 1: Number of byte(s) to mask
                                           # Byte 0:  Bit 4 = 1: Indicate mask is valid  Bit 0 = 1: Enable Vital Product Page
	'SUBTEST_SPECIFIC_2' : (0x0000,),  # Byte 0: Vital Product Page (i.e. 00h, 80h,...)
	'SUBTEST_SPECIFIC_3' : (0x2000,),  # Byte 1: Byte offset into data field
                                           # Byte 0: Byte Mask - Set required bits to one, Clear all 'don't care' bits to zero.
	'SN_BYTES_0_1' : (0x0000,),
	'SN_BYTES_2_3' : (0x0000,),
	'SN_BYTES_4_5' : (0x0000,),
	'SN_BYTES_6_7' : (0x0000,),
}

prm_544_SavedModeSenseCheck = {
# oProc.St({'test_num':544,'prm_name':'Saved ModeSense Check'},0x0000,0x0004,0x0000,0x0003,0x003F,0x0000,0x0000,0x0000,0x0000,0x0000,dlfile=(CN,self.eqspecfile),timeout = 300)  # Saved Mode sense check
	'test_num':544,
	'prm_name':'Saved ModeSense Check',
	'timeout':300,
	'TEST_FUNCTION' : (0x0000,),
	'FORMAT_OPTIONS_VARIABLE' : (0x0000,),
	'TEST_OPERATING_MODE' : (0x0004,),  # Mode Sense Compare option
	'OPTIONS' : (0x0000,),
	'SUBTEST_SPECIFIC_1' : (0x0003,),  # Byte 0: Mode Page 0=Current, 1=Changeable, 2=Default, 3=Saved
	'SUBTEST_SPECIFIC_2' : (0x003F,),  # Byte 0: Page Code (only 0x3F, all supported presently)
	'SUBTEST_SPECIFIC_3' : (0x0000,),  # Mask bytes
	'SN_BYTES_0_1' : (0x0000,),
	'SN_BYTES_2_3' : (0x0000,),
	'SN_BYTES_4_5' : (0x0000,),
	'SN_BYTES_6_7' : (0x0000,),
}

prm_544_VerifyReadCapacity = {
# oProc.St({'test_num':544,'prm_name':'Verify Read Capacity'},0x0000,0x0005,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,dlfile=(CN,self.eqspecfile),timeout = 300)  # Read Capacity
	'test_num':544,
	'prm_name':'Verify Read Capacity',
	'timeout':300,
	'TEST_FUNCTION' : (0x0000,),
	'FORMAT_OPTIONS_VARIABLE' : (0x0000,),
	'TEST_OPERATING_MODE' : (0x0005,),  # Read Capacity option
	'OPTIONS' : (0x0000,),
	'SUBTEST_SPECIFIC_1' : (0x0000,),
	'SUBTEST_SPECIFIC_2' : (0x0000,),
	'SUBTEST_SPECIFIC_3' : (0x0000,),
	'SN_BYTES_0_1' : (0x0000,),
	'SN_BYTES_2_3' : (0x0000,),
	'SN_BYTES_4_5' : (0x0000,),
	'SN_BYTES_6_7' : (0x0000,),
}

prm_544_SendReceiveDiagnostics = {
# oProc.St({'test_num':544,'prm_name':'Send Receive Diagnostics'},0x0000,0x0007,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,dlfile=(CN,self.eqspecfile),timeout=600) # Send/Receive Diagnostics
	'test_num':544,
	'prm_name':'Send - Receive Diagnostics',
	'timeout':600,
	'TEST_FUNCTION' : (0x0000,),
	'FORMAT_OPTIONS_VARIABLE' : (0x0000,),
	'TEST_OPERATING_MODE' : (0x0007,),  # Send/Receive Diagnostics option
	'OPTIONS' : (0x0000,),
	'SUBTEST_SPECIFIC_2' : (0x0000,),
	'SUBTEST_SPECIFIC_3' : (0x0000,),
	'SUBTEST_SPECIFIC_1' : (0x0000,),
	'SN_BYTES_0_1' : (0x0000,),
	'SN_BYTES_2_3' : (0x0000,),
	'SN_BYTES_4_5' : (0x0000,),
	'SN_BYTES_6_7' : (0x0000,),
}

prm_544_VerifyLBA = {
# oProc.St({'test_num':544,'prm_name':'Verify LBA 0'},0x0000,0x0008,0x0000,0x0000,0x0000,0x0002,0x0000,0x0000,0x0000,0x0000,dlfile=(CN,self.eqspecfile),timeout = 300) # Verify LBA 0 is 00 data
	'test_num':544,
	'prm_name':'Verify LBA 0 to Block 1 data',
	'timeout':300,
	'TEST_FUNCTION' : (0x0000,),
	'FORMAT_OPTIONS_VARIABLE' : (0x0000,),
	'TEST_OPERATING_MODE' : (0x0008,),  # Compare LBA Contents option
	'OPTIONS' : (0x0000,),  # Compare
	'SUBTEST_SPECIFIC_1' : (0x0000,),  # LBA (MSW)
	'SUBTEST_SPECIFIC_2' : (0x0000,),  # LBA (LSW)
	'SUBTEST_SPECIFIC_3' : (0x0001,),  # Byte 0: LBA block to compare against or update against (1 - 10)
	'SN_BYTES_0_1' : (0x0000,),
	'SN_BYTES_2_3' : (0x0000,),
	'SN_BYTES_4_5' : (0x0000,),
	'SN_BYTES_6_7' : (0x0000,),
}

prm_552_SSCITest = {
	'test_num':552,
	'prm_name':'prm_552_SSCITest',
	'timeout':300,
	'TEST_FUNCTION' : (0x0000,),
	'PARAMETER_10' : (0x0000,),
	'PARAMETER_9' : (0x0000,),
	'PARAMETER_8' : (0x0000,),
	'PARAMETER_3' : (0x0000,),
	'PARAMETER_2' : (0x0000,),
	'PARAMETER_1' : (0x0000,),
	'PARAMETER_7' : (0x0000,),
	'PARAMETER_6' : (0x0000,),
	'PARAMETER_5' : (0x0000,),
	'PARAMETER_4' : (0x0000,),
}

prm_555_WrtCapValue = {
   'test_num':555,
   'prm_name':'prm_555_WrtCapValue',
   'timeout':60,
   'dlfile' : 'CAP',
   'TEST_FUNCTION' :           (0x0000,),
   'TEST_OPERATING_MODE' :     (0x0002,),  # Can set bit 8 to print the before&after CAP file
   'WRITE_XFR_LENGTH' :        (0x0004,),  # Define number of bytes to write up to 6
   'MODIFY_APM_BYTE_NUM' :     (0x00D4,),  # Define start location of bytes to change
   'PARAMETER_0' :             (0x3131,),
   'PARAMETER_1' :             (0x3939,),
   'PARAMETER_2' :             (0x0000,),
}

prm_564_DispCumulativeSmart = {
# oProc.St({'test_num':564,'prm_name':'Disp Cumulative SMART'},0x00FF,0xFF1E,0xFFFF,0xFFFF,0xFFFF,0xFFFF,0xFFFF,0xFFFF,0x30FF,0xFFFF,timeout=600,spc_id=6) # Display Cumulative SMART Values
	'test_num':564,
	'prm_name':'Disp Cumulative SMART',
	'timeout':600,
	'spc_id':6,
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
	'SEEK_ERR_LIMIT' : (0x0030,),
	'SELECTED_HEAD' : (0x0000,),
	'NO_TIMING_MARK_DET' : (0xFFFF,),
	'ONE_THIRD_SEEK' : (0x00FF,),
	'SRVO_UNSF_SPEC' : (0x00FF,),
	'EXTREME_HEADS' : (0x0000,),
}

prm_575_AuthenticateToMakerSymK = {
# oProc.St({'test_num':575,'prm_name':'authenticate to maker sym k'},0x0001,0x0000,0x0001,0x0000,0x0000,0x0009,0x0000,0x0004,0x0000,0x0000, timeout=30) # authenticate to maker sym k
	'test_num':575,
	'prm_name':'authenticate to maker sym k',
	'timeout':300,
	'TEST_MODE' : (0x0001,),
	'UIDMSWU' : (0x0000,),
	'DRIVE_STATE' : (0x0000,),
	'PASSWORD_TYPE' : (0x000D,),
	'UIDLSWL' : (0x0004,),
	'REPORTING_MODE' : (0x0000,),
	'UIDLSWU' : (0x0000,),
	'WHICH_SP' : (0x0000,),
	'UIDMSWL' : (0x0009,),
}

prm_575_AuthenticateToMSID = {
	'test_num':575,
	'prm_name':'authenticate to MSID',
	'timeout':300,
	'TEST_MODE' : (0x0001,),
	'UIDMSWU' : (0x0000,),
	'DRIVE_STATE' : (0x0000,),
	'PASSWORD_TYPE' : (0x0002,),
	'UIDLSWL' : (0x8402,),
	'REPORTING_MODE' : (0x0000,),
	'UIDLSWU' : (0x0000,),
	'WHICH_SP' : (0x0000,),
	'UIDMSWL' : (0x0009,),
}

prm_575_AuthenticateToSID = {
	'test_num':575,
	'prm_name':'authenticate to SID',
	'timeout':300,
	'TEST_MODE' : (0x0001,),
	'UIDMSWU' : (0x0000,),
	'DRIVE_STATE' : (0x0000,),
	'PASSWORD_TYPE' : (0x0002,),
	'UIDLSWL' : (0x0006,),
	'REPORTING_MODE' : (0x0000,),
	'UIDLSWU' : (0x0000,),
	'WHICH_SP' : (0x0000,),
	'UIDMSWL' : (0x0009,),
}

prm_575_FDE_GetPSIDfromFIS = {
   'test_num' : 575,
   'prm_name' : 'prm_575_FDE_GetPSIDfromFIS',
   "TEST_MODE"  : (0x24,),
   "REPORTING_MODE"  : (0x0000,),
}

prm_575_FDE_AuthPSID = {
   'test_num' : 575,
   'prm_name' : 'prm_575_FDE_AuthPSID',
   "CERT_KEYTYPE" : (0x0000,),
   "CERT_TSTMODE" : (0x0002,),
   "DRIVE_STATE" : (0x0000,),
   "PASSWORD_TYPE"  : (0x0009,),
   "REPORTING_MODE" : (0x0000,),
   "TEST_MODE" : (0x0001,),
   "UIDLSWL" : (0xFF01,),
   "UIDLSWU" : (0x0001,),
   "UIDMSWL" : (0x0009,),
   "UIDMSWU" : (0x0000,),
   "WHICH_SP" : (0x0000,),
}

prm_575_CloseSession = {
# oProc.St({'test_num':575,'prm_name':'close session'},0x0003,0x0000,0x0000,0x0000,0x0000,0x0205,0x0000,0x0001,0x0000,0x0000, timeout=30) # close session
	'test_num':575,
	'prm_name':'close session',
	'timeout':300,
	'TEST_MODE' : (0x0003,),
	'UIDMSWU' : (0x0000,),
	'DRIVE_STATE' : (0x0000,),
	'PASSWORD_TYPE' : (0x0000,),
	'UIDLSWL' : (0x0001,),
	'REPORTING_MODE' : (0x0000,),
	'UIDLSWU' : (0x0000,),
	'WHICH_SP' : (0x0000,),
	'UIDMSWL' : (0x0205,),
}

prm_575_Discovery = {
# oProc.St({'test_num':575,'prm_name':'Discovery'},0x8007,0x0000,0x0000,0x0019,0x0000,0x0205,0x0000,0x0001,0x0000,0x0000, timeout=30)  # Discovery
	'test_num':575,
	'prm_name':'Discovery',
	'timeout':300,
	'TEST_MODE' : (0x0007,),
	'UIDMSWU' : (0x0000,),
	'DRIVE_STATE' : (0x0000,),
	'PASSWORD_TYPE' : (0x0000,),
	'UIDLSWL' : (0x0001,),
	'REPORTING_MODE' : (0x0000,),
	'UIDLSWU' : (0x0000,),
	'WHICH_SP' : (0x0000,),
	'UIDMSWL' : (0x0205,),
}

prm_575_GetDiagUnlockTable = {
# oProc.St({'test_num':575,'prm_name':'Get Diag unlock table'},0x0005,0x0000,0x0000,0x0000,0x0001,0x0002,0x0001,0x0001,0x0000,0x0000, timeout=30) # Get Diag unlock table
	'test_num':575,
	'prm_name':'Get Diag unlock table',
	'timeout':300,
	'TEST_MODE' : (0x0005,),
	'UIDMSWU' : (0x0001,),
	'DRIVE_STATE' : (0x0000,),
	'PASSWORD_TYPE' : (0x0000,),
	'UIDLSWL' : (0x0001,),
	'REPORTING_MODE' : (0x0000,),
	'UIDLSWU' : (0x0001,),
	'WHICH_SP' : (0x0000,),
	'UIDMSWL' : (0x0002,),
}

prm_575_GetFWUnlockTable = {
# oProc.St({'test_num':575,'prm_name':'Get FW unlock table'},0x8005,0x0000,0x0000,0x0000,0x0001,0x0002,0x0001,0x0002,0x0000,0x0000, timeout=30)
	'test_num':575,
	'prm_name':'Get FW unlock table',
	'timeout':300,
	'TEST_MODE' : (0x0005,),
	'UIDMSWU' : (0x0001,),
	'DRIVE_STATE' : (0x0000,),
	'PASSWORD_TYPE' : (0x0000,),
	'UIDLSWL' : (0x0002,),
	'REPORTING_MODE' : (0x0000,),
	'UIDLSWU' : (0x0001,),
	'WHICH_SP' : (0x0000,),
	'UIDMSWL' : (0x0002,),
}

prm_575_GetMsidFromDrive = {
# oProc.St({'test_num':575,'prm_name':'Get MSID from Drive'},0x0011,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000, timeout=30) # Get MSID from Drive
	'test_num':575,
	'prm_name':'Get MSID from Drive',
	'timeout':300,
	'TEST_MODE' : (0x0011,),
	'UIDMSWU' : (0x0000,),
	'DRIVE_STATE' : (0x0000,),
	'PASSWORD_TYPE' : (0x0000,),
	'UIDLSWL' : (0x0000,),
	'REPORTING_MODE' : (0x0000,),
	'UIDLSWU' : (0x0000,),
	'WHICH_SP' : (0x0000,),
	'UIDMSWL' : (0x0000,),
}

prm_575_GetUdsUnlockTable = {
# oProc.St({'test_num':575,'prm_name':'Get UDS unlock table'},0x0005,0x0000,0x0000,0x0000,0x0001,0x0002,0x0001,0x0003,0x0000,0x0000, timeout=30) # Get UDS unlock table
	'test_num':575,
	'prm_name':'Get UDS unlock table',
	'timeout':300,
	'TEST_MODE' : (0x0005,),
	'UIDMSWU' : (0x0001,),
	'DRIVE_STATE' : (0x0000,),
	'PASSWORD_TYPE' : (0x0000,),
	'UIDLSWL' : (0x0003,),
	'REPORTING_MODE' : (0x0000,),
	'UIDLSWU' : (0x0001,),
	'WHICH_SP' : (0x0000,),
	'UIDMSWL' : (0x0002,),
}

prm_575_StartAdminSession = {
# oProc.St({'test_num':575,'prm_name':'start admin session'},0x0002,0x0000,0x0000,0x0019,0x0000,0x0205,0x0000,0x0001,0x0000,0x0000, timeout=30) # start admin session
	'test_num':575,
	'prm_name':'start admin session',
	'timeout':300,
	'TEST_MODE' : (0x0002,),
	'UIDMSWU' : (0x0000,),
	'DRIVE_STATE' : (0x0000,),
	'PASSWORD_TYPE' : (0x0000,),
	'UIDLSWL' : (0x0001,),
	'REPORTING_MODE' : (0x0000,),
	'UIDLSWU' : (0x0000,),
	'WHICH_SP' : (0x0000,),
	'UIDMSWL' : (0x0205,),
}

prm_575_UnlockDiagPort = {
# oProc.St({'test_num':575,'prm_name':'Unlock Diag port'},0x0013,0x0000,0x0000,0x0000,0x0001,0x0002,0x0001,0x0001,0x0000,0x0000, timeout=30) # Unlock Diag port
	'test_num':575,
	'prm_name':'Unlock Diag port',
	'timeout':300,
	'TEST_MODE' : (0x0013,),
	'UIDMSWU' : (0x0001,),
	'DRIVE_STATE' : (0x0000,),
	'PASSWORD_TYPE' : (0x0000,),
	'UIDLSWL' : (0x0001,),
	'REPORTING_MODE' : (0x0000,),
	'UIDLSWU' : (0x0001,),
	'WHICH_SP' : (0x0000,),
	'UIDMSWL' : (0x0002,),
}

prm_575_UnlockUdsPort = {
# oProc.St({'test_num':575,'prm_name':'Unlock UDS port'},0x0013,0x0000,0x0000,0x0000,0x0001,0x0002,0x0001,0x0003,0x0000,0x0000, timeout=30) # Unlock UDS port
	'test_num':575,
	'prm_name':'Unlock UDS port',
	'timeout':300,
	'TEST_MODE' : (0x0013,),
	'UIDMSWU' : (0x0001,),
	'DRIVE_STATE' : (0x0000,),
	'PASSWORD_TYPE' : (0x0000,),
	'UIDLSWL' : (0x0003,),
	'REPORTING_MODE' : (0x0000,),
	'UIDLSWU' : (0x0001,),
	'WHICH_SP' : (0x0000,),
	'UIDMSWL' : (0x0002,),
}

prm_575_UnlockDLPort = {
# oProc.St({'test_num':575,'prm_name':'Unlock DL port'},0x0013,0x0000,0x0000,0x0000,0x0001,0x0002,0x0001,0x0002,0x0000,0x0000, timeout=30)
	'test_num':575,
	'prm_name':'Unlock DL port',
	'timeout':300,
	'TEST_MODE' : (0x0013,),
	'UIDMSWU' : (0x0001,),
	'DRIVE_STATE' : (0x0000,),
	'PASSWORD_TYPE' : (0x0000,),
	'UIDLSWL' : (0x0002,),
	'REPORTING_MODE' : (0x0000,),
	'UIDLSWU' : (0x0001,),
	'WHICH_SP' : (0x0000,),
	'UIDMSWL' : (0x0002,),
}

prm_575_DisableResetLock = {
# oProc.St({'test_num':575,'prm_name':'Disable Reset Lock'},0x0015,0x0000,0x0000,0x0000,0x0001,0x0002,0x0001,0x0002,0x0000,0x0000, timeout=30)
	'test_num':575,
	'prm_name':'Disable Reset Lock',
	'timeout':300,
	'TEST_MODE' : (0x0015,),
	'UIDMSWU' : (0x0001,),
	'DRIVE_STATE' : (0x0000,),
	'PASSWORD_TYPE' : (0x0000,),
	'UIDLSWL' : (0x0002,),
	'REPORTING_MODE' : (0x0000,),
	'UIDLSWU' : (0x0001,),
	'WHICH_SP' : (0x0000,),
	'UIDMSWL' : (0x0002,),
}

prm_575_SetResetLock = {
	'test_num':575,
	'prm_name':'Set Reset Lock',
	'timeout':300,
	'TEST_MODE' : (0x002C,),
	'UIDMSWU' : (0x0001,),
	'DRIVE_STATE' : (0x0000,),
	'PASSWORD_TYPE' : (0x0000,),
	'UIDLSWL' : (0x0002,),
	'REPORTING_MODE' : (0x0000,),
	'UIDLSWU' : (0x0001,),
	'WHICH_SP' : (0x0000,),
	'UIDMSWL' : (0x0002,),
}

prm_575_SetSSC1MT = {
    ## Corespec 1.0, MSID is master authority, TCG mode
   'test_num' : 575,
   'prm_name' : 'prm_575_SetSSC1MT',
   'timeout' : 30,
   "TEST_MODE"  : (0x23,),
   "MASTER_AUTHORITY" : (0x00,),
   "CORE_SPEC"  : (0x01,),
   "OPAL_SSC_SUPPORT" : (0x00,),
   "SYMK_KEY_TYPE" : (0x01,),       ##00 = legacy 3DES, 01 =  new 3DES. 02 AES256.
   "MAINTSYMK_SUPP" : (0x01,),
##   "REPORTING_MODE" : (0x0000,),
   "REPORTING_MODE" : (0x0001,),  # Turn on Global Reporting mode
}

prm_575_FDE_GetSOM = {
   'test_num' : 575,
   'prm_name' : 'prm_575_FDE_GetSOM',
	"TEST_MODE"  : (0x1B,),
	"DRIVE_STATE"  : (0x0000,),
	"REPORTING_MODE"  : (0x0001,),
	"WHICH_SP"  : (0x0000,),
}

prm_575_FDE_RevertSP = {
   'test_num' : 575,
   'prm_name' : 'prm_575_FDE_RevertSP',
	"TEST_MODE"  : (0x1E,),
	"REPORTING_MODE"  : (0x0000,),
	"WHICH_SP"  : (0x0000,),
	"PASSWORD_TYPE"  : (0x0000,),
	"DRIVE_STATE"  : (0x0000,),
	"UIDMSWU"  : (0x0000,),
	"UIDMSWL"  : (0x0205,),
	"UIDLSWU"  : (0x0000,),
	"UIDLSWL"  : (0x0001,),
	"CERT_TSTMODE" : (0x0000,),
	"CERT_KEYTYPE" : (0x0000,),
}

prm_575_CheckPort_states = {
   'test_num' : 575,
   'prm_name' : 'prm_575_CheckPort_states',
   'TEST_MODE' : (0x0037,),
   'UIDMSWU' : (0x0001,),
   'UIDMSWL' : (0x0002,),
   'UIDLSWU' : (0x0001,),
   'UIDLSWL' : (0x0001,),  # 1 - DIAG, 2 - FW, 3 - UDS
   'REPORTING_MODE' : (0x0000,),
   'PORT_LOCKED'    : (0x0001,),  # 0x0000 - port not locked - 0x0001 - port locked
   'LOCK_ON_RESET'  : (0x0001,),  # 0x0000 - lock on reset nulled - 0x0001 - lock on reset set
}

prm_575_FDE_Check_band_values = {
   'test_num' : 575,
   'prm_name' : 'prm_575_FDE_Check_band_values',
   "TEST_MODE"          : (0x0036,),
   "REPORTING_MODE"     : (0x0000,),
   "WHICH_SP"           : (0x0001,),
   "PASSWORD_TYPE"      : (0x0002,),
   "UIDMSWU"            : (0x0000,),
   "UIDMSWL"            : (0x0802,),
   "UIDLSWU"            : (0x0000,),
   "UIDLSWL"            : (0x0002,),
   "RANGE_START"        : (0x0000,),
   "RANGE_LENGTH"       : (0x0000,),
   "READ_LOCKED"        : (0x0001,),
   "WRITE_LOCKED"       : (0x0001,),
   "READ_LOCK_ENABLED"  : (0x0000,),
   "WRITE_LOCK_ENABLED" : (0x0000,),
   "LOCK_ON_RESET"      : (0x0001,),
}

prm_575_FDE_Check_band_enables = {
   'test_num' : 575,
   'prm_name' : 'prm_575_FDE_Check_band_enables',
   "TEST_MODE"          : (0x0038,),
   "REPORTING_MODE"     : (0x0000,),
   "WHICH_SP"           : (0x0001,),
   "PASSWORD_TYPE"      : (0x0002,),
   "UIDMSWU"            : (0x0000,),
   "UIDMSWL"            : (0x0802,),
   "UIDLSWU"            : (0x0000,),
   "UIDLSWL"            : (0x0002,),
   "BAND_ENABLED"       : (0x0000,),
}

prm_575_FDE_StartLockingSession = {
   'test_num' : 575,
   'prm_name' : 'prm_575_FDE_StartLockingSession',
	"DRIVE_STATE" : (0x0000,),
	"PASSWORD_TYPE" : (0x0000,),
	"REPORTING_MODE" : (0x0000,),
	"TEST_MODE" : (0x0002,),
	"UIDLSWL" : (0x0001,),
	"UIDLSWU" : (0x0001,),
	"UIDMSWL" : (0x0205,),
	"UIDMSWU" : (0x0000,),
	"WHICH_SP" : (0x0001,),
}

prm_575_FDE_CloseLockingSession = {
   'test_num' : 575,
   'prm_name' : 'prm_575_FDE_CloseLockingSession',
	"DRIVE_STATE" : (0x0000,),
	"PASSWORD_TYPE" : (0x0000,),
	"REPORTING_MODE" : (0x0000,),
	"TEST_MODE" : (0x0003,),
	"UIDLSWL" : (0x0001,),
	"UIDLSWU" : (0x0001,),
	"UIDMSWL" : (0x0205,),
	"UIDMSWU" : (0x0000,),
	"WHICH_SP" : (0x0001,),
}

prm_575_FDE_CapturePersistentData = {
   'test_num' : 575,
   'prm_name' : 'prm_575_FDE_CapturePersistentData',
   "TEST_MODE"  : (0x1D,),
   "REPORTING_MODE"  : (0x0000,),
   "WHICH_SP"  : (0x0000,),
   "PASSWORD_TYPE"  : (0x0000,),
}

prm_577_FdeSetDiag = {
# oProc.St({'test_num':577,'prm_name':'FDE Set DIAG'},0x0006,0x0001,0x0001,0x0001,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=3600)
	'test_num':577,
	'prm_name':'FDE Set DIAG',
	'timeout':3600,
	'DRIVE_STATE' : (0x0001,),
	'REPORTING_MODE' : (0x0000,),
	'TEST_MODE' : (0x0006,),
	'MSID_TYPE' : (0x0001,),
}

prm_577_FdeSetMfg = {
# oProc.St({'test_num':577,'prm_name':'FDE Set MFG'},0x0006,0x0001,0x0081,0x0001,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=3600)
	'test_num':577,
	'prm_name':'FDE Set MFG',
	'timeout':3600,
	'DRIVE_STATE' : (0x0081,),
	'REPORTING_MODE' : (0x0000,),
	'TEST_MODE' : (0x0006,),
	'MSID_TYPE' : (0x0001,),
}

prm_577_FdeSetSetup = {
# oProc.St({'test_num':577,'prm_name':'FDE Set SETUP'},0x0006,0x0001,0x0000,0x0001,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=3600)
	'test_num':577,
	'prm_name':'FDE Set SETUP',
	'timeout':3600,
	'DRIVE_STATE' : (0x0000,),
	'REPORTING_MODE' : (0x0000,),
	'TEST_MODE' : (0x0006,),
	'MSID_TYPE' : (0x0001,),
}

prm_577_SEDSetUse = {
	'test_num':577,
	'prm_name':'SED Set USE',
	'timeout':3600,
	'DRIVE_STATE' : (0x0080,),
	'REPORTING_MODE' : (0x0000,),
	'TEST_MODE' : (0x0006,),
	'MSID_TYPE' : (0x0001,),
}

prm_575_SetSOM0 = {
   'test_num' : 575,
   'prm_name' : 'prm_575_SetSOM0',
   'TEST_MODE'  : (0x1A,),
   'DRIVE_STATE'  : (0x0000,),
   'REPORTING_MODE'  : (0x0000,),
   'WHICH_SP'  : (0x0000,),
}

prm_575_FDE_GetSOM = {
   'test_num' : 575,
   'prm_name' : 'prm_575_FDE_GetSOM',
	"TEST_MODE"  : (0x1B,),
	"DRIVE_STATE"  : (0x0000,),
	"REPORTING_MODE"  : (0x0000,),
	"WHICH_SP"  : (0x0000,),
}

prm_599_BusDeviceReset = {
# oProc.St({'test_num':599,'prm_name':'Bus Device Reset'},0x0000,0x0002,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=600) # Bus Device Reset Message with wait til ready
	'test_num':599,
	'prm_name':'Bus Device Reset',
	'timeout':600,
	'PARAMETER_1' :  (0x0000,),
	'PARAMETER_2' :  (0x0002,),
	'PARAMETER_3' :  (0x0000,),
	'PARAMETER_4' :  (0x0000,),
	'PARAMETER_5' :  (0x0000,),
	'PARAMETER_6' :  (0x0000,),
	'PARAMETER_7' :  (0x0000,),
	'PARAMETER_8' :  (0x0000,),
	'PARAMETER_9' :  (0x0000,),
	'PARAMETER_10':  (0x0000,),
}

prm_599_ReceiveFactoryCommand = {
# oProc.St({'test_num':599,'prm_name':'Receive Factory Command'},0x0001,0xE100,0x0000,0x2800,0x2459,0x0000,0x0200,0x0000,0x0000,0x0000,timeout=600) # Manually issue Receive Factory Command
	'test_num':599,
	'prm_name':'Receive Factory Command',
	'timeout':600,
	'PARAMETER_1' :  (0x0001,),
	'PARAMETER_2' :  (0xE100,),
	'PARAMETER_3' :  (0x0000,),
	'PARAMETER_4' :  (0x2800,),
	'PARAMETER_5' :  (0x2459,),
	'PARAMETER_6' :  (0x0000,),
	'PARAMETER_7' :  (0x0200,),
	'PARAMETER_8' :  (0x0000,),
	'PARAMETER_9' :  (0x0000,),
	'PARAMETER_10':  (0x0000,),
}

prm_599_SendFactoryCommand = {
# oProc.St({'test_num':599,'prm_name':'Send Factory Command'},0x0001,0xE000,0x0000,0x1000,0x2459,0x0000,0x0200,0x0000,0x0000,0x0000,timeout=600) # Manually issue Send Factory Command
	'test_num':599,
	'prm_name':'Send Factory Command',
	'timeout':600,
	'PARAMETER_1' :  (0x0001,),
	'PARAMETER_2' :  (0xE000,),
	'PARAMETER_3' :  (0x0000,),
	'PARAMETER_4' :  (0x1000,),
	'PARAMETER_5' :  (0x2459,),
	'PARAMETER_6' :  (0x0000,),
	'PARAMETER_7' :  (0x0200,),
	'PARAMETER_8' :  (0x0000,),
	'PARAMETER_9' :  (0x0000,),
	'PARAMETER_10':  (0x0000,),
}

prm_599_SetMaxBuffer = {
# oProc.St({'test_num':599,'prm_name':'Set Max Buffer'},0x0006,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=600) # Set Buffer sizes to maximum
	'test_num':599,
	'prm_name':'Set Max Buffer',
	'timeout':600,
	'PARAMETER_1' : (0x0006,),
	'PARAMETER_2' : (0x0000,),
	'PARAMETER_3' : (0x0000,),
	'PARAMETER_4' : (0x0000,),
	'PARAMETER_5' : (0x0000,),
	'PARAMETER_6' : (0x0000,),
	'PARAMETER_7' : (0x0000,),
	'PARAMETER_8' : (0x0000,),
	'PARAMETER_9' : (0x0000,),
	'PARAMETER_10': (0x0000,),
}


prm_605_PortBypassTest = {
# oProc.St({'test_num':605},0x0000,0x0004,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=600)
	'test_num':605,
	'prm_name':'Port Bypass Test',
	'timeout':600,
	'TEST_FUNCTION' : (0x0000,),
	'WAIT_READY' : (0x0000,),
	'TEST_OPERATING_MODE' : (0x0004,),
	'OPTIONS' : (0x0000,),
	'RETRY_LIMIT' : (0x0000,),
	'DELAY_TIME' : (0x0000,),
}

prm_608_PortLoginA = {
# oProc.St({'test_num':608,'prm_name':'Port Login A'},0x0000,0x0200,0x0001,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=300) # Clears LIP on Port A for login
	'test_num':608,
	'prm_name':'Port Login A',
	'timeout':600,
	'TEST_FUNCTION' : (0x0000,),
	'REPORT_OPTION' : (0x0000,),
	'LOGIN_OPTION' : (0x0000,),
	'LOOP_INIT' : (0x0001,),
	'FRAME_SIZE' : (0x0200,),
}

prm_608_PortLoginB = {
# oProc.St({'test_num':608,'prm_name':'Port Login B'},0x1000,0x0200,0x0001,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=300) # Clears LIP on Port B for login
	'test_num':608,
	'prm_name':'Port Login B',
	'timeout':600,
	'TEST_FUNCTION' : (0x1000,),
	'REPORT_OPTION' : (0x0000,),
	'LOGIN_OPTION' : (0x0000,),
	'LOOP_INIT' : (0x0001,),
	'FRAME_SIZE' : (0x0200,),
}

prm_638_ClearSmartCounters = {
# oProc.St({'test_num':638,'prm_name':'Clear SMART Counters'},0x0001,0x5201,0x0100,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=600) # Clear SMART Counters
	'test_num':638,
	'prm_name':'Clear SMART Counters',
	'timeout':600,
	'TEST_FUNCTION' : (0x0000,),
	'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
	'SCSI_COMMAND' : (0x0000,),
	'LONG_COMMAND' : (0x0000,),
	'ATTRIBUTE_MODE' : (0x0000,),
	'REPORT_OPTION' : (0x0000,),
	'BYPASS_WAIT_UNIT_RDY' : (0x0001,),
	'PARAMETER_0' : (0x5201,),
	'PARAMETER_1' : (0x0100,),
	'PARAMETER_2' : (0x0000,),
	'PARAMETER_3' : (0x0000,),
	'PARAMETER_4' : (0x0000,),
	'PARAMETER_5' : (0x0000,),
	'PARAMETER_6' : (0x0000,),
	'PARAMETER_7' : (0x0000,),
	'PARAMETER_8' : (0x0000,),
}

prm_638_FormatSmartFrames = {
# oProc.St({'test_num':638,'prm_name':'Format SMART Frames'},0x0000,0x5201,0x0100,0x0800,0x0000,0x0000,0x0200,0x0000,0x0000,0x0000,timeout=1200) # Format SMART Frames
	'test_num':638,
	'prm_name':'Format SMART Frames',
	'timeout':1200,
	'TEST_FUNCTION' : (0x0000,),
	'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
	'SCSI_COMMAND' : (0x0000,),
	'LONG_COMMAND' : (0x0000,),
	'ATTRIBUTE_MODE' : (0x0000,),
	'REPORT_OPTION' : (0x0000,),
	'BYPASS_WAIT_UNIT_RDY' : (0x0000,),
	'PARAMETER_0' : (0x5201,),
	'PARAMETER_1' : (0x0100,),
	'PARAMETER_2' : (0x0800,),
	'PARAMETER_3' : (0x0000,),
	'PARAMETER_4' : (0x0000,),
	'PARAMETER_5' : (0x0200,),
	'PARAMETER_6' : (0x0000,),
	'PARAMETER_7' : (0x0000,),
	'PARAMETER_8' : (0x0000,),
}

prm_638_GetSmartSramFrame = {
# oProc.St({'test_num':638,'prm_name':'Get SMART SRAM Frame'},0x0002,0x5201,0x0100,0x0300,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=600) # Get SMART SRAM Frame
	'test_num':638,
	'prm_name':'Get SMART SRAM Frame',
	'timeout':600,
	'TEST_FUNCTION' : (0x0000,),
	'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
	'SCSI_COMMAND' : (0x0000,),
	'LONG_COMMAND' : (0x0000,),
	'ATTRIBUTE_MODE' : (0x0000,),
	'REPORT_OPTION' : (0x0001,),
	'BYPASS_WAIT_UNIT_RDY' : (0x0000,),
	'PARAMETER_0' : (0x5201,),
	'PARAMETER_1' : (0x0100,),
	'PARAMETER_2' : (0x0300,),
	'PARAMETER_3' : (0x0000,),
	'PARAMETER_4' : (0x0000,),
	'PARAMETER_5' : (0x0000,),
	'PARAMETER_6' : (0x0000,),
	'PARAMETER_7' : (0x0000,),
	'PARAMETER_8' : (0x0000,),
}

prm_638_HeadAmpMeasurements = {
# oProc.St({'test_num':638,'prm_name':'Head amp measurements'},0x0001,0x5201,0x0100,0x0a00,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=600) # Do head amp measurements for SMART
	'test_num':638,
	'prm_name':'Head amp measurements',
	'timeout':600,
	'TEST_FUNCTION' : (0x0000,),
	'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
	'SCSI_COMMAND' : (0x0000,),
	'LONG_COMMAND' : (0x0000,),
	'ATTRIBUTE_MODE' : (0x0000,),
	'REPORT_OPTION' : (0x0000,),
	'BYPASS_WAIT_UNIT_RDY' : (0x0001,),
	'PARAMETER_0' : (0x5201,),
	'PARAMETER_1' : (0x0100,),
	'PARAMETER_2' : (0x0A00,),
	'PARAMETER_3' : (0x0000,),
	'PARAMETER_4' : (0x0000,),
	'PARAMETER_5' : (0x0000,),
	'PARAMETER_6' : (0x0000,),
	'PARAMETER_7' : (0x0000,),
	'PARAMETER_8' : (0x0000,),
}

prm_638_ManufactureControlInitialize = {
# oProc.St({'test_num':638,'prm_name':'Manufacture Control Initialize'},0x0001,0x6301,0x0100,0x0300,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=600) # Manufacture Control Initialize
	'test_num':638,
	'prm_name':'Manufacture Control Initialize',
	'timeout':600,
	'TEST_FUNCTION' : (0x0000,),
	'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
	'SCSI_COMMAND' : (0x0000,),
	'LONG_COMMAND' : (0x0000,),
	'ATTRIBUTE_MODE' : (0x0000,),
	'REPORT_OPTION' : (0x0000,),
	'BYPASS_WAIT_UNIT_RDY' : (0x0001,),
	'PARAMETER_0' : (0x6301,),
	'PARAMETER_1' : (0x0100,),
	'PARAMETER_2' : (0x0300,),
	'PARAMETER_3' : (0x0000,),
	'PARAMETER_4' : (0x0000,),
	'PARAMETER_5' : (0x0000,),
	'PARAMETER_6' : (0x0000,),
	'PARAMETER_7' : (0x0000,),
	'PARAMETER_8' : (0x0000,),
}

prm_638_EWLM_ControlClearLog = {
# oProc.St({'test_num':638,'prm_name':'EWLM Control: Clear Log'},0x0001,0x7401,0x0100,0x0100,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=600)  # EWLM Control: Clear Log
	'test_num':638,
	'prm_name':'EWLM Control: Clear Log',
	'timeout':600,
	'TEST_FUNCTION' : (0x0000,),
	'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
	'SCSI_COMMAND' : (0x0000,),
	'LONG_COMMAND' : (0x0000,),
	'ATTRIBUTE_MODE' : (0x0000,),
	'REPORT_OPTION' : (0x0000,),
	'BYPASS_WAIT_UNIT_RDY' : (0x0001,),
	'PARAMETER_0' : (0x7401,),
	'PARAMETER_1' : (0x0100,),
	'PARAMETER_2' : (0x0100,),
	'PARAMETER_3' : (0x0000,),
	'PARAMETER_4' : (0x0000,),
	'PARAMETER_5' : (0x0000,),
	'PARAMETER_6' : (0x0000,),
	'PARAMETER_7' : (0x0000,),
	'PARAMETER_8' : (0x0000,),
}

prm_638_PlatformFactoryUnlock = {
# oProc.St({'test_num':638,'prm_name':'Platform Factory Unlock'},0x0001,0xFFFF,0x0100,0x9A32,0x4F03,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=600) # Unlock for Platform
	'test_num':638,
	'prm_name':'Platform Factory Unlock',
	'timeout':600,
	'TEST_FUNCTION' : (0x0000,),
	'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
	'SCSI_COMMAND' : (0x0000,),
	'LONG_COMMAND' : (0x0000,),
	'ATTRIBUTE_MODE' : (0x0000,),
	'REPORT_OPTION' : (0x0000,),
	'BYPASS_WAIT_UNIT_RDY' : (0x0001,),
	'PARAMETER_0' : (0xFFFF,),
	'PARAMETER_1' : (0x0100,),
	'PARAMETER_2' : (0x9A32,),
	'PARAMETER_3' : (0x4F03,),
	'PARAMETER_4' : (0x0000,),
	'PARAMETER_5' : (0x0000,),
	'PARAMETER_6' : (0x0000,),
	'PARAMETER_7' : (0x0000,),
	'PARAMETER_8' : (0x0000,),
}

prm_638_ReadCapacity = {
# oProc.St({'test_num':638,'prm_name':'Read Capacity'},0x0012,0x2500,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000) # Read Capacity
	'test_num':638,
	'prm_name':'Read Capacity',
	'TEST_FUNCTION' : (0x0000,),
	'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
	'SCSI_COMMAND' : (0x0001,),
	'LONG_COMMAND' : (0x0000,),
	'ATTRIBUTE_MODE' : (0x0000,),
	'REPORT_OPTION' : (0x0001,),
	'BYPASS_WAIT_UNIT_RDY' : (0x0000,),
	'PARAMETER_0' : (0x2500,),
	'PARAMETER_1' : (0x0000,),
	'PARAMETER_2' : (0x0000,),
	'PARAMETER_3' : (0x0000,),
	'PARAMETER_4' : (0x0000,),
	'PARAMETER_5' : (0x0000,),
	'PARAMETER_6' : (0x0000,),
	'PARAMETER_7' : (0x0000,),
	'PARAMETER_8' : (0x0000,),
}

prm_638_ReadChangeableModesense = {
# oProc.St({'test_num':638,'prm_name':'Read Changeable ModeSense'},0x0012,0x5a00,0x7f00,0x0000,0x00ff,0xff00,0x0000,0x0000,0x0000,0x0000) # Read Changeable Mode Sense
	'test_num':638,
	'prm_name':'Read Changeable ModeSense',
	'TEST_FUNCTION' : (0x0000,),
	'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
	'SCSI_COMMAND' : (0x0001,),
	'LONG_COMMAND' : (0x0000,),
	'ATTRIBUTE_MODE' : (0x0000,),
	'REPORT_OPTION' : (0x0001,),
	'BYPASS_WAIT_UNIT_RDY' : (0x0000,),
	'PARAMETER_0' : (0x5A00,),
	'PARAMETER_1' : (0x7F00,),
	'PARAMETER_2' : (0x0000,),
	'PARAMETER_3' : (0x00FF,),
	'PARAMETER_4' : (0xFF00,),
	'PARAMETER_5' : (0x0000,),
	'PARAMETER_6' : (0x0000,),
	'PARAMETER_7' : (0x0000,),
	'PARAMETER_8' : (0x0000,),
}

prm_638_ReadCurrentModesense = {
# oProc.St({'test_num':638,'prm_name':'Read Current ModeSense'},0x0012,0x5a00,0x3f00,0x0000,0x00ff,0xff00,0x0000,0x0000,0x0000,0x0000) # Read Current Mode Sense
	'test_num':638,
	'prm_name':'Read Current ModeSense',
	'TEST_FUNCTION' : (0x0000,),
	'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
	'SCSI_COMMAND' : (0x0001,),
	'LONG_COMMAND' : (0x0000,),
	'ATTRIBUTE_MODE' : (0x0000,),
	'REPORT_OPTION' : (0x0001,),
	'BYPASS_WAIT_UNIT_RDY' : (0x0000,),
	'PARAMETER_0' : (0x5A00,),
	'PARAMETER_1' : (0x3F00,),
	'PARAMETER_2' : (0x0000,),
	'PARAMETER_3' : (0x00FF,),
	'PARAMETER_4' : (0xFF00,),
	'PARAMETER_5' : (0x0000,),
	'PARAMETER_6' : (0x0000,),
	'PARAMETER_7' : (0x0000,),
	'PARAMETER_8' : (0x0000,),
}

prm_638_ReadDefaultModesense = {
# oProc.St({'test_num':638,'prm_name':'Read Default ModeSense'},0x0012,0x5a00,0xbf00,0x0000,0x00ff,0xff00,0x0000,0x0000,0x0000,0x0000) # Read Default Mode Sense
	'test_num':638,
	'prm_name':'Read Default ModeSense',
	'TEST_FUNCTION' : (0x0000,),
	'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
	'SCSI_COMMAND' : (0x0001,),
	'LONG_COMMAND' : (0x0000,),
	'ATTRIBUTE_MODE' : (0x0000,),
	'REPORT_OPTION' : (0x0001,),
	'BYPASS_WAIT_UNIT_RDY' : (0x0000,),
	'PARAMETER_0' : (0x5A00,),
	'PARAMETER_1' : (0xBF00,),
	'PARAMETER_2' : (0x0000,),
	'PARAMETER_3' : (0x00FF,),
	'PARAMETER_4' : (0xFF00,),
	'PARAMETER_5' : (0x0000,),
	'PARAMETER_6' : (0x0000,),
	'PARAMETER_7' : (0x0000,),
	'PARAMETER_8' : (0x0000,),
}

prm_638_ReadSavedModesense = {
# oProc.St({'test_num':638,'prm_name':'Read Saved ModeSense'},0x0012,0x5a00,0xff00,0x0000,0x00ff,0xff00,0x0000,0x0000,0x0000,0x0000) # Read Saved Mode Sense
	'test_num':638,
	'prm_name':'Read Saved ModeSense',
	'TEST_FUNCTION' : (0x0000,),
	'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
	'SCSI_COMMAND' : (0x0001,),
	'LONG_COMMAND' : (0x0000,),
	'ATTRIBUTE_MODE' : (0x0000,),
	'REPORT_OPTION' : (0x0001,),
	'BYPASS_WAIT_UNIT_RDY' : (0x0000,),
	'PARAMETER_0' : (0x5A00,),
	'PARAMETER_1' : (0xFF00,),
	'PARAMETER_2' : (0x0000,),
	'PARAMETER_3' : (0x00FF,),
	'PARAMETER_4' : (0xFF00,),
	'PARAMETER_5' : (0x0000,),
	'PARAMETER_6' : (0x0000,),
	'PARAMETER_7' : (0x0000,),
	'PARAMETER_8' : (0x0000,),
}

prm_638_StandardInquiryData = {
# oProc.St({'test_num':638,'prm_name':'Standard Inquiry Data'},0x0012,0x1200,0x0000,0xff00,0x00ff,0xff00,0x0000,0x0000,0x0000,0x0000) # Read Standard Inquiry Data
	'test_num':638,
	'prm_name':'Standard Inquiry Data',
	'TEST_FUNCTION' : (0x0000,),
	'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
	'SCSI_COMMAND' : (0x0001,),
	'LONG_COMMAND' : (0x0000,),
	'ATTRIBUTE_MODE' : (0x0000,),
	'REPORT_OPTION' : (0x0001,),
	'BYPASS_WAIT_UNIT_RDY' : (0x0000,),
	'PARAMETER_0' : (0x1200,),
	'PARAMETER_1' : (0x0000,),
	'PARAMETER_2' : (0xFF00,),
	'PARAMETER_3' : (0x00FF,),
	'PARAMETER_4' : (0xFF00,),
	'PARAMETER_5' : (0x0000,),
	'PARAMETER_6' : (0x0000,),
	'PARAMETER_7' : (0x0000,),
	'PARAMETER_8' : (0x0000,),
}

prm_638_ReadDIF = {
# oProc.St({'test_num':638,'prm_name':'Read DIF file'},0x0001,0x4401,0x0100,0x0100,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=3600)  #Read DIF file
	'test_num':638,
	'prm_name':'Read DIF file',
	'timeout':600,
	'TEST_FUNCTION' : (0x0000,),
	'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
	'SCSI_COMMAND' : (0x0000,),
	'LONG_COMMAND' : (0x0000,),
	'ATTRIBUTE_MODE' : (0x0000,),
	'REPORT_OPTION' : (0x0000,),
	'BYPASS_WAIT_UNIT_RDY' : (0x0001,),
	'PARAMETER_0' : (0x4401,),
	'PARAMETER_1' : (0x0100,),
	'PARAMETER_2' : (0x0100,),
	'PARAMETER_3' : (0x0000,),
	'PARAMETER_4' : (0x0000,),
	'PARAMETER_5' : (0x0000,),
	'PARAMETER_6' : (0x0000,),
	'PARAMETER_7' : (0x0000,),
	'PARAMETER_8' : (0x0000,),
}

prm_638_WriteDIF = {
# oProc.St({'test_num':638,'prm_name':'Write DIF file'},0x0001,0x4501,0x0100,0x0100,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=3600)  #Write DIF file
	'test_num':638,
	'prm_name':'Write DIF file',
	'timeout':600,
	'TEST_FUNCTION' : (0x0000,),
	'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
	'SCSI_COMMAND' : (0x0000,),
	'LONG_COMMAND' : (0x0000,),
	'ATTRIBUTE_MODE' : (0x0000,),
	'REPORT_OPTION' : (0x0000,),
	'BYPASS_WAIT_UNIT_RDY' : (0x0001,),
	'PARAMETER_0' : (0x4501,),
	'PARAMETER_1' : (0x0100,),
	'PARAMETER_2' : (0x0100,),
	'PARAMETER_3' : (0x0000,),
	'PARAMETER_4' : (0x0000,),
	'PARAMETER_5' : (0x0000,),
	'PARAMETER_6' : (0x0000,),
	'PARAMETER_7' : (0x0000,),
	'PARAMETER_8' : (0x0000,),
}

prm_638_ReadMIF = {
#      oProc.St({'test_num':638},0x0001,0x4401,0x0100,0x0500,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=3600)  #Read MIF file
	'test_num':638,
	'prm_name':'Read MIF file',
	'timeout':600,
      	'TEST_FUNCTION' : (0x0000,),
      	'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
      	'SCSI_COMMAND' : (0x0000,),
      	'LONG_COMMAND' : (0x0000,),
      	'ATTRIBUTE_MODE' : (0x0000,),
      	'REPORT_OPTION' : (0x0000,),
      	'BYPASS_WAIT_UNIT_RDY' : (0x0001,),
      	'PARAMETER_0' : (0x4401,),
      	'PARAMETER_1' : (0x0100,),
      	'PARAMETER_2' : (0x0500,),
      	'PARAMETER_3' : (0x0000,),
      	'PARAMETER_4' : (0x0000,),
      	'PARAMETER_5' : (0x0000,),
      	'PARAMETER_6' : (0x0000,),
      	'PARAMETER_7' : (0x0000,),
      	'PARAMETER_8' : (0x0000,),
}

prm_638_WriteMIF = {
#      oProc.St({'test_num':638},0x0001,0x4501,0x0100,0x0500,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=3600)  #Write MIF file
	'test_num':638,
	'prm_name':'Write MIF file',
	'timeout':600,
      	'TEST_FUNCTION' : (0x0000,),
      	'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
      	'SCSI_COMMAND' : (0x0000,),
      	'LONG_COMMAND' : (0x0000,),
      	'ATTRIBUTE_MODE' : (0x0000,),
      	'REPORT_OPTION' : (0x0000,),
      	'BYPASS_WAIT_UNIT_RDY' : (0x0001,),
      	'PARAMETER_0' : (0x4501,),
      	'PARAMETER_1' : (0x0100,),
      	'PARAMETER_2' : (0x0500,),
      	'PARAMETER_3' : (0x0000,),
      	'PARAMETER_4' : (0x0000,),
      	'PARAMETER_5' : (0x0000,),
      	'PARAMETER_6' : (0x0000,),
      	'PARAMETER_7' : (0x0000,),
      	'PARAMETER_8' : (0x0000,),
}

prm_638_ReadFLASHCAP = {
#      oProc.St({'test_num':638},0x0001,0x4B01,0x0100,0x0101,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=3600)  #Read FLASH CAP
	'test_num':638,
	'prm_name':'Read FLASH CAP',
	'timeout':600,
      	'TEST_FUNCTION' : (0x0000,),
      	'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
      	'SCSI_COMMAND' : (0x0000,),
      	'LONG_COMMAND' : (0x0000,),
      	'ATTRIBUTE_MODE' : (0x0000,),
      	'REPORT_OPTION' : (0x0000,),
      	'BYPASS_WAIT_UNIT_RDY' : (0x0001,),
      	'PARAMETER_0' : (0x4B01,),
      	'PARAMETER_1' : (0x0100,),
      	'PARAMETER_2' : (0x0101,),
      	'PARAMETER_3' : (0x0000,),
      	'PARAMETER_4' : (0x0000,),
      	'PARAMETER_5' : (0x0000,),
      	'PARAMETER_6' : (0x0000,),
      	'PARAMETER_7' : (0x0000,),
      	'PARAMETER_8' : (0x0000,),
}

prm_1501_SavEqDef = {
   'test_num':1501,
   'prm_name':'Mode Sense:  SAV=DEF',
   'timeout':600,
   'FIRST_SKIPPED_PAGE' : (0xffff,),  # (0xffff,) = no page skip
   'SECOND_SKIPPED_PAGE': (0xffff,),  # (0xffff,) = no page skip
   'THIRD_SKIPPED_PAGE' : (0xffff,),  # (0xffff,) = no page skip
   'FOURTH_SKIPPED_PAGE': (0xffff,),  # (0xffff,) = no page skip
   'FIFTH_SKIPPED_PAGE' : (0xffff,),  # (0xffff,) = no page skip
}
