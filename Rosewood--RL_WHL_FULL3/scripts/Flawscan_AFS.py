#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Analog Flawscan Module
#  - Contains AFS specific flawscan support
#  - Limit use to AFS base classes
#
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/12/28 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Flawscan_AFS.py $
# $Revision: #6 $
# $DateTime: 2016/12/28 23:07:30 $
# $Author: yihua.jiang $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Flawscan_AFS.py#6 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
from State import CState
import MessageHandler as objMsg
from PowerControl import objPwrCtrl
import ScrCmds
from StateTable import StateTable
from Servo import CServoFunc
from FSO import dataTableHelper

from MediaScan import CServoFlaw
from MediaScan import CUserFlaw
from Process import CProcess
from MediaScan import SeekType


#----------------------------------------------------------------------------------------------------------
class CDataFlawScan(CState):
   """
      Analog (data read/write) flaw scan, builds Primary Defect List, Thermal Asperity (TA) List
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      self.dut = dut
      depList = []
      self.dth = dataTableHelper()
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if testSwitch.FE_0241396_505235_FLAWSCAN_POWER_LOSS_RECOVERY:
         from Utility import executionState
         self.checkpoint = executionState()
         lastPoint, count = self.checkpoint.getLast(self.dut)
      else:
         lastPoint = None
         
      self.oUserFlaw = CUserFlaw()
      self.oServoFlaw = CServoFlaw()
      self.oSrvFunc = CServoFunc()
      
      if testSwitch.extern.FE_0251134_387179_RAP_ALLOCATE_FOR_LIVE_SENSOR_ON_HAP:
         self.oUserFlaw.St(TP.LiveSensor_prm_094_2)

      #add a powercycle to clear any memory issue from previous run.
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

      self.oSrvFunc.ChangeServoChannelSetting(0x0001) # stress servo channel setting

      if 'S' in StateTable[self.dut.nextOper][self.dut.nextState][OPT]:
         self.oUserFlaw.St(TP.hdstr_tempCheck)

      #self.oFSO.getZoneTable(supressOutput = 0, newTable =1)
      self.hdstrProc = self.dut.HDSTR_PROC == 'Y'

      if (testSwitch.MR_RESISTANCE_MONITOR and 0):
         try:
             self.oUserFlaw.St(TP.PresetAGC_InitPrm_186_break)
         except:
           pass

      if 1:#not testSwitch.extern.FE_0113223_009410_LOG_ERRORS_TO_SLIST_DURING_ZAP:
         #Initialize the flaw lists
         self.GetExecution(lastPoint, self.initializeFlawLists)

         # Detect Zoned Servo CrossOver Frequency tracks and mapped it as skip track 
         # bypass for cheopsam run, code not in amazone
         if (testSwitch.ROSEWOOD7) and (testSwitch.FE_0184102_326816_ZONED_SERVO_SUPPORT) and (not testSwitch.WA_0276349_228371_CHEOPSAM_SRC_BRING_UP):
            self.oUserFlaw.St(TP.DetectZSCOF_track_126)
            self.oUserFlaw.St(TP.prm_126_read_sft_oracle, spc_id=1000) #report servo flaw table

      try:
         #Flawscan the drive
         self.GetExecution(lastPoint, self.flaw_sequence)
         #DBI screening
         self.oUserFlaw.St(TP.prm_DBI_Fail_Limits_140)
         #Scan adjacent servo fields to servo defects for marginality
         if not testSwitch.FE_0136821_426568_P_DISABLE_SCRATCH_FILL_PADDING:
            self.GetExecution(lastPoint, self.runAdjacentServoFS)

         if testSwitch.WA_0173484_231166_P_DO_FPW_2T_PRIOR_TA:
            self.oUserFlaw.St(TP.disableAGCUnsafes_11)
            self.oUserFlaw.St(TP.prm_AFS_109_TA_REWRITE)

         if testSwitch.FE_0116185_357260_ENABLE_SWD_DURING_SERVO_FS:
            self.oUserFlaw.St(TP.disableAGCUnsafes_11)

         #Rescan TA list for defects
         if testSwitch.WA_0154353_350027_LCO_DISABLE_TA_DETECTION_AND_CHARACTERIZATION:
            objMsg.printMsg("TA Scanning and Characterization Disabled")
         else:
            self.GetExecution(lastPoint, self.runTAScan)

         #Build PList
         self.GetExecution(lastPoint, self.buildPList, param = 1491)

         #Beatup Test
         if testSwitch.ENABLE_FLAWSCAN_BEATUP:
            self.GetExecution(lastPoint, self.runFlawScanBeatup)

         #Media Damage Screen 
         self.GetExecution(lastPoint, self.runMediaDamageScreen)

         #ScratchFill found defects
         self.GetExecution(lastPoint, self.runScratchFill)
         self.oUserFlaw.writePListToSlipList(spcId = 2)

         #Always dump defect information for mapping programs
         self.dumpDefectSummaryInfo()

         if testSwitch.FE_0137414_357552_CHECK_SLIP_SPACE_FOR_FIELD_REFORMAT:
            #Ensure we have adequate slip space for field re-formats
            self.oUserFlaw.checkSpareSpace()

         if (testSwitch.MR_RESISTANCE_MONITOR and 0):
            try:
               self.oUserFlaw.St(TP.PresetAGC_InitPrm_186_break)
            except:
               pass

      except ScriptTestFailure, (failureData):#finally:
         #Always dump defect information for mapping programs
         self.dumpDefectSummaryInfo()

         objMsg.printMsg('failureData[0][2] = %s'% str(failureData[0][2]))
         objMsg.printMsg('failureData[0][1] = %s'% str(failureData[0][1]))
         objMsg.printMsg('failureData[0][0] = %s'% str(failureData[0][0]))
         error_code = failureData[0][2]

         if testSwitch.FE_SGP_505235_ENABLE_REZAP_ATTRIBUTE:
            if error_code == 10463 or error_code == 10504:
               flaws = self.dut.dblData.Tables('P126_SRVO_FLAW_HD').tableDataObj()
               skipTrack = 0
               servoFlaw = 0
               badHd1 = 0
               badHd2 = 0
               for rec in flaws:
                  if int(rec['SKIP_TRACKS']) > skipTrack:
                     skipTrack = int(rec['SKIP_TRACKS'])
                     badHd1 = int(rec['HD_LGC_PSN'])

                  if int(rec['REFINED_SRVO_FLAW_CNT']) > servoFlaw:
                     servoFlaw = int(rec['REFINED_SRVO_FLAW_CNT'])
                     badHd2 = int(rec['HD_LGC_PSN'])

               objMsg.printMsg('Head %d has more skip tracks' % badHd1)
               objMsg.printMsg('Head %d has more servo flaws' % badHd2)
               if (self.dut.rezapAttr & (1 << badHd1 + 8)) or (self.dut.rezapAttr & (1 << badHd2 + 8)):
                  objMsg.printMsg('Head %d or %d has already reZAP' % (badHd1, badHd2))
                  if error_code in TP.stateRerunParams['states']['D_FLAWSCAN']:
                     TP.stateRerunParams['states']['D_FLAWSCAN'].remove(error_code)
               else:
                  if not self.dut.rezapAttr & (1 << badHd1):
                     self.dut.rezapAttr |= 1 << badHd1 + 8
                  if not self.dut.rezapAttr & (1 << badHd2):
                     self.dut.rezapAttr |= 1 << badHd2 + 8

         List_VRFD_FLAWS   = [0 for hd in xrange(self.dut.imaxHead)]
         List_servo_defect_count = [0 for hd in xrange(self.dut.imaxHead)]
         if failureData[0][2] == 10591 or failureData[0][2] == 10532 or failureData[0][2] == 10482: #dbi log full 10532
            try:
               RawTable = self.dut.dblData.Tables('P107_VERIFIED_FLAWS').chopDbLog('SPC_ID', 'match',str(1))
            except:
               objMsg.printMsg("Table P107_VERIFIED_FLAWS not found")
               errCode  = failureData[0][2]
               errMsg   = failureData[0][0]
               failTest = failureData[0][1]
               ScrCmds.raiseException(errCode, 'Fail Test: ' + str(failTest)  + ' ErrMsg: ' + errMsg)

            for i in xrange(len(RawTable)):
               iHead      = int(RawTable[i]['HD_LGC_PSN'])
               VRFD_FLAWS = int(RawTable[i]['VRFD_FLAWS'])
               List_VRFD_FLAWS[iHead]= int(VRFD_FLAWS)
            objMsg.printMsg('List_VRFD_FLAWS = %s'% str(List_VRFD_FLAWS))
            depop_head = List_VRFD_FLAWS.index( max(List_VRFD_FLAWS) )

            self.dut.dblData.Tables('P_DFLAWSCAN_STATUS').addRecord({
              'SPC_ID'              : 1, #self.dut.objSeq.curRegSPCID,
              'OCCURRENCE'          : self.dut.objSeq.getOccurrence(),
              'SEQ'                 : self.dut.objSeq.curSeq,
              'TEST_SEQ_EVENT'      : self.dut.objSeq.getTestSeqEvent(0),
              'HD_PHYS_PSN'         : depop_head,  # hd
              'HD_STATUS'           : str(error_code),
            })
            objMsg.printDblogBin(self.dut.dblData.Tables('P_DFLAWSCAN_STATUS'))

         if failureData[0][2] == 10463: #sevo defect full
            try:
               RawTable = self.dut.dblData.Tables('P130_SYS_SLIST_DETAILED').chopDbLog('SPC_ID', 'match',str(1))
            except:
               objMsg.printMsg("Table P130_SYS_SLIST_DETAILED not found")
               errCode  = failureData[0][2]
               errMsg   = failureData[0][0]
               failTest = failureData[0][1]
               ScrCmds.raiseException(errCode, 'Fail Test: ' + str(failTest)  + ' ErrMsg: ' + errMsg)

            for i in xrange(len(RawTable)):
               iHead      = int(RawTable[i]['HD_LGC_PSN'])
               List_servo_defect_count[iHead] = List_servo_defect_count[iHead] + 1
            objMsg.printMsg('List_servo_defect_count = %s'% str(List_servo_defect_count))
            depop_head = List_servo_defect_count.index( max(List_servo_defect_count) )

            self.dut.dblData.Tables('P_DFLAWSCAN_STATUS').addRecord({
              'SPC_ID'              : 1, #self.dut.objSeq.curRegSPCID,
              'OCCURRENCE'          : self.dut.objSeq.getOccurrence(),
              'SEQ'                 : self.dut.objSeq.curSeq,
              'TEST_SEQ_EVENT'      : self.dut.objSeq.getTestSeqEvent(0),
              'HD_PHYS_PSN'         : depop_head,  # hd
              'HD_STATUS'           : str(error_code),
            })
            objMsg.printDblogBin(self.dut.dblData.Tables('P_DFLAWSCAN_STATUS'))
         raise

      if testSwitch.FE_0320143_305538_P_T134_TA_SCREEN_SPEC:
         from dbLogUtilities import DBLogCheck
         dblchk = DBLogCheck(self.dut)
         if ( dblchk.checkComboScreen(TP.T134_TA_Screen_Spec) == FAIL ):
            objMsg.printMsg('Failed for TA combo spec')
            self.dut.driveattr['PROC_CTRL11'] = '48667'
            #if testSwitch.ENABLE_ON_THE_FLY_DOWNGRADE and self.downGradeOnFly(1, 48667):
            #   objMsg.printMsg('Failed for TA combo spec, downgrade to %s as %s' % (self.dut.BG, self.dut.partNum))
            #else:
            #   ScrCmds.raiseException(48667, 'TA Spec exceeded limit @ Head : %s' % str(dblchk.failHead))

         if testSwitch.FE_0331797_228371_P_T134_TA_SCREEN_SPEC_TRK300:
            if ( dblchk.checkComboScreen(TP.T134_TA_Screen_Spec_TRK300) == FAIL ):
               objMsg.printMsg('Failed for TA SL7 combo spec')
               self.dut.driveattr['PROC_CTRL11'] = '48667'
               #if testSwitch.ENABLE_ON_THE_FLY_DOWNGRADE and self.downGradeOnFly(1, 48667):
               #   objMsg.printMsg('Failed for TA SL7 combo spec, downgrade to %s as %s' % (self.dut.BG, self.dut.partNum))
               #else:
               #   ScrCmds.raiseException(48667, 'TA SL7 Spec exceeded track limit 300 @ Head : %s' % str(dblchk.failHead))

      if testSwitch.FE_0157865_409401_P_TEMP_CHECKING_IN_ZAP_AND_FLAWSCAN_FOR_GHG_FLOW and self.dut.HDSTR_PROC == 'Y':
         self.oUserFlaw.St({'test_num':172, 'prm_name':'HDA TEMP', 'timeout': 200, 'CWORD1': (17,), 'REPORT_OPTION':1, 'DATA_ID': 10002})

      #Malloc clearing power cycle
      if self.dut.HDSTR_PROC == 'Y':
         objMsg.printMsg("CURRENTLY IN HDSTR RECORD MODE --- DO NOT POWER CYCLE THE DRIVE!!!")
      else:
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      if testSwitch.FE_0174524_426568_P_ENABLE_ATS_CALIBRATION_AFTER_FLAWSCAN: # Anticipatory Track Seek calibration
         self.oUserFlaw.St(TP.prm_194_ATS)

      if testSwitch.FE_0184102_326816_ZONED_SERVO_SUPPORT: # zoned servo support
         #objSAMTOL = CSAMTOL()
         #objSAMTOL.run()
         self.oUserFlaw.St(TP.prm_011_TimingMarkEnable)
         self.oUserFlaw.St(TP.saveSvoRam2Flash_178)
      if testSwitch.FE_0258915_348429_COMMON_TWO_TEMP_CERT_SCRN_A00004:
         self.ID_REGION_FLAW_SCREEN()
      if testSwitch.FE_0258915_348429_COMMON_TWO_TEMP_CERT_SCRN_A00005:
         self.TA_AFH_TEST_ZONE_SCREEN()

      self.oSrvFunc.ChangeServoChannelSetting(0x0000) # restore servo channel setting
      if testSwitch.extern.FE_0366862_322482_CERT_DETCR_LIVE_SENSOR:
         from base_TccCal import CTccCalibration
         self.oTccCal = CTccCalibration(self.dut)
         self.oTccCal.saveThresholdToHap(20, UseAFHDbLog=0)
         #self.oFSO.St(TP.enableTASensor_11)
         from FSO import CFSO
         self.oFSO = CFSO()
         self.oFSO.St(TP.enableLiveSensor_11)
         self.oFSO.St(TP.disableTASensor_11)
         self.oFSO.saveSAPtoFLASH()
   #-------------------------------------------------------------------------------------------------------
   def ID_REGION_FLAW_SCREEN(self):
      """
      Add ORT Erasure Screening for Common 2Temp CERT
      Filter Criterion:
      In Last 2 Zones VRFD_FLAWS>500 & UNVRFD_FLAWS>15000,open downgrade to SBS
      """
      objMsg.printMsg("===============FE_0258915_348429_COMMON_TWO_TEMP_CERT_SCRN_A00004===============")
      entries = None
      try:
         entries = self.dut.dblData.Tables('P140_FLAW_COUNT').tableDataObj()[-(self.dut.imaxHead * self.dut.numZones):]
      except:
         objMsg.printMsg('Attention:Table P140_FLAW_COUNT not exist!!!')
      if entries:
         fail_list = []
         for entry in entries:
            HD_LGC_PSN = int(entry['HD_LGC_PSN'])
            ZONE = int(entry['DATA_ZONE'])
            VRFD_FLAWS = int(entry['VERIFIED_FLAW_COUNT'])
            UNVRFD_FLAWS = int(entry['UNVERIFIED_FLAW_COUNT'])
            
            if VRFD_FLAWS > TP.ID_REGION_VRFD_FLAW_LIMIT and UNVRFD_FLAWS > TP.ID_REGION_UNVRFD_FLAW_LIMIT and ZONE in [self.dut.numZones -1, self.dut.numZones - 2]:
               objMsg.printMsg('Hd %d\tZn %d\tVRFD_FLAWS %d\tUNVRFD_FLAWS %d\texceeds the spec,need to downgrade.!!!' % (HD_LGC_PSN,ZONE,VRFD_FLAWS,UNVRFD_FLAWS))
               fail_list.append(HD_LGC_PSN)
            else:
               objMsg.printMsg("Hd %d\tZn %d\tVRFD_FLAWS %d\tUNVRFD_FLAWS %d" % (HD_LGC_PSN,ZONE,VRFD_FLAWS,UNVRFD_FLAWS))
               
         if fail_list:
            if self.dut.CAPACITY_CUS.find('STD') < 0 and not self.downGradeOnFly(1, 10293):
               ScrCmds.raiseException(10291,'VRFD_FLAWS & UNVRFD_FLAWS exceeds limit')
   #-------------------------------------------------------------------------------------------------------
   def TA_AFH_TEST_ZONE_SCREEN(self):
      """
      Check AFH test zones if got high TA
      """
      objMsg.printMsg("===============FE_0258915_348429_COMMON_TWO_TEMP_CERT_SCRN_A00005===============")
      # Populate Zone table as TA table do not indicate zone
      entries = None
      try:
         entries = self.dut.dblData.Tables(TP.zone_table['table_name']).tableDataObj()         
      except:
         objMsg.printMsg('Attention:Table P172_ZONE_TBL not exist!!!')
      Zn_Table = {}
      prevZone = -1
      if entries:
         for entry in entries:
            HD_LGC_PSN = int(entry['HD_LGC_PSN'])
            ZONE = int(entry['DATA_ZONE'])
            ZN_START_CYL = int(entry['ZN_START_CYL'])
            TRK_NUM = int(entry['TRK_NUM'])
            if ZONE == prevZone:
               Zn_Table[HD_LGC_PSN,ZONE] += TRK_NUM
            else:
               Zn_Table[HD_LGC_PSN,ZONE] = ZN_START_CYL + TRK_NUM
               prevZone = ZONE
            
      entries = None
      try:
         entries = self.dut.dblData.Tables('P134_TA_DETCR_DETAIL').tableDataObj()
      except:
         objMsg.printMsg('Attention:Table P134_TA_DETCR_DETAIL not exist!!!')
      if entries and Zn_Table:
         TA_list = [0 for hd in range (self.dut.imaxHead)]
         for entry in entries:
            HD_LGC_PSN = int(entry['HD_LGC_PSN'])
            TRK_NUM = int(entry['TRK_NUM'])
            TA_SEVERITY = int(entry['TA_SEVERITY'])
            DFCT_NUM= int(entry['DFCT_NUM'])
            if TA_SEVERITY > 4:
               #Get Zone
               ta_zone = self.dut.numZones-1
               for ZONE in range(self.dut.numZones):
                  if TRK_NUM < Zn_Table[HD_LGC_PSN,ZONE]:
                     break
                  ta_zone = ZONE
               
               if ta_zone in [4, 8, 12, 14, 22, 26, 30]: # Hardcoded AFH test ZOne for now
                  TA_list[HD_LGC_PSN] +=1
                  objMsg.printMsg('HD %2d  ZN %2d  DFCT_NUM %2d  TA_SEVERITY %2d  TRK_NUM %d  AFH_ZONE' % (HD_LGC_PSN, ta_zone, DFCT_NUM, TA_SEVERITY, TRK_NUM))
               else:
                  objMsg.printMsg('HD %2d  ZN %2d  DFCT_NUM %2d  TA_SEVERITY %2d  TRK_NUM %d' % (HD_LGC_PSN, ta_zone, DFCT_NUM, TA_SEVERITY, TRK_NUM))
                  
         fail_list = []
         objMsg.printMsg('TA in AFH Zones Specs %d' % TP.MAX_TA_IN_AFH_TEST_ZONES)
         for hd in range(len(TA_list)):
            if TA_list[hd] > TP.MAX_TA_IN_AFH_TEST_ZONES:
               objMsg.printMsg('Hd %d\tTA_Count %d exceeds the spec,need to downgrade.!!!' % (hd, TA_list[hd]))
               fail_list.append(hd)
            else:
               objMsg.printMsg('Hd %d\tTA_Count %d' % (hd, TA_list[hd]))
         if fail_list:
            #objMsg.printMsg('Hd %s exceeds the TA spec in AFH Test Zone,need to downgrade.!!!' % (fail_list))
            if self.dut.CAPACITY_CUS.find('STD') < 0 and not self.downGradeOnFly(1, 10293):
               ScrCmds.raiseException(10293,'TA_FLAWS in AFH Test ZONE exceeds limit')

   #-------------------------------------------------------------------------------------------------------
   def initializeFlawLists(self):
      PrevFailState = DriveAttributes.get('FAIL_STATE', '')
      if testSwitch.ZFS and 'ZAP' in self.dut.statesExec[self.dut.nextOper] and PrevFailState != 'D_FLAWSCAN':
         return
      # only skip init if use T275 and Zap already run and drive didn't fail in flawscan previously
      objMsg.printMsg('PrevFailState=%s, no ZAP state.. need to initialize defect flaw list..' % PrevFailState)
      self.oUserFlaw.initPList()
      self.oUserFlaw.initTAList()
      self.oUserFlaw.initSFT()
      self.oUserFlaw.initdbi() # initialize the dblog buffer for flawscan within f/w

   #-------------------------------------------------------------------------------------------------------
   def dumpDefectSummaryInfo(self):
      if not self.hdstrProc:
         try:
            #don't clog hdstr results since we can dump after fs
            if testSwitch.FE_0131622_357552_USE_T126_REPSLFAW_INSTEAD_OF_T130:
               #Use unique spc_id for last Servo Flaw dump
               self.oUserFlaw.St(TP.prm_126_read_sft_oracle, spc_id=1000) #report servo flaw table
            else:
               self.oUserFlaw.repServoFlaws()
            self.oUserFlaw.repdbi() # dump db log to host (result file)
            self.oUserFlaw.repPList() # dump p-list to host (result file)
            try:
               if DriveAttributes.get('DISC_1_LOT','NONE')[0]=='P':
                  self.oUserFlaw.St(TP.prm_107_aperio)
               if testSwitch.checkMediaFlip:
                  DISC_FLIP_VALUE = 'PW00000000000'
                  if DriveAttributes.get('DISC_1_LOT','NONE')[0:13] == DISC_FLIP_VALUE or DriveAttributes.get('DISC_2_LOT','NONE')[0:13] == DISC_FLIP_VALUE or DriveAttributes.get('DISC_3_LOT','NONE')[0:13] == DISC_FLIP_VALUE:
                     objMsg.printMsg('========= Media Flip Screen (T107)=========')
                     P107VerifyFlaws = self.dut.dblData.Tables('P107_VERIFIED_FLAWS').tableDataObj()
                     for i in xrange(len(P107VerifyFlaws)):
                        objMsg.printMsg('Head %s : VRFD_FLAWS = %d'%(P107VerifyFlaws[i]['HD_LGC_PSN'],int(P107VerifyFlaws[i]['VRFD_FLAWS'])))
                        if int(P107VerifyFlaws[i]['VRFD_FLAWS']) > TP.specVerFlaws:
                           ScrCmds.raiseException(49999, "This Drive is Media Flip and Drive failed with TA_CNT and VRFD_FLAWS more than spec")
                     objMsg.printMsg('=====================================')
            except:
               pass
         except FOFSerialTestTimeout:
            #Ignore FOFSerialTestTimeout's
            pass

   #-------------------------------------------------------------------------------------------------------
   def flaw_sequence(self):
      if testSwitch.FE_0241396_505235_FLAWSCAN_POWER_LOSS_RECOVERY:
         lastPoint, count = self.checkpoint.getLast(self.dut)
      else:
         lastPoint = None
      if testSwitch.FE_0123768_426568_OUTPUT_SERVO_COUNTERS_DURING_FLAWSCAN or testSwitch.FE_0126442_357552_OUTPUT_SERVO_COUNTERS_AFTER_FLAWSCAN_READPASS:
         from Servo import CServoScreen
         self.oSvoScrn = CServoScreen()

      try:
         #=== Marvel Adaptive Threshold Tuning
         if testSwitch.Enable_ATAFS:
            self.GetExecution(lastPoint, self.MarvelAdaptiveThresholdTuning)
         #=== TA Threshold Tuning
         if testSwitch.FE_0135335_342029_P_DETCR_TP_SUPPORT and not testSwitch.FE_0153357_007955_P_USE_DETCR_PREAMP_SETUP_STATE:
            self.GetExecution(lastPoint, self.TaThresholdTuning)
         #=== Set OCLIM
         if testSwitch.FE_0143876_421106_P_HDSTR_OR_GEMINI_PROCESS_WITH_DRIVE_ATTR:
            self.DriveAttrHdstrProc = self.dut.HDSTR_PROC
         else:
            self.DriveAttrHdstrProc = ConfigVars[CN].get("Hdstr Process",'N')    

         if testSwitch.FE_0111784_347506_USE_DEFAULT_OCLIM_FOR_FLAWSCAN and self.DriveAttrHdstrProc == 'N':
            self.UseDefaultOcLimForFlawscan()
         #=== SWD: Enable AGC
         if not testSwitch.WA_0163780_231166_P_DO_NOT_ENABLE_SWD_FOR_AFS:
            self.oUserFlaw.St(TP.enableAGCUnsafes_11)
         #=== Prog Target 
         if testSwitch.useDefaultTargetForAFS:
            self.UseDefaultTargetForAfs()
         #=== Reduce report in T109 and T126
         if self.hdstrProc:
            self.ReduceReportInT109T126()
         #=== Not auditTest: Flawscan
         if not testSwitch.auditTest:
            # Special odd/even flawsan with separate parameters
            # Intended as a more aggressive flawscan at the OD, but this may be altered through parameters.
            if testSwitch.WA_0128885_357915_SEPARATE_OD_ODD_EVEN_FLAWSCAN:
               self.SeparateOdOddEvenFlawscan()
            # Normal flawscan
            if testSwitch.FULL_INTERLACE_FLAWSCAN:
              self.FullInterlaceFlawscan()
            elif testSwitch.EVEN_ODD_FLAWSCAN and (getattr(TP, 'bgSTD', 0) == 0):
               self.EvenOddFlawscan()
            elif testSwitch.FE_0134776_357915_EO_WRT_EO_RD_FLAWSCAN and (getattr(TP, 'bgSTD', 0) == 0):
               self.EoWrtEoRdFlawscan()
            elif testSwitch.FE_0124728_357915_FULL_WRT_EO_RD_FLAWSCAN and (getattr(TP, 'bgSTD', 0) == 0):
               self.FullWrtEoRdFlawscan()
            elif testSwitch.EO_WRT_FULL_RD_FLAWSCAN and (getattr(TP, 'bgSTD', 0) == 0):
               self.EoWrtFullRdFlawscan()
            elif testSwitch.UMP_SHL_FLAWSCAN:
               self.GetExecution(lastPoint, self.ShingledUmpFlawscan) # SMR products
            else:
               self.SeqFullWrtFullRdFlawscan() # Chengai/ SMR products
         #=== AuditTest: Flawscan
         if testSwitch.auditTest:
            if testSwitch.EVEN_ODD_FLAWSCAN:
               self.AuditTest_EvenOddFlawscan()
            elif testSwitch.FE_0124728_357915_FULL_WRT_EO_RD_FLAWSCAN and (getattr(TP, 'bgSTD', 0) == 0):
               self.AuditTest_FullWrEoRdFlawscan()
            elif testSwitch.EO_WRT_FULL_RD_FLAWSCAN and (getattr(TP, 'bgSTD', 0) == 0):
               self.AuditTest_EoWrtFullRdFlawscan()
            else:
               self.AuditTest_SeqFullWrtFullRdFlawscan()
         #=== Restore OCLIM
         if testSwitch.FE_0111784_347506_USE_DEFAULT_OCLIM_FOR_FLAWSCAN and self.DriveAttrHdstrProc == 'N':
            self.RestoreOcLim()
         #=== Restore Prog Target
         if testSwitch.useDefaultTargetForAFS:
            self.oUserFlaw.St({
                              'test_num': 178,
                              'prm_name': 'Recover RAP from Flash',
                              'timeout': 500,
                              'spc_id' : 1,
                              'CWORD1': 0x204,
                           })
         #=== SWD: Disable AGC
         if not testSwitch.FE_0116185_357260_ENABLE_SWD_DURING_SERVO_FS:
            self.oUserFlaw.St(TP.disableAGCUnsafes_11)
            if 'S' in StateTable[self.dut.nextOper][self.dut.nextState][OPT]:
               objMsg.printMsg("Finish D_FLAW in HDSTR testing...")
               self.oUserFlaw.St(TP.hdstr_tempCheck)
               return
      finally:
         self.dut.driveattr['FLAW_SCAN_TESTED'] = 1


   # MSE scan odd
   if testSwitch.FE_0118875_006800_RUN_T109_MSE_SCAN:
      def T109MSEScan(self, inPrm, percent, rd_trim, trkctl):
         fsParm = inPrm.copy()
         fsParm['PERCENT_LIMIT'] = percent
         fsParm['R_STDEV_LIMIT'] = rd_trim
         if (trkctl == 'odd'):
            fsParm['WRODDTRK'] = ()
         elif (trkctl == 'even'):
            fsParm['WREVENTRK'] = ()
         self.oUserFlaw.St(fsParm)

   #-------------------------------------------------------------------------------------------------------
   def runAdjacentServoFS(self):
      if testSwitch.FE_0241396_505235_FLAWSCAN_POWER_LOSS_RECOVERY:
         lastPoint, count = self.checkpoint.getLast(self.dut)
      else:
         lastPoint = None

      if (DriveAttributes.get('DENT_SCRN','NONE') == 'NONE' or self.dut.powerLossEvent) and testSwitch.FE_0139575_336764_SKIP_DSP_SCRN_IF_DRIVE_FAIL_AT_T109_PRE2 :
         if testSwitch.FE_0165754_409401_P_SKIP_DSP_SCRN_FOR_2_HD and self.dut.imaxHead == 2:
            pass
         else:
            DriveAttributes['DENT_SCRN'] = 'FAIL'
            DspScreenPrms = TP.DspScreen_140.copy()
            self.oUserFlaw.St(DspScreenPrms)
            DriveAttributes['DENT_SCRN'] = 'PASS'
      self.GetExecution(lastPoint, self.oUserFlaw.St, TP.adj_svo_scan_write_prm_126) #scan adjacent tracks of mapped servo flaws in write positition
      self.GetExecution(lastPoint, self.oUserFlaw.St, TP.adj_svo_scan_read_prm_126) #scan adjacent tracks of mapped servo flaws in read positition
      PrmReportSFT = TP.prm_126_read_sft_oracle.copy()
      PrmReportSFT['prm_name'] = 'PRM_REPORT_RAW_SERVO_FLAWS_126'
      PrmReportSFT['spc_id'] = 126
      self.GetExecution(lastPoint, self.oUserFlaw.St, PrmReportSFT) #report servo flaw table
      validList = self.SaveSList(lastPoint)
      if testSwitch.FE_0137096_342029_P_T64_SUPPORT:
         self.GetExecution(lastPoint, self.oUserFlaw.St, TP.prm_64_servo_pad, validList)          # Skipped Track Padding
      else:
         self.GetExecution(lastPoint, self.oUserFlaw.St, TP.prm_126_cw1, validList)               # Skipped Track Padding
      self.oUserFlaw.St(TP.prm_126_read_sft_oracle) #report servo flaw table

   #-------------------------------------------------------------------------------------------------------
   def runTAScan(self):
      if testSwitch.FE_0143743_426568_P_RUN_T_67_FOR_TA_SCAN:
         self.oUserFlaw.St(TP.prm_67_TA_Reset)
         self.oUserFlaw.St(TP.prm_67_TA_DC_Scan)
         #self.oUserFlaw.St(TP.prm_67_TA_Burnish)
         self.oUserFlaw.St(TP.prm_67_TA_DC_ReScan)
      else:
         if testSwitch.FE_0139634_399481_P_DETCR_T134_T94_CHANGES:
            self.oUserFlaw.St(TP.prm_134_TA_Rescan)
         else:
            base_prm_134_TA_Scan = TP.prm_134_TA_Scan.copy()
            if testSwitch.T134_TA_FAILURE_SPEC and testSwitch.extern.FE_0315265_228371_T134_SPEC_ADD_SYMBOL_LENTGTH_NO_CRITERIA:
               T134cword1= base_prm_134_TA_Scan['CWORD1'] | 0x100
               base_prm_134_TA_Scan.update({
                                        'CWORD1'  : T134cword1,                           #enable spec
                                        'MAX_ASPS'  :(TP.TA_PER_DRV_1D, TP.TA_PER_SUF_1D),#fail max number ta, drive/surface,"0" means off criteria
                                        'MARVELL_THRESH_LIMIT'  :TP.MARVELL_THRESH_LIMIT, #last 4 bits, number of passive, top 12 bits, TA track length                                         })
                                         })
               PartNum = DriveAttributes.get('PART_NUM', ConfigVars[CN].get('PartNum', '9WN144'))
               objMsg.printMsg("PartNum %s" % PartNum)
               if PartNum[5]=='4': #4Hd drive
                  base_prm_134_TA_Scan.update({
                                            'MAX_ASPS'  :(TP.TA_PER_DRV_2D, TP.TA_PER_SUF_2D),#max ta, drive/surface,"0" means off criteria
                                             })


            try:
               startIndex = len(self.dut.dblData.Tables('P134_TA_DETCR_DETAIL').tableDataObj())
            except:
               startIndex = 0
            try:
               self.oUserFlaw.St(base_prm_134_TA_Scan)
            except ScriptTestFailure, failureData:
               if failureData[0][2] == 10293:
                  if self.dut.BG not in ['SBS']:
                     if  testSwitch.ENABLE_ON_THE_FLY_DOWNGRADE and self.downGradeOnFly(1, 10293):
                        objMsg.printMsg('EC10293, downgrade to %s as %s' % (self.dut.BG, self.dut.partNum))
                     else:
                        raise failureData
            
                  totalTACount = 0 # For YIP, only need count TA 5 / 6 / 7
                  for entry in self.dut.dblData.Tables('P134_TA_DETCR_DETAIL').tableDataObj()[startIndex:]:
                     if int(entry['TA_SEVERITY']) in [6,7]:
                        totalTACount += 1
                  objMsg.printMsg('TA Count for 6 / 7: %d, Spec: %d'%(totalTACount, base_prm_134_TA_Scan['MAX_ASPS'][0]))
                  if totalTACount > base_prm_134_TA_Scan['MAX_ASPS'][0]:
                     raise failureData                  
               else:
                  raise failureData
            #if hasattr(TP,'prm_134_TA_Burnish'):
            #   self.oUserFlaw.St(TP.prm_134_TA_Burnish)
            #if hasattr(TP,'prm_134_TA_Rescan'):
            #   self.oUserFlaw.St(TP.prm_134_TA_Rescan)
            #self.oUserFlaw.St(TP.prm_134_TA_Scan_S34)
            #self.oUserFlaw.St(TP.prm_134_TA_Scan_S56)
            #self.oUserFlaw.St(TP.prm_134_TA_Scan_S67)
         if testSwitch.checkMediaFlip:
            DISC_FLIP_VALUE = 'PW00000000000'
            if DriveAttributes.get('DISC_1_LOT','NONE')[0:13] == DISC_FLIP_VALUE or DriveAttributes.get('DISC_2_LOT','NONE')[0:13] == DISC_FLIP_VALUE or DriveAttributes.get('DISC_3_LOT','NONE')[0:13] == DISC_FLIP_VALUE:
               objMsg.printMsg('========= Media Flip Screen (T134)=========')
               P134TaSumHD2 = self.dut.dblData.Tables('P134_TA_SUM_HD2').tableDataObj()
               for i in xrange(len(P134TaSumHD2)):
                  objMsg.printMsg('Head %s : TA Count = %d'%(P134TaSumHD2[i]['HD_LGC_PSN'],int(P134TaSumHD2[i]['TA_CNT'])))
                  if int(P134TaSumHD2[i]['TA_CNT']) > TP.specTA_CNT:
                     ScrCmds.raiseException(49999, "This Drive is Media Flip and Drive failed with TA_CNT and VRFD_FLAWS more than spec")
               objMsg.printMsg('=====================================')


      base_TA_deallocation_prm_215 = TP.TA_deallocation_prm_215.copy()

      if testSwitch.T215_DETCR_TA_PAD_BY_SEVERITY and testSwitch.extern.FE_0316551_228371_TA_PAD_BY_SEVERITY:
         T215cword2 = base_TA_deallocation_prm_215['CWORD2'] | 0x40 # pad by severity
         base_TA_deallocation_prm_215.update({
                                           'CWORD2':T215cword2, 
                                          }) 

      self.oUserFlaw.St(base_TA_deallocation_prm_215) # TA padding, 4 track deallocation for bins 4,5,6,7

      if testSwitch.FE_0112719_399481_ADD_T126_DATA_TO_DATAFLAWSCAN_TASCAN:
         self.oUserFlaw.St(TP.prm_126_read_sft)  #report servo flaw table, no data to oracle

      if testSwitch.FE_0173804_007955_ADD_T130_TALIST_DATA_TO_DATAFLAWSCAN_TASCAN:
         self.oUserFlaw.repTAList()  #report servo flaw table

      if testSwitch.YARRAR:
         for row in self.dut.dblData.Tables('P134_TA_SUM_HD2').tableDataObj() :
            if int(row['AMP6_CNT']) + int(row['AMP7_CNT']) >= 9:
               objMsg.printMsg('P134_TA_SUM_HD2 AMP6_CNT+AMP7_CNT>=9. Downgrade with ec10293')
               CState(self.dut).downGradeOnFly(1,10293)
               if self.dut.partNum[-3:] not in TP.RetailTabList:
                  ScrCmds.raiseException(10293,"P134_TA_SUM_HD2 AMP6_CNT+AMP7_CNT>=9 and Cannot Downgrade")
               break

   #-------------------------------------------------------------------------------------------------------
   def buildPList(self, spcId = 1):
      self.oUserFlaw.writeDbiToPList(spcId)
      self.oUserFlaw.writeSrvListToPList()

   #-------------------------------------------------------------------------------------------------------
   def runFlawScanBeatup(self):
      '''
      P117_MEDIA_SCREEN: 
       HD_PHYS_PSN HD_LGC_PSN SCRATCH_ID START_ZONE END_ZONE BEGINNING_TRK ENDING_TRK SCRATCH_LENGTH DEFECTS TOTAL_BYTES SCREEN_PF_FLAG 
                 1          1          1          0        0             0          5              6       4          13              P 
                 1          1          3          0        0           288        299             12      10          35              P 
                 0          0          4          4        4         12393      12395              3       2          29              P 
                 0          0          5          4        4         12474      12498             25     114        4498              P
      '''
      #=== inParms
      inPrmWrite = TP.prm_AFS_2T_Write_Beatup_109.copy()
      inPrmRead = TP.prm_AFS_2T_Read_Beatup_109.copy()
      inPrmSrv = TP.svoFlawPrm_126.copy()
      inPrmWrite['stSuppressResults'] = ST_SUPPRESS__CM_OUTPUT | ST_SUPPRESS_RECOVER_LOG_ON_FAILURE
      inPrmRead['stSuppressResults'] = ST_SUPPRESS__CM_OUTPUT | ST_SUPPRESS_RECOVER_LOG_ON_FAILURE
      inPrmSrv['stSuppressResults'] = ST_SUPPRESS__CM_OUTPUT | ST_SUPPRESS_RECOVER_LOG_ON_FAILURE

      if testSwitch.SMR:
         UmpZones = TP.UMP_ZONE_BY_HEAD[self.dut.imaxHead][self.dut.numZones]
      BeatupExtendedTracks = TP.BeatupExtendedTracks
      BeatupScratchLen = TP.BeatupScratchLen
      NumberOfWriteLoops = TP.NumberOfWriteLoops
      #=== Run Media Damage Screen
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=5, onTime=5, useESlip=1)
      self.DeleteDblData("P117_MEDIA_SCREEN")
      self.oUserFlaw.St(TP.prm_scratch_fill_117_1)

      #=== Get P117_MEDIA_SCREEN table
      objMsg.printMsg ("###=== AFS_BEATUP: START ===###")
      try:
         ScratchEntries = self.dut.dblData.Tables('P117_MEDIA_SCREEN').tableDataObj()
         objMsg.printMsg ("NumScratches = %d" %len(ScratchEntries))
      except:
         objMsg.printMsg ("P117_MEDIA_SCREEN not found. Exit.")
         objMsg.printMsg ("###=== AFS_BEATUP: END ===###")
         return

      #=== Get system zone info
      sysZnStartEndCyl = {}
      sysZt = self.dut.dblData.Tables(TP.zone_table['resvd_table_name']).tableDataObj()
      for hd in xrange(self.dut.imaxHead):
         Index = self.dth.getFirstRowIndexFromTable_byHead(sysZt, hd)
         startCyl = int(sysZt[Index]['ZN_START_CYL'])
         endCyl = startCyl + int(sysZt[Index]['TRK_NUM'])  - 1
         while Index+1< len(sysZt) and int(sysZt[Index]['ZN']) == int(sysZt[Index+1]['ZN']):
            endCyl += int(sysZt[Index+1]['TRK_NUM'])
            Index += 1   
         sysZnStartEndCyl.setdefault(hd, {}).update({'startCyl': startCyl, 'endCyl': endCyl})

      #=== Run beat-up test
      ScratchIndex = 1
      for entry in ScratchEntries:
         scratchLen = int(entry['SCRATCH_LENGTH'])
         if testSwitch.SMR:
            #=== Scratches in UMP zones
            condition = (int(entry['START_ZONE']) in UmpZones) or (int(entry['END_ZONE']) in UmpZones)            
            extTracks = BeatupExtendedTracks
         else:
            condition = scratchLen > BeatupScratchLen
            extTracks = int(scratchLen * BeatupExtendedTracks + 0.5)

         if condition:
            head = int(entry['HD_LGC_PSN'])
            startCyl = max(int(entry['BEGINNING_TRK']) - extTracks, 0)
            endCyl = min(int(entry['ENDING_TRK']) + extTracks, self.dut.maxTrack[head])
            #=== Handling for test cyl falling within system zone (MD system zone)
            if startCyl in xrange(sysZnStartEndCyl[head]['startCyl'],sysZnStartEndCyl[head]['endCyl']+1):
               objMsg.printMsg ("Start cyl within system zone. Shift cyl.")
               startCyl = sysZnStartEndCyl[head]['endCyl'] + 1
            if endCyl in xrange(sysZnStartEndCyl[head]['startCyl'],sysZnStartEndCyl[head]['endCyl']+1):
               objMsg.printMsg ("End cyl within system zone. Shift cyl.")
               endCyl = sysZnStartEndCyl[head]['startCyl'] - 1
            #=== Update inParms
            inPrmWrite['HEAD_RANGE'] = head * 0x0101
            inPrmWrite['START_CYL'] = self.oUserFlaw.oUtility.ReturnTestCylWord(startCyl)
            inPrmWrite['END_CYL'] = self.oUserFlaw.oUtility.ReturnTestCylWord(endCyl)
            inPrmRead['HEAD_RANGE'] = head * 0x0101
            inPrmRead['START_CYL'] = self.oUserFlaw.oUtility.ReturnTestCylWord(startCyl)
            inPrmRead['END_CYL'] = self.oUserFlaw.oUtility.ReturnTestCylWord(endCyl)
            #=== Run interlace flaw scan
            objMsg.printMsg ("BEATUP_SCRATCH_%02d: H%d, Trks %d - %d, ScrLen %d, extTracks %d"
                           %(ScratchIndex, head,
                             int(entry['BEGINNING_TRK']),
                             int(entry['ENDING_TRK']),
                             scratchLen, extTracks))
            self.oServoFlaw.servoFlawScan(inPrmSrv, SeekType.writeSeek)
            inPrmWrite['LOOP_CNT'] = 1   # First write x1
            self.evenOddFlawScan(inPrmWrite, 'even')
            inPrmWrite['LOOP_CNT'] = NumberOfWriteLoops
            self.evenOddFlawScan(inPrmWrite, 'odd')
            self.oServoFlaw.servoFlawScan(inPrmSrv, SeekType.readSeek)
            self.evenOddFlawScan(inPrmRead, 'even')
            self.oServoFlaw.servoFlawScan(inPrmSrv, SeekType.writeSeek)
            self.evenOddFlawScan(inPrmWrite, 'even')
            self.oServoFlaw.servoFlawScan(inPrmSrv, SeekType.readSeek)
            self.evenOddFlawScan(inPrmRead, 'odd')
         ScratchIndex += 1
      objMsg.printMsg ("###=== AFS_BEATUP: END ===###")
      #=== Re-build PList 
      self.buildPList(spcId = 1492) # Compare with spcId 1491 to check additional captured by Beatup Test

   #-------------------------------------------------------------------------------------------------------
   def runMediaDamageScreen(self):
      #=== Run T117 Media Damage Screen
      self.DeleteDblData("P117_MEDIA_SCREEN")
      inParm = TP.prm_scratch_fill_117_1.copy()
      inParm['spc_id'] = 2
      try:
         self.oUserFlaw.St(inParm)
      except: pass
      #=== Screen number of scratches per head per zone (PHPZ)
      if testSwitch.FE_ENABLE_T117_SCREEN_NUM_SCRATCH_PHPZ:
         objMsg.printMsg ("###=== Screen number of scratches per head per zone ===###")
         #=== Get P117_MEDIA_SCREEN table
         try:
            ScratchEntries = self.dut.dblData.Tables('P117_MEDIA_SCREEN').tableDataObj()
         except:
            objMsg.printMsg ("P117_MEDIA_SCREEN not found. Exit.")
            return
   
         #=== Populate number of scratches per head per zone
         NumScratchPerHeadPerZone = dict()
         try: # Return if P117_MEDIA_SCREEN has no zone info. 
            for entry in ScratchEntries:
               key = int(entry['HD_LGC_PSN']), int(entry['START_ZONE'])
               NumScratchPerHeadPerZone[key] = NumScratchPerHeadPerZone.get(key, 0) + 1
         except:
            objMsg.printMsg ("P117_MEDIA_SCREEN does not have zone info. Exit.")
            return

         #=== Print result
         try:
            objMsg.printMsg ("MaxNumScratchPerHeadPerZone = %d" %(max(NumScratchPerHeadPerZone.values())))
         except:
            objMsg.printMsg ("MaxNumScratchPerHeadPerZone = 0")
            return

         #=== Check limit
         NumScratchLimitPHPZ = TP.T117_NUM_SCRATCH_LIMIT_PHPZ
         ScreenZoneList = TP.T117_SCREEN_ZONE_LIST
         for key in NumScratchPerHeadPerZone:
            #=== Screen all zones
            if "All" in ScreenZoneList:
               ScreenZone = True
            #=== Screen selected zones only
            else:
               if key[1] in ScreenZoneList:
                  ScreenZone = True
               else:
                  ScreenZone = False
            #=== Screening   
            if ScreenZone:
               ScreenZone = False
               if NumScratchPerHeadPerZone[key] >= NumScratchLimitPHPZ:
                  ScrCmds.raiseException(10296, 'NumScratchPerHeadPerZone exceeded limit, %d >= %d.' 
                                                %(NumScratchPerHeadPerZone[key], NumScratchLimitPHPZ))

   #-------------------------------------------------------------------------------------------------------   
   def runScratchFill(self):
      if testSwitch.FE_0241396_505235_FLAWSCAN_POWER_LOSS_RECOVERY:
         lastPoint, count = self.checkpoint.getLast(self.dut)
      else:
         lastPoint = None

      if testSwitch.VARIABLE_SPARES:
         self.oUserFlaw.saveSListToPcFile()

      #=== T118: Padding by vbar
      isBpiFileNeeded = testSwitch.FE_0205578_348432_T118_PADDING_BY_VBAR and not testSwitch.FE_0269922_348085_P_SIGMUND_IN_FACTORY 
      if isBpiFileNeeded:
         from bpiFile import CBpiFile
         obpiFile = CBpiFile()
         dlfile = (CN, obpiFile.bpiFileName)

      #=== TA padding
      if testSwitch.FE_0125537_399481_TA_ONLY_T118_CALL:
         inPrm = TP.prm_118_rev2_radial002_TA_Only.copy()
         if isBpiFileNeeded: inPrm['dlfile'] = dlfile
         self.GetExecution(lastPoint, self.oUserFlaw.St, inPrm)
      if testSwitch.FE_0151000_007955_P_TRIPAD_UNVISITED_T118_CALL:
         inPrm = TP.prm_118_Tripad_Unvisited.copy()
         if isBpiFileNeeded: inPrm['dlfile'] = dlfile
         self.GetExecution(lastPoint, self.oUserFlaw.St, inPrm)
      #=== Long padding
      inPrm = TP.prm_118_rev2_long002.copy()
      if isBpiFileNeeded: inPrm['dlfile'] = dlfile
      self.GetExecution(lastPoint, self.oUserFlaw.St, inPrm)
      #=== Radial padding
      inPrm = TP.prm_118_rev2_radial002.copy()
      if isBpiFileNeeded: inPrm['dlfile'] = dlfile
      self.GetExecution(lastPoint, self.oUserFlaw.St, inPrm)
      #=== Short padding
      inPrm = TP.prm_118_rev2_short002.copy()
      if isBpiFileNeeded: inPrm['dlfile'] = dlfile
      self.GetExecution(lastPoint, self.oUserFlaw.St, inPrm)
      #=== Unvisited padding
      inPrm = TP.prm_118_rev2_unvisited002.copy()
      if isBpiFileNeeded: inPrm['dlfile'] = dlfile
      self.GetExecution(lastPoint, self.oUserFlaw.St, inPrm)
      inPrm = None # Garbage Collector
      #=== Sort PList
      self.GetExecution(lastPoint, self.oUserFlaw.St, TP.prm_118_sort_fill_def_list)
      #=== Wedge padding
      if testSwitch.FE_0137096_342029_P_T64_SUPPORT:
         self.GetExecution(lastPoint, self.oUserFlaw.St, TP.prm_64_isolated_servo_pad)
      else:
         validList = self.SaveSList(lastPoint)
         self.GetExecution(lastPoint, self.oUserFlaw.St, TP.prm_scratch_fill_117_2, validList)
      #=== Filter scratches
      self.GetExecution(lastPoint, self.filterExcessiveScratchesInMovingWindow)

   #-------------------------------------------------------------------------------------------------------
   def filterExcessiveScratchesInMovingWindow(self):
      try:
         data = self.dut.dblData.Tables('P117_MEDIA_SCREEN').tableDataObj()

         self.dut.dblData.Tables('P117_MEDIA_SCREEN').deleteIndexRecords(confirmDelete=1)
         self.dut.dblData.delTable('P117_MEDIA_SCREEN')
      except:
         if DEBUG:
            objMsg.printMsg('Cannot Access P117_MEDIA_SCREEN table')
         return

      try:
         ScratchLength = TP.prm_filterExcessiveScratches['SCRATCH_LENGTH']
         NumScratches = TP.prm_filterExcessiveScratches['NUM_SCRATCHES']
         TrkWindow = TP.prm_filterExcessiveScratches['TRK_WINDOW']
      except:
         if DEBUG:
            objMsg.printMsg('prm_filterExcessiveScratches input not defined')
         return

      try:
         Scratches = {}
         for entry in data:
            if int(entry['SCRATCH_LENGTH']) > ScratchLength:
               head = int(entry['HD_PHYS_PSN'])
               beginning_trk = int( entry['BEGINNING_TRK'])
               scratch_length = int( entry['SCRATCH_LENGTH'])

               if Scratches.has_key( head ):
                  Scratches[head].append([beginning_trk, scratch_length])
               else:
                  Scratches[head] = [[beginning_trk, scratch_length]]

         for key in Scratches.keys():
            Scratches[key].sort()
      except:
         if DEBUG:
            objMsg.printMsg('Not filtering for excessive scratches in P117_MEDIA_SCREEN')
         return

      objMsg.printMsg("Filtering drives with more than %d" % NumScratches + " scratches longer than %d" % ScratchLength + " within a %d" % TrkWindow + " track window in P117_MEDIA_SCREEN")
      for key in Scratches:
         ScratchesList = Scratches[key]
         for item in ScratchesList:
            # Perform the check once we can look at "NumScratches" scratches at once
            # Then, if the track numbers for scratches that are longer than "ScratchLength" length are within
            #   the "TrkWindow" window, then there are too many scratches within the window.
            if ScratchesList.index(item) >= (NumScratches - 1):
               EndingTrk = ScratchesList[ScratchesList.index(item)][0]
               BeginningTrk = ScratchesList[ScratchesList.index(item) - NumScratches - 1][0]
               if (EndingTrk - BeginningTrk ) < TrkWindow:
                  ScrCmds.raiseException(10304,"Too many scratches within a given window in P117_MEDIA_SCREEN") #10304 = MEDIA_DAMAGE_FAILURE in codes.h

   #-------------------------------------------------------------------------------------------------------
   def evenOddFlawScan(self, inPrm, mode):
      '''
      To be used for flawscan reading even or odd tracks.  User passes in mode, either 'even' or 'odd'
      Test parameter WREVENTRK or WRODDTRK is then added the the parameters list and the test is called.
      '''
      fsParm = inPrm.copy()
      if mode == 'even':
         fsParm['WREVENTRK'] = ()
      elif mode == 'odd':
         fsParm['WRODDTRK'] = ()
      elif mode == 'all':
         objMsg.printMsg('Flawscan ALL MODE')         
      else:
         ScrCmds.raiseException(11044,"evenOddFlawScan: input parameter 'mode' is not specified or specified improperly")
      self.oUserFlaw.St(fsParm)

   #-------------------------------------------------------------------------------------------------------
   def auditTestServoFlawscan(self,inPrm,seekType):
      """ run servo flawscan on audit test heads and zone groups determined in RAP file/auditTestRAPDict
      """
      svoFSPrm = inPrm.copy()
      # NEW INPUT PARM ??!! timeout needs to be based on number of track being tested in each zone_group
      #SeekType.writeSeek
      objMsg.printMsg("                       AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA                         ",objMsg.CMessLvl.IMPORTANT)
      objMsg.printMsg("              ******** AUDIT TEST: HEADS AND TRACK BANDS SET IN RAP TABLE ********             ",objMsg.CMessLvl.IMPORTANT)
      for head, zoneGroups in self.dut.auditTestRAPDict.items():
         hdMask = (head<<8) + head
         svoFSPrm["HEAD_RANGE"] = (hdMask)
         for band in zoneGroups:
            startCyl = band[0]
            endCyl = band[1]
            svoFSPrm["timeout"] = 2*(endCyl-startCyl)
            upperWord,lowerWord = self.oUserFlaw.oUtility.ReturnTestCylWord(startCyl)
            svoFSPrm["START_CYL"] = upperWord,lowerWord
            upperWord,lowerWord = self.oUserFlaw.oUtility.ReturnTestCylWord(endCyl)
            svoFSPrm["END_CYL"] = upperWord,lowerWord
            self.oServoFlaw.servoFlawScan(svoFSPrm,seekType)

   #-------------------------------------------------------------------------------------------------------
   def auditTestUserFlawscan(self,inPrm,mode = 'none'):
      """ run user flawscan on audit test heads and zone groups determined in RAP file/auditTestRAPDict
      """
      userFSPrm = inPrm.copy()
      objMsg.printMsg("                       AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA                         ",objMsg.CMessLvl.IMPORTANT)
      objMsg.printMsg("              ******** AUDIT TEST: HEADS AND TRACK BANDS SET IN RAP TABLE ********             ",objMsg.CMessLvl.IMPORTANT)
      for head, zoneGroups in self.dut.auditTestRAPDict.items():
         hdMask = (head<<8) + head
         userFSPrm["HEAD_RANGE"] = (hdMask)
         for band in zoneGroups:
            startCyl = band[0]
            endCyl = band[1]
            userFSPrm["timeout"] = 2*(endCyl-startCyl)
            upperWord,lowerWord = self.oUserFlaw.oUtility.ReturnTestCylWord(startCyl)
            userFSPrm["START_CYL"] = upperWord,lowerWord
            upperWord,lowerWord = self.oUserFlaw.oUtility.ReturnTestCylWord(endCyl)
            userFSPrm["END_CYL"] = upperWord,lowerWord
            if testSwitch.EVEN_ODD_FLAWSCAN:
               self.evenOddFlawScan(userFSPrm,mode)
            else:
               self.oUserFlaw.St(userFSPrm)

   #-------------------------------------------------------------------------------------------------------
   def DeleteDblData(self, tblName):
      try:
         self.dut.dblData.Tables(tblName).deleteIndexRecords(1)
         self.dut.dblData.delTable(tblName)
         objMsg.printMsg("Deleted table %s" %(tblName))
      except:
         objMsg.printMsg("Can't find table %s" %(tblName))
         pass

   #-------------------------------------------------------------------------------------------------------
   def CreateThresInfoData(self):
      self.thresInfo = {}
      #=== Get P107_DBI_LOG_ZONE_SUMMARY
      self.DeleteDblData('P107_DBI_LOG_ZONE_SUMMARY')
      self.oUserFlaw.repdbi()
      dt = self.dut.dblData.Tables('P107_DBI_LOG_ZONE_SUMMARY').tableDataObj()
      self.DeleteDblData('P107_DBI_LOG_ZONE_SUMMARY')

      #=== Get P172_ZONE_TBL
      zt = self.dut.dblData.Tables(TP.zone_table['table_name']).tableDataObj()      

      #=== Create thresInfo dict
      for head in xrange(self.dut.imaxHead):
         for zone in xrange(self.dut.numZones):
            #=== start and end cyls
            Index = self.dth.getFirstRowIndexFromTable_byZone(zt, head, zone)
            sc = int(zt[Index]['ZN_START_CYL'])
            ec = sc + int(zt[Index]['NUM_CYL']) - 1
            while Index+1< len(zt) and int(zt[Index]['ZN']) == int(zt[Index+1]['ZN']):
               ec += int(zt[Index+1]['NUM_CYL']) 
               Index += 1
               
            startCyl = self.oUserFlaw.oUtility.ReturnTestCylWord(sc)
            endCyl = self.oUserFlaw.oUtility.ReturnTestCylWord(ec)
            #=== zone masks
            if (2**zone) < 0xFFFFFFFF + 1:
               znMask = 2**zone
               znMaskExt = 0
            else:
               znMask = 0
               znMaskExt = 2**zone
            zoneMask = self.oUserFlaw.oUtility.ReturnTestCylWord(znMask)
            zoneMaskExt = self.oUserFlaw.oUtility.ReturnTestCylWord(znMaskExt)

            item = {'headRange': 0x0101 * head,
                    'startCyl': startCyl,
                    'endCyl': endCyl,
                    'zoneMask': zoneMask,
                    'zoneMaskExt': zoneMaskExt,
                    'dbiCap': int(dt[zone]['CAPACITY']),
                    'adaptVgar': 0,
                    'origThres': 0,
                    'newThres': 0,
                    'adjThres': 0,
                    'qualTrk': 0,
                    'qualCnt': 0,
                    'qualStat': 0,
                    'verCnt': -1,
                    'unverCnt': -1,
                    'doneFlag': 0,
                    'retryNum': 0,
                   }
            self.thresInfo.setdefault((head, zone),{}).update(item)

   #-------------------------------------------------------------------------------------------------------
   def GetVgarAndThres(self):
      if (not testSwitch.KARNAK):
         tt = self.dut.dblData.Tables('P109_THRESHOLD_SUM').tableDataObj()
      try:
         for rec in tt:
            head = int(rec['HD_LGC_PSN'])
            zone = int(rec['DATA_ZONE'])
            self.thresInfo[head, zone]['adaptVgar'] = int(rec['ADAPT_VGAR'])
            self.thresInfo[head, zone]['origThres'] = int(rec['ORIG_THRES'])
            self.thresInfo[head, zone]['newThres'] = int(rec['NEW_THRES'])
            self.thresInfo[head, zone]['qualTrk'] = int(rec['QUAL_TRACK'])
            self.thresInfo[head, zone]['qualCnt'] = int(rec['QUAL_CNT'])
            self.thresInfo[head, zone]['qualStat'] = int(rec['STATUS'])
      except:
         pass
   
   #-------------------------------------------------------------------------------------------------------
   def repThresInfo(self):
      objMsg.printMsg("")
      objMsg.printMsg("P000_FLAWSCAN_READ_THRES:")
      objMsg.printMsg("HEAD  ZONE  ADAPT_VGAR  ORIG_THRES  NEW_THRES  ADJ  CAP_PER_ZONE  VER_CNT  UNVER_CNT  QUAL_TRK  QUAL_CNT  QUAL_STAT  STAT  RETRY_NUM")
      fmt = "%4d  %4d  %10d  %10d  %9d  %3d  %12d  %7d  %9d  %8d  %8d  %9d  %4d  %9d"
      for head in xrange(self.dut.imaxHead):
         for zone in xrange(self.dut.numZones):
            objMsg.printMsg(fmt %(head, zone,
                                  self.thresInfo[head, zone]['adaptVgar'],
                                  self.thresInfo[head, zone]['origThres'],
                                  self.thresInfo[head, zone]['newThres'],
                                  self.thresInfo[head, zone]['adjThres'],
                                  self.thresInfo[head, zone]['dbiCap'],
                                  self.thresInfo[head, zone]['verCnt'],
                                  self.thresInfo[head, zone]['unverCnt'],
                                  self.thresInfo[head, zone]['qualTrk'],
                                  self.thresInfo[head, zone]['qualCnt'],
                                  self.thresInfo[head, zone]['qualStat'],
                                  self.thresInfo[head, zone]['doneFlag'],
                                  self.thresInfo[head, zone]['retryNum']
                                 )
                           )
      objMsg.printMsg("")

   #-------------------------------------------------------------------------------------------------------
   def getVerUnver(self):
      self.DeleteDblData('P140_FLAW_COUNT')
      try:
         #=== Report DBI
         inPrmDbi = TP.prm_DBI_Fail_Limits_140.copy()
         inPrmDbi['prm_name'] = "Report DBI"
         inPrmDbi['spc_id'] = 100
         self.oUserFlaw.St(inPrmDbi)
         #=== Retrieve table P140_FLAW_COUNT
         tf = self.dut.dblData.Tables('P140_FLAW_COUNT').tableDataObj()
         for rec in tf:
            head = int(rec['HD_LGC_PSN'])
            zone = int(rec['DATA_ZONE'])
            self.thresInfo[head, zone]['verCnt'] = int(rec['VERIFIED_FLAW_COUNT'])
            self.thresInfo[head, zone]['unverCnt'] = int(rec['UNVERIFIED_FLAW_COUNT'])
      except:
         pass
      self.DeleteDblData('P140_FLAW_COUNT')

   #-------------------------------------------------------------------------------------------------------
   def UseDefaultOcLimForFlawscan(self):
      #=== Get OCLIM in order to check later
      self.currOClim = []
      for head in range(self.dut.imaxHead):
         self.currOClim.append(self.oSrvFunc.getwriteOCLIM_byHead(head))
   
      objMsg.printMsg("Current OCLIM = %s " %(self.currOClim))
   
      #=== Set OCLIM in memory only
      if testSwitch.FE_0243459_348085_DUAL_OCLIM_CUSTOMER_CERT:
         self.oSrvFunc.setOClim({},TP.defaultOCLIM_customer)
      else:
         self.oSrvFunc.setOClim({},TP.defaultOCLIM)
      tempOClim = self.oSrvFunc.getOCLIM(TP.oclimSAPOffset,)  #SET ALL HEADS AT ONCE
      objMsg.printMsg("OCLIM set to default for Flaw Scan => %s " %(tempOClim))
   
   #-------------------------------------------------------------------------------------------------------
   def RestoreOcLim(self):
      objPwrCtrl.powerCycle(5000,12000,10,10) #use to restore OCLIM
      endOClim = []
      for head in range(self.dut.imaxHead):
         endOClim.append(self.oSrvFunc.getwriteOCLIM_byHead(head))
   
      if self.currOClim != endOClim:
         objMsg.printMsg("Pre-FlawScan OCLIM of %s IS NOT EQUAL TO Post-FlawScan OCLIM of %s" % (self.currOClim,endOClim))
         ScrCmds.raiseException(11044,"OCLIM HAS CHANGED.")
      objMsg.printMsg("Pre-FlawScan OCLIM restored.  Pre-FlawScan OCLIM = %s.  Post-FlawScan OCLIM = %s" % (self.currOClim,endOClim))
   
   #-------------------------------------------------------------------------------------------------------
   def UseDefaultTargetForAfs(self):
      from RdWr import CProgRdChanTrg
      oProg = CProgRdChanTrg()
      oProg.setNPT_156 = TP.setNPT_156.copy()
      zone_mask = 0
      for zone in range(self.dut.numZones):
         zone_mask = (1<<zone)
      #oProg.setNPT_156['ZONE_MASK'] = self.oUserFlaw.oUtility.ReturnTestCylWord(self.oUserFlaw.oUtility.setZoneMask(range(self.dut.numZones)))
      oProg.setNPT_156['ZONE_MASK'] = self.oUserFlaw.oUtility.ReturnTestCylWord(zone_mask & 0xFFFFFFFF)
      oProg.setNPT_156['ZONE_MASK_EXT'] = self.oUserFlaw.oUtility.ReturnTestCylWord(zone_mask >> 32 & 0xFFFFFFFF)
      defaultTarget = getattr(TP,'defaultNptTarget_Index',0)
      oProg.curHd = -1
      oProg.curZn = -1
      oProg.setNPT(TP.NPT_Targets_156[defaultTarget])
   
   #-------------------------------------------------------------------------------------------------------
   def ReduceReportInT109T126(self):
      import types
      # Change CWORD to reduce report to prevent result file storage in disc full
      if type(TP.prm_AFS_2T_Write_109['CWORD1']) in [types.ListType,types.TupleType]:
         TP.prm_AFS_2T_Write_109['CWORD1'] = TP.prm_AFS_2T_Write_109['CWORD1'][0]
      if type(TP.prm_AFS_CM_Read_109['CWORD1']) in [types.ListType,types.TupleType]:
         TP.prm_AFS_CM_Read_109['CWORD1'] = TP.prm_AFS_CM_Read_109['CWORD1'][0]
      TP.prm_AFS_2T_Write_109['CWORD1'] &= 0xFF8E
      TP.prm_AFS_CM_Read_109['CWORD1'] &= 0xFF8E
   
      if testSwitch.FE_0145589_345963_P_T126_DISABLE_DEBUG_MESSAGE:
         if type(TP.svoFlawPrm_126['CWORD1']) in [types.ListType,types.TupleType]:
            TP.svoFlawPrm_126['CWORD1'] = TP.svoFlawPrm_126['CWORD1'][0]
         TP.svoFlawPrm_126['CWORD1'] &= 0x3FFF
   
   #-------------------------------------------------------------------------------------------------------
   def MarvelAdaptiveThresholdTuning(self):
      inPrm = TP.prm_ATAFS_395.copy()
      #=== T395: Test time reduction for waterfall drive
      # (a) Disable T109 fine-tune threshold.
      # (b) Disable T395 threshold averaging
      # (c) Change T395 SLOPE from 180 to 200.
      if testSwitch.FLAWSCAN_ADAPT_THRES_TTR_FOR_WTF:
         objMsg.printMsg("T395 TTR: CAPACITY_PER_HEAD = %.2f, NATIVE_CAP_PER_HEAD = %.2f" %(TP.CAPACITY_PER_HEAD, TP.NATIVE_CAP_PER_HEAD))
         if TP.CAPACITY_PER_HEAD < TP.NATIVE_CAP_PER_HEAD:
            testSwitch.ENABLE_T109_FINE_TUNE_THRESHOLD = 0
            inPrm["prm_name"] = "prm_ATAFS_395_WTF"
            inPrm["CWORD1"] = inPrm["CWORD1"] | TP.T395_CW1_SKIP_AVERAGING # SKIP_AVERAGING = 0x0020
            inPrm["SLOPE_LIMIT"] = TP.T395_SLOPE_LIMIT_WTF
      self.oUserFlaw.St(inPrm)
   
   #-------------------------------------------------------------------------------------------------------
   def TaThresholdTuning(self):
      objMsg.printMsg("Starting DETCR")
      objMsg.printMsg("mfr = %s" % self.dut.PREAMP_MFR)
      T186prm={}
      T186prm.update(TP.prm_186_0001)
      if self.dut.HGA_SUPPLIER == 'RHO':
         if str(self.dut.PREAMP_MFR).find("TI")!= -1:
            T186prm["INPUT_VOLTAGE"]=(230,)
         else:
            T186prm["INPUT_VOLTAGE"]=(230,)
      elif self.dut.HGA_SUPPLIER in ['TDK', 'HWY']:
         T186prm["INPUT_VOLTAGE"]=(230,)
      else:
         ScrCmds.raiseException(11044, "Preamp info N/A to set T186 Input voltage")
      if testSwitch.FE_228371_DETCR_TA_SERVO_CODE_SUPPORTED:  # servo code not support yet
          self.oUserFlaw.St(T186prm)  # temproily off as symbol address of gain,bias not defined, use manual set value
      if not testSwitch.WA_DETCRTA_NOT_CONNECT_SOC:
         if testSwitch.FE_0139634_399481_P_DETCR_T134_T94_CHANGES and testSwitch.extern.FE_0134663_006800_T094_DETCR_CAL_REV2:
            self.oUserFlaw.St(TP.prm_094_0003)
         else:
            if testSwitch.FE_0280534_480505_DETCR_ON_OFF_BECAUSE_SERVO_DISABLE_DETCR_BY_DEFAULT:
               # needed due to M10P servo code, servo code disables DETCR by default so DETCR on/off commands need to be called before and after using DETCR
               self.oUserFlaw.St(TP.setDetcrOnPrm_011)
               self.oUserFlaw.St({'test_num':178, 'prm_name':'Save SAP in RAM to FLASH', 'CWORD1':0x420})
            if testSwitch.FE_228371_DETCR_TA_SERVO_CODE_SUPPORTED: 
               self.oUserFlaw.St(TP.prm_094_0002)

            if testSwitch.FE_0280534_480505_DETCR_ON_OFF_BECAUSE_SERVO_DISABLE_DETCR_BY_DEFAULT:
               # needed due to M10P servo code, servo code disables DETCR by default so DETCR on/off commands need to be called before and after using DETCR
               self.oUserFlaw.St(TP.setDetcrOffPrm_011)
               self.oUserFlaw.St({'test_num':178, 'prm_name':'Save SAP in RAM to FLASH', 'CWORD1':0x420})
      objMsg.printMsg("End of DETCR")
   
   #-------------------------------------------------------------------------------------------------------
   def SeparateOdOddEvenFlawscan(self):
      objMsg.printMsg("Starting OD flawscan")
      if not testSwitch.ZFS:
         self.oServoFlaw.servoFlawScan(TP.svoFlawPrm_126,SeekType.writeSeek) #126 write
         self.evenOddFlawScan(TP.prm_AFS_2T_Write_OD_109, 'even') #109 write even
      for wrtPass in range(TP.numWritePasses):
         if not testSwitch.ZFS:
            self.evenOddFlawScan(TP.prm_AFS_2T_Write_OD_109, 'odd') #109 write odd
      self.oServoFlaw.servoFlawScan(TP.svoFlawPrm_126,SeekType.readSeek) #126 read
      self.evenOddFlawScan(TP.prm_AFS_CM_Read_OD_109, 'even') #109 read even
      if not testSwitch.ZFS:
         self.oServoFlaw.servoFlawScan(TP.svoFlawPrm_126,SeekType.writeSeek) #126 write
      for wrtPass in range(TP.numWritePasses):
         if not testSwitch.ZFS:
            self.evenOddFlawScan(TP.prm_AFS_2T_Write_OD_109, 'even') #109 write even
      self.oServoFlaw.servoFlawScan(TP.svoFlawPrm_126,SeekType.readSeek) #126 read
      self.evenOddFlawScan(TP.prm_AFS_CM_Read_OD_109, 'odd') #109 read odd
      objMsg.printMsg("OD flawscan finished")
   
   #-------------------------------------------------------------------------------------------------------
   def EvenOddFlawscan(self):
      if not testSwitch.ZFS:
         self.oServoFlaw.servoFlawScan(TP.svoFlawPrm_126,SeekType.writeSeek) #126 write
      if testSwitch.FE_0123768_426568_OUTPUT_SERVO_COUNTERS_DURING_FLAWSCAN:
         self.oSvoScrn.clearServoErrCntrs()   # Clear servo error counters
      if not testSwitch.ZFS:
         self.evenOddFlawScan(TP.prm_AFS_2T_Write_109, 'even') #109 write even
      if testSwitch.FE_0123768_426568_OUTPUT_SERVO_COUNTERS_DURING_FLAWSCAN:
         self.oSvoScrn.dumpServoErrCntrs(spcId=1091)  # Dump servo error counters
         self.oSvoScrn.clearServoErrCntrs()   # Clear servo error counters
      if not testSwitch.ZFS:
         self.evenOddFlawScan(TP.prm_AFS_2T_Write_109, 'odd') #109 write odd
      if testSwitch.FE_0123768_426568_OUTPUT_SERVO_COUNTERS_DURING_FLAWSCAN:
         self.oSvoScrn.dumpServoErrCntrs(spcId=1092)  # Dump servo error counters
      if testSwitch.GA_0115920_357915_REPORT_SERVO_FLAW_TABLE_BETWEEN_READ_AND_WRITE_SCANS:
         self.oUserFlaw.St(TP.prm_126_read_sft_oracle) #report servo flaw table
   
      self.oServoFlaw.servoFlawScan(TP.svoFlawPrm_126,SeekType.readSeek) #126 read
      if testSwitch.FE_0126442_357552_OUTPUT_SERVO_COUNTERS_AFTER_FLAWSCAN_READPASS:
         self.oSvoScrn.clearServoErrCntrs()   # Clear servo error counters
      if testSwitch.FE_0138445_336764_P_AUTO_RETEST_T109_FROM_EC11231_EC11049:
         try:
            self.evenOddFlawScan(TP.prm_AFS_CM_Read_109, 'even') #109 read even
         except ScriptTestFailure, (failureData):
            if failureData[0][2] in [11049,11231]:
               objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
               self.oServoFlaw.servoFlawScan(TP.svoFlawPrm_126,SeekType.readSeek) #126 read
               self.evenOddFlawScan(TP.prm_AFS_CM_Read_109, 'even') #109 read even
            else:
               raise
      else:
         self.evenOddFlawScan(TP.prm_AFS_CM_Read_109, 'even') #109 read even
      if testSwitch.FE_0126442_357552_OUTPUT_SERVO_COUNTERS_AFTER_FLAWSCAN_READPASS:
         self.oSvoScrn.dumpServoErrCntrs(spcId=1093)  # Dump servo error counters
      if testSwitch.GA_0115920_357915_REPORT_SERVO_FLAW_TABLE_BETWEEN_READ_AND_WRITE_SCANS:
         self.oUserFlaw.St(TP.prm_126_read_sft_oracle) #report servo flaw table
   
      if not testSwitch.ZFS:
         self.oServoFlaw.servoFlawScan(TP.svoFlawPrm_126,SeekType.writeSeek) #126 write
      if testSwitch.FE_0123768_426568_OUTPUT_SERVO_COUNTERS_DURING_FLAWSCAN:
         self.oSvoScrn.clearServoErrCntrs()   # Clear servo error counters
      if not testSwitch.ZFS:
         self.evenOddFlawScan(TP.prm_AFS_2T_Write_109, 'even') #109 write even
      if testSwitch.FE_0123768_426568_OUTPUT_SERVO_COUNTERS_DURING_FLAWSCAN:
         self.oSvoScrn.dumpServoErrCntrs(spcId=1094)  # Dump servo error counters
      if testSwitch.GA_0115920_357915_REPORT_SERVO_FLAW_TABLE_BETWEEN_READ_AND_WRITE_SCANS:
         self.oUserFlaw.St(TP.prm_126_read_sft_oracle) #report servo flaw table
   
      self.oServoFlaw.servoFlawScan(TP.svoFlawPrm_126,SeekType.readSeek) #126 read
      if testSwitch.FE_0126442_357552_OUTPUT_SERVO_COUNTERS_AFTER_FLAWSCAN_READPASS:
         self.oSvoScrn.clearServoErrCntrs()   # Clear servo error counters
      if testSwitch.FE_0138445_336764_P_AUTO_RETEST_T109_FROM_EC11231_EC11049:
         try:
            self.evenOddFlawScan(TP.prm_AFS_CM_Read_109, 'odd') #109 read odd
         except ScriptTestFailure, (failureData):
            if failureData[0][2] in [11049,11231]:
               objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
               self.oServoFlaw.servoFlawScan(TP.svoFlawPrm_126,SeekType.readSeek) #126 read
               self.evenOddFlawScan(TP.prm_AFS_CM_Read_109, 'odd') #109 read odd
            else:
               raise
      else:
         self.evenOddFlawScan(TP.prm_AFS_CM_Read_109, 'odd') #109 read odd
      if testSwitch.FE_0126442_357552_OUTPUT_SERVO_COUNTERS_AFTER_FLAWSCAN_READPASS:
         self.oSvoScrn.dumpServoErrCntrs(spcId=1095)  # Dump servo error counters
      # MSE scan even - scan top written tracks
      if testSwitch.FE_0118875_006800_RUN_T109_MSE_SCAN:
         if testSwitch.FE_0138445_336764_P_AUTO_RETEST_T109_FROM_EC11231_EC11049:
            try:
               self.T109MSEScan(TP.prm_MSE_Scan_109, 800, 0x0101, 'even')
            except ScriptTestFailure, (failureData):
               if failureData[0][2] in [11049,11231]:
                  objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
                  self.T109MSEScan(TP.prm_MSE_Scan_109, 800, 0x0101, 'even')
               else:
                  raise
         else:
            self.T109MSEScan(TP.prm_MSE_Scan_109, 800, 0x0101, 'even')
   
   #-------------------------------------------------------------------------------------------------------
   def EoWrtEoRdFlawscan(self):
      if not testSwitch.ZFS:
         self.oServoFlaw.servoFlawScan(TP.svoFlawPrm_126,SeekType.writeSeek) #126 write
      if testSwitch.FE_0123768_426568_OUTPUT_SERVO_COUNTERS_DURING_FLAWSCAN:
         self.oSvoScrn.clearServoErrCntrs()   # Clear servo error counters
      if not testSwitch.ZFS:
         self.evenOddFlawScan(TP.prm_AFS_2T_Write_109, 'even') #109 write even
      if testSwitch.FE_0123768_426568_OUTPUT_SERVO_COUNTERS_DURING_FLAWSCAN:
         self.oSvoScrn.dumpServoErrCntrs(spcId=1091)  # Dump servo error counters
         self.oSvoScrn.clearServoErrCntrs()   # Clear servo error counters
      if not testSwitch.ZFS:
         self.evenOddFlawScan(TP.prm_AFS_2T_Write_109, 'odd') #109 write odd
      if testSwitch.FE_0123768_426568_OUTPUT_SERVO_COUNTERS_DURING_FLAWSCAN:
         self.oSvoScrn.dumpServoErrCntrs(spcId=1092)  # Dump servo error counters
      if testSwitch.GA_0115920_357915_REPORT_SERVO_FLAW_TABLE_BETWEEN_READ_AND_WRITE_SCANS:
         self.oUserFlaw.St(TP.prm_126_read_sft_oracle) #report servo flaw table
   
      self.oServoFlaw.servoFlawScan(TP.svoFlawPrm_126,SeekType.readSeek) #126 read
      if testSwitch.FE_0126442_357552_OUTPUT_SERVO_COUNTERS_AFTER_FLAWSCAN_READPASS:
         self.oSvoScrn.clearServoErrCntrs()   # Clear servo error counters
      self.evenOddFlawScan(TP.prm_AFS_CM_Read_109, 'even') #109 read even
      if testSwitch.FE_0126442_357552_OUTPUT_SERVO_COUNTERS_AFTER_FLAWSCAN_READPASS:
         self.oSvoScrn.dumpServoErrCntrs(spcId=1093)  # Dump servo error counters
      if testSwitch.GA_0115920_357915_REPORT_SERVO_FLAW_TABLE_BETWEEN_READ_AND_WRITE_SCANS:
         self.oUserFlaw.St(TP.prm_126_read_sft_oracle) #report servo flaw table
   
      self.oServoFlaw.servoFlawScan(TP.svoFlawPrm_126,SeekType.readSeek) #126 read
      self.evenOddFlawScan(TP.prm_AFS_CM_Read_109, 'odd') #109 read odd
      if testSwitch.FE_0126442_357552_OUTPUT_SERVO_COUNTERS_AFTER_FLAWSCAN_READPASS:
         self.oSvoScrn.dumpServoErrCntrs(spcId=1095)  # Dump servo error counters
      # MSE scan - top written tracks even or odd doesn't matter
      if testSwitch.FE_0118875_006800_RUN_T109_MSE_SCAN:
         self.T109MSEScan(TP.prm_MSE_Scan_109, 800, 0x0101, 'even')

   #-------------------------------------------------------------------------------------------------------
   def FullWrtEoRdFlawscan(self):
      if not testSwitch.ZFS:
         self.oServoFlaw.servoFlawScan(TP.svoFlawPrm_126,SeekType.writeSeek) #126 write
      if testSwitch.FE_0123768_426568_OUTPUT_SERVO_COUNTERS_DURING_FLAWSCAN:
         self.oSvoScrn.clearServoErrCntrs()   # Clear servo error counters
      if not testSwitch.ZFS:
         self.oUserFlaw.St(TP.prm_AFS_2T_Write_109) # full write pass
      if testSwitch.FE_0123768_426568_OUTPUT_SERVO_COUNTERS_DURING_FLAWSCAN:
         self.oSvoScrn.dumpServoErrCntrs(spcId=1091)  # Dump servo error counters
      if testSwitch.GA_0115920_357915_REPORT_SERVO_FLAW_TABLE_BETWEEN_READ_AND_WRITE_SCANS:
         self.oUserFlaw.St(TP.prm_126_read_sft_oracle) #report servo flaw table
   
      self.oServoFlaw.servoFlawScan(TP.svoFlawPrm_126,SeekType.readSeek) #126 read
      if testSwitch.FE_0126442_357552_OUTPUT_SERVO_COUNTERS_AFTER_FLAWSCAN_READPASS:
         self.oSvoScrn.clearServoErrCntrs()   # Clear servo error counters
      self.evenOddFlawScan(TP.prm_AFS_CM_Read_109, 'even') #109 read even
      if testSwitch.FE_0126442_357552_OUTPUT_SERVO_COUNTERS_AFTER_FLAWSCAN_READPASS:
         self.oSvoScrn.dumpServoErrCntrs(spcId=1093)  # Dump servo error counters
         self.oSvoScrn.clearServoErrCntrs()   # Clear servo error counters
   
      self.oServoFlaw.servoFlawScan(TP.svoFlawPrm_126,SeekType.readSeek) #126 read
      self.evenOddFlawScan(TP.prm_AFS_CM_Read_109, 'odd') #109 read odd
      if testSwitch.FE_0126442_357552_OUTPUT_SERVO_COUNTERS_AFTER_FLAWSCAN_READPASS:
         self.oSvoScrn.dumpServoErrCntrs(spcId=1095)  # Dump servo error counters
      # MSE scan - top written tracks even or odd doesn't matter
      if testSwitch.FE_0118875_006800_RUN_T109_MSE_SCAN:
         self.T109MSEScan(TP.prm_MSE_Scan_109, 800, 0x0101, 'even')
   
   #-------------------------------------------------------------------------------------------------------
   def EoWrtFullRdFlawscan(self):
      if not testSwitch.ZFS:
         self.oServoFlaw.servoFlawScan(TP.svoFlawPrm_126,SeekType.writeSeek) #126 write
      if testSwitch.FE_0123768_426568_OUTPUT_SERVO_COUNTERS_DURING_FLAWSCAN:
         self.oSvoScrn.clearServoErrCntrs()   # Clear servo error counters
      if not testSwitch.ZFS:
         self.evenOddFlawScan(TP.prm_AFS_2T_Write_109, 'even') #109 write even
         self.evenOddFlawScan(TP.prm_AFS_2T_Write_109, 'odd') #109 write odd
      if testSwitch.FE_0123768_426568_OUTPUT_SERVO_COUNTERS_DURING_FLAWSCAN:
         self.oSvoScrn.dumpServoErrCntrs(spcId=1091)  # Dump servo error counters
      if testSwitch.GA_0115920_357915_REPORT_SERVO_FLAW_TABLE_BETWEEN_READ_AND_WRITE_SCANS:
         self.oUserFlaw.St(TP.prm_126_read_sft_oracle) #report servo flaw table
   
      self.oServoFlaw.servoFlawScan(TP.svoFlawPrm_126,SeekType.readSeek) #126 read
      if testSwitch.FE_0126442_357552_OUTPUT_SERVO_COUNTERS_AFTER_FLAWSCAN_READPASS:
         self.oSvoScrn.clearServoErrCntrs()   # Clear servo error counters
      self.oUserFlaw.St(TP.prm_AFS_CM_Read_109) #109 full read
      if testSwitch.FE_0126442_357552_OUTPUT_SERVO_COUNTERS_AFTER_FLAWSCAN_READPASS:
         self.oSvoScrn.dumpServoErrCntrs(spcId=1093)  # Dump servo error counters
      # MSE scan odd - scan top written tracks
      if testSwitch.FE_0118875_006800_RUN_T109_MSE_SCAN:
         self.T109MSEScan(TP.prm_MSE_Scan_109, 800, 0x0101, 'odd')
   
   #-------------------------------------------------------------------------------------------------------
   def SeqFullWrtFullRdFlawscan(self):
      #=== Sequential write
      if not testSwitch.ZFS:
         self.oServoFlaw.servoFlawScan(TP.svoFlawPrm_126,SeekType.writeSeek)
      if testSwitch.FE_0123768_426568_OUTPUT_SERVO_COUNTERS_DURING_FLAWSCAN:
         self.oSvoScrn.clearServoErrCntrs()   # Clear servo error counters
      if not testSwitch.ZFS:
         self.oUserFlaw.St(TP.prm_AFS_2T_Write_109) # analog flawscan write pass
      if testSwitch.FE_0123768_426568_OUTPUT_SERVO_COUNTERS_DURING_FLAWSCAN:
         self.oSvoScrn.dumpServoErrCntrs(spcId=1091)  # Dump servo error counters
      if testSwitch.GA_0115920_357915_REPORT_SERVO_FLAW_TABLE_BETWEEN_READ_AND_WRITE_SCANS:
         self.oUserFlaw.St(TP.prm_126_read_sft_oracle) #report servo flaw table
      #=== Threshold Tuning
      if testSwitch.FE_0168920_322482_ADAPTIVE_THRESHOLD_FLAWSCAN_LSI:
         # Init and display AFS threshold by head by zone
         self.oUserFlaw.St(TP.PRM_INIT_AFS_THRESHOLD_355)
         self.oUserFlaw.St(TP.PRM_DISPLAY_AFS_THRESHOLD_355)
         # Tune SLIM and UMP tracks thresholds.
         self.oServoFlaw.servoFlawScan(TP.svoFlawPrm_126,SeekType.readSeek)
         self.oUserFlaw.St(TP.PRM_TUNE_SLIM_UMP_AFS_THRESHOLD_109)
         if testSwitch.FE_0000000_348432_AFS_SYNC_UP_AFS_THRESHOLD:
            # Same threshold for SLIM track and FAT track.
            self.oUserFlaw.St(TP.PRM_SYNCUP_AFS_THRESHOLD_355)
         else:
            # Tune FAT track threshold. Different threshold for SLIM track and FAT track.
            self.oUserFlaw.St(TP.PRM_TUNE_FAT_AFS_THRESHOLD_109)
         # Display threshold table
         self.oUserFlaw.St(TP.PRM_DISPLAY_AFS_THRESHOLD_355_2)
      #=== Sequential read
      self.oServoFlaw.servoFlawScan(TP.svoFlawPrm_126,SeekType.readSeek)
      if testSwitch.FE_0126442_357552_OUTPUT_SERVO_COUNTERS_AFTER_FLAWSCAN_READPASS:
         self.oSvoScrn.clearServoErrCntrs()   # Clear servo error counters
      self.oUserFlaw.St(TP.prm_AFS_CM_Read_109) # analog flawscan read pass
      if testSwitch.FE_0126442_357552_OUTPUT_SERVO_COUNTERS_AFTER_FLAWSCAN_READPASS:
         self.oSvoScrn.dumpServoErrCntrs(spcId=1093)  # Dump servo error counters
      #=== MSE scan - top written tracks even or odd doesn't matter
      if testSwitch.FE_0118875_006800_RUN_T109_MSE_SCAN:
         self.T109MSEScan(TP.prm_MSE_Scan_109, 800, 0x0101, 'even')

   #-------------------------------------------------------------------------------------------------------
   def ShingledUmpFlawscan(self):

      if testSwitch.FE_0241396_505235_FLAWSCAN_POWER_LOSS_RECOVERY:
         lastPoint, count = self.checkpoint.getLast(self.dut)
      else:
         lastPoint = None
         
      #=== Write
      self.oServoFlaw.servoFlawScan(TP.svoFlawPrm_126,SeekType.writeSeek)
      if testSwitch.FE_0241396_505235_FLAWSCAN_POWER_LOSS_RECOVERY:
         self.DoForEachHead(self.evenOddFlawScan, {'inPrm': TP.PRM_WRITE_UMP_ZONES_109.copy(), 'mode': 'even'}, lastPoint, count)
         self.DoForEachHead(self.evenOddFlawScan, {'inPrm': TP.PRM_WRITE_UMP_ZONES_109.copy(), 'mode': 'odd'}, lastPoint, count)
         self.DoForEachHead(self.evenOddFlawScan, {'inPrm': TP.PRM_WRITE_SHL_ZONES_109.copy(), 'mode': 'all'}, lastPoint, count)
      else:
         self.evenOddFlawScan(TP.PRM_WRITE_UMP_ZONES_109, 'even')
         self.evenOddFlawScan(TP.PRM_WRITE_UMP_ZONES_109, 'odd')
         self.evenOddFlawScan(TP.PRM_WRITE_SHL_ZONES_109, 'all')

      #=== Threshold Tuning
      if testSwitch.FE_0168920_322482_ADAPTIVE_THRESHOLD_FLAWSCAN_LSI:
         self.GetExecution(lastPoint, self.FlawscanThresholdTuning)

      #=== Read
      if testSwitch.FE_0234376_229876_T109_READ_ZFS:
         import SdatParameters
         self.oUserFlaw.St(SdatParameters.zapPrm_RdzapOff)
      self.oServoFlaw.servoFlawScan(TP.svoFlawPrm_126,SeekType.readSeek)
      if testSwitch.FE_0241396_505235_FLAWSCAN_POWER_LOSS_RECOVERY:
         self.DoForEachHead(self.evenOddFlawScan, {'inPrm': TP.PRM_READ_SHL_ZONES_109.copy(), 'mode': 'all'}, lastPoint, count)
         self.DoForEachHead(self.evenOddFlawScan, {'inPrm': TP.PRM_READ_UMP_ZONES_109.copy(), 'mode': 'even'}, lastPoint, count)
      else:
         self.evenOddFlawScan(TP.PRM_READ_SHL_ZONES_109, 'all')
         self.evenOddFlawScan(TP.PRM_READ_UMP_ZONES_109, 'even')

      #=== UMP zones: Write even -> Read odd
      if testSwitch.FE_0234376_229876_T109_READ_ZFS:
         self.oUserFlaw.St(SdatParameters.zapPrm_RdzapOn)      
      self.oServoFlaw.servoFlawScan(TP.svoFlawPrm_126,SeekType.writeSeek)
      if testSwitch.FE_0241396_505235_FLAWSCAN_POWER_LOSS_RECOVERY:
         self.DoForEachHead(self.evenOddFlawScan, {'inPrm': TP.PRM_WRITE_UMP_ZONES_109.copy(), 'mode': 'even'}, lastPoint, count)
      else:
         self.evenOddFlawScan(TP.PRM_WRITE_UMP_ZONES_109, 'even')

      if testSwitch.FE_0234376_229876_T109_READ_ZFS:
         self.oUserFlaw.St(SdatParameters.zapPrm_RdzapOff)
      self.oServoFlaw.servoFlawScan(TP.svoFlawPrm_126,SeekType.readSeek)
      if testSwitch.FE_0241396_505235_FLAWSCAN_POWER_LOSS_RECOVERY:
         self.DoForEachHead(self.evenOddFlawScan, {'inPrm': TP.PRM_READ_UMP_ZONES_109.copy(), 'mode': 'odd'}, lastPoint, count)
      else:
         self.evenOddFlawScan(TP.PRM_READ_UMP_ZONES_109, 'odd')

      if testSwitch.FE_0234376_229876_T109_READ_ZFS:
         self.oUserFlaw.St(SdatParameters.zapPrm_RdzapOn)

   #-------------------------------------------------------------------------------------------------------
   def FlawscanThresholdTuning(self):

      if testSwitch.FE_0241396_505235_FLAWSCAN_POWER_LOSS_RECOVERY:
         lastPoint, count = self.checkpoint.getLast(self.dut)
      else:
         lastPoint = None
         
      #=== Init and display AFS threshold by head by zone
      self.oUserFlaw.St(TP.PRM_INIT_AFS_THRESHOLD_355)

      #=== Tune SLIM and UMP tracks thresholds.
      self.oServoFlaw.servoFlawScan(TP.svoFlawPrm_126,SeekType.readSeek)
      self.oUserFlaw.St(TP.PRM_TUNE_SLIM_UMP_AFS_THRESHOLD_109)

      if testSwitch.FE_0000000_348432_AFS_SYNC_UP_AFS_THRESHOLD:
         #=== Same threshold for SLIM track and FAT track.
         self.oUserFlaw.St(TP.PRM_SYNCUP_AFS_THRESHOLD_355)
      else:
         #=== Tune FAT track threshold. Different threshold for SLIM track and FAT track.
         self.oUserFlaw.St(TP.PRM_TUNE_FAT_AFS_THRESHOLD_109)

      #=== Display threshold table
      self.oUserFlaw.St(TP.PRM_DISPLAY_AFS_THRESHOLD_355_2)

   #-------------------------------------------------------------------------------------------------------
   def AuditTest_EvenOddFlawscan(self):
      if not testSwitch.ZFS:
         self.auditTestServoFlawscan(TP.svoFlawPrm_126,SeekType.writeSeek) #126 wr sk
         self.auditTestUserFlawscan(TP.prm_AFS_2T_Write_109,'even')  #109 wr even
         self.auditTestUserFlawscan(TP.prm_AFS_2T_Write_109,'odd')  #109 wr odd
      if testSwitch.GA_0115920_357915_REPORT_SERVO_FLAW_TABLE_BETWEEN_READ_AND_WRITE_SCANS:
         self.oUserFlaw.St(TP.prm_126_read_sft_oracle) #report servo flaw table
      self.auditTestServoFlawscan(TP.svoFlawPrm_126,SeekType.readSeek) #126 read sk
      self.auditTestUserFlawscan(TP.prm_AFS_CM_Read_109,'even') #109 rd even
      if testSwitch.GA_0115920_357915_REPORT_SERVO_FLAW_TABLE_BETWEEN_READ_AND_WRITE_SCANS:
         self.oUserFlaw.St(TP.prm_126_read_sft_oracle) #report servo flaw table
      if not testSwitch.ZFS:
         self.auditTestServoFlawscan(TP.svoFlawPrm_126,SeekType.writeSeek) #126 wr sk
         self.auditTestUserFlawscan(TP.prm_AFS_2T_Write_109,'even')  #109 wr even
      if testSwitch.GA_0115920_357915_REPORT_SERVO_FLAW_TABLE_BETWEEN_READ_AND_WRITE_SCANS:
         self.oUserFlaw.St(TP.prm_126_read_sft_oracle) #report servo flaw table
      self.auditTestServoFlawscan(TP.svoFlawPrm_126,SeekType.readSeek) #126 read sk
      self.auditTestUserFlawscan(TP.prm_AFS_CM_Read_109,'odd') #109 rd odd
   
   #-------------------------------------------------------------------------------------------------------
   def AuditTest_FullWrEoRdFlawscan(self):
      if not testSwitch.ZFS:
         self.auditTestServoFlawscan(TP.svoFlawPrm_126,SeekType.writeSeek)
         self.auditTestUserFlawscan(TP.prm_AFS_2T_Write_109) # full write pass
      if testSwitch.GA_0115920_357915_REPORT_SERVO_FLAW_TABLE_BETWEEN_READ_AND_WRITE_SCANS:
         self.oUserFlaw.St(TP.prm_126_read_sft_oracle) #report servo flaw table
      self.auditTestUserFlawscan(TP.prm_AFS_CM_Read_109,'even') #109 rd even
      self.auditTestServoFlawscan(TP.svoFlawPrm_126,SeekType.readSeek) #126 read sk
      self.auditTestUserFlawscan(TP.prm_AFS_CM_Read_109,'odd') #109 rd odd
   
   #-------------------------------------------------------------------------------------------------------
   def AuditTest_EoWrtFullRdFlawscan(self):
      if not testSwitch.ZFS:
         self.auditTestServoFlawscan(TP.svoFlawPrm_126,SeekType.writeSeek) #126 write
         self.auditTestUserFlawscan(TP.prm_AFS_2T_Write_109, 'even') #109 write even
         self.auditTestUserFlawscan(TP.prm_AFS_2T_Write_109, 'odd') #109 write odd
      if testSwitch.GA_0115920_357915_REPORT_SERVO_FLAW_TABLE_BETWEEN_READ_AND_WRITE_SCANS:
         self.oUserFlaw.St(TP.prm_126_read_sft_oracle) #report servo flaw table
      self.auditTestServoFlawscan(TP.svoFlawPrm_126,SeekType.readSeek) #126 read
      self.auditTestUserFlawscan(TP.prm_AFS_CM_Read_109) #109 full read
   
   #-------------------------------------------------------------------------------------------------------
   def AuditTest_SeqFullWrtFullRdFlawscan(self):
      if not testSwitch.ZFS:
         self.auditTestServoFlawscan(TP.svoFlawPrm_126,SeekType.writeSeek)
         self.auditTestUserFlawscan(TP.prm_AFS_2T_Write_109) # analog flawscan write pass
      if testSwitch.GA_0115920_357915_REPORT_SERVO_FLAW_TABLE_BETWEEN_READ_AND_WRITE_SCANS:
         self.oUserFlaw.St(TP.prm_126_read_sft_oracle) #report servo flaw table
      self.auditTestServoFlawscan(TP.svoFlawPrm_126,SeekType.readSeek)
      self.auditTestUserFlawscan(TP.prm_AFS_CM_Read_109) # analog flawscan read pass
   
   #-------------------------------------------------------------------------------------------------------
   def FullInterlaceFlawscan(self):
      if testSwitch.FE_0241396_505235_FLAWSCAN_POWER_LOSS_RECOVERY:
         lastPoint, count = self.checkpoint.getLast(self.dut)
      else:
         lastPoint = None

      #=== Init self.thresInfo
      self.CreateThresInfoData()

      #=== Full interlace flaw scan
      objMsg.printMsg("###=== Full Interlace Flawscan ===###")
      try:
         #=== Write even & odd
         self.oServoFlaw.servoFlawScan(TP.svoFlawPrm_126, SeekType.writeSeek)
         if testSwitch.FE_0241396_505235_FLAWSCAN_POWER_LOSS_RECOVERY:
            self.DoForEachHead(self.evenOddFlawScan, {'inPrm': TP.prm_AFS_2T_Write_109.copy(), 'mode': 'even'}, lastPoint, count)
            self.DoForEachHead(self.evenOddFlawScan, {'inPrm': TP.prm_AFS_2T_Write_109.copy(), 'mode': 'odd'}, lastPoint, count)
         else:
            self.evenOddFlawScan(TP.prm_AFS_2T_Write_109, 'even')
            self.evenOddFlawScan(TP.prm_AFS_2T_Write_109, 'odd')

         execTest, point = self.GetExecutionOption(lastPoint)

         #=== MVL Fine-tune AFS threshold
         if execTest and testSwitch.ENABLE_T109_FINE_TUNE_THRESHOLD:
            self.oServoFlaw.servoFlawScan(TP.svoFlawPrm_126, SeekType.readSeek)
            self.evenOddFlawScan(TP.prm_Fine_Tune_Threshold_109, 'even')
            self.GetVgarAndThres()
            if execTest > 1:
               self.checkpoint.save(self.dut, point)
         #objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=3, onTime=3, useESlip=1)

         #=== LSI Threshold Tuning
         if execTest and testSwitch.FE_0168920_322482_ADAPTIVE_THRESHOLD_FLAWSCAN_LSI:
            # Init and display AFS threshold by head by zone
            self.oUserFlaw.St(TP.PRM_INIT_AFS_THRESHOLD_355)
            self.oUserFlaw.St(TP.PRM_DISPLAY_AFS_THRESHOLD_355)
            # Tune SLIM and UMP tracks thresholds.
            self.oServoFlaw.servoFlawScan(TP.svoFlawPrm_126,SeekType.readSeek)
            self.evenOddFlawScan(TP.PRM_TUNE_SLIM_UMP_AFS_THRESHOLD_109, 'even')
            self.oUserFlaw.St(TP.PRM_SYNCUP_AFS_THRESHOLD_355)
            # Display threshold table
            self.oUserFlaw.St(TP.PRM_DISPLAY_AFS_THRESHOLD_355_2)
            if execTest > 1:
               self.checkpoint.save(self.dut, point)

         #=== Read even
         self.oServoFlaw.servoFlawScan(TP.svoFlawPrm_126,SeekType.readSeek)
         if testSwitch.FE_0241396_505235_FLAWSCAN_POWER_LOSS_RECOVERY:
            self.DoForEachHead(self.evenOddFlawScan, {'inPrm': TP.prm_AFS_CM_Read_109.copy(), 'mode': 'even'}, lastPoint, count)
         else:
            self.evenOddFlawScan(TP.prm_AFS_CM_Read_109, 'even')
         #=== Write even
         self.oServoFlaw.servoFlawScan(TP.svoFlawPrm_126, SeekType.writeSeek)
         if testSwitch.FE_0241396_505235_FLAWSCAN_POWER_LOSS_RECOVERY:
            self.DoForEachHead(self.evenOddFlawScan, {'inPrm': TP.prm_AFS_2T_Write_109.copy(), 'mode': 'even'}, lastPoint, count)
         else:
            self.evenOddFlawScan(TP.prm_AFS_2T_Write_109, 'even')
         #=== Read odd
         self.oServoFlaw.servoFlawScan(TP.svoFlawPrm_126,SeekType.readSeek)
         if testSwitch.FE_0241396_505235_FLAWSCAN_POWER_LOSS_RECOVERY:
            self.DoForEachHead(self.evenOddFlawScan, {'inPrm': TP.prm_AFS_CM_Read_109.copy(), 'mode': 'odd'}, lastPoint, count)
         else:
            self.evenOddFlawScan(TP.prm_AFS_CM_Read_109, 'odd')
         self.getVerUnver()
         self.repThresInfo()
      except:
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
         self.getVerUnver()
         self.repThresInfo()
         raise

   #-------------------------------------------------------------------------------------------------------
   def GetExecutionOption(self, lastPoint):
      if not testSwitch.FE_0241396_505235_FLAWSCAN_POWER_LOSS_RECOVERY:
         execTest = 1       # normal execution
         point = None
      else:
         point = self.checkpoint.get(self.dut, -1)
         if not self.dut.powerLossEvent or (point > lastPoint):
            execTest = 2    # execution with checkpoint
         else:
            execTest = 0    # no execution

      return execTest, point

   #-------------------------------------------------------------------------------------------------------
   def SaveSList(self, lastPoint):
      validList = False
      # check status
      if (not testSwitch.FE_0241396_505235_FLAWSCAN_POWER_LOSS_RECOVERY):
         pass
      else:
         point = self.checkpoint.get(self.dut, -1)
         if not self.dut.powerLossEvent or (point > lastPoint):
            self.oUserFlaw.saveSListToPcFile()
            self.checkpoint.save(self.dut, point, -1)
         else:
            validList = True
            
      objMsg.printMsg("SaveSList validList: %x" % (validList))
      return validList

   #-------------------------------------------------------------------------------------------------------
   def GetExecution(self, lastPoint, func, param=None, validList=False):
      # check status
      if not testSwitch.FE_0241396_505235_FLAWSCAN_POWER_LOSS_RECOVERY:
         execTest = 1       # normal execution
      else:
         point = self.checkpoint.get(self.dut, -1)
         if not self.dut.powerLossEvent or (point > lastPoint):
            execTest = 2    # execution with checkpoint
         else:
            execTest = 0    # no execution
      # execution
      objMsg.printMsg("GetExecution validList: %x" % (validList))
      if execTest:
         if validList:
            self.oUserFlaw.restoreSListFromPcFile()
         if param:
            func(param)
         else:
            func()
      if execTest > 1:
         self.checkpoint.save(self.dut, point, -1)
         
      return execTest
      
   #-------------------------------------------------------------------------------------------------------
   def DoForEachHead(self, func, param, lastPoint, count):
      for hd in range(self.dut.imaxHead):
         point = self.checkpoint.get(self.dut, -1)
         if self.dut.powerLossEvent:
            if point < lastPoint:
               break
            elif (point == lastPoint) and (hd <= count-1):
               continue
         param["inPrm"]["HEAD_RANGE"] = (hd<<8) + hd
         func(**param)
         self.checkpoint.save(self.dut, point, -1)
