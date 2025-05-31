#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2009, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Feature_Release_Test_Switches Module
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/11/09 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Feature_Release_Test_Switches.py $
# $Revision: #5 $
# $DateTime: 2016/11/09 22:11:41 $
# $Author: kai.k.yang $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Feature_Release_Test_Switches.py#5 $
# Level: 3

#---------------------------------------------------------------------------------------------------------#
from Constants import *
import ScrCmds

#######################################################################################################################
#
#                   Purpose:  This is very analogous to the firmware header file feature.h which specifies flag
#                             settings based on the AFH Major and Minor revision numbers symbols
#
#                             AFH_MAJ_REL_NUM - major release number
#                             AFH_MIN_REL_NUM - minor release number
#
#                             The idea is for the PF3 code to auto-adapt the important AFH flag settings based on the
#                             version of the AFH firmware.  This is communicated through the following mechanism.
#
#                             In Drive Firmware Code
#                                1.) The 2 release number flags above are defined in the defaults_st.h file.
#                                2.) The product can choose to select an AFH release number
#                                3.) SF3/F3 flags are then specified according to the release numbers chosen.
#                                4.) The flags.py file is created from the flags.h file at build time.
#
#                             In PF3 Process code
#                                1.) The flags.py file is read in dynamically at run-time.
#
#######################################################################################################################


class CFeature_Release_Test_Switches:

   def __init__(self, testSwitchRef):

      #########################################################################################
      #
      #               Initialize for simulator only the system settings for various products.
      #
      #########################################################################################

      if testSwitchRef.virtualRun:
         # Load build target info
         from Constants import PF3_BUILD_TARGET
         buildTargetList = PF3_BUILD_TARGET.split(".")

         if len(buildTargetList) >= 1:
            programName = buildTargetList[0]
         else:
            programName = ""

         if len(buildTargetList) >= 2:
            programTarget = buildTargetList[1]
         else:
            programTarget = ""
         from TestParamExtractor import TP
         print ("TP.program=%s programName=%s" % (TP.program, programName))
         
         # Set VBAR block release level for VE
         if programName.upper() in ["KINTA", "LINGGI", "AMAZON"]:
            if testSwitchRef.SMR:
               testSwitchRef.extern.VBAR_MAJ_REL_NUM = 11
               testSwitchRef.extern.VBAR_MIN_REL_NUM = 0
            else:
               testSwitchRef.extern.VBAR_MAJ_REL_NUM = 10
               testSwitchRef.extern.VBAR_MIN_REL_NUM = 2
            #if TP.program in ["Rosewood7", "AngsanaH", "Angsana2D", "Angsana", "Chengai", "Angsana2DH"]:
            testSwitchRef.extern.POLY_ZAP = 1

         # Set VBAR MAJ and MIN REL NUMs below and uncomment, for VE change verification, but don't alter Desperado.
         #if programTarget not in ["DS7A"]:
         #   testSwitchRef.extern.VBAR_MAJ_REL_NUM = 10
         #   testSwitchRef.extern.VBAR_MIN_REL_NUM = 2

         # Set default AFH block release level for VE
         testSwitchRef.extern.AFH_MAJ_REL_NUM = 20
         testSwitchRef.extern.AFH_MIN_REL_NUM = 2

         # default for Luxor program in VE
         if ( programName == "Luxor" ):
            testSwitchRef.extern.AFH_MAJ_REL_NUM = 21
            testSwitchRef.extern.AFH_MIN_REL_NUM = 0

         if ( testSwitchRef.IS_DUAL_HEATER ):
            from Drive import objDut   # usage is objDut
            self.dut = objDut

            testSwitchRef.extern.AFH_MAJ_REL_NUM = 36
            testSwitchRef.extern.AFH_MIN_REL_NUM = 0

            self.dut.isDriveDualHeater = 1

         if TP.program in ["AngsanaH"] :
            testSwitchRef.extern.FAFH = 0
            testSwitchRef.extern.FAFH_MAJ_REL_NUM = 34
            testSwitchRef.extern.FAFH_MIN_REL_NUM = 0
            testSwitchRef.extern.FE_0147923_341036_FAFH_MASTER_ENABLE_T74_IN_PF3_PROCESS = 0
         if TP.program in ["Rosewood7", "Chengai"] :
            testSwitchRef.extern.FAFH = 1
            testSwitchRef.extern.FAFH_MAJ_REL_NUM = 36
            testSwitchRef.extern.FAFH_MIN_REL_NUM = 1
            testSwitchRef.extern.FE_0147923_341036_FAFH_MASTER_ENABLE_T74_IN_PF3_PROCESS = 1 # Need to enable the switch for VE

         testSwitchRef.extern.ABIE_MAJ_REL_NUM = 3
         testSwitchRef.extern.ABIE_MIN_REL_NUM = 3
            
         testSwitchRef.extern.FE_0202123_228373_KARNAK_YARRAR_LSI = 1
         testSwitchRef.extern.RW_FORMAT_APPLY_SECONDARY_ER_MODE = 1
         
         if TP.program in ["Rosewood7"]:
            testSwitchRef.extern.FE_0191285_496741_STRING_REPRESENTATION_OF_SIM_FILE                       = 1
            testSwitchRef.extern.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT                                  = 1
            testSwitchRef.extern.FE_0270095_504159_SUPPORT_LOOPING_ZONE_T178                               = 1
            testSwitchRef.extern.FE_0255966_357263_T172_AFH_SUMMARY_TBL                                    = 1
            testSwitchRef.extern.FE_0269440_496741_LOG_RED_P172_ZONE_TBL_SPLIT                             = 1            
            # ----- Test 321 to replace T186 -----
            testSwitchRef.FE_0173493_347506_USE_TEST321 = 1
            testSwitchRef.extern.SFT_TEST_0321 = 1
            # ----- Enable 504 Parity -----
            testSwitchRef.WA_0309963_504266_504_LDPC_PARAM = 1


         if testSwitchRef.SMR:
            testSwitchRef.extern._128_REG_PREAMPS                                                          = 1
            testSwitchRef.extern.SFT_TEST_0236                                                             = 1

         
         testSwitchRef.extern.ZAP_MAJ_REL_NUM = 9
         testSwitchRef.extern.ZAP_MIN_REL_NUM = 1

         testSwitchRef.extern.FE_0315265_228371_T134_SPEC_ADD_SYMBOL_LENTGTH_NO_CRITERIA                  = 1
#################### end of virtualrun flags
      
      ScriptComment("CFeature_Release_Test_Switches.__init__/ Using AFH Major System Release Number: %s,  Minor Release Number: %s"
         % ( testSwitchRef.extern.AFH_MAJ_REL_NUM, testSwitchRef.extern.AFH_MIN_REL_NUM ))

      ScriptComment("CFeature_Release_Test_Switches.__init__/ Using OPTI Major System Release Number: %s,  Minor Release Number: %s"
         % ( testSwitchRef.extern.OPTI_MAJ_REL_NUM, testSwitchRef.extern.OPTI_MIN_REL_NUM ))

      ScriptComment("CFeature_Release_Test_Switches.__init__/ Using VBAR Major System Release Number: %s,  Minor Release Number: %s"
         % ( testSwitchRef.extern.VBAR_MAJ_REL_NUM, testSwitchRef.extern.VBAR_MIN_REL_NUM ))

      ScriptComment("CFeature_Release_Test_Switches.__init__/ Using FLAWSCAN Major System Release Number: %s,  Minor Release Number: %s"
         % ( testSwitchRef.extern.FLAWSCAN_MAJ_REL_NUM, testSwitchRef.extern.FLAWSCAN_MIN_REL_NUM ))

      ScriptComment("CFeature_Release_Test_Switches.__init__/ Using SCRATCH_FILL Major System Release Number: %s,  Minor Release Number: %s"
         % ( testSwitchRef.extern.SCRATCH_FILL_MAJ_REL_NUM, testSwitchRef.extern.SCRATCH_FILL_MIN_REL_NUM ))

      ScriptComment("CFeature_Release_Test_Switches.__init__/ Using ZAP Major System Release Number: %s,  Minor Release Number: %s"
         % ( testSwitchRef.extern.ZAP_MAJ_REL_NUM, testSwitchRef.extern.ZAP_MIN_REL_NUM ))

      ScriptComment("CFeature_Release_Test_Switches.__init__/ Using ZEST Major System Release Number: %s,  Minor Release Number: %s"
         % ( testSwitchRef.extern.ZEST_MAJ_REL_NUM, testSwitchRef.extern.ZEST_MIN_REL_NUM ))

      ScriptComment("CFeature_Release_Test_Switches.__init__/ Using ZFS Major System Release Number: %s,  Minor Release Number: %s"
         % ( testSwitchRef.extern.ZFS_MAJ_REL_NUM, testSwitchRef.extern.ZFS_MIN_REL_NUM ))

      ScriptComment("CFeature_Release_Test_Switches.__init__/ Using FAFH Major System Release Number: %s,  Minor Release Number: %s"
         % ( testSwitchRef.extern.FAFH_MAJ_REL_NUM, testSwitchRef.extern.FAFH_MIN_REL_NUM ))

      if testSwitchRef.FE_0139178_399481_P_ADD_DFS_AND_TA_SCAN_TO_FEATURE_REV_DISPLAY or \
         testSwitchRef.extern.FE_0177600_007955_ADDITIONAL_T166_BLOCK_POINT_REPORTING:
         ScriptComment("CFeature_Release_Test_Switches.__init__/ Using DFS Major System Release Number: %s,  Minor Release Number: %s"
            % ( testSwitchRef.extern.DFS_MAJ_REL_NUM, testSwitchRef.extern.DFS_MIN_REL_NUM ))

         ScriptComment("CFeature_Release_Test_Switches.__init__/ Using TA Scan Major System Release Number: %s,  Minor Release Number: %s"
            % ( testSwitchRef.extern.TA_SCAN_MAJ_REL_NUM, testSwitchRef.extern.TA_SCAN_MIN_REL_NUM ))

      if testSwitchRef.FE_0146586_007955_P_ADD_RW_SCREEN_TO_FEATURE_REV_DISPLAY or \
         testSwitchRef.extern.FE_0177600_007955_ADDITIONAL_T166_BLOCK_POINT_REPORTING:
         ScriptComment("CFeature_Release_Test_Switches.__init__/ Using RW_SCREEN Major System Release Number: %s,  Minor Release Number: %s"
            % ( testSwitchRef.extern.RW_SCREEN_MAJ_REL_NUM, testSwitchRef.extern.RW_SCREEN_MIN_REL_NUM ))

      if testSwitchRef.extern.FE_0149151_350037_ENABLE_SDAT_MDW_DATA_SUPPORT or \
         testSwitchRef.extern.FE_0177600_007955_ADDITIONAL_T166_BLOCK_POINT_REPORTING:
         ScriptComment("CFeature_Release_Test_Switches.__init__/ Using SDAT Major System Release Number: %s,  Minor Release Number: %s"
            % ( testSwitchRef.extern.SDAT_MAJ_REL_NUM, testSwitchRef.extern.SDAT_MIN_REL_NUM ))

      ScriptComment("CFeature_Release_Test_Switches.__init__/ Using ABIE Major System Release Number: %s,  Minor Release Number: %s"
         % ( testSwitchRef.extern.ABIE_MAJ_REL_NUM, testSwitchRef.extern.ABIE_MIN_REL_NUM ))

      ScriptComment("CFeature_Release_Test_Switches.__init__/ Using Clr Settling Major System Release Number: %s,  Minor Release Number: %s"
         % ( testSwitchRef.extern.CLR_SETTLING_MAJ_REL_NUM, testSwitchRef.extern.CLR_SETTLING_MIN_REL_NUM ))

      ScriptComment("CFeature_Release_Test_Switches.__init__/ Using SERVO_BODE Major System Release Number: %s,  Minor Release Number: %s"
         % ( testSwitchRef.extern.SERVO_BODE_MAJ_REL_NUM, testSwitchRef.extern.SERVO_BODE_MIN_REL_NUM ))

      # end of __init__


   #########################################################################################
   #
   #               Function:  setSwitches
   #
   #        Original Author:  Michael T. Brady
   #
   #            Description:  Set the AFH "switches" to specified values based on the Major
   #                          and minor revision numbering scheme.
   #
   #                  Input:  testSwitchRef( a reference to the testSwitch singleton object)
   #
   #                 Return:  None
   #
   #########################################################################################

   def setSwitches( self, testSwitchRef ):

      # Note:  All feature flags controlled by meta-flags must be disabled by default.
      #        Also, bug fix flags should NOT be disabled by default.

      #
      try:
         from Drive import objDut   # usage is objDut
         self.dut = objDut

         currentOperation = self.dut.nextOper
      except:
         currentOperation = "None"



      testSwitchRef.FE_0117973_341036_AFH_BETTER_FRAMES_DISPLAY_OPTION                                = 0
      testSwitchRef.FE_0130770_341036_AFH_FORCE_SAVING_AFH_SIM_TO_DRIVE_ETF                           = 0
      testSwitchRef.FE_0130771_341036_AFH_FORCE_USE_AFH3_AND_AFH4_IN_TCS_CALC                         = 0
      testSwitchRef.FE_0136598_341036_AFH_PRVNT_INDX_ERROR_P_135_FINAL_CONTACT                        = 0

      #FAFH
      testSwitchRef.IS_FAFH = 1

      #########################################################################################
      #
      # Deprecated AFH Release numbers
      #
      #########################################################################################

      if testSwitchRef.extern.SFT_FIRMWARE and ((testSwitchRef.extern.AFH_MAJ_REL_NUM < 20) or \
         ((testSwitchRef.extern.AFH_MAJ_REL_NUM >= 30) and (testSwitchRef.extern.AFH_MAJ_REL_NUM < 35))  ):
         ScrCmds.raiseException(11044, "Deprecated AFH Release Number %s was used." % (testSwitchRef.extern.AFH_MAJ_REL_NUM))


      if testSwitchRef.extern.AFH_MAJ_REL_NUM >= 13:

         # Work-arounds
         testSwitchRef.WA_0111581_341036_AFH_RUN_AFH1_SCREENS_AFTER_HIRP                              = 1

         ScriptComment("setSwitches/ AFH Major version %s, Minor version %s set" % ( testSwitchRef.extern.AFH_MAJ_REL_NUM, testSwitchRef.extern.AFH_MIN_REL_NUM ))

         # end of if testSwitchRef.extern.AFH_MAJ_REL_NUM >= 13:

      # No PF3 changes for AFH_MAJ_REL_NUM = 14



      if (testSwitchRef.extern.AFH_MAJ_REL_NUM >= 19):

         # AFH clean-up flags

         # HIRP/WHIRP/191 flags

         # misc. PF3 flags
         testSwitchRef.FE_0117973_341036_AFH_BETTER_FRAMES_DISPLAY_OPTION                             = 1


      if (testSwitchRef.extern.AFH_MAJ_REL_NUM == 20) and (testSwitchRef.extern.AFH_MIN_REL_NUM == 2):
         testSwitchRef.FE_0127824_341036_AFH_DISABLE_WHIRP_NOT_CT_ACCESSIBLE                          = 1

      if (testSwitchRef.extern.AFH_MAJ_REL_NUM >= 21):
         testSwitchRef.FE_0127824_341036_AFH_DISABLE_WHIRP_NOT_CT_ACCESSIBLE                          = 1
         testSwitchRef.FE_0130770_341036_AFH_FORCE_SAVING_AFH_SIM_TO_DRIVE_ETF                        = 1
         testSwitchRef.FE_0130771_341036_AFH_FORCE_USE_AFH3_AND_AFH4_IN_TCS_CALC                      = (1 and testSwitchRef.AFH3_ENABLED)
         testSwitchRef.FE_0131890_341036_AFH_ADD_FOLDING_OF_TCS_CALC                                  = 1



      if (testSwitchRef.extern.AFH_MAJ_REL_NUM >= 22):
         pass


      # FROZEN
      if ( testSwitchRef.extern.AFH_MAJ_REL_NUM >= 30 ):
         testSwitchRef.IS_DH_CODE_ENABLED                                                             = 1

         testSwitchRef.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT                     = 1
         testSwitchRef.FE_0136598_341036_AFH_PRVNT_INDX_ERROR_P_135_FINAL_CONTACT                     = 1
         testSwitchRef.WA_0111581_341036_AFH_RUN_AFH1_SCREENS_AFTER_HIRP                              = 0  # intra-state clr chk should be disabled
         testSwitchRef.AFH_ENABLE_TEST135_OD_ID_ROLLOFF_SCREEN                                        = 0  # intra-state clr chk should be disabled


      # FROZEN
      if ( testSwitchRef.extern.AFH_MAJ_REL_NUM >= 31 ):
         pass

      if ( testSwitchRef.extern.AFH_MAJ_REL_NUM >= 32 ):

         testSwitchRef.FE_0139633_341036_AFH_NEW_PROGRAM_NAME_FUNCTION                                = 0

         testSwitchRef.FE_0139388_341036_AFH_DUAL_HEATER_V32_ABOVE                                    = 1
      
      if ( testSwitchRef.extern.AFH_MAJ_REL_NUM >= 33 ):

         testSwitchRef.FE_0140570_357263_T135_HEAT_ONLY_FULL_SEARCH                                   = 1
         testSwitchRef.FE_0142458_341036_AFH_NO_RETROACTIVELY_HIRP_ADJUST_NEG_CLR                     = 1
         testSwitchRef.FE_0294085_357595_P_CM_LOADING_REDUCTION                                       = 1



      if ( testSwitchRef.extern.AFH_MAJ_REL_NUM >= 34 ):
         testSwitchRef.FE_0143795_341036_AFH_CONS_CHK_SUPPORT_FOR_SINGLE_HTR_MODE                     = 1

         # This should stay disabled until we are ready to check-in and run in the oven.

      if ( testSwitchRef.extern.AFH_MAJ_REL_NUM >= 34 ):
         testSwitchRef.FE_0143000_341036_AFH_CONS_CHK_3RD_GEN_PHASE_2                                 = 1

      ##################################################################################################################
      #
      # Safety check for the V34 to V35 transition to ensure that firmware and process are kept in sync.
      #
      # Python equivalent of assert statements to ensure these flags are enabled in the Test_Switches.py
      # they can't be enabled here as this file is set after these flags are referenced in modules that are imported
      # before this code in Feature_Release_Test_Switches.py is executed.
      #
      ##################################################################################################################
      if ( currentOperation in ['PRE2', 'CAL2']) and ( testSwitchRef.extern.SFT_FIRMWARE == 1):
         if ( testSwitchRef.extern.AFH_MAJ_REL_NUM == 34 ) and (testSwitchRef.AFH_V35 == 1):
            ScrCmds.raiseException(11044, 'ASSERT Fail VE - flag AFH_V35 needs to be disabled in Test_Switches.py for AFH version 34.')

         if ( testSwitchRef.extern.AFH_MAJ_REL_NUM == 35 ) and (not (testSwitchRef.AFH_V35 == 1)):
            ScrCmds.raiseException(11044, 'ASSERT Fail VE - flag AFH_V35 needs to be enabled in Test_Switches.py for AFH version 35.')

         #
      #

      if ( testSwitchRef.extern.AFH_MAJ_REL_NUM >= 35 ) and ( testSwitchRef.extern.SFT_FIRMWARE == 1):

         if (not (testSwitchRef.AFH_ENABLE_ANGSTROMS_SCALER_USE_254 == 1)):
            ScrCmds.raiseException(11044, 'Flag AFH_ENABLE_ANGSTROMS_SCALER_USE_254 needs to be enabled in Test_Switches.py for AFH version 35.')


         if (not (testSwitchRef.FE_0147357_341036_AFH_T172_FIX_TRUNK_MERGE_CWORD1_31 == 1)):
            ScrCmds.raiseException(11044, 'Flag FE_0147357_341036_AFH_T172_FIX_TRUNK_MERGE_CWORD1_31 needs to be enabled in Test_Switches.py for AFH version 35.')

         if (not (testSwitchRef.FE_0148582_341036_AFH_WHIRP_V35_CHANGE_VALUES == 1)):
            ScrCmds.raiseException(11044, 'Flag FE_0148582_341036_AFH_WHIRP_V35_CHANGE_VALUES needs to be enabled in Test_Switches.py for AFH version 35.')


      if ( testSwitchRef.extern.AFH_MAJ_REL_NUM >= 35 ):


         testSwitchRef.FE_0127824_341036_AFH_DISABLE_WHIRP_NOT_CT_ACCESSIBLE                          = 1 ## Angsanah want to enable Hirp only 0
         testSwitchRef.BF_0150006_341036_AFH_DH_RETROACTIVE_ADJUST_AFH1_PREHEAT                       = 1
         testSwitchRef.BF_0187702_340210_SNGL_HTR_2_PASS                                              = ( 1 and  (not testSwitchRef.FE_0127824_341036_AFH_DISABLE_WHIRP_NOT_CT_ACCESSIBLE ) and (not testSwitchRef.extern.FE_0256634_357263_T191_SEPARATE_HIRP_WHIRP_HEAT_DACS))

      if ( testSwitchRef.extern.AFH_MAJ_REL_NUM == 35 ) and ( testSwitchRef.extern.AFH_MIN_REL_NUM >= 2 ):
         testSwitchRef.FE_0158373_341036_ENABLE_AFH_LIN_CAL_BEFORE_READER_HEATER                      = 1

      if ( testSwitchRef.extern.AFH_MAJ_REL_NUM == 35 ) and ( testSwitchRef.extern.AFH_MIN_REL_NUM >= 3 ):
         testSwitchRef.FE_0158373_341036_ENABLE_AFH_LIN_CAL_BEFORE_READER_HEATER                      = 0

      if ( testSwitchRef.extern.AFH_MAJ_REL_NUM == 35 ) and ( testSwitchRef.extern.AFH_MIN_REL_NUM >= 4 ):
         if not (testSwitchRef.IS_FAFH):
            testSwitchRef.FE_0163822_341036_AFH_DISABLE_VCAT_FOR_T135                                 = 0

      if ( testSwitchRef.extern.AFH_MAJ_REL_NUM >= 36 ):
         testSwitchRef.FE_0158373_341036_ENABLE_AFH_LIN_CAL_BEFORE_READER_HEATER                      = 0

         if not (testSwitchRef.IS_FAFH):
            testSwitchRef.FE_0163822_341036_AFH_DISABLE_VCAT_FOR_T135                                 = 0

         testSwitchRef.FE_0165920_341036_DISABLE_READER_HEATER_CONTACT_DETECT_AFH2                    = 0   # ScPk Change: Force to 0
         testSwitchRef.FE_0165687_341036_AFH_SKIP_DELTA_VBAR_CHK_AFH2B_READER_HTR                     = 1   # For DH skip DELTA VBAR check only in AFH2B for the READER_HEATER

      if testSwitchRef.virtualRun: #setting flags
         testSwitchRef.extern.FE_0139388_341036_AFH_DUAL_HEATER_V32_ABOVE                             = (testSwitchRef.extern.AFH_MAJ_REL_NUM >= 32 )
         testSwitchRef.extern.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT              = (testSwitchRef.extern.AFH_MAJ_REL_NUM >= 30 )
      
      if not (testSwitchRef.IS_FAFH): #Tidy up to prevent mismatch
         testSwitchRef.FE_AFH3_TO_IMPROVE_TCC                                                         = testSwitchRef.extern.FE_0243165_322482_REAFH3

      if ( testSwitchRef.extern.FE_0274637_496738_DC_DETCR_DSA_CONTACT_DETECTION == 1 ):
         testSwitchRef.FE_0274637_496738_P_DC_DETCR_DSA_CONTACT_DETECTION                             = 1

      if ( testSwitchRef.extern.FE_0278186_496738_WRT_CUR_REDUCTION_TO_AVOID_STE == 1 ):
         testSwitchRef.FE_0278186_496738_P_WRT_CUR_REDUCTION_TO_AVOID_STE                             = 1

      #########################################################################################
      #
      # clearance settling
      #
      #########################################################################################

      if (testSwitchRef.extern.CLR_SETTLING_MAJ_REL_NUM >= 3):
         if not testSwitchRef.CALCULATE_THS:
            ScrCmds.raiseException(11044, 'Flag CALCULATE_THS needs to be enabled in Test_Switches.py for clr settling version 3.')
         testSwitch.FE_0169221_007867_VBAR_ADD_SETTLING_CLR_CALC = 1 # Calculate the amount of settling correction for poor-man's settling code

      # Future versions
      # Only enable FE_0121797_341036_AFH_USE_T109_FOR_TEST_135_TRACK_CLEANUP if SF3 flags
      # FE_0115820_000630_LBA_MODE_TEST_SUPPORT and FE_0120362_000630_LBA_MODE_UPDATES are set per Magill's question and my assumption.


      # FAFH

      if testSwitchRef.extern.FAFH_MAJ_REL_NUM >= 5 and testSwitchRef.IS_FAFH:
         testSwitchRef.FE_AFH3_TO_IMPROVE_TCC                                                         = 0
         testSwitchRef.AFH3_ENABLED                                                                   = 1
         testSwitchRef.DISPLAY_FAFH_PARAM_FILE_FOR_DEBUG                                              = 1


      if ( testSwitchRef.extern.FE_0147923_341036_FAFH_MASTER_ENABLE_T74_IN_PF3_PROCESS == 1 ):
         testSwitchRef.FE_0145389_341036_FAFH_ENABLE_FREQUENCY_SELECT_CAL                             = 1
         testSwitchRef.FE_0145391_341036_FAFH_ENABLE_T191_USE_T74_CAL_FREQ                            = 1
         testSwitchRef.FE_0145400_341036_FAFH_ENABLE_TRACK_PREP                                       = 1
         testSwitchRef.FE_0145412_341036_FAFH_ENABLE_AR_MEASUREMENT                                   = 1
         testSwitchRef.ENABLE_FAFH_STATE_CHECKING                                                     = 1
         testSwitchRef.FE_0151344_341036_FAFH_ENABLE_T135_FAFH_SPECIFIC_PARAMS                        = 1
         testSwitchRef.FE_0159364_341036_FAFH_INIT_HIRP_RAP_CORR_REF_TRK                              = 1

      if testSwitchRef.extern.FAFH_MAJ_REL_NUM >= 35 and testSwitchRef.IS_FAFH:
         testSwitchRef.FE_AFH3_TO_IMPROVE_TCC                                                         = 1 #AFH3 by exception
         testSwitchRef.AFH3_ENABLED                                                                   = 0
         
      #####################################################################################################################################
      ###
      ###   List of PF3 Flags not yet enabled.
      ###   Note these must remain commented-out!!!
      ###   ------------------------------------------------------------------------------------------------
      ###
      ###
      ###
      #####################################################################################################################################



         ###############
###################################################### VBAR SECTION #####################################################################
         ###############

      # Combine the release numbers for readability
      vbarRelNum = testSwitchRef.extern.VBAR_MAJ_REL_NUM * 10 + testSwitchRef.extern.VBAR_MIN_REL_NUM

      # VBAR 5.0
      # Flags removed

      # VBAR 5.1
      # Flags removed

      # VBAR 5.2
      # Flags removed

      # VBAR 5.3
      # No PF3 flags

      # VBAR 5.4
      # Flags removed

      # VBAR 5.5
      # Flags removed

      # VBAR 6.0
      # Flags removed

      # VBAR 6.1
      # Flags removed

      # VBAR 8.0
      testSwitchRef.FE_0161887_007867_VBAR_REDUCE_T255_LOG_DUMPS                                   = (vbarRelNum >= 80) # Eliminate the test 255 dumps prior to the opti call and skip reporting of P255_NPML_TAP0_1_LSI_DATA, P255_NPML_TAP2_3_LSI_DATA, and P255_NPML_BIAS_LSI_DATA

      # VBAR 10.0
      testSwitchRef.FE_0166516_007867_PF3_VBAR_CONSOLIDATED_T211_CALLS                             = (vbarRelNum >= 100) # Consolidate Test 211 calls for multiple heads and zones to reduce CM loading and log file size.

      # VBAR 10.1
      testSwitchRef.FE_0171570_208705_HMS_MARGIN_RAIL                                              = (vbarRelNum >= 101) # HMS margin only includes the measured settle amount if it is positive

      # VBAR 10.2
      testSwitchRef.BF_0170582_208705_BPI_NOMINAL_CAPS                                             = (vbarRelNum >= 102) # Force format reset before BPI Nominal measurements.
      testSwitchRef.FE_0168027_007867_USE_PHYS_HDS_IN_VBAR_DICT                                    = (vbarRelNum >= 102) # Use physical rather than logical head indexing in the VBAR meas dictionary so Depop on the Fly will function correctly.
      testSwitchRef.FE_0171684_007867_DISPLAY_PICKER_AS_TBL                                        = (vbarRelNum >= 102) # Convert textual picker data into DBLog Table data.
      testSwitchRef.FE_0172018_208705_P_ENABLE_HMS_2PT                                             = (vbarRelNum >= 102) # VBAR HMS:  Enable 2-point crossing algo in T211

      # Release checking
      if getattr(testSwitchRef, "VBAR_HMS_V4", 0) and testSwitchRef.extern.SFT_FIRMWARE and vbarRelNum < 80:
         ScrCmds.raiseException(11044, 'VBAR HMS Phase 4 requires VBAR 8.0')

      # Set up SF3 flags for VE
      if testSwitchRef.virtualRun:
         testSwitchRef.extern.FE_0155563_208705_FIX_DUPLICATE_REGIDS                                  = (vbarRelNum >= 71)
         testSwitchRef.extern.FE_0155984_208705_VBAR_HMS_BER_PENALTY                                  = (vbarRelNum >= 71)
         testSwitchRef.extern.FE_0164615_208705_T211_STORE_CAPABILITIES                               = (vbarRelNum >= 80)
         testSwitchRef.extern.FE_0116328_231166_SAVE_RETR_NPT_TARGET_DATA_FROM_SIM                    = (vbarRelNum >= 80)
         testSwitchRef.extern.FE_0125575_357552_SAVE_GMR_RES_RANGE_TO_SIM                             = (vbarRelNum >= 80)
         testSwitchRef.extern.BF_0168996_007867_VBAR_REPLACE_INACCURATE_WP_TBL                        = (vbarRelNum >= 101)
         testSwitchRef.extern.FE_0158806_007867_T210_TPI_SMR_SUPPORT                                  = (vbarRelNum >= 110)  # This feature should not be enabled as a VBAR SF3 Release, so 90 was changed to 900
         testSwitchRef.extern.FE_0161563_208705_TPI_FMT_RELATIVE_UNITS                                = (vbarRelNum >= 110)  # This feature should not be enabled as a VBAR SF3 Release, so 90 was changed to 900
         if testSwitch.TRUNK_BRINGUP or testSwitch.ROSEWOOD7:
            testSwitchRef.extern.SFT_TEST_0271                                                        = 1                    # Turn on the T271 OTC measurement
         if testSwitch.ROSEWOOD7:
            testSwitchRef.extern.PROD_BY_HEAD_BPI_BIN_SUPPORT                                         = 1                    # Turn on SIF
            testSwitchRef.extern.PROD_SIGMUND_IN_FACTORY_SUPPORT                                      = 1                    # Turn on SIF
            testSwitchRef.extern.WA_0300067_504266_4K_SECTOR_MARKOV_SUPPORT                           = 1                    # Turn on MARKOV SUPPORT
            testSwitchRef.extern.ENABLE_SEL_ZONE                                                      = 1                    # Turn on SEL_ZONE
            testSwitchRef.extern.FE_0313488_228371_T238_FASTIO_DATA_VGA_SUPPORT                       = 1                    # Turn on FASTIO_DATA_VGA_SUPPORT
         ###############
###################################################### ZFS SECTION #####################################################################
         ###############

      if testSwitchRef.virtualRun:
         testSwitchRef.extern.ZFS_MAJ_REL_NUM = 0   # Disable ZFS for VE
         testSwitchRef.extern.ZFS_MIN_REL_NUM = 0
         ScriptComment("setSwitches/ ZFS Major version %s, Minor version %s set" % ( testSwitchRef.extern.ZFS_MAJ_REL_NUM, testSwitchRef.extern.ZFS_MIN_REL_NUM ))

      if (testSwitchRef.extern.ZFS_MAJ_REL_NUM >= 1):            # Rev 1.0 and above enables ZFS
         testSwitchRef.ZFS                                                          = 1
         testSwitchRef.ZFS_LEGACY_MODE                                              = 1
         testSwitchRef.FE_SGP_81592_PWRCYCLE_RETRY_WHEN_T175_REPORT_EC11087_IN_ZAP  = 0 # Added pwr cycle n retry once if Test 175 reported EC11087 (hang) in FNC2 ZAP state.
         testSwitchRef.SWD_CAL_AFTER_ZAP                                            = 0
         testSwitch.FE_0123768_426568_OUTPUT_SERVO_COUNTERS_DURING_FLAWSCAN         = 0
         ScriptComment("T275 is on")

      if (testSwitchRef.extern.ZFS_MAJ_REL_NUM >= 4):            # Rev 1.0 and above enables ZFS
         testSwitchRef.TOPAZ_DRZAP_ENABLE                                           = 1
         ScriptComment("SF3 DrZAP & TOPAZ Enabled")
         
         ### end ZFS section

         ###############
###################################################### ZAP SECTION #####################################################################
         ###############

      if testSwitchRef.virtualRun:
         testSwitchRef.extern.FE_0253057_350037_EXTEND_GAP_CAL_SUPPORT = 1 # Syncless zap

      testSwitchRef.FE_0122823_231166_ALLOW_SWITCH_REFS_IN_TP                                         = 1   # Allow switch refs in Test Parameter resolution

      if (testSwitchRef.extern.ZAP_MAJ_REL_NUM > 1):                 # warning: these test switch settings will over-ride Test_Switches.py
         testSwitchRef.FE_0125510_209214_ZAP_PARAMETER_CLEANUP_1                                      = 1   # cleanup and simplify the zap parameters. First revision.
         testSwitchRef.BF_0120661_357260_ENABLE_ZAP_DURING_INIT_FS                                    = 1
         testSwitchRef.FE_0110811_320363_DISABLE_SHOCK_SENSOR_IN_ZAP                                  = 0
         testSwitchRef.FE_0113059_357260_APPLY_IVBARZAP_TO_OPTIZAP                                    = 1
         testSwitchRef.FE_0118779_357260_SAVE_SLIST_IN_ZAP                                            = 1
         testSwitchRef.FE_0122125_7955_DISABLE_OPTIZAP_RUN_BEFORE_T250                                = 0
         testSwitchRef.FINE_OPTI_ZAP_ENABLED                                                          = 1
         if not testSwitchRef.DISABLE_T250_SER_ZAP:
            testSwitchRef.T250_SER_ZAP                                                                = 1
         else:
            testSwitchRef.T250_SER_ZAP                                                                = 0
         testSwitchRef.WA_0110971_009438_POWER_CYCLE_AT_ZAP_START                                     = 0
         testSwitchRef.FE_0120496_231166_DISABLEZAP_IN_MDWCALS                                        = 0
         testSwitchRef.BF_0119055_231166_USE_SVO_CMD_ZAP_CTRL                                         = 0

      if (testSwitchRef.extern.ZAP_MAJ_REL_NUM >= 3):                                                      # Rev 3.0 disables uJog ZAP in CAL2
         testSwitchRef.FINE_OPTI_ZAP_ENABLED                                                          = 0

      if (testSwitchRef.extern.ZAP_MAJ_REL_NUM >= 4):                                                      # Rev 4.0 adjusts the number of tracks zapped in the special zap ranges (VBAR, System area, uJog, opti)
         testSwitchRef.FE_0132665_209214_ZAP_PARAMETER_CLEANUP_2                                      = 1

      if (testSwitchRef.extern.ZAP_MAJ_REL_NUM == 4) and (testSwitchRef.extern.ZAP_MIN_REL_NUM == 1):      # Rev 4.1 enables uJog ZAP in CAL2
         testSwitchRef.FINE_OPTI_ZAP_ENABLED                                                          = 1
         # Rev 5.0 enables write ZAP for all system area writes (SF3 only)

      if (testSwitchRef.extern.ZAP_MAJ_REL_NUM >= 6):                                                      # Rev 6.0 Use fixed ZGAIN during full surface zap.
         testSwitchRef.FE_0150178_209214_ZAP_USE_FIXED_ZGAIN                                          = 1

      if (testSwitchRef.extern.ZAP_MAJ_REL_NUM == 9) and (testSwitchRef.extern.ZAP_MIN_REL_NUM == 1):      # Rev 4.1 enables uJog ZAP in CAL2
         testSwitchRef.FINE_OPTI_ZAP_ENABLED                                                          = 1

### end ZAP section

         ###############
###################################################### PRISM/ZEST SECTION #####################################################################
         ###############

      if testSwitchRef.virtualRun:
         testSwitchRef.extern.ZEST_MAJ_REL_NUM = 0   # Disable PRIMS/ZEST for VE
         testSwitchRef.extern.ZEST_MIN_REL_NUM = 0
         ScriptComment("setSwitches/ ZEST Major version %s, Minor version %s set" % ( testSwitchRef.extern.ZEST_MAJ_REL_NUM, testSwitchRef.extern.ZEST_MIN_REL_NUM ))

      if (testSwitchRef.extern.ZEST_MAJ_REL_NUM >= 1):                                                      # Rev 1.0 and above enables PRISM/ZEST
         testSwitchRef.ZEST                                                                           = 1

### end ZEST section




         ###############
###################################################### SDAT FEATURES SECTION #####################################################################
         ###############


      if (testSwitchRef.extern.SDAT_MAJ_REL_NUM >= 1):     # Rev 1.0 and above enables SDAT features / improvements
         testSwitchRef.BF_0121115_010200_REMOVE_UNNECESSARY_T150_CALLS_IN_SDAT                          = 1
         testSwitchRef.FE_0126858_010200_SDAT_ROBUSTNESS_IMPROVEMENTS                                   = 1

#### end SDAT features section


         ###############
###################################################### SERVO BODE FEATURES SECTION ###############################################################
         ###############

      # Rev 1.0 or higher: enable manifest driven Sensitivity Scoring mode selection.
      # If servo release package includes a binary sensitivity limit file, use T282 to check sensitity margins.
      if (testSwitchRef.extern.SERVO_BODE_MAJ_REL_NUM >= 1):
         testSwitchRef.FE_0142952_010200_SFW_PKG_BIN_SENSITIVITY_SCORING_LIMITS                         = 1
         testSwitchRef.FE_0156514_357260_P_SERVO_FILES_IN_MANIFEST                                      = 1
         testSwitchRef.BF_0163537_010200_CONSISTENT_PKG_RES_NO_FILE_FOUND_RESPONSE                      = 1
 
#### end SERVO BODE features section

         ###############
###################################################### Enable Script test switch using extern flag ###############################################
         ###############

      if testSwitchRef.extern.FE_0253166_504159_MERGE_FAT_SLIM:
         testSwitchRef.FE_0253166_504159_MERGE_FAT_SLIM                                                 = 0
      if testSwitchRef.extern.FE_0191285_496741_STRING_REPRESENTATION_OF_SIM_FILE:
         ScriptComment("Extern Switches of %s is on" % ("FE_0191285_496741_STRING_REPRESENTATION_OF_SIM_FILE") )
      if testSwitchRef.ROSEWOOD7 or testSwitchRef.M11P_BRING_UP or testSwitchRef.M11P: #link TA supported switchs
         testSwitchRef.FE_0173493_347506_USE_TEST321 = testSwitchRef.extern.SFT_TEST_0321
      testSwitchRef.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT = testSwitchRef.extern.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT 
      ### Link sigmund sf3 flag to turn on PF3 switch
      testSwitchRef.FE_0269922_348085_P_SIGMUND_IN_FACTORY = testSwitchRef.extern.PROD_BY_HEAD_BPI_BIN_SUPPORT | testSwitchRef.extern.PROD_SIGMUND_IN_FACTORY_SUPPORT | testSwitchRef.extern.PROD_BPI_BIN_BY_HEAD_SUPPORT

      if testSwitchRef.FE_0269922_348085_P_SIGMUND_IN_FACTORY:
         ScriptComment("Test Switches of %s is on" % ("FE_0269922_348085_P_SIGMUND_IN_FACTORY") )
      if testSwitchRef.FE_0284077_007867_SGL_CALL_250_ZN_VBAR_SUPPORT:
         ScriptComment("Test Switches of %s is on" % ("FE_0284077_007867_SGL_CALL_250_ZN_VBAR_SUPPORT") )

      testSwitchRef.WA_0308810_504266_RDS_ED_MICROJOG = testSwitchRef.extern.WA_0300067_504266_4K_SECTOR_MARKOV_SUPPORT and not testSwitchRef.extern.FE_0313488_228371_T238_FASTIO_DATA_VGA_SUPPORT
      if testSwitchRef.WA_0308810_504266_RDS_ED_MICROJOG:
         ScriptComment("Test Switch %s is on" % ("WA_0308810_504266_RDS_ED_MICROJOG") )
      if testSwitchRef.extern.FE_0308987_403980_PRECODER_PF3_INPUT:
         testSwitchRef.FE_0308987_403980_PRECODER_PF3_INPUT

      testSwitchRef.WA_0309963_504266_504_LDPC_PARAM = testSwitchRef.WA_0309963_504266_504_LDPC_PARAM or testSwitchRef.extern.CODE_GRAPH_4096_GLS_4_15_CW23_116 or testSwitchRef.extern.CODE_GRAPH_4096_GLS_4_15_3_116 or testSwitchRef.extern.CODE_GRAPH_4096_4_15_3_116
      if testSwitchRef.WA_0309963_504266_504_LDPC_PARAM:
         ScriptComment("504 Parity flag WA_0309963_504266_504_LDPC_PARAM enabled")
         
      testSwitchRef.FE_0315237_504266_T240_DISABLE_SKIP_TRACK = not testSwitchRef.extern.FE_0316533_504266_T240_LOCAL_FAT_FILE
###################################################### Precautionary Opti SECTION ########################################################
      if testSwitchRef.extern.RW_PRECAUTIONARY_LUT_RETRY_SF3 and testSwitchRef.extern.SFT_TEST_0256:
         testSwitchRef.FE_0343664_403980_P_ENABLE_PRECAUTIONARY_OPTI                                                         = 1                           
         ScriptComment("Test Switches of %s is on" % ("FE_0343664_403980_P_ENABLE_PRECAUTIONARY_OPTI") )
      if testSwitchRef.extern.FE_0345901_403980_MULTI_METRICS_TRIPLET_TUNING:
         testSwitchRef.FE_0345901_403980_P_MMT_TO_LOOP_IW_IN_SF3 = 1
         ScriptComment("Test Switches of %s is on" % ("FE_0345901_403980_P_MMT_TO_LOOP_IW_IN_SF3") )
      if testSwitchRef.extern.FE_0352662_403980_MMT_IW_SWEEP_LOW_TO_HIGH:
         testSwitchRef.FE_0352662_403980_P_MMT_IW_SWEEP_LOW_TO_HIGH = 1
         ScriptComment("Test Switches of %s is on" % ("FE_0352662_403980_P_MMT_IW_SWEEP_LOW_TO_HIGH") )

#### end extern flags section
