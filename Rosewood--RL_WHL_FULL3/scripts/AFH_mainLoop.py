#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2008, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: AFH Module
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/09/01 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/AFH_mainLoop.py $
# $Revision: #3 $
# $DateTime: 2016/09/01 01:52:44 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/AFH_mainLoop.py#3 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#

from Constants import *
from TestParamExtractor import TP
import ScrCmds
from Process import CProcess
import Utility
import FSO
from AFH_SIM import CAFH_Frames
from Drive import objDut
from Servo import CServoOpti
import MessageHandler as objMsg
from AFH_constants import *
from PowerControl import objPwrCtrl
from Temperature import CTemperature
from AFH_manageHeaters import CAFH_manageActiveHeaters
from SampleMonitor import TD
import MathLib


if testSwitch.extern.AFH_MAJ_REL_NUM >= 21:
   objMsg.printMsg("using st135Params_AFH_v%s 135 params file" % ( testSwitch.extern.AFH_MAJ_REL_NUM ))
   Utility.CUtility().getCodeVersion("st135Params_AFH_v%s.py" % ( testSwitch.extern.AFH_MAJ_REL_NUM ))
   fileNameToImport = "st135Params_AFH_v%s" % (testSwitch.extern.AFH_MAJ_REL_NUM)
elif testSwitch.extern.AFH_MAJ_REL_NUM in [18,20]:
   objMsg.printMsg("using st135Params 135 params file")
   Utility.CUtility().getCodeVersion("st135Params.py")
   fileNameToImport = "st135Params"
else:
   ScrCmds.raiseException(11044, "No valid 135 param file found")


if testSwitch.FE_0135882_409401_CONTINUE_T135_FROM_FAIL_DRIVE == 1:
   from Failcode import getFailCodeAndDesc

INVALID_TRACK_NUMBER = -99999
XHEATER_CLR_DELTA_EXCEEDED = 42197  #/ * AFH- Cross heater clearance delta exceeded. */
INDEX_INTO_HEAD_ELEMENT_OF_RETRY = 1

if testSwitch.FE_AFH3_TO_IMPROVE_TCC or testSwitch.FE_AFH4_TO_USE_TWO_ZONES_TCC:
   AFH3_CLR_VS_AFH2_DELTA_PASSED = 15001 
   AFH4_TEST_TWO_ZONE_PASSED  = 15002
   if testSwitch.KARNAK :
      AFH3_CLR_VS_AFH2_DELTA_PASSED = 15003 
      AFH4_TEST_TWO_ZONE_PASSED  = 15004
   if testSwitch.TRUNK_BRINGUP or testSwitch.ROSEWOOD7: # trunk/RW EC different for AFH3_CLR_VS_AFH2_DELTA_PASSED & AFH4_TEST_TWO_ZONE_PASSED
      AFH3_CLR_VS_AFH2_DELTA_PASSED = 48879
      AFH4_TEST_TWO_ZONE_PASSED  = 48878

class CAFH_test135(CProcess):
   def __init__(self):
      CProcess.__init__(self)
      self.dut = objDut

      # libraries to link in.
      self.frm = CAFH_Frames()
      self.mFSO = FSO.CFSO()

      self.headList = range(objDut.imaxHead)   # note imaxHead is the number of heads

      # variables to initialize
      if (testSwitch.FE_0159597_357426_DSP_SCREEN == 1):
         stateTableName = self.dut.nextState
         if stateTableName == "AFH1_DSP":
            objMsg.printMsg("DSPTruthValue AFH2 is %x" % TD.Truth)
            self.headList = TD.Truth

      self.AFH_State = AFH_UNINITIALIZED_AFH_STATE
      self.PRODUCTION_MODE = ON

      self.AFH_State = self.frm.set_AFH_StateFromStateTableStateName()
      self.spcID = int(self.AFH_State * 10000)   # this statement must be after setting the internal AFH State

      if testSwitch.FE_0136197_341036_AFH_SPECIAL_SPC_ID_FOR_STATE_AFH2B == 1:
         stateTableName = self.dut.nextState
         if stateTableName == "AFH2B":
            self.spcID = int(6 * 10000)   # encode SPC_ID = 60000 for AFH state 2B

      self.unitTest = {}
      self.unitTest['mainLoopOutput'] = []
      self.unitTest['mainLoopAllTestsOutput'] = []
      self.unitTest['mainLoopErrorCode'] = []
      if testSwitch.virtualRun == 1:
         self.unitTest['errorCode'] = [0 for i in xrange(0,1000)] + [14555 for i in xrange(23)]

      testSwitch.getmd5SumForAFH_flags()
      if ( testSwitch.extern.AFH_MAJ_REL_NUM == 0 ) and ( testSwitch.extern.AFH_MIN_REL_NUM == 0 ):
         objMsg.printMsg("AFH Release 0.0 Detected.  Most likely caused by SF3 flg.py file not loaded.  Fail.")
         ScrCmds.raiseException(11044, 'Invalid AFH Release Number 0.0 detected!')  # should never execute this
      self.retry_t135 = ['0' for i in range(self.dut.imaxHead)]


      if testSwitch.FE_0136598_341036_AFH_PRVNT_INDX_ERROR_P_135_FINAL_CONTACT == 1:
         self.numRowsInP135_FINAL_CONTACT_BufferBeforeCurrentCall = 0
      self.AFH_error = ()

      self.objHtrManager = CAFH_manageActiveHeaters()
      self.headRetryStack = []
      if testSwitch.FE_AFH3_TO_IMPROVE_TCC == 1 or testSwitch.FE_AFH4_TO_USE_TWO_ZONES_TCC == 1 or testSwitch.FE_AFH3_TO_DO_BURNISH_CHECK == 1:
          self.reAFH3_error = {}
          self.reAFH3_heads = []
          for iHead in self.headList:
              self.reAFH3_error[iHead] = -1 #0
      self.ReAFH3_for_burnish = 0

   def __del__(self):
      del self.frm 
      del self.mFSO
      
   def updateRequiredAFH_Tables(self, spc_id = -1):
      # 3. zone table
      self.mFSO.getZoneTable()


   ########################################################################################################################
   #
   #               Function:  set_AFH_error and raise_AFH_error
   #
   #        Original Author:  Michael T. Brady
   #
   #            Description:  A mechanism to allow for suppressing and then raising AFH errors.
   #
   #          Prerrequisite:  None
   #
   #                  Input:  errorCode, errorString
   #
   #           Return Value:  None
   #
   ########################################################################################################################
   def set_AFH_error(self, errorCode, errorString):
      if (self.AFH_error == () and self.suppress_AFH_errors != DISABLE):
         objMsg.printMsg('Fatal Script Error Occurred!!!')
         objMsg.printMsg('Error Code: %s (%s) is being suppressed until after all FH contact values have been measured.' \
            % (str(errorCode), str(errorString)))
         self.AFH_error = (errorCode, errorString)

      if (self.suppress_AFH_errors == DISABLE):
         ScrCmds.raiseException(errorCode, errorString)


   def raise_AFH_error(self,):
      if self.AFH_error != ():
         ScrCmds.raiseException(self.AFH_error[0], self.AFH_error[1])


   #######################################################################################################################
   #
   #               Function:  findClearance_st135
   #
   #        Original Author:  Michael T. Brady
   #
   #            Description:  The new main loop for test 135.
   #
   #          Prerrequisite:  MDW_CALs at a minimum
   #
   #                  Input:  heatSearchParams is a dictionary of parameters only required for OCLIM setting
   #
   #           Return  Type:  Integer
   #
   #           Return Value:  None
   #
   #######################################################################################################################
   def findClearance_st135(self, heatSearchParams ):
      """
          Function:  findClearance_st135

   Original Author:  Michael T. Brady

       Description:  Python wrapper to call test 135 and update required PF3 data structures, including the AFH frames stack

     Prerrequisite:  MDW Cals

             Input:

      Return Value:  None

      """
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      if not testSwitch.ROSEWOOD7 and (testSwitch.FE_AFH3_TO_IMPROVE_TCC == 1 or testSwitch.FE_AFH4_TO_USE_TWO_ZONES_TCC == 1):
         objMsg.printMsg("display clr")
         self.displayClearanceAndHeatUsingTest172AndSaveRAPtoFLASH( self.spcID )
      # relevant initializations
      self.updateRequiredAFH_Tables(self.spcID)
      self.frm.readFramesFromCM_SIM()

      stateName = self.dut.nextState[-4:]

      if (not testSwitch.AFH2_FAIL_BURNISH_RERUN_AFH1) or (not self.dut.BurnishFailedHeads):
         self.frm.removePreviousStateInformationIfItExists(stateName)   # This is in to allow retries to work properly.  
         self.frm.writeFramesToCM_SIM()
         self.frm.readFramesFromCM_SIM()


      self.frm.display_frames()
      self.spcID = int(self.AFH_State * 10000)   # this statement must be after setting the internal AFH State

      objMsg.printMsg("HeadType - self.dut.HGA_SUPPLIER: %s" % ( self.dut.HGA_SUPPLIER ))


      # Measure many zones standard set-up

      # run test 135
      objMsg.printMsg("Send standard call to start test 135")
      headRetryCounter = 0
      iHead_local = 0

      baseIPD2Prm_135 = {}
      if testSwitch.FE_AFH3_TO_DO_BURNISH_CHECK == 1 and self.AFH_State == 3 :
         self.mFSO.getAFHWorkingAdaptives(self.spcID + 30, self.dut.numZones)
      if testSwitch.FE_0143000_341036_AFH_CONS_CHK_3RD_GEN_PHASE_2 == 1:
         self.st135_stateMachine( baseIPD2Prm_135, [ AFH_MODE, AFH_MODE_TEST_135_INTERPOLATED_DATA ]  )  # since this runs both W+H and HO, only call it once per acutuation mode
      else:
         self.st135_noStateMachine( baseIPD2Prm_135, [ AFH_MODE, AFH_MODE_TEST_135_INTERPOLATED_DATA ]  )  # since this runs both W+H and HO, only call it once per acutuation mode
      if testSwitch.FE_AFH3_TO_IMPROVE_TCC == 1 or testSwitch.FE_AFH4_TO_USE_TWO_ZONES_TCC == 1 or testSwitch.FE_AFH3_TO_DO_BURNISH_CHECK == 1:
         objMsg.printMsg("FE_AFH3_TO_DO_BURNISH_CHECK %d %s" %(self.AFH_State, str(self.reAFH3_error)))
      if testSwitch.FE_AFH3_TO_DO_BURNISH_CHECK == 1 and self.AFH_State == 3 and self.dut.AFH3FailBurnish == 0:
          objMsg.printMsg("FE_AFH3_TO_DO_BURNISH_CHECK %d %s" %(self.AFH_State, str(self.reAFH3_error)))
          for iHead in self.headList:
              if self.reAFH3_error[iHead] != AFH3_CLR_VS_AFH2_DELTA_PASSED:
                self.ReAFH3_for_burnish = 1
                objMsg.printMsg("FE_AFH3_TO_DO_BURNISH_CHECK %d %s" %(self.ReAFH3_for_burnish, str(self.reAFH3_error)))
                self.st135_stateMachine( baseIPD2Prm_135, [ AFH_MODE, AFH_MODE_TEST_135_INTERPOLATED_DATA ]  )               
                break      
      if testSwitch.FE_0135882_409401_CONTINUE_T135_FROM_FAIL_DRIVE == 1:
         self.suppress_AFH_errors = DISABLE  #enable AFH errors again.
         self.raise_AFH_error()
      if not testSwitch.ROSEWOOD7 and (testSwitch.FE_AFH3_TO_IMPROVE_TCC == 1 or testSwitch.FE_AFH4_TO_USE_TWO_ZONES_TCC == 1):
         self.displayClearanceAndHeatUsingTest172AndSaveRAPtoFLASH( self.spcID + 1000)
      if testSwitch.FE_AFH3_TO_DO_BURNISH_CHECK == 1 and self.AFH_State == 3 :
         self.mFSO.getAFHWorkingAdaptives(self.spcID + 50, self.dut.numZones)
      # end of findClearance_st135


   #######################################################################################################################
   #
   #               Function:  findClearance_V3BAR
   #
   #        Original Author:  Michael T. Brady
   #
   #            Description:  Find Contact using 135 for V3BAR purposes only.
   #
   #          Prerrequisite:  MDW_CALs at a minimum
   #
   #                  Input:  iHead(int)
   #
   #                 Return:  None
   #
   #######################################################################################################################
   def findClearance_V3BAR(self, iHead, iTrack ):
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

      # relevant initializations
      self.AFH_State = stateTableToAFH_internalStateNumberTranslation['V3BAR']
      self.spcID = int(self.AFH_State * 10000)   # this statement must be after setting the internal AFH State
      self.updateRequiredAFH_Tables(self.spcID)

      # This may not be necessary, but is a good precaution.
      self.frm.readFramesFromCM_SIM()
      stateName = self.dut.nextState[-4:]
      self.frm.removePreviousStateInformationIfItExists(stateName)   # This is in to allow retries to work properly.
      self.frm.writeFramesToCM_SIM()
      self.frm.readFramesFromCM_SIM()
      self.frm.display_frames()

      # run test 135
      objMsg.printMsg("HeadType - self.dut.HGA_SUPPLIER: %s" % ( self.dut.HGA_SUPPLIER ))
      objMsg.printMsg("Send standard call to start test 135")
      headRetryCounter = 0

      dut = self.dut
      headType = dut.HGA_SUPPLIER
      benchMode = 0  # 0=disabled. This should ALWAYS be disabled for production.

      if testSwitch.FE_0139633_341036_AFH_NEW_PROGRAM_NAME_FUNCTION == 1:
         from ProgramName import getProgramNameGivenTestSwitch
         programName = getProgramNameGivenTestSwitch( testSwitch )
      else:
         programName = TP.program


      #
      enableFAFH = testSwitch.FE_0151344_341036_FAFH_ENABLE_T135_FAFH_SPECIFIC_PARAMS

      iConsistencyCheckRetry = 0
      baseIPD2Prm_135 =    __import__("%s" % ( fileNameToImport )).getSelfTest135Dictionary(
                                             self.AFH_State,  headRetryCounter,       programName,
                                             "WRITER_HEATER", iHead,                  dut.servoWedges,
                                             dut.rpm,         headType,               dut.AABType,
                                             dut.numZones,    dut.isDriveDualHeater,  testSwitch.virtualRun,
                                             benchMode,       enableFAFH,             iConsistencyCheckRetry )

      # not going to call the llogicalTrackToNominalTrack translation as in V3BAR before VBAR nominal = logical

      NUM_HEAD_RETRIES = getattr(TP,'Test135_numHeadRetries', 3)

      heaterElement = "WRITER_HEATER"
      self.run135_forSingleHead( iHead, baseIPD2Prm_135, NUM_HEAD_RETRIES, iTrack, heaterElement, iConsistencyCheckRetry )

      # end of findClearance_V3BAR


   #######################################################################################################################
   #
   #               Function:  st135_noStateMachine  (legacy code to drive test135 contact detection)
   #
   #        Original Author:  D. Martin
   #
   #            Description:  Do the following:
   #                          1. set-up to run test 135
   #                          2. call test 135
   #                          3. issue global retries if necessary.
   #                          4. save AFH information to the AFH SIM file
   #
   #          Prerrequisite:  OCLIM needs to be opened to 200% track using test 11
   #
   #                  Input:  None
   #
   #           Return  Type:  Integer
   #
   #           Return Value:  None
   #
   #######################################################################################################################
   def st135_noStateMachine(self, baseIPD2Prm_135, listOfAFHModesToSaveBasedOnTest135Data ):

      # This belongs in the test Parameter file

      iConsistencyCheckRetry = 0
      NUM_HEAD_RETRIES = getattr(TP,'Test135_numHeadRetries', 3)

      if testSwitch.FE_0135882_409401_CONTINUE_T135_FROM_FAIL_DRIVE == 1:
         self.suppress_AFH_errors = ENABLE  # suppress all AFH errors until end of st135.
         self.attrName = 'P135_'+ self.dut.nextState +'_RETRY'
         self.dut.driveattr[self.attrName] = ''

      try:
         self.dut.dblData.delTable('P135_SEARCH_RESULTS')
         objMsg.printMsg("st135/ P135_SEARCH_RESULTS table successfully deleted.")
      except:
         objMsg.printMsg("st135/ Call to delete DBLog table P135_SEARCH_RESULTS failed!!!")

      #LUL Xloop after Power Cycle before T135
      if testSwitch.FE_0149438_395340_P_LUL_BEFORE_RUN_AFH:
         if self.AFH_State in TP.AFH_LUL['AFH_State']:
            self.LULxLoop(loopCount = TP.AFH_LUL['loop'])
         else:
            objMsg.printMsg("AFH%d don't need %dx LUL."% (self.AFH_State,TP.AFH_LUL['loop']))
      if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT == 1:
         for iHead in self.headList:
            if testSwitch.AFH2_FAIL_BURNISH_RERUN_AFH1:
              if self.dut.BurnishFailedHeads: #rerun becos burnish check fail
                 if iHead not in self.dut.BurnishFailedHeads: #test only failed heads
                   objMsg.printMsg("bypass burnish-pass head: %s not in dut.BurnishFailedHeads %s"  % (str(iHead), str(self.dut.BurnishFailedHeads)))
                   continue
            for heaterElement in self.dut.heaterElementList:
               if testSwitch.FE_AFH3_TO_IMPROVE_TCC == 1 or testSwitch.FE_AFH4_TO_USE_TWO_ZONES_TCC == 1:
                  errorCode = self.run135_forSingleHead( iHead, baseIPD2Prm_135, NUM_HEAD_RETRIES, INVALID_TRACK_NUMBER, heaterElement, iConsistencyCheckRetry )
               else:
                     self.run135_forSingleHead( iHead, baseIPD2Prm_135, NUM_HEAD_RETRIES, INVALID_TRACK_NUMBER, heaterElement, iConsistencyCheckRetry )
               if testSwitch.FE_AFH3_TO_IMPROVE_TCC == 1 or testSwitch.FE_AFH4_TO_USE_TWO_ZONES_TCC == 1:
                  objMsg.printMsg("errorcode=%d" %errorCode)
                  if errorCode in [AFH3_CLR_VS_AFH2_DELTA_PASSED, AFH4_TEST_TWO_ZONE_PASSED]:
                     self.reAFH3_error[iHead] = AFH3_CLR_VS_AFH2_DELTA_PASSED

               if testSwitch.FE_0135882_409401_CONTINUE_T135_FROM_FAIL_DRIVE == 1 and self.AFH_error != ():
                  objMsg.printMsg("Skip saveTest135DataToFramesData!!!")
                  pass
               else:
                  if testSwitch.FE_AFH3_TO_IMPROVE_TCC == 1 or testSwitch.FE_AFH4_TO_USE_TWO_ZONES_TCC == 1:
                     if self.reAFH3_error[iHead] in [AFH3_CLR_VS_AFH2_DELTA_PASSED, AFH4_TEST_TWO_ZONE_PASSED]:
                        self.reAFH3_error[iHead] = 0
                        break
                     else:
                        for afhMode in listOfAFHModesToSaveBasedOnTest135Data:
                           objMsg.printMsg("st135/ calling saveTest135DataToFramesData for Hd: %s, afhMode: %s, heaterElement: %s"  % ( iHead, afhMode, heaterElement  ))
                           self.saveTest135DataToFramesData( iHead, baseIPD2Prm_135, afhMode, heaterElement )

                  else:
                     for afhMode in listOfAFHModesToSaveBasedOnTest135Data:
                        objMsg.printMsg("st135/ calling saveTest135DataToFramesData for Hd: %s, afhMode: %s, heaterElement: %s"  % ( iHead, afhMode, heaterElement  ))
                        self.saveTest135DataToFramesData( iHead, baseIPD2Prm_135, afhMode, heaterElement )
                  # end of for loop

      else:

         for iHead in self.headList:
            if testSwitch.AFH2_FAIL_BURNISH_RERUN_AFH1:
              if self.dut.BurnishFailedHeads: #rerun becos burnish check fail
                 if iHead not in self.dut.BurnishFailedHeads: #test only failed heads
                   objMsg.printMsg("bypass burnish-pass head: %s not in dut.BurnishFailedHeads %s"  % (str(iHead), str(self.dut.BurnishFailedHeads)))
                   continue
            if testSwitch.FE_AFH3_TO_IMPROVE_TCC == 1 or testSwitch.FE_AFH4_TO_USE_TWO_ZONES_TCC == 1:
               errorCode = self.run135_forSingleHead( iHead, baseIPD2Prm_135, NUM_HEAD_RETRIES, INVALID_TRACK_NUMBER, "WRITER_HEATER", iConsistencyCheckRetry )
            else:
               self.run135_forSingleHead( iHead, baseIPD2Prm_135, NUM_HEAD_RETRIES, INVALID_TRACK_NUMBER, "WRITER_HEATER", iConsistencyCheckRetry )

            if testSwitch.FE_AFH3_TO_IMPROVE_TCC == 1 or testSwitch.FE_AFH4_TO_USE_TWO_ZONES_TCC == 1:
               objMsg.printMsg("errorcode=%d" %errorCode)
               if errorCode in [AFH3_CLR_VS_AFH2_DELTA_PASSED, AFH4_TEST_TWO_ZONE_PASSED]:
                  self.reAFH3_error[iHead] = AFH3_CLR_VS_AFH2_DELTA_PASSED

            if testSwitch.FE_0135882_409401_CONTINUE_T135_FROM_FAIL_DRIVE == 1 and self.AFH_error != ():
               objMsg.printMsg("Skip saveTest135DataToFramesData!!!")
               pass
            else:

               if testSwitch.FE_AFH3_TO_IMPROVE_TCC == 1 or  testSwitch.FE_AFH4_TO_USE_TWO_ZONES_TCC == 1:
                  if self.reAFH3_error[iHead] != AFH3_CLR_VS_AFH2_DELTA_PASSED:
                     self.reAFH3_error[iHead] = 0
                     self.reAFH3_heads.append(iHead)
                     for afhMode in listOfAFHModesToSaveBasedOnTest135Data:
                        objMsg.printMsg("st135/ calling saveTest135DataToFramesData for Hd: %s, and Mode: %s"  % (iHead, afhMode))
                        self.saveTest135DataToFramesData( iHead, baseIPD2Prm_135, afhMode )
               else:
                  for afhMode in listOfAFHModesToSaveBasedOnTest135Data:
                     objMsg.printMsg("st135/ calling saveTest135DataToFramesData for Hd: %s, and Mode: %s"  % (iHead, afhMode))
                     self.saveTest135DataToFramesData( iHead, baseIPD2Prm_135, afhMode )
               # end of for iHead in self.headList

      if testSwitch.FE_0135882_409401_CONTINUE_T135_FROM_FAIL_DRIVE == 1:
         self.suppress_AFH_errors = DISABLE # enable AFH errors again.
         self.raise_AFH_error()

      if not (testSwitch.FE_0121797_341036_AFH_USE_T109_FOR_TEST_135_TRACK_CLEANUP == 1):
         self.saveTest135AFH_CleanUpTracksToDUTObject()
      #

      # add code from the refactor to support backwards compatibility here.

      if self.AFH_State in AFH_LIST_STATES_TO_UPDATE_CERT_TEMP:
         numRetries = 0
         temp = CTemperature()

         temp.setCERTTemp(temp.retHDATemp(0, numRetries, TP.tempDiodeMultRtry['driveTempDiodeRangeLimit']))
      # Note contents of RAP need to be committed to flash at this point.

      self.displayClearanceAndHeatUsingTest172AndSaveRAPtoFLASH( self.spcID ) # saving RAP to flash here

      if testSwitch.FE_0130770_341036_AFH_FORCE_SAVING_AFH_SIM_TO_DRIVE_ETF == 1:
         if not (self.AFH_State in [ stateTableToAFH_internalStateNumberTranslation['AFH1'],
                                     stateTableToAFH_internalStateNumberTranslation['AFH4']   ]):

            if self.AFH_State == stateTableToAFH_internalStateNumberTranslation['AFH3'] and testSwitch.IS_FAFH:
               #tweak via t172 before saving the sim file to the drive
               self.St(TP.AFH_Display_Working_Preamp_Adaptives_Table_Prm_172, spc_id=self.spcID)

            self.frm.SaveSIMFilesToDrive_ETF()

      # end of st135()


   #######################################################################################################################
   #
   #               Function:  st135_stateMachine
   #
   #            Description:  Runs the T135 PF3 state machine to provide for retry conditions
   #
   #          Prerrequisite:
   #
   #                  Input:  None
   #
   #           Return  Type:  Integer
   #
   #           Return Value:  None
   #
   #######################################################################################################################
   def st135_stateMachine(self, baseIPD2Prm_135, listOfAFHModesToSaveBasedOnTest135Data ):

      NUM_HEAD_RETRIES = getattr(TP,'Test135_numHeadRetries', 3)
      NUM_CONS_CHK_RETRIES = getattr(TP,'Test135_numConsistencyCheckRetries', 3)
      GLOBAL_RETRY_LIMIT = 1000

      self.objHtrManager.setActiveHeaters( self.AFH_State )

      state = 'start'
      consChkRetryDict = {}  # this need to be by head though!
      nDict = {}
      heaterElement = ''
      iHead = 0

      originalSPC_ID = self.spcID

      n=0
      while (state != 'end'):
         n += 1
         if n > GLOBAL_RETRY_LIMIT:
            ScrCmds.raiseException(14800, 'Consistency Check exceeded global maximum retry limit of %d' % (GLOBAL_RETRY_LIMIT))


         if state == 'start':

            # This belongs in the test Parameter file

            try:
               self.dut.dblData.delTable('P135_SEARCH_RESULTS')
               objMsg.printMsg("st135/ P135_SEARCH_RESULTS table successfully deleted.")
            except:
               objMsg.printMsg("st135/ Call to delete DBLog table P135_SEARCH_RESULTS failed!!!")

            if testSwitch.FE_0135882_409401_CONTINUE_T135_FROM_FAIL_DRIVE == 1:
               self.suppress_AFH_errors = ENABLE  # suppress all AFH errors until end of st135.
               self.attrName = 'P135_'+ self.dut.nextState +'_RETRY'
               self.dut.driveattr[self.attrName] = ''

            #
            objMsg.printMsg("st135_stateMachine/ Starting state machine.")

            self.headRetryStack = []
            if (testSwitch.FE_0159597_357426_DSP_SCREEN == 1):
               stateTableName = self.dut.nextState

            if (testSwitch.FE_0159597_357426_DSP_SCREEN == 1) and (stateTableName == "AFH1_DSP"):
               iHead = TD.Truth
               consChkRetryDict[ iHead ] = 0
               nDict[ iHead ] = 0
               for heaterElement in self.dut.heaterElementList:
                  self.headRetryStack.append([ heaterElement, iHead ])
               self.headRetryStack.reverse()
            else:
               for iHead in self.headList:
                  if (testSwitch.AFH2_FAIL_BURNISH_RERUN_AFH1 and self.AFH_State in [stateTableToAFH_internalStateNumberTranslation['AFH1'],  stateTableToAFH_internalStateNumberTranslation['AFH2']]) or (testSwitch.FE_AFH3_TO_DO_BURNISH_CHECK and self.AFH_State == stateTableToAFH_internalStateNumberTranslation['AFH3']):
                     if self.dut.BurnishFailedHeads: #rerun becos burnish check fail
                        if iHead not in self.dut.BurnishFailedHeads: #test only failed heads
                           objMsg.printMsg("bypass burnish-pass head: %s not in dut.BurnishFailedHeads %s"  % (str(iHead), str(self.dut.BurnishFailedHeads)))
                           continue
                        elif self.AFH_State == stateTableToAFH_internalStateNumberTranslation['AFH1']:
                           # Indicating reAFH2
                           if 'RE_AFH2' in TP.Proc_Ctrl30_Def:
                              self.dut.driveattr['PROC_CTRL30'] = '0X%X' % (int(self.dut.driveattr.get('PROC_CTRL30', '0'),16) | TP.Proc_Ctrl30_Def['RE_AFH2'])
                              if testSwitch.FE_0359619_518226_REAFH2AFH3_BYHEAD_SCREEN:
                                 objMsg.printMsg("re-AFH2 head: %s" % str(iHead))
                                 self.dut.driveattr['RE_AFH2_HEAD'] = str(int(self.dut.driveattr.get('RE_AFH2_HEAD', '0')) | 1<<iHead)                             
                     if testSwitch.FE_AFH3_TO_IMPROVE_TCC == 1 or testSwitch.FE_AFH4_TO_USE_TWO_ZONES_TCC == 1 or testSwitch.FE_AFH3_TO_DO_BURNISH_CHECK == 1:
                        if (self.AFH_State == stateTableToAFH_internalStateNumberTranslation['AFH3']) and self.reAFH3_error[iHead] == AFH3_CLR_VS_AFH2_DELTA_PASSED:
                           objMsg.printMsg("bypass reAFH3 Passed head: %s error %s"  % (str(iHead), str(self.reAFH3_error)))
                           continue
                  if testSwitch.ENABLE_TCC_RESET_BY_HEAD_BEFORE_AFH4:
                     if self.dut.TccResetHeadList: #
                        if iHead in self.dut.TccResetHeadList: 
                           objMsg.printMsg("bypass TccReset head: %s not in dut.TccResetHeadList %s"  % (str(iHead), str(self.dut.TccResetHeadList)))
                           continue
                  consChkRetryDict[ iHead ] = 0
                  nDict[ iHead ] = 0
                  for heaterElement in self.dut.heaterElementList:
                     self.headRetryStack.append([ heaterElement, iHead ])
               self.headRetryStack.reverse()

            if testSwitch.FE_0163822_341036_AFH_DISABLE_VCAT_FOR_T135 == 1:
               state = 'disableVCAT'
            else:
               state = 'doMoreMeasurementsNeedToBeMade'

         if state == 'disableVCAT':
            # disable servo vcat and chrome here.
            self.St(TP.vCatGoRealPrm_47)
            state = 'doMoreMeasurementsNeedToBeMade'

         if state == 'doMoreMeasurementsNeedToBeMade':
            if not (self.headRetryStack == []):
               state = 'clearFramesDataForCurrentMeasurement'

               # if changing head number then clear the by head counters
               nextHeadToMeasure_B = self.headRetryStack[-1][1]
               if nextHeadToMeasure_B != iHead:
                  # clear all counters related to by head measurements.
                  self.spcID = originalSPC_ID


            else:
               state = 'FinishedWithAllHeadsAndStartCleanUpSequence'



         # clear goes here
         if state == 'clearFramesDataForCurrentMeasurement':
            # need to clear frames

            iPos = len(self.frm.dPesSim.DPES_FRAMES) - 1
            while iPos >= 0:
               frame = self.frm.dPesSim.DPES_FRAMES[iPos]
               if (frame['stateIndex'] == self.AFH_State) and (frame['LGC_HD'] == iHead) and ( frame['Heater Element'] == heaterElement ):
                  self.frm.dPesSim.DPES_FRAMES.pop(iPos)
               iPos -= 1
            self.frm.dPesSim.DPES_HEADER.set('NumFrames', len(self.frm.dPesSim.DPES_FRAMES) )

            state = 'makeNext135Measurement'

         self.CurrentT135Code = TEST_PASSED
         if state == 'makeNext135Measurement':
            [ heaterElement, iHead ] = self.headRetryStack.pop()
            iConsistencyCheckRetry = consChkRetryDict[ iHead ]
            errorCode = self.run135_forSingleHead( iHead, baseIPD2Prm_135, NUM_HEAD_RETRIES, INVALID_TRACK_NUMBER, heaterElement, iConsistencyCheckRetry )
            self.CurrentT135Code = errorCode
            if testSwitch.FE_AFH3_TO_IMPROVE_TCC == 1 or testSwitch.FE_AFH4_TO_USE_TWO_ZONES_TCC == 1 or testSwitch.FE_AFH3_TO_DO_BURNISH_CHECK == 1:
               objMsg.printMsg("errorcode=%d" %errorCode)
               if testSwitch.FE_AFH3_TO_IMPROVE_TCC == 1 and self.AFH_State == stateTableToAFH_internalStateNumberTranslation['AFH3'] and errorCode == TEST_PASSED:
                  self.reAFH3_error[iHead] = 0
               if  testSwitch.FE_AFH3_TO_DO_BURNISH_CHECK and self.AFH_State == stateTableToAFH_internalStateNumberTranslation['AFH3'] :
                   if errorCode == TEST_PASSED:
                       self.reAFH3_error[iHead] = 0
                       self.reAFH3_heads.append(iHead)
               if errorCode in [AFH3_CLR_VS_AFH2_DELTA_PASSED, AFH4_TEST_TWO_ZONE_PASSED]:
                  if self.reAFH3_error[iHead] != 0:
                     self.reAFH3_error[iHead] = AFH3_CLR_VS_AFH2_DELTA_PASSED
                  errorCode = TEST_PASSED
            nDict[ iHead ] += 1
            state = 'saveDataToFrames'


         if state == 'saveDataToFrames':
            objMsg.printMsg("reafh3errorcode0=%d" %testSwitch.FE_AFH3_TO_IMPROVE_TCC)
            if testSwitch.FE_AFH3_TO_IMPROVE_TCC == 1 :
               objMsg.printMsg("reafh3errorcode=%d AFHerror=%s T135EC=%d" %(self.reAFH3_error[iHead], str(self.AFH_error), self.CurrentT135Code))
            if self.AFH_error != ():
               objMsg.printMsg("Skip saveTest135DataToFramesData!!!")
               ## !! What to do with this case?!  We should skip saving the frames and consistency check and simply re-measure!
               state = 'doMoreMeasurementsNeedToBeMade'
            else:
               if testSwitch.FE_AFH3_TO_IMPROVE_TCC == 1 or testSwitch.FE_AFH4_TO_USE_TWO_ZONES_TCC == 1 or testSwitch.FE_AFH3_TO_DO_BURNISH_CHECK:
                  if (testSwitch.FE_AFH3_TO_DO_BURNISH_CHECK and self.ReAFH3_for_burnish == 1 and self.AFH_State == 3) or  ( self.CurrentT135Code != AFH3_CLR_VS_AFH2_DELTA_PASSED) :                                        
                     for afhMode in listOfAFHModesToSaveBasedOnTest135Data :
                        objMsg.printMsg("st135/ calling saveTest135DataToFramesData for Hd: %s, afhMode: %s, heaterElement: %s"  % ( iHead, afhMode, heaterElement  ))
                        self.saveTest135DataToFramesData( iHead, baseIPD2Prm_135, afhMode, heaterElement )
                     if self.AFH_State == stateTableToAFH_internalStateNumberTranslation['AFH3']:
                        # Indicating full AFH3
                        if 'FULL_AFH3' in TP.Proc_Ctrl30_Def:
                           self.dut.driveattr['PROC_CTRL30'] = '0X%X' % (int(self.dut.driveattr.get('PROC_CTRL30', '0'),16) | TP.Proc_Ctrl30_Def['FULL_AFH3'])
                           #if re-AFH2 and re-AFH3 happen on same head, fail the drv
                           objMsg.printMsg("re-AFH3 head: %s" % str(iHead))
                           if testSwitch.FE_0359619_518226_REAFH2AFH3_BYHEAD_SCREEN and (int(self.dut.driveattr.get('RE_AFH2_HEAD', '0')) & 1<<iHead):
                              ScrCmds.raiseException(14559, "Head: %s triggered both re-AFH2 and re-AFH3, fail the drv " % str(iHead))
                  # end of for iHead in self.headList
                     #self.reAFH3_error[iHead] = 0
                  else:
                      objMsg.printMsg("REAFH3 Skip saveTest135DataToFramesData!!!")

               else:
                  for afhMode in listOfAFHModesToSaveBasedOnTest135Data:
                     objMsg.printMsg("st135/ calling saveTest135DataToFramesData for Hd: %s, afhMode: %s, heaterElement: %s"  % ( iHead, afhMode, heaterElement  ))
                     self.saveTest135DataToFramesData( iHead, baseIPD2Prm_135, afhMode, heaterElement )
               state = 'needToRunConsistencyCheck'

               #
               if (testSwitch.FE_0158373_341036_ENABLE_AFH_LIN_CAL_BEFORE_READER_HEATER == 1):
                  state = 'runLinearizationCal'
               else:
                  state = 'needToRunConsistencyCheck'
               #
         #
         if state == 'runLinearizationCal':

            listOfAFHStatesForLinearizationCal = [1]

            if (heaterElement == "WRITER_HEATER") and \
               (errorCode == 0) and \
               (self.AFH_State in listOfAFHStatesForLinearizationCal):

               # run the linearization cal.
               oSrvOpti = CServoOpti()
               oSrvOpti.servoLinCal_AFH(TP.servoLinCalPrm_150, iHead )

               # need to save linearization cal results in SAP to flash
               self.mFSO.saveRAPSAPtoFLASH()


               # need to re-enable ZAP if after AFH2
               s0 = "AFH Main/_servocal state: %s,             servo linear cal, head: %s                                                             " % \
                     (self.AFH_State, iHead)
               objMsg.printMsg(s0)
               self.unitTest['mainLoopAllTestsOutput'].append(s0)

            #
            state = 'needToRunConsistencyCheck'


         if state == 'needToRunConsistencyCheck':

            numberOfActiveHeaters = len(self.objHtrManager.getActiveHeaters())

            if (self.AFH_State in getattr(TP,'allowedAFH_statesToRunConsistencyCheckList', [1,2]) ) and \
               (self.dut.isDriveDualHeater == 1) and \
               (nDict[ iHead ] >= numberOfActiveHeaters ):
               state = 'doWeNeedToRetry'
            else:
               state = 'doMoreMeasurementsNeedToBeMade'


         if state == 'doWeNeedToRetry':
            headStatus = errorCode
            if (headStatus != OK):
               # are there any measurements left for this head?  if so then let them proceed?
               if self.AnyMeasurementsLeftForThisHead(iHead) == True:
                  state = 'doMoreMeasurementsNeedToBeMade'
               else:
                  state = 'areRetriesExceeded'
            else:
               # headStatus == OK
               if consChkRetryDict[ iHead ] >= 1:
                  self.removeRetriesForThisHeadIfTheyExist(iHead)
               state = 'doMoreMeasurementsNeedToBeMade'

         if state == 'areRetriesExceeded':
            if ((consChkRetryDict[ iHead ] >= NUM_CONS_CHK_RETRIES) and (heaterElement == "READER_HEATER")) or \
               (consChkRetryDict[ iHead ] >= NUM_CONS_CHK_RETRIES + 1):
               objMsg.printMsg("st135_stateMachine/ Consistency Check retries exceeded.")
               objMsg.printDblogBin(self.dut.dblData.Tables('P_AFH_DH_CONSISTENCY_CHK'))
               ScrCmds.raiseException(14800, 'Consistency Check between writer and reader heater Failed')
            else:
               state = 'requestMeasurementsToRetry'


         if state == 'requestMeasurementsToRetry':
            requestREADER_HEATER_retry = 0
            requestWRITER_HEATER_retry = 0

            self.spcID += 10     # increase SPC_ID for consistency check retry
            consChkRetryDict[ iHead ] += 1

            if self.objHtrManager.areBothHeatersActive():
               # if on the 2nd retry re-do the WRITER_HEATER as well
               if consChkRetryDict[ iHead ] >= 2:
                  requestWRITER_HEATER_retry = 1
            else:
               requestWRITER_HEATER_retry = 1


            #  Standard READER_HEATER retry.
            if (self.dut.isDriveDualHeater == 1):
               if (self.AFH_State in self.objHtrManager.getDisableREADER_HEATER_inAFH_stateList()):
                  if ( consChkRetryDict[ iHead ] >= 2 ):
                     requestREADER_HEATER_retry = 1
               else:
                  requestREADER_HEATER_retry = 1

            if (requestWRITER_HEATER_retry + requestREADER_HEATER_retry) == 0:
               ScrCmds.raiseException(11044, 'AFH Main Loop state machine.  Should never happen.  Retries required but no retries requested.')  # should never execute this


            state = 'addMoreMeasurements'
            # end of if state == 'requestMeasurementsToRetry':

         if state == 'addMoreMeasurements':
            if requestREADER_HEATER_retry == 1:
               retryREADER_HEATER = [ "READER_HEATER", iHead ]
               if not (retryREADER_HEATER in self.headRetryStack):
                  self.headRetryStack.append(retryREADER_HEATER)    # these should all be the same variable and in scope.
               objMsg.printMsg("ConsistencyCheck3rdGen/ Adding retry for Hd: %s, retry Num: %d" % ( iHead, consChkRetryDict[ iHead ] ))


            if requestWRITER_HEATER_retry == 1:
               retryWRITER_HEATER = [ "WRITER_HEATER", iHead ]
               if not (retryWRITER_HEATER in self.headRetryStack):
                  self.headRetryStack.append(retryWRITER_HEATER)    # these should all be the same variable and in scope.
               objMsg.printMsg("ConsistencyCheck3rdGen/ Adding retry for Hd: %s, retry Num: %d" % ( iHead, consChkRetryDict[ iHead ] ))

            state = 'doMoreMeasurementsNeedToBeMade'

         if state == 'FinishedWithAllHeadsAndStartCleanUpSequence':
            state = 'oldEnd'

         if state == 'oldEnd':
            # display this once at the true end
            objMsg.printDblogBin(self.dut.dblData.Tables('P_AFH_DH_CONSISTENCY_CHK'))

            self.suppress_AFH_errors = DISABLE # enable AFH errors again.
            self.raise_AFH_error()

            if not (testSwitch.FE_0121797_341036_AFH_USE_T109_FOR_TEST_135_TRACK_CLEANUP == 1):
               self.saveTest135AFH_CleanUpTracksToDUTObject()

            state = 'saveCERT_temperature'

         if state == 'saveCERT_temperature':
            from Temperature import CTemperature

            if self.AFH_State in AFH_LIST_STATES_TO_UPDATE_CERT_TEMP:
               numRetries = 0
               temp = CTemperature()

               temp.setCERTTemp(temp.retHDATemp(0, numRetries, TP.tempDiodeMultRtry['driveTempDiodeRangeLimit']))
            # Note contents of RAP need to be committed to flash at this point.
            state = 'displayClearanceAndHeatUsingTest172AndSaveRAPtoFLASH'


         if state == 'displayClearanceAndHeatUsingTest172AndSaveRAPtoFLASH':
            self.displayClearanceAndHeatUsingTest172AndSaveRAPtoFLASH( self.spcID ) # saving RAP to flash here

            if testSwitch.FE_0163822_341036_AFH_DISABLE_VCAT_FOR_T135 == 1:
               state = 'reEnableVCAT'
            else:
               state = 'saveAFH_SIM_dataToDriveETF'

         if state == 'reEnableVCAT':

            # enable VCAT virtual mode ON and chrome on.
            self.St(TP.vCatOn_47)
            state = 'saveAFH_SIM_dataToDriveETF'

         if state == 'saveAFH_SIM_dataToDriveETF':
            if testSwitch.FE_0130770_341036_AFH_FORCE_SAVING_AFH_SIM_TO_DRIVE_ETF == 1:
               if not (self.AFH_State in [ stateTableToAFH_internalStateNumberTranslation['AFH1'],
                                           stateTableToAFH_internalStateNumberTranslation['AFH4']   ]):

                  if self.AFH_State == stateTableToAFH_internalStateNumberTranslation['AFH3'] and testSwitch.IS_FAFH:
                     #tweak via t172 before saving the sim file to the drive
                     self.St(TP.AFH_Display_Working_Preamp_Adaptives_Table_Prm_172)

                  if testSwitch.FE_0280534_480505_DETCR_ON_OFF_BECAUSE_SERVO_DISABLE_DETCR_BY_DEFAULT:
                     # needed due to M10P servo code, servo code disables DETCR by default so DETCR on/off commands need to be called before and after using DETCR
                     oSrvOpti = CServoOpti()
                     oSrvOpti.St(TP.setDetcrOffPrm_011)
                     oSrvOpti.St({'test_num':178, 'prm_name':'Save SAP in RAM to FLASH', 'CWORD1':0x420})
                  self.frm.SaveSIMFilesToDrive_ETF()

            state = 'end'

         if state == 'end':
            pass


   #######################################################################################################################
   #
   #               Function:  removeRetriesForThisHeadIfTheyExist
   #
   #            Description:  Remove Any retries if they exist.
   #
   #                  Input:  iHead2(int)
   #
   #                 Return:  boolean
   #
   #######################################################################################################################
   def removeRetriesForThisHeadIfTheyExist(self, iHead2):
      self.headRetryStack = filter(lambda retry: retry[ INDEX_INTO_HEAD_ELEMENT_OF_RETRY ] != iHead2, self.headRetryStack)


   #######################################################################################################################
   #
   #               Function:  AnyMeasurementsLeftForThisHead
   #
   #            Description:  Decide if there are any remaining measurements for this head.
   #
   #                  Input:  iHead2(int)
   #
   #                 Return:  boolean
   #
   #######################################################################################################################
   def AnyMeasurementsLeftForThisHead(self, iHead2):
      retriesForThisHeadList = filter(lambda retry: retry[ INDEX_INTO_HEAD_ELEMENT_OF_RETRY ] == iHead2, self.headRetryStack)
      if len(retriesForThisHeadList) > 0:
         return True
      else:
         return False


   #######################################################################################################################
   #
   #               Function:  run135_forSingleHead
   #
   #            Description:  Run 135 for a single head
   #
   #          Prerrequisite:
   #
   #                  Input:  iHead(int)
   #
   #                 Return:  None
   #
   #######################################################################################################################
   def run135_forSingleHead( self, iHead, baseIPD2Prm_135, NUM_HEAD_RETRIES, iTrack, heaterElement, iConsistencyCheckRetry ):
      headRetryCounter = 0
      ec = TEST_PASSED + 1  # set to not TEST_PASSED
      spc_idHeadRetry = 0

      listPassedErrorCodes = [TEST_PASSED, XHEATER_CLR_DELTA_EXCEEDED ]

      if testSwitch.FE_AFH3_TO_IMPROVE_TCC == 1 :
         listPassedErrorCodes.append( AFH3_CLR_VS_AFH2_DELTA_PASSED)
      if testSwitch.FE_AFH4_TO_USE_TWO_ZONES_TCC == 1:
         listPassedErrorCodes.append( AFH4_TEST_TWO_ZONE_PASSED )

      while ( not ( ec in listPassedErrorCodes )):

         dut = self.dut
         headType = dut.HGA_SUPPLIER
         benchMode = 0  # 0=disabled. This should ALWAYS be disabled for production.

         if testSwitch.FE_0139633_341036_AFH_NEW_PROGRAM_NAME_FUNCTION == 1:
            from ProgramName import getProgramNameGivenTestSwitch
            programName = getProgramNameGivenTestSwitch( testSwitch )
         else:
            programName = TP.program

         enableFAFH = testSwitch.FE_0151344_341036_FAFH_ENABLE_T135_FAFH_SPECIFIC_PARAMS

         baseIPD2Prm_135 =    __import__("%s" % ( fileNameToImport )).getSelfTest135Dictionary(
                                                   self.AFH_State,  headRetryCounter,       programName,
                                                   heaterElement,   iHead,                  dut.servoWedges,
                                                   dut.rpm,         headType,               dut.AABType,
                                                   dut.numZones,    dut.isDriveDualHeater,  testSwitch.virtualRun,
                                                   benchMode,       enableFAFH,             iConsistencyCheckRetry, dut.PREAMP_TYPE, dut.PREAMP_REV, dut.HSA_WAFER_CODE )
         baseIPD2Prm_135["HEAD_RANGE"] = (iHead<<8) + iHead

         if  testSwitch.FE_AFH3_TO_DO_BURNISH_CHECK == 1 and self.AFH_State == 3 and (self.ReAFH3_for_burnish == 1 or self.dut.AFH3FailBurnish >= 1):
              NO_CTRL1_REAFH3 = 0xF7FF
              l_detcr = list(baseIPD2Prm_135['DETCR_CD'])
              l_detcr[1] &= NO_CTRL1_REAFH3
              baseIPD2Prm_135['DETCR_CD'] = tuple(l_detcr)
              NO_CWORD3_BY_EXCEPTION = 0xFFFB
              baseIPD2Prm_135["CWORD3"]     &= NO_CWORD3_BY_EXCEPTION 
               
         if iTrack != INVALID_TRACK_NUMBER:
            baseIPD2Prm_135["TEST_CYL"] = self.oUtility.ReturnTestCylWord( iTrack )


         if (headRetryCounter > NUM_HEAD_RETRIES):
            if testSwitch.virtualRun == 1:
               break
            if testSwitch.FE_0135882_409401_CONTINUE_T135_FROM_FAIL_DRIVE == 1:
               self.dut.driveattr[self.attrName] = self.dut.driveattr[self.attrName]+'F'
               ec = failureData[0][2]
               erCode135, erMsg135 = getFailCodeAndDesc(ec)
               self.set_AFH_error(erCode135, erMsg135)
               break
            else:
               if (testSwitch.AFH2_FAIL_BURNISH_RERUN_AFH1 and self.AFH_State == stateTableToAFH_internalStateNumberTranslation['AFH2']) or (testSwitch.FE_AFH3_TO_DO_BURNISH_CHECK and self.AFH_State == stateTableToAFH_internalStateNumberTranslation['AFH3']):
                  if ec in TP.AFH2_RETRYFROM_AFH1_ERROR_CODE:
                     self.dut.BurnishFailedHeads.append(iHead)

               raise   # go ahead and fail the drive here; should fail for a test 135 unique error code
               ScrCmds.raiseException(11044, 'Test 135 failed after retries')  # should never execute this


         #
         try:
            self.dut.dblData.delTable('P135_FINAL_CONTACT')
            objMsg.printMsg("st135/ All Test 135 Data successfully deleted.")
         except:
            objMsg.printMsg("st135/ Call to delete DBLog table P135_FINAL_CONTACT failed!!!")

         try:
            p135Tbl = self.dut.dblData.Tables('P135_FINAL_CONTACT').tableDataObj()
            if testSwitch.FE_0136598_341036_AFH_PRVNT_INDX_ERROR_P_135_FINAL_CONTACT == 1:
               if testSwitch.virtualRun == 1:
                  # data is not actively being collected so this is needed for VE to pass
                  self.numRowsInP135_FINAL_CONTACT_BufferBeforeCurrentCall = 0
               else:
                  self.numRowsInP135_FINAL_CONTACT_BufferBeforeCurrentCall = len( p135Tbl )
            objMsg.printMsg("P135_FINAL_CONTACT should be empty. len(p135Tbl): %s" % (str(len(p135Tbl))))
         except:
            objMsg.printMsg("Call to get P135_FINAL_CONTACT data failed.")


         try:

            baseIPD2Prm_135["SPC_ID"] = self.spcID + spc_idHeadRetry
            if (testSwitch.AFH2_FAIL_BURNISH_RERUN_AFH1 and self.AFH_State == stateTableToAFH_internalStateNumberTranslation['AFH2']) or (testSwitch.FE_AFH3_TO_DO_BURNISH_CHECK and self.AFH_State == stateTableToAFH_internalStateNumberTranslation['AFH3']):
               if iHead in self.dut.BurnishFailedHeads:
                   baseIPD2Prm_135["SPC_ID"] += 1000
                   

            if not testSwitch.FE_0236367_357260_P_REMOVE_REDUNDANT_T135_PARAM_DISPLAY:
                objMsg.printMsg("test135 parameter dictionary immediately before self.St() call" )
                self.displayTest135Dictionary( TEST135_DISPLAY_DICTIONARY_AND_VERTICAL_SORTED_KEYS, baseIPD2Prm_135 )
            self.St(baseIPD2Prm_135)
            ec = TEST_PASSED
            if testSwitch.FE_0135882_409401_CONTINUE_T135_FROM_FAIL_DRIVE == 1:
               self.dut.driveattr[self.attrName] = self.dut.driveattr[self.attrName]+str(headRetryCounter)

            if testSwitch.virtualRun == 1:
               if 'errorCode' in self.unitTest.keys():
                  if not len(self.unitTest['errorCode']) == 0:
                     ec = self.unitTest['errorCode'].pop()
                  else:
                     ec = 0
            if (testSwitch.ENABLE_MIN_HEAT_RECOVERY == 1) and \
               (self.AFH_State == 1) and \
               (iHead not in self.dut.BurnishFailedHeads) and \
               (headType in ["TDK", "HWY"]):
               objMsg.printMsg("testSwitch.ENABLE_MIN_HEAT_RECOVERY = %d." % testSwitch.ENABLE_MIN_HEAT_RECOVERY)
               objMsg.printMsg("ENABLE_MIN_HEAT_RECOVERY is enabled.")

               #process AFH1 data here
               listWrtDacInterpolated = []
               #p135Tbl = dut.dblData.Tables('P135_FINAL_CONTACT').tableDataObj()
               p135Tbl = dut.dblData.Tables('P135_FINAL_CONTACT').chopDbLog('SPC_ID', 'match',str(baseIPD2Prm_135["SPC_ID"]))

               for entry in p135Tbl:
                  if (entry.get('MSRD_INTRPLTD') == AFH_TEST135_INTERPOLATED_SYMBOL) and \
                     (iHead == int(entry.get('HD_LGC_PSN'))):
                     listWrtDacInterpolated.append(int(entry.get('WRT_CNTCT_DAC')))
               
               objMsg.printMsg("listWrtDacInterpolated len %d." % len(listWrtDacInterpolated))
               objMsg.printMsg("listWrtDacInterpolated %s." % listWrtDacInterpolated)

               MinInterpolatedDAC = min(listWrtDacInterpolated)
               objMsg.printMsg("Head:%d, minInterploateDac:%d" %(iHead,MinInterpolatedDAC))
               if not testSwitch.FE_0334525_348429_INTERPOLATED_DEFAULT_TRIPLET:
                  DefaultIw, DefaultOvs, DefaultOvd = TP.VbarWpTable[dut.PREAMP_TYPE]['ALL'][2]
               else:
                  try:
                     DefaultIw, DefaultOvs, DefaultOvd = TP.VbarWpTable[dut.PREAMP_TYPE]['ALL'][2]
                  except:
                     DefaultIw, DefaultOvs, DefaultOvd = TP.VbarWpTable[dut.PREAMP_TYPE]['OD'][2]
               if iHead in dut.MaxIwByAFH.keys():
                  CurrentIw = min(DefaultIw, dut.MaxIwByAFH[iHead])
               else:
                  CurrentIw = DefaultIw
               #self.St({'test_num':172,'prm_name':"Retrieve WP's",'CWORD1':12, 'timeout':100, 'spc_id':1234})
               #CurrentWpTbl = dut.dblData.Tables('P172_WRITE_POWERS').chopDbLog('SPC_ID', 'match','1234')
               #for entry in CurrentWpTbl:
               #   if iHead == int(entry['HD_LGC_PSN']):
               #      CurrentIw = int(entry['WRT_CUR'])
               #      break
               objMsg.printMsg("Head:%d, DefaultIw:%d" %(iHead,DefaultIw))
               objMsg.printMsg("Head:%d, CurrentIw:%d" %(iHead,CurrentIw))
               #CurrentIw = min(CurrentIw, DefaultIw)
               #if MinInterpolatedDAC < TP.MinimumHeatRecoverySpec['MIN_DAC_REQUIRED'] and CurrentIw > TP.MinimumHeatRecoverySpec['MIN_IW_REQUIRED']:
               redoT135ForThisHd = 0
               if MinInterpolatedDAC < TP.MinimumHeatRecoverySpec['MIN_DAC_REQUIRED']:
                  newIw = int(CurrentIw + (MinInterpolatedDAC - TP.MinimumHeatRecoverySpec['MIN_DAC_REQUIRED'])/TP.MinimumHeatRecoverySpec['IW_DAC_SLOPE'])
                  objMsg.printMsg("Head:%d, newIw should be:%d" %(iHead,newIw))

                  if newIw != CurrentIw and CurrentIw > TP.MinimumHeatRecoverySpec['MIN_IW_REQUIRED']:
                     if newIw < TP.MinimumHeatRecoverySpec['MIN_IW_REQUIRED']:
                        newIw = TP.MinimumHeatRecoverySpec['MIN_IW_REQUIRED']
                        redoT135ForThisHd = 1
                        objMsg.printMsg("Head:%d, newIw is cap at:%d" %(iHead,newIw))

                  if redoT135ForThisHd == 1:
                     objMsg.printMsg("******Head:%d Faild MinDac required:%d, will retry with new Iw:%d******" %(iHead, TP.MinimumHeatRecoverySpec['MIN_DAC_REQUIRED'],newIw))
                     prm = {'test_num': 178, 'prm_name': 'prm_wp_178', 'timeout': 1200, 'spc_id': 0,}
                     prm.update({
                        'prm_name'             : "Set WP",
                        'CWORD1'               : 0x0200,
                        'CWORD2'               : 0x1107,
                        'BIT_MASK'             : (0xFFFF, 0xFFFF),
                        'HEAD_RANGE'           : 2**iHead,
                        'WRITE_CURRENT'        : newIw,
                        'DAMPING'              : DefaultOvs,
                        'DURATION'             : DefaultOvd,
                        })
                     self.St(prm)
                     self.mFSO.saveRAPtoFLASH()
                     ec = TEST_PASSED + 1   # force global retry
                     spc_idHeadRetry += 10
                     self.dut.MaxIwByAFH[iHead]= newIw
                     try:
                        self.dut.objData.update({'MaxIwByAFH':self.dut.MaxIwByAFH})  
                     except:
                        objMsg.printMsg("Fail to save MaxIwByAFH to objdata")
                     #objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
                     self.St({'test_num':172,'prm_name':"Retrieve WP's",'CWORD1':12, 'timeout':100, 'spc_id':0})

         except ScriptTestFailure, (failureData):
            try: ec = failureData[0][2]
            except: ec = -1
            objMsg.printMsg('st135/ ec: %s' % str(ec), objMsg.CMessLvl.VERBOSEDEBUG)

            if ec in [AFH_ERROR_CODE_DAC_MAXED_OUT]:
               if testSwitch.FE_0135882_409401_CONTINUE_T135_FROM_FAIL_DRIVE == 1:
                  self.dut.driveattr[self.attrName] = self.dut.driveattr[self.attrName]+'F'
                  erCode135, erMsg135 = getFailCodeAndDesc(ec)
                  self.set_AFH_error(erCode135, erMsg135)
                  break
               else:
                  raise
            if not (self.AFH_State == 3 and testSwitch.FE_AFH3_TO_IMPROVE_TCC and (not testSwitch.FE_AFH3_TO_SAVE_CLEARANCE_TO_RAP)):
               self.mFSO.saveRAPtoFLASH()
            #LUL Xloop after Power Cycle before T135
            if testSwitch.FE_0149438_395340_P_LUL_BEFORE_RUN_AFH:
               if testSwitch.FE_0162917_407749_P_AFH_LUL_FOR_RETRY_BY_ERROR_CODE:
                  if self.AFH_State in TP.AFH_LUL['AFH_State'] and ec in TP.AFH_LUL['AFH_EC_LIST']:
                     self.dut.driveattr['10X_LUL_T135'] = 'FAIL'
                     self.LULxLoop(loopCount = TP.AFH_LUL['loop'])
                     self.dut.driveattr['10X_LUL_T135'] = 'DONE'
                  else:
                     objMsg.printMsg("AFH%d ec: %d don't need %dx LUL for retry."% (self.AFH_State,ec,TP.AFH_LUL['loop']))
                     objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
               else:
                  if self.AFH_State in TP.AFH_LUL['AFH_State']:
                     self.dut.driveattr['10X_LUL_T135'] = 'FAIL'
                     self.LULxLoop(loopCount = TP.AFH_LUL['loop'])
                     self.dut.driveattr['10X_LUL_T135'] = 'DONE'
                  else:
                     objMsg.printMsg("AFH%d don't need %dx LUL for retry."% (self.AFH_State,TP.AFH_LUL['loop']))
                     objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
            else:
               objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

         headRetryCounter += 1
         spc_idHeadRetry += 100

         s0 = "AFH Main/ test 135 state: %s, heaterElement: %s, head: %s, hd retry: %s, cons retry: %s, spc_id: %s, errorCode: %5s                  %s" % \
            (self.AFH_State, heaterElement, iHead, headRetryCounter, iConsistencyCheckRetry, baseIPD2Prm_135["SPC_ID"], ec, self.headRetryStack)
         self.unitTest['mainLoopOutput'].append(s0)
         self.unitTest['mainLoopAllTestsOutput'].append(s0)
         objMsg.printMsg(s0)

         # Attempt to clean debris off the head
         if testSwitch.FE_0145432_325269_P_CLEAN_OFF_HEAD_DEBRI == 1:
            objMsg.printMsg("Cleaning debris off Head: %d" % (iHead))
            tmp = TP.prm_084_RandomSeeks.copy()
            tmp['TEST_HEAD'] = iHead                                    ##Clean this head
            try:
               self.St( tmp )
            except:
               objPwrCtrl.powerCycle(5000,12000,10,10, useESlip=1)      ## Any failure ... go ahead and power cycle so we can continue. Should be temporary?
               pass

         # end of while loop
      #

      if (testSwitch.FE_0158373_341036_ENABLE_AFH_LIN_CAL_BEFORE_READER_HEATER == 1):
         # should this only happen if ec == 0?
         self.mFSO.saveRAPtoFLASH()
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)


      #

      CTemperature().getCellTemperature()

      return ec

   #######################################################################################################################
   #
   #               Function:  displayMainLoopDebug
   #
   #        Original Author:  Michael T. Brady
   #
   #            Description:  A nice summary table to display the AFH Main loop controls
   #
   #          Prerrequisite:  None
   #
   #                  Input:  None
   #
   #                Return :  None
   #
   #######################################################################################################################
   def displayMainLoopDebug(self,):

      objMsg.printMsg("len(self.unitTest['mainLoopOutput']) : %s" % ( len(self.unitTest['mainLoopOutput'])))
      for n,s0 in enumerate(self.unitTest['mainLoopOutput']):
         objMsg.printMsg("%s" % ( s0 ))


   #######################################################################################################################
   #
   #               Function:  displayTest135Dictionary
   #
   #        Original Author:  Michael T. Brady
   #
   #            Description:  display the test 135 dictionary
   #
   #                  Input:  displayLevel, baseIPD2Prm_135(dict)
   #
   #                 Output:  None
   #
   #######################################################################################################################
   def displayTest135Dictionary(self, displayLevel, baseIPD2Prm_135):

      keys = baseIPD2Prm_135.keys()
      keys.sort()

      for key in keys:
         objMsg.printMsg("[%s] = %s" % ( key, baseIPD2Prm_135[key] ))


   #######################################################################################################################
   #
   #               Function:  getSortedListOfAllValidZonesTestedFromTest135
   #
   #        Original Author:  Michael T. Brady
   #
   #            Description:  get a list of all valid zones from test 135 DBLog data.
   #
   #          Prerrequisite:  running test 135
   #
   #                  Input:  iHead(int), typeTest135Data(string) I or M data
   #
   #                Return :  is measurement invalid (boolean)
   #
   #######################################################################################################################
   def getSortedListOfAllValidZonesTestedFromTest135( self, iHead, typeTest135Data, p135Tbl, heaterElement ):
      zonesTested = []

      for i in range(0, len(p135Tbl)):
         zn = int(p135Tbl[i]['DATA_ZONE'])

         if self.isTest135MeasurementInvalid( p135Tbl[i], heaterElement ) == True:
            continue # skip this data.

         if (
               (iHead == int(p135Tbl[i]['HD_LGC_PSN'])) and \
               (typeTest135Data == p135Tbl[i]['MSRD_INTRPLTD']) and \
               (zn not in zonesTested)
            ):
            zonesTested.append(zn)

      # I'm intentionally sorting the zone list to ensure that the zones appear in order in the SIM file.
      # If this were not the case test 49 will completely fall apart.
      zonesTested.sort()
      return zonesTested


   #######################################################################################################################
   #
   #               Function:  isTest135MeasurementInvalid
   #
   #        Original Author:  Michael T. Brady
   #
   #            Description:  determine if the test 135 data is valid or not.
   #
   #                          Validity in this case currently means measured data where contact was declared for both W+H and HO
   #
   #          Prerrequisite:  running test 135
   #
   #                  Input:  dbLogRowFromTest135 (list technically... a row of DBLog data from test 135)
   #
   #                Return :  is measurement invalid (boolean)
   #
   #######################################################################################################################
   def isTest135MeasurementInvalid(self, dbLogRowFromTest135, heaterElement):
      detectorMaskContactNotDeclared = 0


      htrOnlyDetectionMask = (int(dbLogRowFromTest135['DETECTOR_MASK']) >> 8) & 0x00FF
      wrtHeatDetectionMask = int(dbLogRowFromTest135['DETECTOR_MASK']) & 0x00FF

      if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT == 1:

         listAFHStatesIgnoreWPH_DetectorMask = [2,3,4]

         listAFHStatesIgnoreWPH_DetectorMask.append(1)
         listAFHStatesIgnoreWPH_DetectorMask.append(2)

         if ((self.AFH_State in listAFHStatesIgnoreWPH_DetectorMask) and \
            ( dbLogRowFromTest135['MSRD_INTRPLTD'] == AFH_TEST135_MEASURED_SYMBOL ) and \
            ( heaterElement == "READER_HEATER" )):

            if ( htrOnlyDetectionMask == detectorMaskContactNotDeclared ):
               return True
            else:
               return False

      if ( dbLogRowFromTest135['MSRD_INTRPLTD'] == AFH_TEST135_MEASURED_SYMBOL ) and (( wrtHeatDetectionMask == detectorMaskContactNotDeclared ) or ( htrOnlyDetectionMask == detectorMaskContactNotDeclared )):
         return True
      else:
         return False


   #######################################################################################################################
   #
   #               Function:  saveTest135DataToFramesData
   #
   #        Original Author:  Michael T. Brady
   #
   #            Description:  save test 135 data to AFH SIM file a.k.a. the "frames" data
   #
   #          Prerrequisite:  running test 135
   #
   #                  Input:  iHead - head number (int), baseIPD2Prm_135 or test 135 parameters (dictionary),
   #
   #           Return  Type:  None
   #
   #           Return Value:  None
   #
   #######################################################################################################################
   def saveTest135DataToFramesData( self, iHead, baseIPD2Prm_135, afhMode, heaterElement = "WRITER_HEATER" ):
      # 1. determine what type of data to save in the AFH SIM file
      # determine based on the requested afhMode, if "I" or "M" test 135 data needs to be pulled.

      # if this is interpolated set to new AFH mode for only test 49 to use (screens will ignore this data),
      # otherwise if this is measured data set the standard AFH mode of 0
      if afhMode == AFH_MODE_TEST_135_INTERPOLATED_DATA:
         typeTest135Data = AFH_TEST135_INTERPOLATED_SYMBOL
      elif afhMode == AFH_MODE:
         typeTest135Data = AFH_TEST135_MEASURED_SYMBOL
      elif afhMode == AFH_MODE_TEST_135_EXTREME_ID_OD_DATA:
         typeTest135Data = AFH_TEST135_MEASURED_SYMBOL
      else:
         ScrCmds.raiseException(11044, "saveTest135DataToFramesData/ afhMode: %s" % ( afhMode ))


      # 1B. read in the data.
      self.frm.clearFrames()  # clear active frames data for a fresh read.
      self.frm.readFramesFromCM_SIM()
      p135Tbl = self.dut.dblData.Tables('P135_FINAL_CONTACT').tableDataObj()


      # 2. filter
      zonesTested = self.getSortedListOfAllValidZonesTestedFromTest135( iHead, typeTest135Data, p135Tbl, heaterElement )

      if afhMode == AFH_MODE_TEST_135_INTERPOLATED_DATA:
         self.frm.dPesSim.DPES_HEADER['Measurements Per Head'] = len(zonesTested)
      consistCheckIndex = 0 # no python retries
      if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT == 1:
         if heaterElement == "WRITER_HEATER":
            consistCheckIndex = WRITER_HEATER_INDEX
         else:
            consistCheckIndex = READER_HEATER_INDEX

      # update AFH Frames data
      detectorMaskContactNotDeclared = 0

      iPos = 0
      for zn in zonesTested:
         # force looking at the last data first.  Should (not does) fix  PDD-0112933: Marina IPD2 Bringup: 100% fail for EC14740
         if testSwitch.FE_0136598_341036_AFH_PRVNT_INDX_ERROR_P_135_FINAL_CONTACT == 1:
            endLoop = self.numRowsInP135_FINAL_CONTACT_BufferBeforeCurrentCall
         else:
            endLoop = 0

         for i in range( len(p135Tbl) - 1, endLoop - 1, -1):
            p135TblRow = p135Tbl[i]
            if (
                  (iHead == int(p135TblRow['HD_LGC_PSN'])) and \
                  (typeTest135Data == p135TblRow['MSRD_INTRPLTD']) and \
                  (zn == int(p135TblRow['DATA_ZONE']))
               ):

               iTemp = int(p135TblRow['CONTACT_TEMP'])
               if (testSwitch.virtualRun == 1) and (self.AFH_State == 4):
                  iTemp -= 25

               if self.isTest135MeasurementInvalid( p135TblRow, heaterElement ) == True:
                  continue # skip this data.

               htrOnlyDetectionMask = (int(p135TblRow['DETECTOR_MASK']) >> 8) & 0x00FF
               wrtHeatDetectionMask = int(p135TblRow['DETECTOR_MASK']) & 0x00FF

               if not (testSwitch.FE_0140570_357263_T135_HEAT_ONLY_FULL_SEARCH == 1):
                  # negative values forced back into a 1-byte unsigned value are interpreted as large not small.
                  if ( p135TblRow['MSRD_INTRPLTD'] == AFH_TEST135_INTERPOLATED_SYMBOL ) and (int(p135TblRow['WRT_CNTCT_DAC']) < 0):
                     ScrCmds.raiseException( 14839, "Write contact DAC :%s, less than 0" )

                  if ( p135TblRow['MSRD_INTRPLTD'] == AFH_TEST135_INTERPOLATED_SYMBOL ) and (int(p135TblRow['RD_CNTCT_DAC']) < 0):
                     ScrCmds.raiseException( 14839, "Read  contact DAC :%s, less than 0" )

               self.frm.dPesSim.addMeasurement(afhMode, self.dut.nextState[-4:], self.AFH_State, consistCheckIndex,
                  iHead,  # this should be interpreted as logical head
                  int(p135TblRow['DATA_ZONE']),
                  int(p135TblRow['TRK_NUM']),
                  iPos,
                  iTemp,
                  int(p135TblRow['WRT_CNTCT_DAC']),
                  int(p135TblRow['RD_CNTCT_DAC']),
                  float(p135TblRow['RD_CLR']) / angstromsScaler,
                  float(p135TblRow['WRT_CLR']) / angstromsScaler,
                  float(p135TblRow['WRT_LOSS']) / angstromsScaler,
                  )
               iPos += 1
               break
               # end of if
            # end of while
         # end of for zn in zonesTested:

      self.frm.display_frames(1)

      if (testSwitch.FE_0159597_357426_DSP_SCREEN == 1):
         stateTableName = self.dut.nextState

      if ((testSwitch.FE_0159597_357426_DSP_SCREEN == 1) and (stateTableName == "AFH1_DSP")):
         objMsg.printMsg("tested head %d" % iHead)
      else:
         if len(self.frm.dPesSim.DPES_FRAMES) == 0:
            ScrCmds.raiseException(11044, 'No Frames data written after test 135 finished!')

      if testSwitch.FE_0328119_322482_P_SAVE_AFH_CERT_TEMP_TO_FIS:
          if self.AFH_State == 2:
             minTempInAFH = self.frm.getMinimumTemp(2)
             DriveAttributes['PRIMARY_TEMP']   = minTempInAFH
             DriveAttributes['SECONDARY_TEMP'] = minTempInAFH
             objMsg.printMsg("save AFH mini temperature %d" % minTempInAFH)
          if self.AFH_State == 3:
             minTempInAFH = self.frm.getMinimumTemp(3)
             DriveAttributes['SECONDARY_TEMP'] = minTempInAFH
             objMsg.printMsg("save AFH mini temperature %d" % minTempInAFH)

      self.frm.writeFramesToCM_SIM()


   #######################################################################################################################
   #
   #               Function:  get135ResultsForV3BAR
   #
   #        Original Author:  Michael T. Brady
   #
   #            Description:  get the 135 results for V3BAR use only.
   #
   #          Prerrequisite:  running test 135
   #
   #                  Input:
   #
   #                 Return:  contactDAC(int), rdClr(float)
   #
   #######################################################################################################################
   def get135ResultsForV3BAR(self, ):
      p135Tbl = self.dut.dblData.Tables('P135_FINAL_CONTACT').tableDataObj()
      p135TblRow = p135Tbl[ -1 ]

      contactDAC = p135TblRow['RD_CNTCT_DAC']
      rdClr = float(p135TblRow['RD_CLR']) / angstromsScaler

      return contactDAC, rdClr


   #######################################################################################################################
   #
   #               Function:  saveTest135AFH_CleanUpTracksToDUTObject
   #
   #        Original Author:  Michael T. Brady
   #
   #            Description:  save test 135 head and track numbers to be cleaned-up by F3 code diags to DUT object
   #
   #          Prerrequisite:  running test 135
   #
   #                  Input:  None
   #
   #           Return  Type:  status(int)
   #
   #######################################################################################################################
   def saveTest135AFH_CleanUpTracksToDUTObject(self, ):
      objMsg.printMsg("saveTest135AFH_CleanUpTracksToDUTObject/ In AFH State %s " % (self.AFH_State) )
      AFH_STATE_NUMBER_INTENDED_TO_CLEAN_UP_TEST_135_TRACKS = 4

      AFH_StateToCleanUp = [ getattr(TP, 'AFH_statesToCleanUpTest135Tracks', AFH_STATE_NUMBER_INTENDED_TO_CLEAN_UP_TEST_135_TRACKS) ]

      objMsg.printMsg("saveTest135AFH_CleanUpTracksToDUTObject/ In AFH State %s, AFH_StateToCleanUp: %s " % ( self.AFH_State, AFH_StateToCleanUp ) )

      if self.AFH_State in AFH_StateToCleanUp:
         from AFH import CAFH_AR_Shared_Functions

         OAFH_AR_Shared_Functions = CAFH_AR_Shared_Functions()
         try:
            if testSwitch.extern.FE_0123864_357621_T135_NEW_SEARCH_RESULTS_TABLE:
               p135SrchRes = self.dut.dblData.Tables('P135_SEARCH_RESULTS_DAC').tableDataObj()
            else:
               p135SrchRes = self.dut.dblData.Tables('P135_SEARCH_RESULTS').tableDataObj()
         except:
            p135SrchRes = []
         # the status of the flag below will overwrite p135SrchRes = [] generated above.
         if testSwitch.extern.FE_0211321_454766_REPORT_TRACK_INFO_IN_T135_BEFORE_CONTACT_DETECT:
            objMsg.printMsg("Capture test trks using P135_USED_TRACK_INFO table.")
            try:
               p135SrchRes1 = self.dut.dblData.Tables('P135_USED_TRACK_INFO').tableDataObj()
            except:
               objMsg.printMsg("Tbl P135_USED_TRACK_INFO not found")
               p135SrchRes1 = []
               
            for row in p135SrchRes1:
               logicalHead = int(row['HD_LGC_PSN'])
               logicalTrk = int(row['TRK_NUM'])
               OAFH_AR_Shared_Functions.logTestTracks( logicalHead , logicalTrk )
               
         if testSwitch.virtualRun == 1:
            if 'forceCustomSearchResultsTable' in self.unitTest:
               if self.unitTest['forceCustomSearchResultsTable'] == 1:
                  p135SrchRes = self.unitTest['customSearchResultsTable']
         
         # Log all tracks notes in SEARCH_RESULTS
         if testSwitch.extern.FE_0123864_357621_T135_NEW_SEARCH_RESULTS_TABLE:
            objMsg.printMsg("Capture test trks using P135_SEARCH_RESULTS_DAC table.")
         else:
            objMsg.printMsg("Capture test trks using P135_SEARCH_RESULTS table.")
         for row in p135SrchRes:
            logicalHead = int(row['HD_LGC_PSN'])
            logicalTrk = int(row['TRK_NUM'])

            OAFH_AR_Shared_Functions.logTestTracks( logicalHead , logicalTrk )

         if 'LogTest35_Tracks' in self.dut.objData.marshallObject:
            for iHead in self.headList:
               if iHead in self.dut.objData.marshallObject['LogTest35_Tracks']:
                  objMsg.printMsg("saveTest135AFH_CleanUpTracksToDUTObject/ Hd: %s, self.dut.objData.marshallObject['LogTest35_Tracks'] Log Trks: %s " %
                     ( iHead, self.dut.objData.marshallObject['LogTest35_Tracks'][iHead] ) )

      return OK


   #######################################################################################################################
   #
   #               Function:  writeCustomerZeroesToTestedTracksUsingTest109
   #
   #        Original Author:  Michael T. Brady
   #
   #            Description:  For each track that 135 tested write customer readable zeroes to the track and surrounding tracks
   #                          specifiedby the TP.AFH_statesToCleanUpTest135Tracks.
   #                          Note: self-test 109 is used to write custmoer readable zeroes
   #
   #          Prerrequisite:  running test 135
   #
   #                  Input:  None
   #
   #           Return  Type:  status(int)
   #
   #######################################################################################################################
   def writeCustomerZeroesToTestedTracksUsingTest109(self, ):
      objMsg.printMsg("writeCustomerZeroesToTestedTracks/ In AFH State %s " % (self.AFH_State) )

      AFH_StatesToCleanUpList = [ 4 ]
      if not ( self.AFH_State in AFH_StatesToCleanUpList ):
         objMsg.printMsg("writeCustomerZeroesToTestedTracks/ Skipping running of AFH Cleanu-p in AFH State: %s " % (self.AFH_State) )
         return -1

      tracksToPadInAFH_cleanUp = getattr(TP, 'tracksToPadInAFH_cleanUp', 100)

      p135_searchResultsTableName = "P135_SEARCH_RESULTS_DAC"

      try:
         p135SrchRes = self.dut.dblData.Tables( p135_searchResultsTableName ).tableDataObj()
      except:
         p135SrchRes = []

      #P135_SEARCH_RESULTS_DAC:
      #HD_PHYS_PSN HD_LGC_PSN DATA_ZONE TRK_NUM NOM_TRK_NUM RETRY_CNT POLY_ORDER WPH_START WPH_END WPH_CONTACT HO_END HO_CONTACT WPH_ZONE_LIMIT HO_ZONE_LIMIT WPH_INTERVAL HO_INTERVAL ERROR_FLAGS DETECTOR_MASK ACTIVE_HEATER INACTIVE_HEATER_DAC
      #          1          1        29  363182      356699         0          0       120     158           0    158        144              0           183            0           0           0           256             R                   0

      # Log all tracks notes in SEARCH_RESULTS

      objMsg.printMsg("writeCustomerZeroesToTestedTracksUsingTest109/ len(p135SrchRes): %s" % ( len(p135SrchRes) ))
      objMsg.printMsg("writeCustomerZeroesToTestedTracksUsingTest109/ p135SrchRes: %s" % ( p135SrchRes ))

      for row in p135SrchRes:
         logicalHead = int(row['HD_LGC_PSN'])
         logicalTrk = int(row['TRK_NUM'])

         prm_109 = {}
         prm_109.update(TP.prm_109_AFH_CleanUpWriteZeroesToTracks)
         startCyl = int( logicalTrk - tracksToPadInAFH_cleanUp )
         endCyl = int( logicalTrk + tracksToPadInAFH_cleanUp )
         prm_109['START_CYL'] = self.oUtility.ReturnTestCylWord( startCyl ) # should this force the trk to be > 0.!!??
         prm_109['END_CYL'] = self.oUtility.ReturnTestCylWord( endCyl )     # I confirmed with Ray Pacek that 109 code is smart enough to not have to worry about specifying tracks > maxTrack
         prm_109['HEAD_RANGE'] = 2 ** logicalHead

         #
         objMsg.printMsg("writeCustomerZeroesToTestedTracksUsingTest109/ Hd: %2s, Cleaning-up AFH target Logical Trk: %9s, from startCyl: %9s, to Trk : %9s, padding on BOTH sides by: %5s tracks." %
            ( logicalHead, logicalTrk, startCyl, logicalTrk + tracksToPadInAFH_cleanUp, tracksToPadInAFH_cleanUp )  )
         self.St(prm_109)

         # error handling should go here in case T109 can't write the tracks?!


      objMsg.printMsg("writeCustomerZeroesToTestedTracksUsingTest109/ Finished.")

      return OK


   #######################################################################################################################
   #
   #               Function:  displayClearanceAndHeatUsingTest172AndSaveRAPtoFLASH
   #
   #        Original Author:  Michael T. Brady
   #
   #            Description:  Save the RAP to Flash this will commit the clearance numbers in buffer RAP to Flash
   #
   #          Prerrequisite:  running test 135
   #
   #                  Input:  None
   #
   #           Return  Type:  status(int)
   #
   #######################################################################################################################
   def displayClearanceAndHeatUsingTest172AndSaveRAPtoFLASH(self, spcID ):

      listStatesToUpdateClearance = AFH_LIST_STATES_TO_UPDATE_CLEARANCE
      listValidStates = [1, 2, 3, 4, 28, 40, 41, 42, 43]

      if not (self.AFH_State in listValidStates):
         objMsg.printMsg("displayClearanceAndHeatUsingTest172AndSaveRAPtoFLASH/ called from Unknown State: %s, AFH State: %s" % (self.dut.nextState, self.AFH_State))
         ScrCmds.raiseException(11044, 'AFH Update Clearance called from unknown state.')  # should never execute this

      if self.AFH_State in listStatesToUpdateClearance:
         updateClearance = ON
      else:
         updateClearance = OFF
         objMsg.printMsg("skipping calculation of clearance in state: %s" % (self.dut.nextState))
         return -1

      spc_id = spcID + 1
      # if testSwitch.FE_AFH3_TO_IMPROVE_TCC == 1 or testSwitch.FE_AFH4_TO_USE_TWO_ZONES_TCC == 1:

         # spc_id += 100
      if (testSwitch.AFH2_FAIL_BURNISH_RERUN_AFH1 and self.AFH_State == stateTableToAFH_internalStateNumberTranslation['AFH2']) or (testSwitch.FE_AFH3_TO_DO_BURNISH_CHECK and self.AFH_State == stateTableToAFH_internalStateNumberTranslation['AFH3']):
          if self.dut.BurnishFailedHeads:
             spc_id += 1000  

      self.mFSO.getAFHWorkingAdaptives(spc_id, self.dut.numZones)
      self.mFSO.getAFHTargetClearances(spc_id, ST_SUPPRESS__NONE, False)


      if updateClearance == ON:
         objMsg.printMsg("Saving working RAP values including clearance and heater values to FLASH")
         self.mFSO.saveRAPtoFLASH()
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      if testSwitch.FE_AFH3_TO_IMPROVE_TCC != 1 and testSwitch.FE_AFH4_TO_USE_TWO_ZONES_TCC != 1:

         spc_id += 100
         self.mFSO.getAFHWorkingAdaptives(spc_id, self.dut.numZones)
         self.mFSO.getAFHTargetClearances(spc_id, ST_SUPPRESS__NONE, False)


   #######################################################################################################################
   #
   #               Function:  LULxLoop
   #
   #        Original Author:  Sitthipong S.
   #
   #            Description:  PowerCycle 1 time and Use Load UnLoad command x Loop follow parameter.
   #
   #          Prerrequisite:  None
   #
   #                  Input:  None
   #
   #           Return  Type:  None
   #
   #######################################################################################################################
   def LULxLoop(self,loopCount = 1):
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

      if testSwitch.FE_0158023_357260_P_AFH_LOOP_COUNT_BY_STATE and TP.AFH_LUL.has_key('AFH_StateLoops'):
         loopCount = TP.AFH_LUL['AFH_StateLoops'][self.AFH_State]

      for i in range(loopCount):
         self.St(TP.spindownPrm_2)
         self.St(TP.spinupPrm_1)

# ------------------------------------------------->    <--------------------------------------------------
