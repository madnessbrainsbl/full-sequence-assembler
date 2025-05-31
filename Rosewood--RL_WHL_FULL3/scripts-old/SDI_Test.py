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
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/SDI_Test.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/SDI_Test.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#

import traceback

from PowerControl import objPwrCtrl
from State import CState
import MessageHandler as objMsg
from Test_Switches import testSwitch

#from Drive import objDut
#import serialScreen, sptCmds
#from Exceptions import CRaiseException

from ICmdFactory import ICmd


#---------------------------------------------------------------------------------------------------------#
def SDIParam(ovPrm):

   sdi_remap =  {
      'CTRL_WORD1' : 'Ctrl1Wrd',
      'CTRL_WORD2' : 'Ctrl2Wrd',
      'STARTING_LBA' : 'StrtLba',
      'TOTAL_BLKS_TO_XFR64' : 'TtlLbaTrnsfr64',
      'TOTAL_BLKS_TO_XFR' : 'TtlLbaTrnsfr',
      'MAXIMUM_LBA' : 'MxLba',
      'BLKS_PER_XFR' : 'NumLbaPerTrnsfr',
      'DATA_PATTERN0' : 'DtaPttrn0',
      'RANDOM_SEED' : 'RdmSeed',
      'MAX_NBR_ERRORS' : 'MxNumErr',
      'RESET_AFTER_ERROR' : 'RstAftrErr',
      'CCT_BIN_SETTINGS' : 'CctBinSetg',
      'CCT_LBAS_TO_SAVE' : 'CctLbaSav',
      'MIN_COMMAND_TIME' : 'MinCmdTm',
      'MAX_COMMAND_TIME' : 'MxCmdTm',
      'STEP_SIZE' : 'StepSz',
      'DITS_MODE' : 'DitsMode',
      'CACHE_CONTROL' : 'WrCache',
      'FULL_RETRY_CONTROL' : 'FullRtryCtrl',
      'FREE_RETRY_CONTROL' : 'DisblFreeRtry',
      'HIDDEN_RETRY_CONTROL' : 'HidnRtry',
      'RPT_HIDDEN_RETRY_CNTRL' : 'RprtHidnRtry',
      'DISABLE_ECC_ON_FLY' : 'DisblEcc',
      'ECC_CONTROL' : 'Ecc',
      'ECC_T_LEVEL' : 'Tlvl',
      'OPTIONS' : 'OptnWrd1',
      'PATTERN_MODE' : 'PttrnMode',
      'WRITE_READ_MODE' : 'WrRdMode',
      'ENABLE_HW_PATTERN_GEN' : 'HwPttrnGen',
      'DEBUG_FLAG' : 'DbgFlag',
      'COMPARE_OPTION' : 'CmprOptn',
      'BERP_OVERRIDE' : 'BerpOvrd',
      'DERP_RETRY_CONTROL' : 'DerpRtryCtrl',
      'MEASURE_TIME' : 'MeasTm',
      'MSECS_PER_CMD_SPEC' : 'MsecPerCmd',
      'TOT_CMDS_MINS_SPEC' : 'TtlCmdTmMin',
      'ENABLE_WT_SAME' : 'EnblWrSame',
      'TIMER_MAX' : 'StatChkDly',
      'STATUS_CHECK_DELAY' : 'StatChkDly',
      'RANDOM_LBA_ALIGNMENT' : 'RdmLbaAlign',           

      'TOTAL_RETRIES' : 'TtlRtry',   # Start Apple T639
      'MULTIPLIER' : 'Mult', 
      'COMMAND_TIMEOUT' : 'CmdTmout', 
      'GROUP_RETRIES' : 'GrpRtry', 
      'SAMPLE_SIZE' : 'SampSz', 
      'NUM_SAMPLES' : 'NumSamp',     # End Apple T639

      'FEATURES'              : "Feat",  # Start T538
      'SECTOR_COUNT'          : "SctrCnt",
      'SECTOR'                : "Sctr",
      'CYLINDER'              : "Cyl",
      'COMMAND'               : "Cmd",
      'HEAD'                  : "Hd",
      'DEVICE'                : "Dvce",
      'PARAMETER_0'           : "LbaModeCmd",  
      'LBA_LOW'               : "LbaLo",
      'LBA_MID'               : "LbaMid",
      'LBA_HIGH'              : "LbaHi", # End T538

      'BUFFER_LENGTH'         : "BufLen",       # Start T508
      'BYTE_OFFSET'           : "BytOfst",
      'READ_BUFFER_OFFSET'    : "RdBufOfst",
      'WRITE_BUFFER_OFFSET'   : "WrBufOfst",
      'BYTE_PATTERN_LENGTH'   : "BytPttrnLen",
      'PATTERN_TYPE'          : "PttrnTyp",
      'RANDOM_SEED'           : "RdmSeed",
      'BIT_PATTERN_LENGTH'    : "BitPttrnLen",  # End T508

   }

   ### convert dict keys ###
   for key, value in ovPrm.iteritems():
      if key in sdi_remap:
         ovPrm[sdi_remap[key]] = value
         del ovPrm[key]

   import types
   from Utility import CUtility

   ### convert tuple to int ###
   for key, value in ovPrm.iteritems():
      if type(value) == types.TupleType:
         ovPrm[key] = CUtility.reverseLbaWords(value)

   ### ensure StepSz is multiple of 8 for 4K drives ###
   if ovPrm.has_key('StepSz'):
      objMsg.printMsg('StepSz before=%s' % ovPrm['StepSz'])
      while ovPrm['StepSz'] > 0:
         if ovPrm['StepSz'] % 8 == 0:
            break
         ovPrm['StepSz'] -= 1
      objMsg.printMsg('StepSz aftere=%s' % ovPrm['StepSz'])

   return ovPrm


###########################################################################################################
###########################################################################################################
class CSDI(CState):
   """
      Provide a single call to run SDI tests. 
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def dnld_sdi(self):
      from Process import CProcess

      oProc = CProcess()

      try: 
         from TestParamExtractor import TP
         if testSwitch.SPLIT_BASE_SERIAL_TEST_FOR_CM_LA_REDUCTION:
            from Serial_Download import CDnldCode
         else:
            from base_SerialTest import CDnldCode
         oDnldCode = CDnldCode(self.dut,{'CODES':['TGTB','OVLB'],})
         oDnldCode.run()
      except: 
         objMsg.printMsg("dnldCode bridge code failed: %s" % traceback.format_exc())

      self.dut.IsSDI = True
      
      try: 
         objPwrCtrl.powerCycle()
         oProc.dnldCode('CFW', fileName='cfw_plusoverlays_SDI_0509.lod', timeout=500)  # SDI code
      except: 
         objMsg.printMsg("dnldCode SDI Failed: %s" % traceback.format_exc())

   #-------------------------------------------------------------------------------------------------------
   def parmX(self):
      from parmX import *
      parmX()

   #-------------------------------------------------------------------------------------------------------
   def handlder70(self):

      try:
         from TestParameters import overlayMap
         backup = overlayMap[self.dut.nextOper]
         overlayMap[self.dut.nextOper] = 'S_OVL'      # this must be specified in Codes.py
      except:
         objMsg.printMsg("TestParameters overlayMap Failed: %s" % traceback.format_exc())

      import FSO
      FSO.Overlay_Handler(self.dut)

      try:
         overlayMap[self.dut.nextOper] = backup      # this must be specified in Codes.py
      except:
         objMsg.printMsg("TestParameters overlayMap Restore Failed: %s" % traceback.format_exc())

   #---------------------------------------------------------------------------------------------------------#
   def run(self, sdi_cust_test = None):
      from Codes import fwConfig
      from Setup import CSetup

      try:
         backup = fwConfig[self.dut.partNum]['S_OVL']
      except:
         backup = None

      try:
         fwConfig[self.dut.partNum]['S_OVL'] = 'S_OVL.LOD'  # SDI code
         
         if not testSwitch.FE_0190240_007955_USE_FILE_LIST_FUNCTIONS_FROM_DUT_OBJ:
            CSetup().buildFileList()
         else:
            self.dut.buildFileList()            
         
         back_suppress = testSwitch.FE_0127479_231166_SUPPRESS_INFO_ONLY_TSTS
         testSwitch.FE_0127479_231166_SUPPRESS_INFO_ONLY_TSTS = 0

         self.runsdi(sdi_cust_test = sdi_cust_test)
         try: 
            objPwrCtrl.powerCycle()
            oProc.dnldCode('CFW', fileName='cfw_plusoverlays_9.lod', timeout=500)  # SDM9 bridge code
         except: 
            objMsg.printMsg("dnldCode SDM9 Overlay Failed: %s" % traceback.format_exc())

         self.dut.IsSDI = False
                  
         from TestParamExtractor import TP
         if testSwitch.SPLIT_BASE_SERIAL_TEST_FOR_CM_LA_REDUCTION:
            from Serial_Download import CDnldCode
         else:
            from base_SerialTest import CDnldCode

         oDnldCode = CDnldCode(self.dut,{'CODES':getattr(TP, 'TCG_DNLD_SEQ', ['TGTB','OVLB','IV', 'TGT','OVL','CXM']),})
         oDnldCode.run()
      finally:
         self.dut.IsSDI = False

         testSwitch.FE_0127479_231166_SUPPRESS_INFO_ONLY_TSTS = back_suppress

         if backup:
            fwConfig[self.dut.partNum]['S_OVL'] = backup
            if not testSwitch.FE_0190240_007955_USE_FILE_LIST_FUNCTIONS_FROM_DUT_OBJ:
               CSetup().buildFileList()
            else:
               self.dut.buildFileList()

         objPwrCtrl.powerCycle()

   #---------------------------------------------------------------------------------------------------------#
   def runsdi(self, sdi_cust_test = None):

      objMsg.printMsg("start SDI")

      self.dnld_sdi()

      objPwrCtrl.powerCycle()

      if not testSwitch.virtualRun:
         self.handlder70()
         self.parmX()

         # Test 535 - Initial Tests - Output initiator download revision
         prm_535_InitiatorDownloadVersion = {
            "TstMode" : (0x0002,),
         }

         ret = st(535, prm_535_InitiatorDownloadVersion, timeout=120)
         objMsg.printMsg("SDI T535 ret=%s" % `ret`)


      if sdi_cust_test:
         sdi_cust_test(self.dut, self.params).run()

      '''
      # Test 506 - Set T510 Duration
      prm_506_SetRunTime_60S = {
         "TstTmSec" : (60,),
      }
      prm_506_SetRunTime_3600S = {
         "TstTmSec" : (3600,),
      }
      ret = st(506, prm_506_SetRunTime_60S, timeout=120)
      objMsg.printMsg("ret=%s" % `ret`)

      from IntfClass import CIdentifyDevice
      ret = CIdentifyDevice().ID
      objMsg.printMsg("ID start=%s" % ret)

      '''

      #prm_510_CCT = {'NumLbaPerTrnsfr': 128, 'StrtLba': 0, 'Ctrl2Wrd': 16384, 'WrRdMode': 2, 'StepSz': 128, 'PttrnMode': 128, 'CctBinSetg': 5642, 'timeout': 3600, 'MxLba': 3840, 'CctLbaSav': 10, 'DtaPttrn0': 0}
      #st(510, prm_510_CCT, timeout=1200)



      if 0:
         try:
            objMsg.printMsg("CBluenunScanAuto...")
            from CustomerScreens import CBluenunScanAuto
            CBluenunScanAuto(self.dut, self.params).run()
         except: 
            objMsg.printMsg("CBluenunScanAuto Failed: %s" % traceback.format_exc())

      if 0:
         try:
            objMsg.printMsg("CSonyScreenTest...")
            from CustomerScreens import CSonyScreenTest
            CSonyScreenTest(self.dut, self.params).run()
         except: 
            objMsg.printMsg("CSonyScreenTest Failed: %s" % traceback.format_exc())

      if 0:
         try:
            objMsg.printMsg("CAVScan...")
            from CustomerScreens import CAVScan
            CAVScan(self.dut, self.params).run()
         except: 
            objMsg.printMsg("CAVScan Failed: %s" % traceback.format_exc())


################################################################################
class CSonyScreenTest(CSDI):
   #----------------------------------------------------------------------------
   def run(self):
      objMsg.printMsg("SDI CSonyScreenTest start")
      from CustomerScreens import CSonyScreenTest
      CSDI(self.dut, self.params).run(sdi_cust_test = CSonyScreenTest)
      objMsg.printMsg("SDI CSonyScreenTest end")

################################################################################
class CAVScan(CSDI):
   #----------------------------------------------------------------------------
   def run(self):
      objMsg.printMsg("SDI CAVScan start")
      from CustomerScreens import CAVScan
      CSDI(self.dut, self.params).run(sdi_cust_test = CAVScan)
      objMsg.printMsg("SDI CAVScan end")

################################################################################
class CBluenunScanAuto(CSDI):
   #----------------------------------------------------------------------------
   def run(self):
      objMsg.printMsg("SDI CBluenunScanAuto start")
      from CustomerScreens import CBluenunScanAuto
      CSDI(self.dut, self.params).run(sdi_cust_test = CBluenunScanAuto)
      objMsg.printMsg("SDI CBluenunScanAuto end")



