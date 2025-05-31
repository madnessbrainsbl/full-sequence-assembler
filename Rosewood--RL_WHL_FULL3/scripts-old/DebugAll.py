#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2008, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: DebugAll Module
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/DebugAll.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/DebugAll.py#1 $
# Level: 3

#---------------------------------------------------------------------------------------------------------#

import types, os, time
from TestParamExtractor import TP
from Constants import *
import MessageHandler as objMsg
from State import CState
from Drive import objDut
from PowerControl import objPwrCtrl


class CDebugAll(CState):
   """
    Provide for debug team
   """
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self,dut,depList)

#---------------------------------------------------------------------------------------------------------#
   def run(self):
       from Process import CProcess
       self.oProc = CProcess()
       
       prm_103_WIJITA = {'test_num' : 103,
          'prm_name'       : 'Measure WIJITA',
          'timeout'        : 1200,
          'spc_id'         : 0,
          'WEDGE_NUM'      : 0x28A8,
          'LOOP_CNT'       : 200,
          'STD_DEV_LIMIT'  : 350,
          'DELTA_LIMIT'    : 18,
          'CWORD1'         : 0x41C8,
          'HEAD_RANGE'     : 0x00FF,
          'RW_MODE'        : 0x0008,
        }
        
       self.oProc.St(prm_103_WIJITA)
        
        
      