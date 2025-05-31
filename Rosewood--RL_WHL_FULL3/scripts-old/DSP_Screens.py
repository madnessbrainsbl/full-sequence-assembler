#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: DSP screen specific states
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
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/DSP_Screens.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/DSP_Screens.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
from State import CState
from SampleMonitor import CSampMon
import MessageHandler as objMsg


#----------------------------------------------------------------------------------------------------------
class CDspScreen(CState, CSampMon):
   """
      Description:
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from RdWr import CRdWrOpti
      oRdWr = CRdWrOpti(self.params)
      oRdWr.St(TP.zapPrm_175_zapOff)  ### ZAP OFF ###

      # Run opti on required zones
      DSP_Screen_Zones = [8,9,10,11,12,13,14,15,16] #Prasanna
      from Opti_Base import CSimpleOpti
      optiObj = CSimpleOpti(self.dut, {'ZONES':DSP_Screen_Zones, 'ZONE_POS':TP.VBAR_ZONE_POS, 'DISABLE_ZAP': False})
      #optiObj.run()
      """"
      Prasanna Commented this
      oRdWr.St(TP.DSP_ScanWritePrm_109)       # Perform T109 Write pass
      oRdWr.St(TP.DSP_ScanReadPrm_109)        # Perform T109 Read and Write pass
      """
      #Prasanna - updated here

      try:
         if testSwitch.FE_0135335_342029_P_DETCR_TP_SUPPORT:
            objMsg.printMsg("Starting DETCR")
            objMsg.printMsg("mfr = %s" % self.dut.PREAMP_MFR)
            HGA_SUPPLIER=self.dut.HGA_SUPPLIER
            objMsg.printMsg("HGA_SUPPLIER = %s" % HGA_SUPPLIER)
            T186prm={}
            T186prm.update(TP.prm_186_0001)
            if self.dut.HGA_SUPPLIER == 'RHO':
               if str(self.dut.PREAMP_MFR).find("TI")!= -1:
                  T186prm["INPUT_VOLTAGE"]=(250,)
               else:
                  T186prm["INPUT_VOLTAGE"]=(200,)
            elif self.dut.HGA_SUPPLIER == 'TDK':
               T186prm["INPUT_VOLTAGE"]=(150,)
            else:
               import ScrCmds
               ScrCmds.raiseException(11044, "Preamp info N/A to set T186 Input voltage")
            objMsg.printMsg("Starting T186")
            oRdWr.St(T186prm)
            objMsg.printMsg("End of DETCR")
      except:
         objMsg.printMsg("Exception in DETCR")
         pass

      if testSwitch.FE_0159597_357426_DSP_SCREEN == 1:
         from SampleMonitor import TD
         objMsg.printMsg("DSPtruthValue222 is %x" % TD.Truth)
         DSP_Head =  TD.Truth << 8
         objMsg.printMsg("DSPruthValue223 is %x" %  DSP_Head)
         DSP_Head2 = TD.Truth | DSP_Head
         objMsg.printMsg("MODTruthValue222 is %x" % DSP_Head2)

         #oRdWr.St(TP.DSP_prm_094_NEG)#Run OR'ed comparator CAL
         DSP_094 = oRdWr.oUtility.copy(TP.DSP_prm_094_NEG)#DSP_Read_109 = oRdWr.oUtility.copy(TP.prm_AFS_CM_Read_109)
         DSP_094.update({
         'HEAD_RANGE'         : DSP_Head2,
         })
         oRdWr.St(DSP_094)        # Perform T109 Read LUL

         DSP_Read_109 = oRdWr.oUtility.copy(TP.DSP_LULDefectScanPrm_109)#DSP_Read_109 = oRdWr.oUtility.copy(TP.prm_AFS_CM_Read_109)
         #This is program specific.
         DSP_Read_109.update({
         'HEAD_RANGE'         : DSP_Head2,
         })
         oRdWr.St(DSP_Read_109)        # Perform T109 Read LUL
         #oRdWr.St(TP.DSP_LULDefectScanPrm_109)        # Perform T109 Read LUL
      else:
#############################OR'ed Comparator Pass##########################
         ######Test 94 - Pass
         DSP_prm_094 = oRdWr.oUtility.copy(TP.prm_094_0002)
         DSP_prm_094.update({
         'prm_name' : 'DSP_prm_094_NEG',
         'ZONE_MASK':(0x1,0xFF00),#Run from Zones - 8-16
         'CWORD2'   :(0x82), #Allow manual offset
         'OFFSET'   :(5), #Reducing offset compared to what T109 uses
         "DYNAMIC_THRESH"        : (31,7,1,0x10,1,),  #Bias, Gain, Filter, Polarity, and vthRange 0 = reduced 9 - 102, 1 = full 18-204
         })
         oRdWr.St(DSP_prm_094)#Run OR'ed comparator CAL

         DSP_Read_109 = oRdWr.oUtility.copy(TP.DSP_LULDefectScanPrm_109)#DSP_Read_109 = oRdWr.oUtility.copy(TP.prm_AFS_CM_Read_109)
         #This is program specific.
         DSP_Read_109.update({
         'START_CYL'    : (2,0x22e0),#140K
         'END_CYL'      : (3,0x3450),#210K
         'HEAD_RANGE'         : 0x00F,
         })
         oRdWr.St(DSP_Read_109)        # Perform T109 Read LUL
#############################OR'ed Comparator Pass##########################


      #oRdWr.St(SdatParameters.zapPrm_zapOn)  ### ZAP ON ###
      from PowerControl import objPwrCtrl
      objPwrCtrl.powerCycle(useESlip=1)

      # If the sample monitor flag is enabled and DSP Screen has run send a message to the
      # server that indicates that DSP completed successfully on this drive.
      if testSwitch.FE_0159597_357426_DSP_SCREEN == 1:
         Operation = self.dut.nextOper
         TestName = ''
         HdCount = ''
         SBR = self.dut.sbr
         PartNum = self.dut.partNum
         HdCount = 0

         data = self.ProcessSampleComplete( Operation, TestName, PartNum, SBR, HdCount )
         if data == 0:
            objMsg.printMsg("Sample monitor completion data sent!")
         else:
            objMsg.printMsg("Error during attempt to send sample monitor completion data!")


#----------------------------------------------------------------------------------------------------------
class CInitAFH_DSP(CState):
   """
      Description: Class that will perform a 1 stop AFH Calibrations/testing
      Base: Based on Firebirds calibration routines.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from base_AFH import CInitAFH
      CInitAFH(self.dut, self.params).run()


#----------------------------------------------------------------------------------------------------------
class CInitRAP_DSP(CState):
   """
      Description: Class that will initialize the RAP.  Only to be performed very early in PRE2.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from base_RAP import CInitRAP
      CInitRAP(self.dut, self.params).run()


#----------------------------------------------------------------------------------------------------------
class CReadWriteGapCal_DSP(CState):
   """
      Description: Class that will perform optimization of the reader writer offset calibrations
      Base: Based on AGERE Venus calibration flows.
      Usage: Optionally add an input parameter of 'ZONES' to list specific zones to be optimized.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from RdWr import CRdWrOpti
      oRdWr = CRdWrOpti()

      if testSwitch.MEASCQM_DATA == 1:
         oRdWr.measCQM() #Check post opti cqm for debug

      rwgapParams = oRdWr.oUtility.copy(TP.Writer_Reader_Gap_Calib_176)
      skipsyszone = self.params.get('SKIP_SYS_ZONE', 0) # Default is to include system zone during tuning
      if skipsyszone:
         rwgapParams['CWORD1'] = rwgapParams['CWORD1']|0x0002

      if testSwitch.FE_0159597_357426_DSP_SCREEN == 1:
         from SampleMonitor import TD
         objMsg.printMsg("DSPtruthValue2 is %x" % TD.Truth)
         DSP_Head =  TD.Truth << 8
         objMsg.printMsg("DSPruthValue3 is %x" %  DSP_Head)
         DSP_Head2 = TD.Truth | DSP_Head
         objMsg.printMsg("MODTruthValue is %x" % DSP_Head2)
         rwgapParams['HEAD_RANGE'] = DSP_Head2   #add DSP Head info
         rwgapParams['SPC_ID'] = 10100

      rwgapParams['CWORD1'] = rwgapParams['CWORD1']& 0xBFFF #Clear the save to RAP bit 0x4000
      oRdWr.Writer_Reader_Gap_Calib(rwgapParams, zapFromDut = self.params.get('zapFromDut',0))

