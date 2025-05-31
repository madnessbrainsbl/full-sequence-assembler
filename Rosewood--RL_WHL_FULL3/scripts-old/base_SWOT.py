#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: base Serial Port calibration states
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_SWOT.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_SWOT.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from State import CState


#----------------------------------------------------------------------------------------------------------
class CEnableSWOT(CState):
   """
      Description: This class allows the SWOT sensor to be enabled outside of CSetupProc
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from Servo import CServoFunc
      self.oSrvFunc = CServoFunc()
      if testSwitch.FE_0127808_426568_SET_SWOT_BASED_ON_CONFIG_VAR_IN_CENABLESWOT:
         if ConfigVars[CN].get('enableSwotSensor', 0):
            self.oSrvFunc.setSwotSensor(enable = True)
      else:
         self.oSrvFunc.setSwotSensor(enable = True)

