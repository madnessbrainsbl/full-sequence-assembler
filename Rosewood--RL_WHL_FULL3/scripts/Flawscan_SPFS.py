#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: base Serial Port calibration states
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/12/29 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Flawscan_SPFS.py $
# $Revision: #15 $
# $DateTime: 2016/12/29 22:40:52 $
# $Author: yihua.jiang $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Flawscan_SPFS.py#15 $
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
from Flawscan_ZAFS import CMiniZapAfs
import ScrCmds
from Servo import CServoFunc

###########################################################################################################
class CSinglePassFlawScan(CState):
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
      #=== Import libraries
      self.importLibraries()
      #=== Power loss recovery 
      if testSwitch.FE_0241396_505235_FLAWSCAN_POWER_LOSS_RECOVERY:
         self.checkpoint = Utility.executionState()
         lastPoint, count = self.checkpoint.getLast(self.dut)
      else:
         lastPoint = None
      #=== Add a powercycle to clear any memory issue from previous run.
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=5, onTime=5, useESlip=1)
      #=== Stress servo channel setting
      self.oSrvFunc.ChangeServoChannelSetting(0x0001)
      #=== Check HDA temperature
      self.hdstrProc = self.dut.HDSTR_PROC == 'Y'
      if 'S' in StateTable[self.dut.nextOper][self.dut.nextState][OPT]:
         self.oProcess.St(TP.hdstr_tempCheck)
      #=== Init flaw lists
      if not (testSwitch.M11P or testSwitch.M11P_BRING_UP or 'SPF_REZAP' in self.dut.statesExec[self.dut.nextOper]):
         self.GetExecution(lastPoint, self.initFlawLists)
      #=== Setup DETCR preamp
      if not testSwitch.FE_0153357_007955_P_USE_DETCR_PREAMP_SETUP_STATE: # Temporary: Disable T94
         self.GetExecution(lastPoint, self.SetupDetcrPreamp)
      try:         
         #=== UMP Analog Flaw Scan
         if not (testSwitch.M11P or testSwitch.M11P_BRING_UP):
            if self.dut.nextOper == 'STS':
                oMiniZapAfs = CMiniZapAfs(self.dut, self.params)
                oMiniZapAfs.run()
            else : 
                self.GetExecution(lastPoint, self.runUmpAnalogFlawScan)      
         if not self.dut.nextOper == 'STS':
             #=== Single Pass Flaw Scan
             self.GetExecution(lastPoint, self.runSinglePassFlawScan)
         #=== Power cycle badly needed here as some reminent register setup was effecting T134 and causing 0 TA's.
         objPwrCtrl.powerCycle(useESlip=1) 
         #=== Adjacent Servo Flaw Scan + Skipped Track Padding
         self.GetExecution(lastPoint, self.runAdjServoFlawScan)
      except ScriptTestFailure, (failureData):
         if testSwitch.FE_0365343_518226_SPF_REZAP_BY_HEAD and failureData[0][2] in [10463]: 
            flaws = self.dut.dblData.Tables('P126_SRVO_FLAW_HD').tableDataObj()[-self.dut.imaxHead:]
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
            self.dut.driveattr['SPF_CUR_HEAD'] = badHd1   
         raise      
      #=== TA Scan + 'Ujog' Padding
      self.GetExecution(lastPoint, self.runTAScan)
      #=== Build P-List from DBI and S-List
      self.GetExecution(lastPoint, self.buildPList, param = 1491)
      #==== AFS Beatup Test
      if testSwitch.ENABLE_FLAWSCAN_BEATUP:
         self.GetExecution(lastPoint, self.runFlawScanBeatup)
      #=== Parse DBI limits and Media Damage Screen
      self.GetExecution(lastPoint, self.oProcess.St, TP.prm_DBI_Fail_Limits_140)
      self.GetExecution(lastPoint, self.runMediaDamageScreen)
      #=== Scratch Fill
      self.GetExecution(lastPoint, self.runScratchFill)
      #=== Build Slip List
      self.oUserFlaw.writePListToSlipList(spcId = 2)
      #=== Report tables
      self.repFlawLists()
      #=== Restore servo channel setting
      self.oSrvFunc.ChangeServoChannelSetting(0x0000)
      #=== 
      self.dut.driveattr['FLAW_SCAN_TESTED'] = 1
      if self.hdstrProc:
         objMsg.printMsg("Finish D_FLAW in HDSTR testing...")
         self.oProcess.St(TP.hdstr_tempCheck)
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
   def importLibraries(self):
      self.oSeekType = SeekType
      self.oProcess = CProcess()
      self.oUserFlaw = CUserFlaw()
      self.oServoFlaw = CServoFlaw()
      self.oSrvFunc = CServoFunc()

   #-------------------------------------------------------------------------------------------------------
   def initFlawLists(self):
      PrevFailState = DriveAttributes.get('FAIL_STATE', '')
      if (testSwitch.ZFS and 'ZAP' in self.dut.statesExec[self.dut.nextOper] and not 'D_FLAWSCAN' in self.dut.statesExec[self.dut.nextOper]) and PrevFailState != 'SPF':
         return
      self.oUserFlaw.initdbi()
      self.oUserFlaw.initPList()
      self.oUserFlaw.initSFT()
      self.oUserFlaw.initTAList()

   #-------------------------------------------------------------------------------------------------------
   def repFlawLists(self):
      if not self.hdstrProc:
         try:
            self.oUserFlaw.repServoFlaws_T126()
            self.oUserFlaw.repdbi(spcId = 3)
            self.oUserFlaw.repPList()
            self.oUserFlaw.repSlipList()
         except FOFSerialTestTimeout:
            pass

   #-------------------------------------------------------------------------------------------------------
   def SetupDetcrPreamp(self): 
      if testSwitch.SPLIT_BASE_SERIAL_TEST_FOR_CM_LA_REDUCTION:
         from base_Preamp import CDETCRPreampSetup
      else:
         from base_SerialTest import CDETCRPreampSetup      
      oDETCRPreampSetup = CDETCRPreampSetup(self.dut, self.params)
      try: # fail safe
         if testSwitch.extern.FE_0251134_387179_RAP_ALLOCATE_FOR_LIVE_SENSOR_ON_HAP:
            self.oProcess.St(TP.LiveSensor_prm_094_2)
         oDETCRPreampSetup.run()
      except:
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=5, onTime=5, useESlip=1)
         pass
   
   #-------------------------------------------------------------------------------------------------------
   def runUmpAnalogFlawScan(self):
      #=== Power loss recovery support
      if testSwitch.FE_0241396_505235_FLAWSCAN_POWER_LOSS_RECOVERY:
         lastPoint, count = self.checkpoint.getLast(self.dut)
      else:
         lastPoint = None

      #=== Init AFS threshold
      if testSwitch.FE_0168920_322482_ADAPTIVE_THRESHOLD_FLAWSCAN_LSI:
         
         prmInitAfsThreshold = TP.PRM_INIT_AFS_THRESHOLD_355.copy()
         prmInitAfsThreshold["THRESHOLD"] = 42 #from 50 RSS recommendation         
         self.oUserFlaw.St(prmInitAfsThreshold)

      #=== Write even-odd
      self.oServoFlaw.servoFlawScan(TP.svoFlawPrm_126,SeekType.writeSeek)
      if testSwitch.FE_0241396_505235_FLAWSCAN_POWER_LOSS_RECOVERY:
         self.DoForEachHead(self.evenOddFlawScan, {'inPrm': TP.PRM_WRITE_UMP_ZONES_109.copy(), 'mode': 'even'}, lastPoint, count)
         self.DoForEachHead(self.evenOddFlawScan, {'inPrm': TP.PRM_WRITE_UMP_ZONES_109.copy(), 'mode': 'odd'}, lastPoint, count)
      else:
         self.evenOddFlawScan(TP.PRM_WRITE_UMP_ZONES_109, 'even')
         self.evenOddFlawScan(TP.PRM_WRITE_UMP_ZONES_109, 'odd')

      #=== Read even
      self.oServoFlaw.servoFlawScan(TP.svoFlawPrm_126,SeekType.readSeek)
      if testSwitch.FE_0241396_505235_FLAWSCAN_POWER_LOSS_RECOVERY:
         self.DoForEachHead(self.evenOddFlawScan, {'inPrm': TP.PRM_READ_UMP_ZONES_109.copy(), 'mode': 'even'}, lastPoint, count)
      else:
         self.evenOddFlawScan(TP.PRM_READ_UMP_ZONES_109, 'even')

      #=== Write even
      self.oServoFlaw.servoFlawScan(TP.svoFlawPrm_126,SeekType.writeSeek)
      if testSwitch.FE_0241396_505235_FLAWSCAN_POWER_LOSS_RECOVERY:
         self.DoForEachHead(self.evenOddFlawScan, {'inPrm': TP.PRM_WRITE_UMP_ZONES_109.copy(), 'mode': 'even'}, lastPoint, count)
      else:
         self.evenOddFlawScan(TP.PRM_WRITE_UMP_ZONES_109, 'even')

      #=== Read odd
      self.oServoFlaw.servoFlawScan(TP.svoFlawPrm_126,SeekType.readSeek)
      if testSwitch.FE_0241396_505235_FLAWSCAN_POWER_LOSS_RECOVERY:
         self.DoForEachHead(self.evenOddFlawScan, {'inPrm': TP.PRM_READ_UMP_ZONES_109.copy(), 'mode': 'odd'}, lastPoint, count)
      else:
         self.evenOddFlawScan(TP.PRM_READ_UMP_ZONES_109, 'odd')
      
   #-------------------------------------------------------------------------------------------------------
   def runSinglePassFlawScan(self):
      #=== Power loss recovery support
      if testSwitch.FE_0241396_505235_FLAWSCAN_POWER_LOSS_RECOVERY:
         lastPoint, count = self.checkpoint.getLast(self.dut)
      else:
         lastPoint = None

      if testSwitch.EVEN_ODD_FLAWSCAN:
         self.GetExecution(lastPoint, self.Test2108Write, ('even', 11))
         self.GetExecution(lastPoint, self.Test2108Write, ('odd', 12))
         self.GetExecution(lastPoint, self.Test2108Read, ('even', 13))
         self.GetExecution(lastPoint, self.Test2108Write, ('even', 14))
         self.GetExecution(lastPoint, self.Test2108Read, ('odd', 15))
      else:
         self.GetExecution(lastPoint, self.Test2108Write, ('all', 11))
         self.GetExecution(lastPoint, self.Test2108Read, ('all', 12))

   #-------------------------------------------------------------------------------------------------------
   def Test2108Write(self, arg):
      #=== Power loss recovery support
      if testSwitch.FE_0241396_505235_FLAWSCAN_POWER_LOSS_RECOVERY:
         lastPoint, count = self.checkpoint.getLast(self.dut)
      else:
         lastPoint = None

      #=== Input arguments
      mode = arg[0]
      t126_spcid = arg[1]

      #=== Write
      self.oServoFlaw.servoFlawScan(TP.svoFlawPrm_126, self.oSeekType.writeSeek)
      if testSwitch.FE_0241396_505235_FLAWSCAN_POWER_LOSS_RECOVERY:
         self.DoForEachHead(self.evenOddFlawScan, {'inPrm': TP.prm_SPFS_WRITE_2108.copy(), 'mode': mode}, lastPoint, count)
      else:
         self.evenOddFlawScan(TP.prm_SPFS_WRITE_2108, mode)

      #=== Build Slip-List from DBI and S-List
      self.oUserFlaw.writeSrvListToPList() 
      
      #=== Report Servo Flaw Table
      self.GetExecution(lastPoint, self.oUserFlaw.repServoFlaws_T126, param = t126_spcid)

   #-------------------------------------------------------------------------------------------------------
   def Test2108Read(self, arg):
      #=== Power loss recovery support
      if testSwitch.FE_0241396_505235_FLAWSCAN_POWER_LOSS_RECOVERY:
         lastPoint, count = self.checkpoint.getLast(self.dut)
      else:
         lastPoint = None

      #=== Input arguments
      mode = arg[0]
      t126_spcid = arg[1]

      #=== Read
      self.oServoFlaw.servoFlawScan(TP.svoFlawPrm_126, self.oSeekType.readSeek)
      if testSwitch.FE_0241396_505235_FLAWSCAN_POWER_LOSS_RECOVERY:
         self.DoForEachHead(self.evenOddFlawScan, {'inPrm': TP.prm_SPFS_READ_2108.copy(), 'mode': mode}, lastPoint, count)
      else:
         self.evenOddFlawScan(TP.prm_SPFS_READ_2108, mode)

      #=== Xlate EVM defect types
      self.oUserFlaw.xlateEvmDefectTypes()

      #=== Build P-List & Slip-List from DBI and S-List
      self.oUserFlaw.writeDbiToPList()
      self.oUserFlaw.writeSrvListToPList()

      #=== Report Servo Flaw Table
      self.GetExecution(lastPoint, self.oUserFlaw.repServoFlaws_T126, param = t126_spcid)

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
      for i in range(2):
         try:
            self.oProcess.St(fsParm)
            break
         except ScriptTestFailure, (failureData):
            if failureData[0][2] in [10211]: pass #fail safe FE_CONVERSION_ERROR, which is failure when we have whole band of tracks being skipped
            elif failureData[0][2] in [10547]:
               if self.dut.BG not in ['SBS'] and \
                  testSwitch.ENABLE_ON_THE_FLY_DOWNGRADE and self.downGradeOnFly(1, 10547):
                  objMsg.printMsg('EC10547, downgrade to %s as %s' % (self.dut.BG, self.dut.partNum))
               else:
                  raise failureData
            else: 
               raise failureData

   #-------------------------------------------------------------------------------------------------------
   def runAdjServoFlawScan(self):
      if testSwitch.FE_0241396_505235_FLAWSCAN_POWER_LOSS_RECOVERY:
         lastPoint, count = self.checkpoint.getLast(self.dut)
      else:
         lastPoint = None

      self.GetExecution(lastPoint, self.oProcess.St, TP.adj_svo_scan_write_prm_126)
      self.GetExecution(lastPoint, self.oProcess.St, TP.adj_svo_scan_read_prm_126)

      #=== Save "raw" Servo Flaw Table
      validList = self.SaveSList(lastPoint)

      if testSwitch.FE_0137096_342029_P_T64_SUPPORT:
         self.GetExecution(lastPoint, self.oProcess.St, TP.prm_64_servo_pad, validList)          # Skipped Track Padding
      else:
         self.GetExecution(lastPoint, self.oProcess.St, TP.prm_126_cw1, validList)               # Skipped Track Padding
      self.GetExecution(lastPoint, self.oUserFlaw.repServoFlaws_T126, 18)

   #-------------------------------------------------------------------------------------------------------
   def runTAScan(self):
      #=== T134 TA Scan
      base_prm_134_TA_Scan = TP.prm_134_TA_Scan.copy()
      if testSwitch.T134_TA_FAILURE_SPEC and testSwitch.extern.FE_0315265_228371_T134_SPEC_ADD_SYMBOL_LENTGTH_NO_CRITERIA:
         T134cword1= base_prm_134_TA_Scan['CWORD1'] | 0x100
         base_prm_134_TA_Scan.update({
                                  'CWORD1'  : T134cword1,                           #enable spec
                                  'MAX_ASPS'  :(TP.TA_PER_DRV_1D, TP.TA_PER_SUF_1D),#fail max number ta, drive/surface,"0" means off criteria
                                  'MARVELL_THRESH_LIMIT'  :TP.MARVELL_THRESH_LIMIT, #last 4 bits, number of passive, top 12 bits, TA track length
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
         self.oProcess.St(base_prm_134_TA_Scan)
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

      #=== T215 TA Deallocation
      base_TA_deallocation_prm_215 = TP.TA_deallocation_prm_215.copy()
      if testSwitch.T215_DETCR_TA_PAD_BY_SEVERITY and testSwitch.extern.FE_0316551_228371_TA_PAD_BY_SEVERITY:
         T215cword2 = base_TA_deallocation_prm_215['CWORD2'] | 0x40 # pad by severity
         base_TA_deallocation_prm_215.update({
                                           'CWORD2':T215cword2, 
                                          })
      self.oProcess.St(base_TA_deallocation_prm_215)
      defectTrack = list()
      entries = self.dut.dblData.Tables('P215_TA_DFCT_TRK_CNT').tableDataObj()
      for entry in entries:
         defectTrack.append(int(entry['DFCT_TRK']))
      self.dut.driveattr['DFCT_TRK'] = str(defectTrack)
      self.oUserFlaw.repTAList()
      if testSwitch.FE_0320143_305538_P_T134_TA_SCREEN_SPEC:
         from dbLogUtilities import DBLogCheck
         dblchk = DBLogCheck(self.dut)
         if dblchk.checkComboScreen(TP.T134_TA_Screen_Spec) == FAIL:
            objMsg.printMsg('Failed for TA combo spec')
            self.dut.driveattr['PROC_CTRL11'] = '48667'
            #if testSwitch.ENABLE_ON_THE_FLY_DOWNGRADE and self.downGradeOnFly(1, 48667):
            #   objMsg.printMsg('TA Spec exceeded limit , downgrade to %s as %s' % (self.dut.BG, self.dut.partNum))
            #else:
            #   ScrCmds.raiseException(48667, 'TA Spec exceeded limit @ Head : %s' % str(dblchk.failHead))
         if testSwitch.FE_0331797_228371_P_T134_TA_SCREEN_SPEC_TRK300:
            if dblchk.checkComboScreen(TP.T134_TA_Screen_Spec_TRK300) == FAIL:
               objMsg.printMsg('Failed for TA SL7 combo spec')
               self.dut.driveattr['PROC_CTRL11'] = '48667'
               #if testSwitch.ENABLE_ON_THE_FLY_DOWNGRADE and self.downGradeOnFly(1, 48667):
               #   objMsg.printMsg('TA Spec exceeded limit , downgrade to %s as %s' % (self.dut.BG, self.dut.partNum))
               #else:
               #   ScrCmds.raiseException(48667, 'TA SL7 Spec exceeded track limit 300 @ Head : %s' % str(dblchk.failHead))

   #-------------------------------------------------------------------------------------------------------
   def buildPList(self, spcId = 1):
      self.oUserFlaw.writeDbiToPList(spcId)
      self.oUserFlaw.writeSrvListToPList()

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
      from FSO import dataTableHelper
      self.dth = dataTableHelper()
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
      self.oProcess.St(inParm)

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
         self.GetExecution(lastPoint, self.oProcess.St, inPrm)
      if testSwitch.FE_0151000_007955_P_TRIPAD_UNVISITED_T118_CALL:
         inPrm = TP.prm_118_Tripad_Unvisited.copy()
         if isBpiFileNeeded: inPrm['dlfile'] = dlfile
         self.GetExecution(lastPoint, self.oProcess.St, inPrm)
      #=== Long padding
      inPrm = TP.prm_118_rev2_long002.copy()
      if isBpiFileNeeded: inPrm['dlfile'] = dlfile
      self.GetExecution(lastPoint, self.oProcess.St, inPrm)
      #=== Radial padding
      inPrm = TP.prm_118_rev2_radial002.copy()
      if isBpiFileNeeded: inPrm['dlfile'] = dlfile
      self.GetExecution(lastPoint, self.oProcess.St, inPrm)
      #=== Short padding
      inPrm = TP.prm_118_rev2_short002.copy()
      if isBpiFileNeeded: inPrm['dlfile'] = dlfile
      self.GetExecution(lastPoint, self.oProcess.St, inPrm)
      #=== Unvisited padding
      inPrm = TP.prm_118_rev2_unvisited002.copy()
      if isBpiFileNeeded: inPrm['dlfile'] = dlfile
      self.GetExecution(lastPoint, self.oProcess.St, inPrm)
      inPrm = None # Garbage Collector
      #=== Sort PList
      self.GetExecution(lastPoint, self.oProcess.St, TP.prm_118_sort_fill_def_list)
      #=== Wedge padding
      if testSwitch.FE_0137096_342029_P_T64_SUPPORT:
         self.GetExecution(lastPoint, self.oProcess.St, TP.prm_64_isolated_servo_pad)
      else:
         validList = self.SaveSList(lastPoint)
         self.GetExecution(lastPoint, self.oProcess.St, TP.prm_scratch_fill_117_2, validList)

   #=======================================================================================================
   # Power loss recovery support functions
   #=======================================================================================================
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
      if not testSwitch.FE_0241396_505235_FLAWSCAN_POWER_LOSS_RECOVERY:
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
         if testSwitch.FE_0365343_518226_SPF_REZAP_BY_HEAD:
            self.dut.driveattr['SPF_CUR_HEAD'] = hd     
         if testSwitch.UPS_PARAMETERS:
            param["inPrm"]['HdRg'] = (hd, hd)
         else:
            param["inPrm"]["HEAD_RANGE"] = (hd<<8) + hd

         func(**param)
         self.checkpoint.save(self.dut, point, -1)
      if testSwitch.FE_0365343_518226_SPF_REZAP_BY_HEAD:
         self.dut.driveattr['SPF_CUR_HEAD'] = -1
      
