// Do NOT modify or remove this copyright and confidentiality notice!
//
// Copyright (c) 2001 - $Date: 2016/10/03 $ Seagate Technology, LLC.
//
// The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
// Portions are also trade secret. Any use, duplication, derivation, distribution
// or disclosure of this code, for any reason, not expressly authorized is
// prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
//

/*******************************************************************************
*
* VCS Information:
*                 $File: //depot/TSE/Shared/source/DIN_DEX/messages.h $
*                 $Revision: #139 $
*                 $Change: 1127728 $
*                 $Author: brandon.j.templin $
*                 $DateTime: 2016/10/03 10:35:36 $
*
*******************************************************************************/
/*******************************************************************************
*
*        designer: J. S. Finch
*
*     description: This file is for establishing encoded string reporting from firmware.
*                  Acceptable uses are reporting:
*                     1. errors to the text file only.
*                     2. messages (in lieu of using send_debug_message)
*
*      Rules:
*              1) Messages must be limited to 80 characters on a single line.
*              2) Variable data is NOT allowed; If this capability is needed, use a standard DBLog table.
*              3) Keep messages for each FW type (SELFTEST, IOTEST, SATATEST, etc.) within their designated sections.
*              4) Use the MSG__ (double underscore) prefix for all entries.  This will make finding the population in the source code much simpler.
*
*  Use the P_MESSAGE table defined in table_cd.h to report these encoded messages.
*  Keep messages short and to the point.
*
*******************************************************************************/
/****************************************************************************************************************************

   #               #    ##        ######      #      #   ###   #      #     ######
    #             #    #  #       #      #    # #    #    #    # #    #    #      #
     #     #     #    #    #      #      #    #  #   #    #    #  #   #   #
      #   # #   #    ########     ######      #   #  #    #    #   #  #   #     ###
       # #   # #    #        #    #     #     #    # #    #    #    # #   #       #
        #     #    #          #   #      #    #     ##    #    #     ##    #      #
        #     #   #            #  #       #   #      #   ###   #      #      ####

 Deleting or modifying any established entry or its attributes in this file could result in serious process consequences.
 E.g. previously released firmware that depends on the changed or deleted entry will function incorrectly or could stop
 functioning altogether.

 If a change is needed in an established entry, a new entry must be made to incorporate that change.
 This MUST be observed until a permanent solution is in place.

*****************************************************************************************************************************/

// *******************  SELFTEST DBLog Message definitions  *************************
//      Message define               MESSAGE_CODE  ***  Message ***
#define MSG__ITERATION                          0  /* Iteration Gains (dB) */
#define MSG__FINAL_SCAN                         1  /* Final Gains (dB) */
#define MSG__NO_TM_FOUND                        2  /* No TM found Headswitch failed */
#define MSG__RETRACT_FAILED                     3  /* Retract failed - Heads over data */
#define MSG__DEMOD_SYNC                         4  /* Demod Sync Retry after failure */
#define MSG__HRP_WRT_ERROR                      5  /* HRP Wrt Error */
#define MSG__DISCARD_POINTS                     6  /* Too many Discard Points */
#define MSG__MOVING_AVG_ON                      7  /* Moving Avg must be on for FFT-First */
#define MSG__BASELINE_FAILURE                   8  /* Baseline Failure */
#define MSG__BL_PSD_SM                          9  /* BL PSD SM */
#define MSG__MEASURED_FAILURE                  10  /* Measured Failure */
#define MSG__DPSD                              11  /* dPSD */
#define MSG__DPSD_SMOOTH                       12  /* dPSD Smooth */
#define MSG__AGC                               13  /* AGC */
#define MSG__DAGC                              14  /* DAGC */
#define MSG__SMOOTH_DPES                       15  /* SmoothdPES */
#define MSG__HEATER_MAX_SWEEP                  16  /* Heater reached max sweep */
#define MSG__SFLAWT_INVALID                    17  /* Invalid track data in Servo Flaw Table */
#define MSG__WRITE_ZAP                         18  /* WRITE ZAP: */
#define MSG__READ_ZAP                          19  /* READ ZAP: */
#define MSG__ASP_LOGGED                        20  /* ASP Logged: */
#define MSG__DBI_LOG_FLUSHED_1                 21  /* DBI Log Flushed 1 */
#define MSG__NO_MORE_NEW_RECS                  22  /* No More New Recs */
#define MSG__NO_MORE_ACCUM_RECS                23  /* No More Accum Recs */
#define MSG__MERGE_NEW_ACCUM                   24  /* Merge New Accum */
#define MSG__SHOULD_NOT_OCCUR_1                25  /* Should Not Occur #1 */
#define MSG__SHOULD_NOT_OCCUR_2                26  /* Should Not Occur #2 */
#define MSG__WEDGE_NUMBER_OVERRANGE            27  /* Wedge Number Overrange */
#define MSG__TIGHTENED_SPECS                   28  /* Tightened Specs */
#define MSG__ORIGINAL_SPECS                    29  /* Original Specs */
#define MSG__ENABLE_ZAP                        30  /* ZAP must be Enabled */
#define MSG__DISABLE_ZAP                       31  /* ZAP must be Disabled */
#define MSG__ENABLE_REJECT_CHROME              32  /* REJECT CHROME must be Enabled */
#define MSG__DISABLE_REJECT_CHROME             33  /* REJECT CHROME must be Disabled */
#define MSG__ENABLE_VCAT_VIRTUAL_MODE          34  /* VCAT virtual mode must be Enabled */
#define MSG__DISABLE_VCAT_VIRTUAL_MODE         35  /* VCAT virtual mode must be Disabled */
#define MSG__BAD_u16_TIMING_MARK_NOT_DETECTED  36  /* BAD u16_TIMING_MARK_NOT_DETECTED */
#define MSG__1ST_LVL_UNSERVOABLE               37  /* 1ST LVL: UNSERVOABLE */
#define MSG__1ST_LVL                           38  /* 1ST LVL: */
#define MSG__2ND_LVL                           39  /* 2ND LVL: */
#define MSG__LOOK_BACK                         40  /* LOOK BACK: */
#define MSG__SKIP_LB_UNVER                     41  /* SKIP LB: UNVER */
#define MSG__VER_1                             42  /* VER 1: */
#define MSG__SKIP_LB_ADJ_TO_WEDGE_1            43  /* SKIP LB: ADJ TO WEDGE1 */
#define MSG__SKIP_LB_TOO_CLOSE_TO_WEDGE_1      44  /* SKIP LB: TOO CLOSE TO WEDGE1 */
#define MSG__VER_2                             45  /* VER 2: */
#define MSG__SKIP_LB_ADJ_TO_WEDGE_2            46  /* SKIP LB: ADJ TO WEDGE2 */
#define MSG__SKIP_LB_TOO_CLOSE_TO_WEDGE_2      47  /* SKIP LB: TOO CLOSE TO WEDGE2 */
#define MSG__VER_3                             48  /* VER 3: */
#define MSG__QUIT_4TH_VER                      49  /* QUIT: 4TH VER */
#define MSG__LBT_NV                            50  /* LBT: NV */
#define MSG__LBT_V                             51  /* LBT: V */
#define MSG__LBT_DEL_VER_1                     52  /* LBT: DEL VER1 */
#define MSG__LBT_DEL_VER_2                     53  /* LBT: DEL VER2 */
#define MSG__LBT_ADJ_TO_WEDGE_1                54  /* LBT: ADJ TO WEDGE1 */
#define MSG__LBT_DEL_VER_3                     55  /* LBT: DEL VER3 */
#define MSG__LBT_ADJ_TO_WEDGE_2                56  /* LBT: ADJ TO WEDGE2 */
#define MSG__2ND_LVL_UNSERVOABLE               57  /* 2ND LVL: UNSERVOABLE */
#define MSG__LOG_SKIP_TRACK                    58  /* LOG SKIP-TRACK: */
#define MSG__CERT_SFLAW_TRACK_FAILED           59  /* CERT SFLAW: TRACK FAILED: */
#define MSG__INVALID_MODE                      60  /* Invalid Mode! */
#define MSG__FCS_CATCH_ALL_NOT_SELECTED        61  /* FCS_CATCH_ALL_NOT_SELECTED */
#define MSG__PRE_CHROME                        62  /* PRE-CHROME: */
#define MSG__POST_CHROME                       63  /* POST-CHROME: */
#define MSG__DPES_FIXEDBASELINE                64  /* Dpes from fixed baseline in moving baseline*/
#define MSG__BURNISH_WARNING                   65  /* BURNISH WARNING - 1T SS Write without interleave support */
#define MSG__ZAP_PARITY_ERRORS                 66  /* TOO MANY ZAP PARITY ERRORS.  SLIP TRACK */
#define MSG__BUTTERFLY_SEEKS                   67  /* Butterfly Seeks */
#define MSG__IDOD_SEEKS                        68  /* IDOD Seeks */
#define MSG__SWEEP_SEEKS                       69  /* Sweep Seeks */
#define MSG__SPIN_DOWN_IDLE_TIME               70  /* Spin Down Idle Time */
#define MSG__OPTIMIZATION_SCAN                 71  /* Optimization Scan */
#define MSG__VERIFICATION_SCAN                 72  /* Verification Scan */
#define MSG__ACFF_DID_NOT_UPDATE               73  /* Acffs did not update */
#define MSG__VBAR_4K_SPLIT_SECTOR_MODE         74  /* VBAR 4K split sector MODE .... */
#define MSG__MULT_EN_WG                        75  /* SCOPY multi enable WG */
#define MSG__NOT_EN_WG                         76  /* SCOPY not enable WG */
#define MSG__PARAM_FAULT                       77  /* SCOPY param fault */
#define MSG__STATE_FAULT                       78  /* SCOPY state fault */
#define MSG__WRT_UNF_FAULT                     79  /* SCOPY wrt unf fault */
#define MSG__WRITE_FAULT                       80  /* SCOPY write fault */
#define MSG__COMP_INSIDE_WG                    81  /* SCOPY comp inside WG */
#define MSG__SCOPY_UNDEFINED_SERVO             82  /* SCOPY Unknown Servo fault */
#define MSG__BACKOFF_SQZ_TO_RECOVER            83  /* Backoff Squeeze to recover at nominal */
#define MSG__BUCKET_RAILED_RD_OFFSET_RESTORED  84  /* Rd Offset Search Railed, Original Offset Restored */
#define MSG__FAILED_AC_DIAG_SEEK               85  /* Failed AC Diag Seek */
#define MSG__MEASURE_ZONE_OFFSET_FAILED        86  /* Measure Zone Offset Failed */
#define MSG__MEASURE_LIMIT_FAILED              87  /* Failed Measure Limit */
#define MSG__DC_OFFSET_TOO_BIG                 88  /* DC offset too big */
#define MSG__TIME_OFFSET_TOO_BIG               89  /* Time offset too big */
#define MSG__FINAL_DC_OFFSET_TOO_BIG           90  /* Final DC offset too big */
#define MSG__FINAL_TIME_OFFSET_TOO_BIG         91  /* Final Time offset too big */
#define MSG__SAP_TIMING_ENABLED                92  /* SAP timing enabled */
#define MSG__NOT_ENOUGH_POINTS                 93  /* Failed to measure enough points */
#define MSG__FINAL_AC_TRACK_TOO_BIG            94  /* Final AC track too big */
#define MSG__FINAL_AC_TIME_TOO_BIG             95  /* Final time AC too big */
#define MSG__FAILED_SEEK_BNDRY_ADJ             96  /* Failed seek after boundary adjustment */
#define MSG__FAILED_FORCE_FROM_ZONE_SEEK       97  /* Failed force-from-zone phys safe seek */
#define MSG__MEASUREMENT_FAILED_TMVALID        98  /* No TMValid, Measurment failed */
#define MSG__RESIDUAL_FAILED                   99  /* Residual Failed */
#define MSG__NO_TMVALID_FOUND                 100  /* No TMValid found */
#define MSG__TRACK_UNVIRTUALIZER_WRAPAROUND   101  /* Warning - Possible track unvirtualizer buffer wrap-around; Data may be corrupted. */
#define MSG__BAD_HEADSWITCH_CAL_SEEK          102  /* Headswitch cal seek failed */
#define MSG__NO_LENGTH_GIVEN_RADIX_2_FFT      103  /* A length must be provided for radix 2 fft. */
#define MSG__PLIST_SLIST_COPY_FAILURE         104  /* Plist and Slist copy failed. */
#define MSG__FLAWLISTS_COPIED                 105  /* Plist and Slist copied to buffer. */
#define MSG__LOWER_ZONED_TIME_LIMIT_FAILED    106  /* Lower zone specific time offset failed*/
#define MSG__UPPER_ZONED_TIME_LIMIT_FAILED    107  /* Upper zone specific time offset failed*/
#define MSG__INCOMPATIBLE_FILE_OPTS_SELECTED  108  /* Can't save and retrieve in same test call. */
#define MSG__GAP_ALREADY_CALIBRATED           109  /* Can't rerun Gap cal unless RAP is restored to defaults. */
#define MSG__CAL_TRANSITION_NOT_FOUND         110  /* Couldn't find timing delay transition point. */
#define MSG__NO_ZAP_POLY_COEFFS               111  /* Zap polynomial coefficients not stored in SAP. */
#define MSG__INTERPOLATION_APPLIED            112  /* Bode measurement included frequency which required interpolation. */
#define MSG__VCM_HEAT_SEEKS_NOT_SUPPORTED     113  /* VCM heat seeks requested in parameters but not supported in code. */
#define MSG__APPLYING_RESCUE_NOTCH            114  /* Rescue notch required and placed to restore margin. */
#define MSG__RESCUE_NOTCH_NOT_AVAILABLE       115  /* Rescue notch required but no notch available to place. */
#define MSG__BASELINE_BER                     116  /* Measuring baseline bit error rate. */
#define MSG__BASELINE_BER_COMPLETE            117  /* Baseline BER measurements complete. */
#define MSG__BASELINE_RESISTANCE              118  /* Measuring baseline head and DETCR resistance. */
#define MSG__BASELINE_RESISTANCE_COMPLETE     119  /* Baseline head resistance and DETCR resistance measurements completed. */
#define MSG__BAD_BER_ZONES_REQUESTED          120  /* Invalid zones chosen for bit error rate measurements. */
#define MSG__PROBLEM_WRITING_BER_TRACKS       121  /* Bit error rate tracks not written! */
#define MSG_BAD_DWELL_OPTIONS                 122  /* Invalid dwell type chosen. */
#define MSG__NO_TA_MET_INC_CRIT               123  /* No TA's met inclusion for the parameters provided, no tracks to dwell on. */
#define MSG__COULD_NOT_GET_BER_TRKS           124  /* Unable to assign the required bit error rate test tracks. */
#define MSG__NO_DATA_TO_INTERPOLATE           125  /* No Data Point found to interpolate. */
#define MSG__UPDATING_SEEK_LENGTH             126  /* Updating the test seek length. */
#define MSG__VARIABLE_ZBZ_SUPPORTED           127  /* Variable SGate Zone By Zone enabled. */
#define MSG__CONSECUTIVE_PT_RQMT_FAILED       128  /* Too many consecutive data points missing to do poly fit. */
#define MSG__MIN_PT_RQMT_FAILED               129  /* Too many data points missing to do poly fit. */
#define MSG__CANT_MEASURE_SKEW_ON_ONE_HEAD    130  /* DC Skew Cal is not required for a one head drive and will not be run. */
#define MSG__SCAN_TNU_SFLAW_TABLE_FULL        131  /* Servo flaw table full during TNU scan */
#define MSG__SCAN_TNU_TOO_MANY_SKIP_TRACKS    132  /* Too many skip tracks during TNU scan */
#define MSG__AGC_LIFT_RAMP_DETECT_FAILED      133  /* AGC Lift Ramp Detect Failed */
#define MSG__T285_REQUIRES_VBAR_SUPPORT       134  /* T285 requires V3BAR support */
#define MSG__T43_SKEW_CHECK_NEED_2_CYLS       135  /* Geometry skew check requires at least 2 points to check OD and ID */
#define MSG__SWD_ENABLED                      136  /* SWD Enabled */
#define MSG__SWD_DISABLED                     137  /* SWD Disabled */
#define MSG__SHOCK_SENSOR_ENABLED             138  /* Shock Sensor Enabled */
#define MSG__SHOCK_SENSOR_DISABLED            139  /* Shock Sensor Disabled */
#define MSG__SWD_ALREADY_ENABLED              140  /* SWD was found enabled prior to the command to enable SWD */
#define MSG__SWD_ALREADY_DISABLED             141  /* SWD was found disabled prior to the command to disable SWD */
#define MSG__SHOCK_ALREADY_ENABLED            142  /* Shock Sensor was found enabled prior to the command to enable Shock Sensor */
#define MSG__SHOCK_ALREADY_DISABLED           143  /* Shock Sensor was found disabled prior to the command to disable Shock Sensor */
#define MSG__ALT_PH_NOTCH_REQ_BR_1_5          144  /* Enable B.R of SERVO_BODE to 1.5 for Detrended Phase response SNO. */
#define MSG__ALL_PASS_FILTER_ENABLED          145  /* Phase response SNO placed all pass filter prior to Bode measurement. */
#define MSG__RVLV_ENABLED                     146  /* RVLV Enabled */
#define MSG__RVLV_DISABLED                    147  /* RVLV Disabled */
#define MSG__RVLV_ALREADY_ENABLED             148  /* RVLV was found enabled prior to the command to enable RVLV */
#define MSG__RVLV_ALREADY_DISABLED            149  /* RVLV was found disabled prior to the command to disable RVLV */
#define MSG__SELFTEST_RESERVED_END          15999  /* Place your message here */
/****************************************************************************************************************************

   #               #    ##        ######      #      #   ###   #      #     ######
    #             #    #  #       #      #    # #    #    #    # #    #    #      #
     #     #     #    #    #      #      #    #  #   #    #    #  #   #   #
      #   # #   #    ########     ######      #   #  #    #    #   #  #   #     ###
       # #   # #    #        #    #     #     #    # #    #    #    # #   #       #
        #     #    #          #   #      #    #     ##    #    #     ##    #      #
        #     #   #            #  #       #   #      #   ###   #      #      ####

 Deleting or modifying any established entry or its attributes in this file could result in serious process consequences.
 E.g. previously released firmware that depends on the changed or deleted entry will function incorrectly or could stop
 functioning altogether.

 If a change is needed in an established entry, a new entry must be made to incorporate that change.
 This MUST be observed until a permanent solution is in place.

*****************************************************************************************************************************/

// *******************  IOTEST DBLog Message definitions  ***************************
//      Message define               MESSAGE_CODE  ***  Message ***
#define MSG__IOTEST_DASH_LINE               16000  /* - */
#define MSG__IOTEST_WRV_WWN                 16001  /* Write/read/verify world wide address to etf block 0 */
#define MSG__IOTEST_READ_ETF_WWN            16002  /* Read world wide address from etf block 0 */
#define MSG__IOTEST_READ_FLASH_WWN          16003  /* Read world wide address from flash */
#define MSG__IOTEST_XFR_WWN_ETF_2_FLASH     16004  /* Transfer world wide address from the etf log to flash */
#define MSG__IOTEST_XFR_WWN_FLASH_2_ETF     16005  /* Transfer world wide address from the flash to etf log */
#define MSG__IOTEST_COMPARE_WWN             16006  /* Compare world wide address */
#define MSG__IOTEST_PH1                     16007  /*  */
#define MSG__IOTEST_CLEAR_LOGS              16008  /* Clear Logs */
#define MSG__IOTEST_BLANK_LINE              16009  /*  */
#define MSG__IOTEST_BAD_SENSE_1             16010  /* Bad sense after first request sense */
#define MSG__IOTEST_BAD_SENSE_2             16011  /* Bad sense after second request sense */
#define MSG__IOTEST_544_HEADER              16012  /* Reset Response Verify Test */
#define MSG__IOTEST_ILL_VP_PAGE             16013  /* Illegal vital page %X selected */
#define MSG__IOTEST_REC_INQ_DATA            16014  /* Received Inquiry Data: */
#define MSG__IOTEST_EXP_INQ_DATA            16015  /* Expected Inquiry Data: */
#define MSG__IOTEST_CURR_PAGE_SELECTED      16016  /* Current page selected */
#define MSG__IOTEST_DEFT_PAGE_SELECTED      16017  /* Default page selected */
#define MSG__IOTEST_SAVED_PAGE_SELECTED     16018  /* Saved page selected  */
#define MSG__IOTEST_CHGB_PAGE_SELECTED      16019  /* Changeable page selected */
#define MSG__IOTEST_PRIMARY_EQUIP_SPEC      16020  /* Primary equipment spec. (Equip Spec) */
#define MSG__IOTEST_SECONDY_EQUIP_SPEC      16021  /* Secondary equipment spec. (Equip Spec 2 if valid, else Equip Spec again) */
#define MSG__IOTEST_CURR_VALUES             16022  /* Current values */
#define MSG__IOTEST_DEFT_VALUES             16023  /* Default values */
#define MSG__IOTEST_SAVED_VALUES            16024  /* Saved values  */
#define MSG__IOTEST_CHGB_VALUES             16025  /* Changeable values */
#define MSG__IOTEST_MODE_SENSE_DATA         16026  /* MODE SENSE DATA: */
#define MSG__IOTEST_APPLE_DATA_136          16027  /* Apple drives require at least 136 bytes returned */
#define MSG__IOTEST_RECEIVED_CAP            16028  /* Received Capacity Data: */
#define MSG__IOTEST_EXPECTED_CAP            16029  /* Expected Capacity Data: */
#define MSG__IOTEST_SER_NUM_TEST            16030  /* Compare Serial Number Test: */
#define MSG__IOTEST_INQ_SER_NUM             16031  /* Inquiry serial number digits:: */
#define MSG__IOTEST_STP_SER_NUM             16032  /* STP supplied serial number digits: */
#define MSG__IOTEST_AUTH_MAKERSYMK1         16033  /* ---> Authority is MakerSymK - attempt 1 <---*/
#define MSG__IOTEST_AUTH_MAKERSYMK2         16034  /* ---> Authority is MakerSymK - attempt 2 <---*/
#define MSG__IOTEST_AUTH_MSID               16035  /* ---> Authority is MSID <---*/
#define MSG__IOTEST_AUTH_SID                16036  /* ---> Authority is SID <---*/
#define MSG__IOTEST_AUTH_BANDMASTER0        16037  /* ---> Authority is BandMaster0 <---*/
#define MSG__IOTEST_AUTH_BANDMASTER1        16038  /* ---> Authority is BandMaster1 <---*/
#define MSG__IOTEST_GET_SEC_STATE_CNTRL     16039  /* ---> Getting Security State Control Table <---*/
#define MSG__IOTEST_SET_SEC_STATE_CNTRL     16040  /* ---> Setting Security State Control Table <---*/
#define MSG__IOTEST_SET_MSID_CRED           16041  /* ---> Set MSID Credential <---*/
#define MSG__IOTEST_SET_SID_CRED            16042  /* ---> Set SID Credential <---*/
#define MSG__IOTEST_SET_BM0_CRED            16043  /* ---> Set BandMaster0 Credential <---*/
#define MSG__IOTEST_SET_BM1_CRED            16044  /* ---> Set BandMaster1 Credential <---*/
#define MSG__IOTEST_SET_EM_CRED             16045  /* ---> Set EraseMaster Credential <---*/
#define MSG__IOTEST_GET_TPERINFO_TABLE      16046  /* ---> Get TPer Info Table <---*/
#define MSG__IOTEST_GET_LOCK_TABLE_BAND1    16047  /* ---> Get Locking Table - Band <---*/
#define MSG__IOTEST_NOT_AUTH                16048  /* ---> NOT AUTHORIZED <---*/
#define MSG__IOTEST_READ_ONLY               16049  /* ---> READ ONLY <---*/
#define MSG__IOTEST_SP_BUSY                 16050  /* ---> SP BUSY <---*/
#define MSG__IOTEST_SP_FAILED               16051  /* ---> SP FAILED <---*/
#define MSG__IOTEST_SP_DISABLED             16052  /* ---> SP DISABLED <---*/
#define MSG__IOTEST_SP_FROZEN               16053  /* ---> SP FROZEN <---*/
#define MSG__IOTEST_INDEX_CONFLICT          16054  /* ---> INDEX CONFLICT <---*/
#define MSG__IOTEST_INSUFF_SPACE            16055  /* ---> INSUFFICIENT SPACE <---*/
#define MSG__IOTEST_INSUFF_ROWS             16056  /* ---> INSUFFICIENT ROWS <---*/
#define MSG__IOTEST_INV_COMMAND             16057  /* ---> INVALID COMMAND <---*/
#define MSG__IOTEST_INV_PARAM               16058  /* ---> INVALID PARAMETER <---*/
#define MSG__IOTEST_INVALID_REF             16059  /* ---> INVALID REFERENCE <---*/
#define MSG__IOTEST_INVALID_DATA            16060  /* ---> INVALID DATA <---*/
#define MSG__IOTEST_INV_SECMSG_PROP         16061  /* ---> INVALID SECMSG PROPERTIES <---*/
#define MSG__IOTEST_TPER_MALFUNC            16062  /* ---> TPER MALFUNCTION <---*/
#define MSG__IOTEST_TRANS_FAILURE           16063  /* ---> TRANSACTION FAILURE <---*/
#define MSG__IOTEST_RESP_OVRFLW             16064  /* ---> RESPONSE OVERFLOW <---*/
#define MSG__IOTEST_AUTH_PASSED             16065  /* ---> Authentication passed <---*/
#define MSG__IOTEST_AUTH_FAILED_ZSR         16066  /* ---> Authentication failed - zero status returned<---*/
#define MSG__IOTEST_AUTH_LOST               16067  /* ---> Authentication fail - timeout waiting for SECURITY IN cmd <---*/
#define MSG__IOTEST_NO_SESS_AVAIL           16068  /* ---> NO SESSIONS AVAILABLE <---*/
#define MSG__IOTEST_SET_TABLE_PASSED        16069  /* ---> Set Table passed <---*/
#define MSG__IOTEST_SET_TABLE_FAILED        16070  /* ---> Set Table failed <---*/
#define MSG__IOTEST_SET_TABLE_LOST          16071  /* ---> Set table process failure <---*/
#define MSG__IOTEST_GET_TABLE_PASSED        16072  /* ---> Get Table passed <---*/
#define MSG__IOTEST_GET_TABLE_FAILED        16073  /* ---> Get Table failed <---*/
#define MSG__IOTEST_GET_TABLE_LOST          16074  /* ---> Get table process failure <---*/
#define MSG__IOTEST_AUTH_ERASEMASTER        16075  /* ---> Authority was EraseMaster <---*/
#define MSG__IOTEST_SET_GUDID_NU            16076  /* ---> Set GUDID - serial number field in TPerInfo table <---*/
#define MSG__IOTEST_SET_FW_VER_NU           16077  /* ---> Set Firmware version in TPerInfo table <---*/
#define MSG__IOTEST_POWER_CYCLE_DRIVE       16078  /* Power cycle the drive */
#define MSG__IOTEST_RD_WRT_DRV_PROBL        16079  /* Problem Reading/Writing from/to the drive */
#define MSG__IOTEST_RD_WRT_BLK_PROBL        16080  /* Problem Reading/Writing block */
#define MSG__IOTEST_SAVING_PROBLEM          16081  /* Problem Saving Data */
#define MSG__IOTEST_DATA_SAVED              16082  /* Data are saved to the disk */
#define MSG__IOTEST_WRITE_TO_DISK           16083  /* Retry writing to disk */
#define MSG__IOTEST_ADAP_GAIN_SAVED         16084  /* Adaptive Gain are saved to disk */
#define MSG__IOTEST_HEADER_MISMATCH         16085  /* Header Mismatched */
#define MSG__IOTEST_RANDOM_LBA_EXCEEDED     16086  /* Warning: random_lba_seed exceeds end_lba */
#define MSG__IOTEST_SEEK_TIME_SAVED         16087  /* Min/Max/Ave Seek Time are saved */
#define MSG__IOTEST_SEEK_TIME_SAVED_PROBL   16088  /* Problem saving the Seek Time */
#define MSG__IOTEST_PMSE_DATA_SAVED         16089  /* PMSE Data are saved to the disk */
#define MSG__IOTEST_PORT_BUSY_DETECT        16090  /* Port Busy detected */
#define MSG__IOTEST_CYL_NOT_MATCHED         16091  /* Cylinders NOT matched! */
#define MSG__IOTEST_4TH_ORDER_POLYNOMIAL    16092  /* 4th Order Polynomial */
#define MSG__IOTEST_CLEANUP_FAILED          16093  /* Cleanup failed after retries */
#define MSG__IOTEST_BIAS_MISMATCHED         16094  /* Bias number Mismatched */
#define MSG__IOTEST_INVALID_T192_HEADER     16095  /* Invalid SPT Test 192 Header */
#define MSG__IOTEST_RESTORED_FAILED         16096  /* CF/CE restore was not good. Retry was done */
#define MSG__IOTEST_RW_EXTENED_FAILED       16097  /* Wrt/Rd Extended was not good. Retries was done */
#define MSG__IOTEST_CHKSUM_MISMATCH         16098  /* Checksum Mismatched */
#define MSG__IOTEST_CLOSE_SESSION           16099  /* ---> Close session issued <---*/
#define MSG__IOTEST_ADMIN_START_SESSION     16100  /* ---> AdminSP start session issued <---*/
#define MSG__IOTEST_LOCKING_START_SESSION   16101  /* ---> LockingSP start session issued <---*/
#define MSG__IOTEST_START_SESSION_FAILED    16102  /* ---> Start Session Failed <---*/
#define MSG__IOTEST_CLOSE_SESSION_FAILED    16103  /* ---> Close Session Failed <---*/
#define MSG__IOTEST_SET_BAND_LOCK           16104  /* ---> Band Locked <---*/
#define MSG__IOTEST_SET_BAND_CREATED        16105  /* ---> Creating Band <---*/
#define MSG__IOTEST_SET_BAND_UNLOCKED       16106  /* ---> Band Unlocked <---*/
#define MSG__IOTEST_SET_MAKERSYMK_KEY_NU    16107  /* ---> Updating MakerSymK credential <---*/
#define MSG__IOTEST_CQM_CHKSUM_MISMATCH     16108  /* CQM Checksum Mismatched */
#define MSG__IOTEST_PSME_CHKSUM_MISMATCH    16109  /* PSME Checksum Mismatched */
#define MSG__IOTEST_SPT_CHKSUM_MISMATCH     16110  /* SPT Checksum Mismatched */
#define MSG__IOTEST_INVALID_SPT_DATA_SAVED  16111  /* Invalid SPT Data Saved */
#define MSG__IOTEST_CQM_DATA_SAVED          16112  /* CQM Data are saved to the disk */
#define MSG__IOTEST_FAILING_PAGE            16113  /* Failing page(s) */
#define MSG__IOTEST_DRIVE_ALREADY_SE_MODE   16114  /* Drive already in SE mode. */
#define MSG__IOTEST_FORCE_SINGLE_ENDED_MODE 16115  /* Force Single Ended Mode */
#define MSG__IOTEST_DRIVE_ALREADY_LVD_MODE  16116  /* Drive already in LVD mode. */
#define MSG__IOTEST_MIN_MAX_AVE_SEEK_TIME   16117  /* Min/Max/Ave Seek Time are saved. */
#define MSG__IOTEST_PROBLEM_SAVE_SEEK_TIME  16118  /* Problem saving the Seek Time. */
#define MSG__IOTEST_PROBLEM_READING_BLOCK   16119  /* Problem reading the block. */
#define MSG__IOTEST_PORT_BUSY_DETECTED      16120  /* Port Busy detected */
#define MSG__IOTEST_INVALID_TEST_FOR_SAS    16121  /* Invalid test for SAS */
#define MSG__IOTEST_CRC_ADDRESS_DETECTED    16122  /* CRC Address detected. */
#define MSG__IOTEST_CRC_DATA_DETECTED       16123  /* CRC Data detected. */
#define MSG__IOTEST_RETRY_EXECUTED          16124  /* Retry Executed */
#define MSG__IOTEST_END_WORD_NOT_FOUND      16125  /* End word not found! */
#define MSG__IOTEST_CYCLINDERS_NOT_MATCHED  16126  /* Cylinders NOT matched! */
#define MSG__IOTEST_WRITE_READ_EXT_RETRY    16127  /* Wrt/Rd Extended Retry. */
#define MSG__IOTEST_PROBLEM_READING_T707    16128  /* Problem reading Test 707. */
#define MSG__IOTEST_PROBLEM_READING_T714    16129  /* Problem reading Test 714. */
#define MSG__IOTEST_DRIVE_STATE_MISCCOMPARE 16130  /* ---> Drive Security State incorrect after Set_Table method <---*/
#define MSG__IOTEST_CLOSE_FAILED_SESSION    16131  /* ---> Closing session after previous test failed <---*/
#define MSG__IOTEST_CLOSE_SESS_FAILED       16132  /* ---> Failed to close session after previous test failure  <---*/
#define MSG__IOTEST_UNKNOWN_STATUS          16133  /* ---> UNKNOWN ERROR Cannot parse <--- */
#define MSG__IOTEST_DISP_REC_DATA           16134  /* ---> SECURITY IN frame data <--- */
#define MSG__IOTEST_DISP_SENT_DATA          16135  /* ---> SECURITY OUT frame data <---*/
#define MSG__IOTEST_RESPONSE_CODE_00        16136  /* Task Management Function Completed */
#define MSG__IOTEST_RESPONSE_CODE_02        16137  /* Invalid Frame */
#define MSG__IOTEST_RESPONSE_CODE_04        16138  /* Task Management Function Not Supported  */
#define MSG__IOTEST_RESPONSE_CODE_05        16139  /* Task Management Function Failed */
#define MSG__IOTEST_RESPONSE_CODE_08        16140  /* Task Management Function Succeeded  */
#define MSG__IOTEST_RESPONSE_CODE_09        16141  /* Incorrect Logical Unit Number */
#define MSG__IOTEST_RESPONSE_CODE_0A        16142  /* Overlapped Tag Attempted */
#define MSG__IOTEST_FLASHED_LED             16143  /* Initiator Flashed LED Detected */
#define MSG__IOTEST_DISP_PROPERTIES         16144  /* ---> DRIVE Properties <---*/
#define MSG__IOTEST_AUTH_FAILED_NZSC        16145  /* ---> Authentication failed - non zero status code <---*/
#define MSG__IOTEST_AUTH_FAILED_NNR         16146  /* ---> Authentication failed - no nonce returned <---*/
#define MSG__IOTEST_GET_TABLE               16147  /* ---> Executing Get Table <---*/
#define MSG__IOTEST_SET_TABLE               16148  /* ---> Executing Set Table <---*/
#define MSG__IOTEST_SET_SETUP_STATE         16149  /* ---> Setting setup state <---*/
#define MSG__IOTEST_SET_MANUFACTURING_STATE 16150  /* ---> Setting manufacturing state <---*/
#define MSG__IOTEST_SET_USE_STATE           16151  /* ---> Setting use state <---*/
#define MSG__IOTEST_SET_DIAG_STATE          16152  /* ---> Setting diag state <---*/
#define MSG__IOTEST_SET_SID_CREDENTIAL      16153  /* ---> Writing SID credential <---*/
#define MSG__IOTEST_SET_MSID_CREDENTIAL     16154  /* ---> Writing MSID credential <---*/
#define MSG__IOTEST_SET_BM0_CREDENTIAL      16155  /* ---> Writing Bandmaster credential <---*/
#define MSG__IOTEST_SET_BM1_CREDENTIAL      16156  /* ---> Writing Bandmaster 1 credential <---*/
#define MSG__IOTEST_SET_EM_CREDENTIAL       16157  /* ---> Writing Erasemaster credential <---*/
#define MSG__IOTEST_SET_GUDID               16158  /* ---> Setting GUDID <---*/
#define MSG__IOTEST_SET_FW_VER              16159  /* ---> Writing Firmware Version <---*/
#define MSG__IOTEST_SET_BYTES               16160  /* ---> Setting Byte Table <---*/
#define MSG__IOTEST_CONFIGURE_BAND          16161  /* ---> Configuring Band <---*/
#define MSG__IOTEST_CREATE_BAND             16162  /* ---> Creating Band <---*/
#define MSG__IOTEST_ERASE_BAND              16163  /* ---> Erasing Band <---*/
#define MSG__IOTEST_SET_MAKERSYMK_KEY       16164  /* ---> Writing MakerSymK 3DES Credential <---*/
#define MSG__IOTEST_SET_FW_LOCK             16165  /* ---> Writing to Port Locking table Unlock<---*/
#define MSG__IOTEST_SET_CERTIFICATE         16166  /* ---> Writing Certificates <---*/
#define MSG__IOTEST_SET_RSA_KEYS            16167  /* ---> Writing RSA Keys <---*/
#define MSG__IOTEST_SET_C_L_O_R             16168  /* ---> Writing Clear Lock On Reset <---*/
#define MSG__IOTEST_ENABLE_BAND             16169  /* ---> Enabling Band <---*/
#define MSG__IOTEST_DISABLE_BAND            16170  /* ---> Disabling Band <---*/
#define MSG__IOTEST_SET_FW_LOCK_ON          16171  /* ---> Writing to Port Locking table Lock<---*/
#define MSG__IOTEST_SET_SOM0_STATE          16172  /* ---> Setting SOM 0 state <---*/
#define MSG__IOTEST_SET_SOM1_STATE          16173  /* ---> Setting SOM 1 state <---*/
#define MSG__IOTEST_SET_SOM2_STATE          16174  /* ---> Setting SOM 2 state <---*/
#define MSG__IOTEST_SET_PSID_CRED           16175  /* ---> Setting PSID Credential <--- */
#define MSG__IOTEST_SET_MAKERSYMK_AES_KEY   16176  /* ---> Writing MakerSymK AES Credential <---*/
#define MSG__IOTEST_SET_MAINTSYMK_KEY       16177  /* ---> Writing MaintSymK AES256 Credential <---*/
#define MSG__IOTEST_SET_TABLE_1D            16178  /* ---> Writing MaintSymK AES Credential <---*/
#define MSG__IOTEST_SET_TABLE_1E            16179  /* ---> Enabling MaintSymK <---*/
#define MSG__IOTEST_SET_TABLE_1F            16180  /* ---> Set PORT LockOnReset <---*/
#define MSG__IOTEST_SET_TABLE_20            16181  /* ---> Se BAND LockOnReset <---*/
#define MSG__IOTEST_SET_TABLE_21            16182  /* ---> Set read and write lock enables <---*/
#define MSG__IOTEST_SET_TABLE_22            16183  /* ---> Security In command failed <---*/
#define MSG__IOTEST_SET_TABLE_23            16184  /* ---> Security In command failed - incorrect session number(1) <---*/
#define MSG__IOTEST_SET_TABLE_24            16185  /* ---> Set ActivationSymK credential <---*/
#define MSG__IOTEST_SET_TABLE_25            16186  /* ---> Set table function x25 placeholder <---*/
#define MSG__IOTEST_SET_TABLE_26            16187  /* ---> Disable xxxxxxxx symk <---*/
#define MSG__IOTEST_SET_TABLE_27            16188  /* ---> Set table function x27 placeholder <---*/
#define MSG__IOTEST_SET_TABLE_28            16189  /* ---> Set table function x28 placeholder <---*/
#define MSG__IOTEST_SET_TABLE_29            16190  /* ---> Set table function x29 placeholder <---*/
#define MSG__IOTEST_SET_TABLE_2A            16191  /* ---> Set table function x2A placeholder <---*/
#define MSG__IOTEST_SET_TABLE_2B            16192  /* ---> Set table function x2B placeholder <---*/
#define MSG__IOTEST_SET_TABLE_2C            16193  /* ---> Set table function x2C placeholder <---*/
#define MSG__IOTEST_SET_TABLE_2D            16194  /* ---> Set table function x2D placeholder <---*/
#define MSG__IOTEST_SET_TABLE_2E            16195  /* ---> Set table function x2E placeholder <---*/
#define MSG__IOTEST_SET_TABLE_2F            16196  /* ---> Set table function x2F placeholder <---*/
#define MSG__IOTEST_GET_CERT_MESSAGE        16197  /* ---> LOOPING IN GET CERT ROUTINE <---*/
#define MSG__IOTEST_GET_CERT_DONE           16198  /* ---> LEAVING GET CERT ROUTINE<---*/
#define MSG__IOTEST_CAPTURE_PERSISTANT_DATA 16199  /* ---> Capturing Persistent Data <--- */
#define MSG__IOTEST_REVERTSP                16200  /* ---> Reverting Persistent Data <--- */
#define MSG__IOTEST_REUSABLE_MESSAGE        16201  /* ---> This Message Available for reuse <--- */
#define MSG__IOTEST_PSID_NOT_SUPPORTED      16202  /* ---> PSID not supported on this product <--- */
#define MSG__IOTEST_NO_WHOLE_SERPENT        16203  /* No Complete Serpent Used in this Zone BypassTesting */
#define MSG__IOTEST_AUTH_MAINTSYMK1         16204  /* ---> Authority is MaintSymK - attempt 1 <---*/
#define MSG__IOTEST_AUTH_MAINTSYMK2         16205  /* ---> Authority is MaintSymK - attempt 2 <---*/
#define MSG__IOTEST_AUTH_PSID               16206  /* ---> Authority is PSID <---*/
#define MSG__ISSUE_PRENUKE_DL               16207  /* ---> Download Bridge code prior to Nuke Firmware Command <---*/
#define MSG__INVALID_NUKE_PW                16208  /* ---> Nuke Firmware password incorrect <---*/
#define MSG__IOTEST_RANDOM_METHOD_FAILED    16209  /* ---> Random Method Failed <---*/
#define MSG__IOTEST_RANDOM_METHOD_PASSED    16210  /* ---> Random Method Passed <---*/
#define MSG__IOTEST_CAP_PER_DATA_FAILED     16211  /* ---> Capture persistent Data Failed <---*/
#define MSG__IOTEST_COMPARE_CHECK           16212  /* ---> Verification Completed. No Miscompare <---*/
#define MSG__NON_PG_PERFORMANCE_LIMITATION  16213  /* ---> IO performance is limited - Recommend using hw pattern generator/checker */
#define MSG__IOTEST_REMOVE_ACE              16214  /* ---> Remove MSID Access Control Element - ISE drives only */
#define MSG__IOTEST_ADD_ACE                 16215  /* ---> Add PSID Access Control Element - ISE drives only */
#define MSG__IOTEST_ADD_ACE_FAILED_NZSC     16216  /* ---> AddACE method failed - non zero status code <---*/
#define MSG__IOTEST_REMOVE_ACE_FAILED_NZSC  16217  /* ---> RemoveACE method failed - non zero status code <---*/
#define MSG__IOTEST_ADD_ACE_FAILED_ZSR      16218  /* ---> AddACE method failed - zero status returned<---*/
#define MSG__IOTEST_REMOVE_ACE_FAILED_ZSR   16219  /* ---> RemoveACE method failed - zero status returned<---*/
#define MSG__IOTEST_EMPTY_LIST_MISSING      16220  /* ---> Empty list not available <---*/
#define MSG__IOTEST_ISE_TEST_PASSED         16221  /* ---> SED ISE test passed <---*/
#define MSG__IOTEST_ISE_INVALID_FRAME       16222  /* ---> SED In Frame corrupted - data invalid <---*/
#define MSG__IOTEST_TPER_PACKET_PARSED      16223  /* ---> Tper packet parsed <---*/
#define MSG__IOTEST_LOCKING_PACKET_PARSED   16224  /* ---> Locking packet parsed <---*/
#define MSG__IOTEST_GEOMETRY_PACKET_PARSED  16225  /* ---> Geometry packet parsed<---*/
#define MSG__IOTEST_LOG_PORT_PACKET_PARSED  16226  /* ---> Logical Port packet parsed<---*/
#define MSG__IOTEST_ISE_PACKET_PARSED       16227  /* ---> ISE feature packet parsed <---*/
#define MSG__IOTEST_ENT_SCC_PACKET_PARSED   16228  /* ---> Enterprise SCC packet parsed <---*/
#define MSG__IOTEST_NO_PACKET_PARSED        16229  /* ---> All available packets parsed - leaving parsing loop <---*/
#define MSG__IOTEST_OPAL_SCC_PACKET_PARSED  16230  /* ---> Opal SCC packet parsed <---*/
#define MSG__IOTEST_OPAL_SU_PACKET_PARSED   16231  /* ---> Opal single user packet parsed <---*/
#define MSG__IOTEST_OPAL_202_PACKET_PARSED  16232  /* ---> Opal Additional DataStores Feature Descriptor packet parsed <---*/
#define MSG__IOTEST_OPAL_203_PACKET_PARSED  16233  /* ---> Opal SSC Feature Descriptor packet parsed  <---*/
#define MSG__IOTEST_EMPTY_LIST              16234  /* ---> Empty List <--- */
#define MSG__IOTEST_ABORTED_CMD_RETRY_EXCEEDED       16235  /* ---> Aborted Command Retry Exceeded <--- */
#define MSG__IOTEST_NOT_A_SECURED_DRIVE     16236  /* ---> Not a Secured Drive - drive not locked  <---*/
#define MSG__IOTEST_SDD_PACKET_PARSED       16237  /* ---> SDD Feature Descriptor C003 packet parsed  <---*/
#define MSG__IOTEST_OPAL_SSC_V2_PACKET_PARSED  16238  /* ---> Opal SSC Feature Descriptor V2 packet parsed  <---*/
#define MSG__IOTEST_NO_SMART_DATA_ON_DISK   16239  /* FW There is No SMART data available on the Disk */
#define MSG__IOTEST_PRE_RESET_IDENTIFY_FAILED  16240  /* ---> Initial Identify failed  <---*/
#define MSG__IOTEST_POST_RESET_IDENTIFY_FAILED  16241  /* ---> Post Reset Identify failed  <---*/
#define MSG__IOTEST_DISCOVERY_FAILED        16242     /* ---> Discovery not supported on this drive  <---*/
#define MSG__IOTEST_ACTIVATING_LOCKINGSP    16243     /* ---> Activating the LockingSP  <---*/
#define MSG__IOTEST_ADDING_MAKERS_TO_ACT    16244     /* ---> Adding Makers ACE to activation ACL  <---*/
#define MSG__IOTEST_REMOVE_SID_ACE_FROM_ACT 16245     /* ---> Removing SID ACE from activation ACL <---*/
#define MSG__IOTEST_REMOVE_ACE_TEST_PASSED  16246     /* ---> Remove ACE method passed <---*/
#define MSG__IOTEST_FIELD_NOT_ACCESSIBLE    16247     /* ---> Port or band not accessable <--- */
#define MSG__IOTEST_STRING_NOT_FOUND        16248     /* ---> string not found in returned frame <--- */
#define MSG__IOTEST_LOCKING_ACTIVE          16249     /* ---> A Locking session is already active <--- */
#define MSG__IOTEST_ADMIN_ACTIVE            16250     /* ---> A Admin session is already active <--- */
#define MSG__IOTEST_LOCKING_INACTIVE        16251     /* ---> No Locking session is active <--- */
#define MSG__IOTEST_ADMIN_INACTIVE          16252     /* ---> No Admin session is active <--- */
#define MSG__IOTEST_INCORRECT_SOM_STATE     16253     /* ---> Drive SOM state is incorrect <--- */
#define MSG__IOTEST_INCORRECT_SECURITY_TYPE     16254     /* ---> Drive type is incorrect <--- */
#define MSG__IOTEST_INCORRECT_SECURITY_STATE     16255     /* ---> Drive security state is incorrect <--- */
#define MSG__IOTEST_FIPS_PN_INCORRECT       16256     /* ---> Unsupported FIPS Part Number <--- */
#define MSG__IOTEST_DITS_COMMAND_FAILED     16257     /* ---> DITS ENABLE_FIPS command failed <--- */
#define MSG__IOTEST_INVALID_FEAT_COMB       16258     /* ---> Invalid Feature configuration <--- */
#define MSG__IOTEST_ACTIVATE_SED            16259     /* ---> Activating SED option <--- */
#define MSG__IOTEST_ACTIVATE_SDD            16260     /* ---> Activating SDD option <--- */
#define MSG__IOTEST_ACTIVATE_ISE            16261     /* ---> Activating ISE option <--- */
#define MSG__IOTEST_ACTIVATE_FIPS           16262     /* ---> Activating FIPS option <--- */
#define MSG__IOTEST_ACTIVATE_SED_FAILED     16263     /* ---> Activate SED option FAILED <--- */
#define MSG__IOTEST_ACTIVATE_SDD_FAILED     16264     /* ---> Activate SDD option FAILED <--- */
#define MSG__IOTEST_ACTIVATE_ISE_FAILED     16265     /* ---> Activate ISE option FAILED <--- */
#define MSG__IOTEST_ACTIVATE_FIPS_FAILED    16266     /* ---> Activate FIPS option FAILED <--- */
#define MSG__IOTEST_SETTING_MASTER_PW       16267     /* ---> Setting ATA Master Password <--- */
#define MSG__IOTEST_SETTING_MASTER_PW_FAIL  16268     /* ---> Setting ATA Master Password FAILED <--- */
#define MSG__IOTEST_ACT_PACKET_PARSED       16269     /* ---> Activation Feature Descriptor C004 parsed <--- */
#define MSG__IOTEST_ACT_CURRENT_CONFIG_SDD  16270     /* ---> Current Activated Config is SDD <--- */
#define MSG__IOTEST_ACT_CURRENT_CONFIG_SED  16271     /* ---> Current Activated Config is SED <--- */
#define MSG__IOTEST_ACT_CURRENT_CONFIG_ISE  16272     /* ---> Current Activated Config is ISE <--- */
#define MSG__IOTEST_ACT_CURRENT_CONFIG_FIPS 16273     /* ---> Current Activated Config is FIPS <--- */
#define MSG__IOTEST_SCAN_COMPLETED          16274     /* ---> Scan Completed <--- */
#define MSG__IOTEST_SECURITY_STATE_UNINIT   16275     /* ---> Drive doesn't support Discovery - no SSC established <--- */
#define MSG__IOTEST_INCORRECT_SYMK_KEY      16276     /* ---> MakerSymK Key detected does not match requested <--- */
#define MSG__IOTEST_TCG_VER_MISMATCH        16277     /* ---> TCG version detected does not match requested <--- */
#define MSG__IOTEST_FW_PLAT_MISMATCH        16278     /* ---> Firmware platform detected does not match requested <--- */
#define MSG__IOTEST_CORESPEC_OR_OPALSUP_MISMATCH 16279     /* ---> Core spec or Opal support detected does not match requested <--- */
#define MSG__IOTEST_DR_SEC_TYPE_MISMATCH    16280     /* ---> Drive security type detected does not match requested <--- */
#define MSG__IOTEST_FWPLAT_MISMATCH         16281     /* ---> Drive Firmware plaform detected does not match requested <--- */
#define MSG__IOTEST_ATA_SECURITY_SUPPORTED  16282     /* ---> Drive Firmware supports ATA security  <--- */
#define MSG__IOTEST_DRIVE_IN_FAILED_STATE   16283     /* ---> Drive is in FAILED state  <--- */
#define MSG__IOTEST_LOCKING_NOT_SUPPORTED   16284     /* ---> Locking not supported on this drive  <--- */
#define MSG__IOTEST_DRIVE_IN_SETUP_STATE    16285     /* ---> Drive is in SETUP state  <--- */
#define MSG__IOTEST_DRIVE_IN_USE_STATE      16286     /* ---> Drive is in USE state  <--- */
#define MSG__IOTEST_DRIVE_IN_DIAG_STATE     16287     /* ---> Drive is in DIAG state  <--- */
#define MSG__IOTEST_DRIVE_IN_MFG_STATE      16288     /* ---> Drive is in MFG state  <--- */
#define MSG__IOTEST_DRIVE_IS_TCG2           16289     /* ---> Drive is TCG2   <--- */
#define MSG__IOTEST_DRIVE_IS_PRE_TCG2       16290     /* ---> Drive is Pre TCG2   <--- */
#define MSG__IOTEST_STANDARD_TCG_IN_USE     16291     /* ---> Standard TCG command mapping in use   <--- */
#define MSG__IOTEST_VU_TCG_IN_USE           16292     /* ---> Seagate Unique TCG command mapping in use   <--- */
#define MSG__IOTEST_ABORTED_COMMAND_RETRY   16293     /* ---> Aborted Cmd Retry  <--- */
#define MSG__IOTEST_BRIDGE_CODE_ONLY        16294     /* ---> COMMAND TIMEOUT likely caused by bridge code on drive  <--- */
#define MSG__IOTEST_CURRENT_CONFIG_SDD      16295     /* ---> Current Config is SDD <--- */
#define MSG__IOTEST_CURRENT_CONFIG_SED      16296     /* ---> Current Config is SED <--- */
#define MSG__IOTEST_CURRENT_CONFIG_ISE      16297     /* ---> Current Config is ISE <--- */
#define MSG__IOTEST_CURRENT_CONFIG_FIPS     16298     /* ---> Current Config is FIPS <--- */
#define MSG__IOTEST_ACT_CFG_NOT_SUPPORTED   16299     /* ---> The desired Config cannot be activated on this drive <--- */
#define MSG__IOTEST_ACT_NOT_SUPPORTED       16300     /* ---> Activation not supported on this drive <--- */
#define MSG__IOTEST_DIAG_PORT_UNLOCKED      16301     /* ---> Diag port unlocked <--- */
#define MSG__IOTEST_UDS_PORT_UNLOCKED       16302     /* ---> UDS port unlocked <--- */
#define MSG__IOTEST_CSFWDL_PORT_UNLOCKED    16303     /* ---> Cross segment firmware download port unlocked <--- */
#define MSG__IOTEST_FWDL_PORT_LOCKED        16304     /* ---> FIrmware download port locked <--- */
#define MSG__IOTEST_xSID_VALID_INVALID      16305     /* ---> xSID value is invalid <--- */
#define MSG__IOTEST_PROT_0_FEATURE_MATCHED  16306     /* ---> The Protocol 0 feature was detected  <--- */
#define MSG__IOTEST_TCG_FEATURE_SET_SUPP    16307     /* ---> The Trusted Computing Feature set is supported  <--- */
#define MSG__IOTEST_DRIVE_IS_TCG3           16308     /* ---> Drive is TCG3   <--- */
#define MSG__IOTEST_AUTH_ACTIVATIONSYMK1    16309     /* ---> Authority is ActivationSymK - attempt 1 <---*/
#define MSG__IOTEST_AUTH_ACTIVATIONSYMK2    16310     /* ---> Authority is ActivationSymK - attempt 2 <---*/
#define MSG__IOTEST_SET_ACTIVATIONSYMK_AES_KEY 16311  /* ---> Writing unique ActivationSymK credential <---*/
#define MSG__IOTEST_TLS_PACKET_PARSED       16312     /* ---> TLS packet parsed<---*/
#define MSG__IOTEST_ZERO_LENGTH_ACL         16313  /* ---> Access control list length equals zero <---*/
#define MSG__IOTEST_ACL_LENGTH_MISMATCH     16314  /* ---> Expected vs. received ACL length mismatch <---*/
#define MSG__IOTEST_INVALID_ACE_IN_ACL      16315  /* ---> Received ACL vs. expected ACL mismatch <---*/
#define MSG__IOTEST_NUM_OF_BANDS_0          16316     /* ---> Number of bands detected is 0 <---*/
#define MSG__IOTEST_NUM_OF_BANDS_INCORRECT  16317     /* ---> Number of bands detected does not match customer option specified number of bands <---*/
#define MSG__IOTEST_FRB_PORT_UNLOCKED       16318     /* ---> Firmware Rollback port unlocked <--- */
#define MSG__IOTEST_RESERVED_END            31999  /*  */
/****************************************************************************************************************************

   #               #    ##        ######      #      #   ###   #      #     ######
    #             #    #  #       #      #    # #    #    #    # #    #    #      #
     #     #     #    #    #      #      #    #  #   #    #    #  #   #   #
      #   # #   #    ########     ######      #   #  #    #    #   #  #   #     ###
       # #   # #    #        #    #     #     #    # #    #    #    # #   #       #
        #     #    #          #   #      #    #     ##    #    #     ##    #      #
        #     #   #            #  #       #   #      #   ###   #      #      ####

 Deleting or modifying any established entry or its attributes in this file could result in serious process consequences.
 E.g. previously released firmware that depends on the changed or deleted entry will function incorrectly or could stop
 functioning altogether.

 If a change is needed in an established entry, a new entry must be made to incorporate that change.
 This MUST be observed until a permanent solution is in place.

*****************************************************************************************************************************/



// *******************  SATATEST DBLog Message definitions  *************************
//      Message define               MESSAGE_CODE  ***  Message ***
#define MSG__RESIDENT_GLIST                 32000  /* Resident G-List */
#define MSG__NON_RESIDENT_GLIST             32001  /* Non-Resident G-List*/
#define MSG__SCSI_TIMER                     32002  /* Internal SCSI Timer Used */
#define MSG__SERVO_TIMER                    32003  /* SERVO Processor Reported */
#define MSG__ADAP_SPEC_EXCEEDED             32004  /* Adaptive Gain Spec Exceeded */
#define MSG__POS_DELTA_EXCEEDED             32005  /* +Delta Spec Exceeded */
#define MSG__NEG_DELTA_EXCEEDED             32006  /* -Delta Spec Exceeded */
#define MSG__ZONE_ADJUSTED                  32007  /* Ending Zone Value Adjusted */
#define MSG__NO_ZONE_UNION                  32008  /* Zone Does not have a Union for all heads */
#define MSG__NOT_FOUND_IN_PARAM_TBL         32009  /* Parameter not found in parm_tbl or invalid */
#define MSG__CONFLICTING_PARAMETERS         32010  /* An Old And New Parameter Sent with Non Default Value */
#define MSG__PARAMETER_RANGE_ERROR          32011  /* Parameter is not in allowed range */
#define MSG__REQUIRED_PARAMETER_MISSING     32012  /* A required parameter is missing */
#define MSG__MULTIPLE_PARAMETER_CONFLICT    32013  /* Multiple parameters are conflicting */
#define MSG__PARAMETER_NOT_VALID_FOR_TEST   32014  /* Parameter is not valid for this test */
#define MSG__NOT_BUSY_PARTIAL_DATA_TRANSFER 32015  /* Drive is not BUSY-however not all the data was transferred */
#define MSG__SECTOR_COUNT_TOO_LARGE         32016  /* SectorCount is too large for this drive write-4K sector */
#define MSG__NO_MINI_MINI_ZONE_SUPPORT      32017  /* LBA order suggests drive uses mini serpents. Use Physical Test instead of Logical.*/
#define MSG__HEAD_SUPPORT_EXCEEDED          32018  /* This Drive Requires support for more Heads. Notify TSE for Support.*/
#define MSG__RAP_REVISION_NOT_SUPPORTED     32019  /* This Drives RAP is Not yet supported in Initiator code. Notify TSE for Support.*/
#define MSG__USR_ZN_CNT_SUPPORT_EXCEEDED    32020  /* This Drive Requires support for more User Zones. Notify TSE for Support.*/
#define MSG__SYS_ZN_CNT_SUPPORT_EXCEEDED    32021  /* This Drive Requires support for more System Zones. Notify TSE for Support.*/
#define MSG__ZAP_GBH_VECTOR_NOT_ALLOCATED   32022  /* Gain by harmonic requires ZapGbh memory to be allocated. */
#define MSG__NTZ_REQD_PARMS_MISSING         32023  /* OnRampLength or OffRampLength cannot be zero. */
#define MSG__NTZ_HD_RG_OVERRIDE             32024  /* HdRg forced to single head due to a CylRg being specified in test params. */
#define MSG__GIVE_TO_INITIATOR_PROGRAMMER   32025  /* Potentialy Unsupported Drive Configuration Give failure to Initiator Programmer. */
#define MSG__SATATEST_RESERVED_END          47999  /* Place your message here */

/****************************************************************************************************************************

   #               #    ##        ######      #      #   ###   #      #     ######
    #             #    #  #       #      #    # #    #    #    # #    #    #      #
     #     #     #    #    #      #      #    #  #   #    #    #  #   #   #
      #   # #   #    ########     ######      #   #  #    #    #   #  #   #     ###
       # #   # #    #        #    #     #     #    # #    #    #    # #   #       #
        #     #    #          #   #      #    #     ##    #    #     ##    #      #
        #     #   #            #  #       #   #      #   ###   #      #      ####

 Deleting or modifying any established entry or its attributes in this file could result in serious process consequences.
 E.g. previously released firmware that depends on the changed or deleted entry will function incorrectly or could stop
 functioning altogether.

 If a change is needed in an established entry, a new entry must be made to incorporate that change.
 This MUST be observed until a permanent solution is in place.

*****************************************************************************************************************************/


// *******************  ISETEST DBLog Message definitions  **************************
//      Message define               MESSAGE_CODE  ***  Message ***
#define MSG__ISETEST_RESERVED_START         48000  /* Place your message here */
#define MSG__ISETEST_RESERVED_END           63999  /* Place your message here */

/****************************************************************************************************************************

   #               #    ##        ######      #      #   ###   #      #     ######
    #             #    #  #       #      #    # #    #    #    # #    #    #      #
     #     #     #    #    #      #      #    #  #   #    #    #  #   #   #
      #   # #   #    ########     ######      #   #  #    #    #   #  #   #     ###
       # #   # #    #        #    #     #     #    # #    #    #    # #   #       #
        #     #    #          #   #      #    #     ##    #    #     ##    #      #
        #     #   #            #  #       #   #      #   ###   #      #      ####

 Deleting or modifying any established entry or its attributes in this file could result in serious process consequences.
 E.g. previously released firmware that depends on the changed or deleted entry will function incorrectly or could stop
 functioning altogether.

 If a change is needed in an established entry, a new entry must be made to incorporate that change.
 This MUST be observed until a permanent solution is in place.

*****************************************************************************************************************************/


// *******************  GENERIC DBLog Message definitions  **************************
//      Message define               MESSAGE_CODE  ***  Message ***
#define MSG__GENERIC_RESERVED_START         64000  /* Place holder for start of generic message section */

#define MSG__NOT_FOUND                      65535  /* Error: !!! Message decode NOT found in messages.h file !!! */

/****************************************************************************************************************************

   #               #    ##        ######      #      #   ###   #      #     ######
    #             #    #  #       #      #    # #    #    #    # #    #    #      #
     #     #     #    #    #      #      #    #  #   #    #    #  #   #   #
      #   # #   #    ########     ######      #   #  #    #    #   #  #   #     ###
       # #   # #    #        #    #     #     #    # #    #    #    # #   #       #
        #     #    #          #   #      #    #     ##    #    #     ##    #      #
        #     #   #            #  #       #   #      #   ###   #      #      ####

 Deleting or modifying any established entry or its attributes in this file could result in serious process consequences.
 E.g. previously released firmware that depends on the changed or deleted entry will function incorrectly or could stop
 functioning altogether.

 If a change is needed in an established entry, a new entry must be made to incorporate that change.
 This MUST be observed until a permanent solution is in place.

*****************************************************************************************************************************/


