#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2008, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: AR Module
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/AR2.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/AR2.py#1 $
# Level: 3

#---------------------------------------------------------------------------------------------------------#

##########################################################################################################################
#
# imports
#
##########################################################################################################################

import types
import time

from Constants import *
import MathLib
from AFH_SIM import CAFH_Frames

from array import array
from AFH_constants import *
from Drive import objDut   # usage is objDut
import FSO
import MessageHandler as objMsg
from Process import CProcess
import ScrCmds
import Utility
from TestParamExtractor import TP
from SampleMonitor import TD
from SampleMonitor import CSampMon

##########################################################################################################################
#
# constants
#
##########################################################################################################################

#           CWORD2
#           2  	 x0004  	 WRT_ADJ_TO_FLASH [1:Write Fit W/HIRP adjustment values to RAP FLASH. Default: 0.]
#           1 	x0002 	WRT_ADJ_TO_BUFFER_RAP [1:Write Fit W/HIRP adjustment values to Buffer RAP. Default: 0.]

TEST_191_CWORD2_CLOSED_LOOP_HIRP = 0x0002
# after reviewing the 191 code this also updates the passive clearance as well, but NOT the system area.



##########################################################################################################################
#
# Class CAR
#
##########################################################################################################################

class CAR(CProcess):
   """
      Class for measuring the read and write HIRP slope and offset.
   """
   def __init__(self, ):
      """__init__: Intializes the class level variables.
      """
      CProcess.__init__(self)


      # other class links
      self.frm = CAFH_Frames()
      self.oUtility = Utility.CUtility()
      self.dth = FSO.dataTableHelper()
      self.mth = MathLib.CAFH_Computations()
      self.lmt = MathLib.CDAC_limits()


      self.dut = objDut

      self.mFSO = FSO.CFSO()
      self.mFSO.getZoneTable()

      self.AFH_State = self.frm.set_AFH_StateFromStateTableStateName()
      self.setHIRP_SPC_ID_fromStateTableStateName()

      self.runClosedLoopHIRP = ( self.AFH_State in LIST_VALID_CLOSED_LOOP_HIRP_STATES )


      self.headList = range(objDut.imaxHead)   # getZoneTable()  # needs to be called prior to the init so that this is valid
      testSwitch.getmd5SumForAFH_flags()
      if ( testSwitch.extern.AFH_MAJ_REL_NUM == 0 ) and ( testSwitch.extern.AFH_MIN_REL_NUM == 0 ):
         objMsg.printMsg("AFH Release 0.0 Detected.  Most likely caused by SF3 flg.py file not loaded.  Fail.")
         ScrCmds.raiseException(11044, 'Invalid AFH Release Number 0.0 detected!')  # should never execute this


   #######################################################################################################################
   #
   #               Function:  measureAR
   #
   #        Original Author:  Michael T. Brady
   #
   #            Description:  Main Method in PF3 HIRP code
   #
   #          Prerrequisite:  None
   #
   #                  Input:  None
   #
   #                 Return:  None
   #
   #######################################################################################################################


   def measureAR(self, st191_params, AR_params, test178_scale_offset, exec231 = 0):

      self.St(TP.spinupPrm_1)               # spin up



      self.frm.clearFrames()
      self.frm.readFramesFromCM_SIM()
      self.UNDO_HIRP_adjustment_retroactively_to_frames()



      headRetryCounter = 0
      self.total_AR_measurements = 0     # This is a safety net to prevent the loop from testing forever
      testedTracks = {}
      headStack = self.oUtility.copy(self.headList)
      headStack.reverse()
      oldLenHeadStack = len(headStack)
      while (headStack != []):
         iHead = headStack.pop()
         if len(headStack) != oldLenHeadStack:
            # This is required to determine when heads have switched
            headRetryCounter = 0
         oldLenHeadStack = len(headStack)


         st191_params['HEAD_RANGE'] = (iHead<<8) + iHead

         '''
         minNumZonesBeforeSkippingZonesInConcurrentHIRP = getattr(TP,'minNumZonesBeforeSkippingZonesInConcurrentHIRP', AFH_TEST191_MINIMUM_NUM_ZONES_BEFORE_SKIPPING_ZONES_IN_CONCURRENT_HIRP)

         if self.dut.numZones > minNumZonesBeforeSkippingZonesInConcurrentHIRP:
            st191_params["ZONE"]     = (0x0302)
         else:
            st191_params["ZONE"]     = (0x0101)
         '''
         cword2 = st191_params["CWORD2"]
         if testSwitch.FE_SGP_T191_BPI_PUSH_BY_ZONE == 1 :
            st191_params["FREQ_BY_ZONE"] = [125,125,125,125,125,125,125,125,125,125,125,125,125,125,125,125,125,125,130,130,135,135,145,145,145,145,150,150,160,165,170,170]
         if type(cword2) == types.TupleType:
            cword2 = cword2[0]
         if type(cword2) == types.ListType:
            cword2 = cword2[0]

         if ( testSwitch.FE_0145391_341036_FAFH_ENABLE_T191_USE_T74_CAL_FREQ == 1 ):
            ### Call Test 191 using Calibrated Frequencies from the RAP:
            CWORD2_USE_CAL_FREQ_FROM_T74 = 0x0008
            CWORD2_FAFH_TEST_TRACKS      = 0x0010
            cword2 = cword2 | CWORD2_USE_CAL_FREQ_FROM_T74
            cword2 = cword2 | CWORD2_FAFH_TEST_TRACKS

         if self.runClosedLoopHIRP:
            # set closed -loop HIRP bit
            cword2 = cword2 | TEST_191_CWORD2_CLOSED_LOOP_HIRP
            objMsg.printMsg("measureAR/ Running in Closed-loop HIRP mode")
         else:
            cword2 = cword2 & ( 0xFFFF - TEST_191_CWORD2_CLOSED_LOOP_HIRP )
            objMsg.printMsg("measureAR/ Running in Open-loop HIRP mode")
         st191_params["CWORD2"] = cword2

         if testSwitch.FE_0127824_341036_AFH_DISABLE_WHIRP_NOT_CT_ACCESSIBLE == 1:
            CWORD1_HIRP_HEATER_ONLY = 0x0080     # otherwise known as disable WHIRP
            cword1 = st191_params["CWORD1"]
            if type(cword1) == types.TupleType:
               cword1 = cword1[0]
            if type(cword1) == types.ListType:
               cword1 = cword1[0]
            cword1 = cword1 | CWORD1_HIRP_HEATER_ONLY
            st191_params["CWORD1"] = cword1


         self.total_AR_measurements += 1

         trkRetryCounter = 0
         spc_id = int((self.spcID) + (1e2 * headRetryCounter) + (1 * trkRetryCounter))

         st191_status = self.st_AR( st191_params, iHead, spc_id )


         objMsg.printMsg('HIRP Head %s, self.total_AR_measurements: %s' % (iHead, self.total_AR_measurements), objMsg.CMessLvl.IMPORTANT)


         totalRetryLimit = (AR_params['HEAD_RETEST_LIMIT'] + 1) * len(self.headList)
         if self.total_AR_measurements > totalRetryLimit:

            if st191_status != TEST_PASSED:
               raise

            ScrCmds.raiseException(11044, "HIRP/ total retries %s exceeded limit %s" % (self.total_AR_measurements, totalRetryLimit))

         # end of for all heads


      if self.runClosedLoopHIRP:
         self.apply_HIRP_adjustment_retroactively_to_frames()   # can only be called once ever in the process

      self.frm.writeFramesToCM_SIM()
      if not ( testSwitch.WA_0111543_399481_SKIP_readFromCM_SIMWriteToDRIVE_SIM_IN_HIRP == 1 ):
         self.frm.readFromCM_SIMWriteToDRIVE_SIM(exec231)

      objMsg.printMsg('Clear memory/FRAMES at the end of measureAR()', objMsg.CMessLvl.VERBOSEDEBUG)
      self.frm.clearFrames()
      if not testSwitch.FE_0294085_357595_P_CM_LOADING_REDUCTION :
         self.frm.display_frames()


   #######################################################################################################################
   #
   #               Function:  measure HIRP for Dual Heater
   #
   #        Original Author:  Michael T. Brady
   #
   #            Description:  Main Method in PF3 HIRP code
   #
   #          Prerrequisite:  None
   #
   #######################################################################################################################


   def measureAR_DH(self, AR_params, exec231 = 0, singleHtr2Pass = 0):

      self.St(TP.spinupPrm_1)               # spin up


      self.frm.clearFrames()
      self.frm.readFramesFromCM_SIM()
      self.UNDO_HIRP_adjustment_retroactively_to_frames()


      ########   PER ELEMENT LOOP STARTS  ############   

      if testSwitch.FE_0165920_341036_DISABLE_READER_HEATER_CONTACT_DETECT_AFH2:
         heaterElementList = self.dut.heaterElementList
      else:
         heaterElementList = [ "WRITER_HEATER" ]
         if (self.dut.isDriveDualHeater == 1)  or (testSwitch.virtualRun == 1) or (singleHtr2Pass == 1):
            heaterElementList.append( "READER_HEATER" )
         
      for heaterElement in heaterElementList:
         if heaterElement == "WRITER_HEATER":
            st191_params = TP.baseT191_WRITER_HEATER
         elif heaterElement == "READER_HEATER":
            st191_params = TP.baseT191_READER_HEATER
         else:
            ScrCmds.raiseException(11044, "HIRP/ invalid element type selected.  heaterElement: %s" % ( heaterElement ))

         headRetryCounter = 0
         self.total_AR_measurements = 0     # This is a safety net to prevent the loop from testing forever
         testedTracks = {}
         headStack = self.oUtility.copy(self.headList)
         headStack.reverse()
         if (testSwitch.FE_0159597_357426_DSP_SCREEN == 1)and (self.dut.nextState == 'HIRP1A_DSP'):
            headStack = [TD.Truth]

         oldLenHeadStack = len(headStack)
         while (headStack != []):
            iHead = headStack.pop()
            if len(headStack) != oldLenHeadStack:
               # This is required to determine when heads have switched
               headRetryCounter = 0
            oldLenHeadStack = len(headStack)

            st191_params['HEAD_RANGE'] = (iHead<<8) + iHead

            '''
            minNumZonesBeforeSkippingZonesInConcurrentHIRP = getattr(TP,'minNumZonesBeforeSkippingZonesInConcurrentHIRP', AFH_TEST191_MINIMUM_NUM_ZONES_BEFORE_SKIPPING_ZONES_IN_CONCURRENT_HIRP)

            if self.dut.numZones > minNumZonesBeforeSkippingZonesInConcurrentHIRP:
               st191_params["ZONE"]     = (0x0302)
            else:
               st191_params["ZONE"]     = (0x0101)
            '''
            cword2 = st191_params["CWORD2"]
            if type(cword2) == types.TupleType:
               cword2 = cword2[0]
            if type(cword2) == types.ListType:
               cword2 = cword2[0]

            if (self.runClosedLoopHIRP) and ( testSwitch.AFH_ENABLE_CLOSED_LOOP_HIRP_DH == 1 ):
               # set closed -loop HIRP bit
               cword2 = cword2 | TEST_191_CWORD2_CLOSED_LOOP_HIRP
               objMsg.printMsg("measureAR/ Running in Closed-loop HIRP mode")
            else:
               cword2 = cword2 & ( 0xFFFF - TEST_191_CWORD2_CLOSED_LOOP_HIRP )
               objMsg.printMsg("measureAR/ Running in Open-loop HIRP mode")

            if ( testSwitch.FE_0145391_341036_FAFH_ENABLE_T191_USE_T74_CAL_FREQ == 1 ):
               ### Call Test 191 using Calibrated Frequencies from the RAP:
               CWORD2_USE_CAL_FREQ_FROM_T74 = 0x0008
               cword2 = cword2 | CWORD2_USE_CAL_FREQ_FROM_T74

               CWORD2_FAFH_TEST_TRACKS      = 0x0010
               cword2 = cword2 | CWORD2_FAFH_TEST_TRACKS
               
            if heaterElement == 'READER_HEATER' and singleHtr2Pass == 1:
               st191_params['DUAL_HEATER_CONTROL'] = [0, -1]
               DONT_COPY_SINGLE_HTR_HO_HIRP_TO_WHIRP = 0x8000
               cword2 = cword2 | DONT_COPY_SINGLE_HTR_HO_HIRP_TO_WHIRP 

            st191_params["CWORD2"] = cword2

            if testSwitch.FE_0127824_341036_AFH_DISABLE_WHIRP_NOT_CT_ACCESSIBLE == 1:
               CWORD1_HIRP_HEATER_ONLY = 0x0080     # otherwise known as disable WHIRP
               cword1 = st191_params["CWORD1"]
               if type(cword1) == types.TupleType:
                  cword1 = cword1[0]
               if type(cword1) == types.ListType:
                  cword1 = cword1[0]
               cword1 = cword1 | CWORD1_HIRP_HEATER_ONLY
               st191_params["CWORD1"] = cword1


            self.total_AR_measurements += 1

            trkRetryCounter = 0
            spc_id = int((self.spcID) + (1e2 * headRetryCounter) + (1 * trkRetryCounter))

            st191_status = self.st_AR( st191_params, iHead, spc_id )


            objMsg.printMsg('HIRP Main/ Head %s, Element Type: %s, self.total_AR_measurements: %s' % (iHead, heaterElement, self.total_AR_measurements), objMsg.CMessLvl.IMPORTANT)


            totalRetryLimit = (AR_params['HEAD_RETEST_LIMIT'] + 1) * len(self.headList)
            if self.total_AR_measurements > totalRetryLimit:

               if st191_status != TEST_PASSED:
                  raise

               ScrCmds.raiseException(11044, "HIRP/ total retries %s exceeded limit %s" % (self.total_AR_measurements, totalRetryLimit))

            # end of for all heads


      ########   PER ELEMENT LOOP ENDS  ############   
      if self.runClosedLoopHIRP:
         self.apply_HIRP_adjustment_retroactively_to_frames()   # can only be called once ever in the process
         if ( testSwitch.FE_0142458_341036_AFH_NO_RETROACTIVELY_HIRP_ADJUST_NEG_CLR == 1) and not( testSwitch.FE_0294085_357595_P_CM_LOADING_REDUCTION == 1):
            self.frm.display_frames(2)


      self.frm.writeFramesToCM_SIM()
      if not ( testSwitch.WA_0111543_399481_SKIP_readFromCM_SIMWriteToDRIVE_SIM_IN_HIRP == 1 ):
         self.frm.readFromCM_SIMWriteToDRIVE_SIM(exec231)

      objMsg.printMsg('Clear memory/FRAMES at the end of measureAR()', objMsg.CMessLvl.VERBOSEDEBUG)
      self.frm.clearFrames()
      if not testSwitch.FE_0294085_357595_P_CM_LOADING_REDUCTION :
         self.frm.display_frames()

   def setHIRP_SPC_ID_fromStateTableStateName(self, ):
      """
      #######################################################################################################################
      #
      #               Function:  setHIRP_SPC_ID_fromStateTableStateName
      #
      #        Original Author:  Michael T. Brady
      #
      #            Description:  set the HIRP SPC_ID based on the StateTable State Name
      #
      #          Prerrequisite:  All HIRP states should be defined in AFH_constants.py in dictionary stateTableToHIRP_SPC_ID_encoding
      #
      #                  Input:  None
      #
      #           Return Value:  Status(int)
      #
      #######################################################################################################################

      """

      stateTableName = self.dut.nextState
      self.spcID = stateTableToHIRP_SPC_ID_encoding.get( stateTableName , HIRP_DEFAULT_SPC_ID)
      objMsg.printMsg("setHIRP_SPC_ID_fromStateTableStateName/ in stateTable state: %s setting HIRP SPC_ID to %s" % ( stateTableName, self.spcID ) )

      # end of setHIRP_SPC_ID_fromStateTableStateName
      return OK


   def st_AR(self, dInPrm, head, spc_id):
      """ Perform dPES Measurement via st() call.
      @type dInPrm: dict
      @param dInPrm: Input Parameters defined in L(testParameters)
      @type iTimeout: integer
      @param iTimeout: Execution timeout in seconds.
      @type iSpc_id:  integer
      @param iSpc_id: Manual iterator for multiple test sequencing.
      """

      dInPrm['spc_id'] = spc_id
      try:     self.dut.dblData.delTable('P191_CLR_COEF_CAL', forceDeleteDblTable = 1)
      except:  pass

      try:
         self.St(dInPrm)
         errorCode = 0
      except ScriptTestFailure, (failureData):
         objMsg.printMsg('MeasureAR/ failureData:%s' % str(failureData), objMsg.CMessLvl.DEBUG)
         objMsg.printMsg('MeasureAR/ Drive failed to successfully run st(191) AR test', objMsg.CMessLvl.DEBUG)
         try: errorCode = failureData[0][2]
         except: errorCode = 0
         objMsg.printMsg('st_AR/ Severe Error st(191) returned an error.  Head: %s, error code from st(191): %s' % \
            (head, errorCode), objMsg.CMessLvl.VERBOSEDEBUG)

      return errorCode



   #######################################################################################################################
   #
   #               Function:  apply_HIRP_adjustment_retroactively_to_frames
   #
   #        Original Author:  Michael T. Brady
   #
   #            Description:  apply HIRP adjustments to frames data
   #
   #          Prerrequisite:  frames data loaded
   #
   #                  Input:  None
   #
   #                 Return:  None
   #
   #######################################################################################################################

   def apply_HIRP_adjustment_retroactively_to_frames(self,):
      """
            Purpose of this function is to retroactively apply the HIRP adjustment to the AFH 1 (or AFH1) data.
         """
      objMsg.printMsg("retroactively applying HIRP correction to all previous AFH frames clearance measurements contained in process code", objMsg.CMessLvl.IMPORTANT)

      self.applyHIRP_adjustmentUsingFunctionPassedToFrames(self.mth.fromClrToHirpClr)



   #######################################################################################################################
   #
   #               Function:  UNDO_HIRP_adjustment_retroactively_to_frames
   #
   #        Original Author:  Michael T. Brady
   #
   #            Description:  UNDO HIRP adjustments to frames data
   #
   #          Prerrequisite:  frames data loaded
   #
   #                  Input:  None
   #
   #                 Return:  None
   #
   #######################################################################################################################

   def UNDO_HIRP_adjustment_retroactively_to_frames(self,):
      """
            Purpose of this function is to retroactively apply the HIRP adjustment to the AFH 1 (or AFH1) data.
         """
      if self.AFH_State > min(LIST_VALID_CLOSED_LOOP_HIRP_STATES):
         objMsg.printMsg("UNDOING HIRP correction to all previous AFH frames clearance measurements contained in process code", objMsg.CMessLvl.IMPORTANT)
         self.applyHIRP_adjustmentUsingFunctionPassedToFrames(self.mth.fromHirpClrToClr)
      else:
         objMsg.printMsg("Undoing HIRP corrections not necessary -- No closed loop HIRP States have yet run.", objMsg.CMessLvl.IMPORTANT)  


   #######################################################################################################################
   #
   #               Function:  apply_HIRP_adjustment_retroactively_to_frames
   #
   #        Original Author:  Michael T. Brady
   #
   #            Description:  apply HIRP adjustments using the function passed to the frames data
   # 
   #                          Note, the idea of passing the function pointer is so that the logic of which data to match 
   #                          with which heater is only expressed in one spot.
   #
   #          Prerrequisite:  frames data loaded
   #
   #                  Input:  None
   #
   #                 Return:  None
   #
   #######################################################################################################################

   def applyHIRP_adjustmentUsingFunctionPassedToFrames(self, genericFunc):

      self.St({'test_num':172, 'prm_name':'P172_CLR_COEF_ADJ', 'timeout': 1800, 'CWORD1': 20, 'spc_id': self.spcID + 1})

      #mth = MathLib.CAFH_Computations()
      self.mth.buildHirpScaleOffsetTable()
      afhModesToAdjust = [ AFH_MODE, AFH_MODE_TEST_135_INTERPOLATED_DATA, AFH_MODE_TEST_135_EXTREME_ID_OD_DATA ]

      # expect the frames data is already loaded
      for meaNo,frame in enumerate(self.frm.dPesSim.DPES_FRAMES):

         iHead = self.dut.PhysToLgcHdMap[frame['PHYS_HD']]              # P172_CLR_COEF_ADJ only outputs physical head
         if iHead != INVALID_HD and frame['mode'] in afhModesToAdjust:  # Check to make sure it is AFH data
            if testSwitch.FE_0295624_357595_P_FE_357595_HIRP_MOVE_TO_AFTER_AFH2 and (frame['stateName'] == 'AFH1'):
                continue

            iZone = frame['Zone']

            if testSwitch.IS_DH_CODE_ENABLED == 1:
               if ( frame['Heater Element'] == WRITER_HEATER_INDEX ):
                  frame['Write Clearance'] = genericFunc(iHead, iZone, frame['Write Clearance'], "WrtClr")

                  if self.dut.isDriveDualHeater == 1:
                     frame['Read Clearance']  = genericFunc(iHead, iZone, frame['Read Clearance'], "WrtClr")
                  else:
                     frame['Read Clearance']  = genericFunc(iHead, iZone, frame['Read Clearance'], "RdClr")

               elif ( frame['Heater Element'] == READER_HEATER_INDEX ):
                  # READER_HEATER WrtClr we do NOT adjust.
                  frame['Read Clearance']  = genericFunc(iHead, iZone, frame['Read Clearance'], "RdClr")
            else:
               # if SH code finds READER_HEATER data then it will adjust it.
               frame['Read Clearance']  = genericFunc(iHead, iZone, frame['Read Clearance'], "RdClr")
               frame['Write Clearance'] = genericFunc(iHead, iZone, frame['Write Clearance'], "WrtClr")
      self.mth.emptyHIRPscaleOffsetTable()
