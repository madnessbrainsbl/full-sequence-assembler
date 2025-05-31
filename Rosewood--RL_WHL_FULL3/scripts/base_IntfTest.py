#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: base Interface calibration states
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/10/19 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_IntfTest.py $
# $Revision: #5 $
# $DateTime: 2016/10/19 20:12:36 $
# $Author: yihua.jiang $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_IntfTest.py#5 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
import time, os, types
from Process import CProcess

from Drive import objDut
import string, time, traceback, re, types
from Cell import theCell
from Rim import objRimType, theRim
import MessageHandler as objMsg
import Utility
import ScrCmds
from State import CState
from PowerControl import objPwrCtrl
from IntfClass import CIdentifyDevice

import serialScreen
if testSwitch.SPLIT_BASE_SERIAL_TEST_FOR_CM_LA_REDUCTION:
   from Serial_Init import CInit_DriveInfo
else:
   from base_SerialTest import CInit_DriveInfo
from sptCmds import objComMode, comMode

from CodeVer import theCodeVersion

import sptCmds
from Utility import CUtility

from ICmdFactory import ICmd
import SATA_SetFeatures
if testSwitch.BF_0196490_231166_P_FIX_TIER_SU_CUST_TEST_CUST_SCREEN:
   import CommitServices
###########################################################################################################
from UPS import upsObj

class CInitTesting(CState):
   """
      Provide a single call to prepare drive for interface module testing
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)
      self.oProc = CProcess()


   #-------------------------------------------------------------------------------------------------------
   def run(self):

      if testSwitch.Enable_Reconfig_WTF_Niblet_Level_Check:
         from CustomCfg import CCustomCfg
         CCustomCfg().CheckReconfig(objDut.partNum)

      #Check RerunTODT
      if testSwitch.FE_0145983_409401_P_SEND_ATTR_FOR_CONTROL_DRIVE_ERROR:
         self.RerunTODT()

      self.dut.sptActive = objComMode
      self.dut.sptActive.setMode(objComMode.availModes.intBase)
      ICmd.downloadIORimCode()

      benchTop_Enable = RequestService('GetSiteconfigSetting','SKDC_BENCHTOP_ENABLE')[1]
      if type(benchTop_Enable) == types.StringType and benchTop_Enable == 'Error or not supported':
         objMsg.printMsg("***WARNING: RequestService('GetSiteconfigSetting') requires Host RPM 14.2-16 ***")
         benchTop_Enable={'SKDC_BENCHTOP_ENABLE': 0}

      if not self.dut.PSTROper and objRimType.IsPSTRRiser()  and benchTop_Enable.get('SKDC_BENCHTOP_ENABLE',0) == 0:
         objMsg.printMsg('Current operation %s is not allow to run in PSTR' % self.dut.nextOper)
         ScrCmds.raiseException(49052,'Current operation %s is not allow to run in PSTR' % self.dut.nextOper)

      # Check overlay for re-FIN2 and FNG2
      if testSwitch.FE_0221365_402984_RESTORE_OVERLAY:
         if (self.dut.nextOper == 'FIN2' and self.dut.scanTime)  or  (self.dut.nextOper == 'FNG2'):
            from Setup import CSetup
            CSetup().recoverOverlay()

      if objRimType.isNeptuneRiser():
         objMsg.printMsg("Neptune drive cycle in CMT2")
         DriveOff(10)
         DriveOn(5000,12000,30)

      ICmd.SetRFECmdTimeout(TP.prm_IntfTest["Default ICmd Timeout"])
      #Enable CRCError Retries limits are checked after each St command
      ICmd.CRCErrorRetry(IO_CRC_RETRY_VAL)
      ICmd.SetIntfTimeout(TP.prm_IntfTest["Default CPC Cmd Timeout"]*1000)

      from  PackageResolution import PackageDispatcher
      from FSO import CFSO
      oFSO = CFSO()

      self.dut.sptActive = comMode(comMode.availModes.intBase)

      #Set the default cert temperature based on the current operations temperature defined in temp_profile in TP.py
      if not ConfigVars[CN]['BenchTop']:
         reqTemp, minTemp, maxTemp = TP.temp_profile[self.dut.nextOper]
         theCell.setTemp(reqTemp, minTemp, maxTemp, self.dut.objSeq, objDut) #Breaks bench cell so we don't execute this if BenchTop set true

      objMsg.printMsg("Current cell temperature is "+str(ReportTemperature()/10.0)+"C.", objMsg.CMessLvl.IMPORTANT)
      self.dut.driveattr['ODT_TEST_DONE'] = 'NONE'
      self.dut.driveattr['IDT_TEST_DONE'] = 'NONE'
      self.dut.driveattr['OBA_TEST_DONE'] = 'NONE'

      if self.dut.nextOper == 'FIN2':
         self.dut.driveattr['TIME_TO_READY'] = 0

      if testSwitch.WA_0134988_395340_RESET_TIMEOUT_THAT_REMAIN_ON_CPC:
         self.oProc.St(TP.prm_506_RESET_RUNTIME)


      if testSwitch.BF_0169635_231166_P_USE_CERT_OPER_DUT:
         if testSwitch.WA_0164214_231166_P_DISABLE_DIAGS_IN_INTERFACE_OPS and not self.dut.certOper:
            testSwitch.WA_0122534_231166_DIAGS_UNSUPPORTED = 1
      else:
         if testSwitch.WA_0164214_231166_P_DISABLE_DIAGS_IN_INTERFACE_OPS and not objPwrCtrl.certOper:
            testSwitch.WA_0122534_231166_DIAGS_UNSUPPORTED = 1

      if testSwitch.FE_0160968_395340_P_FIX_POWER_CYCLE_FAIL_ON_PWL:
         try:
            objPwrCtrl.powerCycle(5000,12000,10,30, ataReadyCheck = self.params.get('ATA_READY_CHCK',  'force')) #TODO enable #ataReadyCheck = False)#
         except:
            if self.dut.powerLossEvent:
               # Initial Power Trip
               objMsg.printMsg("Re-Initializing slips")
               sptCmds.enableDiags()
               sptCmds.gotoLevel('T')
               sptCmds.sendDiagCmd('m0,6,,,,,,22',timeout = 600, printResult = True)
            else:
               raise
            objPwrCtrl.powerCycle(5000,12000,10,30, ataReadyCheck = self.params.get('ATA_READY_CHCK',  'force')) #TODO enable #ataReadyCheck = False)#
      else:
         objPwrCtrl.powerCycle(5000,12000,10,30, ataReadyCheck = self.params.get('ATA_READY_CHCK',  'force')) #TODO enable #ataReadyCheck = False)#

      self.dut.readyTimeLimit = None   # set to NONE to trigger TTRLimit checking
      objMsg.printMsg("Updated objPwrCtrl.readyTimeLimit : %s Msec" % objPwrCtrl.readyTimeLimit) #This will trigger TTRLimit checking

      oIdentifyDevice = CIdentifyDevice()
#CHOOI-18May17 OffSpec
#      oIdentifyDevice.check_dutID_syID()

      # Detect drive lifestate for TCG and SDnD drives only
      if oIdentifyDevice.Is_FDE() or str(self.dut.driveConfigAttrs.get('SECURITY_TYPE',(0,None))[1]).rstrip() == 'SECURED BASE (SD AND D)' or testSwitch.IS_SDnD:
         if testSwitch.COTTONWOOD:
            objMsg.printMsg("COTTONWOOD - No SED")
         elif oIdentifyDevice.Is_SeaCosFDE():
            from KwaiPrep import InitTrustedDL
            InitTrustedDL(self.dut)
         else:
            from TCG import CTCGPrepTest, LifeStates
            oTCG = CTCGPrepTest(self.dut, self.params)
            if testSwitch.BF_0157429_231166_P_FIX_LOCKED_SED_DRV_INIT:
               oTCG.InitTrustedTCG()
            else:
               if testSwitch.BF_0180787_231166_P_REMOVE_FDE_CALLBACKS_FOR_CHECKFDE:
                  try:
                     oTCG.CheckFDEState()
                     if self.dut.LifeState not in [ LifeStates['INVALID'], LifeStates['SETUP']]:
                        oTCG.InitTrustedTCG()
                  finally:
                     oTCG.RemoveCallback()
               else:
                  oTCG.CheckFDEState()
                  if self.dut.LifeState not in [ LifeStates['INVALID'], LifeStates['SETUP']]:
                     oTCG.InitTrustedTCG()

      try:
#CHOOI-18May17 OffSpec
#         oFSO.validateDriveSN()
         if testSwitch.FE_0160608_395340_P_FIX_FAILURE_FROM_T514_ON_SIC:
            objPwrCtrl.powerCycle(5000,12000,10,30, ataReadyCheck = True) #Use power cycle before get IdentifyDevice By P'Supitcha on SIC
         oIdentifyDevice = CIdentifyDevice()
      except:
         if self.params.get('ATA_READY_CHCK',  True):
            raise
         else:
            try:
               time.sleep(130) #wait for drive ready
               oFSO.validateDriveSN()
               oIdentifyDevice = CIdentifyDevice()
            except:
               return

      #oIdentifyDevice.check_dutID_syID()


      if ( self.dut.drvIntf in TP.WWN_INF_TYPE.get('WW_SAS_ID', []) or self.dut.drvIntf == 'SAS' ):
         self.dut.driveattr['JUMPER_SET'] = 'SATA_NO_JMPR'
      else:
         if oIdentifyDevice.Is_POIS():
            ConfigVars[CN].update({'Power On Set Feature':'ON'})
            self.dut.driveattr['POWER_ON_TYPE']="PWR_ON_IN_STDBY"
            objPwrCtrl.powerCycle(5000,12000,10,30, ataReadyCheck = self.params.get('ATA_READY_CHCK',  True)) #TODO enable #ataReadyCheck = False)
            # Disable POIS in case firmware don't support
            objMsg.printMsg("Disabling POIS.")
            from CustomerContent import CPois
            oPOIS = CPois(self.dut,{'ENABLED':0})
            oPOIS.run()
         else:
            self.dut.driveattr['POWER_ON_TYPE']="POIS_DISABLED"


         #check whether drive is SATA1 / SATA2
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

         self.dut.driveattr['MODEL_NUM'] = ret['IDModel'].strip()
         self.USB_Reconfig()

         #Update Interface Timeout Attribute after Drive PowerOn
         theCodeVersion.ChkUSB()
         if self.dut.driveattr['USB_INTF'] == 'Y':
            self.dut.driveattr['ATA_ReadyTimeout'] = 'USB'
         else:
            self.dut.driveattr['ATA_ReadyTimeout'] = 'NON_USB'


         objMsg.printMsg("FDE_DRIVE=%s at the end of Init" % self.dut.driveattr['FDE_DRIVE'])
         if (self.dut.driveattr['FDE_DRIVE']=='FDE') and (self.dut.objData.retrieve('KwaiPrepDone')==0) and (self.dut.objData.retrieve('TCGPrepDone')==0):
            if not ConfigVars[CN].get('PRODUCTION_MODE',0) and testSwitch.FE_0246029_385431_SED_DEBUG_MODE:
               objMsg.printMsg("FE_0246029_385431_SED_DEBUG_MODE on, continue")
            else:
               objMsg.printMsg("FDE_DRIVE = FDE at the end of Init, failed")
               ScrCmds.raiseException(14802, "FDE_DRIVE = FDE at the end of Init, failed")

         if testSwitch.DISABLE_NVCACHE_WHILE_TESTING:
            if objRimType.IOInitRiser():
               objPwrCtrl.powerCycle(5000,12000,10,30) # added power-cycle, otherwise below serial port cmd to disable NV cache will fail
            sptCmds.enableDiags()
            sptCmds.gotoLevel('O')
            sptCmds.sendDiagCmd('I', timeout = 300, printResult = True)
            sptCmds.gotoLevel('T')
            sptCmds.sendDiagCmd('F"DISABLE_WRITE_PINNING",1',timeout = 1200, altPattern = 'DISABLE_WRITE_PINNING = 1', printResult = True)
            sptCmds.sendDiagCmd('F"DISABLE_READ_PINNING",1', timeout = 1200, altPattern = 'DISABLE_READ_PINNING = 1',  printResult = True)
            sptCmds.sendDiagCmd('F"CongenConfigurationState"',timeout = 1200, printResult = True)
            objMsg.printMsg("DISABLE_NVCACHE_WHILE_TESTING")
            objPwrCtrl.powerCycle(5000,12000,10,30)

         try:
            #initialize any variables
            if testSwitch.COTTONWOOD:
               objMsg.printMsg("COTTONWOOD - skipping CInit_DriveInfo")
            else:
               CInit_DriveInfo(self.dut, self.params).run()

         except:
            objMsg.printMsg(traceback.format_exc())
            objPwrCtrl.powerCycle(5000,12000,10,30, ataReadyCheck = self.params.get('ATA_READY_CHCK',  True)) #TODO enable #ataReadyCheck = False)#
            if not self.params.get('ATA_READY_CHCK',  True):
               time.sleep(130)

      if testSwitch.CPCWriteReadRemoval:
         objMsg.printMsg("Using CPC tracking")
         oIdentifyDevice = CIdentifyDevice()
         self.dut.numLba = oIdentifyDevice.getMaxLBA()
         self.dut.numTrackingZone = getattr(TP,'prm_WriteReadRemoval', 980)    # Max = 980

         #enable, reset and setup tracking
         objMsg.printMsg('Reset and start tracking, numLBA = %d numTrackingZone = %d'% (self.dut.numLba,self.dut.numTrackingZone))
         result = ICmd.CommandLocation(1,self.dut.numTrackingZone,self.dut.numLba)
         objMsg.printMsg('result = %s' % result)

      if ConfigVars[CN].get('AMPS Reset',0):
         from base_IntfTest import CAMPSCheck
         oAMPSCheck = CAMPSCheck(self.dut, self.params)
         try:
            oAMPSCheck.run()
         except:
            if oAMPSCheck.AMPSdict['AMPS_STATE'] < 0:
               raise
         if oAMPSCheck.AMPSdict['AMPS_STATE'] > 1:
            from base_IntfTest import CResetAMPS
            oResetAMPS = CResetAMPS(self.dut, self.params)
            oResetAMPS.run()
            oAMPSCheck.run()

      if testSwitch.FE_0146555_231166_P_VER_TEMP_SAT_INIT:
         #Set the default cert temperature based on the current operations temperature defined in temp_profile in TestParam.py
         from Temperature import CTemperature
         CTemperature().verifyHDASaturation()

      self.dut.MCDriveReprocess = not ('SDP1' in self.dut.driveattr.get('CODE_VER', 'SDP1'))

   #-------------------------------------------------------------------------------------------------------
   def USB_Reconfig(self):
      theCodeVersion.ChkUSBReconfig()

   #-------------------------------------------------------------------------------------------------------
   def RerunTODT(self):
      if self.dut.driveattr['TODT_DEF'] == 'H' and self.dut.driveattr['PART_NUM'][6:] not in ['-301']:
         objMsg.printMsg('Not allow to rerun, the system block the hard EC to key customer')
         ScrCmds.raiseException(22333, 'Hard Defect - cannot rerun')

#----------------------------------------------------------------------------------------------------------
class CDnlduCode(CState):
   """
   State class for utilizing the download uCode feature on ATA drives--> Downloads code over the interface to the HDA.
   """
   def __init__(self, dut, params=[]):
      self.dut = dut
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def DownloadUnlock(self):
      if testSwitch.FE_0124012_231166_ALLOW_PF3_UNLK_CODE_ACCESS:
         import PackageResolution
         oProc = CProcess()
         maxRetry = 3
         for retry in xrange(maxRetry):
            if not objRimType.IOInitRiser():
               #Force ESLIP off so st8 uses dluCode
               theCell.disableESlip()
            #Confirm we have the drive's full attention...
            ICmd.HardReset()
            try:
               #Send the code
               oProc.dnldCode(PackageResolution.UNLK_KEY, timeout = 100, interfaceDownload = True)
               break
            except:
               objMsg.printMsg('Failed to download unlock code')
               objPwrCtrl.powerCycle(5000, 12000, 10, 30, ataReadyCheck = False)

      else:
         import os.path
         fileName = 'unlock_m.lod' #assuming that this file has been added to config.
         if os.path.isfile(os.path.join(ScrCmds.getSystemDnldPath(), fileName)):
            oProc = CProcess()
            dnldParam = 'Download uCode- %s->%s'
            dnldDict = {'test_num'     : 8,
                        'prm_name'     : dnldParam,
                        'timeout'      : 100,
                        'retryECList'  : [10340, 11049, 11087, 11088, 11169],
                        'retryCount'   : 2,
                        'retryMode'    : POWER_CYCLE_RETRY,
                        }
            code = 'UNLK'
            #Override the dl params
            dnldDictCpy = dict(dnldDict)
            dnldDictCpy['dlfile'] = (CN,fileName)
            dnldDictCpy['prm_name'] = dnldParam %(code, fileName,)
            maxRetry = 3
            for retry in xrange(maxRetry):
               #Force ESLIP off so st8 uses dluCode
               theCell.disableESlip()
               #Confirm we have the drive's full attention...
               ICmd.HardReset()
               try:
                  #Send the code
                  oProc.St(dnldDictCpy)
                  break
               except:
                  objMsg.printMsg('Failed to download unlock code')
                  objPwrCtrl.powerCycle(5000, 12000, 10, 30, ataReadyCheck = False)

   #-------------------------------------------------------------------------------------------------------
   def run(self):

      if testSwitch.FE_0180513_007955_COMBINE_CRT2_FIN2_CUT2:
         self.dut.certOper = False
         objPwrCtrl.certOper = False
      if testSwitch.FE_0165086_231166_P_INGORE_TTR_IN_FIN2_DL:
         objPwrCtrl.downloadActive = True

      # detect if drive should possibly trigger an MC data invalid init
      self.dut.MCDriveReprocess = not ( ( 'SDP1' in self.dut.driveattr.get('CODE_VER', 'SDP1') ) or ( 'APD1' in self.dut.driveattr.get('CODE_VER', 'APD1') ) or ( 'APD2' in self.dut.driveattr.get('CODE_VER', 'APD2') ) or ( 'CVC1' in self.dut.driveattr.get('CODE_VER', 'CVC1') ) )
      try:
         if testSwitch.FE_0158866_231166_P_RETRY_DNLD_CODE_NON_COMMIT:
            result = False
            maxRetries = self.params.get('COMMIT_RETRIES', 2)
            for retryNum in xrange(maxRetries):
               try:
                  result = self.download_code()
               except:
                  objMsg.printMsg("download failure!!\n%s" % (traceback.format_exc(),))
                  result = False
                  if 'TGT' not in self.params['CODES']:
                     #if we don't have a TGT in the sequence for SDP1 transition then lets add it.. with UNLK to be safe
                     self.params['CODES'].insert( 0, 'TGT')
                     self.params['CODES'].insert(0, 'UNLK')
                     #now = UNLK, TGT, ...

                  #now verify with 2 power cycles the cell and drive are reset
                  objPwrCtrl.powerCycle(5000,12000,10,30, ataReadyCheck = False)
                  objPwrCtrl.powerCycle(5000,12000,10,30, ataReadyCheck = True)


               if result == True:
                  break
               else:
                  objMsg.printMsg("Download failed to commit code to the flash- on attempt %d/%d" % (retryNum+1, maxRetries), objMsg.CMessLvl.CRITICAL)
            else:
               #none worked!!
               ScrCmds.raiseException(12505, "Failed to download code to DUT")
         else:
            self.download_code()
      finally:
         if testSwitch.FE_0165086_231166_P_INGORE_TTR_IN_FIN2_DL:
            objPwrCtrl.downloadActive = False

#CHOOI-25Apr17 OffSpec
#      if testSwitch.BF_0217062_347506_RESET_BIST_SPEED_AFTER_DOWNLOAD:
      if (not testSwitch.OOS_Code_Enable) and (testSwitch.BF_0217062_347506_RESET_BIST_SPEED_AFTER_DOWNLOAD):
         if self.dut.drvIntf == 'SATA':
            objMsg.printMsg("Reset SCT-BIST Signal Speed to nominal")

            sptCmds.enableDiags()
            sptCmds.gotoLevel('T')
            sptCmds.sendDiagCmd('F"SCTCommandSetSupported",BB30', printResult = True)
            objPwrCtrl.powerCycle()

            ICmd.St(TP.UnlockFactoryCmdsDETS_prm)
            if testSwitch.FE_0203458_231166_ADD_DETS_UNLOCK_STRING_PHASE_1:
               prm_T638_UnlockDETS= {
                     'test_num'           : 638,
                     'prm_name'           : 'prm_T638_UnlockDETS',
                     'stSuppressResults'  : 0,
                     'CTRL_WORD1'         : 0x0008, # Command Supplied is a DETS Command
                     'DFB_WORD_0'         : 0x0303, # FunctionId ()
                     'DFB_WORD_1'         : 0x0100,
                     'DFB_WORD_2'         : 0x0000,
                     'DFB_WORD_3'         : 0x0000,
                     'DFB_WORD_4'         : 0x9A32,
                     'DFB_WORD_5'         : 0x4F03,
                  }

               ICmd.St(prm_T638_UnlockDETS)

            SCT_Cmd.SetBistSpeed(SCT_Cmd.speedOptions['nominal'])

#CHOOI-25Apr17 OffSpec
#      if testSwitch.FE_0174818_231166_P_RESET_SMART_POST_DL:
      if (not testSwitch.OOS_Code_Enable) and ( testSwitch.FE_0174818_231166_P_RESET_SMART_POST_DL):
         objMsg.printMsg("RESETTING SMART POST DOWNLOAD", objMsg.CMessLvl.IMPORTANT)
         oClearSmt = CClearSMART(self.dut)
         oClearSmt.run()

#CHOOI-25Apr17 OffSpec
#      if testSwitch.FE_0202455_231166_P_RESET_XFER_CAP_POST_DL:
      if (not testSwitch.OOS_Code_Enable) and  (testSwitch.FE_0202455_231166_P_RESET_XFER_CAP_POST_DL):
         self.dut.driveattr['XFER_CAP'] = 99.0

   def download_code(self):

      SED_DNLD = 'TCG' in self.dut.nextState
      custCodes = ['TGT2', 'SFWTGT2', 'TGT']
      svoCodes = ['SFWI2','SFW']
      #if testSwitch.FE_0141467_231166_P_SAS_FDE_SUPPORT
      #   theRim.powerCycleRim()
      #   objPwrCtrl.powerCycle(ataReadyCheck = False)

#possibly remove
      if not self.dut.sptActive.getMode() in [self.dut.sptActive.availModes.sptDiag, self.dut.sptActive.availModes.intBase]:
         ScrCmds.raiseException(13424, "CDnlduCode only valid when interface code is on the HDA.")
      elif not testSwitch.FE_0110517_347506_ADD_POWER_MODE_TO_DCM_CONFIG_ATTRS:
         oIdentifyDevice = CIdentifyDevice()
         if oIdentifyDevice.Is_POIS():
            from CustomerContent import CPois
            oPOIS = CPois(self.dut,{'ENABLED':0})
            oPOIS.run()
            self.dut.driveattr['POWER_ON_TYPE']="POIS_DISABLED"
#end remove

      if testSwitch.FE_0121834_231166_PROC_TCG_SUPPORT:
         dnldParam = 'Download uCode- %s->%s'
         dnldDict_578 = {'test_num'     : 578,
                     'prm_name'     : dnldParam,
                     'timeout'      : 100,
                     'retryECList'  : [10340, 11049, 11087, 11088, 11169, 10468],
                     'retryCount'   : 2,
                     'retryMode'    : POWER_CYCLE_RETRY,
                     'TEST_MODE'    : 1, # 1= Initiatl Volume Download, 2= locking params
                     'FW_PLATFORM'  : 0x10, #CANNON fw platform type
                     }

         dnldDict_8 = {
                     'test_num'     : 8,
                     'prm_name'     : dnldParam,
                     'timeout'      : 100,
                     'retryECList'  : [10340, 11049, 11087, 11088, 11169],
                     'retryCount'   : 2,
                     'retryMode'    : POWER_CYCLE_RETRY,
                     }
         testModes = self.params.get('TEST_MODE', [1 for i in self.params['CODES']])

      oProc = CProcess()
      dnldParam = 'Download uCode- %s->%s'
      dnldDict = {'test_num'     : 8,
                  'prm_name'     : dnldParam,
                  'timeout'      : 100,
                  'retryECList'  : [10340, 11049, 11087, 11088, 11169],
                  'retryCount'   : 2,
                  'retryMode'    : POWER_CYCLE_RETRY,
                  }

      from  PackageResolution import PackageDispatcher
      codesToDownload = self.params['CODES']
      if testSwitch.FE_0193436_231166_P_SUPPORT_FW_NAME_REV_25 and [i for i in codesToDownload if 'SFWTGT' in i] != []:
         for idx in [2, 3]:
            val = 'SFWTGT%d' % idx
            if val in codesToDownload:
               pd = PackageDispatcher(self.dut, val)
               fileName = pd.getFileName()
               if fileName not in [None, '']:
                  for name in ['TGT', 'SFWI']:
                     name2 = '%s%d' % (name, idx)
                     if name2 in codesToDownload:
                        codesToDownload.remove(name2)
                        objMsg.printMsg("Removing %s from codesToDownload" % (name2,))
               else:
                  #remove the val since it isn't in package
                  codesToDownload.remove(val)
      if testSwitch.FE_0156072_409401_P_ENABLE_COMPARE_TGTA_CODE:
         for code in self.params['CODES']:
            matchCode = 0
            if code in custCodes + svoCodes and self.params.get('CMP_CODE', 0) == 1:
               theCodeVersion.updateCodeRevisions()
               if code in custCodes:
                  fileName = PackageDispatcher(self.dut, code).packageHandler.getManifestName()
                  codeOnDrive = theCodeVersion.CODE_VER
                  objMsg.printMsg('Code to be dnld: %s'%(str(fileName)))
               elif code in svoCodes:
                  fileName = PackageDispatcher(self.dut, code).getFileName()
                  codeOnDrive = theCodeVersion.SERVO_CODE
                  objMsg.printMsg('Code to be dnld: %s'%(str(fileName)))
               try:
                  patt = re.compile(codeOnDrive, re.I)
               except:
                  if testSwitch.virtualRun:
                     continue
                  else:
                     raise
               mobj = patt.search(fileName)
               if not mobj == None:
                  objMsg.printMsg('Drive already has code: %s, no need to dnld code: %s' %(codeOnDrive, str(fileName)))
                  matchCode = 1
               else:
                  objMsg.printMsg("Drive hasn't code.")
                  matchCode = 0
                  break
         if matchCode == 1:
            objMsg.printMsg('Drive already has codes. No need to download again.')
            return True # matches the passing download state
         else:
            objMsg.printMsg("Need to download %s"%(self.params['CODES']))
            objPwrCtrl.powerCycle(5000,12000,10,30, ataReadyCheck = self.params.get('ATA_READY_CHCK',  True))

      if testSwitch.FE_0138491_231166_P_BYPASS_UNLK_FOR_TGTP_ON_DUT:
         objMsg.printMsg("Downloading %s" % (codesToDownload,))

      bypassUNLK = False
      if codesToDownload != [] and codesToDownload[0] == 'UNLK' and \
         'TGT' in codesToDownload and testSwitch.FE_0138491_231166_P_BYPASS_UNLK_FOR_TGTP_ON_DUT:

         theCodeVersion.updateCodeRevisions()
         codeVersion = theCodeVersion.CODE_VER

         pd = PackageDispatcher(self.dut, codeType = None, codeVersion = codeVersion, regex = True)
         result = pd.packageHandler != None

         if not result:

            for permutation in Utility.permutations(codeVersion.split('.')[0:2]):
               packageName = '.'.join(permutation)

               pd = PackageDispatcher(self.dut, codeType = None, codeVersion = codeVersion, regex = True)
               result = pd.packageHandler != None

               if result:
                  break

         if not result or pd.codeType == None:
            pd = PackageDispatcher(self.dut, codeType = None, codeVersion = theCodeVersion.AltF3_SAS_ID, regex = True)
            result = pd.packageHandler != None

         if result and pd.codeType == 'TGT': #if we found it and it is TGTP type
            objMsg.printMsg("Found TGTP on drive. Bypassing UNLK download")
            del codesToDownload[0]
            bypassUNLK = True
         elif result:
            objMsg.printMsg("Found package related to code on drive but not TGTP type: found %s" % (pd.codeType,))
         else:
            objMsg.printMsg("Unable to find package related to code on drive to ID code type.")


      lastCodeLoad = ''
      codeVerID = None
      servoCodeName = None
      unlkFile = False

      # Code download routine
      for idx, code in enumerate(codesToDownload):
         pd = PackageDispatcher(self.dut, code)
         fileName = pd.getFileName()
         unlkFile = code.find('UNLK') != -1 #sets to true if unlock file
         if testSwitch.FE_0152922_231166_P_DNLD_U_CODE_PKG_CODE_VER:
            if code.find('TGT') != -1:
               # If this is a new target code
               if pd.manifestName and not self.dut.codes.has_key(code):
                  #And we used manifest for translation
                  codeVerID = pd.manifestName[:pd.manifestName.upper().find('.MFT')]
                  objMsg.printMsg("Code version validation enabled. Using %s for validation post download sequence." % (codeVerID, ))
               else:
                  # Disable the after download check
                  codeVerID = None
            elif code.find('SFW') != -1 and testSwitch.FE_0175236_231166_P_VERIFY_SERVO_CODE_IN_INTF_DNLD:
               servoCodeName = fileName

         if fileName in  ['',None]:
            if testSwitch.FailcodeTypeNotFound:
               if testSwitch.virtualRun:
                  objMsg.printMsg('Code not found in codeType resolution for %s' % code)
                  continue

               else:
                  ScrCmds.raiseException(10326,'Code not found in codeType resolution.')
            else:
               objMsg.printMsg("*"*20 + "Warning: Skipping %s Download" % code, objMsg.CMessLvl.IMPORTANT)
               continue

         if testSwitch.FE_0140102_357552_ENABLE_COMPARE_CODE_FUNCTIONALITY:
            # Specifically check servo code as same servo code download will fail.
            if self.params.get('CMP_CODE', 0) == 1 and code in svoCodes:
               #Skip code load if drive already has it
               objMsg.printMsg("Verifying %s code." %code)
               theCodeVersion.updateCodeRevisions()

               if code in svoCodes:
                  codeOnDrive = theCodeVersion.SERVO_CODE
               else:
                  codeOnDrive = theCodeVersion.CODE_VER
               if ( self.dut.drvIntf in TP.WWN_INF_TYPE.get('WW_SAS_ID', []) or self.dut.drvIntf == 'SAS' ):
                  codeOnDrive = theCodeVersion.AltF3_SAS_ID

               objMsg.printMsg('Drive has code: %s, code to be dnld: %s' %(codeOnDrive, str(fileName)))
               try:
                  patt = re.compile(codeOnDrive, re.I)
               except:
                  if testSwitch.virtualRun:
                  # VE has code_ver invalid or ? sometimes and this causes the compile to fail
                     continue
                  else:
                     raise
               mobj = patt.search(fileName)
               if not mobj == None and code is 'SFW':
                  objMsg.printMsg('Drive already has code: %s, no need to dnld code: %s' %(codeOnDrive, str(fileName)))
                  continue
               if not mobj == None and not ('TGT' in lastCodeLoad and 'OVL' in pd.codeType):  #Don't want to skip loading 2nd half of code
                  objMsg.printMsg('Drive already has code: %s, no need to dnld code: %s' %(codeOnDrive, str(fileName)))
                  continue
               objPwrCtrl.powerCycle(5000,12000,10,30, ataReadyCheck = self.params.get('ATA_READY_CHCK',  True))

         lastCodeLoad = pd.codeType

         if pd and pd.flagFileName:
            testSwitch.importExternalFlags(pd.flagFileName)

         if testSwitch.FE_0121834_231166_PROC_TCG_SUPPORT:
            if fileName.lower().find('.trd') == -1:
               dnldDict = CUtility.copy(dnldDict_8)
               RAW_IV_DOWNLOAD = False
            else:
               #TRD file so use trusted download
               dnldDict = CUtility.copy(dnldDict_578)
               fileObj = open(os.path.join(ScrCmds.getSystemDnldPath(),  fileName),  'r')
               try:
                  if testSwitch.virtualRun:
                     fileSize = CUtility.ReturnTestCylWord(0)
                  else:
                     fileSize = CUtility.ReturnTestCylWord(ScrCmds.getFileSize(fileObj))
               finally:
                  fileObj.close()
               dnldDict['FILE_LEN_MSW'] = fileSize[0]
               dnldDict['FILE_LEN_LSW'] = fileSize[1]

               dnldDict['TEST_MODE'] = testModes[idx]
               RAW_IV_DOWNLOAD = True
               SED_DNLD = True
         else:
            RAW_IV_DOWNLOAD = False

         #Override the dl params
         dnldDict['dlfile'] = (CN,fileName)
         dnldDict['prm_name'] = dnldParam % (code, fileName)

         maxRetry = 3 #exec 0,1,exception
         for retry in xrange(maxRetry):



            #Confirm we have the drive's full attention...
            if not testSwitch.FE_0132943_231166_DISABLE_HARD_RESET_DNLD_UCODE:
               ICmd.HardReset()
            if testSwitch.FE_0117013_399481_DO_IDENTIFYDEVICE_BEFORE_DOWNLOAD:
               if ((not (SED_DNLD or unlkFile)) or idx <= 1) or not testSwitch.FE_0184924_231166_P_BYPASS_INIT_PWR_CYCLE_UNLK_AND_SED:
                  oIdentifyDevice = CIdentifyDevice()

            ICmd.SetIntfTimeout(300*1000) #always set
            try:
               #Send the code
               if testSwitch.FE_0116900_399481_ATTEMP_UNLOCK_F3_DNLD and not bypassUNLK:
                  self.DownloadUnlock()

               if (not RAW_IV_DOWNLOAD) :
                  if testSwitch.virtualRun and fileName == None:
                     fileName = ''
                  objMsg.printMsg("fileName = %s" % fileName)

                  try:
                     oProc.dnldCode(code, fileName = fileName, timeout = 400, interfaceDownload = True)

#CHOOI-25Apr17 OffSpec
                     if self.dut.nextState in ['DNLD_OOS_CODE','DNLD_OOS_CODE_1','DNLD_OOS_CODE_2']:
                        testSwitch.OOS_Code_Enable    = 1  #CHOOI-02May14

                        objMsg.printMsg('====================================================================================')
                        objMsg.printMsg('====================================================================================')
                        objMsg.printMsg('testSwitch.OOS_Code_Enable: %s' % (testSwitch.OOS_Code_Enable))
                        objMsg.printMsg('====================================================================================')
                        objMsg.printMsg('====================================================================================')

                     if (SED_DNLD or unlkFile) and testSwitch.FE_0184924_231166_P_BYPASS_INIT_PWR_CYCLE_UNLK_AND_SED:
                        objMsg.printMsg("Detected SED or UNLK download- bypassing power cycle")
                        break
                     if code == 'OVLB' and testSwitch.TCGSuperParity:
                        objMsg.printMsg("TCG Super Parity after OVLB download, need to perform quick serial format")
                        objPwrCtrl.powerCycle()
                        sptCmds.enableDiags()
                        sptCmds.gotoLevel('T')
                        sptCmds.sendDiagCmd('m0,6,3,,,,,22',timeout = 1200, printResult = True)
                        objMsg.printMsg("Quick serial format done")

#CHOOI-15May17 Offpsec
#                     if testSwitch.BF_0163846_231166_P_SATA_DNLD_ROBUSTNESS:
                     if (not testSwitch.OOS_Code_Enable) and (testSwitch.BF_0163846_231166_P_SATA_DNLD_ROBUSTNESS):
                        if code[:3] == 'OVL':
                           objPwrCtrl.powerCycle()                               # Corrects Invalid Diag Cmd after OVL code download
                           oSerial = serialScreen.sptDiagCmds()
                           ovlValid = oSerial.OverlayRevCorrect()
                           if testSwitch.virtualRun:
                              ovlValid = True
                              objMsg.printMsg("Forcing OVL valid for virtual execution.")
                           sptCmds.enableESLIP()
                           if not ovlValid:
                              ScrCmds.raiseException(12505, "Failed to download OVL code to DUT. Attempted: %s" % ( fileName ))


#CHOOI-15May17 OffSpec
#                     if testSwitch.WA_0130599_357466_T528_EC10124:
                     if (not testSwitch.OOS_Code_Enable) and (testSwitch.WA_0130599_357466_T528_EC10124):
                        try:
                           DriveOff(10)
                           self.dut.baudRate = DEF_BAUD
                           RimOff()
                           RimOn()
                           from UartCls import theUart
                           theUart.setBaud(DEF_BAUD)
                           DriveOn(5000,12000,30)
                           self.dut.sptActive.setMode(objComMode.availModes.intBase)
                           import base_BaudFunctions
                           base_BaudFunctions.changeBaud(PROCESS_HDA_BAUD)
                           prm_517_01 = {
                               "SENSE_DATA_8" : (0x0000,0x0000,0x0000,0x0000,),
                               "MAX_REQS_CMD_CNT" : (0x000F,),
                               "SENSE_DATA_4" : (0x0000,0x0000,0x0000,0x0000,),
                               "SENSE_DATA_1" : (0x0000,0x0000,0x0000,0x0000,),
                               "TEST_FUNCTION" : (0x0000,),
                               "SENSE_DATA_3" : (0x0000,0x0000,0x0000,0x0000,),
                               "CHK_FRU_CODE" : (0x0000,),
                               "SENSE_DATA_5" : (0x0000,0x0000,0x0000,0x0000,),
                               "SENSE_DATA_6" : (0x0000,0x0000,0x0000,0x0000,),
                               "SENSE_DATA_7" : (0x0000,0x0000,0x0000,0x0000,),
                               "ACCEPTABLE_SNS_DATA" : (0x0000,),
                               "RPT_SEL_SNS_DATA" : (0x0000,),
                               "SRVO_LOOP_CODE" : (0x0000,),
                               "CHK_SRVO_LOOP_CODE" : (0x0000,),
                               "SEND_TUR_CMDS_ONLY" : (0x0001,),
                               "RPT_REQS_CMD_CNT" : (0x0000,),
                               "SENSE_DATA_2" : (0x0000,0x0000,0x0000,0x0000,),
                               "OMIT_DUP_ENTRY" : (0x0000,),
                               "ACCEPTABLE_IF_MATCH" : (0x0000,),
                           }
                           prm_517_01['SEND_TUR_CMDS_ONLY'] = 1

                           st(517, prm_517_01)  #clear sense
                        except:
                           objMsg.printMsg(traceback.format_exc())


                  except ScriptTestFailure, (failData):
                     objMsg.printMsg("Exception: %s" % (traceback.format_exc(),))
#CHOOI-15May17 OffSpec
#                     if failData[0][2] in [39200,] and code == 'TGT2':
                     if failData[0][2] in [39200,] and code in ['TGT2','TGT5']:
                        #FDE bridge... continue to IV
                        continue
                     elif testSwitch.FE_0147966_231166_P_IGNORE_UNLK_DNLD_FAIL and code == 'UNLK':
                        continue
                     else:
                        raise

               else:
                  oProc.St(dnldDict)


               break
            except:
               objMsg.printMsg("Exception: %s" % (traceback.format_exc(),))
               if retry == maxRetry-1:
                  raise
               else:
                  objPwrCtrl.powerCycle(5000,12000,10,30, ataReadyCheck = self.params.get('ATA_READY_CHCK',  True)) #TODO enable #ataReadyCheck = False)#

         if testSwitch.FE_0130984_231166_PWR_CYCLE_VER_DNLDUCODE:
            if ( not (SED_DNLD or unlkFile)) or (not testSwitch.FE_0184924_231166_P_BYPASS_INIT_PWR_CYCLE_UNLK_AND_SED):
               objPwrCtrl.powerCycle(5000,12000,10,30, ataReadyCheck = self.params.get('ATA_READY_CHCK',  True)) #TODO enable #ataReadyCheck = False)#

#CHOOI-15May17 OffSpec
#         if testSwitch.BF_0163846_231166_P_SATA_DNLD_ROBUSTNESS and testSwitch.Media_Cache and code == "TGT2":
         if testSwitch.BF_0163846_231166_P_SATA_DNLD_ROBUSTNESS and testSwitch.Media_Cache and code in ["TGT2","TGT5"]:
            if testSwitch.FE_0178061_231166_P_REDUCE_MC_DNLD_SLEEP:
               objMsg.printMsg("Waiting 1min to let Drive initialize...")
               time.sleep(60)
            else:
               objMsg.printMsg("Waiting 3min to let Drive initialize...")
               time.sleep(180)
      #for idx, code in enumerate(self.params['CODES']):

      if testSwitch.FE_0110517_347506_ADD_POWER_MODE_TO_DCM_CONFIG_ATTRS:
         oIdentifyDevice = CIdentifyDevice()
         if oIdentifyDevice.Is_POIS():
            ConfigVars[CN].update({'Power On Set Feature':'ON'})
            objPwrCtrl.powerCycle(5000,12000,10,30, ataReadyCheck = self.params.get('ATA_READY_CHCK',  True)) #TODO enable #ataReadyCheck = False)#
         else:
            ConfigVars[CN].update({'Power On Set Feature':'OFF'})

      if not self.params.get('ATA_READY_CHCK',  True):
         time.sleep(130) #allow drive to come ready in it's own time
      #Update dcm after all codes are updated
      theCodeVersion.updateCodeRevisions()

#CHOOI-15May17 OffSpec
#      if testSwitch.FE_0152922_231166_P_DNLD_U_CODE_PKG_CODE_VER and not SED_DNLD:
      if (not testSwitch.OOS_Code_Enable) and (testSwitch.FE_0152922_231166_P_DNLD_U_CODE_PKG_CODE_VER and not SED_DNLD):
         f3Code_invalid = (codeVerID != None) and (codeVerID != self.dut.driveattr['CODE_VER'])
         attempted = codeVerID
         resident = self.dut.driveattr['CODE_VER']

         if testSwitch.FE_0158862_231166_P_VERIFY_OVL_DNLD_U_CODE:
            oSerial = serialScreen.sptDiagCmds()
            ovlValid = oSerial.OverlayRevCorrect()
            if testSwitch.virtualRun:
               ovlValid = True
               objMsg.printMsg("Forcing OVL valid for virtual execution.")
            sptCmds.enableESLIP()

            f3Code_invalid = (ovlValid == 0) or f3Code_invalid

         if testSwitch.FE_0175236_231166_P_VERIFY_SERVO_CODE_IN_INTF_DNLD:
            if not f3Code_invalid: # don't validate if f3 failed
               # if we downloaded an sfw and it isn't found in the dl file name

               if (servoCodeName != None) and (servoCodeName.find(self.dut.driveattr['SERVO_CODE']) == -1):
                  if not testSwitch.virtualRun:
                     f3Code_invalid = True
                     attempted = servoCodeName
                     resident = self.dut.driveattr['SERVO_CODE']
               else:
                  objMsg.printMsg("Validated: Resident %s, Attempted: %s" % ( self.dut.driveattr['SERVO_CODE'], servoCodeName))


         if f3Code_invalid:
            if testSwitch.FE_0158866_231166_P_RETRY_DNLD_CODE_NON_COMMIT:
               return False
            else:
               ScrCmds.raiseException(12505, "Failed to download code to DUT. Resident %s, Attempted: %s" % ( resident, attempted))
         else:
            objMsg.printMsg("Validated: Resident %s, Attempted: %s" % ( resident, attempted))

#CHOOI-15May17 OffSpec
#      if testSwitch.FE_0139645_426568_P_STATE_TABLE_RESET_TIME_TO_READY:
      if (not testSwitch.OOS_Code_Enable) and (testSwitch.FE_0139645_426568_P_STATE_TABLE_RESET_TIME_TO_READY):
         if self.params.get('RESET_TTR', False):
            self.dut.driveattr['TIME_TO_READY'] = 0

#CHOOI-15May17 OffSpec
#      if testSwitch.FE_0155594_357260_P_INITIALIZE_DRIVE_INFO_AFTER_INTF_DOWNLOAD:
      if (not testSwitch.OOS_Code_Enable) and (testSwitch.FE_0155594_357260_P_INITIALIZE_DRIVE_INFO_AFTER_INTF_DOWNLOAD):
         # Initialize any variables
         try:
            CInit_DriveInfo(self.dut, self.params).run()
         except:
            pass

      ICmd.SetIntfTimeout(TP.prm_IntfTest["Default CPC Cmd Timeout"]*1000)

      if testSwitch.FE_0158866_231166_P_RETRY_DNLD_CODE_NON_COMMIT:
         return True

###########################################################################################################
class CResetAMPS(CState):
   """
      Disable reset AMPS to defaults
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut

   def run(self):
      oSerial = serialScreen.sptDiagCmds()
      sptCmds.enableDiags()
      oSerial.resetAMPs()

      if not self.params.get('NO_PWR_CYCLE',0):
         objPwrCtrl.powerCycle()

###########################################################################################################
class CAMPSCheck(CState):
   """
      Write or Read the drive defined in FullPackReadWrite
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut
      self.AMPSdict = {'AMPS_STATE' : -1}

   #-------------------------------------------------------------------------------------------------------
   def run(self):

      oSerial = serialScreen.sptDiagCmds()
      lbaXlatePattern = '\S+\s+CongenConfigurationState\s=\s(?P<AMPS_STATE>[a-fA-F\d]+)'
      if not testSwitch.virtualRun:
         data = oSerial.getCongen()
      else:
         data = """
               F"CongenConfigurationState"  Byte:0192:  CongenConfigurationState = 01
               """
      data = data.replace("\n","")
      match = re.search(lbaXlatePattern, data)

      if match:
         tempDict = match.groupdict()
         self.AMPSdict =  oSerial.convDictItems(tempDict, int, [16,])
         objMsg.printMsg("AMPS check CongenConfigurationState = %d" % self.AMPSdict['AMPS_STATE'])
         if self.AMPSdict['AMPS_STATE'] > 1:
            ScrCmds.raiseException(11044, "AMPS Check Failure: CongenConfigurationState is invalid")
      else:
         objMsg.printMsg("AMPS check return data: %s" % (str(data)))
         ScrCmds.raiseException(11044, "AMPS Check Failure: Unable determine APMS status")
      objPwrCtrl.powerCycle()

###########################################################################################################
class CZoneXferTest(CState):
   """
      Zone Transfer Test - Write/Read
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut
      self.IDmaxLBA = 0

   #-------------------------------------------------------------------------------------------------------
   def run(self):

      Debug = 0
      oSerial = serialScreen.sptDiagCmds()

      if objRimType.CPCRiser():
         eval(self.params["XFER_TYPE"]).update({"DEBUG_FLAG" : 0 })   # Workaround for CPC EC11169

      tmpdct = eval(self.params["XFER_TYPE"])
      if tmpdct.has_key("adj_serp_width"):
         try:
            Drive_Serp_Width = TP.VbarNomSerpentWidth
         except:
            sptCmds.enableDiags()
            Drive_Serp_Width = oSerial.GetSerpWidth()     # from 2>I,1,11 command
            objPwrCtrl.powerCycle()

         import math
         tmpdct["NUM_SERP"] = int(math.ceil(float(tmpdct["NUM_SERP"]) * float(tmpdct["adj_serp_width"]) / float(Drive_Serp_Width)))
         tmpdct.pop("adj_serp_width")
         objMsg.printMsg("Drive_Serp_Width = %s Compensated dict = %s" % (Drive_Serp_Width, eval(self.params["XFER_TYPE"])))

      self.set_rpm()
      if int(self.dut.driveattr['SPINDLE_RPM']) == 5400:
         eval(self.params["XFER_TYPE"])["REV_TIME"] = 0x2B66
      elif int(self.dut.driveattr['SPINDLE_RPM']) == 7200:
         eval(self.params["XFER_TYPE"])["REV_TIME"] = 0x208D

      if objRimType.CPCRiser():
         theCell.disableESlip()     # Fix CPC T638 Unlock hang-up

      objPwrCtrl.powerCycle()       #Full powercycle to make sure SATA speed is set correctly.
      ICmd.HardReset()
      ICmd.UnlockFactoryCmds()

      if testSwitch.FE_0148727_231166_P_ENABLE_WC_ZONE_XFER:
         if testSwitch.BF_0151111_231166_P_USE_ALL_INTF_CAPABLE_CACHE_CMD:
            ICmd.enable_WriteCache()
         else:
            SATA_SetFeatures.enable_WriteCache()

      try:
         if not testSwitch.SMRPRODUCT:
            ICmd.St(eval(self.params["XFER_TYPE"]))    # Zone based transfer test - Write or Read
         else: #for SMR product, we need to do averaging for different heads
            #--- Save P598 table if any---
            self.hdata = []
            self.ThruLst = []
            try: # save table content and restore it later
               self.savedTable = self.dut.dblData.Tables('P598_ZONE_XFER_RATE').tableDataObj()
            except:
               self.savedTable = []
               pass
            if len(self.savedTable):
               self.dut.dblData.Tables('P598_ZONE_XFER_RATE').deleteIndexRecords(confirmDelete=1) #del indexrecords
               self.dut.dblData.delTable('P598_ZONE_XFER_RATE', 1) #del table
            #--- Get throughput rate from H0 and H1---
            for head in xrange(self.dut.imaxHead):
               objMsg.printMsg("Testing Head %d..." % head)
               if testSwitch.virtualRun:
                  self.hdata = [[{'STATUS': '0', 'DATA_RATE': '111.64708', 'OCCURRENCE': 3, 'SPC_ID': 1, 'START_LBA': '787170', 'LBAS_XFERED': '559993', 'RATIO': '1.02', 'PARAMETER_1': '0', 'TEST_SEQ_EVENT': 1, 'END_LBA': '80FCE9', 'CALC_RATE': '108.42258', 'DATA_ZONE': '1', 'SEQ': 1, 'LBA_AT_MIN_TIME': '80FCE9', 'LBA_AT_MAX_TIME': '79ADF2', 'MAX_TIME_PER_XFER': '57659', 'TIME': '2449093', 'MIN_TIME_PER_XFER': '201'}, {'STATUS': '0', 'DATA_RATE': '111.10198', 'OCCURRENCE': 3, 'SPC_ID': 1, 'START_LBA': 'E04E80', 'LBAS_XFERED': '559993', 'RATIO': '1.02', 'PARAMETER_1': '0', 'TEST_SEQ_EVENT': 1, 'END_LBA': 'E8D9F9', 'CALC_RATE': '108.59137', 'DATA_ZONE': '2', 'SEQ': 1, 'LBA_AT_MIN_TIME': 'E8D9F9', 'LBA_AT_MAX_TIME': 'E15B62', 'MAX_TIME_PER_XFER': '29339', 'TIME': '2461109', 'MIN_TIME_PER_XFER': '201'}, {'STATUS': '0', 'DATA_RATE': '107.87711', 'OCCURRENCE': 3, 'SPC_ID': 1, 'START_LBA': '2B37550', 'LBAS_XFERED': '550393', 'RATIO': '1.01', 'PARAMETER_1': '0', 'TEST_SEQ_EVENT': 1, 'END_LBA': '2BBDB49', 'CALC_RATE': '106.71923', 'DATA_ZONE': '3', 'SEQ': 1, 'LBA_AT_MIN_TIME': '2BBDB49', 'LBA_AT_MAX_TIME': '2B483AF', 'MAX_TIME_PER_XFER': '44838', 'TIME': '2491229', 'MIN_TIME_PER_XFER': '359'}, {'STATUS': '0', 'DATA_RATE': '107.40563', 'OCCURRENCE': 3, 'SPC_ID': 1, 'START_LBA': '37F6610', 'LBAS_XFERED': '547193', 'RATIO': '1.01', 'PARAMETER_1': '0', 'TEST_SEQ_EVENT': 1, 'END_LBA': '387BF89', 'CALC_RATE': '106.13038', 'DATA_ZONE': '4', 'SEQ': 1, 'LBA_AT_MIN_TIME': '387BF89', 'LBA_AT_MAX_TIME': '3807C5F', 'MAX_TIME_PER_XFER': '54824', 'TIME': '2487617', 'MIN_TIME_PER_XFER': '333'}, {'STATUS': '0', 'DATA_RATE': '103.18026', 'OCCURRENCE': 3, 'SPC_ID': 1, 'START_LBA': '561CA40', 'LBAS_XFERED': '543993', 'RATIO': '0.97', 'PARAMETER_1': '0', 'TEST_SEQ_EVENT': 1, 'END_LBA': '56A1739', 'CALC_RATE': '105.33057', 'DATA_ZONE': '5', 'SEQ': 1, 'LBA_AT_MIN_TIME': '56A1739', 'LBA_AT_MAX_TIME': '5629723', 'MAX_TIME_PER_XFER': '28760', 'TIME': '2574345', 'MIN_TIME_PER_XFER': '207'}, {'STATUS': '0', 'DATA_RATE': '101.68689', 'OCCURRENCE': 3, 'SPC_ID': 1, 'START_LBA': '5E8AD80', 'LBAS_XFERED': '542393', 'RATIO': '0.97', 'PARAMETER_1': '0', 'TEST_SEQ_EVENT': 1, 'END_LBA': '5F0F439', 'CALC_RATE': '104.53686', 'DATA_ZONE': '6', 'SEQ': 1, 'LBA_AT_MIN_TIME': '5E9EA02', 'LBA_AT_MAX_TIME': '5E9C44E', 'MAX_TIME_PER_XFER': '24739', 'TIME': '2604469', 'MIN_TIME_PER_XFER': '375'}, {'STATUS': '0', 'DATA_RATE': '100.88495', 'OCCURRENCE': 3, 'SPC_ID': 1, 'START_LBA': '7A921E0', 'LBAS_XFERED': '537593', 'RATIO': '0.96', 'PARAMETER_1': '0', 'TEST_SEQ_EVENT': 1, 'END_LBA': '7B155D9', 'CALC_RATE': '104.06523', 'DATA_ZONE': '7', 'SEQ': 1, 'LBA_AT_MIN_TIME': '7B155D9', 'LBA_AT_MAX_TIME': '7A934BA', 'MAX_TIME_PER_XFER': '35611', 'TIME': '2601940', 'MIN_TIME_PER_XFER': '89'}, {'STATUS': '0', 'DATA_RATE': '91.54518', 'OCCURRENCE': 3, 'SPC_ID': 1, 'START_LBA': '84F3EE0', 'LBAS_XFERED': '532793', 'RATIO': '0.88', 'PARAMETER_1': '0', 'TEST_SEQ_EVENT': 1, 'END_LBA': '8576019', 'CALC_RATE': '103.48380', 'DATA_ZONE': '8', 'SEQ': 1, 'LBA_AT_MIN_TIME': '8576019', 'LBA_AT_MAX_TIME': '85051B6', 'MAX_TIME_PER_XFER': '247581', 'TIME': '2841797', 'MIN_TIME_PER_XFER': '148'}, {'STATUS': '0', 'DATA_RATE': '104.43247', 'OCCURRENCE': 3, 'SPC_ID': 1, 'START_LBA': 'A1F5298', 'LBAS_XFERED': '527993', 'RATIO': '1.01', 'PARAMETER_1': '0', 'TEST_SEQ_EVENT': 1, 'END_LBA': 'A276111', 'CALC_RATE': '102.55749', 'DATA_ZONE': '9', 'SEQ': 1, 'LBA_AT_MIN_TIME': 'A276111', 'LBA_AT_MAX_TIME': 'A206176', 'MAX_TIME_PER_XFER': '58009', 'TIME': '2468668', 'MIN_TIME_PER_XFER': '208'}, {'STATUS': '0', 'DATA_RATE': '103.67321', 'OCCURRENCE': 3, 'SPC_ID': 1, 'START_LBA': 'AB66188', 'LBAS_XFERED': '523193', 'RATIO': '1.02', 'PARAMETER_1': '0', 'TEST_SEQ_EVENT': 1, 'END_LBA': 'ABE5D41', 'CALC_RATE': '101.45388', 'DATA_ZONE': '10', 'SEQ': 1, 'LBA_AT_MIN_TIME': 'ABE5D41', 'LBA_AT_MAX_TIME': 'AB75D8C', 'MAX_TIME_PER_XFER': '41720', 'TIME': '2464140', 'MIN_TIME_PER_XFER': '339'}],
                                [{'STATUS': '0', 'DATA_RATE': '111.64708', 'OCCURRENCE': 3, 'SPC_ID': 1, 'START_LBA': '787170', 'LBAS_XFERED': '559993', 'RATIO': '1.02', 'PARAMETER_1': '0', 'TEST_SEQ_EVENT': 1, 'END_LBA': '80FCE9', 'CALC_RATE': '108.42258', 'DATA_ZONE': '1', 'SEQ': 1, 'LBA_AT_MIN_TIME': '80FCE9', 'LBA_AT_MAX_TIME': '79ADF2', 'MAX_TIME_PER_XFER': '57659', 'TIME': '2449093', 'MIN_TIME_PER_XFER': '201'}, {'STATUS': '0', 'DATA_RATE': '111.10198', 'OCCURRENCE': 3, 'SPC_ID': 1, 'START_LBA': 'E04E80', 'LBAS_XFERED': '559993', 'RATIO': '1.02', 'PARAMETER_1': '0', 'TEST_SEQ_EVENT': 1, 'END_LBA': 'E8D9F9', 'CALC_RATE': '108.59137', 'DATA_ZONE': '2', 'SEQ': 1, 'LBA_AT_MIN_TIME': 'E8D9F9', 'LBA_AT_MAX_TIME': 'E15B62', 'MAX_TIME_PER_XFER': '29339', 'TIME': '2461109', 'MIN_TIME_PER_XFER': '201'}, {'STATUS': '0', 'DATA_RATE': '107.87711', 'OCCURRENCE': 3, 'SPC_ID': 1, 'START_LBA': '2B37550', 'LBAS_XFERED': '550393', 'RATIO': '1.01', 'PARAMETER_1': '0', 'TEST_SEQ_EVENT': 1, 'END_LBA': '2BBDB49', 'CALC_RATE': '106.71923', 'DATA_ZONE': '3', 'SEQ': 1, 'LBA_AT_MIN_TIME': '2BBDB49', 'LBA_AT_MAX_TIME': '2B483AF', 'MAX_TIME_PER_XFER': '44838', 'TIME': '2491229', 'MIN_TIME_PER_XFER': '359'}, {'STATUS': '0', 'DATA_RATE': '107.40563', 'OCCURRENCE': 3, 'SPC_ID': 1, 'START_LBA': '37F6610', 'LBAS_XFERED': '547193', 'RATIO': '1.01', 'PARAMETER_1': '0', 'TEST_SEQ_EVENT': 1, 'END_LBA': '387BF89', 'CALC_RATE': '106.13038', 'DATA_ZONE': '4', 'SEQ': 1, 'LBA_AT_MIN_TIME': '387BF89', 'LBA_AT_MAX_TIME': '3807C5F', 'MAX_TIME_PER_XFER': '54824', 'TIME': '2487617', 'MIN_TIME_PER_XFER': '333'}, {'STATUS': '0', 'DATA_RATE': '103.18026', 'OCCURRENCE': 3, 'SPC_ID': 1, 'START_LBA': '561CA40', 'LBAS_XFERED': '543993', 'RATIO': '0.97', 'PARAMETER_1': '0', 'TEST_SEQ_EVENT': 1, 'END_LBA': '56A1739', 'CALC_RATE': '105.33057', 'DATA_ZONE': '5', 'SEQ': 1, 'LBA_AT_MIN_TIME': '56A1739', 'LBA_AT_MAX_TIME': '5629723', 'MAX_TIME_PER_XFER': '28760', 'TIME': '2574345', 'MIN_TIME_PER_XFER': '207'}, {'STATUS': '0', 'DATA_RATE': '101.68689', 'OCCURRENCE': 3, 'SPC_ID': 1, 'START_LBA': '5E8AD80', 'LBAS_XFERED': '542393', 'RATIO': '0.97', 'PARAMETER_1': '0', 'TEST_SEQ_EVENT': 1, 'END_LBA': '5F0F439', 'CALC_RATE': '104.53686', 'DATA_ZONE': '6', 'SEQ': 1, 'LBA_AT_MIN_TIME': '5E9EA02', 'LBA_AT_MAX_TIME': '5E9C44E', 'MAX_TIME_PER_XFER': '24739', 'TIME': '2604469', 'MIN_TIME_PER_XFER': '375'}, {'STATUS': '0', 'DATA_RATE': '100.88495', 'OCCURRENCE': 3, 'SPC_ID': 1, 'START_LBA': '7A921E0', 'LBAS_XFERED': '537593', 'RATIO': '0.96', 'PARAMETER_1': '0', 'TEST_SEQ_EVENT': 1, 'END_LBA': '7B155D9', 'CALC_RATE': '104.06523', 'DATA_ZONE': '7', 'SEQ': 1, 'LBA_AT_MIN_TIME': '7B155D9', 'LBA_AT_MAX_TIME': '7A934BA', 'MAX_TIME_PER_XFER': '35611', 'TIME': '2601940', 'MIN_TIME_PER_XFER': '89'}, {'STATUS': '0', 'DATA_RATE': '91.54518', 'OCCURRENCE': 3, 'SPC_ID': 1, 'START_LBA': '84F3EE0', 'LBAS_XFERED': '532793', 'RATIO': '0.88', 'PARAMETER_1': '0', 'TEST_SEQ_EVENT': 1, 'END_LBA': '8576019', 'CALC_RATE': '103.48380', 'DATA_ZONE': '8', 'SEQ': 1, 'LBA_AT_MIN_TIME': '8576019', 'LBA_AT_MAX_TIME': '85051B6', 'MAX_TIME_PER_XFER': '247581', 'TIME': '2841797', 'MIN_TIME_PER_XFER': '148'}, {'STATUS': '0', 'DATA_RATE': '104.43247', 'OCCURRENCE': 3, 'SPC_ID': 1, 'START_LBA': 'A1F5298', 'LBAS_XFERED': '527993', 'RATIO': '1.01', 'PARAMETER_1': '0', 'TEST_SEQ_EVENT': 1, 'END_LBA': 'A276111', 'CALC_RATE': '102.55749', 'DATA_ZONE': '9', 'SEQ': 1, 'LBA_AT_MIN_TIME': 'A276111', 'LBA_AT_MAX_TIME': 'A206176', 'MAX_TIME_PER_XFER': '58009', 'TIME': '2468668', 'MIN_TIME_PER_XFER': '208'}, {'STATUS': '0', 'DATA_RATE': '103.67321', 'OCCURRENCE': 3, 'SPC_ID': 1, 'START_LBA': 'AB66188', 'LBAS_XFERED': '523193', 'RATIO': '1.02', 'PARAMETER_1': '0', 'TEST_SEQ_EVENT': 1, 'END_LBA': 'ABE5D41', 'CALC_RATE': '101.45388', 'DATA_ZONE': '10', 'SEQ': 1, 'LBA_AT_MIN_TIME': 'ABE5D41', 'LBA_AT_MAX_TIME': 'AB75D8C', 'MAX_TIME_PER_XFER': '41720', 'TIME': '2464140', 'MIN_TIME_PER_XFER': '339'}]]
                  param = {"ENDING_ZONE": (59)}
                  self.param_spcid = 1
               else:
                  param = eval(self.params["XFER_TYPE"])
                  param["HEAD_TO_TEST"] = head
                  self.param_spcid = param["spc_id"] # require this in dBlog table
                  ICmd.St(param)    # Zone based transfer test - Write or Read
                  self.hdata.append(self.dut.dblData.Tables('P598_ZONE_XFER_RATE').tableDataObj())
                  self.dut.dblData.Tables('P598_ZONE_XFER_RATE').deleteIndexRecords(confirmDelete=1) #del indexrecords
                  self.dut.dblData.delTable('P598_ZONE_XFER_RATE', 1) #del table
               if Debug:
                  objMsg.printMsg("H%d Dblog data: %s" % (head, self.hdata[head]))

            #--- Get max zone num ---
            end_zone = param["ENDING_ZONE"]
            if self.dut.imaxHead != len(self.hdata):
               objMsg.printMsg("maxNumHead %d LengthHeadData %s " % (self.dut.imaxHead, len(self.hdata)))
               ScrCmds.raiseException(10506,  "Throughput data is not measured over all heads")
            if Debug:
               objMsg.printMsg("self.dut.numZones: %d, Max_zone: %d, maxNumHead: %d, LengthHeadData: %s" % (self.dut.numZones, end_zone, self.dut.imaxHead, len(self.hdata)))

            #--- Getting Avg from all the heads ---
            #Loop for max zone
            #if zone missing from both table, skip this zone
            for i in xrange(end_zone + 1): #Create Throughput List
               zonedata = {'zone': i, 'Thruput': 0, 'Cal_Thruput': 0, 'Ratio': 0, 'StartLBA': 0, 'EndLBA': 0}
               firstValiddata = True
               for head in xrange(self.dut.imaxHead):
                  tmpdict = self.search_zonetable(head, i)
                  if tmpdict != None and firstValiddata:
                     zonedata = {'zone': int(tmpdict['DATA_ZONE']), 'Thruput': float(tmpdict['DATA_RATE']), 'Cal_Thruput': float(tmpdict['CALC_RATE']), 'Ratio': float(tmpdict['RATIO']), 'StartLBA': int(tmpdict['START_LBA'], 16), 'EndLBA': int(tmpdict['END_LBA'], 16)}
                     firstValiddata = False
                  elif tmpdict != None:
                     tmpzone = int(tmpdict['DATA_ZONE'])
                     tmpthruput = self.GetAve(zonedata['Thruput'], float(tmpdict['DATA_RATE']))
                     tmpcalthruput = self.GetAve(zonedata['Cal_Thruput'], float(tmpdict['CALC_RATE']))
                     tmpratio = self.GetAve(zonedata['Ratio'], float(tmpdict['RATIO']))

                     tmpstartlba = self.GetData(zonedata['StartLBA'], int(tmpdict['START_LBA'], 16), ChkMin = True)
                     tmpendlba = self.GetData(zonedata['EndLBA'], int(tmpdict['END_LBA'], 16), ChkMin = False)
                     zonedata = {'zone': tmpzone, 'Thruput': tmpthruput, 'Cal_Thruput': tmpcalthruput, 'Ratio': tmpratio, 'StartLBA': tmpstartlba, 'EndLBA': tmpendlba}
                  if Debug:
                     objMsg.printMsg("zonedata : %s" % zonedata)
               if not firstValiddata:
                  self.ThruLst.append(zonedata)

            if Debug:
               objMsg.printMsg("ThruLst: %s" % self.ThruLst)

            #--- Create DBlog table ---
            self.PutDbLog()
            del self.hdata
            del self.ThruLst
            del self.savedTable
         if hasattr(TP,'prm_598_spec') and not testSwitch.virtualRun:
            self.DataThroughput_Check('P598_ZONE_XFER_RATE')

         if testSwitch.IOWriteReadRemoval and self.params.get('XFER_MODE', 'READ') == 'WRITE':
            self.WR_AddDict('P598_ZONE_XFER_RATE')

         if testSwitch.FE_0132889_7955_CREATE_P598_ZONE_DATA_RATE_TABLE and not testSwitch.virtualRun:
            self.createP598ZoneDataRateTable()

      except Exception, M:
         dct = eval(self.params["XFER_TYPE"]).copy()
         dct.update({"DISPLAY_WEAKEST_HEAD" :1})
         try:
            ICmd.St(dct)  #for EC10578 data collection
         except:
            pass
         raise M

      if testSwitch.FE_0148727_231166_P_ENABLE_WC_ZONE_XFER:
         objPwrCtrl.powerCycle(5000,12000,10,30, ataReadyCheck = True) #TODO enable #ataReadyCheck = False)#

      if testSwitch.EnableDebugLogging_T598:
         #sptCmds.enableDiags()
         oSerial.quickDiag()
         oSerial.gotoLevel('T')
         oSerial.dumpReassignedSectorList()
         oSerial.gotoLevel('1')
         oSerial.getCriticalEventLog()
         objPwrCtrl.powerCycle()

   def GetData(self, old, new, ChkMin = True):
      if ChkMin:
         return min(old, new)
      else:
         return max(old, new)

   def GetAve(self, old, new):
      if new <= 0:      # if new is invalid, no change
         return old

      if old <= 0:
         return new

      return (old + new) / 2

   def search_zonetable(self, head = 0, zone = 0):

      for item in self.hdata[head]:
         if item["DATA_ZONE"] == str(zone):
            return item
      else:
         return None

   def PutDbLog(self):
      #Restore saved table
      for i in self.savedTable:
         self.dut.dblData.Tables('P598_ZONE_XFER_RATE').addRecord(i)

      #Update the table
      curSeq, occurrence, testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
      for i in self.ThruLst:
         self.dut.dblData.Tables('P598_ZONE_XFER_RATE').addRecord({
            'SPC_ID': self.param_spcid,
            'OCCURRENCE': occurrence,
            'SEQ': curSeq,
            'TEST_SEQ_EVENT': testSeqEvent,

            'DATA_ZONE': str(i['zone']),
            'DATA_RATE': str(i['Thruput']),
            'CALC_RATE': str(i['Cal_Thruput']),
            'RATIO': str(i['Ratio']),

            'START_LBA': '%X' % i['StartLBA'],
            'END_LBA': '%X' %  i['EndLBA'],
            'LBAS_XFERED': (i['EndLBA'] - i['StartLBA']), # note, this must be numeral

            'TIME': str(0),
            'STATUS': str(0),
            'PARAMETER_1': str(0),
            'LBA_AT_MIN_TIME': str(0),
            'LBA_AT_MAX_TIME': str(0),
            'MIN_TIME_PER_XFER': str(0),
            'MAX_TIME_PER_XFER': str(0),
         })
      objMsg.printMsg("P598_ZONE_XFER_RATE Table after Averaging")
      objMsg.printDblogBin(self.dut.dblData.Tables('P598_ZONE_XFER_RATE'))
   #-------------------------------------------------------------------------------------------------------
   def createP598ZoneDataRateTable(self):
      """
      For GOTF use,   indicates failure during WRITE or READ pass during T598, spec'd by stateparams.

      'WRITE_XFER' : "{... 'ZONE_SPEC': [150,145,105,104,103,101,100,99,98,96,95,94,92,89,88,86,84,82,80,77,76,73,71,68,65,63,60,58,55,54] }
      'READ_XFER'  : "{... 'ZONE_SPEC': [150,145,105,104,103,101,100,99,98,96,95,94,92,89,88,86,84,82,80,77,76,73,71,68,65,63,60,58,55,54] }

      'ZONE_SPEC' - IOPS spec, the actual IOPS measurement has to be greater than the spec, or the zone is marked failed.
      """
      curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
      tabledata = self.dut.dblData.Tables('P598_ZONE_XFER_RATE').tableDataObj()
      wrtNumZoneFail = 0
      rdNumZoneFail = 0
      totalZonesFail = 0
      wrt_rd = ""

      for record in range(len(tabledata)):
         thisZonePassFail = "PASS"
         dataZone = int(tabledata[record]['DATA_ZONE'])
         dataRateSpec = self.params["ZONE_SPEC"][dataZone]
         dataRate = int((round(float(tabledata[record]['DATA_RATE']),0)))

         if int(tabledata[record]['SPC_ID']) == 1: # write
            wrt_rd = "WRITE"
            if dataRate < dataRateSpec:
               thisZonePassFail = "FAIL"
               wrtNumZoneFail += 1

         if int(tabledata[record]['SPC_ID']) == 2:   # read
            wrt_rd = "READ"
            if dataRate < dataRateSpec:
               thisZonePassFail = "FAIL"
               rdNumZoneFail += 1

         if wrt_rd == "WRITE":
            totalZonesFail = wrtNumZoneFail
         elif wrt_rd == "READ":
            totalZonesFail = rdNumZoneFail

         self.dut.dblData.Tables('P598_ZONE_DATA_RATE').addRecord({
               'SPC_ID': -1,
               'OCCURRENCE' : occurrence,
               'SEQ' : curSeq,
               'TEST_SEQ_EVENT' : testSeqEvent,
               'DATA_ZONE' : dataZone,
               'DATA_RATE_SPEC' : dataRateSpec,
               'DATA_RATE' : dataRate,
               'WRITE_READ'  : wrt_rd,
               'PASS_FAIL'   : thisZonePassFail,
               'TOTAL_ZONES_FAIL' : totalZonesFail,
               })

      objMsg.printDblogBin(self.dut.dblData.Tables('P598_ZONE_DATA_RATE'))

   #-------------------------------------------------------------------------------------------------------
   def DataThroughput_Check(self, dblogname):
      """
      DataThroughput_Check function is used to check the Data ThroughPut(DATA_RATE) values extracted
      from P598_ZONE_XFER_RATE table against Design Requirement.

      Note: Try to run the function only if prm_598_spec is available in TestParameters.py.
      """
      objMsg.printMsg('########################################################')
      objMsg.printMsg(' P598 - DataThroughput Check against Design Requirement')
      objMsg.printMsg('########################################################')
      if testSwitch.virtualRun:
         tabledata = [{'STATUS': '0', 'DATA_RATE': '105.24865', 'OCCURRENCE': 1, 'SPC_ID': 1, 'START_LBA': '0',       'LBAS_XFERED': '2171446', 'RATIO': '0.96', 'PARAMETER_1': '0', 'TEST_SEQ_EVENT': 1, 'END_LBA': '212236',   'CALC_RATE': '106.73273', 'DATA_ZONE': '0',  'SEQ': 1, 'LBA_AT_MIN_TIME': '100E23',    'LBA_AT_MAX_TIME': '20027A',  'MAX_TIME_PER_XFER': '52991', 'TIME': '20689794', 'MIN_TIME_PER_XFER': '379'},
                      {'STATUS': '0', 'DATA_RATE': '103.21940', 'OCCURRENCE': 1, 'SPC_ID': 1, 'START_LBA': '200DBB0', 'LBAS_XFERED': '2177923', 'RATIO': '0.96', 'PARAMETER_1': '0', 'TEST_SEQ_EVENT': 1, 'END_LBA': '2221733',  'CALC_RATE': '107.05519', 'DATA_ZONE': '1',  'SEQ': 1, 'LBA_AT_MIN_TIME': '200E2A2',   'LBA_AT_MAX_TIME': '220DEA9', 'MAX_TIME_PER_XFER': '71229', 'TIME': '10302705', 'MIN_TIME_PER_XFER': '379'},
                      {'STATUS': '0', 'DATA_RATE': '105.83213', 'OCCURRENCE': 1, 'SPC_ID': 2, 'START_LBA': '0',        'LBAS_XFERED': '2171446', 'RATIO': '0.97', 'PARAMETER_1': '0', 'TEST_SEQ_EVENT': 1, 'END_LBA': '212236',   'CALC_RATE': '106.73273', 'DATA_ZONE': '0',  'SEQ': 2, 'LBA_AT_MIN_TIME': '3022F8',   'LBA_AT_MAX_TIME': '195CE',    'MAX_TIME_PER_XFER': '23740', 'TIME': '10211448', 'MIN_TIME_PER_XFER': '428'},
                      {'STATUS': '0', 'DATA_RATE': '104.22791', 'OCCURRENCE': 1, 'SPC_ID': 2, 'START_LBA': '200DBB0',  'LBAS_XFERED': '2177923', 'RATIO': '0.97', 'PARAMETER_1': '0', 'TEST_SEQ_EVENT': 1, 'END_LBA': '2221733',  'CALC_RATE': '107.05519', 'DATA_ZONE': '1',  'SEQ': 2, 'LBA_AT_MIN_TIME': '20CD709',  'LBA_AT_MAX_TIME': '200DC2F',  'MAX_TIME_PER_XFER': '15191', 'TIME': '10203016', 'MIN_TIME_PER_XFER': '362'}]
      else:
         try:
            tabledata = self.dut.dblData.Tables(dblogname).tableDataObj()
         except:
            ScrCmds.raiseException(14537, "No valid data in %s table." %dblogname)
      if not testSwitch.NoIO:
         oSerial = serialScreen.sptDiagCmds()
         oSerial.quickDiag()
         AGBStatus = oSerial.GetAGBStatus()
         objMsg.printMsg("AGB Status : %s " %(AGBStatus))
         if testSwitch.ROSEWOOD7:
            AGBRemapZones = ['0','1','2','3']
         elif testSwitch.CHENGAI:
            AGBRemapZones = ['0','1','2']

      DBLog_dict = []
      DriveCap = 0
      DBLog_RatioDict = []
      DBLog_StartLbaDict = []

      if self.IDmaxLBA == 0:
         ret = CIdentifyDevice().ID
         self.IDmaxLBA = ret['IDDefaultLBAs']
         if ret['IDCommandSet5'] & 0x400:
            self.IDmaxLBA = ret['IDDefault48bitLBAs']
         DriveCap = str((self.IDmaxLBA * self.dut.IdDevice['Logical Sector Size'])/1000000000)
      else:
         DriveCap = str((self.IDmaxLBA * 512)/1000000000)   # return value is already in 512 sector size

      rpm = self.dut.driveattr.get('SPINDLE_RPM','5400')

      objMsg.printMsg("SPINDLE_RPM:%s DriveCap:%s Numhead:%s" %(rpm, DriveCap, self.dut.imaxHead) )

      # Get DATA_RATE values from table object and transfer to DBLog_dict.
      # Inorder to support Decon drives, transfer the DATA_RATE values only if,
      #  1. START_LBA notequal to END_LBA, and
      #  2. END_LBA less than MAX LBA
      minAllowedDataRate = 46.0
      for i in tabledata:
         if str(i['SPC_ID']) == str(eval(self.params["XFER_TYPE"])["spc_id"]):
            if not testSwitch.NoIO and (AGBStatus and i['DATA_ZONE'] in AGBRemapZones):
               objMsg.printMsg("AGB enabled... Skip remapped zone %s" % i['DATA_ZONE'])
               continue
            if (int(i['START_LBA'],16)!=int(i['END_LBA'],16)) and (int(i['END_LBA'],16) < self.IDmaxLBA):
               DBLog_dict.append(float(i['DATA_RATE']))
               DBLog_RatioDict.append(i['DATA_ZONE'] + ':' + i['RATIO'])
               DBLog_StartLbaDict.append(int(i['START_LBA'],16))
            else:
               break

      # Get Design Requirement values from TestParameters.py based on drive capacity calculated.
      if testSwitch.IS_2D_DRV == 0 and self.dut.BG in ['SBS'] and DriveCap == '500' and min(DBLog_dict) <= minAllowedDataRate:
         msg = 'data_rate =%s limit=%02.1f' %(min(DBLog_dict), minAllowedDataRate)
         objMsg.printMsg(msg)
         ScrCmds.raiseException(10578, msg)
                  
      # Get Design Requirement values from TestParameters.py based on drive capacity calculated.
      # If values found, generate the criteria string for,
      #     'offset':0 -> First User Zone == data_rate -> DBLog_dict[0]
      #     'offset':-1 -> Last User Zone == data_rate -> DBLog_dict[-1]
      # If values not found, fail the drive.

      try:
         data_rate = TP.prm_598_spec.get(rpm)[DriveCap][str(self.dut.imaxHead)]
      except TypeError:
         data_rate = TP.prm_598_spec.get(DriveCap,None)
      except KeyError:
        if testSwitch.WA_0256539_480505_SKDC_M10P_BRING_UP_DEBUG_OPTION:
         data_rate = TP.prm_598_spec.get(rpm)['4000']['10']
        else:
         objMsg.printMsg('KeyError: TP.prm_598_spec=%s' %str(TP.prm_598_spec))
         raise

      if data_rate is None:
         objMsg.printMsg('Drive capacity %sG not found in prm_598_spec' %DriveCap)
         ScrCmds.raiseException(10578, 'Drive capacity not found in prm_598_spec')

      if len(data_rate) == 2:
         try:
            objMsg.printMsg('Find first and last user zone...')
            MinLbaIndex = DBLog_StartLbaDict.index(min(DBLog_StartLbaDict)) # First User Zone, with HostLBA = 0
            MaxLbaIndex = -1 #DBLog_StartLbaDict.index(max(DBLog_StartLbaDict)) # Last User Zone, with max HostLBA
            criteria = [{'offset':MinLbaIndex, 'data_rate':data_rate[0]},{'offset':MaxLbaIndex, 'data_rate':data_rate[1]}]
         except:
            criteria = [{'offset':0, 'data_rate':data_rate[0]},{'offset':-1, 'data_rate':data_rate[1]}]
            pass
      else:
         criteria = []
         count = 0
         for drate in data_rate:
            tmpdict = {'offset':count, 'data_rate': drate}
            criteria.append(tmpdict)
            count = count + 1

      objMsg.printMsg('Criteria - %s' % (criteria))

      #Check First and Last User Zone values against Design Requirement.
      for i in criteria:
         msg = 'data_rate rd=%02.1f limit=%02.1f' %(DBLog_dict[i['offset']],i['data_rate'])
         objMsg.printMsg(msg)

         if DBLog_dict[i['offset']] < i['data_rate']:
            msg = 'data_rate rd=%02.1f limit=%02.1f' %(DBLog_dict[i['offset']],i['data_rate'])
            objMsg.printMsg(msg)
            ScrCmds.raiseException(10578, msg)

      #Ratio Check
      ratiolimit = getattr(TP,'prm_598_limit', 0.8)

      if type(ratiolimit) == types.FloatType:
         for i in DBLog_RatioDict:
            FailData = re.split(':',i)
            if float(FailData[1]) < ratiolimit:
               ScrCmds.raiseException(10578,"Failed RATIO check - Zone:%d Ratio:%02.2f Limit:%02.2f" %(int(FailData[0]),float(FailData[1]),ratiolimit))
      else:
         for i in xrange(len(ratiolimit)):
            fdata = float(re.split(':', DBLog_RatioDict[i])[1])
            if fdata < ratiolimit[i]:
               ScrCmds.raiseException(10578,"Failed RATIO check - Zone:%d Ratio:%02.2f Limit:%02.2f" %(i, fdata, ratiolimit[i]))
   #-------------------------------------------------------------------------------------------------------
   def guardBand(self):
      """ Detect variable guard band """
      sptCmds.enableDiags()
      sptCmds.gotoLevel('A')
      data = sptCmds.sendDiagCmd('F0')

      if testSwitch.virtualRun:
         data = "User      00000000 00000000 00000000 +1.195999E+3 00    01 00000000 00000000 014B    014B    0000   0016      0011      04FE      0000     00       CD"
      mat = re.search ('User (.*)', data)

      objPwrCtrl.powerCycle()
      return int(mat.group(0).split()[6])

   #-------------------------------------------------------------------------------------------------------
   def WR_AddDict(self, dblogname):
      '''
        This function is used to add Dict entry for Write Read Removal purpose
        For Write 598 only.
      '''
      objMsg.printMsg('########################################################')
      objMsg.printMsg(' P598 - WR_VERIFY Add Dictionary')
      objMsg.printMsg('########################################################')
      tabledata = self.dut.dblData.Tables(dblogname).tableDataObj()

      # Calculate Drive Capacity based on Max LBA value
      ret = CIdentifyDevice().ID
      self.IDmaxLBA = ret['IDDefaultLBAs']
      if ret['IDCommandSet5'] & 0x400:
         self.IDmaxLBA = ret['IDDefault48bitLBAs']

      # Get Start_Lba and End_Lba. Inorder to support Decon drives, get only if,
      #  1. START_LBA notequal to END_LBA, and
      #  2. END_LBA less than MAX LBA
      for i in tabledata:
         if str(i['SPC_ID']) == str(eval(self.params["XFER_TYPE"])["spc_id"]):
            if (int(i['START_LBA'],16)!=int(i['END_LBA'],16)) and (int(i['END_LBA'],16) < self.IDmaxLBA):
               RWDict = []
               RWDict.append ('Read')
               RWDict.append (int(i['START_LBA'],16))
               RWDict.append (int(i['END_LBA'],16))
               RWDict.append ('CZoneXferTest')
               objMsg.printMsg('WR_VERIFY appended - %s' % (RWDict))
               TP.RWDictGlobal.append (RWDict)
            else:
               break

   #-------------------------------------------------------------------------------------------------------
   def set_rpm(self, force=False):
      '''
       Determine the drive's RPM. Get drive's RPM using CTRL_L if not found.
      '''
      if (str(self.dut.driveattr.get('SPINDLE_RPM')) not in getattr(TP,'spindle_rpm',['5400','7200','10000','15000'])) or force:
         ScrCmds.statMsg("Detected spindle RPM: %s. Re-acquiring drive spindle RPM.." %str(self.dut.driveattr.get('SPINDLE_RPM','NONE')))
         oSerial = serialScreen.sptDiagCmds()
         sptCmds.enableDiags()
         try:
            rpm = int(oSerial.GetCtrl_L()['RPM'])
            self.dut.driveattr['SPINDLE_RPM'] = CInit_DriveInfo(self.dut).findRPMCategory(rpm)
            objPwrCtrl.powerCycle()
         except:
            ScrCmds.raiseException(10128, "Unable to determine drive's spindle rpm!")
      ScrCmds.statMsg("Drive's 'SPINDLE_RPM' = %s" %self.dut.driveattr['SPINDLE_RPM'])


###########################################################################################################
class CPackWrite(CState):
   """
      Class that performs Full Pack Write using SequentialWriteDMAExt
         Error reporting is enabled.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut
   #-------------------------------------------------------------------------------------------------------
   def run(self):

      if self.dut.nextOper == "FNG2" and testSwitch.NoIO:
         objMsg.printMsg("NoIO Full Pack Write...")

         #Need to identify SDnD drive. /Aq4 cmd uses this condition to set SED option
         if str(self.dut.driveConfigAttrs.get('SECURITY_TYPE',(0,None))[1]).rstrip() == 'SECURED BASE (SD AND D)':
            testSwitch.IS_SDnD = 1

         objPwrCtrl.powerCycle()
         import GIO
         GIO.CWriteDriveZero(self.dut, params={}).doWriteZeroPatt('', 'MaxLBA')
         return

      if testSwitch.FE_0163769_357260_P_SKIP_FORMAT_OR_PACK_WRITE_IF_ZERO_PAT_DONE:
         if str(self.dut.driveattr.get('ZERO_PTRN_RQMT', DriveAttributes.get('ZERO_PTRN_RQMT',None))).rstrip() == '20':
            objMsg.printMsg('CPackWrite: ZERO_PTRN_RQMT == 20 detected - skipping full pack write')
            return

      if testSwitch.FE_0151079_395340_P_FIX_TEST_TIME_FPW_T510_ON_3TB and testSwitch.MANTA_RAY_SAS:
         stepLBA = sctCnt = 4096   # For mantaray 3T can use 512, 1024 and 4096 with same as test time about 7 Hours.
      else:
         stepLBA = sctCnt = 256

      oProcess = CProcess()
      ICmd.HardReset()
      if testSwitch.FE_0138033_426568_P_SET_ZERO_PTRN_RQMT_IN_PACKWRITE :
         self.dut.driveattr['ZERO_PTRN_RQMT'] = getattr(TP, 'ZeroPatternRequirement', "20")
      result = ICmd.ClearBinBuff(WBF)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(11044, "Full Pack Zero Write - Failed to fill buffer for zero write")

      maxLBA = int(ICmd.GetMaxLBA()['MAX48'],16)-1
      if testSwitch.FE_0130092_7955_FPW_ALLOW_1_RETRY_ON_FAIL:
         for retry in range(0,2):
            if testSwitch.FE_0117027_399481_ENABLE_WRITE_CACHE_IN_PACK_WRITE:
               if testSwitch.BF_0151111_231166_P_USE_ALL_INTF_CAPABLE_CACHE_CMD:
                  ICmd.enable_WriteCache()
               else:
                  if testSwitch.BF_0145549_231166_P_FIX_538_ATA_CMDS_SIC:
                     SATA_SetFeatures.enable_WriteCache()
                  else:
                     ICmd.St(TP.enableWriteCache_538)
            objMsg.printMsg('Begin Full Pack Write')
            result = ICmd.SequentialWriteDMAExt(0, maxLBA, stepLBA, sctCnt)
            objMsg.printMsg('Full Pack Zero Write - Result %s' %str(result))
            if result['LLRET'] != 0:
               if testSwitch.FE_0128864_7955_DUMP_REGS_IF_FAIL_DURING_FPW:
                  try:
                     sptCmds.enableDiags()
                     sptCmds.sendDiagCmd(CTRL_I,printResult = True)
                  except:
                     pass
               if retry == 0:
                  objPwrCtrl.powerCycle()
                  ICmd.FlushCache()
                  continue
               ScrCmds.raiseException(12657, "Full Pack Zero Write Failed")
            else:
               break

      else:
         if testSwitch.FE_0117027_399481_ENABLE_WRITE_CACHE_IN_PACK_WRITE:
            if testSwitch.BF_0151111_231166_P_USE_ALL_INTF_CAPABLE_CACHE_CMD:
               ICmd.enable_WriteCache()
            else:
               if testSwitch.BF_0145549_231166_P_FIX_538_ATA_CMDS_SIC:
                  SATA_SetFeatures.enable_WriteCache()
               else:
                  ICmd.St(TP.enableWriteCache_538)
         objMsg.printMsg('maxLBA = %s' %str(maxLBA))
         objMsg.printMsg('stepLBA = %s' %str(stepLBA))
         objMsg.printMsg('sctCnt = %s' %str(sctCnt))
         objMsg.printMsg('Starting Full Pack Zero Write...')  
         result = ICmd.SequentialWriteDMAExt(0, maxLBA, stepLBA, sctCnt)
         objMsg.printMsg('Full Pack Zero Write - Result %s' %str(result))
         if result['LLRET'] != 0:
            if testSwitch.FE_0128864_7955_DUMP_REGS_IF_FAIL_DURING_FPW:
               try:
                  sptCmds.enableDiags()
                  sptCmds.sendDiagCmd(CTRL_I,printResult = True)
               except:
                  pass
            ScrCmds.raiseException(12657, "Full Pack Zero Write Failed")

      ICmd.FlushCache()
      if testSwitch.SMRPRODUCT:
         ICmd.FlushMediaCache()
      if testSwitch.FE_0117027_399481_ENABLE_WRITE_CACHE_IN_PACK_WRITE:
         objPwrCtrl.powerCycle()

      self.dut.driveattr['ZERO_PTRN_RQMT'] = "20"

###########################################################################################################
class CFullZeroCheck(CState):
   """
      Class that performs Full Pack Zero verify
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if testSwitch.FE_0000103_347508_ENABLE_ZERO_CHECK:
         if not ConfigVars[CN].get('CHECK_FULL_ZERO',0) and self.dut.nextOper not in ['CUST_CFG']:
            objMsg.printMsg('CHECK_FULL_ZERO set to 0, Skipping Full Pack Zero check!!!')
            return
         sctCnt = 0x800

         ICmd.HardReset()
         maxLBA = int(ICmd.GetMaxLBA()['MAX48'],16)-1
         result = ICmd.ZeroCheck(0, maxLBA, sctCnt)
         objMsg.printMsg('Full Pack Zero check result: %s' %result)
         if result['LLRET'] != OK:
            DriveAttributes['FULL_ZERO'] = 'FAIL'
            data = ICmd.GetBuffer(RBF, 0, 512)['DATA']
            objMsg.printMsg("failing read buffer")
            objMsg.printBin(data)
            ScrCmds.raiseException(14723, "Full Pack Zero Check - Failed to verify Zero Pattern")
         else:
            DriveAttributes['FULL_ZERO'] = 'PASS'
      else:
         sctCnt = 0x800

         ICmd.HardReset()
         maxLBA = int(ICmd.GetMaxLBA()['MAX48'],16)-1
         result = ICmd.ZeroCheck(0, maxLBA, sctCnt)
         objMsg.printMsg('Full Pack Zero check result: %s' %result)
         if result['LLRET'] != OK:
            ScrCmds.raiseException(14723, "Full Pack Zero Check - Failed to verify Zero Pattern")

      if testSwitch.CPCWriteReadRemoval:
         # Note ICmd.CommandLocation is not supported by SI
         objMsg.printMsg('Reset TrackingList to none after performing full pack read')
         result = ICmd.CommandLocation(3)
         objMsg.printMsg('result = %s' % result)
         self.TrackingList = ''
         objMsg.printMsg('Tracking List = %s' % self.dut.TrackingList)
         self.dut.objData.update({'TrackingList': self.dut.TrackingList})

         objMsg.printMsg('Reset tracking, numLBA = %d numTrackingZone = %d'% (self.dut.numLba,self.dut.numTrackingZone))
         result = ICmd.CommandLocation(1,self.dut.numTrackingZone,self.dut.numLba)

###########################################################################################################
class CZeroPattern(CState):
   """
      Write first and last n blocks (or full pack) with zero pattern
         - Blocks to write based on ZERO_PTRN_RQMT attribute
         - Default is 20 Million first / last LBAs
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):

      if testSwitch.BF_0196490_231166_P_FIX_TIER_SU_CUST_TEST_CUST_SCREEN:
         if CommitServices.isTierPN( self.dut.partNum ):
            objMsg.printMsg("Don't run Zero pattern/verify as tier drive.")
            raise Exceptions.BypassCustUniqueTest

      from CustomCfg import CCustomCfg
      zeroPatternLookup = {
         '10' : ('FirstandLast', 'First / Last 400K Lba Zero Write',       20971520 ),    # Write 20 million LBAs if < 20 Million
         '12' : ('FirstandLast', 'First / Last 1 Million LBA Zero Write',  20971520 ),    # - does not add much time
         '13' : ('FirstandLast', 'First / Last 2 Million LBA Zero Write',  20971520 ),    # - does not add much time
         '15' : ('FirstandLast', 'First / Last 20 Million LBA Zero Write', 20971520 ),
         '20' : ('All',          'Full Pack Zero Write',                   0        ),}

      # from CustomCfg import CCustomCfg
      # CustConfig = CCustomCfg()
      # CustConfig.getDriveConfigAttributes()

      zeroRequirement = str(self.dut.driveConfigAttrs.get('ZERO_PTRN_RQMT',(0,None))[1]).rstrip()
      if zeroRequirement in ['None','NA','']:
         objMsg.printMsg('No Zero pattern DCM Attribute detected - Applying 20 Million LBA Zero Write')
         zeroRequirement = '15'

      try:
         zeroType, zeroLabel, xferlength = zeroPatternLookup[zeroRequirement]
      except:
         ScrCmds.raiseException(11044, 'Zero Pattern Write Failed - DCM ZERO_PTRN_RQMT : %s not supported')

      currentAttrVal = str(self.dut.driveattr.get('ZERO_PTRN_RQMT', DriveAttributes.get('ZERO_PTRN_RQMT',None))).rstrip()

      if currentAttrVal not in ['None','','NONE'] and int(currentAttrVal) >= int(zeroRequirement):
         objMsg.printMsg('Skipping Zero Pattern Write  - Already complete - ZERO_PTRN_RQMT = %s' % zeroRequirement)
      else:
         objMsg.printMsg('Performing %s' % zeroLabel)
         maxLBA = int(ICmd.GetMaxLBA()['MAX48'],16)-1

         ICmd.HardReset()
         ICmd.enable_WriteCache()

         result = ICmd.ClearBinBuff(WBF)
         if result['LLRET'] != OK:
            ScrCmds.raiseException(11044, '%s - Failed to fill buffer for zero write' %zeroLabel)

         if zeroType == 'FirstandLast':
            self.zeroPatternWrite(0, xferlength, zeroLabel = zeroLabel)                   # Write first n lbas zero pattern
            self.zeroPatternWrite(maxLBA - xferlength + 1, maxLBA, zeroLabel = zeroLabel)  # Write last n lbas zero pattern
         if zeroType == 'All':
            self.zeroPatternWrite(0, maxLBA, zeroLabel = zeroLabel)                       # Write full pack zero pattern

         ICmd.FlushCache()
         if testSwitch.SMRPRODUCT:
            ICmd.FlushMediaCache()
         objPwrCtrl.powerCycle()                                                          # Power cycle to restore write cache setting

      self.dut.driveattr['ZERO_PTRN_RQMT'] = zeroRequirement

   def zeroPatternWrite(self, startlba, endlba, zeroLabel = 'Zero Pattern Write', stepLBA = 4096, sctCnt = 4096):

      ICmd.RestorePrimaryBuffer(BWR)
      ICmd.MakeAlternateBuffer( BWR , sctCnt , exc = 1  )    # 0x03 = Both Write and Read Buffer
      ICmd.ClearBinBuff(BWR)

      result = ICmd.SequentialWriteDMAExt(startlba, endlba, stepLBA, sctCnt)
      objMsg.printMsg('%s - Result %s' %(zeroLabel, str(result)))
      if result['LLRET'] != 0:
         if testSwitch.WA_0174392_470833_P_POWERCYCLE_UPON_RETRY_IN_ZERO_PATTERN_WRITE:
            objMsg.printMsg("base_IntfTest: zeroPatternWrite- power cycle before retry")
            objPwrCtrl.powerCycle()
            ICmd.enable_WriteCache()
         result = ICmd.SequentialWriteDMAExt(startlba, endlba, stepLBA, sctCnt)
         objMsg.printMsg('%s - Result %s' % (zeroLabel, str(result)))
         if result['LLRET'] != 0:
            try:
               try:
                  sptCmds.enableDiags()
                  sptCmds.sendDiagCmd(CTRL_I,printResult = True)                          # Dump regs if failed write operation
               finally:
                  sptCmds.enableESLIP()
            except:
               pass

            ScrCmds.raiseException(12657, '%s Failed' %zeroLabel)

      if testSwitch.IOWriteReadRemoval :
         RWDict = []
         RWDict.append ('Write')
         RWDict.append (startlba)
         RWDict.append (endlba)
         RWDict.append (zeroLabel)
         objMsg.printMsg('WR_VERIFY appended - %s' % (RWDict))
         TP.RWDictGlobal.append (RWDict)


###########################################################################################################
class CZeroValidate(CState):
   """
      Validates the first and last n blocks (or full pack) zero pattern
         - Blocks to write based on ZERO_PTRN_RQMT attribute
         - Default is 20 Million first / last LBAs
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if testSwitch.BF_0196490_231166_P_FIX_TIER_SU_CUST_TEST_CUST_SCREEN:
         if CommitServices.isTierPN( self.dut.partNum ):
            objMsg.printMsg("Don't run Zero pattern/verify as tier drive.")
            raise Exceptions.BypassCustUniqueTest

      zeroPatternLookup = {
         '10' : ('FirstandLast', 'First / Last 400K Lba Zero Pattern Check',        400000 ),
         '12' : ('FirstandLast', 'First / Last 1 Million LBA Zero Pattern Check',   1048576 ),
         '13' : ('FirstandLast', 'First / Last 2 Million LBA Zero Pattern Check',   1048576 ),
         '15' : ('FirstandLast', 'First / Last 20 Million LBA Zero Pattern Check',  20971520 ),
         '20' : ('All',          'Full Pack Zero Pattern Check',                    0        ),}

      from CustomCfg import CCustomCfg
      CustConfig = CCustomCfg()
      CustConfig.getDriveConfigAttributes()
      sctCnt = getattr(TP,  'zeroPatternValidate',  {}).get('sctCnt', 512)

      zeroRequirement = str(self.dut.driveConfigAttrs.get('ZERO_PTRN_RQMT',(0,None))[1]).rstrip()
      if zeroRequirement in ['None','NA','']:
         objMsg.printMsg('No Zero pattern DCM Attribute detected - Applying 20 Million LBA Zero Validation')
         zeroRequirement = '15'

      try:
         zeroType, zeroLabel, xferlength = zeroPatternLookup[zeroRequirement]
      except:
         ScrCmds.raiseException(11044, 'Zero Pattern Write Validate - DCM ZERO_PTRN_RQMT : %s not supported')

      objMsg.printMsg('Performing %s' % zeroLabel)
      maxLBA = int(ICmd.GetMaxLBA()['MAX48'],16)-1

      ICmd.HardReset()

      if zeroType == 'FirstandLast':
         self.zeroPatternValidate(0, xferlength, zeroLabel = zeroLabel, sctCnt = sctCnt)                   # Validate first n lbas zero pattern
         self.zeroPatternValidate(maxLBA - xferlength + 1, maxLBA, zeroLabel = zeroLabel, sctCnt = sctCnt) # Validate last n lbas zero pattern
      if zeroType == 'All':
         self.zeroPatternValidate(0, maxLBA, zeroLabel = zeroLabel, sctCnt = sctCnt)                       # Validate full pack zero pattern


   def zeroPatternValidate(self, startlba, endlba, zeroLabel = 'Zero Pattern Write', sctCnt = 512):

      ICmd.RestorePrimaryBuffer(BWR)
      ICmd.MakeAlternateBuffer( BWR , sctCnt )     # 0x03 = Both Write and Read Buffer
      ICmd.ClearBinBuff(BWR)

      result = ICmd.ZeroCheck(startlba, endlba, sctCnt)
      objMsg.printMsg('%s - Result %s' %(zeroLabel, str(result)))
      if result['LLRET'] != 0:
         ScrCmds.raiseException(14723, '%s Failed' %zeroLabel)


###########################################################################################################
class C400KZeros(CState):
   """
      Write first and last 400K blocks with zero pattern
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      xferlength = 400000
      stepLBA = sctCnt = 256

      ICmd.HardReset()
      result = ICmd.ClearBinBuff(WBF)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(11044, "400K Zero Write - Failed to fill buffer for zero write")

      result = ICmd.SequentialWriteDMAExt(0, xferlength - 1, stepLBA, sctCnt)
      objMsg.printMsg('First 400K - Result %s' %str(result))
      if result['LLRET'] != 0:
         result = ICmd.SequentialWriteDMAExt(0, xferlength - 1, stepLBA, sctCnt)
         objMsg.printMsg('First 400K - Result %s' %str(result))
         if result['LLRET'] != 0:
            ScrCmds.raiseException(12657, "400K Zero DMA Write Failed")

      if testSwitch.IOWriteReadRemoval :
         RWDict = []
         RWDict.append ('Read')
         RWDict.append (0)
         RWDict.append (xferlength-1)
         RWDict.append ('C400KZeros')
         objMsg.printMsg('WR_VERIFY appended - %s' % (RWDict))
         TP.RWDictGlobal.append (RWDict)

      maxLBA = int(ICmd.GetMaxLBA()['MAX48'],16)-1
      result = ICmd.SequentialWriteDMAExt(maxLBA - xferlength +1, maxLBA, stepLBA, sctCnt)
      objMsg.printMsg('Last 400K - Result %s' %str(result))
      if result['LLRET'] != 0:
         result = ICmd.SequentialWriteDMAExt(maxLBA - xferlength +1, maxLBA, stepLBA, sctCnt)
         objMsg.printMsg('Last 400K - Result %s' %str(result))
         if result['LLRET'] != 0:
            ScrCmds.raiseException(12657, "400K Zero DMA Write Failed")
      ICmd.FlushCache()
      if testSwitch.SMRPRODUCT:
         ICmd.FlushMediaCache()

      if testSwitch.IOWriteReadRemoval :
         RWDict = []
         RWDict.append ('Read')
         RWDict.append (maxLBA - xferlength +1)
         RWDict.append (maxLBA)
         RWDict.append ('C400KZeros')
         objMsg.printMsg('WR_VERIFY appended - %s' % (RWDict))
         TP.RWDictGlobal.append (RWDict)

      self.dut.driveattr['ZERO_PTRN_RQMT'] = '10'

###########################################################################################################
class C400KZeroCheck(CState):
   """
      Zero Verify first and last 400K blocks.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      xferlength = 400000
      sctCnt = 0x800

      ICmd.HardReset()
      result = ICmd.ZeroCheck(0, xferlength - 1, sctCnt)
      objMsg.printMsg('First 400K LBA Zero check result: %s' %result)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(14723, "400K Zero Check - Failed to verify Zero Pattern on first 400K LBAs")

      maxLBA = int(ICmd.GetMaxLBA()['MAX48'],16)-1
      result = ICmd.ZeroCheck(maxLBA - xferlength + 1, maxLBA, sctCnt)
      objMsg.printMsg('Last 400K LBA Zero check result: %s' %result)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(14723, "400K Zero Check - Failed to verify Zero Pattern on last 400K LBAs")

###########################################################################################################
class C1MZeros(CState):
   """
      Write first and last 1M blocks with zero pattern
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      xferlength = 1048576
      stepLBA = sctCnt = 256

      ICmd.HardReset()
      result = ICmd.ClearBinBuff(WBF)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(11044, "1M Zero Write - Failed to fill buffer for zero write")

      result = ICmd.SequentialWriteDMAExt(0, xferlength - 1, stepLBA, sctCnt)
      objMsg.printMsg('First 1M - Result %s' %str(result))
      if result['LLRET'] != 0:
         result = ICmd.SequentialWriteDMAExt(0, xferlength - 1, stepLBA, sctCnt)
         objMsg.printMsg('First 1M - Result %s' %str(result))
         if result['LLRET'] != 0:
            ScrCmds.raiseException(12657, "1M Zero DMA Write Failed")

      if testSwitch.IOWriteReadRemoval :
         RWDict = []
         RWDict.append ('Read')
         RWDict.append (0)
         RWDict.append (xferlength-1)
         RWDict.append ('C1MZeros')
         objMsg.printMsg('WR_VERIFY appended - %s' % (RWDict))
         TP.RWDictGlobal.append (RWDict)

      maxLBA = int(ICmd.GetMaxLBA()['MAX48'],16)-1
      result = ICmd.SequentialWriteDMAExt(maxLBA - xferlength +1, maxLBA, stepLBA, sctCnt)
      objMsg.printMsg('Last 1M - Result %s' %str(result))
      if result['LLRET'] != 0:
         result = ICmd.SequentialWriteDMAExt(maxLBA - xferlength +1, maxLBA, stepLBA, sctCnt)
         objMsg.printMsg('Last 1M - Result %s' %str(result))
         if result['LLRET'] != 0:
            ScrCmds.raiseException(12657, "1M Zero DMA Write Failed")
      ICmd.FlushCache()
      if testSwitch.SMRPRODUCT:
         ICmd.FlushMediaCache()

      if testSwitch.IOWriteReadRemoval :
         RWDict = []
         RWDict.append ('Read')
         RWDict.append (maxLBA - xferlength +1)
         RWDict.append (maxLBA)
         RWDict.append ('C1MZeros')
         objMsg.printMsg('WR_VERIFY appended - %s' % (RWDict))
         TP.RWDictGlobal.append (RWDict)

      if testSwitch.FE_0152254_357260_P_CHANGE_1M_ZERO_PTRN_RQMT_TO_12:
         self.dut.driveattr['ZERO_PTRN_RQMT'] = '12'
      else:
         self.dut.driveattr['ZERO_PTRN_RQMT'] = "25"

###########################################################################################################
class C20MZeros(CState):
   """
      Write first and last 20 Million blocks with zero pattern
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut

   #-------------------------------------------------------------------------------------------------------
   def run(self, xferlength = 20971520, Ste_Name = 'C20MZeros', ZERO_PTRN_RQMT = "15"):
      stepLBA = sctCnt = 256

      ICmd.HardReset()
      result = ICmd.ClearBinBuff(WBF)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(11044, "%s Zero Write - Failed to fill buffer for zero write" % Ste_Name)

      result = ICmd.SequentialWriteDMAExt(0, xferlength - 1, stepLBA, sctCnt)
      objMsg.printMsg('First %s - Result %s' % (Ste_Name, str(result)))
      if result['LLRET'] != 0:
         ScrCmds.raiseException(12657, "%s Zero Write Failed" % Ste_Name)

      if testSwitch.IOWriteReadRemoval :
         RWDict = []
         RWDict.append ('Read')
         RWDict.append (0)
         RWDict.append (xferlength-1)
         RWDict.append (Ste_Name)
         objMsg.printMsg('WR_VERIFY appended - %s' % (RWDict))
         TP.RWDictGlobal.append (RWDict)

      maxLBA = int(ICmd.GetMaxLBA()['MAX48'],16)-1
      result = ICmd.SequentialWriteDMAExt(maxLBA - xferlength +1, maxLBA, stepLBA, sctCnt)
      objMsg.printMsg('Last %s - Result %s' % (Ste_Name, str(result)))
      if result['LLRET'] != 0:
         ScrCmds.raiseException(12657, "%s Zero Write Failed" % Ste_Name)
      ICmd.FlushCache()
      if testSwitch.SMRPRODUCT:
         ICmd.FlushMediaCache()

      if testSwitch.IOWriteReadRemoval :
         RWDict = []
         RWDict.append ('Read')
         RWDict.append (maxLBA - xferlength +1)
         RWDict.append (maxLBA)
         RWDict.append (Ste_Name)
         objMsg.printMsg('WR_VERIFY appended - %s' % (RWDict))
         TP.RWDictGlobal.append (RWDict)

      self.dut.driveattr['ZERO_PTRN_RQMT'] = ZERO_PTRN_RQMT

###########################################################################################################
class C2MZeros(C20MZeros):
   """
      Write first and last 2 Million blocks with zero pattern
   """
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      C20MZeros.run(self, xferlength = 2097152, Ste_Name = 'C2MZeros', ZERO_PTRN_RQMT = "13")  # cannot use super() as CState is not type, but classobj

###########################################################################################################
class C20MZeroCheck(CState):
   """
      Zero Verify first and last 20 Million blocks.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut
   #-------------------------------------------------------------------------------------------------------
   def run(self, xferlength = 20971520, Ste_Name = 'C20MZeroCheck'):
      sctCnt = 0x800

      ICmd.HardReset()
      result = ICmd.ZeroCheck(0, xferlength - 1, sctCnt)
      objMsg.printMsg('First %s LBA Zero check result: %s' % (Ste_Name, result))
      if result['LLRET'] != OK:
         ScrCmds.raiseException(14723, "%s Zero Check - Failed to verify Zero Pattern on first LBAs" % Ste_Name)

      maxLBA = int(ICmd.GetMaxLBA()['MAX48'],16)-1
      result = ICmd.ZeroCheck(maxLBA - xferlength + 1, maxLBA, sctCnt)
      objMsg.printMsg('Last %s LBA Zero check result: %s' % (Ste_Name, result))
      if result['LLRET'] != OK:
         ScrCmds.raiseException(14723, "%s Zero Check - Failed to verify Zero Pattern on last LBAs" % Ste_Name)

###########################################################################################################
class C2MZeroCheck(C20MZeroCheck):
   """
      Zero Verify first and last 2 Million blocks.
   """
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      try:
         objMsg.printMsg("start C2MZeroCheck")
         C20MZeroCheck.run(self, xferlength = 2097152, Ste_Name = 'C2MZeroCheck')   # normal C20MZeroCheck
         objMsg.printMsg("end C2MZeroCheck")
      except:
         objMsg.printMsg("C20MZeroCheck exception: %s" % (traceback.format_exc(),))
         if testSwitch.SP_RETRY_WORKAROUND and testSwitch.NoIO:

            try:
               self.dut.driveattr['PROC_CTRL12'] = str(int(self.dut.driveattr['PROC_CTRL12']) + 1)
            except:
               self.dut.driveattr['PROC_CTRL12'] = 1

            objMsg.printMsg("PROC_CTRL12=%s" % self.dut.driveattr['PROC_CTRL12'])

            rlist = -1
            try:
               oSerial = serialScreen.sptDiagCmds()
               oSerial.quickDiag()
               reassignData = oSerial.dumpReassignedSectorList()
               objMsg.printMsg("reassignData data: %s" % (reassignData))
               rlist = reassignData['NUMBER_OF_TOTALALTS']
            except:
               objMsg.printMsg("reassignData exception: %s" % (traceback.format_exc(),))

            #if rlist > 0:
            #   raise

            objMsg.printMsg("Retrying C2MZeros")
            oZeros = C2MZeros(self.dut, self.params)
            oZeros.run()
            objMsg.printMsg("Retrying C20MZeroCheck")
            C20MZeroCheck.run(self, xferlength = 2097152, Ste_Name = 'C2MZeroCheck')

         else:
            raise


###########################################################################################################
class CCheck_DefList(CState):
   """
      Check Defect list
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut
   #-------------------------------------------------------------------------------------------------------
   def run(self, Check = True):
      self.oSerial = serialScreen.sptDiagCmds()
      self.oSerial.quickDiag()

      reassignData = self.oSerial.dumpReassignedSectorList()
      rListSectors, rListWedges = self.oSerial.dumpRList()
      self.dut.dblData.Tables('P000_DEFECTIVE_PBAS').addRecord({
                           'SPC_ID'          : 2,
                           'OCCURRENCE'      : self.dut.objSeq.getOccurrence(),
                           'SEQ'             : self.dut.objSeq.curSeq,
                           'TEST_SEQ_EVENT'  : self.dut.objSeq.getTestSeqEvent(0),
                           'NUMBER_OF_PBAS'  : reassignData['NUMBER_OF_TOTALALTS'],
                           'RLIST_SECTORS'   : rListSectors,
                           'RLIST_WEDGES'    : rListWedges,
                           })

      objMsg.printDblogBin(self.dut.dblData.Tables('P000_DEFECTIVE_PBAS'))

      if Check == True and hasattr(TP,'CHK_DEFECTIVE_PBAS'):
         if self.appleDetect():
            objMsg.printMsg("Checking TP.CHK_DEFECTIVE_PBAS=%s" % TP.CHK_DEFECTIVE_PBAS)
            tabledata = self.dut.dblData.Tables('P000_DEFECTIVE_PBAS').tableDataObj()
            for key in TP.CHK_DEFECTIVE_PBAS:
               for tab in tabledata:
                  if tab.has_key(key) and (int(tab[key]) > int(TP.CHK_DEFECTIVE_PBAS[key])):
                     ScrCmds.raiseException(13456, 'Fail SMART Glist/Rlist/Alt list')


      if self.dut.SkipPCycle:
         objMsg.printMsg("CCheck_DefList SkipPCycle")
      else:
         objPwrCtrl.powerCycle()

      if self.params.get('FAIL_NEW_DEFECTS', False):
         if reassignData['NUMBER_OF_TOTALALTS'] > 0 or \
            rListSectors > 0 or \
            rListWedges > 0:
            ScrCmds.raiseException(10506,  "Drive failed for grown defects!")
      else:
         objMsg.printMsg("FAIL_NEW_DEFECTS param is not defined. Skip checking R-list")

   #-------------------------------------------------------------------------------------------------------
   def appleDetect(self):
      """
         Check PIF entries and Signature of Apple Code in Firmware Package Version; returns True if Apple
      """

      import PIF
      ApplePartNum = getattr(PIF, 'ApplePartNum', [])
      AppleFWSignature = getattr(PIF, 'AppleFWSignature', '')

      objMsg.printMsg('appleDetect ApplePartNum=%s, AppleFWSignature=%s PN=%s' % (ApplePartNum, AppleFWSignature, self.dut.driveattr['PART_NUM']))
      if len(ApplePartNum) == 0 and len(AppleFWSignature) == 0:
         return True    # backward compatibility when PIF.py has no entries

      if self.dut.driveattr['PART_NUM'][-3:] in ApplePartNum:
         return True

      if len(AppleFWSignature) > 0:
         packVer = self.oSerial.GetCtrl_L()['PackageVersion']
         pat = packVer[23:]
         objMsg.printMsg('Package Version=%s, Pattern=%s' % (packVer, pat))
         if pat.find(AppleFWSignature) >= 0:
            return True

      return False

###########################################################################################################
class CDisplay_G_list(CState):
   """
      Display G list
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      params.setdefault('startup',1)
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut
   #-------------------------------------------------------------------------------------------------------
   def run(self, DispGlistInCCV= 0):
      self.oSerial = serialScreen.sptDiagCmds()
      if testSwitch.FE_0121885_399481_ALLOW_SPC_ID_TO_BE_SET_BY_CALLER_IN_DISPLAY_G_LIST:
         spc_id = self.params.get('spc_id', 2)
      else:
         spc_id = 2

      if (self.dut.drvIntf in TP.WWN_INF_TYPE.get('WW_SAS_ID', []) or self.dut.drvIntf == 'SAS') and not testSwitch.FE_0171507_231166_P_SERIAL_CMDS_SAS_FORMAT_IN_IO:
         reassignData = ICmd.DisplayBadBlocks()
         rListSectors = 0
         rListWedges = 0
      else:
         if self.params['startup']:
            objPwrCtrl.powerCycle()
            sptCmds.enableDiags()
         reassignData = self.oSerial.dumpReassignedSectorList()
         rListSectors, rListWedges = self.oSerial.dumpRList()
         if testSwitch.FE_0144392_007955_P_V40_DUMP_IN_DISPLAY_G_LIST:
            self.oSerial.dumpNonResidentGList()  # Displays non-resident Glist

         if testSwitch.FE_0122102_399481_GET_CRITICAL_EVENTS_AFTER_G_LIST:
            self.oSerial.getCriticalEventLog() # assumes we're in level 1

      self.dut.dblData.Tables('P000_DEFECTIVE_PBAS').addRecord(
         {
         'SPC_ID'          : spc_id,
         'OCCURRENCE'      : self.dut.objSeq.getOccurrence(),
         'SEQ'             : self.dut.objSeq.curSeq,
         'TEST_SEQ_EVENT'  : self.dut.objSeq.getTestSeqEvent(0),
         'NUMBER_OF_PBAS'  : reassignData['NUMBER_OF_TOTALALTS'],
         'RLIST_SECTORS'   : rListSectors,
         'RLIST_WEDGES'    : rListWedges,
         })

      objMsg.printDblogBin(self.dut.dblData.Tables('P000_DEFECTIVE_PBAS'))

      if self.params['startup']:
         objPwrCtrl.powerCycle()

      if testSwitch.FE_0146575_231166_P_CHCK_PARAMS_0_ALTS and not DispGlistInCCV:

         if self.params.get('FAIL_NEW_DEFECTS', True):
            if reassignData['NUMBER_OF_TOTALALTS'] > 0 or \
               rListSectors > 0 or \
               rListWedges > 0:
               ScrCmds.raiseException(10506,  "Drive failed for grown defects!")


      if DispGlistInCCV:
         return reassignData['NUMBER_OF_TOTALALTS'],rListSectors,rListWedges
###########################################################################################################
class CCheckMergeGList(CState):
   """
      Check to to see if G-List, R-List, Alt List entries.  If they exceed the limits do a G->P Merge.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      oProcess = CProcess()

      from serialScreen import sptDiagCmds

      self.oSerial = serialScreen.sptDiagCmds()
      self.DEBUG = 0

      if testSwitch.BF_0122949_231166_CHK_MRG_G_PWR_LOSS_SAFE:
         pwrLossIntratransitionOK = self.dut.objData.get('CHK_MRG_G_PWR_LOSS_OK', True)
      else:
         pwrLossIntratransitionOK = True

      if testSwitch.FE_0130184_399481_OPTION_TO_RUN_LONG_DST_AFTER_G_LIST_MERGE:
         runLongDSTonMerge = self.params.get('runLongDSTonMerge', False)

      # Initial Power Trip
      if testSwitch.BF_0156546_395340_P_FIX_CONDITION_PWL_AT_MERGE_G_TO_P:
         if self.dut.powerLossEvent and testSwitch.FE_0151315_395340_P_POWER_TRIP_AT_CHK_MRG_G_ON_CUT2:
            objMsg.printMsg("Re-Initializing slips")
            sptCmds.enableDiags()
            sptCmds.gotoLevel('T')
            sptCmds.sendDiagCmd('m0,6,,,,,,22',timeout = 600, printResult = True)
            self.oSerial.CheckNumEntriesInGList() # Re-display lists
            self.dut.powerLossEvent = 0
      else:
         if self.dut.stateTransitionEvent == 'powerLossEvent' and testSwitch.FE_0151315_395340_P_POWER_TRIP_AT_CHK_MRG_G_ON_CUT2:
            objMsg.printMsg("Re-Initializing slips")
            sptCmds.enableDiags()
            sptCmds.gotoLevel('T')
            sptCmds.sendDiagCmd('m0,6,,,,,,22',timeout = 600, printResult = True)
            oSerial.CheckNumEntriesInGList() # Re-display lists

      if testSwitch.WA_0173899_475827_P_SKIP_ATA_READY_CHECK_AFTER_G_P_MERGE_FORMAT:
         objPwrCtrl.powerCycle(ataReadyCheck = False)
      else:
         objPwrCtrl.powerCycle()

      mergeG2P = self.processDefectLists(processPendingEntries = True)

      if not (mergeG2P or testSwitch.virtualRun or self.dut.powerLossEvent):
         objMsg.printMsg("No entries found.  Skipping merge G to P")
      else:
         # download TGTP in order to perform G-> P Merge
         if testSwitch.FE_0157728_426568_P_CONDITIONAL_CODE_DNLD_G_P_MERGE:
            objMsg.printMsg("Items Found in the G List... Downloading TGTP code")
            codeToDnld= getattr(TP, 'GP_DNLD_SEQ', {'CODES': ['TGT','OVL',],})
            oDnldCode = CDnlduCode(self.dut,codeToDnld)
            oDnldCode.run()
         if pwrLossIntratransitionOK:
            objMsg.printMsg("ATTEMPING G->P MERGE")
            ScrCmds.insertHeader("Defects found during First/Last Write/Read operation - attempting GList Merge and Write Pass")
            if testSwitch.FE_0171507_231166_P_SERIAL_CMDS_SAS_FORMAT_IN_IO or not ( (self.dut.drvIntf in TP.WWN_INF_TYPE.get('WW_SAS_ID', [] ) or self.dut.drvIntf == 'SAS' ) ):
               sptCmds.enableDiags()
               self.oSerial.mergeG_to_P()
               objMsg.printMsg("Re-Initializing slips")
               sptCmds.gotoLevel('T')
               # Format Partition Command: User Partition,(Disable User Partition Certify & Disable User Partition Format),,,,,,Valid Command Key
               formatTimeout = int(2.6*60*60*(self.dut.imaxHead+1))

               if testSwitch.FE_0139421_399481_P_BIE_SETTINGS_IN_CHK_MRG_G_FMT:
                  formatOptions = TP.formatOptionsChkMrgG

                  if formatOptions["BIE_THRESH"]:
                     self.oSerial.setupBIEThresh(
                        formatOptions["BIE_THRESH"],
                        formatOptions["ITER_LOAD"],
                        printResult = True
                        )

                     sptCmds.gotoLevel('2')
                     sptCmds.sendDiagCmd('Y%s' % formatOptions["RETRIES"], printResult = True)
                     sptCmds.sendDiagCmd('D%X' % formatOptions["ITER_CNT"], printResult = True)

                  sptCmds.gotoLevel('T')
                  mCmd = self.oSerial.createFormatCmd(formatOptions)
                  sptCmds.sendDiagCmd(mCmd,timeout = formatTimeout, printResult = True, loopSleepTime = 5)

                  if formatOptions["BIE_THRESH"]:
                     self.oSerial.disableBIEDetector(printResult = True)

               else:
                  if testSwitch.FE_0148837_357260_ENABLE_VERIFY_IN_G_P_MERGE_FORMAT:
                     sptCmds.sendDiagCmd('m0,49,,40,,,,22',timeout = formatTimeout, printResult = True, loopSleepTime = 5)
                  else:
                     sptCmds.sendDiagCmd('m0,4,,40,,,,22',timeout = formatTimeout, printResult = True, loopSleepTime = 5)

            else:
               ICmd.MergeDefectLists(formatDrive = True)
            if testSwitch.BF_0122949_231166_CHK_MRG_G_PWR_LOSS_SAFE:
               self.dut.objData['CHK_MRG_G_PWR_LOSS_OK'] = False

         #####################################################################################
         #display the lists before we do the full pack write to make sure they are cleared
         if not ( ( self.dut.drvIntf in TP.WWN_INF_TYPE.get('WW_SAS_ID', [] ) or self.dut.drvIntf == 'SAS') ):
            if self.DEBUG:
               defectLimitExceeded = self.processDefectLists()


         if not ( ( self.dut.drvIntf in TP.WWN_INF_TYPE.get('WW_SAS_ID', [] ) or self.dut.drvIntf == 'SAS' ) ):
            #re-establish communication.
            theCell.enableESlip(sendESLIPCmd = True)
            theCell.disableESlip()

         if testSwitch.BF_0122949_231166_CHK_MRG_G_PWR_LOSS_SAFE:
            self.dut.objData['CHK_MRG_G_PWR_LOSS_OK'] = True

         #check the lists again to ensure the merge went smoothly
         # power cycle required to update smart attributes or
         # g list entries will still be present and we'll fail
         if testSwitch.WA_0173899_475827_P_SKIP_ATA_READY_CHECK_AFTER_G_P_MERGE_FORMAT:
            objPwrCtrl.powerCycle(ataReadyCheck = False)
         else:
            objPwrCtrl.powerCycle()

         defectLimitExceeded = self.processDefectLists()
         if defectLimitExceeded:
            ScrCmds.raiseException(10049, 'There are still entries in the Glist/Rlist/Alt list')

         if testSwitch.FE_0130184_399481_OPTION_TO_RUN_LONG_DST_AFTER_G_LIST_MERGE and runLongDSTonMerge:
            oSmartDSTLong = CSmartDSTLong(self.dut)
            oSmartDSTLong.run()

         objPwrCtrl.powerCycle()

         if testSwitch.FE_0157728_426568_P_CONDITIONAL_CODE_DNLD_G_P_MERGE:
            # download customer code after G-> P Merge
            objMsg.printMsg("G -> P Merge Complete... Downloading Customer code")
            import PIF
            if hasattr(PIF,'TCG_PN_REG'):
               pnMatch = PIF.TCG_PN_REG
               try:
                  regVal = re.compile(pnMatch)
               except re.error:
                  #Ignore invalid re's... incase
                  objMsg.printMsg("Invalid re in PIF PN: '%s'" % pnMatch)
                  if testSwitch.FAIL_INVALID_PIF_REGEX:
                     ScrCmds.raiseException(11044,"Script Error in resolving regex for %s" % pnMatch)
               mMatch = regVal.search(self.dut.partNum)
               if mMatch:
                  codeToDnld = getattr(TP, 'GP_TCG_DNLD_SEQ', {'CODES': ['UNLK','TGT','OVL','UNLK','TGT4','OVL4','UNLK','TGT2','SFW2'], 'CMP_CODE': 0})
                  objMsg.printMsg("Using TCG download String: %s" % codeToDnld)
               else:
                  codeToDnld = getattr(TP, 'GP_NON_TCG_DNLD_SEQ', {'CODES': ['UNLK','TGT2','OVL2','SFW2'], 'CMP_CODE': 1 })
                  objMsg.printMsg("Using standard download String: %s" % codeToDnld)
            else:
               codeToDnld = getattr(TP, 'GP_NON_TCG_DNLD_SEQ', {'CODES': ['UNLK','TGT2','OVL2','SFW2'], 'CMP_CODE': 1 })
               objMsg.printMsg("Using standard download String: %s" % codeToDnld)
            oDnldCode = CDnlduCode(self.dut,codeToDnld)
            oDnldCode.run()

      objPwrCtrl.powerCycle()


   def processDefectLists(self, processPendingEntries = False):
      '''Return True if defects exceed the limit set.  Check ALT List but as verification
      also check rList and SMART log/attributes that the customer sees'''
      defectLimitExceeded = 0

      prm_SmartDefectList = getattr(TP,'prm_SmartDefectList',{})
      DefectListLimits = prm_SmartDefectList.get('ALT_LIST',0)

      if testSwitch.FE_0171507_231166_P_SERIAL_CMDS_SAS_FORMAT_IN_IO or not ( ( self.dut.drvIntf in TP.WWN_INF_TYPE.get('WW_SAS_ID', [] ) or self.dut.drvIntf == 'SAS' ) ):
         self.oSerial.enableDiags()

      if processPendingEntries:
         reassignData = self.processPendingEntries()
      else:
         if ( self.dut.drvIntf in TP.WWN_INF_TYPE.get('WW_SAS_ID', [] ) or self.dut.drvIntf == 'SAS' ) and not testSwitch.FE_0171507_231166_P_SERIAL_CMDS_SAS_FORMAT_IN_IO:
            reassignData = ICmd.DisplayBadBlocks()
         else:
            reassignData = self.oSerial.dumpReassignedSectorList()

      if self.DEBUG:
         if testSwitch.FE_0171507_231166_P_SERIAL_CMDS_SAS_FORMAT_IN_IO or not ( ( self.dut.drvIntf in TP.WWN_INF_TYPE.get('WW_SAS_ID', [] ) or self.dut.drvIntf == 'SAS' ) ):
            Glist = self.oSerial.dumpNonResidentGList()
            ResGlist = self.oSerial.dumpResidentGList()
            objMsg.printMsg('Display Smart Attributes via Diag')
            self.oSerial.gotoLevel('1')
            sptCmds.sendDiagCmd('N5', printResult = True)

      #All entries should show up in the ALT list but just in case check what the customer sees as well.
      objMsg.printMsg("Returned %s" % (reassignData,))
      if reassignData['NUMBER_OF_TOTALALTS'] > DefectListLimits:
         if testSwitch.FE_0130184_399481_OPTION_TO_RUN_LONG_DST_AFTER_G_LIST_MERGE:
            self.oSerial.dumpSmartLog()
         objMsg.printMsg("%d Alt LIST ENTRIES GREATER THAN LIMIT %d, ATTEMPING G->P MERGE" % (reassignData['NUMBER_OF_TOTALALTS'], DefectListLimits))
         defectLimitExceeded = 1

      if testSwitch.FE_0171507_231166_P_SERIAL_CMDS_SAS_FORMAT_IN_IO or not ( ( self.dut.drvIntf in TP.WWN_INF_TYPE.get('WW_SAS_ID', [])  or self.dut.drvIntf == 'SAS' ) ):
         #check the rlist
         rList = self.oSerial.dumpRList()
         if rList[0] > DefectListLimits:
            objMsg.printMsg("%d R LIST ENTRIES GREATER THAN LIMIT %d " % (rList[0], DefectListLimits))
            defectLimitExceeded = 1

      #check the smart logs/ attributes that the customer has access to
      if not ( (self.dut.drvIntf in TP.WWN_INF_TYPE.get('WW_SAS_ID', []) or self.dut.drvIntf == 'SAS') ):
         objPwrCtrl.powerCycle(ataReadyCheck = False)
         smartList = CSmartDefectList(self.dut,{'failForLimits': 0})
         smartLogDefects = {
            "PENDING"   : smartList.PList(failForLimits = 0),
            "GLIST"     : smartList.GList(failForLimits = 0),
         }

         import SmartFuncs
         smrtObj = SmartFuncs.CSmartAttrAccess()
         smrtObj.loadSmartLog(force = True)
         smartAttrDefects = {
            "GLIST"                 : smrtObj.ReadRetiredSectorCount(),
            "PENDING"               : smrtObj.ReadPendingSpareCount(),
            "UNCORRECT_SCTR_CNT"    : smrtObj.UncorrectableSectorsCount(),
            "SPARES_BEFORE_RESET"   : smrtObj.ReadSpareCountWhenLastResetSmart(),
            "PENDING_BEFORE_RESET"  : smrtObj.ReadPendingSpareCountWhenLastResetSmart(),
            }
         objMsg.printDict(smartAttrDefects)
         if sum(smartLogDefects.values()) > DefectListLimits:
            objMsg.printMsg("SmartLog A8/A9 ENTRIES GREATER THAN LIMIT %d" % (DefectListLimits))
            defectLimitExceeded = 1
         elif sum(smartAttrDefects.values()) > DefectListLimits:
            objMsg.printMsg("SmartAttributes 5, C5, C6, 410, 412 ENTRIES GREATER THAN LIMIT %d" % (DefectListLimits))
            defectLimitExceeded = 1

      return defectLimitExceeded

   def processPendingEntries(self):
      '''Write at the location of a pending defect entry to tranisition it to a alt entry'''
      if ( self.dut.drvIntf in TP.WWN_INF_TYPE.get('WW_SAS_ID', []) or self.dut.drvIntf == 'SAS' ) and not testSwitch.FE_0171507_231166_P_SERIAL_CMDS_SAS_FORMAT_IN_IO:
         reassignData = ICmd.DisplayBadBlocks()
         objMsg.printMsg("Returned %s" % (reassignData,))

         if testSwitch.WA_0141744_357552_BYPASS_T515_CERTIFY:
            objMsg.printMsg("WA_0141744_357552_BYPASS_T515_CERTIFY set - Skipping T515 Certify")
         else:
            if testSwitch.BF_0127472_231166_DONT_CERT_BBT_NO_BBTS:
               if reassignData['NUMBER_OF_PENDING_ENTRIES'] or reassignData['NUMBER_OF_TOTALALTS']:
                  ICmd.CertBadBlocks()
            else:
               ICmd.CertBadBlocks()
      else:
         if testSwitch.FE_0174882_231166_P_PROCESS_PENDING_TO_ALT:
            reassignData = self.oSerial.addPendingListToAltList()
         else:
            reassignData, altListLBAs = self.oSerial.dumpReassignedSectorList(returnAltListLBAS = 1)

            if reassignData['NUMBER_OF_PENDING_ENTRIES']:
               objMsg.printMsg("%d Pending Entries found in the ALT list.  Need to perform writes at these locations" %reassignData['NUMBER_OF_PENDING_ENTRIES'])
               objMsg.printMsg('LBAs to write to: %s' % altListLBAs)

               for lba in altListLBAs:
                  try:
                     self.oSerial.rw_LBAs(lba,lba,mode = 'W')
                  except:
                     objMsg.printMsg('Unable to write to LBAs %s' % lba)

               reassignData = self.oSerial.dumpReassignedSectorList()
               if reassignData['NUMBER_OF_PENDING_ENTRIES']:
                  objMsg.printMsg('Warning Pending Entries still exist in the ALT list')

      return reassignData


###########################################################################################################
###########################################################################################################
class CVoltageHLTest(CState):
   def __init__(self, dut, params=[]):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.margin5V = TP.prm_IntfTest["5V_margin"]
      self.margin12V = TP.prm_IntfTest["12V_margin"]
      try:
         self.loop_count = self.params.get('VHL_Loop_Count', TP.prm_IntfTest["VoltHL_LoopCount"])
      except:
         self.loop_count = 1
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from VoltageHighLow import CVoltageHighLow
      oVoltageHighLow = CVoltageHighLow()
      count = self.loop_count
      while count > 0:
         oVoltageHighLow.voltageHighLowTest(self.margin5V, self.margin12V)
         count -= 1
###########################################################################################################
class CPowerCycleLoops(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params=[]):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      self.loop_count = self.params.get('LOOP_COUNT',1)
      ScrCmds.insertHeader("Executing %s Power Cycles" %self.loop_count)
      for i in range(self.loop_count):
         objPwrCtrl.powerCycle(ataReadyCheck = False)

###########################################################################################################
class CCommandSet(CState):
   def __init__(self, dut, params=[]):
      self.dut = dut
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from CommandSet import CCommandSetTest
      oCommandSet = CCommandSetTest(self.dut)
      oCommandSet.commandSetTest()

###########################################################################################################
class CAccessTime(CState):
   def __init__(self, dut, params=[]):
      self.dut = dut
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from AccessTime import CAccessTimeTest
      oAccessTime = CAccessTimeTest(self.dut)
      if testSwitch.auditTest ==0:
         oAccessTime.accessTimeTest()
      elif testSwitch.auditTest ==1:
         objMsg.printMsg("                       AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA                         ",objMsg.CMessLvl.IMPORTANT)
         objMsg.printMsg("AUDIT TEST: bypass access time test until issues are resolved",objMsg.CMessLvl.IMPORTANT)# access time test SP icmd is not returning 'SnSkMinTm' key, which leads to exception.
      #oAccessTime.accessTimeTest(TP.prm_AccessTime)

###########################################################################################################
class CPowerMode(CState):
   def __init__(self, dut, params=[]):
      self.dut = dut
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from PowerMode import CPowerModeTest
      oPowerMode = CPowerModeTest(self.dut)
      oPowerMode.powerModeTest()

###########################################################################################################
class CDRamScreen(CState):
   def __init__(self, dut, params=[]):
      self.dut = dut
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from DRamScreen import CDRamScreenTest
      oDRamScreen = CDRamScreenTest(self.dut)
      oDRamScreen.dRamScreenTest()

################################# SMART Section ###########################################################
###########################################################################################################
class CVerifySMART(CState):
   """
      Description: Class that will perform Verify SMART.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):

      if testSwitch.WA_0124639_231166_DRIVE_SMART_NOT_SUPPORTED:
         objMsg.printMsg("SMART access disabled for this F3 based on PF3 flag WA_0124639_231166_DRIVE_SMART_NOT_SUPPORTED")
         return

      smartEnableOperData = ICmd.SmartEnableOper()
      objMsg.printMsg("SmartEnableOper data: %s" % smartEnableOperData, objMsg.CMessLvl.IMPORTANT)
      if smartEnableOperData['LLRET'] != 0:
         ScrCmds.raiseException(13455, 'Failed Smart Enable Oper')

      if not ( self.dut.drvIntf in TP.WWN_INF_TYPE.get('WW_SAS_ID', []) or self.dut.drvIntf == 'SAS' ):
         CriticalLogData = ICmd.SmartReadLogSec(0xA1,1)

      smartReturnStatusData = ICmd.SmartReturnStatus()
      objMsg.printMsg("SmartReturnStatus data: %s" % smartReturnStatusData, objMsg.CMessLvl.IMPORTANT)
      objMsg.printMsg("SmartReturnStatus value: %x" % int(smartReturnStatusData['LBA']), objMsg.CMessLvl.IMPORTANT)
      if int(smartReturnStatusData['LBA']) != 0xc24f00:
         ScrCmds.raiseException(13455, 'Failed Smart Threshold Value')

###########################################################################################################
class CClearSMART(CState):
   """
      Description: Class that will perform SMART reset and generic customer prep.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params = {}):
      params.setdefault('startup',1)
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if testSwitch.WA_0124639_231166_DRIVE_SMART_NOT_SUPPORTED:
         objMsg.printMsg("SMART access disabled for this F3 based on PF3 flag WA_0124639_231166_DRIVE_SMART_NOT_SUPPORTED")
         return

      if ( self.dut.drvIntf in TP.WWN_INF_TYPE.get('WW_SAS_ID', []) or self.dut.drvIntf == 'SAS' ) :
         ICmd.ClearSmart()
      else:

         oSerial = serialScreen.sptDiagCmds()
         if self.params['startup']:
            sptCmds.enableDiags()

         #Display Debug information - ScPk request
         try:
            if testSwitch.EnableDebugLogging:
               if testSwitch.BIGS_FIRMWARE_NEED_SPECIAL_CMD_IN_F3:
                  oSerial.initBIGSFirmware()
               oSerial.gotoLevel('1')
               oSerial.getCriticalEventAttributes(30,failOnThresholdViolation=False)
               ####### Added as per request from CheeWai Lum - 15-Nov-2011  #######
               oSerial.gotoLevel('T')
               reassignData = oSerial.dumpReassignedSectorList()
               if reassignData['NUMBER_OF_TOTALALTS'] > 0:
                  ScrCmds.raiseException(10506,  "Drive failed for RST List!")
               oSerial.gotoLevel('1')
               oSerial.getCriticalEventLog()
               ####################################################################
         except:
            if not testSwitch.FE_0174192_395340_P_USE_C5_C6_TO_CHECK_P_LIST_ON_CUT2:
               pass
            else:
               objMsg.printMsg("Except Occure when screening C5 and C6")
               smartResetParms = TP.smartResetParams.copy()
               if testSwitch.FE_0133890_231166_VALIDATE_SHIPMENT_DEPENDANCIES:
                  # Make sure 1 and 0x23 are updated to clear the smart data and the persistent info
                  minimum_SMART_INIT_OPS = [1, 0x23]
                  smartResetParms['options'] = set(smartResetParms['options'])
                  smartResetParms['options'].update(minimum_SMART_INIT_OPS)
                  smartResetParms['options'] = list(smartResetParms['options'])
               oSerial.SmartCmd(smartResetParms)
               objPwrCtrl.powerCycle(5000,12000,10,30,ataReadyCheck=False)

               if self.params.get('INITWZEROS', 0):
                  from IntfClass import CInterface
                  oIntf = CInterface()
                  smartLogs = getattr(TP,'smartLogsWithZeros',[0x9A,0x80]) #dell ppid, avscan
                  for log in smartLogs:
                     oIntf.writeZerosToSmartLog(log)
               #Report N5 Command again for Debugging by Supitcha S.
               objMsg.printMsg("*** Stop Drive test to raise Exception ***")
               raise

         smartResetParms = TP.smartResetParams.copy()
         if testSwitch.FE_0133890_231166_VALIDATE_SHIPMENT_DEPENDANCIES or testSwitch.FE_0174396_231166_P_MOVE_CLEANUP_TO_OWN_STATE:
            # Make sure 1 and 0x23 are updated to clear the smart data and the persistent info
            minimum_SMART_INIT_OPS = [1, 0x23]


            smartResetParms['options'] = set(smartResetParms['options'])
            smartResetParms['options'].update(minimum_SMART_INIT_OPS)
            smartResetParms['options'] = list(smartResetParms['options'])

         oSerial.SmartCmd(smartResetParms)

         if self.params['startup'] or not testSwitch.FE_0183110_231166_P_OPTIMIZE_CCV_PWR_CYCLES:
            objPwrCtrl.powerCycle(5000,12000,10,30,ataReadyCheck=False)
         if testSwitch.FE_0164115_340210_SMART_FH_WRT:

            ICmd.UnlockFactoryCmds()
            ICmd.WrtAltTones()


         if self.params.get('INITWZEROS', 0):
            from IntfClass import CInterface
            oIntf = CInterface()

            smartLogs = getattr(TP,'smartLogsWithZeros',[0x9A,0x80]) #dell ppid, avscan
            for log in smartLogs:
               oIntf.writeZerosToSmartLog(log)

         if not self.params['startup']:
            sptCmds.enableDiags()

###########################################################################################################
class CClearSMARTCCV(CState):
   """
      Description: Class that will perform SMART reset and generic customer prep.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      params.setdefault('startup',1)
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):

      #objPwrCtrl.powerCycle(5000,12000,10,30)
      oSerial = serialScreen.sptDiagCmds()
      if self.params['startup']:
         objPwrCtrl.powerCycle()
         oSerial.enableDiags()

      oSerial.SmartCmd(TP.smartResetParams)
      if self.params['startup']:
         objPwrCtrl.powerCycle(5000,12000,10,30)

###########################################################################################################
class CClearDOS(CState):
   """
      Description: Class that will perform DOS clearing.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      params.setdefault('startup',1)
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):

      if not testSwitch.FE_0168661_231166_P_ALLOW_SAS_RESET_DOS and ( self.dut.drvIntf in TP.WWN_INF_TYPE.get('WW_SAS_ID', []) or self.dut.drvIntf == 'SAS' ) :
         objMsg.printMsg("DOS reset not supported for SAS")
      else:
         oSerial = serialScreen.sptDiagCmds()
         if self.params['startup']:
            sptCmds.enableDiags()

         oSerial.clearDOS(TP.clearDOSParams)
         if self.params['startup']:
            if self.dut.SkipPCycle:
               objMsg.printMsg("CClearDOS SkipPCycle")
            else:
               objPwrCtrl.powerCycle(5000,12000,10,30,ataReadyCheck=False)

###########################################################################################################
###########################################################################################################
class CCapScrn(CProcess):
   """
   Test Purpose: Validate drive capacity and model no.
   Basic Algorithm:
   - Use serial port L command get the drive model and capacity
   - Interface "Identify" command, compare the model and capacity
   Failure: Fail on incorrect drive capacity or model no.
   """
   #---------------------------------------------------------------------------------------------------------#
   def __init__(self, dut, params=[]):
      self.dut = dut
   #---------------------------------------------------------------------------------------------------------#
   def CapScrnTest(self, drvInfoDict):
      """
      Execute function loop.
      @return result: Returns OK or FAIL
      """
      result, spDrvCap, spDrvModel, spPFM_ID, spHeads, spDrvSn = self.serialGetDrvData()
      objMsg.printMsg('Serial Port -    Model: %s   S/N: %s   Capacity: %dGB   ' % (spDrvModel,spDrvSn,spDrvCap))
      objMsg.printMsg('Serial Port -    PFM_ID: %s   Heads:%s   ' % (spPFM_ID,spHeads)) 
      objPwrCtrl.powerCycle() # Loke
      return result
   #---------------------------------------------------------------------------------------------------------#
   def serialGetDrvData(self):
      self.oSerial = serialScreen.sptDiagCmds()
      sptCmds.enableDiags()
      sptCmds.sendDiagCmd(CTRL_Z,altPattern='>',printResult=True,raiseException=0, Ptype='PChar')

      data = sptCmds.sendDiagCmd( CTRL_L, altPattern = 'PreampType:',printResult=True, Ptype='PChar')
   
      self.oSerial.flush()
      sptCmds.sendDiagCmd(CTRL_Z,altPattern='>',printResult=True,raiseException=0, Ptype='PChar')
   
      data2 = sptCmds.sendDiagCmd( 'F"InternalSeagateModelNumber"', altPattern='T>' )
   
      d = data
      m = re.search('Lbas:', d)
      if m == None:  # knl 26Dec07
          objMsg.printMsg('CapScrn fail. Cannot read "Lbas:"')
          return 1,-1,-1,-1,-1,''

      cap = d[m.end():].split(',')[0]
      cap = int(cap,16)

      if 3907029168 <= cap*8:
         objMsg.printMsg('Capacity is 2000G......')
         sptCmds.sendDiagCmd(CTRL_Z,altPattern='>',printResult=True)
         sptCmds.gotoLevel('T')
         sptCmds.sendDiagCmd('J1,8\r' , printResult = True)
         sptCmds.sendDiagCmd('JE8E088B0,17\r' , printResult = True)
         sptCmds.sendDiagCmd('J"00000000",1\r' , printResult = True)
         sptCmds.sendDiagCmd('W0,,22\r' , printResult = True)
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      if 2930277168 <= cap*8 < 3907029168:
         objMsg.printMsg('Capacity is 1500G......')
         sptCmds.sendDiagCmd(CTRL_Z,altPattern='>',printResult=True)
         sptCmds.gotoLevel('T')
         sptCmds.sendDiagCmd('J2,8\r' , printResult = True)
         sptCmds.sendDiagCmd('JAEA87B30,17\r' , printResult = True)
         sptCmds.sendDiagCmd('J"00000000",1\r' , printResult = True)
         sptCmds.sendDiagCmd('W0,,22\r' , printResult = True)
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      if 1813525168 <= cap*8 < 2930277168:
         objMsg.printMsg('Capacity is 1000G......')
         sptCmds.sendDiagCmd(CTRL_Z,altPattern='>',printResult=True)
         sptCmds.gotoLevel('T')
         sptCmds.sendDiagCmd('J3,8\r' , printResult = True)
         sptCmds.sendDiagCmd('J74706DB0,17\r' , printResult = True)
         sptCmds.sendDiagCmd('J"00000000",1\r' , printResult = True)
         sptCmds.sendDiagCmd('W0,,22\r' , printResult = True)
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      if 1465149168 <= cap*8 < 1953525168:
         objMsg.printMsg('Capacity is 750G......')
         sptCmds.sendDiagCmd(CTRL_Z,altPattern='>',printResult=True)
         sptCmds.gotoLevel('T')
         sptCmds.sendDiagCmd('J4,8\r' , printResult = True)
         sptCmds.sendDiagCmd('J575466F0,17\r' , printResult = True)
         sptCmds.sendDiagCmd('J"00000000",1\r' , printResult = True)
         sptCmds.sendDiagCmd('W0,,22\r' , printResult = True)
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      if 976773168 <= cap*8 < 1465149168:
         objMsg.printMsg('Capacity is 500G......')
         sptCmds.sendDiagCmd(CTRL_Z,altPattern='>',printResult=True)
         sptCmds.gotoLevel('T')
         sptCmds.sendDiagCmd('JF,8\r' , printResult = True)
         sptCmds.sendDiagCmd('J25426030,17\r' , printResult = True)
         sptCmds.sendDiagCmd('J"00000000",1\r' , printResult = True)
         sptCmds.sendDiagCmd('W0,,22\r' , printResult = True)
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      if cap*8 < 976773168:
         objMsg.printMsg('Capacity is 320G......')
         sptCmds.sendDiagCmd(CTRL_Z,altPattern='>',printResult=True)
         sptCmds.gotoLevel('T')
         sptCmds.sendDiagCmd('JF,8\r' , printResult = True)
         sptCmds.sendDiagCmd('J374FEAB0,17\r' , printResult = True)
         sptCmds.sendDiagCmd('J"00000000",1\r' , printResult = True)
         sptCmds.sendDiagCmd('W0,,22\r' , printResult = True)
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      # Get hda s/n
      d = data
      m = re.search('HDA SN:', d)
      if m == None:  # knl 26Dec07
          objMsg.printMsg('CapScrn fail. Cannot read "HDA SN:"')
          return 1,-1,-1,-1,-1,''

      hdasn = d[m.end():].split(',')[0]
      hdasn = hdasn.split()[0]

      # Get PFM_ID
      d = data
      m = re.search('MemberId:', d)
      if m == None:  
          objMsg.printMsg('CapScrn fail. Cannot read "MemberId:"')
          return 1,-1,-1,-1,-1,''

      pfm_id = d[m.end():].split(',')[0]
      pfm_id = pfm_id.split()[0]
      pfm_id = int(pfm_id,16)

      # Get Heads
      d = data
      m = re.search('Heads:', d)
      if m == None:  
          objMsg.printMsg('CapScrn fail. Cannot read "Heads:"')
          return 1,-1,-1,-1,-1,''

      heads = d[m.end():].split(',')[0]
      heads = heads.split()[0]
      heads = int(heads,16)
      # Get Model number
      m = re.search('ModelNumber =', data2)
      if m == None:  # knl 26Dec07
          objMsg.printMsg('CapScrn fail. Cannot read "ModelNumber ="')
          return 1,-1,-1,-1,-1,''

      model = data2[m.end():].split("'")[1]
      model = model.strip()
   
      return OK, (cap*512*8/1000000000), model, pfm_id, heads, hdasn
###########################################################################################################

class CCapacityScreen(CState):
   def __init__(self, dut, params=[]):
      self.dut = dut
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      import serialScreen, sptCmds
      oCapScrn = CCapScrn(self.dut)
      oCapScrn.CapScrnTest(self.params)
###########################################################################################################
###########################################################################################################
class CSetDriveConfigAttributes(CState):
   def __init__(self, dut, params=[]):
      self.dut = dut
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):

      from CustomCfg import CCustomCfg
      CustConfig = CCustomCfg()

#CHOOI-25Apr17 OffSpec
      if self.dut.nextState in ['OOS_CHECK_ID','OOS_CHECK_ID_1','OOS_CHECK_ID_2']:
         self.checkdriveattribute()
         return

#          self.validateDCMAttr('TP_DRV_SN', failIfUnavailable=True)
#          self.validateDCMAttr('DRV_MODEL_NUM', failIfUnavailable=True)
#          self.validateDCMAttr('USER_LBA_COUNT', failIfUnavailable=True)

      CustConfig.getDriveConfigAttributes(partNum=self.dut.partNum, failInvalidDCM = True)
      if self.dut.IdDevice.has_key('Logical Sector Size'):
         self.dut.driveattr['BYTES_PER_SCTR'] = str(self.dut.IdDevice['Logical Sector Size'])

      # update FIRMWARE_VER and CODE_VER just in case there is code download at earlier FIN2
      from CodeVer import theCodeVersion
      theCodeVersion.updateCodeRevisions()
      #self.validateDCMAttr('FIRMWARE_VER')
      objMsg.printMsg("DCM check is not required for FIRMWARE_VER. CCV and label station will check code version")

      objMsg.printMsg("testSwitch.FE_0180898_231166_OPTIMIZE_ATTR_VAL_FUNCS=%s" % (testSwitch.FE_0180898_231166_OPTIMIZE_ATTR_VAL_FUNCS))
      if testSwitch.FE_0180898_231166_OPTIMIZE_ATTR_VAL_FUNCS:
         sptCmds.enableDiags()

      #Bypass, as current CCV already validates the model number
      #and CCA CCV handles the model number processing when active
#CHOOI-02Jun17 Offspec
#       if testSwitch.FE_0181878_007523_CCA_CCV_PROCESS_LCO:
#           self.dut.driveattr['CUST_MODEL_NUM'] = self.dut.driveConfigAttrs['CUST_MODEL_NUM'][1] #MGM... won't work for anyone except sas... maybe ok but needs to be in new section
      self.handleModelNumber()
      self.handleMaxLBA()

#CHOOI-31May17 OffSpec
#       self.handleSNPrefix()      #to validate valid SNPrefix for the package
#
#       self.handleZGS()
#
#       self.handleBufferVerification()
#
#       if testSwitch.FE_0110517_347506_ADD_POWER_MODE_TO_DCM_CONFIG_ATTRS and not testSwitch.FE_0180898_231166_OPTIMIZE_ATTR_VAL_FUNCS:
#          self.handlePowerMode()
#
#       self.handleSetManufacturingStatus()
#
#       if testSwitch.FE_0318342_402984_CHECK_HDA_FW & testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT:
#          CustConfig.autoValidateHDAFw('HDA_FW')

      if testSwitch.FE_0180898_231166_OPTIMIZE_ATTR_VAL_FUNCS:
         # Make sure any cap values or drive values are refreshed with flash update
         if testSwitch.customerConfigInCAP:
            oSer = sptDiagCmds()
            if testSwitch.BF_0189843_470833_P_LOAD_OVLS_BEFORE_SAVE_CAP_TO_FLASH:
               oSer.OverlayRevCorrect() #force loading of overlays before attempting to save CAP to flash
            oSer.saveSegmentToFlash(0) #save CAP to flash
            oSer.getCapValue()
         sptCmds.enableESLIP()

         # Update the drive attributes for verification
         objPwrCtrl.powerCycle()

#CHOOI-31May17 OffSpec
#          CustConfig.updateDriveFISAttributes()
# 
#          # Fail if DCM check isn't availble unless disabled by configvar or sun model num
#          failIfUnavailable = testSwitch.FE_0141653_231166_P_FORCE_DCM_MODEL_AVAILABLE and ConfigVars[CN].get("F_DCM_N_MOD", True)
# 
#          # Validate attributes:
#          if not testSwitch.FE_0182319_426568_P_SKIP_LBA_MODEL_NUM_CHK_IF_NUM_HEADS_SET or (ConfigVars[CN].get('numHeads',0) == 0):
# 
#             if 'CUST_MODEL_NUM' in self.dut.driveConfigAttrs or (failIfUnavailable and not testSwitch.FE_0186972_357260_DESCRIPTIVE_FAIL_DCM_MISSING):
#                CustConfig.autoValidateDCMAttrString('CUST_MODEL_NUM')
#             elif failIfUnavailable and testSwitch.FE_0186972_357260_DESCRIPTIVE_FAIL_DCM_MISSING:
#                ScrCmds.raiseException(14761, "DCM Attribute CUST_MODEL_NUM Missing")
# 
#             if 'CUST_MODEL_NUM2' in self.dut.driveConfigAttrs: # This part of the cust model 1.. so if it isn't there then it isn't meant to be
#                CustConfig.autoValidateDCMAttrString('CUST_MODEL_NUM2')
# 
#             if not ConfigVars[CN].get('SKIP_LBA_CHECK', 0) and ('USER_LBA_COUNT' in self.dut.driveConfigAttrs or (testSwitch.FAIL_IF_NO_LBA_INFO_FOR_PARTNUMBER and not testSwitch.FE_0186972_357260_DESCRIPTIVE_FAIL_DCM_MISSING)):
#                   CustConfig.autoValidateDCMAttrLBAs('USER_LBA_COUNT')
#             elif testSwitch.FAIL_IF_NO_LBA_INFO_FOR_PARTNUMBER and testSwitch.FE_0186972_357260_DESCRIPTIVE_FAIL_DCM_MISSING:
#                ScrCmds.raiseException(14761, "DCM Attribute USER_LBA_COUNT Missing")

   def handleSetManufacturingStatus(self):
      if testSwitch.setManufacturingStatus: # BLM preventive as these calls were dangerous- F3 issue
         from serialScreen import sptDiagCmds
         oSer = sptDiagCmds()
         if not testSwitch.FE_0180898_231166_OPTIMIZE_ATTR_VAL_FUNCS:
            sptCmds.enableDiags()

         oSer.setCurrentManufacturingStatus(self.dut.nextOper, 0)
         if not testSwitch.FE_0180898_231166_OPTIMIZE_ATTR_VAL_FUNCS:
            objPwrCtrl.powerCycle()
            ICmd.HardReset()
            oIdentifyDevice = CIdentifyDevice()

   def handleATASignalSpeed(self):
      if ( self.dut.drvIntf in TP.WWN_INF_TYPE.get('WW_SAS_ID', []) or self.dut.drvIntf == 'SAS' ) :
         return
      import PIF

      ATASpeed_1_5  = getattr(PIF, 'ATASpeed_1.5', [])
      ATASpeed_3_0  = getattr(PIF, 'ATASpeed_3.0', [])

      reqSpeed = 'nominal'

      if self.dut.partNum[:6] in ATASpeed_1_5:
         reqSpeed = 1.5
         objMsg.printMsg("1.5 ATA Speed Requested")
      elif self.dut.partNum in ATASpeed_3_0:
         reqSpeed = 3.0
         objMsg.printMsg("3.0 ATA Speed Requested")
      else:
         objMsg.printMsg("No ATA Speed Requested. Setting to nominal.")

      from CustomerContent import CSetATASignalSpeed
      oSpeed = CSetATASignalSpeed(self.dut)
      oSpeed.run(reqSpeed)

   def handlePowerMode(self):
      '''Set Power Mode based on DCM attributes like Power On in Standby'''
      if ( self.dut.drvIntf in TP.WWN_INF_TYPE.get('WW_SAS_ID', []) or self.dut.drvIntf == 'SAS' ) :
         return

      objMsg.printMsg("Setting Power Mode")
      from CustomerContent import CPois

      oPois = 0
      if 'POWER_ON_TYPE' in self.dut.driveConfigAttrs:
         if self.dut.driveConfigAttrs['POWER_ON_TYPE'] =='PWR_ON_IN_STDBY':
            objMsg.printMsg("Power On in Standby detected from DCM.  Enabling POIS")
            oPois = CPois(self.dut,{'ENABLED':1})
         else:
            #placeholder for future power modes
            ScrCmds.raiseException(14761, "Unrecognized DCM attribute: %s" %self.dut.driveConfigAttrs['POWER_ON_TYPE'])
      else:
         #check to see if pois needs to be disabled
         oIdentifyDevice = CIdentifyDevice()
         if oIdentifyDevice.Is_POIS():
            objMsg.printMsg("Power On in Standby not detected from DCM but drive is in POIS mode.  Disabling POIS")
            oPois = CPois(self.dut,{'ENABLED':0})

      if oPois: #enable or disable pois based on how oPois was instantiated
         oPois.run()



   def handleBufferVerification(self):
      objMsg.printMsg("Setting Buffer Destroke Flags")
      if not testSwitch.customerConfigInCAP:
         objMsg.printMsg("Buffer Destroke Flags disabled by customerConfigInCAP == False")
         return
      import PIF

      CAP_Destroked_Buf_index = 0xFF

      CacheDestrokeLookup = { #cache size = 2**key, Value = F3 destroke word
        '3': 0x00,  #8Mb
        '4': 0x01,  #16Mb
        '5': 0x02,  #32Mb
        '6': 0x03,} #64Mb

      power = ''

      if testSwitch.useNonIntelligentPNCacheScheme:
         buffer8M  = getattr(PIF, 'Buffer_8M_PN', [])
         buffer16M = getattr(PIF, 'Buffer_16M_PN', [])

         if self.dut.partNum[:6] in buffer8M:
            power = '3'
         elif self.dut.partNum in buffer16M:
            power = '4'

      elif CacheDestrokeLookup.has_key(self.dut.partNum[4]):
         #Cache size is 2**(5th digit in the PN)
         power = self.dut.partNum[4]


      #if buffer size request detected, set F3 J cmd value and check against physical cache size
      if power:
         CAP_Destroked_Buf_index = CacheDestrokeLookup[power]
         destrokeCache = 2**int(power)

         objMsg.printMsg("%sM Buffer PN Detected" % destrokeCache)

         physCache = int(self.dut.driveattr.get('DRAM_PHYS_SIZE',0)) / 1000000.0

         if destrokeCache > physCache:
            objMsg.printMsg('Physical Cache (%sM) not as large as requested cache (%sM)' %(physCache,destrokeCache))
            if testSwitch.failIfPhysCacheSizeExceeded and not testSwitch.virtualRun:
               ScrCmds.raiseException(14761, "Requested cache larger than actual cache")
      else:
         objMsg.printMsg("No Alternate PN Buffer Size Detected. Setting to auto-detect (default).")


      from serialScreen import sptDiagCmds
      oSer = sptDiagCmds()
      #sptCmds.enableDiags()
      if testSwitch.FE_0180898_231166_OPTIMIZE_ATTR_VAL_FUNCS:
         oSer.setCAPValue("DESTROK_BUF_SZ_INDEX", CAP_Destroked_Buf_index, saveToFlash = False)
      else:
         oSer.setCAPValue("DESTROK_BUF_SZ_INDEX", CAP_Destroked_Buf_index, saveToFlash = True)
         objPwrCtrl.powerCycle()
         ICmd.HardReset()
         oIdentifyDevice = CIdentifyDevice()


   def handleMaxLBA(self):

      userLBACountOverride = getattr(TP, 'USER_LBA_COUNT_Override', {}).get(self.dut.partNum, None)
      if not userLBACountOverride:
         userLBACountOverride = getattr(TP, 'USER_LBA_COUNT_Override', {}).get(self.dut.partNum[:6], None)

      if ("USER_LBA_COUNT" in self.dut.driveConfigAttrs or userLBACountOverride != None) and (testSwitch.customerConfigInCAP and testSwitch.auditTest ==0):
         #Allow TP overrides
         if userLBACountOverride != None:
            if testSwitch.FE_0146721_007955_P_ALLOW_DRVMODELNUM_LBA_OVERRIDES_AT_LCO_ONLY:
               if testSwitch.BF_0166991_231166_P_USE_PROD_MODE_DEV_PROD_HOSTSITE_FIX:
                  if not ConfigVars[CN]['PRODUCTION_MODE']:
                     objMsg.printMsg("Overrode DCM 'USER_LBA_COUNT' with TP value %s" % (userLBACountOverride,))
                     self.dut.driveConfigAttrs['USER_LBA_COUNT'] = ('=',userLBACountOverride)
               else:
                  if RequestService('GetSiteconfigSetting','CMSHostSite')[1].get('CMSHostSite','NA') in ['LCO']:
                     objMsg.printMsg("Overrode DCM 'USER_LBA_COUNT' with TP value %s" % (userLBACountOverride,))
                     self.dut.driveConfigAttrs['USER_LBA_COUNT'] = ('=',userLBACountOverride)
            else:
               objMsg.printMsg("Overrode DCM 'USER_LBA_COUNT' with TP value %s" % (userLBACountOverride,))
               self.dut.driveConfigAttrs['USER_LBA_COUNT'] = ('=',userLBACountOverride)

         from serialScreen import sptDiagCmds
         oSer = sptDiagCmds()
         if testSwitch.FE_0180898_231166_OPTIMIZE_ATTR_VAL_FUNCS:
            oSer.setCAPValue("IDEMA_CAP", int(self.dut.driveConfigAttrs["USER_LBA_COUNT"][1]), saveToFlash = False)
         else:
            #sptCmds.enableDiags()
            oSer.setCAPValue("IDEMA_CAP", int(self.dut.driveConfigAttrs["USER_LBA_COUNT"][1]), saveToFlash = True)
            objPwrCtrl.powerCycle()
            ICmd.HardReset()
            oIdentifyDevice = CIdentifyDevice()

      if not testSwitch.FE_0180898_231166_OPTIMIZE_ATTR_VAL_FUNCS:
         if not "Max LBA" in self.dut.IdDevice or not "Max LBA Ext" in self.dut.IdDevice:
            oIdentifyDevice = CIdentifyDevice()

         self.dut.driveattr['USER_LBA_COUNT'] = str(max(self.dut.IdDevice["Max LBA Ext"]+1, self.dut.IdDevice["Max LBA"]+1))

         if testSwitch.auditTest == 0:
            if not ConfigVars[CN].get('SKIP_LBA_CHECK', 0):
               self.validateDCMAttr('USER_LBA_COUNT', failIfUnavailable = testSwitch.FAIL_IF_NO_LBA_INFO_FOR_PARTNUMBER)
         else:
            objMsg.printMsg("AUDIT TEST: Bypasing validateDCMAttr call",objMsg.CMessLvl.IMPORTANT)# num LBAs are small, dont check this against normal LBA count

   def handleModelNumber(self):
      from CustomCfg import CCustomCfg
      from serialScreen import sptDiagCmds
      if testSwitch.FE_0180898_231166_OPTIMIZE_ATTR_VAL_FUNCS:
         oCFG = CCustomCfg()
         localModelNumber = oCFG.getDCMModelNum()

#CHOOI-15May17 OffSpec
         oSer = sptDiagCmds()

         if DriveAttributes['PART_NUM'][3:6] == '174':
            localModelNumber = 'ST2000LM007'
         elif DriveAttributes['PART_NUM'][3:6] == '17G':
            localModelNumber = 'ST1500LM012'
         elif DriveAttributes['PART_NUM'][3:6] == '172':
            localModelNumber = 'ST1000LM035'
         else:
            localModelNumber = 'ST500LM030'

         objMsg.printMsg("1. localModelNumber: %s, " % (localModelNumber))

#         oSer.setCAPValue("HDA_SN", "00000000", saveToFlash = False)
         oSer.setCAPValue("EXTERNAL_MODEL_NUM", localModelNumber, saveToFlash = False)
         oSer.setCAPValue("INTERNAL_MODEL_NUM", localModelNumber, saveToFlash = False)
#          if testSwitch.customerConfigInCAP:
#             oSer = sptDiagCmds()
# 
#             localModelNumber = localModelNumber.replace('[','').replace(']','')
# 
#             if not testSwitch.FE_0195908_231166_P_WRT_ST_MODEL_PART_INTERNAL:
#                oSer.setCAPValue("INTERNAL_MODEL_NUM", localModelNumber, saveToFlash = False)
#             oSer.setCAPValue("EXTERNAL_MODEL_NUM", localModelNumber, saveToFlash = False)
# 
#             if testSwitch.FE_0195908_231166_P_WRT_ST_MODEL_PART_INTERNAL:
#                internalMod = 'ST_PROC_INVALID'
#                match = re.search('ST\w*', localModelNumber)
#                if match:
#                   internalMod = match.group()
# 
#                oSer.setCAPValue("INTERNAL_MODEL_NUM", internalMod, saveToFlash = False)


      else:
         if testSwitch.FE_0124649_399481_SKIP_MODEL_NUMBER_HANDLER_BY_PN:
            PN_regexkey = Utility.CUtility.getRegex(self.dut.partNum, TP.Skip_Model_Number_Handler)
            if PN_regexkey:
               objMsg.printMsg("PN: %s, matched Skip_Model_Number_Handler entry for %s, skipping handleModelNumber." % (self.dut.partNum, PN_regexkey,))
               return

         sunModelID = None
         justification = "LEFT"

         if testSwitch.FE_0152577_231166_P_FIS_SUPPORTS_CUST_MODEL_BRACKETS:
            if '[' not in self.dut.driveConfigAttrs.get('CUST_MODEL_NUM', ['', ''])[1]:
               objMsg.printMsg("Detected [] not supported in cust model num... disabling FE_0152577_231166_P_FIS_SUPPORTS_CUST_MODEL_BRACKETS.")
               testSwitch.FE_0152577_231166_P_FIS_SUPPORTS_CUST_MODEL_BRACKETS = 0

         drvModelNumOverride = getattr(TP, 'DRV_MODEL_NUM_Override', {}).get(self.dut.partNum, None)
         if not drvModelNumOverride:
            drvModelNumOverride = getattr(TP, 'DRV_MODEL_NUM_Override', {}).get(self.dut.partNum[:6], None)

         if (("CUST_MODEL_NUM" in self.dut.driveConfigAttrs or 'DRV_MODEL_NUM' in self.dut.driveConfigAttrs) or drvModelNumOverride !=None) and testSwitch.customerConfigInCAP:
            #Allow TP overrides

            if drvModelNumOverride != None:
               if testSwitch.FE_0146721_007955_P_ALLOW_DRVMODELNUM_LBA_OVERRIDES_AT_LCO_ONLY:
                  if testSwitch.BF_0166991_231166_P_USE_PROD_MODE_DEV_PROD_HOSTSITE_FIX:
                     if not ConfigVars[CN]['PRODUCTION_MODE']:
                        objMsg.printMsg("Overrode DCM 'DRV_MODEL_NUM' with TP value %s" % (drvModelNumOverride,))
                        self.dut.driveConfigAttrs['DRV_MODEL_NUM'] = ('=',drvModelNumOverride)
                  else:
                     if RequestService('GetSiteconfigSetting','CMSHostSite')[1].get('CMSHostSite','NA') in ['LCO']:
                        objMsg.printMsg("Overrode DCM 'DRV_MODEL_NUM' with TP value %s" % (drvModelNumOverride,))
                        self.dut.driveConfigAttrs['DRV_MODEL_NUM'] = ('=',drvModelNumOverride)
               else:
                  objMsg.printMsg("Overrode DCM 'DRV_MODEL_NUM' with TP value %s" % (drvModelNumOverride,))
                  self.dut.driveConfigAttrs['DRV_MODEL_NUM'] = ('=',drvModelNumOverride)

            custModelNumOverride = getattr(TP, 'CUST_MODEL_NUM_Override', {}).get(self.dut.partNum, None)
            if custModelNumOverride == None:
               custModelNum = self.dut.driveConfigAttrs.get("CUST_MODEL_NUM",(None,None))

               if custModelNum[1] == None:
                  custModelNum = self.dut.driveConfigAttrs['DRV_MODEL_NUM']

               self.dut.driveConfigAttrs['CUST_MODEL_NUM'] = custModelNum
            else:
               objMsg.printMsg("Overrode DCM 'CUST_MODEL_NUM' with TP value %s" % (custModelNumOverride,))
               self.dut.driveConfigAttrs['CUST_MODEL_NUM'] = ('=',custModelNumOverride)

            if testSwitch.FE_0121886_231166_FULL_SUN_MODEL_NUM:
               from PIFHandler import CPIFHandler
               PIFHandler = CPIFHandler()
               dPNum = PIFHandler.getPnumInfo(self.dut.partNum)                 # Get the dict of info for this partnum

               if 'WRITE_SUN_MODEL' in [i['ID'] for i in dPNum['lCAIDS']]:
                  #ID if SUN PN

                  objMsg.printMsg("Detected SUN model number update required")
                  import PIF
                  #Get the sun model number ID from PIF... for mat is SunModelId = {'PN':value}
                  sunModelID = Utility.CUtility.getRegex(self.dut.partNum, PIF.SunModelId)
                  if sunModelID == None:
                     ScrCmds.raiseException(11049, "PIF.SunModelId not set up properly for SUN_MODEL_NUM")


                  custCfg = CCustomCfg()

                  sptCmds.enableESLIP()
                  ICmd.HardReset()

                  custCfg.writeWorkDate()
                  if custModelNumOverride != None:
                     sunModelNum = custCfg.getSunModelNum(self.dut.driveConfigAttrs['CUST_MODEL_NUM'][1], sunModelID)

                     if testSwitch.WA_0149421_231166_P_REMOVE_SPACES_MODEL_NUM:
                        self.dut.driveConfigAttrs['CUST_MODEL_NUM'] = ('=', sunModelNum[0:32].strip())
                        if len(sunModelNum) > 32:
                           self.dut.driveConfigAttrs['CUST_MODEL_NUM2'] = ('=', sunModelNum[32:].strip())
                     else:
                        self.dut.driveConfigAttrs['CUST_MODEL_NUM'] = ('=', sunModelNum[0:32])
                        if len(sunModelNum) > 32:
                           self.dut.driveConfigAttrs['CUST_MODEL_NUM2'] = ('=', sunModelNum[32:])

                  sptCmds.enableDiags()

            # Valid justifications are "LEFT" or "RIGHT"
            justification = self.dut.driveConfigAttrs.get('CUST_MN_JUSTIFY', getattr(TP, 'driveModelJustification',{}).get(self.dut.partNum, ('=',"LEFT")))[1]
            self.dut.driveattr['CUST_MN_JUSTIFY'] = justification

            if self.dut.nextOper == "CUT2" and testSwitch.auditTest:
               self.dut.driveConfigAttrs['DRV_MODEL_NUM'] = (0, "STFFFFAUDIT")
               self.dut.driveConfigAttrs['CUST_MODEL_NUM'] = (0, "STFFFFAUDIT")

            from serialScreen import sptDiagCmds
            if testSwitch.FE_0152577_231166_P_FIS_SUPPORTS_CUST_MODEL_BRACKETS:
               #fix up the local values to strip out spaces and chars not meant for drive
               localModelNumber = self.dut.driveConfigAttrs['CUST_MODEL_NUM'][1] + self.dut.driveConfigAttrs.get('CUST_MODEL_NUM2',('',''))[1]

               #remove the [ ] and trailing spaces
               localModelNumber = localModelNumber.replace('[', '').replace(']', '').rstrip()

               if justification == "RIGHT":


                  if ( self.dut.drvIntf in TP.WWN_INF_TYPE.get('WW_SAS_ID', []) or self.dut.drvIntf == 'SAS' ):
                     #sas
                     localModelNumber = localModelNumber.rjust(24," ")

                  else:
                     #sata
                     localModelNumber = localModelNumber.rjust(40," ")

               objMsg.printMsg("Writing %s model number to CAP" % localModelNumber)

               oSer = sptDiagCmds()
               #sptCmds.enableDiags()
               oSer.setCAPValue("INTERNAL_MODEL_NUM", localModelNumber, saveToFlash = False)
               oSer.setCAPValue("EXTERNAL_MODEL_NUM", localModelNumber, saveToFlash = True)


            else:
               if justification == "RIGHT":
                  operator, value = self.dut.driveConfigAttrs['CUST_MODEL_NUM']
                  self.dut.driveConfigAttrs['CUST_MODEL_NUM'] = (operator, value.rjust(40," "))


               oSer = sptDiagCmds()
               #sptCmds.enableDiags()
               oSer.setCAPValue("INTERNAL_MODEL_NUM", self.dut.driveConfigAttrs['DRV_MODEL_NUM'][1] +  self.dut.driveConfigAttrs.get('DRV_MODEL_NUM2', ('', ''))[1], saveToFlash = False)
               oSer.setCAPValue("EXTERNAL_MODEL_NUM", self.dut.driveConfigAttrs['CUST_MODEL_NUM'][1] + self.dut.driveConfigAttrs.get('CUST_MODEL_NUM2', ('', ''))[1], saveToFlash = True)

            objPwrCtrl.powerCycle()
            ICmd.HardReset()
            oIdentifyDevice = CIdentifyDevice()

         if testSwitch.virtualRun:
            dmod = getattr(TP, 'veModelNum','ST3500410AS')

            if self.dut.nextOper == "CUT2" and testSwitch.auditTest:
               dmod = "STFFFFAUDIT"

            self.dut.IdDevice['IDModel'] = dmod

         if not 'IDModel' in self.dut.IdDevice:
            oIdentifyDevice = CIdentifyDevice()

         if testSwitch.FE_0121886_231166_FULL_SUN_MODEL_NUM:
            idModelNum = self.dut.IdDevice['IDModel']
            if testSwitch.FE_0152577_231166_P_FIS_SUPPORTS_CUST_MODEL_BRACKETS:
               if justification == "RIGHT":
                  #need to remove the left spaces for validation- that is handled seperately
                  idModelNum = idModelNum.lstrip()
         else:
            idModelNum = self.dut.IdDevice['IDModel'].strip()


         if not testSwitch.FE_0142909_231166_P_SUPPORT_SAS_DRV_MODEL_NUM and ( self.dut.drvIntf in TP.WWN_INF_TYPE.get('WW_SAS_ID', []) or self.dut.drvIntf == 'SAS' ):
            driveModelNum = self.dut.IdDevice['IDModel']
         else:
            driveModelNum = self.getDriveModelNum()


         if idModelNum == '':
            idModelNum = driveModelNum

         failIfUnavailable = False
         if testSwitch.FE_0141653_231166_P_FORCE_DCM_MODEL_AVAILABLE:
            # Fail if dcm check isn't availble unless disabled by configvar or sun model num
            failIfUnavailable = True and ConfigVars[CN].get("F_DCM_N_MOD", True) and (sunModelID == None)


         if testSwitch.BF_0163418_231166_P_ECHO_DRV_MODEL_NUM_TO_FIS_DCM:
            if 'DRV_MODEL_NUM' in self.dut.driveConfigAttrs:
               self.dut.driveattr['DRV_MODEL_NUM'] = self.dut.driveConfigAttrs['DRV_MODEL_NUM'][1]
            if 'DRV_MODEL_NUM2' in self.dut.driveConfigAttrs:
               self.dut.driveattr['DRV_MODEL_NUM2'] = self.dut.driveConfigAttrs['DRV_MODEL_NUM2'][1]

            self.validateDCMAttr('DRV_MODEL_NUM', False)
            self.validateDCMAttr('DRV_MODEL_NUM2', False)
         else:
            self.dut.driveattr['DRV_MODEL_NUM'] = driveModelNum
            if not testSwitch.BF_0157043_231166_P_DISABLE_DRV_MODEL_NUM_VALIDATION:
               self.validateDCMAttr('DRV_MODEL_NUM', failIfUnavailable)




         if testSwitch.FE_0152577_231166_P_FIS_SUPPORTS_CUST_MODEL_BRACKETS:

            self.dut.driveattr['CUST_MODEL_NUM'], self.dut.driveattr['CUST_MODEL_NUM2'] = CCustomCfg().makeModelNumFisReady(idModelNum)


            self.validateDCMAttr('CUST_MODEL_NUM', failIfUnavailable)
            if 'CUST_MODEL_NUM2' not in self.dut.driveConfigAttrs:
               #remove it to avoid the need to validate
               del self.dut.driveattr['CUST_MODEL_NUM2']
            else:
               self.validateDCMAttr('CUST_MODEL_NUM2', failIfUnavailable)

         else:
            if len(idModelNum) <= 32:
               if testSwitch.WA_0149421_231166_P_REMOVE_SPACES_MODEL_NUM:
                  self.dut.driveattr['CUST_MODEL_NUM'] = idModelNum.strip()
               else:
                  self.dut.driveattr['CUST_MODEL_NUM'] = idModelNum
               self.validateDCMAttr('CUST_MODEL_NUM', failIfUnavailable)
            else:
               if testSwitch.FE_0145290_231166_P_SUPPORT_QUTOES_CUST_MODEL_NUM:
                  idModelNum = idModelNum.strip()
                  self.dut.driveattr['CUST_MODEL_NUM'] = '"%s"' %  (idModelNum[0:30],)
                  self.dut.driveattr['CUST_MODEL_NUM2'] = '"%s"' % (idModelNum[30:],)
               else:
                  if testSwitch.WA_0149421_231166_P_REMOVE_SPACES_MODEL_NUM:
                     self.dut.driveattr['CUST_MODEL_NUM'] = idModelNum[0:32].strip()
                     self.dut.driveattr['CUST_MODEL_NUM2'] = idModelNum[32:].strip()
                  else:
                     self.dut.driveattr['CUST_MODEL_NUM'] = idModelNum[0:32]
                     self.dut.driveattr['CUST_MODEL_NUM2'] = idModelNum[32:]


               self.validateDCMAttr('CUST_MODEL_NUM', failIfUnavailable)

               if testSwitch.BF_0123471_231166_DEL_CUST_MOD2_IF_INVALID and self.dut.driveattr['CUST_MODEL_NUM2'].strip() in ['','?']:
                  del self.dut.driveattr['CUST_MODEL_NUM2']
               else:
                  self.validateDCMAttr('CUST_MODEL_NUM2', failIfUnavailable)


   def handleSNPrefix(self):

      drvSn = self.dut.IdDevice['IDSerialNumber']

      if not len(self.params):
         objMsg.printMsg("No SNPrefix" )
         return
      else:
         if drvSn[1:3].upper() not in self.params.keys():
            objMsg.printMsg('Invalid drv s/n prefix')
            if not testSwitch.virtualRun:
               ScrCmds.raiseException(14761, "SNPrefix mismatch")

   def getSNPrefix_SP(self):
      if testSwitch.FE_0314744_496648_GET_CAP_VAL_USING_DETS:
         serialnumber = ICmd.getCAPSettings(01)
         return serialnumber
      else:
         from serialScreen import sptDiagCmds
         oSer = sptDiagCmds()
         oSer.enableDiags()
         pattern = 'Number:\s(?P<HDASN>\w+)'
         result = oSer.getCapValue(prmKey=0x1)
         match = re.search(pattern,result)
         drvsn = match.groupdict()['HDASN']
         return drvsn

   def handleZGS(self):
      if testSwitch.FE_0180898_231166_OPTIMIZE_ATTR_VAL_FUNCS:

         if 'ZERO_G_SENSOR' in self.dut.driveConfigAttrs:
            from CustomCfg import CCustomCfg
            CCustomCfg().autoValidateZGS()
      else:
         ZGS = self.dut.IdDevice['ZGS']
         driveattr_ZGS = self.dut.driveattr['ZERO_G_SENSOR']

         if not (str(self.dut.driveConfigAttrs.get('ZERO_G_SENSOR',(0,'NA'))[1]).rstrip() == 'NA' and testSwitch.FE_0157486_357260_P_DO_NOT_CHECK_ZGS_BIT_IF_DCM_SAYS_NA):
            if ZGS and (driveattr_ZGS == "0" or driveattr_ZGS == "NA"):
               objMsg.printMsg('Error: ZGS = 1 but DriveAttribute ZERO_G_SENSOR = 0/NA')
               ScrCmds.raiseException(14761, "ZGS = 1 but DriveAttribute ZERO_G_SENSOR = 0/NA")
            elif not ZGS and driveattr_ZGS == "1":
               objMsg.printMsg('Error: ZGS = 0 but DriveAttribute ZERO_G_SENSOR = 1')
               if not testSwitch.BF_0122964_231166_NO_FAIL_FOR_ZGS_AVAIL_NOT_NEED:
                  ScrCmds.raiseException(14761, "ZGS = 0 but DriveAttribute ZERO_G_SENSOR = 1")

         self.validateDCMAttr('ZERO_G_SENSOR')

   def getZGS_SP(self):
      sptCmds.enableDiags()
      sptCmds.gotoLevel('T')
      result = sptCmds.sendDiagCmd('''F"FREEFALL_SENSOR_SUPPORTED"''')
      result = result.replace('F3 T>','')
      ZGS = int(result.strip()[-1:])
      return ZGS

########################################################################################
 #CHOOI-01JUN16 OFFSPEC
   def checkdriveattribute(self):

      ICmd.SetRFECmdTimeout(14*3600)
      ICmd.SetIntfTimeout(15*1000)

      oIdentifyDevice = CIdentifyDevice()

      objMsg.printMsg("===============================================================")
      objMsg.printMsg("IDSerialNumber : %s " % (self.dut.IdDevice['IDSerialNumber']) )
      objMsg.printMsg("IDModel        : %s " % (self.dut.IdDevice['IDModel']) )
      objMsg.printMsg("Max Cyl        : %s " % (self.dut.IdDevice["Max Cyl"]+1) )
      objMsg.printMsg("Max LBA        : %s " % (self.dut.IdDevice["Max LBA"]+1) )
      objMsg.printMsg("Max LBA Ext    : %s " % (self.dut.IdDevice["Max LBA Ext"]+1) )
      objMsg.printMsg("===============================================================")

#CHOOI-03Apr14 Added
      if DriveAttributes['PART_NUM'][3:6] == '174':
         driveModelNum = 'OOS2000G'
      elif DriveAttributes['PART_NUM'][3:6] == '17G':
         driveModelNum = 'OOS1500G'
      elif DriveAttributes['PART_NUM'][3:6] == '172':
         driveModelNum = 'OOS1000G'
      else:
         driveModelNum = 'OOS500G'

#      driveModelNum = self.dut.IdDevice['IDModel'].strip()
      self.dut.driveattr['DRV_MODEL_NUM'] = driveModelNum
      self.dut.driveattr['TP_DRV_SN'] = self.dut.IdDevice['IDSerialNumber']
      self.dut.driveattr['USER_LBA_COUNT'] = str(max(self.dut.IdDevice["Max LBA Ext"]+1, self.dut.IdDevice["Max LBA"]+1))

      self.dut.driveattr['SECURITY_TYPE'] = 'SECURED BASE (SD AND D)'
      self.dut.driveattr['SED_LC_STATE'] = 'USE'
      self.dut.driveattr['CUST_TESTNAME'] = 'SC1'
      self.dut.driveattr['ZERO_PTRN_RQMT'] = '20'
      self.dut.driveattr['BYTES_PER_SCTR'] = '512'
      DriveAttributes['IV_SW_REV'] = self.dut.driveattr['IV_SW_REV'] = '30.05'

########################################################################################

   def validateDCMAttr(self, attrName, failIfUnavailable = False):
      if attrName in self.dut.driveConfigAttrs:
         if not testSwitch.FE_0122225_399481_STRIP_TRAILING_WHITESPACE_IN_ATTRIBUTE_COMPARE:
            if not self.dut.driveConfigAttrs[attrName][1] == self.dut.driveattr[attrName]:
               msg = "Invalid DCM attribute found in validation!\nAttrName:%s\nAttrValue:%s\nAttrRequirement:%s" % (attrName, self.dut.driveattr[attrName], self.dut.driveConfigAttrs[attrName][1])
               if not ( testSwitch.virtualRun or ConfigVars[CN].get('DIS_ATRV_VER', 0) or ConfigVars[CN].get('BenchTop', 0) ):
                  ScrCmds.raiseException(14761, msg)
               else:
                  objMsg.printMsg("VE WARNING!!!-> %s" % msg)
         else:
            if not self.dut.driveConfigAttrs[attrName][1].rstrip() == self.dut.driveattr[attrName].rstrip():
               msg = "Invalid DCM attribute found in validation!\nAttrName:%s\nAttrValue:%s\nAttrRequirement:%s" % (attrName, self.dut.driveattr[attrName], self.dut.driveConfigAttrs[attrName][1])
               if not ( testSwitch.virtualRun or ConfigVars[CN].get('DIS_ATRV_VER', 0) or ConfigVars[CN].get('BenchTop', 0) ):
                  ScrCmds.raiseException(14761, msg)
               else:
                  objMsg.printMsg("VE WARNING!!!-> %s" % msg)
         objMsg.printMsg("Validated attribute %s = %s" % (attrName, self.dut.driveattr[attrName]) )
      else:
         if failIfUnavailable and not ConfigVars[CN].get('DIS_ATRV_VER', 0):
            ScrCmds.raiseException(14761, "Unable to validate DCM attribute: No information for validation of %s" % attrName)
         else:
            objMsg.printMsg("Skipping DCM attribute validation: No information for validation of %s" % attrName)


   def getDriveModelNum(self):

      if testSwitch.NoIO:

         sptCmds.enableDiags()
         data2=sptCmds.sendDiagCmd('/TF"InternalSeagateModelNumber"\r',altPattern='T>',printResult=True)
         if testSwitch.virtualRun:
            data2 = \
               """
               Byte:01A0:       InternalSeagateModelNumber =
                                53 54 35 30 30 4C 54 30 31 32 2D 31 44 47 31 34
                                32 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20
                                20 20 20 20 20 20 20 20
                                'ST500LT012-1DG142                       '
               """
         m = re.search('ModelNumber =', data2)
         if m == None:
            objMsg.printMsg('getDriveModelNum failed. Cannot read "ModelNumber ="')
            ScrCmds.raiseException(10609,"getDriveModelNum failed.")

         model = data2[m.end():].split("'")[1]
         model = model.strip()

         objMsg.printMsg("NoIO getDriveModelNum. ModelNum= %s " % (model))

         return model

      import struct
      if testSwitch.FE_0142909_231166_P_SUPPORT_SAS_DRV_MODEL_NUM and ( self.dut.drvIntf in TP.WWN_INF_TYPE.get('WW_SAS_ID', []) or self.dut.drvIntf == 'SAS' ):
         cmdDef = {'modelNum'    : (7     , 16 , 's'),
                   }
         ICmd.DriveModelNumberInquiry()
      else:
         cmdDef = {'modelNum'    : (20     , 60 , 's'),
                }
         packageOutput = {}
         buffNum = 1   #ATA feature bit 11
         mode = 5       #PIO Read
         objPwrCtrl.powerCycle()
         ICmd.HardReset()
         stat = ICmd.IdentifyDevice(force = True)
         ICmd.ClearBinBuff()

         dataBuffer = ICmd.PassThrough( mode, 0xEC, 0x2097, 0xa0, 0xdb, 0, buffNum, 0 )

         objMsg.printDict(dataBuffer)
         if dataBuffer['LLRET'] == -1:
            ScrCmds.raiseException(10609,"Extended Mode command 0xEC for page 11 extended ID data failed.")

      dataBuffer = ICmd.GetBuffer( 0x2, 0, 0x200 )
      if testSwitch.virtualRun:
         dataBuffer = {}
         dmod = getattr(TP, 'veModelNum','ST3500410AS')
         dataBuffer['DATA'] = (60-len(dmod))*'\x00' + dmod
      modData = {}

      for key in cmdDef.keys():
         pckData = dataBuffer['DATA'][cmdDef[key][0]:cmdDef[key][0]+cmdDef[key][1]]
         lenPckData = len(pckData)
         try:
            modData[key] = objMsg.cleanASCII(''.join(struct.unpack(cmdDef[key][2]*lenPckData,pckData)))
            modData[key] = modData[key].strip()
         except:
            objMsg.printMsg(traceback.format_exc())
            objMsg.printMsg("Failure Info: Buffer[%s]; Format[%s]" % (pckData,cmdDef[key][2]*lenPckData))

      return modData.get('modelNum')

   #---------------------------------------------------------------------------------------------------------#
   def serialGetDrvData(self):

      result = ICmd.Standby(0)
      if result['LLRET'] != OK:
         objMsg.printMsg('Standby Mode 0 failed!')
         return 1,-1,-1,-1,-1,''


      result = ICmd.SetFeatures(0x85)
      if result['LLRET'] != OK:
         if result['ERR'] == '4':
            objMsg.printMsg("Disable APM not supported")
            ICmd.HardReset()
            ICmd.IdentifyDevice()
         else:
            objMsg.printMsg('Disable Advance Power Management Failed!')
            return 1,-1,-1,-1,-1,''

      result = ICmd.Seek(0)      # Seek to LBA 0
      if result['LLRET'] != OK:
         objMsg.printMsg('Seek cmd Failed!')
         return 1,-1,-1,-1,-1,''


      sptCmds.sendDiagCmd(CTRL_Z,altPattern='>',printResult=True)
      data=sptCmds.sendDiagCmd(CTRL_L,altPattern='PreampType:',printResult=True)
      sptCmds.sendDiagCmd('/\r',altPattern='T>',printResult=True)
      data2=sptCmds.sendDiagCmd('F"InternalSeagateModelNumber"\r',altPattern='T>',printResult=True)

      # Get max LBA
      m = re.search('Lbas:', data)
      if m == None:
         objMsg.printMsg('serialGetDrvData fail. Cannot read "Lbas:"')
         return 1,-1,-1,-1,-1,''
      lbas = data[m.end():].split(',')[0]
      lbas = int(lbas,16)

      # Get hda s/n
      m = re.search('HDA SN:', data)
      if m == None:
         objMsg.printMsg('serialGetDrvData fail. Cannot read "HDA SN:"')
         return 1,-1,-1,-1,-1,''
      hdasn = data[m.end():].split(',')[0]
      hdasn = hdasn.split()[0]

      # Get PFM_ID
      m = re.search('MemberId:', data)
      if m == None:
         objMsg.printMsg('serialGetDrvData fail. Cannot read "MemberId:"')
         return 1,-1,-1,-1,-1,''
      pfm_id = data[m.end():].split(',')[0]
      pfm_id = pfm_id.split()[0]
      pfm_id = int(pfm_id,16)

      # Get Heads
      m = re.search('Heads:', data)
      if m == None:
         objMsg.printMsg('serialGetDrvData fail. Cannot read "Heads:"')
         return 1,-1,-1,-1,-1,''
      heads = data[m.end():].split(',')[0]
      heads = heads.split()[0]
      heads = int(heads,16)

      # Get Model number
      m = re.search('ModelNumber =', data2)
      if m == None:
         objMsg.printMsg('serialGetDrvData fail. Cannot read "ModelNumber ="')
         return 1,-1,-1,-1,-1,''

      model = data2[m.end():].split("'")[1]
      model = model.strip()

      return OK, lbas , model, pfm_id, heads, hdasn
###########################################################################################################
###########################################################################################################
class CCustomConfig(CState):
   """
      Class that implements the Customer Configuration functionality.  A PIF file which defines the customer functions to implement is imported and
      each operation is executed.  If the partnumber is not in the PIF file, this function will fail.
   """
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)


   def run(self):

      from CustomCfg import CCustomCfg
      CustConfig = CCustomCfg()
      dcm_data = CustConfig.getDriveConfigAttributes(partNum = self.dut.partNum, failInvalidDCM = True)
      from PIFHandler import CPIFHandler
      PIFHandler = CPIFHandler()


      dPNum = PIFHandler.getPnumInfo(self.dut.partNum)                 # Get the dict of info for this partnum
      if 'SC1' in dcm_data.get('CUST_TESTNAME',('=','NONE'))[1]:
         try:
            dPNum["Screens"].remove('LOW_SPIN_CURRENT') # low current spinup done in earlier LC_SPINUP state
         except:
            pass

      if len(dPNum):
         objMsg.printMsg('%s Screens: %s, Content: %s' % (self.dut.partNum, dPNum.get('Screens',[]), dPNum.get('Content',[])))
         if testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT and testSwitch.FE_0221005_504374_P_3TIER_MULTI_OPER:
            if objComMode.getMode() != objComMode.availModes.intBase:
               objPwrCtrl.powerCycle()
         CustConfig.ProcessCustomCfg(dPNum)                    # Go process the customer operations for this partnum
         CustConfig.ProcessCustomScreens(dPNum)
         if testSwitch.FE_0152007_357260_P_DCM_ATTRIBUTE_VALIDATION:
            CustConfig.ProcessCustomContent(dPNum)
            CustConfig.ProcessCustomAttributeRequirements()
         else:
            CustConfig.ProcessCustomAttributeRequirements()
            CustConfig.ProcessCustomContent(dPNum)
      else:
         objMsg.printMsg( 'Partnum %s not found in PIF file' % self.dut.partNum )
         ScrCmds.raiseException(11044,"Partnumber: %s not found in PIF file" % self.dut.partNum)

###########################################################################################################
class CConfigLowCurrentSpinup(CState):
   """
      Class that checks and implements low current spin up feature.
   """
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)


   def run(self):

      from CustomCfg import CCustomCfg
      CustConfig = CCustomCfg()
      dcm_data = CustConfig.getDriveConfigAttributes(partNum = self.dut.partNum, failInvalidDCM = True)

      dPNum = {}
      if 'SC1' in dcm_data.get('CUST_TESTNAME',('=','NONE'))[1]:
         dPNum["Screens"] = ['LOW_SPIN_CURRENT']
      else:
         dPNum["Screens"] = ['NORMAL_SPIN_CURRENT']

      if len(dPNum):
         objMsg.printMsg('%s Screens: %s' % (self.dut.partNum, dPNum.get('Screens',[])))
         if testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT and testSwitch.FE_0221005_504374_P_3TIER_MULTI_OPER:
            if objComMode.getMode() != objComMode.availModes.intBase:
               objPwrCtrl.powerCycle()
         CustConfig.ProcessCustomCfg(dPNum)                    # Go process the customer operations for this partnum
         CustConfig.ProcessCustomScreens(dPNum)
      else:
         objMsg.printMsg( 'Partnum %s not found in PIF file' % self.dut.partNum )
         ScrCmds.raiseException(11044,"Partnumber: %s not found in PIF file" % self.dut.partNum)


###########################################################################################################
class CCriticalEvents(CState):
   """
      Description: Class that will Check the Critical Event Log.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):

      if self.dut.drvIntf in TP.WWN_INF_TYPE.get('WW_SAS_ID', []) or self.dut.drvIntf == 'SAS':
         ICmd.SmartReturnFrameData()

         if testSwitch.FE_0140112_357552_FAIL_FOR_IO_TCM_ECC_ERRORS:
            ICmd.IOECC_DTCM_Check()

            #NOT Drive self test - this is "Default" (or SCSI) Self-Test - tests things that
            #  Drive Self Test does not - e.g. DRAM test.
            ICmd.SCSI_SelfTest()

      else:
         smartEnableOperData = ICmd.SmartEnableOper()
         objMsg.printMsg("SmartEnableOper data: %s" % smartEnableOperData, objMsg.CMessLvl.IMPORTANT)
         if smartEnableOperData['LLRET'] != 0:
            ScrCmds.raiseException(13455, 'Failed Smart Enable Oper')
         CriticalLogData = ICmd.SmartReadLogSec(0xA1, 20) #Read 20 Log sectors
         objMsg.printMsg("SmartReadLogSec data: %s" % CriticalLogData, objMsg.CMessLvl.IMPORTANT)
         if CriticalLogData['LLRET'] != 0:
            ScrCmds.raiseException(13456, 'Failed Reading Smart Log:0xA1')
         else:
            CriticalLogData['GETBUFFER'] = ICmd.GetBuffer(RBF, 0, (512*20))  # 20 Critical Event Log Sectors

         critical_event_count = 0
         if testSwitch.virtualRun:
            objMsg.printMsg("Interface Critical Log verification disabled in VE.")
            return

         for i in xrange ((512*20)/32):
            if ord(CriticalLogData['GETBUFFER']['DATA'][i*32+28]):
               critical_event_count = critical_event_count + 1
            else:
               break
         objMsg.printMsg("Critical Event Count = %d" % critical_event_count, objMsg.CMessLvl.IMPORTANT)

         if critical_event_count > 0:
            CriticalEventDict = {}
            InputEventDict = {}
            try:
               if "PARAM_NAME" in self.params:
                  InputEventDict = eval(self.params["PARAM_NAME"])
                  objMsg.printMsg("Critical Event limit from State Params - %s" % InputEventDict, objMsg.CMessLvl.IMPORTANT)
               else:
                  InputEventDict = getattr(TP, 'prm_CriticalEvents', {})
                  objMsg.printMsg("Critical Event limit from TestParameters - %s" % InputEventDict, objMsg.CMessLvl.IMPORTANT)
            except:
               pass

            if InputEventDict == {}:
               ScrCmds.raiseException(11044, "No critical event dictionary limits found.")

            objMsg.printMsg('-------------------------------------------------------------------', objMsg.CMessLvl.IMPORTANT)
            objMsg.printMsg('Event #    Hr   Time Stamp  Type  Error LBA        Temp', objMsg.CMessLvl.IMPORTANT)
            objMsg.printMsg('--------- ---  ------------ ----  ----- ---------- ----', objMsg.CMessLvl.IMPORTANT)
            event_offset = 0
            data = CriticalLogData['GETBUFFER']['DATA']

            try:
               for i in xrange (1, (critical_event_count+1)):
                  event_pointer  = event_offset + 0
                  event_type     = ord(data[event_pointer])
                  event_pointer  = event_pointer + 2
                  event_hr       = self.swapBytes(data[event_pointer:event_pointer+2])
                  event_pointer  = event_pointer + 2
                  event_time     = self.swapBytes(data[event_pointer:event_pointer+4])

                  event_pointer  = event_pointer + 4
                  event_LBA      = self.swapBytes(data[event_pointer:event_pointer+4])
                  event_pointer  = event_pointer + 4
                  event_error_code  = self.swapBytes(data[event_pointer:event_pointer+4])
                  event_pointer = event_pointer + 4
                  event_temp    = ord(data[event_pointer])
                  event_offset   = event_offset + 32

                  # Critical Event accumulator, Save Critical Event to a dictionary
                  stringCE = 'CE_' + str(hex(event_type))
                  if CriticalEventDict.has_key(stringCE) == 0:
                     CriticalEventDict[stringCE] = 1
                  else:
                     CriticalEventDict[stringCE] = CriticalEventDict[stringCE] + 1

                  objMsg.printMsg('Event%3d:%4d  %12d  0x%X   0x%X  %10d %2dC' % \
                     (i, event_hr, event_time, event_type, event_error_code, event_LBA, event_temp), objMsg.CMessLvl.IMPORTANT)

                  self.dut.dblData.Tables('CRITICAL_EVENT_LOG').addRecord(
                     {
                     'EVENT_CTR' : i,
                     'ERR_CODE': str(event_type),
                     'TIMESTAMP': int(event_hr),
                     'LBA': int(event_LBA),
                     })
            except:
               objMsg.printMsg("Error in CE log parse: %s" % traceback.format_exc())

            # Error limit check
            objMsg.printMsg('--------------------------------------------------------------------', objMsg.CMessLvl.IMPORTANT)
            objMsg.printMsg("Critical Event Type: %s" % CriticalEventDict, objMsg.CMessLvl.IMPORTANT)
            objMsg.printMsg("Critical Event Limits : %s" % InputEventDict, objMsg.CMessLvl.IMPORTANT)
            for key in CriticalEventDict:
               if key in InputEventDict:
                  objMsg.printMsg('--------------------------------------------------------------------', objMsg.CMessLvl.IMPORTANT)
                  objMsg.printMsg("Critical Event Type: %s Count=%s Limit=%s" % (key, CriticalEventDict[key], InputEventDict[key]), objMsg.CMessLvl.IMPORTANT)
                  if CriticalEventDict[key] > InputEventDict[key]:
                     objMsg.printMsg("------------------- Failed Check Critical Logs --------------------------", objMsg.CMessLvl.IMPORTANT)
                     failMessage = ("Failed Critical Events Type: %s Count=%s Limit=%s" % (key, CriticalEventDict[key], InputEventDict[key]) )
                     ScrCmds.raiseException(13456, failMessage)
   #-------------------------------------------------------------------------------------------------------
   def swapBytes(self, data):
      value = 0L
      value = value | ord(data[0])
      value = value | ord(data[1]) << 8
      if len(data) > 2:
         value = value | ord(data[2]) << 16
      if len(data) > 3:
         value = value | ord(data[3]) << 24
      return value

###########################################################################################################
class CSmartDSTLong(CState):
   """
      Description: Class that will perform SMART Drive Self Test(DST).
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):

      try:
         if 'DV3' in self.dut.driveattr['CUST_TESTNAME']:
            objMsg.printMsg("Long DST DV3 already complete.")
            return
      except:
         pass

      if testSwitch.NoIO:
         objMsg.printMsg("NoIO Long DST")
         from GIO import CSPFIN2
         return CSPFIN2(self.dut, self.params).run(prm_spfin2 = [('IDT_FULL_DST_IDE', 'ON')])

      #oProcess = CProcess()
      objPwrCtrl.powerCycle(5000,12000,10,30)
      ICmd.HardReset()
      if testSwitch.FE_0144363_421106_P_TIMEOUT_SPEC_FOR_SMART_LONG_DST:
         #obtain timoeout from smart attribute table
         from CustomCfg import CCustomCfg
         Cfg = CCustomCfg()
         data = Cfg.ReadSmartAttrIO()
         poll_time = ord(data[373])
         objMsg.printMsg('Timeout returned from SMART LOG = %d minutes - Long DST polling timeout set to = %d minutes' % (poll_time, poll_time * 1.4))

         ICmd.UnlockFactoryCmds()
         ICmd.LongDST(poll_time * 80) #The unit of Time limit spec is second. 80 = 1.4 * 60
      else:
         ICmd.UnlockFactoryCmds()
         ICmd.LongDST()

      objPwrCtrl.powerCycle(5000,12000,10,30)

###########################################################################################################
class CSmartDSTShort(CState):
   """
      Description: Class that will perform SMART Drive Self Test(DST).
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):

      oProcess = CProcess()
      objPwrCtrl.powerCycle(5000,12000,10,30)
      ICmd.HardReset()
      ICmd.UnlockFactoryCmds()
      ICmd.ShortDST()

      objPwrCtrl.powerCycle(5000,12000,10,30)

###########################################################################################################
class CSDOD(CState):
   """
      Description: Class that will perform Check SDOD
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):

      self.oSerial = serialScreen.sptDiagCmds()
      startLBA, endLBA = self.oSerial.getLBARange()
      objMsg.printMsg('User LBA mode: startLBA=%X endLBA=%X' % (startLBA, endLBA))
      self.oSerial.setLBASpace(startLBA, endLBA)

      if testSwitch.M11P or testSwitch.M11P_BRING_UP:
         objMsg.printMsg("Not Supported for M11P, skip seek to LBA 0")
      else:
         if not testSwitch.NoIO:
            objPwrCtrl.powerCycle(5000,12000,10,30)
         result = ICmd.Seek(0)      # Seek to LBA 0
         if result['LLRET'] != OK:
            objMsg.printMsg('Seek cmd Failed!')
            ScrCmds.raiseException(14640, "Seek fail")

      sptCmds.enableDiags()
      self.oSerial.ShowPreAmpHeadResistance()
      self.SDOD_SerialCmd()
      objPwrCtrl.powerOff()
      objPwrCtrl.DisablePowerCycle()

   #-------------------------------------------------------------------------------------------------------
   def SDOD_SerialCmd(self):
      sdod_cmds = [('/2','2>', 0.1),
                   ('Z', '2>', 1),
                   ('U3','2>', 1),
                   ('Z', '2>', 1)]

      try:
         sdod_timeout = TP.SDOD.get('SerialTimeout',10)
      except:
         sdod_timeout = 10
      objMsg.printMsg('Serial Timeout: %s sec' %sdod_timeout)


      for cmd,resp,loopDelay in sdod_cmds:
         sptCmds.sendDiagCmd(cmd,sdod_timeout,altPattern=resp,printResult=True,loopSleepTime=loopDelay)


###########################################################################################################
###########################################################################################################
class CRandomWrite(CState):
   """
      Description: Class that will perform random read/write testing.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if getattr(TP, 'bgSTD', 0) == 1:
         return
      oProcess = CProcess()
      objPwrCtrl.powerCycle(5000,12000,10,30)
      ICmd.HardReset()
      ICmd.UnlockFactoryCmds()
      prm = TP.prm_510_RndW
      startLBA = Utility.CUtility.reverseLbaWords( prm['STARTING_LBA'] )
      loopCount = Utility.CUtility.reverseTestCylWord(prm['TOTAL_BLKS_TO_XFR'])/prm['BLKS_PER_XFR']
      maxLBA = int(ICmd.GetMaxLBA()['MAX48'],16)-1
      if DEBUG:
         objMsg.printMsg("Writing from %X to %X randomly with sector count %X; %X times" % (startLBA, maxLBA, prm['BLKS_PER_XFR'], loopCount))
      ICmd.RandomWriteDMAExt(startLBA, maxLBA, prm['BLKS_PER_XFR'], prm['BLKS_PER_XFR'], loopCount)

###########################################################################################################
class CPhysicalJumperCheck(CState):
   """
      Description: Class that will check physical jumper presence installed
                   between REQSVC and Ground on drive's PCBA.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if testSwitch.SDBP_TN_GET_JUMPER_SETTING and (not objDut.certOper) and (not self.dut.isFDE()):
         from SDBPTestNumber import CSDBPTestNumber
         sdbp = CSDBPTestNumber(self.dut)
         sdbp.enableOnlineModeRequests()
         # 0x0 when the jumper was not installed
         # 0x1 when the jumper was installed
         if sdbp.getJumperSetting():
            jumper_detect = 'SATA_JMPR_ON'
         else:
            jumper_detect = 'SATA_NO_JMPR'
         objMsg.printMsg("JUMPER_SET: %s" % jumper_detect)
         self.dut.driveattr['JUMPER_SET'] = jumper_detect
         sdbp.disableOnlineModeRequests()

      else:
         #Change to Level 1 diagnostic mode
         #Send m400d1004 command to read back I/O direction

         sptCmds.enableDiags()
         sptCmds.sendDiagCmd(CTRL_Z,altPattern='T>')
         sptCmds.sendDiagCmd('/1',altPattern='1>')
         data = sptCmds.sendDiagCmd('m400d,1004,,4',altPattern='>',printResult=True)
         sptCmds.sendDiagCmd(CTRL_Z,altPattern='1>')

         if testSwitch.virtualRun:
            return
         #Change I/O direction to input by masking Bit_5 to Zero.
         IODirection = re.split('=',data)[1].strip()
         IODirection = re.split(' ',IODirection)[0].strip()
         IODirection = string.atoi(IODirection,16)
         InpDirection = IODirection & 0xFFDF
         CmdString = 'm400d1004,,' + re.split('x',str(hex(InpDirection)))[1].strip()
         sptCmds.sendDiagCmd(CmdString,altPattern='1>',printResult=True)

         #Send m400d1050 command to read back I/O pin status
         #Below is the example of expected output:-
         '''
         Jul 16 2008-10:08:36  Result from m400d1050 cmd:
         m400d1050
         Adr 400d1050 ( 400d1050 ) = 0064  -->
         '''
         data = sptCmds.sendDiagCmd('m400d,1050,,4',altPattern='>',printResult=True)

         JumperData = re.split('=',data)[1].strip()
         JumperData = re.split(' ',JumperData)[0].strip()
         JumperData = string.atoi(JumperData,16)
         JumperData = JumperData & 0x20

         if JumperData == 32:     # check bit 5 (32==1)
            jumper_detect = 'SATA_NO_JMPR'
            objMsg.printMsg("JUMPER_SET: %s" %jumper_detect)
         elif JumperData == 0:   # check bit 5
            jumper_detect = 'SATA_JMPR_ON'
            objMsg.printMsg("JUMPER_SET: %s" %jumper_detect)

         self.dut.driveattr['JUMPER_SET'] = jumper_detect
         objPwrCtrl.powerCycle(5000,12000,10,30)
###########################################################################################################
class CSmartDefectList(CState):
   """
      Description: Class that will perform Pending and Grown Defect List analysis.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if testSwitch.WA_0124639_231166_DRIVE_SMART_NOT_SUPPORTED:
         objMsg.printMsg("SMART access disabled for this F3 based on PF3 flag WA_0124639_231166_DRIVE_SMART_NOT_SUPPORTED")
         return
      failForLimits = self.params.get('failForLimits', 1)

      from IntfClass import CInterface
      self.oIntf = CInterface()
      self.oIntf.smartEnableOper()


      smartLogDefects = {}
      smartLogDefects['PENDING'] = self.PList(failForLimits)
      smartLogDefects['GLIST']   = self.GList(failForLimits)

      smartAttrDefects = self.smartAttrDefects(failForLimits)
      return smartLogDefects, smartAttrDefects
   #-------------------------------------------------------------------------------------------------------
   def PList(self,failForLimits):
      if ( self.dut.drvIntf in TP.WWN_INF_TYPE.get('WW_SAS_ID', [] ) or self.dut.drvIntf == 'SAS' ) :
         objMsg.printMsg("Pending list retreival not active/valid for SAS-- accumulated in Glist scan.")
         return 0
      objMsg.printMsg("Retrieving Pending Defect list from Smart Log A9")
      if failForLimits:
         objMsg.printMsg(20*'-' + 'PLIST Log' + '-'*20)
         try:
            PListLimit = TP.prm_SmartDefectList.get('PLIST_LIMIT',20)
            objMsg.printMsg("PLIST limit from TestParameters - %s" % PListLimit, objMsg.CMessLvl.IMPORTANT)
         except:
            ScrCmds.raiseException(14718, "prm_SmartDefectList not found in TestParameters.py")

      #Read P-List from Log 0xA9
      PendingLogData = ICmd.SmartReadLogSec(0xA9, 1)
      objMsg.printMsg("SmartReadLogSec data: %s" % PendingLogData, objMsg.CMessLvl.IMPORTANT)
      if PendingLogData['LLRET'] != 0:
         ScrCmds.raiseException(14718, 'Failed Reading Smart Log:0xA9')
      else:
         PendingLogData['GETBUFFER'] =  ICmd.GetBuffer(2, 0, 512)

      if testSwitch.virtualRun:
         objMsg.printMsg("Interface Pending Defect List verification disabled in VE.")
         return 0

      data = PendingLogData['GETBUFFER']['DATA'][16:] #Ignore first 16bytes of data
      PListCount = 0
      for i in xrange((512-16)/16): #Defect LBA entry is every 16bytes
         PListLBA = self.SwapBytes(data[(6+i*16):(6+i*16)+4])
         PListTimeStamp = self.SwapBytes(data[(10+i*16):(10+i*16)+2])
         if PListLBA <> 0:
            PListCount = PListCount + 1
            objMsg.printMsg ("Defect LBA (%d entry) = %X; Time Stamp = %d" % (i, PListLBA, PListTimeStamp))

      if failForLimits and PListCount > PListLimit :
         objMsg.printMsg ("Failed Pending Defect List : Count=%d Limit=%d" %(PListCount,PListLimit),objMsg.CMessLvl.IMPORTANT)
         ScrCmds.raiseException(14718, 'Failed Pending Defect List')
      else:
         objMsg.printMsg ("PLIST Count = %d" % PListCount)
         self.dut.dblData.Tables('P_PENDING_DEFECT_LIST').addRecord(
            {
            'SPC_ID' : getattr(TP,"spcid_SmartDefectList",{}).get(self.dut.nextOper,self.dut.objSeq.curRegSPCID),
            'OCCURRENCE': self.dut.objSeq.getOccurrence(),
            'SEQ' : self.dut.objSeq.curSeq,
            'TEST_SEQ_EVENT': self.dut.objSeq.getTestSeqEvent(0),
            'TOTAL_DFCTS_DRIVE': PListCount
            })

      return PListCount
   #-------------------------------------------------------------------------------------------------------
   def GList(self,failForLimits):



      objMsg.printMsg("Retrieving Grown Defect list from Smart Log A8")
      if failForLimits:
         objMsg.printMsg(20*'-' + 'GLIST Log' + '-'*20)
         try:
            GListLimit = TP.prm_SmartDefectList.get('GLIST_LIMIT',20)
            objMsg.printMsg("GLIST limit from TestParameters - %s" % GListLimit, objMsg.CMessLvl.IMPORTANT)
         except:
            ScrCmds.raiseException(14719, "prm_SmartDefectList not found in TestParameters.py")

      if ( self.dut.drvIntf in TP.WWN_INF_TYPE.get('WW_SAS_ID', [] ) or self.dut.drvIntf == 'SAS' ) :
         objMsg.printMsg("Retrieving Grown Defect list from Smart Log A8")
         reassignData = ICmd.DisplayBadBlocks()
         GListCount = reassignData['NUMBER_OF_TOTALALTS']
      else:
         #Read G-List from Log 0xA8
         GrownLogData = ICmd.SmartReadLogSec(0xA8, 20)
         objMsg.printMsg("SmartReadLogSec data: %s" % GrownLogData, objMsg.CMessLvl.IMPORTANT)
         if GrownLogData['LLRET'] != 0:
            ScrCmds.raiseException(14719, 'Failed Reading Smart Log:0xA8')
         else:
            GrownLogData['GETBUFFER'] =  ICmd.GetBuffer(2, 0, 20*512)

         if testSwitch.virtualRun:
            objMsg.printMsg("Interface Grown Defect List verification disabled in VE.")
            return 0

         data = GrownLogData['GETBUFFER']['DATA'][16:] #Ignore first 16bytes of data
         GListCount = 0
         for i in xrange(((512*20)-16)/16): #Defect LBA entry is every 16bytes
            GListLBA = self.SwapBytes(data[(6+i*16):(6+i*16)+4])
            GListTimeStamp = self.SwapBytes(data[(10+i*16):(10+i*16)+2])
            if GListLBA <> 0:
               GListCount = GListCount + 1
               objMsg.printMsg ("Defect LBA (%d entry) = %X; Time Stamp = %d" % (i, GListLBA, GListTimeStamp))

      if failForLimits and GListCount > GListLimit:
         objMsg.printMsg ("Failed Grown Defect List : Count=%d Limit=%d" %(GListCount,GListLimit), objMsg.CMessLvl.IMPORTANT)
         ScrCmds.raiseException(14719, 'Failed Grown Defect List')
      else:
         objMsg.printMsg ("GLIST Count = %d" % GListCount)
         self.dut.dblData.Tables('P_GROWN_DEFECT_LIST').addRecord(
            {
            'SPC_ID' : getattr(TP,"spcid_SmartDefectList",{}).get(self.dut.nextOper,self.dut.objSeq.curRegSPCID),
            'OCCURRENCE': self.dut.objSeq.getOccurrence(),
            'SEQ' : self.dut.objSeq.curSeq,
            'TEST_SEQ_EVENT': self.dut.objSeq.getTestSeqEvent(0),
            'PBA':0,
            'RW_FLAGS':0,
            'ERR_LENGTH': GListCount
            })

      return GListCount
   #-------------------------------------------------------------------------------------------------------
   def SwapBytes(self, data):
      value = 0L
      value = value | ord(data[0])
      value = value | ord(data[1]) << 8
      if len(data) > 2:
         value = value | ord(data[2]) << 16
      if len(data) > 3:
         value = value | ord(data[3]) << 24
      return value

   def smartAttrDefects(self,failForLimits):

      if ( self.dut.drvIntf in TP.WWN_INF_TYPE.get('WW_SAS_ID', [] ) or self.dut.drvIntf == 'SAS' ) :
         smartAttrs = {'ATTRIBUTES': [0,]*512, 'WORDOFFSETS': [0,]*512}
      else:
         smartAttrs = self.oIntf.retrieiveSmartAttributes()

      smartAttrDefects = {}
      smartAttrDefects['GLIST'] = smartAttrs['ATTRIBUTES'][5]
      smartAttrDefects['PENDING'] = smartAttrs['ATTRIBUTES'][197]
      smartAttrDefects['UNCORRECT_SCTR_CNT'] = smartAttrs['ATTRIBUTES'][198]
      smartAttrDefects['SPARES_BEFORE_RESET'] = smartAttrs['WORDOFFSETS'][410]
      smartAttrDefects['PENDING_BEFORE_RESET'] = smartAttrs['WORDOFFSETS'][412]

      objMsg.printMsg('Defects in SMART ATTRIBUTE log:\n GList(5): %d\n Pending(C5): %d\n Uncorrectable Sector Count (C6): %d\n Spares Before SMART reset (410): %d\n Pending Entries Before SMART reset (412):  %d'\
            % (smartAttrDefects['GLIST'],smartAttrDefects['PENDING'],smartAttrDefects['UNCORRECT_SCTR_CNT'],smartAttrDefects['SPARES_BEFORE_RESET'],smartAttrDefects['PENDING_BEFORE_RESET']))

      return smartAttrDefects

###########################################################################################################
class CRandomWR(CState):
   """
      Description: Class that will do random write/read testing.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      oProcess = CProcess()
      objPwrCtrl.powerCycle(5000,12000,10,30)
      ICmd.HardReset()
      ICmd.UnlockFactoryCmds()
      ICmd.St(TP.prm_510_RndWR)

##################################### END Section #########################################################
###########################################################################################################
class CFailProc(CState):
   """
      Put in your fail sequence code in this class' run() method
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)

   def statePassEventHandler(self, state):
      #Can't run any exit testing
      pass
   #-------------------------------------------------------------------------------------------------------
   def DoFailProc(self):
      #
      # Fail handling code here

      if testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT:
         import CommitCls
         try:
            #if not tier and we did commit
            if ( ( not CommitServices.isTierPN(self.dut.partNum) ) and self.dut.driveattr['ORG_TIER'] == 'NONE' and ( self.dut.driveattr.get('COMMIT_DONE', "FAIL") == "PASS" or DriveAttributes.get('COMMIT_DONE', "FAIL") == 'PASS')):
               CommitCls.CAutoCommit(self.dut, {'TYPE': 'DECOMMIT'}).run()
         except:
            objMsg.printMsg("Commit error!!\n%s" % (traceback.format_exc(),))

      if testSwitch.COTTONWOOD:
         objMsg.printMsg("COTTONWOOD - skipping DoFailProc")
         return

      oProcess = CProcess()

      if testSwitch.SPLIT_BASE_SERIAL_TEST_FOR_CM_LA_REDUCTION:
         from Serial_Download import CDnldCode
      else:
         from base_SerialTest import CDnldCode

      if testSwitch.FE_0125562_405392_DISABLE_ALL_DEBUG_IF_CELL_NOT_RESPONSE:
         self.RimExceptionEvent = 0

      #Used to prevent adjacent drive fail if timeout failure occuring
      if testSwitch.FE_0118805_405392_POWER_CYCLE_AT_FAILPROC_START:
         try:
            if testSwitch.FE_0125564_405392_INIT_RIM_PRIOR_TO_POWER_CYCLE:
               #Turn off/on cell power for recovery cell
               theCell.powerOff()
               theCell.powerOn()

               #Re-Initializing Rim to restorable the cell in case of cell not respond (maybe take a long time)
               theRim.initRim()

            objPwrCtrl.powerCycle()
         except:
            if testSwitch.FE_0125562_405392_DISABLE_ALL_DEBUG_IF_CELL_NOT_RESPONSE:
               self.RimExceptionEvent = 1
               try:
                  #Turn off/on cell power for recovery cell
                  theCell.powerOff()
                  theCell.powerOn()
               except:
                  pass
            else:
               pass

      if testSwitch.FE_0125562_405392_DISABLE_ALL_DEBUG_IF_CELL_NOT_RESPONSE and self.RimExceptionEvent:
         objMsg.printMsg("***** Cell not response. Skipping all debug *****")
      else:

         #Allow for redefine if not imported by program
         TP.basePrm_IO_FailProc_504 = getattr(TP,'basePrm_IO_FailProc_504',{'test_num':504, 'prm_name': 'basePrm_IO_FailProc_504', 'timeout': 60,})

         try:
            # Grab debug data from CPC
            oProcess.St(TP.basePrm_IO_FailProc_504)
         except:
            pass


         #Display Debug information for all failure drive as per ScPk request
         if testSwitch.EnableDebugLogging:
            try:
               oSerial = serialScreen.sptDiagCmds()
               sptCmds.enableDiags()
               oSerial.dumpReassignedSectorList()
               sptCmds.gotoLevel('1')
               oSerial.getCriticalEventAttributes(30,failOnThresholdViolation=False)
               if not testSwitch.FE_0162554_336764_ENABLE_SLIP_LIST_INFO_DISP_AT_FAIL_PROC:
                  oSerial.getCriticalEventLog(30)
               else:
                  CELogData, summaryData, ceData = oSerial.getCriticalEventLog(30)
                  LBAList     = [i['LBA'] for i in ceData]                             #Get LBA List from N8 command
                  HdLBAList   = [{'hd':i['hours'],'LBA':i['LBA']} for i in ceData]     #Get hd and LBA List from N8 command
                  HdCylSummaryList = oSerial.getHdCylFromLBA(LBAList)
                  oSerial.dispSlipInfo(HdCylSummaryList)

            except:
               pass



         if testSwitch.setManufacturingStatus:
            try:
               sptCmds.enableDiags()
               try:
                  from serialScreen import sptDiagCmds
                  oSer = sptDiagCmds()
                  oSer.enableDiags()

                  try:
                     ec = self.dut.failureData[0][2]
                  except:
                     ec = self.dut.errCode

                  oSer.setCurrentManufacturingStatus(self.dut.nextOper, ec)
               except:
                  pass
            finally:
               try:
                  objPwrCtrl.powerCycle()
               except:
                  pass

         if testSwitch.FE_0154423_231166_P_ADD_POST_STATE_TEMP_MEASUREMENT:
            self.updateStateTemperature(self.dut.currentState)
      if ConfigVars[CN].get('PRODUCTION_MODE',0):
         objMsg.printMsg("self.dut.failureData[0][2] %s"%self.dut.failureData[0][2])
         if testSwitch.FE_0158563_345172_HDSTR_SP_PROCESS_ENABLE:
            if self.dut.failureData[0][2] in TP.HDTSP_Recycle_PCBA:
               objMsg.printMsg("HDSTR SP Feature turn on & drive fail EC that need to download CFW")
               try:
                  objMsg.printMsg("Power Cycle")
                  objPwrCtrl.powerCycle()
               except:
                  pass
               ClearFailSafe()
               try:  #Prevent com-check fail
                  objMsg.printMsg("Download CFW before raise fail!!!")
                  objProc = CProcess()
                  objProc.dnldCode(codeType='CFW', timeout =300)
               except:
                  try:
                     mode = self.dut.sptActive.getMode()
                     #self.dut.sptActive.setMode(mode)
                     objMsg.printMsg("Run serial port mode to retry download CFW")
                     objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
                     objProc.dnldCode(codeType='UNLK', timeout =300)
                     objProc.dnldCode(codeType='CFW', timeout =300)
                  except:
                     objMsg.printMsg("Download CFW uncomplete")
                     pass
               SetFailSafe()

      objMsg.printDblogBin(self.dut.dblData.Tables('P_TIME_TO_READY'), spcId32 = 1)
      # Check IOEDC failure

      iddis_PN_list =ConfigVars[CN].get('IDDIS_PN',[])
      if testSwitch.AutoFAEnabled and not (testSwitch.AutoFA_IDDIS_Enabled and \
           (self.dut.driveattr['PART_NUM'] in iddis_PN_list \
           or self.dut.driveattr['PART_NUM'][0:3] in iddis_PN_list or 'ALL' in iddis_PN_list)):
         try:
            from AUTOFA import *
            try:
               errorcode = int(self.dut.failureData[0][2])
            except:
               errorcode = int(self.dut.errCode)
            objMsg.printMsg('<<< POTENTIAL FAIL CAUSE ANALYSIS FOR EC %s START >>>' % errorcode)
            objFA = CAutoFA(self.dut)
            objFA.run(errorcode)
            objMsg.printMsg('<<< POTENTIAL FAIL CAUSE ANALYSIS FOR EC %s COMPLETE>>>'% errorcode)

         except:
            objMsg.printMsg("INIT FA DEBUG: %s" % traceback.format_exc())
      elif type(self.dut.failureData) == types.TupleType and len(self.dut.failureData) != 0 and self.dut.failureData[0][2] not in [11098]:
         from Exceptions import CRaiseException
         try:
            objPwrCtrl.powerCycle()
            CIOEDCCheck(self.dut, {}).run()
         except CRaiseException,exceptionData:
            if exceptionData[0][2] in [11098]:
               self.dut.failureData = exceptionData.args
         except Exception, e:
            pass

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      ###### Warning - any exception here may cause drive to pass ######
      objMsg.printMsg('<<< Test failure Handling >>>')
      SetFailSafe()

      try:
         self.DoFailProc()
      except:
         objMsg.printMsg("DoFailProc Exception %s" % traceback.format_exc())

      #
      ClearFailSafe()
      #
      # throw an exception next
      #
      self.exitStateMachine() # this will throw exception to be handled by top level code in Setup.py

###########################################################################################################
###########################################################################################################
class CEndTesting(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   def statePassEventHandler(self, state):
      #Can't run any exit testing
      pass

   def statePreExecuteEventHandler(self, state):
      #Update the temp prior to running state
      if testSwitch.FE_0154423_231166_P_ADD_POST_STATE_TEMP_MEASUREMENT:
         self.updateStateTemperature(state)

   #-------------------------------------------------------------------------------------------------------
   def run(self):

      if testSwitch.FE_0163145_470833_P_NEPTUNE_SUPPORT_PROC_CTRL20_21:
         cellTemp = ReportTemperature()/10.0
         self.dut.updateCellTemp(cellTemp)
         objMsg.printMsg("CEndTesting: Current cell temperature is "+str(cellTemp)+"C.", objMsg.CMessLvl.IMPORTANT)

      objMsg.printDblogBin(self.dut.dblData.Tables('P_TIME_TO_READY'), spcId32 = 1)

      if testSwitch.operationLoop == 1:
         objMsg.printMsg("Loop Limit: %d" % testSwitch.operationLoopLimit)
         try:
            self.dut.operationLoopCounter += 1
         except:
            self.dut.operationLoopCounter = 1
         objMsg.printMsg("Loop iteration %d" % self.dut.operationLoopCounter)
         if self.dut.operationLoopCounter > testSwitch.operationLoopLimit:
            ScrCmds.raiseException(11044,"Operation Loop Limit Exceeded")

      if testSwitch.setManufacturingStatus: # BLM -F3 issue- this call was zeroing out the CAP block
         if not objRimType.IOInitRiser():
            try:
               objPwrCtrl.powerCycle()            # Note this will force power on
               from serialScreen import sptDiagCmds
               oSer = sptDiagCmds()
               sptCmds.enableDiags()
               oSer.setCurrentManufacturingStatus(self.dut.nextOper, self.dut.errCode)
            except:
               pass
            objPwrCtrl.powerCycle()

      if testSwitch.FE_0121834_231166_PROC_TCG_SUPPORT and not testSwitch.PROC_TCG_SKIP_END_TESTING:
         oIdentifyDevice = CIdentifyDevice()
         if oIdentifyDevice.Is_FDE():
            if not oIdentifyDevice.Is_SeaCosFDE():
               # TCG drive not KWAI

               from TCG import CTCGPrepTest, SetUseState, LifeStates, LifeStatesLookup
               oTCG = CTCGPrepTest(self.dut)
               if ( self.dut.drvIntf in TP.WWN_INF_TYPE.get('WW_SAS_ID', []) or self.dut.drvIntf == 'SAS' ) :
                  # SAS doesn't have SOM state but runs most of the process in MFG state- ship in USE state
                  if self.dut.nextOper == 'CUT2':
                     oProcess = CProcess()
                     objMsg.printMsg("Running test 577 - Verification of credentials - Change to USE state - FIS's PSID")
                     oProcess.St(SetUseState,timeout=3600)
               else:
                  try:
                     oTCG.CheckFDEState()
                     if LifeStatesLookup.get(self.dut.LifeState, 'INVALID') == 'USE':
                        oTCG.ResetSOMState()
                        oTCG.unlockFwDlPortOnReset()
                        oTCG.GetSOMState()
                  finally:
                     if testSwitch.BF_0180787_231166_P_REMOVE_FDE_CALLBACKS_FOR_CHECKFDE:
                        oTCG.RemoveCallback()

      if self.dut.nextOper == "CUT2" and testSwitch.auditTest:
         ScrCmds.raiseException(14827, "Audit test passer. Not a shippable drive config.")

###########################################################################################################
###########################################################################################################
#----------------------------------------------------------------------------------------------------------
# Class CReadWWN -  Handles WWN Readback and validate functions
#----------------------------------------------------------------------------------------------------------
class CReadWWN(CState):
   """
   Handles WWN Readback and validate functions
   """
   def __init__(self, dut, params={}):
      self.params   = params
      depList       = []
      self.dut      = dut
      CState.__init__(self, dut, depList)

   def run(self):
      from FSO import WorldWideName
      if not testSwitch.virtualRun:
         self.hdd = CIdentifyDevice(refreshBuffer=False, force=False).ID     # get drive params
         self.wwn  = self.hdd['IDWorldWideName']       # sata_id
      else:
         self.wwn = DriveAttributes.get('WW_SATA_ID', '5000C50011EBF574')

      WorldWideName().verify(self.wwn)              # validate wwn

###########################################################################################################
class CWRVerify(CState):
   """
      Handle Write Read Verify for full write and/or full read removal
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):

      if self.dut.skipWRVerify: #if we do LongDST in S_PARITY_CHK state, skip WRVerify
         objMsg.printMsg("Skipped WR_VERIFY state, LongDST run in S_PARITY_CHK state")
         return

      try:
         objMsg.printMsg("start CWRVerify")
         self.runme()      # normal CWRVerify
         objMsg.printMsg("end CWRVerify")
      except:
         objMsg.printMsg("CWRVerify exception: %s" % (traceback.format_exc(),))
         if testSwitch.SP_RETRY_WORKAROUND and testSwitch.NoIO:

            try:
               self.dut.driveattr['PROC_CTRL12'] = str(int(self.dut.driveattr['PROC_CTRL12']) + 1)
            except:
               self.dut.driveattr['PROC_CTRL12'] = 1

            objMsg.printMsg("PROC_CTRL12=%s" % self.dut.driveattr['PROC_CTRL12'])

            rlist = -1
            try:
               oSerial = serialScreen.sptDiagCmds()
               oSerial.quickDiag()
               reassignData = oSerial.dumpReassignedSectorList()
               objMsg.printMsg("reassignData data: %s" % (reassignData))
               rlist = reassignData['NUMBER_OF_TOTALALTS']
            except:
               objMsg.printMsg("reassignData exception: %s" % (traceback.format_exc(),))

            #if rlist > 0:
            #   raise

            objMsg.printMsg("Retrying Long DST")
            from GIO import CSPFIN2
            if self.dut.BG in ['SBS']: # Workaround for EDAC issue. Pending new F3 code to fix this problem
               CSPFIN2(self.dut, self.params).run(prm_spfin2 = [('IDT_FULL_DST_IDE', 'ON', {'NUM_RETRY':1})])
            else:
               CSPFIN2(self.dut, self.params).run(prm_spfin2 = [('IDT_FULL_DST_IDE', 'ON')])            
         else:
            raise

   #-------------------------------------------------------------------------------------------------------
   def runme(self):
      try:
         self.SerialTruputRW()
      except:
         objMsg.printMsg("SP Data loss suspected. Doing retry. SerialTruputRW exception: %s" % (traceback.format_exc(),))
         self.SerialTruputRW()

      stepLBA     = 1024
      sec_count   = 1024
      stampFlag   = 0
      compareFlag = self.params.get('COMPARE_FLAG',0) #default is 0    ***
      writepattern = '\x00'
      self.extraSec = self.params.get('EXTRA_SEC',2000)    #default is 2000
      self.RWDictWrite = []
      self.RWDictRead = []
      EC = 14737

      if len(TP.RWDictGlobal) == 0 and not testSwitch.CPCWriteReadRemoval:
         objMsg.printMsg('len of TP.RWDictGlobal is ZERO, return')
         return

      objPwrCtrl.powerCycle()
      ret = CIdentifyDevice(force = False).ID
      self.maxLBA = ret['IDDefaultLBAs'] -1
      if ret['IDCommandSet5'] & 0x400:
         self.maxLBA = ret['IDDefault48bitLBAs'] -1

      if testSwitch.IOWriteReadRemoval:
         objMsg.printMsg('*** WR_VERIFY - IO Tracking ***')

      if testSwitch.CPCWriteReadRemoval:
         objMsg.printMsg('*** WR_VERIFY - CPC Tracking ***')

         if len(self.dut.TrackingList):

            zoneSize = (self.dut.numLba+1) / self.dut.numTrackingZone
            objMsg.printMsg('Size of zone = %s' % zoneSize)
            objMsg.printMsg('numLBA = %d numTrackingZone = %d'% (self.dut.numLba,self.dut.numTrackingZone))
            objMsg.printMsg('Tracking List = %s' % self.dut.TrackingList)

            tempTrackingList = re.split(',',self.dut.TrackingList)
            objMsg.printMsg('tempTrackingList after split = %s' % tempTrackingList)
            tempTrackingList.sort()
            objMsg.printMsg('tempTrackingList after sort = %s' % tempTrackingList)
            tempZoneWritten = set(tempTrackingList)
            objMsg.printMsg('tempZoneWritten = %s' % tempZoneWritten)

            # sort again after set
            newTrackingList = []
            for abc in tempZoneWritten:
               objMsg.printMsg('abc = %s' % abc)
               if len(abc) == 0 :
                  continue
               tempabc = int(abc,10)
               newTrackingList.append(tempabc)

            objMsg.printMsg('newTrackingList = %s' % newTrackingList)
            newTrackingList.sort()
            objMsg.printMsg('tempTrackingList after sort = %s' % newTrackingList)

            for tempZone in newTrackingList:
               objMsg.printMsg('tempZone = %s' % tempZone)

               tempstartLBA= tempZone * zoneSize
               tempendLBA= (tempZone+1) * zoneSize -1

               if tempZone+1 == self.dut.numTrackingZone:
                  tempendLBA = self.maxLBA

               RWDict = []
               RWDict.append ('Write')
               RWDict.append (tempstartLBA)
               RWDict.append (tempendLBA)
               RWDict.append (tempZone)
               objMsg.printMsg('WR_VERIFY appended - %s' % (RWDict))
               TP.RWDictGlobal.append (RWDict)

         else:
            objMsg.printMsg('len(self.dut.TrackingList) = 0, no need to add dict from CPC tracking')

      if len(TP.RWDictGlobal) == 0:
         objMsg.printMsg('len of TP.RWDictGlobal is ZERO, return')
         return

      else:
         self.sortLBA()

         ICmd.MakeAlternateBuffer(BWR, sec_count)
         ICmd.ClearBinBuff(BWR)

         if (not len(self.RWDictWrite)==0) and self.params.get('WRITE',0):  #default is read(0) only ***
            i=0
            for RWDictTemp in self.RWDictWrite:
               objMsg.printMsg('%s) SequentialWriteDMAExt - StartLBA= %s, EndLBA= %s' % (i,RWDictTemp[1],RWDictTemp[2]))
               data = ICmd.SequentialWriteDMAExt(RWDictTemp[1], RWDictTemp[2], stepLBA, sec_count, stampFlag, compareFlag)
               result = data['LLRET']
               if result != OK:
                  objMsg.printMsg('%s SequentialWriteDMAExt Failed, data = %s' % (RWDictTemp[3],data))
                  ScrCmds.raiseException(EC,"CWRVerify: SequentialWriteDMAExt Failed")
               i=i+1
         i=0
         for RWDictTemp in self.RWDictRead:
            objMsg.printMsg('%s) SequentialReadDMAExt - StartLBA= %s, EndLBA= %s' % (i,RWDictTemp[1],RWDictTemp[2]))
            data = ICmd.SequentialReadDMAExt(RWDictTemp[1], RWDictTemp[2], stepLBA, sec_count, stampFlag, compareFlag)
            result = data['LLRET']
            if result != OK:
               objMsg.printMsg('%s SequentialReadDMAExt Failed, data = %s' % (RWDictTemp[3],data))
               ScrCmds.raiseException(EC,"CWRVerify: SequentialReadDMAExt Failed")
            i=i+1

         ICmd.RestorePrimaryBuffer(BWR)

      objMsg.printMsg('*** WR_VERIFY - Tracking Done ***')

   def SerialTruputRW(self):

      if testSwitch.NoIO:
         objMsg.printMsg("SP_WR_THRUPUT test range is already appended during SP_WR_THRUPUT state.")
         return

      try:
         if testSwitch.NoIO and not testSwitch.SMRPRODUCT:
            oXFRTest = CZoneXferTest(self.dut, {'XFER_TYPE': "TP.prm_sp_wr_truput"})
            oXFRTest.WR_AddDict('P598_ZONE_XFER_RATE')
            return
      except:
         objMsg.printMsg("Missing P598_ZONE_XFER_RATE LBA data. Warning: %s" % (traceback.format_exc(),))

      try:
         RWOper = TP.RWSerialTruputOper
      except:
         RWOper = 'FIN2'

      if self.dut.nextOper == RWOper or testSwitch.NoIO:
         try:
            from base_RssScreens import CSerial_Truput
            oTruput = CSerial_Truput(self.dut, self.params)
            oTruput.FullReadRemoval = True
            oTruput.run()

            for i in oTruput.TruputLst:
               RWDict = []
               RWDict.append ('Read')
               RWDict.append (int(i['StartLBA'], 16))
               RWDict.append (int(i['EndLBA'], 16) )
               RWDict.append ('CSerial_Truput')
               objMsg.printMsg('CSerial_Truput WR_VERIFY appended - %s' % (RWDict))
               TP.RWDictGlobal.append (RWDict)

         except:
            ScrCmds.raiseException(10345,"Fail running CSerial_Truput. Traceback=%s" % traceback.format_exc())

   def sortLBA(self):

      i=0
      self.RWDictWrite = []
      self.RWDictRead  = []

      objMsg.printMsg('sortLBA: Original')
      for RWDictTemp in TP.RWDictGlobal:
         objMsg.printMsg('%s) - %s' % (i,RWDictTemp))
         i=i+1

      for RWDictTemp in TP.RWDictGlobal:
         if RWDictTemp[0] == "Write":
            self.RWDictWrite.append (RWDictTemp)

      for RWDictTemp in self.RWDictWrite:
         objMsg.printMsg('Write: Before sort - %s' % (RWDictTemp))

      self.sortRange(mode="Write")

      for RWDictTemp in self.RWDictWrite:
         objMsg.printMsg('Write: After sort - %s' % (RWDictTemp))
         self.RWDictRead.append (RWDictTemp)    #For write, need to do read too.

      for RWDictTemp in TP.RWDictGlobal:
         if RWDictTemp[0] == "Read":
            self.RWDictRead.append (RWDictTemp)

      for RWDictTemp in self.RWDictRead:
         startLBA = RWDictTemp[1] - self.extraSec
         endLBA = RWDictTemp[2] + self.extraSec

         if startLBA < 0:
            startLBA = 0

         if endLBA > self.maxLBA :
            endLBA = self.maxLBA

         RWDictTemp[1] = startLBA
         RWDictTemp[2] = endLBA

      for RWDictTemp in self.RWDictRead:
         objMsg.printMsg('Read: Before sort - %s' % (RWDictTemp))

      self.sortRange(mode="Read")

      for RWDictTemp in self.RWDictRead:
         objMsg.printMsg('Read: After sort - %s' % (RWDictTemp))

   def sortRange(self, mode="Write"):

      if mode == "Write":
         RWDict = self.RWDictWrite
      else:
         RWDict = self.RWDictRead

      RWDictNew = []
      for RWDictTemp in RWDict:

         if len(RWDictNew) == 0:
            RWDictNew.append (RWDictTemp)
         else:
            found = 0
            for newRWDictTemp in RWDictNew:
               if (RWDictTemp[1] > newRWDictTemp[2]) or (RWDictTemp[2] < newRWDictTemp[1]) : # no overlapping at all
                  continue

               elif (RWDictTemp[1] >= newRWDictTemp[1]) and (RWDictTemp[2] <= newRWDictTemp[2]) : #Within range
                  found = found + 1
                  break

               elif (RWDictTemp[1] >= newRWDictTemp[1]) and (RWDictTemp[2] >= newRWDictTemp[2]) : #Higher LBA
                  if RWDictTemp[2] > newRWDictTemp[2]:
                     newRWDictTemp[2] = RWDictTemp[2]    #endLBA extended
                     found = found + 1
                     break

               elif (RWDictTemp[1] <= newRWDictTemp[1]) and (RWDictTemp[2] <= newRWDictTemp[2]) :  #Smaller startLBA
                  if RWDictTemp[1] < newRWDictTemp[1]:
                     newRWDictTemp[1] = RWDictTemp[1]    #startLBA shorten

                     found = found + 1
                     break

               elif (RWDictTemp[1] < newRWDictTemp[1]) and (RWDictTemp[2] > newRWDictTemp[2]) :    #Bigger range
                  newRWDictTemp[1] = RWDictTemp[1]
                  newRWDictTemp[2] = RWDictTemp[2]
                  found = found + 1
                  break

            if not found:
               RWDictNew.append (RWDictTemp)

      if mode == "Write":
         self.RWDictWrite = RWDictNew
      else:
         self.RWDictRead = RWDictNew

###########################################################################################################
class CDisableUDR2(CState):
   """
      Description: Class that will disable UDR2 (Unwritten Drive Recovery)
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self, EnableUDR2 = True):
      CEnableUDR2(self.dut).run(EnableUDR2 = False)

###########################################################################################################
class CEnableUDR2(CState):
   """
      Description: Class that will enable UDR2 (Unwritten Drive Recovery)
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self, EnableUDR2 = True):

      self.oSerial = serialScreen.sptDiagCmds()
      if testSwitch.SDBP_TN_GET_UDR2 and (not objDut.certOper) and (not self.dut.IdDevice.has_key('FDE')):
         self.runudr2_tn(EnableUDR2)
      else:
         self.runudr2(EnableUDR2)
         theCell.enableESlip(sendESLIPCmd = True)

   #-------------------------------------------------------------------------------------------------------
   # To run UDR2 using SDBP test numbers. Eventually, all SP diagnostic
   # commands will be converted into SDBP test numbers.
   def runudr2_tn(self, EnableUDR2 = True):

      from SDBPTestNumber import CSDBPTestNumber
      sdbp = CSDBPTestNumber(self.dut)
      sdbp.enableOnlineModeRequests()
      udrStatus = sdbp.getUDRStatus()
      sdbp.disableOnlineModeRequests()

      udrDict = {0x00:None, 0x01:False, 0x02:True}
      IsUDR2 = udrDict[udrStatus]
      objMsg.printMsg("Drive IsUDR2 = %s EnableUDR2 = %s" % (IsUDR2, EnableUDR2))

      if IsUDR2 == None:
         objMsg.printMsg("UDR2 not supported")
         return
      # Enable the UDR2
      if EnableUDR2 == True:  # this is called at end of test
         self.enableUDR()
      # Disable UDR2
      else:                   # this is called at start of test
         self.disableUDR(IsUDR2)

      # Read back UDR status
      sdbp.enableOnlineModeRequests()
      udrStatus = sdbp.getUDRStatus()
      sdbp.disableOnlineModeRequests()
      IsUDR2 = udrDict[udrStatus]

      self.verifyUDR(IsUDR2, EnableUDR2)

   #-------------------------------------------------------------------------------------------------------
   def runudr2(self, EnableUDR2 = True):

      IsUDR2 = self.oSerial.GetUDR2(getCTRL_L = True)
      objMsg.printMsg("Drive IsUDR2 = %s EnableUDR2 = %s" % (IsUDR2, EnableUDR2))
      if IsUDR2 == None:
         objMsg.printMsg("UDR2 not supported")
         return

      # Enable the UDR2
      elif EnableUDR2 == True:  # this is called at end of test
         self.enableUDR()
         self.oSerial.GetCtrl_L(force=True)  # refresh CTRL_L data
      # Disable UDR2
      else:                   # this is called at start of test
         self.disableUDR(IsUDR2)

      IsUDR2 = self.oSerial.GetUDR2(getCTRL_L = True)
      self.verifyUDR(IsUDR2, EnableUDR2)


   #-------------------------------------------------------------------------------------------------------
   def PIF_UDR(self):
      PIFUdr = None
      try:
         import PIF
         from PIFHandler import CPIFHandler
         PIFHandler = CPIFHandler()
         dPNum = PIFHandler.getPnumInfo(sPnum=self.dut.partNum, dPNumInfo=PIF.dPNumInfo, GetAll=True)
         objMsg.printMsg('GetUDR2 dPNum=%s' % dPNum)
         for iter1 in dPNum['AllLst']:
            if iter1.has_key('ProcessControl'):
               for iter2 in iter1['ProcessControl']:
                  if iter2.has_key('UDR2DISABLE'):
                     PIFUdr = iter2['UDR2DISABLE']
                     break
               break
         msg = 'PIFUdr=%s' % PIFUdr
         if PIFUdr == True:
            msg = msg + " ******* UDR2 SETTING IS OVERWRITTEN BY dPNum {ProcessControl}**********"
         objMsg.printMsg(msg)
      except:
         PIFUdr = None
      return PIFUdr

   def enableUDR(self):
      """ Enable UDR2 """
      pif_udr = self.PIF_UDR()

      self.oSerial = serialScreen.sptDiagCmds()
      self.oSerial.enableDiags()

      if pif_udr == None:
         poh = self.oSerial.GetLTTCPowerOnHours() # if poh == 0, UDR2 is disabled
         pif_udr = not bool(poh)
         objMsg.printMsg("Drive LTTCPowerOnHours=%s New pif_udr=%s" % (poh, pif_udr))

      if pif_udr == True:
         objMsg.printMsg("PIF_UDR True. Drive UDR2 disabled")
         self.oSerial.PChar(CTRL_T)
         return

      smartParams1 = {
         'options'                  : [1, 0x23],
         'initFastFlushMediaCache'  : 0,
         'timeout'                  : 60,
         }
      self.oSerial.SmartCmd(smartParams1, dumpDEBUGResponses = 0)

      # Let base_Initiator_CMD handle the switching
      #if objRimType.IOInitRiser():
      #   theRim.EnableInitiatorCommunication(objComMode)
      if objRimType.CPCRiser():
         self.oSerial.PChar(CTRL_T)

   def disableUDR(self, IsUDR2=False):
      """ Disables UDR2 """
      if IsUDR2 == False:
         return

      # Rev >= 0015.0001 supports 1>N24 to disable UDR2
      sptCmds.enableDiags()
      cmdDict = self.oSerial.getCommandVersion('1', 'N')
      objMsg.printMsg('1>N rev=%s' % repr(cmdDict))

      try:
         CmdRev = (cmdDict['majorRev'] * 10000) + cmdDict['minorRev']
      except:
         CmdRev = 0
      if CmdRev >= 150001 or testSwitch.virtualRun:
         smartParams1 = {
            'options'                  : [0x24],
            'initFastFlushMediaCache'  : 0,
            'timeout'                  : 60,
            }
         self.oSerial.SmartCmd(smartParams1, dumpDEBUGResponses = 0)
      else:
         theCell.enableESlip(sendESLIPCmd = True)
         res = ICmd.ReadLong(0)
         if res['LLRET'] != OK:
            ScrCmds.raiseException(14845, "Fail UDR2 ReadLong")
         ICmd.BufferCopy(1, 0, 2, 0, 512) # Copy to write buff (offset 0) from read buff (offset 0), total 512 bytes
         res = ICmd.WriteLong(0)
         if res['LLRET'] != OK:
            ScrCmds.raiseException(14845, "Fail UDR2 WriteLong")

   def verifyUDR(self, IsUDR2, EnableUDR2):
      """ Verify UDR status if changed correctly """
      objMsg.printMsg("Drive IsUDR2 = %s" % IsUDR2)
      if IsUDR2 != EnableUDR2:
         msg = "C_UDR2 Fail IsUDR2 = %s EnableUDR2 = %s" % (IsUDR2, EnableUDR2)
         if testSwitch.virtualRun:
            objMsg.printMsg(msg)
         else:
            ScrCmds.raiseException(14845, msg)

###########################################################################################################
class CDisableMC(CState):
   """
      Description: Class that will disable media cache
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      oSerial = serialScreen.sptDiagCmds()
      mc = oSerial.Get_MCStatus() #Use serial cmd
      objMsg.printMsg("mc status: %s" % mc)
      if mc == True:
         objPwrCtrl.powerCycle()
         from IntfClass import CInterface
         CInterface().DoMediaCache(action = 'disable')

         if oSerial.Get_MCStatus('disable') != False:
            ScrCmds.raiseException(14842, "Fail to disable Media Cache")
      elif mc == False:
         objMsg.printMsg("Media cache already disabled")
      else:
         objMsg.printMsg("Media cache not supported")


###########################################################################################################
class CEnableMC(CState):
   """
      Description: Class that will enable media cache
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      oSerial = serialScreen.sptDiagCmds()
      mc = oSerial.Get_MCStatus() #Use serial cmd
      objMsg.printMsg("mc status: %s" % mc)
      if mc == False:
         objPwrCtrl.powerCycle()
         if testSwitch.NoIO:
            oSerial.enableMC()
         else:
            from IntfClass import CInterface
            oIntf = CInterface()
            oIntf.DoMediaCache(action = 'enable')

         if oSerial.Get_MCStatus('enable') != True:
            if testSwitch.virtualRun:
               objMsg.printMsg('VE - Fail to enable Media Cache')
            else:
               ScrCmds.raiseException(14842, "Fail to enable Media Cache")

         self.init_mc()
      elif mc == True:
         objMsg.printMsg("Media cache already enabled")
         theCell.disableESlip()
         self.init_mc()
      else:
         objMsg.printMsg("Media cache not supported")

   #-------------------------------------------------------------------------------------------------------
   def init_mc(self):
      if testSwitch.NoIO:
         oSerial = serialScreen.sptDiagCmds()
         oSerial.enableDiags()
         if not oSerial.IsMCClean():
            if ConfigVars[CN].get('MC_INIT_FIX', 0) == 0:
               ScrCmds.raiseException(14875, "Media cache is not empty.")
            else:
               # Note: C>U2 command is not SMR safe
               oSerial.initMCCache()
               import GIO
               # write pass drive, until C>U2 command is SMR safe
               objMsg.printMsg("write pass drive, since C>U2 may cause UDE if there is data in MC")
               GIO.CWriteDriveZero(self.dut, params={}).doWriteZeroPatt('FIN2', 'MaxLBA')
               #Call LongDST, any write pass will need a LongDST
               GIO.CSmartDST_SPT(self.dut, params={}).DSTTest_IDE('INIT_MC', 'Long')
      else:
         objPwrCtrl.powerCycle()
         from IntfClass import CInterface
         oIntf = CInterface()
         oIntf.DoMediaCache(action = 'init')

      objMsg.printMsg("Media cache initialized")



###########################################################################################################
class CClearEpc(CState):
   """
      Class that will insure EPC is supported and all power conditions timers disabled
      Input parameters:
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      params.setdefault('startup',1)
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      oProcess = CProcess()

      if self.params['startup']:
         objPwrCtrl.powerCycle(5000,12000,10,30)
      ICmd.HardReset()
      result = ICmd.SetFeatures(0x0C,0xFF,0x50)['LLRET']
      objMsg.printMsg("SetFeatures - Restore Power Condition Settings = %s" % str(result))
      if result != OK:
         objMsg.printMsg('SetFeatures - Restore Power Condition Settings - FAILED')
      else:
         objMsg.printMsg('SetFeatures - Restore Power Condition Settings - PASSED')

      result = ICmd.SetFeatures(0x0C,0xFF,0x13)['LLRET']
      objMsg.printMsg("SetFeatures - Set Power Condition State = %s" % str(result))
      if result != OK:
         objMsg.printMsg('SetFeatures - Set Power Condition State - FAILED')
      else:
         objMsg.printMsg('SetFeatures - Set Power Condition State - PASSED')

###########################################################################################################
class CEnaFAFH(CState):
   """
      Description: Class that will enabke FAFH (data collection mode, must b blk pt RW4A onwards)
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      import serialScreen, sptCmds
      SupportFAFH = serialScreen.sptDiagCmds().GetFAFHStatus()
      if 1: #SupportFAFH:
         objMsg.printMsg("FAFH Supported %s" % SupportFAFH)
         timeoutbyhd = self.dut.imaxHead * 100
         objPwrCtrl.powerCycle()
         time.sleep(10) # additional delay for FAFH
         serialScreen.sptDiagCmds().enableDiags()
         serialScreen.sptDiagCmds().gotoLevel('H')
         sptCmds.sendDiagCmd("f6,8002,5",timeout = timeoutbyhd, printResult = True, loopSleepTime=0.5)   # enable fafh trigger
         #self.oSerial.gotoLevel('H')
         #sptCmds.sendDiagCmd("f6,2,1B,0,D",timeout = timeoutbyhd, printResult = True, loopSleepTime=0.5) #enable clr compensation
         #if testSwitch.FE_0246774_009408_DIS_HD_RES_MEAS_BY_FAFH_ST_MACH:
         #self.oSerial.gotoLevel('H')
         #sptCmds.sendDiagCmd("f6,2,1f",timeout = timeoutbyhd, printResult = True, loopSleepTime=0.5)
         sptCmds.enableESLIP()
      else:
         objMsg.printMsg("FAFH not enabled!")
###################################################################################
class CClearMiniCert(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      params.setdefault('startup',1)
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      oProcess = CProcess()
      objMsg.printMsg('Dump and clear mini cert log')
      if self.params['startup']:
         objPwrCtrl.powerCycle(5000,12000,10,30)
         sptCmds.enableDiags()

      sptCmds.gotoLevel('T')
      sptCmds.sendDiagCmd('V200',printResult = True)
      sptCmds.sendDiagCmd('i200,1,22',printResult = True)

      if self.params['startup']:
         objPwrCtrl.powerCycle()

if testSwitch.FE_0134083_231166_UPDATE_SMART_AND_UDS_INIT:
   ###################################################################################
   ###################################################################################
   class Clear_UDS(CState):
      """
      This is a platform based test function for clearing the SMART and UDS counters prior to
      drive shipment to the customer.

      ** Should be placed BEFORE ClearSmart call **
      """

      #-------------------------------------------------------------------------------------------------------
      def __init__(self, dut, params={}):
         self.params = params
         depList = []
         CState.__init__(self, dut, depList)
         self.dut = dut
      #-------------------------------------------------------------------------------------------------------
      def run(self):
         ICmd.ClearUDS()
   ###################################################################################
   ###################################################################################

###################################################################################
###################################################################################
class CVGATest(CState):
   """
      Perform VGA test per VGA param that was specified in Statetable
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut

   #-------------------------------------------------------------------------------------------------------
   def run(self):

      oProcess = CProcess()
      ICmd.HardReset()
      ICmd.UnlockFactoryCmds()
      oProcess.St(eval(self.params["VGA_PARAM"]))    # VGA test - PRE or POST
      objPwrCtrl.powerCycle(5000,12000,10,30)

      #Delta VGA screening for reliability improvement on Head related portion
      if self.params.get('VGA_SCRN',0):
         if 'ALL' in TP.VGA_SCRN_PN or self.dut.partNum in TP.VGA_SCRN_PN:
            delta_hd = [0 for i in range(self.dut.imaxHead)]
            fail_hd = '0'*self.dut.imaxHead
            objMsg.printMsg("The default value of head is %s" % fail_hd)
            headFail = 0
            tbl = self.dut.dblData.Tables('P707_ADAPGAIN_COMP').tableDataObj()
            for i in range(len(tbl)):
               idx = int(tbl[i]['HD_PHYS_PSN'])
               delta_hd[idx] = int(tbl[i]['DELTA'])

            for hd in range(len(delta_hd)):
               if delta_hd[hd] < -50:
                  headFail = 1
                  fail_hd = fail_hd[0:hd] + '1' + fail_hd[hd+1:]
                  objMsg.printMsg("The delta value of head %s is %s" %(hd,delta_hd[hd]))

            if headFail == 1:
               self.dut.driveattr['VGA_FAIL_HEAD'] = fail_hd
               ScrCmds.raiseException(16511, 'The delta value less than -50')

###################################################################################
###################################################################################
class CClearMCCache(CState):
   """
      Waits until MCCache is cleared
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)


   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if not testSwitch.extern.FE_0116076_355860_MEDIA_CACHE:
         if testSwitch.FE_0154003_231166_P_ALLOW_BYPASS_MC_CMDS_BASED_F3_FLAG and not testSwitch.virtualRun:
            objMsg.printMsg("FE_0116076_355860_MEDIA_CACHE in F3 is disabled... bypassing state")
            return
         else:
            objMsg.printMsg("FE_0116076_355860_MEDIA_CACHE not detected but FE_0154003_231166_P_ALLOW_BYPASS_MC_CMDS_BASED_F3_FLAG is false- running state.")

      MCCount = 99999999

      objPwrCtrl.powerCycle(baudRate = Baud38400)
      sCmds = serialScreen.sptDiagCmds()
      sleepTimes = [180, 60, 30, 30, 30]
      startTime = time.time()
      idx = 0
      while MCCount > 0:
         time.sleep(sleepTimes[idx])
         idx += 1
         if idx == len(sleepTimes):
            idx = len(sleepTimes)-1


         sptCmds.enableDiags()
         MCCount = sCmds.getMCCacheCount()
         if testSwitch.virtualRun and idx == len(sleepTimes)-1:
            MCCount = 0
         sptCmds.enableOnlineMode()

         if (time.time() - startTime) > 1800:
            ScrCmds.raiseException(42216, "Unable to clear media cache in 1800 seconds")

      objPwrCtrl.powerCycle()

###################################################################################
class CClearUds(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      params.setdefault('startup',1)
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      oProcess = CProcess()
      if self.params['startup']:
         objPwrCtrl.powerCycle(5000,12000,10,30)
      if objRimType.isIoRiser() and not testSwitch.NoIO :
         ICmd.HardReset()
         objMsg.printMsg('Clear UDS via Interface')
         oProcess.St(TP.prm_638_Unlock_Seagate)   # Unlock Seagate Access
         oProcess.St(TP.prm_556_SmartFunction,CTRL_WORD1=(0x0A),)  # Return current sram smart frame
         oProcess.St(TP.prm_556_SmartFunction,CTRL_WORD1=(0x0F),)  # Initialize UDS & SMART
         oProcess.St(TP.prm_556_SmartFunction,CTRL_WORD1=(0x0A),)  # Return current sram smart frame
         if testSwitch.FE_0176418_336764_TIMESTAMP_UDS_CLEAR_ENABLE:
            oProcess.St(TP.prm_638_HeadAmpMeasurements)  # Return current sram smart frame

      else:
         sptCmds.enableDiags()
         oSerial = serialScreen.sptDiagCmds()
         oSerial.SmartCmd(TP.smartUDSResetParams, dumpDEBUGResponses=1)

      if not testSwitch.NoIO:
         objPwrCtrl.powerCycle(5000,12000,10,30)

##################################### PIF dPNumInfo SMARTREADDATA ################################################
class CChkSmartAttr(CState):
   """
      This is the same function as PIF dPNumInfo SMARTREADDATA
      It is put to a new class so that any operation can have this STATE anywhere
   """
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   def run(self):
      try:
         import PIF
         from PIF import dSmartInfo
      except:
         objMsg.printMsg('Unable to read PIF dSmartInfo. Skipping check')
         return

      from PIFHandler import CPIFHandler
      PIFHandler = CPIFHandler()
      dPNum = PIFHandler.getPnumInfo(sPnum=self.dut.partNum, dPNumInfo=PIF.dSmartInfo, force=True)
      objMsg.printMsg('CChkSmartAttr dPNum=%s' % dPNum)

      from CustomCfg import CCustomCfg
      CCustomCfg().SMARTReadData(dPNum['lCAIDS'][0])

###########################################################################################################
class CIOEDCCheck(CState):
   """
      Description: Class that will display ReadAfterWrite(422) before reset smart.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      try:
         from CustomCfg import CCustomCfg
         custConfig = CCustomCfg()
         objPwrCtrl.powerCycle(5000,12000,10,30)
         custConfig.SMARTReadData(TP.prm_SmtIOEDC.get('lCAIDS', {}))
      except:
         ScrCmds.raiseException(11098, "Report IOEDC failure")

###########################################################################################################
class CGIO(CState):
   def __init__(self, dut, params=[]):
      self.dut = dut
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #---------------------------------------------------------
   def prePowerCycle(self, *args, **kwargs):
      try:
         ICmd.FlushCache()
         ICmd.StandbyImmed()
      except:
         objMsg.printMsg("Skipping prePowerCycle Exception: %s" % (traceback.format_exc(),))

   #---------------------------------------------------------
   def run(self):
      spmqm_enable = int(ConfigVars[ConfigId[2]].get('SPMQM_ENABLE','0'))
      objMsg.printMsg('class CGIO ConfigVars SPMQM_ENABLE=%s' % spmqm_enable)
      if spmqm_enable == 0:
         return

      Modules = [
                  ('gio.doWriteTestMobile()'    , 'OFF'),
                  ('gio.doSystemFileLoad()'     , 'OFF'),
                  ('gio.doIdleAPMTest()'        , 'ON'),
                ]

      IOMQM__Modules = getattr(TP,"prm_IOMQM_Modules",Modules)
      if len(IOMQM__Modules) == 0:
         objMsg.printMsg('IOMQM__Modules disabled')
         return

      from CGIOTest import CGIOTest, CGIOTest_CPC
      if objRimType.CPCRiser():
         gio = CGIOTest_CPC(self.dut)
      else:
         gio = CGIOTest(self.dut)

      gio.testCmdCount = 0
      gio.testTimeSec = 0
      gio.failCode = 0
      gio.oRF.prePowerCycle = self.prePowerCycle

      for module,status in iter(IOMQM__Modules):
         if status == 'OFF': continue

         startTime = time.time()
         objMsg.printMsg('IOMQM module=%s starttime=%s' % (module, startTime))

         try:
            ret = eval(module)
         except:
            if gio.failCode == 0:
               gio.failCode = 13169

            objMsg.printMsg("module=%s gio.failCode=%s traceback: %s" % (module, gio.failCode, repr(traceback.format_exc())))
            if not testSwitch.virtualRun:
               ScrCmds.raiseException(gio.failCode, "IOMQM fail " + module)

         elapsed = time.time() - startTime
         objMsg.printMsg('IOMQM module=%s elapsed=%.2f sec %.2f min ret=%s' % (module, elapsed, elapsed/60, ret))

###########################################################################################################
class CClearEWLM(CState):
   """
      Displays and clears drive EWLM using DITS command 0x0174
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def SPreadWorkLogPage(self):
      sptCmds.enableDiags()
      sptCmds.gotoLevel('T')
      data = sptCmds.sendDiagCmd('/Tr132,,,,30,300',timeout = 60, printResult = True)
      lastParameterCode = 0xFFFF

      for line in data.splitlines():
         splited = line.split()
         if len(splited) == 18 and splited[0] == '00000010':
            lastParameterCode = (int(splited[10], 16) * 256) + (int(splited[9], 16))
            objMsg.printMsg("SP lastParameterCode=%s" % (lastParameterCode))
            break

      return lastParameterCode

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      """
      Requires
         - CPC 2.247 and above.
         - SIC 551420 and above.
      """
      from SmartFuncs import smartEWLM as ewlm

      try:
         if not testSwitch.NoIO:
            if not testSwitch.virtualRun:
               ver = ICmd.getRimCodeVer()
               if objRimType.CPCRiser():
                  try:
                     float(ver)
                  except ValueError:
                     objMsg.printMsg("Beta version detected, not a float value")
                     ver = ver[:-1]
                     objMsg.printMsg("Beta RimCodeVer %s" %ver)
                  if (float(ver) < 2.247):
                     ScrCmds.raiseException(10251, "CPC version %s unable to support clearing of EWLM." %ver)
               elif objRimType.IOInitRiser():      # REL.SATA.551420.BAN20.SI.LOD
                  ver = [v for v in ver.split('.') if v.isdigit()][0]
                  if int(ver) < 551420:
                     ScrCmds.raiseException(10251, "SIC version %s unable to support clearing of EWLM." %ver)
                  objPwrCtrl.powerCycle(5000,12000,10,30)

            objMsg.printMsg('EWLM log page before clearing.')
            ewlm.readWorkLogPage()
            ewlm.clearWorkLogPage()                                  # clear log page
            time.sleep(30)

            # display log page after clearing
            objMsg.printMsg('EWLM log page after clearing.')
            ewlm.readWorkLogPage()
            data = ICmd.GetBuffer(RBF, 0, 512*1)['DATA'][4:]
            import binascii
            lastParameterCode = int(binascii.hexlify(data[24:26]),16)
            if lastParameterCode > 1:
               raise

         else:

            import sdbpCmds
            objMsg.printMsg('*** SERIAL PORT ***')
            self.SPreadWorkLogPage()

            if self.dut.SkipPCycle:
               sptCmds.sendDiagCmd(CTRL_T, printResult = True)
            else:
               objPwrCtrl.powerCycle(5000, 12000, 10, 10, ataReadyCheck = False)

            sptCmds.enableESLIP()
            try:
               sdbpCmds.unlockDits()
            except:
               pass

            data, error, dataBlock = sdbpCmds.clearEWLM()
            time.sleep(30)

            if self.SPreadWorkLogPage() > 0:
               raise

      except:
         objMsg.printMsg('*** EWLM not cleared! *** Traceback %s' %traceback.format_exc())
         if testSwitch.virtualRun:
            objMsg.printMsg('EWLM clearing not supported in VE.')
         elif testSwitch.FE_SGP_402984_RAISE_EWLM_CLEAR_FAILURE:
            ScrCmds.raiseException(10251, "EWLM last parameter code not cleared! %s" %traceback.format_exc())


###########################################################################################################
class CNAND_WO_Restore(CState):
   """
      NAND wearout info restore on recycled pcba
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      self.DEBUG = 0
      import re
      if testSwitch.CLEAR_NAND_FLASH_ON_RECYCLE_PCBA and int(DriveAttributes.get('PCBA_CYCLE_COUNT', 0)) > 1: #For Recycle PCBA, restore wearout info from serial flash to CFS
         objMsg.printMsg("*** For Hybrid drive with recycle PCBA, restoring NAND wearout info from Serial NOR flash ***")
         pattern = 'Clump\s*Prev->Curr->Next\s*1stNode\s*ValidLBAs\s*EraseCnt\s*WkRd/UECC\s*SLCMode\s*EraseFailCnt\s*ProgramFailCnt'

         objMsg.printMsg("Verify wearout info in Serial NOR flash")
         sptCmds.gotoLevel('O')
         drive_resp = sptCmds.sendDiagCmd('f1', printResult = True, loopSleepTime = 0.01)
         match = re.search(pattern, drive_resp)
         if match:
            objMsg.printMsg("Valid wearout information is available in Serial flash")
         else:
            ScrCmds.raiseException(14521, "For Hybrid drive with recycle PCBA, no valid wearout info in Serial flash %s" %traceback.format_exc())

         objMsg.printMsg("Restore NAND wearout info to CFS")
         #sptCmds.gotoLevel('O')
         sptCmds.sendDiagCmd('f3', printResult = True)

         objMsg.printMsg("Verify wearout info in CFS")
         #sptCmds.gotoLevel('O')
         drive_resp = sptCmds.sendDiagCmd('f0', printResult = True, loopSleepTime = 0.01)
         match = re.search(pattern, drive_resp)
         if match:
            objMsg.printMsg("Copied wearout info from Serial flash to CFS successfully")
         else:
            ScrCmds.raiseException(14521, "Failed to restore wearout info to CFS %s" %traceback.format_exc())

         if self.DEBUG:
            objMsg.printMsg("Print out wearout info from CFS")
            #sptCmds.gotoLevel('O')
            sptCmds.sendDiagCmd('b0', printResult = True)

###########################################################################################################
class CSParityCheck(CState):
   """
      Displays SuperParity Invalid ratio.
      If SPRatio > spec, do track clean up using G>Q,,22 followed by LongDST (LongDST to police against track clean up action)
      If SPRatio > spec, fail drive
      If LongDST was run, skip following 'WR_VERIFY' state to save test time
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      self.oSerial = serialScreen.sptDiagCmds()

      if sptCmds.objComMode.getMode() != sptCmds.objComMode.availModes.sptDiag:
         objPwrCtrl.powerCycle(5000,12000,10,30)
         time.sleep(5) # In IO mode, require 5sec delay to fully load Super Parity table after power cycle

      #Get SPRatio
      SPRatio = self.oSerial.GetSPRatio(getCTRL_L = True)
      objMsg.printMsg("Initial SPRatio: %s" % SPRatio)
      self.dut.driveattr['PROC_CTRL7'] = SPRatio

      if testSwitch.CHECK_SUPERPARITY_INVALID_RATIO:
         if SPRatio == None:
            ScrCmds.raiseException(48665, "Invalid SuperParity_Ratio detected")

         SPRatio_spec = float(getattr(TP, 'SPRatio', 0))
         if SPRatio > SPRatio_spec:
            import GIO
            #Clean up
            if testSwitch.INVALID_SUPER_PARITY_FULL_PACK_WRITE:
               # write pass drive, until G>Q,,22 is SMR friendly
               objMsg.printMsg("SPRatio > spec, write pass drive.")
               GIO.CWriteDriveZero(self.dut, params={}).doWriteZeroPatt('FIN2', 'MaxLBA')
            else:
               sptCmds.gotoLevel('G')
               try:
                  data = sptCmds.sendDiagCmd("/GQ,,22",timeout = 5400, printResult = True)
               except:
                  objMsg.printMsg("Q,,22Error in Q,,22: %s" % traceback.format_exc())
                  if not ConfigVars[CN]['BenchTop']:
                     raise

            #Call LongDST
            GIO.CSmartDST_SPT(self.dut, params={}).DSTTest_IDE('S_PARITY_CHK', 'Long')

            #Check SPRatio after clean up
            SPRatio = self.oSerial.GetSPRatio(getCTRL_L = True)
            objMsg.printMsg("After clean up SPRatio: %f" % SPRatio)
            if SPRatio > SPRatio_spec:
               ScrCmds.raiseException(48665,'IDT_SUPER_PARITY_CLEANUP Failed')
            else:
               #Skip WR_VERIFY state
               objMsg.printMsg('Track clean up Passed. Skip following WR_VERIFY state')
               self.dut.skipWRVerify = 1
         else:
            objMsg.printMsg('SuperParity Check Passed.')
            self.dut.skipWRVerify = 0

###########################################################################################################
class CSeaCorder(CState):
   """
      clear SeaCorder logs
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      objMsg.printMsg('Init SeaCorder')
      self.GetSeaCorder()
      self.dut.SkipY2 = True
      sptCmds.sendDiagCmd(CTRL_T, printResult = True)

      from sdbpCmds import SeaCorder
      data, errorCode, dataBlock = SeaCorder()
      objMsg.printMsg('Error Code = %x Data = %s' % (errorCode, repr(data)))

      if errorCode:
         ScrCmds.raiseException(14444,"SeaCorder Init Fail")

      if self.GetSeaCorder().find('NextEntry 0000') == -1:
          ScrCmds.raiseException(14444,"SeaCorder Init Fail")
      else:
          objMsg.printMsg('Init SeaCorder Pass')

      if not testSwitch.NoIO:
         objPwrCtrl.powerCycle(5000, 12000, 10, 10, ataReadyCheck = False)

   def GetSeaCorder(self):
      sptCmds.enableDiags(retries = 1)
      sptCmds.gotoLevel('1')
      return sptCmds.sendDiagCmd(':C', timeout = 10, printResult = True)

