#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: AFH Coefficient file for Luxor
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Amazon/AFH_coeffs.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $perp
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Amazon/AFH_coeffs.py#1 $
# Level: 1
#---------------------------------------------------------------------------------------------------------#

from Constants import *
from Test_Switches import testSwitch

PRE_AMP_HEATER_MODE = 'LO_POWER'

if testSwitch.M10P:
   from AFH_coeffs_M10P import clearance_Coefficients
elif testSwitch.CHENGAI:
   from AFH_coeffs_Chengai import clearance_Coefficients
elif testSwitch.CHEOPSAM_LITE_SOC:
   from AFH_coeffs_RosewoodLC import clearance_Coefficients
else:
   from AFH_coeffs_Rosewood import clearance_Coefficients
