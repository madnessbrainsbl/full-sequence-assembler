#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: This file holds all operational switches for the process
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/12/20 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Amazon/Test_Switches.py $
# $Revision: #53 $
# $DateTime: 2016/12/20 00:58:41 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Amazon/Test_Switches.py#53 $
# Level: 1
#---------------------------------------------------------------------------------------------------------#
from base_Test_Switches import CBaseSwitches
from RimTypes import intfTypeMatrix

try:
   CE, CP, CN, CV = ConfigId
except:
   CN = 'bench'
   ConfigVars = {CN:{}}

class CSwitches(CBaseSwitches):

   STPGPD_ENABLED = {
      'FIN2' : 0,
      'CUT2' : 0,
      }

   # Set up build target flags
   #SMR Products
   SMR00 = 0

   #KarnakA SOC
   Karnak = 0

   #Rosewood
   RW11 = 0  # for Rosewood7 Linggi Karnak+ CH12 mule
   RW12 = 0  # for Rosewood7 Linggi Karnak+ CH12 mule + zone alignment + zone copy opti
   CM11 = 0  # for Chengai-Mule using (Pre)Amazon branch
   RW21 = 0  # for Rosewood7 Trunk CheopsAM + zone alignment + zone copy opti
   RW30 = 0  # for Rosewood7 Trunk CheopsAM + VBAR refactoring
   RW31 = 0  # for Rosewood72D features that will not be ready for 1D
   RL40 = 0  # for Rosewood7 Trunk CheopsLite + VBAR refactoring
   RL41 = 0  # for Rosewood72DLC features that will not be ready for 1DLC
   RL42 = 0  # for Rosewood7LC Unify PCO
   RL51 = 0  # for Rosewood7 LC SCOPY features
   #HAMR
   HR01 = 0
   #UPS
   UP01 = 0

   exec(CBaseSwitches.BUILD_TARGET + '=1')
   print('Build target = %s' % CBaseSwitches.BUILD_TARGET)


   if RL42 or RL51:
      ScriptComment("HDASerialNumber = %s" % HDASerialNumber)
      if not DriveAttributes.get('SF3CODE','NONE') == '8C':
         if HDASerialNumber[1:3] in ['DE', 'ES','93','CB','F6']:
            RL40 = 1
            ScriptComment("RL40 = %d" % RL40)
            ScriptComment("RL41 = %d" % RL41)
         elif HDASerialNumber[1:3] in ['DZ','94','CC','C0','C7','C8','BZ','F5','F4','F7','F8','F9']:
            RL41 = 1
            ScriptComment("RL40 = %d" % RL40)
            ScriptComment("RL41 = %d" % RL41)
         else:
            ScriptComment("HDA SN-Prefix not supported!!")
            raise
      else:
         if HDASerialNumber[1:3] in ['DE', 'ES','93','CB','F6']:
            RW30 = 1
            ScriptComment("RW30 = %d" % RW30)
            ScriptComment("RW31 = %d" % RW31)
         elif HDASerialNumber[1:3] in ['DZ','94','CC','C0','C7','C8','BZ','F5','F4','F7','F8','F9']:
            RW31 = 1
            ScriptComment("RW30 = %d" % RW30)
            ScriptComment("RW31 = %d" % RW31)
         else:
            ScriptComment("HDA SN-Prefix not supported!!")
            raise

   # Program meta-flags (these lists should include all build targets for a given program)
   # All Capital letters
   ROSEWOOD7        = ( RW11 | RW12 | CM11 | RW21 | RW30 | RL40 | HR01 | RW31 |  RL41 | UP01 )
   CHENGAI          = ( CM11 )
   SMRPRODUCT       = ( SMR00 | CHENGAI | ROSEWOOD7 ) # Shingled Magnetic Recording Products
   KARNAK           = 1 #Karnak SOC
   #KARNAKPLUSBP9    = ( RW11 | RW12 | CM11 | RW21 | RW30 | RL40 | HR01 | RW31 |  RL41 )
   TRUNK_BRINGUP    = ( 0 )
   THIRTY_TRACKS_PER_BAND = ( RW11 | RW12 | CM11 | RW21 | RW30 | RL40 | HR01 | RW31 |  RL41 | UP01 )
   TEMP25_52        = ( RW12 | RW21 | RW30 | RL40 | HR01 | RW31 | RL41 | UP01 )
   MARVELL_SRC      = ( RW21 | RW30 | RL40 | HR01 | RW31 | RL41 | UP01 ) # default turn on for trunk code bringup, Marvell
   HAMR             = ( HR01 )   
   ROSEWOOD72D      = ( RW31 | RL41 )
   CHEOPSAM_LITE_SOC= ( RL40 | RL41 ) # for CheopsAMLite only

   DEFAULT_STD_TAB                                                               = '6E8'
   DATA_COLLECTION_ON                                                            = 1

   ########################################################################
   ####################### SCOPY ##########################################
   SCOPY_TARGET                                                                  = RL51            # Using for common SCOPY option
   WRITE_SERVO_PATTERN_USING_SCOPY                                               = SCOPY_TARGET    # Write servo pattern using servo copy
   PES_SCRN_AFTER_LIN_SCRN                                                       = SCOPY_TARGET
   ########################################################################

   ########################################################################
   #######################  HAMR ##########################################
   ########################################################################
   HAMR_FLC_ATI      = 0
   HAMR_LBC_ENABLED  = 0

   ######################################################################
   ############## Log printing control : Start #####################
   ######################################################################
   FE_0299849_356688_P_CM_REDUCTION_REDUCE_PRINT                                 = ( ConfigVars[CN].get('PRODUCTION_MODE',0) & ( RW30 | RL40 | RW31 |  RL41 ))    # turn on in mass pro only
   FE_0309813_348429_P_CM_REDUCTION_REDUCE_HM_DATA                               = ConfigVars[CN].get('PRODUCTION_MODE',0)               # turn on in mass pro only
   FE_0310548_348429_P_CM_REDUCTION_REDUCE_VBAR_DATA                             = ( 0 | FE_0299849_356688_P_CM_REDUCTION_REDUCE_PRINT ) # VBAR monitoring data, turn on in mass pro only
   FE_0314243_356688_P_CM_REDUCTION_REDUCE_VBAR_MSG                              = ( 1 | FE_0299849_356688_P_CM_REDUCTION_REDUCE_PRINT ) # VBAR related
   FE_0367608_348429_P_CM_REDUCTION_REDUCE_CHANNEL_MSG_VBAR                      = ( 1 | FE_0299849_356688_P_CM_REDUCTION_REDUCE_PRINT ) # Channel related
   FE_0314243_356688_P_CM_REDUCTION_REDUCE_CHANNEL_MSG                           = ( ROSEWOOD72D | FE_0367608_348429_P_CM_REDUCTION_REDUCE_CHANNEL_MSG_VBAR | FE_0299849_356688_P_CM_REDUCTION_REDUCE_PRINT ) # Channel related
   FE_0314243_356688_P_CM_REDUCTION_REDUCE_ATI_MSG                               = ( 0 | FE_0299849_356688_P_CM_REDUCTION_REDUCE_PRINT ) # ATI related
   FE_0314243_356688_P_CM_REDUCTION_REDUCE_TRIPLET_MSG                           = ( 0 | FE_0299849_356688_P_CM_REDUCTION_REDUCE_PRINT ) # Triplet related
   FE_0314243_356688_P_CM_REDUCTION_REDUCE_FILE_MSG                              = ( 0 | FE_0299849_356688_P_CM_REDUCTION_REDUCE_PRINT ) # File related
   FE_0314243_356688_P_CM_REDUCTION_REDUCE_PROCESS_MSG                           = ( 0 | FE_0299849_356688_P_CM_REDUCTION_REDUCE_PRINT ) # Process related
   FE_0167407_357260_P_SUPPRESS_EXECUTION_INFO                                   = ( 0 | FE_0299849_356688_P_CM_REDUCTION_REDUCE_PRINT )
   FE_0315250_322482_P_AFH_CM_OVERLOADING                                        = (ROSEWOOD72D | FE_0299849_356688_P_CM_REDUCTION_REDUCE_PRINT ) # AFH reduce printing to save CM memory / CPU
   FE_0328119_322482_P_SAVE_AFH_CERT_TEMP_TO_FIS                                 = (ROSEWOOD72D | FE_0299849_356688_P_CM_REDUCTION_REDUCE_PRINT ) # save AFH cert temperature in attribute then retrive in CRT2 to save test time
   REDUCE_LOG_SIZE                                                               = 0
   ############## Log printing control : End #######################

   # Configuration management meta-flags
   ADJUST_HMS_FOR_CONSTANT_MARGIN                                                = 0
   ADJUST_TPI_FOR_CONSTANT_MARGIN                                                = 0
   AFH_V35                                                                       = 0
   CAL2_LIN_SCREEN                                                               = 0
   CALCULATE_THS                                                                 = 0
   DESPERADO                                                                     = SMRPRODUCT
   DISABLE_POSTCMT2_GOTF_CHK                                                     = 1   # Disable Cust Score & Drive Score check
   DISABLE_VCM_OFFSET_SCREEN                                                     = 0
   DO_BIE_IN_FMT                                                                 = 0
   FE_SGP_81592_ENABLE_2_PLUG_PROCESS_FLOW                                       = 1 # Set to 1 in order to enable 2-plug process flow in state table
   FE_0216004_433430_ENABLE_CCV_TEST                                             = 1
   IS_DETCR                                                                      = 1
   IS_DFS                                                                        = 0   # Set to 1 to enable Digital Flawscan
   IS_DUAL_HEATER                                                                = 1
   IS_2D_DRV                                                                     = ROSEWOOD72D
   Media_Cache                                                                   = 0
   ODMZ                                                                          = 0
   REMOVE_DOS_VERIFY                                                             = 0
   REMOVE_PES_SCRN2                                                              = 0
   REMOVE_SERIAL_FORMAT                                                          = 0
   REMOVE_VBAR_ZAP_STATES                                                        = 0
   RSSDAT                                                                        = 0
   RUN_AFH4                                                                      = 0
   RUN_DIBIT_IN_CHANNEL_OPTI                                                     = 0
   RUN_DWELL_TEST_334                                                            = 0
   RUN_HEAD_POLARITY_TEST                                                        = 0
   RUN_F3_BER                                                                    = 0
   RUN_FNC2_BODE3                                                                = 0
   RUN_LUL_MAX_CURRENT_SCREEN                                                    = 0
   RUN_LUL_TEST97                                                                = 0
   RUN_MANTARAY_BODE_SCRN                                                        = 0
   RUN_OTF_DATA_COLLECTION                                                       = 0
   RUN_PRE2_BODE                                                                 = 0
   RUN_PRE_HEAT_OPTI                                                             = 0
   RUN_QUICK_FMT_IN_FNC2                                                         = 0
   RUN_SEEK_TEST                                                                 = 0
   RUN_SER_FMT_WRT_IN_FNC2                                                       = 0
   RUN_SKIPWRITE_SCRN                                                            = 0
   RUN_SKIPWRITE_SCRN_FAIL_ENABLE                                                = 0
   RUN_SNO                                                                       = ROSEWOOD7
   RUN_SNO_PD                                                                    = ( CHENGAI | ROSEWOOD7 )
   RUN_FOF_SCREEN                                                                = 1
   INIT_CONGEN_SKIP                                                              = 0
   SINGLEPASSFLAWSCAN                                                            = CHEOPSAM_LITE_SOC
   SINGLEPASSFLAWSCAN_AUDIT                                                      = SINGLEPASSFLAWSCAN & 0
   FE_0272568_358501_P_ADAPTIVE_BIE_IN_SPF                                       = SINGLEPASSFLAWSCAN & 0
   FE_0272573_358501_P_SKIP_WRITE_IN_SPF                                         = SINGLEPASSFLAWSCAN & 0
   ENABLE_NPCAL_OFF_SETUP_IN_SPF                                                 = SINGLEPASSFLAWSCAN & CHENGAI
   SINGLEPASSFLAWSCAN_WRITE_FMT                                                  = SINGLEPASSFLAWSCAN & 0
   RUN_TEST_315                                                                  = ( CHENGAI ) or (SINGLEPASSFLAWSCAN & 0) # Set 1 to enable Test 315, needed for Digital FS
   RUN_T150_BEFORE_T176_RETRY                                                    = 0
   RUN_T176_IN_VBAR                                                              = 1
   RUN_FINE_UJOG_IN_VBAR                                                         = not SMRPRODUCT
   FINE_OPTI_ZAP_ENABLED                                                         = ( 1 & RUN_FINE_UJOG_IN_VBAR)  # Perform MiniZap before fine ujog
   SKIP_HIRP1A                                                                   = 0
   RUN_T191_HIRP_OPEN_LOOP                                                       = 0 
   RUN_T195_IN_FNC2_CRT2                                                         = 0
   RUN_WEAK_WRT_IN_IOSC2                                                         = 0
   RUN_WEAK_WR_DELTABER                                                          = 0
   RUN_ZAP_TO_DATA_TPI                                                           = 1
   RUN_ZEST                                                                      = 1 # RW7: servo 8a32, F3 AB0017 onwards
   RUN_T250_3_TIMES_ON_FAILED_DRIVES                                             = 0
   SAMTOL                                                                        = 0
   SER_FMT_WRT                                                                   = 0
   SMRDAT                                                                        = 0
   SMR_V1                                                                        = 0
   SWD_AFTER_AFH4                                                                = 0
   SWD_CAL_AFTER_ZAP                                                             = 0
   SWD_ENABLE_IN_FNC2                                                            = 0
   SWD_IN_CAL2                                                                   = 0
   SWD_VER_AFTER_DFS                                                             = 0
   T51_ALL_ZONES                                                                 = 0
   TIPS_CFG                                                                      = 0
   VBAR_HMS_V2                                                                   = 0
   VBAR_HMS_V4                                                                   = 1
   SCP_HMS                                                                       = 1 #when SCP_HMS is on, make sure VBAR_HMS_MEAS_ONLY is on, if not have to remove HMSC_DATA state
   FE_0325284_348429_P_VBAR_SMR_HMS                                              = 1 & SCP_HMS# use new method to cater for SMR Zone Alignment
   FAST_SCP_HMS                                                                  = 0 # SCP_HMS implementation without changing format, fast version
   FAST_SCP_HMS_VERIFY                                                           = 0 & FAST_SCP_HMS# invoke setting the BPIC - HMS Margin and measure the HMSC for verification purpose
   FE_0338929_348429_P_ENABLE_SQZ_HMS                                            = 1 & SCP_HMS # Enable Squeeze Writes in HMS #clwoo
   VBAR_HMS_MEAS_ONLY                                                            = 1 # data collection only
   CONDITIONAL_RUN_HMS                                                           = ( 0 ) and not (SCP_HMS | FAST_SCP_HMS) # conditional Vbar by HMS, ensure VBAR_HMS_MEAS_ONLY is enabled too
   BF_0224594_358501_LIMIT_MIN_BPIC_SET_DURING_HMSADJ                            = ( 0 )
   FE_SEGMENTED_BPIC                                                             = 0 # Turn On to run New Segmented BPIC Tuning
   FE_0321700_348429_P_SEGMENTED_BPIC_SQZ                                        = 1 & FE_SEGMENTED_BPIC# Turn On to run New Segmented BPIC Tuning SQz
   FE_0304753_348085_P_SEGMENTED_BER                                             = 1
   RUN_ATI_IN_VBAR                                                               = ROSEWOOD7
   FE_0268922_504159_VBAR_ATI_ONLY_RELAX_DIR                                     = RUN_ATI_IN_VBAR & SMRPRODUCT
   FE_0285640_348429_VBAR_ATI_CHECK_FOR_STE                                      = 1 # Switch to check STE Tracks before compensating for ATI
   FE_0285640_348429_VBAR_ATI_CHECK_FOR_STE_10K                                  = 0 & FE_0285640_348429_VBAR_ATI_CHECK_FOR_STE# Switch to check STE Tracks using 10k Writes before compensating for ATI
   FE_0285640_348429_VBAR_STE_BACKOFF_BPI                                        = 0 # Switch to backoff BPI when detected STe ISSUE during VBAR ATI
   FE_0316337_348429_VBAR_ATI_STEEP_BACKOFF                                      = 0 # Switch to put additional backoff when detect Steep ATI Degradation
   VCM_AFTER_HD_CAL                                                              = 0
   RUN_VBIAS_T186                                                                = 0  # BLOCK POINT CHANGE!!!! with AS06
   RUN_VBIAS_T186_A2D                                                            = 1
   FE_0262766_480561_RUN_MRBIAS_OPTI_T251                                        = 0 # MR BIAS Opti(test251 feature)
   RUN_VWFT_SUPPORT                                                              = 0
   RUN_STRONG_WRT_SCREEN                                                         = 0 #YARRAR
   disableTestDataOutput                                                         = []
   disable_tests_deferred_spin                                                   = [1, 2, 8, 11, 102, 166, 172, 178, 186]
   forceDummyPartNumWWN                                                          = ''
   doSeaserial                                                                   = 0
   encroachedWriteScreen                                                         = 0
   LAUNCHPAD_RELEASE                                                             = CHEOPSAM_LITE_SOC #for launchpad release FW

   # Alphabetized Switches
   AFH_ENABLE_ANGSTROMS_SCALER_USE_254                                           = 1
   AFH_ENABLE_CLR_RANGE_CHECK_IN_CROSS_STROKE_CHECK                              = 0
   AFH_ENABLE_TEST135_ADDITIONAL_MEASUREMENTS_AT_EXTREME_OD_ID                   = 0
   AFH_ENABLE_TEST135_OD_ID_ROLLOFF_SCREEN                                       = 0
   AFH_FORCE_DPES_TO_DECLARE_LAST_CONSISTENCY_CHECK_RETRY                        = 0
   AFH_V3BAR_phase5                                                              = 0
   ALL_DRIVES_GET_WWN                                                            = 1
   AUTO_RERUN_HDSTR                                                              = 0
   BF_0112487_208705_MUST_FIND_CORRECT_SERVO                                     = 0
   BF_0119055_231166_USE_SVO_CMD_ZAP_CTRL                                        = 0
   BF_0120661_357260_ENABLE_ZAP_DURING_INIT_FS                                   = 0
   BF_0121115_010200_REMOVE_UNNECESSARY_T150_CALLS_IN_SDAT                       = 0
   BF_0122569_341036_AFH_MASTER_HEAT_SET_T011_USE_MASK_VALUE_FFFE                = 0
   BF_0122749_231166_FIX_CRC_RETRIES_PRINT                                       = 0
   BF_0123402_231166_SET_CELL_BAUD_BEF_ASCII_DBG                                 = 0
   BF_0123842_231166_FILE_XFER_FIX_BNCH_MULTI_BLOCK                              = 0
   BF_0124078_347508_PHARAOH_MASS_PRO_ADG_SETUP                                  = 0
   BF_0124988_231166_FIX_SUPPR_CONST_IMPL                                        = 0
   BF_0125115_231166_FIX_SVO_F3_PKG_MFT_LOOKUP                                   = 0
   BF_0126057_231166_FAIL_INVALID_TST_RETURN                                     = 0
   BF_0126696_231166_FIX_CMD_FAIL_IN_SAS_DITS_UNLK                               = 0
   BF_0127147_357552_REFERENCE_T180_PARAM_BY_STRING_NAME                         = 0
   BF_0127710_231166_FIX_COM_MODE_POST_MCT_TEST                                  = 0
   BF_0130425_357466_FIX_T597_DOS_VER                                            = 0
   BF_0130884_354753_ANIMAL_SCRIPTS_CHANGES_TO_WORK_WITH_F3TRUNK                 = 0
   BF_0132023_161897_SATA_INITIATOR_CRT2_11087                                   = 0
   BF_0133084_231166_DYNAMIC_ATTR_PARAM_REDUCTION                                = 0
   BF_0133147_208705_TABLE_MISSING_HEAD_DATA                                     = 1 # Fix P_DELTA_RRAW to include valid physical head data
   BF_0133851_372897_BLUENUNSLIDE_BUG_FIX_FOR_SI                                 = 0
   BF_0133915_231166_SCT_BIST_RIM_SUPPORT_CHECK                                  = 0
   BF_0134266_399481_ENC_WR_SCRN_LBASTOADD_LIST_AS_SET_TYPE                      = 0
   BF_0134704_357915_PROPERLY_REPORT_DCM_CCA_VALIDATION                          = 0
   BF_0135010_357552_ADD_POWER_CYCLE_AT_CCV_START                                = 0
   BF_0135400_231166_FIX_CTRL_L_ESLIP_TRANSITION                                 = 1    # Fix bug where eslip wasn't enabled after CTRL_L in codever
   BF_0135542_231166_FIX_RETURN_SPEED_LIST_IO                                    = 0
   BF_0136108_231166_P_INCL_ASFT_IN_FORMAT_REQ                                   = 0
   BF_0137159_231166_FORCE_SPINDOWN_PRIOR_DIAG_FLSH_WRITE                        = 0
   BF_0137280_231166_FIX_GOTF_FILE_CAP_FIXES_FOR_SI                              = 0
   BF_0137361_357915_P_CHECK_ARGS_TYPE_WHEN_USING_RETRYPARMS                     = 0
   BF_0137977_231166_P_FIX_RISER_LOOKUP_NOT_INCLUDING_EXT                        = 0
   BF_0138112_231166_P_RESET_SOM_STATE_IN_ENDTEST                                = 0
   BF_0139058_231166_P_FIX_SI_BUFFER_FILE_PARAM                                  = 0
   BF_0139418_399481_P_NO_CTRL_Z_IN_BIE_SETUP_OR_DISABLE                         = 0
   BF_0139424_231166_P_FIX_SI_BUFFER_FILE_FOLDER_NAME                            = 0
   BF_0139838_231166_P_FIX_CPCRISERNEWSPT_SEASERIAL                              = 0
   BF_0140005_231166_P_FIX_FOFFILENAME_REF_BUFFER                                = 0
   BF_0140597_231166_P_USE_COMMON_F3_CODE_IDENT                                  = 0
   BF_0141335_357552_MAKE_WCE_DISABLE_VOLATILE                                   = 0
   BF_0142220_395340_P_FIX_LONG_TIME_RW_ON_DIAG_COMMAND                          = ( 1 & FE_SGP_81592_ENABLE_2_PLUG_PROCESS_FLOW )  # for 2-plug process
   BF_0142538_231166_P_FIX_UNDERBAR_MODEL_SAS                                    = 0
   BF_0142561_231166_P_FIX_STEP_LBA_SAS                                          = 0
   BF_0142777_231166_P_ADJ_MAX_SAS_LBA_FOR_COUNT                                 = 0
   BF_0142781_231166_P_FIX_SAS_TTR_PARAMETERS_FOR_START_STOP                     = 1
   BF_0143036_231166_P_FIX_506_TIMED_TEST_510                                    = 0
   BF_0143469_231166_P_DISABLE_G_LIST_ABSOLUTE_FAIL_DOS_VER                      = 0
   BF_0143505_426568_P_DISPLAY_ENTIRE_DOS_TABLE                                  = 0
   BF_0143903_357552_P_SED_PERSONALIZE_BEFORE_CUST_CFG                           = 0
   BF_0143925_231166_P_FIX_SAS_CUST_MOD_VENDOR_FIELD                             = 0
   BF_0144006_231166_P_SHIP_PROTECTION_MEDIA_CACHE                               = 0
   BF_0144790_231166_P_FIX_GOTF_DBL_REGRADE_DUP_ROWS                             = 0
   BF_0144993_231166_P_FIX_KEY_ERROR_DBLOG_GOTF_BUG                              = 1
   BF_0145392_231166_P_CHECK_COMM_MODE_SYNCSF3_SATA                              = 0
   BF_0145507_231166_P_FIX_ATA_READY_IN_CERT_OPER                                = 1   # Don't execute ATA ready check in cert operations in CPC cell
   BF_0146418_231166_P_ONLY_PRINT_ERASE_DELTA_ONCE                               = 0
   BF_0147076_357552_P_ADD_SKUA_21_REV                                           = 0
   BF_0147176_357552_P_PWRCYCLE_AFTER_CALLBACK_FOR_D_SENSE                       = 0
   BF_0147585_426568_P_FIX_SRVO_CNTRLR_ID_SPELLING                               = 1   # fix spelling of Drive Attribute SRVO_CNTRLR_ID in Servo.py
   BF_0147704_231166_P_ALWAYS_SET_LOR_FW_PORT_TCG                                = 0
   BF_0148226_357552_P_CHECK_SECTSIZE_ATTR_EXIST                                 = 0
   BF_0148756_208705_TPI_TLEVEL_CONTROL                                          = 1
   BF_0149101_357260_P_UPDATE_COO_CODES                                          = 0
   BF_0149206_231166_P_SET_LOR_AND_UNLOCK_DL_PORT                                = 0
   BF_0149507_010200_SDAT_READ_SYMBOL_TABLE_CONST                                = 0
   BF_0150174_231166_P_FIX_FLG_LOOKUP_TGT_MFT                                    = 0
   BF_0150238_231166_P_FIX_DOS_VERIFY_1B_PARSE                                   = 0
   BF_0164718_357260_P_HANDLE_LEGACY_32_BIT_LBAS                                 = ( 1 & FE_SGP_81592_ENABLE_2_PLUG_PROCESS_FLOW ) # Provide legacy support for 32 bit LBAs.
   BF_0150521_231166_P_RAW_SAS_MODEL_QUERY                                       = 0
   BF_0151621_231166_P_SYNC_BAUD_DIS_INIT_ESLIP_FAIL                             = 0
   BF_0152393_231166_P_RE_ADD_LEGACY_ESLIP_PORT_INCR_TMO                         = 0
   BF_0152505_231166_P_USE_V_CMD_FMT_DEF_LIST                                    = 0
   BF_0154261_231166_P_FIX_LGC_PHYS_MAP_DEF_PHYS_HDS                             = 0
   BF_0154839_231166_P_USE_CERT_TEMP_REF_HDA_SATURATION                          = 0
   BF_0155580_231166_P_DISABLE_517_PWR_CYCLE_SATA                                = 1
   BF_0156216_231166_MODIFY_PROMPT_SEARCH_FOR_SF3_PROMPT_DETECTION               = 0
   BF_0156515_231166_P_EXT_ON_TIME_INIT_PWR_ON                                   = 1   # Use extended RimOn time at first INC power on
   BF_0157043_231166_P_DISABLE_DRV_MODEL_NUM_VALIDATION                          = 0
   BF_0157044_231166_P_NEW_SERVO_PREFIX_DEPOP_RE_MATCH                           = 0
   BF_0157147_231166_P_SET_XFER_PRIOR_LOCK_DOWN                                  = 0
   BF_0157187_231166_P_FIX_BER_DATA_ZONE_PARSE_RETURN                            = 0
   BF_0157252_231166_P_USE_NON_EXT_FIELD_28_BIT_VALIDATION                       = 0
   BF_0157675_231166_P_FIX_SIC_TTR_SCALER_TO_MS                                  = 0
   BF_0159246_231166_P_ALWAYS_SET_BAUD_SYNC_CMD                                  = 0
   BF_0159805_208705_PREVENT_MULTIPLE_CLR_CHANGES                                = 0
   BF_0160098_231166_P_DISABLE_READY_VAR_CHECK_DISABLED                          = 0
   BF_0160118_208705_VBAR_DEPOP_HEAD_SELECTION                                   = 0
   BF_0160549_342996_P_FIX_ATA_READY_IN_CERT_OPER_ADDN                           = 1
   BF_0161447_340210_DUAL_HTR_IN_HEAD_CAL                                        = 0
   BF_0162483_426568_P_SKIP_POWER_CYCLES_IN_DISABLE_INITIATOR                    = 0
   BF_0162753_231166_P_ALWAYS_PWR_CYCLE_PRE_DNLD                                 = 0
   BF_0162945_231166_P_FIX_APM_DISABLE_DEF_SPIN_PIN                              = 1   # Fix issue where ESC key as APM disable causes drive to be stuck in BFW
   BF_0163148_231166_P_ALLOW_RETRIES_FOR_ENABLE_ESLIP                            = 0
   BF_0163420_231166_P_UTILIZE_SERIAL_CMD_FOR_SERIAL_FMT_G_LIST                  = 0
   BF_0163420_231166_P_UTILIZE_SERIAL_CMD_FOR_SERIAL_FMT_G_LIST                  = 0
   BF_0163462_007955_REVERSE_IDDEV_AND_VALIDATEDRVSN                             = 0
   BF_0163537_010200_CONSISTENT_PKG_RES_NO_FILE_FOUND_RESPONSE                   = 1   # Make the servo and generic Package Resolution getFileName response for "file not found" consistent (return None)
   BF_0163578_231166_P_FIX_DO_SERVO_CMD10_USAGE                                  = 1
   BF_0163631_340210_CORRECT_FILE_POS                                            = 0
   BF_0163846_231166_P_SATA_DNLD_ROBUSTNESS                                      = 0
   BF_0164283_007955_FIX_ZONEDATA_DICT_STRUCT                                    = 0
   BF_0164505_231166_P_ALWAYS_PWR_CYCL_POST_SPT_DNLD                             = 0
   BF_0164962_231166_P_FIX_DOS_CHK_THRESH_ENABLE                                 = ( 1 & FE_0216004_433430_ENABLE_CCV_TEST)
   BF_0165552_231166_P_RESET_COM_PWRCYCLE_INITIATOR                              = 0
   BF_0165681_340210_SERVO_MFT_SN_PREFIX_CHK                                     = 0
   BF_0165869_231166_P_SIC_PHY_TTR_METRIC                                        = 0
   BF_0165911_231166_P_FIX_NEXTPRE2_WITH_PLR                                     = 0
   BF_0166428_340210_ANG_MI_CONV                                                 = 0
   BF_0166446_231166_P_FIX_ZONE_BER_PARSING_FOR_LARGE_ERROR                      = 0
   BF_0166676_475827_P_RAISE_11201_FOR_NO_ATTRVAL                                = 0
   BF_0166867_231166_P_FIX_CRT2_SF3_INIT_DRV_INFO_DETCT                          = 0 # fix issue with power cycle transitions in CRT2 not id'ing the code type
   BF_0166991_231166_P_USE_PROD_MODE_DEV_PROD_HOSTSITE_FIX                       = 0
   BF_0167020_231166_P_SF3_DETECTION_ROBUSTNESS                                  = 1   # Robustness changes for sf3 mode detection
   BF_0168507_231166_P_ROBUST_CHANGE_TO_BER_BY_ZONE_PARSE                        = 0
   BF_0168885_231166_P_REORDER_INTF_INIT_TEMP_CHECK_AT_END                       = 0
   BF_0169360_231166_P_ALLOW_CHAR_ROBUST_BER_BY_ZONE                             = 0
   BF_0169624_007955_USE_CAMPSCheck_IN_CCV                                       = ( 1 & FE_0216004_433430_ENABLE_CCV_TEST)
   BF_0169635_231166_P_USE_CERT_OPER_DUT                                         = 1   # Fix issue where IO Rim in SIC didn't default to sf3 comm in cert opers
   BF_0171855_475827_SUPPORT_NEW_R_LIST_FORMAT_FOR_R_LIST_DUMP                   = 1   # Support new format of R List to preclude parse error during RListDump in CHK_MRG_G
   BF_0177881_231166_RETRIES_FOR_R_LIST_DUMP                                     = 1   # Add retries to the dump of the R list
   BF_0172797_231166_EXACT_MATCH_DETERMINE_CODE_TYPE                             = 1   # Determine drive code type by its return prompt
   BF_0185696_231166_P_DRIVEON_BEFORE_528                                        = 1   # Power drive on prior to 528 for TTR since sic fails after 60seconds and requires retry
   BF_0188304_340210_SUPPRESS_UNLOCK_IN_SIC                                      = 1   # unlock key suppressed in echo back
   BF_0119058_399481_NUMCYLS_LIST_LENGTH_EQUAL_TO_NUMHEADS                       = 1   # Improve VE data returned from serialScreen.getZoneInfo, prevents imaxHead from being improperly set to 1, or numZones from being blindly set to 17.
   COMPART_SSO_SCREENING                                                         = 0
   DISABLE_T250_SER_ZAP                                                          = 1
   ENC_WRT_G_TO_P                                                                = 0
   EVEN_ODD_FLAWSCAN                                                             = not SMRPRODUCT
   FULL_INTERLACE_FLAWSCAN                                                       = not SMRPRODUCT
   EnableDebugLogging                                                            = 1   # Display Reassign List and Event Log on failure and CClearSMART()
   EnableAVScanCheck                                                             = 0
   FE_0000131_231166_GOTF_REGRADE_SUPPORT                                        = 0
   FE_0000132_347508_PHARAOH_WRITE_MOBILE_MODIFICATION                           = 0
   FE_0110380_231166_USE_SETBAUD_NOT_POWERCYCLE_TO_VERIFY_DOWNLOAD_READY         = 0
   FE_0110811_320363_DISABLE_SHOCK_SENSOR_IN_ZAP                                 = 0
   FE_0111302_231166_RUN_195_IN_SEPERATE_STATE                                   = 1
   FE_0111377_345334_RUN_T43_BEFORE_T189                                         = 0
   FE_0111623_231166_BASIC_BANSHEE_SUPPORT_FROM_BRINKS_MULE                      = 0
   FE_0111784_347506_USE_DEFAULT_OCLIM_FOR_FLAWSCAN                              = 1
   FE_0111872_347506_SEASERIAL_RECYCLED_PCBAS                                    = 1
   FE_0118805_405392_POWER_CYCLE_AT_FAILPROC_START                               = 0 # PowerCycle at beginning of CFailProc() to prevent adjacent drive fail at IO cell if timeout failure occuring
   FE_0112135_345334_SPIN_UP_SERVO_BEFORE_T47                                    = 0
   FE_0112139_340210_210_OPTI                                                    = 0
   FE_0112188_345334_HEAD_RANGE_SUPPORT_10_HEADS                                 = 0
   FE_0112192_345334_ADD_T56_FOR_PZT_CAL                                         = 0
   FE_0112213_357260_DISABLE_EAW                                                 = (not DATA_COLLECTION_ON)
   FE_0112289_231166_REMOVE_INEFFICIENT_RETRIES_IN_ESLIP_BAUD_RETRIES            = 0
   FE_0112311_345334_ADD_SERVO_SPINUP_BEFORE_T56                                 = 0
   FE_0112376_231166_RAISE_11049_EC_WITH_CFLASHCORRUPTEXCEPTION                  = 1  # Raise 11049 EC with CFlashCorruption exception so it can be handled appropriately
   BF_0115535_405392_FIX_RAISE_11049_EC_WITH_CFLASHCORRUPTEXCEPTION              = 1  # BF for raise 11049 EC with CFlashCorruption exception
   FE_SGP_81592_TRIGGER_PWR_CYL_ON_1_RETRY_OF_ESLIP_RECOVERY                     = not SMRPRODUCT
   FE_0112692_231166_XLATE_TPM_SENSE_CODES_TO_FOF_CODE_WITH_DESCRIPTION          = 0
   FE_0112848_231166_USE_ZFAR_INSTEAD_OF_ZFR_BOOST                               = 0
   FE_0113230_345334_REENABLE_DUAL_STAGE_AFTER_SNO_NOTCHES                       = 0
   FE_0113290_231166_NPT_TARGETS_FROM_PARAM_FOR_T251                             = 1
   FE_0113354_231166_ADD_CHANNELCODE_4_SUPPORT_FOR_BONANZA                       = 0
   FE_0113550_231166_ADD_RETRIES_TO_THE_231_INITIALIZE_HEADER_RECORDS_TESTS      = 0
   FE_0113708_231166_JOIN_CUST_TESTNAME_WITH_AND_IF_LIST                         = 0
   FE_0113902_345334_SAVE_SAP_WHEN_CHANGING_DUAL_STAGE                           = 0
   FE_0114266_231166_INTERPOLATE_SINGLE_ZONE_FAILED_VBAR_MEASURES                = 1
   FE_0114409_231166_ALLOW_SIMPLE_OPTI_STATE_PARAM_OVERRIDE                      = 1
   FE_0114475_231166_UPDATE_RECYCLE_TRACKING_TO_REVA_DRAFT5                      = 0
   FE_0114499_357260_USE_ZAPFROMDUT_AS_DEFAULT                                   = 0
   FE_0114523_357260_ALLOW_ALPHA_TABS                                            = 0
   FE_0114826_231166_ADD_CSERVOTESTS_TO_BASE_SERIALTEST                          = 1
   FE_0115010_231166_POST_ONLY_FINAL_210_CAP_DEC_TO_ORACLE                       = 0
   FE_0115134_357915_ADD_BITERR_MODE_TO_QUICK_SYMBOL_ERROR_RATE                  = 0
   FE_0115413_357260_DISABLE_LVFF_FOR_MDW_CAL                                    = 0
   FE_0115640_010200_SDAT_DUAL_STAGE_SUPPORT                                     = 1
   FE_0115900_231166_REGEX_LIST_BASED_SDAT_SN_MATCH                              = 0
   FE_0116894_357268_SERVO_SUPPLIED_TEST_PARMS                                   = 1
   FE_0116898_399481_USE_M_COMMAND_FOR_FPW_ZERO_IN_CHECK_MERGE_G                 = 0
   FE_0116920_357260_POWERCYCLE_RETRIES_IN_CWRITEETF                             = 0
   FE_0117013_399481_DO_IDENTIFYDEVICE_BEFORE_DOWNLOAD                           = 0
   FE_0117022_399481_REENABLE_CRC_RETRIES_FOR_FULL_PACK_WRITE                    = 0
   FE_0117031_007955_CREATE_P186_BIAS_CAL2_MRE_DIFF                              = 0
   FE_0117063_7955_GOTF_ENABLE_MIN_MEAN                                          = 0
   FE_0117068_010200_IGNORE_ONLY_EC10137_IN_SNO                                  = 0
   FE_0117216_231166_ALLOW_PARAM_SET_POWERONTIME                                 = 0
   FE_0117296_357260_SUPPORT_SECOND_MR_CALL_AND_DIFF                             = 0
   FE_0117758_231166_NVCACHE_CAL_SUPPORT                                         = 1   # Add support for NVCache
   FE_0117926_357260_MQM_ATI_TEST_USE_STEPLBA                                    = 0
   FE_0118039_231166_SEND_CPC_VER_AS_ATTR                                        = 1   # Send CPC Version to attribute system
   FE_0118151_357260_ALLOW_HGA_SUPPLIER_FROM_CONFIGVAR                           = 0
   FE_0118213_399481_SET_VE_SERIAL_NUMBER_BY_PART_NUMBER                         = 0
   FE_0118405_357260_RUN_SECOND_T195_IN_READ_SCRN                                = 0
   FE_0118779_357260_SAVE_SLIST_IN_ZAP                                           = 0
   FE_0118796_231166_OUTPUT_PF3_BUILD_TARGET                                     = 0
   FE_0118821_231166_USE_PGM_LVL_VOST_DEFAULT                                    = 0
   FE_0118875_006800_RUN_T109_MSE_SCAN                                           = 0
   FE_0119988_357260_MULTIPLE_T50_ZONE_POSITIONS                                 = 0
   FE_0120780_231166_F3_SPT_RESULTS_ACCESS                                       = 1   # Support for extracting SPT_DIAG_RESULTS data from F3 diagnostics
   FE_0121254_357260_SKIP_T163_IN_READ_SCRN                                      = 1
   FE_0121834_231166_PROC_TCG_SUPPORT                                            = 1
   FE_0199808_231166_P_SEND_MSID_TO_FIS                                          = 0
   TCGSuperParity                                                                = 0   # Super Parity
   NSG_TCG_OPAL_PROC                                                             = 1   # For TCG Opal, use this flag to denote NSG specify change
   PROC_TCG_SKIP_END_TESTING                                                     = 1   # For TCG, skip end testing
   FE_0225282_231166_P_TCG2_SUPPORT                                              = 1   # Add support for tcg2.0 f3 code
   FE_0246029_385431_SED_DEBUG_MODE                                              = 0   # Debug mode for non production, which will not re-personalize for re-FIN2
   IS_SDnD                                                                       = 1   # DO NOT CHANGE: SdnD drive support - This one for debugging or manual trigger only. Auto trigger SDnD personalization based on 'SECURITY_TYPE'= 'SECURED BASE (SD AND D)'.
   FE_0241189_231166_P_NEW_TDCI_API_RETRIES                                      = 1   # Enable use of new TDCI api from host as well as retry scheme
   FE_0385431_MOVE_FINAL_LIFE_STATE_TO_END                                       = 1   # Change the SED/SDnD lifestate to "USE" at the end
   FE_0385431_SED_ACTIVATION                                                     = 1   # To enable activation
   FE_0267840_440337_P_SERIAL_PORT_AUTO_DETECT                                   = 1   # Add support for Activation on Secure Drives
   FE_0234883_426568_P_IEEE1667_SUPPORT                                          = 1   # Support to enable or disable IEEE 1667 Port in SED functionality
   SET_IEEE_1667_DEACTIVATED_IF_SDND_AND_NA                                      = 1   # Support to set IEEE 1667 Port for SDnD to 'DEACTIVATED' if NA/None
   NO_POWERCYCLE_BEFORE_AND_AFTER_UPDATECODEREVISION                             = 1
   BF_0160951_231166_P_ALLOW_SED_REP_INFO_RESP_CALLBACK                          = 1   # Allow _REPORT_INFO response as well as _INPROGRESS response to the SED callbacks
   FE_0121835_399481_WEAK_WRITE_ENHANCEMENT                                      = 1
   FE_0122163_357915_DUAL_STAGE_ACTUATOR_SUPPORT                                 = 0
   FE_0122180_357915_T150_DISABLE_UACT                                           = 0
   FE_0122186_354753_SUPPORT_FOR_SAS_REVISIONING                                 = 0
   FE_0122298_231166_ASCII_DEBUG_FIRST_BAUD_CMD                                  = 0   # Use ascii debug retry as the initial baud negotiation function as it has a higher success rate for PS programs.
   FE_0122328_231166_ALLOW_STATE_PRM_IGNORE_ATA_READY                            = 0
   FE_0122594_231166_ROBUST_BASE_RIM_TYPE_MODS                                   = 0
   FE_0122822_337233_GET_SERVO_CHIP_ID                                           = 0
   FE_0122823_231166_ALLOW_SWITCH_REFS_IN_TP                                     = 1
   FE_0122824_231166_ADD_LATENT_SETUP_TO_DUT                                     = 0
   FE_0122934_231166_551_SUPPORT_IN_INIT                                         = 0
   FE_0123282_231166_ADD_SWITCH_CONTROL_TO_STATE_TABLE                           = 1
   FE_0123391_357915_DISABLE_ADAPTIVE_ANTI_NOTCH_UNTIL_AFTER_ZAP                 = 0
   FE_0123723_399481_MR_BIAS_BACKOFF_T62_IN_VBAR                                 = 0
   FE_0123768_426568_OUTPUT_SERVO_COUNTERS_DURING_FLAWSCAN                       = 0
   FE_0123775_220554_ENABLE_RPS_SEEK_T237_PF3_SUPPORT                            = 1
   FE_0123872_399481_MQM_AUDITTEST_SKIP_INCOMPATIBLE_PARTS                       = 0
   FE_0124012_231166_ALLOW_PF3_UNLK_CODE_ACCESS                                  = 0
   FE_0124220_426568_RUN_THIRD_T195_IN_READ_SCRN                                 = 0
   FE_0124378_391186_HDSTR_CONTROLLED_BY_FILE                                    = 0
   FE_0124433_357552_RUN_GMR_RES_NO_DEMOD                                        = 0
   FE_0124465_391186_HDSTR_SHARE_FNC_FNC2_STATES                                 = 0
   FE_0124468_391186_MUSKIE_HDSTR_SUPPORT                                        = 0
   FE_0124492_399481_SINGLE_T252_CALL_IN_COLD_WRITE_SCREEN                       = not ( SMRPRODUCT )
   FE_0124554_399481_GET_BER_DATA_USING_LEVEL2_B_CMD                             = 0
   FE_0124728_357915_FULL_WRT_EO_RD_FLAWSCAN                                     = 0
   FE_0124846_357915_SWOT_SENSOR_SUPPORT                                         = 0
   FE_0124984_357466_ENABLE_END_OPER_PLUGINS                                     = 0
   FE_0125416_357915_ENABLE_ATS_CALIBRATION                                      = 0
   FE_0125486_354753_SCRIPTS_SUPPORT_FOR_DOS_PARMS_SUPPORT                       = 0
   FE_0125501_357915_PRINT_WWN_FAILURE_INFO                                      = (1) # Output additional failure and help information when WWN retrieval fails
   FE_0125503_357552_T33_RVFF_OFF_AND_ON                                         = 0
   FE_0125537_399481_TA_ONLY_T118_CALL                                           = 0
   FE_0126442_357552_OUTPUT_SERVO_COUNTERS_AFTER_FLAWSCAN_READPASS               = 0
   FE_0126858_010200_SDAT_ROBUSTNESS_IMPROVEMENTS                                = 0
   FE_0127049_231166_CONV_PCKG_ITEMS_NUMBERS                                     = 0
   FE_0127082_426568_USE_FREEZE_RESTORE_FOR_ADAPTIVE_ANTINOTCH                   = 0
   FE_0127479_231166_SUPPRESS_INFO_ONLY_TSTS                                     = 1   # Suppress output automatically for 504,507,508,514,538
   FE_0127527_426568_STEPLBA_SET_BY_TEST_PARAMETER_IN_DOS_VERIFY                 = 0
   FE_0127531_231166_USE_EXPLICIT_INTF_TYPE                                      = 0
   FE_0127808_426568_SET_SWOT_BASED_ON_CONFIG_VAR_IN_CENABLESWOT                 = 0
   FE_0128343_231166_STEP_SIZE_SUPPORT_IF3                                       = 0
   FE_0129198_399481_BIE_THRESH_IN_ENCROACHED_WRITES                             = 0
   FE_0129265_405392_SPECIAL_STATES_PLR                                          = 0
   FE_0129273_336764_ENABLE_MFG_EVAL_CTRL                                        = 0
   FE_0129672_357260_DISPLAY_P152_BODE_SENSITIVE_SCORE_IN_LOG                    = 0
   FE_0130958_336764_ADD_T186_TO_FAILPROC                                        = 0
   FE_0130984_231166_PWR_CYCLE_VER_DNLDUCODE                                     = 1
   FE_0131136_426568_RUN_T199_TWICE_IN_READ_SCREEN                               = 0
   FE_0131531_357915_SPC_ID_IN_STATE_PARAM_FOR_CHEADINSTABILITY                  = 0
   FE_0131622_357552_USE_T126_REPSLFAW_INSTEAD_OF_T130                           = 1
   FE_0131645_208705_MAX_LBA_FOR_SAS                                             = 0
   FE_0131646_357915_ALLOW_FAILURE_WHEN_RUNNING_MULTIPLE_T50_ZONE_POS            = 0
   FE_0131647_357552_HACK_SECTOR_SIZES_INTO_RAP                                  = 0
   FE_0131794_426568_RUN_T25_BEFORE_T185                                         = 0
   FE_0132082_231166_UPLOAD_PREAMP_REV                                           = 1
   FE_0132170_357915_USE_RETRY_PARMS_FOR_T51                                     = 0
   FE_0132468_357260_AUTO_SEASERIAL_FOR_CHECKSUM_MISMATCH                        = 0
   FE_0132639_405392_CHANGE_ZONE_DATA_FROM_PHYCYL_TO_LOGCYL                      = 1
   FE_0132647_336764_ADD_T208_TO_FAILPROC                                        = 0
   FE_0132730_336764_RE_WHOLE_PRE2_WHEN_POWER_TRIP_AT_MDW_STATE                  = 1
   FE_0132943_231166_DISABLE_HARD_RESET_DNLD_UCODE                               = 0
   FE_0133029_231166_RAISE_MISS_DATA_EXC_PHAST_OPTI                              = 0
   FE_0133706_357260_T234_EAW_RETRY_SUPPORT                                      = 0
   FE_0133860_372897_ADD_PARA_TEST_FUNCTION_FOR_T528                             = 0
   FE_0133890_231166_VALIDATE_SHIPMENT_DEPENDANCIES                              = 0
   FE_0133918_357260_USE_RETRY_PARMS_FOR_T50                                     = 0
   FE_0133958_357552_T149_MFGDATE_TO_ETF                                         = 0
   FE_0134030_347506_SAVE_AND_RESTORE                                            = 0
   FE_0134083_231166_UPDATE_SMART_AND_UDS_INIT                                   = 0
   FE_0134158_357552_CLEAR_MODE_PAGES_FOR_SAS                                    = 0
   FE_0134462_399481_DUMP_V4_ALLOW_DIAG_NOT_TO_FAIL                              = 0
   FE_0134663_006800_P_T186_TDK_HEAD_SUPPORT                                     = 0
   FE_0134690_231166_ALLOW_DCAID_IN_CONTENT                                      = 0
   FE_0134715_211118_ENABLE_TEST_335                                             = 0
   FE_0134771_357552_TCO_STYLE_CCV                                               = 0
   FE_0134776_357915_EO_WRT_EO_RD_FLAWSCAN                                       = 0
   FE_0135028_426568_CLEAR_MODE_PAGES_FOR_SATA                                   = 0
   FE_0135314_208705_DELTA_BPIC_SCREEN                                           = 0
   FE_0135335_342029_P_DETCR_TP_SUPPORT                                          = 1
   FE_0135432_426568_REMOVE_CALL_TO_RWK_YIELD_MANAGER                            = 1
   FE_0135987_357552_TRUNCATE_DTD_ATTR_TO_SPEC_LENGTH                            = 0
   FE_0136005_357552_USE_ALL_FIS_ATTRS_FOR_DTD_CREATION                          = 0
   FE_0136008_426568_WRITE_PCBA_PART_NUM_CAP                                     = 0
   FE_0136017_357552_DELL_PPID_FOR_SAS                                           = 0
   FE_0136807_426568_P_BANSHEE_VSCALE_OPTI                                       = 0
   FE_0136851_399481_P_USE_SMART_ATTR_ACCESS_IN_CHECKMERGEG                      = 0
   FE_0137096_342029_P_T64_SUPPORT                                               = 1
   FE_0137414_357552_CHECK_SLIP_SPACE_FOR_FIELD_REFORMAT                         = 0
   FE_0137804_399481_P_BIE_SERIAL_FORMAT                                         = 0
   FE_0137957_357552_POWER_CYCLE_FOR_CODE_LOADS                                  = 0
   FE_0138033_426568_P_SET_ZERO_PTRN_RQMT_IN_PACKWRITE                           = 0
   FE_0138035_208705_P_NO_TARGET_OPTI_IN_VBAR_HMS                                = 0
   FE_0138325_336764_P_DISABLE_FLAW_TABLE_CHK_AFTER_RETRY_T50_T51                = 1
   FE_0138460_357552_FORCE_REFORMAT_IN_CSASFORMAT_CLASS                          = 0
   FE_0138708_009410_FWA_P_SWD_DISABLE_ZERO_LATENCY                              = 0
   FE_0139087_231166_P_ALLOW_TP_OVERRIDE_SPEED_LOOKUP                            = 1
   FE_0139136_357552_T530_CHECK_PLIST_AND_SPARE_SPACE                            = 0
   FE_0139178_399481_P_ADD_DFS_AND_TA_SCAN_TO_FEATURE_REV_DISPLAY                = 0
   FE_0139319_336764_P_DELAY_BEFORE_SET_BAUDRATE_FOR_SATA_ON_SAS_SLOT            = 0
   FE_0139421_399481_P_BIE_SETTINGS_IN_CHK_MRG_G_FMT                             = 0
   FE_0139501_357552_KEEP_ALL_ZEROS_CHECK_TO_500MB                               = 0
   FE_0139584_357552_SUPPORT_NON_DEFAULT_SECTOR_SIZE                             = 0
   FE_0139634_399481_P_DETCR_T134_T94_CHANGES                                    = 0
   FE_0140112_357552_FAIL_FOR_IO_TCM_ECC_ERRORS                                  = 0
   FE_0140446_357552_PER_TAB_ZEROS_CHECK                                         = 0
   FE_0140980_231166_P_SUPPORT_TAG_Q_SI_0_QD                                     = 0
   FE_0141083_357552_PI_FORMAT_SUPPORT                                           = 0
   FE_0141300_231166_P_ADD_SUPPORT_FOR_STPA                                      = 0
   FE_0141467_231166_P_SAS_FDE_SUPPORT                                           = 0
   FE_0141653_231166_P_FORCE_DCM_MODEL_AVAILABLE                                 = 0
   FE_0141706_399481_P_T51_DELTA_TABLE                                           = 0
   FE_0142099_407749_P_NEW_HEADER_FILE_FORMAT                                    = 0 # Enable New Header File Format
   FE_0142439_357552_ADDED_LOG_PAGE_CLEAR                                        = 0
   FE_0142471_405392_P_ALLOW_OPERLIST_OVERRIDE_OPERATIONS                        = 0
   FE_0142673_399481_MOVE_SERVO_PARAMETERS_TO_SEPARATE_FILE                      = 1
   FE_0142909_231166_P_SUPPORT_SAS_DRV_MODEL_NUM                                 = 0
   FE_0142983_357552_ADD_SECTSIZE_TO_ICMD                                        = 0
   FE_0143087_357552_BYPASS_SETUP_JUST_UNLOCK                                    = 0
   FE_0143280_426568_P_SKIP_REQ_VS_CURRENT_SPEED_CHECK                           = 0
   FE_0143655_345172_P_SPECIAL_SBR_ENABLE                                        = 0
   FE_0143702_325269_P_PRESSURE_SENSOR_SUPPORT                                   = 0
   FE_0143730_399481_P_SEND_WEAK_WRITE_DELTA_TABLE_TO_DB                         = 0
   FE_0144101_208705_P_NO_TARGET_OPTI_IN_VBAR_ZN                                 = 0
   FE_0144125_336764_P_GEMINI_CENTRAL_DRIVE_COUNT_SUPPORT                        = 0
   FE_0144392_007955_P_V40_DUMP_IN_DISPLAY_G_LIST                                = 0
   FE_0144401_231166_P_SUPPORT_VEND_CMD_SEP                                      = 0
   FE_0144660_426568_DISABLE_BGMS_IN_PERFORMANCE                                 = 0
   FE_0144766_007955_P_IGNORE_11049_DURING_DFS                                   = 0
   FE_0145513_357552_P_IF3_IGNORE_11107_ERRORS                                   = 0
   FE_0145538_208705_VBAR_HMS_INCREASE_TGT_CLR                                   = 0
   FE_0145589_345963_P_T126_DISABLE_DEBUG_MESSAGE                                = 0
   FE_0145622_357552_P_ADD_MODE_PAGE_RESET_AT_FIN2_START                         = 0
   FE_0145659_357552_P_REARRANGE_MR_CCV2_STATE_TABLE                             = 0
   FE_0146187_007955_P_SET_OCLIM_BEFORE_AFTER_T213                               = 0
   FE_0146430_231166_P_ENABLE_CERTIFY_SAS_FMT                                    = 0
   FE_0146434_007955_P_T80_HD_CAL_ITEMS_TO_POP_BY_HD_TYPE                        = 0
   FE_0146555_231166_P_VER_TEMP_SAT_INIT                                         = 0
   FE_0146586_007955_P_ADD_RW_SCREEN_TO_FEATURE_REV_DISPLAY                      = 0
   FE_0146721_007955_P_ALLOW_DRVMODELNUM_LBA_OVERRIDES_AT_LCO_ONLY               = 0
   FE_0146812_231166_P_ALLOW_DL_UNLK_BY_PN_TCG                                   = 0
   FE_0146843_007955_P_DISABLE_PRINT_ERASE_DELTA                                 = 0
   FE_0147058_208705_SHORTEN_VBAR_LOGS                                           = ROSEWOOD7
   FE_0147072_007955_P_EAW_USE_T240_IN_PLACE_OF_T234                             = 1
   FE_0147082_231166_P_VERIFY_MEDIA_CACHE                                        = 0
   FE_0147105_426568_P_COMBO_STATE_SELECTION_P_TESTSWITCH                        = 0
   FE_0147357_341036_AFH_T172_FIX_TRUNK_MERGE_CWORD1_31                          = 1
   FE_0147673_208705_VBAR_HMS_TPIMT_ADJUSTMENT                                   = 0
   FE_0147794_345172_A_FLAWSCAN_PWR_LOSS_CHK                                     = 0
   FE_0147914_231166_P_ADD_SUPPORT_MC_INIT_DIAG                                  = 0
   FE_0148237_357552_P_ADD_HP_SPECIFIC_BGMS_DISABLE                              = 0
   FE_0148582_341036_AFH_WHIRP_V35_CHANGE_VALUES                                 = 1
   FE_0148599_357552_P_MOVE_RESET_SMART_TO_BEGINNING                             = 0
   FE_0148727_231166_P_ENABLE_WC_ZONE_XFER                                       = 0
   FE_0148761_409401_P_CHECK_HDA_TEMP                                            = 0
   FE_0148766_007955_P_FNC2_FAILPROC_DONT_LOAD_CFW_IF_F3_LOADED                  = 0
   FE_0149477_007955_P_SAVE_SAP_ON_NON_DUAL_STAGE_ACT                            = 0
   FE_0149739_357552_P_FMT_PI_SKIP_MP3_RESET                                     = 0
   FE_0150126_007955_P_DUMP_SERVO_FLAW_LIST_AT_END_OF_DFS                        = 0
   FE_0150604_208705_P_VBAR_HMS_PHASE_2_INCREASE_TGT_CLR                         = 0
   FE_0150973_357260_P_REDUCE_PARAMETER_EXTRACTOR_VERBOSITY                      = 1
   FE_0151000_007955_P_TRIPAD_UNVISITED_T118_CALL                                = 0
   FE_0151342_007955_P_CREATE_P_FMT_T250_RAW_ERROR_RATE_DELTA_TABLE              = 0
   FE_0151360_231166_P_ADD_SUPPORT_SAS_SED_CRT2_UNLK                             = 0
   FE_0151675_231166_P_SUPPORT_SINGLE_DIAG_INIT_SHIP                             = 0
   FE_0151714_208705_IGNORE_HEAD_COUNT_FROM_DEPOP                                = 0
   FE_0151949_345172_P_SEND_ATTR_PRE2_START_FOR_DAILY_TRACKING_YIELD             = 0
   FE_0152007_357260_P_DCM_ATTRIBUTE_VALIDATION                                  = 0
   FE_0152175_007955_ADD_NUM_PHYS_HDS_TO_DUT_OBJ                                 = 1
   FE_0152577_231166_P_FIS_SUPPORTS_CUST_MODEL_BRACKETS                          = 1
   FE_0152759_231166_P_ADD_ROBUST_PN_SN_SEARCH_AND_VALIDATION                    = 0
   FE_0152922_231166_P_DNLD_U_CODE_PKG_CODE_VER                                  = 0
   FE_0153357_007955_P_USE_DETCR_PREAMP_SETUP_STATE                              = 0
   FE_0153649_231166_P_ADD_INC_DRIVE_ATTR                                        = 1   # Add SIC rev to attributes
   FE_0153930_007955_P_FMT_CMD_DONT_DEFAULT_DefectListOptions_TO_3               = 0
   FE_0154003_231166_P_ALLOW_BYPASS_MC_CMDS_BASED_F3_FLAG                        = 0
   FE_0154366_231166_P_FDE_OPAL_SUPPORT                                          = 1
   FE_0154423_231166_P_ADD_POST_STATE_TEMP_MEASUREMENT                           = 0
   FE_0154440_007955_P_SYNC_BAUD_RATE_IN_MQM_GET_MAX_CYLS                        = 0
   FE_0154456_220554_P_POWER_CYCLE_AFTER_RESONANCE_SCREEN                        = 0
   FE_0154480_220554_P_SPIN_DOWN_BEFORE_T186_DURING_HEAD_CAL                     = 0
   FE_0154841_231166_P_USE_SEEKS_HEAT_HDA                                        = 0
   FE_0154919_420281_P_SUPPORT_SIO_TEST_RIM_TYPE_55                              = 0
   FE_0155581_231166_PROCESS_CUSTOMER_SCREENS_THRU_DCM                           = 1
   FE_0155584_231166_P_RUN_ALL_DIAG_CMDS_LOW_BAUD                                = 0
   FE_0155812_007955_P_T176_DONT_RECAL_IF_POLYZAP_SAVED_TO_SAP                   = 0
   FE_0155925_007955_P_T251_SEPERATE_SYS_AREA_PARAMS                             = 1
   FE_0155956_336764_P_SEND_OPER_TES_TIME_AS_ATTRIBUTE                           = 1
   FE_0156514_357260_P_SERVO_FILES_IN_MANIFEST                                   = 1   # Assume Servo package contains valid manifest
   FE_0156020_231166_P_UPLOAD_USER_SLIP_LIST_TBL                                 = 0
   FE_0157311_345172_TURN_ON_ZAP_AFTER_HDSTR_UNLOAD                              = 0
   FE_0157407_231166_P_USE_SINGLE_CHAR_SVO_REL_PREFIX                            = 0
   FE_0158153_231166_P_ALL_SPT_MQM_NO_ATA_RDY                                    = 0
   FE_0158386_345172_HDSTR_SP_PRE2_IN_GEMINI                                     = 0
   FE_0158388_345172_HDSTR_SP_CHECK_TEMP_EVAL_PURPOSE                            = 0
   #PSTR
   FE_0318846_385431_WAIT_FOR_CERT_TEMP_DOWN                                     = 1   #Drive too hot, power down drive and wait
   FE_0318846_385431_FAIL_IF_CERT_TEMP_TOO_HIGH                                  = 1   #Fail the drive if too hot as this mean not able to meet the temperature delta at CRT2       

   FE_0158563_345172_HDSTR_SP_PROCESS_ENABLE                                     = 0
   FE_0158632_357260_P_ENABLE_TEST_163_MDW_QUALITY_CHECK                         = 0
   FE_0158685_345172_ENABLE_HDSTR_TEMP_CHECK                                     = 0
   FE_0158815_208705_VBAR_ZN_MEAS_ONLY                                           = 0
   FE_0158827_208705_VBAR_HMS2_WATERFALL                                         = 0
   FE_0158862_231166_P_VERIFY_OVL_DNLD_U_CODE                                    = 0
   FE_0158866_231166_P_RETRY_DNLD_CODE_NON_COMMIT                                = 0
   FE_0159339_007955_P_FAIL_PROC_GET_MR_VALUES_ON_RAMP_186                       = 0
   FE_0159477_350037_SAMPLE_MONITOR                                              = 0
   FE_0159597_357426_DSP_SCREEN                                                  = 0
   FE_0159615_448877_P_ALLOW_T054_TO_FAIL                                        = 0
   FE_0159624_220554_P_POWER_CYCLE_AT_BEGINNING_OF_SWDVERIFY                     = 0
   FE_0160076_336764_FORCED_SEASERIAL_AT_INIT_PRE2                               = 0
   FE_0160097_007867_VBAR_MEASUREHMS_211_PARMS_BY_STATE                          = 0
   FE_0160361_220554_P_SET_T130_TIMEOUT_TO_3600_SECONDS                          = 0
   FE_0160686_220554_P_USE_ZONE_1_INSTEAD_OF_0_IN_WEAK_WRITE_SCRN                = 0
   FE_0160731_357260_P_USE_DCM_VALUES_FOR_CUST_TESTNAME                          = 0
   FE_0160791_7955_P_ADD_STATE_TABLE_SWITCH_CONTROL_IN_H_OPT                     = 0
   FE_0160792_210191_P_TEMP_CHECKING_IN_GEMINI_CRITICAL_STATES                   = 0
   FE_0161626_231166_P_DISABLE_TEMP_MSR_BLUE_NUN                                 = 0
   FE_0161827_345172_P_CONTROL_TEMP_PROFILE_BY_HEAD                              = 0
   FE_0161887_007867_VBAR_REDUCE_T255_LOG_DUMPS                                  = 0
   FE_0162081_007955_MDWCAL_RUN_T163_T335_AFTER_T185                             = 0
   FE_0162444_208705_ASYMMETRIC_VBAR_HMS                                         = 0
   FE_0162448_007867_MOVE_VBAR_HMS_SPEC_AND_MT_ADJUSTS_TO_NIBLET                 = 0
   FE_0162554_336764_ENABLE_SLIP_LIST_INFO_DISP_AT_FAIL_PROC                     = 0
   FE_0162917_407749_P_AFH_LUL_FOR_RETRY_BY_ERROR_CODE                           = 0
   FE_0163083_410674_RETRIEVE_P_VBAR_NIBLET_TABLE_AFTER_POWER_RECOVERY           = 0
   FE_0163145_470833_P_NEPTUNE_SUPPORT_PROC_CTRL20_21                            = (1)   # Enable Neptune support. For use of PROC_CTRL20 and PROC_CTRL21.
   FE_0163564_410674_GET_ZONE_INFO_BY_HEAD_AND_BY_ZONE                           = 1
   FE_0163871_336764_P_DO_LOGPOWERON_AFTER_COMPLETE_FULL_PWC_RETRY               = 0
   FE_0164094_407749_P_ADD_AUTO_RETRIES_FOR_READ_CMD                             = 0
   FE_0164115_340210_SMART_FH_WRT                                                = 0
   FE_0164322_410674_RETRIEVE_P_VBAR_TABLE_AFTER_POWER_RECOVERY                  = 0
   FE_0165086_231166_P_INGORE_TTR_IN_FIN2_DL                                     = 0
   FE_0165113_231166_P_SIC_PHY_READY_TTR                                         = 0
   FE_0165256_208705_VBAR_STORE_TEMP                                             = 0
   FE_0165651_345172_FE_PROC_TEST_FLOW_ATTR_FOR_SEPARATE_FLOW                    = 0
   FE_0166236_010200_ADD_VCM_SENSITIVITY_ON_DS_PRODUCTS                          = 0
   FE_0166634_231166_SAS_SMART_FH_TRACK_INIT                                     = 0
   FE_0166720_407749_P_SENDING_ATTR_BPI_TPI_INFO_FOR_ADG_DISPOSE                 = 0
   FE_0166912_336764_P_ADD_T25_TO_FAILPROC                                       = 0
   FE_0167320_007955_CREATE_P_DELTA_BURNISH_TA_SUM_COMBO                         = 0
   FE_0167431_345172_P_SEND_ATTR_PRE2_BP                                         = 0
   FE_0167481_007955_ZAP_OFF_DURING_LUL_T109                                     = 0
   FE_0168027_007867_USE_PHYS_HDS_IN_VBAR_DICT                                   = 0
   FE_0168477_209214_ZAP_REV_ALLOCATION                                          = 0
   FE_0168661_231166_P_ALLOW_SAS_RESET_DOS                                       = 0
   FE_0168708_208705_VBAR_HMS_ITERATION_TAG                                      = 0
   FE_0169171_231166_MC_PART_B_SEP_TBL_PARSE                                     = 0
   FE_0169221_007867_VBAR_ADD_SETTLING_CLR_CALC                                  = 0
   FE_0169232_341036_ENABLE_AFH_TGT_CLR_CANON_PARAMS                             = 0
   FE_0169378_475827_ADD_SPINUP_BEFORE_T177                                      = 0
   FE_0169617_220554_P_SET_SIM_FSO_SIMDICT_ADAPT_FS_PRM_TO_38912                 = 0
   FE_0143811_357263_ADD_IPD3                                                    = 1
   FE_0158916_357263_AGC_BASELINE_JUMP_DETECTION                                 = 1
   FE_0173503_357260_P_RAISE_EXCEPTION_IF_UNABLE_TO_READ_DCM                     = 1   # If we cannot read customer attributes, raise 14761
   FE_0173306_475827_P_SUPPORT_TRUNK_AND_BRANCH_F3_FOR_GET_TRACK_INFO            = ( 1 & FE_SGP_81592_ENABLE_2_PLUG_PROCESS_FLOW ) # Allows calculation of proper track cleanup range for both trunk and branch F3 code, regardless of flag settings.
   FE_0174396_231166_P_MOVE_CLEANUP_TO_OWN_STATE                                 = ( 1 & FE_0216004_433430_ENABLE_CCV_TEST )
   FE_0175666_007955_ENABLE_DISABLE_WTF_ATTRS_USING_CONFIGVAR                    = 1
   FE_0177176_345172_ENABLE_RETURN_VALUE_CHECKING_FROM_T507                      = 1   # Add feature checking from 'CTRL_Z' and 'CTRL_T' after send T507.
   FE_0184238_475827_P_ADD_RETRIES_FOR_CCVTEST_UDR2_CHK                          = ( 1 & FE_0216004_433430_ENABLE_CCV_TEST )
   FE_0183111_231166_P_CCV_CHECK_ALL_DOS                                         = ( 1 & FE_0216004_433430_ENABLE_CCV_TEST)
   FE_0188217_357260_P_AUTO_DETECT_TRACK_INFO                                    = ( 1 & FE_SGP_81592_ENABLE_2_PLUG_PROCESS_FLOW ) # for 2-plug process
   FE_0203247_463655_AFH_ENABLE_WGC_CLR_SETTING_SUPPORT                          = 0
   FE_0207956_463655_AFH_ENABLE_WGC_CLR_DATA_COLLECTION                          = ( 1 & FE_0203247_463655_AFH_ENABLE_WGC_CLR_SETTING_SUPPORT)   # Data collection for WGC (Write Gate Count) test
   FE_0207956_463655_AFH_ENABLE_WGC_CLR_TUNING                                   = ( 0 & FE_0207956_463655_AFH_ENABLE_WGC_CLR_DATA_COLLECTION)   # Data collection for WGC (Write Gate Count) test
   FE_0264856_480505_USE_OL_GAIN_INSTEAD_OF_S_GAIN_IN_282                        = 0 # Open Loop gain instead of Sensitivity gain in doBodePrm_282
   FE_0320895_502689_P_RUN_SPIO_LOW_BAUD                                         = 1 # In SPFIN2, use lower 38K baud rate


   SGP_81592_CHS_READS_IN_AFH_CLEANUP                                            = ( 1 & FE_SGP_81592_ENABLE_2_PLUG_PROCESS_FLOW ) # Enable read verifies (CHS mode) in AFH Cleanup - for FA purposes
   FORCE_LOWER_BAUD_RATE                                                         = 0
   FailcodeTypeNotFound                                                          = 1
   GA_0113069_231166_ENABLE_VERBOSE_DEBUG_IN_238_AGC_JOG                         = 0
   GA_0113384_231166_DUMP_RAP_OPTI_DATA_PRE_AND_POST_OPTI                        = 0
   GA_0115421_231166_MEASURE_BER_POST_WP_OPTI_NOM_FMT                            = 0
   GA_0115920_357915_REPORT_SERVO_FLAW_TABLE_BETWEEN_READ_AND_WRITE_SCANS        = 0
   GA_0152127_357267_ERROR_RATE_AUDIT_PRE_AND_POST_OPTI                          = not (FE_0310548_348429_P_CM_REDUCTION_REDUCE_VBAR_DATA)
   GA_0160140_350027_REPORT_CHANNEL_DIE_TEMP_THROUGHOUT_PROCESS                  = 0
   Muskie_4KMDF                                                                  = 0
   OPAL_FDE_META_FLAG                                                            = 0
   proqualCheck                                                                  = 1 # Set this flag to enable Proqual checking for valid operation using the attribute
   RUN_HEAD_LOAD_DAMAGE_SCREEN                                                   = 0
   SET_HEAD_SUPPLIER_IN_SAP                                                      = 1
   USE_HGA_AAB_ATTR                                                              = 1
   USE_HSA_WAFER_CODE_ATTR                                                       = HAMR # Define HSA_WAFER_CODE, derived from FIS attr HEAD_SN_00. Fail drive if cannot get from FIS or ConfigVar
   USE_HGA_VENDOR_ATTR                                                           = 1 # Use the drive attribute HGA_VENDOR to identify head type- fallback to configvar if not available
   USE_LOAD_ONLY_IN_PRODUCTION                                                   = 0
   VARIABLE_OST                                                                  = 0
   VBAR_SUPPRESS_REPORT                                                          = 0
   WA_0110324_357260_POWER_CYCLE_TO_READ_TEMP                                    = 0
   WA_0111543_399481_SKIP_readFromCM_SIMWriteToDRIVE_SIM_IN_HIRP                 = 0
   WA_0111624_231166_BANSHEE_TEST_238_HANG                                       = 0
   WA_0115021_231166_DISABLE_WRITING_RESULTS_FILE_TO_DUT                         = 1
   WA_0115472_208705_DISALLOW_13409_WATERFALL                                    = 0
   WA_0115641_010200_DISABLE_OL_BODE_ON_DUAL_STAGE                               = 0
   WA_0117940_231166_IGNORE_INIT_DL_MISMATCH                                     = 0
   WA_0119554_231166_DIAG_MAX_LBA_LEN_LIMITED                                    = 0
   WA_0121630_325269_SAS_TGT_DNLD_IGNORE_TIMEOUT                                 = 0
   WA_0121752_399481_USE_U_CMD_TO_SPIN_UP_IN_WEAK_WRITE_SCREEN                   = 0
   WA_0122681_231166_EXTENDED_BAD_CLUMP_TIMEOUT                                  = 1    # Add additional time for bad clump drives to come SPT ready
   WA_0122875_231166_NOM_SPEED_TP_OVERRIDE                                       = 0
   WA_0124639_231166_DRIVE_SMART_NOT_SUPPORTED                                   = 0
   WA_0124652_231166_DISABLE_SET_XFER_SPEED                                      = 0
   WA_0124831_231166_FORCE_INTF_TYPE                                             = 0
   WA_0125708_426568_FULLY_DISABLE_LVFF                                          = 0
   WA_0126043_426568_TOGGLE_SAPBIT_FOR_HIGH_BW_FILTER                            = 0
   WA_0126798_357260_FORCE_DIAG_OVERLAY_LOAD                                     = 0
   WA_0126987_426568_RUN_TEST_193_TWICE_WITH_NEW_GAIN_VALUE                      = 0
   WA_0128885_357915_SEPARATE_OD_ODD_EVEN_FLAWSCAN                               = 0
   WA_0129386_426568_DISABLE_LVFF_AFTER_ZAP_BASED_ON_PCBA_NUM                    = 0
   WA_0129851_399481_ENCROACHED_SCREEN_ERROR_FILTERING                           = 0
   WA_0130075_357260_SKIP_SPEED_CHECK                                            = 0
   WA_0130599_357466_T528_EC10124                                                = 0
   WA_0133429_399481_RETRY_ALT_LBA_IN_ENC_WR_SCRN                                = 0
   WA_0134988_395340_RESET_TIMEOUT_THAT_REMAIN_ON_CPC                            = 0
   WA_0135289_357552_DSENSE_BIT_NOT_DEFAULT_ON_34_BIT_LBA                        = 0
   WA_0139361_395340_P_PARTICLE_AGITATION_IO_PLUG                                = 0
   WA_0139526_231166_P_HARD_RESET_PRIOR_IDENT                                    = 0
   WA_0139839_231166_P_RETRY_11102_IN_MERGE_G                                    = 0
   WA_0141203_357552_FULL_POWER_CYCLE_AFTER_CODE_LOAD                            = 0
   WA_0141744_357552_BYPASS_T515_CERTIFY                                         = 0
   WA_0143409_426568_P_CAST_STRINGS_IN_SONY_SCREEN                               = 1   # Cast strings to ints in Sony Screen
   WA_0145880_231166_P_FIX_INIT_HANG_BDG_DL                                      = 0
   WA_0149624_007955_P_ENABLE_RESETWATERFALLATTTRIBUTE_FOR_LCO                   = 0
   WA_0151540_342996_DISABLE_TEST_103                                            = 0
   WA_0154353_350027_LCO_DISABLE_TA_DETECTION_AND_CHARACTERIZATION               = 0
   WA_0156250_231166_P_DONT_SET_PROC_BAUD_ENABLE_ESLIP                           = 0
   WA_0158450_231166_P_ONLY_RESET_OVL_FOR_SHIP_FLED_FIX                          = 0
   WA_0159131_007955_P_PWR_CYCLE_BEFORE_BODE_TEST                                = 0
   WA_0159248_231166_P_DELAY_DIAG_FOR_MC_INIT                                    = 0
   WA_0162362_007955_SPLIT_TEST_335_INTO_2_CALLS                                 = 0
   WA_0163780_231166_P_DO_NOT_ENABLE_SWD_FOR_AFS                                 = 1
   WA_0164214_231166_P_DISABLE_DIAGS_IN_INTERFACE_OPS                            = 0
   WA_0168153_007955_USE_AP2_WITH_BLUENUNSLIDE                                   = 0
   WA_0256539_480505_SKDC_M10P_BRING_UP_DEBUG_OPTION                             = 0 # For SKDC M10P Bring up workaround option
   WA_0262223_480505_FIX_QNR_CODE_DOWNLOAD_ISSUE_FOR_PSTR                        = 0 # PSTR QNR code download issue (after download power cycle, send serial command)
   WA_0299052_517205_RECONNECT_AND_CONTINUE_ON_11049_ERR_FOR_T178                = 1 #Ignore all 11049 errors @ T178. Re establish connection and continue
   FE_0258650_480505_SKDC_M10P_PROCESS_TIME_REDUCTION                            = 0 # For SKDC M10P Bring up Process Time Reduction items
   FE_0303934_517205_SET_OVERSHOOT_PARAM_AT_SETUP_PROC                           = ( RW31 | RL41 | RW30 | RL40 | HR01 | UP01 ) # to set write current rise time,Overshoot rise time and overshoot falll time @ PRE2-SETUP_PROC
   WO_MULTIRATESNO_TT122                                                         = 0
   WO_V3BAR_ENABLED                                                              = 0
   checkMediaFlip                                                                = 0
   customerConfigInCAP                                                           = 0
   forceRapDownLoad                                                              = 0
   iVBARZAP                                                                      = 0
   modifyRunTimeServoController                                                  = 0
   resetWaterfallAttributes                                                      = 0
   BF_0174032_231166_P_FULL_PWR_CYCLE_ENABLE_INIT_FAIL                           = 1
   BF_0178970_007955_HANDLE_SF3_TABLES_WRITTEN_TO_MEMORY_VIA_PF3                 = 1
   FE_0166305_357263_T135_RAP_CONSISTENCY_CHECK                                  = 0
   FE_0238194_348432_T109_REWRITE_BEFORE_VERIFY_READ                             = 0 # Rewrite once before first verify read
   FE_0139240_208705_P_IMPROVED_MAX_LBA_CALC                                     = 0 # Align max LBA values with official Seagate requirements
   BF_0144913_208705_P_SET_CAPACITY_NOT_MAX_LBA                                  = 0 # Modify VBAR to set capacity in the RAP rather than max LBA

   #################################################################################
   ############################        SCPK START      #############################
   #################################################################################
   RELOAD_DEMAND_TABLE_ON_WTF                                                    = 1
   MARVELL_PHAST_MICROJOG                                                        = 1
   FE_0007406_402984_USE_INTFTTR_MAX_VALUE                                       = 1
   NEW_TTR_SPEC_CHECK                                                            = ROSEWOOD72D   
   FE_SGP_PREAMP_GAIN_TUNING                                                     = 1
   FE_SGP_81592_DISABLE_HEATER_RES_MEAS_T80                                      = 1
   FE_SGP_81592_COLLECT_BER_B4_N_AFTER_RD_OPTI                                   = not (FE_0310548_348429_P_CM_REDUCTION_REDUCE_VBAR_DATA)
   FE_0184276_322482_AFH_64ZONES_T135_SQUEEZE_PARAM                              = ROSEWOOD7 or CHENGAI
   FE_0194098_322482_SCREEN_DETCR_OPEN_CONNECTION                                = 0 # failed for PreAmazon/F3Trunk
   ENABLE_SINGLE_STAGE_IN_DAULSTAGE_DRV                                          = 0
   FE_SGP_DEFINE_AABTYPE_IN_CONFIG_VAR_BASED_ON_HGA_SUPPLIER                     = USE_HGA_AAB_ATTR  # Set 1 to allow specifying AAB type in configvar.py
   AAB_PER_HGA_SUPPLIER                                                          = not (FE_SGP_DEFINE_AABTYPE_IN_CONFIG_VAR_BASED_ON_HGA_SUPPLIER )  # Set 1 to define AAB type in AFH_params.py
   TurnOffZapAfterInitSys                                                        = 1
   SEA_SWEEPER_ENABLED                                                           = 1
   SEA_SWEEPER_RPM                                                               = 1 # enable T04 in HRPM_SPIN
   AFH3_ENABLED                                                                  = 0
   FE_AFH3_TO_DO_BURNISH_CHECK                                                   = 1 # & FE_AFH3_TO_IMPROVE_TCC) #
   FE_SGP_OPTIZAP_ADDED                                                          = 1
   EnableDebugLogging_T598                                                       = 1   # Enable T598 defect list debug
   EnableT250DataSavingToSIM                                                     = 1
   luxorM93_channel_switch                                                       = 1   # Set when running LuxorM9300 boards
   depMREStatCheck                                                               = 0
   WO_T250_NODUMMYREAD_SF374013                                                  = 0
   BERScreen2_Enabled                                                            = 0
   FE_0110575_341036_ENABLE_MEASURING_CONTACT_USING_TEST_135                     = 1
   #FE_0157745_387179_AFH_TCS_WARP                                                = 0   # TCS WARP
   AFH_TCS_WARP_ALLZONES_USE_SAME_VALUE                                          = (0 ) # & FE_0157745_387179_AFH_TCS_WARP)
   AFH_BURNISH_CHECK_BYPASS_READER_CLR                                           = 1
   forceTcs2EqualZero                                                            = 1
   FE_SGP_402984_P_SUPPRESS_SUPPRESSED_OUTPUT_INFO                               = not (DATA_COLLECTION_ON)  # Dblog size reduction. Suppress suppressed output info.

   FE_0182188_231166_P_ALLOW_DETS_CE_LOG_CAPTURE                                 = 1   # Allow capture of CE log data through SPT DETS command
   FE_0168920_322482_ADAPTIVE_THRESHOLD_FLAWSCAN_LSI                             = ROSEWOOD7 # Analog flaw scan threshold by head by zone for LSI
   FE_0000000_348432_AFS_SYNC_UP_AFS_THRESHOLD                                   = 1 and FE_0168920_322482_ADAPTIVE_THRESHOLD_FLAWSCAN_LSI  # SMR: Same AFS threshold for SLIM and FAT tracks.
   FE_0247885_081592_BODE_PLOT_AT_7200RPM                                        = 0 #CHENGAI and not M10P # Switch to enable 7200RPM bode plot (test 282) at the beginning of PRE2
   #####   DBLOG Switches  #######
   ADD_PARAMETRICS_TO_LIMITS                                                     = 0 # Enables increasing the parametric loading up to the maximum parametric limit
   USE_WAFER_CODE_ATTR                                                           = CHENGAI # Use the parameter WAFER_CODE_MATRIX to resolve attributes to determine wafer code- fallback to configvar if not available
   ## VBAR ATI related switches
   ## For SMR products OTC is being used instead of ATI
   VBAR_T51_ITERATION                                                            = RUN_ATI_IN_VBAR   # Flag to turn on T51 Looping
   VBAR_TPIM_SLOPE_CAL                                                           = RUN_ATI_IN_VBAR   # Flag to use Slope Cal to provide TPIM
   TPIM_SMOOTH                                                                   = not (ROSEWOOD7 or CHENGAI)  # RUN_ATI_IN_VBAR   # Enable Smoothing in TPIM
   VBAR_T51_STEP_FOLLOW_SERPENT                                                  = not (ROSEWOOD7 or CHENGAI)  # Flag to use smallest serpent width step in T51 Measurements
   VBAR_T51_ITER_OPTIMIZATION                                                    = RUN_ATI_IN_VBAR # Flag to reduce the iteration when OTF BER is very good
   ## end of VBAR ATI
   try:                                                                                # IO test time reduction
      CPCWriteReadRemoval                                                        = riserType in intfTypeMatrix['SATA']['riserTypeMatrix']['CPCList']
      IOWriteReadRemoval                                                         = not CPCWriteReadRemoval   # to enable write read removal for test time saving
   except:
      IOWriteReadRemoval                                                         = 1   # VE support
   SDBP_TN_GET_JUMPER_SETTING                                                    = 0   # SDBP using Test Number Flags
   SDBP_TN_GET_NUMBER_OF_HEADS_AND_ZONES                                         = 1   # SDBP using Test Number Flags
   SDBP_TN_GET_BASIC_DRIVE_INFORMATION                                           = 1   # SDBP using Test Number Flags
   SDBP_TN_GET_UDR2                                                              = 1   # SDBP using Test Number Flags
   CHECK_SUPERPARITY_INVALID_RATIO                                               = 1   #Check SuperParityInvalidRatio against spec at FIN2, S_PARITY_CHK
   FE_AFH_BURNISH_CHECK_BY_RDDAC                                                 = 0
   ADAPTIVE_GUARD_BAND                                                           = 1   # Enable Adaptive guard band
   EnableVariableGB_by_Ramp                                                      = 1  # implement variable FCO. Set to 1 to turn on the feature else is off
   Enable_OAR_PAD                                                                = not SMRPRODUCT # need to review for SMR
   Enable_OAR_SCREEN_Failling_Spec                                               = 1
   OAR_CW_SEC                                                                    = 1  #1 -Sector mode, 0 - Codeword mode
   BodeScreen                                                                    = 1  # Flag to enable screening of Bode
   BodeScreen_Fail_Enabled                                                       = 0 # 1 = Enable failing criteria   0 = test does not fail
   FE_SGP_SKIP_TEST_167_IN_RD_SCRN                                               = 1
   FE_SGP_HSA_OFFSET_SCRN                                                        = 0
   OW_FAIL_ENABLE                                                                = 0 # Turn on Over Write test failing criteria
   SMROW_FAIL_ENABLE                                                             = 0 # Turn on FNC2 SMR Over Write test failing criteria
   OW_DATA_COLLECTION                                                            = DATA_COLLECTION_ON      #Turn on Over Write test data collection in PRE2,CRT2
   Enable_BPIC_ZONE_0_BY_FSOW_AND_SEGMENT                                        = 0 and not (SCP_HMS | FE_SEGMENTED_BPIC)
   VBAR_CHECK_IMBALANCED_HEAD                                                    = 0   # Check for delta of zone 0 BPIC between heads, limit specified in ImbalancedHeadLimit (0.20)
   VBAR_CHECK_MINIMUM_THRUPUT                                                    = 1   # Calculate throughput at OD & ID, fail if cannot meet limit specified in OD_THRUPUT_LIMIT & ID_THRUPUT_LIMIT
   FE_SGP_402984_ALLOW_MULTIPLE_FAIL_STATE_RETRIES                               = 1   # Allow multiple state retries during mass pro
   HDI_ENABLED                                                                   = 0
   VBART51_MEASURE_ODTRACK                                                       = 1   # Enable VBAR T51 measure on OD Tracks of OD ZOnes
   FE_0184418_357260_P_USE_TRACK_WRITES_FOR_CLEANUP                              = ( ADAPTIVE_GUARD_BAND & (not SMRPRODUCT) ) # Perform track writes for TRACK_CLEANUP (vs LBA writes)
   FE_SGP_81592_RETRY_DURING_TRACK_CLEANUP_4_CHS_MODE                            = ( 1 & FE_0184418_357260_P_USE_TRACK_WRITES_FOR_CLEANUP )
   FE_0189781_357595_HEAD_RECOVERY                                               = 0
   ADD_SPINUP_AFTER_UPDATING_FLASH                                               = 0
   CheckAverageQBER_Enabled                                                      = 1
   ENABLE_ZEST_BIT_IN_SAP                                                        = 1
   FE_0253168_403980_RD_OPTI_ODD_ZONE_COPY_TO_EVEN                               = 0   # opti on odd zones, copy results to adjacent even zones
   TTR_REDUCED_PARAMS_T251                                                       = 0   # reduced params to tune for PreOpti, Bpinominal & Vbar
   TTR_BPINOMINAL_V2                                                             = 0   # 2-pt BpiNom 1
   TTR_T176_READ_PC_FILE                                                         = 0   # rw_gap_cal - read from pc file
   TTR_BPINOMINAL_V2_CONST_AVG                                                   = 0 & (TTR_BPINOMINAL_V2)
   AGC_SCRN_DESTROKE                                                             = 0 # Enable ADC Screen Destroke without new RAP (same as YarraBP)
   AGC_SCRN_DESTROKE_FOR_SBS                                                     = 1 # Enable AGC Screen Destroke for SBS
   AGC_DATA_COLLECTION                                                           = (not (RW30 | RL40)) & (not AGC_SCRN_DESTROKE)
   AGC_SCRN_DESTROKE_WITH_NEW_RAP                                                = ( (not SMRPRODUCT) & AGC_SCRN_DESTROKE )  # Enable ADC Screen Destroke wtih new RAP
   IN_DRIVE_AFH_COEFF_PER_HEAD_GENERATION_SUPPORT                                = 0
   IN_DRIVE_AFH_COEFF_PER_HEAD_GENERATION_SUPPORT_DATA_COLLECTION                = (0 & IN_DRIVE_AFH_COEFF_PER_HEAD_GENERATION_SUPPORT)
   Enable_Reconfig_WTF_Niblet_Level_Check                                        = 1   # Re-config Waterfall Control
   FE_0131335_220554_NEW_AUD_LODT_FLOW                                           = 1
   SEND_OPERATION_METRICS                                                        = 1
   EWAC_FIXED_FREQ                                                               = 0  # EWAC measurement with fixed frequency
   RUN_4PCT_ZAP                                                                  = 0
   RUN_3P5PCT_ZAP                                                                = ROSEWOOD7 or CHENGAI # RZAP 7% and WZAP 3.5
   AFH2_FAIL_BURNISH_RERUN_AFH1                                                  = ( CHENGAI | ROSEWOOD7 )
   ENABLE_CLR_SETTLING_STATE                                                     = 0
   Delta_BER_IN_CLR_SETTLING                                                     = ENABLE_CLR_SETTLING_STATE
   CLR_SETTLING_CLOSEDLOOP                                                       = 0 & ENABLE_CLR_SETTLING_STATE
   GOTF_GRADING_TABLE_BY_RPM                                                     = 0   # sync with YarraBP
   RECONFIG_RPM_CHK                                                              = 0   # sync with YarraBP
   FE_SGP_EN_REPORT_WTF_FAILURE                                                  = 1
   FE_SGP_EN_REPORT_RESTART_FAILURE                                              = ROSEWOOD7 # temp disable EC12168
   EN_REPORT_SAME_CAPACITY_WTF                                                   = 1 # Option to send unyielded WTF EC to FIS for drive with same capacity but diff tab, 1 = send, 0 = not send
   WTFCheckSectorSize                                                            = 0 # check sector size when do waterfall for ADG/rerun/ force WTF drives
   FE_0148166_381158_DEPOP_ON_THE_FLY                                            = 1 # # Enable Depop on the Fly if set to 1
   DEPOP_TESTING                                                                 = 0
   FE_0184102_326816_ZONED_SERVO_SUPPORT                                         = not HAMR # set to 1 to enable zoned servo
   FAIL_ON_INITIATOR_REVISION_CHECK_FAILURE                                      = 1 # Fail if unable to detect SIC revision
   USE_ICMD_DOWNLOAD_RIM_CODE                                                    = 0 # Download initiator code using ICmd.downloadIORimCode()
   T69EWAC_T61OW_LIMIT_FORCE_REZONE                                              = 0 # forced rezone based on t61 ow vs t69 ewac criteria
   RESET_TCC1_SLOPE_IF_BOTH_TCC1_AND_BER_OVER_SPEC                               = TEMP25_52 # Reset Tcc1 slope to default vaule if both Tcc1 slope & BER are over spec
   FE_0283799_454766_P_DTH_ADJ_ON_THE_FLY                                        = TEMP25_52 # dTh adjustment on the fly base on CRT2 BER
   ENABLE_FLAWSCAN_BEATUP                                                        = ROSEWOOD72D # Enable Flaw scan beat-up test to improve Relia GMD.
   FE_0241396_505235_FLAWSCAN_POWER_LOSS_RECOVERY                                = 1 # Power loss recovery for data flaw scan
   FE_0329412_340866_STRESS_CHANNEL_DURING_FLAW_SCAN                             = ROSEWOOD7 # During flaw scan state tighten channel setting
   ENABLE_BYPASS_T193_EC10414                                                    = 1
   ENABLE_BYPASS_T151_EC10007                                                    = 0
   ENABLE_1ST_MDW_TRACK_CAL                                                      = 0 # data collection only
   ENABLE_ON_THE_FLY_DOWNGRADE                                                   = 1 # Down grade on the fly by error code
   CHANGE_PREAMP_GAIN_BEFORE_T177_RETRY                                          = 0
   SGP_4K_MAX_LBA_CALCULATION                                                    = 1
   COMBO_SPEC_SCRN                                                               = 0 # enable GMD/NMD combo screen in WRITE_SCRN
   COMBO_SPEC_SCRN_FAIL_ENABLE                                                   = 0 # enable fail reporting for COMBO_SPEC_SCRN
   FE_0178765_231166_P_SAVE_INITIATOR_INFO_FILE                                  = 1 # Gemini cell reprogramming
   FE_0205626_231166_P_VER_1_INIT_PKL_FILE                                       = 1 # Use the version 1 pkl file for saving initiator information
   ENABLE_DOWNGRADE_ON_ZONE_REMAP                                                = 1 #ENABLE_ON_THE_FLY_DOWNGRADE
   FE_SGP_81592_REZAP_ON_MAXRRO_EXCEED_LIMIT                                     = not SMRPRODUCT  # switch to enable re-zap (Test 175) when maxRRO (frm Test 33) is greater than limit defined as MAX_RRO (in ServoParameters.py)
   FE_SGP_505235_MOVING_REZAP_TO_INDIVIDUAL_TEST                                 = FE_SGP_81592_REZAP_ON_MAXRRO_EXCEED_LIMIT
   FE_AFH4_TRACK_CLEAN_UP                                                        = 0 # SF3 cleanup after AFH4
   FE_SGP_81592_ADD_FULL_STROKE_RND_SK_IN_BASIC_SWEEP_2_IMPROVE_T136             = 1 # Switch to add test 30 full stroke rnd sk in basic sweep.
   CHECK_FAILURE_FOR_EC10522_IN_RS2A_2C_2H                                       = 0 # Enable to allow failure for EC10522 in READ_SCRN2A, READ_SCRN2C & READ_SCRN2H.
   HSC_BASED_TCS_CAL                                                             = 0 # T190 not supported in PreAmazon/F3Trunk  # not TRUNK_BRINGUP and not TEMP25_52   # NCTC HSC based TCS Cal
   NCTC_CLOSED_LOOP                                                              = 0 # NCTC HSC based TCS Cal Closed Loop
   ENABLE_MIN_HEAT_RECOVERY                                                      = CHENGAI # Enable minimum heat recovery
   INITIALIZE_FLAW_LIST_BEFORE_FULL_ZAP                                          = 1
   ENABLE_THERMAL_SHOCK_RECOVERY_V3                                              = 1   # Screen head instability by doing TSR using T297 data.
   FE_0322846_403980_P_DUAL_HEATER_N_BIAS_TSHR                                   = 1 # Enable writer heater and voltage bias support during T72 thermal shock head recovery.
   ENABLE_T315_SCRN                                                              = 0 # Screen head instability using P315_INSTABILITY_METRIC data
   RD_OPTI_SEPARATE_PARM_FOR_320G                                                = 0
   ENABLE_TCC_RESET_BY_HEAD_BEFORE_AFH4                                          = 0 # Use to enable TCS RESET by head before AFH4
   FE_0205578_348432_T118_PADDING_BY_VBAR                                        = 1 # T118 padding by vbar
   ENABLE_T118_EXTEND_ISOLATED_DEFECT_PADDING                                    = 0 # Enable T118 extend isolated defect padding. (Requested by Sebastian to close RW2D Relia MSD NMD issue.)
   BPICHMS                                                                       = 0 # Quick BPI at Backoff Clearance
   HARD_CODE_SERIAL_FORMAT_CMD                                                   = 1
   ENABLE_HMSCAP_SCREEN                                                          = 0 # enable HMSCAP screen
   ENABLE_CSC_SCREEN                                                             = 0 # enable CSC screen
   ENABLE_SCRN_HEAD_INSTABILITY_BY_SOVA_DATA_ERR                                 = 0 # enable screen head instability by sova data err
   FE_0368834_505898_P_MARGINAL_SOVA_HEAD_INSTABILITY_SCRN                       = RL40 # enable marginal sova head instability screen
   ENABLE_DATA_COLLECTION_IN_READSCRN2H_FOR_HEAD_INSTABILITY_SCRN                = 0 # enable data collection in readscrn2h for head instability screen by sova data err
   ENABLE_DATA_COLLECTION_IN_READSCRN2_FOR_HEAD_INSTABILITY_SCRN                 = not SMRPRODUCT  # enable data collection in readscrn2 for head instability screen by sova data err
   ENABLE_HEAD_INSTABILITY_SCRN_IN_READSCRN2                                     = ( ENABLE_DATA_COLLECTION_IN_READSCRN2_FOR_HEAD_INSTABILITY_SCRN )   # enable head instability screen by sova data err in readscrn2
   FE_SGP_81592_PWRCYCLE_RETRY_WHEN_T175_REPORT_EC11087_IN_ZAP                   = 1 # Added pwr cycle n retry once if Test 175 reported EC11087 (hang) in FNC2 ZAP state.
   FNG2_Mode                                                                     = 2 # FNG2_Mode 1 for simplified method, 2 for RequestService (restart with 4C) method
#CHOOI-18May17 OffSpec
   FORCE_SERIAL_ICMD                                                             = 1 # if 1, then force serial commands, even in IO cells - Loke
#   FORCE_SERIAL_ICMD                                                             = 0 # if 1, then force serial commands, even in IO cells - Loke
   SP_RETRY_WORKAROUND                                                           = 1 # if 1, workaround SP retries not as robust as IO
   FE_0246520_356922_SPMQM_Y2_RETRY                                              = 1 # Level F Y2 Retry setting after power cycle
   FE_0249024_356922_CTRLZ_Y2_RETRY                                              = 1 # Level F Y2 Retry setting after ctrlz
   FE_0283639_402984_TURN_OFF_THRUPUT_RAW_AND_LARGE_SHOCK_DETECT                 = 0 # Turn off large shock detection during FIN2 throughput test for RW7
   FE_0255791_356922_SPMQM_ZONETRUPUT_WRITE_READ                                 = 1 # SPMQM IDT_PM_ZONETHRUPUT - Do Write Followed by Read
   RW72D_SBS_RETAIL_MQM                                                          = 0 # RW72D SBS MQM modules

   ENABLE_DIHA_FOR_INSTABLE_HD_SCRN                                              = 1 # Detection of Inconsistent Harmonic Amplitude Excitation to capture head instabilities
   CLEAR_DATA_SCRUB_TABLE_AFTER_CLEAR_ALT_LIST                                   = 1
   ENABLE_DESTROKE_BASE_ON_T193_CHROME                                           = 0 # enable Destroke base on T193 Chrome
   FE_SGP_402984_RAISE_EWLM_CLEAR_FAILURE                                        = 1 # Raise exception if EWLM SMART log page B6h not cleared
   FE_0219921_402984_ENABLE_CLEAR_EWLM                                           = 1 # Activate clearing of EWLM
   BYPASS_N2_CMD                                                                 = 0 # For AngH product, F3 code not yet ready for /1N2
   USE_ZERO_LATENCY_WRITE_IN_T50_T51                                             = ((not MARVELL_SRC)<<4 ) & 0x10   # set to 0x10 (cword1 bit 4) to turn on ZLW. set to 0 to turn off ZLW
   FE_SGP_81592_DISPLAY_ZAP_AUDIT_STATS_IN_OPTIZAP                               = 0 # enable displaying of zap audit stats during minizap
   AutoFAEnabled                                                                 = 0 # enable auto FA
   FE_ENABLE_SFT_BEATUP                                                          = 0 # enable MQM beatup after serial format.
   DOS_THRESHOLD_BY_BG                                                           = 1 # set Dos STEThresholdScalar, STERange and ATIThresholdScalar   according to drive business group
   DOS_THRESHOLD_BY_ATI                                                          = not DOS_THRESHOLD_BY_BG # set Dos STEThresholdScalar, STERange and ATIThresholdScalar   according to Head's Write Screen ATI result
   SKIPZONE                                                                      = 0
   VARIABLE_SPARES                                                               = 1
   FE_0349420_356688_P_ENABLE_OPTI                                               = 0 # run opti when bpi adjust triggered
   FE_0319957_356688_P_STORE_BPIP_MAX_IN_SIM                                     = ROSEWOOD7 # store BPIP_MAX to SIM to support variable spare BPI margin check
   FE_0363840_356688_P_ENABLE_GT_WRITE                                           = 1 # write last trk of each zone to overwirte Aperio left over signal between the zone to zone boundary.
   FORCE_WTF_SET_ATTR_BY_NIBLET_TABLE                                            = 1 # Change waterfall req attr to the correct one based on niblet table
   FORCE_UPDATE_BPI_ALL_HEADS_ALL_ZONES                                          = 1 # if enable will update the BPI config all head all zone
                                                                                     # during BPIN, BPIN2, WATERFALL
   #DiagOverlayWipeOnly                                                          = YARRAR  # to wipe the Diag Overlay
   DiagOverlayWipeOnly                                                           = 0 # to wipe the Diag Overlay, disable for now
   FE_0221365_402984_RESTORE_OVERLAY                                             = (1 & DiagOverlayWipeOnly)  # Recover TGT and OVL codes prior to GIO or MQM
   FE_SGP_T191_BPI_PUSH_BY_ZONE                                                  = 0
   CPC_ICMD_TO_TEST_NUMBER_MIGRATION                                             = 1 #This switch is to be enabled for CPC non-intrinsic function testing
   FE_SGP_81592_MOVE_MDW_TUNING_TO_SVO_TUNE_STATE                                = 1
   FE_SGP_REPLACE_T152_WITH_T282                                                 = 1 # Use Test 282 instead of 152 for Bode
   FE_SGP_ENABLE_BIAS_CAL_SCREEN_VIA_TEST136                                     = 1
   ENABLE_NEW_CERT_DONE_BIT12                                                    = 0
   RUN_MOTOR_JITTER_SCRN                                                         = 0 # Run Motor Jitter Screen
   RUN_ATS_SEEK_TUNING                                                           = ( ROSEWOOD7 or CHENGAI ) # Run ATS Seek Tuning
   FE_0238515_081592_SET_ZAP_SEC_CYL_TO_20PCT_OF_MAX_TRK                         = ( ROSEWOOD7 or CHENGAI ) #Enable dynamic updating of SEC_CYL of T175 at 20% of max trk of each hd
   FE_0130200_231166_SAVE_ZAP_INCR_STATE_FOR_PLR                                 = ( 1 ) #Zap Power Loss recovery by saving head done
   ENABLE_T175_ZAP_CONTROL                                                       = ( 1 ) # Uses T175 to turn ZAP on/off instead of T011 & T178. Reduce CM load.
   WA_REMOVE_PCBA_SN_CHK_FRM_STATE_TABLE_DURING_EM_PHASE                         = 0 # this switch will remove PCBA_SN_CHECK state in PRE2
   pztCalTestEnabled                                                             = ( ROSEWOOD7 or CHENGAI ) # PZT Calibration T332 enable
   CAL2_OPERATION_ENABLE                                                         = ( ROSEWOOD7 or CHENGAI ) # Enable CAL2 operation (split from PRE2 LIN_SCREEN2)
   SDAT2_OPERATION_ENABLE                                                        = 1 # Enable SDAT2 operation after FNC2
   FE_SGP_505235_ENABLE_REZAP_ATTRIBUTE                                          = 1
   FE_0112851_007955_ADD_HWY_OPTION_TO_SETSAP_HEADTYPE                           = 1   # Ability to set SAP bit for HWY hds
   GANTRY_INSERTION_PROTECTION                                                   = 0   #Enable the disabling of a cell to reduce the probability of insertion disturbance during a sensitive test
   ENABLE_SMART_TCS_LIMITS_DATA_COLLECTION                                       = 0   # enable smart TCS limits for data collection only
   ENABLE_SMART_TCS_LIMITS                                                       = 0   # enable smart TCS limits
   ENABLE_TCC_SCRN_IN_AFH4                                                       = (ROSEWOOD7 or CHENGAI) # Screen TCC in AFH4
   FE_0228550_357260_P_LIMIT_LOGICAL_TRACK_RANGE_PER_PHYSICAL_MAX                = 0   # For Track Cleanup calculations, use Log Trk of Max Physical track as max Logical (Accouts for cases where additional log track may exist - e.g. Media Cache
   BF_0209197_357260_P_TRACK_CLEANUP_HANDLE_MAX_TRACK                            = 0   #KARNAKPLUSBP9 (SF in CRT2)# Handle cases at or near end of logical space
   BF_0219840_357260_P_USE_DEFECT_LOG_TO_MANAGE_TRACK_CLEANUP_ERRORS             = 0   #KARNAKPLUSBP9 (SF in CRT2)# Use Defect Log to track diag errors during writeTrackRange() (TRACK_CLEANUP)_
   BF_233858_402984_FIX_IO_DYNAMIC_RIM_TYPE                                      = 1  # Fix IO double density cell temperature sharing in dynamic rim type config
   ENABLE_HEAD_SCRN_IN_PRE2                                                      = (CHENGAI or ROSEWOOD7)   # Enable Head Screen in PRE2
   ENABLE_HEAD_SCRN_IN_FNC2                                                      = ROSEWOOD7 # Enable Head Screen in FNC2
   ENABLE_HEAD_SCRN_IN_CRT2                                                      = ROSEWOOD7 # Enable Head Screen in CRT2
   ENABLE_ATE_SCRN                                                               = (CHENGAI) & (not MARVELL_SRC)  # Enable ATE SCRN
   FE_0247889_505898_PRECODER                                                    = 0 # Enable precoder tuning, default off (Karnak plus)
   FE_0298712_403980_PRECODER_IN_T251                                            = 1 # Added precoder tuning in T251 (CheopsAM)
   FE_0311911_403980_P_PRECODER_IN_READ_OPTI_ONLY                                = (1 & FE_0298712_403980_PRECODER_IN_T251) # Run T251 precoder tuning in READ_OPTI only.
   FE_0308035_403980_P_MULTIMATRIX_TRIPLET                                       = 1 # New triplet opti
   FE_348429_0247869_TRIPLET_INTEGRATED_ATISTE                                   = not FE_0308035_403980_P_MULTIMATRIX_TRIPLET # Enable ATI/STE Test in Triplet Opti to define the maximum tuneable WP
   FE_0332552_348429_TRIPLET_INTEGRATED_OW_HMS                                   = ROSEWOOD7 # Enable OW/HMS Test in Triplet Opti to define the minimum tuneable WP
   FE_0334525_348429_INTERPOLATED_DEFAULT_TRIPLET                                = ROSEWOOD7 # Interpolated Default Triplet from OD to ID
   FE_0327703_403980_P_CERT_BASED_ATB                                            = 0 # Enable CERT_BASED_ATB, in place of bench run ATB done by RSS.
   FE_0255243_505898_T315_ODD_EVEN_ZONE                                          = CHENGAI and not SINGLEPASSFLAWSCAN # Enable Odd/Even test zone selection for head instability
   ZFS                                                                           = 0 # Run ZFS T275
   ZFS_LEGACY_MODE                                                               = 0 # Disables the flawscan pattern write, Run T275 in ZAP only mode
   FE_0234376_229876_T109_READ_ZFS                                               = CHENGAI and 0 # Read ZAP flawscan
   FE_0247538_402984_MASK_CUDACOM_ARGS_16BIT                                     = 1   # Mask cudacom *args to 16 bits. Converts signed to unsigned integers passed to CM fn function
   FE_0261922_305538_CONSOLIDATE_AFH_TARGET_ZONES                                = 1   # Consolidate all zone bit masks to single T178 call for the same target clearance settings in init rap
   DC_0205578_348432_T118_PADDING_BY_VBAR                                        = CHENGAI # Data collection (DC) for T118 Padding by vbar

   # no need to define here, control at Feature_Release_Test_Switches.py
   #FE_AFH3_TO_IMPROVE_TCC                                                        = CHENGAI or ROSEWOOD7# enable AFH3
   FE_AFH3_TO_SAVE_CLEARANCE_TO_RAP                                              = 1
   ENABLE_T396_DATACOLLECTION                                                    = 1   # use to control T396 data collection
   FE_0315237_504266_T240_DISABLE_SKIP_TRACK                                     = 1   # mapping out the test track
   FE_0315271_348085_P_OPTIMIZING_TCC_BY_BER_FOR_CM_OVERLOADING                  = 1

#CHOOI-26May16 OffSpec
   OOS_Code_Enable = 0
   FE_0180898_231166_OPTIMIZE_ATTR_VAL_FUNCS                                     = 1   # optimize attr val and reduce time and complexity

   # --- 3 tier switches --
   if 0:    # Reserved for 3-tier phase eval
      FE_0180513_007955_COMBINE_CRT2_FIN2_CUT2                                      = (YARRAR)  # A merge of CRT2 & CUT2 states into FIN2, for I/O test time savings
      FE_0185032_231166_P_TIERED_COMMIT_SUPPORT                                     = FE_0180513_007955_COMBINE_CRT2_FIN2_CUT2  # Implement tiered commit support
#      FE_0180898_231166_OPTIMIZE_ATTR_VAL_FUNCS                                     = 1   # optimize attr val and reduce time and complexity
      FE_0185033_231166_P_MODULARIZE_DCM_COMMIT                                     = FE_0185032_231166_P_TIERED_COMMIT_SUPPORT   # Modularize the DCM ACMT functions for better re-usability
      FE_0190240_007955_USE_FILE_LIST_FUNCTIONS_FROM_DUT_OBJ                        = (YARRAR)  # Use filelist functions in Drive.py - moved from setup.py
      BF_0196490_231166_P_FIX_TIER_SU_CUST_TEST_CUST_SCREEN                         = 1
      FE_0208720_470167_P_AUTO_DOWNGRADE_BLUENUN_FAIL_FOR_APPLE                     = (1) # Adding auto downgrade (GOTF) for drives apple that failing EC14520 at Bluenun Scan after downgrade complete need to download new TGTA
      AutoCommit                                                                    = FE_0185032_231166_P_TIERED_COMMIT_SUPPORT
      #FE_0198600_231166_P_SEND_CMT2_INLINE_EVENT                                    = 1   # Send CMT2 event during COMMIT operation.
      FE_0221005_504374_P_3TIER_MULTI_OPER                                          = YARRAR   # To be able to run Serial Port only states within the 3-Tier flow and structure
      BF_0185687_007955_P_PREVENT_DOWNGRADE_TO_HIGHER_BG                            = 1   # Prevent "downgrade" to "higher" business group ( i.e. if started as 'STD' cant accidently be changed to 'OEM1F')
      FE_0185387_231166_P_RECONFIGURE_CONFIGVAR                                     = FE_0180513_007955_COMBINE_CRT2_FIN2_CUT2   # Allow FIN2 to be a reconfigure operation
      FE_0198029_231166_P_WWN_BEG_AND_END                                           = 1   # Write WWN to cap 100% and validate 100% if not tier and not already performed. Perform at SETUP and FIN2
      FE_0114521_007955_WRITE_WWN_USING_F3_DIAG                                     = FE_0198029_231166_P_WWN_BEG_AND_END  # Write WWN using F3 diag 'J' cmd
      FE_0152007_357260_P_DCM_ATTRIBUTE_VALIDATION                                  = 1   # DCM/drive attribute autovalidation
      BF_0183298_231166_P_FIX_DRV_MODEL_NUM_ECHO_OPT_ATTRVAL                        = FE_0180898_231166_OPTIMIZE_ATTR_VAL_FUNCS   # fix issue where drive model num wasn't echo'd for FIS validation
      FE_0156072_409401_P_ENABLE_COMPARE_TGTA_CODE                                  = 1   # Add compare TGTA code in base_IntfTest.py
      FE_0175236_231166_P_VERIFY_SERVO_CODE_IN_INTF_DNLD                            = 1   # Validate servo committed to flash
      FE_0140102_357552_ENABLE_COMPARE_CODE_FUNCTIONALITY                           = 1   # Add base_serialTest CMP_CODE functionality in base_intfTest.py

      # Downgrade
      FE_0245993_504374_P_MANUAL_COMMIT_DOWNGRADE_TO_TIER                           = YARRAR # Capability for Manual Commit, 9-Digit CC PN drives to downgrade to Tier tab, if applicable, and follow Tier flow
      FE_0156504_357260_P_RAISE_GOTF_FAILURE_THROUGH_FAIL_PROC                      = 1   # Use stateTransitionEvent to process GOTF failure
      FE_DOWNGRADE_TO_LOWER_TIER_BASED_ON_ACMS_EC                                   = FE_0185032_231166_P_TIERED_COMMIT_SUPPORT   # Commit to next lower tier if tier commit failed in ACMS based on error codes

   else:
      FE_0185032_231166_P_TIERED_COMMIT_SUPPORT                                     = 0  # Implement tiered commit support
   # --- 3 tier switches --

   # Desperado 3 switches
   FE_0308542_348085_P_DESPERADO_3                                                  = 0
   FE_348085_P_NEW_UMP_MC_ZONE_LAYOUT                                               = FE_0308542_348085_P_DESPERADO_3  # UMP zones then MC zones then Main Store.
   FE_0325260_348085_P_VARIABLE_GUARD_TRACKS_FOR_ISO_BAND_ISOLATION                 = FE_0308542_348085_P_DESPERADO_3

   #################################################################################
   ###################           special for Angsana2D              ################
   #################################################################################
   BIGS_FIRMWARE_NEED_SPECIAL_CMD_IN_F3                                         = CHENGAI # Issue T>Wfefe in F3 mode in CRT2 for BIGS feature - Only needed in RW7 2D later
   P_DELAY_AFTER_OVL_DNLD                                                       = ( ROSEWOOD7 or CHENGAI )  # Add 15 seconds delay after OVL dnld due to BIGS initialization
   CHECK_AND_WAIT_HDA_TEMP_IN_AFH                                               = 0 # Check and wait for hda temp to reach needed range

   ######################################################################
   ############## SMR related switches only : Start #####################
   ######################################################################
   SMR                                                                          = ( SMRPRODUCT )
   FE_0191830_320363_P_DISABLE_T50_51_IN_WRITE_SCREEN                           =  0   # Disable T50/51 in Write Screen for SMR
   LCO_VBAR_PROCESS                                                             = 0
   DISPLAY_SMR_FMT_SUMMARY                                                      = ( SMR )
   SMR_2D_VBAR_OTC_BASED                                                        = 0
   SMR_TRIPLET_OPTI_WITH_EFFECTIVE_TPIC                                         = 0
   SMR_TRIPLET_OPTI_SET_BPI_TPI                                                 = 0
   RUN_EAW_IN_WRITESCREEN                                                       = not ROSEWOOD7 # Disable EAW in Write Scrn
   FE_0215591_007867_COMPUTE_TPIC_AS_RATIO_MERGE_CL537310                       = ( SMR ) # new definition of the TPIC
   ENABLE_MEDIA_CACHE                                                           = SMR # Disable/Enable MC for Chengai drives
   DISABLE_UNLOAD_OPER_FOF_SCRN                                                 = ( ROSEWOOD7 or CHENGAI )
   DeltaBER_Disabled                                                            = ( ROSEWOOD7 or CHENGAI )
   FE_ENABLE_MT50_10_DATA_COLLECTION                                            = SMR  #Enable M50_10
   FE_0194980_357260_P_LIMIT_SMR_TRACK_CLEANUP_TO_VALID_BANDS                   = TRUNK_BRINGUP
   FE_0187241_357260_P_USE_BAND_WRITES_FOR_CLEANUP                              = TRUNK_BRINGUP
   FE_0254235_081592_ADDING_RETRY_WITH_PWRCYC_IN_SMR_TRACK_CLEANUP              = ( 1 & FE_0187241_357260_P_USE_BAND_WRITES_FOR_CLEANUP )
   FE_0258639_305538_CONSOLIDATE_BANDS_BEFORE_CLEANUP                           = ( THIRTY_TRACKS_PER_BAND & FE_0187241_357260_P_USE_BAND_WRITES_FOR_CLEANUP ) # Consolidate all overlapped and contiguous bands before performing band writes in track cleanup
   UMP_SHL_FLAWSCAN                                                             = 1 & SMR # Interlace scan for UMP zones, seq scan for SHL zones.
   FE_0245944_504159_USE_DFT_VAL_RADIUS_GAP_FRE_FRM_RAP_SAP                     = SMR # Use default values for Frequency, Gap & Raduis frm RAP&SAP
   FE_0252331_504159_SHINGLE_WRITE                                              = SMR # Use Shingle write
   FE_0261598_504159_SCREEN_OTF                                                 = FE_0252331_504159_SHINGLE_WRITE & 0
   FE_0336349_305538_P_RUN_SQZWRITE2_IN_CRT2                                    = FE_0252331_504159_SHINGLE_WRITE # Run another SqzWrite test in CRT2
   FE_0254388_504159_SQZ_BPIC                                                   = MARVELL_SRC # SQUEEZE BPIC Measurement
   FE_0254064_081592_CLEANUP_WKWRT_DELTABER_TRKS_USING_MC_INIT                  = ( SMR & RUN_WEAK_WR_DELTABER ) # Switch to replace +/- 1 track cleanup in WkWrt_DeltaBER state with MC Init that will wrt pass all MC zone
   FE_348429_0255607_ENABLE_BAND_WRITE_T251                                     = 1 and ( ROSEWOOD7 or CHENGAI ) # Enable Band Write when tuning Channel in SMR format
   FE_402984_271733_FAIL_DRIVE_WITH_MC_RESIDUE                                  = 1   # Option to fail drive if media cache is not cleared
   INVALID_SUPER_PARITY_FULL_PACK_WRITE                                         = 0 # enabled to replace G>Q,,22 super parity cleanup (not SMR friendly) with full pack write, temporarily
   FE_0253362_356688_ADC_SUMMARY                                                = SMR
   FE_0313724_517205_DISPLAY_SOC_INFO                                           = ROSEWOOD7   #Display SOC info in T 166
   ######################################################################
   ############## SMR related switches only : End #######################
   ######################################################################

   ######################################################################
   ############## KARNAK related switches only : Start #####################
   ######################################################################
   MR_RESISTANCE_MONITOR                                                        = 0
   WA_DETCRTA_NOT_CONNECT_SOC                                                   = 0
   SKIP_MR_RESISTANCE_CHECK                                                     = 0
   RSS_TARGETLIST_GEN                                                           = 0 # turn on it when need to eval target list
   FE_0188555_210191_NVC_SEQ_REV3                                               = 1 # Initialize and test flash after CUST_CFG in FIN2
   FE_NVC_SEQ_REV4                                                              = 1 # Rev 4 of the sequence For AngsanaH, to set together with Rev3
   DISABLE_NVCACHE_WHILE_TESTING                                                = 0 # To disable NVCACHE while testing
   FE_0191751_231166_P_172_DUMP_PREAMP                                          = 0 #
   FE_0141107_357260_P_INCREASE_CMD_TO_FOR_SKIP_CODE_CHECK                      = 0 # Increase TO from 10 to 30 for CTRL_Z when checking for F3 code.
   ASD_DEFECT_LIST_INITIATION                                                   = 0 # initial defect list for ANGSANAH ASD drive
   FE_0124304_231166_FAIL_IF_NO_FLAG_FILE_FOUND                                 = 0 # Fail if process can't ID the code on the drive to load the extern flags- also provid permuation based code lookup
   T118_OPTIMIZED_PADDING_PARAMETERS                                            = 1 # Flag to select T118 optimized padding parameters
   DNLD_F3_5IN1_SED                                                             = 0 ##ANGSANAH
   ENABLE_NAND_SCREEN                                                           = 1 # Screen NAND Flash life cycle and bad clumps
   FE_ENHANCED_TRIPLET_OPTI                                                     = 0 # Triplet OSD/OSA Limiting for recovery of strong write
   FE_0243269_348085_FIX_BPI_TPI_WATERFALL                                      = ROSEWOOD7 or CHENGAI
   WA_0247335_348085_WATERFALL_WITH_10_DIGITS_PARTNUMBER                        = 0
   FE_0243459_348085_DUAL_OCLIM_CUSTOMER_CERT                                   = ROSEWOOD7
   FE_0246017_081592_ENABLE_RV_SENSOR_IN_CERT_PROCESS                           = 0 # KARNAKPLUSBP9 and (not TRUNK_BRINGUP)
   FE_0250198_348085_AUTO_DETECT_TEST_TRACK_WEAK_WR_DELTABER                    = (ROSEWOOD7 or CHENGAI)
   FE_0250539_348085_MEDIA_CACHE_WITH_CAPACITY_ALIGNED                          = (ROSEWOOD7 or CHENGAI)
   FE_0251080_081592_ENABLE_SDD_SED_FOR_LINGGI_BASE_PRODUCT                     = THIRTY_TRACKS_PER_BAND   # Flag to enable code download flow (5-1) for SDD & SED
                                                                                      # config for product using Linggi branch
   CLEAR_NAND_FLASH_ON_RECYCLE_PCBA                                             = 0
   WA_0264977_321126_WAIT_UNTIL_DST_COMPLETION                                  = 1   # No command to abort DST. After PLR, need wait some time to avoid 10340

   ######################################################################
   ############## KARNAK related switches only : End #######################
   ######################################################################

   ######################################################################
   ############## KARNAK 2D SMR VBAR                #####################
   ######################################################################
   VBAR_2D                                                         = SMR #( CHENGAI )
   VBAR_ADP_EQUAL_ADC                                              = 0 or HAMR # Set BPIP/TPIP = BPIC/TPIC, only when running data collection
   OTC_BASED_QTPI                                                  = VBAR_2D  # Use OTC based Measurement in QTPI
   VBAR_SKIP_MIN_CAPABILITY_CHECK                                  = VBAR_2D  # Skip checking of BPI/TPI below minimum configs
   FAST_2D_VBAR                                                    = VBAR_2D  # Use T211 to generate BER vs BPIC Slope
   FAST_2D_VBAR_INTERLACE                                          = (0 & VBAR_2D & FAST_2D_VBAR) or (FE_0258650_480505_SKDC_M10P_PROCESS_TIME_REDUCTION)  # Interlace Measurement in Fast VBAR
   WP_FAIL_SAFE_SATURATION                                         = VBAR_2D  # Fail safe No saturation EC13409 during WP
   FAST_2D_VBAR_XFER_PER_HD                                        = VBAR_2D  # Transfer Function Per Head
   FAST_2D_VBAR_XFER_PER_HD_FILTER                                 = VBAR_2D  # Enable Filtering of BPIC and TPIC_S when picking the best Target SFR
   FAST_2D_VBAR_XFER_PER_HD_DELTA_BPI                              = VBAR_2D  # Enable BPI Delta when calculation for BPIC
   FAST_2D_VBAR_2DIR_SWEEP                                         = VBAR_2D  # Enable 2x T211 Call to trigger BPI Sweep data using higher and lower target SFRs
   FAST_2D_VBAR_TPI_FF                                             = VBAR_2D # TPI Feed Forward during Fast 2D Measurement
   FAST_2D_VBAR_UNVISITED_ZONE                                     = 1 & FAST_2D_VBAR_XFER_PER_HD & (not FAST_2D_VBAR_INTERLACE) # Use PolyFit when predicting parameters for VBAR Unvisted Zone
   FAST_2D_VBAR_UMP_FIX_BEST_TARGET_SOVA_BER                       = FAST_2D_VBAR_UNVISITED_ZONE
   FAST_2D_VBAR_TESTTRACK_CONTROL                                  = FAST_2D_VBAR_UNVISITED_ZONE & (not TRUNK_BRINGUP)
   FAST_2D_MEASURE_SQZ_BER                                         = FAST_2D_VBAR_UNVISITED_ZONE
   FE_0320673_356688_P_BEST_TARGET_SOVA_BER_FAVOUR                 = 1 and VBAR_2D  # best target sova selection biase to DefaultTargetSFRIndex
   FE_0253509_348429_UVZ_IMPROVE_FILTERING1                        = (SMR ) & FAST_2D_VBAR_UNVISITED_ZONE  # Add 2nd and 2nd zone to the last in disabled 5pt median filter, also use mean in lumping algo
   FE_0289797_348429_ZONE_ALIGN_IMPROVE_FILTERING                  = MARVELL_SRC # Filtering method for use in Zone Alignement
   EFFECTIVE_TPIC_EQUAL_TPIS                                       = 0  # When saving format, save Track Pitch as TPIS instead of EFfective TPI
   skipVBARDictionaryCheck                                         = VBAR_2D # Skip VBAR Dictionary Check specially when adding new keys but skipping the entire PRE2 process.
   #**** VBAR MARGIN BY OTC SWITCHES ****#
   VBAR_MARGIN_BY_OTC                                              = MARVELL_SRC # Run T211 OTC Margin measurements in VBAR
   OTC_BASED_RD_OFFSET                                             = VBAR_2D  # set read ujog offset in RAP using VBAR OTC Bucket Rd Offset
   OTC_MEAS_ONLY_SHINGLE_DIR                                       = VBAR_2D  # Set to measure OTC Bucket only in selected shingle direction during VBAR_OTC
   OTC_RESET_RD_OFFSET_BEFORE_TUNE                                 = not FAST_2D_VBAR_UNVISITED_ZONE # reset read offset before tuning.
   OTC_REV_CONTROL                                                 = FAST_2D_VBAR_UNVISITED_ZONE # VBAR_OTC to measure at rev control to save test time
   VBAR_2D_DEBUG_MODE                                              = 0  # 2D VBAR FAST DEBUG MODE
   DO_NOT_SAVE_FORMAT                                              = 0
   #**** TMR/Noise Inject SWITCHES ****#
   MEASURE_TMR                                                     = 0  #meausure TMR during VBAR OTC
   NOISE_INJECTION_ON_TMR_DURING_T211                              = 0  # Add Nooise Injection on T211 at VBAR_ZN
   NOISE_INJECTION_ON_TMR                                          = 0  # Add Nooise Injection on TMR State
   APPLY_FILTER_ON_SMR_TPI                                         = VBAR_2D  # Appply filter on both TPI IDSS and ODSS
   FE_0318595_348429_P_APPLY_FILTER_ON_UMP_TPI                     = 1 #VBAR_2D & RW30 | RL40 # Appply filter on UMP TPI DSS
   OTC_BUCKET_LINEAR_FIT                                           = 0  & VBAR_MARGIN_BY_OTC # use linear fit to finally compute the TPI OTC
   OTC_SKIP_ZONE_MAXIMIZATION                                      = 1   # Skip relaxing track pitch during Calculate track pitch, do not turn On in Mass PRO
   OTC_BUCKET_ZONE_POLYFITTED                                      = 0  & VBAR_MARGIN_BY_OTC # Zone Fitting in TPI OTC
   OTC_NOT_STOP_ON_TARGET                                          = 0 & VBAR_MARGIN_BY_OTC # T211 OTC Measurement stop only when TPI adjust exceed +/-7%, this is to have enough data for linear regression
   FE_0288274_348429_OTC_MARGIN_MULTIZONE                          = 1 & VBAR_MARGIN_BY_OTC # Consolidate multiple test zones into ST single call
   #**** VBAR MARGIN BY OTC TRACK PITCH SWITCHES ****#
   FE_0293889_348429_VBAR_MARGIN_BY_OTCTP                          = MARVELL_SRC # Switch to enable OTC margin version 2 that reduce test time
   FE_0293889_348429_VBAR_MARGIN_BY_OTCTP_INTERBAND_MARGIN         = not FE_0308542_348085_P_DESPERADO_3 # switch to enable interband Margin for SMR zones
   FE_0293889_348429_VBAR_MARGIN_BY_OTCTP_RD_OFFSET_CALC           = 1 & FE_0293889_348429_VBAR_MARGIN_BY_OTCTP # switch to enable read offset calculate by OTC measurements
   FE_0293889_348429_VBAR_MARGIN_BY_OTCTP_OVERRIDE_TP_TG           = 0 # switch to override the desperadoplus picker TP and TG maximization
   FE_0293889_348429_VBAR_MARGIN_BY_OTCTP_USE_MULTI_WRITES         = 0 # switch to use multi writes OTC instead of single write
   FE_0293889_348429_VBAR_MARGIN_BY_OTCTP_INTERBAND_MEAS           = not FE_0308542_348085_P_DESPERADO_3 # switch to measure interband OTC
   # Log Opti Switches
   T251_TURNOFF_REPORT_OPTIONS_DURING_VBAR_ZN                      = 0
   T211_TURNOFF_REPORT_OPTIONS_DURING_2DVBAR_TPIC_MEAS             = 1 # reduce log size
   T211_MERGE_READ_OFFSET_TBL_INTO_TPI_MEAS_TBL                    = 1
   FE_0273368_348429_ENABLE_TPINOMINAL                             = 0 # Switch to Enable TPINOMINAL before TRIPLET_OPTI and VBAR TUNING
   FE_0273368_348429_TEMP_ENABLE_TPINOMINAL_FOR_ATI_STE            = ROSEWOOD7 # temporary switch to enable TPINOMINAL before TRIPLET_OPTI when ATI STE Feature Turned On
   FE_0279318_348429_SPLIT_2DVBAR_MODULES                          = ROSEWOOD7 # Switch to split VBAR_ZN into 2D VBAR Modules.
   FE_0309814_348429_SPLIT_VBAR_MARGIN_MODULES                     = ROSEWOOD7 & FE_0279318_348429_SPLIT_2DVBAR_MODULES# Switch to split VBAR_MARGIN into Sub Modules.
   FE_0281130_348429_ENABLE_SINGULAR_SMR_DIR_SHIFT                 = 1 # Switch to enable single interzone SMR Direction Shift by head
   FE_0247196_334287_FIXED_WP_FQ_ET                                = 0
   SMR_SGL_SHINGLE_DIRECTION_SWITCH                                = 0
   FE_0228288_336764_P_PAUSE_CRITICAL_LOCATION_AT_VBAR_FOR_LA_CM_REDUCTION   =  1
   FE_0232067_211428_VBAR_USE_DESPERADO_PLUS_FORMAT_PICKER         = (SMR)
   FE_0257373_348085_ZONED_SERVO_CAPACITY_CALCULATION              = 0 & CHENGAI
   FE_0257006_348085_EXCLUDE_UMP_FROM_TCC_BY_BER                   = SMR
   FE_0254909_348085_VBAR_REDUCDED_TG                              = SMR
   FE_0257372_504159_TPI_DSS_UMP_MEASURMENT                        = 0 & FAST_2D_VBAR_UNVISITED_ZONE
   FE_CONSOLIDATED_BPI_MARGIN                                      = 1 & (FAST_SCP_HMS | SCP_HMS | FE_SEGMENTED_BPIC | (FE_0254388_504159_SQZ_BPIC and not TRUNK_BRINGUP) ) # Turn On to run Consolidated Margin when running SCP_HMS and New Segmented BPIC Tuning
   VBAR_TPI_MARGIN_THRESHOLD_BY_HD_BY_ZN                           = RUN_ATI_IN_VBAR | VBAR_MARGIN_BY_OTC   #TPI margin is computed using OTC instead of ATI
   CAL_TRUE_MAX_CAPACITY                                           = VBAR_TPI_MARGIN_THRESHOLD_BY_HD_BY_ZN #this depends on this flag
   FE_0258044_348085_WATERFALL_WITH_ONE_TRK_PER_BAND               = 0 #THIRTY_TRACKS_PER_BAND
   FE_0262424_504159_ST210_SETTING_FORMAT_IN_ZONE                  = THIRTY_TRACKS_PER_BAND # Calling t210 setting format by passing param in term of zone
   FE_0261758_356688_LBR                                           = (1 & FE_0232067_211428_VBAR_USE_DESPERADO_PLUS_FORMAT_PICKER) and not FE_0308542_348085_P_DESPERADO_3
   FE_0335607_356688_P_TRIGGER_LBR_BY_CONDITION                    = 1 & FE_0261758_356688_LBR   # trigger LBR by condition
   FE_0385234_356688_P_MULTI_ID_UMP                                = 0   # Cactus multiple ID ump zones
   FE_0279297_348085_PROG_MC_UMP_IN_RAP                            = ROSEWOOD7
   FE_0332676_348085_P_SUPPORT_REVBAR_AT_CAL2_FOR_DEPOP            = ( RW31 |  RL41 )
   USE_TEST231_RETRIVE_BPI_PROFILE_FILE                            = not FE_0332676_348085_P_SUPPORT_REVBAR_AT_CAL2_FOR_DEPOP
   FE_0298709_348085_P_PRECISE_MEDIA_CACHE_SIZE_ALLOCATION         = 1
   FE_0309959_348085_P_DEFAULT_580KTPI_FOR_DATA_TRACK_SUPPORT      = 0
   FE_0321705_348429_P_ADD_SHIFTZONE_IN_MARGIN                     = 1 # include SMR shift zone boundary in margin measurements
   FE_0376137_348429_P_ADD_SHIFTZONE_IN_MARGIN_BY_HD               = 1 # include SMR shift zone boundary in margin measurements by head
   FE_0325893_348429_P_OD_ID_RESONANCE_MARGIN                      = ( RW30 | RL40 ) # Enable more backoff on BPI/TPI margin at OD/ID zones for resonance.
   FE_0325513_348429_P_RUN_PRE_VBAR_PES                            = 0 and not (FE_0310548_348429_P_CM_REDUCTION_REDUCE_VBAR_DATA) # Run pre VBAR PES on test zones
   FE_0338482_348429_P_DESPERADOPLUS_EFFECTIVE_TPI_CALC            = 0 # Calculate using desperado plus effective tpi
   FE_0345101_348429_P_AVM_RD_OFFSET_AND_CHANNEL_TUNE              = 1 # Enable Read Offset Tuning before AVM and Channel Tuning before Margin OTC
   FE_0345891_348429_TPIM_SOVA_USING_FIX_TRANSFER                  = 1 # Enable AVM Estimator TPIM SOVA using fixed transfer between TPIM and SQZ SOVA BER

   FE_0358600_322482_P_ESNR_CBD                                    = 0    # T488 to measure eSNR and CBD
   ######################################################################
   ############## KARNAK 2D SMR VBAR        : End #######################
   ######################################################################

   #################################################################################
   ###################       special for Common 2 Temp CERT         ################
   #################################################################################
   FE_0258915_348429_COMMON_TWO_TEMP_CERT                                        = TEMP25_52 # Turn On Common 2Temp CERT, ambient PRE2/CAL2/FNC2 and hot CRT2
   FE_0258915_348429_COMMON_TWO_TEMP_CERT_SCRN_A00001                            = 0 & FE_0258915_348429_COMMON_TWO_TEMP_CERT # Turn on Burnish Spec for Common 2Temp CERT
   FE_0258915_348429_COMMON_TWO_TEMP_CERT_SCRN_A00002                            = 0 & FE_0258915_348429_COMMON_TWO_TEMP_CERT # Turn on ID Burnish Spec for Common 2Temp CERT
   FE_0258915_348429_COMMON_TWO_TEMP_CERT_SCRN_A00003                            = 0 & FE_0258915_348429_COMMON_TWO_TEMP_CERT # Turn On Mean HMSC and min HMSC screen for common 2Temp CERT
   FE_0258915_348429_COMMON_TWO_TEMP_CERT_SCRN_A00004                            = 0 & FE_0258915_348429_COMMON_TWO_TEMP_CERT # Turn On ID Region Verified and Unverified Flaw Screen for common 2Temp CERT
   FE_0258915_348429_COMMON_TWO_TEMP_CERT_SCRN_A00005                            = 0 & FE_0258915_348429_COMMON_TWO_TEMP_CERT # Turn On High Severity TA in AFH Test Zones screen for common 2Temp CERT
   FE_0258915_348429_COMMON_TWO_TEMP_CERT_SCRN_A00006                            = 0 & FE_0258915_348429_COMMON_TWO_TEMP_CERT # Turn On LUL Time Screen for common 2Temp CERT
   FE_0258915_348429_COMMON_TWO_TEMP_CERT_SCRN_A00007                            = 0 & FE_0258915_348429_COMMON_TWO_TEMP_CERT # Turn On T250 and TSR Screen for common 2Temp CERT
   FE_0258915_348429_COMMON_TWO_TEMP_CERT_SCRN_A00008                            = 0 & FE_0258915_348429_COMMON_TWO_TEMP_CERT # Turn On TCC and HMSC Screen
   FE_348429_COMMON_TEST_POSITION                                                = 0 & FE_0258915_348429_COMMON_TWO_TEMP_CERT # Test Zone Position to point to common reference
   FE_348429_DYNAMIC_CERT_RECOVERY                                               = 0 & FE_0258915_348429_COMMON_TWO_TEMP_CERT # Enable Dynamic CERT Recovery, initial implementation to tweak zone position
   FE_OPEN_UP_DTH_VALUE                                                          = 1 & FE_0258915_348429_COMMON_TWO_TEMP_CERT # Open up dTH temp trigger to avoid trigger during CERT
   #################################


   ######################################################################
   ############## ROSEWOOD7 switches      : Start #######################
   ######################################################################
   FE_0267637_454766_PREAMP_TEMPTRM_TUNE                          = 0 #Disable as not needed for TI7551
   FE_0274346_356688_ZONE_ALIGNMENT                               = ROSEWOOD7 # enable zone alignment for 150zone test time reduction
   FE_0367608_348429_ZONE_ALIGNMENT_TTR                           = 1 # enable zone alignment for 150zone test time reduction
   FE_0293167_356688_VBAR_MARGIN_ZONE_ALIGNMENT                   = ROSEWOOD7 # zone alignment for test zone optimization in VBAR_MARGIN
   FE_0367608_348429_VBAR_MARGIN_ZONE_ALIGNMENT_OTC_TTR           = 1 & FE_0293167_356688_VBAR_MARGIN_ZONE_ALIGNMENT # TTR zone alignment for test zone optimization in VBAR OTC MARGIN
   FE_0376137_348429_VBAR_MARGIN_ZONE_ALIGNMENT_SEG_TTR           = 1 & FE_0293167_356688_VBAR_MARGIN_ZONE_ALIGNMENT # TTR zone alignment for test zone optimization in VBAR SEG/OAR MARGIN
   FE_0376137_348429_VBAR_MARGIN_ZONE_ALIGNMENT_SHMS_TTR          = 1 & FE_0293167_356688_VBAR_MARGIN_ZONE_ALIGNMENT # TTR zone alignment for test zone optimization in VBAR SHMS MARGIN
   FE_0384272_348429_VBAR_MARGIN_ZONE_ALIGNMENT_SEG_TTR2          = 0 & FE_0293167_356688_VBAR_MARGIN_ZONE_ALIGNMENT # Further TTR in VBAR SEG/OAR MARGIN
   FE_0384272_348429_VBAR_MARGIN_ZONE_ALIGNMENT_SHMS_TTR2         = 0 & FE_0293167_356688_VBAR_MARGIN_ZONE_ALIGNMENT # Further TTR in VBAR SHMS MARGIN
   FE_0293167_356688_VBAR_MARGIN_ZONE_COPY                        = 0 # zone copy for test zone optimization in VBAR_MARGIN
   FE_0376137_356688_VBAR_MARGIN_ZONE_COPY_TTR                    = 1 & FE_0293167_356688_VBAR_MARGIN_ZONE_COPY # Implement Zone Copy in VBAR Margin Opti with TTR
   FE_0302686_356688_P_VBAR_OTC_ZONE_ALIGNMENT                    = 1 # zone alignment for test zone optimization in VBAR_OTC, VBAR_OTC2
   FE_0364447_356688_P_VBAR_OTC_ZONE_ALIGNMENT_TTR                = 1 # TTR zone alignment for test zone optimization in VBAR_OTC
   FE_0271421_403980_P_ZONE_COPY_OPTIONS                          = ROSEWOOD7  # opti on middle zones, copy results to zones on both side
   FE_0163943_470833_P_T250_ADD_RETRY_NO_FLAWLIST_SCAN            = ROSEWOOD7 # Perform an additional retry during T250_BER_FNC2 (spc_id=2) that doesn't scan the flawlist
   FE_0281621_305538_SET_SERVO_TRK_0_VALUE                        = RW12 # Update servo trk 0 (from RAP if available)
   FE_0297449_348429_P_RUN_ATI_TEST_POST_VBAR                     = 0 # Run ATI test (CAL2/PRE2) after VBAR prior to Full ZAP
   FE_0299263_348429_P_USE_FULL_AGB_CAPACITY_BY_DEFAULT           = MARVELL_SRC # Use full AGB by default during the VBAR Picker whether have excess capacity or not
   FE_0321677_356688_P_USE_FULL_AGB_CAPACITY_FOR_NATIVE_ONLY      = 1 # Use full AGB for native only during the VBAR Picker
   WA_0152247_231166_P_POWER_CYCLE_RETRY_SIM_ERRORS               = ( TRUNK_BRINGUP or SMR )# Add feature to implement a power cycle retry for read header error due to read issue after reset
   FE_0221722_379676_BYPASS_TPM_DOWNLOAD                          = ROSEWOOD7 or TRUNK_BRINGUP # Trunk code don't have TPM.LOD anymore
   ENABLE_FAFH_FIN2                                               = 1
   FE_0252611_433430_CLEAR_UDS                                    = 1
   FE_0273221_348085_P_SUPPORT_MULTIPLE_SF3_OVL_DOWNLOAD          = 1 # support multiple SF3 overlay code
   FE_0297446_348429_P_PRECISE_PARITY_ALLOCATION                  = 1 # Calculate overhead for super parity sector on the fly during format picker routine
   RUN_PREVBAR_ZAP                                                = FE_0273368_348429_ENABLE_TPINOMINAL | FE_0274346_356688_ZONE_ALIGNMENT
   RUN_TPINOMINAL1                                                = FE_0273368_348429_ENABLE_TPINOMINAL | FE_0273368_348429_TEMP_ENABLE_TPINOMINAL_FOR_ATI_STE
   FE_0284435_504159_P_VAR_MC_UMP_ZONES                           = ROSEWOOD7 # variable mc and ump zones
   GET_MANIFEST_FILE_BASED_ON_CODETYPE_ONLY                       = 1
   FE_0296361_402984_DEFECT_LIST_TRACKING_FROM_CRT2               = 0 # Trace defect lists at the start of FIN2 to verify CRT2 not causing defect lists.
                                                                      # Will tie to SINGLEPASSFLAWSCAN once RW7 full serial format stabilized.
   FE_0297451_348429_P_USE_ACTUAL_DENSITY_IN_INITIAL_PICKER       = 1 # Use actual capacity based on ADC on initial picker and margin return calculation
   FE_0337427_348429_TRACKPITCH_BASED_MARGIN_RETURN               = 1 # Use track pitch based margin return to improve the picker iteration
   FE_0337430_348429_ITERATIVE_MARGIN_RETURN                      = 1 # Use iterative Margin Return in case the initial pick > Target by > 1% Nominal
   FE_0298339_305538_T177_RETRY_CHANGE_TEST_CYL                   = MARVELL_SRC # Retry at test cyl (190k, 195k) if fail T177
   FE_0302539_348429_P_ENABLE_VBAR_OC2                            = 1 & MARVELL_SRC # Enable VBAR OC2 state to change BPIC, TPIC or both
   FE_0307316_356688_P_ADC_SUMMARY_OC2                            = 1 & FE_0302539_348429_P_ENABLE_VBAR_OC2 # to display OC2 P_VBAR_ADC_SUMMARY
   FE_0370517_348429_ADDITIONAL_OC2_BPI_PUSH                      = 1 & FE_0302539_348429_P_ENABLE_VBAR_OC2 # AMADC Enable additional BPI Margin Push, i.e. in retail
   FE_0303511_305538_P_ENABLE_UNLOAD_CURR_OVER_TIME_SCREEN        = 0 # Enable unload current screening based on stdev and max values
   FE_0303725_348429_P_VBAR_MARGIN_RELOAD                         = 1 # Switch to turn on VBAR margin reload prior to OTC Margin Tuning
   FE_xxxxxxx_348429_P_SET_ADC_FMT                                = VBAR_MARGIN_BY_OTC | FE_0254388_504159_SQZ_BPIC | RUN_ATI_IN_VBAR | FE_0253362_356688_ADC_SUMMARY # consolidate under one switch
   FE_0309812_348429_P_LOAD_BY_ACTIVE_HEAD_ZONES                  = 1 # Switch to load the BPI Config data by active heads/zones
   FE_0309818_348429_P_MOVE_POST_VBAR_STATES_TO_FNC2              = 0 # Switch to end CAL2 operation after VBAR FMT PICKER
   ENABLE_PREAMP_DIE_TEMPERATURE_RECENTER                         = 1 # preamp TI temperature compensation
   FE_0308170_403980_P_SHORTEN_MMT_LOGS                           = 0 # Suppress log for new triplet opti
   FE_0308779_356996_SNO_BODE_DATA_VERIFY                         = 1 # Verify BODE DATA after SNO. Retest if data is bogus
   FE_0309927_228373_TWO_TEMP_T189_IMPLEMENTATION                 = 1 # Two-T189 Two-T189 for Temperature Dependent Radial Timing Implementation
   FE_0349167_228373_T189_MULTI_PRE2_CRT2_COMPARISON              = 0 # Compare T189 multipliers at PRE2 vs CRT2 in CRT2
   FE_0341704_340866_BODE_SCREEN_IN_CRT2                          = CHEOPSAM_LITE_SOC # Run T282 bode screen in CRT2
   FE_0325684_340866_SHOCK_SENSOR_SCREEN                          = 0 # Shock sensor screening in T180
   FE_0314630_402984_FIX_SERIAL_ZONE_AVG_CAL                      = 1 # New method to fix serial thruput average calculation
   FE_ENABLE_HEAD_PIN_REVERSAL_SCREEN                             = 0 # Head Pin Reversal Screening Test
   TOPAZ_DRZAP_ENABLE                                             = 0 # TOPAZ and DRZAP
   FE_0316568_305538_P_ENABLE_TORN_WRITE_PROTECTION               = 1 # Enable Torn Write Protection bit in SAP in CRT2
   FE_0317559_305538_P_USE_MEDIA_PART_NUM                         = not HAMR # Use media part num to determine media type
   AutoFA_IDDIS_Enabled                                           = 1 # enable DDIS2 operation
   FE_0318342_402984_CHECK_HDA_FW                                 = 0 ^ FE_0185032_231166_P_TIERED_COMMIT_SUPPORT

   FE_0320123_505235_P_MIN_ERASURE_BER_SCREEN                     = ( RW30 | RL40 ) # Enable min erasure BER screen
   FE_0324384_518226_P_CRT2_1K_COMBO_SPEC_SCREEN                  = 1 # CRT2 1K combo spec screen 
   FE_0320340_348085_P_OAR_SCREENING_SPEC                         = 1 # Failing spec for the OAR test
   FE_0320939_305538_P_T287_ZEST_SCREEN_SPEC                      = ( RW30 ) # Enable failing spec for Prism Zest test 287
   FE_0320143_305538_P_T134_TA_SCREEN_SPEC                        = ( RW30 | RL40 ) # fail TA screening
   FE_0331797_228371_P_T134_TA_SCREEN_SPEC_TRK300                 = ( RW30 | RL40 ) # fail TA screening
   FE_0332210_305538_P_T337_OVERWRITE_SCREEN                      = 1 # fail overwrite screening
   FE_0332210_305538_P_T250_SQZ_WRITE_SCREEN                      = RW30 | RL40 | RL41 # fail sqz write screening
   FE_0332210_305538_P_SERFMT_OTF_SCREEN                          = ROSEWOOD7 # fail serial format OTF screening
   FE_0338712_305538_P_AFH_CLR_SCREENING                          = ( RW30 | RL40 ) # fail AFH clearance screening
   FE_0340631_305538_P_RDSCRN2H_COMBO_SCREEN                      = ( RW30 ) # fail Read Scrn2H max/mean BER screening
   FE_305538_P_MT50_MT10_SCREEN                                   = ( RW30 | RL40 ) # fail MT50/MT10 screening
   FE_305538_P_T297_WPE_SCREEN                                    = ( RW30 | RL40 ) # fail WPE/T297 screening
   FE_305538_P_T250_COMBO_SCREEN                                  = ( RW30 | RL40 ) # fail delta and avg BER combo screening
   FE_0365907_305538_P_T185_UFCO_OFFSET_SCREEN                    = ( RW30 | RL40 ) # fail rampcyl and lul combo screening

   FE_0322256_356996_T282_SENSITIVITY_LIMIT_CHECK                 = 1 # Run T282 for Sensitivity Limit Check
   ENABLE_SBS_DWNGRADE_BASED_ON_SOC_BIT                           = 0 # Based on SOC bit, downgrade fast drives to SBS tab
   FE_0328298_305538_P_ENABLE_ADAPTIVE_AFH_DETCR_BIAS             = 1 # Enable adaptive DETCR CD bias by zone group (need SF3 support)
   FE_AFH_RSQUARE_TCC                                             = 1 # rsquare TCC value   
   FE_0334752_305538_P_USE_HSA_PART_NUM                           = 1 # Use HSA_PART_NUM to determine IBE3 process for HWY rd tgt clr
   FE_0335463_305538_P_USE_MEDIA_PART_NUM_FOR_AFH                 = not HAMR # Use MEDIA_PART_NUM to determine UV process for rd tgt clr
   FE_0335634_228373_WHOLE_SURFACE_SCAN_IN_SNO                    = 0 # RL40  # Whole surface scan (4% - 99%) in SNO_PHASE
   FE_0338894_357001_T257_TEST_BY_DISC                            = 0 # Perform WIRRO T257 measurement by disc
   FE_305538_P_ENABLE_CTF_IN_SERIAL_FORMAT                        = ( RW30 | RL40 ) # Enable CTF before serial format and revert back after (with power cycle)
   FE_305538_P_CHANGE_OCLIM_IN_SERIAL_FORMAT                      = ( RW30 | RL40 ) # Change OCLIM before serial format and revert back after (with power cycle)
   FE_305538_P_T33_REZAP_ON_MAXRRO_EXCEED_LIMIT                   = 1 # Trigger reZap when maxRRO (frm Test 33) exceeded limit

   POST_SERVO_FLAW_SCAN_IN_CRT2                                   = 1 # Issue T126 for full surface scan in CRT2  
   

   BF_0174138_395340_P_FIX_RUN_WRONG_STATE_TEST_AFTER_PWL         = 1    # Update new "NEXT_STATE" value to objData when current state is skipped by StateTable option to help PWL at next state.
   #RFWD
   FE_0334158_379676_P_RFWD_FFV_1_POINT_5                         = 1 # Download FFV code, invoke test 393 and compare signatures in CCV
                                                                      
   FE_0362477_228373_T180_RESONANCE_RRO_SCRN_CRT2                 = 1    # T180 Resonance RRO Screen in CRT2
   ENABLE_SONY_FT2                                                = 0 # Enable SONY FT2 screening algo 
   FE_0385813_385431_Enable_MSFT_CactusScreen                     = 0   #Enable Miscrosoft Cactus test
   FE_0359619_518226_REAFH2AFH3_BYHEAD_SCREEN                     = ( RW31 | RL41 )   #AFH SCREEN
   FE_0365343_518226_SPF_REZAP_BY_HEAD                            = ( RW31 | RL41 )
   FE_0360203_518226_2D_CTU_RDG_RDCLR_COMBO_SCREEN                = ( RW31 | RL41 )
   #################################################################################
   ###################                      PBIC                    ################
   #################################################################################
   PBIC_SUPPORT                                                   = 1    #To support Performance based Intelligent Cert
   PBIC_DATA_COLLECTION_MODE                                      = 1  & PBIC_SUPPORT
   #################################################################################

   FE_228371_DETCR_TA_SERVO_CODE_SUPPORTED                        = MARVELL_SRC # turn on detcr TA (CL857615 above for cheopsaM)
   FE_PREAMP_DUAL_POLARITY_SUPPORT_DETCR_TA                       = 0   # use dual polarity in detcr TA, set to true to turn on

   #################################################################################
   ###################                    CHEOPSAM                  ################
   #################################################################################
   WA_0276349_228371_CHEOPSAM_SRC_BRING_UP                        =  MARVELL_SRC  # This switch will be enabled for cheopsam workaround only,need to review later
   FE_0276349_228371_CHEOPSAM_SRC                                 =  MARVELL_SRC  # This switch will be enabled for cheopsam feature only
   FE_0284269_228371_SUPPORT_CL794987_NEW_PREAMP_WR_CMD           =  MARVELL_SRC  # only after CL794987,trunk code
   WA_0000000_348432_FLAWSCAN_AMPLITUDE_DROP                      =  1            # Workaround for T109 amplitude drop issue.
   FE_ENABLE_T117_SCREEN_NUM_SCRATCH_PHPZ                         =  0            # RW1D TVM UDE failure CA.

   #################################################################################
   ###################                      SPFS                    ################
   #################################################################################
   SPFS_DISABLE_FSB = 0
   SPFS_DISABLE_EVM = 0
   #################################################################################
   ###################            CM LOAD REDUCTION                 ################
   #################################################################################
   FE_0227626_336764_P_REMOVE_SUMMARY_DISP_FRAME_CAL_FOR_LA_CM_REDUCTION          = ROSEWOOD7 #Remove summaryDisplayFrames calculation for reduce CM load average.
   FE_0227617_336764_P_OPTIMIZE_WRITE_READ_AFH_FRAME_FOR_LA_CM_REDUCTION          = (ROSEWOOD7) #Optimize write read frame algorithm for reduce CM load average.
   FE_0237593_336764_P_OPTIMIZE_FRAME_ACCESS_DATA_FOR_CM_LA_REDUCTION             = (ROSEWOOD7 and FE_0227617_336764_P_OPTIMIZE_WRITE_READ_AFH_FRAME_FOR_LA_CM_REDUCTION) #Change the method to access frame data
   FE_0239301_336764_P_CLEAR_DPES_FRAME                                           = (ROSEWOOD7)   # Clear DPES frame for memory reduction
   FE_0311724_348429_P_LOAD_COMMON_TRACK_PER_ZONE                                 = ( RW31 | RL41 | RW30 | RL40 | HR01 | UP01 )# Load one copy of tracks per zone in bpi config
   FE_0312337_348429_P_GET_MARGIN_MATRIX_ON_THE_FLY                               = ( RW31 | RL41 | RW30 | RL40 | HR01 | UP01 ) # skip building dictionary for Margin Matrix and get it on the fly
   FE_0312338_348429_P_GET_CLOSEST_BPI_BY_HD_ZN                                   = ( RW31 | RL41 | RW30 | RL40 | HR01 | UP01 ) # Get closest BPI file by given head and zone only

   ENABLE_TARGET_TUNING_T251                                                      = 1 # enable target tuning
   USE_NEW_PROGRAMMABLE_TARGET_LIST_0727_2015                                     = 1 and ENABLE_TARGET_TUNING_T251 # enable new target list RSS provide July 27
   FE_0295624_357595_P_FE_357595_HIRP_MOVE_TO_AFTER_AFH2                          = 1

   SPLIT_BASE_SERIAL_TEST_FOR_CM_LA_REDUCTION                                     = ( RW31 |  RL41 | RW30 | RL40 | HR01 )        # Split base_SerialTest.py
   SPLIT_VBAR_FOR_CM_LA_REDUCTION                                                 = ( RW31 |  RL41 | RW30 | RL40 | HR01 )        # Split VBAR.py
   FE_0236367_357260_P_REMOVE_REDUNDANT_T135_PARAM_DISPLAY                        = ROSEWOOD7   # Remove extra display of T135 parameters.
   FE_0227602_336764_P_REDUCE_T11_TEST_LOOP_FOR_LA_CM_REDUCTION                   = ROSEWOOD7   # Reduce T11 test loop

   T134_TA_FAILURE_SPEC                                                           = 1           # TA spec 
   T215_DETCR_TA_PAD_BY_SEVERITY                                                  = 1           # TA padding by severity
   FE_0341719_228371_MORE_PAD_LOW_SEVERITY_TA                                     = RL40
   FE_0342075_228371_TA_PADDING_SBS_2D                                            = 0 # TA padding scheme from 2D retail
   FE_0237612_336764_P_ADD_RESULT_FILE_READ_BUFFER_FOR_LA_CM_REDUCTION            = 0 # Add result file read buffer 
   UPS_PARAMETERS                                                                 = ( UP01 )
  
   FE_0345154_403980_P_ZONE_COPY_OPTIONS_T256                                     = CHEOPSAM_LITE_SOC
   
   #################################################################################
   ###################            HIGH RPM ZAP                      ################
   #################################################################################
   FE_0335299_454766_P_ENABLE_HIGH_RPM_ZAP                                        = 0 # for high RPM ZAP   
   FE_0335299_454766_P_ENABLE_HIGH_RPM_ZAP_DEBUG                                  = 0 # for high RPM ZAP DEBUG
   #################################################################################
   ############################        ScPk END        #############################
   #################################################################################


testSwitch = CSwitches()
