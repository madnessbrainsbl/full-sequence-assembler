#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: base Serial Port CAL states
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
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_CALTest.py $
# $Revision: #5 $
# $DateTime: 2016/12/15 23:34:49 $
# $Author: weichen.lau $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_CALTest.py#5 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
from State import CState
import MessageHandler as objMsg
from PowerControl import objPwrCtrl
from Process import CProcess
import ScrCmds


#----------------------------------------------------------------------------------------------------------
class CAdaptiveUmpZone(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      import Utility
      from FSO import CFSO
      
      self.oFSO = CFSO()
      
      objMsg.printMsg('Default Setting:')
      objMsg.printMsg('TP.numHeads %s' % str(TP.numHeads))
      objMsg.printMsg('self.dut.imaxHead %s' % str(self.dut.imaxHead))
      objMsg.printMsg('self.dut.numZones %s' % str(self.dut.numZones))
      objMsg.printMsg('TP.UMP_ZONE %s' % str(TP.UMP_ZONE))
      objMsg.printMsg('TP.BPIMeasureZone %s' % str(TP.BPIMeasureZone))
      objMsg.printMsg('TP._2DVBAR_ZN %s' % str(TP._2DVBAR_ZN))
      objMsg.printMsg('TP.VBAR_measured_Zones %s' % str(TP.VBAR_measured_Zones))
      objMsg.printMsg('TP.Measured_2D_Zones %s' % str(TP.Measured_2D_Zones))
      objMsg.printMsg('TP.SMRZoneAfterUMP %s' % str(TP.SMRZoneAfterUMP))
      objMsg.printMsg('TP.BERInVBAR_ZN %s' % str(TP.BERInVBAR_ZN))
      objMsg.printMsg('TP.MC_ZONE %s' % str(TP.MC_ZONE))
      objMsg.printMsg('TP.baseVbarTestZones %s' % str(TP.baseVbarTestZones))
      objMsg.printMsg('TP.UMP_ZONE_BY_HEAD %s' % str(TP.UMP_ZONE_BY_HEAD))
      if testSwitch.FE_0385234_356688_P_MULTI_ID_UMP:
         objMsg.printMsg('TP.baseSMRZoneBeforeUMP %s' % str(TP.baseSMRZoneBeforeUMP))

      # On the fly change the number of required UMP zones based on the total number of logical head.
      TP.UMP_ZONE[self.dut.numZones] = TP.UMP_ZONE_BY_HEAD[self.dut.imaxHead][self.dut.numZones]
      ump_start_zone = min(TP.UMP_ZONE[self.dut.numZones])
      num_ump_zone   = len(TP.UMP_ZONE[self.dut.numZones])-1
      TP.numUMP      = len(TP.UMP_ZONE[self.dut.numZones])
      self.oFSO.updateUMP_Zone(ump_start_zone, num_ump_zone)

      objMsg.printMsg('After change (The UMP zones with required logical head):')
      objMsg.printMsg('TP.UMP_ZONE %s' % str(TP.UMP_ZONE))
      objMsg.printMsg('TP.numUMP %s' % str(TP.numUMP))
      objMsg.printMsg('TP.BPIMeasureZone %s' % str(TP.BPIMeasureZone))
      objMsg.printMsg('TP._2DVBAR_ZN %s' % str(TP._2DVBAR_ZN))
      objMsg.printMsg('TP.VBAR_measured_Zones %s' % str(TP.VBAR_measured_Zones))
      objMsg.printMsg('TP.Measured_2D_Zones %s' % str(TP.Measured_2D_Zones))
      objMsg.printMsg('TP.SMRZoneAfterUMP %s' % str(TP.SMRZoneAfterUMP))
      objMsg.printMsg('TP.BERInVBAR_ZN %s' % str(TP.BERInVBAR_ZN))
      objMsg.printMsg('TP.MC_ZONE %s' % str(TP.MC_ZONE))
      objMsg.printMsg('TP.numMC %s' % str(TP.numMC))
      objMsg.printMsg('TP.baseVbarTestZones %s' % str(TP.baseVbarTestZones))
      if testSwitch.FE_0385234_356688_P_MULTI_ID_UMP:
         objMsg.printMsg('TP.baseSMRZoneBeforeUMP %s' % str(TP.baseSMRZoneBeforeUMP))
         
#----------------------------------------------------------------------------------------------------------
class CPVScreen(CState):
   """
      Class made for misc checking after VBAR
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      self.dut = dut
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def adjust_preHeat(self, hd_list=[]):
      if len(hd_list) == 0:
         return
      hd_mask = 0
      for hd in hd_list:
         hd_mask += (1 << hd)
      
      self.oProc = CProcess()
 
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      self.oProc.St({'test_num': 172, 'prm_name':'ClearanceTable before Adjusting PreHeat', 'timeout':1200, 'spc_id': 101, 'CWORD1':5,})
      self.oProc.St({'test_num': 172, 'prm_name':'P172_AFH_WORKING_ADAPTS', 'timeout':1200, 'spc_id': 101, 'CWORD1':4,})

      from AFH import CdPES
      odPES = CdPES(TP.masterHeatPrm_11, TP.defaultOCLIM)

      newpreHeatClr = []
      preHeat_change = -3
      afhZoneTargets_preHeat = TP.afhZoneTargets.copy()

      for zn in range(self.dut.numZones+1):
         new_val =  preHeat_change + TP.afhZoneTargets['TGT_PREWRT_CLR'][zn]
         newpreHeatClr.append(new_val)

      afhZoneTargets_preHeat['TGT_PREWRT_CLR'] = newpreHeatClr

      inPrm = TP.afhTargetClearance_by_zone.copy()
      inPrm.update({'HEAD_RANGE' : hd_mask})

      odPES.setClearanceTargets(inPrm, afhZoneTargets_preHeat, range(0, int(self.dut.numZones + 1)))
      self.oProc.St(TP.activeClearControl_178)

      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      self.oProc.St({'test_num': 172, 'prm_name':'ClearanceTable after Adjusting PreHeat', 'timeout':1200, 'spc_id': 102, 'CWORD1':5,})
      self.oProc.St({'test_num': 172, 'prm_name':'P172_AFH_WORKING_ADAPTS', 'timeout':1200, 'spc_id': 102, 'CWORD1':4,})

   #-------------------------------------------------------------------------------------------------------
   def check_max_trk(self):
      #limit Total physical tracks on drive due to limitation of Super Parity to handle it
      MaxTrk = self.dut.maxTrack
      totaltrk = 0
      for head in xrange (len(MaxTrk)):
          totaltrk += int(MaxTrk[head])
      objMsg.printMsg("check_max_trk total tracks %d SuperparityTrkLimit %d" % (totaltrk,TP.SuperparityTrkLimit ))

      if totaltrk > TP.SuperparityTrkLimit:
         from VBAR import CUtilityWrapper
         if (CUtilityWrapper(self.dut,{}).SearchLowerCapacityPn()!=0):
            self.dut.Waterfall_Req = "REZONE"
            self.dut.driveattr["DNGRADE_ON_FLY"] = '%s_%s_%s'%(self.dut.nextOper, self.dut.partNum[-3:], "SPTRK")
            objMsg.printMsg('DNGRADE_ON_FLY: %s' %(self.dut.driveattr["DNGRADE_ON_FLY"]))
            objMsg.printMsg("check_max_trk Rezone Required. new Waterfall_Req: %s " % (self.dut.Waterfall_Req ))
            ScrCmds.raiseException(48463,"check_max_trk failed")
         else:
            ScrCmds.raiseException(48464,"check_max_trk failed")

   #-------------------------------------------------------------------------------------------------------
   def check_BPIC_FSOW(self):
      BPIC_FSOW_list = {}
      table = self.dut.dblData.Tables('P_VBAR_FORMAT_SUMMARY_ZN0').tableDataObj()
      for row in table:
         BPIC_FSOW_list.setdefault(row['HD_LGC_PSN'], float(row['BPIC_FSOW']))

      for hd,val in BPIC_FSOW_list.items():
         objMsg.printMsg( 'BPIC_FSOW H%d: %1.4f' % (hd,val) )

      for hd in BPIC_FSOW_list:
         if BPIC_FSOW_list[hd] < 0.81:
            ScrCmds.raiseException(14614,"check_BPIC_FSOW failed 0.81 spec")
         elif BPIC_FSOW_list[hd] < 0.84:
            self.downGradeOnFly(1, "FSOWT")
            if(self.dut.partNum[-3:] not in TP.RetailTabList):
               ScrCmds.raiseException(14614,"check_BPIC_FSOW OEM partnumber failed 0.84 spec")

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if not testSwitch.KARNAK:
         self.check_max_trk()

      if not testSwitch.KARNAK and testSwitch.Enable_BPIC_ZONE_0_BY_FSOW_AND_SEGMENT and self.dut.HGA_SUPPLIER in ['TDK', 'HWY']:
         self.check_BPIC_FSOW()


#----------------------------------------------------------------------------------------------------------
class CSegmentedErrRate(CState):
   """
      Class made for calling method that runs test250 for track err rate differential screen
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      self.dut = dut
      depList = []
      self.spc_id_segmented_ber = 22 # SEGMENTED_BER
      self.spc_id_seg_ber_sqz   = 23 # SEG_BER_SQZ
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      WaterfallFlag = 0
      errCodes = TP.stateRerunParams['states'].get(self.dut.nextState, [])
      #=== OAR retry loop
      for retry in xrange(2):
         try:
            objMsg.printMsg("Segmented BER retry: %d" %retry)
            self.runSegmentedErrRate()
            break
         except ScrCmds.CRaiseException, failureData:
            pass

      if testSwitch.FE_0320340_348085_P_OAR_SCREENING_SPEC and self.dut.BG not in ['SBS']:
         from dbLogUtilities import DBLogCheck
         dblchk = DBLogCheck(self.dut)
         if self.dut.nextState is 'SEG_BER_SQZ':
            if dblchk.checkComboScreen(TP.T250_OAR_Screen_Spec) == FAIL:
               if testSwitch.ENABLE_ON_THE_FLY_DOWNGRADE and self.downGradeOnFly(1, 49017):
                  objMsg.printMsg('OAR Error Rate out of spec , downgrade')
               else:
                  ScrCmds.raiseException(49017, 'OAR Error Rate out of spec @ Head : %s' % str(dblchk.failHead))
         elif self.dut.nextState is 'SEGMENTED_BER':
            if dblchk.checkComboScreen(TP.T250_OAR_Screen_Spec_ID) == FAIL:
               if testSwitch.ENABLE_ON_THE_FLY_DOWNGRADE and self.downGradeOnFly(1, 49017):
                  objMsg.printMsg('OAR Error Rate out of spec @ID , downgrade')
               else:
                  ScrCmds.raiseException(49017, 'OAR Error Rate out of spec @ Head : %s' % str(dblchk.failHead))
   #-------------------------------------------------------------------------------------------------------
   def runSegmentedErrRate(self):
      big_diff = False
      fail_minimum = False
      rate = [[[] for zone in xrange(self.dut.numZones)] for hd in xrange(self.dut.imaxHead)]

      # testing
      import types
      segmented_Prm = TP.prm_OAR_ErrRate_250['base'].copy()
      segmented_Prm['ZONE_POSITION'] = 0
      segmented_Prm['NUM_TRACKS_PER_ZONE'] = self.params.get('NUM_TRACKS_PER_ZONE', TP.SEG_BER_NUM_TRACKS_PER_ZONE)
      segmented_Prm['CWORD2'] = 0x450 # Segmented Align
      segmented_Prm['timeout'] = self.dut.imaxHead * 3600
      if type(segmented_Prm['CWORD1']) in [types.TupleType,types.ListType]:
            segmented_Prm['CWORD1'] = segmented_Prm['CWORD1'][0]

      if self.dut.nextState in ['SEGMENTED_BER', 'SEGMENTED_BER2']:
         segmented_Prm['spc_id']              = self.spc_id_segmented_ber # On track
         segmented_Prm['CWORD2'] = segmented_Prm['CWORD2'] | 0x0800 # Reset Rd Offset

      if self.dut.nextState in ['SEG_BER_SQZ', 'SEG_BER_SQZ2']:
         segmented_Prm['spc_id']              = self.spc_id_seg_ber_sqz   #  write
         segmented_Prm['CWORD1'] = segmented_Prm['CWORD1'] | 0x4000 # SQZ WRITE
         segmented_Prm['NUM_SQZ_WRITES'] = 1   #  number of adj track write 

      if self.dut.nextState in ['SEGMENTED_BER2','SEG_BER_SQZ2']:
         segmented_Prm['CWORD2'] = segmented_Prm['CWORD2'] | 0x0001 # Temp Compensate
         segmented_Prm['CWORD1'] = segmented_Prm['CWORD1'] | 0x0040 # Flaw list

      znLst = eval(str(self.params.get('ZONES', "range(self.dut.numZones)")))# self.params.get('ZONES', xrange(self.dut.numZones))

      # Run Segmented BER Parameters
      self.oProc = CProcess()
      
      SetFailSafe()
      if testSwitch.ENABLE_T175_ZAP_CONTROL:
         self.oProc.St(TP.zapPrm_175_zapOn)
      else:
         self.oProc.St(TP.setZapOnPrm_011)
         if not testSwitch.BF_0119055_231166_USE_SVO_CMD_ZAP_CTRL:
            self.oProc.St(TP.saveSvoRam2Flash_178)

      # OD Position 0
      test_zone = []
      for zn in TP.OD_POSITION_TEST_ZONES:
         if zn in znLst:
            test_zone.append(zn)
      if test_zone:
         if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
            MaskList = self.oProc.oUtility.convertListToZoneBankMasks(test_zone)
            for bank, list in MaskList.iteritems():
               if list:
                  segmented_Prm['ZONE_MASK_EXT'], segmented_Prm['ZONE_MASK'] = self.oProc.oUtility.convertListTo64BitMask(list)
                  segmented_Prm['ZONE_MASK_BANK'] = bank
                  self.oProc.St(segmented_Prm)
         else:
            segmented_Prm['ZONE_MASK'] = (0, 0x0012)
            self.oProc.St(segmented_Prm)

      if self.params.get('SUM_ONLY',1):
         segmented_Prm['CWORD2'] = segmented_Prm['CWORD2'] | 0x0200 # Summary Only on the rest of the zones
      if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
         segmented_Prm['ZONE_POSITION'] = 198
         MaskList = self.oProc.oUtility.convertListToZoneBankMasks(znLst)
         for bank, list in MaskList.iteritems():
            if list:
               segmented_Prm['ZONE_MASK_EXT'], segmented_Prm['ZONE_MASK'] = self.oProc.oUtility.convertListTo64BitMask(list)
               segmented_Prm['ZONE_MASK_BANK'] = bank
               self.oProc.St(segmented_Prm)
      else:
         segmented_Prm['ZONE_MASK'] = (0xFFFF, 0xFFFE)#(128L, 0)
         segmented_Prm['ZONE_MASK_EXT'] = (0xFFFF, 0xFFFE)#(128L, 0)
         segmented_Prm['ZONE_POSITION'] = 198
         self.oProc.St(segmented_Prm)

      if TP.zapOffOper_SegmentedBER: #defined zapoff according to operation
         if testSwitch.ENABLE_T175_ZAP_CONTROL: self.oProc.St(TP.zapPrm_175_zapOff)
         else:
            self.oProc.St(TP.setZapOffPrm_011)
            if not testSwitch.BF_0119055_231166_USE_SVO_CMD_ZAP_CTRL:
               self.oProc.St({'test_num':178, 'prm_name':'Save SAP in RAM to FLASH', 'CWORD1':0x420})
      ClearFailSafe()


#----------------------------------------------------------------------------------------------------------
class CWriteODIDGuardBand(CState):
   """
   Write extreme OD and ID
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from FSO import CFSO
      from Servo import CServoFunc

      self.oFSO = CFSO()
      self.oSrvFunc = CServoFunc()

      self.oFSO.getZoneTable()
      self.maxTrack = self.oFSO.dut.maxTrack
      self.ODWriteTrack = self.params.get('OD_Pad',0)
      self.IDWriteTrack = self.params.get('ID_Pad',0)

      ################### Force change to OCLIM to 30%
      try:
         objMsg.printMsg("Set OCLim to 30 before writing OD/ID guardband.")
         self.oSrvFunc.setOClim({}, 30, updateFlash = 1)
      except: objMsg.printMsg("Set OCLim failed!")

      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      self.oSrvFunc.St(TP.spinupPrm_2)

      for hd in range(self.dut.imaxHead):
         #arg = [reference_cylinder, num_cylinder, dir:OD/ID]
         guardBand_arg = [ [0, self.ODWriteTrack, -1], [self.maxTrack[hd], self.IDWriteTrack, +1] ]
         for args in guardBand_arg:
            for i in range(args[1]):
               testcyl = args[0] + (i + 1)*args[2]
               objMsg.printMsg("Hd=%s TestCyl=%s" % (hd, testcyl))
               ret = self.oSrvFunc.wsk(testcyl,hd)
               if(ret): #servo seek failure, skipping write track
                  objMsg.printMsg('Servo Seek Error Code: %s during write seek, skipping write track' % (str(ret)))
               else:
                  buf, errorCode = self.oSrvFunc.Fn(1283, 6, 0, 0xFFFF, 0x2004, 0x0004, 0xCCCC)  # write 1 track
                  buf, errorCode = self.oSrvFunc.Fn(1283, 6, 0, 0xFFFF, 0x2004, 0x0004, 0xCCCC)  # write 1 track
                  objMsg.printMsg('Error Code: %s during write.' % (str(errorCode)))

      ################### Force change to OCLIM to default
      try:
         objMsg.printMsg("Set back OCLim to default value")
         self.oSrvFunc.setOClim({}, TP.defaultOCLIM, updateFlash = 1)
      except: objMsg.printMsg("Set OCLim failed!")
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)


#----------------------------------------------------------------------------------------------------------
class CDisableZap(CState):
   """Disable ZAP."""
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      CProcess().St(TP.zapPrm_175_zapOff)
