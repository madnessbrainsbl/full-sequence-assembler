// Do NOT modify or remove this copyright and confidentiality notice!
//
// Copyright (c) 2001 - $Date: 2016/11/24 $ Seagate Technology, LLC.
//
// The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
// Portions are also trade secret. Any use, duplication, derivation, distribution
// or disclosure of this code, for any reason, not expressly authorized is
// prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
//

/*******************************************************************************
*                 $File: //depot/TSE/Shared/source/codes/codes.h $
*                 $Revision: #391 $
*                 $Change: 1155102 $
*                 $Author: thakool.narinnork $
*                 $DateTime: 2016/11/24 00:02:56 $
********************************************************************************/

/****************************************************************************************************************************

   #               #    ##        ######      #      #   ###   #      #     ######
    #             #    #  #       #      #    # #    #    #    # #    #    #      #
     #     #     #    #    #      #      #    #  #   #    #    #  #   #   #
      #   # #   #    ########     ######      #   #  #    #    #   #  #   #     ###
       # #   # #    #        #    #     #     #    # #    #    #    # #   #       #
        #     #    #          #   #      #    #     ##    #    #     ##    #      #
        #     #   #            #  #       #   #      #   ###   #      #      ####

 Deleting any entry from this file or modifying any attributes of an established entry in this file could result in
 serious process consequences.  E.g. previously released firmware that depends on the changed or deleted entry will
 function incorrectly or could stop functioning altogether.

 If a change is needed in an established entry, a new entry must be made to incorporate that change.
 This MUST be observed until a permanent solution is in place.

 All new entries must have comment section lengths of 40 chars. or less in order to fit into the SCSS system.
 The comment section should be copied verbatim to the corresponding SCSS definition to avoid confusion.

*****************************************************************************************************************************/

/*******************************************************************************
*
*     description: Error Codes returned from the Firmware; All code numbers used in this file MUST be assigned by the SCSS data base.
*     SCSS link: http://sgpscssapp.sing.seagate.com/WebSCSS/index.do
*
*     Do NOT indent any #defines, since this will break DEX parsing.
*
*******************************************************************************/

// -----------------------------------------------------------------------------
// ******************** Public Macro / Constant Section ************************
// -----------------------------------------------------------------------------
#define TEST_PASSED                           0   /* Test Passed */                                            // SF2/3 various          // Defined as "Drive Passed" in SCSS
#define SUCCEEDED                             0   /* No error occurred. */
#define SCSI_4031_01_03___10              10001   /* Svo Flt-01/03XX10 Write Fault Servo */                    //
#define SCSI_4031_01_03                   10002   /* Wt Flt-01/03XX Rec */                                     //
#define SCSI_4031_03_03                   10003   /* Svo Flt-03/03XX10 Unrec Wt Flt Servo */                   //
#define SCSI_4031_03_03___10              10004   /* Wt Flt-03/03XX Unrec */                                   //
#define SCSI_4031_04_03                   10005   /* Wt Flt-04/03XX HW */                                      //
#define SCSI_4031_01_09                   10006   /* Svo PES-01/09XX Rec Trk Following Err */                  //
#define SCSI_4031_04_09                   10007   /* Svo PES-04/09XX Unrec Trk Fol'wing Err */                 // SF2/3 reporting
#define SCSI_4031_01_15                   10008   /* Svo Seek-01/15XX Rec Seek Error */                        //
#define SCSI_4031_03_15                   10009   /* Svo Seek-03/15XX Unrec Seek Error */                      //
#define SCSI_4031_04_15                   10010   /* Svo Seek-04/15XX HW Seek Error */                         //
#define SCSI_4031_04_02                   10011   /* Svo Seek-04/02XX No Seek Complete */                      //
#define SCSI_4031____1C                   10012   /* Drv CPF-XX/1CXX Log Recovery Err */                       //
#define SCSI_4031_04_19                   10013   /* Drv H/W Err-04/19XX Defect List Error */                  //
#define SCSI_4031____31_91_0B             10014   /* Proc M.E.-XX/31910B Inval WWN in ETF Log */               //
#define SCSI_4031_03_31                   10015   /* Proc M.E.-03/31XX Format Corrupt */                       //
#define SCSI_4031____3f_91                10016   /* Proc Operator-XX/3F91 WWN Mismatch */                     //
#define SCSI_4031____32                   10017   /* Wt Fmt-XX/32XX No Spares Available */                     //
#define SCSI_4031_02_04_00                10018   /* Svo Startup-02/0400 Drive Not Ready */                    //
#define SCSI_4031_02_04_01                10019   /* Svo Startup-02/0401 Not Rdy Becoming Rdy */               //
#define SCSI_4031_02_04_02                10020   /* Svo Startup-02/0402 Not Rdy Init Cmd Req */               //
#define SCSI_4031_01_40_01                10021   /* Svo Startup-01/4001 Spin-up Retry No Jog */               //
#define SCSI_4031_01_40_02                10022   /* Drv Startup-01/4002 Spin-up Retries: Jog */               //
#define SCSI_4031_05_24                   10023   /* Proc M.E.-05/24XX Invalid Field in CDB */                 //
#define SCSI_4031_04_42                   10024   /* Drv PCBA-04/42XX Pwr-on Selftest Fail */                  //
#define SCSI_4031_04_44                   10025   /* Drv PCBA-04/44XX Int Target Failure */                    //
#define SCSI_4031_04_80_80                10026   /* Rd H/W Err-04/8080 FIFO Error on Read */                  //
#define SCSI_4031_04_80_81                10027   /* Wt H/W Err-04/8081 FIFO Error on Write */                 //
#define SCSI_4031_09_80                   10028   /* Drv F/W-09/80XX Firmware Error */                         //
#define SCSI_4031_0B_08_00                10029   /* Drv Iface-0B/0800 Log. Unit Comm Fail */                  //
#define SCSI_4031_0B_08_01                10030   /* Drv Timeout-0B/0801 Log. Unit Comm T-O */                 //
#define SCSI_4031_0B_08_02                10031   /* Drv Iface-0B/0802 L-Unit Comm Parity Err */               //
#define SCSI_4031_0B_47                   10032   /* Drv Iface-0B/47XX SCSI Parity Error */                    //
#define SCSI_4031_01_16                   10033   /* Rd Rec Err-01/16XX Data Sync Error */                     //
#define SCSI_4031_03_16                   10034   /* Rd Unrec Err-03/16XX Unrec Data Sync Err */               // SF2/3 reporting
#define SCSI_4031_01_17_02                10035   /* Rd Rec Err-01/1702 Rec Rd Err w/+Offsets */               //
#define SCSI_4031_01_17_03                10036   /* Rd Rec Err-01/1703 Rec Rd Err w/-Offsets */               //
#define SCSI_4031_01_17                   10037   /* Rd Rec Err-01/17XX Rec Rd Error */                        //
#define SCSI_4031_01_18                   10038   /* Rd Rec Err-01/18XX Rec Rd Error w/ECC */                  //
#define SCSI_4031_03_11_01                10039   /* Rd Unrec Err-03/11XX Unrec Read Error */                  // SF2/3 reporting  IF2/3 T551
#define SCSI_4031_03_11_02                10040   /* Wt Flt-01/11XX Rec */                                     //
#define SCSI_4031_03_11_03                10041   /* Drv H/W Err-04/0100 No Index/Sec Signal */                //
#define SCSI_4031_06_5b_00                10042   /* Drv SMART-06/5B00 Log Thrshld Exceeded */                 //
#define SCSI_4031_XX_1D_00                10043   /* Drv Iface-XX/1D00 Data Miscompare-Verify */               //
#define SCSI_4031_05_21_XX                10044   /* Proc M.E.-05/21XX LBA Out of Range */                     // IF2/3 T509, T1509, T539
#define SCSI_4031_04_40_XX                10045   /* Drv PCBA-04/40XX DRAM parity Error */                     //
#define SCSI_4031_01_5D_XX                10046   /* Drv SMART-01/5D Fail Pred Threshold Exc */                //
#define SCSI_4031_05_20_XX                10047   /* Proc M.E.-05/20XX Invalid Command */                      //
#define SCSI_4031_05_26_99                10048   /* Proc TSD-05/2699 Invalid Field - F/W Tag */               //
#define EXCEEDED_MAX_TOTAL_FLAWS          10049   /* Wt/Rd Def's-# of Flaws Exc's Total Flaws */               // SF3  T117
#define CODE_1001                         10050   /* Svo Def's-=> 2 Def on a Trk */                            //
#define CODE_1003                         10051   /* Svo Def's-=>2 Def on a Trk - Diff S&C */                  //
#define CODE_1002                         10052   /* Svo Def's-=>2 Def on a Trk-Scratch Fill */                //
#define CODE_1406                         10053   /* Svo Rec Err-01,01,00 No Index Sector */                   // SF3 T45
#define CODE_1407                         10054   /* Svo Seek-01,02,00 No Seek Complete */                     //
#define CODE_1422                         10055   /* Wt Flt-01,03,00 */                                        //
#define CODE_1409                         10056   /* Svo PES-01,09,00 Track Following */                       //
#define CODE_1411                         10057   /* Svo Seek-01,15,01 Mech. pos. error */                     //
#define CODE_1408                         10058   /* Svo Seek-03,02,00 No Seek Complete */                     //
#define CODE_1410                         10059   /* Svo PES-03,09,00 Track Following */                       //
#define CODE_1412                         10060   /* Svo Seek-03,15,01 Mech. pos. error */                     //
#define DST_02                            10061   /* Drv DST-Aborted by Host Device */                         // IF2/3 T600
#define DST_01                            10062   /* Drv DST-Aborted by Operator Abort Cmd */                  // IF2/3 T600
#define ACM_COUNTER_INIT_LT_ZERO          10063   /* Svo ZAP-ACM_COUNTER_INIT < zero */                        //
#define APM_WRITE_FAILED                  10064   /* Drv F/W-Adaptive Parameters Write Failed */               //
#define T151_ADDRESS_FAULT                10065   /* Svo Flt-Address */                                        // SF2/3 reporting
#define ADJACENT_SERVO_FLAWS              10066   /* Svo Def's-Adjacent Servo Flaws */                         //
#define SMT_ALT_TONE_BUFR_PE              10067   /* Drv SMART-Alt Tone Buffer Parity Error */                 //
#define SMT_ALT_TONE_IX_TO_01             10068   /* Drv SMART-Alt Tone IX to 01 */                            // IF2/3 T538, 638
#define SMT_ALT_TONE_IX_TO_02             10069   /* Drv SMART-Alt Tone IX to 02 */                            //
#define SMT_ALT_TONE_UNKNOWN_FAULT        10070   /* Drv SMART-Alt Tone Unknown Fault */                       //
#define SMT_ALT_TONE_UNKNOWN_HALT         10071   /* Drv SMART-Alt Tone Unknown Halt */                        //
#define NO_APM_ON_START                   10072   /* Drv F/W-APM Data Bad */                                   //
#define CODE_1401                         10073   /* Svo Def's-ASFT Full during Scratch Fill */                //
#define ASPERITY_SCRATCH                  10074   /* Wt/Rd T.A.s-Asperity Scratch */                           // SF2/3 T117
#define CODE_1415                         10075   /* Wt Flt-Attention */                                       //
#define CODE_1420                         10076   /* Wt Flt-Attention + No Trk Center & WG */                  //
#define CODE_1416                         10077   /* Wt Flt-Attention + Rd & Wt Gate */                        //
#define CODE_1417                         10078   /* Wt Flt-Attention + Unsafe & WG */                         //
#define CODE_1418                         10079   /* Wt Flt-Attention + Voltage & WG */                        //
#define CODE_2600                         10080   /* Wt/Rd Flt-ATTN + DC erase */                              //
#define CODE_2601                         10081   /* Wt/Rd Flt-ATTN + RWLSI test mode */                       //
#define CODE_2602                         10082   /* Wt/Rd Flt-ATTN + TMS bit set */                           //
#define BAD_AVG_FWD_HEAD_SWITCH           10083   /* Svo Sk Time-Avg Forward Hd Switch Exc */                  // IF2/3 T549
#define BAD_AVG_HD0_HD0_SEEK_TIME         10084   /* Svo Sk Time-Avg Hd 0 to Hd 0 Limit Exc */                 // IF2/3 T549
#define AVG_OFFSET_TIME_FAILED            10085   /* Svo Sk Time-Avg Hd Offset Limit Exc */                    //
#define BAD_AVG_HEAD_SWITCH               10086   /* Svo Sk Time-Avg Head Switch Limit Exc */                  // IF2/3 T549
#define BAD_AVG_SEEK_TIME                 10087   /* Svo Sk Time-Avg Limit Exceeded */                         // SF2/3 T30,32; IF2/3 T549
#define BAD_AVG_MAXHD_MAXHD_SEEK_TIME     10088   /* Svo Sk Time-Avg Max Hd-Max Hd Limit Exc */                // IF2/3 T549
#define BAD_AVG_REV_HEAD_SWITCH           10089   /* Svo Sk Time-Avg Rev Hd Switch Limit Exc */                // IF2/3 T549
#define BBT_FULL                          10091   /* Wt/Rd Def's-Bad Block Table Full */                       // IF2/3 flawfnt
#define BAD_DL_TAGS_2                     10092   /* Proc M.E.-Bad D/L Tags (APM-1) */                         // SF2/3 T8; IF2/3 T8
#define BAD_DL_TAGS_3                     10093   /* Proc M.E.-Bad D/L Tags (APM-2) */                         // SF2/3 T8
#define BAD_DL_TAGS_4                     10094   /* Proc M.E.-Bad D/L Tags (APM-3) */                         // SF2/3 T8
#define BAD_DL_TAGS_1                     10095   /* Proc M.E.-Bad D/L Tags (XOR) */                           // SF3 T8
#define BAD_DELTA_OFF_MARGIN              10096   /* Wt/Rd Cal-Bad Delta Offset Margin */                      //
#define BAD_LATCH                         10097   /* Drv Latch-Bad Drive Latch Setting */
#define BAD_FCC_TABLE                     10098   /* Svo Cal-Bad FCC Table */
#define BAD_FIRMWARE_REV                  10099   /* Proc M.E.-Bad Firmware Revision */
#define COMMAND_TIMED_OUT                 10100   /* Drv Timeout-Command */
#define REQ_ASSERT_TIMEOUT                10101   /* Drv Timeout-REQ Assert */
#define REQ_NEGATE_TIMEOUT                10102   /* Drv Timeout-REQ Negate */
#define UNEXPECTED_PHASE                  10103   /* Drv Timeout-Unexpected SCSI Phase */
#define SELECT_TIMEOUT                    10104   /* Drv Timeout-Select */
#define RESELECT_TIMEOUT                  10105   /* Drv Timeout-Reselect */
#define WTS_TIMEOUT                       10106   /* Drv Timeout-WTS */
#define UNEXPECTED_INTERRUPT              10107   /* Drv Iface-Unexpected Interrupt Occurred */
#define INITR_DETECTED_PE                 10108   /* Drv Iface-Initiator Detected Parity Err */
#define UNEXPECTED_BUSFREE                10109   /* Drv Iface-Unexpected Bus Free on SCSI */
#define BAD_ID                            10110   /* Drv Latch-Bad I.D. Stop Setting */
#define BAD_ID_LIMIT                      10111   /* Svo Pattern-Bad ID Limit Exceeded */                      // SF2/3 T163
#define BAD_LATCH_ID_DELTA                10112   /* Drv Latch-Bad ID Setting */
#define BAD_DBI_LOG                       10113   /* Drv DBI-Bad Log */                                        // SF2/3 T101, 107, 109, 134, 140, DBIlog, Sysfiles, Shared mk_rep
#define BAD_ETF_LOG                       10114   /* Drv CPF-Bad Log */                                        // SF2/3 sysfiles
#define BAD_MAJOR_REVISION                10115   /* Proc M.E.-Bad Major Revision */
#define BAD_MARGINS_LOG                   10116   /* Drv Misc-Bad Margins Log */
#define BAD_MINOR_REVISION                10117   /* Proc M.E.-Bad Minor Revision */
#define BAD_OD                            10118   /* Drv Latch-Bad O.D. Stop Setting */
#define BAD_OCLIM_OFFSET                  10119   /* Proc M.E.-Bad OCLIM Offset */
#define BAD_OFF_MARGIN                    10120   /* Wt/Rd Cal-Bad Offset Margin */
#define BAD_PDQ_MARGIN                    10121   /* Wt/Rd Cal-Bad PDQ Margin */
#define BAD_RDS_MARGIN                    10122   /* Wt/Rd Cal-Bad RDS Margin */
#define BAD_SN_FROM_GP                    10123   /* Proc Operator-Bad S/N from GetPut */
#define COMMAND_FAILED                    10124   /* Drv Misc-Bad SCSI Status */                               // Shared mk_rep
#define BAD_SERVO_RAM_READ                10125   /* Drv PCBA -Bad Servo RAM Read */                           // SF2/3 T10, 11, 136, 138, 139, 197
#define BAD_SERVO_RAM_REV                 10126   /* Proc M.E.-Bad Servo RAM Revision */
#define BAD_SERVO_ROM_REV                 10127   /* Proc M.E.-Bad Servo ROM Revision */
#define BAD_SPINDLE_SPEED                 10128   /* Svo Spindle-Bad Spindle Speed */
#define BAD_SP240_RESULT_FILE_ON_DRIVE    10129   /* Proc TSD-Bad SPT Result File on Drive */                  // SF2/3 T231
#define BAD_START_TIME                    10130   /* Svo Startup-Bad Start Time */                             // SF2/3 T1
#define BAD_STOP_TIME                     10131   /* Svo Spindle-Bad Stop Time */
#define WRONG_TEST                        10132   /* Proc M.E.-Bad Test # from Drive */                        // SF2 T215
#define BAD_VOLTAGE                       10133   /* Tester Pwr/Temp Ctrl-Bad Voltage Sensed */
#define BAD_WW_ADDRESS                    10134   /* Proc Operator-Bad Worldwide Address */
#define RV_SENSOR_RAILED                  10135   /* Svo RV-Baseline Too Big */
#define BDRAG_FAILED                      10136   /* Svo Cal-Bdrag Limit Exceeded */                           // SF2/3 T10, 136
#define FAILED_BODE_GAIN_MARGIN           10137   /* Svo Cal-Bode Gain Margin Failed */                        // SF2/3 T152
#define READ_ERROR_2                      10138   /* Drv PCBA-Buffer Checksum Read Error */                    // Shared mk_rep
#define T151_BFRPE                        10139   /* Drv PCBA-Buffer Parity Error */
#define UNABLE_TO_FMT_DBI_CYL             10140   /* Wt DBI-Can't Format DBI Cylinder */                       // SF2/3 DBIlog
#define ETF_CTRL_PARM_CS_FAILURE          10141   /* Drv F/W-CAP File Checksum Failure */
#define CHARACTERIZE_FLAW_FAILURE         10142   /* Svo Def's-Characterize Flaw Failure */                    // SF2/3 T109, 126
#define ETF_CHECKSUM_MISMATCH             10143   /* Drv CPF-Checksum Copy Mismatch */
#define ETF_CHECKSUM_FAILURE              10144   /* Drv CPF-Checksum Failure */                               // SF2/3 sysfiles, T37
#define DBI_CHECKSUM_FAILURE              10145   /* Drv DBI-Checksum Failure */
#define CHKSUM_MISCOMP_UNREC_ERROR        10146   /* Drv CPF-Checksum Miscompare w/Unrec Err */
#define CODE_5002                         10147   /* Tester Comm Mgr-Comm Error on Receive */
#define FAILED_DC_ERASE_CMD               10148   /* Wt Trk Erase-Command Failed */                            // SF2/3 T138, 139
#define COMPARE_TEST_FAILED               10150   /* Compare Test Failed */                                    // Shared mk_rep
#define NO_END_OF_LOG                     10151   /* Wt/Rd Def's-Couldn't Find Log Terminator */               // SF2/3 T117
#define SATURATION_FAILURE                10152   /* Wt/Rd Cal-CQM Values All Saturated */                     // SF2/3 T151
#define CPL_FAILURE                       10153   /* Wt/Rd Cal-Critical Parameter Lmt Failed */                // SF3 diagAPI, T176
#define CYL_NOT_IN_ZONE                   10154   /* Proc M.E.-Cylinder Not in Zone */
#define CTLR_DL_ERROR                     10155   /* Drv F/W-D/L Controller Error */                           // SF2/3 T8
#define SERVO_DL_ERROR                    10156   /* Drv F/W-D/L Servo Error */
#define DL_SPINDN_ERR                     10157   /* Drv F/W-D/L Spindown Error */
#define DATA_MISCOMPARE                   10158   /* Drv Iface-Data Miscompare */
#define DATA_MISCOMP_UNREC_ERROR          10159   /* Drv Iface-Data Miscompare w/Unrec. Err */
#define DP0_DP1_BAD                       10160   /* Drv Iface-Data parity 0 or 1 Bad */
#define DATA_XFR_ERROR                    10161   /* Drv Iface-Data Transfer Error Occurred */
#define CODE_1414                         10162   /* Wt Flt-DBI */
#define CODE_1419                         10163   /* Wt Flt-DBI Offtrack */
#define CODE_1421                         10164   /* Wt Flt-DBI Offtrack & Unsafe */
#define CODE_1423                         10165   /* Wt DBI-DBI Same Cyl. Format Unit Error */
#define DBI_SECTOR_RE_READ_FAILED         10166   /* Rd DBI-DBI Sector Re-read Failed */
#define ETF_DFLTS_TO_DRAM_FAILED          10167   /* Drv CPF-Defaults to DRAM Failed */
#define ZAP_DISABLE_CMD_FAILED            10168   /* Svo ZAP-Disable cmd failed */                             // SF2/3 T175
#define T151_DISC_TIMEOUT                 10169   /* Drv Timeout-Disc */                                       // SF2/3 reporting
#define DIVIDE_BY_ZERO_ERROR              10170   /* Proc TSD-Divide by 0 in Xfer Rate Test */                 // SF3 T178
#define DRAM_VERIFY_FAILED                10171   /* Drv PCBA -DRAM Verify Failed */                           // SF2/3 T102
#define ABORTED_BIN                       10172   /* Proc Operator-Drive Aborted */                            // Shared mk_rep
#define INCORRECT_SERVO_CODE              10173   /* Proc M.E.-Incorrect Servo Code */
#define FAILED_UBH_SETUP                  10174   /* Drv Iface-Drive Failed to Enable UBH */
#define MIN_RUN_TIME_ERROR                10175   /* Proc M.E.-Drive Finished Too Soon */
#define ETF_DRV_INFO_CS_FAILURE           10176   /* Drv CPF-Drive Info File Checksum Failure */
#define MAX_RUN_TIME_ERROR                10177   /* Drv Misc-Drive Ran Too Long */
#define CODE_6021                         10178   /* Proc Operator-Drv Removed While Testing */
#define DRIVE_TYPE_UNKNOWN                10179   /* Proc TSD-Drive Type Unknown */
#define DRIVE_VERIFY_FAILED               10180   /* Rd CPF-Drive Verify Failed */
#define DST_06                            10181   /* Svo Seek-DST Seek Segment Failed */
#define MJ_SLOPE_CHANGED                  10182   /* Rd Err Rate-E.R. Below Read ER Threshold */
#define DST_05                            10183   /* Drv DST-Electrical Segment Failed */
#define ZAP_ENABLE_CMD_FAILED             10184   /* Svo ZAP-Enable cmd failed */                              // SF2/3 T35, 175
#define SCSIERR_FILE_ERROR                10185   /* Proc M.E.-Error in SCSIERR.TXT */
#define MJ_ER_MIN_MARGIN                  10186   /* Wt/Rd Cal-Error Rate minimum margin */                    // SF2/3 T167
#define MJ_ER_WRITE_TRACK                 10187   /* Wt/Rd Cal-Error Rate write track */
#define CODE_2635                         10188   /* Wt CPF-Error Writing Servo Defect List */
#define BAD_SERVO_RAM_WRITE               10189   /* Drv PCBA-Error Writing Servo RAM */
#define T151_BAD_TRACK                    10190   /* Wt/Rd Def's-Error-Free Track Not Found */                 // SF2/3 T151, 211
#define EVENT_COUNT_TOO_SMALL             10191   /* Wt/Rd Err Rate-Event Count Too Small */
#define EXCITED_RV_DELTA_TOO_LOW          10192   /* Svo RV-Excited vs Baseline Delta Too Low */
#define NARROW_MODE                       10193   /* Drv Iface-Expecting 8-Bit Transfer Mode */
#define WIDE_MODE                         10194   /* Drv Iface-Expecting Wide Transfer Mode */
#define FAILED_IOPS                       10195   /* Drv Iface-Failed I/O Ops/Sec Limit */
#define FAILED_NC_VARIANCE_SPEC           10196   /* Wt/Rd Cal-Failed NC Variance Spec */                      // Shared mk_rep
#define FAILED_TIME_TO_READY              10197   /* Svo Startup-Failed Power on Ready Time */
#define FAILED_SAM_SCREEN                 10198   /* Svo Misc-Failed SAM Screen */
#define FAILED_SPIN_DOWN_TIME             10199   /* Svo Spindle-Failed Spin Down Time */
#define FAILED_SPIN_UP_TIME               10200   /* Svo Startup-Failed Spin Up Time */
#define CODE_1400                         10201   /* Svo Misc-Fails R/W Sanity Check */
#define BAD_FCC_INTERP                    10202   /* Svo Cal-FCC Table Did Not Converge */                     // SF2/3 T10
#define FCON_FAILED                       10203   /* Svo Cal-FCON Limit Exceeded */
#define FCON2_RAILED                      10204   /* Svo Cal-FCON2 Railed */
#define MJ_FINE_UJOG_FAILURE              10205   /* Wt/Rd Cal-Fine Microjog Failure */                        // SF2/3 T139
#define T151_FIR_CAL_ERR                  10206   /* Wt/Rd Cal-FIR Cal Error */                                // SF2/3 T151
#define SMT_FRW_FAULT                     10207   /* Drv SMART-Firmware Fault */
#define FIRST_SEEK_NOT_DONE               10208   /* Svo Seek-First Seek Failed */
#define FLAW_ALREADY_IN_LOG               10209   /* Wt/Rd Def's-Flaw Already in Defect Log */
#define FLAW_NOT_LOCATED                  10210   /* Wt/Rd Def's-Flaw Not Located */
#define FE_CONVERSION_ERROR               10211   /* Proc TSD-Float Error conversion error */
#define FE_DIVIDE_ZERO                    10212   /* Proc TSD-Float Error divide by zero */                    // SF2/3 T138, 151, 167, 191
#define FE_INT_OVERFLOW                   10213   /* Proc TSD-Float Error integer overflow */
#define FE_OVERFLOW                       10214   /* Proc TSD-Float Error overflow */                          // SF2/3 T102
#define FE_STACK_OVERFLOW                 10215   /* Proc TSD-Float Error stack overflow */
#define FE_STACK_UNDERFLOW                10216   /* Proc TSD-Float Error stack underflow */
#define FE_UNDEFINED_FLOAT                10217   /* Proc TSD-Float Error undefined float */
#define FE_UNDERFLOW                      10218   /* Proc TSD-Float Error underflow */
#define CODE_2636                         10219   /* Wt Fmt-Format Failed */
#define FORMAT_ETF_FAILED                 10220   /* Wt CPF-Format Failed */
#define FORMAT_FAILURE                    10221   /* Wt Fmt-Format Failure Couldn't Rec. */
#define SPT_FE_OE                         10222   /* Tester Comm Mgr-Framing or Overrun Error */
#define FREQ_TOO_LOW                      10223   /* Svo Pattern-Frequency Too Low */                          // SF2/3 fastservo
#define T151_FRW_FAULT                    10224   /* Svo Flt-FRW */
#define GIVE2MCT_PROGRAMMER               10225   /* Proc TSD-Deliver Unit to SPT Programmer */                // SF2/3 parameters, mr_model, T37, 172, 177, 178, 186
#define SERVO_FLAW_HEAD_CLAMPED           10226   /* Svo Def's-Head Clamped */                                 // SF2/3 T126
#define HEAD_CLAMPED                      10227   /* Wt/Rd Def's-Head Clamped */
#define OFFSET_TIME_FAILED                10228   /* Svo Sk Time-Head Offset Limit Exceeded */
#define T155_OVER_MAX_RESIST              10229   /* Drv Head-Resistance > Max Resistance */
#define CODE_7001                         10230   /* Drv CPF-Header Not Recovered */
#define CODE_5201                         10231   /* Drv F/W-Hold Time Exceeded */
#define ILLEGAL_VOLTAGE_MARGIN            10232   /* Proc M.E.-Illegal Voltage Margin Req'ed */
#define T155_INCONSISTENT                 10233   /* Wt/Rd Cal-Inconsistent Measurements */                    // SF2/3 T195
#define TCC_FAILED                        10234   /* Proc M.E.-Incorrect TCC Set */
#define NO_INITIATOR_IN_BIN               10235   /* Tester RIM-Initiator Card Missing */
#define LVD_XFR_MODE_FAILURE              10236   /* Tester RIM-Init Couldn't Enter LVD Mode */
#define SE_XFR_MODE_FAILURE               10237   /* Tester RIM-Init Couldn't Enter SE Mode */
#define INITR_DETECTED_CRC_ERR            10238   /* Drv Iface-Initiator Detected CRC Error */
#define INITR_DETECTED_P1_ERR             10239   /* Drv Iface-Initiator Detected P1 Error */
#define INITR_DETECTED_UBH_ERR            10240   /* Drv Iface-Initiator Detected UBH Error */
#define TH_ERASE_INN_PLUS_NOM             10241   /* Wt DC Erase-Inner Failure <--^> */
#define TH_ERASE_INN_CENT_NOM             10242   /* Wt DC Erase-Inner Failure <-^-> */
#define TH_ERASE_INN_MINUS_NOM            10243   /* Wt DC Erase-Inner Failure <^--> */
#define DDT_DST_TABLE_ERR                 10244   /* Wt/Rd Def's-Insuff DDT/DST Table Entries */
#define FAILED_INTERFACE_ERROR_RATE       10245   /* Wt/Rd Err Rate-Interface E.R. Not Met */
#define CREATE_LIST_ERROR                 10246   /* Proc TSD-Internal Memory Error */                         // SF2/3 T117, 197
#define INVALID_ATTRIBUTE                 10247   /* Proc M.E.-Invalid Attribute */                            // SF2/3 T189, Shared mk_rep
#define INVALID_CHAMBER_TEMP              10248   /* Tester Pwr/Temp Ctrl-Inv Chamber Temp */
#define INVALID_DL_LENGTH                 10249   /* Proc M.E.-Invalid D/L Length */                           // SF2/3 T8
#define INVALID_DL_TYPE                   10250   /* Proc M.E.-Invalid D/L Type */                             // SF2/3 T8
#define INVALID_SMART_DATA                10251   /* Drv SMART-Invalid Data */                                 // Shared mk_rep
#define NO_GAP_OR_WDGS_P_TRK              10252   /* Svo Misc-Invld Gap Byte Cnt or Wdges/Trk */
#define INVALID_TEST                      10253   /* Proc M.E.-Invalid Test */                                 // SF2/3 main
#define INVALID_PARAM_1                   10254   /* Proc M.E.-Invalid Test Parameter (1) */                   // SF2/3 T109, 117, 152, 191, 231
#define INVALID_PARAM_10                  10255   /* Proc M.E.-Invalid Test Parameter (10) */
#define INVALID_PARAM_2                   10256   /* Proc M.E.-Invalid Test Parameter (2) */                   // SF2/3 T32, 34, 80, 117, 127, 191
#define INVALID_PARAM_3                   10257   /* Proc M.E.-Invalid Test Parameter (3) */                   // SF2/3 T33, 34, 127
#define INVALID_PARAM_4                   10258   /* Proc M.E.-Invalid Test Parameter (4) */                   // SF2/3 T8, 117, 127, 167
#define INVALID_PARAM_5                   10259   /* Proc M.E.-Invalid Test Parameter (5) */                   // SF2/3 T33. 127
#define INVALID_PARAM_6                   10260   /* Proc M.E.-Invalid Test Parameter (6) */
#define INVALID_PARAM_7                   10261   /* Proc M.E.-Invalid Test Parameter (7) */
#define INVALID_PARAM_8                   10262   /* Proc M.E.-Invalid Test Parameter (8) */                   // SF2/3 T32
#define INVALID_PARAM_9                   10263   /* Proc M.E.-Invalid Test Parameter (9) */
#define INVALID_PARAM_VALUE               10264   /* Deprecated-Proc M.E.-Invld Test Param(s) */                    // SF2/3 various
#define NO_WWN_NETWORK_ATTRIBUTE          10265   /* Proc M.E.-Invalid WWN Network Attribute */
#define JOG_HEAD_FAILED                   10266   /* Wt/Rd Cal-Jog Head Failed */
#define JOG_TABLE_ERROR                   10267   /* Wt/Rd Cal-Jog Table Error */                              // SF2/3 T138, 139, jog
#define JOG_TEST_FAILURE                  10268   /* Drv Startup-Jog Test Failed */
#define LZ_NOT_FOUND                      10269   /* Drv Latch-Landing Zone Not Found */
#define LZ_CLOSE_TO_LATCH                 10270   /* Drv Latch-Landing Zone Too Close to ETF */
#define LZ_CLOSE_TO_ETF                   10271   /* Drv Latch-Landing Zn Too Close to Latch */
#define BAD_LED_CHECK                     10272   /* Drv PCBA-LED Check Failed */
#define T150_ENDPOINTS_INVALID            10273   /* Svo Cal-Lin Table End Pts Not 8000 Apart */
#define T150_TABLE_NOT_INCREASING         10274   /* Svo Cal-Lin Table Not Cont Increasing */
#define SERVO_DEFECT_LIST_FULL            10275   /* Svo Def's-List Full */
#define DEF_LST_LEN_ERR                   10276   /* Proc TSD-List Length Not a Multiple of 8 */               // Shared mk_rep
#define PRIMARY_DEFECT_LIST_ERROR         10277   /* Wt/Rd Def's-List Too Large */                             // SF2/3 sysfiles
#define LOG_CLAMPED                       10278   /* Wt/Rd Def's-Log Clamped-Too Many Defects */
#define DATA_OUT_OF_SPEC                  10279   /* Drv Misc-Log Data Out of Spec */                          // SF2 T25, Shared mk_rep
#define ASP_LOG_FULL                      10280   /* Wt/Rd T.A.s-Log Full */                                   // SF2/3 T109, 134
#define ETF_LOG_FULL                      10281   /* Wt/Rd Def's-Log Full */
#define UNFOUND_ETF_LOG_END               10282   /* Drv CPF-Log Full - End Not Found */
#define LOOPBACK_TEST_FAILED              10283   /* Drv Iface-Loopback Test Failed */
#define LOW_ATTR_COUNT                    10284   /* Tester Network-Low Attr Cnt from GetPut */
#define T151_LSI_FAULT                    10285   /* Wt/Rd Flt-LSI */                                          // SF2/3 reporting
#define PFLAW_PARTICLE_SUSPECTED          10286   /* Drv Misc-Magnetic Erasure Detected */
#define RV_MAGNITUDE_OOS                  10287   /* Svo RV-Magnitude Out of Spec */
#define SYSTEM_MALLOC_ERROR               10288   /* Proc TSD-Malloc Error */                                  // SF2/3 various
#define GMAX_FAILURE                      10289   /* Svo Cal-Max Gain Variation Too Large */                   // SF2/3 T150
#define T155_MAX_POWER_NOT_SET            10290   /* Proc M.E.-Max Power Not Set */
#define MAX_SCRATCH_LENGTH_ERROR          10291   /* Wt/Rd Def's-Max Scratch Length Exceeded */                // SF2/3 T117
#define EXCEEDS_MAX_AT_REJECT_THRESH      10292   /* Wt/Rd T.A.s-Max TA Reject Threshold Exc */
#define EXCEEDS_MAX_ASPS_PER_HDA          10293   /* Wt/Rd T.A.s-Max TAs Exceeded */                           // SF2/3 T109, 134
#define EXCEEDS_MAX_ASPS_PER_SURFACE      10294   /* Wt/Rd T.A.s-Max TAs/Surface Exceeded */                   // SF2/3 T134
#define EXCEEDS_MAX_ASPS_PER_TRACK        10295   /* Wt/Rd T.A.s-Max TAs/Track Exceeded */
#define VIRTUAL_SURFACE_ERROR             10296   /* Wt/Rd Def's-Max Virtual Surface Spec Exc */               // SF2/3 T117
#define T155_MAX_VOLT_NOT_SET             10297   /* Proc M.E.-Max Volt Not Set */
#define EXCD_MAX_DELTA_LMT                10298   /* Wt/Rd Cal-Max. Delta Limit Exceeded */                    // SF2/3 T35
#define BAD_MAX_HEAD_SWITCH               10299   /* Svo Sk Time-Max. Head Switch Limit Exc */
#define BAD_MAX_SEEK_TIME                 10300   /* Svo Sk Time-Max. Limit Exceeded */                        // SF2/3 T30, 32
#define CODE_1200                         10301   /* Svo Sk Time-Max. Sk-Sk Limit Exc. */
#define RV_MEAN_VALUE_OUT_OF_SPEC         10302   /* Svo RV-Mean Value Out of Spec */
#define CODE_1424                         10303   /* Svo Seek-Mech. Pos. Error */
#define MEDIA_DAMAGE_FAILURE              10304   /* Wt/Rd Def's-Media Damage Screen Failure */                // SF2/3 T117
#define SMT_MM_ERROR                      10305   /* Drv SMART-Media Manager Error */
#define T151_MM_ERROR                     10306   /* Wt/Rd Cal-Media Manager Error */                          // SF2/3 reporting
#define T151_MM_DDT_FETCH_ERR             10307   /* Wt/Rd Cal-Media Mgr Error - DDT Fetch */
#define T151_MM_IDX_ERR                   10308   /* Wt/Rd Cal-Media Mgr Error - Index */                      // SF2/3 reporting
#define T151_MM_PAR_ERR                   10309   /* Wt/Rd Cal-Media Mgr Error - Parity */                     // SF2/3 reporting
#define T151_MM_SRVO_ERR                  10310   /* Wt/Rd Cal-Media Mgr Error - Servo */                      // SF2/3 reporting
#define MJ_CENTERING                      10311   /* Wt/Rd Cal-Microjog Centering error */                     // SF2/3 T167
#define MJ_MAX_MARGIN                     10312   /* Wt/Rd Cal-Microjog Err Rate Max Margin */                 // SF2/3 T167
#define MJ_HIGH_NON_MONOTONICITY          10313   /* Wt/Rd Cal-Microjog High Non Monotonicity */
#define MJ_INTERPOLATION_CHANGED          10314   /* Wt/Rd Cal-Microjog Interpolation Changed */
#define MJ_INTERPOLATION_FAIL             10315   /* Wt/Rd Cal-Microjog Interpolation Failure */
#define MJ_LOW_CORRELATION                10316   /* Wt/Rd Cal-Microjog Low Correlation */
#define MJ_LOW_VALID_POINTS               10317   /* Wt/Rd Cal-Microjog Low Valid Points */
#define MJ_NEGATIVE_SLOPE                 10318   /* Wt/Rd Cal-Microjog Negative Slope */
#define MJ_JOG_TABLE                      10319   /* Wt/Rd Cal-ujog Offset Table Dim Conflict */               // SF2/3 T138, 139
#define MJ_OPPOSITE_STRESS_LIMIT          10320   /* Wt/Rd Cal-Microjog Opposite Stress Limit */
#define MJ_ZERO_SLOPE                     10321   /* Wt/Rd Cal-ujog Zero Slope - Can't Read */
#define BAD_MIN_HEAD_SWITCH               10322   /* Svo Sk Time-Min Hd Switch Limit Not Met */
#define BAD_MIN_SEEK_TIME                 10323   /* Svo Sk Time-Min. Limit Not Met */                         // SF2/3 T30, 32
#define T151_CANDIDATES                   10324   /* Wt/Rd Cal-Min_Candidates > Array Size */                  // SF2/3 T151
#define MISSED_FASTIO_SAMPLES             10325   /* Svo Cal-Missed FastIO Samples */                          // SF2/3 fastservo, T13, 33, 47, 175, 193
#define MULTIPLE_ERRORS                   10327   /* Drv Misc-Multiple Errors within Window */
#define MULTIPLE_SERVO_FLAWS              10328   /* Svo Def's-Multiple Servo Flaws */                         // SF2/3 T126, 134
#define T155_NEGATIVE_VOLTAGE             10329   /* Wt/Rd Cal-Negative Voltage From A/D */
#define NO_CPL_FILE                       10330   /* Proc M.E.-No CPL File */
#define NO_DATA_FOR_CURRENT_INDEX         10331   /* Drv DLD-No Data for Current Index */
#define NO_DOWNLOAD_DATA_REQUESTED        10332   /* Proc M.E.-No Download Data Requested */
#define NO_DRIVE_IN_BIN                   10333   /* Proc Operator-No Drive in Slot */
#define NO_ERROR_FREE_CYL                 10334   /* Wt/Rd Def's-No Error Free Cylinder */
#define NO_ETF_FILE                       10335   /* Proc M.E.-No ETF File */
#define NO_SERVO_FASTIO_RESPONSE          10336   /* Svo Cal-No FastIO Response */                             // SF2/3 fastservo, T150, 152, 175, 193
#define NO_GAIN_CONVERGENCE               10337   /* Svo Cal-No Gain Convergence */
#define NO_HDA_SN                         10338   /* Tester Network-No HDA S/N from Seatrack */
#define T155_NO_INCREASE                  10339   /* Wt/Rd Cal-No Increase in 4 Readings */
#define NO_INIT_COM                       10340   /* Drv Startup-No Initial Communications */
#define NO_SERVO_NPQ_RESPONSE             10341   /* Svo Cal-No NPQ Lin. Response */
#define NO_PARAM_FILE                     10342   /* Proc M.E.-No Parameter File */
#define NO_ETF_RECORDS                    10343   /* Drv CPF-No Records */                                     // SF2/3 sysfiles
#define CODE_6008                         10344   /* Proc Operator-NO SCN - operator abort */
#define NO_SCN_FROM_SEATRACK              10346   /* Proc Operator-No SCN from Seatrack */
#define NO_SCSI_FILE                      10347   /* Proc M.E.-No SCSI File */
#define CODE_1405                         10348   /* Svo Seek-No Seek Complete */
#define NO_SFLAW_FREE_CYL_FOUND           10349   /* Svo Def's-No Servo Flaw Free Cyl Found */
#define NO_TMD_LIMIT                      10350   /* Svo Pattern-No TMD Limit Exceeded */                      // SF2/3 T163
#define NO_VALID_DLD_INDEX_AVAILABLE      10351   /* Drv DLD-No Valid Data for Any Index */
#define ZAP_NORM_RD_CMD_FAILED            10352   /* Svo ZAP-Normalize rd cmd failed */                        // SF2/3 T175
#define ZAP_NORM_WRT_CMD_FAILED           10353   /* Svo ZAP-Normalize wrt cmd failed */                       // SF2/3 T175
#define NUM_ETF_COPIES                    10354   /* Drv CPF-Not Enough Copies */
#define CODE_7000                         10355   /* Drv Startup-Not Ready in Time */
#define NOT_LATCHED                       10356   /* Drv Latch-Not Set */
#define NRRO_OUT_OF_SPEC                  10357   /* Svo PES-NRRO Linearity Out of Spec */                     // SF2/3 T134
#define NRRO_OOS                          10358   /* Svo PES-NRRO Out of Spec */                               // SF2/3 T33
#define SERVO_FAULTS                      10359   /* Svo Flt-Off-track OOS */                                  // SF2/3 fastservo, T43, 195
#define TH_ERASE_OUT_PLUS_NOM             10360   /* Wt DC Erase-Outer Failure <--^> */
#define TH_ERASE_OUT_CENT_NOM             10361   /* Wt DC Erase-Outer Failure <-^-> */
#define TH_ERASE_OUT_MINUS_NOM            10362   /* Wt DC Erase-Outer Failure <^--> */
#define PPR_FAILED                        10363   /* Drv Iface-Parellel Protocol Req Failed */                 // Shared mk_rep
#define MSGIN_PE                          10364   /* Drv Iface-Parity Error During Message In */
#define PP_FAILURE                        10365   /* Svo Cal-Point to Point Gain Too Large */
#define PORT_A_NOT_BYPASSED               10366   /* Drv Iface-Port A Not Bypassed */
#define PORT_B_NOT_BYPASSED               10367   /* Drv Iface-Port B Not Bypassed */
#define REMOTE_PWR_CNTRL_ERR2             10368   /* Drv Iface-Port Open after Remote Pwr Off */
#define XOR_ERROR                         10369   /* Drv Iface-Possibly an XOR Error */                        // Shared mk_rep
#define POST_RV_ABS_DIFF_OOS              10370   /* Svo RV-Post Difference Out of Spec */
#define POST_RV_MEAN_VALUE_OOS            10371   /* Svo RV-Post Mean Value Out of Spec */
#define POST_RV_ABS_VAL_OOS               10372   /* Svo RV-Post Seek Max Out of Spec */
#define MJ_PRESCAN_THRESHOLD              10373   /* Wt/Rd Cal-Prescan Measurements Too High */
#define RV_IDLE_VALUE_OUT_OF_SPEC         10374   /* Svo RV-Pre-seek ABS Value Out of Spec */
#define ETF_PDFECT_CS_FAILURE             10375   /* Drv CPF-Prim. Defect File Chksum Failure */
#define CODE_1425                         10376   /* Svo Seek-Prim Rdm Seeks in Progress */
#define PROQUAL_FAILURE                   10377   /* Proc Operator-Proqual Failure */
#define MJ_ER_SUM_DELTA                   10378   /* Wt/Rd Cal-QMM Figure of Merit too big */                  // SF2/3 mk_rep, T138, 139
#define QUAL_ACUTAL_REWORK                10379   /* Proc Operator-Actual Rwk != Rec'ed Rwk */
#define QUAL_AGT_SVR_DOWN                 10380   /* Tester Network-Server Connection Down */
#define QUAL_DEFECT_MAP_NOT_FOUND         10381   /* Proc M.E.-Defect Map Not Found */
#define QUAL_WRONG_OP                     10382   /* Proc Operator-Drive at Wrong Oper */
#define QUAL_DRIVE_FAILED_TO_SELECT       10383   /* Drv Iface-Drive Failed to Select */
#define QUAL_GETPUT_PROQUAL_FAILURE       10384   /* Proc Operator-Get/Put ProQual Fail */
#define QUAL_INCORRECT_DCC                10385   /* Proc Operator-Wrong DCC Assigned to Drv */
#define QUAL_MISSING_RECORD               10386   /* Proc Operator-Missing Rec/Access Failure */
#define QUAL_MOVE_TO_NEW_SLOT             10387   /* Tester RIM-Move Drive to New Slot */
#define QUAL_NO_PROCESS_TABLE             10388   /* Proc M.E.-No Process Table for P/N */
#define QUAL_NO_VALID_OP                  10389   /* Proc Operator-Invalid Oper Table for S/N */
#define QUAL_OP_NOT_ENTRY_POINT           10390   /* Proc Operator-Oper is Not an Entry Pt */
#define QUAL_OP_TOO_EARLY                 10391   /* Proc Operator-Oper Started too Early */
#define QUAL_OP_TOO_LATE                  10392   /* Proc Operator-Oper Started too Late */
#define QUAL_BAD_PART_NUM                 10393   /* Proc Operator-P/N Fmt Not XXXXXX-XXX */
#define QUAL_UNKNOWN_OP                   10394   /* Proc Operator-Requested Oper Unknwn */
#define QUAL_REWORK_NO_DIAG               10395   /* Proc Operator-Rework Without Diag */
#define QUAL_TOO_MANY_RUNS                10396   /* Proc Operator-Too Many Runs @Oper */
#define QUAL_NO_ROUTE                     10397   /* Proc M.E.-No Route for P/N at Oper */
#define DST_07                            10398   /* Rd DST-Rd/Verify Segment Failed */
#define READ_ETF_FAILED_AFTER_WRITE       10399   /* Drv CPF-Read after Write Failure */                       // SF2/3 T149
#define ETF_READ_BACK_FAILED              10400   /* Rd CPF-Read Back Failed */
#define T151_RD_PREAMP_UNSAFE             10401   /* Wt/Rd T.A.s-Read During Preamp Unsafe */                  // SF2/3 reporting
#define READ_ERROR                        10402   /* Rd Misc-Read Error */                                     // SF2/3 T139, 151, 191, 195 Shared mk_rep
#define READ_ETF_FAILED                   10403   /* Rd CPF-Read Failed */                                     // SF2/3 T37, 114, 130, 149 Shared mk_rep
#define T151_READ_TOO_LONG                10404   /* Wt/Rd Cal-Read Longer Than Write */
#define RCVD_RD_ERR_LIM_EXCEEDED          10405   /* Rd Err Rate-Rec Rd Error Limit Exceeded */
#define RCVD_SRVO_ERR_LIM_EXCEEDED        10406   /* Svo Err Rate-Rec Svo Err Limit Exceeded */
#define RCVD_WRT_ERR_LIM_EXCEEDED         10407   /* Wt Err Rate-Rec Wt Error Limit Exceeded */
#define FILE_TOO_LARGE                    10408   /* Proc M.E.-Report File Too Large */
#define CODE_2638                         10409   /* Proc TSD-Request TSE LBA Failed */
#define DST_08                            10410   /* Drv DST-Reserved Selftest Value */
#define T151_ETF_RESTORE_FAILED           10411   /* Wt CPF-Restore of Data Failed */
#define RST_SYS_FRM_DFLTS_FAILED          10412   /* Drv CPF-Restore of Defaults Failed */
#define RO_OOS                            10413   /* Svo PES-RO Out of Spec */
#define RRO_OOS                           10414   /* Svo PES-RRO Out of Spec */                                // SF2/3 T29, 33, 193, 194
#define ETF_RDF_CS_FAILURE                10415   /* Drv CPF-RSVD Def File Checksum Failure */
#define BAD_RTZ_TIME                      10416   /* Svo Sk Time-RTZ Limit Exceeded */
#define CODE_2637                         10417   /* Wt Fmt-Same Cylinder Format Error */
#define ETF_SAP_CS_FAILURE                10418   /* Drv F/W-SAP File Checksum Failure */
#define SAVE_TO_ETF_FAILED                10419   /* Wt CPF-Save to ETF Failed */                              // SF2/3 T118, 149
#define SCRATCH_FILL_FAILED               10420   /* Drv CPF-Scratch Fill Failed */
#define BUS_DATA_BITS_ASSERTED            10421   /* Drv Iface-SCSI Data Asserted in Bus Free */               // Shared mk_rep
#define SCSI_SELF_TEST                    10422   /* Drv PCBA-SCSI Selftest Command Failed */
#define SCSI_COMMAND_FAILED               10423   /* Drv Iface-SCSI Serial Command Failed */
#define SCSI_ERR_RETRIES_EXCEEDED         10424   /* Tester Comm Mgr-SCSIERR.TXT Retries Exc */
#define CODE_1426                         10425   /* Svo Seek-Sec. rdm seeks in progress */
#define ETF_SECTOR_RE_READ_FAILED         10426   /* Rd CPF-Sector Re-read Failed */
#define SEEK_FAILURE                      10427   /* Svo Seek-Seek Failure */                                  // SF2/3 various
#define RV_SENSOR_SELFTEST_DELTA_FAILED   10428   /* Svo RV-Selftest Failure */
#define DST_0F                            10429   /* Drv DST-Selftest in Progress */
#define RV_SENSOR_DETECTED                10430   /* Svo RV-Sensor Detected & Not Req'ed */
#define RV_SENSOR_FAULTY_OR_MISSING       10431   /* Svo RV-Sensor Faulty or Missing */
#define STACK_DEPTH_EXCEEDED              10432   /* Proc TSD-Seq. Stack Depth Exceeded */
#define T151_SEQ_HANDSHAKE                10433   /* Proc M.E.-Sequencer Handshake Error */
#define T151_MYSTERY                      10434   /* Wt/Rd Cal-Sequencer Mystery Halt */
#define T151_SEQ_SYNC0                    10435   /* Wt/Rd Cal-Sequencer Sync Error 0 */
#define T151_SEQ_SYNC1                    10436   /* Wt/Rd Cal-Sequencer Sync Error 1 */
#define T151_SEQ_UNKNOWN                  10437   /* Wt/Rd Cal-Sequencer Unknown Error */
#define T151_SEQ_WAIT0                    10438   /* Wt/Rd Cal-Sequencer Wait Error 0 */
#define T151_SEQ_WAIT1                    10439   /* Wt/Rd Cal-Sequencer Wait Error 1 */
#define T151_WATCHDOG                     10440   /* Drv Timeout-Sequencer Watchdog */
#define SERIAL_SCSI_CHECK_CONDITION       10441   /* Drv Iface-Serial SCSI Check */
#define SERIAL_SCSI_COMMAND_ABORTED       10442   /* Drv Iface-Serial SCSI Command Aborted */
#define SERVO_FAILURE                     10443   /* Svo Generic-Servo Failure */                                 // SF2/3 various
#define SHORTED_TURN_DETECTED             10444   /* Svo VCM-Shorted Turn */
#define TOO_MANY_WEAK_HEADS               10445   /* Rd Err Rate-Sgl Hd W/R on Too Many Hds */
#define SLIP_FAILURE                      10446   /* Wt/Rd Def's-Slip Failure */                               // SF2/3 T130
#define SMT_ALT_TONE_UNKNOWN_TO           10447   /* Drv Timeout-SMART Alt Tone Unknown */
#define SMT_SERVO_UNSAFE                  10448   /* Svo PES-SMART Servo Unsafe */
#define SMT_WATCHDOG_TO                   10449   /* Drv Timeout-SMART Watchdog */
#define SERVO_SPIKE_FAILURE               10450   /* Svo Seek-Spike Failure */                                 // SF2/3 T30
#define SP240_RESULT_FILE_READ_ERROR      10451   /* Rd Misc-SPT Result File Read Error */                     // SF2/3 T231
#define SSI_OPT_FAILED                    10452   /* Wt/Rd Cal-SSI Optimization Failed */
#define HD_STABILITY_TEST_FAILED          10453   /* Drv Head-Stability Test Failed */
#define START_MOTOR_FAILED                10454   /* Svo Startup-Start Motor Failed */                         // SF2/3 main, T1, 47, 178, 185
#define SENSE_DATA_TOO_LARGE              10455   /* Proc TSD-Sense Data Storage Too Small */
#define SENSE_DATA_PAGE_ERROR             10456   /* Proc TSD-Sense Pg Data Storage Too Small */
#define SYNCH_XFR_MODE_FAILED             10457   /* Drv Iface-Sync Data Transfer Mode Failed */               // Shared mk_rep
#define T151_SYNC_ERROR                   10458   /* Wt/Rd Cal-Sync Error */
#define SYNC_ERR_LZONE                    10459   /* Drv Latch-Sync Errors in Landing Zone */
#define CORRUPTED_ASP_LOG                 10460   /* Wt/Rd Def's-T.A. Log Corrupted */                         // SF2/3 T134
#define T151_BLOW_OUT                     10461   /* Wt/Rd Cal-T151 Blow-out Re-measurement */
#define T151_OFFSET_SEARCH                10462   /* Wt/Rd Cal-T151 Offset Search Excess Cnt */                // SF2/3 T151
#define SFLAW_TABLE_FULL                  10463   /* Svo Def's-Table Full */                                   // SF2/3 various
#define TCQ_BAD_SCSI_STATUS_H             10464   /* Wt/Rd Misc-Tag Cmd Q'ing Bad SCSI Status */
#define TCC_OFFSET_ERROR                  10465   /* Proc M.E.-TCC Offset Spec Exceeded */
#define DC_ERASE_TEST_FAILURE             10466   /* Wt Trk Erase-Test Failed */                               // SF2 T127
#define SMART_FAILED                      10467   /* Drv SMART-Test Failed */
#define TEST_FAILED                       10468   /* Drv Misc-Test Failed */                                   // SF2/3 various
#define TEST_FAILED_ERROR_LIMIT           10469   /* Wt/Rd Err Rate-Test Failed Error Limit */                 // SF3 T109
#define FAILED_TEST_TIME                  10470   /* Proc M.E.-Test Time Limit Exceeded */
#define TEST_TIMED_OUT                    10471   /* Drv Timeout-Test Time Limit Exceeded */                   // Shared mk_rep
#define ETF_TEST_TRKS_FAILED              10472   /* Drv CPF-Test Tracks Failed */
#define TOO_MANY_AST_ENTRIES              10473   /* Wt/Rd Def's-Too Many AST Entries */                       // SF2/3 T130
#define TOO_MANY_BAD_SECTORS              10474   /* Wt/Rd Def's-Too Many Deallocated Sectors */
#define TOO_DEF_SECTORS_PER_ZONE          10475   /* Wt/Rd Def's-Too Many Defective Sectrs/Zn */
#define PFLAW_TESTING_FAILED              10476   /* Wt/Rd Def's-Too Many Defects or Seeks */
#define TOO_MANY_DEFS_HD                  10477   /* Wt/Rd Def's-Too Many Defects Per Head */                  // Shared mk_rep
#define TOO_MANY_DST_ENTRIES              10478   /* Wt/Rd Def's-Too Many DST Entries */                       // SF2/3 T130
#define TOO_MANY_ERRORS                   10479   /* Wt/Rd Err Rate-Too Many Errors */                         // SF3 T109
#define FLAWS_PER_CYL_FAILED              10480   /* Wt/Rd Def's-Too Many Errs/Cyl After Fill */               // Shared mk_rep
#define FLAWS_PER_TRK_FAILED              10481   /* Wt/Rd Def's-Too Many Errs/Trk After Fill */               // Shared mk_rep
#define TOO_MANY_FLAWS                    10482   /* Wt/Rd Def's-Too Many Flaws After Filling */               // SF2/3 various
#define MAKE_LIST_ERROR                   10483   /* Wt/Rd Def's-Too Many Flaws Before Fill */
#define TOO_MANY_FLAWS_PER_CYL            10484   /* Wt/Rd Def's-Too Many Flaws Per Cylinder */                // SF2/3 T140
#define TOO_MANY_FLAWS_PER_TRACK          10485   /* Wt/Rd Def's-Too Many Flaws Per Track */                   // SF2/3 T140
#define TOO_MANY_FLAWS_HEAD               10486   /* Wt/Rd Def's-Too Many Flaws/Hd After Fill */               // SF2/3 T117
#define TOO_MANY_FLAWS_PER_REGION         10487   /* Wt/Rd Def's-Too Many Flaws/Region */                      // Shared mk_rep
#define TOO_MANY_DEPOP_HEADS              10488   /* Wt/Rd Err Rate-Too Many Hds to Depop */
#define TOO_MANY_BAD_HEADS                10489   /* Wt/Rd Cal-Too Many Heads to Optimize */
#define RLEC_ERROR                        10490   /* Drv Misc-Too Many Logged Exceptions */
#define TOO_MANY_MAX_ASP_CAP_TRACKS       10491   /* Wt/Rd T.A.s-Too Many Max TA Cap Tracks */
#define TOO_MANY_NONDTA_RD_ER             10492   /* Rd Err Rate-Too Many Nondata Read Errors */
#define TOO_MANY_RD_ERRORS                10493   /* Rd Err Rate-Too Many Read Errors */
#define TOO_MANY_REALLOC_SECT_ZN          10494   /* Wt/Rd Def's-Too Many Realloc Sect/Zone */                 // SF2/3 T130
#define TOO_MANY_REC_NONREC_ERRORS        10495   /* Wt/Rd Err Rate-Too Many Rec & Unrec Errs */
#define TOO_MANY_REC_ERRORS               10496   /* Wt/Rd Err Rate-Too Many Rec Errors */
#define TOO_MANY_RECOV_UNVER              10497   /* Wt/Rd Err Rate-Too Many Rec/Unver Errors */
#define TOO_MANY_RECOV_VERIF              10498   /* Wt/Rd Def's-Too Many Rec/Ver Errors */
#define FLAWS_PER_RESCYL_FAILED           10499   /* Wt/Rd Def's-Too Many Reserved Cyl. Flaws */               // Shared mk_rep
#define TOO_MANY_REVS                     10500   /* Svo Seek-Too Many Revs */
#define TOO_MANY_SCSI_ERR_CODES           10501   /* Wt/Rd Err Rate-Too Many SCSI Error Codes */
#define TOO_MANY_SEEK_ERRS                10502   /* Svo Seek-Too Many Seek Errors */                          // SF2/3 various
#define TOO_MANY_SERVO_ERRORS             10503   /* Svo Err Rate-Too Many Servo Errors */                     // SF2/3 T163
#define TOO_MANY_SERVO_FLAWS              10504   /* Svo Def's-Too Many Servo Flaws */                         // SF2/3 T117, 126, 134
#define TRACK_SLIPPED                     10505   /* Svo Def's-Too Many Slipped Trks */
#define TOO_MANY_TOT_DEFS                 10506   /* Wt/Rd Def's-Too Many Total Defects */                     // Shared mk_rep
#define TOO_MANY_NONREC_ERRORS            10507   /* Wt/Rd Err Rate-Too Many Unrec Errors */
#define TOO_MANY_UNREC_UNVER              10508   /* Wt/Rd Err Rate-Too Many Unrec/Unver Errs */
#define TOO_MANY_UNREC_VERIF              10509   /* Wt/Rd Def's-Too Many Unrec/Ver Errors */
#define TOTAL_UNVER_FAILED                10510   /* Wt/Rd Err Rate-Too Many Unver Errors */                   // SF2/3 T140
#define TWO_PLUS_UNVER_HD_FAILURE         10511   /* Wt/Rd Err Rate-Too Many Unver Errs>2 Hds */               // SF2/3 T140
#define ONE_UNVER_HD_FAILURE              10512   /* Wt/Rd Err Rate-Too Many Unver Errs-1 Hd */                // SF2/3 T140
#define TWO_UNVER_HD_FAILURE              10513   /* Wt/Rd Err Rate-Too Many Unver Errs-2 Hds */               // SF2/3 T140
#define TOO_MANY_UNVER_PER_HEAD           10514   /* Wt/Rd Err Rate-Too Many Unver Errs/Head */                // Shared mk_rep
#define UNVER_HEAD_ZONE_FAILURE           10515   /* Wt/Rd Def's-Too Many Unver. Errs/Hd-Zone */               // SF2/3 T140
#define TOTAL_VER_FAILED                  10516   /* Wt/Rd Def's-Too Many Ver Errors */                        // SF2/3 T140
#define TWO_PLUS_VER_HD_FAILURE           10517   /* Wt/Rd Def's-Too Many Ver Errs on >2 Hds */                // SF2/3 T140
#define ONE_VER_HD_FAILURE                10518   /* Wt/Rd Def's-Too Many Ver Errs on 1 Head */                // SF2 T140
#define TWO_VER_HD_FAILURE                10519   /* Wt/Rd Def's-Too Many Ver Errs on 2 Hds */                 // SF2/3 T140
#define TOO_MANY_VER_PER_HEAD             10520   /* Wt/Rd Def's-Too Many Ver Errors/Head */                   // Shared mk_rep
#define TOO_MANY_WRITE_ERRS               10521   /* Wt Err Rate-Too Many Write Errors */                      // SF2/3 T167, 210
#define WRITE_FAILURE                     10522   /* Wt Err Rate-Too Many Wt Errs, Can't Cont */               // SF2/3 various
#define T155_TOO_MANY_ZEROS               10523   /* Wt/Rd Cal-Too Many Zero Readings */
#define WIDE_HEAD_FAILURE                 10524   /* Drv Head-Too Wide */
#define TRANSFER_FAILURE                  10525   /* Drv Iface-Transfer Failure */
#define TRUNCATED_RESULT_FILE_READ        10526   /* Proc M.E.-Truncated Result File Read */
#define TRUNCATED_RESULT_FILE_WRITE       10527   /* Proc M.E.-Truncated Result File Write */                  // SF2/3 T231
#define TUNED_SEEK_FAILURE                10528   /* Svo Seek-Tuned Seek Failure */                            // SF2/3 T7
#define T151_LSI_WF                       10529   /* Wt Flt-Type Not Specified */
#define MSGIN_UBH_ERROR                   10530   /* Drv Iface-UBH Error During Message In */
#define STATUS_PHASE_UBH_ERROR            10531   /* Drv Iface-UBH Error During Status Phase */
#define OUT_OF_MEMORY                     10532   /* Tester Comm Mgr-Can't Allocate Memory */                  // SF2/3 various
#define BAD_ERASE                         10533   /* Drv F/W-Unable to Erase Flash */
#define FILL_LIST_ERROR                   10534   /* Wt/Rd Def's-Can't Fill, Too Many Flaws */
#define PORT_NOT_OPENED                   10535   /* Drv Iface-Unable to Open Port */
#define NO_TESTSEQ_FILE                   10536   /* Proc M.E.-Unable to Open Test Seq File */
#define BAD_PROGRAM                       10537   /* Drv F/W-Unable to Program Flash */
#define READ_PC_FILE_FAILED               10538   /* Tester Comm Mgr-Unable to Read a PC File */               // SF2/3 various
#define BAD_ETF_BLOCK_0                   10539   /* Rd CPF-Unable to Read Block 0 */
#define BAD_FLASH_ID                      10540   /* Drv F/W-Unable to Read Flash ID */
#define NO_FILE_BLOCK                     10541   /* Proc M.E.-Unable to Receive File From PC */               // SF3 T152
#define T155_SEL_MODE_ERROR               10542   /* Wt/Rd Cal-Unable To Select a Mode */
#define NO_START_NETWORK_DOWN             10543   /* Tester Network-Can't Start, Network Down */
#define WRITE_PC_FILE_FAILED              10544   /* Tester Comm Mgr-Unable to Wt a PC File */                 // SF2/3 various
#define UNACCEPTABLE_REQUEST_SENSE        10545   /* Drv Misc-Unacceptable Request Sense */
#define UNCERTED_TRACK                    10546   /* Svo Def's-Uncerted Track */                               // SF2/3 T109, 126
#define UNCERTED_TRACK_RW                 10547   /* Wt/Rd Def's-Uncerted Track RW */                          // SF2/3 T109
#define UNCERTED_TRACK_SERVO              10548   /* Svo Def's-Uncerted Track Servo */                         // SF2/3 T109
#define UNCERTED_TRACK_SFLAW              10549   /* Svo Def's-Uncerted Track Sflaw */                         // SF2/3 T109
#define UNCORRECTED_GAIN_DELTA_FAILURE    10550   /* Svo Cal-Uncorrected Gain Delta Failure */
#define CODE_5003                         10551   /* Drv Iface-Undefined Message from Drive */
#define REMOTE_PWR_CNTRL_ERR1             10552   /* Drv Iface-PreRemote Pwr Off Unexp Status */
#define DST_03                            10553   /* Drv DST-Unknown Error; Can't Complete */
#define UNKNOWN_PREAMP                    10554   /* Proc TSD-Unknown Preamp */                                // SF2/3 servo, T191
#define DST_04                            10555   /* Drv DST-Unknown Segment Failed */
#define REMOTE_PWR_CNTRL_ERR3             10556   /* Drv Iface-Remote Pwr-On Unlock Failed */
#define FAILED_FOR_UNRCVD_ERR             10557   /* Wt/Rd Def's-Unrec. Error */
#define T155_UNSUPPORTED_PREAMP           10558   /* Proc TSD-Unrecognized Preamp Rev */                       // SF2/3 servo, T109, 178
#define UNSAFE_LIMIT                      10559   /* Svo PES-Unsafe Limit Exceeded */                          // SF2/3 T30, 35, 163
#define UNSTABLE_HEAD                     10560   /* Drv Head-Unstable */
#define UNSUPPORTED_LOG_TYPE              10561   /* Proc TSD-Unsupported Log Type */                          // SF2/3 sort
#define PERCENT_SPARES_EXCEEDED           10562   /* Wt/Rd Def's-Used Spare Trks % Limit Exc */
#define VERIFICATION_MISCOMPARE           10563   /* Drv Iface-Verification Miscompare */                      // SF2/3 sort
#define VERIFY_ETF_FAILED                 10564   /* Rd CPF-Verify Failed */
#define VIC_FAULT                         10565   /* Wt/Rd Flt-VIC Fault */
#define TCQ_IO_TIMEOUT_H                  10566   /* Drv Timeout-Waiting for Cmd Complete */
#define WRT_CUR_ADJ_FAILED                10567   /* Wt/Rd Cal-Write Current Adjust Failed */
#define T151_WRT_CUR_MARGIN_LIMIT         10568   /* Wt/Rd Cal-Write Current Margin Limit */                   // Shared mk_rep
#define T151_WRT_SHOCK                    10569   /* Wt Flt-Write During Shock */                              // SF2/3 reporting
#define WRITE_ETF_FAILED                  10570   /* Wt CPF-Write Failed */                                    // SF2/3 sysfiles, T37, 149
#define WRG_GAT_SRV_UNSAFE                10571   /* Wt Flt-Write Gate w/Servo Unsafe */
#define T151_WRT_INTO_SERVO               10572   /* Wt Flt-Write into Servo Wedge */
#define CODE_2639                         10573   /* Wt Misc-Write TSE LBA Failed */
#define T151_WRT_LOW_VOLT                 10574   /* Wt Flt-Write with Low Voltage */
#define T151_WRT_PREAMP_UNSAFE            10575   /* Wt Flt-Write with Preamp Unsafe */                        // SF2/3 reporting
#define T151_WRT_SERVO_UNSAFE             10576   /* Wt Flt-Write with Servo Unsafe */                         // SF2/3 diagapi, T151
#define WRONG_PS1_POLARITY                10577   /* Svo Pattern-Wrong PS1 Polarity */
#define ZONE_BASED_TRANSFER_RATE_OOS      10578   /* Wt/Rd Xfer Rate-Zone-based Rates Not Met */
#define CODE_6225                         10579   /* Proc M.E.-Mode Select Failed */
#define ILLEGAL_VALIDATION_KEY            10580   /* Drv Misc-Validation Keys Did Not Match */
#define SLEW_RATE_OUT_OF_SPEC             10581   /* Proc M.E.-Slew Rate Out Of Spec */
#define HEAD_LOT_NOT_SUPPORTED            10582   /* Proc M.E.-No Hd Lot Support In This Fmt */
#define RPRINTF_FAILURE                   10583   /* Proc TSD-rprintf() Failure */                             // SF2/3 T151, Shared DIN_DEX
#define MIN_TRANSFER_RATE_NOT_MET         10584   /* Wt/Rd Xfer Rate-Min. Xfer Rate Not Met */
#define ADD_MULT_OVERFLOW                 10585   /* Proc TSD-Add or Mult. Overflow */
#define SELF_TEST_SERVO_CMD_TIMEOUT       10586   /* Svo Misc-Timeout Waiting For Servo Cmd */
#define EXCEED_MAX_BDRAG_DELTA_LIMIT      10587   /* Svo Cal-Exceeded Max BDRAG Delta Limit */                 // SF2/3 T10
#define SAMPLE_A_MAG_OOS                  10588   /* Svo Cal-Sample_a out of spec */                           // SF2/3 T25, 31
#define SAMPLE_B_MAG_OOS                  10589   /* Svo Cal-Sample_b out of spec */                           // SF2/3 T25, 31
#define OFFSET_DELTA_OOS                  10590   /* Svo Cal-Offset delta out of spec */                       // SF2/3 T31, 44
#define LOG_FULL                          10591   /* Drv DBI-DBI Log Full */                                   // SF2/3 T109, 134
#define MJ_ZERO_DATA                      10592   /* Proc TSD-Not enough data pts/div by 0 */                  // SF2/3 T139, 152, 191
#define MJ_2T_WRT_FAIL                    10593   /* Wt Misc-2T PLO Wt Fail; Svo/Dsk Event */                  // SF2/3 T139
#define INVALID_LSI_INFORMATION           10594   /* Drv F/W-Invalid LSI Information */
#define NOT_IN_FAST_SEEK_MODE             10595   /* Proc M.E.-Not in Fast Seek Mode */
#define ELS_FRAME_TIMEOUT                 10596   /* Drv Timeout-Extended Link Srvc Frame T-O */
#define ELS_FRAME_REJECTED                10597   /* Drv Iface-Ext Link Serv. Frame Rejected */
#define BAD_PRLI_RESPONSE_CODE            10598   /* Drv Iface-Bad Proc Login Response Code */
#define FAILED_SECTOR_CRC_BOUNDARY        10599   /* Drv Iface-Data/CRC not Modulo sect edge */
#define INVALID_TYPE_CMD                  10600   /* Drv Iface-Cmd Sent doesn't match LQ Type */
#define INVALID_LQ_TYPE                   10601   /* Drv Iface-Invalid LQ Type */
#define PORT_NOT_LOGGED_IN                10602   /* Drv Iface-Port Not Logged In */
#define POSITION_MAP_MISMATCH             10603   /* Drv Iface-Position Map Error */
#define UNIQUE_ERROR_CODE                 10604   /* Drv Misc-Unique Error Code */
#define DPT_CMD_PROC_ERROR                10607   /* Drv Iface-No Dual Port Cmd Processed */
#define DPT_CMD_COM_ERROR                 10608   /* Drv Iface-No Dual Port Test Cmd Complete */
#define NO_CC                             10609   /* Drv Iface-No Command Complete */
#define INVALID_HDA_SERIAL_NUMBER         10610   /* Tester Misc-Invalid HDA S/N Rd From HDA */
#define COM_CHECK_COMPLETE                10611   /* Tester Misc-Communications Check OK */
#define NO_SSP_FILE                       10612   /* Proc M.E.-Unable To Open SSP File */
#define SSP_LOG_CHECK_BAD_PAGE            10613   /* Proc M.E.- SSP-Requested page not found */
#define SSP_LOG_CHECK_BAD_PARM            10614   /* Proc M.E.-SSP-Req'ed parameter not found */
#define SSP_NO_SMART_DATA                 10615   /* Proc M.E.-No smart frame in data file */
#define SSP_LOG_CHECK                     10616   /* Drv F/W-SSP Log Check Failure */
#define TOO_MANY_BAD_SEEK_TIME            10617   /* Svo Seek-Too Many Bad Seek Time */                        // SF2/3 T37
#define STD_DEVIATION_TOO_LARGE           10618   /* Svo Seek-Standard Deviation Too Large */                  // SF2/3 T37, 175
#define T155_BELOW_MIN_RESIST             10619   /* Drv Head-Hd Resistance Below Min Resist */
#define VGA_SATURATION_FAILURE            10620   /* Wt/Rd Cal-VGA values Saturated */
#define FAILS_LANDING_ZONE_TA_LIMIT       10621   /* Wt/Rd T.A.s-Fails landing zone TA limit */
#define AGC_DELTA_EXCEEDED                10622   /* Drv Head- AGC Delta exceeded */
#define HEAD_CLAMPED_UNCERTED_TRK_OOS     10623   /* Wt/Rd Def's-Uncerted Trks>Limit */
#define HEAD_CLAMPED_VER_HD_ZONE_OOS      10624   /* Wt/Rd Def's-Ver Defs in Hd-Zn>Limit */                    // SF2/3 T109
#define HEAD_CLAMPED_UNVER_HD_ZONE_OOS    10625   /* Wt/Rd Err Rate-Unver Errs in Hd-Zn>Limit */               // SF2/3 T109
#define TOO_MANY_CONSEC_SKIP_TRACKS       10626   /* Svo Def's-Too Many Consec SFT Skip Trks */                // SF2/3 T126
#define TOO_MANY_SKIP_TRACKS              10627   /* Svo Def's-Too Many Skip Trks in SFT */                    // SF2/3 T126
#define DIFF_MAGNITUDE_OOS                10628   /* Svo Cal-OD-ID AC Magnitude Diff. Exceeded */              // SF2/3 T12, 13, 31, 43, 44
#define DIFF_DC_OFFSET_OOS                10629   /* Svo Cal-OD-ID DC Offset Diff. Exceeded */                 // SF2/3 T31
#define HOST_NOT_IN_PKT_MODE              10630   /* Drv Iface-Host Not in Packetized Mode */
#define INVALID_MESSAGE                   10631   /* Drv Iface-Invalid Negotiation Message */
#define ERROR_RATE_ERROR                  10632   /* Wt/Rd Err Rate-Min. Err Rate Not Met */                   // SF3 T211
#define FAILED_SPINUP_0204                10633   /* Svo Startup-02/04 No Spin Up,LC=22,2D,2E */
#define FAILED_UNLATCH_0204               10634   /* Svo Startup-02/04 Unlatch Failed,LC=7F */
#define FAILED_DEMOD_SYNC_0204            10635   /* Svo Startup-02/04 No Demod Sync,LC=32-3D */
#define FAILED_AGC_CAL_0204               10636   /* Svo Startup-02/04 AGC Cal Failed,LC=88 */
#define FAILED_DC_CAL_0204                10637   /* Svo Startup-02/04 DC Cal Failed,LC=89 */
#define FAILED_FCC_CAL_0204               10638   /* Svo Startup-02/04 FCC Cal Failed,LC=8A */
#define FAILED_SPINUP_0442                10639   /* Svo Startup-04/42 No Spin Up,LC=22,2D,2E */
#define FAILED_UNLATCH_0442               10640   /* Svo Startup-04/42 Unlatch Failed,LC=7F */
#define FAILED_DEMOD_SYNC_0442            10641   /* Svo Startup-04/42 No Demod Sync,LC=32-3D */
#define FAILED_AGC_CAL_0442               10642   /* Svo Startup-04/42 AGC Cal Failed,LC=88 */
#define FAILED_DC_CAL_0442                10643   /* Svo Startup-04/42 DC Cal Failed,LC=89 */
#define FAILED_FCC_CAL_0442               10644   /* Svo Startup-04/42 FCC Cal Failed,LC=8A */
#define SAVE_APM_TO_FILE_ERROR            10645   /* Proc TSD-Error Writing the APM File */
#define SERVO_LIMIT                       10646   /* Svo Cal-Limit Failed */                                   // SF2/3 T43, 189
#define AUTO_REALL_ENABLED                10647   /* Proc Operator-AutoRealloc Enabled on HDA */
#define PWA_INFO_IN_APM_MISMATCH          10648   /* Drv PCBA-APM PCBA Info<>Data Entered */
#define INVALID_ENTRY_IN_DRIVE_CFG        10649   /* Proc M.E.-Invalid Entry in Drive.CFG */
#define DRIVE_TYPE_NOT_FOUND              10650   /* Proc M.E.-Drive Type Not in Drive.CFG */
#define GENERIC_APM_FILE_NOT_FOUND        10651   /* Proc M.E.-Generic APM File Not Found */                   // SF3 diagapi
#define SAP_FILE_NOT_FOUND                10652   /* Proc Operator-SAP File Not Found */
#define UNABLE_TO_CREATE_CAP_FILE         10653   /* Proc TSD-Can't Create Cap_APM.LOD File */
#define CODE_6013                         10654   /* Proc M.E.-F/W File Size <> Spec */
#define ACTCVALUE_OOS                     10655   /* Svo Cal-AC Magnitude Limit Exceeded */                    // SF2/3 T31
#define DIFF_SAMPLE_A_B_OOS               10656   /* Svo Cal-Sample A-Sample B Diff. Exceeded */               // SF2/3 T31
#define INCONSISTENT_ZAP_RW_CAL           10657   /* Svo ZAP-Inconsistent ZAP R/W Cal */                       // SF3 T175
#define NEGATIVE_ZAP_RW_CAL_SLOPE         10658   /* Svo ZAP-Negative ZAP R/W Cal Slope */                     // SF2/3 T175
#define ANALOG_CAL_FAILED                 10659   /* Wt/Rd Cal-Analog Cal Did Not Complete */
#define TBG_CAL_FAILED                    10660   /* Wt/Rd Cal-TBG Cal Did Not Complete */
#define VGA_MAX_SPEC_EXCEEDED             10661   /* Wt/Rd Cal-VGA Exceeded Maximum Spec */
#define VGA_DELTA_EXCEEDED                10662   /* Wt/Rd Cal-VGA Delta Exceeded */
#define EXCEEDED_SERVO_CNT_LIMIT          10663   /* Svo Def's-Servo Count Limit Exceeded */                   // SF2/3 T25
#define FAILED_SPINUP                     10664   /* Svo Startup-No Spin Up,LC=21 -> 2E */                     // SF2/3 main, T186, 208
#define FAILED_UNLATCH                    10665   /* Svo Startup-Unlatch Failed,LC=7F */                       // SF2/3 main, T186, 208
#define FAILED_DEMOD_SYNC                 10666   /* Svo Startup-No Demod Sync,LC=32 -> 3D */                  // SF2/3 T13, 43, 44, 45, 47, 177, 186, 208
#define FAILED_VEL_CTRL_CAL               10667   /* Svo Startup-Vel Ctrl Cal Failed,LC=42 -> 47 */            // SF2/3 main T208
#define FAILED_AGC_CAL                    10668   /* Svo Startup-AGC Cal Failed,LC=88 */                       // SF2/3 main T208
#define FAILED_DC_CAL                     10669   /* Svo Startup-DC Cal Failed,LC=89 */                        // SF2/3 main T208
#define FAILED_FC_CAL                     10670   /* Svo Startup-FC Cal Failed,LC=8A */                        // SF2/3 main T208
#define FAILED_ACFF_CAL                   10671   /* Svo Startup-ACFF Cal Failed,LC=8B */                      // SF2/3 main T208
#define FAILED_TRK_FOLLOW_CAL             10672   /* Svo Startup-Track Follow Cal Failed,LC=8C */              // SF2/3 main T208
#define REGRESSION_DRV_FW_FAILED_FUNC_1   10673   /* Regr F/W-Failed Function 1 */
#define REGRESSION_DRV_FW_FAILED_FUNC_2   10674   /* Regr F/W-Failed Function 2 */
#define REGRESSION_DRV_FW_FAILED_FUNC_3   10675   /* Regr F/W-Failed Function 3 */
#define REGRESSION_DRV_FW_FAILED_FUNC_4   10676   /* Regr F/W-Failed Function 4 */
#define REGRESSION_DRV_FW_FAILED_FUNC_5   10677   /* Regr F/W-Failed Function 5 */
#define REGRESSION_DRV_FW_FAILED_FUNC_6   10678   /* Regr F/W-Failed Function 6 */
#define REGRESSION_DRV_FW_FAILED_FUNC_7   10679   /* Regr F/W-Failed Function 7 */
#define REGRESSION_DRV_FW_FAILED_FUNC_8   10680   /* Regr F/W-Failed Function 8 */
#define REGRESSION_DRV_FW_FAILED_FUNC_9   10681   /* Regr F/W-Failed Function 9 */
#define REGRESSION_DRV_FW_FAILED_FUNC_10  10682   /* Regr F/W-Failed Function 10 */
#define REGRESSION_DRV_FW_FAILED_FUNC_11  10683   /* Regr F/W-Failed Function 11 */
#define REGRESSION_DRV_FW_FAILED_FUNC_12  10684   /* Regr F/W-Failed Function 12 */
#define REGRESSION_DRV_FW_FAILED_FUNC_13  10685   /* Regr F/W-Failed Function 13 */
#define REGRESSION_DRV_FW_FAILED_FUNC_14  10686   /* Regr F/W-Failed Function 14 */
#define REGRESSION_DRV_FW_FAILED_FUNC_15  10687   /* Regr F/W-Failed Function 15 */
#define REGRESSION_DRV_FW_FAILED_FUNC_16  10688   /* Regr F/W-Failed Function 16 */
#define REGRESSION_DRV_FW_FAILED_FUNC_17  10689   /* Regr F/W-Failed Function 17 */
#define REGRESSION_DRV_FW_FAILED_FUNC_18  10690   /* Regr F/W-Failed Function 18 */
#define REGRESSION_DRV_FW_FAILED_FUNC_19  10691   /* Regr F/W-Failed Function 19 */
#define REGRESSION_DRV_FW_FAILED_FUNC_20  10692   /* Regr F/W-Failed Function 20 */
#define REGRESSION_DRV_FW_FAILED_FUNC_21  10693   /* Regr F/W-Failed Function 21 */
#define REGRESSION_DRV_FW_FAILED_FUNC_22  10694   /* Regr F/W-Failed Function 22 */
#define REGRESSION_DRV_FW_FAILED_FUNC_23  10695   /* Regr F/W-Failed Function 23 */
#define REGRESSION_DRV_FW_FAILED_FUNC_24  10696   /* Regr F/W-Failed Function 24 */
#define REGRESSION_DRV_FW_FAILED_FUNC_25  10697   /* Regr F/W-Failed Function 25 */
#define REGRESSION_DRV_FW_FAILED_FUNC_26  10698   /* Regr F/W-Failed Function 26 */
#define REGRESSION_DRV_FW_FAILED_FUNC_27  10699   /* Regr F/W-Failed Function 27 */

#define SCSI_4031_07_27_00                10700   /* Proc Operator-Wt Prot Not Rdy-07/27/00/02 */              // Unused in Platform
#define CHS_LBA_TRANSLATE_FAILED          10701   /* Drv CHS_LBA Translation Failed */

#define SERVO_DIE_TEMP_OUT_OF_RANGE       10710   /* Servo measured die temperature out of range */
#define SERVO_HDA_TEMP_OUT_OF_RANGE       10711   /* Servo measured HDA temperature out of range */
#define SERVO_I2C_COMM_FAILED             10712   /* Servo can not communicate with I2C reliably */

#define EXCEEDED_TEMPERATURE_LIMIT        10800    /* Drv SMART-Temperature Limit Exceeded */
#define EXCEEDED_BUZZ_CNT_LIMIT           10802    /* Drv SMART-Buzz count Limit Exceeded */
#define EXCEEDED_BAD_ID_LIMIT             10804    /* Drv SMART-Bad ID Limit Exceeded */
#define EXCEEDED_BAD_SAMP_LIMIT           10806    /* Drv SMART-Bad Sample Limit Exceeded */                   // SF2/3 T43, 44, 47, 189
#define EXCEEDED_NO_TMD_LIMIT             10808    /* Drv SMART-No TMD Limit Exceeded */
#define EXCEEDED_ONE_THIRD_SEEK_LIMIT     10810    /* Drv SMART-One-third Seek Limit Exceeded */
#define EXCEEDED_ONE_TRACK_LIMIT          10812    /* Drv SMART-One Track Limit Exceeded */
#define EXCEEDED_WRITE_FAULT_LIMIT        10814    /* Drv SMART-Write Fault Limit Exceeded */
#define EXCEEDED_READ_ERROR_LIMIT         10816    /* Drv SMART-Read Error Limit Exceeded */
#define EXCEEDED_TA_LIMIT                 10818    /* Drv SMART-TA Limit Exceeded */                           // SF2/3 T134
#define EXCEEDED_SEEK_ERROR_LIMIT         10820    /* Drv SMART-Seek Error Limit Exceeded */
#define EXCEEDED_TF_LIMIT                 10822    /* Drv SMART-TF Limit Exceeded */
#define EXCEEDED_ARE_LIMIT                10824    /* Drv SMART-ARE Limit Exceeded */
#define EXCEEDED_TA_WUS_LIMIT             10826    /* Drv SMART-TA Wus Limit Exceeded */
#define EXCEEDED_SPINUP_LIMIT             10827    /* Drv SMART-Spinups Limit Exceeded */
#define MULTIPLE_SMART_FRAME_ERRORS       10850    /* Drv SMART-Multiple Limits Exceeded */
#define QUEUE_NOT_ABORTED                 10851    /* Drv SMART-Command Queue Not Aborted */
#define PAGE_OR_SUBPAGE_NOT_FOUND         10852    /* Drv SMART-MSEN Page or Subpage Not Found */
#define INCORRECT_DRIVE_TYPE              10853    /* Incorrect Initiator Drive Type */                       // Not in SCSS
#define INCORRECT_SENSE_DATA              10854    /* Sense Data returned are not expected */                 // Not in SCSS

#define FC_ADDRESS_LINE_FAILED            10900    /* Drv Iface-FC Address Line Failed */
#define FC_ESI_NOT_ENABLED                10901    /* Drv Iface-FC ESI is NOT Enabled */
#define FC_ESI_ALREADY_ENABLED            10902    /* Drv Iface-FC ESI is Already Enabled */
#define CRC_NOT_DETECTED                  10903    /* Drv Iface-CRC Failed to Detect */
#define TOO_MANY_LOSS_COUNT               10904    /* Drv Iface-FC Loss Sync & Disparity Exc. */
#define START_JUMPER_IS_ON                10905    /* Start Jumper is ON */                                   // Not in SCSS
#define FASTIO_FAIL_SERVO_IN_TWIDDLE      10906    /* FASTIO failed since servo in Twiddle */
#define AOD_ZONE_HEAD_COMBO_INVALID       10907    /* Invalid Combination of head and zone for AOD*/
#define INVALID_ADAPTIVE_SETTING          10908    /* Invalid Adaptive Setting*/

#define REGRESSION_DRV_FW_FAILED_FUNC_31  11000    /* Regr F/W-Failed Function 31 */
#define REGRESSION_DRV_FW_FAILED_FUNC_32  11001    /* Regr F/W-Failed Function 32 */
#define REGRESSION_DRV_FW_FAILED_FUNC_33  11002    /* Regr F/W-Failed Function 33 */
#define REGRESSION_DRV_FW_FAILED_FUNC_41  11003    /* Regr F/W-Failed Function 41 */
#define REGRESSION_DRV_FW_FAILED_FUNC_42  11004    /* Regr F/W-Failed Function 42 */
#define REGRESSION_DRV_FW_FAILED_FUNC_43  11005    /* Regr F/W-Failed Function 43 */
#define REGRESSION_DRV_FW_FAILED_FUNC_51  11006    /* Regr F/W-Failed Function 51 */
#define REGRESSION_DRV_FW_FAILED_FUNC_52  11007    /* Regr F/W-Failed Function 52 */
#define REGRESSION_DRV_FW_FAILED_FUNC_61  11008    /* Regr F/W-Failed Function 61 */
#define REGRESSION_DRV_FW_FAILED_FUNC_62  11009    /* Regr F/W-Failed Function 62 */
#define REGRESSION_DRV_FW_FAILED_FUNC_71  11010    /* Regr F/W-Failed Function 71 */
#define REGRESSION_DRV_FW_FAILED_FUNC_72  11011    /* Regr F/W-Failed Function 72 */
#define REGRESSION_DRV_FW_FAILED_FUNC_73  11012    /* Regr F/W-Failed Function 73 */
#define REGRESSION_DRV_FW_FAILED_FUNC_74  11013    /* Regr F/W-Failed Function 74 */
#define REGRESSION_DRV_FW_FAILED_FUNC_75  11014    /* Regr F/W-Failed Function 75 */
#define REGRESSION_DRV_FW_FAILED_FUNC_76  11015    /* Regr F/W-Failed Function 76 */
#define REGRESSION_DRV_FW_FAILED_FUNC_77  11016    /* Regr F/W-Failed Function 77 */
#define REGRESSION_DRV_FW_FAILED_FUNC_78  11017    /* Regr F/W-Failed Function 78 */
#define REGRESSION_DRV_FW_FAILED_FUNC_79  11018    /* Regr F/W-Failed Function 79 */
#define REGRESSION_DRV_FW_FAILED_FUNC_80  11019    /* Regr F/W-Failed Function 80 */
#define REGRESSION_DRV_FW_FAILED_FUNC_81  11020    /* Regr F/W-Failed Function 81 */
#define REGRESSION_DRV_FW_FAILED_FUNC_82  11021    /* Regr F/W-Failed Function 82 */
#define REGRESSION_DRV_FW_FAILED_FUNC_83  11022    /* Regr F/W-Failed Function 83 */
#define REGRESSION_DRV_FW_FAILED_FUNC_84  11023    /* Regr F/W-Failed Function 84 */
#define REGRESSION_DRV_FW_FAILED_FUNC_85  11024    /* Regr F/W-Failed Function 85 */
#define REGRESSION_DRV_FW_FAILED_FUNC_91  11025    /* Regr F/W-Failed Function 91 */
#define REGRESSION_DRV_FW_FAILED_FUNC_92  11026    /* Regr F/W-Failed Function 92 */
#define REGRESSION_DRV_FW_FAILED_FUNC_93  11027    /* Regr F/W-Failed Function 93 */
#define REGRESSION_DRV_FW_FAILED_FUNC_94  11028    /* Regr F/W-Failed Function 94 */
#define REGRESSION_DRV_FW_FAILED_FUNC_95  11029    /* Regr F/W-Failed Function 95 */
#define REGRESSION_DRV_FW_FAILED_FUNC_96  11030    /* Regr F/W-Failed Function 96 */
#define REGRESSION_DRV_FW_FAILED_FUNC_97  11031    /* Regr F/W-Failed Function 97 */
#define REGRESSION_DRV_FW_FAILED_FUNC_98  11032    /* Regr F/W-Failed Function 98 */
#define REGRESSION_DRV_FW_FAILED_FUNC_99  11033    /* Regr F/W-Failed Function 99 */
#define REGRESSION_DRV_FW_FAILED_FUNC_100 11034    /* Regr F/W-Failed Function 100 */
#define REGRESSION_DRV_FW_FAILED_FUNC_101 11035    /* Regr F/W-Failed Function 101 */
#define EXCEEDED_TK0_OFFSET_LIMIT         11036    /* Svo Cal-Track Zero Offset Limit Exceeded */              // SF2/3 T185
#define NO_CONFIG_FROM_CMS                11037    /* Tester Network-Cant Get Cfg From CM */
#define NO_RECIPE_BUILT_FROM_CONFIG       11038    /* Tester Network-Cant Build Recipe from Cfg */
#define NO_CMS_SERVER_LOGIN               11039    /* Tester Network-Cant FTP files from CMS */
#define NO_FILES_FROM_CMS_SERVER          11040    /* Tester Network-File not Found on CMS */
#define FILE_FTP_TO_CMS_FAILED            11041    /* Tester Network-Cant FTP Files to CM */
#define CONFIG_CLONE_ON_CMS_FAILED        11042    /* Tester Comm Mgr-Cant Clone Config on CM */
#define INVALID_RECIPE                    11043    /* Process ME-Invalid Recipe */
#define BAD_PLUG_BITS                     11045    /* Tester Misc-Bad Plug Bits */
#define CELL_PROCESS_DIED                 11046    /* Process Misc-Cell Process Died */
#define NO_FACTORY_TEST_OBJECT            11047    /* Process Misc-Can't Make Factory Test Obj */
#define BAD_CELL_STATUS_FLAGS             11048    /* Tester Misc-Bad Cell Status Flags */
#define SYSTEM_TIMED_OUT                  11049    /* Tester Timeout-Test Time Limit Exceeded */
#define SAP_TRACK_VALUE_INVALID           11050    /* Svo Cal- Invalid SAP val TPI or CAL_CYL */
#define BAD_HEAD_SKEW_VALUE               11051    /* Svo Cal- Head skew value low / bad */                    // SF2/3 T43, 189
#define TEMPERATURE_DELTA_EXCEEDED        11052    /* Drv Misc-PCBA/HDA Temp Delta Exceeded */
#define CACHED_CONFIG_NOT_FOUND           11053    /* Cached configuration not found */
#define CONFIG_NOT_FOUND                  11054    /* CMS Configuration not found */
#define CMS_TIMEOUT                       11055    /* CMS Timeout */
#define GENERAL_FAILURE                   11056    /* CMS General Failure */
#define CONNECTION_REFUSED                11057    /* CMS Connection refused */
#define SOCKET_ERROR                      11058    /* CMS Socket error */
#define SPT_HOST_NOT_FOUND                11059    /* CMS Socket error */
#define CM_CPY_TEMP_RAMP_FAILURE          11060    /* Temperature Ramp failure */
#define CM_CPY_BAD_RISER_DATA             11061    /* Bad Riser Data */
#define CM_SPY_DUP_CELL_START             11062    /* Duplicate cell start */
#define CM_SPY_CPY_FORK_FAILED            11063    /* Cell Py Fork failed */
#define BDSMPS_IN_XFR_FUNC_MEASURE        11064    /* Servo Zap-Xfr Func Measure Bad Samples */                // SF2/3 T175
#define NO_TEST_SEQUENCE                  11065    /* Can not get the test sequence */
#define PLIST_NOT_MAPPED                  11066    /* Drv H/W Err P-List not Mapped */
#define DEFECT_IN_RZ_SPARE_REGION         11067    /* Drv H/W Err-Defect in RZ Spare Region */
#define EXCEEDS_STD_DEV_LIMIT             11068    /* Svo VGA - Standard deviation exceeds spec */             // SF2/3 T25, 103
#define OBSERVER_SECTOR_LIMIT             11069    /* Svo Pattern-Failed Observer Sect Err Lmt */              // SF2/3 T163
#define SKEW_TIMING_DELTA_OOS             11070    /* Svo Cal- Skew Timing Delta Out Of spec */
#define BAD_RAW_TRACK_ID                  11071    /* Svo Cal- Bad Raw Track ID For Drive */
#define PS1_PS2_POLARITY_REVERSED         11072    /* Svo PES - PS1 PS2 polarity reversed */                   // SF2/3 T187
#define EXEEDS_TRK_SPACING_FAIL_LIMIT     11073    /* Svo Def's-Exceeds Trk Spacing Fail Limit */              // SF2/3 T187
#define CM_CPY_XY_METHOD_FAILED           11074    /* Process Misc-Xyratex Cell-Control Method failure */
#define CM_CPY_KILL_CELL                  11075    /* Process Misc-User killed CellPy */
#define CM_CPY_CELL_NOT_ONLINE            11076    /* Process Misc-Cell is not online */
#define CM_CPY_BAD_SERIAL_COMM            11077    /* Process Misc-Bad serial communications */
#define CM_CPY_WRONG_PYTHON_VERSION       11078    /* Process Misc-Wrong Python Version */
#define BAD_RIM_TYPE                      11079    /* Tester Misc Invalid/Missing RIM Type */
#define NO_CONFIG_IN_CMS                  11080    /* Tester Misc No configuration in CMS */
#define CM_CPY_HOST_COMM_FAILED           11081    /* Tester Misc CM to Host comm. failure */
#define HOST_CM_COMM_FAIL                 11082    /* Tester Misc Host to CM comm failure */
#define DC_ERASE_SECOND_PATTERN_FAILURE   11083    /* Wt DC Erase of MDW second pattern Failed */
#define UPDATE_ETF_FAIL_DC_ERASE_2ND_PATT 11084    /* Wt/Rd Update ETF/DC Erase of MDW 2nd patt Failed */
#define EXCEEDED_HIDDEN_READ_ERROR_LIMIT  11085    /* Drv SMART-Hidden Read Error Limit Exceeded */
#define ETF_RAP_CRC_FAILURE               11086    /* DRV F/W-RAP CRC Failure */
#define CM_CPY_SERIAL_PROTOCOL_ERROR      11087    /* Tester Misc Serial Protocol Error (CM/Cell) */
#define CM_CPY_SERIAL_TIMEOUT             11088    /* Tester Misc Serial Timeout (CM/Cell) */
#define CM_CPY_SERIAL_OVERFLOW            11089    /* Tester Misc Serial Overflow (CM/Cell) */
#define CM_SCRIPT_COMPILE_ERROR           11090    /* Process M.E. Script compile Error */
#define MODE_PAGE_19_FLASH_ERR            11091    /* Drv F/W Mode Page 19 Flash Error */
#define EXCEEDED_AMPL_LIMIT               11092    /* Svo Misc-Amplitude Limit Exceeded */                     // SF2/3 T180, 186
#define MEDIA_DAMAGE_CROSSES_CYL_RANGE    11093    /* Wt/Rd Def's-Media Damage cross Cyl Range */              // SF2/3 T117
#define BAD_FLASH_MFG_DEV_ID              11094    /* Drv PCBA - Bad Flash Man./Dev. ID */
#define UNABLE_TO_ID_FLASH                11095    /* Drv PCBA - Fail to get Flash Man/Dev ID */
#define INSUFFICIENT_PZT_STROKE           11096    /* Svo Cal-Insufficient PZT stroke */
#define SCSI_4031_01_0B_01                11097    /* Drv F/W-01/0B01 Specified Temp Exceeded */
#define SCSI_4031_04_80_86                11098    /* Rd H/W Err-04/80/86/xx IOEDC Err on Read */
#define SCSI_4031_04_80_87                11099    /* Wt H/W Err-04/80/87/xx IOEDC Err on Wt */
#define SCSI_4031_06_29_01                11100    /* Drv Startup-06/29/01/01 Pwr On Reset */
#define LIP_FAILED                        11101    /* Drv Iface-FC LIP failed, no comm */
#define SDBP_COMMAND_FAILED               11102    /* Drv F/W-SDBP Command Failed */
#define CM_CPY_CELL_FIRMWARE_ERROR        11103    /* Tester CM Cell Firmware Error */
#define CM_CPY_VCLIMIT_TRIP               11104    /* Tester CM voltage/current limit trip */
#define CM_CPY_INTERLOCK_TRIP             11105    /* Tester CM Interlock trip (fan/hotplug) */
#define CM_CPY_FOF_KILL_CELL              11106    /* Tester CM cell status reg indicates an error */
#define UNSUPPORTED_DRIVE                 11107    /* Drive type is not supported on this Line */              // Shared mk_rep
#define SINGLE_STAGE_ACTUATOR             11108    /* Can't enter single stage actuator mode */
#define CANT_READ_THERMISTER              11109    /* Can't read the thermister value from the drive*/         // SF2 diagapi
#define PREAMP_FILE_ERROR                 11110    /* Proc M.E - Error in PREAMP.TXT */
#define TOO_MANY_PREAMPS_DEFINED          11111    /* Proc M.E - Too Many Preamps Defined */
#define TOO_MANY_CYLINDER_RETRIES         11112    /* Proc M.E - Too Many Cylinder Retries */
#define FLY_HEIGHT_DELTA_EXCEEDED         11113    /* Proc M.E - Fly Height Delta Exceeded */
#define NORMALIZED_RATIO_DELTA_EXCEEDED   11114    /* Proc M.E - Normalized Ratio Delta Exceeded */
#define POLARITY_SWITCHED                 11115    /* Drv Head - Polarity Switched */                          // SF2/3 T126
#define EXCEEDS_JOG_ERROR_FAIL_LIMIT      11116    /* Svo Misc - Exceeds Jog Error Fail Limit */               // SF2/3 T187
#define MSE_DELTA_EXCEEDED                11117    /* Drv Head - Bias CQM MSE Delta Exceeded */
#define NON_SELECTED_SET_FAILED           11118    /* Drv Misc-Non Selected Ordered Set fails */
#define HIGH_LIMIT_TEST_FAILED            11119    /* Drv Misc-High Limit Test fails */
#define LOW_LIMIT_TEST_FAILED             11120    /* Drv Misc-Low Limit Test fails */
#define HARD_RESET_FAILED                 11121    /* Drv Misc-Hard Reset Test fails */
#define MAX_SEEK_TIME_DELTA_EXCEEDED      11122    /* Proc Misc. - Max Seek Time Delta Exceeded */
#define MIN_SEEK_TIME_DELTA_EXCEEDED      11123    /* Proc Misc. - Min Seek Time Delta Exceeded */
#define AVE_SEEK_TIME_DELTA_EXCEEDED      11124    /* Proc Misc. - Ave Seek Time Delta Exceeded */
#define DELTA_PMSE_FAILED                 11125    /* Proc Misc. - Delta PMSE Failed */
#define CQM_DELTA_EXCEEDED                11126    /* Drv Head - CQM Delta Exceeded */                         // SF2/3 T195
#define MAX_ITERATION_EXCEEDED            11127    /* Svo Pes.- Max Iteration Exceeded */
#define CACHE_EXPIRED                     11128    /* Tester Network- Cached Config Expired */
#define RESULTS_PROCESSING_ERROR          11129    /* Tester Misc- Error Processing Results */
#define SCSI_4031_01_0C_01                11130    /* Wt Err Rate-01/0C01 Wt Rec w/AutoRealloc */
#define SCSI_4031_03_14_01                11131    /* Rd Unrec Err-03/1401 Record Not Found */
#define SCSI_4031_06_5D                   11132    /* Drv SMART-06/5D Fail Pred Threshold Exc */
#define DELTA_PES_EXCEEDED                11133    /* Drv Head - Delta PES Exceeded */                         // SF2/3 T35
#define INDETERMINATE_POLARITY            11134    /* Drv Head - Indeterminate Polarity */
#define TD_BER_EXCEEDED                   11135    /* Rd Err Rate-Thermal Decay BER Exceeded */
#define LOW_CQM_DATA_POINTS               11136    /* Drv Head-Low CQM Data Points */
#define BAD_UNZAPPED_TRKS_LIMIT_EXCEEDED  11137    /* Svo ZAP-Bad/Unzapped Trks Limit Exceeded */
#define PARTICLE_DAMAGE                   11138    /* Wt/Rd Err Rate- Adjacent Trk Unrec Error */
#define PMSE_DELTA_EXCEEDED               11139    /* Drv Head - B2D vs SPT PMSE Delta Exceeded */
#define SVGA_POS_DELTA_EXCEEDED           11140    /* Svo Misc - SVGA Positive Delta Exceeded */
#define SVGA_NEG_DELTA_EXCEEDED           11141    /* Svo Misc - SVGA Negative Delta Exceeded */
#define SVGA_POS_MAX_SPEC_EXCEEDED        11142    /* Svo Misc - SVGA Positive Maximum Spec Exceeded */
#define SVGA_NEG_MAX_SPEC_EXCEEDED        11143    /* Svo Misc - SVGA Negative Maximum Spec Exceeded */
#define SPECIFIED_TEMP_EXCEEDED           11144    /* Drv Startup-06/0B/01/xx Temp Exceeded */
#define SCSI_4031_02_04_03                11145    /* Svo Startup-02/0403 Drv Not Rdy Help Req */
#define FAILED_DHDI                       11146    /* Wt/Rd Err Rate - DHDI Error */
#define FAILED_PARTICLE_SCRATCH           11147    /* Wt/Rd Err Rate - Particle Scratch Error */
#define B2D_SPT_CQM_DELTA_EXCEEDED        11148    /* Drv Head - B2D vs SPT CQM Delta Exceeded */
#define B2D_SPT_SVGA_DELTA_EXCEEDED       11149    /* Wt/Rd Cal - Svo VGA Delta Exceeded */
#define OPEN_LATCH_RETRIES_EXCEEDED       11150    /* Svo Startup-Open Latch Retries Exceeded */
#define SVO_AGC_LIMIT_EXCEEDED            11151    /* Svo Def's - Servo AGC Limit Exceeded */
#define DELTA_SIGMA_EXCEEDED              11152    /* Drv Head - Delta Sigma Limit Exceeded */                 // SF2/3 T35, 103
#define FAIL_WIJIA_MINMAX                 11153    /* Drv Head - WIJIA, Delta Max-Min Spec */                  // SF2/3 T103
#define BER_DELTA_LIMIT_EXCEEDED          11154    /* Drv Head - BER Delta Limit Exceeded */
#define SLOPE_LIMIT_EXCEEDED              11155    /* Drv Head - Slope Limit Exceeded */
#define SMART_TIME_STAMP_EXCEEDED         11156    /* Drv SMART - Time Stamp Exceeded */
#define POSITIVE_DELTA_MIN_VGA_SPEC_FAILS 11157    /* Wt/Rd Cal-Pos Delta Min VGA Spec Fails */
#define NEGATIVE_DELTA_MAX_VGA_SPEC_FAILS 11158    /* Wt/Rd Cal-Neg Delta Max VGA Spec Fails */
#define VGA_MIN_SPEC_EXCEEDED             11159    /* Wt/Rd Cal-VGA Exceeded Minimum Spec */
#define HEATER_REG_NOT_SET                11160    /* Svo Misc-Writer Heater Values not set in SAP */          // SF2 T27
#define HEATER_FAILURE                    11161    /* Wt/Rd Flt-Writer Heater Shorted or Open Fault */         // SF2/3 T27
#define SPINDLE_HARM_OOL                  11162    /* Drv Misc- Spindle Harmonics OOL */
#define SP240_RESULT_FILE_WRITE_ERROR     11163    /* Wt Misc-SPT Result File Write Error */
#define SPINDLE_MOTOR_FAILURE             11164    /* Drv Misc-Spindle Motor Failure */
#define RISER_TYPE_MISMATCH               11165    /* Tester Misc-Host & CM RIM_Type Mismatch */
#define SCRIPT_TIMEOUT                    11166    /* Tester Timeout-Exceeds Script Time Limit */
#define CHECKSUM_MISMATCH                 11167    /* Tester Misc- Checksum Mismatch */
#define UNEXPECTED_DATA                   11168    /* Tester Misc- Unexpected Data Packet */                   // SF3 T152
#define RIMPROXY_EXCEPTION                11169    /* Tester RIM- Comm. error on FX2 FIFO */
#define FAILS_ADAPTIVE_GAIN_BOUNDARIES    11170    /* Wt/Rd Cal-Fails Adaptive Gain Boundaries */              // SF3 T151
#define NEG_DELTA_VGA_TA_SPEC_EXCEEDED    11171    /* Wt/Rd Cal-Neg Delta VGA w/TA Spec Exceeded */
#define VGA_CQM_SPEC_EXCEEDED             11172    /* Wt/Rd Cal-VGA and CQM Spec Exceeded */                   // SF2/3 T195
#define PHY_NOT_READY                     11173    /* Drv Iface-Sas Phy not ready */
#define SYS_PLUS_COMM_ERROR               11175    /* Tester PwrTemp Ctrl-Temperature Ctlr Err */              // Originally: Tester PwrTemp Ctrl-SysPlusCtlr Communication Error */
#define PERCENT_DIFF_EXCEEDED             11177    /* Drv Head - Percent Difference Exceeded */                // SF2/3 T35
#define CAPACITY_BELOW_REQUIREMENT        11179    /* Drv Misc-Capacity below requirement */
#define EXCEEDS_NR_STDEV_LIMIT            11183    /* Svo VGA - NR_STDEV exceeds spec */                       // SF2/3 T103
#define EXCEEDS_R_STDEV_LIMIT             11184    /* Svo VGA - R_STDEV exceeds spec */                        // SF2/3 T103
#define NO_DEPOP_ATTRIBUTE                11185    /* Proc M.E. - No Depop Attribute for T81 */
#define MIN_CLEARANCE_NOT_MET             11186    /* Drv Head - Min Clearance Not Met */
#define EC04808B                          11190    /* Drv Iface-04/808B Com Buf FIFO Parity Er */
#define EC0B4B03                          11191    /* Drv Timeout-0B/4B03 SAS ACK/NAK T-O */
#define EC020411                          11192    /* Svo Startup-02/0411 Not Ready No Enable */
#define EC048089BE                        11193    /* Rd H/W Err-04/8089BE IOEDC Err on Read */
#define EC04808C                          11194    /* Drv H/W Err-04/808C DFrame Buf Parity Er */
#define POST_RV_GAIN_VALUE_OOS            11195    /* Post RV Gain value out of spec */
#define RV_GAIN_VALUE_OUT_OF_SPEC         11196    /* Initial RV Gain value out of spec */
#define MODULATION_CYCLE_LIMIT_EXC        11198    /* Wt/Rd Def's-Modulation Cycle Limit Exc */
#define EC0B4B04                          11199    /* Drv Iface-0B/4B04 Aborted Cmd Nak Rec'ed */
#define TABLE_ROW_DATA_ERROR              11200    /* Drv F/W-Report_table_row() Error*/                       // Shared DIN_DEX
#define DISABLED_IN_THIS_DOWNLOAD         11203    /* Proc M.E. - Test disabled in this download */            // SF2/3 T166, 176, 180, 187, 231
#define FC_BAD_RSP_CODE                   11204    /* Drv Iface-FC Bad RSP Code */
#define INVALID_HDA_PN                    11205    /* Tester Misc- Invalid HDA Part Number */
#define MAX_CLEARANCE_EXCEEDED            11206    /* Drv Head-Max Clearance Exceeded*/
#define APM_READ_FAILED                   11207    /* Drv F/W-Adaptive Parameters Read Failed */               // SF2 diagapi, T172, 210
#define BAD_TCM                           11212    /* Drv PCBA-TCM Verify Fail */
#define SPINUP_CURRENT_FAILURE            11213    /* Drv Startup - Spinup Current Exceeds Spec*/
#define DAC_GAIN_DIFF_TOO_HIGH            11214    /* Svo Cal - DAC Gain Diff Too High*/
#define DRIVE_ECCENTRICITY_FAILURE        11215    /* Drv Eccentricity Exceeds Limit */                        // SF2/3 T47
#define VCAT_AC_AUDIT_FAILURE             11216    /* Drv Vcat AC Calibration Audit Failed */                  // SF2/3 T47
#define WRITER_HEATER_DIFF_EXCEEDED       11217    /* Wt/Rd Flt-Writer Heater Difference Exceeded */           // SF2/3 T35
#define WRITE_ERROR_SENSEKEY_030C         11218    /* Wt/Rd Sense Key 03/0C */
#define EAW_VGA_STD_DELTA_EXCEEDED        11220    /* Drv EAW Vga STDEV Delta Exceeds Limit */                 // SF2/3 T103
#define EAW_VGA_AVG_DELTA_EXCEEDED        11221    /* Drv EAW Vga Average Delta Exceeds Limit */               // SF2/3 T103
#define MIN_VALID_LIN_TABLES_NOT_MET      11222    /* Drv F/W-Min. valid linearization tables not met. */      // SF2/3 T150
#define INCORRECT_SERVO_MODE              11223    /* Proc M.E.-Incorrect Servo Mode(s) Selected */            // SF2/3 servo
#define MAX_GAIN_CORRECTION_FAILURE       11224    /* Drv F/W-Max. gain correction exceeeded */                // SF2/3 T150
#define EXCESSIVE_RRO_VARIATION           11225    /* Svo PES - Exessive RRO Variation */                      // SF2/3 T46
#define INSUFFICIENT_TRACK_SPACE_AT_ID    11226    /* Svo Cal - Insufficient Trk Space At ID */                // SF2/3 T185
#define INVALID_SCN                       11227    /* Proc Operator - Invalid SCN */
#define DRIVE_FW_FLASH_LED_DETECTED       11231    /* Flash LED detected */
#define EXCEEDED_BGMS_FAILURE_LIMIT       11232    /* Exceeded BGMS Failure Limit */                           // SF3 core
#define PZT_CAL_TEMP_DELTA_FAILED_SPEC    11233    /* Tester - PZT Cal Temp Delta Failed Spec  */
#define DELTA_LOG_CQM_EXCEEDED            11234    /* Drv Head-Delta Log CQM Exceeded */
#define DRIVE_AUTO_DUMP_FAILURE           11235    /* Drv Misc - Drv Auto Dump Failure */
#define DUPLICATE_TRACK_ID                11236    /* Svo Pattern-Duplicate Track ID */
#define SFT_SIM_PRESPINNING_FAILURE       11237    /* Drv Spinup-SIM Pre-Spinning Init Failed */               // SF2/3 main, T1
#define SFT_SIM_SPINNINGUP_FAILURE        11238    /* Drv Spinup-SIM Spinning Up Init Failed */                // SF2/3 main, T1
#define SFT_SIM_INVALID_PARTITION_RANGE   11239    /* Drv Spinup-SIM Invalid Partition Range */                // SF2/3 main, T1
#define MAX_STE_OUT_OF_SPEC               11240    /* Drv Misc - Max STE out of Spec */
#define ATI_ID_OUT_OF_SPEC                11241    /* Drv Misc - ATI_ID out of Spec */
#define ATI_OD_OUT_OF_SPEC                11242    /* Drv Misc - ATI_OD out of Spec */
#define PZT_DAC_GAIN_FAILED_SLOPE_SPEC    11243    /* PZT Dac Gain Failed Slope Spec */                        // Originally: Tester Pwr/Temp Ctrl - PZT DAC Gain Failed Slope Spec
#define UNLATCHED_FAILED                  11245    /* Svo Unlatched Failed */
#define LOOP_CODE_32                      11246    /* Svo Loop Code 32 */
#define SPIN_MOTOR_FAILED                 11247    /* Svo Spin Motor Failed */
#define SUM_SQRT_AMPL_WIDTH_EXCEEDED      11250    /* Wt/Rd T.A.s-Exceeded Sum SqRt Ampl Width */              // SF2 T134
#define TARGET_OPT_BER_OUT_OF_SPEC        11254    /* Wt/Rd Target Optimize BER out of Spec */
#define PMSE_CQM_FAILED                   11255    /* Proc Misc. - PMSE and CQM Failed */
#define INITATOR_FW_FLASH_LED_DETECTED    11256    /* IO Flash LED detected */
#define BACKOFF_HTR_DAC_EXCEEDED          11258    /* Backoff HTR DAC exceeded */                              // T75
#define PZT_MALFUNCTION                   11259    /* PZT is not responding */
#define PZT_POLARITY_ERROR                11260    /* PZT polarity error*/

#define GAMMA_COEFS_ALL_ZERO              12500    /* Gamma Coefficients All 0 */                                  // SF3 T191
#define EXCEED_PLIST                      12751    /* WT/Rd Defs Exceeded Plist Spec */
#define SEQ_READ_FAILED                   12962    /* Proc Misc - Sequential Read failed */
#define SEQ_WRITE_FAILED                  12963    /* Proc Misc - Sequential Write Failed */
#define HEATER_RESISTANCE_LIMIT           12964    /* Heater resistance exceeds test limit */
#define FAFH_TEST_SERPENTS_NOT_DEFINED    12965    /* FAFH Test Serpents are not present in format tables */
#define SED_BAND_RANGE_START_ERROR        12966    /* Band range start value incorrect  */
#define SED_BAND_RANGE_LENGTH_ERROR       12967    /* Band range length value incorrect  */
#define SED_READ_LOCK_ENABLED_ERROR       12968    /* Band ReadLockeEnabled value incorrect  */
#define SED_WRITE_LOCK_ENABLED_ERROR      12969    /* Band WriteLockEnabled value incorrect  */
#define SED_READ_LOCK_ERROR               12970    /* Band ReadLocked value incorrect  */
#define SED_WRITE_LOCK_ERROR              12971    /* Band WriteLocked value incorrect  */
#define SED_LOCK_ON_RESET_ERROR           12972    /* LockOnReset value incorrect  */
#define SED_PORT_LOCK_ERROR               12973    /* Port Lock value incorrect  */
#define BAND_ENABLED_COMPARE_ERROR        12974    /* Band enabled value doesn't match expected value */
#define CRRO_EXCEED_LIMIT                 12975    /* T046 Min or Max CRRO EXCEED LIMIT */
#define SECURITY_DRIVE_TYPE_INCORRECT     12976    /* Unexpected security type reported via Discovery */
#define EXCEED_RRO_LOW_LIMIT              12977    /* RRO Spectral exceed low limit*/                              // T175
#define DETCR_FAILED                      12978    /* Detcr Failure*/
#define EXCEED_ODID_JOG_ERROR_LIMIT       12979    /* ODID Jog Error is too big */
#define EXCEED_ZIPPERZONE_JOG_ERROR_LIMIT 12980    /* Zipperzone Jog Error is too big */
#define EXCEED_ODID_DC_ERROR_LIMIT        12981    /* ODID DC Error is too big */
#define EXCEED_ZIPPERZONE_DC_ERROR_LIMIT  12982    /* Zipperzone DC Error is too big */

/******************************************************************************
* Main category:  Platform SATA Error Codes
* Subcategory:
* Range:          14000 - 14199
******************************************************************************/
/*   These error codes reserved for Platform SATA
******************************************************************************/
#define ATA_GENERAL_ERROR                 14001    /* SATA Misc - undefined error */
#define ATA_FAILED_DIAGNOSTIC             14002    /* SATA Misc - failed diagnostic */
#define ATA_NOT_SUPPORTED                 14003    /* SATA Misc - not supported */
#define ATA_CMDTIMEOUT                    14004    /* SATA Misc - Command timeout */
#define ATA_WAIT_FOR_DRDY                 14005    /* SATA Misc - wait for DRDY */
#define ATA_WAIT_FOR_NOT_BUSY             14006    /* SATA Misc - wait for BUSY */
#define ATA_WAIT_FOR_DRQ                  14007    /* SATA Misc - wait for DRQ */
#define ATA_WAIT_FOR_NOT_DRQ              14008    /* SATA Misc - wait for !DRQ */
#define ATA_WAIT_FOR_NOT_DMA_ARQ          14009    /* SATA Misc - wait for !DMA DRQ */
#define ATA_WAIT_FOR_DMA_NOT_BUSY         14010    /* SATA Misc - wait for DMA !BUSY */
#define ATA_WAIT_FOR_DRIVE_IRQ            14011    /* SATA Misc - wait for IRQ */
#define ATA_BAD_BLOCK                     14012    /* SATA Misc - bad block */
#define ATA_UNCORRECTABLE_ERROR           14013    /* SATA Misc - uncorrectable data error */
#define ATA_MEDIA_CHANGED                 14014    /* SATA Misc - media changed */
#define ATA_SECTOR_NOT_FOUND              14015    /* SATA Misc - sector not found */
#define ATA_MEDIA_CHANGE_REQ              14016    /* SATA Misc - media change requested */
#define ATA_ABORTED_COMMAND               14017    /* SATA Misc - aborted command */
#define ATA_TRACK_ZERO_NOT_FOUND          14018    /* SATA Misc - track 0 not found */
#define ATA_ADDRESS_MARK_NOTFOUND         14019    /* SATA Misc - address mark not found */
#define ATA_BAD_CHS                       14020    /* SATA Misc - bad CHS */
#define ATA_RETRY_FLAG_SET                14021    /* SATA Misc - retry flag set */
#define ATA_INVALID_TARGET                14022    /* SATA Misc - invalid target */
#define ATA_INVALID_VENDOR_BYTE           14023    /* SATA Misc - invalid vendor byte */
#define ATA_INVALID_BLOCK_COUNT           14024    /* SATA Misc - invalid block count */
#define ATA_INVALID_SECTOR_COUNT          14025    /* SATA Misc - invalid sector count */
#define ATA_UDMA_CRC_ERROR                14026    /* SATA Misc - UMDA CRC error */
#define ATA_DATA_MISCOMPARE               14027    /* SATA Misc - data miscompare */
#define ATA_EXCESSIVE_INTERRUPTS          14028    /* SATA Misc - IRQ timed out */
#define ATA_DRIVEFAULT                    14029    /* SATA Misc - driver has encountered a problem */
#define ATA_UDMATXBUSY                    14030    /* SATA Misc - ATA controler busy doing UDMA transfer */
#define ATA_NOTREADY                      14031    /* SATA Misc - drive not ready to check status */
#define ATA_INVALIDDATADIRECTION          14032    /* SATA Misc - invalid data direction */
#define ATA_DASPSTUCK                     14033    /* SATA Misc - DASP line stuck */
#define ATA_BUFFERTOOSMALL                14034    /* SATA Misc - buffer too small */
#define MAX_CCT_TIME_EXCEEDED             14035    /* SATA Misc - Max CCT time exceeded */
#define POWER_ON_WAIT_TIME_EXCEEDED       14036    /* SATA Misc - Power on wait time exceeded */
#define FAILED_IO_SPEED                   14037    /* Drv Iface - failed to set interface speed */
#define BLUENUN_RETRIES_EXCEEDED          14038    /* SATA Misc - BlueNun Retries Exceeded */
#define STE_INITIAL_BER_NOT_MET           14039    /* Drv Misc- STE Track Initial BER Not Met */
#define ATI_INITIAL_BER_NOT_MET           14040    /* Drv Misc- ATI Track Initial BER Not Met */
#define STE_BER_COUNT_EXCEEDED            14041    /* Drv Misc - STE Track BER count exceeded */
#define NO_LBA_INFO_RETURNED              14042    /* Drv Misc - No LBA Information in Registers*/
#define FDE_CAPTURE_PERSISTENT_DATA_FAIL  14043    /* FDE Capture Persistent Data Failed */
#define FDE_SERVER_COM_FAILURE            14044    /* FDE TDCI Server Communication Failure */
#define FDE_REVERT_SP_FAILED              14045    /* FDE RevertSP Failed */
#define SATA_SCT_STATUS_ERROR             14046    /* SATA Misc - SCT status error */
#define SUPERCAP_LIMITS_EXCEEDED          14047    /* SATA Misc - Limits for SuperCap are exceeded */
#define OCLIM_LIMIT_1_EXCEEDED            14048    /* Drv-Misc - OCLim Limit 1 Exceeded */
#define OCLIM_LIMIT_2_EXCEEDED            14049    /* Drv-Misc - OCLim Limit 2 Exceeded */
#define OCLIM_LIMIT_3_EXCEEDED            14050    /* Drv-Misc - OCLim Limit 3 Exceeded */
#define INVALID_BANDOM_INFO               14051    /* Drv-Misc - No Bandom Info Available */
#define LBA_NOT_IN_BAND                   14052    /* Drv-Misc - LBA Not In A Current Band */
#define SATA_SDBP_INPUT_ERROR             14053    /* Drv Misc - SDBP Input Error */
#define XFR_SIZE_BAND_SIZE_MISMATCH       14054    /* Drv-Misc - Xfr Size too Large for Band Size  */
#define EXCEEDED_SWD_DVGA_LIMIT           14055    /* Drv SMART-SWD DVGA Limit Exceeded  */
#define EXCEEDED_SWD_RVGA_LIMIT           14056    /* Drv SMART-SWD RVGA Limit Exceeded  */
#define EYE_MEASUREMENT_LIMITS_FAIL       14057    /* Drv Iface - failed eye measurement */
#define FEATURE_INCOMPATIBILITY           14058    /* Drv Misc - Incompatible Saved Data */
#define HOST_OPERATION_NOT_POSSIBLE       14059    /* SATA Misc - Requested Host Operation is not possible */
#define INTERNAL_DIAG_PORT_UNLOCK_FAIL    14060    /* SATA Misc - Internal TDCI Diagnostic Port Unlock Failed */

/******************************************************************************
* End:  Platform SATA Error Codes
* Subcategory:
* Range:          14000 - 14199
******************************************************************************/

#define MISSING_REQUIRED_PARAM            14207    /* Drv FW - Missing required user test parameter */         // SF2/3 T103
#define FORMAT_SYSTEM_AREA_FAILED         14501    /* Wt/Rd Misc-Format System Area Failed */                  // SF2/3 T149
#define UNABLE_TO_DETECT_ALL_DRIVES       14503    /* Drv Misc - Unable to Detect All Drives */
#define HEC_FAILED                        14506    /* Drv Misc - HEC Failed */
#define DXC_FAILED                        14507    /* Drv Misc - DXC Failed */
#define RAND_RD_FAILED                    14508    /* Drv Misc - Random Read Failed */
#define RAND_WRT_FAILED                   14509    /* Drv Misc - Random Write Failed */
#define RAND_RD_HEC_DXC_FAILED            14510    /* Drv Misc - Rand Read with HEC/DXC Failed */
#define RAND_WRT_HEC_DXC_FAILED           14511    /* Drv Misc - Rand Wrt with HEC/DXC Failed */
#define AP_PROGRAM_FAILED                 14512    /* Drv Misc - Application Program Failed */
#define PSD_THRESH_EXCEEDED               14519    /* Drv Head - PSD THRESH EXCEEDED */                        // SF3 T35
#define BLUENUN_SCAN_FAILED               14520    /* Proc Misc. - BlueNun Scan Failed */
#define GENERAL_SIM_READ_FAILURE          14524    /* Drv F/W - General SIM Read Failure */
#define RSP_INFO_PRESENT                  14532    /* Drv Misc - RSP INFO PRESENT */
#define ZAP_DATA_ERR_PER_HEAD_LIMIT       14533    /* Svo ZAP - WD/RD Error Per Hd Limit */
#define ALPA_IS_INVALID                   14534    /* Drv Misc - Invalid Alpa */
#define MISSING_ALPA                      14535    /* Drv Misc - Missing Alpa */
#define CRRO_LEVEL_TOO_HIGH               14536    /* DRV FW - CRRO level is too high for compensation */
#define ZONE_TBL_MISMATCH                 14537    /* Drv F/W - Zone Table Mismatch */
#define NONINVERTIBLE_MATRIX              14538    /* Drv F/W - Matrix is not invertible */
#define BISECTION_ERROR                   14539    /* Drv F/W - Bisection algorithm failure */
#define TOO_CLOSE_TO_CYL_BOUNDARY         14540    /* Drv F/W - Too Close To The User Cylinder Boundary*/
#define EBUS_CONNECTION_FAILURE           14541    /* Drv Misc - EBUS Connection Failure */
#define SCRIPTS_BPI_AVERAGE               14543    /* Proc Misc - BPI Average exceeds spec from scripts */
#define EXCEEDS_ISE_GLIST_LIMIT           14552    /* Wt/Rd Def's-Exceeded ISE GList Limit */
#define EXCEEDS_DRIVE_GLIST_LIMIT         14553    /* Wt/Rd Def's-Exceeded Drive GList Limit */
#define VTPI_COEFF_OUT_OF_RANGE           14556    /* VTPI Coefficient Out of Range */
#define VTPI_COEFF_NOT_FOUND              14557    /* VTPI Coefficient Not Found */
#define SPT_AUTORUN_INCOMPLETE            14558    /* Proc M.E. Autorun script incomplete */
#define SPT_AUTORUN_NEVER_STARTED         14560    /* Proc M.E. Autorun was setup but never ran */
#define SPT_AUTORUN_INCOMPLETE_FAILURE    14561    /* Proc M.E. Autorun script failed incomplete */
#define SPT_AUTORUN_FAILURE               14562    /* Proc M.E. Autorun script completed with failures */
#define SPT_AUTORUN_MAX_TIME_EXCEEDED     14563    /* Proc M.E. Autorun script aborted due to test time */
#define SPT_AUTORUN_FILE_MISMATCH         14564    /* Proc M.E. Autorun script on disk does not match FW */
#define SPT_AUTORUN_FILE_READ_ERROR       14565    /* Proc M.E. Error reading autorun file from SIM */
#define SPT_AUTORUN_FILESIZE_EXCEEDED     14566    /* Proc M.E. Results file is full, script aborted */
#define DAC_MAXED_OUT                     14567    /* Drv Head - DAC MAXED OUT */
#define RDL_TMNG_RNG_EXCEEDED             14568    /* Radial Timing Error Range Limit Exceeded */
#define RDL_TMNG_FIT_ERR_RNG_EXCEEDED     14569    /* Radial Timing Fit Error Limit Exceeded */
#define SCSI_4031_05_26_XX                14572    /* Proc M.E.- 05/26XX Invalid Parameter List */
#define CHANNEL_NOT_SUPPORTED             14573    /* Channel does not support requested function */
#define TOO_MANY_SKIP_TRKS_BY_HEAD        14577    /* Svo Def's-Too Many Skip Trks by Head */                    // SF2/3 T126
#define SDOD_SERVO_LOOP_CODE_XX           14578    /* Servo Misc - Servo Loop Code 29 (SDOD failure) */
#define NO_RESPONSE_UPON_TIMEOUT          14579    /* Drv. No Response Upon Timeout */
#define ZGS_SENSOR_FAILED                 14582    /* ZGS Sensor failed or is not installed*/
#define FCS_CNTRL_NOT_SELECTED            14587    /* Svo Misc-FCS Controllers Not Selected */              // SF3 T152
#define FCS_CATCH_ALL_NOT_SELECTED        14588    /* Svo Misc-FCS Catch-All Not Selected */                // SF3 T152
#define FCS_SAP_SIZE_EXCEEDED             14589    /* Svo Misc-FCS SAP Size Exceeded */                     // SF3 T152
#define CHROME_SATURATION                 14598    /* Drv FW - CHROME Saturation */                         // SF3 T193
#define SLIP_PERCENTAGE_LIMIT_EXCEEDED    14600    /* Slip limit percentage exceeded  */
#define STE_MIN_BER_NOT_MET               14603    /* Drv Misc- STE testing Min BER not met */              // IF2 T621
#define ATI_MIN_BER_NOT_MET               14604    /* Drv Misc- ATI testing Min BER not met */              // IF2 T621
#define TA_TOO_CLOSE_TO_OD                14605    /* TA too close to OD  */
#define TA_TOO_CLOSE_TO_ID                14606    /* TA too close to ID  */
#define AFH_CLEARANCE_CALC_ERROR          14607    /* SFT - AFH clearance calculation call to RW failed */     // SF3 T49
#define AFH_WRITE_LOSS_CALC_ERROR         14608    /* SFT - AFH write loss calculation call to RW failed */    // SF3 T49
#define AFH_HEATER_CALIBRATION_ERROR      14609    /* SFT - AFH heater calibration call to RW failed */        // SF3 T49
#define UNABLE_TO_PAD_TA_AT_OD            14610    /* Minimum padding can't be applied to TA at OD */
#define UNABLE_TO_PAD_TA_AT_ID            14611    /* Minimum padding can't be applied to TA at ID */
#define FDE_START_SESSION_FAILED          14616    /* FDE Start Session Failed */
#define FDE_CLOSE_SESSION_FAILED          14617    /* FDE Close Session Failed */
#define FDE_AUTHENTICATION_FAILED         14618    /* FDE Authentication method failed */
#define FDE_GET_TABLE_METHOD_FAILED       14619    /* FDE Table Retrieval Failed */
#define FDE_SET_TABLE_METHOD_FAILED       14620    /* FDE Table Modification failed */
#define FDE_TDIC_SERVER_RPC_FAILED        14621    /* FDE TDCI Server RPC Failed */
#define FDE_LP_DOWNLOAD_FAILED            14622    /* FDE Locking Parameter Download Failed */
#define FDE_IV_DOWNLOAD_FAILED            14623    /* FDE Initial Volume Download Failed */
#define FDE_MAKERSYMK_KEY_FAILED          14624    /* FDE MakerSymK Key Retrieval Failed */
#define FDE_MSID_PASSWORD_FAILED          14625    /* FDE MSID Retrieval Failed */
#define FDE_RANDOM_CHALLENGE_FAILED       14626    /* FDE Random Challenge Retrieval Failed */
#define FDE_BAND_ACC_BEHAV_FAILED         14627    /* FDE Band Access Behavior Failed */
#define FDE_BAND_CROSSING_FAILED          14628    /* FDE Band Crossing Behavior Failed */
#define FDE_SECURITY_CMD_LOST             14630    /* Security command exceeded retry count */
#define MAX_TA_SMART_OD                   14631    /* Wt/Rd TA - Max Exceeded in SMART OD  */
#define MAX_TA_SMART_ID                   14632    /* Wt/Rd TA - Max Exceeded in SMART ID  */
#define MAX_TA_SYSTEM_PARTITION           14633    /* Wt/Rd TA - Max TA's in System Partition  */
#define LOG10_BER_EXCEEDED                14636    /* Wt/Rd Err Rate - Log10 BER exceeded */
#define INVALID_SAP_ZAP_MODE              14637    /* Drv - Invalid ZAP mode detected in SAP */
#define TA_AMP_EXCEEDS_ID_SPEC            14641    /* TA exceeds amplitude limit at ID */
#define TA_AMP_EXCEEDS_OD_SPEC            14642    /* TA exceeds amplitude limit at OD */
#define UNABLE_TO_PAD_TA_INTO_SYS_ZONE    14646    /* Unable to pad TA into System Zone */                     // SF3 T215
#define UNCERTED_TRACK_SWD                14648    /* Svo-Fault - Uncerted Track SWD */
#define FASTIO_DATA_COLLECTION_ERROR      14657    /* T35 fastio data collection failed */                     //SF3 T35
#define MR_RESISTANCE_LIMIT_FAILURE       14663    /* Svo Cal - MR Resistance limit failure */                 // SF3 T186
#define HEAD_FAILS_TO_LOAD                14664    /* Load failure during LUL test */                          // SF2 T25
#define HEAD_FAILS_TO_UNLOAD              14665    /* Unload failure during LUL test */                        // SF2 T25
#define EXCEEDED_LUL_VEL_ERROR_LIMIT      14666    /* Load/Unload velocity error exceeds max error spec*/      // CTP T25
#define COMMAND_TIMEOUT_INSUFFICIENT      14668    /* Drv Timeout-Command Insufficient */
#define FAILED_TO_DETECT_CRASH_STOP       14669    /* V3BAR Failed to Detect Crash Stop */
#define FAILED_TO_DETECT_RAMP             14670    /* V3BAR Failed to Detect Ramp */
#define T151_OPTIREGVAL                   14672    /* Wt/Rd Cal-OptiRegVal Below Limit */                      // SF2 T151
#define COMBO_STE_OUT_OF_SPEC             14674    /* Drv Misc - Normalize STE-ATI combo out of spec */
#define TOO_MANY_UNVER_PER_CYL_PER_HEAD   14675    /* Wt/Rd Err Rate-Too Many Unver Errs/Cyl/Head */
#define TOO_MANY_VER_PER_CYL_PER_HEAD     14676    /* Wt/Rd Err Rate-Too Many Ver Errs/Cyl/Head */
#define DESTROKE_LIMIT_FAILED             14677    /* Final Stroke of the Drive is Too Small */
#define PORT_WAKEUP_TIME_EXCEEDED_HW      14678    /* Drv Iface-Port Wakeup Time Exceeded (H/W) */
#define PORT_WAKEUP_TIME_EXCEEDED_CMD     14679    /* Drv Iface-Port Wakeup Time Exceeded (Cmd) */
#define SET_WR_CURRENT_TRIPLET_FAILED     14681    /* Set write current triplet failed. */
#define CONTACT_DETECTED_VIA_SERVO_ERROR  14682    /* T35 had servo error before DPES contact detected */
#define OVERLAY_CODE_INCOMPATIBLE         14688    /* Loaded overlay code is not compatible */
#define OVERLAY_CODE_NOT_PRESENT          14690    /* Overlay code is not loaded yet */
#define UNSUPPORTED_FILE_FORMAT           14695    /* Drv Misc - Unsupported File Format */
#define CHANNEL_VENDOR_INCONSISTENCY      14696    /* Drv Misc - Channel Vendor Inconsistency */
#define BPIFILE_INCONSISTENCY             14697    /* Drv Misc - BPI File Inconsistency */
#define SLOW_MEMORY_LEAK                  14698    /* Drv FW - Slow Memory Leak*/
#define FAST_MEMORY_LEAK                  14699    /* Drv FW - Fast Memory Leak*/
#define POOR_ZAG_QUALITY                  14700    /* Drv FW - Poor ZAG quality */
#define ZAG_DATA_FAILURE                  14701    /* Drv FW - ZAG data failure */
#define DICE_INTERNAL_FAILURE             14702    /* Drive Misc - Internal Dice Error */
#define OD_ID_DAC_LIMIT_FAILURE           14703    /* Drive Head - Failed OD/ID Dac Limit */
#define DC_OFFSET_ID_OD_MISMATCH          14705    /* DC Offset and ID/OD Location Mismatch */
#define MIN_CLEARANCE_FAILURE             14710    /* DRV Head - Failed Min Clearance Limit  */
#define NRRO_BIN_LIMIT_EXCEEDED           14711    /* DRV FW - NRRO Bin Limit Exceeded */
#define NARROW_HEAD_GAIN_LIN_FAILURE      14712    /* Gain Linearization failed due to narrow head */
#define AGC_LIMIT_EXCEEDED                14713    /* AGC Limit Exceeded */
#define SCSI_4031_04_40_00_80             14721    /* Format-Exceeded Max Num Of Trk Recertify */
#define TCS_SPEC_LIMIT_VIOLATED           14722    /* TCS Spec Limit Violated */
#define DICE_BAD_SVGA_DATA                14720    /* AGC Filter Error */
#define DICE_AUDIT_SIGMA_LIMIT            14726    /* Exceeded Dice Audit StdDevFitError limit */
#define TRANSFER_RATE_MISMATCH            14732    /* Drv Iface - Expected Transfer Rate Mismatch */
#define SERVO_SECTOR_OFFSET_FAILURE       14738    /* Svo Cal - Sector Offset Check Failed */
#define TRACK_RADIUS_CONV_FAILURE         14740    /* Track/Radius Conversion routine failed */
#define LATCH_FORCE_LIMIT_FAILED          14743    /* Drv Latch-Latch Force Limit out of Spec */
#define NAMED_PARAMETERS_REQUIRED         14744    /* Initiator Requires Named Parameter Test Format */
#define FDE_CRYPTO_ERASE_FAILED           14745    /* FDE Crypto Erase Failed */

#define HOST_INVALID_TEST_PARAM_NAME      14747    /* HOST-Invalid test param name */
#define HOST_SUPPLD_PARAM_VALUE_RANGE_ERR 14748    /* HOST-Suppld param value(s) range err(*) */
#define HOST_REQRD_TEST_PARAMS_ABSENT     14749    /* HOST-Reqrd test param(s) --- ABSENT --- */
#define HOST_UNSOLICITED_PARAM_NAMES      14750    /* HOST-Unsolicited param name(s) */
#define HOST_PARAM_VALUES_ORDER_SWAP      14751    /* HOST-Param value(s) order --- SWAP --- */
#define FW_INVALID_PARAM_VALUE_TYPE       14752    /* FW-Invalid test parameter value type */
#define FW_EXCEEDED_TEST_PARAM_CAPACITY   14753    /* FW-Exceeded test parameter capacity */
#define FW_REQUEST_PARAM_VALUE_CNT_OFLOW  14754    /* FW-Request param value count overflow */
#define FW_INVALID_PARAM_VALUE_ORDER_SPEC 14755    /* FW-Invalid param value order specifier */
#define FW_REQUESTED_DUPLICATE_PARAMETER  14756    /* FW-Requested duplicate parameter (#) */
#define FW_TEST_PARAM_VALUE_RANGE_ERR     14757    /* FW-Supplied param value(s) range err(@) */
#define FW_PARAM_VALUE_ORDER_SWAP         14758    /* FW-Param value(s) order --- SWAP --- */

#define TRACK_CONV_FAIL_TRK_NOT_EXIST     14815    /* Track Conversion Failed. Requested Track Does Not Exist */
#define COULD_NOT_FIND_SERVO_CTLR_PTRS    14816    /* Search for Servo's Ctlr Ptrs failed */                      // SF3 T172
#define COULD_NOT_FIND_CTLR_COEFFS_PTRS   14817    /* Search for Servo's Ctlr Coef Ptrs failed */                 // SF3 T172

#define HDINSTABILITY_SVGA_MAXEXCEEDED    14821    /* Hd Instability SVGA Max Exceeded  */
#define HDINSTABILITYSVGACREDANCEEXCEEDED 14822    /* Hd Instability SVGA Credence Exceeded */
#define SFT_SIM_RW_DC_MISMATCH            14838    /* RAP Drive Config Mismatch */
#define TOO_FEW_POINTS_FOR_FINAL_FIT      14841    /* Too Few Data Points for Final Fit */
#define OD_ID_CLEARANCE_LIMIT_EXCEEDED    14846    /* OD ID Clearance Limit Failure */
#define MAX_WIRP_CLEARANCE_LIMIT_EXCEEDED 14847    /* Max WIRP Clearance Limit Failure */
#define MAX_ALL_ZONE_CLEARANCE_LIMIT_EXCEEDED 14848 /* Max All Zone Clearance limit failure */
#define MIN_MRE_RESISTANCE_NOT_MET        14854    /* Svo Cal - Min MRE Resistance Not Met */
#define MAX_MRE_RESISTANCE_EXCEEDED       14855    /* Svo Cal - Max MRE Resistance Exceeded */
#define TOO_MANY_POINTS_DISCARDED_FOR_FIT 14864    /* Too Many Points Discard During Curve Fit */
#define FAILED_WIRP_RMS_LIMIT             14865    /* Failed WIRP Curve RMS Limit */
#define BAD_FINAL_INTERPOLATED_DAC        14866    /* Bad Final Interpolated Dac*/
#define HO_DAC_BELOW_WPH                  14867    /* Heat Only Dac Below WPH Dac */
#define FINAL_WIRP_OUTSIDE_RANGE          14868    /* Final WIRP Value Outside Range */
#define TOO_MANY_MEASURED_OUTLIERS        14869    /* Too Many Measured Outliers */
#define CANT_SWITCH_TO_DUAL_STAGE         14870    /* Unable to switch to dual stage actuator mode */
#define EXEEDED_OPERATIONAL_RV_LIMIT      14871    /* FW-Exceeded RV Operational Limit Time */
#define PRIMARY_SECONDARY_FLASH_MISMATCH  14874    /* Drv Primary-Secondary Flash Mismatch */
#define FLASH_MEDIA_FILE_MISMATCH         14875    /* Drv Flash-Media File Mismatch */
#define INVALID_TEST_MODE                 14878    /* HOST-Invalid test mode */
#define ZONE_BASED_TRANSFER_RATE_LIMIT_FAILURE   14879 /* Datarate not within specified limits */
#define MECH_DC_OFFSET_OF_HEADS_TOO_HI    14885    /* Mechanical DC Offset of Heads Too High */
#define DWELLING_CAUSED_HEAD_FAILURE      14904    /* TA Dwelling caused Head failure */
#define EAW_BER_LIMIT_EXCEEDED            14906    /* Drive Head - EAW BER Limit Exceeded */
#define DEF_SECS_PER_TRK_EXCEEDED_RANGE   14907    /* Wt/Rd Def's-Defective Sectors Per Track Exceeded Range */
#define DEF_CYLS_EXCEEDED_RANGE           14908    /* Wt/Rd Def's-Defective Cylinders Exceeded Range */
#define HOST_SUPPLD_PARAM_VALUE_CNT_OFLOW 14909    /* HOST-Param value count overflow */
#define EXPECT_HO_CONTACT_DAC_LOWER_THAN_WPH 14916 /* Expected HO is lower than WPH */
#define ADJ_ZONE_XFR_RATE_DELTA_EXCEEDED  14917    /* Wt/Rd Misc-Adj Zone Transfer Rate Delta Exceeded */
#define FAILED_TOT_MSECS_PER_TOT_CMDS_SPEC 14923   /* Drv Iface-Failed Total mSec/Cmd Limit */
#define FAILED_MSECS_PER_CMD_SPEC         14924    /* Drv Iface-Failed mSec/Cmd Limit */
#define DELTA_DAC_MAXED_OUT               14925    /* Delta DAC Exceeded */
#define FW_DRV_TEMP_RAMP_RATE_FAILURE     14927    /* T235 Drive Temp Ramp Rate Failed */
#define FAILED_TOT_CMDS_MINS_SPEC         14928    /* Drv Iface-Failed Total Cmds in Mins Spec */
#define BER_MEASUREMENT_FAILED            14929    /* BER Measurement Failed */
#define TOO_MANY_SERVO_FLAWS_PER_HEAD     14935    /* Svo Def's-Too Many Servo Flaws Per Head*/                 // SF2/3 T126
#define EXCEEDED_BUFFER_IOECC_LIMIT       14937    /* Drv SMART-Buffer IOECC Limit Exceeded*/
#define TEST_ZONE_NOT_FOUND               14938    /* Testing Zone Not Found */
#define VER_HEAD_ZONE_FAILURE             14939    /* Wt/Rd Def's-Too Many Ver. Errs/Hd-Zone */               // SF2/3 T140
#define ZONE_SPAN_DAC_DELTA_FAILURE       14941    /* Zone Span DAC Delta check failed */
#define FINAL_CURVE_FIT_STDDEV_FAILURE    14942    /* Final Curve Fit Std Dev Limit Exceeds */
#define RRO_BIN_LIMIT_EXCEEDED            14943    /* DRV FW - RRO Bin Limit Exceeded */
#define DID_NOT_RUN_MIN_NUM_ZONES         14944    /* Test didn't run minimum number of zones */
#define PLIST_SECTOR_LIMIT_EXCEEDED       14945    /* Wt/Rd Def's-PLIST_SECTOR Limit Exceeded */
#define PLIST_SFI_LIMIT_EXCEEDED          14946    /* Wt/Rd Def's-PLIST_SFI Limit Exceeded */
#define GLIST_LIMIT_EXCEEDED              14947    /* Wt/Rd Def's-GLIST Limit Exceeded */
#define SERVO_PRIMARY_LIMIT_EXCEEDED      14948    /* Wt/Rd Def's-SERVO_PRIMARY Limit Exceeded */
#define SERVO_ADDED_LIMIT_EXCEEDED        14949    /* Wt/Rd Def's-SERVO_ADDED Limit Exceeded */
#define RANDOM_METHOD_FAILED              14950    /* Random number generator method failed  */
#define FILE_FW_INIT_FW_TAG_MISMATCH      14951    /* File FW tags do not match Initiator Firmware tags  */

#define DEPRECATED__INVALID_PARAM_VALUE   14957    /* DEPRECATED --- Invalid Parameter Value */
#define INVALID_BITMASK_VALUE             14958    /* Bitmask value invalid for test */
#define BAD_CWORD_MODES_COMBINATION       14959    /* Selected CWORD modes incompatible */
#define INVLD_PARAM_RANGE_FOR_CWORD_MODE  14960    /* Bad param range for spec'd cword mode */
#define ESG_V3BAR_FLAG_ERROR              14961    /* ESG V3BAR disabled or bad param */
#define INVALID_CUDACOM_PARAM_RANGE       14962    /* Cudacom - Parameter out of range */
#define INVALID_CUDACOM_ACCESS_TYPE       14963    /* Cudacom - Invalid access type */
#define INVALID_CUDACOM_SS_TYPE           14964    /* Cudacom - Invalid super sector type */
#define INVLD_CUDACOM_PARM_TPE_FOR_FN_NUM 14965    /* Cudacom - Invalid parm type for fn num */
#define INVALID_PLOT_TYPE                 14966    /* Invalid plot type */
#define CWORD_MODE_UNSUPPORTED            14967    /* Control word mode unsupported */
#define SFLAW_OTF_NOT_ENABLED_FOR_CWORD1  14968    /* OTF Servoflaw scan not enabled */
#define FSB_UNSUPPORTED                   14969    /* FSB Unsupported */
#define FAFH_UNSUPPORTED                  14970    /* FAFH Unsupported */
#define INVALID_SPECTRAL_DETECTOR_VAL     14971    /* Spectral Detector value invalid */
#define PARAM_OPTION_UNSUPPORTED          14972    /* Parameter option not supported */
#define INVALID_CONTROL_WORD_VALUE        14973    /* HOST-Invalid control word value */
#define INVALID_ACCESS_TYPE               14974    /* Invalid Access Type */
#define INVLD_SET_XREGxx_FOR_ACCESS_TYPE  14975    /* Invalid addr/mask for dir access */
#define INVD_CWRD_AND_EXTD_FOR_ACCESS_TPE 14976    /* Invld cword, extd parm for 32-bit access */
#define INVALID_WRITE_OR_CAL_PATTERN      14977    /* Write or calibration pattern invalid */
#define INVLD_SFLAW_OTF_FOR_CWORD4_MODE   14978    /* OTF Servoflaw scan invld for cword4 mode */
#define DEFAULT_HEATER_VALS_NOT_IN_RAP    14979    /* Default heater values not in the RAP */
#define INVALID_FSB_VALUE                 14980    /* Invalid FSB value */
#define TFA_SAMPS_MEAS_REPS_PROD_TOO_HIGH 14981    /* Samples and reps prod too large */
#define INVLD_NOTCH_AND_FILTER_OPTIONS    14982    /* NOTCH_CONFIG/FILTERS set wrong */
#define INVALID_REG_ADDRESS               14983    /* Invalid register address */
#define INVALID_FREQ_STEP                 14984    /* Invalid freq_step */
#define INVLD_ZN_MSK_AND_TST_CYL_SELECTED 14985    /* Cannot do both cylinder and zone test */
#define MAX_CQM_PCNT_AND_DCQM_USED        14986    /* Cannot use both max_cqm_pct and dcqm */
#define CTFFR_PCTG_HANDLING_REQUIRED      14987    /* Cutoff Freq Percentage handling required */
#define INVLD_INTERVAL_INCREMENT_VAL      14988    /* Cyl/head rng or Interval size/num invld */
#define CHANNEL_REG_TO_OPTx_RANGE_ERROR   14989    /* Invalid Start/End pair for channel reg */
#define REG_ID_UNSUPP_IN_REL_RANGE_MODE   14990    /* Reg ID unsupported-relative range mode */
#define INVALID_REG_TO_OPTx_EXT_OPT       14991    /* REG_TO_OPTx_EXT options invalid */
#define INVALID_REG_TO_OPTx_EXT_T_AND_D   14992    /* Tap & Dibit Opts invalid for reg to opt */
#define INVALID_SELF_CHECK_VAL            14993    /* Invalid Self Check Value */
#define PRISM_TRAJECTORY_MEAS_ERROR       14994    /* Svo-Prism trajectory meas error */
#define SIM_FILE_WRITE_ERROR              14995    /* Drv-SIM file write error */
#define NO_SERVO_PRISM_SUPPORT            14996    /* Drv-No servo PRISM support */
#define NO_SERVO_ZEST_SUPPORT             14997    /* Drv-No servo ZEST support */
#define SIM_FILE_OPEN_ERROR               14998    /* Drv-SIM file open error */
#define TOO_FEW_PARAM_VALUES              14999    /* Drv-Too few parameter values */
#define NO_CFW_ZEST_SUPPORT               15000    /* Drv-No CFW ZEST support */
#define BASELINE_FOUND_HARD_ERROR         15001    /* T51 specific error when baseline measurement detects a hard error*/
#define BAND_INFO_ERROR                   15002    /* SMR error received from the Calculate Band Info function */
#define TRACK_INVALID_IN_FAFH_PARAM_FILE  15005    /* T135: Test track in FAFH param file is invalid*/
#define POSITIVE_BURNISH_FAILURE          15006    /* T135: Burnish failure */
#define NEGATIVE_BURNISH_FAILURE          15007    /* T135: Burnish failure */
#define NRB_READ_ERROR                    15008    /* T251: NRB read error */
#define NO_SAME_OPTI_ZGROUP_NEAR_THIS_ZONE 15009   /* T135 FAFH crossing error: No same write power zone group around tested zone. */

#define FDE_REMOVE_ACE_METHOD_FAILED      42105    /* RemoveACE method failed - SED  */
#define CV_SEEK_CMD_TIMEOUT               42161    /* Drv-Constant Velocity Seek Timeout */
#define HOST_FAULT_LIMIT_EXCEEDED         42168    /* FW-Fault Limits Exceeded*/
#define ERASE_AFTER_WRITE_FAILURE         42171    /* Erase After Write Test Failure */
#define PRISM_TF_MEASUREMENT_ERROR        42174    /* FW-Prism Xfr Function Measurement Error */
#define PRISM_TF_SETUP_ERROR              42175    /* FW-Prism Xfr Function Setup Error */
#define CV_SEEK_CMD_FAILED                42176    /* Drv-Constant Velocity Seek Failed */
#define TRAJECTORY_MISMATCH               42177    /* Svo-Prism trajectory mismatch */
#define EXCEEDED_SWD_FVGA_LIMIT           42179    /* Drv SMART-SWD FVGA Limit Exceeded */
#define ZEST_TABLE_REQUIRES_ALL_HEADS     42181    /* FW-ZEST table requires all heads */
#define AFH_AND_HD_STABILITY_TEST_FAILED  42184    /* Drv-Failed AFH and failed Head-Stability Test */
#define BURNISH_CHK_INSUFFICIENT_DATA     42187    /* Burnish Chk Insufficient Data */
#define NOISY_SRVO_PREAMBLE               42188    /* Noisy Servo Preamble */
#define SCSI_4031_01_0b_02                42193    /* Drv SMART-01/0B02 Seek Error Warning */                 //
#define XHEATER_CLR_DELTA_EXCEEDED        42197    /* AFH- Cross heater clearance delta exceeded. */                 //
#define INVALID_ZAP_POSITION              42199    /* Invalid ZAP position. */
#define RRO_AMPL_LIMIT_OOS                42208    /* RRO fft amplitude OOS */
#define PRISM_TRAJ_TRGR_SECT_INVALID      42209    /* Invalid trigger sector requested */
#define FREQ_RANGE_TOO_HIGH               42210    /* Frequency Range too High */
#define INVALID_TRAY_LOCK_ACTION          42211    /* FW-Invalid tray lock action requested */
#define TRAY_LOCK_CHG_REQUEST_TIMEOUT     42212    /* FW-Tray lock change request timeout */
#define TRAY_LOCK_TYPE_MISMATCH           42213    /* FW-Tray lock type mismatch */
#define UNDEFINED_TRAY_LOCK_ERROR         42214    /* FW-Tray lock error undefined */
#define UNDEFINED_TRAY_LOCK_HOST_RESPONSE 42215    /* FW-Host tray lock response undefined */
#define BEARING_DELTA_OOS                 42217    /* VCM Bearing OOS */               // T136
#define EXCEEDED_MOTOR_POWER_LIMIT        42218    /* SMART Motor Power Max reading exceeded*/
#define VGAS_LIMIT_EXCEEDED               42219    /* VGAS Limit exceeded */
#define EAW_DEGREDATION_LIMIT_EXCEEDED    42221    /* Erase After Write degredation failure */
#define SSD_DEFECTS_PER_DIE_EXCEEDED      42230    /* Wt/Rd Def's- SSD Number of Defects Per Die Exceeded */
#define FDE_ADD_ACE_METHOD_FAILED         42451    /* AddACE method failed - SED  */

#define MAX_AGC_RANGE_LIMIT_EXCEEDED      48380    /* Drv Head-Max AGC Range Limit Exceeded */
#define AVG_AGC_RANGE_LIMIT_EXCEEDED      48381    /* Drv Head-Avg AGC Range Limit Exceeded */
#define AVG_AGC_STDEV_LIMIT_EXCEEDED      48382    /* Drv Head-Avg AGC Stdev Limit Exceeded */
#define ADJ_ZN_XFR_RATE_PRCT_DELTA_EXCEEDED 48383  /* W/R Prct Delta Adj Zn Xfer Rate Exceeded */
#define REQD_TLEVEL_SPEC_EXCEEDED         48390    /* Required T-Level for Recovery Exceeded Spec */
#define SYSTEM_AREA_MERT_TEST_ABORTED     48391    /* System Area MERT Test Aborted - Log Full */
#define SSD_MERT_TEST_FAILED              48392    /* SSD MERT Test Failed */
#define MR_RESISTANCE_DELTA_LIMIT_EXCEEDED  48393  /* Svo Cal - MR Resistance Delta Limit Exceeded */
#define DELTA_VS_RAP_CLEARANCE_EXCEEDED   48394    /* Clearance Delta vs. RAP Exceeded Limit */
#define PRESSURE_SENSOR_FAILED            48398    /* Pressure Sensor Calibration Failure*/
#define PRESSURE_SENSOR_ABSENT            48399    /* Pressure Sensor was not present*/
#define RAMP_CYL_FAILS_LIMIT              48400    /* Minimum Cylinder Fails to Meet Limit */
#define READER_BIAS_VOLT_LIMIT_EXCEEDED   48402    /* Reader Bias Voltage exceeds limit */
#define POLY_FIT_ERROR_LIMIT_EXCEEDED     48410    /* Polynomial Fit Error Limit Exceeded */
#define CAL_TRANSITION_NOT_FOUND          48411    /* Calibration transition NOT found */
#define AXIAL_DISTORTION_OOS              48412    /* Estimated Axial Distortion OOS */
#define NEG_DELTA_MRE_LIMIT_EXCEEDED      48413    /* Svo Cal - Negative Delta MRE Limit Exceeded */
#define POS_DELTA_MRE_LIMIT_EXCEEDED      48414    /* Svo Cal - Positive Delta MRE Limit Exceeded */
#define HUMIDITY_OUT_OF_BOUNDS            48416    /* T235 Humidity Out of Bounds */
#define ZONE_CAL_FAILURE                  48418    /* Zone Calibration Failure */
#define DETCR_THRSH_SPEC_EXCEEDED         48419    /* DETCR Threshold Spec. Exceeded */
#define HUMIDITY_SENSOR_FAILURE           48420    /* Humidity Sensor Failed */
#define DRIVE_SEAL_FAILED                 48429    /* Drive Seal Failed */
#define ISE_VERSION_INCORRECT             48430    /* ISE version not appropriate for SED/ISE drive type */
#define FOCUS_TRACKS_PER_SERPENT_EXCEEDED 48432    /* FOCUS max tracks per serpent exceeded */
#define FOCUS_REVS_NOT_ACHIEVED           48433    /* FOCUS revs not achieved */
#define BIAS_TARGET_NOT_ACHIEVED          48434    /* Unable to Reach Bias Target at Max DAC  */
#define VOLTAGE_SATURATION                48435    /* Voltage Saturation Failure  */
#define USE_OF_RESERVED_BITS              48438    /* Use of reserved control word bits */
#define INVALID_SERVO_RAM_ADDRESS         48439    /* Invalid servo ram address */
#define NBR_POLY_COEFFS_NOT_MATCH         48440    /* Nbr VTPI Coeffs Not Correct */
#define RAGC_AMPL_LIMIT_OOS               48441    /* Repeatable AGC OOS */
#define NRAGC_AMPL_LIMIT_OOS              48442    /* Non Repeatable AGC OOS */
#define TOO_MANY_VELOCITY_ADJUSTMENTS     48444    /* Too many velocity adjustments required */
#define DETCR_CONTAM_DETECTED             48447    /* DETCR Contamination Detected */
#define PARAM_DICTIONARY_UPLOAD_FAILED    48456    /* Parameter Dictionary Upload Failed */

#define TOO_MANY_SVO_DEF_IN_EXTREME_OD    48462    /* Too Many consec Svo Def in Extreme OD */
#define INITIAL_ATI_OOS                   48472    /* Drv Misc - Initial ATI Out Of Spec */
#define VCM_BEMF_OFFSET_CAL_FAILED        48465    /* VCM BEMF Cal Failed */
#define VCM_INJECT_CURRENT_FAILED         48466    /* VCM Inject Current Failed */
#define AGC_MAG_LIMIT_OOS                 48486    /* AGC Magnitude Limit OOS */
#define PES_AND_AGC_LIMIT_OOS             48487    /* PES and AGC Mag Limit OOS */
#define COIL_TORSION_PHASE_LIMIT_EXCEEDED 48489    /* Coil Torsion Phase Limit Exceeded */
#define CM_CPY_STARTUP_SLOTERRS           48490    /* Tester Misc-Slot Errors at Startup */
#define SCOPY_LOAD_OGB_FAIL               48491    /* Failure during loading head on OGB pattern */
#define SCOPY_HEAD_UNLOAD_FAIL            48492    /* Failure during Unloading head */
#define SCOPY_SWITCH_HYBRID_SPIN_FAIL     48493    /* Hybrid Spindle controll failed */

#define SCOPY_UNDEFINDED_J2S_FAIL         48494    /* Spindle is not spinning */
#define SCOPY_CHAN_SETUP_1_FAIL           48495    /* Servo command 76,01 failure */
#define SCOPY_CHAN_SETUP_2_FAIL           48496    /* Servo command 76,02 failure */
#define SCOPY_CHAN_SETUP_3_FAIL           48497    /* Servo command 76,03 failure */
#define SCOPY_SET_SPIRAL_TESTPIN_FAIL     48498    /* Failure during Spiral test output setting */
#define SCOPY_SPIRAL_AUTO_MODE_FAIL       48499    /* Enable Auto Spiral mode failed */
#define SCOPY_CENTER_FRAME_FAIL           48500    /* Spiral Center Frame failed */
#define SCOPY_SWITCH_TIMING_CONTROL_FAIL  48501    /* Failure during switch timing control */
#define SCOPY_PHASE_DLC_SPOKE_FAIL        48502    /* DLC Phase control based on Spoke SAM2SAM failed */
#define SCOPY_FREQ_DLC_SPOKE_FAIL         48503    /* DLC Frequency control based on Spoke SAM2SAM failed */
#define SCOPY_CONV_TO_SPIRAL_FAIL         48504    /* Failure during switch position control to spiral */
#define SCOPY_INIT_SPIRAL_VAR_FAIL        48505    /* Spiral gate position variable initialization faild */
#define SCOPY_DISABLE_SG_FAIL             48506    /* Failure during Servo Gate shutt off */

#define SCOPY_CAL_AVG_FAIL                48507    /* Failure during average of collected data */
#define SCOPY_SP_SRCH_SK_FAIL             48508    /* Conventional seek failure during spiral search */
#define SCOPY_SP_SRCH_CAL_AVG_FAIL        48509    /* Failure during average of collected data for calibration */

#define SCOPY_BUMP_SEEK_FAIL              48510    /* Spiral Bump seek failure */
#define SCOPY_RAMP_SEEK_FAIL              48511    /* Spiral Ramp seek failure */
#define SCOPY_RAMP_SEEK_1_FAIL            48512    /* Spiral Ramp seek1 failure */
#define SCOPY_RAMP_SEEK_2_FAIL            48513    /* Spiral Ramp seek2 failure */

#define SCOPY_SET_PREAMP_FAIL             48514    /* Preamp setting failure */
#define SCOPY_SET_SPIRAL_VGA_FAIL         48515    /* Spiral VGA control failure */

#define SCOPY_SP_SCAN_OD_FAIL             48516    /* Spiral scan failure at OD */
#define SCOPY_SP_SCAN_MD_FAIL             48517    /* Spiral scan failure at MD */
#define SCOPY_SP_SCAN_ID_FAIL             48518    /* Spiral scan failure at ID */
#define SCOPY_WARPAGE_RAMPSEEK_FAIL       48519    /* Ramp seek failure during IDCS */
#define SCOPY_WARPAGE_AVG_FAIL            48520    /* Warpage averate failure */

#define SCOPY_POS_ZAP_EXCEED_ITER_LIMIT               48521    /* Position ZAP exceeded iteration limit */
#define SCOPY_TIMING_ZAP_EXCEED_ITER_LIMIT            48522    /* Timing ZAP exceeded iteration limit */
#define SCOPY_POSITION_TIMING_NORMAL_LIMIT_FAILED     48523    /* Position & Timing esterr failed at normal limit */
#define SCOPY_POSITION_TIMING_MAX_LIMIT_FAILED        48524    /* Position & Timing esterr failed at max limit */
#define SCOPY_BAD_SPIRALS                 48525    /* Spiral pattern is bad */
#define SCOPY_SERVO_WAIT_TIMEOUT          48526    /* Timeout during data collection */

#define SSD_CATEGORIZED_DEFECTS_PER_DIE_EXCEEDED 48527 /* CAT Number of Defects Per Die Exceeded */
#define SSD_TOTAL_DEFECTS_PER_DIE_EXCEEDED 48528   /* Total Number of Defects Per Die Exceeded */
#define SSD_DEFECTS_PER_PLANE_EXCEEDED    48529    /* Wt/Rd Def's- SSD Number of Defects Per Plane Exceeded */
#define USE_OF_RESERVED_MODES             48530    /* Use of reserved enumeration modes */
#define SSD_MERT_DRAM_LOG_FULL            48531    /* MERT DRAM Log is full*/
#define SSD_MERT_NOR_DFCT_LOG_FULL        48532    /* MERT NOR defect log is full */
#define HUMIDITY_OUT_OF_RANGE             48533    /* Humidity Out of Range */

#define INVALID_ALIGNMENT_SETUP           48551    /* Drv Misc - Invalid Alignment Setup */
#define SSD_MERT_NOR_LOG_NOT_INITALIZED   48553    /* MERT NOR log failed,need to initalize it */
#define DETCR_WRITE_COUPLING_DETECTED     48554    /* DETCR Write Coupling Detected */
#define EXCEEDED_WRITE_FREE_10_LIMIT      48555    /* Drv SMART-Write Free 10 Limit Exceeded */
#define PHOTO_DIODE_RAILED                48556    /* HAMR Photo Diode is bad */

#define WEDGE_NUM_OVERRANGE               48557    /* Wedge Number Overrange */
#define ZEST_DIFF_LIMIT_EXCEEDED          48562    /* First diff of ZEST table exceeded max abs limit*/
#define EXCEEDED_BUFFER_IOEDC_LIMIT       48563    /* Drv SMART-Buffer IOEDC limit exceeded*/
#define PS_ASYMMETRY_OOS                  48566    /* PS asymmetry OOS */
#define ILLEGAL_SERVO_RAM_ADDRESS         48588    /* Illegal (odd) servo ram address */
#define EXCESSIVE_TTPE_AMPLITUDE          48596    /* Excessive TTPE Amplitude on Surface */

#define GAP_ALREADY_CALIBRATED            48598    /* Reader to Writer gap already calibrated. */
#define DETCR_FAULT_COUNT_SATURATED       48655    /* DETCR Fault Count Saturated */

#define MISSING_PARAM_LIST_TERMINATION    48602    /* Param list missing termination code */

#define LASER_CAL_MAX_IADD_REACHED        48607    /* Laser calibration max current reached */
#define TEST_NUMBER_MISMATCH_IN_PARAM_BLOCK 48608  /* Test number mismatch in param block */
#define UNEXPECTED_TESTER_RESPONSE_BLOCK  48609    /* Unexpected tester response block */
#define PARAM_DATA_EXCEEDS_BUFFER_CAPACITY 48610   /* Param data exceeds buffer capacity */
#define LLRW_SERVO_CMD_FAIL               48611    /* R/W Servo Command Failure */
#define HEATER_SHORT_CIRCUIT              48612    /* Heater responds like a short circuit. */
#define HEATER_OPEN_CIRCUIT               48613    /* Heater responds like an open circuit. */

#define ZFS_WRT_BAD_SENSE                 48615    /* ZFS Write returned Unrecognized Error */

#define HEATER_RESISTANCE_RANGE_ERROR     48627    /* Heater resistance out of range */
#define BER_SAVE_AREA_FULL                48628    /* Proc TSD - BER Save Area Full */
#define FAIL_VIRTUAL_REAL_TRANSITION      48631    /* Failed Virtual Real Transition */

#define FLASH_FIRMWARE_IMAGE_CORRUPT      48648    /* Flash firmware image is corrupt */
#define FLASH_FIRMWARE_IMAGE_RECOVERED    48649    /* Flash FW image recovered from corruption */
#define CM_ILLEGAL_SOFTWARE               48650    /* Tester CM illegal software */
#define SRVO_WATCHDOG_FLED_OCCURRED       48651    /* Servo Watchdog flash led occurred*/
#define TRACK_CONVERSION_FAILED           48653    /* Failed To convert Phy to Log Track  */
#define MAX_INITIAL_ADC_ITERATIONS_REACHED 48659   /* Max Initial DC Cancel iterations reached */
#define TABLE_DIMENSION_EXCEEDED          48661    /* Table Dimension Exceeded */
#define STRESS_CERT_TABLE_IS_FULL         48664    /* Stress Cert table is full */
#define HOST_SUPPLD_PARAM_INCOMPLETE_ROW  48666    /* HOST-Suppld param incomplete row */
#define MIN_LIFE_LEFT_EXCEEDED            48671    /* Minimum life left on drive was exceeded  */
#define INVALID_HISTOGRAM_SETUP           48672    /* Invalid servo flaw histogram setup. */
#define DISK_DEFORMATION_LIMIT            48674    /* Drv Misc - Disk may be deformed */
#define EXTRAPOLATION_LIMIT_EXCEEDED      48680    /* Extrapolation limit exceeded */
#define CM_MAX_VSZ_LIMIT_EXCEED           48686    /* Tester CM max VSZ limit exceeded */
#define UNDERFLOW_EVENT                   48700    /* Variable Or Array Underflow Occurred */
#define OVERFLOW_EVENT                    48701    /* Variable Or Array Overflow Occurred */
#define DIAG_CMD_LEN_EXCEEDED             48713    /* Length of Diag Cmd has exceeded */
#define DEGENERATE_MATRIX                 48714    /* Matrix determinant is 0: No solution */
#define PREAMP_REGISTER_RW_ERROR          48726    /* Failure to read or write preamp register */
#define ZONED_SERVO_TM_FAILED_CONVERGENCE 48722    /* Zoned Servo TM to TM Failed Convergence */
#define ZONED_SERVO_DC_FAILED_CONVERGENCE 48723    /* Zoned Servo DC Offset Failed Convergence */
#define ZONED_SERVO_TM_OFFSET_TOO_BIG     48724    /* Zoned Servo Incoming TM Offset Too Big */
#define ZONED_SERVO_DC_OFFSET_TOO_BIG     48725    /* Zoned Servo Incoming DC Offset Too Big */
#define QUADRATIC_NO_SOLUTION             48733    /* No solution to quadratic formula */

#define SCOPY_RELOAD_OGB_FAILED                     48792    /* Failure during reloading head on OGB pattern */
#define SCOPY_PHASE_DLC_SPIRAL_FAILED               48793    /* DLC Phase control based on Spiral failed */
#define SCOPY_FREQ_DLC_SPIRAL_FAILED                48794    /* Spiral DLC Frequency control failed */
#define SCOPY_AST_READ_OGB_TRACK_FAILED             48848    /* Read global position from OGB failed */
#define SCOPY_AST_MOVE_TO_FISRT_J2S_FAILED          48849    /* Move to first J2S location failed */
#define SCOPY_AST_RESET_SPIRAL_TRACK_FAILED         48797    /* Reset spiral to aligned track failed */
#define SCOPY_SP_SK_FAILED_IN_JTS                   48798    /* First conventional seek failure in JTS */
#define SCOPY_SK_FAILED_BEFORE_VGA                  48799    /* Conventional seek failure before VGA change */
#define SCOPY_SK_FAILED_AFTER_VGA                   48800    /* Conventional seek failure after VGA change */
#define SCOPY_SP_VGA_CAL_AVG_FAILED                 48801    /* Failure during average of Spiral VGA */
#define SCOPY_OD_RAMP_DETECTION_SEEK_FAILED         48802    /* Spiral seek to OD Ramp failure */
#define SCOPY_INIT_SPIRAL_VARIABLES_FAILED          48803    /* Failure during init Spiral variables */
#define SCOPY_CHAN_SETUP_BF_SSWEN_FAILED            48804    /* Spiral channel setup before SSWEN failed */
#define SCOPY_RESYNC_SAM2SAM_FAILED                 48805    /* Failure during Servo S2S Resync */
#define SCOPY_RESYNC_SAM2SAM_SPIRAL_FAILED          48806    /* Failure during Spiral Servo S2S Resync */
#define SCOPY_SET_SPIRAL_TRACK_FAILED               48807    /* Failure Set spiral track based on OGB */
#define SCOPY_SETUP_SP_CHNL_AFTER_J2S_FAILED        48808    /* Failure Set spiral channel after J2S */
#define SCOPY_J2S_GET_SP_MAGNITUDE_FAILED           48809    /* Get target spiral magnitude failed */
#define SCOPY_J2S_SP_SAM_THRESHOLD_FAILED           48810    /* Set Spiral SAM Threshold failed */
#define SCOPY_J2S_SET_AMPLITUDE_MAX_FAILED          48811    /* Set Amplitude Range Max failed */
#define SCOPY_J2S_RECALC_ADIF_FAILED                48812    /* Failure during ReCalculate Adif */
#define SCOPY_J2S_MEASURE_XFR_FAILED                48813    /* Measure Xfr function failed */
#define SCOPY_J2S_LEARN_T_ZAP_FAILED                48814    /* Learn Timing Zap failed */
#define SCOPY_J2S_BSEEK_TO_DIFF_SP_FAILED           48815    /* Seek to different Spiral bank failed */
#define SCOPY_J2S_POS_TIME_ZAP_FAILED               48816    /* Position and Timing Zap failed */
#define SCOPY_J2S_BACK_TO_START_TRACK_FAILED        48817    /* Back to Starting Track failed */
#define SCOPY_J2S_TSTAMP_BY_PHASE_FAILED            48818    /* Tstamp selection by phase error failed */
#define SCOPY_J2S_AMPLITUDE_NORM_FAILED             48819    /* Set Amplitude Range to Normal failed */
#define SCOPY_J2S_INIT_READ_S2S_FAILED              48820    /* Init Resync read S2S failed */
#define SCOPY_J2S_VERIFY_RS2S_RESYNC_FAILED         48821    /* Verify Read S2S Resync failed */
#define SCOPY_J2S_VERIFY_RS2S_RESYNC_LOOP_FAILED    48822    /* Loop to verify Read S2S Resync failed */
#define SCOPY_TURN_ON_2ND_SPIRAL_GATE_FAILED        48823    /* Turn on 2nd spiral gate failed */
#define SCOPY_CLOSE_2ND_SPIRAL_GATE_FAILED          48824    /* Turn off 2nd spiral gate failed */
#define SCOPY_APPLY_SPIRAL_DIFFERENCE_FAILED        48825    /* Error when apply spiral difference */
#define SCOPY_CALC_SPIRAL_DIFFERENCE_FAILED         48826    /* Error when calc spiral difference */
#define SCOPY_CLEAR_POS_TIMING_COLLECTION_FAILED    48827    /* Error when clear pos n timing collection */
#define SCOPY_DO_POS_TIMING_COLLECTION_FAILED       48828    /* Position n timing collection failed */
#define SCOPY_AFH_REF_HEAD_FAILED                   48829    /* Error during AFH on ref head */
#define SCOPY_AFH_BANK_HEAD_FAILED                  48830    /* Error during AFH on bank head */
#define SCOPY_SET_RANGE_MAX_FAILED                  48831    /* Set Spiral amplitude range to max failed */
#define SCOPY_SET_RANGE_NORMAL_FAILED               48832    /* Set Spiral amplitude range to normal Err */
#define SCOPY_SEEK_FAILED_DURING_AFH                48833    /* Seek failed during AFH */
#define SCOPY_FORWARD_SEEK_START_FAILED             48834    /* Seek failed to start cylinder Forward SC */
#define SCOPY_FORWARD_INIT_ZAP_FAILED               48835    /* Initial Zap failed at forward SC */
#define SCOPY_FORWARD_ZAP_FAILED                    48836    /* Zap failed during forward SC */
#define SCOPY_FORWARD_ZAP_GAIN_CAL_FAILED           48837    /* Zap gain calib failed during forward SC */
#define SCOPY_FORWARD_ODD_EVEN_ZAP_FAILED           48838    /* Odd even Zap failed during forward SC */
#define SCOPY_FORWARD_SEEK_FAILED                   48839    /* Seek failed during forward SC */
#define SCOPY_FORWARD_COPY_FAILED                   48840    /* Write failed during forward SC */
#define SCOPY_REVERSE_SEEK_START_FAILED             48841    /* Seek failed to start cylinder reverse SC */
#define SCOPY_REVERSE_INIT_ZAP_FAILED               48842    /* Initial Zap failed at reverse SC */
#define SCOPY_REVERSE_ZAP_FAILED                    48843    /* Zap failed during reverse SC */
#define SCOPY_REVERSE_ZAP_GAIN_CAL_FAILED           48844    /* Zap gain calib failed during reverse SC */
#define SCOPY_REVERSE_ODD_EVEN_ZAP_FAILED           48845    /* Odd even Zap failed during reverse SC */
#define SCOPY_REVERSE_SEEK_FAILED                   48846    /* Seek failed during reverse SC */
#define SCOPY_REVERSE_COPY_FAILED                   48847    /* Write failed during reverse SC */
#define SCOPY_J2S_LEARN_POS_ZAP_FAILED              48858    /* Scopy Learn position Zap failed */
#define SCOPY_TURN_OFF_DSA_FAILED                   48859    /* Scopy Turn off DSA failed */
#define SCOPY_TURN_ON_DSA_FAILED                    48860    /* Scopy Turn On DSA failed */
#define SCOPY_SET_SCOPY_CONTROLLER_FAILED           48861    /* Set servo copy controller failed */
#define OPEN_PC_FILE_FAILED                         48865    /* Unable to open a PC file */
#define CLOSE_PC_FILE_FAILED                        48866    /* Unable to close a PC file */
#define UNLATCH_CURRENT_LIMIT_EXCEEDED              48869    /* Drv unlatch current limit exceeded*/
#define SIM_FILE_CLOSE_ERROR                        48873    /* Drv-SIM file close error */
#define TEST_HEAD_NOT_FOUND                         48874    /* Testing head not found */
#define INVALID_HEAD_TO_CONTROLLER_MAP_MASK         48875    /* Cant discard an in use SAP Controller */
#define AFH4_TEST_TWO_ZONE_PASSED                   48878    /* T135 TCS USE TWO ZONES */
#define AFH3_CLR_VS_AFH2_DELTA_PASSED               48879    /* T135 Delta Limit vs Rap Clearance Not Exceeded */
#define INVALID_REGISTER_ID                         48888    /* Invalid Register Identifier */
#define FAILED_PZT_CAL                              48892    /* Svo Startup- Self PZT Cal Failed,LC=8F   */       // SF3 main T208
#define INDEX_OUT_OF_RANGE                          48904    /* Array index out of range */
#define ZAP_POLY_COEFFS_NOT_VALID                   48908    /* ZAP POLY COEFFS NOT VALID */
#define NVC_BURN_FAILED                             48915    /* NVC Failed to Burn */
#define NEGATIVE_BNDRY_INC                          48917    /* Negative Boundary Increment */
#define PHYS_START_TRK_INVALID                      48918    /* New Physical Start Track Invalid */
#define UNSUPPORTED_TSE_FILE_VERSION                48919    /* Unsupported TSE file version */
#define TSE_FILE_ALREADY_ALLOCATED                  48920    /* TSE file has already been allocated */
#define ZAP_ZBZ_NOT_ALLOWED_ON_PARTIAL_SURFACE      48924    /* User-ZBZ NOT allowed on partial surface */
#define INVALID_ADAPTIVE_PARAMETER_TYPE             48925    /* FW- Invalid adaptive parameter type */
#define FIXED_THRESHOLD_NOT_MET                     48926    /* Fixed threshold not met for any BPI */
#define TSE_FILE_NAME_LENGTH_ZERO                   48928    /* TSE File name length is zero */
#define INVALID_FREQUECY_FILE                       48929    /* FW- Invalid frequecy file specified */
#define MAX_CYL_19_BIT_LIMIT_EXCEEDED               48930    /* Max Cyl 19 Bit Limit Exceeded */
#define OVERALL_COMMAND_TIMEOUT_FAILED              48931    /* Overall Command Timeout */
#define STROKE_DELTA_LIMIT_EXCEEDED                 48932    /* Stroke Delta Limit Exceeded */
#define REQUESTED_BYTES_BEYOND_END_OF_FILE          48933    /* Requested bytes beyond end of file */
#define HOST_RETURNED_MORE_BYTES_THAN_EXPECTED      48934    /* Host returned more bytes than expected */
#define PRESSURE_OUT_OF_BOUNDS                      48935    /* Pressure Out of Bounds */
#define THERMAL_ANNEALING_ATTEMPTED_EXCEEDED        48937    /* Thermal Annealing Attempted Limit Exceeded*/
#define THERMAL_ANNEALING_RECOVERED_EXCEEDED        48938    /* Thermal Annealing Recovered Limit Exceeded*/
#define NO_FRAME_NOISE_FLOOR_DATA                   48939    /* No frame data for baseline noise floor data */
#define BAD_HSC_MEASUREMENT                         48940    /* Bad Harmonic Sensor Circuit Measurement */
#define NO_BER_BELOW_THRESHOLD_FOUND                48941    /* No BER below the threshold found */
#define MASTER_HEAT_DISABLED                        48942    /* Master heat disabled */
#define INTERNAL_ERROR                              48944    /* Internal firmware error has occurred */
#define NUMBERED_PARAMS_NOT_SUPPORTED               48946    /* Numbered params unsupported for test */
#define POLY_ZAP_NOT_ENABLED                        48949    /* Poly ZAP not enabled */
#define INVALID_CHANNEL_LIST_STATE                  48951    /* Invalid channel list state */
#define INVALID_ACTUATOR_POSITION                   48952    /* Invalid actuator position */
#define INVALID_DRIVE_STATE                         48957    /* Invalid drive state */
#define INVALID_SERVO_COMMAND_TYPE                  48958    /* Invalid servo command type */
#define INVALID_SERVO_COMMAND_VERSION               48959    /* Invalid servo command version */
#define INVALID_READER_ELEMENT                      48960    /* Invalid reader element */
#define CSEFW_DETECTED_SIGNATURE_MISMATCH           48970    /* CSEFW Detected Signature Mismatch */
#define ZEST_CRC_MISCOMPARE_ON_READ                 48976    /* ZEST CRC miscompare on read */
#define TEST_BAND_ENCROACHES_NEXT_ZONE              48977    /* Test band encroaches next zone */
#define EXHAUSTED_REFERENCE_TRIES                   48978    /* Exhausted reference tries */
#define EXCEEDED_MAX_RETRYABLE_NOISE_FLOOR          48979    /* Exceeded max retryable noise floor */
#define EXCEEDED_NOISE_FLOOR_LIMIT                  48980    /* Exceeded noise floor limit */
#define WPE_READ_POSITION_NOT_FOUND                 48981    /* WPE reference position not found */
#define TRACK_ERASE_FAILED                          48982    /* Track erase failed */
#define EXCEEDED_MAX_ENCROACHMENT                   48983    /* Exceeded max encroachment */
#define EXCEEDED_MAX_WPE_DELTA                      48984    /* Exceeded max WPE delta */
#define FAILED_LINE_FIT                             48985    /* Failed line fit */
#define UNCONVERGED_CODEWORDS                       48987    /* Unconverged codewords on track */
#define ITPIC_DEFECT_CHECK_FAILED                   48988    /* iTPIC defect check failed */
#define ATTEMPTED_SEEK_TO_SKIP_TRACK                48991    /* Attempted seek to a skip track */
#define NOT_ENOUGH_DATA_POINTS_FOR_FIT              48992    /* Gap Timing Measurement Too Few Points */
#define CORRUPTED_OVLY_SYS_FILE                     49002    /* Overlay system file corrupted or absent */
#define ZERO_USED_AS_INCREMENT                      49005    /* Zero used as increment value */
#define NULL_POINTER_ERROR                          49007    /* Attempt to Use Null Pointer */
#define INCONSISTENT_HEAP_STATE                     49009    /* Inconsistent heap state */
#define PASSIVE_TA_SPEC_EXCEEDED                    49031    /* Passive TA Spec Exceeded */
#define EXCESSIVE_PHASE_DETECTED                    49040    /* Excessive Phase Detected */
#define INVALID_ACCLRM_CAL_TYPE                     49041    /* Invalid accelerometer cal type */
#define INVALID_ADC_SERIAL_ADDRESS_INDEX            49042    /* Invalid ADC serial address index */
#define INVALID_NUM_ADC_SAMPLES_PER_SECTOR          49043    /* Invalid num ADC samples per sector */
#define PWR_REG_SAVER_ALREADY_ENABLED               49044    /* Pwr Reg Saver has already been init */
#define INVALID_SERVO_RAM_ACCESS_TYPE               49045    /* Invalid Servo RAM access Type */
#define ZEST_UNSUPPORTED_TABLE_REVISION             49046    /* Unsupported ZEST table revision */
#define ZEST_UNSUPPORTED_COMPRESSION_TYPE           49047    /* Unsupported ZEST compression type */
#define ZEST_UNSUPPORTED_BYTES_PER_STEP             49048    /* Unsupported ZEST bytes per step */
#define ZEST_UNSUPPORTED_STEPS_PER_SEGMENT          49051    /* Unsupported ZEST steps per segment */
#define INVALID_ACCLRM_NOTCH_CAL_TYPE               49063    /* Invalid accelerometer notch cal type */
#define ACCLRM_NOTCH_CAL_F0_MIN_MAG_LIMIT_EXCEEDED  49064    /* Minimum F0 magnitude exceeded limits */
#define ACCLRM_NOTCH_CAL_OFFSET_LIMIT_EXCEEDED      49065    /* Error Check offset exceeded limits */
#define ACCLRM_NOTCH_CAL_P2P_LIMIT_EXCEEDED         49066    /* Error Check peak to peak exceeded limits */
#define ACCLRM_NOTCH_CAL_F0_MAG_LIMIT_EXCEEDED      49067    /* Error Check F0 mag exceeded limits */
#define INVALID_READER_SELECTION                    49068    /* Invalid reader selected */
#define EXCESSIVE_ENVIRONMENT_VARIATION             49069    /* T345: Burnish error excessive env. variation*/
#define ZERO_ENTRIES_ADDED                          49078    /* Can Not Add Defects to NOR */
#define UNSUPPORTED_SERVO_SYMBOL_TSE                49079    /* Servo symbol is not supported in TSE FW */
#define UNSUPPORTED_SERVO_SYMBOL_SERVO              49080    /* Servo symbol isnt supported in Servo FW */
#define BAD_R2R_GAP_VALUES_EXCEEDED_LIMIT           49089    /* Num bad samples for channel gap exceeded */
#define GAMMA_CONVERSION_FAILED                     49091    /* Gamma conversion failed */
#define NUMBER_OF_BANDS_INCORRECT                   49098    /* Number of bands specified did not match the number expected */
#define CM_CPY_SIGN_VER_FAILED                      49101    /* SignedCfg Signature Verification failed */
#define UACT_CAL_CMD_FAILED                         49104    /* Micro Actuator Calibration Command 0x00DF Failed */
#define R2R_DELTA_T_NOT_READY                       49105    /* R2R Cal, Delta T not ready */
#define R2R_M_VALUE_NOT_READY                       49106    /* R2R Cal, M value not ready */
#define INVALID_ADC_DATA                            49107    /* Invalid data recieved from the ADC */
#define MOTOR_FAULT                                 49108    /* Servo reported a motor fault */
#define TOO_MANY_CONSECUTIVE_BAD_SAMPLES            49116    /* Too many consecutive bad samples */
#define TOO_MANY_TOTAL_BAD_SAMPLES                  49117    /* Too many total bad samples */
#define R_SQUARED_VALUE_TOO_LOW                     49118    /* Polyfit R squared value below minimum */
#define ACLRMTR_OFFSET_GT_ZERO_AT_MIN_DAC           49119    /* Aclrmtr offset greater than 0 at min DAC */
#define ACLRMTR_OFFSET_LT_ZERO_AT_MAX_DAC           49120    /* Aclrmtr offset less than 0 at max DAC */
#define MIN_OP_LEFT_EXCEEDED                        49123    /* Minimum OverProvision Was Exceeded */
#define TOO_MANY_PROGRAM_ERRORS                     49124    /* Total number of program errors exceeded */
#define TOO_MANY_ERASE_ERRORS                       49125    /* Total number of erase errors exceeded */
#define HOST_SUPPLD_PARAMETER_VALUE_CONFLICT        49132    /* HOST-Suppld parameter values conflict. */
#define FW_SUPPLD_PARAMETER_VALUE_CONFLICT          49133    /* FW-Suppld parameter values conflict. */
#define UNDEFINED_LATTICE_FILTER_TYPE               49134    /* Undefined Lattice filter type */
#define NTZ_ERROR_COLLECTING_NPQ_SEAMLESS           49135    /* NTZ Error Collecting Npqseamless in find zone edges. */
#define NTZ_WRITE_FAILURE_LIMIT_EXCEEDED            49139    /* Exceeded NTZ write failure limit */
#define PRESSURE_TOO_HIGH                           49143    /* Pressure too high */
#define PRESSURE_TOO_LOW                            49144    /* Pressure too low */
#define NO_FLEXIO_SUPPORT                           49146    /* Drive does not support Flex IO */
#define HOST_SUPPLD_PARAM_RESERVED_BITS             49147    /* HOST-Supplied parameter reserved bits */
#define FW_SUPPLD_PARAM_RESERVED_BITS               49148    /* FW-Supplied parameter reserved bits */
#define READER_SELECT_FAILED                        49156    /* ReaderSelect Failure - Failed to Update Rap Reader*/
#define CFW_RW_SYSTEM_FAILURE                       49158    /* Controller firmware RW system failure */
#define INVALID_RW_MEDIA_PARTITION                  49159    /* Invalid RW media partition */
#define NTZ_INVALID_GAP_BETWEEN_BANDS               49160    /* Gap between two bands of dragontooth */
#define NTZ_ERROR_INVALID_PREVIOUS_WIRRO_DATA       49161    /* Error in previous WIRRO data for tiling */
#define INVALID_SWITCH_CASE                         49162    /* Invalid switch case encountered */
#define NTZ_CURRENT_CAL_FAILURE                     49163    /* Dragontooth trajectory current calibration failed.*/
#define CSEFW_UNKNOWN_TEST_FAILURE                  49170    /* CSEFW Failed for unknown reason */
#define INVALID_LOCATION_REQ                        49173    /* Partition not allowed at requested loation */
#define FLEX_TOUCH_TOP_COVER                        49172    /* screen clicking noise from flex touch top cover */
#define INSUFFICIENT_NUM_HEAD_OFFSET_MEASUREMENTS   49183    /* Insufficient num head offset measurement */
#define WORST_CASE_OFFSET_NOT_CALCULATED            49184    /* Worstcase head offset not calculated */
#define MAX_WRT_RETRY_EXCEEDS_LIMIT                 49189    /* MAX_WRT_RETRY exceeds limit */

// -----------------------------------------------------------------------------
// ********************** Public Typedefs Section ******************************
// -----------------------------------------------------------------------------

typedef uint16 error_code_t;  // When using the error codes in codes.h, use this typedef to define variables/functions that return them.

