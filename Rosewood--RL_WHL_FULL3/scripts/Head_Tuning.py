#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Head Tuning Module
#  - HEAD_CAL etc.
#  - Limit use to PRE2 states when possible
#
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/11/08 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Head_Tuning.py $
# $Revision: #4 $
# $DateTime: 2016/11/08 00:12:47 $
# $Author: gang.c.wang $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Head_Tuning.py#4 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#

from Constants import *
from TestParamExtractor import TP
from State import CState
from PowerControl import objPwrCtrl
import MessageHandler as objMsg
import ScrCmds
from Exceptions import CDblogDataMissing, CRaiseException

#----------------------------------------------------------------------------------------------------------
class CInitializeHead_Elec(CState):
   """
      Description: Class that will perform a calibration of the heads electrical basics- amplitude calibration and resistance (power)
      Base: NA
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

      from Servo import CServoOpti
      self.oSrvOpti = CServoOpti()

   #-------------------------------------------------------------------------------------------------------
   def Clear_MDW_OFST_WithRetry(self, prm = TP.ClearMDWOffset_73, retrycnt = 0):
      while 1:
         try:
            #self.oSrvOpti.St(TP.spinupPrm_1)
            self.oSrvOpti.St(prm)
            break # passed with no error code
         except:
            if retrycnt > 0:
               objMsg.printMsg("PwrCycle & retry Test73. Num Retries left %d \n" % retrycnt)
               objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
               retrycnt -= 1
               if 'T73_RETRY' in TP.Proc_Ctrl30_Def:
                  self.dut.driveattr['PROC_CTRL30'] = '0X%X' % (int(self.dut.driveattr.get('PROC_CTRL30', '0'),16) | TP.Proc_Ctrl30_Def['T73_RETRY'])
            else: # no retries remaining
               raise

   #-------------------------------------------------------------------------------------------------------
   def SeekWithRetry(self, ihd, retrycnt=2):
      retrycyl_1 = 150000
      retrycyl_2 = 210000
      seekprm = TP.prm_030_continuous_seek.copy()
      seekprm['BIT_MASK'] = (0, ihd)
      #self.oSrvOpti.St(seekprm)
      while 1:
         try:
            self.oSrvOpti.St(seekprm)
            break #passed with no error code
         except ScriptTestFailure, (failureData): #catch 14748, retry if it occurs
            if failureData[0][2] in [14748] and retrycnt > 0:
               objMsg.printMsg("EC:14748 - PwrCycle & retry Test30. Num Retries left %d \n" % retrycnt)
               objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
               if retrycnt == 1:
                 seekprm['START_CYL'] = self.oSrvOpti.oUtility.ReturnTestCylWord(retrycyl_2)
                 seekprm['END_CYL'] = self.oSrvOpti.oUtility.ReturnTestCylWord(retrycyl_2)
               else:
                 seekprm['START_CYL'] = self.oSrvOpti.oUtility.ReturnTestCylWord(retrycyl_1)
                 seekprm['END_CYL'] = self.oSrvOpti.oUtility.ReturnTestCylWord(retrycyl_1)
               retrycnt -= 1
            else: #not 14748 or no retries remaining
               raise
         except:
            raise

   #-------------------------------------------------------------------------------------------------------
   def Determine_Demod_Hd_N_Seek(self):
      objMsg.printMsg('Finding demod hd')
      demod_Hd = self.oSrvOpti.find_demod_hd()
      objMsg.printMsg('sync at hd %d, seek to testtrk .' % demod_Hd)
      self.SeekWithRetry(demod_Hd, 3)
      return demod_Hd

   #-------------------------------------------------------------------------------------------------------
   def setDefPGA(self,PGA_address, hd = 0):

      # Read Address 1
      rdPGAaddr = TP.getSymbolViaAddrPrm_11.copy()
      rdPGAaddr['ACCESS_TYPE'] = 3 # 32Bit Access
      rdPGAaddr['CWORD1'] = 1
      rdPGAaddr['START_ADDRESS'] = self.oSrvOpti.oUtility.ReturnTestCylWord(PGA_address)
      rdPGAaddr['END_ADDRESS'] = self.oSrvOpti.oUtility.ReturnTestCylWord(PGA_address)
      self.oSrvOpti.St(rdPGAaddr)

      # Read Address 2
      PGA_address = int(str(self.dut.dblData.Tables('P011_RW_SRVO_RAM_VIA_ADDR').tableDataObj()[-1]['SRVO_DATA']),16)
      rdPGAaddr['START_ADDRESS'] = self.oSrvOpti.oUtility.ReturnTestCylWord(PGA_address + (hd *2))
      rdPGAaddr['END_ADDRESS'] = self.oSrvOpti.oUtility.ReturnTestCylWord(PGA_address+ (hd *2))
      self.oSrvOpti.St(rdPGAaddr)

      # Update Default Gain
      gainWord = int(str(self.dut.dblData.Tables('P011_RW_SRVO_RAM_VIA_ADDR').tableDataObj()[-1]['SRVO_DATA']),16)
      rdPGAaddr.pop('EXTENDED_MASK_VALUE')
      rdPGAaddr['CWORD1'] = 2
      rdPGAaddr['WR_DATA'] = (gainWord & 0xF0FF) + 0x0b00
      rdPGAaddr['MASK_VALUE'] = 0xF0FF
      rdPGAaddr['ACCESS_TYPE'] = 2   # 16Bit Access
      self.oSrvOpti.St(rdPGAaddr)

   #-------------------------------------------------------------------------------------------------------
   def runT177(self):
      pgaGainParm = TP.pgaGainCalPrm_177.copy()
      if not testSwitch.extern.FE_0202123_228373_KARNAK_YARRAR_LSI and not testSwitch.M10P:
         pgaGainParm = TP.pgaGainCalPrm_177_1.copy()
      if 'TEST_CYL' in pgaGainParm: # save original test cyl
         TestCyl = self.oSrvOpti.oUtility.reverseTestCylWord(pgaGainParm['TEST_CYL'])
      else:
         TestCyl = -1

      allbadheadlist = []
      objMsg.printMsg('imaxHead ==> %s' % self.dut.imaxHead)
      for hd in range(self.dut.imaxHead):    #auto depop   //test for each head 
         hdMsk = (hd << 8) + hd
         pgaGainParm['HEAD_RANGE'] = hdMsk
         if TestCyl >= 0:                 # restore original test cyl
            pgaGainParm['TEST_CYL'] = self.oSrvOpti.oUtility.ReturnTestCylWord(TestCyl)
         elif 'TEST_CYL' in pgaGainParm:  # else, remove test cyl if added in by previous hd retry
            del pgaGainParm['TEST_CYL']
         try:
            objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
            self.oSrvOpti.St(TP.spinupPrm_1)
            self.oSrvOpti.St(pgaGainParm)
         except:
            allbadheadlist.append(hd)
      objMsg.printMsg('allbadheadlist ==> %s' % allbadheadlist)
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      if len(allbadheadlist) == 0:     #all head is good
         pass
      elif len(allbadheadlist) == self.dut.imaxHead and self.dut.HGA_SUPPLIER == 'RHO':      #change to TDK
         DriveAttributes['HGA_SUPPLIER'] = 'TDK'
         DriveAttributes['AAB'] = '25RW3E'
         ScrCmds.raiseException(11887, 'RHO All head is bad !!!!!! ')
      elif len(allbadheadlist) < self.dut.imaxHead and len(allbadheadlist) != 0:      #have bad head depop
         for badhd in allbadheadlist:
            depophead = self.dut.LgcToPhysHdMap[badhd]      #auto depop
            self.dut.globaldepopMask.append(depophead)
         self.dut.globaldepopMask = list(set(self.dut.globaldepopMask))
         self.dut.depopMask = self.dut.globaldepopMask
         self.dut.depopMask.sort()
         objMsg.printMsg('Needs to depop list = %s' % self.dut.depopMask)
         # testSwitch.FE_1111111_KillHead = 1
         raise Exception("Head HCL error.")
      else:
         ScrCmds.raiseException(11888, 'ALL Head is Bad !!!!!! ')


      RetryCnt = 2 + 1
      for hd in range(self.dut.imaxHead):
         LoopCnt = RetryCnt
         hdMsk = (hd << 8) + hd
         pgaGainParm['HEAD_RANGE'] = hdMsk
         curTestCyl = TestCyl
         if TestCyl >= 0:                 # restore original test cyl
            pgaGainParm['TEST_CYL'] = self.oSrvOpti.oUtility.ReturnTestCylWord(TestCyl)
         elif 'TEST_CYL' in pgaGainParm:  # else, remove test cyl if added in by previous hd retry
            del pgaGainParm['TEST_CYL']

         while LoopCnt:
            LoopCnt -= 1
            objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
            self.oSrvOpti.St(TP.spinupPrm_1)
            try:
               self.oSrvOpti.St(pgaGainParm)
               break
            except:
               if LoopCnt == 0:
                  objMsg.printMsg("T177 retry exhausted on Hd %d" % hd)
                  raise
               objMsg.printMsg("T177 retry #%d on Hd %d" % ((RetryCnt - LoopCnt), hd))
               if testSwitch.CHANGE_PREAMP_GAIN_BEFORE_T177_RETRY:
                  objMsg.printMsg("DBG: Update Gain Retry Hd %d" % hd)
                  PGA_address = self.oSrvOpti.readServoSymbolTable(['PGAgain'],TP.ReadPVDDataPrm_11, TP.getServoSymbolPrm_11, TP.getSymbolViaAddrPrm_11 )
                  self.setDefPGA(PGA_address, hd)
               if testSwitch.FE_0298339_305538_T177_RETRY_CHANGE_TEST_CYL:
                  if curTestCyl == -1:
                     curTestCyl = 190000  # set initial retry to 190k
                  else:
                     curTestCyl += 5000   # increase test cyl by 5k
                  pgaGainParm['TEST_CYL'] = self.oSrvOpti.oUtility.ReturnTestCylWord(curTestCyl)

   #-------------------------------------------------------------------------------------------------------
   def Init_ACFF_table(self, Demod_Hd):
      objMsg.printMsg('Fetching ACFF coeff.')
      Alt_hd = ~Demod_Hd & 0x01
      H0_Coeff_Hi, H0_Coeff, H1_Coeff_Hi, H1_Coeff = self.oSrvOpti.fetch_SINE_COEFF_16()
      objMsg.printMsg('coeff of H0=0x%X%X and H1=0x%X%X, update hd%d' % (H0_Coeff_Hi, H0_Coeff, H1_Coeff_Hi, H1_Coeff, Alt_hd))
      #objMsg.printMsg('Updating ACFF coeff of hd %d.' % Alt_hd)
      if Demod_Hd: ## if Demod_Hd is 1, use coeff of hd 1 to update hd 0
         self.oSrvOpti.set_hd_coeff(Alt_hd, H1_Coeff_Hi, H1_Coeff) # set hd 0 coeff
      else:  ## if Demod_Hd is 0, use coeff of hd 0 to update hd 1
         self.oSrvOpti.set_hd_coeff(Alt_hd, H0_Coeff_Hi, H0_Coeff) # set hd 1 coeff

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from AFH import CAFH
      self.oAFH = CAFH()
      if testSwitch.BF_0161447_340210_DUAL_HTR_IN_HEAD_CAL == 1:
         if testSwitch.FE_0174845_379676_HUMIDITY_SENSOR_CALIBRATION:
            from Temperature import CTemperature
            CTemperature().measureHumidity(spc_id=201)

         self.oAFH.setDualHeaterinRAP(self.dut.PREAMP_TYPE, self.dut.AABType, TP.clearance_Coefficients)

      #This section of code needs to run as early as possible to prevent over-bias of heads
      if testSwitch.FE_0154480_220554_P_SPIN_DOWN_BEFORE_T186_DURING_HEAD_CAL:
         self.oSrvOpti.St(TP.spindownPrm_2)

      if testSwitch.FE_0246017_081592_ENABLE_RV_SENSOR_IN_CERT_PROCESS:
         self.oSrvOpti.St(TP.RV_ADC_OFFSET_36)

      if testSwitch.FE_0173493_347506_USE_TEST321 and testSwitch.extern.SFT_TEST_0321:
         self.oSrvOpti.St(TP.mrBiasCal_321)
      else:
         from base_SerialTest import CCustUniqSAPCfg
         if CCustUniqSAPCfg(self.dut,{}).RVEnabled(self.dut.partNum) == 'enabled':
            self.oSrvOpti.St(TP.RV_ADC_OFFSET_36)

         if testSwitch.RUN_VBIAS_T186:
            self.oSrvOpti.setePreampBiasMode(enable = True)
         elif testSwitch.RUN_VBIAS_T186_A2D:
            self.oSrvOpti.setBiasOption(TP.CURRENT_MODE)
            objMsg.printMsg("Set Bias Option to Current Mode")
            self.oSrvOpti.St(TP.saveSvoRam2Flash_178)        #write to SAP
            objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1) #perform power cycle before this test
            objMsg.printMsg("Power Cycle Complete")
         self.oSrvOpti.St(TP.PresetAGC_InitPrm_186)
         if testSwitch.RUN_VBIAS_T186:
            self.oSrvOpti.setePreampBiasMode(enable = False)
         elif testSwitch.RUN_VBIAS_T186_A2D:
            self.oSrvOpti.setBiasOption(TP.VOLTAGE_MODE)
            objMsg.printMsg("Set Bias Option to Voltage Mode")
            self.oSrvOpti.St(TP.saveSvoRam2Flash_178)        #write to SAP
            objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1) #perform power cycle before this test
            objMsg.printMsg("Power Cycle Complete")

      if testSwitch.WA_0171001_395340_P_CHANGE_EC_11049_FROM_T177_HEAD_CAL:
         try:
            if not testSwitch.extern.FE_0202123_228373_KARNAK_YARRAR_LSI and not testSwitch.M10P:
               self.oSrvOpti.St(TP.pgaGainCalPrm_177_1)
            else:
               self.oSrvOpti.St(TP.pgaGainCalPrm_177)
         except:
            objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
            st(1, {'DELAY_TIME': [50], 'timeout': 100, 'CWORD1': [0], 'MAX_START_TIME': [200]})
            objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
            self.oSrvOpti.St(TP.prm_208_autoDebug)
            raise
      else:
         ### Running Test 177 on each head individually ###
         ### - org codde: self.oSrvOpti.St(TP.pgaGainCalPrm_177)
         self.runT177()


      ### Adding retry with powercycle and rerun Test 177 on each hds individually b4 rerunning test 186.
      ### org code: self.oSrvOpti.St(TP.PresetAGCPrm_186)
      if not testSwitch.FE_0173493_347506_USE_TEST321:
         try:
            self.oSrvOpti.St(TP.PresetAGCPrm_186)
         except:
            self.runT177()
            self.oSrvOpti.St(TP.PresetAGCPrm_186)
      ### END code needs to be run early

      #if testSwitch.FE_0194098_322482_SCREEN_DETCR_OPEN_CONNECTION:
      #   self.oSrvOpti.St(TP.DETCR_OpenScr_186)

      # Save MR resistance data for later comparison
      from RdWr import CMrResFile
      if testSwitch.FE_0173493_347506_USE_TEST321  and testSwitch.extern.SFT_TEST_0321:
         oMrRes = CMrResFile(TP.get_MR_Resistance_321, TP.mrDeltaLim)
      else:
         oMrRes = CMrResFile(TP.get_MR_Values_186, TP.mrDeltaLim)
      oMrRes.saveToGenResFile()

      #=== Heater resistance measurement
      from PreAmp import CPreAmp
      self.oPreAmp = CPreAmp()
      if testSwitch.FE_0146434_007955_P_T80_HD_CAL_ITEMS_TO_POP_BY_HD_TYPE:
         heaterResistancePrm_80_copy = TP.heaterResistancePrm_80.copy()
         if self.params.get('hdType') and self.params.get('T80ItemsToPop'):
            if self.dut.HGA_SUPPLIER == self.params['hdType']:
               for i in range(len(self.params['T80ItemsToPop'])):
                  heaterResistancePrm_80_copy.pop(self.params['T80ItemsToPop'][i])
         self.oPreAmp.heaterResistanceMeasurement(heaterResistancePrm_80_copy, TP.masterHeatPrm_11, 0)
      else:
         if not testSwitch.FE_SGP_81592_DISABLE_HEATER_RES_MEAS_T80:
            self.oPreAmp.heaterResistanceMeasurement(TP.heaterResistancePrm_80, TP.masterHeatPrm_11, 0)

      self.oAFH.setMasterHeat(TP.masterHeatPrm_11, setMHeatOn = 0) #disable master heat

      if testSwitch.RUN_HEAD_POLARITY_TEST:
         self.oSrvOpti.St(TP.headPolarityTest_26)

      if testSwitch.FE_0184102_326816_ZONED_SERVO_SUPPORT:
         self.Clear_MDW_OFST_WithRetry()
         # add another T73 calibration to find better track offset accuracy
         self.Clear_MDW_OFST_WithRetry(TP.ClearMDWOffset_73_1)
