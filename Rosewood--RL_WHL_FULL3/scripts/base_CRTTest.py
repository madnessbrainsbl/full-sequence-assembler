#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: base Serial Port CAL states
#
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/11/24 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_CRTTest.py $
# $Revision: #8 $
# $DateTime: 2016/11/24 18:38:07 $
# $Author: yihua.jiang $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_CRTTest.py#8 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
from State import CState
import MessageHandler as objMsg
from PowerControl import objPwrCtrl
import ScrCmds


#----------------------------------------------------------------------------------------------------------
class CReadScreenSOVA(CState):
   """
      Description: Class that will perform spt based read screens
      Base: N/A
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   if testSwitch.SMR:
      def updateT250Params(self, tst_prm):
         if testSwitch.FE_0124358_391186_T250_ZONE_SWEEP_RETRIES:
            tst_prm['ZONE_POSITION'] = 198    #Start at the end of the zone before sweeping zone if necessary
         if self.params.get('ODD_ZONES', 0): # Odd Zones only and UMP
            tst_prm.update({'TEST_ZONES' : list( set(range(1, self.dut.numZones, 2))  | \
               set(self.oRdWr.oUtility.getUMPZone(range(self.dut.numZones))) ) })
         objMsg.printMsg("tst_prm['TEST_ZONES'] %s" % str(tst_prm['TEST_ZONES']))
         if self.params.get('OTF', 0): #OTF mode instead of SOVA
            tst_prm.update({'MODES' : ['SECTOR']})
         if self.params.get('RST_RD_OFFSET', 0): #Reset read offset to on track read
            tst_prm.update({'CWORD2' : (tst_prm['CWORD2'][0] | 0x0800, )})
         if self.params.get('BAND_WRITE', 0): # Band writing instead on track write read
            tst_prm.update({'CWORD2' : (tst_prm['CWORD2'][0] | 0x0100, ) })
            tst_prm.update({'MINIMUM' :  -10}) #fail safe
         if self.params.get('SQZ_WRITE', 0): # SQZ writing instead on track write read
            tst_prm.update({'NUM_SQZ_WRITES' : 1 }) #num of adjacent track write
         if self.params.get('MIN_SOVA', 0): # Minimum sova to override
            tst_prm['MINIMUM'] = self.params.get('MIN_SOVA', 0)
         tst_prm.update({'MAX_ERR_RATE' : self.params.get('MAX_ERR_RATE', -90)}) #default -90
         return tst_prm

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from RdWr import CRdWrScreen
      from dbLogUtilities import DBLogCheck
      dblchk = DBLogCheck(self.dut)
      self.oRdWr = CRdWrScreen()
      RetryEC = [10482, 10522]
      passEC = [0, 10632]
      modulationEc = [10632, 10522, 10427]
      modulationEcHdList = [0]
      modulationEcZnList = [30]
      listmeanBER = list()
      failmarginal = 0

      
      prm_dict = {
         'READ_SCRN2A' : self.oRdWr.oUtility.copy(TP.prm_quickSER_250_2A),
         'READ_SCRN2C' : self.oRdWr.oUtility.copy(TP.prm_quickSER_250_TCC),
         'READ_SCRN2C_SMR' : self.oRdWr.oUtility.copy(TP.prm_quickSER_250_TCC),
         'READ_SCRN2D' : self.oRdWr.oUtility.copy(TP.prm_quickSER_250_TCC),
         'READ_SCRN2H' : self.oRdWr.oUtility.copy(TP.prm_quickSER_250_TCC_2),
      }
      modulation_Check_dict = {
         'READ_SCRN2A' : 0,
         'READ_SCRN2C' : 0,
         'READ_SCRN2C_SMR' : 0,
         'READ_SCRN2D' : 0,
         'READ_SCRN2H' : 1,
      }
      BERCheck_dict = {
         'READ_SCRN2A' : 0,
         'READ_SCRN2C' : 0,
         'READ_SCRN2C_SMR' : 0,
         'READ_SCRN2D' : 0,
         'READ_SCRN2H' : 1,
      }

      depMREStatCheck_dict = {
         'READ_SCRN2A' : 0,
         'READ_SCRN2C' : 0,
         'READ_SCRN2C_SMR' : 1,
         'READ_SCRN2D' : 0,
         'READ_SCRN2H' : 1,
      }
      redoMeasureErrRate_dict = {
         'READ_SCRN2A' : 0,
         'READ_SCRN2C' : 0,
         'READ_SCRN2C_SMR' : 0,
         'READ_SCRN2D' : 0,
         'READ_SCRN2H' : 2,
      }

      screen_Raw_tc1_dict = {
         'READ_SCRN2A' : 0,
         'READ_SCRN2C' : 0,
         'READ_SCRN2C_SMR' : 0,
         'READ_SCRN2D' : 0,
         'READ_SCRN2H' : testSwitch.YARRAR and (self.dut.HGA_SUPPLIER=='RHO'),
      }
      inPrm = prm_dict[self.dut.nextState]

      if self.dut.nextState in ['READ_SCRN2D'] and len(self.dut.TccChgByBerHeadList) == 0:
         objMsg.printMsg("******Both head TCC no change in TCC_BY_BER, skip ReadScrn2D******")
         return

      if testSwitch.SMR:
         inPrm = self.updateT250Params(inPrm) #update the test param according user inputs
      SetFailSafe()

      self.oRdWr.St({'test_num':172, 'prm_name':'Display CERT Temperature', 'CWORD1': 18,'timeout': 100})
      self.oRdWr.St({'test_num':172, 'prm_name':'Display Drive Temperature','CWORD1': 17,'timeout': 100})
      self.oRdWr.St({'test_num':172, 'prm_name':'Display Drive TCC',        'CWORD1': 10,'spc_id': inPrm['spc_id']})

      if testSwitch.SKIPZONE and not testSwitch.virtualRun:
         from RdWr import CSkipZnFile
         self.dut.skipzn = CSkipZnFile().Retrieve_SKIPZN(dumpData = 0)
         objMsg.printMsg("Retrieved Skip Zone: %s" % self.dut.skipzn)

      self.oRdWr.ErrorRateMeasurement(inPrm,flawListMask=0x40,spc_id=inPrm['spc_id'],numRetries=3, retryEC=RetryEC )
      if testSwitch.ENABLE_DATA_COLLECTION_IN_READSCRN2H_FOR_HEAD_INSTABILITY_SCRN:
         if redoMeasureErrRate_dict[self.dut.nextState]:
            for i in range (redoMeasureErrRate_dict[self.dut.nextState]):
               self.oRdWr.ErrorRateMeasurement(inPrm,flawListMask=0x40,spc_id=inPrm['spc_id']+(i+1)*100,numRetries=2)
      ClearFailSafe()
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

      ber_Table = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').chopDbLog('SPC_ID', 'match', str(inPrm['spc_id']))
      List_ber = [[1.0]*self.dut.numZones for hd in xrange(self.dut.imaxHead)]
      List_Ec = [[0]*self.dut.numZones for hd in xrange(self.dut.imaxHead)]
      for i in xrange(len(ber_Table)):
         iZone = int(ber_Table[i]['DATA_ZONE'])
         iHead = int(ber_Table[i]['HD_LGC_PSN'])
         if int(ber_Table[i]['FAIL_CODE']) in passEC:
            List_ber[iHead][iZone]=float(str(ber_Table[i]['RAW_ERROR_RATE']).replace('"',''))
         List_Ec[iHead][iZone] = int(ber_Table[i]['FAIL_CODE'])

      #List_Zn0_Ec = [0 for hd in xrange(self.dut.imaxHead)]
      #for head in xrange(self.dut.imaxHead):
         #if List_Ec[iHead][0] == 10482 and 10482 not in List_Ec[iHead][1:]:
            #List_Zn0_Ec[head] = 10482

      # Fail drive when EC10522 occur at RS2A, RS2C & RS2H:
      if (testSwitch.CHECK_FAILURE_FOR_EC10522_IN_RS2A_2C_2H == 1) and self.dut.nextState not in ['READ_SCRN2D']:
         for head in xrange(self.dut.imaxHead):
            for zone in xrange(self.dut.numZones):
               if List_ber[iHead][iZone] > 0:
                  ScrCmds.raiseException(10522, "%s failed EC10522." % self.dut.nextState)

      if self.dut.nextState in ['READ_SCRN2A']:
         self.dut.List_r2a_ber = List_ber
      elif self.dut.nextState in ['READ_SCRN2C']:
         self.dut.List_r2c_ber = List_ber
      elif self.dut.nextState in ['READ_SCRN2D']:
         self.dut.List_r2d_ber = List_ber

      if BERCheck_dict[self.dut.nextState]:
         skipReadScrn2A = testSwitch.FE_0258915_348429_COMMON_TWO_TEMP_CERT or \
            testSwitch.FE_0251909_480505_NEW_TEMP_PROFILE_FOR_ROOM_TEMP_PRE2
         if not skipReadScrn2A: # R2A is skipped
            try:
               List_r2a_ber = self.dut.List_r2a_ber
            except:
               self.dut.stateTransitionEvent = 'restartAtState'
               self.dut.nextState = 'READ_SCRN2A'
               return
         try:
            List_r2_ber = self.dut.List_r2_ber
         except:
            from RdWr import CRdScrn2File
            oRdScrn2File = CRdScrn2File()
            List_r2_ber  = oRdScrn2File.Retrieve_RD_SCRN2_RAW()

         List_r2h_ber = List_ber

         ber_limit = inPrm.get('SER_raw_BER_limit')
         degradation_limit = abs(inPrm.get('max_diff'))
         num_failed_zone_limit = inPrm.get('checkDeltaBER_num_failing_zones')

         if testSwitch.FE_305538_P_T250_COMBO_SCREEN and self.dut.nextState in ('READ_SCRN2H',):
            from dbLogUtilities import DBLogCheck
            dblchk = DBLogCheck(self.dut)
            dblchk.checkComboScreen(TP.T250_RdScrn2H_SqzWrite_Spec)
            sqzFail = dblchk.failHead

         objMsg.printMsg("*** %s vs R2_FNC2 Delta Spec Overpower %4.2f, Degradation %4.2f***" % (self.dut.nextState,TP.delta_R2H_bigger_than_R2,degradation_limit))
         objMsg.printMsg("*** %s Zone BER Spec %4.2f and %d violation per Head allowed***" % (self.dut.nextState,ber_limit, num_failed_zone_limit ))
         for head in xrange(self.dut.imaxHead):
            AllReadscrn2zone_BER = 0
            AllReadscrn2Hzone_BER = 0
            AllReadscrn2Azone_BER = 0
            validZone = 0
            num_failed_zone = 0
            num_wr_rd_failed_zone = 0

            for zone in xrange(self.dut.numZones):
               if testSwitch.FE_0257006_348085_EXCLUDE_UMP_FROM_TCC_BY_BER and zone in TP.UMP_ZONE[self.dut.numZones]:
                  List_r2h_ber[head][zone] = 0
               objMsg.printMsg('Hd=%-2d  Zone=%-2d  %s=%4.2f  RDSCRN2=%4.2f'%(head, zone, self.dut.nextState, List_r2h_ber[head][zone],List_r2_ber[head][zone]))
               if testSwitch.SKIPZONE:
                  if (head,zone) in self.dut.skipzn:
                     objMsg.printMsg("head %s zone %s is skip zone." %(head, zone))
                     continue

               if skipReadScrn2A: # R2A is skipped
                  if List_r2_ber[head][zone] < 0 and  List_r2h_ber[head][zone] < 0 :
                     validZone +=1
                     AllReadscrn2zone_BER += List_r2_ber[head][zone]
                     AllReadscrn2Hzone_BER += List_r2h_ber[head][zone]
                     if List_r2h_ber[head][zone] > ber_limit:
                        num_failed_zone += 1
               else:
                  if List_r2_ber[head][zone] < 0 and  List_r2h_ber[head][zone] < 0 and  List_r2a_ber[head][zone] < 0:
                     validZone +=1
                     AllReadscrn2zone_BER += List_r2_ber[head][zone]
                     AllReadscrn2Hzone_BER += List_r2h_ber[head][zone]
                     AllReadscrn2Azone_BER += List_r2a_ber[head][zone]
                     if List_r2h_ber[head][zone] > ber_limit:
                        num_failed_zone += 1
               if List_r2h_ber[head][zone] > 0 and (zone != 0 or List_Ec[head][0]!= 10482):
                  num_wr_rd_failed_zone += 1

            if validZone > 0:
               ReadScrn2Ave = AllReadscrn2zone_BER / validZone
               ReadScrn2HAve = AllReadscrn2Hzone_BER / validZone
               listmeanBER.append(ReadScrn2HAve)
               ReadScrn2AAve = AllReadscrn2Azone_BER / validZone
               DELTA_RAW  = ReadScrn2HAve - ReadScrn2Ave
               DELTA_RAW_1 = ReadScrn2AAve - ReadScrn2Ave
               objMsg.printMsg('Hd=%-2d  TotalValidZone=%-2d   %s_Avg=%4.2f   RDSCRN2_Avg=%4.2f  DELTA=%4.2f'%(head, validZone,self.dut.nextState, ReadScrn2HAve, ReadScrn2Ave, DELTA_RAW))

               if num_failed_zone > num_failed_zone_limit:
                  ScrCmds.raiseException(10632, "%s failed min BER spec." % self.dut.nextState)
               if DELTA_RAW < 0 and (abs(DELTA_RAW) >= TP.delta_R2H_bigger_than_R2) and DELTA_RAW_1 > 0 and not testSwitch.FE_0283799_454766_P_DTH_ADJ_ON_THE_FLY:
                  ScrCmds.raiseException(48448, "%s failed BER overpower spec." % self.dut.nextState)
               if (DELTA_RAW > degradation_limit):
                  ScrCmds.raiseException(14574, "%s failed BER degradation spec." % self.dut.nextState)
               if (num_wr_rd_failed_zone):
                  ScrCmds.raiseException(10632, "%s failed min BER spec." % self.dut.nextState)
               if testSwitch.FE_305538_P_T250_COMBO_SCREEN and self.dut.nextState in ('READ_SCRN2H',) and self.dut.HGA_SUPPLIER == 'RHO':
                  # sqzFail = dblchk.failHead
                  deltaSpec,Avg2HSpec = TP.T250_RdScrn2H_Combo_Spec['RdScrn2H_FNC2_Delta'], TP.T250_RdScrn2H_Combo_Spec['RdScrn2H_Avg']
                  objMsg.printMsg("Hd=%d, sqzFail=%s, deltaSpec=%4.2f, Avg2HSpec=%4.2f, DELTA_RAW=%4.2f, ReadScrn2HAve=%4.2f" % (head, str(head in sqzFail), deltaSpec, Avg2HSpec, DELTA_RAW, ReadScrn2HAve))
                  if head in sqzFail and DELTA_RAW >= deltaSpec and ReadScrn2HAve >= Avg2HSpec:
                     if testSwitch.ENABLE_ON_THE_FLY_DOWNGRADE and self.downGradeOnFly(1, 11154):
                        objMsg.printMsg('Failed for BER combo spec, downgrade to %s as %s' % (self.dut.BG, self.dut.partNum))
                     else:
                        ScrCmds.raiseException(11154, "Failed BER Combo: SqzWriteFail=%d, DeltaBER=%4.2f, AvgRdScrn2H=%4.2f, " % (sqzFail[str(head)], DELTA_RAW, ReadScrn2HAve))

                   #if self.dut.partNum[-3:] not in TP.RetailTabList:
                   #  ScrCmds.raiseException(10632, "%s failed min BER spec." % self.dut.nextState)
                   #else:
                   #  self.dut.raiseSerialformat = 1
               if abs(DELTA_RAW) >= TP.delta_R2H_bigger_than_R2 and testSwitch.FE_0283799_454766_P_DTH_ADJ_ON_THE_FLY:
                  if DELTA_RAW < 0: # 2H is better
                     objMsg.printMsg("WARNING: %s  BER overpower spec." % self.dut.nextState)
                     newWHdTh = TP.tcc_DH_dict_178 ['WRITER_HEATER']['dTh']
                     newRHdTh = TP.tcc_DH_dict_178 ['READER_HEATER']['dTh']
                     oldWHdTh = TP.tcc_DH_dict_178 ['WRITER_HEATER']['dTh']
                     oldRHdTh = TP.tcc_DH_dict_178 ['READER_HEATER']['dTh']
                     dThComp = 0
                     if abs(ReadScrn2HAve) > TP.dThAdjSpec['R2H_max_ber']:
                        dThComp = TP.dThAdjSpec['Add_dth_low']
                        if abs(DELTA_RAW) > TP.dThAdjSpec['R2H_R2C_delta_ber']:
                           dThComp = TP.dThAdjSpec['Add_dth_high']
                        newWHdTh = TP.tcc_DH_dict_178 ['WRITER_HEATER']['dTh'] - dThComp/(TP.dThAdjSpec['Temp_refer'] - TP.tcc_DH_dict_178 ['WRITER_HEATER']['HOT_TEMP_DTH'])
                        newRHdTh = TP.tcc_DH_dict_178 ['READER_HEATER']['dTh'] - dThComp/(TP.dThAdjSpec['Temp_refer'] - TP.tcc_DH_dict_178 ['READER_HEATER']['HOT_TEMP_DTH'])

                        #Report temperature correction coefficients
                        if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT == 1:
                           from AFH_Screens_DH import CAFH_Screens
                        else:
                           from AFH_Screens_T135 import CAFH_Screens
                        oAFH_Screens  = CAFH_Screens()
                        oAFH_Screens.St({'test_num':172, 'prm_name': 'Retrieve TC Coefficient', "CWORD1" : (10), 'spc_id': 1111, })

                        #read back TCC1 from drive
                        tcc1_List_R = [0,]*self.dut.imaxHead
                        tcc1_List_W = [0,]*self.dut.imaxHead
                        RetrieveTcCoeff_prm = TP.Retrieve_TC_Coeff_Prm_172.copy()
                        RetrieveTcCoeff_prm['spc_id'] = 999
                        oAFH_Screens.St(RetrieveTcCoeff_prm)
                        if not testSwitch.extern.FE_0157745_387179_AFH_TCS_WARP:
                           P172_AFH_DH_TC_COEF_Tbl = self.dut.dblData.Tables('P172_AFH_DH_TC_COEF').chopDbLog('SPC_ID', 'match',str(RetrieveTcCoeff_prm['spc_id']))
                        else:
                           P172_AFH_DH_TC_COEF_Tbl = self.dut.dblData.Tables('P172_AFH_DH_TC_COEF_2').chopDbLog('SPC_ID', 'match',str(RetrieveTcCoeff_prm['spc_id']))
                        for entry in P172_AFH_DH_TC_COEF_Tbl:
                           if entry.get('ACTIVE_HEATER') == 'R':
                              tcc1_List_R[int(entry.get('HD_LGC_PSN'))] = float(entry.get('THERMAL_CLR_COEF1'))
                           else:
                              tcc1_List_W[int(entry.get('HD_LGC_PSN'))] = float(entry.get('THERMAL_CLR_COEF1'))
                        # Save AFH TCC1 and TCC2 to RAP
                        if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT == 1:
                           from RAP import ClassRAP
                           objRAP = ClassRAP()
                           if testSwitch.FE_0169232_341036_ENABLE_AFH_TGT_CLR_CANON_PARAMS == 1:
                              from AFH_canonParams import *
                              tcc_DH_values = getTCS_values()
                           else:
                              tcc_DH_values = TP.tcc_DH_values
                           oldWHdTh = tcc_DH_values["WRITER_HEATER"]['dTh']
                           oldRHdTh = tcc_DH_values["READER_HEATER"]['dTh']
                           tcc_DH_values["WRITER_HEATER"]['dTh'] = newWHdTh
                           tcc_DH_values["READER_HEATER"]['dTh'] = newRHdTh
                           if not testSwitch.extern.FE_0157745_387179_AFH_TCS_WARP:
                              objRAP.SaveTCC_toRAP( head, tcc1_List_W[head], tcc_DH_values["WRITER_HEATER"]['TCS2'], "WRITER_HEATER", tcc_DH_values )
                              objRAP.SaveTCC_toRAP( head, tcc1_List_R[head], tcc_DH_values["READER_HEATER"]['TCS2'], "READER_HEATER", tcc_DH_values )
                           else:
                              objRAP.SaveTCC_toRAP( head, tcc1_List_W[head], tcc_DH_values["WRITER_HEATER"]['TCS2'], "WRITER_HEATER", tcc_DH_values, TP.TCS_WARP_ZONES.keys() )
                              objRAP.SaveTCC_toRAP( head, tcc1_List_R[head], tcc_DH_values["READER_HEATER"]['TCS2'], "READER_HEATER", tcc_DH_values, TP.TCS_WARP_ZONES.keys() )

                        oAFH_Screens.mFSO.saveRAPtoFLASH()
                        oAFH_Screens.St({'test_num':172, 'prm_name': 'Retrieve TC Coefficient', "CWORD1" : (10), 'spc_id': 2222, })

                     self.dut.dblData.Tables('P_DTH_ADDER').addRecord({
                        'HD_PHYS_PSN'            : head,
                        'READ_SCRN2_AVG'         : ReadScrn2Ave,
                        'READ_SCRN2H_AVG'        : ReadScrn2HAve,
                        'DELTA_BER'              : DELTA_RAW,
                        'DTH_COMPENSATION'       : dThComp,
                        'WH_DTH_OLD'             : oldWHdTh,
                        'RH_DTH_OLD'             : oldRHdTh,
                        'WH_DTH_NEW'             : newWHdTh,
                        'RH_DTH_NEW'             : newRHdTh,
                        })
         try:
            objMsg.printMsg("==========================================")
            objMsg.printMsg(" <<< DTH COMPENSATION ADDER ALGORITHM>>>")
            objMsg.printMsg("==========================================")
            objMsg.printMsg("SPECB = %.3f" % TP.dThAdjSpec['R2H_max_ber'])
            objMsg.printMsg("SPECD = %.3f" % TP.dThAdjSpec['R2H_R2C_delta_ber'])
            objMsg.printMsg("SPECH = %.3f" % TP.delta_R2H_R2_by_partnum)
            objMsg.printDblogBin(self.dut.dblData.Tables('P_DTH_ADDER'))
         except:
            pass

      if depMREStatCheck_dict[self.dut.nextState]:
         from RdWr import CMrResFile
         #=== Perform MR resistance delta check
         if testSwitch.FE_0173493_347506_USE_TEST321  and testSwitch.extern.SFT_TEST_0321:
            oMrRes = CMrResFile(TP.get_MR_Resistance_321, TP.mrDeltaLim)
         else:
            oMrRes = CMrResFile(TP.get_MR_Values_186, TP.mrDeltaLim)
         oMrRes.diffMRValues()

      if screen_Raw_tc1_dict[self.dut.nextState]:
         raw_tc1_col = []
         for row in self.dut.dblData.Tables('P_AFH_DH_MEASURED_TCC').tableDataObj():
            raw_tc1_col.append(float(row['RAW_TCC_1']))
         if len(raw_tc1_col) > 0:
            if max(raw_tc1_col) > 0.8:
               ScrCmds.raiseException(14722, "RAW_TCC_1 > 0.8 spec")

      if testSwitch.FE_0340631_305538_P_RDSCRN2H_COMBO_SCREEN:
         if ( dblchk.checkComboScreen(TP.T250_ReadScreen_Spec) == FAIL ):
            if testSwitch.ENABLE_ON_THE_FLY_DOWNGRADE and self.downGradeOnFly(1, 14929):
               objMsg.printMsg('Failed for ReadScrn2H screening, downgrade to %s as %s' % (self.dut.BG, self.dut.partNum))
            else:
               ScrCmds.raiseException(14929, 'Failed for ReadScrn2H screening @ Head : %s' % str(dblchk.failHead))
      if testSwitch.FE_0368834_505898_P_MARGINAL_SOVA_HEAD_INSTABILITY_SCRN and not testSwitch.virtualRun:
         listMeanHMSbyHead = eval(self.dut.driveattr['HMSC_AVG'])
         for head in xrange(self.dut.imaxHead):
            if TP.MarginalSovaMeanHMS_CAP and (listmeanBER[head] >= ((-0.055*listMeanHMSbyHead[head]) - 2.27))  and listMeanHMSbyHead[head]<=TP.MarginalSovaMeanHMS_CAP:
               objMsg.printMsg('head %d' % head) 
               objMsg.printMsg('listmeanBER = %f >= (-0.055*%f - 2.27)' %  (listmeanBER[head],listMeanHMSbyHead[head]))
               objMsg.printMsg('listMeanHMSbyHead = %f <= %f' %  (listMeanHMSbyHead[head],TP.MarginalSovaMeanHMS_CAP))
               failmarginal = 1
         if failmarginal:
             if testSwitch.ENABLE_ON_THE_FLY_DOWNGRADE and self.downGradeOnFly(1, 10560):
                 objMsg.printMsg('Failed for Marginal Sova Instability screening, downgrade to %s as %s' % (self.dut.BG, self.dut.partNum))
             else:
                 ScrCmds.raiseException(10560, 'Failed for Marginal Sova Instability screening @ Head : %s' % str(head))
      if self.dut.nextState in ['READ_SCRN2C'] and TP.T250_RdScrn2C_SovaDgrade_Spec:
         objMsg.printMsg("READ_SCRN2CCombo_Spec1")
         if (dblchk.checkComboScreen(TP.T250_RdScrn2C_SovaDgrade_Spec) == FAIL):
             if testSwitch.ENABLE_ON_THE_FLY_DOWNGRADE and self.downGradeOnFly(1, 10560):
                objMsg.printMsg('Failed for Sova degraded screening, downgrade to %s as %s' % (self.dut.BG, self.dut.partNum))
             else:
                 ScrCmds.raiseException(10560, 'Failed for Sova Degraded screening @ Head : %s' % str(dblchk.failHead))           

#----------------------------------------------------------------------------------------------------------
class CAGB_zoneRemap(CState):
   """
   Zone Remap Configuration
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      """
      P172_CAP_TABLE:
       ADDRESS  0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F            ASCII
       Original is:
          00E0 ff fe 00 00 ff ff ff ff ff ff ff ff ff ff ff ff ................
       After remap is:
          00E0 ff fe 00 00 ff ff fe ff ff ff ff ff 16 ff ff ff ................
                                  |  |  |           |
       F3 Offset:               230 231 232        236
       SF3 CAP_WORD Offset:     0x73    0x74       0x76

      uint32 ZoneRemapTotalCyl; //Total numbers of tracks to remap.?  // bytes 232-235
      uint16 VariableGuardBandControl = 0xFFFE (clear bit 0 to enable AGB) // byte 230-231
      uint8 ZoneRemapDestination = 22 (remap to after zone 22) // byte 236

      When AGB is enabled, remap is automatically enabled and the value in ZoneRemapTotalCyl will be ignored.
      """

      if testSwitch.ADAPTIVE_GUARD_BAND:
         from Process import CProcess
         self.oProc = CProcess()
         TgtZoneForRemap = self.dut.numZones - 2
         objMsg.printMsg("Z0 Remap Set remap Destination to after Zone %d" % TgtZoneForRemap )

         prm1 = TP.prm_setCAPRemapZone_178
         cap_word_value =  (TgtZoneForRemap) | (0xFF<<8)
         prm1["CAP_WORD"] = TP.ZN_REMAP_DEST_CAP_OFS,cap_word_value,0xFF
         if testSwitch.virtualRun: objMsg.printMsg("prm1 = %s"%(str(prm1)))
         self.oProc.St(prm1)

         prm2 = TP.prm_enableAGB_178
         #prm2["CAP_WORD"] = 0x0073,0xFFFE,0xFFFF # To enable AGB
         if testSwitch.virtualRun: objMsg.printMsg("prm2 = %s" % (str(prm2)))
         self.oProc.St(prm2)

         self.oProc.St(TP.prm_dispCAP)
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)         
      else:
         objMsg.printMsg("AGB flag disabled, skip state.")


#----------------------------------------------------------------------------------------------------------
class CInitASDDefectList(CState):
   """
      Description: Class that will perform SMART reset and generic customer prep.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from serialScreen import sptDiagCmds
      import sptCmds

      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      oSerial = sptDiagCmds()
      oSerial.enableDiags()

      # Additional cmd for ASD drvs, added by SWLeow
      oSerial.gotoLevel('N')
      sptCmds.sendDiagCmd("M6,1000,1EAF", timeout = 500, printResult=True)
      sptCmds.sendDiagCmd("M6,1008,DEAD", timeout = 500, printResult=True)
      sptCmds.sendDiagCmd("M6,100E,1000", timeout = 500, printResult=True)
      sptCmds.sendDiagCmd("M6,618,8000", timeout = 500, printResult=True)
      sptCmds.sendDiagCmd("M6,1000,11", timeout = 500, printResult=True)
      sptCmds.sendDiagCmd("M6,100E,0", timeout = 500, printResult=True)
      sptCmds.sendDiagCmd("M6,618,8000", timeout = 500, printResult=True)
      sptCmds.sendDiagCmd("M6,1000,C", timeout = 500, printResult=True)
      sptCmds.sendDiagCmd("M6,618,8000", timeout = 500, printResult=True)
      ScriptPause(10)
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
         # end of additional cmd
         ### oSerial.enableDiags() ## may be we need this


#----------------------------------------------------------------------------------------------------------
class CInitASDforHybrid(CState):
   """
      Description: Class that will perform clear NAND for Rosewood hybrid
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from serialScreen import sptDiagCmds
      import sptCmds

      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      oSerial = sptDiagCmds()
      oSerial.enableDiags()

      oSerial.gotoLevel('N')
      sptCmds.sendDiagCmd("B0", timeout = 500, printResult=True)
      sptCmds.sendDiagCmd("E0,1,32", timeout = 500, printResult=True)
      objMsg.printMsg("Pause for 10s...")
      ScriptPause(10)
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)


#----------------------------------------------------------------------------------------------------------
class CInitCONGEN(CState):
   """
      Description: Class that will perform congen initialization.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from serialScreen import sptDiagCmds
      import sptCmds

      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      oSerial = sptDiagCmds()
      oSerial.enableDiags()

      if testSwitch.FE_0000000_305538_HYBRID_DRIVE: # for hybrid only
         objMsg.printMsg  ("\nClear and Init NAND: O>I\n")
         sptCmds.gotoLevel('O')
         sptCmds.sendDiagCmd('I',timeout = 600, printResult = True)

      if not ( testSwitch.ROSEWOOD7 or testSwitch.M11P or testSwitch.M11P_BRING_UP ): # temporary disable due to cmd not supported yet
         oSerial.gotoLevel('5')
         sptCmds.sendDiagCmd("DEEEE", timeout = 500, printResult=True)

      oSerial.gotoLevel('T')
      sptCmds.sendDiagCmd("F,,22", timeout = 500, printResult=True)

      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)


#----------------------------------------------------------------------------------------------------------
class CSerialBER(CState):
   """
      Description: Class that will collect user level BER.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      self.dut = dut
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------

   def run(self):
      if not testSwitch.RUN_F3_BER:
         return

      from serialScreen import sptDiagCmds
      import sptCmds

      self.RdOnly = self.params.get('READ_ONLY', 0)
      self.AllTrks = self.params.get('WHOLE_SURFACE', 0)
      if self.RdOnly: mode = 'Read Only'
      else: mode = 'Wrt then read'

      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      oSerial = sptDiagCmds()
      oSerial.enableDiags()
      oSerial.syncBaudRate(Baud38400)

      znStart = 0
      testBand = 0x200
      #ZonesPerHd = 0x18
      if self.AllTrks: length = 'whole surface'
      else: length = '200h trks'

      objMsg.printMsg("** Collect Zone BER START (%s) for %s**" % (mode, length))
      numCyls,zones = oSerial.getZoneInfo()
      ZonesPerHd = len(zones[0])
      objMsg.printMsg("MaxCyls of hd = %s" % (str(numCyls)))
      objMsg.printMsg("zones= %s" % str(zones))
      objMsg.printMsg("Num user zones = %d" % (ZonesPerHd-1))

      #oSerial.gotoLevel('2')
      sptCmds.gotoLevel('2')
      #oSerial.gotoLevel('2')
      sptCmds.gotoLevel('2')
      #oSerial.sendDiagCmd("A2", timeout = 500, raiseException = 0)
      sptCmds.sendDiagCmd("A2", timeout = 500, raiseException = 0)
      #oSerial.sendDiagCmd("A2", timeout = 500, raiseException = 0)
      sptCmds.sendDiagCmd("A2", timeout = 500, raiseException = 0)
      accumulator = oSerial.PBlock(CTRL_W)
      accumulator = oSerial.PBlock(CTRL_W)

      for hd in range(self.dut.imaxHead) :
         for znStart in range (ZonesPerHd):
            try:
               testTrk = zones[hd][znStart]
               #objMsg.printMsg("Perform Write and Read from Trk %x to %x, Hd %d" % (testTrk, testTrk+testBand, hd))
               '''
               oSerial.sendDiagCmd("S%x,%d" %(testTrk,hd), timeout = 500, raiseException = 0)
               oSerial.sendDiagCmd("S%x,%d" %(testTrk,hd), timeout = 500, raiseException = 0)
               oSerial.sendDiagCmd("L1,%x" % testBand, timeout = 500, raiseException = 0)
               oSerial.sendDiagCmd("L1,%x" % testBand, timeout = 500, raiseException = 0)
               oSerial.sendDiagCmd("W", timeout = 500, raiseException = 0)
               oSerial.sendDiagCmd("W", timeout = 500, raiseException = 0)
               oSerial.sendDiagCmd("S%x,%d" %(testTrk,hd), timeout = 500, raiseException = 0)
               oSerial.sendDiagCmd("S%x,%d" %(testTrk,hd), timeout = 500, raiseException = 0)
               oSerial.sendDiagCmd("L1,%x" % testBand, timeout = 500, raiseException = 0)
               oSerial.sendDiagCmd("L1,%x" % testBand, timeout = 500, raiseException = 0)
               oSerial.sendDiagCmd("R", timeout = 500, raiseException = 0)
               oSerial.sendDiagCmd("R", timeout = 500, raiseException = 0)
               '''
               if not self.RdOnly:
                  objMsg.printMsg("Perform Wrt and Rd from Trk %d to %d, Hd %d" % (testTrk, testTrk+testBand, hd))
                  sptCmds.sendDiagCmd("S%x,%d" %(testTrk,hd), timeout = 500, raiseException = 0)
                  sptCmds.sendDiagCmd("S%x,%d" %(testTrk,hd), timeout = 500, raiseException = 0)
                  sptCmds.sendDiagCmd("L1,%x" % testBand, timeout = 500, raiseException = 0)
                  sptCmds.sendDiagCmd("L1,%x" % testBand, timeout = 500, raiseException = 0)
                  sptCmds.sendDiagCmd("W", timeout = 500, raiseException = 0)
                  sptCmds.sendDiagCmd("W", timeout = 500, raiseException = 0)
               else: objMsg.printMsg("Perform Rd from Trk %d to %d, Hd %d" % (testTrk, testTrk+testBand, hd))
               sptCmds.sendDiagCmd("S%x,%d" %(testTrk,hd), timeout = 500, raiseException = 0)
               sptCmds.sendDiagCmd("S%x,%d" %(testTrk,hd), timeout = 500, raiseException = 0)
               sptCmds.sendDiagCmd("L1,%x" % testBand, timeout = 500, raiseException = 0)
               sptCmds.sendDiagCmd("L1,%x" % testBand, timeout = 500, raiseException = 0)
               sptCmds.sendDiagCmd("R", timeout = 500, raiseException = 0)
               sptCmds.sendDiagCmd("R", timeout = 500, raiseException = 0)
            except:
               pass

      oSerial.getZoneBERData( tLevel = 0x32, readRetry = 0x63, lowerBaudRate = True, spc_id = 2 )
      objMsg.printMsg("** Collect Zone BER END **")

      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

###########################################################################################################
class CCheckHDA_FW(CState):
   """
      Check HDA, F3, servo and IV code against DCM requirement
      Prerequisite: F3 code download
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      objMsg.printMsg("Checking HDA, f3, servo and IV code versions")
      from CustomCfg import CCustomCfg
      CustConfig = CCustomCfg()

      CustConfig.getDriveConfigAttributes(partNum=self.dut.partNum, failInvalidDCM = True)
      CustConfig.autoValidateHDAFw('HDA_FW')
      
###########################################################################################################
class CMediaCacheVerify(CState):
   """
      Check the media cache size for SBS only for 13426 improvement
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if not self.dut.BG in ['SBS']:
         return
         
      from FSO import CFSO
      self.oFSO = CFSO()
      
      self.oFSO.readMCandUMPInfo()
      MCSize = int(self.dut.dblData.Tables('P172_MISC_INFO').chopDbLog('DESCRIPTION', 'match', 'MediaCacheSizePerDrive')[-1].get('VALUE'))
      
      if MCSize > 150:
         objMsg.printMsg('SBS drive with media cache %dG. Change to 15G'%(MCSize/10))
      else:
         objMsg.printMsg('SBS drive with media cache %dG.'%(MCSize/10))
         return
      self.oFSO.St({'test_num': 178, 'prm_name': 'prm_prog_mc_178', 'CWORD1':0x0220, 'MEDIA_CACHE_SIZE': 150})
      self.oFSO.saveRAPtoFLASH()
      objPwrCtrl.powerCycle(useESlip=1)
      
      self.oFSO.readMCandUMPInfo()
