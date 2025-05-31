#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Base RAP access states
#
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/09/30 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_RAP.py $
# $Revision: #2 $
# $DateTime: 2016/09/30 02:58:41 $
# $Author: yihua.jiang $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_RAP.py#2 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
from State import CState
import MessageHandler as objMsg

verbose = 0 # Set to a value greater than 0 for various levels of debug output in the log.


#----------------------------------------------------------------------------------------------------------
class CInitRAP(CState):
   """
      Description: Class that will initialize the RAP.  Only to be performed very early in PRE2.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params

      if dut.nextOper == 'PRE2':
         depList = ['HEAD_CAL', 'MDW_CAL']
      else:
         depList = []

      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from PreAmp import CPreAmp
      from AFH import CdPES

      oPreamp = CPreAmp()
      if not testSwitch.WA_0111638_231166_DISABLE_SETTING_OF_PREAMP_HEATER_MODE:
         oPreamp.setPreAmpHeaterMode(TP.setPreampHeaterMode_178, TP.PRE_AMP_HEATER_MODE)
      oPreamp = None  # Allow GC

      odPES = CdPES(TP.masterHeatPrm_11, TP.defaultOCLIM)
      if testSwitch.BF_0128273_341036_AFH_DEPOP_HEAD_SUPPORT_AFH_SIM == 1:
         odPES.frm.reinitialize_CAFH_SIM()
      odPES.frm.clearCM_SIM_method( 1 )
      odPES = CdPES(TP.masterHeatPrm_11, TP.defaultOCLIM)
      if 'CoeffTrackingNo' in TP.clearance_Coefficients:
         objMsg.printMsg("Coefficient Tracking Number = %s" % TP.clearance_Coefficients['CoeffTrackingNo'])
      if testSwitch.HAMR:
         odPES.setIRPCoefs(self.dut.PREAMP_TYPE, self.dut.AABType, TP.PRE_AMP_HEATER_MODE, TP.clearance_Coefficients, forceRAPWrite = 1, hrmAddC0WitC1 = 0)
      else:
         odPES.setIRPCoefs(self.dut.PREAMP_TYPE, self.dut.AABType, TP.PRE_AMP_HEATER_MODE, TP.clearance_Coefficients, forceRAPWrite = 1)

      odPES.St({'test_num':172, 'prm_name':'AFH PTP Coef Dump', 'timeout': 1800, 'CWORD1': (15,), 'spc_id':3})

      if testSwitch.FE_0169232_341036_ENABLE_AFH_TGT_CLR_CANON_PARAMS == 1:
         from AFH_canonParams import *
         afhZoneTargets = getTargetClearance()
      else:
         afhZoneTargets = TP.afhZoneTargets

      
      MediaPartNum1 = DriveAttributes.get('MEDIA_PART_NUM', None)
      MediaPartNum2 = DriveAttributes.get('MEDIA_PART_NU_2', None)
      objMsg.printMsg("m1 = %s, m2 = %s" %(MediaPartNum1,MediaPartNum2))
      if self.dut.BG in ['SBS'] and MediaPartNum1 != None and MediaPartNum2 != None and MediaPartNum1 != MediaPartNum2:
         UVMediaBackup = self.dut.UVProcess   
         isUVMediaofDisc2 = int(MediaPartNum2, 10) in TP.UV_MediaPartNum 
         odPES.setClearanceTargets(TP.afhTargetClearance_by_zone, afhZoneTargets, range(0, int(self.dut.numZones + 1)), hd = 0x03)
         if isUVMediaofDisc2:
            self.dut.UVProcess = True
            afhZoneTargets = TP.afhZoneTargets
            odPES.setClearanceTargets(TP.afhTargetClearance_by_zone, afhZoneTargets, range(0, int(self.dut.numZones + 1)), hd = 0x0C)
         else:
            self.dut.UVProcess = False
            afhZoneTargets = TP.afhZoneTargets
            odPES.setClearanceTargets(TP.afhTargetClearance_by_zone, afhZoneTargets, range(0, int(self.dut.numZones + 1)), hd = 0x0C)
         self.dut.UVProcess  = UVMediaBackup
      else:
         odPES.setClearanceTargets(TP.afhTargetClearance_by_zone, afhZoneTargets, range(0, int(self.dut.numZones + 1)))     
      odPES.St(TP.activeClearControl_178)
      odPES.setGammaHValues(self.dut.PREAMP_TYPE, self.dut.AABType, TP.clearance_Coefficients, TP.test178_gammaH)

      odPES = None # Allow GC


      if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT == 1:
         from AFH_Screens_DH import CAFH_Screens
      else:
         from AFH_Screens_T135 import CAFH_Screens
      # Save AFH TCC1 and TCC2 to RAP
      oAFH_Screens = CAFH_Screens()
      if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT == 1:
         from RAP import ClassRAP
         objRAP = ClassRAP()
         if testSwitch.FE_0169232_341036_ENABLE_AFH_TGT_CLR_CANON_PARAMS == 1:
            from AFH_canonParams import *
            tcc_DH_values = getTCS_values()
         else:
            tcc_DH_values = TP.tcc_DH_values
         for iHead in oAFH_Screens.headList:
            if not testSwitch.extern.FE_0157745_387179_AFH_TCS_WARP:
               objRAP.SaveTCC_toRAP( iHead, tcc_DH_values["WRITER_HEATER"]['TCS1'], tcc_DH_values["WRITER_HEATER"]['TCS2'], "WRITER_HEATER", tcc_DH_values )
               objRAP.SaveTCC_toRAP( iHead, tcc_DH_values["READER_HEATER"]['TCS1'], tcc_DH_values["READER_HEATER"]['TCS2'], "READER_HEATER", tcc_DH_values )
            else:
               objRAP.SaveTCC_toRAP( iHead, tcc_DH_values["WRITER_HEATER"]['TCS1'], tcc_DH_values["WRITER_HEATER"]['TCS2'], "WRITER_HEATER", tcc_DH_values, TP.TCS_WARP_ZONES.keys())
               objRAP.SaveTCC_toRAP( iHead, tcc_DH_values["READER_HEATER"]['TCS1'], tcc_DH_values["READER_HEATER"]['TCS2'], "READER_HEATER", tcc_DH_values, TP.TCS_WARP_ZONES.keys())
      else:
         for iHead in oAFH_Screens.headList:
            oAFH_Screens.SaveTCC_toRAP( iHead, TP.tccDict_178['TCS1'], TP.tccDict_178['TCS2'] )

      #Report temperature correction coefficients
      oAFH_Screens.St({'test_num':172, 'prm_name': 'Retrieve TC Coefficient', "CWORD1" : (10), 'spc_id': 1, })

      # Clearance Settling initialization.
      if testSwitch.extern.FE_0166430_341036_ENABLE_AFH_SELFTEST_CLEARANCE_SETTLING_SUPPORT == 1:
         from RAP import ClassRAP
         objRAP = ClassRAP()
         objRAP.initializeClearanceSettlingParams()
         objRAP.St( TP.test172_displayClearanceSettlingData )

      if testSwitch.FE_0159364_341036_FAFH_INIT_HIRP_RAP_CORR_REF_TRK == 1:
         oAFH_Screens.St(TP.fafhInitializeReferenceTrackCorrespondingHIRP_values_074_05)

      if testSwitch.FE_0174845_379676_HUMIDITY_SENSOR_CALIBRATION:
         from RAP import ClassRAP
         objRAP = ClassRAP()
         objRAP.initializeHCSParams(self.dut.PREAMP_TYPE, self.dut.AABType, TP.clearance_Coefficients)

      if testSwitch.extern.FE_0174634_404368_PREAMP_TRISE_IN_RAP or testSwitch.extern.FE_0192143_393174_PREAMP_WRITE_RISE_TIME:
         from RAP import ClassRAP
         objRAP = ClassRAP()
         objRAP.initializeTRiseValues(self.dut.PREAMP_TYPE, self.dut.AABType, TP.clearance_Coefficients)

      from VBAR_RAP import CRapTcc
      cVBAR = CRapTcc()
      cVBAR.updateWP(hd=0, zn=0, wp = 2, working_set = 0, setAllZonesHeads = 1, stSuppress=0) # Updates all zones and heads for defaults based on pre-amp type
      if verbose: cVBAR.printWpTable() #reduce test log

      from FSO import CFSO
      oFSO = CFSO()
      oFSO.saveRAPtoFLASH()
      oFSO.getWritePowers(supressOutput = not testSwitch.extern.FE_0255966_357263_T172_AFH_SUMMARY_TBL)
      cVBAR.updateDblogWpTable()
      
      # HAMR Related.
      if testSwitch.HAMR:
         oAFH_Screens.St(TP.prm_172_HamrPreampTable, spc_id=150)
         oAFH_Screens.St(TP.prm_172_HamrWorkingTable,spc_id=150) 
         oAFH_Screens.St(TP.prm_172_display_AFH_target_clearance)  
         oAFH_Screens.St(TP.prm_172_display_AFH_adapts_summary)
         prm = TP.prm_172_display_AFH_adapts_summary.copy()
         prm['CWORD1'] = 4
         oAFH_Screens.St(prm)
         oAFH_Screens.St({'test_num':172,'timeout': 1800, 'spc_id': 11001, 'CWORD1': 20}) #P172_CLR_COEF_ADJ
         oAFH_Screens.St({'test_num':172,'timeout': 12000.0, 'CWORD1': 9}) # Display RAP
         oAFH_Screens.St({'test_num':172,'timeout': 12000.0, 'CWORD1': 0}) # Display SAP


      if testSwitch.virtualRun and testSwitch.extern.FE_0164615_208705_T211_STORE_CAPABILITIES:
         from SIM_FSO import CSimpleSIMFile
         CSimpleSIMFile("VBAR_DATA").clearCache()
#----------------------------------------------------------------------------------------------------------
class CWpTriplets(CState):
   """
      Description: Class that will set Default Write Power Triplets in RAP. 
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params

      depList = []

      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      """
         set Write Power Triplets to default TP
      """
      from VBAR_RAP import CRapTcc
      cVBAR = CRapTcc()
      cVBAR.updateWP(hd=0, zn=0, wp = 2, working_set = 0, setAllZonesHeads = 1, stSuppress=0) # Updates all zones and heads for defaults based on pre-amp type
      #cVBAR.printWpTable() #reduce test log
      # Update Flash
      from FSO import CFSO
      oFSO = CFSO()
      oFSO.saveRAPtoFLASH()
      from PowerControl import objPwrCtrl
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
