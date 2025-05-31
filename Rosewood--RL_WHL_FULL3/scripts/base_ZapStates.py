#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: base zap states
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/12/29 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_ZapStates.py $
# $Revision: #16 $
# $DateTime: 2016/12/29 22:40:52 $
# $Author: yihua.jiang $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_ZapStates.py#16 $
# Level: 2
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
import types
from Servo import CServoOpti
import Utility
from State import CState
import MessageHandler as objMsg
from FSO import CFSO
from Drive import objDut
from PowerControl import objPwrCtrl

if testSwitch.SPLIT_BASE_SERIAL_TEST_FOR_CM_LA_REDUCTION:
   from Opti_Read import CRdOpti
   from base_GPLists import CInitializeFlawLists
else:
   from base_SerialTest import CRdOpti
   from base_SerialTest import CInitializeFlawLists

###########################################################################################################
###########################################################################################################
class CZap(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      """
         Run the ZAP test.
      """
      from MediaScan import CUserFlaw
      from Process import CProcess
      oProc = CProcess()
      self.oSrvOpti = CServoOpti()
      oUtility = Utility.CUtility()
      if testSwitch.ZFS == 1:
         from Servo import CServoScreen
         oSvoScrn = CServoScreen()

      if (testSwitch.MR_RESISTANCE_MONITOR and 0):
         try:
            CProcess().St(TP.PresetAGC_InitPrm_186_break)
         except:
            pass

      if testSwitch.FE_SGP_81592_REZAP_ON_MAXRRO_EXCEED_LIMIT:
         from Servo import CServoFunc
         import types
         Cyl_Is_Logical =  self.params.get("CYL_IS_LOGICAL", 1)
         oSrvFunc = CServoFunc()

         T33_Prm = TP.pesMeasurePrm_33.copy()
         cword1 = T33_Prm.get('CWORD1',0)

         if type(cword1) in [types.ListType,types.TupleType]:
            cword1 = cword1[0]
         if Cyl_Is_Logical:
            T33_Prm.update({'CWORD1':  cword1 | 0x8000}) # CYL_IS_LOGICAL == TRUE.

         CFSO().getZoneTable()
         objMsg.printMsg("MaxTrack")
         objMsg.printMsg(self.dut.maxTrack)
         iTrack = min(self.dut.maxTrack)- 0x100
         #T33_Prm.update({'END_CYL':  oUtil.ReturnTestCylWord(iTrack)})
         T33_Prm.update({'spc_id':  100})

      if testSwitch.ZFS == 0:    # T275 handles shock sensor enabling/disabling so no need to do it here
         #Disable Shock Sensor before ZAP
         if testSwitch.FE_0110811_320363_DISABLE_SHOCK_SENSOR_IN_ZAP:
            SF3ShockSensorString = getattr(TP, 'Disable_SF3_ShockSensor', None)
            if SF3ShockSensorString != None:
               objMsg.printMsg("Disable Shock Sensor before ZAP \n")
               self.oSrvOpti.St(SF3ShockSensorString)

      if testSwitch.ZFS:
         import types
         prmZap = oUtility.copy(TP.zfs_275)
         prmZap['timeout'] = 172800
         if type(prmZap['CWORD1']) in [types.ListType, types.TupleType]:
            prmZap['CWORD1'] = prmZap['CWORD1'][0]
         prmZap['ZAP_SPAN'] = 5                            # 5 = full surface zap
         prmZap['THRESHOLD2'] = 30                         # for TNU
         if self.dut.BG in ['SBS'] and len(self.dut.rerunReason) > 1 and self.dut.rerunReason[1] in ['ZAP', 'RZAP', 'SPF_REZAP']:
            prmZap['THRESHOLD2'] = 38
         prmZap['THRESHOLD'] = 30  #21                          # for TNU
         prmZap['FILTERS'] = 165                           # for TNU
         prmZap['FILTERS_2'] = 1575                        # for TNU
         prmZap['CWORD1'] |= 0x0400                        # enable ZFS
         prmZap['CWORD1'] &= 0xFFDF                        # disable read ZAP
         if testSwitch.extern.FE_0334551_357001_SEC_SAT_SCREEN:
            prmZap['SEC_CZAP_SAT_LIMIT'] =   287                # 7% High Saturation RRO screen by counter Limit
            prmZap['CZAP_SAT_COUNT_SCREEN'] = 20              # 20 counts for retry/skip
         if self.dut.BG not in ['SBS'] and testSwitch.extern.FE_0349976_340866_ADD_AND_CERT_PROBATION_DEFECT_SLIST:
            if testSwitch.IS_2D_DRV == 1:
               prmZap['COMPARE_VALUE'] = 328             # 8% zap compensation table data
               prmZap['SECTORS_TO_CHK'] = 2              # 2 sector tag probation skip track?            
               prmZap['PERCENT_LIMIT2'] = 70             # start scan from 70% of MaxCyl to MaxCyl             
            else:
               prmZap['COMPARE_VALUE'] = 4095              # open the limit of zap compensation table data
               prmZap['SECTORS_TO_CHK'] = 375              # open the limit of sector tag probation skip track
               prmZap['PERCENT_LIMIT2'] = 70               # start scan from 70% of MaxCyl to MaxCyl 
         if self.dut.BG not in ['SBS'] and testSwitch.extern.FE_0353653_340866_HIGH_ZAP_PWR_DETECTION:
            prmZap['MAX_POWER'] = 2300                # in Q4 format, 2000 correspond to 32000 respect to Sum(abs(Zap))
      else:
         prmZap = oUtility.copy(TP.zapByZone_175)

      if testSwitch.FE_0159091_345963_P_DISABLE_ZBZ_BY_CHANGE_CWORD2 and not testSwitch.ZFS:
         if self.dut.HDSTR_PROC == 'Y':
            if type(prmZap['CWORD2']) in [types.ListType, types.TupleType]:
               prmZap['CWORD2'] = prmZap['CWORD2'][0]
            prmZap['CWORD2'] &= 0xFBFF

      if testSwitch.auditTest ==0:
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

         if testSwitch.FE_0130200_231166_SAVE_ZAP_INCR_STATE_FOR_PLR:
            testRange = range(self.dut.objData.get('ZAP_SAVE_HEAD',  -1) + 1,  self.dut.imaxHead)
         else:
            testRange = range(self.dut.imaxHead)
         if testSwitch.ZFS == 1 and not testSwitch.FE_0335299_454766_P_ENABLE_HIGH_RPM_ZAP:
            oSvoScrn.clearServoErrCntrs()   # Clear servo error counters

         if testSwitch.FE_0365343_518226_SPF_REZAP_BY_HEAD and self.dut.nextState == 'SPF_REZAP' and int(self.dut.driveattr['SPF_CUR_HEAD']) >= 0:
            st(86, {'CWORD2': 0x01, 'TEST_HEAD': self.dut.driveattr['SPF_CUR_HEAD']})
            st(86, {'CWORD2': 0x04, 'TEST_HEAD': self.dut.driveattr['SPF_CUR_HEAD']})
            st(86, {'CWORD2': 0x08, 'TEST_HEAD': self.dut.driveattr['SPF_CUR_HEAD']})  
            st(86, {'CWORD2': 0x02, 'TEST_HEAD': self.dut.driveattr['SPF_CUR_HEAD']})                   
            #self.oUserFlaw = CUserFlaw()
            #self.oUserFlaw.initSFT()
            testRange = (self.dut.driveattr['SPF_CUR_HEAD'],)
            objMsg.printMsg("SPF_REZAP testRange %s" % str(testRange))
         elif self.params.get('Init_FlawList', testSwitch.INITIALIZE_FLAW_LIST_BEFORE_FULL_ZAP):
            CInitializeFlawLists(self.dut,{}).run()

         if testSwitch.UPDATE_SYMBOL_ENTRY_239_BIT14_IN_ZAP:
            self.oSrvOpti.setServoSymbolData('LVFF_ENABLE_SYMBOL_OFFSET', (1 << 14), 0x4000 )   # set servo symbol 239, bit 14

         if testSwitch.ZFS == 1:
            # Set to allow access to FAFH Zones at beginning of STATE
            if testSwitch.IS_FAFH:
               CServoOpti().St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value
               CServoOpti().St(TP.AllowFAFH_AccessBit_178) # Allow FAFH access for servo test
               CServoOpti().St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value

            prmZap['CWORD1'] = 0x6014 # from 0x6814
            #if testSwitch.FE_0235011_509591_P_DISABLE_ZFS_ZAP_BY_ZONE:
               #prmZap['CWORD1'] &= ~(1<<13)
            self.oSrvOpti.zap(prmZap)   # enable ZBZ, intit/save ZBZ pc file, calculate/save TFs
#         if testSwitch.TOPAZ_DRZAP_ENABLE and (self.dut.BG in ['SBS'] or testSwitch.IS_2D_DRV):
         if testSwitch.TOPAZ_DRZAP_ENABLE:
            objMsg.printMsg("DrZAP & TOPAZ Enabled")
         else:
            objMsg.printMsg("DrZAP & TOPAZ Disabled")
         for self.head in testRange:
#            if testSwitch.TOPAZ_DRZAP_ENABLE and (self.dut.BG in ['SBS'] or testSwitch.IS_2D_DRV):
            if testSwitch.TOPAZ_DRZAP_ENABLE :
               prmZap['HEAD_CLAMP'] = 4000
               if 'CWORD2' not in prmZap:
                  prmZap['CWORD2'] = 0x0300
               else:
                  prmZap['CWORD2'] |= 0x0300                        # Turn On Topaz and DRZap
               if 'RD_REVS' not in prmZap:
                  prmZap['RD_REVS'] = 1
               if 'SET_OCLIM' not in prmZap:
                  prmZap['SET_OCLIM'] = 573
            prmZap['HEAD_RANGE'] = (self.head << 8) + self.head
            if testSwitch.FE_0238515_081592_SET_ZAP_SEC_CYL_TO_20PCT_OF_MAX_TRK:
               sec_cyl = int(0.2*self.dut.maxTrack[self.head])
               objMsg.printMsg("Update SEC_CYL to %d" % sec_cyl)
               prmZap.update({'SEC_CYL':  oUtility.ReturnTestCylWord(sec_cyl)})

            if testSwitch.FE_SGP_81592_PWRCYCLE_RETRY_WHEN_T175_REPORT_EC11087_IN_ZAP:
               T175Retry = 1
               while 1:
                  try:
                     CProcess().St(TP.zapPrm_175_zapOff)
                     self.oSrvOpti.zap(prmZap)   # ZAP is done here!
                     break
                  except ScriptTestFailure, (failureData): #catch EC11087, retry w pwr cycle
                     if failureData[0][2] in [11087] and T175Retry > 0:
                        objMsg.printMsg("EC:11087 - pwrcyc n rerun\n")
                        objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1) #perform power cycle before rerun
                        T175Retry = T175Retry - 1
                     else: raise
            else:
               if testSwitch.ZFS == 0:                # Use T175 for ZAP
                  CProcess().St(TP.zapPrm_175_zapOff)
                  self.oSrvOpti.zap(prmZap)           # ZAP is done here!
               else:
                  if testSwitch.ZFS_LEGACY_MODE == 1: # This method of ZAP uses T275 and does not write the flawscan pattern
                     #prmZap.pop('WREVENTRK',None)
                     #prmZap.pop('WRODDTRK',None)
                     prmZap['CWORD1'] = 0xF0E9 # from F8E9 for write zap
    #                 if testSwitch.TOPAZ_DRZAP_ENABLE and (self.dut.BG in ['SBS'] or testSwitch.IS_2D_DRV):
                     if testSwitch.TOPAZ_DRZAP_ENABLE:
                        prmZap['REVS'] = 1 # for write zap
                     else:
                        prmZap['REVS'] = 2 # for write zap
                     #if testSwitch.FE_0274441_210191_P_MAKARAPLUS_INCREASE_WRITE_ZAP_ITERS:
                        #prmZap['ITERATIONS'] = 4
                     #if testSwitch.FE_0235011_509591_P_DISABLE_ZFS_ZAP_BY_ZONE:
                        #prmZap['CWORD1'] &= ~(1<<13)
                     if testSwitch.FE_0335299_454766_P_ENABLE_HIGH_RPM_ZAP:
                        prmZap.update({'DISABLE_HARMONICS' : (273,0),})
                        prmZap.update({'M0_FREQ_RANGE'   : (32,32),})
                        CProcess().St({'test_num':1,'prm_name':'Load ZEST Tbl','CWORD1':8})
                     if testSwitch.M11P_BRING_UP or testSwitch.M11P:
                        prmZap['ITERATIONS'] = 2
                     self.oSrvOpti.zap(prmZap)        # Write ZAP - all tracks
                     if self.dut.BG in ['SBS'] and self.dut.objSeq.SuprsDblObject.has_key('P275_ZAP_SUMMARY'):
                        sumTrkCnt = 0
                        for entry in self.dut.objSeq.SuprsDblObject['P275_ZAP_SUMMARY']:
                           sumTrkCnt += int(entry['OSE_SMPATT_TRK_CNT'])
                        if sumTrkCnt > 1700:
                           self.dut.driveattr['PROC_CTRL19'] = '2'
                              
                  else: # Run ZFS. This method of ZAP uses T275 and includes writing the flawscan pattern
                     prmZap.update({'WREVENTRK'   : (),})
                     prmZap['CWORD1'] = 0xFCE9
                     #if testSwitch.FE_0235011_509591_P_DISABLE_ZFS_ZAP_BY_ZONE:
                        #prmZap['CWORD1'] &= ~(1<<13)
                     self.oSrvOpti.zap(prmZap)        # Write ZAP - even tracks

                     prmZap.pop('WREVENTRK',None)
                     prmZap.update({'WRODDTRK'   : (),})
                     prmZap['CWORD1'] = 0xFCE9
                     #if testSwitch.FE_0235011_509591_P_DISABLE_ZFS_ZAP_BY_ZONE:
                        #prmZap['CWORD1'] &= ~(1<<13)
                     if testSwitch.FE_0335299_454766_P_ENABLE_HIGH_RPM_ZAP:  #
                        prmZap.update({'DISABLE_HARMONICS' : (273,0),})
                        prmZap.update({'M0_FREQ_RANGE'   : (32,32),})
                        CProcess().St({'test_num':1,'prm_name':'Load ZEST Tbl','CWORD1':8})

                     self.oSrvOpti.zap(prmZap)   # Write ZAP - odd tracks

 #                 if not (testSwitch.TOPAZ_DRZAP_ENABLE and (self.dut.BG in ['SBS'] or testSwitch.IS_2D_DRV)):
                  if not testSwitch.TOPAZ_DRZAP_ENABLE :
                     #prmZap.pop('WRODDTRK',None)
                     prmZap['CWORD1'] = 0xF0EA # from F8EA for read zap
                     prmZap['REVS'] = 1 # for read zap
                  #if testSwitch.FE_0235011_509591_P_DISABLE_ZFS_ZAP_BY_ZONE:
                     #prmZap['CWORD1'] &= ~(1<<13)
                  #for item in TP.zfs_275_read_only:
                     #prmZap[item] = TP.zfs_275_read_only[item]
                     self.oSrvOpti.zap(prmZap)   # Read ZAP

            if testSwitch.FE_SGP_81592_REZAP_ON_MAXRRO_EXCEED_LIMIT:
               maxRRO = 0
               iTrack = self.dut.maxTrack[self.head]- 1
               T33_Prm.update({'TEST_HEAD': self.head})
               T33_Prm.update({'END_CYL':  oUtility.ReturnTestCylWord(iTrack)})
               oSrvFunc.St(T33_Prm)
               pesTable = self.dut.dblData.Tables('P033_PES_HD2').chopDbLog('SPC_ID', 'match', str(T33_Prm['spc_id']))
               for pesData in pesTable:
                  if int(pesData['HD_LGC_PSN']) == self.head and float(pesData['RRO']) > maxRRO:
                     maxRRO = float(pesData['RRO'])
               objMsg.printMsg("Head %d MaxRRO %4f" % (self.head, maxRRO))
               if not testSwitch.FE_SGP_505235_MOVING_REZAP_TO_INDIVIDUAL_TEST and (maxRRO >= TP.MAX_RRO):
                  objMsg.printMsg("Max RRO over spec %f, Trigger reZAP" % TP.MAX_RRO)
                  CProcess().St(TP.zapPrm_175_zapOff)
                  self.oSrvOpti.zap(prmZap)

            if testSwitch.FE_0130200_231166_SAVE_ZAP_INCR_STATE_FOR_PLR:
               self.dut.objData['ZAP_SAVE_HEAD']  = self.head
               objMsg.printMsg("Debug: Hd Saved %d" % self.dut.objData['ZAP_SAVE_HEAD'])

            if self.dut.BG not in ['SBS'] and testSwitch.FE_0118779_357260_SAVE_SLIST_IN_ZAP and testSwitch.extern.FE_0349976_340866_ADD_AND_CERT_PROBATION_DEFECT_SLIST:
               self.objFs = CUserFlaw()
               self.objFs.repServoFlaws_T126(spcId = 25)                       # Report servo flaw table
               self.objFs.St(TP.prm_126_svo_scan_probation_write)    # scan probation list

         # Set to dis-allow access to FAFH Zones at end of STATE
         if testSwitch.IS_FAFH:
            CServoOpti().St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value
            CServoOpti().St(TP.DisallowFAFH_AccessBit_178) # Dis-allow FAFH access after completing servo test
            CServoOpti().St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value

         if testSwitch.UPDATE_SYMBOL_ENTRY_239_BIT14_IN_ZAP:
            self.oSrvOpti.setServoSymbolData('LVFF_ENABLE_SYMBOL_OFFSET', 0x0000, 0x4000 )   # clear servo symbol 239, bit 14


         if testSwitch.ZFS == 1:
            oSvoScrn.dumpServoErrCntrs(spcId=1090)  # Dump servo error counters
         if testSwitch.FE_0118779_357260_SAVE_SLIST_IN_ZAP:
            self.objFs = CUserFlaw()
            self.objFs.repServoFlaws_T126(spcId = 275)    # Report servo flaw table
            if self.dut.BG in ['SBS']:
               self.recoverSerialFMTFlashLED()

         if testSwitch.FE_0335299_454766_P_ENABLE_HIGH_RPM_ZAP:
            #self.objFs.St({'test_num':149,'prm_name':"SaveSFlawsToPC",'timeout': 600, 'spc_id': 1, 'CWORD2': 4})
            self.objFs.St(TP.prm_149_ASFL2PC)  #Same as Above Line

      elif testSwitch.auditTest ==1:
         self.auditTestZap(prmZap)                       # Call with ZBZ parms, but disable ZBZ in the method, since only a small band of tracks in audit test

      if testSwitch.FE_0125416_357915_ENABLE_ATS_CALIBRATION: # Anticipatory Track Seek calibration
         self.oSrvOpti.St(TP.prm_194_ATS)

      if testSwitch.ServoAccousticMode== 1:
         self.oSrvOpti.accousticMode(TP.setAccousticSeek)
         self.oSrvOpti.accousticMode(TP.ReadAccoustic)
         self.oSrvOpti.accousticMode(TP.SaveAccoustic)

      #Enable if disabled in SetupProc... only performs actions for programs with ACFF enabled in SAP
      self.oSrvOpti.setZonedACFF(enable = True)

      if testSwitch.FE_0155184_345963_P_DISABLE_ZAP_OFF_AFTER_COMPLETED_ZAP:
         self.dut.zapDone = 1

      if testSwitch.FE_0130200_231166_SAVE_ZAP_INCR_STATE_FOR_PLR:#clear saved hd after zap done
         self.dut.objData['ZAP_SAVE_HEAD']  = -1

      if testSwitch.SCOPY_TARGET:
         self.objFs.St(TP.Incoherent_WIRRO_Meas_H10_257)    # T257 after Zap

      if not testSwitch.WA_0125708_426568_FULLY_DISABLE_LVFF:
         # if LVFF is disabled and not fully disabled this will enable it based upon PCBA part nubmer
         if testSwitch.WA_0129386_426568_DISABLE_LVFF_AFTER_ZAP_BASED_ON_PCBA_NUM :
            self.oSrvOpti.PCBAsetting(TP.pcba_nums,'LVFF')
         else :
            self.oSrvOpti.setLVFF(enable = True)
      if testSwitch.WA_0256539_480505_SKDC_M10P_BRING_UP_DEBUG_OPTION:
         self.oSrvOpti.St(TP.CRRO_IRRO_Prm_46) #CRRO,IRRO
         self.oSrvOpti.St(TP.CRRO_IRRO_RealMode_Prm_46) #CRRO,IRRO
      if testSwitch.FE_0123391_357915_DISABLE_ADAPTIVE_ANTI_NOTCH_UNTIL_AFTER_ZAP:
         self.oSrvOpti.setAdaptiveAntiNotch(enable = True)
      if testSwitch.ZFS == 0:    # T275 handles shock sensor enabling/disabling so no need to do it here
         #Enable Shock Sensor - ZAP is done
         if testSwitch.FE_0110811_320363_DISABLE_SHOCK_SENSOR_IN_ZAP:
            SF3ShockSensorString = getattr(TP, 'Enable_SF3_ShockSensor', None)
            if SF3ShockSensorString != None:
               objMsg.printMsg("Enable Shock Sensor after ZAP \n")
               self.oSrvOpti.St(SF3ShockSensorString)

      if testSwitch.FE_0157865_409401_P_TEMP_CHECKING_IN_ZAP_AND_FLAWSCAN_FOR_GHG_FLOW and self.dut.HDSTR_PROC == 'Y':
         oProc.St({'test_num':172, 'prm_name':'HDA TEMP', 'timeout': 200, 'CWORD1': (17,), 'REPORT_OPTION':1, 'DATA_ID': 10001})


      if (testSwitch.MR_RESISTANCE_MONITOR and 0):
         try:
             CProcess().St(TP.PresetAGC_InitPrm_186_break)
         except:
             pass

      if self.dut.HDSTR_PROC == 'Y':
         objMsg.printMsg("HDSTR TESTING ENABLED!!!  DO NOT POWER CYCLE THE DRIVE!!!!!!!!!")
      else:
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
   def recoverSerialFMTFlashLED(self):
      chkFlag = 1
      if ConfigVars[CN].get('ChkStateDepend', 1):
         if self.dut.statesExec[self.dut.nextOper].count('ZAP') + self.dut.statesExec[self.dut.nextOper].count('RZAP') + self.dut.statesExec[self.dut.nextOper].count('SPF_REZAP') >= 2:
            chkFlag = 0
      else:
         if self.dut.statesExec[self.dut.nextOper].count('ZAP') + self.dut.statesExec[self.dut.nextOper].count('RZAP') + self.dut.statesExec[self.dut.nextOper].count('SPF_REZAP') >= 1:
            chkFlag = 0
            
      if self.dut.objSeq.SuprsDblObject.has_key('P126_SRVO_FLAW_REP') and chkFlag:
         import ScrCmds
         objMsg.printMsg('maxTrack: %s'%self.dut.maxTrack)
         # Trigger reZAP if P126_SRVO_FLAW_REP CYLINDER > max user cyl to recover Serial FMT flash LED(7453)
         for entry in self.dut.objSeq.SuprsDblObject['P126_SRVO_FLAW_REP']:
            if int(entry['CYLINDER']) > self.dut.maxTrack[int(entry['HD_LGC_PSN'])]:
               objMsg.printMsg('Trigger reZAP to recover potential flash LED in Serial FMT')
               ScrCmds.raiseException(10657, 'Trigger reZAP to recover potential flash LED in Serial FMT')
   def auditTestZap(self,inPrm):
      """ run ZAP on audit test heads and zone groups determined in RAP file/auditTestRAPDict
      """
      self.oUtility = Utility.CUtility()
      zapParm = inPrm.copy()
      objMsg.printMsg("                       AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA                         ",objMsg.CMessLvl.IMPORTANT)
      objMsg.printMsg("              ******** AUDIT TEST: HEADS AND TRACK BANDS SET IN RAP TABLE ********             ",objMsg.CMessLvl.IMPORTANT)
      zapParm['CWORD2'] = 0x0000 # turn off ZBZ (bit 10) for small band of tracks
      objMsg.printMsg("AUDIT TEST: ZAP- turn off ZBZ for small band of tracks",objMsg.CMessLvl.IMPORTANT)
      for head, zoneGroups in self.dut.auditTestRAPDict.items():
         hdMask = (head<<8) + head
         zapParm["HEAD_RANGE"] = (hdMask)
         for band in zoneGroups:
            startCyl = band[0]
            endCyl = band[1]

            if startCyl == 0:
               zapParm["timeout"] = 11024 + 2*(endCyl-startCyl) #Increase to handle LUL zone
            else:
               zapParm["timeout"] = 1024 + 2*(endCyl-startCyl)

            upperWord,lowerWord = self.oUtility.ReturnTestCylWord(startCyl)
            zapParm["START_CYL"] = upperWord,lowerWord
            upperWord,lowerWord = self.oUtility.ReturnTestCylWord(endCyl)
            zapParm["END_CYL"] = upperWord,lowerWord

            #If this range contains SEC_CYL cylinder or is less than then let's set it
            if (zapParm.get('SEC_CYL', False)) and (endCyl > self.oUtility.reverseTestCylWord(zapParm.get('SEC_CYL', 0))):
               if startCyl > self.oUtility.reverseTestCylWord(zapParm['SEC_CYL']): #if it is in the range then leave it
                  zapParm['SEC_CYL'] = self.oUtility.ReturnTestCylWord(startCyl)

            self.oSrvOpti.zap(zapParm)


###########################################################################################################
###########################################################################################################
class CReZap(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      """
         Run the ReZAP test.
      """
      from Process import CProcess
      from Servo import CServoFunc
      import types
      from Exceptions import CDblogDataMissing

      Check_Pes_After_Rezap = self.params.get("CHECK_PES_AFTER_REZAP", 0)
      Cyl_Is_Logical =  self.params.get("CYL_IS_LOGICAL", 1)
      oSrvFunc = CServoFunc()
      self.oSrvOpti = CServoOpti()
      oUtility = Utility.CUtility()

      # get zone info
      CFSO().getZoneTable()
      objMsg.printMsg("MaxTrack %s" % str(self.dut.maxTrack))

      # check if forced reZAP
      forceZap = False
      if testSwitch.FE_SGP_505235_ENABLE_REZAP_ATTRIBUTE or testSwitch.FE_SGP_517205_TIMEOUT_REZAP_ATTRIBUTE:
         if self.dut.rezapAttr & 0xff00:
            forceZap = True

      # set reZAP parameters
      if testSwitch.ZFS:
         import types
         prmZap = oUtility.copy(TP.zfs_275)
         prmZap['timeout'] = 172800
         if type(prmZap['CWORD1']) in [types.ListType, types.TupleType]:
            prmZap['CWORD1'] = prmZap['CWORD1'][0]
         prmZap['ZAP_SPAN'] = 5                            # 5 = full surface zap
         #prmZap['CWORD1'] |= 0x0400                        # enable ZFS
         #prmZap['CWORD1'] &= 0xFFDF                        # disable read ZAP
      elif forceZap:
         prmZap = oUtility.copy(TP.zapByZone_175_forced)
      else:
         prmZap = oUtility.copy(TP.zapByZone_175)

      if testSwitch.FE_0159091_345963_P_DISABLE_ZBZ_BY_CHANGE_CWORD2 and not testSwitch.ZFS:
         if self.dut.HDSTR_PROC == 'Y':
            if type(prmZap['CWORD2']) in [types.ListType, types.TupleType]:
               prmZap['CWORD2'] = prmZap['CWORD2'][0]
            prmZap['CWORD2'] &= 0xFBFF

      # set T33 parameters
      T33_Prm = TP.pesMeasurePrm_33.copy()
      cword1 = T33_Prm.get('CWORD1',0)
      if type(cword1) in [types.ListType,types.TupleType]:
         cword1 = cword1[0]
      if Cyl_Is_Logical:
         T33_Prm.update({'CWORD1':  cword1 | 0x8000}) # CYL_IS_LOGICAL == TRUE.

      # init flaw list
      if self.params.get('Init_FlawList', testSwitch.INITIALIZE_FLAW_LIST_BEFORE_FULL_ZAP):
         CInitializeFlawLists(self.dut,{}).run()

      if not forceZap:
         try:
            pesTable = self.dut.dblData.Tables('P033_PES_HD2').tableDataObj()
         except CDblogDataMissing:
            objMsg.printMsg("No P033_PES_HD2 table found. Check PES before reZAP")
            for self.head in range(self.dut.imaxHead):
               # check PES before reZAP
               iTrack = self.dut.maxTrack[self.head] - 1
               T33_Prm.update({'TEST_HEAD': self.head})
               T33_Prm.update({'END_CYL':  oUtility.ReturnTestCylWord(iTrack)})
               T33_Prm.update({'spc_id':  200})
               oSrvFunc.St(T33_Prm)
            pesTable = self.dut.dblData.Tables('P033_PES_HD2').tableDataObj()

      reZaped = False
      for self.head in range(self.dut.imaxHead):
         if forceZap:
            # check if requested to forced re-ZAP
            if self.dut.rezapAttr & (1 << self.head + 8):
               objMsg.printMsg("Force reZAP for head %d" % self.head)
            else:
               continue
         else:
            maxRRO = 0
            for pesData in pesTable:
               if int(pesData['HD_LGC_PSN']) == self.head and float(pesData['RRO']) > maxRRO:
                  maxRRO = float(pesData['RRO'])
            objMsg.printMsg("Head %d MaxRRO %4f" % (self.head, maxRRO))

            if maxRRO >= TP.MAX_RRO:
               objMsg.printMsg("Max RRO over spec %f, triggered reZAP" % TP.MAX_RRO)
            else:
               continue

         # reZAP
         reZaped = True
         prmZap['HEAD_RANGE'] = (self.head << 8) + self.head
         if testSwitch.FE_0238515_081592_SET_ZAP_SEC_CYL_TO_20PCT_OF_MAX_TRK:
            sec_cyl = int(0.2*self.dut.maxTrack[self.head])
            objMsg.printMsg("Update SEC_CYL to %d" % sec_cyl)
            prmZap.update({'SEC_CYL':  oUtility.ReturnTestCylWord(sec_cyl)})

         CProcess().St(TP.zapPrm_175_zapOff)
         self.oSrvOpti.zap(prmZap)
         if testSwitch.FE_SGP_505235_ENABLE_REZAP_ATTRIBUTE  or testSwitch.FE_SGP_517205_TIMEOUT_REZAP_ATTRIBUTE:
            self.dut.rezapAttr |= 1 << self.head

         # check PES after reZAP
         if Check_Pes_After_Rezap:
            iTrack = self.dut.maxTrack[self.head] - 1
            T33_Prm.update({'TEST_HEAD': self.head})
            T33_Prm.update({'END_CYL':  oUtility.ReturnTestCylWord(iTrack)})
            T33_Prm.update({'spc_id':  201})
            oSrvFunc.St(T33_Prm)

      if not reZaped:
         objMsg.printMsg("ReZAP is never triggered",objMsg.CMessLvl.DEBUG)


###########################################################################################################
###########################################################################################################
class CVbarZap(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      """
         Run the ZAP test on VBAR test cyl.
      """
      if testSwitch.CONDITIONAL_RUN_HMS:
         objMsg.printMsg("currentState=%s skipHMS=%s" % (self.dut.currentState, self.dut.skipHMS))
         if (self.dut.currentState in ['VBAR_TPI_ZAP'] and self.dut.skipHMS):
            objMsg.printMsg("Skipping HMS related states")
            return
      oUtility = Utility.CUtility()
      oSrvOpti = CServoOpti()
      oFSO = CFSO()
      oFSO.getZoneTable(newTable = 1, delTables = 1, supressOutput = 0)

      if testSwitch.SPLIT_VBAR_FOR_CM_LA_REDUCTION:
         from VBAR_Zones import CVbarTestZones
      else:
         from VBAR import CVbarTestZones
      oVbarTestZones = CVbarTestZones()
      testZones = oVbarTestZones.getTestZones()

      if testSwitch.ZFS:
         VbarZap = oUtility.copy(TP.zfs_275)
         VbarZap['ZAP_SPAN'] = 3                            # 3 = VBAR zap
         VbarZap['REVS'] = 4
         VbarZap['ITERATIONS'] = 2
         VbarZap['ZONE_POSITION'] = TP.VBAR_ZONE_POS
         for head in range(self.dut.imaxHead):
            hdMsk = (head << 8) + head
            VbarZap["HEAD_RANGE"] = (hdMsk)
#            numZones = self.dut.numZones
#            ZthdOff = (numZones) * head # for zone tbl indexing
            if self.params.get('WP_ZONES_ONLY', 0):
               #VbarZap['ZONE_MASK'] = oUtility.ReturnTestCylWord(oUtility.setZoneMask(testZones))
               zone_mask_low = 0
               zone_mask_high = 0
               for zone in testZones:
                 if zone < 32:
                   zone_mask_low |= (1<<zone)
                 else:
                   zone_mask_high |= (1<<(zone-32))
               VbarZap['ZONE_MASK'] = oUtility.ReturnTestCylWord(zone_mask_low)
               VbarZap['ZONE_MASK_EXT'] = oUtility.ReturnTestCylWord(zone_mask_high)
            oSrvOpti.zap(VbarZap)
      else:
         VbarZap = oUtility.copy(TP.zapbasic_175)
         VbarZap['prm_name'] = "Vbar ZAP"
         VbarZap['CWORD2'] = 0x0014
         numTestCyls = int(VbarZap.get('numTestCyls',30))

         zt = self.dut.dblData.Tables('P172_ZONE_TBL').chopDbLog(parseColumn = 'OCCURRENCE', matchStyle = 'max')

         if testSwitch.FE_0125510_209214_ZAP_PARAMETER_CLEANUP_1 and not testSwitch.FE_0132665_209214_ZAP_PARAMETER_CLEANUP_2:
            VbarZap['TRACK_LIMIT'] = 200

         zt = self.dut.dblData.Tables('P172_ZONE_TBL').chopDbLog(parseColumn = 'OCCURRENCE', matchStyle = 'max')

         for head in range(self.dut.imaxHead):
            hdMsk = (head << 8) + head
            VbarZap["HEAD_RANGE"] = (hdMsk)
            numZones = self.dut.numZones
            ZthdOff = (numZones) * head # for zone tbl indexing

            VbarZap['CWORD2'] = VbarZap['CWORD2'] | 0x40
            VbarZap['ZONE_POSITION'] = TP.VBAR_ZONE_POS
            if self.params.get('WP_ZONES_ONLY', 0):
               #VbarZap['ZONE_MASK'] = oUtility.ReturnTestCylWord(oUtility.setZoneMask(testZones))
               zone_mask_low = 0
               zone_mask_high = 0
               for zone in testZones:
                 if zone < 32:
                   zone_mask_low |= (1<<zone)
                 else:
                   zone_mask_high |= (1<<(zone-32))
               VbarZap['ZONE_MASK'] = oUtility.ReturnTestCylWord(zone_mask_low)
               VbarZap['ZONE_MASK_EXT'] = oUtility.ReturnTestCylWord(zone_mask_high)
            oSrvOpti.zap(VbarZap)

###########################################################################################################
###########################################################################################################
class COptiZap(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      """
         Run the ZAP test on Opti test cylinders.
      """
      from Utility import CUtility
      from Process import CProcess
      oUtil = CUtility()
      self.oSrvOpti = CServoOpti()
      zapFromDut = self.params.get('zapFromDut',1)
      oOptiCls = CRdOpti(self.dut, params = {'zapFromDut':zapFromDut})
      objMsg.printMsg('run optiZAP to cover T251(T251 uses a 60 track span (max) including retries) and first T250(READ_SCRN) call in FNC2-note: in first T250, NUM_TRACKS_PER_ZONE(cword1 set BIT 8) s/b <=1/2 what you ZAP here', objMsg.CMessLvl.IMPORTANT)
      # Set to allow access to FAFH Zones at beginning of STATE
      '''
      if testSwitch.IS_FAFH:
         CServoOpti().St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value
         CServoOpti().St(TP.AllowFAFH_AccessBit_178) # Allow FAFH access for servo test
         CServoOpti().St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value
      '''
      if testSwitch.FE_0271421_403980_P_ZONE_COPY_OPTIONS and testSwitch.FE_228371_ZAP_SPECIFIC_ZONE_BF_READ_OPTI:

          optiZones=[]

          try: #tune specific zone if this Opti zn summary table has been generated
              optiZones_tbl=  self.dut.dblData.Tables('OPTI_ZN_GROUP_SUMMARY').tableDataObj()
              objMsg.printMsg("optiZones_tbl %s" % len(optiZones_tbl))

              for tableofs in range(len(optiZones_tbl)):

                  Head = int(optiZones_tbl[ tableofs ] ['HD_PHYS_PSN'])
                  Opti_Zn = int(optiZones_tbl[ tableofs ] ['OPTI_ZONE'])
                  ZG_Start = int(optiZones_tbl[ tableofs ] ['ZN_GRP_START'])
                  ZG_End = int(optiZones_tbl[ tableofs ] ['ZN_GRP_END'])
                  optiZones.append(Opti_Zn)
                  #objMsg.printMsg("H[%d] Opti_Zn[%d] Start_Zn[%d] End_Zn[%d]" % (Head, Opti_Zn, ZG_Start, ZG_End))

          except:pass

      try: optiZapNumTrks = self.params.get('OPTIZAP_TRACK_LIMIT', TP.OPTIZAP_TRACK_LIMIT)
      except: optiZapNumTrks =0x64 #use low word: lower byte =  num trks toward MD(most common),upper byte = num trks away from MD-note: T251 uses a 60 track span (max) including retries.

      if self.params.get('ZONES'):
         minizapZones = eval(str(self.params.get('ZONES'))) #force type of 'ZONES' to str to be eval for simplicity
      else: minizapZones = range(self.dut.numZones)
      if not testSwitch.ZFS:
         modVal = self.oSrvOpti.setZonedACFF(enable = False)
         modLVFF = self.oSrvOpti.setLVFF(enable = False)

      if self.params.get('MINIZAP_OAR', 1):
         if testSwitch.FE_SEGMENTED_BPIC or testSwitch.FE_0304753_348085_P_SEGMENTED_BER:
            #Do zap on OD of the zone 0,1 zone position 0 of every head.
            oOptiCls.optiZAP([0, 1] + TP.minizap_zone_OAR_ELT_SMR, oUtil.convertTestHeadEncodedMask(0xFF),0x001E, 0, consolidateOffLVFF_ACFF = 1)# blm
         elif testSwitch.FE_0304753_348085_P_SEGMENTED_BER:
            #Do zap on OD of the zone 1,4 zone position 0 of every head.
            oOptiCls.optiZAP([1, 4], oUtil.convertTestHeadEncodedMask(0xFF),0x001E, 0, consolidateOffLVFF_ACFF = 1)# blm
         elif testSwitch.Enable_BPIC_ZONE_0_BY_FSOW_AND_SEGMENT:
            #Do zap on OD of the zone 1 zone position 0 of every head. must sync to oar test zone
            oOptiCls.optiZAP([1] + TP.minizap_zone_OAR_ELT_SMR, oUtil.convertTestHeadEncodedMask(0xFF),0x001E, 0, consolidateOffLVFF_ACFF = 1)# blm
            #Do zap on OD of the zone 0 zone position 1 of every head.
            oOptiCls.optiZAP([0], oUtil.convertTestHeadEncodedMask(0xFF),0x001E, 1, consolidateOffLVFF_ACFF = 1)# blm

      zn_pos = self.params.get('ZONE_POS', TP.ZONE_POS)
      if testSwitch.FE_0271421_403980_P_ZONE_COPY_OPTIONS and testSwitch.FE_228371_ZAP_SPECIFIC_ZONE_BF_READ_OPTI:
      # FE_228371_ZAP_SPECIFIC_ZONE_BF_READ_OPTI should be off before squeeze offset interpolation algo decided and full tune needed
          if len(optiZones)>= 1:
            oOptiCls.optiZAP(optiZones, oUtil.convertTestHeadEncodedMask(0xFF),optiZapNumTrks, zn_pos, consolidateOffLVFF_ACFF = 1)# blm
          else:
            oOptiCls.optiZAP(minizapZones, oUtil.convertTestHeadEncodedMask(0xFF),\
               optiZapNumTrks, zn_pos, consolidateOffLVFF_ACFF = 1)# blm
      else:
          oOptiCls.optiZAP(minizapZones, oUtil.convertTestHeadEncodedMask(0xFF),\
            optiZapNumTrks, zn_pos, consolidateOffLVFF_ACFF = 1)# blm

      if not testSwitch.ZFS:
         if modVal: self.oSrvOpti.setZonedACFF(enable = True)
         if modLVFF: self.oSrvOpti.setLVFF(enable = True)

      self.dut.driveattr['OPTI_ZAP_DONE'] = 1

      if testSwitch.FE_SGP_OPTIZAP_ADDED: #turn off the ZAP
         objMsg.printMsg("OPTIZAP: Tuning off ZAP. The state that needs zap will turn it on in those state")
         oSrvOpti = CServoOpti()
         if testSwitch.ENABLE_T175_ZAP_CONTROL:
            oSrvOpti.St(TP.zapPrm_175_zapOff)
         else:
            oSrvOpti.St(TP.setZapOffPrm_011)
            if not testSwitch.BF_0119055_231166_USE_SVO_CMD_ZAP_CTRL:
               oSrvOpti.St({'test_num':178, 'prm_name':'Save SAP in RAM to FLASH', 'CWORD1':0x420})

      # Set to dis-allow access to FAFH Zones at end of STATE
      '''
      if testSwitch.IS_FAFH:
         CServoOpti().St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value
         CServoOpti().St(TP.DisallowFAFH_AccessBit_178) # Dis-allow FAFH access after completing servo test
         CServoOpti().St(TP.ReadFAFH_AllowAccessBit_172) # Check FAFH bit access value
      '''

###########################################################################################################
###########################################################################################################
if testSwitch.FE_0335299_454766_P_ENABLE_HIGH_RPM_ZAP:
   class CDisableSysPrep(CState):
      def __init__(self, dut, params={}):
         self.params = params
         self.dut = dut
         depList = []
         CState.__init__(self, dut, depList)

      def run(self):
         from Process import CProcess
         oProc = CProcess()
         #self.oServo = CServo()
         #self.oServo.St({'test_num':178,'prm_name':"Disable sys area prep","CWORD1":288,"SYS_AREA_PREP_STATE":255})

         ## Init System bit first (For re running of Failure drive ) ##
         CProcess().St({'test_num':178,'prm_name':"Enable sys area prep","CWORD1":288,"SYS_AREA_PREP_STATE":254})

         ## Init System Flaw List ##
         if self.params.get('Init_FlawList', testSwitch.INITIALIZE_FLAW_LIST_BEFORE_FULL_ZAP):
            CInitializeFlawLists(self.dut,{}).run()

         ## Disable System bit ##
         CProcess().St({'test_num':178,'prm_name':"Disable sys area prep","CWORD1":288,"SYS_AREA_PREP_STATE":255})
         #oProc.St({'test_num':178,'prm_name':"Disable sys area prep","CWORD1":288,"SYS_AREA_PREP_STATE":255})


###########################################################################################################
###########################################################################################################
if testSwitch.FE_0335299_454766_P_ENABLE_HIGH_RPM_ZAP:
   class CEnableSysPrep(CState):
      def __init__(self, dut, params={}):
         self.params = params
         self.dut = dut
         depList = []
         CState.__init__(self, dut, depList)

      def run(self):
         from Process import CProcess
         oProc = CProcess()
         #self.oServo = CServo()
         #self.oServo.St({'test_num':178,'prm_name':"Disable sys area prep","CWORD1":288,"SYS_AREA_PREP_STATE":254})
         CProcess().St({'test_num':178,'prm_name':"Enable sys area prep","CWORD1":288,"SYS_AREA_PREP_STATE":254})
         #oProc.St({'test_num':178,'prm_name':"Disable sys area prep","CWORD1":288,"SYS_AREA_PREP_STATE":254})
         CProcess().St({'test_num':126,'prm_name':"PrintSFlaws_1", 'timeout': 600, 'spc_id': 1, 'CWORD1': 2})
         #CProcess().St({'test_num':149,'prm_name':"RetrieveSFlaws",'timeout': 600, 'spc_id': 1, 'CWORD2': 8})
         CProcess().St(TP.prm_149_PC2ASFL)
         CProcess().St({'test_num':126,'prm_name':"PrintSFlaws_2", 'timeout': 600, 'spc_id': 1, 'CWORD1': 2})

###########################################################################################################
###########################################################################################################

