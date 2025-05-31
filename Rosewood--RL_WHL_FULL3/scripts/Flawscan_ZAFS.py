#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: base Serial Port calibration states
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/12/28 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Flawscan_ZAFS.py $
# $Revision: #2 $
# $DateTime: 2016/12/28 20:22:59 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Flawscan_ZAFS.py#2 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
from State import CState
import Utility
import MessageHandler as objMsg
from PowerControl import objPwrCtrl
from StateTable import StateTable
from Process import CProcess
from MediaScan import SeekType
from MediaScan import CServoFlaw
from MediaScan import CUserFlaw
import ScrCmds
from Servo import CServoFunc
import dbLogUtilities

###########################################################################################################
class CMiniZapAfs(CState):
   """
      Single Pass Flaw Scan
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      self.dut = dut
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      #=== Add a powercycle to clear any memory issue from previous run.
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=5, onTime=5, useESlip=1)
      #=== Import libraries
      self.importLibraries()
      #=== Init flaw lists
      self.initFlawLists()

      
      startCyl, endCyl = self.getStartEndCyl(TP.UMP_ZONE_BY_HEAD[self.dut.imaxHead][self.dut.numZones][0], TP.UMP_ZONE_BY_HEAD[self.dut.imaxHead][self.dut.numZones][-2])
      #=== Test range
      if self.dut.nextState == "STS_DEFECT_SCREEN2": 
          startCyl = 70000
          endCyl   = 110000
      startCyl = self.oUserFlaw.oUtility.ReturnTestCylWord(startCyl)
      endCyl = self.oUserFlaw.oUtility.ReturnTestCylWord(endCyl)

      try:
         #=== ZAP
         self.runMiniZap(startCyl, endCyl)
         self.repFlawLists(spc_id = 1091)
         #=== Setup DETCR preamp
         self.SetupDetcrPreamp()
         #=== Analog Flaw Scan
         self.runMiniAnalogFlawScan(startCyl, endCyl)
         #=== Power cycle badly needed here as some reminent register setup was effecting T134 and causing 0 TA's.
         objPwrCtrl.powerCycle(useESlip=1) 
         #=== Report tables
         self.repFlawLists(spc_id = 1092)
      except:
         objPwrCtrl.powerCycle(useESlip=1)
         try:
            self.repFlawLists(spc_id = 1093)
         except:
            pass
         pass

   #-------------------------------------------------------------------------------------------------------
   def importLibraries(self):
      self.oProcess = CProcess()
      self.oUserFlaw = CUserFlaw()
      self.oServoFlaw = CServoFlaw()
      self.oSrvFunc = CServoFunc()

   #-------------------------------------------------------------------------------------------------------
   def initFlawLists(self):
      try:
         self.oUserFlaw.initdbi()
         self.oUserFlaw.initPList()
         self.oUserFlaw.initSFT()
         self.oUserFlaw.initTAList()
      except:
         pass

   #-------------------------------------------------------------------------------------------------------
   def getTestRange(self, startCyl, endCyl):
      startCyl = 0
      endCyl = 0

   #-------------------------------------------------------------------------------------------------------
   def repFlawLists(self, spc_id = 1):
      try:
         self.oUserFlaw.repServoFlaws_T126(spc_id)
         self.oUserFlaw.repdbi(spc_id)
         #self.oUserFlaw.repPList()
         #self.oUserFlaw.repSlipList()
      except FOFSerialTestTimeout:
         pass

   #-------------------------------------------------------------------------------------------------------
   def SetupDetcrPreamp(self): 
      from base_Preamp import CDETCRPreampSetup
      oDETCRPreampSetup = CDETCRPreampSetup(self.dut, self.params)
      try: # fail safe
         if testSwitch.extern.FE_0251134_387179_RAP_ALLOCATE_FOR_LIVE_SENSOR_ON_HAP:
            self.oProcess.St(TP.LiveSensor_prm_094_2)
         oDETCRPreampSetup.run()
      except:
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=5, onTime=5, useESlip=1)
         pass
   #-------------------------------------------------------------------------------------------------------
   def getStartEndCyl(self, startZn, endZn):

      table = dbLogUtilities.DBLogReader(self.dut, 'P172_ZONED_SERVO_RED')
      table.ignoreExistingData()
      self.oProcess.St({'test_num':172, 'prm_name':'getZnTblInfo', 'CWORD1':TP.zone_table['cword1'], 'spc_id':0, 'stSuppressResults': 0,'timeout': 300, })
      start_cyl = 0
      end_cyl = 0
      for record in table.iterRows():
         hd = int(record['HD_LGC_PSN'])
         zn = int(record['DATA_ZONE'])
         if zn == startZn:
            if hd == 0 or start_cyl > int(record['ZONE_START_CYL']):
               start_cyl = int(record['ZONE_START_CYL'])
         elif zn == endZn:
            if hd == 0 or end_cyl < int(record['ZONE_START_CYL']) + int(record['TRK_NUM']):
               end_cyl = int(record['ZONE_START_CYL']) + int(record['TRK_NUM'])

      return start_cyl, end_cyl

   #-------------------------------------------------------------------------------------------------------
   def runMiniZap(self, startCyl, endCyl):
      inPrm = dict(TP.zfs_275)
      inPrm['timeout'] = 172800
      inPrm['ZAP_SPAN'] = 6
      inPrm['CWORD1'] = 0x00D3
      inPrm['START_CYL'] = startCyl
      inPrm['END_CYL'] = endCyl
      self.oProcess.St(inPrm)

   #-------------------------------------------------------------------------------------------------------
   def runMiniAnalogFlawScan(self, startCyl, endCyl):
      #=== Write
      inPrm = dict(TP.prm_AFS_2T_Write_109)
      inPrm['START_CYL'] = startCyl
      inPrm['END_CYL'] = endCyl
      self.oProcess.St(inPrm)
      #=== Read
      inPrm = dict(TP.prm_AFS_CM_Read_109)
      inPrm['START_CYL'] = startCyl
      inPrm['END_CYL'] = endCyl
      inPrm['RW_MODE'] = 0x4000                 # Use fix threshold
      inPrm['SET_XREG04'] = (0x00AD, 48, 0xCE8) # Drop-out1 threshold  
      inPrm['SET_XREG05'] = (0x00AE, 48, 0xCE8) # Drop-out2 threshold
      self.oProcess.St(inPrm)
