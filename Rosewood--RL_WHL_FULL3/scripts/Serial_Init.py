#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: base Serial Port calibration states
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/12/19 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Serial_Init.py $
# $Revision: #9 $
# $DateTime: 2016/12/19 20:01:07 $
# $Author: yihua.jiang $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Serial_Init.py#9 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#

from Constants import *
from TestParamExtractor import TP
from State import CState
from Drive import objDut
import MessageHandler as objMsg
from PowerControl import objPwrCtrl
from Rim import objRimType
from sptCmds import objComMode
import traceback
import ScrCmds
from UPS import upsObj
from Exceptions import CDblogDataMissing, CRaiseException
#----------------------------------------------------------------------------------------------------------
class CInitTesting(CState):
   """
      Provide a single call to preparing slot/drive for testing. Readies baud rate, power, CM variables
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      # if testSwitch.virtualRun:
         # self.dut.driveattr['MC Offset'] = 0

      # if testSwitch.Enable_Reconfig_WTF_Niblet_Level_Check:
         # from CustomCfg import CCustomCfg
         # CCustomCfg().CheckReconfig(objDut.partNum)

      if objRimType.IsHDSTRRiser() and (str(self.dut.imaxHead) in getattr(TP,'HDSTR_SP_HD',[])):
         objMsg.printMsg('Drive %s Hd. do not HDSTR-SP flow.' % self.dut.imaxHead)
         ScrCmds.raiseException(45630,"Drive %s Hd. do not HDSTR-SP flow." % self.dut.imaxHead)

      if not self.dut.PSTROper and objRimType.IsPSTRRiser():
         objMsg.printMsg('Current operation %s is not allow to run in PSTR' % self.dut.nextOper)
         ScrCmds.raiseException(49052,'Current operation %s is not allow to run in PSTR' % self.dut.nextOper)

      if objRimType.IsPSTRRiser() and ConfigVars[CN].get('PSTRTimeOut',0):
         PSTRTimeOut = ConfigVars[CN].get('PSTRTimeOut',0)
         objMsg.printMsg('PSTRTimeOut= %s' %(PSTRTimeOut))
         RequestService('SetBatchTimeout', PSTRTimeOut ) 
      else:
         objMsg.printMsg('Not PSTR / No PSTRTimeOut Value')

      #Check RerunTODT
      if testSwitch.FE_0145983_409401_P_SEND_ATTR_FOR_CONTROL_DRIVE_ERROR:
         self.RerunTODT()

      from ICmdFactory import ICmd
      if objRimType.IOInitRiser():
         self.dut.sptActive = objComMode
         self.dut.sptActive.setMode(objComMode.availModes.intBase)
         ICmd.downloadIORimCode()

      if self.dut.nextOper == 'PRE2':
         from WTF_Tools import CWTF_Tools
         oWTF_Tools = CWTF_Tools()
         oWTF_Tools.buildClusterList(updateWTF = 1)
      
      from PackageResolution import PackageDispatcher
      from Cell import theCell
      
      
      # if 0:
         # try:
            # from Serial_Download import CFLASH_LOD
            # ofls_lod = CFLASH_LOD(self.dut, codename = 'CFW_BIN')
            # ofls_lod.run()
         # except:
            # objMsg.printMsg("Auto-Seaserial Lod Failed")

      self.dut.sptActive = objComMode
      self.dut.PRE2INIT_SeaSr_Done = False

      if objRimType.CPCRiser():
         retryData = ICmd.CRCErrorRetry(IO_CRC_RETRY_VAL)
         objMsg.printMsg("CRCErrorRetry(%d)='%s'" % (IO_CRC_RETRY_VAL, str(retryData)))

      if not testSwitch.FE_0221722_379676_BYPASS_TPM_DOWNLOAD:
         # Set the TPM file to allow FLASH writes with MCT
         tpmfile = PackageDispatcher(self.dut, 'TPM').getFileName()
         objMsg.printMsg("Setting TPMFile to: %s" % str(tpmfile), objMsg.CMessLvl.IMPORTANT)
         SetTPMFile((CN, tpmfile))

      if testSwitch.FE_0116894_357268_SERVO_SUPPLIED_TEST_PARMS:
         from TestParamExtractor import setSrvoOverrides
         # Check for servo test parameter overrides in the servo release package.
         svo_prm_filename = PackageDispatcher(self.dut, 'SVO_PRM').getFileName()
         if svo_prm_filename != None:
            # If found, read the file contents and send to the TestParamExtractor.
            import os
            svo_file_contents = open(os.path.join(ScrCmds.getSystemDnldPath(),svo_prm_filename), 'rb').read()
            cleaned_svo_file_contents = svo_file_contents.replace("\r", " ")
            setSrvoOverrides(cleaned_svo_file_contents)

      #Set the default cert temperature based on the current operations temperature defined in temp_profile in TestParam.py
      if not ConfigVars[CN]['BenchTop'] and not self.dut.nextOper == "CCV2":
         if objRimType.IsHDSTRRiser() and testSwitch.FE_0161827_345172_P_CONTROL_TEMP_PROFILE_BY_HEAD:
            try:
               PF_SN = self.dut.serialnum[1:3]
               reqTemp, minTemp, maxTemp = TP.temp_profile_by_head[self.dut.nextOper][PF_SN]
               objMsg.printMsg("Control Temp profile by head for HG/GHG2")
            except:
               reqTemp, minTemp, maxTemp = TP.temp_profile[self.dut.nextOper]
               objMsg.printMsg("Fail get control temp profile by head for HG/GHG2, use default in Gemini")
         else:
            reqTemp, minTemp, maxTemp = TP.temp_profile[self.dut.nextOper]

         #overwrite reqTemp if the PRE2 temp was raised to make the drive meet the minDriveTemp in TP.
         if not self.dut.driveattr['PRE2_FINAL_TEMP'] == 'NONE' and self.dut.nextOper in ['CAL2','FNC2'] and objRimType.isNeptuneRiser():
            reqTemp = int(self.dut.driveattr['PRE2_FINAL_TEMP'])
            objMsg.printMsg("PRE2_FINAL_TEMP =%sC, reqTemp changed to: %sC" % (self.dut.driveattr['PRE2_FINAL_TEMP'],reqTemp))

         if (objRimType.isNeptuneRiser() and self.dut.nextOper in ['SCOPY','PRE2','CRT2'] and not self.dut.powerLossEvent) or (objRimType.IsLowCostSerialRiser() and testSwitch.FE_0180754_345172_RAMP_TEMP_NOWAIT_HDSTR_SP):
            RMode = 'nowait'
         else:
            RMode = 'wait'
         objMsg.printMsg("base_SerialTest.py Setting rampMode to: %s" % RMode)
         theCell.setTemp(reqTemp, minTemp, maxTemp, self.dut.objSeq, objDut, RMode) #Breaks bench cell so we don't execute this if BenchTop set true

      objMsg.printMsg("Current cell temperature is "+str(ReportTemperature()/10)+"C.", objMsg.CMessLvl.IMPORTANT)

      if self.dut.nextOper == "PRE2":
         objMsg.printMsg('')
         objMsg.printMsg('')
         objMsg.printMsg("=================================" )
         objMsg.printMsg("=================================" )
         objMsg.printMsg("Performing Auto-Seaserial" )
         objMsg.printMsg("=================================" )
         objMsg.printMsg("=================================" )
         objMsg.printMsg('')
         objMsg.printMsg('')
         try:
            self.autoSeaSerialRetry(0, 1)
            SetDTRPin(0) == 0
            SetDTRPin(1) == 0
         except:
            if not DriveAttributes.get('SF3CODE','NONE') == '8C':
               DriveAttributes['SF3CODE'] = '8C'
               ScrCmds.raiseException(11891, 'SF3 CODE IS ERROR !!!!!! ')
            else:
               ScrCmds.raiseException(11890, 'PCB IS BAD !!!!!! ')


      #1st power on of drive
      if self.dut.nextOper == "PRE2":
         import PIF

      if testSwitch.BF_0165911_231166_P_FIX_NEXTPRE2_WITH_PLR:
         if self.dut.nextOper == "PRE2" and not self.dut.powerLossEvent:
            if len(self.dut.stateSequence[self.dut.nextOper]) > 1:
               if getattr(PIF,'NextPRE2State',''):
                  if self.dut.stateSequence[self.dut.nextOper][1] != getattr(PIF,'NextPRE2State',''):
                     self.dut.PRE2JumpStateInStatetable = True
      else:
         if self.dut.nextOper == "PRE2":
            if getattr(PIF,'NextPRE2State','') and self.dut.stateSequence[self.dut.nextOper][1] != getattr(PIF,'NextPRE2State',''):
               self.dut.PRE2JumpStateInStatetable = True

      objMsg.printMsg("PROC_TEST_FLOW %s OPER %s"%(self.dut.driveattr.get('PROC_TEST_FLOW','GEM'),self.dut.nextOper))
      if objRimType.IsLowCostSerialRiser() and ConfigVars[CN].get('HG_CM_OverLoad',0) == 1 and ((self.dut.nextOper == 'PRE2' and self.dut.driveattr.get('PROC_TEST_FLOW','GEM') == 'HG') or (self.dut.nextOper == 'CAL2' and self.dut.driveattr.get('PROC_TEST_FLOW','GEM') =='GHG2')):
         import time
         timesleep = int(getattr(TP,"TimeWaitStart",{}).get(self.dut.serialnum[1:3],60))*CellIndex  #TP.TimeWaitStart*CellIndex
         objMsg.printMsg("Set time sleep to help CM load average(%d)==> CellIndex(%d) x %d Secs"%(timesleep,CellIndex,getattr(TP,"TimeWaitStart",{}).get(self.dut.serialnum[1:3],60)))
         time.sleep(timesleep)

      if ((testSwitch.FE_0111872_347506_SEASERIAL_RECYCLED_PCBAS and int(DriveAttributes.get('PCBA_CYCLE_COUNT', 0)) > 1) or \
         testSwitch.FE_0160076_336764_FORCED_SEASERIAL_AT_INIT_PRE2 or \
         self.dut.driveattr.get('FDE_DRIVE','NONE') == 'FDE') and \
         (self.dut.nextOper in ["PRE2", "SCOPY"] and not self.dut.powerLossEvent and self.dut.stateTransitionEvent != 'procJumpToState' and not self.dut.PRE2JumpStateInStatetable):

         objMsg.printMsg("Auto-Seaserial for recycled PCBA" )
         if objRimType.isNeptuneRiser():
            #Neptune2 requires special power on in syncBootLoader, which requires SPortToInitiator to be False
            SPortToInitiator(False)
         self.autoSeaSerialRetry(0, 1)
         if self.dut.nextOper == "PRE2":
            self.dut.PRE2INIT_SeaSr_Done = True
         theCell.enableESlip(sendESLIPCmd = True)
         objPwrCtrl.changeBaud(PROCESS_HDA_BAUD)
         self.dut.sptActive.setMode(self.dut.sptActive.availModes.mctBase,determineCodeType = True)
      else:
         try:
            # Following Power Cycle will raise exception 10340 for all locked
            # FDE drives at Serial Cell because locked drive will not accept ESLIP
            # baud command. Since we already know that the drive is locked if
            # FDE_DRIVE = FDE then we just raise the exception to save test time
            # consumed by Power Cycle.
            if testSwitch.FE_0121834_231166_PROC_TCG_SUPPORT:
               if self.dut.driveattr['FDE_DRIVE'] == 'FDE':
                  ScrCmds.raiseException(10340)
               elif self.dut.nextOper in ['CRT2','MQM2','FIN2']:
                  objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

                  if self.dut.certOper:
                     self.dut.sptActive.setMode(self.dut.sptActive.availModes.mctBase,determineCodeType = True) #check for code type & flash LED's
                  else:
                     self.dut.f3Active == 1

                  if self.dut.f3Active:
                     objMsg.printMsg("f3Active, check for drive life cycle state")

                     if self.dut.certOper:
                        objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

                     from TCG import CTCGPrepTest
                     oTCG = CTCGPrepTest(self.dut)

                     try:
                        oTCG.CheckFDEState()          
                     except:
                        objMsg.printMsg("Error in getting drive life cycle state, continue")
                        self.dut.LifeState = "NONE"
                        objMsg.printMsg("Power cycling the drive.")
                        objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

                     if testSwitch.BF_0180787_231166_P_REMOVE_FDE_CALLBACKS_FOR_CHECKFDE:
                        oTCG.RemoveCallback() 

                     if not (self.dut.LifeState == "00" or self.dut.LifeState == "NONE"):
                        objMsg.printMsg("Drive is not in SETUP state, try FDE_Unlock_Retry.")
                        ScrCmds.raiseException(10340)
                     else:
                        objMsg.printMsg("Drive is in SETUP/NONE state, continue")
                  else:
                     objMsg.printMsg("f3Active = false, no need to check for drive life cycle state")     

                  if not self.dut.certOper:
                     self.dut.sptActive.setMode(self.dut.sptActive.availModes.mctBase,determineCodeType = True) #check for code type & flash LED's   
               else:
                  objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)  
                  self.dut.sptActive.setMode(self.dut.sptActive.availModes.mctBase,determineCodeType = True) #check for code type & flash LED's
            else: 
               objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)  
               self.dut.sptActive.setMode(self.dut.sptActive.availModes.mctBase,determineCodeType = True) #check for code type & flash LED's
         except ScrCmds.CRaiseException, (exceptionData):

            ec = exceptionData[0][2]
            try:
               if self.dut.nextOper == "CCV2":
                  objMsg.printMsg("In CCV2 oper, attempting to unlock Diag port only")
                  objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
                  self.dut.objData.update({'TCGPrepDone': 1})
               else:
                  # try and unlock
                  objMsg.printMsg("Attempting SED Unlock")
                  self.FDE_Unlock_Retry(ec)

            except:
               try:
                  #if we have auto-seaserial enabled and we couldn't communicate to hda and we're in pre2 then seaserial the drive
                  self.autoSeaSerialRetry(ec)
               except ScrCmds.CRaiseException, (eData):
                  if eData[0][2] in [11178, ]:
                     ScrCmds.raiseException(11178, "After Attempting SED Unlock autoSeaSerialRetry - Wrong PCBA serial number")
                  else:
                     ScrCmds.raiseException(ec,exceptionData[0][0])
               except:
                  #If this fails then re-raise the original exception
                  ScrCmds.raiseException(ec,exceptionData[0][0])

            theCell.enableESlip(sendESLIPCmd = True)
            objPwrCtrl.changeBaud(PROCESS_HDA_BAUD)
            self.dut.sptActive.setMode(self.dut.sptActive.availModes.mctBase,determineCodeType = True)

      try:
         if self.dut.sptActive.getMode() == self.dut.sptActive.availModes.mctBase:
            if (testSwitch.winFOF or ConfigVars[CN].get('BenchTop',0)) and self.dut.driveattr.get('MDW_CAL_STATE',0) == 0:
               from Servo import CServoFunc
               oSrvFunc = CServoFunc()
               oSrvFunc.getMDWCalState(TP.mdwCalState_11)
      except:
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

      try:
         if self.dut.sptActive.getMode() == self.dut.sptActive.availModes.mctBase:
            oDrvInfo = CInit_DriveInfo(self.dut,self.params)
            oDrvInfo.run()
      except:
         objMsg.printMsg(traceback.format_exc())
         if (self.dut.nextOper == 'FNC2') and (testSwitch.auditTest ==1):
            raise #We're in audit mode so let's not continue if we have an error
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)



      if testSwitch.FE_0146555_231166_P_VER_TEMP_SAT_INIT:
         #Set the default cert temperature based on the current operations temperature defined in temp_profile in TestParam.py
         from Temperature import CTemperature
         CTemperature().verifyHDASaturation()


      #Initialize some drive attributes needed for historical purposes
      if not testSwitch.BF_0159554_426568_P_UNDO_INCORRECT_SETTING_OF_CFG:
         self.dut.driveattr['CFG'] = CN
      self.dut.driveattr['CONGEN_PNUM'] = 'NONE'
      self.dut.driveattr['DRIVE_TYPE'] = 'NONE'
      self.dut.driveattr['USB_DRIVE'] = 'NONE'

      self.dut.driveattr['OPS_CAUSE'] = 'NONE'
      DriveAttributes.update({'OPS_CAUSE': 'NONE'})

      FBP1 = float(DriveAttributes.get("FBP1","0"))   # knl
      FBP2 = float(DriveAttributes.get("FBP2","0"))

      dblogObj = self.dut.dblData

      dblogObj.Tables("FBP_TABLE").addRecord(
         {
         'FBP1_COL': FBP1,
         'FBP2_COL': FBP2,
         })

      objMsg.printMsg("FE_0000000_305538_HYBRID_DRIVE=%d" % testSwitch.FE_0000000_305538_HYBRID_DRIVE)
      objMsg.printMsg("FDE_DRIVE=%s at the end of Init" % self.dut.driveattr['FDE_DRIVE'])
      if (self.dut.driveattr['FDE_DRIVE']=='FDE') and (self.dut.objData.retrieve('KwaiPrepDone')==0) and (self.dut.objData.retrieve('TCGPrepDone')==0):
         if not ConfigVars[CN].get('PRODUCTION_MODE',0) and testSwitch.FE_0246029_385431_SED_DEBUG_MODE:
            objMsg.printMsg("FE_0246029_385431_SED_DEBUG_MODE on, continue")
         else: 
            objMsg.printMsg("FDE_DRIVE = FDE at the end of Init, failed")
            ScrCmds.raiseException(14802, "FDE_DRIVE = FDE at the end of Init, failed")
      if testSwitch.FE_0121834_231166_PROC_TCG_SUPPORT and self.dut.objData.retrieve('TCGPrepDone') == 1:
         from PIFHandler import CPIFHandler
         CPIFHandler().IsSDnD()

      if DriveAttributes.get("TEST_BLOCK","NONE") == 'NONE' or DriveAttributes.get("TEST_BLOCK","NONE") == '2':
         if self.dut.nextOper != "CRT2":
            DriveAttributes["TEST_BLOCK"] = "1"
      if DriveAttributes.get("SGMNT_VAL","NONE") != 'NONE' and self.dut.nextOper in ['SCOPY', 'PRE2']:
         DriveAttributes["SGMNT_VAL"] = "NONE"


      if testSwitch.FE_0134030_347506_SAVE_AND_RESTORE:
         restoreDrive = ConfigVars[CN].get('RestoreDriveState', {}).get(self.dut.nextOper, None)
         if restoreDrive:
            from base_SaveRest import CRestoreDriveState
            oRestore = CRestoreDriveState(self.dut, {'FILENAME_BASE': restoreDrive})
            objMsg.printMsg('\nRESTORING DRIVE NOW!!!\n')
            oRestore.run()

      if testSwitch.shortProcess and (self.dut.nextOper not in ['SCOPY', 'PRE2', 'FIN2', 'IOSC2', 'CUT2']):
         objMsg.printMsg('\nShort process requires a download in the init step to assure new code is on drive.\n')
         from Serial_Download import CDnldCode
         oDownload = CDnldCode(self.dut, {'CODES': ['CFW', 'S_OVL'],})
         oDownload.run()
         # New code on the drive requires a re-init of the drive info.
         oDrvInfo = CInit_DriveInfo(self.dut,self.params)
         oDrvInfo.run()

      if self.dut.nextOper in ['FNC2', 'CRT2', 'MQM2']:
         self.dut.driveattr['SPMQM_TIME'] = 0.0
         objMsg.printMsg("SPMQM_TIME = %s" % self.dut.driveattr['SPMQM_TIME'])

      if testSwitch.NoIO and self.dut.nextOper in ['FIN2', 'CUT2', 'FNG2']:
         self.dut.SkipPCycle = True

         self.dut.readyTimeLimit = None   # set to NONE to trigger TTRLimit checking
         objMsg.printMsg("Updated objPwrCtrl.readyTimeLimit : %s Msec" % objPwrCtrl.readyTimeLimit) #This will trigger TTRLimit checking

         if testSwitch.SP_RETRY_WORKAROUND:
            self.dut.driveattr['PROC_CTRL12'] = '0'
            self.dut.driveattr['PROC_CTRL13'] = '0'

         from sptCmds import sendDiagCmd
         sendDiagCmd(CTRL_Z, printResult = False)
         sendDiagCmd("/FY2,,,,10000000018", printResult = True)

         from serialScreen import sptDiagCmds      
         oSerial = sptDiagCmds()  
         self.dut.imaxHead = int(oSerial.GetCtrl_L()['Heads'])
         objMsg.printMsg("Setting imaxHead to %d" % self.dut.imaxHead)

         objMsg.printMsg('base_SerialTest.py IdentifyDevice')
         from IntfClass import CIdentifyDevice
         oIdentifyDevice = CIdentifyDevice()
         oIdentifyDevice.check_dutID_syID()
         ICmd.SPGetMaxLBA()

         ret = oIdentifyDevice.ID # read device settings with identify device
         jumper_detect = 'SATA_NO_JMPR'

         if ret['SATACapabilities'] & 0x04:     # check bit 3
            objMsg.printMsg("Drive is SATA2")
            jumper_detect = 'SATA_NO_JMPR'

         elif ret['SATACapabilities'] & 0x02:   # check bit 2
            objMsg.printMsg("Drive is SATA1")
            if not testSwitch.WA_0121440_7955_FORCE_SATA_NO_JMPR:
               jumper_detect = 'SATA_JMPR_ON'

         objMsg.printMsg("jumper_detect = %s" %jumper_detect)
         self.dut.driveattr['JUMPER_SET'] = jumper_detect

         #Record the drive's POIS status
         if oIdentifyDevice.Is_POIS_Supported() and oIdentifyDevice.Is_POIS():
            ConfigVars[CN].update({'Power On Set Feature':'ON'})
            self.dut.driveattr['POWER_ON_TYPE']="PWR_ON_IN_STDBY"
            objMsg.printMsg("Setting POWER_ON_TYPE attribute to PWR_ON_IN_STDBY")
         else:
            self.dut.driveattr['POWER_ON_TYPE']="POIS_DISABLED"
            objMsg.printMsg("Setting POWER_ON_TYPE attribute to POIS_DISABLED")

      if testSwitch.FE_0271705_509053_NO_WAIT_FOR_SATAPHY_READY_UNDER_LOOPBACK and self.dut.nextOper in ['FNC2', 'CRT2', 'FIN2', 'CUT2']:
         # SATA port Loop back WA for PSTR (F3 code)
         self.F3SataCheckLoopDisableWA()

   #-------------------------------------------------------------------------------------------------------
   def autoSeaSerialRetry(self, ec, forceseaserial = 0):
      if testSwitch.FE_0132468_357260_AUTO_SEASERIAL_FOR_CHECKSUM_MISMATCH:
         if self.dut.nextOper in ["PRE2", "SCOPY"] and ((ec in [11087, 10340, 12383, 39173, 38912] and ConfigVars[CN].get("AUTO_SEASERIAL", 0)) or forceseaserial):
            try:
               from Serial_Download import CFLS_LOAD
               seaserial = CFLS_LOAD(self.dut)
               return seaserial.run(ReadBootPCBASN = False)
            except:
               objMsg.printMsg("Auto-Seaserial Failed: %s" % traceback.format_exc())
               raise
         else:
            raise
      else:
         if self.dut.nextOper in ["PRE2", "SCOPY"] and ((ec in [11087, 10340, 12383, 39173] and ConfigVars[CN].get("AUTO_SEASERIAL", 0)) or forceseaserial):
            try:
               from Serial_Download import CFLS_LOAD
               seaserial = CFLS_LOAD(self.dut)
               return seaserial.run(ReadBootPCBASN = False)
            except:
               objMsg.printMsg("Auto-Seaserial Failed: %s" % traceback.format_exc())
               raise
         else:
            raise
   #-------------------------------------------------------------------------------------------------------
   def FDE_Unlock_Retry(self,ec):

      if (ec in [11087, 10340]):
         if objRimType.isIoRiser() and \
            (((self.dut.drvIntf in TP.WWN_INF_TYPE.get('WW_SAS_ID', []) or self.dut.drvIntf == 'SAS') and \
            testSwitch.FE_0151360_231166_P_ADD_SUPPORT_SAS_SED_CRT2_UNLK) or \
            (testSwitch.NSG_TCG_OPAL_PROC and self.dut.nextOper == "CRT2")) :

            if self.dut.driveattr['FDE_DRIVE'] == 'FDE':
               from CustomCfg import CCustomCfg
               from Rim import theRim

               # CustConfig = CCustomCfg()
               # CustConfig.getDriveConfigAttributes()

               objPwrCtrl.powerCycle(ataReadyCheck = 'force')

               if objRimType.IOInitRiser():
                  theRim.EnableInitiatorCommunication(objComMode)

               from TCG import CTCGPrepTest
               oTCG = CTCGPrepTest(self.dut)
               try:
                  oTCG.InitTrustedTCG()

                  try:
                     objComMode.setMode(objComMode.availModes.intBase)
                     if objRimType.IOInitRiser():
                        theRim.powerCycleRim()
                     objPwrCtrl.powerCycle()
                  except:
                     import base_BaudFunctions
                     base_BaudFunctions.changeBaud(PROCESS_HDA_BAUD)

                  if not testSwitch.NSG_TCG_OPAL_PROC:
                     self.dut.objData['TCG_ADD_UNLK'] = True
               except:
                  objMsg.printMsg(traceback.format_exc())
                  raise

         else:
            # from CustomCfg import CCustomCfg
            # CustConfig = CCustomCfg()
            # CustConfig.getDriveConfigAttributes()


            from TCG import CTCGPrepTest
            oTCG = CTCGPrepTest(self.dut)
            try:
               objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
               oTCG.InitTrustedTCG()

               if not testSwitch.NSG_TCG_OPAL_PROC:
                  self.dut.objData['TCG_ADD_UNLK'] = True
            except:
               objMsg.printMsg(traceback.format_exc())
               raise

   #-------------------------------------------------------------------------------------------------------
   def RerunTODT(self):
      if self.dut.driveattr['TODT_DEF'] == 'H' and self.dut.driveattr['PART_NUM'][6:] not in ['-301']:
         objMsg.printMsg('Not allow to rerun, the system block the hard EC to key customer')
         ScrCmds.raiseException(22333, 'Hard Defect - cannot rerun')
         
   #-------------------------------------------------------------------------------------------------------
   if testSwitch.WA_0264977_321126_WAIT_UNTIL_DST_COMPLETION:
      def DSTCheck(self): 
         try:
            timeout = 30
            #timeout = int(self.dut.objData.retrieve('dst'))
            ScrCmds.statMsg("dst retrieved=%s" % timeout)
            if timeout > 0:
               if objRimType.isNeptuneRiser():
                  ScriptComment('Call DisableStaggeredStart')
                  DisableStaggeredStart(True)
               from Cell import theCell
               theCell.powerOff(10)
               theCell.powerOn(5000,12000,10)

               try:
                  import sptCmds
                  sptCmds.enableDiags()               
                  sptCmds.sendDiagCmd('/1NF', timeout = 120, printResult = True) # abort DST from PLR
                  return #able to abort DST successfully
               except:
                  # if /1NF is unsupported, drive will return "DiagError 0000000A", EC10253
                  objMsg.printMsg("catch exception:\n%s" % traceback.format_exc())
                  objMsg.printMsg("unable to abort DST... proceed to wait for DST to complete")
                  try:
                     sptCmds.execOnlineCmd(CTRL_R)
                     objMsg.printMsg('Pass CtrlR')
                  except:
                     pass

               objMsg.printMsg('Sleeping %s s...' % timeout)
               import time
               time.sleep(timeout)         
         except:
            objMsg.printMsg("DSTCheck exception:\n%s" % traceback.format_exc())
            pass

   #-------------------------------------------------------------------------------------------------------
   # SATA port Loop back WA for PSTR (F3 code)
   def F3SataCheckLoopDisableWA(self):
      try:
         self.F3SataCheckLoopWA("DD",0xDD)
      except:
         pass

   #-------------------------------------------------------------------------------------------------------
   def F3SataCheckLoopEnableWA(self):
      try:
         self.F3SataCheckLoopWA("FF",0xFF)
      except:
         pass

   #-------------------------------------------------------------------------------------------------------   
   def F3SataCheckLoopWA(self, value_str, value_hex):
      if self.dut.sptActive.getMode() in [self.dut.sptActive.availModes.sptDiag, self.dut.sptActive.availModes.intBase]:
         from sptCmds import sendDiagCmd
         sendDiagCmd('/TJ%s,1B,1'%value_str,timeout = 100, altPattern = '>', printResult = True, stopOnError = False, raiseException = False)
         sendDiagCmd('W,,22'   ,timeout = 100, altPattern = '>', printResult = True, stopOnError = False, raiseException = False)
      elif self.dut.sptActive.getMode() == self.dut.sptActive.availModes.mctBase:
         if testSwitch.TRUNK_BRINGUP:
            addrNoWaitForSataPHYReady = 467 / 2
         else:
            addrNoWaitForSataPHYReady = 395 / 2

         SetFailSafe()
         from Process import CProcess
         objProc = CProcess()
         objProc.St({'test_num':178,'prm_name':'CAP_NO_WAIT_FOR_SATAPHY_READY_UNDER_LOOPBACK','CWORD1':0x120, 'CAP_WORD':(addrNoWaitForSataPHYReady,value_hex << 8,0xFF00)})
         ClearFailSafe()

#----------------------------------------------------------------------------------------------------------
class CTurnOnMasterHeat(CState):
   """
   turn on master heat
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      #self.oSrvOpti = CServoOpti()
      from FSO import CFSO      
      oFSO = CFSO()
      objMsg.printMsg("Turn on Master Heat.")

      # Set to dis-allow access to FAFH Zones at end of STATE
      if testSwitch.IS_FAFH: 
         CFSO().St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value
         CFSO().St(TP.DisallowFAFH_AccessBit_178) # Dis-allow FAFH access after completing servo test
         CFSO().St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value

      # re-enable Master Heat if it was previously enabled
      #if MHBit == 1:
      CFSO().St(TP.masterHeatPrm_11['enable'])
      CFSO().St(TP.masterHeatPrm_11['saveSAP'])
      CFSO().St(TP.masterHeatPrm_11['read'])
         

#----------------------------------------------------------------------------------------------------------
class CSetupProc(CState):
   """
      Sets up process related stuff
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

      from Servo import CServoFunc
      self.oSrvFunc = CServoFunc()

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from FSO import CFSO
      self.oFSO = CFSO()
      self.dut.appendHDResultsFile = 0

      objMsg.printMsg("depopMask==>%s" %str(self.dut.depopMask))
      self.dut.globaldepopMask = self.dut.depopMask
      objMsg.printMsg("globaldepopMask==>%s" %str(self.dut.globaldepopMask))

      objMsg.printMsg('self.dut.depopMask  : %s' % str(self.dut.depopMask), objMsg.CMessLvl.IMPORTANT)
      if testSwitch.FE_0148166_381158_DEPOP_ON_THE_FLY:
         #Set physical max head to CAP so as  the T86 will check against max_head
         numPhysHds = self.dut.Servo_Sn_Prefix_Matrix[self.dut.serialnum[1:3]]['PhysHds']
         if self.dut.depopMask != []:
            self.oSrvFunc.St({'test_num':178,'prm_name':'CAP_HD_COUNT','HD_COUNT':numPhysHds,'CWORD1':0x120})#
            self.oSrvFunc.St({'test_num':178,'prm_name':'SAP_SN','MAX_HEAD':numPhysHds-1,'SAP_HDA_SN': (),'CWORD1':0x420})
            self.oFSO.getZoneTable(newTable = 1, delTables = 1)

      #=== Set family info
      self.oFSO.setFamilyInfo(TP.familyInfo,TP.famUpdatePrm_178,self.dut.depopMask, runDepop = 1)

      #===Get Physical DRAM szie
      from DRamScreen import CPCBA
      oPCBA = CPCBA(self.dut)
      oPCBA.getPhysicalDramSize()

      #=== Initialize Drive Info
      oDrvInfo = CInit_DriveInfo(self.dut)
      oDrvInfo.run(force = 1)

      #=== Display of ATB settings - fail drive if cannot find match
      if testSwitch.FE_348429_0247869_TRIPLET_INTEGRATED_ATISTE:
         objMsg.printMsg('ATB Settings for (%s, %s) (%s, %s)' % (self.dut.HGA_SUPPLIER, self.dut.PREAMP_TYPE, self.dut.MediaType, self.dut.HSA_WAFER_CODE))
         try:
            IwMax = TP.IwMaxCap
            OaMax = TP.OaMaxCap
            IwMin = TP.IwMinCap
         except:
            ScrCmds.raiseException(11044, "IwMaxCap, OaMaxCap or IwMinCap not defined!!")
         objMsg.printMsg('IwMaxCap = %s' % str(IwMax))
         objMsg.printMsg('OaMaxCap = %s' % str(OaMax))
         objMsg.printMsg('IwMinCap = %s' % str(IwMin))
         if not testSwitch.FE_0334525_348429_INTERPOLATED_DEFAULT_TRIPLET:
            objMsg.printMsg('Default Triplets = %s' % str(TP.VbarWpTable[self.dut.PREAMP_TYPE]['ALL'][2]))
         else:
            try:
               objMsg.printMsg('Default Triplets = %s' % str(TP.VbarWpTable[self.dut.PREAMP_TYPE]['ALL'][2]))
            except:
               objMsg.printMsg('Default Triplets OD = %s ID = %s' % (str(TP.VbarWpTable[self.dut.PREAMP_TYPE]['OD'][2]),str(TP.VbarWpTable[self.dut.PREAMP_TYPE]['ID'][2])))
               pass
         if len(IwMax) != len(OaMax):
            ScrCmds.raiseException(11044, "IwMaxCap and OaMaxCap have different length!!")
         if len(IwMax) > len(IwMin) and not testSwitch.FE_0332552_348429_TRIPLET_INTEGRATED_OW_HMS:
            ScrCmds.raiseException(11044, "Length of IwMaxCap > IwMinCap !!")

      #=== Set head type if SET_HEAD_SUPPLIER_IN_SAP is set
      self.oSrvFunc.setSAP_HeadType(self.dut.HGA_SUPPLIER)
      if testSwitch.FE_0112760_399481_POWER_CYCLE_AFTER_SET_HEAD_SUPPLIER_IN_SAP:
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

      #=== Variable OST
      if testSwitch.VARIABLE_OST:
         #self.dut.arcTPI must be populated prior to this
         self.dut.OST = self.oSrvFunc.getOSTRatio(TP.ReadPVDDataPrm_11, TP.getServoSymbolPrm_11, TP.getSymbolViaAddrPrm_11 )
         self.oFSO.saveSAPtoFLASH()

      #=== Holliday: Update and save SAP
      if testSwitch.HOLLIDAY_SINGLE_CODE_SET:
         self.updateSAP_Holliday()

      #=== Set OCLIM in memory only
      self.oSrvFunc.setOClim({},TP.defaultOCLIM)

      #=== Enable RV sensor
      if testSwitch.FE_0246017_081592_ENABLE_RV_SENSOR_IN_CERT_PROCESS:
         objMsg.printMsg('Enable RV sensor')
         self.oSrvFunc.setSPLVFF(enable = True)

      if testSwitch.extern._128_REG_PREAMPS:
         self.updatePREAMP_reg0B()      # temp solution before default correct it

      if (testSwitch.CHENGAI or testSwitch.M10P) and self.dut.HGA_SUPPLIER in ['TDK', 'HWY']:
         self.updateWriteCurrRiseTime()
      if (testSwitch.CHENGAI or testSwitch.M10P) and self.dut.HGA_SUPPLIER in ['RHO']:
         self.updateWriteZout()

      if 'LSI2935' in self.dut.PREAMP_TYPE and self.dut.HGA_SUPPLIER in ['TDK', 'HWY']:
         objMsg.printMsg('Change Preamp Rise Time')
         self.ChangePreampRising()

      objMsg.printMsg('AGC_SCRN_DESTROKE_WITH_NEW_RAP = %s' % str(testSwitch.AGC_SCRN_DESTROKE_WITH_NEW_RAP), objMsg.CMessLvl.IMPORTANT)

      if (testSwitch.AGC_SCRN_DESTROKE_WITH_NEW_RAP and not testSwitch.CHENGAI):  # temp workaround 23/8/13
         self.oSrvFunc.St({'test_num':11, 'prm_name':'Copy VTPI setting from RAP to SAP RAM', 'CWORD1':0x8001})
         self.oFSO.saveSAPtoFLASH()
         if self.dut.driveattr['DESTROKE_REQ'] == 'DSD_NEW_RAP':
            self.oSrvFunc.St(TP.MAX_NOMINAL_VTPI_CYL_WITH_DESTROKE_Prm_11['read'])
            self.oSrvFunc.St(TP.MAX_NOMINAL_VTPI_CYL_WITH_DESTROKE_Prm_11['enable'])
            self.oSrvFunc.St(TP.MAX_NOMINAL_VTPI_CYL_WITH_DESTROKE_Prm_11['saveSAP'])
            self.oSrvFunc.St(TP.MAX_NOMINAL_VTPI_CYL_WITH_DESTROKE_Prm_11['read'])
      #=== Disable here and enable after full zap is called
      self.oSrvFunc.setZonedACFF(enable = False)
      self.oSrvFunc.setLVFF(enable = False)
      if testSwitch.FE_0123391_357915_DISABLE_ADAPTIVE_ANTI_NOTCH_UNTIL_AFTER_ZAP:
         self.oSrvFunc.setAdaptiveAntiNotch(enable = False)
      #===Toggling a SAP bit Servo Filter based upon the PCBA part number
      if testSwitch.WA_0126043_426568_TOGGLE_SAPBIT_FOR_HIGH_BW_FILTER :
         self.oSrvFunc.PCBAsetting(TP.pcba_nums, 'FILTER')
      #=== Modify the SWOT sensor
      if testSwitch.FE_0124846_357915_SWOT_SENSOR_SUPPORT: # Enable to allow process to modify the servo SAP SWOT sensor bit
         if testSwitch.FE_0124846_357915_ENABLE_SWOT_SENSOR or ConfigVars[CN].get('enableSwotSensor', 0):
            self.oSrvFunc.setSwotSensor(enable = True)
         else: # Disable the SWOT sensor
            self.oSrvFunc.setSwotSensor(enable = False)
      #=== Set Servo trk 0 value
      if testSwitch.FE_0281621_305538_SET_SERVO_TRK_0_VALUE:
         #=== Report misc info
         try:
            servoTrk0 = self.oFSO.readServoTrackInfo()
            objMsg.printMsg('servoTrk0 retrieved from RAP = %d' % servoTrk0)
            if servoTrk0 == 0xFFFF: # invalid value, so set to default
               servoTrk0 = 10000
            else:
               servoTrk0 -= 6630 # might need to change this depending on input from RSS/Servo
               if servoTrk0 < 10000: # let's arbitrarily set minimum servo trk to 9000 - 26/2: increase to 10k for CheopsAM
                  servoTrk0 = 10000
         except:
            servoTrk0 = 10000
         objMsg.printMsg('servoTrk0 to set to SAP = %d' % servoTrk0)
         # objMsg.printMsg('Original TRK_0 Values')
         # self.oSrvFunc.getServoSymbolRange('SERVO_TRACK_0_VALUE', 4 )   # read 4 values for each head
         self.oSrvFunc.setServoSymbolRange('SERVO_TRACK_0_VALUE', servoTrk0, 4)   # update 4 values for each head
         objMsg.printMsg('Updated TRK_0 Values')
         self.oSrvFunc.getServoSymbolRange('SERVO_TRACK_0_VALUE', 4 )   # read 4 values for each head

      #=== Report code info
      self.oFSO.reportFWInfo()

      #=== Jumper detection
      if testSwitch.jumperdetect == 1:
         self.oSrvFunc.St(TP.jumper_detect_003)

      #=== Put any rapRev modifications below
      if self.dut.driveattr.get('RAP_REV',0) in []:
         pass

      testSwitch.FE_0309959_348085_P_DEFAULT_580KTPI_FOR_DATA_TRACK_SUPPORT = ( TP.Default_TPI_Format < 1.0 )
      objMsg.printMsg('FE_0309959_348085_P_DEFAULT_580KTPI_FOR_DATA_TRACK_SUPPORT = %d' % testSwitch.FE_0309959_348085_P_DEFAULT_580KTPI_FOR_DATA_TRACK_SUPPORT)

      #=== Reset formats to nominal picks
      # Ensures that the right BPIFile tables and serpent size are loaded
      if testSwitch.extern.FE_0119825_208705_DYNAMIC_SERPENT_SIZE:
         from VBAR import CReloadBPINominal
         CReloadBPINominal().setFormats()

      #=== Get Servo Chip ID
      self.oSrvFunc.getServoChipID()

      #=== Program the UMP zones
      if testSwitch.FE_0284435_504159_P_VAR_MC_UMP_ZONES and testSwitch.FE_348085_P_NEW_UMP_MC_ZONE_LAYOUT:
         TP.UMP_ZONE    = TP.UMP_ZONE_BY_HEAD[self.dut.imaxHead].copy()
         ump_start_zone = min(TP.UMP_ZONE[self.dut.numZones])
         num_ump_zone   = len(TP.UMP_ZONE[self.dut.numZones])-1
         objMsg.printMsg('TP.MC_ZONE %s' % str(TP.MC_ZONE))
         num_mc_zone    = len(TP.MC_ZONE) 
         self.oFSO.updateUMP_MC_Zone(ump_start_zone, num_ump_zone, num_mc_zone)
      elif testSwitch.FE_0284435_504159_P_VAR_MC_UMP_ZONES:
         TP.UMP_ZONE    = TP.UMP_ZONE_BY_HEAD[self.dut.imaxHead].copy()
         ump_start_zone = min(TP.UMP_ZONE[self.dut.numZones])
         num_ump_zone   = len(TP.UMP_ZONE[self.dut.numZones])-1
         self.oFSO.updateUMP_Zone(ump_start_zone, num_ump_zone)

      if testSwitch.FE_0303934_517205_SET_OVERSHOOT_PARAM_AT_SETUP_PROC:
         self.oSrvFunc.St({'test_num':172,'prm_name': 'P172_OVERSHOOT_PARAM','timeout': 1000,'CWORD1': 43})
         self.oSrvFunc.St(TP.prm_wooT178) #Update Write Current Rise Time, Overshoot Rise Time Overshoot Fall Time Values
         self.oSrvFunc.St({'test_num':178,'prm_name': 'Save RAP in RAM to FLASH','timeout': 1000,'CWORD1': 544})
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1) 
         self.oSrvFunc.St({'test_num':172,'prm_name': 'P172_OVERSHOOT_PARAM','timeout': 1000,'CWORD1': 43})

      if testSwitch.extern.SFT_TEST_0078 and testSwitch.ENABLE_PREAMP_DIE_TEMPERATURE_RECENTER:
         try:
            self.oSrvFunc.St({'test_num':78,'prm_name': 'P078_PREAMP_DIE_TEMPERATURE_RECENTER','timeout': 1000})
         except:
            pass
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1) 
      if testSwitch.extern.FE_0366862_322482_CERT_DETCR_LIVE_SENSOR:
         from base_TccCal import CTccCalibration
         self.oTccCal = CTccCalibration(self.dut)
         self.oTccCal.saveThresholdToHap(20)
         #self.oFSO.St(TP.enableTASensor_11)
         self.oFSO.St(TP.enableLiveSensor_11)
         self.oFSO.saveSAPtoFLASH()

   #-------------------------------------------------------------------------------------------------------
   def updatePREAMP_reg0B(self):
      import struct
      from Process import CCudacom
      self.oOudacom = CCudacom()

      #read reg08 before change
      buf, errorCode = self.oOudacom.Fn(1391, 0x0B, 0)        # read
      if not testSwitch.virtualRun:
         if testSwitch.FE_0284269_228371_SUPPORT_CL794987_NEW_PREAMP_WR_CMD:
            bufBytes = struct.unpack('HH',buf)
         else:
            bufBytes = struct.unpack('BB',buf)
      else: bufBytes = [0x15, 0]
      if testSwitch.FE_0284269_228371_SUPPORT_CL794987_NEW_PREAMP_WR_CMD & (not testSwitch.virtualRun) :
         objMsg.printMsg('PRE-Preamp register 0x0B = 0x%X.' % bufBytes[1])
      else:
         objMsg.printMsg('PRE-Preamp register 0x0B = 0x%X.' % (bufBytes[0] + bufBytes[1]<<8))
      buf, errorCode = self.oOudacom.Fn(1392, 0x0B, 0x0600, 0)  # write

      buf, errorCode = self.oOudacom.Fn(1391, 0x0B, 0)        # read
      if not testSwitch.virtualRun:
         if testSwitch.FE_0284269_228371_SUPPORT_CL794987_NEW_PREAMP_WR_CMD:
            bufBytes = struct.unpack('HH',buf)
         else:
            bufBytes = struct.unpack('BB',buf)
      else: bufBytes = [0x6, 0]
      if testSwitch.FE_0284269_228371_SUPPORT_CL794987_NEW_PREAMP_WR_CMD & (not testSwitch.virtualRun):
         objMsg.printMsg('POST-Preamp register 0x0B = 0x%X.' % bufBytes[1])
      else:
         objMsg.printMsg('POST-Preamp register 0x0B = 0x%X.' % (bufBytes[0] + bufBytes[1]<<8))

   #-------------------------------------------------------------------------------------------------------
   def updateSAP_Holliday(self):
      #=== Do not spin up drive
      saveSetting = objDut.mdwCalComplete
      objDut.mdwCalComplete = 1

      #=== If RHO head, set bit 5.
      if not testSwitch.TDK_HEAD:
         self.oSrvFunc.St(TP.setHeadTypeBit5Prm_11)

      #=== If 2-disc, set number of disc to 2 and update notch table.
      sn = self.dut.serialnum[1:3]
      if sn in TP.TwoDiscSerialNumber:
         self.oSrvFunc.St(TP.setNumOfDiscPrm_11)
         self.oSrvFunc.UpdateNotchCoeff()

      #=== Save SAP to FLASH
      self.oFSO.saveSAPtoFLASH()

      #=== Read back data
      self.oSrvFunc.St(TP.getHeadTypePrm_11)
      self.oSrvFunc.St(TP.getNumOfDiscPrm_11)
      self.oSrvFunc.St(TP.getNotchCoeffPrm_152)

      #=== Restore mdwCalComplete
      objDut.mdwCalComplete = saveSetting

   #-------------------------------------------------------------------------------------------------------
   def enableTornWriteProtection(self):
      self.oSrvFunc.St(TP.tornWritePrm_11['read'])
      tnWrtVal = int(self.dut.dblData.Tables('P011_SV_RAM_RD_BY_OFFSET').tableDataObj()[-1]['READ_DATA'],16)
      if tnWrtVal & TP.tornWritePrm_11['enable']['WR_DATA']:
         objMsg.printMsg("TornWrite Protection enabled already ")
      else:
         self.oSrvFunc.St(TP.tornWritePrm_11['enable'])
         self.oSrvFunc.St(TP.tornWritePrm_11['saveSAP'])
         self.oSrvFunc.St(TP.tornWritePrm_11['read'])
         tnWrtVal = int(self.dut.dblData.Tables('P011_SV_RAM_RD_BY_OFFSET').tableDataObj()[-1]['READ_DATA'],16)
         if tnWrtVal & TP.tornWritePrm_11['enable']['WR_DATA']:
            objMsg.printMsg("Torn Write Protection enabled now ")
         else:
            objMsg.printMsg("Failed to enable TornWrite Protection, please make sure servo code support TornWrite ")
            raise

   #-------------------------------------------------------------------------------------------------------
   def ChangeOsRangetoHalf(self):
      self.oSrvFunc.St(TP.OsRangePrm_11['read'])
      self.oSrvFunc.St(TP.OsRangePrm_11['enable'])
      self.oSrvFunc.St(TP.OsRangePrm_11['saveSAP'])
      self.oSrvFunc.St(TP.OsRangePrm_11['read'])

   #-------------------------------------------------------------------------------------------------------
   def updateWriteCurrRiseTime(self):
      self.oSrvFunc.St(TP.IwRiseTimePrm_11['read'])
      if self.dut.PREAMP_TYPE in ['LSI5231','LSI5830']:
         IwRiseTime = int(self.dut.dblData.Tables('P011_SV_RAM_RD_BY_OFFSET').tableDataObj()[-1]['READ_DATA'],16)
         if IwRiseTime&(~TP.IwRiseTimePrm_11['IwRiseTime_lsi']['MASK_VALUE']&0xFFFF) == TP.IwRiseTimePrm_11['IwRiseTime_lsi']['WR_DATA']:
            objMsg.printMsg("same rise time already")
         else:
            self.oSrvFunc.St(TP.IwRiseTimePrm_11['IwRiseTime_lsi'])
            self.oSrvFunc.St(TP.IwRiseTimePrm_11['saveSAP'])
            self.oSrvFunc.St(TP.IwRiseTimePrm_11['read'])
            IwRiseTime = int(self.dut.dblData.Tables('P011_SV_RAM_RD_BY_OFFSET').tableDataObj()[-1]['READ_DATA'],16)
            if IwRiseTime&(~TP.IwRiseTimePrm_11['IwRiseTime_lsi']['MASK_VALUE']&0xFFFF) == TP.IwRiseTimePrm_11['IwRiseTime_lsi']['WR_DATA']:
               objMsg.printMsg("riase time is %d " % (IwRiseTime&(~TP.IwRiseTimePrm_11['IwRiseTime_lsi']['MASK_VALUE']&0xFFFF)))
            else:
               objMsg.printMsg("Failed to update rise time")
               raise
      elif self.dut.PREAMP_TYPE in ['TI7550','TI7551']:
         IwRiseTime = int(self.dut.dblData.Tables('P011_SV_RAM_RD_BY_OFFSET').tableDataObj()[-1]['READ_DATA'],16)
         if IwRiseTime&(~TP.IwRiseTimePrm_11['IwRiseTime_ti']['MASK_VALUE']&0xFFFF) == TP.IwRiseTimePrm_11['IwRiseTime_ti']['WR_DATA']:
            objMsg.printMsg("same rise time already")
         else:
            self.oSrvFunc.St(TP.IwRiseTimePrm_11['IwRiseTime_ti'])
            self.oSrvFunc.St(TP.IwRiseTimePrm_11['saveSAP'])
            self.oSrvFunc.St(TP.IwRiseTimePrm_11['read'])
            IwRiseTime = int(self.dut.dblData.Tables('P011_SV_RAM_RD_BY_OFFSET').tableDataObj()[-1]['READ_DATA'],16)
            if IwRiseTime&(~TP.IwRiseTimePrm_11['IwRiseTime_ti']['MASK_VALUE']&0xFFFF) == TP.IwRiseTimePrm_11['IwRiseTime_ti']['WR_DATA']:
               objMsg.printMsg("riase time is %d " % (IwRiseTime&(~TP.IwRiseTimePrm_11['IwRiseTime_ti']['MASK_VALUE']&0xFFFF)))
            else:
               objMsg.printMsg("Failed to update rise time")
               raise

   #-------------------------------------------------------------------------------------------------------
   def updateWriteZout(self):
      self.oSrvFunc.St(TP.WrtZoutPrm_11['read'])
      if self.dut.PREAMP_TYPE in ['LSI5231','LSI5830']:
         WrtZout = int(self.dut.dblData.Tables('P011_SV_RAM_RD_BY_OFFSET').tableDataObj()[-1]['READ_DATA'],16)
         if WrtZout&(~TP.WrtZoutPrm_11['wrt_lsi']['MASK_VALUE']&0xFFFF) == TP.WrtZoutPrm_11['wrt_lsi']['WR_DATA']:
            objMsg.printMsg("same write Zout already")
         else:
            self.oSrvFunc.St(TP.WrtZoutPrm_11['wrt_lsi'])
            self.oSrvFunc.St(TP.WrtZoutPrm_11['saveSAP'])
            self.oSrvFunc.St(TP.WrtZoutPrm_11['read'])
            WrtZout = int(self.dut.dblData.Tables('P011_SV_RAM_RD_BY_OFFSET').tableDataObj()[-1]['READ_DATA'],16)
            if WrtZout&(~TP.WrtZoutPrm_11['wrt_lsi']['MASK_VALUE']&0xFFFF) == TP.WrtZoutPrm_11['wrt_lsi']['WR_DATA']:
               objMsg.printMsg("write Zout is %s " % (WrtZout&(~TP.WrtZoutPrm_11['wrt_lsi']['MASK_VALUE']&0xFFFF)))
            else:
               objMsg.printMsg("Failed to update write Zout")
               raise
      #elif 'TI7550' in self.dut.PREAMP_TYPE:
      #   WrtZout = int(self.dut.dblData.Tables('P011_SV_RAM_RD_BY_OFFSET').tableDataObj()[-1]['READ_DATA'],16)
      #   if WrtZout&(~TP.WrtZoutPrm_11['wrt_ti']['MASK_VALUE']&0xFFFF) == TP.WrtZoutPrm_11['wrt_ti']['WR_DATA']:
      #      objMsg.printMsg("same write Zout already")
      #   else:
      #      self.oSrvFunc.St(TP.WrtZoutPrm_11['wrt_ti'])
      #      self.oSrvFunc.St(TP.WrtZoutPrm_11['saveSAP'])
      #      self.oSrvFunc.St(TP.WrtZoutPrm_11['read'])
      #      WrtZout = int(self.dut.dblData.Tables('P011_SV_RAM_RD_BY_OFFSET').tableDataObj()[-1]['READ_DATA'],16)
      #      if WrtZout&(~TP.WrtZoutPrm_11['wrt_ti']['MASK_VALUE']&0xFFFF) == TP.WrtZoutPrm_11['wrt_ti']['WR_DATA']:
      #         objMsg.printMsg("write Zout is %d ", (WrtZout&(~TP.WrtZoutPrm_11['wrt_ti']['MASK_VALUE']&0xFFFF)))
      #      else:
      #         objMsg.printMsg("Failed to update write Zout")
      #         raise

   #-------------------------------------------------------------------------------------------------------
   def ChangePreampRising(self):
      self.oSrvFunc.St(TP.preampRisingPrm_11['read'])
      self.oSrvFunc.St(TP.preampRisingPrm_11['enable'])
      self.oSrvFunc.St(TP.preampRisingPrm_11['saveSAP'])
      self.oSrvFunc.St(TP.preampRisingPrm_11['read'])


#----------------------------------------------------------------------------------------------------------
class CInit_DriveInfo(CState):
   """
      Initialize dut variables to be used in the process.  For example testparamExtractor indexes testparameters
      by self.dut.servoWedges.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self, force = 0):
      from FSO import CFSO
      from Servo import CServoFunc
      if testSwitch.FE_0124304_231166_FAIL_IF_NO_FLAG_FILE_FOUND:
         from Utility import permutations
      self.oFSO = CFSO()
      self.oSrvFunc = CServoFunc()

      force = self.params.get('FORCE', force)

      if self.dut.sptActive.getMode() == self.dut.sptActive.availModes.mctBase:
         if force or not self.dut.GotDrvInfo:
            objMsg.printMsg("Initializing Drive Info", objMsg.CMessLvl.IMPORTANT)
            if self.dut.nextState == 'INIT' and self.dut.nextOper == 'PRE2':
               #Set this to a non-oracle load as it is an invalid reference
               spc_id = -1
            else:
               spc_id = 1

            if testSwitch.UPS_PARAMETERS:
               # Try to setup UPS
               #  - Only here if SF3 on drive
               #  - This next call does not fail if drive does not support UPS
               upsObj.setupUPS()

            self.oFSO.reportFWInfo(spc_id = spc_id)
            try:
               if testSwitch.winFOF:
                  # For Bench runs, cases where the reported package does not match the manifest file name, just use the flags
                  # file from available manifest file.  FW built with bincheck-1 reports '0' information but package
                  # naming may still be correctly named (no 0's).  Handling that case here.
                  from PackageResolution import PackageDispatcher
                  pd = PackageDispatcher(self.dut, codeType = 'CFW' )
                  fileName = pd.getFileName()
                  pd.setFlagFileName()
                  testSwitch.importExternalFlags(pd.flagFileName)
               elif testSwitch.FE_0126871_231166_ROBUST_PCK_COMP_SEARCH:
                  packageName = self.dut.dblData.Tables('P166_SELFTEST_PACKAGENAME').tableDataObj()[-1]['PACKAGE_NAME']
                  buildTarget = self.dut.dblData.Tables('P166_SELFTEST_PACKAGENAME').tableDataObj()[-1]['BUILD_TYPE']
                  cl = self.dut.dblData.Tables('P166_SELFTEST_PACKAGENAME').tableDataObj()[-1]['CHANGE_LIST']

                  if 'GID' in self.dut.dblData.Tables('P166_SELFTEST_PACKAGENAME').tableDataObj()[-1]:
                     gid = self.dut.dblData.Tables('P166_SELFTEST_PACKAGENAME').tableDataObj()[-1]['GID']
                  elif 'BUILDER_ID' in self.dut.dblData.Tables('P166_SELFTEST_PACKAGENAME').tableDataObj()[-1]:
                     # set gid to Builder ID if GID column doesn't exist, this is a code from before we
                     # deprecated the Builder ID in favor of the GID
                     gid = self.dut.dblData.Tables('P166_SELFTEST_PACKAGENAME').tableDataObj()[-1]['BUILDER_ID']


                  if testSwitch.WA_0141609_231166_P_NO_FLG_MATCH_GID:
                     packageName  = '.'.join((packageName, buildTarget, cl)).replace("'", "")
                  else:
                     packageName  = '.'.join((packageName, buildTarget, cl, gid)).replace("'", "")
                  result = self.updateFlagFile(packageName, regex = False)

                  if not result:
                     if testSwitch.FE_0124304_231166_FAIL_IF_NO_FLAG_FILE_FOUND:
                        #we didn't find a match then fail unless we are in PRE2 and state is INIT- at this point
                        # it is unlikely that any codes will match and we actually don't care as the code MUST go through
                        # download in masspro
                        if (self.dut.nextState == 'INIT' and self.dut.nextOper == 'PRE2') or testSwitch.virtualRun:
                           objMsg.printMsg("Failed to set FLG file with %s" % packageName)
                        else:
                           ScrCmds.raiseException(11043, "Failed to set FLG file with %s" % packageName)
                     else:
                        objMsg.printMsg("Failed to set FLG file with %s" % packageName)


               else:
                  P166SF3PackageTbl = self.dut.dblData.Tables('P166_SELFTEST_PACKAGENAME').tableDataObj()
                  packageName = P166SF3PackageTbl[-1]['PACKAGE_NAME']
                  result = self.updateFlagFile(packageName)
                  if not result:
                     objMsg.printMsg("Failed to set FLG file with %s. Trying bench submit package format." % packageName)

                     buildTarget = P166SF3PackageTbl[-1]['BUILD_TYPE']
                     cl = P166SF3PackageTbl[-1]['CHANGE_LIST']
                     if 'GID' in P166SF3PackageTbl[-1]:
                         gid = P166SF3PackageTbl[-1]['GID']
                     elif 'BUILDER_ID' in P166SF3PackageTbl[-1]:
                         # set gid to Builder ID if GID column doesn't exist, this is a code from before we
                         # deprecated the Builder ID in favor of the GID
                         gid = P166SF3PackageTbl[-1]['BUILDER_ID']

                     if testSwitch.FE_0124304_231166_FAIL_IF_NO_FLAG_FILE_FOUND:
                        for permutation in permutations(buildTarget, cl, gid):
                           packageName = '.'.join(permutation)
                           result = self.updateFlagFile(packageName)
                           if result:
                              break
                     else:
                        packageName = "%s.%s.%s" % (buildTarget, cl, gid)
                        result = self.updateFlagFile(packageName)

                     if not result:
                        if testSwitch.FE_0124304_231166_FAIL_IF_NO_FLAG_FILE_FOUND:
                           #we didn't find a match then fail unless we are in PRE2 and state is INIT- at this point
                           # it is unlikely that any codes will match and we actually don't care as the code MUST go through
                           # download in masspro
                           if self.dut.nextState == 'INIT' and self.dut.nextOper == 'PRE2':
                              objMsg.printMsg("Failed to set FLG file with %s" % packageName)
                           else:
                              ScrCmds.raiseException(11043, "Failed to set FLG file with %s" % packageName)

                        else:
                           # Cases where the reported package does not match the manifest file name, just use the flags
                           # file from available manifest file.  FW built with bincheck-1 reports '0' information but package
                           # naming may still be correctly named (no 0's).  Handling that case here.
                           from PackageResolution import PackageDispatcher
                           pd = PackageDispatcher(self.dut, codeType = 'CFW' )
                           fileName = pd.getFileName()
                           pd.setFlagFileName()
                           testSwitch.importExternalFlags(pd.flagFileName)
            except:
               objMsg.printMsg("Exception in flag code resolution:\n%s" % (traceback.format_exc(),))
               if testSwitch.FE_0124304_231166_FAIL_IF_NO_FLAG_FILE_FOUND  and not testSwitch.virtualRun:
                  ScrCmds.raiseException(11043, "Failed to set FLG file:\n%s" % (traceback.format_exc()))

            #=== Get zone info
            self.oFSO.getZoneTable(newTable = 1, delTables = 1, supressOutput = 0)
            if self.params.get('GET_WEDGE_INFO', False) and testSwitch.extern.FE_0269440_496741_LOG_RED_P172_ZONE_TBL_SPLIT:
               self.oFSO.getWedgeTable()
            #=== Get servo variables
            self.dut.maxServoTrack, self.dut.rpm, self.dut.servoWedges, self.dut.arcTPI = \
               self.oSrvFunc.readServoSymbolTable(['maxServoTrack','rpm','servoWedges','arcTPI'],TP.ReadPVDDataPrm_11, TP.getServoSymbolPrm_11, TP.getSymbolViaAddrPrm_11 )
            self.dut.rpmCategory = self.findRPMCategory(self.dut.rpm)
            self.dut.driveattr['SPINDLE_RPM'] = self.dut.rpmCategory
            objMsg.printMsg('SPINDLE_RPM: %s' % str(self.dut.driveattr['SPINDLE_RPM']))
            #=== Get Logical to physical head mapping
            self.oFSO.getLgcToPhysHdMap(self.dut.imaxHead)
            if (self.dut.nextOper == 'FNC2') and (testSwitch.auditTest ==1):
               self.auditTestSetup(TP.prm_auditTest_178)
            #=== Get PreAmp info
            from PreAmp import CPreAmp
            self.oPreAmp=CPreAmp()
            preamp_info = self.oPreAmp.getPreAmpType()
            self.dut.PREAMP_TYPE = preamp_info[0]
            self.dut.PREAMP_MFR  = preamp_info[1]
            self.dut.PREAMP_ID   = preamp_info[2]
            self.dut.PREAMP_REV  = preamp_info[3]
            objMsg.printMsg('PREAMP_TYPE AS PER CONFIG TABLE: %s' % (str(self.dut.PREAMP_TYPE)))
            objMsg.printMsg('Detected PREAMP Mfg: %s ID: %s Rev: %s' % (str(self.dut.PREAMP_MFR), str(self.dut.PREAMP_ID), str(self.dut.PREAMP_REV)))
            # update UMP Zones and MC Zones at INIT
            if testSwitch.FE_0284435_504159_P_VAR_MC_UMP_ZONES and self.dut.nextOper is not 'PRE2': 
               numMC, umpStartZone, numUMPZonesPerHead = self.oFSO.readMCandUMPInfo()
               TP.UMP_ZONE[self.dut.numZones] = range(umpStartZone, umpStartZone + numUMPZonesPerHead) + [self.dut.numZones-1]
               TP.numMC = numMC
               TP.numUMP = len(TP.UMP_ZONE[self.dut.numZones])
               
               if testSwitch.FE_348085_P_NEW_UMP_MC_ZONE_LAYOUT:
                  TP.MC_ZONE =  range(umpStartZone + numUMPZonesPerHead, umpStartZone + numUMPZonesPerHead + numMC)
               elif testSwitch.FE_0385234_356688_P_MULTI_ID_UMP:
                  TP.MC_ZONE = range(1,numMC+1,1)
               else:
                  TP.MC_ZONE = range(umpStartZone - numMC, umpStartZone)
            #=== Set DriveInfo flag
            self.dut.GotDrvInfo = 1
         else:
            objMsg.printMsg("Skipping Drive Info Initialization because it was completed previously.", objMsg.CMessLvl.IMPORTANT)

         if testSwitch.SMR:
            objMsg.printMsg("UMP ZONES %s numUMP %s" % (TP.UMP_ZONE[self.dut.numZones], TP.numUMP))
            objMsg.printMsg("MC ZONES %s numMC %s" % (TP.MC_ZONE, TP.numMC))
      else:
         #we have interface code on the drive.

         from CodeVer import theCodeVersion
         theCodeVersion.updateCodeRevisions()
         try:
            if testSwitch.FE_0126871_231166_ROBUST_PCK_COMP_SEARCH:
               result = self.updateFlagFile(theCodeVersion.CODE_VER, regex = False)
               if result:
                  #Got our code let's exit
                  return result


            if testSwitch.FE_0124304_231166_FAIL_IF_NO_FLAG_FILE_FOUND:
               #Break apart into components by . and check for permutations of code name and build target
               for permutation in permutations(theCodeVersion.CODE_VER.split('.')[0:2]):
                  packageName = '.'.join(permutation)
                  result = self.updateFlagFile(packageName)
                  if result:
                     break

               if not result:
                  #we didn't find a match then fail unless we are in PRE2 and state is INIT- at this point
                  # it is unlikely that any codes will match and we actually don't care as the code MUST go through
                  # download in masspro
                  if self.dut.nextState == 'INIT' and self.dut.nextOper == 'PRE2':
                     objMsg.printMsg("Failed to set FLG file with %s" % packageName)
                  else:
                     ScrCmds.raiseException(11043, "Failed to set FLG file with %s" % packageName)

            else:
               self.updateFlagFile(theCodeVersion.CODE_VER)
         except:
            if testSwitch.FE_0124304_231166_FAIL_IF_NO_FLAG_FILE_FOUND and not testSwitch.virtualRun:
               raise

            if testSwitch.FE_0124304_231166_FAIL_IF_NO_FLAG_FILE_FOUND:
               ScrCmds.raiseException(11043, "Failed to set FLG file:\n%s" % (traceback.format_exc()))

         # Update head and zone count in dut object
         if testSwitch.SDBP_TN_GET_NUMBER_OF_HEADS_AND_ZONES and (not objDut.certOper) and (not self.dut.isFDE()):
            from SDBPTestNumber import CSDBPTestNumber
            sdbp = CSDBPTestNumber(self.dut)
            sdbp.unlockFactoryCmds()
            self.dut.imaxHead = sdbp.getHeadNum()
            objMsg.printMsg("Setting imaxHead to %d" % self.dut.imaxHead)
            sdbp.lockFactoryCmds()
            sdbp.enableOnlineModeRequests()
            self.dut.numZones = int(sdbp.getNumberOfUserZones() / self.dut.imaxHead)
            objMsg.printMsg("Setting numZones to %d" % self.dut.numZones)
            sdbp.disableOnlineModeRequests()
         else:
            import serialScreen
            oSerial = serialScreen.sptDiagCmds()
            self.dut.imaxHead = int(oSerial.GetCtrl_L()['Heads'])
            objMsg.printMsg("Setting imaxHead to %d" % self.dut.imaxHead)

            self.dut.numZones = oSerial.GetNumZones()
            objMsg.printMsg("Setting numZones to %d" % self.dut.numZones)

   #-------------------------------------------------------------------------------------------------------
   def updateFlagFile(self, codeVersion, regex = True):
      from PackageResolution import PackageDispatcher
      pd = PackageDispatcher(self.dut, codeType = None, codeVersion = codeVersion, regex = regex)
      pd.setFlagFileName()

      if pd.flagFileName:
         testSwitch.importExternalFlags(pd.flagFileName)
         return True
      else:
         return False

   #-------------------------------------------------------------------------------------------------------
   def findRPMCategory(self, actual_rpm):
      if (actual_rpm < 6000):
         return '5400'
      elif (actual_rpm < 8000):
         return '7200'
      elif (actual_rpm < 12000):
         return '10000'
      else:
         return '15000'

   #-------------------------------------------------------------------------------------------------------
   def auditTestSetup(self,inPrm):
      """
      Audit test is a shortened test process based on an abbreviated RAP, that will still allow for interface testing.
      The RAP info is extracted from a dbLog table and stored in the drive object auditTestRAPDict, so is available for later use.
      maxLBA will need to be adjusted accordingly. here we set NUM_SERP (2~100 tracks),then we get back the audit tables
      and numPBA, then set MaxLBA accordingly
      """
      objMsg.printMsg("                       AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA                         ",objMsg.CMessLvl.IMPORTANT)
      objMsg.printMsg("              ******** AUDIT TEST: HEADS AND TRACK BANDS SET IN RAP TABLE ********             ",objMsg.CMessLvl.IMPORTANT)

      from VBAR_LBA import CVBAR_LBA
      oVbar = CVBAR_LBA()
      if not testSwitch.virtualRun:
         self.oSrvFunc.St(inPrm.copy())
         self.oFSO.getAuditTestRAPDict()
         oVbar.setMaxLBAForAudit()
      else:
         T178Prm = inPrm.copy()
         self.oSrvFunc.St(T178Prm)
         self.oSrvFunc.St({'test_num':172, 'prm_name':'retrieve audit test tables','CWORD1':28,'timeout': 200})

         oVbar.setMaxLBAForAudit()
         self.oFSO.getAuditTestRAPDict()
