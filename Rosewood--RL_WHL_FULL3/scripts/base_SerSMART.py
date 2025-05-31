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
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_SerSMART.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_SerSMART.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#

from Constants import *
from TestParamExtractor import TP
from State import CState
import MessageHandler as objMsg
from PowerControl import objPwrCtrl
import ScrCmds

#----------------------------------------------------------------------------------------------------------
class CClearSMART(CState):
   """
      Description: Class that will perform SMART reset and generic customer prep.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if testSwitch.WA_0124639_231166_DRIVE_SMART_NOT_SUPPORTED:
         objMsg.printMsg("SMART access disabled for this F3 based on PF3 flag WA_0124639_231166_DRIVE_SMART_NOT_SUPPORTED")
         return

      from serialScreen import sptDiagCmds
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      self.oSerial = sptDiagCmds()
      self.oSerial.enableDiags()

      if testSwitch.BIGS_FIRMWARE_NEED_SPECIAL_CMD_IN_F3:

         if testSwitch.WA_0241988_305538_DNLD_F3_2X_WORKAROUND and self.dut.stateRerun.get('FAIL',0) > self.dut.stateRerun.get('RERUN',1):  # already failed once
            self.oSerial.ClearBIGSFlash()

         self.oSerial.initBIGSFirmware()

         if testSwitch.WA_0241988_305538_DNLD_F3_2X_WORKAROUND:
            if self.oSerial.CheckForBootFlashMsg() == False:
               ScrCmds.raiseException(39208, 'Boot Flash message not found')
            objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
            self.oSerial.enableDiags()

      self.oSerial.SmartCmd(TP.smartResetParams)
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

