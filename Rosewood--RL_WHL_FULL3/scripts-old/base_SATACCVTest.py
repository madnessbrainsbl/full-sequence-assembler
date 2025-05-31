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
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_SATACCVTest.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_SATACCVTest.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *

import time, re, string
from TestParamExtractor import TP
from State import CState
from Drive import objDut
import MessageHandler as objMsg
import Utility
from PowerControl import objPwrCtrl

import ScrCmds
from IntfClass import CIdentifyDevice
from IntfClass import CInterface
import serialScreen, sptCmds
import base_IntfTest, DVT_Screens
from ICmdFactory import ICmd
from Rim import objRimType, theRim

###########################################################################################################
###########################################################################################################
class CCheckForCCVTest(CState):
    #------------------------------------------------------------------------------------------------------#
   """ Class to handle CCVTest condition """
   def __init__( self, dut, params=[]):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

      self.dut = dut

   def run(self):
      objMsg.printMsg("Checking For CCVTest")

      if testSwitch.FE_0144125_336764_P_GEMINI_CENTRAL_DRIVE_COUNT_SUPPORT \
            and not ConfigVars[CN].get('BenchTop', 0) \
            and ConfigVars[CN].get('CONFIG_SAMPLE',0) == 1 \
            and (self.dut.chamberType in ["GEMINI"] or (self.dut.chamberType in ["HDSTR"] and ConfigVars[CN].get('Config Monitoring HDSTR Support', 0)))\
            and not testSwitch.virtualRun:
         driveCountCCV = RequestService('AddConfigSample', (CN, str(EditRev), self.dut.driveattr['PART_NUM'] , self.dut.nextOper_CCV) )[1]
      else:
         if ( self.dut.chamberType in ["HDSTR"] and not ConfigVars[CN].get('Config Monitoring HDSTR Support', 0) ):
            driveCount = ConfigVars[CN].get("CCV Quantity",10)+1
         else:
            driveCountCCV = 1
      objMsg.printMsg("configName - %s" % (CN,) )
      objMsg.printMsg("EditRev    - %s" % (EditRev,) )
      objMsg.printMsg("partNum    - %s" % (self.dut.driveattr['PART_NUM'],) )
      objMsg.printMsg("operation  - %s" % (self.dut.nextOper_CCV,) )
      objMsg.printMsg("AddConfigDrive driveCount - %s" % (driveCountCCV,) )

      if testSwitch.FE_0190035_336764_P_ENABLE_SAMPLING_CCV_ITEM_IN_DRIVE_VER_S_LIST:
         self.dut.stateTransitionEvent = 'pass'
         if driveCountCCV <= ConfigVars[CN].get("CCV Quantity",10):
            objMsg.printMsg("CCV TESTING FULL ITEM ENABLED!!!")
            self.dut.CCVSampling = 1
         else:
            objMsg.printMsg("CCV TESTING FULL ITEM DISABLED!!!")
            self.dut.CCVSampling = 0
      else:
         if driveCountCCV <= ConfigVars[CN].get("CCV Quantity",10):
            objMsg.printMsg("CCV TESTING ENABLED!!!")
            self.dut.driveattr['CCV_GROUP']  =  'Y'
            self.dut.stateTransitionEvent = 'pass'
         else:
            objMsg.printMsg("CCV TESTING DISABLED!!!")
            self.dut.stateTransitionEvent = 'noCCV'

###########################################################################################################
###########################################################################################################
class CCCVTest(CState):
    #------------------------------------------------------------------------------------------------------#
   """ Class to handle CCVTest procedure """
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut

      self.attrVerification = {
                           'NETAPP_SCREEN_VER':  {'NETAPP_V3' : 'PASS',},
      }

      self.drvVerification = {
                           'READ_WWN'        : "self.WWNVerification()",
                           'PPID_VER'        : "self.PPIDVerification()",
                           'LENOVO8S_VER'    : "self.Lenovo8SVerification()",
                           'LOWCURSPINUP_CHK': "self.LCSpinupVerify()",
                           'ZERO_CHK_FULL'   : "self.FullZeroPatternCheck()",
                           'ZERO_CHK_SOME'   : "self.SampleZeroPatternCheck()",
                           'VER_400K'        : "self.Chk400K()",
                           'AMPS_CHECK'      : "self.VerAMPs()",
                           'UDR2_CHK'        : "self.UDR2EnableChk()",
                           'BGMS_CHK'        : "self.BGMSEnableChk()",
                           'DOS_CHK'         : "self.DOSEnableChk()",
                           'ZAPON_CHK'       : "self.ZAPOnChk()",
                           'ZERO_GLIST'      : "self.ZeroGList()",
                           'DEFECT_LIST'     : "self.ZeroGList(altEC = True)",
                           'SMART_DFT_LIST'  : "self.ChkSMARTList()",
                           'ZERO_CHK'        : "self.CZeroCheck()",
                           'POWERONTYPE_VER' : "self.POISVerify()",
      }



   #-------------------------------------------------------------------------------------------------------
   def WWNVerification(self, ):
      """
      Verify WWN value between drive and attribute.
      """
      oWWN = base_IntfTest.CReadWWN(self.dut)
      try:
         oWWN.run()
      except:
         return 0
      return 1
   #-------------------------------------------------------------------------------------------------------
   def POISVerify(self):
      """
      Verify POIS value between drive and attribute.
      """
      objMsg.printMsg('------------------------------------------------------------')
      objMsg.printMsg('POIS verification')
      oIdentifyDevice = CIdentifyDevice()

      poisEnabled = True

      if oIdentifyDevice.Is_POIS_Supported():
         poisEnabled = oIdentifyDevice.Is_POIS()
      else:
         poisEnabled = False
         objMsg.printMsg("POIS not supported")

      #default to not correct
      correctConfig = False

      if ( self.dut.driveConfigAttrs.get('POWER_ON_TYPE', ('=', 0) )[1] == 'PWR_ON_IN_STDBY' ):
         if poisEnabled:
            correctConfig = True
      else:
         #case where POWER_ON_TYPE != PWR_ON_IN_STDBY in cca
         if not poisEnabled:
            #only correct if poise is not enabled
            correctConfig = True

      if correctConfig or testSwitch.virtualRun:
         objMsg.printMsg("POIS Setting is correct.")
         return 1
      else:
         objMsg.printMsg("POIS Setting is incorrect.")
         return 0

   #-------------------------------------------------------------------------------------------------------
   def PPIDVerification(self,):
      """
      Verify PPID value between drive and attribute.
      Skip CCV, DellPPID verification for non-Dell drives. 
      """

      screens = []
      chars = 3
      #Check whether dcm has DE1 customer test
      from CustomCfg import CCustomCfg
      custCfg = CCustomCfg()
      dcmdata = custCfg.getDriveConfigAttributes()
      #objMsg.printMsg("debug: dcmdata %s" % (dcmdata,))
      for name in dcmdata.keys(): 
         if name == 'CUST_TESTNAME':
            value = dcmdata[name][1]
            screens = [value[i*chars:(i*chars )+chars] for i in xrange(len(value)/chars)]
            break
      #objMsg.printMsg("debug: screens %s" % (screens,))

      if 'DE1' not in screens:
         objMsg.printMsg("Not Dell drive. No comparison done. Return SKIP")
         return 2

      #Get PPID frm drive
      from IntfClass import CInterface
      oIntf = CInterface()
      if testSwitch.NoIO:
         ScriptComment("SP Read Dell PPID")
         read_PPID = ICmd.ReadPPID() # Loke
      else:
         ScriptComment("IO Read Dell PPID")

         ICmd.SmartReadLogSec(0x9A, 1)
         oIntf.displayBuffer('read')       #display read buffer with smart log data

         bD1 = oIntf.writeBufferToFile(numBytes = 24) #write buffer data to file

         if not testSwitch.virtualRun:
            read_PPID = ''.join(Utility.CUtility.byteSwap( bD1 ))[:24] #truncate to same length as some buffer functions are ' ' padded
         else:
            read_PPID = PPID

      #objMsg.printMsg("debug: read_PPID %s" % read_PPID)


      #Get PPID frm dcm
      PPID = custCfg.getDellPPID()
      if PPID == read_PPID:
         objMsg.printMsg("Dell drive. PPID comparison done. PASS")
         return 1
      else:
         objMsg.printMsg("Dell drive. PPID comparison done. FAIL")
         return 0

   #-------------------------------------------------------------------------------------------------------
   def Lenovo8SVerification(self,):
      """
      Verify Lenovo8S value between drive and attribute.
      Skip CCV, Lenovo8S verification for non-Lenovo drives. 
      """

      screens = []
      chars = 3
      #Check whether dcm has LV1 customer test
      from CustomCfg import CCustomCfg
      custCfg = CCustomCfg()
      dcmdata = custCfg.getDriveConfigAttributes()
      objMsg.printMsg("debug: dcmdata %s" % (dcmdata,))
      for name in dcmdata.keys(): 
         if name == 'CUST_TESTNAME':
            value = dcmdata[name][1]
            screens = [value[i*chars:(i*chars )+chars] for i in xrange(len(value)/chars)]
            break
      #objMsg.printMsg("debug: screens %s" % (screens,))

      if 'LV1' not in screens:
         objMsg.printMsg("Not Lenovo drive. No comparison done. Return SKIP")
         return 2

      #Get Lenovo8S frm drive
      custSerial = self.dut.driveattr['CUST_SERIAL']
      objMsg.printMsg("custSerial: %s, custSerial[0:2]: %s" % (custSerial,custSerial[0:2])) 
      nonProductionSite = False
      if custSerial[0:2] != '8S':
         nonProductionSite = True

      objMsg.printMsg("###### Readback Lenovo8S ######")
      objPwrCtrl.powerCycle()
      logData = ICmd.ReadLenovo8S()
      objMsg.printMsg("Lenovo8S Log DF:")
      objMsg.printBin(logData)

      df_custSerial = logData[20:50].strip()
      df_newcustSer = logData[110:140].strip()
      objMsg.printMsg("org_sn: %s new_sn: %s" %(df_custSerial, df_newcustSer))

      if nonProductionSite:
         objMsg.printMsg("Lenovo non production site code triggered!")
         df_custSerial = df_custSerial[:len(custSerial)]
         df_newcustSer = df_newcustSer[:len(custSerial)]

      if df_custSerial == custSerial and df_newcustSer == custSerial:
         objMsg.printMsg("Lenovo drive. Lenovo8S comparison done. PASS")
         return 1
      else:
         objMsg.printMsg("Lenovo drive. Lenovo8S comparison done. FAIL")
         return 0

   #-------------------------------------------------------------------------------------------------------
   def LCSpinupVerify(self,):
      """
      Verify that low current spinup feature is enabled on SBS drives
      """
      screens = []
      chars = 3

      if testSwitch.virtualRun:
         return 1

      #Check whether dcm has SC1 customer test
      from CustomCfg import CCustomCfg
      custCfg = CCustomCfg()
      dcmdata = custCfg.getDriveConfigAttributes()
      for name in dcmdata.keys(): 
         if name == 'CUST_TESTNAME':
            value = dcmdata[name][1]
            screens = [value[i*chars:(i*chars )+chars] for i in xrange(len(value)/chars)]
            break

      oSerial = serialScreen.sptDiagCmds() # Check status from CTRL_L
      ctr_l = oSerial.GetCtrl_L()
      status = ctr_l.get('LowCurrentSpinUp')
         
      if 'SC1' not in screens:
         #Check Low Current spin is disabled
         if status == 'disabled':
            objMsg.printMsg("Low Current SpinUp feature is disabled. PASS")
            return 1
         else:
            objMsg.printMsg("Low Current SpinUp feature is enabled, supposed to be disabled. FAIL")
            return 0
      else:
         #Check Low Current spin is enabled
         if status == 'enabled':
            objMsg.printMsg("Low Current SpinUp feature is enabled. PASS")
            return 1
         else:
            objMsg.printMsg("Low Current SpinUp feature is disabled, supposed to be enabled. FAIL")
            return 0
   #-------------------------------------------------------------------------------------------------------
   def ZeroPatternVerification(self, msg_result, msg, start_LBA, end_LBA, sctCnt):
      """
      auto rerun if the drive fail EC10158 at T510 and expected result is not zero
      """
      rerun = 1
      if testSwitch.FE_0200009_497324_P_AUTO_RERUN_AND_ZERO_PATTERN_ACTIVITY:
         rerun = 2
      while(rerun > 0):
         rerun = rerun - 1
         result = ICmd.ZeroCheck( start_LBA, end_LBA, sctCnt)
         objMsg.printMsg('%s %s'%(msg_result,result))
         if result['LLRET'] != OK:
            if testSwitch.FE_0200009_497324_P_AUTO_RERUN_AND_ZERO_PATTERN_ACTIVITY:
               if objRimType.IOInitRiser():
                  if int(result['LLRET']) == 10158:
                     try:
                        HwDetectedTable = self.dut.dblData.Tables('P000_PG_HW_DETECTED_ERR').tableDataObj()
                        if string.atoi(HwDetectedTable[len(HwDetectedTable)-1].get('EXPECTED_VALUE',0),16) != 0:
                           if rerun:
                              objPwrCtrl.powerCycle()
                              ICmd.HardReset()
                              objMsg.printMsg("Rerun @Second Time!!!")
                           else:
                              objMsg.printMsg("EC14723, SIC Drive has EXPECTED_VALUE not equal to zero!!!")
                              return 14723
                        else:
                           return 0
                     except:
                        objMsg.printMsg(msg)
                        return 0
                  else:
                     objMsg.printMsg(msg)
                     return int(result['LLRET'])
               else: # objRimType.CPCRiser()
                  if result.get('RESULT','').find('miscompare') < 0:
                     if rerun:
                        objPwrCtrl.powerCycle()
                        ICmd.HardReset()
                        objMsg.printMsg("Rerun @Second Time!!!")
                     else:
                        objMsg.printMsg("EC14723, CPC Drive does not fail from none zero pattern!!!")
                        return 14723
                  else:
                     objMsg.printMsg(msg)
                     return 0
            else:
               objMsg.printMsg(msg)
               return 0
         else:
            return 1

   #-------------------------------------------------------------------------------------------------------
   def FullZeroPatternCheck(self, ):
      """
      Verify Zero pattern drive full surface.
      """
      objMsg.printMsg('------------------------------------------------------------')
      objMsg.printMsg('Verify Zero pattern drive full surface.')

      if testSwitch.FE_0183110_231166_P_OPTIMIZE_CCV_PWR_CYCLES:
         objPwrCtrl.powerCycle()
      ICmd.HardReset()

      ReturnType = self.ZeroPatternVerification(msg_result  = "Full Pack Zero check result:",
                                                msg         = "Verify Zero pattern drive full surface FAIL!!!" ,
                                                start_LBA   = 0,
                                                end_LBA     = int(ICmd.GetMaxLBA()['MAX48'],16)-1,
                                                sctCnt      = 0x800)

      if ReturnType == 1:
         objMsg.printMsg("Verify Zero pattern drive full surface PASS!!!")
         objMsg.printMsg('------------------------------------------------------------')
         return 1
      else:
         return ReturnType

   #-------------------------------------------------------------------------------------------------------
   def SampleZeroPatternCheck(self, ):
      """
      Verify Zero pattern drive whole surface by sampling some LBA.
      """
      objMsg.printMsg('------------------------------------------------------------')
      objMsg.printMsg('Verify Zero pattern drive whole surface by sampling some LBA.')

      if testSwitch.FE_0183110_231166_P_OPTIMIZE_CCV_PWR_CYCLES:
         objPwrCtrl.powerCycle()
      ICmd.HardReset()

      maxLBA = int(ICmd.GetMaxLBA()['MAX48'],16)-1
      start_LBA = 0
      num_Sampling = 60
      for i in range(num_Sampling):
         start_LBA += int(start_LBA/num_Sampling)
         end_LBA = start_LBA+100000

         ReturnType = self.ZeroPatternVerification(msg_result  = ('Full Pack Zero check result loop %d :' %(i+1)),
                                                   msg         =  "Verify Zero pattern drive whole surface by sampling some LBA FAIL!!!" ,
                                                   start_LBA   =  start_LBA,
                                                   end_LBA     =  end_LBA,
                                                   sctCnt      =  0x800)
         if ReturnType != 1:
            return ReturnType

      objMsg.printMsg('Verify Zero pattern drive whole surface by sampling some LBA PASS!!!')
      objMsg.printMsg('------------------------------------------------------------')
      return 1

   #-------------------------------------------------------------------------------------------------------


   def CZeroCheck(self,):
      """
      Verify Zero pattern according to the DCM 
      If Zero_Pattern_Requirement is not defined in dcm, check for min requirement - first and last 2 million LBA 
      """
      zeroPatternLookup = {
         '10' : base_IntfTest.C400KZeroCheck,
         '13' : base_IntfTest.C2MZeroCheck,
         '15' : base_IntfTest.C20MZeroCheck,
         '20' : base_IntfTest.CFullZeroCheck }

      from CustomCfg import CCustomCfg
      CustConfig = CCustomCfg()
      CustConfig.getDriveConfigAttributes()
      
      #objMsg.printMsg("debug: dcmdata - %s" % (self.dut.driveConfigAttrs,))
      zeroRequirement = str(self.dut.driveConfigAttrs.get('ZERO_PTRN_RQMT',(0,None))[1]).rstrip()
      if zeroRequirement in ['None','NA','']: #if not defined in dcm, check for min requirement
         objMsg.printMsg('No Zero pattern DCM Attribute detected - Applying minimum zero pattern requirement 2million LBA')
         zeroRequirement = '13'

      #objMsg.printMsg("debug: zeroRequirement - %s type - %s" % (zeroRequirement, type(zeroRequirement)))
      if testSwitch.virtualRun:
         return 1


      try:
         Inst = zeroPatternLookup[zeroRequirement](self.dut)
         Inst.run()
         objMsg.printMsg("Zero pattern check verification pass")
      except:
         objMsg.printMsg("Zero pattern check verification fail")
         return 0
      return 1
   #-------------------------------------------------------------------------------------------------------

   
   def Chk400K(self, ):
      """
      Verify Zero pattern 1st and last 400K LBA.
      """
      objMsg.printMsg('------------------------------------------------------------')
      objMsg.printMsg('Verify Zero pattern 1st and last 400K LBA.')
      xferlength = 400000

      if testSwitch.FE_0183110_231166_P_OPTIMIZE_CCV_PWR_CYCLES:
         objPwrCtrl.powerCycle()
      ICmd.HardReset()

      ### Verify Zero pattern first 400K LBA
      ReturnType = self.ZeroPatternVerification(msg_result  = "First 400K LBA Zero check result:",
                                                msg         = "Verify Zero pattern first 400K LBA FAIL!!!" ,
                                                start_LBA   = 0,
                                                end_LBA     = xferlength - 1,
                                                sctCnt      = 0x800)
      if ReturnType != 1:
         return ReturnType

      ### Verify Zero pattern last 400K LBA
      maxLBA = int(ICmd.GetMaxLBA()['MAX48'],16)-1

      ReturnType = self.ZeroPatternVerification(msg_result  = "Last 400K LBA Zero check result:",
                                                msg         = "Verify Zero pattern last 400K LBA FAIL!!!" ,
                                                start_LBA   = maxLBA - xferlength + 1,
                                                end_LBA     = maxLBA,
                                                sctCnt      = 0x800)
      if ReturnType != 1:
         return ReturnType

      objMsg.printMsg('Verify Zero pattern 1st and last 400K LBA PASS!!!!!')
      objMsg.printMsg('------------------------------------------------------------')
      return 1
      
   #------------------------------------------------------------------------------------------------------- 

   def VerAMPs(self, ):
      """
      Verify drive if AMPs is reset.
      """

      objMsg.printMsg('------------------------------------------------------------')
      objMsg.printMsg('Verify drive if AMPs is reset.')

      oAMPS = base_IntfTest.CAMPSCheck(self.dut)
      try:
         oAMPS.run()
      except:
         return 0

      return 1

   #-------------------------------------------------------------------------------------------------------
   def UDR2EnableChk(self, ):
      """
      Verify drive if UDR2 Enable.
      """
      objMsg.printMsg('Verify drive if UDR2 is Enable')
      self.oSerial = serialScreen.sptDiagCmds()
      UDR2_Status = self.oSerial.GetUDR2(getCTRL_L = True)
      objMsg.printMsg("Drive UDR2_Status = %s" % UDR2_Status)
      if UDR2_Status == True:
         objMsg.printMsg("UDR2 is enabled! UDR2 verification pass!")
         return 1
      else:
         objMsg.printMsg("UDR2 is disabled. UDR2 verification fail!")
         #return 14845 # raise UDR2 EC 
         return 0

   #-------------------------------------------------------------------------------------------------------
   def BGMSEnableChk(self, ):
      """
      Verify drive if BGMS Enable.
      """
      objMsg.printMsg('------------------------------------------------------------')
      objMsg.printMsg('Verify drive if BGMS Enable.')

      oSerial = serialScreen.sptDiagCmds()
      if not testSwitch.FE_0183110_231166_P_OPTIMIZE_CCV_PWR_CYCLES:
         objPwrCtrl.powerCycle()
      sptCmds.enableDiags()

      lbaXlatePattern = '\S+\s+BGMS_ENABLE\s=\s(?P<BGMS_STATUS>[a-fA-F\d]+)'
      sptCmds.gotoLevel('T')

      if not testSwitch.virtualRun:
         data = sptCmds.sendDiagCmd('''F"BGMS_ENABLE"''', printResult = True)
      else:
         data = """
               F"BGMS_ENABLE"Byte:0184:           Bit:0, BGMS_ENABLE = 1
               """

      data = data.replace("\n","")
      match = re.search(lbaXlatePattern, data)

      if match:
         tempDict = match.groupdict()
         BGMSdict =  oSerial.convDictItems(tempDict, int, [16,])
         objMsg.printMsg("BGMS check BGMS_ENABLE = %d" % BGMSdict['BGMS_STATUS'])
         if BGMSdict['BGMS_STATUS'] == 0:
            objMsg.printMsg('BGMS DISABLE. Verify BGMS FAIL!!!')
            #ScrCmds.raiseException(10150, "BGMS DISABLE. Verify BGMS FAIL!!!")
            return 0
      else:
         objMsg.printMsg("BGMS check BGMS_ENABLE return data: %s" % (str(data)))
         #ScrCmds.raiseException(10150, "BGMS Check Failure: Unable determine BGMS status")
         return 0

      if not testSwitch.FE_0183110_231166_P_OPTIMIZE_CCV_PWR_CYCLES:
         objPwrCtrl.powerCycle()
      objMsg.printMsg('BGMS of this drive enable. Verify PASS!!!')
      objMsg.printMsg('------------------------------------------------------------')
      return 1

   #-------------------------------------------------------------------------------------------------------
   def DOSEnableChk(self, ):
      """
      Verify drive if DOS Enable
      """
      objMsg.printMsg('------------------------------------------------------------')
      objMsg.printMsg('Verify drive if DOS Enable.')


      if testSwitch.FE_0183111_231166_P_CCV_CHECK_ALL_DOS:
         oSerial = serialScreen.sptDiagCmds()
         if not testSwitch.FE_0183110_231166_P_OPTIMIZE_CCV_PWR_CYCLES:
            objPwrCtrl.powerCycle()
         sptCmds.enableDiags()
         #detect the dos type

         dosVersion = 3

         sptCmds.gotoLevel('T')
         try:
            if testSwitch.virtualRun:
               data1 = """
                  Byte:0130:       DOSOughtToScanThreshold = 00 10
                  """
            else:
               data1 = sptCmds.sendDiagCmd('''F"DOSOughtToScanThreshold"''', printResult = True) #dos 3 or single track dos
            if "Invalid Diag Cmd Parameter" in data1:
               raise KeyError, "Not DOS3 or Single track DOS"
         except KeyError:
            if testSwitch.ROSEWOOD7:
               # Check if DOS is supported using level 7>m command
               data1 = sptCmds.sendDiagCmd("/7m")
               sptCmds.gotoLevel('T')
            else:
               dosVersion = 1
               if testSwitch.TRUNK_BRINGUP and testSwitch.M10P:
                  data1 = sptCmds.sendDiagCmd('''F"TCO_DOSOughtToScanThreshold"''', printResult = True)
               else:
                  data1 = sptCmds.sendDiagCmd('''F"DOSATIOughtToScanThreshold"''', printResult = True)

            if "Invalid Diag Cmd Parameter" in data1:
               objMsg.printMsg("Unable to detect DOS type!")
               return 0

         objMsg.printMsg("DOS version %s detected." %dosVersion)
         if dosVersion == 3:
            lbaXlatePattern1 = '\S+\s+DOSOughtToScanThreshold\s=\s(?P<DOS1_STATUS>[a-fA-F\d *]+)'
            lbaXlatePattern2 = '\S+\s+DOSNeedToScanThreshold\s=\s(?P<DOS2_STATUS>[a-fA-F\d *]+)'
         else:
            if testSwitch.TRUNK_BRINGUP and testSwitch.M10P:
               lbaXlatePattern1 = '\S+\s+TCO_DOSOughtToScanThreshold\s=\s(?P<DOS1_STATUS>[a-fA-F\d]+)'
               lbaXlatePattern2 = '\S+\s+TCO_DOSNeedToScanThreshold\s=\s(?P<DOS2_STATUS>[a-fA-F\d]+)'
            else:
               lbaXlatePattern1 = '\S+\s+DOSATIOughtToScanThreshold\s=\s(?P<DOS1_STATUS>[a-fA-F\d]+)'
               lbaXlatePattern2 = '\S+\s+DOSATINeedToScanThreshold\s=\s(?P<DOS2_STATUS>[a-fA-F\d]+)'

         data1 = data1.replace("\n","")
         match1 = re.search(lbaXlatePattern1, data1)

         if not testSwitch.virtualRun:
            if dosVersion == 3:
               data2 = sptCmds.sendDiagCmd('''F"DOSNeedToScanThreshold"''', printResult = True)
            else:
               if testSwitch.TRUNK_BRINGUP and testSwitch.M10P:
                  data2 = sptCmds.sendDiagCmd('''F"TCO_DOSNeedToScanThreshold"''', printResult = True)
               else:
                  data2 = sptCmds.sendDiagCmd('''F"DOSATINeedToScanThreshold"''', printResult = True)
         else:
            data2 = "Byte:013C:       DOSNeedToScanThreshold = 00 20"

         data2 = data2.replace("\n","")
         match2 = re.search(lbaXlatePattern2, data2)

         if (match1 and match2) or (testSwitch.ROSEWOOD7 and match2):
            if match1:
               tempDict1 = match1.groupdict()
               tempDictVal1 = tempDict1['DOS1_STATUS'].replace(" ","")     # join two separate bytes
               tempDict1.update({'DOS1_STATUS':tempDictVal1})
               DOSdict1 =  oSerial.convDictItems(tempDict1, int, [16,])

            tempDict2 = match2.groupdict()
            tempDictVal2 = tempDict2['DOS2_STATUS'].replace(" ","")     # join two separate bytes
            tempDict2.update({'DOS2_STATUS':tempDictVal2})
            DOSdict2 =  oSerial.convDictItems(tempDict2, int, [16,])

            #objMsg.printMsg('DOSdict1 = %s DOSdict2 = %s'%(str(DOSdict1),str(DOSdict2)))
            if match1 and match2:
               dosEnabled = DOSdict1['DOS1_STATUS'] > 0 and DOSdict2['DOS2_STATUS'] > 0
            elif testSwitch.ROSEWOOD7 and match2:
               dosEnabled = DOSdict2['DOS2_STATUS'] > 0

            if dosEnabled:
               if dosVersion == 3:
                  if match1 and match2:
                     objMsg.printMsg("DOSOughtToScanThreshold = %s and DOSNeedToScanThreshold = %s... DOS verification PASS!!!!" %(hex(DOSdict1['DOS1_STATUS']), hex(DOSdict2['DOS2_STATUS'])))
                  elif testSwitch.ROSEWOOD7 and match2:
                     objMsg.printMsg("DOSNeedToScanThreshold = %s... DOS verification PASS!!!!" %hex(DOSdict2['DOS2_STATUS']))
                  else:
                     objMsg.printMsg("DOSOughtToScanThreshold = 0x40 and DOSNeedToScanThreshold = 0x80... DOS verification PASS!!!!")
               else:
                  if testSwitch.TRUNK_BRINGUP and testSwitch.M10P:
                     objMsg.printMsg("TCO_DOSOughtToScanThreshold = 0x40 and TCO_DOSNeedToScanThreshold = 0x80... DOS verification PASS!!!!")
                  else:
                     objMsg.printMsg("DOSATIOughtToScanThreshold = 0x40 and DOSATINeedToScanThreshold = 0x80... DOS verification PASS!!!!")
            else:
               objMsg.printMsg("DOS is DISABLED!!!!")
               #ScrCmds.raiseException(10150, "DOS Check Failure: Unable determine DOS status")
               return 0
         else:
            objMsg.printMsg("DOS Check Failure: Unable determine DOS status")
            return 0

      else:
         objMsg.printMsg("DOS check skipped.")
         return 2



      if not testSwitch.FE_0183110_231166_P_OPTIMIZE_CCV_PWR_CYCLES:
         objPwrCtrl.powerCycle()
      objMsg.printMsg('DOS of this drive is ENABLED. Verify PASS!!!')
      objMsg.printMsg('------------------------------------------------------------')
      return 1
   #-------------------------------------------------------------------------------------------------------
   def ZAPOnChk(self, ):
      """
      Verify drive if ZAP turn on
      """
      objMsg.printMsg('------------------------------------------------------------')
      objMsg.printMsg('Verify drive if ZAP turn on.')

      oSerial = serialScreen.sptDiagCmds()
      if not testSwitch.FE_0183110_231166_P_OPTIMIZE_CCV_PWR_CYCLES:
         objPwrCtrl.powerCycle()
      sptCmds.enableDiags()


      if testSwitch.BF_0170793_231166_P_FIX_ZAP_CCV_CHECK_EXACT_PARSE:
         lbaXlatePattern = 'ZAP Control:\s(?P<ZAP_Status>[\S ]+)'
      else:
         lbaXlatePattern = 'ZAP Control:\s(?P<ZAP_Status>.{24})'

      sptCmds.gotoLevel('5')

      if not testSwitch.virtualRun:
         data = sptCmds.sendDiagCmd('d', printResult = True)
      else:
         if testSwitch.FE_0168477_209214_ZAP_REV_ALLOCATION:
            data = """
                  ZAP Control: Write ZAP from disc
                  """
         else:
            data = """
                  ZAP Control: Read/Write ZAP from disc
                  """

      data = data.replace("\n","")
      match = re.search(lbaXlatePattern, data)


      if match:
         tempDict = match.groupdict()
         objMsg.printMsg("ZAP status = %s" % tempDict['ZAP_Status'])
         if testSwitch.FE_0168477_209214_ZAP_REV_ALLOCATION:
            if testSwitch.BF_0170793_231166_P_FIX_ZAP_CCV_CHECK_EXACT_PARSE:
               if tempDict['ZAP_Status'].find('Write ZAP from disc') > -1 or tempDict['ZAP_Status'].find('Read/Write ZAP from disc') > -1:
                  objMsg.printMsg("ZAP turn on...Verify PASS!!!!")
               else:
                  objMsg.printMsg("ZAP turn off...Verify FAIL!!!!")
                  return 0
            else:
               if tempDict['ZAP_Status'].rstrip() == 'Write ZAP from disc' or tempDict['ZAP_Status'] == 'Read/Write ZAP from disc':
                  objMsg.printMsg("ZAP turn on...Verify PASS!!!!")
               else:
                  objMsg.printMsg("ZAP turn off...Verify FAIL!!!!")
                  #ScrCmds.raiseException(10150, "ZAP turn off...Verify FAIL!!!!")
                  return 0
         else:
            if testSwitch.BF_0170793_231166_P_FIX_ZAP_CCV_CHECK_EXACT_PARSE and tempDict['ZAP_Status'].find('Read/Write ZAP from disc') > -1:
               objMsg.printMsg("ZAP turn on...Verify PASS!!!!")
            elif tempDict['ZAP_Status'] == 'Read/Write ZAP from disc':
               objMsg.printMsg("ZAP turn on...Verify PASS!!!!")
            else:
               objMsg.printMsg("ZAP turn off...Verify FAIL!!!!")
               #ScrCmds.raiseException(10150, "ZAP turn off...Verify FAIL!!!!")
               return 0

      else:
         objMsg.printMsg("ZAP turn off...Verify FAIL!!!!")
         return 0

      if not testSwitch.FE_0183110_231166_P_OPTIMIZE_CCV_PWR_CYCLES:
         objPwrCtrl.powerCycle()
      objMsg.printMsg('ZAP of this drive turn on. Verify PASS!!!')
      objMsg.printMsg('------------------------------------------------------------')
      return 1


   #-------------------------------------------------------------------------------------------------------
   def ZeroGList(self,altEC = False):
      """
      Verify drive if have 0 Glist
      """
      objMsg.printMsg('------------------------------------------------------------')
      objMsg.printMsg('Verify drive if 0 Glist')
      oDL = base_IntfTest.CCheck_DefList(self.dut,{})

      try:
        oDL.run()
      except:
        if altEC:
           return 10506
        else:
           return 0
      return 1


      
   #-------------------------------------------------------------------------------------------------------
   def ChkSMARTList(self):
      oChkSmartList = base_IntfTest.CSmartDefectList(self.dut,{})
      smartLogDefects, smartAttrDefects = oChkSmartList.run()
      defectLimitExceeded = 0
      if sum(smartLogDefects.values()) > 0:
            objMsg.printMsg("SmartLog A8/A9 ENTRIES GREATER THAN LIMIT %d" % (DefectListLimits))
            defectLimitExceeded = 1
      elif sum(smartAttrDefects.values()) > 0:
            objMsg.printMsg("SmartAttributes 5, C5, C6, 410, 412 ENTRIES GREATER THAN LIMIT %d" % (DefectListLimits))
            defectLimitExceeded = 1
      if defectLimitExceeded > 0:
         return 10506
      else:
         return 1
      
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      """
      Exec a list of commands specified in Test Parameters variable "MQMCommandTuple".
      Each tuple entry being a string to execute as code.
      """
      verification_pass = True
      verification_pass_w_alt_EC = True
      curtime = time.time()

      DriveVerificationList = ['DOS_CHK','AMPS_CHECK','ZERO_GLIST','READ_WWN','POWERONTYPE_VER', 'PPID_VER', 'LENOVO8S_VER', 'LOWCURSPINUP_CHK', 'ZAPON_CHK', 'ZERO_CHK']
      #DriveVerificationList = ['BGMS_CHK']
      sum_drive_ver = []

      if len(DriveVerificationList):

         for ver_item in DriveVerificationList:
            objMsg.printMsg("*****************Executing %s*****************"%str(ver_item))
            objMsg.printMsg(self.drvVerification[ver_item])
            result = eval(self.drvVerification[ver_item])
            if int(result) == 2:
               sum_drive_ver.append((ver_item, 'SKIP'))
            elif int(result) != 1:        # result is in case : 0,ec
               if int(result) > 1: #EC case
                  verification_pass_w_alt_EC = False
                  report_fail = result
               else:              # Pass case
                  verification_pass = False
               sum_drive_ver.append((ver_item, 'FAIL'))
            else:
               sum_drive_ver.append((ver_item, 'PASS'))
  
      # Print verification report
      objMsg.printMsg("====================== CCV Result Summary  ======================")
      objMsg.printMsg("configName - %s EditRev    - %s partNum    - %s operation  - %s" % (CN,EditRev,self.dut.driveattr['PART_NUM'],self.dut.nextOper))
      objMsg.printMsg(sum_drive_ver)

      if len(sum_drive_ver):
         ver_num = 0
         objMsg.printMsg("------------------------ Drive Verification result ------------------------")
         objMsg.printMsg("\tNo\tItem\t\t\t\tResult")
         for i in sum_drive_ver:
            ver_num += 1
            self.dut.driveattr[str(i[0])] = str(i[1])
            objMsg.printMsg("\t%d.\t%s\t\t\t\t%s"%(ver_num,str(i[0]),str(i[1])))

      objMsg.printMsg("============================== End ==============================")

      if not verification_pass: # At least one CCV item return 0
         self.dut.driveattr['CCV_TT'] = time.time()- curtime
         if ConfigVars[CN].get('BenchTop', 0):                             # any fail on bench test
            ScrCmds.raiseException(48735, 'CCV on Bench Test FAIL!!!')
         else:
            ScrCmds.raiseException(48735, 'CCV Test FAIL!!!')
      elif not verification_pass_w_alt_EC: # No CCV item return 0 but return alternate EC, should raise alternate EC
         ScrCmds.raiseException(report_fail, 'CCV Test FAIL!!!')

      self.dut.driveattr['CCVTEST'] = 'PASS'
###########################################################################################################
###########################################################################################################
class CCleanupPostCCV(CState):
    #------------------------------------------------------------------------------------------------------#
   """ Class to Cleanup at end of process """
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut


   #-------------------------------------------------------------------------------------------------------
   def UDR2EnableChk(self, startup = 1):
      """
      Verify drive if UDR2 Enable.
      """
      objMsg.printMsg('------------------------------------------------------------')
      objMsg.printMsg('Verify drive if UDR2 Enable.')
      if startup:
         objPwrCtrl.powerCycle()
         sptCmds.enableDiags()
      oSerial = serialScreen.sptDiagCmds()
      oSerial.gotoLevel('T')

      lbaXlatePattern = 'LTTC-UDR2+\s+(?P<UDR2_Status>.{7})'
      if not testSwitch.virtualRun:
         data = sptCmds.sendDiagCmd(CTRL_L,printResult=True)
      else:
         data = """
               Dell - Muskie QNR Yeti3 30 zone RAP17 new skews
               Product FamilyId: 3A, MemberId: 03
               HDA SN: 9WK0W6V1, RPM: 7202, Wedges: 1A0, Heads: 4, Lbas: 74706DB0, PreampType: 58 01
               PCBA SN: 00007050WA1M, Controller: YETIST_3_0(649B)(3-12-3-3), Channel: AGERE_COPPERHEAD_LITE, PowerAsic: MCKINLEY DESKTOP LITE Rev 91, BufferBytes: 2000000
               Package Version: MU0X4B.DEN1.EQ0383.KA02    , Package P/N: 100597561, Package Builder ID: F1,
               Package Build Date: 10/19/2009, Package Build Time: 14:13:35, Package CFW Version: MU0X.DEN1.00214790.F100,
               Package SFW1 Version: B418, Package SFW2 Version: ----, Package SFW3 Version: ----, Package SFW4 Version: ----
               Controller FW Rev: 10191413, CustomerRel: KA02, Changelist: 00214790, ProdType: MU0X.DEN1, Date: 10/19/2009, Time: 141335, UserId: 00391559
               Servo FW Rev: B418
               RAP FW Implementation Key: 11, Format Rev: 0202, Contents Rev: A4 0B 03 00
               Features:
               - Quadradic Equation AFH enabled
               - VBAR with adjustable zone boundaries enabled
               - Volume Based Sparing enabled
               - IOEDC enabled
               - IOECC enabled
               - DERP Read Retries enabled
               - LTTC-UDR2 enabled
               """

      data = data.replace("\n","")
      match = re.search(lbaXlatePattern, data)

      if match:
         tempDict = match.groupdict()
         objMsg.printMsg("UDR2 status = %s" % tempDict['UDR2_Status'])
         if tempDict['UDR2_Status'] == 'enabled':
            objMsg.printMsg("UDR2 ENABLED...Verify PASS!!!!")
         else:
            objMsg.printMsg("UDR2 DISABLED...Verify FAIL!!!!")
            #ScrCmds.raiseException(10150, "UDR2 DISABLED...Verify FAIL!!!!")
            return 0
      elif testSwitch.FE_0184238_475827_P_ADD_RETRIES_FOR_CCVTEST_UDR2_CHK and not testSwitch.virtualRun:
         retries = 3
         while retries > 0:
            objMsg.printMsg("Unable to parse UDR2 status.  Sleeping for 60 seconds.  Retries remaining:  %d" %retries)
            time.sleep(60)
            data = sptCmds.sendDiagCmd(CTRL_L,printResult=True)
            data = data.replace("\n","")
            match = re.search(lbaXlatePattern, data)
            if match:
               tempDict = match.groupdict()
               objMsg.printMsg("UDR2 status = %s" % tempDict['UDR2_Status'])
               if tempDict['UDR2_Status'] == 'enabled':
                  objMsg.printMsg("UDR2 ENABLED...Verify PASS!!!!")
                  break
            retries -= 1
            if retries == 0:
               objMsg.printMsg("UDR2 DISABLED...Verify FAIL!!!!")
               return 0
      else:
         objMsg.printMsg("UDR2 disable...Verify FAIL!!!!")
         return 0

      if startup:
         objPwrCtrl.powerCycle()
      objMsg.printMsg('------------------------------------------------------------')
      return 1

   def run(self):
      objMsg.printMsg('******************Clean up drive before complete******************')
      curtime = time.time()

      try:
         if getattr(testSwitch, 'MUSKIE', False):

            #Clear DOS
            oClearDos = base_IntfTest.CClearDOS(self.dut,{'startup':0})
            oClearDos.run()

            #Clear SMART
            oClrSMRT = base_IntfTest.CClearSMARTCCV(self.dut,{'startup':0})
            oClrSMRT.run()

            #Clear EPC
            sptCmds.enableESLIP()
            oClrEPC = base_IntfTest.CClearEpc(self.dut,{'startup':0})
            oClrEPC.run()
            sptCmds.enableDiags()

            #Clear MiniCert
            oClrMiniCert = base_IntfTest.CClearMiniCert(self.dut,{'startup':0})
            oClrMiniCert.run()

            #Clear UDS
            sptCmds.enableESLIP()
            oClrUds = base_IntfTest.CClearUds(self.dut,{'startup':0})
            oClrUds.run()
            sptCmds.enableDiags()

            #Zero G-List
            oDPG2 = base_IntfTest.CDisplay_G_list(self.dut,{'spc_id': 0,'startup':0})
            oDPG2.run()


         elif getattr(testSwitch, 'SENTOSA', False):

            #Zero G-List
            oDPG2 = base_IntfTest.CDisplay_G_list(self.dut,{'spc_id': 0,'startup':0})
            oDPG2.run()

            #Clear MiniCert
            oClrMiniCert = base_IntfTest.CClearMiniCert(self.dut,{'startup':0})
            oClrMiniCert.run()


            if not testSwitch.FE_0177786_231166_P_REM_CE_AND_VER_SMART_IN_CLEANUP:
               sptCmds.enableESLIP()

               #Verify Smart
               oVerifySmart = base_IntfTest.CVerifySMART(self.dut,{'startup':0})
               oVerifySmart.run()


               #Critical Log Event Check
               oCriticalLog = base_IntfTest.CCriticalEvents(self.dut,{'startup':0})
               oCriticalLog.run()

            sptCmds.enableDiags()

            #Clear SMART
            oClrSMRT = base_IntfTest.CClearSMART(self.dut,{'startup':0})
            oClrSMRT.run()


         elif getattr(testSwitch, 'MANTA_RAY', False):

            #Zero G-List
            oDPG2 = base_IntfTest.CDisplay_G_list(self.dut,{'spc_id': 0,'startup':0})
            oDPG2.run()

            #Clear MiniCert
            oClrMiniCert = base_IntfTest.CClearMiniCert(self.dut,{'startup':0})
            oClrMiniCert.run()

            if not testSwitch.FE_0177786_231166_P_REM_CE_AND_VER_SMART_IN_CLEANUP:
               sptCmds.enableESLIP()

               #Verify Smart
               oVerifySmart = base_IntfTest.CVerifySMART(self.dut,{'startup':0})
               oVerifySmart.run()

               #Critical Log Event Check
               oCriticalLog = base_IntfTest.CCriticalEvents(self.dut,{'startup':0})
               oCriticalLog.run()

            sptCmds.enableDiags()

            #Clear SMART
            oClrSMRT = base_IntfTest.CClearSMART(self.dut,{'startup':0})
            oClrSMRT.run()



         elif (getattr(testSwitch, 'LUXOR', False) or getattr(testSwitch, 'KARNAK', False) or getattr(testSwitch, 'TUI', False)):

            #Zero G-List
            oDPG2 = base_IntfTest.CDisplay_G_list(self.dut,{'spc_id': 0,'startup':0})
            oDPG2.run()

            #Clear MiniCert
            oClrMiniCert = base_IntfTest.CClearMiniCert(self.dut,{'startup':0})
            oClrMiniCert.run()

            if self.params.get('RESET_AMPS', 1):
               #Clear AMPS
               oResetAmps = base_IntfTest.CResetAMPS(self.dut,{'startup':0})
               oResetAmps.run()

            if not testSwitch.FE_0213483_009408_DISABLE_DOS_CLEARING_IN_SATA_CCV:
               #Clear DOS
               oClearDos = base_IntfTest.CClearDOS(self.dut,{'startup':0})
               oClearDos.run()


            if not testSwitch.FE_0177786_231166_P_REM_CE_AND_VER_SMART_IN_CLEANUP:
               sptCmds.enableESLIP()

               #Verify Smart
               oVerifySmart = base_IntfTest.CVerifySMART(self.dut,{'startup':0})
               oVerifySmart.run()

               #Critical Log Event Check
               oCriticalLog = base_IntfTest.CCriticalEvents(self.dut,{'startup':0})
               oCriticalLog.run()

               sptCmds.enableDiags()

            if testSwitch.FE_0191007_231166_P_ADD_MC_PART_A_VERIFY_DIAG_CLEANUP:
               DVT_Screens.CCheckMediaCacheDiag(self.dut,{'startup':0}).run()

            #Clear SMART
            oClrSMRT = base_IntfTest.CClearSMART(self.dut,{'startup':0})
            oClrSMRT.run()
            
            #Reset EPC
            oClrEPC = base_IntfTest.CResetEPC(self.dut)
            oClrEPC.run()

            sptCmds.enableESLIP()

            #Clear UDS
            oClrUds = base_IntfTest.CClearUds(self.dut,{'startup':0})
            oClrUds.run()
            sptCmds.enableDiags()

            if not testSwitch.FE_0178064_231166_P_DISABLE_UDR_CHK_IN_CLEANUP:
               self.UDR2EnableChk()

         else:
            msg = 'This product does not yet support cleanup and can not be shipped!!'
            objMsg.printMsg(msg)
            ScrCmds.raiseException(10150, msg)

         #objPwrCtrl.powerCycle(5000,12000,10,30)


      finally:
         self.dut.driveattr['CLEAN_TT'] = time.time()- curtime




