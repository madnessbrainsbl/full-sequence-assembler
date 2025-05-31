// Do NOT modify or remove this copyright and confidentiality notice!
//
// Copyright (c) 2001 - $Date: 2016/12/15 $ Seagate Technology, LLC.
//
// The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
// Portions are also trade secret. Any use, duplication, derivation, distribution
// or disclosure of this code, for any reason, not expressly authorized is
// prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
//
/*
* VCS Information:
*                 $File: //depot/TSE/Shared/source/parameters/param_cd.h $
*                 $Revision: #846 $
*                 $Change: 1169716 $
*                 $Author: curt.rogers $
*                 $DateTime: 2016/12/15 07:40:19 $
*/
/*******************************************************************************
*
*   description:
*              TSE Test Parameter ID Codes for test parameters
*              Every entry must have 2 components:
*                  #define <parameter_name>_PARM_C     <code #>
*                  #define <parameter_name>_PARM_P     <# of parameter values>  (The number of 16 bit chunks)
*              The 2 components must be grouped as shown.
*
***********************************************************************/
/****************************************************************************************************************************
*
*  ####   #    #  ##### #####   #     #     #####    ####  #####   #####    ####    ####     ##   #####  #    ####    #    #
*  #      # #  #    #   #    #    # #       #    #   #     #    #  #    #   #      #    #   #  #    #    #   #    #   # #  #
*  ###    #  # #    #   #####      #        #     #  ###   #####   #####    ###    #       ######   #    #   #    #   #  # #
*  #      #   ##    #   #    #     #        #    #   #     #       #    #   #      #    #  #    #   #    #   #    #   #   ##
*  #####  #    #    #   #     #    #        #####    ##### #       #     #  #####   ####   #    #   #    #    ####    #    #
*
*
*  #####    ####    #      ###    ####  #     #
*  #    #  #    #   #       #    #    #   # #
*  #####   #    #   #       #    #         #
*  #       #    #   #       #    #    #    #
*  #        ####    #####  ###    ####     #
*
* This policy is for the purpose of maintaining backward compatibility for a specified time period in order to allow TPE and
* FIS to use the same file (or derivative) for combined FW operations and multiple FW revisions.  It also provides for
* eventual replacement of deprecated entries in the FW system.  Changes to this policy require approval of TSE, TPE and FIS.
* This policy applies to all entries in this file (including those for tables not reported to FIS).
*
* Deleting entries from this file is strictly forbidden.
* All established entries must remain defined with the same code number.
*
* Replacement definitions are allowed for expired entries according to the following:
*   1) If an entry becomes obsolete (That is, no longer used in any of the firmware code bases that include this file.),
*      that entry must be date stamped with the deprecation date (last date the entry was required for FW compilation).
*   2) The date stamp will mark the beginning of the time period (1 year) for maintaining backward compatibility.
*      Example:
*         <Blank line should be inserted here for clarity>
*         // Deprecated 3/10/2008
*      Example:
*         <Blank line should be inserted here for clarity>
*         // Deprecated 3/10/2008
*         #define RZONE_DATA_PARM_C                         5
*         #define RZONE_DATA_PARM_P                         1
*
*      In this example, (assuming the maintenance period is 1 year) entry location 5 (RZONE_DATA) would be available for redefinition on 3/10/2009.
*
*   3) At the end of the backward compatibility maintenance time period, the entry will be available for redefinition.
*      On this date the new entry could be:
*         #define NEW_PARM_C                                5
*         #define NEW_PARM_P                                2
*         The NEW_PARM uses a 32 bit value, thus the change to 2 in the second row.
*
* If a change (other than deprecation) is needed in an established entry, a new entry must be made to incorporate that change.
*
*****************************************************************************************************************************/

/* ----------------------------------------------------------------------------
* Due to code space limitations in firmware, please CHECK THOROUGHLY to see if
* there is an existing parameter name that can be used instead of adding a new one.
*
* Keep entries in numeric order by code # for ease of maintenance.
*
* Update parm_tbl.c to match the corresponding firmware segment of this file when
* changes are made.
*
* DO NOT Exceed 24 characters in <parameter_name> (not counting _PARM_x).
*
* NOTE: This file is now segmented by firmware type (SELFTEST, IOTEST, SATATEST, ISETEST); Make
*       sure that any new entries are being added into the correct segment.
*
* ----------------------------------------------------------------------------*/

/* ----------------------------------------------------------------------------------------------------------------------------------------------
 UPS conversion Xref Notes:  Scope: Applies only to F3-trunk conversion process.
 1) All conversion entries must conform to the following format:
    (<Test#>,<NewName>_TPARCD,<TypeSize>,<BitValue>)
    Where:
      Test# is a Capital T followed by the test number with NO leading zeroes.
         "DEF" indicates the default conversion (Used in all tests that are not specifically identified by number).
         "NA" indicates Not Applicable and the conversion script must ignore the entire entry.

      NewName is the UPS parameter conversion name.
         "NA" indicates Not Applicable and the conversion script must ignore the entry for the specified test#.
         If this is a conversion to bit-mapped boolean BitValue must be valid.

      TypeSize is the number of bits (decimal) in each value (NOT the number of 16-bit chunks) for integer types, and an "F" or "D" respectively for single and double precision float.
         "NA" indicates Not Applicable.

      BitValue is the bit value for conversion to a bit-mapped boolean in a control word.
         "NA" if this is not a conversion to boolean.

 2) If any of the fields are NOT applicable they must be filled in with "NA", without the quotes.
 3) Multiple conversions for the same legacy name are permitted but require a separate parenthesized entry for each conversion.
 4) An "UNDEF" in any field (other than the first one), indicates an unfinished entry.
------------------------------------------------------------------------------------------------------------------------------------------------ */


// *******************  SELFTEST and Shared Parameter definitions  **************************************************
// Deprecated 4/14/2006
#define UNDEFINED_PARM_C                          0      // (NA,NA,NA,NA)
#define UNDEFINED_PARM_P                          1

#define CAP_HDA_SN_PARM_C                         1      // (T178,Cwrd4_TPARCD,16,0x8000)
#define CAP_HDA_SN_PARM_P                         0

#define FAM_ID_PARM_C                             2      // (DEF,FamId_TPARCD,16,NA)
#define FAM_ID_PARM_P                             1

#define PFM_ID_PARM_C                             3      // (DEF,PfmId_TPARCD,16,NA)
#define PFM_ID_PARM_P                             1

#define HD_COUNT_PARM_C                           4      // (DEF,HdCnt_TPARCD,16,NA)
#define HD_COUNT_PARM_P                           1

// Deprecated 4/14/2006
#define RZONE_DATA_PARM_C                         5      // (NA,NA,NA,NA)
#define RZONE_DATA_PARM_P                         1

#define CAP_WORD_PARM_C                           6      // (DEF,CapWrd_TPARCD,16,NA)
#define CAP_WORD_PARM_P                           3

#define WWN_PARM_C                                7      // (T178,Cwrd4_TPARCD,16,0x2000)
#define WWN_PARM_P                                0

#define DEPOP_PARM_C                              8      // (DEF,DpopMsk_TPARCD,16,NA)
#define DEPOP_PARM_P                              2

#define SAP_HDA_SN_PARM_C                         9      // (T178,Cwrd4_TPARCD,16,0x2000)
#define SAP_HDA_SN_PARM_P                         0

#define HD_TYPE_PARM_C                           10      // (DEF,HdTyp_TPARCD,16,NA)
#define HD_TYPE_PARM_P                            1

#define MAX_HEAD_PARM_C                          11      // (DEF,MxHd_TPARCD,16,NA)
#define MAX_HEAD_PARM_P                           1

#define PROD_ID_PARM_C                           12      // (DEF,ProdId_TPARCD,16,NA)
#define PROD_ID_PARM_P                            1

#define PES_FIFO_PARM_C                          13      // (DEF,PesFifo_TPARCD,16,NA)
#define PES_FIFO_PARM_P                           1

#define HD_TABLE_PARM_C                          14      // (T178,Cwrd4_TPARCD,16,0x1000)
#define HD_TABLE_PARM_P                           0

#define SAP_WORD_PARM_C                          15      // (DEF,SapWrd_TPARCD,16,NA)
#define SAP_WORD_PARM_P                           3

#define GAIN_CONTROL_PARM_C                      16      // (DEF,GainCtrl_TPARCD,16,NA)
#define GAIN_CONTROL_PARM_P                       1

#define MD_SYNC_PARM_C                           17      // (DEF,MdSync_TPARCD,16,NA)
#define MD_SYNC_PARM_P                            1

#define NO_ETF_PARM_C                            18      // (T136,Cwrd1_TPARCD,16,0x0010)
#define NO_ETF_PARM_P                             0

#define RV_CONTROL_PARM_C                        19      // (NA,NA,NA,NA)
#define RV_CONTROL_PARM_P                         0

#define WWN_USER_PARM_C                          20      // (DEF,Wwn_TPARCD,8,NA) (T542,WwnUse_TPARCD[0-3],16,NA)
#define WWN_USER_PARM_P                           4

#define RW_MODE_PARM_C                           21      // (DEF,RwMode_TPARCD,16,NA) (T598,WrRdMode_TPARCD,8,NA)
#define RW_MODE_PARM_P                            1

// Deprecated 08/02/2006
#define DELAY_WEDGES_PARM_C                      22      // (NA,NA,NA,NA)
#define DELAY_WEDGES_PARM_P                       1

#define CYL_RANGE_PARM_C                         23      // (DEF,CylRg_TPARCD,32,NA) (T545,CylRgSpec_TPARCD,16,NA)
#define CYL_RANGE_PARM_P                          2

#define HEAD_RANGE_PARM_C                        24      // (DEF,HdRg_TPARCD,8,NA) (T178,HdMsk_TPARCD,8,NA) (T532,HdRg_TPARCD,16,0x00FF) (T616,HdRg_TPARCD,16,NA) (T649,HdRg_TPARCD,16,NA) (T705,HdRg_TPARCD,16,0x00FF)
#define HEAD_RANGE_PARM_P                         1      // (T707,HdRg_TPARCD,16,0x00FF) (T707,HdRg_TPARCD,16,0xFF00) (T714,HdRg_TPARCD,16,NA) (T731,HdRg_TPARCD,16,0x00FF) (T731,HdRg_TPARCD,16,0xFF00)

#define PATTERN_BYTE_PARM_C                      25      // (DEF,PttrnByt_TPARCD,16,NA)
#define PATTERN_BYTE_PARM_P                       1

#define HEAD_CLAMP_PARM_C                        26      // (DEF,HdClmp_TPARCD,16,NA)
#define HEAD_CLAMP_PARM_P                         1

#define TRACK_LIMIT_PARM_C                       27      // (DEF,TrkLmt_TPARCD,16,NA) (T621,TrkLmt_TPARCD,8,0x00FF)
#define TRACK_LIMIT_PARM_P                        1

#define ZONE_LIMIT_PARM_C                        28      // (DEF,ZnLmt_TPARCD,16,NA)
#define ZONE_LIMIT_PARM_P                         1

#define CERT_OFFSET_PARM_C                       29      // (DEF,CertOfst_TPARCD,16,NA) (T126,Ofst_TPARCD,16,NA)
#define CERT_OFFSET_PARM_P                        1

#define READ_OFFSET_PARM_C                       30      // (DEF,RdOfst_TPARCD,16,NA)
#define READ_OFFSET_PARM_P                        1

#define CWORD1_PARM_C                            31      // (DEF,Cwrd1_TPARCD,16,NA) (T197,MeasMode_TPARCD,8,NA) (T212,NA,NA,NA) (T234,TstMode_TPARCD,16,NA)
#define CWORD1_PARM_P                             1

#define CWORD2_PARM_C                            32      // (DEF,Cwrd2_TPARCD,16,NA)
#define CWORD2_PARM_P                             1

#define FAIL_SAFE_PARM_C                         33      // (T235,Cwrd1_TPARCD,16,0x8000) (T233,Cwrd2_TPARCD,16,0x8000) (T34,Cwrd1_TPARCD,16,0x8000) (T37,Cwrd2_TPARCD,16,0x8000) (T103,Cwrd1_TPARCD,16,0x2000) (T152, Cwrd2_TPARCD,16,0x8000) (T151,Cwrd2_TPARCD,16,0x4000) (T251,Cwrd1_TPARCD,16,0x8000) (T195,Cwrd1_TPARCD,16,0x8000)
#define FAIL_SAFE_PARM_P                          0

#define RETRY_LIMIT_PARM_C                       34      // (DEF,RtryLmt_TPARCD,16,NA) (T556,RtryLmt_TPARCD,16,0x00FF) (T707,RtryLmt_TPARCD,16,0x00FF)
#define RETRY_LIMIT_PARM_P                        1

#define ASPERITY_OTF_PARM_C                      35      // (T117,Cwrd1_TPARCD,16,0x0100)
#define ASPERITY_OTF_PARM_P                       0

#define SFLAW_OTF_PARM_C                         36      // (T109,Cwrd4_TPARCD,16,0x0010)
#define SFLAW_OTF_PARM_P                          0

#define WRITE_CURRENT_PARM_C                     37      // (DEF,WrCrrnt_TPARCD,16,NA) (T178,PreampParm_TPARCD[0],8,NA) (T211,PreampParm_TPARCD[0],8,NA)
#define WRITE_CURRENT_PARM_P                      1

#define PASS_INDEX_PARM_C                        38      // (DEF,PassIdx_TPARCD,16,NA)
#define PASS_INDEX_PARM_P                         1

// Deprecated 4/14/2006
#define VITERBI_LEVEL_PARM_C                     39      // (NA,NA,NA,NA)
#define VITERBI_LEVEL_PARM_P                      1

#define GAIN_SCALE_PARM_C                        40      // (DEF,GainScal_TPARCD,16,NA)
#define GAIN_SCALE_PARM_P                         1

#define AGC_LOCK_PARM_C                          41      // (T109,Cwrd4_TPARCD,16,0x0020)
#define AGC_LOCK_PARM_P                           0

#define CAP_DOWNLOAD_PARM_C                      42      // (DEF,CapDwnld_TPARCD,16,NA)
#define CAP_DOWNLOAD_PARM_P                       4

#define DO_HSR_BODE_PARM_C                       43      // (NA,NA,NA,NA)
#define DO_HSR_BODE_PARM_P                        0

#define PLOT_TYPE_PARM_C                         44      // (DEF,PlotTyp_TPARCD,16,NA)
#define PLOT_TYPE_PARM_P                          1

#define MEASURE_PHASE_PARM_C                     45      // (T152,Cwrd2_TPARCD,16,0x2000)
#define MEASURE_PHASE_PARM_P                      0

#define FILTERS_PARM_C                           46      // (DEF,Fltr1_TPARCD,16,NA)
#define FILTERS_PARM_P                            1

#define SKIP_ON_FAIL_PARM_C                      47      // (T30,Cwrd1_TPARCD,16,0x1000) (T152,Cwrd2_TPARCD,16,0x1000)
#define SKIP_ON_FAIL_PARM_P                       0

#define TEST_CYL_PARM_C                          48      // (DEF,TstCyl_TPARCD,32,NA)
#define TEST_CYL_PARM_P                           2

#define FREQ_RANGE_PARM_C                        49      // (DEF,FrqRg_TPARCD,16,NA) (T29,RefClk_TPARCD,32,NA)
#define FREQ_RANGE_PARM_P                         2

#define FREQ_INCR_PARM_C                         50      // (DEF,FrqInc_TPARCD,16,NA)
#define FREQ_INCR_PARM_P                          1

#define NBR_NOTCHES_PARM_C                       51      // (DEF,NtchCnt_TPARCD,16,NA)
#define NBR_NOTCHES_PARM_P                        1

#define NBR_TFA_SAMPS_PARM_C                     52      // (DEF,TfaSampCnt_TPARCD,16,NA)
#define NBR_TFA_SAMPS_PARM_P                      1

#define NBR_MEAS_REPS_PARM_C                     53      // (DEF,MeasRepCnt_TPARCD,16,NA)
#define NBR_MEAS_REPS_PARM_P                      1

#define INJ_AMPL_PARM_C                          54      // (DEF,InjAmp_TPARCD,16,NA)
#define INJ_AMPL_PARM_P                           1

#define GAIN_LIMIT_PARM_C                        55      // (DEF,GainLmt_TPARCD,F,NA) (T12,GainCorrLmt_TPARCD,16,NA) (T13,DltaLmt_TPARCD,16,NA) (T177,MnGain_TPARCD,8,NA) (T564,DacGainTgt_TPARCD,16,NA)
#define GAIN_LIMIT_PARM_P                         1

#define ZETA_1_PARM_C                            56      // (DEF,Zta1_TPARCD,16,NA) (T43,TmdRg_TPARCD,8,NA)
#define ZETA_1_PARM_P                             2

#define ZETA_2_PARM_C                            57      // (DEF,Zta2_TPARCD,16,NA)
#define ZETA_2_PARM_P                             2

#define ZETA_3_PARM_C                            58      // (DEF,Zta3_TPARCD,16,NA)
#define ZETA_3_PARM_P                             2

#define PEAK_WIDTH_PARM_C                        59      // (DEF,PkWdth_TPARCD,16,NA)
#define PEAK_WIDTH_PARM_P                         1

#define ZETA_4_PARM_C                            60      // (DEF,Zta4_TPARCD,16,NA)
#define ZETA_4_PARM_P                             2

#define ZETA_5_PARM_C                            61      // (DEF,Zta5_TPARCD,16,NA)
#define ZETA_5_PARM_P                             2

#define SAP_ONLY_PARM_C                          62      // (NA,NA,NA,NA)
#define SAP_ONLY_PARM_P                           0

#define NUM_SVO_NOTCH_PARM_C                     63      // (NA,NA,NA,NA)
#define NUM_SVO_NOTCH_PARM_P                      1

#define PTS_UNDR_PK_PARM_C                       64      // (DEF,PtCntUndrPk_TPARCD,16,NA)
#define PTS_UNDR_PK_PARM_P                        1

#define SHARP_THRESH_PARM_C                      65      // (DEF,ShrpThrsh_TPARCD,F,NA)
#define SHARP_THRESH_PARM_P                       1

#define NOTCH_CONFIG_PARM_C                      66      // (DEF,NtchCnfg_TPARCD[0],16,NA)
#define NOTCH_CONFIG_PARM_P                       1

#define ZETA_6_PARM_C                            67      // (DEF,Zta6_TPARCD,16,NA)
#define ZETA_6_PARM_P                             2

#define GAIN_DELTA_PARM_C                        68      // (DEF,GainDlta_TPARCD,F,NA) (T619,GainDlta_TPARCD,16,0x8000)
#define GAIN_DELTA_PARM_P                         1

#define INJ_AMPL2_PARM_C                         69      // (DEF,InjAmpDual_TPARCD,16,NA)
#define INJ_AMPL2_PARM_P                          1

#define ERRS_B4_SFLAW_SCAN_PARM_C                70      // (DEF,ErrCntBfrSflwScn_TPARCD,16,NA)
#define ERRS_B4_SFLAW_SCAN_PARM_P                 1

#define SEEK_NUMS_PARM_C                         71      // (DEF,SkCnt_TPARCD,16,NA)
#define SEEK_NUMS_PARM_P                          1

#define SEEK_DELAY_PARM_C                        72      // (DEF,SkDly_TPARCD,16,NA)
#define SEEK_DELAY_PARM_P                         1

#define TIMER_OPTION_PARM_C                      73      // (DEF,Tmr_TPARCD,16,NA) (T37,Cwrd2_TPARCD,16,0x2000) (T549,TmrOptn_TPARCD,8,0x0001)
#define TIMER_OPTION_PARM_P                       1

#define REPORT_OPTION_PARM_C                     74      // (DEF,RprtOptn_TPARCD,16,NA) (T504,RprtSnsDta_TPARCD,8,NA)(T556,RprtOptn_TPARCD,16,0x000F) (T556,RprtOptn_TPARCD,16,0x0100) (T602,UdsRprtOptn_TPARCD,8,NA) (T608,RprtOptn_TPARCD,16,0x0001) (T618,RprtOptn_TPARCD,16,0x0001) (T621,RprtOptn_TPARCD,16,0x0001)
#define REPORT_OPTION_PARM_P                      1

#define SEEK_ERR_LIMIT_PARM_C                    75      // (DEF,SkErrLmt_TPARCD,16,NA) (T564,SkErrLmt_TPARCD,16,0x00FF)
#define SEEK_ERR_LIMIT_PARM_P                     1

#define UPDATE_ETF_PARM_C                        76      // (T37,Cwrd2_TPARCD,16,0x4000)
#define UPDATE_ETF_PARM_P                         1

#define BURNISH_PARM_C                           77      // (DEF,Brnsh_TPARCD,8,NA)
#define BURNISH_PARM_P                            2

#define THRESHOLD_PARM_C                         78      // (DEF,Thrsh_TPARCD,16,NA) (T213,BaslneBerLmt_TPARCD,F,NA)
#define THRESHOLD_PARM_P                          1

#define PATTERN_IDX_PARM_C                       79      // (DEF,PttrnIdx_TPARCD,16,NA)
#define PATTERN_IDX_PARM_P                        1

#define TAIL_LEN_PARM_C                          80      // (DEF,TailLen_TPARCD,32,NA) (T134,TaTailLen_TPARCD,8,NA)
#define TAIL_LEN_PARM_P                           2

#define S_OFFSET_PARM_C                          81      // (DEF,Ofst_TPARCD,16,NA)
#define S_OFFSET_PARM_P                           1

#define MAX_ASPS_PARM_C                          82      // (DEF,MxTaCnt_TPARCD,16,NA)
#define MAX_ASPS_PARM_P                           2

#define FILE_ID_PARM_C                           83      // (DEF,FileId_TPARCD,16,NA) (T527,FileId_TPARCD,16,0x000F) (T619,FileId_TPARCD,16,0x00FF)
#define FILE_ID_PARM_P                            1

#define BLOCK_PARM_C                             84      // (DEF,Blk_TPARCD,16,NA)
#define BLOCK_PARM_P                              3

#define NUM_HDS_SAM_SKP_TRK_PARM_C               85      // (DEF,SkpHdLmt_TPARCD,16,NA)
#define NUM_HDS_SAM_SKP_TRK_PARM_P                1

#define MIN_MAX_WRT_CUR_PARM_C                   86      // (DEF,WrCrrntRg_TPARCD,16,NA)
#define MIN_MAX_WRT_CUR_PARM_P                    2

#define ETF_LOG_DATE_PARM_C                      87      // (DEF,Dat_TPARCD,16,NA)
#define ETF_LOG_DATE_PARM_P                       2

#define AGC_INPUT_PARM_C                         88      // (DEF,AgcInpt_TPARCD,16,NA)
#define AGC_INPUT_PARM_P                          1

#define DO_SNO_PARM_C                            89      // (T152,Cwrd2_TPARCD,16,0x4000)
#define DO_SNO_PARM_P                             0

#define SNO_METHOD_PARM_C                        90      // (DEF,SnoMethd_TPARCD,16,NA)
#define SNO_METHOD_PARM_P                         1

#define PEAK_GAIN_MIN_PARM_C                     91      // (DEF,PkGainMn_TPARCD,F,NA)
#define PEAK_GAIN_MIN_PARM_P                      1

#define W_NUM_DEN_PARM_C                         92      // (DEF,Wdth_TPARCD,16,NA)
#define W_NUM_DEN_PARM_P                          2

#define PEAK_SUMMARY_PARM_C                      93      // (DEF,PkSmry_TPARCD,16,NA)
#define PEAK_SUMMARY_PARM_P                       1

#define SET_ANY_REG_PARM_C                       94      // (T177,Atten_TPARCD,8,NA)
#define SET_ANY_REG_PARM_P                        2

#define SAP_DOWNLOAD_PARM_C                      95      // (DEF,SapDwnld_TPARCD,16,NA)
#define SAP_DOWNLOAD_PARM_P                       4

#define BER_RANGE_PARM_C                         96      // (NA,NA,NA,NA)
#define BER_RANGE_PARM_P                          2

#define MAX_BLOCK_COUNT_PARM_C                   97      // (DEF,MxBlkCnt_TPARCD,16,NA) (T531,MxBlkCnt_TPARCD,32,NA)
#define MAX_BLOCK_COUNT_PARM_P                    2

#define DEFECT_LENGTH_PARM_C                     98      // (DEF,DfctLen_TPARCD,16,NA)
#define DEFECT_LENGTH_PARM_P                      1

#define ERR_TABLE_SCALE_PARM_C                   99      // (NA,NA,NA,NA)
#define ERR_TABLE_SCALE_PARM_P                    1

#define CROSSING_PARM_C                         100      // (NA,NA,NA,NA)
#define CROSSING_PARM_P                           0

#define TEST_HEAD_PARM_C                        101      // (DEF,TstHd_TPARCD,8,NA) (T178,HdRg_TPARCD,8,NA) (T228,HdRg_TPARCD,8,NA) (T238,HdRg_TPARCD,8,NA) (T252,NA,NA,NA) (T515,TstHd_TPARCD,16,NA) (T529,TstHd_TPARCD,16,0x00FF) (T556,TstHd_TPARCD,16,NA)
#define TEST_HEAD_PARM_P                          1      // (T615,TstHd_TPARCD,16,0x00FF) (T620,TstHd_TPARCD,16,0x000F) (T620,TstHd_TPARCD,16,0x0F00) (T621,TstHd_TPARCD,16,0x00FF) (T707,TstHd_TPARCD,16,0x000F) (T1509,TstHd_TPARCD,16,NA) (T5509,TstHd_TPARCD,16,NA)

#define PATTERNS_PARM_C                         102      // (DEF,Pttrn_TPARCD,8,NA) (T102,WrdPttrn_TPARCD,16,NA) (T141,WrdPttrn_TPARCD,16,NA)
#define PATTERNS_PARM_P                           3

#define SQZ_PATTERNS_PARM_C                     103      // (DEF,SqzPttrn_TPARCD,8,NA)
#define SQZ_PATTERNS_PARM_P                       2

#define TARGET_TRK_WRITES_PARM_C                104      // (DEF,TgtTrkWrCnt_TPARCD,8,NA) (T234,WrCnt_TPARCD,16,NA) (T213,WrCnt_TPARCD,16,NA)
#define TARGET_TRK_WRITES_PARM_P                  1

#define NUM_SQZ_WRITES_PARM_C                   105      // (DEF,SqzWrCnt_TPARCD,16,NA)
#define NUM_SQZ_WRITES_PARM_P                     1

#define SQZ_OFFSET_PARM_C                       106      // (DEF,SqzOfst_TPARCD,16,NA)
#define SQZ_OFFSET_PARM_P                         1

#define NUM_SAMPLES_PARM_C                      107      // (DEF,SampCnt_TPARCD,16,NA) (T102,MxItr_TPARCD,16,NA)
#define NUM_SAMPLES_PARM_P                        1

#define DIS_WEDGES_PARM_C                       108      // (NA,NA,NA,NA)
#define DIS_WEDGES_PARM_P                         1

#define ZONE_POSITION_PARM_C                    109      // (DEF,ZnPsn_TPARCD,16,NA) (T1509,ZnPsn_TPARCD[0-2],16,NA) (T5509,ZnPsn_TPARCD[0-2],16,NA)
#define ZONE_POSITION_PARM_P                      1

#define DISCARDED_BYTES_PARM_C                  110      // (NA,NA,NA,NA)
#define DISCARDED_BYTES_PARM_P                    1

#define NON_DIS_WEDGES_PARM_C                   111      // (DEF,NonDisWdgCnt_TPARCD,16,NA)
#define NON_DIS_WEDGES_PARM_P                     1

#define INIT_WC_PARM_C                          112      // (DEF,InitWrCrrnt_TPARCD,8,NA)
#define INIT_WC_PARM_P                            1

#define NON_DIS_BYTES_PARM_C                    113      // (NA,NA,NA,NA)
#define NON_DIS_BYTES_PARM_P                      1

#define VITERBI_THRESHOLD_PARM_C                114      // (DEF,VtrbiThrsh_TPARCD,16,NA)
#define VITERBI_THRESHOLD_PARM_P                  1

#define RESULTS_RETURNED_PARM_C                 115      // (DEF,RprtOptn_TPARCD,16,NA) (T74,RprtLvl_TPARCD,16,NA)
#define RESULTS_RETURNED_PARM_P                   1

#define MIN_CAND_PARM_C                         116      // (DEF,MnCand_TPARCD,16,NA)
#define MIN_CAND_PARM_P                           1

#define REG_TO_OPT1_PARM_C                      117      // (DEF,OptReg00_TPARCD,16,NA)
#define REG_TO_OPT1_PARM_P                        4

#define REG_TO_OPT1_EXT_PARM_C                  118      // (DEF,OptRegExt00_TPARCD,16,NA)
#define REG_TO_OPT1_EXT_PARM_P                    3

#define REG_TO_OPT2_PARM_C                      119      // (DEF,OptReg01_TPARCD,16,NA)
#define REG_TO_OPT2_PARM_P                        4

#define REG_TO_OPT2_EXT_PARM_C                  120      // (DEF,OptRegExt01_TPARCD,16,NA)
#define REG_TO_OPT2_EXT_PARM_P                    3

#define REG_TO_OPT3_PARM_C                      121      // (DEF,OptReg02_TPARCD,16,NA)
#define REG_TO_OPT3_PARM_P                        4

#define REG_TO_OPT3_EXT_PARM_C                  122      // (DEF,OptRegExt02_TPARCD,16,NA)
#define REG_TO_OPT3_EXT_PARM_P                    3

#define REG_TO_OPT4_PARM_C                      123      // (DEF,OptReg03_TPARCD,16,NA)
#define REG_TO_OPT4_PARM_P                        4

#define REG_TO_OPT4_EXT_PARM_C                  124      // (DEF,OptRegExt03_TPARCD,16,NA)
#define REG_TO_OPT4_EXT_PARM_P                    3

#define FLAT_BUCKET_VALUE_PARM_C                125      // (NA,NA,NA,NA)
#define FLAT_BUCKET_VALUE_PARM_P                  1

#define COG_THRESHOLD_OFFSET_PARM_C             126      // (DEF,CogThrshOfst_TPARCD,16,NA)
#define COG_THRESHOLD_OFFSET_PARM_P               1

#define ZAP_OTF_PARM_C                          127      // (NA,NA,NA,NA)
#define ZAP_OTF_PARM_P                            0

#define SAP_USE_ETF_PARM_C                      128      // (NA,NA,NA,NA)
#define SAP_USE_ETF_PARM_P                        0

#define SAP_USE_FLASH_PARM_C                    129      // (NA,NA,NA,NA)
#define SAP_USE_FLASH_PARM_P                      0

#define RD_CONST_COEFF_PARM_C                   130      // (DEF,RdConstCoef_TPARCD,16,NA)
#define RD_CONST_COEFF_PARM_P                     1

#define RD_STD_LIMIT_PARM_C                     131      // (DEF,RdStdevLmt_TPARCD,16,NA)
#define RD_STD_LIMIT_PARM_P                       1

#define WRT_CONST_COEFF_PARM_C                  132      // (DEF,WrConstCoef_TPARCD,16,NA)
#define WRT_CONST_COEFF_PARM_P                    1

#define WRT_STD_LIMIT_PARM_C                    133      // (DEF,WrStdevLmt_TPARCD,16,NA)
#define WRT_STD_LIMIT_PARM_P                      1

#define CURRENT_2_POSITION_PARM_C               134      // (NA,NA,NA,NA)
#define CURRENT_2_POSITION_PARM_P                 1

#define SEEK_STEP_PARM_C                        135      // (DEF,SkInc_TPARCD,16,NA)
#define SEEK_STEP_PARM_P                          1

#define STD_DEV_LIMIT_PARM_C                    136      // (DEF,StdevLmt_TPARCD,16,NA)
#define STD_DEV_LIMIT_PARM_P                      1

#define PES_REVS_PARM_C                         137      // (DEF,PesRvs_TPARCD,16,NA)
#define PES_REVS_PARM_P                           1

#define M0_FREQ_RANGE_PARM_C                    138      // (DEF,MFrqRg0_TPARCD,16,NA)
#define M0_FREQ_RANGE_PARM_P                      2

#define M1_FREQ_RANGE_PARM_C                    139      // (DEF,MFrqRg1_TPARCD,16,NA)
#define M1_FREQ_RANGE_PARM_P                      2

#define M2_FREQ_RANGE_PARM_C                    140      // (DEF,MFrqRg2_TPARCD,16,NA)
#define M2_FREQ_RANGE_PARM_P                      2

#define M3_FREQ_RANGE_PARM_C                    141      // (DEF,MFrqRg3_TPARCD,16,NA)
#define M3_FREQ_RANGE_PARM_P                      2

#define M4_FREQ_RANGE_PARM_C                    142      // (DEF,MFrqRg4_TPARCD,16,NA)
#define M4_FREQ_RANGE_PARM_P                      2

#define M5_FREQ_RANGE_PARM_C                    143      // (DEF,MFrqRg5_TPARCD,16,NA)
#define M5_FREQ_RANGE_PARM_P                      2

#define M6_FREQ_RANGE_PARM_C                    144      // (DEF,MFrqRg6_TPARCD,16,NA)
#define M6_FREQ_RANGE_PARM_P                      2

#define OFFSET_SETTING_PARM_C                   145      // (DEF,OfstSetg_TPARCD,16,NA)
#define OFFSET_SETTING_PARM_P                     3

#define MJOG_COG_THRESHOLD_PARM_C               146      // (DEF,MjogCogThrsh_TPARCD,32,NA)
#define MJOG_COG_THRESHOLD_PARM_P                 1

#define MJOG_DELTA_THRESHOLD_PARM_C             147      // (DEF,MjogDltaThrsh_TPARCD,16,NA)
#define MJOG_DELTA_THRESHOLD_PARM_P               1

#define MJOG_FOM_THRESHOLD_PARM_C               148      // (DEF,MjogFomThrsh_TPARCD,F,NA)
#define MJOG_FOM_THRESHOLD_PARM_P                 1

#define NUM_ADJ_ERASE_PARM_C                    149      // (DEF,AdjcntEraseCnt_TPARCD,16,NA) (T695,NumAdjErase_TPARCD,8,NA)
#define NUM_ADJ_ERASE_PARM_P                      1

#define LOAD_OFFSET_PARM_C                      150      // (DEF,LdOfst_TPARCD,16,NA) (T80,MovgBckOff_TPARCD,16,NA)
#define LOAD_OFFSET_PARM_P                        1

#define MARGIN_LIMIT_PARM_C                     151      // (DEF,MargnLmt_TPARCD,16,NA)
#define MARGIN_LIMIT_PARM_P                       1

#define ZN_THRESHOLD_PARM_C                     152      // (DEF,ZnThrsh_TPARCD,16,NA)
#define ZN_THRESHOLD_PARM_P                       1

#define ADAPTIVES_PARM_C                        153      // (DEF,Cwrd4_TPARCD,16,NA) (T151,Cwrd3_TPARCD,16,NA)
#define ADAPTIVES_PARM_P                          1

#define MRBIAS_SAMPLES_PARM_C                   154      // (DEF,MrBiasSampCnt_TPARCD,16,NA)
#define MRBIAS_SAMPLES_PARM_P                     1

#define MRBIAS_MAXV_PARM_C                      155      // (DEF,MrBiasMxVltg_TPARCD,16,NA)
#define MRBIAS_MAXV_PARM_P                        1

#define PRINT_PARM_C                            156      // (DEF,DramFailLmt_TPARCD,16,NA)
#define PRINT_PARM_P                              1

#define TRGT_REWRITE_PARM_C                     157      // (DEF,TgtReWr_TPARCD,16,NA)
#define TRGT_REWRITE_PARM_P                       0

#define TRGT_PRE_READS_PARM_C                   158      // (DEF,TgtPreRdCnt_TPARCD,16,NA)
#define TRGT_PRE_READS_PARM_P                     1

#define TRGT_READS_PARM_C                       159      // (DEF,TgtRdCnt_TPARCD,16,NA)
#define TRGT_READS_PARM_P                         1

#define TRGT_ADC_SAT_PARM_C                     160      // (NA,NA,NA,NA)
#define TRGT_ADC_SAT_PARM_P                       0

#define TRGT_FIR_SAT_PARM_C                     161      // (NA,NA,NA,NA)
#define TRGT_FIR_SAT_PARM_P                       2

#define IGNORE_UNVER_LIMIT_PARM_C               162      // (T109,Cwrd4_TPARCD,16,0x0040)
#define IGNORE_UNVER_LIMIT_PARM_P                 0

#define CSM_DMAPCNT_PARM_C                      163      // (NA,NA,NA,NA)
#define CSM_DMAPCNT_PARM_P                        1

#define CSM_THRESHOLD_PARM_C                    164      // (DEF,CsmThrsh_TPARCD,16,NA)
#define CSM_THRESHOLD_PARM_P                      1

#define CYL_SHIFT_PARM_C                        165      // (DEF,CylShft_TPARCD,32,NA)
#define CYL_SHIFT_PARM_P                          2

#define MAX_SVO_FLW_FAILURES_PARM_C             166      // (DEF,MxSflwFailCnt_TPARCD,16,NA)
#define MAX_SVO_FLW_FAILURES_PARM_P               1

#define PER_TRK_SFLW_LIM_PARM_C                 167      // (DEF,PerTrkSflwLmt_TPARCD,16,NA)
#define PER_TRK_SFLW_LIM_PARM_P                   1

#define CSM_START_DELAY_PARM_C                  168      // (NA,NA,NA,NA)
#define CSM_START_DELAY_PARM_P                    1

#define ADAPT_FIR_PARM_C                        169      // (NA,AdaptFir_TPARCD,8,NA)
#define ADAPT_FIR_PARM_P                          1

#define RW_REG_VAL_PARM_C                       170      // (NA,NA,NA,NA)
#define RW_REG_VAL_PARM_P                         2

#define D_WDG_SZ_ADJ_PARM_C                     171      // (NA,NA,NA,NA)
#define D_WDG_SZ_ADJ_PARM_P                       1

#define TRGT_PATH_WRITES_PARM_C                 172      // (NA,NA,NA,NA)
#define TRGT_PATH_WRITES_PARM_P                   1

#define TRGT_QUALIFIER_PARM_C                   173      // (NA,NA,NA,NA)
#define TRGT_QUALIFIER_PARM_P                     1

#define MIN_CQM_PARM_C                          174      // (DEF,MnCqm_TPARCD,16,NA)
#define MIN_CQM_PARM_P                            1

#define WRT_CUR_SMOOTHING_PARM_C                175      // (NA,NA,NA,NA)
#define WRT_CUR_SMOOTHING_PARM_P                  1

#define TK0_LIMIT_PARM_C                        176      // (DEF,TrkZroLmt_TPARCD,16,NA)
#define TK0_LIMIT_PARM_P                          1

#define PAD_TK_VALUE_PARM_C                     177      // (DEF,PadTrk_TPARCD,16,NA)
#define PAD_TK_VALUE_PARM_P                       1

#define ID_PAD_TK_VALUE_PARM_C                  178      // (DEF,IdPadTrkVal_TPARCD,16,NA)
#define ID_PAD_TK_VALUE_PARM_P                    1

#define TK0_VALUE_PARM_C                        179      // (DEF,TrkZroVal_TPARCD,16,NA)
#define TK0_VALUE_PARM_P                          2

#define FINAL_LSHIFT_VALUE_PARM_C               180      // (DEF,FinalShftVal_TPARCD,16,NA)
#define FINAL_LSHIFT_VALUE_PARM_P                 1

#define DRIVE_TPI_VALUE_PARM_C                  181      // (DEF,DrvTpi_TPARCD,32,NA)
#define DRIVE_TPI_VALUE_PARM_P                    2

#define TRGT_TEST_THRESH_PARM_C                 182      // (DEF,TgtTstThrsh_TPARCD,16,NA)
#define TRGT_TEST_THRESH_PARM_P                   1

#define RETEST_DELAY_PARM_C                     183      // (DEF,ReTstDly_TPARCD,16,NA)
#define RETEST_DELAY_PARM_P                       1

#define NO_TMD_LMT_PARM_C                       184      // (DEF,NoTmdLmt_TPARCD,16,NA)
#define NO_TMD_LMT_PARM_P                         1

#define BAD_ID_LMT_PARM_C                       185      // (DEF,BadIdLmt_TPARCD,16,NA)
#define BAD_ID_LMT_PARM_P                         1

#define UNSAFE_LMT_PARM_C                       186      // (DEF,UnsfLmt_TPARCD,16,NA)
#define UNSAFE_LMT_PARM_P                         1

#define LOOP_CNT_PARM_C                         187      // (DEF,LoopCnt_TPARCD,16,NA)
#define LOOP_CNT_PARM_P                           1

#define FIRST_SECTOR_UP_PARM_C                  188      // (T197,Cwrd1_TPARCD,16,0x0001)
#define FIRST_SECTOR_UP_PARM_P                    0

#define PRETEST_SEEK_PARM_C                     189      // (T163,Cwrd1_TPARCD,16,0x0008)
#define PRETEST_SEEK_PARM_P                       0

#define RETEST_UNSAFE_HDS_PARM_C                190      // (T163,Cwrd1_TPARCD,16,0x0010)
#define RETEST_UNSAFE_HDS_PARM_P                  0

#define READ_MODE_PARM_C                        191      // (T163,Cwrd1_TPARCD,16,0x0001)
#define READ_MODE_PARM_P                          0

#define RETEST_UNSAFE_LMT_PARM_C                192      // (DEF,ReTstUnsfLmt_TPARCD,16,NA)
#define RETEST_UNSAFE_LMT_PARM_P                  1

#define INTERVAL_NUM_PARM_C                     193      // (DEF,IntrvlIdx_TPARCD,32,NA)
#define INTERVAL_NUM_PARM_P                       1

#define INTERVAL_SIZE_PARM_C                    194      // (DEF,IntrvlSz_TPARCD,32,NA) (T45,Wdw_TPARCD,16,NA) (T43,Rg_TPARCD,16,NA)
#define INTERVAL_SIZE_PARM_P                      1

#define MARVELL_ASPERITY_OTF_PARM_C             195      // (NA,NA,NA,NA)
#define MARVELL_ASPERITY_OTF_PARM_P               0

#define MARVELL_TA_THRESHOLD_PARM_C             196      // (NA,NA,NA,NA)
#define MARVELL_TA_THRESHOLD_PARM_P               1

#define ZN_WEIGHTS_PARM_C                       197      // (NA,NA,NA,NA)
#define ZN_WEIGHTS_PARM_P                         2

#define SET_OCLIM_PARM_C                        198      // (DEF,Oclim_TPARCD,16,NA)
#define SET_OCLIM_PARM_P                          1

#define MARVELL_THRESH_LIMIT_PARM_C             199      // (DEF,ThrshLmt_TPARCD,16,NA)
#define MARVELL_THRESH_LIMIT_PARM_P               1

#define UPDATE_FR_ETF_PARM_C                    200      // (NA,NA,NA,NA)
#define UPDATE_FR_ETF_PARM_P                      0

#define SEEK_LENGTH_PARM_C                      201      // (DEF,SkLen_TPARCD,32,NA) (T10,VcmSk_TPARCD,16,NA)
#define SEEK_LENGTH_PARM_P                        2

#define SEEK_COUNT_PARM_C                       202      // (DEF,SkCnt_TPARCD,16,NA) (T136,ExcitSkCnt_TPARCD,16,NA) (T151,Cwrd2_TPARCD,16,0x2000) (T532,SkCnt_TPARCD,16,0x000F) (T549,SkCnt_TPARCD,16,0x00FF)
#define SEEK_COUNT_PARM_P                         1

#define MIN_HEAD_SKEW_VALUE_PARM_C              203      // (DEF,MnHdSkew_TPARCD,16,NA)
#define MIN_HEAD_SKEW_VALUE_PARM_P                1

#define LSHIFT_VALUE_PARM_C                     204      // (DEF,Scal_TPARCD,16,NA)
#define LSHIFT_VALUE_PARM_P                       1

#define TI_FILE_ID_PARM_C                       205      // (DEF,TiFileId_TPARCD,16,NA) (T149,NA,NA,NA)
#define TI_FILE_ID_PARM_P                         1

#define AGERE_FILE_ID_PARM_C                    206      // (DEF,AgFileId_TPARCD,16,NA) (T149,NA,NA,NA)
#define AGERE_FILE_ID_PARM_P                      1

#define WEDGE_LIMIT_PARM_C                      207      // (NA,NA,NA,NA)
#define WEDGE_LIMIT_PARM_P                        1

#define LENGTH_LIMIT_PARM_C                     208      // (DEF,LenLmt_TPARCD,16,NA) (T134,TaLmt_TPARCD[0],16,NA)
#define LENGTH_LIMIT_PARM_P                       1

#define START_CYL_PARM_C                        209      // (DEF,CylRg_TPARCD[0],32,NA) (T532,StrtCyl_TPARCD,32,NA) (T549,StrtCyl_TPARCD,32,NA) (T551,StrtLba_TPARCD,64,0xFFFF) (T551,StrtLba_TPARCD,64,0xFFFF0000) (T618,StrtCyl_TPARCD,32,NA) (T620,StrtCyl_TPARCD,32,NA) (T649,CylRg_TPARCD[0],32,NA) 
#define START_CYL_PARM_P                          2      // (T705,StrtCyl_TPARCD,32,NA) (T707,StrtCyl_TPARCD,32,0x00FFFFFF) (T731,StrtCyl_TPARCD,32,NA)

#define END_CYL_PARM_C                          210      // (DEF,CylRg_TPARCD[1],32,NA) (T532,EndCyl_TPARCD,32,NA) (T549,EndCyl_TPARCD,32,NA) (T549,EndCyl_TPARCD,32,0xFF00) (T618,EndCyl_TPARCD,32,NA) (T649,CylRg_TPARCD[1],32,NA) 
#define END_CYL_PARM_P                            2      // (T705,EndCyl_TPARCD,32,NA) (T707,EndCyl_TPARCD,32,0x00FFFFFF) (T731,EndCyl_TPARCD,32,NA)                                         

#define INITIAL_DELAY_PARM_C                    211      // (DEF,InitDly_TPARCD,16,NA)
#define INITIAL_DELAY_PARM_P                      1

#define FINAL_DELAY_PARM_C                      212      // (DEF,FinalDly_TPARCD,16,NA)
#define FINAL_DELAY_PARM_P                        1

#define DELAY_INCREMENT_PARM_C                  213      // (DEF,DlyInc_TPARCD,16,NA)
#define DELAY_INCREMENT_PARM_P                    1

#define SEEK_TYPE_PARM_C                        214      // (DEF,SkTyp_TPARCD,16,NA)
#define SEEK_TYPE_PARM_P                          1

#define NUM_WORST_UNSAFE_PARM_C                 215      // (DEF,WrstUnsfCnt_TPARCD,16,NA)
#define NUM_WORST_UNSAFE_PARM_P                   1

#define DELAY_B4_RETRY_PARM_C                   216      // (DEF,DlyBfrRtry_TPARCD,16,NA)
#define DELAY_B4_RETRY_PARM_P                     1

#define UNSAFE_MAX_LIMIT_PARM_C                 217      // (DEF,UnsfLmt_TPARCD,16,NA)
#define UNSAFE_MAX_LIMIT_PARM_P                   1

#define START_HARM_PARM_C                       218      // (DEF,StrtHrm_TPARCD,16,NA)
#define START_HARM_PARM_P                         1

#define REVS_PARM_C                             219      // (DEF,Rvs_TPARCD,16,NA)
#define REVS_PARM_P                               1

#define MAX_ITERATION_PARM_C                    220      // (DEF,MxItr_TPARCD,16,NA) (T695,MxItr_TPARCD,8,NA)
#define MAX_ITERATION_PARM_P                      1

#define WZAP_MABS_RRO_LIMIT_PARM_C              221      // (DEF,WrMabsRroLmt_TPARCD,16,NA)
#define WZAP_MABS_RRO_LIMIT_PARM_P                1

#define RZAP_MABS_RRO_LIMIT_PARM_C              222      // (DEF,SecRdMabsRroLmt_TPARCD,16,NA)
#define RZAP_MABS_RRO_LIMIT_PARM_P                1

#define AUDIT_INTERVAL_PARM_C                   223      // (DEF,AudtIntrvl_TPARCD,16,NA)
#define AUDIT_INTERVAL_PARM_P                     1

#define GAIN_PARM_C                             224      // (DEF,Gain_TPARCD,16,NA)
#define GAIN_PARM_P                               1

#define PRE_WRITES_PARM_C                       225      // (DEF,PreWrCnt_TPARCD,16,NA)
#define PRE_WRITES_PARM_P                         1

#define CONVERGE_LIM_1_PARM_C                   226      // (DEF,CnvrgLmt1_TPARCD,16,NA)
#define CONVERGE_LIM_1_PARM_P                     1

#define CONVERGE_LIM_2_PARM_C                   227      // (NA,NA,NA,NA)
#define CONVERGE_LIM_2_PARM_P                     1

#define FREQUENCY_PARM_C                        228      // (DEF,Frq_TPARCD,16,NA)
#define FREQUENCY_PARM_P                          1

#define GAIN_DELTA_LIM_PARM_C                   229      // (DEF,MxSkewDlta_TPARCD,16,NA)
#define GAIN_DELTA_LIM_PARM_P                     1

#define INIT_PT_PT_GAIN_LIM_PARM_C              230      // (NA,NA,NA,NA)
#define INIT_PT_PT_GAIN_LIM_PARM_P                1

#define FINAL_PT_PT_GAIN_LIM_PARM_C             231      // (NA,NA,NA,NA)
#define FINAL_PT_PT_GAIN_LIM_PARM_P               1

#define INIT_PK_PK_GAIN_LIM_PARM_C              232      // (NA,NA,NA,NA)
#define INIT_PK_PK_GAIN_LIM_PARM_P                1

#define FINAL_PK_PK_GAIN_LIM_PARM_C             233      // (DEF,FinalPkPkGainLmt_TPARCD,16,NA)
#define FINAL_PK_PK_GAIN_LIM_PARM_P               1

#define OB_SECT_LMT_PARM_C                      234      // (DEF,BadSampLmt_TPARCD,16,NA)
#define OB_SECT_LMT_PARM_P                        1

#define SFLAWB4_TRK_LIMIT_PARM_C                235      // (DEF,SflwBfrTrkLmt_TPARCD,16,NA)
#define SFLAWB4_TRK_LIMIT_PARM_P                  1

#define BYTE_WINDOW_PARM_C                      236      // (DEF,BytWdw_TPARCD,16,NA)
#define BYTE_WINDOW_PARM_P                        1

#define TRK_SPACING_PARM_C                      237      // (DEF,TrkSpcg_TPARCD,16,NA)
#define TRK_SPACING_PARM_P                        1

#define TAIL_SIZES_PARM_C                       238      // (DEF,TailSz_TPARCD,16,NA)
#define TAIL_SIZES_PARM_P                         4

#define FILL_BACKSIZE_PARM_C                    239      // (DEF,FillBackSz_TPARCD,16,NA)
#define FILL_BACKSIZE_PARM_P                      1

#define MAX_TOTAL_FLAWS_PARM_C                  240      // (DEF,MxTtlFlawCnt_TPARCD,32,NA) (T130,NA,NA,NA)
#define MAX_TOTAL_FLAWS_PARM_P                    1

#define PROCEED_TILL_END_PARM_C                 241      // (NA,Boolean,T117,NA)
#define PROCEED_TILL_END_PARM_P                   0

#define LARGE_FLAW_LEN_PARM_C                   242      // (DEF,LrgFlawLen_TPARCD,16,NA)
#define LARGE_FLAW_LEN_PARM_P                     1

#define SERVO_TAIL_SIZE_PARM_C                  243      // (DEF,SvoTailSz_TPARCD,16,NA)
#define SERVO_TAIL_SIZE_PARM_P                    1

#define MEDIA_DAMAGE_SCREEN_TEST_PARM_C         244      // (T117,Cwrd1_TPARCD,16,0x0080)
#define MEDIA_DAMAGE_SCREEN_TEST_PARM_P           0

#define MDS_MAX_TRK_LEN_B4_PRINT_PARM_C         245      // (DEF,MdsMxTrkPrtThrsh_TPARCD,16,NA)
#define MDS_MAX_TRK_LEN_B4_PRINT_PARM_P           1

#define DATE_PARM_C                             246      // (DEF,Dat_TPARCD,16,NA)
#define DATE_PARM_P                               2

#define MDS_MAX_BYTES_SCR_MULT_PARM_C           247      // (DEF,MdsMxBytScrScal_TPARCD,16,NA)
#define MDS_MAX_BYTES_SCR_MULT_PARM_P             3

#define MDS_SCRATCH_INCLUDES_CYL_PARM_C         248      // (DEF,MdsScrIncldsCyl_TPARCD,16,NA)
#define MDS_SCRATCH_INCLUDES_CYL_PARM_P           2

#define MDS_MAX_TOTAL_BYTES_WCYL_PARM_C         249      // (DEF,MdsTtlCylRgBytCnt_TPARCD,16,NA)
#define MDS_MAX_TOTAL_BYTES_WCYL_PARM_P           1

#define MDS_MAX_SCRATCH_TRK_LEN_PARM_C          250      // (DEF,MdsMxScrTrkLen_TPARCD,16,NA)
#define MDS_MAX_SCRATCH_TRK_LEN_PARM_P            1

#define MDS_VIRTUAL_MAX_BYTES_PARM_C            251      // (DEF,MdsVrtlMxBytCnt_TPARCD,16,NA)
#define MDS_VIRTUAL_MAX_BYTES_PARM_P              1

#define MAX_FLAWS_PER_SURFACE_PARM_C            252      // (DEF,MxSurfFlawCnt_TPARCD,16,NA)
#define MAX_FLAWS_PER_SURFACE_PARM_P              1

#define SELECT_HEADS_PARM_C                     253      // (NA,Boolean,T117,NA)
#define SELECT_HEADS_PARM_P                       0

#define CHK_XOVER_PARM_C                        254      // (NA,Boolean,T117,NA)
#define CHK_XOVER_PARM_P                          0

#define PROXIMITY_WINDOW_PARM_C                 255      // (DEF,ProxWdw_TPARCD,16,NA)
#define PROXIMITY_WINDOW_PARM_P                   1

#define THRESHOLD2_PARM_C                       256      // (DEF,Thrsh2_TPARCD,16,NA) (T151,MnAsym_TPARCD,F,NA)
#define THRESHOLD2_PARM_P                         1

#define MAX_START_TIME_PARM_C                   257      // (DEF,MxStrtTm_TPARCD,16,NA)
#define MAX_START_TIME_PARM_P                     1

#define DELTA_NRRO_LIMIT_PARM_C                 258      // (DEF,DltaNrroLmt_TPARCD,16,NA)
#define DELTA_NRRO_LIMIT_PARM_P                   1

#define DELAY_TIME_PARM_C                       259      // (DEF,DlyTm_TPARCD,16,NA) (T615,DlyTm_TPARCD,16,0x00FF) (T708,DlyTm_TPARCD,16,0x00FF)
#define DELAY_TIME_PARM_P                         1

#define MIN_NRRO_LIMIT_PARM_C                   260      // (DEF,MnNrro_TPARCD,16,NA)
#define MIN_NRRO_LIMIT_PARM_P                     1

#define MAX_NRRO_LIMIT_PARM_C                   261      // (DEF,MxNrro_TPARCD,16,NA)
#define MAX_NRRO_LIMIT_PARM_P                     1

#define MAX_RRO_LIMIT_PARM_C                    262      // (DEF,MxRro_TPARCD,16,NA)
#define MAX_RRO_LIMIT_PARM_P                      1

#define MAX_RO_LIMIT_PARM_C                     263      // (NA,NA,NA,NA)
#define MAX_RO_LIMIT_PARM_P                       1

#define MRBIAS_RANGE_PARM_C                     264      // (DEF,MrBiasRg_TPARCD,16,NA)
#define MRBIAS_RANGE_PARM_P                       2

#define TA_THRESH_RANGE_PARM_C                  265      // (DEF,TaThrshRg_TPARCD,16,NA)
#define TA_THRESH_RANGE_PARM_P                    2

#define RD_BIAS_TA_PARM_C                       266      // (NA,NA,NA,NA)
#define RD_BIAS_TA_PARM_P                         0

#define MAX_ERROR_PARM_C                        267      // (DEF,MxErr_TPARCD,16,NA) (T621,MxErrCnt_TPARCD,16,NA)
#define MAX_ERROR_PARM_P                          1

#define NBR_BINS_PARM_C                         268      // (DEF,BinCnt_TPARCD,16,NA)
#define NBR_BINS_PARM_P                           1

#define BIN_SIZE_PARM_C                         269      // (DEF,BinSz_TPARCD,16,NA)
#define BIN_SIZE_PARM_P                           1

#define SET_STATE_SPACE_USE_PARM_C              270      // (T619,SetStatSpcUse_TPARCD,16,NA)
#define SET_STATE_SPACE_USE_PARM_P                1

#define INPUT_VOLTAGE_PARM_C                    271      // (DEF,Vltg_TPARCD,16,NA)
#define INPUT_VOLTAGE_PARM_P                      1

#define TIME_PARM_C                             272      // (DEF,Tm_TPARCD,16,NA)
#define TIME_PARM_P                               3

#define SEEK_TIME_PARM_C                        273      // (DEF,SkTm_TPARCD,16,NA)
#define SEEK_TIME_PARM_P                          3

#define BIT_MASK_PARM_C                         274      // (DEF,BitMsk_TPARCD,32,NA) (T53,ZnMsk_TPARCD,32,NA) (T141,ZnMsk_TPARCD,32,NA) (T151,ZnMsk_TPARCD,32,NA) (T210,ZnMsk_TPARCD,32,NA) (T251,ZnMsk_TPARCD,32,NA)
#define BIT_MASK_PARM_P                           2

#define BAD_WEDGE_LIMIT_PARM_C                  275      // (NA,NA,NA,NA)
#define BAD_WEDGE_LIMIT_PARM_P                    1

#define DEFECT_LEN_LIMIT_PARM_C                 276      // (DEF,DfctLenLmt_TPARCD,16,NA)
#define DEFECT_LEN_LIMIT_PARM_P                   1

#define LIMIT_PARM_C                            277      // (DEF,Lmt_TPARCD,16,NA) (T134,TaLmt_TPARCD[1],16,NA) (T175,SgmaRroCntLmt_TPARCD,16,NA) (T167,CentrOtcLmt_TPARCD,float,NA)
#define LIMIT_PARM_P                              1

#define LIMIT2_PARM_C                           278      // (DEF,Lmt2_TPARCD,16,NA) (T134,TaLmt_TPARCD[2],16,NA) (T175,MabsRroCntLmt_TPARCD,16,NA)
#define LIMIT2_PARM_P                             1

#define LIMIT32_PARM_C                          279      // (DEF,Lmt32_TPARCD,32,NA)
#define LIMIT32_PARM_P                            2

#define PERCENT_LIMIT_PARM_C                    280      // (DEF,PrctLmt_TPARCD,16,NA) (T649,PrctLmt3_TPARCD,float,NA)
#define PERCENT_LIMIT_PARM_P                      1

#define MAXIMUM_PARM_C                          281      // (DEF,Mx_TPARCD,16,NA) ((T080,ResistLmt_TPARCD[1],16,NA) (T167,MxOtcLmt_TPARCD,float,NA) (T695,UseMxCrrnt_TPARCD,8,NA)(NA,Maximum by itself is maybe a little too vague.)
#define MAXIMUM_PARM_P                            1

#define MAXIMUM32_PARM_C                        282      // (NA,NA,NA,NA)
#define MAXIMUM32_PARM_P                          2

#define MINIMUM_PARM_C                          283      // (DEF,Mn_TPARCD,16,NA) (T167,MnOtcLmt_TPARCD,float,NA) (T80,ResistLmt_TPARCD[0],16,NA)
#define MINIMUM_PARM_P                            1

#define SECTOR_SIZE_PARM_C                      284      // (DEF,SctrSz_TPARCD,16,NA) (T234,SctrCnt_TPARCD,16,NA)
#define SECTOR_SIZE_PARM_P                        1

#define ZONE_LIMIT32_PARM_C                     285      // (NA,NA,NA,NA)
#define ZONE_LIMIT32_PARM_P                       2

#define NEW_OPTION_PARM_C                       286      // (T531,SptOptn_TPARCD,8,NA)
#define NEW_OPTION_PARM_P                         1

#define SCALED_VAL_PARM_C                       287      // (DEF,Scal_TPARCD,16,NA) (T130,Scal2_TPARCD,F,NA) (T530,Scal2_TPARCD,F,NA)
#define SCALED_VAL_PARM_P                         1

#define INCREMENT_PARM_C                        288      // (DEF,Inc_TPARCD,16,NA) (T228,DacRg_TPARCD[2],16,NA)
#define INCREMENT_PARM_P                          1

#define FREQ_SHIFT_PARM_C                       289      // (NA,NA,NA,NA)
#define FREQ_SHIFT_PARM_P                         1

#define PASSES_PARM_C                           290      // (DEF,PassCnt_TPARCD,16,NA) (T510,PassCnt_TPARCD,8,0x00FF) (T515,PassCnt_TPARCD,8,0x00FF)
#define PASSES_PARM_P                             1

#define SECTORS_TO_CHK_PARM_C                   291      // (DEF,SctrCnt_TPARCD,16,NA)
#define SECTORS_TO_CHK_PARM_P                     1

#define PAD_SIZE_PARM_C                         292      // (DEF,PadSz_TPARCD,16,NA)
#define PAD_SIZE_PARM_P                           1

#define MAG_GAIN_PARM_C                         293      // (NA,NA,NA,NA)
#define MAG_GAIN_PARM_P                           1

#define SET_BLOCK_OPERATION_PARM_C              294      // (NA,NA,NA,NA)
#define SET_BLOCK_OPERATION_PARM_P                1

#define MAX_MIN_DELTA_PARM_C                    295      // (DEF,MxMnDlta_TPARCD,16,NA)
#define MAX_MIN_DELTA_PARM_P                      2

#define DEMOD_POS_ERROR_PARM_C                  296      // (T34,Cwrd1_TPARCD,16,0x4000)
#define DEMOD_POS_ERROR_PARM_P                    0

#define RAP_WORD_PARM_C                         297      // (DEF,RapWrd_TPARCD,16,NA)
#define RAP_WORD_PARM_P                           3

#define RAP_DOWNLOAD_PARM_C                     298      // (DEF,RapDwnld_TPARCD,16,NA)
#define RAP_DOWNLOAD_PARM_P                       4

#define AMPL_LIMIT_PARM_C                       299      // (DEF,AmpLmt_TPARCD,16,NA)
#define AMPL_LIMIT_PARM_P                         7

#define MIN_PZT_MOVEMENT_PARM_C                 300      // (DEF,MnPztRg_TPARCD,16,NA)
#define MIN_PZT_MOVEMENT_PARM_P                   1

#define DEBUG_PRINT_PARM_C                      301      // (T29,Cwrd1_TPARCD,16,0x0001) (T177,Cwrd1_TPARCD,16,0x0D00) (T135,DbgPrt_TPARCD,16,NA) (T535,DbgPrt_TPARCD,8,NA) (T731,DbgPrt_TPARCD,8,0x0001)
#define DEBUG_PRINT_PARM_P                        1

#define POSITION_DISTURBANCE_PARM_C             302      // (DEF,InjAmp_TPARCD,16,NA)
#define POSITION_DISTURBANCE_PARM_P               1

#define AC_ERASE_PARM_C                         303      // (T195,Cwrd1_TPARCD,16,0x1000)
#define AC_ERASE_PARM_P                           0

#define ASP_CYL_SPEC_PARM_C                     304      // (NA,NA,NA,NA)
#define ASP_CYL_SPEC_PARM_P                       1

#define PLIST_CYL_SPEC_PARM_C                   305      // (NA,NA,NA,NA)
#define PLIST_CYL_SPEC_PARM_P                     1

#define SLOPE_CYL_1_PARM_C                      306      // (DEF,SlopeCyl1_TPARCD,32,NA)
#define SLOPE_CYL_1_PARM_P                        2

#define SLOPE_CYL_2_PARM_C                      307      // (DEF,SlopeCyl2_TPARCD,32,NA)
#define SLOPE_CYL_2_PARM_P                        2

#define INIT_VEL_TO_POSITION_PARM_C             308      // (NA,NA,NA,NA)
#define INIT_VEL_TO_POSITION_PARM_P               1

#define MVL_THRESH_LEVEL_PARM_C                 309      // (DEF,ThrshLvl_TPARCD,16,NA)
#define MVL_THRESH_LEVEL_PARM_P                   4

#define CUDACOM_FN_PARM_C                       310      // (NA,NA,NA,NA)
#define CUDACOM_FN_PARM_P                         1

#define PARAM_0_4_PARM_C                        311      // (DEF,SvoCmd_TPARCD[0-4],16,NA)
#define PARAM_0_4_PARM_P                          5

#define PARAM_5_9_PARM_C                        312      // (DEF,SvoCmd_TPARCD[5-9],16,NA)
#define PARAM_5_9_PARM_P                          5

#define AGC_HIT_LIMIT_PARM_C                    313      // (DEF,AgcTgt_TPARCD,16,NA)
#define AGC_HIT_LIMIT_PARM_P                      2

#define DELTA_SIGMA_LIMIT_PARM_C                314      // (DEF,DltaSgmaLmt_TPARCD,16,NA)
#define DELTA_SIGMA_LIMIT_PARM_P                  1

#define NBR_CYLS_PARM_C                         315      // (DEF,CylCnt_TPARCD,16,NA) (T620,NumCyl_TPARCD,8,0x00FF) 
#define NBR_CYLS_PARM_P                           1

#define NBR_ZONES_PARM_C                        316      // (DEF,ZnCnt_TPARCD,16,NA)
#define NBR_ZONES_PARM_P                          1

#define RECYCLE_THRESHOLD_PARM_C                317      // (NA,NA,NA,NA)
#define RECYCLE_THRESHOLD_PARM_P                  1

#define END_HARM_PARM_C                         318      // (DEF,EndHrm_TPARCD,16,NA)
#define END_HARM_PARM_P                           1

#define SLOPE_LIMIT_PARM_C                      319      // (DEF,SlopeLmt_TPARCD,16,NA)
#define SLOPE_LIMIT_PARM_P                        1

#define MAX_MISCOMPARES_PARM_C                  320      // (NA,NA,NA,NA)
#define MAX_MISCOMPARES_PARM_P                    2

#define ERASE_OFFSET_PARM_C                     321      // (DEF,EraseOfst_TPARCD,16,NA)
#define ERASE_OFFSET_PARM_P                       1

#define MABS_RRO_LIMIT_PARM_C                   322      // (DEF,MabsRroLmt_TPARCD,16,NA)
#define MABS_RRO_LIMIT_PARM_P                     1

#define M_COUNTER_VAL_PARM_C                    323      // (DEF,Cntr_TPARCD[0],8,NA)
#define M_COUNTER_VAL_PARM_P                      1

#define N_COUNTER_VAL_PARM_C                    324      // (DEF,Cntr_TPARCD[1],8,NA)
#define N_COUNTER_VAL_PARM_P                      1

#define TLEVEL_PARM_C                           325      // (DEF,Tlvl_TPARCD,16,NA)
#define TLEVEL_PARM_P                             1

#define LONG_SCR_TA_SCRSZ_MAXTA_PARM_C          326      // (NA,NA,NA,NA)
#define LONG_SCR_TA_SCRSZ_MAXTA_PARM_P            2

#define MAX_BYTE_SECT_WEDGE_TRK_PARM_C          327      // (NA,NA,NA,NA)
#define MAX_BYTE_SECT_WEDGE_TRK_PARM_P            4

#define BACKWD_PAD_SIZE_PARM_C                  328      // (DEF,BackwdPadSz_TPARCD,16,NA)
#define BACKWD_PAD_SIZE_PARM_P                    1

#define NOTCH_TABLE_PARM_C                      329      // (DEF,NtchTbl_TPARCD,16,NA)
#define NOTCH_TABLE_PARM_P                        1

#define DAMPING_PARM_C                          330      // (DEF,Dampg_TPARCD,16,NA) (T178,PreampParm_TPARCD[1],8,NA) (T211,PreampParm_TPARCD[1],8,NA)
#define DAMPING_PARM_P                            1

#define BDRAG_FCONS_PARM_C                      331      // (DEF,BdragFcon_TPARCD,32,NA)
#define BDRAG_FCONS_PARM_P                        2

#define DWELL_TIME_PARM_C                       332      // (DEF,DwellTm_TPARCD,16,NA)
#define DWELL_TIME_PARM_P                         1

#define BIASHYSTERESIS_INC_PARM_C               333      // (DEF,BiasHystInc_TPARCD,16,NA)
#define BIASHYSTERESIS_INC_PARM_P                 1

#define RV_CTRL_FLASH_PARM_C                    334      // (DEF,RvCtrlFlash_TPARCD,16,NA)
#define RV_CTRL_FLASH_PARM_P                      1

#define FC_DATA_PARM_C                          335      // (NA,NA,NA,NA)
#define FC_DATA_PARM_P                            2

#define RETRIES_PARM_C                          336      // (DEF,RtryCnt_TPARCD,16,NA)
#define RETRIES_PARM_P                            1

#define MAX_JOG_ERROR_PARM_C                    337      // (NA,NA,NA,NA)
#define MAX_JOG_ERROR_PARM_P                      1

#define OOS_JOG_TRACK_LIMIT_PARM_C              338      // (DEF,JogErrDllocLmt_TPARCD,16,NA)
#define OOS_JOG_TRACK_LIMIT_PARM_P                1

#define NBR_JOG_BINS_PARM_C                     339      // (DEF,JogBinCnt_TPARCD,16,NA)
#define NBR_JOG_BINS_PARM_P                       1

#define JOG_BIN_SIZE_PARM_C                     340      // (DEF,JogBinSz_TPARCD,16,NA)
#define JOG_BIN_SIZE_PARM_P                       1

#define NBR_HALF_BINS_PARM_C                    341      // (NA,NA,NA,NA)
#define NBR_HALF_BINS_PARM_P                      1

#define HALF_BIN_SIZE_PARM_C                    342      // (NA,NA,NA,NA)
#define HALF_BIN_SIZE_PARM_P                      1

#define SET_REG00_PARM_C                        343      // (DEF,Reg00_TPARCD,16,NA)
#define SET_REG00_PARM_P                          2

#define SET_REG01_PARM_C                        344      // (DEF,Reg01_TPARCD,16,NA)
#define SET_REG01_PARM_P                          2

#define SET_REG02_PARM_C                        345      // (DEF,Reg02_TPARCD,16,NA)
#define SET_REG02_PARM_P                          2

#define SET_REG03_PARM_C                        346      // (DEF,Reg03_TPARCD,16,NA)
#define SET_REG03_PARM_P                          2

#define SET_REG04_PARM_C                        347      // (DEF,Reg04_TPARCD,16,NA)
#define SET_REG04_PARM_P                          2

#define SET_REG05_PARM_C                        348      // (DEF,Reg05_TPARCD,16,NA)
#define SET_REG05_PARM_P                          2

#define SET_REG06_PARM_C                        349      // (DEF,Reg06_TPARCD,16,NA)
#define SET_REG06_PARM_P                          2

#define SET_REG07_PARM_C                        350      // (DEF,Reg07_TPARCD,16,NA)
#define SET_REG07_PARM_P                          2

#define SET_REG08_PARM_C                        351      // (DEF,Reg08_TPARCD,16,NA)
#define SET_REG08_PARM_P                          2

#define SET_REG09_PARM_C                        352      // (DEF,Reg09_TPARCD,16,NA)
#define SET_REG09_PARM_P                          2

#define SET_REG10_PARM_C                        353      // (DEF,Reg10_TPARCD,16,NA)
#define SET_REG10_PARM_P                          2

#define SET_REG11_PARM_C                        354      // (DEF,Reg11_TPARCD,16,NA)
#define SET_REG11_PARM_P                          2

#define SET_REG12_PARM_C                        355      // (DEF,Reg12_TPARCD,16,NA)
#define SET_REG12_PARM_P                          2

#define SET_REG13_PARM_C                        356      // (DEF,Reg13_TPARCD,16,NA)
#define SET_REG13_PARM_P                          2

#define SET_REG14_PARM_C                        357      // (DEF,Reg14_TPARCD,16,NA)
#define SET_REG14_PARM_P                          2

#define SET_REG15_PARM_C                        358      // (DEF,Reg15_TPARCD,16,NA)
#define SET_REG15_PARM_P                          2

#define SET_REG16_PARM_C                        359      // (DEF,Reg16_TPARCD,16,NA)
#define SET_REG16_PARM_P                          2

#define SET_REG17_PARM_C                        360      // (DEF,Reg17_TPARCD,16,NA)
#define SET_REG17_PARM_P                          2

#define SET_REG18_PARM_C                        361      // (DEF,Reg18_TPARCD,16,NA)
#define SET_REG18_PARM_P                          2

#define SET_REG19_PARM_C                        362      // (DEF,Reg19_TPARCD,16,NA)
#define SET_REG19_PARM_P                          2

#define SET_REG20_PARM_C                        363      // (DEF,Reg20_TPARCD,16,NA)
#define SET_REG20_PARM_P                          2

#define SET_REG21_PARM_C                        364      // (DEF,Reg21_TPARCD,16,NA)
#define SET_REG21_PARM_P                          2

#define SET_REG22_PARM_C                        365      // (DEF,Reg22_TPARCD,16,NA)
#define SET_REG22_PARM_P                          2

#define SET_REG23_PARM_C                        366      // (DEF,Reg23_TPARCD,16,NA)
#define SET_REG23_PARM_P                          2

#define SET_REG24_PARM_C                        367      // (DEF,Reg24_TPARCD,16,NA)
#define SET_REG24_PARM_P                          2

#define SET_REG25_PARM_C                        368      // (DEF,Reg25_TPARCD,16,NA)
#define SET_REG25_PARM_P                          2

#define SET_REG26_PARM_C                        369      // (DEF,Reg26_TPARCD,16,NA)
#define SET_REG26_PARM_P                          2

#define SET_REG27_PARM_C                        370      // (DEF,Reg27_TPARCD,16,NA)
#define SET_REG27_PARM_P                          2

#define SET_REG28_PARM_C                        371      // (DEF,Reg28_TPARCD,16,NA)
#define SET_REG28_PARM_P                          2

#define SET_REG29_PARM_C                        372      // (DEF,Reg29_TPARCD,16,NA)
#define SET_REG29_PARM_P                          2

#define NO_TMD_LMT2_PARM_C                      373      // (NA,NA,NA,NA)
#define NO_TMD_LMT2_PARM_P                        1

#define GAP_SIZE_PARM_C                         374      // (DEF,GapSz_TPARCD,16,NA)
#define GAP_SIZE_PARM_P                           1

#define BASELINE_REVS_PARM_C                    375      // (DEF,BaslneRvs_TPARCD,16,NA)
#define BASELINE_REVS_PARM_P                      1

#define WINDOW_PARM_C                           376      // (DEF,Wdw_TPARCD[0],16,NA)
#define WINDOW_PARM_P                             1

#define WC_RANGE_PARM_C                         377      // (DEF,WrCrrntRg_TPARCD,16,NA)
#define WC_RANGE_PARM_P                           2

#define DELTA_LIMIT_PARM_C                      378      // (DEF,DltaLmt_TPARCD,16,NA)
#define DELTA_LIMIT_PARM_P                        1

#define UNSAFE_WEDGE_LIMIT_PARM_C               379      // (NA,NA,NA,NA)
#define UNSAFE_WEDGE_LIMIT_PARM_P                 1

#define READ_ZAP_REDUCT_PARM_C                  380      // (NA,NA,NA,NA)
#define READ_ZAP_REDUCT_PARM_P                    1

#define RETRY_INCR_PARM_C                       381      // (DEF,RtryInc_TPARCD,16,NA)
#define RETRY_INCR_PARM_P                         1

#define LOG_SPACING_EXCEPT_LIM_PARM_C           382      // (DEF,LgclSpcgExcptLmt_TPARCD,16,NA)
#define LOG_SPACING_EXCEPT_LIM_PARM_P             1

#define LOG_SPACING_DEALLOC_LIM_PARM_C          383      // (DEF,LgclSpcgDllocLmt_TPARCD,16,NA)
#define LOG_SPACING_DEALLOC_LIM_PARM_P            1

#define JOG_ERROR_EXCEPT_LIM_PARM_C             384      // (DEF,JogErrExcptLmt_TPARCD[0],16,NA)
#define JOG_ERROR_EXCEPT_LIM_PARM_P               1

#define JOG_ERROR_DEALLOC_LIM_PARM_C            385      // (DEF,JogErrDllocLmt_TPARCD[0],16,NA)
#define JOG_ERROR_DEALLOC_LIM_PARM_P              1

#define OOS_LOG_SPACING_EXCEPT_PARM_C           386      // (DEF,OosLgclSpcgExcpt_TPARCD,16,NA)
#define OOS_LOG_SPACING_EXCEPT_PARM_P             1

#define OOS_LOG_SPACING_DEALLOC_PARM_C          387      // (DEF,OosLgclSpcgDlloc_TPARCD,16,NA)
#define OOS_LOG_SPACING_DEALLOC_PARM_P            1

#define OOS_JOG_TRACKS_EXCEPT_PARM_C            388      // (DEF,OosJogTrkCntExcpt_TPARCD,16,NA)
#define OOS_JOG_TRACKS_EXCEPT_PARM_P              1

#define OOS_JOG_TRACKS_DEALLOC_PARM_C           389      // (DEF,OosJogTrkCntDlloc_TPARCD,16,NA)
#define OOS_JOG_TRACKS_DEALLOC_PARM_P             1

#define WRITE_GUARDBAND_PARM_C                  390      // (NA,NA,NA,NA)
#define WRITE_GUARDBAND_PARM_P                    0

#define WEDGE_NUM_PARM_C                        391      // (DEF,WdgCnt_TPARCD,16,NA) (T529,WdgNum_TPARCD,16,0x03FF)
#define WEDGE_NUM_PARM_P                          1

#define MAX_ERR_RATE_PARM_C                     392      // (DEF,MxErrRat_TPARCD,16,NA) (T621,MxErrRat_TPARCD,16,0x0FFF)
#define MAX_ERR_RATE_PARM_P                       1

#define SYNC_BYTE_CONTROL_PARM_C                393      // (DEF,SyncBytCtrl_TPARCD,16,NA)
#define SYNC_BYTE_CONTROL_PARM_P                  1

#define DELTA_FREQ_PARM_C                       394      // (DEF,DltaFrq_TPARCD,16,NA)
#define DELTA_FREQ_PARM_P                         1

#define BIAS_RANGE_PARM_C                       395      // (NA,NA,NA,NA)
#define BIAS_RANGE_PARM_P                         1

#define VENDOR_MAX_BIAS_PARM_C                  396      // (NA,NA,NA,NA)
#define VENDOR_MAX_BIAS_PARM_P                    1

#define AGERE_LIMIT_PARM_C                      397      // (DEF,WrCrrntLmt_TPARCD,16,NA)
#define AGERE_LIMIT_PARM_P                        1

#define ASP_LENGTH1_PARM_C                      398      // (DEF,MxTaLen_TPARCD,16,NA)
#define ASP_LENGTH1_PARM_P                        1

#define ASP_WIDTH1_PARM_C                       399      // (DEF,MxTaWdth_TPARCD,16,NA)
#define ASP_WIDTH1_PARM_P                         1

#define ASP_LENGTH2_PARM_C                      400      // (DEF,TaLenThrsh_TPARCD,16,NA)
#define ASP_LENGTH2_PARM_P                        2

#define ASP_WIDTH2_PARM_C                       401      // (NA,NA,NA,NA)
#define ASP_WIDTH2_PARM_P                         2

#define ASP_SPEC_PARM_C                         402      // (NA,NA,NA,NA)
#define ASP_SPEC_PARM_P                           1

#define LATERAL_GROWTH_SIZE_PARM_C              403      // (NA,NA,NA,NA)
#define LATERAL_GROWTH_SIZE_PARM_P                1

#define MVL_THRESH_LEVEL1_PARM_C                404      // (NA,NA,NA,NA)
#define MVL_THRESH_LEVEL1_PARM_P                  4

#define TRACK_GAP_SIZE_PARM_C                   405      // (NA,NA,NA,NA)
#define TRACK_GAP_SIZE_PARM_P                     1

#define HEAD_MASKS_5_PARM_C                     406      // (NA,NA,NA,NA)
#define HEAD_MASKS_5_PARM_P                       5

#define TEST_LIMITS_5_PARM_C                    407      // (DEF,BerLmt_TPARCD,16,NA)
#define TEST_LIMITS_5_PARM_P                      5

#define TEST_LIMITS_1ST_10_PARM_C               408      // (DEF,Lmt10_TPARCD,16,NA)
#define TEST_LIMITS_1ST_10_PARM_P                10

#define TEST_LIMITS_2ND_10_PARM_C               409      // (NA,NA,NA,NA)
#define TEST_LIMITS_2ND_10_PARM_P                10

#define TEST_LIMITS_3RD_10_PARM_C               410      // (NA,NA,NA,NA)
#define TEST_LIMITS_3RD_10_PARM_P                10

#define TEST_LIMITS_4TH_10_PARM_C               411      // (NA,NA,NA,NA)
#define TEST_LIMITS_4TH_10_PARM_P                10

#define TEST_LIMITS_5TH_10_PARM_C               412      // (NA,NA,NA,NA)
#define TEST_LIMITS_5TH_10_PARM_P                10

#define SERVO_CODE_3_PARM_C                     413      // (NA,NA,NA,NA)
#define SERVO_CODE_3_PARM_P                       6

#define SERVO_ADDR_3_PARM_C                     414      // (NA,NA,NA,NA)
#define SERVO_ADDR_3_PARM_P                       6

#define UNVER_LIMIT_PARM_C                      415      // (DEF,UnvfdLmt_TPARCD,16,NA)
#define UNVER_LIMIT_PARM_P                        1

#define VER_LIMIT_PARM_C                        416      // (NA,NA,NA,NA)
#define VER_LIMIT_PARM_P                          1

#define GAIN2_PARM_C                            417      // (T193,IncGain_TPARCD,16,NA) (T25,MxCrrnt_TPARCD,16,NA) (T251,GainCtrl_TPARCD,NA) (T564,Gain2_TPARCD,16,NA)
#define GAIN2_PARM_P                              1

#define AGC_SKIP_TRACK_LIMIT_PARM_C             418      // (NA,NA,NA,NA)
#define AGC_SKIP_TRACK_LIMIT_PARM_P               2

#define USER_DRAM_SIZE_PARM_C                   419      // (DEF,DramSz_TPARCD,32,NA)
#define USER_DRAM_SIZE_PARM_P                     2

#define SERVO_TA_SCAN_PARM_C                    420      // (NA,NA,NA,NA)
#define SERVO_TA_SCAN_PARM_P                      0

#define FREQ_START_5_PARM_C                     421      // (NA,NA,NA,NA)
#define FREQ_START_5_PARM_P                       5

#define FREQ_END_5_PARM_C                       422      // (NA,NA,NA,NA)
#define FREQ_END_5_PARM_P                         5

#define FREQ_WIDTH_5_PARM_C                     423      // (NA,NA,NA,NA)
#define FREQ_WIDTH_5_PARM_P                       5

#define DELTA_FREQ_5_PARM_C                     424      // (NA,NA,NA,NA)
#define DELTA_FREQ_5_PARM_P                       5

#define NOISE_THRESHOLD_5_PARM_C                425      // (NA,NA,NA,NA)
#define NOISE_THRESHOLD_5_PARM_P                  5

#define RAP_HDA_SN_PARM_C                       426      // (NA,NA,NA,NA)
#define RAP_HDA_SN_PARM_P                         0

#define WRITE_CURRENT_ADJ_PARM_C                427      // (NA,NA,NA,NA)
#define WRITE_CURRENT_ADJ_PARM_P                  1

#define BPI_GROUP_PARM_C                        428      // (DEF,BpiGrp_TPARCD,16,NA)
#define BPI_GROUP_PARM_P                          8

#define OD_CYL_PARM_C                           429      // (DEF,OdCyl_TPARCD,32,NA)
#define OD_CYL_PARM_P                             2

#define MD_CYL_PARM_C                           430      // (DEF,MdCyl_TPARCD,32,NA)
#define MD_CYL_PARM_P                             2

#define ID_CYL_PARM_C                           431      // (DEF,IdCyl_TPARCD,32,NA)
#define ID_CYL_PARM_P                             2

#define CONTACT_VERIFY_PARM_C                   432      // (DEF,CntctVfy_TPARCD,16,NA)
#define CONTACT_VERIFY_PARM_P                     1

#define HEATER_PARM_C                           433      // (DEF,Htr_TPARCD,16,NA)
#define HEATER_PARM_P                             2

#define RANGE_PARM_C                            434      // (DEF,Rg_TPARCD,16,NA) (T611,Rg_TPARCD,32,NA)
#define RANGE_PARM_P                              2

#define TA_AMPLITUDE_PARM_C                     435      // (DEF,TaAmp_TPARCD,16,NA)
#define TA_AMPLITUDE_PARM_P                       4

#define NUM_ADJ_CYLS_PARM_C                     436      // (DEF,AdjcntCylCnt_TPARCD,16,NA)
#define NUM_ADJ_CYLS_PARM_P                       4

#define LONG_DEFECT_PAD_PARM_C                  437      // (DEF,LngDfctPad_TPARCD,16,NA)
#define LONG_DEFECT_PAD_PARM_P                    2

#define JOG_ERROR_EXCEPT_LIM_2_PARM_C           438      // (DEF,JogErrExcptLmt_TPARCD[1],16,NA)
#define JOG_ERROR_EXCEPT_LIM_2_PARM_P             1

#define JOG_ERROR_DEALLOC_LIM_2_PARM_C          439      // (DEF,JogErrDllocLmt2_TPARCD[1],16,NA)
#define JOG_ERROR_DEALLOC_LIM_2_PARM_P            1

#define TA_FAIL_SAFE_PARM_C                     440      // (T109,Cwrd4_TPARCD,16,0x0080)
#define TA_FAIL_SAFE_PARM_P                       0

#define AR_CPTP_PARM_C                          441      // (NA,NA,NA,NA)
#define AR_CPTP_PARM_P                            2

#define SMOOTH_PARM_C                           442      // (DEF,Smooth_TPARCD,16,NA)
#define SMOOTH_PARM_P                             1

#define MAX_CQM_PCNT_PARM_C                     443      // (DEF,MxCqmPrct_TPARCD,16,NA)
#define MAX_CQM_PCNT_PARM_P                       1

#define NUM_READS_PARM_C                        444      // (DEF,RdCnt_TPARCD,16,NA) (T545,NumRd_TPARCD,16,NA) (T609,NumRd_TPARCD,16,NA) (T629,NumRdPerWr_TPARCD,16,NA) (T630,NumRdPerWr_TPARCD,16,NA) (T695,NumRd_TPARCD,16,NA) 
#define NUM_READS_PARM_P                          1      // (T714,NumRd_TPARCD,16,NA)

#define E_FACTOR_PARM_C                         445      // (DEF,ExpFctr_TPARCD,F,NA)
#define E_FACTOR_PARM_P                           1

#define PERCENT_LIMIT2_PARM_C                   446      // (DEF,PrctLmt2_TPARCD,16,NA)
#define PERCENT_LIMIT2_PARM_P                     1

#define SEC_CYL_PARM_C                          447      // (DEF,SecCyl_TPARCD,32,NA)
#define SEC_CYL_PARM_P                            2

#define SEC_WZAP_MABS_RRO_LIMIT_PARM_C          448      // (DEF,SecWrMabsRroLmt_TPARCD,16,NA)
#define SEC_WZAP_MABS_RRO_LIMIT_PARM_P            1

#define SEC_RZAP_MABS_RRO_LIMIT_PARM_C          449      // (DEF,SecRdMabsRroLmt_TPARCD,16,NA)
#define SEC_RZAP_MABS_RRO_LIMIT_PARM_P            1

#define TCC_CONTROL_PARM_C                      450      // (NA,NA,NA,NA)
#define TCC_CONTROL_PARM_P                        1

#define ZAP_START_HARM_PARM_C                   451      // (DEF,ZapStrtHrm_TPARCD,16,NA)
#define ZAP_START_HARM_PARM_P                     1

#define MR_BIAS_OFFSET_PARM_C                   452      // (DEF,MrBiasOfst_TPARCD,16,NA)
#define MR_BIAS_OFFSET_PARM_P                     1

#define WRITE_CURRENT_OFFSET_PARM_C             453      // (DEF,PreampCldOfst_TPARCD[0],8,NA) (DEF,PreampHtOfst_TPARCD[0],8,NA)
#define WRITE_CURRENT_OFFSET_PARM_P               2

#define NR_STDEV_LIMIT_PARM_C                   454      // (DEF,NrStdevLmt_TPARCD,16,NA)
#define NR_STDEV_LIMIT_PARM_P                     1

#define R_STDEV_LIMIT_PARM_C                    455      // (DEF,RStdevLmt_TPARCD,16,NA)
#define R_STDEV_LIMIT_PARM_P                      1

#define RD_HEAT_ON_PARM_C                       456      // (NA,NA,NA,NA)
#define RD_HEAT_ON_PARM_P                         1

#define DIAMETER_PARM_C                         457      // (NA,NA,NA,NA)
#define DIAMETER_PARM_P                           1

#define RPM_PARM_C                              458      // (DEF,Rpm_TPARCD,16,NA)
#define RPM_PARM_P                                1

#define H0CONTACT_PARM_C                        459      // (DEF,Hd0Cntct_TPARCD,16,NA)
#define H0CONTACT_PARM_P                          1

#define H1CONTACT_PARM_C                        460      // (DEF,Hd1Cntct_TPARCD,16,NA)
#define H1CONTACT_PARM_P                          1

#define H2CONTACT_PARM_C                        461      // (DEF,Hd2Cntct_TPARCD,16,NA)
#define H2CONTACT_PARM_P                          1

#define H3CONTACT_PARM_C                        462      // (DEF,Hd3Cntct_TPARCD,16,NA)
#define H3CONTACT_PARM_P                          1

#define H4CONTACT_PARM_C                        463      // (DEF,Hd4Cntct_TPARCD,16,NA)
#define H4CONTACT_PARM_P                          1

#define H5CONTACT_PARM_C                        464      // (DEF,Hd5Cntct_TPARCD,16,NA)
#define H5CONTACT_PARM_P                          1

#define H6CONTACT_PARM_C                        465      // (DEF,Hd6Cntct_TPARCD,16,NA)
#define H6CONTACT_PARM_P                          1

#define H7CONTACT_PARM_C                        466      // (DEF,Hd7Cntct_TPARCD,16,NA)
#define H7CONTACT_PARM_P                          1

#define MABS_RRO_TARGET_PARM_C                  467      // (DEF,MabsRroTgt_TPARCD,16,NA)
#define MABS_RRO_TARGET_PARM_P                    1

#define DURATION_PARM_C                         468      // (DEF,Duratn_TPARCD,16,NA) (T178,PreampParm_TPARCD[2],8,NA) (T211,PreampParm_TPARCD[2],8,NA)
#define DURATION_PARM_P                           1

#define RANGE2_PARM_C                           469      // (DEF,Rg2_TPARCD,16,NA) (T195,OfstSetg_TPARCD,16,NA)
#define RANGE2_PARM_P                             4

#define ZONE_PARM_C                             470      // (DEF,Zn_TPARCD,16,NA)
#define ZONE_PARM_P                               1

#define GAP_FILL_PARM_C                         471      // (DEF,GapFill_TPARCD,16,NA)
#define GAP_FILL_PARM_P                           1

#define TRGT_RD_CLEARANCE_PARM_C                472      // (NA,NA,NA,NA)
#define TRGT_RD_CLEARANCE_PARM_P                  1

#define TRGT_WR_CLEARANCE_PARM_C                473      // (NA,NA,NA,NA)
#define TRGT_WR_CLEARANCE_PARM_P                  1

#define AGERE_GAIN_CONTROL_PARM_C               474      // (DEF,GainCtrl_TPARCD,16,NA)
#define AGERE_GAIN_CONTROL_PARM_P                 1

#define DATA_SET_METADATA_PARM_C                475      // (NA,NA,NA,NA)
#define DATA_SET_METADATA_PARM_P                  4

#define DATA_SET1_PARM_C                        476      // (DEF,WrCrrntIntrvl_TPARCD,F,NA)
#define DATA_SET1_PARM_P                          4

#define DATA_SET2_PARM_C                        477      // (DEF,WrCrrntDacIntrvl_TPARCD,8,NA)
#define DATA_SET2_PARM_P                          4

#define DATA_SET3_PARM_C                        478      // (DEF,ThrshIntrvl_TPARCD,F,NA)
#define DATA_SET3_PARM_P                          4

#define DATA_SET4_PARM_C                        479      // (T213,ThrshLvl_TPARCD,16,NA)
#define DATA_SET4_PARM_P                          4

#define DATA_SET5_PARM_C                        480      // (NA,NA,NA,NA)
#define DATA_SET5_PARM_P                          4

#define MAX_RADIUS_PARM_C                       481      // (DEF,MxRdius_TPARCD,16,NA)
#define MAX_RADIUS_PARM_P                         1

#define VERIFIED_HEAD_LIMIT_PARM_C              482      // (DEF,VfdHdLmt_TPARCD,16,NA)
#define VERIFIED_HEAD_LIMIT_PARM_P                1

#define HEAD_UNVER_LIMIT_PARM_C                 483      // (DEF,HdUnvfdLmt_TPARCD,32,NA)
#define HEAD_UNVER_LIMIT_PARM_P                   2

#define VERIFIED_CYL_LIMIT_PARM_C               484      // (DEF,VfdCylLmt_TPARCD,16,NA)
#define VERIFIED_CYL_LIMIT_PARM_P                 1

#define UNVER_TRACK_LIMIT_PARM_C                485      // (NA,NA,NA,NA)
#define UNVER_TRACK_LIMIT_PARM_P                  1

#define VERIFIED_DRIVE_LIMIT_PARM_C             486      // (DEF,VfdDrvLmt_TPARCD,16,NA)
#define VERIFIED_DRIVE_LIMIT_PARM_P               1

#define VERIFIED_TRACK_LIMIT_PARM_C             487      // (DEF,VfdTrkLmt_TPARCD,16,NA)
#define VERIFIED_TRACK_LIMIT_PARM_P               1

#define UNVER_HD_ZONE_LIMIT_PARM_C              488      // (DEF,UnvfdHdZnLmt_TPARCD,32,NA)
#define UNVER_HD_ZONE_LIMIT_PARM_P                2

#define PATTERN_MASK_PARM_C                     489      // (DEF,PttrnMsk_TPARCD,16,NA)
#define PATTERN_MASK_PARM_P                       1

#define GAIN_CORR_LIM_PARM_C                    490      // (DEF,GainCorrLmt_TPARCD,16,NA)
#define GAIN_CORR_LIM_PARM_P                      1

#define TPI_GROUP_PARM_C                        491      // (DEF,TpiGrp_TPARCD,16,NA)
#define TPI_GROUP_PARM_P                          8

#define RETRY_DECR_PARM_C                       492      // (DEF,RtryDecr_TPARCD,16,NA)
#define RETRY_DECR_PARM_P                         1

#define ZONE_MASK_PARM_C                        493      // (DEF,ZnMsk_TPARCD,32,NA)
#define ZONE_MASK_PARM_P                          2

#define MV_PER_TIC_PARM_C                       494      // (DEF,MvScal_TPARCD,16,NA)
#define MV_PER_TIC_PARM_P                         1

#define AMP_CHARACTOR_STEP_PARM_C               495      // (DEF,AmpInc_TPARCD,16,NA)
#define AMP_CHARACTOR_STEP_PARM_P                 1

#define CRRO_HARMONIC1_PARM_C                   496      // (DEF,Crro01_TPARCD,16,NA)
#define CRRO_HARMONIC1_PARM_P                     2

#define CRRO_HARMONIC2_PARM_C                   497      // (DEF,Crro02_TPARCD,16,NA)
#define CRRO_HARMONIC2_PARM_P                     2

#define CRRO_HARMONIC3_PARM_C                   498      // (DEF,Crro03_TPARCD,16,NA)
#define CRRO_HARMONIC3_PARM_P                     2

#define CRRO_HARMONIC4_PARM_C                   499      // (DEF,Crro04_TPARCD,16,NA)
#define CRRO_HARMONIC4_PARM_P                     2

#define CRRO_HARMONIC5_PARM_C                   500      // (DEF,Crro05_TPARCD,16,NA)
#define CRRO_HARMONIC5_PARM_P                     2

#define CRRO_HARMONIC6_PARM_C                   501      // (DEF,Crro06_TPARCD,16,NA)
#define CRRO_HARMONIC6_PARM_P                     2

#define CRRO_HARMONIC7_PARM_C                   502      // (DEF,Crro07_TPARCD,16,NA)
#define CRRO_HARMONIC7_PARM_P                     2

#define CRRO_HARMONIC8_PARM_C                   503      // (DEF,Crro08_TPARCD,16,NA)
#define CRRO_HARMONIC8_PARM_P                     2

#define CRRO_HARMONIC9_PARM_C                   504      // (DEF,Crro09_TPARCD,16,NA)
#define CRRO_HARMONIC9_PARM_P                     2

#define CRRO_HARMONIC10_PARM_C                  505      // (DEF,Crro10_TPARCD,16,NA)
#define CRRO_HARMONIC10_PARM_P                    2

#define CRRO_HARMONIC11_PARM_C                  506      // (DEF,Crro11_TPARCD,16,NA)
#define CRRO_HARMONIC11_PARM_P                    2

#define CRRO_HARMONIC12_PARM_C                  507      // (DEF,Crro12_TPARCD,16,NA)
#define CRRO_HARMONIC12_PARM_P                    2

#define CRRO_HARMONIC13_PARM_C                  508      // (DEF,Crro13_TPARCD,16,NA)
#define CRRO_HARMONIC13_PARM_P                    2

#define CRRO_HARMONIC14_PARM_C                  509      // (DEF,Crro14_TPARCD,16,NA)
#define CRRO_HARMONIC14_PARM_P                    2

#define CRRO_HARMONIC15_PARM_C                  510      // (DEF,Crro15_TPARCD,16,NA)
#define CRRO_HARMONIC15_PARM_P                    2

#define CRRO_HARMONIC16_PARM_C                  511      // (DEF,Crro16_TPARCD,16,NA)
#define CRRO_HARMONIC16_PARM_P                    2

#define CRRO_HARMONIC17_PARM_C                  512      // (DEF,Crro17_TPARCD,16,NA)
#define CRRO_HARMONIC17_PARM_P                    2

#define CRRO_HARMONIC18_PARM_C                  513      // (DEF,Crro18_TPARCD,16,NA)
#define CRRO_HARMONIC18_PARM_P                    2

#define CRRO_HARMONIC19_PARM_C                  514      // (DEF,Crro19_TPARCD,16,NA)
#define CRRO_HARMONIC19_PARM_P                    2

#define CRRO_HARMONIC20_PARM_C                  515      // (DEF,Crro20_TPARCD,16,NA)
#define CRRO_HARMONIC20_PARM_P                    2

#define CRRO_HARMONIC21_PARM_C                  516      // (DEF,Crro21_TPARCD,16,NA)
#define CRRO_HARMONIC21_PARM_P                    2

#define CRRO_HARMONIC22_PARM_C                  517      // (DEF,Crro22_TPARCD,16,NA)
#define CRRO_HARMONIC22_PARM_P                    2

#define CRRO_HARMONIC23_PARM_C                  518      // (DEF,Crro23_TPARCD,16,NA)
#define CRRO_HARMONIC23_PARM_P                    2

#define CRRO_HARMONIC24_PARM_C                  519      // (DEF,Crro24_TPARCD,16,NA)
#define CRRO_HARMONIC24_PARM_P                    2

#define CRRO_HARMONIC25_PARM_C                  520      // (DEF,Crro25_TPARCD,16,NA)
#define CRRO_HARMONIC25_PARM_P                    2

#define DISABLE_HARMONICS_PARM_C                521      // (DEF,DisblHrm_TPARCD,32,NA)
#define DISABLE_HARMONICS_PARM_P                  2

#define START_ADDRESS_PARM_C                    522      // (DEF,StrtAddr_TPARCD,32,NA)
#define START_ADDRESS_PARM_P                      2

#define END_ADDRESS_PARM_C                      523      // (DEF,EndAddr_TPARCD,32,NA)
#define END_ADDRESS_PARM_P                        2

#define COMPARE_VALUE_PARM_C                    524      // (DEF,CmprVal_TPARCD,32,NA)
#define COMPARE_VALUE_PARM_P                      1

#define MASK_VALUE_PARM_C                       525      // (DEF,Msk_TPARCD,16,NA) (T011,BitMsk_TPARCD,32,NA)
#define MASK_VALUE_PARM_P                         1

#define WR_DATA_PARM_C                          526      // (DEF,Pttrn_TPARCD,8,NA) (T011,WrDta_TPARCD,32,NA) (T250,RamSctn_TPARCD,8,NA) (T611,WrRdDta_TPARCD,16,0x00FF) (T611,WrRdDta_TPARCD,16,0xFF00)
#define WR_DATA_PARM_P                            1

#define RAM_SECTION_PARM_C                      527      // (DEF,RamSctn_TPARCD,8,NA)
#define RAM_SECTION_PARM_P                        1

#define SYM_OFFSET_PARM_C                       528      // (DEF,SymblOfst_TPARCD,16,NA)
#define SYM_OFFSET_PARM_P                         1

#define NUM_LOCS_PARM_C                         529      // (DEF,LocCnt_TPARCD,16,NA) (T611,NumLoc_TPARCD,16,NA)
#define NUM_LOCS_PARM_P                           1

#define DASC_OFFSET_PARM_C                      530      // (DEF,DascOfst_TPARCD,16,NA)
#define DASC_OFFSET_PARM_P                        1

#define RAW_MAX_SIN_PARM_C                      531      // (DEF,RawMxSin_TPARCD,16,NA)
#define RAW_MAX_SIN_PARM_P                        1

#define RAW_MAX_COS_PARM_C                      532      // (DEF,RawMxCosin_TPARCD,16,NA)
#define RAW_MAX_COS_PARM_P                        1

#define RAW_MAX_DC_OFFSET_PARM_C                533      // (DEF,RawMxDcOfst_TPARCD,16,NA)
#define RAW_MAX_DC_OFFSET_PARM_P                  1

#define SEEK_RETRY_LIMIT_PARM_C                 534      // (DEF,SkRtryLmt_TPARCD,16,NA) (t1502)
#define SEEK_RETRY_LIMIT_PARM_P                   1

#define HD_SKEW_LENGTH_PARM_C                   535      // (DEF,HdSkew_TPARCD,16,NA)
#define HD_SKEW_LENGTH_PARM_P                     1

#define TIMING_ERR_LIM_PARM_C                   536      // (DEF,TmgErrLmt_TPARCD,16,NA)
#define TIMING_ERR_LIM_PARM_P                     1

#define DELTA_LIM_AC_PARM_C                     537      // (DEF,DltaLmtAc_TPARCD,16,NA)
#define DELTA_LIM_AC_PARM_P                       1

#define DELTA_LIM_DC_PARM_C                     538      // (DEF,DltaLmtDc_TPARCD,16,NA)
#define DELTA_LIM_DC_PARM_P                       1

#define DELTA_LIM_DC_MID_PARM_C                 539      // (DEF,DltaLmtDcMid_TPARCD,16,NA)
#define DELTA_LIM_DC_MID_PARM_P                   1

#define AC_MAG_COMP_PARM_C                      540      // (DEF,AcMagComp_TPARCD,16,NA)
#define AC_MAG_COMP_PARM_P                        1

#define NUM_SEEKS_PARM_C                        541      // (DEF,SkCnt_TPARCD,16,NA) (T532,NumSk_TPARCD,16,NA) (T545,NumSk_TPARCD,16,NA) (T711,NumSk_TPARCD,16,NA)
#define NUM_SEEKS_PARM_P                          1

#define MAX_RECD_SEEK_ERR_PARM_C                542      // (DEF,MxRcovSkErr_TPARCD,16,NA)
#define MAX_RECD_SEEK_ERR_PARM_P                  1

#define OD_OFFSET_PARM_C                        543      // (DEF,OdOfst_TPARCD,16,NA)
#define OD_OFFSET_PARM_P                          1

#define ID_OFFSET_PARM_C                        544      // (DEF,IdOfst_TPARCD,16,NA)
#define ID_OFFSET_PARM_P                          1

#define SKIP_TRACK_PARM_C                       545      // (DEF,SkpTrk_TPARCD,16,NA)
#define SKIP_TRACK_PARM_P                         1

#define SKIP_TRACK_PER_HD_PARM_C                546      // (DEF,SkpTrkPerHd_TPARCD,16,NA)
#define SKIP_TRACK_PER_HD_PARM_P                  1

#define FIRMWARE_FILE_NUM_PARM_C                547      // (NA,NA,NA,NA)
#define FIRMWARE_FILE_NUM_PARM_P                  1

#define DL_FILE_LEN_PARM_C                      548      // (DEF,FileLen_TPARCD,32,NA)
#define DL_FILE_LEN_PARM_P                        2

#define MAX_CQM_PARM_C                          549      // (DEF,MxCqm_TPARCD,16,NA)
#define MAX_CQM_PARM_P                            1

#define DCQM_PARM_C                             550      // (DEF,DltaCqm_TPARCD,16,NA)
#define DCQM_PARM_P                               1

#define VGA_MAX_PARM_C                          551      // (DEF,VgaMx_TPARCD,16,NA)
#define VGA_MAX_PARM_P                            1

#define VGA_MIN_PARM_C                          552      // (DEF,VgaMn_TPARCD,16,NA)
#define VGA_MIN_PARM_P                            1

#define VAR_THRESH_SCALER_PARM_C                553      // (DEF,VarThrshScal_TPARCD,F,NA)
#define VAR_THRESH_SCALER_PARM_P                  1

#define FIXED_THRESH_SCALER_PARM_C              554      // (DEF,FixdThrshScal_TPARCD,F,NA)
#define FIXED_THRESH_SCALER_PARM_P                1

#define ACCESS_TYPE_PARM_C                      555      // (DEF,AccssTyp_TPARCD,16,NA)
#define ACCESS_TYPE_PARM_P                        1

#define EXTENDED_WR_DATA_PARM_C                 556      // (DEF,ExtdWrDta_TPARCD,32,NA)
#define EXTENDED_WR_DATA_PARM_P                   1

#define EXTENDED_COMPARE_VALUE_PARM_C           557      // (DEF,ExtdCmprVal_TPARCD,32,NA)
#define EXTENDED_COMPARE_VALUE_PARM_P             1

#define EXTENDED_MASK_VALUE_PARM_C              558      // (DEF,ExtdMsk_TPARCD,32,NA)
#define EXTENDED_MASK_VALUE_PARM_P                1

#define ZBZ_METRIC_SCALE_FACTOR_PARM_C          559      // (DEF,ZbzMtrcScalFctr_TPARCD,16,NA)
#define ZBZ_METRIC_SCALE_FACTOR_PARM_P            1

#define SQRT_AMP_WIDTH_LIMIT_PARM_C             560      // (DEF,SqrtAmpWdthLmt_TPARCD,16,NA)
#define SQRT_AMP_WIDTH_LIMIT_PARM_P               1

#define WRT_PTP_COEF_PARM_C                     561      // (DEF,PtpCoef_TPARCD[0],F,NA) (T135,HtrPtpCoef_TPARCD,16,NA)
#define WRT_PTP_COEF_PARM_P                       3

#define HTR_PTP_COEF_PARM_C                     562      // (DEF,PtpCoef_TPARCD[1],F,NA)
#define HTR_PTP_COEF_PARM_P                       3

#define WRT_HTR_PTP_COEF_PARM_C                 563      // (DEF,PtpCoef_TPARCD[2],F,NA)
#define WRT_HTR_PTP_COEF_PARM_P                   3

#define TGT_WRT_CLR_PARM_C                      564      // (DEF,TgtClrnc_TPARCD[0],16,NA)
#define TGT_WRT_CLR_PARM_P                        1

#define TGT_PREWRT_CLR_PARM_C                   565      // (DEF,TgtClrnc_TPARCD[1],16,NA)
#define TGT_PREWRT_CLR_PARM_P                     1

#define TGT_RD_CLR_PARM_C                       566      // (DEF,TgtClrnc_TPARCD[2],16,NA)
#define TGT_RD_CLR_PARM_P                         1

#define TGT_IDLE_CLR_PARM_C                     567      // (DEF,TgtIdleClrnc_TPARCD,16,NA)
#define TGT_IDLE_CLR_PARM_P                       1

#define MIN_PREHEAT_USECS_PARM_C                568      // (DEF,MnPreHtTm_TPARCD,16,NA)
#define MIN_PREHEAT_USECS_PARM_P                  1

#define TEMPERATURE_COEF_PARM_C                 569      // (DEF,TmpCoef_TPARCD,F,NA) (T235,TmpRg_TPARCD,16,NA)
#define TEMPERATURE_COEF_PARM_P                   2

#define MEASURED_WRT_HEAT_CLR_PARM_C            570      // (T178,MeasClrnc_TPARCD[0],16,NA)
#define MEASURED_WRT_HEAT_CLR_PARM_P              1

#define MEASURED_HEAT_CLR_PARM_C                571      // (T178,MeasClrnc_TPARCD[1],16,NA)
#define MEASURED_HEAT_CLR_PARM_P                  1

#define SWD_4_SAMP_THRESH_PARM_C                572      // (DEF,AfhHtClrncSwd_TPARCD[0],8,NA)
#define SWD_4_SAMP_THRESH_PARM_P                  1

#define SWD_DELTA_PARM_C                        573      // (DEF,AfhHtClrncSwd_TPARCD[1],8,NA) (T227,SwdDlta_TPARCD,16,NA)
#define SWD_DELTA_PARM_P                          1

#define SWD_FILTER_PARM_C                       574      // (DEF,AfhHtClrncSwd_TPARCD[2],8,NA)
#define SWD_FILTER_PARM_P                         1

#define A_PRE_WR_NUM_WEDGES_PARM_C              575      // (DEF,PreWrWdgCnt_TPARCD,16,NA)
#define A_PRE_WR_NUM_WEDGES_PARM_P                1

#define B_WR_NUM_WEDGES_PARM_C                  576      // (DEF,WrWdgCnt_TPARCD,16,NA)
#define B_WR_NUM_WEDGES_PARM_P                    1

#define C_POST_WR_NUM_WEDGES_PARM_C             577      // (DEF,PstWrWdgCnt_TPARCD,16,NA)
#define C_POST_WR_NUM_WEDGES_PARM_P               1

#define D_RD_NUM_WEDGES_PARM_C                  578      // (DEF,RdWdgCnt_TPARCD,16,NA)
#define D_RD_NUM_WEDGES_PARM_P                    1

#define E_POST_RD_NUM_WEDGES_PARM_C             579      // (DEF,PstRdWdgCnt_TPARCD,16,NA)
#define E_POST_RD_NUM_WEDGES_PARM_P               1

#define NUM_TRACKS_PER_ZONE_PARM_C              580      // (DEF,TrkPerZnCnt_TPARCD,16,NA)
#define NUM_TRACKS_PER_ZONE_PARM_P                1

#define MAX_RANGE_PARM_C                        581      // (DEF,MxRg_TPARCD,16,NA)
#define MAX_RANGE_PARM_P                          1

#define FILTERS_2_PARM_C                        582      // (DEF,Fltr2_TPARCD,16,NA)
#define FILTERS_2_PARM_P                          1

#define TEST_TIMEOUT_PARM_C                     583      // (DEF,TstTmout_TPARCD,32,NA)
#define TEST_TIMEOUT_PARM_P                       1

#define FINE_SEARCH_BACKUP_PARM_C               584      // (DEF,FineSrchBckUp_TPARCD,8,NA)
#define FINE_SEARCH_BACKUP_PARM_P                 1

#define BDRAG_ATTENS_PARM_C                     585      // (DEF,BdragAtten_TPARCD,16,NA)
#define BDRAG_ATTENS_PARM_P                       1

#define DURATION_OFFSET_PARM_C                  586      // (DEF,PreampCldOfst_TPARCD[2],8,NA) (DEF,PreampHtOfst_TPARCD[2],8,NA)
#define DURATION_OFFSET_PARM_P                    2

#define DAMPING_OFFSET_PARM_C                   587      // (DEF,PreampCldOfst_TPARCD[1],8,NA) (DEF,PreampHtOfst_TPARCD[1],8,NA) (T213,DampgOfst_TPARCD,8,NA)
#define DAMPING_OFFSET_PARM_P                     2

#define MR_BIAS_OFFSET_OFFSET_PARM_C            588      // (DEF,MrBiasOfstOfst_TPARCD,16,NA)
#define MR_BIAS_OFFSET_OFFSET_PARM_P              2

#define WRITE_PREHEAT_PARM_C                    589      // (DEF,AfhHtClrnc_TPARCD[0],8,NA)
#define WRITE_PREHEAT_PARM_P                      1

#define WRITE_HEAT_PARM_C                       590      // (DEF,AfhHtClrnc_TPARCD[1],8,NA)
#define WRITE_HEAT_PARM_P                         1

#define READ_HEAT_PARM_C                        591      // (DEF,AfhHtClrnc_TPARCD[2],8,NA)   (T135, HtrRg, 16, NA)
#define READ_HEAT_PARM_P                          1

#define TGT_MAINTENANCE_CLR_PARM_C              592      // (DEF,TgtMaintClrnc_TPARCD,16,NA)
#define TGT_MAINTENANCE_CLR_PARM_P                1

#define CERT_TEMPERATURE_PARM_C                 593      // (DEF,CertTmp_TPARCD,8,NA)
#define CERT_TEMPERATURE_PARM_P                   1

#define ADJ_BPI_FOR_TPI_PARM_C                  594      // (DEF,AdjBpiForTpi_TPARCD,16,NA)
#define ADJ_BPI_FOR_TPI_PARM_P                    1

#define START_OT_FOR_TPI_PARM_C                 595      // (DEF,Ofst_TPARCD,16,NA)
#define START_OT_FOR_TPI_PARM_P                   1

#define TPI_STEP_PARM_C                         596      // (DEF,TpiInc_TPARCD,16,NA)
#define TPI_STEP_PARM_P                           1

#define BPI_MAX_PUSH_RELAX_PARM_C               597      // (DEF,BpiMxPushRlax_TPARCD,16,NA)
#define BPI_MAX_PUSH_RELAX_PARM_P                 1

#define TARGET_SER_PARM_C                       598      // (DEF,TgtSer_TPARCD,16,NA)
#define TARGET_SER_PARM_P                         1

#define CAP_PCBA_SN_PARM_C                      599      // (DEF,CapPcbaSn_TPARCD,8,NA)
#define CAP_PCBA_SN_PARM_P                        6

#define DYNAMIC_THRESH_PARM_C                   600      // (DEF,DynThrsh_TPARCD,16,NA)
#define DYNAMIC_THRESH_PARM_P                     5

#define Q_DEPTH_PARM_C                          601      // (DEF,QDpth_TPARCD,16,NA)
#define Q_DEPTH_PARM_P                            1

#define LATENCY_PARM_C                          602      // (DEF,Latncy_TPARCD,16,NA)
#define LATENCY_PARM_P                            1

#define JIT_PARM_C                              603      // (DEF,Jit_TPARCD,16,NA)
#define JIT_PARM_P                                1

#define NUM_FCS_CTRL_PARM_C                     604      // (DEF,FcsCtrlCnt_TPARCD,16,NA)
#define NUM_FCS_CTRL_PARM_P                       1

#define SNO_FREQ_OFFSET_PARM_C                  605      // (NA,NA,NA,NA)
#define SNO_FREQ_OFFSET_PARM_P                    1

#define APPLIED_OFFSET_PARM_C                   606      // (DEF,AppldOfst_TPARCD,8,NA)
#define APPLIED_OFFSET_PARM_P                     1

#define INDIVIDUAL_OFFSET_PARM_C                607      // (DEF,IndvdlOfst_TPARCD,8,NA)
#define INDIVIDUAL_OFFSET_PARM_P                 20

#define VERIFY_GAMUT_PARM_C                     608      // (DEF,VfyGamut_TPARCD,16,NA)
#define VERIFY_GAMUT_PARM_P                       3

#define ZAP_WRITE_CURRENT_PARM_C                609      // (DEF,WrCrrnt_TPARCD,16,NA)
#define ZAP_WRITE_CURRENT_PARM_P                  1

#define ZAP_WRITE_CURRENT_OSD_PARM_C            610      // (DEF,WrCrrntOsd_TPARCD,16,NA)
#define ZAP_WRITE_CURRENT_OSD_PARM_P              1

#define ZAP_WRITE_CURRENT_OSA_PARM_C            611      // (DEF,WrCrrntOsa_TPARCD,16,NA)
#define ZAP_WRITE_CURRENT_OSA_PARM_P              1

#define RGN_NUM_ELEMENTS_PARM_C                 612      // (DEF,RegnElmntCnt_TPARCD,16,NA)
#define RGN_NUM_ELEMENTS_PARM_P                   1

#define RGN_DENSITY_THRESH_PARM_C               613      // (DEF,RegnDnstyThrsh_TPARCD,16,NA)
#define RGN_DENSITY_THRESH_PARM_P                 1

#define RGN_CYL_SPACING_THRESH_PARM_C           614      // (DEF,RegnCylSpcgThrsh_TPARCD,16,NA)
#define RGN_CYL_SPACING_THRESH_PARM_P             1

#define WIN_NUM_ELEMENTS_PARM_C                 615      // (DEF,WdwElmntCnt_TPARCD,16,NA)
#define WIN_NUM_ELEMENTS_PARM_P                   1

#define WIN_DENSITY_THRESH_PARM_C               616      // (DEF,WdwDnstyThrsh_TPARCD,16,NA)
#define WIN_DENSITY_THRESH_PARM_P                 1

#define WIN_CYL_SPACING_THRESH_PARM_C           617      // (DEF,WdwCylSpcgThrsh_TPARCD,16,NA)
#define WIN_CYL_SPACING_THRESH_PARM_P             1

#define WIN_BYTE_SPACING_THRESH_PARM_C          618      // (DEF,WdwBytSpcgThrsh_TPARCD,16,NA)
#define WIN_BYTE_SPACING_THRESH_PARM_P            1

#define WIN_NUM_INTERVALS_PARM_C                619      // (DEF,WdwIntrvlCnt_TPARCD,16,NA)
#define WIN_NUM_INTERVALS_PARM_P                  1

#define DESPORT_THRESH_PARM_C                   620      // (DEF,OutlrThrsh_TPARCD,16,NA) (T649,OutlrThrsh_TPARCD,float,NA)
#define DESPORT_THRESH_PARM_P                     1

#define BANDSIZE_PARM_C                         621      // (DEF,BndSz_TPARCD,16,NA) (T649,BndSz_TPARCD,32,NA)
#define BANDSIZE_PARM_P                           1

#define SPIRAL_TAIL_LEN_MAX_PARM_C              622      // (DEF,SpirlTailLenMx_TPARCD,16,NA) (T649,SpirlTailLenMx_TPARCD,float,NA)
#define SPIRAL_TAIL_LEN_MAX_PARM_P                1

#define RADIAL_FILL_PAD_CONST_PARM_C            623      // (DEF,RdlFillPadConst_TPARCD,16,NA)
#define RADIAL_FILL_PAD_CONST_PARM_P              1

#define RADIAL_TAIL_LEN_PARM_C                  624      // (DEF,RdlTailLen_TPARCD[0-3],16,NA)
#define RADIAL_TAIL_LEN_PARM_P                    4

#define TANGENTIAL_FILL_PAD_PARM_C              625      // (DEF,TgntlFillPad_TPARCD[0-2],16,NA)
#define TANGENTIAL_FILL_PAD_PARM_P                3

#define TANGENTIAL_TAIL_LEN_PERC_PARM_C         626      // (DEF,TgntlTailLenPrct_TPARCD,16,NA)
#define TANGENTIAL_TAIL_LEN_PERC_PARM_P           1

#define SPIRAL_FILL_PAD_PARM_C                  627      // (DEF,SpirlFillPad_TPARCD,16,NA)
#define SPIRAL_FILL_PAD_PARM_P                    1

#define SPIRAL_TAIL_PAD_PARM_C                  628      // (DEF,SpirlTailPad_TPARCD,16,NA)
#define SPIRAL_TAIL_PAD_PARM_P                    1

#define SPIRAL_TAIL_LEN_PERC_PARM_C             629      // (DEF,SpirlTailLenPrct_TPARCD,16,NA)
#define SPIRAL_TAIL_LEN_PERC_PARM_P               1

#define PSD_STD_DEV_LIMIT_PARM_C                630      // (DEF,PsdStdevLmt_TPARCD,16,NA)
#define PSD_STD_DEV_LIMIT_PARM_P                  1

#define PSD_VAR_THRESH_SCALER_PARM_C            631      // (DEF,PsdVarThrshScal_TPARCD,F,NA)
#define PSD_VAR_THRESH_SCALER_PARM_P              1

#define PSD_LINEAR_FIT_LENGTH_PARM_C            632      // (DEF,PsdLinearFitLen_TPARCD,16,NA)
#define PSD_LINEAR_FIT_LENGTH_PARM_P              1

#define DATA_ID_PARM_C                          633      // (DEF,DtaId_TPARCD,16,NA)
#define DATA_ID_PARM_P                            1

#define TA_THRESHOLD_PARM_C                     634      // (DEF,TaThrsh_TPARCD,16,NA)
#define TA_THRESHOLD_PARM_P                       1

#define TA_LPF_PARM_C                           635      // (DEF,TaLpf_TPARCD,16,NA)
#define TA_LPF_PARM_P                             1

#define WD_PER_HEAD_LIMIT_PARM_C                636      // (DEF,WrErrPerHdLmt_TPARCD,16,NA)
#define WD_PER_HEAD_LIMIT_PARM_P                  1

#define RD_PER_HEAD_LIMIT_PARM_C                637      // (DEF,RdErrPerHdLmt_TPARCD,16,NA)
#define RD_PER_HEAD_LIMIT_PARM_P                  1

#define NUM_SCRATCH_LIMIT_PARM_C                638      // (DEF,ScrLmt_TPARCD,16,NA)
#define NUM_SCRATCH_LIMIT_PARM_P                  1

#define NUM_REGIONS_LIMIT_PARM_C                639      // (DEF,RegnLmt_TPARCD,16,NA)
#define NUM_REGIONS_LIMIT_PARM_P                  1

#define NUM_GROUPS_LIMIT_PARM_C                 640      // (DEF,GrpLmt_TPARCD,16,NA)
#define NUM_GROUPS_LIMIT_PARM_P                   1

#define FOLDER_NAME_PARM_C                      641      // (DEF,FldrNam_TPARCD,8,NA) (DEF,FldrNam_TPARCD[0-3],16,NA)
#define FOLDER_NAME_PARM_P                        4

#define LINEAR_DENSITY_THRESH_PARM_C            642      // (DEF,LinearDnstyThrsh_TPARCD,16,NA) (T649,LinearDnstyThrsh_TPARCD,float,NA)
#define LINEAR_DENSITY_THRESH_PARM_P              1

#define PARAMETER_DIVISOR_PARM_C                643      // (DEF,Scal_TPARCD,16,NA) (T649,Scal2_TPARCD,float,NA)
#define PARAMETER_DIVISOR_PARM_P                  1

#define LONG_SPIRAL_SIGMA_THRESH_PARM_C         644      // (DEF,LngSpirlSgmaThrsh_TPARCD,16,NA)
#define LONG_SPIRAL_SIGMA_THRESH_PARM_P           1

#define REG_ADDR_PARM_C                         645      // (DEF,RegAddr_TPARCD,16,NA)
#define REG_ADDR_PARM_P                           1

#define VERIFY_AUDIT_INTERVAL_PARM_C            646      // (DEF,WrVfyAudtIntrvl_TPARCD,16,NA)
#define VERIFY_AUDIT_INTERVAL_PARM_P              1

#define TMNG_ERR_RANGE_LIMIT_PARM_C             647      // (DEF,TmgErrRgLmt_TPARCD,16,NA)
#define TMNG_ERR_RANGE_LIMIT_PARM_P               1

#define TMNG_FIT_ERR_REF_LIMIT_PARM_C           648      // (DEF,TmgFitErrLmt_TPARCD,16,NA)
#define TMNG_FIT_ERR_REF_LIMIT_PARM_P             1

#define EARLY_FLAW_PARM_C                       649      // (DEF,EarlyFlaw_TPARCD,16,NA)
#define EARLY_FLAW_PARM_P                         3

#define TPI_MAX_PUSH_RELAX_PARM_C               650      // (DEF,TpiMxPushRlax_TPARCD,16,NA)
#define TPI_MAX_PUSH_RELAX_PARM_P                 1

#define MOVING_BACKOFF_PARM_C                   651      // (DEF,MovgBckOff_TPARCD,16,NA)
#define MOVING_BACKOFF_PARM_P                     1

#define POLYFIT_PARM_C                          652      // (DEF,PolyOrdr_TPARCD,16,NA)
#define POLYFIT_PARM_P                            1

#define SKIP_TRACK_LIMIT_PARM_C                 653      // (DEF,SkpTrkLmt_TPARCD,16,NA)
#define SKIP_TRACK_LIMIT_PARM_P                   1

#define RDM_SEEK_BEFORE_WRT_PARM_C              654      // (T51,Cwrd1_TPARCD,16,0x0020)
#define RDM_SEEK_BEFORE_WRT_PARM_P                1

#define BAND_WRITES_PARM_C                      655      // (DEF,BndWr_TPARCD,16,NA)
#define BAND_WRITES_PARM_P                        1

#define BAND_SIZE_PARM_C                        656      // (DEF,BndSz_TPARCD,16,NA)
#define BAND_SIZE_PARM_P                          1

#define AUDIT_ONLY_REVS_PARM_C                  657      // (DEF,AudtRvs_TPARCD,16,NA)
#define AUDIT_ONLY_REVS_PARM_P                    1

#define TRK_WINDOW_SIZE_PARM_C                  658      // (DEF,TrkWdwSz_TPARCD,16,NA)
#define TRK_WINDOW_SIZE_PARM_P                    1

#define SYMBOL_PSN_WINDOW_SIZE_PARM_C           659      // (DEF,SymblPsnWdwSz_TPARCD,16,NA)
#define SYMBOL_PSN_WINDOW_SIZE_PARM_P             1

#define CENTER_TRACK_WRITES_PARM_C              660      // (DEF,CentrTrkWr_TPARCD,16,NA)
#define CENTER_TRACK_WRITES_PARM_P                1

#define RADIAL_FILL_PAD_PERC_PARM_C             661      // (DEF,RdlFillPadPrct_TPARCD,16,NA)
#define RADIAL_FILL_PAD_PERC_PARM_P               1

#define TANGENTIAL_TAIL_LEN_MAX_PARM_C          662      // (DEF,TgntlTailLenMx_TPARCD,16,NA) (T649,TgntlTailLenMx_TPARCD,float,NA)
#define TANGENTIAL_TAIL_LEN_MAX_PARM_P            1

#define WPOWER_PARM_C                           663      // (DEF,WrPwr_TPARCD,16,NA)
#define WPOWER_PARM_P                             1

#define TA_VERIFY_RETRY_PARM_C                  664      // (DEF,TaVfy_TPARCD,16,NA)
#define TA_VERIFY_RETRY_PARM_P                    2

#define DIVISOR_PARM_C                          665      // (DEF,Scal_TPARCD,16,NA)
#define DIVISOR_PARM_P                            1

#define REG_TO_OPT5_PARM_C                      666      // (DEF,OptReg04_TPARCD,16,NA)
#define REG_TO_OPT5_PARM_P                        4

#define REG_TO_OPT5_EXT_PARM_C                  667      // (DEF,OptRegExt04_TPARCD,16,NA)
#define REG_TO_OPT5_EXT_PARM_P                    3

#define REG_TO_OPT6_PARM_C                      668      // (DEF,OptReg05_TPARCD,16,NA)
#define REG_TO_OPT6_PARM_P                        4

#define REG_TO_OPT6_EXT_PARM_C                  669      // (DEF,OptRegExt05_TPARCD,16,NA)
#define REG_TO_OPT6_EXT_PARM_P                    3

#define REG_TO_OPT7_PARM_C                      670      // (DEF,OptReg06_TPARCD,16,NA)
#define REG_TO_OPT7_PARM_P                        4

#define REG_TO_OPT7_EXT_PARM_C                  671      // (DEF,OptRegExt06_TPARCD,16,NA)
#define REG_TO_OPT7_EXT_PARM_P                    3

#define REG_TO_OPT8_PARM_C                      672      // (DEF,OptReg07_TPARCD,16,NA)
#define REG_TO_OPT8_PARM_P                        4

#define REG_TO_OPT8_EXT_PARM_C                  673      // (DEF,OptRegExt07_TPARCD,16,NA)
#define REG_TO_OPT8_EXT_PARM_P                    3

#define REG_TO_OPT9_PARM_C                      674      // (DEF,OptReg08_TPARCD,16,NA)
#define REG_TO_OPT9_PARM_P                        4

#define REG_TO_OPT9_EXT_PARM_C                  675      // (DEF,OptRegExt08_TPARCD,16,NA)
#define REG_TO_OPT9_EXT_PARM_P                    3

#define REG_TO_OPT10_PARM_C                     676      // (DEF,OptReg09_TPARCD,16,NA)
#define REG_TO_OPT10_PARM_P                       4

#define REG_TO_OPT10_EXT_PARM_C                 677      // (DEF,OptRegExt09_TPARCD,16,NA)
#define REG_TO_OPT10_EXT_PARM_P                   3

#define REG_TO_OPT11_PARM_C                     678      // (DEF,OptReg10_TPARCD,16,NA)
#define REG_TO_OPT11_PARM_P                       4

#define REG_TO_OPT11_EXT_PARM_C                 679      // (DEF,OptRegExt10_TPARCD,16,NA)
#define REG_TO_OPT11_EXT_PARM_P                   3

#define REG_TO_OPT12_PARM_C                     680      // (DEF,OptReg11_TPARCD,16,NA)
#define REG_TO_OPT12_PARM_P                       4

#define REG_TO_OPT12_EXT_PARM_C                 681      // (DEF,OptRegExt11_TPARCD,16,NA)
#define REG_TO_OPT12_EXT_PARM_P                   3

#define DWELL_ID_PARM_C                         682      // (DEF,IdDwell_TPARCD,16,NA)
#define DWELL_ID_PARM_P                           1

#define SLIP_LIMIT_PERCENT_PARM_C               683      // (DEF,SlipLmtPrct_TPARCD,16,NA)
#define SLIP_LIMIT_PERCENT_PARM_P                 1

#define ACFF_DELTA_LIMIT_LOW_PARM_C             684      // (DEF,AcffDltaLmt_TPARCD[0],32,NA)
#define ACFF_DELTA_LIMIT_LOW_PARM_P               2

#define ACFF_DELTA_LIMIT_HIGH_PARM_C            685      // (DEF,AcffDltaLmt_TPARCD[1],32,NA)
#define ACFF_DELTA_LIMIT_HIGH_PARM_P              2

#define NORMAL_STEP_PARM_C                      686      // (DEF,NrmlInc_TPARCD,16,NA)
#define NORMAL_STEP_PARM_P                        1

#define TINY_STEP_PARM_C                        687      // (DEF,TinyInc_TPARCD,16,NA)
#define TINY_STEP_PARM_P                          1

#define WEIGHT_HIGH_PARM_C                      688      // (DEF,Wgt_TPARCD[1],16,NA)
#define WEIGHT_HIGH_PARM_P                        1

#define WEIGHT_LOW_PARM_C                       689      // (DEF,Wgt_TPARCD[0],16,NA)
#define WEIGHT_LOW_PARM_P                         1

#define BIAS_AVG_PARM_C                         690      // (DEF,BiasAvg_TPARCD,16,NA)
#define BIAS_AVG_PARM_P                           1

#define TIMER_MAX_PARM_C                        691      // (DEF,TmrMx_TPARCD,16,NA)
#define TIMER_MAX_PARM_P                          1

#define RETRY_COUNTER_MAX_PARM_C                692      // (DEF,RtryCntrMx_TPARCD,16,NA)
#define RETRY_COUNTER_MAX_PARM_P                  1

#define VTPI_COEFFS_PARM_C                      693      // (DEF,VtpiCoef_TPARCD,32,NA)
#define VTPI_COEFFS_PARM_P                        7

#define VTPI_USEORIMULTIPLIERS_PARM_C           694      // (T185,Cwrd2_TPARCD,16,0x0200)
#define VTPI_USEORIMULTIPLIERS_PARM_P             1

#define MAX_MR_BIAS_SCALAR_PARM_C               695      // (DEF,MxMrBiasScal_TPARCD,16,NA)
#define MAX_MR_BIAS_SCALAR_PARM_P                 1

#define MAX_TA_AMPLITUDE_PARM_C                 696      // (DEF,MxTaAmp_TPARCD,16,NA)
#define MAX_TA_AMPLITUDE_PARM_P                   1

#define TA_ID_TRACK_SPEC_PARM_C                 697      // (DEF,TaTrkLmt_TPARCD[1],32,NA)
#define TA_ID_TRACK_SPEC_PARM_P                   1

#define TA_OD_TRACK_SPEC_PARM_C                 698      // (DEF,TaTrkLmt_TPARCD[0],32,NA)
#define TA_OD_TRACK_SPEC_PARM_P                   1

#define GRADING_OUTPUT_PARM_C                   699      // (DEF,GradngOutpt_TPARCD,8,0x0001) (T707,GradngOutpt_TPARCD,8,NA)
#define GRADING_OUTPUT_PARM_P                     1

#define STD_DEV_XZONE_LIMIT_PARM_C              700      // (DEF,AvgAgcStdevLmt_TPARCD,16,NA)
#define STD_DEV_XZONE_LIMIT_PARM_P                1

#define OCLIM_BIN_THRESHOLD_PARM_C              701      // (DEF,OclimBinThrsh_TPARCD,16,NA)
#define OCLIM_BIN_THRESHOLD_PARM_P                3

#define CWORD3_PARM_C                           702      // (DEF,Cwrd3_TPARCD,16,NA)
#define CWORD3_PARM_P                             1

#define VCM_SEEK_STEP_PARM_C                    703      // (DEF,VcmSk_TPARCD[2],32,NA)
#define VCM_SEEK_STEP_PARM_P                      1

#define VCM_HEAT_SEEKS_PARM_C                   704      // (DEF,VcmSk_TPARCD[0],32,NA)
#define VCM_HEAT_SEEKS_PARM_P                     1

#define VCM_SEEK_LENGTH_PARM_C                  705      // (DEF,VcmSk_TPARCD[1],32,NA)
#define VCM_SEEK_LENGTH_PARM_P                    1

#define OPTIONS_PARM_C                          706      // (T178,FafhOpt_TPARCD,8,NA) (T510,Optn_TPARCD,16,0x0001) (T510,Optn_TPARCD,16,0x0002) (T510,Optn_TPARCD,16,0x0008) (T510,Optn_TPARCD,16,0x0040) (T510,Optn_TPARCD,16,0x0080) (T510,Optn_TPARCD,16,0xFF00)
#define OPTIONS_PARM_P                            1      // (T544,Optn_TPARCD,16,NA) (T544,Optn_TPARCD,16,0x0001) (T602,UdsOptn_TPARCD,8,NA) (T605,Optn_TPARCD,16,0x0001) (T605,Optn_TPARCD,16,0x0002) (T619,Optn_TPARCD,16,0x00FF) (T634,Optn_TPARCD,16,0x0001) (T718,OptnByt_TPARCD,8,NA)

#define NUM_WEDGES_PARM_C                       707      // (DEF,WdgCnt_TPARCD,16,NA)
#define NUM_WEDGES_PARM_P                         1

#define FLY_HEIGHT_PARM_C                       708      // (DEF,FlyHght_TPARCD,16,NA)
#define FLY_HEIGHT_PARM_P                         1

#define SET_XREG00_PARM_C                       709      // (NA,NA,NA,NA)
#define SET_XREG00_PARM_P                         3

#define SET_XREG01_PARM_C                       710      // (NA,NA,NA,NA)
#define SET_XREG01_PARM_P                         3

#define SET_XREG02_PARM_C                       711      // (NA,NA,NA,NA)
#define SET_XREG02_PARM_P                         3

#define SET_XREG03_PARM_C                       712      // (NA,NA,NA,NA)
#define SET_XREG03_PARM_P                         3

#define SET_XREG04_PARM_C                       713      // (NA,NA,NA,NA)
#define SET_XREG04_PARM_P                         3

#define SET_XREG05_PARM_C                       714      // (NA,NA,NA,NA)
#define SET_XREG05_PARM_P                         3

#define SET_XREG06_PARM_C                       715      // (NA,NA,NA,NA)
#define SET_XREG06_PARM_P                         3

#define SET_XREG07_PARM_C                       716      // (NA,NA,NA,NA)
#define SET_XREG07_PARM_P                         3

#define SET_XREG08_PARM_C                       717      // (NA,NA,NA,NA)
#define SET_XREG08_PARM_P                         3

#define SET_XREG09_PARM_C                       718      // (NA,NA,NA,NA)
#define SET_XREG09_PARM_P                         3

#define SET_XREG10_PARM_C                       719      // (NA,NA,NA,NA)
#define SET_XREG10_PARM_P                         3

#define SET_XREG11_PARM_C                       720      // (NA,NA,NA,NA)
#define SET_XREG11_PARM_P                         3

#define SET_XREG12_PARM_C                       721      // (NA,NA,NA,NA)
#define SET_XREG12_PARM_P                         3

#define SET_XREG13_PARM_C                       722      // (NA,NA,NA,NA)
#define SET_XREG13_PARM_P                         3

#define SET_XREG14_PARM_C                       723      // (NA,NA,NA,NA)
#define SET_XREG14_PARM_P                         3

#define SET_XREG15_PARM_C                       724      // (NA,NA,NA,NA)
#define SET_XREG15_PARM_P                         3

#define SET_XREG16_PARM_C                       725      // (NA,NA,NA,NA)
#define SET_XREG16_PARM_P                         3

#define SET_XREG17_PARM_C                       726      // (NA,NA,NA,NA)
#define SET_XREG17_PARM_P                         3

#define SET_XREG18_PARM_C                       727      // (NA,NA,NA,NA)
#define SET_XREG18_PARM_P                         3

#define SET_XREG19_PARM_C                       728      // (NA,NA,NA,NA)
#define SET_XREG19_PARM_P                         3

#define SET_XREG20_PARM_C                       729      // (NA,NA,NA,NA)
#define SET_XREG20_PARM_P                         3

#define SET_XREG21_PARM_C                       730      // (NA,NA,NA,NA)
#define SET_XREG21_PARM_P                         3

#define SET_XREG22_PARM_C                       731      // (NA,NA,NA,NA)
#define SET_XREG22_PARM_P                         3

#define SET_XREG23_PARM_C                       732      // (NA,NA,NA,NA)
#define SET_XREG23_PARM_P                         3

#define SET_XREG24_PARM_C                       733      // (NA,NA,NA,NA)
#define SET_XREG24_PARM_P                         3

#define SET_XREG25_PARM_C                       734      // (NA,NA,NA,NA)
#define SET_XREG25_PARM_P                         3

#define SET_XREG26_PARM_C                       735      // (NA,NA,NA,NA)
#define SET_XREG26_PARM_P                         3

#define SET_XREG27_PARM_C                       736      // (NA,NA,NA,NA)
#define SET_XREG27_PARM_P                         3

#define SET_XREG28_PARM_C                       737      // (NA,NA,NA,NA)
#define SET_XREG28_PARM_P                         3

#define SET_XREG29_PARM_C                       738      // (NA,NA,NA,NA)
#define SET_XREG29_PARM_P                         3

#define MAX_FLAWS_PARM_C                        739      // (DEF,MxFlawCnt_TPARCD,16,NA)
#define MAX_FLAWS_PARM_P                          2

#define NLD_WRITE_LOOP_PARM_C                   740      // (DEF,NldWrItr_TPARCD,16,NA)
#define NLD_WRITE_LOOP_PARM_P                     1

#define NLD_READ_LOOP_PARM_C                    741      // (DEF,NldRdItr_TPARCD,16,NA)
#define NLD_READ_LOOP_PARM_P                      1

#define TA_ID_OD_MAX_AMP_PARM_C                 742      // (NA,NA,NA,NA)
#define TA_ID_OD_MAX_AMP_PARM_P                   1

#define TA_ID_MAX_AMP_PARM_C                    743      // (DEF,TaMxAmp_TPARCD[1],16,NA)
#define TA_ID_MAX_AMP_PARM_P                      1

#define TA_OD_MAX_AMP_PARM_C                    744      // (DEF,TaMxAmp_TPARCD[0],16,NA)
#define TA_OD_MAX_AMP_PARM_P                      1

#define SWD_RETRY_PARM_C                        745      // (DEF,SwdRtry_TPARCD,16,NA)
#define SWD_RETRY_PARM_P                          1

#define SPECIFIC_HEAD_PARM_C                    746      // (DEF,TstHd_TPARCD,8,NA)
#define SPECIFIC_HEAD_PARM_P                      1

#define RADIAL_TAIL_LEN_2_PARM_C                747      // (DEF,RdlTailLen2_TPARCD[0-3],16,NA)
#define RADIAL_TAIL_LEN_2_PARM_P                  4

#define RADIAL_SPAN_1_PARM_C                    748      // (DEF,RdlRg1_TPARCD[0-3],16,NA)
#define RADIAL_SPAN_1_PARM_P                      4

#define RADIAL_SPAN_2_PARM_C                    749      // (DEF,RdlRg2_TPARCD[0-3],16,NA)
#define RADIAL_SPAN_2_PARM_P                      4

#define RADIAL_SPN_TA_PARM_C                    750      // (DEF,RdlRgTa_TPARCD,16,NA)
#define RADIAL_SPN_TA_PARM_P                      1

#define RADIAL_SPAN_TA_LEN_PARM_C               751      // (DEF,RdlRgTaLen_TPARCD,16,NA)
#define RADIAL_SPAN_TA_LEN_PARM_P                 1

#define RADIAL_SPAN_TA_PAD_PARM_C               752      // (DEF,RdlRgTaPad_TPARCD,16,NA)
#define RADIAL_SPAN_TA_PAD_PARM_P                 1

#define CLR_COEF_ADJ_PARM_C                     753      // (DEF,ClrCoefAdj_TPARCD,F,NA)
#define CLR_COEF_ADJ_PARM_P                       4

#define AFH_GAMMA_PARM_C                        754      // (DEF,AfhGamma_TPARCD,16,NA)    (T178,AfhHtGamma_TPARCD,F,NA)
#define AFH_GAMMA_PARM_P                          6

#define SYNC_REQUIRED_PARM_C                    755      // (T1,Cwrd1_TPARCD,16,0x0004)
#define SYNC_REQUIRED_PARM_P                      0

#define ZEDD_FREEZE_PERIOD_PARM_C               756      // (NA,NA,NA,NA)
#define ZEDD_FREEZE_PERIOD_PARM_P                 1

#define ZEDD_THRESH_MULTIPLIER_PARM_C           757      // (NA,NA,NA,NA)
#define ZEDD_THRESH_MULTIPLIER_PARM_P             1

#define ZEDD_INV_GAIN_PARM_C                    758      // (NA,NA,NA,NA)
#define ZEDD_INV_GAIN_PARM_P                      1

#define STD_DEV_LIMIT_FLOAT_PARM_C              759      // (DEF,StdevLmt_TPARCD,16,NA)
#define STD_DEV_LIMIT_FLOAT_PARM_P                2

#define VARTHRESH_BACKUPDAC_STEP_PARM_C         760      // (DEF,ThrshBckupDacInc_TPARCD,16,NA)
#define VARTHRESH_BACKUPDAC_STEP_PARM_P           1

#define RZ_RRO_AUDIT_INTERVAL_PARM_C            761      // (DEF,RdRroAudtIntrvl_TPARCD,16,NA)
#define RZ_RRO_AUDIT_INTERVAL_PARM_P              1

#define WZ_RRO_AUDIT_INTERVAL_PARM_C            762      // (DEF,WrRroAudtIntrvl_TPARCD,16,NA)
#define WZ_RRO_AUDIT_INTERVAL_PARM_P              1

#define RZ_VERIFY_AUDIT_INTERVAL_PARM_C         763      // (DEF,RdVfyAudtIntrvl_TPARCD,16,NA)
#define RZ_VERIFY_AUDIT_INTERVAL_PARM_P           1

#define WZ_VERIFY_AUDIT_INTERVAL_PARM_C         764      // (DEF,WrVfyAudtIntrvl_TPARCD,16,NA)
#define WZ_VERIFY_AUDIT_INTERVAL_PARM_P           1

#define WZ_SETTLE_DELAY_PARM_C                  765      // (DEF,WrSetlDly_TPARCD,16,NA)
#define WZ_SETTLE_DELAY_PARM_P                    1

#define RZ_SETTLE_DELAY_PARM_C                  766      // (DEF,RdSetlDly_TPARCD,16,NA)
#define RZ_SETTLE_DELAY_PARM_P                    1

#define VPD_DATA_PARM_C                         767      // (DEF,VpdDta_TPARCD,16,NA)
#define VPD_DATA_PARM_P                           2

#define WRODDTRK_PARM_C                         768      // (T109,Cwrd4_TPARCD,16,0x0100) (T275,Cwrd2_TPARCD,16,0x0100)
#define WRODDTRK_PARM_P                           0

#define WREVENTRK_PARM_C                        769      // (T109,Cwrd4_TPARCD,16,0x0200) (T275,Cwrd2_TPARCD,16,0x0200)
#define WREVENTRK_PARM_P                          0

#define LUL_SCAN_SCRATCH_PARM_C                 770      // (DEF,LulScnScr_TPARCD,16,NA)
#define LUL_SCAN_SCRATCH_PARM_P                   6

#define OFFSET_PARM_C                           771      // (DEF,Ofst_TPARCD,16,NA)
#define OFFSET_PARM_P                             1

#define NUM_LBAS_PARM_C                         772      // (DEF,LbaCnt_TPARCD[1],32,NA)
#define NUM_LBAS_PARM_P                           2

#define NOTCH_DEPTH_PARM_C                      773      // (DEF,NtchCnfg_TPARCD[1],16,NA)
#define NOTCH_DEPTH_PARM_P                        1

#define BANDWIDTH_PARM_C                        774      // (DEF,BndWdth_TPARCD,16,NA)
#define BANDWIDTH_PARM_P                          1

#define CLEARANCE_PARM_C                        775      // (T74,Clrnc_TPARCD,16,NA)
#define CLEARANCE_PARM_P                          1

#define SHORT_SCRATCH_PREPASS_PARM_C            776      // (T118,Cwrd1,16,0x0020) (T649,Cwrd1_TPARCD,16,0x0020)
#define SHORT_SCRATCH_PREPASS_PARM_P              1

#define FVGA_MAX_PARM_C                         777      // (DEF,FltrVgaMx_TPARCD,16,NA)
#define FVGA_MAX_PARM_P                           1

#define DVGA_MAX_PARM_C                         778      // (DEF,DltaVgaMx_TPARCD,16,NA) (T564,MxSvoDvga_TPARCD,16,NA)
#define DVGA_MAX_PARM_P                           1

#define RVGA_MAX_PARM_C                         779      // (DEF,VgaMx_TPARCD,16,NA) (T564,MxSvoRvga_TPARCD,16,NA)
#define RVGA_MAX_PARM_P                           1

#define MAX_FLY_CYL_PARM_C                      780      // (DEF,MxFlyCyl_TPARCD,32,NA)
#define MAX_FLY_CYL_PARM_P                        2

#define MAX_STROKE_PARM_C                       781      // (DEF,MxTrkRg_TPARCD,32,NA)
#define MAX_STROKE_PARM_P                         2

#define MAX_CYL_PARM_C                          782      // (DEF,MxCylLmt_TPARCD,32,NA)
#define MAX_CYL_PARM_P                            2

#define SEEK_TIME_LIMIT_PARM_C                  783      // (DEF,SkTmLmt_TPARCD,16,NA)
#define SEEK_TIME_LIMIT_PARM_P                    1

#define WZ_IZBE_CONF_LEVEL_PARM_C               784      // (DEF,WrIzbeCnfLvl_TPARCD,16,NA)
#define WZ_IZBE_CONF_LEVEL_PARM_P                 2

#define RZ_IZBE_CONF_LEVEL_PARM_C               785      // (DEF,RdIzbeCnfLvl_TPARCD,16,NA)
#define RZ_IZBE_CONF_LEVEL_PARM_P                 2

#define MAX_RAMP_CYL_PARM_C                     786      // (DEF,MxRmpCyl_TPARCD,16,NA)
#define MAX_RAMP_CYL_PARM_P                       2

#define MIN_RAMP_CYL_PARM_C                     787      // (DEF,MnRmpCyl_TPARCD,16,NA)
#define MIN_RAMP_CYL_PARM_P                       2

#define WDG_PAD_TAIL_PARM_C                     788      // (NA,NA,NA,NA)
#define WDG_PAD_TAIL_PARM_P                       4

#define WDG_PAD_WIDTH_PARM_C                    789      // (NA,NA,NA,NA)
#define WDG_PAD_WIDTH_PARM_P                      4

#define GROUP_ENTRY_COUNT_PARM_C                790      // (NA,NA,NA,NA)
#define GROUP_ENTRY_COUNT_PARM_P                  4

#define MAX_BACKOFF_PARM_C                      791      // (DEF,MxBckOff_TPARCD,8,NA)
#define MAX_BACKOFF_PARM_P                        3

#define ACFF_DELTA_SPIKE_WEIGHT_PARM_C          792      // (DEF,AcffDltaWgt_TPARCD,16,NA)
#define ACFF_DELTA_SPIKE_WEIGHT_PARM_P            1

#define SETTLE_COUNTER_MAX_PARM_C               793      // (DEF,SetlCntMx_TPARCD,16,NA)
#define SETTLE_COUNTER_MAX_PARM_P                 1

#define ACFF_DELTA_SCALE_PARM_C                 794      // (DEF,AcffDltaScal_TPARCD,16,NA)
#define ACFF_DELTA_SCALE_PARM_P                   1

#define SYS_AREA_PREP_STATE_PARM_C              795      // (DEF,SysAreaStat_TPARCD,8,NA)
#define SYS_AREA_PREP_STATE_PARM_P                1

#define TIMEOUT_TIMER_SEC_PARM_C                796      // (NA,NA,NA,NA)
#define TIMEOUT_TIMER_SEC_PARM_P                  1

#define ZAG_SECTOR_OFFSET_PARM_C                797      // (DEF,ZagSctrOfst_TPARCD,16,NA)
#define ZAG_SECTOR_OFFSET_PARM_P                  1

#define STUTTER_LIMIT_PARM_C                    798      // (DEF,ZagStutrLmt_TPARCD,16,NA)
#define STUTTER_LIMIT_PARM_P                      2

#define DICE_PARM_C                             799      // (NA,NA,NA,NA)
#define DICE_PARM_P                               9

#define DICE_MAX_DAC_PARM_C                     800      // (DEF,DiceMxDac_TPARCD,16,NA)
#define DICE_MAX_DAC_PARM_P                       2

#define DICE_AUDIT_PARM_C                       801      // (DEF,DiceAudt_TPARCD,16,NA)
#define DICE_AUDIT_PARM_P                         3

#define DEGAUSS_ON_ERR_LIM_PARM_C               802      // (DEF,DgsErrLmt_TPARCD[0],16,NA)
#define DEGAUSS_ON_ERR_LIM_PARM_P                 1

#define DEGAUSS_OFF_ERR_LIM_PARM_C              803      // (DEF,DgsErrLmt_TPARCD[1],16,NA)
#define DEGAUSS_OFF_ERR_LIM_PARM_P                1

#define NARROW_LEFT_LIM_PARM_C                  804      // (T150,WdthLmt_TPARCD[0],16,NA) (T150,WdthRg_TPARCD[0],16,NA)
#define NARROW_LEFT_LIM_PARM_P                    2

#define NARROW_RIGHT_LIM_PARM_C                 805      // (T150,WdthLmt_TPARCD[1],16,NA) (T150,WdthRg_TPARCD[1],16,NA)
#define NARROW_RIGHT_LIM_PARM_P                   2

#define NARROW_MID_LIM_PARM_C                   806      // (T150,WdthLmt_TPARCD[2],16,NA) (T150,WdthRg_TPARCD[2],16,NA)
#define NARROW_MID_LIM_PARM_P                     2

#define ZEDD_INITIAL_THRESH_PARM_C              807      // (DEF,ZddInitThrsh_TPARCD[0],16,NA)
#define ZEDD_INITIAL_THRESH_PARM_P                1

#define ZEDD_MAX_EVENT_WIDTH_PARM_C             808      // (DEF,ZddMxEvntWdth_TPARCD,16,NA)
#define ZEDD_MAX_EVENT_WIDTH_PARM_P               1

#define ZEDD_THRESH_RATIO_PARM_C                809      // (DEF,ZddThrshRatio_TPARCD[0],16,NA)
#define ZEDD_THRESH_RATIO_PARM_P                  1

#define RPS_SEEK_LENGTHS_PARM_C                 810      // (DEF,RpsSkLen_TPARCD,16,NA)
#define RPS_SEEK_LENGTHS_PARM_P                  32

#define RD_SCALE_FACTORS_PARM_C                 811      // (DEF,RdScal_TPARCD,16,NA)
#define RD_SCALE_FACTORS_PARM_P                  16

#define WR_SCALE_FACTORS_PARM_C                 812      // (DEF,WrScal_TPARCD,16,NA)
#define WR_SCALE_FACTORS_PARM_P                  16

#define MDS_MAX_TOT_BYTES_WCYL32_PARM_C         813      // (DEF,MdsDfctvBytLmt_TPARCD,16,NA)
#define MDS_MAX_TOT_BYTES_WCYL32_PARM_P           2

#define AGC_SAFETY_FACTOR_PARM_C                814      // (DEF,AgcMargn_TPARCD,16,NA)
#define AGC_SAFETY_FACTOR_PARM_P                  2

#define SAFETY_FILL_PARM_C                      815      // (DEF,SftyFill_TPARCD,16,NA)
#define SAFETY_FILL_PARM_P                        1

#define DICE_LIMITS_PARM_C                      816      // (DEF,DiceLmt_TPARCD,16,NA)
#define DICE_LIMITS_PARM_P                        3

#define POLY_SMOOTH_ORDER_PARM_C                817      // (DEF,PolyOrdr_TPARCD,16,NA)
#define POLY_SMOOTH_ORDER_PARM_P                  1

#define SWEEP_C1_PARM_C                         818      // (DEF,SwpConst1_TPARCD,16,NA)
#define SWEEP_C1_PARM_P                           1

#define SWEEP_C2_PARM_C                         819      // (DEF,SwpConst2_TPARCD,16,NA)
#define SWEEP_C2_PARM_P                           1

#define SWEEP_C3_PARM_C                         820      // (DEF,SwpConst3_TPARCD,16,NA)
#define SWEEP_C3_PARM_P                           1

#define SIDE_RAIL_LEN_PARM_C                    821      // (DEF,Rg_TPARCD,16,NA)
#define SIDE_RAIL_LEN_PARM_P                      1

#define RD_OFF_TRK_LIM_PARM_C                   822      // (DEF,RdOclim_TPARCD,16,NA)
#define RD_OFF_TRK_LIM_PARM_P                     1

#define RGN_NUM_SCRATCHES_PARM_C                823      // (DEF,RegnScrLmt_TPARCD,16,NA)
#define RGN_NUM_SCRATCHES_PARM_P                  1

#define AGC_MIN_PARM_C                          824      // (DEF,AgcLmt_TPARCD[0],16,NA)
#define AGC_MIN_PARM_P                            1

#define AGC_MAX_PARM_C                          825      // (DEF,AgcLmt_TPARCD[1],16,NA)
#define AGC_MAX_PARM_P                            1

#define RDM_SEEK_RETRIES_PARM_C                 826      // (DEF,SkRtryLmt_TPARCD,16,NA)
#define RDM_SEEK_RETRIES_PARM_P                   1

#define NOTCH_DEPTH_BY_ZONE_PARM_C              827      // (DEF,ZnNtchDpth_TPARCD,16,NA)
#define NOTCH_DEPTH_BY_ZONE_PARM_P                6

#define BANDWIDTH_BY_ZONE_PARM_C                828      // (DEF,ZnBndWdth_TPARCD,16,NA)
#define BANDWIDTH_BY_ZONE_PARM_P                  6

#define SECONDARY_PEAK_MAGNITUDE_PARM_C         829      // (NA,NA,NA,NA)
#define SECONDARY_PEAK_MAGNITUDE_PARM_P           1

#define PHASE_LIMIT_PARM_C                      830      // (DEF,PhasLmt_TPARCD,16,NA)
#define PHASE_LIMIT_PARM_P                        1

#define FSB_SEL_PARM_C                          831      // (DEF,Fsb_TPARCD,16,NA)
#define FSB_SEL_PARM_P                            2

#define DICE_AUDIT_FE_THRESH_PARM_C             832      // (DEF,DiceAudtThrsh_TPARCD,16,NA)
#define DICE_AUDIT_FE_THRESH_PARM_P               1

#define DELTA_LIMIT_POSTPROC_PARM_C             833      // (NA,NA,NA,NA)
#define DELTA_LIMIT_POSTPROC_PARM_P               1

#define SNO_GAIN_RATIO_PARM_C                   834      // (DEF,SnoGainRatio_TPARCD,16,NA)
#define SNO_GAIN_RATIO_PARM_P                     1

#define HT_ONLY_CONTACT_DAC_PARM_C              835      // (DEF,CntctDac_TPARCD[1],8,NA)
#define HT_ONLY_CONTACT_DAC_PARM_P                1

#define HT_ONLY_TEST_CYL_PARM_C                 836      // (DEF,DacTstCyl_TPARCD[1],32,NA)
#define HT_ONLY_TEST_CYL_PARM_P                   2

#define WRT_HT_TEST_CYL_PARM_C                  837      // (DEF,DacTstCyl_TPARCD[0],32,NA)
#define WRT_HT_TEST_CYL_PARM_P                    2

#define WRT_HT_CONTACT_DAC_PARM_C               838      // (DEF,CntctDac_TPARCD[0],8,NA)
#define WRT_HT_CONTACT_DAC_PARM_P                 1

#define MAX_TRK_HARD_ERRORS_PARM_C              839      // (DEF,MxTrkErr_TPARCD,16,NA)
#define MAX_TRK_HARD_ERRORS_PARM_P                1

#define MAX_TRK_OTF_ERRORS_PARM_C               840      // (DEF,MxTrkOtfErr_TPARCD,16,NA)
#define MAX_TRK_OTF_ERRORS_PARM_P                 1

#define SPECTRAL_DETECTOR1_PARM_C               841      // (DEF,SpctrlDtct1_TPARCD,16,NA)
#define SPECTRAL_DETECTOR1_PARM_P                10

#define SPECTRAL_DETECTOR2_PARM_C               842      // (DEF,SpctrlDtct2_TPARCD,16,NA)
#define SPECTRAL_DETECTOR2_PARM_P                10

#define SPECTRAL_DETECTOR3_PARM_C               843      // (DEF,SpctrlDtct3_TPARCD,16,NA)
#define SPECTRAL_DETECTOR3_PARM_P                10

#define SPECTRAL_DETECTOR4_PARM_C               844      // (DEF,SpctrlDtct4_TPARCD,16,NA)
#define SPECTRAL_DETECTOR4_PARM_P                10

#define SPECTRAL_DETECTOR5_PARM_C               845      // (DEF,SpctrlDtct5_TPARCD,16,NA)
#define SPECTRAL_DETECTOR5_PARM_P                10

#define SPECTRAL_DETECTOR6_PARM_C               846      // (DEF,SpctrlDtct6_TPARCD,16,NA)
#define SPECTRAL_DETECTOR6_PARM_P                10

#define WRITE_TRIPLET_PARM_C                    847      // (DEF,WrTrplt_TPARCD,8,NA)
#define WRITE_TRIPLET_PARM_P                      3

#define MAX_BASELINE_DAC_PARM_C                 848      // (DEF,MxBaslneDac_TPARCD,16,NA)
#define MAX_BASELINE_DAC_PARM_P                   1

#define DACS_BEYOND_CONTACT_PARM_C              849      // (DEF,DacRg_TPARCD[1],16,NA)
#define DACS_BEYOND_CONTACT_PARM_P                1

#define SECTOR_RANGE1_PARM_C                    850      // (DEF,SctrRg1_TPARCD,16,NA)
#define SECTOR_RANGE1_PARM_P                      2

#define SECTOR_RANGE2_PARM_C                    851      // (DEF,SctrRg2_TPARCD,16,NA)
#define SECTOR_RANGE2_PARM_P                      2

#define SECTOR_RANGE3_PARM_C                    852      // (DEF,SctrRg3_TPARCD,16,NA)
#define SECTOR_RANGE3_PARM_P                      2

#define DAC_RANGE_PARM_C                        853      // (DEF,DacRg_TPARCD,16,NA)
#define DAC_RANGE_PARM_P                          3

#define CURVE_FIT_PARM_C                        854      // (DEF,Fit_TPARCD,16,NA)
#define CURVE_FIT_PARM_P                          4

#define AGCFILTER_PARM_C                        855      // (DEF,AgcFltr_TPARCD,16,NA)
#define AGCFILTER_PARM_P                          2

#define BASELINE_DAC_OFFSET_PARM_C              856      // (DEF,DacRg_TPARCD[0],16,NA)
#define BASELINE_DAC_OFFSET_PARM_P                1

#define CONTACT_DAC_RANGE_LIMIT_PARM_C          857      // (DEF,CntctDacRgLmt_TPARCD,16,NA)
#define CONTACT_DAC_RANGE_LIMIT_PARM_P            1

#define CYCLES_PER_ITERATION_PARM_C             858      // (DEF,CyclePerItr_TPARCD,16,NA)
#define CYCLES_PER_ITERATION_PARM_P               1

#define ITERATIONS_PARM_C                       859      // (DEF,Itr_TPARCD,16,NA) (T621,ItrCnt_TPARCD,16,NA) (T1509,ItrCnt_TPARCD,16,NA) (T5509,ItrCnt_TPARCD,16,NA)
#define ITERATIONS_PARM_P                         1

#define NUM_RADIAL_MEAS_POINTS_PARM_C           860      // (DEF,RdlMeasCnt_TPARCD,16,NA)
#define NUM_RADIAL_MEAS_POINTS_PARM_P             1

#define REVS_BY_ZONE_PARM_C                     861      // (DEF,RvsPerZn_TPARCD,16,NA)
#define REVS_BY_ZONE_PARM_P                      32

#define FREQ_BAND_LO_1_PARMS_PARM_C             862      // (DEF,FrqBndLo1_TPARCD,16,NA)
#define FREQ_BAND_LO_1_PARMS_PARM_P               3

#define FREQ_BAND_LO_2_PARMS_PARM_C             863      // (DEF,FrqBndLo2_TPARCD,16,NA)
#define FREQ_BAND_LO_2_PARMS_PARM_P               3

#define FREQ_BAND_MID_1_PARMS_PARM_C            864      // (DEF,FrqBndMid1_TPARCD,16,NA)
#define FREQ_BAND_MID_1_PARMS_PARM_P              3

#define FREQ_BAND_MID_2_PARMS_PARM_C            865      // (DEF,FrqBndMid2_TPARCD,16,NA)
#define FREQ_BAND_MID_2_PARMS_PARM_P              3

#define FREQ_BAND_HI_1_PARMS_PARM_C             866      // (DEF,FrqBndHi1_TPARCD,16,NA)
#define FREQ_BAND_HI_1_PARMS_PARM_P               3

#define FREQ_BAND_HI_2_PARMS_PARM_C             867      // (DEF,FrqBndHi2_TPARCD,16,NA)
#define FREQ_BAND_HI_2_PARMS_PARM_P               3

#define BITS_TO_READ_PARM_C                     868      // (DEF,RdBitCnt_TPARCD,16,NA)
#define BITS_TO_READ_PARM_P                       1

#define VERIFY_RPT_COUNT_PARM_C                 869      // (NA,NA,NA,NA)
#define VERIFY_RPT_COUNT_PARM_P                   1

#define SUPPRESS_TABLE_DISPLAY_PARM_C           870      // (DEF,SuprsTblDisp_TPARCD,16,NA)
#define SUPPRESS_TABLE_DISPLAY_PARM_P            10

#define SUPPRESS_PARAM_DISPLAY_PARM_C           871      // (NA,NA,NA,NA)
#define SUPPRESS_PARAM_DISPLAY_PARM_P             0

#define ERRS_B4_SFLAW_SCAN_VIA_REWRITE_PARM_C   872      // (DEF,ErrBfrSflwReWr_TPARCD,16,NA)
#define ERRS_B4_SFLAW_SCAN_VIA_REWRITE_PARM_P     1

#define CONTACT_LIMITS_PARM_C                   873      // (DEF,CntctLmt_TPARCD, ,NA)
#define CONTACT_LIMITS_PARM_P                     7

#define TIMEOUT_TIMER_SEC_32_BITS_PARM_C        874      // (NA,NA,NA,NA)
#define TIMEOUT_TIMER_SEC_32_BITS_PARM_P          2

#define CWORD4_PARM_C                           875      // (DEF,Cwrd4_TPARCD,16,NA)
#define CWORD4_PARM_P                             1

#define COARSE_SEARCH_START_CLEARANCE_PARM_C    876      // (DEF,Clrnc_TPARCD[0],16,NA)
#define COARSE_SEARCH_START_CLEARANCE_PARM_P      1

#define FINE_SEARCH_START_CLEARANCE_PARM_C      877      // (DEF,Clrnc_TPARCD[1],16,NA)
#define FINE_SEARCH_START_CLEARANCE_PARM_P        1

#define CONTACT_SEARCH_LIMIT_CLEARANCE_PARM_C   878      // (DEF,Clrnc_TPARCD[2],16,NA)
#define CONTACT_SEARCH_LIMIT_CLEARANCE_PARM_P     1

#define SELF_CHECK_PARM_C                       879      // (T49,Cwrd2_TPARCD,16,0x8000)
#define SELF_CHECK_PARM_P                         1

#define SET_ACPARM00_PARM_C                     880      // (NA,NA,NA,NA)
#define SET_ACPARM00_PARM_P                       5

#define SET_ACPARM01_PARM_C                     881      // (NA,NA,NA,NA)
#define SET_ACPARM01_PARM_P                       5

#define SET_ACPARM02_PARM_C                     882      // (NA,NA,NA,NA)
#define SET_ACPARM02_PARM_P                       5

#define SET_ACPARM03_PARM_C                     883      // (NA,NA,NA,NA)
#define SET_ACPARM03_PARM_P                       5

#define SET_ACPARM04_PARM_C                     884      // (NA,NA,NA,NA)
#define SET_ACPARM04_PARM_P                       5

#define SET_ACPARM05_PARM_C                     885      // (NA,NA,NA,NA)
#define SET_ACPARM05_PARM_P                       5

#define SET_ACPARM06_PARM_C                     886      // (NA,NA,NA,NA)
#define SET_ACPARM06_PARM_P                       5

#define SET_ACPARM07_PARM_C                     887      // (NA,NA,NA,NA)
#define SET_ACPARM07_PARM_P                       5

#define RW_MODE1_PARM_C                         888      // (NA,NA,NA,NA)
#define RW_MODE1_PARM_P                           1

#define ZONE_SKIP_MASK_PARM_C                   889      // (DEF,ZnSkpMsk_TPARCD,32,NA)
#define ZONE_SKIP_MASK_PARM_P                     2

#define DICE_FIT_ERR_THRESH2_PARM_C             890      // (DEF,DiceAudtThrsh2_TPARCD,16,NA)
#define DICE_FIT_ERR_THRESH2_PARM_P               1

#define RELATIVE_HEATER_EQN_PARM_C              891      // (DEF,HtrEqn_TPARCD,16,NA)
#define RELATIVE_HEATER_EQN_PARM_P                3

#define MULTIPLIER_NUM_DEN_PARM_C               892      // (DEF,SampRatScal_TPARCD,F,NA)
#define MULTIPLIER_NUM_DEN_PARM_P                 2

#define MIN_UNLD_VEL_THRESH_PARM_C              893      // (DEF,MnVel_TPARCD,16,NA)
#define MIN_UNLD_VEL_THRESH_PARM_P                1

#define RD_ZEDD_INITIAL_THRESH_PARM_C           894      // (DEF,ZddInitThrsh_TPARCD[1],16,NA)
#define RD_ZEDD_INITIAL_THRESH_PARM_P             1

#define RD_ZEDD_THRESH_RATIO_PARM_C             895      // (DEF,ZddThrshRatio_TPARCD[1],16,NA)
#define RD_ZEDD_THRESH_RATIO_PARM_P               1

// Deprecated 3/05/2009
#define MR_ON_THE_RAMP_PARM_C                   896      // (NA,NA,NA,NA)
#define MR_ON_THE_RAMP_PARM_P                     0

#define INJECTION_CURRENT_PARM_C                897      // (DEF,InjAmp_TPARCD,16,NA)
#define INJECTION_CURRENT_PARM_P                  1

#define DWELL_STEPS_PARM_C                      898      // (DEF,DwellEvntCnt_TPARCD,16,NA)
#define DWELL_STEPS_PARM_P                        1

#define QTY_RES_MEAS_PARM_C                     899      // (DEF,ResistMeasCnt_TPARCD,16,NA)
#define QTY_RES_MEAS_PARM_P                       1

#define DWELL_STEP_SEQUENCE_PARM_C              900      // (T334,Cword1,16,0x0001)
#define DWELL_STEP_SEQUENCE_PARM_P                1

#define LIMIT_BER_RW_PARM_C                     901      // (DEF,RwBerLmt_TPARCD,16,NA)
#define LIMIT_BER_RW_PARM_P                       1

#define LIMIT_BER_RWRO_PARM_C                   902      // (DEF,DltaBerLmt_TPARCD,16,NA)
#define LIMIT_BER_RWRO_PARM_P                     1

#define LIMIT_BER_RO_PARM_C                     903      // (DEF,RdBerLmt_TPARCD,16,NA)
#define LIMIT_BER_RO_PARM_P                       1

#define LIMIT_RES_PARM_C                        904      // (DEF,DltaResistLmt_TPARCD,16,NA)
#define LIMIT_RES_PARM_P                          1

#define NUM_TRACKS_BER_PARM_C                   905      // (NA,NA,NA,NA)
#define NUM_TRACKS_BER_PARM_P                     1

#define TRACK_STEP_SIZE_PARM_C                  906      // (DEF,TrkSpcg_TPARCD,16,NA)
#define TRACK_STEP_SIZE_PARM_P                    1

#define NUM_BITS_READ_PARM_C                    907      // (DEF,RdBitCnt_TPARCD,16,NA)  // 2nd word of legacy parameter is unused; dropped in UPS
#define NUM_BITS_READ_PARM_P                      2

#define DESPORT_SIGMA_PARM_C                    908      // (DEF,OutlrSgma_TPARCD,16,NA)
#define DESPORT_SIGMA_PARM_P                      1

#define NUM_WRITES_READS_PARM_C                 909      // (DEF,RwCnt_TPARCD,16,NA)
#define NUM_WRITES_READS_PARM_P                   1

#define DFCTS_PER_TRK_SKIP_TRK_SPEC_PARM_C      910      // (DEF,DfctPerTrkLmt_TPARCD,16,NA)
#define DFCTS_PER_TRK_SKIP_TRK_SPEC_PARM_P        2

#define ERRORS_TO_READ_PARM_C                   911      // (DEF,RdErrLmt_TPARCD,32,NA)
#define ERRORS_TO_READ_PARM_P                     1

#define SFIR_OFFSET_PARM_C                      912      // (NA,NA,NA,NA)      // Feature disabled in T109; parameter dropped in UPS
#define SFIR_OFFSET_PARM_P                        1

#define NLD_MODE_PARM_C                         913      // (NA,NA,NA,NA)
#define NLD_MODE_PARM_P                           1

#define NPT_INIT_REG_PARM_C                     914      // (NA,NA,NA,NA)
#define NPT_INIT_REG_PARM_P                       1

#define ASP_QUAL_PARM_C                         915      // (NA,NA,NA,NA)
#define ASP_QUAL_PARM_P                           2

#define AGC_RETRY_ZONES_PARM_C                  916      // (DEF,AgcRtryZnMsk_TPARCD,32,NA)
#define AGC_RETRY_ZONES_PARM_P                    2

#define PES_RETRY_ZONES_PARM_C                  917      // (DEF,PesRtryZnMsk_TPARCD,32,NA)
#define PES_RETRY_ZONES_PARM_P                    2

#define DYNAMIC_THRESH_BACKOFF_PARM_C           918      // (DEF,DynThrshBackOff_TPARCD,16,NA)
#define DYNAMIC_THRESH_BACKOFF_PARM_P             1

#define ZONE_ORDER_PARM_C                       919      // (Def,ZnOrdr_TPARCD,32,NA)
#define ZONE_ORDER_PARM_P                        32

#define FORWARD_PAD_SIZE_PARM_C                 920      // (NA,NA,NA,NA)
#define FORWARD_PAD_SIZE_PARM_P                   1

#define NUM_TRKS_AVERAGED_PARM_C                921      // (DEF,AvgTrkCnt_TPARCD,16,NA)
#define NUM_TRKS_AVERAGED_PARM_P                  1

#define TAG_SIGNATURE_PARM_C                    922      // (DEF,Key_TPARCD,16,NA)
#define TAG_SIGNATURE_PARM_P                      1

#define LO_RAMP_CONT_MINCYL_PARM_C              923      // (NA,NA,NA,NA)
#define LO_RAMP_CONT_MINCYL_PARM_P                2

#define LO_RAMP_CONT_MAXCYL_PARM_C              924      // (NA,NA,NA,NA)
#define LO_RAMP_CONT_MAXCYL_PARM_P                2

#define LO_RAMP_CONT_RANGE_PARM_C               925      // (T135,MxDacBtwnIPD_TPARCD,16,NA) Only 1 parameter
#define LO_RAMP_CONT_RANGE_PARM_P                 2

#define DELTA_LIMIT_32_PARM_C                   926      // (NA,NA,NA,NA)
#define DELTA_LIMIT_32_PARM_P                     2

#define MAX_RAP_HEAT_PARM_C                     927      // (Def,MxRapHt_TPARCD,16,NA)
#define MAX_RAP_HEAT_PARM_P                       3

#define TRIP_LEVEL_PARM_C                       928      // (NA,NA,NA,NA)
#define TRIP_LEVEL_PARM_P                         2

#define DC_OFFSET_RANGE_LIMIT_PARM_C            929      // (NA,NA,NA,NA)
#define DC_OFFSET_RANGE_LIMIT_PARM_P              2

#define TEST_METHOD_PARM_C                      930      // (NA,NA,NA,NA)
#define TEST_METHOD_PARM_P                       10

#define DICE_FEATURES_PARM_C                    931      // (NA,NA,NA,NA)
#define DICE_FEATURES_PARM_P                      1

#define RMS_ERROR_LIMIT_PARM_C                  932      // (DEF,RmsErrLmt_TPARCD,16,NA)
#define RMS_ERROR_LIMIT_PARM_P                    1

#define HEATER_TEST_MODE_PARM_C                 933      // (DEF,HtrMode_TPARCD,16,NA)
#define HEATER_TEST_MODE_PARM_P                   1

#define POLYFIT_RMS_LIMIT_PARM_C                934      // (DEF,PolyFit_TPARCD,16,NA)
#define POLYFIT_RMS_LIMIT_PARM_P                  2

#define POLYFIT_OUTLIER_LIMITS_PARM_C           935      // (DEF,OutlrLmt_TPARCD,8,NA)
#define POLYFIT_OUTLIER_LIMITS_PARM_P             2

#define BPI_GROUP_EXT_PARM_C                    936      // (NA,NA,NA,NA)
#define BPI_GROUP_EXT_PARM_P                     16

#define TPI_GROUP_EXT_PARM_C                    937      // (NA,NA,NA,NA)
#define TPI_GROUP_EXT_PARM_P                     16

#define APERIO_FLAW_00_PARM_C                   938      // (DEF,AperioFlaw00_TPARCD,16,NA)
#define APERIO_FLAW_00_PARM_P                     5

#define APERIO_FLAW_01_PARM_C                   939      // (DEF,AperioFlaw01_TPARCD,16,NA)
#define APERIO_FLAW_01_PARM_P                     5

#define APERIO_FLAW_02_PARM_C                   940      // (DEF,AperioFlaw02_TPARCD,16,NA)
#define APERIO_FLAW_02_PARM_P                     5

#define APERIO_FLAW_03_PARM_C                   941      // (DEF,AperioFlaw03_TPARCD,16,NA)
#define APERIO_FLAW_03_PARM_P                     5

#define APERIO_FLAW_04_PARM_C                   942      // (DEF,AperioFlaw04_TPARCD,16,NA)
#define APERIO_FLAW_04_PARM_P                     5

#define APERIO_FLAW_05_PARM_C                   943      // (DEF,AperioFlaw05_TPARCD,16,NA)
#define APERIO_FLAW_05_PARM_P                     5

#define APERIO_FLAW_06_PARM_C                   944      // (DEF,AperioFlaw06_TPARCD,16,NA)
#define APERIO_FLAW_06_PARM_P                     5

#define APERIO_FLAW_07_PARM_C                   945      // (DEF,AperioFlaw07_TPARCD,16,NA)
#define APERIO_FLAW_07_PARM_P                     5

#define APERIO_FLAW_08_PARM_C                   946      // (DEF,AperioFlaw08_TPARCD,16,NA)
#define APERIO_FLAW_08_PARM_P                     5

#define APERIO_FLAW_09_PARM_C                   947      // (DEF,AperioFlaw09_TPARCD,16,NA)
#define APERIO_FLAW_09_PARM_P                     5

#define APERIO_FLAW_10_PARM_C                   948      // (DEF,AperioFlaw10_TPARCD,16,NA)
#define APERIO_FLAW_10_PARM_P                     5

#define APERIO_FLAW_11_PARM_C                   949      // (DEF,AperioFlaw11_TPARCD,16,NA)
#define APERIO_FLAW_11_PARM_P                     5

#define APERIO_FLAW_12_PARM_C                   950      // (DEF,AperioFlaw12_TPARCD,16,NA)
#define APERIO_FLAW_12_PARM_P                     5

#define APERIO_FLAW_13_PARM_C                   951      // (DEF,AperioFlaw13_TPARCD,16,NA)
#define APERIO_FLAW_13_PARM_P                     5

#define APERIO_FLAW_14_PARM_C                   952      // (DEF,AperioFlaw14_TPARCD,16,NA)
#define APERIO_FLAW_14_PARM_P                     5

#define APERIO_FEED_STATUS_PARM_C               953      // (DEF,AperioStat_TPARCD,16,NA)
#define APERIO_FEED_STATUS_PARM_P                 1

#define RW_OPTIONS_PARM_C                       954      // (T68,RwOptn_TPARCD,32,NA)
#define RW_OPTIONS_PARM_P                         4

#define CLEARANCE_CONSISTENCY_LIMIT_PARM_C      955      // (T135,ClrncVfyLmt_TPARCD,16,NA))
#define CLEARANCE_CONSISTENCY_LIMIT_PARM_P        3

#define RZAP_MABS_EZBZ_RRO_LIMIT_PARM_C         956      // (NA,NA,NA,NA)
#define RZAP_MABS_EZBZ_RRO_LIMIT_PARM_P           1

#define REG_TO_OPT13_PARM_C                     957      // (DEF,OptReg13_TPARCD,16,NA)
#define REG_TO_OPT13_PARM_P                       4

#define REG_TO_OPT13_EXT_PARM_C                 958      // (DEF,OptRegExt13_TPARCD,16,NA)
#define REG_TO_OPT13_EXT_PARM_P                   3

#define REG_TO_OPT14_PARM_C                     959      // (DEF,OptReg14_TPARCD,16,NA)
#define REG_TO_OPT14_PARM_P                       4

#define REG_TO_OPT14_EXT_PARM_C                 960      // (DEF,OptRegExt14_TPARCD,16,NA)
#define REG_TO_OPT14_EXT_PARM_P                   3

#define REG_TO_OPT15_PARM_C                     961      // (DEF,OptReg15_TPARCD,16,NA)
#define REG_TO_OPT15_PARM_P                       4

#define REG_TO_OPT15_EXT_PARM_C                 962      // (DEF,OptRegExt15_TPARCD,16,NA)
#define REG_TO_OPT15_EXT_PARM_P                   3

#define REG_TO_OPT16_PARM_C                     963      // (DEF,OptReg16_TPARCD,16,NA)
#define REG_TO_OPT16_PARM_P                       4

#define REG_TO_OPT16_EXT_PARM_C                 964      // (DEF,OptRegExt16_TPARCD,16,NA)
#define REG_TO_OPT16_EXT_PARM_P                   3

#define REG_TO_OPT17_PARM_C                     965      // (DEF,OptReg17_TPARCD,16,NA)
#define REG_TO_OPT17_PARM_P                       4

#define REG_TO_OPT17_EXT_PARM_C                 966      // (DEF,OptRegExt17_TPARCD,16,NA)
#define REG_TO_OPT17_EXT_PARM_P                   3

#define REG_TO_OPT18_PARM_C                     967      // (DEF,OptReg18_TPARCD,16,NA)
#define REG_TO_OPT18_PARM_P                       4

#define REG_TO_OPT18_EXT_PARM_C                 968      // (DEF,OptRegExt18_TPARCD,16,NA)
#define REG_TO_OPT18_EXT_PARM_P                   3

#define NUM_LBAS_HI_PARM_C                      969      // (DEF,LbaCnt_TPARCD[0],32,NA)
#define NUM_LBAS_HI_PARM_P                        2

#define CURVE_FIT2_PARM_C                       970      // (T135,Fit_TPARCD,16,NA))
#define CURVE_FIT2_PARM_P                         8

#define MIN_CONTACT_BACKOFF_PARM_C              971      // (DEF,MnCntctBckOff_TPARCD,8,NA)
#define MIN_CONTACT_BACKOFF_PARM_P                1

#define AFH_GAMMA_BY_ZONE_PARM_C                972      // (DEF,GammaZn_TPARCD,16,NA)
#define AFH_GAMMA_BY_ZONE_PARM_P                 10

#define DETECTOR_BIT_MASK_PARM_C                973      // (NA,NA,NA,NA)
#define DETECTOR_BIT_MASK_PARM_P                12

#define INTERNAL_MODEL_NUM_PARM_C               974      // (NA,NA,NA,NA)
#define INTERNAL_MODEL_NUM_PARM_P                20

#define EXTERNAL_MODEL_NUM_PARM_C               975      // (NA,NA,NA,NA)
#define EXTERNAL_MODEL_NUM_PARM_P                20

#define AFH_GAMMA_W_PARM_C                      976      // (NA,NA,NA,NA)
#define AFH_GAMMA_W_PARM_P                        6

#define WIRP_POINT_COUNT_PARM_C                 977      // (NA,NA,NA,NA)
#define WIRP_POINT_COUNT_PARM_P                   1

#define HTR_PERCENT_LIMIT_PARM_C                978      // (DEF,HtrPrctLmt_TPARCD,16,NA)
#define HTR_PERCENT_LIMIT_PARM_P                  2

#define FREQ_OPTIONS_PARM_C                     979      // (NA,NA,NA,NA)
#define FREQ_OPTIONS_PARM_P                       1

#define FREQ_START_PARM_C                       980      // (NA,NA,NA,NA)
#define FREQ_START_PARM_P                         2

#define FREQ_STOP_PARM_C                        981      // (NA,NA,NA,NA)
#define FREQ_STOP_PARM_P                          2

#define FREQ_STEP_PARM_C                        982      // (NA,NA,NA,NA)
#define FREQ_STEP_PARM_P                          2

#define FREQ_COUNT_PARM_C                       983      // (NA,NA,NA,NA)
#define FREQ_COUNT_PARM_P                         1

#define SAMPLES_COUNT_TYPE_PARM_C               984      // (NA,NA,NA,NA)
#define SAMPLES_COUNT_TYPE_PARM_P                 1

#define FREQ_ARRAY_PARM_C                       985      // (NA,NA,NA,NA)
#define FREQ_ARRAY_PARM_P                        20

#define COUNT_ARRAY_PARM_C                      986      // (NA,NA,NA,NA)
#define COUNT_ARRAY_PARM_P                       10

#define AMPLITUDE1_ARRAY_PARM_C                 987      // (NA,NA,NA,NA)
#define AMPLITUDE1_ARRAY_PARM_P                  10

#define AMPLITUDE2_ARRAY_PARM_C                 988      // (NA,NA,NA,NA)
#define AMPLITUDE2_ARRAY_PARM_P                  10

#define HEAD_MASK_PARM_C                        989      // (NA,NA,NA,NA)
#define HEAD_MASK_PARM_P                          1

#define TRACK_OPTIONS_PARM_C                    990      // (NA,NA,NA,NA)
#define TRACK_OPTIONS_PARM_P                      1

#define STEP_CYL_PARM_C                         991      // (NA,NA,NA,NA)
#define STEP_CYL_PARM_P                           2

#define RV_LIMIT_PARM_C                         992      // (DEF,RvLmt_TPARCD,16,NA)
#define RV_LIMIT_PARM_P                           1

#define RV_DELAY_LIMIT_PARM_C                   993      // (DEF,RvDlyLmt_TPARCD,16,NA)
#define RV_DELAY_LIMIT_PARM_P                     1

#define RV_THRESHOLD_PARM_C                     994      // (DEF,RvThrsh_TPARCD,8,NA)
#define RV_THRESHOLD_PARM_P                       1

#define BIT_MASK_EXT_PARM_C                     995      // (DEF,BitMskExtd_TPARCD,32,NA) (T75,ZnMskExtd_TPARCD,32,NA) (T135,ZnMskExtd_TPARCD,32,NA) (T210,ZnMskExtd_TPARCD,32,NA) (T251,ZnMskExtd_TPARCD,32,NA)
#define BIT_MASK_EXT_PARM_P                       2

#define ZONE_MASK_EXT_PARM_C                    996      // (DEF,ZnMskExtd_TPARCD,32,NA)
#define ZONE_MASK_EXT_PARM_P                      2

#define INDIVIDUAL_OFFSET_EXT_PARM_C            997      // (DEF,IndvdlOfst_TPARCD,8,NA)
#define INDIVIDUAL_OFFSET_EXT_PARM_P             20

#define ZONE_SKIP_MASK_EXT_PARM_C               998      // (DEF,ZnSkpMskExtd_TPARCD,32,NA)
#define ZONE_SKIP_MASK_EXT_PARM_P                 2

#define REVS_BY_ZONE_EXT_PARM_C                 999      // (DEF,RvsPerZn_TPARCD,16,NA)
#define REVS_BY_ZONE_EXT_PARM_P                   3

#define ZONE_ORDER_EXT_PARM_C                  1000      // (DEF,ZnOrdr_TPARCD,8,NA)
#define ZONE_ORDER_EXT_PARM_P                     3

#define AGC_RETRY_ZONES_EXT_PARM_C             1001      // (DEF,AgcRtryZnMskExtd_TPARCD,32,NA)
#define AGC_RETRY_ZONES_EXT_PARM_P                2

#define PES_RETRY_ZONES_EXT_PARM_C             1002      // (DEF,PesRtryZnMskExtd_TPARCD,32,NA)
#define PES_RETRY_ZONES_EXT_PARM_P                2

#define HIRP_CURVE_FIT_PARM_C                  1003      // (NA,NA,NA,NA)
#define HIRP_CURVE_FIT_PARM_P                    10

#define COARSE_CONFIRM_INTERFERENCE_PARM_C     1004      // (NA,NA,NA,NA)
#define COARSE_CONFIRM_INTERFERENCE_PARM_P        1

#define START_TLBA_PARM_C                      1005      // (NA,NA,NA,NA)
#define START_TLBA_PARM_P                         4

#define END_TLBA_PARM_C                        1006      // (NA,NA,NA,NA)
#define END_TLBA_PARM_P                           4

#define M7_FREQ_RANGE_PARM_C                   1007      // (DEF,MFrqRg6_TPARCD,16,NA)
#define M7_FREQ_RANGE_PARM_P                      2

#define M8_FREQ_RANGE_PARM_C                   1008      // (DEF,MFrqRg6_TPARCD,16,NA)
#define M8_FREQ_RANGE_PARM_P                      2

#define M7_M8_AMP_LIMIT_PARM_C                 1009      // (DEF,AmpLmt_TPARCD[7-8],16,NA)
#define M7_M8_AMP_LIMIT_PARM_P                    2

#define DISCARD_LIMITS_PARM_C                  1010      // (NA,NA,NA,NA)
#define DISCARD_LIMITS_PARM_P                     2

#define MIN_DELTA_PARM_C                       1011      // (DEF,MnDlta_TPARCD,16,NA)
#define MIN_DELTA_PARM_P                          1

#define HMS_STEP_PARM_C                        1012      // (NA,NA,NA,NA)
#define HMS_STEP_PARM_P                           1

#define HMS_MAX_PUSH_RELAX_PARM_C              1013      // (NA,NA,NA,NA)
#define HMS_MAX_PUSH_RELAX_PARM_P                 1

#define BASELINE_CLEANUP_WRT_RETRY_PARM_C      1014      // (NA,NA,NA,NA)
#define BASELINE_CLEANUP_WRT_RETRY_PARM_P         1

#define CHANGE_SEEK_LENGTH_AND_RETRY_PARM_C    1015      // (NA,NA,NA,NA)
#define CHANGE_SEEK_LENGTH_AND_RETRY_PARM_P       1

#define RESIDUAL_STD_DEV_LIMIT_PARM_C          1016
#define RESIDUAL_STD_DEV_LIMIT_PARM_P             2

#define OSA_MIN_PARM_C                         1017      // (DEF,OsaMnBckOff_TPARCD,16,NA)
#define OSA_MIN_PARM_P                            1

#define TARGET_NORM_3RD_HARM_AMPL_PARM_C       1018
#define TARGET_NORM_3RD_HARM_AMPL_PARM_P          1

#define DFS_DATA_DEFECT_PAD_PARM_C             1019
#define DFS_DATA_DEFECT_PAD_PARM_P                2

#define MAX_HD_LD_TIME_LIMIT_PARM_C            1020      // (DEF,MxHdLdTmLmt_TPARCD,16,NA)
#define MAX_HD_LD_TIME_LIMIT_PARM_P               1

#define MAX_SFLAWS_PER_SURFACE_PARM_C          1021      // (DEF,MxSurfSflwCnt_TPARCD,16,NA)
#define MAX_SFLAWS_PER_SURFACE_PARM_P             1

#define MINIMUM_PEAK_SPACING_SNO_BY_ZONE_PARM_C         1022
#define MINIMUM_PEAK_SPACING_SNO_BY_ZONE_PARM_P            1

#define DUAL_HEATER_CONTROL_PARM_C             1023
#define DUAL_HEATER_CONTROL_PARM_P                2

#define VER_HD_ZONE_LIMIT_PARM_C               1024
#define VER_HD_ZONE_LIMIT_PARM_P                  2

#define MIN_REVS_PARM_C                        1025     // (DEF,Rvs_TPARCD,16,NA)
#define MIN_REVS_PARM_P                           1

#define ZONE_DAC_DELTA_PARM_C                  1026     // (NA,NA,NA,NA)
#define ZONE_DAC_DELTA_PARM_P                     2

#define SID_QM_THRESH_PARM_C                   1027
#define SID_QM_THRESH_PARM_P                      4

#define SID_QM_CONTROL_PARM_C                  1028
#define SID_QM_CONTROL_PARM_P                     4

#define PRETHRESH_MIN_PARM_C                  1029
#define PRETHRESH_MIN_PARM_P                     1

#define PRETHRESH_MAX_PARM_C                  1030
#define PRETHRESH_MAX_PARM_P                     1

#define PRETHRESH_S2T_PARM_C                  1031
#define PRETHRESH_S2T_PARM_P                     1

#define ACQFLAW_MIN_PARM_C                    1032
#define ACQFLAW_MIN_PARM_P                       1

#define ACQFLAW_MAX_PARM_C                    1033
#define ACQFLAW_MAX_PARM_P                       1

#define LIMIT_S2T_PARM_C                      1034
#define LIMIT_S2T_PARM_P                         1

#define AFH_GAMMA_R_PARM_C                     1035
#define AFH_GAMMA_R_PARM_P                        6

#define C_ARRAY1_PARM_C                        1036
#define C_ARRAY1_PARM_P                          10

#define CUT_OFF_FRQ_PARM_C                     1037     // (DEF,CutOffFrq_TPARCD,float,NA)
#define CUT_OFF_FRQ_PARM_P                        5

#define MAX_ITER_PARM_C                        1038     // (DEF,MxItr_TPARCD,16,NA)
#define MAX_ITER_PARM_P                           5

#define MEAS_REP_CNT_PARM_C                    1039     // (DEF,MeasRepCnt_TPARCD,16,NA)
#define MEAS_REP_CNT_PARM_P                       5

#define VELOCITY_PARM_C                        1040     // (DEF,Vel_TPARCD,float,NA)
#define VELOCITY_PARM_P                           5

#define CWORD5_PARM_C                          1041      // (DEF,Cwrd5_TPARCD,16,NA)
#define CWORD5_PARM_P                             1

#define FREQ_LIMIT_PARM_C                      1042      // (DEF,FrqLmt_TPARCD,16,NA)
#define FREQ_LIMIT_PARM_P                         2

#define NUM_ITER_READS_PARM_C                  1043
#define NUM_ITER_READS_PARM_P                     1

#define JOG_ERR_THRSH_PARM_C                   1044      // (DEF,JogErrThrsh_TPARCD,16,NA)
#define JOG_ERR_THRSH_PARM_P                      1

#define SQZ_THRSH_PARM_C                       1045      // (DEF,SqzThrsh_TPARCD,16,NA)
#define SQZ_THRSH_PARM_P                          1

#define WINDOW_LAG_PARM_C                      1046     // (DEF, Wdw_TPARCD[1],16,NA)
#define WINDOW_LAG_PARM_P                         1

#define ISLAND_WEDGES_PARM_C                   1047
#define ISLAND_WEDGES_PARM_P                      4

#define RADIAL_TA_NUM_FOR_FRONT_PAD_PARM_C     1048
#define RADIAL_TA_NUM_FOR_FRONT_PAD_PARM_P        1

#define RADIAL_SPN_TA_PREPEND_TRIPAD_PARM_C    1049
#define RADIAL_SPN_TA_PREPEND_TRIPAD_PARM_P       1

#define PZT_BUZZ_TRACK_INTERVAL_PARM_C         1050   // Track interval for performing a PZT element buzz. User must furnish nonzero value to enable PZT buzz in zap
#define PZT_BUZZ_TRACK_INTERVAL_PARM_P            1

#define SM_SGRG_PATCHDLY_PARM_C                1051
#define SM_SGRG_PATCHDLY_PARM_P                   1

#define SM_RG_LENGTHADJUST_PARM_C              1052
#define SM_RG_LENGTHADJUST_PARM_P                 1

#define RRO_AVGS_PARM_C                        1053
#define RRO_AVGS_PARM_P                           3

#define PARAM_10_14_PARM_C                     1054
#define PARAM_10_14_PARM_P                        5

#define PARAM_15_19_PARM_C                     1055
#define PARAM_15_19_PARM_P                        5

#define PARAM_20_24_PARM_C                     1056
#define PARAM_20_24_PARM_P                        5

#define PARAM_25_29_PARM_C                     1057
#define PARAM_25_29_PARM_P                        5

#define PARAM_30_34_PARM_C                     1058
#define PARAM_30_34_PARM_P                        5

#define SERVO_ADDRESSES_PARM_C                 1059
#define SERVO_ADDRESSES_PARM_P                    8

#define SERVO_SHIFTS_PARM_C                    1060
#define SERVO_SHIFTS_PARM_P                       4

#define SERVO_SYMTAB_INDEXES_PARM_C            1061
#define SERVO_SYMTAB_INDEXES_PARM_P               4

#define SM_WG_LENGTHADJUST_PARM_C              1062
#define SM_WG_LENGTHADJUST_PARM_P                 1

#define UPDATE_REG_PARM_C                      1063
#define UPDATE_REG_PARM_P                         2

#define TARGET_BER_PARM_C                      1064
#define TARGET_BER_PARM_P                         1

#define DFS_TRACK_EXAM_PARM_C                  1065
#define DFS_TRACK_EXAM_PARM_P                     2

#define REF_ADC_PARM_C                         1066
#define REF_ADC_PARM_P                            1

#define PREAMBLE_LMTS_PARM_C                   1067
#define PREAMBLE_LMTS_PARM_P                      2

#define MDW_CERT_TRKS_PARM_C                   1068
#define MDW_CERT_TRKS_PARM_P                      6

#define TPI_TLEVEL_PARM_C                      1069
#define TPI_TLEVEL_PARM_P                         1

#define TPI_TARGET_SER_PARM_C                  1070
#define TPI_TARGET_SER_PARM_P                     1

#define CLEARANCE_CONSISTENCY_LIMIT_DH_PARM_C  1071      // t135 cross-heater consistency check
#define CLEARANCE_CONSISTENCY_LIMIT_DH_PARM_P     4

#define PARTICLE_SWEEP_MODE_PARM_C             1072
#define PARTICLE_SWEEP_MODE_PARM_P                1

#define TRIGGER_CHANNEL_PARM_C                 1073
#define TRIGGER_CHANNEL_PARM_P                    2

#define TRIGGER_THRESHOLD_PARM_C               1074
#define TRIGGER_THRESHOLD_PARM_P                  2

#define TRIGGER_FILTER_DEPTH_PARM_C            1075
#define TRIGGER_FILTER_DEPTH_PARM_P               1

#define DETECTOR_BIT_MASK_EXT_PARM_C           1076
#define DETECTOR_BIT_MASK_EXT_PARM_P             12

#define SHORT_REVS_BY_ZONE_PARM_C              1077
#define SHORT_REVS_BY_ZONE_PARM_P                18

#define SHORT_ZONE_ORDER_PARM_C                1078
#define SHORT_ZONE_ORDER_PARM_P                  18

#define GEN_PC_FILES_PARM_C                    1079
#define GEN_PC_FILES_PARM_P                       1

#define MULT_MAG_PARM_C                        1080
#define MULT_MAG_PARM_P                           2

#define RRO_AMPL_LIMIT_PARM_C                  1081
#define RRO_AMPL_LIMIT_PARM_P                     7

#define INTEGRATION_LIMITS_PARM_C              1082
#define INTEGRATION_LIMITS_PARM_P                 2

#define MAX_NUM_DWELL_STEPS_PARM_C             1083      // (T334,MxDwellStepCnt_TPARCD,16,NA))
#define MAX_NUM_DWELL_STEPS_PARM_P                1

#define PSC_COEFF_PARM_C                       1084
#define PSC_COEFF_PARM_P                          3

#define DEF_PSC_CLR_ADJ_PARM_C                 1085
#define DEF_PSC_CLR_ADJ_PARM_P                    1

#define M7_M8_RRO_AMPL_LIMIT_PARM_C            1086
#define M7_M8_RRO_AMPL_LIMIT_PARM_P               2

#define HMS_START_PARM_C                       1087      // (NA,NA,NA,NA)
#define HMS_START_PARM_P                          1

#define CLRNC_DELTA_PARM_C                     1088
#define CLRNC_DELTA_PARM_P                        2

#define WRT_ER_DELTA_THRESHOLD_PARM_C          1089
#define WRT_ER_DELTA_THRESHOLD_PARM_P             1

#define RD_ER_DELTA_THRESHOLD_PARM_C           1090
#define RD_ER_DELTA_THRESHOLD_PARM_P              1

#define WRT_ER_THRESHOLD_PARM_C                1091
#define WRT_ER_THRESHOLD_PARM_P                   1

#define RD_ER_THRESHOLD_PARM_C                 1092
#define RD_ER_THRESHOLD_PARM_P                    1

#define DEGAUSS_ON_ERR_LIM_SER_PARM_C          1093
#define DEGAUSS_ON_ERR_LIM_SER_PARM_P             1

#define DEGAUSS_OFF_ERR_LIM_SER_PARM_C         1094
#define DEGAUSS_OFF_ERR_LIM_SER_PARM_P            1

#define DELTA_LIMIT_SER_PARM_C                 1095
#define DELTA_LIMIT_SER_PARM_P                    1

#define MAX_DVGA_ERR_CNT_PARM_C                1096
#define MAX_DVGA_ERR_CNT_PARM_P                   1

#define MAX_RVGA_ERR_CNT_PARM_C                1097
#define MAX_RVGA_ERR_CNT_PARM_P                   1

#define MAX_FVGA_ERR_CNT_PARM_C                1098
#define MAX_FVGA_ERR_CNT_PARM_P                   1

#define VGAS_DIFF_LIMIT_PARM_C                 1099
#define VGAS_DIFF_LIMIT_PARM_P                    1

#define NUM_WRITES_32BIT_PARM_C                1100
#define NUM_WRITES_32BIT_PARM_P                   2

#define BER_PENALTY_PARM_C                     1101
#define BER_PENALTY_PARM_P                        4

#define SUM_OF_SLOPES_LIMIT_PARM_C             1102
#define SUM_OF_SLOPES_LIMIT_PARM_P                1

#define VGAR_TOLERANCE_PARM_C                  1103
#define VGAR_TOLERANCE_PARM_P                     1

#define VGAS_GUARDBAND_PARM_C                  1104
#define VGAS_GUARDBAND_PARM_P                     1

#define MAX_UNSAFES_PARM_C                     1105         // (T126,UnsfLmt_TPARCD,16,NA)
#define MAX_UNSAFES_PARM_P                        6

#define MIN_ALTITUDE_ADJ_PARM_C                1106
#define MIN_ALTITUDE_ADJ_PARM_P                   1

#define MAX_ALTITUDE_ADJ_PARM_C                1107
#define MAX_ALTITUDE_ADJ_PARM_P                   1

#define CMBN_ER_DELTA_THRESHOLD_PARM_C         1108         // (T88,ErrDltaThrsh_TPARCD,float,NA)
#define CMBN_ER_DELTA_THRESHOLD_PARM_P            1

#define CMBN_ER_THRESHOLD_PARM_C               1109         // (T88,ErrThrsh_TPARCD,float,NA)
#define CMBN_ER_THRESHOLD_PARM_P                  1

#define TRK_PITCH_TBL_PARM_C                   1110      // (DEF,TrkPitch_TPARCD,16,NA)
#define TRK_PITCH_TBL_PARM_P                     16

#define TRK_GUARD_TBL_PARM_C                   1111      // (DEF,TrkGuard_TPARCD,16,NA)
#define TRK_GUARD_TBL_PARM_P                     16

#define WRT_FAULT_THRESHOLD_TBL_PARM_C         1112      // (DEF,WrtFltThresh_TPARCD,16,NA)
#define WRT_FAULT_THRESHOLD_TBL_PARM_P           16

#define SHINGLED_DIRECTION_PARM_C              1113      // (DEF,ShingleDir_TPARCD,8,NA)
#define SHINGLED_DIRECTION_PARM_P                16

#define ZAP_SPAN_PARM_C                        1114         // T275
#define ZAP_SPAN_PARM_P                           1         // T275

#define MICROJOG_SQUEEZE_PARM_C                1115      // (DEF,MicrojogSqz_TPARCD,8,NA)
#define MICROJOG_SQUEEZE_PARM_P                  16

#define SMOOTH_SWD_VALS_PARM_C                 1116
#define SMOOTH_SWD_VALS_PARM_P                    3

#define BAND_OFFSET_PARM_C                     1117      //
#define BAND_OFFSET_PARM_P                        1

#define IFEST_PARMS_1_PARM_C                   1118      //
#define IFEST_PARMS_1_PARM_P                      4

#define IFEST_PARMS_2_PARM_C                   1119      //
#define IFEST_PARMS_2_PARM_P                      4

#define IFEST_PARMS_3_PARM_C                   1120      //
#define IFEST_PARMS_3_PARM_P                      4

#define IFEST_PARMS_4_PARM_C                   1121      //
#define IFEST_PARMS_4_PARM_P                      4

#define PPID_IN_MIF_PARM_C                     1122
#define PPID_IN_MIF_PARM_P                        3

#define TAP1S_RANGE_PARM_C                     1123
#define TAP1S_RANGE_PARM_P                        1

#define TAP2S_RANGE_PARM_C                     1124
#define TAP2S_RANGE_PARM_P                        1

#define CONFIDENCE_PARM_C                      1125
#define CONFIDENCE_PARM_P                         1

#define MR_OP_MODE_PARM_C                      1126
#define MR_OP_MODE_PARM_P                         1

#define RESISTANCE_RANGE_PARM_C                1127
#define RESISTANCE_RANGE_PARM_P                   2

#define MAX_POWER_PARM_C                       1128
#define MAX_POWER_PARM_P                          1

#define MAX_VOLTAGE_PARM_C                     1129
#define MAX_VOLTAGE_PARM_P                        1

#define BACKOFF_HTR_DAC_PARM_C                 1130      // (DEF,BackoffHTRDAC_TPARCD,16,NA)
#define BACKOFF_HTR_DAC_PARM_P                    1

#define PI_BYTE_PARM_C                         1131     //  (DEF,PiBytSz_TPARCD,16,NA)
#define PI_BYTE_PARM_P                            1

#define PERCENT_SECTOR_OVRHD_PARM_C            1132
#define PERCENT_SECTOR_OVRHD_PARM_P               1

#define SECTOR_SIZE_ARRAY_PARM_C               1133
#define SECTOR_SIZE_ARRAY_PARM_P                 10

#define RGN_PREAMBLE_LIMITS_PARM_C             1134
#define RGN_PREAMBLE_LIMITS_PARM_P                6

#define DETCR_CD_PARM_C                        1135     // (NA,NA,NA,NA)
#define DETCR_CD_PARM_P                          10     // (default setting and max for bias, threld and gian,  ctrl1, ctrl2 ,ctrl3, IPD2 bit mask, DETCR bit mask

#define DEFECT_LENGTH2_PARM_C                  1136
#define DEFECT_LENGTH2_PARM_P                     1

#define THRESHOLD3_PARM_C                      1137
#define THRESHOLD3_PARM_P                         1

#define THRESHOLD4_PARM_C                      1138
#define THRESHOLD4_PARM_P                         1

#define MIXEDRATIO_COEF_PARM_C                 1139
#define MIXEDRATIO_COEF_PARM_P                    2

#define RELHUMIDITY_COEF_PARM_C                1140
#define RELHUMIDITY_COEF_PARM_P                   2

#define HUMIDITY_COEF_PARM_C                   1141
#define HUMIDITY_COEF_PARM_P                      1

#define PRE_DWELL_CLEARANCE_PARM_C             1142
#define PRE_DWELL_CLEARANCE_PARM_P                3

#define POST_DWELL_CLEARANCE_PARM_C            1143
#define POST_DWELL_CLEARANCE_PARM_P               3

#define PRE_DWELL_TEST_LOOP_PARM_C             1144
#define PRE_DWELL_TEST_LOOP_PARM_P                1

#define POST_DWELL_TEST_LOOP_PARM_C            1145
#define POST_DWELL_TEST_LOOP_PARM_P               1

#define MAX_SPARES_PARM_C                      1146
#define MAX_SPARES_PARM_P                         1

#define MAX_BPI_STEPS_PARM_C                   1147
#define MAX_BPI_STEPS_PARM_P                      1

#define ERR_RATE_DEGRADATION_PARM_C            1148
#define ERR_RATE_DEGRADATION_PARM_P               1

#define AVAILABLE_SPARES_PARM_C                1149     // (T530,MnAvailSprs_TPARCD,32,NA)
#define AVAILABLE_SPARES_PARM_P                   2

#define TCS_ADDER_PARM_C                       1150
#define TCS_ADDER_PARM_P                          2

#define PERF_ZONE_PARM_C                       1151
#define PERF_ZONE_PARM_P                          2

#define TRACKS_PER_BAND_PARM_C                 1152
#define TRACKS_PER_BAND_PARM_P                   16

#define CLEARANCE_OFFSET_PARM_C                1153
#define CLEARANCE_OFFSET_PARM_P                   1

#define TRISE_MIN_PARM_C                       1154
#define TRISE_MIN_PARM_P                          1

#define TRISE_MAX_PARM_C                       1155
#define TRISE_MAX_PARM_P                          1

#define TRISE_STEP_PARM_C                      1156
#define TRISE_STEP_PARM_P                         1

#define PRECMP_MIN_PARM_C                      1157
#define PRECMP_MIN_PARM_P                         1

#define PRECMP_MAX_PARM_C                      1158
#define PRECMP_MAX_PARM_P                         1

#define PRECMP_STEP_PARM_C                     1159
#define PRECMP_STEP_PARM_P                        1

#define IW_MIN_PARM_C                          1160
#define IW_MIN_PARM_P                             1

#define IW_MAX_PARM_C                          1161
#define IW_MAX_PARM_P                             1

#define IW_STEP_PARM_C                         1162
#define IW_STEP_PARM_P                            1

#define OS_MIN_PARM_C                          1163
#define OS_MIN_PARM_P                             1

#define OS_MAX_PARM_C                          1164
#define OS_MAX_PARM_P                             1

#define OS_STEP_PARM_C                         1165
#define OS_STEP_PARM_P                            1

#define OSD_MIN_PARM_C                         1166
#define OSD_MIN_PARM_P                            1

#define OSD_MAX_PARM_C                         1167
#define OSD_MAX_PARM_P                            1

#define OSD_STEP_PARM_C                        1168
#define OSD_STEP_PARM_P                           1

#define PICK_METHOD_PARM_C                     1169
#define PICK_METHOD_PARM_P                        1

#define ITERATION_LOAD_COUNT_PARM_C            1170
#define ITERATION_LOAD_COUNT_PARM_P               1

#define LBA_OD_MD_ID_POSITION_PARM_C           1171
#define LBA_OD_MD_ID_POSITION_PARM_P              3

#define ASYMMETRIC_SQZ_OFFSET_PARM_C           1172
#define ASYMMETRIC_SQZ_OFFSET_PARM_P              2

#define ASYMMETRIC_SQZ_WRT_CNT_PARM_C          1173
#define ASYMMETRIC_SQZ_WRT_CNT_PARM_P             2

#define NRAGC_AMPL_LIMIT_PARM_C                1174
#define NRAGC_AMPL_LIMIT_PARM_P                   7

#define M7_M8_NRAGC_AMP_LIMIT_PARM_C           1175
#define M7_M8_NRAGC_AMP_LIMIT_PARM_P              2

#define RAGC_AMPL_LIMIT_PARM_C                 1176
#define RAGC_AMPL_LIMIT_PARM_P                    7

#define M7_M8_RAGC_AMP_LIMIT_PARM_C            1177
#define M7_M8_RAGC_AMP_LIMIT_PARM_P               2

#define DETECTOR_ZONE_RANGE_PARM_C             1178
#define DETECTOR_ZONE_RANGE_PARM_P                6

#define AGC_MINMAX_DELTA_PARM_C                1179
#define AGC_MINMAX_DELTA_PARM_P                   1

#define AGC_TRACK_SPAN_PARM_C                  1180
#define AGC_TRACK_SPAN_PARM_P                     1

#define T_RISE_PARM_C                          1181
#define T_RISE_PARM_P                             1

#define WRITE_CUR_LIST_PARM_C                  1182
#define WRITE_CUR_LIST_PARM_P                     4

#define WRITE_DUMP_LIST_PARM_C                 1183
#define WRITE_DUMP_LIST_PARM_P                    4

#define WRITE_DUMPDUR_LIST_PARM_C              1184
#define WRITE_DUMPDUR_LIST_PARM_P                 4

#define TIMING_PARM_C                          1185
#define TIMING_PARM_P                             4

#define TARGET_COEF_PARM_C                     1186
#define TARGET_COEF_PARM_P                        1

#define POS_THRES_OPTI_CRITERIA_PARM_C         1187
#define POS_THRES_OPTI_CRITERIA_PARM_P            3

#define NEG_THRES_OPTI_CRITERIA_PARM_C         1188
#define NEG_THRES_OPTI_CRITERIA_PARM_P            3

#define READER_PREHEAT_PARM_C                  1189
#define READER_PREHEAT_PARM_P                     1

#define READER_WRITE_HEAT_PARM_C               1190
#define READER_WRITE_HEAT_PARM_P                  1

#define READER_READ_HEAT_PARM_C                1191
#define READER_READ_HEAT_PARM_P                   1

#define HMS_CAP_BACKOFF_FOR_TPI_PARM_C         1192
#define HMS_CAP_BACKOFF_FOR_TPI_PARM_P            1

#define TPI_ASYMMETRIC_SQZ_WRT_CNT_PARM_C      1193
#define TPI_ASYMMETRIC_SQZ_WRT_CNT_PARM_P         2

#define MAX_HIC_UPDATE_PRCNT_PARM_C            1194
#define MAX_HIC_UPDATE_PRCNT_PARM_P               1

#define NEW_OST_LOW_LIMIT_PARM_C               1195     // (DEF,NewOSTLowLimit_TPARCD,16,NA)
#define NEW_OST_LOW_LIMIT_PARM_P                  1

#define VENDOR_CYL_PARM_C                      1196     // (DEF,VendorCyl_TPARCD,16,NA)
#define VENDOR_CYL_PARM_P                         1

#define SINGLE_SIDE_SQZ_WRITES_PARM_C          1197
#define SINGLE_SIDE_SQZ_WRITES_PARM_P             1

#define RRO_START_FREQ_PARM_C                  1198      // (DEF,RroStartFreq_TPARCD,16,NA)
#define RRO_START_FREQ_PARM_P                     1

#define RRO_END_FREQ_PARM_C                    1199      // (DEF,RroEndFreq_TPARCD,16,NA)
#define RRO_END_FREQ_PARM_P                       1

#define SPECTRAL_LOW_LIMIT_PARM_C              1200      // (DEF,SpectralLowLimit_TPARCD,8,NA)
#define SPECTRAL_LOW_LIMIT_PARM_P                 1

#define HYST_BIAS_TABLE_SHIFT_PARM_C           1201
#define HYST_BIAS_TABLE_SHIFT_PARM_P              1

#define AGC_HARM_LIMIT_ARRAY_PARM_C            1202
#define AGC_HARM_LIMIT_ARRAY_PARM_P              24

#define ISLAND_WEDGES_ID_PARM_C                1203
#define ISLAND_WEDGES_ID_PARM_P                   4

#define ZEST_DATA_REP_PARM_C                   1204
#define ZEST_DATA_REP_PARM_P                      4

#define DAC_TO_HEAT_PWR_FACTOR_PARM_C          1205
#define DAC_TO_HEAT_PWR_FACTOR_PARM_P             1

#define MAX_CLR_BACKOFF_ANG_PARM_C             1206
#define MAX_CLR_BACKOFF_ANG_PARM_P                1

#define RD_ITERATION_PARM_C                    1207
#define RD_ITERATION_PARM_P                       1

#define LOW_CLR_LIMIT_PARM_C                   1208
#define LOW_CLR_LIMIT_PARM_P                      1

#define PREHEAT_LIMIT_PARM_C                   1209
#define PREHEAT_LIMIT_PARM_P                      2

#define WR_GATE_CNT_LIMIT_PARM_C               1210
#define WR_GATE_CNT_LIMIT_PARM_P                  2

#define ELT_REF_SECTOR_PARM_C                  1211
#define ELT_REF_SECTOR_PARM_P                     2

#define MEASURED_PRE_HEAT_CLR_PARM_C           1212
#define MEASURED_PRE_HEAT_CLR_PARM_P              1

#define AFH_INACTIVE_READ_HEATER_PARM_C        1213
#define AFH_INACTIVE_READ_HEATER_PARM_P           1

#define AFH_INACTIVE_WRITE_HEATER_PARM_C       1214
#define AFH_INACTIVE_WRITE_HEATER_PARM_P          1

#define TRIM_PERCENTAGE_VALUE_PARM_C           1215
#define TRIM_PERCENTAGE_VALUE_PARM_P              1

#define ZONE_BASED_SQZ_PARM_C                  1216
#define ZONE_BASED_SQZ_PARM_P                    64

#define HS_START_PARM_C                        1217
#define HS_START_PARM_P                           1

#define PARAMETER_SWEEP_LIMIT_PARM_C           1218
#define PARAMETER_SWEEP_LIMIT_PARM_P              1

#define POLYFIT_POINT_CNT_PARM_C               1219
#define POLYFIT_POINT_CNT_PARM_P                  1

#define MEDIAN_FLTR_THRESH_FACTOR_PARM_C       1220
#define MEDIAN_FLTR_THRESH_FACTOR_PARM_P          1

#define ZONE_STEP_SIZE_PARM_C                  1221
#define ZONE_STEP_SIZE_PARM_P                     1

#define ISLAND_WEDGES_AFTER_PARM_C             1222      // (DEF,WdgCntAfter_TPARCD,4,NA)
#define ISLAND_WEDGES_AFTER_PARM_P                4

#define ZONE_MASK_64_PARM_C                    1223
#define ZONE_MASK_64_PARM_P                       4

#define MIN_STD_DEV_PARM_C                     1224
#define MIN_STD_DEV_PARM_P                        1

#define FAILCNT_MAX_LIMIT_PARM_C               1225
#define FAILCNT_MAX_LIMIT_PARM_P                  1

#define SQZ_PCT_TBL_PARM_C                     1226
#define SQZ_PCT_TBL_PARM_P                       10

#define HMSC_10X_TARG_TBL_PARM_C               1227
#define HMSC_10X_TARG_TBL_PARM_P                 10

#define WINDOW_2_PARM_C                        1228
#define WINDOW_2_PARM_P                           1

#define OD_RAMP_SATURATION_UNIT_PARM_C         1229
#define OD_RAMP_SATURATION_UNIT_PARM_P            1

#define TTPE_LIMIT_PARM_C                      1230
#define TTPE_LIMIT_PARM_P                         1

#define LIMIT_ST_PARM_C                        1231
#define LIMIT_ST_PARM_P                           1

#define LIMIT_TI_PARM_C                        1232
#define LIMIT_TI_PARM_P                           1

#define FREQ_PARM_C                            1233
#define FREQ_PARM_P                               1

#define MAX_TIME_LIMIT_PARM_C                  1234
#define MAX_TIME_LIMIT_PARM_P                     1

#define SAMPLE_CNT_PARM_C                      1235
#define SAMPLE_CNT_PARM_P                         1

#define ZAP_DEBUG_KEY_PARM_C                   1236
#define ZAP_DEBUG_KEY_PARM_P                      1

#define CLR_BACKOFF_ANGS_PARM_C                1237
#define CLR_BACKOFF_ANGS_PARM_P                   1

#define HMSCAP_DELTA_THRESH_PARM_C             1238
#define HMSCAP_DELTA_THRESH_PARM_P                1

#define HEATER_RANGE_PARM_C                    1239
#define HEATER_RANGE_PARM_P                       1

#define DEFECT_LIST_SCALER_PARM_C              1240
#define DEFECT_LIST_SCALER_PARM_P                 1

#define MR_VBIAS_COEFFS_PARM_C                 1241
#define MR_VBIAS_COEFFS_PARM_P                    2

#define RD_REVS_PARM_C                         1242
#define RD_REVS_PARM_P                            1

#define DETCR_VBIAS_COEFFS_PARM_C              1243
#define DETCR_VBIAS_COEFFS_PARM_P                 2

#define DETCR_THRESH_RANGE_PARM_C              1244
#define DETCR_THRESH_RANGE_PARM_P                 1

#define DETCR_THRESH_ADJUST_PARM_C             1245
#define DETCR_THRESH_ADJUST_PARM_P                1

#define DETCR_COMPSEL_PARM_C                   1246
#define DETCR_COMPSEL_PARM_P                      1

#define DETCR_THRESH_COEFFS_PARM_C             1247
#define DETCR_THRESH_COEFFS_PARM_P                2

#define ERR_THRSH_PARM_C                       1248      // T73 new variable
#define ERR_THRSH_PARM_P                          3

#define MEASURE_SECTORS_PARM_C                 1249      // T73 new variable
#define MEASURE_SECTORS_PARM_P                    1

#define NON_CONV_BIE_RATIO_PARM_C              1250
#define NON_CONV_BIE_RATIO_PARM_P                 1

#define PATTERN_VALUE_PARM_C                   1251
#define PATTERN_VALUE_PARM_P                      1

#define INTRA_TEST_RECOVERY_PARM_C             1252
#define INTRA_TEST_RECOVERY_PARM_P                1

#define AFH_STATES_PARM_C                      1253  //2 AFH states to be compared for burnish/TCC
#define AFH_STATES_PARM_P                         2

#define AFH_SCREEN_LIMITS_PARM_C               1254
#define AFH_SCREEN_LIMITS_PARM_P                  4

#define AFH_SCREEN_MODE_PARM_C                 1255 //Modes: standard burnish, VBAR burnish, ...
#define AFH_SCREEN_MODE_PARM_P                    1

#define PES_THREE_SIGMA_LIMIT_PARM_C           1256
#define PES_THREE_SIGMA_LIMIT_PARM_P              1

#define PES_MAX_ABS_LIMIT_PARM_C               1257
#define PES_MAX_ABS_LIMIT_PARM_P                  1

#define PES_MAX_VELOCITY_LIMIT_PARM_C          1258
#define PES_MAX_VELOCITY_LIMIT_PARM_P             1

#define PES_THREE_SIGMA_MA_LIMIT_PARM_C        1259
#define PES_THREE_SIGMA_MA_LIMIT_PARM_P           1

#define ACTIVE_HEATER_MASK_PARM_C              1260
#define ACTIVE_HEATER_MASK_PARM_P                 1

#define INACTIVE_HEATER_DAC_PARM_C             1261
#define INACTIVE_HEATER_DAC_PARM_P                1

#define DEFAULT_TCR_PARM_C                     1262
#define DEFAULT_TCR_PARM_P                        1

#define TEMPERATURE_INDEX_PARM_C               1263
#define TEMPERATURE_INDEX_PARM_P                  1

#define MIN_BIAS_PARM_C                        1264
#define MIN_BIAS_PARM_P                           1

#define MAX_BIAS_PARM_C                        1265
#define MAX_BIAS_PARM_P                           1

#define BIAS_STEP_PARM_C                       1266
#define BIAS_STEP_PARM_P                          1

#define ZONE_MASK_BANK_PARM_C                  1267
#define ZONE_MASK_BANK_PARM_P                     1

#define NOMRF_REF_VALUE_PARM_C                 1268      //(T251,NOMRF reference value)
#define NOMRF_REF_VALUE_PARM_P                    1

#define REG_TO_OPT19_PARM_C                    1269      // (DEF,OptReg19_TPARCD,16,NA)
#define REG_TO_OPT19_PARM_P                       4

#define REG_TO_OPT19_EXT_PARM_C                1270      // (DEF,OptRegExt19_TPARCD,16,NA)
#define REG_TO_OPT19_EXT_PARM_P                   3

#define REG_TO_OPT20_PARM_C                    1271      // (DEF,OptReg20_TPARCD,16,NA)
#define REG_TO_OPT20_PARM_P                       4

#define REG_TO_OPT20_EXT_PARM_C                1272      // (DEF,OptRegExt20_TPARCD,16,NA)
#define REG_TO_OPT20_EXT_PARM_P                   3

#define REG_TO_OPT21_PARM_C                    1273      // (DEF,OptReg21_TPARCD,16,NA)
#define REG_TO_OPT21_PARM_P                       4

#define REG_TO_OPT21_EXT_PARM_C                1274      // (DEF,OptRegExt21_TPARCD,16,NA)
#define REG_TO_OPT21_EXT_PARM_P                   3

#define REG_TO_OPT22_PARM_C                    1275      // (DEF,OptReg22_TPARCD,16,NA)
#define REG_TO_OPT22_PARM_P                       4

#define REG_TO_OPT22_EXT_PARM_C                1276      // (DEF,OptRegExt22_TPARCD,16,NA)
#define REG_TO_OPT22_EXT_PARM_P                   3

#define REG_TO_OPT23_PARM_C                    1277      // (DEF,OptReg23_TPARCD,16,NA)
#define REG_TO_OPT23_PARM_P                       4

#define REG_TO_OPT23_EXT_PARM_C                1278      // (DEF,OptRegExt23_TPARCD,16,NA)
#define REG_TO_OPT23_EXT_PARM_P                   3

#define REG_TO_OPT24_PARM_C                    1279      // (DEF,OptReg24_TPARCD,16,NA)
#define REG_TO_OPT24_PARM_P                       4

#define REG_TO_OPT24_EXT_PARM_C                1280      // (DEF,OptRegExt24_TPARCD,16,NA)
#define REG_TO_OPT24_EXT_PARM_P                   3

#define DETCR_IPD2_BIT_MASK_EXT_PARM_C         1281
#define DETCR_IPD2_BIT_MASK_EXT_PARM_P            4

#define NUM_WRITES_MULTIPLIER_PARM_C           1282      // Test 51 number of writes multiplier
#define NUM_WRITES_MULTIPLIER_PARM_P              1

#define STE_MULTIPLIER_PARM_C                  1283      // Test 51 STE multiplier (STE thresh = ATI thresh * multiplier)
#define STE_MULTIPLIER_PARM_P                     1

#define BIAS_SPIKE_LIMIT_PARM_C                1284      // Test 136 Bias Spike limit
#define BIAS_SPIKE_LIMIT_PARM_P                   1

#define BIAS_MOVING_WINDOW_PARM_C              1285      // Test 136 Moving Window for bias spike detection
#define BIAS_MOVING_WINDOW_PARM_P                 1

#define BIAS_SUM_ZONES_LIMIT_PARM_C            1286      // Test 136 Sum of Bias for a designated zone limit
#define BIAS_SUM_ZONES_LIMIT_PARM_P               1

#define PRISM_SEEK_LENGTH_PARM_C               1287
#define PRISM_SEEK_LENGTH_PARM_P                  2

#define PRISM_SECTOR_PARM_C                    1288
#define PRISM_SECTOR_PARM_P                       1

#define WIRRO_TARGET_TRACK_PARM_C              1289
#define WIRRO_TARGET_TRACK_PARM_P                 2

#define SECTOR_INCREMENT_PARM_C                1290
#define SECTOR_INCREMENT_PARM_P                   1

#define FAFH_TRIGGER_0_PARM_C                  1291      // (T74,FafhTrig_TPARCD,28,NA) Test 74 FAFH Periodic Timer Table 0
#define FAFH_TRIGGER_0_PARM_P                     7

#define FAFH_TRIGGER_1_PARM_C                  1292      // (T74,FafhTrig_TPARCD,28,NA) Test 74 FAFH Periodic Timer Table 1
#define FAFH_TRIGGER_1_PARM_P                     7

#define FAFH_TRIGGER_2_PARM_C                  1293      // (T74,FafhTrig_TPARCD,28,NA) Test 74 FAFH Periodic Timer Table 2
#define FAFH_TRIGGER_2_PARM_P                     7

#define FAFH_TRIGGER_3_PARM_C                  1294      // (T74,FafhTrig_TPARCD,28,NA) Test 74 FAFH Periodic Timer Table 3
#define FAFH_TRIGGER_3_PARM_P                     7

#define FAFH_TRIGGER_ENTRY_PARM_C              1295      // (T74,FafhTrigEntry,28,NA) Test 74 FAFH Trigger Parameters
#define FAFH_TRIGGER_ENTRY_PARM_P                 7

#define FAFH_MIN_ADJ_PARM_C                    1296      // (T74,FafhMnAdj_TPARCD,28,NA) Test 74 Clearance Adjustments
#define FAFH_MIN_ADJ_PARM_P                       6

#define FAFH_MAX_ADJ_AWAY_PARM_C               1297      // (T74,FafhMnAdjUp_TPARCD,28,NA) Test 74 Clearance Adjustments
#define FAFH_MAX_ADJ_AWAY_PARM_P                  6

#define FAFH_MAX_ADJ_TOWARD_PARM_C             1298      // (T74,FafhMnAdjDwn_TPARCD,28,NA) Test 74 Clearance Adjustments
#define FAFH_MAX_ADJ_TOWARD_PARM_P                6

#define AR_CONVERGENCE_LMTS_SETTLE_PARM_C      1299      // (T74,FafhCnvrgLmtSetl_TPARCD,28,NA) Test 74 settling convergence limits
#define AR_CONVERGENCE_LMTS_SETTLE_PARM_P         7

#define AR_CONVERGENCE_LMTS_STEADY_PARM_C      1300      // (T74,FafhCnvrgLmtStdy_TPARCD,28,NA) Test 74 steady state convergence limits
#define AR_CONVERGENCE_LMTS_STEADY_PARM_P         7

#define FAFH_DEGRADATION_COEF_A_PARM_C         1301      // Test 74 head degradation coefficients A, B, and D
#define FAFH_DEGRADATION_COEF_A_PARM_P            6      // 3 longs (T74,FafhDegradCoefA,28,NA) (T74,FafhDegradCoefB,28,NA) (T74,FafhDegradCoefD,28,NA)

#define FAFH_DEGRADATION_COEF_B_PARM_C         1302
#define FAFH_DEGRADATION_COEF_B_PARM_P            6

#define FAFH_DEGRADATION_COEF_D_PARM_C         1303
#define FAFH_DEGRADATION_COEF_D_PARM_P            6

#define FAFH_TRIGGER_ENABLE_PARM_C             1304      // (T74,FafhTrigEnbl_TPARCD,16,NA) Test 74 trigger enable bits
#define FAFH_TRIGGER_ENABLE_PARM_P                1

#define GB_BY_RAMP_CYL_P1_PARM_C               1305
#define GB_BY_RAMP_CYL_P1_PARM_P                  1

#define GB_BY_RAMP_CYL_P2_PARM_C               1306
#define GB_BY_RAMP_CYL_P2_PARM_P                  1

#define MIN_RAMPCYL_REQ_PARM_C                 1307
#define MIN_RAMPCYL_REQ_PARM_P                    1

#define DSTE_BAND_SIZE_PARM_C                  1308
#define DSTE_BAND_SIZE_PARM_P                     1

#define PSTE_BAND_SIZE_PARM_C                  1309
#define PSTE_BAND_SIZE_PARM_P                     1

#define PATTERN_PARM_C                         1310      // (T74,Pttrn_TPARCD,8,NA) Enter 8 pattern bytes or words depending on format spec
#define PATTERN_PARM_P                            8

#define PATTERN_LENGTH_PARM_C                  1311      // (T74,PttrnLen_TPARCD,8,NA) Optional pattern length for above PATTERN
#define PATTERN_LENGTH_PARM_P                     1

#define AUTO_SCALE_SEED_PARM_C                 1312
#define AUTO_SCALE_SEED_PARM_P                    1

#define DEBUG_PRINT_1_PARM_C                   1313
#define DEBUG_PRINT_1_PARM_P                      1

#define RW_MODE_SEEK_TEST_PARM_C               1314      // RWMode for T30 seek test
#define RW_MODE_SEEK_TEST_PARM_P                  4

#define ARC_LENGTH_LIMIT_PARM_C                1315
#define ARC_LENGTH_LIMIT_PARM_P                   1

#define MAX_TOTAL_BYTES_PARM_C                 1316
#define MAX_TOTAL_BYTES_PARM_P                    2

#define MOTOR_TIMER_DELTA_PARM_C               1317
#define MOTOR_TIMER_DELTA_PARM_P                  1

#define ZERO_CROSSING_REVS_PARM_C              1318
#define ZERO_CROSSING_REVS_PARM_P                 1

#define ZONE_MASK_BLOCK_PARM_C                 1319
#define ZONE_MASK_BLOCK_PARM_P                   16

#define HMSC_RD_10X_TARG_TBL_PARM_C            1320
#define HMSC_RD_10X_TARG_TBL_PARM_P              10

#define DITHER_10X_TBL_PARM_C                  1321
#define DITHER_10X_TBL_PARM_P                    10

#define RD_CLR_BACKOFF_ANGS_PARM_C             1322
#define RD_CLR_BACKOFF_ANGS_PARM_P                1

#define PEAK_AGC_LIMIT_PARM_C                  1323      // (DEF,PkAgcLmt_TPARCD,16,NA)
#define PEAK_AGC_LIMIT_PARM_P                     1

#define SIGMA_AGC_LIMIT_PARM_C                 1324      // (DEF,SgmaAgcLmt_TPARCD,16,NA)
#define SIGMA_AGC_LIMIT_PARM_P                    1

#define TRUNCATE_PARM_C                        1325      // (T231,Truncaste_TPARCD,8,NA)
#define TRUNCATE_PARM_P                           1

#define SIF_CREATE_FORMAT_PARM_C               1326
#define SIF_CREATE_FORMAT_PARM_P                  1

#define SIF_W2R_BY_HEAD_EXT_PARM_C             1327
#define SIF_W2R_BY_HEAD_EXT_PARM_P               16

#define SIF_W2R_TOLERANCE_PARM_C               1328
#define SIF_W2R_TOLERANCE_PARM_P                  1

#define SIF_XFR_BPI_PC_TO_DISC_PARM_C          1329
#define SIF_XFR_BPI_PC_TO_DISC_PARM_P             1

#define TEST_CYL_PCT_PARM_C                    1330      // (DEF,TstCylPct_TPARCD,8,NA)
#define TEST_CYL_PCT_PARM_P                       1

#define FIR_TAP_GRID_LEN_PARM_C                1331
#define FIR_TAP_GRID_LEN_PARM_P                   1

#define DHS_SETUP_PARM_C                       1332      // (T74,DualHrmSnsrCnfg_TPARCD,16,NA)
#define DHS_SETUP_PARM_P                          6

#define WGC_LIMIT_PARM_C                       1333
#define WGC_LIMIT_PARM_P                          2

#define GAP_TRANS_OFFSET_PARM_C                1334
#define GAP_TRANS_OFFSET_PARM_P                   1

#define SUPERPARITY_PER_TRK_PARM_C             1335      // (T530,SctrCnt_TPARCD,16,NA)
#define SUPERPARITY_PER_TRK_PARM_P                1

#define MAX_BPI_ADJ_PARM_C                     1336
#define MAX_BPI_ADJ_PARM_P                        1

#define IPD2_BIT_INDEX_PARM_C                  1337
#define IPD2_BIT_INDEX_PARM_P                     2

#define DETCR_BIT_INDEX_PARM_C                 1338
#define DETCR_BIT_INDEX_PARM_P                    2

#define DETECTOR_BIT_INDEX_PARM_C              1339
#define DETECTOR_BIT_INDEX_PARM_P                12

#define ZONE_NUM_PARM_C                        1340
#define ZONE_NUM_PARM_P                          30

#define START_NOMINAL_TRK_PARM_C               1341
#define START_NOMINAL_TRK_PARM_P                 60

#define NUM_NOMINAL_TRK_PARM_C                 1342
#define NUM_NOMINAL_TRK_PARM_P                   60

#define ZONECOPYOPTIONS_PARM_C                 1343
#define ZONECOPYOPTIONS_PARM_P                    1

#define SHORT_RAMP_CLIP_CYL_PARM_C             1344
#define SHORT_RAMP_CLIP_CYL_PARM_P                1

#define FOLDER_NAME_2_PARM_C                   1345      // (DEF,FldrNam_TPARCD,8,NA)
#define FOLDER_NAME_2_PARM_P                      4

#define RAP_BURNISH_PARM_C                     1346
#define RAP_BURNISH_PARM_P                        2

#define DATA_SET6_PARM_C                       1347      // (NA,NA,NA,NA)
#define DATA_SET6_PARM_P                          4

#define MEDIA_CACHE_SIZE_PARM_C                1348
#define MEDIA_CACHE_SIZE_PARM_P                   1

#define UMP_SIZE_PARM_C                        1349
#define UMP_SIZE_PARM_P                           1

#define NUM_UMP_ZONE_PARM_C                    1350
#define NUM_UMP_ZONE_PARM_P                       1

#define CWORD6_PARM_C                          1351      // (DEF,Cwrd6_TPARCD,16,NA)
#define CWORD6_PARM_P                             1

#define MDD_CONTROL_PARM_C                     1352
#define MDD_CONTROL_PARM_P                        2

#define MDD_TDI_PARM_C                         1353
#define MDD_TDI_PARM_P                            3

#define MDD_TDO_PARM_C                         1354
#define MDD_TDO_PARM_P                            3

#define MDD_WSEL_PARM_C                        1355
#define MDD_WSEL_PARM_P                           3

#define SOURCE_ZONE_PARM_C                     1356
#define SOURCE_ZONE_PARM_P                        1

#define UMP_START_ZONE_PARM_C                  1357
#define UMP_START_ZONE_PARM_P                     1

#define FIXED_MAX_CYL_PARM_C                   1358
#define FIXED_MAX_CYL_PARM_P                      2

#define ERR_AC_THRSH_PARM_C                    1359      // T73 new variable
#define ERR_AC_THRSH_PARM_P                       2

#define RAP_START_ADDR_PARM_C                  1363
#define RAP_START_ADDR_PARM_P                     2

#define NUM_MC_ZONE_PARM_C                     1364
#define NUM_MC_ZONE_PARM_P                        1

#define THERMAL_DECAY_PARM_C                   1365
#define THERMAL_DECAY_PARM_P                     10

#define PRESSURE_COEF_PARM_C                   1366
#define PRESSURE_COEF_PARM_P                      2

#define ZONED_TIME_LIMITS_PARM_C               1367
#define ZONED_TIME_LIMITS_PARM_P                  6

#define LIVE_SENSOR_THRESHOLD_PARM_C           1368
#define LIVE_SENSOR_THRESHOLD_PARM_P             75

#define TRANSITION_ZONES_PARM_C                1369
#define TRANSITION_ZONES_PARM_P                   3

#define SQUEEZE_MODES_PARM_C                   1370
#define SQUEEZE_MODES_PARM_P                      4

#define VOLT_TARG_PARM_C                       1371     // (DEF,TgtVltg_TPARCD,16,NA)
#define VOLT_TARG_PARM_P                          1

#define VGAS_TARG_PARM_C                       1372     // (DEF,TgtVGAS_TPARCD,16,NA)
#define VGAS_TARG_PARM_P                          1

#define LOOP_TO_CHECK_PARM_C                   1373
#define LOOP_TO_CHECK_PARM_P                      8

#define MAX_VIS_RETRY_PARM_C                   1374
#define MAX_VIS_RETRY_PARM_P                      8

#define MAX_HID_RETRY_PARM_C                   1375
#define MAX_HID_RETRY_PARM_P                      8

#define MAX_FREE_RETRY_PARM_C                  1376
#define MAX_FREE_RETRY_PARM_P                     8

#define TA_AMPLITUDE_2_PARM_C                  1377     // (DEF,TaAmp2_TPARCD,16,NA)
#define TA_AMPLITUDE_2_PARM_P                     4

#define NUM_ADJ_CYLS_2_PARM_C                  1378     // (DEF,AdjcntCylCnt2_TPARCD,16,NA)
#define NUM_ADJ_CYLS_2_PARM_P                     4

#define TAIL_SIZES_2_PARM_C                    1379     // (DEF,TailSz2_TPARCD,16,NA)
#define TAIL_SIZES_2_PARM_P                       4

#define AR_COEFF_LIMITS_PARM_C                 1380
#define AR_COEFF_LIMITS_PARM_P                    8

#define FAFH_TARGET_CLR_LIMITS_PARM_C          1381
#define FAFH_TARGET_CLR_LIMITS_PARM_P             2

#define NRRO_THREE_SIGMA_LIMIT_PARM_C          1382
#define NRRO_THREE_SIGMA_LIMIT_PARM_P             1

#define HEAD_MAP_PARM_C                        1383
#define HEAD_MAP_PARM_P                          32

#define CMR_MIN_ERR_RATE_PARM_C                1384
#define CMR_MIN_ERR_RATE_PARM_P                   1

#define PRECODER0_PARM_C                       1385
#define PRECODER0_PARM_P                          2

#define PRECODER1_PARM_C                       1386
#define PRECODER1_PARM_P                          2

#define PRECODER2_PARM_C                       1387
#define PRECODER2_PARM_P                          2

#define PRECODER3_PARM_C                       1388
#define PRECODER3_PARM_P                          2

#define PRECODER4_PARM_C                       1389
#define PRECODER4_PARM_P                          2

#define AFH_CLR_VS_RAP_THRESH_PARM_C           1390
#define AFH_CLR_VS_RAP_THRESH_PARM_P              1

#define REVERSE_IPS_LIMIT_PARM_C               1391
#define REVERSE_IPS_LIMIT_PARM_P                  1

#define BIT_OS_DEFAULT_PARM_C                  1392
#define BIT_OS_DEFAULT_PARM_P                     1

#define TX_LVL_DEFAULT_PARM_C                  1393
#define TX_LVL_DEFAULT_PARM_P                     1

#define PDW_IOS_PARM_C                         1394
#define PDW_IOS_PARM_P                            1
                                    
#define PDW_MODE_PARM_C                        1395
#define PDW_MODE_PARM_P                           1

#define MDD_QLFWIN_PARM_C                      1396
#define MDD_QLFWIN_PARM_P                         3

#define MDD_QLFTHR_PARM_C                      1397
#define MDD_QLFTHR_PARM_P                         3

#define SPINDLE_DIP_LIMIT_PARM_C               1398
#define SPINDLE_DIP_LIMIT_PARM_P                  1

#define MIN_BW_THRESH_PARM_C                   1399		// (T282,minBwTh_TPARCD,16,NA)
#define MIN_BW_THRESH_PARM_P                      1

#define MAX_BW_THRESH_PARM_C                   1400		// (T282,maxBwTh_TPARCD,16,NA)
#define MAX_BW_THRESH_PARM_P                      1

#define POS_VTH_SCALER_PARM_C                  1401     // (T94,PosVltgThrshScal)
#define POS_VTH_SCALER_PARM_P                     1

#define DETCR_BIAS_RANGE_PARM_C                1402     // (T135,DETCR_BIAS_RANGE)
#define DETCR_BIAS_RANGE_PARM_P                   2

#define PDW_IOS_MIN_PARM_C                     1403
#define PDW_IOS_MIN_PARM_P                        1

#define PDW_IOS_MAX_PARM_C                     1404
#define PDW_IOS_MAX_PARM_P                        1

#define PDW_IOS_STEP_PARM_C                    1405
#define PDW_IOS_STEP_PARM_P                       1

#define SEC_CZAP_SAT_LIMIT_PARM_C              1406
#define SEC_CZAP_SAT_LIMIT_PARM_P                 1

#define CZAP_SAT_COUNT_SCREEN_PARM_C           1407
#define CZAP_SAT_COUNT_SCREEN_PARM_P              1

#define LATE1RF_MIN_PARM_C                     1408
#define LATE1RF_MIN_PARM_P                        1

#define LATE1RF_MAX_PARM_C                     1409
#define LATE1RF_MAX_PARM_P                        1

#define LATE1RF_STEP_PARM_C                    1410
#define LATE1RF_STEP_PARM_P                       1

#define LATE2RF_MIN_PARM_C                     1411
#define LATE2RF_MIN_PARM_P                        1

#define LATE2RF_MAX_PARM_C                     1412
#define LATE2RF_MAX_PARM_P                        1

#define LATE2RF_STEP_PARM_C                    1413
#define LATE2RF_STEP_PARM_P                       1

#define CMPRS_ID_PARM_C                        1414     // (T287,CmprsId_TPARCD,8,NA)
#define CMPRS_ID_PARM_P                           1

#define POLY_ORDER_PARM_C                      1415     // (T287,PolyOrdr_TPARCD,16,NA)
#define POLY_ORDER_PARM_P                         1

#define REV_PARM_C                             1416     // (T287,Rev_TPARCD,16,NA)
#define REV_PARM_P                                1

#define PREAMBLE_CYCLE_PARM_C                  1417    
#define PREAMBLE_CYCLE_PARM_P                     4

#define NORMALIZE_TEMP_PARM_C                  1418
#define NORMALIZE_TEMP_PARM_P                     1

#define OPTI_HEADS_PARM_C                      1419
#define OPTI_HEADS_PARM_P                        50

#define OPTI_ZONES_PARM_C                      1420
#define OPTI_ZONES_PARM_P                        50

#define START_ZONES_PARM_C                     1421
#define START_ZONES_PARM_P                       50

#define END_ZONES_PARM_C                       1422
#define END_ZONES_PARM_P                         50

#define RD_WR_GAP_DELAY_PARM_C                 1423
#define RD_WR_GAP_DELAY_PARM_P                    1

#define MAX_NUM_HICCUPS_PARM_C                 1424     // (T2108,MxHiccups_TPARCD,16,NA)
#define MAX_NUM_HICCUPS_PARM_P                    1

#define ADJUST_VOLTAGE_THRESH_PARM_C           1425     // (T2108,AdjVltgThrsh_TPARCD,16,NA)
#define ADJUST_VOLTAGE_THRESH_PARM_P              1

#define MAX_TRKS_W_NOISY_DETCTS_PARM_C         1426     // (T2108,MxTrkNoiseDtct_TPARCD,16,NA)
#define MAX_TRKS_W_NOISY_DETCTS_PARM_P            1

#define MAX_TA_SECTORS_PER_TRK_PARM_C          1427     // (T2108,MxTaSctrPerTrk_TPARCD,16,NA)
#define MAX_TA_SECTORS_PER_TRK_PARM_P             1

#define TRK_CLN_APPEND_PARM_C                  1428
#define TRK_CLN_APPEND_PARM_P                     0

#define SQZ_OFFSET_START_PARM_C                1429      // (DEF,SqzOfstStart_TPARCD,16,NA)
#define SQZ_OFFSET_START_PARM_P                   1

#define SQZ_OFFSET_END_PARM_C                  1430      // (DEF,SqzOfstEnd_TPARCD,16,NA)
#define SQZ_OFFSET_END_PARM_P                     1

#define NUM_SQZ_WRITES_START_PARM_C            1431      // (DEF,SqzWrCntStart_TPARCD,16,NA)
#define NUM_SQZ_WRITES_START_PARM_P               1

#define NUM_SQZ_WRITES_END_PARM_C              1432      // (DEF,SqzWrCntEnd_TPARCD,16,NA)
#define NUM_SQZ_WRITES_END_PARM_P                 1

#define CLEARANCE_OFFSET_START_PARM_C          1433
#define CLEARANCE_OFFSET_START_PARM_P             1

#define CLEARANCE_OFFSET_END_PARM_C            1434
#define CLEARANCE_OFFSET_END_PARM_P               1
#define JOG_ERR_ODID_THRSH_PARM_C              1435      // (T287, ,16,NA)
#define JOG_ERR_ODID_THRSH_PARM_P                 1

#define JOG_ERR_ZIPPERZONE_THRSH_PARM_C        1436      // (T287, ,16,NA)
#define JOG_ERR_ZIPPERZONE_THRSH_PARM_P           1

#define DC_ERR_ODID_THRSH_PARM_C               1437      // (T287, ,16,NA)
#define DC_ERR_ODID_THRSH_PARM_P                  1

#define DC_ERR_ZIPPERZONE_THRSH_PARM_C         1438      // (T287, ,16,NA)
#define DC_ERR_ZIPPERZONE_THRSH_PARM_P            1

#define ODID_BAND_SIZE_PARM_C                  1439      // (T287, ,16,NA)
#define ODID_BAND_SIZE_PARM_P                     1

#define ID_PAD_TK_VALUE_EXT_PARM_C             1440      // (DEF,IdPadTrkVal_TPARCD,16,NA)
#define ID_PAD_TK_VALUE_EXT_PARM_P                2

#define NUM_SUB_WRITES_PARM_C                  1441      
#define NUM_SUB_WRITES_PARM_P                     3

#define RD_TRKS_SUB_WRITES_PARM_C              1442      
#define RD_TRKS_SUB_WRITES_PARM_P                 3

#define SAM_TO_SGDWN_PARM_C                    1443    
#define SAM_TO_SGDWN_PARM_P                       4

/***************************************************************************************************************************

 #     #    ##    #####    #    #  ###  #    #   ####
 #  #  #   #  #   #    #   # #  #   #   # #  #  #
 # # # #  ######  #####    #  # #   #   #  # #  #  ###
 ##   ##  #    #  #    #   #   ##   #   #   ##  #    #
 #     #  #    #  #     #  #    #  ###  #    #   ####

 Check the deprecation and modification policies at the top of this file before making changes.

*****************************************************************************************************************************/


//*****************  IOTEST Unique Parameter definitions  (Starts @ 16000) ***********************************

#define CUSTOMER_OPTION_PARM_C                     16000     // (DEF,CustOptn_TPARCD,8,NA) (T536,CustOptn_TPARCD,8,0x000F)
#define CUSTOMER_OPTION_PARM_P                         1

#define ENABLE_VPD_PARM_C                          16001     // (T514,EnblVpd_TPARCD,8,0x0001)
#define ENABLE_VPD_PARM_P                              1

#define CHECK_MODE_NUMBER_PARM_C                   16002     // (T514,ChkMdlNum_TPARCD,8,0x0001)
#define CHECK_MODE_NUMBER_PARM_P                       1

#define PAGE_CODE_PARM_C                           16003     // (DEF,PgCode_TPARCD,16,NA) (T514,PgCode_TPARCD,16,0x00FF)(T518,PgCode_TPARCD,16,0x007F)
#define PAGE_CODE_PARM_P                               1

#define EXPECTED_FW_REV_1_PARM_C                   16004     // (T514,FwRev1_TPARCD,16,NA) (T535,FwRev1_TPARCD,16,NA)
#define EXPECTED_FW_REV_1_PARM_P                       1

#define EXPECTED_FW_REV_2_PARM_C                   16005     // (T514,FwRev2_TPARCD,16,NA)
#define EXPECTED_FW_REV_2_PARM_P                       1

#define EXPECTED_FW_REV_3_PARM_C                   16006     // (T514,FwRev3_TPARCD,16,NA)
#define EXPECTED_FW_REV_3_PARM_P                       1

#define EXPECTED_FW_REV_4_PARM_C                   16007     // (T514,FwRev4_TPARCD,16,NA)
#define EXPECTED_FW_REV_4_PARM_P                       1

#define GET_FW_REV_FROM_NETWORK_PARM_C             16008     // (T514,GetNetFwRev_TPARCD,8,0x0003)
#define GET_FW_REV_FROM_NETWORK_PARM_P                 1

#define TEST_OPERATING_MODE_PARM_C                 16009     // (DEF,TstMode_TPARCD,16,NA) (T503,TstMode_TPARCD,16,0x0003) (T515,TstMode_TPARCD,16,0x00FF) (T528,TstMode_TPARCD,16,0x0001) (T530,TstMode_TPARCD,16,0x000F) (T535,TstMode_TPARCD,16,0x000F) (T544,TstMode_TPARCD,16,0x000F) (T549,TstMode_TPARCD,16,0x000F)
#define TEST_OPERATING_MODE_PARM_P                     1     // (T551,TstMode_TPARCD,16,0x0001) (T555,TstMode_TPARCD,16,0x000F) (T555,TstMode_TPARCD,16,0x0080) (T556,TstMode_TPARCD,16,0x000F) (T557,TstMode_TPARCD,16,0x000F) (T557,TstMode_TPARCD,16,0x0080) (T558,TstMode_TPARCD,16,0x0001) (T558,TstMode_TPARCD,16,0x0002)
                                                             // (T561,TstMode_TPARCD,16,0x000F) (T591,TstMode_TPARCD,16,0x0003) no functionality (T601,TstMode_TPARCD,16,0x0003) (T605,TstMode_TPARCD,16,0x0001) (T605,TstMode_TPARCD,16,0x0002) (T605,TstMode_TPARCD,16,0x0004)
                                                             // (T611,TstMode_TPARCD,16,0x0003) (T615,TstMode_TPARCD,16,0x0001) (T615,TstMode_TPARCD,16,0x0003) (T621,TstMode_TPARCD,16,0x00FF) (T623,TstMode_TPARCD,16,0x00FF) (T634,TstMode_TPARCD,16,0x00FF) (T708,TstMode_TPARCD,16,0x000F)

#define SAVE_PARAMETERS_PARM_C                     16010     // (T503,SavParm_TPARCD,8,NA)
#define SAVE_PARAMETERS_PARM_P                         1

#define PARAMETER_CODE_1_PARM_C                    16011     // (T503,ParmCode1_TPARCD,16,NA)
#define PARAMETER_CODE_1_PARM_P                        1

#define PARAMETER_CODE_1_MSW_PARM_C                16012     // (T503,ParmCode1Lmt_TPARCD,32,NA) (T599,BufOfst_TPARCD,16,NA)
#define PARAMETER_CODE_1_MSW_PARM_P                    1

#define PARAMETER_CODE_1_LSW_PARM_C                16013     // (T503,ParmCode1Lmt_TPARCD,32,NA) (T599,BufOfst_TPARCD,16,NA)
#define PARAMETER_CODE_1_LSW_PARM_P                    1

#define PARAMETER_CODE_2_PARM_C                    16014     // (T503,ParmCode2_TPARCD,16,NA)
#define PARAMETER_CODE_2_PARM_P                        1

#define PARAMETER_CODE_2_MSW_PARM_C                16015     // (T503,ParmCode2Lmt_TPARCD,32,NA)
#define PARAMETER_CODE_2_MSW_PARM_P                    1

#define PARAMETER_CODE_2_LSW_PARM_C                16016     // (T503,ParmCode2Lmt_TPARCD,32,NA)
#define PARAMETER_CODE_2_LSW_PARM_P                    1

#define ROBUST_LOGGING_PARM_C                      16017     // (T503,RbstLog_TPARCD,16,NA)
#define ROBUST_LOGGING_PARM_P                          1

#define BGMS_FAILURES_PARM_C                       16018     // (T503,BgmsFailLmt_TPARCD,8,NA) (T634,BgmsFailLmt_TPARCD,8,NA)
#define BGMS_FAILURES_PARM_P                           1

#define CONTROLLER_CHIP_REG_PARM_C                 16019     // (T504,CtrlChipReg_TPARCD,8,0x0001)
#define CONTROLLER_CHIP_REG_PARM_P                     1

#define NUMBER_REGISTER_BANKS_PARM_C               16020     // (T504,NumRegBank_TPARCD,16,NA)
#define NUMBER_REGISTER_BANKS_PARM_P                   1

#define TRANSLATE_LOGICAL_BLOCK_PARM_C             16021     // (T504,TrnslatLgclBlk_TPARCD,8,NA)
#define TRANSLATE_LOGICAL_BLOCK_PARM_P                 1

#define COMMAND_TIMEOUT_SECONDS_PARM_C             16022     // (T506,CmdTmoutSec_TPARCD,16,NA)
#define COMMAND_TIMEOUT_SECONDS_PARM_P                 1

#define COMMAND_TIMEOUT_MS_PARM_C                  16023     // (T506,CmdTmoutMsec_TPARCD,16,NA)
#define COMMAND_TIMEOUT_MS_PARM_P                      1

#define FORMAT_CMD_TIME_LSB_PARM_C                 16024     // (T506,FmtCmdWaitTm_TPARCD,32,NA)
#define FORMAT_CMD_TIME_LSB_PARM_P                     1

#define FORMAT_CMD_TIME_MSB_PARM_C                 16025     // (T506,FmtCmdWaitTm_TPARCD,32,NA)
#define FORMAT_CMD_TIME_MSB_PARM_P                     1

#define WAIT_READY_TIME_PARM_C                     16026     // (T506,WaitRdyTmSec_TPARCD,16,NA)
#define WAIT_READY_TIME_PARM_P                         1

#define RESPONSE_TIME_MS_PARM_C                    16027     // (T506,RsponsTmMsec_TPARCD,16,NA)
#define RESPONSE_TIME_MS_PARM_P                        1

#define TEST_EXE_TIME_SECONDS_PARM_C               16028     // (T506,TstTmSec_TPARCD,16,NA) (T625,TstExecTmSec_TPARCD,16,NA)
#define TEST_EXE_TIME_SECONDS_PARM_P                   1

#define FACTORY_CMD_TIMEOUT_SECS_PARM_C            16029     // (T506,FctrCmdTmoutSec_TPARCD,16,NA)
#define FACTORY_CMD_TIMEOUT_SECS_PARM_P                1

#define TIME_TEST_FLAG_PARM_C                      16030     // (T505,TstTmFlag_TPARCD,16,0x0001)
#define TIME_TEST_FLAG_PARM_P                          1

#define TIME_BEFORE_FAIL_PARM_C                    16031     // (T505,MxTmToFail_TPARCD,16,NA)
#define TIME_BEFORE_FAIL_PARM_P                        1

#define NUMBER_OF_TESTS_TO_SKIP_PARM_C             16032     // (T505,NumTstToSkp_TPARCD,16,NA)
#define NUMBER_OF_TESTS_TO_SKIP_PARM_P                 1

#define DRIVE_CONFIG_TBL_REFRESH_PARM_C            16033     // (T507,DrvCnfgTblRfrsh_TPARCD,8,0x0002)Enable (T507,DrvCnfgTblRfrsh_TPARCD,8,0x0001)Option to set always on
#define DRIVE_CONFIG_TBL_REFRESH_PARM_P                1

#define MAX_HEAD_IDENTIFICATION_PARM_C             16034     // (T507,MxHdId_TPARCD,8,0x0002)Enable T507,MxHdId_TPARCD,8,0x0001)Option to set always on
#define MAX_HEAD_IDENTIFICATION_PARM_P                 1

#define UNKNOWN_MODEL_NUMBER_PARM_C                16035     // (T507,UnknownMdlNum_TPARCD,8,0x0002)Enable (T507,UnknownMdlNum_TPARCD,8,0x0001)Option set don't fail
#define UNKNOWN_MODEL_NUMBER_PARM_P                    1

#define RESET_DRIVE_AFTER_TEST_PARM_C              16036     // (T507,RstDrvAftrTst_TPARCD,8,0x0002)Enable (T507,RstDrvAftrTst_TPARCD,8,0x0001)Option
#define RESET_DRIVE_AFTER_TEST_PARM_P                  1

#define SET_SERVO_WEDGES_PER_TRK_PARM_C            16037     // (T507,SetSvoWdgPerTrk_TPARCD,8,0x0002)Enable T507,SetSvoWdgPerTrk_TPARCD,8,0x0001)Option   The Enable Bit Enables SvoWdgPerTrk
#define SET_SERVO_WEDGES_PER_TRK_PARM_P                1

#define SET_SERVO_GAP_BYTE_COUNT_PARM_C            16038     // (T507,SetSvoGapBytCnt_TPARCD,8,0x0002)Enable (T507,SetSvoGapBytCnt_TPARCD,8,0x0001)Option   The Enable Bit Enables SvoGapBytCnt
#define SET_SERVO_GAP_BYTE_COUNT_PARM_P                1

#define SERVO_WEDGES_PER_TRACK_PARM_C              16039     // (T507,SvoWdgPerTrk_TPARCD,16,NA)
#define SERVO_WEDGES_PER_TRACK_PARM_P                  1

#define SERVO_GAP_BYTE_COUNT_PARM_C                16040     // (DEF,SvoGapBytCnt_TPARCD,16,NA)
#define SERVO_GAP_BYTE_COUNT_PARM_P                    1

#define ONE_SEC_PER_ILQ_MODE_PARM_C                16041     // (T507,IlqMode_TPARCD,8,NA) no functionality
#define ONE_SEC_PER_ILQ_MODE_PARM_P                    1

#define ONE_CRC_WRD_PER_PKT_MODE_PARM_C            16042     // (T507,CrcWrdPerPackMode_TPARCD,8,NA) no functionality
#define ONE_CRC_WRD_PER_PKT_MODE_PARM_P                1

#define DELAYED_START_PARM_C                       16043     // (T507,DlyStrt_TPARCD,8,0x0002)Enable (T507,DlyStrt_TPARCD,8,0x0001)Option/Set
#define DELAYED_START_PARM_P                           1

#define REMOTE_START_PARM_C                        16044     // (T507,RemotStrt_TPARCD,8,0x0002)Enable (T507,RemotStrt_TPARCD,8,0x0001)Option/Set
#define REMOTE_START_PARM_P                            1

#define WRT_READ_DISCONNECT_MODE_PARM_C            16045     // (T507,WrRdDiscnnctMode_TPARCD,8,NA) no functionality
#define WRT_READ_DISCONNECT_MODE_PARM_P                1

#define SAVE_LAST_50_COMMANDS_PARM_C               16046     // (T507,SavRprtLast50Cmd_TPARCD,8,0x0003)
#define SAVE_LAST_50_COMMANDS_PARM_P                   1

#define RETRY_COUNT_RANGE_START_PARM_C             16047     // (T507,RtryCntRgStrt_TPARCD,16,0x7FFF) (T507,RtryCntRgStrt_TPARCD,16,0x8000)
#define RETRY_COUNT_RANGE_START_PARM_P                 1

#define RETRY_COUNT_RANGE_END_PARM_C               16048     // (T507,RtryCntRgEnd_TPARCD,16,NA)
#define RETRY_COUNT_RANGE_END_PARM_P                   1

#define ACTIVE_LED_ON_PARM_C                       16049     // (T507,ActvLed_TPARCD,8,0x0002)Enable (T507,ActvLed_TPARCD,8,0x0001)Option/Set
#define ACTIVE_LED_ON_PARM_P                           1

#define SET_SDBP_MODE_ON_PARM_C                    16050     // (T507,SetSdbpModeOn_TPARCD,8,0x0002)Enable (T507,SetSdbpModeOn_TPARCD,8,0x0001)Option/Set
#define SET_SDBP_MODE_ON_PARM_P                        1

#define ACCESS_MODE_PARM_C                         16051     // (DEF,AccssMode_TPARCD,8,NA) (T510,AccssMode_TPARCD,8,0x0001) (T551,AccssMode_TPARCD,8,0x0001)
#define ACCESS_MODE_PARM_P                             1     // (T509,AccssMode_TPARCD,8,NA) (T1509,AccssMode_TPARCD,8,NA) (T5509,AccssMode_TPARCD,8,NA) T509/T1509/T5509 no functionality 

#define WRITE_AND_VERIFY_PARM_C                    16052     // (DEF,WrVfy_TPARCD,16,0x0001)
#define WRITE_AND_VERIFY_PARM_P                        1

#define DISABLE_FREE_RETRY_PARM_C                  16053     // (DEF,DisblFreeRtry_TPARCD,8,0x0001) (T598,DisblFreeRtry_TPARCD,8,NA) (T618,DisblFreeRtry_TPARCD,8,NA) (T621,DisblFreeRtry_TPARCD,8,NA)
#define DISABLE_FREE_RETRY_PARM_P                      1

#define DISABLE_ECC_ON_FLY_PARM_C                  16054     // (DEF,DisblEccFly_TPARCD,8,0x0001) (T598,DisblEccFly_TPARCD,8,NA) (T618,DisblEccFly_TPARCD,8,NA) (T621,DisblEccFly_TPARCD,8,NA)
#define DISABLE_ECC_ON_FLY_PARM_P                      1

#define CACHE_MODE_PARM_C                          16055     // (DEF,CacheMode_TPARCD,8,0x0001)
#define CACHE_MODE_PARM_P                              1

#define TRANSFER_MODE_PARM_C                       16056     // (DEF,TrnsfrMode_TPARCD,8,0x0001) (T558,TrnsfrMode_TPARCD,8,NA) no functionality (T621,TrnsfrMode_TPARCD,8,NA) (T638,TrnsfrMode_TPARCD,8,NA)
#define TRANSFER_MODE_PARM_P                           1

#define WRITE_READ_MODE_PARM_C                     16057     // (DEF,WrRdMode_TPARCD,8,0x0003) (T551,WrRdMode_TPARCD,8,0x0001)Write (T551,WrRdMode_TPARCD,8,0x0002)Read (T618,WrRdMode_TPARCD,8,0x0007) (T625,WrRdMode_TPARCD,8,NA) (T705,WrRdMode_TPARCD,8,0x000F)
#define WRITE_READ_MODE_PARM_P                         1

#define REPORT_HIDDEN_RETRY_PARM_C                 16058     // (DEF,RprtHidnRtry_TPARCD,8,0x0001) (T598,RprtHidnRtry_TPARCD,8,NA) (T618,RprtHidnRtry_TPARCD,8,NA) (T621,RprtHidnRtry_TPARCD,8,NA) (T623,RprtHidnRtry_TPARCD,8,0x0001)
#define REPORT_HIDDEN_RETRY_PARM_P                     1

#define DISCONNECT_MODE_PARM_C                     16059     // (T509,DiscnnctMode_TPARCD,8,0x0001) (T510,DiscnnctMode_TPARCD,8,0x0001) (T551,DiscnnctMode_TPARCD,8,0x0001)WR Discon (T551,DiscnnctMode_TPARCD,8,0x0002)Rd Discon 
#define DISCONNECT_MODE_PARM_P                         1     // (T558,DiscnnctMode_TPARCD,8,NA) (T714,DiscnnctMode_TPARCD,8,NA) T558/T714 no functionality, to remove requires other function call to change but no need to recieve parameter leave variable as default 
                                                             // (T1509,DiscnnctMode_TPARCD,8,0x0001) (T5509,DiscnnctMode_TPARCD,8,0x0001) 

#define EXECUTE_HIDDEN_RETRY_PARM_C                16060     // (DEF,ExecHidnRtry_TPARCD,8,0x0001) (T598,ExecHidnRtry_TPARCD,8,NA) (T618,ExecHidnRtry_TPARCD,8,NA) (T621,ExecHidnRtry_TPARCD,8,NA)
#define EXECUTE_HIDDEN_RETRY_PARM_P                    1     

#define PATTERN_MODE_PARM_C                        16061     // (DEF,PttrnMode_TPARCD,8,0x0083) (T520,PttrnMode_TPARCD,8,NA) (T522,PttrnMode_TPARCD,8,0x00FF) (T532,PttrnMode_TPARCD,8,0x00FF) (T539,PttrnMode_TPARCD,8,0x0010) (T539,PttrnMode_TPARCD,8,0x0040)
#define PATTERN_MODE_PARM_P                            1     // (T550,PttrnMode_TPARCD,8,0x00FF) (T551,PttrnMode_TPARCD,8,NA) (T551,PttrnMode_TPARCD,8,NA) (T551,PttrnMode_TPARCD,8,0x0001) (T558,PttrnMode_TPARCD,8,0x00FF) (T558,PttrnMode_TPARCD,8,0xFF00) (T591,PttrnMode_TPARCD,8,0x00FF) (T597,PttrnMode_TPARCD,8,NA) (T618,PttrnMode_TPARCD,8,NA) (T625,PttrnMode_TPARCD,8,NA)

#define SAVE_READ_ERR_TO_MEDIA_PARM_C              16062     // (DEF,SavRdErrMedia_TPARCD,8,0x0001)
#define SAVE_READ_ERR_TO_MEDIA_PARM_P                  1

#define PATTERN_LENGTH_IN_BITS_PARM_C              16063     // (DEF,BitPttrnLen_TPARCD,16,0x00FF) (T509,BitPttrnLen_TPARCD,16,0x003F) (T510,BitPttrnLen_TPARCD,16,0x003F) (T532,BitPttrnLen_TPARCD,16,0x007F) (T551,BitPttrnLen_TPARCD,16,NA)
#define PATTERN_LENGTH_IN_BITS_PARM_P                  1     // (T591,BitPttrnLen_TPARCD,16,0x007F) (T597,BitPttrnLen_TPARCD,16,NA) (T618,PttrnLen_TPARCD,8,NA) (T623,BitPttrnLen_TPARCD,16,0x003F) (T625,BitPttrnLen_TPARCD,16,NA) (T1509,BitPttrnLen_TPARCD,16,0x003F) (T5509,BitPttrnLen_TPARCD,16,0x003F)

#define ERROR_REPORTING_MODE_PARM_C                16064     // (DEF,ErrRprtMode_TPARCD,16,0x0020)Bypass (DEF,ErrRprtMode_TPARCD,16,0x0040)Report (DEF,ErrRprtMode_TPARCD,16,0x0001)Return
#define ERROR_REPORTING_MODE_PARM_P                    1     // (T510,ErrRprtMode_TPARCD,16,0x0002)Bypass (T510,ErrRprtMode_TPARCD,16,0x0004)Report (T1647,ErrRprtMode_TPARCD,16,NA)

#define FILL_WRITE_BUFFER_PARM_C                   16065     // (DEF,BypasFillWrBuf_TPARCD,8,0x0001)Bypass
#define FILL_WRITE_BUFFER_PARM_P                       1

#define ERROR_LIMITS_ARE_PER_HD_PARM_C             16066     // (DEF,ErrLmtPerHd_TPARCD,8,0x0001)
#define ERROR_LIMITS_ARE_PER_HD_PARM_P                 1

#define ZONE_TO_TEST_PARM_C                        16067     // (DEF,TstZn_TPARCD,8,0x00FF) (T598,ZnToTst_TPARCD,32,NA) (T613,ZnTstSel_TPARCD,16,NA) (T630,TstZn_TPARCD,8,NA)
#define ZONE_TO_TEST_PARM_P                            1

#define MULTIPLIER_NUMBER_PARM_C                   16068     // (DEF,MultNum_TPARCD,8,0x00FF)
#define MULTIPLIER_NUMBER_PARM_P                       1

#define BLOCK_TRANSFER_COUNT_PARM_C                16069     // (DEF,BlkTrnsfrCnt_TPARCD,16,NA) (T551,BlkPerTrnsfr_TPARCD,16,NA)
#define BLOCK_TRANSFER_COUNT_PARM_P                    1

#define MAXIMUM_ERROR_COUNT_PARM_C                 16070     // (DEF,MxErrCnt_TPARCD,16,0x03FF)maxRecov (DEF,MxErrCnt_TPARCD,16,0xFC00)maxNonRecov (T520,MxErrCnt_TPARCD,16,NA) (T545,MxRdErr_TPARCD,16,NA) (T539,MxErrCnt_TPARCD,16,NA)
#define MAXIMUM_ERROR_COUNT_PARM_P                     1     // (T549,MxErrCnt_TPARCD,16,0x00FF) (T549,MxErrCnt_TPARCD,16,0x1F00) (T549,MxErrCnt_TPARCD,16,0xE000) (T550,MxErrCnt_TPARCD,16,NA) (T564,MxRcovErr_TPARCD,32,0x0003)(T630,MxErrCnt_TPARCD,16,NA)

#define PATTERN_LSW_PARM_C                         16071     // (DEF,Pttrn_TPARCD,32,NA)
#define PATTERN_LSW_PARM_P                             1

#define PATTERN_MSW_PARM_C                         16072     // (DEF,Pttrn_TPARCD,32,NA)
#define PATTERN_MSW_PARM_P                             1

#define LBA_INTERVAL_PARM_C                        16073     // (T511,LbaIntrvl_TPARCD,8,NA)
#define LBA_INTERVAL_PARM_P                            1

#define CONDITIONAL_FORMAT_PARM_C                  16074     // (T511,CondFmt_TPARCD,8,0x0001)
#define CONDITIONAL_FORMAT_PARM_P                      1

#define INIT_PATTERN_LENGTH_PARM_C                 16075     // (T511,InitPttrnLen_TPARCD,8,NA)
#define INIT_PATTERN_LENGTH_PARM_P                     1

#define FORMAT_MODE_PARM_C                         16076     // (T511,FmtMode_TPARCD,8,0x0001) (T714,FmtMode_TPARCD,8,NA) (T5509,SavBerFmt_TPARCD,16,NA)
#define FORMAT_MODE_PARM_P                             1

#define DEFECT_LIST_FORMAT_PARM_C                  16077     // (T511,DfctListFmt_TPARCD,8,NA) (T530,DfctListFmt_TPARCD,8,0x000F)
#define DEFECT_LIST_FORMAT_PARM_P                      1

#define INIT_PATTERN_MODIFIER_PARM_C               16078     // (T511,InitPttrnMod_TPARCD,8,NA)
#define INIT_PATTERN_MODIFIER_PARM_P                   1

#define COMPARE_OPTION_PARM_C                      16079     // (T511,CmprOptn_TPARCD,8,0x0001) (T611,CmprOptn_TPARCD,8,0x0003) (T707,CmprOptn_TPARCD,8,0x000F)
#define COMPARE_OPTION_PARM_P                          1

#define COMP_LIST_OF_GRWTH_DEFS_PARM_C             16080     // (T511,CmpltDfctList_TPARCD,8,0x0001)
#define COMP_LIST_OF_GRWTH_DEFS_PARM_P                 1

#define FORMAT_OPTIONS_VARIABLE_PARM_C             16081     // (T511,FmtOptn_TPARCD,8,0x0080) (T544,FmtOptn_TPARCD,8,NA)
#define FORMAT_OPTIONS_VARIABLE_PARM_P                 1

#define DISABLE_PRIMARY_LIST_PARM_C                16082     // (T511,DisblPrimList_TPARCD,8,0x0040)
#define DISABLE_PRIMARY_LIST_PARM_P                    1

#define DISABLE_CERTIFICATION_PARM_C               16083     // (T511,DisblCert_TPARCD,8,0x0020)
#define DISABLE_CERTIFICATION_PARM_P                   1

#define STOP_FMT_ON_DEFT_LST_ERR_PARM_C            16084     // (T511,StopFmtOptn_TPARCD,8,0x0010)
#define STOP_FMT_ON_DEFT_LST_ERR_PARM_P                1

#define INIT_PATTERN_PARM_C                        16085     // (T511,InitPttrn_TPARCD[0-7],16,NA)
#define INIT_PATTERN_PARM_P                            8

#define DISABLE_SAVING_PARAMS_PARM_C               16086     // (T511,DisblSavParm_TPARCD,8,0x0004)
#define DISABLE_SAVING_PARAMS_PARM_P                   1

#define IMMEDIATE_BIT_PARM_C                       16087     // (T511,ImdtOptn_TPARCD,8,0x0002)
#define IMMEDIATE_BIT_PARM_P                           1

#define HEAD_TO_FORMAT_PARM_C                      16088     // (T511,FmtHd_TPARCD,16,NA)
#define HEAD_TO_FORMAT_PARM_P                          1

#define END_TRACK_PARM_C                           16089     // (T511,EndTrk_TPARCD,32,NA)
#define END_TRACK_PARM_P                               2

#define HEAD_TO_FORMAT_MSW_PARM_C                  16090     // (T511,FmtHdMsk_TPARCD,32,NA)
#define HEAD_TO_FORMAT_MSW_PARM_P                      1

#define HEAD_TO_FORMAT_LSW_PARM_C                  16091     // (T511,FmtHdMsk_TPARCD,32,NA)
#define HEAD_TO_FORMAT_LSW_PARM_P                      1

#define START_TRACK_PARM_C                         16092     // (T511,StrtTrk_TPARCD,32,NA)
#define START_TRACK_PARM_P                             2

#define INIT_PATTERN_BIT_PARM_C                    16093     // (T511,InitPttrnOptn_TPARCD,8,NA) (T511,InitPttrnOptn_TPARCD,8,0x0008)
#define INIT_PATTERN_BIT_PARM_P                        1

#define MODE_COMMAND_PARM_C                        16094     // (T518,ModeCmd_TPARCD,16,0x0001) (T537,ModeCmd_TPARCD,16,0x0002)
#define MODE_COMMAND_PARM_P                            1

#define MODE_SENSE_OPTION_PARM_C                   16095     // (T518,ModeSnsOptn_TPARCD,8,0x0003)
#define MODE_SENSE_OPTION_PARM_P                       1

#define SAVE_MODE_PARAMETERS_PARM_C                16096     // (T518,SavModeParm_TPARCD,8,0x0001)
#define SAVE_MODE_PARAMETERS_PARM_P                    1

#define MODIFICATION_MODE_PARM_C                   16097     // (T518,ModMode_TPARCD,8,0x0001)
#define MODIFICATION_MODE_PARM_P                       1

#define PAGE_BYTE_AND_DATA_PARM_C                  16098     // (T518,PgBytDta_TPARCD[1-8],16,NA)
#define PAGE_BYTE_AND_DATA_PARM_P                      8

#define SUB_PAGE_CODE_PARM_C                       16099     // (T503,SubPgCode_TPARCD,16,NA) (T518,SubPgCode_TPARCD,16,0x000F)
#define SUB_PAGE_CODE_PARM_P                           1

#define PAGE_FORMAT_PARM_C                         16100     // (T503,PgFmt_TPARCD,16,NA) (T518,PgFmt_TPARCD,16,0x0001) (T537,PgFmt_TPARCD,16,0x0001)
#define PAGE_FORMAT_PARM_P                             1

#define UNIT_READY_PARM_C                          16101     // (DEF,UnitRdy_TPARCD,8,0x0001) (T1559,WaitRdy_TPARCD,16,0x0001)
#define UNIT_READY_PARM_P                              1 

#define DATA_TO_CHANGE_PARM_C                      16102     // (T518,DtaChg_TPARCD,8,0x0001)
#define DATA_TO_CHANGE_PARM_P                          1

#define VERIFY_MODE_PARM_C                         16103     // (T518,VfyMode_TPARCD,8,0x0001)
#define VERIFY_MODE_PARM_P                             1

#define MODE_SELECT_ALL_INITS_PARM_C               16104     // (T518,ModeSelInitr_TPARCD,8,NA) no functionality 
#define MODE_SELECT_ALL_INITS_PARM_P                   1

#define MODE_SENSE_INITIATOR_PARM_C                16105     // (T518,ModeSnsInitr_TPARCD,8,NA) no functionality 
#define MODE_SENSE_INITIATOR_PARM_P                    1

#define WRITE_STARTING_LBA_PARM_C                  16106     // (T520,WrStrtLba_TPARCD,64,NA)
#define WRITE_STARTING_LBA_PARM_P                      2

#define READ_STARTING_LBA_PARM_C                   16107     // (T520,RdStrtLba_TPARCD,64,NA)
#define READ_STARTING_LBA_PARM_P                       2

#define LINK_SCSI_WRITE_READ_CMD_PARM_C            16108     // (NA, Unused, NA, NA)
#define LINK_SCSI_WRITE_READ_CMD_PARM_P                1

#define SERP_FORMAT_FLAG_PARM_C                    16109     // (NA, Unused, NA, NA)
#define SERP_FORMAT_FLAG_PARM_P                        1

#define FAIL_ERROR_CODES_SCSIERR_PARM_C            16110     // (DEF,FailScsiErr_TPARCD,8,NA) (T507,FailScsiErr_TPARCD,8,0x0001) (T507,FailScsiErr_TPARCD,8,0x0002) (T509,FailScsiErr_TPARCD,8,0x0001) (T510,FailScsiErr_TPARCD,8,0x0001) (T549,FailScsiErr_TPARCD,8,0x0001) (T623,FailErrCodeScsiErr_TPARCD,8,0x0001) 
#define FAIL_ERROR_CODES_SCSIERR_PARM_P                1     // (T1509,FailScsiErr_TPARCD,8,0x0001) (T5509,FailScsiErr_TPARCD,8,0x0001)

#define RANDOM_DATA_PATTERN_PARM_C                 16111     // (NA, Unused, NA, NA)
#define RANDOM_DATA_PATTERN_PARM_P                     1

#define START_LBA_PARM_C                           16112     // (DEF,StrtLba_TPARCD,64,NA) (T510,StrtLba_TPARCD,64,0xFFFF) (T510,StrtLba_TPARCD,64,0xFFFF0000)
#define START_LBA_PARM_P                               2

#define OFFSET_INTO_LBA_PARM_C                     16113     // (T525,LbaOfst_TPARCD,16,NA)
#define OFFSET_INTO_LBA_PARM_P                         1

#define NUMBER_BYTES_TO_CORRUPT_PARM_C             16114     // (T525,NumBytCrrpt_TPARCD,16,NA)
#define NUMBER_BYTES_TO_CORRUPT_PARM_P                 1

#define EXPECTED_RESPONSE_PARM_C                   16115     // (T525,ExpctRspons_TPARCD,16,NA)
#define EXPECTED_RESPONSE_PARM_P                       1

#define CORRUPT_DATA_AS_SYMBOLS_PARM_C             16116     // (T525,CrrptDtaSymbl_TPARCD,8,0x0001)
#define CORRUPT_DATA_AS_SYMBOLS_PARM_P                 1

#define LBA_INCREMENT_PARM_C                       16117     // (T525,LbaInc_TPARCD,32,NA)
#define LBA_INCREMENT_PARM_P                           2

#define SKP_SPINUP_AFTER_SPINDWN_PARM_C            16118     // (T528,SkpSpinUp_TPARCD,8,0x0001)
#define SKP_SPINUP_AFTER_SPINDWN_PARM_P                1

#define MAX_POWER_SPIN_DOWN_TIME_PARM_C            16119     // (T528,MxPwrSpinDwnTm_TPARCD,16,NA)
#define MAX_POWER_SPIN_DOWN_TIME_PARM_P                1

#define MIN_POWER_SPIN_DOWN_TIME_PARM_C            16120     // (T528,MnPwrSpinDwnTm_TPARCD,16,NA)
#define MIN_POWER_SPIN_DOWN_TIME_PARM_P                1

#define ALLOW_SPEC_STATUS_COND_PARM_C              16121     // (T528,AlowSpecStatCond_TPARCD,8,0x0001)
#define ALLOW_SPEC_STATUS_COND_PARM_P                  1

#define SENSE_DATA_1_PARM_C                        16122     // (DEF,SnsDta1_TPARCD[0-3],8,NA)
#define SENSE_DATA_1_PARM_P                            4

#define SENSE_DATA_2_PARM_C                        16123     // (DEF,SnsDta2_TPARCD[0-3],8,NA)
#define SENSE_DATA_2_PARM_P                            4

#define SENSE_DATA_3_PARM_C                        16124     // (DEF,SnsDta3_TPARCD[0-3],8,NA)
#define SENSE_DATA_3_PARM_P                            4

#define FAIL_ON_SLIPPED_TRK_PARM_C                 16125     // (T529,FailSlipTrk_TPARCD,8,0x0001)
#define FAIL_ON_SLIPPED_TRK_PARM_P                     1

#define PAD_D_GLIST_PARM_C                         16126     // (T529,PadDfctGlist_TPARCD,16,0x0001)
#define PAD_D_GLIST_PARM_P                             1

#define CONDITIONAL_REWRITE_PARM_C                 16127     // (T529,CondReWr_TPARCD,8,0x0001)
#define CONDITIONAL_REWRITE_PARM_P                     1

#define GLIST_OPTION_PARM_C                        16128     // (T529,GlistOptn_TPARCD,8,0x0001) (T529,GlistOptn_TPARCD,8,0x0002) (T529,GlistOptn_TPARCD,8,0x0004) (T529,GlistOptn_TPARCD,8,0x000F) (T564,EnblGlistChk_TPARCD,16,NA)
#define GLIST_OPTION_PARM_P                            1

#define SERVO_DEFECT_FUNCTION_PARM_C               16129     // (T529,SvoDfctFunc_TPARCD,16,0x000F)
#define SERVO_DEFECT_FUNCTION_PARM_P                   1

#define MAX_SERVO_DEFECTS_PARM_C                   16130     // (T529,MxSvoDfct_TPARCD,16,NA)
#define MAX_SERVO_DEFECTS_PARM_P                       1

#define WEDGES_PER_TRK_PARM_C                      16131     // (T529,SvoWdgPerTrk_TPARCD,16,NA)
#define WEDGES_PER_TRK_PARM_P                          1

#define PAD_CYLS_PARM_C                            16132     // (T529,PadCyl_TPARCD,8,0x00FF)
#define PAD_CYLS_PARM_P                                1

#define PAD_500_BYTES_UNITS_PARM_C                 16133     // (T529,Pad500BytUnit_TPARCD,16,0x0001) (T529,Pad500BytUnit_TPARCD,16,0x0002) (T529,Pad500BytUnit_TPARCD,16,0x00FF)
#define PAD_500_BYTES_UNITS_PARM_P                     1

#define DISP_1_WEDGE_SERVO_FLAWS_PARM_C            16134     // (T529,DispWdgSflw_TPARCD,16,0x0001)
#define DISP_1_WEDGE_SERVO_FLAWS_PARM_P                1

#define SLIPPED_TRACKS_SPEC_PARM_C                 16135     // (T529,SlipTrkSpec_TPARCD,16,0x00FF)
#define SLIPPED_TRACKS_SPEC_PARM_P                     1

#define SLIPPED_TRACKS_HEAD_NUM_PARM_C             16136     // (T529,SlipTrkHdNum_TPARCD,16,0x00FF)
#define SLIPPED_TRACKS_HEAD_NUM_PARM_P                 1

#define GRADING_OUT_PUT_PARM_C                     16137     // (NA, Unused, NA, NA)
#define GRADING_OUT_PUT_PARM_P                         1

#define MULTIPLY_BY_10_PARM_C                      16138     // (T530,Mult10_TPARCD,8,NA)
#define MULTIPLY_BY_10_PARM_P                          1

#define MAX_DEFECTIVE_SECTORS_PARM_C               16139     // (T530,MxDfctSctr_TPARCD,16,NA)
#define MAX_DEFECTIVE_SECTORS_PARM_P                   1

#define MAX_DEFECTIVE_SECS_HEAD_PARM_C             16140     // (T530,MxDfctSctrHd_TPARCD,16,NA)
#define MAX_DEFECTIVE_SECS_HEAD_PARM_P                 1

#define MAX_DEFECTIVE_SECS_ZONE_PARM_C             16141     // (T530,MxDfctSctrZn_TPARCD,16,NA)
#define MAX_DEFECTIVE_SECS_ZONE_PARM_P                 1

#define MAX_DEFECTIVE_SECS_CYL_PARM_C              16142     // (T530,MxDfctSctrCyl_TPARCD,16,NA)
#define MAX_DEFECTIVE_SECS_CYL_PARM_P                  1

#define MAX_CYL_DISPLAYED_PARM_C                   16143     // (T530,MxCylDisp_TPARCD,16,NA)
#define MAX_CYL_DISPLAYED_PARM_P                       1

#define SET_TO_FAIL_PARM_C                         16144     // (T530,SetToFail_TPARCD,8,0x0010) (T539,SetToFail_TPARCD,8,0x0001)
#define SET_TO_FAIL_PARM_P                             1

#define MIN_ENTRIES_IN_DST_PARM_C                  16145     // (T530,MnEntryDst_TPARCD,16,NA)
#define MIN_ENTRIES_IN_DST_PARM_P                      1

#define MAX_PERCENT_DEFECTIVE_PARM_C               16146     // (T530,MxPrctDfct_TPARCD,16,NA)
#define MAX_PERCENT_DEFECTIVE_PARM_P                   1

#define MIN_PERCENT_ENTRIES_PARM_C                 16147     // (T530,MnPrctEntry_TPARCD,16,NA)
#define MIN_PERCENT_ENTRIES_PARM_P                     1

#define WRITE_READ_REPORT_PARM_C                   16148     // (T531,WrRdRprt_TPARCD,32,0x0002) no functionality (T531,WrRdRprt_TPARCD,32,0x00FF0000)
#define WRITE_READ_REPORT_PARM_P                       2

#define SELECTED_RESULTS_PARM_C                    16149     // (T531,SelRslt_TPARCD,16,0x0001)
#define SELECTED_RESULTS_PARM_P                        1

#define TEST_NUMBER_PARM_C                         16150     // (T531,TstNum_TPARCD[0-1],16,NA) (T730,TstNum_TPARCD[0-1],16,NA)
#define TEST_NUMBER_PARM_P                             2

#define STORE_PARAM_PARM_C                         16151     // (T531,StoreParm_TPARCD[0-1],16,NA)
#define STORE_PARAM_PARM_P                             2

#define STORE_VALUE_PARM_C                         16152     // (T531,StoreVal_TPARCD[0-1],16,NA)
#define STORE_VALUE_PARM_P                             2

#define LOC_TEST_PARM_C                            16153     // (T531,LocTst_TPARCD[0-1],16,NA)
#define LOC_TEST_PARM_P                                2

#define TIME_MODE_FLAG_PARM_C                      16154     // (T532,TmModeFlag_TPARCD,8,0x0001)
#define TIME_MODE_FLAG_PARM_P                          1

#define EXTENDED_LIMITS_PARM_C                     16155     // (T510,ExtdLmt_TPARCD,8,NA) no functionality (T532,ExtdLmt_TPARCD,8,0x0001)
#define EXTENDED_LIMITS_PARM_P                         1

#define TRANSFER_WIDTH_PARM_C                      16156     // (NA, Unused, NA, NA)
#define TRANSFER_WIDTH_PARM_P                          1

#define PROTOCOL_OPTIONS_EN_PARM_C                 16157     // (NA, Unused, NA, NA)
#define PROTOCOL_OPTIONS_EN_PARM_P                     1

#define SDTR_MESSAGE_BYTE_1_PARM_C                 16158     // (NA, Unused, NA, NA)
#define SDTR_MESSAGE_BYTE_1_PARM_P                     1

#define SDTR_MESSAGE_BYTE_2_PARM_C                 16159     // (NA, Unused, NA, NA)
#define SDTR_MESSAGE_BYTE_2_PARM_P                     1

#define INTERFACE_MODE_PARM_C                      16160     // (NA, Unused, NA, NA)
#define INTERFACE_MODE_PARM_P                          1

#define MONITOR_TIME_MS_PARM_C                     16161     // (NA, Unused, NA, NA)
#define MONITOR_TIME_MS_PARM_P                         1

#define SLEW_RATE_CHANGE_PARM_C                    16162     // (NA, Unused, NA, NA)
#define SLEW_RATE_CHANGE_PARM_P                        1

#define DISPLAY_SLEW_RATE_PARM_C                   16163     // (T598,DispSkewRat_TPARCD,8,NA)
#define DISPLAY_SLEW_RATE_PARM_P                       1

#define CHK_TRANSFER_RATE_PARM_C                   16164     // (NA, Unused, NA, NA)
#define CHK_TRANSFER_RATE_PARM_P                       1

#define FC_SAS_TRANSFER_RATE_PARM_C                16165     // (DEF,FcSasTrnsfrRat_TPARCD,16,NA)
#define FC_SAS_TRANSFER_RATE_PARM_P                    1

#define BAUD_RATE_PARM_C                           16166     // (T535,BpsRat_TPARCD,16,NA)
#define BAUD_RATE_PARM_P                               1

#define EXPECTED_FW_REV_PARM_C                     16167     // (NA, Unused, NA, NA)
#define EXPECTED_FW_REV_PARM_P                         1

#define DRIVE_TYPE_PARM_C                          16168     // (T535,DrvTyp_TPARCD,16,NA)
#define DRIVE_TYPE_PARM_P                              1

#define REG_VALUE_PARM_C                           16169     // (T535,RegVal_TPARCD,16,NA)
#define REG_VALUE_PARM_P                               1

#define MODE_PAGES_BYPASSED_1_PARM_C               16170     // (T537,ModePgBypas1_TPARCD,16,NA)
#define MODE_PAGES_BYPASSED_1_PARM_P                   1

#define MODE_PAGES_BYPASSED_2_PARM_C               16171     // (T537,ModePgBypas2_TPARCD,16,NA)
#define MODE_PAGES_BYPASSED_2_PARM_P                   1

#define MODE_PAGES_BYPASSED_3_PARM_C               16172     // (T537,ModePgBypas3_TPARCD,16,NA)
#define MODE_PAGES_BYPASSED_3_PARM_P                   1

#define COMMAND_WORD_1_PARM_C                      16173     // (T538,CmdWrd_TPARCD[0],16,NA) (T538,CmdWrdLsw_TPARCD[0],16,0xFF00)
#define COMMAND_WORD_1_PARM_P                          1

#define COMMAND_WORD_2_PARM_C                      16174     // (T538,CmdWrd_TPARCD[1],16,NA)
#define COMMAND_WORD_2_PARM_P                          1

#define COMMAND_WORD_3_PARM_C                      16175     // (T538,CmdWrd_TPARCD[2],16,NA)
#define COMMAND_WORD_3_PARM_P                          1

#define COMMAND_WORD_4_PARM_C                      16176     // (T538,CmdWrd_TPARCD[3],16,NA)
#define COMMAND_WORD_4_PARM_P                          1

#define COMMAND_WORD_5_PARM_C                      16177     // (T538,CmdWrd_TPARCD[4],16,NA)
#define COMMAND_WORD_5_PARM_P                          1

#define COMMAND_WORD_6_PARM_C                      16178     // (T538,CmdWrd_TPARCD[5],16,NA)
#define COMMAND_WORD_6_PARM_P                          1

#define SELECT_COPY_PARM_C                         16179     // (T538,SelCpy_TPARCD,8,0x000F) (T538,SelCpy_TPARCD,8,0x00FF)
#define SELECT_COPY_PARM_P                             1

#define READ_CAPACITY_PARM_C                       16180     // (T538,RdCpcty_TPARCD,8,0x00FF)
#define READ_CAPACITY_PARM_P                           1

#define CHK_OPEN_LATCH_RETRY_CNT_PARM_C            16181     // (T538,ChkOpenLtchRtryCnt_TPARCD,8,0x0001)
#define CHK_OPEN_LATCH_RETRY_CNT_PARM_P                1

#define SUPRESS_RESULTS_PARM_C                     16182     // (T538,SuprsRslt_TPARCD,8,0x0001)
#define SUPRESS_RESULTS_PARM_P                         1

#define USE_CMD_ATTR_TST_PARMS_PARM_C              16183     // (T538,UseCmdAttrTstParm_TPARCD,8,0x0001)
#define USE_CMD_ATTR_TST_PARMS_PARM_P                  1

#define WRITE_SECTOR_CMD_ALL_HDS_PARM_C            16184     // (T538,WrSctrCmdHd_TPARCD,8,0x0001) (T638,WrSctrCmdHd_TPARCD,8,NA)
#define WRITE_SECTOR_CMD_ALL_HDS_PARM_P                1

#define TRANSFER_OPTION_PARM_C                     16185     // (T538,TrnsfrOptn_TPARCD,16,0x0001) (T538,TrnsfrOptn_TPARCD,16,0x0002) (T538,TrnsfrOptn_TPARCD,16,0x00F0) (T538,TrnsfrOptn_TPARCD,16,0x0300) (T538,TrnsfrOptn_TPARCD,16,0xF000)
#define TRANSFER_OPTION_PARM_P                         1

#define TRANSFER_LENGTH_PARM_C                     16186     // (DEF,TrnsfrLen_TPARCD,16,NA)
#define TRANSFER_LENGTH_PARM_P                         1

#define CYLINDER_MODE_PARM_C                       16187     // (T539,CylMode_TPARCD,8,0x0001) (T618,CylMode_TPARCD,8,0x0001)
#define CYLINDER_MODE_PARM_P                           1

#define VBAR_ZONE_SETTINGS_1_PARM_C                16188     // (T539,VarZnSetg1_TPARCD,16,0x00FF) (T598,StrtZn_TPARCD,16,NA)
#define VBAR_ZONE_SETTINGS_1_PARM_P                    1

#define VBAR_ZONE_SETTINGS_2_PARM_C                16189     // (T539,VarZnSetg2_TPARCD,16,NA) (T539,VarZnSetg2_TPARCD,16,0x000F) (T539,VarZnSetg2_TPARCD,16,0x00F0) (T539,VarZnSetg2_TPARCD,16,0x00FF)(T598,LastZn_TPARCD,16,NA)
#define VBAR_ZONE_SETTINGS_2_PARM_P                    1

#define ZONE_SETTING_MODE_PARM_C                   16190     // (T539,ZnSetgMode_TPARCD,8,0x0001)
#define ZONE_SETTING_MODE_PARM_P                       1

#define BUFFER_SIZE_PARM_C                         16191     // (DEF,BufSz_TPARCD,16,NA)
#define BUFFER_SIZE_PARM_P                             1

#define WWN_NETWORK_PARM_C                         16192     // (T542,WwnNet_TPARCD[0-3],16,NA)
#define WWN_NETWORK_PARM_P                             4

#define FILTER_TAP_PARM_C                          16193     // (NA, Unused, NA, NA)
#define FILTER_TAP_PARM_P                              1

#define CONTACT_DETECT_PARAMS_PARM_C               16194     // (NA, Unused, NA, NA)
#define CONTACT_DETECT_PARAMS_PARM_P                   1

#define SELECT_POS_ERROR_VALUE_PARM_C              16195     // (NA, Unused, NA, NA)
#define SELECT_POS_ERROR_VALUE_PARM_P                  1

#define DISABLE_SEEK_PARM_C                        16196     // (NA, Unused, NA, NA)
#define DISABLE_SEEK_PARM_P                            1

#define XFER_LIMIT_PARM_C                          16197     // (NA, Unused, NA, NA)
#define XFER_LIMIT_PARM_P                              1

#define HEATING_LIMIT_PARM_C                       16198     // (NA, Unused, NA, NA)
#define HEATING_LIMIT_PARM_P                           1

#define START_WEDGE_FOR_HEAT_PARM_C                16199     // (NA, Unused, NA, NA)
#define START_WEDGE_FOR_HEAT_PARM_P                    1

#define NUM_WEDGES_TO_HEAT_PARM_C                  16200     // (NA, Unused, NA, NA)
#define NUM_WEDGES_TO_HEAT_PARM_P                      1

#define COURSE_START_HEATER_DAC_PARM_C             16201     // (NA, Unused, NA, NA)
#define COURSE_START_HEATER_DAC_PARM_P                 1

#define MAX_CONTACT_HEATER_PARM_C                  16202     // (NA, Unused, NA, NA)
#define MAX_CONTACT_HEATER_PARM_P                      1

#define COURSE_STEP_SIZE_PARM_C                    16203     // (NA, Unused, NA, NA)
#define COURSE_STEP_SIZE_PARM_P                        1

#define FINE_STEP_SIZE_PARM_C                      16204     // (NA, Unused, NA, NA)
#define FINE_STEP_SIZE_PARM_P                          1

#define FINE_CONTACT_BACKOFF_PARM_C                16205     // (NA, Unused, NA, NA)
#define FINE_CONTACT_BACKOFF_PARM_P                    1

#define NUM_SAMPLES_TO_AVE_PARM_C                  16206     // (NA, Unused, NA, NA)
#define NUM_SAMPLES_TO_AVE_PARM_P                      1

#define CONTACT_VARIANCE_FACTOR_PARM_C             16207     // (NA, Unused, NA, NA)
#define CONTACT_VARIANCE_FACTOR_PARM_P                 1

#define MIN_NUM_VARIANCE_SAMPLES_PARM_C            16208     // (NA, Unused, NA, NA)
#define MIN_NUM_VARIANCE_SAMPLES_PARM_P                1

#define NUM_VARIANCE_SMPL_TO_LAG_PARM_C            16209     // (NA, Unused, NA, NA)
#define NUM_VARIANCE_SMPL_TO_LAG_PARM_P                1

#define DISABLE_ECC_ON_FLY_SERVO_PARM_C            16210     // (T545,DisblEccFlySvo_TPARCD,8,NA) no functionality
#define DISABLE_ECC_ON_FLY_SERVO_PARM_P                1

#define BASE_CYLINDER_PARM_C                       16211     // (T545,BaseCyl_TPARCD,16,0x3FFF)
#define BASE_CYLINDER_PARM_P                           1

#define CYLINDER_INTERVAL_PARM_C                   16212     // (T545,CylIntrvl_TPARCD,16,NA)
#define CYLINDER_INTERVAL_PARM_P                       1

#define SCAN_MODE_PARM_C                           16213     // (T549,ScnMode_TPARCD,8,0x0001)
#define SCAN_MODE_PARM_P                               1

#define CHK_OFF_TRACK_FAULTS_PARM_C                16214     // (T549,ChkOffTrkFlt_TPARCD,8,0x0001)
#define CHK_OFF_TRACK_FAULTS_PARM_P                    1

#define SEEK_TIME_DELTA_PARM_C                     16215     // (T549,SkTmDlta_TPARCD,8,0x0001)
#define SEEK_TIME_DELTA_PARM_P                         1

#define SAVE_SEEK_TIME_PARM_C                      16216     // (T549,SavSkTm_TPARCD,8,0x0001)
#define SAVE_SEEK_TIME_PARM_P                          1

#define SERVO_RAM_ADDRESS_PARM_C                   16217     // (T549,SvoRamAddr_TPARCD,16,NA) (T549,SvoRamAddr_TPARCD,16,0x00FF) (T549,SvoRamAddr_TPARCD,16,0xFF00)
#define SERVO_RAM_ADDRESS_PARM_P                       1

#define HEAD_SELECTION_PARM_C                      16218     // (T549,HdSel_TPARCD,8,0x0001) (T714,HdSel_TPARCD,8,NA)
#define HEAD_SELECTION_PARM_P                          1

#define REPORT_SEEK_TIME_PARM_C                    16219     // (T549,RprtSkTm_TPARCD,8,0x0001)
#define REPORT_SEEK_TIME_PARM_P                        1

#define BYTES_PER_TRANSFER_PARM_C                  16220     // (DEF,BytTrnsfr_TPARCD,32,NA)
#define BYTES_PER_TRANSFER_PARM_P                      2

#define NUMBER_OF_TRANSFER_PARM_C                  16221     // (T550,NumTrnsfr_TPARCD,32,NA) (T558,NumTrnsfr_TPARCD,32,0x00FF)
#define NUMBER_OF_TRANSFER_PARM_P                      2

#define COMBINED_ERROR_COUNT_PARM_C                16222     // (T550,CmbndErrCnt_TPARCD,16,NA)
#define COMBINED_ERROR_COUNT_PARM_P                    1

#define SET_BYTE_CHK_PARM_C                        16223     // (T510,SetBytChk_TPARCD,8,0x0001) (T551,SetBytChk_TPARCD,8,0x0001)
#define SET_BYTE_CHK_PARM_P                            1

#define BLOCKS_TO_TRANS_PARM_C                     16224     // (T510,NumLbaPerTrnsfr_TPARCD,32,NA) (T551,TtlBlkTrnsfr_TPARCD,32,0xFFFF) (T551,TtlBlkTrnsfr_TPARCD,32,0xFFFF0000) (T623,BlkToTrnsfr_TPARCD,32,NA)
#define BLOCKS_TO_TRANS_PARM_P                         2

#define CALC_CHECK_SUM_PARM_C                      16225     // (T555,CalcChkSum_TPARCD,16,NA) (T555,CalcChkSum_TPARCD,16,0x0001)
#define CALC_CHECK_SUM_PARM_P                          1

#define CHECK_SUM_OFFSET_PARM_C                    16226     // (T555,ChkSumOfst_TPARCD,16,NA)
#define CHECK_SUM_OFFSET_PARM_P                        1

#define MODIFY_APM_BYTE_NUM_PARM_C                 16227     // (T555,ModApBytNum_TPARCD,16,NA)
#define MODIFY_APM_BYTE_NUM_PARM_P                     1

#define APM_INPUT_VALUE_PARM_C                     16228     // (T555,ApmInptVal_TPARCD,16,NA)
#define APM_INPUT_VALUE_PARM_P                         1

#define START_AP_READ_ADDR_PARM_C                  16229     // (T555,StrtApRdAddr_TPARCD,16,NA)
#define START_AP_READ_ADDR_PARM_P                      1

#define AP_READ_BYTE_CNT_PARM_C                    16230     // (T555,ApRdBytCnt_TPARCD,16,NA)
#define AP_READ_BYTE_CNT_PARM_P                        1

#define FAIL_SMART_ERR_PARM_C                      16231     // (T556,FailSmrtErr_TPARCD,8,NA)
#define FAIL_SMART_ERR_PARM_P                          1

#define SAVE_AND_COMPARE_PARM_C                    16232     // (T556,SavCmpr_TPARCD,8,0x0010)GetData (T556,SavCmpr_TPARCD,8,0x0020)CompareData
#define SAVE_AND_COMPARE_PARM_P                        1

#define MIN_HEAD_AMP_PARM_C                        16233     // (T556,MnHdAmp_TPARCD,16,NA)
#define MIN_HEAD_AMP_PARM_P                            1

#define MAX_HEAD_AMP_PARM_C                        16234     // (T556,MxHdAmp_TPARCD,16,NA)
#define MAX_HEAD_AMP_PARM_P                            1

#define MAX_NORM_COEF_PARM_C                       16235     // (T556,MxNrmlCoef_TPARCD,16,NA)
#define MAX_NORM_COEF_PARM_P                           1

#define NUM_MEASUREMENTS_PARM_C                    16236     // (T556,NumMeas_TPARCD,16,0x00FF)
#define NUM_MEASUREMENTS_PARM_P                        1

#define MSB_BYTES_TRANSFER_PARM_C                  16237     // (DEF,BytTrnsfr_TPARCD,32,NA)
#define MSB_BYTES_TRANSFER_PARM_P                      1

#define LSB_BYTES_TRANSFER_PARM_C                  16238     // (DEF,BytTrnsfr_TPARCD,32,NA)
#define LSB_BYTES_TRANSFER_PARM_P                      1

#define FLY_HEIGHT_DELTA_OD_PARM_C                 16239     // (T556,FlyHghtOd_TPARCD,16,NA)
#define FLY_HEIGHT_DELTA_OD_PARM_P                     1

#define FLY_HEIGHT_DELTA_ID_PARM_C                 16240     // (T556,FlyHghtId_TPARCD,16,NA)
#define FLY_HEIGHT_DELTA_ID_PARM_P                     1

#define DATE_FORMAT_PARM_C                         16241     // (T557,DatFmt_TPARCD,8,NA)
#define DATE_FORMAT_PARM_P                             1

#define ETF_DATE_OFFSET_PARM_C                     16242     // (T557,EtfDatOfst_TPARCD,16,NA)
#define ETF_DATE_OFFSET_PARM_P                         1

#define MAX_ETF_DAYS_DELTA_PARM_C                  16243     // (T557,MxEtfDayDlta_TPARCD,16,NA)
#define MAX_ETF_DAYS_DELTA_PARM_P                      1

#define CURRENT_MONTH_YEAR_PARM_C                  16244     // (T557,CrrntMoYr_TPARCD,16,NA)
#define CURRENT_MONTH_YEAR_PARM_P                      1

#define CURRENT_DAY_WEEK_PARM_C                    16245     // (T557,CrrntDayWk_TPARCD,16,NA)
#define CURRENT_DAY_WEEK_PARM_P                        1

#define CURRENT_YEAR_PARM_C                        16246     // (T557,CrrntYr_TPARCD,16,NA)
#define CURRENT_YEAR_PARM_P                            1

#define NO_TIMING_MARK_DET_PARM_C                  16247     // (DEF,NoTmd_TPARCD,16,NA)
#define NO_TIMING_MARK_DET_PARM_P                      1

#define MAX_NO_TIM_MARK_DET_PARM_C                 16248     // (T561,MxNoTmd_TPARCD,16,NA)
#define MAX_NO_TIM_MARK_DET_PARM_P                     1

#define BAD_INDEX_DETECTED_ADDR_PARM_C             16249     // (T561,BadIdxDtctAddr_TPARCD,16,NA)
#define BAD_INDEX_DETECTED_ADDR_PARM_P                 1

#define MAX_BAD_INDEX_DETECTED_PARM_C              16250     // (T561,MxBadIdxDtct_TPARCD,16,NA)
#define MAX_BAD_INDEX_DETECTED_PARM_P                  1

#define SERVO_UNSAFES_ADDR_PARM_C                  16251     // (T561,SvoUnsfAddr_TPARCD,16,NA)
#define SERVO_UNSAFES_ADDR_PARM_P                      1

#define MAX_SERVO_UNSAFES_PARM_C                   16252     // (T561,MxSvoUnsf_TPARCD,16,NA)
#define MAX_SERVO_UNSAFES_PARM_P                       1

#define TEST_SECTOR_PARM_C                         16253     // (T561,TstSctr_TPARCD,16,0x00FF)
#define TEST_SECTOR_PARM_P                             1

#define SECTOR_WRT_RD_COUNT_PARM_C                 16254     // (T561,SctrWrRdCnt_TPARCD,16,0x00FF)
#define SECTOR_WRT_RD_COUNT_PARM_P                     1

#define INSTABILITY_THRESHOLD_PARM_C               16255     // (T561,InstbltyThrsh_TPARCD,16,0x00FF)
#define INSTABILITY_THRESHOLD_PARM_P                   1

#define ENABLE_32_BIT_ADDR_PARM_C                  16256     // (T561,Enbl32BitAddr_TPARCD,8,NA)
#define ENABLE_32_BIT_ADDR_PARM_P                      1

#define COUNTER_TYPE_PARM_C                        16257     // (T561,CntrTyp_TPARCD,8,NA)
#define COUNTER_TYPE_PARM_P                            1

#define SUPPRESS_REPORT_DATA_PARM_C                16258     // (T564,SuprsRprtDta_TPARCD,8,0x0001)
#define SUPPRESS_REPORT_DATA_PARM_P                    1

#define TEMPERATURE_PARM_C                         16259     // (T564,Tmp_TPARCD,16,0x00FF)
#define TEMPERATURE_PARM_P                             1

#define BUZZ_COUNT_PARM_C                          16260     // (T564,BuzCnt_TPARCD,16,0x00FF)
#define BUZZ_COUNT_PARM_P                              1

#define BAD_ADDRESS_COUNT_PARM_C                   16261     // (T564,BadAddrCnt_TPARCD,16,NA)
#define BAD_ADDRESS_COUNT_PARM_P                       1

#define FLY_HEIGHT_MEAS_PARM_C                     16262     // (T564,FlyHghtMeas_TPARCD,8,0x00FF)
#define FLY_HEIGHT_MEAS_PARM_P                         1

#define MAX_REALLOCATED_SECTORS_PARM_C             16263     // (T564,MxReAllocSctr_TPARCD,8,0x00FF)
#define MAX_REALLOCATED_SECTORS_PARM_P                 1

#define ONE_THIRD_SEEK_PARM_C                      16264     // (T564,Mx1ThrdSk_TPARCD,8,0x00FF)
#define ONE_THIRD_SEEK_PARM_P                          1

#define ONE_TRACK_PARM_C                           16265     // (T564,Mx1TrkWrSkTm_TPARCD,8,0x00FF)
#define ONE_TRACK_PARM_P                               1

#define TA_WUS_SPEC_PARM_C                         16266     // (T564,TaWusSpec_TPARCD,16,NA)
#define TA_WUS_SPEC_PARM_P                             1

#define SRVO_UNSF_SPEC_PARM_C                      16267     // (T564,SvoUnsfSpec_TPARCD,8,0x00FF)
#define SRVO_UNSF_SPEC_PARM_P                          1

#define MAX_READ_ERRORS_PARM_C                     16268     // (T618,MxRdErr_TPARCD,16,NA) (T564,MxRdErr_TPARCD,16,0x00FF)
#define MAX_READ_ERRORS_PARM_P                         1

#define BAD_SAMPLE_CNT_PARM_C                      16269     // (T564,BadSampCnt_TPARCD,16,NA)
#define BAD_SAMPLE_CNT_PARM_P                          1

#define SELECTED_HEAD_PARM_C                       16270     // (T564,HdSel_TPARCD,8,0x0007)
#define SELECTED_HEAD_PARM_P                           1

#define EXTREME_HEADS_PARM_C                       16271     // (T564,ExtrmHd_TPARCD,8,0x0001)
#define EXTREME_HEADS_PARM_P                           1

#define SMART_ATTRIBUTE_PARM_C                     16272     // (T564,SmrtAttr_TPARCD,8,0x000F) no functionality
#define SMART_ATTRIBUTE_PARM_P                         1

#define SOME_HEADS_PARM_C                          16273     // (T564,Hd_TPARCD,8,0x0001)
#define SOME_HEADS_PARM_P                              1

#define CHECK_ALL_SELECTED_HDS_PARM_C              16274     // (T564,ChkHdSel_TPARCD,8,0x0003)
#define CHECK_ALL_SELECTED_HDS_PARM_P                  1

#define MAX_THERMAL_ASP_PARM_C                     16275     // (T564,MxTa_TPARCD,8,0x00FF)
#define MAX_THERMAL_ASP_PARM_P                         1

#define SHOW_ZONE_TABLE_PARM_C                     16276     // (T569,ShowZnTbl_TPARCD,16,0x0001) (T628,ShowZnTbl_TPARCD,16,0x000F)
#define SHOW_ZONE_TABLE_PARM_P                         1

#define SHOW_DRIVE_CONFIG_PARM_C                   16277     // (T569,ShowDrvCnfg_TPARCD,16,0x0001) (T628,ShowDrvCnfg_TPARCD,16,0x000F)
#define SHOW_DRIVE_CONFIG_PARM_P                       1

#define SHOW_ETF_FILE_LEN_PARM_C                   16278     // (T569,ShowEtfFileLen_TPARCD,16,0x0001)
#define SHOW_ETF_FILE_LEN_PARM_P                       1

#define ENABLE_PFAST_PARM_C                        16279     // (T591,EnblPfast_TPARCD,8,0x0001) (T598,EnblPfast_TPARCD,8,NA)
#define ENABLE_PFAST_PARM_P                            1

#define ENABLE_EXTENDED_RES_PARM_C                 16280     // (T591,EnblExtdRslt_TPARCD,8,0x0001) (T621,EnblExtdRslt_TPARCD,8,0x0001)
#define ENABLE_EXTENDED_RES_PARM_P                     1

#define BYPASS_RPT_REC0V_ERRS_PARM_C               16281     // (T591,BypasRprtRcovErr_TPARCD,8,0x0020)
#define BYPASS_RPT_REC0V_ERRS_PARM_P                   1

#define RPT_REC0V_ERRS_IMMED_PARM_C                16282     // (T591,RprtRcovErrImdt_TPARCD,8,0x0010)
#define RPT_REC0V_ERRS_IMMED_PARM_P                    1

#define LBA_LSW_PARM_C                             16283     // (DEF,StrtLba_TPARCD,64,NA) (T510,Blk_TPARCD,64,NA)
#define LBA_LSW_PARM_P                                 1

#define LBA_MSW_PARM_C                             16284     // (DEF,StrtLba_TPARCD,64,NA) (T510,Blk_TPARCD,64,NA)
#define LBA_MSW_PARM_P                                 1

#define BLKS_TO_TRANS_FIRST_PARM_C                 16285     // (T591,BlkTrnsfrPass1_TPARCD,16,NA)
#define BLKS_TO_TRANS_FIRST_PARM_P                     1

#define BLKS_TO_TRANS_SECOND_PARM_C                16286     // (T591,BlkTrnsfrPass2_TPARCD,16,NA)
#define BLKS_TO_TRANS_SECOND_PARM_P                    1

#define DISC_IO_PASSES_CNT_PARM_C                  16287     // (T591,DiscIoPassCnt_TPARCD,8,0x00FF)
#define DISC_IO_PASSES_CNT_PARM_P                      1

#define CMD_IO_PASSES_CNT_PARM_C                   16288     // (T591,CmdIoPassCnt_TPARCD,8,0x00FF)
#define CMD_IO_PASSES_CNT_PARM_P                       1

#define BUFFER_IO_PASSES_CNT_PARM_C                16289     // (T591,BufIoPassCnt_TPARCD,8,0x00FF)
#define BUFFER_IO_PASSES_CNT_PARM_P                    1

#define RESELECT_IO_PASSES_CNT_PARM_C              16290     // (T591,ReSelIoPassCnt_TPARCD,8,0x00FF)
#define RESELECT_IO_PASSES_CNT_PARM_P                  1

#define CORRUPT_SELECT_PARM_C                      16291     // (T606,CrrptSel_TPARCD,8,NA)
#define CORRUPT_SELECT_PARM_P                          1

#define INIT_MFG_INFO_FILE_PARM_C                  16292     // (T595,InitMfgInfoFile_TPARCD,8,0x0001)
#define INIT_MFG_INFO_FILE_PARM_P                      1

#define MFG_INFO_FILE_FMT_PARM_C                   16293     // (T595,MfgInfoFileFmt_TPARCD,8,0x0001)
#define MFG_INFO_FILE_FMT_PARM_P                       1

#define ATTRIBUTE_MODE_PARM_C                      16294     // (DEF,AttrMode_TPARCD,8,NA) (T595,AttrMode_TPARCD,8,0x0007) (T595,AttrMode_TPARCD,8,0x000F)
#define ATTRIBUTE_MODE_PARM_P                          1

#define OPTIONS_WORD1_PARM_C                       16295     // (DEF,OptnWrd1_TPARCD,16,NA) (T510,OptnWrd1_TPARCD,16,0x0002) (T510,OptnWrd1_TPARCD,16,0x0004) (T510,OptnWrd1_TPARCD,16,0x0008) (T510,OptnWrd1_TPARCD,16,0x0010) (T510,OptnWrd1_TPARCD,16,0xFFFF)
#define OPTIONS_WORD1_PARM_P                           1     // (T595,OptnWrd1_TPARCD,16,0x0001) (T735,TstOptn_TPARCD,16,NA)

#define OPTIONS_WORD2_PARM_C                       16296     // (DEF,OptnWrd2_TPARCD,16,NA) (T510,OptnWrd2_TPARCD,16,0x0001) (T510,OptnWrd2_TPARCD,16,0x0002) (T510,OptnWrd2_TPARCD,16,0xFFFF)
#define OPTIONS_WORD2_PARM_P                           1

#define AP_LSI_OFFSET_PARM_C                       16297     // (T595,ApLsiOfst_TPARCD,16,NA)
#define AP_LSI_OFFSET_PARM_P                           1

#define VPD_PAGE_DATA1_PARM_C                      16298     // (T595,VpdPgDta_TPARCD,64,NA)
#define VPD_PAGE_DATA1_PARM_P                          1

#define VPD_PAGE_DATA2_PARM_C                      16299     // (T595,VpdPgDta_TPARCD,64,NA)
#define VPD_PAGE_DATA2_PARM_P                          1

#define VPD_PAGE_DATA3_PARM_C                      16300     // (T595,VpdPgDta_TPARCD,64,NA)
#define VPD_PAGE_DATA3_PARM_P                          1

#define VPD_PAGE_DATA4_PARM_C                      16301     // (T595,VpdPgDta_TPARCD,64,NA)
#define VPD_PAGE_DATA4_PARM_P                          1

#define PAGE_LENGTH_PARM_C                         16302     // (T595,PgLen_TPARCD,16,NA)
#define PAGE_LENGTH_PARM_P                             1

#define EMC_TEST_OPTION_PARM_C                     16303     // (T601,EmcTstOptn_TPARCD,8,0x0001)
#define EMC_TEST_OPTION_PARM_P                         1

#define WAIT_READY_PARM_C                          16304     // (T601,WaitRdy_TPARCD,16,0x0001) (T605,WaitRdy_TPARCD,16,0x0001)Bypass (T605,WaitRdy_TPARCD,16,0x000F)WaitReady
#define WAIT_READY_PARM_P                              1

#define BYTE_HIGH_LIMIT_PARM_C                     16305     // (T601,BytHiLmt_TPARCD,16,0x0001)
#define BYTE_HIGH_LIMIT_PARM_P                         1

#define OFF_TIME_PER_SET_PARM_C                    16306     // (T601,MxTm_TPARCD,16,NA)
#define OFF_TIME_PER_SET_PARM_P                        1

#define TIME_BETWEEN_EACH_EXE_PARM_C               16307     // (T601,TmPerTst_TPARCD,16,0xFFFF)
#define TIME_BETWEEN_EACH_EXE_PARM_P                   1

#define TEST_PASS_MULTIPLIER_PARM_C                16308     // (T597,TstPassMult_TPARCD,8,NA)
#define TEST_PASS_MULTIPLIER_PARM_P                    1

#define TEST_PASS_COUNT_PARM_C                     16309     // (T597,TstPassCnt_TPARCD,8,NA)
#define TEST_PASS_COUNT_PARM_P                         1

#define OPERATIONAL_FLAGS_PARM_C                   16310     // (DEF,Cwrd1_TPARCD,8,NA) (T597,OpFlag_TPARCD,8,0x0001) (T597,OpFlag_TPARCD,8,0x0002) (T597,OpFlag_TPARCD,8,0x0004) 
#define OPERATIONAL_FLAGS_PARM_P                       1     // (T599,OpFlag_TPARCD,8,NA) (T707,OpFlag_TPARCD,8,0x000F)

#define QUEUE_TAG_WEIGHT_PARM_C                    16311     // (T597,QTagWgt_TPARCD,16,0x000F) (T597,QTagWgt_TPARCD,16,0x00F0) (T597,QTagWgt_TPARCD,16,0x00F00)
#define QUEUE_TAG_WEIGHT_PARM_P                        1

#define RW_CMD_WEIGHT_PARM_C                       16312     // (T597,WrRdCmdWgt_TPARCD,16,0x000F) (T597,WrRdCmdWgt_TPARCD,16,0x00F0) (T597,WrRdCmdWgt_TPARCD,16,0x0F00) (T597,WrRdCmdWgt_TPARCD,16,0xF000)
#define RW_CMD_WEIGHT_PARM_P                           1

#define HIGH_PARTITION_SIZE_PARM_C                 16313     // (T597,HiPartnSz_TPARCD,8,0x0010)
#define HIGH_PARTITION_SIZE_PARM_P                     1

#define ALLOW_WIDE_MODE_PARM_C                     16314     // (T597,AlowWideMode_TPARCD,8,NA)
#define ALLOW_WIDE_MODE_PARM_P                         1

#define FORCE_ASYNC_PARM_C                         16315     // (T597,FrcAsync_TPARCD,8,NA)
#define FORCE_ASYNC_PARM_P                             1

#define MISC_CMD_WEIGHT_PARM_C                     16316     // (T597,MiscCmdWgt_TPARCD,16,0x0003) (T597,MiscCmdWgt_TPARCD,16,0x000C) (T597,MiscCmdWgt_TPARCD,16,0x0030) (T597,MiscCmdWgt_TPARCD,16,0x00C0) (T597,MiscCmdWgt_TPARCD,16,0x0300)
#define MISC_CMD_WEIGHT_PARM_P                         1

#define PARTITION_SIZE_PARM_C                      16317     // (T597,PartnSz_TPARCD,16,NA)
#define PARTITION_SIZE_PARM_P                          1
 
#define RECOVERED_ERR_LIMS_PARM_C                  16318     // (DEF,MxRcovErr_TPARCD,32,NA) (T597,RcovErrLmt_TPARCD,16,0x000F) (T597,RcovErrLmt_TPARCD,16,0x00F0) (T597,RcovErrLmt_TPARCD,16,0x07F0) (T597,RcovErrLmt_TPARCD,16,0x8000) (T618,MxRcovErr_TPARCD,32,0x03FF) (T621,MxRcovErr_TPARCD,32,0x03FF)
#define RECOVERED_ERR_LIMS_PARM_P                      1     // (T623,MxRcovErr_TPARCD,32,0x03FF) (T623,MxRcovErr_TPARCD,32,0xFC00)

#define QUEUE_DEPT_PARM_C                          16319     // (T597,QDpth_TPARCD,8,0x00FF) (T623,QDpth_TPARCD,8,0x00FF)
#define QUEUE_DEPT_PARM_P                              1

#define IOPS_LOWER_LIM_PARM_C                      16320     // (DEF,IoOpLwrLmt_TPARCD,16,NA) (T510,IoOpLwrLmt_TPARCD,16,0x03FF) (T597,IoOpLwrLmt_TPARCD,16,0x03FF)
#define IOPS_LOWER_LIM_PARM_P                          1

#define MAX_UNRECOVERABLE_ERR_PARM_C               16321     // (DEF,MxNonRcovErr_TPARCD,32,NA) (T597,MxNonRcovErr_TPARCD,32,0x007F) (T597,MxNonRcovErr_TPARCD,32,0x0080) (T618,MxNonRcovErr_TPARCD,32,0x003F) (T621,MxNonRcovErr_TPARCD,32,0x003F)
#define MAX_UNRECOVERABLE_ERR_PARM_P                   1

#define MULT_CMD_PACKET_PARM_C                     16322     // (T597,MultCmdPack_TPARCD,8,NA)
#define MULT_CMD_PACKET_PARM_P                         1

#define REQ_ACK_OFFSET_PARM_C                      16323     // (T597,RqstAckOfst_TPARCD,8,NA)
#define REQ_ACK_OFFSET_PARM_P                          1

#define PARTITION_NUM_PARM_C                       16324     // (T597,PartnNum_TPARCD,8,0x00FF)
#define PARTITION_NUM_PARM_P                           1

#define MAX_BLOCK_PER_CMD_PARM_C                   16325     // (DEF,MxBlkPerCmd_TPARCD,16,NA)
#define MAX_BLOCK_PER_CMD_PARM_P                       1

#define DISPLAY_WEAKEST_HEAD_PARM_C                16326     // (T598,DsplWeakHd_TPARCD,8,NA)
#define DISPLAY_WEAKEST_HEAD_PARM_P                    1

#define SERPENT_BLOCK_OPT_PARM_C                   16327     // (T598,SerpBlkOptn_TPARCD,8,NA)
#define SERPENT_BLOCK_OPT_PARM_P                       1

#define DISABLE_CACHING_PARM_C                     16328     // (T598,DisblCache_TPARCD,8,NA)
#define DISABLE_CACHING_PARM_P                         1

#define ZONE_TEST_PARM_C                           16329     // (T598,ZnTstOptn_TPARCD,16,0x7FFF)SeqRate (T598,ZnTstOptn_TPARCD,16,0x8000)Test
#define ZONE_TEST_PARM_P                               1

#define DERATED_SKEW_TIME_PARM_C                   16330     // (T598,DrtdSkewTm_TPARCD,16,NA)
#define DERATED_SKEW_TIME_PARM_P                       1

#define CYLINDER_SKEW_TIME_PARM_C                  16331     // (T598,CylSkewTm_TPARCD,16,NA)
#define CYLINDER_SKEW_TIME_PARM_P                      1

#define TRACK_SKEW_TIME_PARM_C                     16332     // (T598,TrkSkewTm_TPARCD,16,NA)
#define TRACK_SKEW_TIME_PARM_P                         1

#define REV_TIME_PARM_C                            16333     // (DEF,RevTm_TPARCD,16,NA)
#define REV_TIME_PARM_P                                1

#define QUALIFIER_PARM_C                           16334     // (T602,Qual_TPARCD,16,NA)
#define QUALIFIER_PARM_P                               1

#define MAX_INDEX_COUNT_PARM_C                     16335     // (T602,MxIdxCnt_TPARCD,16,NA)
#define MAX_INDEX_COUNT_PARM_P                         1

#define RV_SENSOR_PRESENCE_PARM_C                  16336     // (T603,RvSnsrExpct_TPARCD,8,NA)
#define RV_SENSOR_PRESENCE_PARM_P                      1

#define RV_ABS_REST_PARM_C                         16337     // (T603,RvAbsRest_TPARCD,32,NA)
#define RV_ABS_REST_PARM_P                             2

#define SENSOR_DELAY_PARM_C                        16338     // (T603,SnsrDly_TPARCD,16,NA)
#define SENSOR_DELAY_PARM_P                            1

#define FLUSH_DELAY_PARM_C                         16339     // (T603,FlushDly_TPARCD,16,NA) no functionality
#define FLUSH_DELAY_PARM_P                             1

#define RANDOM_ACCESS_COUNT_PARM_C                 16340     // (T603,RdmAccssCnt_TPARCD,16,NA)
#define RANDOM_ACCESS_COUNT_PARM_P                     1

#define RV_ABS_ACCESS_PARM_C                       16341     // (T603,RvAbsAccss_TPARCD,32,NA)
#define RV_ABS_ACCESS_PARM_P                           2

#define RV_MEAN_PARM_C                             16342     // (T603,RvMean_TPARCD,32,NA)
#define RV_MEAN_PARM_P                                 2

#define DISPARITY_COUNT_PARM_C                     16343     // (T604,DisParityCnt_TPARCD,8,0x00FF)
#define DISPARITY_COUNT_PARM_P                         1

#define SYNC_COUNT_LOSS_PARM_C                     16344     // (T604,SyncCntLoss_TPARCD,8,0x00FF)
#define SYNC_COUNT_LOSS_PARM_P                         1

#define RESET_OPTION_PARM_C                        16345     // (T604,RstOptn_TPARCD,8,0x0001) (T707,RstOptn_TPARCD,8,NA) no functionality (T714,RstOptn_TPARCD,8,NA)
#define RESET_OPTION_PARM_P                            1

#define SAVE_ERR_TO_MFG_TRK_PARM_C                 16346     // (T515,DisblSavErr_TPARCD,8,0x0001) (T618,SavErrMfgTrk_TPARCD,8,NA)  (T618,SavErrMfgTrk_TPARCD,8,0x0001) 
#define SAVE_ERR_TO_MFG_TRK_PARM_P                     1

#define DISABLE_REASSIGN_BLK_PARM_C                16347     // (T515,DisblReassgnBlk_TPARCD,8,0x0001)
#define DISABLE_REASSIGN_BLK_PARM_P                    1

#define NUMBER_ERR_FOR_VERIFY_PARM_C               16348     // (T515,NumErrVfy_TPARCD,8,NA)
#define NUMBER_ERR_FOR_VERIFY_PARM_P                   1

#define DISABLE_STROBES_PARM_C                     16349     // (T515,DisblStrb_TPARCD,8,NA) no functionality
#define DISABLE_STROBES_PARM_P                         1

#define DISABLE_OFFSETS_PARM_C                     16350     // (T515,DisblOfst_TPARCD,8,0x0001)
#define DISABLE_OFFSETS_PARM_P                         1

#define NUMBER_PATTERNS_PARM_C                     16351     // (T515,NumPttrn_TPARCD,32,0x000F) (T1647,NumPttrn_TPARCD,32,NA)
#define NUMBER_PATTERNS_PARM_P                         1

#define BLOCK_MSW_PARM_C                           16352     // (T515,Blk_TPARCD,64,NA)
#define BLOCK_MSW_PARM_P                               1

#define BLOCK_LSW_PARM_C                           16353     // (T515,Blk_TPARCD,64,NA)
#define BLOCK_LSW_PARM_P                               1

#define POSITION_MSW_PARM_C                        16354     // (T515,Psn_TPARCD,32,NA)
#define POSITION_MSW_PARM_P                            1

#define POSITION_LSW_PARM_C                        16355     // (T515,Psn_TPARCD,32,NA)
#define POSITION_LSW_PARM_P                            1

#define EVAL_OF_INDEX_COUNT_PARM_C                 16356     // (T515,IdxCnt_TPARCD,32,NA) (T515,IdxCnt_TPARCD,32,0xFFFF)
#define EVAL_OF_INDEX_COUNT_PARM_P                     2

#define ET_PARM_C                                  16357     // (T515,EnblTlvl_TPARCD,8,0x0001)
#define ET_PARM_P                                      1

#define TL_PARM_C                                  16358     // (T515,Tlvl_TPARCD,8,0x00FF)
#define TL_PARM_P                                      1

#define FRAME_SIZE_PARM_C                          16359     // (T608,FrameSz_TPARCD,16,NA)
#define FRAME_SIZE_PARM_P                              1

#define LOOP_INIT_PARM_C                           16360     // (T608,LoopInit_TPARCD,8,0x0001)
#define LOOP_INIT_PARM_P                               1

#define LOGIN_OPTION_PARM_C                        16361     // (T608,LoginOptn_TPARCD,16,0x00FF) (T608,LoginOptn_TPARCD,16,0x7F00) (T608,LoginOptn_TPARCD,16,0x8000)
#define LOGIN_OPTION_PARM_P                            1

#define NUMBER_FILTER_TAPS_PARM_C                  16362     // (NA, Unused, NA, NA)
#define NUMBER_FILTER_TAPS_PARM_P                      1

#define FILTER_TAP_VALUES_PARM_C                   16363     // (NA, Unused, NA, NA)
#define FILTER_TAP_VALUES_PARM_P                      10

#define BYPASS_FAILURE_PARM_C                      16364     // (T507,BypasFail_TPARCD,8,0x0002) (T507,BypasFail_TPARCD,8,0x0001)
#define BYPASS_FAILURE_PARM_P                          1

#define REFRESH_LOG_PARM_C                         16365     // (T521,RfrshLog_TPARCD,8,NA) (T611,RfrshLog_TPARCD,8,0x0001)
#define REFRESH_LOG_PARM_P                             1

#define TABLE_INDEX_PARM_C                         16366     // (DEF,TblIdx_TPARCD,16,NA) (DEF,TblIdx_TPARCD,16,0x00FF) (DEF,TblIdx_TPARCD,16,0xFF00)
#define TABLE_INDEX_PARM_P                             1

#define DDR_ADDR_START_PARM_C                      16367     // (T611,DrrAddrStrt_TPARCD,32,NA)
#define DDR_ADDR_START_PARM_P                          2

#define DDR_ADDR_END_PARM_C                        16368     // (T611,DrrAddrEnd_TPARCD,32,NA)
#define DDR_ADDR_END_PARM_P                            2

#define DDR_ADDR_INCR_PARM_C                       16369     // (T611,DrrAddrInc_TPARCD,16,NA)
#define DDR_ADDR_INCR_PARM_P                           1

#define CHK_SRVO_LOOP_CODE_PARM_C                  16370     // (T517,ChkSvoLoopCode_TPARCD,8,0x0001)
#define CHK_SRVO_LOOP_CODE_PARM_P                      1

#define CHK_FRU_CODE_PARM_C                        16371     // (T517,ChkFruCode_TPARCD,8,0x0001)
#define CHK_FRU_CODE_PARM_P                            1

#define RPT_REQS_CMD_CNT_PARM_C                    16372     // (T517,RprtNumRqstCmd_TPARCD,8,0x0001)
#define RPT_REQS_CMD_CNT_PARM_P                        1

#define SRVO_LOOP_CODE_PARM_C                      16373     // (T517,SvoLoopCode_TPARCD,8,NA)
#define SRVO_LOOP_CODE_PARM_P                          1

#define SEND_TUR_CMDS_ONLY_PARM_C                  16374     // (T517,TurCmdOnly_TPARCD,8,0x0001)
#define SEND_TUR_CMDS_ONLY_PARM_P                      1

#define MAX_REQS_CMD_CNT_PARM_C                    16375     // (T517,MxRqstCmdCnt_TPARCD,8,NA)
#define MAX_REQS_CMD_CNT_PARM_P                        1

#define SENSE_DATA_4_PARM_C                        16376     // (T517,SnsDta4_TPARCD[0-3],8,NA)
#define SENSE_DATA_4_PARM_P                            4

#define SENSE_DATA_5_PARM_C                        16377     // (T517,SnsDta5_TPARCD[0-3],8,NA)
#define SENSE_DATA_5_PARM_P                            4

#define SENSE_DATA_6_PARM_C                        16379     // (T517,SnsDta6_TPARCD[0-3],8,NA)
#define SENSE_DATA_6_PARM_P                            4

#define SENSE_DATA_7_PARM_C                        16380     // (T517,SnsDta7_TPARCD[0-3],8,NA)
#define SENSE_DATA_7_PARM_P                            4

#define SENSE_DATA_8_PARM_C                        16381     // (T517,SnsDta8_TPARCD[0-3],8,NA)
#define SENSE_DATA_8_PARM_P                            4

#define SENSE_DATA_9_PARM_C                        16382     // (NA, Unused, NA, NA)
#define SENSE_DATA_9_PARM_P                            4

#define SENSE_DATA_10_PARM_C                       16383     // (NA, Unused, NA, NA)
#define SENSE_DATA_10_PARM_P                           4

#define RPT_SEL_SNS_DATA_PARM_C                    16384     // (T517,RprtRqstDta_TPARCD,8,0x0001)
#define RPT_SEL_SNS_DATA_PARM_P                        1

#define ACCEPTABLE_IF_MATCH_PARM_C                 16385     // (T517,AccptVal_TPARCD,8,0x0001)
#define ACCEPTABLE_IF_MATCH_PARM_P                     1

#define OMIT_DUP_ENTRY_PARM_C                      16386     // (T517,OmitDup_TPARCD,8,0x0001)
#define OMIT_DUP_ENTRY_PARM_P                          1

#define ACCEPTABLE_SNS_DATA_PARM_C                 16387     // (T517,AccptSnsDta_TPARCD,8,0x0001)
#define ACCEPTABLE_SNS_DATA_PARM_P                     1

#define WDG_FROM_END_OF_HEAT_PARM_C                16388     // (NA, Unused, NA, NA)
#define WDG_FROM_END_OF_HEAT_PARM_P                    1

#define LINK_COMMANDS_PARM_C                       16389     // (T618,LnkCmd_TPARCD,8,0x0001)
#define LINK_COMMANDS_PARM_P                           1

#define BER_OPTION_PARM_C                          16390     // (T618,BerOptn_TPARCD,8,0x0003)
#define BER_OPTION_PARM_P                              1

#define USE_SCSIERR_FILE_PARM_C                    16391     // (T618,UseScsiErrFile_TPARCD,8,0x0001)
#define USE_SCSIERR_FILE_PARM_P                        1

#define DELTA_SPEC_PARM_C                          16392     // (T618,DltaSpec_TPARCD,16,0x0FFF)
#define DELTA_SPEC_PARM_P                              1

#define WRT_RD_CUST_FILE_PARM_C                    16393     // (T524,WrRdCustFile_TPARCD,8,0x01) (T536,WrRdCustFile_TPARCD,8,0x000F)
#define WRT_RD_CUST_FILE_PARM_P                        1

#define FILE_LENGTH_PARM_C                         16394     // (DEF,FileLen_TPARCD,32,NA)
#define FILE_LENGTH_PARM_P                             1

#define GAIN_SPEC_PARM_C                           16395     // (T619,GainSpec_TPARCD,8,0x00FF)
#define GAIN_SPEC_PARM_P                               1

#define DEBUG_DELAY_TIME_PARM_C                    16396     // (T615,DbgDlyTm_TPARCD,8,0x0001)
#define DEBUG_DELAY_TIME_PARM_P                        1

#define SET_AGC_MARK_PARM_C                        16397     // (T615,SetAgcMsk_TPARCD,8,0x0001)
#define SET_AGC_MARK_PARM_P                            1

#define DITHERING_ADJUSTMENTS_PARM_C               16398     // (T615,DithAdj_TPARCD,8,0x0001)
#define DITHERING_ADJUSTMENTS_PARM_P                   1

#define ENABLE_DITHERING_PARM_C                    16399     // (T615,EnblDith_TPARCD,8,0x0001)
#define ENABLE_DITHERING_PARM_P                        1

#define ENABLE_POWER_CYCLING_PARM_C                16400     // (T615,EnblPwrCycle_TPARCD,8,0x0001)
#define ENABLE_POWER_CYCLING_PARM_P                    1

#define THRESHOLD_OFFSET_PARM_C                    16401     // (T615,ThrshOfst_TPARCD,16,NA)
#define THRESHOLD_OFFSET_PARM_P                        1

#define TA_MILLISECOND_WAIT_PARM_C                 16402     // (T615,TaMsecWait_TPARCD,16,NA)
#define TA_MILLISECOND_WAIT_PARM_P                     1

#define HEAD_TA_COUNT_PARM_C                       16403     // (T615,HdTaCnt_TPARCD,16,NA)
#define HEAD_TA_COUNT_PARM_P                           1

#define MAX_TA_BEFORE_FAIL_PARM_C                  16404     // (T615,MxTaFail_TPARCD,16,NA)
#define MAX_TA_BEFORE_FAIL_PARM_P                      1

#define MARVELL_REG_1E_SET_PARM_C                  16405     // (T615,MarvelRegSet_TPARCD,16,NA)
#define MARVELL_REG_1E_SET_PARM_P                      1

#define FAILURE_CRITERIA_PARM_C                    16406     // (T615,FailCrit_TPARCD,16,NA)
#define FAILURE_CRITERIA_PARM_P                        1

#define LZ_CURRENT_ADJ_PARM_C                      16407     // (T615,CrrntAdj_TPARCD,16,NA)
#define LZ_CURRENT_ADJ_PARM_P                         1

#define DITHER_DELAY_PARM_C                        16408     // (T615,DithDly_TPARCD,16,NA)
#define DITHER_DELAY_PARM_P                            1

#define MANUAL_OFFSET_PARM_C                       16409     // (T613,ManlOfst_TPARCD,8,NA)
#define MANUAL_OFFSET_PARM_P                           1

#define UNLIMITED_ERROR_PARM_C                     16410     // (T621,NoLmtErr_TPARCD,16,NA)
#define UNLIMITED_ERROR_PARM_P                         1

#define TEST_PORT_PARM_C                           16411     // (T621,TstPort_TPARCD,8,NA)
#define TEST_PORT_PARM_P                               1

#define DISABLE_VBAR_PARM_C                        16412     // (T621,DisblVar_TPARCD,8,0x0001)
#define DISABLE_VBAR_PARM_P                            1

#define USER_MAX_CNTR_WRTS_PARM_C                  16413     // (T621,UseMxCentrWr_TPARCD,8,0x0001)
#define USER_MAX_CNTR_WRTS_PARM_P                      1

#define BASE_MAX_CNTR_WRTS_PARM_C                  16414     // (T621,BaseMxCentrWr_TPARCD,8,0x0001)
#define BASE_MAX_CNTR_WRTS_PARM_P                      1

#define APPLY_T700_PARAMS_PARM_C                   16415     // (T621,UseTst700Parm_TPARCD,8,0x0001)
#define APPLY_T700_PARAMS_PARM_P                       1

#define RND_PAT_BUF_SIZE_PARM_C                    16416     // (T621,RdmPttrnBufSz_TPARCD,16,NA)
#define RND_PAT_BUF_SIZE_PARM_P                        1

#define USR_INPUT_MAX_WRTS_PARM_C                  16417     // (NA, Unused, NA, NA)
#define USR_INPUT_MAX_WRTS_PARM_P                      1

#define CENTER_CYLINDER_PARM_C                     16418     // (T621,CentrCyl_TPARCD,32,NA)
#define CENTER_CYLINDER_PARM_P                         2

#define HEAD_TO_TEST_PARM_C                        16419     // (T613,HdTstSel_TPARCD,8,NA)
#define HEAD_TO_TEST_PARM_P                            1

#define STARTING_OFFSET_PARM_C                     16420     // (T613,StrtOfst_TPARCD,16,NA)
#define STARTING_OFFSET_PARM_P                         1

#define BER_LIMIT_PARM_C                           16421     // (T613,BerLmt_TPARCD,8,NA)
#define BER_LIMIT_PARM_P                               1

#define MIN_ERR_RATE_PARM_C                        16422     // (T613,MnErrRat_TPARCD,16,NA)
#define MIN_ERR_RATE_PARM_P                            1

#define REPORT_OFFSET_PARM_C                       16423     // (T613,RprtOfst_TPARCD,8,NA)
#define REPORT_OFFSET_PARM_P                           1

#define REPORT_ERR_TYPE_PARM_C                     16424     // (T613,RprtErrTyp_TPARCD,8,NA)
#define REPORT_ERR_TYPE_PARM_P                         1

#define REPORT_LBA_PARM_C                          16425     // (T613,RprtLba_TPARCD,8,NA)
#define REPORT_LBA_PARM_P                              1

#define USE_VERIFY_CMD_PARM_C                      16426     // (T613,UseVfyCmd_TPARCD,16,NA)
#define USE_VERIFY_CMD_PARM_P                          1

#define CONTROL_WORD_PARM_C                        16427     // (DEF,Cwrd1_TPARCD,16,NA) (T564,Cwrd1_TPARCD,16,0x0001) (T621,CtrlWrd_TPARCD,16,0x0001) (T621,CtrlWrd_TPARCD,16,0x0002) (T621,CtrlWrd_TPARCD,16,0x0004) (T621,CtrlWrd_TPARCD,16,0x0018)
#define CONTROL_WORD_PARM_P                            1     // (T621,CtrlWrd_TPARCD,16,0x0060) (T621,CtrlWrd_TPARCD,16,0x0080) (T621,CtrlWrd_TPARCD,16,0x0100) (T621,CtrlWrd_TPARCD,16,0x0200) (T621,CtrlWrd_TPARCD,16,0x0400) (T627,Cwrd1_TPARCD,16,0x0001)

#define MIN_ERR_CNT_PARM_C                         16428     // (T621,MnErrCnt_TPARCD,16,NA) (T1509,MnErrCnt_TPARCD,16,NA) (T5509,MnErrCnt_TPARCD,16,NA)
#define MIN_ERR_CNT_PARM_P                             1

#define MAX_SECTOR_PARM_C                          16429     // (DEF,MxSctr_TPARCD,32,NA) (T621,MxSctr_TPARCD,32,0xFFFF) (T621,MxSctr_TPARCD,32,0x0FFF0000) no functionality (T621,MxSctr_TPARCD,32,0xFFFF0000)
#define MAX_SECTOR_PARM_P                              2

#define USER_MAX_CNTR_WRTS_CNT_PARM_C              16430     // (T621,UseMxCentrWrCnt_TPARCD,16,0x00FF)
#define USER_MAX_CNTR_WRTS_CNT_PARM_P                  1

#define SCSI_COMMAND_PARM_C                        16431     // (T638,ScsiCmd_TPARCD,8,NA)
#define SCSI_COMMAND_PARM_P                            1

#define LONG_COMMAND_PARM_C                        16432     // (T638,LngCmd_TPARCD,8,NA)
#define LONG_COMMAND_PARM_P                            1

#define BYPASS_WAIT_UNIT_RDY_PARM_C                16433     // (T638,UnitRdy_TPARCD,8,NA)
#define BYPASS_WAIT_UNIT_RDY_PARM_P                    1

#define AUTO_DETECT_PARM_C                         16434     // (T705,AutoDtct_TPARCD,8,NA)
#define AUTO_DETECT_PARM_P                             1

#define ADDRESS_MODE_PARM_C                        16435     // (T519,AddrMode_TPARCD,8,NA) (T705,AddrMode_TPARCD,8,NA)
#define ADDRESS_MODE_PARM_P                            1

#define INNER_LOOP_CNT_PARM_C                      16436     // (T705,InrLoopCnt_TPARCD,16,NA)
#define INNER_LOOP_CNT_PARM_P                          1

#define OUTER_LOOP_CNT_PARM_C                      16437     // (T705,OutrLoopCnt_TPARCD,16,NA)
#define OUTER_LOOP_CNT_PARM_P                          1

#define TMD_LIMIT_PARM_C                           16438     // (T705,TmdLmt_TPARCD,16,NA)
#define TMD_LIMIT_PARM_P                               1

#define REV_SEEK_PARM_C                            16439     // (T705,RevSk_TPARCD,16,NA)
#define REV_SEEK_PARM_P                                1

#define COMBO_SPEC_PARM_C                          16440     // (T707,CmbSpec_TPARCD,8,NA)
#define COMBO_SPEC_PARM_P                              1

#define GRADIENT_SPEC_PARM_C                       16441     // (T707,GradntSpec_TPARCD,8,NA)
#define GRADIENT_SPEC_PARM_P                           1

#define VGA_REG13_PARM_C                           16442     // (T707,VgaReg13_TPARCD,16,0x00FF) (T707,VgaReg13_TPARCD,16,0xFF00)
#define VGA_REG13_PARM_P                               1

#define POSITIVE_DELTA_PARM_C                      16443     // (T707,PosDlta_TPARCD,16,0x00FF) (T707,PosDlta_TPARCD,16,0xFF00)
#define POSITIVE_DELTA_PARM_P                          1

#define NEGATIVE_DELTA_PARM_C                      16444     // (T707,NegDlta_TPARCD,16,0x00FF) (T707,NegDlta_TPARCD,16,0xFF00)
#define NEGATIVE_DELTA_PARM_P                          1

#define BOUNDARY_PARM_C                            16445     // (T707,Bndry_TPARCD,32,0x000000FF) (T707,Bndry_TPARCD,32,0x0000FF00) (T707,Bndry_TPARCD,32,0x00FF0000) (T707,Bndry_TPARCD,32,0xFF000000)
#define BOUNDARY_PARM_P                                2

#define MAX_TA_SPEC_PARM_C                         16446     // (T707,MxTaSpec_TPARCD,16,0x00FF) (T707,MxTaSpec_TPARCD,16,0x1000)
#define MAX_TA_SPEC_PARM_P                             1

#define TEMP_DIFF_LIMIT_PARM_C                     16447     // (T707,TmpDiffLmt_TPARCD,16,0x7FFF)
#define TEMP_DIFF_LIMIT_PARM_P                         1

#define SEEK_FLAG_PARM_C                           16448     // (T711,SkFlag_TPARCD,16,NA)
#define SEEK_FLAG_PARM_P                               1

#define NUMBER_RETRACTS_PARM_C                     16449     // (T711,NumRtrct_TPARCD,16,NA)
#define NUMBER_RETRACTS_PARM_P                         1

#define TARGET_RETRACT_CYL_PARM_C                  16450     // (T711,TgtRtrctCyl_TPARCD,32,NA)
#define TARGET_RETRACT_CYL_PARM_P                      2

#define DEBUG_PARM_C                               16451     // (T531,Dbg_TPARCD,16,NA) (T711,Dbg_TPARCD,16,NA)
#define DEBUG_PARM_P                                   1

#define DEBUG_CNT_PARM_C                           16452     // (T711,DbgCnt_TPARCD,16,NA)
#define DEBUG_CNT_PARM_P                               1

#define B2D_SVGA_SPEC_PARM_C                       16453     // (NA, Unused, NA, NA)
#define B2D_SVGA_SPEC_PARM_P                           1

#define SPT_SVGA_SPEC_PARM_C                       16454     // (NA, Unused, NA, NA)
#define SPT_SVGA_SPEC_PARM_P                           1

#define TEMP_MODE_PARM_C                           16455     // (T634,TmpMode_TPARCD,8,0x0001)
#define TEMP_MODE_PARM_P                               1

#define DISPLAY_SVGA_PARM_C                        16456     // (NA, Unused, NA, NA)
#define DISPLAY_SVGA_PARM_P                            1

#define FAILSAFE_PARM_C                            16457     // (DEF,FailSaf_TPARCD,8,0x0001) (T714,FailSaf_TPARCD,8,NA) (T717,FailSaf_TPARCD,8,NA)
#define FAILSAFE_PARM_P                                1

#define POWER_ON_TIME_PARM_C                       16458     // (T719,PwrOnTm_TPARCD,8,NA)
#define POWER_ON_TIME_PARM_P                           1

#define POWER_OFF_TIME_PARM_C                      16459     // (T719,PwrOffTm_TPARCD,8,NA)
#define POWER_OFF_TIME_PARM_P                          1

#define PARAM_NUMBER_PARM_C                        16460     // (T730,ParmNum_TPARCD[0-1],16,NA)
#define PARAM_NUMBER_PARM_P                            2

#define UNIQUE_VALUE_PARM_C                        16461     // (T730,UniqVal_TPARCD[0-1],16,NA)
#define UNIQUE_VALUE_PARM_P                            2

#define BIAS_SPEC_PARM_C                           16462     // (T730,BiasSpec_TPARCD,16,NA)
#define BIAS_SPEC_PARM_P                               1

#define TEST_CODE_NUMBER_PARM_C                    16463     // (T730,TstCodeNum_TPARCD,8,0x00FF)
#define TEST_CODE_NUMBER_PARM_P                        1

#define CRESCENDO_ACCESS_PARM_C                    16464     // (T510,CrscndoAccss_TPARCD,8,0x0001)
#define CRESCENDO_ACCESS_PARM_P                        1

#define BUTTERFLY_ACCESS_PARM_C                    16465     // (T510,BtrflyAccss_TPARCD,8,0x0001)
#define BUTTERFLY_ACCESS_PARM_P                        1

#define CHK_NONREC_ERR_PER_HD_PARM_C               16466     // (T503,ChkNonRcovErrHd_TPARCD,8,NA) (T510,ChkNonRcovErrHd_TPARCD,8,0x0001) (T634,ChkNonRcovErrHd_TPARCD,8,NA)
#define CHK_NONREC_ERR_PER_HD_PARM_P                   1

#define TOTAL_BLKS_TO_TRANS_LSW_PARM_C             16467     // (T510,TtlLbaTrnsfr_TPARCD,64,NA)
#define TOTAL_BLKS_TO_TRANS_LSW_PARM_P                 1

#define TOTAL_BLKS_TO_TRANS_MSW_PARM_C             16468     // (T510,TtlLbaTrnsfr_TPARCD,64,NA) (T510,TtlLbaTrnsfr_TPARCD,64,0x0003)
#define TOTAL_BLKS_TO_TRANS_MSW_PARM_P                 1

#define END_LBA_PARM_C                             16469     // (DEF,EndLba_TPARCD,64,NA) (T510,EndLba_TPARCD,64,0xFFFF) (T510,EndLba_TPARCD,64,0xFFFF0000)
#define END_LBA_PARM_P                                 2

#define ERROR_OFFSET_PARM_C                        16470     // (T731,ErrOfst_TPARCD,16,0x00FF) (T731,ErrOfst_TPARCD,16,0xFF00)
#define ERROR_OFFSET_PARM_P                            1

#define NON_ERROR_OFFSET_PARM_C                    16471     // (T731,NonErrOfst_TPARCD,16,0x00FF) (T731,NonErrOfst_TPARCD,16,0xFF00)
#define NON_ERROR_OFFSET_PARM_P                        1

#define MIN_RETRY_QUAL_PARM_C                      16472     // (T731,MnRtryQual_TPARCD,8,0x00FF)
#define MIN_RETRY_QUAL_PARM_P                          1

#define CONSECUTIVE_CYCLE_PARM_C                   16473     // (T731,ConscCycle_TPARCD,8,0x00FF)
#define CONSECUTIVE_CYCLE_PARM_P                       1

#define MIN_LOOP_COUNT_PARM_C                      16474     // (T731,MnLoopCnt_TPARCD,8,0x00FF)
#define MIN_LOOP_COUNT_PARM_P                          1

#define CYCLE_PER_CYL_PARM_C                       16475     // (T731,CyclePerCyl_TPARCD,8,0x00FF)
#define CYCLE_PER_CYL_PARM_P                           1

#define CYCLE_PER_HEAD_PARM_C                      16476     // (T731,CyclePerHd_TPARCD,8,0x00FF)
#define CYCLE_PER_HEAD_PARM_P                          1

#define SMART_TIMESTAMP_CHK_PARM_C                 16477     // (NA, Unused, NA, NA)
#define SMART_TIMESTAMP_CHK_PARM_P                     1

#define SMART_DUMP_PARM_C                          16478     // (NA, Unused, NA, NA)
#define SMART_DUMP_PARM_P                              1

#define HF_DELTA_FLY_PARM_C                        16479     // (NA, Unused, NA, NA)
#define HF_DELTA_FLY_PARM_P                            1

#define LF_DELTA_FLY_PARM_C                        16480     // (NA, Unused, NA, NA)
#define LF_DELTA_FLY_PARM_P                            1

#define DELTA_SPEC_NORM_PARM_C                     16481     // (NA, Unused, NA, NA)
#define DELTA_SPEC_NORM_PARM_P                         1

#define SMART_TIMESTAMP_PARM_C                     16482     // (NA, Unused, NA, NA)
#define SMART_TIMESTAMP_PARM_P                         1

#define FORMAT_PAD_PARM_C                          16483     // (T527,FmtPad_TPARCD,8,0x00FF) (T727,FmtPad_TPARCD,8,0x00FF)
#define FORMAT_PAD_PARM_P                              1

#define ENDING_BLOCK_1ST_RANGE_PARM_C              16484     // (T527,EndBlkRg1_TPARCD,64,NA) (T727,EndBlkRg1_TPARCD,64,NA)
#define ENDING_BLOCK_1ST_RANGE_PARM_P                  2

#define STARTING_BLOCK_2ND_RANGE_PARM_C            16485     // (T527,StrtBlkRg2_TPARCD,64,NA) (T727,StrtBlkRg2_TPARCD,64,NA)
#define STARTING_BLOCK_2ND_RANGE_PARM_P                2

#define ENDING_BLOCK_2ND_RANGE_PARM_C              16486     // (T527,EndBlkRg1_TPARCD,64,NA) (T727,EndBlkRg1_TPARCD,64,NA)
#define ENDING_BLOCK_2ND_RANGE_PARM_P                  2

#define STARTING_BLOCK_3RD_RANGE_PARM_C            16487     // (T527,StrtBlkRg3_TPARCD,64,NA) (T727,StrtBlkRg3_TPARCD,64,NA)
#define STARTING_BLOCK_3RD_RANGE_PARM_P                2

#define BLOCK_LEN_IN_BYTES_PARM_C                  16488     // (T536,BlkLenByt_TPARCD,16,NA)
#define BLOCK_LEN_IN_BYTES_PARM_P                      1

#define SN_BYTES_0_1_PARM_C                        16489     // (T544,SnByt01_TPARCD,16,NA)
#define SN_BYTES_0_1_PARM_P                            1

#define SN_BYTES_2_3_PARM_C                        16490     // (T544,SnByt23_TPARCD,16,NA)
#define SN_BYTES_2_3_PARM_P                            1

#define SN_BYTES_4_5_PARM_C                        16491     // (T544,SnByt45_TPARCD,16,NA)
#define SN_BYTES_4_5_PARM_P                            1

#define SN_BYTES_6_7_PARM_C                        16492     // (T544,SnByt67_TPARCD,16,NA)
#define SN_BYTES_6_7_PARM_P                            1

#define SUBTEST_SPECIFIC_1_PARM_C                  16493     // (T544,SubTstSpec1_TPARCD,16,NA) (T544,SubTstSpec1_TPARCD,16,0x0001) (T544,SubTstSpec1_TPARCD,16,0x0002) (T544,SubTstSpec1_TPARCD,16,0x0003) (T544,SubTstSpec1_TPARCD,16,0x0010)
#define SUBTEST_SPECIFIC_1_PARM_P                      1

#define SUBTEST_SPECIFIC_2_PARM_C                  16494     // (T544,SubTstSpec2_TPARCD,16,NA) (T544,SubTstSpec2_TPARCD,16,0x0001) (T544,SubTstSpec2_TPARCD,16,0x000F) (T544,SubTstSpec2_TPARCD,16,0x003F) (T544,SubTstSpec2_TPARCD,16,0x00FF)
#define SUBTEST_SPECIFIC_2_PARM_P                      1

#define SUBTEST_SPECIFIC_3_PARM_C                  16495     // (T544,SubTstSpec3_TPARCD,16,NA) (T544,SubTstSpec3_TPARCD,16,0x0001) (T544,SubTstSpec3_TPARCD,16,0x0002) 
#define SUBTEST_SPECIFIC_3_PARM_P                      1     // (T544,SubTstSpec3_TPARCD,16,0x000F) (T544,SubTstSpec3_TPARCD,16,0x00F0) (T544,SubTstSpec3_TPARCD,16,0xFF00)

#define SECTOR_SIZE_TYPE_PARM_C                    16496     // (T714,SctrSzTyp_TPARCD,8,NA)
#define SECTOR_SIZE_TYPE_PARM_P                        1

#define DISP_SPT_RESULTS_PARM_C                    16497     // (T714,DispSptRslt_TPARCD,8,NA)
#define DISP_SPT_RESULTS_PARM_P                        1

#define DISP_B2D_RESULTS_PARM_C                    16498     // (T714,DispB2DRslt_TPARCD,8,NA)
#define DISP_B2D_RESULTS_PARM_P                        1

#define ENABLE_PMSE_DELTA_PARM_C                   16499     // (T714,EnblPmseDlta_TPARCD,8,NA)
#define ENABLE_PMSE_DELTA_PARM_P                       1

#define SAVE_PMSE_TO_DISK_PARM_C                   16500     // (T714,SavPmseDisc_TPARCD,8,NA)
#define SAVE_PMSE_TO_DISK_PARM_P                       1

#define CHECK_SPT_DATA_PARM_C                      16501     // (T714,ChkSptDta_TPARCD,8,NA)
#define CHECK_SPT_DATA_PARM_P                          1

#define MSE_DELTA_SPEC_PARM_C                      16502     // (T714,MseDltaSpec_TPARCD,16,NA)
#define MSE_DELTA_SPEC_PARM_P                          1

#define DATA_COLLECTION_PARM_C                     16503     // (T714,DtaCllct_TPARCD,8,NA)
#define DATA_COLLECTION_PARM_P                         1

#define PMSE_SPEC_PARM_C                           16504     // (T714,PmseSpec_TPARCD,16,NA)
#define PMSE_SPEC_PARM_P                               1

#define SEPARATE_PMSE_SPEC_PARM_C                  16505     // (T714,SepPmseSpec_TPARCD,8,NA)
#define SEPARATE_PMSE_SPEC_PARM_P                      1

#define PREAMP_SELECTION_PARM_C                    16506     // (T714,PreampSel_TPARCD,8,NA)
#define PREAMP_SELECTION_PARM_P                        1

#define PMSE_FILE_LOCATION_PARM_C                  16507     // (T714,PmseFileLoc_TPARCD,8,NA)
#define PMSE_FILE_LOCATION_PARM_P                      1

#define REWRITE_TRACK_MODE_PARM_C                  16508     // (T714,ReWrTrkMode_TPARCD,8,NA)
#define REWRITE_TRACK_MODE_PARM_P                      1

#define COMPARE_PMSE_PARM_C                        16509     // (T714,CmprPmse_TPARCD,8,NA)
#define COMPARE_PMSE_PARM_P                            1

#define COMPARE_LH_PMSE_PARM_C                     16510     // (T714,CmprLoHiPmse_TPARCD,8,NA)
#define COMPARE_LH_PMSE_PARM_P                         1

#define ENHANCED_FORMULA_PARM_C                    16511     // (T714,EnhncFrmla_TPARCD,8,NA)
#define ENHANCED_FORMULA_PARM_P                        1

#define ENABLE_B2D_SPT_CQM_PARM_C                  16512     // (T714,EnblB2DSptCqm_TPARCD,8,NA)
#define ENABLE_B2D_SPT_CQM_PARM_P                      1

#define ENABLE_B2D_SPT_PMSE_PARM_C                 16513     // (T714,EnblB2DSptPmse_TPARCD,8,NA)
#define ENABLE_B2D_SPT_PMSE_PARM_P                     1

#define ENABLE_CQM_DELTA_PARM_C                    16514     // (T714,EnblCqmDlta_TPARCD,8,NA)
#define ENABLE_CQM_DELTA_PARM_P                        1

#define SAVE_CQM_VALUES_PARM_C                     16515     // (T714,SavCqmVal_TPARCD,8,NA)
#define SAVE_CQM_VALUES_PARM_P                         1

#define CQM_DELTA_BIAS_PARM_C                      16516     // (T714,CqmDltaBias_TPARCD,8,NA)
#define CQM_DELTA_BIAS_PARM_P                          1

#define PREAMP_RETRY_CNT_PARM_C                    16517     // (T714,PreampRtryCnt_TPARCD,8,NA)
#define PREAMP_RETRY_CNT_PARM_P                        1

#define CYL_RETRY_CNT_PARM_C                       16518     // (T714,CylRtryCnt_TPARCD,8,NA)
#define CYL_RETRY_CNT_PARM_P                           1

#define START_HEAD_PARM_C                          16519     // (T695,StrtHd_TPARCD,8,NA)
#define START_HEAD_PARM_P                              1

#define END_HEAD_PARM_C                            16520     // (T695,EndHd_TPARCD,8,NA)
#define END_HEAD_PARM_P                                1

#define NUMBER_OCCURENCES_PARM_C                   16521     // (NA, Unused, NA, NA)
#define NUMBER_OCCURENCES_PARM_P                       1

#define CYLINDER_OFFSET_PARM_C                     16522     // (NA, Unused, NA, NA)
#define CYLINDER_OFFSET_PARM_P                         1

#define CSM_FAIL_SAFE_PARM_C                       16523     // (NA, Unused, NA, NA)
#define CSM_FAIL_SAFE_PARM_P                           1

#define READ_FAIL_SAFE_PARM_C                      16524     // (NA, Unused, NA, NA)
#define READ_FAIL_SAFE_PARM_P                          1

#define LBA_RETRY_DISPLAY_PARM_C                   16525     // (NA, Unused, NA, NA)
#define LBA_RETRY_DISPLAY_PARM_P                       1

#define CYLINDER_RETRY_PARM_C                      16526     // (NA, Unused, NA, NA)
#define CYLINDER_RETRY_PARM_P                          1

#define AC_OR_DC_ERASE_PARM_C                      16527     // (NA, Unused, NA, NA)
#define AC_OR_DC_ERASE_PARM_P                          1

#define NOISE_THRESHOLD_PARM_C                     16528     // (T695,NoiseThrsh_TPARCD,16,NA)
#define NOISE_THRESHOLD_PARM_P                         1

#define MAX_VERIFIED_PER_HD_PARM_C                 16529     // (NA, Unused, NA, NA)
#define MAX_VERIFIED_PER_HD_PARM_P                     1

#define MAX_UNVERIFIED_PER_HD_PARM_C               16530     // (NA, Unused, NA, NA)
#define MAX_UNVERIFIED_PER_HD_PARM_P                   1

#define NUM_SINGLE_HEADS_RERUN_PARM_C              16531     // (NA, Unused, NA, NA)
#define NUM_SINGLE_HEADS_RERUN_PARM_P                  1

#define MAX_SEQ_ERRORS_PARM_C                      16532     // (NA, Unused, NA, NA)
#define MAX_SEQ_ERRORS_PARM_P                          1

#define MAX_LOG_ERRORS_PARM_C                      16533     // (NA, Unused, NA, NA)
#define MAX_LOG_ERRORS_PARM_P                          1

#define WR_FUNCTION_PARM_C                         16534     // (T574,WrRdFunc_TPARCD,8,NA)
#define WR_FUNCTION_PARM_P                             1

#define REPORTING_MODE_PARM_C                      16535     // (DEF,RprtMode_TPARCD,16,NA)
#define REPORTING_MODE_PARM_P                          1

#define MSID_TYPE_PARM_C                           16536     // (T577,MsidTyp_TPARCD,8,NA)
#define MSID_TYPE_PARM_P                               1

#define DRIVE_STATE_PARM_C                         16537     // (DEF,DrvStat_TPARCD,8,NA)
#define DRIVE_STATE_PARM_P                             1

#define TEST_MODE_PARM_C                           16538     // (DEF,TstMode_TPARCD,16,NA) (T708,TstMode_TPARCD,16,0x00FF)
#define TEST_MODE_PARM_P                               1

#define BANDMASTER_PARM_C                          16539     // (T574,BndMstr_TPARCD,8,NA) (T575,BndMstr_TPARCD,8,NA)
#define BANDMASTER_PARM_P                              1

#define START_LBA_H_PARM_C                         16540     // (T574,StrtLba_TPARCD,64,NA) (T575,StrtLba_TPARCD,64,NA)
#define START_LBA_H_PARM_P                             1

#define START_LBA_L_PARM_C                         16541     // (T574,StrtLba_TPARCD,64,NA) (T575,StrtLba_TPARCD,64,NA)
#define START_LBA_L_PARM_P                             1

#define BAND_SIZE_H_PARM_C                         16542     // (T574,BndSz_TPARCD,32,NA) (T575,BndSz_TPARCD,32,NA)
#define BAND_SIZE_H_PARM_P                             1

#define BAND_SIZE_L_PARM_C                         16543     // (T574,BndSz_TPARCD,32,NA) (T575,BndSz_TPARCD,32,NA)
#define BAND_SIZE_L_PARM_P                             1

#define LOCK_ENABLES_PARM_C                        16544     // (T574,LokEnbl_TPARCD,8,NA)
#define LOCK_ENABLES_PARM_P                            1

#define CLEAR_SESSION_PARM_C                       16545     // (T574,ClrSesn_TPARCD,16,NA) (T602,ClrSesn_TPARCD,16,NA)
#define CLEAR_SESSION_PARM_P                           1

#define DIAG_MODE_PARM_C                           16546     // (T574,DiagMode_TPARCD,8,NA)
#define DIAG_MODE_PARM_P                               1

#define WHICH_SP_PARM_C                            16547     // (T575,TstPort_TPARCD,8,NA)
#define WHICH_SP_PARM_P                                1

#define PASSWORD_TYPE_PARM_C                       16548     // (T575,PassWrdTyp_TPARCD,8,NA)
#define PASSWORD_TYPE_PARM_P                           1

#define UIDMSWU_PARM_C                             16549     // (T575,Uid_TPARCD,64,NA)
#define UIDMSWU_PARM_P                                 1

#define UIDMSWL_PARM_C                             16550     // (T575,Uid_TPARCD,64,NA)
#define UIDMSWL_PARM_P                                 1

#define UIDLSWU_PARM_C                             16551     // (T575,Uid_TPARCD,64,NA)
#define UIDLSWU_PARM_P                                 1

#define UIDLSWL_PARM_C                             16552     // (T575,Uid_TPARCD,64,NA)
#define UIDLSWL_PARM_P                                 1

#define PASS_COUNT_PARM_C                          16553     // (T578,PassCnt_TPARCD,8,NA)
#define PASS_COUNT_PARM_P                              1

#define STATUS_MISCOM_EXP_PARM_C                   16554     // (T574,StatMisCmprExpct_TPARCD,8,NA)
#define STATUS_MISCOM_EXP_PARM_P                       1

#define EXP_SENSE_BYTE2_PARM_C                     16555     // (T574,SnsDta1_TPARCD[0],8,NA)
#define EXP_SENSE_BYTE2_PARM_P                         1

#define EXP_SENSE_BYTE12_PARM_C                    16556     // (T574,SnsDta1_TPARCD[1],8,NA)
#define EXP_SENSE_BYTE12_PARM_P                        1

#define EXP_SENSE_BYTE13_PARM_C                    16557     // (T574,SnsDta1_TPARCD[2],8,NA)
#define EXP_SENSE_BYTE13_PARM_P                        1

#define TEMP_HEATER_CONST_PARM_C                   16558     // (NA, Unused, NA, NA)
#define TEMP_HEATER_CONST_PARM_P                       1

#define TEMP_TEST_MODE_PARM_C                      16559     // (T521,TmpTstMode_TPARCD,8,NA)
#define TEMP_TEST_MODE_PARM_P                          1

#define LOG10_BER_SPEC_PARM_C                      16560     // (DEF,Log10BerSpec_TPARCD,16,0xFFFF)
#define LOG10_BER_SPEC_PARM_P                          1

#define ENBL_LOG10_BER_SPEC_PARM_C                 16561     // (DEF,EnblLog10Ber_TPARCD,8,0x0001)
#define ENBL_LOG10_BER_SPEC_PARM_P                     1

#define NUM_PKS_TO_GROUP_PARM_C                    16562     // (NA, Unused, NA, NA)
#define NUM_PKS_TO_GROUP_PARM_P                        1

#define NUM_PTS_TO_SEP_PEAKS_PARM_C                16563     // (NA, Unused, NA, NA)
#define NUM_PTS_TO_SEP_PEAKS_PARM_P                    1

#define NUM_GRPS_TO_MULTIPLY_PARM_C                16564     // (NA, Unused, NA, NA)
#define NUM_GRPS_TO_MULTIPLY_PARM_P                    1

#define PEAK_PARAMETERS_PARM_C                     16565     // (NA, Unused, NA, NA)
#define PEAK_PARAMETERS_PARM_P                         1

#define ALGORITHM_SELECT_PARM_C                    16566     // (NA, Unused, NA, NA)
#define ALGORITHM_SELECT_PARM_P                        1

#define NUM_STEPS_TO_EXC_THRES_PARM_C              16567     // (NA, Unused, NA, NA)
#define NUM_STEPS_TO_EXC_THRES_PARM_P                  1

#define HTR_DAC_DELTA_MAX_PARM_C                   16568     // (NA, Unused, NA, NA)
#define HTR_DAC_DELTA_MAX_PARM_P                       1

#define CYLINDER_INC_DEC_PARM_C                    16569     // (T549,CylIncDecr_TPARCD,16,NA)
#define CYLINDER_INC_DEC_PARM_P                        1

#define HTR_DAC_DELTA_MIN_PARM_C                   16570     // (NA, Unused, NA, NA)
#define HTR_DAC_DELTA_MIN_PARM_P                       1

#define RETRY_DELTA_PARM_C                         16571     // (NA, Unused, NA, NA)
#define RETRY_DELTA_PARM_P                             1

#define MIN_DAC_PARM_C                             16572     // (NA, Unused, NA, NA)
#define MIN_DAC_PARM_P                                 1

#define FULL_REPORT_PARM_C                         16573     // (NA, Unused, NA, NA)
#define FULL_REPORT_PARM_P                             1

#define REPORT_DEBUG_DATA_PARM_C                   16574     // (NA, Unused, NA, NA)
#define REPORT_DEBUG_DATA_PARM_P                       1

#define SERVO_ADDR_PARM_C                          16575     // (NA, Unused, NA, NA)
#define SERVO_ADDR_PARM_P                              2

#define IO_TIMEOUT_SEC_PARM_C                      16576     // (NA, Unused, NA, NA)
#define IO_TIMEOUT_SEC_PARM_P                          1

#define IO_TIMEOUT_MSEC_PARM_C                     16577     // (NA, Unused, NA, NA)
#define IO_TIMEOUT_MSEC_PARM_P                         1

#define DISPLAY_SUMMARY_PARM_C                     16578     // (NA, Unused, NA, NA)
#define DISPLAY_SUMMARY_PARM_P                         1

#define SEGMENT_SIZE_PARM_C                        16579     // (T602,UdsSegmntSz_TPARCD,32,NA)
#define SEGMENT_SIZE_PARM_P                            2

#define NBR_BYTE_ALLOCATED_PARM_C                  16580     // (T602,UdsNumByt_TPARCD,32,NA) no functionality
#define NBR_BYTE_ALLOCATED_PARM_P                      2

#define ENBL_LOG10_BER_DELTA_PARM_C                16581     // (DEF,EnblLog10BerDlta_TPARCD,8,0x0001)
#define ENBL_LOG10_BER_DELTA_PARM_P                    1

#define LOG10_BER_DELTA_SPEC_PARM_C                16582     // (DEF,Log10BerDlta_TPARCD,8,NA)
#define LOG10_BER_DELTA_SPEC_PARM_P                    1

#define SAVE_BER_TO_DISK_PARM_C                    16583     // (DEF,SavBer_TPARCD,8,0x0001)
#define SAVE_BER_TO_DISK_PARM_P                        1

#define ALWAYS_PASS_PARM_C                         16584     // (NA, Unused, NA, NA)
#define ALWAYS_PASS_PARM_P                             1

#define HD_RES_DELTA_SPEC_PARM_C                   16585     // (T735,HdResistDltaSpec_TPARCD,16,NA)
#define HD_RES_DELTA_SPEC_PARM_P                       1

#define PCT_HD_RES_DELTA_SPEC_PARM_C               16586     // (T735,PrctHdResistDlta_TPARCD,16,NA)
#define PCT_HD_RES_DELTA_SPEC_PARM_P                   1

#define QUEUE_TYPE_PARM_C                          16587     // (T623,QTyp_TPARCD,8,NA)
#define QUEUE_TYPE_PARM_P                              1

#define TEST_OPTION_PARM_C                         16588     // (T531,Cwrd1_TPARCD,16,NA) (T564,TstOptn_TPARCD,16,0x0001) (T695,TstOptn_TPARCD,16,NA)
#define TEST_OPTION_PARM_P                             1

#define STEP_INC_PARM_C                            16589     // (T695,StepInc_TPARCD,8,NA)
#define STEP_INC_PARM_P                                1

#define AC_ERASETYPE_PARM_C                        16590     // (T695,AcDcErase_TPARCD,8,NA)
#define AC_ERASETYPE_PARM_P                            1

#define VBAR_CONVERT_PARM_C                        16591     // (T695,VarCnvrt_TPARCD,8,NA)
#define VBAR_CONVERT_PARM_P                            1

#define PRINT_TRK_REPORT_PARM_C                    16592     // (T695,PrtTrkRprt_TPARCD,8,NA)
#define PRINT_TRK_REPORT_PARM_P                        1

#define TARGET_CYLINDER_PARM_C                     16593     // (T695,TgtCyl_TPARCD,32,NA)
#define TARGET_CYLINDER_PARM_P                         2

#define START_RANGE_PARM_C                         16594     // (T695,StrtRg_TPARCD,8,NA)
#define START_RANGE_PARM_P                             1

#define END_RANGE_PARM_C                           16595     // (T695,EndRg_TPARCD,8,NA)
#define END_RANGE_PARM_P                               1

#define MAX_CSM_THRESHOLD_PARM_C                   16596     // (T695,MxCsmThrsh_TPARCD,32,NA)
#define MAX_CSM_THRESHOLD_PARM_P                       1

#define NUM_TRAIN_RETRIES_PARM_C                   16597     // (T695,NumTrainRtry_TPARCD,8,NA)
#define NUM_TRAIN_RETRIES_PARM_P                       1

#define TEST_ZN_MASK_PARM_C                        16598     // (T695,TstZnMsk_TPARCD,64,NA)
#define TEST_ZN_MASK_PARM_P                            2

#define BYPASS_CLEANUP_PARM_C                      16599     // (T695,BypasClnUp_TPARCD,8,NA)
#define BYPASS_CLEANUP_PARM_P                          1

#define DL_TYPE_PARM_C                             16600     // (NA, Unused, NA, NA)
#define DL_TYPE_PARM_P                                 1

#define DL_MODE_PARM_C                             16601     // (NA, Unused, NA, NA)
#define DL_MODE_PARM_P                                 1

#define PI_TYPE_PARM_C                             16602     // (T530,PiTyp_TPARCD,8,NA) (T624,PiTyp_TPARCD,8,NA)
#define PI_TYPE_PARM_P                                 1

#define COMMAND_COUNT_PARM_C                       16603     // (T624,CmdCnt_TPARCD,16,NA)
#define COMMAND_COUNT_PARM_P                           1

#define PRINT_MESS_REPORT_PARM_C                   16604     // (NA, Unused, NA, NA)
#define PRINT_MESS_REPORT_PARM_P                       1

#define MAX_CSM_MULTIPLIER_PARM_C                  16605     // (T695,MxCsmMult_TPARCD,8,NA)
#define MAX_CSM_MULTIPLIER_PARM_P                      1

#define MAX_DELTA_MULTIPLIER_PARM_C                16606     // (T695,MxDltaMult_TPARCD,8,NA)
#define MAX_DELTA_MULTIPLIER_PARM_P                    1

#define BYPASS_HALFTRACK_PARM_C                    16607     // (NA, Unused, NA, NA)
#define BYPASS_HALFTRACK_PARM_P                        1

#define BYTES_TO_TRANSFER_MSW_PARM_C               16608     // (NA, Unused, NA, NA)
#define BYTES_TO_TRANSFER_MSW_PARM_P                   1

#define BYTES_TO_TRANSFER_LSW_PARM_C               16609     // (NA, Unused, NA, NA)
#define BYTES_TO_TRANSFER_LSW_PARM_P                   1

#define SCSI_REV_BYTES_1_AND_2_PARM_C              16610     // (NA, Unused, NA, NA)
#define SCSI_REV_BYTES_1_AND_2_PARM_P                  1

#define SCSI_REV_BYTES_3_AND_4_PARM_C              16611     // (NA, Unused, NA, NA)
#define SCSI_REV_BYTES_3_AND_4_PARM_P                  1

#define TMS_REV_BYTES_1_AND_2_PARM_C               16612     // (NA, Unused, NA, NA)
#define TMS_REV_BYTES_1_AND_2_PARM_P                   1

#define TMS_REV_BYTES_3_AND_4_PARM_C               16613     // (NA, Unused, NA, NA)
#define TMS_REV_BYTES_3_AND_4_PARM_P                   1

#define INIT_VOLUME_PARM_C                         16614     // (NA, Unused, NA, NA)
#define INIT_VOLUME_PARM_P                             1

#define FIRMWARE_NUMBER_PARM_C                     16615     // (NA, Unused, NA, NA)
#define FIRMWARE_NUMBER_PARM_P                         1

#define BRIDGE_CODE_PARM_C                         16616     // (NA, Unused, NA, NA)
#define BRIDGE_CODE_PARM_P                             1

#define B2D_SETUP_PARM_C                           16617     // (NA, Unused, NA, NA)
#define B2D_SETUP_PARM_P                               1

#define INITIAL_MAX_ERROR_RATE_PARM_C              16618     // (T621,InitMxErrRat_TPARCD,16,NA)
#define INITIAL_MAX_ERROR_RATE_PARM_P                  1

#define REFRENCE_MAX_ERROR_RATE_PARM_C             16619     // (T621,RefMxErrRat_TPARCD,16,0x0FFF)
#define REFRENCE_MAX_ERROR_RATE_PARM_P                 1

#define ERASED_TRACKS_SPEC_PARM_C                  16620     // (T621,EraseTrkSpec_TPARCD,16,NA)
#define ERASED_TRACKS_SPEC_PARM_P                      1

#define NORMALIZED_STE_SPEC_PARM_C                 16621     // (T621,NrmlSteSpec_TPARCD,16,NA)
#define NORMALIZED_STE_SPEC_PARM_P                     1

#define CMD_BYTE_GROUP_0_PARM_C                    16622     // (T638,CmdGrp0_TPARCD[0-5],16,NA)
#define CMD_BYTE_GROUP_0_PARM_P                        6

#define CMD_BYTE_GROUP_1_PARM_C                    16623     // (T638,CmdGrp1_TPARCD[0-5],16,NA)
#define CMD_BYTE_GROUP_1_PARM_P                        6

#define CMD_BYTE_GROUP_2_PARM_C                    16624     // (T638,CmdGrp2_TPARCD[0-5],16,NA)
#define CMD_BYTE_GROUP_2_PARM_P                        6

#define CMD_DFB_LENGTH_PARM_C                      16625     // (T638,CmdDfbLen_TPARCD,8,NA)
#define CMD_DFB_LENGTH_PARM_P                          1

#define START_LBA34_PARM_C                         16626     // (DEF,StrtLba_TPARCD,64,NA) (T510,StrtLba_TPARCD,64,0xFFFF)
#define START_LBA34_PARM_P                             4

#define END_LBA34_PARM_C                           16627     // (DEF,EndLba_TPARCD,64,NA)
#define END_LBA34_PARM_P                               4

#define LBA34_MSW_PARM_C                           16628     // (NA, Unused, NA, NA)
#define LBA34_MSW_PARM_P                               2

#define END_LBA_MSB_PARM_C                         16629     // (NA, Unused, NA, NA)
#define END_LBA_MSB_PARM_P                             1

#define START_LBA_MSB_PARM_C                       16630     // (NA, Unused, NA, NA)
#define START_LBA_MSB_PARM_P                           1

#define LBA_MSB_PARM_C                             16631     // (NA, Unused, NA, NA)
#define LBA_MSB_PARM_P                                 1

#define BTRFLY_LBA_OFFSET_PARM_C                   16632     // (T510,BtrflyLbaOfst_TPARCD,16,NA)
#define BTRFLY_LBA_OFFSET_PARM_P                       1

#define WRITE_START_LBA34_PARM_C                   16633     // (T520,WrStrtLba_TPARCD,64,NA)
#define WRITE_START_LBA34_PARM_P                       4

#define READ_START_LBA34_PARM_C                    16634     // (T520,RdStrtLba_TPARCD,64,NA)
#define READ_START_LBA34_PARM_P                        4

#define END_LBA34_1ST_RANGE_PARM_C                 16635     // (T527,EndBlkRg1_TPARCD,64,NA)
#define END_LBA34_1ST_RANGE_PARM_P                     4

#define START_LBA34_2ND_RANGE_PARM_C               16636     // (T527,StrtBlkRg2_TPARCD,64,NA)
#define START_LBA34_2ND_RANGE_PARM_P                   4

#define END_LBA34_2ND_RANGE_PARM_C                 16637     // (T527,EndBlkRg1_TPARCD,64,NA)
#define END_LBA34_2ND_RANGE_PARM_P                     4

#define START_LBA34_3RD_RANGE_PARM_C               16638     // (T527,StrtBlkRg3_TPARCD,64,NA)
#define START_LBA34_3RD_RANGE_PARM_P                   4

#define TOTAL_LBA_TO_XFER_PARM_C                   16639     // (T510,TtlLbaTrnsfr_TPARCD,64,NA)
#define TOTAL_LBA_TO_XFER_PARM_P                       4

#define NUMBER_LBA_PER_XFER_PARM_C                 16640     // (T510,NumLbaPerTrnsfr_TPARCD,32,NA) (T1500,NumLbaPerTrnsfr_TPARCD,32,NA)
#define NUMBER_LBA_PER_XFER_PARM_P                     2

#define BTRFLY_CMP_DATA_PARM_C                     16641     // (T510,BtrflyCmprDta_TPARCD,16,0x0003)
#define BTRFLY_CMP_DATA_PARM_P                         1

#define CERT_TSTMODE_PARM_C                        16642     // (T575,CertTstMode_TPARCD,8,NA)
#define CERT_TSTMODE_PARM_P                            1

#define CERT_KEYTYPE_PARM_C                        16643     // (T575,CertKeyTyp_TPARCD,8,NA)
#define CERT_KEYTYPE_PARM_P                            1

#define FW_PLATFORM_PARM_C                         16644     // (T577,FwPltfrm_TPARCD,8,NA) (T578,FwPltfrm_TPARCD,8,NA)
#define FW_PLATFORM_PARM_P                             1

#define BYTE_COUNT_PARM_C                          16645     // (T578,BytCnt_TPARCD,16,NA)
#define BYTE_COUNT_PARM_P                              1

#define FILE_LEN_MSW_PARM_C                        16646     // (T578,FileLen_TPARCD,32,NA)
#define FILE_LEN_MSW_PARM_P                            1

#define FILE_LEN_LSW_PARM_C                        16647     // (T578,FileLen_TPARCD,32,NA)
#define FILE_LEN_LSW_PARM_P                            1

#define FMT_P_INFO_PARM_C                          16648     // (T511,FmtPrtInfo_TPARCD,8,NA)
#define FMT_P_INFO_PARM_P                              1

#define RTO_REQ_PARM_C                             16649     // (T511,RefTagRqst_TPARCD,8,NA)
#define RTO_REQ_PARM_P                                 1

#define ATI_CENTER_WRITES_PARM_C                   16650     // (T621,AtiCentrWr_TPARCD,16,NA)
#define ATI_CENTER_WRITES_PARM_P                       1

#define MAX_ATI_ERR_RATE_SPEC_PARM_C               16651     // (T621,AtiErrRat_TPARCD,16,NA)
#define MAX_ATI_ERR_RATE_SPEC_PARM_P                   1

#define COMMAND_WORD_7_PARM_C                      16652     // (T538,CmdWrd_TPARCD[6],16,NA)
#define COMMAND_WORD_7_PARM_P                          1

#define COMMAND_WORD_8_PARM_C                      16653     // (T538,CmdWrd_TPARCD[7],16,NA)
#define COMMAND_WORD_8_PARM_P                          1

#define DISABLE_VMM_THR_NORM_PARM_C                16654     // (T695,DisblVmmThrshNrml_TPARCD,16,NA)
#define DISABLE_VMM_THR_NORM_PARM_P                    1

#define VERBOSE_PARM_C                             16655     // (T624,PrtInfo_TPARCD,8,NA)
#define VERBOSE_PARM_P                                 1

#define FORCE_FORMAT_PARM_C                        16656     // (T624,FrcFmt_TPARCD,8,NA)
#define FORCE_FORMAT_PARM_P                            1

#define OPTIONS_WORD3_PARM_C                       16657     // (NA, Unused, NA, NA)
#define OPTIONS_WORD3_PARM_P                           1

#define ENABLE_CHK_SAME_CYL_HD_PARM_C              16658     // (T515,EnblChkCylHd_TPARCD,8,0x0001)
#define ENABLE_CHK_SAME_CYL_HD_PARM_P                  1

#define SAME_CYL_HD_SPEC_UNVER_PARM_C              16659     // (T515,CylHdSpecNoVfy_TPARCD,8,0xFFFF)
#define SAME_CYL_HD_SPEC_UNVER_PARM_P                  1

#define SAME_CYL_HD_SPEC_VERIF_PARM_C              16660     // (T515,CylHdSpecVfy_TPARCD,8,0xFFFF)
#define SAME_CYL_HD_SPEC_VERIF_PARM_P                  1

#define ENBL_CHECK_SPECIFIC_HEAD_PARM_C            16661     // (DEF,EnblChkSpecHd_TPARCD,8,0x0001)
#define ENBL_CHECK_SPECIFIC_HEAD_PARM_P                1

#define REPORT_HEAD_STATUS_PARM_C                  16662     // (T707,RprtHdStat_TPARCD,8,0x0001)
#define REPORT_HEAD_STATUS_PARM_P                      1

#define ENBL_TEST_SPECIFIC_HEAD_PARM_C             16663     // (T707,EnblTstSpecHd_TPARCD,8,0x0001)
#define ENBL_TEST_SPECIFIC_HEAD_PARM_P                 1

#define FLAWS_PER_TRACK_PARM_C                     16664     // (T529,FlawPerTrk_TPARCD,8,0x000F)
#define FLAWS_PER_TRACK_PARM_P                         1

#define SUN_SEAGATE_SERIAL_NUM_PARM_C              16665     // (T514,SunSn_TPARCD,8,0x0001)
#define SUN_SEAGATE_SERIAL_NUM_PARM_P                  1

#define SEND_NON_DBLOG_FORMAT_PARM_C               16666     // (T638,SendNonDBLogFmt_TPARCD,8,NA)
#define SEND_NON_DBLOG_FORMAT_PARM_P                   1

#define EXTEND_LBA34_MSW_PARM_C                    16667     // (T515,Blk_TPARCD,64,NA) (T574,StrtLba_TPARCD,64,NA)
#define EXTEND_LBA34_MSW_PARM_P                        1

#define PAD_SERVO_FLAW_PARM_C                      16668     // (NA, Unused, NA, NA)
#define PAD_SERVO_FLAW_PARM_P                          1

#define PAD_TRACK_PARM_C                           16669     // (NA, Unused, NA, NA)
#define PAD_TRACK_PARM_P                               1

#define SIXTEEN_BYTE_CMD_FORMAT_PARM_C             16670     // (NA, Unused, NA, NA)
#define SIXTEEN_BYTE_CMD_FORMAT_PARM_P                 1

#define SEEK_DIRECTION_PARM_C                      16671     // (T549,SkDrctn_TPARCD,8,NA)
#define SEEK_DIRECTION_PARM_P                          1

#define COMMAND_WORD_9_PARM_C                      16674     // (T538,CmdWrd_TPARCD[8],16,NA) (T599,CmdWrd_TPARCD[0],16,NA)
#define COMMAND_WORD_9_PARM_P                          1

#define COMMAND_WORD_10_PARM_C                     16675     // (T538,CmdWrd_TPARCD[9],16,NA) (T599,CmdWrd_TPARCD[1],16,NA)
#define COMMAND_WORD_10_PARM_P                         1

#define COMMAND_WORD_11_PARM_C                     16676     // (T538,CmdWrd_TPARCD[10],16,NA) (T599,CmdWrd_TPARCD[2],16,NA)
#define COMMAND_WORD_11_PARM_P                         1

#define COMMAND_WORD_12_PARM_C                     16677     // (T538,CmdWrd_TPARCD[11],16,NA) (T599,CmdWrd_TPARCD[3],16,NA)
#define COMMAND_WORD_12_PARM_P                         1

#define COMMAND_WORD_13_PARM_C                     16678     // (T538,CmdWrd_TPARCD[12],16,NA) (T599,CmdWrd_TPARCD[4],16,NA)
#define COMMAND_WORD_13_PARM_P                         1

#define COMMAND_WORD_14_PARM_C                     16679     // (T538,CmdWrd_TPARCD[13],16,NA) (T599,CmdWrd_TPARCD[5],16,NA)
#define COMMAND_WORD_14_PARM_P                         1

#define COMMAND_WORD_15_PARM_C                     16680     // (T538,CmdWrd_TPARCD[14],16,NA) (T599,CmdWrd_TPARCD[6],16,NA)
#define COMMAND_WORD_15_PARM_P                         1

#define COMMAND_WORD_16_PARM_C                     16681     // (T538,CmdWrd_TPARCD[15],16,NA) (T599,CmdWrd_TPARCD[7],16,NA)
#define COMMAND_WORD_16_PARM_P                         1

#define DELAY_AFTER_SAS_LINK_RESET_PARAM_C         16682     // (NA, Unused, NA, NA)
#define DELAY_AFTER_SAS_LINK_RESET_PARAM_P             1

#define ENBL_POS_LOG10_BER_DELTA_PARM_C            16683     // (DEF,EnblPsnLog10Ber_TPARCD,8,0x0001)
#define ENBL_POS_LOG10_BER_DELTA_PARM_P                1

#define LOG10_POS_BER_DELTA_SPEC_PARM_C            16684     // (DEF,LogPsn10Ber_TPARCD,16,NA)
#define LOG10_POS_BER_DELTA_SPEC_PARM_P                1

#define SAFE_SECTORS_PARM_C                        16685     // (T680,SafSctr_TPARCD,16,NA)
#define SAFE_SECTORS_PARM_P                            1

#define START_LBA_E_PARM_C                         16686     // (NA, Unused, NA, NA)
#define START_LBA_E_PARM_P                             1

#define BAND_SIZE_E_PARM_C                         16687     // (NA, Unused, NA, NA)
#define BAND_SIZE_E_PARM_P                             1

#define DELAY_AFTER_SAS_LINK_RESET_PARM_C          16688     // (T506,DlyTmMsec_TPARCD,16,NA)
#define DELAY_AFTER_SAS_LINK_RESET_PARM_P              1

#define START_BTRFLY_LBA34_PARM_C                  16689     // (T510,StrtBtrflyLba_TPARCD,64,NA)
#define START_BTRFLY_LBA34_PARM_P                      4

#define MAXIMUM_IDET_ERROR_CNT_PARM_C              16690     // (T625,MxInitrDtctErr_TPARCD,32,NA)
#define MAXIMUM_IDET_ERROR_CNT_PARM_P                  2

#define MAXIMUM_TDET_ERROR_CNT_PARM_C              16691     // (T625,MxTgtDtctErr_TPARCD,32,NA)
#define MAXIMUM_TDET_ERROR_CNT_PARM_P                  2

#define MAXIMUM_ITDET_ERROR_CNT_PARM_C             16692     // (T625,MxInitrTgtDtctErr_TPARCD,64,NA)
#define MAXIMUM_ITDET_ERROR_CNT_PARM_P                 4

#define SSC_AMPLITUDE_PARM_C                       16693     // (T625,SscAmp_TPARCD,16,NA)
#define SSC_AMPLITUDE_PARM_P                           1

#define SSC_MODE_PARM_C                            16694     // (T625,SscMode_TPARCD,16,NA)
#define SSC_MODE_PARM_P                                1

#define ATI_MAX_CENTER_WRT_PARM_C                  16695     // (T621,AtiMxCentrWr_TPARCD,32,NA)
#define ATI_MAX_CENTER_WRT_PARM_P                      1

#define STE_MAX_CENTER_WRT_PARM_C                  16696     // (NA, Unused, NA, NA)
#define STE_MAX_CENTER_WRT_PARM_P                      1

#define MAX_NON_REC_ERRS_PER_HD_PARM_C             16697     // (T503,MxNonRcovErrHd_TPARCD,16,NA) (T510,MxNonRcovErrHd_TPARCD,16,NA) (T634,MxNonRcovErrHd_TPARCD,16,NA)
#define MAX_NON_REC_ERRS_PER_HD_PARM_P                 1

#define MAX_REC_ERRS_PER_HD_PARM_C                 16698     // (T503,MxRcovErrHd_TPARCD,16,NA) (T510,MxRcovErrHd_TPARCD,16,NA) (T634,MxNonRcovErrHd_TPARCD,16,NA)
#define MAX_REC_ERRS_PER_HD_PARM_P                     1

#define SET_RW_MODE_CTRL_PARM_C                    16699     // (T510,SetRdWrModeCtrl_TPARCD,16,0x00FF) (T510,SetRdWrModeCtrl_TPARCD,16,0xFF00) (T515,SetRdWrModeCtrl_TPARCD,16,0x00FF) (T515,SetRdWrModeCtrl_TPARCD,16,0xFF00)
#define SET_RW_MODE_CTRL_PARM_P                        1

#define MIN_MRE_RESISTANCE_PARM_C                  16700     // (T735,MnMrResist_TPARCD,16,NA)
#define MIN_MRE_RESISTANCE_PARM_P                      1

#define MAX_MRE_RESISTANCE_PARM_C                  16701     // (T735,MxMrResist_TPARCD,16,NA)
#define MAX_MRE_RESISTANCE_PARM_P                      1

#define ZONE_FOR_TEST_MSW_PARM_C                   16702     // (T509,ZnToTst_TPARCD,32,NA)
#define ZONE_FOR_TEST_MSW_PARM_P                       1

#define ZONE_FOR_TEST_LSW_PARM_C                   16703     // (T509,ZnToTst_TPARCD,32,NA)
#define ZONE_FOR_TEST_LSW_PARM_P                       1

#define INVALID_INFO_0311_RETRY_PARM_C             16704     // (T510,InvldInfo0311Rtry_TPARCD,8,NA)
#define INVALID_INFO_0311_RETRY_PARM_P                 1

#define REG_ADD_PARM_C                             16705     // (T510,RegAdd_TPARCD,8,0x00FF) (T515,RegAddr_TPARCD,16,0x00FF)
#define REG_ADD_PARM_P                                 1

#define BANK_PARM_C                                16706     // (T510,Bank_TPARCD,8,0x00FF) (T515,Bank_TPARCD,8,0x00FF)
#define BANK_PARM_P                                    1

#define READ_TYPE_PARM_C                           16707     // (T621,RdTyp_TPARCD,8,NA) (T695,RdTyp_TPARCD,8,NA)
#define READ_TYPE_PARM_P                               1

#define PAGE_BYTE_AND_DATA34_PARM_C                16708     // (T518,PgBytDta_TPARCD[1-16],16,NA)
#define PAGE_BYTE_AND_DATA34_PARM_P                   16

#define TURN_OFF_LONG_LBA_MODE_PARM_C              16709     // (T507,LngLbaModeOff_TPARCD,8,NA)
#define TURN_OFF_LONG_LBA_MODE_PARM_P                  1

#define TURN_OFF_DS_SENSE_PARM_C                   16710     // (NA, Unused, NA, NA)
#define TURN_OFF_DS_SENSE_PARM_P                       1

#define MASTER_AUTHORITY_PARM_C                    16711     // (T575,MstrAuth_TPARCD,8,NA) no functionality
#define MASTER_AUTHORITY_PARM_P                        1

#define MSID_OFFSET_PARM_C                         16712     // (T575,MsidOfst_TPARCD,8,NA) no functionality
#define MSID_OFFSET_PARM_P                             1

#define DESCRPTIVE_SENSE_OPTION_PARM_C             16713     // (T507,DescSnsOptn_TPARCD,8,NA)
#define DESCRPTIVE_SENSE_OPTION_PARM_P                 1

#define USE_TUR_CLEAR_SENSE_PARM_C                 16714     // (T507,EnblTurClrSns_TPARCD,8,0x0002)Enable (T507,EnblTurClrSns_TPARCD,8,0x0001)Set
#define USE_TUR_CLEAR_SENSE_PARM_P                     1

#define ENBL_DELTA_BER_QUAL_FOR_CHECK_PARM_C       16715     // (T509,EnblDltaBerQualChk_TPARCD,8,0x0001)
#define ENBL_DELTA_BER_QUAL_FOR_CHECK_PARM_P           1

#define DELLOCATE_TRACK_PARM_C                     16716     // (T529,DllocTrk_TPARCD,8,0x0001)
#define DELLOCATE_TRACK_PARM_P                         1

#define ID_ZONE_NUM_PARM_C                         16717     // (T598,IdZnNum_TPARCD,8,NA)
#define ID_ZONE_NUM_PARM_P                             1

#define MD_ZONE_NUM_PARM_C                         16718     // (T598,MdZnNum_TPARCD,8,NA)
#define MD_ZONE_NUM_PARM_P                             1

#define OD_ZONE_NUM_PARM_C                         16719     // (T598,OdZnNum_TPARCD,8,NA)
#define OD_ZONE_NUM_PARM_P                             1

#define ID_DATARATE_MAX_PARM_C                     16720     // (T598,IdDtaRat_TPARCD[1],64,NA)
#define ID_DATARATE_MAX_PARM_P                         2

#define OD_DATARATE_MAX_PARM_C                     16721     // (T598,OdDtaRat_TPARCD[1],64,NA)
#define OD_DATARATE_MAX_PARM_P                         2

#define MD_DATARATE_MAX_PARM_C                     16722     // (T598,MdDtaRat_TPARCD[1],64,NA)
#define MD_DATARATE_MAX_PARM_P                         2

#define ID_DATARATE_MIN_PARM_C                     16723     // (T598,IdDtaRat_TPARCD[0],64,NA)
#define ID_DATARATE_MIN_PARM_P                         2

#define OD_DATARATE_MIN_PARM_C                     16724     // (T598,OdDtaRat_TPARCD[0],64,NA)
#define OD_DATARATE_MIN_PARM_P                         2

#define MD_DATARATE_MIN_PARM_C                     16725     // (T598,MdDtaRat_TPARCD[0],64,NA)
#define MD_DATARATE_MIN_PARM_P                         2

#define BLOCK_SIZE_PARM_C                          16726     // (T574,BlkLenByt_TPARCD,16,NA) (T575,BlkLenByt_TPARCD,16,NA) no functionality
#define BLOCK_SIZE_PARM_P                              1

#define BERP_OVERRIDE_PARM_C                       16727     // (DEF,BerpOvrd_TPARCD,16,NA)
#define BERP_OVERRIDE_PARM_P                           1

#define DERP_RETRY_CONTROL_PARM_C                  16728     // (DEF,DerpRtryCtrl_TPARCD,16,NA) (T510,DerpRtryCtrl_TPARCD,16,0x00FF) (T510,DerpRtryCtrl_TPARCD,16,0xFF00) (T515,DerpRtryCtrl_TPARCD,16,0x00FF) (T515,DerpRtryCtrl_TPARCD,16,0xFF00) 
#define DERP_RETRY_CONTROL_PARM_P                      1     // (T1509,DerpRtryCtrl_TPARCD,16,0x00FF) (T1509,DerpRtryCtrl_TPARCD,16,0xFF00) (T5509,DerpRtryCtrl_TPARCD,16,0x00FF) (T5509,DerpRtryCtrl_TPARCD,16,0xFF00)

#define USER_PATT_AVAIL_PARM_C                     16729     // (T597,UsePttrnAvail_TPARCD,16,NA)
#define USER_PATT_AVAIL_PARM_P                         1

#define PATTERN_WORD3_PARM_C                       16730     // (T597,PttrnWrd_TPARCD,64,NA)
#define PATTERN_WORD3_PARM_P                           1

#define PATTERN_WORD2_PARM_C                       16731     // (T597,PttrnWrd_TPARCD,64,NA)
#define PATTERN_WORD2_PARM_P                           1

#define PATTERN_WORD1_PARM_C                       16732     // (T597,PttrnWrd_TPARCD,64,NA)
#define PATTERN_WORD1_PARM_P                           1

#define PATTERN_WORD0_PARM_C                       16733     // (T597,PttrnWrd_TPARCD,64,NA)
#define PATTERN_WORD0_PARM_P                           1

#define WHILE_LOOP_OPTION_PARM_C                   16734     // (T621,WhileLoopOptn_TPARCD,8,NA)
#define WHILE_LOOP_OPTION_PARM_P                       1

#define HEAD_SKEW_TIME_PARM_C                      16735     // (T598,HdSkewTm_TPARCD,16,NA)
#define HEAD_SKEW_TIME_PARM_P                          1

#define MINIZONE_SKEW_TIME_PARM_C                  16736     // (NA, Unused, NA, NA)
#define MINIZONE_SKEW_TIME_PARM_P                      1

#define USING_SCRIPT_SKEW_TIME_PARM_C              16737     // (T598,UseIntrnlSkewTm_TPARCD,8,NA)
#define USING_SCRIPT_SKEW_TIME_PARM_P                  1

#define COMPARE_ALL_TRANSFERS_PARM_C               16738     // (T558,CmprTrnsfr_TPARCD,8,NA)
#define COMPARE_ALL_TRANSFERS_PARM_P                   1

#define DELAY_CHK_INTERRUPT_OPT_PARM_C             16739     // (T507,DlyChkIntrptOptn_TPARCD,8,0x0001) (T507,DlyChkIntrptOptn_TPARCD,8,0x0002)
#define DELAY_CHK_INTERRUPT_OPT_PARM_P                 1

#define RANDOM_LOOPS_PARM_C                        16740     // (T618,RdmLoop_TPARCD,32,NA)
#define RANDOM_LOOPS_PARM_P                            2

#define BUFFER_IOECC_PARM_C                        16741     // (T564,BufIoEcc_TPARCD,8,NA)
#define BUFFER_IOECC_PARM_P                            1

#define FLAW_GAP_SIZE_PARM_C                       16742     // (T529,FlawGapSz_TPARCD,16,0xFFFF)
#define FLAW_GAP_SIZE_PARM_P                           1

#define FLAW_COUNT_PARM_C                          16743     // (T529,FlawCnt_TPARCD,16,0xFFFF)
#define FLAW_COUNT_PARM_P                              1

#define PLIST_SECTOR_DRV_MAX_PARM_C                16744     // (T627,PlistSctrDrvMx_TPARCD,32,NA)
#define PLIST_SECTOR_DRV_MAX_PARM_P                    2

#define PLIST_SECTOR_HD_MAX_PARM_C                 16745     // (T627,PlistSctrHdMx_TPARCD,32,NA)
#define PLIST_SECTOR_HD_MAX_PARM_P                     2

#define PLIST_SECTOR_ZN_MAX_PARM_C                 16746     // (T627,PlistSctrZnMx_TPARCD,32,NA)
#define PLIST_SECTOR_ZN_MAX_PARM_P                     1

#define PLIST_SFI_DRV_MAX_PARM_C                   16747     // (T627,PlistSfiDrvMx_TPARCD,32,NA)
#define PLIST_SFI_DRV_MAX_PARM_P                       2

#define PLIST_SFI_HD_MAX_PARM_C                    16748     // (T627,PlistSfiHdMx_TPARCD,32,NA)
#define PLIST_SFI_HD_MAX_PARM_P                        2

#define PLIST_SFI_ZN_MAX_PARM_C                    16749     // (T627,PlistSfiZnMx_TPARCD,32,NA)
#define PLIST_SFI_ZN_MAX_PARM_P                        1

#define GLIST_DRV_MAX_PARM_C                       16750     // (T627,GlistDrvMx_TPARCD,16,NA)
#define GLIST_DRV_MAX_PARM_P                           1

#define GLIST_HD_MAX_PARM_C                        16751     // (T627,GlistHdMx_TPARCD,16,NA)
#define GLIST_HD_MAX_PARM_P                            1

#define GLIST_ZN_MAX_PARM_C                        16752     // (T627,GlistZnMx_TPARCD,16,NA)
#define GLIST_ZN_MAX_PARM_P                            1

#define SERVO_PRIMARY_DRV_MAX_PARM_C               16753     // (T627,SvoPrimDrvMx_TPARCD,16,NA)
#define SERVO_PRIMARY_DRV_MAX_PARM_P                   1

#define SERVO_PRIMARY_HD_MAX_PARM_C                16754     // (T627,SvoPrimHdMx_TPARCD,16,NA)
#define SERVO_PRIMARY_HD_MAX_PARM_P                    1

#define SERVO_PRIMARY_ZN_MAX_PARM_C                16755     // (T627,SvoPrimZnMx_TPARCD,16,NA)
#define SERVO_PRIMARY_ZN_MAX_PARM_P                    1

#define SERVO_ADDED_DRV_MAX_PARM_C                 16756     // (T627,SvoAddDrvMx_TPARCD,16,NA)
#define SERVO_ADDED_DRV_MAX_PARM_P                     1

#define SERVO_ADDED_HD_MAX_PARM_C                  16757     // (T627,SvoAddHdMx_TPARCD,16,NA)
#define SERVO_ADDED_HD_MAX_PARM_P                      1

#define SERVO_ADDED_ZN_MAX_PARM_C                  16758     // (T627,SvoAddZnMx_TPARCD,16,NA)
#define SERVO_ADDED_ZN_MAX_PARM_P                      1

#define OC_LIMITS_PARM_C                           16759     // (T564,Oclim_TPARCD[0-2],16,NA)
#define OC_LIMITS_PARM_P                               3

#define ALLOW_04_SENSE_CODES_PARM_C                16760     // (T509,Alow04Err_TPARCD,8,NA) (T1509,Alow04Err_TPARCD,8,NA) (T5509,Alow04Err_TPARCD,8,NA)
#define ALLOW_04_SENSE_CODES_PARM_P                    1

#define SYMK_KEY_TYPE_PARM_C                       16761     // (T575,SymmKeyTyp_TPARCD,8,NA)
#define SYMK_KEY_TYPE_PARM_P                           1

#define MAINTSYMK_SUPP_PARM_C                      16762     // (T575,MaintSymmKeySpprt_TPARCD,8,NA)
#define MAINTSYMK_SUPP_PARM_P                          1

#define PRE_NUKE_PREP_PARM_C                       16763     // (T575,PreNuke_TPARCD,16,NA)
#define PRE_NUKE_PREP_PARM_P                           1

#define NUM_SYMBLS_SECTOR_PARM_C                   16764     // (NA, Unused, NA, NA)
#define NUM_SYMBLS_SECTOR_PARM_P                       1

#define OD_SQZ_WRITE_CNT_PARM_C                    16765     // (T629,OdSqzWrCnt_TPARCD,16,NA)
#define OD_SQZ_WRITE_CNT_PARM_P                        1

#define ID_SQZ_WRITE_CNT_PARM_C                    16766     // (T629,IdSqueezeWriteCount_TPARCD,16,NA)
#define ID_SQZ_WRITE_CNT_PARM_P                        1

#define ZONE_RELATIVE_TRACK_PARM_C                 16767     // (DEF,ZnRelTrk_TPARCD,16,NA)
#define ZONE_RELATIVE_TRACK_PARM_P                     1

#define MAX_SWD_FVGA_SPEC_PARM_C                   16768     // (T564,MxSvoFvga_TPARCD,16,NA)
#define MAX_SWD_FVGA_SPEC_PARM_P                       1

#define PERCENT_TO_USE_PARM_C                      16769     // (T1500,PrctToUse_TPARCD,16,NA)
#define PERCENT_TO_USE_PARM_P                          1

#define BAND_COUNT_PARM_C                          16770     // (T1500,BndCnt_TPARCD,16,NA)
#define BAND_COUNT_PARM_P                              1

#define BANDOM_ENABLE_PARM_C                       16771     // (T597,BndmEnbl_TPARCD,8,NA) (T623,BndmEnbl_TPARCD,8,NA)
#define BANDOM_ENABLE_PARM_P                           1

#define SQUEEZE_PARM_C                             16772     // (T629,SqzOfst_TPARCD,16,NA) (T630,SqzOft_TPARCD,16,NA)
#define SQUEEZE_PARM_P                                 1

#define ZONES_TO_TEST_PARM_C                       16773     // (T629,ZnToTst_TPARCD,64,NA)
#define ZONES_TO_TEST_PARM_P                           4

#define PPID_PARM_C                                16774     // (NA, Unused, NA, NA)
#define PPID_PARM_P                                   32

#define CUSTOMER_CONFIG_NUM_PARM_C                 16775     // (NA, Unused, NA, NA)
#define CUSTOMER_CONFIG_NUM_PARM_P                    10

#define SSD_PRODUCT_INFO_BYTE_PARM_C               16776     // (NA, Unused, NA, NA)
#define SSD_PRODUCT_INFO_BYTE_PARM_P                   1

#define READ_DEFECT_SECS_SPEC_PARM_C               16777     // (T529,TmSecSpecEnbl_TPARCD,16,NA) (T530,TmSecSpecEnbl_TPARCD,16,NA)
#define READ_DEFECT_SECS_SPEC_PARM_P                   1

#define READ_DEFECT_MEASURED_TIME_PARM_C           16778     // (T529,EnblMeasTm_TPARCD,8,NA) (T530,EnblMeasTm_TPARCD,8,NA)
#define READ_DEFECT_MEASURED_TIME_PARM_P               1

#define ENABLE_TWO_PT_ACCESS_PARM_C                16779     // (T510,Enbl2PtAccss_TPARCD,8,0x0001)
#define ENABLE_TWO_PT_ACCESS_PARM_P                    1

#define ENABLE_RD_TRACK_SETTLE_PARM_C              16780     // (T510,EnblRdTrkSetl_TPARCD,8,0x0001)
#define ENABLE_RD_TRACK_SETTLE_PARM_P                  1

#define ALT_TWO_PT_ACCESS_PARM_C                   16781     // (T510,Alt2PtAccss_TPARCD,8,0x0001)
#define ALT_TWO_PT_ACCESS_PARM_P                       1

#define TOTAL_BLK_LSW_1_PARM_C                     16782     // (T510,TtlBlkTrnsfr_TPARCD,32,0xFFFF)
#define TOTAL_BLK_LSW_1_PARM_P                         1

#define TOTAL_BLK_MSW_1_PARM_C                     16783     // (T510,TtlBlkTrnsfr_TPARCD,32,0xFFFF)
#define TOTAL_BLK_MSW_1_PARM_P                         1

#define SCALING_FACTOR_PARM_C                      16784     // (T611,ScalFctr_TPARCD,16,NA)
#define SCALING_FACTOR_PARM_P                          1

#define ZONE_POSITION_IO_PARM_C                    16785     // (T1509,ZnPsn_TPARCD[0-2],16,NA) (T5509,ZnPsn_TPARCD[0-2],16,NA)
#define ZONE_POSITION_IO_PARM_P                        3

#define OFFSET_TO_FIRST_REG_BANK_PARM_C            16786     // (T504,InitRegBankOfst_TPARCD,8,NA)
#define OFFSET_TO_FIRST_REG_BANK_PARM_P                1

#define MOTOR_POWER_TRIP_PARM_C                    16787     // (T564,MtrPwrTrp_TPARCD,16,NA)
#define MOTOR_POWER_TRIP_PARM_P                        1

#define PAGE_MOD_DATA_1_PARM_C                     16788     // (T1501,PgModDta1_TPARCD[0-3],16,NA)
#define PAGE_MOD_DATA_1_PARM_P                         4

#define PAGE_MOD_DATA_2_PARM_C                     16789     // (T1501,PgModDta2_TPARCD[0-3],16,NA) 
#define PAGE_MOD_DATA_2_PARM_P                         4

#define PAGE_MOD_DATA_3_PARM_C                     16790     // (T1501,PgModDta3_TPARCD[0-3],16,NA) 
#define PAGE_MOD_DATA_3_PARM_P                         4

#define PAGE_MOD_DATA_4_PARM_C                     16791     // (T1501,PgModDta4_TPARCD[0-3],16,NA) 
#define PAGE_MOD_DATA_4_PARM_P                         4

#define PAGE_MOD_DATA_5_PARM_C                     16792     // (T1501,PgModDta5_TPARCD[0-3],16,NA)
#define PAGE_MOD_DATA_5_PARM_P                         4

#define PAGE_MOD_DATA_6_PARM_C                     16793     // (T1501,PgModDta6_TPARCD[0-3],16,NA) 
#define PAGE_MOD_DATA_6_PARM_P                         4

#define PAGE_MOD_DATA_7_PARM_C                     16794     // (T1501,PgModDta7_TPARCD[0-3],16,NA) 
#define PAGE_MOD_DATA_7_PARM_P                         4

#define PAGE_MOD_DATA_8_PARM_C                     16795     // (T1501,PgModDta8_TPARCD[0-3],16,NA) 
#define PAGE_MOD_DATA_8_PARM_P                         4

#define PAGE_MOD_DATA_9_PARM_C                     16796     // (T1501,PgModDta9_TPARCD[0-3],16,NA) 
#define PAGE_MOD_DATA_9_PARM_P                         4

#define PAGE_MOD_DATA_10_PARM_C                    16797     // (T1501,PgModDta10_TPARCD[0-3],16,NA) 
#define PAGE_MOD_DATA_10_PARM_P                        4

#define FIRST_SKIPPED_PAGE_PARM_C                  16798     // (T537,SkpPg_TPARCD[0],16,NA) (T1501,SkpPg_TPARCD[0],16,NA)
#define FIRST_SKIPPED_PAGE_PARM_P                      1

#define SECOND_SKIPPED_PAGE_PARM_C                 16799     // (T537,SkpPg_TPARCD[1],16,NA) (T1501,SkpPg_TPARCD[1],16,NA)
#define SECOND_SKIPPED_PAGE_PARM_P                     1

#define THIRD_SKIPPED_PAGE_PARM_C                  16800     // (T537,SkpPg_TPARCD[2],16,NA) (T1501,SkpPg_TPARCD[2],16,NA)
#define THIRD_SKIPPED_PAGE_PARM_P                      1

#define FOURTH_SKIPPED_PAGE_PARM_C                 16801     // (T537,SkpPg_TPARCD[3],16,NA) (T1501,SkpPg_TPARCD[3],16,NA)
#define FOURTH_SKIPPED_PAGE_PARM_P                     1

#define FIFTH_SKIPPED_PAGE_PARM_C                  16802     // (T537,SkpPg_TPARCD[4],16,NA) (T1501,SkpPg_TPARCD[4],16,NA)
#define FIFTH_SKIPPED_PAGE_PARM_P                      1

#define SQUEEZE_STEP_SIZE_PARM_C                   16803     // (NA, NA, NA, NA)
#define SQUEEZE_STEP_SIZE_PARM_P                       1

#define MIN_SQUEEZE_PARM_C                         16804     // (NA, NA, NA, NA)
#define MIN_SQUEEZE_PARM_P                             1

#define MAX_SQUEEZE_PARM_C                         16805     // (NA, NA, NA, NA)
#define MAX_SQUEEZE_PARM_P                             1

#define MIN_ERROR_COUNT_FIT_PARM_C                 16806
#define MIN_ERROR_COUNT_FIT_PARM_P                     1

#define MAX_ERROR_COUNT_FAIL_PARM_C                16807
#define MAX_ERROR_COUNT_FAIL_PARM_P                    1

#define OVERLAP_TEST_VALUE_PARM_C                  16808
#define OVERLAP_TEST_VALUE_PARM_P                      1

#define OVERLAP_TEST_LIMIT_PARM_C                  16809
#define OVERLAP_TEST_LIMIT_PARM_P                      1

#define MLIST_OPTION_PARM_C                        16810     // (T529,MfgListOptn_TPARCD,8,0x000F)
#define MLIST_OPTION_PARM_P                            1

#define MAX_MFG_DEFECTS_PER_DIE_PARM_C             16811     // (T529,MxMfgListEntry_TPARCD,16,NA)
#define MAX_MFG_DEFECTS_PER_DIE_PARM_P                 1

#define ADJ_ZN_XFR_RTE_DLTA_PERC_PARM_C            16812     // (T598,AdjcntZnRatPrct_TPARCD,16,0x7FFF) (T598,AdjcntZnRatPrct_TPARCD,16,0x8000)
#define ADJ_ZN_XFR_RTE_DLTA_PERC_PARM_P                1

#define PE_CYCLES_PARM_C                           16813     // (NA, NA, NA, NA)
#define PE_CYCLES_PARM_P                               1

#define READ_CYCLES_PARM_C                         16814     // (NA, NA, NA, NA)
#define READ_CYCLES_PARM_P                             1

#define REPEAT_CYCLE_COUNT_PARM_C                  16815     // (NA, NA, NA, NA)
#define REPEAT_CYCLE_COUNT_PARM_P                      1

#define RD_ERR_HANDLING_PARAMS_PARM_C              16816     // (NA, NA, NA, NA)
#define RD_ERR_HANDLING_PARAMS_PARM_P                  1

#define READ_GLIST_ADD_THRESHOLD_PARM_C            16817     // (NA, NA, NA, NA)
#define READ_GLIST_ADD_THRESHOLD_PARM_P                1

#define BLOCK_SKIP_CONSTANT_PARM_C                 16818     // (NA, NA, NA, NA)
#define BLOCK_SKIP_CONSTANT_PARM_P                     1

#define NUM_PAGES_TO_TEST_PARM_C                   16819     // (NA, NA, NA, NA)
#define NUM_PAGES_TO_TEST_PARM_P                       1

#define BANDOM_DO_NOT_LOOP_PARM_C                  16820     // (NA, Unused, NA, NA)
#define BANDOM_DO_NOT_LOOP_PARM_P                      1

#define TARGET_SQUEEZE_PARM_C                      16821     // (NA, Unused, NA, NA)
#define TARGET_SQUEEZE_PARM_P                          1

#define USE_TARGET_SQUEEZE_PARM_C                  16822     // (NA, Unused, NA, NA)
#define USE_TARGET_SQUEEZE_PARM_P                      1

#define ERROR_CATEGORIZATION_PARM_C                16823     // (T564,ErrCtgry_TPARCD,16,NA) (T1647,ErrCtgry_TPARCD,16,NA)
#define ERROR_CATEGORIZATION_PARM_P                    1

#define DELTA_TIME_INTERVAL_PARM_C                 16824     // (T564,DltaTmIntrvl_TPARCD,16,NA)
#define DELTA_TIME_INTERVAL_PARM_P                     1

#define DELTA_MRE_SPEC_PARM_C                      16825     // (T564,DltaMreSpec_TPARCD,16,NA)
#define DELTA_MRE_SPEC_PARM_P                          1

#define SMART_TIMESTAMP_VALUE_PARM_C               16826     // (T564,SmrtTmStmpVal_TPARCD,64,NA)
#define SMART_TIMESTAMP_VALUE_PARM_P                   4

#define DELTA_BUZZ_COUNT_SPEC_PARM_C               16827     // (T564,DltaBuzCntSpec_TPARCD,8,NA)
#define DELTA_BUZZ_COUNT_SPEC_PARM_P                   1

#define MOTOR_START_UNLATCH_RETRY_CHECK_PARM_C     16828     // (T564,MtrStrtUnltchRtry_TPARCD,8,NA)
#define MOTOR_START_UNLATCH_RETRY_CHECK_PARM_P         1

#define UNLATCH_RETRY_SPEC_PARM_C                  16829     // (T564,UnltchRtrySpec_TPARCD,8,NA)
#define UNLATCH_RETRY_SPEC_PARM_P                      1

#define MOTOR_START_RETRY_SPEC_PARM_C              16830     // (T564,MtrStrtRtrySpec_TPARCD,8,NA)
#define MOTOR_START_RETRY_SPEC_PARM_P                  1

#define MAX_REQD_TLEVEL_PARM_C                     16831     // (NA, Unused, NA, NA)
#define MAX_REQD_TLEVEL_PARM_P                         1

#define LAST_ELAP_TIME_SPEC_PARM_C                 16832
#define LAST_ELAP_TIME_SPEC_PARM_P                     1

#define MAX_BURN_TIME_SPEC_PARM_C                  16833
#define MAX_BURN_TIME_SPEC_PARM_P                      1

#define DIE_ADDRESS_PARM_C                         16834     // (T519,DieAddr_TPARCD,8,NA)
#define DIE_ADDRESS_PARM_P                             1

#define PAGE_ADDRESS_PARM_C                        16835     // (T519,PgAddr_TPARCD,8,NA)
#define PAGE_ADDRESS_PARM_P                            1

#define BLOCK_ADDRESS_PARM_C                       16836     // (T519,BlkAddr_TPARCD,16,NA)
#define BLOCK_ADDRESS_PARM_P                           1

#define READ_RETRY_SPEC_PARM_C                     16837     // (T510,RdRtrySpec_TPARCD,8,0x00FF)
#define READ_RETRY_SPEC_PARM_P                         1

#define EXPECTED_NUM_DIES_PARM_C                   16838     // (T519,ExpctNumDie_TPARCD,8,NA)
#define EXPECTED_NUM_DIES_PARM_P                       1

#define EXPECTED_FLASH_ID_PARM_C                   16839     // (T519,ExpctFlash_TPARCD,64,NA)
#define EXPECTED_FLASH_ID_PARM_P                       4

#define BURN_TIME_UPDATE_PARM_C                    16840
#define BURN_TIME_UPDATE_PARM_P                        1

#define BACK_EMF_TIME_UPDATE_PARM_C                16841
#define BACK_EMF_TIME_UPDATE_PARM_P                    1

#define DISPLAY_CAP_UPDATE_PARM_C                  16842     // (T521,DispCapUpdt_TPARCD,8,NA)
#define DISPLAY_CAP_UPDATE_PARM_P                      1

#define NVC_BURN_TIME_SPEC_PARM_C                  16843
#define NVC_BURN_TIME_SPEC_PARM_P                      1

#define BACK_EMF_TIME_SPEC_PARM_C                  16844
#define BACK_EMF_TIME_SPEC_PARM_P                      1

#define RANGE_START_PARM_C                         16845     // (T575,RgStrt_TPARCD,64,NA)
#define RANGE_START_PARM_P                             1

#define RANGE_LENGTH_PARM_C                        16846     // (T575,RgLen_TPARCD,64,NA)
#define RANGE_LENGTH_PARM_P                            1

#define READ_LOCKED_PARM_C                         16847     // (T575,RdLok_TPARCD,8,NA)
#define READ_LOCKED_PARM_P                             1

#define WRITE_LOCKED_PARM_C                        16848     // (T575,WrLok_TPARCD,8,NA)
#define WRITE_LOCKED_PARM_P                            1

#define READ_LOCK_ENABLED_PARM_C                   16849     // (T575,RdLokEnbl_TPARCD,8,NA)
#define READ_LOCK_ENABLED_PARM_P                       1

#define WRITE_LOCK_ENABLED_PARM_C                  16850     // (T575,WrLokEnbl_TPARCD,8,NA)
#define WRITE_LOCK_ENABLED_PARM_P                      1

#define PORT_LOCKED_PARM_C                         16851     // (T575,PortLok_TPARCD,8,NA) (T577,PortLok_TPARCD,8,NA) no functionality
#define PORT_LOCKED_PARM_P                             1

#define LOCK_ON_RESET_PARM_C                       16852     // (T575,LokOnRst_TPARCD,8,NA)
#define LOCK_ON_RESET_PARM_P                           1

#define BAND_ENABLED_PARM_C                        16854     // (T575,BndEnbl_TPARCD,8,NA)
#define BAND_ENABLED_PARM_P                            1

#define VENDOR_ID_PARM_C                           16855
#define VENDOR_ID_PARM_P                               5

#define MAX_MISCMP_PER_VENDOR_PARM_C               16856
#define MAX_MISCMP_PER_VENDOR_PARM_P                   5

#define MAX_MISCOMPARES_PER_DIE_PARM_C             16857
#define MAX_MISCOMPARES_PER_DIE_PARM_P                 1

#define VENDOR_0_ID_PARM_C                         16858     // (T519,VndrId_TPARCD[0],64,NA)
#define VENDOR_0_ID_PARM_P                             4

#define VENDOR_1_ID_PARM_C                         16859     // (T519,VndrId_TPARCD[1],64,NA)
#define VENDOR_1_ID_PARM_P                             4

#define VENDOR_2_ID_PARM_C                         16860     // (T519,VndrId_TPARCD[2],64,NA)
#define VENDOR_2_ID_PARM_P                             4

#define VENDOR_3_ID_PARM_C                         16861     // (T519,VndrId_TPARCD[3],64,NA)
#define VENDOR_3_ID_PARM_P                             4

#define VENDOR_4_ID_PARM_C                         16862     // (T519,VndrId_TPARCD[4],64,NA)
#define VENDOR_4_ID_PARM_P                             4

#define VENDOR_0_MAX_MISCMP_PARM_C                 16863     // (T519,VndrMx_TPARCD[0],32,NA)
#define VENDOR_0_MAX_MISCMP_PARM_P                     2

#define VENDOR_1_MAX_MISCMP_PARM_C                 16864     // (T519,VndrMx_TPARCD[1],32,NA)
#define VENDOR_1_MAX_MISCMP_PARM_P                     2

#define VENDOR_2_MAX_MISCMP_PARM_C                 16865     // (T519,VndrMx_TPARCD[2],32,NA)
#define VENDOR_2_MAX_MISCMP_PARM_P                     2

#define VENDOR_3_MAX_MISCMP_PARM_C                 16866     // (T519,VndrMx_TPARCD[3],32,NA)
#define VENDOR_3_MAX_MISCMP_PARM_P                     2

#define VENDOR_4_MAX_MISCMP_PARM_C                 16867     // (T519,VndrMx_TPARCD[4],32,NA)
#define VENDOR_4_MAX_MISCMP_PARM_P                     2

#define SAVE_DEFECT_LIST_PARM_C                    16868     // (T519,SavDfctList_TPARCD,8,NA)
#define SAVE_DEFECT_LIST_PARM_P                        1

#define MIN_MR_BIAS_VOLTAGE_PARM_C                 16869     // (T735,MnMrBiasVltg_TPARCD,16,NA)
#define MIN_MR_BIAS_VOLTAGE_PARM_P                     1

#define MAX_MR_BIAS_VOLTAGE_PARM_C                 16870     // (T735,MxMrBiasVltg_TPARCD,16,NA)
#define MAX_MR_BIAS_VOLTAGE_PARM_P                     1

#define MAX_GLIST_ENTRY_PER_DIE_PARM_C             16871     // (T529,MxGlistEntryPerDie_TPARCD,16,NA)
#define MAX_GLIST_ENTRY_PER_DIE_PARM_P                 1

#define UPPER_LIMIT_MRE_SPEC_PARM_C                16872     // (T564,UprLmtMreSpec_TPARCD,16,NA)
#define UPPER_LIMIT_MRE_SPEC_PARM_P                    1

#define LOWER_LIMIT_MRE_SPEC_PARM_C                16873     // (T564,LwrLmtMreSpec_TPARCD,16,NA)
#define LOWER_LIMIT_MRE_SPEC_PARM_P                    1

#define MRE_POS_DELTA_LIMIT_SPEC_PARM_C            16874     // (T564,MrePosDltaLmtSpec_TPARCD,16,NA)
#define MRE_POS_DELTA_LIMIT_SPEC_PARM_P                1

#define MRE_NEG_DELTA_LIMIT_SPEC_PARM_C            16875     // (T564,MreNegDltaLmtSpec_TPARCD,16,NA)
#define MRE_NEG_DELTA_LIMIT_SPEC_PARM_P                1

#define BUFFER_OFFSET_1_PARM_C                     16876     // (T508,RdOfst_TPARCD,32,NA)
#define BUFFER_OFFSET_1_PARM_P                         2

#define BUFFER_OFFSET_2_PARM_C                     16877     // (T508,WrOfst_TPARCD,32,NA)
#define BUFFER_OFFSET_2_PARM_P                         2

#define ISE_VERSION_PARM_C                         16878     // (T575,IseVer_TPARCD,8,NA)
#define ISE_VERSION_PARM_P                             1

#define BIPS_CONTROL_PARM_C                        16879
#define BIPS_CONTROL_PARM_P                            1

#define PLIST_SECTOR_ZN_MAX_MSW_PARM_C             16880     // (T627,PlistSctrZnMxMsw_TPARCD,16,NA)
#define PLIST_SECTOR_ZN_MAX_MSW_PARM_P                 1

#define RAW_TOTAL_SLIP_OPTION_PARM_C               16881
#define RAW_TOTAL_SLIP_OPTION_PARM_P                   1

#define FAIL_ON_MAX_ERROR_PARM_C                   16882
#define FAIL_ON_MAX_ERROR_PARM_P                       1

#define PLIST_SFI_ZN_MAX_MSW_PARM_C                16883
#define PLIST_SFI_ZN_MAX_MSW_PARM_P                    1

#define MERT4_RESTORE_PARM_C                       16884     // (T1647,MertRstr_TPARCD,8,NA)
#define MERT4_RESTORE_PARM_P                           1

#define MERT4_WRITE_PARM_C                         16885     // (T1647,MertWr_TPARCD,8,NA)
#define MERT4_WRITE_PARM_P                             1

#define MERT4_READ_PARM_C                          16886     // (T1647,MertRd_TPARCD,8,NA)
#define MERT4_READ_PARM_P                              1

#define NUM_PE_CYCLES_PARM_C                       16887     // (T1647,NumCycle_TPARCD,32,NA)
#define NUM_PE_CYCLES_PARM_P                           2

#define DRAM_LOG_ERR_THRESHOLD_PARM_C              16888     // (T1647,LogErrThrsh_TPARCD[0-15],16,NA)
#define DRAM_LOG_ERR_THRESHOLD_PARM_P                 16

#define GLIST_ADD_ERR_THRESHOLD_PARM_C             16889     // (T1647,GlistErrThrsh_TPARCD[0-15],16,NA)
#define GLIST_ADD_ERR_THRESHOLD_PARM_P                16

#define NUM_READ_CYCLES_PARM_C                     16890     // (T1647,NumRdCycle_TPARCD,32,NA)
#define NUM_READ_CYCLES_PARM_P                         2

#define NUM_BLOCKS_SUMMARIZED_PARM_C               16891     // (T1647,NumBlk_TPARCD,32,NA)
#define NUM_BLOCKS_SUMMARIZED_PARM_P                   2

#define DOWNLOAD_OVERLAY_PARM_C                    16892     // (T535,DwnldOverlay_TPARCD,16,NA)
#define DOWNLOAD_OVERLAY_PARM_P                        1

#define DISPLAY_WEDGE_PARM_C                       16893
#define DISPLAY_WEDGE_PARM_P                           1

#define DATA_TYPE_PARM_C                           16894     // (T531,DtaTyp_TPARCD,8,NA)
#define DATA_TYPE_PARM_P                               1

#define RANDOM_LBA_ALIGNMENT_PARM_C                16895     // (T510,RdmLbaAlgnmnt_TPARCD,8,NA) (T597,RdmLbaAlgnmnt_TPARCD,8,NA) (T623,RdmLbaAlgnmnt_TPARCD,8,NA)
#define RANDOM_LBA_ALIGNMENT_PARM_P                    1

#define WEAK_HEAD_OCCURRENCE_PARM_C                16896     // (DEF,WeakHdOccur_TPARCD,32,NA)
#define WEAK_HEAD_OCCURRENCE_PARM_P                    2

#define BAND_BIT_MASK_PARM_C                       16897     // (T575,BndBitMsk_TPARCD,16,NA)
#define BAND_BIT_MASK_PARM_P                           1

#define ZONE_RELATIVE_CYL1_PARM_C                  16898
#define ZONE_RELATIVE_CYL1_PARM_P                      1

#define ZONE_RELATIVE_CYL2_PARM_C                  16899
#define ZONE_RELATIVE_CYL2_PARM_P                      1

#define MINIMUM_PREWRT_CLR1_PARM_C                 16900
#define MINIMUM_PREWRT_CLR1_PARM_P                     1

#define MINIMUM_PREWRT_CLR2_PARM_C                 16901
#define MINIMUM_PREWRT_CLR2_PARM_P                     1

#define MAXIMUM_PREWRT_CLR1_PARM_C                 16902
#define MAXIMUM_PREWRT_CLR1_PARM_P                     1

#define MAXIMUM_PREWRT_CLR2_PARM_C                 16903
#define MAXIMUM_PREWRT_CLR2_PARM_P                     1

#define STEP_WRT_PREHEAT_SEARCH1_PARM_C            16904
#define STEP_WRT_PREHEAT_SEARCH1_PARM_P                1

#define STEP_WRT_PREHEAT_SEARCH2_PARM_C            16905
#define STEP_WRT_PREHEAT_SEARCH2_PARM_P                1

#define STEP_WRT_PREHEAT_TEST1_PARM_C              16906
#define STEP_WRT_PREHEAT_TEST1_PARM_P                  1

#define STEP_WRT_PREHEAT_TEST2_PARM_C              16907
#define STEP_WRT_PREHEAT_TEST2_PARM_P                  1

#define DELTA_WRT_CLR1_PARM_C                      16908
#define DELTA_WRT_CLR1_PARM_P                          1

#define DELTA_WRT_CLR2_PARM_C                      16909
#define DELTA_WRT_CLR2_PARM_P                          1

#define NUM_WRITES1_PARM_C                         16910
#define NUM_WRITES1_PARM_P                             1

#define NUM_WRITES2_PARM_C                         16911
#define NUM_WRITES2_PARM_P                             1

#define MAX_POOLED_SFR1_PARM_C                     16912
#define MAX_POOLED_SFR1_PARM_P                         1

#define MAX_POOLED_SFR2_PARM_C                     16913
#define MAX_POOLED_SFR2_PARM_P                         1

#define SFR_TARGET1_PARM_C                         16914
#define SFR_TARGET1_PARM_P                             1

#define SFR_TARGET2_PARM_C                         16915
#define SFR_TARGET2_PARM_P                             1

#define NUM_ITER_READS1_PARM_C                     16916
#define NUM_ITER_READS1_PARM_P                         1

#define NUM_ITER_READS2_PARM_C                     16917
#define NUM_ITER_READS2_PARM_P                         1

#define MAX_NUERS1_PARM_C                          16918
#define MAX_NUERS1_PARM_P                              1

#define MAX_NUERS2_PARM_C                          16919
#define MAX_NUERS2_PARM_P                              1

#define MAX_ABORTED_CMD_RETRY_PARM_C               16920
#define MAX_ABORTED_CMD_RETRY_PARM_P                   1

#define DRIVE_SECURITY_TYPE_PARM_C                 16921     // (T575,DrvSecurTyp_TPARCD,8,NA)
#define DRIVE_SECURITY_TYPE_PARM_P                     1

#define DATE_TIME_PARM_C                           16922
#define DATE_TIME_PARM_P                               6

#define DRAM_LOG_ERR_THRSH_QUAD_PARM_C             16923     // (T1647,LogErrThrshPlane_TPARCD[0-15],16,NA)
#define DRAM_LOG_ERR_THRSH_QUAD_PARM_P                16

#define GLIST_ADD_ERR_THRSH_QUAD_PARM_C            16924
#define GLIST_ADD_ERR_THRSH_QUAD_PARM_P                2

#define REQ_NUM_WRITES1_PARM_C                     16925
#define REQ_NUM_WRITES1_PARM_P                         1

#define REQ_NUM_WRITES2_PARM_C                     16926
#define REQ_NUM_WRITES2_PARM_P                         1

#define QUAD_TO_SINGLE_PLANE_RTY_PARM_C            16927     // (T1647,SnglPlane_TPARCD[0-15],16,NA)
#define QUAD_TO_SINGLE_PLANE_RTY_PARM_P               16

#define MAJOR_REV_PARM_C                           16928
#define MAJOR_REV_PARM_P                               1

#define MINOR_REV_PARM_C                           16929
#define MINOR_REV_PARM_P                               1

#define MAX_CAT_DEFECTS_PER_DIE_PARM_C             16930
#define MAX_CAT_DEFECTS_PER_DIE_PARM_P                 1

#define MAX_TOT_DEFECTS_PER_DIE_PARM_C             16931
#define MAX_TOT_DEFECTS_PER_DIE_PARM_P                 1

#define LIST_CAT_DEFECTS_PER_DIE_PARM_C            16932
#define LIST_CAT_DEFECTS_PER_DIE_PARM_P                1

#define MAX_MFG_DFCTS_PER_PLANE_PARM_C             16933     // (T529,MxMfgEntryPerPlane_TPARCD,16,NA)
#define MAX_MFG_DFCTS_PER_PLANE_PARM_P                 1

#define MERT4_READ_VERBOSE_PARM_C                  16934     // (T1647,MertRdVerbose_TPARCD,8,NA)
#define MERT4_READ_VERBOSE_PARM_P                      1

#define GLIST_RD_FAILURES_PARM_C                   16935     // (T1647,GlistFail_TPARCD[0-15],16,NA)
#define GLIST_RD_FAILURES_PARM_P                      16

#define DATE_TIME_ENABLE_PARM_C                    16936     // (T708,DatTmFlag_TPARCD,8,NA)
#define DATE_TIME_ENABLE_PARM_P                        1

#define DATA_TO_WRITE_PARM_C                       16937     // (T555,DtaToWr_TPARCD,16[0-7],NA)
#define DATA_TO_WRITE_PARM_P                           8

#define WRITE_TO_FILE_PARM_C                       16938     // (T602,WrToFile_TPARCD,8,NA)
#define WRITE_TO_FILE_PARM_P                           1

#define FRAME_NUMBER_PARM_C                        16939
#define FRAME_NUMBER_PARM_P                            1

#define SET_FRAME_NUMBER_PARM_C                    16940
#define SET_FRAME_NUMBER_PARM_P                        1

#define MAX_EXT_CMD_TIMEOUT_RETRY_PARM_C           16941
#define MAX_EXT_CMD_TIMEOUT_RETRY_PARM_P               1

#define COMMAND_TIMEOUT_EXTENSION_PARM_C           16942
#define COMMAND_TIMEOUT_EXTENSION_PARM_P               1

#define LAST_PAGE_IN_RANGE_PARM_C                  16943     // (T1647,LastPg_TPARCD[0-15],16,NA)
#define LAST_PAGE_IN_RANGE_PARM_P                     16

#define MIN_PZT_CAL_SPEC_PARM_C                    16944     // (T564,MnPztCalcSpec_TPARCD,16,NA)
#define MIN_PZT_CAL_SPEC_PARM_P                        1

#define MAX_PZT_CAL_VAR_SPEC_PARM_C                16945     // (T564,MxPztCalcVarSpec_TPARCD,16,NA)
#define MAX_PZT_CAL_VAR_SPEC_PARM_P                    1

#define MAX_PZT_RECOVERY_CNT_PARM_C                16946     // (T564,MxPztRcovCntSpec_TPARCD,16,NA)
#define MAX_PZT_RECOVERY_CNT_PARM_P                    1

#define MAX_WT_FREE_10_SPEC_PARM_C                 16947     // (T564,MxWrFree10Spec_TPARCD,16,NA)
#define MAX_WT_FREE_10_SPEC_PARM_P                     1

#define BYPASS_HEAD_MAPPING_PARM_C                 16948     // (T507,BypasHdMap_TPARCD,8,0x0001) (T507,BypasHdMap_TPARCD,8,0x0002)
#define BYPASS_HEAD_MAPPING_PARM_P                     1

#define RESULT_FILELEN_PARM_C                      16949     // (T531,FileLen_TPARCD,32,NA)
#define RESULT_FILELEN_PARM_P                          2

#define ERASE_INDEX_PARM_C                         16950     // (T1647,EraseIdx_TPARCD,32,NA)
#define ERASE_INDEX_PARM_P                             2

#define BUFFER_IOEDC_PARM_C                        16951     // (T564,BufIoEdc_TPARCD,8,NA)
#define BUFFER_IOEDC_PARM_P                            1

#define TCG_VERSION_PARM_C                         16952     // (T575,TcgVer_TPARCD,8,NA)
#define TCG_VERSION_PARM_P                             1

#define MRE_POS_DELTA_LIMIT_SPEC_BY_HEAD_PARM_C    16953     // (NA, Unused, NA, NA)
#define MRE_POS_DELTA_LIMIT_SPEC_BY_HEAD_PARM_P        1

#define MRE_NEG_DELTA_LIMIT_SPEC_BY_HEAD_PARM_C    16954     // (NA, Unused, NA, NA)
#define MRE_NEG_DELTA_LIMIT_SPEC_BY_HEAD_PARM_P        1

#define TEST_BY_HEAD_PARM_C                        16955
#define TEST_BY_HEAD_PARM_P                            1

#define FEATURE_OPTION_PARM_C                      16956     // (T577,FeatrOptn_TPARCD,64,NA)
#define FEATURE_OPTION_PARM_P                          4

#define MIN_ENTRIES_IN_DDT_PARM_C                  16957     // (T530,MnEntryDst_TPARCD,16,NA)
#define MIN_ENTRIES_IN_DDT_PARM_P                      1

#define KBYTES_PER_CMD_PARM_C                      16958     // (T597,KBytPerCmd_TPARCD,16,NA)
#define KBYTES_PER_CMD_PARM_P                          1

#define MAX_VISIBLE_ERRS_PARM_C                    16959
#define MAX_VISIBLE_ERRS_PARM_P                        8

#define MAX_HIDDEN_ERRS_PARM_C                     16960
#define MAX_HIDDEN_ERRS_PARM_P                         8

#define HOUR_RUN_TIME_TO_CHECK_PARM_C              16961
#define HOUR_RUN_TIME_TO_CHECK_PARM_P                  8

#define SINGLE_HEAD_LOOP_OPTION_PARM_C             16962
#define SINGLE_HEAD_LOOP_OPTION_PARM_P                 1

#define READS_PER_WRITE_PARM_C                     16963
#define READS_PER_WRITE_PARM_P                         1

#define READS_PER_ERR_CHECK_PARM_C                 16964
#define READS_PER_ERR_CHECK_PARM_P                     1

#define BYPASS_UNRECOV_LOCATION_RETRY_PARM_C       16965
#define BYPASS_UNRECOV_LOCATION_RETRY_PARM_P           1

#define FINISH_TESTING_ON_FAIL_PARM_C              16966
#define FINISH_TESTING_ON_FAIL_PARM_P                  1

#define ENABLE_FULLPACK_COVERAGE_PARM_C            16967
#define ENABLE_FULLPACK_COVERAGE_PARM_P                1

#define BYPASS_SPINUP_PARM_C                       16968     // (T517,BypasSpinUp_TPARCD,8,0x0001)
#define BYPASS_SPINUP_PARM_P                           1

#define MIN_FLASH_LIFE_LEFT_PARM_C                 16969     // (T564,FlashLifeLeft_TPARCD,16,0x03FF) (T564,FlashLifeLeft_TPARCD,16,0x8000) 
#define MIN_FLASH_LIFE_LEFT_PARM_P                     1

#define RV_ABS_MEAN_SPEC_PARM_C                    16970
#define RV_ABS_MEAN_SPEC_PARM_P                        1

#define MAX_RV_ABS_MEAN_SPEC_PARM_C                16971
#define MAX_RV_ABS_MEAN_SPEC_PARM_P                    1

#define FULL_CAP_TEST_TIME_PARM_C                  16972     // (T634,TstTm_TPARCD,16,NA)
#define FULL_CAP_TEST_TIME_PARM_P                      1

#define PATTERN_OPTION_PARM_C                      16973
#define PATTERN_OPTION_PARM_P                          1

#define INTERVAL_PARM_C                            16974
#define INTERVAL_PARM_P                                1

#define DISPLAY_PARAMETER_PARM_C                   16975     // (T503,DispParm_TPARCD,16,NA) (T521,DispParm_TPARCD,16,NA)
#define DISPLAY_PARAMETER_PARM_P                       1

#define USE_ABORTED_CMD_RETRY_FILE_PARM_C          16976
#define USE_ABORTED_CMD_RETRY_FILE_PARM_P              1

#define NUMBER_OF_WRITES_READS_PARM_C              16977
#define NUMBER_OF_WRITES_READS_PARM_P                  1

#define MAX_UNLATCH_CURRENT_PARM_C                 16978     // (T564,MxUnltchCrrnt_TPARCD,16,NA)
#define MAX_UNLATCH_CURRENT_PARM_P                     1

#define WRITE_PATTERN_PARM_C                       16979     // (T1647,WrPttrn_TPARCD[0-15],16,NA)
#define WRITE_PATTERN_PARM_P                          16

#define SCRAMBLER_OPTION_PARM_C                    16980     // (T1647,ScrmblrOptn_TPARCD,32,NA)
#define SCRAMBLER_OPTION_PARM_P                        1

#define MERT_RESTORE_PARM_C                        16981     // (T1647,MertRstr_TPARCD,8,NA)
#define MERT_RESTORE_PARM_P                            1

#define MERT_WRITE_PARM_C                          16982     // (T1647,MertWr_TPARCD,8,NA)
#define MERT_WRITE_PARM_P                              1

#define MERT_READ_PARM_C                           16983     // (T1647,MertRd_TPARCD,8,NA)
#define MERT_READ_PARM_P                               1

#define MERT_READ_VERBOSE_PARM_C                   16984     // (T1647,MertRdVerb_TPARCD,8,NA)
#define MERT_READ_VERBOSE_PARM_P                       1

#define MAX_TEMPERATURE_PARM_C                     16985     // (T564,MxTmp_TPARCD,16,NA)
#define MAX_TEMPERATURE_PARM_P                         1

#define MIN_TEMPERATURE_PARM_C                     16986     // (T564,MnTmp_TPARCD,16,NA)
#define MIN_TEMPERATURE_PARM_P                         1

#define SET_SMART_FRAME_REFERENCE_PARM_C           16987
#define SET_SMART_FRAME_REFERENCE_PARM_P               1

#define OVS_RISE_TIME_PARM_C                       16988
#define OVS_RISE_TIME_PARM_P                           1

#define REV_TRANSCEIVER_POLARITY_PARM_C            16989     // (T507,RevrsXcvrPolarity_TPARCD,8,0x0001) (T507,RevrsXcvrPolarity_TPARCD,8,0x0002)
#define REV_TRANSCEIVER_POLARITY_PARM_P                1

#define NVC_BURN_FAILED_SPEC_PARM_C                16990     // (T521,BurnFail_TPARCD,32,NA)
#define NVC_BURN_FAILED_SPEC_PARM_P                    2

#define EMULATION_SCALE_PARM_C                     16991     // (T530,Scal_TPARCD,16,NA)
#define EMULATION_SCALE_PARM_P                         1

#define SMART_NUMBER_OF_BYTES_PARM_C               16992     // (T564,SmrtNumByt_TPARCD,16,NA)
#define SMART_NUMBER_OF_BYTES_PARM_P                   1

#define SMART_RAW_REPORT_CONTROL_PARM_C            16993     // (T564,SmrtRawRprtCtrl_TPARCD,16,NA)
#define SMART_RAW_REPORT_CONTROL_PARM_P                1

#define ATTRIBUTE_NAME_PARM_C                      16994     // (T564,AttrNam_TPARCD[0-19],16,NA)
#define ATTRIBUTE_NAME_PARM_P                         20

#define SMART_BYTE_OFFSET_PARM_C                   16995     // (T564,SmrtBytOfst_TPARCD,16,NA)
#define SMART_BYTE_OFFSET_PARM_P                       1

#define DRAM_LOG_ERR_THRSH_MULT_PARM_C             16996     // (T1647,LogErrThrshPlane_TPARCD[0-15],16,NA)
#define DRAM_LOG_ERR_THRSH_MULT_PARM_P                16

#define MULT_TO_SINGLE_PLANE_RTY_PARM_C            16997     // (T1647,SnglPlane_TPARCD[0-15],16,NA)
#define MULT_TO_SINGLE_PLANE_RTY_PARM_P               16

#define QUICK_FORMAT_PARM_C                        16998
#define QUICK_FORMAT_PARM_P                            1

#define WEDGES_MULTI_PARM_C                        16999
#define WEDGES_MULTI_PARM_P                            2

#define WEDGES_SINGLE_PARM_C                       17000
#define WEDGES_SINGLE_PARM_P                           2

#define RADIAL_PAD_SIZE_TRACKS_PARM_C              17001
#define RADIAL_PAD_SIZE_TRACKS_PARM_P                  2

#define SPEC_CUMULATIVE_PARM_C                     17002
#define SPEC_CUMULATIVE_PARM_P                         2

#define SPEC_AVERAGE_PARM_C                        17003
#define SPEC_AVERAGE_PARM_P                            2

#define SPEC_MIN_PARM_C                            17004
#define SPEC_MIN_PARM_P                                2

#define SPEC_MAX_PARM_C                            17005
#define SPEC_MAX_PARM_P                                2

#define SPEC_CURRENT_PARM_C                        17006
#define SPEC_CURRENT_PARM_P                            2

#define OVS_FALL_TIME_PARM_C                       17007
#define OVS_FALL_TIME_PARM_P                           1

#define OVERLAP_TEST_VALUE_INC_PARM_C              17008
#define OVERLAP_TEST_VALUE_INC_PARM_P                  1
 
#define CHANNEL_END_PARM_C                         17009
#define CHANNEL_END_PARM_P                             1

#define CHANNEL_STEP_PARM_C                        17010
#define CHANNEL_STEP_PARM_P                            1

#define DIE_START_PARM_C                           17011
#define DIE_START_PARM_P                               1
 
#define DIE_END_PARM_C                             17012
#define DIE_END_PARM_P                                 1

#define DIE_STEP_PARM_C                            17013
#define DIE_STEP_PARM_P                                1

#define BLOCK_START_PARM_C                         17014
#define BLOCK_START_PARM_P                             1
 
#define BLOCK_END_PARM_C                           17015
#define BLOCK_END_PARM_P                               1

#define BLOCK_STEP_PARM_C                          17016
#define BLOCK_STEP_PARM_P                              1

#define RELAX_WAIT_TIME_PARM_C                     17017
#define RELAX_WAIT_TIME_PARM_P                         2

#define ERASE_ERR_COUNT_THRSH_PARM_C               17018
#define ERASE_ERR_COUNT_THRSH_PARM_P                   1

#define PROGRAM_ERR_COUNT_THRSH_PARM_C             17019
#define PROGRAM_ERR_COUNT_THRSH_PARM_P                 1

#define AVG_ERASE_TIME_THRSH_PARM_C                17020
#define AVG_ERASE_TIME_THRSH_PARM_P                    2

#define LWR_PAGE_PRGM_TIME_THRSH_PARM_C            17021
#define LWR_PAGE_PRGM_TIME_THRSH_PARM_P                2

#define MID_PAGE_PRGM_TIME_THRSH_PARM_C            17022
#define MID_PAGE_PRGM_TIME_THRSH_PARM_P                2

#define UPR_PAGE_PRGM_TIME_THRSH_PARM_C            17023
#define UPR_PAGE_PRGM_TIME_THRSH_PARM_P                2

#define LWR_PAGE_BER_THRSH_PARM_C                  17024
#define LWR_PAGE_BER_THRSH_PARM_P                      1

#define MID_PAGE_BER_THRSH_PARM_C                  17025
#define MID_PAGE_BER_THRSH_PARM_P                      1

#define UPR_PAGE_BER_THRSH_PARM_C                  17026
#define UPR_PAGE_BER_THRSH_PARM_P                      1

#define CHANNEL_START_PARM_C                       17027
#define CHANNEL_START_PARM_P                           1

#define NUMBER_BLOCKS_TO_TEST_PARM_C               17028
#define NUMBER_BLOCKS_TO_TEST_PARM_P                   1

#define DC_DETCR_PARM_C                            17029
#define DC_DETCR_PARM_P                               11 

#define DETCR_DETECTOR_PARM_C                      17030
#define DETCR_DETECTOR_PARM_P                         10

#define LASER_PARM_C                               17031
#define LASER_PARM_P                                   3

#define PD_FILTER_PARM_C                           17032
#define PD_FILTER_PARM_P                               3

#define PD_GAIN_PARM_C                             17033
#define PD_GAIN_PARM_P                                 3

#define HEAT_OVERRRIDE_PARM_C                      17034
#define HEAT_OVERRRIDE_PARM_P                          1

#define LASER_CURRENT_STEP_SIZE_PARM_C             17035
#define LASER_CURRENT_STEP_SIZE_PARM_P                 1

#define TARGET_IOP_CURRENT_PARM_C                  17036
#define TARGET_IOP_CURRENT_PARM_P                      1

#define TARGET_ITHRESH_CURRENT_PARM_C              17037
#define TARGET_ITHRESH_CURRENT_PARM_P                  1

#define SERVO_OFFSET_RANGE_PARM_C                  17038
#define SERVO_OFFSET_RANGE_PARM_P                      2

#define THRESHOLD_SETTING_PARM_C                   17039
#define THRESHOLD_SETTING_PARM_P                       4

#define WEDGE_COUNT_PARM_C                         17040
#define WEDGE_COUNT_PARM_PARM_P                        4

#define NUM_GUARD_TRACKS_PARM_C                    17041
#define NUM_GUARD_TRACKS_PARM_P                       16

#define ZONE_MASK_BITS_PARM_C                      17042
#define ZONE_MASK_BITS_PARM_P                         20

#define TEST_BLOCKS_PARM_C                         17043
#define TEST_BLOCKS_PARM_P                             4

#define MAX_PLIST_ENTRIES_PARM_C                   17044
#define MAX_PLIST_ENTRIES_PARM_P                       1

#define HAMR_MODE_PARM_C                           17045
#define HAMR_MODE_PARM_P                               1

#define TARGET_PD_OUTPUT_PARM_C                    17046
#define TARGET_PD_OUTPUT_PARM_P                        1

#define HAMR_CONTROL_PARM_C                        17047
#define HAMR_CONTROL_PARM_P                            1

#define ENABLE_ZONE_MASK_BITS_PARM_C               17048
#define ENABLE_ZONE_MASK_BITS_PARM_P                   1

#define ENBL_SAVE_CMP_ZONE_MASK_BITS_PARM_C        17049
#define ENBL_SAVE_CMP_ZONE_MASK_BITS_PARM_P            1

#define SAVE_CMP_ZONE_MASK_BITS_PARM_C             17050
#define SAVE_CMP_ZONE_MASK_BITS_PARM_P                20

#define CHANNEL_MODE_PARM_C                        17051
#define CHANNEL_MODE_PARM_P                            1

#define NUM_HD_SWITCH_SAMPLES_PARM_C               17052
#define NUM_HD_SWITCH_SAMPLES_PARM_P                   1

#define REDUNDANT_OFFSET_PARM_C                    17053
#define REDUNDANT_OFFSET_PARM_P                        1

#define NUM_REDUNDANT_MSRMNTS_PARM_C               17054
#define NUM_REDUNDANT_MSRMNTS_PARM_P                   1

#define LOAD_UNLOAD_CYCLES_PARM_C                  17055
#define LOAD_UNLOAD_CYCLES_PARM_P                      1

#define MIN_OVERPROVISION_LEFT_PARM_C              17056
#define MIN_OVERPROVISION_LEFT_PARM_P                  1

#define FIELD_CMP_OPTION_PARM_C                    17057
#define FIELD_CMP_OPTION_PARM_P                        1

#define FIELD_DATA_SIZE_PARM_C                     17058
#define FIELD_DATA_SIZE_PARM_P                         1

#define TRANSFER_LENGTH_LIST_PARM_C                17059
#define TRANSFER_LENGTH_LIST_PARM_P                   20

#define LBA_OFFSET_PARM_C                          17060
#define LBA_OFFSET_PARM_P                              4


/****************************************************************************************************************************

 #     #    ##    #####    #    #  ###  #    #   ####
 #  #  #   #  #   #    #   # #  #   #   # #  #  #
 # # # #  ######  #####    #  # #   #   #  # #  #  ###
 ##   ##  #    #  #    #   #   ##   #   #   ##  #    #
 #     #  #    #  #     #  #    #  ###  #    #   ####

 Check the deprecation and modification policies at the top of this file before making changes.

*****************************************************************************************************************************/


// *******************  SATATEST Unique Parameter definitions  (Starts @ 32000) *********************************

#define CTRL_WORD1_PARM_C                     32000     // (T595,CtrlWrd_TPARCD,16,NA) (T1559,CtrlWrd_TPARCD,16,NA)
#define CTRL_WORD1_PARM_P                         1

#define CTRL_WORD2_PARM_C                     32001
#define CTRL_WORD2_PARM_P                         1

#define STARTING_LBA_PARM_C                   32002
#define STARTING_LBA_PARM_P                       4

#define TOTAL_BLKS_TO_XFR_PARM_C              32003     // (DEF,BlkCnt_TPARCD,32,NA) (T598,TtlBlkTrnsfr_TPARCD,32,NA) (T623,TtlBlkTrnsfr_TPARCD,32,NA)
#define TOTAL_BLKS_TO_XFR_PARM_P                  2

#define BLKS_PER_XFR_PARM_C                   32004     // (T598,BlkPerTrnsfr_TPARCD,16,NA)
#define BLKS_PER_XFR_PARM_P                       1

#define DATA_PATTERN0_PARM_C                  32005     // (DEF,DtaPttrn_TPARCD[0-1],16,NA)
#define DATA_PATTERN0_PARM_P                      2

#define DATA_PATTERN1_PARM_C                  32006     // (DEF,DtaPttrn_TPARCD[2-3],16,NA)
#define DATA_PATTERN1_PARM_P                      2

#define RANDOM_SEED_PARM_C                    32007     // (DEF,RdmSeed_TPARCD,16,NA) (T522,RndSeed_TPARCD,16,NA)
#define RANDOM_SEED_PARM_P                        1

#define MAX_NBR_ERRORS_PARM_C                 32008
#define MAX_NBR_ERRORS_PARM_P                     1

#define BYTE_OFFSET_PARM_C                    32009
#define BYTE_OFFSET_PARM_P                        2

#define BUFFER_LENGTH_PARM_C                  32010     // (T508,BufLen_TPARCD,32,NA)
#define BUFFER_LENGTH_PARM_P                      2

#define BIT_PATTERN_LENGTH_PARM_C             32011     // (DEF,BitPttrnLen_TPARCD,16,NA)
#define BIT_PATTERN_LENGTH_PARM_P                 1

#define BYTE_PATTERN_LENGTH_PARM_C            32012     // (DEF,BitPttrnLen_TPARCD,16,NA)
#define BYTE_PATTERN_LENGTH_PARM_P                1

#define PATTERN_TYPE_PARM_C                   32013
#define PATTERN_TYPE_PARM_P                       1

#define SUB_CMD_CODE_PARM_C                   32014
#define SUB_CMD_CODE_PARM_P                       1

#define SUB_CMD_SCNT_PARM_C                   32015
#define SUB_CMD_SCNT_PARM_P                       1

#define SUB_CMD_SCTR_PARM_C                   32016
#define SUB_CMD_SCTR_PARM_P                       1

#define SUB_CMD_CYL_L_PARM_C                  32017
#define SUB_CMD_CYL_L_PARM_P                      1

#define SUB_CMD_CYL_H_PARM_C                  32018
#define SUB_CMD_CYL_H_PARM_P                      1

#define RESET_AFTER_ERROR_PARM_C              32019
#define RESET_AFTER_ERROR_PARM_P                  1

#define PARAMETER_0_PARM_C                    32020     // (DEF,ParmWrd_TPARCD[0],16,NA) (T638,CmdWrd_TPARCD[0],16,NA)
#define PARAMETER_0_PARM_P                        1

#define PARAMETER_1_PARM_C                    32021     // (DEF,ParmWrd_TPARCD[1],16,NA) (T552,TstMode_TPARCD,16,NA) (T599,TstMode_TPARCD,16,NA) (T638,CmdWrd_TPARCD[1],16,NA) (T714,AltVndrId_TPARCD[0],16,NA) 
#define PARAMETER_1_PARM_P                        1

#define PARAMETER_2_PARM_C                    32022     // (DEF,ParmWrd_TPARCD[2],16,NA) (T638,CmdWrd_TPARCD[2],16,NA) (T714,AltVndrId_TPARCD[1],16,NA)
#define PARAMETER_2_PARM_P                        1

#define PARAMETER_3_PARM_C                    32023     // (DEF,ParmWrd_TPARCD[3],16,NA) (T638,CmdWrd_TPARCD[3],16,NA) (T707,AltVndrId_TPARCD[0],16,NA) (T714,AltVndrId_TPARCD[2],16,NA)
#define PARAMETER_3_PARM_P                        1

#define PARAMETER_4_PARM_C                    32024     // (DEF,ParmWrd_TPARCD[4],16,NA) (T638,CmdWrd_TPARCD[4],16,NA) (T707,AltVndrId_TPARCD[1],16,NA) (T714,NrmlFctr_TPARCD,16,NA)
#define PARAMETER_4_PARM_P                        1

#define PARAMETER_5_PARM_C                    32025     // (DEF,ParmWrd_TPARCD[5],16,NA) (T638,CmdWrd_TPARCD[5],16,NA) (T707,AltVndrId_TPARCD[2],16,NA) (T714,AvgCqmOfst_TPARCD,16,NA)
#define PARAMETER_5_PARM_P                        1

#define PARAMETER_6_PARM_C                    32026     // (DEF,ParmWrd_TPARCD[6],16,NA) (T638,CmdWrd_TPARCD[6],16,NA) (T707,NrmlVgaFctr_TPARCD,16,NA) (T714,DltaLogCqmSpec_TPARCD,16,NA)
#define PARAMETER_6_PARM_P                        1

#define PARAMETER_7_PARM_C                    32027     // (DEF,ParmWrd_TPARCD[7],16,NA) (T638,CmdWrd_TPARCD[7],16,NA) (T714,B2DDltaSpec_TPARCD,16,NA)
#define PARAMETER_7_PARM_P                        1

#define PARAMETER_8_PARM_C                    32028     // (DEF,ParmWrd_TPARCD[8],16,NA) (T638,CmdWrd_TPARCD[8],16,NA) (T714,MultB2DDltaSpec_TPARCD,16,NA)
#define PARAMETER_8_PARM_P                        1

#define PARAMETER_9_PARM_C                    32029     // (DEF,ParmWrd_TPARCD[9],16,NA) (T714,OptnMode_TPARCD,16,0x0001) (T714,OptnMode_TPARCD,16,0x0002) (T714,OptnMode_TPARCD,16,0x0004) (T714,OptnMode_TPARCD,16,0x0008) (T714,OptnMode_TPARCD,16,0x0010) (T714,OptnMode_TPARCD,16,0x0020)
#define PARAMETER_9_PARM_P                        1

#define PARAMETER_10_PARM_C                   32030     // (DEF,ParmWrd_TPARCD[10],16,NA)
#define PARAMETER_10_PARM_P                       1

#define PARAMETER_11_PARM_C                   32031     // (DEF,ParmWrd_TPARCD[11],16,NA)
#define PARAMETER_11_PARM_P                       1

#define PARAMETER_12_PARM_C                   32032     // (DEF,ParmWrd_TPARCD[12],16,NA)
#define PARAMETER_12_PARM_P                       1

#define PARAMETER_13_PARM_C                   32033     // (DEF,ParmWrd_TPARCD[13],16,NA)
#define PARAMETER_13_PARM_P                       1

#define PARAMETER_14_PARM_C                   32034     // (DEF,ParmWrd_TPARCD[14],16,NA)
#define PARAMETER_14_PARM_P                       1

#define PARAMETER_15_PARM_C                   32035     // (DEF,ParmWrd_TPARCD[15],16,NA)
#define PARAMETER_15_PARM_P                       1

#define MINIMUM_LBA_PARM_C                    32036
#define MINIMUM_LBA_PARM_P                        4

#define MAXIMUM_LBA_PARM_C                    32037
#define MAXIMUM_LBA_PARM_P                        4

#define READ_PERCENTAGE_PARM_C                32038
#define READ_PERCENTAGE_PARM_P                    1

#define WRITE_XFR_LENGTH_PARM_C               32039     // (T555,WrTrnsfrLen_TPARCD,16,NA)
#define WRITE_XFR_LENGTH_PARM_P                   1

#define READ_XFR_LENGTH_PARM_C                32040
#define READ_XFR_LENGTH_PARM_P                    1

#define QUEUE_LIST_SIZE_PARM_C                32041
#define QUEUE_LIST_SIZE_PARM_P                    1

#define QUEUE_SIZE_PARM_C                     32042
#define QUEUE_SIZE_PARM_P                         1

#define LOOP_COUNT_PARM_C                     32043     // (T522,LoopCnt_TPARCD,16,NA) (T575,LoopCnt_TPARCD,16,NA) (T618,LoopCnt_TPARCD,16,NA) (T707,LoopCnt_TPARCD,16,0x00FF) (T731,LoopCnt_TPARCD,16,0x00FF)
#define LOOP_COUNT_PARM_P                         1

#define INTERFACE_SPEED_PARM_C                32044
#define INTERFACE_SPEED_PARM_P                    1

#define COMMAND_PARM_C                        32045
#define COMMAND_PARM_P                            1

#define FEATURES_PARM_C                       32046
#define FEATURES_PARM_P                           1

#define LBA_LOW_PARM_C                        32047
#define LBA_LOW_PARM_P                            1

#define LBA_MID_PARM_C                        32048
#define LBA_MID_PARM_P                            1

#define LBA_HIGH_PARM_C                       32049
#define LBA_HIGH_PARM_P                           1

#define LBA_PARM_C                            32050
#define LBA_PARM_P                                4

#define DEVICE_PARM_C                         32051
#define DEVICE_PARM_P                             1

#define SECTOR_COUNT_PARM_C                   32052
#define SECTOR_COUNT_PARM_P                       1

#define STARTING_ZONE_PARM_C                  32053
#define STARTING_ZONE_PARM_P                      1

#define ENDING_ZONE_PARM_C                    32054
#define ENDING_ZONE_PARM_P                        1

#define DFB_WORD_0_PARM_C                     32055
#define DFB_WORD_0_PARM_P                         1

#define DFB_WORD_1_PARM_C                     32056
#define DFB_WORD_1_PARM_P                         1

#define DFB_WORD_2_PARM_C                     32057
#define DFB_WORD_2_PARM_P                         1

#define DFB_WORD_3_PARM_C                     32058
#define DFB_WORD_3_PARM_P                         1

#define DFB_WORD_4_PARM_C                     32059
#define DFB_WORD_4_PARM_P                         1

#define DFB_WORD_5_PARM_C                     32060
#define DFB_WORD_5_PARM_P                         1

#define DFB_WORD_6_PARM_C                     32061
#define DFB_WORD_6_PARM_P                         1

#define DFB_WORD_7_PARM_C                     32062
#define DFB_WORD_7_PARM_P                         1

#define DFB_WORD_8_PARM_C                     32063
#define DFB_WORD_8_PARM_P                         1

#define DFB_WORD_9_PARM_C                     32064
#define DFB_WORD_9_PARM_P                         1

#define DFB_WORD_10_PARM_C                    32065
#define DFB_WORD_10_PARM_P                        1

#define DFB_WORD_11_PARM_C                    32066
#define DFB_WORD_11_PARM_P                        1

#define ZONE_CPC_PARM_C                       32067
#define ZONE_CPC_PARM_P                           1

#define MULTIPLIER_PARM_C                     32068     // (DEF,SerpCnt_TPARCD,16,NA) (T618,LoopMult_TPARCD,8,0x0001) (T621,WrCntMult_TPARCD,16,NA) (T730,MultParm_TPARCD,8,NA)
#define MULTIPLIER_PARM_P                         1

#define DEBUG_FLAG_PARM_C                     32069     // (T521,DbgFlag_TPARCD,8,NA) (T575,DbgFlag_TPARCD,8,NA) no functionality
#define DEBUG_FLAG_PARM_P                         1

#define FREE_RETRY_CONTROL_PARM_C             32070     // (DEF,ErrRcovCtrl_TPARCD,16,0x0002) (T532,FreeRtry_TPARCD,8,0x0001) (T551,FreeRtry_TPARCD,8,NA)
#define FREE_RETRY_CONTROL_PARM_P                 1

#define HIDDEN_RETRY_CONTROL_PARM_C           32071     // (DEF,ErrRcovCtrl_TPARCD,16,0x0008) (T532,ExecHidnRtry_TPARCD,8,0x0001) (T551,ExecHidnRtry_TPARCD,8,0x0001) (T591,DisblHidnRtry_TPARCD,8,0x0001)
#define HIDDEN_RETRY_CONTROL_PARM_P               1

#define RPT_HIDDEN_RETRY_CNTRL_PARM_C         32072     // (DEF,ErrRcovCtrl_TPARCD,16,0x0004) (T532,RprtHidnRtry_TPARCD,8,0x0001) (T551,RprtHidnRtry_TPARCD,8,0x0001)
#define RPT_HIDDEN_RETRY_CNTRL_PARM_P             1

#define DISABLE_ECC_ON_THE_FLY_PARM_C         32073     // (DEF,DisblEccFly_TPARCD,8,0x0001) (T551,DisblEccFly_TPARCD,8,NA)
#define DISABLE_ECC_ON_THE_FLY_PARM_P             1

#define ECC_CONTROL_PARM_C                    32074     // (DEF,TlvlCtrl_TPARCD[0],16,0x0001) index[0] = enable index[1] = T-Level (T509,EccCtrl_TPARCD,16,0x00FF) (T509,EccCtrl_TPARCD,16,0x0100) (T510,EccCtrl_TPARCD,16,0x00FF) (T510,EccCtrl_TPARCD,16,0x0100)
#define ECC_CONTROL_PARM_P                        1     // (T621,EccCtrl_TPARCD,16,0x00FF) (T621,EccCtrl_TPARCD,16,0x0100) (T634,EccCtrl_TPARCD,16,0x00FF) (T634,EccCtrl_TPARCD,16,0x0100) (T1509,EccCtrl_TPARCD,16,0x00FF) (T1509,EccCtrl_TPARCD,16,0x0100) (T5509,EccCtrl_TPARCD,16,0x00FF) (T5509,EccCtrl_TPARCD,16,0x0100)

#define ECC_T_LEVEL_PARM_C                    32075     // (DEF,TlvlCtrl_TPARCD[1],16,NA)
#define ECC_T_LEVEL_PARM_P                        1

#define TEST_RUN_TIME_PARM_C                  32076
#define TEST_RUN_TIME_PARM_P                      1

#define SIDE_TRACK_RANGE_PARM_C               32077
#define SIDE_TRACK_RANGE_PARM_P                   1

#define USR_MAX_CENTER_WRITES_PARM_C          32078     // (T621,MxCentrWr_TPARCD,8,0x0001)
#define USR_MAX_CENTER_WRITES_PARM_P              1

#define TEST_CYLINDER_PARM_C                  32079     // (DEF,TstCyl_TPARCD,32,NA)
#define TEST_CYLINDER_PARM_P                      2

#define STE_MAX_ERASURE_SPEC_PARM_C           32080     // (DEF,SteMxEraseLmt_TPARCD,F,NA) (T621,SteMxEraseSpec_TPARCD,16,0x0FFF)
#define STE_MAX_ERASURE_SPEC_PARM_P               1

#define ATI_OD_SPEC_PARM_C                    32081     // (T621,AtiOdSpec_TPARCD,16,0x0FFF)
#define ATI_OD_SPEC_PARM_P                        1

#define ATI_ID_SPEC_PARM_C                    32082     // (T621,AtiIdSpec_TPARCD,16,0x0FFF)
#define ATI_ID_SPEC_PARM_P                        1

#define MIN_ERROR_COUNT_PARM_C                32083
#define MIN_ERROR_COUNT_PARM_P                    1

#define MAX_SECTORS_TO_READ_PARM_C            32084
#define MAX_SECTORS_TO_READ_PARM_P                2

#define MAX_REC_ERRORS_PARM_C                 32085     // (T510,MxReErr_TPARCD,16,NA)
#define MAX_REC_ERRORS_PARM_P                     1

#define MAX_NON_REC_ERRORS_PARM_C             32086
#define MAX_NON_REC_ERRORS_PARM_P                 1

#define NUM_SERP_PARM_C                       32087
#define NUM_SERP_PARM_P                           1

#define OFFSET_VALUE_PARM_C                   32088     // (T515,OfstVal_TPARCD,16,0x00FF) (T515,OfstVal_TPARCD,16,0x0F00) (T515,OfstVal_TPARCD,16,0x1000) (T515,OfstVal_TPARCD,16,0x2000)(T515,OfstVal_TPARCD,16,0x4000) (T515,OfstVal_TPARCD,16,0x8000) (T539,OfstVal_TPARCD,16,0x0001) (T539,OfstVal_TPARCD,16,0x00C0) (T539,OfstVal_TPARCD,16,0x00FF) (T539,OfstVal_TPARCD,16,0xFF00) 
#define OFFSET_VALUE_PARM_P                       1     // (T611,OfstVal_TPARCD,16,NA) (T705,OfstVal_TPARCD,16,0x00C0) (T705,OfstVal_TPARCD,16,0xFF00) (T714,OfstVal_TPARCD,16,NA) (T731,OfstVal_TPARCD,16,0x00FF)

#define NUMBER_OF_PATTERNS_PARM_C             32089
#define NUMBER_OF_PATTERNS_PARM_P                 1

#define VERIFY_COUNT_PARM_C                   32090
#define VERIFY_COUNT_PARM_P                       1

#define TEST_FUNCTION_PARM_C                  32091     // (DEF,TstFunc_TPARCD,16,NA) (T504,TstFunc_TPARCD,16,0x8000) (T505,TstFunc_TPARCD,16,NA) no functionality (T506,TstFunc_TPARCD,16,NA) no functionality (T507,TstFunc_TPARCD,16,0x8000) (T509,TstFunc_TPARCD,16,0x0800) (T510,TstFunc_TPARCD,16,0x8000) (T514,TstFunc_TPARCD,16,0x8000) (T518,TstFunc_TPARCD,16,0xF000) (T535,TstFunc_TPARCD,16,0x8000)
#define TEST_FUNCTION_PARM_P                      1     // (T539,TstFunc_TPARCD,16,0x0100) (T555,TstFunc_TPARCD,16,0x0003) (T557,TstFunc_TPARCD,16,0x8000) (T597,TstFunc_TPARCD,16,0x3000) (T602,TstFunc_TPARCD,16,0x0300) (T623,TstFunc_TPARCD,16,0x0003) (T623,TstFunc_TPARCD,16,0x8000) (T638,TstFunc_TPARCD,16,0x0001) (T707,TstFunc_TPARCD,16,0x2000) (T718,TstFunc_TPARCD,16,0x0800) (T1509,TstFunc_TPARCD,16,0x0800) (T5509,TstFunc_TPARCD,16,0x0800)

#define MAX_REC_UNVERIFIED_PARM_C             32092
#define MAX_REC_UNVERIFIED_PARM_P                 1

#define MAX_REC_VERIFIED_PARM_C               32093
#define MAX_REC_VERIFIED_PARM_P                   1

#define MAX_UNREC_UNVERIFIED_PARM_C           32094
#define MAX_UNREC_UNVERIFIED_PARM_P               1

#define MAX_UNREC_VERIFIED_PARM_C             32095
#define MAX_UNREC_VERIFIED_PARM_P                 1

#define MAX_UNVERIFIED_PARM_C                 32096
#define MAX_UNVERIFIED_PARM_P                     1

#define MAX_VERIFIED_PARM_C                   32097
#define MAX_VERIFIED_PARM_P                       1

#define CCT_BIN_SETTINGS_PARM_C               32098
#define CCT_BIN_SETTINGS_PARM_P                   1

#define MIN_SECTOR_COUNT_PARM_C               32099
#define MIN_SECTOR_COUNT_PARM_P                   1

#define MAX_SECTOR_COUNT_PARM_C               32100
#define MAX_SECTOR_COUNT_PARM_P                   1

#define STATUS_CHECK_DELAY_PARM_C             32101
#define STATUS_CHECK_DELAY_PARM_P                 1

#define SPIN_DOWN_WAIT_TIME_PARM_C            32102     // (T528,SpinDwnWaitTm_TPARCD,16,NA)
#define SPIN_DOWN_WAIT_TIME_PARM_P                1

#define MAX_POWER_SPIN_UP_TIME_PARM_C         32103     // (T528,MxPwrSpinUpTm_TPARCD,16,NA)
#define MAX_POWER_SPIN_UP_TIME_PARM_P             1

#define MIN_POWER_SPIN_UP_TIME_PARM_C         32104     // (T528,MnPwrSpinUpTm_TPARCD,16,NA)
#define MIN_POWER_SPIN_UP_TIME_PARM_P             1

#define MAX_ERROR_RATE_PARM_C                 32105
#define MAX_ERROR_RATE_PARM_P                     1

#define DITS_MODE_PARM_C                      32106
#define DITS_MODE_PARM_P                          1

#define MAX_COMMAND_TIME_PARM_C               32107
#define MAX_COMMAND_TIME_PARM_P                   1

#define SEEK_OPTIONS_BYTE_PARM_C              32108
#define SEEK_OPTIONS_BYTE_PARM_P                  1

#define CYLINDER_INCREMENT_PARM_C             32109
#define CYLINDER_INCREMENT_PARM_P                 1

#define TUNED_END_CYL_PARM_C                  32110     // (T549,TunedEndCyl_TPARCD,32,NA)
#define TUNED_END_CYL_PARM_P                      2

#define MIN_SEEK_TIME_DELTA_SPEC_PARM_C       32111     // (T549,MnSkTmDltaSpec_TPARCD,8,0x00FF)
#define MIN_SEEK_TIME_DELTA_SPEC_PARM_P           1

#define MAX_SEEK_TIME_DELTA_SPEC_PARM_C       32112     // (T549,MxSkTmDltaSpec_TPARCD,8,0x00FF)
#define MAX_SEEK_TIME_DELTA_SPEC_PARM_P           1

#define AVG_SEEK_TIME_DELTA_SPEC_PARM_C       32113     // (T549,AvgSkTmDltaSpec_TPARCD,8,0x00FF)
#define AVG_SEEK_TIME_DELTA_SPEC_PARM_P           1

#define MAX_AVG_SEEK_TIME_PARM_C              32114     // (T549,MxAvgSkTm_TPARCD,16,NA)
#define MAX_AVG_SEEK_TIME_PARM_P                  1

#define MAX_SEEK_TIME_PARM_C                  32115     // (T549,MxSkTm_TPARCD,16,0x00FF) (T549,MxSkTm_TPARCD,16,0xFF00)
#define MAX_SEEK_TIME_PARM_P                      1

#define MAX_AVG_HD_SEL_TIME_PARM_C            32116
#define MAX_AVG_HD_SEL_TIME_PARM_P                1

#define MAX_HD_SEL_TIME_PARM_C                32117
#define MAX_HD_SEL_TIME_PARM_P                    1

#define COMMAND_TIMEOUT_PARM_C                32118
#define COMMAND_TIMEOUT_PARM_P                    2

#define DEVIATION_LIMIT_PARM_C                32119     // (T598,DevLmt_TPARCD,16,0x1FFF) (T598,DevLmt_TPARCD,16,0xE000)
#define DEVIATION_LIMIT_PARM_P                    1

#define CACHE_CONTROL_PARM_C                  32120     // (DEF,CacheCtrl_TPARCD,16,NA)
#define CACHE_CONTROL_PARM_P                      1

#define FINAL_ASSEMBLY_DATE_PARM_C            32121
#define FINAL_ASSEMBLY_DATE_PARM_P                4

#define MAX_DIFFERENCE_IN_DAYS_PARM_C         32122
#define MAX_DIFFERENCE_IN_DAYS_PARM_P             1

#define MAX_POWER_ON_WAIT_TIME_PARM_C         32123
#define MAX_POWER_ON_WAIT_TIME_PARM_P             1

#define MAX_GLIST_ENTRIES_PARM_C              32124     // (DEF,GlstLmt_TPARCD[0-1],16,NA) (T515,MxGlistEntry_TPARCD,32,NA) (T529,MxGlistEntry_TPARCD,32,NA) (T564,MxGlistCnt_TPARCD,16,NA)
#define MAX_GLIST_ENTRIES_PARM_P                  2

#define MAX_AVG_SEEK_TIME32_PARM_C            32125
#define MAX_AVG_SEEK_TIME32_PARM_P                2

#define MAX_SEEK_TIME32_PARM_C                32126
#define MAX_SEEK_TIME32_PARM_P                    2

#define HEAD_PARM_C                           32127     // (T618,Hd_TPARCD,8,0x00FF)
#define HEAD_PARM_P                               1

#define SECTOR_PARM_C                         32128
#define SECTOR_PARM_P                             1

#define CYLINDER_PARM_C                       32129
#define CYLINDER_PARM_P                           1

#define FLAGS_PARM_C                          32130
#define FLAGS_PARM_P                              1

#define TOTAL_BLKS_TO_XFR64_PARM_C            32131
#define TOTAL_BLKS_TO_XFR64_PARM_P                4

#define FULL_RETRY_CONTROL_PARM_C             32132     // (DEF,ErrRcovCtrl_TPARCD,16,0x0010) (T510,FullRtryCtrl_TPARCD,8,NA) (T515,FullRtryCtrl_TPARCD,8,NA) (T621,FullRtryCtrl_TPARCD,8,NA) (T1509,FullRtryCtrl_TPARCD,8,NA) (T5509,FullRtryCtrl_TPARCD,8,NA)
#define FULL_RETRY_CONTROL_PARM_P                 1

#define NUM_WRITES_PARM_C                     32133     // (T510,NumWr_TPARCD,16,NA) (T714,NumWr_TPARCD,16,NA)
#define NUM_WRITES_PARM_P                         1

#define SAMPLE_SIZE_PARM_C                    32134
#define SAMPLE_SIZE_PARM_P                        1

#define TOTAL_RETRIES_PARM_C                  32135
#define TOTAL_RETRIES_PARM_P                      1

#define GROUP_RETRIES_PARM_C                  32136
#define GROUP_RETRIES_PARM_P                      1

#define VGA_ADAPTIVE_SPEC_PARM_C              32137
#define VGA_ADAPTIVE_SPEC_PARM_P                  2

#define MAX_WRITE_RETRIES_PARM_C              32138
#define MAX_WRITE_RETRIES_PARM_P                  1

#define MAX_READ_RETRIES_PARM_C               32139
#define MAX_READ_RETRIES_PARM_P                   1

#define MAX_CERT_RETRIES_PARM_C               32140
#define MAX_CERT_RETRIES_PARM_P                   1

#define PROCESS_GLIST_PARM_C                  32141
#define PROCESS_GLIST_PARM_P                      1

#define PROCESS_PLIST_PARM_C                  32142
#define PROCESS_PLIST_PARM_P                      1

#define START_WRITE_LBA_PARM_C                32143
#define START_WRITE_LBA_PARM_P                    4

#define START_READ_LBA_PARM_C                 32144
#define START_READ_LBA_PARM_P                     4

#define MIN_COMMAND_TIME_PARM_C               32145
#define MIN_COMMAND_TIME_PARM_P                   2

#define CCT_LBAS_TO_SAVE_PARM_C               32146
#define CCT_LBAS_TO_SAVE_PARM_P                   1

#define FORMAT_OPTIONS_PARM_C                 32147
#define FORMAT_OPTIONS_PARM_P                     2

#define DEFECT_LIST_OPTIONS_PARM_C            32148
#define DEFECT_LIST_OPTIONS_PARM_P                2

#define DRIVE_VAR_PARM_C                      32149
#define DRIVE_VAR_PARM_P                          1

// Deprecated 2/24/2009
#define DATA_PATTERN32BIT_PARM_C              32150
#define DATA_PATTERN32BIT_PARM_P                  4

#define MAX_RCV_ERRS_PARM_C                   32151     // (DEF,MxRcovErr_TPARCD,32,NA)
#define MAX_RCV_ERRS_PARM_P                       2

#define MAX_NON_RCV_ERRS_PARM_C               32152     // (DEF,MxNonRcovErr_TPARCD,32,NA)
#define MAX_NON_RCV_ERRS_PARM_P                   2

#define READ_BUFFER_OFFSET_PARM_C             32153
#define READ_BUFFER_OFFSET_PARM_P                 2

#define WRITE_BUFFER_OFFSET_PARM_C            32154
#define WRITE_BUFFER_OFFSET_PARM_P                2

#define SCT_ACTION_CODE_PARM_C                32155
#define SCT_ACTION_CODE_PARM_P                    1

#define SCT_FUNCTION_CODE_PARM_C              32156
#define SCT_FUNCTION_CODE_PARM_P                  1

#define FLASH_MFGDEV_ID_PARM_C                32157
#define FLASH_MFGDEV_ID_PARM_P                    1

#define MEMORY_WEAR_CYCLE_PARM_C              32158
#define MEMORY_WEAR_CYCLE_PARM_P                  2

#define ERASE_RBLOCK0_PARM_C                  32159
#define ERASE_RBLOCK0_PARM_P                      1

#define REG_ADDR32_PARM_C                     32160
#define REG_ADDR32_PARM_P                         2

#define REG_VALUE32_PARM_C                    32161
#define REG_VALUE32_PARM_P                        2

#define REG_SIZE_PARM_C                       32162
#define REG_SIZE_PARM_P                           1

#define QMON_ENABLE_PARM_C                    32163     // (T621,QmonEnbl_TPARCD,16,NA) (T1509,QmonEnbl_TPARCD,16,NA) (T5509,QmonEnbl_TPARCD,16,NA)
#define QMON_ENABLE_PARM_P                        1

#define DIAG_SELECT0_PARM_C                   32164
#define DIAG_SELECT0_PARM_P                       2

#define DIAG_SELECT1_PARM_C                   32165
#define DIAG_SELECT1_PARM_P                       2

#define DIAG_SELECT2_PARM_C                   32166
#define DIAG_SELECT2_PARM_P                       2

#define DIAG_SELECT3_PARM_C                   32167
#define DIAG_SELECT3_PARM_P                       2

#define FOUND_PARAMETER_0_PARM_C              32168
#define FOUND_PARAMETER_0_PARM_P                  0

#define FOUND_PARAMETER_N_PARM_C              32169
#define FOUND_PARAMETER_N_PARM_P                  0

#define ENABLE_HW_PATTERN_GEN_PARM_C          32170
#define ENABLE_HW_PATTERN_GEN_PARM_P              1

#define OPAL_SSC_SUPPORT_PARM_C               32171     //(T575,OpalSscSpprt_TPARCD,8,NA)
#define OPAL_SSC_SUPPORT_PARM_P                   1

#define SSC_VERSION_PARM_C                    32172     //(T575,SscVer_TPARCD,8,NA) no functionality
#define SSC_VERSION_PARM_P                        1

#define CORE_SPEC_PARM_C                      32173     //(T575,CoreSpec_TPARCD,8,NA)
#define CORE_SPEC_PARM_P                          1

#define PROGRAM_ERASE_LOOPS_PARM_C            32174
#define PROGRAM_ERASE_LOOPS_PARM_P                2

#define ERASE_LOOPS_PARM_C                    32175
#define ERASE_LOOPS_PARM_P                        2

#define READ_LOOPS_PARM_C                     32176
#define READ_LOOPS_PARM_P                         2

#define MAX_ERASE_FAILURES_PARM_C             32177
#define MAX_ERASE_FAILURES_PARM_P                 2

#define MAX_PROGRAM_FAILURES_PARM_C           32178
#define MAX_PROGRAM_FAILURES_PARM_P               2

#define MAX_READ_FAILURES_PARM_C              32179
#define MAX_READ_FAILURES_PARM_P                  2

#define EXP_NUMBER_FLASH_DIE_PARM_C           32180
#define EXP_NUMBER_FLASH_DIE_PARM_P               1

#define FORMAT_MISC_FLAG_PARM_C               32181
#define FORMAT_MISC_FLAG_PARM_P                   1

#define MIN_SUPERCAP_HEALTH_PARM_C            32182
#define MIN_SUPERCAP_HEALTH_PARM_P                1

#define MILLISECOND_SCALE_PARM_C              32183
#define MILLISECOND_SCALE_PARM_P                  1

#define MULTI_SECTORS_BLOCK_PARM_C            32184
#define MULTI_SECTORS_BLOCK_PARM_P                1

#define FIXED_SECTOR_COUNT_PARM_C             32185
#define FIXED_SECTOR_COUNT_PARM_P                 1

#define SINGLE_LBA_PARM_C                     32186
#define SINGLE_LBA_PARM_P                         2

#define MAX_LBA_PARM_C                        32187
#define MAX_LBA_PARM_P                            2

#define MID_LBA_PARM_C                        32188
#define MID_LBA_PARM_P                            2

#define MIN_LBA_PARM_C                        32189
#define MIN_LBA_PARM_P                            2

#define CURRENT_PE_CYCLE_COUNT_PARM_C         32190
#define CURRENT_PE_CYCLE_COUNT_PARM_P             2

#define LIFE_IN_SECONDS_PARM_C                32191
#define LIFE_IN_SECONDS_PARM_P                    2

#define PRINTDIAGNOSTICREPORT_PARM_C          32192     // (T552,PrtDiagRprt_TPARCD,16,NA)
#define PRINTDIAGNOSTICREPORT_PARM_P              1

#define DISABLE_MB_SCALING_FACTOR_PARM_C      32193     // (T598,DisblMbScalFctr_TPARCD,8,NA)
#define DISABLE_MB_SCALING_FACTOR_PARM_P          1

#define START_CYL_RANGE_PARM_C                32194
#define START_CYL_RANGE_PARM_P                    1

#define END_CYL_RANGE_PARM_C                  32195
#define END_CYL_RANGE_PARM_P                      1

#define BLOCKS_PER_TRANSFER_PARM_C            32196     // (T618,BlkPerTrnsfr_TPARCD,16,NA)
#define BLOCKS_PER_TRANSFER_PARM_P                1

#define CHECK_SECTOR_RANGE_PARM_C             32197     // (T510,ChkSctrRg_TPARCD,8,NA)
#define CHECK_SECTOR_RANGE_PARM_P                 1

#define CHECK_CYLINDER_RANGE_PARM_C           32198     // (DEF,ChkCylRg_TPARCD,8,NA)
#define CHECK_CYLINDER_RANGE_PARM_P               1

#define SECTOR_RANGE_SPEC_PARM_C              32199     // (T510,SctrRgSpec_TPARCD,16,NA)
#define SECTOR_RANGE_SPEC_PARM_P                  1

#define CYLINDER_RANGE_SPEC_PARM_C            32200     // (T510,CylRgSpec_TPARCD,16,NA)
#define CYLINDER_RANGE_SPEC_PARM_P                1

#define ENABLE_ADJ_ZONE_XFR_RATE_DELTA_PARM_C 32201     // (T598,AdjZnTrnsfrRatDlta_TPARCD,8,NA)
#define ENABLE_ADJ_ZONE_XFR_RATE_DELTA_PARM_P     1

#define ADJ_ZONE_XFR_RATE_DELTA_SPEC_PARM_C   32202     // (T598,AdjZnTrnsfrRatSpec_TPARCD,16,NA)
#define ADJ_ZONE_XFR_RATE_DELTA_SPEC_PARM_P       1

#define BLUENUN_SPAN3_PARM_C                  32203
#define BLUENUN_SPAN3_PARM_P                      4

#define BLUENUN_SKIP3_PARM_C                  32204
#define BLUENUN_SKIP3_PARM_P                      2

#define ENABLE_WT_SAME_PARM_C                 32205     // (T510,EnblWrRep_TPARCD,8,0x0001)
#define ENABLE_WT_SAME_PARM_P                     1

#define MEASURE_TIME_PARM_C                   32206     // (T510,MeasTm_TPARCD,8,0x0001)
#define MEASURE_TIME_PARM_P                       1

#define TEST_CONTINUE_PARM_C                  32207     // (T510,TstCont_TPARCD,8,0x0001)
#define TEST_CONTINUE_PARM_P                      1

#define MSECS_PER_CMD_SPEC_PARM_C             32208     // (T510,MsecPerCmdSpec_TPARCD,16,0xFFFF)
#define MSECS_PER_CMD_SPEC_PARM_P                 1

#define TOT_MSECS_PER_TOT_CMDS_SPEC_PARM_C    32209     // (T510,TtlMsecTtlCmdSpec_TPARCD,16,0xFFFF)
#define TOT_MSECS_PER_TOT_CMDS_SPEC_PARM_P        1

#define TOT_CMDS_MINS_SPEC_PARM_C             32210     // (T510,TtlCmdMinSpec_TPARCD,16,0xFFFF)
#define TOT_CMDS_MINS_SPEC_PARM_P                 1

#define MIN_RAND_LBA_PARM_C                   32211
#define MIN_RAND_LBA_PARM_P                       4

#define MAX_RAND_LBA_PARM_C                   32212
#define MAX_RAND_LBA_PARM_P                       4

#define MIN_REV_LBA_PARM_C                    32213
#define MIN_REV_LBA_PARM_P                        4

#define MAX_REV_LBA_PARM_C                    32214
#define MAX_REV_LBA_PARM_P                        4

#define MIN_SEQ_LBA_PARM_C                    32215
#define MIN_SEQ_LBA_PARM_P                        4

#define MAX_SEQ_LBA_PARM_C                    32216
#define MAX_SEQ_LBA_PARM_P                        4

#define CUSTOMER_ID_PARM_C                    32217
#define CUSTOMER_ID_PARM_P                        2

#define SUB_CUSTOMER_ID_PARM_C                32218
#define SUB_CUSTOMER_ID_PARM_P                    2

#define CONFIGURATION_ID_PARM_C               32219
#define CONFIGURATION_ID_PARM_P                   4

#define MINIMUM_LOCATION_PARM_C               32220
#define MINIMUM_LOCATION_PARM_P                   4

#define MAXIMUM_LOCATION_PARM_C               32221
#define MAXIMUM_LOCATION_PARM_P                   4

#define STEP_SIZE_PARM_C                      32222     // (T510,StepSz_TPARCD,64,NA)
#define STEP_SIZE_PARM_P                          4

#define MASTER_PW_REV_CODE_PARM_C             32223
#define MASTER_PW_REV_CODE_PARM_P                 1

#define SCT_BIST_SPEED_CONTROL_PARM_C         32224
#define SCT_BIST_SPEED_CONTROL_PARM_P             1

#define MIN_DELAY_TIME_PARM_C                 32225
#define MIN_DELAY_TIME_PARM_P                     1

#define MAX_DELAY_TIME_PARM_C                 32226
#define MAX_DELAY_TIME_PARM_P                     1

#define STEP_DELAY_TIME_PARM_C                32227
#define STEP_DELAY_TIME_PARM_P                    1

#define GROUP_SIZE_PARM_C                     32228
#define GROUP_SIZE_PARM_P                         1

#define BLOCK_NUMBER_PARM_C                   32229
#define BLOCK_NUMBER_PARM_P                       1

#define MAX_PAGE_PARM_C                       32230
#define MAX_PAGE_PARM_P                           1

#define CORRECTION_POWER_PARM_C               32231
#define CORRECTION_POWER_PARM_P                   1

#define LOOP_TIME_PARM_C                      32232
#define LOOP_TIME_PARM_P                          2

#define NAPM_WAIT_PARM_C                      32233
#define NAPM_WAIT_PARM_P                          2

#define LULST_WAIT_PARM_C                     32234
#define LULST_WAIT_PARM_P                         2

#define APM_WAIT_MAX_PARM_C                   32235
#define APM_WAIT_MAX_PARM_P                       2

#define APM_WAIT_MIN_PARM_C                   32236
#define APM_WAIT_MIN_PARM_P                       2

#define ID_WORD106_OVERRIDE_PARM_C            32237
#define ID_WORD106_OVERRIDE_PARM_P                1

#define SER_WINDOW_PARM_C                     32238
#define SER_WINDOW_PARM_P                         2

#define STEP_SIZE2_PARM_C                     32239
#define STEP_SIZE2_PARM_P                         4

#define MAIN_LOOP_CNT_PARM_C                  32240
#define MAIN_LOOP_CNT_PARM_P                      1

#define WRITE_LOOP_CNT_PARM_C                 32241
#define WRITE_LOOP_CNT_PARM_P                     1

#define READ_LOOP_CNT_PARM_C                  32242
#define READ_LOOP_CNT_PARM_P                      1

#define END_WRITE_LBA_PARM_C                  32243
#define END_WRITE_LBA_PARM_P                      4

#define END_READ_LBA_PARM_C                   32244
#define END_READ_LBA_PARM_P                       4

#define SECTOR_COUNT2_PARM_C                  32245
#define SECTOR_COUNT2_PARM_P                      1

#define QMON_REGISTERS_PARM_C                 32246     // (T1509,QmonReg_TPARCD[0-6],16,NA) (T5509,QmonReg_TPARCD[0-6],16,NA)
#define QMON_REGISTERS_PARM_P                     7

#define EOM_AMPLITUDE_SPEC_PARM_C             32247
#define EOM_AMPLITUDE_SPEC_PARM_P                 1

#define EOM_WIDTH_SPEC_PARM_C                 32248
#define EOM_WIDTH_SPEC_PARM_P                     1

#define PATTERN0_12BYTE_PARM_C                32249
#define PATTERN0_12BYTE_PARM_P                    6

#define PATTERN1_12BYTE_PARM_C                32250
#define PATTERN1_12BYTE_PARM_P                    6

#define SAMSUNG_SERIAL_NUMBER_PARM_C          32251
#define SAMSUNG_SERIAL_NUMBER_PARM_P              7

#define MCFS_FILENAME_PARM_C                  32252
#define MCFS_FILENAME_PARM_P                      4

#define TX_AMPLITUDE_PARM_C                   32253
#define TX_AMPLITUDE_PARM_P                       1

#define MIDDLE_LBA_PARM_C                     32254
#define MIDDLE_LBA_PARM_P                         4

#define WRITE_PROTECT_PARM_C                  32255
#define WRITE_PROTECT_PARM_P                      1

#define SERIAL_OUTPUT_CONTROL_PARM_C          32256
#define SERIAL_OUTPUT_CONTROL_PARM_P              1

#define DFB_BLOCK_PARM_C                      32257
#define DFB_BLOCK_PARM_P                         32

#define CLEAR_SAVED_DATA_PARM_C               32258     // (T5509,ClrSavDta_TPARCD,16,NA)
#define CLEAR_SAVED_DATA_PARM_P                   1

#define RATIO_PARM_C                          32259     // (T521,Ratio_TPARCD,16,NA) (T718,FltRatio_TPARCD,32,NA)
#define RATIO_PARM_P                              2

#define ELAPSED_TIME_PARM_C                   32260     // (T521,ElapsTm_TPARCD,32,NA) 
#define ELAPSED_TIME_PARM_P                       2

#define MAX_ELAPSED_TIME_PARM_C               32261     // (T521,MxElapsTm_TPARCD,32,NA) 
#define MAX_ELAPSED_TIME_PARM_P                   2

#define AVAILABLE_BURN_TIME_PARM_C            32262     // (T521,AvailBurnTm_TPARCD,32,NA)
#define AVAILABLE_BURN_TIME_PARM_P                2

#define DRV_TEMPERATURE_MONITOR_PARM_C        32263
#define DRV_TEMPERATURE_MONITOR_PARM_P            2

#define THRM_ANNEALING_REC_SPEC_PARM_C        32264
#define THRM_ANNEALING_REC_SPEC_PARM_P            1

#define THRM_ANNEALING_ATMP_SPEC_PARM_C       32265
#define THRM_ANNEALING_ATMP_SPEC_PARM_P           1

#define MIN_BLKS_PER_XFR_PARM_C               32266
#define MIN_BLKS_PER_XFR_PARM_P                   1

#define MAX_BLKS_PER_XFR_PARM_C               32267
#define MAX_BLKS_PER_XFR_PARM_P                   1

#define SELECTIVE_SELFTEST_SPANS_PARM_C       32268
#define SELECTIVE_SELFTEST_SPANS_PARM_P          40

#define WRITE_TYPE_PARM_C                     32269
#define WRITE_TYPE_PARM_P                         1

#define FUA_RATIO_PARM_C                      32270
#define FUA_RATIO_PARM_P                          1


/****************************************************************************************************************************

 #     #    ##    #####    #    #  ###  #    #   ####
 #  #  #   #  #   #    #   # #  #   #   # #  #  #
 # # # #  ######  #####    #  # #   #   #  # #  #  ###
 ##   ##  #    #  #    #   #   ##   #   #   ##  #    #
 #     #  #    #  #     #  #    #  ###  #    #   ####

 Check the deprecation and modification policies at the top of this file before making changes.

*****************************************************************************************************************************/

