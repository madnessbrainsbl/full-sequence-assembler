#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: base Serial Port calibration states
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/12/08 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_SerialTest.py $
# $Revision: #8 $
# $DateTime: 2016/12/08 01:18:29 $
# $Author: yihua.jiang $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_SerialTest.py#8 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
from State import CState
import MessageHandler as objMsg
from PowerControl import objPwrCtrl
import ScrCmds
from Process import CProcess
import re
import os
from ICmdFactory import ICmd


#----------------------------------------------------------------------------------------------------------
class CCustUniqSAPCfg(CState):
   """
      Description: Class that will perform customer unique SAP configuration.
      Base: Based on Moose shock sensor SAP setting process.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def ZGSEnabled(self, pn):
      '''
      Function determines a ZGS capable drive based on the part number's 4th character
      (eg. 'G'). Checking is based on TestParameter.py 'optionsByPN_re' dictionary.
      '''
      for pnRe in getattr(TP,"optionsByPN_re",{}):
          srchRslt = re.compile(pnRe)
          if srchRslt.match(pn) and ('ZGS' in TP.optionsByPN_re[pnRe]):
             return TP.optionsByPN_re[pnRe]['ZGS']
      return None

   #-------------------------------------------------------------------------------------------------------
   def RVEnabled(self, pn):
      '''
      '''
      for pnRe in getattr(TP,"optionsByPN_re",{}):
          srchRslt = re.compile(pnRe)
          if srchRslt.match(pn) and ('RV' in TP.optionsByPN_re[pnRe]):
             return TP.optionsByPN_re[pnRe]['RV']
      return None

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      objMsg.printMsg(20*'*' + "Updating servo features based on Part Number or Business Broup" + 20*'*')

      self.oProc = CProces()

      #JBF: Do I need code here which spins the drive up and down?  Moose did...

      # Locate the entry in the option table which matches this part number
      partNum = self.dut.partNum

      partNumREs = optionsByPN_re.keys()
      srchRslt = None
      for pnRe in partNumREs:
         srchRslt = re.search(pnRe, partNum)
         if srchRslt != None:
            rvffOption        = TP.optionsByPN_re[pnRe]['RVFF']
            shockSensorOption = TP.optionsByPN_re[pnRe]['shock sensor']
            swotOption        = TP.optionsByPN_re[pnRe]['SWOT']
            ostOption         = TP.optionsByPN_re[pnRe]['OST']
            zgsOption         = TP.optionsByPN_re[pnRe]['ZGS']
            break

      # If no options were found for this part number, see if there are any for this Business Group.
      if srchRslt == None:
         busGrp = self.dut.BG

         busGrpREs = optionsByBG_re.keys()
         for bgRe in busGrpREs:
            srchRslt = re.search(bgRe, busGrp)
            if srchRslt != None:
               rvffOption        = TP.optionsByBG_re[bgRe]['RVFF']
               shockSensorOption = TP.optionsByBG_re[bgRe]['shock sensor']
               swotOption        = TP.optionsByBG_re[bgRe]['SWOT']
               ostOption         = TP.optionsByBG_re[bgRe]['OST']
               zgsOption         = TP.optionsByPN_re[pnRe]['ZGS']
               break

      # If an option table entry was found for this drive, set the options accordingly.
      updateFlag = 0  # updateFlag will get set to 1 below if the servo RAM gets modified so that the flash will be updated
      if srchRslt != None:
         if rvffOption == 'disable':
            self.oProc.St(TP.prm_0011_shock_RVFF) # Setup shock detection method and disable RVFF
            updateFlag = 1
         elif rvffOption == 'enable':
            pass # placeholder for operation to enable RVFF
            updateFlag = 1
         elif rvffOption == 'default':
            pass
         else:
            objMsg.printMsg('WARNING: Invalid Customer Unique option setting for RVFF! option = %s' % rvffOption)

         if shockSensorOption == 'disable':
            self.oProc.St(TP.prm_0011_disableshockmode) # Turn off shock detect feature
            updateFlag = 1
         elif shockSensorOption == 'enable':
            #self.oProc.St(prm_0011_enableshockmode) # Turn on shock detect feature
            pass # placeholder for operation to enable shock sensor
            updateFlag = 1
         elif shockSensorOption == 'default':
            pass
         else:
            objMsg.printMsg('WARNING: Invalid Customer Unique option setting for shock sensor! option = %s' % shockSensorOption)

         if swotOption == 'disable':
            pass # placeholder for operation to disable SWOT
            updateFlag = 1
         elif swotOption == 'enable':
            #self.oProc.St(prm_0011_enableSwot) # Turn on SWOT feature
            pass # placeholder for operation to enable SWOT
            updateFlag = 1
         elif swotOption == 'default':
            pass
         else:
            objMsg.printMsg('WARNING: Invalid Customer Unique option setting for SWOT! option = %s' % swotOption)

         if ostOption == 'disable':
            pass # placeholder for operation to disable OST
            updateFlag = 1
         elif ostOption == 'enable':
            self.oProc.St(TP.prm_0011_OST_150KTPI)
            updateFlag = 1
         elif ostOption == 'default':
            pass
         else:
            objMsg.printMsg('WARNING: Invalid Customer Unique option setting for OST! option = %s' % ostOption)
         if zgsOption == 'disable':
            pass # placeholder for operation to disable ZGS
         elif zgsOption == 'enable':
            from Servo import CServoOpti            
            self.oSrvOpti = CServoOpti()
            for i in range(0,2):
               self.oSrvOpti.zgsTest(TP.zgsPrm_52)
               zgsHlthVal = int(self.dut.dblData.Tables('P052_ZGS_CAL_DATA').tableDataObj()[-1]['ZGS_HLTH'])
               if zgsHlthVal == 0:
                  ScrCmds.raiseException(14582,' *** No ZGS on PCBA *** ')
               if i == 1 and zgsHlthVal == 3:   # we are calling it bad after a retry
                  ScrCmds.raiseException(14582,' *** ZGS not reporting good after retry *** ')
               if zgsHlthVal != 3:   # 0 - no sensor, 1 - sensor bad, 2 - sensor good, 3 - sensor needs retested
                  break
         elif zgsOption == 'default':
            pass
         else:
            objMsg.printMsg('WARNING: Invalid Customer Unique option setting for ZGS! option = %s' % zgsOption)

         # If any servo RAM mods were made, update the flash.
         if updateFlag == 1:
            from Servo import CServoFunc
            self.oSrvFunc = CServoFunc()
            self.oSrvFunc.setOClim(TP.saveSvoRam2Flash_178) # save servo ram to SAP


#----------------------------------------------------------------------------------------------------------
class CReadWriteGapCal(CState):
   """
      Description: Class that will perform optimization of the reader writer offset calibrations
      Base: Based on AGERE Venus calibration flows.
      Usage: Optionally add an input parameter of 'ZONES' to list specific zones to be optimized.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.dut = dut
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def prepareRetry(self, head=0):
      #from Cell import theCell
      #import base_BaudFunctions
      #base_BaudFunctions.basicPowerCycle()
      #theCell.enableESlip()
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      self.oProc.St(TP.spinupPrm_1)
      if testSwitch.RUN_T150_BEFORE_T176_RETRY:
         from Servo_Screens import CLinearityScreen
         CLinearityScreen(self.dut,{'CAL' : 'ON', 'HEAD_RANGE':(head<<8|head,) }).run()

   #-------------------------------------------------------------------------------------------------------
   def getSpcId(self):
      spc_id = 0
      if self.dut.currentState == 'RW_GAP_CAL':
         spc_id = 1000
      elif self.dut.currentState == 'RW_GAP_CAL_02':
         spc_id = 2000
      elif self.dut.currentState == 'RW_GAP_CAL_03':
         spc_id = 3000
      elif self.dut.currentState == 'PV_RW_GAP_CAL':
         spc_id = 4000
      elif self.dut.currentState == 'VBAR_HMS1':
         spc_id = 5000 + self.params.get('spc_id', 1)
      elif self.dut.currentState == 'VBAR_HMS2':
         spc_id = 6000 + self.params.get('spc_id', 2)
      elif self.dut.currentState == 'VBAR_CLR':
         spc_id = 7000
      elif self.dut.currentState == 'VBAR_TPI':
         spc_id = 8000
      return spc_id

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from RdWr import CRdWrOpti
      self.oProc = CProcess()
      oRdWr = CRdWrOpti()
      retry = 3

      if testSwitch.MEASCQM_DATA == 1:
         oRdWr.measCQM() #Check post opti cqm for debug

      rwgapParams = self.oProc.oUtility.copy(TP.Writer_Reader_Gap_Calib_176)
      skipsyszone = self.params.get('SKIP_SYS_ZONE', 0) # Default is to include system zone during tuning
      if skipsyszone:
         rwgapParams['CWORD1'] = rwgapParams['CWORD1']|0x0002
         if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
            rwgapParams['ZONE_MASK_BANK'] = 0
      else: #run on sys zone:
         if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT: # F3Trunk requires zone mask bank to be set to 0xFF in order to run system zone. 
            rwgapParams['ZONE_MASK_BANK'] = 0xFF

      rwgapParams['spc_id'] = self.getSpcId()

      for head in range(self.dut.imaxHead):
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
         self.oProc.St(TP.spinupPrm_1)

         rwgapParams.update({'HEAD_RANGE': (self.oProc.oUtility.converttoHeadRangeMask(head, head),)})
         #zone mask for VBAR_HMS
         if(self.params.get('ZONE_MASK')):
            zone_mask_list = self.oProc.oUtility.convertZoneListtoZoneMask(self.params['ZONE_MASK'].get(head, []))
            if (not (zone_mask_list[0] or zone_mask_list[1])):
               continue #skip current head as no zones being tuned
            objMsg.printMsg("zone_mask %x, zone_mask_ext %x" %(zone_mask_list[0], zone_mask_list[1]))
            rwgapParams['ZONE_MASK'] = self.oProc.oUtility.ReturnTestCylWord(zone_mask_list[0])
            rwgapParams['ZONE_MASK_EXT'] = self.oProc.oUtility.ReturnTestCylWord(zone_mask_list[1])

         for i in range(retry):
            try:
               oRdWr.Writer_Reader_Gap_Calib(rwgapParams, zapFromDut = self.params.get('zapFromDut',0))
               break
            except ScriptTestFailure, (failuredata):
               if failuredata[0][2] in [10247]:
                  objMsg.printMsg("EC:10247 - Head %d already calibrated because BPI not changed since previous T176, ignore!!\n" % head)
                  break
               elif i < (retry-1):
                  self.prepareRetry(head)
               else:
                  if testSwitch.FE_0148166_381158_DEPOP_ON_THE_FLY:
                     self.dut.dblData.Tables('P176_TIMEOUT_FAIL_DEPOP').addRecord({
                           'SPC_ID'          : 1,
                           'HD_PHYS_PSN'     : head,
                           'HD_STATUS'       : failuredata[0][2],
                     })
                     objMsg.printDblogBin(self.dut.dblData.Tables('P176_TIMEOUT_FAIL_DEPOP'))
                     self.prepareRetry(head)
                  raise

            except FOFSerialTestTimeout:
               if i < (retry-1):
                  self.prepareRetry(head)
               else:
                  if testSwitch.FE_0148166_381158_DEPOP_ON_THE_FLY:
                     self.dut.dblData.Tables('P176_TIMEOUT_FAIL_DEPOP').addRecord({
                           'SPC_ID'          : 1,
                           'HD_PHYS_PSN'     : head,
                           'HD_STATUS'       : 11049,
                     })
                     objMsg.printDblogBin(self.dut.dblData.Tables('P176_TIMEOUT_FAIL_DEPOP'))
                     self.prepareRetry(head)
                     ScrCmds.raiseException(11049, 'Tester Timeout-Test Time Limit Exceeded')
                  else: raise


#----------------------------------------------------------------------------------------------------------
class CReadWriteGapCal_hc(CState):
   """
      Description: Class that will perform optimization of the reader writer offset calibrations
      Base: Based on AGERE Venus calibration flows.
      Usage: Optionally add an input parameter of 'ZONES' to list specific zones to be optimized.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.dut = dut
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def prepareRetry(self, head=0):
      #from Cell import theCell
      #import base_BaudFunctions
      #base_BaudFunctions.basicPowerCycle()
      #theCell.enableESlip()
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      self.oProc.St(TP.spinupPrm_1)
      if testSwitch.RUN_T150_BEFORE_T176_RETRY:
         from Servo_Screens import CLinearityScreen
         CLinearityScreen(self.dut,{'CAL' : 'ON', 'HEAD_RANGE':(head<<8|head,) }).run()

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from RdWr import CRdWrOpti
      self.oProc = CProcess()
      oRdWr = CRdWrOpti()
      retry = 3

      if testSwitch.MEASCQM_DATA == 1:
         oRdWr.measCQM() #Check post opti cqm for debug

      rwgapParams = self.oProc.oUtility.copy(TP.Writer_Reader_Gap_Calib_176)
      skipsyszone = self.params.get('SKIP_SYS_ZONE', 0) # Default is to include system zone during tuning
      if skipsyszone:
         rwgapParams['CWORD1'] = rwgapParams['CWORD1']|0x0002
      if self.dut.currentState == 'RW_GAP_CAL':
         rwgapParams['spc_id'] = 1000
      if self.dut.currentState == 'RW_GAP_CAL_02':
         rwgapParams['spc_id'] = 2000
      if self.dut.currentState == 'RW_GAP_CAL_03':
         rwgapParams['spc_id'] = 3000
      if self.dut.currentState == 'PV_RW_GAP_CAL':
         rwgapParams['spc_id'] = 4000

      if testSwitch.extern.POLY_ZAP:
            rwgapParams['PAD_SIZE'] = 3000

      for head in range(self.dut.imaxHead):
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
         self.oProc.St(TP.spinupPrm_1)

         rwgapParams.update({'HEAD_RANGE': (head<<8|head,)})
         for i in range(retry):
            try:
               oRdWr.Writer_Reader_Gap_Calib(rwgapParams, zapFromDut = self.params.get('zapFromDut',0))
               break
            except ScriptTestFailure, (failuredata):
               if failuredata[0][2] in [10247]:
                  objMsg.printMsg("EC:10247 - Head %d already calibrated because BPI not changed since previous T176, ignore!!\n" % head)
                  break
               elif i < (retry-1):
                  self.prepareRetry(head)
               else:
                  if testSwitch.FE_0148166_381158_DEPOP_ON_THE_FLY:
                     self.dut.dblData.Tables('P176_TIMEOUT_FAIL_DEPOP').addRecord({
                           'SPC_ID'          : 1,
                           'HD_PHYS_PSN'     : head,
                           'HD_STATUS'       : failuredata[0][2],
                     })
                     objMsg.printDblogBin(self.dut.dblData.Tables('P176_TIMEOUT_FAIL_DEPOP'))
                     self.prepareRetry(head)
                  raise

            except FOFSerialTestTimeout:
               if i < (retry-1):
                  self.prepareRetry(head)
               else:
                  if testSwitch.FE_0148166_381158_DEPOP_ON_THE_FLY:
                     self.dut.dblData.Tables('P176_TIMEOUT_FAIL_DEPOP').addRecord({
                           'SPC_ID'          : 1,
                           'HD_PHYS_PSN'     : head,
                           'HD_STATUS'       : 11049,
                     })
                     objMsg.printDblogBin(self.dut.dblData.Tables('P176_TIMEOUT_FAIL_DEPOP'))
                     self.prepareRetry(head)
                     ScrCmds.raiseException(11049, 'Tester Timeout-Test Time Limit Exceeded')
                  else: raise

      #self.oProc.St(TP.prm_506_RESET_RUNTIME)
      zntbl = self.dut.dblData.Tables(TP.zone_table['table_name']).tableDataObj()
      self.oProc.St({'test_num':172, 'prm_name':"Retrieve Heater's", 'timeout': 1800, 'CWORD1': (4,)})
      self.oProc.St({'test_num':172, 'prm_name':"Retrieve Clr's", 'timeout': 1800, 'CWORD1': (5,)})

      #import struct
      from FSO import dataTableHelper
      self.dth = dataTableHelper()
      for iHd in range(self.dut.imaxHead):
         for iZn in range(self.dut.numZones):

            #also set fly height
            ttrk = self.getTestTrackZonePosition(iHd, iZn, 198, zntbl) #self.getTestTrackZonePosition(iHd, iZn, TP.ZONE_POS, zntbl)

            buf,errorCode = oRdWr.Fn(1345, (ttrk & 0xFFFF), ((ttrk >> 16) & 0xFFFF), iHd, 0, 2)   # set fly height

            #result = struct.unpack("L",buf)
            if errorCode != 0:
               ScrCmds.raiseException(11044, 'setFlyHeight Failed !!!')

      self.oProc.St({'test_num':172, 'prm_name':"Retrieve Heater's", 'timeout': 1800, 'CWORD1': (4,)})
      self.oProc.St({'test_num':172, 'prm_name':"Retrieve Clr's", 'timeout': 1800, 'CWORD1': (5,)})

   #-------------------------------------------------------------------------------------------------------
   def getTestTrackZonePosition(self, iHead, iZone, iZonePos, iZoneTable):
      Index = self.dth.getFirstRowIndexFromTable_byZone(iZoneTable, iHead, iZone)
      startTrk = int(iZoneTable[Index]['ZN_START_CYL'])
      numTrk = int(iZoneTable[Index]['TRK_NUM'])
      while Index+1< len(iZoneTable) and int(iZoneTable[Index]['ZN']) == int(iZoneTable[Index+1]['ZN']):
         numTrk += int(iZoneTable[Index+1]['TRK_NUM'])
         Index += 1   
      znPct    = (iZonePos)/(199.0)
      return int( (numTrk * znPct) + startTrk )


#----------------------------------------------------------------------------------------------------------
class CWriteETF(CState):
   """Description: Class that will perform a 1 stop write and read ETF"""
   def __init__(self, dut, params=[]):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from AFH import CdPES
      odPES = CdPES(TP.masterHeatPrm_11, TP.defaultOCLIM)
      odPES.setMasterHeat(TP.masterHeatPrm_11, setMHeatOn = 1) #enable master heat

      ######################################
      #  Optimize system Area
      ######################################
      odPES.mFSO.getZoneTable() # get number of heads and zones on drive

      useSYSZnParm = testSwitch.FE_0155925_007955_P_T251_SEPERATE_SYS_AREA_PARAMS
      
      from Opti_Read import CRdOpti
      #optiZap = CRdOpti(self.dut, {'ZONES':[self.dut.systemZoneNum,],'zapFromDut':self.params.get('zapFromDut',0), 'DISABLE_ZAP': False}, useSYSZnParm)
      #optiZap.optiZAP([self.dut.systemZoneNum,])
      CRdOpti(self.dut,  {'ZONES':[self.dut.systemZoneNum,]}, useSYSZnParm).run()

      if testSwitch.FE_0134030_347506_SAVE_AND_RESTORE:
         self.clearSystemArea()
      else:
         ######################################
         #  Clear system Area
         ######################################
         clearSystemArea = -1
         iteration = 0
         while (clearSystemArea == -1):
            iteration = iteration + 1
            objMsg.printMsg('Clear system area (ETF) iteration: %s' % str(iteration))

            try:
               odPES.St(TP.prepETFPrm_149)
               clearSystemArea = 1
               self.dut.systemAreaPrepared = 1
               break
            except:
               objMsg.printMsg('Warning not able to clear system area T149 failed!', objMsg.CMessLvl.IMPORTANT)
               clearSystemArea = -1
               self.dut.systemAreaPrepared = 0
               objPwrCtrl.powerCycle(useESlip=1)
               # If we failed all test 149 attempts lets raise the error code.
               if iteration == self.params.get('ITERATIONS', 10):
                  #if testSwitch.TurnOffZapAfterInitSys == 1:
                  #   odPES.St(TP.zapPrm_175_zapOff)
                  raise
         #END of INIT SYS, turn off zap
         if testSwitch.TurnOffZapAfterInitSys == 1:
            odPES.St(TP.zapPrm_175_zapOff)
      if testSwitch.FE_0269922_348085_P_SIGMUND_IN_FACTORY:
      #Write the BPI/SIF file from the /SIF/PC dir into the system area.
         try:
            odPES.St({'test_num': 210, 'prm_name': 'Save SIF/BPI to System Area','timeout': 7200, 'CWORD3':0x02, })
            objPwrCtrl.powerCycle(5000,12000,10,10)
         except ScriptTestFailure, ( failureData ):
            objMsg.printMsg('Failed SIF Saving to System Area')
            #Failcode = failureData[0][2]
            #ScrCmds.raiseException(Failcode)
            raise
   if testSwitch.FE_0134030_347506_SAVE_AND_RESTORE:
      def clearSystemArea(self):
         oProc = CProcess()
         ######################################
         #  Clear system Area
         ######################################
         clearSystemArea = -1
         iteration = 0
         while (clearSystemArea == -1):
            iteration = iteration + 1
            objMsg.printMsg('Clear system area (ETF) iteration: %s' % str(iteration))

            try:
               oProc.St(TP.prepETFPrm_149)
               clearSystemArea = 1
               self.dut.systemAreaPrepared = 1
               break
            except:
               objMsg.printMsg('Warning not able to clear system area T149 failed!', objMsg.CMessLvl.IMPORTANT)
               clearSystemArea = -1
               self.dut.systemAreaPrepared = 0
               objPwrCtrl.powerCycle(useESlip=1)
               # If we failed all test 149 attempts lets raise the error code.
               if iteration == self.params.get('ITERATIONS', 10):
                  if testSwitch.TurnOffZapAfterInitSys == 1:
                     oProc.St(TP.zapPrm_175_zapOff)
                  raise
         #END of INIT SYS, turn off zap
         if testSwitch.TurnOffZapAfterInitSys == 1:
            oProc.St(TP.zapPrm_175_zapOff)


#----------------------------------------------------------------------------------------------------------
class CSaveSIMFilesToDUT(CState):
   """Description: Class that will perform a 1 stop write and read ETF"""
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params=[]):
      self.params = params

      if dut.nextOper == 'PRE2':
         depList = ['HEAD_CAL', 'INIT_SYS', 'AFH1' ]
         if 'AFH' in self.params['saveFiles'] and (not testSwitch.SKIP_HIRP1A) and (not testSwitch.FE_0295624_357595_P_FE_357595_HIRP_MOVE_TO_AFTER_AFH2):
            depList.append( 'HIRP1A' )
            # if we are saving the AFH data then ensure that this is AFTER the HIRP1A state.
            #    This continues to break the burnish checking when the WRT_SIM_FILES state
            #    that saves the AFH data is AFTER the HIRP1A state.

         # Allow for completely disabling HIRP only for DH target.
         try:
            testSwitch.GRENADA
         except:
            testSwitch.GRENADA = 0

         try:
            testSwitch.MANTA_RAY_SAS
         except:
            testSwitch.MANTA_RAY_SAS = 0

         #if testSwitch.IS_DUAL_HEATER:
         #   depList.pop( depList.index( 'HIRP1A' ) )


      else:
         depList = []

      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from FSO import CFSO
      self.oFSO = CFSO()

      if self.params.get('saveFiles'):
         filesToSave = eval(str(self.params.get('saveFiles')))
      else:
         filesToSave = ['HEADER', 'AFH', 'RW_GAP', 'MR_RES', 'RPS', 'SKIPZN']

      if 'HEADER' in filesToSave:
         #  Initialize and Allocate the SPT results file headers
         from SIM_FSO import initSimArea
         initSimArea()

      if 'AFH' in filesToSave:
         ######################################
         #  Save AFH results to the system area (ETF) of the drive under test
         ######################################
         from AFH_SIM import CAFH_Frames
         frm = CAFH_Frames()
         iteration = 0
         self.dut.saveToDisc = -1
         if not self.params.get('noAFH_SIM',0):
            while (self.dut.saveToDisc != 1) and (iteration < 10):
               iteration = iteration + 1
               frm.readFromCM_SIMWriteToDRIVE_SIM(exec231 = 1)

            # Here we need to add code to check that the results are valid.

            frm.clearFrames()
            frm.readFramesFromDRIVE_SIM()
            frm.display_frames()

            if frm.dPesSim.DPES_FRAMES == [] and not testSwitch.virtualRun:
               objMsg.printMsg('After Writing to the Sim File and then reading the same file back again no data was found!!!')
               ScrCmds.raiseException(11044,"DRIVE_SIM data not Found.")
         ######################################

      if 'RW_GAP' in filesToSave:
         from Servo import CServoOpti
         oSvo = CServoOpti()
         oSvo.saveRWGapData()

      if 'MR_RES' in filesToSave:
         from RdWr import CMrResFile
         # Save MR resistance values to SIM
         if testSwitch.FE_0173493_347506_USE_TEST321 and testSwitch.extern.SFT_TEST_0321:
            oMrRes = CMrResFile(TP.get_MR_Resistance_321, TP.mrDeltaLim)
         else:
            oMrRes = CMrResFile(TP.get_MR_Values_186, TP.mrDeltaLim)
         oMrRes.fileToDisc()

      if 'SKIPZN' in filesToSave and not testSwitch.virtualRun:
         if testSwitch.SKIPZONE:
            from RdWr import CSkipZnFile
            oSkZnFile = CSkipZnFile()
            oSkZnFile.Save_SKIPZN(self.dut.skipzn)
            skipzn = oSkZnFile.Retrieve_SKIPZN(dumpData = False)
            objMsg.printMsg("Retrieved Skip Zone From Sim: %s" % skipzn)

      if testSwitch.extern.FE_0125575_357552_SAVE_GMR_RES_RANGE_TO_SIM:
         if 'MR_RANGE' in filesToSave:
            from RdWr import CMrResRange
            if testSwitch.FE_0173493_347506_USE_TEST321 and testSwitch.extern.SFT_TEST_0321:
               oMrResRange = CMrResRange(TP.get_MR_Resistance_321, TP.resRangeLim)
            else:
               oMrResRange = CMrResRange(TP.prm_186_MRRes_noSync, TP.T186_ResRangeLim)

            oMrResRange.fileToDisc()

      if 'RPS' in filesToSave:
         # if sw set and bin file is in servo code package, then download SPT from CM host to ETF log
         from Servo import CServoOpti
         oSrvOpti = CServoOpti()
         oSrvOpti.T37RPSDefaultDownload()

      if ('TPM_FILE' in filesToSave) and not (testSwitch.virtualRun or testSwitch.FE_0221722_379676_BYPASS_TPM_DOWNLOAD):
         from SIM_FSO import objSimArea
         from PackageResolution import PackageDispatcher
         tpmfile = PackageDispatcher(self.dut, 'TPM').getFileName()
         TPMfile = os.path.join(ScrCmds.getSystemDnldPath(), tpmfile)
         self.oFSO.saveResultsFileToDrive(1, TPMfile, 0, objSimArea['TPM_FILE_ON_DISC'],exec231 = 1)

      if 'BER' in filesToSave:
         # Save BER results to SIM
         from BER_SIM import CBERFile
         oBER = CBERFile()
         oBER.saveFileToDrive()

      if 'SIF' in filesToSave and not testSwitch.virtualRun:
         from RdWr import CSifBpiBinFile
         oCSifBpiBinFile = CSifBpiBinFile()
         oCSifBpiBinFile.Save_SifBpiBin_To_Disc()

      if self.params.get('DISABLE_ZAP',False):
         #Disable ZAP in flash so no remenant zap is read in subsequent operations
         self.oFSO.St(TP.zapPrm_175_zapOff)


#----------------------------------------------------------------------------------------------------------
class CReadETF(CState):
   """Description: Class that will perform a 1 step read ETF"""
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params=[]):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from RdWr import CMrResFile
      from AFH_SIM import CAFH_Frames
      frm = CAFH_Frames()
      frm.mFSO.St(TP.readETFPrm_130)
      frm.clearFrames()
      frm.readFramesFromDRIVE_SIM()
      frm.display_frames()
      frm.writeFramesToCM_SIM()

      # Recall MR resistance values from SIM
      if testSwitch.FE_0173493_347506_USE_TEST321 and testSwitch.extern.SFT_TEST_0321:
         oMrRes = CMrResFile(TP.get_MR_Resistance_321, TP.mrDeltaLim)
      else:
         oMrRes = CMrResFile(TP.get_MR_Values_186, TP.mrDeltaLim)
      oMrRes.simToPcFile()


#----------------------------------------------------------------------------------------------------------
class CSteAti(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
  
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if (testSwitch.extern.DOS_PARMS_IN_RAP and testSwitch.extern.FE_0124044_354753_F3TRUNK_INTEGRATIONS_FOR_DOS_PARMS_SUPPORT) or testSwitch.virtualRun:
         oProc = CProcess()
         if testSwitch.FE_0146187_007955_P_SET_OCLIM_BEFORE_AFTER_T213:
            if self.params.get("OCLIM"):
               from Servo import CServoFunc 
               self.oSrvFunc = CServoFunc()
               tmpOClimVal = self.params["OCLIM"]
               self.oSrvFunc.setOClim({},tmpOClimVal)   # in memory only

         parms=self.params.copy()
         if parms.has_key('OCLIM'):
            parms.pop('OCLIM')
         testParmSTE=TP.STE_Prm_213.copy()
         testParmSTE.update(parms)
         oProc.St(testParmSTE)
         if testSwitch.FE_0146187_007955_P_SET_OCLIM_BEFORE_AFTER_T213:
            if self.params.get("OCLIM"):
               objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)  # restore org oclim


#----------------------------------------------------------------------------------------------------------
class CTempReportHumidity(CState):
   """
      Class that will log the mixed ratio and relative humidity data captured from the drive's
      internal Humidity Sensor.  This class can optionally tell the SF3 to save the captured
      humidity values to the RAP.
      Input parameters:
   """
   
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if not hasattr(self.dut.objData,'hcsSpcId'):
         self.dut.objData['hcsSpcId'] = 100
      from Temperature import CTemperature
      oTemp = CTemperature()
      oTemp.measureHumidity(spc_id=self.dut.objData['hcsSpcId'])
      self.dut.objData['hcsSpcId'] += 1


#----------------------------------------------------------------------------------------------------------
class CFormat2File1(CProcess):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self):
      CProcess.__init__(self)
      pcFileName = 'hsc_tcc'
      self.genHSCFmtName = 'hsc_tcc'

      from FSO import CFSO

      self.oFSO = CFSO()
      self.T231Index = 23
      self.HSCFormat_Path = os.path.join(ScrCmds.getSystemPCPath(), pcFileName, self.oFSO.getFofFileName(0))
      self.genericHSCFormatPath = os.path.join(ScrCmds.getSystemResultsPath(), self.oFSO.getFofFileName(0), self.genHSCFmtName)

   #-------------------------------------------------------------------------------------------------------
   def Save_HSC_Format(self, array = []):
      self.arrayToFile(array)
      self.fileToDisc()

   #-------------------------------------------------------------------------------------------------------
   def Retrieve_HSC_Format(self, Flag = False):
      from array import array
      # Get the original values
      ogPcPath = self.SimToPcFile()
      file = open(ogPcPath,'r')
      Array_HSCFormt = array('f', file.read())
      List_HSCFormat = Array_HSCFormt.tolist()
      return List_HSCFormat

   #-------------------------------------------------------------------------------------------------------
   def SimToPcFile(self):
      from SIM_FSO import objSimArea
      record = objSimArea['HSC_TCC']  #CCCYYY
      if not testSwitch.virtualRun:
         path = self.oFSO.retrieveHDResultsFile(record)
      else:
         path = os.path.join('.', self.genericHSCFormatPath)
      return path

   #-------------------------------------------------------------------------------------------------------
   def arrayToFile(self, array1):
      from array import array
      HSCformatFile = GenericResultsFile(self.genHSCFmtName)
      HSCformatFile.open('w')
      arStr = array1.tostring()
      HSCformatFile.write(arStr)
      HSCformatFile.close()

   #-------------------------------------------------------------------------------------------------------
   def fileToDisc(self):
      from SIM_FSO import objSimArea
      
      record = objSimArea['HSC_TCC'] #CCCYYY Debug
      if os.path.exists(self.genericHSCFormatPath):
         filePath = self.genericHSCFormatPath
      elif os.path.exists(self.HSCFormat_Path):
         filePath = self.HSCFormat_Path
      else:
         ScrCmds.raiseException(11044, "HSC FORMAT File does not exist")
      #Write data to drive SIM
      objMsg.printMsg("Saving HSC Format File to drive SIM.  File Path: %s" % filePath, objMsg.CMessLvl.DEBUG)
      self.oFSO.saveResultsFileToDrive(1, filePath, 0, record, 1)
      #Verify data on drive SIM
      if not testSwitch.virtualRun:
         path = self.oFSO.retrieveHDResultsFile(record)
         file = open(path,'rb')
         try:
            file.seek(0,2)  # Seek to the end
            fileLength = file.tell()
         finally:
            file.close()
         objMsg.printMsg("Re-Read of drive SIM File %s had size %d" % (record.name,fileLength), objMsg.CMessLvl.DEBUG)
         if fileLength == 0:
            ScrCmds.raiseException(11044, "HSC FORMAT SIM readback of 0 size.")


#----------------------------------------------------------------------------------------------------------
class COffCertDoneBitInSap(CState):
   """
      Verify critical values are populated during MCT testing.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      #object initialization
      from Servo import CServoFunc
      oSrvFunc = CServoFunc()
      ################### Set CERT Done bit. Requested by servo group.
      try:
         oSrvFunc.setCertDoneSap(enable = False)
      except: pass


#----------------------------------------------------------------------------------------------------------
class CReportZonedServoInfo(CState):
   """
      Report zoned servo info
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      self.dut = dut
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if not (testSwitch.SMR or testSwitch.FE_0184102_326816_ZONED_SERVO_SUPPORT):         
         return
      oProcess = CProcess()
      if testSwitch.FE_0184102_326816_ZONED_SERVO_SUPPORT:
         # t172 zone table in zoned servo format
         if not testSwitch.extern.FE_0269440_496741_LOG_RED_P172_ZONE_TBL_SPLIT:
            oProcess.St(TP.PRM_DISPLAY_ZONED_SERVO_ZONE_TABLE_172)
         oProcess.St(TP.PRM_DISPLAY_ZONED_SERVO_CONFIG_TABLE_172)
      ### print out track per band and smr tp, tg, rd offset ###
      oProcess.St(TP.PRM_DISPLAY_HEAD_TPI_CONFIG_172)
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=3, onTime=3, useESlip=1)


#----------------------------------------------------------------------------------------------------------
class CReportZonedServoRadiusKFCI(CState):
   """
      Report zoned servo info
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      self.dut = dut
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if not (testSwitch.SMR or testSwitch.FE_0184102_326816_ZONED_SERVO_SUPPORT):         
         return
      from FSO import CFSO
      self.oFSO = CFSO()
      self.oFSO.getKFCI()


#----------------------------------------------------------------------------------------------------------
class CRapMCUpdate(CState):
   """
   Update RAP Super Parity Media Cache size 
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.dut = dut
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      self.oProc = CProcess()
      # RAP file offset for "Number of Media Cache Serpents" is at byte 0x08.      
      RapFileOffset = 0x0004
      if self.dut.CAPACITY_PN == '320G':
         objMsg.printMsg ("%s: Change Media Cache size from 2 to 3 minizones." %str(self.dut.CAPACITY_PN))
         self.oProc.St({'test_num':178, 'prm_name':'chgMediaCacheSizePrm_178', 'CWORD1':0x0220, 'RAP_WORD':(RapFileOffset, 3, 0x00FF)})
      elif self.dut.CAPACITY_PN == '250G':
         objMsg.printMsg ("%s: Change Media Cache size from 2 to 4 minizones." %str(self.dut.CAPACITY_PN))
         self.oProc.St({'test_num':178, 'prm_name':'chgMediaCacheSizePrm_178', 'CWORD1':0x0220, 'RAP_WORD':(RapFileOffset, 4, 0x00FF)})      
      else:
         objMsg.printMsg ("Native %s: No change in Media Cache size." %str(self.dut.CAPACITY_PN))


#----------------------------------------------------------------------------------------------------------
class CPBI_Data(CState):

   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from PBIC import CPBIC 
      try:
         objPBIC = CPBIC(self.params)
         objPBIC.run()
      except:
         testSwitch.PBIC_SUPPORT = 0  # turn off PBIC support if excepiton happens, will be better to update to drive attribute later
         objMsg.printMsg("PBIC turn off due to exception !!!!")  
         pass       
class CPostBSPScan(CState):  
   """
   Run Bad Sample Scan
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      self.dut = dut   
      depList = []      
      CState.__init__(self, dut, depList)
      self.failHead = []
      
      self.prmPostBSPScanT126 = {
         'test_num': 126, 
         'prm_name': 'DO BSP SCAN',  
         'SEEK_TYPE': 37,
         'END_CYL': (0xFFFF, 0xFFFF), 
         'spc_id': 1, 
         'START_CYL': (0, 0), 
         'CWORD1': 0, 
         'CWORD2': 0x3000 | 0x0004, # disable TMD skip track
         'timeout': 10800, 
         'REVS': 0x10A,
         'SET_OCLIM': 1228, 
         'THRESHOLD':3,  
         'HEAD_RANGE': 0x0000, 
         'MASK_VALUE': 0xfffe
         }
      self.prmDispSListByZoneT126 = {
         'test_num': 126, 
         'timeout': 600, 
         'CWORD1': 2, 
         'CWORD2': 16384, 
         'prm_name' : 'PRINT SLIST BY ZONE'
         }
      self.prmDispSrvoErrorLogT159 = {
         'test_num':159,
         'prm_name':"Read Servo Error Log",
         "CWORD1":0x8001
         }
      
   #-------------------------------------------------------------------------------------------------------
   def ServoFlawScreen(self):
      self.failHead = []
      entries = self.dut.dblData.Tables('P126_SRVO_FLAW_HD').tableDataObj()
      
      for entry in entries:
         if int(entry['SPC_ID']) == 202 and int(entry['RAW_SRVO_FLAW_CNT']) > 600:
            msg = 'P126_SRVO_FLAW_HD RAW_SRVO_FLAW_CNT > 600 @ Head %s'%entry['HD_LGC_PSN']
            objMsg.printMsg(msg)
            self.failHead.append(int(entry['HD_LGC_PSN']))
      if len(self.failHead) > 0:
         ScrCmds.raiseException(10504, msg)     
      
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from FSO import CFSO 
      import Utility
      from MediaScan import CUserFlaw
      from Exceptions import CRaiseException
      
      self.oFSO  = CFSO()
      self.oUtil = Utility.CUtility()
      self.oUserFlaw = CUserFlaw()
      
      self.oFSO.getZoneTable()
      
      # For OEM, downgrade to retail if RAW_SRVO_FLAW_CNT > 600. And trigger rerun and bypass the RAW_SRVO_FLAW_CNT checking
      # For SBS, trigger 2nd run if RAW_SRVO_FLAW_CNT > 600. And bypass the RAW_SRVO_FLAW_CNT checking
      for i in range(2):
         try:
            self.quickBSPScan()
            break
         except CRaiseException, exceptionData:
            if exceptionData[0][2] == 10504 and testSwitch.ENABLE_ON_THE_FLY_DOWNGRADE and self.downGradeOnFly(1, 10504):
               for table in self.dut.stateDBLogInfo.get(self.dut.currentState,[])[:]:
                   try:
                      self.dut.dblData.Tables(table).deleteIndexRecords(confirmDelete=1)
                      self.dut.dblData.delTable(table)
                   except:
                      pass
            else:
               raise exceptionData
      
      objPwrCtrl.powerCycle(useESlip=1) #perform power cycle before this test
   
   def quickBSPScan(self):
      badHeadList = []
      
      try:
         StartIndex = len(self.dut.dblData.Tables('P126_SRVO_FLAW_HD').tableDataObj())
      except:
         StartIndex = 0
      
      # T126 SERVO FLAW CNT
      self.oUserFlaw.repServoFlaws_T126(101)
      
      # Check if the head need run BSP Scan
      if not self.failHead:
         for entry in self.dut.dblData.Tables('P126_SRVO_FLAW_HD').tableDataObj()[StartIndex:]:
            if int(entry['SPC_ID']) == 101 and int(entry['RAW_SRVO_FLAW_CNT']) >= 100:
               objMsg.printMsg('Hd %s need run BSP Scan'%entry['HD_LGC_PSN'])
               badHeadList.append(int(entry['HD_LGC_PSN']))
      else:
         badHeadList = self.failHead
      
      badHeadList = list(set(badHeadList))
      if len(badHeadList) == 0:
         objMsg.printMsg('No need to run BSP Scan')
         return
         
      # Display Servo Flaw Cnt By Servo Zone Before BSP Scan
      self.prmDispSListByZoneT126['spc_id'] = 102
      self.oFSO.St(self.prmDispSListByZoneT126)
      
      # dump T159 Servo Error Log
      self.prmDispSrvoErrorLogT159['spc_id'] = 101  
      self.oFSO.St(self.prmDispSrvoErrorLogT159)
      
      # T126 BSP Scan loop
      testRegionSequence = [0,4,1,5,2,6,3,7]      
      
      for hd in badHeadList:
         for region in testRegionSequence:            
            startCyl =  int( region * (self.dut.maxTrack[hd] + 1) * 1.0 / len(testRegionSequence) )
            endCyl   =  int((region+1) * (self.dut.maxTrack[hd] + 1) * 1.0 / len(testRegionSequence)) - 1            
            if region == max(testRegionSequence):
               endCyl = self.dut.maxTrack[hd]
            
            #endCyl = startCyl + 10  # for debug only
            objMsg.printMsg("Run BSP Scan T126, Hd %d, Region %d, Cyl %d - %d" % (hd,region,startCyl,endCyl))            
            self.prmPostBSPScanT126['HEAD_RANGE'] = (hd <<8 ) + hd
            self.prmPostBSPScanT126['START_CYL'] = self.oUtil.ReturnTestCylWord(startCyl)
            self.prmPostBSPScanT126['END_CYL'] = self.oUtil.ReturnTestCylWord(endCyl)
            self.prmPostBSPScanT126['timeout'] = max( int((endCyl - startCyl) * 0.05 ), 60 )
            self.oFSO.St(self.prmPostBSPScanT126)
      
      # Save SLIST to PLIST
      self.oUserFlaw.writeSrvListToPList()
      
      self.oUserFlaw.repServoFlaws_T126(201)     
         
      # Display Servo Flaw Cnt By Servo Zone After BSP Scan
      self.prmDispSListByZoneT126['spc_id'] = 202
      self.oFSO.St(self.prmDispSListByZoneT126)      
      
      # dump T159 Servo Error Log      
      self.prmDispSrvoErrorLogT159['spc_id'] = 201  
      self.oFSO.St(self.prmDispSrvoErrorLogT159)  
      
      # New added to screen ODT failures(Servo Flaw(OSE)) which reported in no MQM ODT
      self.ServoFlawScreen()
      
      # power cycle
      #objPwrCtrl.powerCycle(useESlip=1) #perform power cycle before this test

#----------------------------------------------------------------------------------------------------------
class CAGB_Beatup(CState):
   '''
      Wuxi LowContact Air Bearing Eval (Not Official FIN2 screen)
      Loop 10x times of AGB_Algo
   '''

   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.LULFailCount = 0
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if self.dut.AABType not in ['501.42'] or testSwitch.IS_2D_DRV:
         return
      objMsg.printMsg("Start AGB Beatup test...")

      #self.maxLBA = int(ICmd.GetMaxLBA()['MAX48'],16)-1
      #self.startLBA = self.maxLBA - 97656250 #last 50G startLBA
      #self.sctCnt = 0x800
      #objMsg.printMsg("startLBA: %s maxLBA: %s" % (self.startLBA, self.maxLBA))
      
      from serialScreen import sptDiagCmds
      self.oSerial = sptDiagCmds()
      self.oSerial.enableDiags()

      for loop in xrange(10):
         objMsg.printMsg("***************")
         objMsg.printMsg("  AGB loop %s" % (loop + 1))
         objMsg.printMsg("***************")
         self.AGB_Algo()
      objMsg.printMsg('LUL Failed Cnt %d'%self.LULFailCount)

   def AGB_BeatUp(self):
      if not testSwitch.virtualRun:
          data = self.oSerial.sendDiagCmd(CTRL_L, printResult = True)
      else:
          data = """
             - Zone Remap enabled
[PLBA:00000000 Len:0085ACFC Offset:0E06941E]
[PLBA:0085ACFC Len:0E06941E Offset:FF7A5304]
[PLBA:0E8C411A Len:00633585 Offset:00000000]
[PLBA:0EEF769F Len:00000001 Offset:00000000]
- AGB enabled
- SubRelease:0
          """
      
      startIndex = data.find('Zone Remap enabled')
      if startIndex > -1:
         data = data[startIndex:]
         mat = re.search('\[PLBA:(?P<PLBA>[a-fA-F\d]+)\s+Len:(?P<Len>[a-fA-F\d]+)\s+Offset:(?P<Offset>[a-fA-F\d]+).*', data)
         if mat:
            startLBA = int(mat.groupdict()['Offset'], 16)
            length = int(mat.groupdict()['Len'], 16)
            objMsg.printMsg("startLBA: %s Length: %s" % (startLBA, length))
            
            self.oSerial.gotoLevel('2')
            self.oSerial.sendDiagCmd('AD', printResult = True)
            self.oSerial.sendDiagCmd('P0,0', printResult = True)
            self.oSerial.gotoLevel('A')
            self.oSerial.sendDiagCmd('F%X'%(startLBA), printResult = True)
            self.oSerial.sendDiagCmd('F%X'%(startLBA + length - 1), printResult = True)            
            try:
               objMsg.printMsg('Start writing')
               self.oSerial.sendDiagCmd('W%X,%X'%(startLBA, length), timeout=8*60, printResult = True)
            except:
               ScrCmds.raiseException(13412, 'Failed to write Zero Pattern to AGB')
      else:
         objMsg.printMsg('Zone Remap Disabled')
      
   #-------------------------------------------------------------------------------------------------------
   def AGB_Algo(self):
      '''
         1) 20x (load cmd -> delay 1sec -> unload cmd -> delay 1sec)
         2) seq write -> seq read (50G)
         3) 4>s cmd
      '''
      import time
      objMsg.printMsg("***** (1) L/UL 20x times *****")
      self.oSerial.gotoLevel('5') 
      for loop in xrange(20):
         try:
            self.oSerial.sendDiagCmd('C100', printResult = True)
            time.sleep(1)

            self.oSerial.sendDiagCmd('CE00', printResult = True)
            time.sleep(1)
         except:
            self.LULFailCount += 1
            
      self.AGB_BeatUp()
      if not testSwitch.NoIO:
         objPwrCtrl.powerCycle()
      return

      objMsg.printMsg("***** (2) Seq Write and Read of last 50G *****")
      ICmd.HardReset()
      result = ICmd.ClearBinBuff()
      if result['LLRET'] != OK:
         ScrCmds.raiseException(11044, "Failed to fill up write buffer with zero pattern")

      try:
         result = ICmd.SequentialWriteDMAExt(self.startLBA, self.maxLBA, self.sctCnt, self.sctCnt)
      except ScrCmds.CRaiseException, exceptionData:
         mat = re.search("PLP CHS (\w+\.\w+\.\w+)", exceptionData[0][0])
         if mat:
            if int(mat.group(1).split('.')[0], 16) < 20000:
               objMsg.printMsg('The failure happened in OD')
               ScrCmds.raiseException(13413, "Failed to write Zero Pattern to last 50G")
            else:
               objMsg.printMsg('The failure happened in ID')
               ScrCmds.raiseException(13412, "Failed to write Zero Pattern to last 50G")
         raise exceptionData
      objMsg.printMsg("Last 50G Zero pattern write result: %s" % (result,))
      if result['LLRET'] != OK:
         ScrCmds.raiseException(12657, "Failed to write Zero Pattern to last 50G")      

      #result = ICmd.ZeroCheck(self.startLBA, self.maxLBA, self.sctCnt)
      #objMsg.printMsg("Last 50G Zero pattern check result: %s" % (result,))
      #if result['LLRET'] != OK:
      #   ScrCmds.raiseException(14723, "Failed Zero Pattern verification at last 50G")  

      objMsg.printMsg("***** (3) Display Servo sector error count *****")
      self.oSerial.gotoLevel('4') 
      self.oSerial.sendDiagCmd('s', printResult = True)
