#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Base Particle Sweep Module
#
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/12/15 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Opti_Read.py $
# $Revision: #5 $
# $DateTime: 2016/12/15 23:34:49 $
# $Author: weichen.lau $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Opti_Read.py#5 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
from State import CState
import MessageHandler as objMsg
from PowerControl import objPwrCtrl
import ScrCmds
import types
import struct
import Utility
printDbgMsg = Utility.getChannelPrintDbgMsgFunction()
verbose = 0 # Set to a value greater than 0 for output in the log

#----------------------------------------------------------------------------------------------------------
class CRdOpti(CState):
   """
      Description: Class that will perform basic read channel optimization
      Base: Based on AGERE Venus calibration flows.
      Usage: Optionally add an input parameter of 'ZONES' to list specific zones to be optimized.
      Params:
         SQZ_METHOD= ['MAX', 'MEAN'] for iterative opti
         zapFromDut= use zap information on dut/cm to make zapping tracks faster.

   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}, useSYSZnParm=0,zapOtfWP=0,zapOtfWP2=0,zapOtfZN=0,zapOtfHMS=0):
      self.params = params
      self.useSYSZnParm = useSYSZnParm
      self.zapOtfWP = zapOtfWP
      self.zapOtfWP2 = zapOtfWP2
      self.zapOtfZN = zapOtfZN
      self.zapOtfHMS = zapOtfHMS
      depList = []
      CState.__init__(self, dut, depList)
      from Process import CProcess
      self.oProc = CProcess()

   #-------------------------------------------------------------------------------------------------------
   def optiZAP(self, testZones, testHeads = None, trackLimit = None, zonePos = None, consolidateOffLVFF_ACFF = 0):
      """ PRE opti zap section
       @param testZones: Zone selection input to opti.. used to determine if system opti or normal
       @param testHeads: List of heads to be zapped. Default is None which is set to all heads
      """
      from Servo import CServoOpti
      oSrvOpti = CServoOpti()
      zapFromDut = self.params.get('zapFromDut',1)

      if testZones == [self.dut.systemZoneNum,]:
         ######################################
         #  ZAP system Area
         ######################################
         if testSwitch.ZFS:
            zapSys = oSrvOpti.oUtility.copy(TP.zfs_275)
            zapSys['ZAP_SPAN'] = 4                            # 4 = System area zap
            zapSys['REVS'] = 4
            zapSys['ITERATIONS'] = 2
            zapSys['prm_name'] = "System Area ZAP_275"
         else:
            zapSys = oSrvOpti.oUtility.copy(TP.zapbasic_175)
            cword2 = zapSys.get('CWORD2',0)
            if type(cword2) in [types.ListType,types.TupleType]:
               cword2 = cword2[0]
            if testSwitch.ROSEWOOD7:
               cword2 |= (0x8008)
            else:
               cword2 |= (0x8010)   # Only zap system area and save off gap data

            zapSys['prm_name'] = "System Area ZAP_175"
            zapSys['CWORD2'] = cword2
            if 'CWORD3' in zapSys: del zapSys['CWORD3'] 
         oSrvOpti.zap(zapSys, zapFromDut = zapFromDut)
         ######################################
      else:  # opti zap
         if testHeads == None:
            testHeads = range(self.dut.imaxHead)

         #for head in testHeads:
         hdMsk = (min(testHeads) << 8) + max(testHeads)

         if testSwitch.ZFS:
            zapSys = oSrvOpti.oUtility.copy(TP.zfs_275)
            zapSys['ZAP_SPAN'] = 2   # 2 = ZAP the R/W opti cylinders
            zapSys['REVS'] = 2   # changed from 4
            zapSys['ITERATIONS'] = 1   # changed from 2
            if trackLimit != None:
               zapSys['RETRY_INCR'] = trackLimit & 0x00FF    # low byte pad towards MD
               zapSys['RETRIES'] = trackLimit >> 8    # high byte away from MD to ensure coverage.
            zapSys['prm_name'] = "RW Tracks ZAP_275"
         else:
            zapSys = oSrvOpti.oUtility.copy(TP.zapbasic_175)
            cword2 = zapSys.get('CWORD2',0)
            if type(cword2) in [types.ListType,types.TupleType]:
               cword2 = cword2[0]
            if testSwitch.ROSEWOOD7:
               cword2 |= (0x400C)
            else:
               cword2 |= (0x4014)

            if testSwitch.FE_SGP_81592_DISPLAY_ZAP_AUDIT_STATS_IN_OPTIZAP:
               cword2 |= (0x0300) # enable post zap audit
               zapSys['RZ_VERIFY_AUDIT_INTERVAL'] = 100
               zapSys['WZ_VERIFY_AUDIT_INTERVAL'] = 100
               zapSys['RZ_RRO_AUDIT_INTERVAL']    = 10
               zapSys['WZ_RRO_AUDIT_INTERVAL']    = 10
            zapSys['prm_name'] = "RW Tracks MINIZAP_175"
            zapSys['CWORD2'] = cword2

         if not (testSwitch.FE_0125510_209214_ZAP_PARAMETER_CLEANUP_1 and 0): #force it to run no matter VBAR rev from SF3
            if trackLimit != None:
               zapSys['TRACK_LIMIT'] = trackLimit #use low word: lower byte =  num trks toward MD(most common),upper byte = num trks away from MD

         zapSys['HEAD_RANGE'] = (hdMsk,)
         if zonePos == None:
            zapSys["ZONE_POSITION"] = self.params.get("ZONE_POS",TP.ZONE_POS)
         else:
            zapSys["ZONE_POSITION"] = zonePos

         #175: RW Tracks MINIZAP_175 in OPTIZAP_1
         #if not testSwitch.ZFS:
         MaskList = oSrvOpti.oUtility.convertListToZoneBankMasks(testZones)
         for bank, list in MaskList.iteritems():
            if list:
               zapSys['ZONE_MASK_EXT'], zapSys['ZONE_MASK'] = oSrvOpti.oUtility.convertListTo64BitMask(list)
               if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
                  zapSys['ZONE_MASK_BANK'] = bank
               if testSwitch.IS_FAFH:
                  objMsg.printMsg("Allow FAFH access !!!!!!")
                  oSrvOpti.St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value
                  oSrvOpti.St(TP.AllowFAFH_AccessBit_178) # Allow FAFH access for servo test
                  oSrvOpti.St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value
               oSrvOpti.zap(zapSys, zapFromDut = zapFromDut, consolidateOffLVFF_ACFF = consolidateOffLVFF_ACFF) 
         #else: oSrvOpti.zap(zapSys, zapFromDut = zapFromDut) 
         if testSwitch.IS_FAFH:
            objMsg.printMsg("Disable FAFH Track access !!!!!!")
            oSrvOpti.St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value
            oSrvOpti.St(TP.DisallowFAFH_AccessBit_178) # Dis-allow FAFH access after completing servo test
            oSrvOpti.St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value
   
   #-------------------------------------------------------------------------------------------------------
   def T251_zone_copy_support(self,T251_Para,oRdWr):

      try: 
          opti_Zn_index= TP.opti_Zn_index
          nonUMP_zoneGroup_size = TP.nonUMP_zoneGroup_size                       
          ump_zoneGroup_size = TP.ump_zoneGroup_size
      except: 
          opti_Zn_index= [0,0,0,0,0,2,0,0,0,0]
          nonUMP_zoneGroup_size = 5                       
          ump_zoneGroup_size = 1

      zn_group_by_len_all_hd = {}
      zn_group_by_copy_option_all_hd = {}
      single_zone= {} 

      for groupSize in range(nonUMP_zoneGroup_size+1): # for predefined zone, it is all head
         zn_group_by_len_all_hd[groupSize] = [] #{0: [], 1: [], 2: [], 3: [], 4: [], 5: []}

      for hd in range(self.dut.imaxHead):
          single_zone [hd] =[] 

      try: 
          optiZones_tbl=  self.dut.dblData.Tables('OPTI_ZN_SUMMARY').tableDataObj()
          printDbgMsg("optiZones_tbl %s" % len(optiZones_tbl))  
      except:
          CRdOptiZoneInsertion(self.dut,{}).run()
          optiZones_tbl=  self.dut.dblData.Tables('OPTI_ZN_SUMMARY').tableDataObj()
          printDbgMsg("optiZones_tbl2 %s" % len(optiZones_tbl))


      for tableofs in range(len(optiZones_tbl)):

          Head = int(optiZones_tbl[ tableofs ] ['HD_PHYS_PSN'])
          Opti_Zn = int(optiZones_tbl[ tableofs ] ['OPTI_ZONE'])
          ZG_Start = int(optiZones_tbl[ tableofs ] ['ZN_GRP_START'])
          ZG_End = int(optiZones_tbl[ tableofs ] ['ZN_GRP_END'])
          Copy_Option= int(optiZones_tbl[ tableofs ] ['ZN_COPY_OPTION'])
          printDbgMsg("H[%d] Opti_Zn[%d] Start_Zn[%d] End_Zn[%d] Copy_Option[0x%x]" % (Head, Opti_Zn, ZG_Start, ZG_End,Copy_Option))

          #objMsg.printMsg("H[%d] Opti_Zn[%d] Start_Zn[%d] End_Zn[%d] " % (Head, Opti_Zn, ZG_Start, ZG_End))
          groupSize = ZG_End-ZG_Start+1
          if groupSize != 1:
              if zn_group_by_copy_option_all_hd.has_key(Copy_Option):
                  zn_group_by_copy_option_all_hd[Copy_Option].append(Opti_Zn)
              else:
                  zn_group_by_copy_option_all_hd[Copy_Option]= [Opti_Zn]
          else:
              if Head == 0xFF:
                  for hd in range(self.dut.imaxHead) :
                      single_zone[hd].append(Opti_Zn)
              else:
                  single_zone[Head].append(Opti_Zn)
      objMsg.printMsg("zn_group_by_copy_option_all_hd %s" % zn_group_by_copy_option_all_hd)
      objMsg.printMsg("single zn tuning %s" % single_zone)
      if oRdWr.headRange == None:
         oRdWr.headRange = 0xFF
         headlist = range(self.dut.imaxHead)
      else: 
         if not type(oRdWr.headRange) is list:
            headlist = [oRdWr.headRange]
      objMsg.printMsg("headlist %s" % headlist)
      for copy_option in zn_group_by_copy_option_all_hd: # this is for all heads
          if len(zn_group_by_copy_option_all_hd[copy_option])>0:
              oRdWr.testZones = zn_group_by_copy_option_all_hd[copy_option]
              #oRdWr.headRange = 0xFF # all heads
              zoneCopySetting = copy_option
              printDbgMsg("copy_option in HEX %x" % copy_option)
              T251_Para['ZONECOPYOPTIONS'] = zoneCopySetting
              T251_Para['CWORD1'] = T251_Para['CWORD1'] | 0x1000 # to enable zone copy
              oRdWr.phastOpti(T251_Para, maxRetries = 3, zapFunc = None, zapECList = self.zapECList) # 

      for hd in headlist: # this is single zone tuning, by head by zone, overwrite previous setting if it is copied
          if len(single_zone[hd])>0:
              oRdWr.testZones = single_zone[hd]
              oRdWr.headRange = hd
              T251_Para['ZONECOPYOPTIONS'] = 0                   # no zone copy
              T251_Para['CWORD1'] = T251_Para['CWORD1'] & 0xEFFF # to disable zone copy
              oRdWr.phastOpti(T251_Para, maxRetries = 3, zapFunc = None, zapECList = self.zapECList) # 

   #-------------------------------------------------------------------------------------------------------
   def runT250_channel(self, oRdWr, spc_id_on_track = 4, spc_id_sqz_wrt=24):
      ec_st = [] #empty ec ar

      if self.params.get('ON_TRACK_250', 1): 
         prm_ber = oRdWr.oUtility.copy(TP.prm_PrePostOptiAudit_250_2)
         if self.params.get('MAX_ERR_RATE', 0):
            prm_ber.update({'MAX_ERR_RATE': self.params.get('MAX_ERR_RATE', 0)}) 
         if not testSwitch.FAST_2D_VBAR_TESTTRACK_CONTROL:
            prm_ber.update({'CWORD2': prm_ber['CWORD2'] | 0x1000}) # Banded zone pos
         if self.params.get('RST_OFFSET', 0): #reset read offset
            prm_ber.update({'CWORD2': prm_ber['CWORD2'] | 0x0800 }) 

         prm_ber['spc_id'] = spc_id_on_track
         
         MaskList = oRdWr.oUtility.convertListToZoneBankMasks(oRdWr.onTrackTestZonesBER)
         for bank, list in MaskList.iteritems():
            if list:
               prm_ber['ZONE_MASK_EXT'], prm_ber['ZONE_MASK'] = \
                  oRdWr.oUtility.convertListTo64BitMask(list)
               if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
                  prm_ber['ZONE_MASK_BANK'] = bank
               try: self.oProc.St(prm_ber)
               except  ScriptTestFailure, (failureData): 
                  if failureData[0][2] not in ec_st: ec_st.append(failureData[0][2])
                  pass

      if self.params.get('BAND_WRITE_250', 0) and testSwitch.FAST_2D_MEASURE_SQZ_BER:
         prm_sqz_write = oRdWr.oUtility.copy(TP.prm_PrePostOptiAuditSQZWRT_250_2)
         if self.params.get('MAX_ERR_RATE', 0):
            prm_sqz_write.update({'MAX_ERR_RATE': self.params.get('MAX_ERR_RATE', 0)})
         prm_sqz_write['spc_id'] = spc_id_sqz_wrt
         if self.params.get('FIND_DEFECT_FREE_BAND', 0):
            prm_sqz_write['CWORD1'] = prm_sqz_write['CWORD1'] | 0x40  
         if self.params.get('FAIL_SAFE', 0): #fail safe
            prm_sqz_write['MINIMUM'] = 0
         MaskList = oRdWr.oUtility.convertListToZoneBankMasks(oRdWr.sqzWrtTestZonesBER)
         for bank,list in MaskList.iteritems():
            if list:
               prm_sqz_write['ZONE_MASK_EXT'], prm_sqz_write['ZONE_MASK'] = \
                  oRdWr.oUtility.convertListTo64BitMask(list)
               if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
                  prm_sqz_write['ZONE_MASK_BANK'] = bank
               try: self.oProc.St(prm_sqz_write)
               except  ScriptTestFailure, (failureData): 
                  if failureData[0][2] not in ec_st: ec_st.append(failureData[0][2])
                  pass

      return ec_st #return ec to calling code section to handle ec

   #-------------------------------------------------------------------------------------------------------
   def basicAGEREOpti(self, oRdWr, zappedOptiTracks, targetOpti = False, zapOTF = 0, zapOtfWP = 0, zapOtfWP2 = 0):
      # Perform phast opti
      if zappedOptiTracks:
         zapFunc = None
      else:
         zapFunc = self.optiZAP

      #data collection for write to write variation, using offtrack AC erase , optimize offtrack percentage
      #it will take 3 min , try to correct with drive data
      if testSwitch.extern.SFT_TEST_0396 and testSwitch.ENABLE_T396_DATACOLLECTION and (self.dut.nextState == 'READ_OPTI'):
         t396 = {
                'timeout'            : 500000,
                'ZONE_MASK'          : (0x8000, 0x0001),  #OD/MD/ID
                'ZONE_MASK_EXT'      : (0x800, 0x0),
                'STEP_INC'           : 25,               #25 tics 
                'ITERATIONS'         : 20,               #20 iteration to run variation
                'REVS'               : 5    }            #5 revs when collect BIE
         try:
            st(396,t396)
         except:
            pass

      if self.useSYSZnParm:
         if zapOTF == 0:
            oRdWr.phastOpti(TP.base_phastOptiPrm_SysZn_251.copy(),maxRetries = 3, zapFunc = zapFunc, zapECList = self.zapECList) # laulc
         else:
            oRdWr.phastOpti(self.zap_251_params(TP.base_phastOptiPrm_SysZn_251.copy(), zapOtfWP, zapOtfWP2),maxRetries = 3, zapFunc = zapFunc, zapECList = self.zapECList) # laulc

         if not testSwitch.KARNAK:
             oRdWr.St(TP.nld_151)
      elif testSwitch.targetOptiIn251 and targetOpti:
         if zapOTF == 0:
            prm = TP.phastOpti_NPT_Prm_251.copy()
         else:
            prm = self.zap_251_params(TP.phastOpti_NPT_Prm_251.copy(), zapOtfWP, zapOtfWP2)
         prm['dlfile'] = (CN, 'parsedNPT.bin')
         oRdWr.phastOpti(prm, maxRetries = 3, zapFunc = zapFunc, zapECList = self.zapECList) # laulc
      else:
         if zapOTF == 0:
            if testSwitch.FE_SGP_81592_COLLECT_BER_B4_N_AFTER_RD_OPTI:
               #either use state table or testparameter RunT250Pre_Channel
               if self.params.get('RunT250Pre_Channel', TP.RunT250Pre_Channel): 
                  self.runT250_channel(oRdWr, spc_id_on_track = 4) #fail safe

            if (testSwitch.FE_0243151_403980_AVERAGE_RAP_REG_VALUES and self.dut.nextState == 'READ_OPTI'):
               regIDtoAvg = [0x11]# asymm
               self.AveragingRAPRegValues(oRdWr, regIDtoAvg)

            if self.dut.nextState in ['READ_OPTI']:
               if (testSwitch.FE_0253168_403980_RD_OPTI_ODD_ZONE_COPY_TO_EVEN and self.dut.nextState == 'READ_OPTI'):    # only test odd zones
                  orgtestZones = oRdWr.testZones
                  oRdWr.testZones = range(1, self.dut.numZones, 2)
                  if not(self.dut.numZones % 2):
                     if not (self.dut.numZones - 1) in oRdWr.testZones:
                        oRdWr.testZones.append(self.dut.numZones - 1)   # must tune last zone if it's odd zone
                  objMsg.printMsg("oRdWr.testZones = %s" % oRdWr.testZones)
                  if testSwitch.SMR:
                     objMsg.printMsg("self.dut.numZones = %s" % self.dut.numZones)
                     objMsg.printMsg("UMP ZONES = %s" % TP.UMP_ZONE)
                     for zn in TP.UMP_ZONE:
                        if (zn < self.dut.numZones):
                           if (zn % 2):  #odd zone
                              if not (zn - 1) in TP.UMP_ZONE:
                                 if not (zn - 1) in oRdWr.testZones:
                                    oRdWr.testZones.append(zn-1)
                           else: #even zone
                              if not (zn + 1) in TP.UMP_ZONE:
                                 if not (zn) in oRdWr.testZones:
                                    oRdWr.testZones.append(zn)
                  objMsg.printMsg("oRdWr.testZones = %s" % oRdWr.testZones)

               if (testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT and  (self.dut.nextState == 'READ_OPTI' or self.dut.nextState == 'READ_OPTI1') and testSwitch.FE_0271421_403980_P_ZONE_COPY_OPTIONS):
                   orgheadRange = oRdWr.headRange
                   orgtestZones = oRdWr.testZones
                   T251_param = TP.base_phastOptiPrm_251.copy()
                   if testSwitch.extern.FE_0308987_403980_PRECODER_PF3_INPUT:
                      # Temporary update T251 new parameters here.
                      # Extern test switch cannot be added in Test_Switches.py, it can only be added to Feature_Release_Test_Switches.py.
                      # Extern test switch from Feature_Release_Test_Switches.py cannot be added in TestParameters.py.
                      # Thus the only way to use extern.FE_0308987_403980_PRECODER_PF3_INPUT is here. 
                      # This is only a temporary solution to prevent pf3 & sf3 mismatched failure. 
                      # When most pco picks up the latest SF3, this switch can be removed.
                      # These T251 new parameters will be defined in TestParameters.py.
                      T251_param.update({'PRECODER0': (0x0713, 0x4652), 'PRECODER1': (0x0713, 0x4625), 'PRECODER2': (0x0145, 0x7362), 'PRECODER3': (0x0142, 0x7365), 'PRECODER4': (0x7654, 0x3210)}) 
                   self.T251_zone_copy_support(T251_param,oRdWr)
                   oRdWr.headRange = orgheadRange
                   oRdWr.testZones = orgtestZones

               if testSwitch.RD_OPTI_SEPARATE_PARM_FOR_320G and self.dut.CAPACITY_PN in ['320G']:
                  oRdWr.testZones = [0]
                  oRdWr.phastOpti(TP.base_readOpti_Prm_251_zn0.copy(),maxRetries = 3, zapFunc = zapFunc, zapECList = self.zapECList) # laulc
                  oRdWr.testZones = range(1, self.dut.numZones)
                     
               if testSwitch.WA_0256539_480505_SKDC_M10P_BRING_UP_DEBUG_OPTION and self.dut.nextState == 'READ_OPTI':
                  if testSwitch.GA_0113384_231166_DUMP_RAP_OPTI_DATA_PRE_AND_POST_OPTI:
                     spcIdHlpr = Utility.CSpcIdHelper(self.dut)
                     spcId = spcIdHlpr.getSetIncrSpcId('dispChan_255', startSpcId = 100, increment = 1, useOpOffset = 1)
                     t255Params = {}
                     t255Params['SPC_ID'] = spcId
                     t255Params['ZONES'] = range(self.dut.numZones)
                     if testSwitch.FE_0161887_007867_VBAR_REDUCE_T255_LOG_DUMPS:  # Turn off the tables that are never looked at.
                        t255Params['REDUCE_OUTPUT'] = 1
                     from Opti_Base import CDispOptiChan
                     CDispOptiChan(self.dut, params=t255Params).run()
               if (testSwitch.FE_0253168_403980_RD_OPTI_ODD_ZONE_COPY_TO_EVEN and self.dut.nextState == 'READ_OPTI'):    # only test odd zones
                  oRdWr.testZones = orgtestZones
            elif self.dut.nextState == 'VAR_SPARES':
               savedtestZones = oRdWr.testZones
               savedheadRange = oRdWr.headRange
               base_phastOptiPrm_251_local = oRdWr.oUtility.copy(TP.base_phastOptiPrm_251)
               base_phastOptiPrm_251_local.update({'timeout':9000})
               if testSwitch.FAST_2D_VBAR_TESTTRACK_CONTROL:
                  base_phastOptiPrm_251_local.update({'CWORD1': base_phastOptiPrm_251_local['CWORD1'] | 0x8000})
               if testSwitch.extern.FE_0308987_403980_PRECODER_PF3_INPUT:
                  # Temporary update T251 new parameters here.
                  # Extern test switch cannot be added in Test_Switches.py, it can only be added to Feature_Release_Test_Switches.py.
                  # Extern test switch from Feature_Release_Test_Switches.py cannot be added in TestParameters.py.
                  # Thus the only way to use extern.FE_0308987_403980_PRECODER_PF3_INPUT is here. 
                  # This is only a temporary solution to prevent pf3 & sf3 mismatched failure. 
                  # When most pco picks up the latest SF3, this switch can be removed.
                  # These T251 new parameters will be defined in TestParameters.py.
                  base_phastOptiPrm_251_local.update({'PRECODER0': (0x0713, 0x4652), 'PRECODER1': (0x0713, 0x4625), 'PRECODER2': (0x0145, 0x7362), 'PRECODER3': (0x0142, 0x7365), 'PRECODER4': (0x7654, 0x3210)}) 
               prm_ber250 = oRdWr.oUtility.copy(TP.prm_PrePostOptiAudit_250_2)
               prm_ber250.update({'spc_id':23001})
               prm_ber250.update({'MINIMUM': 0})
               prm_ber250.update({'NUM_SQZ_WRITES': TP.prm_230_VarSpares['NUM_SQZ_WRITES']})
               prm_ber250.update({'CWORD1': TP.prm_230_VarSpares['CWORD3']})
               prm_ber250.update({'MAX_ERR_RATE': TP.prm_230_VarSpares['MAX_ERR_RATE']})
               if not testSwitch.FAST_2D_VBAR_TESTTRACK_CONTROL:
                  prm_ber250.update({'CWORD2': prm_ber250['CWORD2'] | 0x1000}) # Banded zone pos
               ZnChanged = {}
               try:
                  ZnChanged = self.dut.dblData.Tables('P210_VBAR_FORMATS').tableDataObj()
               except:
                  objMsg.printMsg('Cannot Access P210_VBAR_FORMATS table')
                  pass

               VS_testZone = {}
               for i in range(self.dut.imaxHead):
                  VS_testZone[i] = []
               for hd in range(self.dut.imaxHead):
                  for rec in ZnChanged:
                     head = int(rec['HD_LGC_PSN'])
                     zone = int(rec['DATA_ZONE'])
                     if head == hd:
                        VS_testZone[hd].append(zone)   


               if (len(ZnChanged)>0 and (not testSwitch.FE_0349420_356688_P_ENABLE_OPTI) ): 
                  for hd in range(self.dut.imaxHead):
                     if (len(VS_testZone[hd]) > len(TP.BPIMeasureZone)) and testSwitch.FE_0271421_403980_P_ZONE_COPY_OPTIONS:
                        # if any one head has more than zone neutral number of zones being adjusted, run KFCI check and T251 zone copy.
                        oRdWr.headRange = hd
                        CRdOptiZoneInsertion(self.dut,{}).run(hd)
                        self.T251_zone_copy_support(base_phastOptiPrm_251_local,oRdWr)
                        oRdWr.headRange = savedheadRange
                        oRdWr.testZones = savedtestZones
                     elif VS_testZone[hd]:
                        oRdWr.testZones = VS_testZone[hd]
                        oRdWr.headRange = None
                        base_phastOptiPrm_251_local.update({'TEST_HEAD': hd})
                        oRdWr.phastOpti(base_phastOptiPrm_251_local, maxRetries = 3, zapFunc = None, zapECList = self.zapECList)
                        
                     if VS_testZone[hd]:
                        prm_ber250.update({'TEST_HEAD': hd<<8 | hd})
                        
                        MaskList = oRdWr.oUtility.convertListToZoneBankMasks(oRdWr.testZones)
                        objMsg.printMsg("MaskList = %s" % MaskList)
                        for bank,list in MaskList.iteritems():
                           if list:
                              objMsg.printMsg("list = %s" % list)
                              prm_ber250['ZONE_MASK_EXT'], prm_ber250['ZONE_MASK'] = oRdWr.oUtility.convertListTo64BitMask(list)
                              if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
                                 prm_ber250['ZONE_MASK_BANK'] = bank
                              objMsg.printMsg("prm_ber250 = %s" % prm_ber250)
                              try: self.oProc.St(prm_ber250)
                              except: pass
               else:
                  if testSwitch.FE_0271421_403980_P_ZONE_COPY_OPTIONS:
                     CRdOptiZoneInsertion(self.dut,{}).run()
                     self.T251_zone_copy_support(base_phastOptiPrm_251_local,oRdWr)
                     oRdWr.headRange = savedheadRange
                     oRdWr.testZones = savedtestZones
                  else:
                     base_phastOptiPrm_251_local.update({'timeout':9000 * self.dut.imaxHead})
                     oRdWr.phastOpti(base_phastOptiPrm_251_local, maxRetries = 3, zapFunc = None, zapECList = self.zapECList)
                  MaskList = oRdWr.oUtility.convertListToZoneBankMasks(oRdWr.testZones)
                  objMsg.printMsg("MaskList = %s" % MaskList)
                  for bank,list in MaskList.iteritems():
                     if list:
                        objMsg.printMsg("list = %s" % list)
                        prm_ber250['ZONE_MASK_EXT'], prm_ber250['ZONE_MASK'] = oRdWr.oUtility.convertListTo64BitMask(list)
                        if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
                           prm_ber250['ZONE_MASK_BANK'] = bank
                        objMsg.printMsg("prm_ber250 = %s" % prm_ber250)
                        try: self.oProc.St(prm_ber250)
                        except: pass
               oRdWr.testZones = savedtestZones
               oRdWr.headRange = savedheadRange
            elif testSwitch.TTR_REDUCED_PARAMS_T251:
               if (testSwitch.TTR_BPINOMINAL_V2 and self.dut.nextState in ['PRE_OPTI', 'PRE_OPTI2']):    # v2: normal full params in Pre-Opti, partial in vbar
                  oRdWr.phastOpti(TP.base_FirstOptiPrm_251.copy(),maxRetries = 3, zapFunc = zapFunc, zapECList = self.zapECList) # PreOpti
               else:
                  oRdWr.phastOpti(TP.base_ReducedPrm_251.copy(),maxRetries = 3, zapFunc = zapFunc, zapECList = self.zapECList) # WTF
            else:
               if testSwitch.FE_TRIPLET_WPC_TUNING and not testSwitch.KARNAK:
                  self.WPC_TunePerHdZn( oRdWr, T251_param = TP.base_phastOptiPrm_251.copy(), zapFunc = zapFunc)
               else:
                  optiparamStr = self.params.get('param', 'base_phastOptiPrm_251')
                  t251_prm = oRdWr.oUtility.copy(getattr(TP, optiparamStr))
                  oRdWr.phastOpti(t251_prm, maxRetries = 3, \
                     zapFunc = zapFunc, zapECList = self.zapECList) 

            if not testSwitch.KARNAK:
               try:
                  oRdWr.St(TP.nld_151)
               except ScriptTestFailure, (failureData):
                  if failureData[0][2] in [10007] and testSwitch.ENABLE_BYPASS_T151_EC10007: pass
                  else: raise

            if testSwitch.FE_SGP_81592_COLLECT_BER_B4_N_AFTER_RD_OPTI:
               if self.params.get('RunT250Post_Channel', TP.RunT250Post_Channel): #always run
                  ec_st = self.runT250_channel(oRdWr, spc_id_on_track = 5)
                  for ec in ec_st:
                     # handling of ec 10632 path
                     if ec == 10632: 
                        if self.dut.CAPACITY_PN not in TP.Native_Capacity:
                           pass
                        '''
                        elif self.dut.nextState in ['READ_OPTI']:
                           from VBAR import CUtilityWrapper
                           if CUtilityWrapper(self.dut,{}).SearchLowerCapacityPn() != 0:
                              self.dut.Waterfall_Req = "REZONE"
                              self.dut.driveattr["DNGRADE_ON_FLY"] = \
                                 '%s_%s_%d' % (self.dut.nextOper, self.dut.partNum[-3:], ec)
                              objMsg.printMsg('READ_OPTI DNGRADE_ON_FLY: %s' %(self.dut.driveattr["DNGRADE_ON_FLY"]))
                              raise
                        '''
                     #other ec(s)
                     else: ScrCmds.raiseException(ec, "Falling of t250 channel")

         else:
            oRdWr.phastOpti(self.zap_251_params(TP.base_phastOptiPrm_251.copy(), zapOtfWP, zapOtfWP2),maxRetries = 3, zapFunc = zapFunc, zapECList = self.zapECList) # laulc

      if testSwitch.FE_0136807_426568_P_BANSHEE_VSCALE_OPTI:
         if zapOTF == 0:
            oRdWr.phastOpti(TP.VSCALE_OptiPrm_251.copy(),maxRetries = 3, zapFunc = zapFunc, zapECList = self.zapECList)
         else:
            oRdWr.phastOpti(self.zap_251_params(TP.VSCALE_OptiPrm_251.copy(), zapOtfWP, zapOtfWP2),maxRetries = 3, zapFunc = zapFunc, zapECList = self.zapECList)
            
   #-------------------------------------------------------------------------------------------------------
   def WPC_TunePerHdZn(self, oRdWr, T251_param = TP.base_readOpti_Prm_251.copy(), zapFunc = None):

      tableData = []
      try:
         if testSwitch.FE_0251897_505235_STORE_WPC_RANGE_IN_SIM:
            from RdWr import CWpcRangeFile
            tableData = CWpcRangeFile().Retrieve_WpcRange()
         else:
            tableData = self.dut.dblData.Tables('P_TRIPLET_WPC').tableDataObj()
      except: pass
      if len(tableData) == 0:
         oRdWr.phastOpti(T251_param.copy(),maxRetries = 3, zapFunc = zapFunc, zapECList = self.zapECList) # laulc
      else:
         # make sure the register setting is correct
         # if base parameter change, this part of script also need to update
         # otherwise, fail. do not let wpc tuning change the wrong register sequence and go through.
         if T251_param['REG_TO_OPT4'][0] != 341:
            objMsg.printMsg('Register mismatch detected!!')
            raise

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
         optiPrm = T251_param.copy()
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
               optiPrm.update({'REG_TO_OPT4': (0x155, wpc, Wpc_Start, -1), 'TEST_HEAD': hd})
               oRdWr.phastOpti(optiPrm.copy(),maxRetries = 3, zapFunc = zapFunc, zapECList = self.zapECList) # laulc


         oRdWr.testZones = list(orig_testZones)

   #-------------------------------------------------------------------------------------------------------
   def CopyToAdjacentZone(self, oRdWr, regID):
      # duplicate regs in regID to adjacent (smaller) zones based on oRdWr.testZones
      regval = {}
      for iHd in range(self.dut.imaxHead):
         regval[iHd] = {}
         for iZn in oRdWr.testZones:
            if (iZn) and ((iZn-1) not in oRdWr.testZones):   # except zone 0 and tuned adjacent zones
               regval[iHd][iZn-1] = {}
            regval[iHd][iZn] = {}
            for nId in range(len(regID)):
               buf,errorCode = oRdWr.Fn(1336, regID[nId], iHd, iZn, retries=3)    # read ram copy channel reg
               result = struct.unpack("HH",buf)
               regval[iHd][iZn][nId]   = result[0]
               if (iZn) and ((iZn-1) not in oRdWr.testZones):   # except zone 0 and tuned adjacent zones
                  regval[iHd][iZn-1][nId] = result[0]
                  #objMsg.printMsg("Writing R%04X = 0x%02X for H%d Z%02d from Z%02d..." % (regID[nId], result[0], iHd, iZn, (iZn-1)))
                  buf,errorCode = oRdWr.Fn(1339, regID[nId], result[0], iHd, (iZn-1), retries=3) # write channel reg to ram copy
                  result = struct.unpack("H",buf)
                  if result[0] != 1:   # pass = 1, else error
                     ScrCmds.raiseException(11044, 'RdOpti Write Channel RAM cudacom failed!')
      # -------------------------------------------------

      objMsg.printMsg("----- RegID Copy Sanity check -----")
      strMsg = "Hd Zn"
      for nId in range(len(regID)):
         strMsg += str(" R%04X" % regID[nId])
      objMsg.printMsg(strMsg)
      for iHd in range(self.dut.imaxHead):
         for iZn in range(self.dut.numZones):
            strMsg = str("%2d %02d" % (iHd, iZn))
            for nId in range(len(regID)):
               strMsg += str("  %04X" % regval[iHd][iZn][nId])
            objMsg.printMsg(strMsg)

      self.oProc.St({'test_num' : 178, 'prm_name' : 'save_rap_to_flash_178', 'CWORD1' : 0x220,})

   #-------------------------------------------------------------------------------------------------------
   def AveragingRAPRegValues(self, oRdWr, regID):
      # Find the average RAP register values and over ride current RAP register value with the average value based on oRdWr.testZones
      objMsg.printMsg("regID %s" % (regID))
      regval = {}
      reg_avg_val = {}
      
      for iHd in range(self.dut.imaxHead):
         regval[iHd] = {}
         reg_avg_val[iHd] = {}
         sum = 0
         for iZn in oRdWr.testZones:
            regval[iHd][iZn] = {}
            for nId in range(len(regID)):
               buf,errorCode = oRdWr.Fn(1336, regID[nId], iHd, iZn, retries=3)    # read ram copy channel reg
               result = struct.unpack("HH",buf)
               val = result[0]
               if (val >= 32768):
                  val_hex = hex(val)
                  val = int(val_hex,16)-(1<<16) #handles two's complement
               regval[iHd][iZn][nId] = val
               objMsg.printMsg("H%d Z%02d R%04X = %u (dec)" % (iHd, iZn, regID[nId], val))
               sum = sum + val
               objMsg.printMsg("Accumulated sum for H%d = %d" % (iHd, sum))
               if (iZn == (len(oRdWr.testZones)-1)):
                  reg_avg_val[iHd][nId] = int(round(float(sum) / len(oRdWr.testZones)))
                  objMsg.printMsg("Average val for H%d = %d / %d = %d" % (iHd, sum, len(oRdWr.testZones), reg_avg_val[iHd][nId]))

      objMsg.printMsg("regval %s" % (regval))

      for iHd in range(self.dut.imaxHead):
         for iZn in oRdWr.testZones:
            for nId in range(len(regID)):
               buf,errorCode = oRdWr.Fn(1339, regID[nId], reg_avg_val[iHd][nId], iHd, iZn, retries=3) # write channel reg to ram copy
               result = struct.unpack("H",buf)
               if result[0] != 1:   # pass = 1, else error  
                  ScrCmds.raiseException(11044, 'RdOpti Write Channel RAM cudacom failed!')
                    

      self.oProc.St({'test_num' : 178, 'prm_name' : 'save_rap_to_flash_178', 'CWORD1' : 0x220,})

      objMsg.printMsg("----- RegID Average Sanity check -----")
      for iHd in range(self.dut.imaxHead):
         for iZn in oRdWr.testZones:
            for nId in range(len(regID)):
               buf,errorCode = oRdWr.Fn(1336, regID[nId], iHd, iZn, retries=3)    # read ram copy channel reg
               result = struct.unpack("HH",buf)
               val = result[0]
               if (val >= 32768):
                  val_hex = hex(val)
                  val = int(val_hex,16)-(1<<16) #handles two's complement
               objMsg.printMsg("Sanity check: H%d Z%02d R%04X = %u (dec)" % (iHd, iZn, regID[nId], val))

   #-------------------------------------------------------------------------------------------------------
   def zap_251_params(self, testParam, zapOtfWP, zapOtfWP2):
      korZAP_OTF = testParam
      korZAP_OTF.update(TP.prm_ZAP_OTF)
      korZAP_OTF['CWORD1'] |= 0x80
      korZAP_OTF['TRACK_LIMIT'] = 0
      korZAP_OTF['timeout'] = 10000 * self.dut.imaxHead
      if zapOtfWP == 1 and not zapOtfWP2:
         korZAP_OTF['GEN_PC_FILES'] = 1

      return korZAP_OTF

   #-------------------------------------------------------------------------------------------------------
   def IterativeChannelOpti(self, oRdWr, testZones, head=None):
      #Set up zones to test... (1 zone per head initially)
      from FSO import dataTableHelper
      self.dth = dataTableHelper()

      #----------------------------------------------------------------------------------------------------
      def overrideSqueeze(param, squeezeVal):
         tPrm = dict(param)
         tPrm['SQZ_OFFSET'] = squeezeVal
         return tPrm

      #----------------------------------------------------------------------------------------------------
      def getZonePositionTrack(iHead, zone, zt):

         Index = self.dth.getFirstRowIndexFromTable_byZone(zt, iHead, zone)
         startCyl = int(zt[Index]['ZN_START_CYL'])
         numTracks = int(zt[Index]['TRK_NUM'])
         while Index+1< len(zt) and int(zt[Index]['ZN']) == int(zt[Index+1]['ZN']):
            numTracks += int(zt[Index+1]['TRK_NUM'])
            Index += 1
         internalScalor = TP.ZONE_POS/(199.0) #ZONE_POS scalor

         return int((internalScalor * numTracks) + startCyl)

      #----------------------------------------------------------------------------------------------------
      def getTargetSqueeze(head, testZones, method = 'MAX'):
         testZones.sort()
         zt = self.dut.dblData.Tables(TP.zone_table['table_name']).tableDataObj()         
         tmpPrm = dict(TP.base_findTargetSqueeze_167)
         mxZone = max(testZones)
         minZone = min(testZones)
         midZone = minZone + ((mxZone-minZone)/2)
         sqzZones = [minZone, midZone , mxZone]

         testTracks = [getZonePositionTrack(head,i,zt) for i in sqzZones]

         optimalSqueeze = [0,]*len(testTracks)
         for index, track in enumerate(testTracks):
            tmpPrm['TEST_CYL'] = oRdWr.oUtility.ReturnTestCylWord(int(track))
            try:
               optimalSqueeze[index] = oRdWr.findTargetSqueeze(tmpPrm, head = head, errorRateRange = TP.base_Iterative_Squeeze_Range)
            except ScriptTestFailure, (failureData):
               #If we can't measure offtrack lets give it a chance ontrack
               optimalSqueeze[index] = 0
         if method == 'MAX':
            optSqz = int(max(optimalSqueeze))
         else:
            optSqz = int(sum(optimalSqueeze)/float(len(optimalSqueeze)))
         objMsg.printMsg("Optimal Squeeze is %d" % optSqz)
         return optSqz

      oRdWr.testZones = None

      #----------------------------------------------------------------------------------------------------
      def opti_A_Parameter(prm, saveVals = False, head = None):

         saveVals = saveVals & (not self.params.get('NO_FLASH_UPDATE',0))
         squeeze_method = self.params.get('SQZ_METHOD','MAX').upper()

         if self.params.get('BASELINE_BER',0):
            TP.base_Ber_verification_250['ZONE_MASK'] = oRdWr.oUtility.ReturnTestCylWord(oRdWr.oUtility.setZoneMask(testZones))
            oRdWr.St(TP.base_Ber_verification_250)

         try:
            try:
               if head is None:
                  heads = xrange(self.dut.imaxHead)
               else:
                  heads = [head]

               for head in heads:
                  #Set the head to test
                  oRdWr.headRange = head
                  oRdWr.testZones = None

                  optimalSqueeze = getTargetSqueeze(head, testZones, method = squeeze_method)
                  oRdWr.testZones = testZones

                  oRdWr.phastOpti(overrideSqueeze(prm, optimalSqueeze))

            finally:
               oRdWr.testZones = None
               if self.params.get('BASELINE_BER',0):

                  oRdWr.St(TP.base_Ber_verification_250)

         except:
            #if we don't want to save the data then ignore the failure and below hda will be power cycled
            if saveVals:
               raise

         if saveVals:
            oRdWr.oFSO.saveRAPtoFLASH()
         else:
            objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)


      opti_A_Parameter(TP.base_VSCALE_OptiPrm_251, saveVals = testSwitch.VSCALE_OPTI, head=head)

      opti_A_Parameter(TP.base_DECGAIN_OptiPrm_251, saveVals = testSwitch.DECGAIN_OPTI, head=head)

      opti_A_Parameter(TP.base_ECWIN_OptiPrm_251, saveVals = testSwitch.ECWIN_OPTI, head=head)

   #-------------------------------------------------------------------------------------------------------
   def basicTargetOpti(self, zappedOptiTracks, head=None):
      # Run TDTARGR opti
      # Compile necessary input parameters
      from RdWr import CProgRdChanTrg

      prctInPrm = TP.prm_ProgRdChanTarget
      prctInPrm['setNPT_156'] = TP.setNPT_156
      prctInPrm['tdtarg_OptiPrm_251'] = TP.tdtarg_OptiPrm_251
      oPRCT = CProgRdChanTrg()
      if zappedOptiTracks:
         zapFunc = None
      else:
         zapFunc = self.optiZAP
      oPRCT.setTargets(prctInPrm,zapFunc,self.zapECList, head)
   
   #-------------------------------------------------------------------------------------------------------
   def sanityCheckChannelParam(self, oRdWr):
      objMsg.printMsg("----- RegID Sanity check after -----")
      objMsg.printMsg("oRdWr.testZones: %s" % oRdWr.testZones)
         
      regIDcheckList = [ 37, 146, 147, 907, 1032, 155, 1031, 1033, 145, 906, 867, 908, 267, 258 ]
      for iHd in range(self.dut.imaxHead):
         for iZn in oRdWr.testZones:
            for nId in range(len(regIDcheckList)):
               try: 
                  buf, errorCode = oRdWr.Fn(1336, regIDcheckList[nId], iHd, iZn)    # read ram copy channel reg
               except: continue
               result = struct.unpack("HH",buf)
               val = result[0]
               if (val >= 32768):
                  val_hex = hex(val)
                  val = int(val_hex,16)-(1<<16) #handles two's complement
               objMsg.printMsg("Sanity check: H%d Z%02d R%04X = %u (dec)" % (iHd, iZn, regIDcheckList[nId], val))

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      """
      StateInfo Parameters
      RUN_TGT_OPTI: If set to 1 only target opti will be performed (no pre-zap ability available)
      """
      if testSwitch.CONDITIONAL_RUN_HMS:
         objMsg.printMsg("currentState=%s skipHMS=%s" % (self.dut.currentState, self.dut.skipHMS))
         if (self.dut.currentState in ['READ_OPTI1'] and self.dut.skipHMS):
            objMsg.printMsg("Skipping HMS related states")
            return

      if hasattr(TP,'zapECList'):
         self.zapECList = TP.zapECList
      else:
         self.zapECList = [10007]

      if self.params.get('ZONES'):
         testZones = eval(str(self.params.get('ZONES')))
      else: 
         testZones = range(self.dut.numZones)

      testHead  = self.params.get('HEAD', None)
      runTgtOpti = self.params.get('RUN_TGT_OPTI', 0) # Default is to skip target opti
      runIterativeOpti = self.params.get('RUN_ITERATIVE_OPTI',0) # Default is to skip iterative block opti
      zappedOptiTracks = False

      from RdWr import CRdWrOpti
      oRdWr = CRdWrOpti(self.params)
      oRdWr.oFSO.getZoneTable()

      #Execute basic target opti
      if runTgtOpti and not testSwitch.targetOptiIn251:
         try:
            self.basicTargetOpti(zappedOptiTracks, testHead)
         except ScriptTestFailure, (failuredata):
            if failuredata[0][2] in self.zapECList and not zappedOptiTracks:
               if testHead is None:
                  self.optiZAP(testZones)
               else:
                  self.optiZAP(testZones, testHeads=[testHead])
               zappedOptiTracks = True
               self.basicTargetOpti(zappedOptiTracks, testHead)
            else:
               raise
         return

      if runIterativeOpti:
         try:
            self.IterativeChannelOpti(oRdWr, testZones, head=testHead)
         except ScriptTestFailure, (failuredata):
            if failuredata[0][2] in self.zapECList and not zappedOptiTracks:
               if testHead is None:
                  self.optiZAP(testZones)
               else:
                  self.optiZAP(testZones, testHeads=[testHead])
               zappedOptiTracks = True
               self.IterativeChannelOpti(oRdWr, testZones, head=testHead)
            else:
               raise

         return

      #IF we aren't zapping by exception only then lets skip the initial
      # Also if we are handling the system area then lets still zap
      if testZones == [self.dut.numZones,]:
         if testHead is None:
            self.optiZAP(testZones)
         else:
            self.optiZAP(testZones, testHeads=[testHead])
         zappedOptiTracks = True
      elif testSwitch.FE_SGP_OPTIZAP_ADDED:
         objMsg.printMsg("nextState: %s" % self.dut.nextState)
         if self.dut.nextState in TP.zapOnstatelist: #defined in the base_testParameter
            if testSwitch.ENABLE_T175_ZAP_CONTROL:
               self.oProc.St(TP.zapPrm_175_zapOn)
            else:
               self.oProc.St(TP.setZapOnPrm_011)
               if not testSwitch.BF_0119055_231166_USE_SVO_CMD_ZAP_CTRL:
                  self.oProc.St({'test_num':178, 'prm_name':'Save SAP in RAM to FLASH', 'CWORD1':0x420})
         zappedOptiTracks = True

      oRdWr.headRange = testHead
      oRdWr.testZones = testZones #Set the test zones to be based on input mask
      if self.params.get('ON_TRK_BER_ZONES'):
         oRdWr.onTrackTestZonesBER = eval(str(self.params.get('ON_TRK_BER_ZONES')))
      else: oRdWr.onTrackTestZonesBER = oRdWr.testZones
      if self.params.get('SQZ_WRT_BER_ZONES'):
         oRdWr.sqzWrtTestZonesBER = eval(str(self.params.get('SQZ_WRT_BER_ZONES')))
      else: oRdWr.sqzWrtTestZonesBER = oRdWr.testZones
      
      if self.params.get('REDUCE_ZONE_250', 0):
         oRdWr.onTrackTestZonesBER = TP.Measured_BPINOMINAL_Zones 

      if verbose:   objMsg.printMsg("Testing zones: %s" % str(testZones), objMsg.CMessLvl.DEBUG)
      if testHead is not None:
         objMsg.printMsg("Testing head %d" % testHead, objMsg.CMessLvl.DEBUG)

      ## dump channel before channel tune
      if self.params.get('SANITY_CHECK_CHANNEL_PARAMS', 0):
         self.sanityCheckChannelParam(oRdWr)

      #Execute basic AGERE Opti
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      try:
         if testSwitch.FE_0150693_409401_P_KORAT_ZAP_OTF and self.params.get('ZAP_OTF',0) or self.zapOtfWP == 1 or self.zapOtfZN == 1 or self.zapOtfHMS == 1:
            self.basicAGEREOpti(oRdWr, zappedOptiTracks, runTgtOpti, zapOTF = 1, zapOtfWP=self.zapOtfWP, zapOtfWP2=self.zapOtfWP2)
         else:
            self.basicAGEREOpti(oRdWr, zappedOptiTracks, runTgtOpti)
      except ScriptTestFailure, (failuredata):
         if failuredata[0][2] in self.zapECList and not zappedOptiTracks:
            if testHead is None:
               self.optiZAP(testZones)
            else:
               self.optiZAP(testZones, testHeads=[testHead])
            zappedOptiTracks = True
            if testSwitch.FE_0150693_409401_P_KORAT_ZAP_OTF and self.params.get('ZAP_OTF',0) or self.zapOtfWP == 1 or self.zapOtfZN == 1 or self.zapOtfHMS == 1:
               self.basicAGEREOpti(oRdWr, zappedOptiTracks, runTgtOpti, zapOTF = 1, zapOtfWP=self.zapOtfWP, zapOtfWP2=self.zapOtfWP2)
            else:
               self.basicAGEREOpti(oRdWr, zappedOptiTracks, runTgtOpti)
         else:
            raise

      oRdWr.oFSO.saveRAPSAPtoFLASH()
      
       ## dump channel after channel tune
      if self.params.get('SANITY_CHECK_CHANNEL_PARAMS', 0):
         self.sanityCheckChannelParam(oRdWr)
      
      oRdWr.headRange = None
      oRdWr.testZones = None
      
      #set testZones to None to force TA_LPF calling not become zone bank calling
      if not testSwitch.USE_DEFAULT_TA_LPF:
         #Initialize TA low pass filter values in RAP
         oRdWr.St(TP.TA_LPF_prm_178)

      if testSwitch.FE_SGP_OPTIZAP_ADDED: #Turn off Zap
         objMsg.printMsg("nextState: %s" % self.dut.nextState)
         if self.dut.nextState in TP.zapOffstatelist: #defined in the base_testParameter
            if testSwitch.ENABLE_T175_ZAP_CONTROL:
               self.oProc.St(TP.zapPrm_175_zapOff)
            else:
               self.oProc.St(TP.setZapOffPrm_011)
               if not testSwitch.BF_0119055_231166_USE_SVO_CMD_ZAP_CTRL:
                  self.oProc.St({'test_num':178, 'prm_name':'Save SAP in RAM to FLASH', 'CWORD1':0x420})
      

#----------------------------------------------------------------------------------------------------------
class CRdOptiZoneInsertion(CState):
   """
   get opti zone and its insertion
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      self.dut = dut
      depList = []
      CState.__init__(self, dut, depList)
     
      from FSO import dataTableHelper
      from Process import CCudacom 
      
      self.dth = dataTableHelper()
      self.oCudacom = CCudacom()

   #-------------------------------------------------------------------------------------------------------
   def group_N_continous_zones_in_list(self, lst, num_per_group):
      """ Read_opti for zone copy functionality support
      @param lst: test zone list.
      @param num_per_group: number of zones you want to group together as one group.
      Example:
      lst, a list of test zones consisting non-UMP zones: [0, 1, 2, 3, 4, 11, 12, 13, 14, 15, 16, 17, 18, 19, ..., 178]
      num_per_group: 5. We want to group them into sub-groups of 5 zones.
      cont_zn_group2: resultant list is [[0, 1, 2, 3, 4], [11, 12, 13, 14, 15], [16, 17, 18, 19, 20], ..., [176, 177, 178]]
      """
      cont_zn_group = []
      a = b = lst[0]
      for zn in lst[1:]:
         if zn == b+1:
            b = zn
         else:
            if a==b:
               cont_zn_group.append([a])
            else:
               cont_zn_group.append(range(a, b+1))
            a = b = zn
      cont_zn_group.append(range(a, b+1))
      if verbose:   objMsg.printMsg("cont_zn_group = %s" % cont_zn_group)
      # cont_zn_group = [[0, 1, 2, 3, 4], [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178]]
      # cont_zn_group = [[5, 6, 7, 8, 9, 10], [179]]

      cont_zn_group2 = []
      for zn_group in cont_zn_group:
         subList = [zn_group[n:n+num_per_group] for n in range(0, len(zn_group), num_per_group)]
         for lst in subList:
            cont_zn_group2.append(lst)
      if verbose:   objMsg.printMsg("cont_zn_group2 = %s" % cont_zn_group2)
      # cont_zn_group2 = [[0, 1, 2, 3, 4], [11, 12, 13, 14, 15], [16, 17, 18, 19, 20], [21, 22, 23, 24, 25], [26, 27, 28, 29, 30], [31, 32, 33, 34, 35], [36, 37, 38, 39, 40], [41, 42, 43, 44, 45], [46, 47, 48, 49, 50], [51, 52, 53, 54, 55], [56, 57, 58, 59, 60], [61, 62, 63, 64, 65], [66, 67, 68, 69, 70], [71, 72, 73, 74, 75], [76, 77, 78, 79, 80], [81, 82, 83, 84, 85], [86, 87, 88, 89, 90], [91, 92, 93, 94, 95], [96, 97, 98, 99, 100], [101, 102, 103, 104, 105], [106, 107, 108, 109, 110], [111, 112, 113, 114, 115], [116, 117, 118, 119, 120], [121, 122, 123, 124, 125], [126, 127, 128, 129, 130], [131, 132, 133, 134, 135], [136, 137, 138, 139, 140], [141, 142, 143, 144, 145], [146, 147, 148, 149, 150], [151, 152, 153, 154, 155], [156, 157, 158, 159, 160], [161, 162, 163, 164, 165], [166, 167, 168, 169, 170], [171, 172, 173, 174, 175], [176, 177, 178]]
      # cont_zn_group2 = [[5, 6, 7], [8, 9, 10], [179]]
      return cont_zn_group2
   
   #-------------------------------------------------------------------------------------------------------
   def get_frequency (self, hd, zn):
      try: zonetable = self.dut.dblData.Tables(TP.zone_table['table_name']).tableDataObj()
      except:
         return 1  #error code 
      Index = self.dth.getFirstRowIndexFromTable_byZone(zonetable, hd, zn)
      frequency = int(zonetable[Index]['NRZ_FREQ'])
      return frequency


   #-------------------------------------------------------------------------------------------------------
   def get_radius(self, hd, zn):
      try: zonetable = self.dut.dblData.Tables(TP.zone_table['table_name']).tableDataObj()
      except:
         return 9999  #error code 

      Index = self.dth.getFirstRowIndexFromTable_byZone(zonetable, hd, zn)
      startTrk = int(zonetable[Index]['ZN_START_CYL'])
      numTrk = int(zonetable[Index]['TRK_NUM'])
      while Index+1< len(zonetable) and int(zonetable[Index]['ZN']) == int(zonetable[Index+1]['ZN']):
         numTrk += int(zonetable[Index+1]['TRK_NUM'])
         Index += 1
      trk      = int(startTrk + numTrk/2) # use middle track
       #  ConvertLogicalTrack
      buf,errorCode  = self.oCudacom.Fn(1370, trk & 0xFFFF,( trk>>16)& 0xFFFF, hd, 0)
      if testSwitch.virtualRun:
         return 9999  #error code
      result = struct.unpack(">LLH", buf)
      radius = float (result[2]/(16.0*1000.0))
      return radius

   #-------------------------------------------------------------------------------------------------------
   def get_KFCI(self, hd, zn):
      row = self.kfciTBL.findRow({'HD_LGC_PSN': hd, 'DATA_ZONE': zn, 'SPC_ID' : self.spcIDKFCI})
      return float(row['MD_KFCI'])

   #-------------------------------------------------------------------------------------------------------
   def zn_KFCI_chk(self, zn_group, opti_Zn_index, KFCI_insert_limit, optiHead=None, base_Zns=None):

      insert_zn= {}
      if (optiHead == None):
         optiHead = range(self.dut.imaxHead)
      else:
         if not type(optiHead) is list:
            optiHead = [optiHead]

      for hd in optiHead:
         insert_zn[hd]= []
         
      if testSwitch.FE_0385234_356688_P_MULTI_ID_UMP:
         lastSMRZn = -1
      else:
         lastSMRZn = -2
         
      for cont_zns in zn_group:
         #a= opti_Zn_index[len(lst)] 
         opti_Zn = sorted(cont_zns)[opti_Zn_index[len(cont_zns)]]
         if cont_zns.count(TP.baseVbarTestZones[self.dut.numZones][lastSMRZn]):
             opti_Zn = TP.baseVbarTestZones[self.dut.numZones][lastSMRZn] # special handlinig for last shingle zone in zone allignement
         for hd in optiHead:
            ref_KFCI= self.get_KFCI(hd, opti_Zn)
            printDbgMsg("opti_zn[%d] hd[%d] ref_KFCI[%f] " % (opti_Zn, hd, ref_KFCI))

            for zn in cont_zns :
               if zn == opti_Zn: continue
               if base_Zns != None and zn not in base_Zns: continue # skip if zn is not in base zone
               KFCI = self.get_KFCI(hd, zn)
               ratio = KFCI/ref_KFCI
               printDbgMsg("copied_zn[%d] hd[%d] KFCI[%f] ratio[%f] " % (zn, hd, KFCI, ratio))
               if (ratio> (1+ KFCI_insert_limit)):
                  insert_zn[hd].append(zn)  
               if (ratio < (1-KFCI_insert_limit)) :
                  insert_zn[hd].append(zn)      

      return insert_zn
   
   #-------------------------------------------------------------------------------------------------------
   def ZnToRemove(self, optiZn_list, zn_list):
      for zn in zn_list:
         if optiZn_list.count(zn) > 0:
            optiZn_list.remove(zn)
            
   #-------------------------------------------------------------------------------------------------------
   def run(self, optiHead=None, base_Zns=None, skip_UMP = False):
      # optiHead will be set 0 or 1 representing head 0 or head 1 in var_spares if the head requires KFCI check and T251 zone copy. 
      printDbgMsg("optiHead = %s" % optiHead)
      if testSwitch.FE_0306627_403980_P_ZONEINSERTION_FOR_DIFF_WRITE_POWER:
         self.oFSO.getWritePowers(supressOutput = not testSwitch.extern.FE_0255966_357263_T172_AFH_SUMMARY_TBL)
         wps = self.dut.dblData.Tables('P172_WRITE_POWERS').tableDataObj()

         wp_info_byhdzn = {}
         for i in xrange(len(wps)):
            iZone = int(wps[i]['DATA_ZONE'])
            iHead = int(wps[i]['HD_LGC_PSN'])
            Iw = int(wps[i]['WRT_CUR'])
            Ovs = int(wps[i]['OVS_WRT_CUR'])
            Ovd = int(wps[i]['OVS_DUR'])
            wp_info = (Iw, Ovs, Ovd) #-> WP Triplet Format: (Write Current, Overshoot, Overshoot Duration)
            if not wp_info_byhdzn.has_key(iHead):
               wp_info_byhdzn[iHead]={}
            if not wp_info_byhdzn[iHead].has_key(iZone):
               wp_info_byhdzn[iHead][iZone]=wp_info
               
      for table in ['OPTI_ZN_SUMMARY']:
         try:
            self.dut.dblData.Tables(table).deleteIndexRecords(1)
            self.dut.dblData.delTable(table, forceDeleteDblTable = 1)
         except: pass
         
      #this will get from testparameter later, hardcoded here first
      pre_optiZones = range(0, self.dut.numZones, 1)  #this will get from testparameter later
      import dbLogUtilities
      self.kfciTBL = dbLogUtilities.DBLogReader(self.dut, 'P172_ZONED_SERVO2')
      self.spcIDKFCI = 3
      try:
         nonUMP_zoneGroup_size = TP.nonUMP_zoneGroup_size                       
         ump_zoneGroup_size = TP.ump_zoneGroup_size
         opti_Zn_index= TP.opti_Zn_index #opti zone index array for group size
         firstBaseVbarZone = TP.baseVbarTestZones[self.dut.numZones][0]
         KFCI_insert_limit = TP.KFCI_insert_limit #insert criteria, eg, KFCI +-1%
      except: # in case not syn up with testparameter.py
         nonUMP_zoneGroup_size = 5                       
         ump_zoneGroup_size = 1
         opti_Zn_index= [0,0,0,0,0,2,0,0,0,0] #opti zone index array for group size
         KFCI_insert_limit = 0.01             #insert criteria, eg, KFCI +-1%
         
      from FSO import CFSO
      self.oFSO = CFSO()
      self.oFSO.getKFCI(self.spcIDKFCI)
      self.ZnToRemove(pre_optiZones, TP.UMP_ZONE[self.dut.numZones])
            
      if testSwitch.FE_0274346_356688_ZONE_ALIGNMENT:
         self.ZnToRemove(pre_optiZones, TP.MC_ZONE)
         firstzoneafterUMP = TP.UMP_ZONE[self.dut.numZones][-2]+1
            
         if testSwitch.FE_0385234_356688_P_MULTI_ID_UMP:
            firstzoneafterUMP = TP.MC_ZONE[-1] + 1
            ID_ZONE = range(TP.baseVbarTestZones[self.dut.numZones][-1]+1,(TP.UMP_ZONE[self.dut.numZones][0]),1)
            self.ZnToRemove(pre_optiZones, ID_ZONE)
            
         if firstzoneafterUMP <= firstBaseVbarZone: # In this case, the test zone still aligned with Vbar test zone. 
            zn_grp4 = range(firstzoneafterUMP, firstBaseVbarZone) 
            firstZone = firstBaseVbarZone
         else:                                      # In this case, the test zone no longer aligned with Vbar test zone for the moment
            zn_grp4 = []
            firstZone = firstzoneafterUMP
               
         self.ZnToRemove(pre_optiZones, zn_grp4)
         zn_grp3 = range(firstZone, firstZone + nonUMP_zoneGroup_size - opti_Zn_index[nonUMP_zoneGroup_size])
         self.ZnToRemove(pre_optiZones, zn_grp3)
      OptiZn_SMR = pre_optiZones
      
      zn_group = []
      if testSwitch.FE_0274346_356688_ZONE_ALIGNMENT:
         zn_group = self.group_N_continous_zones_in_list(TP.MC_ZONE, ump_zoneGroup_size) + [zn_grp3]
         if testSwitch.FE_0385234_356688_P_MULTI_ID_UMP:
            zn_group = zn_group + self.group_N_continous_zones_in_list(zn_grp4, ump_zoneGroup_size)
            zn_group = zn_group + self.group_N_continous_zones_in_list(ID_ZONE, ump_zoneGroup_size)
         else:
            if len(zn_grp4)>0:
               zn_group = zn_group + [zn_grp4]

      if skip_UMP:
         zn_group =zn_group +  self.group_N_continous_zones_in_list(OptiZn_SMR, nonUMP_zoneGroup_size)
      else:
         zn_group =zn_group +  self.group_N_continous_zones_in_list(OptiZn_SMR, nonUMP_zoneGroup_size)+\
            self.group_N_continous_zones_in_list(TP.UMP_ZONE[self.dut.numZones], ump_zoneGroup_size)

      printDbgMsg("zn_group = %s" % zn_group)
      if verbose:   objMsg.printMsg("opti_Zn_index= %s" % opti_Zn_index)
      
      if testSwitch.FE_0306627_403980_P_ZONEINSERTION_FOR_DIFF_WRITE_POWER:
         objMsg.printMsg("New ZONEINSERTION routine, consider WP..")
         zn_group_wp = {}
         for lst in zn_group:
            wp_info_grp = {}
            for zn in lst:
               for hd in range(self.dut.imaxHead):
                  wp_info = wp_info_byhdzn[hd][zn]
                  if not wp_info_grp.has_key(hd):
                     wp_info_grp[hd]={}
                  if not wp_info_grp[hd].has_key(wp_info):
                     wp_info_grp[hd][wp_info]=[]
                  if zn not in wp_info_grp[hd][wp_info]:
                     wp_info_grp[hd][wp_info].append(zn)
            for hd in range(self.dut.imaxHead):
               if not zn_group_wp.has_key(hd):
                  zn_group_wp[hd]=[]
               for wp_info in wp_info_grp[hd]:
                  lst2 = wp_info_grp[hd][wp_info]
                  if not lst2 in zn_group_wp[hd]:
                     zn_group_wp[hd].append(lst2)
                     
      insert_zn = {}
      insert_zn = self.zn_KFCI_chk(zn_group, opti_Zn_index, KFCI_insert_limit, optiHead, base_Zns)  #to be continued
      objMsg.printMsg("insert_zn = %s" % insert_zn)
      opti_lst = []
      if (optiHead == None):
         optiHead = 0xFF
         
      if testSwitch.FE_0385234_356688_P_MULTI_ID_UMP:
         lastSMRZn = -1
      else:
         lastSMRZn = -2
         
      for lst in zn_group:
         #a= opti_Zn_index[len(lst)]
         if not lst.count(TP.baseVbarTestZones[self.dut.numZones][lastSMRZn]):
             opti_lst.append(sorted(lst)[opti_Zn_index[len(lst)]])
             self.dut.dblData.Tables('OPTI_ZN_SUMMARY').addRecord({
                   'HD_PHYS_PSN'         : optiHead, #0xFF,  # hd
                   'OPTI_ZONE'           : sorted(lst)[opti_Zn_index[len(lst)]],
                   'ZN_GRP_START'        : sorted(lst)[0],
                   'ZN_GRP_END'          : sorted(lst)[len(lst)-1],
                   #copy to number of  front zonse( high nibble) and back zones( low nibble )
                   'ZN_COPY_OPTION'      : ( opti_Zn_index[len(lst)]<<8 ) | (len(lst) -1- opti_Zn_index[len(lst)]) ,
             })
         else: # zone 148
             opti_lst.append(TP.baseVbarTestZones[self.dut.numZones][lastSMRZn])
             self.dut.dblData.Tables('OPTI_ZN_SUMMARY').addRecord({
                   'HD_PHYS_PSN'         : optiHead, #0xFF,  # hd
                   'OPTI_ZONE'           : TP.baseVbarTestZones[self.dut.numZones][lastSMRZn],
                   'ZN_GRP_START'        : sorted(lst)[0],
                   'ZN_GRP_END'          : sorted(lst)[len(lst)-1],
                   #copy to number of  front zonse( high nibble) and back zones( low nibble )
                   'ZN_COPY_OPTION'      : (TP.baseVbarTestZones[self.dut.numZones][lastSMRZn]- sorted(lst)[0]) <<8  | ( sorted(lst)[-1]-TP.baseVbarTestZones[self.dut.numZones][lastSMRZn]) ,
             })

      for hd in insert_zn:
         for zn in insert_zn[hd] :
            self.dut.dblData.Tables('OPTI_ZN_SUMMARY').addRecord({
                  'HD_PHYS_PSN'         : hd,  
                  'OPTI_ZONE'           : zn,
                  'ZN_GRP_START'        : zn,
                  'ZN_GRP_END'          : zn,
                  #no zone copy for single zone
                  'ZN_COPY_OPTION'      : 0,
            })
      objMsg.printDblogBin(self.dut.dblData.Tables('OPTI_ZN_SUMMARY'))


#----------------------------------------------------------------------------------------------------------
if testSwitch.FE_SGP_PREAMP_GAIN_TUNING:
   class CVGACal(CState):
      """
      Description: Class that will perform a 1 stop Servo Calibration
      Base: Standard MDW cals, with the option to run T43 radial cals for MD drives
      """
      #-------------------------------------------------------------------------------------------------------
      def __init__(self, dut, params={}):
         self.params = params
         depList = ['HEAD_CAL']
         CState.__init__(self, dut, depList)
      
      #-------------------------------------------------------------------------------------------------------
      def run(self):
         import time
         from FSO import CFSO, dataTableHelper   
         from Servo import CServo
         from Channel import CChannelAccess
 
         self.dth = dataTableHelper()
         self.oFSO = CFSO()
         self.oServo = CServo()
         self.oChannelAccess = CChannelAccess()

         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
         # For debug only
         #setPreamp = {'test_num':11, 'prm_name':"getPreampGain", 'CWORD1':2, 'timeout':100, 'START_ADDRESS': (1L, 35606L), 'END_ADDRESS':  (1L, 35606L), 'ACCESS_TYPE':2, 'WR_DATA':5409}
         #self.oServo.St(setPreamp)

         self.oServo.St(TP.spinupPrm_1)

         testZone = 0
         self.oFSO.getZoneTable()
         ret = self.oServo.wsk(1000,0)
         objMsg.printMsg('Error Code: %s during seek.' % (str(ret)))
         time.sleep(50)


#  #      useSYSZnParm = self.params.get('USE_SYSZN_PARM', 0) # Default is not to use different parameters for sys zone
#  #      #objOpti = CRdOpti(self.dut, {'ZONES':[self.dut.numZones,],'zapFromDut':self.params.get('zapFromDut',0), 'DISABLE_ZAP': False}, useSYSZnParm)
#  #      objOpti.run()
         useSYSZnParm = 1


         for hd in range(self.dut.imaxHead):
            vgar = 0
            gainAdj = 0
            zt = self.dut.dblData.Tables(TP.zone_table['resvd_table_name']).tableDataObj()
            #userZoneTable = self.dut.dblData.Tables(TP.zone_table['table_name']).tableDataObj()            
            startResIndex = self.dth.getFirstRowIndexFromTable_byHead(tbl, hd)
            sysAreaStart = int(zt[startResIndex]['ZN_START_CYL'])
            teststartcyl = sysAreaStart

#  #         index = testZone + (self.dut.numZones*hd)
#  #         teststartcyl=int(zt[index]['ZN_START_CYL'])
            ret = self.oServo.wsk(teststartcyl,hd)
            buf, errorCode = self.oServo.Fn(1355)   # write 1 track
            buf, errorCode = self.oServo.Fn(1355)   # write 1 track
            objMsg.printMsg('Error Code: %s during write.' % (str(errorCode)))

            if (errorCode != 0) :
               gainAdj = 2

            ret = self.oServo.rsk(teststartcyl,hd)
            buf, errorCode = self.oServo.Fn(1356,0)   # read 1 track
            buf, errorCode = self.oServo.Fn(1356,0)   # read 1 track
            objMsg.printMsg('Error Code: %s during read.' % (str(errorCode)))

            if (errorCode != 0) :
               gainAdj = 2

            vgar = self.oChannelAccess.readChannel(0x12C)  # get VGA
            vgar &= 0xFF
            objMsg.printMsg("%-4d%-4d" % (hd,teststartcyl))
            objMsg.printMsg("VGA = 0x%x" % vgar)

            """
            Read Preamp register
            @param Address: Preamp register to read
            @param Page: Page select. Default zero, non zero value selects second page.
            @return: Error code
            """
            buf, errorCode = self.oServo.Fn(1291, 132, 0, 32, 0, 0, 1)
            if testSwitch.virtualRun:
               result = [0x16580]
            else:
               result = struct.unpack("L",buf)
            data = result[0:1]
            objMsg.printMsg("PG2 = 0x%x" % (data[0]+(2*hd)))

            #getPreamp = {'test_num':11, 'prm_name':"getPreampGain", 'CWORD1':1, 'timeout':100, 'START_ADDRESS': (0x1,0x8cfe), 'END_ADDRESS':  (0x1,0x8cfe), 'ACCESS_TYPE':2, 'WR_DATA':0}
            getPreampGain_prm = TP.getPreampGain.copy()
            getPreampGain_prm['START_ADDRESS']  = self.oServo.oUtility.ReturnTestCylWord((data[0]+(2*hd)))
            getPreampGain_prm['END_ADDRESS']  = self.oServo.oUtility.ReturnTestCylWord((data[0]+(2*hd)))
            self.oServo.St(getPreampGain_prm)

            gainByte3 = int(str(self.dut.dblData.Tables('P011_RW_SRVO_RAM_VIA_ADDR').tableDataObj()[-1]['SRVO_DATA']),16)
            gain = (gainByte3 & 0xF00) >> 8
            objMsg.printMsg("Preamp gain for head %d = 0x%x" % (hd, gainByte3))

            if (vgar < TP.VGAR_LowerLimit) and (gainAdj == 0) and (gain > 0):
               gain -= 1
               gainAdj = 1
            elif (vgar > TP.VGAR_UpperLimit) and (gainAdj == 0) and (gain < 7):
               gain += 1
               gainAdj = 1
            else:
               objMsg.printMsg("No adjustment needed...")
               gainAdj = 0

            if (gainAdj == 1):
               newGain = gainByte3 & 0xF0FF
               newGain |= gain << 8
               objMsg.printMsg("New Preamp gain for head %d = 0x%x" % (hd, newGain))
               #setPreamp = {'test_num':11, 'prm_name':"getPreampGain", 'CWORD1':2, 'timeout':100, 'START_ADDRESS': (0x1,0x8cfe), 'END_ADDRESS':  (0x1,0x8cfe), 'ACCESS_TYPE':2, 'WR_DATA':0}
               setPreampGain_prm = TP.setPreampGain.copy()
               setPreampGain_prm['START_ADDRESS']  = self.oServo.oUtility.ReturnTestCylWord((data[0]+(2*hd)))
               setPreampGain_prm['END_ADDRESS']  = self.oServo.oUtility.ReturnTestCylWord((data[0]+(2*hd)))
               setPreampGain_prm['WR_DATA']  = newGain
               self.oServo.St(setPreampGain_prm)
               self.oFSO.saveSAPtoFLASH()

               ret = self.oServo.wsk(teststartcyl,hd)
               buf, errorCode = self.oServo.Fn(1355)   # write 1 track
               buf, errorCode = self.oServo.Fn(1355)   # write 1 track
               objMsg.printMsg('Error Code: %s during write.' % (str(errorCode)))

               ret = self.oServo.rsk(teststartcyl,hd)
               buf, errorCode = self.oServo.Fn(1356)   # read 1 track
               buf, errorCode = self.oServo.Fn(1356)   # read 1 track
               objMsg.printMsg('Error Code: %s during read.' % (str(errorCode)))

               vgarNew = self.oChannelAccess.readChannel(0x12C)  # get VGA
               vgarNew &= 0xFF
               objMsg.printMsg("NEW VGA = 0x%x" % vgarNew)
               self.oServo.St(TP.PresetAGCPrm_186)
               self.oServo.St(TP.spinupPrm_1)


#----------------------------------------------------------------------------------------------------------
class CMeasureCBD(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from Process import CProcess
      self.oProc = CProcess()

      CBD_param = TP.CBDMeasurement_Prm_251.copy()

      if testSwitch.extern.FE_0280068_322482_CBD_MEASUREMENT:
         try:
            objOpti = CRdOpti(self.dut, {'ZONES':range(self.numUserZones)})
            objOpti.optiZAP([0,75,135,],trackLimit=0x0303,zonePos=198)
         except:
            pass
         CBD_param['ZONE_MASK_BANK'] = 0                 #0
         CBD_param['BIT_MASK']      = (0, 0x0001)
         try:
            self.oProc.St(CBD_param)  #zone 0
         except:
            pass
         #objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
         CBD_param['ZONE_MASK_BANK'] = 1                 #75
         CBD_param['BIT_MASK']      = (0, 0x0800)
         try:
            self.oProc.St(CBD_param)
         except:
            pass
         #objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
         CBD_param['ZONE_MASK_BANK'] = 2                 
         CBD_param['BIT_MASK']      = (0, 0x0080)
         try:
            self.oProc.St(CBD_param)                             #135 
         except:
            pass
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

      if testSwitch.FE_0358600_322482_P_ESNR_CBD:
         CBD_param = TP.eSNR_Prm_488.copy()
         if self.dut.nextOper == 'FNC2' or self.dut.nextOper == 'PRE2' :
            # CBD_param['CWORD1']    = 2                 #0
            CBD_param['CWORD2']    = 5     
         self.oProc.St(CBD_param)
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
#----------------------------------------------------------------------------------------------------------

class CSet_Target(CState):

   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      self.dut = dut
      depList = []
      CState.__init__(self, dut, depList)
     
      from FSO import dataTableHelper
      from Process import CCudacom 
      
      self.dth = dataTableHelper()
      self.oCudacom = CCudacom()
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      oProc = CProcess()
      target= TP.TargetLoop[self.params.get('TARGET_INDEX', 0)]
      objMsg.printMsg("TargetLoop %d" % (self.params.get('TARGET_INDEX', 0)))
      for iHd in range(self.dut.imaxHead):
        for iZn in range(self.dut.numZones):
           buf,errorCode = self.oCudacom.Fn(1339, 0xC2, target[0], iHd, iZn,retries=10) # write channel reg to ram copy
           buf,errorCode = self.oCudacom.Fn(1339, 0xC3, target[1], iHd, iZn,retries=10) # write channel reg to ram copy
           buf,errorCode = self.oCudacom.Fn(1339, 0xC4, target[2], iHd, iZn,retries=10) # write channel reg to ram copy
           result = struct.unpack("H",buf)
           if result[0] != 1:   # 1 is PASS
               ScrCmds.raiseException(11044, 'Write Channel RAM cudacom failed!')

      oProc.St({'test_num' : 178,'prm_name' : 'save Flash','CWORD1'   : 0x620,})

      for iHd in range(self.dut.imaxHead):
        for iZn in range(self.dut.numZones):
           buf,errorCode = self.oCudacom.Fn(1336, 0xC2, iHd, iZn, retries=10)# write channel reg to ram copy
           result = struct.unpack("HH",buf)
           tgt0= result[0]

           buf,errorCode = self.oCudacom.Fn(1336, 0xC3, iHd, iZn, retries=10)# write channel reg to ram copy
           result = struct.unpack("HH",buf)
           tgt1= result[0]


           buf,errorCode = self.oCudacom.Fn(1336, 0xC4, iHd, iZn, retries=10)# write channel reg to ram copy
           result = struct.unpack("HH",buf)
           tgt2= result[0]
           objMsg.printMsg("zone-%3d Hd-%3d tgt1-%2d tgt2-%2d tgt3-%2d" % (iZn,iHd,tgt0,tgt1,tgt2))


class CPreCautionaryOpti(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from Process import CProcess
      oProc = CProcess()
      
      #ZAP On
      oProc.St(TP.zapPrm_175_zapOn)
      
      #Precautionary CH LUT    
      if (testSwitch.FE_0345154_403980_P_ZONE_COPY_OPTIONS_T256):
         from RdWr import CRdWrOpti
         oRdWr = CRdWrOpti(self.params)
         oRdWr.oFSO.getZoneTable()
         if self.params.get('ON_TRK_BER_ZONES'):
            oRdWr.testZones = eval(str(self.params.get('ON_TRK_BER_ZONES')))
            oRdWr.headRange = self.params.get('HEAD', None)
         else:
            oRdWr.testZones
            oRdWr.headRange = None
         objMsg.printMsg("oRdWr.testZones: %s" % oRdWr.testZones)
         objMsg.printMsg("oRdWr.headRange: %s" % oRdWr.headRange)
         orgheadRange = oRdWr.headRange
         orgtestZones = oRdWr.testZones
         T256_ATE_param = TP.Precautionary_Opti_Prm_ATE.copy()
         T256_WW_param = TP.Precautionary_Opti_Prm_WW.copy()
         
         try:
            self.T256_zone_copy_support(T256_ATE_param,oRdWr)
            # Reset headRange & testZones for next T256 WW to run properly. 
            oRdWr.headRange = orgheadRange
            oRdWr.testZones = orgtestZones
            self.T256_zone_copy_support(T256_WW_param,oRdWr)
         except:
            objMsg.printMsg("fatal errors during Precautionary CH Opti Test")
            raise
         oRdWr.headRange = orgheadRange
         oRdWr.testZones = orgtestZones               
      else:
         try:
            oProc.St(TP.Precautionary_Opti_Prm_ATE)
            oProc.St(TP.Precautionary_Opti_Prm_WW)
         except:
            objMsg.printMsg("fatal errors during Precautionary CH Opti Test")
            raise
         
      #ZAP Off
      oProc.St(TP.zapPrm_175_zapOff) 
      ## END #### DATA OUTPUT TESTS ONLY--- NO FAILURE
   #-------------------------------------------------------------------------------------------------------   

   def T256_zone_copy_support(self,T256_Para,oRdWr):
      from Utility import CUtility
      self.oUtility = CUtility()
      from Process import CProcess
      oProc = CProcess()
      try: 
          opti_Zn_index= TP.opti_Zn_index
          nonUMP_zoneGroup_size = TP.nonUMP_zoneGroup_size                       
          ump_zoneGroup_size = TP.ump_zoneGroup_size
      except: 
          opti_Zn_index= [0,0,0,0,0,2,0,0,0,0]
          nonUMP_zoneGroup_size = 5                       
          ump_zoneGroup_size = 1

      zn_group_by_len_all_hd = {}
      zn_group_by_copy_option_all_hd = {}
      single_zone= {} 

      for groupSize in range(nonUMP_zoneGroup_size+1): # for predefined zone, it is all head
         zn_group_by_len_all_hd[groupSize] = [] #{0: [], 1: [], 2: [], 3: [], 4: [], 5: []}

      for hd in range(self.dut.imaxHead):
          single_zone [hd] =[] 

      try: 
          optiZones_tbl=  self.dut.dblData.Tables('OPTI_ZN_SUMMARY').tableDataObj()
          printDbgMsg("optiZones_tbl %s" % len(optiZones_tbl))  
      except:
          CRdOptiZoneInsertion(self.dut,{}).run()
          optiZones_tbl=  self.dut.dblData.Tables('OPTI_ZN_SUMMARY').tableDataObj()
          printDbgMsg("optiZones_tbl2 %s" % len(optiZones_tbl))

      Head_input = []
      Opti_Zn_input = []
      ZG_Start_input = []
      ZG_End_input = []
       
      for tableofs in range(len(optiZones_tbl)):

          Head = int(optiZones_tbl[ tableofs ] ['HD_PHYS_PSN'])
          Opti_Zn = int(optiZones_tbl[ tableofs ] ['OPTI_ZONE'])
          ZG_Start = int(optiZones_tbl[ tableofs ] ['ZN_GRP_START'])
          ZG_End = int(optiZones_tbl[ tableofs ] ['ZN_GRP_END'])
          Copy_Option= int(optiZones_tbl[ tableofs ] ['ZN_COPY_OPTION'])
          printDbgMsg("H[%d] Opti_Zn[%d] Start_Zn[%d] End_Zn[%d] Copy_Option[0x%x]" % (Head, Opti_Zn, ZG_Start, ZG_End,Copy_Option))

          Head_input.append(Head)
          Opti_Zn_input.append(Opti_Zn)
          ZG_Start_input.append(ZG_Start)
          ZG_End_input.append(ZG_End)
      printDbgMsg("Head_input %s" % str(Head_input))
      printDbgMsg("Opti_Zn_input %s" % str(Opti_Zn_input))
      printDbgMsg("ZG_Start_input %s" % str(ZG_Start_input))
      printDbgMsg("ZG_End_input %s" % str(ZG_End_input))
      for i in range(50-len(Head_input)):
         Head_input.append(-1)
         Opti_Zn_input.append(-1)
         ZG_Start_input.append(-1)
         ZG_End_input.append(-1)
          
      T256_Para['OPTI_HEADS'] = Head_input
      T256_Para['OPTI_ZONES'] = Opti_Zn_input
      T256_Para['START_ZONES'] = ZG_Start_input
      T256_Para['END_ZONES'] = ZG_End_input
      T256_Para['CWORD1'] |= 0x1000 # Run all heads all zones with zone copy in a single T256 call. 
      printDbgMsg("T256_Para %s" % str(T256_Para))  
      oProc.St(T256_Para)
              
              
