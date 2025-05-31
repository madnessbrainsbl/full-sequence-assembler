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
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_CPC_ICmd_Params.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_CPC_ICmd_Params.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from base_Initiator_Cmd_Params import *


UnlockFactoryCmds = {
   'test_num'              : 638,
   'prm_name'              : 'prm_638_Unlock_Seagate',
   'timeout'               : 3600,
   'spc_id'                : 1,
   'DFB_WORD_0'            : 0xFFFF,            # DITS cmd ID (Unlock Diagnostics)
   'DFB_WORD_1'            : 0x0100,            # Rev ID
   'DFB_WORD_2'            : 0x9A32,            # Unlock Seagate Access Key LSW
   'DFB_WORD_3'            : 0x4F03,            # Unlock Seagate Access Key MSW
   'retryECList'           : [14061, 14029, 14016],
   'retryCount'            : 10,
   'retryMode'             : HARD_RESET_RETRY,
   'stSuppressResults'     : ST_SUPPRESS__ALL,
   }

ClearFormatCorrupt={
   'test_num'              : 638,
   'prm_name'              : 'ClearFormatCorrupt',
   'timeout'               : 3600,
   'spc_id'                : 1,
   'DFB_WORD_0'            : 0x1301,            # DITS cmd ID (Set Clear Format Corrupt Condition)
   'DFB_WORD_1'            : 0x0100,            # Rev ID (Usually x0001)
   'DFB_WORD_2'            : 0x0100,            # LSB_bit_0: 0=Normal operation 1=Clear fmt corrupt
   'DFB_WORD_3'            : 0x0000,
   }

GetPreampTemp={            # Sent servo command 2F (Temperature sensor measurement)
   'test_num'              : 638,
   'prm_name'              : 'GetPreampTemp',
   'timeout'               : 3600,
   'spc_id'                : 1,
   'DFB_WORD_0'            : 0x4F01,            # DITS cmd ID
   'DFB_WORD_1'            : 0x0100,            # Rev ID (Usually x0001)
   'DFB_WORD_2'            : 0x0000,            # LSB_bit_0=CO, bit_1=O, bit_2=F, bit_3=T,bit_4=D.  MSB = rsvd.
   'DFB_WORD_3'            : 0x2F00,            # Servo cmd (16 bits, little endian)
   }

LongDST={
   'test_num'              : 600,
   'prm_name'              : 'LongDST',
   'timeout'               : 54000,
   'spc_id'                : 1,
   'TEST_FUNCTION'         : 2,                 # 1=short DST 2=long DST
   'STATUS_CHECK_DELAY'    : 60,
   }

ShortDST={
   'test_num'              : 600,
   'prm_name'              : 'ShortDST',
   'timeout'               : 3600,
   'spc_id'                : 1,
   'TEST_FUNCTION'         : 1,                 # 1=short DST, 2=long DST
   'STATUS_CHECK_DELAY'    : 10,
   }

WriteFinalAssemblyDate = {
   'test_num'              : 557,
   'prm_name'              : 'WriteFinalAssemblyDate',
   'CTRL_WORD1'            : 0x0001,
   'TEST_FUNCTION'         : 1,                 # 0=Write, 1=Read, 2=Compare to current date, Final Assembly Date Code
   'BYTE_OFFSET'           : (0, 0x0046),
   'FINAL_ASSEMBLY_DATE'   : (0,0,0,0),
   'timeout'               : 600,
   }

ClearUDS = {
   'test_num'              : 556,
   'prm_name'              : 'Clear UDS counters and SMART',
   'timeout'               : 300,
   'CTRL_WORD1'            : 0x10F,
   }

TransferMode = {
   'test_num'              : 533,
   'prm_name'              : 'TransferMode',
   'timeout'               : 300,
   'stSuppressResults'     : ST_SUPPRESS__ALL,
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

SetProductID = {
   'test_num'              : 506,
   'prm_name'              : 'prm_506_set_PROD_ID',
   'timeout'               : 30,
   'stSuppressResults'     : ST_SUPPRESS__ALL,
   'PROD_ID'               : 0,
   }