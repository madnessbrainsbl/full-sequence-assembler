# STOP HALT STOP HALT STOP HALT STOP HALT STOP HALT STOP HALT STOP HALT
#         SSS         TTTTTTTTTTT             OOO          PPPPPP
#      SS     SS          TT               OO     OO       PP    PPP
#     SS                  TT             OO         OO     PP       PP
#      SS                 TT             OO         OO     PP    PPP
#        SSS              TT             OO         OO     PPPPPP
#            SS           TT             OO         OO     PP
#              SS         TT             OO         OO     PP
#     SS     SS           TT               OO     OO       PP
#        SSS              TT                  OOO          PP
# STOP HALT STOP HALT STOP HALT STOP HALT STOP HALT STOP HALT STOP HALT

# Please DO NOT make any changes to this file.  All changes need to go through
# the commonality team responsible for this process.

###########################################################################################################
from Constants import *
import time, re, binascii
from TestParamExtractor import TP
from State import CState
import MessageHandler as objMsg
from PowerControl import objPwrCtrl
import ScrCmds
from IntfClass import CIdentifyDevice
import serialScreen, sptCmds
from ICmdFactory import ICmd
from ReliSmart import CSmartAttributes
from CustomCfg import CCustomCfg
from sdbpComm import *
from Serial_ICmd import Serial_ICmd 
import SED_Serial
import sdbpCmds
import traceback
global CCV1, CCV2

#################################### CCV Version number. ##################################################

# MAJOR changes such as testing support adds must increment the major revision x.0 (x)
# Minor changes such as flow of a lower level validation must increment the minor revision 0.x (x)
versionHistory = {
                  '1.00' :  ['12/9/2015','Initial release for base_CCV.py'],
                  '1.01' :  ['12/23/2015','Check CODE_VER and SERVO_CODE between drive and fis attribute ONLY'],
                  '1.02' :  ['12/01/2016','Added new IV_SW_REV attribute check between drive and fis attribute ONLY'],
                  '1.03' :  ['10/02/2016','Replace DETS Dell PPID cmd with diag. command'],
                  '1.04' :  ['26/02/2016','Include CCV1/2 bug fix in IO mode'],
                  '1.10' :  ['03/01/2016','Support Master and Child common part number process'],
                  '1.20' :  ['05/03/2016','Added RFWD 1.5'],
                  '1.32' :  ['07/28/2016','Minor changes to run CCV in IO mode'],
                  '1.40' :  ['08/01/2016','Check BYTES_PER_SCTR drive attribute'],
                  '1.43' :  ['09/23/2016','Fix timing misalignment between UDS timer and SMART POH'],
                  }
CCV_VERSION = max(versionHistory.keys())
objMsg.printMsg('%s base_CCV.py %s %s %s' % ('-'*20,CCV_VERSION,versionHistory[CCV_VERSION][0], "-" * 20))
for value in versionHistory[CCV_VERSION][1:]:
   objMsg.printMsg(value)
###########################################################################################################

class CCCV_main(CState):
   """
      Class to ensure drive configs are according to customer requirements

      ********************************************************************
      * Only to make changes to this module when there is                *
      * 1) New customer requirement                                      *
      * 2) Existing customer requirement changed                         *
      ********************************************************************
   """

   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut
      global CCV1, CCV2
      CCV1 = False
      CCV2 = False
      if self.dut.nextOper == 'FIN2' or self.dut.nextOper == 'CUT2':
         CCV1 = True
      elif self.dut.nextOper == 'CCV2' or self.dut.nextOper == 'FNG2':
         CCV2 = True
        
                            # CCV Module Name        Corresponding Class        ON/OFF

#CHOOI-02Jun17 OffSpec
#       self.CCV_Modules = [ ('DISABLE_UDR2'         , 'CDisableUDR_CCV'        , 'ON'),
#                            ('DSTAGE_ACT_VER'       , 'CDStageActVer_CCV'      , 'ON'),
#                            ('ZERO_PTTN_VER'        , 'CZeroPttnVer_CCV'       , 'ON'),
#                            ('SMART_THR_VER'        , 'CSMARTThrVer_CCV'       , 'ON'),
#                            ('SMART_LOGSATTRS_VER'  , 'CSMARTLogsAttrsVer_CCV' , 'ON'),
#                            ('POIS_VER'             , 'CPOISVer_CCV'           , 'ON'),
#                            ('SATASPEED_VER'        , 'CSATASpeedVer_CCV'      , 'ON'),
#                            ('PPID_VER'             , 'CPPIDVer_CCV'           , 'ON'),
#                            ('LENOVO8S_VER'         , 'CLenovo8SVer_CCV'       , 'ON'),
#                            ('RLIST_VER'            , 'CRListVer_CCV'          , 'ON'),
#                            ('DOS_VER'              , 'CDOSVer_CCV'            , 'ON'),
#                            ('ZAP_VER'              , 'CZAPVer_CCV'            , 'ON'),
#                            ('WWN_VER'              , 'CWWNVer_CCV'            , 'ON'),
#                            ('DRVATTR_VER'          , 'CAttrVer_CCV'           , 'ON'),
#                            ('SP_VER'               , 'CSPVer_CCV'             , 'ON'),
#                            ('LCSPIN_VER'           , 'CLCSPINVer_CCV'         , 'ON'),
#                            ('MC_VER'               , 'CMCVer_CCV'             , 'ON'),
#                            ('NVC_VER'              , 'CNVCVer_CCV'            , 'ON'),
#                            ('SOC_VER'              , 'CSOCVer_CCV'            , 'ON'),
#                            ('AMPS_RESET'           , 'CAMPSReset_CCV'         , 'ON'),
#                            ('DOS_RESET'            , 'CDOSReset_CCV'          , 'ON'),
#                            ('EPC_RESET'            , 'CEPCReset_CCV'          , 'ON'),
#                            ('EWLM_RESET'           , 'CEWLMReset_CCV'         , 'OFF'),
#                            ('SECURITY_VER'         , 'CSecVer_CCV'            , 'ON'),
#                            ('RFWD_1_5'             , 'CRogueFWDetect_CCV'     , 'ON'),
#                            ('ENABLE_UDR2'          , 'CEnableUDR_CCV'         , 'ON'),
#                            ('SMART_RESET'          , 'CSMARTReset_CCV'        , 'ON'),
#                            ('UDS_RESET'            , 'CUDSReset_CCV'          , 'ON'),]

      self.CCV_Modules = [ ('DISABLE_UDR2'         , 'CDisableUDR_CCV'        , 'ON'),
                           ('DSTAGE_ACT_VER'       , 'CDStageActVer_CCV'      , 'ON'),
                           ('ZERO_PTTN_VER'        , 'CZeroPttnVer_CCV'       , 'ON'),
                           ('SMART_THR_VER'        , 'CSMARTThrVer_CCV'       , 'ON'),
                           ('SMART_LOGSATTRS_VER'  , 'CSMARTLogsAttrsVer_CCV' , 'ON'),
                           ('POIS_VER'             , 'CPOISVer_CCV'           , 'ON'),
                           ('SATASPEED_VER'        , 'CSATASpeedVer_CCV'      , 'ON'),
                           ('PPID_VER'             , 'CPPIDVer_CCV'           , 'ON'),
                           ('LENOVO8S_VER'         , 'CLenovo8SVer_CCV'       , 'ON'),
                           ('RLIST_VER'            , 'CRListVer_CCV'          , 'ON'),
                           ('DOS_VER'              , 'CDOSVer_CCV'            , 'ON'),
                           ('ZAP_VER'              , 'CZAPVer_CCV'            , 'ON'),
                           ('WWN_VER'              , 'CWWNVer_CCV'            , 'OFF'),
                           ('DRVATTR_VER'          , 'CAttrVer_CCV'           , 'OFF'),
                           ('SP_VER'               , 'CSPVer_CCV'             , 'ON'),
                           ('LCSPIN_VER'           , 'CLCSPINVer_CCV'         , 'ON'),
                           ('MC_VER'               , 'CMCVer_CCV'             , 'ON'),
                           ('NVC_VER'              , 'CNVCVer_CCV'            , 'ON'),
                           ('SOC_VER'              , 'CSOCVer_CCV'            , 'ON'),
                           ('AMPS_RESET'           , 'CAMPSReset_CCV'         , 'ON'),
                           ('DOS_RESET'            , 'CDOSReset_CCV'          , 'ON'),
                           ('EPC_RESET'            , 'CEPCReset_CCV'          , 'ON'),
                           ('EWLM_RESET'           , 'CEWLMReset_CCV'         , 'OFF'),
                           ('SECURITY_VER'         , 'CSecVer_CCV'            , 'ON'),
                           ('RFWD_1_5'             , 'CRogueFWDetect_CCV'     , 'ON'),
                           ('ENABLE_UDR2'          , 'CEnableUDR_CCV'         , 'ON'),
                           ('SMART_RESET'          , 'CSMARTReset_CCV'        , 'ON'),
                           ('UDS_RESET'            , 'CUDSReset_CCV'          , 'ON'),]

#       self.CCV_Modules = [ ('DISABLE_UDR2'         , 'CDisableUDR_CCV'        , 'ON'),
#                            ('POIS_VER'             , 'CPOISVer_CCV'           , 'ON'),
#                            ('ENABLE_UDR2'          , 'CEnableUDR_CCV'         , 'ON'),
#                            ('SMART_RESET'          , 'CSMARTReset_CCV'        , 'ON'),
#                            ('UDS_RESET'            , 'CUDSReset_CCV'          , 'ON'),]

      if testSwitch.M11P or testSwitch.M11P_BRING_UP:
         self.disable_CCV_Test_list = ['SMART_THR_VER','SP_VER','LCSPIN_VER']
         for ccv_mod, ccv_class, status in self.CCV_Modules:
            if ccv_mod in self.disable_CCV_Test_list:
               self.CCV_Modules.__setitem__(self.CCV_Modules.index((ccv_mod,ccv_class,status)),(ccv_mod,ccv_class,'OFF'))

      self.CCV2_AttrList = ['CCV_REVISION',
                            'CFG',
                            'RFWD_SEVERITY',
                            'CCV2_TEST_DONE', 
                            'CCV2_TEST_TIME', 
                            'TDCI_COMM_LIFE',
                            'TDCI_COMM_NUM', 
                            'CCVTEST',
                            'FAIL_CODE', 
                            'FAIL_STATE', 
                            'FAIL_TEST',
                            'TEST_EQUIP',
                            'CERT_TEMP',
                            'OPS_CAUSE',
                            'DR_REPLUG_CNT',
                            'RISER_TYPE',
                            'RIM_TYPE',
                            'CPU_METRIC',
                            'RSS',
                            'SZ']      

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      """
      Execute CCV Tests
      """

      # TEMPORARY for RWLC - Selectively turn off RFWD (To remove it after all fw roll to ver4618 and above)
      objMsg.printMsg("Selectively turn off RFWD if (fw_ver < 4618)")
      if testSwitch.virtualRun:
         drv_fw = "RO08B6.SDM1.CC4638.SDM1"
      else:      
         drv_fw = self.dut.driveattr.get('CODE_VER', DriveAttributes.get('CODE_VER', 'NONE'))
      pattern = '\s*\w+.\w+.(?P<FW_VER>[\dA-Fa-f]+).\w+'
      fw_ver = 7777
      sad_fw_ver = False

      match = re.search(pattern, drv_fw)
      if match:
         fw_ver = match.groupdict()['FW_VER']

         if 'CD' in fw_ver: #CD0009
            sad_fw_ver = True
         elif 'CC' in fw_ver: #CC4618
            fw_ver = int(fw_ver[2:6])
         else: #461810
            fw_ver = int(fw_ver[0:4])
      else:
         objMsg.printMsg("FW version cannot be extracted, turn ON RFWD")

      if sad_fw_ver:
         objMsg.printMsg("Turn ON RFWD. Post-SAD Firmware ver = %s" % (drv_fw,))
      elif fw_ver < 4618:
         objMsg.printMsg("Turn OFF RFWD. Firmware ver = %s" % (fw_ver,))
         self.CCV_Modules.__setitem__(self.CCV_Modules.index(('RFWD_1_5','CRogueFWDetect_CCV','ON')),('RFWD_1_5','CRogueFWDetect_CCV','OFF'))
      else:
         objMsg.printMsg("Turn ON RFWD. Firmware ver = %s" % (fw_ver,))

      #Set CCV version 
      self.setCCV_VersionAttr(float(CCV_VERSION))

      #Quick PCO checkout will skip CCV
      if not ConfigVars[CN].get('PRODUCTION_MODE',1) and ConfigVars[CN].get('QUICK_PCO_CHECKOUT',0):
         from Setup import CSetup
         mc_connected = CSetup().IsMCConnected()
         if DEBUG:   objMsg.printMsg("mc_connected=%s" % mc_connected)

         if not mc_connected:
            objMsg.printMsg('Quick_PCO_Checkout = 1, skip CCV')
            return

      #Force get DCM data for CCV1/2
      CCV_PN = 'NONE'
      CCV_PN = DriveAttributes.get('PART_NUM', 'NONE') #CCV1 verification based on PART_NUM

      if CCV2:
         objMsg.printMsg("CCV2 operation, get PART_NUM_SEC")
         CCV_PN = DriveAttributes.get('PART_NUM_SEC', DriveAttributes.get('PART_NUM', 'NONE')) #During Master-Child phase in period, drives may not have PART_NUM_SEC

      objMsg.printMsg("CCV Part Num = %s" % CCV_PN)
      if len(CCV_PN) != 10:
         ScrCmds.raiseException( 11049, "Invalid Part Num %s detected" % CCV_PN )

      CCustomCfg().getDriveConfigAttributes(partNum = CCV_PN, force = True, failInvalidDCM = True)

      #Start CCV1/2 sub modules
      self.ccv_summary = []

      for ccv_mod, ccv_class, status in self.CCV_Modules:
         if status == 'OFF':
            continue
         try:
            objMsg.printMsg("******** Executing %s *********" % str(ccv_mod))
            functionInst = eval(ccv_class)(self.dut, params = {})
            status = functionInst.run()
         finally:
            if status == SKIP:
               self.ccv_summary.append((ccv_mod, 'SKIP'))
            elif status == PASS:
               self.ccv_summary.append((ccv_mod, 'PASS'))
            else:
               self.ccv_summary.append((ccv_mod, 'FAIL'))
               self.print_summary() #print CCV summary before raise exception
               if ccv_mod == 'RFWD_1_5':
                  objPwrCtrl.powerCycle() #powercycle drive, else may loop forever

            del functionInst #release memory

      self.print_summary() #print CCV summary
      self.dut.driveattr['CCVTEST'] = 'PASS' 

   #-------------------------------------------------------------------------------------------------------
   def print_summary(self,):
      """
      Printing CCV result summary
      """
      objMsg.printMsg("====================== CCV Result Summary  ======================")

      if len(self.ccv_summary):
         ver_num = 0
         objMsg.printMsg("\tNo\tItem\t\t\t\t\t\tResult")
         for i in self.ccv_summary:
            ver_num += 1
            self.dut.driveattr[str(i[0])] = str(i[1])
            objMsg.printMsg("\t%d.\t%s\t\t\t\t\t%s"%(ver_num,str(i[0]),str(i[1])))

      objMsg.printMsg("============================== End ==============================")

   #-------------------------------------------------------------------------------------------------------
   def trim_CCV2Attr(self,):
      """
      Update only necessary CCV2 attributes to FIS
      """
      if not CCV2:
         objMsg.printMsg("Not supposed to call trim_CCV2Attr")
         return

      tmp_dict = {}
      for attr in self.CCV2_AttrList:
         if attr in self.dut.driveattr:
            tmp_dict[attr] = self.dut.driveattr[attr]

      return tmp_dict

   #-------------------------------------------------------------------------------------------------------
   def setCCV_VersionAttr(self, ccvVersionNum):
      """
 	    Procedure sets the CCV_REVISION attribute with correct format and verifies business segment
 	    """
      import PIF
      CCV_BS_TYPE = getattr(PIF, 'CCV_BS_TYPE', 'INVALID')

      if CCV_BS_TYPE not in ['NLMCSATA', 'DTSATA', 'NBSATA', 'NLMCSAS']:
         ScrCmds.raiseException( 11049, "Invalid CCV Business segment identified: %s" % CCV_BS_TYPE )

      self.dut.driveattr['CCV_REVISION'] = '%s_%1.2f' % ( CCV_BS_TYPE, ccvVersionNum )
###########################################################################################################

class CDisableUDR_CCV(CState):
   """
      Class to disable UDR2
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut
   #-------------------------------------------------------------------------------------------------------
   def run(self, EnableUDR2 = True):
      """
      Disable UDR2 1>N24
      """
     
      CEnableUDR_CCV(self.dut).run(EnableUDR2 = False)
      return PASS
      
###########################################################################################################

class CEnableUDR_CCV(CState):
   """
      Class to enable UDR2
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut
   #-------------------------------------------------------------------------------------------------------
   def run(self, EnableUDR2 = True):
      """
      Enable UDR2 1>N23
      """
      self.oSerial = serialScreen.sptDiagCmds()
      self.oSerial.quickDiag()
      if EnableUDR2:
         objMsg.printMsg("Enabling UDR2..")
         smartParams1 = {
            'options'                  : [1, 0x23],
            'initFastFlushMediaCache'  : 0,
            'timeout'                  : 60,
            }
         self.oSerial.SmartCmd(smartParams1, dumpDEBUGResponses = 0)
      else:
         objMsg.printMsg("Disabling UDR2..")
         smartParams1 = {
            'options'                  : [0x24],
            'initFastFlushMediaCache'  : 0,
            'timeout'                  : 60,
            }
         self.oSerial.SmartCmd(smartParams1, dumpDEBUGResponses = 0)

      objMsg.printMsg("Verify UDR2 status..")
      UDR2_Status = self.oSerial.GetUDR2(getCTRL_L = True)
      if testSwitch.virtualRun:
         if EnableUDR2:
            UDR2_Status = True
         else:
            UDR2_Status = False
      objMsg.printMsg("Drive UDR2_Status = %s" % UDR2_Status)
      if UDR2_Status == True and EnableUDR2 == True:
         objMsg.printMsg("UDR2 is enabled! UDR2 verification pass!")
         return PASS
      elif UDR2_Status == False and EnableUDR2 == False:
         objMsg.printMsg("UDR2 is disabled! UDR2 verification pass!")
      else:
         objMsg.printMsg("UDR2 status is wrong.")
         ScrCmds.raiseException(14845, "UDR2 verification fail")   
         
###########################################################################################################

class CDStageActVer_CCV(CState):
   """
      Class to ensure Dual Stage Actuator is enabled on supported drives
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut
   #-------------------------------------------------------------------------------------------------------
   def run(self, Check = True):
      """
      Verify Dual Stage Actuator is turned on
      """
      self.oSerial = serialScreen.sptDiagCmds()

      objMsg.printMsg("Verifying Servo Dual Stage Actuator")
      if testSwitch.virtualRun:
         data = "Servo Symbol Table Index 0142 Value 0010E130"
      else:
         data = self.oSerial.sendDiagCmd('/5i142', printResult = True)

      match = re.search('Servo Symbol Table Index 0142 Value\s(?P<SUPPORT>[a-fA-F\d]+)', data)
      if not match:
         objMsg.printMsg("Dual stage actuator signature is not found")
         ScrCmds.raiseException(48735, "Dual Stage Actuator signature is not found")
      else:
         support = match.groupdict()['SUPPORT']
         if hex(int(support,16)) == "0xFFFFFFFF":
            objMsg.printMsg("Dual stage actuator is not supported on this drive. SKIP further verification")
            return SKIP

      objMsg.printMsg("Dual Stage Actuator is supported on drive. Verify if it is enabled")
      if testSwitch.virtualRun:
         data = "Servo Symbol Table Index 0006 RAM Data 0007"
      else:
         data = self.oSerial.sendDiagCmd('r6,2,0', printResult = True)

      match = re.search('Servo Symbol Table Index 0006 RAM Data\s(?P<ENABLED>[a-fA-F\d]+)', data)
      if not match:
         objMsg.printMsg("Dual stage actuator signature is not found")
         ScrCmds.raiseException(48735, "Dual Stage Actuator signature is not found")
      else:
         enable = match.groupdict()['ENABLED']
         if int(enable, 16) & 1: #if bit 0 is 1, actuator is turned on
            objMsg.printMsg("Dual Stage Actuator is turned on. PASS")
         else:
            objMsg.printMsg("Dual Stage Actuator is turned off. FAIL")
            ScrCmds.raiseException(48735, "Dual Stage Actuator is turned off")

      return PASS

###########################################################################################################

class CZeroPttnVer_CCV(CState):
   """
      Class for Zero pattern verification according to customer requirement
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self,):
      """
      Verify Zero pattern according to the DCM 
      If Zero_Pattern_Requirement is not defined in dcm, check for NSG min requirement - first and last 2 million LBA (1GB)
      """
      #Need to identify SDnD drive. /Aq4 cmd uses this condition to set SED option
      if testSwitch.IS_SDnD or str(self.dut.driveConfigAttrs.get('SECURITY_TYPE',(0,None))[1]).rstrip() == 'SECURED BASE (SD AND D)':
         testSwitch.IS_SDnD = 1
      
      zeroRequirement = str(self.dut.driveConfigAttrs.get('ZERO_PTRN_RQMT',(0,None))[1]).rstrip()
      if zeroRequirement in ['None','NA','']: #if not defined in dcm, check for min requirement
         objMsg.printMsg('No Zero pattern DCM Attribute detected - Applying minimum zero pattern requirement 2million LBA')
         zeroRequirement = '13'

      if testSwitch.virtualRun:
         return PASS

      if zeroRequirement == '10': #400k
         self.ZeroPattern_Ver(xferlength = 400000, Ste_Name = '400KZeroCheck')
      elif zeroRequirement == '13': #2million
         self.ZeroPattern_Ver(xferlength = 2097152, Ste_Name = '2MZeroCheck')
      elif zeroRequirement == '15': #20million
         self.ZeroPattern_Ver(xferlength = 20971520, Ste_Name = '20MZeroCheck')
      elif zeroRequirement == '20': #full pack
         self.FullPackZeroPattern_Ver()

      return PASS

   #-------------------------------------------------------------------------------------------------------
   def ZeroPattern_Ver(self, xferlength = 20971520, Ste_Name = 'C20MZeroCheck'):
      """
      Generalized zero pattern verification method
      """
      sctCnt = 0x800
      if not testSwitch.NoIO:
         objPwrCtrl.powerCycle()
      result = ICmd.ZeroCheck(0, xferlength - 1, sctCnt)
      objMsg.printMsg('First %s LBA Zero check result: %s' % (Ste_Name, result))
      if result['LLRET'] != OK:
         ScrCmds.raiseException(14723, "%s Zero Check - Failed to verify Zero Pattern on first LBAs" % Ste_Name)

      maxLBA = int(ICmd.GetMaxLBA()['MAX48'],16)-1
      result = ICmd.ZeroCheck(maxLBA - xferlength + 1, maxLBA, sctCnt)
      objMsg.printMsg('Last %s LBA Zero check result: %s' % (Ste_Name, result))
      if result['LLRET'] != OK:
         ScrCmds.raiseException(14723, "%s Zero Check - Failed to verify Zero Pattern on last LBAs" % Ste_Name)   

   #-------------------------------------------------------------------------------------------------------
   def FullPackZeroPattern_Ver(self):
      """
      Full pack zero pattern verification method
      """
      sctCnt = 0x800
      if not testSwitch.NoIO:
         objPwrCtrl.powerCycle()
      maxLBA = int(ICmd.GetMaxLBA()['MAX48'],16)-1
      result = ICmd.ZeroCheck(0, maxLBA, sctCnt)
      objMsg.printMsg('Full Pack Zero check result: %s' %result)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(14723, "Full Pack Zero Check - Failed to verify Zero Pattern")

###########################################################################################################

class CRListVer_CCV(CState):
   """
      Class that will check zero Reassigned sector list for Apple customer
      RListLimit = 0
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

      seqNum,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
      self.dut.dblData.Tables('P000_DEFECTIVE_PBAS').addRecord({ 
                           'SPC_ID'          : 2,
                           'OCCURRENCE'      : occurrence,
                           'SEQ'             : seqNum, #State seq # in CCV operation
                           'TEST_SEQ_EVENT'  : testSeqEvent, #Similar to Occurance
                           'NUMBER_OF_PBAS'  : reassignData['NUMBER_OF_TOTALALTS'],
                           'RLIST_SECTORS'   : rListSectors,
                           'RLIST_WEDGES'    : rListWedges,
                           })

      objMsg.printDblogBin(self.dut.dblData.Tables('P000_DEFECTIVE_PBAS'))

      if Check == True and hasattr(TP,'CHK_DEFECTIVE_PBAS'):
         if self.appleDetect():
            objMsg.printMsg("Apple drive. Checking TP.CHK_DEFECTIVE_PBAS=%s" % TP.CHK_DEFECTIVE_PBAS)
            tabledata = self.dut.dblData.Tables('P000_DEFECTIVE_PBAS').tableDataObj()
            for key in TP.CHK_DEFECTIVE_PBAS:
               for tab in tabledata:
                  if tab.has_key(key) and (int(tab[key]) > int(TP.CHK_DEFECTIVE_PBAS[key])):
                     ScrCmds.raiseException(13456, 'Fail SMART Glist/Rlist/Alt list')

      if self.params.get('FAIL_NEW_DEFECTS', False):
         if reassignData['NUMBER_OF_TOTALALTS'] > 0 or \
            rListSectors > 0 or \
            rListWedges > 0:
            ScrCmds.raiseException(10506,  "Drive failed for grown defects!")
      else:
         objMsg.printMsg("FAIL_NEW_DEFECTS param is not defined. Skip checking R-list")

      return PASS

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

class CSMARTThrVer_CCV(CState):
   """
      Class that performs SMART Threshold verification (/1N2). 
      Based on class CVerifySMART in GIO module
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)
      self.oSerial = serialScreen.sptDiagCmds()
      self.errorcode = 0
      self.Status = OK

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      """
      Utility verify SMART
      """
      sptCmds.enableDiags()
      data = self.oSerial.sendDiagCmd('/1N2') #Update SMART

      if self.Status == OK:
         if not testSwitch.virtualRun:
            res = self.oSerial.sendDiagCmd('N2')
         else:
            res = "SMART_THRESHOLD_NOT_EXCEEDED_LBA_KEY:C24F00"
         if res: 
            self.Status = OK
         objMsg.printMsg('SmartReturnStatus Data=%s' % str(res))
         data = {'LBA':0}
         data['LBA'] = re.split('LBA_KEY:',res)[1][:6]

      if self.Status == OK:
         objMsg.printMsg('Smart Verify passed!')
         if data.has_key('LBA') != 0:
            data['CYL'] = int(data['LBA'],16) >> 8
            objMsg.printMsg('SmartReturnStatus LBA shifted 8=%d(0x%X)' % (data['CYL'], data['CYL']))
            cyl = int(data['CYL'])
            cyl_low = cyl & 0xff
            cyl_high = cyl >> 8
         if data.has_key('CYL') == 0:
            objMsg.printMsg('SMART Verify failed! SmartReturnStatus missing data(CYL). ' % self.Status)
            failure = 'Fin DST Thres'
            self.Status = FAIL
            self.errorcode = 12378
         else:
            cyl = int(data['CYL'])
            cyl_low = cyl & 0xff
            cyl_high = cyl >> 8
      else:
         objMsg.printMsg('Smart Verify failed!')
         failure = 'IDT Verify Smart'
         self.errorcode = 13061

      if self.Status == OK:
         if (cyl_low == 0xf4) and (cyl_high == 0x2c):
            objMsg.printMsg("SMART Verify failed (threshold exceeded): Cyl=0x2CF4")
            objMsg.printMsg('Serious failure mode, no reruns allowed!')
            failure = 'Fin DST Thres'
            self.Status = FAIL
            self.errorcode = 12378

      if self.Status == OK:
         if data['LBA'] == 'C24F00':
            objMsg.printMsg('SMART Verify passed (thresholds not exceeded):Cyl=0xC24F')
         else:
            objMsg.printMsg("SMART Verify failed (invalid Cyl): not 0x2CF4 or 0xC24F")
            failure = 'Fin DST Thres'
            self.Status = FAIL
            self.errorcode = 12378

      if self.Status != OK:
         objMsg.printMsg('Smart Threshold verification failed!')
         if not testSwitch.virtualRun:
            ScrCmds.raiseException(self.errorcode, 'SMART_THRESHOLD_VERIFICATION Failed' )

      return PASS

###########################################################################################################

class CSMARTLogsAttrsVer_CCV(CState):
   """
      Class that checks Pending List, Grown Defect List, Critical Event List and Smart Attributes.
      CheckSmartLogs --
         PListLimit = 0, GListLimit = 0, CELimit = 0
      CheckSmartAttr(Limit = 0)-- 
         Attr 5      Retired Sector Count
         Attr 184    IOEDC
         Attr 197    Pending Sparing Count
         Attr 198    Uncorrectable Sector Count
         Byte 410    Retired Sector Count when last Smart Reset
         Byte 412    Pending Spare Count when last Smart Reset

   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)
      self.oSerial = serialScreen.sptDiagCmds()
      self.GListLimit = 0
      self.PListLimit = 0
      self.RListLimit = 0
      self.IOEDCLimit = 0
      self.A198Limit = 0
      self.errorcode = 0

      UNDEF = 'UNDEF'
      self.LogList = [0xA1, 0xA8, 0xA9] #list of SMART logs to be checked
      self.Status = OK

   #-------------------------------------------------------------------------------------------------------
   def run(self, check=ON):
      #ScrCmds.raiseException(13053, 'SMART_LOGS_VERIFICATION Failed' )
      self.checkSmartLogs(self.LogList,check)
      self.checkSmartAttr(check)

      return PASS
   #-------------------------------------------------------------------------------------------------------
   def checkSmartLogs(self, LogList, check=ON):
      """
        Utility check SMART Logs
        #With Reference to SoonYak#
        Log 0xA8 - The raw field of Smart attribute #5 (bytes[1:0]) records the number of reallocation,
                   which should match the number of entries in log A8.
        Log 0xA9 - The raw field of Smart attribute #197 (bytes[1:0]) records the number of pending spare count,
                   which should match the number of entries in log A9.
        Log 0xA7 - From revision 278 of Yarra programme onwards, you can use serial port diagnostic mode level '1';
                   'N18' command to retrieve log A7 entry count.
        Log 0xA1 - From 1>N8 command.
      """

      objMsg.printMsg("Check SMART Logs")
      sptCmds.enableDiags()

      self.oSerial.sendDiagCmd('/1N2', printResult = True)  #Update SMART

      CriticalEventLogData = self.oSerial.sendDiagCmd('/1N5', printResult = True)
      CELogAttrs = self.oSerial.parseCEAttributes(CriticalEventLogData)
      if testSwitch.virtualRun:
         GList_Entries = 0
         PList_Entries = 0
      else:
         GList_Entries = CELogAttrs['5']['raw'] & 0xFFFF #Smart attribute #5 (bytes[1:0]) -> G-List Entry
         PList_Entries = CELogAttrs['C5']['raw'] & 0xFFFF #Smart attribute #197 (bytes[1:0]) -> P-List Entry

      objMsg.printMsg('GList_Entries=%s PList_Entries=%s' % (GList_Entries, PList_Entries))
      seqNum,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
      self.dut.dblData.Tables('P_GROWN_DEFECT_LIST').addRecord(
         {
         'SPC_ID' : getattr(TP,"spcid_SmartDefectList",{}).get(self.dut.nextOper,self.dut.objSeq.curRegSPCID),
         'OCCURRENCE': occurrence,
         'SEQ' : seqNum,
         'TEST_SEQ_EVENT': testSeqEvent,
         'PBA':0,
         'RW_FLAGS':0,
         'ERR_LENGTH': GList_Entries
         })

      self.dut.dblData.Tables('P_PENDING_DEFECT_LIST').addRecord(
         {
         'SPC_ID' : getattr(TP,"spcid_SmartDefectList",{}).get(self.dut.nextOper,self.dut.objSeq.curRegSPCID),
         'OCCURRENCE': occurrence,
         'SEQ' : seqNum,
         'TEST_SEQ_EVENT': testSeqEvent,
         'TOTAL_DFCTS_DRIVE': PList_Entries
         })

      if 0xA8 in LogList:
         objMsg.printMsg('Number of Events in GList:%d' % GList_Entries)
         if GList_Entries > 0:
            objMsg.printMsg('GList Limit:%d' % self.GListLimit)
            if GList_Entries > self.GListLimit:
               objMsg.printMsg('GList Entries Exceeds Limit!')
               if check == ON:
                  failure = 'IDT Smart attribute #5 (bytes[1:0])'
                  self.Status = FAIL
                  self.errorcode = 13055

      if 0xA9 in LogList:
         objMsg.printMsg('Number of Events in PList:%d' % PList_Entries)
         if PList_Entries > 0:
            objMsg.printMsg('PList Limit:%d' % self.PListLimit)
            if PList_Entries > self.PListLimit:
               objMsg.printMsg('PList Entries Exceeds Limit!')
               if check == ON:
                  failure = 'IDT Smart attribute #197 (bytes[1:0])'
                  self.Status = FAIL
                  self.errorcode = 13059

      if 0xA7 in LogList:
         sectors, wedges = self.oSerial.dumpRList()
         numOfEvents = sectors + wedges
         objMsg.printMsg('Number of Events in RList:%d' % numOfEvents)
         if numOfEvents > 0:
            objMsg.printMsg('RList Limit:%d' % self.RListLimit)
            if numOfEvents > self.RListLimit:
               objMsg.printMsg('RList Entries Exceeds Limit!')
               if check == ON:
                  failure = 'IDT 1>N18'
                  self.Status = FAIL
                  self.errorcode = 13154

      if 0xA1 in LogList:
         CELogData, summaryData, ceData = self.oSerial.getCriticalEventLog()
         EventList = [0x2,0x3,0x7,0xB]   # from GIO ReliSmart.py
         ceEventSummary = {}
         for item in ceData:
            EventID = int(re.split(' ',item['Type'])[0].strip(), 16)
            if EventID in EventList:
               ceEventSummary[EventID] =  ceEventSummary.get(EventID,0) + 1
         numOfCriticalEvents = sum(ceEventSummary.values())

         AllEventList = ceData
         numOfEvents = len(AllEventList)
         objMsg.printMsg('Number of Events in CE Log:%d' % numOfEvents)
         objMsg.printMsg('CE Log Entries %s: %s' % (EventList,ceEventSummary))
         objMsg.printMsg('Number of Critical Events in CE Log:%d' % numOfCriticalEvents)
         if numOfCriticalEvents > 0:
             objMsg.printMsg('CE Log Entries: %s' % AllEventList)
             objMsg.printMsg('CE Log Entries Exceeds Limit: Event Type (2,3,7 or B) exists!')
             if check == ON:
                failure = 'IDT CE LOG'
                self.Status = FAIL
                self.errorcode = 13053

      if check == ON:
         if self.Status == OK:
            objMsg.printMsg('Smart Logs Check passed!')
         else:
            objMsg.printMsg('Smart Logs Check failed!')
            if not testSwitch.virtualRun:
               ScrCmds.raiseException(self.errorcode, 'SMART_LOGS_VERIFICATION Failed' )

   #-------------------------------------------------------------------------------------------------------
   def checkSmartAttr(self, check=ON):
      """
      SMART Attribute - Retrieve the Smart attribute data from FileID #137 -> T>r137,3,,,,100.
      Utility check SMART Attribute
         Attr 5      Retired Sector Count
         Attr 184    IOEDC
         Attr 197    Pending Sparing Count
         Attr 198    Uncorrectable Sector Count
         Byte 410    Retired Sector Count when last Smart Reset
         Byte 412    Pending Spare Count when last Smart Reset
      """
      objMsg.printMsg("Check SMART Attributes")
      if ConfigVars[CN].has_key('SMART CHECK B410') and ConfigVars[CN]['SMART CHECK B410'] != UNDEF and ConfigVars[CN]['SMART CHECK B410'] == 'OFF':
         Check_B410 = OFF

      if ConfigVars[CN].has_key('SMART CHECK B412') and ConfigVars[CN]['SMART CHECK B412'] != UNDEF and ConfigVars[CN]['SMART CHECK B412'] == 'OFF':
         Check_B412 = OFF

      if ConfigVars[CN].has_key('SMART CHECK IOEDC') and ConfigVars[CN]['SMART CHECK IOEDC'] != UNDEF and ConfigVars[CN]['SMART CHECK IOEDC'] == 'ON':
         Check_IOEDC = ON

      if ConfigVars[CN].has_key('SMART CHECK A198') and ConfigVars[CN]['SMART CHECK A198'] != UNDEF and ConfigVars[CN]['SMART CHECK A198'] == 'ON':
         Check_A198 = ON

      MaxRetry = 2
      for i in xrange(MaxRetry):
         try:
            smartData = ''
            self.oSerial.sendDiagCmd('/1N2', printResult = True) #Update SMART
            
            if testSwitch.virtualRun:
               data = """
                        /Tr137,3,,,200,100
                        File Volume 3
                        File ID 137
                        File Copy Number 0
                        File Descriptor FD382137
                        File Size 00001000
                        Byte Offset 00000000
                        Bytes to read 00000200
                        Offset   00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
                        00000000 0A 00 01 0F 00 64 64 00 00 00 00 00 00 00 03 03
                        00000010 00 64 64 00 00 00 00 00 00 00 04 32 00 64 64 00
                        00000020 00 00 00 00 00 00 05 33 00 64 64 00 00 00 00 00
                        00000030 00 00 07 0F 00 64 FD 00 00 00 00 00 00 00 09 32
                        00000040 00 64 64 00 00 00 00 6F 81 00 0A 13 00 64 64 00
                        00000050 00 00 00 00 00 00 0C 32 00 64 64 00 00 00 00 00
                        00000060 00 00 B8 32 00 64 64 00 00 00 00 00 00 00 BB 32
                        00000070 00 64 64 00 00 00 00 00 00 00 BC 32 00 64 FD 00
                        00000080 00 00 00 00 00 00 BD 3A 00 64 64 00 00 00 00 00
                        00000090 00 00 BE 22 00 4B 4B 19 00 00 19 00 00 00 BF 32
                        000000A0 00 64 64 00 00 00 00 00 00 00 C0 32 00 64 64 00
                        000000B0 00 00 00 00 00 00 C1 32 00 64 64 00 00 00 00 00
                        000000C0 00 00 C2 22 00 19 28 19 00 00 00 19 00 00 C5 12
                        000000D0 00 64 64 00 00 00 00 00 00 00 C6 10 00 64 64 00
                        000000E0 00 00 00 00 00 00 C7 3E 00 C8 FD 00 00 00 00 00
                        000000F0 00 00 F0 00 00 64 FD 00 00 00 00 DA 10 00 F1 00
                        00000100 00 64 FD 00 00 00 00 00 00 00 F2 00 00 64 FD 00
                        00000110 00 00 00 00 00 00 FE 32 00 64 64 00 00 00 00 00
                        00000120 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
                        00000130 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
                        00000140 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
                        00000150 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
                        00000160 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 73
                        00000170 03 00 01 00 01 84 02 00 00 00 00 00 00 00 00 00
                        00000180 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
                        00000190 00 00 00 00 00 00 00 00 00 01 00 00 00 00 00 00
                        000001A0 00 00 00 00 00 00 00 00 60 40 E9 3A 07 00 00 00
                        000001B0 00 00 00 00 01 00 00 00 00 00 00 00 00 00 00 00
                        000001C0 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
                        000001D0 01 00 00 00 00 00 00 00 00 00 00 00 48 00 08 00
                        000001E0 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 25
                        000001F0 00 00 00 00 00 00 00 00 00 00 03 18 00 00 00 21 """
            else:
               data = self.oSerial.sendDiagCmd('/Tr137,3,,,200,100', printResult = True)
         
            rawdata = data.splitlines()
            for line in rawdata:
               dataspt = line.strip().replace(" ",'')
               if len(dataspt) == 40:
                  smartData += dataspt[8:]
            if len(smartData)/2 <> 512:
               if not testSwitch.virtualRun:
                   ScrCmds.raiseException(11044, "smartData is not 512 Bytes!" )
            break
         except:
            if i < MaxRetry - 1:
               objMsg.printMsg("smartData failed. Traceback=%s" % traceback.format_exc())
               objPwrCtrl.powerCycle(baudRate = Baud38400)
               sptCmds.enableDiags()
            else:
               raise
      smartData = binascii.unhexlify(smartData)
      if len(smartData) > 0:
         objMsg.printMsg('Smart Attribute File 137 Data: \r%s' %smartData)
         self.Status = OK
      else:
         self.Status = FAIL

      if self.Status == OK:
         smartAttr = CSmartAttributes(smartData)

         smartAttr.decodeAttribute(5)
         A5_RetdSectCnt = smartAttr.Attribute['RawValue'] & 0xFFFF #Bytes [1:0]
         smartAttr.decodeAttribute(197)
         A197_PendSpareCnt = smartAttr.Attribute['RawValue'] & 0xFFFF #Bytes [1:0]
         smartAttr.decodeAttribute(198)
         A198_UncorrSectCnt = smartAttr.Attribute['RawValue']
         smartAttr.decodeAttribute(184)
         A184_IOEDC = smartAttr.Attribute['RawValue']

         # Read direct from buffer
         B410_RepRetdSectCnt = (ord(smartAttr.buffer[410]) & 0xFF) + ((ord(smartAttr.buffer[411]) & 0xFF) << 8)
         B412_RepPendSpareCnt = (ord(smartAttr.buffer[412]) & 0xFF) + ((ord(smartAttr.buffer[413]) & 0xFF) << 8)

         objMsg.printMsg('Retired Sector Count(Attr5): %d' % A5_RetdSectCnt)
         objMsg.printMsg('Reported IOEDC Errors(Attr184): %d' % A184_IOEDC)
         objMsg.printMsg('Pending Spare Count(Attr197): %d' % A197_PendSpareCnt)
         objMsg.printMsg('Uncorrectable Sector Count(Attr198): %d' % A198_UncorrSectCnt)
         objMsg.printMsg('Spare Count(B410) when last SmartReset: %d' % B410_RepRetdSectCnt)
         objMsg.printMsg('Pending Spare Count(B412) when last SmartReset: %d' % B412_RepPendSpareCnt)

         #Parsing SMART attributes
         smartAttr.decodeAttribute(1)     # Raw Error Rate
         A1_RAW = smartAttr.Attribute['RawValue']
         objMsg.printMsg('Raw Error Rate(Attr1): %d, 0x%X' % ((A1_RAW & 0xFFFFFFFF), A1_RAW))

         smartAttr.decodeAttribute(188)     # Cmd Timeout
         A188_CmdTimeout = smartAttr.Attribute['RawValue']
         objMsg.printMsg('Cmd Timeout Count >7.5s (Attr188): %d, 0x%X' % ((A188_CmdTimeout & 0xFFFF00000000), A188_CmdTimeout))

         smartAttr.decodeAttribute(195)     # ECC OTF
         A195_ECCOTF = smartAttr.Attribute['RawValue']
         objMsg.printMsg('ECC On-The-Fly Count(Attr195): %d, 0x%X' % ((A195_ECCOTF & 0xFFFFFFFF), A195_ECCOTF))

         smartAttr.decodeAttribute(199)     # UDMA CRC Error Count
         A199_UDMACRCErrCnt = smartAttr.Attribute['RawValue']
         objMsg.printMsg('UDMA ECC Error Count(Attr199): %d, 0x%X' % ((A199_UDMACRCErrCnt & 0xFFFFFFFF), A199_UDMACRCErrCnt))

         B422_NumRAWReWrt = (ord(smartAttr.buffer[422]) & 0xFF) + ((ord(smartAttr.buffer[423]) & 0xFF) << 8)
         B438_SysWrtFailCnt = (ord(smartAttr.buffer[438]) & 0xFF) + ((ord(smartAttr.buffer[439]) & 0xFF) << 8)
         objMsg.printMsg('Number of ReadAfterWrite(422) need Rewrite: %d' % B422_NumRAWReWrt)
         objMsg.printMsg('Number of System Write Failures(438): %d' % B438_SysWrtFailCnt)

         #Check SMART attributes against the spec
         if (A5_RetdSectCnt > self.GListLimit):
            objMsg.printMsg('Retired Sector Count(Attr5) exceeded Glist limit')
            if check == ON:
               failure = 'IDT A8 LOG'
               self.Status = FAIL
               self.errorcode = 13055

         if (A197_PendSpareCnt > self.PListLimit):
            objMsg.printMsg('Pending Spare Count(Attr197) exceeded Plist limit')
            if check == ON:
               failure = 'IDT A9 LOG'
               self.Status = FAIL
               self.errorcode = 13059

         if (A184_IOEDC > self.IOEDCLimit):
            objMsg.printMsg('Reported IOEDC Errors(Attr184) exceeded IOEDC limit')
            if check == ON:
               failure = 'IDT A184 IOEDC'
               self.Status = FAIL
               self.errorcode = 13150

         if (A198_UncorrSectCnt > self.A198Limit):
            objMsg.printMsg('Uncorrectable Sector Count(Attr198) exceeded A198 limit')
            if check == ON:
               failure = 'IDT A198 USC'
               self.Status = FAIL
               self.errorcode = 13155

         if (B410_RepRetdSectCnt > self.GListLimit):
            objMsg.printMsg('Spare Count(410) when last SmartReset exceeded Glist limit')
            if check == ON:
               failure = 'IDT A8 LOG'
               self.Status = FAIL
               self.errorcode = 13055

         if (B412_RepPendSpareCnt > self.PListLimit):
            objMsg.printMsg('Pending Spare Count(412) when last SmartReset exceeded Plist limit')
            if check == ON:
               failure = 'IDT A9 LOG'
               self.Status = FAIL
               self.errorcode = 13059

      if check == ON:
         if self.Status == OK:
            objMsg.printMsg('Smart Attribute Check passed!')
         else:
            objMsg.printMsg('Smart Attribute Check failed!')
            if not testSwitch.virtualRun:
               ScrCmds.raiseException(self.errorcode, 'SMART Attribute check Failed' )

###########################################################################################################

class CDOSVer_CCV(CState):
   """
      Class to check Directed Offline Scan (DOS) is enabled on drive
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self, ):
      """
      Verify drive if DOS Enable
      """
      objMsg.printMsg('Verify drive if DOS Enable.')
      oSerial = serialScreen.sptDiagCmds()

      if testSwitch.FE_0222955_470833_P_DOS_CHECK_NEED_TO_SCAN_ONLY:
         dosVersion = 3
         sptCmds.gotoLevel('T')
         try:
            if testSwitch.virtualRun:
               data = """
                  Byte:0135:       DOSNeedToScanThreshold = 40
                  """
            else:
               data = sptCmds.sendDiagCmd('''F"DOSNeedToScanThreshold"''', printResult = True) #dos 3 or single track dos
            if "Invalid Diag Cmd Parameter" in data:
               raise KeyError, "Not DOS3 or Single track DOS"
         except KeyError:
            dosVersion = 1
            data = sptCmds.sendDiagCmd('''F"DOSATINeedToScanThreshold"''', printResult = True)
            if "Invalid Diag Cmd Parameter" in data:
               objMsg.printMsg("Unable to detect DOS type!")
               ScrCmds.raiseException(10150, "DOS Check Failure: Unable determine DOS type")


         if dosVersion == 3:
            lbaXlatePattern = '\S+DOSNeedToScanThreshold=(?P<DOS_STATUS>[a-fA-F\d]+)'
         else:
            lbaXlatePattern = '\S+\s+DOSATINeedToScanThreshold\s=\s(?P<DOS_STATUS>[a-fA-F\d]+)'

         data = data.replace("\n","")
         data = data.replace(' ', '')

         match = re.search(lbaXlatePattern, data)

         if match:
            tempDict = match.groupdict()
            DOSdict =  oSerial.convDictItems(tempDict, int, [16,])

            dosEnabled = DOSdict['DOS_STATUS'] > 0

            if dosEnabled:
               if dosVersion == 3:
                  objMsg.printMsg("DOSNeedToScanThreshold = 0x%s DOS verification PASS!!!!"%dosEnabled)
               else:
                  objMsg.printMsg("DOSATINeedToScanThreshold = 0x%s DOS verification PASS!!!!"%dosEnabled)
            else:
               objMsg.printMsg("DOS is DISABLED!!!!")
               ScrCmds.raiseException(10150, "DOS Check Failure: Unable determine DOS status")
         else:
            if dosVersion == 3:
               objMsg.printMsg("DOS check DOSNeedToScanThreshold return data: %s" % (str(data)))
            else:
               objMsg.printMsg("DOS check DOSATINeedToScanThreshold return data: %s" % (str(data)))
            ScrCmds.raiseException(10150, "DOS Check Failure: Unable determine DOS status")
      else:
         dosVersion = 3
         sptCmds.gotoLevel('T')
         try:
            if testSwitch.virtualRun:
                data1 = """
                        Byte:0130:       DOSOughtToScanThreshold = 00 08
                        """
            else:
               data1 = sptCmds.sendDiagCmd('''F"DOSOughtToScanThreshold"''', printResult = True) #dos 3 or single track dos
            if "Invalid Diag Cmd Parameter" in data1:
               raise KeyError, "Not DOS3 or Single track DOS"
         except KeyError:
            dosVersion = 1
            data1 = sptCmds.sendDiagCmd('''F"DOSATIOughtToScanThreshold"''', printResult = True)
            if "Invalid Diag Cmd Parameter" in data1:
               objMsg.printMsg("Unable to detect DOS type!")
               ScrCmds.raiseException(10150, "DOS Check Failure: Unable determine DOS type")
   
         if dosVersion == 3:
            lbaXlatePattern1 = '\S+\s+DOSOughtToScanThreshold\s=\s(?P<DOS1_STATUS>[a-fA-F\d *]+)'
            lbaXlatePattern2 = '\S+\s+DOSNeedToScanThreshold\s=\s(?P<DOS2_STATUS>[a-fA-F\d *]+)'
         else:
            lbaXlatePattern1 = '\S+\s+DOSATIOughtToScanThreshold\s=\s(?P<DOS1_STATUS>[a-fA-F\d]+)'
            lbaXlatePattern2 = '\S+\s+DOSATINeedToScanThreshold\s=\s(?P<DOS2_STATUS>[a-fA-F\d]+)'
         data1 = data1.replace("\n","")
         match1 = re.search(lbaXlatePattern1, data1)
   
         if not testSwitch.virtualRun:
            if dosVersion == 3:
               data2 = sptCmds.sendDiagCmd('''F"DOSNeedToScanThreshold"''', printResult = True)
            else:
               data2 = sptCmds.sendDiagCmd('''F"DOSATINeedToScanThreshold"''', printResult = True)
         else:
            data2 = """
                  Byte:0140:       DOSNeedToScanThreshold = 00 10
                  """
         data2 = data2.replace("\n","")
         match2 = re.search(lbaXlatePattern2, data2)
   
         if match1 and match2:
            tempDict1 = match1.groupdict()
            tempDictVal1 = tempDict1['DOS1_STATUS'].replace(" ","")     # join two separate bytes
            tempDict1.update({'DOS1_STATUS':tempDictVal1})
            DOSdict1 =  oSerial.convDictItems(tempDict1, int, [16,])
            tempDict2 = match2.groupdict()
            tempDictVal2 = tempDict2['DOS2_STATUS'].replace(" ","")     # join two separate bytes
            tempDict2.update({'DOS2_STATUS':tempDictVal2})
            DOSdict2 =  oSerial.convDictItems(tempDict2, int, [16,])
   
            dosEnabled = DOSdict1['DOS1_STATUS'] > 0 and DOSdict2['DOS2_STATUS'] > 0
   
            if dosEnabled:
               if dosVersion == 3:
                  objMsg.printMsg("DOSOughtToScanThreshold = %s and DOSNeedToScanThreshold = %s... DOS verification PASS!!!!" %(hex(DOSdict1['DOS1_STATUS']), hex(DOSdict2['DOS2_STATUS'])))
               else:
                  objMsg.printMsg("DOSATIOughtToScanThreshold = %s and DOSATINeedToScanThreshold = %s... DOS verification PASS!!!!" %(hex(DOSdict1['DOS1_STATUS']), hex(DOSdict2['DOS2_STATUS'])))
            else:
               objMsg.printMsg("DOS is DISABLED!!!!")
               ScrCmds.raiseException(10150, "DOS Check Failure: Unable determine DOS status")
         else:
            if dosVersion == 3:
               objMsg.printMsg("DOS check DOSOughtToScanThreshold and DOSNeedToScanThreshold return data: %s and %s" % (str(data1), str(data2)))
            else:
               objMsg.printMsg("DOS check DOSATIOughtToScanThreshold and DOSATINeedToScanThreshold return data: %s and %s" % (str(data1), str(data2)))
            ScrCmds.raiseException(10150, "DOS Check Failure: Unable determine DOS status")

      objMsg.printMsg("DOS of this drive is ENABLED. Verify PASS!!!")
      return PASS

###########################################################################################################

class CPOISVer_CCV(CState):
   """
      Class to check POIS status on drive
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      """
      Verify POIS value between drive and attribute.
      """
      objMsg.printMsg('POIS verification')
      if not testSwitch.NoIO:
         objPwrCtrl.powerCycle()

      oIdentifyDevice = CIdentifyDevice(sp_force = True)
      poisEnabled = True

      if oIdentifyDevice.Is_POIS_Supported():
         poisEnabled = oIdentifyDevice.Is_POIS()
      else:
         poisEnabled = False
         objMsg.printMsg("POIS not supported")

      #default to not correct
      correctConfig = False

      if (self.dut.driveConfigAttrs.get('POWER_ON_TYPE', ('=', 0) )[1] == 'PWR_ON_IN_STDBY' ):
         if poisEnabled:
            correctConfig = True
      else:
         #case where POWER_ON_TYPE != PWR_ON_IN_STDBY in cca
         if not poisEnabled:
            #only correct if poise is not enabled
            correctConfig = True

      if correctConfig or testSwitch.virtualRun:
         objMsg.printMsg("POIS Setting is correct.")
      else:
         objMsg.printMsg("POIS Setting is incorrect.")
         ScrCmds.raiseException(13454, "Incorrect POIS setting on drive!")

      return PASS

###########################################################################################################

class CZAPVer_CCV(CState):
   """
      Class to ensure Zero Acceleration Profile (ZAP) is enabled
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self, ):
      """
      Verify drive if ZAP turn on
      """
      objMsg.printMsg('Verify drive if ZAP turn on.')
      sptCmds.enableDiags()

      lbaXlatePattern = 'ZAP Control:\s(?P<ZAP_Status>.{24})'
      sptCmds.gotoLevel('5')

      if not testSwitch.virtualRun:
         data = sptCmds.sendDiagCmd('d', printResult = True)
      else:
         data = """
               ZAP Control: Read/Write ZAP from disc
               """

      data = data.replace("\n","")
      match = re.search(lbaXlatePattern, data)
      if match:
         tempDict = match.groupdict()
         objMsg.printMsg("ZAP status = %s" % tempDict['ZAP_Status'])

         if tempDict['ZAP_Status'] == 'Read/Write ZAP from disc':
            objMsg.printMsg("ZAP turn on...Verify PASS!!!!")
         else:
            objMsg.printMsg("ZAP turn off...Verify FAIL!!!!")
            ScrCmds.raiseException(10150, "ZAP verification FAIL!!!!")
      else:
         objMsg.printMsg("ZAP turn off...Verify FAIL!!!!")
         ScrCmds.raiseException(10150, "ZAP verification FAIL!!!!")

      objMsg.printMsg('ZAP of this drive turn on. Verify PASS!!!')
      return PASS

###########################################################################################################

class CSATASpeedVer_CCV(CState):
   """
     Verify current SATA speed is according to customer requirement (default = max supported speed)
     Use Identify Device Word 77 to determine the current signal speed, Word 76 to determine what the f/w supports,
   """

   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params=[]):
      self.dut = dut
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):

      objMsg.printMsg("Verifying SATA speed")

      screens = []
      chars = 3
      #Check whether dcm has SD1, SD2 customer requirement
      for name in self.dut.driveConfigAttrs.keys():
         if name == 'CUST_TESTNAME':
            value = self.dut.driveConfigAttrs[name][1]
            screens = [value[i*chars:(i*chars )+chars] for i in xrange(len(value)/chars)]
            break

      maxCapableSpeed = self.getATACapability() #ID word 77
      if testSwitch.NoIO:
         objMsg.printMsg("In serial mode, current negotiated ATA speed is not applicable")
      else:
         objPwrCtrl.powerCycle()
         oIdentifyDevice = CIdentifyDevice()
         currNegoSpeed = oIdentifyDevice.getATASpeed() #ID word 76
         objMsg.printMsg("In IO mode, current negotiated ATA speed: %s" %currNegoSpeed)
      
      if testSwitch.virtualRun:
         objMsg.printMsg("Virtual Execution: Drive is at maximum capable SATA speed")
         return PASS

      if 'SD1' in screens:
         reqSpeed = 1.5
         objMsg.printMsg("Customer requested ATA speed: %s Gbps" % reqSpeed)
         if maxCapableSpeed == reqSpeed:
            objMsg.printMsg("ATA speed locked down to customer requirement, PASS")
         else:
            ScrCmds.raiseException(12412, "ATA speed is not according to customer requirement, FAIL")
      elif 'SD2' in screens:
         reqSpeed = 3.0
         objMsg.printMsg("Customer requested ATA speed: %s Gbps" % reqSpeed)
         if maxCapableSpeed == reqSpeed:
            objMsg.printMsg("ATA speed locked down to customer requirement, PASS")
         else:
            ScrCmds.raiseException(12412, "ATA speed is not according to customer requirement, FAIL")
      else:
         reqSpeed = 6.0 #Default SATA speed
         objMsg.printMsg("Maximum supported ATA speed is requested: %s Gbps" % reqSpeed)
         if maxCapableSpeed == reqSpeed:
            objMsg.printMsg("Current ATA speed at maximum supported ATA speed, PASS")
         else:
            ScrCmds.raiseException(12412, "Current ATA speed is not at maximum supported ATA speed, FAIL")

      return PASS

   #-------------------------------------------------------------------------------------------------------
   def getATACapability(self):
      """
      Identify Word 77 return the supported SATA speed
      """

      speedLookup = [
               (6.0, 8), #6.0Gbs
               (3.0, 4), #3.0Gbs
               (1.5, 2), #1.5Gbs
               ]

      capableATASpeed = self.dut.IdDevice['SATA Ver'] #word 77
      objMsg.printMsg("Identify Device word 77 = %s" % capableATASpeed)

      for rate, bitmask in speedLookup:
         if (capableATASpeed & bitmask):
            objMsg.printMsg("Serial ATA capabilities %s Gbps" % rate)
            return rate
         
      return 0

###########################################################################################################

class CWWNVer_CCV(CState):
   """
      Class to verify WWN value between drive and attribute.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params   = params
      depList       = []
      self.dut      = dut
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if not testSwitch.virtualRun:
         if not testSwitch.NoIO:
            objPwrCtrl.powerCycle(5000,12000,10,30, ataReadyCheck = False)
         self.hdd = CIdentifyDevice(sp_force = True).ID     # get drive params
         self.wwn  = self.hdd['IDWorldWideName']       # sata_id         
      else:
         self.wwn = DriveAttributes.get('WW_SATA_ID', '5000C50011EBF574')

      self.verify(self.wwn)              # validate wwn
      return PASS

   #-------------------------------------------------------------------------------------------------------
   def verify(self, wwn64):
      """
      Function verify() - compares the decoded WWN data from
      word 108:111 to the drive attribute 'WW_SATA_ID'
      """

      drive_sata_id = self.validateWWN(wwn64)
      if CCV1:
         cm_sata_id = self.dut.driveattr.get('WW_SATA_ID', None)
      elif CCV2:
         cm_sata_id = self.dut.driveattr.get('WW_SATA_ID', DriveAttributes['WW_SATA_ID'])
      if drive_sata_id == cm_sata_id:
         objMsg.printMsg("WWN Readback Verification PASS...")
      else:
         objMsg.printMsg("WWN verification - drive %s cm %s" % (drive_sata_id, cm_sata_id))
         ScrCmds.raiseException(10016, "Proc Operator-XX/3F91 WWN Mismatch")

   #-------------------------------------------------------------------------------------------------------
   def validateWWN( self, WWN='' ):
      msg = "Checked WWN: %s ,for "%WWN
      if len( WWN ) == 16:
         msg += "Length of 16 Chars" + '- PASS'
      else:
         msg += "Length of 16 Chars %d - FAIL"%(len(WWN))
         ScrCmds.raiseException(12411,{'MSG':'Invalid WWN Len ' + msg,
                                            'WWN_LEN':len(WWN),
                                            'WWN':WWN})

      if WWN[0] == '5':
         msg += "First Character '5' - PASS"
      else:
         msg += "First Character '5' - %s - FAIL"%WWN[0]
         ScrCmds.raiseException(12411,{'MSG':'WWN Header Check Failed ' + msg,
                                       'WWN_LEN':len(WWN),
                                       'WWN':WWN})

      lst = re.findall( '[^0-9-A-F]', WWN )
      if not len( lst ):
         msg += "HEX values - PASS"
      else:
         msg += "HEX values - %s - FAIL"%`lst`
         ScrCmds.raiseException(12411,{'MSG':'RE Hex Content failed ' + msg,
                                       'WWN_LEN':len(WWN),
                                       'WWN':WWN})
      objMsg.printMsg(msg, objMsg.CMessLvl.IMPORTANT)
      return WWN

###########################################################################################################

class CPPIDVer_CCV(CState):
   """
      Class to verify PPID value between drive and attribute.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self,):
      """
      Verify PPID value between drive and attribute.
      Skip CCV, DellPPID verification for non-Dell drives.
      """
      screens = []
      chars = 3
      #Check whether dcm has DE1 customer test
      for name in self.dut.driveConfigAttrs.keys():
         if name == 'CUST_TESTNAME':
            value = self.dut.driveConfigAttrs[name][1]
            screens = [value[i*chars:(i*chars )+chars] for i in xrange(len(value)/chars)]
            break

      if 'DE1' not in screens:
         objMsg.printMsg("*** Not Dell drive. SKIP verification ***")
         return SKIP

      #Get PPID frm drive
      objMsg.printMsg("Read Dell PPID")
      if testSwitch.virtualRun:
         drive_PPID = "SG012348543218220004A00 "
      else:
         drive_PPID = self.getPPID() # use diag. command instead of DETS cmd
      
      objMsg.printMsg("read_PPID from drive: %s" % str(drive_PPID)) 

      #Validate read_PPID length(CUST_SERIAL + CUST_REV + ' ' = 24 chars)
      '''
      if len(drive_PPID) != 24:
         objMsg.printMsg("The full PPID length is incorrect. Should be 24 characters.  Check CUST_SERIAL or CUST_REV attributes.")
         ScrCmds.raiseException(10158,"Dell PPID length is incorrect.")
      else:
         objMsg.printMsg("read_PPID length is correct: %s chars" % len(drive_PPID))
      '''

      #Get PPID from CM (During PPID write, stripped PPID is written to drive attr. So need to add back " ")
      if CCV1:
         cm_PPID = self.dut.driveattr.get('DISC_CUST_SN', None).strip() + " "
      elif CCV2:
         cm_PPID = self.dut.driveattr.get('DISC_CUST_SN', DriveAttributes['DISC_CUST_SN']).strip() + " " 

      if (drive_PPID[:23] == cm_PPID[:23]):
         objMsg.printMsg("Dell drive. PPID comparison done. PASS")
      else:
         objMsg.printMsg("Dell drive. PPID comparison done. FAIL")
         objMsg.printMsg("drive_PPID: %s cm_PPID: %s" % (drive_PPID, cm_PPID))
         ScrCmds.raiseException(10158,"Dell DeviceID comparison failed!")
     
      return PASS

   #-------------------------------------------------------------------------------------------------------
   def ReadPPID(self):
      """ 
      Command reads smart log but functionality only for PPID
      """
      oSerialICmd = Serial_ICmd(self.params, objPwrCtrl)
      oSerialICmd.CCV_SetupCommMode(sdbpForce = True)
      #Read back PPID from SMART log 0x9A
      data, error, dataBlock = DetsCommand(0x326, struct.pack('3HB',0,0x17,0,1))
      PPID = data[15:39]
      return PPID

   #-------------------------------------------------------------------------------------------------------
   def getPPID(self):
      """
      Returns Dell PPID

      F3 L>R,,,1
      DELL PPID:CN0P6R56212326240023X00
      """
      sptCmds.gotoLevel('L')
      pat = re.compile('\s*DELL PPID:*\s*(?P<PPID>[\.a-zA-Z0-9\-]*)')
      mat = pat.search(sptCmds.sendDiagCmd("R,,,1", printResult=True))
      if mat:
         return mat.groupdict().get('PPID')
      else:
         ScrCmds.raiseException(11044,"Unable to parse DellPPID info")

###########################################################################################################

class CLenovo8SVer_CCV(CState):
   """
      Class to verify Lenovo8S value between drive and attribute.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self,):
      """
      Verify Lenovo8S value between drive and attribute.
      Skip CCV, Lenovo8S verification for non-Lenovo drives. 
      """

      screens = []
      chars = 3
      #Check whether dcm has LV1 customer test
      for name in self.dut.driveConfigAttrs.keys(): 
         if name == 'CUST_TESTNAME':
            value = self.dut.driveConfigAttrs[name][1]
            screens = [value[i*chars:(i*chars )+chars] for i in xrange(len(value)/chars)]
            break

      if 'LV1' not in screens:
         objMsg.printMsg("*** Not Lenovo drive. Skip verification ***")
         return SKIP

      #Get CUST_CODE from dcm
      try:
         dcm_custSerial = self.dut.driveConfigAttrs['CUST_CODE'][1].rstrip()
      except:
         dcm_custSerial = None

      #Get Lenovo8S from CM
      if CCV1:
         cm_custSerial = self.dut.driveattr.get('CUST_SERIAL', None)
      elif CCV2:
         cm_custSerial = self.dut.driveattr.get('CUST_SERIAL', DriveAttributes['CUST_SERIAL'])
      objMsg.printMsg("cm_custSerial: %s, cm_custSerial[0:2]: %s" % (cm_custSerial, cm_custSerial[0:2])) 

      nonProductionSite = False
      if cm_custSerial[0:2] != '8S':
         nonProductionSite = True

      #Get Lenovo8S frm drive
      #objPwrCtrl.powerCycle()
      logData = self.ReadLenovo8S()
      objMsg.printMsg("Lenovo8S Log DF:")
      objMsg.printBin(logData)

      drive_custSerial = logData[20:50].strip()
      drive_newcustSer = logData[110:140].strip()
      
      #Validate dcm against cm
      if dcm_custSerial != None:
         objMsg.printMsg("Validating dcm attribute CUST_CODE against drive attribute CUST_SERIAL")
         if dcm_custSerial == cm_custSerial[0:16]: #cm_custSerial = dcm_custSerial + 7 bytes running number
            objMsg.printMsg("Validation between dcm and drive attribute done. PASS")
         else:
            objMsg.printMsg("Validation between dcm %s and drive attribute %s done. FAIL" % (dcm_custSerial, cm_custSerial[0:16]))
            ScrCmds.raiseException(10158, "Lenovo8S verification FAIL")
      else:
         objMsg.printMsg("dcm CUST_CODE is not defined. Skip Validating dcm attribute against drive attribute")

      #Validate drive's custSerial and newCustSer against cm
      objMsg.printMsg("Validating drive custSerial - original and new - against drive attribute CUST_SERIAL")
      if len(drive_custSerial) > 0 and len(drive_newcustSer) > 0:
         objMsg.printMsg("org_sn: %s new_sn: %s" %(drive_custSerial, drive_newcustSer))
      else:
         ScrCmds.raiseException(10158, "Invalid Lenovo8S number detected" )

      if nonProductionSite:
         objMsg.printMsg("Lenovo non production site code triggered!")
         drive_custSerial = drive_custSerial[:len(cm_custSerial)]
         drive_newcustSer = drive_newcustSer[:len(cm_custSerial)]

      if drive_custSerial == drive_newcustSer == cm_custSerial:
         objMsg.printMsg("Validation between drive and drive attribute done. PASS")
      else:
         objMsg.printMsg("Validation between drive and drive attribute done. FAIL")
         objMsg.printMsg("drive_custSerial: %s drive_newcustSer: %s cm_custSerial: %s" % (drive_custSerial, drive_newcustSer, cm_custSerial))
         ScrCmds.raiseException(10158, "Lenovo8S verification FAIL")

      return PASS

   #-------------------------------------------------------------------------------------------------------
   def ReadLenovo8S(self):
      """
      Read Lenovo8S from Smart log 0xDF
      """
      oSerialICmd = Serial_ICmd(self.params, objPwrCtrl)
      oSerialICmd.CCV_SetupCommMode(sdbpForce = True, multisrq_enable = False)
      sn = sdbpCmds.readLogExtended(0xDF, blockOffset = 0, blockXferLen = 1, logSpecific = 0)
      sn = sn.strip()
      return sn

###########################################################################################################

class CAttrVer_CCV(CState):
   """
      Class to verify following drive's attributes:
      DRIVE_MODEL_NUM, CUST_MODEL_NUM, FIRMWARE_VER and USER_LBA_COUNT
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self,):
      """
      Verify CCAs between drive, DCM requirements and FIS drive attributes
      """
      self.oSerial = serialScreen.sptDiagCmds()
      self.oSerial.quickDiag()

      objMsg.printMsg("Getting drive configs:")
      drvmodelnum = self.getDriveModelNum()
      if '[' not in self.dut.driveConfigAttrs.get('CUST_MODEL_NUM', ['', ''])[1]: 
         custmodelnum = self.getCustModelNum() #plain "CUST_MODEL_NUM" drive attr is updated to FIS if not defined in dcm
      else:
         custmodelnum = CCustomCfg().makeModelNumFisReady(self.getCustModelNum())[0].strip() #add trailing space and a bracket
      fwver = self.getDriveFWVer()
      servover = self.getDriveServoVer()
      maxlba = self.getDriveMaxLBA()
      hostsecsize = self.getHostSecSize()
      
      if self.dut.driveattr['FDE_DRIVE'] == 'FDE':
         ivver = self.getDriveIVVer()
         self.validation(ivver, 'IV_SW_REV', 'IV_SW_REV', chk_dcm_attr = False)
      else:
         objMsg.printMsg("Not SED/SdnD drive, skip IV_SW_REV attribute check")

      #Validation drive, dcm, attribute
      self.validation(drvmodelnum, 'DRV_MODEL_NUM', 'DRV_MODEL_NUM')
      self.validation(custmodelnum, 'CUST_MODEL_NUM', 'CUST_MODEL_NUM')
      self.validation(fwver, 'CODE_VER', 'CODE_VER', chk_dcm_attr = False)
      self.validation(servover, 'SERVO_CODE', 'SERVO_CODE', multiple_attr_values = True, chk_dcm_attr = False)
      if not ConfigVars[CN].get('SKIP_LBA_CHECK', 0):
         self.validation(maxlba, 'USER_LBA_COUNT', 'USER_LBA_COUNT')
      self.validation(hostsecsize, 'BYTES_PER_SCTR', 'BYTES_PER_SCTR')
      self.validateZGS() #Validate Zero gravity sensor

      return PASS

   #-------------------------------------------------------------------------------------------------------
   def getDriveModelNum(self):
      """
      Getting DriveModelNum from drive's Congen
      """
      if testSwitch.virtualRun:
         data = """
                  Byte:01A0:       InternalSeagateModelNumber =
                                   53 54 37 35 30 4C 4D 30 32 38 2D 31 4B 4B 31 36
                                   32 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20
                                   20 20 20 20 20 20 20 20
                                   'ST750LM028-1KK162      '
                """
      else:
         data=sptCmds.sendDiagCmd('/TF"InternalSeagateModelNumber"\r',altPattern='T>',printResult=True)
      m = re.search('ModelNumber =', data)
      if m == None:
         objMsg.printMsg('getDriveModelNum failed. Cannot read "ModelNumber ="')
         ScrCmds.raiseException(10609,"getDriveModelNum failed.")

      model = data[m.end():].split("'")[1]
      model = model.strip()    
      objMsg.printMsg("Drive_Model_Num= %s " % (model))                  

      return model 

   #-------------------------------------------------------------------------------------------------------
   def getCustModelNum(self):
      """
      Getting CustModelNum from Identify Device
      """
      if testSwitch.virtualRun:
         idModelNum = 'ST750LM028-1KK162'
      else:
         if not 'IDModel' in self.dut.IdDevice:
            oIdentifyDevice = CIdentifyDevice()
         idModelNum = self.dut.IdDevice['IDModel'].strip()

      if idModelNum == None:
         objMsg.printMsg('getCustModelNum failed. Cannot retrieve "IDModel" from Identify Device')
         ScrCmds.raiseException(10609,"getCustModelNum failed.")
      objMsg.printMsg("Cust_Model_Num= %s " % (idModelNum))                  

      return idModelNum 

   #-------------------------------------------------------------------------------------------------------
   def getDriveFWVer(self):
      """
      Getting drive firmware version
      """
      objMsg.printMsg("sending CTRL_L command")
      if testSwitch.virtualRun:
         res = \
            """
            KarnakPlus.1.1.SATA.Chengai.Mule.Servo376.Rap30.4K.SMR.SDnD.DFW
            Product FamilyId: 87, MemberId: 01
            HDA SN: W6700GC4, RPM: 5412, Wedges: 178, Heads: 2, OrigHeads: 4, Lbas: 00000B4C390B, PreampType: 81 02
            Bits/Symbol: C, Symbols/UserSector: C4B, Symbols/SystemSector: C3F
            PCBA SN: 0000J506LQU9, Controller: KARNAKPLUS_1_0_SATA(FFFF)(FF-FF, Channel: Unknown, PowerAsic: KONA Rev 6042, BufferBytes: 4000000
            Package Version: CH1400.SDM1.CA0153.0001SDM1, Package P/N: ---------, Package Global ID: 00080603,
            Package Build Date: 01/07/2015, Package Build Time: 18:01:49, Package CFW Version: CH14.SDM1.00806820.00080603,
            Package SFW1 Version: ----, Package SFW2 Version: ----, Package SFW3 Version: ----, Package SFW4 Version: ----
            Controller FW Rev: 01530001, CustomerRel: 0001, Changelist: 00806820, ProdType: CH14.SDM1, Date: 01/07/2015, Time: 180149, UserId: 00080603
            Servo FW Rev: 4E95
            TCG IV Version: 21.02
            Package BPN: 7
            RAP FW Implementation Key: 1E, Format Rev: 0105, Contents Rev: 1B 01 04 05
            QNR Container: 1
            Features:
            Serial Flash 8MB
            - Quadradic Equation AFH enabled
            - VBAR with adjustable zone boundaries enabled
            - Volume Based Sparing enabled
            - IOEDC enabled
            - IOECC enabled
            - DERP Read Retries enabled v. 5.0.07.0000000000000003
            - LTTC-UDR2 enabled 
            - SuperParity 4.1 enabled
               TotalSuperBlks     TotalValidSuperBlks
               00097126           00097126
            - Humidity Sensor disabled
            - Media Cache Partition enabled
            - Media Cache enabled
            - Background Reli Activity Critical Event Logging enabled
            - Torn Write Protection enabled
            - Zone Remap enabled
            [PLBA:00000000 Len:003D5578 Offset:008EED1A]
            [PLBA:003D5578 Len:008EED1A Offset:FFC2AA88]
            [PLBA:00CC4292 Len:0A7FF679 Offset:00000000]
            [PLBA:0B4C390B Len:00000001 Offset:00000000]
            - AGB disabled            
            """
      else:
         res = sptCmds.sendDiagCmd(CTRL_L, printResult = True)

      patMat = re.search('\s*Package Version:*\s*(?P<PackageVersion>[\.a-zA-Z0-9\-]*)', res)
      if patMat == None:
         objMsg.printMsg(res, objMsg.CMessLvl.VERBOSEDEBUG)
         ScrCmds.raiseException(11044,{"ERR":'Failed to parse Code Revision',"DATA":res})
      else:
         fwver = patMat.groupdict()['PackageVersion']
      objMsg.printMsg("Firmware ver = %s" % fwver)

      return fwver

   #-------------------------------------------------------------------------------------------------------
   def getDriveServoVer(self):
      """
      Getting drive Servo code version
      """
      objMsg.printMsg("sending CTRL_L command")
      if testSwitch.virtualRun:
         res = \
            """
            KarnakPlus.1.1.SATA.Chengai.Mule.Servo376.Rap30.4K.SMR.SDnD.DFW
            Product FamilyId: 87, MemberId: 01
            HDA SN: W6700GC4, RPM: 5412, Wedges: 178, Heads: 2, OrigHeads: 4, Lbas: 00000B4C390B, PreampType: 81 02
            Bits/Symbol: C, Symbols/UserSector: C4B, Symbols/SystemSector: C3F
            PCBA SN: 0000J506LQU9, Controller: KARNAKPLUS_1_0_SATA(FFFF)(FF-FF, Channel: Unknown, PowerAsic: KONA Rev 6042, BufferBytes: 4000000
            Package Version: CH1400.SDM1.CA0153.0001SDM1, Package P/N: ---------, Package Global ID: 00080603,
            Package Build Date: 01/07/2015, Package Build Time: 18:01:49, Package CFW Version: CH14.SDM1.00806820.00080603,
            Package SFW1 Version: ----, Package SFW2 Version: ----, Package SFW3 Version: ----, Package SFW4 Version: ----
            Controller FW Rev: 01530001, CustomerRel: 0001, Changelist: 00806820, ProdType: CH14.SDM1, Date: 01/07/2015, Time: 180149, UserId: 00080603
            Servo FW Rev: 4E95   
            """
      else:
         res = sptCmds.sendDiagCmd(CTRL_L, printResult = True)

      patMat = re.search('\s*Servo FW Rev:*\s*(?P<ServoVersion>[\.a-zA-Z0-9\-]*)', res)
      if patMat == None:
         objMsg.printMsg(res, objMsg.CMessLvl.VERBOSEDEBUG)
         ScrCmds.raiseException(11044,{"ERR":'Failed to parse Code Revision',"DATA":res})
      else:
         servover = patMat.groupdict()['ServoVersion']
      objMsg.printMsg("Servo code ver = %s" % servover)

      return servover

   #-------------------------------------------------------------------------------------------------------
   def getDriveIVVer(self):
      """
      Getting drive TCG IV version
      """
      objMsg.printMsg("sending CTRL_L command")
      if testSwitch.virtualRun:
         res = \
            """
            KarnakPlus.1.1.SATA.Chengai.Mule.Servo376.Rap30.4K.SMR.SDnD.DFW
            Product FamilyId: 87, MemberId: 01
            HDA SN: W6700GC4, RPM: 5412, Wedges: 178, Heads: 2, OrigHeads: 4, Lbas: 00000B4C390B, PreampType: 81 02
            Bits/Symbol: C, Symbols/UserSector: C4B, Symbols/SystemSector: C3F
            PCBA SN: 0000J506LQU9, Controller: KARNAKPLUS_1_0_SATA(FFFF)(FF-FF, Channel: Unknown, PowerAsic: KONA Rev 6042, BufferBytes: 4000000
            Package Version: CH1400.SDM1.CA0153.0001SDM1, Package P/N: ---------, Package Global ID: 00080603,
            Package Build Date: 01/07/2015, Package Build Time: 18:01:49, Package CFW Version: CH14.SDM1.00806820.00080603,
            Package SFW1 Version: ----, Package SFW2 Version: ----, Package SFW3 Version: ----, Package SFW4 Version: ----
            Controller FW Rev: 01530001, CustomerRel: 0001, Changelist: 00806820, ProdType: CH14.SDM1, Date: 01/07/2015, Time: 180149, UserId: 00080603
            Servo FW Rev: 4E95
            TCG IV Version: 30.05   
            """
      else:
         res = sptCmds.sendDiagCmd(CTRL_L, printResult = True)

      patMat = re.search('\s*TCG IV Version:*\s*(?P<IVVersion>[\.a-zA-Z0-9\-]*)', res)
      if patMat == None:
         objMsg.printMsg(res, objMsg.CMessLvl.VERBOSEDEBUG)
         ScrCmds.raiseException(11044,{"ERR":'Failed to parse Code Revision',"DATA":res})
      else:
         iv_ver = patMat.groupdict()['IVVersion']
      objMsg.printMsg("TCG IV ver = %s" % iv_ver)

      return iv_ver

   #-------------------------------------------------------------------------------------------------------
   def getDriveMaxLBA(self):
      """
      Getting Drive's maximum LBA
      """

      if not "Max LBA" in self.dut.IdDevice or not "Max LBA Ext" in self.dut.IdDevice:
         oIdentifyDevice = CIdentifyDevice()

      if testSwitch.virtualRun:
         maxLBA = '1465149168'
      else:
         maxLBA = str(max(self.dut.IdDevice["Max LBA Ext"]+1, self.dut.IdDevice["Max LBA"]+1)) 
      if maxLBA == None:
         objMsg.printMsg("Failed to get max LBA from identify device")
         ScrCmds.raiseException(11044,"Failed to get max LBA from identify device")
      objMsg.printMsg("Max LBA = %s" % maxLBA)                

      return maxLBA 

   #-------------------------------------------------------------------------------------------------------
   def getHostSecSize(self):
      """
      Getting Drive's Host Sector size/Logical sector size
      """

      if not "Logical Sector Size" in self.dut.IdDevice:
         oIdentifyDevice = CIdentifyDevice()

      if testSwitch.virtualRun:
         hostsecsize = '512'
      else:
         hostsecsize = str(self.dut.IdDevice["Logical Sector Size"])
      if hostsecsize == None:
         objMsg.printMsg("Failed to get Host sector size from identify device")
         ScrCmds.raiseException(11044,"Failed to get Host sector size from identify device")
      objMsg.printMsg("Host sector size = %s" % hostsecsize)                

      return hostsecsize

   #-------------------------------------------------------------------------------------------------------
   def validation(self, drv_config_val = None, dcm_attr_name = None, fis_attr_name = None, multiple_attr_values = False, chk_dcm_attr = True):
      """
      Validation between drive, dcm and attribute
      """
      objMsg.printMsg("Validation of %s ..." % fis_attr_name)
      if testSwitch.virtualRun:
         self.dut.driveConfigAttrs = {'STATUS': ('=', 'PASS'), 'SERVER_ERROR': ('=', 'NO ERROR'), 'JUMPER_SET': ('=', 'SATA_NO_JMPR'), 'SED_LC_STATE': ('=', 'USE'), \
                                      'TIME_TO_READY': ('<', '4000'), 'DLP_SETTING': ('=', 'UNLOCKED'), 'SECURITY_TYPE': ('=', 'SECURED BASE (SD AND D)'), \
                                      'DRV_MODEL_NUM': ('=', 'ST750LM028-1KK162'), 'CUST_MODEL_NUM2': ('=', '[          ]'), 'CUST_MODEL_NUM': ('=', '[ST750LM028-1KK162             ]'), \
                                      'TC_LABEL_BLK_PN': ('=', '708274900'), 'INTERFACE': ('=', 'SATA'), 'USER_LBA_COUNT': ('=', '1465149168'), 'ZERO_PTRN_RQMT': ('>', '13')}

         DriveAttributes['DRV_MODEL_NUM'] = self.dut.driveattr['DRV_MODEL_NUM'] = 'ST750LM028-1KK162'
         DriveAttributes['CUST_MODEL_NUM'] = self.dut.driveattr['CUST_MODEL_NUM'] = '[ST750LM028-1KK162             ]'
         DriveAttributes['CODE_VER'] = self.dut.driveattr['CODE_VER'] = 'CH1400.SDM1.CA0153.0001SDM1'
         DriveAttributes['SERVO_CODE'] = self.dut.driveattr['SERVO_CODE'] = '4E95'
         DriveAttributes['IV_SW_REV'] = self.dut.driveattr['IV_SW_REV'] = '30.05'
         DriveAttributes['USER_LBA_COUNT'] = self.dut.driveattr['USER_LBA_COUNT'] = '1465149168'
         DriveAttributes['BYTES_PER_SCTR'] = self.dut.driveattr['BYTES_PER_SCTR'] = '512'

      #Verify drive config is according to dcm requirement
      if chk_dcm_attr:
         if multiple_attr_values:
            # for multiple attribute values, perform iteration
            status = None
            for key in self.dut.driveConfigAttrs:
               if dcm_attr_name == key[:len(dcm_attr_name)]:
                  # attribute name matches DCM attribute, compare whether values match or not
                  status = False
                  objMsg.printMsg("\tDCM attribute %s value: %s" % (dcm_attr_name, self.dut.driveConfigAttrs[key][1].rstrip()) )
                  if self.dut.driveConfigAttrs[key][1].rstrip() == drv_config_val:
                     objMsg.printMsg("\tVerify DCM attribute against drive config. PASS")
                     status = True
                     break 

            if status is False:
               objMsg.printMsg("\tVerify DCM attribute against drive config. FAIL")
               ScrCmds.raiseException(14761,"%s Attribute validation failed" % dcm_attr_name)
            elif status is None:  
               objMsg.printMsg("\tDCM attribute %s is not defined. Skip verifying DCM attribute against drive config" % dcm_attr_name)

         else:
            if dcm_attr_name in self.dut.driveConfigAttrs:
               objMsg.printMsg("\tDCM attribute %s is defined" % dcm_attr_name)
               if self.dut.driveConfigAttrs[dcm_attr_name][1].rstrip() == drv_config_val:
                  objMsg.printMsg("\tVerify DCM attribute against drive config. PASS")
               else:
                  objMsg.printMsg("\tVerify DCM attribute %s against drive config %s. FAIL" % (self.dut.driveConfigAttrs[dcm_attr_name][1].rstrip(), drv_config_val))
                  ScrCmds.raiseException(14761,"%s Attribute validation failed" % dcm_attr_name)
            else:
               objMsg.printMsg("\tDCM attribute %s is not defined. Skip verifying DCM attribute against drive config" % dcm_attr_name)
      else:
         objMsg.printMsg("\tDCM check is not required for %s. Skip verifying DCM attribute against drive config" % dcm_attr_name)

      #Verify drive config against drive attribute (cm copy)
      if CCV1:
         cm_attr = self.dut.driveattr.get(fis_attr_name, None)
      elif CCV2:
         cm_attr = self.dut.driveattr.get(fis_attr_name, DriveAttributes[fis_attr_name]) #Not all DriveAttributes are copied to driveattr during CCV2 INIT

      if len(str(drv_config_val)) != 0 and drv_config_val == cm_attr:
         objMsg.printMsg("\tVerify Drive config against Drive attribute(CM copy). PASS")
      else:
         objMsg.printMsg("\tVerify Drive config %s against Drive attribute(CM) %s. FAIL" % (drv_config_val, cm_attr))
         ScrCmds.raiseException(14761,"%s Attribute validation failed" % dcm_attr_name)

   #-------------------------------------------------------------------------------------------------------
   def validateZGS(self):

      objMsg.printMsg("Validation of ZERO_G_SENSOR ...")
      drive_ZGS = self.dut.IdDevice['ZGS']
      dcm_ZGS = str(self.dut.driveConfigAttrs.get('ZERO_G_SENSOR',(0,'NA'))[1]).rstrip()
      if CCV1:
         cm_ZGS = str(self.dut.driveattr.get('ZERO_G_SENSOR', None))
      elif CCV2:
         cm_ZGS = str(self.dut.driveattr.get('ZERO_G_SENSOR', DriveAttributes['ZERO_G_SENSOR']))

      if drive_ZGS and (cm_ZGS == "0" or cm_ZGS == "NA"):
         objMsg.printMsg("driveZGS %s cmZGS %s, FAIL" % (drive_ZGS, cm_ZGS))
         ScrCmds.raiseException(14761, "ZGS validation between drive and drive attribute fail")
      elif (not drive_ZGS) and cm_ZGS == "1":
         objMsg.printMsg("driveZGS %s cmZGS %s, FAIL" % (drive_ZGS, cm_ZGS))
         ScrCmds.raiseException(14761, "ZGS validation between drive and drive attribute fail")
      else:
         objMsg.printMsg("\tVerify ZGS drive attribute against drive config. PASS")
       
      if 'ZERO_G_SENSOR' in self.dut.driveConfigAttrs:
         if dcm_ZGS == cm_ZGS:
            objMsg.printMsg("\tVerify dcm attribute against drive attribute. PASS")
         else:
            objMsg.printMsg("dcmZGS %s cmZGS %s, FAIL" % (dcm_ZGS, cm_ZGS))
            ScrCmds.raiseException(14761, "ZGS validation between dcm and drive attribute fail")
      else:
         objMsg.printMsg("\tDCM attribute ZERO_G_SENSOR is not defined. Skip validation")

##########################################################################################################

class CSPVer_CCV(CState):
   """
      Check SuperParity Invalid ratio.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      self.oSerial = serialScreen.sptDiagCmds()

      if sptCmds.objComMode.getMode() != sptCmds.objComMode.availModes.sptDiag:
         objPwrCtrl.powerCycle(5000,12000,10,30)
         time.sleep(5) # In IO mode, require 5sec delay to fully load Super Parity table after power cycle

      #Get SPRatio from drive
      SPRatio = self.oSerial.GetSPRatio(getCTRL_L = True)
      objMsg.printMsg("Initial SPRatio: %s" % SPRatio)
      self.dut.driveattr['PROC_CTRL7'] = SPRatio

      if SPRatio == None:
         ScrCmds.raiseException(48665, "Invalid SuperParity_Ratio detected")

      SPRatio_spec = 0.2    # fail if drive Super Parity Ratio > 0.2
      if SPRatio > SPRatio_spec:
         objMsg.printMsg('SuperParity Check Failed.')
         ScrCmds.raiseException(48665,'SUPER PARITY ratio check Failed')
      else:
         objMsg.printMsg('SUPER PARITY ratio Check Passed')

      return PASS

###########################################################################################################

class CMCVer_CCV(CState):
   """
      Class that verify MC is enabled and MC is initialized
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      # **** MC status ****
      # True = MC supported and enabled, 
      # False = MC supported and disabled
      # None = MC not supported
      mc = self.Get_MCStatus() 
      objMsg.printMsg("Media Cache status: %s" % mc)
      if mc == None:
         objMsg.printMsg("Media cache is not supported")
         return SKIP
      elif mc == False:
         objMsg.printMsg("Media cache is supported but disabled. Fail")
         ScrCmds.raiseException(14842, "Media Cache is supported but disabled")
      elif mc == True:
         objMsg.printMsg("Media cache is supported and enabled")
         if self.IsMCClean():
            objMsg.printMsg("Media cache is clean. PASS")
         else:
            objMsg.printMsg("Media cache is not clean. FAIL")
            ScrCmds.raiseException(14842, "Media Cache is enabled but not clean")

      return PASS

   #-------------------------------------------------------------------------------------------------------
   def Get_MCStatus(self, status=None):
      """ Check if drive supports media cache """
      mc_support = None
      mc_status = None
      sptCmds.enableDiags()
      sptCmds.gotoLevel('T')
      ret_data = sptCmds.sendDiagCmd('F"MediaCache"',timeout=300, printResult = True)
      if testSwitch.virtualRun:
         if status is 'enable':
            ret_data = """
               Byte:0499:       MediaCacheControl = 03
               Byte:0499:           Bit:0, ID_BLOCK_MEDIA_CACHE_SUPPORTED = 1
               Byte:0499:           Bit:1, ID_BLOCK_MEDIA_CACHE_ENABLED = 1
               """
         else:
            ret_data = """
               Byte:0499:       MediaCacheControl = 03
               Byte:0499:           Bit:0, ID_BLOCK_MEDIA_CACHE_SUPPORTED = 0
               Byte:0499:           Bit:1, ID_BLOCK_MEDIA_CACHE_ENABLED = 0
               """
      pattern = 'ID_BLOCK_MEDIA_CACHE_SUPPORTED\s+=\s+(?P<MCSUPPORTED>[\d])[\s+\S+]+ID_BLOCK_MEDIA_CACHE_ENABLED\s+=\s+(?P<MCSTATUS>[\d])'
      match = re.search(pattern, ret_data)
      if match:
         mc_support = match.groupdict()['MCSUPPORTED']
         mc_status = match.groupdict()['MCSTATUS']

      if mc_support == '1':
         if mc_status == '1':
            return True
         else:
            return False
      else:
         return None

   #-------------------------------------------------------------------------------------------------------
   def IsMCClean(self):
      """
      Check MC using CTRL_A MCSegmentUsed and MCNodeUsed.
      If both values are zero means MC is clean
      """
      oSerial = serialScreen.sptDiagCmds()
      cleanMC = False
      for retry in xrange(3):       # allow retry if cannot get data
         data = oSerial.GetCtrl_A()
         pattern = 'MCSegmentUsed\s(?P<SEGMENT>\w+)[\s+\S+]+MCNodeUsed\s+(?P<NODE>\w+)'
         match = re.search(pattern, data)
         if match:
            MCSegmentUsed = match.groupdict()['SEGMENT']
            MCNodeUsed = match.groupdict()['NODE']
            if ( int(MCSegmentUsed, 16) + int(MCNodeUsed, 16) ) == 0:
               cleanMC = True
            break
         else:
            time.sleep(5)
            continue
      else:
         ScrCmds.raiseException(11044,"Unable to determine MC data")
      objMsg.printMsg( "Media cache is clean? %s" %cleanMC)
      return cleanMC

###########################################################################################################

class CNVCVer_CCV(CState):
   """
      Class that verify NVC is clean and wearout info are within spec
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if testSwitch.FE_0000000_305538_HYBRID_DRIVE == 0:
         objMsg.printMsg("Non-hybrid drive, skip NVC verification")
         return SKIP

      objMsg.printMsg("Verify NAND flash is clean")
      sptCmds.gotoLevel('O')
      data = sptCmds.sendDiagCmd('b',printResult = True)
      pattern = 'Pinned Data in Clumps:\n*\s*Read\s*Write\s*Free\s*SIM\s*Total\n*\s*(?P<READ>[a-fA-F\d]+)\s+(?P<WRITE>[a-fA-F\d]+)'

      match = re.search(pattern, data)
      if match:
         if int(match.groupdict()['READ'], 16) == 0 and int(match.groupdict()['WRITE'], 16) == 0:
            objMsg.printMsg("NVC is clean!, READ clump %s, WRITE clump %s" % (match.groupdict()['READ'], match.groupdict()['WRITE']))
         else:
            objMsg.printMsg("NVC is not clean, some pinned data in clumps. READ clump %s WRITE clump %s" % (match.groupdict()['READ'], match.groupdict()['WRITE']))
            ScrCmds.raiseException(13306, "NAND flash is not clean")
      else:
         ScrCmds.raiseException(13306, "Can't find the signature while verifying NAND flash cleanliness")

      objMsg.printMsg("Verify NAND wearout info are within the spec")
      self.NAND_Screen()

      return PASS

   #-------------------------------------------------------------------------------------------------------
   def NAND_Screen (self):
      result = OK

      #Get Max_MLC_EraseCnt, Max_SLC_EraseCnt, Bad_Clump_Cnt, Retired_Clump_Cnt
      if testSwitch.virtualRun:
         max_mlc_ec = '0064'
         max_slc_ec = '00C8'
         bad_clp_cnt = '0002'
         retired_clp_cnt = '0000'
      else:
         oSerial = serialScreen.sptDiagCmds()
         max_slc_ec, max_mlc_ec, bad_clp_cnt, retired_clp_cnt = oSerial.Get_NANDFlash_Param()
         if max_slc_ec == None or max_mlc_ec == None or bad_clp_cnt == None or retired_clp_cnt == None:
            ScrCmds.raiseException(48643, "Cannot get all the NAND Flash parameters! %s" %traceback.format_exc())

      max_mlc_ec = int(max_mlc_ec, 16) #conversion to integer
      max_slc_ec = int(max_slc_ec, 16)
      bad_clp_cnt = int(bad_clp_cnt, 16)
      retired_clp_cnt = int(retired_clp_cnt, 16)

      if testSwitch.virtualRun:
         self.dut.NandVendor = 'Samsung'
      else:
         self.dut.NandVendor = 'default'
         sptCmds.gotoLevel('N')
         ret_data = sptCmds.sendDiagCmd('v',timeout=300, printResult = True)
         Match = re.search('Flash Manufacturer:\s*(?P<VENDOR>\w*)\s*', ret_data)
         if Match:
            NandVendor = Match.group('VENDOR')
            if NandVendor ==None:
               objMsg.printMsg("Warning! Not able to find nand vendor, using deafult")
            else:
               self.dut.NandVendor = NandVendor
         else:
            objMsg.printMsg("Warning! Not able to find nand vendor, using deafult")

         objMsg.printMsg("Nand Vendor: %s" %(self.dut.NandVendor))

      #Check against the spec
      objMsg.printMsg("Bad Clumps Count         :(%s) against spec   :(%s)" % (bad_clp_cnt,TP.prm_NAND_SCREEN['BAD_CLP_CNT']))
      self.dut.driveattr['PROC_CTRL2'] = bad_clp_cnt
      if bad_clp_cnt > TP.prm_NAND_SCREEN['BAD_CLP_CNT']:
         result = NOT_OK
         ScrCmds.raiseException(48643, "Bad clumps count more than spec! %s" %traceback.format_exc())

      objMsg.printMsg("Retired Clumps Count     :(%s) against spec   :(%s)" % (retired_clp_cnt,TP.prm_NAND_SCREEN['RETIRED_CLP_CNT']))
      self.dut.driveattr['PROC_CTRL3'] = retired_clp_cnt
      if retired_clp_cnt > TP.prm_NAND_SCREEN['RETIRED_CLP_CNT']:
         result = NOT_OK
         ScrCmds.raiseException(48643, "Retired clumps count more than spec! %s" %traceback.format_exc())

      objMsg.printMsg("Maximum MLC Erased Count :(%s) against spec   :(%s)" % (max_mlc_ec,TP.prm_NAND_SCREEN['MAX_MLC_EC']))
      self.dut.driveattr['PROC_CTRL4'] = max_mlc_ec
      if max_mlc_ec > TP.prm_NAND_SCREEN['MAX_MLC_EC']:
         result = NOT_OK
         ScrCmds.raiseException(48643, "Maximum MLC erased count more than spec! %s" %traceback.format_exc())

      objMsg.printMsg("Maximum SLC Erased Count :(%s) against spec   :(%s)" % (max_slc_ec,TP.prm_NAND_SCREEN['MAX_SLC_EC']))
      self.dut.driveattr['PROC_CTRL5'] = max_slc_ec
      if max_slc_ec > TP.prm_NAND_SCREEN['MAX_SLC_EC']:
         result = NOT_OK
         ScrCmds.raiseException(48643, "Maximum SLC erased count more than spec! %s" %traceback.format_exc())

      if result == OK:
         objMsg.printMsg("NAND Screen Passed!")

###########################################################################################################

class CSOCVer_CCV(CState):
   """
      Class that verify Fast SOC drives shipped to SBS customer ONLY
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
       
      if testSwitch.ENABLE_SBS_DWNGRADE_BASED_ON_SOC_BIT:
         objMsg.printMsg("Verify SOC type")
         cm_attr = self.dut.driveattr.get("SOC_TYPE", 0)

         if cm_attr == '1' and 'BSNS_SEGMENT' not in self.dut.driveConfigAttrs: #For FastSOC drive, dcm entry 'BSNS_SEGMENT' is required for verification
            objMsg.printMsg("Fast SOC drive detected. BSNS_SEGMENT dcm attribute is not defined")
            ScrCmds.raiseException(14761, "Missing BSNS_SEGMENT dcm attribute")

         dcm_attr = self.dut.driveConfigAttrs.get('BSNS_SEGMENT', ['', 'None'])[1].rstrip()
         objMsg.printMsg("SOC_TYPE = %s, DCM Business Segment = %s" % (cm_attr, dcm_attr))
        
         if cm_attr == '1' and dcm_attr != 'SBS': #Ensure FastSOC drives shipped to SBS customer only
            objMsg.printMsg("Fast SOC drive detected. DCM BSNS_SEGMENT is not equal to SBS")
            ScrCmds.raiseException(14761, "Fast SOC drive tagged with wrong Part number")
         else:
            objMsg.printMsg("Drive SOC verification PASS")

         return PASS
      else:
         objMsg.printMsg("SOC type verification skipped")
         return SKIP

###########################################################################################################

class CLCSPINVer_CCV(CState):
   """
      Class that verify drive's low current spinup feature is according to DCM 
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
       
      screens = []
      chars = 3
      #Check whether dcm has SC1 customer test
      for name in self.dut.driveConfigAttrs.keys(): 
         if name == 'CUST_TESTNAME':
            value = self.dut.driveConfigAttrs[name][1]
            screens = [value[i*chars:(i*chars )+chars] for i in xrange(len(value)/chars)]
            break

      oSerial = serialScreen.sptDiagCmds() # Check status from CTRL_L
      ctr_l = oSerial.GetCtrl_L(force = True)
      status = ctr_l.get('LowCurrentSpinUp')
         
      if 'SC1' not in screens:
         #Check Low Current spin is disabled
         if status == 'disabled':
            objMsg.printMsg("Low Current SpinUp feature is disabled. PASS")
            return PASS
         elif status == 'enabled' and not testSwitch.virtualRun:
            objMsg.printMsg("Low Current SpinUp feature is enabled, supposed to be disabled. FAIL")
            ScrCmds.raiseException(14049, "Low current spin feature check failed")
      else:
         #Check Low Current spin is enabled
         if status == 'enabled':
            objMsg.printMsg("Low Current SpinUp feature is enabled. PASS")
            return PASS
         elif status == 'disabled' and not testSwitch.virtualRun:
            objMsg.printMsg("Low Current SpinUp feature is disabled, supposed to be enabled. FAIL")
            ScrCmds.raiseException(14049, "Low current spin feature check failed")
     
      return PASS

###########################################################################################################

class CAMPSReset_CCV(CState):
   """
      Class resetting AMPS
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):

      objMsg.printMsg("Reset AMPS")
      self.changeAMPS()
      objMsg.printMsg("Reset AMPS PASS")
      return PASS

   #-------------------------------------------------------------------------------------------------------
   def changeAMPS(self,AMPSName = "", Value = 0, mask = 0xFFFF):

      objMsg.printMsg("Setting AMPS %s to %x" % (AMPSName, Value))
      oSerial = serialScreen.sptDiagCmds()
      sptCmds.gotoLevel('T')
      if AMPSName == "":
         acc = oSerial.PBlock("F,,22")
      else:
         acc = oSerial.PBlock('F"%s",%x' % (AMPSName, Value))
      result = sptCmds.promptRead(30,1,accumulator=acc, loopSleepTime = 0)
      del acc
      result = sptCmds.sendDiagCmd('F"%s"' % AMPSName,timeout = 1000, loopSleepTime = 0)
      match = re.search("%s\s*=\s*(?P<val>[\da-fA-F]+)" % AMPSName, result)
      if testSwitch.virtualRun or AMPSName == "":
         return PASS

      if match:
         retDict = match.groupdict()
         if not (int(retDict['val'], 16) & mask) == Value:
            objMsg.printMsg("ErrorDump: \n%s" % result)
            ScrCmds.raiseException(14002, "AMPS set command of %s to %x failed" % (AMPSName, Value))
      else:
         objMsg.printMsg("ErrorDump: \n%s" % result)
         ScrCmds.raiseException(14002, "AMPS set command of %s to %x failed" % (AMPSName, Value))

###########################################################################################################

class CDOSReset_CCV(CState):
   """
      Description: Class that will perform DOS clearing.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      objMsg.printMsg("Reset DOS")
      clearDOSParams = {
         'displayBefore'         : 1,
         'clearDOS'              : 1,
         'clearLength'           : 12416,
         'verifyAfter'           : 1,
         'maxRetries'            : 2,
         }
      self.clearDOS(clearDOSParams)
      objMsg.printMsg("Reset DOS PASS")
      return PASS
         
   #-------------------------------------------------------------------------------------------------------
   def clearDOS(self, clearDOSParams):
      """
         Use level 7>m1/m100 commands to perform DOS Display and DOS Clearing
      """
      oSerial = serialScreen.sptDiagCmds()
      retry = 0
      while retry < clearDOSParams['maxRetries']:

         revDict = oSerial.getCommandVersion('7','m', printResult = True)
         if revDict['majorRev'] > 8000:
            clrDos = 'm100'
            displDos = 'm'
            objMsg.printMsg("Single Track DOS detected")
         else:
            clrDos = "m100"
            displDos = 'm'
            #displDos = 'm1,0,1000000,1'
            objMsg.printMsg("DOS detected")


         sptCmds.gotoLevel('7')

         if clearDOSParams['displayBefore']:
            try:sptCmds.sendDiagCmd(displDos,timeout = 300,printResult = True, maxRetries = 3, loopSleepTime = 0)
            except:pass

         if clearDOSParams['clearDOS']:
            data = sptCmds.sendDiagCmd(clrDos,timeout = 300,printResult = True, maxRetries = 3, loopSleepTime = 0)
            if data.find('Invalid') == -1:# and data.find('m1') != -1 :
               objMsg.printMsg("Passed DOS Table Clear: %s" % data)
               break
            else:
               objMsg.printMsg("Failed DOS Table Clear: %s" % data)
               retry += 1
         else:
            objMsg.printMsg("Clear DOS Table turned OFF - clearDOS=%s" % clearDOSParams['clearDOS'])
            break

      else:
         if not testSwitch.virtualRun:
            ScrCmds.raiseException(13457,"Failed to Clear DOS")

      if clearDOSParams['verifyAfter']:
         try:
            data = sptCmds.sendDiagCmd(displDos,timeout = 300,printResult = True, maxRetries = 3, loopSleepTime = 0)
         except:
            data = ''
         verifyDataLength = len(data)
         objMsg.printMsg("Verify DOS Table data length: %s" % verifyDataLength)
         if verifyDataLength <= clearDOSParams['clearLength']:    # check DOS clearing, check by length #data.find('m1') != -1 and
            objMsg.printMsg("Passed DOS Table Verify: %s" % data)
         else:
            objMsg.printMsg("Failed DOS Table Verify: %s" % data)
            if not testSwitch.virtualRun:
               ScrCmds.raiseException(13457,"Failed to Verify - Clear DOS")
      else:
         objMsg.printMsg("Display/Verify DOS Table Clear turned OFF - verifyAfter=%s" % clearDOSParams['verifyAfter'])

###########################################################################################################

class CEPCReset_CCV(CState):
   """
      Class resetting EPC. Have to check out on Rosewood drive when EPC feature is enabled.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      objMsg.printMsg("CEPCReset_CCV")
#     self.ID['ATASignalSpeedSupport'] = self.__numSwap(data[152:154])                    # Word 76 bit 1-2
#     self.ID['word76_woswap']       = data[152:154]
#     self.ID['ATA_SignalSpeed'    ] = self.__numSwap(data[154:156])                      # Word 77 bit 0-3
#     self.ID['word77_woswap']       = data[154:156]
#     self.ID['word119'            ] = self.__numSwap(data[238:240])     # Word 119
#     self.ID['word119_woswap']       = data[238:240]

      self.Identify = CIdentifyDevice().ID
      objMsg.printMsg("ID_word76 in hex: %x" % self.Identify['ATASignalSpeedSupport'])
      objMsg.printMsg("ID_word77 in hex: %x" % self.Identify['ATA_SignalSpeed'])
      objMsg.printMsg("ID_word119 in hex: %x" % self.Identify['ExtendedPowerCond'])

##########################################################################################################

class CEWLMReset_CCV(CState):
   """
      Displays and clears drive EWLM using DITS command 0x0174
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      """
         Clear EWLM
      """
      from SmartFuncs import smartEWLM as ewlm
      objMsg.printMsg("Reset EWLM")
      try:
         if not testSwitch.NoIO:
            objMsg.printMsg("*** IO mode ****")
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
            self.readWorkLogPage()
            self.clearWorkLogPage()                                  # clear log page
            time.sleep(30)

            # display log page after clearing
            objMsg.printMsg('EWLM log page after clearing.')
            self.readWorkLogPage()
            data = ICmd.GetBuffer(RBF, 0, 512*1)['DATA'][4:]
            lastParameterCode = int(binascii.hexlify(data[24:26]),16)
            if lastParameterCode > 1:
               raise

         else:
            objMsg.printMsg("*** Serial mode ****")
            #Display EWLM
            import sdbpCmds
            self.SPreadWorkLogPage()

            #Clear EWLM using DITS cmd
            sptCmds.sendDiagCmd(CTRL_T, printResult = True)
            sptCmds.enableESLIP()
            try:
               sdbpCmds.unlockDits()
            except:
               pass

            data, error, dataBlock = sdbpCmds.clearEWLM()
            time.sleep(30)

            #Display EWLM and check
            if self.SPreadWorkLogPage() > 0:
               raise
      except:
         objMsg.printMsg('*** EWLM not cleared! *** Traceback %s' %traceback.format_exc())
         if testSwitch.virtualRun:
            objMsg.printMsg('EWLM clearing not supported in VE.')
         elif testSwitch.FE_SGP_402984_RAISE_EWLM_CLEAR_FAILURE:
            ScrCmds.raiseException(10251, "EWLM last parameter code not cleared! %s" %traceback.format_exc())

      objMsg.printMsg("Reset EWLM PASS")
      return PASS

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
   def readWorkLogPage(self):
      """
         Read work load log page B6
      """
      prm_538_SmartWorkLog = {
         'test_num'              : 538,
         'prm_name'              : 'Read log page B6h',
         'timeout'               : 600,
         'COMMAND'               : 47,
         'FEATURES'              : 0,
         'PARAMETER_0'           : 8192,
         'SECTOR_COUNT'          : 1,
         'LBA_HIGH'              : 0,
         'LBA_MID'               : 0,
         'LBA_LOW'               : 182,
         'stSuppressResults'     : ST_SUPPRESS__ALL,
         }
      try:
         ICmd.HardReset()                 # required to reflect correct HP EWLM signature
         ICmd.St(prm_538_SmartWorkLog)
      except:
         ICmd.UnlockFactoryCmds()         # non-hp drive
         ICmd.St(prm_538_SmartWorkLog)
      #self.displayReadBuffer()

   #-------------------------------------------------------------------------------------------------------
   def clearWorkLogPage(self):
      """ 
         Requires CPC 2.247 and above 
      """
      prm_638_EWLM_Control = {
         'test_num'              : 638,
         'prm_name'              : 'Clear log page B6h',
         'DFB_WORD_0'            : 29697,
         'DFB_WORD_1'            : 256,
         'DFB_WORD_2'            : 256,
         'DFB_WORD_3'            : 256,
         'timeout'               : 3600,
         'spc_id'                : 1,
         'stSuppressResults'     : ST_SUPPRESS__ALL,
         }
      ICmd.St(prm_638_EWLM_Control)

###########################################################################################################

class CSecVer_CCV(CState):
   """
      Verifying drive's security features such as life state, port status and SOM
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)
        
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      """
         For SED drive, verify security features
      """
      if self.dut.driveattr['FDE_DRIVE'] != 'FDE' or testSwitch.virtualRun:
         objMsg.printMsg("Not SED/SdnD drive, skip this")
         return SKIP   

      LifeStatesDict = {
                     '00': 'SETUP',
                     '01': 'DIAG',
                     '80': 'USE',
                     '81': 'MFG',
                     'FF': 'INVALID',
                   }

      objMsg.printMsg("*** Verify TD_SID ***")
      from TCG import CTCGPrepTest
      CTCGPrepTest(self.dut)

      if CCV1:
         cm_copy = self.dut.driveattr.get('TD_SID', None)
      elif CCV2:
         cm_copy = self.dut.driveattr.get('TD_SID', DriveAttributes['TD_SID'])
      if len(cm_copy) == 32:
         objMsg.printMsg("TD_SID verification PASS")
      else:
         objMsg.printMsg("len(TD_SID) %s cm_copy %s, FAIL" % (len(cm_copy), cm_copy))
         ScrCmds.raiseException(12383, "Error, TD_SID value is incorrect")

      if testSwitch.FE_0225282_231166_P_TCG2_SUPPORT:
         TCG_VERSION = 2    
      else:
         TCG_VERSION = 1    

      if testSwitch.NoIO:
         objMsg.printMsg("Security verification in SPIO mode..")
         Y2backup = self.dut.SkipY2
         self.dut.SkipY2 = True
         #Drive power cycle to ensure ports are locked
         self.dut.TCGComplete = True #prevent powercycle method from unlocking drive
         objPwrCtrl.powerCycle(useESlip=1) 
        
         # Open session
         SED_Serial.SSCDriveVerify(binResponse=True)
         SED_Serial.SEDdiscovery()
         SED_Serial.authenStartSess()
         SED_Serial.authenSIDSMaker(default = 0, firstRun = 0, handleFail=1)

         objMsg.printMsg("*** Verify SED lifestate ***")
         try: 
            LifeState = binascii.hexlify(SED_Serial.getStateTable())
            objMsg.printMsg("Drive is in %s state" %(LifeState))
         except:
            objMsg.printMsg("Failed checking fde state, retry ")   
            objPwrCtrl.powerCycle(useESlip=1) 
            objMsg.printMsg("sleep 30 seconds.....")  
            time.sleep(30) # wait for 30 seconds
            objMsg.printMsg("after sleep 30 seconds")

            SED_Serial.SSCDriveVerify(binResponse = True)
            SED_Serial.SEDdiscovery()
            SED_Serial.authenStartSess()
            SED_Serial.authenSIDSMaker(default = 0, firstRun = 0, handleFail=1)
            LifeState = binascii.hexlify(SED_Serial.getStateTable())
            objMsg.printMsg("Drive is in %s state" %(LifeState))

         drv_LifeState = LifeStatesDict.get(LifeState, 'INVALID')
         if CCV1:
            cm_LifeState = self.dut.driveattr.get('SED_LC_STATE', None)
         elif CCV2:
            cm_LifeState = self.dut.driveattr.get('SED_LC_STATE', DriveAttributes['SED_LC_STATE'])

         try: 
            dcm_LifeState = self.dut.driveConfigAttrs['SED_LC_STATE'][1].rstrip()
         except:
            dcm_LifeState = "USE"

         if drv_LifeState == cm_LifeState == dcm_LifeState:
            objMsg.printMsg("SED LifeState verification PASS...")
         else:
            objMsg.printMsg("LifeState verification, drv %s, cm %s, dcm %s. FAIL" % (drv_LifeState, cm_LifeState, dcm_LifeState))
            ScrCmds.raiseException(14862, "Drive LifeState verification FAIL")

         objMsg.printMsg("*** Drive port status verification ***")
         objMsg.printMsg("Check firmware download port..")
         dcm_DLP = self.dut.driveConfigAttrs['DLP_SETTING'][1].rstrip()
         if CCV1:
            cm_DLP = self.dut.driveattr.get('DLP_SETTING', None)
         elif CCV2:
            cm_DLP = self.dut.driveattr.get('DLP_SETTING', DriveAttributes['DLP_SETTING'])

         if dcm_DLP == cm_DLP:
            objMsg.printMsg("\tFirmware DLP verification between dcm and cm attribute PASS...")
         else:
            objMsg.printMsg("\tFirmware DLP verification, dcm %s cm %s. FAIL" % (dcm_DLP, cm_DLP))
            ScrCmds.raiseException(12972, "Firmware DLP verification between dcm and cm FAIL")

         if cm_DLP == 'UNLOCKED':
            SED_Serial.checkPortLocking(UIDname = SED_Serial.UID_fwLockingPort, configEnableLORPort = False, configEnablePortLocking = False)
         elif cm_DLP == 'LOCKED':
            SED_Serial.checkPortLocking(UIDname = SED_Serial.UID_fwLockingPort, configEnableLORPort = True, configEnablePortLocking = True)
         objMsg.printMsg("\tFirmware DLP verification between drive and cm attribute PASS...")

         objMsg.printMsg("Check serial diag port is locked..")
         SED_Serial.checkPortLocking(UIDname = SED_Serial.UID_diagLockingPort, configEnableLORPort = True, configEnablePortLocking = True)

         objMsg.printMsg("Check UDS port is locked..")
         SED_Serial.checkPortLocking(UIDname = SED_Serial.UID_udsLockingPort, configEnableLORPort = True, configEnablePortLocking = True)

         objMsg.printMsg("Check cross segment port is locked..")
         if TCG_VERSION == 2:  #All TCG2 products support CSFW download port.
            SED_Serial.checkPortLocking(UIDname = SED_Serial.UID_crossSegFwDnldPort, configEnableLORPort = True, configEnablePortLocking = True)
         elif SED_Serial.sedVar.secureBaseDriveType == 1:
            SED_Serial.checkPortLocking(UIDname = SED_Serial.UID_crossSegFwDnldPort, configEnableLORPort = True, configEnablePortLocking = True)

         objMsg.printMsg("Check IEEE port..")
         dcm_ieee = str(self.dut.driveConfigAttrs.get('IEEE1667_INTF', (0,None))[1]).rstrip()
         if CCV1:
            cm_ieee = self.dut.driveattr.get('IEEE1667_INTF', None)
         elif CCV2:
            cm_ieee = self.dut.driveattr.get('IEEE1667_INTF', DriveAttributes['IEEE1667_INTF'])
         if dcm_ieee != 'None':
            if dcm_ieee != cm_ieee:
               ScrCmds.raiseException(12972, "IEEE port verification between dcm and cm FAIL")

         if cm_ieee in [None,'NA','NONE','ACTIVATED']:
            SED_Serial.checkPortLocking(UIDname = SED_Serial.UID_ieee1667Port, configEnableLORPort = False, configEnablePortLocking = False)
         else:                                                                                                
            SED_Serial.checkPortLocking(UIDname = SED_Serial.UID_ieee1667Port, configEnableLORPort = False, configEnablePortLocking = True)

         objMsg.printMsg("Port verification PASS...")

         objMsg.printMsg("*** Verify drive SOM ***")
         packet = SED_Serial.getTable(UID = SED_Serial.UID_SetSOM0)
         SOMstate = int(binascii.hexlify(packet[64:65]),16)   #SOM State is indexed into this packet

         if SOMstate != 0:
            ScrCmds.raiseException(10158, "Checking SOM State failed. Expected SOM State to be 0 but was actually %d %s" % (SOMstate,traceback.format_exc()))

         objMsg.printMsg("SOM verification PASS...")

         objMsg.printMsg("*** Verify drive security type ***")
         #check drive's security type against dcm requirement
         dcm_SecType = self.dut.driveConfigAttrs['SECURITY_TYPE'][1].rstrip()
         if CCV1:
            cm_SecType = self.dut.driveattr.get('SECURITY_TYPE', None)
         elif CCV2:
            cm_SecType = self.dut.driveattr.get('SECURITY_TYPE', DriveAttributes['SECURITY_TYPE'])

         if dcm_SecType == cm_SecType:
            objMsg.printMsg("Drive security type verification PASS...")
         else:
            objMsg.printMsg("Drive security type verification, dcm %s cm %s. FAIL" % (dcm_SecType, cm_SecType))
            ScrCmds.raiseException(14761, "Drive security type verification FAIL")

         #Close session
         SED_Serial.closeSession()
         self.dut.TCGComplete = False
         self.dut.SkipY2 = Y2backup
         objPwrCtrl.powerCycle(useESlip=1) #to temporarly unlock diag port for subsequent tests

      else:
         objMsg.printMsg("Security verification in IO mode..")
         objMsg.printMsg("*** Verify SED lifestate ***")
         from Process import CProcess
         self.oProcess = CProcess()
         #Drive power cycle to ensure ports are locked
         self.dut.TCGComplete = True #prevent powercycle method from unlocking drive
         objPwrCtrl.powerCycle(5000,12000,10,30, ataReadyCheck = True)

         #TCG Init
         oTCG = CTCGPrepTest(self.dut, self.params) 

         #Set CPC Support
         self.SetCPCSupport()

         #Ask the drive's FDE state
         drv_LifeState = self.CheckFDEState()

         if CCV1:
            cm_LifeState = self.dut.driveattr.get('SED_LC_STATE', None)
         elif CCV2:
            cm_LifeState = self.dut.driveattr.get('SED_LC_STATE', DriveAttributes['SED_LC_STATE'])

         try: 
            dcm_LifeState = self.dut.driveConfigAttrs['SED_LC_STATE'][1].rstrip()
         except:
            dcm_LifeState = "USE"

         if drv_LifeState == cm_LifeState == dcm_LifeState:
            objMsg.printMsg("SED LifeState verification PASS...")
         else:
            objMsg.printMsg("LifeState verification, drive %s, cm %s, dcm %s. FAIL" % (drv_LifeState, cm_LifeState, dcm_LifeState))
            ScrCmds.raiseException(14862, "Drive LifeState verification FAIL")


         objMsg.printMsg("*** Verify Port setting ***")
         self.OpenAdminSession()

         objMsg.printMsg("Check firmware download port..")
         dcm_DLP = self.dut.driveConfigAttrs['DLP_SETTING'][1].rstrip()
         if CCV1:
            cm_DLP = self.dut.driveattr.get('DLP_SETTING', None)
         elif CCV2:
            cm_DLP = self.dut.driveattr.get('DLP_SETTING', DriveAttributes['DLP_SETTING'])

         if dcm_DLP == cm_DLP:
            objMsg.printMsg("\tFirmware DLP verification between dcm and cm attribute PASS...")
         else:
            objMsg.printMsg("\tFirmware DLP verification, dcm %s cm %s. FAIL" % (dcm_DLP, cm_DLP))
            ScrCmds.raiseException(12972, "Firmware DLP verification between dcm and cm FAIL")

         if cm_DLP == 'UNLOCKED':
            self.checkPortLocking(PortName = 'FWDownload', configEnableLORPort = False, configEnablePortLocking = False)
         elif cm_DLP == 'LOCKED':
            self.checkPortLocking(PortName = 'FWDownload', configEnableLORPort = True, configEnablePortLocking = True)
         objMsg.printMsg("\tFirmware DLP verification between drive and cm attribute PASS...")

         objMsg.printMsg("Check serial diag port is locked..")
         self.checkPortLocking(PortName = 'Diag', configEnableLORPort = True, configEnablePortLocking = True)

         objMsg.printMsg("Check UDS port is locked..")
         self.checkPortLocking(PortName = 'UDS', configEnableLORPort = True, configEnablePortLocking = True)

         objMsg.printMsg("Check cross segment port is locked..")
         if TCG_VERSION == 2:  #All TCG2 products support CSFW download port.
            self.checkPortLocking(PortName = 'CSegDld', configEnableLORPort = True, configEnablePortLocking = True)
        
         objMsg.printMsg("Check IEEE port..")
         dcm_ieee = str(self.dut.driveConfigAttrs.get('IEEE1667_INTF', (0,None))[1]).rstrip()
         if CCV1:
            cm_ieee = self.dut.driveattr.get('IEEE1667_INTF', None)
         elif CCV2:
            cm_ieee = self.dut.driveattr.get('IEEE1667_INTF', DriveAttributes['IEEE1667_INTF'])
         if dcm_ieee != 'None':
            if dcm_ieee != cm_ieee:
               ScrCmds.raiseException(12972, "IEEE port verification between dcm and cm FAIL")

         if cm_ieee in [None,'NA','NONE','ACTIVATED']:
            self.checkPortLocking(PortName = 'IEEE1667Port', configEnableLORPort = False, configEnablePortLocking = False)
         else:   
            self.checkPortLocking(PortName = 'IEEE1667Port', configEnableLORPort = False, configEnablePortLocking = True)
        
         objMsg.printMsg("Port verification PASS...")

         objMsg.printMsg("*** Verify drive SOM ***")

         packet = self.getTable(PortName = 'SOMState')
         SOMstate = int(binascii.hexlify(packet[58:59]),16)   #IO getTable return less 6 bytes of data compared to SPIO getTable

         if SOMstate != 0:
            ScrCmds.raiseException(10158, "Checking SOM State failed. Expected SOM State to be 0 but was actually %d %s" % (SOMstate,traceback.format_exc()))

         objMsg.printMsg("SOM verification PASS...")

         objMsg.printMsg("*** Verify drive security type ***")

         #check drive's security type against dcm requirement
         dcm_SecType = self.dut.driveConfigAttrs['SECURITY_TYPE'][1].rstrip()
         if CCV1:
            cm_SecType = self.dut.driveattr.get('SECURITY_TYPE', None)
         elif CCV2:
            cm_SecType = self.dut.driveattr.get('SECURITY_TYPE', DriveAttributes['SECURITY_TYPE'])

         if dcm_SecType == cm_SecType:
            objMsg.printMsg("Drive security type verification PASS...")
         else:
            objMsg.printMsg("Drive security type verification, dcm %s cm %s. FAIL" % (dcm_SecType, cm_SecType))
            ScrCmds.raiseException(14761, "Drive security type verification FAIL")

         #Close session
         self.CloseAdminSession()

         self.dut.TCGComplete = False
         objPwrCtrl.powerCycle(5000,12000,10,30, ataReadyCheck = True)

      return PASS

   #-------------------------------------------------------------------------------------------------------
   def checkPortLocking(self, PortName,configEnableLORPort = True, configEnablePortLocking = True):
      """
      Check port's "Lock On Reset" setting and "Locked/Unlocked" status
      """
      packet = self.getTable(PortName)

      LORPort,LockingPort = self.parsePortLockingData(packet)
      objMsg.printMsg("checkPortLocking: LORPort:%s LockingPort:%s" % (LORPort,LockingPort))

      if configEnableLORPort:
         configLORPort = '\x00'
      else:
         configLORPort = '\xf1'

      if configEnablePortLocking:
         configPortLocking = '\x01'
      else:
         configPortLocking = '\x00'

      if LORPort != configLORPort:
         ScrCmds.raiseException(12972,  "LOR status for %s is not configured correctly. Specified configuration %s" % (PortName, configEnableLORPort))

      if LockingPort != configPortLocking:
         ScrCmds.raiseException(12972,  "Port Locking for %s is not configured correctly. Specified configuration %s" % (PortName, configEnablePortLocking))

   #-------------------------------------------------------------------------------------------------------
   def getTable(self, PortName = None ):
      """
      Get port status table
      """
      UID_Table = {
                  'FWDownload'      : 0x0001000200010002,
                  'Diag'            : 0x0001000200010001,
                  'UDS'             : 0x0001000200010003,
                  'CSegDld'         : 0x000100020001000e,
                  'IEEE1667Port'    : 0x000100020001000f,
                  'SOMState'        : 0x0001000700000000,
                  }
      #oProcess = CProcess()
      objMsg.printMsg("Get %s table" % PortName)

      prm_575_GetPortStatusTable = {
         'test_num'        : 575,
         'prm_name'        : 'prm_575_GetPortStatusTable',
         "TEST_MODE"       : (0x0005,),     ##TestMode         (Prm[0] & 0xff)  = Get Table
         "REPORTING_MODE"  : (0x0001,),##ReportingMode    (Prm[0] & 0x8000)
         "WHICH_SP"        : (0x0000,),     ##WhichSP          (Prm[1] & 0xff)
         "PASSWORD_TYPE"   : (0x0000,),     #PasswordType      (Prm[2] & 0xff)
         "DRIVE_STATE"     : (0x0000,),     ##DriveState       (Prm[8] & 0xff)
         "UIDMSWU"         : (0x0001,),     ##UidMSWU           Prm[4]
         "UIDMSWL"         : (0x0002,),     ##UidMSWL           Prm[5]
         "UIDLSWU"         : (0x0001,),     ##UidLSWU           Prm[6]
         "UIDLSWL"         : (0x0002,),     ##UidLSWl           Prm[7]
         "CERT_TSTMODE"    : (0x0000,),     ##CertTestMode     (Prm[2] & 0xff)
         "CERT_KEYTYPE"    : (0x0000,),     ##CertKeyType      ((Prm[2] & 0xff00) >> 8)
         "DblTablesToParse" : ('P57X_FRAME_DATA',),
      }

      prm_575_GetPortStatusTable["prm_name"] = 'prm_575_Get' + PortName + 'PortStatusTable'
      prm_575_GetPortStatusTable["UIDMSWU"] = (UID_Table[PortName]>>48) & 0xFFFF
      prm_575_GetPortStatusTable["UIDMSWL"] = (UID_Table[PortName]>>32) & 0xFFFF
      prm_575_GetPortStatusTable["UIDLSWU"] = (UID_Table[PortName]>>16) & 0xFFFF
      prm_575_GetPortStatusTable["UIDLSWL"] = (UID_Table[PortName]) & 0xFFFF

      self.oProcess.St(prm_575_GetPortStatusTable,timeout=360)
      
      table = self.dut.objSeq.SuprsDblObject['P57X_FRAME_DATA']
      if DEBUG:
         objMsg.printMsg("%s table data - %s" % (PortName, table))

      import re
      col = re.compile('[\d]')
      data = []
      for row in table:
         if DEBUG:
            objMsg.printMsg("row = %s" % row)
         data1 = []
         data2 = []

         for key in sorted(row.keys()):
            if col.match(key):
               if len(key) == 1:
                  data1.append(row[key])
               else:
                  data2.append(row[key])

         data3 = data1 + data2
         objMsg.printMsg("data3 = %s" % data3)
         data.append(data3)

      if DEBUG:
         objMsg.printMsg("Extracted data = %s" % data)

      finalData = []
      for row in data:
         if DEBUG:
            objMsg.printMsg("Row = %s" % row)
         finalData = finalData + row

      if DEBUG:
         objMsg.printMsg("Consolidated data = %s" % finalData)

      finalData = "".join(finalData)
      finalData = binascii.unhexlify(finalData)
      finalData = finalData[96:] #remove 95 bytes of tx
      objMsg.printMsg("%s table data - %s" % (PortName, finalData))

      return finalData

   #-------------------------------------------------------------------------------------------------------
   def parsePortLockingData(self, data=''):
      """
      Used to parse port locking data
      """
      LockType_FWDownload = '\x46\x57\x44\x6f\x77\x6e\x6c\x6f\x61\x64'
      LockType_Diagnostics = '\x44\x69\x61\x67\x6e\x6f\x73\x74\x69\x63\x73'
      LockType_UDS = '\x55\x44\x53'
      LockType_CSFW = '\x43\x53\x46\x57\x44\x6f\x77\x6e\x6c\x6f\x61\x64'
      LockType_ieee1667= '\x12\x41\x63\x74\x69\x76\x61\x74\x69\x6f\x6e\x49\x45\x45\x45\x31\x36\x36\x37'

      breakOuterLoop = 0
      index = 0
      dataLength = len(data) 

      for index in range(0,dataLength):
         if breakOuterLoop ==1:
            break
         if DEBUG:
            objMsg.printMsg("index: %s" % index)
         if (data[index:index+len(LockType_FWDownload)] == LockType_FWDownload) or (data[index:index+len(LockType_Diagnostics)] == LockType_Diagnostics) or (data[index:index+len(LockType_UDS)] == LockType_UDS) or (data[index:index+len(LockType_CSFW)] == LockType_CSFW) or (data[index:index+len(LockType_ieee1667)] == LockType_ieee1667):     
            nameColumn = data[index-2:index-1]
            for tempIndx in range(index,dataLength):
               if DEBUG:
                  objMsg.printMsg("tempIndx: %s" % tempIndx)
                  objMsg.printMsg("data[tempIndx:tempIndx+2]: %s" % data[tempIndx:tempIndx+2])
                  objMsg.printMsg("data[tempIndx:tempIndx+3]: %s" % data[tempIndx:tempIndx+3])

               if (data[tempIndx:tempIndx+2] == '\xf3\xf2'):
                  tempNameColumn = binascii.a2b_hex('0' + str(int(binascii.hexlify(nameColumn),16)+1))
                  if data[tempIndx+2:tempIndx+3] == tempNameColumn:
                     nameColumn = binascii.a2b_hex('0' + str(int(binascii.hexlify(nameColumn),16) + 1))
                     LORkey = data[tempIndx+4:tempIndx+5]
               elif (data[tempIndx:tempIndx+3] == '\xf1\xf3\xf2'):
                  tempNameColumn = binascii.a2b_hex('0' + str(int(binascii.hexlify(nameColumn),16)+1))
                  if data[tempIndx+3:tempIndx+4] == tempNameColumn:
                     LockPortkey = data[tempIndx+4:tempIndx+5]
                     breakOuterLoop = 1
                     break

      return LORkey,LockPortkey

   #-------------------------------------------------------------------------------------------------------
   def GetSOMState(self):
      """
      Get drive's SOM state
      """
      #oProcess = CProcess()
      GetSOM0 = {
         'test_num'        : 575,
         'prm_name'        : 'prm_575_15',
         "TEST_MODE"       : (0x001B,),     ##TestMode         (Prm[0] & 0xff)
         "REPORTING_MODE"  : (0x8000,),     ##ReportingMode    (Prm[0] & 0x8000)
         "WHICH_SP"        : (0x0000,),     ##WhichSP          (Prm[1] & 0xff)
         "PASSWORD_TYPE"   : (0x0002,),     #PasswordType      (Prm[2] & 0xff)
         "DRIVE_STATE"     : (0x0000,),     ##DriveState       (Prm[8] & 0xff)
         "UIDMSWU"         : (0x0000,),     ##UidLswu           Prm[4]
         "UIDMSWL"         : (0x0000,),     ##UidLswu           Prm[5]
         "UIDLSWU"         : (0x0007,),     ##UidLswu           Prm[6]
         "UIDLSWL"         : (0x0001,),     ##UidLswl           Prm[7]
         "CERT_TSTMODE"    : (0x0000,),     ##CertTestMode     (Prm[2] & 0xff)
         "CERT_KEYTYPE"    : (0x0000,),     ##CertKeyType      ((Prm[2] & 0xff00) >> 8)
      }
      SetFailSafe()
      try:
         if not objRimType.isIoRiser():
            SOM = SED_Serial.getStateTable()
         else:
            SOM = self.oProcess.St(GetSOM0,timeout=360)
      except:
         pass
      objMsg.printMsg("SOM status: %s" % SOM)
      ClearFailSafe()

   #-------------------------------------------------------------------------------------------------------
   def SetCPCSupport(self):

      if DEBUG:   REPORTING_MODE = (0x0001,)
      else:       REPORTING_MODE = (0x0000,)
      self.prm_575_SetCPCSupport = {
         'test_num'        : 575,
         'prm_name'        : 'prm_575_SetCPCSupport',
         "TEST_MODE"       : (0x0023,),      ##TestMode         (Prm[0] & 0xff)  
         "CORE_SPEC"       : (0x0002),       ##OpalSSC          (Prm[0] & 0xff)     #CS2.0
         "SSC_VERSION"     : (0x0001),       ##OpalSSC          (Prm[0] & 0xff)     #OpalSSC      
         "REPORTING_MODE"  : REPORTING_MODE, ##ReportingMode    (Prm[0] & 0x8000)
         "WHICH_SP"        : (0x0000,),      ##WhichSP          (Prm[1] & 0xff)
         "PASSWORD_TYPE"   : (0x0000,),      ##PasswordType     (Prm[2] & 0xff)
         "DRIVE_STATE"     : (0x0000,),      ##DriveState       (Prm[8] & 0xff)
         "UIDMSWU"         : (0x0000,),      ##UidLswu           Prm[4]
         "UIDMSWL"         : (0x0000,),      ##UidLswu           Prm[5]
         "UIDLSWU"         : (0x0000,),      ##UidLswu           Prm[6]
         "UIDLSWL"         : (0x0000,),      ##UidLswl           Prm[7]
         "CERT_TSTMODE"    : (0x0000,),      ##CertTestMode     (Prm[2] & 0xff)
         "CERT_KEYTYPE"    : (0x0000,),      ##CertKeyType      ((Prm[2] & 0xff00) >> 8)
      }
      self.SEDprm_AutoDetect = self.Is_SEDprm_AutoDetect()
      if self.SEDprm_AutoDetect:
         del self.prm_575_SetCPCSupport["SSC_VERSION"]
         self.prm_575_SetCPCSupport.update({"OPAL_SSC_SUPPORT" : 1})
  
      objMsg.printMsg("Running test 575 - Setting CS1.0/2.0 and EntSSC/OpalSSC support")
      self.prm_575_SetCPCSupport["CORE_SPEC"] = getattr(TP,"prm_TCG",{}).get('CORE_SPEC', 0x0002)
      if not self.SEDprm_AutoDetect:
         self.prm_575_SetCPCSupport["SSC_VERSION"]      = getattr(TP,"prm_TCG",{}).get('SSC_VERSION', 0x0001)
      self.prm_575_SetCPCSupport["MASTER_AUTHORITY"] = getattr(TP,"prm_TCG",{}).get('MASTER_AUTHORITY', 0x0001)

      if testSwitch.FE_0154366_231166_P_FDE_OPAL_SUPPORT:
         if getattr(TP,"prm_TCG",{}).get('SSC_VERSION', 0x0001) == 1:
            self.prm_575_SetCPCSupport["MAINTSYMK_SUPP"]=1
            self.prm_575_SetCPCSupport["SYMK_KEY_TYPE"]=2
            self.prm_575_SetCPCSupport["MASTER_PW_REV_CODE"]=0xFFFE
      
      if DEBUG:
         # DEBUG_FLAG is used to force specify PSID Support, (a new properlly named 
         # parameter is in the works for that,)  this is due to a difference in how 
         # test 577 Starts between CPC and Sata Initiaotr.
         self.prm_575_SetCPCSupport['DEBUG_FLAG'] = 1

      self.oProcess.St(self.prm_575_SetCPCSupport,timeout=360)

   #-------------------------------------------------------------------------------------------------------
   def CheckFDEState(self):
      """
      Get drive's life cycle state
      """
      LifeStatesDict = {
                     '00': 'SETUP',
                     '01': 'DIAG',
                     '80': 'USE',
                     '81': 'MFG',
                     'FF': 'INVALID',
                   }
      objMsg.printMsg("*** T575 - Discovery ")
      prm_575_01 = {
         'test_num'        : 575,
         'prm_name'        : 'prm_575_01',
         "TEST_MODE"       : (0x0007,),     ##TestMode         (Prm[0] & 0xff)
         "REPORTING_MODE"  : (0x8000,),     ##ReportingMode    (Prm[0] & 0x8000)
         "WHICH_SP"        : (0x0000,),     ##WhichSP          (Prm[1] & 0xff)
         "PASSWORD_TYPE"   : (0x0000,),     #PasswordType      (Prm[2] & 0xff)     0 - Default
         "DRIVE_STATE"     : (0x0000,),     ##DriveState       (Prm[8] & 0xff)
         "UIDMSWU"         : (0x0000,),     ##UidLswu           Prm[4]
         "UIDMSWL"         : (0x0205,),     ##UidLswu           Prm[5]
         "UIDLSWU"         : (0x0000,),     ##UidLswu           Prm[6]
         "UIDLSWL"         : (0x0001,),     ##UidLswl           Prm[7]
         "CERT_TSTMODE"    : (0x0000,),     ##CertTestMode     (Prm[2] & 0xff)
         "CERT_KEYTYPE"    : (0x0000,),     ##CertKeyType      ((Prm[2] & 0xff00) >> 8)
         "DblTablesToParse": ['P575_DEVICE_DISC_DATA',]          ##Parse out dblog data
      }
      self.oProcess.St(prm_575_01,timeout=360)

      if testSwitch.virtualRun:
         LifeState = '80'
      else:
         LifeState = self.dut.objSeq.SuprsDblObject['P575_DEVICE_DISC_DATA'][-1]['LIFE_CYCLE_STATE']

      return LifeStatesDict.get(LifeState, 'INVALID')

   #-------------------------------------------------------------------------------------------------------
   def Is_SEDprm_AutoDetect(self):

      if objRimType.SerialOnlyRiser() or testSwitch.NoIO: #In serial cell OR NoIO mode, don't care about RimCodeVer
         return False

      auto_detect = False
      rim_ver = ICmd.getRimCodeVer()
      if objRimType.CPCRiser():
         try:
            float(rim_ver)
         except ValueError:
            objMsg.printMsg("Beta version detected, not a float value")
            rim_ver = rim_ver[:-1]
            objMsg.printMsg("Beta RimCodeVer %s" % rim_ver)
         if (float(rim_ver) > 2.254):
            auto_detect = True

      elif objRimType.IOInitRiser():
         Patt = re.compile('REL.SATA.(?P<SIC_VER>[\d]+).')
         Mat = Patt.search(rim_ver)
         if Mat:
            SIC = Mat.groupdict()['SIC_VER']
            if int(SIC) >= 688021:
               auto_detect = True

      return auto_detect

   #-------------------------------------------------------------------------------------------------------
   def OpenAdminSession(self):

      objMsg.printMsg("Open Admin session")

      prm_575_03 = {
        'test_num'        : 575,
        'prm_name'        : 'prm_575_03',
        "TEST_MODE"       : (0x0002,),       ##TestMode         (Prm[0] & 0xff) = Start Session
        "REPORTING_MODE"  : (0x8000,),       ##ReportingMode    (Prm[0] & 0x8000)
        "WHICH_SP"        : (0x0000,),       ##WhichSP          (Prm[1] & 0xff)
        "PASSWORD_TYPE"   : (0x0000,),       ##PasswordType     (Prm[2] & 0xff)
        "DRIVE_STATE"     : (0x0000,),       ##DriveState       (Prm[8] & 0xff)
        "UIDMSWU"         : (0x0000,),       ##UidLswu           Prm[4]
        "UIDMSWL"         : (0x0205,),       ##UidLswu           Prm[5]
        "UIDLSWU"         : (0x0000,),       ##UidLswu           Prm[6]
        "UIDLSWL"         : (0x0001,),       ##UidLswl           Prm[7]
        "CERT_TSTMODE"    : (0x0000,),       ##CertTestMode     (Prm[2] & 0xff)
        "CERT_KEYTYPE"    : (0x0000,),       ##CertKeyType      ((Prm[2] & 0xff00) >> 8)
      }
      objMsg.printMsg("Start Admin session")
      self.oProcess.St(prm_575_03,timeout=360)

      prm_575_06 = {
        'test_num'        : 575,
        'prm_name'        : 'prm_575_06',
        "TEST_MODE"       : (0x0001,),     ##TestMode         (Prm[0] & 0xff)   = Authenticate
        "REPORTING_MODE"  : (0x8000,),     ##ReportingMode    (Prm[0] & 0x8000)
        "WHICH_SP"        : (0x0000,),     ##WhichSP          (Prm[1] & 0xff)
        "PASSWORD_TYPE"   : (0x0001,),     #PasswordType      (Prm[2] & 0xff)   = UNIQUE_MAKERSYMK
        "DRIVE_STATE"     : (0x0000,),     ##DriveState       (Prm[8] & 0xff)
        "UIDMSWU"         : (0x0000,),     ##UidLswu           Prm[4]
        "UIDMSWL"         : (0x0009,),     ##UidLswu           Prm[5]
        "UIDLSWU"         : (0x0000,),     ##UidLswu           Prm[6]
        "UIDLSWL"         : (0x0004,),     ##UidLswl           Prm[7]
        "CERT_TSTMODE"    : (0x0000,),     ##CertTestMode     (Prm[2] & 0xff)
        "CERT_KEYTYPE"    : (0x0000,),     ##CertKeyType      ((Prm[2] & 0xff00) >> 8)
      }
      self.SSC = getattr(TP,"prm_TCG",{}).get('SSC_VERSION', 0x0001)
      if self.SSC == 1 and testSwitch.FE_0154366_231166_P_FDE_OPAL_SUPPORT:
         prm_575_06['PASSWORD_TYPE'] = 14

      objMsg.printMsg("Authenticate to MakerSymk")
      self.oProcess.St(prm_575_06,timeout=360)

      prm_575_04 = {
        'test_num'        : 575,
        'prm_name'        : 'prm_575_04',
        "TEST_MODE"       : (0x0011,),     ##TestMode         (Prm[0] & 0xff)   = Get MSID From Drive
        "REPORTING_MODE"  : (0x8000,),     ##ReportingMode    (Prm[0] & 0x8000)
        "WHICH_SP"        : (0x0000,),     ##WhichSP          (Prm[1] & 0xff)
        "PASSWORD_TYPE"   : (0x0000,),     #PasswordType      (Prm[2] & 0xff)   = DEFAULT MSID
        "DRIVE_STATE"     : (0x0000,),     ##DriveState       (Prm[8] & 0xff)
        "UIDMSWU"         : (0x0000,),     ##UidLswu           Prm[4]
        "UIDMSWL"         : (0x0000,),     ##UidLswu           Prm[5]
        "UIDLSWU"         : (0x0000,),     ##UidLswu           Prm[6]
        "UIDLSWL"         : (0x0000,),     ##UidLswl           Prm[7]
        "CERT_TSTMODE"    : (0x0000,),     ##CertTestMode     (Prm[2] & 0xff)
        "CERT_KEYTYPE"    : (0x0000,),     ##CertKeyType      ((Prm[2] & 0xff00) >> 8)
      }
      objMsg.printMsg("Get MSID from Drive")
      self.oProcess.St(prm_575_04,timeout=360)      

      prm_575_07 = {
        'test_num'        : 575,
        'prm_name'        : 'prm_575_07',
        "TEST_MODE"       : (0x0001,),     ##TestMode         (Prm[0] & 0xff)   = Authenticate
        "REPORTING_MODE"  : (0x8000,),     ##ReportingMode    (Prm[0] & 0x8000)
        "WHICH_SP"        : (0x0000,),     ##WhichSP          (Prm[1] & 0xff)
        "PASSWORD_TYPE"   : (0x0002,),     #PasswordType      (Prm[2] & 0xff)   = MSID
        "DRIVE_STATE"     : (0x0000,),     ##DriveState       (Prm[8] & 0xff)
        "UIDMSWU"         : (0x0000,),     ##UidLswu           Prm[4]
        "UIDMSWL"         : (0x0009,),     ##UidLswu           Prm[5]
        "UIDLSWU"         : (0x0000,),     ##UidLswu           Prm[6]
        "UIDLSWL"         : (0x0006,),     ##UidLswl           Prm[7]
        "CERT_TSTMODE"    : (0x0000,),     ##CertTestMode     (Prm[2] & 0xff)
        "CERT_KEYTYPE"    : (0x0000,),     ##CertKeyType      ((Prm[2] & 0xff00) >> 8)
      }
      objMsg.printMsg("Authenticate to sid")
      self.oProcess.St(prm_575_07,timeout=360)

      prm_575_psid_from_fis = {
         'test_num'        : 575,
         'prm_name'        : 'prm_575_psid_from_fis',
         'TEST_MODE'       : 0x0024,                  # TestMode         (Prm[0] & 0xff)   = Authenticate
         'REPORTING_MODE'  : 0x8000,                  # ReportingMode    (Prm[0] & 0x8000)
         'WHICH_SP'        : 0x0000,                  # WhichSP          (Prm[1] & 0xff)
         'PASSWORD_TYPE'   : 0x000A,                  # PasswordType     (Prm[2] & 0xff)   = DEFAULT PSID
         'DRIVE_STATE'     : 0x0000,                  # DriveState       (Prm[8] & 0xff)
         'UIDMSWU'         : 0x0000,                  # UidLswu           Prm[4]
         'UIDMSWL'         : 0x0009,                  # UidLswu           Prm[5]
         'UIDLSWU'         : 0x0001,                  # UidLswu           Prm[6]
         'UIDLSWL'         : 0xff01,                  # UidLswl           Prm[7]
         'CERT_TSTMODE'    : 0x0000,                  # CertTestMode     (Prm[2] & 0xff)
         'CERT_KEYTYPE'    : 0x0000,                  # CertKeyType      ((Prm[2] & 0xff00) >> 8)
         }
      objMsg.printMsg('Get PSID from FIS')
      self.oProcess.St(prm_575_psid_from_fis,timeout=360)

      psid_auth = {
        'test_num'        : 575,
        'prm_name'        : 'psid_auth',
        "TEST_MODE"       : (0x0001,),     ##TestMode         (Prm[0] & 0xff)   = Authenticate
        "REPORTING_MODE"  : (0x8000,),     ##ReportingMode    (Prm[0] & 0x8000)
        "WHICH_SP"        : (0x0000,),     ##WhichSP          (Prm[1] & 0xff)
        "PASSWORD_TYPE"   : (0x0009,),     #PasswordType      (Prm[2] & 0xff)   = MSID
        "DRIVE_STATE"     : (0x0000,),     ##DriveState       (Prm[8] & 0xff)
        "UIDMSWU"         : (0x0000,),     ##UidLswu           Prm[4]
        "UIDMSWL"         : (0x0009,),     ##UidLswu           Prm[5]
        "UIDLSWU"         : (0x0001,),     ##UidLswu           Prm[6]
        "UIDLSWL"         : (0xff01,),     ##UidLswl           Prm[7]
        "CERT_TSTMODE"    : (0x0000,),     ##CertTestMode     (Prm[2] & 0xff)
        "CERT_KEYTYPE"    : (0x0000,),     ##CertKeyType      ((Prm[2] & 0xff00) >> 8)
      }
      objMsg.printMsg("Authenticate to psid")
      self.oProcess.St(psid_auth,timeout=360)

   #-------------------------------------------------------------------------------------------------------
   def CloseAdminSession(self):
      objMsg.printMsg("Close Admin session")

      prm_575_12 = {
           'test_num'        : 575,
           'prm_name'        : 'prm_575_12',
           "TEST_MODE"       : (0x0003,),      ##TestMode         (Prm[0] & 0xff)
           "REPORTING_MODE"  : (0x8000,),       ##ReportingMode    (Prm[0] & 0x8000)
           "WHICH_SP"        : (0x0000,),       ##WhichSP          (Prm[1] & 0xff)
           "PASSWORD_TYPE"   : (0x0000,),       ##PasswordType     (Prm[2] & 0xff)
           "DRIVE_STATE"     : (0x0000,),       ##DriveState       (Prm[8] & 0xff)
           "UIDMSWU"         : (0x0000,),       ##UidLswu           Prm[4]
           "UIDMSWL"         : (0x0205,),       ##UidLswu           Prm[5]
           "UIDLSWU"         : (0x0000,),       ##UidLswu           Prm[6]
           "UIDLSWL"         : (0x0001,),       ##UidLswl           Prm[7]
           "CERT_TSTMODE"    : (0x0000,),       ##CertTestMode     (Prm[2] & 0xff)
           "CERT_KEYTYPE"    : (0x0000,),       ##CertKeyType      ((Prm[2] & 0xff00) >> 8)
        }
      objMsg.printMsg("Close Admin session")
      self.oProcess.St(prm_575_12,timeout=360)

###########################################################################################################

class CSMARTReset_CCV(CState):
   """
      Class that performs Reset SMART
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)

   #---------------------------------------------------------------------------------------------------------#
   def run(self):
      
      objMsg.printMsg("Reset SMART")
      oSerial = serialScreen.sptDiagCmds()
      sptCmds.enableDiags()

      oSerial.sendDiagCmd('/1N1', printResult = True)
      objMsg.printMsg("Reset SMART PASS")

      return PASS

###########################################################################################################

class CUDSReset_CCV(CState):
   """
      Class resetting Unified Debug System 
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      objMsg.printMsg("Reset UDS")
      sptCmds.enableDiags()
      oSerial = serialScreen.sptDiagCmds()

      smartUDSResetParams = {
         'options'                  : [0x25],
         'initFastFlushMediaCache'  : 1,
         'timeout'                  : 120,
         'retries'                  : 2,
         }
      oSerial.SmartCmd(smartUDSResetParams, dumpDEBUGResponses=1)
      objMsg.printMsg("Reset UDS PASS")

      if not testSwitch.NoIO: #switch to interface mode for subsequent IO tests
         objPwrCtrl.powerCycle(5000,12000,10,30, ataReadyCheck = False)
      return PASS

###########################################################################################################
class CRogueFWDetect_CCV(CState):
   """
   This function uses a special TPM file to extract the FW signatures
   from the drive.  This information is then compared to FW signatures from
   an original FW build file.  They are always expected to match.  If not,
   the FW on the drive is not a Seagate original file, indicating a tampered
   FW file is in use.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)

   #---------------------------------------------------------------------------------------------------------#
   def run(self):

      objMsg.printMsg("Rogue Firmware Detection")
      from FWDetection import fwDetect
      return fwDetect.run()

###########################################################################################################
