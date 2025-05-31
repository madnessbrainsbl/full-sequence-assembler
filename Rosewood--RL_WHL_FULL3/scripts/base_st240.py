#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: base hdstr/st240 state file
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_st240.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_st240.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
import time
from State import CState
import MessageHandler as objMsg
import Utility
from PowerControl import objPwrCtrl
import ScrCmds
from FSO import CFSO
from Process import CProcess

DEBUG = 0

###########################################################################################################
###########################################################################################################
class CHdstrRecord(CState):
    #------------------------------------------------------------------------------------------------------#
   """ Class to handle HdStr record """
   def __init__( self, dut, params=[]):
      self.params = params
      self.dut = dut
      self.dut.HDSTR_RECORD_ACTIVE = 'Y'
      depList = []
      CState.__init__(self, dut, depList)

   def run(self):
      objProc = CProcess()
      objMsg.printMsg("SAP Before Record")
      objProc.St(TP.hdstr_Read_SAP_TABLE) #Display SAP table before run HDSTR.
      objMsg.printMsg("HDSTR_RECORD")

      objMsg.printMsg("Save initial RCS to ETF for later retreival or update by FW.")
      oFSO = CFSO()
      oFSO.saveRCStoETF()

      objProc.St(TP.hdstrDefault)
      objProc.St(TP.hdstrClrBuff)
      objProc.St(TP.hdstrRecord)

      objMsg.printMsg("HDSTRRECORD Started...")

###########################################################################################################
###########################################################################################################
class CCheckForHdstrInGem(CState):
    #------------------------------------------------------------------------------------------------------#
   def __init__(self,dut,params=[]):
      self.params = params
      self.dut    = dut
      depList = []
      CState.__init__(self,dut,depList)

   def run(self):
      #
      #  Check for HDSTR in Gemini
      #
      if not self.dut.HDSTR_IN_GEMINI == 'Y':
         self.dut.stateTransitionEvent = 'nohdstr'
      else:
         objMsg.printMsg("HDSTR IN GEMINI TESTING ENABLED!")

###########################################################################################################
###########################################################################################################
class CHdstrInGemini(CState):
    #------------------------------------------------------------------------------------------------------#
   def __init__(self,dut,params=[]):
      self.params = params
      self.dut    = dut
      depList = []
      CState.__init__(self,dut,depList)

   def run(self):

      DriveOff(30)     #  Drive off wait 30 seconds
      DriveOn( )       #  Drive on and HDSTR testing will automatically start

      objMsg.printMsg("HDSTR SIMULATION... Testing for %s minutes..." % self.dut.HDSTR_DELAY_IN_MINS)
      time.sleep(self.dut.HDSTR_DELAY_IN_MINS * 60)
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=30, onTime=10, useESlip=1)

###########################################################################################################
###########################################################################################################
class CHdstrRecordStop(CState):
    #------------------------------------------------------------------------------------------------------#
   """ Class to handle HdStr Stop """
   def __init__( self, dut, params=[]):
      self.params = params
      self.dut = dut
      self.dut.HDSTR_RECORD_ACTIVE = 'N'
      depList = []
      CState.__init__(self, dut, depList)

   def run(self):
      objProc = CProcess()
      objMsg.printMsg("SAP in HDSTR Process")
      objProc.St(TP.hdstr_Read_SAP_TABLE) #Display SAP table before run HDSTR.
      objMsg.printMsg("HDSTR_RECORD_STOP")

      objProc.St(TP.hdstrStopRecord)
      objProc.St(TP.hdstrSave)
      objProc.St(TP.hdstrDefault)

      objProc.St(TP.hdstr_Enable_autoRun_1secDelay)

###########################################################################################################
###########################################################################################################
class CHdstrEndOfProc(CState):
    #------------------------------------------------------------------------------------------------------#
   """ Class to handle end of HDSTR testing """
   def __init__( self, dut, params=[]):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   def run(self):
      pass
      #objProc = CProcess()
      #objProc.St(TP.spindownPrm_2)

###########################################################################################################
###########################################################################################################
class CHdstrStartOfProc(CState):
    #------------------------------------------------------------------------------------------------------#
   """ Class to handle start of HDSTR testing """
   def __init__( self, dut, params=[]):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   def run(self):
      objProc = CProcess()
      CFSO().reportFWInfo()
      objProc.St(TP.hdstr_tempCheck)
      objProc.St(TP.hdstr_autoSeek_30)
      objProc.St(TP.hdstr_tempCheck)

###########################################################################################################
###########################################################################################################
class CHdstrUnload(CState):
    #------------------------------------------------------------------------------------------------------#
   """ Class to handle HdStr Unload """
   def __init__( self, dut, params=[]):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut.HDSTR_UNLOAD_ACTIVE = 'Y'

   def run(self):
      from MediaScan import CUserFlaw
      from Servo import CServo
      from RdWr import CRdWrScreen
      oServo = CServo()
      objProc = CProcess()
      oRdWr = CRdWrScreen()
      self.oUtility = Utility.CUtility()
      objMsg.printMsg("HDSTR_UNLOAD")

      if testSwitch.FE_0157311_345172_TURN_ON_ZAP_AFTER_HDSTR_UNLOAD:
         oServo.St(TP.zapPrm_175_zapOn)

      objProc.St(TP.hdstrDefault)
      objProc.St(TP.hdstrReadCmdFromDisc)

      try:
         try:
            HDSTR_RETEST = 0
            objProc.St(TP.hdstrDisplayOutput)
         #Upload TT data regardless of failure
            if not testSwitch.virtualRun:
               hdstrData = self.dut.dblData.Tables('P233_AUTORUN_SUMMARY').tableDataObj()
               self.dut.driveattr["ST240_TT"] = hdstrData[-1]['TOTAL_TIME']

               if testSwitch.FE_0167297_395340_P_CHECK_P233_TABLE_AFTER_UNLOAD:
                  hdstrSequence = self.dut.dblData.Tables('P233_TEST_TIME').tableDataObj()
                  if DEBUG:
                     objMsg.printMsg("P233_TEST_TIME : %s" % hdstrSequence)
                     objMsg.printMsg("P233_AUTORUN_SUMMARY : %s" % hdstrData)

                  if len(hdstrSequence) != int(hdstrData[-1]['TOTAL_CMDS']):
                     ScrCmds.raiseException(14562,"Autorun script completed with failure by CMDS is %s < TOTAL_CMDS is %s" % (len(hdstrSequence),int(hdstrData[-1]['TOTAL_CMDS'])))

               #Add HDSTR temperature screening (greater than 40c is pass and less than 40c is fail)
               if testSwitch.FE_0152783_345963_P_HDSTR_TMP_SCRN:
                  chk_drive_temp = DriveVars['Drive_Temperature_Deg_C']
                  objMsg.printMsg("The latest drive temperature on ST240: %d" % chk_drive_temp)
                  if chk_drive_temp < 40:
                     objMsg.printMsg("Drive temperature is less than 40, require auto retest full FNC2")
                     self.dut.driveattr['ST240_PROC'] = 'N'
                     self.dut.HDSTR_UNLOAD_ACTIVE = 'N'
                     self.dut.HDSTR_PROC = 'N'
                     self.dut.driveattr["RERUN_HDSTR"] = 'EC10606'
                     self.dut.HDSTR_RETEST = 1 # Auto re-test in FNC is enabled
                  if testSwitch.FE_0159968_409401_P_HDSTR_HIGH_TEMP_SCRN:
                     if chk_drive_temp > 65:
                        objMsg.printMsg("Drive temperature is more than 65")
                        if testSwitch.FE_0159969_409401_P_RETEST_FULL_FNC2_IF_HDSTR_HIGH_TEMP_SCRN_FAIL:
                           objMsg.printMsg("Auto retest full FNC2")
                           self.dut.driveattr['ST240_PROC'] = 'N'
                           self.dut.HDSTR_UNLOAD_ACTIVE = 'N'
                           self.dut.HDSTR_PROC = 'N'
                           self.dut.driveattr["RERUN_HDSTR"] = 'EC10605'
                           self.dut.HDSTR_RETEST = 1
                        else:
                           ScrCmds.raiseException(10605, "Current Drive Temperature is more than HIGH TEMP 65C")

               if testSwitch.FE_0157865_409401_P_TEMP_CHECKING_IN_ZAP_AND_FLAWSCAN_FOR_GHG_FLOW:
                  tbl172 = self.dut.dblData.Tables('P172_HDA_TEMP').tableDataObj()
                  stateChk = [10001, 10002] #10001: ZAP, 10002: D_FLAWSCAN
                  minHDATempChk = ConfigVars[CN].get('minHDATempChk', 40)
                  chkTempFail = 0
                  for row in range(len(tbl172)):
                     if int(tbl172[row]['TEST_SPC_ID']) in stateChk:
                        if int(tbl172[row]['HDA_TEMP_IN_C']) < minHDATempChk:
                           errorMsg = "Current Drive Temperature %sC (SPC_ID = %s) is less than MIN TEMP %sC" % (tbl172[row]['HDA_TEMP_IN_C'], tbl172[row]['TEST_SPC_ID'],str(minHDATempChk))
                           objMsg.printMsg(errorMsg)
                           chkTempFail = 1
                  if chkTempFail == 1:
                     ScrCmds.raiseException(10606, "Current Drive Temperature is less than MIN TEMP %sC" % (str(minHDATempChk)))

               if testSwitch.FE_0160792_210191_P_TEMP_CHECKING_IN_CRITICAL_STATES_FOR_GHG_FLOW_PHASE_1:
                  tbltemp = self.dut.dblData.Tables('TEST_TIME_BY_STATE').tableDataObj()
                  for row in tbltemp:
                     if row['STATE_NAME'] in TP.CHECK_TEMP_STATES:
                         if row['DRIVE_TEMP'] == '':
                            ScrCmds.raiseException(10606, "No Temperature found for %s" %(row['STATE_NAME']))
                         else:
                            if not(TP.CRITICAL_TEMP_MIN<(int(row['DRIVE_TEMP']))<TP.CRITICAL_TEMP_MAX):
                               ScrCmds.raiseException(10606, "Drive Temperature for state %s is %s and outside limits" %((row['STATE_NAME']),(row['DRIVE_TEMP'])))

         except ScriptTestFailure, (failuredata):
            self.ec= failuredata[0][2]
            if self.ec in [14558,14560,10475] and testSwitch.AUTO_RERUN_HDSTR:
               objMsg.printMsg("Fail 14558 or 14560, require auto retest full FNC2")
               self.dut.driveattr['ST240_PROC'] = 'N'
               self.dut.HDSTR_UNLOAD_ACTIVE = 'N'
               self.dut.HDSTR_PROC = 'N'
               self.dut.driveattr["RERUN_HDSTR"] = 'EC%s' % str(self.ec)
               self.dut.HDSTR_RETEST = 1
            elif self.ec in [11049] and testSwitch.AUTO_RERUN_HDSTR:
               objMsg.printMsg("Fail 11049, require auto retest full FNC2")
               objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
               self.dut.driveattr['ST240_PROC'] = 'N'
               self.dut.HDSTR_UNLOAD_ACTIVE = 'N'
               self.dut.HDSTR_PROC = 'N'
               self.dut.driveattr["RERUN_HDSTR"] = 'EC%s' % str(self.ec)
               self.dut.HDSTR_RETEST = 1
            else:
               raise
         except Exception, e:
            import sys
            if str(sys.exc_info()[0]).find('FOFResultsProcessingFailure') != -1:
               objMsg.printMsg("Fail 11044, require auto retest full FNC2")
               self.dut.driveattr['ST240_PROC'] = 'N'
               self.dut.HDSTR_UNLOAD_ACTIVE = 'N'
               self.dut.HDSTR_PROC = 'N'
               self.dut.driveattr["RERUN_HDSTR"] = 'EC11044'
               self.dut.HDSTR_RETEST = 1
            else:
               raise
      finally:
         #Capture current defect info regardless of failure
         SetFailSafe()
         objFs = CUserFlaw()
         objFs.repServoFlaws()
         objFs.repdbi() # dump db log to host (result file)
         objFs.repPList() # dump p-list to host (result file)
         ClearFailSafe()

      objProc.St(TP.hdstrDefault)
      objProc.St(TP.hdstrDisableAutoRun)
      objMsg.printMsg("SAP After Record")
      objProc.St(TP.hdstr_Read_SAP_TABLE) #Display SAP table after run HDSTR.

      try:
         if DriveAttributes.get('DISC_1_LOT','NONE')[0]=='P':
            self.objProc.St(TP.prm_107_aperio)
      except: pass

      objMsg.printMsg("HDSTR Unload- recovering updated Rap/Cap/Sap from ETF to Flash")
      if not self.dut.HDSTR_RETEST:
         self.dut.driveattr["ST240_PROC"] = 'C'
      #oFSO = CFSO()
      #oFSO.recoverRCSfromETF(updateFlash = True)


      if not testSwitch.FE_0124468_391186_MUSKIE_HDSTR_SUPPORT:
         #
         #  Recover RCS data from ETF to PC file and then to Flash
         #--------------------------------------------------------------------------------------
         objProc.St(TP.hdstr_recover_CAP)		#  Transfer CAP from ETF to PC File
         objProc.St(TP.hdstr_CAP_PCFile_to_Flash)	#  Transfer CAP from PC File to Flash
         #--------------------------------------------------------------------------------------
         objProc.St(TP.hdstr_recover_SAP)		#  Transfer SAP from ETF to PC File
         objProc.St(TP.hdstr_SAP_PCFile_to_Flash)	#  Transfer SAP from PC File to Flash
         #--------------------------------------------------------------------------------------
         objProc.St(TP.hdstr_recover_RAP)		#  Transfer RAP from ETF to PC File
         objProc.St(TP.hdstr_RAP_PCFile_to_Flash)	#  Transfer RAP from PC File to Flash
         #--------------------------------------------------------------------------------------

      from Servo import CServoFunc

      oSvo = CServoFunc()
      oSvo.setZonedACFF(enable = True)
      if testSwitch.FE_0157566_409401_P_MOVE_ZAP_ON_TO_HDSTR_UNLOAD:
         oRdWr.St(TP.zapPrm_175_zapOn)
      oSvo.setLVFF(enable = True)
      if testSwitch.FE_0155771_395340_P_HDSTR_UPDATE_ZAP_DATA_ON_GHG_PROCESS: #P'Vitoon request update ZAP data.
         #Update ZAP data after HDSRT Unload.
         rroAddress  = oSvo.readServoSymbolTable(['RRO_MODE_SYMBOL_OFFSET'], oSvo.ReadPVDDataPrm_11, oSvo.getServoSymbolPrm_11, oSvo.getSymbolViaAddrPrm_11)
         st([11], [], {'START_ADDRESS': self.oUtility.ReturnTestCylWord(rroAddress), 'ACCESS_TYPE': 2, 'spc_id': 1, 'END_ADDRESS': self.oUtility.ReturnTestCylWord(rroAddress), 'timeout': 1000, 'CWORD1': 1})                     # Read Misc.u16_RroMode
         st([11], [], {'timeout': 120, 'SYM_OFFSET': 152, 'MASK_VALUE': 0xfffa, 'CWORD1': 1024, 'spc_id': 1, 'WR_DATA':5, 'NUM_LOCS': 0})                            # Write Misc.u16_RroMode = 0x0005
         st([11], [], {'START_ADDRESS': self.oUtility.ReturnTestCylWord(rroAddress), 'ACCESS_TYPE': 2, 'spc_id': 1, 'END_ADDRESS': self.oUtility.ReturnTestCylWord(rroAddress), 'timeout': 1000, 'CWORD1': 1})                     # Read Misc.u16_RroMode
         acffAddress  = oSvo.readServoSymbolTable(['ZONED_ACFF_SYMBOL_OFFSET'], oSvo.ReadPVDDataPrm_11, oSvo.getServoSymbolPrm_11, oSvo.getSymbolViaAddrPrm_11)
         st([11], [], {'START_ADDRESS': self.oUtility.ReturnTestCylWord(acffAddress), 'ACCESS_TYPE': 3, 'spc_id': 1, 'END_ADDRESS': self.oUtility.ReturnTestCylWord(acffAddress), 'timeout': 1000, 'CWORD1': 1})           # GetSymbolViaAddr
         st([178], [], {'timeout': 600, 'spc_id': 1, 'CWORD1': 1056})

###########################################################################################################
###########################################################################################################
class CCheckForHdstr(CState):
    #------------------------------------------------------------------------------------------------------#
   """ Class to handle HdStr Unload """
   def __init__( self, dut, params=[]):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

      self.dut = dut

   def run(self):
      objMsg.printMsg("Checking For HDSTR")

      if self.dut.HDSTR_PROC == 'Y':
         objMsg.printMsg("HDSTR TESTING ENABLED!!!")
         self.dut.stateTransitionEvent = 'pass'
      else:
         self.dut.stateTransitionEvent = 'nohdstr'
         objMsg.printMsg("HDSTR TESTING DISABLED!!!!!!")

###########################################################################################################
###########################################################################################################
class CST240Load(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params=[]):
      self.params = params
      self.dut = dut
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      oProc = CProcess()

      self.dut.HDSTR_RECORD_ACTIVE = 'Y'

      objMsg.printMsg("******************* Power cycle drive befor download HDSTR code ******************")
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      objMsg.printMsg("******************* ST240 LOAD ******************")
      objMsg.printMsg("----------------- Load HDSTR Code: (%s) ----------------" % self.params['CFW_ST'])
      self.dut.overlayHandler.checkForOverlayKey(overlayKey=self.params['S_OVL_ST'])
      oProc.dnldCode(codeType=self.params['CFW_ST'], timeout=500)

      st([149], [], {'timeout': 300, 'CWORD1': 0x0100}) # Load SF3 OVL code

      st(233,CWORD1= 5, timeout=3000)
      st(233,CWORD1= 4, timeout=3000)
      st(172,{'timeout': 600, 'spc_id': 1, 'CWORD1': 2})

      objMsg.printMsg("******************* ST240 END ******************")

###########################################################################################################
class CST240Unld(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params=[]):
      self.params = params
      depList = []
      self.dut = dut
      self.oUtility = Utility.CUtility()
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      oProc = CProcess()

      self.dut.HDSTR_RECORD_ACTIVE = 'N'
      self.ec = []
      objMsg.printMsg("******************* ST240 Unlaod Start *************")

      st([233], [], {'timeout': 1200, 'CWORD1': 7})
      st([233], [], {'timeout': 5400, 'CWORD1': 0})

      try:
         try:
            st([233], [], {'timeout': 3600, 'spc_id': 1, 'CWORD1': 3})

         except ScriptTestFailure, (failuredata):
            self.ec= failuredata[0][2]
            if self.ec in [14558,14560] and testSwitch.AUTO_RERUN_HDSTR:
               self.dut.stateTransitionEvent = 'reRunFNC'
               self.dut.driveattr['ST240_PROC'] = 'N'
               self.dut.driveattr["RERUN_HDSTR"] = 'EC%s' % str(self.ec)
               return
            raise
         except Exception:
            raise

      finally:
         st([233], [], {'timeout': 60, 'CWORD1': 11})
         st([233], [], {'timeout': 300, 'CWORD1': 5})
         if self.ec in [14558,14560] and testSwitch.AUTO_RERUN_HDSTR:
            TP.HDSTR_WARM_UP = 0
            objMsg.printMsg("******************* Power cycle drive befor download HDSTR code ******************")
            objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
            objMsg.printMsg("----------------- Load Back Original Code: (%s) ----------------" % self.params['CFW_ST'])
            self.dut.overlayHandler.checkForOverlayKey(overlayKey=self.params['S_OVL_ST'])
            oProc.dnldCode(codeType=self.params['CFW_ST'], timeout=500)
            st([149], [], {'timeout': 300, 'CWORD1': 0x0100}) # Load SF3 OVL code
         oAFH_Screens  = CAFH_Screens()

         self.odPES.lmt.maxDAC = (2 ** TP.dpreamp_number_bits_DAC.get(self.dut.PREAMP_TYPE, 0)) - 1
         self.cAFH = AFH.CAFH()
         coefs = self.cAFH.getClrCoeff(TP.clearance_Coefficients, self.dut.PREAMP_TYPE, self.dut.AABType)
         self.cAFH = None  # Allow GC
      #self.ST240_ReadScreen_Unload(spc_id=1)
      oAFH_Screens.AFH_State == 1     # force the AFH state to AFH1

      objMsg.printMsg("******************* Power cycle drive befor download HDSTR code ******************")
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      objMsg.printMsg("----------------- Load Back Original Code: (%s) ----------------" % self.params['CFW_ST'])
      self.dut.overlayHandler.checkForOverlayKey(overlayKey=self.params['S_OVL_ST'])
      oProc.dnldCode(codeType=self.params['CFW_ST'], timeout=500)

      st([149], [], {'timeout': 300, 'CWORD1': 0x0100}) # Load SF3 OVL code

      self.dut.driveattr['ST240_PROC'] = 'C'
      DriveAttributes['ST240_PROC'] = 'C'
      if DriveVars.has_key('ST240_total_time'):
         DriveAttributes['ST240_TIME'] = DriveVars['ST240_total_time']
      objMsg.printMsg("******************* ST240 Unlaod End *************")

      #objMsg.printMsg("************* Enable for programs with zACFF enabled in SAP *************")
      #oSvo = CServoFunc()
      #oSvo.setZonedACFF(enable = True)
   #-------------------------------------------------------------------------------------------------------
   def ST240_ReadScreen_Unload (self, spc_id=1):
      fail_mode = TP.prm_quickSER_250.get('MODES', 'SYMBOL')
      testZoneList = TP.prm_quickSER_250.get('TEST_ZONES', [1,2,9,14,15])
      if spc_id ==2:# grab only the second call data in prep for the P_QUICK_ERR_RATE table update
         if testSwitch.virtualRun:spc_id = str(spc_id)
         P250spc_id2Table = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').chopDbLog('SPC_ID', 'match',spc_id)
         P250choppedTable = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').chopDbLog('ERROR_RATE_TYPE', 'match',fail_mode,tbl=P250spc_id2Table)
      elif spc_id ==1:# for the first call, extract only the best BER for each hd/zone combo in prep for the P_QUICK_ERR_RATE table update
         P250choppedTable = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').chopDbLogLoop(testZoneList,tableName='P250_ERROR_RATE_BY_ZONE',colCoarse='ERROR_RATE_TYPE', colCoarseMatch = fail_mode, colFine='RAW_ERROR_RATE',ColFineMinMax='min')
      curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(250,spc_id)

      for data in xrange(len(P250choppedTable)):
         baseUpdate = {
            'HD_PHYS_PSN': P250choppedTable[data].get('HD_PHYS_PSN'),
            'TRK_NUM': P250choppedTable[data].get('START_TRK_NUM'),
            'SPC_ID': P250choppedTable[data].get('SPC_ID'),
            'OCCURRENCE': occurrence,
            'SEQ':curSeq,
            'TEST_SEQ_EVENT': testSeqEvent,
            'HD_LGC_PSN': P250choppedTable[data].get('HD_LGC_PSN'),
            'RBIT':self.oUtility.setDBPrecision((P250choppedTable[data].get('BITS_READ_LOG10')),4,2),
            'RRAW':self.oUtility.setDBPrecision((P250choppedTable[data].get('RAW_ERROR_RATE')),4,2), #leave sign negative
            'OTF':'', #null for now
            'HARD':'', #null for now
            'DATA_ZONE':P250choppedTable[data].get('DATA_ZONE'),
            }

         self.dut.dblData.Tables('P_QUICK_ERR_RATE').addRecord(baseUpdate)
      if spc_id ==1:
         objMsg.printMsg("quickSymbolErrorRate(first call,spc_id =1): saving P_QUICK_ERR_RATE table to marshall object ", objMsg.CMessLvl.VERBOSEDEBUG)
         self.dut.objData.update({'P_QUICK_ERR_RATE':self.dut.dblData.Tables('P_QUICK_ERR_RATE').tableDataObj()})

###########################################################################################################
class CST240STOP(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params=[]):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      oProc = CProcess()
      objMsg.printMsg("******************* ST240 STOP *************")

      st([233], [], {'timeout': 3000, 'CWORD1': 2})
      st([233], [], {'timeout': 3000, 'CWORD1': 6})
      st([233], [], {'timeout': 3000, 'CWORD1': 0})
      # change initial delay from 1 sec to 10 sec
      st([233], [], {'INITIAL_DELAY': 10, 'timeout': 60, 'CWORD1': 9})
      self.dut.driveattr['ST240_PROC'] = 'Y'
      objMsg.printMsg("******************* ST240 STOP *************")

###########################################################################################################
