#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2008, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: AFH Module
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/AFH_manageHeaters.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/AFH_manageHeaters.py#1 $
# Level: 3

#---------------------------------------------------------------------------------------------------------#

from Constants import *
import ScrCmds
from Process import CProcess

import Utility
import FSO

from TestParamExtractor import TP

from Drive import objDut   # usage is objDut
from Servo import CServoOpti

import MessageHandler as objMsg
from AFH_constants import *

from SampleMonitor import TD
from SampleMonitor import CSampMon



INVALID_TRACK_NUMBER = -99999
XHEATER_CLR_DELTA_EXCEEDED = 42197  #/ * AFH- Cross heater clearance delta exceeded. */               

class CAFH_manageActiveHeaters:
   def __init__(self):
      self.dut = objDut

      self.headList = range(objDut.imaxHead)   # note imaxHead is the number of heads

      # variables to initialize
      if (testSwitch.FE_0159597_357426_DSP_SCREEN == 1):
         stateTableName = self.dut.nextState
         if stateTableName == "AFH1_DSP":
            objMsg.printMsg("DSPTruthValue AFH2 is %x" % TD.Truth)
            self.headList = TD.Truth 

      self.PRODUCTION_MODE = ON

      self.disableREADER_HEATER_inAFH_stateList = []
      if testSwitch.FE_0165920_341036_DISABLE_READER_HEATER_CONTACT_DETECT_AFH2:
         self.disableREADER_HEATER_inAFH_stateList.append(2)

      # end of __init__

   def getDisableREADER_HEATER_inAFH_stateList(self, ):
      return self.disableREADER_HEATER_inAFH_stateList

   def areBothHeatersActive(self, ):
      if len(self.dut.heaterElementList) >= 2:
         return True
      else:
         return False

   # note isDriveDualHeater and areBothHeatersActive is NOW not the same thing since the READER_HEATER contact detect is possibly disabled in AFH2

   def setActiveHeaters(self, AFH_StateLocal):
      self.dut.heaterElementList = [ "WRITER_HEATER" ]

      if (self.dut.isDriveDualHeater == 1) or (testSwitch.virtualRun == 1):

         if not (AFH_StateLocal in self.disableREADER_HEATER_inAFH_stateList):
            self.dut.heaterElementList.append( "READER_HEATER" )



   def getActiveHeaters(self,):
      return self.dut.heaterElementList


   def getActiveHeatersForV3BAR(self, ):
      heaterElementList = [ "WRITER_HEATER" ]
      return heaterElementList

