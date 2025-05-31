#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Serial Port Operation Module for Mack. Contains all test classes (blocks) that support
#              state machine implementation of the manufacturing test process.
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/12/27 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Amazon/SerialTest.py $
# $Revision: #8 $
# $DateTime: 2016/12/27 23:52:43 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Amazon/SerialTest.py#8 $
# Level: 2
#---------------------------------------------------------------------------------------------------------#
from Constants import *
import MessageHandler as objMsg
from State import CState
from TestParamExtractor import TP
from PowerControl import objPwrCtrl
from base_SerialTest import *
if testSwitch.SPLIT_BASE_SERIAL_TEST_FOR_CM_LA_REDUCTION:
   from Opti_Read import CRdOpti
   from base_FNCTest import CDeltaRSSScreenBase 


###########################################################################################################
###########################################################################################################
class CPreLULTest25(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from Servo import CServoScreen
      self.oSrvScreen = CServoScreen()
      #self.oSrvScreen.St(TP.PresetAGCPrm_186)
      LULCycleCount = self.params.get('CYCLE_CNT', 100)           # Default is 100
      lulParams = self.oSrvScreen.oUtility.copy(TP.PreLoadUnloadPrm_25)
      lulParams.update({"NUM_SAMPLES":(LULCycleCount)})
      lulParams.update({"timeout":(LULCycleCount*15)})
      
      #self.oSrvScreen.St(TP.LULDefectScanPrm_109)       # LUL Area Defect Pre-Scan
      self.oSrvScreen.servoRetract(lulParams)            # T25 LUL Cycles
      #self.oSrvScreen.St(TP.LULDefectScanPrm_109)       # LUL Area Defect Post25-Scan
      #objPwrCtrl.powerCycle(useESlip=1)
      #self.oSrvScreen.St(TP.PresetAGCPrm_186)

      #self.oSrvScreen.St(TP.PresetAGC_InitPrm_186_PostPRE2)


###########################################################################################################
###########################################################################################################
class C250_BER(CState):
   """
      Description: Class that will T250 based BER test
      Base: N/A
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from RdWr import CRdWrScreen
      oRdWr = CRdWrScreen()

      #=== Test250: BER by zone
      oRdWr.quickSymbolErrorRate(TP.prm_quickSER_250,flawListMask=0,spc_id=2,numRetries=2)


###########################################################################################################
# This class is an envolving class used to get rid of perticles for MantaRay
# It will not be part of future test process
###########################################################################################################
class CPreParticleSweepBode(CState):
   """
      This class runs a pre particle sweep bode measurement
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.dut    = dut
      self.params = params
      CState.__init__(self, dut, [])
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from SDAT import CSdatTrkFlw
      if testSwitch.COMPART_SSO_SCREENING and self.dut.nextState in ['BODE3'] and DriveAttributes.get('HSA_REV','C') not in ['R','L','B']:
         cyl = self.params.get('CYL', 0) # default to zero to only do one cylinder
         self.dut.objData.update({'TEMP_P_SDAT_INFO' : {}})
         self.oSdatTrkFlw = CSdatTrkFlw(self.dut)
         if testSwitch.WA_0159131_007955_P_PWR_CYCLE_BEFORE_BODE_TEST:
            objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

         # Use T152 to measure bode only if the latest version of T288 is NOT used.  Otherwise, all bode data is already collected.
         self.oSdatTrkFlw.measureVcmBode(cyl)
         if testSwitch.FE_0115640_010200_SDAT_DUAL_STAGE_SUPPORT:
            self.oSdatTrkFlw.measureUactBode(cyl)
         if not testSwitch.WA_0115641_010200_DISABLE_OL_BODE_ON_DUAL_STAGE :
            self.oSdatTrkFlw.measureOlBode(cyl)
      elif not testSwitch.COMPART_SSO_SCREENING:
         cyl = self.params.get('CYL', 0) # default to zero to only do one cylinder
         self.dut.objData.update({'TEMP_P_SDAT_INFO' : {}})
         self.oSdatTrkFlw = CSdatTrkFlw(self.dut)
         if testSwitch.WA_0159131_007955_P_PWR_CYCLE_BEFORE_BODE_TEST:
            objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

         # Use T152 to measure bode only if the latest version of T288 is NOT used.  Otherwise, all bode data is already collected.
         self.oSdatTrkFlw.measureVcmBode(cyl)
         if testSwitch.FE_0115640_010200_SDAT_DUAL_STAGE_SUPPORT:
            self.oSdatTrkFlw.measureUactBode(cyl)
         if not testSwitch.WA_0115641_010200_DISABLE_OL_BODE_ON_DUAL_STAGE :
            self.oSdatTrkFlw.measureOlBode(cyl)

###########################################################################################################
# # This class is an envolving class used to get rid of perticles for MantaRay
# It will not be part of future test process
############################################################################################################
class CParticleAgitation(CState):
   """
   Perform a particle sweep along with other agitation attempts.
   This is the Serial (SF3) implementation of this Class.
   This Class uses T30, T25, and T212 to perform the Particle Sweep and agitation
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

      from Process import CProcess
      self.oProc = CProcess()

   #-------------------------------------------------------------------------------------------------------
   def LULsoft(self):
      objMsg.printMsg("*** Performing LUL soft ***")
      self.oProc.St(TP.LULsweep_25)
      return

   #-------------------------------------------------------------------------------------------------------
   def randomRW(self):
      objMsg.printMsg("*** Perfroming Random Write Seeks ***")
      randomWParams = (TP.random_write_seeks_30).copy()
      startZone = randomWParams['start_zone']
      endZone = randomWParams['end_zone']
      randomWParams.pop('start_zone')
      randomWParams.pop('end_zone')

      if testSwitch.WA_0139361_395340_P_PARTICLE_AGITATION_IO_PLUG:
         try:
            zt = self.dut.dblData.Tables(TP.zone_table['table_name']).tableDataObj()
         except:
            objMsg.printMsg("*** HAVE NO ZONE TABEL FROM INIT STATE ***")
            from FSO import CFSO
            self.oFSO = CFSO()
            self.oFSO.getZoneTable()
            zt = self.dut.dblData.Tables(TP.zone_table['table_name']).tableDataObj()
      else:
         zt = self.dut.dblData.Tables(TP.zone_table['table_name']).tableDataObj()

      Index = self.dth.getFirstRowIndexFromTable_byZone(zt, 0, startZone)
      startcyl = int(zt[Index]['ZN_START_CYL'])
      Index = self.dth.getFirstRowIndexFromTable_byZone(zt, 0, endZone)
      endcyl = int(zt[Index]['ZN_START_CYL']) + int(zt[Index]['NUM_CYL']) - 1
      while Index+1< len(zt) and int(zt[Index]['ZN']) == int(zt[Index+1]['ZN']):
         endcyl += int(zt[Index+1]['NUM_CYL']) 
         Index += 1

      randomWParams['START_CYL'] = self.oProc.oUtility.ReturnTestCylWord(startcyl)
      randomWParams['END_CYL'] = self.oProc.oUtility.ReturnTestCylWord(endcyl)
      self.oProc.St(randomWParams)
      return

   #-------------------------------------------------------------------------------------------------------
   def IDODSeeks(self):
      objMsg.printMsg("*** Performing T30 continuous IDOD Seeks ***")
      self.oProc.St(TP.prm_030_continuous_sweep)
      return

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from FSO import dataTableHelper
      self.dth = dataTableHelper()
      loops = self.params.get('LOOPS', 1)
      objMsg.printMsg("Loops: %d"%loops)
      for mainLoop in range(loops):
         objMsg.printMsg("====================== Particle Agitation Test loop %d ========================="%(mainLoop))
         self.oProc.St(TP.prm_particleSweep_212)
         self.IDODSeeks()
         self.randomRW()
         self.LULsoft()
      self.oProc.St(TP.prm_particleSweep_212)


###########################################################################################################
class CDisplay_G_list_X(CState):
   """
      Display G list
      Luxor specific, temporary
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from serialScreen import sptDiagCmds
      import sptCmds
      self.oSerial = sptDiagCmds()
      if testSwitch.FE_0121885_399481_ALLOW_SPC_ID_TO_BE_SET_BY_CALLER_IN_DISPLAY_G_LIST:
         spc_id = self.params.get('spc_id', 2)
      else:
         spc_id = 2

      objPwrCtrl.powerCycle()
      self.oSerial.enableDiags()
      self.oSerial.gotoLevel('T')
      sptCmds.sendDiagCmd("V1,,,1",timeout = 300, printResult = True, loopSleepTime=0)
      self.oSerial.dumpNonResidentGList()
      reassignData = self.oSerial.dumpReassignedSectorList()
      rListSectors, rListWedges = self.oSerial.dumpRList()
      if testSwitch.FE_0122102_399481_GET_CRITICAL_EVENTS_AFTER_G_LIST:
         self.oSerial.getCriticalEventLog() # assumes we're in level 1

      self.dut.dblData.Tables('P000_DEFECTIVE_PBAS').addRecord(
                              {
                              'SPC_ID'          : spc_id,
                              'OCCURRENCE'      : self.dut.objSeq.getOccurrence(),
                              'SEQ'             : self.dut.objSeq.curSeq,
                              'TEST_SEQ_EVENT'  : self.dut.objSeq.getTestSeqEvent(0),
                              'NUMBER_OF_PBAS'  : reassignData['NUMBER_OF_TOTALALTS'],
                              'RLIST_SECTORS'   : rListSectors,
                              'RLIST_WEDGES'    : rListWedges,
                              })

      objMsg.printDblogBin(self.dut.dblData.Tables('P000_DEFECTIVE_PBAS'))

      objPwrCtrl.powerCycle()


##############################################################################
class CHdLoadDamageScrn(CState):
   """
      Description:
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from Process import CProcess
      self.oProc = CProcess()
      self.oProc.St(TP.prm_ClearDBILog_101)
      self.oProc.St(TP.prm_126_read_sft)  #report servo flaw table, no data to oracle
      self.oProc.St(TP.prm_HdLoadDamageWrite_109)
      self.oProc.St(TP.prm_HdLoadDamageRead_109)
      self.oProc.St(prm_HdLoadDamageLimit_140)
      self.oProc.St(TP.prm_ClearDBILog_101)


###########################################################################################################
class CQuickFmt(CState):
   """
      Description:
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
      self.oSerial = sptDiagCmds()
      timeoutbyhd = self.dut.imaxHead * 150
      if( testSwitch.TRUNK_BRINGUP or testSwitch.ROSEWOOD7 ):
         timeoutbyhd = 1000 #workaround for F3 code bug, slow in quick format          
      objPwrCtrl.powerCycle()
      self.oSerial.enableDiags()
      self.oSerial.gotoLevel('T')
      sptCmds.sendDiagCmd("m0,6,2,,,,,22",timeout = timeoutbyhd, printResult = True, loopSleepTime=0)
      
      if testSwitch.SKIPZONE and not testSwitch.virtualRun and testSwitch.SINGLEPASSFLAWSCAN:
         DoneSkipZone = self.oSerial.skipZone()
      else:
         DoneSkipZone = 0
         
      if( testSwitch.TRUNK_BRINGUP or testSwitch.ROSEWOOD7):
         #objPwrCtrl.powerCycle(useESlip=1)
         #oSerial = sptDiagCmds()
         #sptCmds.enableDiags()
         sptCmds.gotoLevel('C')
         # C>U8 to initialize media chche
         result = sptCmds.sendDiagCmd('U8', timeout = 3000)
         objMsg.printMsg  ("\nInitialize media cache table \n%s" % (result))


###########################################################################################################
class CWrtOnlyFmt(CState):
   """
      Description:
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from serialScreen import sptDiagCmds
      import sptCmds
      self.oSerial = sptDiagCmds()
      timeoutbyhd = self.dut.imaxHead * 18000
      objPwrCtrl.powerCycle()
      self.oSerial.enableDiags()
      self.oSerial.gotoLevel('T')
      if testSwitch.SINGLEPASSFLAWSCAN:
         sptCmds.sendDiagCmd("m0,8d,3,15,a,45,,22,,15,a,45,32,0505,0202",timeout = timeoutbyhd, printResult = True, loopSleepTime=10)
      else:
         sptCmds.sendDiagCmd("m0,4,,20,,,,22",timeout = timeoutbyhd, printResult = True, loopSleepTime=0)
      sptCmds.sendDiagCmd('V1,,,1', timeout = 600, printResult = True, raiseException = 0)


###########################################################################################################
class CParticleSweepMode(CState):
   """
   Perform a particle sweep.  This class can either operation using F3 diags, or using SF3 test
   212.  The default mode is F3, but if the user specifies input parameter 'MODE' as 'SF3', it will
   use T212.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      mode = self.params.get('MODE', 'DIAG')
      if mode == 'DIAG':
         from serialScreen import sptDiagCmds
         import sptCmds
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
         oSerial = sptDiagCmds()
         sptCmds.enableDiags()
         oSerial.particleSweep(TP.prm_particleSweep)
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      elif mode == 'SF3':
         from Process import CProcess
         self.oProc = CProcess()

         rework = self.params.get('REWORK','NA')

         if rework=='Y' and DriveAttributes.get('PRIME','NA')=='N': # Rework drive
            loopAgi = 5
         else:
            loopAgi = 1 # Prime drive

         for n in xrange(loopAgi):
            objMsg.printMsg("====================== Particle Sweep Test loop %d ========================="%(n+1))
            self.oProc.St(TP.prm_particleSweepMode_212)

      else:
         objMsg.printMsg("Improper state parameter 'MODE': %s" % mode)


###########################################################################################################
class CRdOpti_2DVBAR(CRdOpti):
   def __init__(self, dut, params={}, useSYSZnParm=0,zapOtfWP=0,zapOtfWP2=0,zapOtfZN=0,zapOtfHMS=0):
      CRdOpti.__init__(self, dut, params, useSYSZnParm, zapOtfWP, zapOtfWP2, zapOtfZN, zapOtfHMS)
      
   if testSwitch.FAST_2D_VBAR: #overriding the base_serialTest function
      #-------------------------------------------------------------------------------------------------------
      def basicAGEREOpti(self, oRdWr, zappedOptiTracks, targetOpti = False, zapOTF = 0, zapOtfWP = 0, zapOtfWP2 = 0):
         zone_copy_State = ['READ_OPTI']
         if testSwitch.FE_0293167_356688_VBAR_MARGIN_ZONE_COPY:
            zone_copy_State.extend(['VBAR_MARGIN', 'VBAR_MARGIN_OPTI', 'VBAR_MARGIN_RLOAD'])
         if testSwitch.FE_SGP_81592_COLLECT_BER_B4_N_AFTER_RD_OPTI:
            #calling runT250_channel which in baseSerialTest.py and ignore ec_st
            self.runT250_channel(oRdWr, spc_id_on_track = 4, spc_id_sqz_wrt=24)

         #data collection for write to write variation, using offtrack AC erase, optimize offtrack percentage
         #it will take 3 min , try to correct with drive data
         #data collection for write to write variation, using offtrack AC erase , optimize offtrack percentage
         #it will take 3 min , try to correct with drive data
         if testSwitch.extern.SFT_TEST_0396 and testSwitch.ENABLE_T396_DATACOLLECTION and (self.dut.nextState == 'READ_OPTI'):
            t396 = {
                   'timeout'            : 500000,
                   'ZONE_MASK'          : (0x8000, 0x0001),
                   'ZONE_MASK_EXT'      : (0x800, 0x0),
                   'STEP_INC'           : 25,
                   'ITERATIONS'         : 20,
                   'REVS'               : 5    }
            try:
                st(396,t396)
            except: pass

         if (self.dut.nextState == 'READ_OPTI' or self.dut.nextState == 'VAR_SPARES'):
            base_phastOptiPrm_251_local = TP.base_phastOptiPrm_251.copy()
         else:
            base_phastOptiPrm_251_local = TP.simple_OptiPrm_251.copy()
         if not testSwitch.FE_0314243_356688_P_CM_REDUCTION_REDUCE_CHANNEL_MSG:
            result_returned = 0x0007
         if self.params.get('OFF_LOG', 1): #off log result
            result_returned   = 0
         cword1 = base_phastOptiPrm_251_local['CWORD1']
         if not self.params.get('BAND_WRITE_251', 0): # with band write 251
            cword1 = cword1 | 0x4000
         if testSwitch.FAST_2D_VBAR_TESTTRACK_CONTROL:
            cword1 = cword1 | 0x8000
         if (testSwitch.FE_0253168_403980_RD_OPTI_ODD_ZONE_COPY_TO_EVEN and self.dut.nextState == 'READ_OPTI'):    # only test odd zones
            orgtestZones = oRdWr.testZones
            oRdWr.testZones = range(1, self.dut.numZones, 2)
            if not(self.dut.numZones % 2):
               if not (self.dut.numZones - 1) in oRdWr.testZones:
                  oRdWr.testZones.append(self.dut.numZones - 1)   # must tune last zone if it's odd zone
            objMsg.printMsg("oRdWr.testZones = %s" % oRdWr.testZones)
            if testSwitch.SMR:
               objMsg.printMsg("self.dut.numZones = %s" % self.dut.numZones)
               objMsg.printMsg("UMP ZONES = %s" % TP.UMP_ZONE[self.dut.numZones])
               for zn in TP.UMP_ZONE[self.dut.numZones]:
                  if (zn < self.dut.numZones):
                     if (zn % 2):  #odd zone
                        if not (zn - 1) in TP.UMP_ZONE[self.dut.numZones]:
                           if not (zn - 1) in oRdWr.testZones:
                              oRdWr.testZones.append(zn-1)
                     else: #even zone
                        if not (zn + 1) in TP.UMP_ZONE[self.dut.numZones]:
                           if not (zn) in oRdWr.testZones:
                              oRdWr.testZones.append(zn)
            objMsg.printMsg("oRdWr.testZones = %s" % oRdWr.testZones)
            cword1 = cword1 | 0x1000 # To enable odd zones copy to even zones in T251
            
         if testSwitch.REDUCE_LOG_SIZE:
            result_returned = 0

         if not testSwitch.FE_0314243_356688_P_CM_REDUCTION_REDUCE_CHANNEL_MSG:
             base_phastOptiPrm_251_local.update({'RESULTS_RETURNED': result_returned, 'CWORD1' : cword1}) 
         else:
             base_phastOptiPrm_251_local.update({'CWORD1' : cword1}) 

         if testSwitch.extern.FE_0308987_403980_PRECODER_PF3_INPUT:
             # Temporary update T251 new parameters here.
             # Extern test switch cannot be added in Test_Switches.py, it can only be added to Feature_Release_Test_Switches.py.
             # Extern test switch from Feature_Release_Test_Switches.py cannot be added in TestParameters.py.
             # Thus the only way to use extern.FE_0308987_403980_PRECODER_PF3_INPUT is here. 
             # This is only a temporary solution to prevent pf3 & sf3 mismatched failure. 
             # When most pco picks up the latest SF3, this switch can be removed.
             # These T251 new parameters will be defined in TestParameters.py.
             base_phastOptiPrm_251_local.update({'PRECODER0': (0x0713, 0x4652), 'PRECODER1': (0x0713, 0x4625), 'PRECODER2': (0x0145, 0x7362), 'PRECODER3': (0x0142, 0x7365), 'PRECODER4': (0x7654, 0x3210)}) 

         if (testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT and (self.dut.nextState in zone_copy_State) and testSwitch.FE_0271421_403980_P_ZONE_COPY_OPTIONS):
             orgheadRange = oRdWr.headRange
             orgtestZones = oRdWr.testZones
             self.T251_zone_copy_support(base_phastOptiPrm_251_local,oRdWr)
             oRdWr.headRange = orgheadRange
             oRdWr.testZones = orgtestZones
         if not (self.dut.nextState in zone_copy_State and testSwitch.FE_0271421_403980_P_ZONE_COPY_OPTIONS):
              oRdWr.phastOpti(base_phastOptiPrm_251_local, maxRetries = 3, zapFunc = None, zapECList = self.zapECList) #
         if (testSwitch.FE_0253168_403980_RD_OPTI_ODD_ZONE_COPY_TO_EVEN and self.dut.nextState == 'READ_OPTI'):    # only test odd zones
            oRdWr.testZones = orgtestZones
         if testSwitch.FE_SGP_81592_COLLECT_BER_B4_N_AFTER_RD_OPTI:
            #calling runT250_channel which in baseSerialTest.py and return ec_st
            if self.dut.nextState == 'READ_OPTI': # display BER for all zone after read opti, for zone copy checkup
                oRdWr.onTrackTestZonesBER = range(0, self.dut.numZones)
                oRdWr.sqzWrtTestZonesBER = range(0, self.dut.numZones)
            ec_st = self.runT250_channel(oRdWr, spc_id_on_track = 5, spc_id_sqz_wrt=25)
          #data collection for write to write variation, using offtrack AC erase, optimize offtrack percentage
          #it will take 3 min , try to correct with drive data
          #data collection for write to write variation, using offtrack AC erase , optimize offtrack percentage
          #it will take 3 min , try to correct with drive data
         if testSwitch.extern.SFT_TEST_0396 and testSwitch.ENABLE_T396_DATACOLLECTION and (self.dut.nextState == 'READ_OPTI'):
            t396 = {
                 'timeout'            : 500000,
                 'ZONE_MASK'          : (0x8000, 0x0001),
                 'ZONE_MASK_EXT'      : (0x800, 0x0),
                 'STEP_INC'           : 25,
                 'ITERATIONS'         : 20,
                 'REVS'               : 5    }
            try:
               st(396,t396)
            except: pass

###########################################################################################################    
 
class CPrecoder(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
     self.params = params
     depList = []
     CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
     from Process import CProcess, CCudacom
     self.oProc = CProcess()
     self.oOudacom = CCudacom()
            
     pIDX0_3 = self.oProc.oUtility.copy(TP.prm_Pcode_DET_LUT_IDX0_3)
     pIDX4_7 = self.oProc.oUtility.copy(TP.prm_Pcode_DET_LUT_IDX4_7)
     pMAP0 = self.oProc.oUtility.copy(TP.prm_Pcode_PCODE_MAP0)
     pMAP1 = self.oProc.oUtility.copy(TP.prm_Pcode_PCODE_MAP1)
     Zn16_allMsk = TP.prm_Pcode_all_msk['Zn16_allMsk']
     Zn32_allMsk = TP.prm_Pcode_all_msk['Zn32_allMsk']
     Zn48_allMsk = TP.prm_Pcode_all_msk['Zn48_allMsk']
     Zn64_allMsk = TP.prm_Pcode_all_msk['Zn64_allMsk']
     
     #objMsg.printMsg(" Zn16_allMsk : %x , Zn32_allMsk : %x  ,  Zn48_allMsk : %x , Zn64_allMsk : %x " % (Zn16_allMsk, Zn32_allMsk , Zn48_allMsk, Zn64_allMsk))
     
     Local_Precoder_BER_prm = TP.Precoder_BER_prm_250.copy()
     #Run 2 T250 with bypass setting to ensure stable result in doing precoder tuning
     xIDX0_3 = pIDX0_3['Param'][0]
     xIDX4_7 = pIDX4_7['Param'][0]
     xMAP0 = pMAP0['Param'][0]
     xMAP1= pMAP1['Param'][0]
     buf, errorCode = self.oOudacom.Fn(TP.pCodeCudocomCMD, pIDX0_3['REG_ID'], xMAP0 , 0xFFFF, Zn16_allMsk, Zn32_allMsk, Zn48_allMsk, Zn64_allMsk, retries=3)
     buf, errorCode = self.oOudacom.Fn(TP.pCodeCudocomCMD, pIDX4_7['REG_ID'], xMAP1 , 0xFFFF, Zn16_allMsk, Zn32_allMsk, Zn48_allMsk, Zn64_allMsk, retries=3)
     buf, errorCode = self.oOudacom.Fn(TP.pCodeCudocomCMD, pMAP0['REG_ID'], xIDX0_3 , 0xFFFF, Zn16_allMsk, Zn32_allMsk, Zn48_allMsk, Zn64_allMsk, retries=3)
     buf, errorCode = self.oOudacom.Fn(TP.pCodeCudocomCMD, pMAP1['REG_ID'], xIDX4_7 , 0xFFFF, Zn16_allMsk, Zn32_allMsk, Zn48_allMsk, Zn64_allMsk, retries=3)
     Local_Precoder_BER_prm.update({'spc_id' : 9421})
     self.oProc.St(Local_Precoder_BER_prm)
     Local_Precoder_BER_prm.update({'spc_id' : 9422})
     self.oProc.St(Local_Precoder_BER_prm)
     # end 2 T250 run
     for x in range(len(pIDX0_3['Param'])):
        
        xIDX0_3 = pIDX0_3['Param'][x]
        xIDX4_7 = pIDX4_7['Param'][x]
        xMAP0 = pMAP0['Param'][x]
        xMAP1= pMAP1['Param'][x]
        buf, errorCode = self.oOudacom.Fn(TP.pCodeCudocomCMD, pIDX0_3['REG_ID'], xMAP0 , 0xFFFF, Zn16_allMsk, Zn32_allMsk, Zn48_allMsk, Zn64_allMsk, retries=3)
        buf, errorCode = self.oOudacom.Fn(TP.pCodeCudocomCMD, pIDX4_7['REG_ID'], xMAP1 , 0xFFFF, Zn16_allMsk, Zn32_allMsk, Zn48_allMsk, Zn64_allMsk, retries=3)
        buf, errorCode = self.oOudacom.Fn(TP.pCodeCudocomCMD, pMAP0['REG_ID'], xIDX0_3 , 0xFFFF, Zn16_allMsk, Zn32_allMsk, Zn48_allMsk, Zn64_allMsk, retries=3)
        buf, errorCode = self.oOudacom.Fn(TP.pCodeCudocomCMD, pMAP1['REG_ID'], xIDX4_7 , 0xFFFF, Zn16_allMsk, Zn32_allMsk, Zn48_allMsk, Zn64_allMsk, retries=3)
        objMsg.printMsg(" Precoder Combi - %d " % x )
        Local_Precoder_BER_prm.update({'spc_id' : (9423 + x)})
        self.oProc.St(Local_Precoder_BER_prm)
        tableData = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').tableDataObj()
        if (x == 0):
            Local_MaxTable = self.oProc.oUtility.copy(TP.MaxTable)
            for row in tableData:
                if (int(row['SPC_ID']) == (9423+x)) :
                    Local_MaxTable['HD_PHYS_PSN'].append(int(row['HD_PHYS_PSN']))
                    Local_MaxTable['DATA_ZONE'].append(int(row['DATA_ZONE']))
                    Local_MaxTable['RAW_ERROR_RATE'].append(float(row['RAW_ERROR_RATE']))
                    Local_MaxTable['COMBI'].append(x)
        else:
            y=0
            for row in tableData:
                if (int(row['SPC_ID']) == (9423+x)) :
                    if(float(row['RAW_ERROR_RATE']) < Local_MaxTable['RAW_ERROR_RATE'][y]):
                        Local_MaxTable['HD_PHYS_PSN'][y] = int(row['HD_PHYS_PSN'])
                        Local_MaxTable['DATA_ZONE'][y] =  int(row['DATA_ZONE'])
                        Local_MaxTable['RAW_ERROR_RATE'][y] = float(row['RAW_ERROR_RATE'])
                        Local_MaxTable['COMBI'][y] = x
                    y+=1
                  
   
     ## Local_MaxTable Processing ##
     Curr_Zone  =  0
     for z in range(len(Local_MaxTable['HD_PHYS_PSN'])):
         
         COMBI = Local_MaxTable['COMBI'][z]
         Curr_Head = Local_MaxTable['HD_PHYS_PSN'][z]
         if (Local_MaxTable['DATA_ZONE'][z] < 16):
           pIDX0_3['Zn16Msk'][COMBI] =  pIDX0_3['Zn16Msk'][COMBI] | 1<<Local_MaxTable['DATA_ZONE'][z]
           pIDX4_7['Zn16Msk'][COMBI] =  pIDX4_7['Zn16Msk'][COMBI] | 1<<Local_MaxTable['DATA_ZONE'][z]
           pMAP0['Zn16Msk'][COMBI] =  pMAP0['Zn16Msk'][COMBI] | 1<<Local_MaxTable['DATA_ZONE'][z]
           pMAP1['Zn16Msk'][COMBI] =  pMAP1['Zn16Msk'][COMBI] | 1<<Local_MaxTable['DATA_ZONE'][z]
          
         elif (Local_MaxTable['DATA_ZONE'][z] < 32):
           pIDX0_3['Zn32Msk'][COMBI] =  pIDX0_3['Zn32Msk'][COMBI] | 1<<(Local_MaxTable['DATA_ZONE'][z]-16)
           pIDX4_7['Zn32Msk'][COMBI] =  pIDX4_7['Zn32Msk'][COMBI] | 1<<(Local_MaxTable['DATA_ZONE'][z]-16)
           pMAP0['Zn32Msk'][COMBI] =  pMAP0['Zn32Msk'][COMBI] | 1<<(Local_MaxTable['DATA_ZONE'][z]-16)
           pMAP1['Zn32Msk'][COMBI] =  pMAP1['Zn32Msk'][COMBI] | 1<<(Local_MaxTable['DATA_ZONE'][z]-16)
           
         elif (Local_MaxTable['DATA_ZONE'][z] < 48):
           pIDX0_3['Zn48Msk'][COMBI] =  pIDX0_3['Zn48Msk'][COMBI] | 1<<(Local_MaxTable['DATA_ZONE'][z]-32)          
           pIDX4_7['Zn48Msk'][COMBI] =  pIDX4_7['Zn48Msk'][COMBI] | 1<<(Local_MaxTable['DATA_ZONE'][z]-32)
           pMAP0['Zn48Msk'][COMBI] =  pMAP0['Zn48Msk'][COMBI] | 1<<(Local_MaxTable['DATA_ZONE'][z]-32)
           pMAP1['Zn48Msk'][COMBI] =  pMAP1['Zn48Msk'][COMBI] | 1<<(Local_MaxTable['DATA_ZONE'][z]-32)
           
         elif (Local_MaxTable['DATA_ZONE'][z] < 60):
           pIDX0_3['Zn60Msk'][COMBI] =  pIDX0_3['Zn60Msk'][COMBI] | 1<<(Local_MaxTable['DATA_ZONE'][z]-48)
           pIDX4_7['Zn60Msk'][COMBI] =  pIDX4_7['Zn60Msk'][COMBI] | 1<<(Local_MaxTable['DATA_ZONE'][z]-48)
           pMAP0['Zn60Msk'][COMBI] =  pMAP0['Zn60Msk'][COMBI] | 1<<(Local_MaxTable['DATA_ZONE'][z]-48)           
           pMAP1['Zn60Msk'][COMBI] =  pMAP1['Zn60Msk'][COMBI] | 1<<(Local_MaxTable['DATA_ZONE'][z]-48)
           
         else:
           objMsg.printMsg("ZONE OUT OF RANGE")
         
         if(Curr_Zone == self.dut.numZones-1):
             CurrHeadMsk = 1<<Curr_Head      
             for i in range(len(pIDX0_3['Param'])):
                buf,errorCode = self.oOudacom.Fn(TP.pCodeCudocomCMD, pIDX0_3['REG_ID'], pIDX0_3['Param'][i] , CurrHeadMsk, pIDX0_3['Zn16Msk'][i], pIDX0_3['Zn32Msk'][i], pIDX0_3['Zn48Msk'][i], pIDX0_3['Zn60Msk'][i], retries=3)
                buf,errorCode = self.oOudacom.Fn(TP.pCodeCudocomCMD, pIDX4_7['REG_ID'], pIDX4_7['Param'][i] , CurrHeadMsk, pIDX4_7['Zn16Msk'][i], pIDX4_7['Zn32Msk'][i], pIDX4_7['Zn48Msk'][i], pIDX4_7['Zn60Msk'][i], retries=3)
                buf,errorCode = self.oOudacom.Fn(TP.pCodeCudocomCMD, pMAP0['REG_ID'], pMAP0['Param'][i] , CurrHeadMsk, pMAP0['Zn16Msk'][i], pMAP0['Zn32Msk'][i], pMAP0['Zn48Msk'][i], pMAP0['Zn60Msk'][i], retries=3)
                buf,errorCode = self.oOudacom.Fn(TP.pCodeCudocomCMD, pMAP1['REG_ID'], pMAP1['Param'][i] , CurrHeadMsk, pMAP1['Zn16Msk'][i], pMAP1['Zn32Msk'][i], pMAP1['Zn48Msk'][i], pMAP1['Zn60Msk'][i], retries=3)
             Curr_Zone = 0
             pIDX0_3 = self.oProc.oUtility.copy(TP.prm_Pcode_DET_LUT_IDX0_3)
             pIDX4_7 = self.oProc.oUtility.copy(TP.prm_Pcode_DET_LUT_IDX4_7)
             pMAP0 = self.oProc.oUtility.copy(TP.prm_Pcode_PCODE_MAP0)
             pMAP1 = self.oProc.oUtility.copy(TP.prm_Pcode_PCODE_MAP1)
         
         else:
             Curr_Zone += 1
         
         
         
     for i in range(len(Local_MaxTable['HD_PHYS_PSN'])):
            self.dut.dblData.Tables('P_PRECODER_SUMMARY').addRecord({
                'SPC_ID'              : 9222,
                'COMBI'               : Local_MaxTable['COMBI'][i],
                'HD_PHYS_PSN'         : Local_MaxTable['HD_PHYS_PSN'][i],  # hd
                'DATA_ZONE'           : Local_MaxTable['DATA_ZONE'][i],
                'RAW_ERROR_RATE'      : Local_MaxTable['RAW_ERROR_RATE'][i],
                'PCodeMap0'           : pMAP0['Param'][Local_MaxTable['COMBI'][i]],
                'PCodeMap1'           : pMAP1['Param'][Local_MaxTable['COMBI'][i]],
                'IDX0_3'              : pIDX0_3['Param'][Local_MaxTable['COMBI'][i]],
                'IDX4_7'              : pIDX4_7['Param'][Local_MaxTable['COMBI'][i]],
                'OCCURRENCE'          : self.dut.objSeq.getOccurrence(),
                'SEQ'                 : self.dut.objSeq.curSeq,
                'TEST_SEQ_EVENT'      : self.dut.objSeq.getTestSeqEvent(0),})      
                
     objMsg.printDblogBin(self.dut.dblData.Tables('P_PRECODER_SUMMARY'))
                
     self.oProc.St({'test_num':178, 'prm_name':'Save RAP in RAM to FLASH', 'CWORD1': 544})      

     if not testSwitch.virtualRun:
        try:
           self.dut.dblData.delTable('P250_ERROR_RATE_BY_ZONE', forceDeleteDblTable = 1)
        except:
           objMsg.printMsg(" delete table failed" )
 

############################################################################################################
##overriding the CDeltaRSSScreen defined in baseSerial
class CDeltaRSSScreen(CDeltaRSSScreenBase):
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CDeltaRSSScreenBase.__init__(self, dut, depList)
   
   if testSwitch.SMR:
      ###Override functions defined in baseSerial for SMR
      #-------------------------------------------------------------------------------------------------------
      def updateT250Params(self, tst_prm):
         if testSwitch.FE_0124358_391186_T250_ZONE_SWEEP_RETRIES:
            tst_prm['ZONE_POSITION'] = 198    #Start at the end of the zone before sweeping zone if necessary
         if self.actions.get('ODD_ZONES', 0): # Odd Zones only and UMP
            from Utility import CUtility
            tst_prm.update({'TEST_ZONES' : list( set(range(1, self.dut.numZones, 2))  | \
               set(CUtility().getUMPZone(range(self.dut.numZones))) ) })
         objMsg.printMsg("tst_prm['TEST_ZONES'] %s" % str(tst_prm['TEST_ZONES'])) 
         if self.actions.get('OTF', 0): #OTF mode instead of SOVA
            tst_prm.update({'MODES' : ['SECTOR']})
         if self.actions.get('RST_RD_OFFSET', 0): #Reset read offset to on track read
            tst_prm.update({'CWORD2' : (tst_prm['CWORD2'][0] | 0x0800, )})
         if self.actions.get('SQZ_WRITE', 0): # SQZ writing instead on track write read
            tst_prm.update({'NUM_SQZ_WRITES' : 1 }) #num of adjacent track write
         if self.actions.get('TCC', 0): # enable temperature compensation
            tst_prm.update({'CWORD2' : (tst_prm['CWORD2'][0] | 0x0001, )})
         if self.actions.get('MIN_SOVA', 0): # Minimum sova to override
            tst_prm['MINIMUM'] = self.actions.get('MIN_SOVA', 0)
         tst_prm.update({'MAX_ERR_RATE' : self.actions.get('MAX_ERR_RATE', -90)}) #default -90
         return tst_prm
         
      #-------------------------------------------------------------------------------------------------------
      def RunT250(self):
         #=== Test250: BER by zone
         from Utility import CUtility
         self.SERprm = CUtility().copy(TP.prm_quickSER_250)
         self.SERprm = self.updateT250Params(self.SERprm) #update the test param according user inputs
         self.spc_id_used_in_readscrn2 = self.actions.get('spc_id', TP.RdScrn2_SPC_ID) #default is 2 

         if self.params.get('SKIP_FLAW', 0):
            flawListMask = 0x100
         else:
            flawListMask = 0x140

         #if flawListMask=0x140 for the call then go with 1 retries
         try:
            self.oRdWr.quickSymbolErrorRate(self.SERprm, flawListMask=flawListMask, spc_id=self.spc_id_used_in_readscrn2, numRetries=1)
         except:
            objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

         if self.params.get('FAIL_SAFE', 0): # fail safe
            objMsg.printMsg("FAIL_SAFE on")
         if testSwitch.FE_0332210_305538_P_T250_SQZ_WRITE_SCREEN and self.dut.BG not in ['SBS']:
            from dbLogUtilities import DBLogCheck
            dblchk = DBLogCheck(self.dut)
            failFlag = (dblchk.checkComboScreen(TP.T250_SqzWrite_Screen_Spec1) == FAIL)
            failFlag = failFlag or (dblchk.checkComboScreen(TP.T250_SqzWrite_Screen_Spec3) == FAIL)
            failFlag = failFlag or (dblchk.checkComboScreen(TP.T250_SqzWrite_Screen_Spec4) == FAIL)
            if failFlag and not self.params.get('FAIL_SAFE', 0):
               if testSwitch.ENABLE_ON_THE_FLY_DOWNGRADE and self.downGradeOnFly(1, 14929):
                  objMsg.printMsg('Failed for Sqz Write Spec, downgrade to %s as %s' % (self.dut.BG, self.dut.partNum))
               else:
                  ScrCmds.raiseException(14929, 'Failed for Sqz Write Spec @ Head : %s' % str(dblchk.failHead))
            if dblchk.checkComboScreen(TP.T250_SqzWrite_Screen_Spec5) == FAIL : 
               if testSwitch.ENABLE_ON_THE_FLY_DOWNGRADE and self.downGradeOnFly(1, 14929):
                  objMsg.printMsg('Failed for Sqz Write Spec, downgrade to %s as %s' % (self.dut.BG, self.dut.partNum))
               else:
                  ScrCmds.raiseException(14929, 'Failed for Sqz Write Spec @ Head : %s' % str(dblchk.failHead))
            
         if TP.PoorSovaHDInstCombo_Spec2 and not testSwitch.virtualRun:
            objMsg.printMsg("PoorSovaHDInstCombo_Spec2")
            wpeUin = eval('[%s]' % self.dut.driveattr['WPE_UIN'])
            if dblchk.checkComboScreen(TP.PoorSovaHDInstCombo_Spec2['MAX_BER']) == FAIL and wpeUin <= TP.PoorSovaHDInstCombo_Spec2['Drive_WPE_uinch'] :
               if testSwitch.ENABLE_ON_THE_FLY_DOWNGRADE and self.downGradeOnFly(1, 10560):
                  objMsg.printMsg('Failed PoorSovaHDInstCombo_Spec2, downgrade to %s as %s' % (self.dut.BG, self.dut.partNum))
               else:
                  ScrCmds.raiseException(10560, "Failed PoorSovaHDInstCombo_Spec2 @ Head : [%s]" % str(hd))

      #-------------------------------------------------------------------------------------------------------
      def handleEC10632(self):
         #retrieve fail hds at rd_scrn2
         import dbLogUtilities
         self.dut.rezapAttr = self.dut.rezapAttr & 0x00ff #clear
         hd_fail_table = self.dut.dblData.Tables('P_ERROR_RATE_STATUS').chopDbLog('SEQ', 'match', self.dut.objSeq.curSeq)
         table_T250 = dbLogUtilities.DBLogReader(self.dut, 'P250_ERROR_RATE_BY_ZONE')
         for hd_row in hd_fail_table:
            fail_rows = table_T250.getRows({'HD_PHYS_PSN': hd_row['HD_PHYS_PSN'], 
               'FAIL_CODE': 10632, 'SPC_ID' : self.spc_id_used_in_readscrn2})
            zap_degrade = False # hd that zap degrade
            for row in fail_rows: #compare with rd_scrn result for same hd and zone
               compare_row = table_T250.findRow({'HD_PHYS_PSN': hd_row['HD_PHYS_PSN'], 'DATA_ZONE': row['DATA_ZONE'],
                  'SPC_ID' : TP.RDScrn_SPC_ID})
               if compare_row and \
                  ((float(row['RAW_ERROR_RATE']) - float(compare_row['RAW_ERROR_RATE']))> self.SERprm['max_diff']):
                  zap_degrade = True
                  break
            objMsg.printMsg("zap_degrade %s for hd %s" %(str(zap_degrade), str(hd_row['HD_PHYS_PSN']))) #debug
            if zap_degrade and not (self.dut.rezapAttr & 1 << hd_row['HD_PHYS_PSN']): 
               self.dut.rezapAttr = self.dut.rezapAttr | (1 << hd_row['HD_PHYS_PSN'] + 8)
         if not (self.dut.rezapAttr & 0xff00) : 
            del TP.stateRerunParams['dependencies']['READ_SCRN2']
            
      #-------------------------------------------------------------------------------------------------------
      def loadActions(self):
         self.actions = {
            'RUN_T163'          : not testSwitch.FE_0121254_357260_SKIP_T163_IN_READ_SCRN,
            'RUN_T250'          : 1,
            'CHK_AVG_BER'       : testSwitch.CheckAverageQBER_Enabled and not self.params.get('OTF', 0),
            'CHK_DELTA_BER'     : not testSwitch.DeltaBER_Disabled,
            'HD_INSTB_SCRN_SOVA': testSwitch.ENABLE_SCRN_HEAD_INSTABILITY_BY_SOVA_DATA_ERR,
            'HD_INSTB_SCRN_V2'  : testSwitch.ENABLE_DATA_COLLECTION_IN_READSCRN2_FOR_HEAD_INSTABILITY_SCRN or \
                                    testSwitch.ENABLE_THERMAL_SHOCK_RECOVERY_V2,
            'SAVE_T250'         : testSwitch.EnableT250DataSavingToSIM and not self.params.get('OTF', 0),
            'DELTA_VGA'         : testSwitch.DeltaVGA_Enabled,
            'CHK_MR_RST_DELTA'  : 1,
            'RUN_SKIPWRITE_SCRN': testSwitch.RUN_SKIPWRITE_SCRN,
            'HANDLE_EC_10632'   : not self.params.get('OTF', 0) and testSwitch.RD_SCRN2_FAIL_RERUN_ZAP,
         }

class CDeltaMRRes(CState) :
      #-------------------------------------------------------------------------------------------------------
      def __init__(self, dut, params={}):
         self.params = params
         depList = []
         CState.__init__(self, dut, depList)
      #-------------------------------------------------------------------------------------------------------
      def run(self):
         from RdWr import CMrResFile

         #=== Perform MR resistance delta check
         if testSwitch.FE_0173493_347506_USE_TEST321 and testSwitch.extern.SFT_TEST_0321:
            oMrRes = CMrResFile(TP.get_MR_Resistance_321, TP.mrDeltaLim)
         else:
            oMrRes = CMrResFile(TP.get_MR_Values_186, TP.mrDeltaLim)
         oMrRes.diffMRValues()

############################################################################################################
class CSQZWrite(CDeltaRSSScreen):
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CDeltaRSSScreen.__init__(self, dut, self.params)
   
   def loadActions(self):
      self.actions = {
         'RUN_T163'          : 0,
         'RUN_T250'          : 1,
         'CHK_AVG_BER'       : 0,
         'CHK_DELTA_BER'     : 0,
         'HD_INSTB_SCRN_SOVA': 0,
         'HD_INSTB_SCRN_V2'  : 0,
         'SAVE_T250'         : 0,
         'DELTA_VGA'         : 0,
         'CHK_MR_RST_DELTA'  : 0,
         'RUN_SKIPWRITE_SCRN': 0,
         'HANDLE_EC_10632'   : 0,
         'OTF'               : 0,
         'SQZ_WRITE'         : 1,
         'spc_id'            : TP.SqzWrite_SPC_ID,
         'MIN_SOVA'          : TP.MIN_SOVA_SQZ_WRT,
         'ODD_ZONES'         : 0,
         'SCREEN_OTF'        : testSwitch.FE_0261598_504159_SCREEN_OTF, 
         'MAX_ERR_RATE'      : -80,
      }


############################################################################################################
class CEnaFAFH(CState):
   """
      Description:
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from serialScreen import sptDiagCmds
      import serialScreen, sptCmds
      self.oSerial = sptDiagCmds()
      timeoutbyhd = self.dut.imaxHead * 100
      objPwrCtrl.powerCycle()
      time.sleep(10) # additional delay for FAFH
      self.oSerial.enableDiags()
      self.oSerial.gotoLevel('H')
      sptCmds.sendDiagCmd("f6,8002,5",timeout = timeoutbyhd, printResult = True, loopSleepTime=0.5)   # enable fafh trigger
      #self.oSerial.gotoLevel('H')
      #sptCmds.sendDiagCmd("f6,2,1B,0,D",timeout = timeoutbyhd, printResult = True, loopSleepTime=0.5) #enable clr compensation
      #if testSwitch.FE_0246774_009408_DIS_HD_RES_MEAS_BY_FAFH_ST_MACH:
         #self.oSerial.gotoLevel('H')
         #sptCmds.sendDiagCmd("f6,2,1f",timeout = timeoutbyhd, printResult = True, loopSleepTime=0.5)
      sptCmds.enableESLIP()


############################################################################################################
class CRunT315(CState):
   """
      Run T315_1, T315_2, T315_3, T315_4, T315_SUM
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if testSwitch.RUN_TEST_315:
         from Process import CProcess
         self.oProc = CProcess()
         t315_hd_instab_det = 0
         try:
            if self.dut.currentState in ['RUN_T315_1']:
               self.oProc.St(TP.prm_T315_RESET)
            self.oProc.St(TP.prm_T315_Data)
            if testSwitch.ENABLE_T315_SCRN:
               objMsg.printMsg('========= T315 screening =========')
               tableData = []
               
               try:
                  tableData = self.dut.dblData.Tables('P315_INSTABILITY_METRIC').tableDataObj()
               except: 
                   objMsg.printMsg("P315_INSTABILITY_METRIC not found!!!!!")
                   pass
               if len(tableData) > 0:
                  for row in tableData:
                      iHead = int(row['HD_LGC_PSN'])
                      hd_metric = int(row['HD_INSTABILITY_METRIC'])
                      if(hd_metric >= TP.t315_hd_instability_spec):
                        t315_hd_instab_det = 1
                        objMsg.printMsg("T315 screening failed!: HD_INSTABILITY_METRIC >= %d" % (TP.t315_hd_instability_spec))
                        
            #self.oProc.St(TP.prm_T315_SUM)
         except:
            objMsg.printMsg("T315 failed at state: %s" % TP.prm_T315_Data['FILE_ID'])
            objPwrCtrl.powerCycle()
            pass
         if testSwitch.ENABLE_T315_SCRN:
            if t315_hd_instab_det == 1:
               import ScrCmds
               ScrCmds.raiseException(11126, "Head instability check failed for T315, cannot downgrade: HD_INSTABILITY_METRIC >= %d" % (TP.t315_hd_instability_spec))

      else:
         objMsg.printMsg("Skipping T315 state: %s" % TP.prm_T315_Data['FILE_ID'])

