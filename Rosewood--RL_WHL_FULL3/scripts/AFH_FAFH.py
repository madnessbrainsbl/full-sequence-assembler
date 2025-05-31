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
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/AFH_FAFH.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/AFH_FAFH.py#1 $
# Level: 3

#---------------------------------------------------------------------------------------------------------#

##########################################################################################################################
#
# Imports
#
##########################################################################################################################


import types

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
from PowerControl import objPwrCtrl



##########################################################################################################################
#
# Class CFAFH
#
##########################################################################################################################

class CFAFH(CProcess):
   """
      Class for calling FAFH calibrations
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
      self.St({'test_num':172, 'prm_name':"Retrieve WP's", 'CWORD1':12, 'timeout':100, 'spc_id': 1})

      # member variables
      self.AFH_State = self.frm.set_AFH_StateFromStateTableStateName()
      self.headList = range(objDut.imaxHead)   # getZoneTable()  # needs to be called prior to the init so that this is valid
      testSwitch.getmd5SumForAFH_flags()
      if ( testSwitch.extern.AFH_MAJ_REL_NUM == 0 ) and ( testSwitch.extern.AFH_MIN_REL_NUM == 0 ):
         objMsg.printMsg("AFH Release 0.0 Detected.  Most likely caused by SF3 flg.py file not loaded.  Fail.")
         ScrCmds.raiseException(11044, 'Invalid AFH Release Number 0.0 detected!')  # should never execute this

      #
      self.spcID = int(self.AFH_State * 10000)   # this statement must be after setting the internal AFH State
      self.headList = range(objDut.imaxHead)   # note imaxHead is the number of heads
      self.numHeads = int(len(self.headList))





   #######################################################################################################################
   #
   #               Function:  runFAFH_frequencyCalibration
   #
   #        Original Author:  Michael T. Brady
   #
   #            Description:  Run the FAFH frequency calibration
   #
   #          Prerrequisite:  AFH1
   #
   #                  Input:  
   #
   #           Return  Type:  None
   #
   #           Return Value:  None
   #
   #######################################################################################################################


   def runFAFH_frequencyCalibration(self, ):
      fafhFrequencyCalibrationParams = TP.fafhFrequencyCalibrationParams_074_01

      # CWORD1, not CWORD3 must exist in these test 74 calls where the below SF3 flag is enabled
      if (not testSwitch.virtualRun) and ('CWORD3' in fafhFrequencyCalibrationParams) and (testSwitch.extern.FE_0170290_357257_FAFH_PROCESS_SUPPORT_REFACTOR):
         ScrCmds.raiseException(11044, 'SF3 flag FE_0170290_357257_FAFH_PROCESS_SUPPORT_REFACTOR requires CWORD1, not CWORD3 be specified.')

      fafhFrequencyCalibrationParams["SPC_ID"] = self.spcID


      listOfErrorCodestoRaise = []
      try:
         self.St( fafhFrequencyCalibrationParams )
      except ScriptTestFailure, (failureData):
         try: ec = failureData[0][2]
         except: ec = 0
         objMsg.printMsg('runFAFH_frequencyCalibration/ ec: %s' % str(ec), objMsg.CMessLvl.VERBOSEDEBUG)

         curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(74)
         self.dut.objSeq.curRegSPCID = 1
         iHead = -1
         self.dut.dblData.Tables('P_MINOR_FAIL_CODE').addRecord(
            {
               'HD_PHYS_PSN':  iHead,
               'ERROR_CODE':  ec,
               'SPC_ID': self.spcID,
               'OCCURRENCE': occurrence,  # This mismatch needs to be addressed all over the code because the generating code is incorrect TODO
               'SEQ':curSeq,
               'TEST_SEQ_EVENT': testSeqEvent,
               'HD_LGC_PSN':  iHead,
               'TEST_NUMBER': 74,
               'FAIL_DATA':   "",
            })
         objMsg.printDblogBin(self.dut.dblData.Tables('P_MINOR_FAIL_CODE'))
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

         raise

      



   #######################################################################################################################
   #
   #               Function:  runFAFH_trackPrep
   #
   #        Original Author:  Michael T. Brady
   #
   #            Description:  Run the FAFH track prep
   #
   #          Prerrequisite:  AFH1
   #
   #                  Input:  
   #
   #           Return  Type:  None
   #
   #           Return Value:  None
   #
   #######################################################################################################################

   def runFAFH_trackPrep(self, ):

      fafhTrackPrepParams = TP.fafhTrackPrepParams_074_02
      fafhTrackPrepParams["SPC_ID"] = self.spcID

      if testSwitch.FE_AFH3_TO_IMPROVE_TCC:
         fafhTrackPrepParams["CWORD3"] |= 0x100 #SURPRESS_PARAM_FILE_INIT_B4_TRACK_PREP


      listOfErrorCodestoRaise = []
      fafhTrackPrepParams['timeout'] *= self.numHeads
      objMsg.printMsg('runFAFH_trackPrep/ timeout: %s' % (fafhTrackPrepParams['timeout']))
      try:
         self.St( fafhTrackPrepParams )

      except ScriptTestFailure, (failureData):
         try: ec = failureData[0][2]
         except: ec = 0
         objMsg.printMsg('runFAFH_trackPrep/ ec: %s' % str(ec), objMsg.CMessLvl.VERBOSEDEBUG)

         curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(74)
         self.dut.objSeq.curRegSPCID = 1
         iHead = -1
         self.dut.dblData.Tables('P_MINOR_FAIL_CODE').addRecord(
            {
               'HD_PHYS_PSN':  iHead,
               'ERROR_CODE':  ec,
               'SPC_ID': self.spcID,
               'OCCURRENCE': occurrence,  # This mismatch needs to be addressed all over the code because the generating code is incorrect TODO
               'SEQ':curSeq,
               'TEST_SEQ_EVENT': testSeqEvent,
               'HD_LGC_PSN':  iHead,
               'TEST_NUMBER': 74,
               'FAIL_DATA':   "",
            })
         objMsg.printDblogBin(self.dut.dblData.Tables('P_MINOR_FAIL_CODE'))
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

         raise

      # always power cycle the drive after track prep.  Possible temporary fix for 100% fail in ZAP?!
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)


   #######################################################################################################################
   #
   #               Function:  runFAFH_AR_measurement
   #
   #        Original Author:  Michael T. Brady
   #
   #            Description:  Run the FAFH track prep
   #
   #          Prerrequisite:  AFH1
   #
   #                  Input:  
   #
   #           Return  Type:  None
   #
   #           Return Value:  None
   #
   #######################################################################################################################

   def runFAFH_AR_measurement(self, tempIndexStr, verifyTestTracksFlag = 0):
      fafhAR_measurementParams = TP.fafhAR_measurementParams_074_03
      fafhAR_measurementParams["SPC_ID"] = self.spcID

      # 'CERT_TEMPERATURE'   : 0 or 1,            # 0 for HIGH Temp and 1 for Low Temp

      FAFH_HOT_MEASUREMENT = 0
      FAFH_COLD_MEASUREMENT = 1


      if verifyTestTracksFlag:
         fafhAR_measurementParams[ 'CWORD1' ] &= ~0x0010   # turn off Bit 4 so the FAFH Parameter File will NOT be written to disk
         fafhAR_measurementParams[ 'CWORD1' ] &= ~0x000F   # clear the command field (least significant nibble)
         fafhAR_measurementParams[ 'CWORD1' ] |=  0x000D   # Set command to VERIFY_TEST_TRACKS
         fafhAR_measurementParams[ 'CERT_TEMPERATURE' ] = FAFH_HOT_MEASUREMENT
      else:
         if tempIndexStr == 'FAFH_HOT_MEASUREMENT':
            fafhAR_measurementParams[ 'CERT_TEMPERATURE' ] = FAFH_HOT_MEASUREMENT
         elif tempIndexStr == 'FAFH_COLD_MEASUREMENT':
            fafhAR_measurementParams[ 'CERT_TEMPERATURE' ] = FAFH_COLD_MEASUREMENT
         else:
            raise


      listOfErrorCodestoRaise = []
      try:
         self.St( fafhAR_measurementParams )

      except ScriptTestFailure, (failureData):
         try: ec = failureData[0][2]
         except: ec = 0
         objMsg.printMsg('runFAFH_AR_measurement/ ec: %s' % str(ec), objMsg.CMessLvl.VERBOSEDEBUG)

         curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(74)
         self.dut.objSeq.curRegSPCID = 1
         iHead = -1
         self.dut.dblData.Tables('P_MINOR_FAIL_CODE').addRecord(
            {
               'HD_PHYS_PSN':  iHead,
               'ERROR_CODE':  ec,
               'SPC_ID': self.spcID,
               'OCCURRENCE': occurrence,  # This mismatch needs to be addressed all over the code because the generating code is incorrect TODO
               'SEQ':curSeq,
               'TEST_SEQ_EVENT': testSeqEvent,
               'HD_LGC_PSN':  iHead,
               'TEST_NUMBER': 74,
               'FAIL_DATA':   "",
            })
         objMsg.printDblogBin(self.dut.dblData.Tables('P_MINOR_FAIL_CODE'))
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

         raise


      # display coefficients
      if tempIndexStr == 'FAFH_COLD_MEASUREMENT':
         fafhAR_displayCoefficientsParams = TP.fafhAR_displayCoefficientsParams_074_04

         listOfErrorCodestoRaise_2 = []
         try:
            self.St( fafhAR_displayCoefficientsParams )

         except ScriptTestFailure, (failureData):
            try: ec = failureData[0][2]
            except: ec = 0
            objMsg.printMsg('runFAFH_AR_measurement/ ec: %s' % str(ec), objMsg.CMessLvl.VERBOSEDEBUG)

            curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(74)
            self.dut.objSeq.curRegSPCID = 1
            iHead = -1
            self.dut.dblData.Tables('P_MINOR_FAIL_CODE').addRecord(
               {
                  'HD_PHYS_PSN':  iHead,
                  'ERROR_CODE':  ec,
                  'SPC_ID': self.spcID,
                  'OCCURRENCE': occurrence,  # This mismatch needs to be addressed all over the code because the generating code is incorrect TODO
                  'SEQ':curSeq,
                  'TEST_SEQ_EVENT': testSeqEvent,
                  'HD_LGC_PSN':  iHead,
                  'TEST_NUMBER': 74,
                  'FAIL_DATA':   "",
               })
            objMsg.printDblogBin(self.dut.dblData.Tables('P_MINOR_FAIL_CODE'))
            objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

            raise


         



