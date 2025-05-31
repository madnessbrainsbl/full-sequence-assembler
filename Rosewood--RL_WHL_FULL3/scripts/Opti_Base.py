#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Base Particle Sweep Module
#
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Opti_Base.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Opti_Base.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
from State import CState
import Utility

#----------------------------------------------------------------------------------------------------------
class CDispOptiChan(CState):
   """
      Description: Class that reports channel opti parameters (Test 255)
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self,dut,depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from Process import CProcess
      oProcess = CProcess()

      prm = TP.reportChanOptiParms_255.copy()

      if 'HEAD' in self.params:
         prm['TEST_HEAD'] = self.params['HEAD']

      if 'ZONES' in self.params:
         zone_mask = 0
         for zone in self.params['ZONES']:
            zone_mask |= (1 << zone)
         prm['BIT_MASK'] = oProcess.oUtility.ReturnTestCylWord(zone_mask & 0xFFFFFFFF)
         prm['BIT_MASK_EXT'] = oProcess.oUtility.ReturnTestCylWord(zone_mask >> 32 & 0xFFFFFFFF)

      if testSwitch.FE_0161887_007867_VBAR_REDUCE_T255_LOG_DUMPS:  # Turn off the tables that are never looked at.
         if self.params.get('REDUCE_OUTPUT', 0):
            P255_PRECOMP_FLTR_VGA_LSI = 0x0001
            P255_FIR_LSI              = 0x0002
            P255_NPTARG_AND_MISC_LSI  = 0x0004
            P255_NPML_TAP0_TAP1_LSI   = 0x0008
            P255_NPML_TAP2_TAP3_LSI   = 0x0010
            P255_NPML_BIAS_LSI        = 0x0020
            P255_PREAMP_CHNL_HD_PARAM = 0x0040

            # Define a RESULTS_RETURNED parameter setting that has the set of desired tables, in case the parameter was not supplied.
            output_tbls = P255_PRECOMP_FLTR_VGA_LSI | P255_FIR_LSI | P255_NPTARG_AND_MISC_LSI | P255_PREAMP_CHNL_HD_PARAM
            # Now make sure the NPML and Bias tables are not requested.
            output_tbls = prm.get('RESULTS_RETURNED', output_tbls) & ~(P255_NPML_TAP0_TAP1_LSI | P255_NPML_TAP2_TAP3_LSI | P255_NPML_BIAS_LSI)
            prm.update({'RESULTS_RETURNED':output_tbls})

      spcId = self.params.get('SPC_ID', TP.reportChanOptiParms_255.get('spc_id', 1))
      oProcess.St(prm, spc_id = spcId)


#-------------------------------------------------------------------------------------------------------------
class CSimpleOpti(CState):
   """
         Description: Class that will perform basic read channel optimization. No zap is performed in this state- please call OPTI_ZAP prior to this state
         Base:
         Usage:
            Optionally add an input parameter of 'ZONES' to list specific zones to be optimized.
            Optionally add an input parameter of "ZONE_POS" to change the zone position used during the opti process
         Params:
      """
   #----------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}, useSYSZnParm=0):
      self.params = params
      self.useSYSZnParm = useSYSZnParm

      depList = []
      CState.__init__(self, dut, depList)
   
   #----------------------------------------------------------------------------------------------------------
   def runT250_channel(self, oRdWr):
      prm_PrePostOptiAudit_250_local = oRdWr.oUtility.copy(TP.prm_PrePostOptiAudit_250)
            
      #override the all heads with specific hd
      if (oRdWr.headRange):
         prm_PrePostOptiAudit_250_local['TEST_HEAD'] = \
            oRdWr.oUtility.converttoHeadRangeMask(oRdWr.headRange, oRdWr.headRange)
      MaskList = oRdWr.oUtility.convertListToZoneBankMasks(oRdWr.testZonesBER)
      for bank,list in MaskList.iteritems():
         if list:
            prm_PrePostOptiAudit_250_local ['ZONE_MASK_EXT'], prm_PrePostOptiAudit_250_local ['ZONE_MASK'] = \
               oRdWr.oUtility.convertListTo64BitMask(list)
            if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
               prm_PrePostOptiAudit_250_local ['ZONE_MASK_BANK'] = bank
            try: oRdWr.St(prm_PrePostOptiAudit_250_local) #11049 has internal retry
            except: pass
      
   #----------------------------------------------------------------------------------------------------------
   def run(self,zapOtfWP=0,zapOtfWP2=0,zapOtfZN=0,zapOtfHMS=0, T250Audit=1):
      if testSwitch.GA_0160140_350027_REPORT_CHANNEL_DIE_TEMP_THROUGHOUT_PROCESS:
         from Temperature import CTemperature
         stateTemp = CTemperature()

      from RdWr import CRdWrOpti
      oRdWr = CRdWrOpti(self.params)

      if testSwitch.GA_0113384_231166_DUMP_RAP_OPTI_DATA_PRE_AND_POST_OPTI:
         spcIdHlpr = Utility.CSpcIdHelper(self.dut)
         if not testSwitch.FE_0161887_007867_VBAR_REDUCE_T255_LOG_DUMPS:
            spcId = spcIdHlpr.getSetIncrSpcId('dispChan_255', startSpcId = 100, increment = 1, useOpOffset = 1)
            t255Params = self.params.copy()
            t255Params['SPC_ID'] = spcId
            CDispOptiChan(self.dut, params=t255Params).run()

      oRdWr.testZones = self.params.get('ZONES', range(self.dut.numZones))#All user zones
      oRdWr.testZonesBER = self.params.get('BER_ZONES', oRdWr.testZones)
      oRdWr.headRange = self.params.get('HEAD', None)

      if testSwitch.GA_0152127_357267_ERROR_RATE_AUDIT_PRE_AND_POST_OPTI:
         if T250Audit and (self.params.get('RunT250Pre_Channel', TP.RunT250Pre_Channel) or self.params.get('FORCE_RUN_PRE_T250', 0)):
            self.runT250_channel(oRdWr)

      if testSwitch.GA_0160140_350027_REPORT_CHANNEL_DIE_TEMP_THROUGHOUT_PROCESS:
         try:
            stateTemp.getChannelDieTemp()    # print channel die temperature
            stateTemp.getHDATemp()           # print HDA temperature
         except: pass

      if self.dut.nextState in ['BPINOMINAL', 'PRE_OPTI', 'PRE_OPTI2']: 
          optiPrm = self.params.get('param', 'simple_OptiPrm_251_short_tune')
      else:
          optiPrm = self.params.get('param', 'simple_OptiPrm_251')

      #if testSwitch.TTR_REDUCED_PARAMS_T251:
         #optiPrm = self.params.get('param', 'base_BpiOptiPrm_251')   # reduced regs for bpi/vbar

      if testSwitch.FE_0155925_007955_P_T251_SEPERATE_SYS_AREA_PARAMS:
         if self.useSYSZnParm:
            optiPrm = 'base_phastOptiPrm_SysZn_251'

      if zapOtfWP == 1 or zapOtfZN == 1 or zapOtfHMS == 1:
         t251_prm = getattr(TP, optiPrm).copy()
         if self.params.get('COPY_2_ADJACENT', 0):
            t251_prm['CWORD1'] |= 0x1000
         oRdWr.phastOpti(self.zap_251_params(t251_prm, zapOtfWP = zapOtfWP, zapOtfWP2 =  zapOtfWP2), maxRetries = 3)
      else:
         if testSwitch.FE_TRIPLET_WPC_TUNING and not testSwitch.KARNAK:
            tableData = []
            try:
               if testSwitch.FE_0251897_505235_STORE_WPC_RANGE_IN_SIM:
                  from RdWr import CWpcRangeFile
                  tableData = CWpcRangeFile().Retrieve_WpcRange()
               else:
                  tableData = self.dut.dblData.Tables('P_TRIPLET_WPC').tableDataObj()
            except: pass
            if len(tableData) == 0:
               oRdWr.phastOpti(getattr(TP, optiPrm).copy(), maxRetries = 3)
            else:
               orig_testZones = list(oRdWr.testZones)

               # Get WPC Reference Table
               if testSwitch.FE_0251897_505235_STORE_WPC_RANGE_IN_SIM:
                  WPC_table = tableData
                  hd_list = set([hd for hd, zn in tableData.keys()])
               else:
                  WPC_table = {}
                  hd_list = []
                  for index in range(len(tableData)):
                     hd = int(tableData[index]['HD_PHYS_PSN'])
                     if not hd in hd_list:
                        hd_list.append(hd)
                     zn = int(tableData[index]['DATA_ZONE'])
                     WPC_table[hd,zn] = int(tableData[index]['WPC'])

               objMsg.printMsg('WPC_table: %s' % (WPC_table))

               if type(oRdWr.headRange) != types.NoneType:
                  hd_list = range(oRdWr.headRange)
               # Tune per same WPC
               for hd in hd_list:
                  oRdWr.testZones=[]
                  testZones = list(orig_testZones)
                  while len(testZones) > 0:
                     wpc = WPC_table[hd,testZones[0]]
                     oRdWr.testZones = []
                     pendingzone = []
                     for zn_idx in range(len(testZones)):
                        if wpc == WPC_table[hd,testZones[0]]:
                           oRdWr.testZones.append(testZones.pop(0))
                        else:
                           pendingzone.append(testZones.pop(0))
                     testZones = list(pendingzone)
                     objMsg.printMsg('testZones: %s' % (oRdWr.testZones))
                     objMsg.printMsg('pendingzone: %s' % (pendingzone))

                     Wpc_Start = 0
                     if wpc < 5: Wpc_Start = wpc
                     testParam = getattr(TP, optiPrm).copy()
                     if self.params.get('COPY_2_ADJACENT', 0):
                        testParam['CWORD1'] |= 0x1000
                     testParam.update({'REG_TO_OPT4': (0x155, wpc, Wpc_Start, -1), 'TEST_HEAD': hd})
                     oRdWr.phastOpti(testParam.copy(), maxRetries = 3)
                     testZones = list(pendingzone)

               oRdWr.testZones = list(orig_testZones)
         else:
            t251_prm = getattr(TP, optiPrm).copy()
            if self.params.get('COPY_2_ADJACENT', 0):
               t251_prm['CWORD1'] |= 0x1000
            oRdWr.phastOpti(t251_prm, maxRetries = 3)


      if testSwitch.FE_0136807_426568_P_BANSHEE_VSCALE_OPTI:
         if zapOtfWP == 1 or zapOtfZN == 1 or zapOtfHMS == 1:
            oRdWr.phastOpti(self.zap_251_params(TP.VSCALE_OptiPrm_251.copy(),zapOtfWP = zapOtfWP, zapOtfWP2 =  zapOtfWP2), maxRetries = 3)
         else:
            oRdWr.phastOpti(TP.VSCALE_OptiPrm_251.copy(), maxRetries = 3)

      if not testSwitch.KARNAK:
          try:
             oRdWr.St(TP.nld_151)
          except ScriptTestFailure, (failureData):
             if failureData[0][2] in [10007] and testSwitch.ENABLE_BYPASS_T151_EC10007: pass
             else: raise

      if testSwitch.GA_0160140_350027_REPORT_CHANNEL_DIE_TEMP_THROUGHOUT_PROCESS:
         try:
            stateTemp.getChannelDieTemp()    # print channel die temperature
            stateTemp.getHDATemp()           # print HDA temperature
         except:
            pass

      if testSwitch.GA_0113384_231166_DUMP_RAP_OPTI_DATA_PRE_AND_POST_OPTI:
         spcId = spcIdHlpr.getSetIncrSpcId('dispChan_255', startSpcId = 100, increment = 1, useOpOffset = 1)
         t255Params = self.params.copy()
         t255Params['SPC_ID'] = spcId
         if testSwitch.FE_0161887_007867_VBAR_REDUCE_T255_LOG_DUMPS:  # Turn off the tables that are never looked at.
            t255Params['REDUCE_OUTPUT'] = 1
         CDispOptiChan(self.dut, params=t255Params).run()

      if testSwitch.GA_0152127_357267_ERROR_RATE_AUDIT_PRE_AND_POST_OPTI:
         if T250Audit and self.params.get('RunT250Post_Channel', 1): #always run
            self.runT250_channel(oRdWr)

      oRdWr.oFSO.saveRAPSAPtoFLASH()
      oRdWr.testZones = None


      #Disable ZAP in flash so no remenant zap is read in subsequent operations
      if self.params.get('DISABLE_ZAP',True):
         oRdWr.St(TP.zapPrm_175_zapOff)

   #----------------------------------------------------------------------------------------------------------
   def zap_251_params(self, testParam, zapOtfWP, zapOtfWP2):
      korZAP_OTF = testParam
      korZAP_OTF.update(TP.prm_ZAP_OTF)
      korZAP_OTF['CWORD1'] |= 0x80
      korZAP_OTF['TRACK_LIMIT'] = 0
      korZAP_OTF['timeout'] = 10000 * self.dut.imaxHead
      if zapOtfWP == 1 and not zapOtfWP2:
         korZAP_OTF['GEN_PC_FILES'] = 1
      return korZAP_OTF

