#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: base Serial Port calibration states
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/06 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_Temperature.py $
# $Revision: #2 $
# $DateTime: 2016/05/06 00:36:23 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_Temperature.py#2 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
from State import CState
import MessageHandler as objMsg


#----------------------------------------------------------------------------------------------------------
class CRampDown(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from Rim import objRimType
      try:
         if not objRimType.isNeptuneRiser():
            return

         Next_Op = self.dut.operList[self.dut.operList.index(self.dut.nextOper) + 1]
      except:
         objMsg.printMsg("Invalid operation list or hardware. Cannot perform early rampdown")
         return

      Next_Temp = TP.temp_profile[Next_Op][0]*10
      objMsg.printMsg("Early RampDown for Neptune Next_Op=%s Next_Temp=%s" % (Next_Op, Next_Temp))
      RampToTempNoWait(Next_Temp)


#----------------------------------------------------------------------------------------------------------
class CThermistor_SF3(CState):
   """
      Read SF3 drive thermistor temperature
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from Temperature import CTemperature
      GEM_REC = self.params.get('GEM_REC_TEMP_ONLY', 0)
      N2_REC = self.params.get('N2_REC_TEMP_ONLY', 0)
      PERFORM_CS = self.params.get('PERFORM_COOLING_STEPS', 1)
      CTemperature().tempMonitoring(SF3 = True, GEM_REC_TEMP_ONLY = GEM_REC, N2_REC_TEMP_ONLY = N2_REC, PERFORM_COOLING_STEPS = PERFORM_CS)
      if testSwitch.FE_0194098_322482_SCREEN_DETCR_OPEN_CONNECTION:
         from Process import CProces
         self.oProc = CProces()
         self.oProc.St(TP.DETCR_OpenScr_186)


#----------------------------------------------------------------------------------------------------------
class CThermistor_F3(CState):
   """
      Read F3 drive thermistor temperature
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from Temperature import CTemperature
      GEM_REC = self.params.get('GEM_REC_TEMP_ONLY', 0)
      N2_REC = self.params.get('N2_REC_TEMP_ONLY', 0)
      PERFORM_CS = self.params.get('PERFORM_COOLING_STEPS', 1)
      CTemperature().tempMonitoring(SF3 = False, GEM_REC_TEMP_ONLY = GEM_REC, N2_REC_TEMP_ONLY = N2_REC, PERFORM_COOLING_STEPS = PERFORM_CS)


#----------------------------------------------------------------------------------------------------------
class CWaitTemp(CState):
   """
      Wait for temperature to settle
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):

      CellTemp = ReportTemperature()/10.0
      objMsg.printMsg("CWaitTemp: Current cell temperature is "+str(CellTemp)+"C.", objMsg.CMessLvl.IMPORTANT)

      if not ConfigVars[CN]['BenchTop']:
         # reqTemp, minTemp, maxTemp = temp_profile[DriveAttributes.get('SET_OPER',ConfigVars[CN].get("SET_OPER",'DEF'))]
         reqTemp, minTemp, maxTemp = TP.temp_profile[self.dut.nextOper]
         from Cell import theCell
         from Drive import objDut
         theCell.setTemp(reqTemp, minTemp, maxTemp, self.dut.objSeq, objDut) #Breaks bench cell so we don't execute this if BenchTop set true

