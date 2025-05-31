#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Generalized SDAT Test Script, contolled by SdatParameters.py
# Owner: Jim French
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/SDAT.py $
# $Revision: #1 $
# $Id: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/SDAT.py#1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/SDAT.py#1 $
# Level: ?
#---------------------------------------------------------------------------------------------------------#
#******************************************************************************
#**********************CODE BELOW FOR SDAT 2.0 and ABOVE **********************
#******************************************************************************

# Once everything is switched to at least SDAT 2.0 everything in other section can be removed
from Constants import *
from TestParamExtractor import TP
from Exceptions import CDblogDataMissing
from State import CState
from Servo import CServoOpti, CServoFunc, CServoScreen
if testSwitch.SPLIT_BASE_SERIAL_TEST_FOR_CM_LA_REDUCTION:
   from Serial_Init import CInit_DriveInfo
else:
   from base_SerialTest import CInit_DriveInfo
import ScrCmds
import MessageHandler as objMsg
from FSO import CFSO
import XmlResults
from Setup import CSetup
import math
import os
import time
import traceback
import DbLogAlias
from SampleMonitor import TD
from SampleMonitor import CSampMon
import SdatParameters
from PowerControl import objPwrCtrl

#Define Constants for parsing the truth value
TMR_SUITE          = 0x0001 # Turns on all in test suite
TRACK_FOLLOW_SUITE = 0x0002 # Turns on all in test suite

UACT_GAIN_CAL_2  = 0x0010 # uActGainCal Class
MDW_REL_2        = 0x0020 # MDW Class
CTRL_NOTCH_2     = 0x0040 # Controller Notch Class
TMR_VERIFY_2     = 0x0080 # TMR Verify Class
BODES_2          = 0x0100 # Bode Class
TRK_FOLLOW_2     = 0x0200 # Track Follow Class (individual T288 track follow call
SERVO_LIN_2      = 0x0400 # Servo Linearization Class
ZEST_2           = 0x0800 # Zest Class

PES_COLLECT_2    = 0x1000 # Vibe collection
XV_TRANSFER_FUNC = 0x2000 # XV transfer function
WIRRO_SQ_2       = 0x8000 # T257 WIRRO_SQ Run

FULL_SDAT        = 0x2FF0 # The current 'full' sdat run

from SdatParameters import *

# Modes for RV / Tester Vibe data collection (associated with ConfigVar "SDAT_VIBE_DATA")
VIBE_PES_COLLECTION = 100     # Mode 100  = Collect 100 revs of PES on 16 tracks per head @ OD (note: 100 is a version, NOT the number of revs to collect PES)
#define new RV / Vibe Data collection modes here

class CSdatUtils(CState):
   def __init__(self, dut, params=[]):
      self.dut    = dut
      self.params = params
      CState.__init__(self, dut, [])
      self.oSrvFunc = CServoFunc()

   def determineActionFromTruthValue (self, TruthVal, ClassID):
      if ( TruthVal & ClassID ):
         return True
      else:
         return False

   def Separator(self):
      objMsg.printMsg("+" * 80)
      return

class CSdatBase2(CSdatUtils, CState):
   """
      Provide a single call to generate the SDAT data
   """
   def __init__(self, dut, params=[]):
      TraceMessage( '=' * 80 )
      self.dut    = dut
      self.params = params
      self.oSrvOpti = CServoOpti()
      CState.__init__(self, dut, [])
      self.dut.objData.update({'TEMP_P_SDAT_INFO' : {}}) # storing p_sdat_info here, then updating when running
      # tmr_verify, track_follow, or dcsq, to set flags accordingly
      from time import localtime
      year,month,day = localtime()[:3]
      hour,minute,second = localtime( )[3:6]
      self.MonDayString = "%02d%02d"%(month,day)
      self.YearString = "%04d"%(year)
      self.TimeString = "%02d_%02d_%02d"%(hour,minute,second)

   def run(self):
      try:
         if testSwitch.extern.SDAT_MAJ_REL_NUM < 2 :
            objMsg.printMsg('SDAT NOT HIGH ENOUGH VERSION FOR THIS CODE')
            raise
         TraceMessage("SDAT Class Now Running")

         #Will init drive info if not already initialized
         oDrvInfo = CInit_DriveInfo(self.dut)
         oDrvInfo.run()

         FailedState = DriveAttributes.get('FAIL_STATE','N/A')
         FailedCode  = DriveAttributes.get('FAIL_CODE',0)
         ChangeTruthValOnFail = 0

         SDATOnly = len(self.dut.operList) == 1 # if sdat is the only operation being run the operList lenght is 1, run full sdat

         if testSwitch.FE_0159477_350037_SAMPLE_MONITOR == 1:
            TD.Truth = int(DriveAttributes.get('SAMP_MON_TRUTH',0))
            # if sdat is run with a failure drive, forget the truth value passed in a full run is desired
            if (int(FailedCode) != 0):
               TD.Truth = FULL_SDAT
               ChangeTruthValOnFail = 1
            if SDATOnly:
               TD.Truth = FULL_SDAT
            if TD.Truth >= 1:
               if self.determineActionFromTruthValue(TD.Truth, TMR_SUITE):
                  TD.Truth &= 0xFFFE
                  TD.Truth |= 0x0080
               if self.determineActionFromTruthValue(TD.Truth, TRACK_FOLLOW_SUITE):
                  TD.Truth &= 0xFFFD
                  TD.Truth |= 0x0360
            objMsg.printMsg("TruthValue is %x" % TD.Truth)
         #
         # Collect Drive Info at SF3 Level
         #
         self.oSrvOpti.St(InitializeAndDriveInfoPrm_288) # Set all T288 params to default clear binary output file and get Drive Info on SF3 side

         # convert partnum to project name (if available)
         pn = self.dut.partNum
         if pn2Prj.has_key(pn):
            projectName = pn2Prj[pn]
         else:
            projectName = pn2Prj.get('DEF',pn)

         (mV3,mA3),(mV5,mA5),(mV12,mA12)  = GetDriveVoltsAndAmps()
         chamberTemp = ReportTemperature()/10.0
         startDate = self.YearString + '-' + self.MonDayString[0:2] + '-' + self.MonDayString[2:4]

         # Make a request to get all of drive history, HistoryData should be a dictionary
         # with 1 entry as 'rows'. This points to a list of all entries as dictionaries.
         # They are added newest first.
         HistoryName, HistoryData = RequestService("GetDriveHistory", (self.dut.serialnum))
         HistoryList = HistoryData.get('rows')
         CurrentRunInfo = HistoryList[0]
         StartTime = CurrentRunInfo.get('EVENT_TIME', self.TimeString )
         TransSeq  = CurrentRunInfo.get('TRANS_SEQ', 0 )
         StartDate = CurrentRunInfo.get('EVENT_DATE', startDate )

         tempSdatInfo = {
                        'SBR'        : self.dut.sbr,
                        'START_DATE' : StartDate,
                        'START_TIME' : StartTime,
                        'PROJECT'    : projectName,
                        'SEQ_NUM'    : int(TransSeq),        #currently unavailable
                        'SN'         : self.dut.serialnum,
                        'FAIL_TEST'  : FailedState,
                        'ERROR_CODE' : int(FailedCode),
                        'INTERFACE'  :'Gemini',  #maybe this can change and not be hardcoded...
                        'TESTER'     : HOST_ID,
                        'SLOT_NUM'   : str(CellNumber),
                        'TEMP'       : chamberTemp,
                        'VOLTS_3'    : mV3/1000.0,
                        'VOLTS_5'    : mV5/1000.0,
                        'VOLTS_12'   : mV12/1000.0,
                        'PLOT_TYPE'  : 6,
                        'MDW_REL'          : 0,
                        'TRACK_FOLLOW'     : 0,
                        'CTRL_NOTCH'       : 0,
                        'TMR_VERIFY'       : 0,
                        'ZEST'             : 0,
                        'BODES'            : 0,
                        'SERVO_LIN'        : 0,
                        'VIBE'             : 0,
                        'UACT_GAIN_CAL'    : 0,
                        'CUSTOM_RV'        : 0,
                        'XV_TRANSFER_FUNC' : 0,
                        'WIRRO_SQ'         : 0,
                        'TruthChangeForFail' : ChangeTruthValOnFail,
                        'SDATOnlyOper'  : SDATOnly,
                        'CM_REV'        : CMCodeVersion,
                        'HOST_REV'      : HostVersion,
                        'PRODUCT'       : str(ConfigId[1]),
                        'CONFIG'        : str(ConfigId[2]),
                        'SCN'           : str(self.dut.partNum),
                        'RIM_TYPE'      : str(self.dut.rimType),
                        'BIRTH_DATE'    : DriveAttributes.get('BIRTH_DATE','N/A'),
                        }

         self.dut.objData.update({'TEMP_P_SDAT_INFO' : tempSdatInfo})

      except:
         from sys import exc_info
         objMsg.printMsg('EXCEPTION IN SDAT: Exception was raised in SDAT but contained so that it cannot stop test process')
         sdatExceptionInfo = exc_info()
         objMsg.printMsg('EXCEPTION IN SDAT: type: %s' % sdatExceptionInfo[0])
         objMsg.printMsg('EXCEPTION IN SDAT: value: %s' % sdatExceptionInfo[1])
         objMsg.printMsg('EXCEPTION IN SDAT: traceback: %s' % traceback.format_exc())

      return

class CSdatControllerNotch2(CSdatUtils, CState):
   """
      SDAT Controller and Notch Coefficients Test class
   """
   def __init__(self, dut, params=[]):
      TraceMessage( '=' * 80 )
      self.dut    = dut
      self.params = params
      self.oSrvOpti = CServoOpti()
      CState.__init__(self, dut, [])

   def run(self):
      try:
         if ( (testSwitch.FE_0159477_350037_SAMPLE_MONITOR == 1 and (self.determineActionFromTruthValue(TD.Truth, CTRL_NOTCH_2))) or (testSwitch.FE_0159477_350037_SAMPLE_MONITOR == 0)):
            # Update the sdat info
            tempSdatInfo = self.dut.objData.retrieve('TEMP_P_SDAT_INFO')
            tempSdatInfo['CTRL_NOTCH'] = CTRL_NOTCH_2
            self.dut.objData.update({'TEMP_P_SDAT_INFO' : tempSdatInfo})
            # Run the test
            TraceMessage("SDAT Controller and Notch Coefficients Class Now Running")
            objMsg.printMsg("Controller and Notch Coefficients being handled through Test 288!")
            # Collect the servo controller and notch table coefficients, and add them to the T288 binary output file
            self.oSrvOpti.St(getCtrlAndNotchCoeffs_288)
            objMsg.printMsg("Controller and Notch data collection Complete, processed through Test 288!")

      except:
         from sys import exc_info
         objMsg.printMsg('EXCEPTION IN SDAT: Exception was raised in SDAT but contained so that it cannot stop test process')
         sdatExceptionInfo = exc_info()
         objMsg.printMsg('EXCEPTION IN SDAT: type: %s' % sdatExceptionInfo[0])
         objMsg.printMsg('EXCEPTION IN SDAT: value: %s' % sdatExceptionInfo[1])
         objMsg.printMsg('EXCEPTION IN SDAT: traceback: %s' % traceback.format_exc())

      return

class CSdatUACT2(CSdatUtils, CState):
   """
      SDAT uActuator Gain Cal class
   """

   def __init__(self, dut, params=[]):
      TraceMessage( '=' * 80 )
      self.dut    = dut
      self.params = params
      self.oSrvFunc = CServoFunc()
      CState.__init__(self, dut, [])

   def run(self):
      try:
         if ( (testSwitch.FE_0159477_350037_SAMPLE_MONITOR == 1 and (self.determineActionFromTruthValue(TD.Truth, UACT_GAIN_CAL_2))) or (testSwitch.FE_0159477_350037_SAMPLE_MONITOR == 0)):
            #Update the sdat Info
            tempSdatInfo = self.dut.objData.retrieve('TEMP_P_SDAT_INFO')
            tempSdatInfo['UACT_GAIN_CAL'] = UACT_GAIN_CAL_2
            self.dut.objData.update({'TEMP_P_SDAT_INFO' : tempSdatInfo})
            # Run the test
            objMsg.printMsg("uActuator Gain Cal handled through Test 288!")
            self.oSrvFunc.St( getuActGainCalPrm_288 )
            objMsg.printMsg("uActuator Gain Cal complete through Test 288!")

      except:
         from sys import exc_info
         objMsg.printMsg('EXCEPTION IN SDAT: Exception was raised in SDAT but contained so that it cannot stop test process')
         sdatExceptionInfo = exc_info()
         objMsg.printMsg('EXCEPTION IN SDAT: type: %s' % sdatExceptionInfo[0])
         objMsg.printMsg('EXCEPTION IN SDAT: value: %s' % sdatExceptionInfo[1])
         objMsg.printMsg('EXCEPTION IN SDAT: traceback: %s' % traceback.format_exc())

      return

class XVTransferFunction(CSdatUtils, CState):
   """
      SDAT XVTransferFunction class
   """
   def __init__( self, dut, params = [ ] ):
      TraceMessage( '=' * 80 )
      self.dut    = dut
      self.params = params
      self.oSrvFunc = CServoFunc( )
      CState.__init__( self, dut, [ ] )

   def run( self ):
      try:
          if ( (testSwitch.FE_0159477_350037_SAMPLE_MONITOR == 1 and (self.determineActionFromTruthValue(TD.Truth, XV_TRANSFER_FUNC))) ):
            tempSdatInfo = self.dut.objData.retrieve('TEMP_P_SDAT_INFO')
            tempSdatInfo['XV_TRANSFER_FUNC'] = XV_TRANSFER_FUNC
            TraceMessage( "SDAT XVTransferFunction Class Now Running" )
            objMsg.printMsg( "OD" )
            self.oSrvFunc.St( xvTransferFuncPrmOD_288 )
            objMsg.printMsg( "ID" )
            self.oSrvFunc.St( xvTransferFuncPrmID_288 )

      except:
         from sys import exc_info
         objMsg.printMsg('EXCEPTION IN SDAT: Exception was raised in SDAT but contained so that it cannot stop test process')
         sdatExceptionInfo = exc_info()
         objMsg.printMsg('EXCEPTION IN SDAT: type: %s' % sdatExceptionInfo[0])
         objMsg.printMsg('EXCEPTION IN SDAT: value: %s' % sdatExceptionInfo[1])
         objMsg.printMsg('EXCEPTION IN SDAT: traceback: %s' % traceback.format_exc())

      return

class CSdatMDW2(CSdatUtils, CState):
   """
      SDAT MDW Test class
   """
   def __init__(self, dut, params=[]):
      TraceMessage( '=' * 80 )
      self.dut    = dut
      self.params = params
      self.oSrvFunc = CServoFunc()
      CState.__init__(self, dut, [])

   def run(self):
      try:
         if ( (testSwitch.FE_0159477_350037_SAMPLE_MONITOR == 1 and (self.determineActionFromTruthValue(TD.Truth, MDW_REL_2))) or (testSwitch.FE_0159477_350037_SAMPLE_MONITOR == 0)):
            # Update the sdat info
            tempSdatInfo = self.dut.objData.retrieve('TEMP_P_SDAT_INFO')
            tempSdatInfo['MDW_REL'] = MDW_REL_2
            self.dut.objData.update({'TEMP_P_SDAT_INFO' : tempSdatInfo})
            # Run the test
            TraceMessage("SDAT MDW Class Now Running")
            objMsg.printMsg("Eccentricity data, bad sector rates and track zero data being handled through Test 288!")
            self.oSrvFunc.St(getMdwDataPrm_288)
            objMsg.printMsg("MDW data collection Complete, processed through Test 288!")

      except:
         from sys import exc_info
         objMsg.printMsg('EXCEPTION IN SDAT: Exception was raised in SDAT but contained so that it cannot stop test process')
         sdatExceptionInfo = exc_info()
         objMsg.printMsg('EXCEPTION IN SDAT: type: %s' % sdatExceptionInfo[0])
         objMsg.printMsg('EXCEPTION IN SDAT: value: %s' % sdatExceptionInfo[1])
         objMsg.printMsg('EXCEPTION IN SDAT: traceback: %s' % traceback.format_exc())

      return

class CSdatTmrVerf2(CSdatUtils, CState):
   """
      SDAT TMR Verify Test class
   """
   def __init__(self, dut, params=[]):
      TraceMessage( '=' * 80 )
      self.dut    = dut
      self.params = params
      self.oSrvFunc = CServoFunc()
      CState.__init__(self, dut, [])

   def run(self):
      try:
         if ( (testSwitch.FE_0159477_350037_SAMPLE_MONITOR == 1 and (self.determineActionFromTruthValue(TD.Truth, TMR_VERIFY_2))) or (testSwitch.FE_0159477_350037_SAMPLE_MONITOR == 0)):
            # Update the sdat info
            tempSdatInfo = self.dut.objData.retrieve('TEMP_P_SDAT_INFO')
            tempSdatInfo['TMR_VERIFY'] = TMR_VERIFY_2
            self.dut.objData.update({'TEMP_P_SDAT_INFO' : tempSdatInfo})
            # Run the test
            TraceMessage("SDAT TMR Verify Class Now Running")
            objMsg.printMsg("TMR Verify being processed by Test 288!")
            self.oSrvFunc.St( getTmrVerPrm_288 )
            objMsg.printMsg("TMR Verify Complete, processed through Test 288!")

      except:
         from sys import exc_info
         objMsg.printMsg('EXCEPTION IN SDAT: Exception was raised in SDAT but contained so that it cannot stop test process')
         sdatExceptionInfo = exc_info()
         objMsg.printMsg('EXCEPTION IN SDAT: type: %s' % sdatExceptionInfo[0])
         objMsg.printMsg('EXCEPTION IN SDAT: value: %s' % sdatExceptionInfo[1])
         objMsg.printMsg('EXCEPTION IN SDAT: traceback: %s' % traceback.format_exc())

      return

class CSdatTrkFlw2(CSdatUtils, CState):
   """
      SDAT Track Follow Test class
   """
   def __init__(self, dut, params=[]):
      TraceMessage( '=' * 80 )
      self.dut    = dut
      self.params = params
      self.oSrvFunc = CServoFunc()
      CState.__init__(self, dut, [])

   def run(self):
      try:
         if ( (testSwitch.FE_0159477_350037_SAMPLE_MONITOR == 1 and (self.determineActionFromTruthValue(TD.Truth, TRK_FOLLOW_2))) or (testSwitch.FE_0159477_350037_SAMPLE_MONITOR == 0)):
            # Update the sdat info
            tempSdatInfo = self.dut.objData.retrieve('TEMP_P_SDAT_INFO')
            tempSdatInfo['TRACK_FOLLOW'] = TRK_FOLLOW_2
            self.dut.objData.update({'TEMP_P_SDAT_INFO' : tempSdatInfo})
            TraceMessage("SDAT Track Follow  Class Now Running")
            # Track Follow Test
            # This is the start of the variations of rro.
            objMsg.printMsg("Track follow variations of RRO data being handled through Test 288!")
            self.oSrvFunc.St( getTrkFollowPrm_288 )
            objMsg.printMsg("Track follow variations of RRO data collection complete through Test 288!")
            TraceMessage("SDAT Track Follow Complete")

      except:
         from sys import exc_info
         objMsg.printMsg('EXCEPTION IN SDAT: Exception was raised in SDAT but contained so that it cannot stop test process')
         sdatExceptionInfo = exc_info()
         objMsg.printMsg('EXCEPTION IN SDAT: type: %s' % sdatExceptionInfo[0])
         objMsg.printMsg('EXCEPTION IN SDAT: value: %s' % sdatExceptionInfo[1])
         objMsg.printMsg('EXCEPTION IN SDAT: traceback: %s' % traceback.format_exc())

      return

class CSdatWirroSq2(CSdatUtils, CState):
   """
      SDAT RRHP and WIRRO (squeeze) collection class
   """

   def __init__(self, dut, params=[]):
      TraceMessage( '=' * 80 )
      self.dut    = dut
      self.params = params
      self.oSrvFunc = CServoFunc()
      CState.__init__(self, dut, [])


   def run(self):
      try:
         if ( (testSwitch.FE_0159477_350037_SAMPLE_MONITOR == 1 and (self.determineActionFromTruthValue(TD.Truth, WIRRO_SQ_2)) ) ):
            # Update the sdat info
            tempSdatInfo = self.dut.objData.retrieve('TEMP_P_SDAT_INFO')
            tempSdatInfo['WIRRO_SQ'] = WIRRO_SQ_2
            self.dut.objData.update({'TEMP_P_SDAT_INFO' : tempSdatInfo})
            TraceMessage("SDAT WIRRO_SQ Test Running")
            objMsg.printMsg("WIRRO_SQ being run from T257!")
            self.oSrvFunc.St(WirroSqSdatPrm_257)
            objMsg.printMsg("WIRRO_SQ complete through Test 257!")
            TraceMessage("SDAT WIRRO_SQ Test Complete")


      except:
         from sys import exc_info
         objMsg.printMsg('EXCEPTION IN SDAT: Exception was raised in SDAT but contained so that it cannot stop test process')
         sdatExceptionInfo = exc_info()
         objMsg.printMsg('EXCEPTION IN SDAT: type: %s' % sdatExceptionInfo[0])
         objMsg.printMsg('EXCEPTION IN SDAT: value: %s' % sdatExceptionInfo[1])
         objMsg.printMsg('EXCEPTION IN SDAT: traceback: %s' % traceback.format_exc())

      return


# THIS CLASS IS ONLY INCLUDED WHEN SAMPLE MONITOR IS SET TO 1
class CSdatVibe2(CSdatUtils, CState):
   """
      SDAT Vibe collection class
   """

   def __init__(self, dut, params=[]):
      TraceMessage( '=' * 80 )
      self.dut    = dut
      self.params = params
      self.oSrvFunc = CServoFunc()
      CState.__init__(self, dut, [])


   def run(self):
      try:

         if testSwitch.FE_0159477_350037_SAMPLE_MONITOR == 1:
            tempSdatInfo = self.dut.objData.retrieve('TEMP_P_SDAT_INFO')

            if self.determineActionFromTruthValue(TD.Truth, PES_COLLECT_2):
               tempSdatInfo['VIBE'] = PES_COLLECT_2
               tempSdatInfo['CUSTOM_RV'] = VIBE_PES_COLLECTION;
               #This is the collector drive
               objMsg.printMsg("Collect Vibe Data.")
               self.oSrvFunc.St(VibeDataCollection_288)

            self.dut.objData.update({'TEMP_P_SDAT_INFO' : tempSdatInfo})


      except:
         from sys import exc_info
         objMsg.printMsg('EXCEPTION IN SDAT: Exception was raised in SDAT but contained so that it cannot stop test process')
         sdatExceptionInfo = exc_info()
         objMsg.printMsg('EXCEPTION IN SDAT: type: %s' % sdatExceptionInfo[0])
         objMsg.printMsg('EXCEPTION IN SDAT: value: %s' % sdatExceptionInfo[1])
         objMsg.printMsg('EXCEPTION IN SDAT: traceback: %s' % traceback.format_exc())

      return

class CSdatZest2(CSdatUtils, CState):
   """
      SDAT Zest collection class
   """

   def __init__(self, dut, params=[]):
      TraceMessage( '=' * 80 )
      self.dut    = dut
      self.params = params
      self.oSrvFunc = CServoFunc()
      CState.__init__(self, dut, [])

   def run(self):
      try:
         if ( (testSwitch.FE_0159477_350037_SAMPLE_MONITOR == 1 and (self.determineActionFromTruthValue(TD.Truth, ZEST_2))) or (testSwitch.FE_0159477_350037_SAMPLE_MONITOR == 0)):
            #Update the sdat info
            tempSdatInfo = self.dut.objData.retrieve('TEMP_P_SDAT_INFO')
            tempSdatInfo['ZEST'] = ZEST_2
            self.dut.objData.update({'TEMP_P_SDAT_INFO' : tempSdatInfo})
            # Get the compressed zest table
            objMsg.printMsg("Zest Table being compressed with gzip through Test 288!")
            self.oSrvFunc.St(getZestTableZip_288)
            objMsg.printMsg("Zest Table compression complete!")

      except:
         from sys import exc_info
         objMsg.printMsg('EXCEPTION IN SDAT: Exception was raised in SDAT but contained so that it cannot stop test process')
         sdatExceptionInfo = exc_info()
         objMsg.printMsg('EXCEPTION IN SDAT: type: %s' % sdatExceptionInfo[0])
         objMsg.printMsg('EXCEPTION IN SDAT: value: %s' % sdatExceptionInfo[1])
         objMsg.printMsg('EXCEPTION IN SDAT: traceback: %s' % traceback.format_exc())

      return


class CSdatServoLin2(CSdatUtils, CState):
   """
      SDAT Linearization class
   """

   def __init__(self, dut, params=[]):
      TraceMessage( '=' * 80 )
      self.dut    = dut
      self.params = params
      self.oSrvFunc = CServoFunc()
      CState.__init__(self, dut, [])

   def run(self):
      try:
         if ( (testSwitch.FE_0159477_350037_SAMPLE_MONITOR == 1 and (self.determineActionFromTruthValue(TD.Truth, SERVO_LIN_2))) or (testSwitch.FE_0159477_350037_SAMPLE_MONITOR == 0)):
            #Update the sdat Info
            tempSdatInfo = self.dut.objData.retrieve('TEMP_P_SDAT_INFO')
            tempSdatInfo['SERVO_LIN'] = SERVO_LIN_2
            self.dut.objData.update({'TEMP_P_SDAT_INFO' : tempSdatInfo})
            # Run the test
            objMsg.printMsg("servo linearizationdata being handled through Test 288!")
            self.oSrvFunc.St( getLinearizationPrm_288 )
            objMsg.printMsg("servo linearization data collection complete through Test 288!")

      except:
         from sys import exc_info
         objMsg.printMsg('EXCEPTION IN SDAT: Exception was raised in SDAT but contained so that it cannot stop test process')
         sdatExceptionInfo = exc_info()
         objMsg.printMsg('EXCEPTION IN SDAT: type: %s' % sdatExceptionInfo[0])
         objMsg.printMsg('EXCEPTION IN SDAT: value: %s' % sdatExceptionInfo[1])
         objMsg.printMsg('EXCEPTION IN SDAT: traceback: %s' % traceback.format_exc())

      return

class CSdatBodes2(CSdatUtils, CState):
   """
      SDAT Bode measurements class
   """

   def __init__(self, dut, params=[]):
      TraceMessage( '=' * 80 )
      self.dut    = dut
      self.params = params
      self.oSrvOpti = CServoOpti()
      CState.__init__(self, dut, [])

   def run(self):
      try:
         if ( (testSwitch.FE_0159477_350037_SAMPLE_MONITOR == 1 and (self.determineActionFromTruthValue(TD.Truth, BODES_2))) or (testSwitch.FE_0159477_350037_SAMPLE_MONITOR == 0)):
            #Update the Sdat Info
            tempSdatInfo = self.dut.objData.retrieve('TEMP_P_SDAT_INFO')
            tempSdatInfo['BODES'] = BODES_2
            self.dut.objData.update({'TEMP_P_SDAT_INFO' : tempSdatInfo})
            # This is the Bode measurement part of track follow. When T288 is being used.
            if testSwitch.FE_0115640_010200_SDAT_DUAL_STAGE_SUPPORT :
               self.measureAllDualStageBodes()
            else:
               self.measureAllSingleStageBodes()
      except:
         from sys import exc_info
         objMsg.printMsg('EXCEPTION IN SDAT: Exception was raised in SDAT but contained so that it cannot stop test process')
         sdatExceptionInfo = exc_info()
         objMsg.printMsg('EXCEPTION IN SDAT: type: %s' % sdatExceptionInfo[0])
         objMsg.printMsg('EXCEPTION IN SDAT: value: %s' % sdatExceptionInfo[1])
         objMsg.printMsg('EXCEPTION IN SDAT: traceback: %s' % traceback.format_exc())

      return

   def measureAllDualStageBodes(self):
      """This function calls T288 to measure all bode data required for dual stage products"""
      #
      #  Collect all bode data for dual stage products.  T288 can run multiple bode measurements
      #  on multiple test tracks, all with one call.  The data is saved in a binary PC File (sdatfile).
      #
      objMsg.printMsg("Start of Dual Stage Bode measurements (OD, MD, ID)")
      self.oSrvOpti.St(doDualStageBodeTestsPrm_288)     # Measure uAct Plant, VCM plant, and Dual Stage Open Loop bodes
      objMsg.printMsg("End of Dual Stage Bode measurements")
      self.Separator()

      return

   def measureAllSingleStageBodes(self):
      """This function calls T288 to measure all bode data required for single stage products"""
      #
      #  Collect all bode data for single stage products.  T288 can run multiple bode measurements
      #  on multiple test tracks, all with one call.  The data is saved in a binary PC File (sdatfile).
      #
      objMsg.printMsg("Start of Single Stage Bode measurements (OD, MD, ID)")
      self.oSrvOpti.St(doVCMBodeTestsPrm_288)           # Measure VCM Plant and VCM Open Loop bodes
      objMsg.printMsg("End of Single Stage Bode measurements")
      self.Separator()

      return

class CSdatDblog2(CState, CSampMon):
   """
      SDAT DBLOG processing class
   """

   def __init__(self, dut, params=[]):
      TraceMessage( '=' * 80 )
      self.dut    = dut
      self.params = params
      CState.__init__(self, dut, [])

   def run(self):
      try:
         objMsg.printMsg("SDAT DBLOG Class Now Running")
         self.dut.dblData.Tables('P_SDAT_INFO').addRecord(self.dut.objData.retrieve('TEMP_P_SDAT_INFO'))
         self.moveDblog()
         objMsg.printMsg("SDAT DBLOG Class Complete")
      except:
         from sys import exc_info
         objMsg.printMsg('EXCEPTION IN SDAT: Exception was raised in SDAT but contained so that it cannot stop test process')
         sdatExceptionInfo = exc_info()
         objMsg.printMsg('EXCEPTION IN SDAT: type: %s' % sdatExceptionInfo[0])
         objMsg.printMsg('EXCEPTION IN SDAT: value: %s' % sdatExceptionInfo[1])
         objMsg.printMsg('EXCEPTION IN SDAT: traceback: %s' % traceback.format_exc())
      return

   def moveDblog(self):
      """Completes the drive info data only found on PF3 side and places everything in BIN file [name = drive S/N] and then FTPs it over to the SDAT server"""
      import struct

      objTest = CSetup() # create test object
      objTest.create_P_EVENT_SUMMARY_TABLE()

      SpecBuildReq = str(self.dut.sbr)
      TimeStamp = time.localtime()
      DateStr = time.strftime("%Y-%m-%d",TimeStamp)
      ClockStr = time.strftime("%H-%M-%S", TimeStamp)
      sendFileName = HDASerialNumber + '_' + SpecBuildReq + '_' + DateStr + '_' + ClockStr + '.bin'

      resFile = GenericResultsFile(sendFileName)
      resFile.open('w')
      objMsg.printMsg("File: %s, Path: %s"%(sendFileName, pn2Prj.get(self.dut.partNum,pn2Prj.get('DEF',self.dut.partNum))))

      # Now append the binary data from T288
      binFileName = os.path.join(ScrCmds.getSystemPCPath(), "sdatfile", CFSO().getFofFileName(0))
      binFileSize = os.path.getsize(binFileName)
      objMsg.printMsg("sdatfile Binary filesize : %s"%binFileSize)
      binFile = open(binFileName, 'r')
      binData = binFile.read()
      binFile.close()
      resFile.write(binData)

      Info = self.dut.objData.retrieve('TEMP_P_SDAT_INFO')
      #format of the struct being written
      StructString = ('<13s10s8s8s11s16sHfff12sHHHHf8sHH8sHH9s21s10s14s10s4s8s5s')

      DataCollected = Info['TMR_VERIFY'] | Info['TRACK_FOLLOW'] | Info['ZEST'] | Info['VIBE'] | Info['BODES'] | Info['SERVO_LIN'] | Info['MDW_REL'] | Info['CTRL_NOTCH'] | Info['UACT_GAIN_CAL'] | Info['WIRRO_SQ'] | Info['XV_TRANSFER_FUNC']
      objMsg.printMsg("Tests Run %s" % DataCollected )
      runTime = (time.time() - self.dut.birthtime) / 3600.00
      if testSwitch.FE_0159477_350037_SAMPLE_MONITOR == 1:
         TruthVal = TD.Truth
         SampMonFlag = 1
      else:
         TruthVal = 0
         SampMonFlag = 0
      #header: uin32 (length s.size + header length (12)) uint16 (Record Type (0001)) uint16 (Revision (17)) uint16 (Error Code (0)) uint16 (Details (0))
      #header = struct.Struct( 'LHHHH' ) #uint32 uint16 uint16 uint16 uint16
      #headerValues are ( (12 + (length of each of the values (look at StructString for format sizes)), 1, 17, 0, 0 ) #12 is header length other is other length
      headerValues = ( (12 + (13+10+8+8+11+16+2+4+4+4+12+2+2+2+2+4+8+2+2+8+2+2+9+21+10+14+10+4+8+5)), 1, 17, 0, 0 ) #12 is header length other is other length
      DriveInfoHeader = struct.pack('LHHHH', *headerValues)
      values = (Info['SBR'], Info['START_DATE'], Info['SN'], Info['INTERFACE'], Info['TESTER'], Info['SLOT_NUM'], Info['TEMP'],
         Info['VOLTS_3'], Info['VOLTS_5'], Info['VOLTS_12'], Info['PROJECT'], Info['PLOT_TYPE'], Info['CUSTOM_RV'], TruthVal,
         DataCollected, runTime, Info['START_TIME'], Info['SEQ_NUM'], Info['ERROR_CODE'], Info['FAIL_TEST'], SampMonFlag,
         Info['TruthChangeForFail'], Info['CM_REV'],Info['HOST_REV'],Info['PRODUCT'],Info['CONFIG'],Info['SCN'],
         Info['RIM_TYPE'],Info['BIRTH_DATE'],str(Info['SDATOnlyOper']))
      DriveInfoValues = struct.pack( StructString, *values )
      resFile.write(DriveInfoHeader)
      resFile.write(DriveInfoValues)

      resFile.close()

      RequestService('SetResultDir', '')

      # FTP the BIN file over to the SDAT server
      try:
         # If DataCollected has a value of 0 no tests were run. This should only happen if an invalid truthValue was passed into Sample Monitor.
         if (DataCollected == 0) and (Info['ERROR_CODE'] == 0):
            objMsg.printMsg('No data other than Drive Info was collected. Files not sent to FTP site!!')
         else:
            RequestService("SendGenericFile", ((sendFileName,), "SDAT"))
            if not testSwitch.virtualRun:
               ftpServers = RequestService('GetSiteconfigSetting','AltFtpServers')[1].get('AltFtpServers', {})
               altServerKey = "SDAT"
               if altServerKey not in ftpServers:
                  objMsg.printMsg('Files not sent to FTP site!!.  Site Config not set up for server %s' %altServerKey)
               else:
                  if not(self.dut.driveattr.get('BRAZIL_PROC','N') == 'Y' and testSwitch.CheckBrazilProc):
                     ftpPath = ftpServers[altServerKey]['Servers'][0] + ftpServers[altServerKey]['InitialDir']
                  else:
                     ftpPath = ftpServers[altServerKey]['InitialDir']

                  objMsg.printMsg('File successfully sent via FTP to %s' %ftpPath)
      except:
         objMsg.printMsg("FTP of SDAT/DBLOG/BIN file: %s failed." % sendFileName, objMsg.CMessLvl.DEBUG)
      resFile.delete()
      objMsg.printMsg("Result File deleted!")

      # If the sample monitor flag is enabled and SDAT has run send a message to the
      # server that indicates that SDAT completed successfully on this drive.
      # If this run was a report on failure only the TruthVal will be 0, in that case
      # do not update as the run would not count as an actual run
      if testSwitch.FE_0159477_350037_SAMPLE_MONITOR == 1 and (TruthVal != 0):
         if Info['TruthChangeForFail'] == 0:
            data = self.ProcessSampleComplete( self.dut.nextOper, 'SDAT', self.dut.partNum, self.dut.sbr, '' )
         else: #Send complete on FAILURE
            data = self.ProcessSampleComplete( self.dut.nextOper, 'SDAT_F', self.dut.partNum, self.dut.sbr, '' )
         if data == 0:
            objMsg.printMsg("Sample monitor completion data sent!")
         else:
            objMsg.printMsg("Error during attempt to send sample monitor completion data!")

      self.dut.dblData.delTable('P_EVENT_SUMMARY', deleteRecords = 1)

      return

