#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: All global constants live within this file
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/26 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Amazon/RL42/pgm_Constants.py $
# $Revision: #2 $
# $DateTime: 2016/05/26 19:08:01 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Amazon/RL42/pgm_Constants.py#2 $
# Level: 1
#---------------------------------------------------------------------------------------------------------#


#======Section to change by program for VE======================================
virtualPgm = 'RL42'
virtualPartNum = '1RK172-8J8'  #For BootScript, cmEmul
virtualDrvSN = 'QDE003BD'      #For cmEmul , 2hdr sn from yarraBP
virtualNibletString = 'DE_N2L3_1000G_4096_5400' # pls use '0H_NHL3_1000G_4096_5400' for 1T
#===============================================================================

try:
   PROCESS_HDA_BAUD = Baud460800 
except:
   PROCESS_HDA_BAUD = 460800        #Exception case when not running in CM

