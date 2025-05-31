// Do NOT modify or remove this copyright and confidentiality notice!
//
// Copyright (c) 2001 - $Date: 2016/12/07 $ Seagate Technology, LLC.
//
// The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
// Portions are also trade secret. Any use, duplication, derivation, distribution
// or disclosure of this code, for any reason, not expressly authorized is
// prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
//


/*******************************************************************************
*     SCSS link: http://sgpscssapp.sing.seagate.com/WebSCSS/index.do
*******************************************************************************/

#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description:
# $File: //depot/TSE/Shared/source/codes/proc_codes.h $
# $Revision: #254 $
# $DateTime: 2016/12/07 13:50:43 $
# $Author: ben.t.cordova $
# $Header: //depot/TSE/Shared/source/codes/proc_codes.h#254 $
# Level:3
#---------------------------------------------------------------------------------------------------------#
#define BAD_PARAM_FILE                  10090   /* Proc M.E.-Bad .prm Parameter File */
#define WT_RD_CAL_BAD_DELTA_OFFSET      10096   /* Wt/Rd Cal-Bad Delta Offset Margin */
#define COMMUNICATIONS_FAILURE          10149   /* Tester Comm Mgr-Communications Failure */
#define COEF_RAP_PROCESS_MISMATCH       10279   /* Drv Misc-Log Data Out of Spec */
#define NO_FW_FILE                      10326   /* Proc M.E.-Missing Drive F/W File(s) */
#define NO_SCN                          10345   /* Proc M.E.-No SCN File */
#define HOT_CHAMBER_TEMP                10605   /* Tester Pwr/Temp Ctrl-Chamber too hot */
#define COLD_CHAMBER_TEMP               10606   /* Tester Pwr/Temp Ctrl-Chamber too cold */
#define SCRIPT_EXCEPTION                11044   /* Process ME-Script Exception */
#define SCRIPT_EXCEPTION                11887   /* RHO All head is bad ! ! ! ! ! !*/
#define SCRIPT_EXCEPTION                11888   /* ALL Head is Bad ! ! ! ! ! !*/
#define SCRIPT_EXCEPTION                11889   /* Head 177 Bad ! ! ! ! ! !*/
#define SCRIPT_EXCEPTION                11890   /* PCB IS BAD ! ! ! ! ! !*/
#define SCRIPT_EXCEPTION                11891   /* SF3 CODE IS ERROR ! ! ! ! ! !*/
#define MISSING_PCBA_HSA_PART_NUMBER    11176   /* Tester Misc-Missing PCBA HSA Part Number */
#define CAP_FILE_MISSING_PCBA_PART_SN   11178   /* CAP file missing PCBA part/serial number */
#define VBAR_CAP_BELOW_REQUIRED         11179   /* Drv Misc-Capacity below requirement */
#define CONTACT_DETECT_INCONSISTENT     11180   /* Drv Head - Contact Detect Inconsistent */
#define WWN_NOT_VALID                   11181   /* Drv PCBA-CAP WWN Not Valid for Interface */
#define MIN_CLEARANCE_NOT_MET           11186   /* Drv Head - Min Clearance Not Met */
#define RIM_TYPE_VALID_OPER_MISMATCH    11187   /* Proc Oper-RIM_TYPE/Valid Oper Mismatch */
#define INCORRECT_FIJI_REV              11188   /* Proc M.E.-Incorrect Fiji Rev */
#define UNRECOGNIZED_PCBA_PART_NUMBER   11189   /* Proc M.E.-Unrecognized PCBA Part Number */
#define TABLE_ERROR                     11200   /* Drv F/W-Report_table_row() Error */
#define MISSING_REQUIRED_ATTRIBUTE      11201   /* Proc M.E.-Required Attribute is Missing */
#define MAX_CLEARANCE_EXCEEDED          11206   /* Drv Head-Max Clearance Exceeded*/
#define VPD_ATTR_INCORRECT              11249   /* Drv Misc - VPD Attribute is Incorrect */
#define CTRL0_NOT_XO                    11251   /* Drv Misc - Ctrl 0 is not XO */
#define LUN_CREATE_FAILED               11252   /* Drv Misc - LUN Creation Failed */
#define CAN_NOT_DETERMINE_X0_NXO        11253   /* Drv Misc - Unable to determine XO or NXO */
#define OD_ID_DELTA_EXCEEDED            11257   /* Write+Heat Mode OD/ID Delta Exceeded*/
#define WATERFALL_FAILED                12150   /* Proc Misc - Waterfall failed */
#define DEPOP_REZONE                    12168   /* Drv Misc - Auto-Waterfall Rezone */
#define DEPOP_RESTART                   12169   /* Drv Misc - Auto-Waterfall Depopped */
#define DIODE_CERT_TEMP_CHK_ERR         12179   /* Proc Functional - Diode cert temp check error */
#define KWAI_PREP_FAILED                12383   /* Proc Misc - Kwai Prep Failed */
#define VERIFY_WWN_FAIL                 12411   /* Proc Misc - Verify WWN fail */
#define VERIFY_ATA_SPEED_FAIL           12412   /* Proc Misc - Verify ATA SPEED fail */
#define SET_XFER_RATE_FAIL              12413   /* Proc Misc - Unable to set xfer rate */
#define CIT_NOT_BUFFER_COMPARE          12513   /* Proc Misc - CIT Not Buffer Compare */
#define TWO_TEMP_CERT_FAILURE           12517   /* Proc Final - Two Temp Cert Failure */
#define TWO_TEMP_CERT_DIODE_FAILURE     12518   /* Proc Misc-Two Temp Cert Diode Failure */
#define CIT_DEFAULT_FAIL                12525   /* Proc CIT - Default Miscompare failure code*/
#define RANDOM_DMA_READ                 12653   /* Random DMA read fail */
#define SEQ_DMA_READ                    12656   /* Sequential DMA read fail*/
#define SEQ_DMA_WRITE                   12657   /* Sequential DMA write fail */
#define RANDOM_DMA_WRITE                12664   /* Random DMA write fail */
#define FULL_READ_VERIFY                12674   /* Full read verify fail */
#define CSBM16                          12716   /* Cit SingleBitMis MIS1 */
#define CMBM17                          12717   /* Cit MultiBitMis MIS2 */
#define CMS318                          12718   /* Cit 50 IOEDC MIS3 */
#define CMS419                          12719   /* Cit Not 50 IOEDC MIS4 */
#define CIO120                          12720   /* Cit IO Not MIS I/O1 */
#define CIO221                          12721   /* Cit IO UNK MIS I/O2 */
#define ENCRYPT_BLK_CHK_FAILED          12753   /* Proc Misc - Encryption Blk Chk Fail */
#define GET_KWAI_SETTING_FAILED         12754   /* Proc Misc - Unable to get KwaiPrep settings */
#define NVC_FAIL                        13306   /* Proc Misc - NVC validation failed */
#define HI_LOW_SEEK                     13370   /* Hi-Low Seek fail */
#define FUNNEL_SEEK                     13371   /* Funnel Seek fail */
#define RANDOM_SEEK                     13372   /* Random Seek fail */
#define SONY_SCREEN_TEST                13373   /* Sony Screen Test fail */
#define TRK_2_TRK_SEEK                  13374   /* Track to Track Seek fail */
#define LINEAR_VERIFY                   13381   /* Linear Verify fail */
#define AGITATION_CLEANUP               13382   /* MQM - Agitation CleanUp fail */
#define SWOT_TEST                       13383   /* MQM - SWOT Test fail */
#define ENCRO_TEST                      13384   /* MQM - Encro Test fail */
#define RANDOM_WRITE                    13385   /* MQM - Random Write fail */
#define RANDOM_READ                     13386   /* MQM - Random Read fail */
#define ID_SCRN                         13387   /* Drive failed for UDE at ID screening */
#define DOWNLOAD_CPC_ERROR              13401   /* Proc Misc - CPC Interface FPGA Code Dnld Failed */
#define CPC_VERSION_ERROR               13402   /* Proc Misc - CPC Code Ver and Config Ver Mismatch */
#define DEPEDENCY_CHECK_ERROR           13403   /* dependency check error*/
#define VBAR_CAPABILITY_FAILED          13404   /* Proc VBAR - VBAR Capability Failed */
#define VBAR_PERFORMANCE_FAILED         13405   /* Proc VBAR - VBAR Performance Failed */
#define VBAR_CAPACITY_FAILED            13406   /* Proc VBAR - VBAR Capacity Failed */
#define VBAR_FAIL_HEAD_COUNT            13408   /* Proc VBAR - VBAR fail head count */
#define VBAR_HEAD_SATURATION_FAILED     13409   /* Proc VBAR - VBAR Head Saturation Failed */
#define WRITE_CRC_ERROR                 13410   /* 03 CRC error bit is set during a write command */
#define WRITE_IDNF_ERROR                13411   /* 04 Write address outside user-accessible address space */
#define WRITE_ABRT_ERROR                13412   /* 05 Write command aborted */
#define WRITE_UD_ERROR                  13413   /* 06 Undetermined write error */
#define READ_CRC_ERROR                  13414   /* 07 CRC error bit set during read command */
#define READ_UNC_ERROR                  13415   /* 08 Uncorrectable data during read */
#define READ_IDNF_ERROR                 13416   /* 09 Read address outside user-accessible address space */
#define READ_ABRT_ERROR                 13417   /* 10 Read command aborted */
#define READ_UD_ERROR                   13418   /* 12 Undetermined read error */
#define VERIFY_WWN_FAILED               13419   /* 11 Verification of WWN Failed*/
#define ID_DEVICE_ERROR                 13420   /* 13 generic CPC IdentifyDevice() error*/
#define SET_FEATURES_ERROR              13421   /* 14 Set Features failed */
#define RW_ERROR                        13422   /* 15 Generic Read Write Error */
#define GET_BUFFER_ERROR                13423   /* 16 Generic Get Buffer Error */
#define ATA_READY_ERROR                 13424   /* 17 Drive failed to power on and come ready in Interface*/
#define GOTF_NO_DEMAND                  13425   /* Drive failed current BG and cannot commit to any other BG */
#define DIAG_ERROR                      13426   /* SPT Diagnostic command failed */
#define ACCESS_TIME_ERROR               13450   /* 18 Access Time out of Spec Error */
#define COMMAND_SET_ERROR               13452   /* 19 Command Set test Error */
#define CAP_MODEL_ERROR                 13453   /* Capacity & Model No. Screen Fail? */
#define POWER_MODE_ERROR                13454   /* 20 Power Mode Idle/Standby/Sleep Error*/
#define SMART_VERIFY_THRESH             13455   /* Failed Smart Verify Thresholds*/
#define SMART_CRITICAL_EVENT            13456   /* Failed Smart Critical Event Log*/
#define SMART_DOS_RESET                 13457   /* Failed Smart DOS Reset*/
#define SMART_DST_SHORT_FAILED          13458   /* Failed Smart DST Short - Drive Self Test*/
#define SMART_DST_LONG_FAILED           13459   /* Failed Smart DST Long - Drive Self Test*/
#define DRAM_SCREEN_ERROR               13460   /* 21 DRam Screen, Miscompare screen*/
#define INVALID_CARRIER_ID              13501   /* Carrier ID's length is not 8*/
#define PORT_EXCEPTION                  13502   /* Unable to select port on carrier */
#define GENERIC_CPC_CMD_FAILURE         14001   /* Iface SATA - Undefined Error */
#define WEAK_WRITE_BER_DELTA_FAILED     14180   /* RAW_ERROR_DELTA out of spec */
#define P185_TRK_0_V3BAR_CALHD_FAILED   14183   /* CRASH_STOP_CYL out of spec */
#define FORMAT_ZONE_ERROR_RATE_FAILED   14184   /* RAW_ERROR_RATE out of spec */
#define P080_DUAL_HTR_RESISTANCE_FAILED 14185   /* HEATER_RESISTANCE out of spec */
#define P240_EAW_ERROR_RATE_FAILED      14186   /* DELTA_SER out of spec */
#define WEAK_WRITE_BER_DELTA_FAILED     14187   /* OTF_ERROR_RATE out of spec */
#define P051_ERASURE_BER_DELTAS_FAILED  14188   /* OTF_BER_DELTA out of spec */
#define UNABLE_TO_LOGIN                 14201   /* Drv Misc - Unable to login */
#define IP_OUT_OF_RANGE                 14202   /* Drv Misc - Ifconfig: IP out of range */
#define CAN_NOT_FIND_IP_BCAST           14203   /* Drv Misc - Ifconfig: IP/Bcast not found */
#define MAC_ADDR_NOT_FOUND              14204   /* Drv Misc - Ifconfig: MAC addr not found */
#define ETH0_ETH1_NOT_FOUND             14205   /* Drv Misc - Ifconfig: eth0/eth1 not found */
#define IFCONFIG_NOT_FOUND              14206   /* Drv Misc - Ifconfig data not found */
#define UNABLE_TO_STOP_AUTOBOOT         14211   /* Drv Misc - Unable to stop autoboot */
#define UNABLE_TO_TURN_OFF_BATT         14212   /* Drv Misc - Unable to turn off battery */
#define INVALID_LUN_PARAM               14513   /* Drv Misc - Invalid LUN Parameters */
#define SET_VPD_FAILED                  14514   /* Drv Misc - Set VPD Failed */
#define GET_VPD_FAILED                  14515   /* Drv Misc - Get VPD Failed */
#define INVALID_CONTROLLER              14516   /* Drv Misc - Invalid Controller Selected */
#define AVAIL_LUNS_EXCEEDED             14517   /* Drv Misc - Available LUNs Exceeded */
#define SAME_IP_FOR_XO_NXO              14518   /* Drv Misc - XO and NXO have the same IP */
#define UNABLE_TO_DETERMINE_MDA_TYPE    14522   /* Drv Misc - Unable to Determine MDA Type */
#define GENERAL_SIM_READ_FAILURE        14524   /* Drv F/W - General SIM Read Failure */
#define INVALID_DICTIONARY_KEY          14526   /* Proc M.E. - Invalid key in dictionary */
#define OBJECT_MISSING_ATTRIBUTE        14527   /* Proc M.E. - Object missing attribute */
#define INVALID_ISE_PART_NUMBER         14529   /* Drv Misc - Invalid ISE Part Number */
#define LOW_BATT_EXP_LIFE               14530   /* Drv Misc - Low Battery Expected Life */
#define MIXED_MDA_TYPE                  14531   /* Drv Misc - Mixed MDA Type */
#define REFORMAT_ISE_FAILURE            14542   /* Drv Misc - Reformat ISE Failure */
#define BPI_BELOW_SPEC                  14543   /* DRV MISC - BPI average below spec */
#define UNKNOWN_INITIATOR_CODE          14551   /* Proc M.E. - Unknown Initiator code */
#define INVALID_LIST_INDEX              14554   /* Proc M.E. - Invalid List Index */
#define UNDEFINED_GLOBAL_NAME           14555   /* Proc M.E. - Undefined Global Name */
#define FAILED_BURNISH_CHECK            14559   /* Proc M.E. - Failed Burnish Check */
#define BURNISH_INCONSISTENT            14570   /* Proc M.E. - Burnish inconsistent */
#define BURNISH_RETRY_FAILED            14571   /* Proc M.E. - Burnish Retry Failed */
#define DELTA_BER_OVER_LIMIT            14574   /* Proc M.E. - BER change, as measured by quickErrRate, exceeded limit */
#define INVALID_PREAMP_AAB_TYPE         14575   /* Proc Misc - Invalid Preamp and AAB Type */
#define BURNISH_CAP_EXCEEDED            14576   /* Proc M.E. - Burnish Check Cap Exceed Max */
#define GET_TD_SID_FAILED               14581   /* Proc Misc - Failed to retrieve TD_SID from FIS */
#define HEAT_ONLY_OD_ID_DELTA_EXCEEDED  14586   /* Heat Only Mode OD/ID Delta Exceeded */
#define DELTA_MR_RES_OVER_LIMIT         14599   /* Wt/Rd Misc - Delta MR Resistance over limit */
#define FAIL_TO_UNLOCK_SERIAL_PORT      14601   /* Proc Misc - Failed to unlock serial port */
#define POOR_AVE_QBER_PER_HD            14612   /* Poor Average QBER per head */
#define FW_CHECKSUM_MISMATCH            14615   /* Drv F/W - Download Checksum Mismatch */
#define SELF_TEST_FAILED_TO_EXECUTE     14629   /* Self-Test Failed to Execute */
#define FAILED_BER_FULL_ENCROACHMENT    14634   /* Failed BER full encroachment */
#define FAILED_BER_SIDE_ENCROACHMENT    14635   /* Failed BER side encroachment */
#define VBAR_GENERIC_FAILED             14644   /* Proc VBAR - VBAR Generic Failed */
#define LOW_OTF_DURING_FORMAT           14651   /* Failed for low OTF during format */
#define HIGH_WRTY_DURING_FORMAT         14652   /* Failed for excessive write retries during format */
#define VBAR_SQEEZE_FAILURE             14655   /* Final VBAR squeeze test failure */
#define VBAR_ABSOLUTE_SQZ_THRESH        14656   /* Absolute Squeeze SER Threshold Failure */
#define POOR_QBER_PER_ZONE              14658   /* Poor QBER per zone */
#define FAILED_QBER_SCREENING           14659   /* Failed QBER screening */
#define FAILED_DELTA_VGA_LIMIT          14662   /* Exceed delta VGA limit in read screen2*/
#define BER_PREDICTION_FAILED           14673   /* 1 million writes BER Prediction */
#define CLR_SCREEN_PFL1139_FAILURE      14680   /* Clearance Screen Failure PFL1139 */
#define ST35_SERVO_TWIDDLE_ERRORS       14682   /* ST35 return servo twiddle error */
#define ID_CLR_CONTAMINATION            14683   /* Drive failed for clearance contamination at the ID */
#define FAIL_MIN_BPI_TPI                14686   /* Drv Head - Insufficient Areal Density Capability */
#define HIRP_STDEV_EXCEEDED             14691   /* HIRP StDev Between Zones Exceeds Limit */
#define HIRP_ADJACENT_ZONES_FAILED      14692   /* HIRP Adjacent Zones Failed */
#define Brinks_62kHz_OD_Cntct_Mod_Scrn  14704   /* Brinks 62kHz OD Contact Mod Scrn Failure */
#define V3BAR_RETRIES_EXCEEDED          14706   /* V3BAR Number Retries Exceeded */
#define MDW_TPI_RETRIEVAL_FAILED        14709   /* Retrieval of MDW TPI from FIS and Gemini local DB Failed */
#define EXCEED_DELTA_DEFECT_COUNT_LIMIT 14714   /* Exceeded delta defect count limit */
#define FAIL_DUMP_SMART_PENDING_LIST    14718   /* Failed Smart Pending Defect List*/
#define FAIL_DUMP_SMART_GROWN_LIST      14719   /* Failed Smart Grown Defect List*/
#define TCS_SPEC_LIMIT_VIOLATED         14722   /* TCS Spec Limit Violated */
#define FAIL_TO_UNLOCK_INTERFACE_PORT   14725   /* Proc Misc - Failed to unlock interface port */
#define EXCEEDED_DICE_AUDIT_STDDEV      14726   /* Exceeded Dice Audit StdDevFitError limit */
#define CALCULATION_ERROR_FW_AND_PF3    14727   /* Calculation Error FW and PF3 */
#define DYNAMIC_RIM_TYPE_MISMATCH       14728   /* Dynamic Rim Type Mismatch with temp req  */
#define MISSING_DYNAMIC_RIM_TYPE        14729   /* RimType not in Dynamic Rim Type list */
#define POST_CMT2 GOTF FAILURE          14733   /* Cannot change BG on the fly. Reprocess drive at CMT2 */
#define FAILED_HEATER_DAC_SCREEN        14734   /* Proc M.E. - Failed for Heater DAC value screening */
#define WR_VERIFY_FAILED                14737   /* Proc Misc - Failed to verify the drive in WR_VERIFY */
#define C410SCREEN_FAILED               14746   /* Drv Misc - Failed to pass C410_Screen test */
#define INVALID_LBA                     14760   /* Misc - LBA not divisible by number of heads  */
#define SET_DRIVE_CONFIG_FAILED         14761   /* Drv Misc - Failed CSetDriveConfigAttributes */
#define THERMISTOR_VALUE_OUT_OF_RANGE   14798   /* Drive Thermistor value out of spec range */
#define RERUN_VBAR_MORE_THAN_ONCE       14799   /* Attempting to rerun VBAR more than once */
#define FAIL_GOTF_CTQ0                  14765   /* Failed Grading at CTQ0  */
#define FAIL_GOTF_CTQ1                  14766   /* Failed Grading at CTQ1  */
#define FAIL_GOTF_CTQ2                  14767   /* Failed Grading at CTQ2  */
#define FAIL_GOTF_CTQ3                  14768   /* Failed Grading at CTQ3  */
#define FAIL_GOTF_CTQ4                  14769   /* Failed Grading at CTQ4  */
#define FAIL_GOTF_CTQ5                  14770   /* Failed Grading at CTQ5  */
#define FAIL_GOTF_CTQ6                  14771   /* Failed Grading at CTQ6  */
#define FAIL_GOTF_CTQ7                  14772   /* Failed Grading at CTQ7  */
#define FAIL_GOTF_CTQ8                  14773   /* Failed Grading at CTQ8  */
#define FAIL_GOTF_CTQ9                  14774   /* Failed Grading at CTQ9  */
#define FAIL_GOTF_CTQ10                 14775   /* Failed Grading at CTQ10 */
#define FAIL_GOTF_CTQ11                 14776   /* Failed Grading at CTQ11 */
#define FAIL_GOTF_CTQ12                 14777   /* Failed Grading at CTQ12 */
#define FAIL_GOTF_CTQ13                 14778   /* Failed Grading at CTQ13 */
#define FAIL_GOTF_CTQ14                 14779   /* Failed Grading at CTQ14 */
#define FAIL_GOTF_CTQ15                 14780   /* Failed Grading at CTQ15 */
#define FAIL_GOTF_CTQ16                 14781   /* Failed Grading at CTQ16 */
#define FAIL_GOTF_CTQ17                 14782   /* Failed Grading at CTQ17 */
#define FAIL_GOTF_CTQ18                 14783   /* Failed Grading at CTQ18 */
#define FAIL_GOTF_CTQ19                 14784   /* Failed Grading at CTQ19 */
#define FAIL_GOTF_CTQ20                 14785   /* Failed Grading at CTQ20 */
#define FAIL_GOTF_CTQ21                 14786   /* Failed Grading at CTQ21 */
#define FAIL_GOTF_CTQ22                 14787   /* Failed Grading at CTQ22 */
#define FAIL_GOTF_CTQ23                 14788   /* Failed Grading at CTQ23 */
#define FAIL_GOTF_CTQ24                 14789   /* Failed Grading at CTQ24 */
#define FAIL_GOTF_CTQ25                 14790   /* Failed Grading at CTQ25 */
#define FAIL_GOTF_CTQ26                 14791   /* Failed Grading at CTQ26 */
#define FAIL_GOTF_CTQ27                 14792   /* Failed Grading at CTQ27 */
#define FAIL_GOTF_CTQ28                 14793   /* Failed Grading at CTQ28 */
#define FAIL_GOTF_CTQ29                 14794   /* Failed Grading at CTQ29 */
#define FAIL_GOTF_CTQ30                 14795   /* Failed Grading at CTQ30 */
#define FAIL_GOTF_CTQ31                 14796   /* Failed Grading at CTQ31 */
#define CONS_CHECK_RETRIES_EXCEEDED     14800   /* Consistency Check Exceeded Retries And Failed  */
#define RECONFIG_RPM_CHECK              14801   /* Proc Misc - Fail Drive Reconfig RPM check */
#define FDE_RECONFIGURE_FAILED          14802   /* Proc Misc - Failed to reconfigure FDE drive to STD drive.  */
#define VBAR_SQEEZE_SER_FAILURE         14803   /* FAILVBAR does not meet squeeze SER limit */
#define FAIL_TI_ATE_TEST                14804   /* Failed TI ATE Screen */
#define FAIL_WEAK_WRITE_SCRN_H0         14805   /* Weak Write Scrn - defect found on H0 */
#define FAIL_WEAK_WRITE_SCRN_H1         14806   /* Weak Write Scrn - defect found on H1 */
#define FAIL_WEAK_WRITE_SCRN_H2         14807   /* Weak Write Scrn - defect found on H2 */
#define FAIL_WEAK_WRITE_SCRN_H3         14808   /* Weak Write Scrn - defect found on H3 */
#define FAIL_ENCR_SCRN_H0               14809   /* Encroachment Scrn - defect found on H0 */
#define FAIL_ENCR_SCRN_H1               14810   /* Encroachment Scrn - defect found on H1 */
#define FAIL_ENCR_SCRN_H2               14811   /* Encroachment Scrn - defect found on H2 */
#define FAIL_ENCR_SCRN_H3               14812   /* Encroachment Scrn - defect found on H3 */
#define DELAY_WRITE                     14813   /* Delay write fail */
#define UNSUPPORTED_REQUEST_FROM_DRIVE  14823   /* Unsupported Request from drive */
#define UNRECOGNIZED_TEST_NUM           14824   /* Unrecognized test number */
#define VBAR_HEATER_CAP_FAIL            14826   /* Heater Cap - Bad Single Sector Error */
#define BLOCK_AUDIT_TEST_PASSING_DRIVE  14827   /* Prevent passing audit test drive from shipping */
#define CET_ASUS_IDLE_1_FAILED          14828   /* Asus Idle 1 Test Failed */
#define CET_ASUS_S4_FAILED              14829   /* Asus S4 Test Failed */
#define CET_VAR_IDLE_MODE_FAILED        14830   /* Various Idle Mode Test Failed */
#define CET_COPY_STATION_FAILED         14831   /* Copy Station Test Failed */
#define CET_SIE_FITS_FIT_FAILED         14832   /* SIE FITS Fitness Test Failed */
#define CET_SIE_FITS_WRC_FAILED         14833   /* SIE FITS Write Read Compare Test Failed */
#define CET_MAYHEM_FILE_COPY_CMP_FAILED 14834   /* Mayhem File Copy Compare Simulation Test Failed */
#define CET_FITNESS_CACHE_SIM_FAILED    14835   /* Fitness Cache Simulation Test Failed */
#define FAIL_COMBO_SPEC_SCRN            14836   /* Combo Spec Scrn - WPP and BER */
#define RECONF_BG_IS_NOT_ALLOWED        14837   /* Reconfig Business Group is not allowed */
#define TST_135_CNTCT_DAC_LESS_STRT_DAC 14839   /* Test 135 Contact DAC less Start DAC */
#define CET_FOUR_STREAM_FAILED          14840   /* Four Stream Test Failed */
#define MEDIA_CACHE_CONTROL             14842   /* Media Cache Control */
#define CET_FJS_HDD_DIAG_FAILED         14843   /* Fujitsu HDD Diagnostic Test Failed */
#define FIRMWARE_TPM_FAILING_SENSE      14844   /* TPM Returned a failing sense code in download. Check log for sense code and description.*/
#define UDR2_SETTING                    14845   /* Fail to change drive UDR2 Unwritten Drive Recovery */
#define CET_APPLE_LTOS_FAILED           14849   /* Apple LTOS Test Failed */
#define CET_DELAY_RANDOM_READ_FAILED    14850   /* Delay Random Read Test Failed */
#define CET_HP_WRC_FAILED               14851   /* HP WRC Test Failed */
#define CET_HP_INTG_SIM_FAILED          14852   /* HP Integration Simulation Test Failed */
#define CET_APPLE_STONE_CUTTER_FAILED   14853   /* Apple Stone Cutter Test Failed */
#define VBAR_ABSOLUTE_SQZ_THRESH        14856   /* Absolute Squeeze SER Threshold Failure */
#define CET_NEC_PERFORMANCE_FAILED      14857   /* NEC Performance Test Failed */
#define FDE_NOT_IN_USE_OR_MFG_MODE      14858   /* FDE drive not in USE or MFG Mode */
#define UNSUPPORTED_CUSTOMER            14859   /* Unsupported customer */
#define UNSUPPORTED_CUSTOMER_DLFILE     14860   /* Unsupported customer config dlfile */
#define STE_SCREEN_FAILED               14861   /* Test 621 STE Screen Failed  */
#define MIN_RAMP_CYL_DETECTED           14872   /* min ramp cyl for all heads detected */
#define TRK0_CYL_HD_DELTA_EXCEEDED      14873   /* Ramp cyl odd/even head delta exceeded */
#define TCG_PERSONALIZATION_FAILED      14862   /* Proc Misc - TCG Prep Error */
#define PN_VS_SECTOR_SIZE_ERROR         14863   /* Proc Misc - Wrong PN vs Drv Sector Size */
#define WIJIA_HD_STABILITY_FAILED       14876   /* WIJIA - Head Stability Screen Fail? */
#define TEST_198_SKIP_WRITE_DETECT      14877   /* Test 198 Skip Write Detect */
#define RIM_TYPE_REPLUG_COUNT_EXCEEDED  14881   /* Dynamic Rim Type replug count exceeded */
#define PRIM_CAP_MISMATCH_SEC_CAP       14882   /* Primary CAP does not match Secondary CAP */
#define PRIM_RAP_MISMATCH_SEC_RAP       14883   /* Primary RAP does not match Secondary RAP */
#define PRIM_SAP_MISMATCH_SEC_SAP       14884   /* Primary SAP does not match Secondary SAP */
#define CCV_ME_PROCESS_SETUP_ERROR      14886   /* CCV - ME CCV Process Setup Error */
#define SUPER_CERTIFY_IN_PROGRESS       14888   /* Svo Startup-02/04F0 Not Ready Super Certify in Progr */
#define INVALID_PARAM_CHK_MODE_PG       14889   /* Proc M.E.-05/26/00/04 Invalid Param-CheckModePage */
#define INVALID_BUILD_TRANS_ADDR_PG     14890   /* Proc M.E.-05/26/00/0B Invalid-BuildTranslateAddrPg */
#define INVALID_INPUT_HEAD              14891   /* Proc M.E.-05/26/00/81 Invalid-Input Head */
#define INVALID_DIAG_CMD                14892   /* Proc M.E.-05/26/02/10 DIAG-Invalid command */
#define UNSUPPORTED_DIAG_CMD            14893   /* Proc M.E.-05/26/02/13 DIAG-Unsupported DIAG Cmd */
#define SED_DNLD_INVALID_PARAM          14894   /* Proc M.E.-05/26/9A/00 SED DNLD-Invalid Param */
#define POWER_ON_RESET                  14895   /* Drv Startup-06/29/01/xx Pwr On Reset */
#define MODE_PARAMS_CHANGED             14896   /* Drv F/W-06/2A/01/xx Mode Params Changed */
#define SED_LOCKED_LBA                  14897   /* Drv F/W-07/20/02/00 Access Denied SED Locked LBA */
#define WRITE_PROTECT                   14898   /* Drv F/W-07/27/00/xx Wt Protect */
#define CORRUPT_WWN_IN_DIF              14899   /* Proc M.E.-03/31/91/xx Corrupt WWN in DIF */
#define NO_SPARES_AVAILABLE             14900   /* Wt/Rd Def's-04/32/00/xx No Spares Available */
#define DEFECT_LIST_NOT_FOUND           14901   /* Drv CPF-04/1C/00/xx Defect List Not Found */
#define DATA_MISCOMPARE_DURING_VERIF    14902   /* Drv F/W-0E/1D/00/xx Data Miscompare During Verify */
#define ETF_CAP_WWN_MISMATCH            14903   /* Proc M.E.-06/3F/91/xx ETF CAP WWN Mismatch */
#define DATA_CRC_MISMATCH               14910   /* RimProxy - Data CRC Mismatch */
#define GOT_WRONG_TRAY                  14911   /* RimProxy - Got Wrong Tray */
#define EP2OUT_NOT_EMPTY                14912   /* RimProxy - EP2OUT not EMPTY */
#define XYRC_NO_RESPONSE_FROM_CELL      14913   /* RimProxy - xyrc No Response From Cell */
#define XYRC_DRIVER_ERROR               14914   /* RimProxy - xyrc Driver Error */
#define CET_HP_STORE_STINT_FAILED       14915   /* HP Store Self Test Interrupt Failed */
#define ADJ_ZONE_XFER_RATE_EXCEEDED     14917   /* Adjacent zone xfer rate delta exceeded */
#define CET_APPLE_WRC_FAILED            14919   /* Apple Write Read Compare Test Failed */
#define CET_ACER_S3_FAILED              14920   /* Acer S3 Test Failed */
#define CET_ACER_S4_FAILED              14921   /* Acer S4 Test Failed */
#define CET_ACER_S5_FAILED              14922   /* Acer S5 Test Failed */
#define CET_WRRDSMT_FAILED              14926   /* Write/Read SMART (WrRdSmt) Test Failed */
#define CH_OPTI_BER_EXCEEDED            14930   /* Drv Head - Channel Opti BER Limit Exceeded */
#define CET_HP_DST_PFM_FAILED           14931   /* HP DST Performance Test Failed */
#define GOTF_THERMAL_CLR_COEF1_OOS      14933   /* GOTF Thermal Clearance Coefficient 1 Out Of Spec  */
#define GOTF_MEAN3SIG_RRO_OOS           14934   /* GOTF Mean 3 Sigma RRO Out Of Spec  */
#define WRITE_READ IOPS_COMP_PERFOMANCE 14954   /* Write Read IOPS Comp Performance   */
#define RIMTYPE_TO_RISERTYPE_MISMATCH   14956   /* Rim type to riser type mismatch  */
#define T199_HD_STABILITY_FAILED        14957   /* Drv Head-Stability Test Failed */
#define DELTA LOAD_PEAK_CUR OVER LIMIT  49033   /* Delta LOAD_PEAK_CUR from T25 over limit*/
#define BURNISH_CHK_INSUFFICIENT_DATA   42187   /* Burnish Chk Insufficient Data */
#define CAL_CLK_FAILED                  48902   /* Cal Clk Failed */

//F3 sense translation EC's

#define IR_CFW_BRIDGE_FAIL_SRC          39197   /* 05/2699, FRU 1D - Invalid Unlock tags in Flash Download Source Customer does not match installed firmware */
#define IR_CFW_BRIDGE_FAIL_DEST         39198   /* 05/2699, FRU 1D - Invalid Unlock tags in Flash Download Destination Customer not allowed */
#define IR_CFW_BRIDGE_FAIL_SUM          39199   /* 05/2699, FRU 1D - Invalid Unlock tags in Flash Download Checksum failed */
#define IR_CFW_BLOCKPOINT_FAIL          39200   /* 05/2699, FRU 20 - Trying to download older firmware over newer firmware */
#define IR_OVERLAY_CFW_INCOMPATIBLE     39201   /* 05/2699, FRU 21 - Downloaded overlay is incompatible with curent CFW */
#define IR_OVERLAY_FAIL1                39202   /* 05/2699, FRU 22 - Overlay download failure 1 */
#define IR_OVERLAY_FAIL2                39203   /* 05/2699, FRU 23 - Overlay download failure 2 */
#define IR_DL_HANDLING_UNSUPPORTED      39204   /* 05/2699, FRU 24 - Download does not support this feature or handling */
#define IR_DL_GENERAL_FAILURE           39205   /* 05/2699, FRU 25 - General download failure */
#define IR_CFW_BRIDGE_PRODUCT_MISMATCH  39206   /* 05/2699, FRU 26 - Trying to download bridge file for the incorrect product family */
#define IR_BAD_FWTAG_FACTORY_FLAGS      39207   /* 05/2699, FRU 27 - Factory Flags mismatch - *** CheckFWTags( ) *** */
#define IR_MISSING_BOOTFW               39208   /* 05/2699, FRU 28 - Illegal combination, Missing BootFW module. */
#define IR_MISSING_CUSTFWFEATURE_FLAGS  39209   /* 05/2699, FRU 29 - Illegal combination, Missing Customer FW Feature Flags module. */
#define IR_ILLEGAL_CPIM_DOWNLOAD_ONLY   39210   /* 05/2699, FRU 2A - Illegal combination, Programmable Inquiry download only not supported. */
#define IR_MISSING_CUSTFW               39211   /* 05/2699, FRU 2B - Illegal combination, Missing CustomerFW module. */
#define IR_CONGEN_HEADER_FAIL           39212   /* 05/2699, FRU 2C - Download Congen header failure. */
#define IR_CONGEN_XML_FAIL              39214   /* 05/2699, FRU 2E - Download Congen XML failure. */
#define IR_CONGEN_FORMAT_INVALID        39215   /* 05/2699, FRU 2F - Download Congen version failure. */
#define IR_CONGEN_XML_SIM_MAKELOCAL_FAIL           39216   /* 05/2699, FRU 30 - Download Congen XML SIM MakeLocalFile failure. */
#define IR_CONGEN_MODE_DATA_HDR_FAIL               39217   /* 05/2699, FRU 31 - Download Congen mode data failure - could not save mode header. */
#define IR_CONGEN_MODE_DATA_LENGTH_MISCOMPARE_FAIL 39218   /* 05/2699, FRU 32 - Download Congen mode data failure - mode page had sent length/spec length miscompare. */
#define IR_CONGEN_MODE_DATA_PAGE_CHK_FAIL          39219   /* 05/2699, FRU 33 - Download Congen mode data failure - mode page had invalid contents. */
#define IR_CONGEN_MODE_DATA_CHANGE_MASK_FAIL       39220   /* 05/2699, FRU 34 - Download Congen mode data failure - mode page tried to change contents not allowed by change mask. */
#define IR_CONGEN_MODE_DATA_SAVE_ALL_FAIL          39221   /* 05/2699, FRU 35 - Download Congen mode data failure - save all mode pages could not write to media. */
#define IR_CONGEN_MODE_DATA_SAVE_PARTIAL_FAIL      39222   /* 05/2699, FRU 36 - Download Congen mode data failure - save partial mode pages could not write to media. */
#define IR_CONGEN_MODE_DATA_CHANGE_COMPLETE_FAIL   39223   /* 05/2699, FRU 37 - Download Congen mode data failure - mode change callbacks did not complete successfully. */
#define IR_PKG_ENFORCEMENT_FAILED       39224   /* 05/2699, FRU 38 - Package Enforcement Failure - Package didn't contain valid SFW component */
#define IR_INVALID_LINK_RATE            39225   /* 05/2699, FRU 39 - Invalid link rate in SaveProgrammablePhyMinMaxLinkRateToFlash */
#define IR_ILLEGAL_CROSSBRAND_DNLD_ATTEMPTED       39232   /* 05/2699, FRU 40 - Illegal Cross Brand Download Attempted */
#define IR_INV_DNLD_HDR_LEN             39248   /* 05/2699, FRU 50 - Download header length invalid - *** DownloadFirmware( ) *** */
#define IR_INV_DNLD_BUF_WRD_LEN         39249   /* 05/2699, FRU 51 - Download length is not a multiple of the buffer word size - *** DownloadFirmware( ) *** */
#define IR_INV_DNLD_LEN_SEG_LEN_MISMATCH           39250   /* 05/2699, FRU 52 - Download length and segment length mismatch - *** DownloadFirmware( ) *** */
#define IR_CHKFWTAG_FAIL                39329   /* 05/2699, FRU A1 - Unknow fw tag type in checkfwtag routine. */


#define ASD_PERFORMANCE_SCRN_TIME_OOS   42163   /* ASD Performance Screen Time Out Of Spec */
#define DELTA_OTF_EXCEEDS_LIMIT         42170   /* Delta OTF Exceeds Limit */
#define SED_NUKE_FAILED                 42182   /* Drv F/W - SED Nuke Failed */
#define MIN_BIAS_VOLT_NOT_MET           42183   /* Drv Head - Min Bias Voltage Not Met */
#define EAW_BER_DELTA_LIMIT_EXCEEDED    42198   /* Drv Misc - T234 / T240 EAW Test - BER / SER Exceeded defined limit */
#define CLEAR_MEDIA_CACHE_TIMED_OUT     42216   /* Clear Media Cache Timed-out */
#define CCV_UNDEFINED_FOR_TAB           42220   /* CCV definition for tab is not defined */
#define ERASE_AFTER_WRITE_DEGRADATION   42221   /* Erase After Write degradation failure by EAW_BER_CHUNK1 */
#define DFS_SER_OOS                     42231   /* Digital Flawscan SER Out Of Spec */
#define BPI_TPI_FILTER_PTS              48384   /* Rd/Wt-Not Enough Pts for BPI/TPI Filter */
#define HEAD_BURNISH_TA_EXCEEDED        48401   /* Too Many TA's with Head Burnish */
#define BURNISH_TA_AMP_COUNT_FAILED     48403   /* Burnish TA Sum Amp Count Failed */
#define P_SETTLING_SUMMARY_FAILED       48407   /* P Settling Summary Failed */
#define HSA_BP_DELTA_OTF_FAILED         48408   /* HSA BP Delta OTF Table Delta OTF Fail */
#define EAW_ERROR_RATE_FAILED           48409   /* EAW Error Rate Fail */
#define SERIAL_FLASH_FAILED             48427   /* Serial flash programming failed */
#define DRIVE_SEAL_FAILURE              48429   /* Drive Seal Failed */
#define ERROR_RATE_ZONE_ITERATION_FAIL  48431   /* Error Rate By Zone-Average Iteration Fail*/
#define RESET_RIM_TYPE_REPLUG_DRIVE     48436   /* Reset rim type and replug drive */
#define GAIN_SUM_CORR_GAIN_DELTA_FAILED 48446   /* P150 Gain Sum Delta Table Fail*/
#define TCC1_OVERPOWER                  48448   /* Drv Head - TCC1 OVERPOWER */
#define EAW_COMBO_SPEC_FAILURE          48454   /* Proc M.E. - EAW Combo Spec Failure */
#define INSTABILITY_METRIC_FAILED       48455   /* P315 Instability Metric Native And BTC */
#define UNVFYD_ERR_CNT_BY_HEAD_OOS      48457   /* Unverified Error Count By Head Out of Spec */
#define P134_TA_DETCR_DETAIL_SUM_HD2_COMBO  48458  /* Combo of MAX_AMP_WIDTH & AMP7_CNT out of Spec */
#define DFS_RRAW_BER_OOS                48460  /* DFS RRAW BER Out Of Spec */
#define ENCROACH_OTF_BER_OOS            48467  /*Encroach OTF BER out of spec*/
#define FBP_TABLE_OOS                   48468  /*FBP out of spec*/
#define VFYD_ERR_CNT_BY_HEAD_OOS        48469  /*Verified Error Limit Exceeded*/
#define SCRATCHFILL_TTL_BYTES_EXCEEDED  48470  /*Scratch Fill Total Bytes Exceeded*/
#define GOTF_MAX3SIG_RRO_OOS            48471  /*GOTF Max 3 Sigma RRO out of spec*/
#define ENCROACH_BIE_BER_OOS            48481  /*Encroach BIE BER out of spec*/
#define BIAS_VOLT_MES_OOS               48483  /*Bias Voltage Measurement Not Within Spec */
#define DFS_DATA_OOS_1                  48484  /*DFS Data Out Of Spec #1  */
#define OTF_BER_VARIANCE_OOS            48485   /*Test 50 BER variance OOS*/
#define DFS_DATA_OOS_2                  48488  /*DFS Data Out Of Spec #2  */
#define HMS_CAP_OOS                     48536  /*HMS Capability Out Of Spec*/
#define CSC_DELTA_BER_OOS               48537  /*CSC DELTA BER Out Of Spec*/
#define T25_LOAD_TIME_VIOLATION         48538 /*T25 Load Time Violation*/
#define T25_UNLOAD_TIME_VIOLATION       48539 /*T25 Unload Time Violation*/
#define T25_ERROR_COUNT_VIOLATION       48540 /*T25 Error Count Violation*/
#define T97_LOAD_TIME_VIOLATION         48541 /*T97 Load Time Violation*/
#define T97_UNLOAD_TIME_VIOLATION       48542 /*T97 Unload Time Violation*/
#define T250_T255_HEAD_ZONE_VIOLATION   48546 /*Does not meet IBM Opti Screen criteria*/
#define MOA_NLD_SCREEN_VIOLATION        48561 /*Moa NLD Screen Failed - Viterbi Channel Register Lockup*/
#define P56_DELTA_UACT_GAIN_MEAN_EXCEEDED  48564  /*PZT Degrade*/
#define P051_HARD_ERR_CNT_OOS           48585 /*P051 HARD_ERR_CNT Out of Spec*/
#define ATI_BIE                         48574 /*ATI BIE*/
#define pSTE_BIE                        48575 /*pSTE BIE*/
#define dSTE_BIE                        48576 /*dSTE BIE*/
#define ATI_STE_OTF_BIE_COMBO           48577 /*ATI STE OTF BIE COMBO*/
#define pSTE_HARD_ERROR                 48578 /*pSTE Hard Error*/
#define dSTE_HARD_ERROR                 48579 /*dSTE Hard Error*/
#define dSTE_BIE_HIGH_WRITES            48580 /*dSTE Hard Error High Writes*/
#define dSTE_HARD_ERROR_HIGH_WRITES     48581 /*dSTE Hard Error High Writes*/
#define STE_GREATER_THAN_ATI            48582 /*STE Greater Than ATI*/
#define pSTE_OTF_HIGH_WRITES            48583 /*pSTE OTF High Writes*/
#define dSTE_OTF_HIGH_WRITES            48584 /*dSTE OTF High Writes*/
#define T136_SMOOTHED_BIAS_VAL_EXCEEDED 48589 /*T136 Smoothed Bias Value Limit Exceeded*/
#define BG_DO_NOT_MEET_CRITERIA         48590 /*BG Check Drive don't Meet Criteria*/
#define ATI_OD_OOS                      48599 /*ATI OD out of spec*/
#define NRRO_OOS                        48600 /*Svo PES-NRRO Out of Spec*/
#define P117_SCRATCH_LENGTH_OOS         48606 /*P117 SCRATCH_LENGTH Out of Spec*/
#define SURFACE_PASSIVE_SEVERITY_TA_WIDTH_OOS 48617 /* Per Surface High TA Width Tracks Limit Exceeded*/
#define T50_ENCR_HD_ERR_LIM_EXCEEDED    48618 /*T50 Encroach Hard ERR CNT Exceeded*/
#define DRV_PASSIVE_TA_LIM_OOS          48619 /* Drive Passive TA Count Limit Exceeded */
#define SURFACE_TA_PASSIVE_LIM_OOS      48620 /* Per Surface TA Passive Count Exceeded */
#define TA_SEVERITY_LV_5_CNT_OOS        48621 /* TA Severity Level 5 Count Exceeded*/
#define TA_SEVERITY_LV_6_CNT_OOS        48622 /* TA Severity Level 6 Count Exceeded*/
#define TA_SEVERITY_LV_7_CNT_OOS        48623 /* TA Severity Level 7 Count Exceeded*/
#define SERVO_SCTR_ERR_CNT_OOS          48624 /* Servo Sector Error Count Exceeded*/
#define T186_DETCR_RESISTANCE_OOS       48629 /*T186 DETCR Resistance Out of Spec*/
#define AFH_RSA_DAMAGED                 48636 /* AFH-RSA Damaged */
#define AFH_LARGE_ID_OD_DELTA           48637 /* AFH-Large ID-OD Delta */
#define NAND_SCREEN                     48643 /* NAND_SCREEN failure out of spec */
#define HD_INST_BIE_Z_SCORE_EXCEEDED    48646 /* Head Instability BIE Z-Score Exceeded*/
#define HD_INST_BIE_SIGMA_EXCEEDED      48652 /* Head Instability BIE Sigma Exceeded*/
#define HD_INST_BIE_FULL_SIGMA_EXCEEDED 48876 /* Head Instability BIE Full Sigma Exceeded*/
#define DFS_MEAN_SSER_BY_HD_OOS         48657 /* DFS Mean SSER by head out of spec*/
#define MRA_SCRN_FAIL                   48660 /* MRA Srcn fail by NLFR_DELTA out of spec*/
#define P315_BIE_SLOPE_COMBO_FAIL       48662 /* P315 BIE slope combo spec failure */
#define P041_MAX_PCT_DIFF_EXCEEDED      48663 /* P041 Max Percent Diff Exceeded */
#define SEV7_TA_TRK_WDTH_SUM_PER_HD_OOS 48667 /* Sev7 TA track widths sum/head OOS */
#define DFS_MEAN_HARD_BER_OOS           48668 /* DFS Mean Hard BER out of spec */
#define ATI_BER_OOS                     48673 /* ATI BER out of spec */
#define BER_DEGRADED_OOS                48675 /* P240 BER Degraded out of spec */
#define T213_MAX_MAX_STE_OOS            48676 /* P213 Max STE By Head Screen out of spec*/
#define ATI_STE_HARD_ERROR              48677 /* ATI/STE Hard Error */
#define P315_INSTABILITY_OOS            48684 /* P315 Instability metric out of spec */
#define P250_DELTA_RAW_ERR_RATE_OOS     48685 /* P250 Delta Raw Err Rate out of spec */
#define P297_FULL_MEAN_OOS              48697 /* P297 Full mean out of spec */
#define P2109_RBIT_MINUS_SER_OOS        48698 /* P2109 RBit minus SER out of spec */
#define T285_TRK_0_CYL_OOS              48715 /* T285 Track 0 Cylinder out of Spec*/
#define P598_ZONE_XFER_CALC_RATE_OOS    48716 /* P598 Zone Xfer Rate - Calc Rate out of spec*/
#define TRACK_CLEANUP_FAILED_WRITE      48729 /* Failed Track Cleanup Diagnostic writes */
#define FAILED_FROM_WUS_SCREENING       48856 /* Drive failed from WUS screening */
#define DFS_MIN_RBIT_MIN_SSER_OOS       48870 /* DFS Min RBIT Min SSER Combo out of spec */

//Armada KV Fail Codes
#define KINETIC_FILE_DOWNLOAD_FAILED    48717 /* KINETIC File Download Failed*/
#define KINETIC_FILE_INSTALL_FAILED     48718 /* KINETIC File Install Failed*/
#define KINETIC_FAILED_TO_SET_ENV_VAR   48719 /* KINETIC failed to set environment variable*/
#define KINETIC_FAILED_KEY_CERT_VERIF   48887 /*KINETIC failed to verify SSL cert or key*/
//end Armada KV Fail Codes
#define SEQ_PERFORMANCE_ZONE_RATIO_OOS  48721 /* Sequential read/write performance - zone ratio out of spec */
#define ATI_ID_OOS                      48730 /* ATI ID out of spec */
#define HD_INST_BIE_SIGMA_LOSS_OOS      48731 /* Head Instability BIE Sigma Loss Out of spec */
#define CCV_TEST                        48735 /* Customer Confg requirement check failure */
#define FAILED_NEG_BURNISH_CHECK        48850 /* Failed Negative Burnish Check spec */
#define FAILED_NEG_BURNISH_RESTART      48851 /* Failed Negative Burnish restart spec*/
#define FAILED_POS_BURNISH_CHECK        48852 /* Failed Positive Burnish Check spec */
#define FAILED_POS_BURNISH_RESTART      48853 /* Failed Positive Burnish restart spec*/
#define P297_FULL_MEAN_ZSCORE_OOS       48863 /* Combo P297 Full_Mean and Zscore OOS */
#define COMBO_P2109_AND_P315            48880 /* Combo P2109 and P315 */
#define P297_GLITCH_LOSS_OSS            48882 /* Combo P297 Glitch Loss OOS */
#define DFS_SRVO_FLW_CNT_OOS            48886 /* DFS P126 Refined Servo Flaw Count OOS */
#define GOTF_LIMIT_GLITH_LOSS           48889 /* GOTF Out of limti GLITH_LOSS P297 */
#define P297_NUM_MODES_MODE_LOSS_OOS    48891 /* GOTF Out of Spec NUM_MODES and MODE_LOSS Head Instability P297 */
#define ADG_AFH_PRE2_RESTART_SPEC_MET   48896 /* ADG AFH PRE2 Restart Spec Met*/
#define P297_FULL_MEAN_ZSCORE           48897 /* P297 Full mean ZScore GOTF fail */
#define P297_SIGMA_LOSS_MODE_LOSS       48898 /* P297 Sigma loss Mode loss GOTF fail */
#define P297_ZSCORE_MODE_LOSS           48899 /* P297 ZScore mode loss GOTF fail */
#define P297_FULL_COV_OOS               48900 /* P297 Full COV GOTF fail */
#define P339_DETCR_TEMP_RISE            48912 /* T339 Hot DETCR Temp Rise High  */
#define P221_HEAT_POWER_NOM             48913 /* T221 Heat Power Nom High  */
#define P2109_TRIPLE_COMBO_OSS          48877 /* P2109 triple combo, Rbit, Sser, Hard_Ber */
#define P297_SIGMA_LOSS_RATIO_OOS       48890 /* P297 Z_Score and sigma loss/ratio OOS  */
#define SPFS_HIGH_UNSAFE_CNTS           48857 /* SPFS High Unsafe Error Count  */
#define DELTA_HMS_CAP_OOS               48696 /* Delta HMS Cap out of spec  */
#define P299_DOS_PICK_OOS               48943 /* P299 DOS Pick OOS  */
#define RRO_DELTA_OOS                   48947 /* RRO Delta OOS */
#define P299_DOS_DELTAS_OOS             48950 /* P299 DOS Deltas OOS */
#define DRAM_SIZE_CHECK_FAILED          48956 /* DRAM Size Check Failed */
#define P297_MODE_LOSS_AND_FULL_COV_OOS 48973 /* P297 MODE_LOSS and FULL_COV OOS */
#define Proc_HDI_Occurred               48974 /* Proc HDI Occurred */
#define P037_STDV_W_R_GOTF_FAIL         48975 /* T037 out of spec max stdv read and write */
#define FAILED_PAWL_LATCH_TEST          48989 /* Drv Pawl Latch Test Failed */
#define P250_DATA_ERR_CNT_OOS           48990 /* P250_ERROR_RATE_BY_ZONE DATA ERR CNT OOS */
#define SSD_DOWNLOAD_FAILED             48962 /* SSD Firmware Download Failed */
#define SSD_BAD_NAND_ID                 48963 /* SSD Bad NAND IDs Detected */
#define SSD_SEND_BUFFER_FAIL            48965 /* SSD Serial Diagnostic SendBuffer Command Failed */
#define SSD_RECEIVE_BUFFER_FAIL         48966 /* SSD Serial Diagnostic ReceiveBuffer Command Failed */
#define RFWD_EC_CSEFW_DETECTED_SIGNATURE_MISMATCH      48970 /* RFWD Deteted Signature Mismatch */
#define RFWD_EC_CSEFW_DETECTED_SIGNATURE_EXTR_FAILURE  48971 /* RFWD Deteted Signature Extraction Failure */
#define RFWD_EC_DETECTED_SIG_VS_TRUSTED_SIG_MISMATCH   48972 /* RFWD Deteted Signature vs Trusted Mismatch */
#define RFWD_EC_RWFD_ESLIP_ERROR                       48993 /* RFWD ESLIP Comm Error */
#define RFWD_EC_RFWD_CHECKSUM                          48997 /* RFWD Checksum Error */
#define RFWD_EC_PICKLE_FILE_UNAVALIABLE                48998 /* RFWD Pickle File Unavailable */
#define RFWD_EC_PICKLE_FILE_EXP_REC_MISMATCH           48999 /* RFWD Pickle File Exptected Record Mismatch */
#define RFWD_EC_TOO_FEW_SEGMENTS                       49000 /* RFWD Too Few Segments */
#define RFWD_EC_RFWD_TEST_TIMEOUT                      49001 /* RFWD Test Timeout*/
#define RFWD_EC_CORRUPTED_OVLY_SYS_FILE                49002 /* RFWD Corrupted Overlay System File */
#define RFWD_EC_TOO_MANY_SEGMENTS                      49003 /* RFWD Too Many Segments */
#define P299_MIN_MEAN_BIE_OOS                          49008 /* P299_STE_WRT_DATA MIN MEAN BIE OOS */
#define SSD_PE_COUNT_LIMIT                             49010 /* SSD PE Cycle Count Limit Exceeded */
#define RFWD_EC_RFWD_STREAM_XFER_ERROR                 49011 /* RFWD Streaming Signature Transfer Error */
#define RFWD_EC_EXTRACTION_TPM_DL_ERROR                49012 /* RFWD Extraction TPM Download Error */
#define RFWD_EC_INIT_TPM_DL_ERROR                      49013 /* RFWD Initialization TPM Download Error */
#define TA_GOTF_COMBO_EMC                              49014 /* GOTF TA COMBO Out Of Spec - EMC */
#define SYS_AREA_TA_COUNT_EXCEEDED                     49016 /* Check system area for TAs */
#define OAR_ERROR_RATE_OOS                             49017 /* OAR Error Rate out of spec */
#define TA_GOTF_COMBO_DELL                             49018 /* GOTF TA COMBO Out Of Spec - Dell */
#define VBAR_SATIDX_FAIL                               49027 /* Drive failed for trying to index of SATIDX < 0 */
#define T172_MAX_LBA_NOT_VALID                         49028 /* Max LBA is not valid */
#define EXCEED_LUL_DEFECT_COUNT_LIMIT                  49029 /* Exceeded LUL defect count limit */
#define RFWD_EC_PKLFILE_LODFILE_NAME_MISCOMPARE        49030 /* RFWD Pickle File vs LOD File Name Miscompare */
#define TIER_PARTNUM_ON_FIN2                           49039 /* Drive Tier PN run on FIN2 */
#define LTA2_GOTF_LIMIT_FAIL                           49054 /* LTA2 out of Spec P135 */
#define GOTF_MAX_AMP_WIDTH_SPEC                        49055 /* GOTF MAX_AMP_WIDTH out of spec */
#define GOTF_SPSC2_P297_SPEC                           49057 /* Out of GOTF Spec P297 SPSC2  */
#define LTA3_DELTA_BER_OOS                             49082 /* LTA3 Delta BER out of spec  */
#define LTA3_SPEC_SCREEN_FAIL                          49083 /* LTA3 Spec Screen Fail  */
#define LTA4_GOTF_LIMIT_SPEC_FAIL                      49085 /* LTA4 GOTF Combo spec limit Fail  */
#define LTA2_GOTF_LIMIT_SPEC_FAIL                      49086 /* LTA2 GOTF limit Fail  */
#define P107_GOTF_REG_FLAW_SPEC_FAIL                   49097 /* P107 GOTF REG flaws per surface limit fail */
#define GOTF_SPSC2_P297_315_COMBO_SPEC                 49081 /* GOTF Out of Spec MODE_LOSS_2 from P297_315_COMBO table */
#define LTA4_2_GOTF_LIMIT_SPEC_FAIL                    49103 /* LTA4.2 GOTF Combo spec limit Fail  */
#define GOTF_DELTA_MEAN_RAW_BER3_FAIL                  49109 /* GOTF delta mean raw BER measured between READ_SCRN and T250_BER3 */
#define GOTF_T297_INSTABILITY_FULL_COV                 49110 /* GOTF T297 instability failure on FULL_COV and GLITCH_LOSS */
#define PFC_CMD_TIMEOUT                                49127 /* Processor timed out */
#define SMIF_TRAINING_FAILURE                          49128 /* Flash training failed */
#define CHANNEL_INIT_TIEMOUT                           49129 /* Channel initalization timeout */
#define P297_CAL2_SUM_MODE_LOSS_GOTF_FAIL              49140 /* GOTF T297 SUM_MODE_LOSS GOTF fail */
#define DEFECT_COMBO_SPEC_FAIL                         49149 /* Defect Combo Spec Fail */
#define HUMIDITY_SPEC_CHK_BREATHER_FILTER              49150 /* Humidity Spec for Missing Breather Filter issue */
#define P299_DOS_PICK_PSTE_OOS                         49151 /* P299 DOS Pick PSTE OOS */
#define P299_DOS_CNT_ATI_OOS                           49152 /* P299 DOS Count ATI OOS */
#define P299_DOS_Count_STE_OOS                         49153 /* P299 DOS Count STE OOS */
#define WRT_PWR_PICKER_CAPACITY_CALC_OOS               49154 /* Wrt Pwr Picker Capacity Calc OOS */
#define P107_P118_COMBINED_DEF_FLAW_FAIL               49167 /* P107 P118 Combined table: flaws per surface limit and defects added limit reached  */
#define P297_P250_COMBO_TABLE_FAIL_GOTF                49175 /* Fail GOTF from P297_P250_COMBO table */
#define CANNOT_GET_DRIVE_SN                            49176 /* Can not get Drive SN */
#define P299_P315_DSTE_COMBO_SPEC_FAIL                 49182 /* dSTE instability combo spec fail */
#define GOTF_DELTA_MEAN_RAW_BER_FAIL                   49171 /* GOTF delta mean raw BER measured between READ_SCRN and T250_BER */
#define GOTF_VBAR_TPI_VBAR_SME_TABLE_COMBINED_FAIL     49185 /* GOTF VBAR TPI,SME combined table grading fail */
#define WPE_NM_MINIMUM_FAIL                            49177 /* WPE_NM mininum value fail at PRE2:EWAC */
#define GOTF_P135_FINAL_CURVE_FIT_STAT_FAIL            49186 /* GOTF grade T135 MAX and MIN ID_OD DELTA DAC */
#define FTP_HOST_SERVICE_FAILURE                       49197 /* Sometimes we can't communicate with a site's Save and Restore FTP server and that's sad */
