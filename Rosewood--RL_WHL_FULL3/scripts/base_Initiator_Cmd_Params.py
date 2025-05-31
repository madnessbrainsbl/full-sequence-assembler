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
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_Initiator_Cmd_Params.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_Initiator_Cmd_Params.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *

InitiatorRev = {
   'test_num'              : 535,
   'prm_name'              : 'prm_535_InitiatorRev',
   'timeout'               : 30,
   'TEST_FUNCTION'         : 0x8800,
   'TEST_OPERATING_MODE'   : 0x0002,
   'DblTablesToParse'      : ['P535_INITIATOR_RELEASE',],
   }

CommandTimeout = {
   'test_num'              : 506,
   'prm_name'              : 'prm_506_CMD_TMO',
   'timeout'               : 30,
   'stSuppressResults'     : ST_SUPPRESS__ALL,
   }

TransferMode = {
   'test_num'              : 533,
   'prm_name'              : 'TransferMode',
   'timeout'               : 300,
   'FC_SAS_TRANSFER_RATE'  : 0x0000,
   'TEST_FUNCTION'         : 0x8000,
   }

CurrentFwOptionsSettings = {
   'test_num':638,
   'prm_name':'CurrentFwOptionsSettings',
   'TEST_FUNCTION'         : 0x0000,
   'WRITE_SECTOR_CMD_ALL_HDS' : 0x0000,
   'SCSI_COMMAND'          : 0x0000,
   'LONG_COMMAND'          : 0x0000,
   'ATTRIBUTE_MODE'        : 0x0000,
   'REPORT_OPTION'         : 0x0001,
   'BYPASS_WAIT_UNIT_RDY'  : 0x0001,
   'PARAMETER_0'           : 0x6001,                     # DITS command 0x160 - Read Congen
   'PARAMETER_1'           : 0x0100,
   'PARAMETER_2'           : 0x0000,
   'timeout'               : 600,
   'DblTablesToParse'      : ['P638_INCOMING_DATA_SIZE']
   }

WrtDefaultFwOptions = {
   'test_num'              : 638,
   'prm_name'              : 'WrtDefaultFwOptions',
   'TEST_FUNCTION'         : 0x0000,
   'WRITE_SECTOR_CMD_ALL_HDS' : 0x0000,
   'SCSI_COMMAND'          : 0x0000,
   'LONG_COMMAND'          : 0x0000,
   'ATTRIBUTE_MODE'        : 0x0000,
   'REPORT_OPTION'         : 0x0001,
   'BYPASS_WAIT_UNIT_RDY'  : 0x0001,
   'PARAMETER_0'           : 0x6101,                     # DITS command 0x161 - Write Congen
   'PARAMETER_1'           : 0x0100,
   'PARAMETER_2'           : 0x0400,                     # Bit 4 -> 1 means Reset all Congen values to defaults
   'timeout'               : 600
   }
