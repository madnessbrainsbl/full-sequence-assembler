#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: SWD Tuning Module
#
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/PCBA_Screen.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/PCBA_Screen.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
from State import CState
import MessageHandler as objMsg

#----------------------------------------------------------------------------------------------------------
class CPcbaScreen(CState):
   """
      Description: Class that will perform early pcba screens
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self,dut,depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from Process import CProcess
      self.oProc = CProcess()

      for modes in TP.pcbaDram_102['modes'].items():
         basePrm = {}
         basePrm.update(TP.pcbaDram_102['base'])
         objMsg.printMsg("%s Testing DRAM Mode %s %s" % (10*'*',str(modes[0]),10*'*'), objMsg.CMessLvl.DEBUG)
         basePrm.update(modes[1])
         self.oProc.St(basePrm)
