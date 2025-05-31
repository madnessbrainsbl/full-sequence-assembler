#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2009, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Temperature Module
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/12/15 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Temperature.py $
# $Revision: #7 $
# $DateTime: 2016/12/15 19:55:01 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Temperature.py#7 $
# Level: 3

#---------------------------------------------------------------------------------------------------------#
from Constants import *
from Process import CProcess
import ScrCmds, time

from Drive import objDut   # usage is objDut[PortIndex]
from TestParamExtractor import TP
import MessageHandler as objMsg
import sptCmds, serialScreen
import re
import Exceptions

from Utility import timoutCallback

from Cell import theCell
from Rim import objRimType
from PowerControl import objPwrCtrl


DEBUG = 0
FAST_DEBUG = 0

#######################################################################################################################
#
#                  class:  CTemperature
#
#        Original Author:  Michael T. Brady
#
#            Description:  All functions temperature related.
#
#          Prerrequisite:  None
#
#######################################################################################################################



class CTemperature(CProcess):
   def __init__(self):
      CProcess.__init__(self)
      self.unitTest = {}
      self.unitTest['waitForTempRamp'] = {}
      self.unitTest['waitForTempRamp']['output'] = []


   def verifyHDASaturation(self):
      if not ( ConfigVars[CN]['BenchTop'] ):
         tempSaturationDifferentialReq = TP.tempSaturation_DifferentialReq.get(objDut.nextOper, 6)
         if tempSaturationDifferentialReq == -1:
            if objDut.powerLossEvent == 1:
               if  self.dut.nextOper == 'STS' and (objDut.powerLossState == 'INIT' or objDut.powerLossState == 'DNLD_CODE'): #only run in normal CERT, exclude from STS oper.
                   return
               else :
                   #special case of don't check- unless in power loss recovery... then we use default
                   tempSaturationDifferentialReq = 6
            else:
               return

         objMsg.printMsg("Verifying HDA temperature is saturated.")

         #Get the cell temp
         temp=(ReportTemperature())/10.0
         hdaTemp = self.getHDATemp()

         if testSwitch.FE_0163145_470833_P_NEPTUNE_SUPPORT_PROC_CTRL20_21:
            self.dut.updateCellTemp(temp)
            self.dut.updateDriveTemp(hdaTemp)

         tmo = timoutCallback( TP.tempSaturation_maxWaitTime*60, ScrCmds.raiseException, 10606)

         if testSwitch.BF_0154839_231166_P_USE_CERT_TEMP_REF_HDA_SATURATION:


            #Get the current setpoint temp for the process... 30 is about the cutover for ambient target
            if TP.temp_profile[self.dut.nextOper][0] > 30:
               if self.dut.sptActive.getMode() == self.dut.sptActive.availModes.mctBase:
                  certTemp = self.retHDATemp(certTemp = 1)
               else:
                  # For non MCT codes lets just use attribute for cert temp. Early process with MCT might need to pull value
                  #   if out of sync with server
                  objMsg.printMsg("HDA TEMP %f"%float(hdaTemp))
                  certTemp = float(self.dut.driveattr.get('CERT_TEMP', hdaTemp)) #default to hdaTemp for non-connected systems
                  objMsg.printMsg("Cert TEMP %f in F3"%float(certTemp))

               if testSwitch.BF_0178740_470167_P_CHECK_CERT_TEMP_VALUE_ON_PWL and objDut.powerLossEvent == 1 and self.dut.nextOper == 'PRE2':
                  certTemp = int(self.dut.driveattr.get('CERT_TEMP',0))

               if certTemp == 0:
                  certTemp = (ReportTemperature())/10.0
                  objMsg.printMsg("Cert temp invalid. Will cell temp data instead and set spec = 10")
                  tempSaturationDifferentialReq = 10

               refTemp = lambda : certTemp
               objMsg.printMsg("Hot temp saturation detected- using CERT_TEMP (%dC) reference temp." % (refTemp(),))
               rampHot = True
            else:
               refTemp = lambda : (ReportTemperature())/10.0
               objMsg.printMsg("Cold temp saturation detected- using cell  (%dC) reference temp." % (refTemp(),))
               rampHot = False


            while (abs(hdaTemp-refTemp()) > tempSaturationDifferentialReq):
               if rampHot and testSwitch.FE_0154841_231166_P_USE_SEEKS_HEAT_HDA:
                  self.heatHDASeeks()
               else:
                  time.sleep(30)

               hdaTemp = self.getHDATemp()

               #evaluate timeout
               tmo()
               if testSwitch.virtualRun:
                  break
            objMsg.printMsg("Actual abs temp differential between refTemp and HDA = %f" % (abs(hdaTemp-refTemp())))
         else:
            while (abs(hdaTemp-temp) > tempSaturationDifferentialReq):
               time.sleep(30)

               temp=(ReportTemperature())/10.0
               hdaTemp = self.getHDATemp()

               #evaluate timeout
               tmo()
               if testSwitch.virtualRun:
                  break

            objMsg.printMsg("Actual abs temp differential between cell and HDA = %f" % (abs(hdaTemp-temp)))

   def heatHDASeeks(self):
      """
      Calls requisite SF3 or F3 function to heat HDA for 30 seconds via random seeks
      """
      if self.dut.sptActive.getMode() == self.dut.sptActive.availModes.mctBase:
         return self.heatHDASeeks_SF3()
      else:
         return self.heatHDASeeks_F3()

   def heatHDASeeks_SF3(self):
      """
      Performs random seeks for 30 seconds via SF3
      """
      SetFailSafe()
      try:
         ret = self.St(TP.heatHDA_Seeks_prm)
      finally:
         ClearFailSafe()
      return ret

   def heatHDASeeks_F3(self):
      """
      Performs random seeks for 30 seconds via F3
      """
      oSer = serialScreen.sptDiagCmds()
      sptCmds.enableDiags()
      try:
         oSer.randSeeks(mode = 'R',  duration = 0.5) #30 seconds of random read seeks
      except:
         pass
      sptCmds.enableESLIP()
      return [0,0,0,0]

   def getChannelDieTemp(self):
      """
      Returns the Channel Die Temperature of drive, currently supports SF3 only
      """
      ret = ''
      if self.dut.sptActive.getMode() == self.dut.sptActive.availModes.mctBase:
         try:
            ret = self.St(TP.ChannelDieTempPrm_172)

         except ScriptTestFailure, (failData):
            if failData[0][2] == 11144 and testSwitch.FE_0173689_231166_ENABLE_DIE_TEMP_FAIL:
               ScrCmds.raiseException(11144, 'Die temp exceeded pre-set maximum and potentially damaged part.', Exceptions.ExcessiveDieTempException)

      return ret

   def getHDATemp(self):
      """
      Returns the HDA temp of drive from SF3 or F3
      """
      if self.dut.sptActive.getMode() == self.dut.sptActive.availModes.mctBase:
         return self.retHDATemp()
      else:
         return self.getF3Temp()

   def getCellTemperature(self, ):
      cellTempFlt = float((ReportTemperature())/10.0)
      objMsg.printMsg("getCellTemperature/ Cell temperature in Celsius: %f" % ( cellTempFlt ))


   def getF3Temp(self):
      """
      Returns the HDA temp of drive from F3
      """
      initialMode = self.dut.sptActive.getMode()

      oSerial = serialScreen.sptDiagCmds()
      sptCmds.enableDiags(retries = 2)
      sptCmds.gotoLevel('T')
      data = ''
      try:
         data = sptCmds.sendDiagCmd(CTRL_B, timeout=30, printResult=True)
      except:
         data = sptCmds.execOnlineCmd(CTRL_B, timeout = 30, waitLoops = 100)
         objMsg.printMsg("execOnlineCmd thermistor reading=%s" % (data))
      #oSerial.PChar(CTRL_T)

      Pat = re.compile(', (?P<thermistor>\d+)d\r\n')
      Mat = Pat.search(data)

      thermistor = -1
      if Mat:
         thermistor = int(Mat.groupdict()['thermistor'])
         if DEBUG:
            objMsg.printMsg("Thermistor = %s" % (thermistor))
      else:
         ScrCmds.raiseException(11175, "Failed to get F3 Temperature")

      if objRimType.CPCRiser():
         oSerial.PChar(CTRL_T)
      elif (self.dut.sptActive.getMode() != initialMode) and objRimType.IOInitRiser():
         objPwrCtrl.powerCycle(ataReadyCheck = False)    # Do drive and rim power cycle

      return thermistor

   def getDeviceTemp(self, devSelect=3):
      """
      Dev: 2, Returns the HDA temperature
      Dev: 3, Returns the temperature of SOC
      """
      temperature = -1
      sptCmds.gotoLevel('7')

      if devSelect==2:
         data = sptCmds.sendDiagCmd("D", timeout=30, printResult=True)
         if testSwitch.virtualRun:
            data = "Ref voltage 0000 Thermistor voltage 0F80 Thermistor temp in degrees C 0019, 25d"
         Pat = re.compile(', (?P<temperature>\d+)')
         Mat = re.search(Pat, data)
         if Mat:
            temperature = float(Mat.groupdict()['temperature'])
         else:
            ScrCmds.raiseException(11175, "Failed to get F3 Temperature")

      elif devSelect==3:
         data = sptCmds.sendDiagCmd("D,3", timeout=30, printResult=True)
         if testSwitch.CHEOPSAM_LITE_SOC: #CheopsLite SOC, read SOC temp from Channel sensor
            if testSwitch.virtualRun:
               data = "SRC temp in degree C 01CD, 46.1"
            Pat = 'SRC temp in degree C\s*\w*,\s*(?P<SOC_TEMP>[-+]?[0-9]*\.?[0-9]*)'
         else:
            if testSwitch.virtualRun:
               data = "Channel temp in degrees C 0206, 52"
            Pat = 'Channel temp in degrees C\s*\w*,\s*(?P<SOC_TEMP>[-+]?[0-9]*\.?[0-9]*)'
         Mat = re.search(Pat, data)
         if Mat:
            temperature = float(Mat.groupdict()['SOC_TEMP'])
         else:
            ScrCmds.raiseException(11175, "Failed to get F3 Temperature")

      if DEBUG:
         objMsg.printMsg("Temperature = %s" % (temperature))
      return temperature


   def retHDATemp(self, certTemp = 0, numRetries = 0, driveTempDiodeRangeLimit = 100):
      """
      Simple function to get the temperature of the drive
      @type certTemp: integer
      @param certTemp: switch to use the CERT Temp as opposed to active drive temperature
      @type numRetries: integer
      @param numRetries: Workaround switch to read the diode multiple times to see if anomalous values are being reported
      @type driveTempDiodeRangeLimit: integer
      @param driveTempDiodeRangeLimit: Limit for the acceptable range of values in Celsius accepted between successive temp diode calls (T172, CWORD1 = 17).

      """

      if certTemp == 0:

         tempsList = []

         for retry in range(0, numRetries+1):    # there is a plus one here so that in the baes case we call the temperature measurement at least once
            # take the standard path if not retries
            self.St({'test_num':172, 'prm_name':'HDA TEMP', 'timeout': 200, 'CWORD1': (17,)})

            drive_temp_C = DriveVars['Drive_Temperature_Deg_C']

            # fail the drive if the drive temperature can not be contained inside of a 1 signed byte
            if (drive_temp_C >= 127) or (drive_temp_C <= -128):
               ScrCmds.raiseException(12179, "Drive Temp is greater than 127 or less than -128: %s" % str(drive_temp_C))
            tempsList.append(drive_temp_C)

         driveTempDiodeRange = max(tempsList) - min(tempsList)
         if driveTempDiodeRange > driveTempDiodeRangeLimit:
            objMsg.printMsg('Drive Temp diode values are suspected to be anomalous.', objMsg.CMessLvl.IMPORTANT)
            objMsg.printMsg('Range of values is: %s which exceeded limit of %s' % (str(driveTempDiodeRange), str(driveTempDiodeRangeLimit)), objMsg.CMessLvl.IMPORTANT)
            ScrCmds.raiseException(12179, "Variation in multiple drive temp diode readings was too high.")

         # this is only used for debug to enable 2 Temp CERT.
         if (self.dut.objData.marshallObject.get('NEXT_STATE', 'NULL') == 'TCC_CAL') and (FAST_DEBUG >= 3):
            return 25
         else:
            return DriveVars['Drive_Temperature_Deg_C']


      else:
         self.St({'test_num':172, 'prm_name':'CERT TEMP', 'timeout': 200, 'CWORD1': (18,)})
         drive_temp_C = DriveVars['Cert_Temperature_Deg_C']
         # check to see if the drive_temp is a value outside of a signed 1-byte

         if (drive_temp_C >= 127) or (drive_temp_C <= -128):
            ScrCmds.raiseException(12179, "CERT Temp is greater than 127 or less than -128")

         return DriveVars['Cert_Temperature_Deg_C']

   def setCERTTemp(self, temp):
      """
      Sets the cert temperature in the RAP via SF3
      """
      self.St({'test_num':178, 'prm_name':'Set CERT Temp', 'CERT_TEMPERATURE': temp, 'timeout': 500, 'CWORD2': (32,), 'CWORD1': (8740,)})
      self.St({'test_num':172, 'prm_name':'CERT TEMP', 'timeout': 200, 'CWORD1': (18,)})
      if not DriveVars['Cert_Temperature_Deg_C'] == temp and not testSwitch.virtualRun:
         ScrCmds.raiseException(11175, "Failed to set CERT Temperature")
      self.dut.driveattr['CERT_TEMP'] = temp



   #
   def waitForTempRamp(self, minTempDelta, tempMargin, minTempInAFH3):
      #######################################################################################################################
      #
      #               Function:  waitForTempRamp
      #
      #        Original Author:  Mike Magill / Michael T. Brady
      #
      #
      #                  Input:  None
      #
      #                 Return:  tccStructDict(dict)  A structure of other dictionaries holding the raw data to be computed.
      #
      #######################################################################################################################
      if ConfigVars[CN]['BenchTop'] == 1:
         return 0

      minTempMargin = 2
      retryLimit = 50

      certTemperature = minTempInAFH3
      if testSwitch.virtualRun and testSwitch.unitTest:
         certTemperature, curTemp = self.getTempsForUnitTesting()

      #Spin-down drive to allow quicker cooling
      if not testSwitch.TCC_MEASTEMP_SPIN_ENABLED:
         self.St(TP.spindownPrm_2)
      else:
         self.St(TP.spinupPrm_1)

      if testSwitch.WA_0136676_7955_P_POWER_DOWN_DELAY_AFTER_PARTICLE_SWEEP:
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=600, onTime=10, useESlip=1) # poweroff for 10 min


      curTemp = self.retHDATemp()

      #if slope is neg then we need to increase temp
      #if slope is pos then we need to decrease temp
      slope = (certTemperature - curTemp)/abs(certTemperature - curTemp)

      if slope >=0:
         self.waitForTempRampDown(minTempDelta, tempMargin, minTempInAFH3)
      else:
         self.waitForTempRampUp(minTempDelta, tempMargin)



   #
   def waitForTempRampDown(self, minTempDelta, tempMargin, minTempInAFH3):
      #######################################################################################################################
      #
      #               Function:  waitForTempRampDown
      #
      #        Original Author:  Mike Magill / Michael T. Brady
      #
      #            Description:  Wait for a temperature change between the current temp minus CERT temp to be
      #                          less than a specified amount, specifically:
      #                          wait for (current temp - CERT temp) < (minTempDelta + tempMargin)
      #
      #          Prerrequisite:  run getTCCData
      #
      #                  Input:  None
      #
      #                 Return:  tccStructDict(dict)  A structure of other dictionaries holding the raw data to be computed.
      #
      #######################################################################################################################


      if ConfigVars[CN]['BenchTop'] == 1:
         return 0

      objMsg.printMsg("waitForTempRampDown/ Ramping to verified temperature differential", objMsg.CMessLvl.DEBUG)

      minTempMargin = 2
      retryLimit = 90
      retry = 0
      addtionalTemp = 0 
      additionalTempDelta = TP.temp_profile.get('additionalTempDelta',0) #Additional delta to heat up the drive in VER_RAMP, set to zero if want to disable

      certTemperature = minTempInAFH3
      if testSwitch.virtualRun:
         certTemperature, curTemp = self.getTempsForUnitTesting()

      #Spin-down drive to allow quicker cooling
      if not testSwitch.TCC_MEASTEMP_SPIN_ENABLED and not testSwitch.FE_0258915_348429_COMMON_TWO_TEMP_CERT:
         self.St(TP.spindownPrm_2)
      else:
         self.St(TP.spinupPrm_1)

      if testSwitch.WA_0136676_7955_P_POWER_DOWN_DELAY_AFTER_PARTICLE_SWEEP:
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=600, onTime=10, useESlip=1) # poweroff for 10 min

      #Perform initial ramp to temp outside of loop to get cell saturated even if drive is cold start.
      reqTemp, minTemp, maxTemp = TP.temp_profile[self.dut.nextOper]
      objMsg.printMsg("Cell Temp %d" % (ReportTemperature()/10.0))
      objMsg.printMsg("Ramping to %d (%d,%d)" % (reqTemp, minTemp, maxTemp))
      theCell.setTemp(reqTemp, minTemp, maxTemp, self.dut.objSeq, objDut) # Breaks bench cell

      #Read the current drive temp
      curTemp = self.retHDATemp()

      msg0 = "waitForTempRampDown/ During - retry: %2d, curTemp: %s, certTemperature: %s, minTempDelta: %s, tempMargin: %s, additionalTempDelta: %s" % \
         (retry, curTemp, certTemperature, minTempDelta, tempMargin, additionalTempDelta)
      objMsg.printMsg(msg0)
      self.unitTest['waitForTempRamp']['output'].append( msg0 )

      # Save the cert temp with occurrence = 3
      CellTemp = (ReportTemperature()/10.0)
      DriveTemp = certTemperature
      self.dut.dblData.Tables('P_TEMPERATURES').addRecord(
               {
               'SPC_ID'       : 0,
               'OCCURRENCE'   : 3,
               'SEQ'          : self.dut.seqNum+1,
               'TEST_SEQ_EVENT': 0,
               'STATE_NAME'   : self.dut.nextState,
               'DRIVE_TEMP'   : DriveTemp,
               'CELL_TEMP'    : CellTemp,
               })

      # Save the current temp before looping with occurrence = 1
      DriveTemp = curTemp
      self.dut.dblData.Tables('P_TEMPERATURES').addRecord(
               {
               'SPC_ID'       : 0,
               'OCCURRENCE'   : 1,
               'SEQ'          : self.dut.seqNum+1,
               'TEST_SEQ_EVENT': 0,
               'STATE_NAME'   : self.dut.nextState,
               'DRIVE_TEMP'   : DriveTemp,
               'CELL_TEMP'    : CellTemp,
               })
      while 1:
         if testSwitch.FE_0258915_348429_COMMON_TWO_TEMP_CERT:
            curTempDelta  = curTemp - certTemperature - tempMargin
         else:
            curTempDelta  = certTemperature - curTemp - tempMargin
         if curTempDelta >= (minTempDelta + additionalTempDelta): # try to achieve tempdelta + additionalTempDelta
            break
         if retry > retryLimit:
            if curTempDelta >= minTempDelta: #pass the drive if can achieve minTempDelta
               break

            if ConfigVars[CN].get('hotBenchTop', 0) == 1:
               return 0
            else:
               CellTemp = (ReportTemperature()/10.0)
               DriveTemp = curTemp
               self.dut.dblData.Tables('P_TEMPERATURES').addRecord(
                        {
                        'SPC_ID'       : 0,
                        'OCCURRENCE'   : 2,
                        'SEQ'          : self.dut.seqNum+1,
                        'TEST_SEQ_EVENT': retry,
                        'STATE_NAME'   : self.dut.nextState,
                        'DRIVE_TEMP'   : DriveTemp,
                        'CELL_TEMP'    : CellTemp,
                        })
               objMsg.printMsg("cell temp =%sC drive temp =%sC" % (CellTemp, DriveTemp))
               ScrCmds.raiseException(12517, "Failed to achieve required temperature differential: %s" % (minTempDelta + tempMargin))

         if testSwitch.WA_0110324_357260_POWER_CYCLE_TO_READ_TEMP:
            objPwrCtrl.powerCycle(useESlip=1)         # Power cycle to get new temp
            curTemp = self.retHDATemp()
            self.St(TP.spindownPrm_2)           # Spin back down
         else:
            curTemp = self.retHDATemp()

         if testSwitch.virtualRun:
            certTemperature, curTemp = self.getTempsForUnitTesting()

         reqTemp, minTemp, maxTemp = TP.temp_profile[self.dut.nextOper]
         cellDif = (ReportTemperature()/10.0) - reqTemp
         objMsg.printMsg("Cell Temp %d" % (ReportTemperature()/10.0))
         if cellDif >= 0:
            if retry != 0:
               tempMaxTemp =  reqTemp + (0.5 * cellDif) + minTempMargin #Take 50% steps to achieve longer HDA saturation
               if tempMaxTemp < maxTemp:
                  maxTemp = tempMaxTemp
            if objRimType.CPCRiser():
               objMsg.printMsg("Ramping to %d (%d,%d)" % (reqTemp, minTemp, maxTemp))
               theCell.setTemp(reqTemp+addtionalTemp, minTemp+addtionalTemp, maxTemp+addtionalTemp, self.dut.objSeq, objDut)
               #Soak HDA at lower temp
            ScriptPause(60)
            retry += 1
         else:
            if objRimType.CPCRiser():
               theCell.setTemp(reqTemp+addtionalTemp, minTemp+addtionalTemp, maxTemp+addtionalTemp, self.dut.objSeq, objDut)
               #Soak HDA a little longer
            ScriptPause(60)
         #
         msg0 = "waitForTempRampDown/ During - retry: %2d, curTemp: %s, certTemperature: %s, minTempDelta: %s, tempMargin: %s" % \
            (retry, curTemp, certTemperature, minTempDelta, tempMargin)
         objMsg.printMsg(msg0)
         self.unitTest['waitForTempRamp']['output'].append( msg0 )

         if retry == 10:
            addtionalTemp = 2 
            objMsg.printMsg("Increase cell temperature by %sC from the set temp %sC." %(addtionalTemp,reqTemp))
            theCell.setTemp(reqTemp+addtionalTemp, minTemp+addtionalTemp, maxTemp+addtionalTemp, self.dut.objSeq, objDut)
      #
      objMsg.printMsg("waitForTempRampDown/ end of while loop.")

      CellTemp = (ReportTemperature()/10.0)
      DriveTemp = curTemp
      self.dut.dblData.Tables('P_TEMPERATURES').addRecord(
               {
               'SPC_ID'       : 0,
               'OCCURRENCE'   : 2,
               'SEQ'          : self.dut.seqNum+1,
               'TEST_SEQ_EVENT': retry,
               'STATE_NAME'   : self.dut.nextState,
               'DRIVE_TEMP'   : DriveTemp,
               'CELL_TEMP'    : CellTemp,
               })
      objMsg.printMsg("cell temp =%sC drive temp =%sC" % (CellTemp, DriveTemp))

      if testSwitch.WA_0139361_395340_P_PARTICLE_AGITATION_IO_PLUG:
         curTemp = self.retHDATemp()
         if curTemp > 29:
            objMsg.printMsg("waitForTempRampDown/ Current Temp %d more than 29C" % curTemp)
            theCell.setTemp(reqTemp+addtionalTemp, minTemp+addtionalTemp, maxTemp+addtionalTemp, self.dut.objSeq, objDut)
            objMsg.printMsg("waitForTempRampDown/ Wait temp 10 minute.")
            ScriptPause(600)
            curTemp = self.retHDATemp()
         objMsg.printMsg("waitForTempRampDown/ Current Temp %d." % curTemp)
      self.St(TP.spinupPrm_1)



   #
   def waitForTempRampUp(self, minTempDelta, tempMargin):
      #######################################################################################################################
      #
      #               Function:  waitForTempRampUp
      #
      #        Original Author:  Mike Magill / Michael T. Brady
      #
      #            Description:  Wait for a temperature change between the current temp minus CERT temp to be
      #                          less than a specified amount, specifically:
      #                          while (current temp - CERT temp) > (minTempDelta + tempMargin)
      #
      #          Prerrequisite:  run getTCCData
      #
      #                  Input:  None
      #
      #                 Return:  tccStructDict(dict)  A structure of other dictionaries holding the raw data to be computed.
      #
      #######################################################################################################################


      if ConfigVars[CN]['BenchTop'] == 1:
         return 0

      objMsg.printMsg("Ramping to verified temperature differential", objMsg.CMessLvl.DEBUG)

      minTempMargin = 2
      retryLimit = 150
      driveTempReadingList = []

      curTemp = self.retHDATemp()
      certTemperature = self.retHDATemp(certTemp = 1)
      if testSwitch.virtualRun:
         certTemperature, curTemp = self.getTempsForUnitTesting()

      self.St(TP.spinupPrm_1)


      retry = 0
      #Perform initial ramp to temp outside of loop to get cell saturated even if drive is cold start.
      reqTemp, minTemp, maxTemp = TP.temp_profile[self.dut.nextOper]
      objMsg.printMsg("Cell Temp %d" % (ReportTemperature()/10.0))
      objMsg.printMsg("Ramping to %d (%d,%d)" % (reqTemp, minTemp, maxTemp))

      if objRimType.IsLowCostSerialRiser() and testSwitch.FE_0180754_345172_RAMP_TEMP_NOWAIT_HDSTR_SP:
         RMode = 'nowait'
      else:
         RMode = 'wait'

      theCell.setTemp(reqTemp, minTemp, maxTemp, self.dut.objSeq, objDut,RMode) # Breaks bench cell

      msg0 = "waitForTempRampUp/ During - retry: %2d, curTemp: %s, certTemperature: %s, minTempDelta: %s, tempMargin: %s" % \
         (retry, curTemp, certTemperature, minTempDelta, tempMargin)
      objMsg.printMsg(msg0)
      self.unitTest['waitForTempRamp']['output'].append( msg0 )

      while ((curTemp - certTemperature + tempMargin) < minTempDelta):
         if retry > retryLimit:
            objMsg.printMsg("waitForTempRampUp/ Failed to meet desired temperature delta.  Let the drive continue testing.")
            break


         self.heatHDASeeks()
         curTemp = self.retHDATemp()

         if testSwitch.virtualRun:
            certTemperature, curTemp = self.getTempsForUnitTesting()

         #
         driveTempReadingList.append( curTemp )
         if len(driveTempReadingList) > 10:
            lastTenReadingsDriveTempReadingList = driveTempReadingList[-10:]
            if abs(max(lastTenReadingsDriveTempReadingList) - min(lastTenReadingsDriveTempReadingList)) < 1:
               objMsg.printMsg("waitForTempRampUp/ Minimal to no change in the last 10 readings ... exiting.")
               break


         reqTemp, minTemp, maxTemp = TP.temp_profile[self.dut.nextOper]
         cellDif = (ReportTemperature()/10.0) - reqTemp
         objMsg.printMsg("Cell Temp %d" % (ReportTemperature()/10.0))
         if cellDif >= 0:
            if retry != 0:
               tempMaxTemp =  reqTemp + (0.5 * cellDif) + minTempMargin #Take 50% steps to achieve longer HDA saturation
               if tempMaxTemp < maxTemp:
                  maxTemp = tempMaxTemp
            if objRimType.CPCRiser():
               objMsg.printMsg("Ramping to %d (%d,%d)" % (reqTemp, minTemp, maxTemp))
               theCell.setTemp(reqTemp, minTemp, maxTemp, self.dut.objSeq, objDut) #Breaks bench cell
               #Soak HDA at lower temp
            retry += 1
         else:
            if objRimType.CPCRiser():
               theCell.setTemp(reqTemp, minTemp, maxTemp, self.dut.objSeq, objDut) #Breaks bench cell
               #Soak HDA a little longer
         #
         ScriptPause(2)

         msg0 = "waitForTempRampUp/ During - retry: %2d, curTemp: %s, certTemperature: %s, minTempDelta: %s, tempMargin: %s" % \
            (retry, curTemp, certTemperature, minTempDelta, tempMargin)
         objMsg.printMsg(msg0)
         self.unitTest['waitForTempRamp']['output'].append( msg0 )


      #
      objMsg.printMsg("waitForTempRampUp/ end of while loop.")




   #######################################################################################################################
   #
   #               Function:  getTempsForUnitTesting
   #
   #        Original Author:  Michael T. Brady
   #
   #            Description:  Function to get data from a stack for unit testing purposes only.
   #
   #          Prerrequisite:  Run in VE only.
   #
   #                  Input:  None
   #
   #                 Return:  None
   #
   #######################################################################################################################

   def getTempsForUnitTesting(self, ):

      if testSwitch.FE_0258915_348429_COMMON_TWO_TEMP_CERT:
         certTemperature = 25
         curTemp = 52
      else:
         certTemperature = 52
         curTemp = 25
      if 'waitForTempRamp' in self.unitTest:
         if 'certTemperature' in self.unitTest['waitForTempRamp']:
            certTemperature = self.unitTest['waitForTempRamp']['certTemperature']

         if 'curTempList' in self.unitTest['waitForTempRamp']:
            if len(self.unitTest['waitForTempRamp']['curTempList']) > 0:
               curTemp = self.unitTest['waitForTempRamp']['curTempList'].pop()

      return certTemperature, curTemp


   def measureHumidity(self, saveToRap=0, spc_id=1, keepItParsable=False):
      '''
               Function:  measureHumidity

        Original Author:  Ben T Cordova

            Description:  Logs Humidity information and optionally saves it to the RAP

          Prerrequisite:  None

                  Input:  saveToRap is a flag which toggles bit8 in  CWORD1 in test 235
                          keepItParsable sets DblTablesToParse with the humidity table so we can pull date out of it in

                 Return:  None

      '''

      if testSwitch.extern.FE_0138500_308514_HUMIDITY_SENSOR_SUPPORT:

         t235parm = TP.prm_MeasureHumidity_235

         if saveToRap == 1:
            t235parm = TP.prm_MeasureAndSaveHumidity_235

         if keepItParsable:
            t235parm['DblTablesToParse'] = ['P235_DRIVE_TEMP_HUMIDITY']

         self.St(t235parm, spc_id=spc_id)

   def tempMonitoring(self, SF3 = True, GEM_REC_TEMP_ONLY = 0 ,N2_REC_TEMP_ONLY = 0, PERFORM_COOLING_STEPS = 1):
      #######################################################################################################################
      #
      #               Function:  tempMonitoring
      #
      #        Original Author:  HN Yeo
      #
      #            Description:  Read Drive thermistor temperature
      #                          Fail the drive if drive temp can not achieve minDriveTemp after 60 loops of 1 minutes
      #                          Fail the drive if drive temp is higher than maxDriveTemp for maxOverHeatCount
      #
      #          Prerrequisite:  None
      #
      #                  Input:  None
      #
      #                 Return:  None
      #
      #######################################################################################################################

      """
         Read Drive thermistor temperature
         Fail the drive if drive temp can not achieve minDriveTemp after 60 loops of 1 minutes
         Fail the drive if drive temp is higher than maxDriveTemp for maxOverHeatCount
         Fail the drive if drive temp can not achieve below maxCertTemp after 2 loops of 15 minutes 
      """
      objMsg.printMsg("tempMonitoring, SF3 = %s GEM_REC_TEMP_ONLY = %s, N2_REC_TEMP_ONLY = %s, PERFORM_COOLING_STEPS = %s" % (SF3, GEM_REC_TEMP_ONLY, N2_REC_TEMP_ONLY, PERFORM_COOLING_STEPS))

      if ConfigVars[CN]['BenchTop'] == 1 or testSwitch.virtualRun:
         return

      from Temperature import CTemperature
      counter = 0
      addtionalTemp = 0
      reqTemp, minTemp, maxTemp = TP.temp_profile[self.dut.nextOper]
      minDriveTemp = TP.temp_profile.get('minDriveTemp',(reqTemp-3))
      maxDriveTemp = TP.temp_profile.get('maxDriveTemp',(reqTemp+10))
      maxOverHeatCount = TP.temp_profile.get('maxOverHeatCount',2)
      objMsg.printMsg("tempMonitoring: minDriveTemp =%sC maxDriveTemp =%sC maxOverHeatCount=%s" % (minDriveTemp, maxDriveTemp, maxOverHeatCount))

      from Cell import theCell
      theCell.setTemp(reqTemp, minTemp, maxTemp, self.dut.objSeq, objDut)
      objMsg.printMsg("tempMonitoring: reqTemp =%sC minDriveTemp =%sC maxDriveTemp =%sC " % (reqTemp, minDriveTemp, maxDriveTemp))

      for i in xrange(60):
         CellTemp = ReportTemperature()/10.0
         if SF3 == True:
            objMsg.printMsg("tempMonitoring: SF3 drive temp")
            DriveTemp = CTemperature().retHDATemp(certTemp = 0)
         else:
            objMsg.printMsg("tempMonitoring: F3 drive temp")
            DriveTemp = CTemperature().getF3Temp()

         objMsg.printMsg("tempMonitoring: Loop =%s CellTemp =%sC DriveTemp =%sC" % (i, CellTemp, DriveTemp))

         if i == 0 :
            # Save the cert temp with occurrence = 1
            self.dut.dblData.Tables('P_TEMPERATURES').addRecord(
                     {
                     'SPC_ID'       : 0,
                     'OCCURRENCE'   : 1,
                     'SEQ'          : self.dut.seqNum+1,
                     'TEST_SEQ_EVENT': 0,
                     'STATE_NAME'   : self.dut.nextState,
                     'DRIVE_TEMP'   : DriveTemp,
                     'CELL_TEMP'    : CellTemp,
                     })

         if (cellTypeString == 'Neptune2' and N2_REC_TEMP_ONLY) or (not cellTypeString == 'Neptune2' and GEM_REC_TEMP_ONLY):
            objMsg.printMsg("Temperature recording only, no more looping")
            break

         if DriveTemp < minDriveTemp:
            objMsg.printMsg("Drive not yet reach desired temp. Waiting for another 60sec...")
            ScriptPause(60)

            if i == 0 or i == 30:
               if i == 0:
                  addtionalTemp = 2
                  self.St(TP.spinupPrm_1)
               else:
                  addtionalTemp = 4

               objMsg.printMsg("Increase cell temperature by %sC from the set temp %sC." %(addtionalTemp,reqTemp))
               theCell.setTemp(reqTemp+addtionalTemp, minTemp, maxTemp, self.dut.objSeq, objDut)
               objMsg.printMsg("tempMonitoring: reqTemp =%sC minDriveTemp =%sC maxDriveTemp =%sC " % (reqTemp+addtionalTemp, minDriveTemp, maxDriveTemp))

         elif DriveTemp > maxDriveTemp:
            counter = counter + 1
            if counter == maxOverHeatCount :
               objMsg.printMsg("tempMonitoring: CellTemp =%sC. DriveTemp =%sC, higher than maxDriveTemp(%sC)" % (CellTemp, DriveTemp, maxDriveTemp))
               if cellTypeString == 'Neptune2': 
                  objMsg.printMsg("Please check sled if repeated failures")
               ScrCmds.raiseException(42227, "Drive Temperature above maxDriveTemp after ramp")
               break
            objMsg.printMsg("Drive not yet reach desired temp. Waiting for another 60sec...")
            ScriptPause(60)
         else:
            break

      # Save the drive temp with occurrence = 2, after wait
      self.dut.dblData.Tables('P_TEMPERATURES').addRecord(
               {
               'SPC_ID'       : 0,
               'OCCURRENCE'   : 2,
               'SEQ'          : self.dut.seqNum+1,
               'TEST_SEQ_EVENT': i,
               'STATE_NAME'   : self.dut.nextState,
               'DRIVE_TEMP'   : DriveTemp,
               'CELL_TEMP'    : CellTemp,
               })
      objMsg.printMsg("tempMonitoring: reqTemp =%sC minDriveTemp =%sC maxDriveTemp =%sC " % (reqTemp, minDriveTemp, maxDriveTemp))
      objMsg.printMsg("tempMonitoring: cell temp =%sC drive temp =%sC" % (CellTemp, DriveTemp))
      
      if testSwitch.FE_0258915_348429_COMMON_TWO_TEMP_CERT and PERFORM_COOLING_STEPS:
         maxCertTemp = TP.temp_profile.get('maxCertTemp',(reqTemp+5))

         if DriveTemp > maxCertTemp:
            objMsg.printMsg("tempMonitoring: Drive temp =%sC > maxCertTemp =%sC" % (DriveTemp, maxCertTemp))

            if not testSwitch.FE_0318846_385431_WAIT_FOR_CERT_TEMP_DOWN:
               objMsg.printMsg("Please check ambient temperature if repeated failures")
               ScrCmds.raiseException(42227, "Drive Temperature above maxCertTemp")                    
            else:
               for i in xrange(2):
                  objPwrCtrl.powerOff()
                  objMsg.printMsg("tempMonitoring: Drive not yet reach desired temp. Waiting for another 15mins...")
                  ScriptPause(900)
                  objPwrCtrl.powerOn()
                  CellTemp = ReportTemperature()/10.0
                  if SF3 == True:
                     objMsg.printMsg("tempMonitoring: SF3 drive temp")
                     DriveTemp = CTemperature().retHDATemp(certTemp = 0)
                  else:
                     objMsg.printMsg("tempMonitoring: F3 drive temp")
                     DriveTemp = CTemperature().getF3Temp()
                    
                  objMsg.printMsg("tempMonitoring: Loop =%s CellTemp =%sC DriveTemp =%sC" % (i, CellTemp, DriveTemp))

                  if DriveTemp <= maxCertTemp:
                     objMsg.printMsg("tempMonitoring: Drive temp =%sC <= maxCertTemp =%sC, break" % (DriveTemp, maxCertTemp))
                     objPwrCtrl.powerCycle()
                     break

               # Save the drive temp with occurrence = 3, after power down
               self.dut.dblData.Tables('P_TEMPERATURES').addRecord(
                  {
                  'SPC_ID'       : 0,
                  'OCCURRENCE'   : 3,
                  'SEQ'          : self.dut.seqNum+1,
                  'TEST_SEQ_EVENT': (i+1)*15,
                  'STATE_NAME'   : self.dut.nextState,
                  'DRIVE_TEMP'   : DriveTemp,
                  'CELL_TEMP'    : CellTemp,
                  })                    

               if DriveTemp > maxCertTemp:
                  objMsg.printMsg("tempMonitoring: CellTemp =%sC. DriveTemp =%sC, higher than maxCertTemp(%sC)" % (CellTemp, DriveTemp, maxCertTemp))
                  objMsg.printMsg("Please check ambient temperature if repeated failures")
                  if testSwitch.FE_0318846_385431_FAIL_IF_CERT_TEMP_TOO_HIGH:
                     ScrCmds.raiseException(42227, "Drive Temperature above maxCertTemp after wait")                    
         else:
            objMsg.printMsg("tempMonitoring: Drive temp =%sC <= maxCertTemp =%sC" % (DriveTemp, maxCertTemp))


      if (cellTypeString == 'Neptune2' and N2_REC_TEMP_ONLY) or (not cellTypeString == 'Neptune2' and GEM_REC_TEMP_ONLY):
         objMsg.printMsg("Temperature recording only, return")
         return

      if not addtionalTemp == 0 and self.dut.nextOper == 'PRE2':
         self.dut.driveattr['PRE2_FINAL_TEMP'] = reqTemp+addtionalTemp
         objMsg.printMsg("tempMonitoring: PRE2_FINAL_TEMP =%sC" % (self.dut.driveattr['PRE2_FINAL_TEMP']))

      if DriveTemp < minDriveTemp:
         objMsg.printMsg("tempMonitoring: CellTemp =%sC. DriveTemp =%sC, lower than minDriveTemp(%sC)" % (CellTemp, DriveTemp, minDriveTemp))
         objMsg.printMsg("Please check wedge if repeated failures")
         ScrCmds.raiseException(42226, "Drive Temperature below minDriveTemp after ramp")

      elif DriveTemp > maxDriveTemp:
         objMsg.printMsg("tempMonitoring: CellTemp =%sC. DriveTemp =%sC, higher than maxDriveTemp(%sC)" % (CellTemp, DriveTemp, maxDriveTemp))
         if cellTypeString == 'Neptune2': 
            objMsg.printMsg("Please check sled if repeated failures")
         ScrCmds.raiseException(42227, "Drive Temperature above maxDriveTemp after ramp")
