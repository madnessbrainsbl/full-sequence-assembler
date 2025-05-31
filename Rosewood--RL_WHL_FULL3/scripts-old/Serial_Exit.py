#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: base Serial Port calibration states
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Serial_Exit.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Serial_Exit.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
from State import CState
import MessageHandler as objMsg
import traceback
from sptCmds import comMode
from PowerControl import objPwrCtrl
import ScrCmds


#----------------------------------------------------------------------------------------------------------
class CEndTesting(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def statePassEventHandler(self, state):
      #Can't run any exit testing
      pass

   #-------------------------------------------------------------------------------------------------------
   def statePreExecuteEventHandler(self, state):
      #Update the temp prior to running state
      if testSwitch.FE_0154423_231166_P_ADD_POST_STATE_TEMP_MEASUREMENT:
         self.updateStateTemperature(state)

   #-------------------------------------------------------------------------------------------------------
   def run(self):

      if testSwitch.FE_0271705_509053_NO_WAIT_FOR_SATAPHY_READY_UNDER_LOOPBACK and self.dut.nextOper in ['FNC2', 'CRT2', 'FIN2', 'CUT2']:
         # SATA port Loop back WA for PSTR (F3 code)
         from Serial_Init import CInitTesting 
         CInitTesting(self.dut).F3SataCheckLoopEnableWA()

      if not testSwitch.NoIO:
         objPwrCtrl.powerCycle(5000,12000,10,10, useESlip=1)

      if testSwitch.FE_0163145_470833_P_NEPTUNE_SUPPORT_PROC_CTRL20_21:
         cellTemp = ReportTemperature()/10.0
         self.dut.updateCellTemp(cellTemp)
         objMsg.printMsg("CEndTesting: Current cell temperature is "+str(cellTemp)+"C.", objMsg.CMessLvl.IMPORTANT)

      if testSwitch.operationLoop == 1:
         objMsg.printMsg("Loop Limit: %d" % testSwitch.operationLoopLimit)
         try:
            self.dut.operationLoopCounter += 1
         except:
            self.dut.operationLoopCounter = 1
         objMsg.printMsg("Loop iteration %d" % self.dut.operationLoopCounter)
         if self.dut.operationLoopCounter > testSwitch.operationLoopLimit:
            ScrCmds.raiseException(11044,"Operation Loop Limit Exceeded")

      # from FSO import CFSO
      # oFSO = CFSO()

      # if self.dut.sptActive.getMode() == comMode.availModes.mctBase:
         # try:
            # oFSO.saveRCStoPCFile()
         # except:
            # objPwrCtrl.powerCycle(5000,12000,10,10, useESlip=1)

      # if testSwitch.captureDriveVars == 1 and not ConfigVars[CN].get('PRODUCTION_MODE',0):
         # try:
            # mfile = GenericResultsFile("DriveVars.txt")
            # mfile.open('w')
         # except:
            # pass
         # try:
            # mfile.write(str(self.dut.DriveVarsMaster))
         # finally:
            # mfile.close()
      # try:
         # if testSwitch.FtpPCFiles and not ConfigVars[CN].get('PRODUCTION_MODE',0):
            # oFSO.ftpPCFiles()
      # except:
         # objMsg.printMsg("Failed to FTP files.",objMsg.CMessLvl.DEBUG)


#----------------------------------------------------------------------------------------------------------
class CFailProc(CState):
   """
      Put in your fail sequence code in this class' run() method
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def statePassEventHandler(self, state):
      #Can't run any exit testing
      pass

   #-------------------------------------------------------------------------------------------------------
   def GetStringCntInBinLog(self,pattern):
      Cnt=0
      HdSkipCnt=[0 for y in range(self.dut.imaxHead)]
      SkipType={}
      for head in range(self.dut.imaxHead):
         SkipType.setdefault(head,{})[36] = 0
         SkipType.setdefault(head,{})[58] = 0
      try:
         ResultsFile.open('rb')
         data=  ResultsFile.read()
         ResultsFile.close()

         mysearch = re.finditer(pattern,data)
         for search in mysearch:
            Cnt+=1
            if pattern =='\x06\x00\xFC\\x2A\x35\x38':               
               for i in range(search.end(),search.end()+200):
                  if ((data[i]=='\x2A' and data[i+1]=='\x24' and data[i+2]=='\x01') or
                      (data[i]=='\x2A' and data[i+1]=='\x2F' and data[i+2]=='\x04')):
                     HdSkipCnt[int(data[i+5])]+=1
                     FailHead=int(data[i+5])
                     SkipType[FailHead][58] += 1
                     for j in range(search.end()-7,search.end()-300,-1):
                        if data[j]=='\x06' and data[j+1]=='\x00' and data[j+2]=='\xFC':
                           ec=int(data[j+4])*10+int(data[j+5])
                           if ec != 58: # Do not save Skip Track Entry since it already save at beginning
                              try:
                                 if ec in SkipType[FailHead]:
                                    SkipType[FailHead][ec]+=1
                                 else:
                                    SkipType.setdefault(FailHead,{})[ec] = 1
                              except:
                                 SkipType.setdefault(FailHead,{})[ec] = 1
                           break
                     break
      except:
         pass

      return Cnt,HdSkipCnt,SkipType
   #-------------------------------------------------------------------------------------------------------   

   def run(self):
      from Process import CProcess
      self.oProc = CProcess()

      # if testSwitch.FE_0271705_509053_NO_WAIT_FOR_SATAPHY_READY_UNDER_LOOPBACK and self.dut.nextOper in ['FNC2', 'CRT2', 'FIN2', 'CUT2']:
         # # SATA port Loop back WA for PSTR (F3 code)
         # from Serial_Init import CInitTesting
         # CInitTesting(self.dut).F3SataCheckLoopEnableWA()

      # if testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT:
         # import CommitCls, CommitServices

         # try:
            # tmpFailData = self.oProc.oUtility.copy(self.dut.failureData)  #Because we want a value copy and it has to be deep/nested
            # noFailData = 0
         # except:
            # noFailData = 1

         # try:
            # #if not tier and we did commit
            # if ( ( not CommitServices.isTierPN(self.dut.partNum) ) and self.dut.driveattr['ORG_TIER'] == 'NONE' and ( self.dut.driveattr.get('COMMIT_DONE', "FAIL") == "PASS" or DriveAttributes.get('COMMIT_DONE', "FAIL") == 'PASS')):
               # CommitCls.CAutoCommit(self.dut, {'TYPE': 'DECOMMIT'}).run()
         # except:
            # objMsg.printMsg("Commit error!!\n%s" % (traceback.format_exc(),))
            # if noFailData != 1:
               # self.dut.failureData = tmpFailData

      # if self.dut.AFHCleanUp and testSwitch.FE_0150954_336764_P_ADD_AFH_CLEAN_UP_IN_FAIL_PROC_FOR_DRIVE_FAIL_AFTER_AFH4:
         # try:
            # objMsg.printMsg('Drive fail after AFH4 and do not pass AFH Clean up yet. AFH Clean up require before fail drive')
            # # dnld TGT code
            # from Serial_Download import CDnldCode
            # oDnldF3Code = CDnldCode(self.dut,{'CODES': ['UNLK','TGT','OVL'],})
            # oDnldF3Code.run()
            # # AFH Clean up
            # from base_TccCal import CTrackCleanup
            # oAFHCleanUp = CTrackCleanup(self.dut,{})
            # oAFHCleanUp.run()
         # except Exception, e:
            # objMsg.printMsg('Exception in AFH cleanup')
            # objMsg.printMsg(traceback.format_exc())

      # if self.dut.nextOper in ['FNC','FNC2','SPSC2'] and testSwitch.FE_0132440_336764_CFW_DNLD_AT_FNC2_AND_SPSC2:
         # if ConfigVars[CN].get('PRODUCTION_MODE',False) or ConfigVars[CN].get('ADG_ENABLE', False):
            # if testSwitch.FE_0148766_007955_P_FNC2_FAILPROC_DONT_LOAD_CFW_IF_F3_LOADED and self.dut.nextOper in ['FNC2']:
               # if not self.dut.sptActive.getMode() in [self.dut.sptActive.availModes.sptDiag, self.dut.sptActive.availModes.intBase]:
                  # try:
                     # objPwrCtrl.powerCycle(5000,12000,10,10)
                     # self.oProc.dnldCode(codeType='CFW', timeout =300)
                  # except:
                     # pass
            # else:
               # try:
                  # objPwrCtrl.powerCycle(5000,12000,10,10)
                  # self.oProc.dnldCode(codeType='CFW', timeout =300)
               # except:
                  # pass
      if not testSwitch.FE_0148166_381158_DEPOP_ON_THE_FLY:
         currentDisposition = self.dut.stateTransitionEvent

         try:
            from OTF_Waterfall import WTFDisposition
            WTFDisposition(self.dut).run()

            #If WTFDisposition changed the state transition then we want to quietly exit from failProc
            #  and allow the transition to do it's work
            if not self.dut.stateTransitionEvent in ['fail','pass']:
               return

         except Exception, e:
            objMsg.printMsg('Exception in WTF Disposition')
            objMsg.printMsg(traceback.format_exc())

         self.dut.stateTransitionEvent = currentDisposition


      objMsg.printMsg('<<< Test failure Handling >>>')
      # try:
         # tmpFailData = self.oProc.oUtility.copy(self.dut.failureData)  #Because we want a value copy and it has to be deep/nested
         # noFailData = 0
      # except:
         # noFailData = 1
      # iddis_PN_list =ConfigVars[CN].get('IDDIS_PN',[])
      # if testSwitch.AutoFA_IDDIS_Enabled and \
            # (self.dut.driveattr['PART_NUM'] in iddis_PN_list \
            # or self.dut.driveattr['PART_NUM'][0:3] in iddis_PN_list or 'ALL' in iddis_PN_list) and \
            # self.dut.sptActive.getMode() == comMode.availModes.mctBase :
         # if (self.dut.nextOper == 'FNC2'):
            # self.dut.iDDIS_Info = {}
            # self.dut.iDDIS_Info['DFlawTM'] = self.GetStringCntInBinLog('\x06\x00\xFC\\x2A\x33\x36')
            # self.dut.iDDIS_Info['DFlawUnservoable'] = self.GetStringCntInBinLog('\x06\x00\xFC\\x2A\x35\x37')
            # self.dut.iDDIS_Info['DFlawSkipTrk'] = self.GetStringCntInBinLog('\x06\x00\xFC\\x2A\x35\x38')
            # self.dut.iDDIS_Info['DFlaw4thVer'] = self.GetStringCntInBinLog('\x06\x00\xFC\\x2A\x34\x39')
            # self.dut.iDDIS_Info['DFlawAdjToWedge2'] = self.GetStringCntInBinLog('\x06\x00\xFC\\x2A\x34\x36')
            # objMsg.printMsg('DDIS Skip Track Summary %s'%self.dut.iDDIS_Info)

         # # will run IDDIS ,save P159 data
         # try:
            # self.oProc.St({'test_num':159,'timeout': 60, 'CWORD1': 0, 'DblTablesToParse': ['P159_FIFO']})
            # T_FIFO = self.dut.objSeq.SuprsDblObject['P159_FIFO']
            # self.dut.FIFO = []
            # for entry in T_FIFO:
              # self.dut.FIFO.extend([entry['*'][a:a+4] for a in xrange(0,len(entry['*']),4)])
         # except:
            # objMsg.printMsg("DUMP P159 Fail: %s" % traceback.format_exc())
            # pass
      # elif testSwitch.AutoFAEnabled :
         # try:
            # try:
               # errorcode = self.dut.failureData[0][2]
            # except:
               # errorcode = self.dut.errCode
            # objMsg.printMsg('<<< POTENTIAL FAIL CAUSE ANALYSIS FOR EC %s START >>>' %errorcode)
            # objFA = CAutoFA(self.dut)
            # objFA.run(errorcode)
         # except:
            # objMsg.printMsg("INIT FA DEBUG: %s" % traceback.format_exc())

      # SetFailSafe()
      # try:
         # #
         # # Fail handling code here
         # #

         # if testSwitch.FE_0139892_231166_P_SEARCH_FLED_FAIL_PROC:

            # self.dut.flashLedSearch_endTest = False
            # try:
               # ScrCmds.statMsg("Searching for FLASH LED's")
               # flashAddr = DriveVars.get('RW_FLASH_LED_ADDR','')
               # flashCode = DriveVars.get('RW_FLASH_LED_CODE','')

               # if flashAddr == '' and flashCode == '':
                  # import sptCmds

                  # flashAddr, flashCode = sptCmds.flashLEDSearch(120)
                  # ScrCmds.statMsg("Completed Searching for FLASH LED's")

               # if not flashAddr == '' and not flashCode == '':
                  # self.dut.errCode = 11231
                  # self.dut.errMsg = {"FLASH_LED_CODE":flashCode,"FLASH_LED_ADDR":flashAddr}
                  # tmpFailData = ScrCmds.makeFailureData(self.dut.errCode, self.dut.errMsg)
                  # self.dut.failureData = tmpFailData

            # except:
               # ScrCmds.statMsg("FLASH LED Search failed: Exception")

            # if self.dut.errCode in [11049,11231] and testSwitch.virtualRun != 1:
               # objPwrCtrl.powerCycle(useESlip = 1)


         # if self.dut.sptActive.getMode() == comMode.availModes.mctBase and testSwitch.DUMP_INFO_IN_FAIL_PROC:
            # from Servo import CServo
            # CServo().readServoFIFO()

            # if self.dut.HDSTR_PROC == 'Y':
               # st(233,CWORD1= 5, timeout=3000)

            # objMsg.printMsg("Attempting preperation of system area.")
            # try:
               # try:
                  # ClearFailSafe()
                  # #Only opti/init etf if not already initialized
                  # self.oProc.St(TP.readETFPrm_130)
                  # SetFailSafe()
               # except:
                  # #initialize the system area
                  # from base_SerialTest import CWriteETF, CSaveSIMFilesToDUT
                  # ClearFailSafe()
                  # CWriteETF(self.dut).run()
                  # CSaveSIMFilesToDUT(self.dut,params = []).run()

            # except:
               # objPwrCtrl.powerCycle(5000,12000,10,10)

            # if testSwitch.FE_0130958_336764_ADD_T186_TO_FAILPROC:
               # try:
                  # if testSwitch.FE_0173493_347506_USE_TEST321 and testSwitch.extern.SFT_TEST_0321:
                     # self.oProc.St(TP.get_MR_Resistance_321,spc_id=3,timeout=600,)
                  # elif testSwitch.FE_0159339_007955_P_FAIL_PROC_GET_MR_VALUES_ON_RAMP_186:
                     # self.oProc.St(TP.get_MR_Values_on_ramp_186,spc_id=3,timeout=600,)
                  # else:
                     # self.oProc.St(TP.PresetAGC_InitPrm_186,spc_id=2,timeout=600,MRBIAS_RANGE=(9999, 0), MAXIMUM=[125],)
               # except:
                  # objPwrCtrl.powerCycle(5000,12000,10,10)

            # if (testSwitch.MR_RESISTANCE_MONITOR and 0):
               # try:
                  # self.oProc.St(TP.PresetAGC_InitPrm_186_break)
               # except:
                  # pass

            # if testSwitch.FE_0132647_336764_ADD_T208_TO_FAILPROC:
               # try:
                  # self.oProc.St(TP.prm_208_autoDebug)
               # except:
                  # objPwrCtrl.powerCycle(5000,12000,10,10)

            # if testSwitch.FE_0166912_336764_P_ADD_T25_TO_FAILPROC:
               # try:
                  # self.oProc.St(TP.FailProcLoadUnloadPrm_25)
               # except:
                  # objPwrCtrl.powerCycle(5000,12000,10,10)

            # if testSwitch.WA_0141401_395340_P_T199_DATA_FOR_DEBUG_ANALYSE and self.dut.nextOper in ['FNC2']:  #Increase T199 for Debug Team
               # try:
                  # self.oProc.St(TP.Instability_TA_199)
               # except:
                  # objPwrCtrl.powerCycle(5000,12000,10,10)
               # try:
                  # self.oProc.St(TP.Instability_TA_199_2)
               # except:
                  # objPwrCtrl.powerCycle(5000,12000,10,10)

            # try:  #Fixed Add T103 WIJITA
               # from DebugAll import CDebugAll
               # objDebug = CDebugAll(self.dut, self.params)

               # if self.dut.HDSTR_PROC == 'Y':
                  # #need to download code if unload hdstr failed
                  # objPwrCtrl.powerCycle(5000,12000,10,10)
                  # self.oProc.dnldCode(codeType='CFW', timeout =300)
               # if not testSwitch.WA_0151540_342996_DISABLE_TEST_103:
                  # if not self.params.get('DISABLE_T103', 0):
                     # objDebug.run()
            # except:
               # pass

         # if testSwitch.FE_0154423_231166_P_ADD_POST_STATE_TEMP_MEASUREMENT:
            # self.updateStateTemperature(self.dut.currentState)
         # #
         # #
         # #
      # except:
         # pass
      # ClearFailSafe()
      # if noFailData == 0:
         # self.dut.failureData = tmpFailData
      # """
      # We want to raise an exception below so that the calling method (Setup.py) can report error to
      # host and do other standard failure actions like run STPGPD, send parametric data, run DBLog etc.
      # NOTE: It is possible to simply handle failure at this level, if that is what you want,
            # then comment out the following line and add your failure handling code.
      # """
      if not testSwitch.FE_0157872_395340_P_T135_ON_FAIL_PROC_FOR_ADG:
         self.exitStateMachine() # this will throw exception to be handled by top level code in Setup.py

