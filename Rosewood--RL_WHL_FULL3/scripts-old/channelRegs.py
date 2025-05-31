#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description:
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/channelRegs.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/channelRegs.py#1 $
# Level:3
#---------------------------------------------------------------------------------------------------------#

"""
Registers
'ID': {'reg':0xFF, 'min':F, 'max':F}
"""

AGERE = {
'AccessType': 16,
'FREF': {'reg':0x84,'min':0,'max':7},
'N1': {'reg':0x87,'min':12,'max':13},
'F1': {'reg':0x87,'min':8,'max':11},
'M1': {'reg':0x87,'min':0,'max':7},
'CTF':{'reg':0x94,'min':0,'max':12},
'NOMF':{'reg':0x8b,'min':0,'max':4},
}
MARVELL8800 = {
}
MARVELL8830 = {
}