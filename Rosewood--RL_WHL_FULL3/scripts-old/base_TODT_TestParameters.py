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
# $Date: 2016/05/05 $ 11/09/2008
# $Author: Randy Taylor
# $Source:$
# Level:

####  Revision Log ####
#  Date        Rev.     Comments
#  07/20/2010  1.3      Add Mantaray "9SM"
#  03/17/2010  1.2      Add GLIST_MAX and ALLOW_REC_ERR product control fields
#  03/10/2010  1.1      Add MAX_RCV_ERRS field to prm_ODT butterfly,random,seq
#  03/09/2010  1.0      Initial create of ODT with IO34 initiator
#
#-----------------------------------------------------------------------------------------#
#
#

###############################################################################
# Must have the product listed here and the fields correctly listed or it will
# fail.
# The following are the fields that are currently supported/required:
# 'DRV_TYPE'      = defines the drive type as either "non-SED" or "SED"
# 'INIT_TYPE'     = defines the initiator field name to use from the standard
#                    Codes.py file.
# 'ODTLOOPS'      = number of full ODT processes to run (typically the value is 1)
# 'RUN_TEMP'      = Process run temperature with wait
# 'END_TEMP'      = Ending cell temperature setting with wait
# 'GLIST_MAX'     = Allowable number of Glist errors
# 'ALLOW_REC_ERR' = Allowable recoverable errors per test
# 
from Test_Switches import testSwitch

ODTfamilyInfo={
#Compass
'9TE':{'DRV_TYPE': 'non-SED',   'INIT_TYPE': 'INC_IF3',   'ODTLOOPS': '1',   'RUN_TEMP': '42',   'END_TEMP': '22',   'GLIST_MAX': '2',   'ALLOW_REC_ERR': '3',}, # 300Gig
'9TF':{'DRV_TYPE': 'non-SED',   'INIT_TYPE': 'INC_IF3',   'ODTLOOPS': '1',   'RUN_TEMP': '42',   'END_TEMP': '22',   'GLIST_MAX': '2',   'ALLOW_REC_ERR': '3',}, # 450Gig
'9TG':{'DRV_TYPE': 'non-SED',   'INIT_TYPE': 'INC_IF3',   'ODTLOOPS': '1',   'RUN_TEMP': '42',   'END_TEMP': '22',   'GLIST_MAX': '2',   'ALLOW_REC_ERR': '3',}, # 600Gig
'9TH':{'DRV_TYPE': 'non-SED',   'INIT_TYPE': 'INC_IF3',   'ODTLOOPS': '1',   'RUN_TEMP': '42',   'END_TEMP': '22',   'GLIST_MAX': '2',   'ALLOW_REC_ERR': '3',}, # 900Gig
#Yellowjack
'9SV':{'DRV_TYPE': 'non-SED',   'INIT_TYPE': 'INC_IF3',   'ODTLOOPS': '1',   'RUN_TEMP': '42',   'END_TEMP': '22',   'GLIST_MAX': '2',   'ALLOW_REC_ERR': '3',}, # 146Gig
'9SW':{'DRV_TYPE': 'non-SED',   'INIT_TYPE': 'INC_IF3',   'ODTLOOPS': '1',   'RUN_TEMP': '42',   'END_TEMP': '22',   'GLIST_MAX': '2',   'ALLOW_REC_ERR': '3',}, # 300Gig
#Airwalker
'9RZ':{'DRV_TYPE': 'non-SED',   'INIT_TYPE': 'INC_IF3',   'ODTLOOPS': '1',   'RUN_TEMP': '48',   'END_TEMP': '48',   'GLIST_MAX': '4',   'ALLOW_REC_ERR': '4',}, # 146Gig

#Mantaray
'9SM':{'DRV_TYPE': 'non-SED',   'INIT_TYPE': 'INC_IF3',   'ODTLOOPS': '1',   'RUN_TEMP': '48',   'END_TEMP': '48',   'GLIST_MAX': '4',   'ALLOW_REC_ERR': '4',}, # 3000Gig
'9XT':{'DRV_TYPE': 'SED',       'INIT_TYPE': 'INC_IF3',   'ODTLOOPS': '1',   'RUN_TEMP': '48',   'END_TEMP': '48',   'GLIST_MAX': '4',   'ALLOW_REC_ERR': '4',}, # 3000Gig
'9XK':{'DRV_TYPE': 'SED',       'INIT_TYPE': 'INC_IF3',   'ODTLOOPS': '1',   'RUN_TEMP': '48',   'END_TEMP': '48',   'GLIST_MAX': '4',   'ALLOW_REC_ERR': '4',}, # 3000Gig

#Muskie+
'9YZ':{'DRV_TYPE': 'non-SED',   'INIT_TYPE': 'INC_IF3',   'ODTLOOPS': '1',   'RUN_TEMP': '48',   'END_TEMP': '48',   'GLIST_MAX': '4',   'ALLOW_REC_ERR': '4',}, # 3000Gig

}
###############################################################################




prm_503_Display_Log_Pages = {
	'test_num':503,
	'prm_name':'Display log page 2',
	'timeout':1200,
	"PARAMETER_CODE_1_MSW" : (0xFFFF,),
	"TEST_OPERATING_MODE" : (0x0001,),
	"TEST_FUNCTION" : (0x0000,),
	"SAVE_PARAMETERS" : (0x0000,),
	"PARAMETER_CODE_2_LSW" : (0xFFFF,),
	"PARAMETER_CODE_1_LSW" : (0xFFFF,),
	"PARAMETER_CODE_2_MSW" : (0xFFFF,),
	"BGMS_FAILURES" : (0x0000,),
	"PAGE_CODE" : (0x0002,),
	"ROBUST_LOGGING" : (0xFFFF,),
	"PARAMETER_CODE_2" : (0xFFFF,),
	"PARAMETER_CODE_1" : (0xFFFF,),
}

prm_504_DisplaySense_LastCommand = {
	'test_num':504,
	'prm_name':'Display Sense, Last Cmd, Cyl, Hd, Sec, LBA',
	'timeout':1200,
	"TEST_FUNCTION" : (0x8000,),
	"NUMBER_REGISTER_BANKS" : (0x0000,),
	"CONTROLLER_CHIP_REG" : (0x0000,),
	"TRANSLATE_LOGICAL_BLOCK" : (0x0000,),
}

prm_506_SetTest_StopTime = {
	'test_num':506,
	'prm_name':'Set Test Stop Time = 20 min',
	'timeout':60,
	"FORMAT_CMD_TIME_MSB" : (0x0000,),
	"FACTORY_CMD_TIMEOUT_SECS" : (0x0000,),
	"COMMAND_TIMEOUT_MS" : (0x0000,),
	"TEST_FUNCTION" : (0x0000,),
	"TEST_EXE_TIME_SECONDS" : (0x04B0,),  # 20 min
	"RESPONSE_TIME_MS" : (0x0000,),
	"WAIT_READY_TIME" : (0x0000,),
	"FORMAT_CMD_TIME_LSB" : (0x0000,),
	"COMMAND_TIMEOUT_SECONDS" : (0x0000,),
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

prm_510_ODTRandom = {
	'test_num':510,
	'prm_name':'Random Write - 16 BLK XFer',
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
	"WRITE_READ_MODE" : (0x0002,),
	"ECC_CONTROL" : (0x0000,),
	"BUTTERFLY_ACCESS" : (0x0000,),
	"LBA_LSW" : (0x0000,),
	"TOTAL_BLKS_TO_TRANS_MSW" : (0x0000,),
	"NUMBER_LBA_PER_XFER" : (0x0000,0x0010,),  # 16 blocks per command
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

prm_510_ODTSeq = {
	'test_num':510,
	'prm_name':'Sequential Write - 16 BLK XFer',
	'timeout':36000,
	"ERROR_REPORTING_MODE" : (0x0000,),
	"CACHE_MODE" : (0x0001,),
	"PATTERN_MODE" : (0x0080,),
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
	"WRITE_READ_MODE" : (0x0002,),
	"ECC_CONTROL" : (0x0000,),
	"BUTTERFLY_ACCESS" : (0x0000,),
	"LBA_LSW" : (0x0000,),
	"TOTAL_BLKS_TO_TRANS_MSW" : (0x0000,),
	"NUMBER_LBA_PER_XFER" : (0x0000,0x0010,),  # 16 blocks per command
	"FILL_WRITE_BUFFER" : (0x0000,),
	"SAVE_READ_ERR_TO_MEDIA" : (0x0001,),
	"MAX_REC_ERRORS" : (0x0003,),
	"MAX_RCV_ERRS" : (0x0000,0x0003,),
	"REPORT_HIDDEN_RETRY" : (0x0000,),
	"PATTERN_LSW" : (0x0000,),
	"DISABLE_ECC_ON_FLY" : (0x0000,),
	"MAX_UNRECOVERABLE_ERR" : (0x0000,),
	"CRESCENDO_ACCESS" : (0x0000,),
	"TRANSFER_MODE" : (0x0000,),
	"PATTERN_MSW" : (0x0000,),
	"WRITE_AND_VERIFY" : (0x0000,),
	"LBA_MSW" : (0x0000,),
	"ACCESS_MODE" : (0x0000,),
	"PATTERN_LENGTH_IN_BITS" : (0x0000,),
}

prm_510_ODTButfly = {
	'test_num':510,
	'prm_name':'Butterfly In Write - 16 BLK XFer',
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
	"WRITE_READ_MODE" : (0x0002,),
	"ECC_CONTROL" : (0x0000,),
	"BUTTERFLY_ACCESS" : (0x0001,),  # Butterfly Access
	"LBA_LSW" : (0x0000,),
	"TOTAL_BLKS_TO_TRANS_MSW" : (0x0000,),
	"NUMBER_LBA_PER_XFER" : (0x0000,0x0010,),  # 16 blocks per command
	"FILL_WRITE_BUFFER" : (0x0000,),
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
	"ACCESS_MODE" : (0x0000,),
	"PATTERN_LENGTH_IN_BITS" : (0x0000,),
}

prm_514_FwServoInfo = {
	'test_num':514,
	'prm_name':'FW Servo info',
	'timeout':600,
	'CHECK_MODE_NUMBER' : (0x0000,),
	'ENABLE_VPD' : (0x0001,),
	'TEST_FUNCTION' : (0x8000,),
	'GET_FW_REV_FROM_NETWORK' : (0x0000,),
	'EXPECTED_FW_REV_1' : (0x0000,),
	'EXPECTED_FW_REV_2' : (0x0000,),
	'EXPECTED_FW_REV_3' : (0x0000,),
	'EXPECTED_FW_REV_4' : (0x0000,),
	'PAGE_CODE' : (0x00C0,),
}

prm_514_StdInquiryData = {
	'test_num':514,
	'prm_name':'Std Inquiry Data',
	'timeout':600,
	'CHECK_MODE_NUMBER' : (0x0000,),
	'ENABLE_VPD' : (0x0000,),
	'TEST_FUNCTION' : (0x8000,),
	'GET_FW_REV_FROM_NETWORK' : (0x0000,),
	'EXPECTED_FW_REV_1' : (0x0000,),
	'EXPECTED_FW_REV_2' : (0x0000,),
	'EXPECTED_FW_REV_3' : (0x0000,),
	'EXPECTED_FW_REV_4' : (0x0000,),
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
	'SENSE_DATA_1' : (0x0000,0x0000,0x0000,0x0000,),
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

prm_518_Disable_PreScan_and_BGMS = {
	'test_num':518,
	'prm_name':'Disable PreScan and BGMS',
	'timeout':600,
	"UNIT_READY" : (0x0000,),
	"SAVE_MODE_PARAMETERS" : (0x0001,),
	"MODE_SENSE_INITIATOR" : (0x0000,),
	"TEST_FUNCTION" : (0x0000,),
	"MODIFICATION_MODE" : (0x0000,),
	"MODE_SELECT_ALL_INITS" : (0x0000,),
	"PAGE_FORMAT" : (0x0001,),
	"MODE_SENSE_OPTION" : (0x0003,),
	"PAGE_BYTE_AND_DATA34" : (0x0004,0x0000,0x0005,0x0000,0x0006,0x00FF,0x0007,0x00FF,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,),
	"MODE_COMMAND" : (0x0001,),
	"VERIFY_MODE" : (0x0001,),
	"DATA_TO_CHANGE" : (0x0000,),
	"PAGE_CODE" : (0x001C,),
	"SUB_PAGE_CODE" : (0x0001,),
}

prm_529_CheckServoDefects = {
	'test_num':529,
	'prm_name':'Check for zero Servo Defects',
	'timeout':14400,
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

prm_529_CheckGrowthDefects = {
	'test_num':529,
	'prm_name':'Check for zero Growth Defects',
	'timeout':14400,
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

prm_535_InitiatorInfo = {
	'test_num':535,
	'prm_name':'Initiator info',
	'timeout':600,
	'REG_ADDR' : (0x0000,),
	'REG_VALUE' : (0x0000,),
	'TEST_OPERATING_MODE' : (0x0002,),
	'TEST_FUNCTION' : (0x8800,),
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

prm_538_SpinDown = {
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

prm_538_GetDLD = {
	'test_num':538,
	'prm_name':'Get DLD data',
	'timeout':3600,
	'TEST_FUNCTION' : (0x0000,),
	'SELECT_COPY' : (0x0000,),
	'READ_CAPACITY' : (0x0000,),
	'CHK_OPEN_LATCH_RETRY_CNT' : (0x0000,),
	'SUPRESS_RESULTS' : (0x0000,),
	'USE_CMD_ATTR_TST_PARMS' : (0x0000,),
	'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
	'COMMAND_WORD_1' : (0x4C00,),
	'COMMAND_WORD_2' : (0x4000,),
	'COMMAND_WORD_3' : (0x0000,),
	'COMMAND_WORD_4' : (0x0000,),
	'COMMAND_WORD_5' : (0x0C00,),
	'COMMAND_WORD_6' : (0x0200,),
	'SECTOR_SIZE' : (0x0000,),
	'TRANSFER_OPTION' : (0x0000,),
	'TRANSFER_LENGTH' : (0x0000,),
}

prm_538_GetServoCodes = {
	'test_num':538,
	'prm_name':'Read Servo Fail Loop Code',
	'timeout':3600,
	'TEST_FUNCTION' : (0x0000,),
	'SELECT_COPY' : (0x0000,),
	'READ_CAPACITY' : (0x0001,),
	'CHK_OPEN_LATCH_RETRY_CNT' : (0x0000,),
	'SUPRESS_RESULTS' : (0x0000,),
	'USE_CMD_ATTR_TST_PARMS' : (0x0000,),
	'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
	'COMMAND_WORD_1' : (0xF610,),
	'COMMAND_WORD_2' : (0x0113,),
	'COMMAND_WORD_3' : (0x0000,),
	'COMMAND_WORD_4' : (0x0000,),
	'COMMAND_WORD_5' : (0x0000,),
	'COMMAND_WORD_6' : (0x0200,),
	'SECTOR_SIZE' : (0x0000,),
	'TRANSFER_OPTION' : (0x0000,),
	'TRANSFER_LENGTH' : (0x0000,),
}

prm_564_DispCumulativeSmart = {
	'test_num':564,
	'prm_name':'Disp Cumulative SMART',
	'timeout':600,
	"BAD_SAMPLE_CNT" : (0xFFFF,),
	"BAD_ADDRESS_COUNT" : (0xFFFF,),
	"TEST_FUNCTION" : (0x0000,),
	"MAX_REALLOCATED_SECTORS" : (0x00FF,),
	"CHECK_ALL_SELECTED_HDS" : (0x0000,),
	"BUZZ_COUNT" : (0xFFFF,),
	"MAX_THERMAL_ASP" : (0x00FF,),
	"MAXIMUM_ERROR_COUNT" : (0x0000,),
	"SUPPRESS_REPORT_DATA" : (0x0000,),
	"SOME_HEADS" : (0x0000,),
	"SMART_ATTRIBUTE" : (0x0000,),
	"ONE_TRACK" : (0x00FF,),
	"MAX_READ_ERRORS" : (0x00FF,),
	"TEMPERATURE" : (0xFF21,),
	"FLY_HEIGHT_MEAS" : (0x00FF,),
	"TA_WUS_SPEC" : (0x00FF,),
	"SEEK_ERR_LIMIT" : (0x0030,),
	"SELECTED_HEAD" : (0x0000,),
	"NO_TIMING_MARK_DET" : (0xFFFF,),
	"ONE_THIRD_SEEK" : (0x00FF,),
	"SRVO_UNSF_SPEC" : (0x00FF,),
	"EXTREME_HEADS" : (0x0000,),
}

prm_575_Discovery = {
	'test_num':575,
	'prm_name':'Discovery',
	'timeout':30,
	'TEST_MODE' : (0x0007,),
	'UIDMSWU' : (0x0000,),
	'DRIVE_STATE' : (0x0000,),
	'PASSWORD_TYPE' : (0x0000,),
	'UIDLSWL' : (0x0001,),
	'REPORTING_MODE' : (0x8000,),
	'UIDLSWU' : (0x0000,),
	'WHICH_SP' : (0x0000,),
	'UIDMSWL' : (0x0205,),
}

prm_577_FdeSetDiag = {
	'test_num':577,
	'prm_name':'FDE Set DIAG',
	'timeout':3600,
	'DRIVE_STATE' : (0x0001,),
	'REPORTING_MODE' : (0x0000,),
	'TEST_MODE' : (0x0006,),
	'MSID_TYPE' : (0x0001,),
}
if testSwitch.FE_0180710_426568_P_PSID_MSYMK_AUTH_REQUIRED_FOR_SED_ACCESS:
   prm_577_FdeSetDiag['MSID_TYPE'] = (0x0009,)

prm_577_FdeSetMfg = {
	'test_num':577,
	'prm_name':'FDE Set MFG',
	'timeout':3600,
	'DRIVE_STATE' : (0x0081,),
	'REPORTING_MODE' : (0x0000,),
	'TEST_MODE' : (0x0006,),
	'MSID_TYPE' : (0x0001,),
}
if testSwitch.FE_0180710_426568_P_PSID_MSYMK_AUTH_REQUIRED_FOR_SED_ACCESS:
   prm_577_FdeSetMfg['MSID_TYPE'] = (0x0009,)

prm_600_DST = {
	'test_num':600,
	'prm_name':'Extended DST',
	'timeout':54000,
	'TEST_FUNCTION' : (0x0000,),
	'TEST_OPERATING_MODE' : (0x0002,),
	'DELAY_TIME' : (0x007D,),
}

prm_602_DLD = {
	'test_num':602,
	'prm_name':'Drive Log Dump',
	'timeout':1200,
	'TEST_FUNCTION' : (0x0000,),
	'TEST_OPERATING_MODE' : (0x0001,),
}

prm_608_PortLoginA = {
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
	'test_num':608,
	'prm_name':'Port Login B',
	'timeout':600,
	'TEST_FUNCTION' : (0x1000,),
	'REPORT_OPTION' : (0x0000,),
	'LOGIN_OPTION' : (0x0000,),
	'LOOP_INIT' : (0x0001,),
	'FRAME_SIZE' : (0x0200,),
}

prm_638_ReadCapacity = {
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

prm_518_ModeSelect_Set_Capacity = {
	'test_num':518,
	'prm_name':'Mode Select drive to Maximum Capacity',
	'timeout':600,
	"UNIT_READY" : (0x0000,),
	"SAVE_MODE_PARAMETERS" : (0x0001,),
	"MODE_SENSE_INITIATOR" : (0x0000,),
	"TEST_FUNCTION" : (0x0000,),
	"MODIFICATION_MODE" : (0x0001,),
	"MODE_SELECT_ALL_INITS" : (0x0000,),
	"PAGE_FORMAT" : (0x0000,),
	"MODE_SENSE_OPTION" : (0x0003,),
 	"PAGE_BYTE_AND_DATA34" : (0x00FF,0x01FF,0x02FF,0x03FF,0x04FF,0x05FF,0x06FF,0x07FF,0x0800,0x0900,0x0A00,0x0B00,0x0C00,0x0D00,0x0E00,0x0F00,),
	"MODE_COMMAND" : (0x0001,),
	"VERIFY_MODE" : (0x0000,),
	"DATA_TO_CHANGE" : (0x0000,),
	"PAGE_CODE" : (0x0000,),
	"SUB_PAGE_CODE" : (0x0000,),
}
