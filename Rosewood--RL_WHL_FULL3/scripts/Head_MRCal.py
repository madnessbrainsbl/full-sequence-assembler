#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Head Cal Module
#  - Contains support for CAL_MR_RES state
#  - Limit this module to PRE2 states if possible
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
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Head_MRCal.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Head_MRCal.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
from State import CState


#----------------------------------------------------------------------------------------------------------
class CCalibrateMRRes(CState):
   """
      Description: Class that will calibrate MR resistance and save the values to SIM file.  The first
      head resistance calibration is run in CInitializeHead_Elec.  This is intented to be run later
      in the process when a re-calibration is necessary.  Calibrated resistances may be saved for
      comparison later in the process.
      Parameters:
         DIFF_MR_RESULTS:  Force Diff of results - test against limit TP.mrDeltaLim ( Default = 0 )
         SAVE_TO_SIM: Choose to update SIM with new values ( Default = 1 )
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from RdWr import CMrResFile
      from Process import CProcess
      self.oProc = CProcess()

      diffMRresults = self.params.get('DIFF_MR_RESULTS',0)
      saveToSIM = self.params.get('SAVE_TO_SIM',1)

      if testSwitch.FE_0117296_357260_SUPPORT_SECOND_MR_CALL_AND_DIFF:
         if testSwitch.FE_0173493_347506_USE_TEST321 and testSwitch.extern.SFT_TEST_0321:
            oMrRes = CMrResFile(TP.mrBiasCal_321, TP.mrDeltaLim)
         else:
            oMrRes = CMrResFile(TP.PresetAGC_InitPrm_186, TP.mrDeltaLim)

         if diffMRresults:    # Re-calibrate and Diff MR resistance
            oMrRes.diffMRValues(mrOGfromSIM = 0)
         else:                # Re-calibrate MR resistance
            if testSwitch.FE_0173493_347506_USE_TEST321	and testSwitch.extern.SFT_TEST_0321:
               self.oProc.St(TP.mrBiasCal_321)
            else:
               self.oProc.St(TP.PresetAGC_InitPrm_186)
         if saveToSIM:        # Save MR resistance data for later comparison
            oMrRes.saveToGenResFile()
      else:
         # Re-calibrate MR resistance
         if testSwitch.FE_0173493_347506_USE_TEST321 and testSwitch.extern.SFT_TEST_0321:
            self.oProc.St(TP.mrBiasCal_321)
         else:
            self.oProc.St(TP.PresetAGC_InitPrm_186)
         # Save MR resistance data for later comparison
         if testSwitch.FE_0173493_347506_USE_TEST321 and testSwitch.extern.SFT_TEST_0321:
            oMrRes = CMrResFile(TP.get_MR_Resistance_321, TP.mrDeltaLim)
         else:
            oMrRes = CMrResFile(TP.get_MR_Values_186, TP.mrDeltaLim)
         oMrRes.saveToGenResFile()


#-------------------------------------------------------------------------------------------------------------
if testSwitch.FE_0117296_357260_SUPPORT_SECOND_MR_CALL_AND_DIFF:
   class CDeltaMRRes(CState):
      """
         Description: Class that will measure the MR resistance check the values against the values in the SIM file.
         Parameters:
            None
      """
      #-------------------------------------------------------------------------------------------------------
      def __init__(self, dut, params={}):
         self.params = params
         depList = []
         CState.__init__(self, dut, depList)
      #-------------------------------------------------------------------------------------------------------
      def run(self):
         from RdWr import CMrResFile

         #=== Perform MR resistance delta check
         if testSwitch.FE_0173493_347506_USE_TEST321 and testSwitch.extern.SFT_TEST_0321:
            oMrRes = CMrResFile(TP.get_MR_Resistance_321, TP.mrDeltaLim)
         else:
            oMrRes = CMrResFile(TP.get_MR_Values_186, TP.mrDeltaLim)
         oMrRes.diffMRValues()

