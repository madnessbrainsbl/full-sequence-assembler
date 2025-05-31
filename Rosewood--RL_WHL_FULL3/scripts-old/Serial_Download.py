#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Serial Download Module
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
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Serial_Download.py $
# $Revision: #5 $
# $DateTime: 2016/12/28 17:27:59 $
# $Author: yihua.jiang $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Serial_Download.py#5 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#

from Constants import *
from TestParamExtractor import TP
from State import CState
from PowerControl import objPwrCtrl
import MessageHandler as objMsg
import ScrCmds
import traceback
from Exceptions import SeaSerialRequired
from PackageResolution import PackageDispatcher
from UPS import upsObj

#----------------------------------------------------------------------------------------------------------
class CFLS_LOAD(CState):
   """
      Class that will re-load a flash image into the serial flash using base TPM protocol and serial load SLIP
      - Emulates Win32 App SeaSerial
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      self.reqKeys = ['TXT_TPM','IMG_BIN']
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self, ReadBootPCBASN = False):
      DEBUG = 0
      missingCodes = []
      missingCodes = [key for key in self.reqKeys if PackageDispatcher(self.dut, key).getFileName() in ['',None]]
      if not len(missingCodes) == 0:
         missString = "FwKey(s): %s not found in Codes.py" % str(missingCodes)
         if testSwitch.winFOF == 1 or testSwitch.virtualRun == 1:   #Ignore missing files if winFOF
            objMsg.printMsg("winFOF mode active ignoring missing files...")
            objMsg.printMsg(missString)
         else:
            ScrCmds.raiseException(10345, missString)

      from RawBootLoader import CFlashLoad
      ofls = CFlashLoad()

      if ReadBootPCBASN == True:
         pcba_sn_boot = ''
         bootfiles = getattr(TP, 'PCBA_SN_BOOT_FILES', [])
         for file in bootfiles:
            try:
               pcba_sn_boot, hda_sn_boot = ofls.GetBootPCBASN(file)
               pcba_sn_boot = pcba_sn_boot.lstrip('0')                # trim string left 0 character
               objMsg.printMsg("Read pcba_sn_boot = %s hda_sn_boot = %s" % (pcba_sn_boot, hda_sn_boot))
               self.dut.objData.update({'pcba_sn_boot': pcba_sn_boot})
               self.dut.objData.update({'hda_sn_boot': hda_sn_boot})
               break
            except:
               objMsg.printMsg("GetBootPCBASN failed: %s" % (traceback.format_exc(),))
               pcba_sn_boot = ''
         if pcba_sn_boot != '':  # Only check the drive if we can retrieve the PCBA SN.
            from PCBA_Base import CCheckPCBA_SN
            CCheckPCBA_SN(self.dut, self.params).run()
            objMsg.printMsg("CCheckPCBA_SN passed")

         #################################################################################################
         # We do NAND wearout information retention on following conditions:
         # 1) On a Hybrid drive. Test switch CLEAR_NAND_FLASH_ON_RECYCLE_PCBA is set true for Hybrid drive
         # 2) Copying wearout info to Serial NOR flash is only done in PRE2 INIT
         # 3) Wearout info retention only performed on Recycle drive
         #################################################################################################
         if testSwitch.CLEAR_NAND_FLASH_ON_RECYCLE_PCBA and self.dut.nextOper == 'PRE2' and int(DriveAttributes.get('PCBA_CYCLE_COUNT', 0)) > 1:
            objMsg.printMsg("SeaSerial with special TPM and headerless BIN file for Hybrid drive with recycle PCBA")
            ofls_hdaless = CFlashLoad('HDALESS_TPM','HDALESS_BIN')
            ofls_hdaless.flashBoard()
            DriveOff(5)
            DriveOn(5000,12000,10)            
            promptStatus = sptCmds.sendDiagCmd(CTRL_Z, timeout = 200, Ptype='PChar', maxRetries = 3)

            if DEBUG:
               objMsg.printMsg("Original NAND wearout info on Recycle PCBA")
               sptCmds.gotoLevel('O')
               sptCmds.sendDiagCmd('b0', printResult = True)

            objMsg.printMsg("Copy NAND wearout info to Serial NOR flash")
            sptCmds.gotoLevel('O')
            sptCmds.sendDiagCmd('f2', printResult = True)

            objMsg.printMsg("Verify NAND wearout info in Serial NOR flash")
            pattern = 'Clump\s*Prev->Curr->Next\s*1stNode\s*ValidLBAs\s*EraseCnt\s*WkRd/UECC\s*SLCMode\s*EraseFailCnt\s*ProgramFailCnt'
            #sptCmds.gotoLevel('O')
            drive_resp = sptCmds.sendDiagCmd('f1', printResult = True, loopSleepTime = 0.01)
            import re
            match = re.search(pattern, drive_resp)
            if match:
               objMsg.printMsg("Copied NAND wearout info to Serial NOR flash successfully")
            else:
               ScrCmds.raiseException(14521, "Failed to copy NAND wearout info to Serial NOR flash %s" %traceback.format_exc())  

            objMsg.printMsg("Wipe off CFS and ALF by clearing first 32 clumps of NAND flash.")
            sptCmds.gotoLevel('N')
            sptCmds.sendDiagCmd('I0', printResult = True)
            sptCmds.sendDiagCmd('B0', printResult = True)
            sptCmds.sendDiagCmd('E0,1,20,1', printResult = True) #clear first 32 clumps of NAND flash
            DriveOff(5)
            DriveOn(5000,12000,10)
            UseESlip(1)            
            objMsg.printMsg("Successfully wipe off CFS and ALF on Hybrid drive with recycle PCBA")
            del ofls_hdaless
            del ofls #For Hybrid drive with recycle PCBA, use special TPM file to keep wearout information stored on Serial NOR flash
            ofls = CFlashLoad('HDALESS_TPM','IMG_BIN') #Special TPM file and SF3 BIN file

      retries = 0
      while 1:
         try:
            if not testSwitch.virtualRun:
               ofls.flashBoard()
            self.dut.reset_DUT_dnld_segment(self.reqKeys[-1])
            break
         except:
            objMsg.printMsg("Flashing board failed: %s" % (traceback.format_exc(),))
            retries = retries + 1
            if ConfigVars[CN].get('PRODUCTION_MODE',False) or testSwitch.FE_0176570_336764_ALWAYS_PAUSE_AFTER_SEASERIAL_FAIL:
               ScriptPause(30) #failure may be due to heavy CM load, so pause and try agian
            if retries >2:
               if testSwitch.winFOF == 1:
                  objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
                  return 0
               else:
                  raise

      if self.dut.driveattr.get('FDE_DRIVE','NONE') == 'FDE':
         self.dut.resetFDEAttributes()

      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      objMsg.printMsg("Auto_Seaserial PASS")
      self.dut.driveattr['AUTO_SEASERIAL'] = 'PASS'

      return 1


#----------------------------------------------------------------------------------------------------------
class CFLASH_LOD(CState):
   """
      Class that will re-load a flash image into the serial flash using base TPM protocol and serial load SLIP 
      to dnld LOD file 
      - Emulates Win32 App SeaSerial
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, codename , params={}):
      depList = []
      self.code = codename
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from RawBootLoader import CFlashLoad
                    
      objMsg.printMsg(" FLashing LOD %s" %PackageDispatcher(self.dut, self.code).getFileName()  )
      odfls = CFlashLoad()
      odfls.flashLod(PackageDispatcher(self.dut, self.code).getFileName())
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

#----------------------------------------------------------------------------------------------------------

class CSeaSerialRFWDTPMs(CState):
   """
      Class that will load a FFV flash image into the serial flash using base TPM protocol and serial load SLIP
      - Emulates Win32 App SeaSerial
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      self.reqKeys = ['RFWD15_TPM']
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def SeaSerialRFWDTPMs(self, tpmKey1=None, setBaud=True):

      """
      Init Dblog
      Syncronize boot up for serial flash programming
      Load Streaming TPM file
      """

      if testSwitch.virtualRun:
         return

      if tpmKey1 is None:
         tpmKey1 = self.reqKeys[0]

      from RawBootLoader import CFlashLoad
      oFlashLoad = CFlashLoad(tpmKey1)

      try:
         oFlashLoad.syncBootLoader()  # Power on the drive in bootstrap mode

         oFlashLoad.loadTextTPM(exitPrompt='TPM For Displaying Signatures of Firmware Segments',
                                linesPerPrint=20000,
                                updateBaud=setBaud,
                                verifyPrompt=True,
                                bypassDelay=True)
      except:
        objMsg.printMsg(traceback.format_exc())
        ScrCmds.raiseException(49013, "Streaming TPM failed to download during RFWD")

      return oFlashLoad

#----------------------------------------------------------------------------------------------------------
class CDnldCode(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def _rebuildDepopMask(self):
      if self.dut.driveattr['DEPOP_REQ'][0] == 'D':
         depopHeads = map(str, self.dut.depopMask)
         depopReq = self.dut.driveattr['DEPOP_REQ'][1:].split(',')
         objMsg.printMsg('depopHeads = %s, depopReq = %s' %(depopHeads,depopReq))
         if len(depopHeads) == 0:
            self.dut.objData.update({'T86_FINISHED': False})
            self.dut.depopMask = map(int, depopReq)
            self.dut.objData.update({'depopMask':self.dut.depopMask})
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from FSO import CFSO
      from CodeVer import theCodeVersion
      from Cell import theCell
      from Rim import objRimType, theRim
      import sptCmds

      self.oFSO = CFSO()
      flashed = 0
      if getattr(self.dut, 'PRE2INIT_SeaSr_Done', False):
         objMsg.printMsg('SeaSerial already done in PRE2 INIT. Skip TXT_TPM and IMG code download.')
         flashed = 1

      if self.params.get('ZEST_OFF', 0):
         self.oFSO.St(TP.zestPrm_11_zestOff)

      mctCodes =  ['CFW', 'CFW_1', 'CFW_2', 'CFW_3', 'IMG', 'CMB', 'CMB2', 'CMB3', 'TXT_TPM', 'IMG_BIN',
                  'RAPA', 'RAPT', 'RAPT_TDK', 'RAPT_RHO','RAPL', 'RAP',]
      mctCodes.append('S_OVL')
      intfCodes = ['TGT', 'CGN', 'OVL', 'SFWI', 'TGT2', 'OVL2', 'SFWI2','BDG_2','TGTB', 'OVLB', 'IV', 'TGT3', 'OVL3', 'SFWI3','CXM', 'IV3']
      svoCodes = ['SFWI', 'SFWI2', 'SFWI3', 'SFW']
      ovlCodes = ['OVL', 'OVL2', 'OVL3']

      from PreAmp import CPreAmp
      oPreAmp = CPreAmp()
      fsLoad = CFLS_LOAD(self.dut)

      preAmpCodeTypes = ['RAPA', 'RAPT', 'RAPT_RHO', 'RAPT_TDK', 'RAPL', 'RAP']
      allowSeaSerial = ['IMG'] #Only allow SeaSerial on download failures for these code types
      timeout = getattr(TP,'prm_DownloadCodeTimeout',300)

      # Registeroverlay()
      if len(self.params['CODES']) > 0:
         overlay_key = self.get_overlay_key()
      else:
         overlay_key = False

      if testSwitch.FE_0273221_348085_P_SUPPORT_MULTIPLE_SF3_OVL_DOWNLOAD and ( self.params.get('registerOvl', False) or overlay_key ):
         if overlay_key:
            self.dut.registerOvl = overlay_key
         else:
            self.dut.registerOvl = self.params.get('registerOvl', 'S_OVL')
         self.dut.objData.update({'registerOvl': self.dut.registerOvl})
         objMsg.printMsg("registerOvl %s " % (self.dut.registerOvl))

      if not testSwitch.FE_0110517_347506_ADD_POWER_MODE_TO_DCM_CONFIG_ATTRS :
         #disable POIS, if necessary
         if self.dut.sptActive.getMode() in [self.dut.sptActive.availModes.sptDiag, self.dut.sptActive.availModes.intBase] \
             and objRimType.CPCRiser():
            from IntfClass import CIdentifyDevice

            try:
               oIdentifyDevice = CIdentifyDevice()
            except:
               objMsg.printMsg('Identify Device failed')
               if testSwitch.FE_0110380_231166_USE_SETBAUD_NOT_POWERCYCLE_TO_VERIFY_DOWNLOAD_READY:
                  # If the drive is format corrupt then it won't respond to the ID and we need to pwrcycle to get back to a download-able state
                  objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
            else:
               if oIdentifyDevice.Is_POIS():
                  from CustomerContent import CPois
                  oPOIS = CPois(self.dut,{'ENABLED':0})
                  oPOIS.run()
                  self.dut.driveattr['POWER_ON_TYPE']="NA"

      if len(self.params['CODES']) > 0 and (not self.params['CODES'][0] in fsLoad.reqKeys):
         if ( self.dut.sptActive.getMode() in [self.dut.sptActive.availModes.sptDiag, self.dut.sptActive.availModes.intBase] ) or \
            testSwitch.BF_0162753_231166_P_ALWAYS_PWR_CYCLE_PRE_DNLD:
            #Set initial eslip mode to perform mct download
            if testSwitch.FE_0110380_231166_USE_SETBAUD_NOT_POWERCYCLE_TO_VERIFY_DOWNLOAD_READY and \
               not testSwitch.BF_0162753_231166_P_ALWAYS_PWR_CYCLE_PRE_DNLD:
               sptCmds.disableAPM()

               theCell.enableESlip()
               objPwrCtrl.changeBaud(PROCESS_HDA_BAUD)
            else:
               objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

         if self.params.get('CMP_CODE', 0) == 1:
            theCodeVersion.updateCodeRevisions()
            theCell.enableESlip()
            objPwrCtrl.changeBaud(PROCESS_HDA_BAUD)

      if self.dut.objData.get('TCG_ADD_UNLK', False) and testSwitch.FE_0151360_231166_P_ADD_SUPPORT_SAS_SED_CRT2_UNLK:
         from sptCmds import objComMode
         self.dut.objData['TCG_ADD_UNLK'] = False
         objComMode.setMode(objComMode.availModes.intBase)
         #theRim.powerCycleRim()
         objPwrCtrl.powerCycle(ataReadyCheck = 'force')
         self.oFSO.dnldCode(codeType='UNLK', timeout= timeout)
         try:
            self.oFSO.dnldCode(codeType='CFW', timeout= timeout)
         except:
            #drive won't come out of reset with sf3 code... ignore and let subsequent downloads correct
            pass
         objPwrCtrl.powerCycle()

      for code in self.params['CODES']:
         if not code in fsLoad.reqKeys:
            if flashed and code == 'IMG':
               objMsg.printMsg("Bypassing download of %s since Seaserial already performed" % code)
               continue #bypass IMG download since we already seaserialed
            if code in preAmpCodeTypes:
               preamp_type, preampMfgr, preampId, preampRev = oPreAmp.getPreAmpType()
               preampCodeType = TP.PreAmpTypes.get(preampMfgr,{}).get('CODE_TYPE','')

               if not preampCodeType == '':
                  fileName = PackageDispatcher(self.dut, preampCodeType).getFileName()
                  if fileName in ['',None] and not testSwitch.forceRapDownLoad:
                     if not (testSwitch.virtualRun == 1 or testSwitch.winFOF == 1):
                        ScrCmds.raiseException(10554 ,'Preamp code not found.')
                  elif testSwitch.forceRapDownLoad:
                     for preampCodeType in preAmpCodeTypes:
                        fileName = PackageDispatcher(self.dut, preampCodeType).getFileName()
                        if not fileName in ['',None]:
                           break
                     else:
                        if testSwitch.FailcodeTypeNotFound and not testSwitch.virtualRun:
                           ScrCmds.raiseException(10554 ,'Preamp code not found.')

                  preampCodeType = TP.PreAmpTypes.get(preampMfgr,{}).get('CODE_TYPE','')
                  if preampId in TP.PreAmpTypes[preampMfgr].keys() and \
                     (preampRev in TP.PreAmpTypes[preampMfgr][preampId][1] or TP.PreAmpTypes[preampMfgr][preampId][1] == []):
                     objMsg.printMsg('MFG: %s  ID: %s  Rev: %s  CodeType: %s' % ( preampMfgr,preampId,preampRev,preampCodeType), objMsg.CMessLvl.DEBUG)
                  elif testSwitch.forceRapDownLoad:
                     objMsg.printMsg('Forcing RAP download...', objMsg.CMessLvl.DEBUG)
                  else:
                     ScrCmds.raiseException(10554 ,'Unknown Preamp')
                  try:
                     self.oFSO.dnldCode(codeType=preampCodeType, timeout= timeout)
                  except ScriptTestFailure, (failureData):
                     if failureData[0][2] in [39169,39170,] and self.dut.codes.has_key('BDG_2'):
                        try:
                           self.oFSO.dnldCode(codeType='BDG_2', timeout= timeout)
                        except:
                           objMsg.printMsg('Resume initial code download')
                        self.oFSO.dnldCode(codeType=preampCodeType, timeout= timeout)

                     #If we failed because of DLTAGs let's try and bridge up
                     elif failureData[0][2] in [39187,11049,10092,10093,10094,10095,10250,39180,10471] and self.dut.codes.has_key('BDG'):
                        self.oFSO.dnldCode(codeType='BDG', timeout= timeout)
                        self.oFSO.dnldCode(codeType=preampCodeType, timeout= timeout)
                     elif failureData[0][2] in [39170,] and testSwitch.FE_0151360_231166_P_ADD_SUPPORT_SAS_SED_CRT2_UNLK:
                        self.oFSO.dnldCode(codeType='UNLK', timeout= timeout)
                        self.oFSO.dnldCode(codeType=preampCodeType, timeout= timeout)
                     else:
                        raise

               else:
                  ScrCmds.raiseException(10554 ,'Unknown Preamp')
            else:
               objMsg.printMsg("param= %s" %str(self.params))
               if (code in intfCodes or code == "SFW") and self.params.get('CMP_CODE', 0) == 1:
                  objMsg.printMsg('Download code has param CMP_CODE == 1')
                  if code in svoCodes:
                     fileName = PackageDispatcher(self.dut, code).getFileName()
                     codeVer = theCodeVersion.SERVO_CODE
                  else:
                     fileName = PackageDispatcher(self.dut, code).packageHandler.getManifestName()
                     codeVer = theCodeVersion.CODE_VER
                  objMsg.printMsg('Drive has code: %s, code to be dnld: %s' %(codeVer, str(fileName)))
                  try:
                     import re
                     patt = re.compile(codeVer, re.I)
                  except:
                     if testSwitch.virtualRun:
                        # VE has code_ver invalid or ? sometimes and this causes the compile to fail
                        continue
                     else:
                        raise
                  if testSwitch.virtualRun and fileName==None:
                     mobj = None
                  else:
                     mobj = patt.search(fileName)
                  if not mobj == None:
                     import serialScreen
                     oSerial = serialScreen.sptDiagCmds()
                     if code not in ovlCodes or (code in ovlCodes and oSerial.OverlayRevCorrect()):
                        objMsg.printMsg('Drive already has code: %s, no need to dnld code: %s' %(codeVer, str(fileName)))

                        sptCmds.enableESLIP(printResult = False)
                        continue

                  if self.dut.sptActive.getMode() in [self.dut.sptActive.availModes.sptDiag, self.dut.sptActive.availModes.intBase]:
                     sptCmds.enableESLIP(printResult = False)

               if testSwitch.FE_0142329_357260_P_USE_DETERMINECODETYPE_FOR_SKIP_CODE_CHECK:
                  if code in ['CFW_3', 'CFW', 'S_OVL'] and self.params.get('SKIP_CODE', False):
                     if self.dut.sptActive.determineCodeType():
                        objPwrCtrl.powerCycle(useESlip=1)
                        self.dut.sptActive.setMode(self.dut.sptActive.availModes.intBase)
                     else:
                        objMsg.printMsg('Ctrl-Z fail, no F3 code, skip dnld SF3 code')
                        continue
               else:
                  if code in ['CFW_3', 'CFW', 'S_OVL'] and self.params.get('SKIP_CODE', False):
                     import serialScreen
                     oSerial = serialScreen.sptDiagCmds()
                     try:
                        if testSwitch.FE_0141107_357260_P_INCREASE_CMD_TO_FOR_SKIP_CODE_CHECK:
                           data = sptCmds.execOnlineCmd(CTRL_Z, timeout = 30, waitLoops = 300)
                        else:
                           data = sptCmds.execOnlineCmd(CTRL_Z, timeout = 10, waitLoops = 100)
                     except:
                        objMsg.printMsg("Retry on CTRL-Z data OnlinedCmd")
                        objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
                        if testSwitch.FE_0141107_357260_P_INCREASE_CMD_TO_FOR_SKIP_CODE_CHECK:
                           data = sptCmds.execOnlineCmd(CTRL_Z, timeout = 30, waitLoops = 300)
                        else:
                           data = sptCmds.execOnlineCmd(CTRL_Z, timeout = 10, waitLoops = 100)
                     objMsg.printMsg("CDnldCode - CTRL-Z data = %s" % data)

                     if testSwitch.BF_0172797_231166_EXACT_MATCH_DETERMINE_CODE_TYPE:
                        if data.find('SF3') != -1:
                           objMsg.printMsg('Drive has SF3 code, skip dnld SF3 code')
                           continue
                        else:
                           objMsg.printMsg("Drive has F3 code, need to dnld SF3 code")
                           objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
                           self.dut.sptActive.setMode(self.dut.sptActive.availModes.intBase)
                     else:
                        if data.find('>') != -1:
                           objMsg.printMsg("Ctrl-Z passed, has F3 code, need to dnld SF3 code")
                           objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
                           self.dut.sptActive.setMode(self.dut.sptActive.availModes.intBase)
                        else:
                           objMsg.printMsg('Ctrl-Z fail, no F3 code, skip dnld SF3 code')
                           continue

               if (testSwitch.FE_0138677_336764_P_POWER_CYCLE_BEFORE_CFW_AND_S_OVL_DNLD and code in ['CFW','S_OVL']) or \
                  (testSwitch.WA_157020_357260_P_POWER_CYCLE_BEFORE_TGT_DOWNLOAD and code in ['TGT', 'TGT2', 'TGT3']):
                  objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

               try:
                  if testSwitch.WA_0120500_231166_PH_CRT2_ESLIP_DNLD_SETTING:
                     if code != 'OVL' and objRimType.CPCRiser() and self.dut.nextOper == 'CRT2' and not objRimType.CPCRiserNewSpt():
                        objMsg.printMsg("Download code in CRT2.DedicatedHandler:begin")
                        objPwrCtrl.eslipToggleRetry()
                        from ICmdFactory import ICmd
                        ESLSIPRetries = ICmd.EslipRetry()
                        try:
                           ESLIPSync = ICmd.ESync(512,1)
                        except:
                           objMsg.printMsg("DedicatedHandler:ESend / Receive Failure: Re-sync Failed")
                        objPwrCtrl.powerCycle(useESlip=1)

                  if code in ['TGT','TGT2','TGTB']: timeout = 10*60
                  self.oFSO.dnldCode(codeType=code, timeout= timeout)
               except ScrCmds.CRaiseException,(exceptionData):
                  # Try SeaSerial to recover we had eslip failures
                  if (exceptionData[0][2] in [11049, 11087, 39173] and code in allowSeaSerial and ConfigVars[CN].get("AUTO_SEASERIAL",0)) or\
                     (testSwitch.FE_0132468_357260_AUTO_SEASERIAL_FOR_CHECKSUM_MISMATCH and \
                     (exceptionData[0][2] in [11049, 11087, 39173, 38912] and code in allowSeaSerial and ConfigVars[CN].get("AUTO_SEASERIAL",0))):
                     try:
                        odfls = CFLS_LOAD(self.dut)
                        flashed = odfls.run()
                        self.oFSO.dnldCode(codeType=code, timeout= timeout)
                     except:
                        objMsg.printMsg("Auto-Seaserial Failed")
                        raise exceptionData
                  else:
                     raise
               except SeaSerialRequired:
                  if code in allowSeaSerial and ConfigVars[CN].get("AUTO_SEASERIAL",0):
                     odfls = CFLS_LOAD(self.dut)
                     flashed = odfls.run()

               except ScriptTestFailure, (failureData):
                  if code in intfCodes and failureData[0][2] in [11049, 11087] and testSwitch.WA_0121630_325269_SAS_TGT_DNLD_IGNORE_TIMEOUT:
                     if testSwitch.FE_0154919_420281_P_SUPPORT_SIO_TEST_RIM_TYPE_55:
                        objPwrCtrl.powerCycle(useESlip=1)
                     else:
                        objPwrCtrl.powerCycle()
                     continue
                  # Try SeaSerial to recover if download timed out
                  if (failureData[0][2] in [11049, 11087, 39173] and code in allowSeaSerial and ConfigVars[CN].get("AUTO_SEASERIAL",0)) or\
                     (testSwitch.FE_0132468_357260_AUTO_SEASERIAL_FOR_CHECKSUM_MISMATCH and \
                     (failureData[0][2] in [11049, 11087, 39173, 38912] and code in allowSeaSerial and ConfigVars[CN].get("AUTO_SEASERIAL",0))):
                     try:
                        objMsg.printMsg("pause 5 mins and try again")
                        ScriptPause(5*60) #failure may be due to heavy CM load, so pause 5 mins and try agian
                        odfls = CFLS_LOAD(self.dut)
                        flashed = odfls.run()
                        self.oFSO.dnldCode(codeType=code, timeout= timeout)
                     except:
                        objMsg.printMsg("Auto-Seaserial Failed, pause 5 mins ")
                        ScriptPause(5*60) #failure may be due to heavy CM load, so pause 5 mins and try agian
                        try:
                           objMsg.printMsg("seaserial failed, set lower baudrate 115200 and retry")
                           objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10,baudRate=Baud115200, useESlip=1)
                           self.oFSO.dnldCode(codeType=code, timeout= timeout)
                        except:
                           objMsg.printMsg("Auto-Seaserial Failed, pause 5 mins ")
                           ScriptPause(5*60) #failure may be due to heavy CM load, so pause 5 mins and try agian
                           try:
                              objMsg.printMsg("seaserial failed, set lower baudrate 38400 and retry")
                              objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10,baudRate=Baud38400, useESlip=1)
                              self.oFSO.dnldCode(codeType=code, timeout= timeout)
                           except:
                              raise failureData
                  #If we failed because of DLTAGs let's try and bridge up
                  elif failureData[0][2] in [39187,11049,10092,10093,10094,10095,10250,39180,10471] and self.dut.codes.has_key('BDG'):
                     self.oFSO.dnldCode(codeType='BDG', timeout= timeout)
                     self.oFSO.dnldCode(codeType=code, timeout= timeout)
                  elif failureData[0][2] in [39169,39170,11049] and self.dut.codes.has_key('BDG_2'):
                     try:
                        self.oFSO.dnldCode(codeType='BDG_2', timeout= timeout)
                     except:
                        objMsg.printMsg('Resume initial code download')
                     self.oFSO.dnldCode(codeType=code, timeout= timeout)
                  elif failureData[0][2] in [39170,] and testSwitch.FE_0151360_231166_P_ADD_SUPPORT_SAS_SED_CRT2_UNLK:
                     self.oFSO.dnldCode(codeType='UNLK', timeout= timeout)
                     self.oFSO.dnldCode(codeType=code, timeout= timeout)
                  else:
                     raise
               if code == 'IMG' and objRimType.IsLowCostSerialRiser() :
                  self.oFSO.St({'test_num':178,'prm_name':'PCBA_SN','CAP_PCBA_SN':self.oFSO.mctPcbaSN(),'CWORD1':0x120})
                  self.oFSO.St({'test_num':166,'CWORD1':0x0800, 'timeout': 200})

               if code == 'OVLB' and testSwitch.TCGSuperParity:
                  objMsg.printMsg("TCG Super Parity after OVLB download, need to perform quick serial format")
                  objPwrCtrl.powerCycle()
                  sptCmds.enableDiags()
                  sptCmds.gotoLevel('T')
                  sptCmds.sendDiagCmd('m0,6,3,,,,,22',timeout = 1200, printResult = True)
                  objMsg.printMsg("Quick serial format done")
         else:
            if flashed == 0: #only flash code once
               flashed = fsLoad.run()
            else:
               pass

         if code in mctCodes:                         # Self Test code was loaded
            self.dut.sptActive.setMode(self.dut.sptActive.availModes.mctBase)
            self.dut.f3Active = False
         elif code in intfCodes:                      # Interface code was loaded

            if testSwitch.P_DELAY_AFTER_OVL_DNLD:
               objMsg.printMsg("Pause 15 seconds after code download")
               ScriptPause(15)

            if objRimType.IOInitRiser() and not testSwitch.SI_SERIAL_ONLY:
               theRim.EnableInitiatorCommunication(self.dut.sptActive)
            else:
               self.dut.sptActive.setMode(self.dut.sptActive.availModes.intBase)

            if not testSwitch.FE_0110380_231166_USE_SETBAUD_NOT_POWERCYCLE_TO_VERIFY_DOWNLOAD_READY:
               try:                              
                  objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
               except:
                  objMsg.printMsg("1st powercycle failed, retry")
                  objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
                  objMsg.printMsg("After 2nd powercycle, okay")

         if testSwitch.FE_0110380_231166_USE_SETBAUD_NOT_POWERCYCLE_TO_VERIFY_DOWNLOAD_READY:
            sptCmds.disableAPM()
            objPwrCtrl.changeBaud(PROCESS_HDA_BAUD)

      if 'TGT' in self.params['CODES']:      #check to ensure USB Reconfiguration is allowed.
         theCodeVersion.ChkUSBReconfig()
         objPwrCtrl.drvATASpeed = 0          # reset drive SATA speed detection

      if testSwitch.BF_0164505_231166_P_ALWAYS_PWR_CYCL_POST_SPT_DNLD:
         objPwrCtrl.powerCycle(useESlip=1)

         if testSwitch.BF_0167020_231166_P_SF3_DETECTION_ROBUSTNESS:
            if self.params['CODES'][-1] in mctCodes:                         # Self Test code was loaded
               self.dut.sptActive.setMode(self.dut.sptActive.availModes.mctBase)

      if self.dut.sptActive.getMode() in [self.dut.sptActive.availModes.sptDiag, self.dut.sptActive.availModes.intBase] \
         and objRimType.CPCRiser():

         if testSwitch.FE_0110517_347506_ADD_POWER_MODE_TO_DCM_CONFIG_ATTRS :
            from IntfClass import CIdentifyDevice
            oIdentifyDevice = CIdentifyDevice()
            if not oIdentifyDevice.Is_POIS():
               ConfigVars[CN].update({'Power On Set Feature':'OFF'})

         if not testSwitch.NO_POWERCYCLE_BEFORE_AND_AFTER_UPDATECODEREVISION or testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION: #non-intrinsic script require pwr_cycle before/after updateCodeRevisions
            if testSwitch.FE_0154919_420281_P_SUPPORT_SIO_TEST_RIM_TYPE_55:
               objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
            else:
               objPwrCtrl.powerCycle(5000,12000,10,30)

            theCodeVersion.updateCodeRevisions()
            if testSwitch.FE_0154919_420281_P_SUPPORT_SIO_TEST_RIM_TYPE_55:
               objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
            else:
               objPwrCtrl.powerCycle(5000,12000,10,30)
         else:
            theCodeVersion.updateCodeRevisions()

      else:
         theCodeVersion.updateCodeRevisions()

      if self.params.get('CLR_CERTDONE_BIT', False):
         from Servo import CServoFunc
         oSrvFunc = CServoFunc()
         try:
            oSrvFunc.setCertDoneSap(enable = False)
            objMsg.printMsg('Cert Done bit cleared to 0.')
         except:
            objMsg.printMsg('Unable to clear Cert Done bit.')
            pass

      #Update SOC_Type
      if testSwitch.ENABLE_SBS_DWNGRADE_BASED_ON_SOC_BIT:
         soctype = 0
         if (self.dut.nextOper == "PRE2" and 'IMG' in self.params['CODES']):
            from Process import CProcess
            oProc = CProcess()
            oProc.St({'test_num':166,'CWORD1':32, 'timeout': 200, 'spc_id': 1}) #Get SOC_Type info
            if testSwitch.virtualRun:
               fastbit = "FALSE"
            else:
               fastbit = self.dut.dblData.Tables('P166_SOC_INFO').tableDataObj()[-1]['FAST_BIT']

            if fastbit == "TRUE":
               soctype = 1
            elif fastbit == "FALSE":
               soctype = 0
            self.dut.driveattr['SOC_TYPE'] = soctype  #update drive attribute
            self.update_dblFASTSOC(soctype) #update parametric table
         elif (self.dut.nextOper == "CRT2" and 'CFW' in self.params['CODES']):
            soctype = self.dut.driveattr.get('SOC_TYPE', 0)
            self.update_dblFASTSOC(soctype)
         self.oFSO.validateDriveSN()

      #For port checking on SP_HDSTR
      if self.dut.nextOper == "PRE2" and objRimType.IsHDSTRRiser() and not ConfigVars[CN]['BenchTop']:
         self.oFSO.St({'test_num':1,'prm_name':'spinupPrm_1','timeout':100,"CWORD1" : (0x1,),"MAX_START_TIME" : (200,),"DELAY_TIME" : (50,),})
         st([11],{'timeout': 120, 'PARAM_0_4': (0x0e00,0x02,0x00,0x00,0x0000)})
         import time
         for i in range(80):
            time.sleep(60)
            objMsg.printMsg('time sleep : %d' %i)
      if testSwitch.virtualRun:
         testSwitch.updateExternLocalRefs()

      if not self.dut.GotDrvInfo:
         pd = PackageDispatcher(self.dut, codeType = 'CFW' )
         fileName = pd.getFileName()
         pd.setFlagFileName()
         try:
            testSwitch.importExternalFlags(pd.flagFileName)
         except:
            objMsg.printMsg("Exception in flag code resolution:\n%s" % (traceback.format_exc(),))
            if testSwitch.FE_0124304_231166_FAIL_IF_NO_FLAG_FILE_FOUND  and not testSwitch.virtualRun:
               ScrCmds.raiseException(11043, "Failed to set FLG file:\n%s" % (traceback.format_exc()))
      
      if self.dut.nextOper == 'PRE2' and self.dut.nextState == 'DNLD_CODE':
         self._rebuildDepopMask()
   #-------------------------------------------------------------------------------------------------------
   def update_dblFASTSOC(self, soctype = 0):
      if testSwitch.virtualRun:
         return
      curSeq, occurrence, testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
      self.dut.dblData.Tables('P_FASTSOC').addRecord({
               'SPC_ID': str(0),
               'OCCURRENCE': occurrence,                 
               'SEQ': curSeq,
               'TEST_SEQ_EVENT': testSeqEvent,
               'SOC_TYPE': soctype,
            })
      objMsg.printDblogBin(self.dut.dblData.Tables('P_FASTSOC'), spcId32 = 0)
   #-------------------------------------------------------------------------------------------------------
   def get_overlay_key(self):
      for key in self.params['CODES']:
         if 'S_OVL' in key[0:5]:
            return key
      return False
